# backtest/pathd_earned_negative.py
"""Earned-negative EVIDENCE bundle for the Path D OI grid (ADVISORY).

Adapted from backtest/pathc_earned_negative.py. This module ASSEMBLES the
evidence for the earned-negative read; it does NOT fire any operational decision.
Per the authorization discipline, the binding taxonomy verdict AND the
D-escalation are Charlie's register at the earned-negative gate.

Taxonomy (LOCK Pre-registration 4), keyed on Tier-5 ``holdout_sharpe > 0`` (NOT
DSR pass_B):
  MECHANISM_REFUTED        — NO OI leg's conditional forward-return sign
                             matched its hypothesized direction. Earned negative.
  PROCESS_REFUTED_FOR_GRID — >=1 leg mechanism-sane, but NO variant clears Tier-5
                             holdout_sharpe>0 at 15bps on forward_2026 — refuted
                             for THIS grid/cost, not the OI axis in general.
                             Earned negative.
  D_POSITIVE               — >=1 variant clears Tier-5 holdout_sharpe>0, even if it
                             then fails DSR-FWER. NOT an earned negative. Strength:
                             'weak_needs_2025_oos' if no DSR pass; 'dsr_promoted'
                             if >=1 DSR pass_B.

Tiered mechanism-sanity threading: the per-leg argument carries the C5 tier
(``strong_sane`` / ``weak_sane`` / ``refuted``) per OI leg. A leg is
mechanism-sane iff its tier is ``strong_sane`` or ``weak_sane``;
``verdict_rests_on_weak_sane_only`` is True when ``any_mechanism_sane`` rests
SOLELY on weak-sane legs (>=1 sane leg AND no strong-sane leg) — so a verdict
manufactured by a single-horizon noise flip is flagged for Charlie's §9 read.

Under-determined carve-out (generic predicate, §38.3 inheritance):
A leg that is floor-INDETERMINATE (``eligible == False``) AND returns a
thin-sample non-negative forward Sharpe (trade count below the
UNDER_DETERMINED_TRADE_THRESHOLD AND holdout_sharpe >= 0) is tagged
``under_determined=True`` and is NOT folded into the earned-negative. This
predicate is GENERIC — it applies to any floor type (H1 flat-exit-episodes,
H2/H3 zero_fraction/trade-count, H2 de-risk occupancy), NOT zero_fraction-specific
(Path C's F3 carve-out was zero_fraction-specific; Path D generalizes it to
ANY eligible==False floor predicate). The under-determined leg is surfaced in the
advisory bundle as a power gap.

NET-NEW for Path D vs Path C:
- Under-powered-but-SANE H3 annotation: when H3 is under-determined
  (under_determined=True) AND its mechanism-sanity tier is strong_sane or
  weak_sane, ``consistent_with_momentum_or_vol_leakage=True`` is recorded in the
  bundle to flag that the underpowered positive result is CONSISTENT with the OI
  momentum/vol hypothesis — but NOT confirmed (the power gap prevents a substantive
  read). Charlie sees this as: "OI momentum adds no RESCUE here, but the direction
  isn't cleanly refuted — under-powered."

F3 THRESHOLD (pre-registered default): ``UNDER_DETERMINED_TRADE_THRESHOLD = 10``.

Tier threading: the per-leg strong/weak-sane tier from C5
(``pathd_perleg_mechanism``) is threaded into ``assemble_evidence`` to set
``verdict_rests_on_weak_sane_only``.

A True promotion side effect is a hard error (the harness must be read-only).
"""
from __future__ import annotations

MECHANISM_REFUTED = "mechanism_refuted"
PROCESS_REFUTED_FOR_GRID = "process_refuted_for_this_grid"
D_POSITIVE = "d_positive"

STRONG_SANE = "strong_sane"
WEAK_SANE = "weak_sane"
REFUTED = "refuted"
_SANE_TIERS = (STRONG_SANE, WEAK_SANE)

# F3 under-determined trade threshold (generic predicate — applies to ANY
# eligible==False floor, not zero_fraction-specific; inherits the pre-registered
# Path C value, pre-data choice per LOCK §38.3).
UNDER_DETERMINED_TRADE_THRESHOLD = 10

