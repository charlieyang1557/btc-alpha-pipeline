"""Phase 2C evaluation gate — regime holdout AND-gate against corrected candidates.

Runs the 2022 regime holdout AND-gate (per config/environments.yaml +
backtest.engine._evaluate_regime_holdout_pass) against Phase 2C
corrected candidates. Per docs/phase2c/PHASE2C_6_EVALUATION_GATE_PLAN.md.

Three reusable engine entry points called by this script:
    - backtest.engine.run_regime_holdout: top-level wrapper
    - backtest.engine._evaluate_regime_holdout_pass: 4-condition AND gate
    - backtest.engine._load_regime_block_config: parameterized env config
      loader (renamed from _load_regime_holdout_config in PHASE2C_7.1
      sub-step 1.2 to support multi-regime evaluation; the
      regime_holdout block remains the default for backward-compat)

Two attestation domains kept separate per backtest/wf_lineage.py:
    - WF artifacts: walk_forward_results / walk_forward_summary use
      wf_semantics='corrected_test_boundary_v1' (NOT used here)
    - Single-run holdout artifacts: this script's outputs use
      evaluation_semantics='single_run_holdout_v1' + the 4 lineage fields
      validated by check_evaluation_semantics_or_raise()

CLI surface:
    --source-batch-id <phase2c_batch_uuid>  Upstream Phase 2C proposer batch
                                            whose corrected candidates are
                                            evaluated. Default: b6fcbf86-...
    --universe primary|audit                primary=44 corrected winners;
                                            audit=all 198 corrected candidates
    --candidate-hashes <csv>                Comma-separated 8+ char hash
                                            prefixes. Mutually exclusive with
                                            --universe.
    --run-id <id>                           Identifier for THIS evaluation run
                                            (smoke_v1, or auto-UUID4).
    --output-root <path>                    Default: data/phase2c_evaluation_gate/
    --dry-run                               Verify config + candidate selection
                                            without running backtests.
    --force                                 Allow overwriting non-empty
                                            <output-root>/<run-id>/.

Lineage guard ordering: parse_args() runs first (so --help works
without invoking git), then enforce_corrected_engine_lineage() runs
before any engine execution or artifact write.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backtest.engine import run_regime_holdout, RegimeHoldoutResult  # noqa: E402
from backtest.wf_lineage import (  # noqa: E402
    CORRECTED_WF_ENGINE_COMMIT,
    ENGINE_CORRECTED_LINEAGE_TAG,
    EVALUATION_SEMANTICS_TAG,
    check_evaluation_semantics_or_raise,
    enforce_corrected_engine_lineage,
)
from strategies.dsl import StrategyDSL  # noqa: E402

logger = logging.getLogger(__name__)

DEFAULT_SOURCE_BATCH_ID = "b6fcbf86-4d57-4d1f-ae41-1778296b1ae9"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "phase2c_evaluation_gate"
DEFAULT_CORRECTED_BATCH_ROOT = (
    PROJECT_ROOT / "data" / "phase2c_walkforward"
)
DEFAULT_RAW_PAYLOADS_DIR = PROJECT_ROOT / "raw_payloads"

PRIMARY_THRESHOLD = 0.5  # corrected wf_test_period_sharpe > this = primary winner

# Markdown fence regex matching scripts/run_phase2c_batch_walkforward.py
_FENCE_RE = re.compile(
    r"```(?:\s*json)?\s*(.*?)\s*```",
    re.DOTALL | re.IGNORECASE,
)


def _strip_markdown_fence(raw: str) -> str:
    """Strip markdown code fence; return contents if found, else raw."""
    m = _FENCE_RE.search(raw)
    return m.group(1) if m else raw


def _utc_now_iso() -> str:
    """Return current UTC time as ISO-8601 with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Candidate selection
# ---------------------------------------------------------------------------


def _load_corrected_candidates(source_batch_id: str) -> list[dict[str, Any]]:
    """Load all 198 corrected candidates from the corrected CSV.

    Returns one dict per candidate with: hypothesis_hash, position, theme,
    name, wf_test_period_sharpe.
    """
    corrected_dir = (
        DEFAULT_CORRECTED_BATCH_ROOT
        / f"batch_{source_batch_id}_corrected"
    )
    csv_path = corrected_dir / "walk_forward_results.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Corrected Phase 2C CSV not found at {csv_path}. "
            f"Verify --source-batch-id is correct."
        )
    candidates: list[dict[str, Any]] = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            candidates.append({
                "hypothesis_hash": row["hypothesis_hash"],
                "position": int(row["position"]),
                "theme": row["theme"],
                "name": row["name"],
                "wf_test_period_sharpe": float(
                    row["wf_test_period_sharpe"]
                ) if row["wf_test_period_sharpe"] else 0.0,
            })
    return candidates


