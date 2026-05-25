"""T1.3 Registry + API extension tests.

TDD discipline: tests written FIRST (RED) per testing.md discipline.
Implementation targets:
- backtest/artifact_schema.py: canonicalize_execution_config_path() + LineageContext
- backtest/engine.py: _write_to_registry() + run_backtest() + run_regime_holdout() + run_walk_forward()
- scripts/run_phase2c_evaluation_gate.py: LineageContext integration

Test organization:
1. Migration smoke test (cost_anchor_id column exists after create_table())
2. canonicalize_execution_config_path() parametrized tests
3. LineageContext dataclass tests (field count, required/optional, __post_init__, frozen)
4. HYBRID T1.3-C conflict-check tests
5. Engine entry-point wiring tests (run_backtest / run_regime_holdout / run_walk_forward)
6. Backward compat regression (legacy callers unaffected)

Contract references:
- T1.3-A: migration approach (MIGRATION_COLUMNS entry at experiment_registry.py:139)
- T1.3-B: canonicalize_execution_config_path() pure function spec
- T1.3-C: HYBRID parent_run_id conflict-check at write boundary
- T1.3-D: LineageContext frozen dataclass with 14 dataclass fields (13 Contract 2.0.5 + T_obs)
- Contract 2.0.4: cost_anchor_id mapping (6-row R3.1d §5.2)
- Contract 2.0.5: 14 header fields per artifact
"""
from __future__ import annotations

import dataclasses
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Repo root for path-canonicalization tests
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent  # btc-alpha-pipeline/


# ---------------------------------------------------------------------------
# 1. Migration smoke test — cost_anchor_id column exists after create_table()
# ---------------------------------------------------------------------------


