# tests/test_pathd_orchestrator.py
"""Path D orchestrator composition tests (mock engine — no data touch).

Adapted from tests/test_pathc_orchestrator.py. The orchestrator composes the
advisory pipeline (gauntlet -> holdout_sharpe; integrity-gated moments; DSR-FWER
N*=3; tiered per-leg sanity; earned-negative taxonomy with GENERIC under-determined
carve-out; H3 leakage annotation; next-axis escalation keyed on n_dsr_pass==0)
and threads the C7 hypothesis-class floors.

KEY DIVERGENCES from pathc:
  - D1-only: oi_marginal (not basis_marginal) in the bundle; no D2 references.
  - H3 leakage annotation: consistent_with_momentum_or_vol_leakage in bundle.
  - GENERIC F3 carve-out (any eligible==False floor).
"""
from __future__ import annotations

import pytest

from backtest.pathd_orchestrator import run_pathd_verdict, INDETERMINATE


def _leg(tier):
    return {"tier": tier}


def test_orchestrator_composes_advisory_pipeline():
    # 3 candidates; 1 clears Tier-5 -> D_POSITIVE; escalation NOT warranted.
    fake_holdout = {
        "H1": {"holdout_sharpe": 0.3, "holdout_total_trades": 20},
        "H2": {"holdout_sharpe": -0.1, "holdout_total_trades": 15},
        "H3": {"holdout_sharpe": -0.2, "holdout_total_trades": 12},
    }
    out = run_pathd_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda holdouts: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane"), "H2": _leg("weak_sane"),
                          "H3": _leg("strong_sane")},
    )
    assert out["taxonomy"]["advisory_taxonomy"] == "d_positive"
    assert out["escalation"]["d_escalation_warranted"] is False
    assert out["n_tier5_pass"] == 1


def test_orchestrator_process_refuted_warrants_escalation_on_zero_dsr():
    # No Tier-5 pass + >=1 sane leg + n_dsr_pass == 0 -> process-refuted + escalation.
    out = run_pathd_verdict(
        hypotheses={"H1": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.4, "holdout_total_trades": 10},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane"), "H2": _leg("refuted"),
                          "H3": _leg("refuted")},
    )
    assert out["taxonomy"]["advisory_taxonomy"] == "process_refuted_for_this_grid"
    assert out["escalation"]["d_escalation_warranted"] is True
    assert out["n_dsr_pass"] == 0


def test_orchestrator_threads_floors_when_provided():
    floors = {"H1": {"eligible": True, "status": "ok"},
              "H2": {"eligible": False, "status": INDETERMINATE},
              "H3": {"eligible": True, "status": "ok"}}
    out = run_pathd_verdict(
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
    out = run_pathd_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane"), "H2": _leg("strong_sane"),
                          "H3": _leg("strong_sane")},
        floors=floors,
    )
    assert out["n_tier5_pass"] == 1
    assert out["holdouts"]["H1"]["tier5_status"] == INDETERMINATE
    assert out["holdouts"]["H2"].get("tier5_status") != INDETERMINATE


def test_orchestrator_floors_none_keeps_legacy_tier5_count():
    fake_holdout = {
        "H1": {"holdout_sharpe": 0.9, "holdout_total_trades": 30},
        "H2": {"holdout_sharpe": 0.4, "holdout_total_trades": 20},
        "H3": {"holdout_sharpe": -0.3, "holdout_total_trades": 15},
    }
    out = run_pathd_verdict(
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


def test_orchestrator_threads_oi_marginal_fenced():
    """D1-ONLY: oi_marginal (not basis_marginal) in the bundle; promotion_affecting=False."""
    marginal = {"H1": {"d1": {"d1_marginal_sharpe": -0.5, "promotion_affecting": False,
                               "in_n_star": False}, "promotion_affecting": False, "in_n_star": False}}
    out = run_pathd_verdict(
        hypotheses={"H1": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.4, "holdout_total_trades": 10},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane")},
        oi_marginal=marginal,
    )
    assert out["oi_marginal"] == marginal
    assert out["n_tier5_pass"] == 0  # unchanged by the marginal


def test_orchestrator_no_d2_in_oi_marginal():
    """No D2 in the oi_marginal dict — OI is independent, D2 dropped."""
    marginal = {"H1": {"d1": {"d1_marginal_sharpe": 0.1, "promotion_affecting": False,
                               "in_n_star": False}, "promotion_affecting": False, "in_n_star": False}}
    out = run_pathd_verdict(
        hypotheses={"H1": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.2, "holdout_total_trades": 8},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("refuted")},
        oi_marginal=marginal,
    )
    # No d2, no redundancy_read in oi_marginal for Path D.
    assert "d2" not in out["oi_marginal"]["H1"]
    assert "redundancy_read" not in out["oi_marginal"]["H1"]


# ---------------------------------------------------------------------------
# GENERIC F3: under-determined carve-out via the orchestrator path
# ---------------------------------------------------------------------------

