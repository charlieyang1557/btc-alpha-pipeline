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

ALLOWED_SOURCES = {"binance_vision", "ccxt_api"}

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


def check_schema(df: pd.DataFrame) -> dict[str, Any]:
    """Verify all required columns are present with correct dtypes.

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

    # Check open_time_utc is datetime with UTC tz
    if "open_time_utc" in df.columns:
        if not hasattr(df["open_time_utc"].dtype, "tz") or df["open_time_utc"].dt.tz is None:
            issues.append("open_time_utc is not timezone-aware")
        elif str(df["open_time_utc"].dt.tz) != "UTC":
            issues.append(f"open_time_utc timezone is {df['open_time_utc'].dt.tz}, expected UTC")

    # Check ingested_at_utc is datetime with UTC tz
    if "ingested_at_utc" in df.columns:
        if not hasattr(df["ingested_at_utc"].dtype, "tz") or df["ingested_at_utc"].dt.tz is None:
            issues.append("ingested_at_utc is not timezone-aware")
        elif str(df["ingested_at_utc"].dt.tz) != "UTC":
            issues.append(
                f"ingested_at_utc timezone is {df['ingested_at_utc'].dt.tz}, expected UTC"
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
        dupe_timestamps = df.loc[dupes, "open_time_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ").tolist()
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

    timestamps = df["open_time_utc"].sort_values().reset_index(drop=True)
    diffs_ms = timestamps.diff().dt.total_seconds() * 1000
    # First diff is NaT → NaN, skip it
    gap_mask = diffs_ms[1:] != ONE_HOUR_MS
    gap_indices = gap_mask[gap_mask].index.tolist()

    if gap_indices:
        missing_intervals = []
        for idx in gap_indices:
            start = timestamps.iloc[idx - 1]
            end = timestamps.iloc[idx]
            missing_intervals.append(
                {
                    "after": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "before": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "missing_hours": int(diffs_ms.iloc[idx] / ONE_HOUR_MS) - 1,
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
        examples = ts[misaligned].head(10).dt.strftime("%Y-%m-%dT%H:%M:%SZ").tolist()
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
                    "timestamp": df.loc[idx, "open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
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
        timestamps = (
            df.loc[zero_mask, "open_time_utc"]
            .dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            .tolist()
        )
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
        flagged = (
            df.loc[drop_mask, "open_time_utc"]
            .dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            .tolist()
        )
        return {"count": drop_count, "details": flagged[:100]}
    return {"count": 0, "details": None}


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
    # WARNING: no_gaps, price_anomalies, zero_volume_bars, volume_drops
    warning_checks = ["no_gaps", "price_anomalies", "zero_volume_bars", "volume_drops"]

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


def save_report(report: dict[str, Any], report_dir: Path, prefix: str = "validation") -> Path:
    """Save a validation report as JSON.

    Args:
        report: The validation report dict from validate_ohlcv().
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
    parser = argparse.ArgumentParser(description="Validate OHLCV parquet data")
    parser.add_argument("--file", type=str, required=True, help="Path to parquet file")
    parser.add_argument("--report", type=str, default=None, help="Directory to save report")
    parser.add_argument("--dry-run", action="store_true", help="Print report but don't save")
    args = parser.parse_args()

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
