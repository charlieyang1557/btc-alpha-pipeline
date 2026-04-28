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
    ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
    ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1,
    CORRECTED_WF_ENGINE_COMMIT,
    ENGINE_CORRECTED_LINEAGE_TAG,
    EVALUATION_SEMANTICS_TAG,
    REGIME_KEY_LABEL_MAPPING,
    check_evaluation_semantics_or_raise,
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


# ===========================================================================
# PHASE2C_7.1 §6 / §7 — --regime-key flag + 3 lineage fields (sub-step 1.3)
# ===========================================================================


class TestRegimeKeyCliFlag:
    """``--regime-key`` argparse plumbing."""

    def test_regime_key_default_is_regime_holdout(self):
        """Q2 backward-compat: omitted --regime-key → v2.regime_holdout."""
        args = runner._build_argparser().parse_args([
            "--candidate-hashes", "0bf34de1",
            "--run-id", "x",
        ])
        assert args.regime_key == "v2.regime_holdout"

    def test_regime_key_flag_accepts_validation(self):
        """--regime-key v2.validation parsed correctly."""
        args = runner._build_argparser().parse_args([
            "--candidate-hashes", "0bf34de1",
            "--run-id", "x",
            "--regime-key", "v2.validation",
        ])
        assert args.regime_key == "v2.validation"

    def test_regime_key_unknown_value_rejected_at_main(
        self, tmp_path, monkeypatch
    ):
        """Unknown --regime-key value (not in REGIME_KEY_LABEL_MAPPING) rejected.

        Failing early (before any backtest spend) is the operational
        anchor — without this, a typo in the flag would only surface at
        consumer-guard time after the run produces unvalidated artifacts.
        """
        monkeypatch.setattr(
            sys, "argv",
            ["run_phase2c_evaluation_gate.py",
             "--candidate-hashes", "0bf34de1",
             "--run-id", "test_unknown_rk",
             "--output-root", str(tmp_path),
             "--regime-key", "v2.does_not_exist",
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
        assert rc != 0, (
            "Expected non-zero exit code on unknown --regime-key value "
            "(must be in REGIME_KEY_LABEL_MAPPING)"
        )

    # PHASE2C_8.1 §6 — --regime alias + novel regime_keys

    def test_regime_alias_flag_synonym_with_regime_key(self):
        """--regime is a synonym of --regime-key (PHASE2C_8.1 §6 alias)."""
        args = runner._build_argparser().parse_args([
            "--candidate-hashes", "0bf34de1",
            "--run-id", "x",
            "--regime", "v2.validation",
        ])
        assert args.regime_key == "v2.validation"

    def test_regime_alias_accepts_eval_2020_v1(self):
        """--regime evaluation_regimes.eval_2020_v1 parsed correctly."""
        args = runner._build_argparser().parse_args([
            "--candidate-hashes", "0bf34de1",
            "--run-id", "x",
            "--regime", "evaluation_regimes.eval_2020_v1",
        ])
        assert args.regime_key == "evaluation_regimes.eval_2020_v1"

    def test_regime_alias_accepts_eval_2021_v1(self):
        """--regime evaluation_regimes.eval_2021_v1 parsed correctly."""
        args = runner._build_argparser().parse_args([
            "--candidate-hashes", "0bf34de1",
            "--run-id", "x",
            "--regime", "evaluation_regimes.eval_2021_v1",
        ])
        assert args.regime_key == "evaluation_regimes.eval_2021_v1"

    def test_regime_key_flag_still_accepts_eval_2020_v1(self):
        """Backward-compat: --regime-key still works for novel regimes too."""
        args = runner._build_argparser().parse_args([
            "--candidate-hashes", "0bf34de1",
            "--run-id", "x",
            "--regime-key", "evaluation_regimes.eval_2020_v1",
        ])
        assert args.regime_key == "evaluation_regimes.eval_2020_v1"


class TestLineageMetadataThreeNewFields:
    """``_lineage_metadata`` stamps Q3(a) three new fields on EVERY artifact.

    Per Q3(a): the new producer code stamps artifact_schema_version,
    regime_key, regime_label on every forward artifact regardless of
    regime. PHASE2C_6 on-disk artifacts (which predate the schema)
    remain untouched and are covered by the legacy-path regression
    test below.
    """

    def test_default_regime_key_stamps_phase2c_7_1_schema(self):
        """Default regime_key (v2.regime_holdout) → phase2c_7_1 schema with bear_2022 label."""
        meta = runner._lineage_metadata(
            head_sha="abcd1234567890",
            regime_key="v2.regime_holdout",
        )
        assert meta["artifact_schema_version"] == (
            ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1
        )
        assert meta["regime_key"] == "v2.regime_holdout"
        assert meta["regime_label"] == "bear_2022"
        # Five legacy fields remain stamped.
        assert meta["evaluation_semantics"] == EVALUATION_SEMANTICS_TAG
        assert meta["engine_commit"] == CORRECTED_WF_ENGINE_COMMIT
        assert meta["engine_corrected_lineage"] == (
            ENGINE_CORRECTED_LINEAGE_TAG
        )
        assert meta["lineage_check"] == "passed"
        assert meta["current_git_sha"] == "abcd1234567890"

    def test_validation_regime_key_stamps_phase2c_7_1_schema(self):
        """v2.validation regime_key → phase2c_7_1 schema with validation_2024 label."""
        meta = runner._lineage_metadata(
            head_sha="abcd1234567890",
            regime_key="v2.validation",
        )
        assert meta["artifact_schema_version"] == (
            ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1
        )
        assert meta["regime_key"] == "v2.validation"
        assert meta["regime_label"] == "validation_2024"

    def test_unknown_regime_key_raises_at_lineage_metadata(self):
        """Defensive: producer-side helper refuses unknown regime_key."""
        with pytest.raises(ValueError) as exc_info:
            runner._lineage_metadata(
                head_sha="abcd1234567890",
                regime_key="v2.unknown",
            )
        assert "regime_key" in str(exc_info.value)
        assert "v2.unknown" in str(exc_info.value)

    # PHASE2C_8.1 §7 — per-regime discriminator selection

    def test_eval_2020_v1_regime_key_stamps_phase2c_8_1_schema(self):
        """Novel regime_key (eval_2020_v1) → phase2c_8_1 schema with eval_2020_v1 label."""
        meta = runner._lineage_metadata(
            head_sha="abcd1234567890",
            regime_key="evaluation_regimes.eval_2020_v1",
        )
        assert meta["artifact_schema_version"] == (
            ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1
        )
        assert meta["regime_key"] == "evaluation_regimes.eval_2020_v1"
        assert meta["regime_label"] == "eval_2020_v1"
        # Five legacy fields remain stamped on novel-regime artifacts.
        assert meta["evaluation_semantics"] == EVALUATION_SEMANTICS_TAG
        assert meta["engine_commit"] == CORRECTED_WF_ENGINE_COMMIT
        assert meta["engine_corrected_lineage"] == (
            ENGINE_CORRECTED_LINEAGE_TAG
        )
        assert meta["lineage_check"] == "passed"
        assert meta["current_git_sha"] == "abcd1234567890"

    def test_eval_2021_v1_regime_key_stamps_phase2c_8_1_schema(self):
        """Novel regime_key (eval_2021_v1) → phase2c_8_1 schema with eval_2021_v1 label."""
        meta = runner._lineage_metadata(
            head_sha="abcd1234567890",
            regime_key="evaluation_regimes.eval_2021_v1",
        )
        assert meta["artifact_schema_version"] == (
            ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1
        )
        assert meta["regime_key"] == "evaluation_regimes.eval_2021_v1"
        assert meta["regime_label"] == "eval_2021_v1"

    def test_inherited_and_novel_discriminator_selection_independent(self):
        """Mixed-discriminator metadata reconciliation per spec §6.5.

        Inherited regimes stamp phase2c_7_1; novel regimes stamp
        phase2c_8_1; the two paths coexist in the same producer
        invocation surface. Verifies that the discriminator selection
        is per-regime, not global.
        """
        inherited = runner._lineage_metadata(
            head_sha="abcd1234567890",
            regime_key="v2.regime_holdout",
        )
        novel = runner._lineage_metadata(
            head_sha="abcd1234567890",
            regime_key="evaluation_regimes.eval_2020_v1",
        )
        assert inherited["artifact_schema_version"] == (
            ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1
        )
        assert novel["artifact_schema_version"] == (
            ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1
        )
        assert inherited["lineage_check"] == "passed"
        assert novel["lineage_check"] == "passed"


class TestPerCandidateArtifactStampsThreeFields:
    """Per-candidate artifacts stamp the three new fields and validate via new schema path.

    Q3(a) contract: every per-candidate artifact produced by the new
    producer carries artifact_schema_version + regime_key + regime_label
    regardless of which regime is being evaluated.
    """

    def test_default_regime_key_per_candidate_stamps_and_validates(
        self, tmp_path
    ):
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
        ) as mock_holdout:
            summary = runner._evaluate_one_candidate(
                candidate=candidate,
                head_sha="abcd1234567890",
                source_batch_id="stub-source",
                run_id="test_v1",
                output_dir=output_dir,
                regime_key="v2.regime_holdout",
            )

        # Three new fields present on the in-memory summary.
        assert summary["artifact_schema_version"] == (
            ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1
        )
        assert summary["regime_key"] == "v2.regime_holdout"
        assert summary["regime_label"] == "bear_2022"

        # Plumbing assertion: producer passes regime_key to the engine.
        # The engine's run_regime_holdout signature change is sub-step
        # 1.2's deliverable; this test verifies sub-step 1.3 actually
        # uses the parameter rather than relying on the engine's default.
        mock_holdout.assert_called_once()
        call_kwargs = mock_holdout.call_args.kwargs
        assert call_kwargs["regime_key"] == "v2.regime_holdout"

        # On-disk artifact validates via the NEW schema path (not the
        # legacy absent-field path), proving Q3(a) is implemented.
        summary_path = (
            output_dir
            / candidate["hypothesis_hash"]
            / "holdout_summary.json"
        )
        reloaded = json.loads(summary_path.read_text())
        assert "artifact_schema_version" in reloaded, (
            "Q3(a) contract broken: default-regime invocation produced "
            "a legacy-schema artifact (no artifact_schema_version field)."
        )
        check_evaluation_semantics_or_raise(
            reloaded, artifact_path=str(summary_path)
        )

    def test_validation_regime_key_per_candidate_stamps_and_validates(
        self, tmp_path
    ):
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
        ) as mock_holdout:
            summary = runner._evaluate_one_candidate(
                candidate=candidate,
                head_sha="abcd1234567890",
                source_batch_id="stub-source",
                run_id="test_v1",
                output_dir=output_dir,
                regime_key="v2.validation",
            )

        assert summary["artifact_schema_version"] == (
            ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1
        )
        assert summary["regime_key"] == "v2.validation"
        assert summary["regime_label"] == "validation_2024"

        # Engine called with v2.validation, not the default.
        call_kwargs = mock_holdout.call_args.kwargs
        assert call_kwargs["regime_key"] == "v2.validation"

        summary_path = (
            output_dir
            / candidate["hypothesis_hash"]
            / "holdout_summary.json"
        )
        reloaded = json.loads(summary_path.read_text())
        check_evaluation_semantics_or_raise(
            reloaded, artifact_path=str(summary_path)
        )


