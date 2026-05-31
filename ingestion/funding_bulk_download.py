"""Bulk download Binance Vision USDT-M funding rate history for BTCUSDT.

Mirrors ingestion/bulk_download.py: download monthly ZIPs from
data.binance.vision, parse to parquet. (NOTE: bulk_download.py does NOT verify
checksums — there is no .CHECKSUM step to mirror.) Funding is an 8h settlement
series; calc_time is the settlement timestamp (UTC ms epoch).
Source: data/futures/um/monthly/fundingRate/BTCUSDT/ (history from 2020-01).

Usage:
    python -m ingestion.funding_bulk_download --pair BTCUSDT --start 2020-01
    python -m ingestion.funding_bulk_download --pair BTCUSDT --start 2020-01 --end 2024-12
    python -m ingestion.funding_bulk_download --pair BTCUSDT --start 2020-01 --dry-run
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
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_funding_8h.parquet"
ARCHIVE_DIR = PROJECT_ROOT / "data" / "raw" / "archive"
QUALITY_DIR = PROJECT_ROOT / "data" / "quality"

# Binance Vision USDT-M futures funding-rate monthly archives.
# data.binance.vision serves these under data/futures/um/monthly/fundingRate/.
VISION_PREFIX = "data/futures/um/monthly/fundingRate/BTCUSDT/"
BASE_URL = "https://data.binance.vision"


def _normalize_funding_raw(raw: pd.DataFrame, name: str) -> pd.DataFrame:
    """Normalize a raw fundingRate frame into the canonical funding schema.

    Shared by parse_funding_csv (headered file) and _parse_funding_buffer
    (headered/headerless in-memory buffer). Expects columns calc_time,
    funding_interval_hours, last_funding_rate.

    Output schema: open_time_utc(datetime64[ms,UTC] PK), funding_rate(float64),
      funding_interval_hours(int64), source(string), ingested_at_utc(datetime64[ms,UTC]).
    Null policy: rows with NaN calc_time/last_funding_rate are dropped + counted (logged).

    Args:
        raw: Raw parsed CSV frame.
        name: Source name (file/CSV) for logging.

    Returns:
        DataFrame matching the canonical funding schema (sorted, source=binance_vision).
    """
    n_in = len(raw)
    raw = raw.dropna(subset=["calc_time", "last_funding_rate"])     # drop + count NaN rows
    n_dropped = n_in - len(raw)
    if n_dropped:
        logger.info("_normalize_funding_raw: dropped %d NaN row(s) from %s", n_dropped, name)
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(raw["calc_time"], unit="ms", utc=True).astype("datetime64[ms, UTC]"),
        "funding_rate": raw["last_funding_rate"].astype("float64"),
        "funding_interval_hours": raw["funding_interval_hours"].astype("int64"),
    })
    df["source"] = pd.array(["binance_vision"] * len(df), dtype="string")   # schema 'string', not object
    df["ingested_at_utc"] = pd.Timestamp(datetime.now(timezone.utc)).as_unit("ms")
    return df.sort_values("open_time_utc").reset_index(drop=True)


def parse_funding_csv(path: Path) -> pd.DataFrame:
    """Parse one Binance Vision fundingRate CSV into the canonical funding schema.

    Inputs: a CSV with header calc_time,funding_interval_hours,last_funding_rate.
    Output schema: open_time_utc(datetime64[ms,UTC] PK), funding_rate(float64),
      funding_interval_hours(int64), source(string), ingested_at_utc(datetime64[ms,UTC]).
    Null policy: rows with NaN calc_time/last_funding_rate are dropped + counted (logged).
    """
    raw = pd.read_csv(path)
    return _normalize_funding_raw(raw, path.name)


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


def download_month(pair: str, month_key: str) -> pd.DataFrame | None:
    """Download and parse a single monthly fundingRate ZIP from Binance Vision.

    Args:
        pair: Trading pair (e.g. "BTCUSDT").
        month_key: Month in YYYY-MM format.

    Returns:
        DataFrame with parsed funding data, or None if the month is not available.
    """
    filename = f"{pair}-fundingRate-{month_key}.zip"
    url = f"{BASE_URL}/{VISION_PREFIX}{filename}"

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
            # Extract the CSV to a temp path so parse_funding_csv can read it.
            with zf.open(csv_names[0]) as csv_file:
                tmp = io.BytesIO(csv_file.read())
            df = _parse_funding_buffer(tmp, csv_names[0])
    except (zipfile.BadZipFile, Exception) as e:
        logger.warning("Error parsing %s: %s", filename, e)
        return None

    logger.info("  Parsed %d rows for %s", len(df), month_key)
    return df


def _parse_funding_buffer(buf: io.BytesIO, name: str) -> pd.DataFrame:
    """Parse a fundingRate CSV from an in-memory buffer into the funding schema.

    Some Binance Vision fundingRate CSVs are headerless; this mirrors the
    headered/headerless handling of bulk_download.py while reusing the same
    canonical column transform as parse_funding_csv.

    Args:
        buf: In-memory bytes buffer of the CSV contents.
        name: CSV filename (for logging only).

    Returns:
        DataFrame matching the canonical funding schema.
    """
    first_line = buf.readline().decode("utf-8", errors="replace")
    buf.seek(0)
    first_field = first_line.strip().split(",")[0]
    has_header = not first_field.replace(".", "").replace("-", "").isdigit()
    if has_header:
        raw = pd.read_csv(buf)
    else:
        raw = pd.read_csv(
            buf,
            header=None,
            names=["calc_time", "funding_interval_hours", "last_funding_rate"],
        )

    return _normalize_funding_raw(raw, name)


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Sort, enforce ms resolution, and deduplicate the concatenated funding frame.

    Args:
        df: Raw concatenated DataFrame from per-month parses.

    Returns:
        Processed DataFrame matching the funding schema (sorted, unique PK).
    """
    df = df.copy()
    df["open_time_utc"] = df["open_time_utc"].astype("datetime64[ms, UTC]")
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")
    df = df.sort_values("open_time_utc").reset_index(drop=True)

    before = len(df)
    df = df.drop_duplicates(subset=["open_time_utc"], keep="first").reset_index(drop=True)
    after = len(df)
    if before != after:
        logger.warning("Removed %d duplicate rows", before - after)
    return df


