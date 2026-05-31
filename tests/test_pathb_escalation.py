# tests/test_pathb_escalation.py
"""A-escalation ADVISORY: warranted iff process-refuted negative AND Step-0 no-lift.
Advisory only — the actual escalation to Objective A is a Charlie register-event."""
from __future__ import annotations

import pytest

import backtest.pathb_escalation as esc
import backtest.pathb_earned_negative as en


def test_warranted_on_process_refuted_and_no_step0_lift():
    adv = esc.a_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, step0_lifted_any=False)
    assert adv["a_escalation_warranted"] is True
    assert adv["reason"] == esc.REASON_PROCESS_REFUTED_WARRANTS
    assert adv["authority"] == "charlie_register"


def test_not_warranted_if_step0_lifted_someone():
    # §9 A-trigger 2nd prong: Step-0 cost-aware re-score lifted a dead candidate
    # -> the process fix may still rescue OHLCV -> A not yet warranted.
    adv = esc.a_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, step0_lifted_any=True)
    assert adv["a_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_STEP0_LIFTED


def test_not_warranted_on_mechanism_refuted():
    adv = esc.a_escalation_advisory(
        taxonomy=en.MECHANISM_REFUTED, step0_lifted_any=False)
    assert adv["a_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_MECHANISM_REFUTED_DIFFERENT_AXIS


def test_not_warranted_on_b_positive():
    # B-positive = OHLCV process produced a Tier-5 survivor; A is optional upside,
    # Charlie re-evaluates. Never an automatic escalation.
    adv = esc.a_escalation_advisory(
        taxonomy=en.B_POSITIVE, step0_lifted_any=False)
    assert adv["a_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_B_POSITIVE_A_OPTIONAL


def test_advisory_never_fires_an_action():
    adv = esc.a_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, step0_lifted_any=False)
    assert adv["authority"] == "charlie_register"
    assert "fired" not in adv and "executed" not in adv


def test_unknown_taxonomy_raises():
    with pytest.raises(ValueError, match="unknown taxonomy"):
        esc.a_escalation_advisory(taxonomy="bogus", step0_lifted_any=False)
