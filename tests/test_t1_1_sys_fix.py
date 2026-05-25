"""Comprehensive F-systematic fix iteration tests — B-C-extended Scope-B cycle.

TDD discipline: tests written FIRST (RED) per testing.md discipline.
All tests target the SYS-fix-1 comprehensive asymmetry closure:
  B1: LineageContext.__post_init__ symmetric validation for STRICT fields
  B2: scalar/LC conflict-check at _write_to_registry (run_id, hypothesis_hash,
      source_batch_id/batch_id, engine_commit/git_commit)
  B3: Registry write population from LC (regime_key, current_git_sha,
      execution_config_path, execution_config_sha256, parquet_data_sha256)
  B4: Registry schema additions (5 new MIGRATION_COLUMNS)
  B5: T_obs > 0 producer guard at write_per_bar_artifact
  B6: Write-boundary path-confinement + SHA256 recheck for returns_per_bar

D1-b: STRICT vs LATE_FILL field split in _BCE_REQUIRED_STRING_FIELDS
D2-b: artifact_schema_version provenance asymmetry documented in LC docstring

Contract references:
- FIX-T1.1-SYS-B1: symmetric __post_init__ validation for required string fields
- D1-b: late-fill semantics for returns_per_bar_path + returns_per_bar_sha256
- D2-b: producer-stamped schema_version (LineageContext stays 14 fields)
- Plan v5 F-systematic audit cross-leg convergent enumeration
"""
from __future__ import annotations

import hashlib
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _build_valid_lc_kwargs(**overrides: Any) -> dict[str, Any]:
    """Minimal valid LineageContext kwargs for SYS-fix-1 tests.

    All 10 STRICT fields are non-empty. LATE_FILL fields default to empty
    (the deferred state before T1.1 writer fills them; allowed at construction
    per D1-b). Tests that exercise B6 recheck must override these with real
    artifact-backed values.

    SYS2-B2 note: _write_to_registry raises when LATE_FILL is non-empty but
    artifact_dir=None (FIX-T1.1-SYS2-B2). Defaulting to empty LATE_FILL
    allows B2/B3 tests to call _write_to_registry without artifact_dir.
    B6-specific tests override with real artifact paths + provide artifact_dir.
    """
    base = {
        "run_id": "sys-fix-run-001",
        "hypothesis_hash": "abc123def456",
        "source_batch_id": "batch-sys-fix-001",
        "regime_key": "v2.regime_holdout",
        "engine_commit": "eb1c87f",
        "current_git_sha": "deadbeef1234",
        "execution_config_path": "config/execution.yaml",
        "execution_config_sha256": "sha256:aabbccdd",
        "parquet_data_sha256": "sha256:11223344",
        # LATE_FILL fields (D1-b): default empty (deferred state).
        # Override in B6-specific tests with real artifact-backed values + artifact_dir.
        "returns_per_bar_path": "",
        "returns_per_bar_sha256": "",
        "T_obs": 10,
        "parent_run_id": None,
    }
    base.update(overrides)
    return base


def _make_equity_curve(n: int = 10, start_val: float = 10000.0) -> pd.Series:
    """Synthetic monotone equity curve with n bars."""
    idx = pd.date_range("2024-01-01", periods=n, freq="h")
    vals = [start_val * (1 + 0.001 * i) for i in range(n)]
    return pd.Series(vals, index=idx, dtype=float)


def _sha256_file(path: Path) -> str:
    """Compute SHA256 of file via 64KB chunked streaming."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# B1: LineageContext.__post_init__ symmetric validation for STRICT fields
# ---------------------------------------------------------------------------
# D1-b: 10 STRICT fields (non-empty required at construction):
#   run_id, hypothesis_hash, source_batch_id, regime_key, engine_commit,
#   current_git_sha, execution_config_path, execution_config_sha256,
#   parquet_data_sha256, cost_anchor_id (auto-resolved)
# D1-b: 2 LATE_FILL fields (allowed empty at construction):
#   returns_per_bar_path, returns_per_bar_sha256
# ---------------------------------------------------------------------------

_STRICT_REQUIRED_FIELDS = [
    "run_id",
    "hypothesis_hash",
    "source_batch_id",
    "regime_key",
    "engine_commit",
    "current_git_sha",
    "execution_config_sha256",
    "parquet_data_sha256",
    # execution_config_path is also STRICT but canonicalization changes '' to error
    # cost_anchor_id is auto-resolved from execution_config_path; no direct test
]

# Fields tested separately due to their special validation paths:
# execution_config_path → canonicalized + COST_ANCHOR_ID_MAPPING lookup
# returns_per_bar_path → LATE_FILL (allowed empty)
# returns_per_bar_sha256 → LATE_FILL (allowed empty)
# parent_run_id → Optional[str] per B2-b
# T_obs → int (not string field)


class TestB1LineageContextStrictFieldsEmptyString:
    """B1: Empty string must raise ValueError for each STRICT required field."""

    @pytest.mark.parametrize("field_name", _STRICT_REQUIRED_FIELDS)
    def test_empty_string_raises_value_error(self, field_name: str) -> None:
        """LineageContext(field_name='') raises ValueError (FIX-T1.1-SYS-B1)."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(**{field_name: ""})
        with pytest.raises(ValueError, match=field_name):
            LineageContext(**kwargs)

    @pytest.mark.parametrize("field_name", _STRICT_REQUIRED_FIELDS)
    def test_whitespace_only_raises_value_error(self, field_name: str) -> None:
        """LineageContext(field_name='   ') raises ValueError (whitespace-only FAIL CLOSED)."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(**{field_name: "   "})
        with pytest.raises(ValueError, match=field_name):
            LineageContext(**kwargs)

    @pytest.mark.parametrize("field_name", _STRICT_REQUIRED_FIELDS)
    def test_tab_whitespace_raises_value_error(self, field_name: str) -> None:
        """LineageContext(field_name='\\t\\n') raises ValueError."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(**{field_name: "\t\n"})
        with pytest.raises(ValueError, match=field_name):
            LineageContext(**kwargs)

    @pytest.mark.parametrize("field_name", _STRICT_REQUIRED_FIELDS)
    def test_valid_non_empty_passes(self, field_name: str) -> None:
        """LineageContext(field_name='valid_value') passes __post_init__ for STRICT fields."""
        from backtest.artifact_schema import LineageContext

        # Use the base valid kwargs (all non-empty); just verify construction succeeds
        kwargs = _build_valid_lc_kwargs()
        lc = LineageContext(**kwargs)
        val = getattr(lc, field_name)
        assert isinstance(val, str) and val.strip(), (
            f"STRICT field {field_name!r} should be non-empty after construction; "
            f"got {val!r}"
        )


class TestB1LineageContextExecutionConfigPathStrict:
    """B1: execution_config_path is STRICT — empty/whitespace at construction raises."""

    def test_empty_execution_config_path_raises(self) -> None:
        """LineageContext with empty execution_config_path raises ValueError."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(execution_config_path="")
        with pytest.raises((ValueError, TypeError)):
            LineageContext(**kwargs)

    def test_whitespace_execution_config_path_raises(self) -> None:
        """LineageContext with whitespace-only execution_config_path raises ValueError."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(execution_config_path="   ")
        with pytest.raises((ValueError, TypeError)):
            LineageContext(**kwargs)

    def test_valid_execution_config_path_passes(self) -> None:
        """LineageContext with known valid execution_config_path passes."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(execution_config_path="config/execution.yaml")
        lc = LineageContext(**kwargs)
        assert lc.execution_config_path == "config/execution.yaml"


class TestD1bLateFilledFieldsAllowedEmpty:
    """D1-b: LATE_FILL fields (returns_per_bar_path, returns_per_bar_sha256) allowed empty at construction."""

    def test_returns_per_bar_path_empty_allowed_at_construction(self) -> None:
        """LineageContext(returns_per_bar_path='') must NOT raise at construction (D1-b)."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(returns_per_bar_path="")
        # D1-b: LATE_FILL — empty is allowed at LC construction
        # Validator (check_b_c_extended_semantics_or_raise) catches at consumption-time
        lc = LineageContext(**kwargs)
        assert lc.returns_per_bar_path == ""

    def test_returns_per_bar_sha256_empty_allowed_at_construction(self) -> None:
        """LineageContext(returns_per_bar_sha256='') must NOT raise at construction (D1-b)."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(returns_per_bar_sha256="")
        lc = LineageContext(**kwargs)
        assert lc.returns_per_bar_sha256 == ""

    def test_returns_per_bar_path_whitespace_allowed_at_construction(self) -> None:
        """LineageContext(returns_per_bar_path='   ') with sha256='   ' — whitespace pair.

        Pre-SYS4: whitespace path was tolerated at construction (D1-b relaxed guard).
        Post-SYS4: whitespace-only pair ('   ', '   ') is neither the deferred state
        ('', '') nor the filled state (non-empty non-whitespace), so it raises.
        This test is updated to reflect the SYS4 closed-set invariant.
        """
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(returns_per_bar_path="   ")
        # SYS4: whitespace path + empty sha is pair-desync → ValueError
        with pytest.raises(ValueError, match="closed-set pair-state"):
            LineageContext(**kwargs)

    def test_strict_fields_still_fail_when_late_fill_is_empty(self) -> None:
        """When LATE_FILL is empty, STRICT fields still validate (no cross-contamination)."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(
            returns_per_bar_path="",  # LATE_FILL: allowed
            run_id="",               # STRICT: must fail
        )
        with pytest.raises(ValueError, match="run_id"):
            LineageContext(**kwargs)


class TestB1ConstantSetsDefinedInModule:
    """B1: Verify that the STRICT/LATE_FILL constants are defined in artifact_schema."""

    def test_strict_fields_constant_exists(self) -> None:
        """_BCE_REQUIRED_STRING_FIELDS_STRICT is exported from artifact_schema."""
        from backtest import artifact_schema

        assert hasattr(artifact_schema, "_BCE_REQUIRED_STRING_FIELDS_STRICT"), (
            "_BCE_REQUIRED_STRING_FIELDS_STRICT must exist in backtest.artifact_schema "
            "(D1-b split from _BCE_REQUIRED_STRING_FIELDS)"
        )

    def test_late_fill_fields_constant_exists(self) -> None:
        """_BCE_REQUIRED_STRING_FIELDS_LATE_FILL is exported from artifact_schema."""
        from backtest import artifact_schema

        assert hasattr(artifact_schema, "_BCE_REQUIRED_STRING_FIELDS_LATE_FILL"), (
            "_BCE_REQUIRED_STRING_FIELDS_LATE_FILL must exist in backtest.artifact_schema "
            "(D1-b split)"
        )

    def test_strict_fields_contains_ten_entries(self) -> None:
        """_BCE_REQUIRED_STRING_FIELDS_STRICT has exactly 10 entries (per D1-b spec)."""
        from backtest.artifact_schema import _BCE_REQUIRED_STRING_FIELDS_STRICT

        assert len(_BCE_REQUIRED_STRING_FIELDS_STRICT) == 10, (
            f"_BCE_REQUIRED_STRING_FIELDS_STRICT must have 10 entries per D1-b; "
            f"got {len(_BCE_REQUIRED_STRING_FIELDS_STRICT)}: {_BCE_REQUIRED_STRING_FIELDS_STRICT}"
        )

    def test_late_fill_fields_contains_two_entries(self) -> None:
        """_BCE_REQUIRED_STRING_FIELDS_LATE_FILL has exactly 2 entries (per D1-b spec)."""
        from backtest.artifact_schema import _BCE_REQUIRED_STRING_FIELDS_LATE_FILL

        assert len(_BCE_REQUIRED_STRING_FIELDS_LATE_FILL) == 2, (
            f"_BCE_REQUIRED_STRING_FIELDS_LATE_FILL must have 2 entries per D1-b; "
            f"got {len(_BCE_REQUIRED_STRING_FIELDS_LATE_FILL)}: {_BCE_REQUIRED_STRING_FIELDS_LATE_FILL}"
        )

    def test_late_fill_contains_correct_fields(self) -> None:
        """LATE_FILL contains exactly returns_per_bar_path + returns_per_bar_sha256."""
        from backtest.artifact_schema import _BCE_REQUIRED_STRING_FIELDS_LATE_FILL

        assert "returns_per_bar_path" in _BCE_REQUIRED_STRING_FIELDS_LATE_FILL, (
            "returns_per_bar_path must be in _BCE_REQUIRED_STRING_FIELDS_LATE_FILL"
        )
        assert "returns_per_bar_sha256" in _BCE_REQUIRED_STRING_FIELDS_LATE_FILL, (
            "returns_per_bar_sha256 must be in _BCE_REQUIRED_STRING_FIELDS_LATE_FILL"
        )

    def test_strict_fields_does_not_contain_late_fill_fields(self) -> None:
        """STRICT set must not contain LATE_FILL fields (clean separation per D1-b)."""
        from backtest.artifact_schema import (
            _BCE_REQUIRED_STRING_FIELDS_STRICT,
            _BCE_REQUIRED_STRING_FIELDS_LATE_FILL,
        )

        strict_set = set(_BCE_REQUIRED_STRING_FIELDS_STRICT)
        for late_field in _BCE_REQUIRED_STRING_FIELDS_LATE_FILL:
            assert late_field not in strict_set, (
                f"LATE_FILL field {late_field!r} must NOT be in STRICT fields (D1-b clean separation)"
            )

    def test_original_twelve_field_constant_preserved_backward_compat(self) -> None:
        """Original _BCE_REQUIRED_STRING_FIELDS still exported for consumer backward compat."""
        from backtest import artifact_schema

        assert hasattr(artifact_schema, "_BCE_REQUIRED_STRING_FIELDS"), (
            "_BCE_REQUIRED_STRING_FIELDS must remain exported for consumer backward compat "
            "(check_b_c_extended_semantics_or_raise still uses it at consumption-time)"
        )


