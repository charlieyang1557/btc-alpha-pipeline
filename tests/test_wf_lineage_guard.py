"""Unit tests for the corrected-engine lineage guards (producer + consumer)."""
import subprocess
from unittest.mock import patch
import pytest

from backtest.wf_lineage import (
    enforce_corrected_engine_lineage,
    CORRECTED_WF_ENGINE_COMMIT,
)


def test_guard_accepts_descendant_head():
    """When HEAD is descended from the corrected commit, returns SHA."""
    with patch(
        "backtest.wf_lineage.subprocess.check_output",
        return_value="abcd1234\n",
    ), patch(
        "backtest.wf_lineage.subprocess.call", return_value=0,
    ):
        result = enforce_corrected_engine_lineage()
    assert result == "abcd1234"


def test_guard_rejects_pre_correction_head():
    """When HEAD is NOT descended from the corrected commit, exits."""
    with patch(
        "backtest.wf_lineage.subprocess.check_output",
        return_value="0531741\n",
    ), patch(
        "backtest.wf_lineage.subprocess.call", return_value=1,
    ):
        with pytest.raises(SystemExit) as exc_info:
            enforce_corrected_engine_lineage()
    msg = str(exc_info.value)
    assert CORRECTED_WF_ENGINE_COMMIT in msg
    assert "Section RS" in msg


def test_guard_rejects_outside_git_repo():
    """When git rev-parse fails, exits with clear error."""
    with patch(
        "backtest.wf_lineage.subprocess.check_output",
        side_effect=subprocess.CalledProcessError(128, ["git"]),
    ):
        with pytest.raises(SystemExit) as exc_info:
            enforce_corrected_engine_lineage()
    assert "cannot resolve HEAD" in str(exc_info.value)


def test_guard_anchors_git_calls_to_repo_root():
    """Both subprocess calls must run with cwd=_REPO_ROOT, regardless of caller CWD.

    Codex Task 7.6 re-review (2026-04-26) flagged that running git from
    the caller's CWD false-rejects legitimate corrected runs invoked
    from /tmp, notebooks, CI wrappers, etc. This test catches any
    future refactor that drops the cwd kwarg from either call.

    Also verifies that merge-base --is-ancestor receives the resolved
    head_sha (not the symbolic 'HEAD'), so what's stamped equals what's
    verified.
    """
    from backtest.wf_lineage import _REPO_ROOT

    with patch(
        "backtest.wf_lineage.subprocess.check_output",
        return_value="abcd1234\n",
    ) as mock_check, patch(
        "backtest.wf_lineage.subprocess.call", return_value=0,
    ) as mock_call:
        result = enforce_corrected_engine_lineage()

    assert result == "abcd1234"
    # check_output (rev-parse HEAD) must use cwd=_REPO_ROOT.
    assert mock_check.call_args.kwargs.get("cwd") == _REPO_ROOT, (
        "rev-parse HEAD must run with cwd=_REPO_ROOT, not caller CWD"
    )
    # call (merge-base --is-ancestor) must use cwd=_REPO_ROOT.
    assert mock_call.call_args.kwargs.get("cwd") == _REPO_ROOT, (
        "merge-base --is-ancestor must run with cwd=_REPO_ROOT"
    )
    # The ancestry check must reference the resolved head_sha, not the
    # symbolic 'HEAD'. This eliminates any HEAD-shift race between the
    # two subprocess calls and ensures stamped SHA == verified SHA.
    call_argv = mock_call.call_args.args[0]
    assert call_argv == [
        "git", "merge-base", "--is-ancestor",
        CORRECTED_WF_ENGINE_COMMIT, "abcd1234",
    ], f"merge-base argv must use resolved head_sha, got {call_argv!r}"


def test_guard_works_when_invoked_from_outside_repo(monkeypatch, tmp_path):
    """Integration test: the guard must succeed regardless of caller CWD.

    Changes CWD to a non-repo directory, then invokes the guard against
    the real repository. If the helper correctly anchors to _REPO_ROOT,
    git should resolve HEAD from the project root and the ancestry
    check should pass (current HEAD is descended from eb1c87f).

    This catches the exact failure Codex reproduced via PYTHONPATH from
    /tmp on 2026-04-26: the guard exited as 'not in a git repo' even
    though the actual checkout was corrected.
    """
    monkeypatch.chdir(tmp_path)
    head_sha = enforce_corrected_engine_lineage()
    assert head_sha, "guard returned empty SHA"
    # Sanity check: SHA looks like a git SHA (hex, length >= 7).
    assert len(head_sha) >= 7
    assert all(c in "0123456789abcdef" for c in head_sha.lower())


