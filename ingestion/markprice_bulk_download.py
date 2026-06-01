"""Bulk download Binance Vision USDT-M markPrice + indexPrice 1h klines for BTCUSDT.

Mirrors ingestion/bulk_download.py: download monthly ZIPs from data.binance.vision,
parse to parquet. (bulk_download.py does NOT verify checksums — no .CHECKSUM step to
mirror.) Mark/index klines are 12-col headerless; open_time is ms epoch UTC.
Sources:
  data/futures/um/monthly/markPriceKlines/BTCUSDT/1h/  (history from 2020-01)
  data/futures/um/monthly/indexPriceKlines/BTCUSDT/1h/ (history from 2020-01)

Usage:
    python -m ingestion.markprice_bulk_download --pair BTCUSDT --start 2020-01
    python -m ingestion.markprice_bulk_download --pair BTCUSDT --start 2020-01 --end 2024-12
    python -m ingestion.markprice_bulk_download --pair BTCUSDT --start 2020-01 --dry-run
"""

from __future__ import annotations

import argparse
import io
import logging
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

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
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_markprice_1h.parquet"
ARCHIVE_DIR = PROJECT_ROOT / "data" / "raw" / "archive"
QUALITY_DIR = PROJECT_ROOT / "data" / "quality"

BASE_URL = "https://data.binance.vision"
MARK_PREFIX = "data/futures/um/monthly/markPriceKlines/BTCUSDT/1h/"
INDEX_PREFIX = "data/futures/um/monthly/indexPriceKlines/BTCUSDT/1h/"

# Binance Vision *PriceKlines CSV: 12 headerless columns, in order.
_KLINE_COLS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_volume", "count", "taker_base", "taker_quote", "ignore",
]


def parse_kline_csv(path: Path, close_col_name: str) -> pd.DataFrame:
    """Parse one Binance Vision 12-col headerless kline CSV, keeping only the close.

    Inputs: a headerless CSV with the 12 standard Binance Vision kline columns
      (open_time ms epoch, open, high, low, close, volume, close_time,
      quote_volume, count, taker_base, taker_quote, ignore).
    Output: open_time_utc(datetime64[ms,UTC] PK), <close_col_name>(float64),
      source(string), ingested_at_utc(datetime64[ms,UTC]).
    Warmup period: none (timestamp conversion only).
    Null policy: rows with NaN open_time/close are dropped + counted (logged).

    Args:
        path: Path to the headerless CSV file.
        close_col_name: Column name to use for the close price (e.g. "mark_close").

    Returns:
        DataFrame with open_time_utc, <close_col_name>, source, ingested_at_utc.
    """
    raw = pd.read_csv(path, header=None, names=_KLINE_COLS)
    n_in = len(raw)
    raw = raw.dropna(subset=["open_time", "close"])
    n_dropped = n_in - len(raw)
    if n_dropped:
        logger.info("parse_kline_csv: dropped %d NaN row(s) from %s", n_dropped, path.name)
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(raw["open_time"], unit="ms", utc=True).astype("datetime64[ms, UTC]"),
        close_col_name: raw["close"].astype("float64"),
    })
    df["source"] = pd.array(["binance_vision"] * len(df), dtype="string")
    df["ingested_at_utc"] = pd.Timestamp(datetime.now(timezone.utc)).as_unit("ms")
    return df.sort_values("open_time_utc").reset_index(drop=True)


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


def _download_kline_month(prefix: str, pair: str, interval: str, month_key: str,
                          close_col_name: str) -> pd.DataFrame | None:
    """Download and parse a single monthly kline ZIP from Binance Vision.

    Args:
        prefix: URL prefix path (MARK_PREFIX or INDEX_PREFIX).
        pair: Trading pair (e.g. "BTCUSDT").
        interval: Candle interval (e.g. "1h").
        month_key: Month in YYYY-MM format.
        close_col_name: Column name to use for the close price.

    Returns:
        DataFrame with parsed kline data, or None if the month is not available.
    """
    filename = f"{pair}-{interval}-{month_key}.zip"
    url = f"{BASE_URL}/{prefix}{filename}"

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
                buf = io.BytesIO(csv_file.read())
        # Parse from the in-memory buffer using a temp Path workaround:
        # write to a temp file so parse_kline_csv (which takes a Path) can read it.
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp_path.write_bytes(buf.read())
        try:
            df = parse_kline_csv(tmp_path, close_col_name=close_col_name)
        finally:
            tmp_path.unlink(missing_ok=True)
    except (zipfile.BadZipFile, Exception) as e:
        logger.warning("Error parsing %s: %s", filename, e)
        return None

    logger.info("  Parsed %d rows for %s", len(df), month_key)
    return df


