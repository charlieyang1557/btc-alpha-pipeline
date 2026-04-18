"""D7 Stage 2b — five-call live D7b batch probe.

Single-script orchestrator for the five sequential replay candidates locked
in ``docs/d7_stage2b/replay_candidates.json``. Fires the selection in
firing-order (position ascending), enforces 23 hard-fail gates, records
cost / reasoning / score sequences as ordered lists (never distributions),
and writes an append-only aggregate record via ``os.replace()`` atomic
move.

CONTRACT BOUNDARY: no retries beyond Stage 2a's inheritance (one API-level
retry, zero content-level retries). No prompt caching. No rate-limiting.
``STAGE2B_N == 5``; N is not user-configurable.

CONTRACT BOUNDARY: abort-rule classification consumes the persisted
per-call record fields — never raw exception objects from the batch loop.
This keeps per-call record and abort decision in a single source of truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal

# Allow bare ``python scripts/run_d7_stage2b_batch.py`` invocation.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agents.critic.d7a_feature_extraction import extract_factors  # noqa: E402
from agents.critic.d7b_prompt import (  # noqa: E402
    D7B_PROTECTED_TERMS,
    build_d7b_prompt,
    run_leakage_audit,
)
from agents.critic.d7b_stub import StubD7bBackend  # noqa: E402
from agents.critic.orchestrator import run_critic  # noqa: E402
from agents.critic.replay import reconstruct_batch_context_at_position  # noqa: E402
from agents.orchestrator.budget_ledger import BudgetLedger  # noqa: E402


# ---------------------------------------------------------------------------
# Locked constants — CONTRACT BOUNDARY
# ---------------------------------------------------------------------------

# Per-call cost ceiling (matches Stage 2a cost discipline).
STAGE2B_PER_CALL_COST_CEILING_USD: float = 0.05
# Total cost cap across the 5-call sequence.
STAGE2B_TOTAL_COST_CAP_USD: float = 0.10
# Inter-call pacing; well under Anthropic tier-1 rate limits.
STAGE2B_INTER_CALL_SLEEP_SECONDS: int = 5
# N=5. Not user-configurable per launch prompt §7.
STAGE2B_N: int = 5
# The sole Stage 2b batch UUID (signed-off Stage 2d replay source).
STAGE2B_BATCH_UUID: str = "5cf76668-47d1-48d7-bd90-db06d31982ed"
# D7b score polarity threshold (pinned). exact 0.5 → classified as >= 0.5 (HIGH).
STRUCTURAL_VARIANT_RISK_HIGH_THRESHOLD: float = 0.5

# Aggregate record schema version (lock F).
STAGE_LABEL: str = "d7_stage2b"
RECORD_VERSION: str = "1.0"


# ---------------------------------------------------------------------------
# Production paths (defaults; all overridable for tests)
# ---------------------------------------------------------------------------

SELECTION_JSON_PATH: Path = Path("docs/d7_stage2b/replay_candidates.json")
EXPECTATIONS_PATH: Path = Path("docs/d7_stage2b/stage2b_expectations.md")
AGGREGATE_RECORD_PATH: Path = Path("docs/d7_stage2b/stage2b_batch_record.json")
PER_CALL_RECORD_DIR: Path = Path("docs/d7_stage2b")
RAW_PAYLOAD_ROOT: Path = Path("raw_payloads")
LEDGER_PATH: Path = Path("agents/spend_ledger.db")
PROMPT_TEMPLATE_PATH: Path = Path("agents/critic/d7b_prompt.py")

# Stub-mode physical isolation root (launch prompt §4.10).
DRYRUN_ROOT: Path = Path("dryrun_payloads/dryrun_stage2b")


# ---------------------------------------------------------------------------
# Exceptions (startup aborts — sys.exit(1))
# ---------------------------------------------------------------------------


class Stage2bStartupError(RuntimeError):
    """Raised when a pre-fire gate fails; maps to exit code 1."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_dotenv(path: Path | None = None) -> None:
    """Load ``.env`` into ``os.environ`` (stdlib-only)."""
    env_path = path or _REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _file_sha256(path: Path) -> str:
    """SHA-256 of a file's raw bytes (HG2/HG6/HG7/HG20)."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit_unixtime(path: Path) -> int | None:
    """Return the last commit's Unix timestamp for ``path``, or None if untracked."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(path)],
            capture_output=True, text=True, timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    out = result.stdout.strip()
    if not out:
        return None
    try:
        return int(out)
    except ValueError:
        return None


def _git_commit_iso(path: Path) -> str | None:
    """Return the last commit's ISO 8601 UTC timestamp for ``path``."""
    ts = _git_commit_unixtime(path)
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )


def _now_unixtime() -> int:
    return int(time.time())


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# Gate logic (pure functions, unit-testable)
# ---------------------------------------------------------------------------


