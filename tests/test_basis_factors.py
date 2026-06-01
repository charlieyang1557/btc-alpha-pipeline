"""Tests for basis factors (Path C Phase B, Tasks B1-B4).

Covers all 5 basis factor functions in ``factors.basis``:
- ``basis_sign``
- ``basis_ewm_240``
- ``basis_ewm_480``
- ``basis_pct_rank_2160``
- ``basis_ewm_240_pctrank_2160``

Each factor is tested for:
- Known-value correctness (spot-checks against pandas primitives or explicit logic).
- Warmup / NaN boundaries.
- Causality (delete-future invariance: truncating future rows leaves earlier values unchanged).
- Output dtype and range constraints.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factors.basis import (
    basis_ewm_240,
    basis_ewm_240_pctrank_2160,
    basis_ewm_480,
    basis_pct_rank_2160,
    basis_sign,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _df(basis_rel: list[float]) -> pd.DataFrame:
    """Build a minimal DataFrame with a 'basis_rel' column."""
    return pd.DataFrame({"basis_rel": basis_rel})


def _df_rng(n: int, seed: int = 42) -> pd.DataFrame:
    """Build a DataFrame of length n with pseudo-random basis_rel values."""
    rng = np.random.default_rng(seed)
    vals = rng.normal(loc=0.0001, scale=0.002, size=n)
    return _df(vals.tolist())


# ---------------------------------------------------------------------------
# basis_sign
# ---------------------------------------------------------------------------


class TestBasisSign:
    def test_known_values(self) -> None:
        """Known basis_rel values map to correct signs."""
        df = _df([0.002, -0.001, 0.0, 0.0005])
        result = basis_sign(df)
        expected = pd.Series([1.0, -1.0, 0.0, 1.0])
        pd.testing.assert_series_equal(result.reset_index(drop=True), expected, check_names=False)

    def test_output_dtype_float64(self) -> None:
        df = _df([0.001, -0.001])
        assert basis_sign(df).dtype == np.float64

    def test_nan_propagates(self) -> None:
        """NaN basis_rel -> NaN output."""
        df = _df([float("nan"), 0.001])
        result = basis_sign(df)
        assert np.isnan(result.iloc[0])
        assert result.iloc[1] == 1.0

    def test_values_in_set(self) -> None:
        """Output contains only {-1.0, 0.0, 1.0} or NaN."""
        df = _df_rng(50)
        result = basis_sign(df)
        non_nan = result.dropna()
        assert set(non_nan.unique()).issubset({-1.0, 0.0, 1.0})


# ---------------------------------------------------------------------------
# basis_ewm_240
# ---------------------------------------------------------------------------


class TestBasisEwm240:
    def test_matches_pandas_ewm(self) -> None:
        """Output equals pandas ewm(span=240, adjust=False).mean()."""
        df = _df_rng(300)
        result = basis_ewm_240(df)
        expected = df["basis_rel"].ewm(span=240, adjust=False).mean()
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_adjust_false_semantics_first_value(self) -> None:
        """With adjust=False, index-0 EWM equals the first observation (no warm-up trick)."""
        df = _df([0.005, 0.010, 0.003])
        result = basis_ewm_240(df)
        # With adjust=False, first EWM value equals first obs
        assert result.iloc[0] == pytest.approx(df["basis_rel"].iloc[0])

    def test_causality_delete_future(self) -> None:
        """Delete-future invariance: truncating rows > k leaves earlier values unchanged."""
        df = _df_rng(400)
        result_full = basis_ewm_240(df)
        k = 250
        result_trunc = basis_ewm_240(df.iloc[:k])
        pd.testing.assert_series_equal(
            result_full.iloc[:k].reset_index(drop=True),
            result_trunc.reset_index(drop=True),
            check_names=False,
        )

    def test_output_dtype_float64(self) -> None:
        df = _df_rng(50)
        assert basis_ewm_240(df).dtype == np.float64


# ---------------------------------------------------------------------------
# basis_ewm_480
# ---------------------------------------------------------------------------


class TestBasisEwm480:
    def test_matches_pandas_ewm(self) -> None:
        """Output equals pandas ewm(span=480, adjust=False).mean()."""
        df = _df_rng(600)
        result = basis_ewm_480(df)
        expected = df["basis_rel"].ewm(span=480, adjust=False).mean()
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_adjust_false_semantics_first_value(self) -> None:
        """With adjust=False, index-0 EWM equals the first observation."""
        df = _df([0.005, 0.010, 0.003])
        result = basis_ewm_480(df)
        assert result.iloc[0] == pytest.approx(df["basis_rel"].iloc[0])

    def test_causality_delete_future(self) -> None:
        """Delete-future invariance: truncating rows > k leaves earlier values unchanged."""
        df = _df_rng(600)
        result_full = basis_ewm_480(df)
        k = 400
        result_trunc = basis_ewm_480(df.iloc[:k])
        pd.testing.assert_series_equal(
            result_full.iloc[:k].reset_index(drop=True),
            result_trunc.reset_index(drop=True),
            check_names=False,
        )

    def test_span_larger_than_240(self) -> None:
        """EWM-480 converges more slowly than EWM-240 (larger span -> more memory)."""
        df = _df_rng(500)
        ewm240 = basis_ewm_240(df)
        ewm480 = basis_ewm_480(df)
        # EWM-480 should be 'smoother': smaller absolute difference from prior value
        diff240 = (ewm240.diff().abs()).mean()
        diff480 = (ewm480.diff().abs()).mean()
        assert diff480 < diff240, "EWM-480 should be smoother (smaller mean abs diff) than EWM-240"


# ---------------------------------------------------------------------------
# EWM NaN-policy (FIX 2 — null-policy violation guard)
# ---------------------------------------------------------------------------


class TestBasisEwmNanPolicy:
    """FIX 2: EWM factors must output NaN at bars where basis_rel is NaN, not
    carry forward the prior EWM state (which would violate the null policy)."""

    def test_basis_ewm_propagates_nan(self) -> None:
        """Input [0.01]*240 + [nan] + [0.02] → the EWM output at the NaN bar is NaN,
        not a carry-forward of the pre-NaN EWM value.

        Specifically tests basis_ewm_240 (the primary EWM factor). The masked
        implementation uses .where(basis_rel.notna()) to zero out the carry-forward.
        """
        vals = [0.01] * 240 + [float("nan")] + [0.02]
        df = _df(vals)
        result_240 = basis_ewm_240(df)
        nan_idx = 240
        assert pd.isna(result_240.iloc[nan_idx]), (
            f"basis_ewm_240: expected NaN at the NaN basis_rel bar (index {nan_idx}), "
            f"got {result_240.iloc[nan_idx]!r} (carry-forward violates null policy)."
        )
        # Also verify the bar after NaN is non-NaN (the EWM resumes from there).
        assert not pd.isna(result_240.iloc[nan_idx + 1]), (
            f"basis_ewm_240: bar after NaN should be non-NaN, "
            f"got {result_240.iloc[nan_idx + 1]!r}"
        )

    def test_basis_ewm_480_propagates_nan(self) -> None:
        """basis_ewm_480 also outputs NaN at a NaN basis_rel bar."""
        vals = [0.01] * 240 + [float("nan")] + [0.02]
        df = _df(vals)
        result_480 = basis_ewm_480(df)
        nan_idx = 240
        assert pd.isna(result_480.iloc[nan_idx]), (
            f"basis_ewm_480: expected NaN at the NaN basis_rel bar (index {nan_idx}), "
            f"got {result_480.iloc[nan_idx]!r} (carry-forward violates null policy)."
        )


# ---------------------------------------------------------------------------
# basis_pct_rank_2160
# ---------------------------------------------------------------------------


class TestBasisPctRank2160:
    def test_warmup_nan_before_2160(self) -> None:
        """Indices 0..2158 are NaN (min_periods=2160)."""
        df = _df_rng(2200)
        result = basis_pct_rank_2160(df)
        # All of indices 0..2158 must be NaN
        assert result.iloc[:2159].isna().all(), "Indices 0..2158 must all be NaN"

    def test_first_valid_at_2159(self) -> None:
        """Index 2159 (the 2160th bar) is the first non-NaN value."""
        df = _df_rng(2200)
        result = basis_pct_rank_2160(df)
        assert not np.isnan(result.iloc[2159]), "Index 2159 must be first non-NaN"

    def test_window_max_gives_rank_1(self) -> None:
        """A series where the last element is the max of the window -> rank 1.0."""
        # Build a 2160-element series: all small values except the last which is large
        vals = [0.001] * 2159 + [0.999]
        df = _df(vals)
        result = basis_pct_rank_2160(df)
        assert result.iloc[2159] == pytest.approx(1.0), (
            f"Max of window should rank 1.0, got {result.iloc[2159]}"
        )

    def test_output_in_unit_interval(self) -> None:
        """All non-NaN outputs are in [0.0, 1.0]."""
        df = _df_rng(2250)
        result = basis_pct_rank_2160(df)
        non_nan = result.dropna()
        assert (non_nan >= 0.0).all() and (non_nan <= 1.0).all()

    def test_causality_delete_future(self) -> None:
        """Delete-future invariance: truncating future rows leaves value at k-1 unchanged."""
        df = _df_rng(2300)
        result_full = basis_pct_rank_2160(df)
        k = 2200
        result_trunc = basis_pct_rank_2160(df.iloc[:k])
        # Compare the last valid index of the truncated result against the full
        last_idx = k - 1
        assert result_full.iloc[last_idx] == pytest.approx(result_trunc.iloc[last_idx], rel=1e-10)

    def test_explicit_count_not_mean(self) -> None:
        """Spot-check: known window where exact count is verifiable."""
        # 2160 values: 1000 below zero, 1160 >= zero, last value = 0.0
        # rank of 0.0: fraction of window with value <= 0.0
        # = count(values <= 0) / 2160
        # values <= 0 = 1000 negatives + 1 zero (the last bar) = 1001
        vals = [-0.001] * 1000 + [0.001] * 1159 + [0.0]
        df = _df(vals)
        result = basis_pct_rank_2160(df)
        expected_rank = 1001 / 2160
        assert result.iloc[2159] == pytest.approx(expected_rank, rel=1e-9)


# ---------------------------------------------------------------------------
# basis_ewm_240_pctrank_2160
# ---------------------------------------------------------------------------


class TestBasisEwm240Pctrank2160:
    def test_warmup_nan_before_2160(self) -> None:
        """Indices 0..2158 are NaN (percentile min_periods=2160 dominates)."""
        df = _df_rng(2250)
        result = basis_ewm_240_pctrank_2160(df)
        assert result.iloc[:2159].isna().all(), "Indices 0..2158 must all be NaN"

    def test_first_valid_at_2159(self) -> None:
        """Index 2159 (the 2160th bar) is the first non-NaN value."""
        df = _df_rng(2250)
        result = basis_ewm_240_pctrank_2160(df)
        assert not np.isnan(result.iloc[2159]), "Index 2159 must be first non-NaN"

    def test_output_in_unit_interval(self) -> None:
        """All non-NaN outputs are in [0.0, 1.0]."""
        df = _df_rng(2250)
        result = basis_ewm_240_pctrank_2160(df)
        non_nan = result.dropna()
        assert (non_nan >= 0.0).all() and (non_nan <= 1.0).all()

    def test_causality_delete_future(self) -> None:
        """Delete-future invariance: truncating future rows leaves value at k-1 unchanged."""
        df = _df_rng(2300)
        result_full = basis_ewm_240_pctrank_2160(df)
        k = 2200
        result_trunc = basis_ewm_240_pctrank_2160(df.iloc[:k])
        last_idx = k - 1
        assert result_full.iloc[last_idx] == pytest.approx(result_trunc.iloc[last_idx], rel=1e-10)

    def test_differs_from_raw_pctrank(self) -> None:
        """EWM-smoothed pctrank differs from raw pctrank (smoothing changes the ranked series)."""
        df = _df_rng(2300)
        raw = basis_pct_rank_2160(df)
        smoothed = basis_ewm_240_pctrank_2160(df)
        # They should generally differ (different input series being ranked)
        diff = (raw.dropna() - smoothed.dropna()).abs().mean()
        assert diff > 0.0, "EWM-smoothed pctrank must differ from raw pctrank"
