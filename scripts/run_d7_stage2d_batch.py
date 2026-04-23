"""D7 Stage 2d — 200-record replay fire script (Patch 2).

This patch adds the 200-position main loop on top of the Patch 1
skeleton:

* ``Stage2dStartupError`` + ``Stage2dConfig`` dataclass
* CLI argument parsing (``--stub`` | ``--confirm-live``, mutually exclusive)
* Stub/live path routing per Lock 10 / Lock 10.2
* ``_assert_stub_isolation`` — stub must never resolve under ``raw_payloads/``
* Eleven ``_startup_gates`` (design spec §6) in the ratified order
* Backend factory (``StubD7bBackend`` / ``LiveSonnetD7bBackend``)
* ``_synthesize_pos116_record`` — Lock 1.5 11-field core + Layer B envelope
* ``_run_one_call`` — BatchContext reconstruction, prompt build, leakage
  audit, ledger pre-charge, ``run_critic``, ledger finalize, per-call
  artifact writes
* 200-position main loop (199 live D7b + 1 synthetic pos 116)
* Minimal aggregate: ``completed_call_count``, three-counter
  ``critic_status_counts``, per-call records, trailing ``write_completed_at``

Patch 3 will add abort-rule evaluation (Lock 7 rules a-g), the full
53-key aggregate schema (stratum breakdown, HG20 input-drift guard,
Stage 2c archive SHAs, checkpoint log), and richer per-call record
expansion to the documented 31-key shape.

Parallel discipline to ``scripts/run_d7_stage2c_batch.py`` — duplication
is intentional per scope-lock §10.2. Do not refactor the two into a
shared module.

CONTRACT BOUNDARY: stub mode MUST NOT touch ``raw_payloads/`` or
``agents/spend_ledger.db`` under any circumstance. All stub I/O is
physically isolated under ``dryrun_payloads/dryrun_stage2d/``.

CONTRACT BOUNDARY: pos 116 produces a per-call record but no ledger
row and no prompt / response / critic_result artifacts (Lock 1.5 +
C.7 revised ruling). Patch 3 aggregate assertions codify this as the
"200 records vs 199 ledger rows" invariant (design spec §11.3).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agents.critic.d7b_backend import D7bBackend  # noqa: E402
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
# Locked constants — §3 of design spec
# ---------------------------------------------------------------------------

# Lock 1.6 / Lock 10.2 — source/call arithmetic
STAGE2D_SOURCE_N: int = 200
STAGE2D_LIVE_D7B_CALL_N: int = 199
STAGE2D_SKIPPED_POSITIONS: tuple[int, ...] = (116,)

# Lock 1.3 — batch identity (same UUID as Stage 2a/2b/2c)
STAGE2D_BATCH_UUID: str = "5cf76668-47d1-48d7-bd90-db06d31982ed"

# Lock 9 — cost envelope
STAGE2D_PER_CALL_COST_CEILING_USD: float = 0.08    # Rule (d)
STAGE2D_TOTAL_COST_CAP_USD: float = 8.00           # Rule (e)

# Lock 7 — error thresholds
STAGE2D_CONSECUTIVE_API_ERROR_THRESHOLD: int = 2   # Rule (a)
STAGE2D_ERROR_RATE_K_FLOOR: int = 3                # Rule (b) K
STAGE2D_ERROR_RATE_THRESHOLD: float = 0.40         # Rule (b) > 40%
STAGE2D_CONTENT_ERROR_ABS_THRESHOLD: int = 4       # Rule (c)

# Lock 7 / design spec §10.5 — abort-reason vocabulary. `abort_reason`
# field in the aggregate MUST be ``None`` or a member of this frozenset.
# Enforcement: aggregate builder assertion before write.
STAGE2D_ABORT_REASON_VOCAB: frozenset[str] = frozenset({
    # Inherited from Stage 2c Lock 7.
    "consecutive_api_errors",       # Rule (a), §7.1
    "error_rate_threshold",         # Rule (b), §7.2
    "content_level_threshold",      # Rule (c), §7.3
    "per_call_cost_exceeded",       # Rule (d), §7.4
    "cumulative_cost_cap_exceeded", # Rule (e), §7.5
    # Stage 2d-new per §7.7.
    "unexpected_skipped_source",    # Rule (g)
})

# Lock 10 — I/O paths
RAW_PAYLOAD_ROOT: Path = Path("raw_payloads")
LEDGER_PATH: Path = Path("agents/spend_ledger.db")
DRYRUN_ROOT: Path = Path("dryrun_payloads/dryrun_stage2d")
STAGE2D_BATCH_DIR_NAME: str = f"batch_{STAGE2D_BATCH_UUID}"

# Lock 10.5 — Stage 2c preservation
STAGE2C_ARCHIVE_RELATIVE: Path = Path("critic/stage2c_archive")

# HG-series anchors — Lock 11.5
STAGE2D_REPLAY_CANDIDATES_ANCHOR_COMMIT: str = "2771bef"
STAGE2D_REPLAY_CANDIDATES_REPO_PATH: str = "docs/d7_stage2d/replay_candidates.json"

STAGE2D_EXPECTATIONS_PATH: Path = Path("docs/d7_stage2d/stage2d_expectations.md")
STAGE2D_REPLAY_CANDIDATES_PATH: Path = Path("docs/d7_stage2d/replay_candidates.json")
STAGE2D_TEST_RETEST_PATH: Path = Path("docs/d7_stage2d/test_retest_baselines.json")
STAGE2D_DEEP_DIVE_PATH: Path = Path("docs/d7_stage2d/deep_dive_candidates.json")
STAGE2D_LABEL_UNIVERSE_PATH: Path = Path("docs/d7_stage2d/label_universe_analysis.json")
STAGE2D_SELF_CHECK_SCRIPT: Path = Path("scripts/stage2d_self_check.py")
PROMPT_TEMPLATE_PATH: Path = Path("agents/critic/d7b_prompt.py")

# Stage 2c archive — 20 positions × 3 files each (§6 Gate 11 detail)
STAGE2C_ARCHIVE_POSITIONS: tuple[int, ...] = (
    17, 22, 27, 32, 62, 72, 73, 74, 77, 83,
    97, 102, 107, 112, 117, 138, 143, 147, 152, 162,
)

# Stage 2b overlap positions — inherited from Stage 2c launch prompt §4.3.
# Used for is_stage2b_overlap compute-from-constant per §9.2 Advisor Precision 2.
STAGE2B_OVERLAP_POSITIONS: frozenset[int] = frozenset({17, 73, 74, 97, 138})

# Inter-call pacing. Live mode matches Stage 2c (5s) for tier-1 rate-limit
# parity. Stub mode uses 0s because no API is hit — no operational
# reason to pace. Both values reported in the aggregate record.
STAGE2D_LIVE_INTER_CALL_SLEEP_SECONDS: float = 5.0
STAGE2D_STUB_INTER_CALL_SLEEP_SECONDS: float = 0.0

# Aggregate schema identity
STAGE_LABEL: str = "d7_stage2d"
RECORD_VERSION: str = "1.0-patch3c"

# Reconciliation threshold — Stage 2c parity (structural_variant_risk >= 0.5
# classified as HIGH; < 0.5 as LOW; exactly 0.5 tie-broken to HIGH).
STRUCTURAL_VARIANT_RISK_HIGH_THRESHOLD: float = 0.5


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class Stage2dStartupError(RuntimeError):
    """Startup-gate failure; maps to exit code 1, no aggregate written."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_dotenv(path: Path | None = None) -> None:
    """Load ``.env`` into ``os.environ`` (stdlib-only, parity with 2c)."""
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
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_show_sha256(commit: str, repo_path: str) -> str | None:
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


def _git_commit_unixtime(path: Path) -> int | None:
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


def _now_unixtime() -> int:
    return int(time.time())


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _unix_to_iso(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, ensure_ascii=False)
    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, path)


def _audit_pass(config: "Stage2dConfig", gate_name: str, **extra: object) -> None:
    """Record a gate pass in ``config.startup_audit``.

    Schema: every entry has ``gate`` + ``status="pass"``. Gates that need to
    record extra detail (e.g. subprocess stdout tail) pass ``extra`` kwargs.
    """
    entry: dict[str, object] = {"gate": gate_name, "status": "pass"}
    entry.update(extra)
    config.startup_audit.append(entry)


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------