def verify_selection_invariants(selection: dict) -> None:
    """HG2b: re-verify tier / warnings invariants at fire time.

    Raises Stage2bStartupError on violation.
    """
    tier = selection.get("selection_tier")
    warnings = selection.get("selection_warnings", [])
    if tier not in (0, 1, 2):
        raise Stage2bStartupError(
            f"HG2b: selection_tier must be 0/1/2; got {tier!r}"
        )
    if not isinstance(warnings, list):
        raise Stage2bStartupError(
            "HG2b: selection_warnings must be a list"
        )
    if tier == 0 and warnings:
        raise Stage2bStartupError(
            "HG2b: selection_tier=0 must have empty selection_warnings; "
            f"got {warnings!r}"
        )
    if tier in (1, 2) and len(warnings) < 1:
        raise Stage2bStartupError(
            f"HG2b: selection_tier={tier} must have >=1 warnings; got none"
        )
    if tier == 2:
        has_divergence = any(
            isinstance(w, dict)
            and w.get("constraint_relaxed") == "divergence_coverage"
            for w in warnings
        )
        if not has_divergence:
            raise Stage2bStartupError(
                "HG2b: selection_tier=2 requires a warning with "
                "constraint_relaxed='divergence_coverage'"
            )


def verify_candidate_count_and_keys(selection: dict) -> list[dict]:
    """HG1 surface: five candidates present with required keys.

    Returns the list of candidate dicts in firing order.
    """
    candidates = selection.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != STAGE2B_N:
        raise Stage2bStartupError(
            f"HG1: selection must contain exactly {STAGE2B_N} candidates; "
            f"got {len(candidates) if isinstance(candidates, list) else 'n/a'}"
        )
    required = {
        "firing_order", "position", "theme", "hypothesis_hash",
        "d7a_b_relationship_label",
    }
    for i, c in enumerate(candidates, 1):
        missing = required - set(c.keys())
        if missing:
            raise Stage2bStartupError(
                f"HG1: candidate #{i} missing keys {sorted(missing)}"
            )
        if c.get("firing_order") != i:
            raise Stage2bStartupError(
                f"HG1: candidate at index {i} has firing_order="
                f"{c.get('firing_order')!r}; expected {i}"
            )
    return candidates


# HG4 / HG4b — expectations structural validator

_AGGREGATE_HEADER = "## Aggregate Expectations Across All 5 Calls"
_ANTI_HINDSIGHT_HEADER = "## Anti-Hindsight Anchor"
_PER_CANDIDATE_HEADER = "## Per-Candidate Expectations"


def _expected_candidate_header(i: int, c: dict) -> str:
    """Build the exact candidate section header (HG4b ground truth).

    Format: ``### Candidate <N> — Position <P>, <theme>, <label>``
    The em dash is U+2014 to match the launch prompt §4.7 schema.
    """
    return (
        f"### Candidate {i} \u2014 Position {c['position']}, "
        f"{c['theme']}, {c['d7a_b_relationship_label']}"
    )


def validate_expectations_file(
    expectations_text: str, candidates: list[dict],
) -> None:
    """HG4 + HG4b: structural + identity-exact-match validation.

    Raises Stage2bStartupError on any violation.
    """
    # HG4 — required headers.
    for header in (
        _ANTI_HINDSIGHT_HEADER, _AGGREGATE_HEADER, _PER_CANDIDATE_HEADER,
    ):
        if header not in expectations_text:
            raise Stage2bStartupError(
                f"HG4: expectations file missing header {header!r}"
            )

    # HG4b — per-candidate identity exact match.
    for i, c in enumerate(candidates, 1):
        expected = _expected_candidate_header(i, c)
        if expected not in expectations_text:
            raise Stage2bStartupError(
                f"HG4b: expectations file missing exact header for "
                f"candidate #{i}. Expected line: {expected!r}"
            )


def verify_commit_ordering(
    selection_ts: int | None,
    expectations_ts: int | None,
    now_ts: int,
) -> None:
    """HG5: selection commit < expectations commit < wall-clock.

    Raises Stage2bStartupError with pointer to the failing inequality.
    """
    if selection_ts is None:
        raise Stage2bStartupError(
            "HG5: selection JSON is not committed to git (no commit timestamp)"
        )
    if expectations_ts is None:
        raise Stage2bStartupError(
            "HG5/HG3: expectations file is not committed to git "
            "(no commit timestamp). Commit the expectations file before fire."
        )
    if not (selection_ts < expectations_ts):
        raise Stage2bStartupError(
            f"HG5: selection commit ({selection_ts}) must be strictly less "
            f"than expectations commit ({expectations_ts})"
        )
    if not (expectations_ts < now_ts):
        raise Stage2bStartupError(
            f"HG5: expectations commit ({expectations_ts}) must be strictly "
            f"less than wall-clock ({now_ts})"
        )


# ---------------------------------------------------------------------------
# Abort-rule classification (single source of truth)
# ---------------------------------------------------------------------------


_API_LEVEL_SIGNATURE_MARKERS = (
    "timeout", "connection", "authentication", "rate limit",
    "could not resolve", "api_error", "api_connection", "api_timeout",
    "api_rate_limit", "api_server_error", "api_auth",
)


def classify_d7b_error(
    error_signature: str | None, actual_cost_usd: float,
) -> str:
    """Classify a d7b_error as ``api_level`` or ``content_level``.

    Key discriminator: did Anthropic bill us? If ``actual_cost_usd > 0``,
    the call reached the API and downstream parsing failed → content_level.
    Otherwise fall back to signature pattern matching. Conservative default
    is ``content_level`` because content errors are budget-safe whereas
    over-counting API errors can trigger unwarranted aborts.
    """
    if actual_cost_usd > 0:
        return "content_level"
    sig = (error_signature or "").lower()
    for marker in _API_LEVEL_SIGNATURE_MARKERS:
        if marker in sig:
            return "api_level"
    return "content_level"