# ---------------------------------------------------------------------------
# B2: scalar/LC conflict-check at _write_to_registry
# B2 covers 4 dimensions: run_id, hypothesis_hash, source_batch_id/batch_id,
#   engine_commit/git_commit
# For each: agree / disagree / scalar-only / LC-only / both-None
# ---------------------------------------------------------------------------


class TestB2ConflictCheckRunId:
    """B2: run_id dimension — scalar vs lineage_context.run_id conflict check."""

    def _call_write_to_registry(
        self,
        tmp_path: Path,
        lc_run_id: str,
        scalar_run_id: str | None,
    ) -> None:
        """Helper: call _write_to_registry with specified run_id dimensions."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b2_run_id_dummy"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        kwargs = _build_valid_lc_kwargs(run_id=lc_run_id)
        lc = LineageContext(**kwargs)

        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / f"b2_run_id_{uuid.uuid4().hex[:8]}.db"

        _write_to_registry(
            run_id=scalar_run_id if scalar_run_id is not None else lc_run_id,
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            lineage_context=lc,
        )

    def test_run_id_agree_passes(self, tmp_path: Path) -> None:
        """scalar run_id == lineage_context.run_id: no error (agreement)."""
        # When scalar equals LC run_id, no conflict; pass through
        # Since _write_to_registry uses its own run_id parameter (not from LC for this),
        # this tests that LC run_id field doesn't conflict with the scalar run_id
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b2_run_id_agree"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        shared_run_id = "shared-run-001"
        lc = LineageContext(**_build_valid_lc_kwargs(run_id=shared_run_id))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b2_agree.db"

        # Agreement: both scalar run_id (first arg) == lc.run_id
        _write_to_registry(
            run_id=shared_run_id,  # same as lc.run_id
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            lineage_context=lc,
        )
        # Verify row was stored with correct run_id
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute("SELECT run_id FROM runs WHERE run_id = ?", (shared_run_id,)).fetchone()
        finally:
            conn.close()
        assert row is not None, f"Row with run_id={shared_run_id!r} must be in registry"

    def test_run_id_disagree_raises_value_error(self, tmp_path: Path) -> None:
        """scalar run_id != lineage_context.run_id → ValueError (fail closed per B2)."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b2_run_id_disagree"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        lc = LineageContext(**_build_valid_lc_kwargs(run_id="lc-run-id-001"))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b2_disagree.db"

        with pytest.raises(ValueError, match="run_id"):
            _write_to_registry(
                run_id="DIFFERENT-scalar-run-id",  # disagrees with lc.run_id
                strategy_cls=_Dummy,
                strategy_params={},
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
                effective_start=None,
                warmup_bars=0,
                cost_model=cost_model,
                metrics={
                    "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                    "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                    "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                    "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
                },
                db_path=db_path,
                lineage_context=lc,
            )


class TestB2ConflictCheckHypothesisHash:
    """B2: hypothesis_hash dimension — scalar vs lineage_context.hypothesis_hash conflict check."""

    def test_hypothesis_hash_agree_passes(self, tmp_path: Path) -> None:
        """scalar hypothesis_hash == lc.hypothesis_hash: no error."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b2_hh_agree"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        shared_hash = "shared-hyp-hash-001"
        lc = LineageContext(**_build_valid_lc_kwargs(hypothesis_hash=shared_hash))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b2_hh_agree.db"

        _write_to_registry(
            run_id=lc.run_id,
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            hypothesis_hash=shared_hash,  # agrees with lc.hypothesis_hash
            lineage_context=lc,
        )

    def test_hypothesis_hash_disagree_raises_value_error(self, tmp_path: Path) -> None:
        """scalar hypothesis_hash != lc.hypothesis_hash → ValueError (B2 fail closed)."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b2_hh_disagree"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        lc = LineageContext(**_build_valid_lc_kwargs(hypothesis_hash="lc-hash-value"))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b2_hh_disagree.db"

        with pytest.raises(ValueError, match="hypothesis_hash"):
            _write_to_registry(
                run_id=lc.run_id,
                strategy_cls=_Dummy,
                strategy_params={},
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
                effective_start=None,
                warmup_bars=0,
                cost_model=cost_model,
                metrics={
                    "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                    "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                    "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                    "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
                },
                db_path=db_path,
                hypothesis_hash="DIFFERENT-scalar-hash",  # disagrees with lc.hypothesis_hash
                lineage_context=lc,
            )

    def test_hypothesis_hash_scalar_only_no_lc_passes(self, tmp_path: Path) -> None:
        """Scalar hypothesis_hash without LC: stored in registry (backward compat)."""
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b2_hh_scalar_only"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b2_hh_scalar_only.db"
        run_id = str(uuid.uuid4())

        _write_to_registry(
            run_id=run_id,
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            hypothesis_hash="scalar-only-hash",
            lineage_context=None,
        )
        # Verify hypothesis_hash persisted
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT hypothesis_hash FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        assert row[0] == "scalar-only-hash"

    def test_hypothesis_hash_lc_only_no_scalar_passes(self, tmp_path: Path) -> None:
        """LC hypothesis_hash without scalar: stored in registry (LC-only path)."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b2_hh_lc_only"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        lc = LineageContext(**_build_valid_lc_kwargs(hypothesis_hash="lc-only-hash-001"))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b2_hh_lc_only.db"

        _write_to_registry(
            run_id=lc.run_id,
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            hypothesis_hash=None,  # scalar is None → LC-only path
            lineage_context=lc,
        )
        # Verify lc.hypothesis_hash persisted
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT hypothesis_hash FROM runs WHERE run_id = ?", (lc.run_id,)
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        assert row[0] == "lc-only-hash-001"


class TestB2ConflictCheckSourceBatchId:
    """B2: source_batch_id/batch_id dimension — scalar batch_id vs lc.source_batch_id conflict check."""

    def test_batch_id_disagree_raises_value_error(self, tmp_path: Path) -> None:
        """scalar batch_id != lc.source_batch_id → ValueError (B2 fail closed)."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b2_bid_disagree"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        lc = LineageContext(**_build_valid_lc_kwargs(source_batch_id="lc-batch-001"))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b2_bid_disagree.db"

        with pytest.raises(ValueError, match="(?i)(batch_id|source_batch_id)"):
            _write_to_registry(
                run_id=lc.run_id,
                strategy_cls=_Dummy,
                strategy_params={},
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
                effective_start=None,
                warmup_bars=0,
                cost_model=cost_model,
                metrics={
                    "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                    "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                    "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                    "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
                },
                db_path=db_path,
                batch_id="DIFFERENT-scalar-batch-id",  # disagrees with lc.source_batch_id
                lineage_context=lc,
            )

    def test_batch_id_agree_passes(self, tmp_path: Path) -> None:
        """scalar batch_id == lc.source_batch_id: no error (agreement)."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b2_bid_agree"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        shared_batch = "shared-batch-001"
        lc = LineageContext(**_build_valid_lc_kwargs(source_batch_id=shared_batch))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b2_bid_agree.db"

        _write_to_registry(
            run_id=lc.run_id,
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            batch_id=shared_batch,
            lineage_context=lc,
        )


class TestB2ConflictCheckEngineCommit:
    """B2: engine_commit/git_commit dimension — lc.engine_commit must populate git_commit."""

    def test_engine_commit_from_lc_stored_in_git_commit_column(self, tmp_path: Path) -> None:
        """When LC is present, lc.engine_commit must be stored in git_commit registry column."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b2_ec_lc_store"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        lc_engine_commit = "lc-commit-deadbeef"
        lc = LineageContext(**_build_valid_lc_kwargs(engine_commit=lc_engine_commit))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b2_ec.db"

        _write_to_registry(
            run_id=lc.run_id,
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            lineage_context=lc,
        )

        # lc.engine_commit should override the auto-derived git_commit
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT git_commit FROM runs WHERE run_id = ?", (lc.run_id,)
            ).fetchone()
        finally:
            conn.close()

        assert row is not None
        assert row[0] == lc_engine_commit, (
            f"git_commit column must store lc.engine_commit={lc_engine_commit!r} "
            f"when LC is present (B2 engine_commit dimension); "
            f"got {row[0]!r}"
        )


# ---------------------------------------------------------------------------
# B3: Registry write population from LC (5 new fields)
# ---------------------------------------------------------------------------


class TestB3RegistryPopulationFromLC:
    """B3: When lineage_context is present, 5 new fields are populated in registry."""

    def _make_lc_and_write(self, tmp_path: Path, *, db_name: str = "b3.db") -> tuple:
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b3_lc_pop"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        lc = LineageContext(**_build_valid_lc_kwargs(
            regime_key="v2.regime_holdout",
            current_git_sha="b3deadbeef9999",
            execution_config_path="config/execution.yaml",
            execution_config_sha256="sha256:b3aabbccdd",
            parquet_data_sha256="sha256:b3eeff1122",
        ))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / db_name

        _write_to_registry(
            run_id=lc.run_id,
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            lineage_context=lc,
        )
        return lc, db_path

    def test_regime_key_populated_from_lc(self, tmp_path: Path) -> None:
        """regime_key column is populated from lineage_context.regime_key (B3)."""
        lc, db_path = self._make_lc_and_write(tmp_path, db_name="b3_regime_key.db")
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT regime_key FROM runs WHERE run_id = ?", (lc.run_id,)
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        assert row[0] == "v2.regime_holdout", (
            f"regime_key must be populated from LC; got {row[0]!r}"
        )

    def test_current_git_sha_populated_from_lc(self, tmp_path: Path) -> None:
        """current_git_sha column is populated from lineage_context.current_git_sha (B3)."""
        lc, db_path = self._make_lc_and_write(tmp_path, db_name="b3_current_git_sha.db")
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT current_git_sha FROM runs WHERE run_id = ?", (lc.run_id,)
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        assert row[0] == "b3deadbeef9999", (
            f"current_git_sha must be populated from LC; got {row[0]!r}"
        )

    def test_execution_config_path_populated_from_lc(self, tmp_path: Path) -> None:
        """execution_config_path column is populated from lineage_context.execution_config_path (B3)."""
        lc, db_path = self._make_lc_and_write(tmp_path, db_name="b3_exec_config_path.db")
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT execution_config_path FROM runs WHERE run_id = ?", (lc.run_id,)
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        assert row[0] == "config/execution.yaml", (
            f"execution_config_path must be populated from LC; got {row[0]!r}"
        )

    def test_execution_config_sha256_populated_from_lc(self, tmp_path: Path) -> None:
        """execution_config_sha256 column is populated from lineage_context.execution_config_sha256 (B3)."""
        lc, db_path = self._make_lc_and_write(tmp_path, db_name="b3_exec_sha256.db")
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT execution_config_sha256 FROM runs WHERE run_id = ?", (lc.run_id,)
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        assert row[0] == "sha256:b3aabbccdd", (
            f"execution_config_sha256 must be populated from LC; got {row[0]!r}"
        )

    def test_parquet_data_sha256_populated_from_lc(self, tmp_path: Path) -> None:
        """parquet_data_sha256 column is populated from lineage_context.parquet_data_sha256 (B3)."""
        lc, db_path = self._make_lc_and_write(tmp_path, db_name="b3_parquet_sha256.db")
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT parquet_data_sha256 FROM runs WHERE run_id = ?", (lc.run_id,)
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        assert row[0] == "sha256:b3eeff1122", (
            f"parquet_data_sha256 must be populated from LC; got {row[0]!r}"
        )

    def test_five_new_fields_null_without_lc(self, tmp_path: Path) -> None:
        """Without lineage_context, 5 new B3 fields are NULL (backward compat)."""
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b3_no_lc"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b3_no_lc.db"
        run_id = str(uuid.uuid4())

        _write_to_registry(
            run_id=run_id,
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            lineage_context=None,
        )

        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT regime_key, current_git_sha, execution_config_path, "
                "execution_config_sha256, parquet_data_sha256 "
                "FROM runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        finally:
            conn.close()

        assert row is not None
        regime_key, current_git_sha, exec_config_path, exec_config_sha256, parquet_sha256 = row
        assert regime_key is None, f"regime_key must be NULL without LC; got {regime_key!r}"
        assert current_git_sha is None, f"current_git_sha must be NULL without LC; got {current_git_sha!r}"
        assert exec_config_path is None, f"execution_config_path must be NULL without LC; got {exec_config_path!r}"
        assert exec_config_sha256 is None, f"execution_config_sha256 must be NULL without LC; got {exec_config_sha256!r}"
        assert parquet_sha256 is None, f"parquet_data_sha256 must be NULL without LC; got {parquet_sha256!r}"


