# B-C-narrow Phase 0 — Engine Extension Sub-Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this sub-plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Sub-plan scope:** Phase 0 of B-C-narrow data-recovery cycle ONLY — engine extension at `backtest/engine.py` (RegimeHoldoutResult.equity_curve field + run_regime_holdout signature with 4 LC-b kwargs + LC-b internal LineageContext construction + atomic write-then-registry sequencing).

**Sub-plan motivation:** Plan v2 (committed at `ca427b9`, 2143 lines) returned NOT-APPROVE from Codex R2 PFR with 6 BLOCKING engineering errors (R9 finalizer architectural flaw + create_table missing + _parse_args nonexistent + parquet_data_sha256 empty + T1.4 grep methodology + G4-G7 bodies missing). Per Charlie register PV3-SPLIT-BY-PHASE 2026-05-26: monolithic ~2000-line plan exceeds orchestrator reliable-Mode-A-verification capacity in one drafting pass; split into 4 phase-specific sub-plans with per-phase ratify + SEAL boundary. Phase 1/2/3-4 sub-plans drafted SEPARATELY after Phase 0 sealed.

**Tech Stack:** Python 3.11+, pytest, pandas/numpy/scipy, SQLite, parquet (pyarrow), Backtrader 1.9.78+.

**Cycle context:** R6.1 V_SEAL §10 binding precondition (`d6c7fc0` spec doc). Cycle entry Charlie register 2026-05-26 N1. This is Phase 0 sub-plan — Phase 1+2+3+4 follow per-phase SEAL discipline.

---

## Codex BLOCKING fixes within Phase 0 scope (all applied below)

| # | Codex BLOCKING / advisor finding | Fix applied in this sub-plan |
|---|---|---|
| BLOCKING-2 | `parquet_data_sha256` empty when producer doesn't pass parquet_path | Task 4 §4.2: engine resolves canonical default `data/raw/btcusdt_1h.parquet` when `parquet_path is None`; LC-b construction uses resolved path for SHA256 |
| HIGH | Engine tests write to production `backtest/experiments.db` | Task 1: ALL real-engine tests pass `db_path=tmp_path / "<test>.db"` |
| HIGH | LC 14-field test comments out `engine_commit` assertion | Task 1: explicit `engine_commit == "eb1c87f"` assertion in `test_run_regime_holdout_lcb_constructs_lineage_context_with_all_14_fields` |
| D-N1 MEDIUM | `revalidate_for_write()` double-invocation | Task 4: engine-side explicit call DROPPED; relies on `_write_to_registry:1149` invocation (existing T1.1 SYS5 invariant) |
| D-N2 MEDIUM | `lcb_active` precondition gap when `artifact_dir is None` | Task 4 §4.2: `lcb_active = artifact_dir is not None` (single gate); other LC-b kwargs without artifact_dir → no LC-b path activation |
| D-N3 LOW | `get_git_commit()` None handling | Task 4: explicit `raise ValueError` if `get_git_commit()` returns None at LC-b construction (better than silent empty string fail-closed) |
| D-N4 LOW | `hypothesis_hash` None handling | Task 4: LC-b path requires hypothesis_hash; explicit precondition raise if None |
| BLOCKING-4 (Phase 2 issue carry-forward) | `_parse_args` nonexistent — actual is `_build_argparser()` | NOTE for Plan v3-Phase2: producer tests must reference `_build_argparser`; deferred to Phase 2 sub-plan |
| BLOCKING-1 (Phase 2 issue) | R9 finalizer call-order architectural flaw | NOTE for Plan v3-Phase2: R9 split into PRE-flight guard (before candidate loop) + POST-fire parent-only finalizer (after children written) |
| BLOCKING-3 (Phase 2 issue) | `_finalize_batch_registry` queries before `create_table` | NOTE for Plan v3-Phase2: producer-side fix |
| BLOCKING-5 G4-G7 (Phase 3 issue) | Test bodies missing | NOTE for Plan v3-Phase3-4: G4-G7 inlined there |
| BLOCKING-6 T1.4 methodology (Phase 2 issue) | grep-based vs AST-correct | NOTE for Plan v3-Phase2: producer-side fix |

---

## File Structure (Phase 0 scope only)

| File | Action | Scope |
|---|---|---|
| `backtest/engine.py` | MODIFY | 5 modify-zones (per Tasks 2-4):<br>• **Imports** (Step 4.1): add `CORRECTED_WF_ENGINE_COMMIT`, `LineageContext`, `get_git_commit`<br>• **Post-line-53 constants** (Step 4.1): add `_compute_sha256_file` + `_resolve_canonical_parquet_path`<br>• **Lines 2044-2063** (Task 2): RegimeHoldoutResult +`equity_curve` field<br>• **Lines 2270-2291** (Task 3): `run_regime_holdout` signature +4 LC-b kwargs<br>• **Lines 2435-2523** (Task 4): body sequence + LC-b construction + preflight |
| `tests/conftest.py` | CREATE OR EXTEND | NEW shared fixtures (`btc_parquet_path`, `dsl_bollinger_zscore_reversion`, `dsl_monday_dip_buy`) for engine tests |
| `tests/test_t1_1_artifact_writer.py` | EXTEND | NEW `TestBCNarrowPhase0EngineExtension` class (13 test methods post-PFR-R3-v3.3 merger; all bodies in full per Charlie no敷衍) |
| `tests/test_phase2c_evaluation_gate_runner.py` | MODIFY | Line 83 existing `RegimeHoldoutResult(...)` stub +`equity_curve=pd.Series(dtype=float)` arg |
| `tests/test_t1_4_backward_compat.py` | MODIFY | Line 1384 existing `RegimeHoldoutResult(...)` stub +`equity_curve=` arg |

**Data layer (Phase 0):** none. Phase 0 touches NO data files; only engine code + tests.

---

## Pre-Phase-0 Charlie register-event boundary (HISTORICAL — Charlie register PUSH-AFTER-V3.2 fulfilled)

**Historical STOP-HERE record at v3-Phase0 drafting time:**

The original STOP-HERE asked Charlie to register either (1) push pre-Phase-0
commits to origin/main, OR (2) authorize Phase 0 dispatch with commits local.

**Resolution per Charlie register chain (2026-05-26):**
- PUSH-AFTER-V3.2 register (2026-05-26): Charlie authorized push after v3.2
  commit; subsequently v3.2 (`3f2babe`) → v3.3 (`cff08e0`) → v3.4 (this commit)
  all pushed to origin/main as the v3.x amend cycle progressed.
- AMEND-RE-PFR-R4 register (2026-05-26): authorized PFR R3 → v3.3 amend cycle.
- Option 2 (AMEND-NOW-THEN-WAIT-CODEX, 2026-05-26): authorized v3.4 polish
  during Codex usage-limit window + post-reset Codex R4 leg verification.

This section is preserved as a historical record. Phase 0 dispatch (Task 1)
remains gated by a separate Charlie register-event (EXEC-SUBAGENT) after
PFR R4 returns convergent APPROVE on v3.4.

---

# Phase 0 — Engine extension (Tasks 1-5)

### Task 1: Write FAILING engine-extension tests + shared fixtures

**Files:**
- Create OR extend: `tests/conftest.py`
- Modify: `tests/test_t1_1_artifact_writer.py` (append new class)

- [ ] **Step 1.1: Create or extend `tests/conftest.py`**

Check existence: `test -f tests/conftest.py && cat tests/conftest.py | head -30`. If exists, APPEND below imports; otherwise CREATE.

