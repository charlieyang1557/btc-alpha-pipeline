"""Tests for the Bayesian / continuous-evidence eval-layer scoping analysis.

TDD anchors for the SV1-SV7 read-only spot-checks (spec
docs/superpowers/specs/2026-06-02-bayesian-eval-layer-scoping-design.md §4).
Expected values are hand-computed / design-point-B2-previewed; the module must
reproduce them. All checks are read-only; none touches the sealed dir.
"""
import math

import pytest

from backtest import eval_layer_scoping as els


# --------------------------------------------------------------------------
# SV1 (M1) — posterior-sizing ruin profile.
# --------------------------------------------------------------------------
def test_sv1_full_kelly_fraction():
    assert els.full_kelly_fraction(1.5, 0.6) == pytest.approx(2.5)


def test_sv1_se_ann_matches_186():
    se = els.se_ann(els.FORWARD_T, els.FORWARD_PPY)
    assert se == pytest.approx(1.862, abs=0.005)


def test_sv1_prob_sharpe_le_zero():
    se = els.se_ann(els.FORWARD_T, els.FORWARD_PPY)
    assert els.prob_sharpe_le_zero(1.5, se) == pytest.approx(0.210, abs=0.005)


def test_sv1_profile_flags_no_power_gain():
    r = els.sv1_sizing_profile(1.5)
    assert r["no_power_gain"] is True
    assert r["prob_sharpe_le_zero"] > 0.15  # one-in-five sign error


# --------------------------------------------------------------------------
# SV3 (M3) — shrinkage backfire (the seed mechanism; assumption-disclosed band).
# --------------------------------------------------------------------------
def test_sv3_cohort_mean():
    assert els.cohort_mean() == pytest.approx(-2.5467, abs=0.001)


def test_sv3_shrinkage_band():
    r = els.sv3_shrinkage(1.5)
    assert r["posterior_mean_denoised"] == pytest.approx(-1.60, abs=0.06)
    assert r["posterior_mean_raw"] == pytest.approx(-0.26, abs=0.06)


def test_sv3_backfires_both_below_deploy_line():
    r = els.sv3_shrinkage(1.5)
    assert r["posterior_mean_denoised"] < 1.0
    assert r["posterior_mean_raw"] < 1.0
    assert r["backfires"] is True


# --------------------------------------------------------------------------
# SV4 (M4) — skeptical prior can only tighten.
# --------------------------------------------------------------------------
def test_sv4_skeptical_only_tightens():
    r = els.sv4_skeptical_direction(1.5)
    assert r["posterior_mean"] < 1.5
    assert r["only_tightens"] is True
    assert r["raises_power"] is False


# --------------------------------------------------------------------------
# SV5 (M5) — always-valid / e-value attainability (only-via-time).
# --------------------------------------------------------------------------
def test_sv5_expected_log_lr():
    lr = els.expected_log_lr(1.5, els.FORWARD_T, els.FORWARD_PPY)
    assert lr == pytest.approx(0.3246, abs=0.001)


def test_sv5_attainability_needs_years():
    r = els.sv5_attainability(1.5)
    assert r["log_e_threshold"] == pytest.approx(math.log(20.0), abs=1e-9)
    assert r["bars_to_threshold"] == pytest.approx(23325, rel=0.02)
    assert r["years_to_threshold"] == pytest.approx(2.66, abs=0.06)
    assert r["only_via_time"] is True


# --------------------------------------------------------------------------
# SV6 (M6) — change-the-estimand power comparison (VERDICT-CRITICAL).
# --------------------------------------------------------------------------
def test_sv6_sharpe_power_matches_mc():
    p = els.power_sharpe_test(1.5, els.FORWARD_T, els.FORWARD_PPY)
    assert p == pytest.approx(0.20, abs=0.02)


def test_sv6_gaussian_are_is_two_over_pi():
    assert els.sign_test_are(3.0) == pytest.approx(2.0 / math.pi, abs=1e-3)


def test_sv6_directional_overtakes_at_realistic_kurtosis():
    # CORRECTED (Codex B2): the sign/median test overtakes the mean/Sharpe test at
    # realistic kurtosis (~12), NOT astronomical; ARE > 1 by gamma4=60.
    assert 10.0 < els.kurtosis_crossover() < 14.0
    assert els.sign_test_are(60.0) > 1.0


def test_sv6_not_refuted_as_power_lever():
    r = els.sv6_estimand_comparison(1.5)
    assert r["refuted_as_power_lever"] is False
    assert r["plausibly_raises_power"] is True
    # M6 raises power for the directional estimand at BTC kurtosis (ARE ~ 1.0)...
    assert r["are_observed_g4"] == pytest.approx(1.0, abs=0.02)
    # ...but deployment-relevance (hit-rate != Sharpe) is NOT resolved inline.
    assert r["deployment_relevance_resolved_inline"] is False


# --------------------------------------------------------------------------
# SV2 (M2) — sequential posterior gives no free acceleration (tiny MC).
# --------------------------------------------------------------------------
def test_sv2_no_free_acceleration():
    r = els.sv2_no_acceleration(1.5, m=1500, seed=42)
    assert r["detection_sequential"] <= r["detection_fixed_T"] + 0.05
    assert r["detection_fixed_T"] == pytest.approx(0.20, abs=0.06)
    assert r["only_via_time"] is True


# --------------------------------------------------------------------------
# SV7 (M7) — within-batch EB winner's-curse (conditional / out of scope now).
# --------------------------------------------------------------------------
def test_sv7_conditional_and_shrinks():
    r = els.sv7_eb_illustration()
    assert 0.0 < r["shrinkage_factor"] < 1.0
    assert r["in_scope_now"] is False


# --------------------------------------------------------------------------
# Safety: import-primitives-only, never writes the sealed dir.
# --------------------------------------------------------------------------
def test_no_evaluate_cohort_call():
    """AST-level: the module never IMPORTS or CALLS evaluate_cohort (the docstring
    may mention it in the CONTRACT BOUNDARY note); and never names the sealed dir."""
    import ast

    src = open(els.__file__).read()
    tree = ast.parse(src)
    called: set[str] = set()
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                called.add(f.id)
            elif isinstance(f, ast.Attribute):
                called.add(f.attr)
        if isinstance(node, ast.ImportFrom):
            for a in node.names:
                imported.add(a.name)
    assert "evaluate_cohort" not in called
    assert "evaluate_cohort" not in imported
    assert "tier6_dsr_v1" not in src  # never references the sealed dir path


def test_run_analysis_assembles_all_svs():
    out = els.run_analysis(sv2_m=400, seed=7)
    for k in ("SV1", "SV2", "SV3", "SV4", "SV5", "SV6", "SV7"):
        assert k in out
    assert out["SV3"]["backfires"] is True
    assert out["SV6"]["refuted_as_power_lever"] is False