def main() -> int:
    """CLI entry point for funding bulk download.

    Returns:
        Exit code: 0 on success, 1 on validation/download failure.
    """
    parser = argparse.ArgumentParser(
        description="Bulk download USDT-M funding rate data from Binance Vision"
    )
    parser.add_argument("--pair", type=str, default="BTCUSDT", help="Trading pair")
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
            "Override the rule that only funding_reconcile.py modifies the "
            "canonical funding dataset. Use only for explicit re-bootstrap; "
            "the existing canonical is archived to data/raw/archive/ before "
            "overwrite. Normal updates should use funding_incremental_update.py "
            "+ funding_reconcile.py."
        ),
    )
    args = parser.parse_args()

    month_keys = generate_month_keys(args.start, args.end)
    logger.info(
        "Will download %d months: %s to %s", len(month_keys), month_keys[0], month_keys[-1]
    )

    if args.dry_run:
        for mk in month_keys:
            print(f"  Would download: {VISION_PREFIX}{args.pair}-fundingRate-{mk}.zip")
        return 0

    all_dfs: list[pd.DataFrame] = []
    for mk in month_keys:
        df = download_month(args.pair, mk)
        if df is not None:
            all_dfs.append(df)

    if not all_dfs:
        logger.error("No data downloaded")
        return 1

    logger.info("Concatenating %d monthly DataFrames ...", len(all_dfs))
    raw_df = pd.concat(all_dfs, ignore_index=True)
    logger.info("Total raw rows: %d", len(raw_df))

    df = process_dataframe(raw_df)
    logger.info("Processed rows: %d", len(df))
    logger.info(
        "Date range: %s to %s",
        df["open_time_utc"].iloc[0],
        df["open_time_utc"].iloc[-1],
    )

    # Run funding validator
    from ingestion.validators import save_report, validate_funding

    report = validate_funding(df)
    report["file_checked"] = str(args.output)
    logger.info("Validation ok: %s", report["ok"])
    for err in report["errors"]:
        logger.error("  ERROR: %s", err)
    for warn in report["warnings"]:
        logger.warning("  WARN: %s", warn)

    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    save_report(report, QUALITY_DIR, prefix="funding_bulk_validation")

    if not report["ok"]:
        logger.error("Validation FAILED — refusing to write parquet. Review quality report.")
        return 1

    # Canonical-write protection: refuse to overwrite an existing canonical
    # unless --force, which archives the existing file first. Mirrors
    # bulk_download.py.
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not args.force:
        logger.error(
            "Refusing to overwrite existing canonical file: %s. "
            "For normal updates, use:\n"
            "  python -m ingestion.funding_incremental_update --pair %s\n"
            "  python -m ingestion.funding_reconcile --existing %s --new <update>\n"
            "If you genuinely need to re-bootstrap, re-run with --force; the "
            "existing canonical will be archived to %s/ before overwrite.",
            output_path,
            args.pair,
            output_path,
            ARCHIVE_DIR,
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

    # Atomic-promote: write to staging, then rename.
    staging_path = output_path.with_suffix(output_path.suffix + ".staging")
    df.to_parquet(staging_path, engine="pyarrow", index=False)
    staging_path.replace(output_path)
    logger.info("Saved %d rows to %s", len(df), output_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
