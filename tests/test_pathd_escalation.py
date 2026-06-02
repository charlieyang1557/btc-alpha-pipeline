# tests/test_pathd_escalation.py
"""Path D next-axis (Objective-D) escalation ADVISORY: warranted iff
process-refuted negative AND no OI variant lifted above DSR-significance
(n_dsr_pass == 0). Advisory only — the actual escalation to the next axis
is a Charlie register-event.

Adapted from tests/test_pathc_escalation.py. Path D has NO Step-0 (fresh OI
cohort; no prior dead cohort to re-score). The escalation second prong keys on
n_dsr_pass == 0. Signature: d_escalation_advisory(taxonomy, n_dsr_pass).
"""
from __future__ import annotations

import pytest

import backtest.pathd_escalation as esc
import backtest.pathd_earned_negative as en


def test_warranted_on_process_refuted_and_no_dsr_pass():
    """n_dsr_pass==0 (no OI variant reached DSR-significance) -> warranted."""
    adv = esc.d_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, n_dsr_pass=0)
    assert adv["d_escalation_warranted"] is True
    assert adv["reason"] == esc.REASON_PROCESS_REFUTED_WARRANTS
    assert adv["authority"] == "charlie_register"


def test_not_warranted_if_an_oi_variant_passed_dsr():
    """n_dsr_pass>0 (an OI variant lifted above pass_B) -> NOT warranted."""
    adv = esc.d_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, n_dsr_pass=1)
    assert adv["d_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_DSR_PASS


def test_not_warranted_on_mechanism_refuted():
    adv = esc.d_escalation_advisory(
        taxonomy=en.MECHANISM_REFUTED, n_dsr_pass=0)
    assert adv["d_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_MECHANISM_REFUTED_DIFFERENT_AXIS


def test_not_warranted_on_d_positive():
    adv = esc.d_escalation_advisory(
        taxonomy=en.D_POSITIVE, n_dsr_pass=0)
    assert adv["d_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_D_POSITIVE_NEXT_AXIS_OPTIONAL


def test_advisory_never_fires_an_action():
    adv = esc.d_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, n_dsr_pass=0)
    assert adv["authority"] == "charlie_register"
    assert "fired" not in adv and "executed" not in adv


def test_unknown_taxonomy_raises():
    with pytest.raises(ValueError, match="unknown taxonomy"):
        esc.d_escalation_advisory(taxonomy="bogus", n_dsr_pass=0)


# ---------------------------------------------------------------------------
# FIX 2: §37.3 substantive-vs-vacuous escalation gating
# ---------------------------------------------------------------------------

def test_warranted_on_substantive_basis_and_no_dsr_pass():
    """§37.3 (a): >=1 measured-loss leg + 0 DSR pass -> escalation warranted."""
    adv = esc.d_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID,
        n_dsr_pass=0,
        negative_has_substantive_basis=True,
    )
    assert adv["d_escalation_warranted"] is True
    assert adv["reason"] == esc.REASON_PROCESS_REFUTED_WARRANTS


def test_not_warranted_on_vacuous_only_negative():
    """§37.3 (b): all legs under-determined (no measured loss) -> escalation NOT warranted.
    The verdict hedges: 'OI not actually tested on this grid', NOT 'OI is dead'."""
    adv = esc.d_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID,
        n_dsr_pass=0,
        negative_has_substantive_basis=False,
    )
    assert adv["d_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_VACUOUS_ONLY_NOT_WARRANTED


def test_default_substantive_basis_preserves_backward_compat():
    """When negative_has_substantive_basis is not provided (default True),
    behavior is unchanged from pre-fix (escalation warranted on process_refuted + 0 dsr)."""
    adv = esc.d_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID,
        n_dsr_pass=0,
        # negative_has_substantive_basis defaults to True
    )
    assert adv["d_escalation_warranted"] is True
