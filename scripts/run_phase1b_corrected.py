"""Phase 1B baseline corrected-engine rerun.

Reruns the 4 sealed Phase 1B hand-written baselines under the
corrected WF engine (per docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md).
Produces per-baseline + aggregate artifacts with corrected-engine
lineage metadata stamped at both levels.

This script establishes the first authoritative v2 walk-forward
baseline publication for Phase 1B under the corrected engine —
prior registry rows for these baselines are not treated as sealed
canonical baselines (the original closeout only published single-run
2024 H1 numbers, not v2 WF aggregates).

Sealed Phase 1B v2 split (from config/environments.yaml):
  train_windows: 2020-2021 + 2023 (disjoint)
  holdout: 2022 (regime-holdout, NOT used here — see run_regime_holdout)
  validation: 2024
  test: 2025

CLI surface:
    --baseline {sma_crossover|momentum|mean_reversion|volatility_breakout}
    --all                 (default if neither --baseline nor --all)
    --batch-id <id>       (default: fresh UUID)
    --output-root <path>  (default: data/phase1b_corrected/)
    --dry-run             Print resolved configuration and exit before
                          engine execution. Lineage guard IS invoked.
    --force               Allow overwriting an existing batch directory.

Lineage guard ordering: parse_args() runs first (so --help works
without invoking git), then enforce_corrected_engine_lineage() runs
before any engine execution or artifact write.
"""
from __future__ import annotations

import argparse
import json
import logging
import statistics
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backtest.engine import WalkForwardResult, run_walk_forward  # noqa: E402
from backtest.wf_lineage import (  # noqa: E402
    CORRECTED_WF_ENGINE_COMMIT,
    WF_SEMANTICS_TAG,
    check_wf_semantics_or_raise,
    enforce_corrected_engine_lineage,
)
from strategies.baseline.mean_reversion import MeanReversion  # noqa: E402
from strategies.baseline.momentum import Momentum  # noqa: E402
from strategies.baseline.sma_crossover import SMACrossover  # noqa: E402
from strategies.baseline.volatility_breakout import VolatilityBreakout  # noqa: E402

logger = logging.getLogger(__name__)


BASELINES: dict[str, type] = {
    "sma_crossover": SMACrossover,
    "momentum": Momentum,
    "mean_reversion": MeanReversion,
    "volatility_breakout": VolatilityBreakout,
}

DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "phase1b_corrected"
ENV_CONFIG_PATH = PROJECT_ROOT / "config" / "environments.yaml"
SPLIT_VERSION = "v2"


# ---------------------------------------------------------------------------
# Per-CSV helpers
# ---------------------------------------------------------------------------


_CSV_FIELDS: tuple[str, ...] = (
    "baseline",
    "window_index",
    "train_start",
    "train_end",
    "test_start",
    "test_end",
    "total_return",
    "sharpe_ratio",
    "max_drawdown",
    "max_drawdown_duration_hours",
    "total_trades",
    "win_rate",
    "warmup_bars",
    "effective_start",
)


