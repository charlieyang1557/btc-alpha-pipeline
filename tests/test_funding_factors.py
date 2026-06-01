"""Tests for Path A funding-rate factors (Phase B, Tasks B1-B5).

The funding factors are computed on the 8h settlement series (causal, rolling
over settlement units). They are carried onto the 1h bar grid downstream by
``factors.funding_align.carry_funding_to_bars`` (Task B4). All factors are
top-level named callables, rolling/causal only (must pass the G1-G4 leakage
guards). All UTC. Mirrors the OHLCV factor test conventions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from factors.funding import (
    funding_ewm_30,
    funding_ewm_30_pctrank_270,
    funding_ewm_60,
    funding_pct_rank_270,
    funding_sign,
)
from factors.registry import _assert_no_future_ops


def _funding_df(values) -> pd.DataFrame:
    """Wrap a funding-rate sequence in the canonical funding factor input frame."""
    return pd.DataFrame({"funding_rate": pd.Series(values, dtype="float64")})


def _funding_compute_v1(df: pd.DataFrame) -> pd.Series:
    """Funding compute fn v1 (module-level for the feature_version test).

    Inputs: funding_rate. Warmup: 0. Output dtype: float64. Null policy: none.
    """
    return df["funding_rate"].ewm(span=30, adjust=False).mean()


def _funding_compute_v2(df: pd.DataFrame) -> pd.Series:
    """Funding compute fn v2 — same shape, different span (must bump the hash).

    Inputs: funding_rate. Warmup: 0. Output dtype: float64. Null policy: none.
    """
    return df["funding_rate"].ewm(span=31, adjust=False).mean()


# ---------------------------------------------------------------------------
# Task B1: funding_sign
# ---------------------------------------------------------------------------


def test_funding_sign():
    s = pd.Series([0.0002, -0.0001, 0.0, 0.00005])
    out = funding_sign(pd.DataFrame({"funding_rate": s}))
    assert out.tolist() == [1.0, -1.0, 0.0, 1.0]


# ---------------------------------------------------------------------------
# Task B2: funding_ewm_30 / funding_ewm_60
# ---------------------------------------------------------------------------


def test_funding_ewm_30_matches_unadjusted_ewm():
    rng = np.random.default_rng(11)
    s = pd.Series(rng.normal(0, 1e-4, 200), dtype="float64")
    out = funding_ewm_30(_funding_df(s))
    expected = s.ewm(span=30, adjust=False).mean()
    pd.testing.assert_series_equal(out, expected, check_names=False)


def test_funding_ewm_60_matches_unadjusted_ewm():
    rng = np.random.default_rng(12)
    s = pd.Series(rng.normal(0, 1e-4, 200), dtype="float64")
    out = funding_ewm_60(_funding_df(s))
    expected = s.ewm(span=60, adjust=False).mean()
    pd.testing.assert_series_equal(out, expected, check_names=False)


def test_funding_ewm_uses_adjust_false():
    # adjust=False and adjust=True diverge on a non-constant series; assert the
    # factor uses the unadjusted (classic recursive) form, not the adjusted one.
    s = pd.Series([1e-4, -2e-4, 3e-4, -1e-4, 5e-5], dtype="float64")
    out = funding_ewm_30(_funding_df(s))
    adjusted = s.ewm(span=30, adjust=True).mean()
    # The two forms agree at index 0 but must differ thereafter.
    assert not np.allclose(out.to_numpy(), adjusted.to_numpy())


def test_funding_ewm_is_causal_delete_future_invariant():
    # Value at settlement N must be independent of settlements > N: truncating
    # the future leaves earlier values bit-identical.
    rng = np.random.default_rng(13)
    s = pd.Series(rng.normal(0, 1e-4, 120), dtype="float64")
    full = funding_ewm_30(_funding_df(s))
    trunc = funding_ewm_30(_funding_df(s.iloc[:80]))
    np.testing.assert_array_equal(trunc.to_numpy(), full.iloc[:80].to_numpy())


# ---------------------------------------------------------------------------
# Task B3: funding_pct_rank_270
# ---------------------------------------------------------------------------


def test_funding_pct_rank_causal_and_bounded():
    s = pd.Series(np.r_[np.zeros(299), [5.0]])  # 300 rows; last value is max of its window
    out = funding_pct_rank_270(_funding_df(s))
    assert out.iloc[-1] == 1.0
    assert out.iloc[:269].isna().all()  # warmup: indices 0..268 NaN (min_periods=270)
    assert not np.isnan(out.iloc[269])  # first valid value at index 269
    # causality: truncating future rows leaves earlier values unchanged
    trunc = funding_pct_rank_270(_funding_df(s.iloc[:280]))
    assert trunc.iloc[270] == out.iloc[270]


def test_funding_pct_rank_bounded_unit_interval():
    rng = np.random.default_rng(21)
    s = pd.Series(rng.normal(0, 1e-4, 400), dtype="float64")
    out = funding_pct_rank_270(_funding_df(s))
    post = out.iloc[269:]
    assert (post >= 0.0).all() and (post <= 1.0).all()


def test_funding_pct_rank_known_midpoint():
    # Final window = 270 values where the last is the 136th-smallest of 270:
    # 135 strictly-below + itself -> count 136 -> 136/270.
    window = list(range(269)) + [134.5]
    s = pd.Series([float(v) for v in window], dtype="float64")
    out = funding_pct_rank_270(_funding_df(s))
    # values 0..134 (135 of them) are < 134.5; itself counts (<=) -> 136/270.
    assert out.iloc[-1] == 136.0 / 270.0


def test_funding_pct_rank_is_g1_ast_safe():
    # CRITICAL: must NOT use bare .mean()/.std()/.sum() on a window (the G1 AST
    # scanner bans those). An explicit count loop is required.
    _assert_no_future_ops(funding_pct_rank_270, "funding_pct_rank_270")  # no raise


# ---------------------------------------------------------------------------
# Task C2: funding_ewm_30_pctrank_270 (causal rolling-270 percentile of funding_ewm_30)
# ---------------------------------------------------------------------------


def test_funding_ewm_30_pctrank_causal_and_bounded():
    # The factor first computes funding_ewm_30 (causal EWM, non-NaN from row 0),
    # then a causal rolling-270 percentile of THAT series. With a constant input
    # series the ewm is constant, so the percentile is 1.0 at every full window.
    s = pd.Series(np.r_[np.zeros(299), [5.0]])  # 300 rows
    out = funding_ewm_30_pctrank_270(_funding_df(s))
    # The ewm of the spike at the end is still the largest value of its window.
    assert out.iloc[-1] == 1.0
    assert out.iloc[:269].isna().all()  # warmup: 270-settlement percentile window
    assert not np.isnan(out.iloc[269])  # first valid value at index 269
    # bounded [0, 1] post-warmup
    post = out.iloc[269:]
    assert (post >= 0.0).all() and (post <= 1.0).all()


def test_funding_ewm_30_pctrank_is_delete_future_invariant():
    # Causality: value at row N independent of rows > N. Truncating the future
    # leaves earlier valid values bit-identical. (Both the ewm and the rolling
    # percentile are strictly backward-looking.)
    rng = np.random.default_rng(51)
    s = pd.Series(rng.normal(0, 1e-4, 360), dtype="float64")
    full = funding_ewm_30_pctrank_270(_funding_df(s))
    trunc = funding_ewm_30_pctrank_270(_funding_df(s.iloc[:330]))
    np.testing.assert_array_equal(
        trunc.iloc[269:].to_numpy(), full.iloc[269:330].to_numpy()
    )


def test_funding_ewm_30_pctrank_is_g1_ast_safe():
    # CRITICAL: must NOT use bare .mean()/.std()/.sum() on a window for the
    # percentile (the G1 AST scanner bans those). An explicit count loop is
    # required, same pattern as funding_pct_rank_270. (The inner funding_ewm_30
    # uses ewm(...).mean(), which IS a windowed reducer and is allowed.)
    _assert_no_future_ops(funding_ewm_30_pctrank_270, "funding_ewm_30_pctrank_270")  # no raise


# ---------------------------------------------------------------------------
# Task B5: registration + input_source routing + build integration
# ---------------------------------------------------------------------------

FUNDING_FACTORS = [
    "funding_ewm_30",
    "funding_ewm_30_pctrank_270",
    "funding_ewm_60",
    "funding_pct_rank_270",
    "funding_sign",
]

# FIX 3: Path C Phase B added 5 basis factors with input_source="basis" — exclude
# them from the ohlcv-default assertion so the test's intent (OHLCV factors keep
# the default) is preserved without false failures on the new non-OHLCV sources.
EXPECTED_BASIS_FACTORS = [
    "basis_sign",
    "basis_ewm_240",
    "basis_ewm_480",
    "basis_pct_rank_2160",
    "basis_ewm_240_pctrank_2160",
]


def _fresh_registry():
    from factors.registry import FactorRegistry, _bootstrap_core_factors

    reg = FactorRegistry()
    _bootstrap_core_factors(reg)
    return reg


def test_funding_factors_registered_with_funding_input_source():
    reg = _fresh_registry()
    names = set(reg.list_names())
    for f in FUNDING_FACTORS:
        assert f in names, f"funding factor {f!r} not registered"
        spec = reg.get(f)
        assert spec.input_source == "funding", (
            f"{f}: input_source must be 'funding' so the build routes it onto "
            f"the 8h settlement frame, not the OHLCV frame"
        )
        assert spec.null_policy == "nan_before_warmup_only"
        assert spec.inputs == ["funding_rate"]


def test_ohlcv_factors_keep_default_input_source():
    reg = _fresh_registry()
    # Every factor that is neither a funding factor nor a basis factor must keep
    # the default "ohlcv" input_source. Basis factors have input_source="basis"
    # (Path C Phase B Task B5) — they are explicitly excluded here so that adding
    # new non-OHLCV sources does not require re-opening this test each time.
    non_ohlcv = set(FUNDING_FACTORS) | set(EXPECTED_BASIS_FACTORS)
    for name in reg.list_names():
        if name not in non_ohlcv:
            assert reg.get(name).input_source == "ohlcv", (
                f"{name}: expected input_source='ohlcv' for non-funding non-basis factor"
            )


def test_funding_factor_warmups_declared():
    reg = _fresh_registry()
    # warmup_bars are declared in 8h-SETTLEMENT units (the frame the factors are
    # computed on); these are UNCHANGED by the FIX 1 bar-equivalent conversion —
    # the conversion lives in input_period_bars, not warmup_bars.
    assert reg.get("funding_sign").warmup_bars == 0
    assert reg.get("funding_ewm_30").warmup_bars == 30
    assert reg.get("funding_ewm_60").warmup_bars == 60
    assert reg.get("funding_pct_rank_270").warmup_bars == 270
    assert reg.get("funding_ewm_30_pctrank_270").warmup_bars == 270


def test_funding_factor_input_period_bars_is_8():
    """FIX 1: funding factors carry 8h settlements onto the 1h grid, so each
    settlement of declared warmup spans 8 1h bars. input_period_bars=8 lets the
    compiler convert the settlement-unit warmup into a bar-equivalent warmup.
    OHLCV factors keep the default input_period_bars=1."""
    reg = _fresh_registry()
    for f in FUNDING_FACTORS:
        assert reg.get(f).input_period_bars == 8, (
            f"{f}: input_period_bars must be 8 (BTCUSDT 8h funding / 1h bars)"
        )
    for name in reg.list_names():
        if name not in FUNDING_FACTORS:
            assert reg.get(name).input_period_bars == 1, (
                f"{name}: OHLCV factor input_period_bars must default to 1"
            )


def test_funding_factors_pass_g1_ast_scan():
    reg = _fresh_registry()
    for f in FUNDING_FACTORS:
        spec = reg.get(f)
        _assert_no_future_ops(spec.compute, f)  # no raise


def test_input_period_bars_excluded_from_feature_version():
    """FIX 1: input_period_bars is a routing/warmup-unit concern (like
    input_source) — it MUST be excluded from canonical_metadata/feature_version.
    Two registries differing ONLY in input_period_bars hash identically."""
    from factors.registry import (
        FactorRegistry,
        FactorSpec,
        compute_feature_version,
    )

    r1 = FactorRegistry()
    r1.register(FactorSpec(
        name="x", category="funding", warmup_bars=0, inputs=["funding_rate"],
        output_dtype="float64", compute=_funding_compute_v1, docstring="d",
        input_source="funding", input_period_bars=1,
    ))
    r2 = FactorRegistry()
    r2.register(FactorSpec(
        name="x", category="funding", warmup_bars=0, inputs=["funding_rate"],
        output_dtype="float64", compute=_funding_compute_v1, docstring="d",
        input_source="funding", input_period_bars=8,
    ))
    assert compute_feature_version(r1) == compute_feature_version(r2)


def test_feature_version_changes_when_funding_compute_changes():
    # Editing a funding compute body must bump the feature_version hash.
    # Compute fns are module-level (the registry rejects nested/local callables
    # because inspect.getsource is unstable on them).
    from factors.registry import (
        FactorRegistry,
        FactorSpec,
        compute_feature_version,
    )

    r1 = FactorRegistry()
    r1.register(FactorSpec(
        name="x", category="funding", warmup_bars=0, inputs=["funding_rate"],
        output_dtype="float64", compute=_funding_compute_v1, docstring="d",
        input_source="funding",
    ))
    r2 = FactorRegistry()
    r2.register(FactorSpec(
        name="x", category="funding", warmup_bars=0, inputs=["funding_rate"],
        output_dtype="float64", compute=_funding_compute_v2, docstring="d",
        input_source="funding",
    ))
    assert compute_feature_version(r1) != compute_feature_version(r2)


def test_compute_all_ohlcv_default_excludes_funding():
    # The default compute_all path computes ONLY ohlcv-source factors, so it
    # never tries to read funding_rate from an OHLCV frame.
    from tests.test_factors import EXPECTED_OHLCV_FACTORS, _make_synthetic

    reg = _fresh_registry()
    ohlcv = _make_synthetic(300)
    out = reg.compute_all(ohlcv)  # default input_source="ohlcv"
    assert set(out.columns) == set(EXPECTED_OHLCV_FACTORS)
    for f in FUNDING_FACTORS:
        assert f not in out.columns


def test_compute_all_funding_source_computes_funding_factors():
    reg = _fresh_registry()
    # 8h settlement frame.
    times = pd.date_range("2020-01-01", periods=400, freq="8h", tz="UTC")
    rng = np.random.default_rng(31)
    funding = pd.DataFrame({
        "open_time_utc": times,
        "funding_rate": rng.normal(0, 1e-4, 400),
    })
    out = reg.compute_all(funding, input_source="funding")
    assert set(out.columns) == set(FUNDING_FACTORS)
    # Post-warmup (max funding warmup = 270) must be free of NaN.
    assert not out.iloc[270:].isna().any().any()


def test_build_integration_carries_funding_onto_bars():
    # The build routes funding factors onto the 8h frame then carries them onto
    # the 1h feature frame; the resulting frame has the funding columns.
    from factors.build_features import build_features_df

    reg = _fresh_registry()
    # Small synthetic OHLCV + funding frames spanning the same window.
    n_bars = 2400
    bar_times = pd.date_range("2020-01-01", periods=n_bars, freq="1h", tz="UTC")
    rng = np.random.default_rng(41)
    close = 30000.0 + np.cumsum(rng.normal(0, 50, n_bars))
    raw = pd.DataFrame({
        "open_time_utc": bar_times,
        "open": close - rng.normal(0, 20, n_bars),
        "high": close + np.abs(rng.normal(0, 30, n_bars)),
        "low": close - np.abs(rng.normal(0, 30, n_bars)),
        "close": close,
        "volume": np.abs(rng.normal(1000, 200, n_bars)),
    })
    n_settle = n_bars // 8
    funding = pd.DataFrame({
        "open_time_utc": pd.date_range("2020-01-01", periods=n_settle, freq="8h", tz="UTC"),
        "funding_rate": rng.normal(0, 1e-4, n_settle),
    })

    out = build_features_df(raw, reg, funding_df=funding)
    # All funding factors are present as carried columns on the 1h grid.
    for f in FUNDING_FACTORS:
        assert f in out.columns
    assert len(out) == n_bars
    # The carried funding columns are non-NaN well past warmup (270 settlements
    # = 2160 bars); check the final bars.
    assert not out[FUNDING_FACTORS].iloc[-1].isna().any()