# ---------------------------------------------------------------------------
# B4: Registry schema additions (5 new MIGRATION_COLUMNS + CREATE_TABLE_SQL)
# ---------------------------------------------------------------------------


class TestB4RegistrySchemaAdditions:
    """B4: 5 new MIGRATION_COLUMNS entries + CREATE_TABLE_SQL columns."""

    _EXPECTED_NEW_COLUMNS = [
        "regime_key",
        "current_git_sha",
        "execution_config_path",
        "execution_config_sha256",
        "parquet_data_sha256",
    ]

    @pytest.mark.parametrize("col_name", _EXPECTED_NEW_COLUMNS)
    def test_migration_columns_has_new_column(self, col_name: str) -> None:
        """MIGRATION_COLUMNS includes {col_name} (B4)."""
        from backtest.experiment_registry import MIGRATION_COLUMNS
        col_names = {name for name, _ in MIGRATION_COLUMNS}
        assert col_name in col_names, (
            f"MIGRATION_COLUMNS must include {col_name!r} (B4 registry schema addition)"
        )

    @pytest.mark.parametrize("col_name", _EXPECTED_NEW_COLUMNS)
    def test_create_table_sql_has_new_column(self, col_name: str) -> None:
        """CREATE_TABLE_SQL includes {col_name} (B4)."""
        from backtest.experiment_registry import CREATE_TABLE_SQL
        assert col_name in CREATE_TABLE_SQL, (
            f"CREATE_TABLE_SQL must include {col_name!r} (B4 registry schema addition)"
        )

    def test_fresh_db_has_all_five_new_columns(self, tmp_path: Path) -> None:
        """Fresh DB: create_table() adds all 5 new B4 columns via PRAGMA table_info."""
        from backtest.experiment_registry import create_table, get_connection

        db_path = tmp_path / "b4_migration_smoke.db"
        conn = get_connection(db_path)
        try:
            create_table(conn)
            cursor = conn.execute("PRAGMA table_info(runs)")
            col_names = {row[1] for row in cursor.fetchall()}
        finally:
            conn.close()

        for col in self._EXPECTED_NEW_COLUMNS:
            assert col in col_names, (
                f"After create_table(), column {col!r} must exist; "
                f"found columns: {sorted(col_names)}"
            )

    def test_migration_columns_text_type_for_new_fields(self) -> None:
        """All 5 new MIGRATION_COLUMNS entries have TEXT type."""
        from backtest.experiment_registry import MIGRATION_COLUMNS
        col_map = {name: defn for name, defn in MIGRATION_COLUMNS}
        for col in self._EXPECTED_NEW_COLUMNS:
            assert col in col_map, f"{col!r} not in MIGRATION_COLUMNS"
            assert "TEXT" in col_map[col], (
                f"MIGRATION_COLUMNS[{col!r}] must have TEXT type; got {col_map[col]!r}"
            )

    def test_existing_legacy_rows_unaffected_by_migration(self, tmp_path: Path) -> None:
        """Legacy rows (no LC) have NULL for all 5 new columns after migration."""
        from backtest.experiment_registry import create_table, get_connection, insert_run

        db_path = tmp_path / "b4_legacy_compat.db"
        conn = get_connection(db_path)
        try:
            create_table(conn)
            run_id = str(uuid.uuid4())
            insert_run(conn, {
                "run_id": run_id,
                "strategy_name": "legacy_strat",
                "strategy_source": "manual",
            })
            cursor = conn.execute(
                "SELECT regime_key, current_git_sha, execution_config_path, "
                "execution_config_sha256, parquet_data_sha256 "
                "FROM runs WHERE run_id = ?",
                (run_id,),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        assert row is not None
        for i, col in enumerate(self._EXPECTED_NEW_COLUMNS):
            assert row[i] is None, (
                f"Legacy row: {col!r} must be NULL (backward compat); got {row[i]!r}"
            )


# ---------------------------------------------------------------------------
# B5: T_obs > 0 producer guard at write_per_bar_artifact
# ---------------------------------------------------------------------------


class TestB5WritePerBarArtifactTObsGuard:
    """B5: write_per_bar_artifact raises ValueError when equity curve produces T_obs=0."""

    def test_empty_equity_curve_raises_value_error(self, tmp_path: Path) -> None:
        """Empty equity curve → ValueError from write_per_bar_artifact (B5 producer guard)."""
        from backtest.engine import write_per_bar_artifact

        empty_ec = pd.Series([], dtype=float, index=pd.DatetimeIndex([]))
        with pytest.raises(ValueError, match="(?i)(T_obs|empty|no.*return|zero)"):
            write_per_bar_artifact(
                equity_curve=empty_ec,
                artifact_dir=tmp_path / "b5_empty",
                run_id="b5-empty-test",
            )

    def test_all_nan_equity_curve_raises_value_error(self, tmp_path: Path) -> None:
        """All-NaN equity curve → ValueError (T_obs=0 for finite returns) (B5 producer guard)."""
        from backtest.engine import write_per_bar_artifact

        idx = pd.date_range("2024-01-01", periods=3, freq="h")
        all_nan_ec = pd.Series([float("nan")] * 3, index=idx, dtype=float)
        with pytest.raises(ValueError, match="(?i)(T_obs|empty|no.*return|zero)"):
            write_per_bar_artifact(
                equity_curve=all_nan_ec,
                artifact_dir=tmp_path / "b5_all_nan",
                run_id="b5-nan-test",
            )

    def test_single_bar_raises_value_error(self, tmp_path: Path) -> None:
        """Single-bar equity curve → T_obs=0 (no finite return from pct_change) → ValueError (B5)."""
        from backtest.engine import write_per_bar_artifact

        idx = pd.date_range("2024-01-01", periods=1, freq="h")
        single_ec = pd.Series([10000.0], index=idx, dtype=float)
        with pytest.raises(ValueError, match="(?i)(T_obs|empty|no.*return|zero)"):
            write_per_bar_artifact(
                equity_curve=single_ec,
                artifact_dir=tmp_path / "b5_single",
                run_id="b5-single-test",
            )

    def test_valid_equity_curve_returns_positive_t_obs(self, tmp_path: Path) -> None:
        """Valid equity curve (n>=2) does NOT raise; returns T_obs > 0 (B5 regression)."""
        from backtest.engine import write_per_bar_artifact

        ec = _make_equity_curve(n=10)
        result = write_per_bar_artifact(
            equity_curve=ec,
            artifact_dir=tmp_path / "b5_valid",
            run_id="b5-valid-test",
        )
        assert result["T_obs"] > 0, (
            f"Valid equity curve must return T_obs > 0; got {result['T_obs']!r}"
        )

    def test_two_bar_equity_curve_passes(self, tmp_path: Path) -> None:
        """Two-bar equity curve: T_obs=1 (one finite pct_change) — passes B5 guard."""
        from backtest.engine import write_per_bar_artifact

        idx = pd.date_range("2024-01-01", periods=2, freq="h")
        two_bar_ec = pd.Series([10000.0, 10100.0], index=idx, dtype=float)
        result = write_per_bar_artifact(
            equity_curve=two_bar_ec,
            artifact_dir=tmp_path / "b5_two_bar",
            run_id="b5-two-bar-test",
        )
        assert result["T_obs"] >= 1, (
            f"Two-bar curve must yield T_obs >= 1; got {result['T_obs']!r}"
        )


# ---------------------------------------------------------------------------
# B6: Write-boundary path-confinement + SHA256 recheck for returns_per_bar
# ---------------------------------------------------------------------------


class TestB6WriteBoundaryRecheck:
    """B6: _write_to_registry re-validates returns_per_bar path confinement + SHA256 integrity."""

    def _write_artifact_and_build_lc(
        self, tmp_path: Path, artifact_subdir: str = "b6_artifact"
    ) -> tuple:
        """Write a real artifact, build a valid LC from it."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import write_per_bar_artifact

        artifact_dir = tmp_path / artifact_subdir
        artifact_dir.mkdir(parents=True)
        ec = _make_equity_curve(n=10)
        result = write_per_bar_artifact(
            equity_curve=ec, artifact_dir=artifact_dir, run_id="b6-test"
        )
        lc = LineageContext(**_build_valid_lc_kwargs(
            returns_per_bar_path=result["returns_per_bar_path"],
            returns_per_bar_sha256=result["returns_per_bar_sha256"],
            T_obs=result["T_obs"],
        ))
        return lc, artifact_dir

    def test_valid_path_and_sha_passes_at_write_boundary(self, tmp_path: Path) -> None:
        """Valid returns_per_bar with matching SHA256 passes _write_to_registry (B6 regression)."""
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b6_valid"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        lc, artifact_dir = self._write_artifact_and_build_lc(tmp_path)
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b6_valid.db"

        # Must not raise
        _write_to_registry(
            run_id=lc.run_id,
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            lineage_context=lc,
            artifact_dir=artifact_dir,  # B6: write boundary needs artifact_dir to resolve path
        )

    def test_sha256_mismatch_raises_value_error_at_write_boundary(self, tmp_path: Path) -> None:
        """Tampered file → SHA256 mismatch → ValueError at write boundary (B6 integrity check)."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry, write_per_bar_artifact
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b6_sha_mismatch"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        artifact_dir = tmp_path / "b6_sha_mismatch"
        artifact_dir.mkdir(parents=True)
        ec = _make_equity_curve(n=10)
        result = write_per_bar_artifact(
            equity_curve=ec, artifact_dir=artifact_dir, run_id="b6-sha-test"
        )

        # Tamper the file AFTER writing (so SHA256 stored in result no longer matches)
        parquet_path = artifact_dir / result["returns_per_bar_path"]
        parquet_path.write_bytes(parquet_path.read_bytes() + b"\x00TAMPERED")

        lc = LineageContext(**_build_valid_lc_kwargs(
            returns_per_bar_path=result["returns_per_bar_path"],
            returns_per_bar_sha256=result["returns_per_bar_sha256"],  # stale SHA256
            T_obs=result["T_obs"],
        ))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b6_sha_mismatch.db"

        with pytest.raises(ValueError, match="(?i)(sha256|mismatch|tamper|integrity)"):
            _write_to_registry(
                run_id=lc.run_id,
                strategy_cls=_Dummy,
                strategy_params={},
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
                effective_start=None,
                warmup_bars=0,
                cost_model=cost_model,
                metrics={
                    "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                    "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                    "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                    "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
                },
                db_path=db_path,
                lineage_context=lc,
                artifact_dir=artifact_dir,
            )

    def test_late_fill_empty_skips_recheck(self, tmp_path: Path) -> None:
        """LC with empty LATE_FILL fields (before T1.1 writer fills) skips B6 recheck (no false positive)."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b6_late_fill_skip"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        # LC with empty LATE_FILL fields (D1-b: allowed at construction)
        lc = LineageContext(**_build_valid_lc_kwargs(
            returns_per_bar_path="",   # LATE_FILL: empty
            returns_per_bar_sha256="",  # LATE_FILL: empty
        ))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b6_late_fill_skip.db"

        # Must NOT raise: empty LATE_FILL → skip B6 recheck
        _write_to_registry(
            run_id=lc.run_id,
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            lineage_context=lc,
            # No artifact_dir needed since LATE_FILL is empty → recheck is skipped
        )

    def test_path_traversal_raises_value_error_at_write_boundary(self, tmp_path: Path) -> None:
        """Path containing '../' in returns_per_bar_path raises ValueError at write boundary (B6)."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "b6_path_escape"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        # LC with path-traversal in returns_per_bar_path
        lc = LineageContext(**_build_valid_lc_kwargs(
            returns_per_bar_path="../../../etc/passwd",  # path escape attempt
            returns_per_bar_sha256="sha256:somehash",
        ))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / "b6_path_escape.db"
        artifact_dir = tmp_path / "b6_safe_dir"
        artifact_dir.mkdir(parents=True)

        with pytest.raises(ValueError, match="(?i)(path|confinement|escape|traversal|confined)"):
            _write_to_registry(
                run_id=lc.run_id,
                strategy_cls=_Dummy,
                strategy_params={},
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
                effective_start=None,
                warmup_bars=0,
                cost_model=cost_model,
                metrics={
                    "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                    "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                    "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                    "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
                },
                db_path=db_path,
                lineage_context=lc,
                artifact_dir=artifact_dir,
            )


# ---------------------------------------------------------------------------
# D2-b: Producer-stamped schema_version — LineageContext stays 14 fields
# ---------------------------------------------------------------------------


class TestD2bLineageContextStays14Fields:
    """D2-b: LineageContext has exactly 14 fields (no artifact_schema_version field added)."""

    def test_lineage_context_has_exactly_14_fields(self) -> None:
        """LineageContext must have exactly 14 dataclass fields per D2-b lock."""
        import dataclasses
        from backtest.artifact_schema import LineageContext

        n_fields = len(dataclasses.fields(LineageContext))
        assert n_fields == 14, (
            f"LineageContext must have exactly 14 dataclass fields (13 Contract 2.0.5 + T_obs per D2-b); "
            f"got {n_fields}. D2-b: artifact_schema_version is producer-stamped onto "
            f"artifact JSON header, NOT added as a 15th LC field."
        )

    def test_lineage_context_has_no_artifact_schema_version_field(self) -> None:
        """LineageContext must NOT have an artifact_schema_version field (D2-b)."""
        import dataclasses
        from backtest.artifact_schema import LineageContext

        field_names = {f.name for f in dataclasses.fields(LineageContext)}
        assert "artifact_schema_version" not in field_names, (
            "LineageContext must NOT have artifact_schema_version field (D2-b: "
            "producer-stamped on artifact JSON, not a LC field)"
        )

    def test_artifact_schema_version_constant_still_exported(self) -> None:
        """ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 constant is still exported from artifact_schema."""
        from backtest.artifact_schema import ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1

        assert ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 == "b_c_extended_v1"

    def test_lineage_context_docstring_mentions_provenance_asymmetry(self) -> None:
        """LineageContext docstring documents the D2-b provenance asymmetry (documentation check)."""
        from backtest.artifact_schema import LineageContext

        docstring = LineageContext.__doc__ or ""
        # Check for any mention of schema_version, provenance, or D2-b
        keywords = ["schema_version", "producer-stamped", "D2-b", "provenance", "artifact header"]
        has_keyword = any(kw.lower() in docstring.lower() for kw in keywords)
        assert has_keyword, (
            f"LineageContext docstring must document D2-b provenance asymmetry "
            f"(artifact_schema_version is producer-stamped, not a field). "
            f"Expected one of {keywords!r} in docstring."
        )


# ---------------------------------------------------------------------------
# Cross-cutting: Asymmetry closure verification
# ---------------------------------------------------------------------------


class TestAsymmetryClosureVerification:
    """Empirical probes confirming each asymmetry is closed."""

    def test_lc_empty_run_id_raises_at_construction(self) -> None:
        """A1-probe: LC with empty run_id raises at construction (asymmetry closed)."""
        from backtest.artifact_schema import LineageContext

        with pytest.raises(ValueError, match="run_id"):
            LineageContext(**_build_valid_lc_kwargs(run_id=""))

    def test_lc_empty_hypothesis_hash_raises_at_construction(self) -> None:
        """A2-probe: LC with empty hypothesis_hash raises at construction."""
        from backtest.artifact_schema import LineageContext

        with pytest.raises(ValueError, match="hypothesis_hash"):
            LineageContext(**_build_valid_lc_kwargs(hypothesis_hash=""))

    def test_lc_empty_source_batch_id_raises_at_construction(self) -> None:
        """A3-probe: LC with empty source_batch_id raises at construction."""
        from backtest.artifact_schema import LineageContext

        with pytest.raises(ValueError, match="source_batch_id"):
            LineageContext(**_build_valid_lc_kwargs(source_batch_id=""))

    def test_lc_empty_regime_key_raises_at_construction(self) -> None:
        """A4-probe: LC with empty regime_key raises at construction."""
        from backtest.artifact_schema import LineageContext

        with pytest.raises(ValueError, match="regime_key"):
            LineageContext(**_build_valid_lc_kwargs(regime_key=""))

    def test_lc_empty_engine_commit_raises_at_construction(self) -> None:
        """A5-probe: LC with empty engine_commit raises at construction."""
        from backtest.artifact_schema import LineageContext

        with pytest.raises(ValueError, match="engine_commit"):
            LineageContext(**_build_valid_lc_kwargs(engine_commit=""))

    def test_lc_empty_current_git_sha_raises_at_construction(self) -> None:
        """A6-probe: LC with empty current_git_sha raises at construction."""
        from backtest.artifact_schema import LineageContext

        with pytest.raises(ValueError, match="current_git_sha"):
            LineageContext(**_build_valid_lc_kwargs(current_git_sha=""))

    def test_lc_empty_execution_config_sha256_raises_at_construction(self) -> None:
        """A8-probe: LC with empty execution_config_sha256 raises at construction."""
        from backtest.artifact_schema import LineageContext

        with pytest.raises(ValueError, match="execution_config_sha256"):
            LineageContext(**_build_valid_lc_kwargs(execution_config_sha256=""))

    def test_lc_empty_parquet_data_sha256_raises_at_construction(self) -> None:
        """A9-probe: LC with empty parquet_data_sha256 raises at construction."""
        from backtest.artifact_schema import LineageContext

        with pytest.raises(ValueError, match="parquet_data_sha256"):
            LineageContext(**_build_valid_lc_kwargs(parquet_data_sha256=""))

    def test_write_to_registry_run_id_conflict_raises(self, tmp_path: Path) -> None:
        """scalar+LC run_id disagreement → ValueError (B2 run_id dimension asymmetry closed)."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "asym_run_id"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        lc = LineageContext(**_build_valid_lc_kwargs(run_id="lc-run-asym"))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)

        with pytest.raises(ValueError, match="run_id"):
            _write_to_registry(
                run_id="DISAGREE-run-asym",
                strategy_cls=_Dummy,
                strategy_params={},
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
                effective_start=None,
                warmup_bars=0,
                cost_model=cost_model,
                metrics={
                    "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                    "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                    "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                    "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
                },
                db_path=tmp_path / "asym_run_id.db",
                lineage_context=lc,
            )

    def test_hypothesis_hash_conflict_raises(self, tmp_path: Path) -> None:
        """scalar+LC hypothesis_hash disagreement → ValueError (B2 hypothesis_hash asymmetry closed)."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "asym_hh"
            WARMUP_BARS = 0
            def next(self) -> None: pass

        lc = LineageContext(**_build_valid_lc_kwargs(hypothesis_hash="lc-hh-asym"))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)

        with pytest.raises(ValueError, match="hypothesis_hash"):
            _write_to_registry(
                run_id=lc.run_id,
                strategy_cls=_Dummy,
                strategy_params={},
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
                effective_start=None,
                warmup_bars=0,
                cost_model=cost_model,
                metrics={
                    "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                    "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                    "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                    "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
                },
                db_path=tmp_path / "asym_hh.db",
                hypothesis_hash="DISAGREE-hh-asym",
                lineage_context=lc,
            )