def is_consistent_with_label(
    pre_registered_label: str, structural_variant_risk: float | None,
) -> bool | None:
    """Mechanical reconciliation of D7b's structural_variant_risk to label.

    Returns True / False / None (None on d7b_error or neutral label).
    Exactly 0.5 is classified as ``>= 0.5`` (HIGH).
    """
    if structural_variant_risk is None:
        return None
    if pre_registered_label == "divergence_expected":
        return structural_variant_risk < STRUCTURAL_VARIANT_RISK_HIGH_THRESHOLD
    if pre_registered_label == "agreement_expected":
        return structural_variant_risk >= STRUCTURAL_VARIANT_RISK_HIGH_THRESHOLD
    # neutral or unknown → no prediction
    return None


def reconciliation_rationale(
    pre_registered_label: str, structural_variant_risk: float | None,
) -> str:
    """Human-readable rationale embedded in aggregate record."""
    if structural_variant_risk is None:
        return (
            "d7b_error; no structural_variant_risk score produced; "
            "cannot reconcile"
        )
    if pre_registered_label == "neutral":
        return (
            "neutral label has no structural_variant_risk prediction; "
            "not reconciled"
        )
    direction = (
        "low (< 0.5)"
        if structural_variant_risk < STRUCTURAL_VARIANT_RISK_HIGH_THRESHOLD
        else "high (>= 0.5)"
    )
    consistent = is_consistent_with_label(
        pre_registered_label, structural_variant_risk,
    )
    verdict = "supports" if consistent else "contradicts"
    return (
        f"{pre_registered_label} with D7b structural_variant_risk "
        f"{structural_variant_risk:.4f} = {direction} {verdict} "
        f"pre-registered label"
    )


def should_abort(
    call_index: int,
    call_histories: list[dict],
    current_call_cost: float,
    cumulative_cost: float,
) -> tuple[bool, str | None]:
    """Return (abort, reason). Consumes persisted per-call record fields only.

    ``call_histories`` is a list of per-call records written after each
    completed call; each entry MUST contain ``critic_status``,
    ``d7b_error_category``, ``actual_cost_usd``.
    """
    # Rule (d): per-call cost ceiling.
    if current_call_cost > STAGE2B_PER_CALL_COST_CEILING_USD:
        return True, "per_call_cost_exceeded"
    # Rule (e): cumulative cost cap.
    if cumulative_cost > STAGE2B_TOTAL_COST_CAP_USD:
        return True, "cumulative_cost_exceeded"
    # Rule (a): two consecutive API-level errors with cost=0.
    if call_index >= 2:
        last_two = call_histories[-2:]
        if all(
            c.get("critic_status") == "d7b_error"
            and c.get("d7b_error_category") == "api_level"
            and (c.get("actual_cost_usd") or 0) == 0
            for c in last_two
        ):
            return True, "api_level_consecutive"
    # Rule (b): cumulative d7b_error rate > 40% at K >= 3.
    if call_index >= 3:
        error_count = sum(
            1 for c in call_histories if c.get("critic_status") == "d7b_error"
        )
        if error_count / call_index > 0.40:
            return True, "cumulative_error_rate"
    # Rule (c): content-level d7b_error in >= 3 of any K >= 3.
    if call_index >= 3:
        content_errors = sum(
            1 for c in call_histories
            if c.get("critic_status") == "d7b_error"
            and c.get("d7b_error_category") == "content_level"
        )
        if content_errors >= 3:
            return True, "content_level_threshold"
    return False, None


# ---------------------------------------------------------------------------
# Stage 2a archival (launch prompt §4.9)
# ---------------------------------------------------------------------------


def archive_stage2a_artifacts_if_present(
    critic_dir: Path, position: int = 73,
) -> Path | None:
    """If ``call_<position:04d>_*`` files exist, archive them.

    Moves the matched files into ``<critic_dir>/stage2a_archive/``. If the
    archive dir already exists, raises Stage2bStartupError (Stage 2b must
    not co-mingle archival stages).
    Returns the archive directory if archival occurred, else None.
    """
    pattern = f"call_{position:04d}_*"
    matches = sorted(critic_dir.glob(pattern))
    if not matches:
        return None
    archive_dir = critic_dir / "stage2a_archive"
    if archive_dir.exists():
        raise Stage2bStartupError(
            f"Stage 2a archive directory already exists at {archive_dir}; "
            "cannot archive a second time. Manual reconciliation required."
        )
    archive_dir.mkdir(parents=True)
    for m in matches:
        if m.is_file():
            shutil.move(str(m), str(archive_dir / m.name))
    return archive_dir


# ---------------------------------------------------------------------------
# Atomic write
# ---------------------------------------------------------------------------


