"""Bulk download Binance Vision USDT-M open-interest metrics for BTCUSDT.

Mirrors ingestion/bulk_download.py (incl. HEADER-AUTODETECT — the metrics CSV carries a
header row, unlike headerless klines; §38.2). Source (daily partitions, ~5-min cadence):
  data/futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-YYYY-MM-DD.zip
Columns (header): create_time, symbol, sum_open_interest, sum_open_interest_value, ...
create_time is a UTC datetime STRING. Keep the two OI columns; sum_open_interest (contracts)
is the signal, sum_open_interest_value (notional) is a cross-check only. The parsed 5-min
frame is downsampled to 1h by downsample_oi_to_1h (Task A3) before write.
NOTE (§38.1): the EXACT metrics schema/header/cadence is re-verified at the A7 integration run.

Usage:
    python -m ingestion.oi_bulk_download --pair BTCUSDT --start 2020-09
    python -m ingestion.oi_bulk_download --pair BTCUSDT --start 2020-09 --dry-run
"""

from __future__ import annotations

import argparse
import io
import logging
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
# OUTPUT_PATH is deliberately NOT defined here — Task A3 wires the downsample + write.
# This module produces a 5-min concatenated frame; A3 extends main() to downsample + save.

BASE_URL = "https://data.binance.vision"
METRICS_PREFIX = "data/futures/um/daily/metrics/BTCUSDT/"

_REQUIRED = ["create_time", "sum_open_interest", "sum_open_interest_value"]

# Positional column names for the headerless defensive path (8-col metrics schema).
# NOTE (§38.1): verified/adjusted at A7 integration run.
_HEADERLESS_COLS = [
    "create_time", "symbol", "sum_open_interest", "sum_open_interest_value",
    "count_toptrader_long_short_ratio", "sum_toptrader_long_short_ratio",
    "count_long_short_ratio", "sum_taker_long_short_vol_ratio",
]


def _is_header_field(first_field: str) -> bool:
    """Return True if first_field is a header token (NOT parseable as a UTC timestamp).

    'create_time' -> True (header row present).
    '2020-09-01 00:00:00' -> False (data row; no header).

    Rationale: pd.to_datetime with utc=True raises / returns NaT on non-datetime strings
    such as 'create_time', while valid datetime strings parse cleanly. This avoids the
    digits-only trap that a naive strip-separators-and-isdigit check falls into (a datetime
    string contains digits but is NOT a pure epoch integer).

    Args:
        first_field: The first comma-separated token from the CSV's first line.

    Returns:
        True if the field is a header token; False if it is a valid timestamp.
    """
    try:
        result = pd.to_datetime(first_field.strip(), utc=True)
        return bool(pd.isna(result))
    except (ValueError, TypeError, OverflowError):
        return True


def parse_metrics_csv(path: Path) -> pd.DataFrame:
    """Parse one Binance Vision metrics CSV (HEADER-autodetect), keeping the OI columns.

    Handles both header-present (normal Binance Vision metrics format) and headerless
    (defensive fallback) variants by inspecting the first field of the first line.

    Inputs:
        path: A Binance Vision metrics CSV (daily partition, ~5-min cadence).
    Output schema:
        open_time_utc  datetime64[ms, UTC]  — parsed from create_time (UTC string)
        sum_open_interest      float64       — contracts (the signal series)
        sum_open_interest_value float64      — notional (cross-check / diagnostic only)
        source         string               — always "binance_vision"
        ingested_at_utc datetime64[ms, UTC]  — write timestamp
    Warmup period: none (timestamp conversion only).
    Null policy: rows with NaN create_time or sum_open_interest are dropped + counted (logged).

    Args:
        path: Path to the metrics CSV file.

    Returns:
        DataFrame with open_time_utc, sum_open_interest, sum_open_interest_value,
        source, ingested_at_utc, sorted ascending by open_time_utc.

    Raises:
        ValueError: If required columns are absent after header detection.
    """
    first_line = path.read_text().splitlines()[0]
    first_field = first_line.split(",")[0].strip()
    has_header = _is_header_field(first_field)

    if has_header:
        raw = pd.read_csv(path, header=0)
    else:
        # Defensive positional fallback — metrics normally has a header.
        n_cols = len(first_line.split(","))
        col_names = _HEADERLESS_COLS[:n_cols]
        raw = pd.read_csv(path, header=None, names=col_names)

    missing = [c for c in _REQUIRED if c not in raw.columns]
    if missing:
        raise ValueError(
            f"parse_metrics_csv: missing required columns {missing} in {path.name}"
        )

    n_in = len(raw)
    raw = raw.dropna(subset=["create_time", "sum_open_interest"])
    n_dropped = n_in - len(raw)
    if n_dropped:
        logger.info("parse_metrics_csv: dropped %d NaN row(s) from %s", n_dropped, path.name)

    df = pd.DataFrame({
        "open_time_utc": (
            pd.to_datetime(raw["create_time"], utc=True).astype("datetime64[ms, UTC]")
        ),
        "sum_open_interest": raw["sum_open_interest"].astype("float64"),
        "sum_open_interest_value": raw["sum_open_interest_value"].astype("float64"),
    })
    df["source"] = pd.array(["binance_vision"] * len(df), dtype="string")
    df["ingested_at_utc"] = pd.Timestamp(datetime.now(timezone.utc))
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")
    return df.sort_values("open_time_utc").reset_index(drop=True)