@dataclass
class Stage2dConfig:
    """Paths, mode, and captured startup state for a Stage 2d run."""

    confirm_live: bool
    stub: bool
    mode: str                                        # "stub" | "live"

    aggregate_record_path: Path
    raw_payload_root: Path
    ledger_path: Path
    api_call_kind_override: str
    startup_audit_path: Path

    # Read-only inputs (identical for stub/live)
    selection_json_path: Path = STAGE2D_REPLAY_CANDIDATES_PATH
    expectations_path: Path = STAGE2D_EXPECTATIONS_PATH
    test_retest_path: Path = STAGE2D_TEST_RETEST_PATH
    deep_dive_path: Path = STAGE2D_DEEP_DIVE_PATH
    label_universe_path: Path = STAGE2D_LABEL_UNIVERSE_PATH
    prompt_template_path: Path = PROMPT_TEMPLATE_PATH
    self_check_script: Path = STAGE2D_SELF_CHECK_SCRIPT

    # Inter-call pacing — see §15 item 6 of design spec. Live = 5s (parity
    # with Stage 2c), stub = 0s (no API round-trip to pace).
    inter_call_sleep_seconds: float = STAGE2D_LIVE_INTER_CALL_SLEEP_SECONDS

    # Captured at gate time; default empty / None until filled. The six
    # SHA / commit-timestamp fields below feed §10.1 carry-forward and
    # §10.2 aggregate keys. selection_tier / selection_warnings_count are
    # intentionally absent — Stage 2d selection pipeline does not produce
    # them, so the corresponding aggregate rows are deferred to Patch 3d.
    prompt_template_sha: str | None = None
    replay_candidates_sha: str | None = None
    expectations_file_sha256: str | None = None
    selection_commit_timestamp_utc: str | None = None
    expectations_commit_timestamp_utc: str | None = None
    deep_dive_candidates_sha256: str | None = None
    test_retest_baselines_sha256: str | None = None
    label_universe_analysis_sha256: str | None = None
    startup_audit: list[dict] = field(default_factory=list)
    startup_completed_at_utc: str | None = None

    # Injectables (keeps pure-function gate logic unit-testable)
    anchor_hash_fn: Callable[[str, str], str | None] = field(default=_git_show_sha256)
    selection_commit_ts_fn: Callable[[Path], int | None] = field(default=_git_commit_unixtime)
    expectations_commit_ts_fn: Callable[[Path], int | None] = field(default=_git_commit_unixtime)
    now_unixtime_fn: Callable[[], int] = field(default=_now_unixtime)
    now_iso_fn: Callable[[], str] = field(default=_iso_now)
    sleep_fn: Callable[[float], None] = field(default=time.sleep)
    reconstruct_fn: Callable[..., Any] = field(
        default=reconstruct_batch_context_at_position
    )
    backend_factory: Callable[..., D7bBackend] | None = None


def build_stage2d_config(confirm_live: bool, stub: bool) -> Stage2dConfig:
    """Build a production config with stub/live path routing."""
    if confirm_live and stub:
        raise ValueError("--confirm-live and --stub are mutually exclusive")
    if not (confirm_live or stub):
        raise ValueError("one of --confirm-live or --stub is required")

    if stub:
        return Stage2dConfig(
            confirm_live=False,
            stub=True,
            mode="stub",
            aggregate_record_path=DRYRUN_ROOT / "stage2d_aggregate_record.json",
            startup_audit_path=DRYRUN_ROOT / "stage2d_startup_audit.json",
            raw_payload_root=DRYRUN_ROOT / "raw_payloads",
            ledger_path=DRYRUN_ROOT / "ledger_dryrun.db",
            api_call_kind_override="d7b_critic_stub",
            inter_call_sleep_seconds=STAGE2D_STUB_INTER_CALL_SLEEP_SECONDS,
        )
    return Stage2dConfig(
        confirm_live=True,
        stub=False,
        mode="live",
        aggregate_record_path=(
            RAW_PAYLOAD_ROOT / STAGE2D_BATCH_DIR_NAME / "critic"
            / "stage2d_aggregate_record.json"
        ),
        startup_audit_path=(
            RAW_PAYLOAD_ROOT / STAGE2D_BATCH_DIR_NAME / "critic"
            / "stage2d_startup_audit.json"
        ),
        raw_payload_root=RAW_PAYLOAD_ROOT,
        ledger_path=LEDGER_PATH,
        api_call_kind_override="d7b_critic_live",
        inter_call_sleep_seconds=STAGE2D_LIVE_INTER_CALL_SLEEP_SECONDS,
    )


# ---------------------------------------------------------------------------
# Stub isolation contract
# ---------------------------------------------------------------------------


def _resolve(p: Path) -> Path:
    return p.resolve() if p.is_absolute() else (Path.cwd() / p).resolve()


def _is_under(child: Path, parent: Path) -> bool:
    """True iff ``child`` is at or below ``parent`` (both resolved)."""
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _assert_stub_isolation(config: Stage2dConfig) -> None:
    """In stub mode, no write path may resolve under ``raw_payloads/`` and
    the ledger MUST NOT point at the production ``agents/spend_ledger.db``.

    Uses ``Path.relative_to`` semantics (not string containment) so that
    symlinks, trailing-slash variants, and sibling names that happen to
    share a prefix cannot spoof the predicate.
    """
    if not config.stub:
        return

    forbidden_raw = _resolve(Path("raw_payloads"))
    dryrun_root = _resolve(DRYRUN_ROOT)
    prod_ledger = _resolve(LEDGER_PATH)

    to_check = (
        ("aggregate_record_path", config.aggregate_record_path),
        ("startup_audit_path", config.startup_audit_path),
        ("raw_payload_root", config.raw_payload_root),
        ("ledger_path", config.ledger_path),
    )
    for name, p in to_check:
        resolved = _resolve(p)
        # A stub path under raw_payloads/ is always a violation — even if
        # it also lies under dryrun_payloads/ (which would indicate a
        # misconfigured symlink).
        if _is_under(resolved, forbidden_raw):
            raise Stage2dStartupError(
                f"stub isolation: {name}={p} resolves under raw_payloads/ "
                f"(resolved={resolved}). Stub mode must stay under "
                f"{DRYRUN_ROOT}."
            )
        # Positive-containment check for the three path fields.
        if name in ("aggregate_record_path", "startup_audit_path", "raw_payload_root"):
            if not _is_under(resolved, dryrun_root):
                raise Stage2dStartupError(
                    f"stub isolation: {name}={p} (resolved={resolved}) "
                    f"is not under {dryrun_root}."
                )
        if name == "ledger_path" and resolved == prod_ledger:
            raise Stage2dStartupError(
                f"stub isolation: ledger_path={p} resolves to production "
                "ledger agents/spend_ledger.db. Stub mode must use "
                "dryrun_payloads/dryrun_stage2d/ledger_dryrun.db."
            )


# ---------------------------------------------------------------------------
# Startup gates — 11 checks in ratified order (design spec §6)
# ---------------------------------------------------------------------------


def _gate_self_check_subprocess(config: Stage2dConfig) -> None:
    """Gate 1 — C.4 ruling: run stage2d_self_check.py, fail on any non-zero."""
    result = subprocess.run(
        [sys.executable, str(config.self_check_script)],
        capture_output=True, text=True, timeout=120,
        cwd=str(_REPO_ROOT),
    )
    if result.returncode != 0:
        raise Stage2dStartupError(
            f"HG_SELF_CHECK: stage2d_self_check.py exited {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    _audit_pass(
        config,
        "self_check_subprocess",
        exit_code=0,
        stdout_tail=result.stdout[-4000:],
    )


def _gate_replay_candidates_exists_and_parses(config: Stage2dConfig) -> None:
    """Gate 2 / HG1 — file present and parses as JSON with a ``candidates`` list."""
    p = config.selection_json_path
    if not p.is_file():
        raise Stage2dStartupError(f"HG1: replay candidates file missing: {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Stage2dStartupError(f"HG1: replay candidates JSON parse failed: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("candidates"), list):
        raise Stage2dStartupError(
            "HG1: replay candidates JSON must have top-level 'candidates' list"
        )
    _audit_pass(config, "replay_candidates_exists_and_parses")


def _gate_replay_candidates_sha_anchor(config: Stage2dConfig) -> None:
    """Gate 3 / HG2 — on-disk SHA must equal the anchor-commit SHA."""
    on_disk = _file_sha256(config.selection_json_path)
    anchor = config.anchor_hash_fn(
        STAGE2D_REPLAY_CANDIDATES_ANCHOR_COMMIT,
        STAGE2D_REPLAY_CANDIDATES_REPO_PATH,
    )
    if anchor is None:
        raise Stage2dStartupError(
            f"HG2: cannot resolve anchor commit "
            f"{STAGE2D_REPLAY_CANDIDATES_ANCHOR_COMMIT!r} for "
            f"{STAGE2D_REPLAY_CANDIDATES_REPO_PATH!r}"
        )
    if on_disk != anchor:
        raise Stage2dStartupError(
            f"HG2: replay_candidates.json drift. on_disk={on_disk} "
            f"anchor={anchor} (commit {STAGE2D_REPLAY_CANDIDATES_ANCHOR_COMMIT})"
        )
    config.replay_candidates_sha = on_disk
    _audit_pass(
        config,
        "replay_candidates_sha_anchor",
        anchor_commit=STAGE2D_REPLAY_CANDIDATES_ANCHOR_COMMIT,
        sha256=on_disk,
    )