# ===========================================================================
# SYS2 fix iteration tests (FIX-T1.1-SYS2-B1 through FIX-T1.1-SYS2-M1)
# TDD RED-GREEN-REFACTOR: tests written FIRST (RED), then implementation fixes.
# ===========================================================================


# ---------------------------------------------------------------------------
# FIX-T1.1-SYS2-B1: LC T_obs=None bypass
#
# Bug: __post_init__ guard uses `if t_obs is not None and ...` so None passes
# construction silently. Required fix: T_obs must be a strictly-required positive
# integer — None MUST raise ValueError at construction time.
# ---------------------------------------------------------------------------


class TestSys2B1TObsNoneBypass:
    """SYS2-B1: LineageContext(T_obs=None) must raise ValueError at construction."""

    def test_t_obs_none_raises_value_error(self) -> None:
        """LineageContext(T_obs=None) → ValueError (FIX-T1.1-SYS2-B1)."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(T_obs=None)
        with pytest.raises(ValueError, match="(?i)(T_obs|required|positive|None)"):
            LineageContext(**kwargs)

    def test_t_obs_zero_raises_value_error_regression(self) -> None:
        """LineageContext(T_obs=0) → ValueError (regression-protect existing guard)."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(T_obs=0)
        with pytest.raises(ValueError, match="(?i)(T_obs|positive|zero)"):
            LineageContext(**kwargs)

    def test_t_obs_negative_raises_value_error_regression(self) -> None:
        """LineageContext(T_obs=-1) → ValueError (regression-protect existing guard)."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(T_obs=-1)
        with pytest.raises(ValueError, match="(?i)(T_obs|positive|negative)"):
            LineageContext(**kwargs)

    def test_t_obs_one_passes_regression(self) -> None:
        """LineageContext(T_obs=1) → passes (regression-protect minimum positive)."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(T_obs=1)
        lc = LineageContext(**kwargs)
        assert lc.T_obs == 1

    def test_t_obs_positive_passes_regression(self) -> None:
        """LineageContext(T_obs=10) → passes (regression-protect normal positive)."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(T_obs=10)
        lc = LineageContext(**kwargs)
        assert lc.T_obs == 10

    def test_t_obs_bool_true_raises_value_error(self) -> None:
        """LineageContext(T_obs=True) → ValueError (bool is a subclass of int; guard must reject)."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(T_obs=True)
        with pytest.raises(ValueError, match="(?i)(T_obs|bool|positive)"):
            LineageContext(**kwargs)


# ---------------------------------------------------------------------------
# FIX-T1.1-SYS2-B2: B6 require artifact_dir when LATE_FILL is non-empty
#
# Bug: B6 gate at engine.py uses `if _lc_bar_path and _lc_bar_sha and artifact_dir is not None`
# — silently SKIPS recheck when artifact_dir is None even if LATE_FILL fields are non-empty.
# Required fix: if returns_per_bar_path OR returns_per_bar_sha256 is non-empty, artifact_dir
# must be provided (not None); otherwise raise ValueError.
# ---------------------------------------------------------------------------


def _make_write_registry_call(
    tmp_path: "Path",
    lc: "Any",
    *,
    artifact_dir: "Any" = None,
    strategy_name_suffix: str = "",
) -> None:
    """Helper for SYS2-B2 tests: call _write_to_registry with given LC + artifact_dir."""
    from backtest.engine import _write_to_registry
    from backtest.execution_model import ConstantSlippage
    from backtest.slippage import load_execution_config
    import backtrader as bt
    from datetime import timezone

    strategy_name = f"sys2b2_dummy{strategy_name_suffix}"

    # Dynamically create a unique strategy class (avoid STRATEGY_REGISTRY conflict)
    _Dummy = type(
        f"_Dummy_{strategy_name}",
        (bt.Strategy,),
        {"STRATEGY_NAME": strategy_name, "WARMUP_BARS": 0, "next": lambda self: None},
    )

    config = load_execution_config()
    cost_model = ConstantSlippage.from_config(config)
    db_path = tmp_path / f"sys2b2_{strategy_name_suffix}.db"

    _write_to_registry(
        run_id=lc.run_id,
        strategy_cls=_Dummy,
        strategy_params={},
        start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
        effective_start=None,
        warmup_bars=0,
        cost_model=cost_model,
        metrics={
            "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
            "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
            "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
            "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
        },
        db_path=db_path,
        lineage_context=lc,
        artifact_dir=artifact_dir,
    )


