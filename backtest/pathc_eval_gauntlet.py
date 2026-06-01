# backtest/pathc_eval_gauntlet.py
"""Path C basis hypothesis DSL builders (Phase C, Tasks C1-C3).

build_h1_dsl / build_h2_dsl / build_h3_dsl construct the LOCKed N*=3 basis
H-grid DSLs using the REAL DSL/compiler API:
  - Condition(value=...) for factor-vs-scalar AND factor-vs-factor (the field is
    ``value``, NOT ``threshold``);
  - OR-groups = a list of ConditionGroup; within a group, conditions are AND'd;
  - compile via ``compile_dsl_to_strategy(dsl, write_manifest=False)``
    (there is NO ``compile_strategy`` and NO ``dsl.referenced_factors()`` method);
  - ``referenced_factors(dsl)`` is a module-level helper here that walks
    ``dsl.entry`` / ``dsl.exit`` / ``dsl.position_sizing``.

All parameter values are frozen by the Path C Step -1 pre-registration LOCK
(docs/superpowers/specs/2026-05-31-pathc-step-minus-1-preregistration-lock.md).
H1 has NO time-stop — it exits to flat ONLY via the tail-gate and re-enters long
when the tail clears (inherits Path A's Amendment-A1 correction by design: H1 is a
near-always-long de-risk overlay, so a max_hold would impose ~non-mechanistic churn
drag). The DSL has NO ``NOT`` operator, so H1's "flat when (tail) else long" is
expressed by De Morgan (see ``build_h1_dsl``).

DESIGN INVARIANT (H1/H3 exact-partition tie-break): H1's flat-gate uses
``basis_pct_rank_2160 >= theta`` while H3 enters on ``basis_pct_rank_2160 < theta``
(STRICT less-than). These two predicates form an EXACT partition at theta — H1's
tail fires at >= theta, H3's entry is eligible at < theta. H1's flat-gate also
requires ``basis_sign > 0`` (a subset of that tail), so the theta boundary bar
belongs exclusively to H1's flat domain. The LOCK strict-</>= values are kept
exactly as specified (B2 Codex Finding 2e).

Scope note: this module holds ONLY the C1-C3 DSL builders. The verdict-harness
wiring (EVAL gauntlet, guard routing, etc., Tasks C4+) is a separate dispatch and
intentionally not implemented here.
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
# Step -1 LOCK: basis factor names + threshold values (symbolic; do NOT change
# without a LOCK update / Charlie-registered amendment).
# ---------------------------------------------------------------------------

BASIS_RANK = "basis_pct_rank_2160"
BASIS_SIGN = "basis_sign"
BASIS_EWM_240_PCTRANK = "basis_ewm_240_pctrank_2160"
BASIS_EWM_480 = "basis_ewm_480"

DECAY_FAST = "decay_linear_close_48"
DECAY_SLOW = "decay_linear_close_168"
VOL_SIZING_FACTOR = "cdf_realized_vol_720"

# LOCK Pre-registration 1 thresholds.
H1_TAIL_RANK_DEFAULT = 0.90   # basis_pct_rank_2160 extreme-tail gate (build-time default)
H2_DERISK_PCTRANK = 0.80      # basis_ewm_240_pctrank_2160 regime de-risk percentile
H3_TAIL_RANK_DEFAULT = 0.90   # basis_pct_rank_2160 (exact partition with H1 via STRICT <)

# LOCK Pre-registration 1 time-stops. H1 has NONE (inherits Amendment-A1 by design).
H2_MAX_HOLD = 24
H3_MAX_HOLD = 48

# LOCK Pre-registration 1 sizing: vol-CDF ternary on cdf_realized_vol_720 —
# 1.0 in band [0.3, 0.8) (HALF-OPEN), else 0.5; 0 when flat (handled by the engine).
SIZING_BAND_LOWER = 0.3
SIZING_BAND_UPPER = 0.8
SIZING_BAND_SIZE = 1.0
SIZING_DEFAULT = 0.5


def _vol_cdf_ternary_sizing() -> SizingSpec:
    """The shared LOCKed vol-CDF ternary sizing spec (identical for H1/H2/H3).

    Single-factor ternary on ``cdf_realized_vol_720``: ``1.0`` inside the band
    ``[0.3, 0.8)`` (HALF-OPEN), else ``default_size = 0.5``. Basis gates the
    long ON/OFF; it never scales position size (LOCK Pre-registration 3).
    """
    return SizingSpec(
        factor=VOL_SIZING_FACTOR,
        bands=[SizingBand(lower=SIZING_BAND_LOWER, upper=SIZING_BAND_UPPER, size=SIZING_BAND_SIZE)],
        default_size=SIZING_DEFAULT,
    )


def build_h1_dsl(theta: float = H1_TAIL_RANK_DEFAULT) -> StrategyDSL:
    """H1 basis_extreme_fade — crowded-premium reversal, long-biased de-risk overlay.

    LOCK: flat when (``basis_pct_rank_2160 >= theta`` AND ``basis_sign > 0``);
    long otherwise (the ~90% complement). NO time-stop (inherits Path A Amendment-A1
    by design — H1 exits ONLY via the tail-gate).

    The DSL has no NOT operator, so "long on the complement of the tail" is
    expressed by **De Morgan**:
        NOT(rank >= theta AND sign > 0)  ==  (rank < theta) OR (sign <= 0)
    ENTRY = two OR-groups: ``[rank < theta]`` OR ``[sign <= 0]`` (``sign <= 0``
    covers {-1, 0}). EXIT = the single tail-gate group ``(rank >= theta AND
    sign > 0)``. Vol-CDF ternary sizing.

    Args:
        theta: The tail-rank threshold (default 0.90; fallback 0.85 evaluated at
            RUN-TIME on train per LOCK Pre-registration 1 deterministic rule — do
            NOT bake the fallback here; pass theta=0.85 from the orchestrator when
            the floor fires).

    Inputs: basis_pct_rank_2160 (causal rolling-2160 percentile of basis_rel),
        basis_sign (sign of basis_rel), cdf_realized_vol_720 (sizing).
    Warmup: 2160 bars (dominated by basis_pct_rank_2160 min_periods=2160; all in
        native 1h-bar units — no cross-cadence carry for basis).
    Output: long/flat position signal; 0 when flat.
    Null policy: NaN in any condition evaluates to False (DSL compiler invariant).
    """
    entry_rank = ConditionGroup(conditions=[
        Condition(factor=BASIS_RANK, op="<", value=theta),
    ])
    entry_sign = ConditionGroup(conditions=[
        Condition(factor=BASIS_SIGN, op="<=", value=0.0),
    ])
    # EXIT = the extreme-tail gate (the De Morgan negand): rank >= theta AND sign > 0.
    exit_tail = ConditionGroup(conditions=[
        Condition(factor=BASIS_RANK, op=">=", value=theta),
        Condition(factor=BASIS_SIGN, op=">", value=0.0),
    ])
    return StrategyDSL(
        name="pathc_h1",
        description=(
            "Path C H1: basis_extreme_fade — long-biased de-risk overlay, flat on the "
            "crowded-premium basis tail (De Morgan complement), vol-CDF ternary sizing, "
            "no time-stop."
        ),
        entry=[entry_rank, entry_sign],
        exit=[exit_tail],
        position_sizing=_vol_cdf_ternary_sizing(),
        max_hold_bars=None,  # NO time-stop (inherits Amendment-A1 by design).
    )


def build_h2_dsl() -> StrategyDSL:
    """H2 basis_regime_gate — regime-gate on a price-trend book.

    LOCK: regime axis = causal rolling-2160 percentile of ``basis_ewm_240``
    (the registered ``basis_ewm_240_pctrank_2160`` factor). PERMISSIVE
    (long-enabled) when that percentile ``< 0.80`` AND ``decay_linear_close_48 >
    decay_linear_close_168`` (price-trend confirm) -> long. DE-RISK (flat) when
    the percentile ``>= 0.80``. Exit on de-risk regime / trend roll-over
    (``48 <= 168``) / ``max_hold_bars = 24``. Vol-CDF ternary sizing.

    Inputs: basis_ewm_240_pctrank_2160 (causal rolling-2160 pctrank of basis_ewm_240),
        decay_linear_close_48, decay_linear_close_168, cdf_realized_vol_720 (sizing).
    Warmup: 2160 bars (percentile min_periods=2160 dominates the inner 240-EWM warmup;
        native 1h-bar units).
    Output: long/flat position signal; 0 when flat.
    Null policy: NaN in any condition evaluates to False (DSL compiler invariant).
    """
    entry = ConditionGroup(conditions=[
        Condition(factor=BASIS_EWM_240_PCTRANK, op="<", value=H2_DERISK_PCTRANK),
        Condition(factor=DECAY_FAST, op=">", value=DECAY_SLOW),
    ])
    # Exit OR-groups: enter the de-risk regime, OR the price trend rolls over.
    exit_derisk = ConditionGroup(conditions=[
        Condition(factor=BASIS_EWM_240_PCTRANK, op=">=", value=H2_DERISK_PCTRANK),
    ])
    exit_trend_roll = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op="<=", value=DECAY_SLOW),
    ])
    return StrategyDSL(
        name="pathc_h2",
        description=(
            "Path C H2: basis_regime_gate — permissive long-on-trend when the basis-EWM "
            "regime percentile is low, flat in the de-risk regime, vol-CDF ternary sizing."
        ),
        entry=[entry],
        exit=[exit_derisk, exit_trend_roll],
        position_sizing=_vol_cdf_ternary_sizing(),
        max_hold_bars=H2_MAX_HOLD,
    )


def build_h3_dsl(theta: float = H3_TAIL_RANK_DEFAULT) -> StrategyDSL:
    """H3 basis_momentum_continuation — moderate-persistence trend confirm.

    LOCK: long when ``basis_ewm_480 > 0`` AND ``basis_pct_rank_2160 < theta``
    (STRICT less-than: exact partition with H1's >= theta flat-tail, B2 Codex
    Finding 2e) AND ``decay_linear_close_48 > decay_linear_close_168``.
    Exit: ``basis_ewm_480 <= 0`` / trend roll-over (``48 <= 168``) /
    ``basis_pct_rank_2160 >= theta`` / ``max_hold_bars = 48``. Vol-CDF ternary sizing.

    Args:
        theta: The tail-rank threshold (default 0.90; must be the SAME value as H1's
            theta for the exact-partition invariant to hold — the orchestrator sets
            both together when the fallback fires).

    Inputs: basis_ewm_480 (causal EWM span-480 of basis_rel), basis_pct_rank_2160
        (causal rolling-2160 percentile), decay_linear_close_48,
        decay_linear_close_168, cdf_realized_vol_720 (sizing).
    Warmup: 2160 bars (pctrank min_periods=2160 dominates; native 1h-bar units).
    Output: long/flat position signal; 0 when flat.
    Null policy: NaN in any condition evaluates to False (DSL compiler invariant).
    """
    entry = ConditionGroup(conditions=[
        Condition(factor=BASIS_EWM_480, op=">", value=0.0),
        Condition(factor=BASIS_RANK, op="<", value=theta),   # STRICT < (exact partition)
        Condition(factor=DECAY_FAST, op=">", value=DECAY_SLOW),
    ])
    # Exit OR-groups (3): basis momentum flips / trend rolls over / basis enters the
    # extreme tail. The 4th LOCK exit (max_hold 48) is the DSL max_hold_bars field.
    exit_mom_flip = ConditionGroup(conditions=[
        Condition(factor=BASIS_EWM_480, op="<=", value=0.0),
    ])
    exit_trend_roll = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op="<=", value=DECAY_SLOW),
    ])
    exit_tail = ConditionGroup(conditions=[
        Condition(factor=BASIS_RANK, op=">=", value=theta),
    ])
    return StrategyDSL(
        name="pathc_h3",
        description=(
            "Path C H3: basis_momentum_continuation — long while basis EWM-480 is positive, "
            "off the extreme tail (strict < theta, exact partition with H1), with a "
            "price-trend confirm; vol-CDF ternary sizing."
        ),
        entry=[entry],
        exit=[exit_mom_flip, exit_trend_roll, exit_tail],
        position_sizing=_vol_cdf_ternary_sizing(),
        max_hold_bars=H3_MAX_HOLD,
    )


def build_all_hypotheses() -> dict[str, StrategyDSL]:
    """The full N*=3 pre-registered basis grid (one variant each)."""
    return {"H1": build_h1_dsl(), "H2": build_h2_dsl(), "H3": build_h3_dsl()}


# ---------------------------------------------------------------------------
# Task C6 no-basis baselines — the fenced dual-orthogonalization D1 counterfactual
# (LOCK Pre-registration 3). Each baseline is the SAME strategy WITHOUT the basis
# gate, run on the SAME forward bars, so any D1-result attributes to basis's
# MARGINAL contribution and not Path B's already-dead decay-MA leg (H2/H3) or
# buy-and-hold (H1). These never feed N* or promotion; they exist only to compute
# basis_marginal_d1(gated, baseline) (DESIGN INVARIANT: backtest.pathc_marginal_diagnostic
# fences the result with structural promotion_affecting=False / in_n_star=False flags).
# ---------------------------------------------------------------------------

# Always-true / never-true sentinels on the bounded [0, 1] vol CDF (the H1
# baseline's "always-long" gate): cdf_realized_vol_720 in [0.0, 1.0], so
# ``>= 0.0`` is always true (NaN during warmup -> False, the correct no-trade)
# and ``> 1.0`` is never true. This keeps the baseline basis-free while satisfying
# the DSL's min_length=1 entry/exit requirement.
_VOL_CDF_FLOOR = 0.0   # cdf_realized_vol_720 >= 0.0 is always true on a CDF
_VOL_CDF_CEIL = 1.0    # cdf_realized_vol_720 > 1.0 is never true on a CDF


def build_h1_baseline_dsl() -> StrategyDSL:
    """H1 no-basis baseline: ALWAYS-LONG (the H1 counterfactual minus the gate).

    Strips H1's basis flat-gate entirely: entry is an always-true predicate on
    the bounded vol CDF (``cdf_realized_vol_720 >= 0.0``) and exit is a never-true
    one (``cdf_realized_vol_720 > 1.0``), so the book is long whenever it is
    sizeable. Same vol-CDF ternary sizing; NO time-stop (mirrors H1's no-time-stop).

    Inputs: cdf_realized_vol_720 (sizing; the only referenced factor — no basis factors).
    Warmup: 720 bars (vol CDF min_periods=720 only; no basis warmup).
    Output: long/flat signal; always-long during the evaluated window.
    Null policy: NaN in any condition evaluates to False (DSL compiler invariant).
    Diagnostic-only — never in N* / promotion.
    """
    entry_always = ConditionGroup(conditions=[
        Condition(factor=VOL_SIZING_FACTOR, op=">=", value=_VOL_CDF_FLOOR),
    ])
    exit_never = ConditionGroup(conditions=[
        Condition(factor=VOL_SIZING_FACTOR, op=">", value=_VOL_CDF_CEIL),
    ])
    return StrategyDSL(
        name="pathc_h1_baseline",
        description=(
            "Path C H1 no-basis baseline: always-long (basis flat-gate stripped), "
            "vol-CDF ternary sizing, no time-stop — the D1 basis-marginal counterfactual."
        ),
        entry=[entry_always],
        exit=[exit_never],
        position_sizing=_vol_cdf_ternary_sizing(),
        max_hold_bars=None,
    )


def _price_trend_only_baseline(name: str, description: str, max_hold: int) -> StrategyDSL:
    """Shared price-trend-only book for the H2/H3 no-basis baselines.

    Entry = ``decay_linear_close_48 > decay_linear_close_168`` (the price-trend
    confirm both H2 and H3 share); exit = the trend roll-over ``48 <= 168``. NO
    basis condition. Same vol-CDF ternary sizing. ``max_hold`` is the gated
    hypothesis's own backstop (H2=24 / H3=48) so the baseline is the SAME
    strategy minus only the basis gate.

    Inputs: decay_linear_close_48, decay_linear_close_168, cdf_realized_vol_720 (sizing).
    Warmup: 168 bars (decay_linear_close_168 dominates; no basis warmup).
    Output: long/flat signal; long whenever price-trend condition holds.
    Null policy: NaN in any condition evaluates to False (DSL compiler invariant).
    """
    entry = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op=">", value=DECAY_SLOW),
    ])
    exit_trend_roll = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op="<=", value=DECAY_SLOW),
    ])
    return StrategyDSL(
        name=name,
        description=description,
        entry=[entry],
        exit=[exit_trend_roll],
        position_sizing=_vol_cdf_ternary_sizing(),
        max_hold_bars=max_hold,
    )


def build_h2_baseline_dsl() -> StrategyDSL:
    """H2 no-basis baseline: the price-trend-only book (H2 minus the basis gate).

    Strips the ``basis_ewm_240_pctrank_2160 < 0.80`` regime gate; retains the
    ``decay_linear_close_48 > decay_linear_close_168`` entry + trend-rollover exit
    + ``max_hold_bars = 24``. Diagnostic-only — never in N* / promotion.
    """
    return _price_trend_only_baseline(
        name="pathc_h2_baseline",
        description=(
            "Path C H2 no-basis baseline: price-trend-only (basis regime-gate stripped), "
            "vol-CDF ternary sizing, max_hold 24 — the D1 basis-marginal counterfactual."
        ),
        max_hold=H2_MAX_HOLD,
    )


def build_h3_baseline_dsl() -> StrategyDSL:
    """H3 no-basis baseline: the price-trend-only book (H3 minus the basis gate).

    Strips the ``basis_ewm_480 > 0`` AND ``basis_pct_rank_2160 < theta`` gates;
    retains the ``decay_linear_close_48 > decay_linear_close_168`` entry + trend-
    rollover exit + ``max_hold_bars = 48``. Diagnostic-only — never in N* / promotion.
    """
    return _price_trend_only_baseline(
        name="pathc_h3_baseline",
        description=(
            "Path C H3 no-basis baseline: price-trend-only (basis momentum/tail gate stripped), "
            "vol-CDF ternary sizing, max_hold 48 — the D1 basis-marginal counterfactual."
        ),
        max_hold=H3_MAX_HOLD,
    )


def build_all_baselines() -> dict[str, StrategyDSL]:
    """The 3 no-basis baselines keyed by hypothesis id (Task C6 D1 counterfactual)."""
    return {
        "H1": build_h1_baseline_dsl(),
        "H2": build_h2_baseline_dsl(),
        "H3": build_h3_baseline_dsl(),
    }


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
