# tests/test_pathc_escalation.py
"""Path C next-axis (Objective-C) escalation ADVISORY: warranted iff
process-refuted negative AND no basis variant lifted above DSR-significance
(n_dsr_pass == 0). Advisory only — the actual escalation to the next
crypto-native axis (OI / liquidations / short legs / basis-scaled sizing) is a
Charlie register-event.

Adapted from tests/test_patha_escalation.py. Sub-fix 1b: Path C has NO Step-0
diagnostic (Path C is a FRESH basis cohort; no prior dead cohort to re-score).
The escalation second prong keys on n_dsr_pass == 0, NOT on any step0 re-score.
Signature: c_escalation_advisory(taxonomy, n_dsr_pass).
"""
from __future__ import annotations

import pytest

import backtest.pathc_escalation as esc
import backtest.pathc_earned_negative as en


def test_warranted_on_process_refuted_and_no_dsr_pass():
    """Sub-fix 1b: n_dsr_pass==0 (no basis variant reached DSR-significance) -> warranted."""
    adv = esc.c_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, n_dsr_pass=0)
    assert adv["c_escalation_warranted"] is True
    assert adv["reason"] == esc.REASON_PROCESS_REFUTED_WARRANTS
    assert adv["authority"] == "charlie_register"


def test_not_warranted_if_a_basis_variant_passed_dsr():
    """Sub-fix 1b: n_dsr_pass>0 (a basis variant lifted above pass_B) -> NOT warranted."""
    adv = esc.c_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, n_dsr_pass=1)
    assert adv["c_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_DSR_PASS


def test_not_warranted_on_mechanism_refuted():
    adv = esc.c_escalation_advisory(
        taxonomy=en.MECHANISM_REFUTED, n_dsr_pass=0)
    assert adv["c_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_MECHANISM_REFUTED_DIFFERENT_AXIS


def test_not_warranted_on_c_positive():
    adv = esc.c_escalation_advisory(
        taxonomy=en.C_POSITIVE, n_dsr_pass=0)
    assert adv["c_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_C_POSITIVE_NEXT_AXIS_OPTIONAL


def test_advisory_never_fires_an_action():
    adv = esc.c_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, n_dsr_pass=0)
    assert adv["authority"] == "charlie_register"
    assert "fired" not in adv and "executed" not in adv


def test_unknown_taxonomy_raises():
    with pytest.raises(ValueError, match="unknown taxonomy"):
        esc.c_escalation_advisory(taxonomy="bogus", n_dsr_pass=0)
