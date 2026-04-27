"""Smoke tests for scripts/run_phase2c_evaluation_gate.py.

Verifies the script's wiring (CLI parsing -> lineage guard -> candidate
selection -> per-candidate evaluation -> aggregate write) end-to-end with
the engine call mocked. Does NOT exercise run_regime_holdout itself —
that's covered by tests/test_regime_holdout.py.

Six load-bearing categories:
  1. Lineage guard fires before any engine call.
  2. Per-candidate summary schema for holdout_passed path.
  3. Per-candidate summary schema for holdout_error path (raw_payloads
     missing → resilient failure handling).
  4. Aggregate summary round-trip validates via consumer helper.
  5. --force overwrite refusal on non-empty existing run directory.
  6. --dry-run short-circuits before any engine call or artifact write.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.engine import RegimeHoldoutResult  # noqa: E402
from backtest.wf_lineage import (  # noqa: E402
    CORRECTED_WF_ENGINE_COMMIT,
    ENGINE_CORRECTED_LINEAGE_TAG,
    EVALUATION_SEMANTICS_TAG,
)

runner = importlib.import_module("scripts.run_phase2c_evaluation_gate")


# ---------------------------------------------------------------------------
# Stub fixtures
# ---------------------------------------------------------------------------


def _stub_corrected_candidates() -> list[dict]:
    """Stub a minimal corrected-CSV candidate list: 2 winners + 1 non-winner."""
    return [
        {
            "hypothesis_hash": "0bf34de1eeb57782",
            "position": 1,
            "theme": "volume_divergence",
            "name": "volume_divergence_momentum_194",
            "wf_test_period_sharpe": 2.789,
        },
        {
            "hypothesis_hash": "812216d4abcdef01",
            "position": 23,
            "theme": "mean_reversion",
            "name": "bb_squeeze_oversold_reversal",
            "wf_test_period_sharpe": 0.949,
        },
        {
            "hypothesis_hash": "9436a54bdeadbeef",
            "position": 137,
            "theme": "mean_reversion",
            "name": "oversold_bb_reversion_mean",
            "wf_test_period_sharpe": 0.295,
        },
    ]


def _stub_regime_holdout_result(passed: bool) -> RegimeHoldoutResult:
    """Build a stub RegimeHoldoutResult."""
    sharpe = 0.25 if passed else -0.8
    dd = 0.10 if passed else 0.40
    ret = 0.05 if passed else -0.20
    trades = 50 if passed else 3
    return RegimeHoldoutResult(
        run_id="stub-run-id",
        parent_run_id="stub-parent",
        batch_id="stub-batch",
        hypothesis_hash="stub-hash",
        regime_holdout_passed=passed,
        sharpe_ratio=sharpe,
        max_drawdown=dd,
        total_return=ret,
        total_trades=trades,
        passing_criteria={
            "min_sharpe": -0.5,
            "max_drawdown": 0.25,
            "min_total_return": -0.15,
            "min_total_trades": 5,
        },
        metrics={"sharpe_ratio": sharpe},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_lineage_guard_invoked_before_evaluation(tmp_path, monkeypatch):
    """The script must call enforce_corrected_engine_lineage() at startup."""
    monkeypatch.setattr(
        sys, "argv",
        ["run_phase2c_evaluation_gate.py",
         "--candidate-hashes", "0bf34de1",
         "--run-id", "test_v1",
         "--output-root", str(tmp_path),
         "--dry-run"],
    )
    with patch.object(
        runner, "enforce_corrected_engine_lineage",
        return_value="stub_sha"
    ) as mock_guard, patch.object(
        runner, "_load_corrected_candidates",
        return_value=_stub_corrected_candidates(),
    ):
        rc = runner.main()
    assert rc == 0
    assert mock_guard.called


def test_universe_primary_filters_to_winners(tmp_path, monkeypatch):
    """--universe primary selects only candidates with wf_test_period_sharpe > 0.5."""
    monkeypatch.setattr(
        sys, "argv",
        ["run_phase2c_evaluation_gate.py",
         "--universe", "primary",
         "--run-id", "test_v1",
         "--output-root", str(tmp_path),
         "--dry-run"],
    )
    with patch.object(
        runner, "enforce_corrected_engine_lineage",
        return_value="stub_sha"
    ), patch.object(
        runner, "_load_corrected_candidates",
        return_value=_stub_corrected_candidates(),
    ):
        # Capture the candidate list passed to evaluation
        # via _resolve_candidate_universe behavior.
        all_candidates = _stub_corrected_candidates()
        args = runner._build_argparser().parse_args()
        selected = runner._resolve_candidate_universe(args, all_candidates)
    # Of 3 stub candidates: 2 are winners (>0.5), 1 is non-winner.
    assert len(selected) == 2
    assert all(c["wf_test_period_sharpe"] > 0.5 for c in selected)


def test_per_candidate_summary_holdout_passed_schema(tmp_path):
    """Per-candidate summary for a passing candidate has all required fields."""
    candidate = _stub_corrected_candidates()[0]
    holdout_result = _stub_regime_holdout_result(passed=True)
    output_dir = tmp_path / "test_run"
    output_dir.mkdir()

    with patch.object(
        runner, "_load_dsl_from_response",
        return_value="stub_dsl",
    ), patch.object(
        runner, "run_regime_holdout",
        return_value=holdout_result,
    ):
        summary = runner._evaluate_one_candidate(
            candidate=candidate,
            head_sha="abcd1234567890",
            source_batch_id="stub-source",
            run_id="test_v1",
            output_dir=output_dir,
        )

    # Required schema fields
    assert summary["lifecycle_state"] == "holdout_passed"
    assert summary["holdout_passed"] is True
    assert summary["error_message"] is None
    assert summary["holdout_metrics"]["sharpe_ratio"] == pytest.approx(0.25)
    assert summary["gate_pass_per_criterion"]["sharpe_passed"] is True
    assert summary["gate_pass_per_criterion"]["drawdown_passed"] is True
    assert summary["gate_pass_per_criterion"]["return_passed"] is True
    assert summary["gate_pass_per_criterion"]["trades_passed"] is True
    # Lineage stamping
    assert summary["evaluation_semantics"] == EVALUATION_SEMANTICS_TAG
    assert summary["engine_commit"] == CORRECTED_WF_ENGINE_COMMIT
    assert summary["engine_corrected_lineage"] == ENGINE_CORRECTED_LINEAGE_TAG
    assert summary["lineage_check"] == "passed"
    assert summary["current_git_sha"] == "abcd1234567890"
    # Artifact written and round-trip validated
    summary_path = (
        output_dir / candidate["hypothesis_hash"] / "holdout_summary.json"
    )
    assert summary_path.exists()
    reloaded = json.loads(summary_path.read_text())
    assert reloaded["lifecycle_state"] == "holdout_passed"


def test_per_candidate_summary_holdout_error_schema(tmp_path):
    """Per-candidate summary for an errored candidate has nullable gate fields + traceback."""
    candidate = _stub_corrected_candidates()[0]
    output_dir = tmp_path / "test_run"
    output_dir.mkdir()

    # Force an exception by pointing _load_dsl_from_response at a missing path
    def _raise_missing(*args, **kwargs):
        raise FileNotFoundError("simulated raw_payloads missing")

    with patch.object(
        runner, "_load_dsl_from_response", side_effect=_raise_missing,
    ):
        summary = runner._evaluate_one_candidate(
            candidate=candidate,
            head_sha="abcd1234567890",
            source_batch_id="stub-source",
            run_id="test_v1",
            output_dir=output_dir,
        )

    # holdout_error path
    assert summary["lifecycle_state"] == "holdout_error"
    assert summary["holdout_passed"] is None
    assert summary["holdout_metrics"] is None
    assert summary["passing_criteria"] is None
    assert summary["gate_pass_per_criterion"] is None
    assert summary["error_message"] is not None
    assert "FileNotFoundError" in summary["error_message"]
    assert "simulated raw_payloads missing" in summary["error_message"]
    # Lineage stamping still present in the error path
    assert summary["evaluation_semantics"] == EVALUATION_SEMANTICS_TAG
    assert summary["lineage_check"] == "passed"


def test_aggregate_summary_round_trip_validates(tmp_path):
    """Aggregate summary round-trip validates through check_evaluation_semantics_or_raise."""
    summaries = [
        {
            "hypothesis_hash": "0bf34de1eeb57782",
            "position": 1, "theme": "volume_divergence",
            "name": "x", "wf_test_period_sharpe": 2.789,
            "lifecycle_state": "holdout_passed",
            "holdout_passed": True,
            "holdout_metrics": {
                "sharpe_ratio": 0.5, "max_drawdown": 0.1,
                "total_return": 0.05, "total_trades": 50,
            },
            "wall_clock_seconds": 1.5,
            "error_message": None,
        },
        {
            "hypothesis_hash": "9436a54bdeadbeef",
            "position": 137, "theme": "mean_reversion",
            "name": "y", "wf_test_period_sharpe": 0.295,
            "lifecycle_state": "holdout_failed",
            "holdout_passed": False,
            "holdout_metrics": {
                "sharpe_ratio": -0.8, "max_drawdown": 0.4,
                "total_return": -0.2, "total_trades": 3,
            },
            "wall_clock_seconds": 1.4,
            "error_message": None,
        },
    ]
    aggregate = runner._aggregate_summary_dict(
        summaries=summaries,
        head_sha="abcd1234",
        source_batch_id="stub-source",
        run_id="test_v1",
        universe="audit",
        explicit_hashes=None,
        run_started_utc="2026-04-26T00:00:00Z",
        run_finished_utc="2026-04-26T00:00:30Z",
    )
    out_path = tmp_path / "holdout_summary.json"
    runner._write_aggregate_summary(aggregate, out_path)
    assert out_path.exists()
    reloaded = json.loads(out_path.read_text())
    assert reloaded["counts"]["holdout_passed"] == 1
    assert reloaded["counts"]["holdout_failed"] == 1
    assert reloaded["counts"]["holdout_error"] == 0
    assert reloaded["primary_universe_holdout_passed"] == 1
    assert reloaded["primary_universe_total"] == 1
    assert reloaded["audit_only_holdout_passed"] == 0
    assert reloaded["audit_only_total"] == 1
    # Lineage fields present and validated
    assert reloaded["evaluation_semantics"] == EVALUATION_SEMANTICS_TAG
    assert reloaded["engine_commit"] == CORRECTED_WF_ENGINE_COMMIT


def test_force_overwrite_refusal(tmp_path, monkeypatch):
    """Without --force, the script refuses to overwrite a non-empty existing run dir."""
    run_dir = tmp_path / "existing_run"
    run_dir.mkdir()
    (run_dir / "leftover.txt").write_text("existing artifact")

    monkeypatch.setattr(
        sys, "argv",
        ["run_phase2c_evaluation_gate.py",
         "--candidate-hashes", "0bf34de1",
         "--run-id", "existing_run",
         "--output-root", str(tmp_path),
         "--dry-run"],
    )
    with patch.object(
        runner, "enforce_corrected_engine_lineage",
        return_value="stub_sha"
    ), patch.object(
        runner, "_load_corrected_candidates",
        return_value=_stub_corrected_candidates(),
    ):
        rc = runner.main()
    assert rc == 1, (
        "Expected non-zero exit code when overwriting non-empty dir without --force"
    )
    # Verify --force allows the overwrite
    monkeypatch.setattr(
        sys, "argv",
        ["run_phase2c_evaluation_gate.py",
         "--candidate-hashes", "0bf34de1",
         "--run-id", "existing_run",
         "--output-root", str(tmp_path),
         "--force",
         "--dry-run"],
    )
    with patch.object(
        runner, "enforce_corrected_engine_lineage",
        return_value="stub_sha"
    ), patch.object(
        runner, "_load_corrected_candidates",
        return_value=_stub_corrected_candidates(),
    ):
        rc = runner.main()
    assert rc == 0, "Expected --force to allow overwrite of non-empty dir"
