"""Incremental update of BTC open-interest 1h snapshots via CCXT.

Reads the existing canonical OI parquet, finds the latest open_time_utc,
fetches new OI history rows from (latest + 1h) to now via CCXT's unified
``fetch_open_interest_history(symbol, timeframe, since, limit)`` call,
normalizes to the oi schema, then hands off to oi_reconcile.py for merge.

**Endpoint limit warning:** Binance's OI-history endpoint returns only ~30 days
of history.  This module is a RECENT-WINDOW top-up only.  The bulk Binance
Vision download (oi_bulk_download.py) is the sole full-history path.

Mirrors ingestion/markprice_incremental_update.py: CCXT's built-in rate limiter
plus a custom exponential backoff for NetworkError / RateLimitExceeded
(start 1s, max 60s, 5 retries).  Results are paginated by ``since``.

Output schema (oi):
    open_time_utc           datetime64[ms, UTC]   PK
    sum_open_interest       float64               CONTRACT/base-asset OI
                                                  FIREWALL: NOT the USDT notional
    sum_open_interest_value float64               USDT notional (diagnostic only)
    source                  string                always "ccxt_binance"
    ingested_at_utc         datetime64[ms, UTC]

NOTE (A7 re-verify): the CCXT unified field names used here
(``openInterestAmount`` for contracts, ``openInterestValue`` for USDT notional)
are based on current CCXT documentation research.  A7 (§38.1) must confirm
these against a live or recorded CCXT response before any production use.

Usage:
    python -m ingestion.oi_incremental_update --pair BTCUSDT
    python -m ingestion.oi_incremental_update --pair BTCUSDT --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import ccxt
import pandas as pd

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_oi_1h.parquet"
UPDATE_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_oi_1h_update.parquet"

# CCXT retry config (mirrors markprice_incremental_update.py)
MAX_RETRIES = 5
INITIAL_BACKOFF_S = 1.0
MAX_BACKOFF_S = 60.0

# OI page size cap (Binance allows up to 500 per call for OI history).
OI_LIMIT = 500

ONE_HOUR_MS = 3_600_000

# Binance OI-history endpoint covers approximately 30 days.
ENDPOINT_WINDOW_DAYS = 30
ENDPOINT_WINDOW_MS = ENDPOINT_WINDOW_DAYS * 24 * ONE_HOUR_MS

# CCXT unified perpetual symbol for BTCUSDT USDT-M.
DEFAULT_SYMBOL = "BTC/USDT:USDT"
DEFAULT_TIMEFRAME = "1h"

_OI_SCHEMA_COLUMNS = [
    "open_time_utc",
    "sum_open_interest",
    "sum_open_interest_value",
    "source",
    "ingested_at_utc",
]

# ---------------------------------------------------------------------------
# Security helpers (mirrors markprice_incremental_update.py)
# ---------------------------------------------------------------------------

_ALLOWED_EXCHANGES = frozenset(ccxt.exchanges)


def _redact_url(url: str) -> str:
    """Strip userinfo from a URL before logging."""
    try:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        redacted = parsed._replace(netloc=parsed.hostname + (
            f":{parsed.port}" if parsed.port else ""
        ))
        return urlunparse(redacted)
    except Exception:
        return "<proxy-url>"


# ---------------------------------------------------------------------------
# Exchange factory
# ---------------------------------------------------------------------------

def create_exchange(exchange_id: str = "binance", proxy: str | None = None) -> ccxt.Exchange:
    """Create a CCXT exchange instance with rate limiting enabled.

    Args:
        exchange_id: CCXT exchange identifier (default "binance").
            Must be a known CCXT exchange (validated against ccxt.exchanges).
        proxy: Optional HTTP(S) proxy URL. Also read from CCXT_PROXY env var.

    Returns:
        Configured exchange instance with markets loaded.

    Raises:
        ValueError: If ``exchange_id`` is not in the CCXT exchange allowlist.
    """
    import os
    if exchange_id not in _ALLOWED_EXCHANGES:
        raise ValueError(
            f"exchange_id {exchange_id!r} is not a known CCXT exchange."
        )

    proxy_url = proxy or os.environ.get("CCXT_PROXY")

    config: dict = {"enableRateLimit": True, "options": {"defaultType": "future"}}
    if proxy_url:
        config["proxies"] = {"http": proxy_url, "https": proxy_url}
        logger.info("Using proxy: %s", _redact_url(proxy_url))

    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class(config)
    logger.info("Loading markets for %s ...", exchange_id)
    exchange.load_markets()
    return exchange


# ---------------------------------------------------------------------------
# Fetch with backoff
# ---------------------------------------------------------------------------

def fetch_oi_with_backoff(
    exchange: object,
    symbol: str,
    timeframe: str,
    since: int,
    limit: int = OI_LIMIT,
) -> list[dict]:
    """Fetch one page of OI history with exponential backoff.

    Calls CCXT's unified ``fetch_open_interest_history`` and retries on
    NetworkError / RateLimitExceeded.

    Args:
        exchange: CCXT exchange instance (or compatible stub).
        symbol: Unified perpetual symbol (e.g. "BTC/USDT:USDT").
        timeframe: Candle interval (e.g. "1h").
        since: Start time in milliseconds since epoch.
        limit: Max rows per request.

    Returns:
        List of CCXT OI-history dicts.

    Raises:
        ccxt.NetworkError: After MAX_RETRIES exhausted.

    NOTE (A7 re-verify §38.1): each returned dict is expected to contain
    ``openInterestAmount`` (contracts) and ``openInterestValue`` (USDT notional).
    Confirm field names against a live CCXT response before production use.
    """
    backoff = INITIAL_BACKOFF_S
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return exchange.fetch_open_interest_history(
                symbol, timeframe, since=since, limit=limit
            )
        except (ccxt.NetworkError, ccxt.RateLimitExceeded) as e:
            if attempt == MAX_RETRIES:
                logger.error("Max retries (%d) exhausted: %s", MAX_RETRIES, e)
                raise
            logger.warning(
                "Attempt %d/%d failed (%s), retrying in %.1fs ...",
                attempt, MAX_RETRIES, type(e).__name__, backoff,
            )
            time.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF_S)
    return []  # unreachable; satisfies type checker


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

def fetch_oi_history_paged(
    exchange: object,
    symbol: str,
    timeframe: str,
    since_ms: int,
) -> list[dict]:
    """Paginate through OI history from since_ms to now.

    Emits a WARNING if ``since_ms`` is older than ~30 days (endpoint limit).

    Args:
        exchange: CCXT exchange instance (or compatible stub).
        symbol: Unified perpetual symbol.
        timeframe: Candle interval.
        since_ms: Start time in ms since epoch.

    Returns:
        Deduplicated, ascending list of CCXT OI-history dicts.
    """
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    cutoff_ms = now_ms - ENDPOINT_WINDOW_MS
    if since_ms < cutoff_ms:
        logger.warning(
            "Requested since=%s is older than the ~%dd endpoint window limit. "
            "Only ~30d of OI history is available via this CCXT endpoint. "
            "Use oi_bulk_download.py for full history.",
            pd.Timestamp(since_ms, unit="ms", tz="UTC"),
            ENDPOINT_WINDOW_DAYS,
        )

    all_rows: list[dict] = []
    seen: set[int] = set()
    current_since = since_ms

    while True:
        logger.info(
            "Fetching OI from %s ...",
            pd.Timestamp(current_since, unit="ms", tz="UTC"),
        )
        page = fetch_oi_with_backoff(exchange, symbol, timeframe, current_since)
        if not page:
            break

        new_rows = [r for r in page if int(r["timestamp"]) not in seen]
        if not new_rows:
            break
        for r in new_rows:
            seen.add(int(r["timestamp"]))
        all_rows.extend(new_rows)
        logger.info("  Got %d rows (total: %d)", len(new_rows), len(all_rows))

        if len(page) < OI_LIMIT:
            break

        last_ts = max(int(r["timestamp"]) for r in page)
        current_since = last_ts + ONE_HOUR_MS

    all_rows.sort(key=lambda r: int(r["timestamp"]))
    return all_rows


# ---------------------------------------------------------------------------
# Normalizer
# ---------------------------------------------------------------------------

def oi_rows_to_dataframe(rows: list[dict]) -> pd.DataFrame:
    """Convert CCXT OI-history rows to a schema-compliant oi DataFrame.

    FIREWALL: ``sum_open_interest`` is taken from the CONTRACT/base-asset
    field (``openInterestAmount``), NOT the USDT notional.  The USDT notional
    embeds price-return velocity and is stored in ``sum_open_interest_value``
    as a contamination-diagnostic column only.

    NOTE (A7 re-verify §38.1): field names ``openInterestAmount`` and
    ``openInterestValue`` are based on current CCXT unified schema research.
    Confirm against a live CCXT response before production use.

    Args:
        rows: List of CCXT fetch_open_interest_history dicts.

    Returns:
        DataFrame with columns:
            open_time_utc           datetime64[ms, UTC]  PK
            sum_open_interest       float64              contracts (base asset)
            sum_open_interest_value float64              USDT notional
            source                  string               "ccxt_binance"
            ingested_at_utc         datetime64[ms, UTC]
    """
    if not rows:
        return pd.DataFrame(columns=_OI_SCHEMA_COLUMNS)

    records = []
    for r in rows:
        ts_ms = int(r["timestamp"])
        # FIREWALL: openInterestAmount = contracts (base/coin), NOT notional.
        # A7 must re-verify this field name against a live CCXT response.
        contract_oi = float(r["openInterestAmount"])
        # USDT notional: contamination-diagnostic only; None-safe.
        notional = r.get("openInterestValue")
        notional_float = float(notional) if notional is not None else float("nan")
        records.append({
            "ts_ms": ts_ms,
            "sum_open_interest": contract_oi,
            "sum_open_interest_value": notional_float,
        })

    df = pd.DataFrame(records)
    df["open_time_utc"] = (
        pd.to_datetime(df["ts_ms"], unit="ms", utc=True)
        .astype("datetime64[ms, UTC]")
    )
    df["sum_open_interest"] = df["sum_open_interest"].astype("float64")
    df["sum_open_interest_value"] = df["sum_open_interest_value"].astype("float64")
    df["source"] = pd.array(["ccxt_binance"] * len(df), dtype="string")
    df["ingested_at_utc"] = pd.Timestamp(datetime.now(timezone.utc)).as_unit("ms")

    result = (
        df[_OI_SCHEMA_COLUMNS]
        .sort_values("open_time_utc")
        .reset_index(drop=True)
    )
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    """CLI entry point for incremental OI update.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(description="Incremental OI update via CCXT (recent-window)")
    parser.add_argument("--pair", type=str, default="BTCUSDT", help="Trading pair (no slash)")
    parser.add_argument("--exchange", type=str, default="binance", help="CCXT exchange id")
    parser.add_argument(
        "--proxy", type=str, default=None,
        help="HTTP(S) proxy URL (also reads CCXT_PROXY env var)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fetched")
    args = parser.parse_args()

    if args.pair != "BTCUSDT":
        raise ValueError(
            f"Path D OI incremental update supports only --pair BTCUSDT, got {args.pair!r}"
        )
    symbol = DEFAULT_SYMBOL

    if not CANONICAL_PATH.exists():
        logger.error("Canonical OI file not found: %s", CANONICAL_PATH)
        logger.error("Run oi_bulk_download.py first")
        return 1

    existing = pd.read_parquet(CANONICAL_PATH)
    latest = existing["open_time_utc"].max()
    logger.info("Existing OI: %d rows, latest = %s", len(existing), latest)

    since_ms = int(latest.timestamp() * 1000) + ONE_HOUR_MS
    since_ts = pd.Timestamp(since_ms, unit="ms", tz="UTC")
    logger.info("Fetching new OI from %s", since_ts)

    if args.dry_run:
        print(f"Would fetch OI {symbol} from {since_ts} to now (recent-window ~30d)")
        return 0

    exchange = create_exchange(args.exchange, proxy=args.proxy)
    rows = fetch_oi_history_paged(exchange, symbol, DEFAULT_TIMEFRAME, since_ms)

    if not rows:
        logger.info("No new OI rows available")
        return 0

    df = oi_rows_to_dataframe(rows)
    if df.empty:
        logger.info("No rows after normalization")
        return 0

    logger.info("Fetched %d new rows (source=ccxt_binance)", len(df))
    logger.info(
        "New data range: %s to %s",
        df["open_time_utc"].iloc[0],
        df["open_time_utc"].iloc[-1],
    )

    from ingestion.validators import validate_oi

    report = validate_oi(df)
    logger.info("New data validation ok: %s", report["ok"])
    if not report["ok"]:
        for err in report["errors"]:
            logger.error("  ERROR: %s", err)
        logger.error("New data failed validation — aborting")
        return 1

    df.to_parquet(UPDATE_PATH, engine="pyarrow", index=False)
    logger.info("Saved %d new rows to %s", len(df), UPDATE_PATH)
    logger.info("Run oi_reconcile.py to merge into canonical dataset")

    return 0


if __name__ == "__main__":
    sys.exit(main())
