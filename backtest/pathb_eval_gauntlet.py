# backtest/pathb_eval_gauntlet.py
"""Path B hypothesis DSL builder + evaluation gauntlet stage->guard routing.

build_hypothesis_dsl constructs the locked H-grid DSL using the REAL DSL/
compiler API (Condition(value=...) — NOT threshold; StrategyDSL(description=...,
entry=..., exit=..., position_sizing=...); compile_dsl_to_strategy(...) — NOT
compile_strategy).

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
    SizingSpec,
    StrategyDSL,
)
from strategies.dsl_compiler import compile_dsl_to_strategy

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATHB_EVAL_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/pathb_eval_gauntlet_v1"

# Step -1 human-locked hypothesis param value (symbolic; H1 fades a DOWN-push).
THETA_PUSH = -0.6

# Stage -> guard name. train WF artifacts use the WF guard; every single-run
# evaluation (regime holdout, validation, Tier 5) uses the evaluation guard.
EVAL_GAUNTLET: dict[str, str] = {
    "train_wf": "check_wf_semantics_or_raise",
    "regime_holdout_2022": "check_evaluation_semantics_or_raise",
    "validation_2024": "check_evaluation_semantics_or_raise",
    "tier5": "check_evaluation_semantics_or_raise",
}


def build_hypothesis_dsl() -> StrategyDSL:
    """Build the H1 hypothesis DSL using the real DSL + compiler contract.

    H1 (spec §3) is microstructure MEAN-REVERSION: long when intrabar_push <
    THETA_PUSH (fade a one-sided DOWN-push), exit when the push reverts, with a
    vol-regime ternary SizingSpec on cdf_realized_vol_720 (NOT zscore_48 — that
    is H2's factor).

    Returns:
        A valid StrategyDSL (entry on intrabar_push < THETA_PUSH = fade a
        down-push) with a vol-regime ternary SizingSpec on a registered factor.
    """
    entry = ConditionGroup(
        conditions=[Condition(factor="intrabar_push", op="<", value=THETA_PUSH)]
    )
    exit_grp = ConditionGroup(
        conditions=[Condition(factor="intrabar_push", op=">", value=0.0)]
    )
    # H1 sizing is a vol-regime ternary on cdf_realized_vol_720 (spec §3 H1):
    # full size in the mid-vol band [0.3, 0.8], half outside. NOT zscore_48.
    sizing = SizingSpec(
        factor="cdf_realized_vol_720",
        bands=[{"lower": 0.3, "upper": 0.8, "size": 1.0}],
        default_size=0.5,
    )
    return StrategyDSL(
        name="pathb_h1",
        description="Path B H1: fade a one-sided down-push (mean-reversion), vol-regime ternary sizing on cdf_realized_vol_720.",
        entry=[entry],
        exit=[exit_grp],
        position_sizing=sizing,
        max_hold_bars=24,
    )


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
    return compile_dsl_to_strategy(build_hypothesis_dsl(), write_manifest=False)