class TestMigrationSmoke:
    """Verify T1.3-A: fresh empty DB → create_table() → cost_anchor_id column exists."""

    def test_cost_anchor_id_column_exists_after_create_table_on_fresh_db(
        self, tmp_path: Path
    ) -> None:
        """Fresh SQLite DB: create_table() must create cost_anchor_id column."""
        from backtest.experiment_registry import create_table

        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        create_table(conn)

        cursor = conn.execute("PRAGMA table_info(runs)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        assert "cost_anchor_id" in columns, (
            "cost_anchor_id must be present in runs table after create_table() "
            "(T1.3-A: MIGRATION_COLUMNS entry at experiment_registry.py:139)"
        )

    def test_cost_anchor_id_column_exists_on_in_memory_db(self) -> None:
        """In-memory SQLite DB: create_table() produces cost_anchor_id column."""
        from backtest.experiment_registry import create_table

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        create_table(conn)

        cursor = conn.execute("PRAGMA table_info(runs)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        assert "cost_anchor_id" in columns

    def test_create_table_idempotent_cost_anchor_id_preserved(self, tmp_path: Path) -> None:
        """create_table() called twice: cost_anchor_id column still present."""
        from backtest.experiment_registry import create_table

        conn = sqlite3.connect(str(tmp_path / "test.db"))
        conn.row_factory = sqlite3.Row
        create_table(conn)
        create_table(conn)  # second call — idempotent

        cursor = conn.execute("PRAGMA table_info(runs)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        assert "cost_anchor_id" in columns


# ---------------------------------------------------------------------------
# 2. canonicalize_execution_config_path() tests
# ---------------------------------------------------------------------------


class TestCanonicalizeExecutionConfigPath:
    """T1.3-B: canonicalize_execution_config_path() pure function."""

    def _canonical(self, path: Any, **kwargs: Any) -> str:
        from backtest.artifact_schema import canonicalize_execution_config_path

        return canonicalize_execution_config_path(path, **kwargs)

    # --- Happy paths ---

    def test_absolute_path_under_repo_root_returns_posix_relative(self) -> None:
        """Absolute path under repo root → POSIX repo-relative string."""
        abs_path = _REPO_ROOT / "config" / "execution.yaml"
        result = self._canonical(abs_path)
        assert result == "config/execution.yaml"

    def test_relative_path_resolved_against_repo_root(self) -> None:
        """Relative path → resolved against repo root → POSIX repo-relative."""
        # "config/execution.yaml" as a bare relative string
        result = self._canonical("config/execution.yaml")
        assert result == "config/execution.yaml"

    def test_path_object_same_as_string(self) -> None:
        """Path object and string produce identical result."""
        p = _REPO_ROOT / "config" / "execution.yaml"
        result_obj = self._canonical(p)
        result_str = self._canonical("config/execution.yaml")
        assert result_obj == result_str

    def test_all_six_mapping_keys_canonicalize_correctly(self) -> None:
        """All 6 R3.1d §5.2 config paths canonicalize to their key form."""
        expected_keys = [
            "config/execution.yaml",
            "config/execution_phase4_07bps.yaml",
            "config/execution_phase4_13bps.yaml",
            "config/execution_phase4_15bps.yaml",
            "config/execution_phase4_17bps.yaml",
            "config/execution_phaseb_spot_15bps.yaml",
        ]
        for key in expected_keys:
            result = self._canonical(key)
            assert result == key, f"Expected {key!r}, got {result!r}"

    def test_explicit_repo_root_override(self, tmp_path: Path) -> None:
        """repo_root kwarg overrides default; path must be under that root."""
        # Create a file under tmp_path to simulate a path under an explicit root
        sub = tmp_path / "config" / "execution.yaml"
        sub.parent.mkdir(parents=True)
        sub.touch()

        result = self._canonical(sub, repo_root=tmp_path)
        assert result == "config/execution.yaml"

    # --- Fail-closed paths ---

    def test_path_outside_repo_root_raises_value_error(self, tmp_path: Path) -> None:
        """Path outside repo root → FAIL CLOSED with ValueError."""
        outside_path = tmp_path / "outside.yaml"
        outside_path.touch()

        with pytest.raises(ValueError, match="outside.*repo root"):
            self._canonical(outside_path)

    def test_case_only_mismatch_raises_or_maps_miss(self) -> None:
        """Case-only mismatch (Config/execution.yaml) fails closed.

        On case-insensitive filesystems (macOS HFS+/APFS), os.path.realpath
        may resolve to the same inode. The canonicalized key is the
        relpath result, which on macOS still preserves the filesystem's
        stored casing. The COST_ANCHOR_ID_MAPPING uses lowercase keys, so
        a case-different path must produce a mapping miss (no silent fallback).

        We test that either:
        (a) canonicalize raises ValueError for case-mismatch (strict mode), OR
        (b) the canonicalized result does NOT match any mapping key (mapping miss)

        Both are correct per plan v5 Fv5-1: case-only mismatches FAIL CLOSED
        via mapping miss. The canonicalize function itself doesn't guarantee the
        miss, but the downstream mapping lookup will miss.
        """
        # Build the uppercase path and check canonicalize doesn't add silent normcase
        abs_path = _REPO_ROOT / "config" / "Execution.yaml"
        # If the file doesn't exist at this path (it shouldn't on case-sensitive),
        # realpath will still produce a path. We just verify normcase is NOT applied.
        try:
            result = self._canonical(abs_path)
            # If canonicalization succeeded (on case-insensitive FS), the result
            # must NOT be silently lowercased to "config/execution.yaml"
            # (no os.path.normcase applied per plan v5 Fv5-1).
            # On case-sensitive FS, file won't exist but realpath still works.
            # Either the mapping lookup will miss, or the result has wrong case.
            from backtest.artifact_schema import COST_ANCHOR_ID_MAPPING

            # Allow the path through but verify no normcase was applied
            # (result preserves filesystem case, not forced-lower)
            assert isinstance(result, str)
            # The key "config/Execution.yaml" should NOT be in mapping
            assert result not in COST_ANCHOR_ID_MAPPING or result == "config/execution.yaml"
        except ValueError:
            # Strict-mode canonicalization raised — also acceptable
            pass

    def test_symlinked_path_resolves_via_realpath(self, tmp_path: Path) -> None:
        """Symlinked path → realpath resolution → correct repo-relative key."""
        # Create a real config file under repo root
        target = _REPO_ROOT / "config" / "execution.yaml"
        if not target.exists():
            pytest.skip("config/execution.yaml not present on disk")

        # Create symlink in tmp_path pointing to the real file
        link = tmp_path / "exec_link.yaml"
        link.symlink_to(target)

        result = self._canonical(link)
        assert result == "config/execution.yaml"

    def test_none_path_raises_type_or_value_error(self) -> None:
        """None path raises TypeError or ValueError (not silent)."""
        with pytest.raises((TypeError, ValueError)):
            self._canonical(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 3. LineageContext dataclass tests
# ---------------------------------------------------------------------------


class TestLineageContextFieldCount:
    """T1.3-D: LineageContext must have exactly 14 dataclass fields (13 Contract 2.0.5 + T_obs)."""

    def test_field_count_is_14(self) -> None:
        """len(dataclasses.fields(LineageContext)) == 14 (contract lock)."""
        from backtest.artifact_schema import LineageContext

        n = len(dataclasses.fields(LineageContext))
        assert n == 14, (
            f"LineageContext must have exactly 14 dataclass fields (13 Contract 2.0.5 + T_obs), "
            f"got {n}. If fields were added/removed, update Contract 2.0.5 and "
            f"the plan v5 §2.0.5 enumeration table."
        )


class TestLineageContextFieldNames:
    """Each field name must match Contract 2.0.5 verbatim enumeration."""

    EXPECTED_FIELDS = {
        "run_id",
        "hypothesis_hash",
        "source_batch_id",
        "regime_key",
        "engine_commit",
        "current_git_sha",
        "execution_config_path",
        "execution_config_sha256",
        "parquet_data_sha256",
        "cost_anchor_id",
        "returns_per_bar_path",
        "returns_per_bar_sha256",
        "T_obs",
        "parent_run_id",
    }

    def test_all_expected_fields_present(self) -> None:
        """All 14 LineageContext field names are present in LineageContext."""
        from backtest.artifact_schema import LineageContext

        actual = {f.name for f in dataclasses.fields(LineageContext)}
        missing = self.EXPECTED_FIELDS - actual
        extra = actual - self.EXPECTED_FIELDS

        assert not missing, f"Missing fields: {missing}"
        assert not extra, f"Unexpected extra fields: {extra}"


class TestLineageContextRequiredOptional:
    """13 fields required; parent_run_id Optional (B2-b)."""

    def _build_valid_kwargs(self) -> dict[str, Any]:
        """Return minimal valid kwargs for constructing LineageContext.

        Note: cost_anchor_id is NOT included — it is auto-resolved by
        __post_init__ from execution_config_path via COST_ANCHOR_ID_MAPPING.
        """
        return {
            "run_id": "run-abc-123",
            "hypothesis_hash": "abc123def456",
            "source_batch_id": "batch-xyz-789",
            "regime_key": "v2.regime_holdout",
            "engine_commit": "eb1c87f",
            "current_git_sha": "deadbeef",
            "execution_config_path": "config/execution.yaml",
            "execution_config_sha256": "sha256:aabbccdd",
            "parquet_data_sha256": "sha256:11223344",
            "returns_per_bar_path": "returns_per_bar.parquet",
            "returns_per_bar_sha256": "sha256:55667788",
            "T_obs": 100,
            "parent_run_id": None,
        }

    def test_construction_with_all_required_fields_succeeds(self) -> None:
        """LineageContext constructs with all 13 required + parent_run_id=None."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._build_valid_kwargs()
        lc = LineageContext(**kwargs)
        assert lc.run_id == "run-abc-123"
        assert lc.parent_run_id is None

    def test_parent_run_id_none_is_valid(self) -> None:
        """parent_run_id=None is explicitly valid (B2-b single-run callers)."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._build_valid_kwargs()
        kwargs["parent_run_id"] = None
        lc = LineageContext(**kwargs)
        assert lc.parent_run_id is None

    def test_parent_run_id_non_empty_string_is_valid(self) -> None:
        """parent_run_id as non-empty string is valid (B2-b)."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._build_valid_kwargs()
        kwargs["parent_run_id"] = "parent-run-uuid-here"
        lc = LineageContext(**kwargs)
        assert lc.parent_run_id == "parent-run-uuid-here"

    def test_parent_run_id_empty_string_fails_closed(self) -> None:
        """parent_run_id='' raises ValueError (B2-b: empty-string FAIL CLOSED)."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._build_valid_kwargs()
        kwargs["parent_run_id"] = ""

        with pytest.raises(ValueError, match="parent_run_id"):
            LineageContext(**kwargs)

    def test_parent_run_id_whitespace_only_fails_closed(self) -> None:
        """parent_run_id='   ' raises ValueError (B2-b: whitespace-only FAIL CLOSED)."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._build_valid_kwargs()
        kwargs["parent_run_id"] = "   "

        with pytest.raises(ValueError, match="parent_run_id"):
            LineageContext(**kwargs)

    def test_missing_required_field_raises(self) -> None:
        """Omitting a required field (run_id) raises TypeError."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._build_valid_kwargs()
        del kwargs["run_id"]

        with pytest.raises(TypeError):
            LineageContext(**kwargs)


class TestLineageContextPostInit:
    """__post_init__ canonicalization + cost_anchor_id resolution."""

    def _build_valid_kwargs(self) -> dict[str, Any]:
        # cost_anchor_id intentionally omitted — auto-resolved by __post_init__
        return {
            "run_id": "run-001",
            "hypothesis_hash": "hash001",
            "source_batch_id": "batch-001",
            "regime_key": "v2.regime_holdout",
            "engine_commit": "abc1234",
            "current_git_sha": "def5678",
            "execution_config_path": "config/execution.yaml",
            "execution_config_sha256": "sha256:aabb",
            "parquet_data_sha256": "sha256:ccdd",
            "returns_per_bar_path": "returns_per_bar.parquet",
            "returns_per_bar_sha256": "sha256:eeff",
            "T_obs": 50,
            "parent_run_id": None,
        }

    def test_execution_config_path_canonicalized_at_construction(self) -> None:
        """Raw relative path in → canonicalized POSIX string stored."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._build_valid_kwargs()
        kwargs["execution_config_path"] = "config/execution.yaml"
        lc = LineageContext(**kwargs)
        # After __post_init__, execution_config_path must be canonicalized
        assert lc.execution_config_path == "config/execution.yaml"

    def test_cost_anchor_id_resolved_at_construction(self) -> None:
        """cost_anchor_id is resolved from execution_config_path at construction."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._build_valid_kwargs()
        kwargs["execution_config_path"] = "config/execution.yaml"
        lc = LineageContext(**kwargs)
        # cost_anchor_id must be populated by __post_init__
        assert lc.cost_anchor_id == "legacy_perp_inspired_7bps_v0"

    def test_phaseb_spot_path_resolves_correct_anchor(self) -> None:
        """config/execution_phaseb_spot_15bps.yaml → spot_realistic_15bps_v1."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._build_valid_kwargs()
        kwargs["execution_config_path"] = "config/execution_phaseb_spot_15bps.yaml"
        lc = LineageContext(**kwargs)
        assert lc.cost_anchor_id == "spot_realistic_15bps_v1"

    def test_unmapped_execution_config_path_raises(self) -> None:
        """Unmapped execution_config_path raises ValueError with structured message."""
        from backtest.artifact_schema import LineageContext

        kwargs = self._build_valid_kwargs()
        kwargs["execution_config_path"] = "config/unknown_cost_model.yaml"

        with pytest.raises(ValueError) as exc_info:
            LineageContext(**kwargs)

        msg = str(exc_info.value)
        # Error message must include guidance and known mappings
        assert "COST_ANCHOR_ID_MAPPING" in msg or "R3.1d" in msg or "mapping" in msg.lower()


class TestLineageContextFrozen:
    """Frozen semantics: post-construction mutation raises FrozenInstanceError."""

    def _build_valid_kwargs(self) -> dict[str, Any]:
        # cost_anchor_id intentionally omitted — auto-resolved by __post_init__
        return {
            "run_id": "run-frozen-test",
            "hypothesis_hash": "hashfrozen",
            "source_batch_id": "batch-frozen",
            "regime_key": "v2.regime_holdout",
            "engine_commit": "aaa1111",
            "current_git_sha": "bbb2222",
            "execution_config_path": "config/execution.yaml",
            "execution_config_sha256": "sha256:frozen",
            "parquet_data_sha256": "sha256:frzdata",
            "returns_per_bar_path": "returns_per_bar.parquet",
            "returns_per_bar_sha256": "sha256:frzbar",
            "T_obs": 10,
            "parent_run_id": None,
        }

    def test_mutation_after_construction_raises(self) -> None:
        """Attempt to set a field after construction raises FrozenInstanceError."""
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**self._build_valid_kwargs())
        with pytest.raises(dataclasses.FrozenInstanceError):
            lc.run_id = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 4. HYBRID T1.3-C conflict-check tests
# ---------------------------------------------------------------------------


class TestHybridParentRunIdConflict:
    """T1.3-C: HYBRID conflict-check at _write_to_registry write boundary."""

    def _make_minimal_write_args(self) -> dict[str, Any]:
        """Minimal args for _write_to_registry that avoid real backtrader calls."""
        from backtest.execution_model import ConstantSlippage

        # Use a real class so __name__ attribute works correctly.
        # _write_to_registry calls getattr(strategy_cls, "STRATEGY_NAME", strategy_cls.__name__)
        # which fails on MagicMock because __name__ is not a standard MagicMock attribute.
        class MockStrategy:
            STRATEGY_NAME = "test_strategy"

        strategy_cls = MockStrategy

        cost_model = MagicMock(spec=ConstantSlippage)
        cost_model.fee_model_label = "effective_7bps_per_side"

        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        return {
            "run_id": "test-run-id-001",
            "strategy_cls": strategy_cls,
            "strategy_params": {},
            "start_date": now,
            "end_date": now,
            "effective_start": now,
            "warmup_bars": 0,
            "cost_model": cost_model,
            "metrics": {
                "initial_capital": 10000.0,
                "final_capital": 10100.0,
                "total_return": 0.01,
                "sharpe_ratio": 1.0,
                "max_drawdown": 0.05,
                "max_drawdown_duration_hours": 24.0,
                "total_trades": 5,
                "win_rate": 0.6,
                "avg_trade_duration_hours": 4.0,
                "avg_trade_return": 0.002,
                "profit_factor": 1.5,
            },
        }

    def test_legacy_caller_no_lineage_context_succeeds(self, tmp_path: Path) -> None:
        """Legacy caller with no lineage_context and no execution_config_path succeeds.

        Interpretation (b): None → config/execution.yaml → legacy_perp_inspired_7bps_v0.
        """
        from backtest.engine import _write_to_registry

        db_path = tmp_path / "test_legacy.db"
        args = self._make_minimal_write_args()
        args["db_path"] = db_path

        # Must not raise
        _write_to_registry(**args)

        # Verify cost_anchor_id was populated
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT cost_anchor_id FROM runs WHERE run_id = ?",
            (args["run_id"],),
        ).fetchone()
        conn.close()

        assert row is not None
        assert row["cost_anchor_id"] == "legacy_perp_inspired_7bps_v0"

    def test_conflict_check_disagreement_raises(self, tmp_path: Path) -> None:
        """scalar parent_run_id='A' + lineage_context.parent_run_id='B' → FAIL CLOSED."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry

        db_path = tmp_path / "test_conflict.db"
        args = self._make_minimal_write_args()
        args["db_path"] = db_path
        args["parent_run_id"] = "parent-A"

        lc = LineageContext(
            run_id="run-conflict-test",
            hypothesis_hash="hash-conflict",
            source_batch_id="batch-conflict",
            regime_key="v2.regime_holdout",
            engine_commit="aaa",
            current_git_sha="bbb",
            execution_config_path="config/execution.yaml",
            execution_config_sha256="sha256:xx",
            parquet_data_sha256="sha256:yy",
            returns_per_bar_path="returns_per_bar.parquet",
            returns_per_bar_sha256="sha256:zz",
            T_obs=10,
            parent_run_id="parent-B",  # disagrees with scalar above; cost_anchor_id auto-resolved
        )
        args["lineage_context"] = lc

        with pytest.raises(ValueError, match="parent_run_id"):
            _write_to_registry(**args)

    def test_conflict_check_scalar_none_lineage_has_value_no_conflict(
        self, tmp_path: Path
    ) -> None:
        """scalar parent_run_id=None + lineage_context.parent_run_id='B' → use B (no conflict).

        B2 SYS-fix-1: scalar run_id must match lc.run_id (B2 run_id conflict-check).
        Use lc.run_id as scalar run_id to satisfy B2 agreement requirement.
        """
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry

        db_path = tmp_path / "test_no_conflict.db"
        args = self._make_minimal_write_args()
        args["db_path"] = db_path
        args["parent_run_id"] = None  # scalar default-None

        lc = LineageContext(
            run_id="run-no-conflict",
            hypothesis_hash="hash-nc",
            source_batch_id="batch-nc",
            regime_key="v2.regime_holdout",
            engine_commit="ccc",
            current_git_sha="ddd",
            execution_config_path="config/execution.yaml",
            execution_config_sha256="sha256:aa",
            parquet_data_sha256="sha256:bb",
            returns_per_bar_path="",   # LATE_FILL empty (FIX-T1.1-SYS2-B2: artifact_dir not provided)
            returns_per_bar_sha256="",
            T_obs=5,
            parent_run_id="parent-B",
            # cost_anchor_id auto-resolved from execution_config_path
        )
        args["lineage_context"] = lc
        # B2 SYS-fix-1: scalar run_id must agree with lc.run_id
        args["run_id"] = lc.run_id

        # Must not raise — None vs 'B' is not a conflict
        _write_to_registry(**args)

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT parent_run_id, cost_anchor_id FROM runs WHERE run_id = ?",
            (args["run_id"],),
        ).fetchone()
        conn.close()

        assert row is not None
        assert row["parent_run_id"] == "parent-B"
        assert row["cost_anchor_id"] == "legacy_perp_inspired_7bps_v0"

    def test_explicit_lineage_context_all_14_fields_propagate(
        self, tmp_path: Path
    ) -> None:
        """New caller with explicit LineageContext → all 14 fields propagate correctly.

        B2 SYS-fix-1: scalar run_id must match lc.run_id (B2 run_id conflict-check).
        Use lc.run_id as scalar run_id to satisfy B2 agreement requirement.
        """
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry

        db_path = tmp_path / "test_full_lineage.db"
        args = self._make_minimal_write_args()
        args["db_path"] = db_path

        lc = LineageContext(
            run_id="run-full-lineage",
            hypothesis_hash="fullhash1234",
            source_batch_id="fullbatch-5678",
            regime_key="v2.regime_holdout",
            engine_commit="eee111",
            current_git_sha="fff222",
            execution_config_path="config/execution_phaseb_spot_15bps.yaml",
            execution_config_sha256="sha256:phaseb",
            parquet_data_sha256="sha256:parquetdata",
            returns_per_bar_path="",   # LATE_FILL empty (FIX-T1.1-SYS2-B2: artifact_dir not provided)
            returns_per_bar_sha256="",
            T_obs=250,
            parent_run_id="parent-run-full",
            # cost_anchor_id auto-resolved to "spot_realistic_15bps_v1"
        )
        args["lineage_context"] = lc
        # B2 SYS-fix-1: scalar run_id must agree with lc.run_id
        args["run_id"] = lc.run_id

        _write_to_registry(**args)

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM runs WHERE run_id = ?",
            (args["run_id"],),
        ).fetchone()
        conn.close()

        assert row is not None
        assert row["cost_anchor_id"] == "spot_realistic_15bps_v1"
        assert row["parent_run_id"] == "parent-run-full"

    def test_execution_config_path_kwarg_only_populates_cost_anchor_id(
        self, tmp_path: Path
    ) -> None:
        """execution_config_path kwarg-only in _write_to_registry populates cost_anchor_id."""
        from backtest.engine import _write_to_registry

        db_path = tmp_path / "test_exec_path.db"
        args = self._make_minimal_write_args()
        args["db_path"] = db_path
        args["execution_config_path"] = Path("config/execution_phaseb_spot_15bps.yaml")

        _write_to_registry(**args)

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT cost_anchor_id FROM runs WHERE run_id = ?",
            (args["run_id"],),
        ).fetchone()
        conn.close()

        assert row is not None
        assert row["cost_anchor_id"] == "spot_realistic_15bps_v1"