def main() -> int:
    """CLI entry point for markprice + indexprice bulk download.

    Downloads monthly mark-price and index-price kline ZIPs from Binance Vision,
    parses each, inner-joins the two series on open_time_utc, then writes
    the combined frame to OUTPUT_PATH.

    Returns:
        Exit code: 0 on success, 1 on download or join failure.
    """
    parser = argparse.ArgumentParser(
        description="Bulk download USDT-M markPrice + indexPrice klines from Binance Vision"
    )
    parser.add_argument("--pair", type=str, default="BTCUSDT", help="Trading pair")
    parser.add_argument("--interval", type=str, default="1h", help="Candle interval")
    parser.add_argument("--start", type=str, required=True, help="Start month (YYYY-MM)")
    parser.add_argument("--end", type=str, default=None, help="End month (YYYY-MM), default=now")
    parser.add_argument("--dry-run", action="store_true", help="List months but don't download")
    parser.add_argument(
        "--output", type=str, default=str(OUTPUT_PATH), help="Output parquet path"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Override the rule that only a reconcile step modifies the canonical "
            "markprice dataset. Use only for explicit re-bootstrap; the existing "
            "canonical is archived to data/raw/archive/ before overwrite."
        ),
    )
    args = parser.parse_args()

    month_keys = generate_month_keys(args.start, args.end)
    logger.info(
        "Will download %d months: %s to %s", len(month_keys), month_keys[0], month_keys[-1]
    )

    if args.dry_run:
        for mk in month_keys:
            print(f"  Would download: {MARK_PREFIX}{args.pair}-{args.interval}-{mk}.zip")
            print(f"  Would download: {INDEX_PREFIX}{args.pair}-{args.interval}-{mk}.zip")
        return 0

    # Download mark-price months
    mark_dfs: list[pd.DataFrame] = []
    for mk in month_keys:
        df = _download_kline_month(MARK_PREFIX, args.pair, args.interval, mk, "mark_close")
        if df is not None:
            mark_dfs.append(df)

    if not mark_dfs:
        logger.error("No mark-price data downloaded")
        return 1

    # Download index-price months
    index_dfs: list[pd.DataFrame] = []
    for mk in month_keys:
        df = _download_kline_month(INDEX_PREFIX, args.pair, args.interval, mk, "index_close")
        if df is not None:
            index_dfs.append(df)

    if not index_dfs:
        logger.error("No index-price data downloaded")
        return 1

    logger.info("Concatenating %d mark-price + %d index-price monthly DataFrames ...",
                len(mark_dfs), len(index_dfs))
    mark_df = pd.concat(mark_dfs, ignore_index=True)
    index_df = pd.concat(index_dfs, ignore_index=True)
    logger.info("Total raw rows: mark=%d, index=%d", len(mark_df), len(index_df))

    # Inner-join on open_time_utc: only keep bars present in both series.
    joined = mark_df.merge(
        index_df[["open_time_utc", "index_close"]],
        on="open_time_utc",
        how="inner",
    )
    logger.info("After inner join: %d rows (mark=%d, index=%d)",
                len(joined), len(mark_df), len(index_df))

    # Sort + deduplicate
    joined = joined.sort_values("open_time_utc").reset_index(drop=True)
    before = len(joined)
    joined = joined.drop_duplicates(subset=["open_time_utc"], keep="first").reset_index(drop=True)
    after = len(joined)
    if before != after:
        logger.warning("Removed %d duplicate rows", before - after)

    logger.info(
        "Date range: %s to %s",
        joined["open_time_utc"].iloc[0],
        joined["open_time_utc"].iloc[-1],
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not args.force:
        logger.error(
            "Refusing to overwrite existing canonical file: %s. "
            "Re-run with --force to archive the existing file and overwrite.",
            output_path,
        )
        return 1

    if output_path.exists() and args.force:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive_name = f"{output_path.stem}_{timestamp}{output_path.suffix}"
        archive_path = ARCHIVE_DIR / archive_name
        shutil.copy2(output_path, archive_path)
        logger.warning(
            "--force override: existing canonical %s archived to %s.",
            output_path,
            archive_path,
        )

    # Atomic-promote: write to staging path, then rename.
    staging_path = output_path.with_suffix(output_path.suffix + ".staging")
    joined.to_parquet(staging_path, engine="pyarrow", index=False)
    staging_path.replace(output_path)
    logger.info("Saved %d rows to %s", len(joined), output_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