# --- Consumer-side helper tests (check_wf_semantics_or_raise) ---

from backtest.wf_lineage import (
    check_wf_semantics_or_raise,
    WF_SEMANTICS_TAG,
)


def test_check_wf_semantics_passes_on_correct_summary():
    """Valid summary dict passes silently."""
    summary = {
        "wf_semantics": WF_SEMANTICS_TAG,
        "corrected_wf_semantics_commit": CORRECTED_WF_ENGINE_COMMIT,
    }
    # Should not raise.
    check_wf_semantics_or_raise(summary)


def test_check_wf_semantics_raises_on_missing_tag():
    """Missing wf_semantics field raises ValueError with 'missing' in message."""
    summary = {
        "corrected_wf_semantics_commit": CORRECTED_WF_ENGINE_COMMIT,
    }
    with pytest.raises(ValueError) as exc_info:
        check_wf_semantics_or_raise(summary, artifact_path="/tmp/foo.json")
    msg = str(exc_info.value)
    assert "missing" in msg
    assert "Section RS" in msg
    assert "/tmp/foo.json" in msg


def test_check_wf_semantics_raises_on_wrong_tag():
    """Wrong wf_semantics value raises ValueError with both expected and actual."""
    summary = {
        "wf_semantics": "old_broken_v0",
        "corrected_wf_semantics_commit": CORRECTED_WF_ENGINE_COMMIT,
    }
    with pytest.raises(ValueError) as exc_info:
        check_wf_semantics_or_raise(summary)
    msg = str(exc_info.value)
    assert "old_broken_v0" in msg
    assert WF_SEMANTICS_TAG in msg
    assert "Section RS" in msg


def test_check_wf_semantics_raises_on_wrong_commit():
    """Mismatched corrected_wf_semantics_commit raises ValueError."""
    summary = {
        "wf_semantics": WF_SEMANTICS_TAG,
        "corrected_wf_semantics_commit": "0531741",  # pre-correction
    }
    with pytest.raises(ValueError) as exc_info:
        check_wf_semantics_or_raise(summary)
    msg = str(exc_info.value)
    assert "0531741" in msg
    assert CORRECTED_WF_ENGINE_COMMIT in msg
    assert "Section RS" in msg


# --- Single-run holdout consumer-side helper tests ---
# (check_evaluation_semantics_or_raise — PHASE2C_6 evaluation gate work)

from backtest.wf_lineage import (
    check_evaluation_semantics_or_raise,
    EVALUATION_SEMANTICS_TAG,
    ENGINE_CORRECTED_LINEAGE_TAG,
)


def _valid_eval_summary() -> dict:
    """Helper: construct a valid single-run holdout summary for tests."""
    return {
        "evaluation_semantics": EVALUATION_SEMANTICS_TAG,
        "engine_commit": CORRECTED_WF_ENGINE_COMMIT,
        "engine_corrected_lineage": ENGINE_CORRECTED_LINEAGE_TAG,
        "lineage_check": "passed",
        "current_git_sha": "abcd1234567890",
    }


def test_check_evaluation_semantics_passes_on_correct_summary():
    """Valid single-run holdout summary dict passes silently."""
    # Should not raise.
    check_evaluation_semantics_or_raise(_valid_eval_summary())


def test_check_evaluation_semantics_raises_on_missing_tag():
    """Missing evaluation_semantics field raises ValueError with field name + path."""
    summary = _valid_eval_summary()
    del summary["evaluation_semantics"]
    with pytest.raises(ValueError) as exc_info:
        check_evaluation_semantics_or_raise(
            summary, artifact_path="/tmp/holdout.json"
        )
    msg = str(exc_info.value)
    assert "evaluation_semantics" in msg
    assert "missing" in msg
    assert EVALUATION_SEMANTICS_TAG in msg
    assert "Section RS" in msg
    assert "/tmp/holdout.json" in msg


