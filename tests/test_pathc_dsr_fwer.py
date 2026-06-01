# tests/test_pathc_dsr_fwer.py
"""Path C DSR-FWER: per-candidate evaluate_candidate loop; survivors = pass_B True.

Adapted from tests/test_patha_dsr_fwer.py. PATHC_N_STAR = 3 (= PATHA_N_STAR =
PATHB_N_STAR); the DSR math is REUSED from tier6 (evaluate_candidate, Form B,
frozen Z_PASS) — this module only loops it per basis candidate and selects
pass_B survivors.
"""
from __future__ import annotations

import backtest.pathc_dsr_fwer as fwer
from backtest.tier6_dsr import CandidateMoments


def _moments(hh: str, sr: float, T: int = 2000) -> CandidateMoments:
    return CandidateMoments(
        hypothesis_hash=hh, name=hh, theme="pathc",
        sr_per_bar=sr, gamma3=0.0, gamma4=3.0, T=T, trades=50,
    )


def test_pathc_n_star_default_is_3():
    assert fwer.PATHC_N_STAR == 3


def test_pathc_n_star_equals_patha_n_star():
    import backtest.patha_dsr_fwer as pa
    assert fwer.PATHC_N_STAR == pa.PATHA_N_STAR


def test_dsr_rows_is_per_candidate_loop_over_evaluate_candidate():
    cands = [_moments("a", 0.0), _moments("b", 0.5)]
    rows = fwer._dsr_rows(cands, n_star=fwer.PATHC_N_STAR)
    assert len(rows) == 2
    # Each row carries the n_star used (evaluate_candidate stamps it).
    assert all(r["n_star"] == fwer.PATHC_N_STAR for r in rows)
    assert all("pass_B" in r for r in rows)


def test_survivors_are_rows_with_pass_B_true():
    # A tiny SR over a huge T forces pass_B True; SR=0 forces pass_B False.
    cands = [_moments("loser", 0.0), _moments("winner", 5.0, T=5000)]
    result = fwer.run_dsr_fwer(cands, n_star=fwer.PATHC_N_STAR)
    survivors = result["survivors"]
    assert all(r["pass_B"] is True for r in survivors)
    assert "loser" not in [r["hypothesis_hash"] for r in survivors]
    assert result["n_candidates"] == 2


def test_does_not_route_through_evaluate_cohort(monkeypatch):
    # Guard: evaluate_cohort hard-requires 18/21; Path C's basis cohort must NOT call it.
    import backtest.tier6_dsr as t6

    def boom(*a, **k):
        raise AssertionError("evaluate_cohort must NOT be called by Path C FWER")

    monkeypatch.setattr(t6, "evaluate_cohort", boom)
    fwer.run_dsr_fwer([_moments("a", 0.1)], n_star=fwer.PATHC_N_STAR)