def _resolve_candidate_universe(
    args: argparse.Namespace,
    all_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Apply --universe / --candidate-hashes to the full candidate list."""
    if args.candidate_hashes:
        prefixes = [
            h.strip() for h in args.candidate_hashes.split(",") if h.strip()
        ]
        selected: list[dict[str, Any]] = []
        for prefix in prefixes:
            matches = [
                c for c in all_candidates
                if c["hypothesis_hash"].startswith(prefix)
            ]
            if len(matches) == 0:
                raise ValueError(
                    f"--candidate-hashes prefix {prefix!r} matched no "
                    f"candidate in source batch."
                )
            if len(matches) > 1:
                raise ValueError(
                    f"--candidate-hashes prefix {prefix!r} matched "
                    f"{len(matches)} candidates (ambiguous): "
                    f"{[m['hypothesis_hash'] for m in matches]}"
                )
            selected.append(matches[0])
        return selected
    if args.universe == "primary":
        return [
            c for c in all_candidates
            if c["wf_test_period_sharpe"] > PRIMARY_THRESHOLD
        ]
    # audit: all 198
    return list(all_candidates)


# ---------------------------------------------------------------------------
# DSL re-extraction from raw_payloads
# ---------------------------------------------------------------------------


def _load_dsl_from_response(
    source_batch_id: str, position: int
) -> StrategyDSL:
    """Re-extract a candidate's DSL from raw_payloads/.../attempt_NNNN_response.txt."""
    response_path = (
        DEFAULT_RAW_PAYLOADS_DIR
        / f"batch_{source_batch_id}"
        / f"attempt_{position:04d}_response.txt"
    )
    if not response_path.exists():
        raise FileNotFoundError(
            f"raw_payloads response file not found at {response_path}"
        )
    raw_text = response_path.read_text(encoding="utf-8")
    payload = json.loads(_strip_markdown_fence(raw_text))
    return StrategyDSL.model_validate(payload)


# ---------------------------------------------------------------------------
# Lineage stamping
# ---------------------------------------------------------------------------


def _lineage_metadata(head_sha: str) -> dict[str, str]:
    """Construct the 5-field lineage metadata block for single-run holdout artifacts."""
    return {
        "evaluation_semantics": EVALUATION_SEMANTICS_TAG,
        "engine_commit": CORRECTED_WF_ENGINE_COMMIT,
        "engine_corrected_lineage": ENGINE_CORRECTED_LINEAGE_TAG,
        "current_git_sha": head_sha,
        "lineage_check": "passed",
    }


# ---------------------------------------------------------------------------
# Per-candidate evaluation
# ---------------------------------------------------------------------------


def _per_candidate_summary(
    candidate: dict[str, Any],
    head_sha: str,
    source_batch_id: str,
    run_id: str,
    holdout_result: RegimeHoldoutResult | None,
    lifecycle_state: str,
    error_message: str | None,
    wall_clock_seconds: float,
) -> dict[str, Any]:
    """Build the per-candidate summary dict.

    For lifecycle_state == 'holdout_error', the 4 gate metrics and 4
    pass/fail flags are null per the regime_holdout_passed: bool | None
    pattern in backtest/engine.py:502.
    """
    summary: dict[str, Any] = {
        "source_batch_id": source_batch_id,
        "run_id": run_id,
        "hypothesis_hash": candidate["hypothesis_hash"],
        "position": candidate["position"],
        "theme": candidate["theme"],
        "name": candidate["name"],
        "wf_test_period_sharpe": candidate["wf_test_period_sharpe"],
        "lifecycle_state": lifecycle_state,
        "error_message": error_message,
        "wall_clock_seconds": round(wall_clock_seconds, 4),
    }
    if holdout_result is not None:
        passing_criteria = holdout_result.passing_criteria
        summary["holdout_metrics"] = {
            "sharpe_ratio": holdout_result.sharpe_ratio,
            "max_drawdown": holdout_result.max_drawdown,
            "total_return": holdout_result.total_return,
            "total_trades": holdout_result.total_trades,
        }
        summary["passing_criteria"] = passing_criteria
        summary["gate_pass_per_criterion"] = {
            "sharpe_passed": (
                holdout_result.sharpe_ratio
                >= passing_criteria["min_sharpe"]
            ),
            "drawdown_passed": (
                holdout_result.max_drawdown
                <= passing_criteria["max_drawdown"]
            ),
            "return_passed": (
                holdout_result.total_return
                >= passing_criteria["min_total_return"]
            ),
            "trades_passed": (
                holdout_result.total_trades
                >= passing_criteria["min_total_trades"]
            ),
        }
        summary["holdout_passed"] = holdout_result.regime_holdout_passed
    else:
        # holdout_error: gate didn't run, all gate fields are null
        summary["holdout_metrics"] = None
        summary["passing_criteria"] = None
        summary["gate_pass_per_criterion"] = None
        summary["holdout_passed"] = None
    summary.update(_lineage_metadata(head_sha))
    return summary


def _evaluate_one_candidate(
    candidate: dict[str, Any],
    head_sha: str,
    source_batch_id: str,
    run_id: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Evaluate a single candidate through the regime holdout AND-gate.

    Resilient: any exception is caught at the candidate boundary, recorded
    as lifecycle_state='holdout_error' with a full traceback in the
    error_message field. Continues to the next candidate.
    """
    started = datetime.now(timezone.utc)
    try:
        dsl = _load_dsl_from_response(
            source_batch_id, candidate["position"]
        )
        holdout_result = run_regime_holdout(
            dsl=dsl,
            batch_id=source_batch_id,
            parent_run_id=f"phase2c_eval_gate_{run_id}",
        )
        lifecycle_state = (
            "holdout_passed" if holdout_result.regime_holdout_passed
            else "holdout_failed"
        )
        error_message: str | None = None
    except Exception:
        holdout_result = None
        lifecycle_state = "holdout_error"
        error_message = traceback.format_exc()
        logger.warning(
            "%s position=%d: holdout_error\n%s",
            candidate["hypothesis_hash"][:8],
            candidate["position"],
            error_message,
        )
    finished = datetime.now(timezone.utc)
    wall_clock = (finished - started).total_seconds()

    summary = _per_candidate_summary(
        candidate=candidate,
        head_sha=head_sha,
        source_batch_id=source_batch_id,
        run_id=run_id,
        holdout_result=holdout_result,
        lifecycle_state=lifecycle_state,
        error_message=error_message,
        wall_clock_seconds=wall_clock,
    )

    candidate_dir = output_dir / candidate["hypothesis_hash"]
    candidate_dir.mkdir(parents=True, exist_ok=True)
    summary_path = candidate_dir / "holdout_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    # Round-trip validate immediately
    with open(summary_path) as f:
        reloaded = json.load(f)
    check_evaluation_semantics_or_raise(
        reloaded, artifact_path=str(summary_path)
    )

    logger.info(
        "%s position=%d theme=%s name=%s state=%s wall=%.1fs",
        candidate["hypothesis_hash"][:8],
        candidate["position"],
        candidate["theme"],
        candidate["name"][:40],
        lifecycle_state,
        wall_clock,
    )
    return summary


# ---------------------------------------------------------------------------
# Aggregate write
# ---------------------------------------------------------------------------


_CSV_FIELDS: tuple[str, ...] = (
    "hypothesis_hash",
    "position",
    "theme",
    "name",
    "wf_test_period_sharpe",
    "lifecycle_state",
    "holdout_passed",
    "holdout_sharpe",
    "holdout_max_drawdown",
    "holdout_total_return",
    "holdout_total_trades",
    "wall_clock_seconds",
    "error_message",
)


def _write_aggregate_csv(
    summaries: list[dict[str, Any]], csv_path: Path
) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for s in summaries:
            m = s.get("holdout_metrics") or {}
            writer.writerow({
                "hypothesis_hash": s["hypothesis_hash"],
                "position": s["position"],
                "theme": s["theme"],
                "name": s["name"],
                "wf_test_period_sharpe": (
                    f"{s['wf_test_period_sharpe']:.6f}"
                ),
                "lifecycle_state": s["lifecycle_state"],
                "holdout_passed": (
                    "" if s["holdout_passed"] is None
                    else ("1" if s["holdout_passed"] else "0")
                ),
                "holdout_sharpe": (
                    f"{m['sharpe_ratio']:.6f}" if m else ""
                ),
                "holdout_max_drawdown": (
                    f"{m['max_drawdown']:.6f}" if m else ""
                ),
                "holdout_total_return": (
                    f"{m['total_return']:.6f}" if m else ""
                ),
                "holdout_total_trades": (
                    str(m["total_trades"]) if m else ""
                ),
                "wall_clock_seconds": s["wall_clock_seconds"],
                "error_message": (
                    (s.get("error_message") or "").splitlines()[-1]
                    if s.get("error_message") else ""
                ),
            })


def _aggregate_summary_dict(
    summaries: list[dict[str, Any]],
    head_sha: str,
    source_batch_id: str,
    run_id: str,
    universe: str | None,
    explicit_hashes: list[str] | None,
    run_started_utc: str,
    run_finished_utc: str,
) -> dict[str, Any]:
    counts = {
        "total": len(summaries),
        "holdout_passed": sum(
            1 for s in summaries if s["lifecycle_state"] == "holdout_passed"
        ),
        "holdout_failed": sum(
            1 for s in summaries if s["lifecycle_state"] == "holdout_failed"
        ),
        "holdout_error": sum(
            1 for s in summaries if s["lifecycle_state"] == "holdout_error"
        ),
    }
    primary_summaries = [
        s for s in summaries
        if s["wf_test_period_sharpe"] > PRIMARY_THRESHOLD
    ]
    audit_only_summaries = [
        s for s in summaries
        if s["wf_test_period_sharpe"] <= PRIMARY_THRESHOLD
    ]
    primary_passed = sum(
        1 for s in primary_summaries
        if s["lifecycle_state"] == "holdout_passed"
    )
    audit_passed = sum(
        1 for s in audit_only_summaries
        if s["lifecycle_state"] == "holdout_passed"
    )
    by_theme: dict[str, dict[str, int]] = {}
    for s in summaries:
        theme = s["theme"]
        bucket = by_theme.setdefault(
            theme, {"total": 0, "holdout_passed": 0}
        )
        bucket["total"] += 1
        if s["lifecycle_state"] == "holdout_passed":
            bucket["holdout_passed"] += 1
    aggregate: dict[str, Any] = {
        "run_id": run_id,
        "source_batch_id": source_batch_id,
        "universe": universe,
        "explicit_candidate_hashes": explicit_hashes,
        "run_started_utc": run_started_utc,
        "run_finished_utc": run_finished_utc,
        "counts": counts,
        "primary_universe_holdout_passed": primary_passed,
        "primary_universe_total": len(primary_summaries),
        "audit_only_holdout_passed": audit_passed,
        "audit_only_total": len(audit_only_summaries),
        "by_theme": by_theme,
    }
    aggregate.update(_lineage_metadata(head_sha))
    return aggregate


def _write_aggregate_summary(
    aggregate: dict[str, Any], path: Path
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(aggregate, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    with open(path) as f:
        reloaded = json.load(f)
    check_evaluation_semantics_or_raise(
        reloaded, artifact_path=str(path)
    )


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 2C evaluation gate: regime holdout AND-gate against "
            "corrected Phase 2C candidates. See "
            "docs/phase2c/PHASE2C_6_EVALUATION_GATE_PLAN.md."
        ),
    )
    parser.add_argument(
        "--source-batch-id",
        type=str,
        default=DEFAULT_SOURCE_BATCH_ID,
        help=(
            "Upstream Phase 2C proposer batch UUID whose corrected "
            f"candidates are evaluated. Default: {DEFAULT_SOURCE_BATCH_ID}."
        ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--universe",
        type=str,
        choices=["primary", "audit"],
        default=None,
        help=(
            "primary=44 corrected winners (wf_test_period_sharpe>0.5); "
            "audit=all 198 corrected candidates."
        ),
    )
    group.add_argument(
        "--candidate-hashes",
        type=str,
        default=None,
        help=(
            "Comma-separated 8+ char hash prefixes to evaluate (each "
            "must resolve to exactly one candidate). Mutually exclusive "
            "with --universe."
        ),
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help=(
            "Identifier for THIS evaluation-gate output run. Examples: "
            "'smoke_v1' for smoke runs, auto-generated UUID4 for full "
            "runs. Distinct from --source-batch-id."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=str(DEFAULT_OUTPUT_ROOT),
        help=f"Output root. Default: {DEFAULT_OUTPUT_ROOT}.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Print resolved configuration + candidate selection and "
            "exit before any backtest. Lineage guard IS still invoked."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Allow overwriting an existing non-empty <output-root>/<run-id>/"
            " directory. Without --force, the script refuses to overwrite."
        ),
    )
    return parser


def _resolve_run_id(args: argparse.Namespace) -> str:
    return args.run_id or str(uuid.uuid4())


def _check_overwrite_protection(
    run_dir: Path, force: bool
) -> int | None:
    if not run_dir.exists():
        return None
    try:
        non_empty = any(run_dir.iterdir())
    except OSError:
        non_empty = True
    if non_empty and not force:
        print(
            f"\nERROR: run directory {run_dir} already exists and is "
            f"non-empty. Re-run with --force to overwrite, or pass a "
            f"different --run-id.",
            file=sys.stderr,
        )
        return 1
    return None


def main() -> int:
    """Entry point.

    Order of operations:
      1. parse_args (so --help works without git).
      2. enforce_corrected_engine_lineage (before any engine run / write).
      3. Load corrected CSV, resolve candidate universe.
      4. Overwrite-protection gate.
      5. (--dry-run) print resolved config and exit.
      6. Per-candidate runs (each writes artifact + round-trip validates).
      7. Aggregate write + round-trip validation.
    """
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        level=logging.INFO,
    )
    args = _build_argparser().parse_args()

    if args.universe is None and args.candidate_hashes is None:
        print(
            "ERROR: one of --universe or --candidate-hashes is required.",
            file=sys.stderr,
        )
        return 2

    head_sha = enforce_corrected_engine_lineage()

    all_candidates = _load_corrected_candidates(args.source_batch_id)
    selected = _resolve_candidate_universe(args, all_candidates)
    run_id = _resolve_run_id(args)
    run_dir = Path(args.output_root).resolve() / run_id

    explicit_hashes = (
        [c.strip() for c in args.candidate_hashes.split(",") if c.strip()]
        if args.candidate_hashes else None
    )

    print(f"[Phase 2C eval gate] run_id: {run_id}")
    print(f"[Phase 2C eval gate] source_batch_id: {args.source_batch_id}")
    print(f"[Phase 2C eval gate] head_sha: {head_sha}")
    print(f"[Phase 2C eval gate] universe: {args.universe}")
    print(f"[Phase 2C eval gate] explicit_hashes: {explicit_hashes}")
    print(f"[Phase 2C eval gate] candidates_to_run: {len(selected)}")
    print(f"[Phase 2C eval gate] output_dir: {run_dir}")
    print(f"[Phase 2C eval gate] dry_run: {args.dry_run}")
    print(f"[Phase 2C eval gate] force: {args.force}")

    rc = _check_overwrite_protection(run_dir, args.force)
    if rc is not None:
        return rc

    if args.dry_run:
        print("\n[Phase 2C eval gate] --dry-run: stopping before backtests.")
        for c in selected[:10]:
            print(
                f"  would evaluate: {c['hypothesis_hash'][:8]} "
                f"position={c['position']} theme={c['theme']} "
                f"name={c['name'][:40]} "
                f"wf_sharpe={c['wf_test_period_sharpe']:+.4f}"
            )
        if len(selected) > 10:
            print(f"  ... and {len(selected) - 10} more")
        return 0

    run_dir.mkdir(parents=True, exist_ok=True)
    run_started_utc = _utc_now_iso()

    summaries: list[dict[str, Any]] = []
    for i, candidate in enumerate(selected, start=1):
        logger.info(
            "[%d/%d] evaluating %s ...",
            i, len(selected), candidate["hypothesis_hash"][:8],
        )
        s = _evaluate_one_candidate(
            candidate=candidate,
            head_sha=head_sha,
            source_batch_id=args.source_batch_id,
            run_id=run_id,
            output_dir=run_dir,
        )
        summaries.append(s)

    run_finished_utc = _utc_now_iso()

    # Per-row CSV
    _write_aggregate_csv(summaries, run_dir / "holdout_results.csv")

    # Aggregate summary JSON
    aggregate = _aggregate_summary_dict(
        summaries=summaries,
        head_sha=head_sha,
        source_batch_id=args.source_batch_id,
        run_id=run_id,
        universe=args.universe,
        explicit_hashes=explicit_hashes,
        run_started_utc=run_started_utc,
        run_finished_utc=run_finished_utc,
    )
    _write_aggregate_summary(aggregate, run_dir / "holdout_summary.json")

    # Final stdout summary
    print("\n[Phase 2C eval gate] === AGGREGATE ===")
    print(f"  total candidates evaluated: {aggregate['counts']['total']}")
    print(f"  holdout_passed: {aggregate['counts']['holdout_passed']}")
    print(f"  holdout_failed: {aggregate['counts']['holdout_failed']}")
    print(f"  holdout_error:  {aggregate['counts']['holdout_error']}")
    print(
        f"  primary universe (wf>{PRIMARY_THRESHOLD}): "
        f"{aggregate['primary_universe_holdout_passed']}"
        f"/{aggregate['primary_universe_total']} passed holdout"
    )
    print(
        f"  audit-only (wf<={PRIMARY_THRESHOLD}): "
        f"{aggregate['audit_only_holdout_passed']}"
        f"/{aggregate['audit_only_total']} passed holdout"
    )
    print(f"\n[Phase 2C eval gate] run_dir: {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
