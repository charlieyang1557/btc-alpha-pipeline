# backtest/pathb_eval_gauntlet.py
"""Path B hypothesis DSL builders + evaluation gauntlet stage->guard routing.

build_h1_dsl / build_h2_dsl / build_h3_dsl construct the locked N*=3 H-grid
DSLs using the REAL DSL/compiler API (Condition(value=...) — NOT threshold;
StrategyDSL(description=..., entry=..., exit=..., position_sizing=...);
compile_dsl_to_strategy(...) — NOT compile_strategy).

EVAL_GAUNTLET pins which wf_lineage guard each stage uses:
  - train WALK-FORWARD artifacts  -> check_wf_semantics_or_raise (corrected_test_boundary_v1)
  - 2022 regime-holdout / 2024 validation / Tier-5 (all SINGLE-RUN evaluations)
        -> check_evaluation_semantics_or_raise (single_run_holdout_v1)

The two guards do NOT cross-validate; routing them by stage is the contract.
Path B writes into its OWN namespace, never the sealed cohort/tier6 dirs.

Threshold values (THETA_PUSH etc.) are Step -1 human-locked; referenced
symbolically.
"""
from __future__ import annotations

from pathlib import Path

from backtest.wf_lineage import (
    check_evaluation_semantics_or_raise,
    check_wf_semantics_or_raise,
)
from strategies.dsl import (
    Condition,
    ConditionGroup,
    SizingBand,
    SizingSpec,
    StrategyDSL,
)
from strategies.dsl_compiler import compile_dsl_to_strategy

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATHB_EVAL_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/pathb_eval_gauntlet_v1"

# ---------------------------------------------------------------------------
# Step -1 LOCK: H1 parameter values (symbolic; do NOT change without LOCK update)
# ---------------------------------------------------------------------------

THETA_PUSH = -0.6
THETA_RANGE = 1.0   # LOCK: range_over_atr > 1.0 (meaningful displacement)
H1_MAX_HOLD = 3     # LOCK: max_hold_bars = 3

# H2 parameter values
THETA_Z_LOW = -1.0
THETA_Z_HIGH = 1.0
VOL_REGIME_SPLIT = 0.5  # cdf_realized_vol_720 median split
H2_MAX_HOLD = 24        # build-pinned time-stop (per-leg signal exit not DSL-expressible)

# H3 parameter values
DECAY_FAST = "decay_linear_close_48"
DECAY_SLOW = "decay_linear_close_168"
VOL_TOP_TAIL_GATE = 0.9  # LOCK: realized vol below its cdf_realized_vol_720 top-decile
H3_MAX_HOLD = 48         # build-pinned time-stop (trend held longer than H2)

# Stage -> guard name. train WF artifacts use the WF guard; every single-run
# evaluation (regime holdout, validation, Tier 5) uses the evaluation guard.
EVAL_GAUNTLET: dict[str, str] = {
    "train_wf": "check_wf_semantics_or_raise",
    "regime_holdout_2022": "check_evaluation_semantics_or_raise",
    "validation_2024": "check_evaluation_semantics_or_raise",
    "tier5": "check_evaluation_semantics_or_raise",
}


def build_h1_dsl() -> StrategyDSL:
    """H1 intrabar_push_fade, conforming to the Step -1 LOCK.

    Long when a large one-sided DOWN-push occurs at meaningful displacement
    (intrabar_push < -0.6 AND range_over_atr > 1.0); exit on reversion or
    after max_hold_bars=3. Vol-regime ternary sizing on cdf_realized_vol_720.
    """
    entry = ConditionGroup(conditions=[
        Condition(factor="intrabar_push", op="<", value=THETA_PUSH),
        Condition(factor="range_over_atr", op=">", value=THETA_RANGE),
    ])
    exit_grp = ConditionGroup(conditions=[
        Condition(factor="intrabar_push", op=">", value=0.0)
    ])
    sizing = SizingSpec(
        factor="cdf_realized_vol_720",
        bands=[SizingBand(lower=0.3, upper=0.8, size=1.0)],
        default_size=0.5,
    )
    return StrategyDSL(
        name="pathb_h1",
        description="Path B H1: fade a large-displacement one-sided down-push (mean-reversion), vol-regime ternary sizing.",
        entry=[entry],
        exit=[exit_grp],
        position_sizing=sizing,
        max_hold_bars=H1_MAX_HOLD,
    )