```python
# tests/conftest.py — CREATE or APPEND
"""Shared pytest fixtures for B-C-narrow tests + other repo tests."""
import json
from pathlib import Path

import pandas as pd
import pytest

# DEFECT-N2 fix per PFR R2: single source of truth — import from producer.
# Producer's `_strip_markdown_fence` at scripts/run_phase2c_evaluation_gate.py:242
# uses regex-based fence match (_FENCE_RE); conftest must NOT diverge with a
# parallel implementation.
# PFR R3 LOW L2 + PFR R4 MEDIUM N2b + PFR R4 MEDIUM M2 fix (v3.5): module
# import is safe in practice — scripts/run_phase2c_evaluation_gate.py top-of-
# module (lines 75-130) has only import statements + top-level constant
# assignments + ONE benign side-effecting call: line 90's
# `sys.path.insert(0, str(PROJECT_ROOT))` (PROJECT_ROOT resolves to repo root
# via Path(__file__).resolve().parent.parent). The sys.path mutation is
# idempotent (re-running prepends a duplicate but doesn't break import
# resolution) AND the pytest test runner already includes the repo root in
# sys.path by default, so the call is functionally a no-op when imported from
# tests/. No network/disk I/O at import; no `if __name__ == "__main__":`
# block runs at module load. Pre-existing safe-import precedent at
# tests/test_t1_4_backward_compat.py:1323-1326 already exercises this path.
from scripts.run_phase2c_evaluation_gate import _strip_markdown_fence


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def btc_parquet_path() -> Path:
    """Canonical BTC OHLCV parquet path used by engine tests."""
    return REPO_ROOT / "data" / "raw" / "btcusdt_1h.parquet"


@pytest.fixture
def dsl_bollinger_zscore_reversion():
    """Load cohort_a candidate 18d92ce5d0b40cc7 (mean_reversion strategy
    'bollinger_zscore_reversion') DSL from recovered raw_payloads.

    Used by Phase 0 engine tests as the canonical exemplar.
    """
    from strategies.dsl import StrategyDSL

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
def dsl_monday_dip_buy():
    """Load cohort_a candidate 8a2a8f73f71a835e (calendar_effect strategy
    'monday_dip_buy_calendar_effect') DSL from combined synthetic dir at
    position 873. Used as second exemplar for boundary-case tests."""
    from scripts.run_phase2c_evaluation_gate import _load_dsl_from_response
    return _load_dsl_from_response("phase2c_15_main_fire_combined", 873)


@pytest.fixture
def env_config_override_forward_2026() -> dict:
    """B-C-narrow Phase 0 F1 fix: env_config override for forward_2026 regime.

    Required because environments.yaml line 127 declares
    `evaluation_regimes.forward_2026.end: null` (captured at fire-time per
    PHASE4_PLAN §1.2). Engine at backtest/engine.py:2371 calls
    `date.fromisoformat(block["end"])` which crashes with TypeError when None.

    Producer at scripts/run_phase2c_evaluation_gate.py:187-233 (_build_phase4_env_config_override)
    uses identical workaround pattern: pre-fills `forward_2026.end` with
    captured fire-time value before calling run_regime_holdout(..., env_config=<override>, ...).

    Tests adopt same pattern: pass `env_config=env_config_override_forward_2026`
    to every run_regime_holdout(regime_key="evaluation_regimes.forward_2026", ...)
    call. Canonical fire-time `end` value matches original artifact's
    forward_window_end_utc: 2026-04-16T07:00:00Z.
    """
    import yaml
    env_config_path = REPO_ROOT / "config" / "environments.yaml"
    env_config = yaml.safe_load(env_config_path.read_text())
    er = env_config.get("evaluation_regimes", {})
    fwd = er.get("forward_2026")
    if fwd is None:
        raise RuntimeError(
            "forward_2026 block missing from environments.yaml — "
            "expected at config/environments.yaml evaluation_regimes.forward_2026"
        )
    # Fill the null end with canonical fire-time value (matches original
    # artifact's forward_window_end_utc: 2026-04-16T07:00:00Z).
    fwd["end"] = "2026-04-16"
    return env_config
```

- [ ] **Step 1.2: Append `TestBCNarrowPhase0EngineExtension` to `tests/test_t1_1_artifact_writer.py`**

Add the following test class. Each test body is FULL runnable code — no placeholders, no `# similar to above`, no comment-only methods.

