# tests/test_pathb_earned_negative.py
"""Earned-negative EVIDENCE bundle (advisory): keyed on Tier-5 holdout_sharpe>0,
NOT DSR pass_B. The binding verdict + A-escalation is Charlie's read at the gate."""
from __future__ import annotations

import pytest

import backtest.pathb_earned_negative as en


def _ev(per_leg, n_tier5_pass, n_dsr_pass, side_effect=False):
    return en.assemble_evidence(
        per_leg=per_leg,
        n_tier5_pass=n_tier5_pass,
        n_dsr_pass=n_dsr_pass,
        step0_promotion_side_effect=side_effect,
    )


def test_mechanism_refuted_when_all_legs_insane():
    ev = _ev({"h2_low_leg_sane": False, "h2_high_leg_sane": False,
              "h1_sane": False, "h3_sane": False}, n_tier5_pass=0, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.MECHANISM_REFUTED
    assert ev["is_earned_negative"] is True


def test_process_refuted_when_sane_but_no_tier5_pass():
    # Keyed on Tier-5 holdout_sharpe>0 (n_tier5_pass), NOT DSR pass_B.
    ev = _ev({"h2_low_leg_sane": True, "h2_high_leg_sane": False,
              "h1_sane": False, "h3_sane": False}, n_tier5_pass=0, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.PROCESS_REFUTED_FOR_GRID
    assert ev["is_earned_negative"] is True


def test_b_positive_when_a_variant_clears_tier5_even_if_dsr_fails():
    # Spec §9: B-positive = >=1 variant clears Tier-5 holdout_sharpe>0, even if it
    # later fails DSR-FWER (n_dsr_pass=0). NOT an earned negative; weak (small-N*).
    ev = _ev({"h2_low_leg_sane": True, "h2_high_leg_sane": True,
              "h1_sane": True, "h3_sane": True}, n_tier5_pass=1, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.B_POSITIVE
    assert ev["is_earned_negative"] is False
    assert ev["b_positive_strength"] == "weak_needs_2025_oos"


def test_b_positive_strong_when_dsr_passes():
    ev = _ev({"h1_sane": True}, n_tier5_pass=2, n_dsr_pass=1)
    assert ev["advisory_taxonomy"] == en.B_POSITIVE
    assert ev["b_positive_strength"] == "dsr_promoted"


def test_promotion_side_effect_true_is_a_hard_error():
    # Step 0 / 23 guarantees read-only; a True side effect invalidates the run.
    with pytest.raises(ValueError, match="promotion_side_effect"):
        _ev({"h1_sane": True}, n_tier5_pass=0, n_dsr_pass=0, side_effect=True)


def test_bundle_is_advisory_not_a_fired_decision():
    ev = _ev({"h1_sane": True}, n_tier5_pass=0, n_dsr_pass=0)
    assert "escalate" not in ev  # no fired action
    assert ev["verdict_authority"] == "charlie_register_at_earned_negative_gate"


def test_assemble_evidence_carries_pinned_tempers():
    from backtest.pathb_earned_negative import APPROXIMATION_TEMPERS
    out = _ev({"h1_sane": True}, n_tier5_pass=0, n_dsr_pass=0)
    # the pinned, data-independent build approximations must be in the bundle
    assert out["approximation_tempers"] == list(APPROXIMATION_TEMPERS)
    assert any("sizing" in t for t in out["approximation_tempers"])
    assert any("exit" in t for t in out["approximation_tempers"])
