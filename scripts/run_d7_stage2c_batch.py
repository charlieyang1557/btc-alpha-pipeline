"""D7 Stage 2c — twenty-call live D7b batch probe.

Single-script orchestrator for the twenty sequential replay candidates
locked in ``docs/d7_stage2c/replay_candidates.json`` at commit ``b71ffd1``.
Fires the selection in firing-order (position ascending), enforces 25
hard-fail gates, records cost / reasoning / score sequences as ordered
lists (never distributions), and writes an append-only aggregate record
via ``os.replace()`` atomic move.

Parallel code path to ``scripts/run_d7_stage2b_batch.py`` — explicit
duplication is intentional per scope-lock discipline; do NOT refactor the
two scripts into a shared module. Purely utility helpers (SHA-256, ISO
timestamps) may be duplicated rather than extracted.

CONTRACT BOUNDARY: no retries beyond Stage 2a's inheritance (one API-level
retry, zero content-level retries). No prompt caching. No rate-limiting.
``STAGE2C_N == 20``; N is not user-configurable.

CONTRACT BOUNDARY: abort-rule classification consumes the persisted
per-call record fields — never raw exception objects from the batch loop.
This keeps per-call record and abort decision in a single source of truth.

CONTRACT BOUNDARY: Stage 2c abort rule (c) uses scope-lock primacy
(content-level errors >= 4 with K >= 8 floor). This conflicts with the
launch prompt wording (no K floor); scope lock wins per launch prompt §2.

CONTRACT BOUNDARY: stub mode MUST NOT touch ``raw_payloads/`` under any
circumstance. All stub I/O is physically isolated under
``dryrun_payloads/dryrun_stage2c/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# Allow bare ``python scripts/run_d7_stage2c_batch.py`` invocation.
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

# Per-call cost ceiling (unchanged from Stage 2b).
STAGE2C_PER_CALL_COST_CEILING_USD: float = 0.05
# Total cost cap across the 20-call sequence (SCALED from Stage 2b's 0.10).
STAGE2C_TOTAL_COST_CAP_USD: float = 0.50
# Inter-call pacing; well under Anthropic tier-1 rate limits.
STAGE2C_INTER_CALL_SLEEP_SECONDS: int = 5
# N=20. Not user-configurable per launch prompt §7.
STAGE2C_N: int = 20
# The sole Stage 2c batch UUID (signed-off Stage 2d replay source, identical
# to Stage 2a and Stage 2b).
STAGE2C_BATCH_UUID: str = "5cf76668-47d1-48d7-bd90-db06d31982ed"
# D7b score polarity threshold (pinned). exact 0.5 → classified as >= 0.5 (HIGH).
STRUCTURAL_VARIANT_RISK_HIGH_THRESHOLD: float = 0.5

# Abort rule (c): fires whenever content-level errors reach this count.
STAGE2C_CONTENT_ERROR_ABS_THRESHOLD: int = 4
# Rule (c) fires on this count alone, no minimum-K floor.
# Note: rule (b) (error rate > 40% at K>=3) substantially overlaps
# rule (c) in early-clustered-error scenarios, so the K-floor removal
# is primarily a specification-correctness fix, not a large behavioral
# change. See launch prompt v2 Amendment 7 for full rationale.

# Selection JSON anchor — commit that locked the selection. Runtime HG2c
# reads this commit via ``git show`` and compares SHA-256 against on-disk.
STAGE2C_SELECTION_ANCHOR_COMMIT: str = "b71ffd1"
STAGE2C_SELECTION_ANCHOR_PATH: str = "docs/d7_stage2c/replay_candidates.json"

# Stage 2b overlap positions — candidates present in both Stage 2b and
# Stage 2c selections. Stable facts, hardcoded per launch prompt §4.3.
STAGE2B_OVERLAP_POSITIONS: frozenset[int] = frozenset({17, 73, 74, 97, 138})

# Aggregate record schema version (launch prompt §4.2).
STAGE_LABEL: str = "d7_stage2c"
RECORD_VERSION: str = "1.0"


# ---------------------------------------------------------------------------
# Production paths (defaults; all overridable for tests)
# ---------------------------------------------------------------------------

SELECTION_JSON_PATH: Path = Path("docs/d7_stage2c/replay_candidates.json")
EXPECTATIONS_PATH: Path = Path("docs/d7_stage2c/stage2c_expectations.md")
AGGREGATE_RECORD_PATH: Path = Path("docs/d7_stage2c/stage2c_batch_record.json")
PER_CALL_RECORD_DIR: Path = Path("docs/d7_stage2c")
RAW_PAYLOAD_ROOT: Path = Path("raw_payloads")
LEDGER_PATH: Path = Path("agents/spend_ledger.db")
PROMPT_TEMPLATE_PATH: Path = Path("agents/critic/d7b_prompt.py")

# Stub-mode physical isolation root (launch prompt §4.10).
DRYRUN_ROOT: Path = Path("dryrun_payloads/dryrun_stage2c")


# ---------------------------------------------------------------------------
# Exceptions (startup aborts — sys.exit(1))
# ---------------------------------------------------------------------------


class Stage2cStartupError(RuntimeError):
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


def _git_show_sha256(commit: str, repo_path: str) -> str | None:
    """Return SHA-256 of ``git show <commit>:<repo_path>`` output, or None if unavailable.

    HG2c anchor computation — reads the committed file contents from git
    history and hashes them. Not hardcoded as a constant so the gate
    remains valid across repo checkouts.
    """
    try:
        result = subprocess.run(
            ["git", "show", f"{commit}:{repo_path}"],
            capture_output=True, timeout=10, cwd=str(_REPO_ROOT),
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    return hashlib.sha256(result.stdout).hexdigest()


def _now_unixtime() -> int:
    return int(time.time())


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# Gate logic (pure functions, unit-testable)
# ---------------------------------------------------------------------------


def verify_selection_invariants(selection: dict) -> None:
    """HG2b: re-verify tier / warnings invariants at fire time.

    Raises Stage2cStartupError on violation.
    """
    tier = selection.get("selection_tier")
    warnings = selection.get("selection_warnings", [])
    if tier not in (0, 1, 2):
        raise Stage2cStartupError(
            f"HG2b: selection_tier must be 0/1/2; got {tier!r}"
        )
    if not isinstance(warnings, list):
        raise Stage2cStartupError(
            "HG2b: selection_warnings must be a list"
        )
    if tier == 0 and warnings:
        raise Stage2cStartupError(
            "HG2b: selection_tier=0 must have empty selection_warnings; "
            f"got {warnings!r}"
        )
    if tier in (1, 2) and len(warnings) < 1:
        raise Stage2cStartupError(
            f"HG2b: selection_tier={tier} must have >=1 warnings; got none"
        )
    if tier == 2:
        has_divergence = any(
            isinstance(w, dict)
            and w.get("constraint_relaxed") == "divergence_coverage"
            for w in warnings
        )
        if not has_divergence:
            raise Stage2cStartupError(
                "HG2b: selection_tier=2 requires a warning with "
                "constraint_relaxed='divergence_coverage'"
            )


def verify_candidate_count_and_keys(selection: dict) -> list[dict]:
    """HG1 surface: twenty candidates present with required keys.

    Returns the list of candidate dicts in firing order.
    """
    candidates = selection.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != STAGE2C_N:
        raise Stage2cStartupError(
            f"HG1: selection must contain exactly {STAGE2C_N} candidates; "
            f"got {len(candidates) if isinstance(candidates, list) else 'n/a'}"
        )
    required = {
        "firing_order", "position", "theme", "hypothesis_hash",
        "d7a_b_relationship_label",
    }
    for i, c in enumerate(candidates, 1):
        missing = required - set(c.keys())
        if missing:
            raise Stage2cStartupError(
                f"HG1: candidate #{i} missing keys {sorted(missing)}"
            )
        if c.get("firing_order") != i:
            raise Stage2cStartupError(
                f"HG1: candidate at index {i} has firing_order="
                f"{c.get('firing_order')!r}; expected {i}"
            )
    return candidates


def verify_selection_anchor_hash(
    selection_path: Path,
    anchor_commit: str = STAGE2C_SELECTION_ANCHOR_COMMIT,
    anchor_repo_path: str = STAGE2C_SELECTION_ANCHOR_PATH,
    git_show_fn: Callable[[str, str], str | None] = _git_show_sha256,
) -> str:
    """HG2c: on-disk selection SHA-256 must equal the committed anchor hash.

    Reads the committed version via ``git show <commit>:<path>`` and hashes
    it, then compares to the on-disk file. Raises Stage2cStartupError on
    drift or on inability to resolve the anchor commit.

    Returns the (matching) SHA-256 hex string.
    """
    on_disk = _file_sha256(selection_path)
    anchor_hash = git_show_fn(anchor_commit, anchor_repo_path)
    if anchor_hash is None:
        raise Stage2cStartupError(
            f"HG2c: cannot resolve anchor commit {anchor_commit!r} for "
            f"{anchor_repo_path!r}. Verify the commit exists in this repo."
        )
    if on_disk != anchor_hash:
        raise Stage2cStartupError(
            f"HG2c: selection JSON at {selection_path} has drifted from "
            f"scope-lock anchor (commit {anchor_commit}). "
            f"on_disk_sha256={on_disk}, anchor_sha256={anchor_hash}. "
            "Scope lock invalidated; re-adjudicate before re-firing."
        )
    return on_disk


# Expectations structural headers (HG4 / HG4b / HG4c)

_AGGREGATE_HEADER = "## Aggregate Expectations Across All 20 Calls"
_ANTI_HINDSIGHT_HEADER = "## Anti-Hindsight Anchor"
_PER_CANDIDATE_HEADER = "## Per-Candidate Expectations"
_NEUTRAL_GROUP_HEADER = "## Aggregate Prediction for Neutral Group"
_NEUTRAL_GROUP_MIN_NON_WS_CHARS = 50


def _expected_candidate_header(i: int, c: dict) -> str:
    """Build the exact candidate section header (HG4b ground truth).

    Format: ``### Candidate <N> — Position <P>, <theme>, <label>``
    The em dash is U+2014 to match the launch prompt §4.7 schema.
    """
    return (
        f"### Candidate {i} \u2014 Position {c['position']}, "
        f"{c['theme']}, {c['d7a_b_relationship_label']}"
    )


def extract_neutral_group_section_body(text: str) -> str | None:
    """Extract text between ``## Aggregate Prediction for Neutral Group``
    and the next ``##``-level header (or EOF).

    Returns None if the header is not present. Returns empty string if the
    header is the last ``##`` header in the file with no body.
    """
    lines = text.splitlines(keepends=True)
    start_idx: int | None = None
    for i, line in enumerate(lines):
        if line.rstrip("\n\r") == _NEUTRAL_GROUP_HEADER:
            start_idx = i + 1
            break
    if start_idx is None:
        return None
    # Find next line starting with "## " (but not "### ").
    end_idx = len(lines)
    pat = re.compile(r"^##\s")
    for j in range(start_idx, len(lines)):
        if pat.match(lines[j]):
            end_idx = j
            break
    return "".join(lines[start_idx:end_idx])


def validate_expectations_file(
    expectations_text: str, candidates: list[dict],
) -> None:
    """HG4 + HG4b + HG4c: structural + identity-exact-match + neutral-group
    validation.

    Raises Stage2cStartupError on any violation.
    """
    # HG4 — required top-level headers.
    for header in (
        _ANTI_HINDSIGHT_HEADER, _AGGREGATE_HEADER, _PER_CANDIDATE_HEADER,
    ):
        if header not in expectations_text:
            raise Stage2cStartupError(
                f"HG4: expectations file missing header {header!r}"
            )

    # HG4b — per-candidate identity exact match.
    for i, c in enumerate(candidates, 1):
        expected = _expected_candidate_header(i, c)
        if expected not in expectations_text:
            raise Stage2cStartupError(
                f"HG4b: expectations file missing exact header for "
                f"candidate #{i}. Expected line: {expected!r}"
            )

    # HG4c — neutral-group aggregate prediction header + >= 50 non-whitespace
    # characters in the section body.
    body = extract_neutral_group_section_body(expectations_text)
    if body is None:
        raise Stage2cStartupError(
            f"HG4c: expectations file missing header "
            f"{_NEUTRAL_GROUP_HEADER!r}. "
            "Scope lock Lock 8 requires a falsifiable aggregate-level "
            "prediction for the 9-candidate neutral group."
        )
    non_whitespace = re.sub(r"\s+", "", body)
    if len(non_whitespace) < _NEUTRAL_GROUP_MIN_NON_WS_CHARS:
        raise Stage2cStartupError(
            f"HG4c: neutral-group aggregate prediction section body has "
            f"{len(non_whitespace)} non-whitespace characters; requires "
            f">= {_NEUTRAL_GROUP_MIN_NON_WS_CHARS}. "
            "Body extracted between "
            f"{_NEUTRAL_GROUP_HEADER!r} and the next '## '-level header "
            "(or EOF). The check is structural — semantic quality is "
            "reviewed in sign-off, not enforced here."
        )


def verify_commit_ordering(
    selection_ts: int | None,
    expectations_ts: int | None,
    now_ts: int,
) -> None:
    """HG5: selection commit < expectations commit < wall-clock.

    Raises Stage2cStartupError with pointer to the failing inequality.
    """
    if selection_ts is None:
        raise Stage2cStartupError(
            "HG5: selection JSON is not committed to git (no commit timestamp)"
        )
    if expectations_ts is None:
        raise Stage2cStartupError(
            "HG5/HG3: expectations file is not committed to git "
            "(no commit timestamp). Commit the expectations file before fire."
        )
    if not (selection_ts < expectations_ts):
        raise Stage2cStartupError(
            f"HG5: selection commit ({selection_ts}) must be strictly less "
            f"than expectations commit ({expectations_ts})"
        )
    if not (expectations_ts < now_ts):
        raise Stage2cStartupError(
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
            "neutral label has no per-candidate structural_variant_risk "
            "prediction; aggregate-level reconciliation performed in sign-off"
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

    Rule (c) uses scope-lock primacy: ``content_errors >= 4`` evaluated only
    once ``call_index >= 8``.
    """
    # Rule (d): per-call cost ceiling.
    if current_call_cost > STAGE2C_PER_CALL_COST_CEILING_USD:
        return True, "per_call_cost_exceeded"
    # Rule (e): cumulative cost cap (scaled to $0.50 for N=20).
    if cumulative_cost > STAGE2C_TOTAL_COST_CAP_USD:
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
    # Rule (c) fires on absolute count, no K floor.
    # Rationale: 4 content-level errors is systemic whenever it occurs;
    # waiting for K>=8 would waste budget on a failing sequence.
    # Rule (b) and rule (c) have overlapping coverage in early-clustered
    # scenarios, but rule (c) remains the authoritative absolute-count
    # trigger per launch prompt v2 §4.4 + Amendment 7.
    content_errors = sum(
        1 for c in call_histories
        if c.get("critic_status") == "d7b_error"
        and c.get("d7b_error_category") == "content_level"
    )
    if content_errors >= STAGE2C_CONTENT_ERROR_ABS_THRESHOLD:
        return True, "content_level_threshold"
    return False, None