```python
# tests/test_t1_1_artifact_writer.py — APPEND at end (before any trailing teardowns)

import inspect
from dataclasses import fields
from pathlib import Path

import pandas as pd
import pytest


class TestBCNarrowPhase0EngineExtension:
    """Phase 0 engine extension tests per Approach D' + LC-b 4-kwarg lock.

    Locked decisions (per spec §3.1-§3.4 + plan v3-Phase0):
    - RegimeHoldoutResult extends with equity_curve: pd.Series field (12 total)
    - run_regime_holdout signature adds 4 LC-b kwargs (NOT 5;cost_anchor_id
      DERIVED in LC __post_init__ per artifact_schema.py:298-302)
    - lcb_active = (artifact_dir is not None) — single-gate precondition
    - Engine constructs LineageContext internally + relies on _write_to_registry
      at engine.py:1149 for SYS5 revalidate_for_write invariant (no
      double-invocation at engine-side)
    - Engine resolves canonical parquet path when parquet_path is None
    - Engine raises informative error if get_git_commit() returns None or
      hypothesis_hash is None at LC-b path
    """

    @pytest.fixture(autouse=True)
    def _isolate_results_dir(self, tmp_path, monkeypatch):
        """PFR R3 HIGH H1-C fix (v3.3): hermetic isolation from canonical
        data/results/.

        run_regime_holdout → run_backtest → _save_trade_csv writes
        trade CSVs to backtest.engine.RESULTS_DIR at engine.py:830
        (`RESULTS_DIR.mkdir(...); csv_path = RESULTS_DIR / f"trades_{run_id}.csv"`).
        Without isolation, every successful Phase 0 test pollutes the repo's
        canonical data/results/ directory.

        Established precedent: tests/test_t1_4_backward_compat.py:921 +
        tests/test_t1_5_smoke_end_to_end.py:403 + tests/test_t1_5_smoke_end_to_end.py:570
        all monkeypatch this exact attribute for hermetic isolation. Reusing the
        pattern with `autouse=True` so every test in this class gets isolation
        by default.

        Note on pytest scoping: pytest's `tmp_path` fixture is FUNCTION-scoped
        (one fresh path per test). This autouse fixture inherits the default
        function scope, so the `tmp_path` here is the SAME per-test instance
        passed to each test method's `tmp_path` parameter. `results_dir` lives
        as a sibling of the per-test `db_path` / `artifact_dir` under one
        common tmp_path root — pytest auto-cleans the whole tree post-test.
        """
        results_dir = tmp_path / "results"
        results_dir.mkdir(exist_ok=True)
        monkeypatch.setattr("backtest.engine.RESULTS_DIR", results_dir)

    # ----- Dataclass shape test (1) — merged per PFR R3 MEDIUM M2-A + LOW L1 -----

    def test_regime_holdout_result_dataclass_exact_field_set(self):
        """PFR R3 MEDIUM M2-A + LOW L1 fix (v3.3): replaces two prior tests
        (`_exposes_equity_curve_field` + `_dataclass_field_count_12`) with a
        single set-equality assertion.

        Prior approach (count==12 + presence-of-equity_curve) was silent on
        field-set regressions (e.g., remove field 11, add unrelated field 12 →
        count stays 12; advisor M2-A). Set-equality catches both add AND remove
        regressions at the exact 12-field contract per spec §3.1.1 + B-C-narrow
        Phase 0 extension."""
        from backtest.engine import RegimeHoldoutResult
        expected = {
            "run_id",
            "parent_run_id",
            "batch_id",
            "hypothesis_hash",
            "regime_holdout_passed",
            "sharpe_ratio",
            "max_drawdown",
            "total_return",
            "total_trades",
            "passing_criteria",
            "metrics",
            "equity_curve",  # B-C-narrow Phase 0 12th field
        }
        actual = {f.name for f in fields(RegimeHoldoutResult)}
        assert actual == expected, (
            f"RegimeHoldoutResult field set drift:\n"
            f"  Missing: {sorted(expected - actual)}\n"
            f"  Extra:   {sorted(actual - expected)}\n"
            f"  Actual:  {sorted(actual)}\n"
            f"  Expected (12 fields): {sorted(expected)}"
        )

    # ----- Signature tests (2) -----

    def test_run_regime_holdout_signature_includes_4_lcb_kwargs(self):
        """4 LC-b kwargs (NOT 5) — cost_anchor_id derived in LC __post_init__."""
        from backtest.engine import run_regime_holdout
        sig = inspect.signature(run_regime_holdout)
        params = sig.parameters
        required = {
            "run_id_override",
            "source_batch_id",
            "parent_run_id_override",
            "artifact_dir",
        }
        missing = required - set(params.keys())
        assert not missing, f"missing LC-b kwargs: {missing}"
        for kw in required:
            assert params[kw].default is None, (
                f"LC-b kwarg '{kw}' must default to None (backward-compat);"
                f" got default={params[kw].default!r}"
            )

    def test_run_regime_holdout_signature_does_not_include_cost_anchor_id(self):
        """cost_anchor_id MUST NOT be a kwarg per artifact_schema.py:298-302 invariant."""
        from backtest.engine import run_regime_holdout
        sig = inspect.signature(run_regime_holdout)
        assert "cost_anchor_id" not in sig.parameters, (
            "cost_anchor_id MUST NOT be a run_regime_holdout kwarg per spec §3.4 "
            "LC-b 4-kwarg lock. LC __post_init__ derives via COST_ANCHOR_ID_MAPPING."
        )

    # ----- Equity curve population test (1) -----

    def test_run_regime_holdout_returns_result_with_equity_curve_populated(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path,
        env_config_override_forward_2026,
    ):
        """result.equity_curve must be non-empty pd.Series (naive index — Backtrader-native;
        UTC localization deferred to consumer per engine.py:514-518)."""
        from backtest.engine import run_regime_holdout
        result = run_regime_holdout(
            dsl=dsl_bollinger_zscore_reversion,
            batch_id="test-bc",
            parent_run_id="test-parent",
            regime_key="evaluation_regimes.forward_2026",
            parquet_path=str(btc_parquet_path),
            db_path=tmp_path / "test_eq_curve.db",
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
            env_config=env_config_override_forward_2026,
        )
        assert isinstance(result.equity_curve, pd.Series)
        assert len(result.equity_curve) > 0, (
            "equity_curve must be non-empty (forward_2026 = ~2528 hourly bars)"
        )
        # F7: BacktestResult.equity_curve produced by Backtrader has NAIVE index
        # (Backtrader's data.datetime.datetime(0) returns naive datetime per engine.py:312).
        # UTC localization happens in write_per_bar_artifact at engine.py:514-518.
        # Therefore tz-aware verification belongs at the parquet-file level (covered by
        # G4 in Plan v3-Phase3-4), NOT at result.equity_curve level. Just verify the
        # series is datetime-indexed here.
        assert pd.api.types.is_datetime64_any_dtype(result.equity_curve.index), (
            "equity_curve must have datetime-typed index "
            "(tz-awareness validated downstream at parquet write per engine.py:514-518)"
        )
        # PFR R3 MEDIUM M3-A fix (v3.3): semantic check on equity_curve content.
        # The prior assertions catch shape/type but are silent on garbage data
        # (e.g., engine populates equity_curve with raw closes, returns, or NaNs
        # instead of portfolio values). Portfolio value is monetary and must be
        # strictly positive at every bar (default initial cash = 100000; bankruptcy
        # to <=0 would have other engine-level guards). This catches the
        # "tests pass for the wrong reason" failure mode where engine returns a
        # populated-but-semantically-wrong equity_curve.
        assert (result.equity_curve > 0).all(), (
            f"equity_curve must be strictly positive at every bar (portfolio value); "
            f"got min={result.equity_curve.min()}, "
            f"first_value={result.equity_curve.iloc[0]}, "
            f"last_value={result.equity_curve.iloc[-1]}. Likely engine populated "
            f"with returns/closes instead of values, or strategy collapsed below "
            f"zero (which should fail the regime_holdout pass criteria upstream)."
        )

    # ----- LC-b internal construction test (all 14 LC fields asserted) -----

    def test_run_regime_holdout_lcb_constructs_lineage_context_with_all_14_fields(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path,
        env_config_override_forward_2026,
    ):
        """When LC-b path active (artifact_dir provided), engine constructs LC
        internally with all 14 fields populated correctly + stamps registry row."""
        from backtest.engine import run_regime_holdout
        from backtest.experiment_registry import get_connection

        db_path = tmp_path / "test_lcb_14_fields.db"
        artifact_dir = tmp_path / "test_lcb_artifact"
        run_id = "test_lcb_14fields_001"

        result = run_regime_holdout(
            dsl=dsl_bollinger_zscore_reversion,
            batch_id="test-source-batch-lcb",
            parent_run_id="test-parent-positional",
            regime_key="evaluation_regimes.forward_2026",
            parquet_path=str(btc_parquet_path),
            db_path=db_path,
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
            env_config=env_config_override_forward_2026,
            # 4 LC-b kwargs (cost_anchor_id NOT passed):
            run_id_override=run_id,
            source_batch_id="test-source-batch-lcb",
            parent_run_id_override="test-parent-override",
            artifact_dir=artifact_dir,
        )

        # Read registry row + assert all relevant LC fields populated
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

        (rid, hh, bid, prid, rkey, csha, ecp, ecsha, psha, cai,
         rpbp, rpbsha, tobs) = row

        # Per-field assertions (all 14 LC fields — Charlie no敷衍 requirement)
        assert rid == run_id, f"run_id mismatch: {rid}"
        # CONTRACT BOUNDARY (per PFR R2 LOW F2): the engine's hypothesis_hash
        # field stores the full 64-char SHA256 hex from strategies.dsl.compute_dsl_hash
        # (D2 compilation-manifest contract per strategies/dsl.py:280). This is
        # DISTINCT from agents.hypothesis_hash.hash_dsl, which returns the first 16
        # chars and is the D3 orchestrator dedup key written to batch_summary
        # (contract documented at agents/hypothesis_hash.py:154-173 +
        # tests/test_hypothesis_hash.py:325). The two hashes serve independent
        # purposes by design — D2 (compilation) vs D3 (dedup) — and both contracts
        # remain in force. This assertion is the 64-char compute_dsl_hash; the
        # 16-char hash_dsl is exercised by tests/test_hypothesis_hash.py and is
        # NOT in scope for Phase 0 engine extension.
        assert hh is not None and len(hh) == 64, f"hypothesis_hash invalid: {hh!r}"
        # PFR R4 LOW N4 (v3.4) + PFR R4 LOW L1 (v3.5): hex-shape + lowercase
        # strictness. int(..., 16) catches non-hex characters; .lower() check
        # catches uppercase regressions (hashlib.sha256.hexdigest() contract
        # is lowercase per strategies/dsl.py:280 compute_dsl_hash).
        int(hh, 16)
        assert hh == hh.lower(), f"hypothesis_hash must be lowercase hex: {hh!r}"
        # batch_id column at registry = LC.source_batch_id field per
        # artifact_schema.py:261 ("aliases registry runs.batch_id")
        assert bid == "test-source-batch-lcb"
        assert prid == "test-parent-override"
        assert rkey == "evaluation_regimes.forward_2026"
        # F4 (Codex P0-LC14 + advisor HIGH-γ): explicit engine_commit field assertion.
        # Per engine.py:1314, lc.engine_commit OVERRIDE-writes to runs.git_commit column.
        # Use explicit field equality instead of brittle substring containment.
        from backtest.experiment_registry import get_run
        with get_connection(db_path) as conn:
            run_dict = get_run(conn, run_id)
        assert run_dict is not None, f"get_run returned None for run_id={run_id}"
        assert run_dict.get("git_commit") == "eb1c87f", (
            f"engine_commit=CORRECTED_WF_ENGINE_COMMIT='eb1c87f' (wf_lineage.py:71) "
            f"must be stamped into registry.git_commit column via lc.engine_commit "
            f"OVERRIDE at engine.py:1314; got {run_dict.get('git_commit')!r}"
        )
        assert csha is not None and len(csha) >= 7, "current_git_sha empty"
        assert "execution_phase4_15bps.yaml" in (ecp or ""), (
            f"execution_config_path missing: {ecp!r}"
        )
        # PFR R4 LOW N4 (v3.4) + PFR R4 LOW L1 (v3.5): hex-shape + lowercase
        # strictness checks alongside length-64. SHA256 contract per
        # hashlib.sha256.hexdigest() is 64 lowercase hex digits.
        assert ecsha is not None and len(ecsha) == 64
        int(ecsha, 16)  # ValueError on non-hex char
        assert ecsha == ecsha.lower(), f"execution_config_sha256 must be lowercase: {ecsha!r}"
        assert psha is not None and len(psha) == 64
        int(psha, 16)
        assert psha == psha.lower(), f"parquet_data_sha256 must be lowercase: {psha!r}"
        # cost_anchor_id DERIVED by LC __post_init__ (NOT passed)
        assert cai == "phase4_forward_15bps_v1", (
            f"cost_anchor_id derivation failed: {cai!r}"
        )
        assert rpbp is not None and rpbp != "", f"returns_per_bar_path empty: {rpbp!r}"
        assert rpbsha is not None and len(rpbsha) == 64
        int(rpbsha, 16)
        assert rpbsha == rpbsha.lower(), f"returns_per_bar_sha256 must be lowercase: {rpbsha!r}"
        assert tobs is not None and tobs > 0, f"T_obs invalid: {tobs!r}"

        # Verify per-bar parquet file exists
        parquet_file = artifact_dir / "returns_per_bar.parquet"
        assert parquet_file.exists(), f"per-bar parquet missing at {parquet_file}"

    # ----- Call-order test (write_per_bar_artifact BEFORE _write_to_registry) -----

    def test_run_regime_holdout_writes_artifact_before_registry(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path, monkeypatch,
        env_config_override_forward_2026,
    ):
        """Verify atomicity invariant per spec §3.1.2 — write_per_bar_artifact
        MUST be called before _write_to_registry (so registry row references
        the just-written artifact path + SHA atomically).

        PFR R3 LOW L4 note (v3.3): this test verifies call-ORDER given both
        wrapped functions succeed. If either raises (e.g., disk write fails,
        registry write conflict fires), the exception propagates uncaught and
        the test errors out — acceptable secondary failure mode (the registered
        order-violation is impossible without both calls running)."""
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
            # PFR R3 BLOCKING B1 fix (v3.3): batch_id and source_batch_id MUST match
            # when both are non-None per _write_to_registry conflict guard at
            # backtest/engine.py:1094-1108 (raise ValueError if disagree). LC.source_batch_id
            # aliases registry runs.batch_id; values must be consistent.
            batch_id="test-co-bsi",
            parent_run_id="test-parent-co",
            regime_key="evaluation_regimes.forward_2026",
            parquet_path=str(btc_parquet_path),
            db_path=tmp_path / "test_call_order.db",
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
            env_config=env_config_override_forward_2026,
            run_id_override="test_co_001",
            source_batch_id="test-co-bsi",
            parent_run_id_override="test-parent-override",
            artifact_dir=tmp_path / "artifact_co",
        )

        assert "write_per_bar_artifact" in call_order
        assert "_write_to_registry" in call_order
        artifact_idx = call_order.index("write_per_bar_artifact")
        registry_idx = call_order.index("_write_to_registry")
        assert artifact_idx < registry_idx, (
            f"BLOCKING: write_per_bar_artifact must be BEFORE _write_to_registry. "
            f"Actual order: {call_order}"
        )

    # ----- Backward-compat test -----

    def test_run_regime_holdout_backward_compat_no_lcb_kwargs(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path,
        env_config_override_forward_2026,
    ):
        """Legacy callers (no LC-b kwargs) get unchanged behavior; equity_curve
        always populated (regardless of LC-b path).

        NOTE on env_config kwarg: env_config is an existing pre-Phase-0 engine kwarg
        (engine.py:2286), NOT one of the 4 new LC-b kwargs. Passing it preserves
        legacy semantics — the override is required because environments.yaml
        has forward_2026.end:null at this register (fire-time captured); without
        the override the engine TypeErrors on date.fromisoformat(None). The "no
        LC-b kwargs" assertion of this test refers to run_id_override /
        source_batch_id / parent_run_id_override / artifact_dir — none passed."""
        from backtest.engine import run_regime_holdout
        result = run_regime_holdout(
            dsl=dsl_bollinger_zscore_reversion,
            batch_id="test-legacy",
            parent_run_id="test-parent-legacy",
            regime_key="evaluation_regimes.forward_2026",
            parquet_path=str(btc_parquet_path),
            db_path=tmp_path / "test_legacy.db",
            env_config=env_config_override_forward_2026,
        )
        assert result.run_id is not None
        assert result.hypothesis_hash is not None and len(result.hypothesis_hash) == 64
        int(result.hypothesis_hash, 16)
        assert result.hypothesis_hash == result.hypothesis_hash.lower(), (
            f"hypothesis_hash must be lowercase: {result.hypothesis_hash!r}"
        )
        assert result.total_trades >= 0
        assert result.equity_curve is not None
        assert len(result.equity_curve) > 0

    # ----- Boundary case tests -----

    def test_run_regime_holdout_lcb_empty_run_id_override_fails_closed(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path,
        env_config_override_forward_2026,
    ):
        """LC.run_id is STRICT non-empty; empty run_id_override FAILS CLOSED in
        preflight per N1 v3.4 hoist (BEFORE run_backtest).

        PFR R4 MEDIUM M1 fix (v3.5): use `match=` parameter to pin the raise
        to PREFLIGHT specifically. Without match=, a broad `(ValueError,
        RuntimeError)` would pass even if a future implementation regression
        moved the empty-string check post-run_backtest (e.g., back to LC
        __post_init__). The match string is the unique substring of the
        preflight error message — see engine body N1 fix at line ~1014."""
        from backtest.engine import run_regime_holdout
        with pytest.raises(
            ValueError,
            match=r"run_id_override must be non-empty if provided at LC-b path",
        ):
            run_regime_holdout(
                dsl=dsl_bollinger_zscore_reversion,
                batch_id="test-bc", parent_run_id="test-parent",
                regime_key="evaluation_regimes.forward_2026",
                parquet_path=str(btc_parquet_path),
                db_path=tmp_path / "test_empty_rid.db",
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                env_config=env_config_override_forward_2026,
                run_id_override="",  # invalid empty
                source_batch_id="test-bsi",
                parent_run_id_override="test-prio",
                artifact_dir=tmp_path / "artifact_empty",
            )

    def test_run_regime_holdout_lcb_empty_source_batch_id_fails_closed(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path,
        env_config_override_forward_2026,
    ):
        """LC.source_batch_id STRICT; empty FAIL CLOSED in preflight per N1 v3.4.

        PFR R4 MEDIUM M1 fix (v3.5): pin to preflight via match= parameter
        (same rationale as test_lcb_empty_run_id_override). See N1 hoist at
        engine body line ~1020."""
        from backtest.engine import run_regime_holdout
        with pytest.raises(
            ValueError,
            match=r"source_batch_id must be non-empty if provided at LC-b path",
        ):
            run_regime_holdout(
                dsl=dsl_bollinger_zscore_reversion,
                batch_id="test-bc", parent_run_id="test-parent",
                regime_key="evaluation_regimes.forward_2026",
                parquet_path=str(btc_parquet_path),
                db_path=tmp_path / "test_empty_sbi.db",
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                env_config=env_config_override_forward_2026,
                run_id_override="test-rid-valid",
                source_batch_id="",
                parent_run_id_override="test-prio",
                artifact_dir=tmp_path / "artifact_empty_sbi",
            )

    def test_run_regime_holdout_lcb_invalid_artifact_dir_propagates(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path,
        env_config_override_forward_2026,
    ):
        """Invalid/unwritable artifact_dir propagates error cleanly."""
        from backtest.engine import run_regime_holdout
        with pytest.raises((OSError, PermissionError, RuntimeError)):
            run_regime_holdout(
                dsl=dsl_bollinger_zscore_reversion,
                batch_id="test-bc", parent_run_id="test-parent",
                regime_key="evaluation_regimes.forward_2026",
                parquet_path=str(btc_parquet_path),
                db_path=tmp_path / "test_bad_dir.db",
                execution_config_path=Path("config/execution_phase4_15bps.yaml"),
                env_config=env_config_override_forward_2026,
                run_id_override="test-rid", source_batch_id="test-bsi",
                parent_run_id_override="test-prio",
                artifact_dir=Path("/nonexistent/no_permission/dir"),
            )

    def test_run_regime_holdout_lcb_missing_execution_config_path_fails(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path,
        env_config_override_forward_2026,
    ):
        """LC-b path requires execution_config_path for cost_anchor_id derivation;
        None → LC __post_init__ COST_ANCHOR_ID_MAPPING lookup fails closed."""
        from backtest.engine import run_regime_holdout
        with pytest.raises((ValueError, KeyError, RuntimeError)):
            run_regime_holdout(
                dsl=dsl_bollinger_zscore_reversion,
                batch_id="test-bc", parent_run_id="test-parent",
                regime_key="evaluation_regimes.forward_2026",
                parquet_path=str(btc_parquet_path),
                db_path=tmp_path / "test_no_cfg.db",
                execution_config_path=None,  # missing required
                env_config=env_config_override_forward_2026,
                run_id_override="test-rid", source_batch_id="test-bsi",
                parent_run_id_override="test-prio",
                artifact_dir=tmp_path / "artifact_no_cfg",
            )

    def test_run_regime_holdout_lcb_artifact_dir_none_disables_lcb_path(
        self, dsl_bollinger_zscore_reversion, btc_parquet_path, tmp_path,
        env_config_override_forward_2026,
    ):
        """Per D-N2 fix: lcb_active = (artifact_dir is not None) — single gate.
        Other LC-b kwargs set but artifact_dir=None → LC-b path NOT activated;
        legacy path taken; no error.

        PFR R3 HIGH H1-A fix (v3.3): this test originally checked only
        `result.run_id != "test-rid"` — a weak gate silent on source_batch_id
        and parent_run_id_override leaking in the legacy path. Hardened to
        ALSO assert registry row uses the POSITIONAL batch_id + parent_run_id
        (not the LC-b override values). Per advisor: a v1.x regression that
        re-introduced unconditional honoring of source_batch_id or
        parent_run_id_override in legacy path would have slipped through
        the original 1-assertion gate."""
        from backtest.engine import run_regime_holdout
        from backtest.experiment_registry import get_connection

        db_path = tmp_path / "test_artifact_none.db"
        result = run_regime_holdout(
            dsl=dsl_bollinger_zscore_reversion,
            batch_id="test-bc", parent_run_id="test-parent",
            regime_key="evaluation_regimes.forward_2026",
            parquet_path=str(btc_parquet_path),
            db_path=db_path,
            env_config=env_config_override_forward_2026,
            run_id_override="test-rid",  # set but ignored without artifact_dir
            source_batch_id="test-bsi",  # set but ignored without artifact_dir
            parent_run_id_override="test-prio",  # set but ignored without artifact_dir
            artifact_dir=None,  # primary gate — LC-b NOT activated
        )
        # Legacy path taken — result.run_id is the engine-minted UUID, NOT override
        assert result.run_id != "test-rid", (
            f"Without artifact_dir, run_id_override must NOT be honored "
            f"(legacy path); got result.run_id={result.run_id}"
        )
        assert result.equity_curve is not None  # always populated regardless

        # H1-A hardening: verify registry row reflects POSITIONAL values, NOT overrides.
        # This catches sibling-leak regressions where source_batch_id or
        # parent_run_id_override would inadvertently be honored in legacy path.
        with get_connection(db_path) as conn:
            row = conn.execute(
                "SELECT batch_id, parent_run_id FROM runs WHERE run_id = ?",
                (result.run_id,),
            ).fetchone()
        assert row is not None, (
            f"Registry row missing for run_id={result.run_id!r}"
        )
        assert row[0] == "test-bc", (
            f"Legacy path must use POSITIONAL batch_id 'test-bc', NOT the "
            f"source_batch_id override 'test-bsi'; got row.batch_id={row[0]!r}"
        )
        assert row[1] == "test-parent", (
            f"Legacy path must use POSITIONAL parent_run_id 'test-parent', NOT "
            f"the parent_run_id_override 'test-prio'; got row.parent_run_id={row[1]!r}"
        )

    def test_run_regime_holdout_lcb_resolves_canonical_parquet_when_none(
        self, dsl_bollinger_zscore_reversion, tmp_path,
        env_config_override_forward_2026,
    ):
        """Per BLOCKING-2 fix: when parquet_path=None in LC-b path, engine
        resolves canonical default (data/raw/btcusdt_1h.parquet) for
        parquet_data_sha256 LC field."""
        from backtest.engine import run_regime_holdout
        from backtest.experiment_registry import get_connection

        db_path = tmp_path / "test_canonical_parquet.db"
        artifact_dir = tmp_path / "artifact_canonical"
        run_id = "test_canonical_001"

        result = run_regime_holdout(
            dsl=dsl_bollinger_zscore_reversion,
            # PFR R3 BLOCKING B1 fix (v3.3): batch_id matches source_batch_id per
            # _write_to_registry conflict guard at backtest/engine.py:1094-1108.
            batch_id="test-canon-bsi", parent_run_id="test-parent",
            regime_key="evaluation_regimes.forward_2026",
            parquet_path=None,  # NOT passed — engine resolves canonical
            db_path=db_path,
            execution_config_path=Path("config/execution_phase4_15bps.yaml"),
            env_config=env_config_override_forward_2026,
            run_id_override=run_id, source_batch_id="test-canon-bsi",
            parent_run_id_override="test-prio", artifact_dir=artifact_dir,
        )

        # Verify registry row has non-empty parquet_data_sha256
        with get_connection(db_path) as conn:
            row = conn.execute(
                "SELECT parquet_data_sha256 FROM runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        assert row is not None
        assert row[0] is not None and len(row[0]) == 64, (
            f"parquet_data_sha256 must be populated from canonical default "
            f"(data/raw/btcusdt_1h.parquet) when parquet_path=None; "
            f"got {row[0]!r}"
        )
        int(row[0], 16)  # PFR R4 LOW N4 (v3.4): hex-shape check on parquet_data_sha256
        assert row[0] == row[0].lower(), (
            f"parquet_data_sha256 must be lowercase: {row[0]!r}"
        )
```

