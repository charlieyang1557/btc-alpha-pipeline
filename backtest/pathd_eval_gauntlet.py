# backtest/pathd_eval_gauntlet.py
"""Path D OI-axis hypothesis DSL builders (Phase D, Tasks C1-C3).

build_h1_dsl / build_h2_dsl / build_h3_dsl construct the LOCKed N*=3 OI
H-grid DSLs using the REAL DSL/compiler API:
  - Condition(value=...) for factor-vs-scalar AND factor-vs-factor (the field is
    ``value``, NOT ``threshold``);
  - OR-groups = a list of ConditionGroup; within a group, conditions are AND'd;
  - compile via ``compile_dsl_to_strategy(dsl, write_manifest=False)``
    (there is NO ``compile_strategy`` and NO ``dsl.referenced_factors()`` method);
  - ``referenced_factors(dsl)`` is a module-level helper here that walks
    ``dsl.entry`` / ``dsl.exit`` / ``dsl.position_sizing``.

OI is DIRECTIONLESS — direction is 100% the inherited price-trend cross;
OI enters ONLY as a gate (level-tail, regime, or new-flow continuation).

All parameter values are frozen by the Path D Step -1 pre-registration LOCK.
H1 is the SIMPLER form: NO sign conjunct, NO price-trend conjunct, NO time-stop
(Amendment-A1 inheritance). No De Morgan is needed for H1 (the entry and exit
are a single OR-group each — the entry is directly the complement-predicate, the
exit is the tail-gate, exactly symmetrical).

DESIGN INVARIANT (H1/H3 exact-partition tie-break): H1's flat-gate uses
``oi_pct_rank_2160 >= theta`` while H3 enters on ``oi_pct_rank_2160 < theta``
(STRICT less-than). These two predicates form an EXACT partition at theta.

Scope note: this module holds ONLY the C1-C3 DSL builders. The verdict-harness
wiring (Tasks C4+) is a separate dispatch and intentionally not implemented here.
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
# Step -1 LOCK: OI factor names + threshold values (symbolic; do NOT change
# without a LOCK update / Charlie-registered amendment).
# ---------------------------------------------------------------------------

OI_RANK = "oi_pct_rank_2160"
OI_VELOCITY_EWM_240 = "oi_velocity_ewm_240"
OI_VELOCITY_EWM_240_PCTRANK = "oi_velocity_ewm_240_pctrank_2160"
# oi_sign is LOCK-registered for factor-family completeness but referenced
# by NO hypothesis (per the Task B5 LOCK rationale in CLAUDE.md).

DECAY_FAST = "decay_linear_close_48"
DECAY_SLOW = "decay_linear_close_168"
VOL_SIZING_FACTOR = "cdf_realized_vol_720"

# LOCK: thresholds
H1_TAIL_RANK_DEFAULT = 0.90   # oi_pct_rank_2160 extreme-tail gate (build-time default)
H2_DERISK_PCTRANK = 0.80      # oi_velocity_ewm_240_pctrank_2160 regime de-risk percentile
H3_TAIL_RANK_DEFAULT = 0.90   # oi_pct_rank_2160 (exact partition with H1 via STRICT <)

# LOCK: time-stops. H1 has NONE (inherits Amendment-A1 by design).
H2_MAX_HOLD = 24
H3_MAX_HOLD = 48

# LOCK: sizing — vol-CDF ternary on cdf_realized_vol_720:
# 1.0 in band [0.3, 0.8) (HALF-OPEN), else 0.5; 0 when flat (handled by engine).
SIZING_BAND_LOWER = 0.3
SIZING_BAND_UPPER = 0.8
SIZING_BAND_SIZE = 1.0
SIZING_DEFAULT = 0.5


def _vol_cdf_ternary_sizing() -> SizingSpec:
    """The shared LOCKed vol-CDF ternary sizing spec (identical for H1/H2/H3).

    Single-factor ternary on ``cdf_realized_vol_720``: ``1.0`` inside the band
    ``[0.3, 0.8)`` (HALF-OPEN), else ``default_size = 0.5``. OI gates the
    long ON/OFF; it never scales position size.
    """
    return SizingSpec(
        factor=VOL_SIZING_FACTOR,
        bands=[SizingBand(lower=SIZING_BAND_LOWER, upper=SIZING_BAND_UPPER, size=SIZING_BAND_SIZE)],
        default_size=SIZING_DEFAULT,
    )


def build_h1_dsl(theta: float = H1_TAIL_RANK_DEFAULT) -> StrategyDSL:
    """H1 oi_extreme_fade — level-tail de-risk overlay (SIMPLER than Path C H1).

    LOCK: long when ``oi_pct_rank_2160 < theta`` (the ~90% complement of the
    extreme-high-OI tail); flat when ``oi_pct_rank_2160 >= theta``.
    NO time-stop (inherits Path A Amendment-A1 by design — H1 exits ONLY via
    the tail-gate). NO ``oi_sign`` conjunct, NO price-trend conjunct (pure
    level-tail overlay; D1 baseline is always-long).

    Unlike Path C H1, there is NO sign conjunct in the flat-gate, so De Morgan
    is NOT needed. ENTRY = single group ``[oi_pct_rank_2160 < theta]``.
    EXIT = single group ``[oi_pct_rank_2160 >= theta]``. Vol-CDF ternary sizing.

    Args:
        theta: The tail-rank threshold (default 0.90; fallback 0.85 evaluated at
            RUN-TIME on train per LOCK deterministic rule — do NOT bake the
            fallback here; pass theta=0.85 from the orchestrator when the
            floor fires).

    Inputs: oi_pct_rank_2160 (causal rolling-2160 percentile of OI log-change),
        cdf_realized_vol_720 (sizing).
    Warmup: 2160 bars (oi_pct_rank_2160 min_periods=2160 dominates).
    Output: long/flat position signal; 0 when flat.
    Null policy: NaN in any condition evaluates to False (DSL compiler invariant).
    """
    entry = ConditionGroup(conditions=[
        Condition(factor=OI_RANK, op="<", value=theta),
    ])
    exit_tail = ConditionGroup(conditions=[
        Condition(factor=OI_RANK, op=">=", value=theta),
    ])
    return StrategyDSL(
        name="pathd_h1",
        description=(
            "Path D H1: oi_extreme_fade — long-biased de-risk overlay, flat on the "
            "extreme-high-OI tail (oi_pct_rank_2160 >= theta), vol-CDF ternary sizing, "
            "no time-stop, no sign/price-trend conjunct."
        ),
        entry=[entry],
        exit=[exit_tail],
        position_sizing=_vol_cdf_ternary_sizing(),
        max_hold_bars=None,  # NO time-stop (inherits Amendment-A1 by design).
    )


def build_h2_dsl() -> StrategyDSL:
    """H2 oi_regime_gate — regime gate on a price-trend book.

    LOCK: PERMISSIVE (long-enabled) when ``oi_velocity_ewm_240_pctrank_2160 < 0.80``
    AND ``decay_linear_close_48 > decay_linear_close_168`` (price-trend confirm).
    DE-RISK (flat) when ``oi_velocity_ewm_240_pctrank_2160 >= 0.80`` (regardless
    of trend). Exit on de-risk regime / trend roll-over (``48 <= 168``) /
    ``max_hold_bars = 24``. Vol-CDF ternary sizing.

    Inputs: oi_velocity_ewm_240_pctrank_2160 (causal rolling-2160 pctrank of
        oi_velocity_ewm_240), decay_linear_close_48, decay_linear_close_168,
        cdf_realized_vol_720 (sizing).
    Warmup: 2160 bars (percentile min_periods=2160 dominates).
    Output: long/flat position signal; 0 when flat.
    Null policy: NaN in any condition evaluates to False (DSL compiler invariant).
    """
    entry = ConditionGroup(conditions=[
        Condition(factor=OI_VELOCITY_EWM_240_PCTRANK, op="<", value=H2_DERISK_PCTRANK),
        Condition(factor=DECAY_FAST, op=">", value=DECAY_SLOW),
    ])
    # Exit OR-groups: enter the de-risk regime, OR the price trend rolls over.
    exit_derisk = ConditionGroup(conditions=[
        Condition(factor=OI_VELOCITY_EWM_240_PCTRANK, op=">=", value=H2_DERISK_PCTRANK),
    ])
    exit_trend_roll = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op="<=", value=DECAY_SLOW),
    ])
    return StrategyDSL(
        name="pathd_h2",
        description=(
            "Path D H2: oi_regime_gate — permissive long-on-trend when the OI-velocity "
            "regime percentile is low, flat in the de-risk regime, vol-CDF ternary sizing."
        ),
        entry=[entry],
        exit=[exit_derisk, exit_trend_roll],
        position_sizing=_vol_cdf_ternary_sizing(),
        max_hold_bars=H2_MAX_HOLD,
    )


def build_h3_dsl(theta: float = H3_TAIL_RANK_DEFAULT) -> StrategyDSL:
    """H3 oi_momentum_continuation — new-flow continuation; strict partition vs H1.

    LOCK: long when ``oi_velocity_ewm_240 > 0`` AND ``oi_pct_rank_2160 < theta``
    (STRICT less-than: exact partition with H1's >= theta flat-tail) AND
    ``decay_linear_close_48 > decay_linear_close_168``. NO extra price-return
    conjunct beyond the decay cross (the graft fix — keeps D1 attributable).
    Exit: ``oi_velocity_ewm_240 <= 0`` / trend roll-over / ``oi_pct_rank_2160 >= theta``
    / ``max_hold_bars = 48``. Vol-CDF ternary sizing.

    Args:
        theta: The tail-rank threshold (default 0.90; must be the SAME value as H1's
            theta for the exact-partition invariant to hold — the orchestrator sets
            both together when the fallback fires).

    Inputs: oi_velocity_ewm_240 (causal EWM span-240 of OI log-change),
        oi_pct_rank_2160 (causal rolling-2160 percentile), decay_linear_close_48,
        decay_linear_close_168, cdf_realized_vol_720 (sizing).
    Warmup: 2160 bars (pctrank min_periods=2160 dominates).
    Output: long/flat position signal; 0 when flat.
    Null policy: NaN in any condition evaluates to False (DSL compiler invariant).
    """
    entry = ConditionGroup(conditions=[
        Condition(factor=OI_VELOCITY_EWM_240, op=">", value=0.0),
        Condition(factor=OI_RANK, op="<", value=theta),   # STRICT < (exact partition)
        Condition(factor=DECAY_FAST, op=">", value=DECAY_SLOW),
    ])
    # Exit OR-groups: OI velocity flips / trend rolls over / OI enters the
    # extreme tail. The 4th LOCK exit (max_hold 48) is the DSL max_hold_bars field.
    exit_velocity_flip = ConditionGroup(conditions=[
        Condition(factor=OI_VELOCITY_EWM_240, op="<=", value=0.0),
    ])
    exit_trend_roll = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op="<=", value=DECAY_SLOW),
    ])
    exit_tail = ConditionGroup(conditions=[
        Condition(factor=OI_RANK, op=">=", value=theta),
    ])
    return StrategyDSL(
        name="pathd_h3",
        description=(
            "Path D H3: oi_momentum_continuation — long while OI velocity EWM-240 is "
            "positive, off the extreme tail (strict < theta, exact partition with H1), "
            "with a price-trend confirm; vol-CDF ternary sizing."
        ),
        entry=[entry],
        exit=[exit_velocity_flip, exit_trend_roll, exit_tail],
        position_sizing=_vol_cdf_ternary_sizing(),
        max_hold_bars=H3_MAX_HOLD,
    )


def build_all_hypotheses() -> dict[str, StrategyDSL]:
    """The full N*=3 pre-registered OI grid (one variant each)."""
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