def _gate_replay_candidates_invariants(config: Stage2dConfig) -> None:
    """Gate 4 — §1.3 / §1.4 / §1.5 invariants on the 200-candidate list."""
    data = json.loads(config.selection_json_path.read_text(encoding="utf-8"))
    candidates = data["candidates"]
    if len(candidates) != STAGE2D_SOURCE_N:
        raise Stage2dStartupError(
            f"HG1b: expected {STAGE2D_SOURCE_N} candidates, got {len(candidates)}"
        )
    # Firing order must equal 1..N, positions sorted ascending.
    for i, c in enumerate(candidates, start=1):
        if c.get("firing_order") != i:
            raise Stage2dStartupError(
                f"HG1b: candidate #{i} firing_order={c.get('firing_order')!r}; expected {i}"
            )
    # Pos 116 must be the single skipped source with the Lock 1.5 markers.
    skipped = [c for c in candidates if c.get("is_skipped_source")]
    if [c["position"] for c in skipped] != list(STAGE2D_SKIPPED_POSITIONS):
        raise Stage2dStartupError(
            f"HG1b: skipped positions must be {list(STAGE2D_SKIPPED_POSITIONS)}; "
            f"got {[c['position'] for c in skipped]}"
        )
    pos116 = skipped[0]
    if pos116.get("lifecycle_state") != "rejected_complexity":
        raise Stage2dStartupError(
            f"HG1b: pos 116 lifecycle_state must be 'rejected_complexity'; "
            f"got {pos116.get('lifecycle_state')!r}"
        )
    # Non-skipped count must match LIVE_D7B_CALL_N
    live_n = sum(1 for c in candidates if not c.get("is_skipped_source"))
    if live_n != STAGE2D_LIVE_D7B_CALL_N:
        raise Stage2dStartupError(
            f"HG1b: non-skipped candidate count {live_n}; expected "
            f"{STAGE2D_LIVE_D7B_CALL_N}"
        )
    _audit_pass(config, "replay_candidates_invariants", source_n=STAGE2D_SOURCE_N,
                live_n=STAGE2D_LIVE_D7B_CALL_N)


def _gate_expectations_exists(config: Stage2dConfig) -> None:
    """Gate 5 / HG3 — expectations file must exist, be non-empty, and have
    its SHA-256 captured for the aggregate record (§10.1 row 10)."""
    p = config.expectations_path
    if not p.is_file():
        raise Stage2dStartupError(f"HG3: expectations file missing: {p}")
    if p.stat().st_size == 0:
        raise Stage2dStartupError(f"HG3: expectations file is empty: {p}")
    config.expectations_file_sha256 = _file_sha256(p)
    _audit_pass(
        config, "expectations_exists",
        sha256=config.expectations_file_sha256,
    )


def _gate_expectations_committed(config: Stage2dConfig) -> None:
    """Gate 6 / HG5 — selection and expectations both committed, with
    ``selection_commit < expectations_commit < wall_clock``.

    Scope lock §11.5 ordering chain is strict (``replay_candidates <
    scope_lock_v2 < expectations``), so selection-vs-expectations is
    strict ``<``, not ``<=``.
    """
    sel_ts = config.selection_commit_ts_fn(config.selection_json_path)
    exp_ts = config.expectations_commit_ts_fn(config.expectations_path)
    now_ts = config.now_unixtime_fn()

    if sel_ts is None:
        raise Stage2dStartupError(
            "HG5: selection JSON is not committed to git (no commit timestamp)"
        )
    if exp_ts is None:
        raise Stage2dStartupError(
            "HG5/HG3: expectations file is not committed to git. "
            "Commit before fire."
        )
    if not (sel_ts < exp_ts):
        raise Stage2dStartupError(
            f"HG5: selection commit ({sel_ts}) must be strictly < "
            f"expectations commit ({exp_ts}) per scope lock §11.5"
        )
    if not (exp_ts < now_ts):
        raise Stage2dStartupError(
            f"HG5: expectations commit ({exp_ts}) must be strictly < wall-clock ({now_ts})"
        )
    config.selection_commit_timestamp_utc = _unix_to_iso(sel_ts)
    config.expectations_commit_timestamp_utc = _unix_to_iso(exp_ts)
    _audit_pass(
        config, "expectations_committed",
        selection_commit_ts=sel_ts,
        expectations_commit_ts=exp_ts,
        selection_commit_timestamp_utc=config.selection_commit_timestamp_utc,
        expectations_commit_timestamp_utc=config.expectations_commit_timestamp_utc,
    )


def _gate_prompt_template_sha(config: Stage2dConfig) -> None:
    """Gate 7 / HG6 — capture SHA-256 of the D7b prompt template at startup."""
    p = config.prompt_template_path
    if not p.is_file():
        raise Stage2dStartupError(f"HG6: prompt template missing: {p}")
    config.prompt_template_sha = _file_sha256(p)
    _audit_pass(config, "prompt_template_sha", sha256=config.prompt_template_sha)


def _gate_read_only_inputs(config: Stage2dConfig) -> None:
    """Gate 8 — §10.2a / §10.2b / §3.x / §4.x auxiliary artifacts must exist
    and parse as JSON. The fire script never derives these; it only reads.

    SHA-256 of each auxiliary input is captured onto the Config so the
    aggregate record (§10.2 rows 712-714) can carry them without a
    separate re-hash pass.
    """
    captured: dict[str, str] = {}
    for label, path, attr in (
        ("test_retest_baselines", config.test_retest_path,
            "test_retest_baselines_sha256"),
        ("deep_dive_candidates", config.deep_dive_path,
            "deep_dive_candidates_sha256"),
        ("label_universe_analysis", config.label_universe_path,
            "label_universe_analysis_sha256"),
    ):
        if not path.is_file():
            raise Stage2dStartupError(
                f"HG_RO_INPUTS: auxiliary input {label} missing at {path}"
            )
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise Stage2dStartupError(
                f"HG_RO_INPUTS: auxiliary input {label} at {path} is not valid JSON: {exc}"
            )
        sha = _file_sha256(path)
        setattr(config, attr, sha)
        captured[attr] = sha
    _audit_pass(config, "read_only_inputs", **captured)


def _gate_aggregate_record_absent(config: Stage2dConfig) -> None:
    """Gate 9 / HG8 — the target aggregate must not pre-exist (Lock 11 invariant)."""
    if config.aggregate_record_path.exists():
        raise Stage2dStartupError(
            f"HG8: aggregate record already exists at "
            f"{config.aggregate_record_path}. Refusing to overwrite."
        )
    _audit_pass(config, "aggregate_record_absent")


def _gate_partial_prior_run(config: Stage2dConfig) -> None:
    """Gate 10 — live only. Hard-fail on evidence of a crashed prior
    Stage 2d fire.

    NOTE (Round 1 review): Stage 2d per-call files will land under
    ``raw_payloads/batch_<UUID>/critic/`` using the same
    ``call_NNNN_prompt.txt`` / ``_response.json`` / ``_critic_result.json``
    convention as Stage 2c — meaning the critic dir already contains
    Stage 2c's 20 per-call files plus the ``stage2c_archive/`` subdir. A
    correct partial-prior-run predicate therefore needs a cross-reference
    against the Stage 2c archive position set, which belongs in the
    second-stage (main-loop) patch where the per-call filename
    convention is locked.

    Until then, this gate flags only the one unambiguous marker of a
    crashed mid-write: a leftover atomic-write sidecar
    ``stage2d_aggregate_record.json.tmp``. That file is never
    legitimately present at startup (gate 9 ensures no aggregate,
    and atomic-write cleans up on success). Full per-call
    partial-state detection is deferred.
    """
    if config.mode != "live":
        _audit_pass(config, "partial_prior_run", skipped_reason="live_only_gate")
        return
    critic_dir = config.raw_payload_root / STAGE2D_BATCH_DIR_NAME / "critic"
    if critic_dir.is_dir():
        tmp_sidecar = critic_dir / "stage2d_aggregate_record.json.tmp"
        if tmp_sidecar.exists():
            raise Stage2dStartupError(
                f"HG_PARTIAL: aggregate tmp sidecar present at "
                f"{tmp_sidecar} — prior Stage 2d fire crashed mid-write. "
                "Adjudicate before re-firing."
            )
    _audit_pass(
        config,
        "partial_prior_run",
        note="placeholder_check_refine_at_main_loop_authoring",
    )


def _gate_stage2c_archival(config: Stage2dConfig) -> None:
    """Gate 11 / §10.5 — live only. Stage 2c archive directory must hold all
    20 positions × 3 files each (optional traceback files are accepted)."""
    if config.mode != "live":
        _audit_pass(config, "stage2c_archival", skipped_reason="live_only_gate")
        return
    archive_dir = config.raw_payload_root / STAGE2D_BATCH_DIR_NAME / STAGE2C_ARCHIVE_RELATIVE
    if not archive_dir.is_dir():
        raise Stage2dStartupError(
            f"HG_STAGE2C_ARCHIVE: Lock 10.5 preservation contract failed. "
            f"Expected directory missing: {archive_dir}"
        )
    expected: set[str] = set()
    for pos in STAGE2C_ARCHIVE_POSITIONS:
        for suffix in ("prompt.txt", "response.json", "critic_result.json"):
            expected.add(f"call_{pos:04d}_{suffix}")
    present = {p.name for p in archive_dir.iterdir() if p.is_file()}
    missing = expected - present
    if missing:
        raise Stage2dStartupError(
            "HG_STAGE2C_ARCHIVE: preservation directory missing files: "
            f"{sorted(missing)}"
        )
    _audit_pass(config, "stage2c_archival", archive_file_count=len(present))