# ---------------------------------------------------------------------------
# 5. Engine entry-point wiring tests
# ---------------------------------------------------------------------------


class TestRunBacktestLineageContext:
    """run_backtest() accepts lineage_context kwarg-only (opt-in disabled by default)."""

    def test_run_backtest_accepts_lineage_context_kwarg(self) -> None:
        """run_backtest() signature includes lineage_context kwarg without error."""
        import inspect
        from backtest.engine import run_backtest

        sig = inspect.signature(run_backtest)
        assert "lineage_context" in sig.parameters, (
            "run_backtest() must accept lineage_context kwarg-only "
            "(T1.3-D LineageContext propagation surface)"
        )

    def test_lineage_context_default_is_none(self) -> None:
        """lineage_context defaults to None (opt-in=False backward compat)."""
        import inspect
        from backtest.engine import run_backtest

        sig = inspect.signature(run_backtest)
        param = sig.parameters["lineage_context"]
        assert param.default is None, (
            "lineage_context default must be None (opt-in=False preserves backward compat)"
        )


class TestRunRegimeHoldoutLineageContext:
    """run_regime_holdout() accepts and threads lineage_context."""

    def test_run_regime_holdout_accepts_lineage_context_kwarg(self) -> None:
        """run_regime_holdout() signature includes lineage_context kwarg."""
        import inspect
        from backtest.engine import run_regime_holdout

        sig = inspect.signature(run_regime_holdout)
        assert "lineage_context" in sig.parameters, (
            "run_regime_holdout() must accept lineage_context kwarg "
            "(T1.3-D propagation surface point 2)"
        )


class TestRunWalkForwardExecutionConfigPath:
    """run_walk_forward() accepts execution_config_path parameter."""

    def test_run_walk_forward_accepts_execution_config_path(self) -> None:
        """run_walk_forward() signature includes execution_config_path param."""
        import inspect
        from backtest.engine import run_walk_forward

        sig = inspect.signature(run_walk_forward)
        assert "execution_config_path" in sig.parameters, (
            "run_walk_forward() must accept execution_config_path parameter "
            "(T1.3-D propagation surface point 3; currently missing per Codex verification)"
        )

    def test_execution_config_path_default_is_none(self) -> None:
        """run_walk_forward() execution_config_path defaults to None."""
        import inspect
        from backtest.engine import run_walk_forward

        sig = inspect.signature(run_walk_forward)
        param = sig.parameters["execution_config_path"]
        assert param.default is None


# ---------------------------------------------------------------------------
# 6. Public shim re-export from wf_lineage.py
# ---------------------------------------------------------------------------


class TestWfLineagePublicShim:
    """canonicalize_execution_config_path and LineageContext re-exported via wf_lineage."""

    def test_canonicalize_exported_from_wf_lineage(self) -> None:
        """canonicalize_execution_config_path importable from backtest.wf_lineage."""
        from backtest.wf_lineage import canonicalize_execution_config_path  # noqa: F401

        assert callable(canonicalize_execution_config_path)

    def test_lineage_context_exported_from_wf_lineage(self) -> None:
        """LineageContext importable from backtest.wf_lineage."""
        from backtest.wf_lineage import LineageContext  # noqa: F401

        assert dataclasses.is_dataclass(LineageContext)


# ---------------------------------------------------------------------------
# 7. Backward compatibility regression — legacy callers unaffected
# ---------------------------------------------------------------------------


class TestBackwardCompatRegression:
    """Legacy callers must not be broken by T1.3 changes."""

    def test_write_to_registry_legacy_signature_still_works(self, tmp_path: Path) -> None:
        """_write_to_registry with old (pre-T1.3) kwargs succeeds without error."""
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage

        class LegacyStrategy:
            STRATEGY_NAME = "legacy_strategy"

        strategy_cls = LegacyStrategy
        cost_model = MagicMock(spec=ConstantSlippage)
        cost_model.fee_model_label = "effective_7bps_per_side"
        now = datetime(2024, 6, 1, tzinfo=timezone.utc)

        # Call with ONLY pre-T1.3 kwargs (no lineage_context, no execution_config_path)
        _write_to_registry(
            run_id="legacy-run-001",
            strategy_cls=strategy_cls,
            strategy_params={"fast": 20, "slow": 50},
            start_date=now,
            end_date=now,
            effective_start=now,
            warmup_bars=20,
            cost_model=cost_model,
            metrics={
                "initial_capital": 10000.0,
                "final_capital": 10200.0,
                "total_return": 0.02,
                "sharpe_ratio": 1.1,
                "max_drawdown": 0.04,
                "max_drawdown_duration_hours": 48.0,
                "total_trades": 8,
                "win_rate": 0.625,
                "avg_trade_duration_hours": 6.0,
                "avg_trade_return": 0.0025,
                "profit_factor": 1.6,
            },
            db_path=tmp_path / "legacy.db",
        )

    def test_run_backtest_without_lineage_context_succeeds(self) -> None:
        """run_backtest() called without lineage_context doesn't raise TypeError."""
        import inspect
        from backtest.engine import run_backtest

        # Just verify the signature is backward compat — kwarg-only with default None
        sig = inspect.signature(run_backtest)
        params = sig.parameters

        # lineage_context must be KEYWORD_ONLY with default None
        if "lineage_context" in params:
            p = params["lineage_context"]
            assert p.default is None, "lineage_context must default to None"
            # keyword-only or keyword-or-positional both acceptable as long as
            # existing positional callers are unaffected


