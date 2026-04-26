"""Phase 2C Phase 1 — local walk-forward funnel for proposer batch candidates.

Implementation contract: docs/phase2c/PHASE2C_4_PHASE1_PLAN.md (committed at
1c218c1).

Phase 1 scope (this script): for a Stage 2d proposer batch, extract every
``pending_backtest`` candidate's DSL, compile to a Backtrader strategy
class, and (in subsequent sessions) drive each through ``run_walk_forward``,
emitting a per-candidate results CSV plus an aggregate summary JSON.

Component status in this commit:
  - Component A (candidate extraction + DSL re-validation): IMPLEMENTED.
  - Compile step (call ``compile_dsl_to_strategy`` per candidate, capture
    success/failure status): IMPLEMENTED — needed by sanity check 3 of the
    contract (compiler manual verification on 5 diverse candidates).
  - Component B (per-candidate ``run_walk_forward`` driver): NOT IMPLEMENTED
    in this commit. Without ``--dry-run``, the script exits with a clear
    pointer to the contract.
  - Component C (aggregation report + CSV/JSON emission): NOT IMPLEMENTED
    in this commit.

CLI:
  python scripts/run_phase2c_batch_walkforward.py \\
      --batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \\
      --limit 5 \\
      --dry-run

Exit codes:
  0 — success (dry-run completed; or future Components B+C completed).
  1 — fatal error (batch dir missing, summary unparseable, etc.).
  2 — Component B requested (no --dry-run) but not yet implemented.

Per the contract, this script writes outputs only under
``data/phase2c_walkforward/batch_<batch-id>/`` (NOT under ``raw_payloads/``,
which is reserved for proposer audit artifacts).
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Project imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.hypothesis_hash import hash_dsl  # noqa: E402
from strategies.dsl import StrategyDSL  # noqa: E402
from strategies.dsl_compiler import (  # noqa: E402
    ManifestDriftError,
    compile_dsl_to_strategy,
)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PENDING_BACKTEST = "pending_backtest"
DEFAULT_RAW_PAYLOADS_DIR = PROJECT_ROOT / "raw_payloads"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "phase2c_walkforward"

# Markdown fence regex — same shape as agents.proposer.stub_backend._FENCE_RE
# (contract boundary: parsing fence-stripped JSON is identical between
# proposer ingest and Phase 1 re-extraction).
_FENCE_RE = re.compile(
    r"```(?:\s*json)?\s*(.*?)\s*```",
    re.DOTALL | re.IGNORECASE,
)


def _strip_markdown_fence(raw: str) -> str:
    """Extract JSON body from a markdown code fence if present.

    Mirrors ``agents.proposer.stub_backend._strip_markdown_fence``; reproduced
    here to avoid importing proposer-side modules in the Phase 1 evaluation
    path. Re-validation reads the on-disk ``attempt_NNNN_response.txt`` files
    that the proposer wrote during the batch.
    """
    m = _FENCE_RE.search(raw)
    return m.group(1) if m else raw


# ---------------------------------------------------------------------------
# Component A — candidate extraction + DSL re-validation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExtractedCandidate:
    """One candidate extracted from a proposer batch directory."""

    position: int
    theme: str
    hypothesis_hash: str
    name: str
    factors_used: tuple[str, ...]
    dsl: StrategyDSL


@dataclass(frozen=True)
class ExtractionFailure:
    """A candidate that failed to re-extract / re-validate."""

    position: int
    theme: str
    hypothesis_hash: str | None
    failure_kind: str  # "response_file_missing" | "json_decode" | "dsl_validation"
    error_message: str


def _load_summary(batch_dir: Path) -> dict[str, Any]:
    """Load and validate ``stage2d_summary.json`` from a batch directory."""
    summary_path = batch_dir / "stage2d_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(
            f"stage2d_summary.json not found at {summary_path}"
        )
    with open(summary_path) as f:
        summary = json.load(f)
    if "calls" not in summary:
        raise ValueError(
            f"summary at {summary_path} is missing required 'calls' key"
        )
    return summary


def _filter_pending_backtest_calls(
    summary: dict[str, Any],
    limit: int | None,
    positions: set[int] | None,
) -> list[dict[str, Any]]:
    """Filter calls list to ``pending_backtest`` candidates per CLI args."""
    calls = [
        c for c in summary["calls"]
        if c.get("lifecycle_state") == PENDING_BACKTEST
    ]
    if positions is not None:
        calls = [c for c in calls if c.get("position") in positions]
    elif limit is not None:
        calls = calls[:limit]
    return calls


def _extract_one_candidate(
    call: dict[str, Any],
    batch_dir: Path,
) -> ExtractedCandidate | ExtractionFailure:
    """Re-parse and re-validate one candidate from its response file."""
    position = call["position"]
    theme = call.get("theme", "unknown")
    hypothesis_hash = call.get("hypothesis_hash")

    response_path = batch_dir / f"attempt_{position:04d}_response.txt"
    if not response_path.exists():
        return ExtractionFailure(
            position=position,
            theme=theme,
            hypothesis_hash=hypothesis_hash,
            failure_kind="response_file_missing",
            error_message=f"missing: {response_path.name}",
        )

    raw_text = response_path.read_text(encoding="utf-8")
    parse_input = _strip_markdown_fence(raw_text)

    try:
        payload = json.loads(parse_input)
    except json.JSONDecodeError as exc:
        return ExtractionFailure(
            position=position,
            theme=theme,
            hypothesis_hash=hypothesis_hash,
            failure_kind="json_decode",
            error_message=f"json_decode_error: {exc}",
        )

    try:
        dsl = StrategyDSL.model_validate(payload)
    except Exception as exc:
        return ExtractionFailure(
            position=position,
            theme=theme,
            hypothesis_hash=hypothesis_hash,
            failure_kind="dsl_validation",
            error_message=f"dsl_validation_error: {type(exc).__name__}: {exc}",
        )

    # Cross-check: re-computed D3 hypothesis_hash (16 hex chars,
    # semantic-equivalence-aware) should match the proposer's recorded
    # hash. A mismatch is itself a finding worth surfacing.
    # CONTRACT BOUNDARY: D3 dedup hash (agents.hypothesis_hash.hash_dsl) is
    # deliberately separate from D2 byte-stable hash
    # (strategies.dsl.compute_dsl_hash); this script uses D3 because that's
    # the form recorded by the proposer in stage2d_summary.json.
    recomputed_hash = hash_dsl(dsl)
    recorded_hash = call.get("hypothesis_hash")
    if recorded_hash and recomputed_hash != recorded_hash:
        logger.warning(
            "position=%d hash mismatch: recomputed=%s recorded=%s "
            "(re-extracted DSL is not semantically equivalent to "
            "the proposer-time DSL — investigate)",
            position, recomputed_hash, recorded_hash,
        )

    factors_used_list = call.get("factors_used") or []
    return ExtractedCandidate(
        position=position,
        theme=theme,
        hypothesis_hash=recomputed_hash,
        name=dsl.name,
        factors_used=tuple(factors_used_list),
        dsl=dsl,
    )


def extract_candidates(
    batch_dir: Path,
    limit: int | None = None,
    positions: set[int] | None = None,
) -> tuple[list[ExtractedCandidate], list[ExtractionFailure]]:
    """Component A entry point.

    Args:
        batch_dir: Path to ``raw_payloads/batch_<uuid>/``.
        limit: If set (and ``positions`` is None), take the first N
            pending_backtest candidates.
        positions: If set, take only candidates whose 1-indexed position is
            in this set; overrides ``limit``.

    Returns:
        (extracted, failures) — paired lists. Every pending_backtest call
        appears in exactly one of the two lists.
    """
    summary = _load_summary(batch_dir)
    calls = _filter_pending_backtest_calls(summary, limit, positions)

    extracted: list[ExtractedCandidate] = []
    failures: list[ExtractionFailure] = []
    for call in calls:
        result = _extract_one_candidate(call, batch_dir)
        if isinstance(result, ExtractedCandidate):
            extracted.append(result)
        else:
            failures.append(result)
    return extracted, failures


# ---------------------------------------------------------------------------
# Compile step — exercise the DSL compiler on each candidate
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CompileSuccess:
    """A candidate that compiled cleanly."""
    position: int
    hypothesis_hash: str
    strategy_class_name: str
    warmup_bars: int


@dataclass(frozen=True)
class CompileFailure:
    """A candidate whose compile_dsl_to_strategy raised."""
    position: int
    hypothesis_hash: str
    failure_kind: str  # "manifest_drift" | "compile_error"
    error_message: str


def compile_one(candidate: ExtractedCandidate) -> CompileSuccess | CompileFailure:
    """Compile one extracted candidate, capturing success or failure."""
    try:
        strategy_cls = compile_dsl_to_strategy(candidate.dsl)
    except ManifestDriftError as exc:
        return CompileFailure(
            position=candidate.position,
            hypothesis_hash=candidate.hypothesis_hash,
            failure_kind="manifest_drift",
            error_message=str(exc),
        )
    except Exception as exc:
        return CompileFailure(
            position=candidate.position,
            hypothesis_hash=candidate.hypothesis_hash,
            failure_kind="compile_error",
            error_message=f"{type(exc).__name__}: {exc}",
        )

    warmup_bars = getattr(strategy_cls, "WARMUP_BARS", 0)
    return CompileSuccess(
        position=candidate.position,
        hypothesis_hash=candidate.hypothesis_hash,
        strategy_class_name=strategy_cls.__name__,
        warmup_bars=warmup_bars,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _utc_now_iso() -> str:
    """Return current UTC time as ISO 8601 string with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 2C Phase 1 — local walk-forward funnel for proposer "
            "batch candidates. Implementation contract: "
            "docs/phase2c/PHASE2C_4_PHASE1_PLAN.md."
        ),
    )
    parser.add_argument(
        "--batch-id",
        type=str,
        required=True,
        help="Batch UUID (directory under raw_payloads/batch_<uuid>/).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help=(
            "Process at most N pending_backtest candidates. Default 5 "
            "(deliberately small so accidental no-flag runs don't burn "
            "compute). Ignored if --positions is set."
        ),
    )
    parser.add_argument(
        "--positions",
        type=str,
        default=None,
        help=(
            "Comma-separated 1-indexed positions to process; "
            "overrides --limit. Example: --positions 1,11,21,31"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Extract + validate + compile only; do not run walk-forward. "
            "Use to verify Component A and the compile step before "
            "spending compute on Component B."
        ),
    )
    parser.add_argument(
        "--raw-payloads-dir",
        type=str,
        default=str(DEFAULT_RAW_PAYLOADS_DIR),
        help="Override default raw_payloads/ root.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help=(
            "Override default output dir "
            "(data/phase2c_walkforward/batch_<batch-id>/)."
        ),
    )
    return parser


