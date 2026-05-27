# B-C-narrow Phase 2 — Producer TDD Sub-Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this sub-plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Sub-plan scope:** Phase 2 of B-C-narrow data-recovery cycle ONLY — producer edits at `scripts/run_phase2c_evaluation_gate.py` (5 substantive zones + 2 NEW functions + 1 NEW CLI flag) under strict TDD discipline. NO engine code edits (Phase 0 sealed at `f112599`). NO data writes outside test tmp_path. NO new test files (Phase 3-4 will add `tests/test_b_c_narrow_recovery.py` + `tests/test_b_c_narrow_v4_reproducibility.py` per spec §6.1).

**Sub-plan motivation:** Phase 0 (engine extension; sealed at task level 2026-05-27 per Charlie register `SEAL-TASK-LEVEL`) added `RegimeHoldoutResult.equity_curve` + 4 LC-b kwargs + LC-b internal `LineageContext` construction + atomic write-then-registry sequencing in `run_regime_holdout`. Phase 1 (pre-impl gates; sealed at task level 2026-05-27) returned all 4 BLOCKING gates PASS (G1 engine-diff audit + G2 DSL backward-compat + G3 raw_payloads inventory + G3.5 engine extension smoke pre-satisfied). Phase 2 wires the producer to consume Phase 0's LC-b API and finalize the cohort registry layout. Phase 2 also lands the 4 BLOCKING-carry items deferred from Phase 0 plan v2 PFR R2 — BLOCKING-1 R9 architectural call-order fix + BLOCKING-3 `create_table` precondition + BLOCKING-4 `_parse_args` → `_build_argparser` reference correction + BLOCKING-6 T1.4 grep methodology replaced with AST classifier output. Per Charlie register PV3-SPLIT-BY-PHASE 2026-05-26: per-phase ratify + SEAL discipline preserved.

**Tech Stack:** Python 3.11+, pytest, SQLite (`backtest.experiment_registry`), pathlib, shutil, pandas, argparse. NO new dependencies.

**Cycle context:** R6.1 V_SEAL §10 binding precondition (`d6c7fc0` spec doc); cycle entry Charlie register N1 2026-05-26. Phase 2 is the LARGEST sub-plan (substantively) of the 5-phase B-C-narrow arc (Phase 0 sealed → Phase 1 sealed → Phase 2 this sub-plan → Phase 3 fire → Phase 4 cycle SEAL). Phase 3-4 sub-plans drafted SEPARATELY per Charlie register chain (anti-pre-emption).

---

## Codex BLOCKING-carry fixes addressed in this sub-plan (4 from Phase 0 plan v2 PFR R2)

| # | BLOCKING-carry from Phase 0 plan v2 | Fix applied in this sub-plan |
|---|---|---|
| **BLOCKING-1** | R9 finalizer call-order architectural flaw: original v2 wiring placed `_finalize_batch_registry` AFTER children written, which then refuses or deletes them. | **Task 10**: R9 split into TWO halves — (PRE-flight) `_finalize_batch_registry_preflight_or_raise()` BEFORE candidate loop checks parent_run_id absence (refuse-if-exists; `--force-rerun-existing` opt-in DELETEs WHERE parent_run_id); (POST-fire) `_finalize_batch_registry()` AFTER candidate loop writes the parent batch_summary row only. Children written by engine inside `run_regime_holdout` per Phase 0 sequencing. |
| **BLOCKING-3** | `_finalize_batch_registry` queries SQLite before `create_table` runs → OperationalError on missing `runs` table. | **Task 10 Step 10.4**: `_finalize_batch_registry()` imports `create_table` + `get_connection` + `insert_run` from `backtest.experiment_registry` and calls `create_table(conn)` UNCONDITIONALLY before `insert_run(conn, parent_row_dict)`. Idempotent (CREATE TABLE IF NOT EXISTS + MIGRATION_COLUMNS additive). |
| **BLOCKING-4** | Phase 0 plan v2 test code referenced `_parse_args` — function does NOT exist in `scripts/run_phase2c_evaluation_gate.py`. The actual function is `_build_argparser()` at line 726. | **Task 9 Step 9.2**: every Phase 2 test that touches the producer's argparse layer references `_build_argparser()` (verified at scripts:726). Added explicit test `test_build_argparser_callable_no_parse_args` to lock the convention going forward. |
| **BLOCKING-6** | Phase 0 plan v2 §6.5 "Plan v1 computes exact via grep" for T1.4 4-tuple update — grep-based counting is methodologically wrong per `tests/test_t1_4_backward_compat.py:67-80` §8.1 METHODOLOGY DIVERGENCE NOTE (AST-correct numbers required; grep over-counts by including `def` + docstrings + comments). | **Task 11**: T1.4 baseline maintenance uses the AST classifier at `TestT1_4_B1_SignatureBackwardCompat._enumerate_call_sites()` (lines 422-488) to compute new 4-tuple. NO grep counting anywhere. AST classifier dry-run runs BEFORE updating `_B1_LOCKED_4TUPLE`; observed counts inserted with rationale. |

**Locked decisions consumed (do NOT re-litigate per handoff):**

| Decision | Lock value | Source |
|---|---|---|
| R9 mechanism | R9-B-guarded: refuse-if-exists + `--force-rerun-existing` opt-in (DELETE WHERE parent_run_id) + Charlie manual confirm if parent_run_id re-used | Charlie register pre-PV2 |
| LineageContext construction | LC-b 4-kwarg lock (run_id_override + source_batch_id + parent_run_id_override + artifact_dir); cost_anchor_id DERIVED in LC `__post_init__` | Charlie register pre-PV2 + Codex R2 confirmation (Phase 0 SEAL) |
| Cycle-scope CLI flag | `--enable-b-c-narrow-recovery` (NEW flag; default False) — gates the 3 NEW producer behaviors (archive PRE-flight + finalize PRE-flight guard + finalize POST-fire); legacy callers (PHASE2C_15, PHASE2C_8.1, etc.) unaffected | Plan v3-Phase2 v1 lock (this plan) |
| γ3/γ4 persistence | Per-candidate `holdout_summary.json` ONLY (NOT registry rows); T_obs in BOTH | Spec §3.6 |
| Compensating cleanup | Option (a) refuse-if-exists by default + `--force-rerun-existing` opt-in DELETE; manual cleanup otherwise (R9-B-guarded) | Charlie register pre-PV2 |
| TDD discipline | No敷衍 — all test bodies are runnable code with full assertions; no placeholders | Charlie register pre-PV2 + Phase 0/1 precedent |

---

## File Structure (Phase 2 scope only)

| File | Action | Scope |
|---|---|---|
| `scripts/run_phase2c_evaluation_gate.py` | MODIFY | 7 modify-zones (per Task 10):<br>• **Imports** (Step 10.1): add `create_table`, `get_connection`, `insert_run`, `get_run` from `backtest.experiment_registry`; `compute_moments`, `compute_per_bar_returns`, `_compute_sha256_file` from `backtest.engine`; `shutil` for archive `move`<br>• **`_build_argparser`** (Step 10.2): add `--enable-b-c-narrow-recovery` boolean flag + `--force-rerun-existing` boolean flag<br>• **NEW `_archive_canonical_pre_flight()`** (Step 10.3): pre-loop archive of `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` → `archive/phase4_forward_2026_15bps_v1_d0b8101/`<br>• **NEW `_finalize_batch_registry_preflight_or_raise()`** (Step 10.4a): BLOCKING-1 PRE-flight guard (refuse-if-exists; `--force-rerun-existing` DELETE WHERE parent_run_id)<br>• **NEW `_finalize_batch_registry()`** (Step 10.4b): BLOCKING-1 POST-fire parent row write via `insert_run`; calls `create_table` first (BLOCKING-3 fix)<br>• **`_evaluate_one_candidate`** signature + body (Step 10.5; lines 480-573): add 4 LC-b kwargs + compute moments + merge B-C-narrow fields into inline JSON write at lines 550-556<br>• **`_CSV_FIELDS`** (Step 10.6; lines 581-595): add 5 new fields (gamma3, gamma4, T_obs, returns_per_bar_path, returns_per_bar_sha256)<br>• **`_write_aggregate_csv`** (Step 10.7; lines 598-637): emit 5 new fields per row<br>• **`main()`** (Step 10.8; lines 864-1072): wire `_archive_canonical_pre_flight` (between overwrite-protection at line 929 and `run_dir.mkdir` at line 946) + wire `_finalize_batch_registry_preflight_or_raise` (after archive PRE-flight) + thread `artifact_dir_root` + `parent_run_id_override` to `_evaluate_one_candidate` + wire `_finalize_batch_registry` after candidate loop (after CSV write at line 996; before aggregate JSON write at line 1053) |
| `tests/test_phase2c_evaluation_gate_runner.py` | EXTEND | NEW `TestBCNarrowPhase2ProducerEdits` class (14 test methods; all bodies full runnable code per Charlie no敷衍 + Phase 0 precedent) |
| `tests/test_t1_4_backward_compat.py` | MODIFY | `_B1_LOCKED_4TUPLE` update at lines 84-89 per AST classifier dry-run output post-Phase-2-implementation commits + (if any new dynamic-pattern test) extend `approved_files` at lines 538-541 with rationale |

