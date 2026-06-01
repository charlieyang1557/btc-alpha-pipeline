# tests/test_pathc_marginal.py
"""Path C fenced dual-orthogonalization diagnostic tests (Task C6).

Two diagnostics are fenced as DIAGNOSTIC-ONLY (never in N*, never promotion-
affecting):
  D1 (vs momentum): basis_marginal_d1(hyp_id, gated_equity, baseline_equity)
     — Sharpe delta (basis-gated minus the identical no-basis baseline on the
     SAME bars). Mirrors patha_marginal_diagnostic.funding_marginal, retargeted.
  D2 (vs funding): basis_marginal_d2(hyp_id, basis_gated_equity, funding_gated_equity)
     — Sharpe delta (basis-gated minus the Path-A funding-gated strategy on
     identical bars). Measures whether higher-frequency basis adds over the 8h
     funding it is derived from.

redundancy_read(d2_agrees, d1_noninert) -> str:
  Pinned inference rule from LOCK Pre-registration 3 / Pre-registration 4 §9
  "Finding D" conjunction:
    "redundancy_confirmed" iff d2_agrees AND d1_noninert
    "vacuous"              iff d2_agrees AND NOT d1_noninert   (vacuous agreement)
    "basis_adds_signal"    iff NOT d2_agrees AND d1_noninert   (D2-disagree branch)
    "vacuous"              iff NOT d2_agrees AND NOT d1_noninert (both inert)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.pathc_marginal_diagnostic import (
    basis_marginal_d1,
    basis_marginal_d2,
    redundancy_read,
)


# ---------------------------------------------------------------------------
# D1 — vs-momentum baseline diagnostic
# ---------------------------------------------------------------------------


def test_d1_is_fenced_diagnostic():
    """D1: fenced flags always False, marginal sign correct (gated under-performs)."""
    gated = np.array([1.0, 1.01, 1.00, 1.02])
    baseline = np.array([1.0, 1.02, 1.03, 1.05])
    out = basis_marginal_d1("H2", gated_equity=gated, baseline_equity=baseline)
    assert out["d1_marginal_sharpe"] < 0          # gated lost relative to baseline
    assert out["promotion_affecting"] is False
    assert out["in_n_star"] is False


def test_d1_positive_when_gated_beats_baseline():
    """D1: positive marginal when gated outperforms."""
    gated = np.array([1.0, 1.03, 1.05, 1.08])
    baseline = np.array([1.0, 1.0, 1.0, 1.0])    # flat baseline -> 0 Sharpe
    out = basis_marginal_d1("H1", gated_equity=gated, baseline_equity=baseline)
    assert out["d1_marginal_sharpe"] > 0


def test_d1_records_both_sharpes_and_hyp_id():
    """D1: output contains hyp_id, gated_sharpe, baseline_sharpe, d1_marginal_sharpe."""
    gated = np.array([1.0, 1.01, 1.02, 1.03])
    baseline = np.array([1.0, 1.005, 1.01, 1.015])
    out = basis_marginal_d1("H3", gated_equity=gated, baseline_equity=baseline)
    assert out["hyp_id"] == "H3"
    assert "gated_sharpe" in out and "baseline_sharpe" in out
    assert out["d1_marginal_sharpe"] == pytest.approx(
        out["gated_sharpe"] - out["baseline_sharpe"]
    )


def test_d1_requires_identical_bar_count():
    """D1: mismatched equity curve lengths raise ValueError."""
    with pytest.raises(ValueError, match="identical"):
        basis_marginal_d1("H2", gated_equity=np.array([1.0, 1.1]),
                          baseline_equity=np.array([1.0, 1.1, 1.2]))


def test_d1_rejects_same_length_misaligned_series_index():
    """D1: same-length Series on DIFFERENT timestamps are rejected."""
    idx_a = pd.date_range("2026-01-01", periods=4, freq="h", tz="UTC")
    idx_b = pd.date_range("2026-01-01 01:00", periods=4, freq="h", tz="UTC")
    gated = pd.Series([1.0, 1.01, 1.02, 1.03], index=idx_a)
    baseline = pd.Series([1.0, 1.005, 1.01, 1.015], index=idx_b)
    with pytest.raises(ValueError, match="(?i)index|align|identical bars"):
        basis_marginal_d1("H2", gated_equity=gated, baseline_equity=baseline)


def test_d1_accepts_aligned_series_index():
    """D1: same-length Series on IDENTICAL timestamps are accepted."""
    idx = pd.date_range("2026-01-01", periods=4, freq="h", tz="UTC")
    gated = pd.Series([1.0, 1.01, 1.00, 1.02], index=idx)
    baseline = pd.Series([1.0, 1.02, 1.03, 1.05], index=idx)
    out = basis_marginal_d1("H2", gated_equity=gated, baseline_equity=baseline)
    assert out["d1_marginal_sharpe"] < 0
    assert out["promotion_affecting"] is False and out["in_n_star"] is False


def test_d1_fenced_flags_are_always_false():
    """D1: no input can flip the fence (structural constants)."""
    for hyp in ("H1", "H2", "H3"):
        out = basis_marginal_d1(hyp, gated_equity=np.array([1.0, 2.0, 3.0]),
                                baseline_equity=np.array([1.0, 1.0, 1.0]))
        assert out["promotion_affecting"] is False
        assert out["in_n_star"] is False


# ---------------------------------------------------------------------------
# D2 — vs-funding baseline diagnostic (NET-NEW Path C element)
# ---------------------------------------------------------------------------


def test_d2_is_fenced_diagnostic():
    """D2: fenced flags always False, marginal sign correct (basis under-performs funding)."""
    basis_gated = np.array([1.0, 1.01, 1.00, 1.02])
    funding_gated = np.array([1.0, 1.02, 1.03, 1.05])
    out = basis_marginal_d2("H2", basis_gated_equity=basis_gated,
                             funding_gated_equity=funding_gated)
    assert out["d2_marginal_sharpe"] < 0          # basis loses vs funding here
    assert out["promotion_affecting"] is False
    assert out["in_n_star"] is False


def test_d2_positive_when_basis_beats_funding():
    """D2: positive marginal when basis-gated outperforms funding-gated."""
    basis_gated = np.array([1.0, 1.03, 1.05, 1.08])
    funding_gated = np.array([1.0, 1.0, 1.0, 1.0])
    out = basis_marginal_d2("H1", basis_gated_equity=basis_gated,
                             funding_gated_equity=funding_gated)
    assert out["d2_marginal_sharpe"] > 0


def test_d2_records_both_sharpes_and_hyp_id():
    """D2: output contains hyp_id, basis_sharpe, funding_sharpe, d2_marginal_sharpe."""
    basis_gated = np.array([1.0, 1.01, 1.02, 1.03])
    funding_gated = np.array([1.0, 1.005, 1.01, 1.015])
    out = basis_marginal_d2("H3", basis_gated_equity=basis_gated,
                             funding_gated_equity=funding_gated)
    assert out["hyp_id"] == "H3"
    assert "basis_sharpe" in out and "funding_sharpe" in out
    assert out["d2_marginal_sharpe"] == pytest.approx(
        out["basis_sharpe"] - out["funding_sharpe"]
    )


def test_d2_requires_identical_bar_count():
    """D2: mismatched equity curve lengths raise ValueError."""
    with pytest.raises(ValueError, match="identical"):
        basis_marginal_d2("H2", basis_gated_equity=np.array([1.0, 1.1]),
                           funding_gated_equity=np.array([1.0, 1.1, 1.2]))


def test_d2_rejects_same_length_misaligned_series_index():
    """D2: same-length Series on DIFFERENT timestamps are rejected."""
    idx_a = pd.date_range("2026-01-01", periods=4, freq="h", tz="UTC")
    idx_b = pd.date_range("2026-01-01 01:00", periods=4, freq="h", tz="UTC")
    basis_gated = pd.Series([1.0, 1.01, 1.02, 1.03], index=idx_a)
    funding_gated = pd.Series([1.0, 1.005, 1.01, 1.015], index=idx_b)
    with pytest.raises(ValueError, match="(?i)index|align|identical bars"):
        basis_marginal_d2("H2", basis_gated_equity=basis_gated,
                           funding_gated_equity=funding_gated)


def test_d2_fenced_flags_are_always_false():
    """D2: no input can flip the fence (structural constants)."""
    for hyp in ("H1", "H2", "H3"):
        out = basis_marginal_d2(hyp, basis_gated_equity=np.array([1.0, 2.0, 3.0]),
                                funding_gated_equity=np.array([1.0, 1.0, 1.0]))
        assert out["promotion_affecting"] is False
        assert out["in_n_star"] is False


# ---------------------------------------------------------------------------
# redundancy_read — pinned 3-branch inference rule (Pre-reg 3 / §9 Finding D)
# ---------------------------------------------------------------------------


def test_redundancy_read_conjunction():
    """The 3 named outcomes of the pinned inference rule (+ 4th vacuous combo)."""
    # (True, True) -> "redundancy_confirmed": D2 agrees AND D1 non-inert
    assert redundancy_read(d2_agrees=True, d1_noninert=True) == "redundancy_confirmed"
    # (True, False) -> "vacuous": agreement is vacuous when D1 is inert
    assert redundancy_read(d2_agrees=True, d1_noninert=False) == "vacuous"
    # (False, True) -> "basis_adds_signal": D2 disagrees + D1 non-inert
    assert redundancy_read(d2_agrees=False, d1_noninert=True) == "basis_adds_signal"
    # (False, False) -> "vacuous": both inert, inconclusive
    assert redundancy_read(d2_agrees=False, d1_noninert=False) == "vacuous"


# ---------------------------------------------------------------------------
# Deliverable (A): no-basis baseline builders compile
# ---------------------------------------------------------------------------


def test_pathc_no_basis_baselines_compile():
    """The 3 no-basis baseline DSLs compile via the REAL DSL compiler."""
    from backtest.pathc_eval_gauntlet import build_all_baselines
    from strategies.dsl_compiler import compile_dsl_to_strategy

    baselines = build_all_baselines()
    assert set(baselines) == {"H1", "H2", "H3"}
    for hyp_id, dsl in baselines.items():
        cls = compile_dsl_to_strategy(dsl, write_manifest=False)
        assert cls is not None, f"{hyp_id} baseline failed to compile"