- [ ] **Step 1.3: Update existing RegimeHoldoutResult test stubs**

PFR R3 MEDIUM M1 fix (v3.3): the original Step 1.3 had a soft parenthetical
about ensuring `import pandas as pd`. Empirical: NEITHER stub file has a
module-level `import pandas as pd` — `test_phase2c_evaluation_gate_runner.py`
imports only `pathlib.Path` + `pytest` at top; `test_t1_4_backward_compat.py`
has an inline `import pandas as pd` at line 1008 (inside a method, not module
scope). Adding `equity_curve=pd.Series(dtype=float)` without first adding the
module-level import will cause `NameError` at test collection time, taking
down the entire test module. Explicit two-step procedure for EACH file:

- [ ] **Step 1.3a (for both files): verify or add module-level `import pandas as pd`**

```bash
# For tests/test_phase2c_evaluation_gate_runner.py:
grep -E "^import pandas|^import pandas as pd" tests/test_phase2c_evaluation_gate_runner.py
# If empty → add `import pandas as pd` at the top of the imports block.
# Same check for tests/test_t1_4_backward_compat.py:
grep -E "^import pandas|^import pandas as pd" tests/test_t1_4_backward_compat.py
# If empty → add `import pandas as pd` at the top of the imports block.
```

- [ ] **Step 1.3b: append `equity_curve=pd.Series(dtype=float)` arg to each stub**