**Data layer (Phase 2):** none. Phase 2 touches NO data files; archive step + parent-row DB write are exercised in tests via tmp_path isolation. The actual recovery fire is Phase 3 (separate sub-plan + Charlie register-event #N+3).

**No engine code changes.** Phase 0 sealed at `f112599`. Phase 2 consumes Phase 0's LC-b API verbatim.

---

## Pre-Phase-2 Charlie register-event boundary (HISTORICAL — Phase 1 SEAL fulfilled)

Phase 1 task-level SEAL acknowledged 2026-05-27 per Charlie register `SEAL-TASK-LEVEL` (no Phase Marker advance per anti-pre-emption — arc-level closeout reserved for Phase 4 cycle SEAL). Phase 1 evidence chain (now on origin/main at `b10ffb2`):

| Commit | Role |
|---|---|
| `e583e78` | Plan v3-Phase1 v1 drafted |
| `b1a183f` | Plan v3-Phase1 v2 (PFR R1 11 inline fixes) |
| `b8d6523` | Plan v3-Phase1 v3 SEAL (PFR R2 6 inline fixes; convergent APPROVE post PFR R3) |
| `b10ffb2` | Phase 1 evidence chain (G1+G2+G3+G3.5 gate results; 5 artifacts; 599 lines) |

Phase 1 ratify packet at [`docs/superpowers/phase-1-gate-results/phase-1-ratify-summary.md`](../phase-1-gate-results/phase-1-ratify-summary.md). All 4 gates PASS. V4 ε=1e-6 expected achievable at §4.2 post-impl gate (Phase 3 fire).

Plan v3-Phase2 drafting authorized 2026-05-27 per Charlie register `Path A — DRAFT-V1-NOW` (separate register-event #N+2 from Phase 1 ratify per anti-pre-emption).

---

# Phase 2 — Producer edits (Tasks 9-12)

## Phase 2 execution preconditions

Before any T9-T12 execution, verify:

- [ ] **Precondition 1: Clean working tree** (Phase 1 precedent — PFR R2 HIGH-2/NEW-2 fix v3 carryforward)

V4 reproducibility claims at Phase 3 will reference Phase 2 SEAL HEAD. If any code module touched by Phase 2 has unstaged modifications mid-execution, gates execute against modified files but claims reference a stale SHA — silent breach. Verify clean state:

```bash
git status --porcelain backtest/ tests/ config/ scripts/ strategies/ factors/
```

Expected: empty output (untracked `backtest/engine.py,cover` from coverage tool is acceptable — filter with `grep -v '^??'`). Any tracked-file modification → STOP and surface to Charlie (uncommitted changes must be either committed or stashed before Phase 2 dispatch).

- [ ] **Precondition 2: Writable execution environment** (Phase 1 PFR R1 LOW F6 fix v2 carryforward)

```bash
python -c "import tempfile; f = tempfile.NamedTemporaryFile(); print(f'writable: {f.name}'); f.close()"
```

Expected: prints a temp file path successfully. Failure → environment issue, NOT a real test failure; surface to Charlie for environment remediation.

- [ ] **Precondition 3: Phase 0 SEAL chain present on HEAD**

Phase 2 tests + producer edits consume Phase 0 LC-b API. Verify:

```bash
python -c "from backtest.engine import run_regime_holdout, RegimeHoldoutResult, compute_per_bar_returns, compute_moments, write_per_bar_artifact, _compute_sha256_file, _resolve_canonical_parquet_path; import inspect; sig = inspect.signature(run_regime_holdout); assert 'run_id_override' in sig.parameters and 'source_batch_id' in sig.parameters and 'parent_run_id_override' in sig.parameters and 'artifact_dir' in sig.parameters, 'Phase 0 LC-b kwargs missing'; from dataclasses import fields; assert 'equity_curve' in {f.name for f in fields(RegimeHoldoutResult)}, 'Phase 0 equity_curve field missing'; print('Phase 0 SEAL chain verified.')"
```

Expected: prints `Phase 0 SEAL chain verified.` Any AssertionError → Phase 0 commits missing from HEAD; STOP and surface to Charlie.

---

### Task 9: Write FAILING producer-edit tests (TDD RED)

**Files:**
- Modify: `tests/test_phase2c_evaluation_gate_runner.py` (append `TestBCNarrowPhase2ProducerEdits` class)

**Reuse:** `_stub_corrected_candidates` at line 51 + existing fixture patterns at lines 78-108. Use `dsl_bollinger_zscore_reversion` fixture from `tests/conftest.py` (Phase 0 deliverable) for end-to-end tests that need a real DSL.

- [ ] **Step 9.1: Verify required imports present at top of `tests/test_phase2c_evaluation_gate_runner.py`**

```bash
head -50 tests/test_phase2c_evaluation_gate_runner.py
```

Required imports (add at module top if missing):

```python
import json
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from backtest.engine import RegimeHoldoutResult, compute_moments, compute_per_bar_returns
from backtest.experiment_registry import create_table, get_connection, get_run, insert_run
from scripts.run_phase2c_evaluation_gate import (
    _CSV_FIELDS,
    _archive_canonical_pre_flight,
    _build_argparser,
    _evaluate_one_candidate,
    _finalize_batch_registry,
    _finalize_batch_registry_preflight_or_raise,
    _write_aggregate_csv,
    _write_aggregate_summary,
)
```

Note: 3 symbols (`_archive_canonical_pre_flight`, `_finalize_batch_registry`, `_finalize_batch_registry_preflight_or_raise`) are NEW per Task 10 — these imports will fail at RED-phase test collection (NameError on import). Expected.

- [ ] **Step 9.2: Append `TestBCNarrowPhase2ProducerEdits` class to `tests/test_phase2c_evaluation_gate_runner.py`**

Add the following class. Each test body is FULL runnable code — no placeholders, no `# similar to above`, no comment-only methods.

```python
# tests/test_phase2c_evaluation_gate_runner.py — APPEND at end (before any trailing teardowns)


class TestBCNarrowPhase2ProducerEdits:
    """Phase 2 producer-edit tests per spec §6.3 (12 enumerated) + BLOCKING-4 reference test (1) + LC-b threading test (1) = 14 methods.

    Locked decisions:
    - --enable-b-c-narrow-recovery CLI flag gates the recovery flow (3 NEW behaviors)
    - Archive step uses shutil.move with refuse-if-exists guard (R10 §4.3 G7)
    - `_finalize_batch_registry()` calls create_table before insert_run (BLOCKING-3 fix)
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
        """
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir  # same directory; per-candidate subdirs created below

        captured_kwargs: dict = {}

        def fake_run_regime_holdout(**kwargs):
            captured_kwargs.update(kwargs)
            return stub_holdout_result

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            side_effect=fake_run_regime_holdout,
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
        """
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        artifact_dir = artifact_dir_root / stub_candidate["hypothesis_hash"]
        artifact_dir.mkdir(parents=True)
        # Pre-create a fake returns_per_bar.parquet so the producer's SHA256
        # computation succeeds (engine's write step is bypassed by mocking
        # run_regime_holdout above).
        (artifact_dir / "returns_per_bar.parquet").write_bytes(b"fake-parquet-bytes-for-sha-only")

        captured_equity_curve_id: list = []

        def fake_run_regime_holdout(**kwargs):
            # Use object identity check by appending id to captured list
            captured_equity_curve_id.append(id(stub_holdout_result.equity_curve))
            return stub_holdout_result

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            side_effect=fake_run_regime_holdout,
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_per_bar_returns"
        ) as mock_pbr, patch(
            "scripts.run_phase2c_evaluation_gate.compute_moments"
        ) as mock_moments:
            mock_pbr.return_value = pd.Series([0.01] * 2527)
            mock_moments.return_value = {"gamma3": 0.5, "gamma4": 3.2, "T_obs": 2527, "mean": 0.01, "std": 0.005}

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
        includes gamma3, gamma4, T_obs from compute_moments output."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        artifact_dir = artifact_dir_root / stub_candidate["hypothesis_hash"]
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "returns_per_bar.parquet").write_bytes(b"fake-parquet-bytes")

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            return_value=stub_holdout_result,
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_per_bar_returns",
            return_value=pd.Series([0.01] * 2527),
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_moments",
            return_value={"gamma3": 0.5, "gamma4": 3.2, "T_obs": 2527, "mean": 0.01, "std": 0.005},
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
            )

        summary_path = artifact_dir / "holdout_summary.json"
        assert summary_path.exists(), f"holdout_summary.json missing at {summary_path}"
        summary = json.loads(summary_path.read_text())
        assert summary.get("gamma3") == 0.5, f"gamma3 missing/wrong: {summary.get('gamma3')!r}"
        assert summary.get("gamma4") == 3.2, f"gamma4 missing/wrong: {summary.get('gamma4')!r}"
        assert summary.get("T_obs") == 2527, f"T_obs missing/wrong: {summary.get('T_obs')!r}"

    # ----- 4. Path + SHA in summary JSON (1 test) -----

    def test_evaluate_one_candidate_summary_includes_returns_per_bar_path_sha(
        self, stub_holdout_result, stub_candidate, tmp_path
    ):
        """Verify summary dict includes returns_per_bar_path (relative to output_dir)
        + returns_per_bar_sha256 (64-char lowercase hex)."""
        import hashlib

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        artifact_dir = artifact_dir_root / stub_candidate["hypothesis_hash"]
        artifact_dir.mkdir(parents=True)
        parquet_bytes = b"deterministic-parquet-content-for-sha-verification"
        parquet_path = artifact_dir / "returns_per_bar.parquet"
        parquet_path.write_bytes(parquet_bytes)
        expected_sha = hashlib.sha256(parquet_bytes).hexdigest()

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            return_value=stub_holdout_result,
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_per_bar_returns",
            return_value=pd.Series([0.01] * 2527),
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_moments",
            return_value={"gamma3": 0.5, "gamma4": 3.2, "T_obs": 2527, "mean": 0.01, "std": 0.005},
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
            )

        summary = json.loads((artifact_dir / "holdout_summary.json").read_text())
        # returns_per_bar_path must be relative to output_dir (NOT absolute)
        rpb_path = summary.get("returns_per_bar_path")
        assert rpb_path is not None, "returns_per_bar_path missing"
        assert not Path(rpb_path).is_absolute(), (
            f"returns_per_bar_path must be relative to output_dir; got absolute: {rpb_path!r}"
        )
        expected_rel = f"{stub_candidate['hypothesis_hash']}/returns_per_bar.parquet"
        assert rpb_path == expected_rel, (
            f"returns_per_bar_path mismatch: expected {expected_rel!r}, got {rpb_path!r}"
        )
        # SHA256 lowercase hex
        rpb_sha = summary.get("returns_per_bar_sha256")
        assert rpb_sha is not None and len(rpb_sha) == 64
        int(rpb_sha, 16)  # ValueError on non-hex
        assert rpb_sha == rpb_sha.lower(), f"SHA must be lowercase: {rpb_sha!r}"
        assert rpb_sha == expected_sha, (
            f"SHA256 mismatch: expected {expected_sha!r}, got {rpb_sha!r}"
        )

    # ----- 5. _finalize_batch_registry parent-only write (1 test) -----

    def test_finalize_batch_registry_writes_parent_row_only(
        self, tmp_path
    ):
        """Verify `_finalize_batch_registry()` writes ONLY the 1 parent batch_summary row
        at run_id=parent_run_id; does NOT write any child rows. Children are written
        per-candidate inside engine's run_regime_holdout `_write_to_registry` call
        (Phase 0 sequencing per spec §3.1.2)."""
        db_path = tmp_path / "test_parent_only.db"

        cohort_metadata = {
            "execution_config_path": "config/execution_phase4_15bps.yaml",
            "execution_config_sha256": "a" * 64,
            "parquet_data_sha256": "b" * 64,
            "regime_key": "evaluation_regimes.forward_2026",
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "current_git_sha": "f112599",
            "effective_start": "2026-01-01T00:00:00Z",
            "initial_capital": 100000.0,
            "fee_model": "phase4_15bps_v1",
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
        db_path = tmp_path / "test_cohort_meta.db"
        cohort_metadata = {
            "execution_config_path": "config/execution_phase4_15bps.yaml",
            "execution_config_sha256": "c" * 64,
            "parquet_data_sha256": "d" * 64,
            "regime_key": "evaluation_regimes.forward_2026",
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "current_git_sha": "f112599",
            "effective_start": "2026-01-01T00:00:00Z",
            "initial_capital": 100000.0,
            "fee_model": "phase4_15bps_v1",
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
        f'{parent_run_id}_{hypothesis_hash}' scheme (spec §2 Q4 + §3.4)."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir

        captured_run_id_override: list = []

        def fake_run_regime_holdout(**kwargs):
            captured_run_id_override.append(kwargs.get("run_id_override"))
            return stub_holdout_result

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            side_effect=fake_run_regime_holdout,
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_per_bar_returns",
            return_value=pd.Series([0.01] * 2527),
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_moments",
            return_value={"gamma3": 0.5, "gamma4": 3.2, "T_obs": 2527, "mean": 0.01, "std": 0.005},
        ):
            artifact_dir = artifact_dir_root / stub_candidate["hypothesis_hash"]
            artifact_dir.mkdir(parents=True)
            (artifact_dir / "returns_per_bar.parquet").write_bytes(b"x")
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
            )

        expected = f"{self.PARENT_RUN_ID}_{stub_candidate['hypothesis_hash']}"
        assert captured_run_id_override == [expected], (
            f"Child run_id_override scheme drift: expected {expected!r}, "
            f"got {captured_run_id_override!r}. Spec §2 Q4 lock: "
            f"f'{{parent_run_id}}_{{hypothesis_hash}}'."
        )

    # ----- 8. Parent idempotency refuses duplicate (1 test) -----

    def test_finalize_batch_registry_parent_idempotency_refuses_duplicate(
        self, tmp_path
    ):
        """Verify _finalize_batch_registry_preflight_or_raise raises if parent
        run_id already exists in registry (R9 §7 refuse-if-exists)."""
        db_path = tmp_path / "test_idempotent.db"
        cohort_metadata = {
            "execution_config_path": "config/execution_phase4_15bps.yaml",
            "execution_config_sha256": "e" * 64,
            "parquet_data_sha256": "f" * 64,
            "regime_key": "evaluation_regimes.forward_2026",
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "current_git_sha": "f112599",
            "effective_start": "2026-01-01T00:00:00Z",
            "initial_capital": 100000.0,
            "fee_model": "phase4_15bps_v1",
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

        Simulates partial-cohort write: 5 child rows inserted, parent NOT yet,
        then operator passes --force-rerun-existing → preflight DELETEs 5 children
        + (if parent exists) parent → clean state ready for re-fire."""
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
                    "fee_model": "phase4_15bps_v1",
                    "initial_capital": 100000.0,
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
                "fee_model": "phase4_15bps_v1",
                "initial_capital": 100000.0,
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
        NOT raise on the augmented summary."""
        from backtest.wf_lineage import check_evaluation_semantics_or_raise

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        artifact_dir = artifact_dir_root / stub_candidate["hypothesis_hash"]
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "returns_per_bar.parquet").write_bytes(b"x")

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            return_value=stub_holdout_result,
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_per_bar_returns",
            return_value=pd.Series([0.01] * 2527),
        ), patch(
            "scripts.run_phase2c_evaluation_gate.compute_moments",
            return_value={"gamma3": 0.5, "gamma4": 3.2, "T_obs": 2527, "mean": 0.01, "std": 0.005},
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
            )

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
```

- [ ] **Step 9.3: Run all 14 new tests — they MUST FAIL (RED)**

```bash
cd /Users/yutianyang/Documents/GitHub/btc-alpha-pipeline
python -m pytest tests/test_phase2c_evaluation_gate_runner.py::TestBCNarrowPhase2ProducerEdits -v
```

Expected: most tests FAIL at collection time with `ImportError` on `_archive_canonical_pre_flight`, `_finalize_batch_registry`, or `_finalize_batch_registry_preflight_or_raise` (NEW functions per Task 10). Some tests may also FAIL with `TypeError: _evaluate_one_candidate() got an unexpected keyword argument 'artifact_dir_root'` or `AttributeError` on missing `_CSV_FIELDS` entries.

If ALL 14 tests pass at this point → SOMETHING WRONG (Task 10 already implemented OR tests are no-ops). Halt and inspect.

- [ ] **Step 9.4: Commit failing tests**

```bash
git add tests/test_phase2c_evaluation_gate_runner.py
git commit -m "test(b-c-narrow/phase-2): add 14 failing producer-edit tests (T9)

Per Plan v3-Phase2 Task 9. RED-phase tests verify (post-Task-10):
- LC-b kwarg threading from producer to engine (1 test)
- equity_curve consumption from extended RegimeHoldoutResult (1 test)
- γ3/γ4/T_obs merge into inline per-candidate JSON write (1 test)
- returns_per_bar_path (relative) + returns_per_bar_sha256 (lowercase hex) in JSON (1 test)
- _finalize_batch_registry parent-only write (no child rows) (1 test)
- Parent cohort metadata complete + per-candidate metric fields NULL (1 test)
- Child run_id deterministic scheme f'{parent_run_id}_{hypothesis_hash}' (1 test)
- Parent idempotency refuse-if-exists without --force-rerun-existing (1 test)
- Compensating cleanup DELETE WHERE parent_run_id with --force-rerun-existing (1 test)
- Archive step creates archive/ dir if absent (1 test)
- Archive step refuses existing target (G7 §4.3) (1 test)
- _CSV_FIELDS extension with 5 new fields (1 test)
- BLOCKING-4 _build_argparser callable + --enable-b-c-narrow-recovery + --force-rerun-existing flags (1 test)
- Schema domain routing: evaluation_domain on summary with ADDITIVE B-C-narrow fields (1 test)

All 14 tests FAIL at this commit (RED phase). T10 implements producer edits to bring GREEN."
```

---

### Task 10: Implement producer edits (TDD GREEN)

**Files:**
- Modify: `scripts/run_phase2c_evaluation_gate.py` (7 modify-zones per File Structure table above)

This is the largest task. Implementation order: imports → CLI flags → archive step → finalize step → `_evaluate_one_candidate` → CSV fields → CSV writer → `_aggregate_summary_dict` (NOT touched per spec §3.2.2 — cohort fields already cohort-level) → `main()` wiring → GREEN.

- [ ] **Step 10.1: Add imports**

Edit `scripts/run_phase2c_evaluation_gate.py` near top of file (after existing imports, around line 87-103). Add:

```python
import shutil  # B-C-narrow Phase 2: archive PRE-flight uses shutil.move

# B-C-narrow Phase 2: producer-side moments + LC-b file sha helpers (Phase 0 SEAL chain f112599)
from backtest.engine import (  # noqa: E402  (sys.path.insert prepended above)
    compute_moments,
    compute_per_bar_returns,
    _compute_sha256_file,
)
from backtest.experiment_registry import (  # noqa: E402
    create_table,
    get_connection,
    get_run,
    insert_run,
)
```

**Placement:** AFTER the existing `from backtest.engine import run_regime_holdout, RegimeHoldoutResult` block at line 92, and AFTER the existing `from backtest.wf_lineage import (...)` block at lines 93-102. The new imports are additive; existing imports preserved verbatim.

Verify imports resolve cleanly:

```bash
python -c "from scripts.run_phase2c_evaluation_gate import compute_moments, compute_per_bar_returns, _compute_sha256_file, create_table, get_connection, get_run, insert_run; print('imports OK')"
```

Expected: `imports OK`.

- [ ] **Step 10.2: Add `--enable-b-c-narrow-recovery` + `--force-rerun-existing` CLI flags**

Edit `_build_argparser()` at lines 726-837. Append BEFORE the final `return parser` at line 837 (after the existing `--execution-config` block at lines 823-836):

```python
    # B-C-narrow Phase 2 recovery flags (spec §3.2.3 + §3.2.4; R9-B-guarded lock).
    parser.add_argument(
        "--enable-b-c-narrow-recovery",
        action="store_true",
        default=False,
        help=(
            "Enable B-C-narrow data-recovery flow (3 NEW behaviors): "
            "(1) PRE-flight archive of canonical phase4_forward_2026_15bps_v1/ "
            "to archive/phase4_forward_2026_15bps_v1_d0b8101/ via shutil.move "
            "(refuse-if-exists); (2) PRE-flight parent_run_id idempotency guard "
            "(refuse-if-exists in registry); (3) POST-fire _finalize_batch_registry "
            "writes the parent batch_summary row (children written by engine "
            "per-candidate inside run_regime_holdout). Default False preserves "
            "backward-compat for legacy callers (PHASE2C_15, PHASE2C_8.1, etc.)."
        ),
    )
    parser.add_argument(
        "--force-rerun-existing",
        action="store_true",
        default=False,
        help=(
            "When --enable-b-c-narrow-recovery is set AND parent_run_id already "
            "exists in registry, DELETE all rows WHERE parent_run_id = ... AND "
            "the parent row itself before re-fire. Operator-confirmed clean state "
            "discipline per R9-B-guarded lock. Default False (refuse-if-exists; "
            "manual cleanup required)."
        ),
    )
```

- [ ] **Step 10.3: Add NEW `_archive_canonical_pre_flight()` function**

Add the function in the producer at a stable location — RECOMMENDED: AFTER `_check_overwrite_protection()` at line 861 and BEFORE `def main():` at line 864. This keeps R9 helpers grouped with main() preconditions.

```python
def _archive_canonical_pre_flight(
    canonical_path: Path,
    archive_root: Path,
    archive_basename: str,
) -> None:
    """B-C-narrow Phase 2: PRE-flight archive of canonical artifact dir before recovery fire.

    Per spec §3.2.4 + BLOCKING-1 R9 PRE-flight split:
    - Check archive_root exists; create if absent.
    - Check archive_root / archive_basename does NOT exist (refuse-if-exists per G7).
    - shutil.move canonical_path → archive_root / archive_basename.
    - Verify post-move: canonical_path vacated; archive target populated.

    Args:
        canonical_path: e.g., data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/
        archive_root:   e.g., data/phase2c_evaluation_gate/archive/
        archive_basename: e.g., "phase4_forward_2026_15bps_v1_d0b8101" (uses original current_git_sha)

    Raises:
        FileNotFoundError: if canonical_path does not exist (nothing to archive).
        FileExistsError: if archive_root / archive_basename already exists
            (operator manual cleanup required per R10 §4.3 G7 strict refuse).
    """
    if not canonical_path.exists():
        raise FileNotFoundError(
            f"B-C-narrow archive PRE-flight: canonical path {canonical_path} does not exist. "
            f"Nothing to archive. (Did Phase 3 already run? Or canonical never present?)"
        )
    archive_root.mkdir(parents=True, exist_ok=True)
    archive_target = archive_root / archive_basename
    if archive_target.exists():
        raise FileExistsError(
            f"B-C-narrow archive PRE-flight: archive target {archive_target} already exists. "
            f"Refusing to overwrite (G7 §4.3 strict). Operator must manually cleanup the "
            f"stale archive (e.g., from a prior aborted attempt) before re-fire. "
            f"Recommended: inspect {archive_target} content before deletion."
        )
    shutil.move(str(canonical_path), str(archive_target))
    if canonical_path.exists():
        raise RuntimeError(
            f"B-C-narrow archive PRE-flight: shutil.move did not vacate canonical_path "
            f"{canonical_path}. Possible cross-filesystem partial move failure."
        )
    if not archive_target.exists():
        raise RuntimeError(
            f"B-C-narrow archive PRE-flight: shutil.move did not populate archive_target "
            f"{archive_target}."
        )
```

- [ ] **Step 10.4: Add NEW `_finalize_batch_registry_preflight_or_raise()` + `_finalize_batch_registry()` functions**

Add both functions AFTER `_archive_canonical_pre_flight()` (so all R9 helpers are grouped pre-main):

```python
def _finalize_batch_registry_preflight_or_raise(
    parent_run_id: str,
    force_rerun_existing: bool,
    db_path: Path | None = None,
) -> None:
    """B-C-narrow Phase 2: PRE-flight idempotency guard for parent_run_id (R9-B-guarded).

    Per spec §3.2.3 + BLOCKING-1 R9 PRE-flight split:
    - Open db via get_connection(db_path); ensure runs table exists (create_table
      is idempotent per BLOCKING-3 fix).
    - Count rows WHERE run_id = parent_run_id (parent itself) AND rows WHERE
      parent_run_id = parent_run_id (children from prior attempt).
    - If any rows present:
      - If force_rerun_existing=False → raise RuntimeError (refuse).
      - If force_rerun_existing=True → DELETE all matching rows (children + parent).
        Commit transaction.

    Args:
        parent_run_id: cohort parent run_id (e.g., "phase4_forward_2026_15bps_v1_b_c_narrow").
        force_rerun_existing: operator opt-in to DELETE pre-existing rows.
        db_path: SQLite registry path. Default None → get_connection's default
            (typically backtest/experiments.db). Default-None co-locates the
            parent row with engine-written children (engine calls get_connection
            with the same default inside _write_to_registry).

    Raises:
        RuntimeError: if pre-existing rows found AND force_rerun_existing=False.
    """
    with get_connection(db_path) as conn:
        create_table(conn)  # BLOCKING-3: ensure runs table exists before query
        n_children = conn.execute(
            "SELECT COUNT(*) FROM runs WHERE parent_run_id = ?", (parent_run_id,)
        ).fetchone()[0]
        n_parent = conn.execute(
            "SELECT COUNT(*) FROM runs WHERE run_id = ?", (parent_run_id,)
        ).fetchone()[0]
        if n_children == 0 and n_parent == 0:
            return  # clean state; proceed
        if not force_rerun_existing:
            raise RuntimeError(
                f"B-C-narrow finalize PRE-flight: parent_run_id {parent_run_id!r} "
                f"already exists in registry ({n_parent} parent row, {n_children} "
                f"child rows). Refusing to re-fire without --force-rerun-existing "
                f"flag (R9-B-guarded lock). Operator must either (a) inspect "
                f"+ accept pre-existing state, OR (b) re-run with --force-rerun-existing "
                f"to DELETE rows and re-fire from clean state."
            )
        # force_rerun_existing=True: DELETE children + parent
        conn.execute("DELETE FROM runs WHERE parent_run_id = ?", (parent_run_id,))
        conn.execute("DELETE FROM runs WHERE run_id = ?", (parent_run_id,))
        conn.commit()


def _finalize_batch_registry(
    parent_run_id: str,
    cohort_metadata: dict[str, Any],
    db_path: Path | None = None,
) -> None:
    """B-C-narrow Phase 2: POST-fire parent batch_summary row write (R9 POST-fire half).

    Per spec §3.2.3:
    - Open db via get_connection(db_path); ensure runs table exists (create_table
      BLOCKING-3 fix).
    - Build parent row dict with cohort-level fields populated + per-candidate
      metric fields NULL.
    - insert_run(conn, parent_row_dict).

    Children (39 rows) are written by engine inside run_regime_holdout's
    _write_to_registry call (Phase 0 sequencing per spec §3.1.2). This function
    writes ONLY the 1 parent row.

    Args:
        parent_run_id: e.g., "phase4_forward_2026_15bps_v1_b_c_narrow".
        cohort_metadata: dict with required keys:
            execution_config_path, execution_config_sha256, parquet_data_sha256,
            regime_key, cost_anchor_id, current_git_sha, effective_start,
            initial_capital, fee_model.
        db_path: SQLite registry path. Default None → get_connection's default
            (typically backtest/experiments.db). Default-None co-locates the
            parent row with engine-written children.
    """
    required_keys = {
        "execution_config_path", "execution_config_sha256", "parquet_data_sha256",
        "regime_key", "cost_anchor_id", "current_git_sha", "effective_start",
        "initial_capital", "fee_model",
    }
    missing = required_keys - set(cohort_metadata.keys())
    if missing:
        raise ValueError(
            f"B-C-narrow _finalize_batch_registry: cohort_metadata missing required "
            f"keys: {sorted(missing)}. Required: {sorted(required_keys)}."
        )

    parent_row = {
        "run_id": parent_run_id,
        "run_type": "batch_summary",
        "parent_run_id": None,
        "strategy_name": "cohort_summary",
        "strategy_source": "b_c_narrow_recovery",
        "git_commit": cohort_metadata["current_git_sha"],
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "effective_start": cohort_metadata["effective_start"],
        "initial_capital": cohort_metadata["initial_capital"],
        "fee_model": cohort_metadata["fee_model"],
        "execution_config_path": cohort_metadata["execution_config_path"],
        "execution_config_sha256": cohort_metadata["execution_config_sha256"],
        "parquet_data_sha256": cohort_metadata["parquet_data_sha256"],
        "regime_key": cohort_metadata["regime_key"],
        "cost_anchor_id": cohort_metadata["cost_anchor_id"],
        "current_git_sha": cohort_metadata["current_git_sha"],
        # Per-candidate metric fields NULL at parent (spec §3.2.3):
        "sharpe_ratio": None,
        "max_drawdown": None,
        "total_return": None,
        "total_trades": None,
        "hypothesis_hash": None,
        "returns_per_bar_path": None,
        "returns_per_bar_sha256": None,
        "T_obs": None,
        "batch_id": parent_run_id,  # parent's batch_id = its own run_id (cohort grouping key)
    }
    with get_connection(db_path) as conn:
        create_table(conn)  # BLOCKING-3: ensure runs table exists before insert
        insert_run(conn, parent_row)
```

- [ ] **Step 10.5: Edit `_evaluate_one_candidate` — signature + LC-b threading + moments merge**

Edit `scripts/run_phase2c_evaluation_gate.py` at function definition starting line 480.

**Signature change (lines 480-489):** add 2 NEW kwargs at end (default None preserves backward-compat for all legacy callers).

```python
def _evaluate_one_candidate(
    candidate: dict[str, Any],
    head_sha: str,
    source_batch_id: str,
    run_id: str,
    output_dir: Path,
    regime_key: str = "v2.regime_holdout",
    execution_config_path: Path | None = None,
    env_config_override: dict[str, Any] | None = None,
    # B-C-narrow Phase 2 LC-b kwargs (default None preserves backward-compat):
    artifact_dir_root: Path | None = None,
    parent_run_id_override: str | None = None,
) -> dict[str, Any]:
```

**Body changes:**

1. Compute LC-b activation early in body (before run_regime_holdout call). Insert AFTER docstring at line 506 (BEFORE `started = datetime.now(...)` at line 507):

```python
    # B-C-narrow Phase 2 LC-b activation: derived from cohort-level artifact_dir_root.
    # When artifact_dir_root is None (legacy callers), LC-b kwargs stay None → engine
    # legacy path. When provided, build per-candidate scalars matching engine's LC-b
    # 4-kwarg contract (Phase 0 SEAL signature).
    lcb_active = artifact_dir_root is not None
    if lcb_active:
        candidate_artifact_dir = artifact_dir_root / candidate["hypothesis_hash"]
        candidate_artifact_dir.mkdir(parents=True, exist_ok=True)
        child_run_id_override = f"{run_id}_{candidate['hypothesis_hash']}"
    else:
        candidate_artifact_dir = None
        child_run_id_override = None
```

2. Modify the `run_regime_holdout(...)` call at lines 512-519. Add 4 LC-b kwargs (passing None when not active is safe per Phase 0 single-gate `lcb_active = artifact_dir is not None`):

```python
        holdout_result = run_regime_holdout(
            dsl=dsl,
            batch_id=source_batch_id,
            parent_run_id=f"phase2c_eval_gate_{run_id}",
            regime_key=regime_key,
            execution_config_path=execution_config_path,
            env_config=env_config_override,
            # B-C-narrow Phase 2 LC-b 4 kwargs (None when artifact_dir_root is None;
            # engine's single-gate lcb_active = artifact_dir is not None → no LC-b path):
            run_id_override=child_run_id_override,
            source_batch_id=source_batch_id if lcb_active else None,
            parent_run_id_override=parent_run_id_override if lcb_active else None,
            artifact_dir=candidate_artifact_dir,
        )
```

3. Add moments compute + B-C-narrow field merge AFTER `summary = _per_candidate_summary(...)` block at lines 538-548, BEFORE `candidate_dir = output_dir / candidate["hypothesis_hash"]` at line 550:

```python
    # B-C-narrow Phase 2: compute γ3/γ4/T_obs from equity_curve + merge into summary.
    # Only on LC-b path AND when holdout_result populated (lifecycle != 'holdout_error');
    # legacy + error paths skip the merge to preserve backward-compat schema.
    if lcb_active and holdout_result is not None:
        returns = compute_per_bar_returns(holdout_result.equity_curve)
        moments = compute_moments(returns)
        summary["gamma3"] = moments.get("gamma3")
        summary["gamma4"] = moments.get("gamma4")
        summary["T_obs"] = moments.get("T_obs")
        # Derive parquet path + SHA from engine's atomic write (engine wrote
        # candidate_artifact_dir / "returns_per_bar.parquet" inside run_regime_holdout
        # per Phase 0 spec §3.1.2). Path is relative to output_dir for portability.
        rpb_absolute = candidate_artifact_dir / "returns_per_bar.parquet"
        if not rpb_absolute.exists():
            raise RuntimeError(
                f"B-C-narrow merge: engine did not write {rpb_absolute} despite LC-b path. "
                f"Possible Phase 0 SEAL regression. Inspect run_regime_holdout."
            )
        summary["returns_per_bar_path"] = str(rpb_absolute.relative_to(output_dir))
        summary["returns_per_bar_sha256"] = _compute_sha256_file(rpb_absolute)
```

The remainder of `_evaluate_one_candidate` (the inline JSON write at lines 550-573) is **NOT changed** — the per-candidate JSON `holdout_summary.json` write at lines 552-556 now naturally includes the merged B-C-narrow fields because `summary` was extended.

- [ ] **Step 10.6: Extend `_CSV_FIELDS`**

Edit `scripts/run_phase2c_evaluation_gate.py` lines 581-595. Append 5 new fields at the end of the tuple:

```python
_CSV_FIELDS: tuple[str, ...] = (
    "hypothesis_hash",
    "position",
    "theme",
    "name",
    "wf_test_period_sharpe",
    "lifecycle_state",
    "holdout_passed",
    "holdout_sharpe",
    "holdout_max_drawdown",
    "holdout_total_return",
    "holdout_total_trades",
    "wall_clock_seconds",
    "error_message",
    # B-C-narrow Phase 2 additions (spec §3.2.5):
    "gamma3",
    "gamma4",
    "T_obs",
    "returns_per_bar_path",
    "returns_per_bar_sha256",
)
```

- [ ] **Step 10.7: Edit `_write_aggregate_csv` to emit the 5 new fields**

Edit `scripts/run_phase2c_evaluation_gate.py` lines 598-637. The DictWriter `writer.writerow({...})` at lines 607-637 currently has 13 keys. Add 5 keys before the closing `})`:

```python
            writer.writerow({
                "hypothesis_hash": s["hypothesis_hash"],
                "position": s["position"],
                "theme": s["theme"],
                "name": s["name"],
                "wf_test_period_sharpe": (
                    f"{s['wf_test_period_sharpe']:.6f}"
                ),
                "lifecycle_state": s["lifecycle_state"],
                "holdout_passed": (
                    "" if s["holdout_passed"] is None
                    else ("1" if s["holdout_passed"] else "0")
                ),
                "holdout_sharpe": (
                    f"{m['sharpe_ratio']:.6f}" if m else ""
                ),
                "holdout_max_drawdown": (
                    f"{m['max_drawdown']:.6f}" if m else ""
                ),
                "holdout_total_return": (
                    f"{m['total_return']:.6f}" if m else ""
                ),
                "holdout_total_trades": (
                    str(m["total_trades"]) if m else ""
                ),
                "wall_clock_seconds": s["wall_clock_seconds"],
                "error_message": (
                    (s.get("error_message") or "").splitlines()[-1]
                    if s.get("error_message") else ""
                ),
                # B-C-narrow Phase 2 additions (spec §3.2.5):
                "gamma3": (
                    f"{s['gamma3']:.6f}" if s.get("gamma3") is not None else ""
                ),
                "gamma4": (
                    f"{s['gamma4']:.6f}" if s.get("gamma4") is not None else ""
                ),
                "T_obs": (
                    str(s["T_obs"]) if s.get("T_obs") is not None else ""
                ),
                "returns_per_bar_path": s.get("returns_per_bar_path") or "",
                "returns_per_bar_sha256": s.get("returns_per_bar_sha256") or "",
            })
```

The behavior on legacy callers (where `gamma3` / `gamma4` / `T_obs` / `returns_per_bar_path` / `returns_per_bar_sha256` are absent from `summary` dict): the `.get(..., None)` calls return None → emitted as empty string in CSV (matches existing pattern for `holdout_passed` None handling).

- [ ] **Step 10.8: Wire `_archive_canonical_pre_flight` + `_finalize_batch_registry_preflight_or_raise` + `_finalize_batch_registry` into `main()`**

Edit `scripts/run_phase2c_evaluation_gate.py` `main()` function (lines 864-1072). 4 wiring points:

**Wiring point 1: pass new args from CLI to local vars (after argparse at line 881).** No code change needed — `args.enable_b_c_narrow_recovery` and `args.force_rerun_existing` are auto-bound by argparse to the dest attributes (`enable_b_c_narrow_recovery` and `force_rerun_existing` per `--enable-b-c-narrow-recovery` / `--force-rerun-existing` standard dash-to-underscore conversion).

**Wiring point 2: archive PRE-flight (after `_check_overwrite_protection` at line 929; before `if args.dry_run:` at line 933).** Insert:

```python
    # B-C-narrow Phase 2 PRE-flight chain (gated by --enable-b-c-narrow-recovery):
    # (1) Archive canonical phase4_forward_2026_15bps_v1/ to archive/...d0b8101/ via shutil.move.
    # (2) Idempotency guard: refuse if parent_run_id exists OR DELETE if --force-rerun-existing.
    if args.enable_b_c_narrow_recovery:
        canonical_phase4_path = Path(args.output_root).resolve() / "phase4_forward_2026_15bps_v1"
        archive_root = Path(args.output_root).resolve() / "archive"
        # archive_basename uses the original artifact's current_git_sha "d0b8101"
        # (spec §2 Q3 lock). DO NOT recompute from current HEAD.
        _archive_canonical_pre_flight(
            canonical_path=canonical_phase4_path,
            archive_root=archive_root,
            archive_basename="phase4_forward_2026_15bps_v1_d0b8101",
        )
        # parent_run_id for B-C-narrow recovery is the --run-id arg verbatim (the
        # operator passes --run-id phase4_forward_2026_15bps_v1_b_c_narrow per Phase 3 T13).
        # db_path=None → get_connection's default; co-locates parent with engine-written
        # children (engine uses the same default inside _write_to_registry).
        _finalize_batch_registry_preflight_or_raise(
            parent_run_id=run_id,
            force_rerun_existing=args.force_rerun_existing,
            db_path=None,
        )
```

**Wiring point 3: thread `artifact_dir_root` + `parent_run_id_override` to `_evaluate_one_candidate` (loop at lines 975-991).** Modify the call site:

```python
    for i, candidate in enumerate(selected, start=1):
        logger.info(
            "[%d/%d] evaluating %s ...",
            i, len(selected), candidate["hypothesis_hash"][:8],
        )
        s = _evaluate_one_candidate(
            candidate=candidate,
            head_sha=head_sha,
            source_batch_id=args.source_batch_id,
            run_id=run_id,
            output_dir=run_dir,
            regime_key=args.regime_key,
            execution_config_path=args.execution_config,
            env_config_override=env_config_override,
            # B-C-narrow Phase 2 LC-b kwargs (None on legacy callers preserves backward-compat):
            artifact_dir_root=(run_dir if args.enable_b_c_narrow_recovery else None),
            parent_run_id_override=(run_id if args.enable_b_c_narrow_recovery else None),
        )
        summaries.append(s)
```

**Wiring point 4: `_finalize_batch_registry` POST-fire (after CSV write at line 996; before aggregate JSON write at line 1053).** Insert:

```python
    # B-C-narrow Phase 2 POST-fire chain (gated by --enable-b-c-narrow-recovery):
    # Write the parent batch_summary row. Children (39 rows) already written by engine
    # per-candidate inside run_regime_holdout's _write_to_registry call (Phase 0).
    if args.enable_b_c_narrow_recovery:
        # Derive cohort metadata from forward_window_metadata + execution_config probe.
        # parquet_data_sha256 comes from forward_window_metadata (captured at fire-time;
        # exists for forward_2026 regime per scripts:957).
        if forward_window_metadata is None:
            raise RuntimeError(
                "B-C-narrow finalize: forward_window_metadata missing. "
                "B-C-narrow recovery requires --regime-key evaluation_regimes.forward_2026 "
                "(per spec §1 cohort_a scope)."
            )
        cohort_metadata = {
            "execution_config_path": _exec_cfg_path_relative,
            "execution_config_sha256": hashlib.sha256(_exec_cfg_bytes).hexdigest(),
            "parquet_data_sha256": forward_window_metadata["parquet_data_sha256"],
            "regime_key": args.regime_key,
            # cost_anchor_id locked to phase4_forward_15bps_v1 per spec §2 Q5
            # (B-C-narrow uses phase4_forward_15bps_v1 anchor; Tier 5/6 promotion
            # uses spot_realistic_15bps_v1 anchor at SEPARATE successor cycle).
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "current_git_sha": head_sha,
            "effective_start": forward_window_metadata["forward_window_start_utc"],
            "initial_capital": 100000.0,  # canonical default per BacktestResult.initial_capital
            "fee_model": "phase4_15bps_v1",
        }
        _finalize_batch_registry(
            parent_run_id=run_id,
            cohort_metadata=cohort_metadata,
            db_path=None,  # get_connection default; co-locates with engine-written children
        )
        logger.info(
            "[B-C-narrow] _finalize_batch_registry: parent batch_summary row written at "
            "run_id=%s with cohort metadata (%d fields)",
            run_id, len(cohort_metadata),
        )
```

**IMPORTANT subtle point:** `_exec_cfg_path_relative`, `_exec_cfg_bytes`, and `hashlib` are computed at scripts:1016-1034 (currently AFTER `_write_aggregate_csv` and AFTER `_aggregate_summary_dict`). The POST-fire `_finalize_batch_registry` block must run AFTER that computation. Place the POST-fire block BETWEEN scripts:1034 (last hashlib computation) and scripts:1053 (aggregate JSON write), or equivalently AFTER scripts:1051 (the `aggregate["forward_window_metadata"] = ...` line). Use that placement.

**Re-validate the placement:**

```bash
grep -n "_exec_cfg_bytes\|aggregate\['forward_window_metadata'\]\|_write_aggregate_summary" scripts/run_phase2c_evaluation_gate.py | head -10
```

Expected: `_exec_cfg_bytes` defined around line 1023; `aggregate["forward_window_metadata"]` around 1051; `_write_aggregate_summary` call around 1053. Place `_finalize_batch_registry` POST-fire block between lines 1051 and 1053.

- [ ] **Step 10.9: Run all 14 Phase 2 tests — must PASS (GREEN)**

```bash
python -m pytest tests/test_phase2c_evaluation_gate_runner.py::TestBCNarrowPhase2ProducerEdits -v
```

Expected: 14/14 PASS.

If any test FAILS, inspect — likely culprits:
- import error in producer (Step 10.1 missed an import)
- typo in CLI flag dest names (Step 10.2; argparse converts `--enable-b-c-narrow-recovery` → `enable_b_c_narrow_recovery` and `--force-rerun-existing` → `force_rerun_existing`)
- `_finalize_batch_registry` raising on missing `cohort_metadata` key — check the required_keys set vs test fixture
- `_evaluate_one_candidate` merge block not running (verify `lcb_active` gate)

- [ ] **Step 10.10: Full test suite zero-regression**

```bash
python -m pytest -q
```

Expected: zero regression vs pre-Phase-2 baseline (HEAD `b10ffb2`: 2328 pass / 0 failed / 2 xfailed per Phase 0 SEAL note) + 14 net new passing Phase 2 tests. Total expected: 2342 pass / 0 failed / 2 xfailed (binding contract is zero regression + 14 new passing; the 2342 integer is informational).

The T1.4 `test_4_tuple_matches_locked_values` test (at `tests/test_t1_4_backward_compat.py:490`) may FAIL at this step because the AST classifier now sees additional test/scripts-side `_write_to_registry` callers (if any added). Task 11 handles T1.4 baseline maintenance — if T1.4 fails at Step 10.10, proceed to Step 10.11 (commit Task 10) WITHOUT fixing T1.4 here. Task 11 commit closes the T1.4 baseline gap atomically.

- [ ] **Step 10.11: Commit producer edits**

```bash
git add scripts/run_phase2c_evaluation_gate.py
git commit -m "feat(b-c-narrow/phase-2): implement producer edits with --enable-b-c-narrow-recovery flag (T10)

Per Plan v3-Phase2 Task 10 + spec §3.2 + 4 Codex BLOCKING-carry fixes from Phase 0 plan v2:

- BLOCKING-1 R9 architectural call-order split: PRE-flight (archive + finalize_preflight) BEFORE candidate loop; POST-fire (finalize) AFTER children written by engine
- BLOCKING-3 create_table precondition: _finalize_batch_registry + _finalize_batch_registry_preflight_or_raise call create_table(conn) before insert/query
- BLOCKING-4 _build_argparser reference correction: all tests reference _build_argparser (NOT _parse_args)
- NEW CLI flags: --enable-b-c-narrow-recovery (default False; gates 3 NEW behaviors) + --force-rerun-existing (default False; R9-B-guarded DELETE opt-in)
- NEW _archive_canonical_pre_flight(): shutil.move with refuse-if-exists guard
- NEW _finalize_batch_registry_preflight_or_raise(): refuse-if-exists OR DELETE WHERE parent_run_id
- NEW _finalize_batch_registry(): writes ONLY 1 parent batch_summary row via insert_run; 39 child rows written by engine
- _evaluate_one_candidate: +2 LC-b kwargs (artifact_dir_root, parent_run_id_override); threads 4 LC-b scalars (run_id_override, source_batch_id, parent_run_id_override, artifact_dir) to engine; computes γ3/γ4/T_obs from equity_curve; merges B-C-narrow fields into inline per-candidate JSON write
- _CSV_FIELDS: +5 fields (gamma3, gamma4, T_obs, returns_per_bar_path, returns_per_bar_sha256)
- _write_aggregate_csv: emits 5 new fields with backward-compat None→empty-string pattern
- main(): wires archive PRE-flight + finalize PRE-flight guard + LC-b kwargs threading + finalize POST-fire (all gated by --enable-b-c-narrow-recovery for backward-compat)

Tests: 14/14 Phase 2 tests GREEN. T1.4 baseline maintenance pending Task 11. Full suite zero regression except for expected T1.4 4-tuple drift (Task 11 closes)."
```

---

### Task 11: T1.4 baseline maintenance (BLOCKING-6 AST classifier output)

**Files:**
- Modify: `tests/test_t1_4_backward_compat.py` (lines 84-89 `_B1_LOCKED_4TUPLE` + lines 538-541 `approved_files` if needed)

**BLOCKING-6 discipline:** Phase 0 plan v2 §6.5 said "Plan v1 computes exact via grep". That is METHODOLOGICALLY WRONG per `tests/test_t1_4_backward_compat.py:67-80` §8.1 METHODOLOGY DIVERGENCE NOTE (grep over-counts via `def` + docstrings + comments). Task 11 uses the EXISTING AST classifier `TestT1_4_B1_SignatureBackwardCompat._enumerate_call_sites()` at lines 422-488 to produce the new 4-tuple — NO grep counting anywhere.

- [ ] **Step 11.1: Dry-run the AST classifier to compute observed 4-tuple post-Phase-2 commits**

Use the existing classifier directly (it scans `backtest/`, `tests/`, `scripts/` excluding `test_t1_4_backward_compat.py` self-reference and excluding `EXCLUDED_PATH_FRAGMENTS`):

```bash
python -c "
from tests.test_t1_4_backward_compat import TestT1_4_B1_SignatureBackwardCompat as T
from pathlib import Path
REPO_ROOT = Path('/Users/yutianyang/Documents/GitHub/btc-alpha-pipeline')
call_sites = T._enumerate_call_sites()

prod_count = sum(1 for (p, _, _, _, _) in call_sites if (REPO_ROOT / 'backtest') in p.parents or p.parent == (REPO_ROOT / 'backtest'))
test_count = sum(1 for (p, _, _, _, _) in call_sites if (REPO_ROOT / 'tests') in p.parents or p.parent == (REPO_ROOT / 'tests'))
scripts_count = sum(1 for (p, _, _, _, _) in call_sites if (REPO_ROOT / 'scripts') in p.parents or p.parent == (REPO_ROOT / 'scripts'))
dynamic_count = sum(1 for (_, _, _, dyn, _) in call_sites if dyn)

print(f'prod_count: {prod_count}')
print(f'test_count: {test_count}')
print(f'scripts_count: {scripts_count}')
print(f'dynamic_count: {dynamic_count}')

# Enumerate dynamic call sites for adjudication
dynamic_sites = [(str(p), line) for (p, line, _, dyn, _) in call_sites if dyn]
print()
print('Dynamic call sites:')
for (pp, ll) in dynamic_sites:
    print(f'  {pp}:{ll}')
"
```

Expected output:
- `prod_count`: still 4 (Phase 2 added NO new `_write_to_registry` callers in `backtest/`)
- `test_count`: 49 (Phase 2 added zero direct `_write_to_registry` calls in tests — all 14 new tests use mocking via `unittest.mock.patch` OR call `_evaluate_one_candidate` which internally calls `run_regime_holdout` which internally calls `_write_to_registry`; the AST classifier counts only DIRECT call sites in `tests/`, so test_count stays 49 UNLESS a new test directly invokes `_write_to_registry`)
- `scripts_count`: still 0 (Phase 2's `_finalize_batch_registry` uses `insert_run`, NOT `_write_to_registry`; these are DIFFERENT functions)
- `dynamic_count`: still 23 (Phase 2 tests use `unittest.mock.patch` decorator/context, NOT `_write_to_registry(**args)` dynamic pattern)

**Pre-Task-11 prediction**: 4-tuple `(4, 49, 0, 23)` UNCHANGED. T1.4 `test_4_tuple_matches_locked_values` should still PASS post-Phase-2.

If the observed 4-tuple matches `(4, 49, 0, 23)` exactly → SKIP Step 11.2 (no baseline update needed; just commit a no-op note in Step 11.4 commit body). If it differs → proceed to Step 11.2.

- [ ] **Step 11.2: Update `_B1_LOCKED_4TUPLE` if the AST classifier shows drift**

If Step 11.1 surfaces drift (e.g., a Phase 2 test directly calls `_write_to_registry` against expectation), update `tests/test_t1_4_backward_compat.py` lines 84-89:

```python
_B1_LOCKED_4TUPLE = {
    "prod_count": <observed>,      # B-C-narrow Phase 2 (Task 11): <delta rationale, e.g., "unchanged at 4">
    "test_count": <observed>,      # B-C-narrow Phase 2 (Task 11): <delta rationale, e.g., "49 → 51 per +2 new direct calls in test_X / test_Y">
    "scripts_count": <observed>,   # B-C-narrow Phase 2 (Task 11): <delta rationale, e.g., "unchanged at 0; _finalize_batch_registry uses insert_run not _write_to_registry">
    "dynamic_count": <observed>,   # B-C-narrow Phase 2 (Task 11): <delta rationale, e.g., "unchanged at 23">
}
```

Replace `<observed>` and `<delta rationale>` with the actual values from Step 11.1 output AND inline rationale citing the specific files + lines that contributed to any delta.

- [ ] **Step 11.3: Extend `approved_files` allowlist in `test_dynamic_count_all_in_uniform_pattern_file` if needed**

If `dynamic_count` delta is NON-ZERO AND the new dynamic sites land in a file NOT already in the `approved_files` set at lines 538-541, extend the set:

```python
        approved_files = {
            _REPO_ROOT / "tests" / "test_t1_3_registry_api.py",  # T1.4 SEAL locked
            _REPO_ROOT / "tests" / "test_t1_5_registry_integrity.py",  # T1.5 Charlie B1 2026-05-24
            # B-C-narrow Phase 2 (Task 11) — IF NEW dynamic sites added; else preserve set:
            # _REPO_ROOT / "tests" / "<new_file>.py",  # B-C-narrow Phase 2: <rationale>
        }
```

**Lock**: Phase 2 plan expects NO new dynamic sites (all Phase 2 tests use `unittest.mock.patch`, NOT `_write_to_registry(**args)`). If Step 11.1 surfaces any new dynamic site, that is a Phase 2 plan FAILURE (single-pattern adjudication discipline violated) and should be re-litigated as a Phase 2 plan amend rather than silently widening the allowlist.

- [ ] **Step 11.4: Run T1.4 test class — must PASS**

```bash
python -m pytest tests/test_t1_4_backward_compat.py::TestT1_4_B1_SignatureBackwardCompat -v
```

Expected: all tests in the class PASS.

- [ ] **Step 11.5: Full test suite zero-regression**

```bash
python -m pytest -q
```

Expected: 2342 pass / 0 failed / 2 xfailed (14 net new passing vs pre-Phase-2 baseline). Zero regression.

- [ ] **Step 11.6: Commit T1.4 baseline maintenance (skip if no drift)**

If Step 11.2 was a no-op (4-tuple unchanged), skip the commit and proceed to Task 12. The pre-Task-11 prediction holds; no maintenance needed.

If Step 11.2 updated the 4-tuple:

```bash
git add tests/test_t1_4_backward_compat.py
git commit -m "test(b-c-narrow/phase-2): T1.4 baseline maintenance per AST classifier output (T11; BLOCKING-6 fix)

Per Plan v3-Phase2 Task 11 + BLOCKING-6 carry from Phase 0 plan v2 PFR R2.

AST classifier output post-Phase-2 commits:
- prod_count: <old> → <new> (<rationale>)
- test_count: <old> → <new> (<rationale>)
- scripts_count: <old> → <new> (<rationale>)
- dynamic_count: <old> → <new> (<rationale>)

Methodology: AST classifier at TestT1_4_B1_SignatureBackwardCompat._enumerate_call_sites
(lines 422-488). NO grep counting (BLOCKING-6 fix from Phase 0 plan v2 §6.5
methodological error)."
```

---

### Task 12: Phase 2 final ratify packet

- [ ] **Step 12.1: Confirm 14 tests GREEN + full suite zero regression + T1.4 baseline updated (or unchanged)**

```bash
python -m pytest tests/test_phase2c_evaluation_gate_runner.py::TestBCNarrowPhase2ProducerEdits -v
python -m pytest tests/test_t1_4_backward_compat.py::TestT1_4_B1_SignatureBackwardCompat -v
python -m pytest -q
```

Expected:
- 14/14 Phase 2 tests PASS
- T1.4 B1 class PASSES (4-tuple verified)
- Full suite: 2342 pass / 0 failed / 2 xfailed (zero regression vs `b10ffb2` baseline + 14 net new passing)

- [ ] **Step 12.2: Write Phase 2 ratify packet artifact**

Create `docs/superpowers/phase-2-impl-results/phase-2-ratify-summary.md`:

```markdown
# B-C-narrow Phase 2 ratify packet

**Date:** <ISO UTC>
**HEAD commit:** <git rev-parse --short HEAD>
**Plan version:** v3-Phase2 v1 (or post-PFR iteration count)
**Plan path:** `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-2-producer-tdd-plan.md`
**Spec path:** `docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md` (sealed at `d6c7fc0`)
**Authorization:** Charlie register `EXEC-SUBAGENT-ALL-PHASE-2` <date>

## Pre-execution preconditions

| Precondition | Result | Evidence |
|---|---|---|
| Clean working tree (PFR R2 HIGH-2/NEW-2 fix v3 carryforward) | PASS | `git status --porcelain backtest/ tests/ config/ scripts/ strategies/ factors/` empty |
| Writable execution environment | PASS | `tempfile.NamedTemporaryFile()` succeeded |
| Phase 0 SEAL chain present | PASS | Phase 0 LC-b API verified via import + signature inspection |

## Test results

| Test class | Methods | PASS | FAIL | Status |
|---|---|---|---|---|
| TestBCNarrowPhase2ProducerEdits | 14 | 14 | 0 | GREEN |
| TestT1_4_B1_SignatureBackwardCompat | (existing) | (all) | 0 | GREEN |
| Full suite (b10ffb2 baseline + 14 new) | 2342 | 2342 | 0 (+ 2 xfailed) | zero regression |

## 4 BLOCKING-carry fixes verified

| # | BLOCKING-carry | Status |
|---|---|---|
| BLOCKING-1 | R9 architectural call-order split (PRE-flight + POST-fire halves) | FIXED — verified by `test_finalize_batch_registry_writes_parent_row_only` + `test_archive_step_*` + `test_finalize_batch_registry_*_idempotency` tests |
| BLOCKING-3 | `_finalize_batch_registry` create_table precondition | FIXED — both `_finalize_batch_registry_preflight_or_raise` and `_finalize_batch_registry` call `create_table(conn)` before query/insert |
| BLOCKING-4 | `_parse_args` → `_build_argparser` reference | FIXED — verified by `test_build_argparser_callable_no_parse_args` (asserts `_build_argparser` callable AND `_parse_args` not present) |
| BLOCKING-6 | T1.4 grep methodology → AST classifier | FIXED — Task 11 used AST classifier; 4-tuple `(<final>, <final>, <final>, <final>)` |

## Overall verdict

ALL Phase 2 deliverables GREEN. Phase 2 ratify gate met.

Phase 3 fire (T13 producer run + T14 V4 reproducibility gate + T14b canonical-path relocation) drafting is a SEPARATE register-event (#N+3) per anti-pre-emption discipline; do NOT bundle into #N+2.

## Next register-event (#N+2) — Phase 2 ratify ONLY

Per anti-pre-emption discipline: register-event #N+2 is Phase 2 ratify acknowledgment ONLY. The Phase 3 fire-plan drafting authorization is a SEPARATE register-event #N+3.

- Phase 2 ratify acknowledgment
- Push decision for Phase 2 implementation commits (T9 + T10 + T11)

Phase 3 fire sub-plan drafting is NOT a sub-option of #N+2; it requires its own register-event #N+3.
```

- [ ] **Step 12.3: Commit Phase 2 ratify packet + Charlie register-event #N+2 dispatch**

```bash
git add docs/superpowers/phase-2-impl-results/phase-2-ratify-summary.md
git commit -m "evidence(b-c-narrow/phase-2): Phase 2 ratify packet (T12)

Per Plan v3-Phase2 Task 12.

Phase 2 deliverables: 14/14 TestBCNarrowPhase2ProducerEdits PASS; full suite
zero regression vs b10ffb2 baseline + 14 net new passing. T1.4 baseline
maintained per BLOCKING-6 AST classifier output.

4 BLOCKING-carry fixes from Phase 0 plan v2 PFR R2 all verified:
- BLOCKING-1 R9 architectural call-order split
- BLOCKING-3 create_table precondition
- BLOCKING-4 _parse_args → _build_argparser
- BLOCKING-6 T1.4 grep → AST classifier methodology

Verdict: ALL PASS. Phase 2 ratify gate met; awaiting Charlie register-event
#N+2 for Phase 2 ratify acknowledgment ONLY. Phase 3 fire sub-plan drafting
is a SEPARATE register-event #N+3 per anti-pre-emption discipline."
```

- [ ] **Step 12.4: STOP HERE — Surface to Charlie register-event #N+2**

**STOP.** Surface to Charlie:
- 14 Phase 2 producer-edit tests GREEN
- T1.4 B1 4-tuple unchanged (or updated per AST classifier; whichever applies)
- Full test suite zero regression vs pre-Phase-2 baseline + 14 net new passing
- Producer modifications confined to `scripts/run_phase2c_evaluation_gate.py` (7 modify-zones + 3 NEW functions) + 1 test file extension
- All 4 BLOCKING-carry items from Phase 0 plan v2 PFR R2 verified fixed (BLOCKING-1 + BLOCKING-3 + BLOCKING-4 + BLOCKING-6)

**Do NOT surface Phase 3 fire-plan drafting authorization as a sub-option of #N+2.** Per anti-pre-emption discipline, Phase 3 drafting requires its own register-event #N+3 — fire that as a SEPARATE Charlie message after #N+2 is resolved.

Phase 2 sealed at task level (no Phase Marker advance per [feedback_claude_md_freshness.md] mid-cycle discipline — arc-level closeout reserved for Phase 4 cycle SEAL).

---

## DEFER items (Phase 2 scope only)

**Phase-2-internal:** NONE. All 4 BLOCKING-carry items from Phase 0 plan v2 PFR R2 (BLOCKING-1 + BLOCKING-3 + BLOCKING-4 + BLOCKING-6) addressed inline in Tasks 10-11.

**Phase 3+ blockers DEFERRED** to respective sub-plans per spec §5 enumeration:

- **Phase 3** (T12 archive operator command + T13 producer fire + T14 V4 reproducibility gate + T14b canonical-path relocation): 39-candidate cohort_a re-run with `parquet_data_sha256` populated + per-bar artifacts + γ3/γ4 moments + V4 reproducibility gate (ε=1e-6). Drafting requires Charlie register-event #N+3 after Phase 2 ratify.
- **Phase 4** (T15 NOTE doc + T16 SEAL bundle + Phase Marker advance per Option 1A atomic): B-C-narrow data-recovery cycle SEAL artifact + arc-level closeout. Drafting requires Charlie register-event #N+4 after Phase 3 SEAL.
- **BLOCKING-5 G4-G7 test bodies** (per Codex R2 Phase 0 plan v2 finding): G4 per-bar parquet integrity + G5 γ3/γ4 round-trip + G6 registry parent-child integrity + G7 archive idempotency. All 4 gates are POST-impl gates that fire at Phase 3 (per spec §4.3). Bodies inlined in Plan v3-Phase3 (not Phase 2 scope).

Each sub-plan requires separate Charlie register-event for drafting authorization per anti-pre-emption discipline.

---

## Execution Handoff

Plan v3-Phase2 v1 saved to `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-2-producer-tdd-plan.md`.

After Plan v3-Phase2 B2 2-leg PFR returns APPROVE (or APPROVE-WITH-FINDINGS at LOW-only floor) → use **superpowers:subagent-driven-development** per Charlie register PV3-SPLIT-BY-PHASE: dispatch fresh subagent per task (T9 → T10 → T11 → T12) with two-stage review OR orchestrator-manual execution per Charlie register-event-by-register-event.

After Phase 2 SEALED (Task 12 ratify) → request Charlie register-event for Plan v3-Phase3 sub-plan drafting authorization (separate fire — anti-pre-emption discipline preserved).
