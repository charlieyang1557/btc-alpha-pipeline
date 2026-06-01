"""
Data validation for BTC Alpha Pipeline OHLCV data.

Implements all validation checks defined in PHASE0_BLUEPRINT.md and schemas.yaml:
- Timestamp integrity (timezone-aware UTC, no duplicates, no gaps, hour-aligned)
- Price integrity (positive, OHLC consistency, anomaly detection)
- Volume integrity (non-negative, zero-volume flagging, volume drop detection)
- Schema integrity (required columns, dtypes, no nulls, source populated)

Usage:
    python -m ingestion.validators --file data/raw/btcusdt_1h.parquet --report data/quality/
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
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
# Config helpers
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_PATH = PROJECT_ROOT / "config" / "schemas.yaml"

REQUIRED_COLUMNS = [
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

EXPECTED_DTYPES = {
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "volume": "float64",
    "quote_volume": "float64",
    "trade_count": "int64",
}

# Allowed source labels. Each encodes acquisition method + venue.
# "binance_vision" = bulk historical archive from Binance global.
# "ccxt_binance" = CCXT API against Binance global.
# "ccxt_binanceus" = CCXT API against Binance.US (separate venue).
ALLOWED_SOURCES = {"binance_vision", "ccxt_binance", "ccxt_binanceus"}


def _safe_ts_str(ts: pd.Timestamp) -> str:
    """Convert a pandas Timestamp to ISO string without crashing on out-of-range years.

    Args:
        ts: A pandas Timestamp (possibly with year > 9999 from bad data).

    Returns:
        ISO-formatted string, or str(ts) as fallback.
    """
    try:
        return ts.strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, NotImplementedError, OverflowError):
        return str(ts)


def _safe_ts_series(series: pd.Series) -> list[str]:
    """Convert a Series of Timestamps to ISO strings safely.

    Args:
        series: pandas Series of Timestamps.

    Returns:
        List of ISO-formatted strings with fallback for bad values.
    """
    try:
        return series.dt.strftime("%Y-%m-%dT%H:%M:%SZ").tolist()
    except (ValueError, NotImplementedError, OverflowError):
        return [str(v) for v in series]

ONE_HOUR_MS = 3_600_000


def load_schema() -> dict[str, Any]:
    """Load the OHLCV schema from config/schemas.yaml.

    Returns:
        dict: The parsed YAML schema definition.
    """
    if SCHEMAS_PATH.exists():
        with open(SCHEMAS_PATH) as f:
            return yaml.safe_load(f)
    return {}


# ---------------------------------------------------------------------------
# Individual check functions
# ---------------------------------------------------------------------------


def _check_datetime_col(df: pd.DataFrame, col: str, issues: list[str]) -> None:
    """Validate a datetime column for UTC tz and ms resolution.

    Args:
        df: DataFrame to check.
        col: Column name.
        issues: Mutable list to append issues to.
    """
    if col not in df.columns:
        return
    dtype = df[col].dtype
    if not hasattr(dtype, "tz") or df[col].dt.tz is None:
        issues.append(f"{col} is not timezone-aware")
    elif str(df[col].dt.tz) != "UTC":
        issues.append(f"{col} timezone is {df[col].dt.tz}, expected UTC")
    # Enforce ms resolution per schemas.yaml: datetime64[ms, UTC]
    dtype_str = str(dtype)
    if "datetime64" in dtype_str and "ms" not in dtype_str:
        issues.append(f"{col} has resolution {dtype_str}, expected datetime64[ms, UTC]")


def check_schema(df: pd.DataFrame) -> dict[str, Any]:
    """Verify all required columns are present with correct dtypes.

    Enforces:
    - All required columns present
    - Numeric columns are float64/int64
    - Datetime columns are datetime64[ms, UTC]
    - Source column is string (not object)

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'passed' (bool) and 'details' (list of issues found).
    """
    issues: list[str] = []

    # Check required columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        issues.append(f"Missing columns: {missing}")

    # Check numeric dtypes
    for col, expected in EXPECTED_DTYPES.items():
        if col in df.columns and str(df[col].dtype) != expected:
            issues.append(f"Column '{col}' has dtype {df[col].dtype}, expected {expected}")

    # Check datetime columns: UTC tz + ms resolution
    _check_datetime_col(df, "open_time_utc", issues)
    _check_datetime_col(df, "ingested_at_utc", issues)

    # Check source is string dtype (not object)
    if "source" in df.columns:
        if df["source"].dtype == "object":
            issues.append(
                f"Column 'source' has dtype object, expected string "
                f"(use pd.StringDtype() or astype('string'))"
            )

    return {"passed": len(issues) == 0, "details": issues if issues else None}


def check_no_nulls(df: pd.DataFrame) -> dict[str, Any]:
    """Verify no null/NaN values in core market fields.

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'passed' (bool) and 'details' (dict of columns with null counts).
    """
    core_fields = ["open", "high", "low", "close", "volume", "quote_volume", "trade_count"]
    present = [c for c in core_fields if c in df.columns]
    null_counts = {col: int(df[col].isna().sum()) for col in present if df[col].isna().any()}

    return {"passed": len(null_counts) == 0, "details": null_counts if null_counts else None}


def check_source_populated(df: pd.DataFrame) -> dict[str, Any]:
    """Verify the source column is populated for every row with valid values.

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'passed' (bool) and 'details' (dict of issues).
    """
    if "source" not in df.columns:
        return {"passed": False, "details": {"error": "source column missing"}}

    null_count = int(df["source"].isna().sum())
    empty_count = int((df["source"] == "").sum())
    invalid_values = set(df["source"].dropna().unique()) - ALLOWED_SOURCES
    issues: dict[str, Any] = {}

    if null_count > 0:
        issues["null_count"] = null_count
    if empty_count > 0:
        issues["empty_count"] = empty_count
    if invalid_values:
        issues["invalid_values"] = sorted(invalid_values)

    return {"passed": len(issues) == 0, "details": issues if issues else None}


def check_no_duplicates(df: pd.DataFrame) -> dict[str, Any]:
    """Verify no duplicate open_time_utc values.

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'passed' (bool) and 'details' (dict with duplicate info).
    """
    if "open_time_utc" not in df.columns:
        return {"passed": False, "details": {"error": "open_time_utc column missing"}}

    dupes = df["open_time_utc"].duplicated()
    dupe_count = int(dupes.sum())

    if dupe_count > 0:
        dupe_timestamps = _safe_ts_series(df.loc[dupes, "open_time_utc"])
        return {
            "passed": False,
            "details": {
                "duplicate_count": dupe_count,
                "duplicate_timestamps": dupe_timestamps[:50],
            },
        }
    return {"passed": True, "details": None}


def check_no_gaps(df: pd.DataFrame) -> dict[str, Any]:
    """Verify consecutive open_time_utc values differ by exactly 1 hour.

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'passed' (bool), 'details' (dict with gap info).
        Severity is 'warning' — gaps are flagged, not fatal.
    """
    if "open_time_utc" not in df.columns or len(df) < 2:
        return {"passed": True, "details": None}

    one_hour = pd.Timedelta(hours=1)
    timestamps = df["open_time_utc"].sort_values().reset_index(drop=True)
    diffs = timestamps.diff()
    # First diff is NaT, skip it
    gap_mask = diffs[1:] != one_hour
    gap_indices = gap_mask[gap_mask].index.tolist()

    if gap_indices:
        missing_intervals = []
        for idx in gap_indices:
            start = timestamps.iloc[idx - 1]
            end = timestamps.iloc[idx]
            gap_duration = diffs.iloc[idx]
            missing_hours = int(gap_duration / one_hour) - 1
            missing_intervals.append(
                {
                    "after": _safe_ts_str(start),
                    "before": _safe_ts_str(end),
                    "missing_hours": missing_hours,
                }
            )

        total_missing = sum(g["missing_hours"] for g in missing_intervals)
        return {
            "passed": False,
            "details": {
                "gaps_found": len(gap_indices),
                "total_missing_hours": total_missing,
                "missing_intervals": missing_intervals[:100],
            },
        }
    return {"passed": True, "details": None}


def check_hour_aligned(df: pd.DataFrame) -> dict[str, Any]:
    """Verify all timestamps are aligned to exact hour boundaries.

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'passed' (bool) and 'details' (dict with misaligned info).
    """
    if "open_time_utc" not in df.columns:
        return {"passed": False, "details": {"error": "open_time_utc column missing"}}

    ts = df["open_time_utc"]
    misaligned = (ts.dt.minute != 0) | (ts.dt.second != 0) | (ts.dt.microsecond != 0)
    misaligned_count = int(misaligned.sum())

    if misaligned_count > 0:
        examples = _safe_ts_series(ts[misaligned].head(10))
        return {
            "passed": False,
            "details": {"misaligned_count": misaligned_count, "examples": examples},
        }
    return {"passed": True, "details": None}


def check_prices_positive(df: pd.DataFrame) -> dict[str, Any]:
    """Verify all OHLC prices are strictly positive (> 0).

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'passed' (bool) and 'details' (dict of issues by column).
    """
    price_cols = ["open", "high", "low", "close"]
    present = [c for c in price_cols if c in df.columns]
    issues: dict[str, int] = {}

    for col in present:
        bad_count = int((df[col] <= 0).sum())
        if bad_count > 0:
            issues[col] = bad_count

    return {"passed": len(issues) == 0, "details": issues if issues else None}


def check_ohlc_consistency(df: pd.DataFrame) -> dict[str, Any]:
    """Verify OHLC bar consistency: high >= max(open,close), low <= min(open,close).

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'passed' (bool) and 'details' (dict with violation counts).
    """
    required = ["open", "high", "low", "close"]
    if not all(c in df.columns for c in required):
        return {"passed": False, "details": {"error": "Missing OHLC columns"}}

    high_violations = int((df["high"] < df[["open", "close"]].max(axis=1)).sum())
    low_violations = int((df["low"] > df[["open", "close"]].min(axis=1)).sum())

    issues: dict[str, int] = {}
    if high_violations > 0:
        issues["high_below_max_open_close"] = high_violations
    if low_violations > 0:
        issues["low_above_min_open_close"] = low_violations

    return {"passed": len(issues) == 0, "details": issues if issues else None}


def check_price_anomalies(df: pd.DataFrame) -> dict[str, Any]:
    """Flag bars where close-to-close change exceeds 50%.

    This is a warning-level check. Extreme moves are real in crypto
    and should NOT be auto-removed.

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'count' (int) and 'details' (list of anomalous timestamps).
    """
    if "close" not in df.columns or "open_time_utc" not in df.columns or len(df) < 2:
        return {"count": 0, "details": None}

    pct_change = df["close"].pct_change().abs()
    anomaly_mask = pct_change > 0.50
    anomaly_count = int(anomaly_mask.sum())

    if anomaly_count > 0:
        anomalies = []
        for idx in df.index[anomaly_mask]:
            anomalies.append(
                {
                    "timestamp": _safe_ts_str(df.loc[idx, "open_time_utc"]),
                    "pct_change": round(float(pct_change.loc[idx]), 4),
                }
            )
        return {"count": anomaly_count, "details": anomalies[:50]}
    return {"count": 0, "details": None}


def check_volume_non_negative(df: pd.DataFrame) -> dict[str, Any]:
    """Verify all volume values are >= 0.

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'passed' (bool) and 'details' (dict of negative volume info).
    """
    vol_cols = ["volume", "quote_volume"]
    present = [c for c in vol_cols if c in df.columns]
    issues: dict[str, int] = {}

    for col in present:
        neg_count = int((df[col] < 0).sum())
        if neg_count > 0:
            issues[col] = neg_count

    return {"passed": len(issues) == 0, "details": issues if issues else None}


def check_zero_volume_bars(df: pd.DataFrame) -> dict[str, Any]:
    """Flag zero-volume bars. Do NOT auto-remove.

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'count' (int) and 'timestamps' (list of affected timestamps).
    """
    if "volume" not in df.columns or "open_time_utc" not in df.columns:
        return {"count": 0, "timestamps": []}

    zero_mask = df["volume"] == 0
    zero_count = int(zero_mask.sum())

    if zero_count > 0:
        timestamps = _safe_ts_series(df.loc[zero_mask, "open_time_utc"])
        return {"count": zero_count, "timestamps": timestamps[:200]}
    return {"count": 0, "timestamps": []}


def check_volume_drops(df: pd.DataFrame) -> dict[str, Any]:
    """Flag bars where volume drops > 95% vs rolling 24h median (possible partial candle).

    Args:
        df: The OHLCV DataFrame to validate.

    Returns:
        dict with 'count' (int) and 'details' (list of flagged timestamps).
    """
    if "volume" not in df.columns or "open_time_utc" not in df.columns or len(df) < 25:
        return {"count": 0, "details": None}

    rolling_median = df["volume"].rolling(window=24, min_periods=24).median()
    # Avoid division by zero
    safe_median = rolling_median.replace(0, np.nan)
    ratio = df["volume"] / safe_median
    drop_mask = ratio < 0.05  # drops > 95%
    # Exclude NaN rows from the rolling window warm-up
    drop_mask = drop_mask & ratio.notna()
    drop_count = int(drop_mask.sum())

    if drop_count > 0:
        flagged = _safe_ts_series(df.loc[drop_mask, "open_time_utc"])
        return {"count": drop_count, "details": flagged[:100]}
    return {"count": 0, "details": None}


def check_partial_last_candle(
    df: pd.DataFrame,
    now_utc: pd.Timestamp | None = None,
    timeframe_hours: int = 1,
) -> dict[str, Any]:
    """Check whether the last candle in the dataset is potentially partial.

    A candle is partial if its open_time + timeframe > now, meaning the
    candle period has not yet closed.

    Args:
        df: The OHLCV DataFrame to validate.
        now_utc: Current UTC time. Defaults to pd.Timestamp.now(tz="UTC").
        timeframe_hours: Candle duration in hours (default 1).

    Returns:
        dict with 'passed' (bool) and 'details' (dict with partial candle info).
        Severity is 'warning'.
    """
    if "open_time_utc" not in df.columns or len(df) == 0:
        return {"passed": True, "details": None}

    if now_utc is None:
        now_utc = pd.Timestamp.now(tz="UTC")

    last_open = df["open_time_utc"].max()
    candle_close = last_open + pd.Timedelta(hours=timeframe_hours)

    if candle_close > now_utc:
        return {
            "passed": False,
            "details": {
                "last_open_time": _safe_ts_str(last_open),
                "candle_close_time": _safe_ts_str(candle_close),
                "now_utc": _safe_ts_str(now_utc),
            },
        }
    return {"passed": True, "details": None}


# ---------------------------------------------------------------------------
# Main validation orchestrator
# ---------------------------------------------------------------------------


def validate_ohlcv(df: pd.DataFrame) -> dict[str, Any]:
    """Run all OHLCV validation checks and return a structured report.

    Args:
        df: The OHLCV DataFrame to validate. Must contain all columns
            defined in config/schemas.yaml.

    Returns:
        dict: Structured validation report with check results and overall status.
            overall_status is one of: "PASS", "WARNING", "FAIL".
    """
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Determine date range (use isoformat to handle out-of-range timestamps safely)
    date_range: dict[str, str | None] = {"start": None, "end": None}
    if "open_time_utc" in df.columns and len(df) > 0:
        sorted_ts = df["open_time_utc"].sort_values()
        date_range["start"] = str(sorted_ts.iloc[0])
        date_range["end"] = str(sorted_ts.iloc[-1])

    # Run all checks
    checks: dict[str, Any] = {}
    checks["schema"] = check_schema(df)
    checks["no_nulls"] = check_no_nulls(df)
    checks["source_populated"] = check_source_populated(df)
    checks["no_duplicates"] = check_no_duplicates(df)
    checks["no_gaps"] = check_no_gaps(df)
    checks["hour_aligned"] = check_hour_aligned(df)
    checks["prices_positive"] = check_prices_positive(df)
    checks["ohlc_consistency"] = check_ohlc_consistency(df)
    checks["price_anomalies"] = check_price_anomalies(df)
    checks["volume_non_negative"] = check_volume_non_negative(df)
    checks["zero_volume_bars"] = check_zero_volume_bars(df)
    checks["volume_drops"] = check_volume_drops(df)
    checks["partial_last_candle"] = check_partial_last_candle(df)

    # Determine overall status
    # FAIL: schema, no_nulls, no_duplicates, prices_positive, ohlc_consistency,
    #        volume_non_negative, source_populated, hour_aligned
    fatal_checks = [
        "schema",
        "no_nulls",
        "no_duplicates",
        "prices_positive",
        "ohlc_consistency",
        "volume_non_negative",
        "source_populated",
        "hour_aligned",
    ]
    # WARNING: no_gaps, price_anomalies, zero_volume_bars, volume_drops, partial_last_candle
    warning_checks = [
        "no_gaps", "price_anomalies", "zero_volume_bars", "volume_drops",
        "partial_last_candle",
    ]

    has_fatal = any(
        checks[name].get("passed") is False
        for name in fatal_checks
        if name in checks
    )
    has_warning = any(
        (checks[name].get("passed") is False or checks[name].get("count", 0) > 0)
        for name in warning_checks
        if name in checks
    )

    if has_fatal:
        overall_status = "FAIL"
    elif has_warning:
        overall_status = "WARNING"
    else:
        overall_status = "PASS"

    report = {
        "check_date_utc": now_utc,
        "file_checked": None,
        "row_count": len(df),
        "date_range": date_range,
        "checks": checks,
        "overall_status": overall_status,
    }

    return report


# ---------------------------------------------------------------------------
# Funding-rate validation (Path A — 8h settlement series)
# ---------------------------------------------------------------------------

# Allowed source labels for the funding settlement series.
# "binance_vision" = bulk historical archive; "ccxt_binance" = live incremental.
# (Funding is a separate file from OHLCV, so binanceus is not a valid source here.)
FUNDING_ALLOWED_SOURCES = {"binance_vision", "ccxt_binance"}

FUNDING_REQUIRED_COLUMNS = [
    "open_time_utc",
    "funding_rate",
    "funding_interval_hours",
    "ingested_at_utc",
    "source",
]


def validate_funding(df: pd.DataFrame) -> dict[str, Any]:
    """Validate the funding-rate settlement series against the funding schema.

    Checks (errors -> ok=False):
    - required columns present
    - open_time_utc is timezone-aware UTC
    - open_time_utc has no duplicates (unique primary key)
    - open_time_utc is strictly ascending (sorted)
    - funding_rate has no NaN (schema nullable: false)
    - funding_interval_hours is > 0 and not NaN for every row
    - source values are within FUNDING_ALLOWED_SOURCES, populated (no null/empty)

    Warnings (do NOT set ok=False):
    - settlement gaps (spacing != 8h) — flagged always (even alongside an
      error), never interpolated/removed

    Args:
        df: The funding DataFrame to validate.

    Returns:
        dict with keys "ok" (bool), "errors" (list[str]), "warnings" (list[str]),
        and "rows" (int).
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Required columns
    missing = [c for c in FUNDING_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
        # Without the PK column we cannot run the remaining checks meaningfully.
        return {"ok": False, "errors": errors, "warnings": warnings, "rows": len(df)}

    pk = df["open_time_utc"]

    # UTC tz-aware
    if not hasattr(pk.dtype, "tz") or pk.dt.tz is None:
        errors.append("open_time_utc is not timezone-aware")
    elif str(pk.dt.tz) != "UTC":
        errors.append(f"open_time_utc timezone is {pk.dt.tz}, expected UTC")

    # Unique PK (no duplicates)
    dupe_count = int(pk.duplicated().sum())
    if dupe_count > 0:
        errors.append(f"open_time_utc has {dupe_count} duplicate value(s)")

    # Strictly ascending (sorted)
    if not pk.is_monotonic_increasing or dupe_count > 0:
        errors.append("open_time_utc is not strictly ascending (sorted_pk)")

    # funding_rate present (schema nullable: false — no NaN allowed)
    nan_rate = int(df["funding_rate"].isna().sum())
    if nan_rate > 0:
        errors.append(f"funding_rate has {nan_rate} NaN value(s)")

    # funding_interval_hours > 0 per row (NaN is also invalid; NaN is not <= 0)
    interval = df["funding_interval_hours"]
    bad_interval = int((interval.isna() | (interval <= 0)).sum())
    if bad_interval > 0:
        errors.append(f"funding_interval_hours has {bad_interval} row(s) NaN or <= 0")

    # source populated + allowed
    src = df["source"]
    null_count = int(src.isna().sum())
    empty_count = int((src == "").sum())
    invalid_values = set(src.dropna().unique()) - FUNDING_ALLOWED_SOURCES
    if null_count > 0:
        errors.append(f"source has {null_count} null value(s)")
    if empty_count > 0:
        errors.append(f"source has {empty_count} empty value(s)")
    if invalid_values:
        errors.append(f"source has invalid value(s): {sorted(invalid_values)}")

    # Gap detection (warning only; flagged, never interpolated). A "gap" is a
    # MISSING settlement: spacing >= 1.5x the per-row funding interval. Binance
    # calc_time jitters a few ms off the nominal 00/08/16 boundary, so consecutive
    # spacings are 8h +/- a few ms — that sub-minute jitter is NOT a gap and must
    # not be flagged. Uses the per-row funding_interval_hours (never hardcodes 8h).
    # Always run per the schema's no_forward_fill "flag missing settlements" rule
    # — flagged even when an error is also present.
    if len(df) >= 2:
        s = df.sort_values("open_time_utc").reset_index(drop=True)
        diffs = s["open_time_utc"].diff().iloc[1:].reset_index(drop=True)
        expected = pd.to_timedelta(
            s["funding_interval_hours"].iloc[1:].reset_index(drop=True), unit="h"
        )
        # Skip rows whose interval is non-positive or NaN (already flagged as an
        # error above) so the gap computation cannot divide by zero / NaT.
        valid = expected > pd.Timedelta(0)
        gap_mask = valid & (diffs >= expected * 1.5)
        gap_count = int(gap_mask.sum())
        if gap_count > 0:
            missing = int(((diffs[gap_mask] / expected[gap_mask]).round() - 1).sum())
            warnings.append(
                f"{gap_count} settlement gap(s) (missing settlements; spacing >= 1.5x "
                f"interval, ~{missing} missing) flagged — not interpolated"
            )

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "rows": len(df),
    }


