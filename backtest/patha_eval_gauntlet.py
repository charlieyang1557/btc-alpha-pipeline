# backtest/patha_eval_gauntlet.py
"""Path A funding hypothesis DSL builders (Phase C, Tasks C1-C3).

build_h1_dsl / build_h2_dsl / build_h3_dsl construct the LOCKed N*=3 funding
H-grid DSLs using the REAL DSL/compiler API:
  - Condition(value=...) for factor-vs-scalar AND factor-vs-factor (the field is
    ``value``, NOT ``threshold``);
  - OR-groups = a list of ConditionGroup; within a group, conditions are AND'd;
  - compile via ``compile_dsl_to_strategy(dsl, write_manifest=False)``
    (there is NO ``compile_strategy`` and NO ``dsl.referenced_factors()`` method);
  - ``referenced_factors(dsl)`` is a module-level helper here that walks
    ``dsl.entry`` / ``dsl.exit`` / ``dsl.position_sizing``.

All parameter values are frozen by the Path A Step -1 pre-registration LOCK
(docs/superpowers/specs/2026-05-31-patha-step-minus-1-preregistration-lock.md),
INCLUDING Amendment A1: H1 has NO time-stop — it exits to flat ONLY via the
tail-gate and re-enters long when the tail clears (the ``max_hold_bars = 72``
in the original Pre-registration 1 text is SUPERSEDED). The DSL has NO ``NOT``
operator, so H1's "flat when (tail) else long" is expressed by De Morgan (see
``build_h1_dsl``).

DESIGN INVARIANT (H1/H3 tail tie-break): H1's flat-gate uses
``funding_pct_rank_270 >= 0.90`` while H3 enters on ``funding_pct_rank_270 <=
0.90``. The two predicates overlap only at *exactly* 0.90 — a measure-zero event
on a continuous percentile. H1's flat-gate takes precedence there, and H3
additionally requires ``funding_ewm_60 > 0`` + a price-trend confirm, so the
boundary is immaterial. The LOCK ``<=`` / ``>=`` values are kept as-is.

Scope note: this module currently holds ONLY the C1-C3 DSL builders. The
verdict-harness wiring (EVAL gauntlet, guard routing, etc., Tasks C4-C7) is a
separate dispatch and intentionally not implemented here.
"""
from __future__ import annotations

from strategies.dsl import (
    Condition,
    ConditionGroup,
    SizingBand,
    SizingSpec,
    StrategyDSL,
)

# ---------------------------------------------------------------------------
# Step -1 LOCK: funding factor names + threshold values (symbolic; do NOT change
# without a LOCK update / Charlie-registered amendment).
# ---------------------------------------------------------------------------

FUNDING_RANK = "funding_pct_rank_270"
FUNDING_SIGN = "funding_sign"
FUNDING_EWM_60 = "funding_ewm_60"
FUNDING_EWM_30_PCTRANK = "funding_ewm_30_pctrank_270"

DECAY_FAST = "decay_linear_close_48"
DECAY_SLOW = "decay_linear_close_168"
VOL_SIZING_FACTOR = "cdf_realized_vol_720"

# LOCK Pre-registration 1 thresholds.
H1_TAIL_RANK = 0.90       # funding_pct_rank_270 extreme-tail gate
H2_DERISK_PCTRANK = 0.80  # funding_ewm_30 regime de-risk percentile
H3_TAIL_RANK = 0.90       # funding_pct_rank_270 (excludes H1's tail)

# LOCK Pre-registration 1 time-stops. H1 has NONE (Amendment A1).
H2_MAX_HOLD = 24
H3_MAX_HOLD = 48

# LOCK Pre-registration 1 sizing: vol-CDF ternary on cdf_realized_vol_720 —
# 1.0 in band [0.3, 0.8), else 0.5; 0 when flat (handled by the engine).
SIZING_BAND_LOWER = 0.3
SIZING_BAND_UPPER = 0.8
SIZING_BAND_SIZE = 1.0
SIZING_DEFAULT = 0.5


def _vol_cdf_ternary_sizing() -> SizingSpec:
    """The shared LOCKed vol-CDF ternary sizing spec (identical for H1/H2/H3).

    Single-factor ternary on ``cdf_realized_vol_720``: ``1.0`` inside the band
    ``[0.3, 0.8)``, else ``default_size = 0.5``. Funding gates the long ON/OFF;
    it never scales position size (LOCK Pre-registration 3).
    """
    return SizingSpec(
        factor=VOL_SIZING_FACTOR,
        bands=[SizingBand(lower=SIZING_BAND_LOWER, upper=SIZING_BAND_UPPER, size=SIZING_BAND_SIZE)],
        default_size=SIZING_DEFAULT,
    )


def build_h1_dsl() -> StrategyDSL:
    """H1 funding_extreme_fade — crowded-long reversal, long-biased de-risk overlay.

    LOCK: flat when (``funding_pct_rank_270 >= 0.90`` AND ``funding_sign > 0``);
    long otherwise (the ~90% complement). NO time-stop (Amendment A1).

    The DSL has no NOT operator, so "long on the complement of the tail" is
    expressed by **De Morgan**:
        NOT(rank >= 0.90 AND sign > 0)  ==  (rank < 0.90) OR (sign <= 0)
    ENTRY = two OR-groups: ``[rank < 0.90]`` OR ``[sign <= 0]`` (``sign <= 0``
    covers {-1, 0}). EXIT = the single tail-gate group ``(rank >= 0.90 AND
    sign > 0)``. Vol-CDF ternary sizing.
    """
    entry_rank = ConditionGroup(conditions=[
        Condition(factor=FUNDING_RANK, op="<", value=H1_TAIL_RANK),
    ])
    entry_sign = ConditionGroup(conditions=[
        Condition(factor=FUNDING_SIGN, op="<=", value=0.0),
    ])
    # EXIT = the extreme-tail gate (the De Morgan negand): rank >= 0.90 AND sign > 0.
    exit_tail = ConditionGroup(conditions=[
        Condition(factor=FUNDING_RANK, op=">=", value=H1_TAIL_RANK),
        Condition(factor=FUNDING_SIGN, op=">", value=0.0),
    ])
    return StrategyDSL(
        name="patha_h1",
        description="Path A H1: funding_extreme_fade — long-biased de-risk overlay, flat on the crowded-long funding tail (De Morgan complement), vol-CDF ternary sizing, no time-stop.",
        entry=[entry_rank, entry_sign],
        exit=[exit_tail],
        position_sizing=_vol_cdf_ternary_sizing(),
        max_hold_bars=None,  # Amendment A1: H1 exits ONLY via the tail-gate.
    )


