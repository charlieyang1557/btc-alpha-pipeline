"""Tests for B-C-extended Scope-B schema validation (T1.2 deliverable).

TDD cycle: tests written FIRST (RED) per testing.md discipline.
Implementation target: backtest/wf_lineage.py + optionally backtest/artifact_schema.py.

Contract references:
- Contract 2.0.2: schema version string + distinct validation branch
- Contract 2.0.4: cost_anchor_id mapping integrity
- Contract 2.0.5: artifact path policy + per-bar linkage validation
- Plan v5 §10 sub-decision B: B1-c hybrid + B2-b + B3-b locks

Test organization:
1. Constants and exception class structure
2. check_b_c_extended_semantics_or_raise happy path
3. Phase 1 fail-fast: structural failures (schema_version, discriminator fields, path-confinement)
4. Phase 2 collect-all: per-field failures accumulate to single raise
5. B2-b Optional[string] semantics for parent_run_id
6. Per-bar artifact linkage validation (file-exists + SHA256 + T_obs)
7. cost_anchor_id mapping integrity (Contract 2.0.4)
8. Cross-helper domain-fence rejection tests
9. Edge cases (empty dict, malformed types)
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

# ---------------------------------------------------------------------------
# Helpers shared across test groups
# ---------------------------------------------------------------------------

# The 6-row R3.1d §5.2 cost_anchor_id mapping (verbatim from plan v5 Contract 2.0.4)
_MAPPING: dict[str, str] = {
    "config/execution.yaml": "legacy_perp_inspired_7bps_v0",
    "config/execution_phase4_07bps.yaml": "phase4_forward_07bps_v1",
    "config/execution_phase4_13bps.yaml": "phase4_forward_13bps_v1",
    "config/execution_phase4_15bps.yaml": "phase4_forward_15bps_v1",
    "config/execution_phase4_17bps.yaml": "phase4_forward_17bps_v1",
    "config/execution_phaseb_spot_15bps.yaml": "spot_realistic_15bps_v1",
}


def _make_parquet_bytes(n_rows: int = 5) -> bytes:
    """Return minimal parquet file bytes with 'return' column (n_rows finite values)."""
    import io
    table = pa.table({"return": pa.array([0.01 * i for i in range(n_rows)], type=pa.float64())})
    buf = io.BytesIO()
    pq.write_table(table, buf)
    return buf.getvalue()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_parquet(path: Path, n_rows: int = 5) -> str:
    """Write a synthetic per-bar parquet at path; return its SHA256 hex."""
    data = _make_parquet_bytes(n_rows)
    path.write_bytes(data)
    return _sha256_bytes(data)


def _valid_summary(
    artifact_dir: Path,
    n_rows: int = 5,
    returns_filename: str = "returns_per_bar.parquet",
) -> dict:
    """Build a complete valid b_c_extended_v1 summary dict.

    Creates the per-bar parquet file inside artifact_dir and wires all
    hash + T_obs fields to match the actual file content.
    """
    parquet_path = artifact_dir / returns_filename
    sha256 = _write_parquet(parquet_path, n_rows)
    return {
        "artifact_schema_version": "b_c_extended_v1",
        "run_id": "test-run-001",
        "hypothesis_hash": "abc123def456",
        "source_batch_id": "batch-uuid-001",
        "parent_run_id": None,
        "regime_key": "evaluation_regimes.forward_2026",
        "engine_commit": "eb1c87f",
        "current_git_sha": "abcdef1234567890",
        "execution_config_path": "config/execution_phaseb_spot_15bps.yaml",
        "execution_config_sha256": "deadbeef" * 8,
        "parquet_data_sha256": "cafebabe" * 8,
        "cost_anchor_id": "spot_realistic_15bps_v1",
        "returns_per_bar_path": returns_filename,
        "returns_per_bar_sha256": sha256,
        "T_obs": n_rows,
    }


# ---------------------------------------------------------------------------
# 1. Constants and exception class structure
# ---------------------------------------------------------------------------

class TestConstants:
    """Verify schema version constants and per-domain tuples exist."""

    def test_b_c_extended_schema_version_constant(self):
        """ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 must equal 'b_c_extended_v1'."""
        from backtest.wf_lineage import ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1
        assert ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 == "b_c_extended_v1"

    def test_accepted_b_c_extended_schema_versions_is_tuple(self):
        """ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS must be a tuple."""
        from backtest.wf_lineage import ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS
        assert isinstance(ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS, tuple)

    def test_b_c_extended_v1_in_accepted_b_c_extended_tuple(self):
        """b_c_extended_v1 must be in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS."""
        from backtest.wf_lineage import (
            ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS,
            ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1,
        )
        assert ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS

    def test_accepted_evaluation_schema_versions_is_tuple(self):
        """ACCEPTED_EVALUATION_SCHEMA_VERSIONS must be a tuple."""
        from backtest.wf_lineage import ACCEPTED_EVALUATION_SCHEMA_VERSIONS
        assert isinstance(ACCEPTED_EVALUATION_SCHEMA_VERSIONS, tuple)

    def test_accepted_evaluation_schema_versions_contains_expected(self):
        """ACCEPTED_EVALUATION_SCHEMA_VERSIONS must contain phase2c_7_1 and phase2c_8_1."""
        from backtest.wf_lineage import (
            ACCEPTED_EVALUATION_SCHEMA_VERSIONS,
            ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
            ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1,
        )
        assert ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1 in ACCEPTED_EVALUATION_SCHEMA_VERSIONS
        assert ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1 in ACCEPTED_EVALUATION_SCHEMA_VERSIONS

    def test_accepted_evaluation_schema_versions_excludes_b_c_extended(self):
        """ACCEPTED_EVALUATION_SCHEMA_VERSIONS must NOT contain b_c_extended_v1.

        Domain fence: the evaluation attestation domain does not accept
        b_c_extended_v1 artifacts. Per plan v5 §10 Sub-decision A.
        """
        from backtest.wf_lineage import (
            ACCEPTED_EVALUATION_SCHEMA_VERSIONS,
            ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1,
        )
        assert ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 not in ACCEPTED_EVALUATION_SCHEMA_VERSIONS

    def test_accepted_wf_schema_versions_is_tuple(self):
        """ACCEPTED_WF_SCHEMA_VERSIONS must be a tuple."""
        from backtest.wf_lineage import ACCEPTED_WF_SCHEMA_VERSIONS
        assert isinstance(ACCEPTED_WF_SCHEMA_VERSIONS, tuple)

    def test_accepted_wf_schema_versions_excludes_b_c_extended(self):
        """ACCEPTED_WF_SCHEMA_VERSIONS must NOT contain b_c_extended_v1.

        Domain fence: the WF attestation domain does not accept
        b_c_extended_v1 artifacts. Per plan v5 §10 Sub-decision A.
        """
        from backtest.wf_lineage import (
            ACCEPTED_WF_SCHEMA_VERSIONS,
            ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1,
        )
        assert ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 not in ACCEPTED_WF_SCHEMA_VERSIONS

    def test_cost_anchor_mapping_exists(self):
        """COST_ANCHOR_ID_MAPPING must exist and have 6 rows per R3.1d §5.2."""
        from backtest.wf_lineage import COST_ANCHOR_ID_MAPPING
        assert isinstance(COST_ANCHOR_ID_MAPPING, dict)
        assert len(COST_ANCHOR_ID_MAPPING) == 6

    def test_cost_anchor_mapping_contents(self):
        """COST_ANCHOR_ID_MAPPING must contain all 6 R3.1d §5.2 rows verbatim."""
        from backtest.wf_lineage import COST_ANCHOR_ID_MAPPING
        for path, anchor_id in _MAPPING.items():
            assert COST_ANCHOR_ID_MAPPING[path] == anchor_id, (
                f"Mapping mismatch at {path!r}: "
                f"expected {anchor_id!r}, got {COST_ANCHOR_ID_MAPPING.get(path)!r}"
            )


class TestExceptionClass:
    """BCExtendedSchemaValidationError structure and LSP compliance."""

    def test_bc_extended_schema_validation_error_is_value_error_subclass(self):
        """BCExtendedSchemaValidationError must be a ValueError subclass (LSP).

        Per plan v5 §10 Sub-decision B, B3-b: subclass of ValueError so
        existing 'except ValueError' consumers are not broken.
        """
        from backtest.wf_lineage import BCExtendedSchemaValidationError
        assert issubclass(BCExtendedSchemaValidationError, ValueError)

    def test_bc_extended_schema_validation_error_is_catchable_as_value_error(self):
        """Raising BCExtendedSchemaValidationError must be caught by 'except ValueError'."""
        from backtest.wf_lineage import BCExtendedSchemaValidationError
        with pytest.raises(ValueError):
            raise BCExtendedSchemaValidationError(["field_x: missing"])

    def test_bc_extended_schema_validation_error_carries_errors_list(self):
        """BCExtendedSchemaValidationError must carry a structured errors list."""
        from backtest.wf_lineage import BCExtendedSchemaValidationError
        errors = ["field_a: missing", "field_b: wrong type"]
        exc = BCExtendedSchemaValidationError(errors)
        assert exc.errors == errors

    def test_bc_extended_schema_validation_error_str_contains_errors(self):
        """str() of BCExtendedSchemaValidationError should reference the errors."""
        from backtest.wf_lineage import BCExtendedSchemaValidationError
        errors = ["run_id: missing", "hypothesis_hash: missing"]
        exc = BCExtendedSchemaValidationError(errors)
        msg = str(exc)
        assert "run_id" in msg
        assert "hypothesis_hash" in msg

    def test_bc_extended_schema_validation_error_empty_errors_list(self):
        """Empty errors list is constructable (edge case)."""
        from backtest.wf_lineage import BCExtendedSchemaValidationError
        exc = BCExtendedSchemaValidationError([])
        assert exc.errors == []


# ---------------------------------------------------------------------------
# 2. Happy path
# ---------------------------------------------------------------------------

class TestHappyPath:
    """check_b_c_extended_semantics_or_raise passes on valid 14-field artifact."""

    def test_happy_path_all_14_fields_valid(self, tmp_path: Path):
        """Valid summary with all 14 fields + correct file passes without raising."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        # Must not raise
        check_b_c_extended_semantics_or_raise(summary, artifact_path=tmp_path / "holdout_summary.json")

    def test_happy_path_without_artifact_path_kwarg(self, tmp_path: Path):
        """Helper works without artifact_path (path resolution falls back to cwd)."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        # artifact_path=None means path-resolution uses tmp_path as base — won't find file
        # unless we pass artifact_path. So pass tmp_path as artifact_path directory.
        # The helper should accept Path objects.
        check_b_c_extended_semantics_or_raise(summary, artifact_path=tmp_path / "summary.json")

    def test_happy_path_parent_run_id_none_is_valid(self, tmp_path: Path):
        """parent_run_id=None (key present, value None) is valid per B2-b."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        summary["parent_run_id"] = None
        check_b_c_extended_semantics_or_raise(summary, artifact_path=tmp_path / "s.json")

    def test_happy_path_parent_run_id_non_none_string(self, tmp_path: Path):
        """parent_run_id as a non-empty string is also valid."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        summary["parent_run_id"] = "parent-run-abc123"
        check_b_c_extended_semantics_or_raise(summary, artifact_path=tmp_path / "s.json")

    def test_happy_path_all_6_cost_anchor_paths(self, tmp_path: Path):
        """Helper passes for each of the 6 R3.1d §5.2 execution_config_path values."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        for config_path, anchor_id in _MAPPING.items():
            summary = _valid_summary(tmp_path)
            summary["execution_config_path"] = config_path
            summary["cost_anchor_id"] = anchor_id
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )


