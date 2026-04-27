"""Phase 2C Phase 1 — local walk-forward funnel for proposer batch candidates.

Implementation contract: docs/phase2c/PHASE2C_4_PHASE1_PLAN.md (committed at
1c218c1).

Phase 1 scope (this script): for a Stage 2d proposer batch, extract every
``pending_backtest`` candidate's DSL, compile to a Backtrader strategy
class, drive each through ``run_walk_forward``, and emit a per-candidate
results CSV plus an aggregate summary JSON.

Component status:
  - Component A (candidate extraction + DSL re-validation): IMPLEMENTED.
  - Compile step (call ``compile_dsl_to_strategy`` per candidate, capture
    success/failure status): IMPLEMENTED — exercised by sanity check 3 of
    the contract (compiler manual verification on 5 diverse candidates,
    passed clean).
  - Component B (per-candidate ``run_walk_forward`` driver): IMPLEMENTED.
    Captures compile failures, runtime exceptions (full traceback to
    ``errors/<hash>_traceback.txt``), zero-trade windows, and elapsed
    time per candidate. Defensively dedupes by hypothesis_hash.
  - Component C (aggregation report + CSV/JSON emission): IMPLEMENTED.
    Incremental CSV writes for crash safety, distribution-stat summary
    JSON, and a stdout top-10 leaderboard plus binary verdict against
    the Phase 1 success criterion (Sharpe > 0.5).

Phase 1 explicit non-scope (per contract section 1):
  - Regime holdout AND-gate integration (run_regime_holdout exists; not
    called).
  - DSR multiple-testing screen integration.
  - Lifecycle state writes (pending_backtest → terminal states): the
    engine writes runs rows with NULL ``hypothesis_hash``, ``batch_id``,
    ``lifecycle_state``, ``regime_holdout_passed``. The Phase 1 CSV is
    the source of truth for per-candidate hash↔WF-result linkage; Phase
    2 will populate the engine-side fields.
  - Critic invocation (live or stub).

CLI (per contract section 7):
  # Smoke (Tier 1)
  python scripts/run_phase2c_batch_walkforward.py \\
      --batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \\
      --limit 5

  # Pilot (Tier 2)
  python scripts/run_phase2c_batch_walkforward.py \\
      --batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \\
      --positions 1,11,21,31,41,51,61,71,81,91,101,111,121,131,141,151,161,171,181,191

  # Full sweep (Tier 3)
  python scripts/run_phase2c_batch_walkforward.py \\
      --batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \\
      --limit 200

  # Dry-run: extract + compile only (used for sanity check 3)
  python scripts/run_phase2c_batch_walkforward.py \\
      --batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \\
      --positions 1,2,15,32,198 --dry-run

Exit codes:
  0 — success (dry-run completed; or full Component B+C run completed).
  1 — fatal error (batch dir missing, summary unparseable, etc.).

Per the contract, this script writes outputs only under
``data/phase2c_walkforward/batch_<batch-id>/`` (NOT under ``raw_payloads/``,
which is reserved for proposer audit artifacts).
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import re
import statistics
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Project imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.hypothesis_hash import hash_dsl  # noqa: E402
from backtest.engine import WalkForwardResult, run_walk_forward  # noqa: E402
from backtest.wf_lineage import (  # noqa: E402
    CORRECTED_WF_ENGINE_COMMIT,
    WF_SEMANTICS_TAG,
    enforce_corrected_engine_lineage,
)
from strategies.dsl import StrategyDSL  # noqa: E402
from strategies.dsl_compiler import (  # noqa: E402
    ManifestDriftError,
    compile_dsl_to_strategy,
)
from strategies.template import BaseStrategy  # noqa: E402


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Corrected-engine lineage guard (Task 7.6)
#
# The producer-side guard helper and lineage constants now live in
# `backtest/wf_lineage.py` (imported above) — that module is the single
# source of truth for both producer- and consumer-side enforcement of
# Section RS of docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md.
#
# Corrected runs additionally:
#   - write outputs to a `_corrected` suffixed directory so corrected
#     and pre-correction artifacts live in adjacent siblings.
#   - stamp `wf_semantics: corrected_test_boundary_v1` (load-bearing,
#     downstream consumers MUST check this before ingestion via
#     `backtest.wf_lineage.check_wf_semantics_or_raise`) and three
#     auditor-facing lineage fields into walk_forward_summary.json.
# ---------------------------------------------------------------------------


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
    """A candidate that compiled cleanly.

    ``strategy_cls`` is held as an attribute so Component B can run the
    walk-forward without re-invoking ``compile_dsl_to_strategy`` (which
    would re-verify the manifest — idempotent but wasteful). Class
    objects are unhashable for ``eq``, so this dataclass is intentionally
    not hashable; do not store CompileSuccess in a set.
    """
    position: int
    hypothesis_hash: str
    strategy_class_name: str
    warmup_bars: int
    strategy_cls: type[BaseStrategy] = field(compare=False, repr=False)


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
        strategy_cls=strategy_cls,
    )


# ---------------------------------------------------------------------------
# Component B — per-candidate walk-forward driver
#
# Per the contract section 4 Component B:
#   - every candidate produces a CSV row, including failures.
#   - compile failure → record compile_status, runtime_status='not_attempted'.
#   - runtime exception → log full traceback to errors/<hash>_traceback.txt,
#     record runtime_status='error', continue with next candidate.
#   - zero-trade WF window → not a failure; record metrics as engine reports.
#   - duplicate hypothesis_hash → dedupe defensively (batch-1 has 0).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CandidateOutcome:
    """One row of the per-candidate WF results CSV.

    Field-name semantics (per contract section 4 Component C, verified
    against ``backtest/engine.py:_aggregate_walk_forward_metrics``):

    - ``wf_test_period_sharpe``, ``wf_test_period_return``, ``wf_test_period_max_drawdown``, ``wf_test_period_total_trades``,
      ``wf_test_period_win_rate`` are mean/max/sum aggregations across walk-forward
      sub-windows, where each sub-window's metric is computed on its
      *test portion only* (the engine trims per-window equity curves
      to ``test_start`` before recomputing). This is why the columns
      are named ``wf_*`` and not ``train_*`` — they describe the WF
      output, which is itself a test-window aggregation.
    - ``wf_test_period_window_count`` is the number of WF sub-windows that produced
      metrics (v2 split with disjoint train ranges 2020-2021 + 2023
      yields a fixed count per candidate).
    """
    batch_id: str
    position: int
    hypothesis_hash: str
    name: str
    theme: str
    factors_used: str  # semicolon-joined; CSV-friendly
    compile_status: str  # ok | manifest_drift | compile_error | re_validation_failed | duplicate_skipped
    runtime_status: str  # ok | error | not_attempted
    wf_test_period_sharpe: float | None
    wf_test_period_return: float | None
    wf_test_period_max_drawdown: float | None
    wf_test_period_total_trades: int | None
    wf_test_period_win_rate: float | None
    wf_test_period_window_count: int | None
    elapsed_seconds: float
    error_message: str  # one-line; empty for ok runs


_CSV_FIELDS: tuple[str, ...] = (
    "batch_id",
    "position",
    "hypothesis_hash",
    "name",
    "theme",
    "factors_used",
    "compile_status",
    "runtime_status",
    "wf_test_period_sharpe",
    "wf_test_period_return",
    "wf_test_period_max_drawdown",
    "wf_test_period_total_trades",
    "wf_test_period_win_rate",
    "wf_test_period_window_count",
    "elapsed_seconds",
    "error_message",
)


def _write_traceback(
    errors_dir: Path,
    hypothesis_hash: str,
    tb_text: str,
) -> Path:
    """Write a full traceback file for a runtime error. Returns the path."""
    errors_dir.mkdir(parents=True, exist_ok=True)
    path = errors_dir / f"{hypothesis_hash}_traceback.txt"
    path.write_text(tb_text, encoding="utf-8")
    return path


def _outcome_from_compile_failure(
    candidate: ExtractedCandidate,
    failure: CompileFailure,
    batch_id: str,
    elapsed_seconds: float,
) -> CandidateOutcome:
    """Build a CSV row for a compile-stage failure."""
    return CandidateOutcome(
        batch_id=batch_id,
        position=candidate.position,
        hypothesis_hash=candidate.hypothesis_hash,
        name=candidate.name,
        theme=candidate.theme,
        factors_used=";".join(candidate.factors_used),
        compile_status=failure.failure_kind,
        runtime_status="not_attempted",
        wf_test_period_sharpe=None,
        wf_test_period_return=None,
        wf_test_period_max_drawdown=None,
        wf_test_period_total_trades=None,
        wf_test_period_win_rate=None,
        wf_test_period_window_count=None,
        elapsed_seconds=elapsed_seconds,
        error_message=failure.error_message[:200],
    )


def run_one_candidate_wf(
    candidate: ExtractedCandidate,
    compile_result: CompileSuccess | CompileFailure,
    batch_id: str,
    errors_dir: Path,
) -> CandidateOutcome:
    """Drive one candidate end-to-end (compile + WF) into a CSV row.

    Args:
        candidate: Extracted DSL candidate.
        compile_result: Result of ``compile_one(candidate)``. If a
            failure, the WF run is skipped and a CSV row recording the
            compile failure is returned. Re-passing the prior compile
            result avoids redundant manifest work.
        batch_id: Batch UUID; embedded in every CSV row.
        errors_dir: Directory for runtime-traceback files.

    Returns:
        Exactly one CandidateOutcome (every candidate → one row).
    """
    start = time.time()

    if isinstance(compile_result, CompileFailure):
        return _outcome_from_compile_failure(
            candidate, compile_result, batch_id, time.time() - start
        )

    strategy_cls = compile_result.strategy_cls
    try:
        wf_result: WalkForwardResult = run_walk_forward(strategy_cls)
    except Exception as exc:
        elapsed = time.time() - start
        tb_text = traceback.format_exc()
        tb_path = _write_traceback(errors_dir, candidate.hypothesis_hash, tb_text)
        logger.warning(
            "position=%d hash=%s WF runtime error: %s "
            "(traceback at %s)",
            candidate.position, candidate.hypothesis_hash,
            type(exc).__name__, tb_path,
        )
        return CandidateOutcome(
            batch_id=batch_id,
            position=candidate.position,
            hypothesis_hash=candidate.hypothesis_hash,
            name=candidate.name,
            theme=candidate.theme,
            factors_used=";".join(candidate.factors_used),
            compile_status="ok",
            runtime_status="error",
            wf_test_period_sharpe=None,
            wf_test_period_return=None,
            wf_test_period_max_drawdown=None,
            wf_test_period_total_trades=None,
            wf_test_period_win_rate=None,
            wf_test_period_window_count=None,
            elapsed_seconds=elapsed,
            error_message=f"{type(exc).__name__}: {str(exc)[:160]}",
        )

    elapsed = time.time() - start
    sm = wf_result.summary_metrics
    return CandidateOutcome(
        batch_id=batch_id,
        position=candidate.position,
        hypothesis_hash=candidate.hypothesis_hash,
        name=candidate.name,
        theme=candidate.theme,
        factors_used=";".join(candidate.factors_used),
        compile_status="ok",
        runtime_status="ok",
        wf_test_period_sharpe=float(sm["sharpe_ratio"]),
        wf_test_period_return=float(sm["total_return"]),
        wf_test_period_max_drawdown=float(sm["max_drawdown"]),
        wf_test_period_total_trades=int(sm["total_trades"]),
        wf_test_period_win_rate=float(sm["win_rate"]),
        wf_test_period_window_count=len(wf_result.window_results),
        elapsed_seconds=elapsed,
        error_message="",
    )


def _build_duplicate_skip_outcome(
    candidate: ExtractedCandidate,
    batch_id: str,
    first_position_seen: int,
) -> CandidateOutcome:
    """CSV row for a defensively-deduped duplicate hash."""
    return CandidateOutcome(
        batch_id=batch_id,
        position=candidate.position,
        hypothesis_hash=candidate.hypothesis_hash,
        name=candidate.name,
        theme=candidate.theme,
        factors_used=";".join(candidate.factors_used),
        compile_status="duplicate_skipped",
        runtime_status="not_attempted",
        wf_test_period_sharpe=None,
        wf_test_period_return=None,
        wf_test_period_max_drawdown=None,
        wf_test_period_total_trades=None,
        wf_test_period_win_rate=None,
        wf_test_period_window_count=None,
        elapsed_seconds=0.0,
        error_message=f"hypothesis_hash first seen at position {first_position_seen}",
    )


# ---------------------------------------------------------------------------
# Component C — incremental CSV writer + summary JSON + leaderboard
# ---------------------------------------------------------------------------


def _open_csv_writer(csv_path: Path) -> tuple[Any, Any]:
    """Open the CSV file for incremental writes. Returns (file, writer).

    The header is written immediately. Caller is responsible for closing
    the file. Crash safety: each row is flushed via ``file.flush()``
    after the row is written.
    """
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    f = open(csv_path, "w", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
    w.writeheader()
    f.flush()
    return f, w


def _write_csv_row(file_obj: Any, writer: Any, outcome: CandidateOutcome) -> None:
    """Write one outcome row and flush for crash safety."""
    row = {
        "batch_id": outcome.batch_id,
        "position": outcome.position,
        "hypothesis_hash": outcome.hypothesis_hash,
        "name": outcome.name,
        "theme": outcome.theme,
        "factors_used": outcome.factors_used,
        "compile_status": outcome.compile_status,
        "runtime_status": outcome.runtime_status,
        "wf_test_period_sharpe": "" if outcome.wf_test_period_sharpe is None else f"{outcome.wf_test_period_sharpe:.6f}",
        "wf_test_period_return": "" if outcome.wf_test_period_return is None else f"{outcome.wf_test_period_return:.6f}",
        "wf_test_period_max_drawdown": (
            "" if outcome.wf_test_period_max_drawdown is None
            else f"{outcome.wf_test_period_max_drawdown:.6f}"
        ),
        "wf_test_period_total_trades": (
            "" if outcome.wf_test_period_total_trades is None else outcome.wf_test_period_total_trades
        ),
        "wf_test_period_win_rate": "" if outcome.wf_test_period_win_rate is None else f"{outcome.wf_test_period_win_rate:.6f}",
        "wf_test_period_window_count": (
            "" if outcome.wf_test_period_window_count is None else outcome.wf_test_period_window_count
        ),
        "elapsed_seconds": f"{outcome.elapsed_seconds:.3f}",
        "error_message": outcome.error_message,
    }
    writer.writerow(row)
    file_obj.flush()


def _git_head_sha() -> str:
    """Return the current git HEAD sha (short form), or 'unknown'."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=PROJECT_ROOT,
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8").strip()
    except Exception:
        return "unknown"