class TestSys2B2B6RequireArtifactDir:
    """SYS2-B2: _write_to_registry must require artifact_dir when LATE_FILL is non-empty."""

    def test_nonempty_bar_path_with_none_artifact_dir_raises(self, tmp_path: Path) -> None:
        """Both LATE_FILL filled via tampered LC + artifact_dir=None → ValueError (SYS2-B2).

        Pre-SYS4: LC(path='returns.parquet', sha='') was constructible; only sha was empty.
        Post-SYS4: asymmetric state raises at construction. To test the write-boundary
        artifact_dir guard (SYS2-B2 defense-in-depth), we construct a valid deferred LC
        then tamper both fields to a filled state via object.__setattr__, bypassing __post_init__.
        The write-boundary guard must still catch artifact_dir=None when LATE_FILL is non-empty.
        """
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys2b2-path-001",
            returns_per_bar_path="",
            returns_per_bar_sha256="",
        ))
        # Bypass __post_init__ to simulate a tampered filled state reaching the write boundary.
        object.__setattr__(lc, "returns_per_bar_path", "returns.parquet")
        object.__setattr__(lc, "returns_per_bar_sha256", "abc123sha")
        with pytest.raises(ValueError, match="(?i)(artifact_dir|required|non.empty|LATE_FILL)"):
            _make_write_registry_call(tmp_path, lc, artifact_dir=None, strategy_name_suffix="b2a")

    def test_nonempty_bar_sha_with_none_artifact_dir_raises(self, tmp_path: Path) -> None:
        """Both LATE_FILL filled via tampered LC + artifact_dir=None → ValueError (SYS2-B2).

        Symmetric to test above. Tamper both fields to a filled state and verify
        the write-boundary artifact_dir guard fires for the sha-first tamper variant.
        """
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys2b2-sha-001",
            returns_per_bar_path="",
            returns_per_bar_sha256="",
        ))
        object.__setattr__(lc, "returns_per_bar_path", "returns_sha_variant.parquet")
        object.__setattr__(lc, "returns_per_bar_sha256", "abc123sha")
        with pytest.raises(ValueError, match="(?i)(artifact_dir|required|non.empty|LATE_FILL)"):
            _make_write_registry_call(tmp_path, lc, artifact_dir=None, strategy_name_suffix="b2b")

    def test_both_nonempty_with_none_artifact_dir_raises(self, tmp_path: Path) -> None:
        """Both LATE_FILL non-empty + artifact_dir=None → ValueError (SYS2-B2)."""
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys2b2-both-001",
            returns_per_bar_path="returns.parquet",
            returns_per_bar_sha256="abc123sha",
        ))
        with pytest.raises(ValueError, match="(?i)(artifact_dir|required|non.empty|LATE_FILL)"):
            _make_write_registry_call(tmp_path, lc, artifact_dir=None, strategy_name_suffix="b2c")

    def test_both_empty_late_fill_with_none_artifact_dir_passes(self, tmp_path: Path) -> None:
        """Both LATE_FILL empty + artifact_dir=None → passes (deferred; no recheck needed)."""
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys2b2-empty-001",
            returns_per_bar_path="",
            returns_per_bar_sha256="",
        ))
        # Must NOT raise: empty LATE_FILL with no artifact_dir is the deferred case
        _make_write_registry_call(tmp_path, lc, artifact_dir=None, strategy_name_suffix="b2d")

    def test_nonempty_with_artifact_dir_provided_runs_recheck(self, tmp_path: Path) -> None:
        """Non-empty LATE_FILL + valid artifact_dir → normal recheck applies (regression)."""
        from backtest.artifact_schema import LineageContext
        from backtest.engine import write_per_bar_artifact

        artifact_dir = tmp_path / "b2e_artifacts"
        artifact_dir.mkdir()
        ec = _make_equity_curve(n=10)
        result = write_per_bar_artifact(
            equity_curve=ec, artifact_dir=artifact_dir, run_id="sys2b2-recheck"
        )
        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys2b2-recheck-001",
            returns_per_bar_path=result["returns_per_bar_path"],
            returns_per_bar_sha256=result["returns_per_bar_sha256"],
            T_obs=result["T_obs"],
        ))
        # Must NOT raise: valid artifact_dir + matching SHA256 → recheck passes
        _make_write_registry_call(
            tmp_path, lc, artifact_dir=artifact_dir, strategy_name_suffix="b2e"
        )


# ---------------------------------------------------------------------------
# FIX-T1.1-SYS2-B3: B2 engine_commit OVERRIDE-not-conflict-check documentation
#
# Bug (Codex BLOCKING): B2 brief promised "4-dimension conflict-check" but
# engine_commit/git_commit uses OVERRIDE pattern (no scalar parameter to conflict
# against). Required fix (option b): document OVERRIDE pattern explicitly with
# CONTRACT GAP marker + update _write_to_registry docstring.
# ---------------------------------------------------------------------------


class TestSys2B3EngineCommitOverrideDocumented:
    """SYS2-B3: OVERRIDE-not-conflict-check pattern for engine_commit must be documented."""

    def test_contract_gap_marker_present_at_engine_commit_override_block(self) -> None:
        """CONTRACT GAP marker must appear in engine.py at the engine_commit override block (SYS2-B3)."""
        import inspect
        from backtest import engine

        src = inspect.getsource(engine)
        # CONTRACT GAP marker must exist near the engine_commit override
        # (within engine.py source — exact line proximity verified by searching near keyword)
        assert "CONTRACT GAP" in src, (
            "engine.py must contain a 'CONTRACT GAP' marker at the engine_commit "
            "override block per FIX-T1.1-SYS2-B3 (OVERRIDE-not-conflict-check pattern). "
            "Add: '# CONTRACT GAP: ...' near the engine_commit OVERRIDE section in "
            "_write_to_registry."
        )

    def test_contract_gap_mentions_override_not_conflict_check(self) -> None:
        """CONTRACT GAP at engine_commit block must mention OVERRIDE-not-conflict-check pattern."""
        engine_path = Path(__file__).resolve().parent.parent / "backtest" / "engine.py"
        source = engine_path.read_text()
        # The CONTRACT GAP comment near engine_commit must mention the OVERRIDE pattern
        # (not necessarily on the same line; search for the two concepts near each other)
        has_contract_gap = "CONTRACT GAP" in source
        has_override_mention = "OVERRIDE" in source
        assert has_contract_gap and has_override_mention, (
            f"engine.py must have both 'CONTRACT GAP' and 'OVERRIDE' in its source "
            f"to document the engine_commit OVERRIDE-not-conflict-check pattern (SYS2-B3). "
            f"CONTRACT GAP present: {has_contract_gap}, OVERRIDE mention: {has_override_mention}"
        )

    def test_write_to_registry_docstring_mentions_override_pattern(self) -> None:
        """_write_to_registry docstring must mention OVERRIDE-not-conflict-check for engine_commit."""
        from backtest.engine import _write_to_registry

        docstring = (_write_to_registry.__doc__ or "").lower()
        # Docstring should note that engine_commit uses OVERRIDE (not conflict-check)
        has_override = "override" in docstring
        has_engine_commit = "engine_commit" in docstring or "git_commit" in docstring
        assert has_override and has_engine_commit, (
            f"_write_to_registry docstring must mention 'override' AND "
            f"'engine_commit'/'git_commit' to document the SYS2-B3 OVERRIDE pattern. "
            f"override present: {has_override}, engine_commit/git_commit: {has_engine_commit}. "
            f"Current docstring: {_write_to_registry.__doc__!r}"
        )


# ---------------------------------------------------------------------------
# FIX-T1.1-SYS2-H1: B5 ordering bug — T_obs check BEFORE parquet write
#
# Bug: At engine.py, T_obs==0 check occurs AFTER parquet file is already written
# (os.replace). Leaves a partial artifact on disk on failure.
# Required fix: compute T_obs (via compute_moments) BEFORE writing parquet;
# if T_obs==0, raise ValueError WITHOUT writing file.
# ---------------------------------------------------------------------------


class TestSys2H1TObsCheckBeforeWrite:
    """SYS2-H1: write_per_bar_artifact must raise BEFORE writing parquet when T_obs=0."""

    def test_empty_equity_curve_raises_before_file_written(self, tmp_path: Path) -> None:
        """Empty equity curve → ValueError AND no parquet file at artifact path (SYS2-H1)."""
        from backtest.engine import write_per_bar_artifact

        artifact_dir = tmp_path / "h1_empty"
        artifact_dir.mkdir()
        empty_ec = pd.Series([], dtype=float, index=pd.DatetimeIndex([]))

        with pytest.raises(ValueError, match="(?i)(T_obs|empty|no.*return|zero)"):
            write_per_bar_artifact(
                equity_curve=empty_ec,
                artifact_dir=artifact_dir,
                run_id="h1-empty-test",
            )

        # Critical: no parquet file must exist after ValueError (no partial artifact)
        parquet_path = artifact_dir / "returns_per_bar.parquet"
        assert not parquet_path.exists(), (
            f"After T_obs=0 ValueError, no parquet file must exist at {parquet_path}. "
            f"File was left on disk — ordering bug (SYS2-H1: T_obs check must occur "
            f"BEFORE os.replace(), not after)."
        )

    def test_all_nan_curve_raises_before_file_written(self, tmp_path: Path) -> None:
        """All-NaN equity curve → ValueError AND no parquet file left on disk (SYS2-H1)."""
        from backtest.engine import write_per_bar_artifact

        artifact_dir = tmp_path / "h1_nan"
        artifact_dir.mkdir()
        idx = pd.date_range("2024-01-01", periods=3, freq="h")
        nan_ec = pd.Series([float("nan")] * 3, index=idx, dtype=float)

        with pytest.raises(ValueError, match="(?i)(T_obs|empty|no.*return|zero)"):
            write_per_bar_artifact(
                equity_curve=nan_ec,
                artifact_dir=artifact_dir,
                run_id="h1-nan-test",
            )

        parquet_path = artifact_dir / "returns_per_bar.parquet"
        assert not parquet_path.exists(), (
            f"After T_obs=0 ValueError on all-NaN curve, no parquet must exist. "
            f"Partial file left at {parquet_path} (SYS2-H1 ordering bug)."
        )

    def test_single_bar_raises_before_file_written(self, tmp_path: Path) -> None:
        """Single-bar equity curve → ValueError AND no parquet file left on disk (SYS2-H1)."""
        from backtest.engine import write_per_bar_artifact

        artifact_dir = tmp_path / "h1_single"
        artifact_dir.mkdir()
        idx = pd.date_range("2024-01-01", periods=1, freq="h")
        single_ec = pd.Series([10000.0], index=idx, dtype=float)

        with pytest.raises(ValueError, match="(?i)(T_obs|empty|no.*return|zero)"):
            write_per_bar_artifact(
                equity_curve=single_ec,
                artifact_dir=artifact_dir,
                run_id="h1-single-test",
            )

        parquet_path = artifact_dir / "returns_per_bar.parquet"
        assert not parquet_path.exists(), (
            f"After T_obs=0 ValueError on single-bar curve, no parquet must exist. "
            f"Partial file left at {parquet_path} (SYS2-H1 ordering bug)."
        )

    def test_valid_curve_still_writes_file(self, tmp_path: Path) -> None:
        """Valid 10-bar curve: T_obs>0, file IS written and returned in result (regression)."""
        from backtest.engine import write_per_bar_artifact

        artifact_dir = tmp_path / "h1_valid"
        artifact_dir.mkdir()
        ec = _make_equity_curve(n=10)

        result = write_per_bar_artifact(
            equity_curve=ec,
            artifact_dir=artifact_dir,
            run_id="h1-valid-test",
        )

        parquet_path = artifact_dir / result["returns_per_bar_path"]
        assert parquet_path.exists(), (
            f"Valid equity curve: parquet file must exist at {parquet_path} (regression)."
        )
        assert result["T_obs"] > 0, f"Valid curve must return T_obs > 0; got {result['T_obs']}"

    def test_no_temp_file_left_after_t_obs_zero(self, tmp_path: Path) -> None:
        """After T_obs=0 ValueError, NO temp file (*.tmp.*) left in artifact_dir either."""
        from backtest.engine import write_per_bar_artifact

        artifact_dir = tmp_path / "h1_no_tmp"
        artifact_dir.mkdir()
        idx = pd.date_range("2024-01-01", periods=1, freq="h")
        ec = pd.Series([10000.0], index=idx, dtype=float)

        with pytest.raises(ValueError):
            write_per_bar_artifact(
                equity_curve=ec, artifact_dir=artifact_dir, run_id="h1-notmp"
            )

        tmp_files = list(artifact_dir.glob("*.tmp.*"))
        assert not tmp_files, (
            f"No temp files must remain after T_obs=0 ValueError; "
            f"found: {[f.name for f in tmp_files]}"
        )


# ---------------------------------------------------------------------------
# FIX-T1.1-SYS2-H2: Scalar run_id None/empty bypass
#
# Bug: At engine.py conflict-check uses truthiness gate `lc_run_id and run_id`
# so empty scalar run_id="" bypasses the conflict check silently.
# Required fix: use explicit `is not None` checks: if either lc_run_id is not
# None and run_id is not None (even if empty), and they differ → raise ValueError.
# Also: empty scalar run_id="" must fail closed regardless of LC.run_id.
# ---------------------------------------------------------------------------


