"""Incremental update of BTC mark-price and index-price 1h klines via CCXT.

Reads the existing canonical markprice parquet, finds the latest open_time_utc,
fetches new mark and index OHLCV klines from (latest + 1h) to now via CCXT's
unified fetch_ohlcv with params={"price":"mark"} / {"price":"index"}, inner-joins
on open_time_utc, normalizes to the markprice schema, then hands off to
markprice_reconcile.py for merge.

Mirrors ingestion/funding_incremental_update.py: CCXT's built-in rate limiter plus a
custom exponential backoff for NetworkError / RateLimitExceeded (start 1s,
max 60s, 5 retries). Klines are paginated by `since`.

Output schema (inner-joined on open_time_utc):
    open_time_utc   datetime64[ms, UTC]   PK
    mark_close      float64
    index_close     float64
    source          string                always "ccxt_binance"
    ingested_at_utc datetime64[ms, UTC]

Usage:
    python -m ingestion.markprice_incremental_update --pair BTCUSDT
    python -m ingestion.markprice_incremental_update --pair BTCUSDT --dry-run
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
CANONICAL_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_markprice_1h.parquet"
UPDATE_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_markprice_1h_update.parquet"

# CCXT retry config (mirrors funding_incremental_update.py)
MAX_RETRIES = 5
INITIAL_BACKOFF_S = 1.0
MAX_BACKOFF_S = 60.0

# Kline page size cap.
KLINE_LIMIT = 1000

ONE_HOUR_MS = 3_600_000

# CCXT unified perpetual symbol for BTCUSDT USDT-M.
DEFAULT_SYMBOL = "BTC/USDT:USDT"
DEFAULT_TIMEFRAME = "1h"

_MARKPRICE_SCHEMA_COLUMNS = [
    "open_time_utc", "mark_close", "index_close", "source", "ingested_at_utc",
]


def _redact_url(url: str) -> str:
    """Strip userinfo (username:password) from a URL before logging.

    ``http://user:pass@host:port/path`` → ``http://host:port/path``
    ``http://host:port/path`` (no credentials) → unchanged.
    """
    try:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        # Replace netloc with host-only (drop user:pass@)
        redacted = parsed._replace(netloc=parsed.hostname + (
            f":{parsed.port}" if parsed.port else ""
        ))
        return urlunparse(redacted)
    except Exception:
        return "<proxy-url>"


# Allowlist of CCXT exchange identifiers accepted by create_exchange.
# Guards against arbitrary code execution via unvalidated --exchange CLI input.
_ALLOWED_EXCHANGES = frozenset(ccxt.exchanges)


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
    # FIX 6 (security): validate exchange_id against ccxt.exchanges before
    # getattr — prevents arbitrary attribute access on the ccxt module.
    if exchange_id not in _ALLOWED_EXCHANGES:
        raise ValueError(
            f"exchange_id {exchange_id!r} is not a known CCXT exchange. "
            f"Must be one of the exchanges listed in ccxt.exchanges."
        )

    proxy_url = proxy or os.environ.get("CCXT_PROXY")

    config: dict = {"enableRateLimit": True, "options": {"defaultType": "future"}}
    if proxy_url:
        config["proxies"] = {"http": proxy_url, "https": proxy_url}
        # FIX 5 (security): redact credentials from proxy URL before logging.
        logger.info("Using proxy: %s", _redact_url(proxy_url))

    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class(config)
    logger.info("Loading markets for %s ...", exchange_id)
    exchange.load_markets()
    return exchange


def fetch_markprice_with_backoff(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    since: int,
    price_type: str,
    limit: int = KLINE_LIMIT,
) -> list[list]:
    """Fetch one page of mark or index OHLCV with exponential backoff.

    Calls CCXT's unified fetch_ohlcv with params={"price": price_type} and
    retries on NetworkError / RateLimitExceeded.

    Args:
        exchange: CCXT exchange instance.
        symbol: Unified perpetual symbol (e.g. "BTC/USDT:USDT").
        timeframe: Candle interval (e.g. "1h").
        since: Start time in milliseconds since epoch.
        price_type: Either "mark" or "index".
        limit: Max candles per request.

    Returns:
        List of OHLCV rows [[timestamp_ms, open, high, low, close, volume], ...].

    Raises:
        ccxt.NetworkError: After MAX_RETRIES exhausted.
    """
    backoff = INITIAL_BACKOFF_S
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return exchange.fetch_ohlcv(
                symbol, timeframe, since=since, limit=limit,
                params={"price": price_type},
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
    return []  # unreachable, satisfies type checker


def _fetch_one_series(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    since_ms: int,
    price_type: str,
) -> list[list]:
    """Paginate through one mark or index OHLCV series from since_ms to now.

    Args:
        exchange: CCXT exchange instance.
        symbol: Unified perpetual symbol.
        timeframe: Candle interval.
        since_ms: Start time in ms since epoch.
        price_type: Either "mark" or "index".

    Returns:
        Deduplicated, ascending list of OHLCV rows.
    """
    all_rows: list[list] = []
    seen: set[int] = set()
    current_since = since_ms

    while True:
        logger.info(
            "Fetching %s price from %s ...",
            price_type,
            pd.Timestamp(current_since, unit="ms", tz="UTC"),
        )
        page = fetch_markprice_with_backoff(
            exchange, symbol, timeframe, current_since, price_type
        )
        if not page:
            break

        new_rows = [r for r in page if int(r[0]) not in seen]
        if not new_rows:
            break
        for r in new_rows:
            seen.add(int(r[0]))
        all_rows.extend(new_rows)
        logger.info("  Got %d rows (total: %d)", len(new_rows), len(all_rows))

        if len(page) < KLINE_LIMIT:
            break

        last_ts = max(int(r[0]) for r in page)
        current_since = last_ts + ONE_HOUR_MS

    all_rows.sort(key=lambda r: int(r[0]))
    return all_rows


def fetch_all_markprice(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    since_ms: int,
) -> tuple[list[list], list[list]]:
    """Fetch both mark-price and index-price OHLCV series from since_ms to now.

    Args:
        exchange: CCXT exchange instance.
        symbol: Unified perpetual symbol.
        timeframe: Candle interval.
        since_ms: Start time in ms since epoch.

    Returns:
        Tuple (mark_rows, index_rows), each a list of OHLCV rows sorted ascending.
    """
    mark_rows = _fetch_one_series(exchange, symbol, timeframe, since_ms, "mark")
    index_rows = _fetch_one_series(exchange, symbol, timeframe, since_ms, "index")
    return mark_rows, index_rows


def ohlcv_to_markprice_dataframe(
    mark_rows: list[list],
    index_rows: list[list],
) -> pd.DataFrame:
    """Convert mark and index OHLCV rows to a schema-compliant markprice DataFrame.

    Inner-joins on open_time_utc: timestamps absent from either series are dropped.

    Args:
        mark_rows: OHLCV rows for mark price [[ts_ms, o, h, l, close, vol], ...].
        index_rows: OHLCV rows for index price [[ts_ms, o, h, l, close, vol], ...].

    Returns:
        DataFrame with columns:
            open_time_utc   datetime64[ms, UTC]  PK (inner join)
            mark_close      float64
            index_close     float64
            source          string               "ccxt_binance"
            ingested_at_utc datetime64[ms, UTC]
    """
    if not mark_rows or not index_rows:
        return pd.DataFrame(columns=_MARKPRICE_SCHEMA_COLUMNS)

    mark_df = pd.DataFrame(mark_rows, columns=["ts", "open", "high", "low", "close", "vol"])
    index_df = pd.DataFrame(index_rows, columns=["ts", "open", "high", "low", "close", "vol"])

    mark_df["ts"] = pd.to_numeric(mark_df["ts"], errors="coerce").astype("int64")
    index_df["ts"] = pd.to_numeric(index_df["ts"], errors="coerce").astype("int64")

    # Inner join on timestamp
    merged = pd.merge(
        mark_df[["ts", "close"]].rename(columns={"close": "mark_close"}),
        index_df[["ts", "close"]].rename(columns={"close": "index_close"}),
        on="ts",
        how="inner",
    )

    if merged.empty:
        return pd.DataFrame(columns=_MARKPRICE_SCHEMA_COLUMNS)

    merged["open_time_utc"] = pd.to_datetime(merged["ts"], unit="ms", utc=True).astype("datetime64[ms, UTC]")
    merged["mark_close"] = merged["mark_close"].astype("float64")
    merged["index_close"] = merged["index_close"].astype("float64")
    merged["source"] = pd.array(["ccxt_binance"] * len(merged), dtype="string")
    merged["ingested_at_utc"] = pd.Timestamp(datetime.now(timezone.utc)).as_unit("ms")

    result = merged[_MARKPRICE_SCHEMA_COLUMNS].sort_values("open_time_utc").reset_index(drop=True)
    return result


def main() -> int:
    """CLI entry point for incremental markprice update.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(description="Incremental markprice update via CCXT")
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
            f"Path C markprice ingestion supports only --pair BTCUSDT, got {args.pair!r}"
        )
    symbol = DEFAULT_SYMBOL

    if not CANONICAL_PATH.exists():
        logger.error("Canonical markprice file not found: %s", CANONICAL_PATH)
        logger.error("Run markprice_bulk_download.py first")
        return 1

    existing = pd.read_parquet(CANONICAL_PATH)
    latest = existing["open_time_utc"].max()
    logger.info("Existing markprice: %d rows, latest = %s", len(existing), latest)

    since_ms = int(latest.timestamp() * 1000) + ONE_HOUR_MS
    since_ts = pd.Timestamp(since_ms, unit="ms", tz="UTC")
    logger.info("Fetching new klines from %s", since_ts)

    if args.dry_run:
        print(f"Would fetch markprice {symbol} from {since_ts} to now")
        return 0

    exchange = create_exchange(args.exchange, proxy=args.proxy)
    mark_rows, index_rows = fetch_all_markprice(exchange, symbol, DEFAULT_TIMEFRAME, since_ms)

    if not mark_rows and not index_rows:
        logger.info("No new markprice klines available")
        return 0

    df = ohlcv_to_markprice_dataframe(mark_rows, index_rows)
    if df.empty:
        logger.info("No rows remain after inner join of mark and index series")
        return 0

    logger.info("Fetched %d new rows (source=ccxt_binance)", len(df))
    logger.info(
        "New data range: %s to %s",
        df["open_time_utc"].iloc[0],
        df["open_time_utc"].iloc[-1],
    )

    from ingestion.validators import validate_markprice

    report = validate_markprice(df)
    logger.info("New data validation ok: %s", report["ok"])
    if not report["ok"]:
        for err in report["errors"]:
            logger.error("  ERROR: %s", err)
        logger.error("New data failed validation — aborting")
        return 1

    df.to_parquet(UPDATE_PATH, engine="pyarrow", index=False)
    logger.info("Saved %d new rows to %s", len(df), UPDATE_PATH)
    logger.info("Run markprice_reconcile.py to merge into canonical dataset")

    return 0


if __name__ == "__main__":
    sys.exit(main())
