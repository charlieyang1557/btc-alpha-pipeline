"""Tests for ingestion/reconcile.py.

Tests the reconciliation logic: merging, deduplication,
source priority, gap detection, archiving.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ingestion.reconcile import archive_file, reconcile, verify_overlap


def make_ohlcv_df(
    start: str, n_hours: int, source: str = "binance_vision"
) -> pd.DataFrame:
    """Create a synthetic OHLCV DataFrame.

    Args:
        start: Start timestamp in ISO format.
        n_hours: Number of hourly bars.
        source: Data source label.

    Returns:
        Valid OHLCV DataFrame.
    """
    rng = np.random.default_rng(42)
    timestamps = pd.date_range(start=start, periods=n_hours, freq="h", tz="UTC")
    base = 40000.0
    closes = base + rng.normal(0, 50, n_hours).cumsum()
    closes = np.maximum(closes, 100)
    opens = closes + rng.normal(0, 10, n_hours)
    opens = np.maximum(opens, 100)
    highs = np.maximum(opens, closes) + rng.uniform(5, 50, n_hours)
    lows = np.minimum(opens, closes) - rng.uniform(5, 50, n_hours)
    lows = np.maximum(lows, 1)

    df = pd.DataFrame({
        "open_time_utc": timestamps.astype("datetime64[ms, UTC]"),
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": rng.uniform(100, 1000, n_hours),
        "quote_volume": rng.uniform(1e6, 1e7, n_hours),
        "trade_count": rng.integers(5000, 50000, n_hours).astype(np.int64),
        "ingested_at_utc": pd.Timestamp.now(tz="UTC").floor("ms"),
        "source": pd.array([source] * n_hours, dtype="string"),
    })
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")
    return df


class TestReconcile:
    def test_simple_merge(self):
        existing = make_ohlcv_df("2024-01-01", n_hours=48)
        new = make_ohlcv_df("2024-01-03", n_hours=24, source="ccxt_api")
        merged, stats = reconcile(existing, new, remove_partial=False)

        assert stats["rows_before"] == 48
        assert stats["rows_new"] == 24
        assert stats["rows_after"] == 72
        assert stats["rows_deduped"] == 0
        assert merged["open_time_utc"].is_monotonic_increasing

    def test_deduplication(self):
        existing = make_ohlcv_df("2024-01-01", n_hours=48)
        # Overlapping 12 hours
        new = make_ohlcv_df("2024-01-02T12:00:00", n_hours=24, source="ccxt_api")
        merged, stats = reconcile(existing, new, remove_partial=False)

        # 48 existing + 24 new - 12 overlap = 60
        assert stats["rows_deduped"] == 12
        assert stats["rows_after"] == 60
        assert merged["open_time_utc"].is_unique

    def test_binance_vision_preferred_on_conflict(self):
        existing = make_ohlcv_df("2024-01-01", n_hours=24, source="binance_vision")
        new = make_ohlcv_df("2024-01-01", n_hours=24, source="ccxt_api")
        merged, stats = reconcile(existing, new, remove_partial=False)

        # All 24 rows should be from binance_vision
        assert stats["rows_after"] == 24
        assert (merged["source"] == "binance_vision").all()

    def test_ccxt_preferred_when_only_source(self):
        existing = make_ohlcv_df("2024-01-01", n_hours=24, source="ccxt_api")
        new = make_ohlcv_df("2024-01-02", n_hours=24, source="ccxt_api")
        merged, stats = reconcile(existing, new, remove_partial=False)

        assert stats["rows_after"] == 48
        assert (merged["source"] == "ccxt_api").all()

    def test_gap_detection(self):
        existing = make_ohlcv_df("2024-01-01", n_hours=24)
        # Gap: skip 2 hours
        new = make_ohlcv_df("2024-01-02T02:00:00", n_hours=24, source="ccxt_api")
        merged, stats = reconcile(existing, new, remove_partial=False)

        assert stats["gaps_found"] == 1

    def test_sorted_output(self):
        existing = make_ohlcv_df("2024-01-01", n_hours=24)
        new = make_ohlcv_df("2024-01-02", n_hours=24, source="ccxt_api")
        merged, stats = reconcile(existing, new, remove_partial=False)

        assert merged["open_time_utc"].is_monotonic_increasing

    def test_no_gaps_clean_merge(self):
        existing = make_ohlcv_df("2024-01-01", n_hours=24)
        new = make_ohlcv_df("2024-01-02", n_hours=24, source="ccxt_api")
        merged, stats = reconcile(existing, new, remove_partial=False)

        assert stats["gaps_found"] == 0


class TestArchive:
    def test_archive_creates_copy(self, tmp_path: Path):
        # Create a test file
        src = tmp_path / "test.parquet"
        df = make_ohlcv_df("2024-01-01", n_hours=10)
        df.to_parquet(src, engine="pyarrow", index=False)

        # We need to mock ARCHIVE_DIR for this test
        import ingestion.reconcile as rec
        orig_archive = rec.ARCHIVE_DIR
        rec.ARCHIVE_DIR = tmp_path / "archive"

        try:
            result = archive_file(src)
            assert result is not None
            assert result.exists()
            assert "test_" in result.name

            # Verify the archived file has same data
            archived_df = pd.read_parquet(result)
            assert len(archived_df) == len(df)
        finally:
            rec.ARCHIVE_DIR = orig_archive

    def test_archive_nonexistent_returns_none(self, tmp_path: Path):
        result = archive_file(tmp_path / "nonexistent.parquet")
        assert result is None


class TestVerifyOverlap:
    def test_no_overlap(self):
        existing = make_ohlcv_df("2024-01-01", n_hours=24)
        new = make_ohlcv_df("2024-01-02", n_hours=24, source="ccxt_api")
        result = verify_overlap(existing, new)
        assert result["passed"] is True
        assert result["overlap_rows"] == 0

    def test_matching_overlap_passes(self):
        existing = make_ohlcv_df("2024-01-01", n_hours=24)
        # Exact same data as overlap
        new = existing.iloc[12:].copy()
        new["source"] = pd.array(["ccxt_api"] * len(new), dtype="string")
        result = verify_overlap(existing, new)
        assert result["passed"] is True
        assert result["overlap_rows"] == 12

    def test_divergent_overlap_fails(self):
        existing = make_ohlcv_df("2024-01-01", n_hours=24)
        new = existing.iloc[12:].copy()
        new["source"] = pd.array(["ccxt_api"] * len(new), dtype="string")
        # Introduce >0.01% price deviation
        new.loc[new.index[0], "close"] *= 1.01  # 1% off
        result = verify_overlap(existing, new)
        assert result["passed"] is False
        assert result["overlap_rows"] == 12
        assert len(result["details"]) > 0
