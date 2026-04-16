"""
Bulk download historical BTC/USDT 1h klines from Binance Vision.

Downloads monthly ZIP archives from https://data.binance.vision/,
parses CSVs, concatenates, renames columns to match schema, adds
source and ingested_at_utc metadata, runs validators, and saves
to data/raw/btcusdt_1h.parquet.

Usage:
    python -m ingestion.bulk_download --pair BTCUSDT --interval 1h --start 2020-01
    python -m ingestion.bulk_download --pair BTCUSDT --interval 1h --start 2020-01 --end 2024-12
    python -m ingestion.bulk_download --pair BTCUSDT --interval 1h --start 2020-01 --dry-run
"""

from __future__ import annotations

import argparse
import io
import logging
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import yaml

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
SCHEMAS_PATH = PROJECT_ROOT / "config" / "schemas.yaml"
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"
QUALITY_DIR = PROJECT_ROOT / "data" / "quality"

BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"

# Binance Vision kline CSV has no header; these are the column names in order
BINANCE_CSV_COLUMNS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "trade_count",
    "taker_buy_base",
    "taker_buy_quote",
    "ignore",
]

COLUMNS_TO_KEEP = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "trade_count",
]


def load_schema() -> dict:
    """Load the OHLCV schema from config/schemas.yaml.

    Returns:
        dict: The parsed YAML schema definition, or empty dict if not found.
    """
    if SCHEMAS_PATH.exists():
        with open(SCHEMAS_PATH) as f:
            return yaml.safe_load(f)
    return {}


def generate_month_keys(start: str, end: str | None = None) -> list[str]:
    """Generate list of YYYY-MM month strings from start to end.

    Args:
        start: Start month in YYYY-MM format (e.g. "2020-01").
        end: End month in YYYY-MM format. If None, uses current month.

    Returns:
        List of month strings in YYYY-MM format.
    """
    start_year, start_month = map(int, start.split("-"))
    if end:
        end_year, end_month = map(int, end.split("-"))
    else:
        now = datetime.now(timezone.utc)
        end_year = now.year
        end_month = now.month

    months: list[str] = []
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        months.append(f"{year:04d}-{month:02d}")
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months


