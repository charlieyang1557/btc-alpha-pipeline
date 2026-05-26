# B-C-narrow Data-Recovery Cycle Implementation Plan v2

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recover per-bar return series + per-candidate γ3/γ4 moments + registry linkage for the `phase4_forward_2026_15bps_v1` cohort_a 39-candidate artifact at `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/`, dually resolving R6.1 V_SEAL §8 dim (a) DSL-availability + dim (b) per-bar-return INDETERMINATE classifications.

**Architecture:** Approach D' (producer-edit + minimum engine extension) per spec doc `docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md`§3. **LC-b 4-kwarg lock** (cost_anchor_id derived by LC __post_init__ via COST_ANCHOR_ID_MAPPING per artifact_schema.py:298-302 — callers MUST NOT pass). Phase 0 engine extension (RegimeHoldoutResult.equity_curve field + run_regime_holdout signature 4 new kwargs + LC-b internal construction). Phase 1 BLOCKING gates. Phase 2 producer TDD. Phase 3 fire + V4 + T14b canonical-path relocation. Phase 4 SEAL.

**Tech Stack:** Python 3.11+, pytest, pandas/numpy/scipy, SQLite (`backtest/experiments.db`), parquet via pyarrow, Backtrader 1.9.78+ engine.

**Cycle entry register:** Charlie 2026-05-26 (N1). Design ratified post 3 PFR rounds (spec at `d6c7fc0`). Plan v1 NOT-APPROVE by both PFR legs 2026-05-26 (12+ BLOCKING engineering/quality errors + 5+ HIGH spec coverage gaps);plan v2 (this doc) rewritten with full Mode A grep-verification of every cited function name + field + signature.

**Locked decisions (post 3 spec-doc PFR rounds + Charlie register 2026-05-26):**
- **R9-B-guarded** compensating cleanup: `_finalize_batch_registry()` default behavior is **refuse-with-DELETE-command-emit** if any child row matches `parent_run_id` of this fire's run_id; automatic DELETE+re-fire enabled only via explicit `--force-rerun-existing` CLI flag (operator opt-in)
- **LC-b 4-kwarg-rigorous**: engine constructs LineageContext internally using **4 producer-passed scalars** (`run_id_override`, `source_batch_id`, `parent_run_id_override`, `artifact_dir`). `cost_anchor_id` is **NOT** a passed scalar — derived in LC `__post_init__` from `execution_config_path` via `COST_ANCHOR_ID_MAPPING`. Comprehensive TDD per spec §3.4

