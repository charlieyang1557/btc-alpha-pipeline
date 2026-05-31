"""Incremental update of BTC/USDT:USDT funding rates via CCXT.

Reads the existing canonical funding parquet, finds the latest settlement,
fetches new funding settlements from (latest + interval) to now via CCXT's
unified fetch_funding_rate_history, normalizes to the funding schema, then
hands off to funding_reconcile.py for merge.

Mirrors ingestion/incremental_update.py: CCXT's built-in rate limiter plus a
custom exponential backoff for NetworkError / RateLimitExceeded (start 1s,
max 60s, 5 retries). Funding history is paginated by `since`.

The CCXT unified funding-rate-history shape is a list of dicts with
`timestamp` (ms) and `fundingRate`; source is labeled "ccxt_binance".

Usage:
    python -m ingestion.funding_incremental_update --pair BTCUSDT
    python -m ingestion.funding_incremental_update --pair BTCUSDT --dry-run
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
CANONICAL_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_funding_8h.parquet"
UPDATE_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_funding_8h_update.parquet"

# CCXT retry config (mirrors incremental_update.py)
MAX_RETRIES = 5
INITIAL_BACKOFF_S = 1.0
MAX_BACKOFF_S = 60.0

# Funding-history page size cap.
FUNDING_LIMIT = 1000

# Default funding interval (hours) when the payload does not carry it.
# BTCUSDT settles every 8h over the window; we read per-row from the CCXT
# `info` payload when present and only fall back to this default.
DEFAULT_FUNDING_INTERVAL_HOURS = 8
EIGHT_HOURS_MS = 8 * 3_600_000

# CCXT unified perpetual symbol for BTCUSDT USDT-M.
DEFAULT_SYMBOL = "BTC/USDT:USDT"


def create_exchange(exchange_id: str = "binance", proxy: str | None = None) -> ccxt.Exchange:
    """Create a CCXT exchange instance with rate limiting enabled.

    Args:
        exchange_id: CCXT exchange identifier (default "binance").
        proxy: Optional HTTP(S) proxy URL. Also read from CCXT_PROXY env var.

    Returns:
        Configured exchange instance with markets loaded.
    """
    import os
    proxy_url = proxy or os.environ.get("CCXT_PROXY")

    config: dict = {"enableRateLimit": True, "options": {"defaultType": "future"}}
    if proxy_url:
        config["proxies"] = {"http": proxy_url, "https": proxy_url}
        logger.info("Using proxy: %s", proxy_url)

    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class(config)
    logger.info("Loading markets for %s ...", exchange_id)
    exchange.load_markets()
    return exchange


def fetch_funding_with_backoff(
    exchange: ccxt.Exchange,
    symbol: str,
    since: int,
    limit: int = FUNDING_LIMIT,
) -> list[dict]:
    """Fetch one page of funding history with exponential backoff.

    Calls CCXT's unified fetch_funding_rate_history (snake_case) and retries
    on NetworkError / RateLimitExceeded.

    Args:
        exchange: CCXT exchange instance.
        symbol: Unified perpetual symbol (e.g. "BTC/USDT:USDT").
        since: Start time in milliseconds since epoch.
        limit: Max settlements per request.

    Returns:
        List of CCXT funding-rate-history dicts.

    Raises:
        ccxt.NetworkError: After MAX_RETRIES exhausted.
    """
    backoff = INITIAL_BACKOFF_S
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return exchange.fetch_funding_rate_history(symbol=symbol, since=since, limit=limit)
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
    return []  # unreachable, satisfies type checker


def fetch_all_funding(
    exchange: ccxt.Exchange,
    symbol: str,
    since_ms: int,
) -> list[dict]:
    """Paginate through funding history from since_ms to now.

    Args:
        exchange: CCXT exchange instance.
        symbol: Unified perpetual symbol.
        since_ms: Start time in ms since epoch.

    Returns:
        List of all funding-rate-history dicts fetched (deduped by timestamp,
        ascending).
    """
    all_rows: list[dict] = []
    seen: set[int] = set()
    current_since = since_ms

    while True:
        logger.info("Fetching funding from %s ...", pd.Timestamp(current_since, unit="ms", tz="UTC"))
        page = fetch_funding_with_backoff(exchange, symbol, current_since)
        if not page:
            break

        new_rows = [r for r in page if int(r["timestamp"]) not in seen]
        if not new_rows:
            break
        for r in new_rows:
            seen.add(int(r["timestamp"]))
        all_rows.extend(new_rows)
        logger.info("  Got %d settlements (total: %d)", len(new_rows), len(all_rows))

        # Reached the end if the page was under the limit.
        if len(page) < FUNDING_LIMIT:
            break

        # Advance the cursor by +1ms past the last seen settlement (NOT +8h):
        # advancing by a hardcoded 8h could skip a settlement that lands between
        # last_ts and last_ts + 8h. The `seen` dedup set absorbs the boundary
        # row if the CCXT API treats `since` inclusively.
        last_ts = max(int(r["timestamp"]) for r in page)
        current_since = last_ts + 1

    all_rows.sort(key=lambda r: int(r["timestamp"]))
    return all_rows


def _row_interval_hours(row: dict) -> int:
    """Read the funding interval (hours) for one CCXT row, never hardcoded blindly.

    Prefers the venue-provided `info.fundingIntervalHours`; falls back to the
    documented 8h default (BTCUSDT over the window) when absent.

    Args:
        row: A single CCXT funding-rate-history dict.

    Returns:
        Funding interval in hours.
    """
    info = row.get("info") or {}
    raw = info.get("fundingIntervalHours")
    if raw is not None:
        try:
            return int(raw)
        except (ValueError, TypeError):
            pass
    return DEFAULT_FUNDING_INTERVAL_HOURS


_FUNDING_SCHEMA_COLUMNS = [
    "open_time_utc", "funding_rate", "funding_interval_hours",
    "ingested_at_utc", "source",
]


def _funding_rate_or_none(row: dict) -> float | None:
    """Return the row's fundingRate as float, or None if missing/None/NaN.

    Binance returns fundingRate=None during exchange outages; such rows must be
    dropped (not coerced) since funding_rate is schema-declared nullable: false.
    """
    raw = row.get("fundingRate")
    if raw is None:
        return None
    try:
        val = float(raw)
    except (ValueError, TypeError):
        return None
    if val != val:  # NaN
        return None
    return val


def funding_history_to_dataframe(rows: list[dict]) -> pd.DataFrame:
    """Convert CCXT funding-rate-history dicts to a schema-compliant DataFrame.

    Args:
        rows: List of CCXT funding-rate-history dicts (timestamp ms, fundingRate).

    Returns:
        DataFrame matching the funding schema with source="ccxt_binance". Rows
        whose fundingRate is None/NaN (Binance returns None during outages) are
        dropped + counted + logged; funding_rate is schema nullable: false. If
        every row drops, an empty frame with the correct schema columns is
        returned.
    """
    n_in = len(rows)
    rows = [r for r in rows if _funding_rate_or_none(r) is not None]
    n_dropped = n_in - len(rows)
    if n_dropped:
        logger.info(
            "funding_history_to_dataframe: dropped %d row(s) with None/NaN fundingRate",
            n_dropped,
        )

    if not rows:
        return pd.DataFrame(columns=_FUNDING_SCHEMA_COLUMNS)

    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(
            [int(r["timestamp"]) for r in rows], unit="ms", utc=True
        ).as_unit("ms"),
        "funding_rate": [_funding_rate_or_none(r) for r in rows],
        "funding_interval_hours": [_row_interval_hours(r) for r in rows],
    })
    df["funding_rate"] = df["funding_rate"].astype("float64")
    df["funding_interval_hours"] = df["funding_interval_hours"].astype("int64")
    df["source"] = pd.array(["ccxt_binance"] * len(df), dtype="string")
    df["ingested_at_utc"] = pd.Timestamp(datetime.now(timezone.utc)).as_unit("ms")
    return df.sort_values("open_time_utc").reset_index(drop=True)


def main() -> int:
    """CLI entry point for incremental funding update.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(description="Incremental funding update via CCXT")
    parser.add_argument("--pair", type=str, default="BTCUSDT", help="Trading pair (no slash)")
    parser.add_argument("--exchange", type=str, default="binance", help="CCXT exchange id")
    parser.add_argument(
        "--proxy", type=str, default=None,
        help="HTTP(S) proxy URL (also reads CCXT_PROXY env var)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fetched")
    args = parser.parse_args()

    # Phase A is BTCUSDT-only. Refuse any other pair rather than silently
    # building a malformed unified symbol from the naive [:3]/[3:] split.
    if args.pair != "BTCUSDT":
        raise ValueError(
            f"Phase A funding ingestion supports only --pair BTCUSDT, got {args.pair!r}"
        )
    symbol = DEFAULT_SYMBOL

    if not CANONICAL_PATH.exists():
        logger.error("Canonical funding file not found: %s", CANONICAL_PATH)
        logger.error("Run funding_bulk_download.py first")
        return 1

    existing = pd.read_parquet(CANONICAL_PATH)
    latest = existing["open_time_utc"].max()
    logger.info("Existing funding: %d rows, latest = %s", len(existing), latest)

    # Advance +1ms past the latest existing settlement (NOT +8h): a hardcoded
    # 8h step could skip a settlement landing between latest and latest + 8h.
    # Reconcile dedups on the PK, so re-fetching the boundary row is harmless.
    since_ms = int(latest.timestamp() * 1000) + 1
    since_ts = pd.Timestamp(since_ms, unit="ms", tz="UTC")
    logger.info("Fetching new settlements from %s", since_ts)

    if args.dry_run:
        print(f"Would fetch funding {symbol} from {since_ts} to now")
        return 0

    exchange = create_exchange(args.exchange, proxy=args.proxy)
    rows = fetch_all_funding(exchange, symbol, since_ms)

    if not rows:
        logger.info("No new funding settlements available")
        return 0

    df = funding_history_to_dataframe(rows)
    logger.info("Fetched %d new settlements (source=ccxt_binance)", len(df))
    logger.info(
        "New data range: %s to %s",
        df["open_time_utc"].iloc[0],
        df["open_time_utc"].iloc[-1],
    )

    from ingestion.validators import validate_funding

    report = validate_funding(df)
    logger.info("New data validation ok: %s", report["ok"])
    if not report["ok"]:
        for err in report["errors"]:
            logger.error("  ERROR: %s", err)
        logger.error("New data failed validation — aborting")
        return 1

    df.to_parquet(UPDATE_PATH, engine="pyarrow", index=False)
    logger.info("Saved %d new settlements to %s", len(df), UPDATE_PATH)
    logger.info("Run funding_reconcile.py to merge into canonical dataset")

    return 0


if __name__ == "__main__":
    sys.exit(main())