def _parse_positions(arg: str | None) -> set[int] | None:
    if not arg:
        return None
    try:
        return {int(s.strip()) for s in arg.split(",") if s.strip()}
    except ValueError as exc:
        raise SystemExit(f"--positions parse error: {exc}")


def _print_extraction_report(
    extracted: list[ExtractedCandidate],
    failures: list[ExtractionFailure],
) -> None:
    print("\n=== Component A: candidate extraction ===")
    print(f"extracted_ok: {len(extracted)}")
    print(f"extracted_fail: {len(failures)}")
    if failures:
        print("\nfailures:")
        for f in failures:
            print(f"  position={f.position:4d} theme={f.theme:24s} "
                  f"kind={f.failure_kind:24s} {f.error_message[:80]}")
    if extracted:
        print("\nfirst 5 extracted:")
        for c in extracted[:5]:
            print(f"  position={c.position:4d} theme={c.theme:24s} "
                  f"hash={c.hypothesis_hash} name='{c.name}' "
                  f"factors={list(c.factors_used)}")


def _print_compile_report(
    successes: list[CompileSuccess],
    failures: list[CompileFailure],
) -> None:
    print("\n=== Compile step ===")
    print(f"compile_ok: {len(successes)}")
    print(f"compile_fail: {len(failures)}")
    if failures:
        print("\ncompile failures:")
        for f in failures:
            print(f"  position={f.position:4d} hash={f.hypothesis_hash} "
                  f"kind={f.failure_kind:18s} {f.error_message[:100]}")
    if successes:
        print("\nfirst 5 compiled:")
        for s in successes[:5]:
            print(f"  position={s.position:4d} hash={s.hypothesis_hash} "
                  f"class={s.strategy_class_name:48s} "
                  f"warmup_bars={s.warmup_bars}")


