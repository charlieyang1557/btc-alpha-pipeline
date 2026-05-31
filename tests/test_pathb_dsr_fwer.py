# tests/test_pathb_dsr_fwer.py
"""Step 5 DSR-FWER: per-candidate evaluate_candidate loop; survivors = pass_B True."""
from __future__ import annotations

import pytest

import backtest.pathb_dsr_fwer as fwer
from backtest.tier6_dsr import CandidateMoments


def _moments(hh: str, sr: float, T: int = 2000) -> CandidateMoments:
    return CandidateMoments(
        hypothesis_hash=hh, name=hh, theme="t",
        sr_per_bar=sr, gamma3=0.0, gamma4=3.0, T=T, trades=50,
    )


def test_pathb_n_star_default_is_3():
    assert fwer.PATHB_N_STAR == 3


def test_dsr_rows_is_per_candidate_loop_over_evaluate_candidate():
    cands = [_moments("a", 0.0), _moments("b", 0.5)]
    rows = fwer._dsr_rows(cands, n_star=fwer.PATHB_N_STAR)
    assert len(rows) == 2
    # Each row carries the n_star used (evaluate_candidate stamps it).
    assert all(r["n_star"] == fwer.PATHB_N_STAR for r in rows)
    assert all("pass_B" in r for r in rows)


def test_survivors_are_rows_with_pass_B_true():
    # A tiny SR over a huge T forces pass_B True; SR=0 forces pass_B False.
    cands = [_moments("loser", 0.0), _moments("winner", 5.0, T=5000)]
    result = fwer.run_dsr_fwer(cands, n_star=fwer.PATHB_N_STAR)
    survivors = result["survivors"]
    assert all(r["pass_B"] is True for r in survivors)
    assert "loser" not in [r["hypothesis_hash"] for r in survivors]
    assert result["n_candidates"] == 2


def test_does_not_route_through_evaluate_cohort(monkeypatch):
    # Guard: evaluate_cohort hard-requires 18/21; Path B must NOT call it.
    import backtest.tier6_dsr as t6

    def boom(*a, **k):
        raise AssertionError("evaluate_cohort must NOT be called by Path B FWER")

    monkeypatch.setattr(t6, "evaluate_cohort", boom)
    fwer.run_dsr_fwer([_moments("a", 0.1)], n_star=fwer.PATHB_N_STAR)
