"""Shared lineage contract — producer + consumer guards across attestation domains.

This module is the single source of truth for corrected-engine artifact
lineage enforcement (Section RS of
docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md). Producers
(scripts/run_phase2c_batch_walkforward.py, scripts/run_phase1b_corrected.py,
scripts/run_phase2c_evaluation_gate.py, and any future corrected-engine
artifact producer) AND downstream consumers (DSR/PBO/CPCV/MDS/
strategy-shortlist tooling) must use these helpers to enforce the
hard prohibition: pre-correction artifacts must not be produced or
consumed.

Two attestation domains, kept semantically separate:

1. Walk-forward artifacts (wf_semantics='corrected_test_boundary_v1'):
   produced by run_walk_forward and its downstream batch runners.
   Validated by check_wf_semantics_or_raise.

2. Single-run holdout artifacts (evaluation_semantics='single_run_holdout_v1'):
   produced by single-run evaluations like the PHASE2C_6 regime holdout
   gate. Validated by check_evaluation_semantics_or_raise.

The two helpers do not cross-validate — calling check_wf_semantics_or_raise
on a single-run holdout artifact rejects it (no wf_semantics field), and
vice-versa. This is intentional and prevents accidental cross-domain
consumption.

The producer-side helper (enforce_corrected_engine_lineage) refuses
to run on a HEAD that does not contain the corrected engine commit.
It is shared by both attestation domains because the engine fix is a
prerequisite for either kind of corrected artifact.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CORRECTED_WF_ENGINE_COMMIT = "eb1c87f"
WF_SEMANTICS_TAG = "corrected_test_boundary_v1"

# Single-run holdout artifact tags (PHASE2C_6 evaluation gate work).
# Separate from WF_SEMANTICS_TAG because single-run holdout artifacts
# are NOT walk-forward artifacts — claiming the WF tag for them would
# dilute the precision of the corrected-WF attestation. See
# docs/phase2c/PHASE2C_6_EVALUATION_GATE_PLAN.md §3 lineage discipline.
EVALUATION_SEMANTICS_TAG = "single_run_holdout_v1"
ENGINE_CORRECTED_LINEAGE_TAG = "wf-corrected-v1"

# Anchor git subprocess calls to the repo root containing this file, NOT
# to the caller's CWD. Without this anchor the producer guard false-rejects
# legitimate corrected runs invoked from /tmp, notebooks, CI wrappers, or
# any absolute-path launch (Codex Task 7.6 re-review finding,
# 2026-04-26).
_REPO_ROOT = Path(__file__).resolve().parents[1]


def enforce_corrected_engine_lineage() -> str:
    """Producer-side: refuse to run if HEAD doesn't contain the corrected commit.

    Returns the current HEAD SHA on success. Raises SystemExit (clear
    error message) on failure. Used by scripts that PRODUCE
    walk_forward_summary.json artifacts.

    Hard-fails (sys.exit) because callers are scripts at startup —
    aborting is the appropriate response.

    Both git subprocess calls run with cwd anchored to the repo root
    that contains this file, so the guard is independent of the
    caller's CWD. The ancestry check uses the resolved head_sha (not
    the symbolic "HEAD") so the SHA stamped into the summary metadata
    is the same SHA whose ancestry was verified — eliminating any
    HEAD-shift race between the two subprocess calls.
    """
    try:
        head_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, cwd=_REPO_ROOT
        ).strip()
    except subprocess.CalledProcessError as exc:
        sys.exit(
            f"ERROR: cannot resolve HEAD SHA (not in a git repo?): {exc}"
        )

    rc = subprocess.call(
        ["git", "merge-base", "--is-ancestor",
         CORRECTED_WF_ENGINE_COMMIT, head_sha],
        cwd=_REPO_ROOT,
    )
    if rc != 0:
        sys.exit(
            f"ERROR: this script requires the corrected WF engine "
            f"(commit {CORRECTED_WF_ENGINE_COMMIT} or descendant). "
            f"Current HEAD ({head_sha}) is not descended from "
            f"{CORRECTED_WF_ENGINE_COMMIT}. Refusing to run to prevent "
            f"production of pre-correction WF artifacts. See "
            f"docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md Section RS."
        )
    return head_sha


def check_wf_semantics_or_raise(
    summary: dict,
    *,
    artifact_path: str | Path | None = None,
) -> None:
    """Consumer-side: validate a WF summary is safe for RS-sensitive consumption.

    Checks both `wf_semantics == WF_SEMANTICS_TAG` and
    `corrected_wf_semantics_commit == CORRECTED_WF_ENGINE_COMMIT`.
    Distinguishes missing-field from wrong-value in the error message.
    Does NOT gate on `lineage_check` (auditor breadcrumb only, not
    load-bearing).

    Raises ValueError (not SystemExit) so consumers in notebooks /
    test harnesses / batch processors can decide how to handle the
    violation.

    Args:
        summary: The WF summary dict (typically loaded from
            walk_forward_summary.json).
        artifact_path: Optional path to the source JSON file, included
            in the error message for diagnostics. Pass when the caller
            loaded the dict from a known file path.

    Raises:
        ValueError: If wf_semantics is missing, wrong, or if
            corrected_wf_semantics_commit is missing or wrong.
    """
    where = f" at {artifact_path}" if artifact_path else ""
    actual_tag = summary.get("wf_semantics")
    if actual_tag is None:
        raise ValueError(
            f"Unsafe WF artifact{where}: missing 'wf_semantics' field "
            f"(pre-Task-7.6 artifact?). Expected {WF_SEMANTICS_TAG!r}. "
            f"Refusing per docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md "
            f"Section RS."
        )
    if actual_tag != WF_SEMANTICS_TAG:
        raise ValueError(
            f"Unsafe WF artifact{where}: wf_semantics={actual_tag!r}, "
            f"expected {WF_SEMANTICS_TAG!r}. "
            f"Refusing per docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md "
            f"Section RS."
        )
    actual_commit = summary.get("corrected_wf_semantics_commit")
    if actual_commit != CORRECTED_WF_ENGINE_COMMIT:
        raise ValueError(
            f"Unsafe WF artifact{where}: corrected_wf_semantics_commit="
            f"{actual_commit!r}, expected "
            f"{CORRECTED_WF_ENGINE_COMMIT!r}. "
            f"Refusing per docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md "
            f"Section RS."
        )


def check_evaluation_semantics_or_raise(
    summary: dict,
    *,
    artifact_path: str | Path | None = None,
) -> None:
    """Consumer-side: validate a single-run holdout summary is safe for RS-sensitive consumption.

    Companion helper to check_wf_semantics_or_raise(), but for single-run
    holdout artifacts (PHASE2C_6 evaluation gate work) rather than
    walk-forward artifacts. The two helpers MUST stay semantically
    separate — calling this helper on a WF artifact will reject it (it
    won't carry the evaluation_semantics tag), and calling
    check_wf_semantics_or_raise() on a single-run holdout artifact will
    also reject it (it won't carry the wf_semantics tag). This is
    intentional and prevents accidental cross-domain consumption.

    Validates five required fields:

    1. evaluation_semantics == EVALUATION_SEMANTICS_TAG
       ("single_run_holdout_v1")
    2. engine_commit == CORRECTED_WF_ENGINE_COMMIT ("eb1c87f")
    3. engine_corrected_lineage == ENGINE_CORRECTED_LINEAGE_TAG
       ("wf-corrected-v1")
    4. lineage_check == "passed"
    5. current_git_sha is present and non-empty

    Note on lineage_check: this helper validates lineage_check as a
    load-bearing field, unlike the WF helper which treats it as an
    auditor breadcrumb only. The asymmetry is intentional — the
    corrected-engine project arc (Task 7.5 / 7.6 / 11) empirically
    demonstrated that lineage_check round-trip validation catches real
    failure modes that pre-correction artifacts wouldn't. New
    attestation domains (single-run holdout, future validation/test
    evaluations) lock in this stricter validation from day one.

    Raises ValueError (not SystemExit) so consumers in notebooks /
    test harnesses / batch processors can decide how to handle the
    violation.

    Args:
        summary: The single-run holdout summary dict (typically loaded
            from holdout_summary.json or the per-batch aggregate
            summary).
        artifact_path: Optional path to the source JSON file, included
            in the error message for diagnostics.

    Raises:
        ValueError: If any of the five required fields is missing,
            wrong, or empty. The error message identifies the specific
            failing field for diagnostics.
    """
    where = f" at {artifact_path}" if artifact_path else ""

    actual_eval_tag = summary.get("evaluation_semantics")
    if actual_eval_tag is None:
        raise ValueError(
            f"Unsafe single-run holdout artifact{where}: missing "
            f"'evaluation_semantics' field. Expected "
            f"{EVALUATION_SEMANTICS_TAG!r}. Refusing per "
            f"docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md Section RS."
        )
    if actual_eval_tag != EVALUATION_SEMANTICS_TAG:
        raise ValueError(
            f"Unsafe single-run holdout artifact{where}: "
            f"evaluation_semantics={actual_eval_tag!r}, expected "
            f"{EVALUATION_SEMANTICS_TAG!r}. Refusing per "
            f"docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md Section RS."
        )

    actual_engine_commit = summary.get("engine_commit")
    if actual_engine_commit != CORRECTED_WF_ENGINE_COMMIT:
        raise ValueError(
            f"Unsafe single-run holdout artifact{where}: "
            f"engine_commit={actual_engine_commit!r}, expected "
            f"{CORRECTED_WF_ENGINE_COMMIT!r}. Refusing per "
            f"docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md Section RS."
        )

    actual_lineage_tag = summary.get("engine_corrected_lineage")
    if actual_lineage_tag != ENGINE_CORRECTED_LINEAGE_TAG:
        raise ValueError(
            f"Unsafe single-run holdout artifact{where}: "
            f"engine_corrected_lineage={actual_lineage_tag!r}, "
            f"expected {ENGINE_CORRECTED_LINEAGE_TAG!r}. Refusing per "
            f"docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md Section RS."
        )

    actual_check = summary.get("lineage_check")
    if actual_check != "passed":
        raise ValueError(
            f"Unsafe single-run holdout artifact{where}: "
            f"lineage_check={actual_check!r}, expected 'passed'. "
            f"Refusing per docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md "
            f"Section RS."
        )

    actual_sha = summary.get("current_git_sha")
    if not actual_sha:
        raise ValueError(
            f"Unsafe single-run holdout artifact{where}: "
            f"current_git_sha={actual_sha!r} is missing or empty. "
            f"Refusing per docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md "
            f"Section RS."
        )
