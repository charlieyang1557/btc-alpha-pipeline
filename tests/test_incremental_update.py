"""Tests for ingestion/incremental_update.py.

Tests the data conversion logic. Network tests are skipped since
CCXT requires exchange connectivity.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ingestion.incremental_update import candles_to_dataframe
from ingestion.validators import validate_ohlcv


class TestCandlesToDataframe:
    def _make_ccxt_candles(self, n: int = 24) -> list[list]:
        """Create synthetic CCXT OHLCV candle data.

        Args:
            n: Number of candles.

        Returns:
            List of [timestamp_ms, open, high, low, close, volume] lists.
        """
        rng = np.random.default_rng(42)
        start_ms = int(pd.Timestamp("2024-07-01", tz="UTC").timestamp() * 1000)
        candles = []
        base_price = 60000.0
        for i in range(n):
            ts = start_ms + i * 3_600_000
            close = base_price + rng.normal(0, 100)
            open_ = close + rng.normal(0, 20)
            high = max(open_, close) + rng.uniform(10, 100)
            low = min(open_, close) - rng.uniform(10, 100)
            vol = rng.uniform(100, 2000)
            candles.append([ts, open_, high, low, close, vol])
        return candles

    def test_correct_columns(self):
        candles = self._make_ccxt_candles()
        df = candles_to_dataframe(candles)
        expected = {
            "open_time_utc", "open", "high", "low", "close", "volume",
            "quote_volume", "trade_count", "ingested_at_utc", "source",
        }
        assert set(df.columns) == expected

    def test_source_is_ccxt_api(self):
        candles = self._make_ccxt_candles()
        df = candles_to_dataframe(candles)
        assert (df["source"] == "ccxt_api").all()

    def test_timestamps_utc_aware(self):
        candles = self._make_ccxt_candles()
        df = candles_to_dataframe(candles)
        assert df["open_time_utc"].dt.tz is not None
        assert str(df["open_time_utc"].dt.tz) == "UTC"

    def test_sorted_ascending(self):
        candles = self._make_ccxt_candles()
        # Shuffle
        rng = np.random.default_rng(99)
        rng.shuffle(candles)
        df = candles_to_dataframe(candles)
        assert df["open_time_utc"].is_monotonic_increasing

    def test_correct_dtypes(self):
        candles = self._make_ccxt_candles()
        df = candles_to_dataframe(candles)
        assert df["open"].dtype == "float64"
        assert df["volume"].dtype == "float64"
        assert df["trade_count"].dtype == "int64"

    def test_passes_validation(self):
        candles = self._make_ccxt_candles(n=48)
        df = candles_to_dataframe(candles)
        report = validate_ohlcv(df)
        # CCXT data has trade_count=0 which is valid, and
        # quote_volume is computed, so it should pass
        assert report["overall_status"] in ("PASS", "WARNING")

    def test_row_count_matches(self):
        candles = self._make_ccxt_candles(n=100)
        df = candles_to_dataframe(candles)
        assert len(df) == 100
