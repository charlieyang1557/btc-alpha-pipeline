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
import sqlite3
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.engine import (  # noqa: E402
    RegimeHoldoutResult,
    compute_moments,
    compute_per_bar_returns,
)
from backtest.execution_model import ConstantSlippage, load_execution_config  # noqa: E402
from backtest.experiment_registry import (  # noqa: E402
    DEFAULT_DB_PATH,  # H2: explicit import for db_path co-location lock + Test 20 regression guard
    create_table,
    get_connection,
    get_run,
    insert_run,
)
from backtest.wf_lineage import (  # noqa: E402
    ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
    ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1,
    CORRECTED_WF_ENGINE_COMMIT,
    ENGINE_CORRECTED_LINEAGE_TAG,
    EVALUATION_SEMANTICS_TAG,
    REGIME_KEY_LABEL_MAPPING,
    check_evaluation_semantics_or_raise,
)
from scripts.run_phase2c_evaluation_gate import (  # noqa: E402
    _CSV_FIELDS,
    _build_argparser,
    _evaluate_one_candidate,
    _write_aggregate_csv,
    _write_aggregate_summary,
)

# H3 fix: NEW-symbol imports wrapped so collection succeeds at RED phase.
# At RED phase these symbols don't exist; tests using them fail individually
# (with explicit error via the _require_b_c_narrow_symbols helper below), but
# the test file still collects and ALL OTHER existing tests remain visible.
try:
    from scripts.run_phase2c_evaluation_gate import (  # noqa: E402
        BCNARROW_ARCHIVE_BASENAME,
        BCNARROW_EXECUTION_CONFIG_PATH,
        BCNARROW_PARENT_RUN_ID,
        BCNARROW_REGIME_KEY,
        BCNARROW_SOURCE_BATCH_ID,
        _archive_canonical_pre_flight,
        _finalize_batch_registry,
        _finalize_batch_registry_preflight_or_raise,
        _validate_b_c_narrow_recovery_identity_or_raise,
    )
    _BC_NARROW_SYMBOLS_AVAILABLE = True
    _BC_NARROW_IMPORT_ERROR = ""
except ImportError as _e:
    _BC_NARROW_SYMBOLS_AVAILABLE = False
    _BC_NARROW_IMPORT_ERROR = str(_e)


