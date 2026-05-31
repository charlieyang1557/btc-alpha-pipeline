# backtest/patha_escalation.py
"""Next-axis (Objective-A) escalation ADVISORY for Path A (NOT an auto-fire).

Per LOCK Pre-registration 4, next-axis escalation (the next crypto-native data
axes — open interest, perp-spot basis, liquidations — plus short legs and
continuous/funding-scaled sizing) is warranted iff BOTH: (i) the funding cycle is
a PROCESS_REFUTED_FOR_GRID earned negative (no variant cleared Tier-5
holdout_sharpe>0 under the cost-aware + min-trade + ternary-sizing process), AND
(ii) no funding variant lifted above DSR-significance.

KEY ADAPTATION FROM Path B (advisor F3): Path A has NO Step-0 diagnostic. Path B's
escalation second prong keyed on a read-only Step-0 re-score of the dead-18 OHLCV
cohort lifting a candidate above pass_B. Path A is a FRESH funding cohort with no
prior cohort to re-score, so the second prong instead keys on
``n_dsr_pass == 0`` — i.e. no funding variant in the N*=3 grid itself reached
DSR-significance (pass_B). This mirrors the Charlie-registered §9 AMENDMENT that
"a lift" requires DSR-SIGNIFICANCE (pass_B / PSR >= 0.95), not a point estimate.

  PROCESS_REFUTED_FOR_GRID + n_dsr_pass == 0 -> warranted (advisory).
  PROCESS_REFUTED_FOR_GRID + n_dsr_pass  > 0 -> NOT warranted (a funding variant
                                                reached significance; re-evaluate
                                                funding before the next axis).
  MECHANISM_REFUTED -> NOT warranted (edge absent at the mechanism level; the
                       next-cheapest move is different mechanisms, not data).
  B_POSITIVE -> NOT warranted (the funding process produced a Tier-5 survivor; the
                next axis is optional upside; Charlie re-evaluates; weak
                B-positives need 2025 OOS confirmation first).

This module only ADVISES; the actual escalation is a Charlie register-event.
"""
from __future__ import annotations

from backtest.patha_earned_negative import (
    B_POSITIVE,
    MECHANISM_REFUTED,
    PROCESS_REFUTED_FOR_GRID,
)

REASON_PROCESS_REFUTED_WARRANTS = "process_refuted_and_no_dsr_pass_warrants_next_axis"
REASON_DSR_PASS = "a_funding_variant_passed_dsr_reevaluate_funding_first"
REASON_MECHANISM_REFUTED_DIFFERENT_AXIS = "mechanism_refuted_next_step_is_mechanisms_not_data"
REASON_B_POSITIVE_NEXT_AXIS_OPTIONAL = "b_positive_next_axis_optional_charlie_reevaluates"


def a_escalation_advisory(taxonomy: str, n_dsr_pass: int) -> dict:
    """Advise whether next-axis escalation is warranted (Charlie fires it).

    Args:
        taxonomy: A patha_earned_negative taxonomy constant.
        n_dsr_pass: # funding variants passing DSR-FWER (``pass_B``). The LOCK §4
            A-trigger's second prong: a funding variant reaching DSR-significance
            (n_dsr_pass > 0) means the funding axis is NOT yet exhausted.

    Returns:
        An ADVISORY dict: ``a_escalation_warranted`` (bool), ``reason``, and
        ``authority="charlie_register"``. This module NEVER fires the escalation.

    Raises:
        ValueError: If ``taxonomy`` is unknown.
    """
    if taxonomy not in (MECHANISM_REFUTED, PROCESS_REFUTED_FOR_GRID, B_POSITIVE):
        raise ValueError(f"unknown taxonomy {taxonomy!r}")

    if taxonomy == PROCESS_REFUTED_FOR_GRID:
        if n_dsr_pass > 0:
            warranted, reason = False, REASON_DSR_PASS
        else:
            warranted, reason = True, REASON_PROCESS_REFUTED_WARRANTS
    elif taxonomy == MECHANISM_REFUTED:
        warranted, reason = False, REASON_MECHANISM_REFUTED_DIFFERENT_AXIS
    else:  # B_POSITIVE
        warranted, reason = False, REASON_B_POSITIVE_NEXT_AXIS_OPTIONAL

    return {
        "a_escalation_warranted": warranted,
        "reason": reason,
        "authority": "charlie_register",
    }