# ---------------------------------------------------------------------------
# FIX-B1: Duck-typed lineage_context bypass (BLOCKING)
# ---------------------------------------------------------------------------


class TestFakeLineageContextBlocking:
    """FIX-B1: _write_to_registry must reject duck-typed fake objects.

    Both reviewer legs empirically probed: passing a class with the same
    attribute names as LineageContext bypasses isinstance validation and
    allows invalid cost_anchor_id to be written to the registry.

    Required: isinstance(lineage_context, LineageContext) check at entry.
    """

    def _make_minimal_write_args(self, tmp_path: Path) -> dict:
        """Minimal args for _write_to_registry."""
        from backtest.execution_model import ConstantSlippage
        from unittest.mock import MagicMock
        from datetime import datetime, timezone

        class MockStrategy:
            STRATEGY_NAME = "test_strategy"

        cost_model = MagicMock(spec=ConstantSlippage)
        cost_model.fee_model_label = "effective_7bps_per_side"
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        return {
            "run_id": "fake-lc-test-run-001",
            "strategy_cls": MockStrategy,
            "strategy_params": {},
            "start_date": now,
            "end_date": now,
            "effective_start": now,
            "warmup_bars": 0,
            "cost_model": cost_model,
            "metrics": {
                "initial_capital": 10000.0,
                "final_capital": 10000.0,
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0,
                "avg_trade_return": 0.0,
                "profit_factor": 1.0,
            },
            "db_path": tmp_path / "fake_lc.db",
        }

    def test_fake_class_with_lineage_context_attributes_raises_type_error(
        self, tmp_path: Path
    ) -> None:
        """Passing a duck-typed fake object as lineage_context must raise TypeError.

        FIX-B1: isinstance(lineage_context, LineageContext) check required.
        A class with parent_run_id=None and cost_anchor_id="bogus" must be
        rejected before any cost_anchor_id is written.
        """
        from backtest.engine import _write_to_registry

        class FakeLC:
            parent_run_id = None
            cost_anchor_id = "bogus_anchor_id"
            execution_config_path = "config/execution.yaml"

        args = self._make_minimal_write_args(tmp_path)
        args["lineage_context"] = FakeLC()

        with pytest.raises(TypeError, match="LineageContext"):
            _write_to_registry(**args)

    def test_dict_passed_as_lineage_context_raises_type_error(
        self, tmp_path: Path
    ) -> None:
        """Passing a dict as lineage_context must raise TypeError (FIX-B1)."""
        from backtest.engine import _write_to_registry

        fake_dict = {
            "parent_run_id": None,
            "cost_anchor_id": "bogus_from_dict",
            "execution_config_path": "config/execution.yaml",
        }
        args = self._make_minimal_write_args(tmp_path)
        args["lineage_context"] = fake_dict

        with pytest.raises(TypeError, match="LineageContext"):
            _write_to_registry(**args)

    def test_fake_lc_with_invalid_cost_anchor_id_raises_type_error(
        self, tmp_path: Path
    ) -> None:
        """Fake object with invalid cost_anchor_id must raise TypeError, not be written.

        FIX-B1 defensive: the isinstance check must fire BEFORE any write,
        so invalid cost_anchor_id never reaches the registry.
        """
        from backtest.engine import _write_to_registry

        class FakeLCInvalidAnchor:
            parent_run_id = None
            cost_anchor_id = "not_in_mapping"
            execution_config_path = "config/execution.yaml"

        args = self._make_minimal_write_args(tmp_path)
        args["lineage_context"] = FakeLCInvalidAnchor()

        with pytest.raises(TypeError):
            _write_to_registry(**args)

        # Verify nothing was written to the DB (FIX-B1: TypeError fires before
        # create_table/insert_run, so either the DB file doesn't exist yet, or
        # if it exists (e.g., SQLite creates the file on connect), the runs
        # table was never created — check for either condition).
        import sqlite3
        db_file = tmp_path / "fake_lc.db"
        if db_file.exists():
            conn = sqlite3.connect(str(db_file))
            # runs table should not exist (TypeError fired before create_table)
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='runs'"
            ).fetchall()
            conn.close()
            assert len(tables) == 0, (
                "runs table must not exist when TypeError fires before registry write "
                "(FIX-B1: type check must fire before any DB operation)"
            )

    def test_valid_lineage_context_with_bypassed_cost_anchor_raises_value_error(
        self, tmp_path: Path
    ) -> None:
        """Valid LineageContext with mismatched cost_anchor_id via object.__setattr__
        must be caught by defensive re-verification at write boundary (FIX-B1).

        This simulates a future LineageContext bug where __post_init__ is bypassed
        but the object still passes isinstance. The defensive check must catch it.
        """
        from backtest.artifact_schema import LineageContext, COST_ANCHOR_ID_MAPPING
        from backtest.engine import _write_to_registry

        # Build a valid LineageContext first
        lc = LineageContext(
            run_id="run-bypass-test",
            hypothesis_hash="hashbp",
            source_batch_id="batchbp",
            regime_key="v2.regime_holdout",
            engine_commit="aaa",
            current_git_sha="bbb",
            execution_config_path="config/execution.yaml",
            execution_config_sha256="sha256:x",
            parquet_data_sha256="sha256:y",
            returns_per_bar_path="returns.parquet",
            returns_per_bar_sha256="sha256:z",
            T_obs=10,
            parent_run_id=None,
        )
        # cost_anchor_id correctly = "legacy_perp_inspired_7bps_v0" after __post_init__
        assert lc.cost_anchor_id == "legacy_perp_inspired_7bps_v0"

        # Bypass __post_init__ protection: forcibly set a mismatched cost_anchor_id
        # on the frozen instance (simulates future LineageContext bug)
        object.__setattr__(lc, "cost_anchor_id", "bogus_bypassed_anchor")
        object.__setattr__(
            lc, "execution_config_path", "config/execution.yaml"
        )

        args = self._make_minimal_write_args(tmp_path)
        # B2 SYS-fix-1: scalar run_id must agree with lc.run_id to reach the
        # cost_anchor_id defensive re-verification check (otherwise B2 fires first).
        args["run_id"] = lc.run_id
        args["lineage_context"] = lc

        # Defensive re-verification at write boundary must catch the mismatch
        with pytest.raises(ValueError, match="cost_anchor_id"):
            _write_to_registry(**args)


# ---------------------------------------------------------------------------
# FIX-H1: Parallel execution_config_path conflict-check (HIGH)
# ---------------------------------------------------------------------------


class TestHybridExecutionConfigPathConflict:
    """FIX-H1: Parallel conflict-check for execution_config_path dimension.

    T1.3-C HYBRID provides conflict detection for parent_run_id. This fix
    adds the parallel check for execution_config_path: when both scalar
    execution_config_path AND lineage_context are provided, and they disagree
    on the canonicalized path, FAIL CLOSED with ValueError.
    """

    def _make_minimal_write_args(self, tmp_path: Path, run_id: str = "h1-test-run") -> dict:
        from backtest.execution_model import ConstantSlippage
        from unittest.mock import MagicMock
        from datetime import datetime, timezone

        class MockStrategy:
            STRATEGY_NAME = "test_strategy"

        cost_model = MagicMock(spec=ConstantSlippage)
        cost_model.fee_model_label = "effective_7bps_per_side"
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        return {
            "run_id": run_id,
            "strategy_cls": MockStrategy,
            "strategy_params": {},
            "start_date": now,
            "end_date": now,
            "effective_start": now,
            "warmup_bars": 0,
            "cost_model": cost_model,
            "metrics": {
                "initial_capital": 10000.0,
                "final_capital": 10000.0,
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0,
                "avg_trade_return": 0.0,
                "profit_factor": 1.0,
            },
            "db_path": tmp_path / "h1_test.db",
        }

    def test_scalar_execution_config_path_disagrees_with_lineage_context_raises(
        self, tmp_path: Path
    ) -> None:
        """scalar execution_config_path canonicalizes to different key than
        lineage_context.execution_config_path → ValueError (FIX-H1).
        """
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry

        # lineage_context uses phaseb path
        lc = LineageContext(
            run_id="h1-lc-run",
            hypothesis_hash="hash-h1",
            source_batch_id="batch-h1",
            regime_key="v2.regime_holdout",
            engine_commit="aaa",
            current_git_sha="bbb",
            execution_config_path="config/execution_phaseb_spot_15bps.yaml",
            execution_config_sha256="sha256:phaseb",
            parquet_data_sha256="sha256:data",
            returns_per_bar_path="returns.parquet",
            returns_per_bar_sha256="sha256:bar",
            T_obs=20,
            parent_run_id=None,
        )

        args = self._make_minimal_write_args(tmp_path, run_id="h1-conflict-run")
        # B2 SYS-fix-1: align scalar run_id with lc.run_id so B2 does not fire
        # before the execution_config_path conflict check (FIX-H1) can fire.
        args["run_id"] = lc.run_id
        # scalar points to the legacy path — conflicts with lc.execution_config_path
        args["execution_config_path"] = "config/execution.yaml"
        args["lineage_context"] = lc

        with pytest.raises(ValueError, match="execution_config_path"):
            _write_to_registry(**args)

    def test_scalar_execution_config_path_matches_lineage_context_does_not_raise(
        self, tmp_path: Path
    ) -> None:
        """scalar execution_config_path agrees with lineage_context → no conflict."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry

        lc = LineageContext(
            run_id="h1-match-run",
            hypothesis_hash="hash-h1m",
            source_batch_id="batch-h1m",
            regime_key="v2.regime_holdout",
            engine_commit="ccc",
            current_git_sha="ddd",
            execution_config_path="config/execution_phaseb_spot_15bps.yaml",
            execution_config_sha256="sha256:phaseb2",
            parquet_data_sha256="sha256:data2",
            returns_per_bar_path="",   # LATE_FILL empty (FIX-T1.1-SYS2-B2: artifact_dir not provided)
            returns_per_bar_sha256="",
            T_obs=15,
            parent_run_id=None,
        )

        args = self._make_minimal_write_args(tmp_path, run_id="h1-match-ok-run")
        # B2 SYS-fix-1: align scalar run_id with lc.run_id
        args["run_id"] = lc.run_id
        # scalar matches lc.execution_config_path → no conflict
        args["execution_config_path"] = "config/execution_phaseb_spot_15bps.yaml"
        args["lineage_context"] = lc

        # Must not raise
        _write_to_registry(**args)

    def test_scalar_none_lineage_context_has_path_no_conflict(
        self, tmp_path: Path
    ) -> None:
        """scalar execution_config_path=None + lineage_context provides path → no conflict."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry

        lc = LineageContext(
            run_id="h1-none-run",
            hypothesis_hash="hash-h1n",
            source_batch_id="batch-h1n",
            regime_key="v2.regime_holdout",
            engine_commit="eee",
            current_git_sha="fff",
            execution_config_path="config/execution_phaseb_spot_15bps.yaml",
            execution_config_sha256="sha256:n1",
            parquet_data_sha256="sha256:n2",
            returns_per_bar_path="",   # LATE_FILL empty (FIX-T1.1-SYS2-B2: artifact_dir not provided)
            returns_per_bar_sha256="",
            T_obs=12,
            parent_run_id=None,
        )

        args = self._make_minimal_write_args(tmp_path, run_id="h1-none-ok-run")
        # B2 SYS-fix-1: align scalar run_id with lc.run_id
        args["run_id"] = lc.run_id
        args["lineage_context"] = lc
        # No scalar execution_config_path → no conflict

        # Must not raise
        _write_to_registry(**args)