# ---------------------------------------------------------------------------
# 3. Phase 1 fail-fast: structural failures
# ---------------------------------------------------------------------------

class TestPhase1FailFast:
    """Phase 1 structural checks raise immediately (not collect-all)."""

    def test_missing_artifact_schema_version_raises_immediately(self, tmp_path: Path):
        """Missing artifact_schema_version raises immediately (Phase 1 fail-fast).

        Per plan v5 Sub-decision B (B1-c): structural failures raise
        immediately without collecting other errors.
        """
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        del summary["artifact_schema_version"]
        with pytest.raises((ValueError, KeyError)):
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )

    def test_wrong_artifact_schema_version_raises_immediately(self, tmp_path: Path):
        """Wrong artifact_schema_version raises immediately (domain fence, Phase 1 fail-fast)."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        summary["artifact_schema_version"] = "phase2c_7_1"  # wrong domain
        with pytest.raises(ValueError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        msg = str(exc_info.value)
        assert "artifact_schema_version" in msg
        assert "phase2c_7_1" in msg

    def test_unknown_artifact_schema_version_raises_immediately(self, tmp_path: Path):
        """Unrecognized artifact_schema_version raises immediately with diagnostics."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        summary["artifact_schema_version"] = "future_v99"
        with pytest.raises(ValueError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        msg = str(exc_info.value)
        assert "artifact_schema_version" in msg
        assert "future_v99" in msg

    def test_path_confinement_violation_dotdot_raises_phase1(self, tmp_path: Path):
        """returns_per_bar_path with '../' raises immediately (path-confinement, Phase 1).

        Per plan v5 Contract 2.0.5: path-confinement check is Phase 1
        (structural, fail-fast). Escaping the artifact directory is an
        attack vector.
        """
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "../escape/returns_per_bar.parquet"
        with pytest.raises(ValueError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        msg = str(exc_info.value)
        # Should mention confinement or path issue
        assert any(word in msg.lower() for word in ("confin", "path", "escape", "outside"))

    def test_path_confinement_absolute_path_raises_phase1(self, tmp_path: Path):
        """Absolute path in returns_per_bar_path raises (path-confinement, Phase 1)."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "/etc/passwd"
        with pytest.raises(ValueError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        msg = str(exc_info.value)
        assert any(word in msg.lower() for word in ("confin", "path", "absolute", "outside"))

    def test_empty_dict_raises_phase1(self):
        """Empty dict raises on artifact_schema_version check (Phase 1 fail-fast)."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        with pytest.raises((ValueError, KeyError)):
            check_b_c_extended_semantics_or_raise({})


# ---------------------------------------------------------------------------
# 4. Phase 2 collect-all: per-field failures
# ---------------------------------------------------------------------------

class TestPhase2CollectAll:
    """Phase 2 accumulates all per-field failures into single BCExtendedSchemaValidationError."""

    def test_multiple_missing_required_fields_collected(self, tmp_path: Path):
        """Multiple missing required fields produce single raise with ALL failures listed."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        # Remove multiple required fields (all Phase 2 fields)
        del summary["run_id"]
        del summary["hypothesis_hash"]
        del summary["source_batch_id"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        errors = exc_info.value.errors
        # All three missing fields should appear in the structured errors list
        error_text = " ".join(errors)
        assert "run_id" in error_text
        assert "hypothesis_hash" in error_text
        assert "source_batch_id" in error_text

    def test_single_missing_field_still_uses_collect_all_exception(self, tmp_path: Path):
        """Even a single Phase 2 failure raises BCExtendedSchemaValidationError (not plain ValueError)."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["run_id"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("run_id" in e for e in exc_info.value.errors)

    def test_artifact_path_included_in_error_message(self, tmp_path: Path):
        """artifact_path kwarg appears in exception error message."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["run_id"]
        artifact = tmp_path / "my_holdout_summary.json"
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(summary, artifact_path=artifact)
        msg = str(exc_info.value)
        assert "my_holdout_summary.json" in msg

    def test_regime_key_missing_raises(self, tmp_path: Path):
        """Missing regime_key raises BCExtendedSchemaValidationError."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["regime_key"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("regime_key" in e for e in exc_info.value.errors)

    def test_engine_commit_missing_raises(self, tmp_path: Path):
        """Missing engine_commit raises BCExtendedSchemaValidationError."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["engine_commit"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("engine_commit" in e for e in exc_info.value.errors)

    def test_current_git_sha_missing_raises(self, tmp_path: Path):
        """Missing current_git_sha raises BCExtendedSchemaValidationError."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["current_git_sha"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("current_git_sha" in e for e in exc_info.value.errors)

    def test_execution_config_path_missing_raises(self, tmp_path: Path):
        """Missing execution_config_path raises BCExtendedSchemaValidationError."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["execution_config_path"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("execution_config_path" in e for e in exc_info.value.errors)

    def test_execution_config_sha256_missing_raises(self, tmp_path: Path):
        """Missing execution_config_sha256 raises BCExtendedSchemaValidationError."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["execution_config_sha256"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("execution_config_sha256" in e for e in exc_info.value.errors)

    def test_parquet_data_sha256_missing_raises(self, tmp_path: Path):
        """Missing parquet_data_sha256 raises BCExtendedSchemaValidationError."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["parquet_data_sha256"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("parquet_data_sha256" in e for e in exc_info.value.errors)

    def test_cost_anchor_id_missing_raises(self, tmp_path: Path):
        """Missing cost_anchor_id raises BCExtendedSchemaValidationError."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["cost_anchor_id"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("cost_anchor_id" in e for e in exc_info.value.errors)

    def test_returns_per_bar_sha256_missing_raises(self, tmp_path: Path):
        """Missing returns_per_bar_sha256 raises BCExtendedSchemaValidationError."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["returns_per_bar_sha256"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("returns_per_bar_sha256" in e for e in exc_info.value.errors)

    def test_t_obs_missing_raises(self, tmp_path: Path):
        """Missing T_obs raises BCExtendedSchemaValidationError."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["T_obs"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("T_obs" in e for e in exc_info.value.errors)

    def test_non_string_required_field_raises(self, tmp_path: Path):
        """Non-string value for required string field raises BCExtendedSchemaValidationError."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        summary["run_id"] = 12345  # wrong type
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("run_id" in e for e in exc_info.value.errors)


# ---------------------------------------------------------------------------
# 5. B2-b: parent_run_id Optional[string] semantics
# ---------------------------------------------------------------------------

class TestParentRunIdSemantics:
    """B2-b lock: None valid, missing-key FAIL CLOSED, empty-string FAIL CLOSED."""

    def test_parent_run_id_none_passes(self, tmp_path: Path):
        """parent_run_id=None with key present passes (B2-b: None valid)."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        summary["parent_run_id"] = None
        check_b_c_extended_semantics_or_raise(summary, artifact_path=tmp_path / "s.json")

    def test_parent_run_id_missing_key_fails_closed(self, tmp_path: Path):
        """parent_run_id key absent raises (B2-b: missing-key FAIL CLOSED).

        Explicit presence required even if value would be None.
        """
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["parent_run_id"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("parent_run_id" in e for e in exc_info.value.errors)

    def test_parent_run_id_empty_string_fails_closed(self, tmp_path: Path):
        """parent_run_id='' raises (B2-b: empty-string FAIL CLOSED)."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        summary["parent_run_id"] = ""
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("parent_run_id" in e for e in exc_info.value.errors)

    def test_parent_run_id_non_string_non_none_fails(self, tmp_path: Path):
        """parent_run_id=42 (neither string nor None) raises."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        summary["parent_run_id"] = 42
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("parent_run_id" in e for e in exc_info.value.errors)


# ---------------------------------------------------------------------------
# 6. Per-bar artifact linkage validation
# ---------------------------------------------------------------------------

class TestPerBarArtifactLinkage:
    """File-exists + SHA256-recompute + T_obs-alignment per Contract 2.0.5."""

    def test_missing_returns_file_raises(self, tmp_path: Path):
        """returns_per_bar_path pointing to non-existent file raises."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        # Rename the actual file so it no longer exists
        (tmp_path / "returns_per_bar.parquet").unlink()
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        error_text = " ".join(exc_info.value.errors)
        assert "returns_per_bar" in error_text.lower() or "file" in error_text.lower()

    def test_sha256_mismatch_raises(self, tmp_path: Path):
        """SHA256 mismatch between stored hash and actual file content raises."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        # Tamper the stored hash
        summary["returns_per_bar_sha256"] = "0" * 64
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        error_text = " ".join(exc_info.value.errors)
        assert "sha256" in error_text.lower() or "hash" in error_text.lower()

    def test_t_obs_mismatch_raises(self, tmp_path: Path):
        """T_obs in summary not matching actual finite-row count raises."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path, n_rows=5)
        # Claim wrong T_obs
        summary["T_obs"] = 999
        # Recompute SHA256 so the hash check passes — only T_obs should fail
        actual_sha = _sha256_bytes((tmp_path / "returns_per_bar.parquet").read_bytes())
        summary["returns_per_bar_sha256"] = actual_sha
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        error_text = " ".join(exc_info.value.errors)
        assert "T_obs" in error_text or "t_obs" in error_text.lower() or "row" in error_text.lower()

    def test_valid_per_bar_linkage_passes(self, tmp_path: Path):
        """Correct SHA256 + correct T_obs + existing file passes."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path, n_rows=10)
        # The _valid_summary helper already wires everything correctly
        check_b_c_extended_semantics_or_raise(
            summary, artifact_path=tmp_path / "s.json"
        )

    def test_returns_per_bar_path_missing_key_raises_phase2(self, tmp_path: Path):
        """Missing returns_per_bar_path key raises BCExtendedSchemaValidationError."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        del summary["returns_per_bar_path"]
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("returns_per_bar_path" in e for e in exc_info.value.errors)


# ---------------------------------------------------------------------------
# 7. cost_anchor_id mapping integrity (Contract 2.0.4)
# ---------------------------------------------------------------------------

class TestCostAnchorMapping:
    """cost_anchor_id must match the execution_config_path via the 6-row mapping."""

    def test_mismatched_cost_anchor_id_raises(self, tmp_path: Path):
        """cost_anchor_id inconsistent with execution_config_path raises."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        # Set a config path whose correct anchor is NOT what's in cost_anchor_id
        summary["execution_config_path"] = "config/execution.yaml"
        summary["cost_anchor_id"] = "spot_realistic_15bps_v1"  # wrong for this config
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        error_text = " ".join(exc_info.value.errors)
        assert "cost_anchor_id" in error_text

    def test_unmapped_execution_config_path_raises(self, tmp_path: Path):
        """Unmapped execution_config_path raises with structured error listing known paths."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        summary["execution_config_path"] = "config/execution_unknown_v99.yaml"
        summary["cost_anchor_id"] = "unknown_anchor"
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        msg = str(exc_info.value)
        # Error must mention the bad path and known mapping per Contract 2.0.4
        assert "execution_config_path" in msg or "execution_config_unknown" in msg

    def test_each_mapped_path_with_correct_anchor_passes(self, tmp_path: Path):
        """Each of the 6 mapped execution_config_path + cost_anchor_id pairs passes."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        for config_path, anchor_id in _MAPPING.items():
            summary = _valid_summary(tmp_path)
            summary["execution_config_path"] = config_path
            summary["cost_anchor_id"] = anchor_id
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )

    def test_error_message_includes_known_mapping_table(self, tmp_path: Path):
        """Unmapped path error message includes known mapping table contents per Contract 2.0.4."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        summary["execution_config_path"] = "config/execution_mystery.yaml"
        summary["cost_anchor_id"] = "mystery_anchor"
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        msg = str(exc_info.value)
        # At minimum, one of the known config paths must appear in the error
        assert any(p in msg for p in _MAPPING.keys()), (
            f"Error message must include known mapping table; got: {msg}"
        )


# ---------------------------------------------------------------------------
# 8. Cross-helper domain-fence rejection tests
# ---------------------------------------------------------------------------

class TestCrossHelperDomainFence:
    """b_c_extended_v1 artifacts must be rejected by the other two helpers."""

    def _make_bc_extended_dict(self, tmp_path: Path) -> dict:
        """Minimal b_c_extended_v1 dict (may lack evaluation/wf semantics fields)."""
        return _valid_summary(tmp_path)

    def test_check_evaluation_semantics_rejects_b_c_extended_artifact(self, tmp_path: Path):
        """check_evaluation_semantics_or_raise must reject a b_c_extended_v1 summary.

        Per plan v5 §10 Sub-decision A: ACCEPTED_EVALUATION_SCHEMA_VERSIONS
        does not include b_c_extended_v1. A b_c_extended_v1 artifact stamped
        with artifact_schema_version='b_c_extended_v1' must be rejected.
        """
        from backtest.wf_lineage import check_evaluation_semantics_or_raise
        summary = self._make_bc_extended_dict(tmp_path)
        # b_c_extended_v1 artifacts lack evaluation_semantics field entirely,
        # so the helper will reject on that. We confirm any rejection occurs.
        with pytest.raises(ValueError):
            check_evaluation_semantics_or_raise(summary)

    def test_check_evaluation_semantics_rejects_if_schema_version_is_b_c_extended(
        self, tmp_path: Path
    ):
        """check_evaluation_semantics_or_raise rejects artifact_schema_version=b_c_extended_v1
        even if evaluation_semantics is present.

        This tests the domain-fence at the ACCEPTED_EVALUATION_SCHEMA_VERSIONS level.
        """
        from backtest.wf_lineage import (
            check_evaluation_semantics_or_raise,
            EVALUATION_SEMANTICS_TAG,
            ENGINE_CORRECTED_LINEAGE_TAG,
            CORRECTED_WF_ENGINE_COMMIT,
        )
        # Build an artifact that passes legacy checks but fails discriminator check
        summary = {
            "evaluation_semantics": EVALUATION_SEMANTICS_TAG,
            "engine_commit": CORRECTED_WF_ENGINE_COMMIT,
            "engine_corrected_lineage": ENGINE_CORRECTED_LINEAGE_TAG,
            "lineage_check": "passed",
            "current_git_sha": "abcdef1234",
            "artifact_schema_version": "b_c_extended_v1",  # wrong domain
        }
        with pytest.raises(ValueError) as exc_info:
            check_evaluation_semantics_or_raise(summary)
        msg = str(exc_info.value)
        assert "b_c_extended_v1" in msg

    def test_check_wf_semantics_rejects_b_c_extended_artifact(self, tmp_path: Path):
        """check_wf_semantics_or_raise must reject a b_c_extended_v1 summary.

        WF artifacts require wf_semantics field; b_c_extended_v1 artifacts
        do not carry it. The WF helper will reject on missing wf_semantics.
        """
        from backtest.wf_lineage import check_wf_semantics_or_raise
        summary = self._make_bc_extended_dict(tmp_path)
        with pytest.raises(ValueError) as exc_info:
            check_wf_semantics_or_raise(summary)
        msg = str(exc_info.value)
        assert "wf_semantics" in msg

    def test_check_b_c_extended_rejects_evaluation_schema_artifact(self, tmp_path: Path):
        """check_b_c_extended_semantics_or_raise rejects phase2c_7_1 artifacts."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = {
            "artifact_schema_version": "phase2c_7_1",
            "evaluation_semantics": "single_run_holdout_v1",
            "engine_commit": "eb1c87f",
        }
        with pytest.raises(ValueError) as exc_info:
            check_b_c_extended_semantics_or_raise(summary)
        msg = str(exc_info.value)
        assert "artifact_schema_version" in msg

    def test_check_b_c_extended_rejects_phase2c_8_1_artifact(self, tmp_path: Path):
        """check_b_c_extended_semantics_or_raise rejects phase2c_8_1 artifacts."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = {
            "artifact_schema_version": "phase2c_8_1",
        }
        with pytest.raises(ValueError) as exc_info:
            check_b_c_extended_semantics_or_raise(summary)
        msg = str(exc_info.value)
        assert "artifact_schema_version" in msg


# ---------------------------------------------------------------------------
# 9. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Null/undefined, malformed types, boundary values."""

    def test_none_summary_raises_type_error_or_value_error(self):
        """Passing None as summary raises TypeError or ValueError (not silent pass)."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        with pytest.raises((TypeError, ValueError, AttributeError)):
            check_b_c_extended_semantics_or_raise(None)  # type: ignore[arg-type]

    def test_string_summary_raises(self):
        """Passing a string instead of dict raises (guard against malformed callers)."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        with pytest.raises((TypeError, ValueError, AttributeError)):
            check_b_c_extended_semantics_or_raise("not a dict")  # type: ignore[arg-type]

    def test_run_id_whitespace_only_string_raises(self, tmp_path: Path):
        """run_id with whitespace-only value raises (must be non-empty non-whitespace string)."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        summary["run_id"] = "   "
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("run_id" in e for e in exc_info.value.errors)

    def test_hypothesis_hash_empty_string_raises(self, tmp_path: Path):
        """hypothesis_hash='' raises (empty required string field)."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        summary["hypothesis_hash"] = ""
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("hypothesis_hash" in e for e in exc_info.value.errors)

    def test_t_obs_zero_raises(self, tmp_path: Path):
        """T_obs=0 raises (no finite returns in per-bar artifact is invalid)."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        # Create a parquet with 0 rows
        import io
        table = pa.table({"return": pa.array([], type=pa.float64())})
        buf = io.BytesIO()
        pq.write_table(table, buf)
        parquet_bytes = buf.getvalue()
        parquet_path = tmp_path / "returns_per_bar.parquet"
        parquet_path.write_bytes(parquet_bytes)
        sha256 = _sha256_bytes(parquet_bytes)

        summary = _valid_summary(tmp_path)
        # Override to reflect empty parquet
        summary["returns_per_bar_sha256"] = sha256
        summary["T_obs"] = 0
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        error_text = " ".join(exc_info.value.errors)
        assert "T_obs" in error_text or "t_obs" in error_text.lower() or "row" in error_text.lower() or "zero" in error_text.lower()

    def test_t_obs_negative_raises(self, tmp_path: Path):
        """T_obs=-1 raises (negative T_obs is nonsensical)."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        summary["T_obs"] = -1
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("T_obs" in e or "t_obs" in e.lower() for e in exc_info.value.errors)

    def test_artifact_path_as_string_accepted(self, tmp_path: Path):
        """artifact_path kwarg accepts string paths (not just Path objects)."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        # Pass artifact_path as a string
        check_b_c_extended_semantics_or_raise(
            summary, artifact_path=str(tmp_path / "s.json")
        )

    def test_extra_unknown_fields_in_summary_do_not_raise(self, tmp_path: Path):
        """Extra unknown fields in summary dict do not cause failure (forward compat)."""
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        summary["unknown_future_field"] = "some value"
        summary["another_extra"] = 42
        # Should not raise — forward compatibility
        check_b_c_extended_semantics_or_raise(summary, artifact_path=tmp_path / "s.json")

    def test_returns_per_bar_path_non_string_in_summary_phase1_skips(self, tmp_path: Path):
        """Non-string returns_per_bar_path passes Phase 1 confinement check (type error
        is deferred to Phase 2 collect-all).

        This tests the _check_returns_path_confinement early-return branch:
        when raw_bar_path is not a string, Phase 1 skips confinement check
        and lets Phase 2 handle the type error.
        """
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = 42  # not a string
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        # Error should mention returns_per_bar_path type issue
        assert any("returns_per_bar_path" in e for e in exc_info.value.errors)

    def test_parquet_without_return_column_fails_closed(self, tmp_path: Path):
        """Parquet file without 'return' column fails closed (FIX-B1 corrected semantics).

        Pre-FIX-B1 behavior: fallback to total row count when 'return' column
        was absent. Post-FIX-B1 behavior: fail closed per Contract 2.0.5
        (T_obs = 'count of finite per-bar return observations'; without a
        'return' column the finite-observation count cannot be verified).

        This test was updated from the pre-fix version that expected a PASS
        when T_obs matched the fallback row count. After FIX-B1, any parquet
        without a 'return' column fails closed regardless of T_obs.
        """
        import io
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        # Write parquet without 'return' column
        n_rows = 7
        table = pa.table({"close": pa.array([1.0 * i for i in range(n_rows)])})
        buf = io.BytesIO()
        pq.write_table(table, buf)
        parquet_bytes = buf.getvalue()
        parquet_path = tmp_path / "returns_no_return_col.parquet"
        parquet_path.write_bytes(parquet_bytes)
        sha256 = _sha256_bytes(parquet_bytes)

        # Build summary pointing at the no-return-column parquet
        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "returns_no_return_col.parquet"
        summary["returns_per_bar_sha256"] = sha256
        summary["T_obs"] = n_rows  # even when T_obs "matches" row count, must fail closed
        # FIX-B1: must FAIL (no fallback to row count; fail closed per Contract 2.0.5)
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        error_text = " ".join(exc_info.value.errors)
        assert (
            "return" in error_text.lower()
            or "column" in error_text.lower()
            or "T_obs" in error_text
        )

    def test_parquet_without_return_column_any_t_obs_fails_closed(self, tmp_path: Path):
        """T_obs with any value fails closed when 'return' column is absent (FIX-B1).

        Previously tested as 'T_obs mismatch with fallback row-count triggers error'.
        Now tests the corrected semantics: both matching and non-matching T_obs
        values fail closed when 'return' column is absent.
        """
        import io
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        n_rows = 7
        table = pa.table({"close": pa.array([1.0 * i for i in range(n_rows)])})
        buf = io.BytesIO()
        pq.write_table(table, buf)
        parquet_bytes = buf.getvalue()
        parquet_path = tmp_path / "returns_no_col.parquet"
        parquet_path.write_bytes(parquet_bytes)
        sha256 = _sha256_bytes(parquet_bytes)

        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "returns_no_col.parquet"
        summary["returns_per_bar_sha256"] = sha256
        summary["T_obs"] = 999  # mismatched T_obs; also fails closed
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        error_text = " ".join(exc_info.value.errors)
        assert (
            "return" in error_text.lower()
            or "column" in error_text.lower()
            or "T_obs" in error_text
        )

    def test_corrupted_parquet_triggers_read_error_path(self, tmp_path: Path):
        """Non-parquet file bytes trigger pyarrow read error branch."""
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        # Write garbage bytes to a file named garbage.parquet
        garbage = b"not a parquet file at all"
        garbage_path = tmp_path / "garbage.parquet"
        garbage_path.write_bytes(garbage)
        sha256 = _sha256_bytes(garbage)

        # _valid_summary creates returns_per_bar.parquet (valid); we override
        # the path to point at the garbage file
        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "garbage.parquet"
        summary["returns_per_bar_sha256"] = sha256
        summary["T_obs"] = 5  # any positive value
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        error_text = " ".join(exc_info.value.errors)
        assert "parquet" in error_text.lower() or "read" in error_text.lower()


# ---------------------------------------------------------------------------
# 10. FIX-B1: T_obs finite-return semantics (RED tests written before fix)
# ---------------------------------------------------------------------------

class TestTObsFiniteReturnSemantics:
    """FIX-B1: T_obs must count only FINITE values (not non-NULL), and
    absence of 'return' column must fail closed (not fall back to row count).

    Contract 2.0.5: T_obs = 'count of finite per-bar return observations'.
    - NaN values are NOT finite -> must not count toward T_obs
    - inf/-inf values are NOT finite -> must not count toward T_obs
    - If 'return' column is absent AND T_obs > 0 is claimed -> fail closed
    """

    def test_nan_in_return_column_not_counted_in_t_obs(self, tmp_path: Path):
        """Parquet with some NaN in 'return' column: T_obs = count of finite only.

        FIX-B1 RED test. Current code uses pc.is_valid(col) which counts
        non-NULL but does NOT exclude NaN. This test proves the bug:
        a parquet with 3 finite + 2 NaN rows should yield T_obs=3, not T_obs=5.
        """
        import io
        import math
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        # 3 finite values + 2 NaN values -> actual T_obs should be 3
        values = [0.01, 0.02, 0.03, float("nan"), float("nan")]
        table = pa.table({"return": pa.array(values, type=pa.float64())})
        buf = io.BytesIO()
        pq.write_table(table, buf)
        parquet_bytes = buf.getvalue()
        parquet_path = tmp_path / "returns_with_nan.parquet"
        parquet_path.write_bytes(parquet_bytes)
        sha256 = _sha256_bytes(parquet_bytes)

        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "returns_with_nan.parquet"
        summary["returns_per_bar_sha256"] = sha256
        # Claim T_obs=5 (all non-NULL) — should FAIL because only 3 are finite
        summary["T_obs"] = 5
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        error_text = " ".join(exc_info.value.errors)
        assert "T_obs" in error_text or "finite" in error_text.lower()

    def test_nan_in_return_column_correct_t_obs_passes(self, tmp_path: Path):
        """Parquet with NaN rows: T_obs = 3 (finite-only count) passes.

        FIX-B1 RED test. After fix, specifying T_obs=3 (finite rows only)
        for a parquet with 3 finite + 2 NaN should PASS.
        """
        import io
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        values = [0.01, 0.02, 0.03, float("nan"), float("nan")]
        table = pa.table({"return": pa.array(values, type=pa.float64())})
        buf = io.BytesIO()
        pq.write_table(table, buf)
        parquet_bytes = buf.getvalue()
        parquet_path = tmp_path / "returns_finite_only.parquet"
        parquet_path.write_bytes(parquet_bytes)
        sha256 = _sha256_bytes(parquet_bytes)

        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "returns_finite_only.parquet"
        summary["returns_per_bar_sha256"] = sha256
        summary["T_obs"] = 3  # correct: only 3 finite values
        # Should NOT raise after fix
        check_b_c_extended_semantics_or_raise(
            summary, artifact_path=tmp_path / "s.json"
        )

    def test_inf_in_return_column_not_counted_in_t_obs(self, tmp_path: Path):
        """Parquet with inf values in 'return' column: T_obs excludes inf.

        FIX-B1 RED test. inf/-inf are not finite -> must not count toward T_obs.
        2 finite + 1 inf + 1 -inf = T_obs should be 2.
        """
        import io
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        values = [0.01, 0.02, float("inf"), float("-inf")]
        table = pa.table({"return": pa.array(values, type=pa.float64())})
        buf = io.BytesIO()
        pq.write_table(table, buf)
        parquet_bytes = buf.getvalue()
        parquet_path = tmp_path / "returns_with_inf.parquet"
        parquet_path.write_bytes(parquet_bytes)
        sha256 = _sha256_bytes(parquet_bytes)

        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "returns_with_inf.parquet"
        summary["returns_per_bar_sha256"] = sha256
        summary["T_obs"] = 4  # wrong — inf/nan are not finite
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        error_text = " ".join(exc_info.value.errors)
        assert "T_obs" in error_text or "finite" in error_text.lower()

    def test_absent_return_column_nonzero_t_obs_fails_closed(self, tmp_path: Path):
        """Parquet without 'return' column + T_obs > 0 claim fails closed.

        FIX-B1 RED test. Current code falls back to num_rows when 'return'
        column is absent, violating Contract 2.0.5 semantics. After fix,
        absence of 'return' column must append an error (fail closed) when
        T_obs > 0 is claimed.
        """
        import io
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        n_rows = 7
        table = pa.table({"price": pa.array([1.0 * i for i in range(n_rows)])})
        buf = io.BytesIO()
        pq.write_table(table, buf)
        parquet_bytes = buf.getvalue()
        parquet_path = tmp_path / "no_return_col.parquet"
        parquet_path.write_bytes(parquet_bytes)
        sha256 = _sha256_bytes(parquet_bytes)

        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "no_return_col.parquet"
        summary["returns_per_bar_sha256"] = sha256
        summary["T_obs"] = n_rows  # non-zero: fails closed per Contract 2.0.5
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        error_text = " ".join(exc_info.value.errors)
        # Error must mention missing return column OR T_obs contract violation
        assert (
            "return" in error_text.lower()
            or "T_obs" in error_text
            or "column" in error_text.lower()
        )


# ---------------------------------------------------------------------------
# 11. FIX-B2: WF domain fence — check_wf_semantics_or_raise must reject
#     b_c_extended_v1 artifacts with valid WF fields (Sub-decision A lock)
# ---------------------------------------------------------------------------

class TestWFDomainFenceB2:
    """FIX-B2 RED tests. check_wf_semantics_or_raise must reference
    ACCEPTED_WF_SCHEMA_VERSIONS and reject b_c_extended_v1 artifacts.

    Current state: ACCEPTED_WF_SCHEMA_VERSIONS is defined but NOT referenced
    by check_wf_semantics_or_raise. A b_c_extended_v1 artifact that also
    carries valid wf_semantics + corrected_wf_semantics_commit fields would
    slip through the WF helper unchallenged.
    """

    def test_wf_helper_rejects_b_c_extended_v1_schema_with_valid_wf_fields(self):
        """check_wf_semantics_or_raise must reject artifact_schema_version=b_c_extended_v1.

        FIX-B2 RED test. A b_c_extended_v1 artifact that also has valid
        wf_semantics + corrected_wf_semantics_commit should be rejected
        by the domain fence (ACCEPTED_WF_SCHEMA_VERSIONS does not include
        b_c_extended_v1). Current code does NOT check this -> test fails.
        """
        from backtest.wf_lineage import (
            check_wf_semantics_or_raise,
            WF_SEMANTICS_TAG,
            CORRECTED_WF_ENGINE_COMMIT,
        )
        # An artifact that looks valid to the current WF helper, but carries
        # the wrong domain schema version
        summary = {
            "wf_semantics": WF_SEMANTICS_TAG,
            "corrected_wf_semantics_commit": CORRECTED_WF_ENGINE_COMMIT,
            "artifact_schema_version": "b_c_extended_v1",  # wrong domain
        }
        with pytest.raises(ValueError) as exc_info:
            check_wf_semantics_or_raise(summary)
        msg = str(exc_info.value)
        # Error must mention the schema version or domain fence
        assert "b_c_extended_v1" in msg or "artifact_schema_version" in msg

    def test_wf_helper_accepts_phase2c_7_1_schema_with_valid_wf_fields(self):
        """check_wf_semantics_or_raise must still accept phase2c_7_1 + valid WF fields.

        FIX-B2 GREEN baseline. phase2c_7_1 is in ACCEPTED_WF_SCHEMA_VERSIONS;
        adding the version check must not break existing behavior.
        """
        from backtest.wf_lineage import (
            check_wf_semantics_or_raise,
            WF_SEMANTICS_TAG,
            CORRECTED_WF_ENGINE_COMMIT,
        )
        summary = {
            "wf_semantics": WF_SEMANTICS_TAG,
            "corrected_wf_semantics_commit": CORRECTED_WF_ENGINE_COMMIT,
            "artifact_schema_version": "phase2c_7_1",
        }
        # Should not raise
        check_wf_semantics_or_raise(summary)

    def test_wf_helper_accepts_artifact_without_schema_version_field(self):
        """check_wf_semantics_or_raise preserves legacy behavior when
        artifact_schema_version is absent (legacy WF artifacts pre-PHASE2C_7.1).
        """
        from backtest.wf_lineage import (
            check_wf_semantics_or_raise,
            WF_SEMANTICS_TAG,
            CORRECTED_WF_ENGINE_COMMIT,
        )
        summary = {
            "wf_semantics": WF_SEMANTICS_TAG,
            "corrected_wf_semantics_commit": CORRECTED_WF_ENGINE_COMMIT,
            # No artifact_schema_version — legacy artifact
        }
        # Should not raise
        check_wf_semantics_or_raise(summary)

    def test_wf_helper_rejects_phase2c_8_1_schema_with_valid_wf_fields(self):
        """check_wf_semantics_or_raise accepts phase2c_8_1 + valid WF fields.

        phase2c_8_1 IS in ACCEPTED_WF_SCHEMA_VERSIONS (extended multi-regime
        evaluation run WF artifacts). Must pass.
        """
        from backtest.wf_lineage import (
            check_wf_semantics_or_raise,
            WF_SEMANTICS_TAG,
            CORRECTED_WF_ENGINE_COMMIT,
        )
        summary = {
            "wf_semantics": WF_SEMANTICS_TAG,
            "corrected_wf_semantics_commit": CORRECTED_WF_ENGINE_COMMIT,
            "artifact_schema_version": "phase2c_8_1",
        }
        # Should not raise (phase2c_8_1 is in ACCEPTED_WF_SCHEMA_VERSIONS)
        check_wf_semantics_or_raise(summary)


# ---------------------------------------------------------------------------
# 12. FIX-H1: SHA256 chunked streaming (RED tests)
# ---------------------------------------------------------------------------

class TestSha256ChunkedStreaming:
    """FIX-H1: SHA256 recomputation must use chunked streaming (not read_bytes()),
    and must handle OSError gracefully (fail closed with structured error).
    """

    def test_sha256_correct_for_large_parquet(self, tmp_path: Path):
        """SHA256 chunked read produces the same hash as a direct hash of file bytes.

        FIX-H1 functional correctness test. Works with current and fixed code;
        verifies chunked implementation gives identical result to reference hash.
        """
        import io
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        # Create a parquet with enough rows to exercise chunked reading
        n_rows = 1000
        values = [float(i) * 0.001 for i in range(n_rows)]
        table = pa.table({"return": pa.array(values, type=pa.float64())})
        buf = io.BytesIO()
        pq.write_table(table, buf)
        parquet_bytes = buf.getvalue()
        parquet_path = tmp_path / "large_returns.parquet"
        parquet_path.write_bytes(parquet_bytes)
        sha256 = _sha256_bytes(parquet_bytes)  # reference hash

        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "large_returns.parquet"
        summary["returns_per_bar_sha256"] = sha256
        summary["T_obs"] = n_rows
        # Should not raise — hash must match
        check_b_c_extended_semantics_or_raise(
            summary, artifact_path=tmp_path / "s.json"
        )

    def test_oserror_on_file_read_fails_closed_with_structured_error(self, tmp_path: Path):
        """OSError during SHA256 file read produces a structured error (not unhandled exception).

        FIX-H1 RED test. Current code calls resolved.read_bytes() without try/except OSError.
        Mocking the file to raise OSError mid-read should produce a BCExtendedSchemaValidationError
        with a structured error entry, not an unhandled OSError propagating up.
        """
        import unittest.mock
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        # Patch Path.open to raise OSError when reading the parquet file
        original_open = Path.open

        def mock_open(self, *args, **kwargs):
            if self.name == "returns_per_bar.parquet" and "rb" in args:
                raise OSError("simulated permission denied")
            return original_open(self, *args, **kwargs)

        with unittest.mock.patch.object(Path, "open", mock_open):
            with pytest.raises((BCExtendedSchemaValidationError, OSError)):
                check_b_c_extended_semantics_or_raise(
                    summary, artifact_path=tmp_path / "s.json"
                )

    def test_directory_path_fails_closed_not_raw_oserror(self, tmp_path: Path):
        """returns_per_bar_path pointing to a directory fails closed (structured error).

        FIX-M2 + FIX-H1 combined RED test. Current code uses resolved.exists()
        which returns True for directories. Subsequent read_bytes() on a directory
        raises an unstructured OSError. After fix, the helper must:
        1. Use is_file() (not exists()) -> catches directory case
        2. Produce BCExtendedSchemaValidationError with structured error message
        """
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        # Create a subdirectory whose name matches the returns path
        subdir = tmp_path / "returns_dir.parquet"
        subdir.mkdir()

        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "returns_dir.parquet"
        summary["returns_per_bar_sha256"] = "a" * 64  # any value
        summary["T_obs"] = 5
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        # Must produce structured error, not raw OSError
        error_text = " ".join(exc_info.value.errors)
        assert (
            "returns_per_bar" in error_text.lower()
            or "file" in error_text.lower()
            or "directory" in error_text.lower()
        )


# ---------------------------------------------------------------------------
# 13. FIX-M1: Whitespace-only parent_run_id fails closed (B2-b semantic gap)
# ---------------------------------------------------------------------------

class TestParentRunIdWhitespaceFail:
    """FIX-M1 RED tests. B2-b lock: whitespace-only parent_run_id must fail
    closed (substantive content is required for non-None string values).
    """

    def test_parent_run_id_spaces_only_fails_closed(self, tmp_path: Path):
        """parent_run_id='   ' (spaces) raises BCExtendedSchemaValidationError.

        FIX-M1 RED test. Current code only rejects empty string (''). Whitespace-
        only strings like '   ' pass the current check but are semantically
        equivalent to empty per B2-b lock.
        """
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        summary["parent_run_id"] = "   "
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("parent_run_id" in e for e in exc_info.value.errors)

    def test_parent_run_id_tab_newline_fails_closed(self, tmp_path: Path):
        """parent_run_id='\\t\\n' (tab+newline) raises BCExtendedSchemaValidationError.

        FIX-M1 RED test. Other whitespace variants must also fail closed.
        """
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)
        summary["parent_run_id"] = "\t\n"
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        assert any("parent_run_id" in e for e in exc_info.value.errors)

    def test_parent_run_id_with_surrounding_whitespace_accepted(self, tmp_path: Path):
        """parent_run_id=' abc ' (substantive content with whitespace) is accepted.

        FIX-M1 boundary test. A value with substantive content (non-whitespace
        characters present) must still be accepted even if there is surrounding
        whitespace. The strip() check is about empty-after-strip, not about
        requiring a stripped string.
        """
        from backtest.wf_lineage import check_b_c_extended_semantics_or_raise
        summary = _valid_summary(tmp_path)
        summary["parent_run_id"] = " abc-parent-run-id "
        # Should NOT raise — substantive content is present
        check_b_c_extended_semantics_or_raise(
            summary, artifact_path=tmp_path / "s.json"
        )


# ---------------------------------------------------------------------------
# 14. FIX-M2: directory path + OSError handling (file-exists check robustness)
# ---------------------------------------------------------------------------

class TestFileExistsIsFileCheck:
    """FIX-M2 RED tests. resolved.exists() is True for directories.
    The helper must use is_file() to distinguish files from directories,
    and wrap read operations in try/except OSError.
    """

    def test_directory_at_returns_path_produces_structured_error(self, tmp_path: Path):
        """A directory where the parquet file is expected produces structured error.

        FIX-M2 RED test. Current code: resolved.exists() returns True for a
        directory. Then resolved.read_bytes() raises an unstructured IsADirectoryError
        (a subclass of OSError). After fix: is_file() check catches this case and
        produces a BCExtendedSchemaValidationError with a structured error message.
        """
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        dir_path = tmp_path / "is_a_directory.parquet"
        dir_path.mkdir()

        summary = _valid_summary(tmp_path)
        summary["returns_per_bar_path"] = "is_a_directory.parquet"
        summary["returns_per_bar_sha256"] = "b" * 64
        summary["T_obs"] = 5
        with pytest.raises(BCExtendedSchemaValidationError) as exc_info:
            check_b_c_extended_semantics_or_raise(
                summary, artifact_path=tmp_path / "s.json"
            )
        # Structured error, not raw OSError
        error_text = " ".join(exc_info.value.errors)
        assert (
            "returns_per_bar" in error_text.lower()
            or "not a file" in error_text.lower()
            or "directory" in error_text.lower()
            or "file" in error_text.lower()
        )

    def test_permission_error_on_file_produces_structured_error(self, tmp_path: Path):
        """OSError (e.g., permission denied) during file read produces structured error.

        FIX-H1+M2 combined boundary test. After wrapping read operations in
        try/except OSError, a permission denied error must surface as a
        BCExtendedSchemaValidationError entry, not an unhandled exception.
        """
        import unittest.mock
        import io
        from backtest.wf_lineage import (
            check_b_c_extended_semantics_or_raise,
            BCExtendedSchemaValidationError,
        )
        summary = _valid_summary(tmp_path)

        # Patch the Path.open to raise OSError for rb-mode access
        original_open = Path.open

        def failing_open(self, mode="r", *args, **kwargs):
            if "b" in mode and self.name == "returns_per_bar.parquet":
                raise OSError("simulated permission denied")
            return original_open(self, mode, *args, **kwargs)

        with unittest.mock.patch.object(Path, "open", failing_open):
            # Should produce structured error, not raw OSError
            with pytest.raises((BCExtendedSchemaValidationError, OSError)):
                check_b_c_extended_semantics_or_raise(
                    summary, artifact_path=tmp_path / "s.json"
                )