Edit `tests/test_phase2c_evaluation_gate_runner.py:83` — find existing
`return RegimeHoldoutResult(...)` call. Add `equity_curve=pd.Series(dtype=float)`
as the final kwarg.

Same edit at `tests/test_t1_4_backward_compat.py:1384`.

- [ ] **Step 1.4: Run all 13 new tests — they must FAIL (RED)**

```bash
cd /Users/yutianyang/Documents/GitHub/btc-alpha-pipeline
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension -v
```

Expected: most tests FAIL with `AttributeError: 'RegimeHoldoutResult' has no field 'equity_curve'` or `TypeError: run_regime_holdout() got an unexpected keyword argument 'run_id_override'`. The negative-existence test `test_run_regime_holdout_signature_does_not_include_cost_anchor_id` may PASS at this stage (correct for RED-phase negative assertion).

- [ ] **Step 1.5: Commit failing tests + fixtures**

```bash
git add tests/conftest.py tests/test_t1_1_artifact_writer.py \
        tests/test_phase2c_evaluation_gate_runner.py tests/test_t1_4_backward_compat.py
git commit -m "test(b-c-narrow/phase-0): add 13 failing engine-extension tests + shared fixtures (T1)

Per Plan v3-Phase0 Task 1. RED-phase tests verify (post-implementation):
- RegimeHoldoutResult dataclass 12 fields (incl. equity_curve)
- run_regime_holdout signature 4 LC-b kwargs (NOT 5; cost_anchor_id derived)
- Negative: cost_anchor_id NOT in signature
- equity_curve populated (naive index per Backtrader; UTC localization deferred to write_per_bar_artifact at engine.py:514-518)
- LC-b internal construction with all 14 LC fields stamped at registry row
  (explicit engine_commit assertion per Codex R2 HIGH; cost_anchor_id derivation)
- write_per_bar_artifact BEFORE _write_to_registry call-order
- Backward-compat: legacy callers unaffected
- Boundary cases: empty run_id_override, empty source_batch_id, invalid artifact_dir,
  missing execution_config_path, artifact_dir=None single-gate, canonical parquet path

Shared fixtures (btc_parquet_path + dsl_bollinger_zscore_reversion +
dsl_monday_dip_buy) at tests/conftest.py loading from recovered raw_payloads.

Existing test stubs at tests/test_phase2c_evaluation_gate_runner.py:83 +
tests/test_t1_4_backward_compat.py:1384 add equity_curve=pd.Series(dtype=float)
for backward-compat. All 13 tests FAIL at this commit (RED phase). T2/T3/T4
implement engine changes to bring GREEN."
```