def atomic_write_json(path: Path, payload: dict) -> None:
    """Atomic write via ``os.replace()`` (cross-platform)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Config dataclass (injectable dependencies for testability)
# ---------------------------------------------------------------------------


@dataclass
class Stage2bConfig:
    """Paths and injectables for a Stage 2b run."""

    confirm_live: bool
    stub: bool

    selection_json_path: Path = SELECTION_JSON_PATH
    expectations_path: Path = EXPECTATIONS_PATH
    aggregate_record_path: Path = AGGREGATE_RECORD_PATH
    per_call_record_dir: Path = PER_CALL_RECORD_DIR
    raw_payload_root: Path = RAW_PAYLOAD_ROOT
    ledger_path: Path = LEDGER_PATH
    prompt_template_path: Path = PROMPT_TEMPLATE_PATH

    # Injectable for testing.
    selection_commit_ts_fn: Callable[[Path], int | None] = field(
        default=_git_commit_unixtime
    )
    expectations_commit_ts_fn: Callable[[Path], int | None] = field(
        default=_git_commit_unixtime
    )
    now_unixtime_fn: Callable[[], int] = field(default=_now_unixtime)
    now_iso_fn: Callable[[], str] = field(default=_iso_now)
    sleep_fn: Callable[[float], None] = field(default=time.sleep)
    reconstruct_fn: Callable[..., Any] = field(
        default=reconstruct_batch_context_at_position
    )
    backend_factory: Callable[..., Any] | None = None
    # Override ledger api_call_kind (stub mode uses ``d7b_critic_stub``).
    api_call_kind_override: str | None = None


def build_stage2b_config(
    confirm_live: bool, stub: bool,
) -> Stage2bConfig:
    """Build a production config with stub/live path routing."""
    if confirm_live and stub:
        raise ValueError("--confirm-live and --stub are mutually exclusive")
    if not (confirm_live or stub):
        raise ValueError("one of --confirm-live or --stub is required")

    if stub:
        # Stub mode — physical isolation under dryrun_payloads/dryrun_stage2b/.
        return Stage2bConfig(
            confirm_live=False,
            stub=True,
            selection_json_path=SELECTION_JSON_PATH,
            expectations_path=EXPECTATIONS_PATH,
            aggregate_record_path=DRYRUN_ROOT / "stage2b_batch_record.json",
            per_call_record_dir=DRYRUN_ROOT,
            raw_payload_root=DRYRUN_ROOT / "raw_payloads",
            ledger_path=DRYRUN_ROOT / "ledger_dryrun.db",
            prompt_template_path=PROMPT_TEMPLATE_PATH,
            api_call_kind_override="d7b_critic_stub",
        )
    # Live mode.
    return Stage2bConfig(
        confirm_live=True,
        stub=False,
        api_call_kind_override="d7b_critic_live",
    )


# ---------------------------------------------------------------------------
# Per-call record builder
# ---------------------------------------------------------------------------


def _not_reached_scan_result() -> dict:
    return {
        "status": "not_reached",
        "hits": None,
        "reason": "parse failed before scan completion",
    }


def _capture_leakage_audit_result(prompt_text: str) -> dict:
    leakage_detail = run_leakage_audit(prompt_text)
    return {
        "status": "pass" if leakage_detail is None else "fail",
        "violations": [] if leakage_detail is None else [leakage_detail],
        "protected_terms_checked_count": len(D7B_PROTECTED_TERMS),
    }


def build_per_call_record(
    *,
    candidate: dict,
    prompt_text: str,
    prompt_sha256: str,
    prior_factor_sets_count: int,
    theme_hint_factor_count: int,
    request_ts: datetime,
    response_ts: datetime,
    result,  # CriticResult
    ledger_row_id: str,
    backend_label: str,
    estimated_cost_usd: float,
    actual_cost_usd: float,
    raw_payload_paths: dict,
    leakage_audit_result: dict,
    inter_call_sleep_elapsed_seconds: float,
) -> dict:
    """Assemble the per-call record (Stage 2a fields + Stage 2b extensions)."""
    result_dict = result.to_dict()
    wall_clock_s = (response_ts - request_ts).total_seconds()

    scan_results = result.d7b_scan_results if isinstance(
        result.d7b_scan_results, dict,
    ) else None
    forbidden_scan = (
        scan_results.get("forbidden_language_scan", _not_reached_scan_result())
        if scan_results is not None else _not_reached_scan_result()
    )
    refusal_scan = (
        scan_results.get("refusal_scan", _not_reached_scan_result())
        if scan_results is not None else _not_reached_scan_result()
    )

    cost_ratio: float | None = None
    if estimated_cost_usd > 0 and actual_cost_usd > 0:
        cost_ratio = round(actual_cost_usd / estimated_cost_usd, 4)

    # Derive d7b_error_category (single source of truth for abort rules).
    d7b_error_category: str | None = None
    if result.critic_status == "d7b_error":
        d7b_error_category = classify_d7b_error(
            result.critic_error_signature, actual_cost_usd,
        )

    return {
        # --- Stage 2a live_call_record fields ---
        "request_timestamp_utc": request_ts.isoformat().replace("+00:00", "Z"),
        "response_timestamp_utc": response_ts.isoformat().replace("+00:00", "Z"),
        "wall_clock_seconds": round(wall_clock_s, 3),
        "retry_count": result.d7b_retry_count,
        "d7b_mode": result.d7b_mode,
        "critic_result": result_dict,
        "ledger_row": {
            "row_id": ledger_row_id,
            "batch_id": STAGE2B_BATCH_UUID,
            "api_call_kind": f"d7b_critic_{backend_label}",
            "backend_kind": "d7b_critic",
            "call_role": "critique",
            "estimated_cost_usd": estimated_cost_usd,
            "actual_cost_usd": actual_cost_usd,
            "input_tokens": result.d7b_input_tokens,
            "output_tokens": result.d7b_output_tokens,
        },
        "raw_payload_paths": raw_payload_paths,
        "cost": {
            "estimated_usd": estimated_cost_usd,
            "actual_usd": actual_cost_usd,
            "ratio": cost_ratio,
        },
        "leakage_audit_result": leakage_audit_result,
        "forbidden_language_scan_result": forbidden_scan,
        "refusal_scan_result": refusal_scan,

        # --- Stage 2b extensions (lock D + B + error category) ---
        "firing_order": candidate["firing_order"],
        "candidate_position": candidate["position"],
        "candidate_theme": candidate["theme"],
        "candidate_hypothesis_hash": candidate["hypothesis_hash"],
        "pre_registered_label": candidate["d7a_b_relationship_label"],
        "prior_factor_sets_count": prior_factor_sets_count,
        "theme_hint_factor_count": theme_hint_factor_count,
        "prompt_chars": len(prompt_text),
        "prompt_sha256": prompt_sha256,
        "call_index_in_sequence": candidate["firing_order"],
        "inter_call_sleep_elapsed_seconds": round(
            inter_call_sleep_elapsed_seconds, 3,
        ),

        # Convenience mirrors consumed by abort-rule classifier.
        "critic_status": result.critic_status,
        "critic_error_signature": result.critic_error_signature,
        "actual_cost_usd": actual_cost_usd,
        "d7b_error_category": d7b_error_category,
    }


# ---------------------------------------------------------------------------
# Aggregate record builder
# ---------------------------------------------------------------------------


def _extract_d7a_scores(result_dict: dict) -> dict[str, float] | None:
    return result_dict.get("d7a_rule_scores")


def _extract_d7b_scores(result_dict: dict) -> dict[str, float] | None:
    return result_dict.get("d7b_llm_scores")


def build_aggregate_record(
    *,
    candidates: list[dict],
    per_call_records: list[dict],
    fire_timestamp_utc_start: str,
    fire_timestamp_utc_end: str,
    d7b_prompt_template_sha256: str,
    selection_json_sha256_start: str,
    expectations_file_sha256: str,
    selection_commit_timestamp_utc: str | None,
    expectations_commit_timestamp_utc: str | None,
    selection_tier: int,
    selection_warnings_count: int,
    sequence_aborted: bool,
    abort_reason: str | None,
    abort_at_call_index: int | None,
    total_wall_clock_seconds: float,
    fire_script_command: str,
) -> dict:
    """Build the full aggregate record payload (no ``write_completed_at``)."""
    completed = len(per_call_records)

    # Sequence-oriented ordered lists.
    reasoning_lengths = [
        len((c["critic_result"].get("d7b_reasoning") or ""))
        for c in per_call_records
    ]
    actual_costs = [c["actual_cost_usd"] for c in per_call_records]
    estimated_costs = [c["cost"]["estimated_usd"] for c in per_call_records]
    input_tokens = [
        c["critic_result"].get("d7b_input_tokens") for c in per_call_records
    ]
    output_tokens = [
        c["critic_result"].get("d7b_output_tokens") for c in per_call_records
    ]
    wall_clocks = [c["wall_clock_seconds"] for c in per_call_records]
    statuses = [c["critic_status"] for c in per_call_records]
    error_cats = [c.get("d7b_error_category") for c in per_call_records]

    # Per-call indexed score structures.
    d7a_by_call: dict[str, dict | None] = {}
    d7b_by_call: dict[str, dict | None] = {}
    reconciliation: dict[str, dict] = {}
    for rec in per_call_records:
        idx = str(rec["firing_order"])
        d7a_by_call[idx] = _extract_d7a_scores(rec["critic_result"])
        d7b_scores = _extract_d7b_scores(rec["critic_result"])
        d7b_by_call[idx] = d7b_scores
        svr = d7b_scores.get("structural_variant_risk") if d7b_scores else None
        reconciliation[idx] = {
            "pre_registered_label": rec["pre_registered_label"],
            "d7b_structural_variant_risk": svr,
            "observed_consistent_with_label": is_consistent_with_label(
                rec["pre_registered_label"], svr,
            ),
            "rationale": reconciliation_rationale(
                rec["pre_registered_label"], svr,
            ),
        }

    total_actual = sum(float(c or 0) for c in actual_costs)
    total_estimated = sum(float(c or 0) for c in estimated_costs)
    total_input = sum(int(t or 0) for t in input_tokens)
    total_output = sum(int(t or 0) for t in output_tokens)

    return {
        "stage_label": STAGE_LABEL,
        "record_version": RECORD_VERSION,
        "batch_uuid": STAGE2B_BATCH_UUID,
        "fire_script_command": fire_script_command,
        "fire_timestamp_utc_start": fire_timestamp_utc_start,
        "fire_timestamp_utc_end": fire_timestamp_utc_end,
        # write_completed_at is appended LAST by the writer.
        "d7b_prompt_template_sha256": d7b_prompt_template_sha256,
        "selection_json_sha256": selection_json_sha256_start,
        "expectations_file_sha256": expectations_file_sha256,
        "selection_commit_timestamp_utc": selection_commit_timestamp_utc,
        "expectations_commit_timestamp_utc": expectations_commit_timestamp_utc,
        "selection_tier": selection_tier,
        "selection_warnings_count": selection_warnings_count,
        "sequence_aborted": sequence_aborted,
        "abort_reason": abort_reason,
        "abort_at_call_index": abort_at_call_index,
        "completed_call_count": completed,
        "total_wall_clock_seconds": round(total_wall_clock_seconds, 3),
        "inter_call_sleep_seconds": STAGE2B_INTER_CALL_SLEEP_SECONDS,
        "total_actual_cost_usd": round(total_actual, 6),
        "total_estimated_cost_usd": round(total_estimated, 6),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "reasoning_lengths_in_call_order": reasoning_lengths,
        "actual_costs_in_call_order": [round(v, 6) for v in actual_costs],
        "estimated_costs_in_call_order": [round(v, 6) for v in estimated_costs],
        "input_tokens_in_call_order": input_tokens,
        "output_tokens_in_call_order": output_tokens,
        "wall_clock_seconds_in_call_order": wall_clocks,
        "critic_statuses_in_call_order": statuses,
        "d7b_error_categories_in_call_order": error_cats,
        "d7a_scores_by_call": d7a_by_call,
        "d7b_scores_by_call": d7b_by_call,
        "agreement_divergence_reconciliation_by_call": reconciliation,
        "per_call_records": per_call_records,
    }


# ---------------------------------------------------------------------------
# Startup phase (pre-fire gates)
# ---------------------------------------------------------------------------


def _startup_gates(config: Stage2bConfig) -> tuple[dict, list[dict], str, str, str]:
    """Run all pre-fire gates HG1–HG8 (plus HG2b, HG4b, HG6, HG7).

    Returns (selection_dict, candidates, selection_sha256,
    prompt_template_sha256, expectations_sha256).

    Raises Stage2bStartupError on any failure.
    """
    # HG1 — selection JSON exists and parses.
    if not config.selection_json_path.exists():
        raise Stage2bStartupError(
            f"HG1: selection JSON missing at {config.selection_json_path}"
        )
    try:
        raw = config.selection_json_path.read_bytes()
        selection = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise Stage2bStartupError(
            f"HG1: selection JSON unreadable/unparseable: {exc}"
        ) from exc

    # HG2 — capture selection JSON SHA-256.
    selection_sha256_start = hashlib.sha256(raw).hexdigest()

    # HG2b — invariants.
    verify_selection_invariants(selection)

    # HG1 surface — candidates validated.
    candidates = verify_candidate_count_and_keys(selection)

    # HG3 — expectations exists and committed.
    if not config.expectations_path.exists():
        raise Stage2bStartupError(
            f"HG3: expectations file missing at {config.expectations_path}. "
            "Charlie must author and commit "
            "docs/d7_stage2b/stage2b_expectations.md before fire."
        )
    expectations_ts = config.expectations_commit_ts_fn(config.expectations_path)
    if expectations_ts is None:
        raise Stage2bStartupError(
            f"HG3: expectations file at {config.expectations_path} is not "
            "committed to git (no commit timestamp)."
        )

    # HG4 + HG4b — structural + identity validation.
    expectations_text = config.expectations_path.read_text(encoding="utf-8")
    validate_expectations_file(expectations_text, candidates)

    # HG5 — commit ordering.
    selection_ts = config.selection_commit_ts_fn(config.selection_json_path)
    now_ts = config.now_unixtime_fn()
    verify_commit_ordering(selection_ts, expectations_ts, now_ts)

    # HG6 — prompt template SHA-256 captured.
    if not config.prompt_template_path.exists():
        raise Stage2bStartupError(
            f"HG6: D7b prompt template missing at {config.prompt_template_path}"
        )
    prompt_template_sha256 = _file_sha256(config.prompt_template_path)

    # HG7 — expectations file SHA-256 captured.
    expectations_sha256 = _file_sha256(config.expectations_path)

    # HG8 — no existing aggregate record.
    if config.aggregate_record_path.exists():
        raise Stage2bStartupError(
            f"HG8: aggregate record already exists at "
            f"{config.aggregate_record_path}. Stage 2b aggregate artifacts "
            "are append-only and immutable. To re-run, move or archive the "
            "existing file first."
        )

    return (
        selection,
        candidates,
        selection_sha256_start,
        prompt_template_sha256,
        expectations_sha256,
    )


# ---------------------------------------------------------------------------
# Per-call phase
# ---------------------------------------------------------------------------


def _critic_dir(raw_payload_root: Path, batch_uuid: str) -> Path:
    d = raw_payload_root / f"batch_{batch_uuid}" / "critic"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _run_one_call(
    *,
    config: Stage2bConfig,
    candidate: dict,
    startup_prompt_template_sha256: str,
    ledger: BudgetLedger,
    inter_call_sleep_elapsed_seconds: float,
    cumulative_cost_usd: float,
) -> dict:
    """Fire one candidate; return the per-call record.

    Raises Stage2bStartupError on HG6b template drift. All D7b errors
    become critic_status=d7b_error per the orchestrator contract.
    """
    position = candidate["position"]
    backend_label = "stub" if config.stub else "live"
    request_ts = datetime.now(timezone.utc)

    # HG6b — re-verify prompt template hash (mid-sequence drift guard).
    live_template_sha = _file_sha256(config.prompt_template_path)
    if live_template_sha != startup_prompt_template_sha256:
        raise Stage2bStartupError(
            f"HG6b: prompt template SHA-256 drift between startup "
            f"({startup_prompt_template_sha256}) and call at position "
            f"{position} ({live_template_sha}). "
            "Abort reason: prompt_template_mutated_mid_run"
        )

    # HG9 — reconstruct BatchContext.
    dsl, theme, batch_context = config.reconstruct_fn(
        STAGE2B_BATCH_UUID, position,
        stage2d_artifacts_root=RAW_PAYLOAD_ROOT,
    )
    prompt_text = build_d7b_prompt(dsl, theme, batch_context)
    prompt_sha256 = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()

    # Telemetry (lock D).
    prior_factor_sets_count = len(batch_context.prior_factor_sets)
    theme_hint_factor_count = len(batch_context.theme_hints.get(theme, frozenset()))

    # HG10 — leakage audit (orchestrator also runs it, but we capture result).
    leakage_audit_result = _capture_leakage_audit_result(prompt_text)

    # HG15 — always persist prompt (forensic preservation).
    critic_dir = _critic_dir(config.raw_payload_root, STAGE2B_BATCH_UUID)
    prompt_path = critic_dir / f"call_{position:04d}_prompt.txt"
    prompt_path.write_text(prompt_text, encoding="utf-8")

    # Backend + estimated cost.
    if config.backend_factory is not None:
        backend = config.backend_factory(
            raw_payload_dir=config.raw_payload_root,
            api_call_number=position,
            batch_id=STAGE2B_BATCH_UUID,
        )
        estimated_cost = STAGE2B_PER_CALL_COST_CEILING_USD if not config.stub else 0.0
    elif config.stub:
        backend = StubD7bBackend()
        estimated_cost = 0.0
    else:
        # Lazy import keeps dryrun runnable without an anthropic client available.
        from agents.critic.d7b_live import (
            D7B_STAGE2A_COST_CEILING_USD,
            LiveSonnetD7bBackend,
        )
        backend = LiveSonnetD7bBackend(
            raw_payload_dir=config.raw_payload_root,
            api_call_number=position,
            batch_id=STAGE2B_BATCH_UUID,
        )
        estimated_cost = D7B_STAGE2A_COST_CEILING_USD

    # Ledger pre-charge (HG13).
    api_call_kind = config.api_call_kind_override or f"d7b_critic_{backend_label}"
    row_id = ledger.write_pending(
        batch_id=STAGE2B_BATCH_UUID,
        api_call_kind=api_call_kind,
        backend_kind="d7b_critic",
        call_role="critique",
        estimated_cost_usd=estimated_cost,
        now=request_ts,
        notes=(
            f"Stage 2b {backend_label}, position={position}, "
            f"firing_order={candidate['firing_order']}"
        ),
    )

    # Fire.
    result = run_critic(dsl, theme, batch_context, backend)
    response_ts = datetime.now(timezone.utc)

    actual_cost = float(result.d7b_cost_actual_usd or 0.0)

    # Finalize ledger.
    ledger.finalize(
        row_id,
        actual_cost_usd=actual_cost,
        now=response_ts,
        input_tokens=result.d7b_input_tokens,
        output_tokens=result.d7b_output_tokens,
    )

    # Persist CriticResult artifact (HG15).
    result_path = critic_dir / f"call_{position:04d}_critic_result.json"
    result_path.write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    response_path = critic_dir / f"call_{position:04d}_response.json"
    traceback_path = critic_dir / f"call_{position:04d}_traceback.txt"

    raw_payload_paths = {
        "prompt": str(prompt_path),
        "response": str(response_path) if response_path.exists() else None,
        "traceback": str(traceback_path) if traceback_path.exists() else None,
        "critic_result": str(result_path),
    }

    # Assemble per-call record.
    record = build_per_call_record(
        candidate=candidate,
        prompt_text=prompt_text,
        prompt_sha256=prompt_sha256,
        prior_factor_sets_count=prior_factor_sets_count,
        theme_hint_factor_count=theme_hint_factor_count,
        request_ts=request_ts,
        response_ts=response_ts,
        result=result,
        ledger_row_id=row_id,
        backend_label=backend_label,
        estimated_cost_usd=estimated_cost,
        actual_cost_usd=actual_cost,
        raw_payload_paths=raw_payload_paths,
        leakage_audit_result=leakage_audit_result,
        inter_call_sleep_elapsed_seconds=inter_call_sleep_elapsed_seconds,
    )

    # Write per-call record to disk (HG14).
    per_call_path = (
        config.per_call_record_dir
        / f"call_{candidate['firing_order']}_live_call_record.json"
    )
    atomic_write_json(per_call_path, record)
    record["__per_call_record_path"] = str(per_call_path)

    # Console breadcrumb.
    factors = extract_factors(dsl)
    print(
        f"[stage2b] call {candidate['firing_order']}/{STAGE2B_N} "
        f"position={position} theme={theme} factors={len(factors)} "
        f"status={result.critic_status} cost=${actual_cost:.6f}"
    )

    return record


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def run_stage2b(config: Stage2bConfig) -> dict:
    """Orchestrate the full 5-call Stage 2b sequence.

    Returns the aggregate record as a dict. Raises Stage2bStartupError on
    pre-fire gate failure; otherwise writes the aggregate record to disk
    even on sequence abort.
    """
    # Startup gates.
    (
        selection,
        candidates,
        selection_sha256_start,
        prompt_template_sha256,
        expectations_sha256,
    ) = _startup_gates(config)

    selection_commit_iso = None
    expectations_commit_iso = None
    s_ts = config.selection_commit_ts_fn(config.selection_json_path)
    e_ts = config.expectations_commit_ts_fn(config.expectations_path)
    if s_ts is not None:
        selection_commit_iso = datetime.fromtimestamp(
            s_ts, tz=timezone.utc
        ).isoformat().replace("+00:00", "Z")
    if e_ts is not None:
        expectations_commit_iso = datetime.fromtimestamp(
            e_ts, tz=timezone.utc
        ).isoformat().replace("+00:00", "Z")

    # Stage 2a archival (live mode only; stub is physically isolated).
    if not config.stub:
        critic_dir = _critic_dir(config.raw_payload_root, STAGE2B_BATCH_UUID)
        archive_stage2a_artifacts_if_present(critic_dir, position=73)

    fire_timestamp_utc_start = config.now_iso_fn()
    t0 = time.monotonic()
    ledger = BudgetLedger(config.ledger_path)

    per_call_records: list[dict] = []
    sequence_aborted = False
    abort_reason: str | None = None
    abort_at_call_index: int | None = None
    cumulative_cost = 0.0
    inter_call_sleep_elapsed = 0.0

    fire_script_command = (
        "python scripts/run_d7_stage2b_batch.py "
        + ("--confirm-live" if config.confirm_live else "--stub")
    )

    try:
        for idx, candidate in enumerate(candidates, 1):
            record = _run_one_call(
                config=config,
                candidate=candidate,
                startup_prompt_template_sha256=prompt_template_sha256,
                ledger=ledger,
                inter_call_sleep_elapsed_seconds=inter_call_sleep_elapsed,
                cumulative_cost_usd=cumulative_cost,
            )
            per_call_records.append(record)
            current_cost = float(record["actual_cost_usd"] or 0.0)
            cumulative_cost += current_cost

            # Cost gates first — these fire BEFORE any further action.
            abort, reason = should_abort(
                idx, per_call_records, current_cost, cumulative_cost,
            )
            if abort:
                sequence_aborted = True
                abort_reason = reason
                abort_at_call_index = idx
                break

            # Inter-call sleep (not after the last call).
            if idx < STAGE2B_N:
                t_before = time.monotonic()
                config.sleep_fn(STAGE2B_INTER_CALL_SLEEP_SECONDS)
                inter_call_sleep_elapsed = time.monotonic() - t_before

    except Stage2bStartupError as exc:
        # HG6b template drift (mid-sequence) — record + re-raise after write.
        sequence_aborted = True
        abort_reason = "prompt_template_mutated_mid_run"
        abort_at_call_index = len(per_call_records) + 1
        print(f"[stage2b] HG6b abort: {exc}", file=sys.stderr)

    total_wall_clock = time.monotonic() - t0
    fire_timestamp_utc_end = config.now_iso_fn()

    # Build aggregate record (without write_completed_at).
    agg = build_aggregate_record(
        candidates=candidates,
        per_call_records=[
            {k: v for k, v in r.items() if not k.startswith("__")}
            for r in per_call_records
        ],
        fire_timestamp_utc_start=fire_timestamp_utc_start,
        fire_timestamp_utc_end=fire_timestamp_utc_end,
        d7b_prompt_template_sha256=prompt_template_sha256,
        selection_json_sha256_start=selection_sha256_start,
        expectations_file_sha256=expectations_sha256,
        selection_commit_timestamp_utc=selection_commit_iso,
        expectations_commit_timestamp_utc=expectations_commit_iso,
        selection_tier=selection.get("selection_tier"),
        selection_warnings_count=len(selection.get("selection_warnings", [])),
        sequence_aborted=sequence_aborted,
        abort_reason=abort_reason,
        abort_at_call_index=abort_at_call_index,
        total_wall_clock_seconds=total_wall_clock,
        fire_script_command=fire_script_command,
    )

    # HG20 — re-hash selection JSON at sequence end.
    selection_sha256_end = _file_sha256(config.selection_json_path)
    if selection_sha256_end != selection_sha256_start:
        # This is a post-sequence gate; log but do not prevent record writing,
        # so the forensic evidence of drift is preserved in the aggregate.
        print(
            f"[stage2b] HG20 WARNING: selection JSON SHA-256 drift "
            f"({selection_sha256_start} -> {selection_sha256_end})",
            file=sys.stderr,
        )
        agg["selection_json_sha256_end"] = selection_sha256_end
        agg["hg20_drift_detected"] = True

    # HG16 — set write_completed_at LAST (immutability signal).
    agg["write_completed_at"] = config.now_iso_fn()
    atomic_write_json(config.aggregate_record_path, agg)

    # Console summary.
    print(
        f"\n[stage2b] completed_call_count={len(per_call_records)}/{STAGE2B_N} "
        f"total_actual_cost=${agg['total_actual_cost_usd']:.6f}"
    )
    if sequence_aborted:
        print(
            f"[stage2b] SEQUENCE ABORTED: reason={abort_reason} "
            f"at_call={abort_at_call_index}"
        )
    print(f"[stage2b] aggregate record: {config.aggregate_record_path}")

    return agg


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    _load_dotenv()

    parser = argparse.ArgumentParser(
        description=(
            "D7 Stage 2b: five-call live D7b probe against signed-off "
            f"batch {STAGE2B_BATCH_UUID}."
        ),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--stub",
        action="store_true",
        help="Stub mode — no API calls; writes to dryrun_payloads/dryrun_stage2b/.",
    )
    group.add_argument(
        "--confirm-live",
        action="store_true",
        help="Live mode — calls Sonnet. Requires ANTHROPIC_API_KEY.",
    )
    args = parser.parse_args()

    try:
        config = build_stage2b_config(
            confirm_live=args.confirm_live, stub=args.stub,
        )
        run_stage2b(config)
    except Stage2bStartupError as exc:
        print(f"[stage2b] STARTUP ABORT: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - unexpected
        print(
            f"[stage2b] UNCAUGHT ERROR during sequence: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
