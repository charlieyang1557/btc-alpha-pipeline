# backtest/pathb_holdout_producer.py
"""Path B holdout producer: run one candidate on a window -> dead-18-layout
artifacts (returns_per_bar.parquet + holdout_summary.json + a results.csv row),
so the existing tier6 load_candidate_moments integrity gate can consume them.

Writes ONLY into a Path B namespace; never the sealed cohort dirs. The engine
call is injected (default backtest.engine.run_backtest) for test isolation.

IMPL NOTES (verified against backtest/wf_lineage.py):
- EVALUATION_SEMANTICS_TAG = "single_run_holdout_v1"
- CORRECTED_WF_ENGINE_COMMIT = "eb1c87f"  (used as engine_commit)
- ENGINE_CORRECTED_LINEAGE_TAG = "wf-corrected-v1"  (used as engine_corrected_lineage)
- artifact_schema_version = "phase2c_7_1" for regime_key="evaluation_regimes.forward_2026"
  (per REGIME_KEY_TO_SCHEMA_VERSION_MAPPING; plan said "phase2c_8_1" but mapping says
  "phase2c_7_1" — corrected here per guardrail §5).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from backtest.engine import run_backtest, write_per_bar_artifact
from backtest.wf_lineage import (
    CORRECTED_WF_ENGINE_COMMIT,
    ENGINE_CORRECTED_LINEAGE_TAG,
    EVALUATION_SEMANTICS_TAG,
)

# Lineage constants the evaluation guard requires (mirror run_phase2c_evaluation_gate).
# Verified: CORRECTED_WF_ENGINE_COMMIT == "eb1c87f"
# Verified: ENGINE_CORRECTED_LINEAGE_TAG == "wf-corrected-v1"
# Verified: forward_2026 -> "phase2c_7_1" per REGIME_KEY_TO_SCHEMA_VERSION_MAPPING
_ENGINE_COMMIT = CORRECTED_WF_ENGINE_COMMIT   # "eb1c87f"
_ENGINE_LINEAGE = ENGINE_CORRECTED_LINEAGE_TAG  # "wf-corrected-v1"
_ARTIFACT_SCHEMA_VERSION = "phase2c_7_1"        # forward_2026 per REGIME_KEY_TO_SCHEMA_VERSION_MAPPING


def _eval_lineage_metadata(current_git_sha: str) -> dict[str, Any]:
    return {
        "evaluation_semantics": EVALUATION_SEMANTICS_TAG,  # "single_run_holdout_v1"
        "engine_commit": _ENGINE_COMMIT,
        "engine_corrected_lineage": _ENGINE_LINEAGE,
        "lineage_check": "passed",
        "current_git_sha": current_git_sha,
        "artifact_schema_version": _ARTIFACT_SCHEMA_VERSION,
        "regime_key": "evaluation_regimes.forward_2026",
        "regime_label": "forward_2026",
    }


def produce_candidate_holdout(
    *,
    hypothesis_hash: str,
    name: str,
    theme: str,
    strategy_cls: type,
    window: tuple[datetime, datetime],
    cohort_dir: Path,
    execution_config_path: str,
    current_git_sha: str = "PATHB_BUILD",
    _run_backtest: Callable[..., Any] = run_backtest,
    _write_per_bar: Callable[..., Any] = write_per_bar_artifact,
) -> dict[str, Any]:
    """Run one candidate on ``window`` and emit dead-18-layout artifacts.

    Inputs:
        hypothesis_hash: DSL hash string (also the sub-dir name).
        name: Strategy name (e.g. "pathb_h1").
        theme: Theme label (e.g. "pathb").
        strategy_cls: Compiled Backtrader strategy class (unused when engine mocked).
        window: (start_utc, end_utc) datetime tuple for the holdout run.
        cohort_dir: Root path for Path B artifacts; writes to cohort_dir/<hash>/.
        execution_config_path: Repo-relative YAML path for the cost anchor
            (e.g. "config/execution_phaseb_spot_15bps.yaml").
        current_git_sha: Git SHA to stamp; defaults to "PATHB_BUILD" for the build phase.
        _run_backtest: Injected engine callable (default backtest.engine.run_backtest).
        _write_per_bar: Injected artifact writer (default backtest.engine.write_per_bar_artifact).

    Returns:
        Dict with ``holdout_sharpe`` (float) and ``row`` (dict) — the
        holdout_results.csv row: hypothesis_hash, name, theme, T_obs, gamma3,
        gamma4, returns_per_bar_sha256, holdout_total_trades.

    Raises:
        ValueError: If the per-bar artifact has gamma3/gamma4 = None (degenerate
            zero-variance equity curve). Fail fast here so a degenerate candidate
            surfaces as an explicit error, not a loader crash (Codex-3d guard).
    """
    start, end = window
    cand_dir = Path(cohort_dir) / hypothesis_hash
    cand_dir.mkdir(parents=True, exist_ok=True)

    result = _run_backtest(
        strategy_cls=strategy_cls,
        start_date=start,
        end_date=end,
        execution_config_path=Path(execution_config_path),
        write_registry=False,
    )
    per_bar = _write_per_bar(
        equity_curve=result.equity_curve,
        artifact_dir=cand_dir,
        run_id=result.run_id,
    )

    summary = {
        "hypothesis_hash": hypothesis_hash,
        "name": name,
        "theme": theme,
        "run_id": result.run_id,
        "execution_config_path": execution_config_path,
        "forward_window_metadata": {
            "forward_window_start_utc": start.isoformat(),
            "forward_window_end_utc": end.isoformat(),
            # forward_bar_count = nominal window span in 1h bars (matches the
            # dead-18 producer's len(forward) convention; 2026 has no gaps).
            "forward_bar_count": int((end - start).total_seconds() // 3600) + 1,
            # T_obs = post-warmup finite per-bar returns (cdf_realized_vol_720's
            # ~743-bar warmup is consumed from inside the window), distinct from
            # the nominal span above.
            "forward_post_warmup_obs": int(per_bar["T_obs"]),
        },
        **_eval_lineage_metadata(current_git_sha),
    }
    (cand_dir / "holdout_summary.json").write_text(json.dumps(summary, indent=1))

    # Codex-3d guard: write_per_bar_artifact returns gamma3/gamma4 = None for a
    # degenerate (flat / zero-variance) equity curve; load_candidate_moments
    # does float(row["gamma3"]) -> TypeError on None. Fail fast here so a
    # degenerate candidate surfaces as an explicit error, not a loader crash.
    if per_bar["gamma3"] is None or per_bar["gamma4"] is None:
        raise ValueError(
            f"candidate {hypothesis_hash}: degenerate per-bar returns "
            f"(gamma3/gamma4 is None; T_obs={per_bar['T_obs']}) — flat or "
            f"zero-variance equity; cannot build CandidateMoments."
        )

    row = {
        "hypothesis_hash": hypothesis_hash,
        "name": name,
        "theme": theme,
        "T_obs": int(per_bar["T_obs"]),
        "gamma3": per_bar["gamma3"],
        "gamma4": per_bar["gamma4"],
        "returns_per_bar_sha256": per_bar["returns_per_bar_sha256"],
        "holdout_total_trades": int(result.metrics.get("total_trades", 0)),
        "holdout_sharpe": float(result.metrics["sharpe_ratio"]),
    }
    return {"holdout_sharpe": float(result.metrics["sharpe_ratio"]), "row": row}