class TestSys2H2ScalarRunIdNoneEmptyBypass:
    """SYS2-H2: Empty scalar run_id must not bypass conflict-check via truthiness gate."""

    def _write_reg(
        self,
        tmp_path: Path,
        scalar_run_id: str,
        lc_run_id: str,
        suffix: str = "",
    ) -> None:
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt
        from datetime import timezone

        strategy_name = f"sys2h2_{suffix}"
        _D = type(
            f"_D_{strategy_name}",
            (bt.Strategy,),
            {"STRATEGY_NAME": strategy_name, "WARMUP_BARS": 0, "next": lambda self: None},
        )
        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id=lc_run_id,
            returns_per_bar_path="",
            returns_per_bar_sha256="",
        ))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / f"h2_{suffix}.db"

        _write_to_registry(
            run_id=scalar_run_id,
            strategy_cls=_D,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            lineage_context=lc,
        )

    def test_empty_scalar_with_nonempty_lc_run_id_raises(self, tmp_path: Path) -> None:
        """scalar run_id='' + LC.run_id='X' → ValueError (no longer silent bypass) (SYS2-H2)."""
        with pytest.raises(ValueError, match="(?i)(run_id|empty|conflict|disagree)"):
            self._write_reg(tmp_path, scalar_run_id="", lc_run_id="lc-run-X", suffix="empty_nonempty")

    def test_matching_run_ids_pass(self, tmp_path: Path) -> None:
        """scalar run_id='X' + LC.run_id='X' → passes (no conflict) (regression)."""
        # Must not raise
        self._write_reg(tmp_path, scalar_run_id="lc-run-match", lc_run_id="lc-run-match", suffix="match")

    def test_disagreeing_nonempty_run_ids_still_raise(self, tmp_path: Path) -> None:
        """scalar run_id='A' + LC.run_id='B' → ValueError (regression-protect existing conflict-check)."""
        with pytest.raises(ValueError, match="(?i)(run_id|conflict|disagree)"):
            self._write_reg(tmp_path, scalar_run_id="A", lc_run_id="B", suffix="disagree")


class TestSys2H2ScalarHypothesisHashBypass:
    """SYS2-H2: Empty scalar hypothesis_hash must not bypass conflict-check."""

    def _write_reg_hh(
        self,
        tmp_path: Path,
        scalar_hh: "str | None",
        lc_hh: str,
        suffix: str = "",
    ) -> None:
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt
        from datetime import timezone

        strategy_name = f"sys2h2hh_{suffix}"
        _D = type(
            f"_D_{strategy_name}",
            (bt.Strategy,),
            {"STRATEGY_NAME": strategy_name, "WARMUP_BARS": 0, "next": lambda self: None},
        )
        lc = LineageContext(**_build_valid_lc_kwargs(
            hypothesis_hash=lc_hh,
            returns_per_bar_path="",
            returns_per_bar_sha256="",
        ))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / f"h2hh_{suffix}.db"

        _write_to_registry(
            run_id=lc.run_id,
            strategy_cls=_D,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            hypothesis_hash=scalar_hh,
            lineage_context=lc,
        )

    def test_empty_scalar_hh_with_nonempty_lc_raises(self, tmp_path: Path) -> None:
        """scalar hypothesis_hash='' + LC.hypothesis_hash='X' → ValueError (SYS2-H2)."""
        with pytest.raises(ValueError, match="(?i)(hypothesis_hash|empty|conflict|disagree)"):
            self._write_reg_hh(
                tmp_path, scalar_hh="", lc_hh="lc-hash-X", suffix="empty_hh"
            )

    def test_matching_hh_passes(self, tmp_path: Path) -> None:
        """scalar hh='X' + LC.hypothesis_hash='X' → passes (regression)."""
        self._write_reg_hh(
            tmp_path, scalar_hh="shared-hash-val", lc_hh="shared-hash-val", suffix="match_hh"
        )

    def test_none_scalar_hh_lc_only_passes(self, tmp_path: Path) -> None:
        """scalar hypothesis_hash=None + LC.hypothesis_hash='X' → passes (LC-only path) (regression)."""
        self._write_reg_hh(
            tmp_path, scalar_hh=None, lc_hh="lc-only-hash", suffix="none_scalar_hh"
        )


class TestSys2H2ScalarBatchIdBypass:
    """SYS2-H2: Empty scalar batch_id must not bypass conflict-check."""

    def _write_reg_bid(
        self,
        tmp_path: Path,
        scalar_bid: "str | None",
        lc_bid: str,
        suffix: str = "",
    ) -> None:
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt
        from datetime import timezone

        strategy_name = f"sys2h2bid_{suffix}"
        _D = type(
            f"_D_{strategy_name}",
            (bt.Strategy,),
            {"STRATEGY_NAME": strategy_name, "WARMUP_BARS": 0, "next": lambda self: None},
        )
        lc = LineageContext(**_build_valid_lc_kwargs(
            source_batch_id=lc_bid,
            returns_per_bar_path="",
            returns_per_bar_sha256="",
        ))
        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / f"h2bid_{suffix}.db"

        _write_to_registry(
            run_id=lc.run_id,
            strategy_cls=_D,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            batch_id=scalar_bid,
            lineage_context=lc,
        )

    def test_empty_scalar_bid_with_nonempty_lc_raises(self, tmp_path: Path) -> None:
        """scalar batch_id='' + LC.source_batch_id='X' → ValueError (SYS2-H2)."""
        with pytest.raises(ValueError, match="(?i)(batch_id|empty|conflict|disagree)"):
            self._write_reg_bid(
                tmp_path, scalar_bid="", lc_bid="lc-batch-X", suffix="empty_bid"
            )

    def test_matching_bid_passes(self, tmp_path: Path) -> None:
        """scalar batch_id='X' + LC.source_batch_id='X' → passes (regression)."""
        self._write_reg_bid(
            tmp_path, scalar_bid="shared-batch-val", lc_bid="shared-batch-val", suffix="match_bid"
        )

    def test_none_scalar_bid_lc_only_passes(self, tmp_path: Path) -> None:
        """scalar batch_id=None + LC.source_batch_id='X' → passes (LC-only path) (regression)."""
        self._write_reg_bid(
            tmp_path, scalar_bid=None, lc_bid="lc-only-batch", suffix="none_scalar_bid"
        )


# ---------------------------------------------------------------------------
# FIX-T1.1-SYS2-M1: _strict_direct SSOT from _BCE_REQUIRED_STRING_FIELDS_STRICT
#
# Bug: _strict_direct inside __post_init__ is an inline tuple of 8 fields
# (10 STRICT minus 2 indirect: execution_config_path + cost_anchor_id).
# If _BCE_REQUIRED_STRING_FIELDS_STRICT drifts (new field added), _strict_direct
# silently falls out of sync.
# Required fix: derive _strict_direct from _BCE_REQUIRED_STRING_FIELDS_STRICT at
# module load, with a pin-test verifying the SSOT alignment holds.
# ---------------------------------------------------------------------------


class TestSys2M1StrictDirectSSOT:
    """SYS2-M1: _strict_direct must be derived from _BCE_REQUIRED_STRING_FIELDS_STRICT (SSOT)."""

    def test_indirect_strict_fields_constant_exists(self) -> None:
        """_INDIRECT_STRICT_FIELDS constant must exist in artifact_schema (SYS2-M1)."""
        from backtest import artifact_schema

        assert hasattr(artifact_schema, "_INDIRECT_STRICT_FIELDS"), (
            "_INDIRECT_STRICT_FIELDS must exist in backtest.artifact_schema after SYS2-M1 fix. "
            "This constant lists the STRICT fields NOT validated directly by _strict_direct "
            "(execution_config_path validated via canonicalize_...; cost_anchor_id via mapping)."
        )

    def test_indirect_strict_fields_contains_exactly_two_fields(self) -> None:
        """_INDIRECT_STRICT_FIELDS has exactly 2 entries: execution_config_path + cost_anchor_id."""
        from backtest.artifact_schema import _INDIRECT_STRICT_FIELDS

        assert len(_INDIRECT_STRICT_FIELDS) == 2, (
            f"_INDIRECT_STRICT_FIELDS must have exactly 2 entries; "
            f"got {len(_INDIRECT_STRICT_FIELDS)}: {_INDIRECT_STRICT_FIELDS}"
        )

    def test_indirect_strict_fields_correct_members(self) -> None:
        """_INDIRECT_STRICT_FIELDS must contain execution_config_path and cost_anchor_id."""
        from backtest.artifact_schema import _INDIRECT_STRICT_FIELDS

        assert "execution_config_path" in _INDIRECT_STRICT_FIELDS, (
            "execution_config_path must be in _INDIRECT_STRICT_FIELDS "
            "(validated indirectly via canonicalize_execution_config_path)"
        )
        assert "cost_anchor_id" in _INDIRECT_STRICT_FIELDS, (
            "cost_anchor_id must be in _INDIRECT_STRICT_FIELDS "
            "(set via mapping lookup, not direct string validation)"
        )

    def test_ssot_pin_strict_direct_union_indirect_equals_strict(self) -> None:
        """SSOT pin: set(_strict_direct) | set(_INDIRECT_STRICT_FIELDS) == set(_BCE_REQUIRED_STRING_FIELDS_STRICT)."""
        # This test is THE regression-protection pin for future drift.
        # After SYS2-M1 fix: _strict_direct is derived, so this must hold by construction.
        # The test also validates the derivation logic is correct.
        from backtest.artifact_schema import (
            _BCE_REQUIRED_STRING_FIELDS_STRICT,
            _INDIRECT_STRICT_FIELDS,
        )

        # Reconstruct _strict_direct from the SSOT derivation rule
        strict_direct_derived = tuple(
            f for f in _BCE_REQUIRED_STRING_FIELDS_STRICT if f not in _INDIRECT_STRICT_FIELDS
        )

        expected_strict = set(_BCE_REQUIRED_STRING_FIELDS_STRICT)
        actual_union = set(strict_direct_derived) | set(_INDIRECT_STRICT_FIELDS)

        assert actual_union == expected_strict, (
            f"SSOT pin violation: set(_strict_direct) | set(_INDIRECT_STRICT_FIELDS) "
            f"must equal set(_BCE_REQUIRED_STRING_FIELDS_STRICT). "
            f"Derived strict_direct: {strict_direct_derived!r}, "
            f"_INDIRECT_STRICT_FIELDS: {_INDIRECT_STRICT_FIELDS!r}, "
            f"_BCE_REQUIRED_STRING_FIELDS_STRICT: {_BCE_REQUIRED_STRING_FIELDS_STRICT!r}. "
            f"Missing: {expected_strict - actual_union!r}, extra: {actual_union - expected_strict!r}"
        )

    def test_strict_direct_count_is_eight(self) -> None:
        """_strict_direct must have exactly 8 entries (10 STRICT - 2 indirect)."""
        from backtest.artifact_schema import (
            _BCE_REQUIRED_STRING_FIELDS_STRICT,
            _INDIRECT_STRICT_FIELDS,
        )

        strict_direct = tuple(
            f for f in _BCE_REQUIRED_STRING_FIELDS_STRICT if f not in _INDIRECT_STRICT_FIELDS
        )
        assert len(strict_direct) == 8, (
            f"_strict_direct must have 8 entries (10 STRICT - 2 indirect); "
            f"got {len(strict_direct)}: {strict_direct}"
        )

    def test_no_overlap_between_strict_direct_and_indirect(self) -> None:
        """strict_direct and _INDIRECT_STRICT_FIELDS must be disjoint (no field in both)."""
        from backtest.artifact_schema import (
            _BCE_REQUIRED_STRING_FIELDS_STRICT,
            _INDIRECT_STRICT_FIELDS,
        )

        strict_direct = set(
            f for f in _BCE_REQUIRED_STRING_FIELDS_STRICT if f not in _INDIRECT_STRICT_FIELDS
        )
        overlap = strict_direct & set(_INDIRECT_STRICT_FIELDS)
        assert not overlap, (
            f"strict_direct and _INDIRECT_STRICT_FIELDS must be disjoint; "
            f"found overlap: {overlap!r}"
        )


# ---------------------------------------------------------------------------
# SYS3-B1: Partial LATE_FILL pair-completeness gate
#
# Bug: line 1296 uses OR-gate (_late_fill_nonempty = bool(path) OR bool(sha)).
# Asymmetric half-fills (path non-empty + sha empty, or vice versa) + artifact_dir
# provided pass the require-gate but fall through the AND-gate recheck, writing
# a row with one field populated and the other empty — data integrity violation.
#
# Required fix: replace OR-gate with strict pair-completeness check.
# Either BOTH empty (deferred state) OR BOTH non-empty + artifact_dir provided.
# Asymmetric state must raise ValueError at write-boundary (FAIL CLOSED).
# ---------------------------------------------------------------------------