def generate_day_keys(start: str, end: str | None = None) -> list[str]:
    """Generate list of YYYY-MM-DD day strings from start month to end month (inclusive).

    Args:
        start: Start month in YYYY-MM format (e.g. "2020-09").
        end: End month in YYYY-MM format. If None, uses current month.

    Returns:
        List of YYYY-MM-DD strings for every calendar day in the range.
    """
    start_year, start_month = map(int, start.split("-"))
    if end:
        end_year, end_month = map(int, end.split("-"))
    else:
        now = datetime.now(timezone.utc)
        end_year, end_month = now.year, now.month

    # Build a date range covering the full months.
    start_date = pd.Timestamp(year=start_year, month=start_month, day=1)
    # Last day of end_month
    end_date = (
        pd.Timestamp(year=end_year, month=end_month, day=1)
        + pd.offsets.MonthEnd(1)
    )
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    return [d.strftime("%Y-%m-%d") for d in dates]


def _download_day(pair: str, day_key: str) -> pd.DataFrame | None:
    """Download and parse a single daily metrics ZIP from Binance Vision.

    Args:
        pair: Trading pair (e.g. "BTCUSDT").
        day_key: Day in YYYY-MM-DD format.

    Returns:
        Parsed DataFrame for that day, or None if unavailable / parse error.
    """
    filename = f"{pair}-metrics-{day_key}.zip"
    url = f"{BASE_URL}/{METRICS_PREFIX}{filename}"

    logger.info("Downloading %s ...", url)
    try:
        resp = requests.get(url, timeout=60)
    except requests.RequestException as e:
        logger.warning("Network error downloading %s: %s", day_key, e)
        return None

    if resp.status_code == 404:
        logger.warning("Day %s not available (404), skipping", day_key)
        return None
    if resp.status_code != 200:
        logger.warning("HTTP %d for %s, skipping", resp.status_code, day_key)
        return None

    try:
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            csv_names = [n for n in zf.namelist() if n.endswith(".csv")]
            if not csv_names:
                logger.warning("No CSV found in %s", filename)
                return None
            with zf.open(csv_names[0]) as csv_file:
                tmp = Path(f"/tmp/{filename}.csv")
                tmp.write_bytes(csv_file.read())
        df = parse_metrics_csv(tmp)
        tmp.unlink(missing_ok=True)
    except (zipfile.BadZipFile, Exception) as exc:
        logger.warning("Error parsing %s: %s", filename, exc)
        return None

    logger.info("  Parsed %d rows for %s", len(df), day_key)
    return df


OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_oi_1h.parquet"