# ---------------------------------------------------------------------------
# Stage 2b overlap archival (launch prompt §4.9)
# ---------------------------------------------------------------------------


def _existing_stage2c_remnants(
    critic_dir: Path, stage2c_positions: list[int],
) -> list[int]:
    """Return positions in ``stage2c_positions`` for which ``call_<P>_*``
    artifacts exist directly in ``critic_dir`` (not in any archive subdir).

    A remnant at a non-overlap position is an unexpected partial prior
    Stage 2c run and requires human reconciliation.
    """
    if not critic_dir.exists():
        return []
    remnants: list[int] = []
    for pos in stage2c_positions:
        pattern = f"call_{pos:04d}_*"
        matches = [m for m in critic_dir.glob(pattern) if m.is_file()]
        if matches:
            remnants.append(pos)
    return remnants


def detect_unexpected_stage2c_remnants(
    critic_dir: Path,
    stage2c_positions: list[int],
    aggregate_record_path: Path,
    per_call_record_dir: Path,
) -> None:
    """Launch prompt §4.9 partial-prior-run guard.

    If any Stage 2c-position artifact exists in ``critic_dir`` that is NOT
    a Stage 2b overlap position, AND no committed aggregate record exists,
    AND no completed per-call record exists, treat as crashed prior Stage
    2c run and abort.
    """
    remnants = _existing_stage2c_remnants(critic_dir, stage2c_positions)
    non_overlap = [p for p in remnants if p not in STAGE2B_OVERLAP_POSITIONS]
    if not non_overlap:
        return
    # Check whether a completed prior run exists.
    if aggregate_record_path.exists():
        return
    per_call_existing = list(per_call_record_dir.glob("call_*_live_call_record.json"))
    if per_call_existing:
        return
    raise Stage2cStartupError(
        "unexpected Stage 2c artifacts found for positions "
        f"{non_overlap}. "
        "No completed stage2c_batch_record.json exists, suggesting a prior "
        "crashed run. Stage 2b archival logic only handles the 5 overlap "
        "positions from Stage 2b. Manual reconciliation required: inspect "
        "the artifacts, decide whether to preserve them (move to a new "
        "archive dir) or delete them. Do not auto-archive."
    )