def main() -> int:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        level=logging.INFO,
    )
    args = _build_argparser().parse_args()

    raw_payloads_dir = Path(args.raw_payloads_dir).resolve()
    batch_dir = raw_payloads_dir / f"batch_{args.batch_id}"
    if not batch_dir.is_dir():
        print(f"ERROR: batch dir not found: {batch_dir}", file=sys.stderr)
        return 1

    positions = _parse_positions(args.positions)
    if positions is not None:
        print(f"[Phase 1] processing positions: {sorted(positions)}")
    else:
        print(f"[Phase 1] processing first {args.limit} pending_backtest "
              f"candidates from batch_{args.batch_id}")

    print(f"[Phase 1] run_timestamp_utc: {_utc_now_iso()}")
    print(f"[Phase 1] dry_run: {args.dry_run}")

    # Component A
    extracted, extraction_failures = extract_candidates(
        batch_dir=batch_dir,
        limit=args.limit if positions is None else None,
        positions=positions,
    )
    _print_extraction_report(extracted, extraction_failures)

    # Compile step (always run when Component A produced any extracted
    # candidates — sanity check 3 of the contract uses this surface).
    compile_successes: list[CompileSuccess] = []
    compile_failures: list[CompileFailure] = []
    for cand in extracted:
        result = compile_one(cand)
        if isinstance(result, CompileSuccess):
            compile_successes.append(result)
        else:
            compile_failures.append(result)
    _print_compile_report(compile_successes, compile_failures)

    if args.dry_run:
        print("\n[Phase 1] --dry-run: stopping before walk-forward execution.")
        print("[Phase 1] Component B (per-candidate run_walk_forward driver) "
              "is the next deliverable per docs/phase2c/PHASE2C_4_PHASE1_PLAN.md.")
        return 0

    # Component B + Component C — explicit not-yet-implemented gate.
    print("\nERROR: Component B (per-candidate run_walk_forward driver) and "
          "Component C (aggregation report) are not yet implemented.",
          file=sys.stderr)
    print("       Use --dry-run to exercise Component A + compile only.",
          file=sys.stderr)
    print("       Implementation contract: "
          "docs/phase2c/PHASE2C_4_PHASE1_PLAN.md (sealed at 1c218c1).",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