# ---------------------------------------------------------------------------
# FIX-M1: Tighten case-only mismatch test assertion
# ---------------------------------------------------------------------------


class TestCaseOnlyMismatchStrict:
    """FIX-M1: case-only mismatch must fail closed via mapping miss (strict assertion).

    The existing test uses an over-permissive assertion:
      `assert result not in COST_ANCHOR_ID_MAPPING or result == "config/execution.yaml"`
    This allows normcase-silenced mismatches to pass.

    The strict assertion is:
      `assert result not in COST_ANCHOR_ID_MAPPING`
    Case-only mismatches MUST produce a mapping miss, never a silent normalize.
    """

    def test_case_only_mismatch_fails_closed_strict_no_silent_normalize(self) -> None:
        """canonicalize('Config/execution.yaml') must NOT produce 'config/execution.yaml'.

        If canonicalization succeeds (case-insensitive FS), the result must
        NOT be in COST_ANCHOR_ID_MAPPING (mapping miss). It must NOT silently
        normalize case (no normcase). If canonicalization raises ValueError,
        that is also acceptable (strict fail-closed).
        """
        from backtest.artifact_schema import (
            canonicalize_execution_config_path,
            COST_ANCHOR_ID_MAPPING,
        )

        abs_path = _REPO_ROOT / "config" / "Execution.yaml"
        try:
            result = canonicalize_execution_config_path(abs_path)
            # Strict: result must NOT be in mapping (case mismatch = mapping miss)
            # normcase would silently produce "config/execution.yaml" which IS in mapping
            assert result not in COST_ANCHOR_ID_MAPPING, (
                f"canonicalize silently normalized case: got {result!r} which IS in "
                f"COST_ANCHOR_ID_MAPPING. Case-only mismatches must fail closed via "
                f"mapping miss (plan v5 Fv5-1). normcase must NOT be applied."
            )
        except ValueError:
            # ValueError is also acceptable — strict fail-closed
            pass


# ---------------------------------------------------------------------------
# FIX-M2: Empty/whitespace guard in canonicalize_execution_config_path
# ---------------------------------------------------------------------------


class TestCanonicalizeEmptyWhitespaceGuard:
    """FIX-M2: canonicalize_execution_config_path must reject empty/whitespace paths.

    Current behavior: empty string passes Path('') → '.' (repo root) → mapping
    miss (good failure) but error message says '.' not '' (confusing).

    Required: explicit guard at function entry — raise ValueError with message
    identifying the empty/whitespace input.
    """

    def test_empty_string_raises_value_error(self) -> None:
        """canonicalize_execution_config_path('') must raise ValueError (FIX-M2)."""
        from backtest.artifact_schema import canonicalize_execution_config_path

        with pytest.raises(ValueError, match="empty"):
            canonicalize_execution_config_path("")

    def test_whitespace_only_string_raises_value_error(self) -> None:
        """canonicalize_execution_config_path('   ') must raise ValueError (FIX-M2)."""
        from backtest.artifact_schema import canonicalize_execution_config_path

        with pytest.raises(ValueError, match="empty|whitespace"):
            canonicalize_execution_config_path("   ")

    def test_tab_newline_string_raises_value_error(self) -> None:
        """canonicalize_execution_config_path('\\t\\n') must raise ValueError (FIX-M2)."""
        from backtest.artifact_schema import canonicalize_execution_config_path

        with pytest.raises(ValueError, match="empty|whitespace"):
            canonicalize_execution_config_path("\t\n")


# ---------------------------------------------------------------------------
# FIX-L1: HYBRID positive test cases
# ---------------------------------------------------------------------------


