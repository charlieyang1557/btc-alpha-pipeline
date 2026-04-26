"""Shared WF artifact lineage contract — producer + consumer guards.

This module is the single source of truth for the WF test-boundary
semantics correction enforcement (Section RS of
docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md). Both the producer
(scripts/run_phase2c_batch_walkforward.py and any future Phase 1B
rerun entrypoint) AND every downstream consumer (DSR/PBO/CPCV/MDS/
strategy-shortlist tooling) must use these helpers to enforce the
hard prohibition: pre-correction WF artifacts must not be produced
or consumed.

The producer-side helper (enforce_corrected_engine_lineage) refuses
to run on a HEAD that does not contain the corrected engine commit.
The consumer-side helper (check_wf_semantics_or_raise) refuses to
operate on a summary dict whose lineage metadata is missing or stale.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CORRECTED_WF_ENGINE_COMMIT = "eb1c87f"
WF_SEMANTICS_TAG = "corrected_test_boundary_v1"


def enforce_corrected_engine_lineage() -> str:
    """Producer-side: refuse to run if HEAD doesn't contain the corrected commit.

    Returns the current HEAD SHA on success. Raises SystemExit (clear
    error message) on failure. Used by scripts that PRODUCE
    walk_forward_summary.json artifacts.

    Hard-fails (sys.exit) because callers are scripts at startup —
    aborting is the appropriate response.
    """
    try:
        head_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except subprocess.CalledProcessError as exc:
        sys.exit(
            f"ERROR: cannot resolve HEAD SHA (not in a git repo?): {exc}"
        )

    rc = subprocess.call(
        ["git", "merge-base", "--is-ancestor",
         CORRECTED_WF_ENGINE_COMMIT, "HEAD"]
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
