"""Tests for ingestion/bulk_download.py.

Tests the data processing, month-key generation, and CSV header detection
logic using synthetic data. Download tests are skipped since Binance Vision
requires network access.
"""

from __future__ import annotations

import io
import zipfile

import numpy as np
import pandas as pd
import pytest

from ingestion.bulk_download import (
    BINANCE_CSV_COLUMNS,
    _find_timestamp_column,
    _infer_ts_unit,
    _looks_like_epoch_timestamp,
    _map_header_columns,
    _normalize_ts_column,
    download_month,
    generate_month_keys,
    process_dataframe,
)
from ingestion.validators import validate_ohlcv


class TestGenerateMonthKeys:
    def test_single_month(self):
        result = generate_month_keys("2020-01", "2020-01")
        assert result == ["2020-01"]

    def test_full_year(self):
        result = generate_month_keys("2020-01", "2020-12")
        assert len(result) == 12
        assert result[0] == "2020-01"
        assert result[-1] == "2020-12"

    def test_cross_year(self):
        result = generate_month_keys("2020-11", "2021-02")
        assert result == ["2020-11", "2020-12", "2021-01", "2021-02"]

    def test_multi_year(self):
        result = generate_month_keys("2020-01", "2024-12")
        assert len(result) == 60  # 5 years * 12 months


