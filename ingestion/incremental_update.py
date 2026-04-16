"""
Incremental update of BTC/USDT 1h klines via CCXT (Binance).

Reads the existing canonical parquet, finds the latest timestamp,
fetches new candles from (latest + 1h) to now via CCXT, validates
new rows, then hands off to reconcile.py for merge.

Uses CCXT's built-in rate limiter + custom exponential backoff
for NetworkError / RateLimitExceeded (start 1s, max 60s, 5 retries).

Usage:
    python -m ingestion.incremental_update --pair BTCUSDT --interval 1h
    python -m ingestion.incremental_update --pair BTCUSDT --interval 1h --dry-run
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


def create_exchange() -> ccxt.binance:
    """Create a CCXT Binance exchange instance with rate limiting enabled.

    Returns:
        ccxt.binance: Configured exchange instance.
    """
    exchange = ccxt.binance({"enableRateLimit": True})
    return exchange


def fetch_with_backoff(
    exchange: ccxt.binance,
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
    exchange: ccxt.binance,
    symbol: str,
    timeframe: str,
    since_ms: int,
) -> list[list]:
    """Paginate through CCXT to fetch all candles from since_ms to now.

    Args:
        exchange: CCXT exchange instance.
        symbol: Trading pair symbol.
        timeframe: Candle interval.
        since_ms: Start time in ms since epoch.

    Returns:
        List of all OHLCV candles fetched.
    """
    all_candles: list[list] = []
    current_since = since_ms

    while True:
        logger.info(
            "Fetching from %s ...",
            pd.Timestamp(current_since, unit="ms", tz="UTC"),
        )
        candles = fetch_with_backoff(exchange, symbol, timeframe, current_since)
        if not candles:
            break

        all_candles.extend(candles)
        logger.info("  Got %d candles (total: %d)", len(candles), len(all_candles))

        # If we got fewer than the limit, we've reached the end
        if len(candles) < KLINE_LIMIT:
            break

        # Move to the next batch (last candle's time + 1 hour)
        current_since = candles[-1][0] + ONE_HOUR_MS

    return all_candles


def candles_to_dataframe(candles: list[list]) -> pd.DataFrame:
    """Convert CCXT OHLCV candle list to a schema-compliant DataFrame.

    Args:
        candles: List of [timestamp_ms, open, high, low, close, volume] lists.

    Returns:
        DataFrame matching the project OHLCV schema.
    """
    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])

    df["open_time_utc"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.drop(columns=["timestamp"])

    # CCXT doesn't provide quote_volume and trade_count; fill with defaults
    df["quote_volume"] = df["volume"] * df["close"]
    df["trade_count"] = 0  # CCXT basic endpoint doesn't provide this

    # Ensure dtypes
    for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
        df[col] = df[col].astype("float64")
    df["trade_count"] = df["trade_count"].astype("int64")

    # Add metadata
    df["source"] = "ccxt_api"
    df["ingested_at_utc"] = pd.Timestamp.now(tz="UTC")

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

    exchange = create_exchange()
    candles = fetch_all_candles(exchange, symbol, args.interval, since_ms)

    if not candles:
        logger.info("No new candles available")
        return 0

    df = candles_to_dataframe(candles)
    logger.info("Fetched %d new rows", len(df))
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