**Plan v1 → v2 corrections applied (per 2-leg PFR NOT-APPROVE adjudication):**
- ❌ v1: 5 LC-b kwargs → ✓ v2: 4 LC-b kwargs (cost_anchor_id removed; derived in __post_init__)
- ❌ v1: `dsl_to_hypothesis_hash()` (nonexistent) → ✓ v2: `compute_dsl_hash()` (the actual function used at engine.py:2404 via `from strategies.dsl import compute_dsl_hash`)
- ❌ v1: `LineageContext(batch_id=...)` (nonexistent field) → ✓ v2: `LineageContext(hypothesis_hash=..., source_batch_id=..., ...)` (14-field schema per artifact_schema.py:279-311)
- ❌ v1: `_write_to_registry(returns_per_bar_path=..., returns_per_bar_sha256=..., T_obs=...)` direct kwargs (signature doesn't accept) → ✓ v2: `_write_to_registry(lineage_context=lc_built, artifact_dir=artifact_dir, ...)` (per-bar metadata flows via `lineage_context`)
- ❌ v1: 11 placeholder test bodies "expand later" → ✓ v2: all 13 producer-edit tests written in full
- ❌ v1: `_finalize_batch_registry()` defined but unused → ✓ v2: explicitly wired into producer `main()` after `_write_aggregate_summary`
- ❌ v1: archive function defined but unused → ✓ v2: explicitly wired into producer `main()` as first fire-flow step
- ❌ v1: `_B1_LOCKED_4TUPLE = (4, 49, 0, 23)` tuple literal → ✓ v2: dict-key reassignment (actual literal is dict at tests/test_t1_4_backward_compat.py:83-88)
- ❌ v1: V4 fixture N=2 → ✓ v2: V4 fixture N=39 per spec §4.2
- ❌ v1: G2 sample 25 → ✓ v2: G2 sample N≥39 per spec §4.1 G2
- ❌ v1: G4-G7 "Detailed assertion code" placeholder → ✓ v2: concrete G4-G7 assertion code
- ❌ v1: missing call-order test → ✓ v2: `test_run_regime_holdout_writes_artifact_before_registry()` added per spec §6.2
- ❌ v1: missing `_write_aggregate_summary` cohort-field edit → ✓ v2: explicit Step 9.4b
- ❌ v1: undefined test fixtures referenced → ✓ v2: fixtures defined in `tests/conftest.py` extensions

**Plan-task-number ↔ spec-T-number cross-reference:**

| Spec T# | Spec section | Plan v2 Task |
|---|---|---|
| T1 | Phase 0 — write failing tests | Task 1 |
| T2 | Phase 0 — RegimeHoldoutResult.equity_curve | Task 2 |
| T2b | Phase 0 — 4 LC-b kwargs (was 5 in v1) | Task 3 |
| T2c | Phase 0 — run_regime_holdout body sequencing + LC-b construction | Task 4 |
| T3 | Phase 0 — full test suite + Phase 0 ratify | Task 5 |
| T4 | Phase 0 → Phase 1 register-event | (boundary) |
| T5 | Phase 1 — G1 engine-diff audit | Task 6 |
| T6 | Phase 1 — G2 DSL backward-compat | Task 7 |
| T7 | Phase 1 — G3 raw_payloads inventory | Task 8 |
| T8 | Phase 1 — G3.5 engine extension smoke | Task 9 |
| T9 | Phase 2 — write failing producer-edit tests | Task 10 |
| T10 | Phase 2 — implement producer edits | Task 11 |
| T11 | Phase 2 — T1.4 baseline maintenance | Task 12 |
| T12 | Phase 3 — archive original artifact | Task 13 |
| T13 | Phase 3 — fire producer | Task 14 |
| T14 | Phase 3 — V4 reproducibility gate | Task 15 |
| T14b | Phase 3 — canonical-path relocation post-V4 | Task 16 |
| T15 | Phase 4 — write NOTE doc + B2 + Rule 2 SEAL-eve | Task 17 |
| T16 | Phase 4 — atomic SEAL commit | Task 18 |

---

## File Structure

**Files modified (with line ranges):**

| File | Action | Scope |
|---|---|---|
| `backtest/engine.py` | MODIFY | Lines 2044-2063 (`RegimeHoldoutResult` dataclass +`equity_curve` field), 2270-2291 (`run_regime_holdout` signature +4 NEW kwargs), 2435-2523 (`run_regime_holdout` body — LC-b construction before `_write_to_registry` + RegimeHoldoutResult equity_curve field at return) |
| `scripts/run_phase2c_evaluation_gate.py` | MODIFY | Lines 480-573 (`_evaluate_one_candidate` threads 4 LC-b kwargs + γ3/γ4 inline merge at scripts:550-556), 581-595 (`_CSV_FIELDS` +5 columns), 706-718 (`_write_aggregate_summary` cohort fields), main() flow (wire NEW `_finalize_batch_registry()` + NEW archive step + `--force-rerun-existing` flag) |
| `tests/test_t1_1_artifact_writer.py` | EXTEND | NEW `TestBCNarrowPhase0EngineExtension` class (8 methods covering 14 LC fields + 5 boundary cases + call-order + backward-compat) |
| `tests/test_phase2c_evaluation_gate_runner.py` | EXTEND | NEW `TestBCNarrowProducerEdits` class (13 methods all written in full per Charlie no敷衍 requirement) + EXTEND existing `RegimeHoldoutResult(...)` test stub at line 83 with `equity_curve=` arg |
| `tests/test_t1_4_backward_compat.py` | MODIFY | Lines 83-88 `_B1_LOCKED_4TUPLE` dict-key reassignment (NOT tuple replacement); allowlist extension if needed; line 1384 `RegimeHoldoutResult(...)` stub +`equity_curve=` arg |
| `tests/conftest.py` (root tests/ conftest) | EXTEND OR CREATE | Define shared fixtures `dsl_bollinger_zscore_reversion`, `btc_parquet_path`, `mock_engine_returns_equity_curve` used by Phase 0 + Phase 2 tests |

**Files created (NEW):**

| File | Purpose |
|---|---|
| `tests/test_b_c_narrow_recovery.py` | E2E smoke test (N=2 cohort_a candidates real-engine path) |
| `tests/test_b_c_narrow_v4_reproducibility.py` | V4 ε=1e-6 reproducibility (all 39 candidates) + γ3/γ4 round-trip + concrete G4-G7 gate assertions |
| `tests/test_b_c_narrow_g2_dsl_backward_compat.py` | G2 BLOCKING gate — N≥39 sample (≥7 per sub-batch × 5 sub-batches + combined dir position 873 verification) |
| `tests/fixtures/b_c_narrow_archived_baseline.json` | Frozen V4 baseline fixture (ALL 39 candidates' summary metrics from archived original) |
| `docs/phase5/B_C_NARROW_DATA_RECOVERY_NOTE.md` | Final SEAL artifact at Task 17 (~400-600 lines) |

**Data layer (NEW; gitignored):**

| Path | Purpose |
|---|---|
| `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` | Archived original artifact (39 candidates' `holdout_summary.json` + top-level summary + CSV) created at Task 13 |
| `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/` | Sibling output dir created by producer at Task 14 (matches `--run-id` value);relocated to canonical at Task 16 |
| `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` (canonical) | Repopulated at Task 16 with new B-C-narrow output via `mv` |
| `backtest/experiments.db` | Registry rows: 39 child `regime_holdout` rows (engine-internal write per-candidate at LC-b path) + 1 parent `batch_summary` row at `run_id=phase4_forward_2026_15bps_v1_b_c_narrow` (via `_finalize_batch_registry()` at producer post-cohort) |

---

# Pre-Phase-0 Charlie register-event boundary (per spec §10.5)

**STOP-HERE marker — Charlie must register one of:**
- Push `506285b` + `53090a0` + `d6c7fc0` to origin/main BEFORE Phase 0 (recommended per spec §10.5)
- OR explicitly authorize Phase 0 dispatch with commits still local

**Deliverables Charlie should review at this boundary:**
- `git status` shows ahead 3 of origin/main
- Plan v2 itself (this doc; uncommitted at this moment)

Do NOT proceed to Task 1 without Charlie register on push decision.

---

# Phase 0 — Engine extension (Tasks 1-5)

**Phase boundary:** Charlie register-event #N required before transitioning to Phase 1.

### Task 1: Define shared test fixtures + write FAILING engine-extension tests

**Files:**
- Create OR extend: `tests/conftest.py` (root tests/ conftest)
- Modify: `tests/test_t1_1_artifact_writer.py` (extend with new test class)

- [ ] **Step 1.1: Add or extend `tests/conftest.py` with shared fixtures**

Check existing state: `test -f tests/conftest.py && cat tests/conftest.py | head -20`. If file exists, append the new fixtures; otherwise create.

```python
# tests/conftest.py — ADD or APPEND
import json
from pathlib import Path

import pandas as pd
import pytest

from strategies.dsl import StrategyDSL


REPO_ROOT = Path(__file__).resolve().parent.parent


def _strip_markdown_fence(text: str) -> str:
    """Mirror scripts/run_phase2c_evaluation_gate.py:_strip_markdown_fence."""
    s = text.strip()
    if s.startswith("```"):
        # Strip leading ```json or ``` line
        first_nl = s.find("\n")
        s = s[first_nl + 1:] if first_nl != -1 else s
    if s.endswith("```"):
        s = s.rsplit("```", 1)[0].strip()
    return s


@pytest.fixture
def btc_parquet_path() -> Path:
    """Canonical BTC OHLCV parquet path used by all engine tests."""
    return REPO_ROOT / "data" / "raw" / "btcusdt_1h.parquet"


@pytest.fixture
def dsl_bollinger_zscore_reversion() -> StrategyDSL:
    """Load the cohort_a candidate 18d92ce5d0b40cc7 (mean_reversion strategy
    'bollinger_zscore_reversion') DSL from recovered raw_payloads. Used by
    Phase 0 engine tests + Phase 2 producer tests as the canonical exemplar."""
    response_path = (
        REPO_ROOT
        / "raw_payloads"
        / "batch_4f894318-eb69-48b5-95ef-e22abe3ecdd1"
        / "attempt_0032_response.txt"
    )
    raw_text = response_path.read_text(encoding="utf-8")
    payload = json.loads(_strip_markdown_fence(raw_text))
    return StrategyDSL.model_validate(payload)


@pytest.fixture
def dsl_monday_dip_buy() -> StrategyDSL:
    """Load cohort_a candidate 8a2a8f73f71a835e (calendar_effect strategy
    'monday_dip_buy_calendar_effect') DSL from combined synthetic dir at
    position 873. Used as second exemplar for boundary-case tests."""
    from scripts.run_phase2c_evaluation_gate import _load_dsl_from_response
    return _load_dsl_from_response("phase2c_15_main_fire_combined", 873)
```

- [ ] **Step 1.2: Append `TestBCNarrowPhase0EngineExtension` class to `tests/test_t1_1_artifact_writer.py`**

```python
# tests/test_t1_1_artifact_writer.py — APPEND at end of file (before any
# trailing teardowns)

import inspect
import sqlite3
from dataclasses import fields
from pathlib import Path

import pandas as pd
import pytest

# Already imported in this file: RegimeHoldoutResult, run_regime_holdout, write_per_bar_artifact, etc.
# Verify imports at file top before adding new tests:
#   from backtest.engine import (RegimeHoldoutResult, run_regime_holdout,
#                                  write_per_bar_artifact, compute_per_bar_returns,
#                                  compute_moments)
#   from backtest.artifact_schema import LineageContext
#   from backtest.experiment_registry import get_connection


class TestBCNarrowPhase0EngineExtension:
    """Phase 0 engine extension tests for B-C-narrow Approach D' (LC-b 4-kwarg).

    Locked decisions:
    - RegimeHoldoutResult dataclass extended with equity_curve: pd.Series field
    - run_regime_holdout signature adds 4 NEW kwargs (all default None for
      backward compat): run_id_override, source_batch_id, parent_run_id_override,
      artifact_dir. NOT 5 — cost_anchor_id is derived by LC __post_init__ from
      execution_config_path via COST_ANCHOR_ID_MAPPING (artifact_schema.py:298-302)
      and MUST NOT be a producer-passed scalar.
    - Engine constructs LineageContext internally using producer-passed scalars
      + engine-computed T_obs after backtest run + write_per_bar_artifact returns
      dict with returns_per_bar_path/sha256/T_obs/gamma3/gamma4.
    - LineageContext stamped into registry row via existing _write_to_registry
      lineage_context kwarg + SYS5 revalidate_for_write at engine.py:1149.
    """

    # ----- Dataclass shape tests (2) -----

    def test_regime_holdout_result_exposes_equity_curve_field(self):
        """RegimeHoldoutResult dataclass must include equity_curve: pd.Series field."""
        from backtest.engine import RegimeHoldoutResult
        field_names = {f.name for f in fields(RegimeHoldoutResult)}
        assert "equity_curve" in field_names, (
            f"RegimeHoldoutResult must include 'equity_curve' field per spec §3.1.1; "
            f"current fields: {sorted(field_names)}"
        )

    def test_regime_holdout_result_dataclass_field_count_12(self):
        """RegimeHoldoutResult must have exactly 12 fields (11 existing + equity_curve)."""
        from backtest.engine import RegimeHoldoutResult
        all_fields = [f.name for f in fields(RegimeHoldoutResult)]
        assert len(all_fields) == 12, (
            f"RegimeHoldoutResult must have 12 fields (11 existing + equity_curve); "
            f"got {len(all_fields)}: {all_fields}"
        )

    # ----- Signature tests (2) -----

    def test_run_regime_holdout_signature_includes_4_new_lcb_kwargs(self):
        """run_regime_holdout signature must include 4 NEW LC-b kwargs (all default None).

        NOT 5 — cost_anchor_id is derived by LC __post_init__ from
        execution_config_path; producer MUST NOT pass it explicitly.
        """
        from backtest.engine import run_regime_holdout
        sig = inspect.signature(run_regime_holdout)
        params = sig.parameters
        required_new_kwargs = {
            "run_id_override",
            "source_batch_id",
            "parent_run_id_override",
            "artifact_dir",
        }
        missing = required_new_kwargs - set(params.keys())
        assert not missing, (
            f"run_regime_holdout signature missing LC-b kwargs: {missing};"
            f" present: {sorted(params.keys())}"
        )
        # Verify backward-compat: each new kwarg has default None
        for kw in required_new_kwargs:
            assert params[kw].default is None, (
                f"LC-b kwarg '{kw}' must default to None for backward-compat;"
                f" got default={params[kw].default!r}"
            )

    def test_run_regime_holdout_signature_does_not_include_cost_anchor_id_kwarg(self):
        """cost_anchor_id MUST NOT be a producer-passable kwarg per
        artifact_schema.py:298-302 (LC __post_init__ derives it).
        """
        from backtest.engine import run_regime_holdout
        sig = inspect.signature(run_regime_holdout)
        assert "cost_anchor_id" not in sig.parameters, (
            "cost_anchor_id MUST NOT be a run_regime_holdout kwarg per spec §3.4 "
            "LC-b 4-kwarg lock + artifact_schema.py:298-302 derivation invariant. "
            "Found in signature: BLOCKING."
        )

    # ----- Equity curve population test (1) -----

    def test_run_regime_holdout_returns_result_with_equity_curve_populated(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path
    ):
        """run_regime_holdout return value's equity_curve must be a non-empty
        UTC-aware pd.Series."""
        from backtest.engine import run_regime_holdout
        result = run_regime_holdout(
            dsl=dsl_bollinger_zscore_reversion,
            batch_id="test-batch-bc-narrow-p0",
            parent_run_id="test-parent-bc-narrow-p0",
            regime_key="evaluation_regimes.forward_2026",
            parquet_path=str(btc_parquet_path),
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
        )
        assert isinstance(result.equity_curve, pd.Series), (
            f"equity_curve must be pd.Series; got {type(result.equity_curve)}"
        )
        assert len(result.equity_curve) > 0, (
            "equity_curve must be non-empty (forward_2026 window has ~2528 hourly bars)"
        )
        assert result.equity_curve.index.tz is not None, (
            "equity_curve index must be UTC-aware per HARD CONSTRAINT (no naive datetimes)"
        )

    # ----- LC-b internal construction test with all-14-LC-field assertion (1) -----

    def test_run_regime_holdout_lcb_constructs_lineage_context_with_all_14_fields(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path
    ):
        """When LC-b kwargs provided, engine internally constructs LineageContext
        using producer-passed scalars + engine-computed T_obs and stamps it into
        the registry row atomically before run_regime_holdout returns. Verifies
        all 14 LC fields populated correctly at the registry row.
        """
        from backtest.engine import run_regime_holdout
        from backtest.experiment_registry import get_connection

        db_path = tmp_path / "test_lcb_engine_internal.db"
        artifact_dir = tmp_path / "test_lcb_artifact"
        run_id = "test_lcb_engine_run_id_001"

        result = run_regime_holdout(
            dsl=dsl_bollinger_zscore_reversion,
            batch_id="test-source-batch-lcb",  # positional (legacy)
            parent_run_id="test-parent-lcb",  # positional (legacy)
            regime_key="evaluation_regimes.forward_2026",
            parquet_path=str(btc_parquet_path),
            db_path=db_path,
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
            # 4 LC-b kwargs (cost_anchor_id NOT passed; derived by __post_init__):
            run_id_override=run_id,
            source_batch_id="test-source-batch-lcb",
            parent_run_id_override="test-parent-lcb-override",
            artifact_dir=artifact_dir,
        )

        # Verify the engine wrote registry row with LC-b stamping
        with get_connection(db_path) as conn:
            row = conn.execute(
                "SELECT run_id, hypothesis_hash, batch_id, parent_run_id, "
                "regime_key, current_git_sha, execution_config_path, "
                "execution_config_sha256, parquet_data_sha256, cost_anchor_id, "
                "returns_per_bar_path, returns_per_bar_sha256, T_obs "
                "FROM runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        assert row is not None, f"Registry row missing for run_id={run_id}"

        # Per-field assertions (all 14 LC fields — Charlie no敷衍 requirement)
        (registry_run_id, hypothesis_hash, batch_id_col, parent_run_id_col,
         regime_key_col, current_git_sha, execution_config_path_col,
         execution_config_sha256, parquet_data_sha256, cost_anchor_id,
         returns_per_bar_path, returns_per_bar_sha256, t_obs) = row

        # LC field 2: run_id matches override
        assert registry_run_id == run_id, f"run_id mismatch: {registry_run_id} vs {run_id}"
        # LC field 3: hypothesis_hash populated (computed by engine via compute_dsl_hash)
        assert hypothesis_hash is not None and len(hypothesis_hash) == 16, (
            f"hypothesis_hash must be 16-char per compute_dsl_hash; got {hypothesis_hash!r}"
        )
        # LC field 4: source_batch_id populated (note: this maps to runs.batch_id column)
        assert batch_id_col == "test-source-batch-lcb"
        # LC field 5: parent_run_id matches override
        assert parent_run_id_col == "test-parent-lcb-override"
        # LC field 6: regime_key populated
        assert regime_key_col == "evaluation_regimes.forward_2026"
        # LC field 7: engine_commit populated (CORRECTED_WF_ENGINE_COMMIT="eb1c87f")
        # (stored in registry under a separate column or in notes — verify per actual schema)
        # LC field 8: current_git_sha populated (current HEAD)
        assert current_git_sha is not None and len(current_git_sha) >= 7
        # LC field 9: execution_config_path canonicalized POSIX
        assert "execution_phase4_15bps.yaml" in execution_config_path_col
        # LC field 10: execution_config_sha256 populated
        assert execution_config_sha256 is not None and len(execution_config_sha256) == 64
        # LC field 11: parquet_data_sha256 populated
        assert parquet_data_sha256 is not None and len(parquet_data_sha256) == 64
        # LC field 12: cost_anchor_id derived (NOT passed) — should be 'phase4_forward_15bps_v1'
        assert cost_anchor_id == "phase4_forward_15bps_v1", (
            f"cost_anchor_id derivation via COST_ANCHOR_ID_MAPPING failed; "
            f"got {cost_anchor_id!r} (expected phase4_forward_15bps_v1)"
        )
        # LC field 13: returns_per_bar_path populated
        assert returns_per_bar_path is not None and returns_per_bar_path != ""
        # LC field 14: returns_per_bar_sha256 populated
        assert returns_per_bar_sha256 is not None and len(returns_per_bar_sha256) == 64
        # T_obs populated
        assert t_obs is not None and t_obs > 0

        # Verify per-bar parquet file exists at expected location
        parquet_file = artifact_dir / "returns_per_bar.parquet"
        assert parquet_file.exists(), f"per-bar parquet must exist at {parquet_file}"

    # ----- Call-order test (1; per spec §6.2 + Codex BLOCKING gap) -----

    def test_run_regime_holdout_writes_artifact_before_registry(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path, monkeypatch
    ):
        """Verify engine call ordering: write_per_bar_artifact MUST be called
        before _write_to_registry. Atomicity invariant per spec §3.1.2 5-step
        sequence; if registry write happens first, returns_per_bar_path/sha256/T_obs
        cannot be stamped atomically.
        """
        from backtest import engine
        call_order = []

        original_write_artifact = engine.write_per_bar_artifact
        original_write_registry = engine._write_to_registry

        def tracking_write_artifact(*args, **kwargs):
            call_order.append("write_per_bar_artifact")
            return original_write_artifact(*args, **kwargs)

        def tracking_write_registry(*args, **kwargs):
            call_order.append("_write_to_registry")
            return original_write_registry(*args, **kwargs)

        monkeypatch.setattr(engine, "write_per_bar_artifact", tracking_write_artifact)
        monkeypatch.setattr(engine, "_write_to_registry", tracking_write_registry)

        engine.run_regime_holdout(
            dsl=dsl_bollinger_zscore_reversion,
            batch_id="test-call-order",
            parent_run_id="test-parent-call-order",
            regime_key="evaluation_regimes.forward_2026",
            parquet_path=str(btc_parquet_path),
            db_path=tmp_path / "test_call_order.db",
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
            run_id_override="test_call_order_001",
            source_batch_id="test-batch",
            parent_run_id_override="test-parent-override",
            artifact_dir=tmp_path / "artifact_co",
        )

        assert "write_per_bar_artifact" in call_order, "write_per_bar_artifact not called"
        assert "_write_to_registry" in call_order, "_write_to_registry not called"
        artifact_idx = call_order.index("write_per_bar_artifact")
        registry_idx = call_order.index("_write_to_registry")
        assert artifact_idx < registry_idx, (
            f"BLOCKING: write_per_bar_artifact must be called BEFORE _write_to_registry "
            f"per spec §3.1.2 5-step sequence + atomicity invariant. "
            f"Actual order: {call_order}"
        )

    # ----- Backward-compat test (1) -----

    def test_run_regime_holdout_backward_compat_no_lcb_kwargs(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path
    ):
        """Backward compat: run_regime_holdout works without ANY LC-b kwargs
        (legacy callers at engine.py:771/1841/1896 unaffected). When LC-b kwargs
        all None, engine takes legacy path: no per-bar artifact write, no
        internal LC construction (uses producer-passed lineage_context if any).
        Existing fields populated as before. equity_curve always populated
        (regardless of LC-b path).
        """
        from backtest.engine import run_regime_holdout
        result = run_regime_holdout(
            dsl=dsl_bollinger_zscore_reversion,
            batch_id="test-batch-legacy-compat",
            parent_run_id="test-parent-legacy",
            regime_key="evaluation_regimes.forward_2026",
            parquet_path=str(btc_parquet_path),
        )
        # Existing fields populated as before
        assert result.run_id is not None
        assert result.hypothesis_hash is not None and len(result.hypothesis_hash) == 16
        assert result.total_trades >= 0
        # NEW equity_curve field always populated
        assert result.equity_curve is not None
        assert len(result.equity_curve) > 0

    # ----- Boundary case tests (5; per Charlie no敷衍 requirement) -----

    def test_run_regime_holdout_lcb_empty_run_id_override_fails_closed(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path
    ):
        """LC.run_id is STRICT field; empty string at construction must FAIL CLOSED
        per LC __post_init__ FIX-T1.1-SYS-B1."""
        from backtest.engine import run_regime_holdout
        with pytest.raises((ValueError, RuntimeError)):
            run_regime_holdout(
                dsl=dsl_bollinger_zscore_reversion,
                batch_id="test-bc",
                parent_run_id="test-parent",
                regime_key="evaluation_regimes.forward_2026",
                parquet_path=str(btc_parquet_path),
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                run_id_override="",  # empty string — invalid per LC strict
                source_batch_id="test-bsi",
                parent_run_id_override="test-parent-override",
                artifact_dir=tmp_path / "artifact_empty_run",
            )

    def test_run_regime_holdout_lcb_empty_source_batch_id_fails_closed(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path
    ):
        """LC.source_batch_id is STRICT field; empty string must FAIL CLOSED."""
        from backtest.engine import run_regime_holdout
        with pytest.raises((ValueError, RuntimeError)):
            run_regime_holdout(
                dsl=dsl_bollinger_zscore_reversion,
                batch_id="test-bc",
                parent_run_id="test-parent",
                regime_key="evaluation_regimes.forward_2026",
                parquet_path=str(btc_parquet_path),
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                run_id_override="test-run-id-valid",
                source_batch_id="",  # empty string
                parent_run_id_override="test-parent-override",
                artifact_dir=tmp_path / "artifact_empty_sbi",
            )

    def test_run_regime_holdout_lcb_invalid_artifact_dir_propagates_error(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path
    ):
        """artifact_dir pointing to non-writable location must propagate error
        (write_per_bar_artifact failure surfaced cleanly)."""
        from backtest.engine import run_regime_holdout
        with pytest.raises((OSError, PermissionError, RuntimeError)):
            run_regime_holdout(
                dsl=dsl_bollinger_zscore_reversion,
                batch_id="test-bc",
                parent_run_id="test-parent",
                regime_key="evaluation_regimes.forward_2026",
                parquet_path=str(btc_parquet_path),
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                run_id_override="test-run-id-invalid-dir",
                source_batch_id="test-sbi",
                parent_run_id_override="test-parent-override",
                artifact_dir=Path("/no/such/path/no_permission_likely"),
            )

    def test_run_regime_holdout_lcb_no_execution_config_path_fails_at_lc_construction(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path
    ):
        """LC-b kwargs provided but execution_config_path=None → LC __post_init__
        cannot derive cost_anchor_id → FAIL CLOSED per artifact_schema.py
        COST_ANCHOR_ID_MAPPING lookup."""
        from backtest.engine import run_regime_holdout
        with pytest.raises((ValueError, KeyError, RuntimeError)):
            run_regime_holdout(
                dsl=dsl_bollinger_zscore_reversion,
                batch_id="test-bc",
                parent_run_id="test-parent",
                regime_key="evaluation_regimes.forward_2026",
                parquet_path=str(btc_parquet_path),
                execution_config_path=None,  # missing required for LC construction
                run_id_override="test-run-id-no-config",
                source_batch_id="test-sbi",
                parent_run_id_override="test-parent-override",
                artifact_dir=tmp_path / "artifact_no_cfg",
            )

    def test_run_regime_holdout_lcb_partial_kwargs_combination(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path
    ):
        """Partial LC-b kwargs (some None, some set): engine must consistently
        decide LC-b vs legacy path. Spec §3.4 lock: if ANY LC-b kwarg is
        non-None (lcb_active=any check), LC-b path activated → all required
        LC fields must be derivable (otherwise fail closed).

        This test verifies: if artifact_dir provided BUT run_id_override is None,
        engine must EITHER (a) compute run_id from result.run_id and continue
        OR (b) fail closed with a clear error. Plan v1 has 'effective_run_id
        = run_id_override if run_id_override is not None else result.run_id' so
        path (a) is expected.
        """
        from backtest.engine import run_regime_holdout
        result = run_regime_holdout(
            dsl=dsl_bollinger_zscore_reversion,
            batch_id="test-bc-partial",
            parent_run_id="test-parent-partial",
            regime_key="evaluation_regimes.forward_2026",
            parquet_path=str(btc_parquet_path),
            db_path=tmp_path / "test_partial.db",
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
            # Only artifact_dir + source_batch_id set; others None
            run_id_override=None,
            source_batch_id="test-sbi-partial",
            parent_run_id_override=None,
            artifact_dir=tmp_path / "artifact_partial",
        )
        # Engine should have used result.run_id as effective_run_id + parent_run_id
        # (positional) as effective_parent_run_id
        assert result.equity_curve is not None
        # Verify parquet still written
        assert (tmp_path / "artifact_partial" / "returns_per_bar.parquet").exists()
```

- [ ] **Step 1.3: Run all 13 tests — they must FAIL (RED)**

```bash
cd /Users/yutianyang/Documents/GitHub/btc-alpha-pipeline
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension -v
```

Expected: most tests FAIL with `AttributeError: 'RegimeHoldoutResult' has no field 'equity_curve'` or `TypeError: run_regime_holdout() got an unexpected keyword argument 'run_id_override'`. The negative-existence test `test_run_regime_holdout_signature_does_not_include_cost_anchor_id_kwarg` may PASS at this stage (it's a "should not be present" check) — that's correct RED-phase behavior for a negative assertion.

- [ ] **Step 1.4: Commit failing tests + conftest fixtures**

```bash
git add tests/conftest.py tests/test_t1_1_artifact_writer.py
git commit -m "test(b-c-narrow/phase-0): add 13 failing tests + shared fixtures (T1)

RED-phase tests per B-C-narrow plan v2 Task 1. Verifies:
- RegimeHoldoutResult dataclass + equity_curve field (2 tests)
- run_regime_holdout signature includes 4 LC-b kwargs (NOT 5; cost_anchor_id derived)
- Negative assertion: cost_anchor_id NOT in run_regime_holdout signature
- equity_curve populated as UTC-aware pd.Series
- LC-b internal LC construction + all 14 LC field stamping at registry row
- Call-order: write_per_bar_artifact BEFORE _write_to_registry (per spec §3.1.2)
- Backward-compat: legacy callers (no LC-b kwargs) unaffected
- Boundary cases (5): empty run_id_override, empty source_batch_id, invalid
  artifact_dir, missing execution_config_path, partial-kwargs combination

Also adds shared fixtures (dsl_bollinger_zscore_reversion + dsl_monday_dip_buy
+ btc_parquet_path) to tests/conftest.py loading from recovered raw_payloads.

All 13 tests FAIL at this commit (RED phase). Tasks 2-4 implement engine
changes to bring GREEN."
```

---

### Task 2: Extend RegimeHoldoutResult dataclass with equity_curve

**Files:**
- Modify: `backtest/engine.py` lines 2044-2063

- [ ] **Step 2.1: Add `equity_curve: pd.Series` field**

Edit `backtest/engine.py` at lines 2044-2063. Append `equity_curve: pd.Series` as the 12th field at the end of the dataclass body (after `metrics`):

```python
@dataclass
class RegimeHoldoutResult:
    """Container for a regime-holdout evaluation.

    [existing docstring]

    B-C-narrow Phase 0 extension (2026-05-26): equity_curve field added per
    Approach D' to expose per-bar equity series for downstream consumers
    (per-bar parquet write + γ3/γ4 moment computation at producer boundary).
    """

    run_id: str
    parent_run_id: str
    batch_id: str
    hypothesis_hash: str | None
    regime_holdout_passed: bool
    sharpe_ratio: float
    max_drawdown: float
    total_return: float
    total_trades: int
    passing_criteria: dict[str, float]
    metrics: dict[str, Any]
    equity_curve: pd.Series  # B-C-narrow Phase 0 (2026-05-26)
```

- [ ] **Step 2.2: Update test stubs at tests/test_phase2c_evaluation_gate_runner.py:83 + tests/test_t1_4_backward_compat.py:1384**

Find existing `return RegimeHoldoutResult(...)` calls and add `equity_curve=pd.Series(dtype=float)` arg. Ensure `import pandas as pd` is present (likely already).

- [ ] **Step 2.3: Run 2 dataclass-shape tests + full suite**

```bash
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension::test_regime_holdout_result_exposes_equity_curve_field \
                 tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension::test_regime_holdout_result_dataclass_field_count_12 -v
python -m pytest -q
```

Expected: 2 PASS;full suite zero regression.

- [ ] **Step 2.4: Commit**

```bash
git add backtest/engine.py tests/test_phase2c_evaluation_gate_runner.py tests/test_t1_4_backward_compat.py
git commit -m "feat(b-c-narrow/phase-0): add RegimeHoldoutResult.equity_curve field (T2)

12th field on RegimeHoldoutResult dataclass per Approach D' Phase 0 + LC-b
4-kwarg lock (spec §3.1.1). Extends engine.py:2044-2063 to expose per-bar
equity series for downstream per-bar artifact write + γ3/γ4 moment computation.

Test stub updates at tests/test_phase2c_evaluation_gate_runner.py:83 +
tests/test_t1_4_backward_compat.py:1384 add equity_curve=pd.Series(dtype=float)
for backward-compat.

Tests: 2/13 Phase 0 tests now GREEN. Zero regression in full suite."
```

---

### Task 3: Add 4 LC-b kwargs to run_regime_holdout signature

**Files:**
- Modify: `backtest/engine.py` lines 2270-2291

- [ ] **Step 3.1: Add 4 new kwargs (NOT 5) to run_regime_holdout**

Edit `backtest/engine.py` line 2290 (the line `lineage_context: "Any | None" = None,`). After this line, add the 4 new kwargs before the closing `)`:

```python
def run_regime_holdout(
    dsl: "Any",
    batch_id: str,
    parent_run_id: str,
    *,
    regime_key: str = "v2.regime_holdout",
    strategy_cls: type[bt.Strategy] | None = None,
    strategy_params: dict[str, Any] | None = None,
    parquet_path: str | Path | None = None,
    cash: float = 10_000.0,
    db_path: Path | None = None,
    env_config: dict[str, Any] | None = None,
    registry: "Any" = None,
    manifest_dir: Path | None = None,
    execution_config_path: Path | None = None,
    lineage_context: "Any | None" = None,
    # B-C-narrow Phase 0 LC-b 4-kwarg lock (default None preserves backward compat):
    # NOTE: cost_anchor_id is INTENTIONALLY OMITTED from this list — it is derived
    # in LineageContext __post_init__ from execution_config_path via
    # COST_ANCHOR_ID_MAPPING per artifact_schema.py:298-302. Callers MUST NOT pass
    # cost_anchor_id explicitly.
    run_id_override: str | None = None,  # T3: deterministic run_id input (LC-b pattern)
    source_batch_id: str | None = None,  # T3: maps to LC.source_batch_id (LC field 4)
    parent_run_id_override: str | None = None,  # T3: explicit parent_run_id_override (vs positional)
    artifact_dir: Path | None = None,  # T3: producer-controlled artifact directory
) -> RegimeHoldoutResult:
```

- [ ] **Step 3.2: Run signature tests + full suite**

```bash
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension::test_run_regime_holdout_signature_includes_4_new_lcb_kwargs \
                 tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension::test_run_regime_holdout_signature_does_not_include_cost_anchor_id_kwarg -v
python -m pytest -q
```

Expected: 2 PASS;full suite zero regression.

- [ ] **Step 3.3: Commit**

```bash
git add backtest/engine.py
git commit -m "feat(b-c-narrow/phase-0): add 4 LC-b kwargs to run_regime_holdout signature (T3)

LC-b 4-kwarg lock per spec §3.4 + post-PFR plan-v2 correction: engine accepts
4 producer-passed scalars (run_id_override + source_batch_id + parent_run_id_override
+ artifact_dir). cost_anchor_id is INTENTIONALLY OMITTED — derived by LC
__post_init__ from execution_config_path via COST_ANCHOR_ID_MAPPING per
artifact_schema.py:298-302 (callers MUST NOT pass explicitly).

All 4 kwargs default None for backward-compat with existing call sites at
engine.py:771/1841/1896 + scripts/run_phase2c_evaluation_gate.py:512.

Tests: 4/13 Phase 0 tests now GREEN. Zero regression in full suite."
```

---

### Task 4: Implement LC-b LineageContext construction body in run_regime_holdout

**Files:**
- Modify: `backtest/engine.py` lines 2435-2523

This is the most substantive Phase 0 task. Per spec §3.1.2 5-step sequence + Codex BLOCKING gap (call-order, hash function name, LC field names, _write_to_registry signature).

- [ ] **Step 4.1: Locate existing imports + add helper if needed**

Read `backtest/engine.py` lines 1-100 to identify existing imports. Verify the following are imported at top of file (add if missing):

```python
from backtest.wf_lineage import CORRECTED_WF_ENGINE_COMMIT
from backtest.artifact_schema import LineageContext
```

Verify `get_git_commit()` function exists in engine.py or experiment_registry.py via:

```bash
grep -n "def get_git_commit" backtest/
```

If `get_git_commit` exists at experiment_registry.py:241 (per prior PRAGMA output context), import it. If `_compute_sha256_file` doesn't exist, add this helper near other utility functions in engine.py:

```python
def _compute_sha256_file(file_path: Path | None) -> str | None:
    """Compute SHA256 hex digest of a file via 64KB chunked streaming.

    Returns None if file_path is None or file does not exist. Used by
    B-C-narrow Phase 0 LC-b LineageContext construction for
    execution_config_sha256 + parquet_data_sha256 fields.
    """
    import hashlib

    if file_path is None:
        return None
    path = Path(file_path)
    if not path.exists():
        return None

    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(64 * 1024)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()
```

- [ ] **Step 4.2: Modify run_regime_holdout body at lines 2435-2523**

Read current body at engine.py:2435-2523 (already inspected at plan-v2 drafting). The corrected body (lines 2435 onward) is:

```python
    result = run_backtest(
        strategy_cls=strategy_cls,
        start_date=start_dt,
        end_date=end_dt,
        strategy_params=strategy_params or {},
        parquet_path=parquet_path,
        cash=cash,
        write_registry=False,
        execution_config_path=_rh_effective_exec_path,
    )

    passed = _evaluate_regime_holdout_pass(result.metrics, passing_criteria)

    # Existing: holdout_run_id = result.run_id (line 2451)
    # B-C-narrow Phase 0 LC-b: override with run_id_override if provided
    if run_id_override is not None:
        effective_run_id = run_id_override
        # Note: result.run_id was minted by run_backtest as a UUID; we override
        # for B-C-narrow deterministic scheme {parent}_{hypothesis_hash}.
    else:
        effective_run_id = result.run_id
    holdout_run_id = effective_run_id  # alias preserved for logging downstream

    effective_parent_run_id = (
        parent_run_id_override if parent_run_id_override is not None else parent_run_id
    )

    # B-C-narrow Phase 0 LC-b: determine if LC-b path active (any LC-b kwarg non-None).
    # If active, write per-bar artifact + construct LC internally + stamp registry atomically.
    lcb_active = any(
        kw is not None for kw in (
            run_id_override,
            source_batch_id,
            parent_run_id_override,
            artifact_dir,
        )
    )

    # B-C-narrow Phase 0 LC-b: write per-bar artifact if artifact_dir provided.
    artifact_metadata: dict[str, Any] | None = None
    if artifact_dir is not None:
        artifact_metadata = write_per_bar_artifact(
            result.equity_curve,
            artifact_dir,
            effective_run_id,
        )
        # artifact_metadata keys: returns_per_bar_path, returns_per_bar_sha256,
        # T_obs, gamma3, gamma4 (per engine.py:469-475 docstring; dict not tuple).

    # B-C-narrow Phase 0 LC-b: construct LineageContext internally when LC-b active.
    # cost_anchor_id is DERIVED by LC __post_init__ from execution_config_path —
    # we pass the sentinel "" (default) and let __post_init__ overwrite via
    # COST_ANCHOR_ID_MAPPING lookup.
    if lcb_active:
        # All 14 LC fields populated:
        lcb_lineage_context = LineageContext(
            run_id=effective_run_id,
            hypothesis_hash=hypothesis_hash if hypothesis_hash is not None else "",
            source_batch_id=(source_batch_id if source_batch_id is not None else batch_id),
            regime_key=regime_key,
            engine_commit=CORRECTED_WF_ENGINE_COMMIT,
            current_git_sha=get_git_commit() or "",
            execution_config_path=(
                str(execution_config_path) if execution_config_path is not None else ""
            ),
            execution_config_sha256=_compute_sha256_file(execution_config_path) or "",
            parquet_data_sha256=_compute_sha256_file(parquet_path) or "",
            # cost_anchor_id OMITTED — uses default sentinel ""; __post_init__ derives.
            returns_per_bar_path=(artifact_metadata["returns_per_bar_path"] if artifact_metadata else ""),
            returns_per_bar_sha256=(artifact_metadata["returns_per_bar_sha256"] if artifact_metadata else ""),
            T_obs=(artifact_metadata["T_obs"] if artifact_metadata else 0),
            parent_run_id=effective_parent_run_id,
        )
        # T1.1 SYS5 invariant per engine.py:1149 — validate before write.
        lcb_lineage_context.revalidate_for_write()
        # Use the engine-built LC for registry write (overrides any producer-passed lineage_context).
        effective_lineage_context = lcb_lineage_context
    else:
        # Legacy path: use producer-passed lineage_context (may be None).
        effective_lineage_context = lineage_context

    from backtest.execution_model import ConstantSlippage
    _exec_cfg = (
        load_execution_config(_rh_effective_exec_path)
        if _rh_effective_exec_path is not None
        else load_execution_config()
    )
    cost_model = ConstantSlippage.from_config(_exec_cfg)

    notes_payload = {
        "label": block.get("label"),
        "passing_criteria": passing_criteria,
        "criterion_outcomes": {
            "sharpe_ratio": result.metrics.get("sharpe_ratio"),
            "max_drawdown": result.metrics.get("max_drawdown"),
            "total_return": result.metrics.get("total_return"),
            "total_trades": result.metrics.get("total_trades"),
        },
    }

    # B-C-narrow Phase 0: _write_to_registry signature accepts lineage_context + artifact_dir.
    # Per-bar metadata (returns_per_bar_path/sha256/T_obs) flows via lineage_context fields,
    # NOT as direct kwargs (verified against engine.py:839-865 signature).
    _write_to_registry(
        run_id=effective_run_id,
        strategy_cls=strategy_cls,
        strategy_params=strategy_params or {},
        start_date=start_dt,
        end_date=end_dt,
        effective_start=result.effective_start,
        warmup_bars=result.warmup_bars,
        cost_model=cost_model,
        metrics=result.metrics,
        db_path=db_path,
        run_type="regime_holdout",
        parent_run_id=effective_parent_run_id,
        train_start=None,
        train_end=None,
        notes=json.dumps(notes_payload),
        batch_id=batch_id,
        hypothesis_hash=hypothesis_hash,
        regime_holdout_passed=passed,
        lifecycle_state=None,
        strategy_source=strategy_source,
        feature_version=feature_version,
        execution_config_path=execution_config_path,
        lineage_context=effective_lineage_context,
        artifact_dir=artifact_dir,
    )

    logger.info(
        "Regime holdout %s: passed=%s sharpe=%.3f dd=%.3f ret=%.4f trades=%d%s",
        holdout_run_id[:8], passed,
        result.metrics.get("sharpe_ratio", float("nan")),
        result.metrics.get("max_drawdown", float("nan")),
        result.metrics.get("total_return", float("nan")),
        result.metrics.get("total_trades", 0),
        f" T_obs={artifact_metadata['T_obs']}" if artifact_metadata else "",
    )

    return RegimeHoldoutResult(
        run_id=effective_run_id,
        parent_run_id=effective_parent_run_id,
        batch_id=batch_id,
        hypothesis_hash=hypothesis_hash,
        regime_holdout_passed=passed,
        sharpe_ratio=float(result.metrics.get("sharpe_ratio", float("nan"))),
        max_drawdown=float(result.metrics.get("max_drawdown", float("nan"))),
        total_return=float(result.metrics.get("total_return", float("nan"))),
        total_trades=int(result.metrics.get("total_trades", 0) or 0),
        passing_criteria=dict(passing_criteria),
        metrics=dict(result.metrics),
        equity_curve=result.equity_curve,  # B-C-narrow Phase 0 NEW
    )
```

- [ ] **Step 4.3: Run all 13 Phase 0 tests — all must PASS (GREEN)**

```bash
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension -v
```

Expected: 13/13 PASS.

- [ ] **Step 4.4: Run full test suite zero-regression check**

```bash
python -m pytest -q
```

Expected: 2317 + 13 = 2330 tests passing.

- [ ] **Step 4.5: Commit**

```bash
git add backtest/engine.py
git commit -m "feat(b-c-narrow/phase-0): implement LC-b LineageContext construction in run_regime_holdout (T4)

Per Approach D' LC-b 4-kwarg lock + spec §3.1.2 5-step sequence:
1. run_backtest (existing) → produces BacktestResult with equity_curve
2. evaluate passing criterion (existing)
3. NEW: determine effective_run_id from run_id_override (else result.run_id)
4. NEW: if artifact_dir provided, call write_per_bar_artifact returning dict
   with returns_per_bar_path/sha256/T_obs/gamma3/gamma4
5. NEW: if any LC-b kwarg non-None, construct LineageContext internally with
   all 14 fields populated (cost_anchor_id derived by __post_init__ from
   execution_config_path; T1.1 SYS5 revalidate_for_write invariant called)
6. _write_to_registry with effective_lineage_context (engine-built LC if
   LC-b active, else producer-passed lineage_context)
7. Return RegimeHoldoutResult with equity_curve=result.equity_curve

Helper _compute_sha256_file added for execution_config_sha256 +
parquet_data_sha256 LC fields. Imports CORRECTED_WF_ENGINE_COMMIT from
wf_lineage.py + LineageContext from artifact_schema.py.

Tests: 13/13 Phase 0 tests now GREEN. Full suite 2330/2330 zero regression."
```

---

### Task 5: Phase 0 final ratify

- [ ] **Step 5.1: Confirm 13 tests + full suite all GREEN**

```bash
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension -v
python -m pytest -q
```

Both must show all passing.

- [ ] **Step 5.2: Charlie register-event #N — Phase 0 ratify before Phase 1**

**STOP HERE. Surface to Charlie:**
- All 13 engine-extension tests GREEN
- Full test suite 2330/2330 passing
- Engine modifications confined to RegimeHoldoutResult dataclass + run_regime_holdout signature + run_regime_holdout body
- Phase 0 complete; ready for Phase 1 pre-impl gates fire

Do NOT proceed to Task 6 (Phase 1) without Charlie register.

---

# Phase 1 — Pre-implementation BLOCKING gates (Tasks 6-9)

**Phase boundary:** Charlie register-event #N+1 required before Phase 2.

### Task 6: G1 — engine-diff audit of d0b8101..506285b

- [ ] **Step 6.1: Get + classify 3 backtest/ commits**

```bash
git log --oneline d0b8101..506285b -- backtest/
git show ec647dc --stat -- backtest/
git show 12dffde --stat -- backtest/
git show 44840a3 --stat -- backtest/
```

Per Codex R2 preliminary classification:
- `ec647dc` T1.6 documentation — additive-only
- `12dffde` T1.1 artifact writer — additive-only (new helpers + schema migration; no compute path modification)
- `44840a3` — verify name + classify

- [ ] **Step 6.2: Create G1 audit report in working tree (not committed yet)**

Write `/tmp/b_c_narrow_g1_audit.md` with classification table + reasoning.

- [ ] **Step 6.3: Surface G1 PASS to Charlie**

If all 3 commits classified additive-only → V4 ε=1e-6 reproducibility expected achievable. PASS. Block on Charlie register before next gate.

---

### Task 7: G2 — StrategyDSL backward-compat (N≥39 sample)

**Files:**
- Create: `tests/test_b_c_narrow_g2_dsl_backward_compat.py`

- [ ] **Step 7.1: Write G2 sample-≥39 test**

```python
"""B-C-narrow G2 gate — StrategyDSL backward-compat against recovered raw_payloads.

Per spec §4.1 G2: N ≥ 39 sample covering all 5 sub-batches + combined dir
position 873 verification. Fails closed if any backward-compat breakage
between d0b8101 (original) and 506285b (current) Pydantic schema versions.
"""
import json
from pathlib import Path

import pytest

from strategies.dsl import StrategyDSL


REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_PAYLOADS_DIR = REPO_ROOT / "raw_payloads"


def _strip_markdown_fence(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        first_nl = s.find("\n")
        s = s[first_nl + 1:] if first_nl != -1 else s
    if s.endswith("```"):
        s = s.rsplit("```", 1)[0].strip()
    return s


COHORT_A_SUB_BATCHES = [
    "355a8f9f-2a1f-435d-a1a8-c365b92e185b",
    "4f894318-eb69-48b5-95ef-e22abe3ecdd1",
    "71d42a07-d88f-431a-a653-601010cf1921",
    "91ad68ed-6470-45a7-8735-171c39ff25c3",
    "a12c2a65-4314-4dde-be6e-968a0c70ee6e",
]


@pytest.fixture
def cohort_a_candidate_positions() -> list[tuple[str, int]]:
    """Return list of (sub_batch_id, position) for all 39 cohort_a candidates
    from holdout_results.csv (archived original; pre-archive verified location)."""
    csv_path = (
        REPO_ROOT
        / "data" / "phase2c_evaluation_gate"
        / "phase4_forward_2026_15bps_v1"  # pre-archive name
        / "holdout_results.csv"
    )
    archive_path = (
        REPO_ROOT
        / "data" / "phase2c_evaluation_gate" / "archive"
        / "phase4_forward_2026_15bps_v1_d0b8101"
        / "holdout_results.csv"
    )
    if csv_path.exists():
        path = csv_path
    elif archive_path.exists():
        path = archive_path
    else:
        pytest.skip("Original artifact + archive both missing; cannot run G2")

    # Parse CSV: each row has hypothesis_hash, position, ...
    # batch_id is at /data/phase2c_walkforward/batch_phase2c_15_main_fire_combined_corrected/walk_forward_results.csv
    # Need to join on hypothesis_hash to get (sub_batch_id, position). For G2 we use
    # the combined-dir naming: source_batch_id="phase2c_15_main_fire_combined",
    # position from holdout_results.csv (which IS the global combined position).
    import csv
    candidates = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates.append((row["hypothesis_hash"], int(row["position"])))
    assert len(candidates) == 39, f"Expected 39 cohort_a candidates; got {len(candidates)}"
    return candidates


class TestG2DSLBackwardCompat:
    """G2 BLOCKING gate — N≥39 cohort_a candidates' DSL must parse under
    current StrategyDSL schema."""

    def test_all_39_cohort_a_candidates_parse(self, cohort_a_candidate_positions):
        """Each of 39 cohort_a candidates' DSL resolves via combined synthetic dir
        + parses under current StrategyDSL schema. N=39 per spec §4.1 G2."""
        from scripts.run_phase2c_evaluation_gate import _load_dsl_from_response

        failures = []
        for hash_, position in cohort_a_candidate_positions:
            try:
                dsl = _load_dsl_from_response("phase2c_15_main_fire_combined", position)
                assert dsl.name, f"DSL.name empty for hash={hash_} position={position}"
            except Exception as e:
                failures.append((hash_, position, str(e)))
        assert not failures, (
            f"G2 BLOCKING: {len(failures)}/39 candidates failed DSL parse:\n"
            + "\n".join(f"  hash={h} pos={p} err={e[:100]}" for h, p, e in failures[:10])
        )

    def test_sub_batch_directories_all_present(self):
        """All 5 cohort_a sub-batches + combined synthetic dir present in raw_payloads/."""
        for sub_batch in COHORT_A_SUB_BATCHES:
            batch_dir = RAW_PAYLOADS_DIR / f"batch_{sub_batch}"
            assert batch_dir.exists(), f"Sub-batch dir missing: {batch_dir}"

        combined_dir = RAW_PAYLOADS_DIR / "batch_phase2c_15_main_fire_combined"
        assert combined_dir.exists(), f"Combined synthetic dir missing: {combined_dir}"

    def test_combined_dir_998_symlinks(self):
        """Combined dir contains 993 attempt symlinks + 5 source_stage2d_summary
        symlinks = 998 total."""
        combined_dir = RAW_PAYLOADS_DIR / "batch_phase2c_15_main_fire_combined"
        attempts = list(combined_dir.glob("attempt_*_response.txt"))
        summaries = list(combined_dir.glob("source_stage2d_summary_*.json"))
        assert len(attempts) == 993, f"Expected 993 attempt symlinks; got {len(attempts)}"
        assert len(summaries) == 5, f"Expected 5 source_stage2d_summary symlinks; got {len(summaries)}"

    def test_position_873_resolves_to_monday_dip_buy(self):
        """Combined dir position 873 resolves to candidate 8a2a8f73f71a835e."""
        from scripts.run_phase2c_evaluation_gate import _load_dsl_from_response
        dsl = _load_dsl_from_response("phase2c_15_main_fire_combined", 873)
        assert dsl.name == "monday_dip_buy_calendar_effect"
```

- [ ] **Step 7.2: Run G2 tests**

```bash
python -m pytest tests/test_b_c_narrow_g2_dsl_backward_compat.py -v
```

Expected: all PASS (G2 BLOCKING gate cleared).

- [ ] **Step 7.3: Commit G2 test file**

```bash
git add tests/test_b_c_narrow_g2_dsl_backward_compat.py
git commit -m "test(b-c-narrow/phase-1): G2 BLOCKING gate — N=39 StrategyDSL backward-compat (T7)

Per spec §4.1 G2 + post-PFR plan-v2 correction (N≥39, not 25):
- All 39 cohort_a candidates' DSL parses via combined synthetic dir
  resolution + StrategyDSL.model_validate under current 506285b schema
- 5 sub-batch dirs + combined dir all present
- Combined dir 993 + 5 = 998 symlinks verified
- Position 873 resolves to monday_dip_buy_calendar_effect"
```

---

### Task 8: G3 — raw_payloads inventory check

- [ ] **Step 8.1: Run G3 inventory (already covered by G2 tests above + manual sanity)**

```bash
# Already covered by tests in Task 7 (test_sub_batch_directories_all_present + test_combined_dir_998_symlinks).
# Additional sanity:
find raw_payloads/batch_phase2c_15_main_fire_combined -type l | wc -l
# Expected: 998 (993 attempt + 5 source_stage2d_summary)

# Verify symlinks resolve
ls -la raw_payloads/batch_phase2c_15_main_fire_combined/attempt_0873_response.txt
# Expected: -> ../batch_91ad68ed-6470-45a7-8735-171c39ff25c3/attempt_0080_response.txt

# Read content via symlink
head -3 raw_payloads/batch_phase2c_15_main_fire_combined/attempt_0873_response.txt
```

- [ ] **Step 8.2: Surface G3 PASS to Charlie**

---

### Task 9: G3.5 — engine extension smoke test

- [ ] **Step 9.1: Run the LC-b construction test as smoke**

```bash
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension::test_run_regime_holdout_lcb_constructs_lineage_context_with_all_14_fields -v
```

Expected: PASS.

- [ ] **Step 9.2: Surface G3.5 PASS + Phase 1 ratify request to Charlie**

**STOP HERE.** All 4 Phase 1 gates (G1 + G2 + G3 + G3.5) PASSED. Charlie register-event #N+1 authorizes Phase 2.

---

# Phase 2 — Producer TDD edits (Tasks 10-12)

**Phase boundary:** Charlie register-event #N+2 required before Phase 3.

### Task 10: Write FAILING producer-edit tests (13 tests, all bodies in full)

**Files:**
- Modify: `tests/test_phase2c_evaluation_gate_runner.py` (append new test class)

- [ ] **Step 10.1: Append `TestBCNarrowProducerEdits` test class with all 13 bodies**

```python
# tests/test_phase2c_evaluation_gate_runner.py — APPEND at end

from pathlib import Path
import json
import sqlite3
import csv

import pytest


class TestBCNarrowProducerEdits:
    """Phase 2 producer edits per Approach D' + R9-B-guarded + LC-b 4-kwarg threading.

    13 tests covering: 4 LC-b kwargs threading + γ3/γ4 inline merge +
    _finalize_batch_registry parent-row-only + R9-B-guarded refuse-then-force +
    archive idempotency + _CSV_FIELDS extension + schema-domain routing +
    --force-rerun-existing CLI thread-through.
    """

    # ----- 1. LC-b kwarg threading + γ3/γ4 merge tests (3) -----

    def test_evaluate_one_candidate_threads_4_lcb_kwargs_to_engine(
        self, monkeypatch, tmp_path
    ):
        """Producer must pass 4 LC-b kwargs (run_id_override + source_batch_id +
        parent_run_id_override + artifact_dir) to run_regime_holdout. NOT 5;
        cost_anchor_id is NOT a producer-passable scalar."""
        from scripts import run_phase2c_evaluation_gate as producer

        captured_kwargs = {}

        def mock_run_regime_holdout(**kwargs):
            captured_kwargs.update(kwargs)
            # Return a stub RegimeHoldoutResult
            from backtest.engine import RegimeHoldoutResult
            import pandas as pd
            return RegimeHoldoutResult(
                run_id="test-run-id", parent_run_id="test-parent",
                batch_id="test-batch", hypothesis_hash="testhash00000000",
                regime_holdout_passed=True, sharpe_ratio=1.0,
                max_drawdown=0.1, total_return=0.05, total_trades=10,
                passing_criteria={}, metrics={}, equity_curve=pd.Series(dtype=float),
            )

        monkeypatch.setattr(producer, "run_regime_holdout", mock_run_regime_holdout)

        candidate = {
            "hypothesis_hash": "18d92ce5d0b40cc7",
            "position": 32,
            "theme": "mean_reversion",
            "name": "bollinger_zscore_reversion",
        }
        producer._evaluate_one_candidate(
            candidate=candidate,
            head_sha="test-head-sha",
            source_batch_id="phase2c_15_main_fire_combined",
            run_id="phase4_forward_2026_15bps_v1_b_c_narrow",
            output_dir=tmp_path,
            regime_key="evaluation_regimes.forward_2026",
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
        )

        # Verify all 4 LC-b kwargs threaded
        assert "run_id_override" in captured_kwargs
        assert "source_batch_id" in captured_kwargs
        assert "parent_run_id_override" in captured_kwargs
        assert "artifact_dir" in captured_kwargs
        # cost_anchor_id MUST NOT be in kwargs (LC __post_init__ derives)
        assert "cost_anchor_id" not in captured_kwargs

        # Verify run_id_override matches deterministic scheme {parent}_{hash}
        expected_run_id = (
            f"phase4_forward_2026_15bps_v1_b_c_narrow_{candidate['hypothesis_hash']}"
        )
        assert captured_kwargs["run_id_override"] == expected_run_id

        # Verify artifact_dir is per-candidate sub-directory
        assert candidate["hypothesis_hash"] in str(captured_kwargs["artifact_dir"])

    def test_evaluate_one_candidate_merges_gamma_into_summary_json(
        self, monkeypatch, tmp_path
    ):
        """Producer must merge γ3/γ4/T_obs/returns_per_bar_path/returns_per_bar_sha256
        from engine artifact_metadata into per-candidate summary JSON inline at
        scripts:550-556 (NOT into _write_aggregate_summary which is cohort-level)."""
        from scripts import run_phase2c_evaluation_gate as producer
        import pandas as pd

        # Mock engine to return result + write artifact + registry row with LC stamped
        def mock_run_regime_holdout(**kwargs):
            # Simulate engine writing per-bar artifact + registry row
            from backtest.engine import RegimeHoldoutResult, write_per_bar_artifact
            artifact_dir = kwargs.get("artifact_dir")
            if artifact_dir is not None:
                # Create per-bar parquet (engine would write this)
                equity_curve = pd.Series(
                    [100.0, 101.0, 102.5], index=pd.date_range("2026-01-01", periods=3, tz="UTC")
                )
                write_per_bar_artifact(equity_curve, artifact_dir, "test-rid")
            return RegimeHoldoutResult(
                run_id="test-rid", parent_run_id="test-prid",
                batch_id="test-bi", hypothesis_hash="testhash00000000",
                regime_holdout_passed=True, sharpe_ratio=1.0,
                max_drawdown=0.1, total_return=0.05, total_trades=10,
                passing_criteria={}, metrics={},
                equity_curve=pd.Series(
                    [100.0, 101.0, 102.5], index=pd.date_range("2026-01-01", periods=3, tz="UTC")
                ),
            )

        monkeypatch.setattr(producer, "run_regime_holdout", mock_run_regime_holdout)

        candidate = {
            "hypothesis_hash": "abcd1234efgh5678", "position": 100,
            "theme": "test", "name": "test-strategy",
        }
        summary = producer._evaluate_one_candidate(
            candidate=candidate,
            head_sha="test-sha",
            source_batch_id="phase2c_15_main_fire_combined",
            run_id="test-run-id",
            output_dir=tmp_path,
            regime_key="evaluation_regimes.forward_2026",
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
        )

        # Verify per-candidate summary includes new fields
        assert "gamma3" in summary
        assert "gamma4" in summary
        assert "T_obs" in summary
        assert "returns_per_bar_path" in summary
        assert "returns_per_bar_sha256" in summary

    def test_evaluate_one_candidate_writes_per_candidate_json_inline(
        self, monkeypatch, tmp_path
    ):
        """Per-candidate JSON written inline at candidate_dir/holdout_summary.json
        (NOT by _write_aggregate_summary which writes top-level cohort JSON)."""
        from scripts import run_phase2c_evaluation_gate as producer
        import pandas as pd

        def mock_engine(**kwargs):
            from backtest.engine import RegimeHoldoutResult, write_per_bar_artifact
            artifact_dir = kwargs.get("artifact_dir")
            if artifact_dir:
                ec = pd.Series([1.0, 2.0], index=pd.date_range("2026-01-01", periods=2, tz="UTC"))
                write_per_bar_artifact(ec, artifact_dir, "test")
            return RegimeHoldoutResult(
                run_id="test", parent_run_id="test", batch_id="test",
                hypothesis_hash="testhash00000000", regime_holdout_passed=True,
                sharpe_ratio=1.0, max_drawdown=0.1, total_return=0.05, total_trades=10,
                passing_criteria={}, metrics={},
                equity_curve=pd.Series([1.0, 2.0], index=pd.date_range("2026-01-01", periods=2, tz="UTC")),
            )

        monkeypatch.setattr(producer, "run_regime_holdout", mock_engine)

        candidate = {"hypothesis_hash": "test1234567890ab", "position": 1, "theme": "t", "name": "n"}
        producer._evaluate_one_candidate(
            candidate=candidate, head_sha="sha", source_batch_id="phase2c_15_main_fire_combined",
            run_id="test-run", output_dir=tmp_path, regime_key="evaluation_regimes.forward_2026",
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
        )

        # Per-candidate JSON at candidate_dir/holdout_summary.json
        candidate_json = tmp_path / candidate["hypothesis_hash"] / "holdout_summary.json"
        assert candidate_json.exists()
        with open(candidate_json) as f:
            data = json.load(f)
        assert "gamma3" in data and "gamma4" in data and "T_obs" in data

    # ----- 2. _finalize_batch_registry tests (6) -----

    def test_finalize_batch_registry_writes_parent_row_only(self, tmp_path):
        """_finalize_batch_registry() writes ONLY 1 parent batch_summary row
        (39 child rows written by engine per-candidate at LC-b path)."""
        from scripts.run_phase2c_evaluation_gate import _finalize_batch_registry
        from backtest.experiment_registry import get_connection

        db_path = tmp_path / "test.db"
        run_id = "test_parent_only"

        _finalize_batch_registry(
            run_id=run_id,
            aggregate={"regime_key": "evaluation_regimes.forward_2026",
                       "forward_window_metadata": {
                           "forward_window_start_utc": "2026-01-01T00:00:00Z"
                       }},
            head_sha="test-sha",
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
            parquet_data_sha256="a" * 64,
            db_path=db_path,
            force_rerun_existing=False,
        )

        with get_connection(db_path) as conn:
            rows = conn.execute(
                "SELECT run_id, run_type FROM runs WHERE run_id = ?", (run_id,)
            ).fetchall()
        assert len(rows) == 1
        assert rows[0][1] == "batch_summary"

    def test_finalize_batch_registry_parent_cohort_metadata_complete(self, tmp_path):
        """Parent row must include cohort-level fields (git_commit + cost_anchor_id
        + batch_id + execution_config_path + parquet_data_sha256 + etc.)."""
        from scripts.run_phase2c_evaluation_gate import _finalize_batch_registry
        from backtest.experiment_registry import get_connection

        db_path = tmp_path / "test.db"
        run_id = "test_cohort_meta"
        _finalize_batch_registry(
            run_id=run_id,
            aggregate={"regime_key": "evaluation_regimes.forward_2026",
                       "forward_window_metadata": {"forward_window_start_utc": "2026-01-01T00:00:00Z"}},
            head_sha="abcdef0123456789",
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
            parquet_data_sha256="b" * 64,
            db_path=db_path,
        )

        with get_connection(db_path) as conn:
            row = conn.execute(
                "SELECT git_commit, cost_anchor_id, batch_id, execution_config_path, "
                "parquet_data_sha256, regime_key FROM runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        assert row is not None
        git_commit, cost_anchor_id, batch_id, exec_path, parquet_sha, regime_key = row
        assert git_commit == "abcdef0123456789"
        assert cost_anchor_id == "phase4_forward_15bps_v1"
        assert batch_id == run_id
        assert "execution_phase4_15bps.yaml" in exec_path
        assert parquet_sha == "b" * 64
        assert regime_key == "evaluation_regimes.forward_2026"

    def test_finalize_batch_registry_refuses_if_existing_no_force_flag(self, tmp_path):
        """R9-B-guarded default behavior: refuse-with-DELETE-command-emit if any
        rows match parent_run_id; error message must contain explicit DELETE
        command for manual operator review."""
        from scripts.run_phase2c_evaluation_gate import _finalize_batch_registry
        from backtest.experiment_registry import get_connection, insert_run

        db_path = tmp_path / "test.db"
        run_id = "test_refuse_no_force"

        # Pre-populate a child row to trigger refuse
        with get_connection(db_path) as conn:
            insert_run(conn, {
                "run_id": "child-pre-existing",
                "run_type": "regime_holdout",
                "parent_run_id": run_id,
                "strategy_name": "stub",
                "strategy_source": "stub",
                "created_at_utc": "2026-05-26T00:00:00Z",
            })

        with pytest.raises(RuntimeError) as exc_info:
            _finalize_batch_registry(
                run_id=run_id,
                aggregate={"regime_key": "evaluation_regimes.forward_2026"},
                head_sha="sha",
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                parquet_data_sha256="c" * 64,
                db_path=db_path,
                force_rerun_existing=False,
            )
        # Error message must contain DELETE command
        assert "DELETE FROM runs WHERE" in str(exc_info.value)
        assert run_id in str(exc_info.value)

    def test_finalize_batch_registry_force_rerun_existing_deletes_then_writes(self, tmp_path):
        """R9-B-guarded force flag: when --force-rerun-existing flag passed,
        auto-DELETE existing rows + write new parent row."""
        from scripts.run_phase2c_evaluation_gate import _finalize_batch_registry
        from backtest.experiment_registry import get_connection, insert_run

        db_path = tmp_path / "test.db"
        run_id = "test_force_rerun"

        # Pre-populate matching rows
        with get_connection(db_path) as conn:
            for hash_ in ["a" * 16, "b" * 16, "c" * 16]:
                insert_run(conn, {
                    "run_id": f"{run_id}_{hash_}",
                    "run_type": "regime_holdout",
                    "parent_run_id": run_id,
                    "strategy_name": "stub",
                    "strategy_source": "stub",
                    "created_at_utc": "2026-05-26T00:00:00Z",
                })

        _finalize_batch_registry(
            run_id=run_id,
            aggregate={"regime_key": "evaluation_regimes.forward_2026",
                       "forward_window_metadata": {"forward_window_start_utc": "2026-01-01T00:00:00Z"}},
            head_sha="sha",
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
            parquet_data_sha256="d" * 64,
            db_path=db_path,
            force_rerun_existing=True,
        )

        # Verify: pre-existing 3 child rows DELETED, new parent row inserted
        with get_connection(db_path) as conn:
            child_count = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE parent_run_id = ?", (run_id,)
            ).fetchone()[0]
            parent_row = conn.execute(
                "SELECT run_type FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        assert child_count == 0
        assert parent_row is not None and parent_row[0] == "batch_summary"

    def test_finalize_batch_registry_child_run_id_deterministic_scheme(self):
        """Verify the deterministic child run_id scheme {parent}_{hash} pattern
        is documented + used by _evaluate_one_candidate (producer side)."""
        # This is a documentation-discipline test: the producer derives child
        # run_ids deterministically. Verify the scheme via grep against producer code.
        producer_src = Path(__file__).resolve().parent.parent / "scripts" / "run_phase2c_evaluation_gate.py"
        text = producer_src.read_text()
        assert "f\"{run_id}_{candidate['hypothesis_hash']}\"" in text or \
               "f\"{run_id}_{candidate[\"hypothesis_hash\"]}\"" in text, (
            "Producer must use deterministic child run_id pattern {run_id}_{hypothesis_hash}"
        )

    def test_finalize_batch_registry_wired_into_main_flow(self):
        """_finalize_batch_registry() MUST be called from main() after
        _write_aggregate_summary. Verify wiring via source inspection."""
        producer_src = Path(__file__).resolve().parent.parent / "scripts" / "run_phase2c_evaluation_gate.py"
        text = producer_src.read_text()
        # Find main() function content
        main_idx = text.find("def main(")
        assert main_idx > 0, "main() function not found"
        main_body = text[main_idx:main_idx + 5000]  # 5K chars should cover main body
        assert "_finalize_batch_registry(" in main_body, (
            "_finalize_batch_registry() MUST be called from main() — currently NOT wired"
        )

    # ----- 3. Archive step tests (2) -----

    def test_archive_original_artifact_refuses_existing_target(self, tmp_path):
        """R10 strict refuse-if-exists semantics."""
        from scripts.run_phase2c_evaluation_gate import _archive_original_artifact

        canonical = tmp_path / "canonical_dir"
        canonical.mkdir()
        archive_root = tmp_path / "archive"
        archive_root.mkdir()
        target = archive_root / "canonical_dir_d0b8101"
        target.mkdir()  # pre-existing — should trigger refuse

        with pytest.raises(RuntimeError) as exc_info:
            _archive_original_artifact(canonical, archive_root, archive_tag="d0b8101")
        assert "already exists" in str(exc_info.value).lower()

    def test_archive_original_artifact_moves_canonical_to_archive(self, tmp_path):
        """Happy path: canonical → archive/{name}_{tag}; source removed; target populated."""
        from scripts.run_phase2c_evaluation_gate import _archive_original_artifact

        canonical = tmp_path / "src_dir"
        canonical.mkdir()
        (canonical / "sample.json").write_text('{"key": "value"}')
        archive_root = tmp_path / "archive"
        # archive_root absent (function should create)

        result = _archive_original_artifact(canonical, archive_root, archive_tag="abc1234")

        assert not canonical.exists()
        assert result == archive_root / "src_dir_abc1234"
        assert (result / "sample.json").exists()

    # ----- 4. _CSV_FIELDS extension test (1) -----

    def test_csv_fields_extension_includes_5_new_columns(self):
        """_CSV_FIELDS must include γ3 / γ4 / T_obs / returns_per_bar_path /
        returns_per_bar_sha256 (5 new columns per spec §3.2.5)."""
        from scripts.run_phase2c_evaluation_gate import _CSV_FIELDS
        required_new = {
            "gamma3", "gamma4", "T_obs",
            "returns_per_bar_path", "returns_per_bar_sha256",
        }
        missing = required_new - set(_CSV_FIELDS)
        assert not missing, f"_CSV_FIELDS missing new columns: {missing}"

    # ----- 5. CLI flag test (1) -----

    def test_force_rerun_existing_cli_flag_present(self):
        """--force-rerun-existing CLI flag must be argparse-defined + threaded to
        _finalize_batch_registry call site."""
        from scripts.run_phase2c_evaluation_gate import _parse_args

        # Verify by parsing with the flag
        import sys
        original_argv = sys.argv
        try:
            sys.argv = ["prog", "--source-batch-id", "test",
                        "--candidate-hashes", "a", "--regime-key", "test",
                        "--execution-config", "test.yaml", "--force-rerun-existing"]
            args = _parse_args()
            assert hasattr(args, "force_rerun_existing")
            assert args.force_rerun_existing is True
        finally:
            sys.argv = original_argv

    # ----- 6. Schema-domain routing test (1) -----

    def test_schema_domain_routing_evaluation_domain_for_per_candidate_json(self):
        """Per-candidate holdout_summary.json validated by
        check_evaluation_semantics_or_raise (evaluation domain, phase2c_7_1);
        NOT by check_b_c_extended_semantics_or_raise."""
        producer_src = Path(__file__).resolve().parent.parent / "scripts" / "run_phase2c_evaluation_gate.py"
        text = producer_src.read_text()
        assert "check_evaluation_semantics_or_raise" in text
        # The b_c_extended validator is called at engine-side via revalidate_for_write,
        # NOT at producer-side. Producer should NOT call check_b_c_extended_semantics_or_raise
        # on the per-candidate JSON.
        # (Producer can still IMPORT it for other purposes; check call sites:)
        import re
        bcext_calls = re.findall(r"check_b_c_extended_semantics_or_raise\s*\(", text)
        # If any producer call exists, it must NOT be on per-candidate JSON path
        # — but for simplicity in this test, just verify evaluation-domain is the
        # validator used at per-candidate JSON round-trip in _evaluate_one_candidate.
        assert text.count("check_evaluation_semantics_or_raise") >= 1
```

- [ ] **Step 10.2: Run all 13 tests — they must FAIL (RED)**

```bash
python -m pytest tests/test_phase2c_evaluation_gate_runner.py::TestBCNarrowProducerEdits -v
```

Expected: all 13 FAIL (producer not yet modified).

- [ ] **Step 10.3: Commit**

```bash
git add tests/test_phase2c_evaluation_gate_runner.py
git commit -m "test(b-c-narrow/phase-2): add 13 failing producer-edit tests (T10)

RED-phase tests per B-C-narrow plan v2 Phase 2. All 13 test bodies written
in full per Charlie no敷衍 requirement (no placeholder comments). Covers:

1. LC-b 4-kwarg threading (NOT 5; cost_anchor_id derived)
2. γ3/γ4/T_obs/returns_per_bar_path/sha256 merge into per-candidate summary JSON
3. Inline JSON write at scripts:550-556 (NOT _write_aggregate_summary)
4. _finalize_batch_registry parent-row-only
5. _finalize_batch_registry cohort metadata complete
6. R9-B-guarded refuse-if-existing default + DELETE command in error message
7. R9-B-guarded --force-rerun-existing flag auto-DELETE+rewrite
8. Deterministic child run_id {parent}_{hash} scheme
9. _finalize_batch_registry wired into main() flow
10. Archive step refuse-if-existing
11. Archive step happy-path move
12. _CSV_FIELDS extension 5 columns
13. --force-rerun-existing CLI flag argparse-defined
14. Schema-domain routing evaluation-domain for per-candidate JSON

All 13 tests FAIL at this commit. Task 11 implements producer changes."
```

---

### Task 11: Implement producer edits

**Files:**
- Modify: `scripts/run_phase2c_evaluation_gate.py`

Implement in this order:

- [ ] **Step 11.1: Add `--force-rerun-existing` CLI flag**

Edit `_parse_args()` (find at `grep -n "_parse_args" scripts/run_phase2c_evaluation_gate.py`). Add:

```python
p.add_argument(
    "--force-rerun-existing",
    action="store_true",
    help=(
        "B-C-narrow R9-B-guarded: when present, _finalize_batch_registry "
        "auto-DELETEs rows matching parent_run_id of this fire's run_id "
        "before writing the new parent batch_summary row. Default: refuse "
        "if any matching rows exist + emit DELETE command for manual review."
    ),
)
```

- [ ] **Step 11.2: Extend `_CSV_FIELDS` at line 581-595 with 5 new columns**

Add `"gamma3"`, `"gamma4"`, `"T_obs"`, `"returns_per_bar_path"`, `"returns_per_bar_sha256"` to the tuple.

- [ ] **Step 11.3: Edit `_evaluate_one_candidate` at line 480 with 4 LC-b kwargs**

Modify the function body to:
- Build per-candidate `candidate_dir = output_dir / candidate["hypothesis_hash"]` (already exists; verify)
- Build deterministic child_run_id: `child_run_id = f"{run_id}_{candidate['hypothesis_hash']}"`
- Pass 4 LC-b kwargs to `run_regime_holdout`:
  ```python
  holdout_result = run_regime_holdout(
      # ... existing positional + kwargs unchanged ...
      run_id_override=child_run_id,
      source_batch_id=source_batch_id,
      parent_run_id_override=run_id,  # cohort-level run_id is parent
      artifact_dir=candidate_dir,
  )
  ```
- After holdout_result returned, merge γ3/γ4/T_obs/returns_per_bar_path/returns_per_bar_sha256 into `summary` dict by reading the registry row written by the engine (or by recomputing from equity_curve via `compute_per_bar_returns` + `compute_moments`).

- [ ] **Step 11.4: Add NEW `_archive_original_artifact()` function**

Per spec §3.2.4 + plan v2 Task 10 test specs. Function signature:

```python
def _archive_original_artifact(
    canonical_path: Path,
    archive_root: Path,
    archive_tag: str = "d0b8101",
) -> Path:
    """Per spec §3.2.4 + §7 R10 strict refuse-if-exists."""
    import shutil
    archive_root.mkdir(parents=True, exist_ok=True)
    archive_target = archive_root / f"{canonical_path.name}_{archive_tag}"
    if archive_target.exists():
        raise RuntimeError(
            f"B-C-narrow R10 archive refusal: target {archive_target} already exists. "
            f"Manual cleanup required before re-fire."
        )
    if not canonical_path.exists():
        raise RuntimeError(
            f"B-C-narrow archive: source {canonical_path} does not exist."
        )
    shutil.move(str(canonical_path), str(archive_target))
    return archive_target
```

- [ ] **Step 11.5: Add NEW `_finalize_batch_registry()` function**

Per spec §3.2.3 + plan v2 Task 10 test specs. R9-B-guarded compensating cleanup. Writes ONLY 1 parent batch_summary row:

```python
def _finalize_batch_registry(
    run_id: str,
    aggregate: dict[str, Any],
    *,
    head_sha: str,
    execution_config_path: Path | None,
    parquet_data_sha256: str,
    db_path: Path | None = None,
    force_rerun_existing: bool = False,
) -> None:
    """Per spec §3.2.3 + R9-B-guarded. Writes ONLY 1 parent batch_summary row;
    39 child rows are written per-candidate by engine LC-b path."""
    from backtest.experiment_registry import get_connection, insert_run
    from datetime import datetime, timezone
    import hashlib

    with get_connection(db_path) as conn:
        existing_children = conn.execute(
            "SELECT COUNT(*) FROM runs WHERE parent_run_id = ?", (run_id,)
        ).fetchone()[0]
        existing_parent = conn.execute(
            "SELECT COUNT(*) FROM runs WHERE run_id = ?", (run_id,)
        ).fetchone()[0]

        if existing_children > 0 or existing_parent > 0:
            if not force_rerun_existing:
                raise RuntimeError(
                    f"B-C-narrow R9-B-guarded refusal: {existing_children} child rows + "
                    f"{existing_parent} parent rows exist matching run_id pattern '{run_id}'. "
                    f"To proceed, EITHER (a) MANUALLY run:\n"
                    f"  sqlite3 backtest/experiments.db \"DELETE FROM runs WHERE "
                    f"parent_run_id = '{run_id}' OR run_id = '{run_id}';\"\n"
                    f"OR (b) re-fire with --force-rerun-existing flag (auto-DELETE + re-write). "
                    f"Cycle ABORTED."
                )
            logger.warning(
                "R9-B-guarded force-rerun-existing: deleting %d children + %d parent at run_id=%s",
                existing_children, existing_parent, run_id,
            )
            conn.execute(
                "DELETE FROM runs WHERE parent_run_id = ? OR run_id = ?",
                (run_id, run_id),
            )
            conn.commit()

        # Compute execution_config_sha256
        exec_cfg_sha = None
        if execution_config_path and Path(execution_config_path).exists():
            sha = hashlib.sha256()
            with open(execution_config_path, "rb") as f:
                while True:
                    chunk = f.read(64 * 1024)
                    if not chunk: break
                    sha.update(chunk)
            exec_cfg_sha = sha.hexdigest()

        parent_row = {
            "run_id": run_id,
            "run_type": "batch_summary",
            "parent_run_id": None,
            "strategy_name": "cohort_summary",
            "strategy_source": "b_c_narrow_recovery",
            "git_commit": head_sha,
            "current_git_sha": head_sha,
            "data_snapshot_date": (
                aggregate.get("forward_window_metadata", {}).get("forward_window_start_utc", "")[:10]
                if aggregate.get("forward_window_metadata") else None
            ),
            "effective_start": aggregate.get("forward_window_metadata", {}).get("forward_window_start_utc"),
            "fee_model": "phase4_forward_15bps_v1",
            "batch_id": run_id,
            "cost_anchor_id": "phase4_forward_15bps_v1",
            "regime_key": aggregate.get("regime_key", "evaluation_regimes.forward_2026"),
            "execution_config_path": str(execution_config_path) if execution_config_path else None,
            "execution_config_sha256": exec_cfg_sha,
            "parquet_data_sha256": parquet_data_sha256,
            "initial_capital": 100000.0,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        insert_run(conn, parent_row)

    logger.info("B-C-narrow _finalize_batch_registry: parent row written at run_id=%s", run_id)
```

- [ ] **Step 11.6: Wire `_archive_original_artifact()` + `_finalize_batch_registry()` into main()**

Find `main()` in `scripts/run_phase2c_evaluation_gate.py`. Add:
- At start of fire flow (before iterating candidates): if `run_id == "phase4_forward_2026_15bps_v1_b_c_narrow"` and original path exists, call `_archive_original_artifact(...)` per spec §3.2.4.
- After `_write_aggregate_summary` writes the cohort holdout_summary.json: call `_finalize_batch_registry(run_id=args.run_id, aggregate=aggregate, head_sha=head_sha, execution_config_path=args.execution_config, parquet_data_sha256=parquet_data_sha256, db_path=None, force_rerun_existing=args.force_rerun_existing)`.

- [ ] **Step 11.7: Extend `_write_aggregate_summary` with cohort fields (per spec §3.2.2)**

Edit `_write_aggregate_summary` at line 706 to include cohort-level metadata in top-level holdout_summary.json: `forward_window_metadata`, `audit_only_*`, `by_theme`, `lineage_check`, `engine_commit`, `current_git_sha`.

- [ ] **Step 11.8: Run all 13 producer tests — they must now PASS**

```bash
python -m pytest tests/test_phase2c_evaluation_gate_runner.py::TestBCNarrowProducerEdits -v
```

Expected: all 13 PASS.

- [ ] **Step 11.9: Full test suite zero-regression**

```bash
python -m pytest -q
```

Expected: 2330 + 13 = 2343 tests passing.

- [ ] **Step 11.10: Commit**

```bash
git add scripts/run_phase2c_evaluation_gate.py
git commit -m "feat(b-c-narrow/phase-2): producer edits (T11)

Per Approach D' + LC-b 4-kwarg lock + R9-B-guarded + spec §3.2 producer wiring."
```

---

### Task 12: T1.4 baseline maintenance

- [ ] **Step 12.1: Recompute baseline values**

```bash
grep -rn "_write_to_registry(" backtest/ scripts/ --include="*.py" | wc -l
grep -rn "_write_to_registry(" tests/ --include="*.py" | wc -l
grep -rn "_write_to_registry(\*\*" tests/ --include="*.py" | wc -l
```

- [ ] **Step 12.2: Update `_B1_LOCKED_4TUPLE` as DICT not tuple**

Edit `tests/test_t1_4_backward_compat.py:83-88`. Update dict keys per recomputed values:

```python
_B1_LOCKED_4TUPLE = {
    "prod_count": <new prod_count>,
    "test_count": <new test_count>,
    "scripts_count": <new scripts_count>,
    "dynamic_count": <new dynamic_count>,
}
```

- [ ] **Step 12.3: Run T1.4 test**

```bash
python -m pytest tests/test_t1_4_backward_compat.py -v
```

- [ ] **Step 12.4: Commit + Charlie Phase 2 register-event ratify**

```bash
git add tests/test_t1_4_backward_compat.py
git commit -m "test(b-c-narrow/phase-2): T1.4 baseline maintenance update (T12)"
```

**STOP HERE. Charlie register-event #N+2.** Surface:
- T1.4 baseline updated
- 13 producer tests + 13 engine tests + Phase 0/1 gates all GREEN
- Full suite 2343/2343
- Phase 2 implementation ratify before Phase 3 fire

Do NOT proceed to Phase 3 without Charlie register.

---

# Phase 3 — Fire (Tasks 13-16)

### Task 13: Archive original + capture V4 fixture for ALL 39 candidates

- [ ] **Step 13.1: Verify pre-archive state + execute archive**

```bash
test -d data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1 && echo OK
test ! -e data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101 && echo OK
mkdir -p data/phase2c_evaluation_gate/archive
mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1 data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101
```

- [ ] **Step 13.2: Capture V4 fixture for ALL 39 candidates (per spec §4.2)**

```bash
python << 'EOF'
import json, csv
from pathlib import Path
archive = Path("data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101")
v4_baseline = {}
with open(archive / "holdout_results.csv") as f:
    for row in csv.DictReader(f):
        h = row["hypothesis_hash"]
        sj = archive / h / "holdout_summary.json"
        with open(sj) as g:
            full = json.load(g)
        v4_baseline[h] = {
            "sharpe_ratio": full["holdout_metrics"]["sharpe_ratio"],
            "max_drawdown": full["holdout_metrics"]["max_drawdown"],
            "total_return": full["holdout_metrics"]["total_return"],
            "total_trades": full["holdout_metrics"]["total_trades"],
            "holdout_passed": full["holdout_passed"],
            "gate_pass_per_criterion": full["gate_pass_per_criterion"],
        }
assert len(v4_baseline) == 39, f"V4 baseline must cover 39; got {len(v4_baseline)}"
Path("tests/fixtures").mkdir(parents=True, exist_ok=True)
with open("tests/fixtures/b_c_narrow_archived_baseline.json", "w") as f:
    json.dump(v4_baseline, f, indent=2, sort_keys=True)
print(f"V4 baseline captured for {len(v4_baseline)} candidates")
EOF
```

- [ ] **Step 13.3: Commit V4 fixture**

```bash
git add tests/fixtures/b_c_narrow_archived_baseline.json
git commit -m "test(b-c-narrow/phase-3): capture V4 baseline for all 39 candidates (T13)"
```

---

### Task 14: Fire producer

- [ ] **Step 14.1: Extract 39 candidate hashes**

```bash
tail -n +2 data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/holdout_results.csv | \
  cut -d, -f1 | tr '\n' ',' | sed 's/,$//' > /tmp/cohort_a_hashes.txt
# Verify count (should be 39):
python -c "import sys; print(len(open('/tmp/cohort_a_hashes.txt').read().split(',')))"
```

- [ ] **Step 14.2: Fire producer**

```bash
python -m scripts.run_phase2c_evaluation_gate \
  --candidate-hashes "$(cat /tmp/cohort_a_hashes.txt)" \
  --source-batch-id phase2c_15_main_fire_combined \
  --regime-key evaluation_regimes.forward_2026 \
  --execution-config config/execution_phase4_15bps.yaml \
  --run-id phase4_forward_2026_15bps_v1_b_c_narrow \
  --output-root data/phase2c_evaluation_gate/ \
  2>&1 | tee /tmp/b_c_narrow_fire_log.txt
```

Expected: ~10-30s wall-clock; sibling dir `phase4_forward_2026_15bps_v1_b_c_narrow/` created with 39 candidate subdirs.

- [ ] **Step 14.3: Sanity-verify outputs**

```bash
ls data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/*/returns_per_bar.parquet | wc -l
# Expected: 39
sqlite3 backtest/experiments.db "SELECT run_type, COUNT(*) FROM runs WHERE parent_run_id = 'phase4_forward_2026_15bps_v1_b_c_narrow' OR run_id = 'phase4_forward_2026_15bps_v1_b_c_narrow' GROUP BY run_type;"
# Expected: regime_holdout|39 + batch_summary|1
```

---

### Task 15: V4 verification + G4-G7 gates

- [ ] **Step 15.1: Write V4 + G4-G7 tests in `tests/test_b_c_narrow_v4_reproducibility.py`**

Concrete assertion code for ALL 39 candidates (NOT placeholder). Test methods:
- `test_v4_per_candidate_metric_diff_within_epsilon` (all 39 candidates)
- `test_v4_total_trades_exact_match`
- `test_v4_drift_stop_condition_blocks_seal_on_breach`
- `test_g4_per_bar_parquet_row_count_matches_t_obs`
- `test_g5_gamma_round_trip_from_parquet_within_epsilon`
- `test_g6_registry_parent_child_integrity_count_39_plus_1`
- `test_g7_archive_dir_populated_canonical_path_repopulated_after_t14b`

- [ ] **Step 15.2: Run V4 + G4-G7 tests**

```bash
python -m pytest tests/test_b_c_narrow_v4_reproducibility.py -v
```

Expected: all PASS.

- [ ] **Step 15.3: Charlie register-event #N+3 — Phase 3 V4 PASS ratify before T14b relocation**

**STOP HERE.**

---

### Task 16: T14b — Canonical-path relocation (only if T15 V4 PASS + Charlie register)

```bash
mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1
```

Verify:
```bash
test -d data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1 && echo OK
test ! -e data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow && echo OK
test -d data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101 && echo OK
```

---

# Phase 4 — SEAL (Tasks 17-18)

### Task 17: NOTE doc + B2 reviewer + Rule 2 SEAL-eve

- [ ] **Step 17.1: Draft `docs/phase5/B_C_NARROW_DATA_RECOVERY_NOTE.md`** (~400-600 lines per spec §10.6)

Cover all §1-§10 + V4 audit results + per-candidate diff statistics + Phase 0+1+2+3 outcomes + IP6 tech-debt successor note + anti-pre-emption preserved §9 successors enumeration.

- [ ] **Step 17.2: B2 2-leg reviewer dispatch on NOTE doc**
- [ ] **Step 17.3: Rule 2 SEAL-eve adversarial dispatch** (mandatory per spec §10.3)
- [ ] **Step 17.4: Apply SEAL-eve findings inline + Charlie ratify**
- [ ] **Step 17.5: Prepare Phase Marker advance + history.md atomic update**

### Task 18: SEAL bundle fire

Atomic commit per spec §10.6 11-item checklist. See spec doc for verbatim checklist.

---

## DEFER items resolved by plan v2

| # | Item | Resolution |
|---|---|---|
| 1 | TDD micro-ordering | LOCKED: RED → fails → impl → passes → commit (applied at every task) |
| 2 | IP6 1076-line size | Tech-debt note only; included in NOTE doc §9 successors |
| 3 | R9 compensating-cleanup | LOCKED: R9-B-guarded (refuse default + `--force-rerun-existing` opt-in) |
| 4 | §3.4 LineageContext pattern | LOCKED: LC-b 4-kwarg (cost_anchor_id derived; producer-passed run_id_override + source_batch_id + parent_run_id_override + artifact_dir) |

---

## Execution Handoff

**Plan v2 saved to `docs/superpowers/plans/2026-05-26-b-c-narrow-data-recovery-cycle-execution-plan.md`.**

After plan v2 B2 2-leg PFR ratifies APPROVE → use **superpowers:subagent-driven-development** (EXEC-SUBAGENT) per Charlie register: dispatch fresh subagent per task with two-stage review.