class TestHybridPositiveCases:
    """FIX-L1: Positive HYBRID test cases for parent_run_id."""

    def _make_minimal_write_args(self, tmp_path: Path, run_id: str = "l1-run") -> dict:
        from backtest.execution_model import ConstantSlippage
        from unittest.mock import MagicMock
        from datetime import datetime, timezone

        class MockStrategy:
            STRATEGY_NAME = "test_strategy"

        cost_model = MagicMock(spec=ConstantSlippage)
        cost_model.fee_model_label = "effective_7bps_per_side"
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        return {
            "run_id": run_id,
            "strategy_cls": MockStrategy,
            "strategy_params": {},
            "start_date": now,
            "end_date": now,
            "effective_start": now,
            "warmup_bars": 0,
            "cost_model": cost_model,
            "metrics": {
                "initial_capital": 10000.0,
                "final_capital": 10000.0,
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0,
                "avg_trade_return": 0.0,
                "profit_factor": 1.0,
            },
            "db_path": tmp_path / "l1_test.db",
        }

    def test_scalar_parent_run_id_same_as_lc_parent_run_id_passes(
        self, tmp_path: Path
    ) -> None:
        """scalar parent_run_id='A' + lc.parent_run_id='A' → passes; uses 'A'."""
        import sqlite3
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry

        lc = LineageContext(
            run_id="l1-same-run",
            hypothesis_hash="hash-l1s",
            source_batch_id="batch-l1s",
            regime_key="v2.regime_holdout",
            engine_commit="aaa",
            current_git_sha="bbb",
            execution_config_path="config/execution.yaml",
            execution_config_sha256="sha256:l1s",
            parquet_data_sha256="sha256:l1sd",
            returns_per_bar_path="",   # LATE_FILL empty (FIX-T1.1-SYS2-B2: artifact_dir not provided)
            returns_per_bar_sha256="",
            T_obs=5,
            parent_run_id="parent-A",
        )

        args = self._make_minimal_write_args(tmp_path, run_id="l1-same-a-run")
        # B2 SYS-fix-1: align scalar run_id with lc.run_id so B2 does not fire.
        # The DB query must also use lc.run_id since that is what gets written.
        args["run_id"] = lc.run_id
        args["parent_run_id"] = "parent-A"  # same as lc.parent_run_id
        args["lineage_context"] = lc

        # Must not raise — both agree on "parent-A"
        _write_to_registry(**args)

        conn = sqlite3.connect(str(tmp_path / "l1_test.db"))
        row = conn.execute(
            "SELECT parent_run_id FROM runs WHERE run_id = ?", (lc.run_id,)
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "parent-A"

    def test_scalar_parent_run_id_no_lineage_context_passes(
        self, tmp_path: Path
    ) -> None:
        """scalar parent_run_id='A' + no lineage_context → passes; uses 'A'."""
        import sqlite3
        from backtest.engine import _write_to_registry

        args = self._make_minimal_write_args(tmp_path, run_id="l1-no-lc-run")
        args["parent_run_id"] = "parent-A"

        _write_to_registry(**args)

        conn = sqlite3.connect(str(tmp_path / "l1_test.db"))
        row = conn.execute(
            "SELECT parent_run_id FROM runs WHERE run_id = ?", ("l1-no-lc-run",)
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "parent-A"


# ---------------------------------------------------------------------------
# FIX-L2: Legacy pre-existing table migration smoke test
# ---------------------------------------------------------------------------


class TestLegacyTableMigrationSmoke:
    """FIX-L2: create_table() on pre-existing table without cost_anchor_id adds it."""

    def test_create_table_adds_cost_anchor_id_to_existing_table_without_it(self) -> None:
        """Pre-existing runs table WITHOUT cost_anchor_id → create_table() adds it.

        Simulates the ALTER TABLE migration path in create_table().
        """
        import sqlite3
        from backtest.experiment_registry import create_table

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row

        # Create a minimal 'runs' table WITHOUT cost_anchor_id (older schema)
        conn.execute("""
            CREATE TABLE runs (
                run_id TEXT PRIMARY KEY,
                run_type TEXT,
                strategy_name TEXT,
                total_return REAL
            )
        """)
        conn.commit()

        # Verify cost_anchor_id is NOT present before migration
        cursor = conn.execute("PRAGMA table_info(runs)")
        pre_columns = {row[1] for row in cursor.fetchall()}
        assert "cost_anchor_id" not in pre_columns, (
            "Test setup error: cost_anchor_id should not be present before migration"
        )

        # Call create_table() — should ALTER TABLE to add cost_anchor_id
        create_table(conn)

        # Verify cost_anchor_id IS present after migration
        cursor = conn.execute("PRAGMA table_info(runs)")
        post_columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        assert "cost_anchor_id" in post_columns, (
            "create_table() must add cost_anchor_id column to pre-existing tables "
            "without it via ALTER TABLE (T1.3-A migration discipline)."
        )


# ---------------------------------------------------------------------------
# FIX-L3: Behavioral threading tests for run_walk_forward
# ---------------------------------------------------------------------------


class TestRunWalkForwardExecutionConfigPathThreading:
    """FIX-L3: run_walk_forward() threads execution_config_path to _write_to_registry."""

    def test_run_walk_forward_threads_execution_config_path_to_write_registry(
        self,
    ) -> None:
        """run_walk_forward() with execution_config_path threads it to _write_to_registry.

        Monkeypatches _write_to_registry to capture call kwargs.
        Verifies execution_config_path is present in captured calls.
        """
        from datetime import date
        from unittest.mock import patch, MagicMock
        import backtest.engine as engine_mod
        from backtest.engine import run_walk_forward
        from strategies.baseline.sma_crossover import SMACrossover as SMACrossoverStrategy

        captured_calls: list[dict] = []

        def fake_write_to_registry(**kwargs):
            captured_calls.append(kwargs)

        def fake_run_backtest(**kwargs):
            """Minimal stub returning a fake BacktestResult."""
            result = MagicMock()
            result.run_id = str(__import__("uuid").uuid4())
            result.warmup_bars = 0
            result.trades = []
            result.equity_curve = __import__("pandas").Series(
                [10000.0, 10000.0],
                index=__import__("pandas").date_range("2020-01-01", periods=2, freq="h"),
            )
            result.metrics = {
                "initial_capital": 10000.0,
                "final_capital": 10000.0,
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0,
                "avg_trade_return": 0.0,
                "profit_factor": 1.0,
            }
            return result

        exec_path = Path("config/execution.yaml")

        with patch.object(engine_mod, "_write_to_registry", fake_write_to_registry), \
             patch.object(engine_mod, "run_backtest", fake_run_backtest), \
             patch.object(engine_mod, "compute_all_metrics", return_value={
                 "initial_capital": 10000.0, "final_capital": 10000.0,
                 "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                 "max_drawdown_duration_hours": 0.0, "total_trades": 0,
                 "win_rate": 0.0, "avg_trade_duration_hours": 0.0,
                 "avg_trade_return": 0.0, "profit_factor": 1.0,
             }):
            run_walk_forward(
                strategy_cls=SMACrossoverStrategy,
                overall_start=date(2020, 1, 1),
                overall_end=date(2021, 6, 30),
                execution_config_path=exec_path,
            )

        assert len(captured_calls) >= 1, "Expected at least one _write_to_registry call"
        for call_kwargs in captured_calls:
            assert "execution_config_path" in call_kwargs, (
                "execution_config_path must be threaded to _write_to_registry"
            )
            assert call_kwargs["execution_config_path"] == exec_path, (
                f"Expected execution_config_path={exec_path!r}, "
                f"got {call_kwargs.get('execution_config_path')!r}"
            )


# ---------------------------------------------------------------------------
# FIX-H2: Cost-config + registry alignment (run_backtest + run_regime_holdout)
# ---------------------------------------------------------------------------


class TestFIXH2RunBacktestCostConfigDeriveFromLC:
    """FIX-H2: run_backtest() must derive execution_config_path from LC when scalar is None.

    Bug: run_backtest(lineage_context=lc, execution_config_path=None) falls back to
    default 7bps config at line 388-392, but registry records lc.cost_anchor_id.
    Fix: derive scalar execution_config_path from lineage_context.execution_config_path
    before the cost-config loading block.
    """

    def _make_lineage_context(self, config_path_str: str) -> "Any":
        """Construct a minimal LineageContext with a real execution config path."""
        from backtest.artifact_schema import LineageContext
        _REPO_ROOT_STR = str(Path(__file__).resolve().parent.parent)
        return LineageContext(
            run_id="test-run-id-h2",
            hypothesis_hash="abc123",
            source_batch_id="batch-uuid-h2",
            regime_key="v2.regime_holdout",
            engine_commit="deadbeef",
            current_git_sha="cafebabe",
            execution_config_path=config_path_str,
            execution_config_sha256="sha256-placeholder",
            parquet_data_sha256="sha256-parquet-placeholder",
            returns_per_bar_path="returns/candidate.parquet",
            returns_per_bar_sha256="sha256-returns",
            T_obs=100,
            parent_run_id=None,
        )

    def test_run_backtest_lc_provided_scalar_none_loads_lc_config(self) -> None:
        """run_backtest(lineage_context=lc, execution_config_path=None) must load
        execution config from lc.execution_config_path, not the DEFAULT.

        Monkeypatches load_execution_config to capture the path it receives.
        Verifies it is NOT None and matches the LC's canonicalized config path.
        """
        import backtest.engine as engine_mod
        from backtest.artifact_schema import LineageContext
        from unittest.mock import patch, MagicMock
        from datetime import datetime, timezone

        lc = self._make_lineage_context("config/execution_phaseb_spot_15bps.yaml")
        # lc.execution_config_path should be canonicalized to the POSIX key
        assert lc.execution_config_path == "config/execution_phaseb_spot_15bps.yaml"
        assert lc.cost_anchor_id == "spot_realistic_15bps_v1"

        captured_load_paths: list = []

        original_load = engine_mod.load_execution_config

        def capturing_load(path=None):
            captured_load_paths.append(path)
            return original_load()  # always return the default config for Cerebro

        # Patch all expensive engine operations; we only need load_execution_config call
        with patch.object(engine_mod, "load_execution_config", side_effect=capturing_load), \
             patch.object(engine_mod, "ParquetFeed") as mock_feed_cls, \
             patch.object(engine_mod, "bt") as mock_bt, \
             patch.object(engine_mod, "configure_cerebro") as mock_cc, \
             patch.object(engine_mod, "compute_all_metrics", return_value={
                 "initial_capital": 10000.0, "final_capital": 10000.0,
                 "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                 "max_drawdown_duration_hours": 0.0, "total_trades": 0,
                 "win_rate": 0.0, "avg_trade_duration_hours": 0.0,
                 "avg_trade_return": 0.0, "profit_factor": 1.0,
             }), \
             patch.object(engine_mod, "_write_to_registry"), \
             patch.object(engine_mod, "_save_trade_csv", return_value=None):

            # Stub ParquetFeed and Cerebro plumbing
            mock_feed = MagicMock()
            mock_feed_cls.from_parquet.return_value = mock_feed
            mock_cerebro = MagicMock()
            mock_bt.Cerebro.return_value = mock_cerebro
            mock_cost_model = MagicMock()
            mock_cost_model.fee_model_label = "spot_realistic_15bps_v1"
            mock_cc.return_value = mock_cost_model
            strat = MagicMock()
            strat.WARMUP_BARS = 0
            strat.analyzers.trade_collector.get_trades.return_value = []
            strat.analyzers.equity_curve.get_equity_curve.return_value = (
                __import__("pandas").Series(dtype=float)
            )
            mock_cerebro.run.return_value = [strat]

            from strategies.baseline.sma_crossover import SMACrossover
            engine_mod.run_backtest(
                strategy_cls=SMACrossover,
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
                execution_config_path=None,  # scalar None — must derive from LC
                lineage_context=lc,
                write_registry=False,
            )

        # FIX-H2: load_execution_config must have been called with a non-None path
        # that corresponds to the LC's execution_config_path (phaseb_spot_15bps).
        assert len(captured_load_paths) >= 1, (
            "load_execution_config must have been called at least once"
        )
        # The first call must NOT be the no-arg default (which produces legacy 7bps)
        first_call_path = captured_load_paths[0]
        assert first_call_path is not None, (
            "FIX-H2: load_execution_config was called with None (default fallback) "
            "even though lineage_context provided execution_config_path. "
            "Cost-config at runtime diverges from registry's cost_anchor_id — "
            "data integrity violation per CLAUDE.md HARD CONSTRAINT."
        )
        # Verify the path resolves to the LC's canonical key
        from backtest.artifact_schema import canonicalize_execution_config_path
        canon = canonicalize_execution_config_path(first_call_path)
        assert canon == lc.execution_config_path, (
            f"FIX-H2: load_execution_config received path canonicalizing to {canon!r}, "
            f"but lineage_context.execution_config_path={lc.execution_config_path!r}. "
            f"Runtime config diverges from registry anchor."
        )

    def test_run_backtest_backward_compat_lc_none_scalar_none_loads_default(self) -> None:
        """Backward compat: run_backtest(lc=None, execution_config_path=None) → default load.

        No lineage_context: existing behavior unchanged.
        load_execution_config called with no args (default fallback to config/execution.yaml).
        """
        import backtest.engine as engine_mod
        from unittest.mock import patch, MagicMock
        from datetime import datetime, timezone

        captured_load_paths: list = []
        original_load = engine_mod.load_execution_config

        def capturing_load(path=None):
            captured_load_paths.append(path)
            return original_load()

        with patch.object(engine_mod, "load_execution_config", side_effect=capturing_load), \
             patch.object(engine_mod, "ParquetFeed") as mock_feed_cls, \
             patch.object(engine_mod, "bt") as mock_bt, \
             patch.object(engine_mod, "configure_cerebro") as mock_cc, \
             patch.object(engine_mod, "compute_all_metrics", return_value={
                 "initial_capital": 10000.0, "final_capital": 10000.0,
                 "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                 "max_drawdown_duration_hours": 0.0, "total_trades": 0,
                 "win_rate": 0.0, "avg_trade_duration_hours": 0.0,
                 "avg_trade_return": 0.0, "profit_factor": 1.0,
             }), \
             patch.object(engine_mod, "_write_to_registry"), \
             patch.object(engine_mod, "_save_trade_csv", return_value=None):

            mock_feed = MagicMock()
            mock_feed_cls.from_parquet.return_value = mock_feed
            mock_cerebro = MagicMock()
            mock_bt.Cerebro.return_value = mock_cerebro
            mock_cost_model = MagicMock()
            mock_cost_model.fee_model_label = "legacy_perp_inspired_7bps_v0"
            mock_cc.return_value = mock_cost_model
            strat = MagicMock()
            strat.WARMUP_BARS = 0
            strat.analyzers.trade_collector.get_trades.return_value = []
            strat.analyzers.equity_curve.get_equity_curve.return_value = (
                __import__("pandas").Series(dtype=float)
            )
            mock_cerebro.run.return_value = [strat]

            from strategies.baseline.sma_crossover import SMACrossover
            engine_mod.run_backtest(
                strategy_cls=SMACrossover,
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
                execution_config_path=None,  # scalar None, no LC
                lineage_context=None,
                write_registry=False,
            )

        # Backward compat: load_execution_config called with None (default)
        assert len(captured_load_paths) >= 1
        first_call_path = captured_load_paths[0]
        assert first_call_path is None, (
            f"Backward compat broken: expected load_execution_config(None) for "
            f"legacy callers, got load_execution_config({first_call_path!r})"
        )

    def test_run_backtest_backward_compat_lc_none_scalar_provided_loads_scalar(self) -> None:
        """Backward compat: run_backtest(lc=None, execution_config_path=path) → loads scalar.

        Existing Phase 4 behavior: scalar provided, no LC → load from scalar.
        """
        import backtest.engine as engine_mod
        from unittest.mock import patch, MagicMock
        from datetime import datetime, timezone

        captured_load_paths: list = []
        original_load = engine_mod.load_execution_config

        def capturing_load(path=None):
            captured_load_paths.append(path)
            return original_load()

        exec_path = Path(__file__).resolve().parent.parent / "config" / "execution.yaml"

        with patch.object(engine_mod, "load_execution_config", side_effect=capturing_load), \
             patch.object(engine_mod, "ParquetFeed") as mock_feed_cls, \
             patch.object(engine_mod, "bt") as mock_bt, \
             patch.object(engine_mod, "configure_cerebro") as mock_cc, \
             patch.object(engine_mod, "compute_all_metrics", return_value={
                 "initial_capital": 10000.0, "final_capital": 10000.0,
                 "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                 "max_drawdown_duration_hours": 0.0, "total_trades": 0,
                 "win_rate": 0.0, "avg_trade_duration_hours": 0.0,
                 "avg_trade_return": 0.0, "profit_factor": 1.0,
             }), \
             patch.object(engine_mod, "_write_to_registry"), \
             patch.object(engine_mod, "_save_trade_csv", return_value=None):

            mock_feed = MagicMock()
            mock_feed_cls.from_parquet.return_value = mock_feed
            mock_cerebro = MagicMock()
            mock_bt.Cerebro.return_value = mock_cerebro
            mock_cost_model = MagicMock()
            mock_cost_model.fee_model_label = "legacy_perp_inspired_7bps_v0"
            mock_cc.return_value = mock_cost_model
            strat = MagicMock()
            strat.WARMUP_BARS = 0
            strat.analyzers.trade_collector.get_trades.return_value = []
            strat.analyzers.equity_curve.get_equity_curve.return_value = (
                __import__("pandas").Series(dtype=float)
            )
            mock_cerebro.run.return_value = [strat]

            from strategies.baseline.sma_crossover import SMACrossover
            engine_mod.run_backtest(
                strategy_cls=SMACrossover,
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
                execution_config_path=exec_path,  # scalar provided
                lineage_context=None,
                write_registry=False,
            )

        assert len(captured_load_paths) >= 1
        first_call_path = captured_load_paths[0]
        assert first_call_path == exec_path, (
            f"Backward compat broken: expected load_execution_config({exec_path!r}), "
            f"got load_execution_config({first_call_path!r})"
        )

    def test_run_backtest_fix_h1_conflict_still_fires_when_both_non_none_disagree(
        self,
    ) -> None:
        """FIX-H1 conflict check fires when both scalar and LC are provided but disagree.

        Regression: FIX-H2 must not suppress FIX-H1.
        When execution_config_path (scalar) is non-None AND lineage_context is non-None
        and they canonicalize to different paths, _write_to_registry must raise ValueError.
        """
        import backtest.engine as engine_mod
        from backtest.artifact_schema import LineageContext
        from unittest.mock import patch, MagicMock
        from datetime import datetime, timezone

        lc = self._make_lineage_context("config/execution_phaseb_spot_15bps.yaml")
        # scalar points to a different config
        scalar_path = Path(__file__).resolve().parent.parent / "config" / "execution.yaml"

        registry_calls: list[dict] = []
        original_write = None

        # Capture _write_to_registry call to confirm it raises
        import backtest.engine as engine_mod2
        captured_error: list[Exception] = []

        original_write_fn = engine_mod2._write_to_registry

        def capturing_write(**kwargs):
            try:
                original_write_fn(**kwargs)
            except ValueError as exc:
                captured_error.append(exc)
                raise

        with patch.object(engine_mod, "load_execution_config",
                          return_value=engine_mod.load_execution_config()), \
             patch.object(engine_mod, "ParquetFeed") as mock_feed_cls, \
             patch.object(engine_mod, "bt") as mock_bt, \
             patch.object(engine_mod, "configure_cerebro") as mock_cc, \
             patch.object(engine_mod, "compute_all_metrics", return_value={
                 "initial_capital": 10000.0, "final_capital": 10000.0,
                 "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                 "max_drawdown_duration_hours": 0.0, "total_trades": 0,
                 "win_rate": 0.0, "avg_trade_duration_hours": 0.0,
                 "avg_trade_return": 0.0, "profit_factor": 1.0,
             }), \
             patch.object(engine_mod, "_write_to_registry", capturing_write), \
             patch.object(engine_mod, "_save_trade_csv", return_value=None):

            mock_feed = MagicMock()
            mock_feed_cls.from_parquet.return_value = mock_feed
            mock_cerebro = MagicMock()
            mock_bt.Cerebro.return_value = mock_cerebro
            mock_cost_model = MagicMock()
            mock_cost_model.fee_model_label = "legacy_perp_inspired_7bps_v0"
            mock_cc.return_value = mock_cost_model
            strat = MagicMock()
            strat.WARMUP_BARS = 0
            strat.analyzers.trade_collector.get_trades.return_value = []
            strat.analyzers.equity_curve.get_equity_curve.return_value = (
                __import__("pandas").Series(dtype=float)
            )
            mock_cerebro.run.return_value = [strat]

            from strategies.baseline.sma_crossover import SMACrossover
            with pytest.raises(ValueError, match="conflict"):
                engine_mod.run_backtest(
                    strategy_cls=SMACrossover,
                    start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                    end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
                    execution_config_path=scalar_path,  # disagrees with LC
                    lineage_context=lc,
                    write_registry=True,
                )


class TestFIXH2RunRegimeHoldoutCostConfigDeriveFromLC:
    """FIX-H2 applied to run_regime_holdout: same structural bug as run_backtest.

    When run_regime_holdout(lineage_context=lc, execution_config_path=None):
    - run_backtest call at line 1798 receives execution_config_path=None → default config
    - cost_model for registry at line 1822 also uses default config
    Both deviate from lc.execution_config_path when LC carries a non-default path.
    """

    def _make_lineage_context(self, config_path_str: str) -> "Any":
        from backtest.artifact_schema import LineageContext
        return LineageContext(
            run_id="test-run-id-h2-holdout",
            hypothesis_hash="abc123holdout",
            source_batch_id="batch-uuid-h2-holdout",
            regime_key="v2.regime_holdout",
            engine_commit="deadbeef01",
            current_git_sha="cafebabe01",
            execution_config_path=config_path_str,
            execution_config_sha256="sha256-ph",
            parquet_data_sha256="sha256-pq",
            returns_per_bar_path="returns/holdout.parquet",
            returns_per_bar_sha256="sha256-ret",
            T_obs=100,
            parent_run_id=None,
        )

    def test_run_regime_holdout_lc_provided_scalar_none_derives_config_for_backtest(
        self,
    ) -> None:
        """run_regime_holdout(lc=lc, execution_config_path=None) must pass lc's path
        to the inner run_backtest call, not None.

        Captures the execution_config_path arg of the inner run_backtest.
        """
        import backtest.engine as engine_mod
        from backtest.artifact_schema import LineageContext
        from unittest.mock import patch, MagicMock
        import yaml

        lc = self._make_lineage_context("config/execution_phaseb_spot_15bps.yaml")
        assert lc.execution_config_path == "config/execution_phaseb_spot_15bps.yaml"

        captured_backtest_calls: list[dict] = []

        original_run_backtest = engine_mod.run_backtest

        def capturing_run_backtest(**kwargs):
            captured_backtest_calls.append(kwargs)
            # Return a minimal fake BacktestResult
            result = MagicMock()
            result.run_id = "fake-holdout-run-id"
            result.warmup_bars = 0
            result.effective_start = None
            result.metrics = {
                "sharpe_ratio": 1.0, "max_drawdown": 0.05,
                "total_return": 0.1, "total_trades": 10,
                "initial_capital": 10000.0, "final_capital": 11000.0,
            }
            return result

        from strategies.baseline.sma_crossover import SMACrossover

        with patch.object(engine_mod, "run_backtest", capturing_run_backtest), \
             patch.object(engine_mod, "_write_to_registry"), \
             patch.object(engine_mod, "load_execution_config",
                          return_value=engine_mod.load_execution_config()):

            engine_mod.run_regime_holdout(
                dsl=None,
                batch_id="batch-uuid-h2-holdout",
                parent_run_id="parent-run-id",
                strategy_cls=SMACrossover,
                execution_config_path=None,  # scalar None — must derive from LC
                lineage_context=lc,
            )

        assert len(captured_backtest_calls) >= 1, (
            "run_backtest must have been called from run_regime_holdout"
        )
        inner_exec_path = captured_backtest_calls[0].get("execution_config_path")
        assert inner_exec_path is not None, (
            "FIX-H2 (run_regime_holdout): inner run_backtest received "
            "execution_config_path=None even though lineage_context provided a path. "
            "Actual backtest fire at legacy cost vs registry lc.cost_anchor_id — "
            "data integrity violation."
        )
        # Verify it resolves to the LC's canonical key
        from backtest.artifact_schema import canonicalize_execution_config_path
        canon = canonicalize_execution_config_path(inner_exec_path)
        assert canon == lc.execution_config_path, (
            f"FIX-H2 (run_regime_holdout): inner run_backtest path canonicalizes to "
            f"{canon!r} but lc.execution_config_path={lc.execution_config_path!r}"
        )

    def test_run_regime_holdout_lc_provided_scalar_none_derives_config_for_cost_model(
        self,
    ) -> None:
        """run_regime_holdout(lc=lc, execution_config_path=None) must also derive
        the cost_model for registry write from lc's path, not the default.

        Captures the load_execution_config call in the cost_model block (lines 1822-1826).
        """
        import backtest.engine as engine_mod
        from backtest.artifact_schema import LineageContext
        from unittest.mock import patch, MagicMock

        lc = self._make_lineage_context("config/execution_phaseb_spot_15bps.yaml")

        captured_load_paths: list = []
        original_load = engine_mod.load_execution_config

        def capturing_load(path=None):
            captured_load_paths.append(path)
            return original_load()

        fake_run_backtest_result = MagicMock()
        fake_run_backtest_result.run_id = "fake-holdout-run-id-2"
        fake_run_backtest_result.warmup_bars = 0
        fake_run_backtest_result.effective_start = None
        fake_run_backtest_result.metrics = {
            "sharpe_ratio": 1.0, "max_drawdown": 0.05,
            "total_return": 0.1, "total_trades": 10,
            "initial_capital": 10000.0, "final_capital": 11000.0,
        }

        from strategies.baseline.sma_crossover import SMACrossover

        with patch.object(engine_mod, "run_backtest",
                          return_value=fake_run_backtest_result), \
             patch.object(engine_mod, "_write_to_registry"), \
             patch.object(engine_mod, "load_execution_config",
                          side_effect=capturing_load):

            engine_mod.run_regime_holdout(
                dsl=None,
                batch_id="batch-uuid-h2-holdout-2",
                parent_run_id="parent-run-id-2",
                strategy_cls=SMACrossover,
                execution_config_path=None,  # scalar None — derive from LC
                lineage_context=lc,
            )

        # The cost-model load in run_regime_holdout (lines 1822-1826) must have
        # been called with a non-None path matching the LC's config.
        # (There may be multiple calls; we need at least one non-None call)
        non_none_paths = [p for p in captured_load_paths if p is not None]
        assert non_none_paths, (
            "FIX-H2 (run_regime_holdout cost_model): all load_execution_config calls "
            "received None (default path). Registry cost_model will use legacy 7bps "
            "while lc.cost_anchor_id=spot_realistic_15bps_v1 — data integrity violation."
        )
        from backtest.artifact_schema import canonicalize_execution_config_path
        for p in non_none_paths:
            canon = canonicalize_execution_config_path(p)
            assert canon == lc.execution_config_path, (
                f"FIX-H2 (run_regime_holdout cost_model): load path canonicalizes to "
                f"{canon!r} but lc.execution_config_path={lc.execution_config_path!r}"
            )


# ---------------------------------------------------------------------------
# FIX-B1-extension: Defensive parent_run_id re-validation at _write_to_registry
# ---------------------------------------------------------------------------


class TestFIXB1ExtensionParentRunIdDefensiveRevalidation:
    """FIX-B1-extension: _write_to_registry must re-verify parent_run_id at write boundary.

    If caller bypasses LineageContext.__post_init__ via object.__setattr__,
    the empty/whitespace parent_run_id can reach _write_to_registry unchecked.
    Defense-in-depth: mirror the cost_anchor_id defensive check for parent_run_id.
    """

    def _make_valid_lineage_context(self) -> "Any":
        from backtest.artifact_schema import LineageContext
        return LineageContext(
            run_id="test-run-id-b1ext",
            hypothesis_hash="hash-b1ext",
            source_batch_id="batch-b1ext",
            regime_key="v2.regime_holdout",
            engine_commit="commit-b1ext",
            current_git_sha="sha-b1ext",
            execution_config_path="config/execution.yaml",
            execution_config_sha256="sha256-exec",
            parquet_data_sha256="sha256-pq",
            returns_per_bar_path="returns/test.parquet",
            returns_per_bar_sha256="sha256-ret",
            T_obs=50,
            parent_run_id="valid-parent-run-id",
        )

    def _make_minimal_write_kwargs(
        self, lc: "Any"
    ) -> dict:
        """Build minimal kwargs for a _write_to_registry call.

        B2 SYS-fix-1: scalar run_id must agree with lc.run_id. Use lc.run_id
        directly so B2 conflict-check does not fire before the defensive
        re-verification check under test can fire.
        """
        import backtest.engine as engine_mod
        from datetime import datetime, timezone
        from strategies.baseline.sma_crossover import SMACrossover
        mock_cost_model = MagicMock()
        mock_cost_model.fee_model_label = "legacy_perp_inspired_7bps_v0"
        return dict(
            run_id=lc.run_id,  # aligned per B2 SYS-fix-1
            strategy_cls=SMACrossover,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=mock_cost_model,
            metrics={
                "initial_capital": 10000.0, "final_capital": 10000.0,
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0,
                "win_rate": 0.0, "avg_trade_duration_hours": 0.0,
                "avg_trade_return": 0.0, "profit_factor": 1.0,
            },
            lineage_context=lc,
        )

    def test_empty_string_parent_run_id_bypassed_via_setattr_raises_on_write(
        self, tmp_path: Path
    ) -> None:
        """Bypassing __post_init__ to set parent_run_id='' must raise at write boundary.

        object.__setattr__(lc, "parent_run_id", "") bypasses LineageContext validation.
        FIX-T1.1-SYS5-REVALIDATE: revalidate_for_write() now fires first at the
        _write_to_registry SEAL gate, catching this before the old per-field mirrors.
        Match string updated from "defensive re-verification" to "revalidate_for_write"
        (FIX-T1.1-SYS5-REVALIDATE mirror update — old mirror is belt-and-suspenders,
        never reached first).
        """
        import backtest.engine as engine_mod

        lc = self._make_valid_lineage_context()
        # Bypass frozen validation
        object.__setattr__(lc, "parent_run_id", "")

        kwargs = self._make_minimal_write_kwargs(lc)
        kwargs["db_path"] = tmp_path / "test.db"

        with pytest.raises(ValueError, match="revalidate_for_write"):
            engine_mod._write_to_registry(**kwargs)

    def test_whitespace_only_parent_run_id_bypassed_via_setattr_raises_on_write(
        self, tmp_path: Path
    ) -> None:
        """Bypassing __post_init__ to set parent_run_id='   ' must raise at write boundary.

        FIX-T1.1-SYS5-REVALIDATE: revalidate_for_write() now fires first.
        Match string updated from "defensive re-verification" to "revalidate_for_write".
        """
        import backtest.engine as engine_mod

        lc = self._make_valid_lineage_context()
        object.__setattr__(lc, "parent_run_id", "   ")

        kwargs = self._make_minimal_write_kwargs(lc)
        kwargs["db_path"] = tmp_path / "test.db"

        with pytest.raises(ValueError, match="revalidate_for_write"):
            engine_mod._write_to_registry(**kwargs)

    def test_none_parent_run_id_via_setattr_is_valid_passes_write(
        self, tmp_path: Path
    ) -> None:
        """None parent_run_id (set via __setattr__) is valid — must NOT raise.

        None is valid per B2-b for single-run callers without parent linkage.
        """
        import backtest.engine as engine_mod

        lc = self._make_valid_lineage_context()
        # Force to None via setattr (normally None is set at construction)
        object.__setattr__(lc, "parent_run_id", None)

        kwargs = self._make_minimal_write_kwargs(lc)
        kwargs["db_path"] = tmp_path / "test.db"

        # Must not raise — None is valid per B2-b
        try:
            engine_mod._write_to_registry(**kwargs)
        except ValueError as exc:
            if "defensive re-verification" in str(exc):
                pytest.fail(
                    f"_write_to_registry raised defensive re-verification error for "
                    f"parent_run_id=None, which is valid per B2-b. Error: {exc}"
                )


# ---------------------------------------------------------------------------
# FIX-M2-extension: Path('') and Path('.') guard in canonicalize_execution_config_path
# ---------------------------------------------------------------------------


class TestFIXM2ExtensionPathEmptyAndDotGuard:
    """FIX-M2-extension: Path('') and Path('.') must raise ValueError.

    Current FIX-M2 guard: ``if not str(path).strip()`` — catches empty string ''
    but NOT Path('') (str(Path('')) == '.' which is truthy and bypasses the guard).
    """

    def test_path_empty_raises_value_error(self) -> None:
        """Path('') must raise ValueError (not resolve to repo root '.')."""
        from backtest.artifact_schema import canonicalize_execution_config_path

        with pytest.raises(ValueError):
            canonicalize_execution_config_path(Path(""))

    def test_path_dot_raises_value_error(self) -> None:
        """Path('.') must raise ValueError (resolves to repo root itself, not a config)."""
        from backtest.artifact_schema import canonicalize_execution_config_path

        with pytest.raises(ValueError):
            canonicalize_execution_config_path(Path("."))

    def test_path_valid_config_still_works(self) -> None:
        """Path('config') is a directory — does not raise; resolves normally."""
        from backtest.artifact_schema import canonicalize_execution_config_path
        # A relative non-empty, non-dot path: should resolve without error.
        # We don't assert the result value (it may or may not be in the mapping)
        # but we verify no ValueError from the Path('') / Path('.') guard.
        result = canonicalize_execution_config_path("config/execution.yaml")
        assert result == "config/execution.yaml"