def _require_b_c_narrow_symbols():
    """Test-helper: raise AssertionError with explicit message if NEW B-C-narrow
    symbols not yet defined in producer (RED phase). Used by tests in
    TestBCNarrowPhase2ProducerEdits to fail with actionable error rather than
    obscure AttributeError."""
    if not _BC_NARROW_SYMBOLS_AVAILABLE:
        raise AssertionError(
            f"B-C-narrow Phase 2 NEW symbols not yet defined in "
            f"scripts/run_phase2c_evaluation_gate.py — Task 10 implementation "
            f"required to bring this test GREEN. Original ImportError: "
            f"{_BC_NARROW_IMPORT_ERROR}"
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
        equity_curve=pd.Series(dtype=float),
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


# ---------------------------------------------------------------------------
# B-C-narrow Phase 2 producer-edit tests (TDD RED phase)
# ---------------------------------------------------------------------------


class TestBCNarrowPhase2ProducerEdits:
    """Phase 2 producer-edit tests — 26 methods total in v11 (14 base from v1 enumeration:
    12 per spec §6.3 + BLOCKING-4 reference test + LC-b threading test; 8 NEW per PFR R1
    ADOPT for CB1/CB2/CB3/CB5/H2/M1/M4; 2 NEW per PFR R2 ADOPT for MR2-3/MR2-4; 1 NEW per
    PFR R5 ADOPT for CR5-B1; 1 NEW per SEAL-eve R2 ADOPT for CR-SE-R2-H1).

    Locked decisions:
    - --enable-b-c-narrow-recovery CLI flag gates the recovery flow (3 NEW behaviors)
    - Archive step uses shutil.move with refuse-if-exists guard (R10 §4.3 G7)
    - `_finalize_batch_registry()` (POST-fire only) calls create_table before insert_run (BLOCKING-3 fix); preflight is TRULY read-only per CR2-B2 v3 (does NOT call create_table)
    - Producer threads 4 LC-b scalars (run_id_override, source_batch_id, parent_run_id_override, artifact_dir) to run_regime_holdout
    - γ3/γ4/T_obs/returns_per_bar_path/returns_per_bar_sha256 merged into inline JSON write at scripts:550-556
    - Producer tests reference `_build_argparser()` (BLOCKING-4 fix)
    - Parent run_id (B-C-narrow recovery cohort): "phase4_forward_2026_15bps_v1_b_c_narrow"
    - Child run_id deterministic scheme: f"{parent_run_id}_{hypothesis_hash}"
    """

    PARENT_RUN_ID = "phase4_forward_2026_15bps_v1_b_c_narrow"
    SOURCE_BATCH_ID = "phase2c_15_main_fire_combined"
    HEAD_SHA = "f112599abcdef"  # test fixture stand-in (any 7+ char string)

    @pytest.fixture
    def stub_holdout_result(self) -> RegimeHoldoutResult:
        """Stub RegimeHoldoutResult with populated equity_curve for unit tests
        that mock run_regime_holdout (avoids running real engine).

        equity_curve length 2528 matches forward_2026 bar count empirically
        observed at Phase 0 fire (per archived original artifact).
        """
        idx = pd.date_range("2026-01-01", periods=2528, freq="h", tz="UTC")
        ec = pd.Series(100_000.0 + pd.Series(range(2528)).astype(float) * 10.0, index=idx)
        return RegimeHoldoutResult(
            run_id="stub-run-id",
            parent_run_id="stub-parent",
            batch_id="stub-batch",
            hypothesis_hash="0" * 64,
            regime_holdout_passed=True,
            sharpe_ratio=1.5,
            max_drawdown=-0.10,
            total_return=0.25,
            total_trades=50,
            passing_criteria={
                "min_sharpe": -0.5,
                "max_drawdown": 0.25,
                "min_total_return": -0.15,
                "min_total_trades": 5,
            },
            metrics={"sharpe_ratio": 1.5, "max_drawdown": -0.10, "total_return": 0.25, "total_trades": 50},
            equity_curve=ec,
        )

    # CR2-B1 PFR R2 ADOPT (v3) — shared helper for LC-b active tests that mock engine.
    # Mirrors Phase 0 engine behavior: writes parquet at artifact_dir AND inserts a
    # child registry row with LC-stamped fields at db_path. Without this, the producer's
    # CB6 `get_run(conn, child_run_id)` query raises RuntimeError on the LC-b active
    # path, causing Tests 1/2/3/7/14 to fail at GREEN phase. v2 amend only updated
    # Test 4 (rewrite) — v3 extends the pattern to ALL LC-b active tests via this helper.
    def _make_fake_engine_with_registry(
        self,
        stub_result: RegimeHoldoutResult,
        db_path: Path,
        captured_kwargs: dict | None = None,
        expected_path: str = "returns_per_bar.parquet",
        expected_sha: str = "9" * 64,
        expected_t_obs: int = 2527,
    ):
        """Build a fake_run_regime_holdout side_effect that mirrors Phase 0 engine SEAL
        behavior. When the test invokes `_evaluate_one_candidate` with `artifact_dir_root`
        set (LC-b active), the producer threads `artifact_dir` + `db_path` to engine; the
        fake here writes the parquet file AND inserts the child registry row that the
        producer's post-engine `get_run(conn, child_run_id)` query depends on.

        If `captured_kwargs` is a dict, it is updated with every call's kwargs (used by
        Test 1 for LC-b kwarg threading assertions).

        For non-LC-b path (artifact_dir is None in kwargs), this helper falls through to
        just returning stub_result — matches engine's legacy path semantics.
        """
        def _fake(**kwargs):
            if captured_kwargs is not None:
                captured_kwargs.update(kwargs)
            # LC-b path: kwargs["artifact_dir"] is set when producer activates LC-b
            artifact_dir = kwargs.get("artifact_dir")
            if artifact_dir is not None:
                artifact_dir.mkdir(parents=True, exist_ok=True)
                (artifact_dir / "returns_per_bar.parquet").write_bytes(b"x")
                # Producer also threads db_path through (None in main()'s default;
                # tests pass explicit tmp_path). Mirror engine's _write_to_registry
                # behavior — insert child row with LC-stamped fields.
                engine_db_path = kwargs.get("db_path") or db_path
                conn = get_connection(engine_db_path)
                try:
                    with conn:
                        create_table(conn)
                        insert_run(conn, {
                            "run_id": kwargs["run_id_override"],
                            "run_type": "regime_holdout",
                            "parent_run_id": kwargs["parent_run_id_override"],
                            "strategy_name": "test_strat",
                            "strategy_source": "b_c_narrow_recovery",
                            "git_commit": "eb1c87f",  # engine OVERRIDE per engine.py:1328-1348
                            "created_at_utc": "2026-05-27T00:00:00Z",
                            "fee_model": "effective_15bps_per_side",
                            "initial_capital": 10_000.0,
                            "returns_per_bar_path": expected_path,
                            "returns_per_bar_sha256": expected_sha,
                            "T_obs": expected_t_obs,
                            "regime_key": kwargs.get("regime_key", "evaluation_regimes.forward_2026"),
                            "batch_id": kwargs.get("source_batch_id"),  # child.batch_id = source_batch_id (per Phase 0)
                        })
                finally:
                    conn.close()
            return stub_result
        return _fake

    @pytest.fixture
    def stub_candidate(self) -> dict:
        """Stub candidate dict matching _load_corrected_candidates schema."""
        return {
            "hypothesis_hash": "18d92ce5d0b40cc7" + "a" * 48,  # 64-char hex
            "position": 32,
            "theme": "mean_reversion",
            "name": "bollinger_zscore_reversion",
            "wf_test_period_sharpe": 0.85,
        }

    # ----- 1. LC-b kwarg threading (1 test) -----

    def test_evaluate_one_candidate_threads_4_lcb_kwargs_to_run_regime_holdout(
        self, stub_holdout_result, stub_candidate, tmp_path
    ):
        """Verify _evaluate_one_candidate passes 4 LC-b kwargs (run_id_override,
        source_batch_id, parent_run_id_override, artifact_dir) to run_regime_holdout
        when artifact_dir_root is provided (LC-b active path).

        Child run_id scheme: f"{parent_run_id_override}_{hypothesis_hash}".

        CR3-B1 PFR R3 ADOPT (v4): uses `_make_fake_engine_with_registry` helper +
        explicit `db_path=db_path` kwarg so producer's CB6 `get_run(conn, child_run_id)`
        post-engine-return query finds the child row (helper inserts it). Without this,
        the test would FAIL at GREEN phase with RuntimeError("child registry row missing").
        """
        _require_b_c_narrow_symbols()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        db_path = tmp_path / "test_threads_lcb.db"

        captured_kwargs: dict = {}

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            side_effect=self._make_fake_engine_with_registry(
                stub_result=stub_holdout_result,
                db_path=db_path,
                captured_kwargs=captured_kwargs,
            ),
        ):
            _evaluate_one_candidate(
                candidate=stub_candidate,
                head_sha=self.HEAD_SHA,
                source_batch_id=self.SOURCE_BATCH_ID,
                run_id=self.PARENT_RUN_ID,
                output_dir=output_dir,
                regime_key="evaluation_regimes.forward_2026",
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                env_config_override={"evaluation_regimes": {"forward_2026": {"end": "2026-04-16"}}},
                artifact_dir_root=artifact_dir_root,
                parent_run_id_override=self.PARENT_RUN_ID,
                db_path=db_path,  # CR3-B1: thread to helper + producer's CB6 query
            )

        # Assert: 4 LC-b kwargs threaded to engine
        expected_child_run_id = f"{self.PARENT_RUN_ID}_{stub_candidate['hypothesis_hash']}"
        expected_artifact_dir = artifact_dir_root / stub_candidate["hypothesis_hash"]
        assert captured_kwargs.get("run_id_override") == expected_child_run_id, (
            f"run_id_override mismatch: expected {expected_child_run_id!r}, "
            f"got {captured_kwargs.get('run_id_override')!r}"
        )
        assert captured_kwargs.get("source_batch_id") == self.SOURCE_BATCH_ID, (
            f"source_batch_id mismatch: expected {self.SOURCE_BATCH_ID!r}, "
            f"got {captured_kwargs.get('source_batch_id')!r}"
        )
        assert captured_kwargs.get("parent_run_id_override") == self.PARENT_RUN_ID, (
            f"parent_run_id_override mismatch: expected {self.PARENT_RUN_ID!r}, "
            f"got {captured_kwargs.get('parent_run_id_override')!r}"
        )
        assert captured_kwargs.get("artifact_dir") == expected_artifact_dir, (
            f"artifact_dir mismatch: expected {expected_artifact_dir!r}, "
            f"got {captured_kwargs.get('artifact_dir')!r}"
        )

    # ----- 2. equity_curve consumption (1 test) -----

    def test_evaluate_one_candidate_uses_equity_curve_from_extended_result(
        self, stub_holdout_result, stub_candidate, tmp_path
    ):
        """Verify producer reads holdout_result.equity_curve (Phase 0 dependency)
        and feeds it through compute_per_bar_returns + compute_moments at the
        producer-side JSON merge layer (LC-b active path).

        This test catches the regression where producer ignores equity_curve and
        emits NaN/None for gamma3/gamma4 even though equity_curve was populated.

        CR3-B1 PFR R3 ADOPT (v4): uses helper + db_path so CB6 producer query finds row.
        """
        _require_b_c_narrow_symbols()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        db_path = tmp_path / "test_uses_equity_curve.db"

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            side_effect=self._make_fake_engine_with_registry(
                stub_result=stub_holdout_result,
                db_path=db_path,
            ),
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_per_bar_returns"
        ) as mock_pbr, patch(
            "scripts.run_phase2c_evaluation_gate.compute_moments"
        ) as mock_moments:
            # H1: 2528-length with first NaN matches engine.compute_per_bar_returns at engine.py:394-396
            mock_pbr.return_value = pd.Series([float('nan')] + [0.01] * 2527)
            # M1: actual compute_moments returns only 3 keys (engine.py:474)
            mock_moments.return_value = {"gamma3": 0.5, "gamma4": 3.2, "T_obs": 2527}

            _evaluate_one_candidate(
                candidate=stub_candidate,
                head_sha=self.HEAD_SHA,
                source_batch_id=self.SOURCE_BATCH_ID,
                run_id=self.PARENT_RUN_ID,
                output_dir=output_dir,
                regime_key="evaluation_regimes.forward_2026",
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                env_config_override={"evaluation_regimes": {"forward_2026": {"end": "2026-04-16"}}},
                artifact_dir_root=artifact_dir_root,
                parent_run_id_override=self.PARENT_RUN_ID,
                db_path=db_path,  # CR3-B1: thread for CB6 producer query
            )

            # Verify producer fed stub equity_curve into compute_per_bar_returns
            mock_pbr.assert_called_once()
            arg = mock_pbr.call_args.args[0] if mock_pbr.call_args.args else mock_pbr.call_args.kwargs.get("equity_curve")
            assert arg is stub_holdout_result.equity_curve, (
                "compute_per_bar_returns must receive holdout_result.equity_curve verbatim "
                "(not a copy or transformation)"
            )
            mock_moments.assert_called_once()

    # ----- 3. Moments merge into summary JSON (1 test) -----

    def test_evaluate_one_candidate_merges_moments_into_summary(
        self, stub_holdout_result, stub_candidate, tmp_path
    ):
        """Verify summary dict (written to inline holdout_summary.json at scripts:550-556)
        includes gamma3, gamma4, T_obs from compute_moments output.

        CR3-B1 PFR R3 ADOPT (v4): uses helper + db_path so CB6 producer query finds row.
        """
        _require_b_c_narrow_symbols()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        db_path = tmp_path / "test_merges_moments.db"

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            side_effect=self._make_fake_engine_with_registry(
                stub_result=stub_holdout_result,
                db_path=db_path,
            ),
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_per_bar_returns",
            return_value=pd.Series([float('nan')] + [0.01] * 2527),  # H1: 2528-length, first NaN
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_moments",
            return_value={"gamma3": 0.5, "gamma4": 3.2, "T_obs": 2527},  # M1
        ):
            _evaluate_one_candidate(
                candidate=stub_candidate,
                head_sha=self.HEAD_SHA,
                source_batch_id=self.SOURCE_BATCH_ID,
                run_id=self.PARENT_RUN_ID,
                output_dir=output_dir,
                regime_key="evaluation_regimes.forward_2026",
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                env_config_override={"evaluation_regimes": {"forward_2026": {"end": "2026-04-16"}}},
                artifact_dir_root=artifact_dir_root,
                parent_run_id_override=self.PARENT_RUN_ID,
                db_path=db_path,  # CR3-B1: thread for CB6 producer query
            )

        artifact_dir = artifact_dir_root / stub_candidate["hypothesis_hash"]
        summary_path = artifact_dir / "holdout_summary.json"
        assert summary_path.exists(), f"holdout_summary.json missing at {summary_path}"
        summary = json.loads(summary_path.read_text())
        assert summary.get("gamma3") == 0.5, f"gamma3 missing/wrong: {summary.get('gamma3')!r}"
        assert summary.get("gamma4") == 3.2, f"gamma4 missing/wrong: {summary.get('gamma4')!r}"
        assert summary.get("T_obs") == 2527, f"T_obs missing/wrong: {summary.get('T_obs')!r}"

    # ----- 4. Path + SHA in summary JSON (1 test) -----
    # CR3-B1 PFR R3 ADOPT (v4): Test 4 is the v2 ADOPT rewrite per CB5+CB6 — producer reads
    # bare filename + SHA from engine-written child registry row (single source), NOT by
    # recomputing from file. Original v1 body removed.

    def test_evaluate_one_candidate_summary_path_sha_from_engine_registry_row(
        self, stub_holdout_result, stub_candidate, tmp_path
    ):
        """CB5+CB6 PFR R1 fix: producer reads returns_per_bar_path (bare filename)
        + returns_per_bar_sha256 from engine-written child registry row (single
        source of truth); does NOT recompute SHA from file. Same column NAME,
        same VALUE everywhere (registry / JSON / CSV)."""
        _require_b_c_narrow_symbols()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        db_path = tmp_path / "test_path_sha.db"
        expected_path = "returns_per_bar.parquet"  # bare filename per engine.py:526
        expected_sha = "a" * 64  # deterministic fixture SHA (64-char lowercase hex)

        def fake_run_regime_holdout(**kwargs):
            # Simulate engine: write parquet + create registry row with stamped values.
            candidate_artifact_dir = kwargs["artifact_dir"]
            candidate_artifact_dir.mkdir(parents=True, exist_ok=True)
            (candidate_artifact_dir / "returns_per_bar.parquet").write_bytes(b"x")
            conn = get_connection(kwargs["db_path"])
            try:
                with conn:
                    create_table(conn)
                    insert_run(conn, {
                        "run_id": kwargs["run_id_override"],
                        "run_type": "regime_holdout",
                        "parent_run_id": kwargs["parent_run_id_override"],
                        "strategy_name": "test_strat",
                        "strategy_source": "b_c_narrow_recovery",
                        "git_commit": "eb1c87f",
                        "created_at_utc": "2026-05-27T00:00:00Z",
                        "fee_model": "effective_15bps_per_side",
                        "initial_capital": 10_000.0,
                        "returns_per_bar_path": expected_path,  # bare filename
                        "returns_per_bar_sha256": expected_sha,
                        "T_obs": 2527,
                    })
            finally:
                conn.close()
            return stub_holdout_result

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            side_effect=fake_run_regime_holdout,
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_per_bar_returns",
            return_value=pd.Series([float('nan')] + [0.01] * 2527),  # H1
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_moments",
            return_value={"gamma3": 0.5, "gamma4": 3.2, "T_obs": 2527},  # M1
        ):
            _evaluate_one_candidate(
                candidate=stub_candidate,
                head_sha=self.HEAD_SHA,
                source_batch_id=self.SOURCE_BATCH_ID,
                run_id=self.PARENT_RUN_ID,
                output_dir=output_dir,
                regime_key="evaluation_regimes.forward_2026",
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                env_config_override={"evaluation_regimes": {"forward_2026": {"end": "2026-04-16"}}},
                artifact_dir_root=artifact_dir_root,
                parent_run_id_override=self.PARENT_RUN_ID,
                db_path=db_path,  # CB6: explicit db_path for hermetic test
            )

        artifact_dir = artifact_dir_root / stub_candidate["hypothesis_hash"]
        summary = json.loads((artifact_dir / "holdout_summary.json").read_text())

        # CB5: bare filename matches engine's child row (NOT subdir/filename).
        assert summary["returns_per_bar_path"] == expected_path
        # CB6: SHA from registry (single source); no recomputation.
        assert summary["returns_per_bar_sha256"] == expected_sha
        # CB5+CB6: cross-validate summary value == registry value (same source).
        with get_connection(db_path) as conn:
            child_run_id = f"{self.PARENT_RUN_ID}_{stub_candidate['hypothesis_hash']}"
            child_row = get_run(conn, child_run_id)
        assert summary["returns_per_bar_path"] == child_row["returns_per_bar_path"]
        assert summary["returns_per_bar_sha256"] == child_row["returns_per_bar_sha256"]

    # ----- 5. _finalize_batch_registry parent-only write (1 test) -----

    def test_finalize_batch_registry_writes_parent_row_only(
        self, tmp_path
    ):
        """Verify `_finalize_batch_registry()` writes ONLY the 1 parent batch_summary row
        at run_id=parent_run_id; does NOT write any child rows. Children are written
        per-candidate inside engine's run_regime_holdout `_write_to_registry` call
        (Phase 0 sequencing per spec §3.1.2)."""
        _require_b_c_narrow_symbols()
        db_path = tmp_path / "test_parent_only.db"

        cohort_metadata = {
            "execution_config_path": "config/execution_phase4_15bps.yaml",
            "execution_config_sha256": "a" * 64,
            "parquet_data_sha256": "b" * 64,
            "regime_key": "evaluation_regimes.forward_2026",
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "current_git_sha": "f112599",
            "effective_start": "2026-01-01T00:00:00Z",
            "initial_capital": 10_000.0,  # AR-SE-M2 SEAL-eve v9: engine cash default per engine.py:2324
            "fee_model": "effective_15bps_per_side",  # AR-SE-M2 SEAL-eve v9: cost_model.fee_model_label per slippage.py:94-100
        }

        _finalize_batch_registry(
            db_path=db_path,
            parent_run_id=self.PARENT_RUN_ID,
            cohort_metadata=cohort_metadata,
        )

        with get_connection(db_path) as conn:
            # Count rows with this parent_run_id as run_id (parent itself)
            parent_rows = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE run_id = ?", (self.PARENT_RUN_ID,)
            ).fetchone()
            # Count rows with parent_run_id pointing to PARENT_RUN_ID (children)
            child_rows = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE parent_run_id = ?", (self.PARENT_RUN_ID,)
            ).fetchone()

        assert parent_rows[0] == 1, f"Expected exactly 1 parent row; got {parent_rows[0]}"
        assert child_rows[0] == 0, (
            f"_finalize_batch_registry MUST NOT write child rows; got {child_rows[0]} "
            f"child row(s). Children are engine's responsibility (Phase 0 sequencing)."
        )

    # ----- 6. _finalize_batch_registry cohort metadata complete (1 test) -----

    def test_finalize_batch_registry_parent_cohort_metadata_complete(
        self, tmp_path
    ):
        """Verify parent row has all 9 required cohort-level fields populated
        (per spec §3.2.3) and per-candidate metric fields NULL."""
        _require_b_c_narrow_symbols()
        db_path = tmp_path / "test_cohort_meta.db"
        cohort_metadata = {
            "execution_config_path": "config/execution_phase4_15bps.yaml",
            "execution_config_sha256": "c" * 64,
            "parquet_data_sha256": "d" * 64,
            "regime_key": "evaluation_regimes.forward_2026",
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "current_git_sha": "f112599",
            "effective_start": "2026-01-01T00:00:00Z",
            "initial_capital": 10_000.0,  # AR-SE-M2 SEAL-eve v9: engine cash default per engine.py:2324
            "fee_model": "effective_15bps_per_side",  # AR-SE-M2 SEAL-eve v9: cost_model.fee_model_label per slippage.py:94-100
        }
        _finalize_batch_registry(
            db_path=db_path,
            parent_run_id=self.PARENT_RUN_ID,
            cohort_metadata=cohort_metadata,
        )
        with get_connection(db_path) as conn:
            row = get_run(conn, self.PARENT_RUN_ID)
        assert row is not None, "Parent row missing"

        # Cohort-level fields populated
        assert row.get("execution_config_path") == "config/execution_phase4_15bps.yaml"
        assert row.get("execution_config_sha256") == "c" * 64
        assert row.get("parquet_data_sha256") == "d" * 64
        assert row.get("regime_key") == "evaluation_regimes.forward_2026"
        assert row.get("cost_anchor_id") == "phase4_forward_15bps_v1"
        assert row.get("current_git_sha") == "f112599"
        assert row.get("strategy_name") == "cohort_summary", (
            f"Parent row strategy_name must be 'cohort_summary' (spec §3.2.3); "
            f"got {row.get('strategy_name')!r}"
        )
        assert row.get("strategy_source") == "b_c_narrow_recovery", (
            f"Parent row strategy_source must be 'b_c_narrow_recovery' (spec §3.2.3); "
            f"got {row.get('strategy_source')!r}"
        )
        assert row.get("run_type") == "batch_summary", (
            f"Parent row run_type must be 'batch_summary'; got {row.get('run_type')!r}"
        )

        # CB3 PFR R1 ADOPT: derived values match engine defaults
        assert row.get("initial_capital") == 10_000.0    # engine cash default per engine.py:2324
        assert row.get("fee_model") == "effective_15bps_per_side"  # cost_model.fee_model_label
        # CB4 PFR R1 ADOPT: git_commit = engine_commit (OVERRIDE pattern per engine.py:1328-1348)
        assert row.get("git_commit") == "eb1c87f"        # CORRECTED_WF_ENGINE_COMMIT
        assert row.get("current_git_sha") == "f112599"   # fire-time HEAD (separate column)
        # CB4 PFR R1 ADOPT: engine_commit in notes JSON for forensic recoverability
        notes = json.loads(row.get("notes") or "{}")
        assert notes.get("engine_commit") == "eb1c87f"

        # Per-candidate metric fields NULL at parent row (spec §3.2.3)
        assert row.get("sharpe_ratio") is None, "Parent row sharpe_ratio must be NULL"
        assert row.get("max_drawdown") is None, "Parent row max_drawdown must be NULL"
        assert row.get("total_return") is None, "Parent row total_return must be NULL"
        assert row.get("total_trades") is None, "Parent row total_trades must be NULL"
        assert row.get("hypothesis_hash") is None, "Parent row hypothesis_hash must be NULL"
        assert row.get("returns_per_bar_path") is None, "Parent row returns_per_bar_path must be NULL"
        assert row.get("returns_per_bar_sha256") is None, "Parent row returns_per_bar_sha256 must be NULL"
        assert row.get("T_obs") is None, "Parent row T_obs must be NULL"

    # ----- 7. Child run_id deterministic scheme (1 test) -----

    def test_finalize_batch_registry_child_run_id_deterministic_scheme(
        self, stub_holdout_result, stub_candidate, tmp_path
    ):
        """Verify producer-passed child run_id_override follows
        f'{parent_run_id}_{hypothesis_hash}' scheme (spec §2 Q4 + §3.4).

        CR3-B1 PFR R3 ADOPT (v4): uses helper + db_path so CB6 producer query finds row.
        """
        _require_b_c_narrow_symbols()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        db_path = tmp_path / "test_child_run_id.db"

        captured_kwargs: dict = {}

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            side_effect=self._make_fake_engine_with_registry(
                stub_result=stub_holdout_result,
                db_path=db_path,
                captured_kwargs=captured_kwargs,
            ),
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_per_bar_returns",
            return_value=pd.Series([float('nan')] + [0.01] * 2527),  # H1
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_moments",
            return_value={"gamma3": 0.5, "gamma4": 3.2, "T_obs": 2527},  # M1
        ):
            _evaluate_one_candidate(
                candidate=stub_candidate,
                head_sha=self.HEAD_SHA,
                source_batch_id=self.SOURCE_BATCH_ID,
                run_id=self.PARENT_RUN_ID,
                output_dir=output_dir,
                regime_key="evaluation_regimes.forward_2026",
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                env_config_override={"evaluation_regimes": {"forward_2026": {"end": "2026-04-16"}}},
                artifact_dir_root=artifact_dir_root,
                parent_run_id_override=self.PARENT_RUN_ID,
                db_path=db_path,  # CR3-B1: thread for CB6 producer query
            )

        expected = f"{self.PARENT_RUN_ID}_{stub_candidate['hypothesis_hash']}"
        assert captured_kwargs.get("run_id_override") == expected, (
            f"Child run_id_override scheme drift: expected {expected!r}, "
            f"got {captured_kwargs.get('run_id_override')!r}. Spec §2 Q4 lock: "
            f"f'{{parent_run_id}}_{{hypothesis_hash}}'."
        )

    # ----- 8. Parent idempotency refuses duplicate (1 test) -----

    def test_finalize_batch_registry_parent_idempotency_refuses_duplicate(
        self, tmp_path
    ):
        """Verify _finalize_batch_registry_preflight_or_raise raises if parent
        run_id already exists in registry (R9 §7 refuse-if-exists)."""
        _require_b_c_narrow_symbols()
        db_path = tmp_path / "test_idempotent.db"
        cohort_metadata = {
            "execution_config_path": "config/execution_phase4_15bps.yaml",
            "execution_config_sha256": "e" * 64,
            "parquet_data_sha256": "f" * 64,
            "regime_key": "evaluation_regimes.forward_2026",
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "current_git_sha": "f112599",
            "effective_start": "2026-01-01T00:00:00Z",
            "initial_capital": 10_000.0,  # AR-SE-M2 SEAL-eve v9: engine cash default per engine.py:2324
            "fee_model": "effective_15bps_per_side",  # AR-SE-M2 SEAL-eve v9: cost_model.fee_model_label per slippage.py:94-100
        }
        # First write: should succeed
        _finalize_batch_registry(
            db_path=db_path,
            parent_run_id=self.PARENT_RUN_ID,
            cohort_metadata=cohort_metadata,
        )
        # Second call to preflight without --force-rerun-existing must raise
        with pytest.raises(RuntimeError, match=r"parent_run_id .* already exists"):
            _finalize_batch_registry_preflight_or_raise(
                db_path=db_path,
                parent_run_id=self.PARENT_RUN_ID,
                force_rerun_existing=False,
            )

    # ----- 9. Compensating cleanup on partial failure (1 test) -----

    def test_finalize_batch_registry_compensating_cleanup_on_partial_failure(
        self, tmp_path
    ):
        """Verify --force-rerun-existing DELETEs rows WHERE parent_run_id = '...'
        AND WHERE run_id = '...' (parent itself) before re-fire allowed.

        M2 PFR R1 NOTE: this test exercises the DELETE WHERE query behavior, which
        is field-agnostic — children inserted here are hand-rolled minimal-shape
        rows (NOT realistic engine-written rows with full LC-stamped fields).
        The cleanup mechanism works the same way regardless of row shape, so this
        test is sufficient for verifying the DELETE behavior. Realistic engine-
        written partial-fire state exercise is deferred to the Phase 3 E2E test
        suite (tests/test_b_c_narrow_recovery.py per spec §6.1)."""
        _require_b_c_narrow_symbols()
        db_path = tmp_path / "test_cleanup.db"

        # Setup: 5 child rows + 1 parent row pre-existing
        with get_connection(db_path) as conn:
            create_table(conn)
            for i in range(5):
                insert_run(conn, {
                    "run_id": f"{self.PARENT_RUN_ID}_child_{i}",
                    "run_type": "regime_holdout",
                    "parent_run_id": self.PARENT_RUN_ID,
                    "strategy_name": "test_strategy",
                    "strategy_source": "b_c_narrow_recovery",
                    "created_at_utc": "2026-05-27T00:00:00Z",
                    "git_commit": "f112599",
                    "fee_model": "effective_15bps_per_side",  # AR-SE-M2 SEAL-eve v9
                    "initial_capital": 10_000.0,  # AR-SE-M2 SEAL-eve v9
                    "final_capital": 105000.0,
                    "total_return": 0.05,
                    "sharpe_ratio": 1.0,
                    "max_drawdown": -0.10,
                    "total_trades": 10,
                })
            insert_run(conn, {
                "run_id": self.PARENT_RUN_ID,
                "run_type": "batch_summary",
                "parent_run_id": None,
                "strategy_name": "cohort_summary",
                "strategy_source": "b_c_narrow_recovery",
                "created_at_utc": "2026-05-27T00:00:00Z",
                "git_commit": "f112599",
                "fee_model": "effective_15bps_per_side",  # AR-SE-M2 SEAL-eve v9
                "initial_capital": 10_000.0,  # AR-SE-M2 SEAL-eve v9
            })

        # Preflight with --force-rerun-existing: should DELETE all 6 rows
        _finalize_batch_registry_preflight_or_raise(
            db_path=db_path,
            parent_run_id=self.PARENT_RUN_ID,
            force_rerun_existing=True,
        )

        # Verify clean state
        with get_connection(db_path) as conn:
            remaining_children = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE parent_run_id = ?", (self.PARENT_RUN_ID,)
            ).fetchone()[0]
            remaining_parent = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE run_id = ?", (self.PARENT_RUN_ID,)
            ).fetchone()[0]
        assert remaining_children == 0, (
            f"DELETE WHERE parent_run_id incomplete: {remaining_children} children remain"
        )
        assert remaining_parent == 0, (
            f"DELETE WHERE run_id (parent) incomplete: {remaining_parent} parent remains"
        )

    # ----- 10. Archive step creates archive dir if absent (1 test) -----

    def test_archive_step_creates_archive_dir_if_absent(self, tmp_path):
        """Verify _archive_canonical_pre_flight creates archive/ parent dir
        when absent (per spec §3.2.4)."""
        _require_b_c_narrow_symbols()
        canonical = tmp_path / "phase4_forward_2026_15bps_v1"
        canonical.mkdir()
        (canonical / "holdout_summary.json").write_text('{"x": 1}')
        archive_root = tmp_path / "archive"  # does NOT exist
        assert not archive_root.exists()

        _archive_canonical_pre_flight(
            canonical_path=canonical,
            archive_root=archive_root,
            archive_basename="phase4_forward_2026_15bps_v1_d0b8101",
        )

        assert archive_root.exists() and archive_root.is_dir(), (
            "archive/ root dir must be created if absent"
        )
        archived = archive_root / "phase4_forward_2026_15bps_v1_d0b8101"
        assert archived.exists(), f"Archive target missing at {archived}"
        assert (archived / "holdout_summary.json").exists(), "Archive content missing"
        assert not canonical.exists(), "Canonical path must be vacated after archive"

    # ----- 11. Archive step refuses existing archive target (1 test) -----

    def test_archive_step_refuses_existing_archive_target(self, tmp_path):
        """Verify _archive_canonical_pre_flight raises if archive target exists
        (G7 §4.3 strict refuse-if-exists; manual cleanup required)."""
        _require_b_c_narrow_symbols()
        canonical = tmp_path / "phase4_forward_2026_15bps_v1"
        canonical.mkdir()
        (canonical / "holdout_summary.json").write_text('{"x": 1}')
        archive_root = tmp_path / "archive"
        archive_root.mkdir()
        existing_archive = archive_root / "phase4_forward_2026_15bps_v1_d0b8101"
        existing_archive.mkdir()
        (existing_archive / "stale.txt").write_text("stale content")

        with pytest.raises(FileExistsError, match=r"archive target .* already exists"):
            _archive_canonical_pre_flight(
                canonical_path=canonical,
                archive_root=archive_root,
                archive_basename="phase4_forward_2026_15bps_v1_d0b8101",
            )

        # Canonical path must NOT be touched on failure
        assert canonical.exists(), "Canonical must not be vacated on refuse"

    # ----- 12. CSV fields extension includes new columns (1 test) -----

    def test_csv_fields_extension_includes_new_columns(self):
        """Verify _CSV_FIELDS includes the 5 new B-C-narrow fields (spec §3.2.5)
        in addition to all existing 13 fields."""
        _require_b_c_narrow_symbols()
        new_fields = {
            "gamma3",
            "gamma4",
            "T_obs",
            "returns_per_bar_path",
            "returns_per_bar_sha256",
        }
        missing = new_fields - set(_CSV_FIELDS)
        assert not missing, (
            f"_CSV_FIELDS missing B-C-narrow fields: {missing}. "
            f"Spec §3.2.5 lock: 5 new fields appended."
        )
        # Existing 13 fields preserved
        existing_required = {
            "hypothesis_hash", "position", "theme", "name", "wf_test_period_sharpe",
            "lifecycle_state", "holdout_passed", "holdout_sharpe", "holdout_max_drawdown",
            "holdout_total_return", "holdout_total_trades", "wall_clock_seconds",
            "error_message",
        }
        existing_missing = existing_required - set(_CSV_FIELDS)
        assert not existing_missing, (
            f"_CSV_FIELDS lost existing fields (regression): {existing_missing}"
        )

    # ----- 13. BLOCKING-4 _build_argparser callable (1 test) -----

    def test_build_argparser_callable_no_parse_args(self):
        """BLOCKING-4 fix: producer exposes `_build_argparser()` (not `_parse_args`).

        Phase 0 plan v2 referenced non-existent `_parse_args` — this test locks
        the convention forward so future Phase 2 work doesn't re-introduce the
        BLOCKING-4 regression."""
        _require_b_c_narrow_symbols()
        import scripts.run_phase2c_evaluation_gate as runner

        assert callable(getattr(runner, "_build_argparser", None)), (
            "Producer must expose callable `_build_argparser`; BLOCKING-4 fix"
        )
        assert not hasattr(runner, "_parse_args"), (
            "Producer MUST NOT expose `_parse_args` — that name was BLOCKING-4 "
            "from Phase 0 plan v2 (function does not exist)."
        )
        # Verify the parser includes the new --enable-b-c-narrow-recovery flag
        parser = runner._build_argparser()
        actions = {a.dest: a for a in parser._actions}
        assert "enable_b_c_narrow_recovery" in actions, (
            "argparse must include --enable-b-c-narrow-recovery flag (Step 10.2 lock)"
        )
        assert "force_rerun_existing" in actions, (
            "argparse must include --force-rerun-existing flag (R9-B-guarded lock)"
        )

    # ----- 14. Schema domain routing (1 test) -----

    def test_schema_domain_routing_evaluation_for_summary_b_c_extended_for_parquet(
        self, stub_holdout_result, stub_candidate, tmp_path
    ):
        """Per spec §3.3: per-candidate holdout_summary.json uses evaluation domain
        (artifact_schema_version: phase2c_7_1) with ADDITIVE B-C-narrow fields.
        The existing check_evaluation_semantics_or_raise at scripts:557-562 must
        NOT raise on the augmented summary.

        CR3-B1 PFR R3 ADOPT (v4): uses helper + db_path so CB6 producer query finds row.
        """
        _require_b_c_narrow_symbols()
        from backtest.wf_lineage import check_evaluation_semantics_or_raise

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        db_path = tmp_path / "test_schema_routing.db"

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            side_effect=self._make_fake_engine_with_registry(
                stub_result=stub_holdout_result,
                db_path=db_path,
            ),
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_per_bar_returns",
            return_value=pd.Series([float('nan')] + [0.01] * 2527),  # H1
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_moments",
            return_value={"gamma3": 0.5, "gamma4": 3.2, "T_obs": 2527},  # M1
        ):
            _evaluate_one_candidate(
                candidate=stub_candidate,
                head_sha=self.HEAD_SHA,
                source_batch_id=self.SOURCE_BATCH_ID,
                run_id=self.PARENT_RUN_ID,
                output_dir=output_dir,
                regime_key="evaluation_regimes.forward_2026",
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                env_config_override={"evaluation_regimes": {"forward_2026": {"end": "2026-04-16"}}},
                artifact_dir_root=artifact_dir_root,
                parent_run_id_override=self.PARENT_RUN_ID,
                db_path=db_path,  # CR3-B1: thread for CB6 producer query
            )

        artifact_dir = artifact_dir_root / stub_candidate["hypothesis_hash"]
        summary_path = artifact_dir / "holdout_summary.json"
        summary = json.loads(summary_path.read_text())

        # Required evaluation-domain fields preserved
        assert summary.get("artifact_schema_version") == "phase2c_7_1", (
            f"artifact_schema_version drift: {summary.get('artifact_schema_version')!r}"
        )
        assert summary.get("regime_key") == "evaluation_regimes.forward_2026"
        assert summary.get("evaluation_semantics") == "single_run_holdout_v1"

        # B-C-narrow ADDITIVE fields present alongside evaluation-domain fields
        assert "gamma3" in summary
        assert "gamma4" in summary
        assert "T_obs" in summary
        assert "returns_per_bar_path" in summary
        assert "returns_per_bar_sha256" in summary

        # Evaluation validator does NOT raise on the augmented summary
        check_evaluation_semantics_or_raise(summary, artifact_path=str(summary_path))

    # ===== v2 PFR R1 ADOPT — 8 NEW tests =====

    # ----- Test 15 (CB1): --dry-run + --enable-b-c-narrow-recovery no-mutation -----

    def test_dry_run_with_b_c_narrow_recovery_leaves_state_untouched(self, tmp_path, monkeypatch):
        """CB1 PFR R1 fix: when --dry-run is set together with --enable-b-c-narrow-recovery,
        the producer's PRE-flight chain runs read-only checks (identity guard + idempotency)
        and exits at the existing dry-run gate, with NO archive or DB mutation."""
        _require_b_c_narrow_symbols()
        output_root = tmp_path / "output"
        output_root.mkdir()
        canonical = output_root / "phase4_forward_2026_15bps_v1"
        canonical.mkdir()
        (canonical / "marker.json").write_text('{"pre_run": true}')
        archive_root = output_root / "archive"
        db_path = tmp_path / "dry_run_db.db"
        # MR3-1 PFR R3 ADOPT (v4): monkeypatch the PRODUCER's local binding, NOT the
        # experiment_registry module's attribute. Per `from X import Y` semantics:
        # `from backtest.experiment_registry import DEFAULT_DB_PATH` creates a local
        # binding in scripts.run_phase2c_evaluation_gate at import time; patching
        # `backtest.experiment_registry.DEFAULT_DB_PATH` does NOT redirect that local
        # binding. Without this fix the preflight would silently read the REAL DB
        # (backtest/experiments.db, 3.8MB), Test 15 would pass spuriously without
        # actually verifying the CB1 dry-run no-mutation invariant against the tmp DB.
        monkeypatch.setattr("scripts.run_phase2c_evaluation_gate.DEFAULT_DB_PATH", db_path)

        with patch(
            "scripts.run_phase2c_evaluation_gate._load_corrected_candidates",
            return_value=[{
                "hypothesis_hash": "test_hash_" + "a" * 53,
                "position": 0, "theme": "test", "name": "test",
                "wf_test_period_sharpe": 0.5,
            }],
        ), patch(
            "scripts.run_phase2c_evaluation_gate.enforce_corrected_engine_lineage",
            return_value="f112599abcdef",
        ), patch("sys.argv", [
            "run_phase2c_evaluation_gate.py",
            "--source-batch-id", BCNARROW_SOURCE_BATCH_ID,
            "--candidate-hashes", "test_hash_",
            "--run-id", BCNARROW_PARENT_RUN_ID,
            "--regime-key", BCNARROW_REGIME_KEY,
            "--execution-config", BCNARROW_EXECUTION_CONFIG_PATH,
            "--output-root", str(output_root),
            "--enable-b-c-narrow-recovery",
            "--dry-run",
        ]):
            from scripts.run_phase2c_evaluation_gate import main
            rc = main()

        assert canonical.exists(), "CB1: dry-run must NOT archive canonical"
        assert (canonical / "marker.json").exists(), "CB1: marker file must remain"
        assert not archive_root.exists() or not any(archive_root.iterdir()), (
            "CB1: dry-run must NOT create archive target"
        )
        # CR-SE-B1 SEAL-eve v9 fix: actually enforce dry-run DB no-mutation invariant.
        # PRIOR v8 body checked parent-row count IF DB exists AND called create_table(conn)
        # in the assertion path — but create_table commits DDL, which would CREATE the runs
        # table during the assertion, masking the very mutation the test was meant to detect.
        # v9 strict assertion: DB file MUST NOT EXIST after dry-run with absent-DB start
        # state (CR2-B2 v3 preflight is truly read-only on absent-DB → Path 1 early-exit
        # returns clean WITHOUT opening or creating the DB file). If DB file exists post-
        # dry-run, that proves W1 preflight or some downstream code mutated state on a
        # supposedly-read-only path.
        assert not db_path.exists(), (
            f"CR-SE-B1 SEAL-eve: dry-run with absent-DB start MUST leave DB file absent. "
            f"db_path={db_path} unexpectedly exists post-dry-run; this proves W1 preflight "
            f"or downstream code mutated state on a supposedly-read-only dry-run path "
            f"(CB1 invariant breach). CR2-B2 v3 preflight Path 1 must early-exit on absent-DB "
            f"WITHOUT calling get_connection (which creates the file in sqlite3 semantics)."
        )

    # ----- Test 16 (CB1): pre-existing parent row → preflight refuses BEFORE archive -----

    def test_preflight_refuses_before_archive_when_parent_exists(self, tmp_path):
        """CR-SE-R2-M1 SEAL-eve R2 ADOPT v10: this test directly exercises
        `_finalize_batch_registry_preflight_or_raise` (helper-only) — verifies
        the preflight raises RuntimeError when parent_run_id already exists in
        registry. The canonical filesystem untouched assertion below is trivially
        true since preflight is filesystem-read-only.

        Note: end-to-end main() ordering (W1 reorder per CR-SE-H1 v9 — registry
        rows REMAIN when overwrite-protection refuses) is exercised separately
        by Test 26 (`test_w1_reorder_force_rerun_existing_without_force_leaves_registry_intact`).
        This test does NOT exercise main() ordering; only the helper's raise behavior."""
        _require_b_c_narrow_symbols()
        output_root = tmp_path / "output"
        output_root.mkdir()
        canonical = output_root / "phase4_forward_2026_15bps_v1"
        canonical.mkdir()
        (canonical / "marker.json").write_text('{"pre_existing": true}')
        db_path = tmp_path / "test_preflight_refuse.db"

        conn = get_connection(db_path)
        try:
            with conn:
                create_table(conn)
                insert_run(conn, {
                    "run_id": BCNARROW_PARENT_RUN_ID,
                    "run_type": "batch_summary",
                    "parent_run_id": None,
                    "strategy_name": "cohort_summary",
                    "strategy_source": "b_c_narrow_recovery",
                    "git_commit": "eb1c87f",
                    "created_at_utc": "2026-05-26T00:00:00Z",
                    "fee_model": "effective_15bps_per_side",
                    "initial_capital": 10_000.0,
                })
        finally:
            conn.close()

        with pytest.raises(RuntimeError, match=r"parent_run_id .* already exists"):
            _finalize_batch_registry_preflight_or_raise(
                parent_run_id=BCNARROW_PARENT_RUN_ID,
                force_rerun_existing=False,
                db_path=db_path,
            )

        assert canonical.exists()
        assert (canonical / "marker.json").exists()

    # ----- Test 17 (CB2): identity guard rejects each wrong-value field -----

    @pytest.mark.parametrize("wrong_field,wrong_value", [
        ("run_id", "some-random-uuid-not-bcnarrow"),
        ("regime_key", "v2.regime_holdout"),
        ("execution_config_path", Path("config/execution_phase4_07bps.yaml")),
        ("source_batch_id", "some-other-batch-uuid"),
    ])
    def test_identity_guard_rejects_wrong_value(self, wrong_field, wrong_value):
        """CB2 PFR R1 fix: identity guard must reject when any of 4 fields mismatches
        BCNARROW_* constants. Test parametrized across all 4 wrong-value cases."""
        _require_b_c_narrow_symbols()
        kwargs = {
            "run_id": BCNARROW_PARENT_RUN_ID,
            "regime_key": BCNARROW_REGIME_KEY,
            "execution_config_path": Path(BCNARROW_EXECUTION_CONFIG_PATH),
            "source_batch_id": BCNARROW_SOURCE_BATCH_ID,
        }
        kwargs[wrong_field] = wrong_value
        with pytest.raises(ValueError, match=r"must equal"):
            _validate_b_c_narrow_recovery_identity_or_raise(**kwargs)

    # ----- Test 18 (CB3): parent metadata derived from engine defaults -----

    def test_finalize_batch_registry_parent_metadata_matches_engine_defaults(self, tmp_path):
        """CB3 PFR R1 fix: parent.initial_capital MUST equal engine cash default
        (10_000.0 per engine.py:2324); parent.fee_model MUST equal
        cost_model.fee_model_label (= 'effective_15bps_per_side' for 15bps anchor
        per slippage.py:94-100) — both DERIVED, never hardcoded literals."""
        _require_b_c_narrow_symbols()
        db_path = tmp_path / "test_consistency.db"
        exec_cfg = load_execution_config(Path(BCNARROW_EXECUTION_CONFIG_PATH))
        cost_model = ConstantSlippage.from_config(exec_cfg)
        cohort_metadata = {
            "execution_config_path": BCNARROW_EXECUTION_CONFIG_PATH,
            "execution_config_sha256": "e" * 64,
            "parquet_data_sha256": "f" * 64,
            "regime_key": BCNARROW_REGIME_KEY,
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "current_git_sha": "f112599",
            "effective_start": "2026-01-01T00:00:00Z",
            "initial_capital": 10_000.0,
            "fee_model": cost_model.fee_model_label,
        }
        _finalize_batch_registry(
            parent_run_id=BCNARROW_PARENT_RUN_ID,
            cohort_metadata=cohort_metadata,
            db_path=db_path,
        )
        with get_connection(db_path) as conn:
            row = get_run(conn, BCNARROW_PARENT_RUN_ID)
        assert row.get("initial_capital") == 10_000.0
        assert row.get("fee_model") == "effective_15bps_per_side"

    # ----- Test 19 (CB5): producer summary.returns_per_bar_path == registry child row value -----

    def test_producer_returns_per_bar_path_matches_engine_child_row(
        self, stub_holdout_result, stub_candidate, tmp_path
    ):
        """CB5 PFR R1 fix (cross-validation companion to rewritten Test 4):
        verify producer JSON value EQUALS engine child registry row value for
        returns_per_bar_path. Both must be the bare filename 'returns_per_bar.parquet'."""
        _require_b_c_narrow_symbols()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        db_path = tmp_path / "test_path_match.db"
        bare_filename = "returns_per_bar.parquet"

        def fake_run_regime_holdout(**kwargs):
            candidate_artifact_dir = kwargs["artifact_dir"]
            candidate_artifact_dir.mkdir(parents=True, exist_ok=True)
            (candidate_artifact_dir / bare_filename).write_bytes(b"x")
            conn = get_connection(kwargs["db_path"])
            try:
                with conn:
                    create_table(conn)
                    insert_run(conn, {
                        "run_id": kwargs["run_id_override"],
                        "run_type": "regime_holdout",
                        "parent_run_id": kwargs["parent_run_id_override"],
                        "strategy_name": "test_strat",
                        "strategy_source": "b_c_narrow_recovery",
                        "git_commit": "eb1c87f",
                        "created_at_utc": "2026-05-27T00:00:00Z",
                        "fee_model": "effective_15bps_per_side",
                        "initial_capital": 10_000.0,
                        "returns_per_bar_path": bare_filename,
                        "returns_per_bar_sha256": "9" * 64,
                        "T_obs": 2527,
                    })
            finally:
                conn.close()
            return stub_holdout_result

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            side_effect=fake_run_regime_holdout,
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_per_bar_returns",
            return_value=pd.Series([float('nan')] + [0.01] * 2527),
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_moments",
            return_value={"gamma3": 0.5, "gamma4": 3.2, "T_obs": 2527},
        ):
            _evaluate_one_candidate(
                candidate=stub_candidate,
                head_sha=self.HEAD_SHA,
                source_batch_id=self.SOURCE_BATCH_ID,
                run_id=self.PARENT_RUN_ID,
                output_dir=output_dir,
                regime_key="evaluation_regimes.forward_2026",
                execution_config_path=Path(BCNARROW_EXECUTION_CONFIG_PATH),
                env_config_override={"evaluation_regimes": {"forward_2026": {"end": "2026-04-16"}}},
                artifact_dir_root=artifact_dir_root,
                parent_run_id_override=self.PARENT_RUN_ID,
                db_path=db_path,
            )

        artifact_dir = artifact_dir_root / stub_candidate["hypothesis_hash"]
        summary = json.loads((artifact_dir / "holdout_summary.json").read_text())
        # MR3-4 PFR R3 ADOPT (v4): explicit try/finally conn.close() (matches MR2-1 producer pattern + M3 finalize pattern)
        _conn = get_connection(db_path)
        try:
            child_row = get_run(_conn, f"{self.PARENT_RUN_ID}_{stub_candidate['hypothesis_hash']}")
        finally:
            _conn.close()
        assert summary["returns_per_bar_path"] == bare_filename
        assert child_row["returns_per_bar_path"] == bare_filename
        assert summary["returns_per_bar_path"] == child_row["returns_per_bar_path"]

    # ----- Test 20 (H2): DEFAULT_DB_PATH co-location regression guard -----

    def test_default_db_path_constant_regression_guard(self):
        """H2 PFR R1 fix + MR2-2 PFR R2 ADOPT: lock DEFAULT_DB_PATH value to its
        canonical location so a future refactor cannot silently split parent
        (producer-written) from children (engine-written) into different DBs.

        MR2-2 PFR R2 ADOPT (v3): use REGISTRY_PROJECT_ROOT (imported from
        backtest.experiment_registry via `PROJECT_ROOT as REGISTRY_PROJECT_ROOT`)
        instead of hardcoded absolute path /Users/yutianyang/... — test is now
        portable across environments (CI, code-review clones, machine renames)
        while preserving H2 regression-guard goal."""
        _require_b_c_narrow_symbols()
        # MR2-2 v3: portable path via REGISTRY_PROJECT_ROOT (not hardcoded absolute)
        from backtest.experiment_registry import PROJECT_ROOT as _REGISTRY_PROJECT_ROOT
        expected = _REGISTRY_PROJECT_ROOT / "backtest" / "experiments.db"
        assert DEFAULT_DB_PATH == expected, (
            f"H2: DEFAULT_DB_PATH drift. Expected {expected!r}; got {DEFAULT_DB_PATH!r}. "
            f"Parent + engine-written children rely on this constant for co-location."
        )

    # ----- Test 21 (M4): LC-b e2e real engine smoke -----

    def test_lcb_e2e_real_engine_writes_parquet_and_registry(
        self, dsl_bollinger_zscore_reversion, tmp_path,
        env_config_override_forward_2026,
    ):
        """M4 PFR R1 fix + CR-SE-R2-M2 SEAL-eve R2 ADOPT v10: removed unused
        `btc_parquet_path` fixture from signature — engine resolves canonical
        parquet path internally via `_resolve_canonical_parquet_path()` per
        Phase 0 SEAL chain (engine.py:82).

        End-to-end smoke against REAL run_regime_holdout (no mock).
        Verifies engine extension + producer wiring + registry stamping work together
        on a real BTC parquet + real DSL fixture. Catches Phase 0 regressions that
        a mock-only test pyramid would miss."""
        _require_b_c_narrow_symbols()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        db_path = tmp_path / "test_lcb_e2e.db"
        candidate = {
            "hypothesis_hash": "e2e_real_hash_" + "a" * 50,
            "position": 32,
            "theme": "mean_reversion",
            "name": "bollinger_zscore_reversion",
            "wf_test_period_sharpe": 0.85,
        }

        # FIX 4 (manifest isolation): The _evaluate_one_candidate → run_regime_holdout
        # call chain does not thread manifest_dir, so it uses the on-disk production
        # manifest dir. To isolate this test from the mutable production manifest, the
        # stale manifest (produced by a prior registry snapshot) was deleted and the
        # current 33-factor registry will write a fresh one on first run. Future runs
        # find the fresh manifest matching the live registry hash → no drift. This is
        # the acknowledged approach for test isolation when manifest_dir cannot be
        # threaded (data/compiled_strategies/ is gitignored/local-only).
        with patch(
            "scripts.run_phase2c_evaluation_gate._load_dsl_from_response",
            return_value=dsl_bollinger_zscore_reversion,
        ), patch(
            "scripts.run_phase2c_evaluation_gate.enforce_corrected_engine_lineage",
            return_value="f112599abcdef",
        ):
            summary = _evaluate_one_candidate(
                candidate=candidate,
                head_sha="f112599abcdef",
                source_batch_id=BCNARROW_SOURCE_BATCH_ID,
                run_id=BCNARROW_PARENT_RUN_ID,
                output_dir=output_dir,
                regime_key=BCNARROW_REGIME_KEY,
                execution_config_path=Path(BCNARROW_EXECUTION_CONFIG_PATH),
                env_config_override=env_config_override_forward_2026,
                artifact_dir_root=artifact_dir_root,
                parent_run_id_override=BCNARROW_PARENT_RUN_ID,
                db_path=db_path,
            )

        artifact_dir = artifact_dir_root / candidate["hypothesis_hash"]
        rpb = artifact_dir / "returns_per_bar.parquet"
        assert rpb.exists() and rpb.stat().st_size > 0

        child_run_id = f"{BCNARROW_PARENT_RUN_ID}_{candidate['hypothesis_hash']}"
        # MR3-4 PFR R3 ADOPT (v4): explicit try/finally conn.close() (matches MR2-1 producer pattern)
        _conn = get_connection(db_path)
        try:
            child_row = get_run(_conn, child_run_id)
        finally:
            _conn.close()
        assert child_row is not None
        assert child_row.get("returns_per_bar_path") == "returns_per_bar.parquet"
        assert child_row.get("returns_per_bar_sha256") is not None
        assert len(child_row["returns_per_bar_sha256"]) == 64
        int(child_row["returns_per_bar_sha256"], 16)
        assert child_row.get("T_obs") is not None and child_row["T_obs"] > 0
        assert child_row.get("git_commit") == "eb1c87f"
        assert summary.get("returns_per_bar_path") == child_row["returns_per_bar_path"]
        assert summary.get("returns_per_bar_sha256") == child_row["returns_per_bar_sha256"]
        assert summary.get("T_obs") == child_row["T_obs"]

    # ----- Test 22 (M1): compute_moments return-keys API surface lock -----

    def test_compute_moments_return_keys_exactly(self):
        """M1 PFR R1 fix: lock engine.compute_moments API surface — exactly 3 keys
        (gamma3, gamma4, T_obs); NO mean/std/etc. Future engine refactor that
        adds/removes keys breaks producer's summary['gamma3']/['gamma4']/['T_obs']
        consumption — this test catches the drift at engine-test layer."""
        _require_b_c_narrow_symbols()
        import numpy as np
        result = compute_moments(np.array([0.01, 0.02, -0.01, 0.005, -0.003]))
        assert set(result.keys()) == {"gamma3", "gamma4", "T_obs"}

    # ----- Test 23 (MR2-4): parent.batch_id ≠ child.batch_id asymmetry lock -----

    def test_parent_batch_id_diverges_from_child_batch_id_per_spec_lock(self, tmp_path):
        """MR2-4 PFR R2 ADOPT (v3): anti-fragility test locking spec §3.2.3 line 117
        PUSHBACK-SOUND invariant.

        Spec §3.2.3 line 117 EXPLICIT LOCK: parent.batch_id = parent_run_id
        (= BCNARROW_PARENT_RUN_ID = 'phase4_forward_2026_15bps_v1_b_c_narrow').
        Engine writes child.batch_id = source_batch_id (= BCNARROW_SOURCE_BATCH_ID
        = 'phase2c_15_main_fire_combined' for cohort_a) via run_regime_holdout's
        batch_id positional kwarg per engine.py.

        Parent.batch_id ≠ child.batch_id by spec design. This test asserts the
        asymmetry explicitly so a future "consistency cleanup" PR cannot silently
        align them (which would deviate from spec §3.2.3 + break downstream Tier 6
        enumeration queries that depend on the asymmetric semantics)."""
        _require_b_c_narrow_symbols()
        db_path = tmp_path / "test_batch_id_asymmetry.db"

        # Setup: write parent row (via _finalize_batch_registry) + 1 child row
        # (hand-rolled per Test 9 M2 pattern; field-agnostic verification).
        cohort_metadata = {
            "execution_config_path": BCNARROW_EXECUTION_CONFIG_PATH,
            "execution_config_sha256": "a" * 64,
            "parquet_data_sha256": "b" * 64,
            "regime_key": BCNARROW_REGIME_KEY,
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "current_git_sha": "f112599",
            "effective_start": "2026-01-01T00:00:00Z",
            "initial_capital": 10_000.0,
            "fee_model": "effective_15bps_per_side",
        }
        _finalize_batch_registry(
            parent_run_id=BCNARROW_PARENT_RUN_ID,
            cohort_metadata=cohort_metadata,
            db_path=db_path,
        )
        # Hand-rolled child row matching engine's child write pattern (batch_id =
        # source_batch_id per Phase 0 + spec §3.2.1).
        conn = get_connection(db_path)
        try:
            with conn:
                insert_run(conn, {
                    "run_id": f"{BCNARROW_PARENT_RUN_ID}_test_child_hash",
                    "run_type": "regime_holdout",
                    "parent_run_id": BCNARROW_PARENT_RUN_ID,
                    "strategy_name": "test_strat",
                    "strategy_source": "b_c_narrow_recovery",
                    "git_commit": "eb1c87f",
                    "created_at_utc": "2026-05-27T00:00:00Z",
                    "fee_model": "effective_15bps_per_side",
                    "initial_capital": 10_000.0,
                    "batch_id": BCNARROW_SOURCE_BATCH_ID,  # ← child.batch_id per spec
                })
        finally:
            conn.close()

        # Verify the asymmetry
        with get_connection(db_path) as conn:
            parent_row = get_run(conn, BCNARROW_PARENT_RUN_ID)
            child_row = get_run(conn, f"{BCNARROW_PARENT_RUN_ID}_test_child_hash")

        assert parent_row["batch_id"] == BCNARROW_PARENT_RUN_ID, (
            f"MR2-4: spec §3.2.3 line 117 locks parent.batch_id = parent_run_id; "
            f"got parent.batch_id={parent_row['batch_id']!r}"
        )
        assert child_row["batch_id"] == BCNARROW_SOURCE_BATCH_ID, (
            f"MR2-4: per Phase 0 spec §3.2.1, child.batch_id = source_batch_id; "
            f"got child.batch_id={child_row['batch_id']!r}"
        )
        assert parent_row["batch_id"] != child_row["batch_id"], (
            f"MR2-4: parent.batch_id ≠ child.batch_id is spec §3.2.3 invariant. "
            f"If you see this assertion fail, someone aligned the two — that "
            f"deviates from spec (advisor R1 HIGH-5 PUSHBACK SOUND per spec re-read; "
            f"spec amend required at separate Charlie register before changing this lock)."
        )

    # ----- Test 24 (MR2-3): parent.git_commit == child.git_commit engine-consistency lock -----

    def test_parent_git_commit_matches_child_git_commit_engine_consistency(self, tmp_path):
        """MR2-3 PFR R2 ADOPT (v3) + MR3-3 PFR R3 ADOPT (v4): defensive test locking
        CB4 engine-consistency interpretation of spec §3.2.3 line 117 PLUS the parallel
        `current_git_sha = head_sha` interpretation per MR3-3.

        TWO spec-vs-implementation tensions locked by this single test:

        (1) git_commit COLUMN spec literal vs OVERRIDE implementation (MR2-3 v3):
        Spec §3.2.3 line 117 literal: 'git_commit (=506285b)'. Plan interprets the
        registry git_commit COLUMN as receiving engine OVERRIDE (engine_commit='eb1c87f')
        per engine.py:1328-1348, matching children's OVERRIDE stamp. Alternative
        interpretation (spec literal = '506285b' as B-C-narrow code state) would break
        parent-child join consistency on git_commit. NAMED-eligible-for-separate-spec-amend.

        (2) current_git_sha COLUMN spec literal vs head_sha derivation (MR3-3 v4):
        Spec §3.2.3 line 117 literal: 'current_git_sha (=506285b)'. Plan uses
        head_sha (fire-time HEAD per enforce_corrected_engine_lineage at wf_lineage.py:236-239)
        rather than spec literal '506285b' because:
          (a) spec literal reflects spec drafting staleness — spec was authored before
              Phase 0/1/2 SEAL commits that DO touch engine.py + tests/;
          (b) head_sha is the operationally correct value per registry convention
              (current_git_sha records fire-time provenance, not spec-authored intent);
          (c) Phase 0 SEAL commit f112599 + subsequent SEAL commits would diverge
              from spec literal '506285b'.
        Both tensions are NAMED-eligible-for-separate-spec-amend at separate Charlie
        register-event (anti-pre-emption preserved); this test locks both interpretations
        as plan invariants until/unless spec is amended.

        Assertion combined: parent.git_commit == child.git_commit == 'eb1c87f' (locks
        OVERRIDE interpretation) AND parent.current_git_sha != parent.git_commit (locks
        the distinct-fields invariant that head_sha-derivation produces)."""
        _require_b_c_narrow_symbols()
        db_path = tmp_path / "test_git_commit_consistency.db"

        # Setup: parent row via _finalize_batch_registry + 1 child row
        cohort_metadata = {
            "execution_config_path": BCNARROW_EXECUTION_CONFIG_PATH,
            "execution_config_sha256": "c" * 64,
            "parquet_data_sha256": "d" * 64,
            "regime_key": BCNARROW_REGIME_KEY,
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "current_git_sha": "f112599",  # fire-time HEAD (separate column)
            "effective_start": "2026-01-01T00:00:00Z",
            "initial_capital": 10_000.0,
            "fee_model": "effective_15bps_per_side",
        }
        _finalize_batch_registry(
            parent_run_id=BCNARROW_PARENT_RUN_ID,
            cohort_metadata=cohort_metadata,
            db_path=db_path,
        )
        # Child row with engine's OVERRIDE pattern: git_commit = engine_commit = "eb1c87f"
        conn = get_connection(db_path)
        try:
            with conn:
                insert_run(conn, {
                    "run_id": f"{BCNARROW_PARENT_RUN_ID}_test_child_consistency",
                    "run_type": "regime_holdout",
                    "parent_run_id": BCNARROW_PARENT_RUN_ID,
                    "strategy_name": "test_strat",
                    "strategy_source": "b_c_narrow_recovery",
                    "git_commit": "eb1c87f",  # engine OVERRIDE per engine.py:1328-1348
                    "created_at_utc": "2026-05-27T00:00:00Z",
                    "fee_model": "effective_15bps_per_side",
                    "initial_capital": 10_000.0,
                    "current_git_sha": "f112599",
                })
        finally:
            conn.close()

        # Verify engine-consistency: both rows have git_commit = "eb1c87f"
        with get_connection(db_path) as conn:
            parent_row = get_run(conn, BCNARROW_PARENT_RUN_ID)
            child_row = get_run(conn, f"{BCNARROW_PARENT_RUN_ID}_test_child_consistency")

        assert parent_row["git_commit"] == "eb1c87f", (
            f"MR2-3: parent.git_commit must equal CORRECTED_WF_ENGINE_COMMIT 'eb1c87f' "
            f"(CB4 engine-consistency interpretation of spec §3.2.3 line 117); "
            f"got {parent_row['git_commit']!r}"
        )
        assert child_row["git_commit"] == "eb1c87f", (
            f"MR2-3: child.git_commit must equal 'eb1c87f' (engine OVERRIDE per "
            f"engine.py:1328-1348); got {child_row['git_commit']!r}"
        )
        assert parent_row["git_commit"] == child_row["git_commit"], (
            f"MR2-3: parent.git_commit MUST equal child.git_commit for parent-child "
            f"join consistency. If this assertion fails, someone flipped parent.git_commit "
            f"to spec-literal '506285b' — that breaks join consistency. Spec literal "
            f"reading vs OVERRIDE interpretation is NAMED-eligible-for-separate-spec-amend "
            f"cycle (anti-pre-emption); plan locks engine-consistency interpretation here."
        )
        # current_git_sha is the separate column — should NOT equal git_commit
        assert parent_row["current_git_sha"] == "f112599"
        assert parent_row["current_git_sha"] != parent_row["git_commit"], (
            "MR2-3: parent.current_git_sha (fire-time HEAD) and parent.git_commit "
            "(engine_commit OVERRIDE) are DISTINCT fields per spec §2 disambiguation "
            "table. Aligning them silently is a regression."
        )

    # ----- Test 25 (CR5-B1 PFR R5 ADOPT v6): argparse rejects --dry-run + --force-rerun-existing -----

    @pytest.mark.parametrize("dry_run,force_rerun,should_pass", [
        (False, False, True),    # neither flag → OK
        (True, False, True),     # --dry-run alone → OK
        (False, True, True),     # --force-rerun-existing alone → OK
        (True, True, False),     # both flags → REJECTED at argparse
    ])
    def test_argparse_rejects_dry_run_plus_force_rerun_existing_combination(
        self, tmp_path, dry_run, force_rerun, should_pass
    ):
        """CR5-B1 PFR R5 ADOPT v6: --dry-run and --force-rerun-existing are MUTUALLY
        EXCLUSIVE. Combining them would cause W1 preflight (which runs BEFORE dry-run
        exit per CB1 ordering) to DELETE registry rows when force_rerun_existing=True,
        violating CB1 read-only invariant on dry-run path.

        Operator must consciously choose intent-validation (dry-run) vs destructive
        cleanup (force-rerun-existing), never both. Argparse rejects the combination
        at parse-time before any state mutation.

        Codex R5 BLOCKING-1 catch (saturation-expectation Mode A bias: Advisor missed
        this dimension via cycle-saturation prior); B2 reverse-direction value reaffirmed.
        """
        _require_b_c_narrow_symbols()
        argv = [
            "run_phase2c_evaluation_gate.py",
            "--source-batch-id", BCNARROW_SOURCE_BATCH_ID,
            "--candidate-hashes", "test_hash_",
            "--run-id", BCNARROW_PARENT_RUN_ID,
            "--regime-key", BCNARROW_REGIME_KEY,
            "--execution-config", BCNARROW_EXECUTION_CONFIG_PATH,
            "--output-root", str(tmp_path),
            "--enable-b-c-narrow-recovery",
        ]
        if dry_run:
            argv.append("--dry-run")
        if force_rerun:
            argv.append("--force-rerun-existing")

        # CR6-B1 PFR R6 ADOPT (v7): no-op mock all downstream side-effects so should_pass
        # cases reach the "assert e.code != 2" check without uncaught FileNotFoundError
        # from W3 archive PRE-flight (canonical absent at tmp_path) or W4 forward_window
        # capture (parquet absent) or W5 candidate loop (engine not runnable). Test 25
        # specifically targets argparse mutex surface — does NOT test recovery flow.
        # Downstream surfaces mocked: archive (W3) + forward_window capture (W4) +
        # candidate evaluator (W5) + aggregate CSV write + aggregate JSON write +
        # finalize POST-fire (W6).
        with patch(
            "scripts.run_phase2c_evaluation_gate._load_corrected_candidates",
            return_value=[{"hypothesis_hash": "test_hash_" + "a"*53, "position": 0,
                           "theme": "test", "name": "test", "wf_test_period_sharpe": 0.5}],
        ), patch(
            "scripts.run_phase2c_evaluation_gate.enforce_corrected_engine_lineage",
            return_value="f112599abcdef",
        ), patch(
            "scripts.run_phase2c_evaluation_gate.DEFAULT_DB_PATH",
            tmp_path / "test_argparse_guard.db",
        ), patch(
            # CR6-B1: no-op W3 archive PRE-flight (canonical absent at tmp_path → would FileNotFoundError)
            "scripts.run_phase2c_evaluation_gate._archive_canonical_pre_flight",
            return_value=None,
        ), patch(
            # CR6-B1: no-op W4 forward_window capture (real parquet read; not relevant to argparse test)
            "scripts.run_phase2c_evaluation_gate._capture_phase4_forward_window_metadata",
            return_value={
                "forward_window_start_utc": "2026-01-01T00:00:00Z",
                "forward_window_end_utc": "2026-04-16T07:00:00Z",
                "forward_bar_count": 2528,
                "parquet_data_sha256": "x" * 64,
                "forward_end_date_iso": "2026-04-16",
            },
        ), patch(
            # CR6-B1: no-op env_config override builder
            "scripts.run_phase2c_evaluation_gate._build_phase4_env_config_override",
            return_value={"evaluation_regimes": {"forward_2026": {"end": "2026-04-16"}}},
        ), patch(
            # CR6-B1: no-op W5 candidate evaluator (real engine not runnable in unit-test scope)
            "scripts.run_phase2c_evaluation_gate._evaluate_one_candidate",
            return_value={
                "hypothesis_hash": "test_hash_" + "a"*53, "position": 0,
                "theme": "test", "name": "test", "wf_test_period_sharpe": 0.5,
                "lifecycle_state": "holdout_passed", "holdout_passed": True,
                "holdout_metrics": {"sharpe_ratio": 1.0, "max_drawdown": -0.05,
                                     "total_return": 0.1, "total_trades": 10},
                "passing_criteria": {}, "gate_pass_per_criterion": {},
                "wall_clock_seconds": 0.0, "error_message": None,
            },
        ), patch(
            # CR6-B1: no-op CSV + aggregate JSON writers (filesystem side effects)
            "scripts.run_phase2c_evaluation_gate._write_aggregate_csv",
            return_value=None,
        ), patch(
            "scripts.run_phase2c_evaluation_gate._write_aggregate_summary",
            return_value=None,
        ), patch(
            # CR6-B1: no-op W6 POST-fire finalize (registry write)
            "scripts.run_phase2c_evaluation_gate._finalize_batch_registry",
            return_value=None,
        ), patch(
            "scripts.run_phase2c_evaluation_gate._finalize_batch_registry_preflight_or_raise",
            return_value=None,
        ), patch("sys.argv", argv):
            from scripts.run_phase2c_evaluation_gate import main
            if should_pass:
                # No SystemExit on valid combinations (may exit normally with rc=0 for
                # dry-run, or proceed); we don't assert specific return code here.
                try:
                    main()
                except SystemExit as e:
                    # argparse SystemExit (e.code == 2) would be UNEXPECTED here;
                    # other exits (rc=0 dry-run, rc=1 mock-induced) are OK.
                    assert e.code != 2, (
                        f"CR5-B1: dry_run={dry_run} force_rerun={force_rerun} "
                        f"should NOT trigger argparse rejection (rc=2); got rc={e.code}"
                    )
                # No mutation expected on dry_run path (existing behavior; CR5-B1
                # ensures the combination itself is rejected, not the standalone flags).
            else:
                # both flags set → argparse REJECTS with SystemExit(2)
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 2, (
                    f"CR5-B1: --dry-run + --force-rerun-existing combination must "
                    f"be REJECTED at argparse (SystemExit code 2); got code={exc_info.value.code}"
                )
                # No DB mutation should have occurred
                db_path = tmp_path / "test_argparse_guard.db"
                assert not db_path.exists(), (
                    f"CR5-B1: argparse rejection must fire BEFORE any DB I/O; "
                    f"db_path {db_path} unexpectedly exists"
                )

    # ----- Test 26 (CR-SE-R2-H1 SEAL-eve R2 ADOPT v10): main() entrypoint regression test
    #       for CR-SE-H1 v9 W1a/W1b split — state-inconsistency window prevention -----

    def test_w1_reorder_force_rerun_existing_without_force_leaves_registry_intact(
        self, tmp_path, monkeypatch
    ):
        """CR-SE-R2-H1 SEAL-eve R2 ADOPT v10: main() entrypoint regression test for
        CR-SE-H1 v9 W1a/W1b split state-inconsistency-window fix.

        Pre-v9 behavior: W1 destructive DELETE ran BEFORE _check_overwrite_protection.
        Operator passing --force-rerun-existing WITHOUT --force on non-empty run_dir
        would: (1) DELETE registry rows; (2) abort at overwrite gate. State after
        abort: DB cleaned (operator-intended) + filesystem dirty (prior partial state).

        v9 CR-SE-H1 fix: split W1 into W1a (read-only BEFORE _check_overwrite_protection)
        + W1b (destructive DELETE AFTER). If overwrite-protection refuses, W1b never
        executes — operator's state remains intact.

        This test exercises main() end-to-end with the exact scenario CR-SE-H1
        addresses: setup pre-existing parent + child rows + non-empty run_dir +
        --force-rerun-existing WITHOUT --force; assert main() returns overwrite-
        protection rc != 0; assert registry rows REMAIN (NOT deleted); assert
        _archive_canonical_pre_flight was NOT called.
        """
        _require_b_c_narrow_symbols()
        output_root = tmp_path / "output"
        output_root.mkdir()
        canonical = output_root / "phase4_forward_2026_15bps_v1"
        canonical.mkdir()
        (canonical / "marker.json").write_text('{"pre_canonical": true}')
        # Pre-populate non-empty run_dir (sibling dir at BCNARROW_PARENT_RUN_ID name
        # per producer convention; scripts:908 `run_dir = output_root / run_id`).
        run_dir = output_root / BCNARROW_PARENT_RUN_ID
        run_dir.mkdir()
        (run_dir / "partial_state.json").write_text('{"prior_failed_run": true}')
        db_path = tmp_path / "test_w1_reorder.db"
        # CR-SE-R3-L1 SEAL-eve R3 ADOPT v11 DEFENSIVE NOTE: this monkeypatch on
        # DEFAULT_DB_PATH is currently UNUSED in this test's actual flow — W1a's
        # `if not args.force_rerun_existing` evaluates False under --force-rerun-existing,
        # so W1a is SKIPPED entirely; _check_overwrite_protection aborts before W1b
        # could query DB. The monkeypatch is retained DEFENSIVELY against future
        # W1a behavior change that DOES query DB (ensures hermetic isolation if so).
        monkeypatch.setattr("scripts.run_phase2c_evaluation_gate.DEFAULT_DB_PATH", db_path)

        # Pre-populate registry with parent + child rows (simulating prior partial fire)
        conn = get_connection(db_path)
        try:
            with conn:
                create_table(conn)
                insert_run(conn, {
                    "run_id": BCNARROW_PARENT_RUN_ID,
                    "run_type": "batch_summary",
                    "parent_run_id": None,
                    "strategy_name": "cohort_summary",
                    "strategy_source": "b_c_narrow_recovery",
                    "git_commit": "eb1c87f",
                    "created_at_utc": "2026-05-26T00:00:00Z",
                    "fee_model": "effective_15bps_per_side",
                    "initial_capital": 10_000.0,
                })
                insert_run(conn, {
                    "run_id": f"{BCNARROW_PARENT_RUN_ID}_partial_child_test",
                    "run_type": "regime_holdout",
                    "parent_run_id": BCNARROW_PARENT_RUN_ID,
                    "strategy_name": "test_strat",
                    "strategy_source": "b_c_narrow_recovery",
                    "git_commit": "eb1c87f",
                    "created_at_utc": "2026-05-26T00:00:00Z",
                    "fee_model": "effective_15bps_per_side",
                    "initial_capital": 10_000.0,
                })
        finally:
            conn.close()

        # Track if _archive_canonical_pre_flight was called
        archive_called = []

        with patch(
            "scripts.run_phase2c_evaluation_gate._load_corrected_candidates",
            return_value=[{"hypothesis_hash": "test_hash_" + "a"*53, "position": 0,
                           "theme": "test", "name": "test", "wf_test_period_sharpe": 0.5}],
        ), patch(
            "scripts.run_phase2c_evaluation_gate.enforce_corrected_engine_lineage",
            return_value="f112599abcdef",
        ), patch(
            "scripts.run_phase2c_evaluation_gate._archive_canonical_pre_flight",
            side_effect=lambda **kw: archive_called.append(kw),
        ), patch("sys.argv", [
            "run_phase2c_evaluation_gate.py",
            "--source-batch-id", BCNARROW_SOURCE_BATCH_ID,
            "--candidate-hashes", "test_hash_",
            "--run-id", BCNARROW_PARENT_RUN_ID,
            "--regime-key", BCNARROW_REGIME_KEY,
            "--execution-config", BCNARROW_EXECUTION_CONFIG_PATH,
            "--output-root", str(output_root),
            "--enable-b-c-narrow-recovery",
            "--force-rerun-existing",
            # NOTE: --force INTENTIONALLY OMITTED to exercise CR-SE-H1 v9 fix scenario
        ]):
            from scripts.run_phase2c_evaluation_gate import main
            rc = main()

        # Assert: main() returned overwrite-protection refusal rc (typically 1)
        assert rc == 1, (
            f"CR-SE-R2-H1: main() should return _check_overwrite_protection refusal "
            f"rc=1 on non-empty run_dir without --force; got rc={rc}"
        )

        # Assert: archive was NOT called (W3 destructive op refused at overwrite gate)
        assert len(archive_called) == 0, (
            f"CR-SE-R2-H1: _archive_canonical_pre_flight must NOT be called when "
            f"_check_overwrite_protection refuses; got {len(archive_called)} call(s)"
        )

        # Assert: registry rows REMAIN (CR-SE-H1 W1b never executed — operator state intact)
        with get_connection(db_path) as conn:
            n_parent = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE run_id = ?", (BCNARROW_PARENT_RUN_ID,)
            ).fetchone()[0]
            n_children = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE parent_run_id = ?", (BCNARROW_PARENT_RUN_ID,)
            ).fetchone()[0]
        assert n_parent == 1, (
            f"CR-SE-R2-H1: parent registry row must REMAIN (W1b never executed since "
            f"overwrite gate refused); got n_parent={n_parent}"
        )
        assert n_children == 1, (
            f"CR-SE-R2-H1: child registry row must REMAIN (W1b never executed); "
            f"got n_children={n_children}"
        )

        # Assert: canonical artifact untouched
        assert canonical.exists()
        assert (canonical / "marker.json").exists()