# Build-pinned approximation tempers for the Path D OI cycle (data-independent;
# carried so Charlie's earned-negative read sees every conclusiveness caveat in ONE
# place per METHODOLOGY_NOTES §6).
APPROXIMATION_TEMPERS = (
    # D1 (vs no-OI momentum baseline) is the ONLY orthogonalization diagnostic.
    # D2 is DROPPED — OI is an independent axis with no derived-from relation
    # (unlike basis≈funding). The §38.3 inheritance is fenced-label-read +
    # inert-D1-modal discipline only. contamination_correlations (NET-NEW) measures
    # Pearson/Spearman of oi_velocity_ewm_240 vs return/vol — diagnostic-only,
    # never in N*/promotion.
    "d1_only_no_d2_oi_is_independent_axis",
    # OI factors are heavily NaN in 2024/2025 due to scattered zero-OI-glitch
    # gap-propagation — each zero-OI bar NaNs the entire rolling-2160 (~90d)
    # percentile window containing it, so the NaN is data-driven, not a
    # front-loaded burn-in; forward_2026 (the gate) is 0% NaN. Floor eligibility
    # is computed on the non-NaN subset; this is a known power disclosure, handled
    # gracefully (NaN-is-False DSL compiler invariant).
    "oi_factors_nan_in_2024_2025_floor_on_nonnull_subset",
    # Mechanism-sanity is measured at 24h AND 72h horizons (tiered strong/weak);
    # a verdict resting on weak-sane-only legs is flagged separately
    # (verdict_rests_on_weak_sane_only) so a single-horizon noise flip cannot
    # silently manufacture mechanism-sanity.
    "mechanism_sanity_tiered_24h_72h_weak_sane_flagged",
    # The under-determined carve-out is GENERIC: it applies to ANY eligible==False
    # floor (not zero_fraction-specific like Path C's F3). An underpowered positive
    # on a floor-ineligible H3 is annotated consistent_with_momentum_or_vol_leakage
    # when the leg's mechanism tier is sane — it's a power gap, NOT a confirmed edge.
    "generic_under_determined_carve_out_any_floor_h3_leakage_annotation",
    # H2/H3 are expected-INDETERMINATE on zero_fraction under the OI regime gate:
    # price-trend AND-confirm fires <50% of bars (same structural expectation as
    # Path C). An under-floor leg with thin-sample non-negative Sharpe is tagged
    # under_determined rather than folded into the earned-negative.
    "h2_h3_expected_indeterminate_zero_fraction_generic_f3_carve_out",
)

