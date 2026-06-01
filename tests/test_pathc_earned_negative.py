# tests/test_pathc_earned_negative.py
"""Path C earned-negative EVIDENCE bundle (advisory): keyed on Tier-5
holdout_sharpe>0, NOT DSR pass_B. The binding verdict + C-escalation is Charlie's
read at the gate.

Adapted from tests/test_patha_earned_negative.py. The per-leg argument carries
the C5 tiered (strong_sane/weak_sane/refuted) tier per basis leg.

Sub-fix 1c (F3 under-determined carve-out): an under-floor leg that returns a
thin-sample non-negative forward Sharpe (trade count < UNDER_DETERMINED_TRADE_THRESHOLD
AND holdout_sharpe >= 0) is tagged under_determined=True and NOT folded into the
earned-negative. Under-floor + measured loss IS folded as a substantive negative.

Sub-fix 1d (tier threading): verdict_rests_on_weak_sane_only=True when
any_mechanism_sane rests SOLELY on weak-sane legs.
"""
from __future__ import annotations

import pytest

import backtest.pathc_earned_negative as en


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
# Basic taxonomy (mirrors patha)
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


def test_c_positive_when_a_variant_clears_tier5_even_if_dsr_fails():
    ev = _ev({"H1": _leg("strong_sane"), "H2": _leg("weak_sane"), "H3": _leg("strong_sane")},
             n_tier5_pass=1, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.C_POSITIVE
    assert ev["is_earned_negative"] is False
    assert ev["c_positive_strength"] == "weak_needs_2025_oos"


def test_c_positive_strong_when_dsr_passes():
    ev = _ev({"H1": _leg("strong_sane")}, n_tier5_pass=2, n_dsr_pass=1)
    assert ev["advisory_taxonomy"] == en.C_POSITIVE
    assert ev["c_positive_strength"] == "dsr_promoted"


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
    # Path C basis tempers reference basis native-1h and the F3 carve-out.
    assert any("basis" in t for t in out["approximation_tempers"])
    assert any("f3" in t.lower() or "under_determined" in t.lower()
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
# Sub-fix 1c: F3 under-determined carve-out
# ---------------------------------------------------------------------------

def test_f3_under_floor_measured_loss_is_substantive_negative_not_under_determined():
    """Sub-fix 1c (a): under-floor + measured forward LOSS -> NOT under_determined.

    A floor-ineligible leg with holdout_sharpe < 0 (measured loss) IS a substantive
    negative and IS folded into the earned-negative via taxonomy. It is NOT marked
    under_determined because the signal is directionally clear (loss), not vacuous.
    """
    # H2 is under-floor (eligible=False) but has a measured loss -> substantive negative.
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": False},  # NOT under-determined (measured loss)
    )
    # Taxonomy driven by tier-5 and mechanism-sanity, not under_determined_flags:
    assert ev["advisory_taxonomy"] == en.PROCESS_REFUTED_FOR_GRID
    assert ev["is_earned_negative"] is True
    # H2 is not in the under_determined_legs dict.
    assert "H2" not in ev["under_determined_legs"]


def test_f3_under_floor_thin_sample_nonnegative_is_under_determined():
    """Sub-fix 1c (b): under-floor + thin-sample non-negative -> under_determined.

    A floor-ineligible leg with holdout_sharpe >= 0 AND too few trades to support
    a substantive read is tagged under_determined=True (power gap), NOT folded into
    the earned-negative, and surfaced in the advisory bundle.
    """
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted"), "H3": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": True},  # under-determined (thin + non-negative)
    )
    # Under-determined flag is surfaced in the advisory bundle.
    assert ev["under_determined_legs"].get("H2") is True


def test_f3_under_determined_legs_empty_when_no_flags():
    ev = _ev({"H1": _leg("strong_sane")}, n_tier5_pass=0, n_dsr_pass=0)
    assert ev["under_determined_legs"] == {}


def test_f3_threshold_constant_is_preregistered():
    assert en.UNDER_DETERMINED_TRADE_THRESHOLD == 10


# ---------------------------------------------------------------------------
# GAP 3 (F3 headline caveat): earned_negative_power_limited flag
# ---------------------------------------------------------------------------

def test_earned_negative_power_limited_true_when_any_under_determined():
    """GAP 3: assemble_evidence sets earned_negative_power_limited=True and provides
    a non-None note when at least one leg is under_determined."""
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": True},
    )
    assert ev["earned_negative_power_limited"] is True
    assert ev["earned_negative_power_limited_note"] is not None
    assert len(ev["earned_negative_power_limited_note"]) > 0


def test_earned_negative_power_limited_false_when_no_under_determined():
    """GAP 3: assemble_evidence sets earned_negative_power_limited=False and note=None
    when no legs are under-determined."""
    ev = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": False},
    )
    assert ev["earned_negative_power_limited"] is False
    assert ev["earned_negative_power_limited_note"] is None


def test_earned_negative_power_limited_false_when_flags_empty():
    """GAP 3: with no under_determined_flags at all, flag must be False."""
    ev = _ev(
        {"H1": _leg("strong_sane")},
        n_tier5_pass=0, n_dsr_pass=0,
    )
    assert ev["earned_negative_power_limited"] is False
    assert ev["earned_negative_power_limited_note"] is None


def test_earned_negative_power_limited_does_not_change_taxonomy():
    """GAP 3: the power-limited flag must NEVER change the advisory_taxonomy decision.
    It is a clarity flag only — the taxonomy is driven by n_tier5_pass and mechanism-sanity."""
    # Without under-determined flag.
    ev_clean = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
    )
    # With under-determined flag on H2.
    ev_flagged = _ev(
        {"H1": _leg("strong_sane"), "H2": _leg("refuted")},
        n_tier5_pass=0, n_dsr_pass=0,
        under_determined_flags={"H2": True},
    )
    # Taxonomy must be identical; only the power-limited flags differ.
    assert ev_clean["advisory_taxonomy"] == ev_flagged["advisory_taxonomy"]
    assert ev_clean["is_earned_negative"] == ev_flagged["is_earned_negative"]
    assert ev_flagged["earned_negative_power_limited"] is True
    assert ev_clean["earned_negative_power_limited"] is False