def _startup_gates(config: Stage2dConfig) -> None:
    """Run all startup gates in the ratified order. First failure raises.

    Each gate owns its own ``startup_audit`` entry via ``_audit_pass``; this
    orchestrator is a pure sequencer with no sweep/backfill logic.
    """
    gates: tuple[Callable[[Stage2dConfig], None], ...] = (
        _gate_self_check_subprocess,
        _gate_replay_candidates_exists_and_parses,
        _gate_replay_candidates_sha_anchor,
        _gate_replay_candidates_invariants,
        _gate_expectations_exists,
        _gate_expectations_committed,
        _gate_prompt_template_sha,
        _gate_read_only_inputs,
        _gate_aggregate_record_absent,
        _gate_partial_prior_run,
        _gate_stage2c_archival,
    )
    for fn in gates:
        fn(config)


# ---------------------------------------------------------------------------
# Per-call helpers
# ---------------------------------------------------------------------------


def _critic_dir(raw_payload_root: Path, batch_uuid: str) -> Path:
    """Directory that holds ``call_NNNN_*`` artifacts for one batch.

    In stub mode ``raw_payload_root`` is ``DRYRUN_ROOT/raw_payloads``; in
    live mode it is the production ``raw_payloads``. Either way, artifacts
    land under ``<root>/batch_<uuid>/critic/``.
    """
    return raw_payload_root / f"batch_{batch_uuid}" / "critic"


def _not_reached_scan_result() -> dict:
    return {
        "status": "not_reached",
        "hits": None,
        "reason": "parse failed before scan completion",
    }


def _capture_leakage_audit_result(prompt_text: str) -> dict:
    """Leakage audit result dict — matches Stage 2c shape."""
    leakage_detail = run_leakage_audit(prompt_text)
    return {
        "status": "pass" if leakage_detail is None else "fail",
        "violations": [] if leakage_detail is None else [leakage_detail],
        "protected_terms_checked_count": len(D7B_PROTECTED_TERMS),
    }


def _classify_d7b_error(
    critic_error_signature: str | None, actual_cost_usd: float,
) -> str | None:
    """Coarse bucketing for abort-rule category (matches Stage 2c §7).

    Patch 2 uses a conservative default: any non-None signature with
    observed cost > 0 is content-level (model responded, we rejected the
    content); zero cost with a signature is api-level (no response billed).
    Full classifier tuning is Patch 3 work.
    """
    if critic_error_signature is None:
        return None
    if actual_cost_usd > 0:
        return "content_level"
    return "api_level"


def _build_backend(config: Stage2dConfig, position: int) -> D7bBackend:
    """Construct the D7b backend for one call.

    Stub mode returns the deterministic ``StubD7bBackend``. Live mode
    defers import of ``LiveSonnetD7bBackend`` to call time so that
    ``--stub`` runs don't require an Anthropic client to import cleanly.
    A unit-testable ``backend_factory`` override is honoured first.

    Stub vs live artifact asymmetry (Stage 2c parallel discipline):
    ``StubD7bBackend`` returns ``raw_response_path=None`` and writes no
    ``response.json`` or ``traceback.txt``. ``LiveSonnetD7bBackend``
    writes ``response.json`` on success and ``traceback.txt`` on error
    from within ``invoke()`` itself. The caller uses ``.exists()``
    probes to reflect this — identical pattern to Stage 2c fire script.
    """
    if config.backend_factory is not None:
        return config.backend_factory(
            raw_payload_dir=config.raw_payload_root,
            api_call_number=position,
            batch_id=STAGE2D_BATCH_UUID,
        )
    if config.stub:
        return StubD7bBackend()
    from agents.critic.d7b_live import LiveSonnetD7bBackend

    return LiveSonnetD7bBackend(
        raw_payload_dir=config.raw_payload_root,
        api_call_number=position,
        batch_id=STAGE2D_BATCH_UUID,
    )


def _estimated_cost_for_mode(stub: bool) -> float:
    """Pre-flight ledger estimate.

    Stub = 0.0 (no API call). Live = ``D7B_STAGE2A_COST_CEILING_USD``
    ($0.05) per Advisor Precision 1 / design spec §11.1. NOT the rule-(d)
    abort threshold of $0.08.
    """
    if stub:
        return 0.0
    from agents.critic.d7b_live import D7B_STAGE2A_COST_CEILING_USD

    return D7B_STAGE2A_COST_CEILING_USD


def _synthesize_pos116_record(
    *,
    candidate: dict,
    call_index: int,
    iso_now: str,
) -> dict:
    """Synthetic per-call record for position 116 (Lock 1.5 + Layer B).

    Lock 1.5 mandates 11 top-level fields with verbatim values for the
    sole skipped source. Layer B adds 6 envelope fields required for
    aggregate-builder parity across all 200 positions — per the design
    spec §11.0 Layer B governing principle, these may not imply a D7b
    request, response, prompt, ledger event, or critic computation.

    No ledger row is written for pos 116 (C.7 revised ruling); no
    prompt / response / critic_result artifacts either. The record
    exists solely in the aggregate's ``per_call_records[115]`` slot.
    """
    if candidate["position"] != 116:
        raise AssertionError(
            f"_synthesize_pos116_record called for position "
            f"{candidate['position']}; expected 116"
        )

    # Layer A — Lock 1.5 mandated (11 fields, verbatim values).
    lock_15_fields: dict[str, object] = {
        "call_index": call_index,
        "position": 116,
        "critic_status": "skipped_source_invalid",
        "d7b_call_attempted": False,
        "d7b_error_category": "source_invalid",
        "source_lifecycle_state": "rejected_complexity",
        "source_valid_status": "invalid_schema",
        "actual_cost_usd": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "skip_reason": (
            "source candidate is not pending_backtest and "
            "cannot be replayed by BatchContext reconstruction"
        ),
    }

    # Layer B — Stage 2d fire-script envelope (6 fields; per §9.2).
    envelope_fields: dict[str, object] = {
        "stratum_id": candidate.get("stratum_id"),
        "record_written_at_utc": iso_now,
        "firing_order": candidate["firing_order"],
        "is_stage2b_overlap": 116 in STAGE2B_OVERLAP_POSITIONS,  # → False
        "is_deep_dive_candidate": False,  # L12-05 deterministic exclusion
        "test_retest_tier": None,         # pos 116 not in Stage 2c set
    }

    return {**lock_15_fields, **envelope_fields}


