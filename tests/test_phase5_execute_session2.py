"""Smoke tests for session-2 orchestrator integration + Codex HIGH-1 regression.

Sealed sub-spec at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md (sub-spec drafting
cycle SEAL at commit 49ae7e3). Session-1 SEAL at commit ad35915.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from phase5.execute_session2 import (
    SEALED_SUBSPEC_COMMIT,
    derive_detections,
    load_session_1_artifacts,
    run_session2,
)


@pytest.fixture
def session_1_artifacts_dir():
    return (
        Path(__file__).resolve().parent.parent
        / "data"
        / "phase5_diagnostic"
        / "execution_session_1_v1"
    )


@pytest.fixture
def silent_logger():
    logger = logging.getLogger("phase5.test_silent")
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.CRITICAL)
    return logger


# ---------- Session-1 artifact load + sealed_subspec_commit cross-check ----------


def test_load_session_1_artifacts_returns_three_envelopes(session_1_artifacts_dir):
    artifacts = load_session_1_artifacts(session_1_artifacts_dir)
    assert "indicator_outputs" in artifacts
    assert "multi_mode_envelope" in artifacts
    assert "ambiguity_envelope" in artifacts


def test_load_session_1_artifacts_raises_on_missing_directory(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_session_1_artifacts(tmp_path / "nonexistent")


def test_derive_detections_reconstructs_from_multi_mode_firing_and_not_detected_sets():
    multi = {
        "firing_modes": ["cost_drag"],
        "not_detected_modes": ["signal_decay", "cohort_weakness"],
    }
    det = derive_detections(multi)
    assert det == {"cost_drag": True, "signal_decay": False, "cohort_weakness": False}


# ---------- Codex HIGH-1 regression: indicator_outputs sealed_subspec_commit validation ----------


def test_run_session2_raises_on_mismatched_indicator_outputs_sealed_commit_per_codex_high_1(
    tmp_path, silent_logger, session_1_artifacts_dir
):
    """Codex HIGH-1 regression: stale indicator_outputs sealed_subspec_commit must raise.

    Per session-1 schema, indicator_outputs has a sealed_subspec_commit field at top
    level; the orchestrator must validate it (previously unchecked).
    """
    fake_session_1 = tmp_path / "fake_session_1"
    fake_session_1.mkdir()
    # Copy good multi + ambiguity envelopes; corrupt indicator_outputs with stale commit.
    for fname in ["multi_mode_labels.json", "ambiguity_disposition.json"]:
        (fake_session_1 / fname).write_text((session_1_artifacts_dir / fname).read_text())
    with (session_1_artifacts_dir / "indicator_outputs.json").open() as fh:
        ind = json.load(fh)
    ind["sealed_subspec_commit"] = "stale_commit_aaa"
    (fake_session_1 / "indicator_outputs.json").write_text(json.dumps(ind))

    with pytest.raises(ValueError, match="indicator_outputs sealed_subspec_commit mismatch"):
        run_session2(
            session_1_dir=fake_session_1,
            output_dir=tmp_path / "out",
            dry_run=True,
            logger=silent_logger,
        )


def test_run_session2_raises_on_indicator_outputs_detected_mismatch_per_codex_high_1(
    tmp_path, silent_logger, session_1_artifacts_dir
):
    """Codex HIGH-1 regression: cross-check indicator_outputs detected flags against §3.1 sets."""
    fake_session_1 = tmp_path / "fake_session_1"
    fake_session_1.mkdir()
    for fname in ["multi_mode_labels.json", "ambiguity_disposition.json"]:
        (fake_session_1 / fname).write_text((session_1_artifacts_dir / fname).read_text())
    with (session_1_artifacts_dir / "indicator_outputs.json").open() as fh:
        ind = json.load(fh)
    # Flip signal_decay to detected=True (was False per session-1) without updating §3.1 firing_modes.
    ind["mode_results"]["signal_decay"]["detected"] = True
    (fake_session_1 / "indicator_outputs.json").write_text(json.dumps(ind))

    with pytest.raises(ValueError, match=r"indicator_outputs mode_results\[signal_decay\]"):
        run_session2(
            session_1_dir=fake_session_1,
            output_dir=tmp_path / "out",
            dry_run=True,
            logger=silent_logger,
        )


# ---------- End-to-end dry-run with session-1 artifacts at canonical register ----------


def test_run_session2_dry_run_clean_against_canonical_session_1_artifacts(
    tmp_path, silent_logger, session_1_artifacts_dir
):
    """Full pipeline executes cleanly against session-1 sealed outputs in dry-run."""
    result = run_session2(
        session_1_dir=session_1_artifacts_dir,
        output_dir=tmp_path / "out",
        dry_run=True,
        logger=silent_logger,
    )
    assert result["dry_run"] is True
    # Session-2 actual case: §4a single_mode + 1 assignment; §5 both NOT-admit.
    assert result["successor_class_result"]["input_pattern"] == "single_mode"
    assert len(result["successor_class_result"]["assignments"]) == 1
    assert result["admissibility_result"]["substantive"]["admissible"] is False
    assert result["admissibility_result"]["operational"]["admissible"] is False
    # §6 anti-pre-emption audit clean.
    assert result["narrative_result"]["anti_pre_emption_audit"][
        "forbidden_pattern_matches"
    ] == []
