"""Unit tests for the corrected-engine lineage guard."""
import subprocess
from unittest.mock import patch
import pytest

from scripts.run_phase2c_batch_walkforward import (
    _enforce_corrected_engine_lineage,
    CORRECTED_WF_ENGINE_COMMIT,
)


def test_guard_accepts_descendant_head():
    """When HEAD is descended from the corrected commit, returns SHA."""
    with patch("subprocess.check_output", return_value="abcd1234\n"), \
         patch("subprocess.call", return_value=0):
        result = _enforce_corrected_engine_lineage()
    assert result == "abcd1234"


def test_guard_rejects_pre_correction_head():
    """When HEAD is NOT descended from the corrected commit, exits."""
    with patch("subprocess.check_output", return_value="0531741\n"), \
         patch("subprocess.call", return_value=1):
        with pytest.raises(SystemExit) as exc_info:
            _enforce_corrected_engine_lineage()
    msg = str(exc_info.value)
    assert CORRECTED_WF_ENGINE_COMMIT in msg
    assert "Section RS" in msg


def test_guard_rejects_outside_git_repo():
    """When git rev-parse fails, exits with clear error."""
    with patch(
        "subprocess.check_output",
        side_effect=subprocess.CalledProcessError(128, ["git"]),
    ):
        with pytest.raises(SystemExit) as exc_info:
            _enforce_corrected_engine_lineage()
    assert "cannot resolve HEAD" in str(exc_info.value)