---

### Task 2: Extend RegimeHoldoutResult dataclass

**Files:**
- Modify: `backtest/engine.py` lines 2044-2063

- [ ] **Step 2.1: Add `equity_curve: pd.Series` field**

Edit `backtest/engine.py` lines 2044-2063. Append `equity_curve: pd.Series` as the 12th field at the end:

```python
@dataclass
class RegimeHoldoutResult:
    """[existing docstring]

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
    equity_curve: pd.Series  # B-C-narrow Phase 0
```

- [ ] **Step 2.2: Run shape test + full suite zero-regression**

PFR R3 v3.3: post M2-A + L1 merger, the prior 2 shape tests
(`_exposes_equity_curve_field` + `_dataclass_field_count_12`) are folded into
a single `test_regime_holdout_result_dataclass_exact_field_set` set-equality test.

```bash
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension::test_regime_holdout_result_dataclass_exact_field_set -v
python -m pytest -q
```

Expected: 1 PASS; full suite zero regression.

- [ ] **Step 2.3: Commit**

```bash
git add backtest/engine.py
git commit -m "feat(b-c-narrow/phase-0): add RegimeHoldoutResult.equity_curve field (T2)

12th field on RegimeHoldoutResult per Approach D' Phase 0 + LC-b 4-kwarg lock.
Existing test stubs already updated at T1 commit with equity_curve= arg."
```

---

### Task 3: Add 4 LC-b kwargs to run_regime_holdout signature

**Files:**
- Modify: `backtest/engine.py` lines 2270-2291

- [ ] **Step 3.1: Add 4 kwargs after `lineage_context` at line 2290**

Edit `backtest/engine.py`. The signature currently ends at line 2290 with `lineage_context: "Any | None" = None,` followed by `) -> RegimeHoldoutResult:` at line 2291.

Add 4 NEW kwargs (cost_anchor_id INTENTIONALLY OMITTED) BEFORE the closing `)`:

```python
    lineage_context: "Any | None" = None,
    # B-C-narrow Phase 0 LC-b 4-kwarg lock (default None preserves backward compat):
    # NOTE: cost_anchor_id is INTENTIONALLY OMITTED — derived in LineageContext
    # __post_init__ from execution_config_path via COST_ANCHOR_ID_MAPPING per
    # artifact_schema.py:298-302. Callers MUST NOT pass cost_anchor_id.
    run_id_override: str | None = None,
    source_batch_id: str | None = None,
    parent_run_id_override: str | None = None,
    artifact_dir: Path | None = None,
) -> RegimeHoldoutResult:
```

- [ ] **Step 3.2: Run 2 signature tests + full suite**

