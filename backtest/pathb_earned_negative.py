# backtest/pathb_earned_negative.py
"""Earned-negative EVIDENCE bundle for the Path B grid (ADVISORY).

This module ASSEMBLES the evidence for the earned-negative read; it does NOT
fire any operational decision. Per the authorization discipline, the binding
taxonomy verdict AND the A-escalation are Charlie's register at the
earned-negative gate — an automated trigger is exactly where the falsification
polarity kept inverting.

Taxonomy (spec §9), keyed on Tier-5 ``holdout_sharpe > 0`` (NOT DSR pass_B):
  MECHANISM_REFUTED        — NO leg's conditional forward-return sign matched its
                             hypothesized direction (edge absent at the mechanism
                             level). Earned negative.
  PROCESS_REFUTED_FOR_GRID — >=1 leg mechanism-sane, but NO variant clears Tier-5
                             holdout_sharpe>0 — refuted for THIS grid/cost, not the
                             mechanism in general. Earned negative.
  B_POSITIVE               — >=1 variant clears Tier-5 holdout_sharpe>0 (spec §9
                             B-positive), even if it then fails DSR-FWER. NOT an
                             earned negative. Strength: 'weak_needs_2025_oos' if no
                             DSR pass (small-N* bar is easier, §8); 'dsr_promoted'
                             if >=1 DSR pass_B.

A True Step-0 promotion side effect is a hard error (Task 23 guarantees the
re-score is read-only).
"""
from __future__ import annotations

MECHANISM_REFUTED = "mechanism_refuted"
PROCESS_REFUTED_FOR_GRID = "process_refuted_for_this_grid"
B_POSITIVE = "b_positive"

# The per-leg / per-hypothesis sanity keys this bundle consumes.
_SANITY_KEYS = (
    "h2_low_leg_sane",
    "h2_high_leg_sane",
    "h1_sane",
    "h3_sane",
)


def assemble_evidence(
    per_leg: dict,
    n_tier5_pass: int,
    n_dsr_pass: int,
    step0_promotion_side_effect: bool,
) -> dict:
    """Assemble the (advisory) earned-negative evidence bundle.

    Args:
        per_leg: Task 26 per-leg + per-hypothesis sanity booleans.
        n_tier5_pass: # variants clearing Tier-5 ``holdout_sharpe > 0`` at 15bps
            (the spec §9 B-positive / process-refuted KEY — NOT DSR pass_B).
        n_dsr_pass: # variants passing DSR-FWER (Task 28 ``pass_B``) — the stronger
            promotion signal WITHIN B-positive.
        step0_promotion_side_effect: Task 23 read-only flag (MUST be False).

    Returns:
        An advisory dict: ``advisory_taxonomy`` (one of the 3 constants),
        ``is_earned_negative`` (bool), ``b_positive_strength`` (or None), the
        echoed inputs, and ``verdict_authority`` naming Charlie as the binding
        decider. It NEVER returns a fired action.

    Raises:
        ValueError: If ``step0_promotion_side_effect`` is True.
    """
    if step0_promotion_side_effect:
        raise ValueError(
            "promotion_side_effect=True: the Step-0 re-score must be read-only "
            "(Task 23); a side effect invalidates the earned-negative evidence."
        )

    any_mechanism_sane = any(bool(per_leg.get(k, False)) for k in _SANITY_KEYS)

    if n_tier5_pass >= 1:
        taxonomy = B_POSITIVE
        is_earned_negative = False
        strength = "dsr_promoted" if n_dsr_pass >= 1 else "weak_needs_2025_oos"
    elif not any_mechanism_sane:
        taxonomy = MECHANISM_REFUTED
        is_earned_negative = True
        strength = None
    else:
        taxonomy = PROCESS_REFUTED_FOR_GRID
        is_earned_negative = True
        strength = None

    return {
        "advisory_taxonomy": taxonomy,
        "is_earned_negative": is_earned_negative,
        "b_positive_strength": strength,
        "any_mechanism_sane": any_mechanism_sane,
        "n_tier5_pass": int(n_tier5_pass),
        "n_dsr_pass": int(n_dsr_pass),
        "verdict_authority": "charlie_register_at_earned_negative_gate",
    }
