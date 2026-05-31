# backtest/patha_earned_negative.py
"""Earned-negative EVIDENCE bundle for the Path A funding grid (ADVISORY).

Adapted from backtest/pathb_earned_negative.py. This module ASSEMBLES the
evidence for the earned-negative read; it does NOT fire any operational decision.
Per the authorization discipline, the binding taxonomy verdict AND the
A-escalation are Charlie's register at the earned-negative gate.

Taxonomy (LOCK Pre-registration 4), keyed on Tier-5 ``holdout_sharpe > 0`` (NOT
DSR pass_B):
  MECHANISM_REFUTED        — NO funding leg's conditional forward-return sign
                             matched its hypothesized direction. Earned negative.
  PROCESS_REFUTED_FOR_GRID — >=1 leg mechanism-sane, but NO variant clears Tier-5
                             holdout_sharpe>0 at 15bps on forward_2026 — refuted
                             for THIS grid/cost, not the funding axis in general.
                             Earned negative.
  B_POSITIVE               — >=1 variant clears Tier-5 holdout_sharpe>0, even if it
                             then fails DSR-FWER. NOT an earned negative. Strength:
                             'weak_needs_2025_oos' if no DSR pass; 'dsr_promoted'
                             if >=1 DSR pass_B.

Tiered mechanism-sanity threading (advisor F4): the per-leg argument carries the
C5 tier (``strong_sane`` / ``weak_sane`` / ``refuted``) per funding leg. A leg is
mechanism-sane iff its tier is ``strong_sane`` or ``weak_sane``;
``verdict_rests_on_weak_sane_only`` is True when ``any_mechanism_sane`` rests
SOLELY on weak-sane legs (>=1 sane leg AND no strong-sane leg) — so a verdict
manufactured by a single-horizon noise flip is flagged for Charlie's §9 read.

A True promotion side effect is a hard error (the harness must be read-only).
"""
from __future__ import annotations

MECHANISM_REFUTED = "mechanism_refuted"
PROCESS_REFUTED_FOR_GRID = "process_refuted_for_this_grid"
B_POSITIVE = "b_positive"

STRONG_SANE = "strong_sane"
WEAK_SANE = "weak_sane"
REFUTED = "refuted"
_SANE_TIERS = (STRONG_SANE, WEAK_SANE)

# Build-pinned approximation tempers for the Path A funding cycle (data-independent;
# carried so Charlie's earned-negative read sees every conclusiveness caveat in ONE
# place per METHODOLOGY_NOTES §6). Distinct from Path B's: Path A's tempers describe
# the funding-axis build approximations, not Path B's OHLCV ones.
APPROXIMATION_TEMPERS = (
    # The fenced funding-marginal diagnostic isolates funding's marginal
    # contribution vs the no-funding baseline, but it is diagnostic-only and never
    # feeds N* or promotion (LOCK Pre-registration 3); a B-negative localizes to
    # {funding-gated + this grid + 15bps cost}, not the funding axis in general.
    "funding_marginal_is_fenced_diagnostic_not_promotion_input",
    # Funding features are computed on the 8h settlement series and carried onto the
    # 1h bar grid by a backward as-of join (discrete carry; ~2160-bar effective
    # warmup). The carried-funding decay-confound is a known temper on attribution.
    "funding_8h_settlement_carry_to_1h_bars_warmup_2160",
    # Mechanism-sanity is measured at 24h AND 72h horizons (tiered strong/weak);
    # a verdict resting on weak-sane-only legs is flagged separately
    # (verdict_rests_on_weak_sane_only) so a single-horizon noise flip cannot
    # silently manufacture mechanism-sanity.
    "mechanism_sanity_tiered_24h_72h_weak_sane_flagged",
)


def _leg_tier(value) -> str:
    """Extract the tier string from a per-leg value (a {"tier": ...} dict or bare str)."""
    if isinstance(value, dict):
        return str(value.get("tier", REFUTED))
    return str(value)


def assemble_evidence(
    per_leg: dict,
    n_tier5_pass: int,
    n_dsr_pass: int,
    promotion_side_effect: bool,
) -> dict:
    """Assemble the (advisory) earned-negative evidence bundle for Path A.

    Args:
        per_leg: Mapping of leg-id -> tier (C5 ``classify_leg`` output dict with a
            ``"tier"`` key, or a bare tier string). Tiers are ``strong_sane`` /
            ``weak_sane`` / ``refuted``.
        n_tier5_pass: # variants clearing Tier-5 ``holdout_sharpe > 0`` at 15bps on
            forward_2026 (the LOCK §4 B-positive / process-refuted KEY — NOT DSR pass_B).
        n_dsr_pass: # variants passing DSR-FWER (``pass_B``) — the stronger promotion
            signal WITHIN B-positive.
        promotion_side_effect: Read-only flag (MUST be False; the harness never
            mutates the sealed cohort or promotion lists).

    Returns:
        An advisory dict: ``advisory_taxonomy`` (one of the 3 constants),
        ``is_earned_negative`` (bool), ``b_positive_strength`` (or None),
        ``any_mechanism_sane``, ``verdict_rests_on_weak_sane_only``, the echoed
        inputs, ``verdict_authority`` naming Charlie as the binding decider, and
        ``approximation_tempers``. It NEVER returns a fired action.

    Raises:
        ValueError: If ``promotion_side_effect`` is True.
    """
    if promotion_side_effect:
        raise ValueError(
            "promotion_side_effect=True: the Path A harness must be read-only; "
            "a side effect invalidates the earned-negative evidence."
        )

    tiers = {k: _leg_tier(v) for k, v in per_leg.items()}
    any_mechanism_sane = any(t in _SANE_TIERS for t in tiers.values())
    any_strong_sane = any(t == STRONG_SANE for t in tiers.values())
    # The verdict rests on weak-sane-only legs iff it IS mechanism-sane but no leg
    # is strong-sane (every sane leg is weak-sane — a single-horizon sign).
    verdict_rests_on_weak_sane_only = bool(any_mechanism_sane and not any_strong_sane)

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
        "verdict_rests_on_weak_sane_only": verdict_rests_on_weak_sane_only,
        "leg_tiers": tiers,
        "n_tier5_pass": int(n_tier5_pass),
        "n_dsr_pass": int(n_dsr_pass),
        "verdict_authority": "charlie_register_at_earned_negative_gate",
        "approximation_tempers": list(APPROXIMATION_TEMPERS),
    }
