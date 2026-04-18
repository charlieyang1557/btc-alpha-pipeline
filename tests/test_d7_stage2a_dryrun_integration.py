"""Tests for scripts/run_d7_stage2a_dryrun.py — D7 Stage 2a dry-run integration.

Covers:
    - Dry-run with synthetic context produces critic_status=ok
    - Dry-run writes result artifact file
    - Dry-run writes summary file
    - Dry-run creates physically isolated ledger (not production path)
    - Dry-run uses stub backend (d7b_mode=stub)
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

from scripts.run_d7_stage2a_dryrun import run_dryrun


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def dryrun_env(tmp_path):
    """Set up isolated directories for dry-run tests."""
    artifacts_root = tmp_path / "raw_payloads"
    artifacts_root.mkdir()
    dryrun_root = tmp_path / "dryrun_payloads"
    dryrun_root.mkdir()
    ledger_path = tmp_path / "ledger_dryrun.db"
    return {
        "artifacts_root": artifacts_root,
        "dryrun_root": dryrun_root,
        "ledger_path": ledger_path,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_dryrun_synthetic_context_produces_critic_status_ok(dryrun_env):
    """Dry-run with synthetic context produces critic_status=ok."""
    batch_uuid = str(uuid.uuid4())
    result = run_dryrun(
        batch_uuid,
        position=102,
        artifacts_root=dryrun_env["artifacts_root"],
        dryrun_root=dryrun_env["dryrun_root"],
        ledger_path=dryrun_env["ledger_path"],
    )
    assert result["critic_status"] == "ok"


def test_dryrun_writes_result_artifact(dryrun_env):
    """Dry-run writes a critic result JSON artifact."""
    batch_uuid = str(uuid.uuid4())
    run_dryrun(
        batch_uuid,
        position=102,
        artifacts_root=dryrun_env["artifacts_root"],
        dryrun_root=dryrun_env["dryrun_root"],
        ledger_path=dryrun_env["ledger_path"],
    )
    result_path = (
        dryrun_env["dryrun_root"]
        / f"dryrun_batch_{batch_uuid}"
        / "dryrun_critic_result_0102.json"
    )
    assert result_path.exists()
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert "critic_status" in result
    assert "d7a_rule_scores" in result
    assert "d7b_llm_scores" in result


def test_dryrun_writes_summary_file(dryrun_env):
    """Dry-run writes a summary JSON file."""
    batch_uuid = str(uuid.uuid4())
    run_dryrun(
        batch_uuid,
        position=42,
        artifacts_root=dryrun_env["artifacts_root"],
        dryrun_root=dryrun_env["dryrun_root"],
        ledger_path=dryrun_env["ledger_path"],
    )
    summary_path = (
        dryrun_env["dryrun_root"]
        / f"dryrun_batch_{batch_uuid}"
        / "dryrun_summary.json"
    )
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["batch_uuid"] == batch_uuid
    assert summary["position"] == 42
    assert summary["source"] == "synthetic"
    assert summary["critic_status"] == "ok"
    assert summary["d7b_mode"] == "stub"


def test_dryrun_uses_physically_isolated_ledger(dryrun_env):
    """Dry-run creates a ledger at the specified path, not production path."""
    batch_uuid = str(uuid.uuid4())
    run_dryrun(
        batch_uuid,
        position=102,
        artifacts_root=dryrun_env["artifacts_root"],
        dryrun_root=dryrun_env["dryrun_root"],
        ledger_path=dryrun_env["ledger_path"],
    )
    assert dryrun_env["ledger_path"].exists()
    # Production ledger should NOT exist in the dryrun dir.
    production_path = Path("agents/spend_ledger.db")
    assert not (dryrun_env["dryrun_root"] / production_path.name).exists()


def test_dryrun_uses_stub_backend(dryrun_env):
    """Dry-run d7b_mode is 'stub' (no live API calls)."""
    batch_uuid = str(uuid.uuid4())
    result = run_dryrun(
        batch_uuid,
        position=102,
        artifacts_root=dryrun_env["artifacts_root"],
        dryrun_root=dryrun_env["dryrun_root"],
        ledger_path=dryrun_env["ledger_path"],
    )
    assert result["d7b_mode"] == "stub"
