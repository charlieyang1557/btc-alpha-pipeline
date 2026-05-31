"""Tests for Factor Library (Deliverable 1, Phase 2A).

Coverage:
- Registry: registration, duplicate rejection, lambda/nested rejection
- Core factors: each computes without error on synthetic data, known-value checks
- Null policy: NaN only before warmup, never after
- feature_version: deterministic, changes on compute edit, stable on docstring edit
- Forensic future-bar-invariance: split at bar 500, compare — catches lookahead
- Build features: parquet metadata, full-dataset coverage, stale-parquet rebuild
- Determinism: two builds produce identical parquet
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest

from factors.registry import (
    FactorRegistry,
    FactorSpec,
    compute_feature_version,
    get_registry,
    reset_registry,
)
from factors.operators import decay_linear, rolling_backward_percentile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARQUET_PATH = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"

# ---------------------------------------------------------------------------
# Synthetic data helpers
# ---------------------------------------------------------------------------

def _make_synthetic(n: int, seed: int = 42) -> pd.DataFrame:
    """Create n-bar synthetic OHLCV DataFrame for testing."""
    rng = np.random.RandomState(seed)
    base = 40000.0
    close = base + np.cumsum(rng.randn(n) * 100)
    high = close + rng.uniform(50, 200, n)
    low = close - rng.uniform(50, 200, n)
    opn = close + rng.randn(n) * 50
    volume = rng.uniform(100, 10000, n)
    times = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame({
        "open_time_utc": times,
        "open": opn,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


@pytest.fixture
def synthetic_200():
    return _make_synthetic(200)


@pytest.fixture
def synthetic_1000():
    return _make_synthetic(1000)


@pytest.fixture
def registry():
    """Fresh registry with all 23 core factors (18 original + 5 Path B arc additions)."""
    r = FactorRegistry()
    from factors.registry import _bootstrap_core_factors
    _bootstrap_core_factors(r)
    return r


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def _dummy_compute(df: pd.DataFrame) -> pd.Series:
    """Dummy compute for registration tests.

    Inputs: close.
    Warmup: 0 bars.
    Output dtype: float64.
    Null policy: no NaN.
    """
    return df["close"]


class TestRegistration:
    """Registry registration and guard rails."""

    def test_register_and_get(self):
        r = FactorRegistry()
        spec = FactorSpec(
            name="test_factor", category="test", warmup_bars=0,
            inputs=["close"], output_dtype="float64",
            compute=_dummy_compute, docstring="test doc",
        )
        r.register(spec)
        assert r.get("test_factor") is spec

    def test_duplicate_rejected(self):
        r = FactorRegistry()
        spec = FactorSpec(
            name="dup", category="test", warmup_bars=0,
            inputs=["close"], output_dtype="float64",
            compute=_dummy_compute, docstring="test doc",
        )
        r.register(spec)
        with pytest.raises(ValueError, match="collision"):
            r.register(spec)

    def test_lambda_rejected(self):
        with pytest.raises(TypeError, match="lambda"):
            FactorSpec(
                name="bad", category="test", warmup_bars=0,
                inputs=["close"], output_dtype="float64",
                compute=lambda df: df["close"],
                docstring="test doc",
            )

    def test_nested_function_rejected(self):
        def inner_fn(df: pd.DataFrame) -> pd.Series:
            """Nested compute. Inputs: close. Warmup: 0. Output: float64. Null: none."""
            return df["close"]

        with pytest.raises(TypeError, match="nested"):
            FactorSpec(
                name="bad", category="test", warmup_bars=0,
                inputs=["close"], output_dtype="float64",
                compute=inner_fn, docstring="test doc",
            )

    def test_empty_docstring_rejected(self):
        with pytest.raises(ValueError, match="docstring"):
            FactorSpec(
                name="bad", category="test", warmup_bars=0,
                inputs=["close"], output_dtype="float64",
                compute=_dummy_compute, docstring="",
            )

    def test_list_names_sorted(self, registry):
        names = registry.list_names()
        assert names == sorted(names)

    def test_unknown_factor_raises(self, registry):
        with pytest.raises(KeyError):
            registry.get("nonexistent_factor")


# ---------------------------------------------------------------------------
# Core factors — 23 registered (18 original + 5 Path B arc additions)
# ---------------------------------------------------------------------------

EXPECTED_FACTORS = [
    "atr_14",
    "bb_upper_24_2",
    "cdf_realized_vol_720",
    "close",
    "day_of_week",
    "decay_linear_close_168",
    "decay_linear_close_48",
    "ema_12",
    "ema_26",
    "hour_of_day",
    "intrabar_push",
    "macd_hist",
    "range_over_atr",
    "realized_vol_24h",
    "return_168h",
    "return_1h",
    "return_24h",
    "rsi_14",
    "sma_20",
    "sma_24",
    "sma_50",
    "volume_zscore_24h",
    "zscore_48",
]


class TestCoreFactors:
    """All 23 core factors are registered and computable."""

    def test_all_registered(self, registry):
        assert registry.list_names() == EXPECTED_FACTORS

    @pytest.mark.parametrize("name", EXPECTED_FACTORS)
    def test_computes_without_error(self, registry, synthetic_200, name):
        spec = registry.get(name)
        result = spec.compute(synthetic_200)
        assert isinstance(result, pd.Series)
        assert len(result) == 200

    @pytest.mark.parametrize("name", EXPECTED_FACTORS)
    def test_null_policy_compliance(self, registry, synthetic_200, name):
        """NaN only before warmup; none after."""
        spec = registry.get(name)
        result = spec.compute(synthetic_200).astype(spec.output_dtype)
        warmup = spec.warmup_bars
        if warmup < 200:
            post = result.iloc[warmup:]
            assert not post.isna().any(), (
                f"{name}: NaN found after warmup bar {warmup}"
            )


# ---------------------------------------------------------------------------
# Known-value assertions
# ---------------------------------------------------------------------------


class TestKnownValues:
    """Hand-computed reference values for spot-checking factor correctness."""

    def test_return_1h(self, synthetic_200):
        from factors.returns import compute_return_1h
        r = compute_return_1h(synthetic_200)
        c = synthetic_200["close"]
        expected = (c.iloc[1] - c.iloc[0]) / c.iloc[0]
        assert r.iloc[1] == pytest.approx(expected)

    def test_return_24h(self, synthetic_200):
        from factors.returns import compute_return_24h
        r = compute_return_24h(synthetic_200)
        c = synthetic_200["close"]
        expected = (c.iloc[24] - c.iloc[0]) / c.iloc[0]
        assert r.iloc[24] == pytest.approx(expected)

    def test_sma_20_at_bar_19(self, synthetic_200):
        from factors.moving_averages import compute_sma_20
        s = compute_sma_20(synthetic_200)
        c = synthetic_200["close"]
        expected = c.iloc[0:20].mean()
        assert s.iloc[19] == pytest.approx(expected)

    def test_sma_50_at_bar_49(self, synthetic_200):
        from factors.moving_averages import compute_sma_50
        s = compute_sma_50(synthetic_200)
        c = synthetic_200["close"]
        expected = c.iloc[0:50].mean()
        assert s.iloc[49] == pytest.approx(expected)

    def test_rsi_14_range(self, synthetic_200):
        from factors.momentum import compute_rsi_14
        r = compute_rsi_14(synthetic_200)
        post = r.iloc[14:]
        assert (post >= 0.0).all()
        assert (post <= 100.0).all()

    def test_atr_14_positive(self, synthetic_200):
        from factors.volatility import compute_atr_14
        a = compute_atr_14(synthetic_200)
        post = a.iloc[14:]
        assert (post > 0).all()

    def test_hour_of_day_range(self, synthetic_200):
        from factors.structural import compute_hour_of_day
        h = compute_hour_of_day(synthetic_200)
        assert (h >= 0).all() and (h <= 23).all()

    def test_day_of_week_range(self, synthetic_200):
        from factors.structural import compute_day_of_week
        d = compute_day_of_week(synthetic_200)
        assert (d >= 0).all() and (d <= 6).all()

    def test_hour_of_day_known_value(self, synthetic_200):
        from factors.structural import compute_hour_of_day
        h = compute_hour_of_day(synthetic_200)
        assert h.iloc[0] == 0  # 2020-01-01 00:00 UTC
        assert h.iloc[5] == 5  # 2020-01-01 05:00 UTC

    def test_volume_zscore_after_warmup_finite(self, synthetic_200):
        from factors.volume import compute_volume_zscore_24h
        z = compute_volume_zscore_24h(synthetic_200)
        post = z.iloc[23:]
        assert post.isna().sum() == 0
        assert np.isfinite(post).all()

    # --- D5 retroactive additions ---

    def test_close_identity(self, synthetic_200):
        from factors.price import compute_close
        result = compute_close(synthetic_200)
        pd.testing.assert_series_equal(
            result, synthetic_200["close"].astype("float64"), check_names=False
        )

    def test_sma_24_at_bar_23(self, synthetic_200):
        from factors.moving_averages import compute_sma_24
        s = compute_sma_24(synthetic_200)
        c = synthetic_200["close"]
        expected = c.iloc[0:24].mean()
        assert s.iloc[23] == pytest.approx(expected)

    def test_bb_upper_24_2_at_bar_23(self, synthetic_200):
        from factors.volatility import compute_bb_upper_24_2
        bb = compute_bb_upper_24_2(synthetic_200)
        c = synthetic_200["close"]
        window = c.iloc[0:24]
        expected = window.mean() + 2.0 * window.std(ddof=0)
        assert bb.iloc[23] == pytest.approx(expected)

    def test_zscore_48_at_bar_47(self, synthetic_200):
        from factors.volatility import compute_zscore_48
        z = compute_zscore_48(synthetic_200)
        c = synthetic_200["close"]
        window = c.iloc[0:48]
        mean = window.mean()
        std = window.std(ddof=0)
        expected = (c.iloc[47] - mean) / std
        assert z.iloc[47] == pytest.approx(expected)

    def test_zscore_48_flat_window_returns_zero(self):
        """When all closes are identical (std=0), zscore_48 returns 0.0."""
        from factors.volatility import compute_zscore_48
        idx = pd.date_range("2024-01-01", periods=60, freq="1h", tz="UTC")
        flat = pd.DataFrame({
            "open_time_utc": idx,
            "open": 100.0, "high": 101.0, "low": 99.0,
            "close": 100.0, "volume": 1000.0,
        })
        z = compute_zscore_48(flat)
        assert z.iloc[48] == 0.0
        assert z.iloc[59] == 0.0


# ---------------------------------------------------------------------------
# max_warmup
# ---------------------------------------------------------------------------


class TestMaxWarmup:
    def test_single_factor(self, registry):
        assert registry.max_warmup(["return_1h"]) == 1

    def test_multiple_factors(self, registry):
        assert registry.max_warmup(["return_1h", "return_168h", "sma_20"]) == 168

    def test_empty_list(self, registry):
        assert registry.max_warmup([]) == 0

    def test_all_factors(self, registry):
        # cdf_realized_vol_720 has warmup=743 (720-bar rolling realized vol +
        # ATR shift inside); updated from 168 when the Path B arc added the
        # 5 new factors.
        assert registry.max_warmup(registry.list_names()) == 743


# ---------------------------------------------------------------------------
# compute_all
# ---------------------------------------------------------------------------


class TestComputeAll:
    def test_returns_dataframe(self, registry, synthetic_200):
        result = registry.compute_all(synthetic_200)
        assert isinstance(result, pd.DataFrame)
        assert set(result.columns) == set(EXPECTED_FACTORS)

    def test_row_count_matches(self, registry, synthetic_200):
        result = registry.compute_all(synthetic_200)
        assert len(result) == 200

    def test_subset_factors(self, registry, synthetic_200):
        result = registry.compute_all(synthetic_200, ["sma_20", "rsi_14"])
        assert list(result.columns) == ["sma_20", "rsi_14"]

    def test_post_warmup_no_nan(self, registry, synthetic_200):
        """compute_all enforces null policy — no NaN after warmup."""
        result = registry.compute_all(synthetic_200)
        max_w = registry.max_warmup(registry.list_names())
        post = result.iloc[max_w:]
        assert not post.isna().any().any(), (
            f"NaN found after global max warmup={max_w}"
        )


# ---------------------------------------------------------------------------
# feature_version
# ---------------------------------------------------------------------------


def _alt_compute_for_version_test(df: pd.DataFrame) -> pd.Series:
    """Alternative compute function — differs from _dummy_compute by one op.

    Inputs: close.
    Warmup: 0.
    Output dtype: float64.
    Null policy: no NaN.
    """
    return df["close"] * 2.0


def _dummy_compute_different_docstring(df: pd.DataFrame) -> pd.Series:
    """This docstring is DIFFERENT but the body is identical to _dummy_compute.

    Inputs: close.
    Warmup: 0 bars.
    Output dtype: float64.
    Null policy: no NaN.
    """
    return df["close"]


class TestFeatureVersion:
    def test_deterministic(self, registry):
        v1 = compute_feature_version(registry)
        v2 = compute_feature_version(registry)
        assert v1 == v2

    def test_changes_on_compute_edit(self):
        """Different compute body → different feature_version."""
        r1 = FactorRegistry()
        r1.register(FactorSpec(
            name="x", category="test", warmup_bars=0,
            inputs=["close"], output_dtype="float64",
            compute=_dummy_compute, docstring="d",
        ))
        r2 = FactorRegistry()
        r2.register(FactorSpec(
            name="x", category="test", warmup_bars=0,
            inputs=["close"], output_dtype="float64",
            compute=_alt_compute_for_version_test, docstring="d",
        ))
        assert compute_feature_version(r1) != compute_feature_version(r2)

    def test_stable_on_docstring_edit(self):
        """Same function body, different docstring → same feature_version."""
        r1 = FactorRegistry()
        r1.register(FactorSpec(
            name="x", category="test", warmup_bars=0,
            inputs=["close"], output_dtype="float64",
            compute=_dummy_compute, docstring="doc A",
        ))
        r2 = FactorRegistry()
        r2.register(FactorSpec(
            name="x", category="test", warmup_bars=0,
            inputs=["close"], output_dtype="float64",
            compute=_dummy_compute_different_docstring, docstring="doc B",
        ))
        assert compute_feature_version(r1) == compute_feature_version(r2)

    def test_changes_on_warmup_edit(self):
        """Different declared warmup → different feature_version."""
        r1 = FactorRegistry()
        r1.register(FactorSpec(
            name="x", category="test", warmup_bars=10,
            inputs=["close"], output_dtype="float64",
            compute=_dummy_compute, docstring="d",
        ))
        r2 = FactorRegistry()
        r2.register(FactorSpec(
            name="x", category="test", warmup_bars=20,
            inputs=["close"], output_dtype="float64",
            compute=_dummy_compute, docstring="d",
        ))
        assert compute_feature_version(r1) != compute_feature_version(r2)


# ---------------------------------------------------------------------------
# Forensic future-bar-invariance test (CRITICAL)
# ---------------------------------------------------------------------------


class TestForensicFutureBarInvariance:
    """For each factor, split a 1000-bar synthetic series at index 500.
    Compute on the full series and on df.iloc[:501]. Assert values at
    every index <= 500 are identical. Any factor using global .mean(),
    .std(), or any non-causal op will fail because adding future data
    (indices 501-999) changes earlier values.
    """

    SPLIT = 500

    @pytest.mark.parametrize("name", EXPECTED_FACTORS)
    def test_future_bar_invariance(self, registry, synthetic_1000, name):
        spec = registry.get(name)
        full_result = spec.compute(synthetic_1000)
        partial_df = synthetic_1000.iloc[: self.SPLIT + 1].copy().reset_index(drop=True)
        partial_result = spec.compute(partial_df)

        full_prefix = full_result.iloc[: self.SPLIT + 1].reset_index(drop=True)
        partial_result = partial_result.reset_index(drop=True)

        # Compare element-wise, treating NaN == NaN as True.
        both_nan = full_prefix.isna() & partial_result.isna()
        both_val = ~full_prefix.isna() & ~partial_result.isna()
        nan_mismatch = full_prefix.isna() != partial_result.isna()

        assert not nan_mismatch.any(), (
            f"Factor {name!r}: NaN pattern differs between full and partial "
            f"computation (first mismatch at index "
            f"{int(nan_mismatch[nan_mismatch].index[0])})"
        )

        if both_val.any():
            diffs = (full_prefix[both_val] - partial_result[both_val]).abs()
            max_diff = diffs.max()
            assert max_diff < 1e-10, (
                f"Factor {name!r}: max diff = {max_diff:.2e} between full "
                f"and partial computation (lookahead detected!)"
            )


# ---------------------------------------------------------------------------
# Build features: parquet metadata and coverage
# ---------------------------------------------------------------------------


class TestBuildFeatures:
    """Tests that exercise build_features.py end-to-end on synthetic data."""

    @pytest.fixture
    def built_parquet(self, tmp_path, registry):
        """Build a small feature parquet from synthetic raw data."""
        from factors.build_features import (
            build_features_df,
            write_features_parquet,
        )

        raw_df = _make_synthetic(300)
        features_df = build_features_df(raw_df, registry)
        version = compute_feature_version(registry)
        out_path = tmp_path / "features.parquet"
        raw_path = tmp_path / "raw.parquet"
        raw_df.to_parquet(raw_path, index=False)
        write_features_parquet(features_df, out_path, version, raw_path)
        return out_path, features_df, version

    def test_parquet_has_feature_version(self, built_parquet):
        path, _, version = built_parquet
        meta = pq.read_metadata(path).metadata
        assert b"feature_version" in meta
        assert meta[b"feature_version"].decode() == version

    def test_parquet_has_built_at(self, built_parquet):
        path, _, _ = built_parquet
        meta = pq.read_metadata(path).metadata
        assert b"built_at_utc" in meta
        built_at = meta[b"built_at_utc"].decode()
        assert built_at.endswith("Z")

    def test_parquet_has_factor_names(self, built_parquet):
        path, _, _ = built_parquet
        meta = pq.read_metadata(path).metadata
        names = json.loads(meta[b"factor_names"].decode())
        assert set(names) == set(EXPECTED_FACTORS)

    def test_columns_correct(self, built_parquet):
        path, _, _ = built_parquet
        df = pd.read_parquet(path)
        assert "open_time_utc" in df.columns
        for f in EXPECTED_FACTORS:
            assert f in df.columns

    def test_row_count_matches_raw(self, built_parquet):
        _, features_df, _ = built_parquet
        assert len(features_df) == 300

    def test_no_nan_after_max_warmup(self, built_parquet, registry):
        _, features_df, _ = built_parquet
        max_w = registry.max_warmup(registry.list_names())
        post = features_df[EXPECTED_FACTORS].iloc[max_w:]
        assert not post.isna().any().any()


# ---------------------------------------------------------------------------
# Full-dataset coverage test
# ---------------------------------------------------------------------------


pytestmark_data = pytest.mark.skipif(
    not PARQUET_PATH.exists(),
    reason=f"Canonical parquet not found: {PARQUET_PATH}",
)


@pytestmark_data
class TestFullDatasetCoverage:
    """build_features produces parquet covering the full OHLCV range."""

    def test_first_last_index_match(self, tmp_path, registry):
        from factors.build_features import build_features_df, load_raw_ohlcv

        raw_df = load_raw_ohlcv(PARQUET_PATH)
        features_df = build_features_df(raw_df, registry)

        assert features_df["open_time_utc"].iloc[0] == raw_df["open_time_utc"].iloc[0]
        assert features_df["open_time_utc"].iloc[-1] == raw_df["open_time_utc"].iloc[-1]
        assert len(features_df) == len(raw_df)


# ---------------------------------------------------------------------------
# Stale parquet → force rebuild
# ---------------------------------------------------------------------------


class TestStaleParquetForceRebuild:
    """If stored feature_version != live, load_features_or_rebuild rebuilds."""

    def test_stale_triggers_rebuild(self, tmp_path, registry):
        from factors.build_features import (
            build_features_df,
            load_features_or_rebuild,
            write_features_parquet,
        )

        raw_df = _make_synthetic(100)
        raw_path = tmp_path / "raw.parquet"
        raw_df.to_parquet(raw_path, index=False)

        features_df = build_features_df(raw_df, registry)
        out_path = tmp_path / "features.parquet"

        # Write with a FAKE stale version.
        write_features_parquet(features_df, out_path, "stale_version_abc", raw_path)

        # Now load_features_or_rebuild should detect mismatch and rebuild.
        result = load_features_or_rebuild(raw_path, out_path, registry)

        # After rebuild, stored version must match live.
        from factors.build_features import read_feature_version
        stored = read_feature_version(out_path)
        live = compute_feature_version(registry)
        assert stored == live
        assert len(result) == 100

    def test_fresh_parquet_not_rebuilt(self, tmp_path, registry):
        from factors.build_features import (
            build_features,
            read_feature_version,
        )

        raw_df = _make_synthetic(100)
        raw_path = tmp_path / "raw.parquet"
        raw_df.to_parquet(raw_path, index=False)
        out_path = tmp_path / "features.parquet"

        build_features(raw_path, out_path, registry)
        mtime_1 = out_path.stat().st_mtime

        # Build again — should detect up-to-date and return early.
        from factors.build_features import load_features_or_rebuild
        load_features_or_rebuild(raw_path, out_path, registry)
        mtime_2 = out_path.stat().st_mtime

        # File shouldn't have been rewritten.
        assert mtime_1 == mtime_2


# ---------------------------------------------------------------------------
# Determinism: two builds produce identical factor values
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_two_builds_identical(self, registry):
        raw = _make_synthetic(200, seed=99)
        df1 = registry.compute_all(raw)
        df2 = registry.compute_all(raw)
        pd.testing.assert_frame_equal(df1, df2)


# ---------------------------------------------------------------------------
# menu_for_prompt
# ---------------------------------------------------------------------------


class TestMenuForPrompt:
    def test_contains_all_factors(self, registry):
        menu = registry.menu_for_prompt()
        for name in EXPECTED_FACTORS:
            assert name in menu

    def test_contains_warmup(self, registry):
        menu = registry.menu_for_prompt()
        assert "warmup=" in menu


# ---------------------------------------------------------------------------
# Compute primitives (factors/operators.py)
# ---------------------------------------------------------------------------


class TestComputePrimitives:
    """factors/operators.py primitives are causal building blocks, NOT
    registered factors (so the G1 future-ops scanner never reaches them)."""

    def test_decay_linear_weights_are_linear_and_trailing(self):
        # Linearly increasing series: with linear weights 1..w (newest heaviest),
        # the weighted MA of a perfectly linear ramp is computable in closed form.
        s = pd.Series([float(i) for i in range(10)])
        out = decay_linear(s, window=4)
        # First 3 positions are warmup (window-1) -> NaN.
        assert out.iloc[:3].isna().all()
        assert out.iloc[3:].notna().all()
        # At position 3 the window is [0,1,2,3], weights [1,2,3,4] (sum 10):
        # (0*1 + 1*2 + 2*3 + 3*4) / 10 = (0+2+6+12)/10 = 2.0
        assert out.iloc[3] == pytest.approx(2.0)
        # At position 9 the window is [6,7,8,9], weights [1,2,3,4]:
        # (6+14+24+36)/10 = 80/10 = 8.0
        assert out.iloc[9] == pytest.approx(8.0)

    def test_decay_linear_is_causal_window_1_is_identity(self):
        s = pd.Series([3.0, 1.0, 4.0, 1.0, 5.0])
        out = decay_linear(s, window=1)
        # window=1 -> single weight -> identity, no warmup.
        pd.testing.assert_series_equal(out, s, check_names=False)

    def test_rolling_backward_percentile_rank_of_last(self):
        # Strictly increasing series: the last value is always the max within
        # any trailing window -> percentile rank == 1.0 once warmed up.
        s = pd.Series([float(i) for i in range(10)])
        out = rolling_backward_percentile(s, window=5)
        assert out.iloc[:4].isna().all()       # warmup = window-1
        # NOTE: `pd.Series == pytest.approx(scalar)` compares element-wise against
        # the ApproxScalar object (all-False); extract .values and use np.allclose.
        assert np.allclose(out.iloc[4:].values, 1.0)

    def test_rolling_backward_percentile_min_is_zero(self):
        # Strictly decreasing -> last value is the min within the window -> 0.0.
        s = pd.Series([float(9 - i) for i in range(10)])
        out = rolling_backward_percentile(s, window=5)
        assert out.iloc[:4].isna().all()
        # NOTE: `pd.Series == pytest.approx(scalar)` compares element-wise against
        # the ApproxScalar object (all-False); extract .values and use np.allclose.
        assert np.allclose(out.iloc[4:].values, 0.0, atol=1e-9)

    def test_rolling_backward_percentile_midpoint(self):
        # Window [last is the median of 5 distinct ascending values then a dip]:
        # window=5 ending at a value that is the 3rd-smallest of 5 -> rank 0.5.
        s = pd.Series([10.0, 20.0, 30.0, 40.0, 25.0])
        out = rolling_backward_percentile(s, window=5)
        # Within [10,20,30,40,25] the last value 25 has 2 strictly-below
        # (10,20) out of (5-1)=4 others -> 2/4 = 0.5.
        assert out.iloc[4] == pytest.approx(0.5)

    def test_rolling_backward_percentile_window_1_is_zero(self):
        # window=1: no other values to rank against; the (w-1) divisor guard
        # returns 0.0 for every bar (contrast decay_linear(window=1) = identity).
        s = pd.Series([3.0, 1.0, 4.0, 1.0, 5.0])
        out = rolling_backward_percentile(s, window=1)
        assert (out == 0.0).all()

    def test_primitives_not_in_registry(self):
        # Contract: primitives are never registered (G1 never scans them).
        from factors.registry import get_registry
        names = get_registry().list_names()
        assert "decay_linear" not in names
        assert "rolling_backward_percentile" not in names


class TestIntrabarPush:
    def test_known_value(self):
        from factors.price import compute_intrabar_push
        df = pd.DataFrame({
            "open":  [100.0, 50.0],
            "high":  [110.0, 60.0],
            "low":   [ 90.0, 40.0],
            "close": [105.0, 45.0],
        })
        out = compute_intrabar_push(df)
        # bar0: (105-100)/((110-90)+1e-9) = 5/20.000000001 ~ 0.25
        assert out.iloc[0] == pytest.approx(0.25, abs=1e-7)
        # bar1: (45-50)/((60-40)+1e-9) = -5/20 ~ -0.25
        assert out.iloc[1] == pytest.approx(-0.25, abs=1e-7)

    def test_zero_range_does_not_divide_by_zero(self):
        from factors.price import compute_intrabar_push
        # Frozen-price bar (O=H=L=C): numerator 0, denom 1e-9 -> 0.0, not NaN/inf.
        df = pd.DataFrame({
            "open": [50.0], "high": [50.0], "low": [50.0], "close": [50.0],
        })
        out = compute_intrabar_push(df)
        assert out.iloc[0] == pytest.approx(0.0)
        assert np.isfinite(out.iloc[0])

    def test_spec_registered_warmup_zero(self):
        from factors.registry import get_registry
        spec = get_registry().get("intrabar_push")
        assert spec.warmup_bars == 0
        assert sorted(spec.inputs) == ["close", "high", "low", "open"]
        assert spec.category == "price"


class TestRangeOverAtr:
    def test_warmup_then_finite(self):
        from factors.volatility import compute_range_over_atr
        rng = np.random.default_rng(7)
        n = 60
        df = pd.DataFrame({
            "high":  100 + rng.random(n) * 5 + 2,
            "low":   100 + rng.random(n) * 5 - 2,
            "close": 100 + rng.random(n) * 5,
        })
        # ensure high>=low
        df["high"] = np.maximum(df["high"], df["low"] + 0.5)
        out = compute_range_over_atr(df)
        # ATR-14 warmup is 14 (1 to shift + 13 to rolling) -> NaN at 0..13.
        assert out.iloc[:14].isna().all()
        assert out.iloc[14:].notna().all()
        assert np.isfinite(out.iloc[14:]).all()

    def test_matches_independent_atr_recompute(self):
        from factors.volatility import compute_range_over_atr, compute_atr_14
        rng = np.random.default_rng(11)
        n = 40
        df = pd.DataFrame({
            "high":  100 + rng.random(n) * 5 + 2,
            "low":   100 + rng.random(n) * 5 - 2,
            "close": 100 + rng.random(n) * 5,
        })
        df["high"] = np.maximum(df["high"], df["low"] + 0.5)
        # range_over_atr must equal (high-low)/atr_14 using the SAME causal ATR.
        atr = compute_atr_14(df)
        expected = (df["high"] - df["low"]) / atr
        out = compute_range_over_atr(df)
        pd.testing.assert_series_equal(
            out.iloc[14:], expected.iloc[14:], check_names=False,
        )

    def test_spec_registered(self):
        from factors.registry import get_registry
        spec = get_registry().get("range_over_atr")
        assert spec.warmup_bars == 14
        assert sorted(spec.inputs) == ["close", "high", "low"]
        assert spec.category == "volatility"


class TestCdfRealizedVol720:
    def test_warmup_boundary(self):
        from factors.volatility import compute_cdf_realized_vol_720
        rng = np.random.default_rng(3)
        n = 760
        df = pd.DataFrame({"close": 100 + np.cumsum(rng.standard_normal(n)) * 0.5})
        out = compute_cdf_realized_vol_720(df)
        # warmup = 24 (realized_vol) + 719 (percentile window-1) = 743.
        assert out.iloc[:743].isna().all()
        assert out.iloc[743:].notna().all()
        # Percentile output is bounded [0, 1].
        post = out.iloc[743:]
        assert (post >= 0.0).all() and (post <= 1.0).all()

    def test_equals_primitive_composition(self):
        from factors.volatility import compute_cdf_realized_vol_720
        from factors.operators import rolling_backward_percentile
        rng = np.random.default_rng(99)
        n = 760
        df = pd.DataFrame({"close": 100 + np.cumsum(rng.standard_normal(n)) * 0.5})
        rv = df["close"].pct_change(1).rolling(24).std()
        expected = rolling_backward_percentile(rv, 720)
        out = compute_cdf_realized_vol_720(df)
        pd.testing.assert_series_equal(
            out.iloc[743:], expected.iloc[743:], check_names=False,
        )

    def test_spec_registered(self):
        from factors.registry import get_registry
        spec = get_registry().get("cdf_realized_vol_720")
        assert spec.warmup_bars == 743
        assert spec.inputs == ["close"]
        assert spec.category == "volatility"


class TestDecayLinearClose:
    def test_48_warmup_and_value(self):
        from factors.moving_averages import compute_decay_linear_close_48
        from factors.operators import decay_linear
        rng = np.random.default_rng(5)
        df = pd.DataFrame({"close": 100 + np.cumsum(rng.standard_normal(200)) * 0.3})
        out = compute_decay_linear_close_48(df)
        assert out.iloc[:47].isna().all()
        assert out.iloc[47:].notna().all()
        expected = decay_linear(df["close"], 48)
        pd.testing.assert_series_equal(
            out.iloc[47:], expected.iloc[47:], check_names=False,
        )

    def test_168_warmup(self):
        from factors.moving_averages import compute_decay_linear_close_168
        rng = np.random.default_rng(6)
        df = pd.DataFrame({"close": 100 + np.cumsum(rng.standard_normal(300)) * 0.3})
        out = compute_decay_linear_close_168(df)
        assert out.iloc[:167].isna().all()
        assert out.iloc[167:].notna().all()

    def test_specs_registered(self):
        from factors.registry import get_registry
        reg = get_registry()
        s48 = reg.get("decay_linear_close_48")
        s168 = reg.get("decay_linear_close_168")
        assert s48.warmup_bars == 47
        assert s168.warmup_bars == 167
        assert s48.inputs == ["close"] and s168.inputs == ["close"]
        # NOTE: real category is "moving_averages" (plural) — plan said "moving_average"
        # (singular); using the real convention from existing SPEC_SMA_20 etc.
        assert s48.category == "moving_averages" and s168.category == "moving_averages"


# ---------------------------------------------------------------------------
# Task 4b — presence guard: 5 new Path B arc factors
# ---------------------------------------------------------------------------

NEW_FACTORS_THIS_ARC = [
    "intrabar_push",
    "range_over_atr",
    "cdf_realized_vol_720",
    "decay_linear_close_48",
    "decay_linear_close_168",
]


class TestNewFactorPresence:
    """Task 4b presence guard: the 5 new factors are registered and the
    library now has exactly 23 factors, alphabetically ordered."""

    def test_expected_factors_has_23(self):
        assert len(EXPECTED_FACTORS) == 23

    def test_expected_factors_is_alphabetical(self):
        assert EXPECTED_FACTORS == sorted(EXPECTED_FACTORS)

    def test_five_new_factors_registered(self, registry):
        names = set(registry.list_names())
        for n in NEW_FACTORS_THIS_ARC:
            assert n in names, f"new factor {n!r} not registered"

    def test_total_is_23_and_matches_expected(self, registry):
        names = registry.list_names()
        assert len(names) == 23
        assert names == EXPECTED_FACTORS


# ---------------------------------------------------------------------------
# Task 11 — feature_version sensitivity: adding/removing factors bumps hash
# ---------------------------------------------------------------------------


class TestFeatureVersionSensitivity:
    """compute_feature_version is module-level (in factors.registry); there is
    NO FactorRegistry.feature_version() method."""

    def _subset_registry(self, drop: list[str]) -> FactorRegistry:
        """A fresh registry holding every core factor EXCEPT `drop`."""
        full = get_registry()
        sub = FactorRegistry()
        for name in full.list_names():
            if name not in drop:
                sub.register(full.get(name))
        return sub

    def test_full_differs_from_subset_missing_new_factors(self):
        full = get_registry()
        sub = self._subset_registry(drop=NEW_FACTORS_THIS_ARC)
        assert len(sub.list_names()) == 18
        assert len(full.list_names()) == 23
        # Adding the 5 new factors MUST change the feature_version hash.
        assert compute_feature_version(full) != compute_feature_version(sub)

    def test_version_is_deterministic(self):
        full = get_registry()
        assert compute_feature_version(full) == compute_feature_version(full)

    def test_dropping_one_new_factor_changes_version(self):
        full = get_registry()
        sub = self._subset_registry(drop=["intrabar_push"])
        assert len(sub.list_names()) == 22
        assert compute_feature_version(full) != compute_feature_version(sub)


# ---------------------------------------------------------------------------
# Task 12 — build_features_df stamps the 23-factor feature_version
# ---------------------------------------------------------------------------


class TestForceRebuildFeatureVersion:
    """build_features_df stamps the live 23-factor feature_version; the
    full `--force-rebuild` over the canonical dataset is slow because
    cdf_realized_vol_720 is O(N*720) — exercised on a synthetic frame here."""

    def _synthetic_raw(self, n: int) -> pd.DataFrame:
        rng = np.random.default_rng(123)
        close = 100 + np.cumsum(rng.standard_normal(n)) * 0.5
        idx = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
        return pd.DataFrame({
            "open_time_utc": idx,
            "open": close,
            "high": close + np.abs(rng.standard_normal(n)) * 0.5,
            "low": close - np.abs(rng.standard_normal(n)) * 0.5,
            "close": close,
            "volume": rng.random(n) * 10 + 1,
        })

    def test_rebuilt_features_carry_23_factor_version(self):
        from factors.build_features import build_features_df
        from factors.registry import compute_feature_version, get_registry

        raw = self._synthetic_raw(800)  # > 743 warmup for cdf_realized_vol_720
        reg = get_registry()
        out = build_features_df(raw, reg)
        # All 23 factors present as columns (plus open_time_utc).
        for name in EXPECTED_FACTORS:
            assert name in out.columns
        # build_features_df returns open_time_utc + one column per factor.
        assert len(out.columns) == 1 + 23

        live_version = compute_feature_version(reg)

        # The 18-factor (pre-arc) hash must differ -> rebuild is required.
        sub = FactorRegistry()
        for name in reg.list_names():
            if name not in NEW_FACTORS_THIS_ARC:
                sub.register(reg.get(name))
        old_version = compute_feature_version(sub)
        assert live_version != old_version

    def test_force_rebuild_roundtrips_version_via_parquet(self, tmp_path):
        from factors.build_features import (
            build_features_df,
            read_feature_version,
            write_features_parquet,
        )
        from factors.registry import compute_feature_version, get_registry

        raw = self._synthetic_raw(800)
        reg = get_registry()
        out = build_features_df(raw, reg)
        live_version = compute_feature_version(reg)

        # Write a synthetic raw parquet so write_features_parquet has a real
        # source_parquet path to embed (mirrors TestBuildFeatures.built_parquet).
        raw_path = tmp_path / "raw.parquet"
        raw.to_parquet(raw_path, index=False)

        parquet_path = tmp_path / "features.parquet"
        write_features_parquet(out, parquet_path, live_version, raw_path)

        stored = read_feature_version(parquet_path)
        assert stored == live_version

        sub = FactorRegistry()
        for name in reg.list_names():
            if name not in NEW_FACTORS_THIS_ARC:
                sub.register(reg.get(name))
        assert stored != compute_feature_version(sub)