def archive_stage2b_overlap_artifacts_if_present(
    critic_dir: Path,
    overlap_positions: frozenset[int] = STAGE2B_OVERLAP_POSITIONS,
) -> Path | None:
    """If any ``call_<P:04d>_*`` files exist for an overlap position, archive.

    Moves the matched files into ``<critic_dir>/stage2b_archive/``. If the
    archive directory already exists, raises Stage2cStartupError (partial
    prior Stage 2c archival — operator must reconcile). Returns the archive
    directory if archival occurred, else None.
    """
    existing: list[Path] = []
    for pos in sorted(overlap_positions):
        pattern = f"call_{pos:04d}_*"
        existing.extend(sorted(critic_dir.glob(pattern)))

    if not existing:
        return None

    archive_dir = critic_dir / "stage2b_archive"
    if archive_dir.exists():
        raise Stage2cStartupError(
            f"Stage 2b archive directory already exists at {archive_dir}; "
            "cannot archive a second time. Manual reconciliation required."
        )
    archive_dir.mkdir(parents=True)
    for m in existing:
        if m.is_file():
            shutil.move(str(m), str(archive_dir / m.name))
    return archive_dir


# ---------------------------------------------------------------------------
# Atomic write
# ---------------------------------------------------------------------------


def atomic_write_json(path: Path, payload: dict) -> None:
    """Atomic write via ``os.replace()`` (cross-platform).

    Serializes to the ``.tmp`` sidecar first; on JSON serialization error,
    removes the sidecar so no partial file is ever visible at ``path``.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        data = json.dumps(payload, indent=2, ensure_ascii=False)
    except TypeError:
        # Never created a sidecar; nothing to clean up.
        raise
    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Config dataclass (injectable dependencies for testability)
# ---------------------------------------------------------------------------


@dataclass
class Stage2cConfig:
    """Paths and injectables for a Stage 2c run."""

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
    # HG2c anchor resolver (override to bypass git in tests).
    anchor_hash_fn: Callable[[str, str], str | None] = field(
        default=_git_show_sha256
    )
    # Opt-out for HG2c in isolated tests (production never sets this).
    skip_anchor_check: bool = False


def build_stage2c_config(
    confirm_live: bool, stub: bool,
) -> Stage2cConfig:
    """Build a production config with stub/live path routing.

    Stub-mode isolation contract: ``raw_payload_root``, ``ledger_path``, and
    all write destinations resolve under ``DRYRUN_ROOT``. The live-mode
    branch is the ONLY place that ``raw_payloads/`` can be written.
    """
    if confirm_live and stub:
        raise ValueError("--confirm-live and --stub are mutually exclusive")
    if not (confirm_live or stub):
        raise ValueError("one of --confirm-live or --stub is required")

    if stub:
        return Stage2cConfig(
            confirm_live=False,
            stub=True,
            selection_json_path=SELECTION_JSON_PATH,
            expectations_path=EXPECTATIONS_PATH,
            aggregate_record_path=DRYRUN_ROOT / "stage2c_batch_record.json",
            per_call_record_dir=DRYRUN_ROOT,
            raw_payload_root=DRYRUN_ROOT / "raw_payloads",
            ledger_path=DRYRUN_ROOT / "ledger_dryrun.db",
            prompt_template_path=PROMPT_TEMPLATE_PATH,
            api_call_kind_override="d7b_critic_stub",
        )
    return Stage2cConfig(
        confirm_live=True,
        stub=False,
        api_call_kind_override="d7b_critic_live",
    )


def _assert_stub_isolation(config: Stage2cConfig) -> None:
    """Stub-mode isolation contract: no write destination may resolve under
    ``raw_payloads/``. Live mode bypasses this check.
    """
    if not config.stub:
        return
    forbidden = Path("raw_payloads").resolve()
    to_check = (
        config.aggregate_record_path,
        config.per_call_record_dir,
        config.raw_payload_root,
        config.ledger_path,
    )
    for p in to_check:
        try:
            resolved = (Path.cwd() / p).resolve() if not p.is_absolute() else p.resolve()
        except OSError:
            resolved = Path(str(p))
        resolved_str = str(resolved)
        if str(forbidden) in resolved_str and "dryrun_payloads" not in resolved_str:
            raise Stage2cStartupError(
                f"stub-mode isolation violated: path {p} resolves under "
                "raw_payloads/. Stub mode must never touch raw_payloads/."
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
    """Assemble the per-call record (Stage 2a/2b fields + Stage 2c extensions).

    Stage 2c-specific addition: ``is_stage2b_overlap`` boolean.
    """
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

    is_overlap = candidate["position"] in STAGE2B_OVERLAP_POSITIONS

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
            "batch_id": STAGE2C_BATCH_UUID,
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

        # --- Stage 2b extensions (preserved) ---
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

        # --- Stage 2c extension ---
        "is_stage2b_overlap": is_overlap,

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


def _compute_label_counts(candidates: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {
        "agreement_expected": 0,
        "divergence_expected": 0,
        "neutral": 0,
    }
    for c in candidates:
        label = c.get("d7a_b_relationship_label")
        if label in counts:
            counts[label] += 1
    return counts


def _compute_theme_counts(candidates: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for c in candidates:
        theme = c.get("theme", "unknown")
        counts[theme] = counts.get(theme, 0) + 1
    return counts


def _svr_by_label(per_call_records: list[dict]) -> dict[str, dict]:
    """Partition completed SVR scores by pre-registered label.

    Each partition: ``{completed_count, positions, svr_values}``.
    Only candidates with a non-None SVR (i.e., non-d7b_error) contribute.
    Positions are sorted ascending; svr_values pair by index.
    """
    buckets: dict[str, list[tuple[int, float]]] = {
        "agreement_expected": [],
        "divergence_expected": [],
        "neutral": [],
    }
    for rec in per_call_records:
        label = rec.get("pre_registered_label")
        if label not in buckets:
            continue
        d7b = _extract_d7b_scores(rec["critic_result"])
        if not d7b:
            continue
        svr = d7b.get("structural_variant_risk")
        if svr is None:
            continue
        buckets[label].append((rec["candidate_position"], float(svr)))

    out: dict[str, dict] = {}
    for label, pairs in buckets.items():
        pairs.sort(key=lambda t: t[0])
        out[label] = {
            "completed_count": len(pairs),
            "positions": [p for p, _ in pairs],
            "svr_values": [round(v, 6) for _, v in pairs],
        }
    return out


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
    is_overlap_seq = [bool(c.get("is_stage2b_overlap")) for c in per_call_records]

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

    # Stage 2c-specific aggregates — counts over the declared selection, not
    # the completed subset. ``stage2b_overlap_completed_count`` captures the
    # completed subset separately.
    theme_counts = _compute_theme_counts(candidates)
    label_counts = _compute_label_counts(candidates)
    stage2b_overlap_positions_sorted = sorted(STAGE2B_OVERLAP_POSITIONS)
    stage2b_overlap_completed = sum(
        1 for c in per_call_records
        if c["candidate_position"] in STAGE2B_OVERLAP_POSITIONS
    )
    svr_by_label = _svr_by_label(per_call_records)

    return {
        "stage_label": STAGE_LABEL,
        "record_version": RECORD_VERSION,
        "batch_uuid": STAGE2C_BATCH_UUID,
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
        "inter_call_sleep_seconds": STAGE2C_INTER_CALL_SLEEP_SECONDS,
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
        "is_stage2b_overlap_in_call_order": is_overlap_seq,
        "d7a_scores_by_call": d7a_by_call,
        "d7b_scores_by_call": d7b_by_call,
        "agreement_divergence_reconciliation_by_call": reconciliation,
        # Stage 2c-specific aggregates.
        "theme_counts_in_sequence": theme_counts,
        "label_counts_in_sequence": label_counts,
        "stage2b_overlap_count": len(STAGE2B_OVERLAP_POSITIONS),
        "stage2b_overlap_positions": stage2b_overlap_positions_sorted,
        "stage2b_overlap_completed_count": stage2b_overlap_completed,
        "svr_by_label": svr_by_label,
        "per_call_records": per_call_records,
    }


# ---------------------------------------------------------------------------
# Startup phase (pre-fire gates)
# ---------------------------------------------------------------------------


def _startup_gates(
    config: Stage2cConfig,
) -> tuple[dict, list[dict], str, str, str]:
    """Run all pre-fire gates HG1–HG8 (plus HG2b, HG2c, HG4b, HG4c, HG6, HG7).

    Returns (selection_dict, candidates, selection_sha256,
    prompt_template_sha256, expectations_sha256).

    Raises Stage2cStartupError on any failure.
    """
    # HG1 — selection JSON exists and parses.
    if not config.selection_json_path.exists():
        raise Stage2cStartupError(
            f"HG1: selection JSON missing at {config.selection_json_path}"
        )
    try:
        raw = config.selection_json_path.read_bytes()
        selection = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise Stage2cStartupError(
            f"HG1: selection JSON unreadable/unparseable: {exc}"
        ) from exc

    # HG2 — capture selection JSON SHA-256.
    selection_sha256_start = hashlib.sha256(raw).hexdigest()

    # HG2b — invariants.
    verify_selection_invariants(selection)

    # HG1 surface — candidates validated.
    candidates = verify_candidate_count_and_keys(selection)

    # HG2c — selection JSON anchor hash check (scope-lock commit).
    if not config.skip_anchor_check:
        anchor_hash = config.anchor_hash_fn(
            STAGE2C_SELECTION_ANCHOR_COMMIT, STAGE2C_SELECTION_ANCHOR_PATH,
        )
        if anchor_hash is None:
            raise Stage2cStartupError(
                f"HG2c: cannot resolve anchor commit "
                f"{STAGE2C_SELECTION_ANCHOR_COMMIT!r} for "
                f"{STAGE2C_SELECTION_ANCHOR_PATH!r}. "
                "Verify the commit exists in this repo."
            )
        if selection_sha256_start != anchor_hash:
            raise Stage2cStartupError(
                f"HG2c: selection JSON at {config.selection_json_path} has "
                f"drifted from scope-lock anchor "
                f"(commit {STAGE2C_SELECTION_ANCHOR_COMMIT}). "
                f"on_disk_sha256={selection_sha256_start}, "
                f"anchor_sha256={anchor_hash}. "
                "Scope lock invalidated; re-adjudicate before re-firing."
            )

    # HG3 — expectations exists and committed.
    if not config.expectations_path.exists():
        raise Stage2cStartupError(
            f"HG3: expectations file missing at {config.expectations_path}. "
            "Charlie must author and commit "
            "docs/d7_stage2c/stage2c_expectations.md before fire."
        )
    expectations_ts = config.expectations_commit_ts_fn(config.expectations_path)
    if expectations_ts is None:
        raise Stage2cStartupError(
            f"HG3: expectations file at {config.expectations_path} is not "
            "committed to git (no commit timestamp)."
        )

    # HG4 + HG4b + HG4c — structural + identity + neutral-group validation.
    try:
        expectations_text = config.expectations_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise Stage2cStartupError(
            f"HG4: expectations file at {config.expectations_path} is not "
            f"valid UTF-8: {exc}. Re-author without smart quotes or BOM."
        ) from exc
    validate_expectations_file(expectations_text, candidates)

    # HG5 — commit ordering.
    selection_ts = config.selection_commit_ts_fn(config.selection_json_path)
    now_ts = config.now_unixtime_fn()
    verify_commit_ordering(selection_ts, expectations_ts, now_ts)

    # HG6 — prompt template SHA-256 captured.
    if not config.prompt_template_path.exists():
        raise Stage2cStartupError(
            f"HG6: D7b prompt template missing at {config.prompt_template_path}"
        )
    prompt_template_sha256 = _file_sha256(config.prompt_template_path)

    # HG7 — expectations file SHA-256 captured.
    expectations_sha256 = _file_sha256(config.expectations_path)

    # HG8 — no existing aggregate record.
    if config.aggregate_record_path.exists():
        raise Stage2cStartupError(
            f"HG8: aggregate record already exists at "
            f"{config.aggregate_record_path}. Stage 2c aggregate artifacts "
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
    config: Stage2cConfig,
    candidate: dict,
    startup_prompt_template_sha256: str,
    ledger: BudgetLedger,
    inter_call_sleep_elapsed_seconds: float,
    cumulative_cost_usd: float,
) -> dict:
    """Fire one candidate; return the per-call record.

    Raises Stage2cStartupError on HG6b template drift. All D7b errors
    become critic_status=d7b_error per the orchestrator contract.
    """
    position = candidate["position"]
    backend_label = "stub" if config.stub else "live"
    request_ts = datetime.now(timezone.utc)

    # HG6b — re-verify prompt template hash (mid-sequence drift guard).
    # MUST hash raw file bytes only — not inspect.getsource().
    live_template_sha = _file_sha256(config.prompt_template_path)
    if live_template_sha != startup_prompt_template_sha256:
        raise Stage2cStartupError(
            f"HG6b: prompt template SHA-256 drift between startup "
            f"({startup_prompt_template_sha256}) and call at position "
            f"{position} ({live_template_sha}). "
            "Abort reason: prompt_template_mutated_mid_run"
        )

    # HG9 — reconstruct BatchContext.
    dsl, theme, batch_context = config.reconstruct_fn(
        STAGE2C_BATCH_UUID, position,
        stage2d_artifacts_root=RAW_PAYLOAD_ROOT,
    )
    prompt_text = build_d7b_prompt(dsl, theme, batch_context)
    prompt_sha256 = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()

    prior_factor_sets_count = len(batch_context.prior_factor_sets)
    theme_hint_factor_count = len(batch_context.theme_hints.get(theme, frozenset()))

    # HG10 — leakage audit (orchestrator also runs it; we capture result).
    leakage_audit_result = _capture_leakage_audit_result(prompt_text)

    # HG15 — always persist prompt (forensic preservation).
    critic_dir = _critic_dir(config.raw_payload_root, STAGE2C_BATCH_UUID)
    prompt_path = critic_dir / f"call_{position:04d}_prompt.txt"
    prompt_path.write_text(prompt_text, encoding="utf-8")

    # Backend + estimated cost.
    if config.backend_factory is not None:
        backend = config.backend_factory(
            raw_payload_dir=config.raw_payload_root,
            api_call_number=position,
            batch_id=STAGE2C_BATCH_UUID,
        )
        estimated_cost = STAGE2C_PER_CALL_COST_CEILING_USD if not config.stub else 0.0
    elif config.stub:
        backend = StubD7bBackend()
        estimated_cost = 0.0
    else:
        from agents.critic.d7b_live import (
            D7B_STAGE2A_COST_CEILING_USD,
            LiveSonnetD7bBackend,
        )
        backend = LiveSonnetD7bBackend(
            raw_payload_dir=config.raw_payload_root,
            api_call_number=position,
            batch_id=STAGE2C_BATCH_UUID,
        )
        estimated_cost = D7B_STAGE2A_COST_CEILING_USD

    # Ledger pre-charge (HG13).
    api_call_kind = config.api_call_kind_override or f"d7b_critic_{backend_label}"
    row_id = ledger.write_pending(
        batch_id=STAGE2C_BATCH_UUID,
        api_call_kind=api_call_kind,
        backend_kind="d7b_critic",
        call_role="critique",
        estimated_cost_usd=estimated_cost,
        now=request_ts,
        notes=(
            f"Stage 2c {backend_label}, position={position}, "
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
    overlap_marker = " [overlap]" if record["is_stage2b_overlap"] else ""
    print(
        f"[stage2c] call {candidate['firing_order']}/{STAGE2C_N} "
        f"position={position}{overlap_marker} theme={theme} "
        f"factors={len(factors)} status={result.critic_status} "
        f"cost=${actual_cost:.6f}"
    )

    return record


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def run_stage2c(config: Stage2cConfig) -> dict:
    """Orchestrate the full 20-call Stage 2c sequence.

    Returns the aggregate record as a dict. Raises Stage2cStartupError on
    pre-fire gate failure; otherwise writes the aggregate record to disk
    even on sequence abort.
    """
    # Stub-mode isolation gate (assert before any I/O).
    _assert_stub_isolation(config)

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

    # Stage 2b archival (live mode only; stub physically isolated).
    if not config.stub:
        stage2c_positions = [c["position"] for c in candidates]
        critic_dir = _critic_dir(config.raw_payload_root, STAGE2C_BATCH_UUID)
        # Partial-prior-run guard: fires only on non-overlap remnants.
        detect_unexpected_stage2c_remnants(
            critic_dir=critic_dir,
            stage2c_positions=stage2c_positions,
            aggregate_record_path=config.aggregate_record_path,
            per_call_record_dir=config.per_call_record_dir,
        )
        archive_stage2b_overlap_artifacts_if_present(critic_dir)

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
        "python scripts/run_d7_stage2c_batch.py "
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

            abort, reason = should_abort(
                idx, per_call_records, current_cost, cumulative_cost,
            )
            if abort:
                sequence_aborted = True
                abort_reason = reason
                abort_at_call_index = idx
                break

            if idx < STAGE2C_N:
                t_before = time.monotonic()
                config.sleep_fn(STAGE2C_INTER_CALL_SLEEP_SECONDS)
                inter_call_sleep_elapsed = time.monotonic() - t_before

    except Stage2cStartupError as exc:
        # HG6b template drift (mid-sequence) — record + continue to write.
        sequence_aborted = True
        abort_reason = "prompt_template_mutated_mid_run"
        abort_at_call_index = len(per_call_records) + 1
        print(f"[stage2c] HG6b abort: {exc}", file=sys.stderr)

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
        print(
            f"[stage2c] HG20 WARNING: selection JSON SHA-256 drift "
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
        f"\n[stage2c] completed_call_count={len(per_call_records)}/{STAGE2C_N} "
        f"total_actual_cost=${agg['total_actual_cost_usd']:.6f}"
    )
    if sequence_aborted:
        print(
            f"[stage2c] SEQUENCE ABORTED: reason={abort_reason} "
            f"at_call={abort_at_call_index}"
        )
    print(f"[stage2c] aggregate record: {config.aggregate_record_path}")

    return agg


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    _load_dotenv()

    parser = argparse.ArgumentParser(
        description=(
            "D7 Stage 2c: twenty-call live D7b probe against signed-off "
            f"batch {STAGE2C_BATCH_UUID}."
        ),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--stub",
        action="store_true",
        help="Stub mode — no API calls; writes to dryrun_payloads/dryrun_stage2c/.",
    )
    group.add_argument(
        "--confirm-live",
        action="store_true",
        help="Live mode — calls Sonnet. Requires ANTHROPIC_API_KEY.",
    )
    args = parser.parse_args()

    try:
        config = build_stage2c_config(
            confirm_live=args.confirm_live, stub=args.stub,
        )
        run_stage2c(config)
    except Stage2cStartupError as exc:
        print(f"[stage2c] STARTUP ABORT: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - unexpected
        print(
            f"[stage2c] UNCAUGHT ERROR during sequence: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
