"""
Incremental update of BTC/USDT 1h klines via CCXT.

Reads the existing canonical parquet, finds the latest timestamp,
fetches new candles from (latest + 1h) to now via CCXT, validates
new rows, then hands off to reconcile.py for merge.

Supports multiple exchanges via --exchange flag. Default is "binance"
(Binance global). Use "binanceus" for US-accessible Binance.US.

IMPORTANT: Binance.US is a separate venue with different liquidity and
order flow. Its candles are NOT equivalent to Binance global data.
The source column reflects the venue (e.g. "ccxt_binance" vs
"ccxt_binanceus"), and reconcile.py will refuse to merge data from
different venues into the same canonical file.

Uses CCXT's built-in rate limiter + custom exponential backoff
for NetworkError / RateLimitExceeded (start 1s, max 60s, 5 retries).

Usage:
    python -m ingestion.incremental_update --pair BTCUSDT --interval 1h
    python -m ingestion.incremental_update --pair BTCUSDT --interval 1h --dry-run
    python -m ingestion.incremental_update --pair BTCUSDT --interval 1h --exchange binanceus
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
CANONICAL_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"
UPDATE_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h_update.parquet"

# CCXT retry config (per PHASE0_BLUEPRINT.md)
MAX_RETRIES = 5
INITIAL_BACKOFF_S = 1.0
MAX_BACKOFF_S = 60.0

# Binance CCXT kline limit per request
KLINE_LIMIT = 1000

ONE_HOUR_MS = 3_600_000


SUPPORTED_EXCHANGES = {"binance", "binanceus"}


def create_exchange(exchange_id: str = "binance") -> ccxt.Exchange:
    """Create a CCXT exchange instance with rate limiting enabled.

    Args:
        exchange_id: CCXT exchange identifier ("binance" or "binanceus").

    Returns:
        Configured exchange instance with markets loaded.

    Raises:
        ValueError: If exchange_id is not supported.
    """
    if exchange_id not in SUPPORTED_EXCHANGES:
        raise ValueError(
            f"Unsupported exchange '{exchange_id}'. "
            f"Supported: {sorted(SUPPORTED_EXCHANGES)}"
        )
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({"enableRateLimit": True})
    logger.info("Loading markets for %s ...", exchange_id)
    exchange.load_markets()
    return exchange


def fetch_with_backoff(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    since: int,
    limit: int = KLINE_LIMIT,
) -> list[list]:
    """Fetch OHLCV candles with exponential backoff on network/rate-limit errors.

    Args:
        exchange: CCXT exchange instance.
        symbol: Trading pair symbol (e.g. "BTC/USDT").
        timeframe: Candle interval (e.g. "1h").
        since: Start time in milliseconds since epoch.
        limit: Maximum candles per request.

    Returns:
        List of OHLCV candles [[timestamp, open, high, low, close, volume], ...].

    Raises:
        ccxt.NetworkError: After MAX_RETRIES exhausted.
        ccxt.ExchangeError: Non-retryable exchange errors.
    """
    backoff = INITIAL_BACKOFF_S
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
        except (ccxt.NetworkError, ccxt.RateLimitExceeded) as e:
            if attempt == MAX_RETRIES:
                logger.error("Max retries (%d) exhausted: %s", MAX_RETRIES, e)
                raise
            logger.warning(
                "Attempt %d/%d failed (%s), retrying in %.1fs ...",
                attempt,
                MAX_RETRIES,
                type(e).__name__,
                backoff,
            )
            time.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF_S)
    return []  # unreachable, satisfies type checker


def fetch_all_candles(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    since_ms: int,
) -> list[list]:
    """Paginate through Binance to fetch all full klines from since_ms to now.

    Uses the full Binance kline endpoint (12 fields) for real
    quote_volume and trade_count. Falls back to 6-field CCXT OHLCV
    if the full endpoint fails.

    Args:
        exchange: CCXT exchange instance.
        symbol: Trading pair symbol.
        timeframe: Candle interval.
        since_ms: Start time in ms since epoch.

    Returns:
        List of all kline rows fetched.
    """
    all_candles: list[list] = []
    current_since = since_ms
    use_full = True

    while True:
        logger.info(
            "Fetching from %s ...",
            pd.Timestamp(current_since, unit="ms", tz="UTC"),
        )
        try:
            if use_full:
                candles = fetch_with_full_klines(
                    exchange, symbol, timeframe, current_since
                )
            else:
                candles = fetch_with_backoff(
                    exchange, symbol, timeframe, current_since
                )
        except Exception as e:
            if use_full:
                logger.warning("Full kline fetch failed (%s), falling back to OHLCV", e)
                use_full = False
                continue
            raise

        if not candles:
            break

        all_candles.extend(candles)
        logger.info("  Got %d candles (total: %d)", len(candles), len(all_candles))

        # If we got fewer than the limit, we've reached the end
        if len(candles) < KLINE_LIMIT:
            break

        # Move to the next batch (last candle's time + 1 hour)
        last_ts = int(candles[-1][0])
        current_since = last_ts + ONE_HOUR_MS

    return all_candles


def fetch_full_klines(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    since_ms: int,
    limit: int = KLINE_LIMIT,
) -> list[list]:
    """Fetch full Binance klines (including quote_volume and trade_count).

    Uses the Binance REST API directly via CCXT's public GET to retrieve
    all 12 kline fields, not just the 6-field OHLCV subset.

    Args:
        exchange: CCXT exchange instance.
        symbol: Trading pair symbol (e.g. "BTC/USDT").
        timeframe: Candle interval (e.g. "1h").
        since_ms: Start time in milliseconds since epoch.
        limit: Maximum candles per request.

    Returns:
        List of raw Binance kline rows (12 fields each).
    """
    market = exchange.market(symbol)
    params = {
        "symbol": market["id"],
        "interval": timeframe,
        "startTime": since_ms,
        "limit": limit,
    }
    return exchange.publicGetKlines(params)


def fetch_with_full_klines(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    since: int,
    limit: int = KLINE_LIMIT,
) -> list[list]:
    """Fetch full klines with exponential backoff on network/rate-limit errors.

    Args:
        exchange: CCXT exchange instance.
        symbol: Trading pair symbol (e.g. "BTC/USDT").
        timeframe: Candle interval (e.g. "1h").
        since: Start time in milliseconds since epoch.
        limit: Maximum candles per request.

    Returns:
        List of raw Binance kline rows.

    Raises:
        ccxt.NetworkError: After MAX_RETRIES exhausted.
        ccxt.ExchangeError: Non-retryable exchange errors.
    """
    backoff = INITIAL_BACKOFF_S
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return fetch_full_klines(exchange, symbol, timeframe, since, limit)
        except (ccxt.NetworkError, ccxt.RateLimitExceeded) as e:
            if attempt == MAX_RETRIES:
                logger.error("Max retries (%d) exhausted: %s", MAX_RETRIES, e)
                raise
            logger.warning(
                "Attempt %d/%d failed (%s), retrying in %.1fs ...",
                attempt,
                MAX_RETRIES,
                type(e).__name__,
                backoff,
            )
            time.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF_S)
    return []  # unreachable, satisfies type checker


def source_label(exchange_id: str) -> str:
    """Return the source column value for a given exchange.

    Each exchange is a distinct venue. The source label encodes both
    the acquisition method (ccxt) and the specific venue so that
    reconcile.py can detect and reject cross-venue merges.

    Args:
        exchange_id: CCXT exchange identifier (e.g. "binance", "binanceus").

    Returns:
        Source string like "ccxt_binance" or "ccxt_binanceus".
    """
    return f"ccxt_{exchange_id}"


def candles_to_dataframe(
    candles: list[list],
    exchange_id: str = "binance",
) -> pd.DataFrame:
    """Convert Binance kline rows to a schema-compliant DataFrame.

    Accepts either full 12-field Binance klines or 6-field CCXT OHLCV.
    Full klines provide real quote_volume and trade_count; 6-field
    fallback estimates quote_volume and sets trade_count to 0.

    Args:
        candles: List of kline rows. Each row is either 12 fields
            (full Binance) or 6 fields (CCXT OHLCV fallback).
        exchange_id: CCXT exchange id, used to set the source label.

    Returns:
        DataFrame matching the project OHLCV schema.
    """
    if not candles:
        return pd.DataFrame(columns=[
            "open_time_utc", "open", "high", "low", "close",
            "volume", "quote_volume", "trade_count",
            "ingested_at_utc", "source",
        ])

    if len(candles[0]) >= 12:
        # Full Binance kline: [open_time, open, high, low, close, volume,
        #   close_time, quote_volume, trade_count, taker_buy_base,
        #   taker_buy_quote, ignore]
        df = pd.DataFrame(candles, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trade_count",
            "taker_buy_base", "taker_buy_quote", "ignore",
        ])
        df = df[["timestamp", "open", "high", "low", "close",
                 "volume", "quote_volume", "trade_count"]]
    else:
        # 6-field CCXT OHLCV fallback
        df = pd.DataFrame(
            candles, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        logger.warning(
            "Using 6-field OHLCV: quote_volume estimated, trade_count=0"
        )
        df["quote_volume"] = df["volume"].astype(float) * df["close"].astype(float)
        df["trade_count"] = 0

    df["open_time_utc"] = pd.to_datetime(
        pd.to_numeric(df["timestamp"], errors="coerce"), unit="ms", utc=True
    )
    df = df.drop(columns=["timestamp"])

    # Ensure dtypes
    for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
    df["trade_count"] = pd.to_numeric(df["trade_count"], errors="coerce").fillna(0).astype("int64")

    # Enforce ms resolution and schema-compliant metadata dtypes
    df["open_time_utc"] = df["open_time_utc"].astype("datetime64[ms, UTC]")
    src = source_label(exchange_id)
    df["source"] = pd.array([src] * len(df), dtype="string")
    df["ingested_at_utc"] = pd.Timestamp.now(tz="UTC").floor("ms")
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")

    # Reorder columns
    df = df[
        [
            "open_time_utc",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_volume",
            "trade_count",
            "ingested_at_utc",
            "source",
        ]
    ]

    df = df.sort_values("open_time_utc").reset_index(drop=True)
    return df


def main() -> int:
    """CLI entry point for incremental update.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(description="Incremental update via CCXT")
    parser.add_argument("--pair", type=str, default="BTCUSDT", help="Trading pair (no slash)")
    parser.add_argument("--interval", type=str, default="1h", help="Candle interval")
    parser.add_argument(
        "--exchange",
        type=str,
        default="binance",
        choices=sorted(SUPPORTED_EXCHANGES),
        help="CCXT exchange id (default: binance). binanceus is a separate "
        "venue with different data — do not mix with binance global",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fetched")
    args = parser.parse_args()

    # Map pair format: BTCUSDT → BTC/USDT
    symbol = f"{args.pair[:3]}/{args.pair[3:]}" if "/" not in args.pair else args.pair

    # Load existing data
    if not CANONICAL_PATH.exists():
        logger.error("Canonical file not found: %s", CANONICAL_PATH)
        logger.error("Run bulk_download.py first")
        return 1

    existing = pd.read_parquet(CANONICAL_PATH)
    latest = existing["open_time_utc"].max()
    logger.info("Existing data: %d rows, latest = %s", len(existing), latest)

    # Fetch from latest + 1 hour
    since_ms = int(latest.timestamp() * 1000) + ONE_HOUR_MS
    since_ts = pd.Timestamp(since_ms, unit="ms", tz="UTC")
    logger.info("Fetching new candles from %s", since_ts)

    if args.dry_run:
        print(f"Would fetch {symbol} {args.interval} from {since_ts} to now")
        return 0

    exchange = create_exchange(args.exchange)
    candles = fetch_all_candles(exchange, symbol, args.interval, since_ms)

    if not candles:
        logger.info("No new candles available")
        return 0

    df = candles_to_dataframe(candles, exchange_id=args.exchange)
    logger.info("Fetched %d new rows (source=%s)", len(df), source_label(args.exchange))
    logger.info(
        "New data range: %s to %s",
        df["open_time_utc"].iloc[0],
        df["open_time_utc"].iloc[-1],
    )

    # Validate new rows
    from ingestion.validators import validate_ohlcv

    report = validate_ohlcv(df)
    logger.info("New data validation: %s", report["overall_status"])

    if report["overall_status"] == "FAIL":
        logger.error("New data failed validation — aborting")
        return 1

    # Save update file for reconcile.py
    df.to_parquet(UPDATE_PATH, engine="pyarrow", index=False)
    logger.info("Saved %d new rows to %s", len(df), UPDATE_PATH)
    logger.info("Run reconcile.py to merge into canonical dataset")

    return 0


if __name__ == "__main__":
    sys.exit(main())