class TestProcessDataframe:
    def _make_raw_binance_df(self, n_hours: int = 48) -> pd.DataFrame:
        """Create a synthetic DataFrame mimicking raw Binance Vision CSV output.

        Args:
            n_hours: Number of rows.

        Returns:
            DataFrame with Binance Vision column layout.
        """
        rng = np.random.default_rng(42)
        start_ms = int(pd.Timestamp("2020-01-01", tz="UTC").timestamp() * 1000)
        open_times = [start_ms + i * 3_600_000 for i in range(n_hours)]
        close_times = [t + 3_600_000 - 1 for t in open_times]

        base_price = 7200.0
        closes = base_price + rng.normal(0, 50, n_hours).cumsum()
        closes = np.maximum(closes, 100)
        opens = closes + rng.normal(0, 10, n_hours)
        opens = np.maximum(opens, 100)
        highs = np.maximum(opens, closes) + rng.uniform(5, 50, n_hours)
        lows = np.minimum(opens, closes) - rng.uniform(5, 50, n_hours)
        lows = np.maximum(lows, 1)
        volumes = rng.uniform(100, 1000, n_hours)
        quote_volumes = volumes * closes
        trade_counts = rng.integers(5000, 40000, n_hours)

        df = pd.DataFrame(
            {
                "open_time": open_times,
                "open": opens,
                "high": highs,
                "low": lows,
                "close": closes,
                "volume": volumes,
                "close_time": close_times,
                "quote_volume": quote_volumes,
                "trade_count": trade_counts,
                "taker_buy_base": rng.uniform(50, 500, n_hours),
                "taker_buy_quote": rng.uniform(50000, 500000, n_hours),
                "ignore": 0,
            }
        )
        return df

    def test_correct_columns(self):
        raw = self._make_raw_binance_df()
        result = process_dataframe(raw)
        expected_cols = {
            "open_time_utc", "open", "high", "low", "close",
            "volume", "quote_volume", "trade_count",
            "ingested_at_utc", "source",
        }
        assert set(result.columns) == expected_cols

    def test_timestamps_are_utc_aware(self):
        raw = self._make_raw_binance_df()
        result = process_dataframe(raw)
        assert result["open_time_utc"].dt.tz is not None
        assert str(result["open_time_utc"].dt.tz) == "UTC"

    def test_source_is_binance_vision(self):
        raw = self._make_raw_binance_df()
        result = process_dataframe(raw)
        assert (result["source"] == "binance_vision").all()

    def test_sorted_by_open_time(self):
        raw = self._make_raw_binance_df()
        # Shuffle the raw data
        raw = raw.sample(frac=1, random_state=42).reset_index(drop=True)
        result = process_dataframe(raw)
        assert result["open_time_utc"].is_monotonic_increasing

    def test_no_duplicates(self):
        raw = self._make_raw_binance_df()
        # Add a duplicate
        raw = pd.concat([raw, raw.iloc[[0]]], ignore_index=True)
        result = process_dataframe(raw)
        assert result["open_time_utc"].is_unique

    def test_correct_dtypes(self):
        raw = self._make_raw_binance_df()
        result = process_dataframe(raw)
        assert result["open"].dtype == "float64"
        assert result["high"].dtype == "float64"
        assert result["low"].dtype == "float64"
        assert result["close"].dtype == "float64"
        assert result["volume"].dtype == "float64"
        assert result["quote_volume"].dtype == "float64"
        assert result["trade_count"].dtype == "int64"

    def test_passes_validation(self):
        """Processed synthetic data should pass all validators."""
        raw = self._make_raw_binance_df(n_hours=48)
        result = process_dataframe(raw)
        report = validate_ohlcv(result)
        assert report["overall_status"] in ("PASS", "WARNING"), (
            f"Validation failed: {report['checks']}"
        )

    def test_dropped_columns_not_present(self):
        raw = self._make_raw_binance_df()
        result = process_dataframe(raw)
        assert "close_time" not in result.columns
        assert "taker_buy_base" not in result.columns
        assert "taker_buy_quote" not in result.columns
        assert "ignore" not in result.columns

    def test_float64_open_time_precision(self):
        """Ensure ms-epoch ints survive even if read_csv yields float64.

        When pandas reads large integers it may store them as float64,
        which can lose precision. process_dataframe must still produce
        correct timestamps.
        """
        raw = self._make_raw_binance_df(n_hours=24)
        # Simulate float64 precision issue
        raw["open_time"] = raw["open_time"].astype("float64")
        result = process_dataframe(raw)
        # All timestamps must land in 2020
        assert (result["open_time_utc"].dt.year == 2020).all()

    def test_timestamps_reasonable_range(self):
        """All parsed timestamps must be in a reasonable range (2017-2030)."""
        raw = self._make_raw_binance_df(n_hours=48)
        result = process_dataframe(raw)
        assert (result["open_time_utc"].dt.year >= 2017).all()
        assert (result["open_time_utc"].dt.year <= 2030).all()

    def test_microsecond_timestamps_end_to_end(self):
        """Microsecond timestamps from 2025+ should survive the full pipeline.

        Simulates the scenario where download_month normalizes us→ms timestamps
        and then process_dataframe converts them to datetime. No rows should be
        dropped by the out-of-range sanity filter.
        """
        rng = np.random.default_rng(42)
        n_hours = 24
        # Build raw df with 2025 timestamps already in ms (post-normalization)
        start_ms = int(pd.Timestamp("2025-01-01", tz="UTC").timestamp() * 1000)
        open_times = [start_ms + i * 3_600_000 for i in range(n_hours)]
        close_times = [t + 3_600_000 - 1 for t in open_times]

        base_price = 94000.0
        closes = base_price + rng.normal(0, 50, n_hours).cumsum()
        closes = np.maximum(closes, 100)
        opens = closes + rng.normal(0, 10, n_hours)
        opens = np.maximum(opens, 100)
        highs = np.maximum(opens, closes) + rng.uniform(5, 50, n_hours)
        lows = np.minimum(opens, closes) - rng.uniform(5, 50, n_hours)
        lows = np.maximum(lows, 1)

        raw = pd.DataFrame({
            "open_time": open_times,
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": rng.uniform(100, 1000, n_hours),
            "close_time": close_times,
            "quote_volume": rng.uniform(1e6, 1e7, n_hours),
            "trade_count": rng.integers(5000, 40000, n_hours),
            "taker_buy_base": rng.uniform(50, 500, n_hours),
            "taker_buy_quote": rng.uniform(50000, 500000, n_hours),
            "ignore": 0,
        })
        result = process_dataframe(raw)
        # All 24 rows must survive — none dropped by sanity filter
        assert len(result) == n_hours
        assert (result["open_time_utc"].dt.year == 2025).all()


