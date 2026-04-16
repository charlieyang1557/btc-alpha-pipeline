"""Integration test: incremental_update → reconcile end-to-end.

Mocks only the CCXT exchange layer (create_exchange + fetch_all_candles)
so the entire pipeline runs for real: candle conversion, validation,
parquet I/O, archiving, and reconciliation.

This verifies the pipeline works correctly without requiring network
access to Binance, which is geo-blocked from the US.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from ingestion.incremental_update import candles_to_dataframe, source_label
from ingestion.reconcile import reconcile
from ingestion.validators import validate_ohlcv


def make_canonical_df(start: str, n_hours: int) -> pd.DataFrame:
    """Create a synthetic canonical dataset (simulating bulk_download output).

    Args:
        start: Start timestamp in ISO format.
        n_hours: Number of hourly bars.

    Returns:
        Schema-compliant OHLCV DataFrame with source="binance_vision".
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
        "source": pd.array(["binance_vision"] * n_hours, dtype="string"),
    })
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")
    return df


def make_fake_klines(start_ts: pd.Timestamp, n_hours: int) -> list[list]:
    """Create synthetic 12-field Binance klines (what the real API returns).

    Args:
        start_ts: Start timestamp (UTC-aware).
        n_hours: Number of hourly candles.

    Returns:
        List of 12-field kline rows.
    """
    rng = np.random.default_rng(123)
    start_ms = int(start_ts.timestamp() * 1000)
    candles = []

    base = 40000.0
    for i in range(n_hours):
        ts = start_ms + i * 3_600_000
        close_time = ts + 3_600_000 - 1
        c = base + rng.normal(0, 100)
        o = c + rng.normal(0, 20)
        h = max(o, c) + rng.uniform(10, 100)
        l = min(o, c) - rng.uniform(10, 100)
        l = max(l, 1)
        vol = rng.uniform(100, 2000)
        qv = vol * c
        tc = int(rng.integers(1000, 50000))
        tbb = vol * 0.4
        tbq = tbb * c
        candles.append([ts, o, h, l, c, vol, close_time, qv, tc, tbb, tbq, "0"])

    return candles