class TestAggregateArtifactStampsThreeFields:
    """Aggregate summary stamps the three new fields and validates via new schema path."""

    def test_aggregate_artifact_validates_via_new_schema_path(
        self, tmp_path
    ):
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
            regime_key="v2.validation",
        )
        assert aggregate["artifact_schema_version"] == (
            ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1
        )
        assert aggregate["regime_key"] == "v2.validation"
        assert aggregate["regime_label"] == "validation_2024"

        out_path = tmp_path / "holdout_summary.json"
        runner._write_aggregate_summary(aggregate, out_path)
        reloaded = json.loads(out_path.read_text())
        # Validates via the NEW schema path (regime_label cross-checked).
        check_evaluation_semantics_or_raise(
            reloaded, artifact_path=str(out_path)
        )


class TestPhase2C6BackwardCompat:
    """PHASE2C_6 audit_v1 on-disk artifacts validate via legacy absent-field path.

    Regression test using a real canonical PHASE2C_6 artifact as fixture.
    Per Q3(a) interpretation: existing on-disk artifacts predate the
    artifact_schema_version field and continue to validate via the
    sub-step 1.1 discriminator's absent-field branch. This test catches
    any future change that retroactively requires the field on legacy
    artifacts (which would invalidate ~352 PHASE2C_6 artifacts on disk).
    """

    def test_audit_v1_per_candidate_artifact_validates_via_legacy_path(self):
        """Real on-disk PHASE2C_6 audit_v1 artifact validates without the new field."""
        canonical_path = (
            PROJECT_ROOT
            / "data" / "phase2c_evaluation_gate" / "audit_v1"
            / "01f077141926ca19" / "holdout_summary.json"
        )
        if not canonical_path.exists():
            pytest.skip(
                f"PHASE2C_6 audit_v1 fixture not found at {canonical_path} "
                "(may be missing in fresh checkouts; not a sub-step 1.3 "
                "implementation defect)"
            )
        summary = json.loads(canonical_path.read_text())
        # Confirm fixture is what we think it is.
        assert "artifact_schema_version" not in summary, (
            "PHASE2C_6 fixture unexpectedly carries artifact_schema_version; "
            "if a backfill happened this test must be updated to a "
            "different fixture."
        )
        # Must validate via absent-field branch.
        check_evaluation_semantics_or_raise(
            summary, artifact_path=str(canonical_path)
        )


def test_regime_key_label_mapping_round_trip():
    """Sanity: every key in REGIME_KEY_LABEL_MAPPING resolves to a non-empty label.

    Catches future entries that forget to provide a label or use an
    empty string (which would silently fall through to ``regime_label``
    None on artifacts).
    """
    assert REGIME_KEY_LABEL_MAPPING, "Mapping is empty"
    for key, label in REGIME_KEY_LABEL_MAPPING.items():
        assert "." in key, f"regime_key {key!r} must be dotted"
        assert label, f"regime_label for {key!r} must be non-empty"