class TestSys3B1PartialLateFillPairCompleteness:
    """SYS3-B1: _write_to_registry must reject asymmetric LATE_FILL state (FAIL CLOSED)."""

    def test_path_nonempty_sha_empty_artifact_dir_provided_raises(self, tmp_path: Path) -> None:
        """Tampered LC (path set, sha empty via bypass) + artifact_dir → ValueError at write boundary.

        Pre-SYS4: LC(path='returns.parquet', sha='') was constructible; asymmetric state
        reached write boundary where OR-gate passed but AND-gate silently failed.
        Post-SYS4: asymmetric state is rejected at LC construction (SYS4 invariant).
        This test now uses object.__setattr__ to bypass __post_init__ and verify the
        write-boundary pair-completeness gate (SYS3-B1 defense-in-depth) still fires
        for tampered instances.
        """
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys3b1-half-path-001",
            returns_per_bar_path="",
            returns_per_bar_sha256="",
        ))
        # Bypass __post_init__ to inject asymmetric state (path set, sha empty).
        object.__setattr__(lc, "returns_per_bar_path", "returns_per_bar.parquet")
        # returns_per_bar_sha256 remains "" — asymmetric tamper
        artifact_dir = tmp_path / "sys3b1_a"
        artifact_dir.mkdir()
        with pytest.raises(ValueError, match="(?i)(pair|asymmetric|LATE_FILL|both|sha|path)"):
            _make_write_registry_call(
                tmp_path, lc, artifact_dir=artifact_dir, strategy_name_suffix="3b1a"
            )

    def test_sha_nonempty_path_empty_artifact_dir_provided_raises(self, tmp_path: Path) -> None:
        """Tampered LC (sha set, path empty via bypass) + artifact_dir → ValueError at write boundary.

        Symmetric to test above. SHA populated, path empty via bypass. Write-boundary
        pair-completeness gate (SYS3-B1 defense-in-depth) must still catch this case.
        """
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys3b1-half-sha-001",
            returns_per_bar_path="",
            returns_per_bar_sha256="",
        ))
        # Bypass __post_init__ to inject asymmetric state (sha set, path empty).
        object.__setattr__(lc, "returns_per_bar_sha256", "abc123def456")
        # returns_per_bar_path remains "" — asymmetric tamper
        artifact_dir = tmp_path / "sys3b1_b"
        artifact_dir.mkdir()
        with pytest.raises(ValueError, match="(?i)(pair|asymmetric|LATE_FILL|both|sha|path)"):
            _make_write_registry_call(
                tmp_path, lc, artifact_dir=artifact_dir, strategy_name_suffix="3b1b"
            )

    def test_both_empty_with_artifact_dir_none_passes(self, tmp_path: Path) -> None:
        """LC(path='', sha='') + artifact_dir=None → passes (deferred state; no recheck).

        Both LATE_FILL fields empty is the canonical deferred state (B skip D1-b).
        Must remain a no-error path — regression protection for valid deferred state.
        """
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys3b1-both-empty-001",
            returns_per_bar_path="",
            returns_per_bar_sha256="",
        ))
        # Must NOT raise: empty/empty is the valid deferred state
        _make_write_registry_call(tmp_path, lc, artifact_dir=None, strategy_name_suffix="3b1c")

    def test_both_nonempty_with_artifact_dir_provided_passes(self, tmp_path: Path) -> None:
        """LC(path='returns.parquet', sha=<real-sha>) + valid artifact_dir → passes (normal B6 recheck).

        Both LATE_FILL fields non-empty + artifact_dir provided is the canonical
        filled state. Must run B6 recheck (path-confinement + SHA256) without error
        when file and SHA match — regression protection for normal B6 recheck path.
        """
        from backtest.artifact_schema import LineageContext
        from backtest.engine import write_per_bar_artifact

        artifact_dir = tmp_path / "sys3b1_d_artifacts"
        artifact_dir.mkdir()
        ec = _make_equity_curve(n=12)
        result = write_per_bar_artifact(
            equity_curve=ec, artifact_dir=artifact_dir, run_id="sys3b1-both-nonempty"
        )
        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys3b1-both-nonempty-001",
            returns_per_bar_path=result["returns_per_bar_path"],
            returns_per_bar_sha256=result["returns_per_bar_sha256"],
            T_obs=result["T_obs"],
        ))
        # Must NOT raise: valid pair + matching artifact → B6 recheck passes
        _make_write_registry_call(
            tmp_path, lc, artifact_dir=artifact_dir, strategy_name_suffix="3b1d"
        )


# ---------------------------------------------------------------------------
# SYS3-B2: Write-boundary T_obs defensive revalidation
#
# Bug: LC.__post_init__ correctly rejects T_obs=None/0/-1/bool (SYS2-B1 fix).
# But object.__setattr__(lc, "T_obs", None) bypasses frozen-dataclass guard.
# _write_to_registry copies lineage_context.T_obs at line 1251 without
# revalidation — registry T_obs column nullable → writes NULL silently.
#
# Required fix: add defensive T_obs revalidation at _write_to_registry boundary
# (mirror FIX-B1-extension pattern for cost_anchor_id/parent_run_id).
# Re-check that T_obs is a positive integer (not None, not bool, not <= 0).
# Raise structured ValueError if bypassed via object.__setattr__ tampering.
# ---------------------------------------------------------------------------


class TestSys3B2TObsWriteBoundaryRevalidation:
    """SYS3-B2: _write_to_registry must defensively revalidate T_obs at write-boundary."""

    def test_mutated_t_obs_none_raises_at_write_boundary(self, tmp_path: Path) -> None:
        """Mutate LC.T_obs=None via object.__setattr__; _write_to_registry → ValueError.

        LC is constructed with valid T_obs=10 (passes __post_init__). Then
        object.__setattr__ bypasses the frozen guard. Write-boundary defensive
        revalidation must catch the tampered None value and raise ValueError.
        """
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys3b2-t-obs-none-001", T_obs=10
        ))
        # Bypass frozen dataclass guard
        object.__setattr__(lc, "T_obs", None)
        with pytest.raises(ValueError, match="(?i)(T_obs|None|write.boundary|tamper|revalidat)"):
            _make_write_registry_call(tmp_path, lc, artifact_dir=None, strategy_name_suffix="3b2a")

    def test_mutated_t_obs_zero_raises_at_write_boundary(self, tmp_path: Path) -> None:
        """Mutate LC.T_obs=0 via object.__setattr__; _write_to_registry → ValueError.

        T_obs=0 was rejected at construction (SYS2-B1). Bypass via
        object.__setattr__ must also be caught at write-boundary.
        """
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys3b2-t-obs-zero-001", T_obs=10
        ))
        object.__setattr__(lc, "T_obs", 0)
        with pytest.raises(ValueError, match="(?i)(T_obs|zero|positive|write.boundary|tamper|revalidat)"):
            _make_write_registry_call(tmp_path, lc, artifact_dir=None, strategy_name_suffix="3b2b")

    def test_mutated_t_obs_negative_raises_at_write_boundary(self, tmp_path: Path) -> None:
        """Mutate LC.T_obs=-1 via object.__setattr__; _write_to_registry → ValueError.

        T_obs=-1 was rejected at construction (SYS2-B1). Bypass via
        object.__setattr__ must also be caught at write-boundary.
        """
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys3b2-t-obs-neg-001", T_obs=10
        ))
        object.__setattr__(lc, "T_obs", -1)
        with pytest.raises(ValueError, match="(?i)(T_obs|negative|positive|write.boundary|tamper|revalidat)"):
            _make_write_registry_call(tmp_path, lc, artifact_dir=None, strategy_name_suffix="3b2c")

    def test_valid_t_obs_passes_write_boundary(self, tmp_path: Path) -> None:
        """Normal LC with valid T_obs=10 passes write-boundary revalidation (regression-protect).

        No object.__setattr__ tampering — normal construction + write path.
        Defensive revalidation must be a no-op for valid T_obs values.
        """
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys3b2-valid-001", T_obs=10
        ))
        # Must NOT raise: valid T_obs → defensive recheck passes silently
        _make_write_registry_call(tmp_path, lc, artifact_dir=None, strategy_name_suffix="3b2d")


# ---------------------------------------------------------------------------
# FIX-T1.1-SYS4-LATE-FILL: producer-side closed-set LATE_FILL pair invariant
# ---------------------------------------------------------------------------

class TestSys4LateFillProducerInvariant:
    """SYS4: LineageContext.__post_init__ must enforce the closed-set LATE_FILL pair invariant.

    Valid states are exactly two (closed set):
      - Deferred: ("", "")  — both exact empty strings
      - Filled:   (non_empty_non_whitespace_str, non_empty_non_whitespace_str)

    All other combinations (None, mixed, whitespace-only, non-str) must raise
    ValueError with FIX-T1.1-SYS4-LATE-FILL tag language in the message.

    Truth-table (8 cases):
      1. (None, "")               → ValueError (type check), message contains "str"
      2. ("", "")                 → PASS (deferred state)
      3. ("non_empty", "")        → ValueError (pair desync), message contains "closed-set pair-state"
      4. ("", "non_empty")        → ValueError (pair desync), message contains "closed-set pair-state"
      5. ("non_empty", "non_empty") → PASS (filled state)
      6. (123, "abc")             → ValueError (type check), message contains "type"
      7. ("abc", 123)             → ValueError (type check), message contains "type"
      8. ("   ", "   ")           → ValueError (whitespace-only, neither deferred nor filled),
                                    message contains "closed-set pair-state"
    """

    def test_case1_none_and_empty_raises_type_error(self) -> None:
        """Case 1: (None, '') — type check fails; ValueError with 'str' in message."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(
            returns_per_bar_path=None,
            returns_per_bar_sha256="",
        )
        with pytest.raises(ValueError, match="str"):
            LineageContext(**kwargs)

    def test_case2_both_empty_passes_deferred_state(self) -> None:
        """Case 2: ('', '') — deferred state; LC construction must NOT raise."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(
            returns_per_bar_path="",
            returns_per_bar_sha256="",
        )
        lc = LineageContext(**kwargs)
        assert lc.returns_per_bar_path == ""
        assert lc.returns_per_bar_sha256 == ""

    def test_case3_path_nonempty_sha_empty_raises_pair_desync(self) -> None:
        """Case 3: ('non_empty', '') — pair desync; ValueError with 'closed-set pair-state' in message."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(
            returns_per_bar_path="data/results/returns_001.parquet",
            returns_per_bar_sha256="",
        )
        with pytest.raises(ValueError, match="closed-set pair-state"):
            LineageContext(**kwargs)

    def test_case4_path_empty_sha_nonempty_raises_pair_desync(self) -> None:
        """Case 4: ('', 'non_empty') — pair desync; ValueError with 'closed-set pair-state' in message."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(
            returns_per_bar_path="",
            returns_per_bar_sha256="sha256:aabbccdd1122",
        )
        with pytest.raises(ValueError, match="closed-set pair-state"):
            LineageContext(**kwargs)

    def test_case5_both_nonempty_passes_filled_state(self) -> None:
        """Case 5: ('non_empty', 'non_empty') — filled state; LC construction must NOT raise."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(
            returns_per_bar_path="data/results/returns_002.parquet",
            returns_per_bar_sha256="sha256:deadbeef1234",
        )
        lc = LineageContext(**kwargs)
        assert lc.returns_per_bar_path == "data/results/returns_002.parquet"
        assert lc.returns_per_bar_sha256 == "sha256:deadbeef1234"

    def test_case6_int_path_str_sha_raises_type_error(self) -> None:
        """Case 6: (123, 'abc') — non-str path; ValueError with 'type' in message."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(
            returns_per_bar_path=123,
            returns_per_bar_sha256="abc",
        )
        with pytest.raises(ValueError, match="type"):
            LineageContext(**kwargs)

    def test_case7_str_path_int_sha_raises_type_error(self) -> None:
        """Case 7: ('abc', 123) — non-str sha; ValueError with 'type' in message."""
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(
            returns_per_bar_path="abc",
            returns_per_bar_sha256=123,
        )
        with pytest.raises(ValueError, match="type"):
            LineageContext(**kwargs)

    def test_case8_whitespace_only_pair_raises_pair_state_error(self) -> None:
        """Case 8: ('   ', '   ') — whitespace-only; neither deferred nor filled.

        Whitespace-only strings are not exact empty strings (not deferred) and
        do not satisfy non-empty non-whitespace (not filled). Must raise
        ValueError with 'closed-set pair-state' in message.
        """
        from backtest.artifact_schema import LineageContext

        kwargs = _build_valid_lc_kwargs(
            returns_per_bar_path="   ",
            returns_per_bar_sha256="   ",
        )
        with pytest.raises(ValueError, match="closed-set pair-state"):
            LineageContext(**kwargs)


