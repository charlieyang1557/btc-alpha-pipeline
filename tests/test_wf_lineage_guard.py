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
