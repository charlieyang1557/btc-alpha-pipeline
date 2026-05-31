# tests/test_patha_earned_negative.py
"""Path A earned-negative EVIDENCE bundle (advisory): keyed on Tier-5
holdout_sharpe>0, NOT DSR pass_B. The binding verdict + A-escalation is Charlie's
read at the gate.

Adapted from tests/test_pathb_earned_negative.py; the per-leg argument now carries
the C5 tiered (strong_sane/weak_sane/refuted) tier per funding leg (advisor F4),
and assemble_evidence sets verdict_rests_on_weak_sane_only=True when
any_mechanism_sane rests SOLELY on weak-sane legs.
"""
from __future__ import annotations

import pytest

import backtest.patha_earned_negative as en


def _ev(per_leg, n_tier5_pass, n_dsr_pass, side_effect=False):
    return en.assemble_evidence(
        per_leg=per_leg,
        n_tier5_pass=n_tier5_pass,
        n_dsr_pass=n_dsr_pass,
        promotion_side_effect=side_effect,
    )


# Per-leg tier dicts (mirror C5 classify_leg output: {"tier": ...}).
def _leg(tier):
    return {"tier": tier}


def test_mechanism_refuted_when_all_legs_refuted():
    ev = _ev({"H1": _leg("refuted"), "H2": _leg("refuted"), "H3": _leg("refuted")},
             n_tier5_pass=0, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.MECHANISM_REFUTED
    assert ev["is_earned_negative"] is True
    assert ev["any_mechanism_sane"] is False
    assert ev["verdict_rests_on_weak_sane_only"] is False


def test_process_refuted_when_strong_sane_but_no_tier5_pass():
    # >=1 leg mechanism-sane (strong), no Tier-5 holdout_sharpe>0 -> process-refuted.
    ev = _ev({"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
             n_tier5_pass=0, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.PROCESS_REFUTED_FOR_GRID
    assert ev["is_earned_negative"] is True
    assert ev["any_mechanism_sane"] is True
    # A strong-sane leg is present -> verdict does NOT rest on weak-sane only.
    assert ev["verdict_rests_on_weak_sane_only"] is False


def test_verdict_rests_on_weak_sane_only_when_sole_sane_is_weak():
    # The ONLY sane leg is weak_sane -> flag the conclusiveness caveat.
    ev = _ev({"H1": _leg("weak_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
             n_tier5_pass=0, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.PROCESS_REFUTED_FOR_GRID
    assert ev["any_mechanism_sane"] is True
    assert ev["verdict_rests_on_weak_sane_only"] is True


def test_b_positive_when_a_variant_clears_tier5_even_if_dsr_fails():
    ev = _ev({"H1": _leg("strong_sane"), "H2": _leg("weak_sane"), "H3": _leg("strong_sane")},
             n_tier5_pass=1, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.B_POSITIVE
    assert ev["is_earned_negative"] is False
    assert ev["b_positive_strength"] == "weak_needs_2025_oos"


def test_b_positive_strong_when_dsr_passes():
    ev = _ev({"H1": _leg("strong_sane")}, n_tier5_pass=2, n_dsr_pass=1)
    assert ev["advisory_taxonomy"] == en.B_POSITIVE
    assert ev["b_positive_strength"] == "dsr_promoted"


def test_promotion_side_effect_true_is_a_hard_error():
    with pytest.raises(ValueError, match="promotion_side_effect"):
        _ev({"H1": _leg("strong_sane")}, n_tier5_pass=0, n_dsr_pass=0, side_effect=True)


def test_bundle_is_advisory_not_a_fired_decision():
    ev = _ev({"H1": _leg("strong_sane")}, n_tier5_pass=0, n_dsr_pass=0)
    assert "escalate" not in ev  # no fired action
    assert ev["verdict_authority"] == "charlie_register_at_earned_negative_gate"


def test_assemble_evidence_carries_pinned_tempers():
    out = _ev({"H1": _leg("strong_sane")}, n_tier5_pass=0, n_dsr_pass=0)
    assert out["approximation_tempers"] == list(en.APPROXIMATION_TEMPERS)
    # Path A funding tempers reference the funding-marginal + causal-carry caveats.
    assert any("funding" in t for t in out["approximation_tempers"])


def test_accepts_bare_string_tiers_too():
    # per_leg values may be the bare tier string OR a {"tier": ...} dict.
    ev = _ev({"H1": "weak_sane", "H2": "refuted", "H3": "refuted"},
             n_tier5_pass=0, n_dsr_pass=0)
    assert ev["any_mechanism_sane"] is True
    assert ev["verdict_rests_on_weak_sane_only"] is True