def test_orchestrator_f3_under_floor_thin_nonnegative_is_under_determined():
    """GENERIC F3: an under-floor leg with thin-sample holdout_sharpe>=0 is
    tagged under_determined in the orchestrator's taxonomy output."""
    floors = {"H2": {"eligible": False, "status": INDETERMINATE}}
    fake_holdout = {
        "H2": {"holdout_sharpe": 0.05, "holdout_total_trades": 2},
    }
    out = run_pathd_verdict(
        hypotheses={"H2": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H2": _leg("refuted")},
        floors=floors,
    )
    assert out["under_determined_legs"].get("H2") is True


def test_orchestrator_f3_under_floor_measured_loss_not_under_determined():
    """GENERIC F3: an under-floor leg with a measured forward LOSS (holdout_sharpe<0)
    is NOT under-determined — it IS a substantive negative regardless of trade count."""
    floors = {"H2": {"eligible": False, "status": INDETERMINATE}}
    fake_holdout = {
        "H2": {"holdout_sharpe": -0.8, "holdout_total_trades": 2},
    }
    out = run_pathd_verdict(
        hypotheses={"H2": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H2": _leg("refuted")},
        floors=floors,
    )
    assert not out["under_determined_legs"].get("H2", False)


# ---------------------------------------------------------------------------
# C7 resolve_theta deterministic rule
# ---------------------------------------------------------------------------

def test_resolve_theta_returns_090_when_episodes_gte_200():
    from backtest.pathd_orchestrator import resolve_theta
    assert resolve_theta(200) == 0.90
    assert resolve_theta(201) == 0.90
    assert resolve_theta(999) == 0.90


def test_resolve_theta_returns_085_when_episodes_lt_200():
    from backtest.pathd_orchestrator import resolve_theta
    assert resolve_theta(0) == 0.85
    assert resolve_theta(150) == 0.85
    assert resolve_theta(199) == 0.85


def test_resolve_theta_boundary_at_200():
    from backtest.pathd_orchestrator import resolve_theta
    assert resolve_theta(200) == 0.90  # boundary: >=200 stays at 0.90
    assert resolve_theta(199) == 0.85  # just below: falls back


# ---------------------------------------------------------------------------
# Instrument repair: degenerate (flat / zero-variance) leg handling
# ---------------------------------------------------------------------------

def test_orchestrator_degenerate_leg_excluded_from_dsr_recorded_in_bundle():
    """Instrument repair: a degenerate holdout (degenerate=True) must be:
    - excluded from the DSR cohort
    - recorded in ``degenerate_legs``
    - NOT counted in n_tier5_pass
    - run COMPLETES (no crash)
    """
    fake_holdout = {
        "H1": {"holdout_sharpe": 0.5, "holdout_total_trades": 20},
        "H2": {"holdout_sharpe": 0.0, "holdout_total_trades": 0, "degenerate": True},
    }
    moments_input_keys = []

    def _capture_moments(holdouts):
        moments_input_keys.extend(holdouts.keys())
        return []

    out = run_pathd_verdict(
        hypotheses={"H1": object(), "H2": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=_capture_moments,
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane"), "H2": _leg("refuted")},
    )
    assert "holdouts" in out
    assert "n_tier5_pass" in out
    # Degenerate leg must NOT be passed to build_moments.
    assert "H2" not in moments_input_keys
    assert out["n_tier5_pass"] == 1
    assert "degenerate_legs" in out
    assert "H2" in out["degenerate_legs"]
    assert out["degenerate_legs"]["H2"] is True


def test_orchestrator_all_degenerate_no_crash():
    """All-degenerate cohort → run completes, n_dsr_pass=0, taxonomy coherent."""
    fake_holdout = {
        "H1": {"holdout_sharpe": 0.0, "holdout_total_trades": 0, "degenerate": True},
        "H2": {"holdout_sharpe": 0.0, "holdout_total_trades": 0, "degenerate": True},
        "H3": {"holdout_sharpe": 0.0, "holdout_total_trades": 0, "degenerate": True},
    }
    out = run_pathd_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda holdouts: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("refuted"), "H2": _leg("refuted"),
                          "H3": _leg("refuted")},
    )
    assert "taxonomy" in out
    assert out["n_dsr_pass"] == 0
    assert out["n_tier5_pass"] == 0
    assert "degenerate_legs" in out
    assert set(out["degenerate_legs"]) >= {"H1", "H2", "H3"}
    assert out["taxonomy"].get("advisory_taxonomy") is not None


# ---------------------------------------------------------------------------
# consistent_with_momentum_or_vol_leakage in bundle (NET-NEW for Path D)
# ---------------------------------------------------------------------------

def test_orchestrator_bundle_carries_h3_leakage_annotation():
    """consistent_with_momentum_or_vol_leakage must be present in the bundle."""
    out = run_pathd_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.2, "holdout_total_trades": 5},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"H1": _leg("strong_sane"), "H2": _leg("strong_sane"),
                          "H3": _leg("strong_sane")},
    )
    assert "consistent_with_momentum_or_vol_leakage" in out
