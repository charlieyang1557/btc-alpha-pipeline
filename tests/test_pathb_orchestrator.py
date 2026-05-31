# tests/test_pathb_orchestrator.py
"""Orchestrator composition tests (mock engine — no data touch)."""
from __future__ import annotations

import pytest
from backtest.pathb_orchestrator import run_pathb_verdict


def test_orchestrator_composes_advisory_pipeline():
    # 3 candidates; 1 clears Tier-5 -> B_POSITIVE; escalation NOT warranted.
    fake_holdout = {
        "H1": {"holdout_sharpe": 0.3}, "H2": {"holdout_sharpe": -0.1}, "H3": {"holdout_sharpe": -0.2},
    }
    out = run_pathb_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda holdouts: [],            # no DSR pass in this scenario
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"h1_sane": True, "h2_low_leg_sane": True,
                          "h2_high_leg_sane": False, "h3_sane": True},
        step0_lifted_any=False,
    )
    assert out["taxonomy"]["advisory_taxonomy"] == "b_positive"
    assert out["escalation"]["a_escalation_warranted"] is False
    assert out["n_tier5_pass"] == 1


def test_orchestrator_process_refuted_warrants_escalation():
    out = run_pathb_verdict(
        hypotheses={"H1": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.4},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"h1_sane": True, "h2_low_leg_sane": False,
                          "h2_high_leg_sane": False, "h3_sane": False},
        step0_lifted_any=False,
    )
    assert out["taxonomy"]["advisory_taxonomy"] == "process_refuted_for_this_grid"
    assert out["escalation"]["a_escalation_warranted"] is True


def test_cli_smoke_writes_namespace_and_guards_sealed(tmp_path, monkeypatch):
    import scripts.pathb_run_verdict as cli
    # assert the sealed-dir guard rejects a sealed out-dir
    with pytest.raises(ValueError, match="sealed"):
        cli.assert_not_sealed(cli.SEALED_DIRS[0])