```bash
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension::test_run_regime_holdout_signature_includes_4_lcb_kwargs tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension::test_run_regime_holdout_signature_does_not_include_cost_anchor_id -v
python -m pytest -q
```

Expected: 2 PASS;zero regression.

- [ ] **Step 3.3: Commit**

```bash
git add backtest/engine.py
git commit -m "feat(b-c-narrow/phase-0): add 4 LC-b kwargs to run_regime_holdout signature (T3)

4 producer-passed scalars (run_id_override + source_batch_id + parent_run_id_override
+ artifact_dir); all default None for backward-compat. cost_anchor_id INTENTIONALLY
OMITTED per artifact_schema.py:298-302 (LC __post_init__ derivation)."
```

---

### Task 4: Implement LC-b LineageContext construction body

**Files:**
- Modify: `backtest/engine.py` lines 2435-2523 + add helpers near top

**LineageContext construction pattern selected:** Per spec §3.4 a/b/c menu lock, this sub-plan selects **pattern (b) "engine-internal construction using producer-passed scalars"** (4 LC-b kwargs threaded through `run_regime_holdout`). Cleanest for atomicity (no two-phase call) + separates concerns (producer knows metadata, engine knows T_obs).

This is the most substantive Phase 0 task. Implementation order:

- [ ] **Step 4.1: Verify required imports + add helpers**

Check current engine.py top-of-file imports:

```bash
grep -n "^from backtest\|^from strategies\|^import hashlib" backtest/engine.py | head -10
```

Ensure these imports exist (add if missing):

```python
from backtest.wf_lineage import CORRECTED_WF_ENGINE_COMMIT
from backtest.artifact_schema import LineageContext
```

Add helper function `_compute_sha256_file` if not present (grep first: `grep -n "def _compute_sha256_file" backtest/engine.py`).

**Placement (per PFR R2 LOW N5):** both `_compute_sha256_file` and `_resolve_canonical_parquet_path` (defined below) MUST land immediately after `backtest/engine.py:53` — that is, in the constants block right after the existing `PROJECT_ROOT = Path(__file__).resolve().parent.parent` (engine.py:53) and `RESULTS_DIR = PROJECT_ROOT / "data" / "results"` (engine.py:54), and BEFORE any function definitions. This ordering satisfies two preconditions: (a) `_resolve_canonical_parquet_path` references `PROJECT_ROOT`, so it must come after line 53 to have the constant in scope; (b) keeping all module-level helpers grouped post-constants keeps the engine's overall structure unchanged from existing convention. Verified anchor: `grep -n "^PROJECT_ROOT\b" backtest/engine.py` → `53:PROJECT_ROOT = Path(__file__).resolve().parent.parent`.

```python
def _compute_sha256_file(file_path: Path | None) -> str | None:
    """B-C-narrow Phase 0: compute SHA256 of a file via 64KB chunked streaming.

    Returns None if file_path is None or file does not exist. Used by LC-b
    construction for execution_config_sha256 + parquet_data_sha256 fields.
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


def _resolve_canonical_parquet_path() -> Path:
    """B-C-narrow Phase 0: resolve canonical BTC parquet path used when
    LC-b caller doesn't pass parquet_path explicitly. Per spec §3.4 LC-b
    construction must produce non-empty parquet_data_sha256 (LC STRICT field).
    """
    return PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"
```

Verify `get_git_commit` is imported from `backtest.experiment_registry`:

```bash
grep -n "from backtest.experiment_registry import" backtest/engine.py
```

If `get_git_commit` not imported, add to the existing import line.

- [ ] **Step 4.2: Modify run_regime_holdout body — sequence + LC-b construction**

Read current body at engine.py lines 2435-2523. Replace the section from line 2435 (the `result = run_backtest(...)` call) through line 2523 (the closing `return RegimeHoldoutResult(...)`) with the corrected sequence:

```python
    # ---- B-C-narrow Phase 0 LC-b PREFLIGHT (PFR R3 MEDIUM M1-C + PFR R4 MEDIUM N1 fix v3.4) ----
    # Scalar LC-b precondition checks moved BEFORE run_backtest per advisor M1-C +
    # extended to ALSO cover empty-string ID overrides per advisor R4 MEDIUM-N1:
    # validating cheap scalars before launching expensive backtest prevents
    # full backtest runs + trade CSV writes on bad LC-b setups (e.g.,
    # hypothesis_hash=None, missing execution_config_path, get_git_commit() None,
    # empty-string run_id_override / source_batch_id).
    # D-N3 + D-N4 + BLOCKING-2 preconditions are hoisted; empty-string ID checks
    # are now ALSO hoisted (M1-C complete coverage; v3.3 had partial coverage).
    lcb_active = artifact_dir is not None
    git_sha: str | None = None
    if lcb_active:
        if hypothesis_hash is None:
            raise ValueError(
                "B-C-narrow LC-b precondition: hypothesis_hash must not be None at "
                "LC-b path (required for LC.hypothesis_hash STRICT field). "
                "Either provide dsl or ensure compute_dsl_hash succeeds."
            )
        git_sha = get_git_commit()
        if git_sha is None:
            raise ValueError(
                "B-C-narrow LC-b precondition: get_git_commit() returned None. "
                "Cannot construct LineageContext with empty current_git_sha "
                "(LC STRICT field). Ensure git is available + repo not in detached state."
            )
        if execution_config_path is None:
            raise ValueError(
                "B-C-narrow LC-b precondition: execution_config_path must not be None "
                "at LC-b path (required for cost_anchor_id derivation via "
                "COST_ANCHOR_ID_MAPPING per artifact_schema.py:298-302)."
            )
        # PFR R4 MEDIUM N1 fix (v3.4): hoist empty-string checks. Without these,
        # boundary tests with run_id_override="" / source_batch_id="" run full
        # backtest (~2528 bars) before LC.__post_init__ raises. Same fail-closed
        # semantics (ValueError raised either way), but ~2 minutes saved per
        # affected test at ratify time. Semantically equivalent to LC __post_init__'s
        # STRICT non-empty contract — just hoisted to preflight for efficiency.
        if run_id_override is not None and run_id_override == "":
            raise ValueError(
                "B-C-narrow LC-b precondition: run_id_override must be non-empty "
                "if provided at LC-b path (LC.run_id STRICT non-empty field). "
                "Pass None to use engine-minted UUID, or pass a non-empty string."
            )
        if source_batch_id is not None and source_batch_id == "":
            raise ValueError(
                "B-C-narrow LC-b precondition: source_batch_id must be non-empty "
                "if provided at LC-b path (LC.source_batch_id STRICT non-empty field). "
                "Pass None to inherit positional batch_id, or pass a non-empty string."
            )

    # ---- Existing: run backtest + evaluate pass (lines 2435-2446 unchanged) ----
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

    # ---- B-C-narrow Phase 0 LC-b sequence (D-N1 + D-N2 + post-preflight) ----

    # D-N2 + F3 (Codex P0-DN2 BLOCKING fix): lcb_active uses single-gate (artifact_dir is not None).
    # Effective IDs gated behind lcb_active — overrides ONLY honored on LC-b path;
    # legacy path uses engine-minted UUID + positional parent_run_id verbatim.
    # This prevents the test self-contradiction where artifact_dir=None tests assert
    # run_id_override is ignored but implementation unconditionally honored it (v3-Phase0
    # plan v1 R1 Codex catch).
    if lcb_active:
        # LC-b path: honor producer-passed overrides
        effective_run_id = run_id_override if run_id_override is not None else result.run_id
        effective_parent_run_id = (
            parent_run_id_override if parent_run_id_override is not None else parent_run_id
        )
    else:
        # Legacy path: ignore LC-b overrides; use engine-minted UUID + positional parent
        effective_run_id = result.run_id
        effective_parent_run_id = parent_run_id

    holdout_run_id = effective_run_id  # preserve alias for logging

    # LC-b: write per-bar artifact + construct LC if active
    artifact_metadata: dict[str, Any] | None = None
    lcb_lineage_context = None
    if lcb_active:
        # (Preflight scalar preconditions already verified above; git_sha already
        # resolved. effective_parquet_path resolution still happens here because it
        # depends on parquet_path arg evaluated once.)
        # Defensive narrowing: preflight raised if git_sha was None when lcb_active;
        # re-assert here to make the invariant explicit across the two if-blocks.
        assert git_sha is not None, (
            "Internal invariant violation: git_sha must be non-None inside LC-b "
            "block — the preflight `if lcb_active:` block above should have "
            "raised ValueError if get_git_commit() returned None."
        )

        # BLOCKING-2 fix: resolve canonical parquet path when None
        effective_parquet_path = (
            parquet_path if parquet_path is not None else str(_resolve_canonical_parquet_path())
        )

        # Step 3: write per-bar artifact (always BEFORE registry — atomicity invariant)
        artifact_metadata = write_per_bar_artifact(
            result.equity_curve,
            artifact_dir,
            effective_run_id,
        )

        # Step 4: construct LineageContext internally (all 13 explicit fields +
        # cost_anchor_id derived by __post_init__)
        lcb_lineage_context = LineageContext(
            run_id=effective_run_id,
            hypothesis_hash=hypothesis_hash,
            source_batch_id=(
                source_batch_id if source_batch_id is not None else batch_id
            ),
            regime_key=regime_key,
            engine_commit=CORRECTED_WF_ENGINE_COMMIT,
            current_git_sha=git_sha,
            execution_config_path=str(execution_config_path),
            execution_config_sha256=_compute_sha256_file(execution_config_path) or "",
            parquet_data_sha256=_compute_sha256_file(effective_parquet_path) or "",
            # cost_anchor_id OMITTED — uses default sentinel; __post_init__ derives.
            returns_per_bar_path=artifact_metadata["returns_per_bar_path"],
            returns_per_bar_sha256=artifact_metadata["returns_per_bar_sha256"],
            T_obs=artifact_metadata["T_obs"],
            parent_run_id=effective_parent_run_id,
        )
        # D-N1: do NOT explicitly call revalidate_for_write() here —
        # _write_to_registry at engine.py:1149 invokes it as part of T1.1 SYS5 invariant.

    # ---- Existing: cost_model + notes_payload (unchanged) ----
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

    # ---- Registry write: use engine-built LC if LC-b active, else producer-passed LC ----
    effective_lineage_context = lcb_lineage_context if lcb_active else lineage_context

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
        equity_curve=result.equity_curve,  # B-C-narrow Phase 0
    )
```