def build_h2_dsl() -> StrategyDSL:
    """H2 funding_sign_regime_switch — funding regime-gate on a price-trend book.

    LOCK: regime axis = causal rolling-270 percentile of ``funding_ewm_30``
    (the registered ``funding_ewm_30_pctrank_270`` factor). PERMISSIVE
    (long-enabled) when that percentile ``< 0.80`` AND ``decay_linear_close_48 >
    decay_linear_close_168`` (price-trend confirm) -> long. DE-RISK (flat) when
    the percentile ``>= 0.80``. Exit on de-risk regime / trend roll-over /
    ``max_hold_bars = 24``. Vol-CDF ternary sizing.
    """
    entry = ConditionGroup(conditions=[
        Condition(factor=FUNDING_EWM_30_PCTRANK, op="<", value=H2_DERISK_PCTRANK),
        Condition(factor=DECAY_FAST, op=">", value=DECAY_SLOW),
    ])
    # Exit OR-groups: enter the de-risk regime, OR the price trend rolls over.
    exit_derisk = ConditionGroup(conditions=[
        Condition(factor=FUNDING_EWM_30_PCTRANK, op=">=", value=H2_DERISK_PCTRANK),
    ])
    exit_trend_roll = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op="<=", value=DECAY_SLOW),
    ])
    return StrategyDSL(
        name="patha_h2",
        description="Path A H2: funding_sign_regime_switch — permissive long-on-trend when the funding-EWM regime percentile is low, flat in the de-risk regime, vol-CDF ternary sizing.",
        entry=[entry],
        exit=[exit_derisk, exit_trend_roll],
        position_sizing=_vol_cdf_ternary_sizing(),
        max_hold_bars=H2_MAX_HOLD,
    )


def build_h3_dsl() -> StrategyDSL:
    """H3 funding_momentum_continuation — moderate-persistence trend confirm.

    LOCK: long when ``funding_ewm_60 > 0`` AND ``funding_pct_rank_270 <= 0.90``
    (excludes H1's tail -> non-overlapping populations) AND
    ``decay_linear_close_48 > decay_linear_close_168``. Exit: ``funding_ewm_60
    <= 0`` / trend roll-over (``48 <= 168``) / ``funding_pct_rank_270 > 0.90`` /
    ``max_hold_bars = 48``. Vol-CDF ternary sizing.
    """
    entry = ConditionGroup(conditions=[
        Condition(factor=FUNDING_EWM_60, op=">", value=0.0),
        Condition(factor=FUNDING_RANK, op="<=", value=H3_TAIL_RANK),
        Condition(factor=DECAY_FAST, op=">", value=DECAY_SLOW),
    ])
    # Exit OR-groups (3): funding momentum flips / trend rolls over / funding
    # enters the extreme tail. The 4th LOCK exit (max_hold 48) is the DSL
    # ``max_hold_bars`` field, not an exit group.
    exit_mom_flip = ConditionGroup(conditions=[
        Condition(factor=FUNDING_EWM_60, op="<=", value=0.0),
    ])
    exit_trend_roll = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op="<=", value=DECAY_SLOW),
    ])
    exit_tail = ConditionGroup(conditions=[
        Condition(factor=FUNDING_RANK, op=">", value=H3_TAIL_RANK),
    ])
    return StrategyDSL(
        name="patha_h3",
        description="Path A H3: funding_momentum_continuation — long while funding EWM is positive, off the extreme tail, with a price-trend confirm; vol-CDF ternary sizing.",
        entry=[entry],
        exit=[exit_mom_flip, exit_trend_roll, exit_tail],
        position_sizing=_vol_cdf_ternary_sizing(),
        max_hold_bars=H3_MAX_HOLD,
    )


def build_all_hypotheses() -> dict[str, StrategyDSL]:
    """The full N*=3 pre-registered funding grid (one variant each)."""
    return {"H1": build_h1_dsl(), "H2": build_h2_dsl(), "H3": build_h3_dsl()}


def referenced_factors(dsl: StrategyDSL) -> set[str]:
    """Return the set of factor names a DSL references.

    Walks every ``Condition`` in ``dsl.entry`` and ``dsl.exit`` (collecting the
    LHS ``factor`` and, when the RHS ``value`` is a factor name string rather
    than a numeric scalar, the RHS factor too), plus the
    ``dsl.position_sizing`` sizing factor when sizing is a :class:`SizingSpec`.

    This is the module-level replacement for the (non-existent)
    ``dsl.referenced_factors()`` method referenced by older drafts.
    """
    names: set[str] = set()
    for group in (*dsl.entry, *dsl.exit):
        for cond in group.conditions:
            names.add(cond.factor)
            if isinstance(cond.value, str):  # factor-vs-factor RHS
                names.add(cond.value)
    sizing = dsl.position_sizing
    if isinstance(sizing, SizingSpec):
        names.add(sizing.factor)
    return names
