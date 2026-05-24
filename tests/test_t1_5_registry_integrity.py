"""T1.5 (d) Registry integrity tests.

Per ratified T1.5 sub-plan v3.2 (v_final) at
`docs/superpowers/plans/2026-05-23-t1_5-fixture-smoke-registry-test-suite-cycle-execution-plan.md`.

Sub-plan v_final RATIFIED 2026-05-24 per Charlie register chain
(cycle entry + Path B + sub-plan drafting fire + quant-research-advisor +
DS2 Option (i) + G1 + R1 + R2b + R1' + R5b + R6a + R7a) under B-C-extended
Scope-B structural artifact-preservation refactor cycle per R3.1d
sequencing 1→3→4.

Coverage scope (Contract 2.0.3 + 2.0.4 + 2.0.6 (d) per parent plan v5):
- Triple-resolution happy path: (hypothesis_hash + batch_id + run_id) lookup
  returns exactly one row with 14 Contract 2.0.5 header fields populated.
- 5 failure-mode fail-closed branches:
  1. Duplicate run_id → IntegrityError
  2. Missing hypothesis_hash → ValueError (DS8 PENDING; xfail; see method)
  3. Missing batch_id → ValueError (DS8 PENDING; xfail; see method)
  4. cost_anchor_id tamper via object.__setattr__ → ValueError per SYS5
  5. Un-mapped canonicalized execution_config_path via LineageContext
     construction → ValueError
- Path canonicalization edge case: case-only mismatch on case-insensitive FS
  → ValueError via mapping miss (DS6 lock; macOS HFS+ skip on Linux).

Out-of-scope per §2.3.12:
- End-to-end engine→registry flow (§2.2 Smoke scope).
- Per-bar artifact SHA256 verification (T1.2 SEAL scope).
- Regime-holdout-passed semantics (T1.3 + Phase 2A scope).
- All-14-fields LineageContext field-tamper coverage (T1.1 SEAL at
  tests/test_t1_1_sys_fix.py:2583 TestSys5RevalidateForWriteDirectStrictFields;
  §2.3.6 references one specific tamper only).
- B2.a/b/c/d 4-scenario default-normalization (T1.4 B2 SEAL coverage).
- Outside-repo path fail-closed (T1.4 B2.d coverage).
- Walk-forward / evaluation-gate driver opt-out registry (T1.4 B3.3/B3.4 γ-1 SEAL).
- DB migration idempotency (T1.4 SEAL TestT1_4_DBMigrationIdempotency).

Hermetic isolation discipline per §2.3.9 + T1.4 B3.4 precedent:
- Temp experiments.db per test method (not shared via class fixture).
- DEFAULT_DB_PATH monkeypatch BEFORE any _write_to_registry call.
- create_table() per test for full 14-Contract-2.0.5 schema availability.

DS8 PENDING (deferred to Charlie register; surface at Implementation PFR rounds):
- §2.3.4 + §2.3.5 test the strict-interpretation of Contract 2.0.6 (d)
  ("Missing hypothesis_hash/batch_id: fail closed"). Current engine accepts
  None per Phase 1A baseline pattern (CLAUDE.md per backtest/engine.py:903
  comment "NULL for hand-written"). Tests use pytest.mark.xfail(strict=True)
  to surface the spec-vs-implementation gap without blocking the suite;
  Charlie register required for either (a) T1.3 corrective adding strict
  rejection OR (b) Contract 2.0.6 (d) spec clarification on conditional
  Phase 2+ rejection scope.

DS6 LOCK (subagent recommendation):
- §2.3.10 Edge B (case-only mismatch) covered at LineageContext-construction
  path; Edge A (outside-repo) deferred to T1.4 B2.d cross-reference; Edge C
  (relative `..`) deferred to T1.3 canonicalize unit test scope.
"""
from __future__ import annotations

import platform
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Test stub strategy (mirrors T1.4 _MockStrategy pattern)
# ---------------------------------------------------------------------------


class _MockStrategy:
    """Stub strategy class for _write_to_registry argument signatures."""

    WARMUP_BARS = 0

    class _StubParams:
        pass

    params: Any = _StubParams()


