"""Tests for the estimand-deployability minimal-confirmation (P1-P4).

Anchors to the design-point 2-leg previews (spec
docs/superpowers/specs/2026-06-02-estimand-deployability-confirmation-design.md):
P1 skew-divorce, P2 net-benefit-after-2N*, P3 multiplicity z, P4 runs-test inert.
All read-only; none touches the sealed dir.
"""
import math

import pytest

from backtest import eval_estimand_deploy as edc


# --------------------------------------------------------------------------
# P1 — skew-divorce: directional gate fires at net-Sharpe <= 0 (non-deployable).
# --------------------------------------------------------------------------
def test_p1_skew_divorce_case():
    r = edc.skew_divorce_case(a=-10.0, drift=-0.02)
    assert r["gamma3"] == pytest.approx(-0.956, abs=0.01)
    assert r["sharpe"] < 0.0                 # NOT deployable
    assert r["p_up"] > 0.55                  # but directional hit-rate is high
    assert r["sign_z"] > 2.0                 # directional gate fires hard
    assert r["directional_fires_but_not_deployable"] is True


def test_p1_advantage_concentrates_in_nondeployable_zone():
    r = edc.p1_skew_divorce_summary()
    # the max directional hit-rate reachable at net-Sharpe<=0 is large (fires),
    # confirming the directional advantage overlaps the non-deployable zone.
    assert r["max_p_up_at_nonpositive_sharpe"] > 0.55
    assert r["concentrates_in_nondeployable_zone"] is True


# --------------------------------------------------------------------------
# P2 — net benefit of adding a directional gate, AFTER 2N* multiplicity, is
# far below the >=10pp tripwire across the deployable band.
# --------------------------------------------------------------------------
def test_p2_net_benefit_below_tripwire():
    r = edc.p2_net_benefit_after_multiplicity()
    assert r["max_net_benefit_pp"] < 10.0    # the DON'T-BUILD tripwire
    assert r["tripwire_pp"] == 10.0
    assert r["below_tripwire"] is True


# --------------------------------------------------------------------------
# P3 — 2N* multiplicity z-threshold increase (the cost a 2nd gate imposes).
# --------------------------------------------------------------------------
def test_p3_multiplicity_threshold_increase():
    assert edc.multiplicity_z(18) == pytest.approx(2.773, abs=0.005)
    assert edc.multiplicity_z(36) == pytest.approx(2.991, abs=0.005)
    r = edc.p3_multiplicity_cost()
    assert r["z_increase_n18"] == pytest.approx(0.218, abs=0.005)
    assert r["doubling_inflates_bar"] is True


def test_out_of_grid_global_max_below_tripwire():
    # false-negative foreclosure: global max over a wide dense box (incl. the
    # absurd non-deployable corner) is still < the 10pp tripwire.
    r = edc.out_of_grid_search()
    assert r["global_max_net_benefit_pp"] == pytest.approx(7.09, abs=0.15)
    assert r["below_tripwire"] is True
    assert r["global_max_at"]["sharpe_ann"] == pytest.approx(2.0)
    assert r["n_cells"] >= 3000


# --------------------------------------------------------------------------
# P4 — runs-test is a confirmation-layer category error: a serial-dependence
# edge shows up in STRATEGY P&L Sharpe (the gate catches it), so a runs-test
# adds no deployable-confirmation value the Sharpe gate misses.
# --------------------------------------------------------------------------
def test_p4_runs_test_inert_at_confirmation_layer():
    r = edc.p4_runs_test_inert(rho=0.32, seed=7)
    assert abs(r["raw_return_sharpe"]) < 0.05      # raw returns ~ Sharpe-blind
    assert r["momentum_pnl_sharpe"] > 0.1          # but the strategy P&L isn't
    assert r["serial_edge_shows_in_pnl_sharpe"] is True


# --------------------------------------------------------------------------
# Aggregate verdict + safety.
# --------------------------------------------------------------------------
def test_run_confirmation_verdict_dont_build():
    out = edc.run_confirmation()
    for k in ("P1", "P2", "P3", "P4"):
        assert k in out
    assert out["verdict"] == "DONT_BUILD"


def test_no_evaluate_cohort_call():
    import ast

    src = open(edc.__file__).read()
    tree = ast.parse(src)
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                called.add(f.id)
            elif isinstance(f, ast.Attribute):
                called.add(f.attr)
    assert "evaluate_cohort" not in called
    assert "tier6_dsr_v1" not in src
