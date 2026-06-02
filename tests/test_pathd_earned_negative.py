# tests/test_pathd_earned_negative.py
"""Path D earned-negative EVIDENCE bundle (advisory): keyed on Tier-5
holdout_sharpe>0, NOT DSR pass_B.

Adapted from tests/test_pathc_earned_negative.py. NET-NEW for Path D:
- GENERIC under-determined carve-out (any eligible==False floor, not
  zero_fraction-specific).
- H3 leakage annotation: consistent_with_momentum_or_vol_leakage=True when H3
  is under-determined AND mechanism-sane.
- d_positive_strength (not c_positive_strength).
"""
from __future__ import annotations

import pytest

import backtest.pathd_earned_negative as en


def _ev(per_leg, n_tier5_pass, n_dsr_pass, side_effect=False, under_determined_flags=None):
    return en.assemble_evidence(
        per_leg=per_leg,
        n_tier5_pass=n_tier5_pass,
        n_dsr_pass=n_dsr_pass,
        promotion_side_effect=side_effect,
        under_determined_flags=under_determined_flags,
    )


def _leg(tier):
    return {"tier": tier}


# ---------------------------------------------------------------------------
# Basic taxonomy
# ---------------------------------------------------------------------------

def test_mechanism_refuted_when_all_legs_refuted():
    ev = _ev({"H1": _leg("refuted"), "H2": _leg("refuted"), "H3": _leg("refuted")},
             n_tier5_pass=0, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.MECHANISM_REFUTED
    assert ev["is_earned_negative"] is True
    assert ev["any_mechanism_sane"] is False
    assert ev["verdict_rests_on_weak_sane_only"] is False


def test_process_refuted_when_strong_sane_but_no_tier5_pass():
    ev = _ev({"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
             n_tier5_pass=0, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.PROCESS_REFUTED_FOR_GRID
    assert ev["is_earned_negative"] is True
    assert ev["any_mechanism_sane"] is True
    assert ev["verdict_rests_on_weak_sane_only"] is False


def test_d_positive_when_a_variant_clears_tier5_even_if_dsr_fails():
    ev = _ev({"H1": _leg("strong_sane"), "H2": _leg("weak_sane"), "H3": _leg("strong_sane")},
             n_tier5_pass=1, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.D_POSITIVE
    assert ev["is_earned_negative"] is False
    assert ev["d_positive_strength"] == "weak_needs_2025_oos"


def test_d_positive_strong_when_dsr_passes():
    ev = _ev({"H1": _leg("strong_sane")}, n_tier5_pass=2, n_dsr_pass=1)
    assert ev["advisory_taxonomy"] == en.D_POSITIVE
    assert ev["d_positive_strength"] == "dsr_promoted"


def test_promotion_side_effect_true_is_a_hard_error():
    with pytest.raises(ValueError, match="promotion_side_effect"):
        _ev({"H1": _leg("strong_sane")}, n_tier5_pass=0, n_dsr_pass=0, side_effect=True)


def test_bundle_is_advisory_not_a_fired_decision():
    ev = _ev({"H1": _leg("strong_sane")}, n_tier5_pass=0, n_dsr_pass=0)
    assert "escalate" not in ev
    assert ev["verdict_authority"] == "charlie_register_at_earned_negative_gate"


def test_assemble_evidence_carries_pinned_tempers():
    out = _ev({"H1": _leg("strong_sane")}, n_tier5_pass=0, n_dsr_pass=0)
    assert out["approximation_tempers"] == list(en.APPROXIMATION_TEMPERS)
    # Path D tempers reference OI independent axis + generic F3 carve-out.
    assert any("d1_only" in t or "independent" in t for t in out["approximation_tempers"])
    assert any("generic" in t.lower() or "f3" in t.lower() or "under_determined" in t.lower()
               for t in out["approximation_tempers"])


def test_accepts_bare_string_tiers_too():
    ev = _ev({"H1": "weak_sane", "H2": "refuted", "H3": "refuted"},
             n_tier5_pass=0, n_dsr_pass=0)
    assert ev["any_mechanism_sane"] is True
    assert ev["verdict_rests_on_weak_sane_only"] is True


# ---------------------------------------------------------------------------
# Sub-fix 1d: verdict_rests_on_weak_sane_only
# ---------------------------------------------------------------------------

def test_verdict_rests_on_weak_sane_only_when_sole_sane_is_weak():
    ev = _ev({"H1": _leg("weak_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
             n_tier5_pass=0, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.PROCESS_REFUTED_FOR_GRID
    assert ev["any_mechanism_sane"] is True
    assert ev["verdict_rests_on_weak_sane_only"] is True


def test_verdict_does_not_rest_on_weak_sane_only_when_strong_sane_present():
    ev = _ev({"H1": _leg("strong_sane"), "H2": _leg("weak_sane"), "H3": _leg("refuted")},
             n_tier5_pass=0, n_dsr_pass=0)
    assert ev["verdict_rests_on_weak_sane_only"] is False


# ---------------------------------------------------------------------------
# GENERIC under-determined carve-out (Path D divergence from Path C)
# ---------------------------------------------------------------------------

def test_generic_under_determined_carve_out_flags_leg():
    """GENERIC F3: under-floor + thin-sample non-negative -> under_determined.
    The predicate is eligible==False AND ..., NOT zero_fraction-specific."""
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": True},
    )
    assert ev["under_determined_legs"].get("H2") is True


def test_generic_under_determined_measured_loss_not_flagged():
    """GENERIC F3: under-floor + measured loss -> NOT under_determined."""
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": False},
    )
    assert "H2" not in ev["under_determined_legs"]


def test_under_determined_legs_empty_when_no_flags():
    ev = _ev({"H1": _leg("strong_sane")}, n_tier5_pass=0, n_dsr_pass=0)
    assert ev["under_determined_legs"] == {}


def test_f3_threshold_constant_is_preregistered():
    assert en.UNDER_DETERMINED_TRADE_THRESHOLD == 10


# ---------------------------------------------------------------------------
# NET-NEW for Path D: H3 leakage annotation
# ---------------------------------------------------------------------------

def test_h3_leakage_annotation_true_when_h3_under_determined_and_sane():
    """NET-NEW: H3 under-determined + mechanism-sane -> consistent_with_momentum_or_vol_leakage=True."""
    ev = _ev(
        {"H1": _leg("refuted"), "H2": _leg("refuted"), "H3": _leg("strong_sane")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H3": True},
    )
    assert ev["consistent_with_momentum_or_vol_leakage"] is True


def test_h3_leakage_annotation_false_when_h3_not_under_determined():
    """H3 is eligible (not under-determined) -> consistent_with_momentum_or_vol_leakage=False."""
    ev = _ev(
        {"H1": _leg("refuted"), "H2": _leg("refuted"), "H3": _leg("strong_sane")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H3": False},
    )
    assert ev["consistent_with_momentum_or_vol_leakage"] is False


def test_h3_leakage_annotation_false_when_h3_under_determined_but_refuted():
    """H3 under-determined but refuted -> NOT consistent (refuted means sign failed)."""
    ev = _ev(
        {"H1": _leg("refuted"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H3": True},
    )
    assert ev["consistent_with_momentum_or_vol_leakage"] is False


def test_h3_leakage_annotation_key_always_present():
    """consistent_with_momentum_or_vol_leakage must always be present in the bundle."""
    ev = _ev({"H1": _leg("strong_sane"), "H2": _leg("strong_sane"), "H3": _leg("strong_sane")},
             n_tier5_pass=0, n_dsr_pass=0)
    assert "consistent_with_momentum_or_vol_leakage" in ev


# ---------------------------------------------------------------------------
# F3 headline caveat: earned_negative_power_limited flag
# ---------------------------------------------------------------------------

def test_earned_negative_power_limited_true_when_any_under_determined():
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": True},
    )
    assert ev["earned_negative_power_limited"] is True
    assert ev["earned_negative_power_limited_note"] is not None


def test_earned_negative_power_limited_false_when_no_under_determined():
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": False},
    )
    assert ev["earned_negative_power_limited"] is False
    assert ev["earned_negative_power_limited_note"] is None


def test_earned_negative_power_limited_does_not_change_taxonomy():
    ev_clean = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
    )
    ev_flagged = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": True},
    )
    assert ev_clean["advisory_taxonomy"] == ev_flagged["advisory_taxonomy"]
    assert ev_clean["is_earned_negative"] == ev_flagged["is_earned_negative"]
    assert ev_flagged["earned_negative_power_limited"] is True
    assert ev_clean["earned_negative_power_limited"] is False


# ---------------------------------------------------------------------------
# Q5: verdict_headline
# ---------------------------------------------------------------------------

def test_verdict_headline_power_limited_contains_power_limited_and_leg_id():
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": True},
    )
    assert "verdict_headline" in ev
    assert "POWER-LIMITED" in ev["verdict_headline"]
    assert "H2" in ev["verdict_headline"]
    assert ev["is_earned_negative"] is True


def test_verdict_headline_clean_case_no_power_limited():
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
    )
    assert "verdict_headline" in ev
    assert "POWER-LIMITED" not in ev["verdict_headline"]
    assert "PROCESS_REFUTED" in ev["verdict_headline"] or "process_refuted" in ev["verdict_headline"].lower()


# ---------------------------------------------------------------------------
# FIX 2: §37.3 substantive-vs-vacuous fields
# ---------------------------------------------------------------------------

def test_substantive_basis_true_when_at_least_one_leg_has_measured_loss():
    """§37.3 (a): >=1 measured-loss leg + 0 DSR pass -> substantive basis, escalation warranted."""
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": False, "H3": False},
    )
    # Manually call with holdout_sharpes to test the field
    ev2 = en.assemble_evidence(
        per_leg={"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        promotion_side_effect=False,
        under_determined_flags={"H2": False, "H3": False},
        holdout_sharpes={"H1": -0.87, "H2": -1.5, "H3": -0.5},
    )
    assert ev2["n_substantive_loss_legs"] == 3
    assert ev2["negative_has_substantive_basis"] is True
    assert ev2["negative_is_vacuous_only"] is False


def test_vacuous_only_when_all_legs_under_determined_no_measured_loss():
    """§37.3 (b): all legs under-determined (no measured loss) -> negative_is_vacuous_only=True."""
    ev = en.assemble_evidence(
        per_leg={"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        promotion_side_effect=False,
        under_determined_flags={"H1": True, "H2": True, "H3": True},
        holdout_sharpes={"H1": 0.0, "H2": 0.1, "H3": 0.05},  # all non-negative
    )
    assert ev["n_substantive_loss_legs"] == 0
    assert ev["negative_has_substantive_basis"] is False
    assert ev["negative_is_vacuous_only"] is True
    assert "VACUOUS" in ev["verdict_headline"]


def test_mixed_case_some_loss_some_under_determined():
    """§37.3 (c): mixed — 1 leg with measured loss, 1 under-determined."""
    ev = en.assemble_evidence(
        per_leg={"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        promotion_side_effect=False,
        under_determined_flags={"H2": True, "H3": False},
        holdout_sharpes={"H1": -0.87, "H2": 0.1, "H3": -0.5},
    )
    # H1 and H3 have measured losses; H2 is under-determined (non-negative)
    assert ev["n_substantive_loss_legs"] == 2
    assert ev["negative_has_substantive_basis"] is True
    assert ev["negative_is_vacuous_only"] is False


def test_37_3_fields_always_present_in_bundle():
    """§37.3 fields must always appear (not only when earned-negative)."""
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("strong_sane"), "H3": _leg("strong_sane")},
        n_tier5_pass=1, n_dsr_pass=0,
    )
    assert "n_substantive_loss_legs" in ev
    assert "negative_has_substantive_basis" in ev
    assert "negative_is_vacuous_only" in ev


def test_37_3_conservative_fallback_when_holdout_sharpes_not_provided():
    """§37.3 conservative fallback: when holdout_sharpes is None and is_earned_negative=True,
    n_substantive_loss_legs defaults to 1 (conservative — preserves escalation_warranted)."""
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
    )
    # is_earned_negative is True; fallback gives n_substantive_loss_legs=1
    assert ev["is_earned_negative"] is True
    assert ev["n_substantive_loss_legs"] == 1
    assert ev["negative_has_substantive_basis"] is True
    assert ev["negative_is_vacuous_only"] is False


def test_37_3_vacuous_only_false_when_not_earned_negative():
    """§37.3: negative_is_vacuous_only is False when not earned-negative (D_POSITIVE)."""
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("strong_sane"), "H3": _leg("strong_sane")},
        n_tier5_pass=2, n_dsr_pass=0,
    )
    assert ev["is_earned_negative"] is False
    assert ev["negative_is_vacuous_only"] is False
