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

# Pinned BEFORE any data-touch (these describe build-pinned approximations of
# the Step -1 LOCK, not results). Surfaced in the advisory bundle so Charlie's
# §9 earned-negative read sees every conclusiveness temper in ONE place rather
# than buried in spec prose (advisor Points 2/5; METHODOLOGY_NOTES §6).
APPROXIMATION_TEMPERS = (
    # Decision 1: LOCK named a 2-factor sizing; realized single-factor cdf ladder.
    "sizing_single_factor_cdf_vs_locked_2factor",
    # H2 exit: regime-flip cross only (+ time-stop); the spec §5.2 natural
    # OR-exit's zscore-reverts leg was approximated away; 15bps cdf-0.5
    # boundary-whipsaw is a known downward pressure on H2 holdout_sharpe.
    "h2_exit_regime_flip_only_vs_natural_or_zscore_reverts",
    # Mechanism-sanity uses a uniform 1-bar forward-return horizon for all legs:
    # apt for the reversion legs (H1, H2-LOW) but conservative-to-pessimistic for
    # the trend legs (H2-HIGH, H3) whose edge accrues over the 24/48-bar hold (a
    # 1-bar conditional sign can under-credit a real trend; advisor MED). Bounded:
    # MECHANISM_REFUTED needs ALL legs to fail, so a sane reversion leg downgrades
    # to PROCESS_REFUTED; mechanism sanity never gates Tier-5.
    "mechanism_sanity_uniform_1bar_horizon_pessimistic_for_trend_legs",
)
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
        echoed inputs, ``verdict_authority`` naming Charlie as the binding
        decider, and ``approximation_tempers`` (the pinned build-approximation
        tempers; data-independent, set at build time per METHODOLOGY_NOTES §6).
        It NEVER returns a fired action.

        Note: A B-negative result (especially process-refuted) under the
        current approximation tempers is marginally less conclusive (F3 temper),
        as both the sizing (single-factor vs LOCK's 2-factor) and the H2 exit
        (regime-flip only vs natural OR-zscore-reverts) are approximated.

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
        # Build-pinned approximation tempers (data-independent; carried for the
        # §9 advisory read so Charlie sees every conclusiveness caveat in one
        # place — METHODOLOGY_NOTES §6 + B2 advisor Points 2/5).
        "approximation_tempers": list(APPROXIMATION_TEMPERS),
    }