def _percentile(values: list[float], pct: float) -> float | None:
    """Return the p-th percentile of values (0 <= pct <= 100)."""
    if not values:
        return None
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * (pct / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] + (s[c] - s[f]) * (k - f)


def _build_summary(
    outcomes: list[CandidateOutcome],
    *,
    batch_id: str,
    run_started_utc: str,
    run_finished_utc: str,
    total_elapsed_seconds: float,
    head_sha: str,
) -> dict[str, Any]:
    """Distribution stats + run metadata for the summary JSON.

    Per the contract section 2 ("Research-interpretation reporting"):
    median, mean, max, count > 0.5, count > 0.0, count > -0.3, plus
    failure-mode counts.
    """
    sharpes = [
        o.wf_test_period_sharpe for o in outcomes
        if o.runtime_status == "ok" and o.wf_test_period_sharpe is not None
        and not math.isnan(o.wf_test_period_sharpe)
    ]

    compile_status_counts: dict[str, int] = {}
    runtime_status_counts: dict[str, int] = {}
    for o in outcomes:
        compile_status_counts[o.compile_status] = (
            compile_status_counts.get(o.compile_status, 0) + 1
        )
        runtime_status_counts[o.runtime_status] = (
            runtime_status_counts.get(o.runtime_status, 0) + 1
        )

    # Distribution shape on the survivors-with-sharpe subset.
    distribution: dict[str, Any]
    if sharpes:
        distribution = {
            "n": len(sharpes),
            "median": float(statistics.median(sharpes)),
            "mean": float(statistics.fmean(sharpes)),
            "stdev": float(statistics.pstdev(sharpes)) if len(sharpes) > 1 else 0.0,
            "min": float(min(sharpes)),
            "max": float(max(sharpes)),
            "p10": _percentile(sharpes, 10),
            "p25": _percentile(sharpes, 25),
            "p75": _percentile(sharpes, 75),
            "p90": _percentile(sharpes, 90),
            "count_gt_0_5": sum(1 for x in sharpes if x > 0.5),
            "count_gt_0_0": sum(1 for x in sharpes if x > 0.0),
            "count_gt_neg_0_3": sum(1 for x in sharpes if x > -0.3),
        }
    else:
        distribution = {
            "n": 0,
            "median": None,
            "mean": None,
            "stdev": None,
            "min": None,
            "max": None,
            "p10": None, "p25": None, "p75": None, "p90": None,
            "count_gt_0_5": 0,
            "count_gt_0_0": 0,
            "count_gt_neg_0_3": 0,
        }

    binary_pass = distribution["count_gt_0_5"] >= 1

    elapsed_per_candidate = [o.elapsed_seconds for o in outcomes]
    return {
        "batch_id": batch_id,
        "run_started_utc": run_started_utc,
        "run_finished_utc": run_finished_utc,
        "git_sha": _git_head_sha(),
        # Task 7.6 lineage stamping. `wf_semantics` is the load-bearing
        # field downstream consumers (DSR, PBO, CPCV, MDS, shortlist)
        # MUST check before ingestion. The other three are auditor-facing.
        "wf_semantics": WF_SEMANTICS_TAG,
        "corrected_wf_semantics_commit": CORRECTED_WF_ENGINE_COMMIT,
        "current_git_sha": head_sha,
        "lineage_check": "passed",
        "total_candidates": len(outcomes),
        "total_elapsed_seconds": round(total_elapsed_seconds, 3),
        "mean_elapsed_per_candidate_seconds": (
            round(sum(elapsed_per_candidate) / len(elapsed_per_candidate), 3)
            if elapsed_per_candidate else 0.0
        ),
        "compile_status_counts": compile_status_counts,
        "runtime_status_counts": runtime_status_counts,
        "wf_test_period_sharpe_distribution": distribution,
        "phase1_binary_success_criterion_met": binary_pass,
        "phase1_success_threshold": 0.5,
    }