# ---------------------------------------------------------------------------
# Module-level helpers per §2.3.9 (mirror T1.4 _make_minimal_write_args /
# _make_db pattern at tests/test_t1_4_backward_compat.py:131 / :650)
# ---------------------------------------------------------------------------


def _make_minimal_write_args(
    *,
    run_id: str = "t1-5-test-run-id",
    parent_run_id: str | None = None,
) -> dict[str, Any]:
    """Minimal args for _write_to_registry per T1.4 helper pattern.

    Mirrors tests/test_t1_4_backward_compat.py:131 _make_minimal_write_args
    to reuse proven helper signature; helper duplicated here per per-test-
    file independence convention (no inter-test-file imports).
    """
    from backtest.execution_model import ConstantSlippage

    cost_model = MagicMock(spec=ConstantSlippage)
    cost_model.fee_model_label = "effective_7bps_per_side"

    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return {
        "run_id": run_id,
        "strategy_cls": _MockStrategy,
        "strategy_params": {},
        "start_date": now,
        "end_date": now,
        "effective_start": now,
        "warmup_bars": 0,
        "cost_model": cost_model,
        "parent_run_id": parent_run_id,
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


def _make_db(tmp_path: Path, name: str = "t1_5_registry.db") -> Path:
    """Create a fresh temp experiments.db with create_table schema applied.

    Mirrors tests/test_t1_4_backward_compat.py:650 _make_db pattern.
    """
    from backtest.experiment_registry import create_table

    db_path = tmp_path / name
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    create_table(conn)
    conn.close()
    return db_path


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


class TestT1_5_RegistryIntegrity:
    """T1.5 (d) Registry integrity tests per sub-plan v3.2 (v_final) §2.3.

    7 test methods per Path B narrow scope:
    - test_triple_resolution_happy_path — Contract 2.0.3 triple linkage
    - test_failure_1_duplicate_run_id — SQLite UNIQUE PRIMARY KEY
    - test_failure_2_missing_hypothesis_hash — DS8 PENDING (xfail)
    - test_failure_3_missing_batch_id — DS8 PENDING (xfail)
    - test_failure_4_cost_anchor_id_tamper_via_setattr — Contract 2.0.4 +
      T1.1 SYS5 revalidate_for_write cross-reference
    - test_failure_5_unmapped_path_via_lineage_context_construction —
      Contract 2.0.4 fail-closed via LC __post_init__
    - test_canonicalization_case_only_mismatch_fails_closed_on_case_insensitive_fs —
      DS6 Edge B (macOS HFS+; skip on Linux)

    Hermetic isolation per §2.3.9 (CRITICAL):
    - Temp DB per test method via _make_db(tmp_path, name=...)
    - DEFAULT_DB_PATH monkeypatch BEFORE _write_to_registry
    - No class-scoped DB (ordering-dependent failures risk)

    All test methods follow the same setup pattern:
        tmp_db = _make_db(tmp_path, name="<unique_name>.db")
        monkeypatch.setattr(registry_mod, "DEFAULT_DB_PATH", tmp_db)
        args = _make_minimal_write_args(run_id="<unique_run_id>")
        args["db_path"] = tmp_db
        # ... per-test-specific args ...
        _write_to_registry(**args)  # or with pytest.raises
    """

    def test_triple_resolution_happy_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Triple linkage (hypothesis_hash + batch_id + run_id) resolves to one row.

        Per Contract 2.0.3 line 86 triple linkage discipline + §2.3.2 spec:
        "Insert one row with full lineage context populated; query by
        (hypothesis_hash, batch_id, run_id); assert exactly one row
        returned; verify each of 14 Contract 2.0.5 header fields persisted
        correctly."

        Per SEAL-eve HIGH-2 fix 2026-05-24 (Codex): test extended from
        scalar-pathway-only (run_id + hypothesis_hash + batch_id) to full
        LineageContext threading + 9 T1.x column persistence verification.
        Prior scalar-only path persisted 9 T1.x columns as NULL — structural
        coverage gap per §2.3.2 spec.

        Coverage scope:
        - Triple linkage primary-key resolution via 3-axis query
        - 6 T1.x string columns persisted from LineageContext (cost_anchor_id
          resolved via Contract 2.0.4 mapping; regime_key + current_git_sha +
          execution_config_path + execution_config_sha256 + parquet_data_sha256
          persisted verbatim from LC)
        - 3 T1.x columns in deferred-state (returns_per_bar_path +
          returns_per_bar_sha256 empty per LATE_FILL discipline + T_obs=10
          placeholder per LineageContext smoke convention)

        Full 14-field tamper invariant scope is T1.1 SYS5
        `revalidate_for_write` coverage at tests/test_t1_1_sys_fix.py:2583
        TestSys5RevalidateForWriteDirectStrictFields.
        """
        import backtest.experiment_registry as registry_mod
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry

        tmp_db = _make_db(tmp_path, name="triple.db")
        monkeypatch.setattr(registry_mod, "DEFAULT_DB_PATH", tmp_db)

        # Full LineageContext per §2.3.2 spec (HIGH-2 fix + HIGH-F closure
        # per SEAL-eve v2 Codex 2026-05-24: real parquet hash NOT placeholder).
        # Note: this registry test doesn't depend on actual DS2 window data
        # (it tests registry persistence directly); using a deterministic
        # but non-trivially-shaped real hash for parquet_data_sha256 satisfies
        # Contract 2.0.5 field-content semantic without requiring parquet
        # I/O at this unit-level test scope.
        import hashlib as _hashlib
        _triple_parquet_real_sha = (
            "sha256:" + _hashlib.sha256(b"triple-test-parquet-bytes").hexdigest()
        )
        lc = LineageContext(
            run_id="triple-run-id",
            hypothesis_hash="triple-hash",
            source_batch_id="triple-batch",
            regime_key="v2.regime_holdout",
            engine_commit="triple-engine-commit",
            current_git_sha="triple-git-sha-full",
            execution_config_path="config/execution.yaml",
            execution_config_sha256="sha256:triple-exec",
            parquet_data_sha256=_triple_parquet_real_sha,
            returns_per_bar_path="",  # DEFERRED LATE_FILL
            returns_per_bar_sha256="",  # DEFERRED LATE_FILL
            T_obs=10,
            parent_run_id=None,
        )

        args = _make_minimal_write_args(run_id="triple-run-id")
        args["db_path"] = tmp_db
        args["lineage_context"] = lc
        args["hypothesis_hash"] = "triple-hash"
        args["batch_id"] = "triple-batch"

        _write_to_registry(**args)

        # Triple-linkage query: WHERE hypothesis_hash AND batch_id AND run_id
        conn = sqlite3.connect(str(tmp_db))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM runs WHERE hypothesis_hash = ? AND batch_id = ? "
            "AND run_id = ?",
            ("triple-hash", "triple-batch", "triple-run-id"),
        ).fetchall()
        conn.close()

        assert len(rows) == 1, (
            f"Triple-linkage query must return exactly 1 row; got {len(rows)}"
        )
        row = rows[0]
        # Triple linkage primary-key resolution (3 scalar fields)
        assert row["run_id"] == "triple-run-id"
        assert row["hypothesis_hash"] == "triple-hash"
        assert row["batch_id"] == "triple-batch"

        # HIGH-2 fix per SEAL-eve 2026-05-24: 6 T1.x columns persisted from
        # LineageContext (cost_anchor_id resolved via Contract 2.0.4 mapping;
        # 5 others persisted verbatim from LC fields). Prior scalar-only
        # test pathway left these as NULL — structural coverage gap per
        # §2.3.2 spec ("verify each of 14 Contract 2.0.5 header fields
        # persisted correctly").
        assert row["cost_anchor_id"] == "legacy_perp_inspired_7bps_v0", (
            f"T1.x col cost_anchor_id must resolve via Contract 2.0.4 "
            f"mapping for execution_config_path='config/execution.yaml'; "
            f"got {row['cost_anchor_id']!r}."
        )
        assert row["regime_key"] == "v2.regime_holdout", (
            f"T1.x col regime_key must persist verbatim from LC; got "
            f"{row['regime_key']!r}."
        )
        assert row["current_git_sha"] == "triple-git-sha-full", (
            f"T1.x col current_git_sha must persist verbatim from LC; got "
            f"{row['current_git_sha']!r}."
        )
        assert row["execution_config_path"] == "config/execution.yaml", (
            f"T1.x col execution_config_path must persist canonicalized POSIX "
            f"per Contract 2.0.4 + LC field; got "
            f"{row['execution_config_path']!r}."
        )
        assert row["execution_config_sha256"] == "sha256:triple-exec", (
            f"T1.x col execution_config_sha256 must persist verbatim from "
            f"LC; got {row['execution_config_sha256']!r}."
        )
        assert row["parquet_data_sha256"] == _triple_parquet_real_sha, (
            f"T1.x col parquet_data_sha256 must persist verbatim from LC "
            f"(real hash per HIGH-F closure); got "
            f"{row['parquet_data_sha256']!r}."
        )

        # HIGH-2 closure tight per SEAL-eve v2 Codex + Advisor #8 CONVERGED
        # HIGH 2026-05-24: assert 3 deferred-state T1.x fields are
        # persisted as placeholder values (T_obs=10 + returns_per_bar_path=""
        # + returns_per_bar_sha256=""). Prior HIGH-2 closure asserted only
        # 6-of-9 columns; this extension brings to full 9-of-9 T1.x coverage
        # per §2.3.2 spec ("verify each of 14 Contract 2.0.5 header fields
        # persisted correctly"). 14 = 5 always-non-LC (run_id +
        # parent_run_id + hypothesis_hash + source_batch_id + engine_commit
        # asserted via _make_minimal_write_args) + 9 T1.x = 14 total.
        assert row["T_obs"] == 10, (
            f"T1.x col T_obs must persist placeholder value 10 from LC "
            f"deferred-state; got {row['T_obs']!r}."
        )
        assert row["returns_per_bar_path"] == "", (
            f"T1.x col returns_per_bar_path must persist empty string from "
            f"LC deferred-state LATE_FILL; got {row['returns_per_bar_path']!r}."
        )
        assert row["returns_per_bar_sha256"] == "", (
            f"T1.x col returns_per_bar_sha256 must persist empty string from "
            f"LC deferred-state LATE_FILL; got {row['returns_per_bar_sha256']!r}."
        )

    def test_failure_1_duplicate_run_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Duplicate run_id fails closed (SQLite UNIQUE constraint on PRIMARY KEY).

        Per backtest/experiment_registry.py:56 `run_id TEXT PRIMARY KEY`.
        SQLite enforces uniqueness; second insert with same run_id raises
        IntegrityError (or wrapped ValueError per engine implementation
        choice per T1.4 A2 Codex F1 v2 PFR precedent).

        Test accepts (sqlite3.IntegrityError, ValueError) tuple to preserve
        flexibility for T1.x implementation wrapping choices.

        Error message content assertion: run_id value OR "UNIQUE" present
        (don't lock specific wording — wording is engine internal; contract
        is "operator can diagnose which row collided").
        """
        import backtest.experiment_registry as registry_mod
        from backtest.engine import _write_to_registry

        tmp_db = _make_db(tmp_path, name="dup.db")
        monkeypatch.setattr(registry_mod, "DEFAULT_DB_PATH", tmp_db)

        args = _make_minimal_write_args(run_id="dup-run-id")
        args["db_path"] = tmp_db

        # First insert: succeeds
        _write_to_registry(**args)

        # Second insert with same run_id: must fail closed
        args2 = _make_minimal_write_args(run_id="dup-run-id")
        args2["db_path"] = tmp_db
        with pytest.raises((sqlite3.IntegrityError, ValueError)) as exc_info:
            _write_to_registry(**args2)

        msg = str(exc_info.value)
        assert ("dup-run-id" in msg) or ("UNIQUE" in msg.upper()), (
            f"Duplicate run_id failure must surface run_id value or UNIQUE "
            f"constraint in message; got: {exc_info.value!r}"
        )

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "DS8 PENDING Charlie register on strict-vs-conditional "
            "hypothesis_hash rejection scope per sub-plan §2.3.4 + §8.2 "
            "DS8 named sub-decision. Current engine accepts hypothesis_hash=None "
            "per Phase 1A baseline pattern (backtest/engine.py:903 comment "
            "'NULL for hand-written'). Spec Contract 2.0.6 (d) says 'Missing "
            "hypothesis_hash: fail closed'; spec-vs-implementation gap; T1.3 "
            "corrective work OR spec clarification required at fresh Charlie "
            "register-event (NOT T1.5 in-scope per §3.2 failure handling). "
            "When DS8 resolves: remove xfail (if strict adopted) OR remove "
            "test method (if conditional adopted with Phase 1A None-permitted)."
        ),
    )
    def test_failure_2_missing_hypothesis_hash(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Missing hypothesis_hash fails closed (DS8 PENDING; xfail).

        Per Contract 2.0.6 (d) line 195: "Missing hypothesis_hash: fail
        closed." Engine MUST surface field-name in error message.

        DS8 SPEC-VS-IMPLEMENTATION GAP: current engine accepts None
        (intended for Phase 1A hand-written baselines per CLAUDE.md);
        this test xfails strict-mode pending Charlie register on T1.3
        corrective vs spec clarification.
        """
        import backtest.experiment_registry as registry_mod
        from backtest.engine import _write_to_registry

        tmp_db = _make_db(tmp_path, name="missing_hh.db")
        monkeypatch.setattr(registry_mod, "DEFAULT_DB_PATH", tmp_db)

        args = _make_minimal_write_args(run_id="missing-hh-run-id")
        args["db_path"] = tmp_db
        args["hypothesis_hash"] = None
        args["batch_id"] = "some-batch"

        with pytest.raises(ValueError) as exc_info:
            _write_to_registry(**args)

        msg = str(exc_info.value)
        assert "hypothesis_hash" in msg, (
            f"Missing hypothesis_hash failure must identify field name; "
            f"got: {msg!r}"
        )

        # Defensive: NOT silently inserted as NULL
        conn = sqlite3.connect(str(tmp_db))
        rows = conn.execute(
            "SELECT * FROM runs WHERE run_id = ?", ("missing-hh-run-id",)
        ).fetchall()
        conn.close()
        assert len(rows) == 0, (
            f"Missing hypothesis_hash must NOT silently insert NULL row; "
            f"got {len(rows)} rows with run_id='missing-hh-run-id'"
        )

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "DS8 PENDING Charlie register on strict-vs-conditional batch_id "
            "rejection scope per sub-plan §2.3.5 + §8.2 DS8 named sub-decision. "
            "Current engine accepts batch_id=None per Phase 1A pre-batch run "
            "pattern (backtest/engine.py:902 comment 'NULL for pre-batch runs'). "
            "Spec Contract 2.0.6 (d) says 'Missing batch_id: fail closed'; "
            "spec-vs-implementation gap; T1.3 corrective work OR spec "
            "clarification required at fresh Charlie register-event (NOT T1.5 "
            "in-scope per §3.2 failure handling). When DS8 resolves: remove "
            "xfail (if strict adopted) OR remove test method (if conditional "
            "adopted with Phase 1A None-permitted) OR edit assertion (if "
            "Contract 2.0.6 (d) amended to permit None for specific lifecycle "
            "states). Symmetric framework with test_failure_2_missing_hypothesis_hash "
            "per Codex IPFR LOW 2026-05-24."
        ),
    )
    def test_failure_3_missing_batch_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Missing batch_id fails closed (DS8 PENDING; xfail).

        Per Contract 2.0.6 (d) line 196: "Missing batch_id: fail closed."
        Per Contract 2.0.3 line 86: source_batch_id (artifact field) aliases
        registry batch_id; alias resolution discipline verified by surfacing
        EITHER name in error message.

        DS8 SPEC-VS-IMPLEMENTATION GAP per test_failure_2 framework.
        """
        import backtest.experiment_registry as registry_mod
        from backtest.engine import _write_to_registry

        tmp_db = _make_db(tmp_path, name="missing_bid.db")
        monkeypatch.setattr(registry_mod, "DEFAULT_DB_PATH", tmp_db)

        args = _make_minimal_write_args(run_id="missing-bid-run-id")
        args["db_path"] = tmp_db
        args["hypothesis_hash"] = "some-hash"
        args["batch_id"] = None

        with pytest.raises(ValueError) as exc_info:
            _write_to_registry(**args)

        msg = str(exc_info.value)
        assert ("batch_id" in msg) or ("source_batch_id" in msg), (
            f"Missing batch_id failure must identify field name (batch_id or "
            f"source_batch_id alias per Contract 2.0.3); got: {msg!r}"
        )

    def test_failure_4_cost_anchor_id_tamper_via_setattr(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """cost_anchor_id post-construction tamper fails via SYS5 revalidate_for_write.

        Per Contract 2.0.4 integrity + T1.1 SYS5 revalidate_for_write
        invariant at backtest/artifact_schema.py revalidate_for_write().

        The mismatch case is structurally unreachable via normal LineageContext
        construction because __post_init__ resolves cost_anchor_id from
        execution_config_path at construction time. The post-construction
        tamper path (via object.__setattr__ bypassing frozen-dataclass guard)
        is closed by SYS5 revalidate_for_write() invariant invoked at write-
        boundary.

        Cross-reference: tests/test_t1_1_sys_fix.py:2583
        TestSys5RevalidateForWriteDirectStrictFields covers the full 14-field
        tamper class; §2.3.6 references the engine→registry pathway
        specifically via cost_anchor_id tamper.

        Phase B anchor naming-namespace divergence (per IPFR-fix Advisor #6
        MEDIUM-2 2026-05-24): registry test deliberately uses Phase B Tier
        5/6 anchor `spot_realistic_15bps_v1` (at L412 below) to trigger
        cost_anchor_id mismatch — the tamper test needs a real-but-different
        anchor ID from the construction-time-resolved
        `legacy_perp_inspired_7bps_v0` (from `config/execution.yaml`) to
        exercise the mismatch detection path. Smoke test §2.2.6 explicitly
        AVOIDS Phase B anchor to prevent promotion-namespace conceptual
        confusion in non-promotion smoke scope; registry tamper test scope
        is INTRINSICALLY mismatch-triggering, so Phase B anchor use here is
        intentional + bounded to this specific tamper test (not propagated
        to other §2.3 tests or to §2.2 smoke).
        """
        import backtest.experiment_registry as registry_mod
        from backtest.artifact_schema import LineageContext
        from backtest.engine import _write_to_registry

        tmp_db = _make_db(tmp_path, name="mismatch.db")
        monkeypatch.setattr(registry_mod, "DEFAULT_DB_PATH", tmp_db)

        lc = LineageContext(
            run_id="mismatch-run-id",
            hypothesis_hash="h",
            source_batch_id="b",
            regime_key="v2.regime_holdout",
            engine_commit="abc123",
            current_git_sha="def456",
            execution_config_path="config/execution.yaml",
            execution_config_sha256="sha256:exec",
            parquet_data_sha256="sha256:parquet",
            returns_per_bar_path="returns_per_bar.parquet",
            returns_per_bar_sha256="sha256:rpb",
            T_obs=100,
            parent_run_id=None,
        )
        # Post-construction tamper (intentional bypass of frozen guard)
        object.__setattr__(lc, "cost_anchor_id", "spot_realistic_15bps_v1")

        args = _make_minimal_write_args(run_id="mismatch-run-id")
        args["db_path"] = tmp_db
        args["lineage_context"] = lc

        with pytest.raises(ValueError) as exc_info:
            _write_to_registry(**args)

        msg = str(exc_info.value)
        assert "cost_anchor_id" in msg, (
            f"Mismatch must surface cost_anchor_id field in message; "
            f"got: {msg!r}"
        )

    def test_failure_5_unmapped_path_via_lineage_context_construction(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Un-mapped execution_config_path fails closed at LineageContext __post_init__.

        Per Contract 2.0.4 fail-closed clause via LC __post_init__ path
        (vs scalar-path covered at T1.4 B2.c).

        Cross-reference: tests/test_t1_4_backward_compat.py:712
        TestT1_4_B2_LegacyDefaultNormalization covers the scalar-path entry
        (B2.c). This test covers the LineageContext-construction-time fail-
        closed (raises at __post_init__, NOT at _write_to_registry).

        Error message content per Codex F3 v2 PFR tightening precedent at
        T1.4 B2.c: FULL mapping enumeration MUST be present (all 6 entries
        of COST_ANCHOR_ID_MAPPING) so operators can immediately see the
        accepted set.
        """
        from backtest.artifact_schema import COST_ANCHOR_ID_MAPPING, LineageContext

        unmapped_path = "config/execution_phase4_unknown.yaml"

        with pytest.raises(ValueError) as exc_info:
            LineageContext(
                run_id="unmapped-run-id",
                hypothesis_hash="h",
                source_batch_id="b",
                regime_key="v2.regime_holdout",
                engine_commit="e",
                current_git_sha="g",
                execution_config_path=unmapped_path,
                execution_config_sha256="s1",
                parquet_data_sha256="s2",
                returns_per_bar_path="",
                returns_per_bar_sha256="",
                T_obs=10,
                parent_run_id=None,
            )

        msg = str(exc_info.value)
        # Unmapped path identifier should appear (filename suffix at minimum)
        assert ("unknown.yaml" in msg) or (unmapped_path in msg), (
            f"Unmapped path failure must identify the un-mapped path; "
            f"got: {msg!r}"
        )
        # FULL mapping enumeration per Codex F3 v2 PFR precedent at T1.4 B2.c
        for path_key, anchor_id in COST_ANCHOR_ID_MAPPING.items():
            assert path_key in msg, (
                f"Mapping entry path_key={path_key!r} missing from error "
                f"message; per Contract 2.0.4 fail-closed clause + T1.4 B2.c "
                f"Codex F3 tightening precedent, FULL mapping enumeration "
                f"must be surfaced. Got: {msg!r}"
            )
            assert anchor_id in msg, (
                f"Mapping entry anchor_id={anchor_id!r} missing from error "
                f"message. Got: {msg!r}"
            )

    @pytest.mark.skipif(
        platform.system() == "Linux",
        reason=(
            "DS6 LOCK §2.3.10 Edge B (case-only mismatch on case-insensitive "
            "filesystem) per Contract 2.0.4 line 106. Linux ext4 default is "
            "case-sensitive — the case-mismatched path would resolve to a "
            "non-existent file rather than via case-folding, so the test "
            "semantic does not apply on Linux. macOS HFS+/APFS default is "
            "case-insensitive (this test's target)."
        ),
    )
    def test_canonicalization_case_only_mismatch_fails_closed_on_case_insensitive_fs(
        self,
    ) -> None:
        """Case-only mismatch on case-insensitive FS fails closed via mapping miss.

        Per Contract 2.0.4 line 106 case-sensitivity policy LOCK:
        "On case-insensitive filesystems (macOS HFS+/APFS default), exact-
        case match is required at mapping lookup (do NOT apply
        os.path.normcase); case-only mismatches (e.g., config/Execution.yaml)
        FAIL CLOSED via mapping miss. This is intentional — mapping table
        keys are case-sensitive lowercase by convention."

        DS6 LOCK per subagent recommendation + Charlie R1 ADOPT (§2.3.10
        recommend Edge B include only; A + C deferred to T1.4 B2.d + T1.3
        canonicalize unit test scope).

        [VERIFIED at Implementation PFR 2026-05-24 on macOS APFS]: realpath()
        on macOS APFS preserves input case (does NOT case-fold); case-
        mismatched input `config/Execution.yaml` does NOT resolve to
        canonical lowercase path; mapping lookup correctly raises ValueError
        via mapping miss as Contract 2.0.4 spec requires. Test PASSED at
        orchestrator run + Codex IPFR independent re-verification. Resolves
        sub-plan v3.1 PFR-rule-Y v4 [UNVERIFIED] tag per Advisor #6 IPFR
        LOW-5 2026-05-24.

        Skip on Linux: case-sensitive filesystem; case-mismatched path
        resolves to non-existent file (test semantic does not apply).
        """
        from backtest.artifact_schema import LineageContext

        case_mismatch_path = "config/Execution.yaml"  # capital E (mapping key is lowercase)

        with pytest.raises(ValueError) as exc_info:
            LineageContext(
                run_id="case-mismatch-run-id",
                hypothesis_hash="h",
                source_batch_id="b",
                regime_key="v2.regime_holdout",
                engine_commit="e",
                current_git_sha="g",
                execution_config_path=case_mismatch_path,
                execution_config_sha256="s1",
                parquet_data_sha256="s2",
                returns_per_bar_path="",
                returns_per_bar_sha256="",
                T_obs=10,
                parent_run_id=None,
            )

        msg = str(exc_info.value)
        # Error message should identify the path or field name
        assert ("Execution.yaml" in msg) or ("execution_config_path" in msg), (
            f"Case-mismatch failure must identify path or field; got: {msg!r}"
        )
