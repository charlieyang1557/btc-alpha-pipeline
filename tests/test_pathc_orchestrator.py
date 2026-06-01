# tests/test_pathc_orchestrator.py
"""Path C orchestrator composition tests (mock engine — no data touch).

Adapted from tests/test_patha_orchestrator.py. The orchestrator composes the
advisory pipeline (gauntlet -> holdout_sharpe; integrity-gated moments; DSR-FWER
N*=3; tiered per-leg sanity; earned-negative taxonomy with F3 carve-out + 1d tier
threading; next-axis escalation keyed on n_dsr_pass==0) and threads the C7
hypothesis-class floors.
"""
from __future__ import annotations

import pytest

from backtest.pathc_orchestrator import run_pathc_verdict, INDETERMINATE


def _leg(tier):
    return {"tier": tier}


def test_orchestrator_composes_advisory_pipeline():
    # 3 candidates; 1 clears Tier-5 -> C_POSITIVE; escalation NOT warranted.
    fake_holdout = {
        "H1": {"holdout_sharpe": 0.3, "holdout_total_trades": 20},
        "H2": {"holdout_sharpe": -0.1, "holdout_total_trades": 15},
        "H3": {"holdout_sharpe": -0.2, "holdout_total_trades": 12},
    }
    out = run_pathc_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda holdouts: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane"), "H2": _leg("weak_sane"),
                          "H3": _leg("strong_sane")},
    )
    assert out["taxonomy"]["advisory_taxonomy"] == "c_positive"
    assert out["escalation"]["c_escalation_warranted"] is False
    assert out["n_tier5_pass"] == 1


def test_orchestrator_process_refuted_warrants_escalation_on_zero_dsr():
    # No Tier-5 pass + >=1 sane leg + n_dsr_pass == 0 -> process-refuted + escalation.
    out = run_pathc_verdict(
        hypotheses={"H1": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.4, "holdout_total_trades": 10},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane"), "H2": _leg("refuted"),
                          "H3": _leg("refuted")},
    )
    assert out["taxonomy"]["advisory_taxonomy"] == "process_refuted_for_this_grid"
    assert out["escalation"]["c_escalation_warranted"] is True
    assert out["n_dsr_pass"] == 0


def test_orchestrator_threads_floors_when_provided():
    floors = {"H1": {"eligible": True, "status": "ok"},
              "H2": {"eligible": False, "status": INDETERMINATE},
              "H3": {"eligible": True, "status": "ok"}}
    out = run_pathc_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.1, "holdout_total_trades": 5},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("refuted"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        floors=floors,
    )
    assert out["floors"] == floors


def test_orchestrator_floors_gate_under_floor_candidate_from_tier5_count():
    # LOCK "floors before ranking": an under-floor candidate with holdout_sharpe>0
    # must NOT count as a Tier-5 pass and must be marked INDETERMINATE.
    floors = {"H1": {"eligible": False, "status": INDETERMINATE},
              "H2": {"eligible": True, "status": "ELIGIBLE"},
              "H3": {"eligible": True, "status": "ELIGIBLE"}}
    fake_holdout = {
        "H1": {"holdout_sharpe": 0.9, "holdout_total_trades": 50},   # positive but UNDER-FLOOR
        "H2": {"holdout_sharpe": 0.4, "holdout_total_trades": 30},   # positive + eligible -> counts
        "H3": {"holdout_sharpe": -0.3, "holdout_total_trades": 20},  # negative
    }
    out = run_pathc_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane"), "H2": _leg("strong_sane"),
                          "H3": _leg("strong_sane")},
        floors=floors,
    )
    # Only the eligible positive-Sharpe candidate counts.
    assert out["n_tier5_pass"] == 1
    assert out["holdouts"]["H1"]["tier5_status"] == INDETERMINATE
    assert out["holdouts"]["H2"].get("tier5_status") != INDETERMINATE


def test_orchestrator_floors_none_keeps_legacy_tier5_count():
    # When floors is None, the count is the raw positive-Sharpe count.
    fake_holdout = {
        "H1": {"holdout_sharpe": 0.9, "holdout_total_trades": 30},
        "H2": {"holdout_sharpe": 0.4, "holdout_total_trades": 20},
        "H3": {"holdout_sharpe": -0.3, "holdout_total_trades": 15},
    }
    out = run_pathc_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane"), "H2": _leg("strong_sane"),
                          "H3": _leg("strong_sane")},
        floors=None,
    )
    assert out["n_tier5_pass"] == 2
    assert "tier5_status" not in out["holdouts"]["H1"]


def test_orchestrator_threads_basis_marginal_fenced():
    marginal = {"H1": {"basis_marginal_sharpe": -0.5, "promotion_affecting": False,
                        "in_n_star": False}}
    out = run_pathc_verdict(
        hypotheses={"H1": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.4, "holdout_total_trades": 10},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane")},
        basis_marginal=marginal,
    )
    assert out["basis_marginal"] == marginal
    assert out["n_tier5_pass"] == 0  # unchanged by the marginal


# ---------------------------------------------------------------------------
# Sub-fix 1c (F3): under-determined carve-out via the orchestrator path
# ---------------------------------------------------------------------------

def test_orchestrator_f3_under_floor_thin_nonnegative_is_under_determined():
    """Sub-fix 1c (b): an under-floor leg with thin-sample holdout_sharpe>=0 is
    tagged under_determined in the orchestrator's taxonomy output, NOT folded
    into the earned-negative as a substantive negative."""
    floors = {"H2": {"eligible": False, "status": INDETERMINATE}}
    # H2: under-floor + few trades + non-negative Sharpe -> under_determined
    fake_holdout = {
        "H2": {"holdout_sharpe": 0.05, "holdout_total_trades": 2},
    }
    out = run_pathc_verdict(
        hypotheses={"H2": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H2": _leg("refuted")},
        floors=floors,
    )
    assert out["under_determined_legs"].get("H2") is True


def test_orchestrator_f3_under_floor_measured_loss_not_under_determined():
    """Sub-fix 1c (a): an under-floor leg with a measured forward LOSS (holdout_sharpe<0)
    is NOT under-determined — it IS a substantive negative regardless of trade count."""
    floors = {"H2": {"eligible": False, "status": INDETERMINATE}}
    fake_holdout = {
        "H2": {"holdout_sharpe": -0.8, "holdout_total_trades": 2},
    }
    out = run_pathc_verdict(
        hypotheses={"H2": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H2": _leg("refuted")},
        floors=floors,
    )
    assert not out["under_determined_legs"].get("H2", False)