class TestDownloadMonthHeaderDetection:
    """Test that download_month handles CSVs with and without headers."""

    def _make_csv_zip(self, csv_content: str, filename: str = "BTCUSDT-1h-2020-01.csv") -> bytes:
        """Create an in-memory ZIP containing a single CSV.

        Args:
            csv_content: Raw CSV string.
            filename: Name of the CSV file inside the ZIP.

        Returns:
            Bytes of the ZIP file.
        """
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(filename, csv_content)
        return buf.getvalue()

    def test_headerless_csv_parsed(self, monkeypatch):
        """Binance CSVs without header row should parse correctly."""
        # Two rows, no header — 12 fields matching BINANCE_CSV_COLUMNS:
        # open_time,open,high,low,close,volume,close_time,quote_volume,
        # trade_count,taker_buy_base,taker_buy_quote,ignore
        csv = (
            "1577836800000,7195.24,7196.25,7175.47,7184.27,"
            "489.85,1577840399999,3521345.76,18543,244.92,1760672.88,0\n"
            "1577840400000,7184.27,7186.35,7177.33,7182.04,"
            "302.11,1577843999999,2171018.31,12040,151.05,1085509.15,0\n"
        )
        zip_bytes = self._make_csv_zip(csv)

        import requests as req

        class FakeResp:
            status_code = 200
            content = zip_bytes

        monkeypatch.setattr(req, "get", lambda *a, **kw: FakeResp())

        df = download_month("BTCUSDT", "1h", "2020-01")
        assert df is not None
        assert len(df) == 2
        # open_time must be int, not string
        assert pd.api.types.is_integer_dtype(df["open_time"])
        assert df["open_time"].iloc[0] == 1577836800000

    def test_header_csv_parsed(self, monkeypatch):
        """Binance CSVs with a header row should also parse correctly."""
        csv = (
            "open_time,open,high,low,close,volume,close_time,"
            "quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
            "1577836800000,7195.24,7196.25,7175.47,7184.27,"
            "489.85,1577840399999,3521345.76,18543,244.92,1760672.88,0\n"
            "1577840400000,7184.27,7186.35,7177.33,7182.04,"
            "302.11,1577843999999,2171018.31,12040,151.05,1085509.15,0\n"
        )
        zip_bytes = self._make_csv_zip(csv)

        import requests as req

        class FakeResp:
            status_code = 200
            content = zip_bytes

        monkeypatch.setattr(req, "get", lambda *a, **kw: FakeResp())

        df = download_month("BTCUSDT", "1h", "2020-01")
        assert df is not None
        assert len(df) == 2
        assert pd.api.types.is_integer_dtype(df["open_time"])
        assert df["open_time"].iloc[0] == 1577836800000

    def test_header_with_different_names(self, monkeypatch):
        """CSVs with Binance's alternative header names should map correctly."""
        # Uses "Number of trades" instead of "count", "Quote asset volume", etc.
        csv = (
            "Open time,Open,High,Low,Close,Volume,Close time,"
            "Quote asset volume,Number of trades,"
            "Taker buy base asset volume,Taker buy quote asset volume,Ignore\n"
            "1735689600000,94000.5,94200.0,93800.0,94100.0,"
            "500.0,1735693199999,47050000.0,25000,250.0,23525000.0,0\n"
            "1735693200000,94100.0,94300.0,93900.0,94200.0,"
            "450.0,1735696799999,42390000.0,22000,225.0,21195000.0,0\n"
        )
        zip_bytes = self._make_csv_zip(csv, "BTCUSDT-1h-2025-01.csv")

        import requests as req

        class FakeResp:
            status_code = 200
            content = zip_bytes

        monkeypatch.setattr(req, "get", lambda *a, **kw: FakeResp())

        df = download_month("BTCUSDT", "1h", "2025-01")
        assert df is not None
        assert len(df) == 2
        assert pd.api.types.is_integer_dtype(df["open_time"])
        # 2025-01-01 00:00 UTC
        assert df["open_time"].iloc[0] == 1735689600000
        # trade_count mapped from "Number of trades"
        assert "trade_count" in df.columns
        assert df["trade_count"].iloc[0] == 25000

    def test_extra_leading_column_with_header(self, monkeypatch):
        """CSV with an extra leading column should still parse via name mapping."""
        # Extra "id" column at position 0
        csv = (
            "id,open_time,open,high,low,close,volume,close_time,"
            "quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
            "1,1735689600000,94000.5,94200.0,93800.0,94100.0,"
            "500.0,1735693199999,47050000.0,25000,250.0,23525000.0,0\n"
            "2,1735693200000,94100.0,94300.0,93900.0,94200.0,"
            "450.0,1735696799999,42390000.0,22000,225.0,21195000.0,0\n"
        )
        zip_bytes = self._make_csv_zip(csv, "BTCUSDT-1h-2025-01.csv")

        import requests as req

        class FakeResp:
            status_code = 200
            content = zip_bytes

        monkeypatch.setattr(req, "get", lambda *a, **kw: FakeResp())

        df = download_month("BTCUSDT", "1h", "2025-01")
        assert df is not None
        assert len(df) == 2
        # Name-based mapping should correctly identify open_time
        assert "open_time" in df.columns
        assert pd.api.types.is_integer_dtype(df["open_time"])
        assert df["open_time"].iloc[0] == 1735689600000

    def test_microsecond_timestamps_normalized(self, monkeypatch):
        """2025+ CSVs with microsecond timestamps should be normalized to ms.

        This is the root cause of the 10,920-row bug: Binance Vision switched
        from millisecond to microsecond epoch timestamps in 2025+ files.
        Without normalization, 1735689600000000 (us) is treated as ms and
        converts to year ~56970, which fails the sanity filter.
        """
        # Microsecond timestamps (16 digits) — 2025-01-01 00:00 and 01:00 UTC
        us_open_0 = 1735689600000000    # 2025-01-01 00:00 in us
        us_close_0 = 1735693199999000   # close_time in us
        us_open_1 = 1735693200000000    # 2025-01-01 01:00 in us
        us_close_1 = 1735696799999000
        csv = (
            f"{us_open_0},94000.5,94200.0,93800.0,94100.0,"
            f"500.0,{us_close_0},47050000.0,25000,250.0,23525000.0,0\n"
            f"{us_open_1},94100.0,94300.0,93900.0,94200.0,"
            f"450.0,{us_close_1},42390000.0,22000,225.0,21195000.0,0\n"
        )
        zip_bytes = self._make_csv_zip(csv, "BTCUSDT-1h-2025-01.csv")

        import requests as req

        class FakeResp:
            status_code = 200
            content = zip_bytes

        monkeypatch.setattr(req, "get", lambda *a, **kw: FakeResp())

        df = download_month("BTCUSDT", "1h", "2025-01")
        assert df is not None
        assert len(df) == 2
        # open_time must be normalized to ms
        assert df["open_time"].iloc[0] == 1735689600000  # ms, not us
        assert df["open_time"].iloc[1] == 1735693200000

    def test_microsecond_header_csv_normalized(self, monkeypatch):
        """Header CSVs with microsecond timestamps should also normalize."""
        us_open_0 = 1735689600000000
        us_close_0 = 1735693199999000
        us_open_1 = 1735693200000000
        us_close_1 = 1735696799999000
        csv = (
            "Open time,Open,High,Low,Close,Volume,Close time,"
            "Quote asset volume,Number of trades,"
            "Taker buy base asset volume,Taker buy quote asset volume,Ignore\n"
            f"{us_open_0},94000.5,94200.0,93800.0,94100.0,"
            f"500.0,{us_close_0},47050000.0,25000,250.0,23525000.0,0\n"
            f"{us_open_1},94100.0,94300.0,93900.0,94200.0,"
            f"450.0,{us_close_1},42390000.0,22000,225.0,21195000.0,0\n"
        )
        zip_bytes = self._make_csv_zip(csv, "BTCUSDT-1h-2025-01.csv")

        import requests as req

        class FakeResp:
            status_code = 200
            content = zip_bytes

        monkeypatch.setattr(req, "get", lambda *a, **kw: FakeResp())

        df = download_month("BTCUSDT", "1h", "2025-01")
        assert df is not None
        assert len(df) == 2
        assert df["open_time"].iloc[0] == 1735689600000


