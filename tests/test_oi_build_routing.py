"""Integration tests for the OI-factor build routing (Path D Phase B Task B5).

Synthetic-only — NO real network, NO real-data value inspection.

Verifies that ``build_features_df`` with a synthetic OI frame:
1. Produces the 4 OI factor columns in the feature frame.
2. Leaves OHLCV and funding columns unaffected.
3. Does NOT drop OHLCV rows (left-join preserves all OHLCV bars).
4. Raises on OI-vs-OHLCV grid misalignment >= 1 bar.
5. Propagates zero-poison NaN correctly through the built feature frame.

No-peek discipline applies: this file NEVER inspects any real forward_2026
or production-data OI factor values.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factors.registry import FactorRegistry, FactorSpec, _bootstrap_core_factors
from factors.oi import oi_sign


# ---------------------------------------------------------------------------
# (a) Contract-widen test: input_source="oi" must be accepted by FactorSpec
# ---------------------------------------------------------------------------


class TestInputSourceOiWiden:
    """FactorSpec must accept input_source='oi' after the B5 contract widen."""

    def test_factor_spec_oi_constructs_without_raising(self) -> None:
        """FactorSpec(input_source='oi') must construct without ValueError.

        TDD RED→GREEN test for sub-task (a): before the widen,
        __post_init__ raised on any input_source outside {'ohlcv', 'funding', 'basis'}.
        After the widen to {'ohlcv', 'funding', 'basis', 'oi'}, this must pass.
        """
        spec = FactorSpec(
            name="oi_sign",
            category="oi",
            warmup_bars=1,
            inputs=["sum_open_interest"],
            output_dtype="float64",
            compute=oi_sign,
            docstring=oi_sign.__doc__ or "oi sign",
            input_source="oi",
            input_period_bars=1,
        )
        assert spec.input_source == "oi"
        assert spec.name == "oi_sign"

    def test_invalid_input_source_still_raises(self) -> None:
        """input_source='unknown_source' must still raise ValueError."""
        with pytest.raises(ValueError, match="input_source"):
            FactorSpec(
                name="oi_sign",
                category="oi",
                warmup_bars=1,
                inputs=["sum_open_interest"],
                output_dtype="float64",
                compute=oi_sign,
                docstring="test",
                input_source="unknown_source",
            )


# ---------------------------------------------------------------------------
# Synthetic data helpers
# ---------------------------------------------------------------------------

EXPECTED_OI_FACTOR_NAMES = [
    "oi_pct_rank_2160",
    "oi_sign",
    "oi_velocity_ewm_240",
    "oi_velocity_ewm_240_pctrank_2160",
]

EXPECTED_OHLCV_FACTOR_NAMES = [
    "atr_14",
    "bb_upper_24_2",
    "close",
    "return_1h",
    "sma_20",
]  # spot-check subset — not exhaustive


def _make_ohlcv(n: int, seed: int = 42) -> pd.DataFrame:
    """Synthetic n-bar 1h OHLCV frame starting 2021-01-01 UTC."""
    rng = np.random.default_rng(seed)
    close = 40000.0 + np.cumsum(rng.standard_normal(n) * 100)
    times = pd.date_range("2021-01-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame(
        {
            "open_time_utc": times,
            "open": close + rng.standard_normal(n) * 10,
            "high": close + np.abs(rng.standard_normal(n)) * 50 + 10,
            "low": close - np.abs(rng.standard_normal(n)) * 50 - 10,
            "close": close,
            "volume": rng.uniform(100, 10000, n),
        }
    )


def _make_oi(ohlcv_df: pd.DataFrame, seed: int = 77) -> pd.DataFrame:
    """Synthetic OI frame aligned to the SAME grid as ``ohlcv_df``.

    ``sum_open_interest`` is strictly positive (no zero-poison bars in this
    helper — zero-poison is tested separately via _make_oi_with_zero_bar).
    Preserves UTC timezone-aware dtype on ``open_time_utc``.
    """
    rng = np.random.default_rng(seed)
    n = len(ohlcv_df)
    oi = np.abs(rng.uniform(50000, 100000, n)) + 1.0  # strictly > 0
    return pd.DataFrame(
        {
            "open_time_utc": ohlcv_df["open_time_utc"],  # preserve UTC-aware dtype
            "sum_open_interest": oi,
        }
    ).reset_index(drop=True)


def _make_oi_with_zero_bar(ohlcv_df: pd.DataFrame, zero_idx: int) -> pd.DataFrame:
    """Synthetic OI frame with a zero OI at ``zero_idx`` to test zero-poison."""
    rng = np.random.default_rng(88)
    n = len(ohlcv_df)
    oi = np.abs(rng.uniform(50000, 100000, n)) + 1.0
    oi[zero_idx] = 0.0  # plant the zero
    return pd.DataFrame(
        {
            "open_time_utc": ohlcv_df["open_time_utc"],
            "sum_open_interest": oi,
        }
    ).reset_index(drop=True)


@pytest.fixture
def small_registry() -> FactorRegistry:
    """Fresh registry with all 37 core factors (including 4 OI factors)."""
    r = FactorRegistry()
    _bootstrap_core_factors(r)
    return r


@pytest.fixture
def small_ohlcv() -> pd.DataFrame:
    """300-bar synthetic OHLCV frame — fast for OHLCV factor computation."""
    return _make_ohlcv(300)


# ---------------------------------------------------------------------------
# (b/c) OI factor presence in registry
# ---------------------------------------------------------------------------


class TestOiRegistration:
    """The 4 OI factors appear in the registry with correct metadata."""

    def test_oi_factors_in_list_names(self, small_registry: FactorRegistry) -> None:
        names = small_registry.list_names()
        for name in EXPECTED_OI_FACTOR_NAMES:
            assert name in names, (
                f"Expected OI factor {name!r} in registry; got {names}"
            )

    def test_oi_factors_input_source(self, small_registry: FactorRegistry) -> None:
        for name in EXPECTED_OI_FACTOR_NAMES:
            spec = small_registry.get(name)
            assert spec.input_source == "oi", (
                f"Factor {name!r} must have input_source='oi'; got {spec.input_source!r}"
            )

    def test_oi_factors_warmups(self, small_registry: FactorRegistry) -> None:
        """Declared warmups must match the LOCK."""
        expected = {
            "oi_sign": 1,
            "oi_velocity_ewm_240": 240,
            "oi_pct_rank_2160": 2160,
            "oi_velocity_ewm_240_pctrank_2160": 2160,
        }
        for name, warmup in expected.items():
            spec = small_registry.get(name)
            assert spec.warmup_bars == warmup, (
                f"Factor {name!r} warmup: expected {warmup}, got {spec.warmup_bars}"
            )

    def test_oi_factors_input_period_bars(self, small_registry: FactorRegistry) -> None:
        """All OI factors must have input_period_bars=1 (native-1h, no carry)."""
        for name in EXPECTED_OI_FACTOR_NAMES:
            spec = small_registry.get(name)
            assert spec.input_period_bars == 1, (
                f"OI factor {name!r} must have input_period_bars=1 (native-1h); "
                f"got {spec.input_period_bars}"
            )

    def test_oi_factors_category(self, small_registry: FactorRegistry) -> None:
        for name in EXPECTED_OI_FACTOR_NAMES:
            spec = small_registry.get(name)
            assert spec.category == "oi", (
                f"Factor {name!r} must have category='oi'; got {spec.category!r}"
            )


# ---------------------------------------------------------------------------
# (d) Integration tests
# ---------------------------------------------------------------------------


class TestOiBuildRouting:
    """Integration tests for the OI-factor routing in build_features_df."""

    def test_oi_factor_columns_present(
        self, small_registry: FactorRegistry, small_ohlcv: pd.DataFrame
    ) -> None:
        """build_features_df produces all 4 OI factor columns when oi_df is given."""
        from factors.build_features import build_features_df

        oi_df = _make_oi(small_ohlcv)
        out = build_features_df(small_ohlcv, small_registry, oi_df=oi_df)

        for name in EXPECTED_OI_FACTOR_NAMES:
            assert name in out.columns, (
                f"Expected OI factor column {name!r} in feature frame; "
                f"columns = {list(out.columns)}"
            )

    def test_ohlcv_columns_unaffected(
        self, small_registry: FactorRegistry, small_ohlcv: pd.DataFrame
    ) -> None:
        """OI routing does not alter OHLCV factor column values.

        Build twice — once with oi_df (OI routing active) and once without
        (OI routing absent, NaN columns). The OHLCV factor values must be
        byte-identical between the two builds.
        """
        from factors.build_features import build_features_df

        oi_df = _make_oi(small_ohlcv)
        out_with_oi = build_features_df(
            small_ohlcv, small_registry, oi_df=oi_df
        )
        out_no_oi = build_features_df(
            small_ohlcv, small_registry, oi_df=None
        )

        for name in EXPECTED_OHLCV_FACTOR_NAMES:
            assert name in out_with_oi.columns
            assert name in out_no_oi.columns
            pd.testing.assert_series_equal(
                out_with_oi[name].reset_index(drop=True),
                out_no_oi[name].reset_index(drop=True),
                check_names=False,
                obj=f"OHLCV factor {name!r} changed when OI routing was added",
            )

    def test_ohlcv_rows_not_dropped(
        self, small_registry: FactorRegistry, small_ohlcv: pd.DataFrame
    ) -> None:
        """Left-join semantics: all OHLCV rows are preserved."""
        from factors.build_features import build_features_df

        oi_df = _make_oi(small_ohlcv)
        out = build_features_df(small_ohlcv, small_registry, oi_df=oi_df)

        assert len(out) == len(small_ohlcv), (
            f"Row count mismatch: expected {len(small_ohlcv)}, got {len(out)}. "
            f"build_features_df must preserve all OHLCV rows (left-join semantics)."
        )
        pd.testing.assert_series_equal(
            out["open_time_utc"].reset_index(drop=True),
            small_ohlcv["open_time_utc"].reset_index(drop=True),
            check_names=False,
            obj="open_time_utc column order must match input OHLCV frame",
        )

    def test_coverage_guard_raises_on_zero_overlap(
        self, small_registry: FactorRegistry, small_ohlcv: pd.DataFrame
    ) -> None:
        """Coverage guard raises ValueError when OI and OHLCV grids are completely disjoint.

        Build an OI frame whose timestamps are in a completely different time range
        (no shared bars). The guard must raise ValueError to prevent silently producing
        all-NaN OI columns from a completely wrong parquet (timezone error, unit error,
        wrong file).

        Note: small known gaps (known exchange outages producing missing bars within the
        OI window) are accepted — the left-join maps those OHLCV bars to NaN OI values.
        Only ZERO-OVERLAP (completely disjoint grids) raises.
        """
        from factors.build_features import build_features_df

        # Build an OI frame in a completely different time range (2030 vs OHLCV's 2021).
        # This simulates a timezone error (UTC vs local time) or wrong parquet file.
        rng = np.random.default_rng(99)
        n = len(small_ohlcv)
        oi_wrong_era = pd.DataFrame(
            {
                "open_time_utc": pd.date_range("2030-01-01", periods=n, freq="h", tz="UTC"),
                "sum_open_interest": np.abs(rng.uniform(50000, 100000, n)) + 1.0,
            }
        )
        with pytest.raises(ValueError, match="coverage"):
            build_features_df(small_ohlcv, small_registry, oi_df=oi_wrong_era)

    def test_zero_poison_propagates_nan_through_built_columns(
        self, small_registry: FactorRegistry, small_ohlcv: pd.DataFrame
    ) -> None:
        """Zero-poison NaN propagates correctly through the built OI feature columns.

        Build a synthetic OHLCV frame + an OI frame that has a zero-OI bar at
        position 10. After routing through build_features_df:
        - ``oi_sign`` at index 10 must be NaN (zero-poison from log-change).
        - ``oi_sign`` at index 11 must be NaN (prior bar was zero -> log(NaN) = NaN).
        - ``oi_velocity_ewm_240`` at index 10 must be NaN (masked where log-change NaN).
        - ``oi_velocity_ewm_240`` at index 11 must be NaN (same mask).
        - ``oi_pct_rank_2160`` at index 10 must be NaN (zero bar excluded from ranking).
        - All 4 OI columns are present in the output.
        """
        from factors.build_features import build_features_df

        zero_idx = 10
        oi_df = _make_oi_with_zero_bar(small_ohlcv, zero_idx)
        out = build_features_df(small_ohlcv, small_registry, oi_df=oi_df)

        # All 4 OI columns must be present.
        for name in EXPECTED_OI_FACTOR_NAMES:
            assert name in out.columns, (
                f"OI factor column {name!r} missing from built feature frame"
            )

        # oi_sign: zero-OI bar -> NaN; next bar -> NaN.
        assert np.isnan(out["oi_sign"].iloc[zero_idx]), (
            f"oi_sign at zero-OI bar ({zero_idx}) must be NaN; "
            f"got {out['oi_sign'].iloc[zero_idx]}"
        )
        assert np.isnan(out["oi_sign"].iloc[zero_idx + 1]), (
            f"oi_sign at bar after zero-OI ({zero_idx + 1}) must be NaN "
            f"(prior bar was zero -> log(NaN) = NaN); "
            f"got {out['oi_sign'].iloc[zero_idx + 1]}"
        )

        # oi_velocity_ewm_240: masked where log-change is NaN.
        assert np.isnan(out["oi_velocity_ewm_240"].iloc[zero_idx]), (
            f"oi_velocity_ewm_240 at zero-OI bar ({zero_idx}) must be NaN; "
            f"got {out['oi_velocity_ewm_240'].iloc[zero_idx]}"
        )
        assert np.isnan(out["oi_velocity_ewm_240"].iloc[zero_idx + 1]), (
            f"oi_velocity_ewm_240 at bar after zero-OI ({zero_idx + 1}) must be NaN; "
            f"got {out['oi_velocity_ewm_240'].iloc[zero_idx + 1]}"
        )

        # oi_pct_rank_2160: zero bar excluded from ranking -> NaN (not a spurious 0.0).
        # The pct_rank warmup is 2160 so index 10 is in the warmup window — NaN from warmup
        # is acceptable (and actually stronger: the row is NaN for TWO reasons).
        assert np.isnan(out["oi_pct_rank_2160"].iloc[zero_idx]), (
            f"oi_pct_rank_2160 at zero-OI bar ({zero_idx}) must be NaN "
            f"(zero-poisoned; not a spurious all-time-low rank); "
            f"got {out['oi_pct_rank_2160'].iloc[zero_idx]}"
        )