# OI hypothesis ids (used for the H3 leakage annotation)
_H3_KEY = "H3"


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
    *,
    under_determined_flags: dict | None = None,
    holdout_sharpes: dict | None = None,
) -> dict:
    """Assemble the (advisory) earned-negative evidence bundle for Path D.

    Args:
        per_leg: Mapping of leg-id -> tier (C5 ``classify_leg`` output dict with a
            ``"tier"`` key, or a bare tier string). Tiers are ``strong_sane`` /
            ``weak_sane`` / ``refuted``.
        n_tier5_pass: # variants clearing Tier-5 ``holdout_sharpe > 0`` at 15bps on
            forward_2026 (the LOCK §4 D-positive / process-refuted KEY — NOT DSR pass_B).
        n_dsr_pass: # variants passing DSR-FWER (``pass_B``) — the stronger promotion
            signal WITHIN D-positive.
        promotion_side_effect: Read-only flag (MUST be False; the harness never
            mutates the sealed cohort or promotion lists).
        under_determined_flags: Optional mapping of leg-id -> bool
            (True = this leg is under-determined per the GENERIC carve-out). When
            provided, under-determined legs are surfaced in the advisory bundle as
            power gaps but NOT folded into the earned-negative taxonomy.
        holdout_sharpes: Optional mapping of leg-id -> float holdout Sharpe. Used
            to determine ``n_substantive_loss_legs`` per §37.3: a leg with
            ``holdout_sharpe < 0`` has a MEASURED LOSS (substantive); a leg that is
            under-determined (holdout_sharpe >= 0) does NOT. When None, all eligible
            legs with ``is_earned_negative=True`` are conservatively treated as having
            a substantive basis.

    Returns:
        An advisory dict: ``advisory_taxonomy`` (one of the 3 constants),
        ``is_earned_negative`` (bool), ``d_positive_strength`` (or None),
        ``any_mechanism_sane``, ``verdict_rests_on_weak_sane_only``, the echoed
        inputs, ``verdict_authority`` naming Charlie as the binding decider,
        ``approximation_tempers``, ``under_determined_legs`` (generic carve-out),
        ``consistent_with_momentum_or_vol_leakage`` (True when H3 is under-
        determined AND mechanism-sane — NET-NEW for Path D), and the §37.3
        substantive-vs-vacuous fields: ``n_substantive_loss_legs``,
        ``negative_has_substantive_basis``, ``negative_is_vacuous_only``.
        ``escalation_warranted`` in the returned dict is NOT set here — it lives
        in pathd_escalation.d_escalation_advisory. However the ``advisory_taxonomy``
        and the §37.3 fields together give the escalation module what it needs.
        It NEVER returns a fired action.

    Raises:
        ValueError: If ``promotion_side_effect`` is True.
    """
    if promotion_side_effect:
        raise ValueError(
            "promotion_side_effect=True: the Path D harness must be read-only; "
            "a side effect invalidates the earned-negative evidence."
        )

    tiers = {k: _leg_tier(v) for k, v in per_leg.items()}
    any_mechanism_sane = any(t in _SANE_TIERS for t in tiers.values())
    any_strong_sane = any(t == STRONG_SANE for t in tiers.values())
    # The verdict rests on weak-sane-only legs iff it IS mechanism-sane but no leg
    # is strong-sane (every sane leg is weak-sane — a single-horizon sign).
    verdict_rests_on_weak_sane_only = bool(any_mechanism_sane and not any_strong_sane)

    # Generic under-determined carve-out: record which legs are power-gap flagged.
    ud = under_determined_flags or {}
    under_determined_legs = {k: bool(v) for k, v in ud.items() if v}

    if n_tier5_pass >= 1:
        taxonomy = D_POSITIVE
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

    # F3 headline caveat: when any leg is under-determined, the headline
    # 'is_earned_negative' is power-limited on those legs.
    earned_negative_power_limited = bool(under_determined_legs)
    if earned_negative_power_limited:
        power_limited_note = (
            "One or more legs are UNDER-DETERMINED (floor-ineligible with a thin-sample "
            "non-negative forward Sharpe). 'is_earned_negative' applies to the eligible "
            "legs only; the under-determined legs are power-gap flagged and NOT counted "
            "as substantive negatives. See 'under_determined_legs' for detail."
        )
    else:
        power_limited_note = None

    # §37.3: substantive-vs-vacuous distinction.
    # A leg has a SUBSTANTIVE measured loss if holdout_sharpe < 0. A leg that is
    # under-determined (holdout_sharpe >= 0) does NOT constitute a substantive loss.
    # Note: an under-determined leg has holdout_sharpe >= 0 by definition of the
    # carve-out (see _is_under_determined); a measured-loss leg always has sharpe < 0
    # and is therefore NOT under-determined — the two sets are disjoint.
    if holdout_sharpes is not None:
        n_substantive_loss_legs = sum(
            1 for k, s in holdout_sharpes.items()
            if float(s) < 0.0
        )
    else:
        # Conservative fallback: treat any earned-negative as substantive (no per-leg
        # sharpe provided). This preserves backward-compatibility for callers that do
        # not thread holdout_sharpes.
        n_substantive_loss_legs = int(is_earned_negative)
    negative_has_substantive_basis = (n_substantive_loss_legs >= 1)
    negative_is_vacuous_only = bool(is_earned_negative and not negative_has_substantive_basis)

    # NET-NEW for Path D: under-powered-but-SANE H3 annotation.
    # When H3 is under-determined AND its mechanism tier is sane, record
    # consistent_with_momentum_or_vol_leakage=True: the underpowered positive is
    # consistent with the OI momentum hypothesis, but NOT confirmed.
    h3_tier = tiers.get(_H3_KEY, REFUTED)
    h3_under_determined = bool(under_determined_legs.get(_H3_KEY, False))
    consistent_with_momentum_or_vol_leakage = bool(
        h3_under_determined and h3_tier in _SANE_TIERS
    )

    # Q5: verdict_headline — unmissable top-line summary.
    ud_leg_ids = ", ".join(sorted(under_determined_legs))
    if negative_is_vacuous_only:
        # Vacuity can be degeneracy-driven (0-trade flat legs) OR under-determination-driven
        # (floor-ineligible thin-sample non-negative). Point the reader at BOTH bundle fields
        # generically (advisor B2) — an all-degenerate cohort leaves under_determined_legs
        # empty, so don't direct solely there. (assemble_evidence does not receive
        # degenerate_legs; the orchestrator's bundle carries both fields.)
        verdict_headline = (
            f"{taxonomy.upper()} — VACUOUS-ONLY: no measured forward loss on any leg "
            f"(all legs degenerate and/or under-determined); OI NOT actually tested on this "
            f"grid — see the bundle's degenerate_legs + under_determined_legs for the vacuity source"
        )
    elif earned_negative_power_limited:
        verdict_headline = (
            f"{taxonomy.upper()} — EARNED-NEGATIVE IS POWER-LIMITED "
            f"(under-determined legs: {ud_leg_ids}); "
            f"not a clean negative — see under_determined_legs"
        )
    elif is_earned_negative:
        verdict_headline = f"{taxonomy.upper()} (earned-negative)"
    else:
        # D_POSITIVE: never power-limited, not an earned-negative
        strength_tag = f"; strength={strength}" if strength else ""
        verdict_headline = f"{taxonomy.upper()}{strength_tag}"

    return {
        "advisory_taxonomy": taxonomy,
        "is_earned_negative": is_earned_negative,
        "earned_negative_power_limited": earned_negative_power_limited,
        "earned_negative_power_limited_note": power_limited_note,
        "verdict_headline": verdict_headline,
        "d_positive_strength": strength,
        "any_mechanism_sane": any_mechanism_sane,
        "verdict_rests_on_weak_sane_only": verdict_rests_on_weak_sane_only,
        "leg_tiers": tiers,
        "n_tier5_pass": int(n_tier5_pass),
        "n_dsr_pass": int(n_dsr_pass),
        "under_determined_legs": under_determined_legs,
        # §37.3: substantive-vs-vacuous fields.
        "n_substantive_loss_legs": n_substantive_loss_legs,
        "negative_has_substantive_basis": negative_has_substantive_basis,
        "negative_is_vacuous_only": negative_is_vacuous_only,
        # NET-NEW for Path D: H3 leakage annotation.
        "consistent_with_momentum_or_vol_leakage": consistent_with_momentum_or_vol_leakage,
        "verdict_authority": "charlie_register_at_earned_negative_gate",
        "approximation_tempers": list(APPROXIMATION_TEMPERS),
    }
