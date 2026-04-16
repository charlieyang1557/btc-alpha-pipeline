"""Tests for ingestion/validators.py using synthetic DataFrames.

Covers every validation check:
- Schema integrity
- Null detection
- Source validation
- Duplicate timestamps
- Gap detection
- Hour alignment
- Price positivity
- OHLC consistency
- Price anomaly detection
- Volume non-negative
- Zero volume bars
- Volume drop detection
- Overall status logic (PASS / WARNING / FAIL)
- Report saving
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ingestion.validators import (
    check_hour_aligned,
    check_no_duplicates,
    check_no_gaps,
    check_no_nulls,
    check_ohlc_consistency,
    check_partial_last_candle,
    check_price_anomalies,
    check_prices_positive,
    check_schema,
    check_source_populated,
    check_volume_drops,
    check_volume_non_negative,
    check_zero_volume_bars,
    save_report,
    validate_ohlcv,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_good_df(n_hours: int = 48, start: str = "2024-01-01T00:00:00") -> pd.DataFrame:
    """Create a fully valid synthetic OHLCV DataFrame.

    Args:
        n_hours: Number of hourly bars to generate.
        start: ISO start timestamp.

    Returns:
        A valid OHLCV DataFrame that should pass all checks.
    """
    timestamps = pd.date_range(start=start, periods=n_hours, freq="h", tz="UTC")
    rng = np.random.default_rng(42)

    base_price = 42000.0
    closes = base_price + rng.normal(0, 100, n_hours).cumsum()
    closes = np.maximum(closes, 100)  # ensure positive

    opens = closes + rng.normal(0, 20, n_hours)
    opens = np.maximum(opens, 100)
    highs = np.maximum(opens, closes) + rng.uniform(10, 200, n_hours)
    lows = np.minimum(opens, closes) - rng.uniform(10, 200, n_hours)
    lows = np.maximum(lows, 1)  # ensure positive

    volumes = rng.uniform(500, 3000, n_hours)
    quote_volumes = volumes * closes
    trade_counts = rng.integers(10000, 80000, n_hours)

    df = pd.DataFrame(
        {
            "open_time_utc": timestamps.astype("datetime64[ms, UTC]"),
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
            "quote_volume": quote_volumes,
            "trade_count": trade_counts.astype(np.int64),
            "ingested_at_utc": pd.Timestamp.now(tz="UTC").floor("ms"),
            "source": pd.array(["binance_vision"] * n_hours, dtype="string"),
        }
    )
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")
    return df


# ---------------------------------------------------------------------------
# Schema checks
# ---------------------------------------------------------------------------


class TestCheckSchema:
    def test_good_schema_passes(self):
        df = make_good_df()
        result = check_schema(df)
        assert result["passed"] is True
        assert result["details"] is None

    def test_missing_column_fails(self):
        df = make_good_df().drop(columns=["volume"])
        result = check_schema(df)
        assert result["passed"] is False
        assert "Missing columns" in result["details"][0]

    def test_wrong_dtype_fails(self):
        df = make_good_df()
        df["open"] = df["open"].astype("float32")
        result = check_schema(df)
        assert result["passed"] is False
        assert any("dtype" in d for d in result["details"])

    def test_naive_timestamp_fails(self):
        df = make_good_df()
        df["open_time_utc"] = df["open_time_utc"].dt.tz_localize(None)
        result = check_schema(df)
        assert result["passed"] is False
        assert any("timezone" in d for d in result["details"])

    def test_naive_ingested_at_fails(self):
        df = make_good_df()
        df["ingested_at_utc"] = pd.Timestamp("2024-01-01")
        result = check_schema(df)
        assert result["passed"] is False


# ---------------------------------------------------------------------------
# Null checks
# ---------------------------------------------------------------------------


class TestCheckNoNulls:
    def test_no_nulls_passes(self):
        df = make_good_df()
        result = check_no_nulls(df)
        assert result["passed"] is True

    def test_null_close_fails(self):
        df = make_good_df()
        df.loc[5, "close"] = np.nan
        result = check_no_nulls(df)
        assert result["passed"] is False
        assert "close" in result["details"]
        assert result["details"]["close"] == 1

    def test_multiple_null_columns(self):
        df = make_good_df()
        df.loc[0, "open"] = np.nan
        df.loc[1, "high"] = np.nan
        df.loc[2, "high"] = np.nan
        result = check_no_nulls(df)
        assert result["passed"] is False
        assert result["details"]["open"] == 1
        assert result["details"]["high"] == 2


# ---------------------------------------------------------------------------
# Source checks
# ---------------------------------------------------------------------------


class TestCheckSourcePopulated:
    def test_valid_source_passes(self):
        df = make_good_df()
        result = check_source_populated(df)
        assert result["passed"] is True

    def test_null_source_fails(self):
        df = make_good_df()
        df.loc[3, "source"] = None
        result = check_source_populated(df)
        assert result["passed"] is False
        assert result["details"]["null_count"] == 1

    def test_invalid_source_value_fails(self):
        df = make_good_df()
        df.loc[0, "source"] = "unknown_exchange"
        result = check_source_populated(df)
        assert result["passed"] is False
        assert "unknown_exchange" in result["details"]["invalid_values"]

    def test_missing_source_column_fails(self):
        df = make_good_df().drop(columns=["source"])
        result = check_source_populated(df)
        assert result["passed"] is False

    def test_ccxt_binance_source_passes(self):
        df = make_good_df()
        df["source"] = "ccxt_binance"
        result = check_source_populated(df)
        assert result["passed"] is True


# ---------------------------------------------------------------------------
# Duplicate checks
# ---------------------------------------------------------------------------


class TestCheckNoDuplicates:
    def test_no_duplicates_passes(self):
        df = make_good_df()
        result = check_no_duplicates(df)
        assert result["passed"] is True

    def test_duplicates_detected(self):
        df = make_good_df()
        # Duplicate one timestamp
        df.loc[10, "open_time_utc"] = df.loc[5, "open_time_utc"]
        result = check_no_duplicates(df)
        assert result["passed"] is False
        assert result["details"]["duplicate_count"] == 1

    def test_missing_column(self):
        df = make_good_df().drop(columns=["open_time_utc"])
        result = check_no_duplicates(df)
        assert result["passed"] is False


# ---------------------------------------------------------------------------
# Gap checks
# ---------------------------------------------------------------------------


class TestCheckNoGaps:
    def test_no_gaps_passes(self):
        df = make_good_df()
        result = check_no_gaps(df)
        assert result["passed"] is True

    def test_gap_detected(self):
        df = make_good_df(n_hours=48)
        # Remove rows 10-12 to create a gap
        df = df.drop(index=[10, 11, 12]).reset_index(drop=True)
        result = check_no_gaps(df)
        assert result["passed"] is False
        assert result["details"]["gaps_found"] == 1
        assert result["details"]["total_missing_hours"] == 3

    def test_multiple_gaps(self):
        df = make_good_df(n_hours=48)
        df = df.drop(index=[5, 20, 21]).reset_index(drop=True)
        result = check_no_gaps(df)
        assert result["passed"] is False
        assert result["details"]["gaps_found"] == 2

    def test_single_row_no_gap(self):
        df = make_good_df(n_hours=1)
        result = check_no_gaps(df)
        assert result["passed"] is True


# ---------------------------------------------------------------------------
# Hour alignment checks
# ---------------------------------------------------------------------------


class TestCheckHourAligned:
    def test_aligned_passes(self):
        df = make_good_df()
        result = check_hour_aligned(df)
        assert result["passed"] is True

    def test_misaligned_detected(self):
        df = make_good_df()
        # Shift one timestamp by 30 minutes
        df.loc[5, "open_time_utc"] = df.loc[5, "open_time_utc"] + pd.Timedelta(minutes=30)
        result = check_hour_aligned(df)
        assert result["passed"] is False
        assert result["details"]["misaligned_count"] == 1


# ---------------------------------------------------------------------------
# Price positivity checks
# ---------------------------------------------------------------------------


class TestCheckPricesPositive:
    def test_positive_prices_pass(self):
        df = make_good_df()
        result = check_prices_positive(df)
        assert result["passed"] is True

    def test_zero_price_fails(self):
        df = make_good_df()
        df.loc[0, "open"] = 0.0
        result = check_prices_positive(df)
        assert result["passed"] is False
        assert result["details"]["open"] == 1

    def test_negative_price_fails(self):
        df = make_good_df()
        df.loc[3, "close"] = -100.0
        result = check_prices_positive(df)
        assert result["passed"] is False
        assert result["details"]["close"] == 1


# ---------------------------------------------------------------------------
# OHLC consistency checks
# ---------------------------------------------------------------------------


class TestCheckOhlcConsistency:
    def test_consistent_ohlc_passes(self):
        df = make_good_df()
        result = check_ohlc_consistency(df)
        assert result["passed"] is True

    def test_high_below_close_fails(self):
        df = make_good_df()
        # Set high below close
        df.loc[0, "high"] = df.loc[0, "close"] - 10
        result = check_ohlc_consistency(df)
        assert result["passed"] is False
        assert "high_below_max_open_close" in result["details"]

    def test_low_above_open_fails(self):
        df = make_good_df()
        # Set low above open
        df.loc[0, "low"] = df.loc[0, "open"] + 10
        result = check_ohlc_consistency(df)
        assert result["passed"] is False
        assert "low_above_min_open_close" in result["details"]


# ---------------------------------------------------------------------------
# Price anomaly checks
# ---------------------------------------------------------------------------


class TestCheckPriceAnomalies:
    def test_normal_prices_no_anomalies(self):
        df = make_good_df()
        result = check_price_anomalies(df)
        assert result["count"] == 0

    def test_large_price_jump_flagged(self):
        df = make_good_df()
        # Create a >50% price jump
        df.loc[10, "close"] = df.loc[9, "close"] * 2
        result = check_price_anomalies(df)
        assert result["count"] >= 1
        assert result["details"] is not None

    def test_empty_df_no_anomalies(self):
        df = make_good_df(n_hours=1)
        result = check_price_anomalies(df)
        assert result["count"] == 0


# ---------------------------------------------------------------------------
# Volume checks
# ---------------------------------------------------------------------------


class TestCheckVolumeNonNegative:
    def test_positive_volume_passes(self):
        df = make_good_df()
        result = check_volume_non_negative(df)
        assert result["passed"] is True

    def test_negative_volume_fails(self):
        df = make_good_df()
        df.loc[5, "volume"] = -100
        result = check_volume_non_negative(df)
        assert result["passed"] is False
        assert result["details"]["volume"] == 1

    def test_negative_quote_volume_fails(self):
        df = make_good_df()
        df.loc[7, "quote_volume"] = -1.0
        result = check_volume_non_negative(df)
        assert result["passed"] is False
        assert result["details"]["quote_volume"] == 1


class TestCheckZeroVolumeBars:
    def test_no_zero_volume(self):
        df = make_good_df()
        result = check_zero_volume_bars(df)
        assert result["count"] == 0

    def test_zero_volume_flagged(self):
        df = make_good_df()
        df.loc[3, "volume"] = 0
        df.loc[8, "volume"] = 0
        result = check_zero_volume_bars(df)
        assert result["count"] == 2
        assert len(result["timestamps"]) == 2


class TestCheckVolumeDrops:
    def test_no_drops_in_uniform_volume(self):
        df = make_good_df(n_hours=48)
        # Make volume very uniform so no drops
        df["volume"] = 1000.0
        result = check_volume_drops(df)
        assert result["count"] == 0

    def test_extreme_volume_drop_flagged(self):
        df = make_good_df(n_hours=48)
        # Set uniform volume then create extreme drop
        df["volume"] = 1000.0
        df.loc[30, "volume"] = 1.0  # 99.9% drop
        result = check_volume_drops(df)
        assert result["count"] >= 1

    def test_short_df_skipped(self):
        df = make_good_df(n_hours=10)
        result = check_volume_drops(df)
        assert result["count"] == 0


# ---------------------------------------------------------------------------
# Overall validation orchestrator
# ---------------------------------------------------------------------------


class TestValidateOhlcv:
    def test_perfect_data_passes(self):
        df = make_good_df()
        report = validate_ohlcv(df)
        assert report["overall_status"] == "PASS"
        assert report["row_count"] == 48
        assert report["date_range"]["start"] is not None
        assert report["date_range"]["end"] is not None

    def test_gaps_produce_warning(self):
        df = make_good_df(n_hours=48)
        df = df.drop(index=[10]).reset_index(drop=True)
        report = validate_ohlcv(df)
        assert report["overall_status"] == "WARNING"

    def test_zero_volume_produces_warning(self):
        df = make_good_df()
        df.loc[5, "volume"] = 0
        report = validate_ohlcv(df)
        assert report["overall_status"] == "WARNING"

    def test_null_prices_produce_fail(self):
        df = make_good_df()
        df.loc[3, "close"] = np.nan
        report = validate_ohlcv(df)
        assert report["overall_status"] == "FAIL"

    def test_duplicate_timestamps_produce_fail(self):
        df = make_good_df()
        df.loc[10, "open_time_utc"] = df.loc[5, "open_time_utc"]
        report = validate_ohlcv(df)
        assert report["overall_status"] == "FAIL"

    def test_schema_violation_produces_fail(self):
        df = make_good_df().drop(columns=["volume"])
        report = validate_ohlcv(df)
        assert report["overall_status"] == "FAIL"

    def test_negative_price_produces_fail(self):
        df = make_good_df()
        df.loc[0, "open"] = -5.0
        report = validate_ohlcv(df)
        assert report["overall_status"] == "FAIL"

    def test_price_anomaly_produces_warning(self):
        df = make_good_df()
        new_close = df.loc[9, "close"] * 2
        df.loc[10, "close"] = new_close
        df.loc[10, "open"] = new_close - 10
        # Ensure high/low still satisfy OHLC consistency
        df.loc[10, "high"] = new_close + 100
        df.loc[10, "low"] = new_close - 100
        report = validate_ohlcv(df)
        # Price anomaly alone is only a warning (extreme moves are real)
        assert report["overall_status"] == "WARNING"

    def test_empty_dataframe(self):
        df = make_good_df(n_hours=0)
        # Empty df with correct columns
        report = validate_ohlcv(df)
        assert report["row_count"] == 0

    def test_report_has_required_keys(self):
        df = make_good_df()
        report = validate_ohlcv(df)
        assert "check_date_utc" in report
        assert "row_count" in report
        assert "date_range" in report
        assert "checks" in report
        assert "overall_status" in report


# ---------------------------------------------------------------------------
# Report saving
# ---------------------------------------------------------------------------


class TestSaveReport:
    def test_save_creates_file(self, tmp_path: Path):
        df = make_good_df()
        report = validate_ohlcv(df)
        report_path = save_report(report, tmp_path, prefix="test_validation")
        assert report_path.exists()
        assert report_path.suffix == ".json"

        with open(report_path) as f:
            loaded = json.load(f)
        assert loaded["overall_status"] == "PASS"
        assert loaded["row_count"] == 48

    def test_save_creates_directory(self, tmp_path: Path):
        nested = tmp_path / "a" / "b" / "c"
        df = make_good_df()
        report = validate_ohlcv(df)
        report_path = save_report(report, nested)
        assert report_path.exists()
        assert nested.exists()


# ---------------------------------------------------------------------------
# Partial candle checks
# ---------------------------------------------------------------------------


class TestCheckPartialLastCandle:
    def test_old_data_passes(self):
        df = make_good_df(start="2020-01-01T00:00:00")
        result = check_partial_last_candle(df)
        assert result["passed"] is True

    def test_recent_candle_flagged(self):
        # Create a candle with open_time = now, which is definitely partial
        now = pd.Timestamp.now(tz="UTC").floor("h")
        df = make_good_df(n_hours=1, start=str(now))
        result = check_partial_last_candle(df, now_utc=now + pd.Timedelta(minutes=30))
        assert result["passed"] is False
        assert "last_open_time" in result["details"]

    def test_completed_candle_passes(self):
        now = pd.Timestamp.now(tz="UTC").floor("h")
        two_hours_ago = now - pd.Timedelta(hours=2)
        df = make_good_df(n_hours=1, start=str(two_hours_ago))
        result = check_partial_last_candle(df, now_utc=now)
        assert result["passed"] is True


# ---------------------------------------------------------------------------
# Schema enforcement (strict dtypes)
# ---------------------------------------------------------------------------


class TestStrictSchema:
    def test_object_source_dtype_fails(self):
        df = make_good_df()
        df["source"] = df["source"].astype("object")
        result = check_schema(df)
        assert result["passed"] is False
        assert any("source" in d for d in result["details"])

    def test_microsecond_datetime_fails(self):
        df = make_good_df()
        # Convert to microsecond precision
        df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[us, UTC]")
        result = check_schema(df)
        assert result["passed"] is False
        assert any("ingested_at_utc" in d for d in result["details"])

    def test_compliant_dtypes_pass(self):
        df = make_good_df()
        result = check_schema(df)
        assert result["passed"] is True