def downsample_oi_to_1h(df5: pd.DataFrame) -> pd.DataFrame:
    """Causally downsample a ~5-min OI frame to the 1h grid: each 1h bar N (covering
    [N, N+1h)) takes the LAST 5-min observation WITHIN the bar (timestamps strictly
    < N+1h) = the bar-N-close OI (the mark_close analog). Strictly causal — row N uses
    only observations with timestamp < N+1h. No future read; gaps NOT interpolated.

    Inputs:
        df5: 5-min frame with columns open_time_utc (UTC tz-aware datetime),
            sum_open_interest (float64), sum_open_interest_value (float64), source (str).
    Computation:
        1. Sort by open_time_utc, set as index.
        2. resample("1h", label="left", closed="left").last(): each 1h bin is [N, N+1h),
           stamped at N. closed="left" excludes the N+1h boundary obs from bar N.
           label="left" stamps the bin at N (the OHLCV open_time_utc grid convention).
           .last() takes the final obs within [N, N+1h) = the bar-N-close OI.
        3. Drop any 1h bins where sum_open_interest is NaN (hour-gaps; NOT interpolated).
        4. Restore open_time_utc as a datetime64[ms, UTC] column; attach source +
           ingested_at_utc from the input frame (or now() if absent).
    Output:
        1h frame with columns (open_time_utc, sum_open_interest, sum_open_interest_value,
        source, ingested_at_utc), sorted ascending by open_time_utc.
    Warmup period: N/A (aggregation only; no rolling window).
    Null policy: 1h bins with no within-bar obs yield NaN and are dropped (flagged
        downstream by the validator). No interpolation or forward-fill.

    Args:
        df5: ~5-min OI DataFrame as produced by parse_metrics_csv / concat.

    Returns:
        1h aligned DataFrame, open_time_utc on the OHLCV open_time grid.
    """
    s = df5.sort_values("open_time_utc").set_index("open_time_utc")
    # label='left', closed='left' -> each 1h bin is [N, N+1h), stamped at N.
    # .last() takes the final obs WITHIN the bar (= bar-N-close OI, the mark_close analog).
    # Causal: row N uses only obs with timestamp in [N, N+1h); N+1h obs go to bar N+1.
    agg = s[["sum_open_interest", "sum_open_interest_value"]].resample(
        "1h", label="left", closed="left"
    ).last()
    # Drop hours with no within-bar observations (gaps not interpolated).
    agg = agg.dropna(subset=["sum_open_interest"])
    agg = agg.reset_index().rename(columns={"open_time_utc": "open_time_utc"})
    agg["open_time_utc"] = agg["open_time_utc"].astype("datetime64[ms, UTC]")
    agg["source"] = pd.array(["binance_vision"] * len(agg), dtype="string")
    if "ingested_at_utc" in df5.columns:
        ingested_at = df5["ingested_at_utc"].iloc[0]
    else:
        ingested_at = pd.Timestamp(datetime.now(timezone.utc)).as_unit("ms")
    agg["ingested_at_utc"] = ingested_at
    agg["ingested_at_utc"] = agg["ingested_at_utc"].astype("datetime64[ms, UTC]")
    return agg.sort_values("open_time_utc").reset_index(drop=True)


def main() -> int:
    """CLI entry point: download daily metrics ZIPs, parse to 5-min frame, log rows.

    Task A3 extends this function to downsample to 1h and write the parquet.
    This function assembles and returns the concatenated 5-min frame; the write
    is deferred to avoid calling the not-yet-defined downsample_oi_to_1h.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(
        description="Bulk download USDT-M OI metrics from Binance Vision (5-min, daily ZIPs)"
    )
    parser.add_argument("--pair", type=str, default="BTCUSDT", help="Trading pair")
    parser.add_argument("--start", type=str, required=True, help="Start month (YYYY-MM)")
    parser.add_argument("--end", type=str, default=None, help="End month (YYYY-MM), default=now")
    parser.add_argument("--dry-run", action="store_true", help="List days but don't download")
    args = parser.parse_args()

    day_keys = generate_day_keys(args.start, args.end)
    logger.info(
        "Will download %d days: %s to %s", len(day_keys), day_keys[0], day_keys[-1]
    )

    if args.dry_run:
        for dk in day_keys:
            print(f"  Would download: {METRICS_PREFIX}{args.pair}-metrics-{dk}.zip")
        return 0

    all_dfs: list[pd.DataFrame] = []
    for dk in day_keys:
        df = _download_day(args.pair, dk)
        if df is not None:
            all_dfs.append(df)

    if not all_dfs:
        logger.error("No OI metrics data downloaded")
        return 1

    logger.info("Concatenating %d daily DataFrames ...", len(all_dfs))
    combined = pd.concat(all_dfs, ignore_index=True)
    combined = combined.sort_values("open_time_utc").reset_index(drop=True)

    before = len(combined)
    combined = combined.drop_duplicates(subset=["open_time_utc"], keep="first").reset_index(drop=True)
    after = len(combined)
    if before != after:
        logger.warning("Removed %d duplicate rows", before - after)

    logger.info(
        "5-min frame: %d rows, %s to %s",
        len(combined),
        combined["open_time_utc"].iloc[0],
        combined["open_time_utc"].iloc[-1],
    )

    logger.info("Downsampling 5-min frame to 1h ...")
    df1h = downsample_oi_to_1h(combined)
    logger.info(
        "1h frame: %d rows, %s to %s",
        len(df1h),
        df1h["open_time_utc"].iloc[0],
        df1h["open_time_utc"].iloc[-1],
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df1h.to_parquet(OUTPUT_PATH, index=False)
    logger.info("Written 1h OI parquet: %s", OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