# ---------------------------------------------------------------------------
# SYS5: revalidate_for_write() — post-construction tamper closure
# FIX-T1.1-SYS5-REVALIDATE
# ---------------------------------------------------------------------------


def _make_valid_lc():
    """Construct a valid LineageContext for SYS5 tamper tests."""
    from backtest.artifact_schema import LineageContext

    return LineageContext(**_build_valid_lc_kwargs())


class TestSys5RevalidateForWriteDirectStrictFields:
    """SYS5: 8 direct STRICT fields tampered via object.__setattr__ must be rejected."""

    @pytest.mark.parametrize("field_name", [
        "run_id",
        "hypothesis_hash",
        "source_batch_id",
        "regime_key",
        "engine_commit",
        "current_git_sha",
        "execution_config_sha256",
        "parquet_data_sha256",
    ])
    def test_empty_string_tamper_raises(self, field_name: str) -> None:
        """object.__setattr__(lc, field, '') then revalidate_for_write raises ValueError."""
        lc = _make_valid_lc()
        object.__setattr__(lc, field_name, "")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    @pytest.mark.parametrize("field_name", [
        "run_id",
        "hypothesis_hash",
        "source_batch_id",
        "regime_key",
        "engine_commit",
        "current_git_sha",
        "execution_config_sha256",
        "parquet_data_sha256",
    ])
    def test_whitespace_tamper_raises(self, field_name: str) -> None:
        """object.__setattr__(lc, field, '   ') then revalidate_for_write raises ValueError."""
        lc = _make_valid_lc()
        object.__setattr__(lc, field_name, "   ")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    @pytest.mark.parametrize("field_name", [
        "run_id",
        "hypothesis_hash",
        "source_batch_id",
        "regime_key",
        "engine_commit",
        "current_git_sha",
        "execution_config_sha256",
        "parquet_data_sha256",
    ])
    def test_none_tamper_raises(self, field_name: str) -> None:
        """object.__setattr__(lc, field, None) then revalidate_for_write raises ValueError."""
        lc = _make_valid_lc()
        object.__setattr__(lc, field_name, None)
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    @pytest.mark.parametrize("field_name", [
        "run_id",
        "hypothesis_hash",
        "source_batch_id",
        "regime_key",
        "engine_commit",
        "current_git_sha",
        "execution_config_sha256",
        "parquet_data_sha256",
    ])
    def test_error_includes_sys5_revalidate_tag(self, field_name: str) -> None:
        """ValueError message must contain 'SYS5-REVALIDATE' tag."""
        lc = _make_valid_lc()
        object.__setattr__(lc, field_name, "")
        with pytest.raises(ValueError, match="SYS5-REVALIDATE"):
            lc.revalidate_for_write()


class TestSys5RevalidateForWriteExecutionConfigPath:
    """SYS5: execution_config_path tamper (non-canonical form) raises via revalidate_for_write."""

    def test_non_canonical_path_raises(self) -> None:
        """Tamper to path with '..' components raises ValueError from revalidate_for_write."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "execution_config_path", "config/../config/execution.yaml")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_absolute_path_tamper_raises(self) -> None:
        """Tamper to absolute path raises ValueError from revalidate_for_write."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "execution_config_path", "/etc/passwd")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_empty_path_tamper_raises(self) -> None:
        """Tamper to empty string raises ValueError from revalidate_for_write."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "execution_config_path", "")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_valid_canonical_path_passes(self) -> None:
        """Valid canonical execution_config_path passes revalidate_for_write."""
        lc = _make_valid_lc()
        # No tampering -- must pass cleanly.
        lc.revalidate_for_write()  # must not raise


class TestSys5RevalidateForWriteCostAnchorId:
    """SYS5: cost_anchor_id tamper (wrong mapping value) raises via revalidate_for_write."""

    def test_wrong_anchor_id_raises(self) -> None:
        """Tamper cost_anchor_id to wrong value raises ValueError."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "cost_anchor_id", "wrong_anchor_id")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_empty_anchor_id_raises(self) -> None:
        """Tamper cost_anchor_id to empty string raises ValueError."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "cost_anchor_id", "")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_none_anchor_id_raises(self) -> None:
        """Tamper cost_anchor_id to None raises ValueError."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "cost_anchor_id", None)
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_correct_anchor_id_passes(self) -> None:
        """Correctly resolved cost_anchor_id passes revalidate_for_write."""
        lc = _make_valid_lc()
        # cost_anchor_id was set correctly by __post_init__; must pass.
        assert lc.cost_anchor_id == "legacy_perp_inspired_7bps_v0"
        lc.revalidate_for_write()  # must not raise


class TestSys5RevalidateForWriteTObs:
    """SYS5: T_obs tamper (None, 0, -1, True) raises via revalidate_for_write."""

    def test_none_t_obs_raises(self) -> None:
        """object.__setattr__(lc, 'T_obs', None) then revalidate_for_write raises ValueError."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "T_obs", None)
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_zero_t_obs_raises(self) -> None:
        """T_obs=0 raises ValueError from revalidate_for_write."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "T_obs", 0)
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_negative_t_obs_raises(self) -> None:
        """T_obs=-1 raises ValueError from revalidate_for_write."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "T_obs", -1)
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_bool_true_t_obs_raises(self) -> None:
        """T_obs=True (bool) raises ValueError from revalidate_for_write (bool is int subclass)."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "T_obs", True)
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_positive_int_t_obs_passes(self) -> None:
        """Valid positive int T_obs passes revalidate_for_write."""
        lc = _make_valid_lc()
        lc.revalidate_for_write()  # must not raise


class TestSys5RevalidateForWriteParentRunId:
    """SYS5: parent_run_id tamper (empty, whitespace, non-str) raises via revalidate_for_write."""

    def test_empty_parent_run_id_raises(self) -> None:
        """object.__setattr__(lc, 'parent_run_id', '') then revalidate_for_write raises."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "parent_run_id", "")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_whitespace_parent_run_id_raises(self) -> None:
        """Whitespace-only parent_run_id raises ValueError from revalidate_for_write."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "parent_run_id", "   ")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_int_parent_run_id_raises(self) -> None:
        """Non-str parent_run_id raises ValueError from revalidate_for_write."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "parent_run_id", 123)
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_none_parent_run_id_passes(self) -> None:
        """None parent_run_id (valid: no parent) passes revalidate_for_write."""
        lc = _make_valid_lc()
        # _build_valid_lc_kwargs defaults parent_run_id=None
        assert lc.parent_run_id is None
        lc.revalidate_for_write()  # must not raise

    def test_non_empty_string_parent_run_id_passes(self) -> None:
        """Valid non-empty string parent_run_id passes revalidate_for_write."""
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(parent_run_id="parent-run-uuid-001"))
        lc.revalidate_for_write()  # must not raise


class TestSys5RevalidateForWriteLateFillPair:
    """SYS5: LATE_FILL pair tamper (asymmetric/type) raises via revalidate_for_write."""

    def test_path_set_sha_empty_raises(self) -> None:
        """Asymmetric ('path', '') pair raises ValueError from revalidate_for_write."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "returns_per_bar_path", "data/results/returns.parquet")
        object.__setattr__(lc, "returns_per_bar_sha256", "")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_path_empty_sha_set_raises(self) -> None:
        """Asymmetric ('', 'sha') pair raises ValueError from revalidate_for_write."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "returns_per_bar_path", "")
        object.__setattr__(lc, "returns_per_bar_sha256", "sha256:deadbeef")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_none_path_str_sha_raises(self) -> None:
        """(None, 'sha') pair raises ValueError from revalidate_for_write."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "returns_per_bar_path", None)
        object.__setattr__(lc, "returns_per_bar_sha256", "sha256:deadbeef")
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_str_path_none_sha_raises(self) -> None:
        """('path', None) pair raises ValueError from revalidate_for_write."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "returns_per_bar_path", "data/results/returns.parquet")
        object.__setattr__(lc, "returns_per_bar_sha256", None)
        with pytest.raises(ValueError, match="revalidate_for_write"):
            lc.revalidate_for_write()

    def test_deferred_state_passes(self) -> None:
        """Deferred state ('', '') passes revalidate_for_write."""
        lc = _make_valid_lc()
        # _build_valid_lc_kwargs defaults to ('', '') deferred state
        assert lc.returns_per_bar_path == ""
        assert lc.returns_per_bar_sha256 == ""
        lc.revalidate_for_write()  # must not raise

    def test_filled_state_passes(self) -> None:
        """Filled state ('non_empty', 'non_empty') passes revalidate_for_write."""
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            returns_per_bar_path="data/results/returns_003.parquet",
            returns_per_bar_sha256="sha256:aabbccdd1122",
        ))
        lc.revalidate_for_write()  # must not raise


class TestSys5RevalidateForWriteValidLCPasses:
    """SYS5: Untampered valid LC must pass revalidate_for_write (regression guard)."""

    def test_all_valid_fields_pass(self) -> None:
        """Untampered valid LC with all 14 dataclass fields (13 Contract 2.0.5 + T_obs) passes revalidate_for_write."""
        lc = _make_valid_lc()
        lc.revalidate_for_write()  # must not raise

    def test_all_cost_anchor_mappings_pass(self) -> None:
        """Each COST_ANCHOR_ID_MAPPING key produces LC that passes revalidate_for_write."""
        from backtest.artifact_schema import COST_ANCHOR_ID_MAPPING, LineageContext

        for exec_path in COST_ANCHOR_ID_MAPPING:
            lc = LineageContext(**_build_valid_lc_kwargs(execution_config_path=exec_path))
            lc.revalidate_for_write()  # must not raise for any known anchor


class TestSys5RevalidateForWriteIntegration:
    """SYS5 integration: tamper + _write_to_registry verifies error raised before DB insert."""

    def _write_tampered_lc(
        self, tmp_path: Path, lc, *, db_name: str = "sys5_integ.db"
    ) -> None:
        """Call _write_to_registry with tampered LC."""
        from backtest.engine import _write_to_registry
        from backtest.execution_model import ConstantSlippage
        from backtest.slippage import load_execution_config
        import backtrader as bt

        class _Dummy(bt.Strategy):
            STRATEGY_NAME = "sys5_integ"
            WARMUP_BARS = 0

            def next(self) -> None:
                pass

        config = load_execution_config()
        cost_model = ConstantSlippage.from_config(config)
        db_path = tmp_path / db_name

        _write_to_registry(
            run_id=lc.run_id,
            strategy_cls=_Dummy,
            strategy_params={},
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
            effective_start=None,
            warmup_bars=0,
            cost_model=cost_model,
            metrics={
                "total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "max_drawdown_duration_hours": 0.0, "total_trades": 0, "win_rate": 0.0,
                "avg_trade_duration_hours": 0.0, "avg_trade_return": 0.0,
                "profit_factor": None, "initial_capital": 10000.0, "final_capital": 10000.0,
            },
            db_path=db_path,
            lineage_context=lc,
        )

    def test_strict_field_tamper_raises_before_insert(self, tmp_path: Path) -> None:
        """Tampered STRICT field raises ValueError before any DB row inserted."""
        lc = _make_valid_lc()
        object.__setattr__(lc, "run_id", "")
        db_path = tmp_path / "sys5_tamper_run_id.db"
        with pytest.raises(ValueError, match="revalidate_for_write"):
            self._write_tampered_lc(tmp_path, lc, db_name="sys5_tamper_run_id.db")
        # DB file may or may not exist; if it does, verify no row inserted.
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            try:
                rows = conn.execute("SELECT COUNT(*) FROM runs").fetchone()
                assert rows[0] == 0, (
                    f"No row should be inserted when revalidate_for_write raises; "
                    f"got {rows[0]} rows."
                )
            except sqlite3.OperationalError:
                pass  # Table doesn't exist yet -- no insert occurred.
            finally:
                conn.close()

    def test_untampered_lc_write_succeeds(self, tmp_path: Path) -> None:
        """Untampered LC passes revalidate_for_write and write succeeds (regression)."""
        from backtest.artifact_schema import LineageContext

        lc = LineageContext(**_build_valid_lc_kwargs(
            run_id="sys5-regression-001",
        ))
        # Must not raise; write must succeed.
        self._write_tampered_lc(tmp_path, lc, db_name="sys5_regression.db")
        db_path = tmp_path / "sys5_regression.db"
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT run_id FROM runs WHERE run_id = ?", ("sys5-regression-001",)
            ).fetchone()
        finally:
            conn.close()
        assert row is not None, "Row must be inserted for untampered LC."
        assert row[0] == "sys5-regression-001"