def _build_normal_per_call_record(
    *,
    candidate: dict,
    call_index: int,
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
    record_written_at_utc: str,
) -> dict:
    """Assemble the per-call record for a non-skipped (live D7b) position.

    Mirrors Stage 2c's ``build_per_call_record`` shape with Stage 2d
    candidate schema adaptations (``universe_b_label`` → pre-registered
    label; ``stratum_id`` / ``is_deep_dive_candidate`` / ``test_retest_tier``
    envelope fields added). Patch 3 will expand this into the full 31-key
    shape specified in design spec §9.1; Patch 2 carries the minimum
    fields required to support the 3-counter ``critic_status_counts``
    and future abort-rule evaluation.
    """
    result_dict = result.to_dict()
    wall_clock_s = (response_ts - request_ts).total_seconds()

    scan_results = (
        result.d7b_scan_results
        if isinstance(result.d7b_scan_results, dict)
        else None
    )
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

    d7b_error_category: str | None = None
    if result.critic_status == "d7b_error":
        d7b_error_category = _classify_d7b_error(
            result.critic_error_signature, actual_cost_usd,
        )

    position = candidate["position"]
    is_overlap = position in STAGE2B_OVERLAP_POSITIONS

    return {
        # --- Stage 2a-derived live-call fields ---
        "request_timestamp_utc": request_ts.isoformat().replace("+00:00", "Z"),
        "response_timestamp_utc": response_ts.isoformat().replace("+00:00", "Z"),
        "wall_clock_seconds": round(wall_clock_s, 3),
        "retry_count": result.d7b_retry_count,
        "d7b_mode": result.d7b_mode,
        "critic_result": result_dict,
        "ledger_row": {
            "row_id": ledger_row_id,
            "batch_id": STAGE2D_BATCH_UUID,
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

        # --- Candidate metadata (Stage 2d schema) ---
        "firing_order": candidate["firing_order"],
        "candidate_position": position,
        "candidate_theme": candidate.get("theme"),
        "pre_registered_label": candidate.get("universe_b_label"),
        "prior_factor_sets_count": prior_factor_sets_count,
        "theme_hint_factor_count": theme_hint_factor_count,
        "prompt_chars": len(prompt_text),
        "prompt_sha256": prompt_sha256,
        "call_index": call_index,
        "call_index_in_sequence": candidate["firing_order"],
        "inter_call_sleep_elapsed_seconds": round(
            inter_call_sleep_elapsed_seconds, 3,
        ),

        # --- Stage 2c inheritance ---
        "is_stage2b_overlap": is_overlap,

        # --- Stage 2d envelope additions (parallel to synthetic pos 116) ---
        "stratum_id": candidate.get("stratum_id"),
        "is_deep_dive_candidate": False,   # Patch 3 wires from deep_dive_candidates
        "test_retest_tier": None,          # Patch 3 wires from test_retest_baselines
        "record_written_at_utc": record_written_at_utc,

        # --- Abort-rule mirrors (single source of truth per Stage 2c) ---
        "critic_status": result.critic_status,
        "critic_error_signature": result.critic_error_signature,
        "actual_cost_usd": actual_cost_usd,
        "d7b_error_category": d7b_error_category,
    }


def _run_one_call(
    *,
    config: Stage2dConfig,
    candidate: dict,
    call_index: int,
    ledger: BudgetLedger,
    inter_call_sleep_elapsed_seconds: float,
    startup_prompt_template_sha256: str,
) -> dict:
    """Fire one non-skipped candidate and return its per-call record.

    Raises ``Stage2dStartupError`` on mid-run prompt-template SHA drift
    (HG6b). All other D7b failures land as ``critic_status="d7b_error"``
    in the returned record — they do not raise.
    """
    position = candidate["position"]
    backend_label = "stub" if config.stub else "live"
    request_ts = datetime.now(timezone.utc)

    # HG6b — mid-sequence prompt-template drift guard.
    live_template_sha = _file_sha256(config.prompt_template_path)
    if live_template_sha != startup_prompt_template_sha256:
        raise Stage2dStartupError(
            f"HG6b: prompt template SHA-256 drift between startup "
            f"({startup_prompt_template_sha256}) and call at position "
            f"{position} ({live_template_sha}). "
            "Abort reason: prompt_template_mutated_mid_run"
        )

    # BatchContext reconstruction from signed-off D6 artifacts.
    dsl, theme, batch_context = config.reconstruct_fn(
        STAGE2D_BATCH_UUID, position,
        stage2d_artifacts_root=RAW_PAYLOAD_ROOT,
    )
    prompt_text = build_d7b_prompt(dsl, theme, batch_context)
    prompt_sha256 = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()

    prior_factor_sets_count = len(batch_context.prior_factor_sets)
    theme_hint_factor_count = len(batch_context.theme_hints.get(theme, frozenset()))

    leakage_audit_result = _capture_leakage_audit_result(prompt_text)

    critic_dir = _critic_dir(config.raw_payload_root, STAGE2D_BATCH_UUID)
    critic_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = critic_dir / f"call_{position:04d}_prompt.txt"
    prompt_path.write_text(prompt_text, encoding="utf-8")

    backend = _build_backend(config, position)
    estimated_cost = _estimated_cost_for_mode(config.stub)

    row_id = ledger.write_pending(
        batch_id=STAGE2D_BATCH_UUID,
        api_call_kind=config.api_call_kind_override,
        backend_kind="d7b_critic",
        call_role="critique",
        estimated_cost_usd=estimated_cost,
        now=request_ts,
        notes=(
            f"Stage 2d {backend_label}, position={position}, "
            f"firing_order={candidate['firing_order']}"
        ),
    )

    # Deterministic ledger-cleanup path: if anything between write_pending
    # and finalize raises, mark the row crashed so it never lingers in
    # ``pending`` status. The pre-charge still counts (CLAUDE.md rule —
    # "crashed batches are not resumed"), but audit telemetry is correct.
    ledger_finalized = False
    try:
        result = run_critic(dsl, theme, batch_context, backend)
        response_ts = datetime.now(timezone.utc)

        actual_cost = float(result.d7b_cost_actual_usd or 0.0)

        ledger.finalize(
            row_id,
            actual_cost_usd=actual_cost,
            now=response_ts,
            input_tokens=result.d7b_input_tokens,
            output_tokens=result.d7b_output_tokens,
        )
        ledger_finalized = True

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

        record_written_at = config.now_iso_fn()
        record = _build_normal_per_call_record(
            candidate=candidate,
            call_index=call_index,
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
            record_written_at_utc=record_written_at,
        )
        return record
    except BaseException:
        if not ledger_finalized:
            try:
                ledger.mark_crashed(
                    row_id,
                    now=datetime.now(timezone.utc),
                    notes=(
                        f"Stage 2d uncaught exception at position {position} "
                        f"(call_index={call_index}); see traceback on caller"
                    ),
                )
            except Exception:
                # Mark-crashed best-effort; never mask the original exception.
                pass
        raise


def _critic_status_counts(per_call_records: list[dict]) -> dict[str, int]:
    """Three-counter status per design spec §10.2.

    Keys are always present (zero when absent) so downstream assertions
    can rely on a fixed-shape dict. Any status value outside the allowed
    enum raises ``AssertionError`` — a typo or new status must be
    surfaced loudly rather than silently folded into ``ok``.
    """
    counts = {"ok": 0, "d7b_error": 0, "skipped_source_invalid": 0}
    for rec in per_call_records:
        status = rec.get("critic_status")
        if status == "ok":
            counts["ok"] += 1
        elif status == "d7b_error":
            counts["d7b_error"] += 1
        elif status == "skipped_source_invalid":
            counts["skipped_source_invalid"] += 1
        else:
            raise AssertionError(
                f"unknown critic_status in per_call_record: {status!r} "
                f"(allowed: 'ok', 'd7b_error', 'skipped_source_invalid')"
            )
    return counts


# ---------------------------------------------------------------------------
# Lock 7 abort evaluation — design spec §7
# ---------------------------------------------------------------------------


def should_abort(
    idx: int,
    records: list[dict],
    per_call_cost: float,
    cumulative_cost: float,
) -> tuple[bool, str | None]:
    """Evaluate Lock 7 abort rules against the sequence so far.

    Rule ordering per C.3 ruling: **g → a → b → c → d → e**. First
    match returns. See design spec §7 for the deterministic pseudocode
    this function implements verbatim.

    Bookkeeping semantics:
      - Rule (g) looks at the just-appended record only.
      - Rules (a), (b), (c) operate on the ``non_skipped`` subsequence
        per §7.8 — skipped records are filtered out of both tail walks
        and denominators (C.1, C.2).
      - Rule (d) is evaluated on the just-completed call's cost; synthetic
        pos 116 has ``actual_cost_usd=0.0`` and cannot trigger.
      - Rule (e) is evaluated on cumulative ledger-written cost; synthetic
        records contribute 0 (no ledger row per C.7).

    Returns ``(True, reason)`` on abort, ``(False, None)`` otherwise.
    The ``reason`` string is guaranteed to be a member of
    :data:`STAGE2D_ABORT_REASON_VOCAB`.

    Enum validation: every record's ``critic_status`` is checked against
    the 3-value enum ``{'ok', 'd7b_error', 'skipped_source_invalid'}``.
    An unknown value raises ``AssertionError`` rather than silently
    distorting rules (a)-(c) — same discipline as
    :func:`_critic_status_counts`.
    """
    _ALLOWED_STATUSES = ("ok", "d7b_error", "skipped_source_invalid")
    for r in records:
        status = r.get("critic_status")
        if status not in _ALLOWED_STATUSES:
            raise AssertionError(
                f"should_abort: unknown critic_status {status!r} "
                f"(allowed: {_ALLOWED_STATUSES!r})"
            )

    last = records[-1]

    # Rule (g) — §7.7 — unexpected skipped_source at unexpected position.
    # Normal records carry ``candidate_position`` (Stage 2c parity); synthetic
    # pos 116 carries ``position`` (Lock 1.5). Read with inline fallback so
    # the abort path tolerates both schemas without a normalization helper.
    if last.get("critic_status") == "skipped_source_invalid":
        last_pos = last.get("position", last.get("candidate_position"))
        if last_pos is None:
            raise AssertionError(
                "should_abort: skipped record missing both 'position' and "
                "'candidate_position' keys"
            )
        if int(last_pos) not in STAGE2D_SKIPPED_POSITIONS:
            return True, "unexpected_skipped_source"

    # Non-skipped subsequence used by rules (a), (b), (c) per §7.8.
    non_skipped = [
        r for r in records
        if r.get("critic_status") != "skipped_source_invalid"
    ]

    # Rule (a) — §7.1 — N consecutive api_level errors (non-skipped subsequence).
    if len(non_skipped) >= STAGE2D_CONSECUTIVE_API_ERROR_THRESHOLD:
        tail = non_skipped[-STAGE2D_CONSECUTIVE_API_ERROR_THRESHOLD:]
        if all(
            r.get("critic_status") == "d7b_error"
            and r.get("d7b_error_category") == "api_level"
            for r in tail
        ):
            return True, "consecutive_api_errors"

    # Rule (b) — §7.2 — error rate > threshold at K >= floor (non-skipped).
    K = len(non_skipped)
    if K >= STAGE2D_ERROR_RATE_K_FLOOR:
        errors = sum(
            1 for r in non_skipped
            if r.get("critic_status") == "d7b_error"
        )
        if (errors / K) > STAGE2D_ERROR_RATE_THRESHOLD:
            return True, "error_rate_threshold"

    # Rule (c) — §7.3 — content_level errors >= absolute threshold (non-skipped).
    content_errors = sum(
        1 for r in non_skipped
        if r.get("critic_status") == "d7b_error"
        and r.get("d7b_error_category") == "content_level"
    )
    if content_errors >= STAGE2D_CONTENT_ERROR_ABS_THRESHOLD:
        return True, "content_level_threshold"

    # Rule (d) — §7.4 — per-call cost ceiling.
    if per_call_cost > STAGE2D_PER_CALL_COST_CEILING_USD:
        return True, "per_call_cost_exceeded"

    # Rule (e) — §7.5 — cumulative cost cap.
    if cumulative_cost > STAGE2D_TOTAL_COST_CAP_USD:
        return True, "cumulative_cost_cap_exceeded"

    return False, None


# ---------------------------------------------------------------------------
# Aggregate record helpers — ported from Stage 2c with Stage 2d adaptations
# per ChatGPT Q1 ruling (universe_b_label label source; keep Stage 2c
# bucket shape). Pos 116 contributions follow design spec §10.3.
#
# Parallel-discipline note: duplicated rather than imported so Stage 2c
# and Stage 2d aggregates can diverge independently (scope-lock §10.2).
# ---------------------------------------------------------------------------


def _is_skipped_record(rec: dict) -> bool:
    """True iff the per-call record is the synthetic pos 116 slot.

    Inline position read follows the same fallback rule as ``should_abort``
    rule (g) — normal records carry ``candidate_position``, synthetic pos
    116 carries ``position`` (Lock 1.5).
    """
    if rec.get("critic_status") == "skipped_source_invalid":
        return True
    pos = rec.get("position", rec.get("candidate_position"))
    return pos is not None and int(pos) in STAGE2D_SKIPPED_POSITIONS


def _extract_d7a_scores(result_dict: dict | None) -> dict[str, float] | None:
    if not result_dict:
        return None
    return result_dict.get("d7a_rule_scores")


def _extract_d7b_scores(result_dict: dict | None) -> dict[str, float] | None:
    if not result_dict:
        return None
    return result_dict.get("d7b_llm_scores")


def is_consistent_with_label(
    pre_registered_label: str | None,
    structural_variant_risk: float | None,
) -> bool | None:
    """Mechanical reconciliation of D7b's structural_variant_risk to label.

    Returns True / False / None (None on d7b_error, neutral label, or
    absent label — pos 116 falls through as None per §10.3).
    Exactly 0.5 classified as ``>= 0.5`` (HIGH). Ported from Stage 2c
    verbatim.
    """
    if structural_variant_risk is None:
        return None
    if pre_registered_label == "divergence_expected":
        return structural_variant_risk < STRUCTURAL_VARIANT_RISK_HIGH_THRESHOLD
    if pre_registered_label == "agreement_expected":
        return structural_variant_risk >= STRUCTURAL_VARIANT_RISK_HIGH_THRESHOLD
    return None


def reconciliation_rationale(
    pre_registered_label: str | None,
    structural_variant_risk: float | None,
) -> str:
    """Human-readable rationale embedded in the aggregate record.

    Ported from Stage 2c. The pos 116 synthetic slot does not reach this
    function; its rationale string is set to ``"skipped_source_invalid"``
    directly in :func:`build_aggregate_record` per §10.3.
    """
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


def _compute_theme_counts(candidates: list[dict]) -> dict[str, int]:
    """Theme histogram over all 200 replay candidates (including pos 116)."""
    counts: dict[str, int] = {}
    for c in candidates:
        theme = c.get("theme", "unknown")
        counts[theme] = counts.get(theme, 0) + 1
    return counts


def _compute_label_counts(candidates: list[dict]) -> dict[str, int]:
    """Pre-registered label histogram using Stage 2d ``universe_b_label``.

    Buckets are fixed ``{agreement_expected, divergence_expected, neutral}``
    to preserve Stage 2c consumer shape. Per ChatGPT Round 2 ruling, the
    skipped-source record (pos 116) carries ``universe_b_label = None``
    and is intentionally NOT folded into ``neutral``: the null bucket
    falls through the ``if label in counts`` filter so the sum is 199
    (not 200). Pos 116's absence is implicit in the 3-key shape.
    """
    counts: dict[str, int] = {
        "agreement_expected": 0,
        "divergence_expected": 0,
        "neutral": 0,
    }
    for c in candidates:
        label = c.get("universe_b_label")
        if label in counts:
            counts[label] += 1
    return counts


def _svr_by_label(per_call_records: list[dict]) -> dict[str, dict]:
    """Partition completed structural_variant_risk scores by label.

    Position read uses the ``rec.get("position", rec.get("candidate_position"))``
    inline fallback so the synthetic pos 116 record — even though it
    cannot contribute (no critic_result, no pre_registered_label) —
    cannot raise a KeyError if it somehow reaches this function.

    Only non-skipped records with a non-None SVR contribute.
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
        critic_result = rec.get("critic_result")
        d7b = _extract_d7b_scores(critic_result)
        if not d7b:
            continue
        svr = d7b.get("structural_variant_risk")
        if svr is None:
            continue
        pos = rec.get("position", rec.get("candidate_position"))
        if pos is None:
            continue
        buckets[label].append((int(pos), float(svr)))

    out: dict[str, dict] = {}
    for label, pairs in buckets.items():
        pairs.sort(key=lambda t: t[0])
        out[label] = {
            "completed_count": len(pairs),
            "positions": [p for p, _ in pairs],
            "svr_values": [round(v, 6) for _, v in pairs],
        }
    return out


def _compute_stratum_breakdown(
    per_call_records: list[dict],
    deep_dive_data: dict | None,
) -> dict[str, dict]:
    """Stratum-level breakdown over the 20 deep-dive candidates only.

    Per ChatGPT Q2 ruling, coverage is deep-dive positions only (not all
    200). Each bucket reports ``count`` (deep-dive records observed),
    ``error_count`` (critic_status == 'd7b_error'), and ``error_rate``.
    Skipped records (pos 116) are excluded from both numerator and
    denominator. Stratum id is string-keyed for JSON stability.
    """
    out: dict[str, dict] = {}
    if not deep_dive_data:
        return out

    dd_candidates = deep_dive_data.get("candidates") or []

    # Index per-call records by position for O(1) lookup.
    by_pos: dict[int, dict] = {}
    for rec in per_call_records:
        pos = rec.get("position", rec.get("candidate_position"))
        if pos is None:
            continue
        by_pos[int(pos)] = rec

    for dd in dd_candidates:
        stratum = dd.get("primary_stratum_id")
        position = dd.get("position")
        if stratum is None or position is None:
            continue
        rec = by_pos.get(int(position))
        if rec is None:
            continue
        if _is_skipped_record(rec):
            continue  # pos 116 cannot land in deep-dive set; defensive.
        key = str(stratum)
        bucket = out.setdefault(
            key, {"count": 0, "error_count": 0, "error_rate": 0.0},
        )
        bucket["count"] += 1
        if rec.get("critic_status") == "d7b_error":
            bucket["error_count"] += 1

    for bucket in out.values():
        n = bucket["count"]
        bucket["error_rate"] = (
            round(bucket["error_count"] / n, 6) if n > 0 else 0.0
        )
    return out


def build_aggregate_record(
    *,
    config: "Stage2dConfig",
    candidates: list[dict],
    per_call_records: list[dict],
    fire_timestamp_utc_start: str,
    fire_timestamp_utc_end: str,
    sequence_aborted: bool,
    abort_reason: str | None,
    abort_at_call_index: int | None,
    total_wall_clock_seconds: float,
    fire_script_command: str,
    deep_dive_data: dict | None,
) -> dict:
    """Assemble the 49-key Stage 2d aggregate (no ``write_completed_at``).

    Field coverage is the 3c target — 41 Stage 2c carry-forward keys
    (``selection_tier`` and ``selection_warnings_count`` deferred to
    Patch 3d because Stage 2d's selection pipeline produces no source
    for them on disk) plus 8 Stage 2d additions (``critic_status_counts``,
    ``stratum_breakdown``, 3 auxiliary-input SHAs, and the 3 explicit
    self-documenting counts). Patch 3d will add HG20 conditionals,
    ``checkpoint_log``, and ``stage2c_archive_sha256_by_file``.
    """
    # ----- Ordered-list fields (§10.1 rows 25-33) ---------------------------
    reasoning_lengths: list[int | None] = []
    actual_costs: list[float] = []
    estimated_costs: list[float] = []
    input_tokens_seq: list[int] = []
    output_tokens_seq: list[int] = []
    wall_clocks: list[float | None] = []
    statuses: list[str] = []
    error_cats: list[str | None] = []
    is_overlap_seq: list[bool] = []

    # ----- Per-call indexed dict fields (§10.1 rows 34-36) ------------------
    d7a_by_call: dict[str, dict | None] = {}
    d7b_by_call: dict[str, dict | None] = {}
    reconciliation: dict[str, dict] = {}

    for rec in per_call_records:
        skipped = _is_skipped_record(rec)
        # firing_order is 1..200 for all 200 records (Lock 1.4 invariant);
        # keying the by-call dicts by firing_order preserves Stage 2c shape.
        idx_key = str(rec["firing_order"])

        if skipped:
            # §10.3 — pos 116 contributions, verbatim.
            reasoning_lengths.append(None)
            actual_costs.append(0.0)
            estimated_costs.append(0.0)
            input_tokens_seq.append(0)
            output_tokens_seq.append(0)
            wall_clocks.append(None)
            statuses.append("skipped_source_invalid")
            error_cats.append("source_invalid")
            is_overlap_seq.append(False)
            d7a_by_call[idx_key] = None
            d7b_by_call[idx_key] = None
            reconciliation[idx_key] = {
                "pre_registered_label": None,
                "d7b_structural_variant_risk": None,
                "observed_consistent_with_label": None,
                "rationale": "skipped_source_invalid",
            }
            continue

        critic_result = rec.get("critic_result")
        d7b_scores = _extract_d7b_scores(critic_result)
        reasoning_text = ""
        if critic_result is not None:
            reasoning_text = critic_result.get("d7b_reasoning") or ""
        reasoning_lengths.append(len(reasoning_text))

        actual_costs.append(float(rec.get("actual_cost_usd") or 0.0))
        est = rec.get("cost", {}).get("estimated_usd", 0.0)
        estimated_costs.append(float(est or 0.0))
        input_tokens_seq.append(int(
            (critic_result or {}).get("d7b_input_tokens") or 0
        ))
        output_tokens_seq.append(int(
            (critic_result or {}).get("d7b_output_tokens") or 0
        ))
        wall_clocks.append(rec.get("wall_clock_seconds"))
        statuses.append(rec["critic_status"])
        error_cats.append(rec.get("d7b_error_category"))
        is_overlap_seq.append(bool(rec.get("is_stage2b_overlap")))

        d7a_by_call[idx_key] = _extract_d7a_scores(critic_result)
        d7b_by_call[idx_key] = d7b_scores
        svr = d7b_scores.get("structural_variant_risk") if d7b_scores else None
        label = rec.get("pre_registered_label")
        reconciliation[idx_key] = {
            "pre_registered_label": label,
            "d7b_structural_variant_risk": svr,
            "observed_consistent_with_label": is_consistent_with_label(label, svr),
            "rationale": reconciliation_rationale(label, svr),
        }

    # ----- Sum scalars (§10.1 rows 21-24) -----------------------------------
    total_actual = sum(float(v or 0) for v in actual_costs)
    total_estimated = sum(float(v or 0) for v in estimated_costs)
    total_input = sum(int(v or 0) for v in input_tokens_seq)
    total_output = sum(int(v or 0) for v in output_tokens_seq)

    # ----- Sequence aggregates (§10.1 rows 37-42) ---------------------------
    theme_counts = _compute_theme_counts(candidates)
    label_counts = _compute_label_counts(candidates)
    overlap_positions_sorted = sorted(STAGE2B_OVERLAP_POSITIONS)
    overlap_completed = sum(
        1 for rec in per_call_records
        if not _is_skipped_record(rec)
        and int(rec.get("candidate_position", -1)) in STAGE2B_OVERLAP_POSITIONS
    )
    svr_by_label = _svr_by_label(per_call_records)

    # ----- Stage 2d additions (§10.2 rows subset — 8 of 10) -----------------
    stratum_breakdown = _compute_stratum_breakdown(per_call_records, deep_dive_data)

    return {
        # --- §10.1 rows 1-9: identity + anchors ---------------------------
        "stage_label": STAGE_LABEL,
        "record_version": RECORD_VERSION,
        "batch_uuid": STAGE2D_BATCH_UUID,
        "fire_script_command": fire_script_command,
        "fire_timestamp_utc_start": fire_timestamp_utc_start,
        "fire_timestamp_utc_end": fire_timestamp_utc_end,
        # write_completed_at is appended LAST by run_stage2d (Lock 11).
        "d7b_prompt_template_sha256": config.prompt_template_sha,
        "selection_json_sha256": config.replay_candidates_sha,

        # --- §10.1 rows 10-12: provenance anchors -------------------------
        "expectations_file_sha256": config.expectations_file_sha256,
        "selection_commit_timestamp_utc": config.selection_commit_timestamp_utc,
        "expectations_commit_timestamp_utc": config.expectations_commit_timestamp_utc,

        # NOTE: §10.1 rows 13-14 (`selection_tier`, `selection_warnings_count`)
        # are intentionally omitted from 3c. Stage 2d's selection pipeline
        # does not produce a selection-tier artifact on disk (verified in
        # 3c Round 2 rulings); these two rows are deferred to Patch 3d.
        # Do NOT hardcode them here — that would invent data.

        # --- §10.1 rows 15-20: sequence summary ---------------------------
        "sequence_aborted": sequence_aborted,
        "abort_reason": abort_reason,
        "abort_at_call_index": abort_at_call_index,
        "completed_call_count": len(per_call_records),
        "total_wall_clock_seconds": round(total_wall_clock_seconds, 3),
        "inter_call_sleep_seconds": config.inter_call_sleep_seconds,

        # --- §10.1 rows 21-24: sum scalars --------------------------------
        "total_actual_cost_usd": round(total_actual, 6),
        "total_estimated_cost_usd": round(total_estimated, 6),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,

        # --- §10.1 rows 25-33: ordered lists (pos 116 per §10.3) ----------
        "reasoning_lengths_in_call_order": reasoning_lengths,
        "actual_costs_in_call_order": [round(v, 6) for v in actual_costs],
        "estimated_costs_in_call_order": [round(v, 6) for v in estimated_costs],
        "input_tokens_in_call_order": input_tokens_seq,
        "output_tokens_in_call_order": output_tokens_seq,
        "wall_clock_seconds_in_call_order": wall_clocks,
        "critic_statuses_in_call_order": statuses,
        "d7b_error_categories_in_call_order": error_cats,
        "is_stage2b_overlap_in_call_order": is_overlap_seq,

        # --- §10.1 rows 34-36: by-call dicts (pos 116 per §10.3) ----------
        "d7a_scores_by_call": d7a_by_call,
        "d7b_scores_by_call": d7b_by_call,
        "agreement_divergence_reconciliation_by_call": reconciliation,

        # --- §10.1 rows 37-42: sequence-wide aggregates -------------------
        "theme_counts_in_sequence": theme_counts,
        "label_counts_in_sequence": label_counts,
        "stage2b_overlap_count": len(STAGE2B_OVERLAP_POSITIONS),
        "stage2b_overlap_positions": overlap_positions_sorted,
        "stage2b_overlap_completed_count": overlap_completed,
        "svr_by_label": svr_by_label,

        # --- §10.2: Stage 2d additions (8 of 10; 2 deferred to 3d) --------
        "critic_status_counts": _critic_status_counts(per_call_records),
        "stratum_breakdown": stratum_breakdown,
        "deep_dive_candidates_sha256": config.deep_dive_candidates_sha256,
        "test_retest_baselines_sha256": config.test_retest_baselines_sha256,
        "label_universe_analysis_sha256": config.label_universe_analysis_sha256,
        "stage2d_skipped_positions": list(STAGE2D_SKIPPED_POSITIONS),
        "stage2d_live_d7b_call_n": STAGE2D_LIVE_D7B_CALL_N,
        "stage2d_source_n": STAGE2D_SOURCE_N,

        # --- §10.1 row 43: per-call records -------------------------------
        "per_call_records": per_call_records,
    }


# ---------------------------------------------------------------------------
# Startup-audit artifact — §12.1 mandates separate file, not embedded in
# aggregate. Written once after startup gates complete successfully.
# ---------------------------------------------------------------------------


def _capture_environment_fields() -> dict[str, str | None]:
    """Capture fire-time environment per design spec §13.3.

    Three fields: ``git_head``, ``python_version``, ``os_platform``.
    ``git_head`` is best-effort: missing ``git`` binary or timeout resolves
    to ``None`` rather than aborting startup_audit write.
    """
    git_head: str | None = None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(_REPO_ROOT),
        )
        if result.returncode == 0:
            git_head = result.stdout.strip() or None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        git_head = None
    return {
        "git_head": git_head,
        "python_version": sys.version.split()[0],
        "os_platform": platform.platform(),
    }


def _write_startup_audit_artifact(config: Stage2dConfig) -> None:
    """Write ``stage2d_startup_audit.json`` alongside the aggregate.

    Contains mode, completion timestamp, §13.3 environment fields, and
    the verbatim gate-by-gate audit list. Kept separate from the
    aggregate per design spec §12.1 so the aggregate stays focused on
    sequence outcomes.

    Patch 3c fix-forward: envelope expanded from 6 to 9 top-level keys
    to satisfy §13.3 verbatim ("git HEAD, python version, OS"). Field
    ordering matches the reviewer-ratified target:
    stage_label, batch_uuid, mode, startup_gates_passed,
    startup_completed_at_utc, git_head, python_version, os_platform,
    startup_audit.
    """
    env_fields = _capture_environment_fields()
    payload = {
        "stage_label": STAGE_LABEL,
        "batch_uuid": STAGE2D_BATCH_UUID,
        "mode": config.mode,
        "startup_gates_passed": True,
        "startup_completed_at_utc": config.startup_completed_at_utc,
        "git_head": env_fields["git_head"],
        "python_version": env_fields["python_version"],
        "os_platform": env_fields["os_platform"],
        "startup_audit": config.startup_audit,
    }
    atomic_write_json(config.startup_audit_path, payload)


# ---------------------------------------------------------------------------
# run_stage2d — Patch 3c: 49-key aggregate + separate startup_audit artifact
# ---------------------------------------------------------------------------


def run_stage2d(config: Stage2dConfig) -> dict:
    """Patch 2+3a: startup gates + 200-record main loop + Lock 7 aborts.

    Sequence invariants (stub-run acceptance):
      - ``completed_call_count``: ``STAGE2D_SOURCE_N`` on normal
        completion; ``abort_at_call_index`` on abort.
      - ``per_call_records`` length equals ``completed_call_count``.
      - ``critic_status_counts``: 3-counter with explicit enum validation.
      - ``write_completed_at``: always the final aggregate key.
      - ``abort_reason``: ``None`` or a member of
        :data:`STAGE2D_ABORT_REASON_VOCAB` (§10.5 enforcement).

    Lock 7 rules a-g fire per design spec §7 pseudocode with ordering
    g → a → b → c → d → e (C.3 ruling). On first match the loop breaks
    and aggregate reflects truncated state.

    Patch 3c will expand to the full 53-key schema (stratum breakdown,
    HG20 input-drift guard, Stage 2c archive SHAs, checkpoint log,
    ordered-list fields).
    """
    _assert_stub_isolation(config)

    fire_start = config.now_iso_fn()
    _startup_gates(config)
    config.startup_completed_at_utc = config.now_iso_fn()
    _write_startup_audit_artifact(config)

    fire_script_command = (
        "python scripts/run_d7_stage2d_batch.py "
        + ("--confirm-live" if config.confirm_live else "--stub")
    )

    # Load the 200-candidate sequence already validated by Gate 4.
    selection = json.loads(
        config.selection_json_path.read_text(encoding="utf-8")
    )
    candidates: list[dict] = selection["candidates"]
    assert len(candidates) == STAGE2D_SOURCE_N, "gate 4 invariant drift"

    # Deep-dive data loaded once; used by stratum_breakdown builder.
    # Gate 8 already validated the JSON parse; a second read keeps the
    # aggregate builder pure (no Config dependency on file contents).
    deep_dive_data = json.loads(
        config.deep_dive_path.read_text(encoding="utf-8")
    )

    ledger = BudgetLedger(config.ledger_path)
    per_call_records: list[dict] = []
    inter_call_sleep_elapsed = 0.0
    cumulative_cost_usd = 0.0
    sequence_aborted = False
    abort_reason: str | None = None
    abort_at_call_index: int | None = None
    t0 = time.monotonic()

    for idx, candidate in enumerate(candidates, start=1):
        position = candidate["position"]
        if position in STAGE2D_SKIPPED_POSITIONS:
            record = _synthesize_pos116_record(
                candidate=candidate,
                call_index=idx,
                iso_now=config.now_iso_fn(),
            )
        else:
            record = _run_one_call(
                config=config,
                candidate=candidate,
                call_index=idx,
                ledger=ledger,
                inter_call_sleep_elapsed_seconds=inter_call_sleep_elapsed,
                startup_prompt_template_sha256=config.prompt_template_sha,
            )
        per_call_records.append(record)

        # Track cost: synthetic records contribute 0 per C.7 ruling.
        per_call_cost = float(record.get("actual_cost_usd", 0.0) or 0.0)
        cumulative_cost_usd += per_call_cost

        # Lock 7 abort evaluation — mid-loop, after append, before sleep.
        aborted, reason = should_abort(
            idx, per_call_records, per_call_cost, cumulative_cost_usd
        )
        if aborted:
            sequence_aborted = True
            abort_reason = reason
            abort_at_call_index = idx
            break

        if idx < STAGE2D_SOURCE_N:
            t_before = time.monotonic()
            config.sleep_fn(config.inter_call_sleep_seconds)
            inter_call_sleep_elapsed = time.monotonic() - t_before

    total_wall_clock_seconds = time.monotonic() - t0
    fire_timestamp_utc_end = config.now_iso_fn()

    aggregate = build_aggregate_record(
        config=config,
        candidates=candidates,
        per_call_records=per_call_records,
        fire_timestamp_utc_start=fire_start,
        fire_timestamp_utc_end=fire_timestamp_utc_end,
        sequence_aborted=sequence_aborted,
        abort_reason=abort_reason,
        abort_at_call_index=abort_at_call_index,
        total_wall_clock_seconds=total_wall_clock_seconds,
        fire_script_command=fire_script_command,
        deep_dive_data=deep_dive_data,
    )

    # §10.5 vocabulary enforcement: abort_reason is None or a member
    # of STAGE2D_ABORT_REASON_VOCAB. Any other value is a programmer
    # error — surface it before writing an unreadable aggregate.
    if aggregate["abort_reason"] is not None:
        if aggregate["abort_reason"] not in STAGE2D_ABORT_REASON_VOCAB:
            raise AssertionError(
                f"abort_reason {aggregate['abort_reason']!r} not in "
                f"STAGE2D_ABORT_REASON_VOCAB {sorted(STAGE2D_ABORT_REASON_VOCAB)!r}"
            )

    # 3c assertion — the aggregate builder returns 48 keys (41 Stage 2c
    # carry-forward minus 2 deferred rows {selection_tier,
    # selection_warnings_count} plus 8 Stage 2d additions minus the
    # LAST-written ``write_completed_at`` tail key). After the tail
    # assignment below the aggregate has 49 keys, the 3c target. HG20
    # conditionals and Patch-3d additions will push this to 53 later.
    assert len(aggregate) == 48, (
        f"aggregate pre-tail key count drift: got {len(aggregate)}, "
        f"expected 48 (3c target minus write_completed_at). Keys: "
        f"{sorted(aggregate.keys())}"
    )

    # Lock 11 invariant: ``write_completed_at`` is appended LAST. Keep the
    # assignment separate from the dict literal so that any future field
    # added upstream cannot dislodge it from tail position.
    aggregate["write_completed_at"] = config.now_iso_fn()
    assert len(aggregate) == 49, (
        f"aggregate final key count drift: got {len(aggregate)}, "
        f"expected 49 (3c target). Keys: {sorted(aggregate.keys())}"
    )
    atomic_write_json(config.aggregate_record_path, aggregate)
    return aggregate


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="D7 Stage 2d 200-record fire script (Patch 2: main loop)",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--stub", action="store_true",
        help="Stub mode: isolated to dryrun_payloads/dryrun_stage2d/",
    )
    group.add_argument(
        "--confirm-live", action="store_true",
        help="Live mode: writes to raw_payloads/ and touches the production ledger",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    _load_dotenv()
    args = _build_arg_parser().parse_args(argv)
    try:
        config = build_stage2d_config(
            confirm_live=args.confirm_live,
            stub=args.stub,
        )
    except ValueError as exc:
        print(f"[stage2d] config error: {exc}", file=sys.stderr)
        return 1

    try:
        aggregate = run_stage2d(config)
    except Stage2dStartupError as exc:
        # Exit code 1: startup-gate failure. No aggregate written.
        print(f"[stage2d] startup gate failed: {exc}", file=sys.stderr)
        return 1
    except Exception:  # noqa: BLE001 — deliberate catch-all per design spec §2
        # Exit code 2: uncaught mid-fire exception. Distinct from 1 so that
        # post-fire triage can separate "startup contract violated" (1)
        # from "startup passed but the fire itself crashed" (2). The second
        # class implies a partial mid-run state that MUST be adjudicated
        # before re-firing.
        print("[stage2d] uncaught exception during fire:", file=sys.stderr)
        traceback.print_exc()
        return 2

    status_counts = aggregate["critic_status_counts"]
    print(
        f"[stage2d] aggregate written to {config.aggregate_record_path} "
        f"(mode={config.mode}, gates={len(config.startup_audit)}, "
        f"completed={aggregate['completed_call_count']}, "
        f"ok={status_counts['ok']}, d7b_error={status_counts['d7b_error']}, "
        f"skipped={status_counts['skipped_source_invalid']}, "
        f"audit={config.startup_audit_path})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