def _print_leaderboard(outcomes: list[CandidateOutcome], summary: dict[str, Any]) -> None:
    """Stdout report: top-10 by Sharpe + distribution stats + binary verdict."""
    ok_outcomes = [
        o for o in outcomes
        if o.runtime_status == "ok" and o.wf_test_period_sharpe is not None
        and not math.isnan(o.wf_test_period_sharpe)
    ]
    ranked = sorted(ok_outcomes, key=lambda o: o.wf_test_period_sharpe, reverse=True)

    print("\n" + "=" * 80)
    print("PHASE 1 WALK-FORWARD RESULTS")
    print("=" * 80)
    print(f"batch_id: {summary['batch_id']}")
    print(f"git_sha: {summary['git_sha']}")
    print(f"candidates processed: {summary['total_candidates']}")
    print(f"total elapsed: {summary['total_elapsed_seconds']:.1f}s "
          f"(mean per candidate: {summary['mean_elapsed_per_candidate_seconds']:.2f}s)")

    print("\n--- compile_status counts ---")
    for k, v in sorted(summary["compile_status_counts"].items()):
        print(f"  {k:30s} {v}")

    print("\n--- runtime_status counts ---")
    for k, v in sorted(summary["runtime_status_counts"].items()):
        print(f"  {k:30s} {v}")

    dist = summary["wf_test_period_sharpe_distribution"]
    print("\n--- wf_test_period_sharpe distribution (compile+runtime ok, non-NaN) ---")
    print(f"  n={dist['n']}")
    if dist["n"] > 0:
        print(f"  median={dist['median']:.4f}  mean={dist['mean']:.4f}  "
              f"stdev={dist['stdev']:.4f}")
        print(f"  min={dist['min']:.4f}  p10={dist['p10']:.4f}  p25={dist['p25']:.4f}  "
              f"p75={dist['p75']:.4f}  p90={dist['p90']:.4f}  max={dist['max']:.4f}")
        print(f"  count > 0.5:  {dist['count_gt_0_5']}")
        print(f"  count > 0.0:  {dist['count_gt_0_0']}")
        print(f"  count > -0.3: {dist['count_gt_neg_0_3']}")

    print("\n--- top-10 by wf_test_period_sharpe ---")
    if not ranked:
        print("  (no candidates produced a valid wf_test_period_sharpe)")
    else:
        print(f"  {'rank':>4}  {'pos':>4}  {'sharpe':>8}  {'return':>8}  "
              f"{'maxdd':>7}  {'trades':>6}  hash               name")
        for i, o in enumerate(ranked[:10], start=1):
            print(f"  {i:>4}  {o.position:>4}  "
                  f"{o.wf_test_period_sharpe:>8.4f}  {o.wf_test_period_return:>8.4f}  "
                  f"{o.wf_test_period_max_drawdown:>7.4f}  {o.wf_test_period_total_trades:>6d}  "
                  f"{o.hypothesis_hash}  {o.name}")

    print("\n--- BINARY VERDICT (Phase 1 success criterion) ---")
    threshold = summary["phase1_success_threshold"]
    if summary["phase1_binary_success_criterion_met"]:
        print(f"  ✓ MET — {dist['count_gt_0_5']} candidate(s) with wf_test_period_sharpe > {threshold}")
    else:
        print(f"  ✗ NOT MET — 0 candidates with wf_test_period_sharpe > {threshold}")
    print("=" * 80)


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
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite an existing walk_forward_results.csv in the output "
            "dir. Without --force, the script refuses to overwrite a "
            "prior run's results — sequential tier runs (smoke → pilot → "
            "full) must use distinct --output-dir paths to retain each "
            "tier's CSV. This default is opt-out destructive: an "
            "accidental re-run never silently overwrites a canonical "
            "result file."
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