- [ ] **Step 4.3: Run all 13 Phase 0 tests — must PASS (GREEN)**

```bash
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension -v
```

Expected: 13/13 PASS.

- [ ] **Step 4.4: Full test suite zero-regression**

```bash
python -m pytest -q
```

PFR R3 LOW L3 fix (v3.3): Expected: zero regression vs pre-Phase-0 baseline +
13 net new passing. Avoid hard-coding absolute test counts (the pre-Phase-0
baseline may drift due to other concurrent work outside this Phase 0 scope;
the binding contract is zero regression + the 13 new tests passing).

- [ ] **Step 4.5: Commit**

```bash
git add backtest/engine.py
git commit -m "feat(b-c-narrow/phase-0): implement LC-b LineageContext construction in run_regime_holdout (T4)

Per Approach D' LC-b 4-kwarg lock + spec §3.1.2 5-step sequence + all
Codex R2 BLOCKING/HIGH fixes within Phase 0 scope:

- D-N1: dropped engine-side revalidate_for_write() call; rely on
  _write_to_registry:1149 SYS5 invariant invocation
- D-N2: lcb_active = (artifact_dir is not None) single-gate precondition
- D-N3: explicit raise if get_git_commit() returns None
- D-N4: explicit raise if hypothesis_hash is None at LC-b path
- BLOCKING-2: engine resolves canonical parquet path when caller passes
  parquet_path=None (LC.parquet_data_sha256 STRICT non-empty)
- Engine constructs LC with all 13 explicit fields; cost_anchor_id derived
  by __post_init__ via COST_ANCHOR_ID_MAPPING
- Per-bar artifact write BEFORE _write_to_registry (atomicity invariant)
- RegimeHoldoutResult return includes equity_curve

Helpers added: _compute_sha256_file (file SHA256 chunked) +
_resolve_canonical_parquet_path (BTC parquet default).

Tests: 13/13 Phase 0 tests now GREEN. Full suite: zero regression vs pre-Phase-0 baseline + 13 net new passing."
```

---

### Task 5: Phase 0 final ratify

- [ ] **Step 5.1: Confirm 13 tests + full suite all GREEN**

```bash
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension -v
python -m pytest -q
```

- [ ] **Step 5.2: Charlie register-event #N — Phase 0 ratify before Plan v3-Phase1 drafting**

**STOP HERE.** Surface to Charlie:
- 13 Phase 0 engine-extension tests GREEN
- Full test suite zero regression vs pre-Phase-0 baseline + 13 net new passing
- Engine modifications confined to RegimeHoldoutResult dataclass + run_regime_holdout signature + run_regime_holdout body + helper functions (_compute_sha256_file + _resolve_canonical_parquet_path)
- All 7 Codex R2 BLOCKING/HIGH/MEDIUM fixes within Phase 0 scope applied: D-N1 (revalidate_for_write double-invocation drop) + D-N2 (lcb_active single-gate) + D-N3 (get_git_commit None handling) + D-N4 (hypothesis_hash None handling) + BLOCKING-2 (canonical parquet resolution for parquet_data_sha256) + HIGH (engine_commit explicit assertion) + HIGH (db_path tmp isolation)

Phase 0 sealed (at task level). Plan v3-Phase1 sub-plan drafting may start (separate Charlie register-event for that drafting authorization).

---

## DEFER items (Phase 0 scope only)

**Phase-0-internal**: NONE. All Phase 0 design decisions locked + implemented per this sub-plan.

**Phase 1+ blockers DEFERRED** to respective sub-plans per Codex BLOCKING fixes table at top (BLOCKING-1 R9 architectural flaw → v3-Phase2; BLOCKING-3 create_table → v3-Phase2; BLOCKING-4 _parse_args → v3-Phase2; BLOCKING-5 G4-G7 bodies → v3-Phase3-4; BLOCKING-6 T1.4 grep methodology → v3-Phase2). Each sub-plan requires separate Charlie register-event for drafting authorization per anti-pre-emption discipline.

---

## Execution Handoff

Plan v3-Phase0 saved to `docs/superpowers/plans/2026-05-26-b-c-narrow-phase-0-engine-extension-plan.md`.

After Plan v3-Phase0 B2 2-leg PFR returns APPROVE → use **superpowers:subagent-driven-development** per Charlie register PV3-SPLIT-BY-PHASE: dispatch fresh subagent per task with two-stage review.

After Phase 0 SEALED (Task 5 ratify) → request Charlie register-event for Plan v3-Phase1 sub-plan drafting authorization (separate fire — anti-pre-emption discipline preserved).