# ---------------------------------------------------------------------------
# Markprice validation (Path C — 1h mark + index price series)
# ---------------------------------------------------------------------------

# Allowed source labels for the markprice series. Mirrors OHLCV allowed sources,
# minus ccxt_binanceus (markprice klines are USDT-M futures; no Binance.US source).
MARKPRICE_ALLOWED_SOURCES = {"binance_vision", "ccxt_binance"}

MARKPRICE_REQUIRED_COLUMNS = [
    "open_time_utc",
    "mark_close",
    "index_close",
    "source",
    "ingested_at_utc",
]

# Maximum allowed (mark_close - index_close) / index_close ratio.
# A benign perp premium is typically <0.1%; 5% bounds real ingestion bugs
# without false-flagging legitimate divergences.
MARK_INDEX_WEDGE_TOL = 0.05


def validate_markprice(df: pd.DataFrame) -> dict[str, Any]:
    """Validate the markprice 1h series (mark_close + index_close) against the markprice schema.

    Inputs: DataFrame with open_time_utc(datetime64[ms,UTC] PK), mark_close(float64),
      index_close(float64), source(string), ingested_at_utc(datetime64[ms,UTC]).
    Computation: structural/PK checks + mark-vs-index cross-check.
    Warmup period: none.
    Output schema: {"ok": bool, "errors": list[str], "warnings": list[str], "rows": int}.
    Null policy: NaN in mark_close / index_close does NOT raise here (ingestion layer
      drops NaN rows before calling this function).

    Checks (errors -> ok=False):
    - required columns present
    - open_time_utc is timezone-aware UTC
    - open_time_utc has no duplicates (unique primary key)
    - open_time_utc is strictly ascending (sorted)
    - source values are within MARKPRICE_ALLOWED_SOURCES, populated (no null/empty)

    Warnings (do NOT set ok=False):
    - spacing gaps (consecutive spacing != 1h) — flagged, never interpolated/removed
    - mark-vs-index wedge exceeding MARK_INDEX_WEDGE_TOL (5%) in any row

    Args:
        df: The markprice DataFrame to validate.

    Returns:
        dict with keys "ok" (bool), "errors" (list[str]), "warnings" (list[str]),
        and "rows" (int).
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Required columns
    missing = [c for c in MARKPRICE_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
        return {"ok": False, "errors": errors, "warnings": warnings, "rows": len(df)}

    pk = df["open_time_utc"]

    # UTC tz-aware
    if not hasattr(pk.dtype, "tz") or pk.dt.tz is None:
        errors.append("open_time_utc is not timezone-aware")
    elif str(pk.dt.tz) != "UTC":
        errors.append(f"open_time_utc timezone is {pk.dt.tz}, expected UTC")

    # Unique PK (no duplicates)
    dupe_count = int(pk.duplicated().sum())
    if dupe_count > 0:
        errors.append(f"open_time_utc has {dupe_count} duplicate value(s)")

    # Strictly ascending (sorted)
    if not pk.is_monotonic_increasing or dupe_count > 0:
        errors.append("open_time_utc is not strictly ascending (sorted_pk)")

    # source populated + allowed
    src = df["source"]
    null_count = int(src.isna().sum())
    empty_count = int((src == "").sum())
    invalid_values = set(src.dropna().unique()) - MARKPRICE_ALLOWED_SOURCES
    if null_count > 0:
        errors.append(f"source has {null_count} null value(s)")
    if empty_count > 0:
        errors.append(f"source has {empty_count} empty value(s)")
    if invalid_values:
        errors.append(f"source has invalid value(s): {sorted(invalid_values)}")

    # Gap detection (warning only; flagged, never interpolated). Expected spacing is
    # exactly 1h (ONE_HOUR_MS ms). A gap is spacing >= 1.5x that. Sub-ms jitter is
    # handled at parse time so spacings here should be exact multiples of ONE_HOUR_MS.
    if len(df) >= 2:
        s = df.sort_values("open_time_utc").reset_index(drop=True)
        diffs = s["open_time_utc"].diff().iloc[1:]
        expected = pd.Timedelta(hours=1)
        gap_mask = diffs >= expected * 1.5
        gap_count = int(gap_mask.sum())
        if gap_count > 0:
            missing_hours = int(((diffs[gap_mask] / expected).round() - 1).sum())
            warnings.append(
                f"{gap_count} gap(s) in open_time_utc spacing (missing bars; ~{missing_hours} "
                f"missing hour(s)) flagged — not interpolated"
            )

    # Mark-vs-index cross-check (warning only). A large wedge suggests a parse error
    # or mismatched series rather than a real perp premium.
    if "mark_close" in df.columns and "index_close" in df.columns:
        index_safe = df["index_close"].replace(0, float("nan"))
        wedge = ((df["mark_close"] - df["index_close"]) / index_safe).abs()
        bad_count = int((wedge > MARK_INDEX_WEDGE_TOL).sum())
        if bad_count > 0:
            warnings.append(
                f"{bad_count} row(s) exceed mark-vs-index cross-check tolerance "
                f"({MARK_INDEX_WEDGE_TOL:.0%}): possible parse/alignment error"
            )

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "rows": len(df),
    }


def save_report(report: dict[str, Any], report_dir: Path, prefix: str = "validation") -> Path:
    """Save a validation report as JSON.

    Args:
        report: The validation report dict from validate_ohlcv() or
            validate_funding().
        report_dir: Directory to save the report in.
        prefix: Filename prefix (default: "validation").

    Returns:
        Path to the saved report file.
    """
    report_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"{prefix}_{date_str}.json"
    report_path = report_dir / filename
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    logger.info("Validation report saved to %s", report_path)
    return report_path


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point for running validators on a parquet file.

    Returns:
        Exit code: 0 on PASS/WARNING, 1 on FAIL.
    """
    parser = argparse.ArgumentParser(description="Validate OHLCV or funding parquet data")
    parser.add_argument("--file", type=str, default=None, help="Path to OHLCV parquet file")
    parser.add_argument(
        "--funding", type=str, default=None,
        help="Path to funding parquet file (validates the funding schema instead of OHLCV)",
    )
    parser.add_argument("--report", type=str, default=None, help="Directory to save report")
    parser.add_argument("--dry-run", action="store_true", help="Print report but don't save")
    args = parser.parse_args()

    if (args.file is None) == (args.funding is None):
        logger.error("Provide exactly one of --file (OHLCV) or --funding")
        return 1

    # Funding-validation path
    if args.funding is not None:
        file_path = Path(args.funding)
        if not file_path.exists():
            logger.error("File not found: %s", file_path)
            return 1
        logger.info("Loading funding %s ...", file_path)
        df = pd.read_parquet(file_path)
        logger.info("Loaded %d rows", len(df))

        report = validate_funding(df)
        report["file_checked"] = str(file_path)
        logger.info("Funding validation ok: %s", report["ok"])
        for err in report["errors"]:
            logger.error("  ERROR: %s", err)
        for warn in report["warnings"]:
            logger.warning("  WARN: %s", warn)

        if args.dry_run:
            print(json.dumps(report, indent=2, default=str))
        elif args.report:
            save_report(report, Path(args.report), prefix="funding_validation")

        return 0 if report["ok"] else 1

    # OHLCV-validation path
    file_path = Path(args.file)
    if not file_path.exists():
        logger.error("File not found: %s", file_path)
        return 1

    logger.info("Loading %s ...", file_path)
    df = pd.read_parquet(file_path)
    logger.info("Loaded %d rows", len(df))

    report = validate_ohlcv(df)
    report["file_checked"] = str(file_path)

    logger.info("Overall status: %s", report["overall_status"])

    # Log individual check results
    for check_name, result in report["checks"].items():
        status = result.get("passed", None)
        count = result.get("count", None)
        if status is not None:
            logger.info("  %-25s %s", check_name, "PASS" if status else "FAIL")
        elif count is not None:
            logger.info("  %-25s %d flagged", check_name, count)

    if args.dry_run:
        print(json.dumps(report, indent=2, default=str))
    elif args.report:
        save_report(report, Path(args.report))

    return 1 if report["overall_status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