def _resolve_output_dir(args: argparse.Namespace, batch_id: str) -> Path:
    """Resolve the output directory for Component C artifacts.

    Task 7.6: corrected runs write to a `_corrected` suffixed directory
    so they are visually distinguishable from any pre-correction artifacts
    that may exist as adjacent siblings under
    ``data/phase2c_walkforward/``. The `--output-dir` override is left
    untouched (caller takes full responsibility).
    """
    if args.output_dir:
        return Path(args.output_dir).resolve()
    return DEFAULT_OUTPUT_ROOT / f"batch_{batch_id}_corrected"


def _build_compile_index(
    extracted: list[ExtractedCandidate],
) -> tuple[dict[int, CompileSuccess | CompileFailure],
           list[CompileSuccess], list[CompileFailure]]:
    """Compile every extracted candidate up-front.

    Returns a position→result index plus the success/failure split. Doing
    this before the WF loop lets us fail-fast on compile errors and keeps
    the main loop's per-iteration work focused on WF execution.
    """
    by_position: dict[int, CompileSuccess | CompileFailure] = {}
    successes: list[CompileSuccess] = []
    failures: list[CompileFailure] = []
    for cand in extracted:
        result = compile_one(cand)
        by_position[cand.position] = result
        if isinstance(result, CompileSuccess):
            successes.append(result)
        else:
            failures.append(result)
    return by_position, successes, failures