def test_check_evaluation_semantics_raises_on_wrong_tag():
    """Wrong evaluation_semantics value raises ValueError with both expected and actual."""
    summary = _valid_eval_summary()
    summary["evaluation_semantics"] = "single_run_validation_v1"  # wrong tag
    with pytest.raises(ValueError) as exc_info:
        check_evaluation_semantics_or_raise(summary)
    msg = str(exc_info.value)
    assert "single_run_validation_v1" in msg
    assert EVALUATION_SEMANTICS_TAG in msg
    assert "Section RS" in msg


def test_check_evaluation_semantics_raises_on_wf_tag_cross_contamination():
    """A WF artifact (with wf_semantics tag, no evaluation_semantics) is rejected.

    Explicit cross-domain rejection test — proves that calling this
    helper on a walk-forward artifact correctly rejects it. Per the
    module-level docstring: the two attestation domains stay
    semantically separate.
    """
    wf_summary = {
        "wf_semantics": WF_SEMANTICS_TAG,
        "corrected_wf_semantics_commit": CORRECTED_WF_ENGINE_COMMIT,
        # Note: does NOT have evaluation_semantics or related fields
    }
    with pytest.raises(ValueError) as exc_info:
        check_evaluation_semantics_or_raise(wf_summary)
    msg = str(exc_info.value)
    assert "evaluation_semantics" in msg
    assert "missing" in msg


def test_check_evaluation_semantics_raises_on_wrong_engine_commit():
    """Mismatched engine_commit raises ValueError with field name and both values."""
    summary = _valid_eval_summary()
    summary["engine_commit"] = "0531741"  # pre-correction
    with pytest.raises(ValueError) as exc_info:
        check_evaluation_semantics_or_raise(summary)
    msg = str(exc_info.value)
    assert "engine_commit" in msg
    assert "0531741" in msg
    assert CORRECTED_WF_ENGINE_COMMIT in msg
    assert "Section RS" in msg


def test_check_evaluation_semantics_raises_on_wrong_lineage_tag():
    """Mismatched engine_corrected_lineage raises ValueError."""
    summary = _valid_eval_summary()
    summary["engine_corrected_lineage"] = "wf-broken-v0"
    with pytest.raises(ValueError) as exc_info:
        check_evaluation_semantics_or_raise(summary)
    msg = str(exc_info.value)
    assert "engine_corrected_lineage" in msg
    assert "wf-broken-v0" in msg
    assert ENGINE_CORRECTED_LINEAGE_TAG in msg
    assert "Section RS" in msg


def test_check_evaluation_semantics_raises_on_failed_lineage_check():
    """lineage_check != 'passed' raises ValueError.

    Asymmetry vs check_wf_semantics_or_raise: the WF helper does NOT gate
    on lineage_check (treats it as auditor breadcrumb). The single-run
    holdout helper DOES gate on it (load-bearing — locks in the stricter
    discipline that the corrected-engine arc taught us is needed).
    """
    summary = _valid_eval_summary()
    summary["lineage_check"] = "failed"
    with pytest.raises(ValueError) as exc_info:
        check_evaluation_semantics_or_raise(summary)
    msg = str(exc_info.value)
    assert "lineage_check" in msg
    assert "failed" in msg
    assert "passed" in msg
    assert "Section RS" in msg


def test_check_evaluation_semantics_raises_on_missing_git_sha():
    """Missing or empty current_git_sha raises ValueError."""
    summary = _valid_eval_summary()
    del summary["current_git_sha"]
    with pytest.raises(ValueError) as exc_info:
        check_evaluation_semantics_or_raise(summary)
    msg = str(exc_info.value)
    assert "current_git_sha" in msg
    assert "missing or empty" in msg
    assert "Section RS" in msg

    # Empty string also fails
    summary = _valid_eval_summary()
    summary["current_git_sha"] = ""
    with pytest.raises(ValueError) as exc_info:
        check_evaluation_semantics_or_raise(summary)
    msg = str(exc_info.value)
    assert "current_git_sha" in msg


def test_check_evaluation_semantics_artifact_path_in_message():
    """When artifact_path is provided, error message includes it for diagnostics."""
    summary = _valid_eval_summary()
    summary["evaluation_semantics"] = "wrong"
    with pytest.raises(ValueError) as exc_info:
        check_evaluation_semantics_or_raise(
            summary, artifact_path="/data/holdout/foo.json"
        )
    msg = str(exc_info.value)
    assert "/data/holdout/foo.json" in msg
