# tests/test_patha_marginal.py
"""Path A fenced funding-marginal-contribution diagnostic tests (Task C6).

funding_marginal(hyp_id, gated_equity, baseline_equity) computes the net-of-cost
Sharpe delta (funding-gated minus no-funding baseline) on identical bars. It is
FENCED: diagnostic-only, never feeds N* or promotion (promotion_affecting=False,
in_n_star=False). The baseline is the SAME strategy WITHOUT the funding gate
(H2/H3 = price-trend-only; H1 = always-long).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.patha_marginal_diagnostic import funding_marginal


def test_marginal_is_fenced_diagnostic():
    # identical-bar equity curves; the funding-gated variant underperforms the
    # no-funding baseline here (the fencing lives in computing both Sharpes on the
    # SAME bars).
    gated = np.array([1.0, 1.01, 1.00, 1.02])
    baseline = np.array([1.0, 1.02, 1.03, 1.05])
    out = funding_marginal("H2", gated_equity=gated, baseline_equity=baseline)
    assert out["funding_marginal_sharpe"] < 0  # funding hurt here
    assert out["promotion_affecting"] is False and out["in_n_star"] is False


def test_marginal_positive_when_gated_beats_baseline():
    gated = np.array([1.0, 1.03, 1.05, 1.08])
    baseline = np.array([1.0, 1.0, 1.0, 1.0])  # flat baseline -> 0 Sharpe
    out = funding_marginal("H1", gated_equity=gated, baseline_equity=baseline)
    assert out["funding_marginal_sharpe"] > 0


def test_marginal_records_both_sharpes_and_hyp_id():
    gated = np.array([1.0, 1.01, 1.02, 1.03])
    baseline = np.array([1.0, 1.005, 1.01, 1.015])
    out = funding_marginal("H3", gated_equity=gated, baseline_equity=baseline)
    assert out["hyp_id"] == "H3"
    assert "gated_sharpe" in out and "baseline_sharpe" in out
    assert out["funding_marginal_sharpe"] == pytest.approx(
        out["gated_sharpe"] - out["baseline_sharpe"]
    )


def test_marginal_requires_identical_bar_count():
    with pytest.raises(ValueError, match="identical"):
        funding_marginal("H2", gated_equity=np.array([1.0, 1.1]),
                         baseline_equity=np.array([1.0, 1.1, 1.2]))


def test_marginal_rejects_same_length_misaligned_series_index():
    # FIX 4: two SAME-LENGTH Series on DIFFERENT timestamps must be rejected — the
    # marginal is only meaningful when both curves cover the IDENTICAL bars. The
    # bare np.asarray path would silently drop the index and pass these as "same
    # bars"; a DatetimeIndex mismatch must raise.
    idx_a = pd.date_range("2026-01-01", periods=4, freq="h", tz="UTC")
    idx_b = pd.date_range("2026-01-01 01:00", periods=4, freq="h", tz="UTC")  # shifted
    gated = pd.Series([1.0, 1.01, 1.02, 1.03], index=idx_a)
    baseline = pd.Series([1.0, 1.005, 1.01, 1.015], index=idx_b)
    with pytest.raises(ValueError, match="(?i)index|align|identical bars"):
        funding_marginal("H2", gated_equity=gated, baseline_equity=baseline)


def test_marginal_accepts_aligned_series_index():
    # Same length AND identical DatetimeIndex -> accepted (the legitimate path).
    idx = pd.date_range("2026-01-01", periods=4, freq="h", tz="UTC")
    gated = pd.Series([1.0, 1.01, 1.00, 1.02], index=idx)
    baseline = pd.Series([1.0, 1.02, 1.03, 1.05], index=idx)
    out = funding_marginal("H2", gated_equity=gated, baseline_equity=baseline)
    assert out["funding_marginal_sharpe"] < 0
    assert out["promotion_affecting"] is False and out["in_n_star"] is False


def test_fenced_flags_are_always_false():
    # The fence is structural: no input can flip promotion_affecting / in_n_star.
    for hyp in ("H1", "H2", "H3"):
        out = funding_marginal(hyp, gated_equity=np.array([1.0, 2.0, 3.0]),
                               baseline_equity=np.array([1.0, 1.0, 1.0]))
        assert out["promotion_affecting"] is False
        assert out["in_n_star"] is False