def _run_walk_forward_loop(
    extracted: list[ExtractedCandidate],
    compile_by_position: dict[int, CompileSuccess | CompileFailure],
    *,
    batch_id: str,
    output_dir: Path,
) -> tuple[list[CandidateOutcome], float]:
    """Drive Component B across all extracted candidates.

    Writes incremental CSV rows for crash safety. Returns the full list
    of outcomes plus total elapsed wall clock for the WF loop.
    """
    csv_path = output_dir / "walk_forward_results.csv"
    errors_dir = output_dir / "errors"

    f, writer = _open_csv_writer(csv_path)
    outcomes: list[CandidateOutcome] = []
    seen_hashes: dict[str, int] = {}  # hash -> first-position-seen
    loop_start = time.time()

    try:
        n = len(extracted)
        for i, cand in enumerate(extracted, start=1):
            cand_start = time.time()
            # Defensive dedupe by hypothesis_hash (contract section 4).
            if cand.hypothesis_hash in seen_hashes:
                outcome = _build_duplicate_skip_outcome(
                    cand, batch_id, seen_hashes[cand.hypothesis_hash]
                )
                logger.info(
                    "[%d/%d] position=%d hash=%s DUPLICATE_SKIPPED "
                    "(first seen at position %d)",
                    i, n, cand.position, cand.hypothesis_hash,
                    seen_hashes[cand.hypothesis_hash],
                )
            else:
                seen_hashes[cand.hypothesis_hash] = cand.position
                compile_result = compile_by_position[cand.position]
                outcome = run_one_candidate_wf(
                    cand, compile_result, batch_id, errors_dir,
                )
                if outcome.runtime_status == "ok":
                    logger.info(
                        "[%d/%d] position=%d hash=%s OK "
                        "sharpe=%.4f return=%.4f trades=%d windows=%d "
                        "elapsed=%.1fs",
                        i, n, cand.position, cand.hypothesis_hash,
                        outcome.wf_test_period_sharpe, outcome.wf_test_period_return,
                        outcome.wf_test_period_total_trades, outcome.wf_test_period_window_count,
                        time.time() - cand_start,
                    )
                elif outcome.runtime_status == "error":
                    logger.warning(
                        "[%d/%d] position=%d hash=%s ERROR %s",
                        i, n, cand.position, cand.hypothesis_hash,
                        outcome.error_message[:100],
                    )
                else:  # not_attempted (compile failure)
                    logger.warning(
                        "[%d/%d] position=%d hash=%s COMPILE_FAIL %s",
                        i, n, cand.position, cand.hypothesis_hash,
                        outcome.error_message[:100],
                    )
            outcomes.append(outcome)
            _write_csv_row(f, writer, outcome)
    finally:
        f.close()

    return outcomes, time.time() - loop_start