def build_h2_dsl() -> StrategyDSL:
    """H2 vol_regime_switch: LOW-vol mean-revert OR HIGH-vol trend, long/flat.

    Entry (OR of two regime legs):
      LOW : cdf_realized_vol_720 < 0.5 AND zscore_48 < -1.0  (oversold-in-calm)
      HIGH: cdf_realized_vol_720 >= 0.5 AND zscore_48 > +1.0 (breakout-in-stress)
    Exit: time-stop max_hold_bars=24 (per-leg signal-reversal exit is not
    cleanly expressible as OR-of-AND exit groups; build-pinned, B2-reviewed).
    Sizing: single-factor cdf_realized_vol_720 inverse-vol ternary (Decision 1).
    """
    low = ConditionGroup(conditions=[
        Condition(factor="cdf_realized_vol_720", op="<", value=VOL_REGIME_SPLIT),
        Condition(factor="zscore_48", op="<", value=THETA_Z_LOW),
    ])
    high = ConditionGroup(conditions=[
        Condition(factor="cdf_realized_vol_720", op=">=", value=VOL_REGIME_SPLIT),
        Condition(factor="zscore_48", op=">", value=THETA_Z_HIGH),
    ])
    # Exit on REGIME FLIP (the switch is the edge) + time-stop. A single global
    # exit condition cannot serve both opposite-signed entry legs (a zscore exit
    # true for the LOW leg is also true at HIGH entry, closing it same-bar). The
    # regime-flip cross is leg-symmetric: a LOW-leg long (cdf<0.5) closes when
    # cdf crosses ABOVE 0.5; a HIGH-leg long (cdf>=0.5) closes when cdf crosses
    # BELOW 0.5. max_hold_bars=24 is the backstop.
    exit_up = ConditionGroup(conditions=[
        Condition(factor="cdf_realized_vol_720", op="crosses_above", value=VOL_REGIME_SPLIT)
    ])
    exit_down = ConditionGroup(conditions=[
        Condition(factor="cdf_realized_vol_720", op="crosses_below", value=VOL_REGIME_SPLIT)
    ])
    sizing = SizingSpec(
        factor="cdf_realized_vol_720",
        bands=[SizingBand(lower=0.0, upper=VOL_REGIME_SPLIT, size=1.0)],
        default_size=0.5,
    )
    return StrategyDSL(
        name="pathb_h2",
        description="Path B H2: vol-regime switch (low-vol revert / high-vol trend), long/flat, single-factor inverse-vol sizing.",
        entry=[low, high],
        exit=[exit_up, exit_down],
        position_sizing=sizing,
        max_hold_bars=H2_MAX_HOLD,
    )


def build_h3_dsl() -> StrategyDSL:
    """H3 decay_trend_persistence: long while fast decay-MA leads slow, ex top-vol.

    Entry: decay_linear_close_48 > decay_linear_close_168 (factor-vs-factor)
           AND cdf_realized_vol_720 <= 0.9 (not in the vol top-decile).
    Exit: trend break (fast <= slow) or time-stop max_hold_bars=48.
    Sizing: single-factor cdf_realized_vol_720 ternary (Decision 1).
    """
    entry = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op=">", value=DECAY_SLOW),
        Condition(factor="cdf_realized_vol_720", op="<=", value=VOL_TOP_TAIL_GATE),
    ])
    exit_grp = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op="<=", value=DECAY_SLOW)
    ])
    sizing = SizingSpec(
        factor="cdf_realized_vol_720",
        bands=[SizingBand(lower=0.0, upper=0.5, size=1.0)],
        default_size=0.5,
    )
    return StrategyDSL(
        name="pathb_h3",
        description="Path B H3: decay-MA trend persistence (fast leads slow), ex vol top-decile, single-factor sizing.",
        entry=[entry],
        exit=[exit_grp],
        position_sizing=sizing,
        max_hold_bars=H3_MAX_HOLD,
    )


def build_all_hypotheses() -> dict[str, StrategyDSL]:
    """The full N*=3 pre-registered grid (one variant each)."""
    return {"H1": build_h1_dsl(), "H2": build_h2_dsl(), "H3": build_h3_dsl()}


def route_guard(stage: str, summary: dict, *, artifact_path: str | None = None) -> None:
    """Dispatch the correct wf_lineage guard for a gauntlet stage.

    Args:
        stage: One of EVAL_GAUNTLET's keys.
        summary: The artifact summary dict to validate.
        artifact_path: Optional source path for diagnostics.

    Raises:
        ValueError: If ``stage`` is unknown, or propagated from the guard.
    """
    guard_name = EVAL_GAUNTLET.get(stage)
    if guard_name is None:
        raise ValueError(f"unknown gauntlet stage {stage!r} (known: {sorted(EVAL_GAUNTLET)})")
    guard = (
        check_wf_semantics_or_raise
        if guard_name == "check_wf_semantics_or_raise"
        else check_evaluation_semantics_or_raise
    )
    guard(summary, artifact_path=artifact_path)


def compile_hypothesis() -> type:
    """Compile the H1 DSL to a Backtrader strategy class (manifest suppressed).

    Returns:
        The compiled strategy class.
    """
    return compile_dsl_to_strategy(build_h1_dsl(), write_manifest=False)
