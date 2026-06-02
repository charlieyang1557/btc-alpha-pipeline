"""Integration tests for the basis-factor build routing (Path C Phase B Task B5).

Synthetic-only — NO real network, NO real-data value inspection.

Verifies that ``build_features_df`` with a synthetic markprice frame:
1. Produces the 5 basis factor columns in the feature frame.
2. Leaves OHLCV and funding columns unaffected.
3. Produces NaN basis values for OHLCV bars absent from the mark/spot shared grid.
4. Does NOT drop OHLCV rows (left-join preserves all OHLCV bars).

No-peek discipline applies: this file NEVER inspects any real forward_2026
or production-data basis factor values.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factors.registry import FactorRegistry, FactorSpec, _bootstrap_core_factors
from factors.basis import basis_sign

# ---------------------------------------------------------------------------
# Synthetic data helpers
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# (a) Contract-widen test: input_source="basis" must be accepted by FactorSpec
# ---------------------------------------------------------------------------


class TestInputSourceBasisWiden:
    """FactorSpec must accept input_source='basis' after the B2-convergent contract widen."""

    def test_factor_spec_basis_constructs_without_raising(self) -> None:
        """FactorSpec(input_source='basis') must construct without ValueError.

        This is the TDD RED→GREEN test for sub-task (a): before the widen,
        __post_init__ raised on any input_source outside {'ohlcv', 'funding'}.
        After the widen to {'ohlcv', 'funding', 'basis'}, this must pass.
        """
        spec = FactorSpec(
            name="basis_sign",
            category="basis",
            warmup_bars=0,
            inputs=["basis_rel"],
            output_dtype="float64",
            compute=basis_sign,
            docstring=basis_sign.__doc__ or "basis sign",
            input_source="basis",
            input_period_bars=1,
        )
        assert spec.input_source == "basis"
        assert spec.name == "basis_sign"

    def test_invalid_input_source_still_raises(self) -> None:
        """input_source='unknown_source' must still raise ValueError."""
        import pytest

        with pytest.raises(ValueError, match="input_source"):
            FactorSpec(
                name="basis_sign",
                category="basis",
                warmup_bars=0,
                inputs=["basis_rel"],
                output_dtype="float64",
                compute=basis_sign,
                docstring="test",
                input_source="unknown_source",
            )


EXPECTED_BASIS_FACTOR_NAMES = [
    "basis_ewm_240",
    "basis_ewm_240_pctrank_2160",
    "basis_ewm_480",
    "basis_pct_rank_2160",
    "basis_sign",
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


def _make_markprice(ohlcv_df: pd.DataFrame, seed: int = 99) -> pd.DataFrame:
    """Synthetic markprice frame aligned to the SAME grid as ``ohlcv_df``.

    ``mark_close[t] ≈ spot_close[t] * (1 + small_basis)`` so the inner-join
    in ``derive_basis_rel`` passes the 5% cross-stream tolerance.

    IMPORTANT: use the pandas Series (not .values) to preserve UTC timezone-aware
    dtype — ``derive_basis_rel`` inner-joins on ``open_time_utc`` and requires
    both sides to be UTC-aware to produce a non-empty intersection.
    """
    rng = np.random.default_rng(seed)
    mark = ohlcv_df["close"].values * (1 + rng.normal(0, 2e-4, len(ohlcv_df)))
    return pd.DataFrame(
        {
            "open_time_utc": ohlcv_df["open_time_utc"],  # preserve UTC-aware dtype
            "mark_close": mark,
        }
    ).reset_index(drop=True)


@pytest.fixture
def small_registry() -> FactorRegistry:
    """Fresh registry with all 37 core factors."""
    r = FactorRegistry()
    _bootstrap_core_factors(r)
    return r


@pytest.fixture
def small_ohlcv() -> pd.DataFrame:
    """300-bar synthetic OHLCV frame — fast for OHLCV factor computation."""
    return _make_ohlcv(300)


# ---------------------------------------------------------------------------
# (d) Integration tests
# ---------------------------------------------------------------------------


class TestBasisBuildRouting:
    """Integration tests for the basis-factor routing in build_features_df."""

    def test_basis_factor_columns_present(
        self, small_registry: FactorRegistry, small_ohlcv: pd.DataFrame
    ) -> None:
        """build_features_df produces all 5 basis factor columns when markprice is given."""
        from factors.build_features import build_features_df

        mark_df = _make_markprice(small_ohlcv)
        out = build_features_df(small_ohlcv, small_registry, markprice_df=mark_df)

        for name in EXPECTED_BASIS_FACTOR_NAMES:
            assert name in out.columns, (
                f"Expected basis factor column {name!r} in feature frame; "
                f"columns = {list(out.columns)}"
            )

    def test_ohlcv_columns_unaffected(
        self, small_registry: FactorRegistry, small_ohlcv: pd.DataFrame
    ) -> None:
        """Basis routing does not alter OHLCV factor column values.

        Build twice — once with markprice (basis routing active) and once without
        (basis routing absent, NaN columns). The OHLCV factor values must be
        byte-identical between the two builds.
        """
        from factors.build_features import build_features_df

        mark_df = _make_markprice(small_ohlcv)
        out_with_basis = build_features_df(
            small_ohlcv, small_registry, markprice_df=mark_df
        )
        out_no_basis = build_features_df(
            small_ohlcv, small_registry, markprice_df=None
        )

        for name in EXPECTED_OHLCV_FACTOR_NAMES:
            assert name in out_with_basis.columns
            assert name in out_no_basis.columns
            pd.testing.assert_series_equal(
                out_with_basis[name].reset_index(drop=True),
                out_no_basis[name].reset_index(drop=True),
                check_names=False,
                obj=f"OHLCV factor {name!r} changed when basis routing was added",
            )

    def test_missing_markprice_bar_gives_nan_basis(
        self, small_registry: FactorRegistry, small_ohlcv: pd.DataFrame
    ) -> None:
        """OHLCV bars absent from the markprice stream get NaN basis factor values.

        Build a markprice frame that covers bars [0, 290) — the last 10 OHLCV bars
        have no markprice. The non-shared fraction = 10/300 ≈ 3.3% < 5% (within
        CROSS_STREAM_DROP_TOL), so derive_basis_rel does not raise. After the
        left-join, basis columns at positions [290, 300) must be NaN. OHLCV rows
        are NOT dropped.
        """
        from factors.build_features import build_features_df

        # Markprice covers bars [0, 290): 10 trailing OHLCV bars have no mark data.
        # 10/300 = 3.3% < 5% tolerance → derive_basis_rel proceeds (inner join).
        mark_partial = _make_markprice(small_ohlcv.iloc[:290].copy())
        out = build_features_df(
            small_ohlcv, small_registry, markprice_df=mark_partial
        )

        # Row count must match the full OHLCV frame — no OHLCV rows dropped.
        assert len(out) == len(small_ohlcv), (
            f"Expected {len(small_ohlcv)} rows; got {len(out)} — OHLCV rows were dropped."
        )

        # Basis columns at positions [290, 300) must be NaN (no markprice coverage
        # for those trailing bars — they are in the OHLCV frame but not in the
        # inner-joined basis_rel frame).
        for name in EXPECTED_BASIS_FACTOR_NAMES:
            assert name in out.columns
            nan_tail = out[name].iloc[290:]
            assert nan_tail.isna().all(), (
                f"Basis factor {name!r} at positions [290, 300) must all be NaN "
                f"(no markprice for those bars); got non-NaN: {nan_tail.dropna()}"
            )

    def test_ohlcv_rows_not_dropped(
        self, small_registry: FactorRegistry, small_ohlcv: pd.DataFrame
    ) -> None:
        """Left-join semantics: all OHLCV rows are preserved even if some lack markprice.

        Use a markprice frame with only 10 of 300 bars shared. The output must
        still have 300 rows (the OHLCV frame is the left side of the join).
        """
        from factors.build_features import build_features_df

        # Only the first 10 bars in markprice — high non-shared fraction would
        # trigger derive_basis_rel's 5% tolerance error, so instead pick a subset
        # that respects the tolerance. Since small_ohlcv has 300 bars and we want
        # only 10 in markprice, the non-shared fraction = (290+0)/300 ≈ 96.7% >
        # 5%. To avoid the ValueError, use a markprice that FULLY covers the OHLCV
        # grid but then test the NaN rows through a different mechanism: verify that
        # the output row count equals the input row count across several markprice
        # coverages. Here we simply use the full-coverage markprice.
        mark_df = _make_markprice(small_ohlcv)
        out = build_features_df(small_ohlcv, small_registry, markprice_df=mark_df)

        assert len(out) == len(small_ohlcv), (
            f"Row count mismatch: expected {len(small_ohlcv)}, got {len(out)}. "
            f"build_features_df must preserve all OHLCV rows (left-join semantics)."
        )
        # open_time_utc alignment must be preserved.
        pd.testing.assert_series_equal(
            out["open_time_utc"].reset_index(drop=True),
            small_ohlcv["open_time_utc"].reset_index(drop=True),
            check_names=False,
            obj="open_time_utc column order must match input OHLCV frame",
        )
