# backtest/pathb_escalation.py
"""Objective-A escalation ADVISORY (NOT an auto-fire).

Per spec §9, escalation to Objective A (crypto-native data: funding/OI/basis/
liquidations) is warranted iff BOTH: (i) Path B is a PROCESS_REFUTED_FOR_GRID
earned negative (no variant cleared Tier-5 holdout_sharpe>0 under the cost-aware
+ min-trade + ternary-sizing process), AND (ii) the Step-0 cost-aware re-score
lifted NO dead candidate above 0. This module only ADVISES; per the
authorization discipline the actual escalation is a Charlie register-event — an
automated trigger is exactly where the falsification polarity kept inverting.

  PROCESS_REFUTED_FOR_GRID + no Step-0 lift -> warranted (advisory).
  PROCESS_REFUTED_FOR_GRID + Step-0 lifted  -> NOT warranted (process fix may
                                               still rescue OHLCV).
  MECHANISM_REFUTED -> NOT warranted (edge absent at the mechanism level; the
                       next-cheapest axis is different mechanisms, not data).
  B_POSITIVE -> NOT warranted (OHLCV process produced a Tier-5 survivor; A is
                optional upside, Charlie re-evaluates; weak B-positives need
                2025 OOS confirmation first, §8).
"""
from __future__ import annotations

from backtest.pathb_earned_negative import (
    B_POSITIVE,
    MECHANISM_REFUTED,
    PROCESS_REFUTED_FOR_GRID,
)

REASON_PROCESS_REFUTED_WARRANTS = "process_refuted_and_no_step0_lift_warrants_A"
REASON_STEP0_LIFTED = "step0_lifted_a_candidate_process_fix_may_rescue_ohlcv"
REASON_MECHANISM_REFUTED_DIFFERENT_AXIS = "mechanism_refuted_next_axis_is_mechanisms_not_data"
REASON_B_POSITIVE_A_OPTIONAL = "b_positive_a_optional_charlie_reevaluates"


def a_escalation_advisory(taxonomy: str, step0_lifted_any: bool) -> dict:
    """Advise whether Objective-A escalation is warranted (Charlie fires it).

    Args:
        taxonomy: A Task 29 taxonomy constant.
        step0_lifted_any: True iff Step-0 lifted any dead candidate above 0
            (the §9 A-trigger's second prong).

    Returns:
        An ADVISORY dict: ``a_escalation_warranted`` (bool), ``reason``, and
        ``authority="charlie_register"``. This module NEVER fires the escalation.

    Raises:
        ValueError: If ``taxonomy`` is unknown.
    """
    if taxonomy not in (MECHANISM_REFUTED, PROCESS_REFUTED_FOR_GRID, B_POSITIVE):
        raise ValueError(f"unknown taxonomy {taxonomy!r}")

    if taxonomy == PROCESS_REFUTED_FOR_GRID:
        if step0_lifted_any:
            warranted, reason = False, REASON_STEP0_LIFTED
        else:
            warranted, reason = True, REASON_PROCESS_REFUTED_WARRANTS
    elif taxonomy == MECHANISM_REFUTED:
        warranted, reason = False, REASON_MECHANISM_REFUTED_DIFFERENT_AXIS
    else:  # B_POSITIVE
        warranted, reason = False, REASON_B_POSITIVE_A_OPTIONAL

    return {
        "a_escalation_warranted": warranted,
        "reason": reason,
        "authority": "charlie_register",
    }