class TestTimestampHelpers:
    """Tests for _infer_ts_unit, _looks_like_epoch_timestamp, _normalize_ts_column."""

    # --- _infer_ts_unit ---

    def test_infer_ms(self):
        # 2024-01-01 00:00 UTC in milliseconds
        assert _infer_ts_unit(1704067200000) == "ms"

    def test_infer_ms_2025(self):
        # 2025-01-01 00:00 UTC in milliseconds
        assert _infer_ts_unit(1735689600000) == "ms"

    def test_infer_us(self):
        # 2025-01-01 00:00 UTC in microseconds (16 digits)
        assert _infer_ts_unit(1735689600000000) == "us"

    def test_infer_ns(self):
        # 2025-01-01 00:00 UTC in nanoseconds (19 digits)
        assert _infer_ts_unit(1735689600000000000) == "ns"

    def test_infer_s(self):
        # 2024-01-01 00:00 UTC in seconds (10 digits)
        assert _infer_ts_unit(1704067200) == "s"

    def test_infer_string_ms(self):
        assert _infer_ts_unit("1704067200000") == "ms"

    def test_infer_string_us(self):
        assert _infer_ts_unit("1735689600000000") == "us"

    def test_infer_garbage_returns_none(self):
        assert _infer_ts_unit("not_a_number") is None

    def test_infer_zero_returns_none(self):
        assert _infer_ts_unit(0) is None

    def test_infer_negative_returns_none(self):
        assert _infer_ts_unit(-1704067200000) is None

    # --- _looks_like_epoch_timestamp ---

    def test_epoch_ms(self):
        assert _looks_like_epoch_timestamp(1704067200000) is True

    def test_epoch_us(self):
        assert _looks_like_epoch_timestamp(1735689600000000) is True

    def test_epoch_ns(self):
        assert _looks_like_epoch_timestamp(1735689600000000000) is True

    def test_epoch_s(self):
        assert _looks_like_epoch_timestamp(1704067200) is True

    def test_epoch_garbage(self):
        assert _looks_like_epoch_timestamp("not_a_number") is False

    def test_epoch_zero(self):
        assert _looks_like_epoch_timestamp(0) is False

    def test_epoch_small_int(self):
        # Small int (e.g. a row ID) should not look like a timestamp
        assert _looks_like_epoch_timestamp(42) is False

    # --- _normalize_ts_column ---

    def test_normalize_ms_noop(self):
        """Millisecond timestamps should pass through unchanged."""
        df = pd.DataFrame({"open_time": pd.array([1704067200000, 1704070800000], dtype="Int64")})
        result = _normalize_ts_column(df, "open_time")
        assert result["open_time"].iloc[0] == 1704067200000

    def test_normalize_us_to_ms(self):
        """Microsecond timestamps (16 digits) should be divided by 1000."""
        us_val = 1735689600000000  # 2025-01-01 in us
        ms_val = 1735689600000    # same in ms
        df = pd.DataFrame({"open_time": pd.array([us_val, us_val + 3_600_000_000], dtype="Int64")})
        result = _normalize_ts_column(df, "open_time")
        assert result["open_time"].iloc[0] == ms_val
        assert result["open_time"].iloc[1] == ms_val + 3_600_000

    def test_normalize_ns_to_ms(self):
        """Nanosecond timestamps (19 digits) should be divided by 1_000_000."""
        ns_val = 1735689600000000000  # 2025-01-01 in ns
        ms_val = 1735689600000
        df = pd.DataFrame({"open_time": pd.array([ns_val], dtype="Int64")})
        result = _normalize_ts_column(df, "open_time")
        assert result["open_time"].iloc[0] == ms_val

    def test_normalize_s_to_ms(self):
        """Second timestamps (10 digits) should be multiplied by 1000."""
        s_val = 1704067200   # 2024-01-01 in seconds
        ms_val = 1704067200000
        df = pd.DataFrame({"open_time": pd.array([s_val], dtype="Int64")})
        result = _normalize_ts_column(df, "open_time")
        assert result["open_time"].iloc[0] == ms_val

    def test_normalize_missing_column_noop(self):
        """If column doesn't exist, return df unchanged."""
        df = pd.DataFrame({"other": [1, 2]})
        result = _normalize_ts_column(df, "open_time")
        assert list(result.columns) == ["other"]

    def test_normalize_empty_df_noop(self):
        """Empty DataFrame should be returned unchanged."""
        df = pd.DataFrame({"open_time": pd.array([], dtype="Int64")})
        result = _normalize_ts_column(df, "open_time")
        assert len(result) == 0

    # --- _find_timestamp_column ---

    def test_find_timestamp_column(self):
        df = pd.DataFrame({
            "id": [1, 2],
            "ts": [1704067200000, 1704070800000],
            "price": [42000.0, 42100.0],
        })
        assert _find_timestamp_column(df) == "ts"

    def test_find_timestamp_column_first_col(self):
        df = pd.DataFrame({
            "open_time": [1704067200000, 1704070800000],
            "price": [42000.0, 42100.0],
        })
        assert _find_timestamp_column(df) == "open_time"

    def test_find_timestamp_column_us(self):
        """Microsecond timestamps should also be found."""
        df = pd.DataFrame({
            "id": [1, 2],
            "ts": [1735689600000000, 1735693200000000],
            "price": [94000.0, 94100.0],
        })
        assert _find_timestamp_column(df) == "ts"

    def test_find_timestamp_column_none(self):
        df = pd.DataFrame({
            "a": [1, 2],
            "b": [3.14, 2.71],
        })
        assert _find_timestamp_column(df) is None


class TestHeaderMapping:
    def test_standard_headers(self):
        cols = [
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trade_count",
            "taker_buy_base", "taker_buy_quote", "ignore",
        ]
        result = _map_header_columns(cols)
        assert result is not None
        assert result["open_time"] == "open_time"

    def test_binance_verbose_headers(self):
        cols = [
            "Open time", "Open", "High", "Low", "Close", "Volume",
            "Close time", "Quote asset volume", "Number of trades",
            "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore",
        ]
        result = _map_header_columns(cols)
        assert result is not None
        assert result["Number of trades"] == "trade_count"
        assert result["Quote asset volume"] == "quote_volume"

    def test_unknown_headers_returns_none(self):
        cols = ["col_a", "col_b", "col_c", "col_d"]
        result = _map_header_columns(cols)
        assert result is None

    def test_extra_columns_still_map(self):
        cols = [
            "row_id", "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "count",
            "taker_buy_volume", "taker_buy_quote_volume", "ignore",
        ]
        result = _map_header_columns(cols)
        assert result is not None
        assert "row_id" not in result  # extra col not mapped
        assert result["count"] == "trade_count"