def main() -> int:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        level=logging.INFO,
    )

    # Task 7.6: refuse to run on a pre-correction engine commit. Captured
    # SHA is stamped into walk_forward_summary.json for auditor traceability.
    head_sha = enforce_corrected_engine_lineage()

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

    run_started_utc = _utc_now_iso()
    print(f"[Phase 1] run_started_utc: {run_started_utc}")
    print(f"[Phase 1] dry_run: {args.dry_run}")

    # Component A
    extracted, extraction_failures = extract_candidates(
        batch_dir=batch_dir,
        limit=args.limit if positions is None else None,
        positions=positions,
    )
    _print_extraction_report(extracted, extraction_failures)

    # Compile step
    compile_by_position, compile_successes, compile_failures = (
        _build_compile_index(extracted)
    )
    _print_compile_report(compile_successes, compile_failures)

    if args.dry_run:
        print("\n[Phase 1] --dry-run: stopping before walk-forward execution.")
        return 0

    if not extracted:
        print("\n[Phase 1] no candidates extracted; nothing to walk-forward.",
              file=sys.stderr)
        return 1

    # Component B + Component C
    output_dir = _resolve_output_dir(args, args.batch_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Overwrite protection: refuse to clobber an existing canonical CSV
    # unless --force is set. Tier sequences (smoke → pilot → full) must
    # use distinct --output-dir paths to retain each tier's results.
    existing_csv = output_dir / "walk_forward_results.csv"
    if existing_csv.exists() and not args.force:
        print(
            f"\nERROR: {existing_csv} already exists. Re-run with --force "
            f"to overwrite, or pass --output-dir <new-path> to keep both "
            f"results.",
            file=sys.stderr,
        )
        return 1

    print(f"\n[Phase 1] output_dir: {output_dir}")
    print(f"[Phase 1] starting walk-forward loop over "
          f"{len(extracted)} candidate(s)...")

    outcomes, loop_elapsed = _run_walk_forward_loop(
        extracted,
        compile_by_position,
        batch_id=args.batch_id,
        output_dir=output_dir,
    )

    run_finished_utc = _utc_now_iso()
    summary = _build_summary(
        outcomes,
        batch_id=args.batch_id,
        run_started_utc=run_started_utc,
        run_finished_utc=run_finished_utc,
        total_elapsed_seconds=loop_elapsed,
        head_sha=head_sha,
    )
    summary_path = output_dir / "walk_forward_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"\n[Phase 1] walk_forward_summary.json: {summary_path}")
    print(f"[Phase 1] walk_forward_results.csv:  {output_dir / 'walk_forward_results.csv'}")

    _print_leaderboard(outcomes, summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
