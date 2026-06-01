# backtest/pathc_earned_negative.py
"""Earned-negative EVIDENCE bundle for the Path C basis grid (ADVISORY).

Adapted from backtest/patha_earned_negative.py. This module ASSEMBLES the
evidence for the earned-negative read; it does NOT fire any operational decision.
Per the authorization discipline, the binding taxonomy verdict AND the
C-escalation are Charlie's register at the earned-negative gate.

Taxonomy (LOCK Pre-registration 4), keyed on Tier-5 ``holdout_sharpe > 0`` (NOT
DSR pass_B):
  MECHANISM_REFUTED        — NO basis leg's conditional forward-return sign
                             matched its hypothesized direction. Earned negative.
  PROCESS_REFUTED_FOR_GRID — >=1 leg mechanism-sane, but NO variant clears Tier-5
                             holdout_sharpe>0 at 15bps on forward_2026 — refuted
                             for THIS grid/cost, not the basis axis in general.
                             Earned negative.
  C_POSITIVE               — >=1 variant clears Tier-5 holdout_sharpe>0, even if it
                             then fails DSR-FWER. NOT an earned negative. Strength:
                             'weak_needs_2025_oos' if no DSR pass; 'dsr_promoted'
                             if >=1 DSR pass_B.

Tiered mechanism-sanity threading: the per-leg argument carries the C5 tier
(``strong_sane`` / ``weak_sane`` / ``refuted``) per basis leg. A leg is
mechanism-sane iff its tier is ``strong_sane`` or ``weak_sane``;
``verdict_rests_on_weak_sane_only`` is True when ``any_mechanism_sane`` rests
SOLELY on weak-sane legs (>=1 sane leg AND no strong-sane leg) — so a verdict
manufactured by a single-horizon noise flip is flagged for Charlie's §9 read.

Sub-fix 1c (F3 under-determined carve-out, LOCK Pre-registration 3 §37.3):
A leg that is floor-INDETERMINATE on zero_fraction AND returns a thin-sample
non-negative forward Sharpe (trade count below the substantive-read threshold AND
holdout_sharpe >= 0) is tagged ``under_determined=True`` and is NOT folded into
the earned-negative (neither substantive-negative nor Tier-5-eligible). It is
surfaced in the advisory bundle as a power gap. This prevents a near-zero positive
on a thin floor-ineligible leg from being silently read as a negative.

F3 THRESHOLD (pre-registered default): ``UNDER_DETERMINED_TRADE_THRESHOLD = 10``.
The LOCK Pre-reg 3 requires a "substantive read" bar but does not pin the exact
count; 10 trades is a conservative floor that flags degenerate/near-zero forward
results while posing no risk of filtering a genuinely active forward hypothesis.
DONE_WITH_CONCERNS: this is a judgment call pre-committed here. Charlie should
review if the actual forward trade count for any under-floor leg lands within
[1, 20] — the threshold may warrant revision for a future cycle.

Sub-fix 1d (tier threading): thread the per-leg strong/weak-sane tier from C5
(``pathc_perleg_mechanism``) into ``assemble_evidence`` to set
``verdict_rests_on_weak_sane_only``.

A True promotion side effect is a hard error (the harness must be read-only).
"""
from __future__ import annotations

MECHANISM_REFUTED = "mechanism_refuted"
PROCESS_REFUTED_FOR_GRID = "process_refuted_for_this_grid"
C_POSITIVE = "c_positive"

STRONG_SANE = "strong_sane"
WEAK_SANE = "weak_sane"
REFUTED = "refuted"
_SANE_TIERS = (STRONG_SANE, WEAK_SANE)

# F3 under-determined trade threshold (LOCK Pre-registration 3 §37.3; pre-registered
# default). A floor-INDETERMINATE leg with holdout_sharpe >= 0 AND trade count
# strictly below this threshold is tagged under_determined=True (power gap), NOT
# folded into the earned-negative.
# DONE_WITH_CONCERNS: 10 is a conservative judgment-call default; see module docstring.
UNDER_DETERMINED_TRADE_THRESHOLD = 10

