# tests/test_patha_orchestrator.py
"""Path A orchestrator composition tests (mock engine — no data touch).

Adapted from tests/test_pathb_orchestrator.py. The orchestrator composes the
advisory pipeline (gauntlet -> holdout_sharpe; integrity-gated moments; DSR-FWER
N*=3; tiered per-leg sanity; earned-negative taxonomy; next-axis escalation keyed
on n_dsr_pass==0) and threads the C7 hypothesis-class floors.
"""
from __future__ import annotations

from backtest.patha_orchestrator import run_patha_verdict


def _leg(tier):
    return {"tier": tier}


def test_orchestrator_composes_advisory_pipeline():
    # 3 candidates; 1 clears Tier-5 -> B_POSITIVE; escalation NOT warranted.
    fake_holdout = {
        "H1": {"holdout_sharpe": 0.3}, "H2": {"holdout_sharpe": -0.1}, "H3": {"holdout_sharpe": -0.2},
    }
    out = run_patha_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda holdouts: [],            # no DSR pass in this scenario
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane"), "H2": _leg("weak_sane"),
                          "H3": _leg("strong_sane")},
    )
    assert out["taxonomy"]["advisory_taxonomy"] == "b_positive"
    assert out["escalation"]["a_escalation_warranted"] is False
    assert out["n_tier5_pass"] == 1


def test_orchestrator_process_refuted_warrants_escalation_on_zero_dsr():
    # No Tier-5 pass + >=1 sane leg + n_dsr_pass == 0 -> process-refuted + escalation.
    out = run_patha_verdict(
        hypotheses={"H1": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.4},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane"), "H2": _leg("refuted"),
                          "H3": _leg("refuted")},
    )
    assert out["taxonomy"]["advisory_taxonomy"] == "process_refuted_for_this_grid"
    assert out["escalation"]["a_escalation_warranted"] is True
    assert out["n_dsr_pass"] == 0


def test_orchestrator_threads_floors_when_provided():
    floors = {"H1": {"eligible": True, "status": "ok"},
              "H2": {"eligible": False, "status": "INDETERMINATE"},
              "H3": {"eligible": True, "status": "ok"}}
    out = run_patha_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.1},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("refuted"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        floors=floors,
    )
    assert out["floors"] == floors


def test_orchestrator_threads_marginal_diagnostic_fenced():
    marginal = {"H1": {"funding_marginal_sharpe": -0.5, "promotion_affecting": False,
                        "in_n_star": False}}
    out = run_patha_verdict(
        hypotheses={"H1": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.4},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane")},
        funding_marginal=marginal,
    )
    # the diagnostic rides along but never feeds N* or promotion.
    assert out["funding_marginal"] == marginal
    assert out["n_tier5_pass"] == 0  # unchanged by the marginal