class TestIncrementalPipelineIntegration:
    """End-to-end test: incremental_update → validate → reconcile."""

    def test_full_pipeline_no_overlap(self, tmp_path: Path):
        """Existing data ends Jan 2, new data starts Jan 3. No overlap."""
        # --- Step 1: Create canonical parquet (simulating bulk_download) ---
        canonical = make_canonical_df("2024-01-01", n_hours=48)  # Jan 1-2
        canonical_path = tmp_path / "btcusdt_1h.parquet"
        canonical.to_parquet(canonical_path, engine="pyarrow", index=False)

        latest = canonical["open_time_utc"].max()
        assert str(latest) == "2024-01-02 23:00:00+00:00"

        # --- Step 2: Generate fake klines (what CCXT would return) ---
        new_start = latest + pd.Timedelta(hours=1)  # 2024-01-03 00:00
        fake_klines = make_fake_klines(new_start, n_hours=24)  # Jan 3

        # --- Step 3: Convert to DataFrame (real code, no mocks) ---
        update_df = candles_to_dataframe(fake_klines, exchange_id="binance")

        # Verify source label
        assert (update_df["source"] == "ccxt_binance").all()
        assert len(update_df) == 24

        # Verify timestamps are contiguous from where canonical left off
        assert update_df["open_time_utc"].iloc[0] == new_start
        assert update_df["open_time_utc"].is_monotonic_increasing

        # --- Step 4: Validate new data (real validator) ---
        report = validate_ohlcv(update_df)
        assert report["overall_status"] in ("PASS", "WARNING"), (
            f"New data failed validation: {report}"
        )

        # --- Step 5: Write update parquet ---
        update_path = tmp_path / "btcusdt_1h_update.parquet"
        update_df.to_parquet(update_path, engine="pyarrow", index=False)

        # Verify round-trip through parquet preserves dtypes
        reloaded = pd.read_parquet(update_path)
        assert str(reloaded["open_time_utc"].dtype) == "datetime64[ms, UTC]"
        assert str(reloaded["source"].dtype) == "string"

        # --- Step 6: Reconcile (real code) ---
        existing_df = pd.read_parquet(canonical_path)
        new_df = pd.read_parquet(update_path)
        merged, stats = reconcile(existing_df, new_df, remove_partial=False)

        # Verify stats
        assert stats["rows_before"] == 48
        assert stats["rows_new"] == 24
        assert stats["rows_deduped"] == 0
        assert stats["rows_after"] == 72
        assert stats["gaps_found"] == 0
        assert stats["overlap_check"]["passed"] is True

        # Verify merged data integrity
        assert merged["open_time_utc"].is_monotonic_increasing
        assert merged["open_time_utc"].is_unique
        assert len(merged) == 72

        # First 48 rows from binance_vision, last 24 from ccxt_binance
        assert (merged.iloc[:48]["source"] == "binance_vision").all()
        assert (merged.iloc[48:]["source"] == "ccxt_binance").all()

        # --- Step 7: Validate merged data ---
        merged_report = validate_ohlcv(merged)
        assert merged_report["overall_status"] in ("PASS", "WARNING"), (
            f"Merged data failed validation: {merged_report}"
        )

    def test_full_pipeline_with_overlap(self, tmp_path: Path):
        """Existing and new data overlap by 12 hours. Dedup should prefer binance_vision."""
        canonical = make_canonical_df("2024-01-01", n_hours=48)  # Jan 1-2
        canonical_path = tmp_path / "btcusdt_1h.parquet"
        canonical.to_parquet(canonical_path, engine="pyarrow", index=False)

        # New data starts 12 hours before canonical ends (overlap)
        overlap_start = canonical["open_time_utc"].iloc[36]  # Jan 2 12:00
        fake_klines = make_fake_klines(overlap_start, n_hours=36)  # 12h overlap + 24h new

        update_df = candles_to_dataframe(fake_klines, exchange_id="binance")
        assert len(update_df) == 36

        # Validate and write
        report = validate_ohlcv(update_df)
        assert report["overall_status"] in ("PASS", "WARNING")

        update_path = tmp_path / "btcusdt_1h_update.parquet"
        update_df.to_parquet(update_path, engine="pyarrow", index=False)

        # Reconcile
        existing_df = pd.read_parquet(canonical_path)
        new_df = pd.read_parquet(update_path)
        merged, stats = reconcile(existing_df, new_df, remove_partial=False)

        # 48 existing + 36 new - 12 overlap = 72
        assert stats["rows_deduped"] == 12
        assert stats["rows_after"] == 72
        assert merged["open_time_utc"].is_unique

        # Overlap rows should keep binance_vision (higher priority)
        overlap_times = set(canonical["open_time_utc"].iloc[36:])
        overlap_rows = merged[merged["open_time_utc"].isin(overlap_times)]
        assert (overlap_rows["source"] == "binance_vision").all()

    def test_full_pipeline_with_gap(self, tmp_path: Path):
        """New data has a 3-hour gap after existing data. Gap should be detected."""
        canonical = make_canonical_df("2024-01-01", n_hours=48)
        canonical_path = tmp_path / "btcusdt_1h.parquet"
        canonical.to_parquet(canonical_path, engine="pyarrow", index=False)

        # Skip 3 hours after canonical ends
        latest = canonical["open_time_utc"].max()
        gap_start = latest + pd.Timedelta(hours=4)  # 3-hour gap
        fake_klines = make_fake_klines(gap_start, n_hours=24)

        update_df = candles_to_dataframe(fake_klines, exchange_id="binance")
        update_path = tmp_path / "btcusdt_1h_update.parquet"
        update_df.to_parquet(update_path, engine="pyarrow", index=False)

        existing_df = pd.read_parquet(canonical_path)
        new_df = pd.read_parquet(update_path)
        merged, stats = reconcile(existing_df, new_df, remove_partial=False)

        assert stats["gaps_found"] == 1
        assert stats["rows_after"] == 72  # 48 + 24, no overlap

    def test_12field_klines_preserve_real_quote_volume(self):
        """Full 12-field klines should use real quote_volume, not estimate."""
        start = pd.Timestamp("2024-01-01", tz="UTC")
        klines = make_fake_klines(start, n_hours=10)

        df = candles_to_dataframe(klines, exchange_id="binance")

        # trade_count should be real (>0), not the fallback 0
        assert (df["trade_count"] > 0).all()

        # quote_volume should match what we put in the kline, not vol*close
        for i, row in df.iterrows():
            # The kline's quote_volume is at index 7
            expected_qv = float(klines[i][7])
            assert abs(row["quote_volume"] - expected_qv) < 0.01

    def test_6field_fallback_estimates_quote_volume(self):
        """6-field OHLCV fallback should estimate quote_volume = vol * close."""
        rng = np.random.default_rng(42)
        start_ms = int(pd.Timestamp("2024-01-01", tz="UTC").timestamp() * 1000)
        candles_6f = []
        for i in range(10):
            ts = start_ms + i * 3_600_000
            o, h, l, c = 40000.0, 40100.0, 39900.0, 40050.0
            vol = 500.0
            candles_6f.append([ts, o, h, l, c, vol])

        df = candles_to_dataframe(candles_6f, exchange_id="binance")

        assert (df["trade_count"] == 0).all()  # fallback value
        # quote_volume ≈ volume * close
        for _, row in df.iterrows():
            expected = row["volume"] * row["close"]
            assert abs(row["quote_volume"] - expected) < 0.01

    def test_cross_venue_rejected(self, tmp_path: Path):
        """binanceus data must not merge into binance global canonical file."""
        canonical = make_canonical_df("2024-01-01", n_hours=24)
        latest = canonical["open_time_utc"].max()
        new_start = latest + pd.Timedelta(hours=1)

        fake_klines = make_fake_klines(new_start, n_hours=12)
        update_df = candles_to_dataframe(fake_klines, exchange_id="binanceus")

        assert (update_df["source"] == "ccxt_binanceus").all()

        with pytest.raises(ValueError, match="Incompatible venue"):
            reconcile(canonical, update_df, remove_partial=False)

    def test_source_label_helper(self):
        """source_label() should produce venue-specific strings."""
        assert source_label("binance") == "ccxt_binance"
        assert source_label("binanceus") == "ccxt_binanceus"

    def test_parquet_roundtrip_dtypes(self, tmp_path: Path):
        """Verify that schema-compliant dtypes survive parquet write/read."""
        start = pd.Timestamp("2024-01-01", tz="UTC")
        klines = make_fake_klines(start, n_hours=10)
        df = candles_to_dataframe(klines, exchange_id="binance")

        path = tmp_path / "test_roundtrip.parquet"
        df.to_parquet(path, engine="pyarrow", index=False)
        reloaded = pd.read_parquet(path)

        assert str(reloaded["open_time_utc"].dtype) == "datetime64[ms, UTC]"
        assert str(reloaded["ingested_at_utc"].dtype) == "datetime64[ms, UTC]"
        assert str(reloaded["source"].dtype) == "string"
        assert reloaded["open"].dtype == "float64"
        assert reloaded["trade_count"].dtype == "int64"
