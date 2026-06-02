# tests/test_pathd_dsr_fwer.py
"""Path D DSR-FWER: per-candidate evaluate_candidate loop; survivors = pass_B True.

Adapted from tests/test_pathc_dsr_fwer.py. PATHD_N_STAR = 3 (= PATHC_N_STAR =
PATHA_N_STAR = PATHB_N_STAR); the DSR math is REUSED from tier6 (evaluate_candidate,
Form B, frozen Z_PASS) — this module only loops it per OI candidate and selects
pass_B survivors.
"""
from __future__ import annotations

import backtest.pathd_dsr_fwer as fwer
from backtest.tier6_dsr import CandidateMoments


def _moments(hh: str, sr: float, T: int = 2000) -> CandidateMoments:
    return CandidateMoments(
        hypothesis_hash=hh, name=hh, theme="pathd",
        sr_per_bar=sr, gamma3=0.0, gamma4=3.0, T=T, trades=50,
    )


def test_pathd_n_star_default_is_3():
    assert fwer.PATHD_N_STAR == 3


def test_pathd_n_star_equals_pathc_n_star():
    import backtest.pathc_dsr_fwer as pc
    assert fwer.PATHD_N_STAR == pc.PATHC_N_STAR


def test_pathd_n_star_equals_patha_n_star():
    import backtest.patha_dsr_fwer as pa
    assert fwer.PATHD_N_STAR == pa.PATHA_N_STAR


def test_dsr_rows_is_per_candidate_loop_over_evaluate_candidate():
    cands = [_moments("oi_a", 0.0), _moments("oi_b", 0.5)]
    rows = fwer._dsr_rows(cands, n_star=fwer.PATHD_N_STAR)
    assert len(rows) == 2
    assert all(r["n_star"] == fwer.PATHD_N_STAR for r in rows)
    assert all("pass_B" in r for r in rows)


def test_survivors_are_rows_with_pass_B_true():
    cands = [_moments("oi_loser", 0.0), _moments("oi_winner", 5.0, T=5000)]
    result = fwer.run_dsr_fwer(cands, n_star=fwer.PATHD_N_STAR)
    survivors = result["survivors"]
    assert all(r["pass_B"] is True for r in survivors)
    assert "oi_loser" not in [r["hypothesis_hash"] for r in survivors]
    assert result["n_candidates"] == 2


def test_does_not_route_through_evaluate_cohort(monkeypatch):
    # Guard: evaluate_cohort hard-requires 18/21; Path D's OI cohort must NOT call it.
    import backtest.tier6_dsr as t6

    def boom(*a, **k):
        raise AssertionError("evaluate_cohort must NOT be called by Path D FWER")

    monkeypatch.setattr(t6, "evaluate_cohort", boom)
    fwer.run_dsr_fwer([_moments("oi_a", 0.1)], n_star=fwer.PATHD_N_STAR)
