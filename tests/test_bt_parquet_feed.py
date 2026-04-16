"""Tests for backtest/bt_parquet_feed.py.

Verifies the Backtrader data feed correctly loads parquet data,
maps columns, filters by date range, and produces values that
match a direct pandas read.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import backtrader as bt
import numpy as np
import pandas as pd
import pytest

from backtest.bt_parquet_feed import ParquetFeed


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_test_parquet(
    tmp_path: Path,
    n_hours: int = 48,
    start: str = "2024-01-01",
    volume_override: list[float] | None = None,
) -> tuple[Path, pd.DataFrame]:
    """Create a synthetic parquet file with deterministic prices.

    Prices are deterministic so tests can verify exact values:
        open  = 100 + i
        high  = 110 + i
        low   =  90 + i
        close = 105 + i
        volume = 1000.0 (unless overridden)

    Args:
        tmp_path: Pytest temporary directory.
        n_hours: Number of hourly bars.
        start: Start date in ISO format.
        volume_override: Optional list of volumes (length must match n_hours).

    Returns:
        Tuple of (path to parquet, original DataFrame).
    """
    timestamps = pd.date_range(start=start, periods=n_hours, freq="h", tz="UTC")
    volumes = volume_override if volume_override else [1000.0] * n_hours
    assert len(volumes) == n_hours

    df = pd.DataFrame({
        "open_time_utc": timestamps.astype("datetime64[ms, UTC]"),
        "open": [100.0 + i for i in range(n_hours)],
        "high": [110.0 + i for i in range(n_hours)],
        "low": [90.0 + i for i in range(n_hours)],
        "close": [105.0 + i for i in range(n_hours)],
        "volume": volumes,
        "quote_volume": [100_000.0 + i * 1000 for i in range(n_hours)],
        "trade_count": np.arange(5000, 5000 + n_hours, dtype="int64"),
        "ingested_at_utc": pd.Timestamp.now(tz="UTC").floor("ms"),
        "source": pd.array(["binance_vision"] * n_hours, dtype="string"),
    })
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")

    path = tmp_path / "test.parquet"
    df.to_parquet(path, engine="pyarrow", index=False)
    return path, df


class _DataCollector(bt.Strategy):
    """Test strategy that records all bar data for verification."""

    def __init__(self):
        self.bars = []

    def next(self):
        self.bars.append({
            "datetime": self.data.datetime.datetime(0),
            "open": self.data.open[0],
            "high": self.data.high[0],
            "low": self.data.low[0],
            "close": self.data.close[0],
            "volume": self.data.volume[0],
        })


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestParquetFeedLoading:
    """Test basic parquet loading and column mapping."""

    def test_row_count_matches(self, tmp_path):
        """Feed should contain same number of bars as the parquet file."""
        path, df = _make_test_parquet(tmp_path, n_hours=48)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_DataCollector)
        results = cerebro.run()

        collector = results[0]
        assert len(collector.bars) == 48

    def test_prices_match_pandas(self, tmp_path):
        """OHLCV values from feed must match the raw DataFrame exactly."""
        path, df = _make_test_parquet(tmp_path, n_hours=24)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_DataCollector)
        results = cerebro.run()

        collector = results[0]
        for i, bar in enumerate(collector.bars):
            assert bar["open"] == pytest.approx(df["open"].iloc[i])
            assert bar["high"] == pytest.approx(df["high"].iloc[i])
            assert bar["low"] == pytest.approx(df["low"].iloc[i])
            assert bar["close"] == pytest.approx(df["close"].iloc[i])
            assert bar["volume"] == pytest.approx(df["volume"].iloc[i])

    def test_first_and_last_bar(self, tmp_path):
        """First and last bar prices must match raw data exactly."""
        path, df = _make_test_parquet(tmp_path, n_hours=100)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_DataCollector)
        results = cerebro.run()

        collector = results[0]
        # First bar
        assert collector.bars[0]["open"] == 100.0
        assert collector.bars[0]["close"] == 105.0
        # Last bar
        assert collector.bars[-1]["open"] == 199.0
        assert collector.bars[-1]["close"] == 204.0

    def test_timestamps_match(self, tmp_path):
        """Bar timestamps must match the parquet open_time_utc values."""
        path, df = _make_test_parquet(tmp_path, n_hours=10)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_DataCollector)
        results = cerebro.run()

        collector = results[0]
        expected_times = df["open_time_utc"].dt.tz_localize(None).tolist()
        actual_times = [bar["datetime"] for bar in collector.bars]
        assert actual_times == expected_times


class TestParquetFeedDateFiltering:
    """Test fromdate/todate filtering."""

    def test_fromdate_filter(self, tmp_path):
        """fromdate should exclude bars before the specified date."""
        path, df = _make_test_parquet(tmp_path, n_hours=48, start="2024-01-01")
        # Filter: start from 2024-01-02 (skip first 24 hours)
        feed = ParquetFeed.from_parquet(
            path, fromdate=datetime(2024, 1, 2)
        )

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_DataCollector)
        results = cerebro.run()

        collector = results[0]
        assert len(collector.bars) == 24
        # First bar should be 2024-01-02 00:00
        assert collector.bars[0]["datetime"] == datetime(2024, 1, 2, 0, 0)

    def test_todate_filter(self, tmp_path):
        """todate should exclude bars after the specified date."""
        path, df = _make_test_parquet(tmp_path, n_hours=48, start="2024-01-01")
        # Filter: end at 2024-01-01 23:00 (keep first 24 hours)
        feed = ParquetFeed.from_parquet(
            path, todate=datetime(2024, 1, 1, 23, 0)
        )

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_DataCollector)
        results = cerebro.run()

        collector = results[0]
        assert len(collector.bars) == 24

    def test_combined_date_filter(self, tmp_path):
        """fromdate + todate together should bracket the data."""
        path, df = _make_test_parquet(tmp_path, n_hours=72, start="2024-01-01")
        feed = ParquetFeed.from_parquet(
            path,
            fromdate=datetime(2024, 1, 2),
            todate=datetime(2024, 1, 2, 23, 0),
        )

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_DataCollector)
        results = cerebro.run()

        collector = results[0]
        assert len(collector.bars) == 24

    def test_empty_range_raises(self, tmp_path):
        """A date range with no data should raise ValueError."""
        path, _ = _make_test_parquet(tmp_path, n_hours=24, start="2024-01-01")
        with pytest.raises(ValueError, match="No data in range"):
            ParquetFeed.from_parquet(
                path,
                fromdate=datetime(2025, 1, 1),
                todate=datetime(2025, 12, 31),
            )


class TestParquetFeedErrors:
    """Test error handling."""

    def test_missing_file_raises(self, tmp_path):
        """Non-existent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ParquetFeed.from_parquet(tmp_path / "nonexistent.parquet")

    def test_missing_columns_raises(self, tmp_path):
        """Parquet without required columns should raise ValueError."""
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        path = tmp_path / "bad.parquet"
        df.to_parquet(path, engine="pyarrow", index=False)

        with pytest.raises(ValueError, match="missing required columns"):
            ParquetFeed.from_parquet(path)
