"""D7 Stage 2d — 200-record replay fire script (SKELETON).

First-stage scaffolding only. This version wires:

* ``Stage2dStartupError`` + ``Stage2dConfig`` dataclass
* CLI argument parsing (``--stub`` | ``--confirm-live``, mutually exclusive)
* Stub/live path routing per Lock 10 / Lock 10.2
* ``_assert_stub_isolation`` — stub must never resolve under ``raw_payloads/``
* Eleven ``_startup_gates`` (per design spec §6) in the ratified order
* A minimal ``run_stage2d`` that, once all startup gates pass, atomically
  writes a startup-only aggregate record sufficient to prove the shell runs

It deliberately does NOT implement the 200-record main loop,
``_run_one_call``, the synthetic pos-116 record, abort rules, or the full
53-key aggregate builder. Those land in the second-stage patch.

Parallel discipline to ``scripts/run_d7_stage2c_batch.py`` — duplication
is intentional per scope-lock §10.2. Do not refactor the two into a shared
module.

CONTRACT BOUNDARY: stub mode MUST NOT touch ``raw_payloads/`` or
``agents/spend_ledger.db`` under any circumstance. All stub I/O is
physically isolated under ``dryrun_payloads/dryrun_stage2d/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


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

# Aggregate schema identity
STAGE_LABEL: str = "d7_stage2d"
RECORD_VERSION: str = "1.0-skeleton"


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

    # Read-only inputs (identical for stub/live)
    selection_json_path: Path = STAGE2D_REPLAY_CANDIDATES_PATH
    expectations_path: Path = STAGE2D_EXPECTATIONS_PATH
    test_retest_path: Path = STAGE2D_TEST_RETEST_PATH
    deep_dive_path: Path = STAGE2D_DEEP_DIVE_PATH
    label_universe_path: Path = STAGE2D_LABEL_UNIVERSE_PATH
    prompt_template_path: Path = PROMPT_TEMPLATE_PATH
    self_check_script: Path = STAGE2D_SELF_CHECK_SCRIPT

    # Captured at gate time; default empty / None until filled
    prompt_template_sha: str | None = None
    replay_candidates_sha: str | None = None
    startup_audit: list[dict] = field(default_factory=list)

    # Injectables (keeps pure-function gate logic unit-testable)
    anchor_hash_fn: Callable[[str, str], str | None] = field(default=_git_show_sha256)
    selection_commit_ts_fn: Callable[[Path], int | None] = field(default=_git_commit_unixtime)
    expectations_commit_ts_fn: Callable[[Path], int | None] = field(default=_git_commit_unixtime)
    now_unixtime_fn: Callable[[], int] = field(default=_now_unixtime)
    now_iso_fn: Callable[[], str] = field(default=_iso_now)


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
            raw_payload_root=DRYRUN_ROOT / "raw_payloads",
            ledger_path=DRYRUN_ROOT / "ledger_dryrun.db",
            api_call_kind_override="d7b_critic_stub",
        )
    return Stage2dConfig(
        confirm_live=True,
        stub=False,
        mode="live",
        aggregate_record_path=(
            RAW_PAYLOAD_ROOT / STAGE2D_BATCH_DIR_NAME / "critic"
            / "stage2d_aggregate_record.json"
        ),
        raw_payload_root=RAW_PAYLOAD_ROOT,
        ledger_path=LEDGER_PATH,
        api_call_kind_override="d7b_critic_live",
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
        # Positive-containment check for the two path fields.
        if name in ("aggregate_record_path", "raw_payload_root"):
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
    """Gate 5 / HG3 — expectations file must exist and be non-empty."""
    p = config.expectations_path
    if not p.is_file():
        raise Stage2dStartupError(f"HG3: expectations file missing: {p}")
    if p.stat().st_size == 0:
        raise Stage2dStartupError(f"HG3: expectations file is empty: {p}")
    _audit_pass(config, "expectations_exists")


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
    _audit_pass(config, "expectations_committed",
                selection_commit_ts=sel_ts, expectations_commit_ts=exp_ts)


def _gate_prompt_template_sha(config: Stage2dConfig) -> None:
    """Gate 7 / HG6 — capture SHA-256 of the D7b prompt template at startup."""
    p = config.prompt_template_path
    if not p.is_file():
        raise Stage2dStartupError(f"HG6: prompt template missing: {p}")
    config.prompt_template_sha = _file_sha256(p)
    _audit_pass(config, "prompt_template_sha", sha256=config.prompt_template_sha)


def _gate_read_only_inputs(config: Stage2dConfig) -> None:
    """Gate 8 — §10.2a / §10.2b / §3.x / §4.x auxiliary artifacts must exist
    and parse as JSON. The fire script never derives these; it only reads."""
    for label, path in (
        ("test_retest_baselines", config.test_retest_path),
        ("deep_dive_candidates", config.deep_dive_path),
        ("label_universe_analysis", config.label_universe_path),
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
    _audit_pass(config, "read_only_inputs")


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
# run_stage2d (skeleton) — writes startup-only aggregate after gates pass
# ---------------------------------------------------------------------------


def run_stage2d(config: Stage2dConfig) -> dict:
    """First-stage scaffolding: gates + minimal aggregate write.

    Second-stage patch will add the 200-record main loop, ``_run_one_call``,
    synthetic pos 116 record, abort rules, and the full 53-key aggregate.
    """
    _assert_stub_isolation(config)

    fire_start = config.now_iso_fn()
    _startup_gates(config)
    startup_completed = config.now_iso_fn()

    aggregate = {
        "stage_label": STAGE_LABEL,
        "record_version": RECORD_VERSION,
        "batch_uuid": STAGE2D_BATCH_UUID,
        "fire_script_command": "run_d7_stage2d_batch.py",
        "mode": config.mode,
        "startup_gates_passed": True,
        "fire_timestamp_utc_start": fire_start,
        "startup_completed_at_utc": startup_completed,
        "skeleton_only": True,
        "replay_candidates_sha256": config.replay_candidates_sha,
        "prompt_template_sha256": config.prompt_template_sha,
        "startup_audit": config.startup_audit,
    }
    # Lock 11: write_completed_at MUST be appended as the literal LAST key.
    # Kept as a separate assignment (not a literal in the dict above) so
    # that any future field added upstream cannot accidentally dislodge it
    # from tail position.
    aggregate["write_completed_at"] = config.now_iso_fn()
    atomic_write_json(config.aggregate_record_path, aggregate)
    return aggregate


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="D7 Stage 2d 200-record fire script (skeleton stage)",
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

    print(
        f"[stage2d] skeleton aggregate written to "
        f"{config.aggregate_record_path} "
        f"(mode={config.mode}, gates={len(aggregate['startup_audit'])})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
