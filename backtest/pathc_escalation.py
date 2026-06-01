# backtest/pathc_escalation.py
"""Next-axis (Objective-C) escalation ADVISORY for Path C (NOT an auto-fire).

Per LOCK Pre-registration 4, next-axis escalation (the next crypto-native data
axes — open interest, liquidations, plus short legs and basis-scaled sizing) is
warranted iff BOTH: (i) the basis cycle is a PROCESS_REFUTED_FOR_GRID earned
negative (no variant cleared Tier-5 holdout_sharpe>0 under the cost-aware +
min-trade + ternary-sizing process), AND (ii) no basis variant lifted above
DSR-significance.

Sub-fix 1b: Path C has NO Step-0 diagnostic (Path C is a FRESH basis cohort,
not a re-score of a prior dead cohort). The escalation second prong therefore
keys on ``n_dsr_pass == 0`` — i.e. no basis variant in the N*=3 grid itself
reached DSR-significance (pass_B). This mirrors the Path A precedent (Path A
also keyed on n_dsr_pass == 0 because it was a fresh funding cohort with no
prior cohort to re-score, per the Charlie-registered §9 AMENDMENT).

  PROCESS_REFUTED_FOR_GRID + n_dsr_pass == 0 -> warranted (advisory).
  PROCESS_REFUTED_FOR_GRID + n_dsr_pass  > 0 -> NOT warranted (a basis variant
                                                reached significance; re-evaluate
                                                basis before the next axis).
  MECHANISM_REFUTED -> NOT warranted (edge absent at the mechanism level; the
                       next-cheapest move is different mechanisms, not data).
  C_POSITIVE -> NOT warranted (the basis process produced a Tier-5 survivor; the
                next axis is optional upside; Charlie re-evaluates; weak
                C-positives need 2025 OOS confirmation first).

This module only ADVISES; the actual escalation is a Charlie register-event.
"""
from __future__ import annotations

from backtest.pathc_earned_negative import (
    C_POSITIVE,
    MECHANISM_REFUTED,
    PROCESS_REFUTED_FOR_GRID,
)

REASON_PROCESS_REFUTED_WARRANTS = "process_refuted_and_no_dsr_pass_warrants_next_axis"
REASON_DSR_PASS = "a_basis_variant_passed_dsr_reevaluate_basis_first"
REASON_MECHANISM_REFUTED_DIFFERENT_AXIS = "mechanism_refuted_next_step_is_mechanisms_not_data"
REASON_C_POSITIVE_NEXT_AXIS_OPTIONAL = "c_positive_next_axis_optional_charlie_reevaluates"


def c_escalation_advisory(taxonomy: str, n_dsr_pass: int) -> dict:
    """Advise whether next-axis escalation is warranted (Charlie fires it).

    Sub-fix 1b: prong-(ii) keys on ``n_dsr_pass == 0`` (no basis variant lifted
    above DSR-significance ``pass_B``). Path C has NO Step-0 (fresh basis cohort,
    no prior dead cohort to re-score); the only prong-2 signal is whether any
    variant in the N*=3 grid itself reached significance.

    Args:
        taxonomy: A pathc_earned_negative taxonomy constant.
        n_dsr_pass: # basis variants passing DSR-FWER (``pass_B``). The LOCK §4
            C-trigger's second prong: a basis variant reaching DSR-significance
            (n_dsr_pass > 0) means the basis axis is NOT yet exhausted.

    Returns:
        An ADVISORY dict: ``c_escalation_warranted`` (bool), ``reason``, and
        ``authority="charlie_register"``. This module NEVER fires the escalation.

    Raises:
        ValueError: If ``taxonomy`` is unknown.
    """
    if taxonomy not in (MECHANISM_REFUTED, PROCESS_REFUTED_FOR_GRID, C_POSITIVE):
        raise ValueError(f"unknown taxonomy {taxonomy!r}")

    if taxonomy == PROCESS_REFUTED_FOR_GRID:
        if n_dsr_pass > 0:
            warranted, reason = False, REASON_DSR_PASS
        else:
            warranted, reason = True, REASON_PROCESS_REFUTED_WARRANTS
    elif taxonomy == MECHANISM_REFUTED:
        warranted, reason = False, REASON_MECHANISM_REFUTED_DIFFERENT_AXIS
    else:  # C_POSITIVE
        warranted, reason = False, REASON_C_POSITIVE_NEXT_AXIS_OPTIONAL

    return {
        "c_escalation_warranted": warranted,
        "reason": reason,
        "authority": "charlie_register",
    }