def _utc_now_iso() -> str:
    """Return current UTC time as ISO 8601 string with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class V2Splits:
    """Resolved v2 split values from environments.yaml."""

    split_version: str
    train_windows: list[list[str]]
    holdout_reserved: list[str]
    split_resolved_from: str


def _load_v2_splits() -> V2Splits:
    """Load v2 splits from environments.yaml; return as serializable shape."""
    with open(ENV_CONFIG_PATH) as f:
        env_config = yaml.safe_load(f)
    splits = env_config.get("splits", {})
    train_windows = [
        [entry[0], entry[1]] for entry in splits.get("train_windows", [])
    ]
    holdout = splits.get("regime_holdout", {})
    holdout_reserved = [holdout.get("start"), holdout.get("end")]
    version = env_config.get("version", "unknown")
    return V2Splits(
        split_version=version,
        train_windows=train_windows,
        holdout_reserved=holdout_reserved,
        split_resolved_from=str(ENV_CONFIG_PATH.relative_to(PROJECT_ROOT)),
    )


def _lineage_metadata(head_sha: str, splits: V2Splits) -> dict[str, Any]:
    """Build the lineage metadata block stamped into every summary."""
    return {
        "wf_semantics": WF_SEMANTICS_TAG,
        "corrected_wf_semantics_commit": CORRECTED_WF_ENGINE_COMMIT,
        "current_git_sha": head_sha,
        "lineage_check": "passed",
        "split_version": splits.split_version,
        "train_windows": splits.train_windows,
        "holdout_reserved": splits.holdout_reserved,
        "split_resolved_from": splits.split_resolved_from,
    }


def _baseline_summary_dict(
    baseline_name: str,
    wf_result: WalkForwardResult,
    head_sha: str,
    splits: V2Splits,
    run_started_utc: str,
    run_finished_utc: str,
) -> dict[str, Any]:
    """Build the per-baseline summary JSON dict."""
    sm = wf_result.summary_metrics
    summary: dict[str, Any] = _lineage_metadata(head_sha, splits)
    summary.update({
        "baseline": baseline_name,
        "summary_run_id": wf_result.summary_run_id,
        "run_started_utc": run_started_utc,
        "run_finished_utc": run_finished_utc,
        "n_windows": len(wf_result.window_results),
        "wf_metrics": {
            "sharpe_ratio": float(sm.get("sharpe_ratio", 0.0)),
            "total_return": float(sm.get("total_return", 0.0)),
            "max_drawdown": float(sm.get("max_drawdown", 0.0)),
            "total_trades": int(sm.get("total_trades", 0)),
            "win_rate": float(sm.get("win_rate", 0.0)),
        },
    })
    return summary


def _aggregate_summary_dict(
    baseline_summaries: dict[str, dict[str, Any]],
    head_sha: str,
    splits: V2Splits,
    batch_id: str,
    run_started_utc: str,
    run_finished_utc: str,
) -> dict[str, Any]:
    """Build the aggregate-level summary JSON dict."""
    summary: dict[str, Any] = _lineage_metadata(head_sha, splits)
    baselines_run = sorted(baseline_summaries.keys())
    sharpes = [
        baseline_summaries[b]["wf_metrics"]["sharpe_ratio"]
        for b in baselines_run
    ]
    returns = [
        baseline_summaries[b]["wf_metrics"]["total_return"]
        for b in baselines_run
    ]
    aggregate_metrics: dict[str, Any] = {
        "n_baselines": len(baselines_run),
        "mean_sharpe_across_baselines": (
            float(statistics.fmean(sharpes)) if sharpes else None
        ),
        "median_sharpe_across_baselines": (
            float(statistics.median(sharpes)) if sharpes else None
        ),
        "mean_return_across_baselines": (
            float(statistics.fmean(returns)) if returns else None
        ),
    }
    summary.update({
        "batch_id": batch_id,
        "run_started_utc": run_started_utc,
        "run_finished_utc": run_finished_utc,
        "baselines_run": baselines_run,
        "per_baseline_summary_paths": {
            b: f"{b}/walk_forward_summary.json" for b in baselines_run
        },
        "aggregate_metrics": aggregate_metrics,
    })
    return summary


def _write_per_baseline_csv(
    baseline_name: str,
    wf_result: WalkForwardResult,
    csv_path: Path,
) -> None:
    """Write the per-window CSV for a single baseline."""
    import csv

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for i, (window, br) in enumerate(
            zip(wf_result.windows, wf_result.window_results), start=1
        ):
            train_start, train_end, test_start, test_end = window
            m = br.metrics
            row = {
                "baseline": baseline_name,
                "window_index": i,
                "train_start": train_start.isoformat(),
                "train_end": train_end.isoformat(),
                "test_start": test_start.isoformat(),
                "test_end": test_end.isoformat(),
                "total_return": f"{float(m.get('total_return', 0.0)):.6f}",
                "sharpe_ratio": f"{float(m.get('sharpe_ratio', 0.0)):.6f}",
                "max_drawdown": f"{float(m.get('max_drawdown', 0.0)):.6f}",
                "max_drawdown_duration_hours": int(
                    m.get("max_drawdown_duration_hours", 0) or 0
                ),
                "total_trades": int(m.get("total_trades", 0)),
                "win_rate": f"{float(m.get('win_rate', 0.0)):.6f}",
                "warmup_bars": int(br.warmup_bars),
                "effective_start": (
                    br.effective_start.isoformat()
                    if br.effective_start is not None else ""
                ),
            }
            writer.writerow(row)


def _write_summary_with_validation(
    summary: dict[str, Any], summary_path: Path
) -> None:
    """Write a summary JSON, then immediately reload + validate via the consumer guard.

    Round-trip validation per Step 3b of the task spec: prove the
    producer-consumer contract works on real Phase 1B artifacts.
    """
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with open(summary_path) as f:
        reloaded = json.load(f)
    check_wf_semantics_or_raise(reloaded, artifact_path=str(summary_path))


# ---------------------------------------------------------------------------
# Per-baseline driver
# ---------------------------------------------------------------------------


def _run_one_baseline(
    baseline_name: str,
    head_sha: str,
    splits: V2Splits,
    output_root: Path,
) -> dict[str, Any]:
    """Run a single baseline through the corrected WF engine.

    Returns the per-baseline summary dict.
    """
    if baseline_name not in BASELINES:
        raise ValueError(
            f"unknown baseline {baseline_name!r}; "
            f"valid: {sorted(BASELINES.keys())}"
        )
    strategy_cls = BASELINES[baseline_name]
    baseline_dir = output_root / baseline_name

    run_started_utc = _utc_now_iso()
    logger.info(
        "[%s] starting corrected v2 WF run...", baseline_name
    )

    wf_result = run_walk_forward(strategy_cls=strategy_cls)

    run_finished_utc = _utc_now_iso()

    csv_path = baseline_dir / "walk_forward_results.csv"
    _write_per_baseline_csv(baseline_name, wf_result, csv_path)

    summary = _baseline_summary_dict(
        baseline_name=baseline_name,
        wf_result=wf_result,
        head_sha=head_sha,
        splits=splits,
        run_started_utc=run_started_utc,
        run_finished_utc=run_finished_utc,
    )
    summary_path = baseline_dir / "walk_forward_summary.json"
    _write_summary_with_validation(summary, summary_path)

    logger.info(
        "[%s] DONE — sharpe=%.4f return=%.4f max_dd=%.4f trades=%d windows=%d",
        baseline_name,
        summary["wf_metrics"]["sharpe_ratio"],
        summary["wf_metrics"]["total_return"],
        summary["wf_metrics"]["max_drawdown"],
        summary["wf_metrics"]["total_trades"],
        summary["n_windows"],
    )
    return summary


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 1B baseline corrected-engine rerun. Runs the 4 sealed "
            "hand-written baselines through the corrected WF engine "
            "(eb1c87f / wf-corrected-v1) under the v2 split, producing "
            "per-baseline + aggregate artifacts with lineage metadata "
            "stamped at both levels."
        ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--baseline",
        type=str,
        choices=sorted(BASELINES.keys()),
        default=None,
        help="Run a single baseline. Mutually exclusive with --all.",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help=(
            "Run all 4 baselines sequentially. Default if neither "
            "--baseline nor --all is passed."
        ),
    )
    parser.add_argument(
        "--batch-id",
        type=str,
        default=None,
        help="Explicit batch ID. Default: a fresh UUID.",
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Override output root. Default: data/phase1b_corrected/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Print resolved configuration and exit before any engine call "
            "or artifact write. The lineage guard IS still invoked."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Allow overwriting an existing batch directory. Without "
            "--force, the script refuses to overwrite a non-empty batch "
            "directory."
        ),
    )
    return parser


def _resolve_baselines_to_run(args: argparse.Namespace) -> list[str]:
    if args.baseline is not None:
        return [args.baseline]
    # --all OR neither flag → run all
    return sorted(BASELINES.keys())


def _resolve_batch_id(args: argparse.Namespace) -> str:
    return args.batch_id or str(uuid.uuid4())


def _check_overwrite_protection(
    batch_dir: Path, force: bool
) -> int | None:
    """Return non-None exit code if batch_dir exists non-empty and not --force.

    A truly empty directory is allowed to proceed (idempotent re-create).
    """
    if not batch_dir.exists():
        return None
    try:
        non_empty = any(batch_dir.iterdir())
    except OSError:
        non_empty = True
    if non_empty and not force:
        print(
            f"\nERROR: batch directory {batch_dir} already exists and is "
            f"non-empty. Re-run with --force to overwrite, or pass a "
            f"different --batch-id.",
            file=sys.stderr,
        )
        return 1
    return None


def main() -> int:
    """Entry point.

    Order of operations (load-bearing):
      1. parse_args() (so --help works without invoking git).
      2. enforce_corrected_engine_lineage() (before ANY engine run or
         artifact write).
      3. Resolve splits, batch_id, output dir.
      4. Overwrite-protection gate.
      5. (--dry-run) print resolved config and exit.
      6. Per-baseline runs (each writes per-baseline CSV + summary,
         each summary is round-trip validated against the consumer
         guard).
      7. Aggregate summary write + round-trip validation.
    """
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        level=logging.INFO,
    )

    args = _build_argparser().parse_args()

    # Lineage guard runs AFTER parse_args (so --help works without git)
    # and BEFORE any engine execution or artifact write. Even --dry-run
    # invokes the guard — the guard is part of "would this run produce
    # valid corrected artifacts?".
    head_sha = enforce_corrected_engine_lineage()

    splits = _load_v2_splits()
    batch_id = _resolve_batch_id(args)
    output_root = Path(args.output_root).resolve() / batch_id
    baselines_to_run = _resolve_baselines_to_run(args)

    print(f"[Phase 1B corrected] batch_id: {batch_id}")
    print(f"[Phase 1B corrected] head_sha: {head_sha}")
    print(f"[Phase 1B corrected] split_version: {splits.split_version}")
    print(f"[Phase 1B corrected] train_windows: {splits.train_windows}")
    print(f"[Phase 1B corrected] holdout_reserved: {splits.holdout_reserved}")
    print(f"[Phase 1B corrected] output_root: {output_root}")
    print(f"[Phase 1B corrected] baselines_to_run: {baselines_to_run}")
    print(f"[Phase 1B corrected] dry_run: {args.dry_run}")
    print(f"[Phase 1B corrected] force: {args.force}")

    rc = _check_overwrite_protection(output_root, args.force)
    if rc is not None:
        return rc

    if args.dry_run:
        print("\n[Phase 1B corrected] --dry-run: stopping before engine "
              "execution and artifact writes.")
        return 0

    output_root.mkdir(parents=True, exist_ok=True)

    run_started_utc = _utc_now_iso()
    baseline_summaries: dict[str, dict[str, Any]] = {}
    for name in baselines_to_run:
        summary = _run_one_baseline(
            baseline_name=name,
            head_sha=head_sha,
            splits=splits,
            output_root=output_root,
        )
        baseline_summaries[name] = summary
    run_finished_utc = _utc_now_iso()

    aggregate_summary = _aggregate_summary_dict(
        baseline_summaries=baseline_summaries,
        head_sha=head_sha,
        splits=splits,
        batch_id=batch_id,
        run_started_utc=run_started_utc,
        run_finished_utc=run_finished_utc,
    )
    aggregate_path = output_root / "walk_forward_summary.json"
    _write_summary_with_validation(aggregate_summary, aggregate_path)

    print("\n[Phase 1B corrected] === AGGREGATE ===")
    am = aggregate_summary["aggregate_metrics"]
    print(f"  n_baselines: {am['n_baselines']}")
    print(f"  mean_sharpe_across_baselines: {am['mean_sharpe_across_baselines']}")
    print(f"  median_sharpe_across_baselines: {am['median_sharpe_across_baselines']}")
    print(f"  mean_return_across_baselines: {am['mean_return_across_baselines']}")
    print(f"\n[Phase 1B corrected] aggregate summary: {aggregate_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