def download_month(pair: str, interval: str, month_key: str) -> pd.DataFrame | None:
    """Download and parse a single monthly kline ZIP from Binance Vision.

    Args:
        pair: Trading pair (e.g. "BTCUSDT").
        interval: Candle interval (e.g. "1h").
        month_key: Month in YYYY-MM format.

    Returns:
        DataFrame with parsed kline data, or None if the month is not available.
    """
    filename = f"{pair}-{interval}-{month_key}.zip"
    url = f"{BASE_URL}/{pair}/{interval}/{filename}"

    logger.info("Downloading %s ...", url)
    try:
        resp = requests.get(url, timeout=60)
    except requests.RequestException as e:
        logger.warning("Network error downloading %s: %s", month_key, e)
        return None

    if resp.status_code == 404:
        logger.warning("Month %s not available (404), skipping", month_key)
        return None
    if resp.status_code != 200:
        logger.warning("HTTP %d for %s, skipping", resp.status_code, month_key)
        return None

    try:
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            csv_names = [n for n in zf.namelist() if n.endswith(".csv")]
            if not csv_names:
                logger.warning("No CSV found in %s", filename)
                return None

            with zf.open(csv_names[0]) as csv_file:
                # Some Binance Vision CSVs have a header row, others don't.
                # Peek at the first line to detect which format we have.
                first_line = csv_file.readline().decode("utf-8", errors="replace")
                csv_file.seek(0)

                first_field = first_line.strip().split(",")[0]
                has_header = not first_field.isdigit()

                if has_header:
                    df = pd.read_csv(csv_file, header=0)
                    # Normalize: Binance header names vary, so rename
                    # positionally to our expected schema
                    df.columns = BINANCE_CSV_COLUMNS[: len(df.columns)]
                else:
                    # Count fields in the first data line to handle
                    # CSVs with more columns than our schema expects
                    n_fields = len(first_line.strip().split(","))
                    if n_fields > len(BINANCE_CSV_COLUMNS):
                        # Extra trailing columns — read all, then drop extras
                        col_names = BINANCE_CSV_COLUMNS + [
                            f"_extra_{i}" for i in range(n_fields - len(BINANCE_CSV_COLUMNS))
                        ]
                    else:
                        col_names = BINANCE_CSV_COLUMNS[:n_fields]
                    df = pd.read_csv(csv_file, header=None, names=col_names)

                # Force timestamp columns to int64 to prevent
                # float64 precision loss on large ms-epoch values
                for col in ["open_time", "close_time"]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    except (zipfile.BadZipFile, Exception) as e:
        logger.warning("Error parsing %s: %s", filename, e)
        return None

    logger.info("  Parsed %d rows for %s", len(df), month_key)
    return df


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw Binance CSV data to match the project schema.

    Keeps only required columns, renames open_time to open_time_utc,
    converts ms timestamps to timezone-aware UTC datetimes, adds
    source and ingested_at_utc metadata columns.

    Args:
        df: Raw concatenated DataFrame from Binance Vision CSVs.

    Returns:
        Processed DataFrame matching config/schemas.yaml.
    """
    # Keep only required columns
    df = df[COLUMNS_TO_KEEP].copy()

    # Rename open_time → open_time_utc
    df = df.rename(columns={"open_time": "open_time_utc"})

    # Convert ms timestamp to timezone-aware UTC datetime
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], unit="ms", utc=True)

    # Sanity check: all timestamps must be in a reasonable range (2017-2035).
    # Bad column alignment or wrong unit produces years like 58217.
    min_valid = pd.Timestamp("2017-01-01", tz="UTC")
    max_valid = pd.Timestamp("2035-01-01", tz="UTC")
    bad_mask = (df["open_time_utc"] < min_valid) | (df["open_time_utc"] > max_valid)
    n_bad = int(bad_mask.sum())
    if n_bad > 0:
        logger.warning(
            "Dropped %d rows with out-of-range timestamps (bad column alignment?)", n_bad
        )
        df = df[~bad_mask].reset_index(drop=True)

    # Ensure correct dtypes
    for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
        df[col] = df[col].astype("float64")
    df["trade_count"] = df["trade_count"].astype("int64")

    # Add metadata columns
    df["source"] = "binance_vision"
    df["ingested_at_utc"] = pd.Timestamp.now(tz="UTC")

    # Sort by primary key
    df = df.sort_values("open_time_utc").reset_index(drop=True)

    # Deduplicate (shouldn't happen but safety net)
    before = len(df)
    df = df.drop_duplicates(subset=["open_time_utc"], keep="first").reset_index(drop=True)
    after = len(df)
    if before != after:
        logger.warning("Removed %d duplicate rows", before - after)

    return df


def main() -> int:
    """CLI entry point for bulk download.

    Returns:
        Exit code: 0 on success, 1 on validation failure.
    """
    parser = argparse.ArgumentParser(description="Bulk download OHLCV data from Binance Vision")
    parser.add_argument("--pair", type=str, default="BTCUSDT", help="Trading pair")
    parser.add_argument("--interval", type=str, default="1h", help="Candle interval")
    parser.add_argument("--start", type=str, required=True, help="Start month (YYYY-MM)")
    parser.add_argument("--end", type=str, default=None, help="End month (YYYY-MM), default=now")
    parser.add_argument("--dry-run", action="store_true", help="List months but don't download")
    parser.add_argument(
        "--output", type=str, default=str(OUTPUT_PATH), help="Output parquet path"
    )
    args = parser.parse_args()

    month_keys = generate_month_keys(args.start, args.end)
    logger.info("Will download %d months: %s to %s", len(month_keys), month_keys[0], month_keys[-1])

    if args.dry_run:
        for mk in month_keys:
            print(f"  Would download: {args.pair}/{args.interval}/{mk}")
        return 0

    # Download all months
    all_dfs: list[pd.DataFrame] = []
    for mk in month_keys:
        df = download_month(args.pair, args.interval, mk)
        if df is not None:
            all_dfs.append(df)

    if not all_dfs:
        logger.error("No data downloaded")
        return 1

    logger.info("Concatenating %d monthly DataFrames ...", len(all_dfs))
    raw_df = pd.concat(all_dfs, ignore_index=True)
    logger.info("Total raw rows: %d", len(raw_df))

    # Process to match schema
    df = process_dataframe(raw_df)
    logger.info("Processed rows: %d", len(df))
    logger.info(
        "Date range: %s to %s",
        df["open_time_utc"].iloc[0],
        df["open_time_utc"].iloc[-1],
    )

    # Run validators
    from ingestion.validators import save_report, validate_ohlcv

    report = validate_ohlcv(df)
    report["file_checked"] = str(args.output)

    logger.info("Validation status: %s", report["overall_status"])
    for check_name, result in report["checks"].items():
        status = result.get("passed", None)
        count = result.get("count", None)
        if status is not None:
            logger.info("  %-25s %s", check_name, "PASS" if status else "FAIL/WARN")
        elif count is not None:
            logger.info("  %-25s %d flagged", check_name, count)

    # Save validation report
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    save_report(report, QUALITY_DIR, prefix="bulk_validation")

    # Save parquet
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, engine="pyarrow", index=False)
    logger.info("Saved %d rows to %s", len(df), output_path)

    if report["overall_status"] == "FAIL":
        logger.error("Validation FAILED — review quality report")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
