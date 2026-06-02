# tests/test_pathd_marginal.py
"""Path D fenced D1-only diagnostic + contamination correlations tests (Task C6).

PATH C→D KEY DIVERGENCE: D2 machinery is DROPPED (OI is an independent axis;
no derived-from relation to funding/basis; Path C's D2-vs-funding evaporates).

Fenced diagnostic (DIAGNOSTIC-ONLY; never in N*, never promotion-affecting):
  D1 (vs no-OI baseline): oi_marginal_d1(hyp_id, gated_equity, baseline_equity)
     — Sharpe delta (OI-gated minus the no-OI baseline on the SAME bars).

NET-NEW for Path D: contamination_correlations(df) — Pearson AND Spearman of
  oi_velocity_ewm_240 vs {return_1h, abs_return_1h, realized_vol_24h,
  cdf_realized_vol_720}. Measured-only; never a control.

A1 regression guard (test_d2_machinery_absent): ensures D2 identifiers are absent
from backtest.pathd_marginal_diagnostic.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import backtest.pathd_marginal_diagnostic as m
from backtest.pathd_marginal_diagnostic import (
    oi_marginal_d1,
    d1_noninert,
    D1_NONINERT_THRESHOLD,
    contamination_correlations,
)


# ---------------------------------------------------------------------------
# A1 regression guard — D2 machinery must be ABSENT
# ---------------------------------------------------------------------------


def test_d2_machinery_absent():
    """The D2 identifiers have been intentionally dropped for Path D (independent axis)."""
    gone_names = (
        "oi_marginal_d2",
        "basis_marginal_d2",
        "redundancy_read",
        "d2_agrees",
        "D2_AGREES_TOLERANCE",
    )
    for gone in gone_names:
        assert not hasattr(m, gone), (
            f"Expected D2 machinery '{gone}' to be ABSENT from pathd_marginal_diagnostic "
            f"(OI is an independent axis; D2 has no role here)."
        )


# ---------------------------------------------------------------------------
# D1_NONINERT_THRESHOLD constant
# ---------------------------------------------------------------------------


def test_d1_threshold_value():
    assert D1_NONINERT_THRESHOLD == 0.10


def test_d1_noninert_above_threshold():
    assert d1_noninert(0.2) is True


def test_d1_noninert_below_threshold():
    assert d1_noninert(0.05) is False


def test_d1_noninert_at_boundary_is_inert():
    # Boundary is strict >; exactly 0.10 is inert.
    assert d1_noninert(0.10) is False
    assert d1_noninert(-0.10) is False


def test_d1_noninert_negative_above_abs_threshold():
    assert d1_noninert(-0.2) is True


# ---------------------------------------------------------------------------
# oi_marginal_d1 — fenced D1 diagnostic
# ---------------------------------------------------------------------------


def test_d1_is_fenced_diagnostic():
    """D1: fenced flags always False, marginal sign correct (gated under-performs)."""
    gated = np.array([1.0, 1.01, 1.00, 1.02])
    baseline = np.array([1.0, 1.02, 1.03, 1.05])
    out = oi_marginal_d1("H2", gated_equity=gated, baseline_equity=baseline)
    assert out["d1_marginal_sharpe"] < 0          # gated lost relative to baseline
    assert out["promotion_affecting"] is False
    assert out["in_n_star"] is False


def test_d1_negative_when_gated_underperforms_baseline():
    """Confirm signed direction: OI-gated that loses vs baseline → negative marginal."""
    gated = np.array([1.0, 1.01, 1.00, 1.02])
    baseline = np.array([1.0, 1.02, 1.03, 1.05])
    out = oi_marginal_d1("H1", gated_equity=gated, baseline_equity=baseline)
    assert out["d1_marginal_sharpe"] < 0


def test_d1_positive_when_gated_beats_baseline():
    """D1: positive marginal when OI-gated outperforms."""
    gated = np.array([1.0, 1.03, 1.05, 1.08])
    baseline = np.array([1.0, 1.0, 1.0, 1.0])   # flat baseline -> 0 Sharpe
    out = oi_marginal_d1("H1", gated_equity=gated, baseline_equity=baseline)
    assert out["d1_marginal_sharpe"] > 0


def test_d1_records_both_sharpes_and_hyp_id():
    """D1: output contains hyp_id, gated_sharpe, baseline_sharpe, d1_marginal_sharpe."""
    gated = np.array([1.0, 1.01, 1.02, 1.03])
    baseline = np.array([1.0, 1.005, 1.01, 1.015])
    out = oi_marginal_d1("H3", gated_equity=gated, baseline_equity=baseline)
    assert out["hyp_id"] == "H3"
    assert "gated_sharpe" in out and "baseline_sharpe" in out
    assert out["d1_marginal_sharpe"] == pytest.approx(
        out["gated_sharpe"] - out["baseline_sharpe"]
    )


def test_d1_fenced_flags_are_always_false():
    """D1: no input can flip the fence (structural constants)."""
    for hyp in ("H1", "H2", "H3"):
        out = oi_marginal_d1(hyp, gated_equity=np.array([1.0, 2.0, 3.0]),
                             baseline_equity=np.array([1.0, 1.0, 1.0]))
        assert out["promotion_affecting"] is False
        assert out["in_n_star"] is False


def test_d1_requires_identical_bar_count():
    """D1: mismatched equity curve lengths raise ValueError."""
    with pytest.raises(ValueError, match="identical"):
        oi_marginal_d1("H2", gated_equity=np.array([1.0, 1.1]),
                       baseline_equity=np.array([1.0, 1.1, 1.2]))


def test_d1_rejects_same_length_misaligned_series_index():
    """D1: same-length Series on DIFFERENT timestamps are rejected."""
    idx_a = pd.date_range("2026-01-01", periods=4, freq="h", tz="UTC")
    idx_b = pd.date_range("2026-01-01 01:00", periods=4, freq="h", tz="UTC")
    gated = pd.Series([1.0, 1.01, 1.02, 1.03], index=idx_a)
    baseline = pd.Series([1.0, 1.005, 1.01, 1.015], index=idx_b)
    with pytest.raises(ValueError, match="(?i)index|align|identical bars"):
        oi_marginal_d1("H2", gated_equity=gated, baseline_equity=baseline)


def test_d1_accepts_aligned_series_index():
    """D1: same-length Series on IDENTICAL timestamps are accepted."""
    idx = pd.date_range("2026-01-01", periods=4, freq="h", tz="UTC")
    gated = pd.Series([1.0, 1.01, 1.00, 1.02], index=idx)
    baseline = pd.Series([1.0, 1.02, 1.03, 1.05], index=idx)
    out = oi_marginal_d1("H2", gated_equity=gated, baseline_equity=baseline)
    assert out["d1_marginal_sharpe"] < 0
    assert out["promotion_affecting"] is False and out["in_n_star"] is False


# ---------------------------------------------------------------------------
# contamination_correlations — NET-NEW fenced Pearson + Spearman set
# ---------------------------------------------------------------------------


def _make_df(n: int = 200, seed: int = 42, include_abs_return: bool = False) -> pd.DataFrame:
    """Synthetic aligned DataFrame with required columns for contamination_correlations."""
    rng = np.random.default_rng(seed)
    d: dict = {
        "oi_velocity_ewm_240": rng.normal(0, 1, n),
        "return_1h": rng.normal(0, 0.01, n),
        "realized_vol_24h": np.abs(rng.normal(0.01, 0.005, n)),
        "cdf_realized_vol_720": rng.uniform(0, 1, n),
    }
    if include_abs_return:
        d["abs_return_1h"] = np.abs(d["return_1h"])
    return pd.DataFrame(d)


def test_contamination_correlations_returns_four_series_each_stat():
    """Result must have pearson and spearman dicts with all 4 series names."""
    out = contamination_correlations(_make_df())
    expected_series = {"return_1h", "abs_return_1h", "realized_vol_24h", "cdf_realized_vol_720"}
    assert set(out["pearson"].keys()) == expected_series
    assert set(out["spearman"].keys()) == expected_series


def test_contamination_correlations_fenced_flags():
    """Result always carries promotion_affecting=False and in_n_star=False."""
    out = contamination_correlations(_make_df())
    assert out["promotion_affecting"] is False
    assert out["in_n_star"] is False


def test_contamination_correlations_values_are_floats_in_range():
    """Pearson/Spearman values are finite floats in [-1, 1]."""
    out = contamination_correlations(_make_df())
    for stat_dict in (out["pearson"], out["spearman"]):
        for name, val in stat_dict.items():
            assert isinstance(val, float), f"{name}: expected float, got {type(val)}"
            assert -1.0 <= val <= 1.0, f"{name}: {val} out of [-1, 1]"


def test_contamination_correlations_derives_abs_return_locally():
    """abs_return_1h is computed from return_1h when not present as a column."""
    df_without = _make_df(include_abs_return=False)
    df_with = _make_df(include_abs_return=True)
    out_without = contamination_correlations(df_without)
    out_with = contamination_correlations(df_with)
    # Both should produce finite correlations for abs_return_1h.
    assert np.isfinite(out_without["pearson"]["abs_return_1h"])
    assert np.isfinite(out_with["pearson"]["abs_return_1h"])
    # They must be equal since abs_return_1h = return_1h.abs() in both cases.
    assert out_without["pearson"]["abs_return_1h"] == pytest.approx(
        out_with["pearson"]["abs_return_1h"], abs=1e-10
    )


def test_contamination_correlations_high_pearson_on_correlated_data():
    """Sanity: oi_velocity_ewm_240 perfectly correlated with return_1h -> r ≈ 1."""
    n = 100
    x = np.linspace(0, 1, n)
    df = pd.DataFrame({
        "oi_velocity_ewm_240": x,
        "return_1h": x,           # perfectly correlated
        "realized_vol_24h": np.abs(x) + 0.001,
        "cdf_realized_vol_720": x,
    })
    out = contamination_correlations(df)
    assert out["pearson"]["return_1h"] == pytest.approx(1.0, abs=1e-9)
    assert out["spearman"]["return_1h"] == pytest.approx(1.0, abs=1e-9)


def test_contamination_correlations_nan_on_insufficient_data():
    """Returns np.nan when fewer than 2 non-NaN shared rows exist for a pair."""
    df = pd.DataFrame({
        "oi_velocity_ewm_240": [np.nan, np.nan, np.nan],
        "return_1h": [0.01, 0.02, 0.03],
        "realized_vol_24h": [0.01, 0.01, 0.01],
        "cdf_realized_vol_720": [0.5, 0.5, 0.5],
    })
    out = contamination_correlations(df)
    for name in ("return_1h", "abs_return_1h", "realized_vol_24h", "cdf_realized_vol_720"):
        assert np.isnan(out["pearson"][name]), f"{name} pearson should be nan"
        assert np.isnan(out["spearman"][name]), f"{name} spearman should be nan"