# Build-pinned approximation tempers for the Path C basis cycle (data-independent;
# carried so Charlie's earned-negative read sees every conclusiveness caveat in ONE
# place per METHODOLOGY_NOTES §6).
APPROXIMATION_TEMPERS = (
    # The fenced dual-orthogonalization diagnostics (D1 vs momentum; D2 vs funding)
    # are diagnostic-only and never feed N* or promotion. A C-negative + confirmed
    # D2 redundancy tightens the localization to "funding/basis adds no directional
    # rescue at either sampling frequency" — NOT "the whole positioning-premium family
    # fails" (funding and basis are near-collinear; OI is the genuinely independent
    # successor).
    "dual_ortho_d1_d2_fenced_diagnostic_not_promotion_input",
    # Basis features are computed on the native 1h basis_rel series (causal rolling
    # over 1h bars — NO cross-cadence carry; basis is native-1h). The basis_pct_rank
    # and EWM windows are calendar-time-calibrated (2160 / 240 / 480 bars) to Path A's
    # 270 settlements × 8.
    "basis_native_1h_no_cross_cadence_carry_warmup_2160",
    # Mechanism-sanity is measured at 24h AND 72h horizons (tiered strong/weak);
    # a verdict resting on weak-sane-only legs is flagged separately
    # (verdict_rests_on_weak_sane_only) so a single-horizon noise flip cannot
    # silently manufacture mechanism-sanity.
    "mechanism_sanity_tiered_24h_72h_weak_sane_flagged",
    # H2/H3 are pre-registered as expected-INDETERMINATE on zero_fraction (price-trend
    # AND-confirm fires <50% of bars); an under-floor leg with a thin-sample
    # non-negative forward Sharpe is tagged under_determined (F3 carve-out) rather
    # than folded into the earned-negative.
    "h2_h3_preregistered_expected_indeterminate_zero_fraction_f3_carve_out",
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
    *,
    under_determined_flags: dict | None = None,
) -> dict:
    """Assemble the (advisory) earned-negative evidence bundle for Path C.

    Args:
        per_leg: Mapping of leg-id -> tier (C5 ``classify_leg`` output dict with a
            ``"tier"`` key, or a bare tier string). Tiers are ``strong_sane`` /
            ``weak_sane`` / ``refuted``.
        n_tier5_pass: # variants clearing Tier-5 ``holdout_sharpe > 0`` at 15bps on
            forward_2026 (the LOCK §4 C-positive / process-refuted KEY — NOT DSR pass_B).
        n_dsr_pass: # variants passing DSR-FWER (``pass_B``) — the stronger promotion
            signal WITHIN C-positive.
        promotion_side_effect: Read-only flag (MUST be False; the harness never
            mutates the sealed cohort or promotion lists).
        under_determined_flags: Optional mapping of leg-id -> bool
            (True = this leg is under-determined per the F3 carve-out). When
            provided, under-determined legs are surfaced in the advisory bundle as
            power gaps but NOT folded into the earned-negative taxonomy.

    Returns:
        An advisory dict: ``advisory_taxonomy`` (one of the 3 constants),
        ``is_earned_negative`` (bool), ``c_positive_strength`` (or None),
        ``any_mechanism_sane``, ``verdict_rests_on_weak_sane_only``, the echoed
        inputs, ``verdict_authority`` naming Charlie as the binding decider,
        ``approximation_tempers``, and ``under_determined_legs`` (F3 carve-out).
        It NEVER returns a fired action.

    Raises:
        ValueError: If ``promotion_side_effect`` is True.
    """
    if promotion_side_effect:
        raise ValueError(
            "promotion_side_effect=True: the Path C harness must be read-only; "
            "a side effect invalidates the earned-negative evidence."
        )

    tiers = {k: _leg_tier(v) for k, v in per_leg.items()}
    any_mechanism_sane = any(t in _SANE_TIERS for t in tiers.values())
    any_strong_sane = any(t == STRONG_SANE for t in tiers.values())
    # The verdict rests on weak-sane-only legs iff it IS mechanism-sane but no leg
    # is strong-sane (every sane leg is weak-sane — a single-horizon sign).
    verdict_rests_on_weak_sane_only = bool(any_mechanism_sane and not any_strong_sane)

    # F3 under-determined carve-out: record which legs are power-gap flagged.
    ud = under_determined_flags or {}
    under_determined_legs = {k: bool(v) for k, v in ud.items() if v}

    if n_tier5_pass >= 1:
        taxonomy = C_POSITIVE
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

    # GAP 3 (F3 headline caveat, B2 advisor Finding 3): when any leg is under-determined,
    # the headline 'is_earned_negative' is power-limited on those legs. Flag this
    # explicitly so a reader of 'is_earned_negative' ALSO sees the power-gap caveat.
    # This flag does NOT change the taxonomy decision — it adds clarity only.
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

    # Q5: verdict_headline — unmissable top-line summary combining taxonomy + power-limited
    # qualifier. A reader of this single field cannot mistake a power-limited earned-negative
    # for a clean one. This is PURELY ADDITIVE — taxonomy/is_earned_negative/tolerances
    # are UNCHANGED.
    ud_leg_ids = ", ".join(sorted(under_determined_legs))
    if earned_negative_power_limited:
        verdict_headline = (
            f"{taxonomy.upper()} — EARNED-NEGATIVE IS POWER-LIMITED "
            f"(under-determined legs: {ud_leg_ids}); "
            f"not a clean negative — see under_determined_legs"
        )
    elif is_earned_negative:
        verdict_headline = f"{taxonomy.upper()} (earned-negative)"
    else:
        # C_POSITIVE: never power-limited, not an earned-negative
        strength_tag = f"; strength={strength}" if strength else ""
        verdict_headline = f"{taxonomy.upper()}{strength_tag}"

    return {
        "advisory_taxonomy": taxonomy,
        "is_earned_negative": is_earned_negative,
        "earned_negative_power_limited": earned_negative_power_limited,
        "earned_negative_power_limited_note": power_limited_note,
        "verdict_headline": verdict_headline,
        "c_positive_strength": strength,
        "any_mechanism_sane": any_mechanism_sane,
        "verdict_rests_on_weak_sane_only": verdict_rests_on_weak_sane_only,
        "leg_tiers": tiers,
        "n_tier5_pass": int(n_tier5_pass),
        "n_dsr_pass": int(n_dsr_pass),
        "under_determined_legs": under_determined_legs,
        "verdict_authority": "charlie_register_at_earned_negative_gate",
        "approximation_tempers": list(APPROXIMATION_TEMPERS),
    }
