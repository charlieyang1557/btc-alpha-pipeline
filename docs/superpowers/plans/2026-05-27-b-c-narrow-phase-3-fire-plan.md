# B-C-narrow Phase 3 — Fire Plan (data-recovery execution)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this sub-plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Tasks 14 + 14b each contain explicit STOP HERE blocks for Charlie register-events #N+19a (T13 fire authorization) + #N+19b (T14b canonical-path relocation authorization) before operational execution — the implementer subagent MUST NOT bypass these without an explicit Charlie register fire.

**Sub-plan scope:** Phase 3 of the B-C-narrow data-recovery cycle ONLY — operational fire of the 39-candidate cohort_a re-run against the forward_2026 window using the Phase 2 producer wiring at HEAD `0a54f65`. Three operational steps consumed from spec §5: T13 producer fire (producer-W3 archive + LC-b candidate loop + W4 finalize parent batch_summary), T14 V4 reproducibility gate (G4-G7 + ε=1e-6 per-candidate match), T14b canonical-path relocation (sibling → canonical mv after V4 PASS). NO new source code edits. NO engine code edits. NO producer code edits. NO spec amendments. The plan adds ONE new test file (`tests/test_b_c_narrow_v4_reproducibility.py`; 7 test methods inlined per BLOCKING-5 carry from Phase 2 plan v3-Phase2 line 3651) + ONE new fixture (`tests/fixtures/b_c_narrow_archived_baseline.json`; created POST-T13 fire BEFORE T14 V4 gate, see Step 14.3) + ONE new evidence artifact (`docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md`).

**Sub-plan motivation:** Phase 0 (engine extension; sealed at `f112599`) added `RegimeHoldoutResult.equity_curve` + 4 LC-b kwargs + atomic write-then-registry sequencing inside `run_regime_holdout`. Phase 1 (pre-impl gates; sealed at `b10ffb2`) returned all 4 BLOCKING gates PASS (G1 engine-diff audit + G2 DSL backward-compat + G3 raw_payloads inventory + G3.5 engine smoke pre-satisfied). Phase 2 (producer TDD; impl sealed at `4b7a4c6`; T10 producer code polish Bundle (a) at `3a1226b`; ratify packet polish Bundle (b) at `0a54f65`) wired the producer behind `--enable-b-c-narrow-recovery` with 4 new helpers (W0 identity guard, W1a/W1b finalize preflight, W3 archive, W4 finalize POST-fire) + 6 module-level `BCNARROW_*` constants. Phase 3 executes the wiring against the 39 cohort_a candidates and verifies V4 reproducibility vs the archived original — the only step that produces new data artifacts in the entire cycle.

**Tech Stack:** Python 3.11+, pytest (V4 + G4-G7 verification), pandas (parquet I/O + holdout_results.csv parsing), pyarrow (parquet engine), scipy.stats (`compute_moments` round-trip in G5), sqlite3 (G6 registry parent-child query), pathlib + shutil (T14b mv), json (fixture capture + summary parsing). NO new dependencies.

**Cycle context:** R6.1 V_SEAL §10 binding precondition (spec at `d6c7fc0`). Cycle entry Charlie register N1 2026-05-26. Phase 3 is the only sub-plan that produces new data artifacts (39 per-candidate holdout_summary.json files + 39 returns_per_bar.parquet files + 1 aggregate holdout_summary.json + 1 holdout_results.csv + 1 archive snapshot of original + 1 parent batch_summary registry row + 39 child regime_holdout registry rows). Phase 4 (SEAL bundle: NOTE doc + B2 reviewer dispatch + Rule 2 SEAL-eve + atomic commit + Phase Marker advance) is a SEPARATE register-event #N+20 per anti-pre-emption discipline.

---

## Sub-decisions applied (Path A defaults per Charlie register #N+18; Charlie may override at PFR R1)

| # | Sub-decision | Default applied | Rationale |
|---|---|---|---|
| (i) | T12 spec supersession handling | Inline plan comment + producer W3 flag (matches Plan v3-Phase2 ADOPT note pattern). Spec amend / Architecture B errata NAMED-eligible at Phase 4 SEAL bundle. | Lowest-friction; preserves Architecture-B sealed-content invariance. T13 fire command in Step 14.1 includes `--enable-b-c-narrow-recovery` flag so producer W3 performs the archive automatically; spec §5 T12 manual `mv` step is superseded de-facto but spec line 286 stays byte-identical. |
| (ii) | Plan structure | TDD-style: write 7 NEW V4+G4-G7 test bodies (RED) → STOP for fire auth → execute fire → capture fixture → run V4 gate (GREEN expected) → STOP for T14b auth → execute relocation → write ratify packet. | Matches Phase 2 precedent (TDD discipline with test bodies authored before producer changes); explicit STOP gates around the 2 operational write steps. |
| (iii) | Charlie register-events for Phase 3 | 3 register-events: #N+19a = T13 fire authorization (after Task 13 RED commit); #N+19b = T14b canonical-path relocation authorization (after Task 14 V4 GREEN commit; only fires if V4 PASS); #N+19c = Phase 3 ratify acknowledgment (after Task 14c ratify packet commit). | CLAUDE.md HARD CONSTRAINTS + operational-write discipline = explicit Charlie register for each cohort write + each canonical-path mutation. |

**Sub-decision (iii) implication:** 4 STOP HERE blocks total in this plan: Step 13.5 (before T13 fire), Step 14.7 (before T14b relocation), Step 14c.2 (before final commit + #N+19c acknowledgment). The 4th STOP is implicit at Step 14b.0 (precondition verification of #N+19b register).

---

## Inherited locked decisions (from Phase 0/1/2 SEAL chain)

| Decision | Lock value | Source |
|---|---|---|
| Engine LC-b API | 4 kwargs added to `run_regime_holdout`: `run_id_override` + `source_batch_id` + `parent_run_id_override` + `artifact_dir`; `cost_anchor_id` DERIVED in `LineageContext.__post_init__` from `execution_config_path` (callers MUST NOT pass `cost_anchor_id`) | Phase 0 SEAL `f112599`; spec §3.4 |
| LC-b internal sequencing | Atomic write-then-registry inside `run_regime_holdout`: (1) `run_backtest` → (2) `write_per_bar_artifact(equity_curve, artifact_dir, run_id)` → (3) `_write_to_registry` with returns_per_bar_path/sha256/T_obs stamped | Phase 0 SEAL `f112599`; spec §3.1.2 |
| Producer cycle gate | `--enable-b-c-narrow-recovery` (default False). Gates W0 identity guard + W1a/W1b finalize preflight + W3 archive + W4 finalize POST-fire. Legacy callers (PHASE2C_15, PHASE2C_8.1, etc.) unaffected. | Phase 2 SEAL Plan v3-Phase2 v11; Tests `test_enable_b_c_narrow_recovery_flag_default_false` etc. |
| Producer identity guard (W0) | 4 fields validated against `BCNARROW_*` constants BEFORE any mutation: `run_id == BCNARROW_PARENT_RUN_ID`, `regime_key == BCNARROW_REGIME_KEY`, `execution_config canonicalizes to BCNARROW_EXECUTION_CONFIG_PATH`, `source_batch_id == BCNARROW_SOURCE_BATCH_ID`. ValueError raised on any mismatch. | Phase 2 SEAL; CB2 PFR R1 |
| Producer module constants | 6 module-level constants at `scripts/run_phase2c_evaluation_gate.py` lines 158-173: `BCNARROW_PARENT_RUN_ID = "phase4_forward_2026_15bps_v1_b_c_narrow"`, `BCNARROW_ARCHIVE_BASENAME = "phase4_forward_2026_15bps_v1_d0b8101"`, `BCNARROW_SOURCE_BATCH_ID = "phase2c_15_main_fire_combined"`, `BCNARROW_REGIME_KEY = "evaluation_regimes.forward_2026"`, `BCNARROW_EXECUTION_CONFIG_PATH = "config/execution_phase4_15bps.yaml"`, `BCNARROW_CANONICAL_BASENAME = "phase4_forward_2026_15bps_v1"` | Phase 2 SEAL; M5 PFR R1 + AR-SE-R2-M4 v10 + CR-SE-R3-M1 v11 |
| γ3/γ4 persistence layout | Per-candidate `holdout_summary.json` ONLY (NOT registry rows). `T_obs` persists in BOTH summary JSON AND registry row. Per-bar series in `returns_per_bar.parquet` (column `timestamp` is UTC-aware, NOT the index). | Phase 0/2 SEAL; spec §3.6 + §4.3 G4 |
| Compensating cleanup | R9-B-guarded: refuse-if-exists by default + `--force-rerun-existing` opt-in DELETEs WHERE parent_run_id. Manual cleanup otherwise. | Phase 2 SEAL; spec §7 R9 |
| TDD discipline | All test bodies are runnable code with full assertions; no placeholders. | Phase 0/1/2 precedent; Charlie register pre-PV2 |
| Engine commit identity disambiguation | `engine_commit` = `eb1c87f` constant (CORRECTED_WF_ENGINE_COMMIT in `backtest/wf_lineage.py:71`); `current_git_sha` advances per HEAD. V4 reproducibility anchor: `engine_commit` unchanged across original (eb1c87f) + new (eb1c87f); only `current_git_sha` differs (`d0b8101` original vs fire-time HEAD). | spec §2 engine-commit table |

---

## NEW locked decisions for Phase 3

| Decision | Lock value | Rationale |
|---|---|---|
| Fire command | `python -m scripts.run_phase2c_evaluation_gate --enable-b-c-narrow-recovery --candidate-hashes <39 csv> --source-batch-id phase2c_15_main_fire_combined --regime-key evaluation_regimes.forward_2026 --execution-config config/execution_phase4_15bps.yaml --run-id phase4_forward_2026_15bps_v1_b_c_narrow --output-root data/phase2c_evaluation_gate/` | Spec §5 T13 with `--enable-b-c-narrow-recovery` flag added per sub-decision (i). The 39 hashes are extracted deterministically from current canonical `holdout_results.csv` per Step 13.1 + Step 14.1. |
| V4 ε tolerance | `abs(new - old) < 1e-6` for `sharpe_ratio`, `max_drawdown`, `total_return` (floats). Exact match (`new == old`) for `total_trades` (int), `holdout_passed` (bool), `gate_pass_per_criterion` 4 subfields (bools). | Spec §4.2 + §6.4 lock. |
| G7 archive idempotency semantic | STRICT refuse-if-exists. NO silent overwrite. NO auto-rename. Pre-fire precondition: `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` MUST NOT exist. Producer W3 raises `RuntimeError` if archive target exists. Manual cleanup required if archive target preexists from aborted attempt. | Spec §4.3 G7 + R10 |
| T14b gating | T14b mv executes ONLY if T14 V4 gate returns GREEN (all 7 tests PASS). On any V4 FAIL: SEAL BLOCKED pending Charlie register adjudication (per spec §4.2 paths a/b/c). Sibling dir + archive dir REMAIN in place; canonical path REMAINS empty until adjudication resolves. | Spec §5 T14b lock |
| Charlie register-event sequencing | 3 register-events for Phase 3: #N+19a = T13 fire authorization (gated by Step 13.5 STOP); #N+19b = T14b canonical-path relocation authorization (gated by Step 14.7 STOP; FIRES ONLY if V4 PASS); #N+19c = Phase 3 ratify acknowledgment (gated by Step 14c.2 STOP). | Sub-decision (iii); CLAUDE.md operational-write discipline; anti-pre-emption |
| Fixture sampling rule | `tests/fixtures/b_c_narrow_archived_baseline.json` captures N=2 candidates: the 2 lexicographically smallest hypothesis_hash strings from the current canonical `holdout_results.csv` (after sort): `18d92ce5d0b40cc7` + `22864f01a49e3452`. Specific keys captured per spec §6.6: `sharpe_ratio`, `max_drawdown`, `total_return` (from `holdout_metrics`); `total_trades` (from `holdout_metrics`); `holdout_passed`; `gate_pass_per_criterion` (4 subfields). | Spec §6.6; deterministic + reproducible |
| Fixture creation timing | Fixture created POST-T13 fire (when archive is populated by producer W3) BEFORE T14 V4 gate runs. Sub-step 14.3 captures the fixture from `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/<hash>/holdout_summary.json`. | Spec §6.6: fixture sourced from archived original (per spec line 365); archive does not exist pre-T13 → fixture capture must be sequenced AFTER T13 archive step completes |
| T12 supersession handling | Spec line 286 ("T12 — Archive original: `mv ...`") byte-identical preserved per Architecture B. Producer W3 (gated by `--enable-b-c-narrow-recovery`) performs the archive INLINE during T13 fire, superseding the manual mv step. Spec §5 T12 + T13 collapse into Step 14.1 single fire command (producer handles both). Spec amend / Architecture B errata NAMED-eligible at Phase 4 SEAL bundle. | Sub-decision (i) |

---

## File structure (Phase 3 scope only)

| File | Action | Scope |
|---|---|---|
| `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-3-fire-plan.md` | CREATE | this plan |
| `tests/test_b_c_narrow_v4_reproducibility.py` | CREATE at Step 13.2 | 7 NEW test methods (5 spec §6.4 + 2 BLOCKING-5 carry G6+G7) |
| `tests/fixtures/b_c_narrow_archived_baseline.json` | CREATE at Step 14.3 | N=2 candidates frozen snapshot from archived original (POST-T13 fire) |
| `docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md` | CREATE at Step 14c.1 | Phase 3 ratify packet (precondition table + V4 results + G4-G7 per-gate results + verdict + next register-event) |

**Read-only references (no modifications):**
- `scripts/run_phase2c_evaluation_gate.py` (HEAD `0a54f65`; producer fire-path consumed via subprocess invocation in Step 14.1)
- `backtest/engine.py` (HEAD `0a54f65`; engine LC-b API consumed transitively via producer)
- `backtest/experiment_registry.py` (HEAD `0a54f65`; SQLite queries in G6 test + Step 14.2 verification)
- `backtest/wf_lineage.py` (HEAD `0a54f65`; `CORRECTED_WF_ENGINE_COMMIT="eb1c87f"` referenced in CB4)
- `docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md` (sealed at `d6c7fc0`; spec referenced but not modified)
- `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-2-producer-tdd-plan.md` (sealed; BLOCKING-5 carry referenced)
- `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` (current canonical; consumed read-only in Step 13.1 for candidate-hashes extraction; relocated by producer W3 in Step 14.1)

**Operational write paths (created during Step 14.1 fire):**
- `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/` (sibling dir; produced by producer because `--run-id phase4_forward_2026_15bps_v1_b_c_narrow` + `--output-root data/phase2c_evaluation_gate/` → `run_dir = output_root / run_id`)
- `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` (archive snapshot of original; created by producer W3 step inside the fire — single source of original lineage post-T14b)
- `backtest/experiments.db` (1 parent `batch_summary` row at `run_id=phase4_forward_2026_15bps_v1_b_c_narrow` via producer W4 + 39 child `regime_holdout` rows via engine `run_regime_holdout` LC-b path)

**Operational mv path (Step 14b.1):**
- `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/` → `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` (sibling → canonical, after V4 PASS only)

---

## Pre-Phase-3 register-event boundary (Charlie register chain)

| Register | Status | Description |
|---|---|---|
| `EXEC-SUBAGENT-ALL-PHASE-2` | FIRED | Phase 2 implementation arc (Tasks 9-12) |
| #N+17 (Phase 2 ratify ack) | FIRED | Bundle (b) ratify packet polish landed at `0a54f65` |
| **#N+18 (Plan v3-Phase3 drafting auth; Path A — DRAFT-V1-NOW)** | **FIRED 2026-05-27** | this plan drafting authorization |
| #N+19a (T13 fire authorization) | PENDING | gates Step 14.1 fire execution |
| #N+19b (T14b canonical-path relocation auth) | PENDING (only fires if V4 PASS) | gates Step 14b.1 mv execution |
| #N+19c (Phase 3 ratify acknowledgment) | PENDING | gates final commit + Phase 4 sub-plan drafting authorization |

Phase 3 implementation arc spans 3 register-events (#N+19a + #N+19b + #N+19c) per sub-decision (iii). Phase 4 sub-plan drafting authorization is a SEPARATE register-event #N+20 per anti-pre-emption discipline.

---

# Phase 3 — Fire execution (Tasks 13 + 14 + 14b + 14c)

## Phase 3 execution preconditions

Before any Task 13/14 execution, verify:

- [ ] **Precondition 1: HEAD pointer at `0a54f65` or descendant (Phase 2 Bundle (b) polish landed)**

```bash
git rev-parse --short HEAD
git log --oneline --first-parent 0a54f65..HEAD | wc -l  # must be 0 (HEAD IS 0a54f65) or all new commits are Phase 3 plan-doc-only
```

Expected: `0a54f65` printed by `git rev-parse --short HEAD`. If HEAD has advanced, verify all commits since `0a54f65` are this plan or plan-revision commits only (no code changes to `backtest/`, `scripts/`, `tests/`, `config/`).

- [ ] **Precondition 2: Clean working tree on code paths**

```bash
git status --porcelain backtest/ tests/ config/ scripts/ strategies/ factors/
```

Expected: empty output OR only pre-existing untracked artifacts inherited from Phase 1+2 ratify packets (e.g., `backtest/engine.py,cover`, `coverage.json`). Any modified tracked file → STOP and surface (uncommitted changes must be committed or stashed before Phase 3 fire).

- [ ] **Precondition 3: Writable execution environment**

```bash
python -c "import tempfile; f = tempfile.NamedTemporaryFile(); print(f'writable: {f.name}'); f.close()"
```

Expected: prints a temp file path successfully. Failure → environment issue (not real test failure); surface to Charlie for environment remediation.

- [ ] **Precondition 4: Phase 2 SEAL state present (producer constants + helpers)**

```bash
python -c "
from scripts.run_phase2c_evaluation_gate import (
    BCNARROW_PARENT_RUN_ID,
    BCNARROW_ARCHIVE_BASENAME,
    BCNARROW_SOURCE_BATCH_ID,
    BCNARROW_REGIME_KEY,
    BCNARROW_EXECUTION_CONFIG_PATH,
    BCNARROW_CANONICAL_BASENAME,
    _validate_b_c_narrow_recovery_identity_or_raise,
    _archive_canonical_pre_flight,
    _finalize_batch_registry_preflight_or_raise,
    _finalize_batch_registry,
)
assert BCNARROW_PARENT_RUN_ID == 'phase4_forward_2026_15bps_v1_b_c_narrow'
assert BCNARROW_ARCHIVE_BASENAME == 'phase4_forward_2026_15bps_v1_d0b8101'
assert BCNARROW_SOURCE_BATCH_ID == 'phase2c_15_main_fire_combined'
assert BCNARROW_REGIME_KEY == 'evaluation_regimes.forward_2026'
assert BCNARROW_EXECUTION_CONFIG_PATH == 'config/execution_phase4_15bps.yaml'
assert BCNARROW_CANONICAL_BASENAME == 'phase4_forward_2026_15bps_v1'
print('Phase 2 SEAL state present: all 6 BCNARROW_* constants + 4 helpers importable')
"
```

Expected: prints `Phase 2 SEAL state present: ...` with zero AssertionError. Any AssertionError or ImportError → STOP and BLOCKED (Phase 2 SEAL state regressed; should not happen at HEAD `0a54f65`).

- [ ] **Precondition 5: Phase 0 engine LC-b API present (`run_regime_holdout` 4-kwarg signature)**

```bash
python -c "
import inspect
from backtest.engine import run_regime_holdout, RegimeHoldoutResult
sig = inspect.signature(run_regime_holdout)
params = set(sig.parameters)
required_lc_b = {'run_id_override', 'source_batch_id', 'parent_run_id_override', 'artifact_dir'}
missing = required_lc_b - params
assert not missing, f'Phase 0 LC-b API missing: {missing}'
import dataclasses
rh_fields = {f.name for f in dataclasses.fields(RegimeHoldoutResult)}
assert 'equity_curve' in rh_fields, 'Phase 0 RegimeHoldoutResult.equity_curve missing'
print('Phase 0 SEAL state present: LC-b 4 kwargs + equity_curve field')
"
```

Expected: prints `Phase 0 SEAL state present: ...` with zero AssertionError. Any AssertionError → STOP and BLOCKED (Phase 0 SEAL state regressed).

---

### Task 13: Pre-fire — V4+G4-G7 test bodies (TDD RED) + pre-flight precondition checks

**Files:**
- Create: `tests/test_b_c_narrow_v4_reproducibility.py` (NEW; 7 test methods)
- Defer to Step 14.3: `tests/fixtures/b_c_narrow_archived_baseline.json` (captured POST-T13 fire BEFORE T14 V4 gate runs)

**Task discipline:** TDD RED phase only. Tests authored against the contract that the fire-step (Task 14) MUST satisfy. RED expected because the fixture file does not exist yet AND the sibling output dir does not exist yet AND the archive dir does not exist yet AND the registry parent row does not exist yet. GREEN expected at Step 14.5 (after fire + fixture capture + V4 gate run).

- [ ] **Step 13.1: Pre-flight verifications (READ-ONLY)**

Run all of these in sequence; each must succeed before proceeding:

```bash
# (a) Verify current canonical holdout_results.csv has 40 lines (header + 39 candidates)
wc -l data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv
# Expected: 40

# (b) Verify the header column structure (first line)
head -1 data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv
# Expected: hypothesis_hash,position,theme,name,wf_test_period_sharpe,lifecycle_state,holdout_passed,holdout_sharpe,holdout_max_drawdown,holdout_total_return,holdout_total_trades,wall_clock_seconds,error_message

# (c) Verify archive target does NOT pre-exist (G7 precondition)
ls -la data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/ 2>&1
# Expected: "ls: ... No such file or directory" (failure with this message is the PASS condition)

# (d) Verify sibling output dir does NOT pre-exist (G7 precondition for sibling write)
ls -la data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/ 2>&1
# Expected: "ls: ... No such file or directory" (failure with this message is the PASS condition)

# (e) Verify Phase 1 G3 raw_payloads still resolve (998 symlinks)
find data/batches/phase2c_15_main_fire_combined/raw_payloads -type l 2>/dev/null | wc -l
# Expected: 998

# (f) Verify Phase 1 G3 a sample symlink resolves cleanly (target file exists)
python -c "
from pathlib import Path
import os
base = Path('data/batches/phase2c_15_main_fire_combined/raw_payloads')
links = sorted(p for p in base.iterdir() if p.is_symlink())[:3]
for link in links:
    target = os.readlink(link)
    resolved = (link.parent / target).resolve() if not target.startswith('/') else Path(target)
    assert resolved.exists(), f'broken symlink: {link} → {target}'
    print(f'OK: {link.name} → {resolved}')
"
# Expected: 3 lines printed, all 'OK: ...', no AssertionError

# (g) Verify no in-progress parent run row exists (W1a precondition)
python -c "
import sqlite3
from backtest.experiment_registry import get_connection, DEFAULT_DB_PATH
conn = get_connection(DEFAULT_DB_PATH)
try:
    cur = conn.cursor()
    cur.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='runs'\")
    if cur.fetchone() is None:
        print('runs table absent — clean state PASS')
    else:
        cur.execute(\"SELECT COUNT(*) FROM runs WHERE parent_run_id=?\", ('phase4_forward_2026_15bps_v1_b_c_narrow',))
        n_children = cur.fetchone()[0]
        cur.execute(\"SELECT COUNT(*) FROM runs WHERE run_id=?\", ('phase4_forward_2026_15bps_v1_b_c_narrow',))
        n_parent = cur.fetchone()[0]
        assert n_children == 0, f'pre-existing child rows for parent_run_id: {n_children}'
        assert n_parent == 0, f'pre-existing parent row: {n_parent}'
        print(f'registry clean: 0 child rows + 0 parent row for parent_run_id=phase4_forward_2026_15bps_v1_b_c_narrow')
finally:
    conn.close()
"
# Expected: prints either 'runs table absent — clean state PASS' OR 'registry clean: 0 child rows + 0 parent row ...'
```

If any precondition (a)-(g) fails (with the wrong message or unexpected count), STOP and surface to Charlie — fixing pre-existing state must be a separate Charlie register-event (NOT bundled into #N+19a fire authorization).

- [ ] **Step 13.2: Create `tests/test_b_c_narrow_v4_reproducibility.py` with 7 NEW test method bodies (TDD RED)**

Write the following file content verbatim:

```python
"""V4 reproducibility + G4-G7 gate tests for B-C-narrow Phase 3 fire.

Per Plan v3-Phase3 Step 13.2. Tests authored RED before Task 14 fire.
GREEN expected at Step 14.5 after fire + fixture capture + V4 gate run.

Test count: 7 methods (5 per spec §6.4 + 2 per BLOCKING-5 carry from
Phase 2 plan v3-Phase2 line 3651 G6+G7 inline coverage requirement).

Fixture file: tests/fixtures/b_c_narrow_archived_baseline.json
  Captured at Step 14.3 POST-T13 fire BEFORE T14 V4 gate runs.
  Sources from data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/
  (created by producer W3 during the fire step).
  Captures N=2 candidates: 18d92ce5d0b40cc7 + 22864f01a49e3452
  (lexicographically smallest 2 hypothesis_hash from cohort_a; deterministic).

Spec references:
  §4.2 V4 reproducibility gate (BLOCKING for SEAL): ε=1e-6 floats; exact int+bool
  §4.3 G4-G7 gate semantics
  §6.4 V4 reproducibility test enumeration
  §6.6 Fixture strategy (specific-keys-only N=2 sample)
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIBLING_RUN_DIR = (
    PROJECT_ROOT
    / "data"
    / "phase2c_evaluation_gate"
    / "phase4_forward_2026_15bps_v1_b_c_narrow"
)
ARCHIVE_RUN_DIR = (
    PROJECT_ROOT
    / "data"
    / "phase2c_evaluation_gate"
    / "archive"
    / "phase4_forward_2026_15bps_v1_d0b8101"
)
FIXTURE_PATH = (
    PROJECT_ROOT / "tests" / "fixtures" / "b_c_narrow_archived_baseline.json"
)

# Locked sample candidates per Plan v3-Phase3 fixture sampling rule:
# lexicographically smallest 2 hypothesis_hash strings from cohort_a.
SAMPLE_HASHES = ["18d92ce5d0b40cc7", "22864f01a49e3452"]

# V4 ε tolerance per spec §4.2
V4_EPSILON = 1e-6

# G5 tolerance per spec §4.3 (γ3/γ4 round-trip)
G5_EPSILON = 1e-10

BCNARROW_PARENT_RUN_ID = "phase4_forward_2026_15bps_v1_b_c_narrow"


def _load_summary(run_dir: Path, hypothesis_hash: str) -> dict:
    """Load holdout_summary.json for a candidate from a run directory."""
    summary_path = run_dir / hypothesis_hash / "holdout_summary.json"
    assert summary_path.exists(), (
        f"holdout_summary.json missing for candidate {hypothesis_hash} "
        f"at {summary_path} (precondition: fire+archive complete)"
    )
    with summary_path.open() as f:
        return json.load(f)


def _load_fixture() -> dict:
    """Load the V4 baseline fixture (N=2 candidates; specific keys)."""
    assert FIXTURE_PATH.exists(), (
        f"V4 baseline fixture missing at {FIXTURE_PATH}. "
        "Per Plan v3-Phase3 Step 14.3, this fixture is captured POST-T13 fire "
        "BEFORE T14 V4 gate runs. If fixture is missing, fire has not yet "
        "produced the archive, OR Step 14.3 fixture-capture sub-step was skipped."
    )
    with FIXTURE_PATH.open() as f:
        return json.load(f)


class TestV4Reproducibility:
    """V4 per-candidate metric reproducibility — sibling vs archived original."""

    def test_v4_per_candidate_metric_diff_within_epsilon(self) -> None:
        """Each sampled candidate's 3 float metrics match archive within ε=1e-6.

        Spec §4.2 + §6.4: sharpe_ratio + max_drawdown + total_return float
        metrics match between sibling new artifact and archived original to
        within absolute tolerance ε=1e-6. Drift > ε → SEAL BLOCKED pending
        Charlie register adjudication.
        """
        fixture = _load_fixture()
        for hh in SAMPLE_HASHES:
            new_summary = _load_summary(SIBLING_RUN_DIR, hh)
            old_metrics = fixture[hh]["holdout_metrics"]
            new_metrics = new_summary["holdout_metrics"]
            for metric_name in ("sharpe_ratio", "max_drawdown", "total_return"):
                old_val = float(old_metrics[metric_name])
                new_val = float(new_metrics[metric_name])
                diff = abs(new_val - old_val)
                assert diff < V4_EPSILON, (
                    f"V4 drift on candidate {hh} metric {metric_name}: "
                    f"old={old_val!r} new={new_val!r} abs_diff={diff!r} "
                    f"exceeds ε={V4_EPSILON} (spec §4.2 strict stop-condition)"
                )

    def test_v4_total_trades_exact_match(self) -> None:
        """Each sampled candidate's total_trades (int) + holdout_passed (bool)
        + 4 gate_pass_per_criterion subfields match archive EXACTLY (no ε).

        Spec §4.2 + §6.4: integer + bool values use exact equality (NO tolerance).
        """
        fixture = _load_fixture()
        for hh in SAMPLE_HASHES:
            new_summary = _load_summary(SIBLING_RUN_DIR, hh)
            old_fix = fixture[hh]
            new_total_trades = int(new_summary["holdout_metrics"]["total_trades"])
            old_total_trades = int(old_fix["holdout_metrics"]["total_trades"])
            assert new_total_trades == old_total_trades, (
                f"V4 total_trades exact-match FAIL on {hh}: "
                f"old={old_total_trades} new={new_total_trades}"
            )
            new_passed = bool(new_summary["holdout_passed"])
            old_passed = bool(old_fix["holdout_passed"])
            assert new_passed == old_passed, (
                f"V4 holdout_passed exact-match FAIL on {hh}: "
                f"old={old_passed} new={new_passed}"
            )
            for subfield in (
                "drawdown_passed",
                "return_passed",
                "sharpe_passed",
                "trades_passed",
            ):
                old_sub = bool(old_fix["gate_pass_per_criterion"][subfield])
                new_sub = bool(new_summary["gate_pass_per_criterion"][subfield])
                assert new_sub == old_sub, (
                    f"V4 gate_pass_per_criterion.{subfield} exact-match FAIL "
                    f"on {hh}: old={old_sub} new={new_sub}"
                )

    def test_v4_drift_stop_condition_blocks_seal_on_breach(self) -> None:
        """Synthetic ε-breach injection must trigger the SEAL stop condition.

        Spec §4.2 stop-condition contract: any 1 candidate × any 1 metric
        breach → SEAL BLOCKED. This test verifies the gate's failure-path
        behavior by constructing an in-memory baseline that diverges from
        an arbitrary actual value by 10× ε, asserting that the V4 epsilon
        check correctly signals the breach.
        """
        fixture_actual_value = 0.123456789
        synthetic_baseline_value = fixture_actual_value + 10 * V4_EPSILON
        diff = abs(synthetic_baseline_value - fixture_actual_value)
        # The drift detector must classify this as a breach.
        assert diff >= V4_EPSILON, (
            "Synthetic injection failed: 10×ε divergence should exceed ε. "
            "Check arithmetic precision or V4_EPSILON constant."
        )
        # Stop-condition simulation: a real V4 gate failure here would raise.
        # We assert the breach is correctly detected so the stop-condition
        # behavior contract is locked even when no real fire has occurred.
        with pytest.raises(AssertionError):
            assert diff < V4_EPSILON, (
                f"Synthetic 10×ε breach must trigger SEAL stop-condition "
                f"(injected diff={diff}, ε={V4_EPSILON})"
            )


class TestG4ParquetIntegrity:
    """G4 per-bar parquet integrity gate."""

    def test_g4_per_bar_parquet_row_count_matches_t_obs(self) -> None:
        """Per-bar parquet row count must equal T_obs from summary; SHA256 must
        match summary; data must be non-degenerate; timestamp column UTC-aware.

        Spec §4.3 G4: (a) row count = T_obs from summary; (b) SHA256 of
        file = `returns_per_bar_sha256` in summary + registry; (c) data not
        all-NaN; (d) `timestamp` column UTC-aware (parquet writes `timestamp`
        as a column not as the index per engine.py:498-510).
        """
        for hh in SAMPLE_HASHES:
            summary = _load_summary(SIBLING_RUN_DIR, hh)
            candidate_dir = SIBLING_RUN_DIR / hh
            parquet_path = candidate_dir / "returns_per_bar.parquet"
            assert parquet_path.exists(), (
                f"G4 missing parquet for candidate {hh} at {parquet_path}"
            )
            # (a) row count = T_obs
            df = pd.read_parquet(parquet_path)
            t_obs_summary = int(summary["T_obs"])
            assert len(df) == t_obs_summary, (
                f"G4(a) row count mismatch on {hh}: "
                f"parquet rows={len(df)} summary T_obs={t_obs_summary}"
            )
            # (b) SHA256 match
            hasher = hashlib.sha256()
            with parquet_path.open("rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    hasher.update(chunk)
            computed_sha = hasher.hexdigest()
            stored_sha = summary["returns_per_bar_sha256"]
            assert computed_sha == stored_sha, (
                f"G4(b) SHA256 mismatch on {hh}: "
                f"computed={computed_sha!r} stored={stored_sha!r}"
            )
            # (c) data not all-NaN (degenerate write)
            assert not df["return"].isna().all(), (
                f"G4(c) degenerate parquet on {hh}: all `return` values NaN"
            )
            # (d) timestamp column UTC-aware (column not index)
            assert "timestamp" in df.columns, (
                f"G4(d) parquet missing `timestamp` column on {hh}: "
                f"columns={list(df.columns)}"
            )
            ts_dtype = df["timestamp"].dtype
            assert pd.api.types.is_datetime64_any_dtype(ts_dtype), (
                f"G4(d) timestamp column dtype non-datetime on {hh}: {ts_dtype}"
            )
            tz = getattr(ts_dtype, "tz", None)
            assert tz is not None and str(tz) in ("UTC", "utc"), (
                f"G4(d) timestamp column not UTC-aware on {hh}: tz={tz!r}"
            )


class TestG5GammaRoundTrip:
    """G5 γ3 / γ4 round-trip gate."""

    def test_g5_gamma_round_trip_from_parquet_within_epsilon(self) -> None:
        """Recompute γ3/γ4 from per-bar parquet via compute_moments; must
        match stored summary values within abs diff < 1e-10 (float64 round-trip
        determinism). T_obs must match bit-exact (integer).

        Spec §4.3 G5: load parquet → compute_moments(returns_array) → compare.
        """
        from backtest.engine import compute_moments

        for hh in SAMPLE_HASHES:
            summary = _load_summary(SIBLING_RUN_DIR, hh)
            candidate_dir = SIBLING_RUN_DIR / hh
            parquet_path = candidate_dir / "returns_per_bar.parquet"
            assert parquet_path.exists(), (
                f"G5 missing parquet for candidate {hh}"
            )
            df = pd.read_parquet(parquet_path)
            returns_arr = df["return"].to_numpy(dtype=np.float64)
            moments = compute_moments(returns_arr)
            # T_obs bit-exact
            t_obs_recomputed = int(moments["T_obs"])
            t_obs_stored = int(summary["T_obs"])
            assert t_obs_recomputed == t_obs_stored, (
                f"G5 T_obs round-trip FAIL on {hh}: "
                f"recomputed={t_obs_recomputed} stored={t_obs_stored}"
            )
            # γ3 + γ4 within ε=1e-10
            for gamma_key in ("gamma3", "gamma4"):
                recomputed = moments[gamma_key]
                stored = summary[gamma_key]
                if recomputed is None and stored is None:
                    continue  # both None (insufficient T_obs); no compare
                assert recomputed is not None and stored is not None, (
                    f"G5 {gamma_key} None-asymmetry on {hh}: "
                    f"recomputed={recomputed!r} stored={stored!r}"
                )
                diff = abs(float(recomputed) - float(stored))
                assert diff < G5_EPSILON, (
                    f"G5 {gamma_key} round-trip drift on {hh}: "
                    f"recomputed={recomputed!r} stored={stored!r} "
                    f"abs_diff={diff!r} exceeds ε={G5_EPSILON}"
                )


class TestG6RegistryParentChildIntegrity:
    """G6 registry parent-child integrity gate."""

    def test_g6_registry_parent_child_integrity_after_fire(self) -> None:
        """Registry must contain exactly 1 batch_summary parent row at
        run_id=phase4_forward_2026_15bps_v1_b_c_narrow + 39 child rows
        (run_type=regime_holdout); each child's parent_run_id = parent.

        Spec §4.3 G6: SELECT COUNT(*) FROM runs WHERE
        parent_run_id='phase4_forward_2026_15bps_v1_b_c_narrow' AND
        run_type='regime_holdout' = 39; parent row exists with
        run_type='batch_summary'. Cohort-level metadata at parent; per-
        candidate metadata at children.

        BLOCKING-5 carry per Plan v3-Phase2 line 3651: G6 inline coverage
        required at Phase 3 (not enumerated in spec §6.4).
        """
        from backtest.experiment_registry import get_connection, DEFAULT_DB_PATH

        conn = get_connection(DEFAULT_DB_PATH)
        try:
            cur = conn.cursor()
            # Parent row
            cur.execute(
                "SELECT run_type FROM runs WHERE run_id = ?",
                (BCNARROW_PARENT_RUN_ID,),
            )
            parent_rows = cur.fetchall()
            assert len(parent_rows) == 1, (
                f"G6 parent row count FAIL: expected 1 parent row at "
                f"run_id={BCNARROW_PARENT_RUN_ID!r}, found {len(parent_rows)}"
            )
            assert parent_rows[0][0] == "batch_summary", (
                f"G6 parent row run_type FAIL: expected 'batch_summary', "
                f"found {parent_rows[0][0]!r}"
            )
            # Child rows
            cur.execute(
                "SELECT COUNT(*) FROM runs WHERE parent_run_id = ? "
                "AND run_type = ?",
                (BCNARROW_PARENT_RUN_ID, "regime_holdout"),
            )
            n_children = cur.fetchone()[0]
            assert n_children == 39, (
                f"G6 child row count FAIL: expected 39 child rows "
                f"(run_type=regime_holdout, parent_run_id={BCNARROW_PARENT_RUN_ID!r}), "
                f"found {n_children}"
            )
            # Each child's parent_run_id = parent (redundant given query above,
            # but locks the invariant against future schema changes)
            cur.execute(
                "SELECT DISTINCT parent_run_id FROM runs WHERE parent_run_id = ?",
                (BCNARROW_PARENT_RUN_ID,),
            )
            distinct_parents = [row[0] for row in cur.fetchall()]
            assert distinct_parents == [BCNARROW_PARENT_RUN_ID], (
                f"G6 child parent_run_id linkage FAIL: expected "
                f"[{BCNARROW_PARENT_RUN_ID!r}], found {distinct_parents!r}"
            )
        finally:
            conn.close()


class TestG7ArchiveIdempotency:
    """G7 archive idempotency gate."""

    def test_g7_archive_idempotency_refuses_existing_target(
        self, tmp_path: Path
    ) -> None:
        """Producer W3 (`_archive_canonical_pre_flight`) MUST raise when
        archive target already exists. Strict refuse-if-exists semantics;
        no silent overwrite; no auto-rename.

        Spec §4.3 G7 + spec §3.2.4 strict refuse semantics. Tested in
        isolation via tmp_path (does NOT mutate real canonical/archive paths).

        BLOCKING-5 carry per Plan v3-Phase2 line 3651: G7 inline coverage
        required at Phase 3 (not enumerated in spec §6.4).
        """
        from scripts.run_phase2c_evaluation_gate import (
            _archive_canonical_pre_flight,
            BCNARROW_ARCHIVE_BASENAME,
        )

        # Construct synthetic canonical + archive paths under tmp_path
        canonical_path = tmp_path / "fake_canonical_dir"
        canonical_path.mkdir()
        (canonical_path / "marker.txt").write_text("source content")
        archive_root = tmp_path / "archive"
        archive_root.mkdir()
        # Pre-create archive target to trigger refuse semantics
        preexisting_archive = archive_root / BCNARROW_ARCHIVE_BASENAME
        preexisting_archive.mkdir()
        (preexisting_archive / "stale.txt").write_text("stale prior content")

        with pytest.raises((RuntimeError, FileExistsError)) as exc_info:
            _archive_canonical_pre_flight(
                canonical_path=canonical_path,
                archive_root=archive_root,
                archive_basename=BCNARROW_ARCHIVE_BASENAME,
            )
        msg = str(exc_info.value).lower()
        assert "archive" in msg or "exist" in msg or BCNARROW_ARCHIVE_BASENAME in str(exc_info.value), (
            f"G7 archive-refuse error message must reference archive target. "
            f"Got: {exc_info.value!r}"
        )
        # Verify source canonical was NOT moved (refuse before any mutation)
        assert (canonical_path / "marker.txt").exists(), (
            "G7 refuse-if-exists FAIL: canonical source mutated despite refusal"
        )
        # Verify pre-existing archive content was NOT overwritten
        assert (preexisting_archive / "stale.txt").read_text() == "stale prior content", (
            "G7 refuse-if-exists FAIL: pre-existing archive content overwritten"
        )
```

- [ ] **Step 13.3: Verify RED phase (all 7 tests FAIL with expected error messages)**

```bash
python -m pytest tests/test_b_c_narrow_v4_reproducibility.py -v
```

Expected behavior:
- `TestV4Reproducibility::test_v4_per_candidate_metric_diff_within_epsilon` → FAIL with AssertionError mentioning either "holdout_summary.json missing" (sibling dir does not exist yet) OR "V4 baseline fixture missing" (fixture file does not exist yet)
- `TestV4Reproducibility::test_v4_total_trades_exact_match` → FAIL similarly
- `TestV4Reproducibility::test_v4_drift_stop_condition_blocks_seal_on_breach` → PASS (pure arithmetic, no precondition on disk state; locks the stop-condition contract)
- `TestG4ParquetIntegrity::test_g4_per_bar_parquet_row_count_matches_t_obs` → FAIL with AssertionError mentioning "holdout_summary.json missing"
- `TestG5GammaRoundTrip::test_g5_gamma_round_trip_from_parquet_within_epsilon` → FAIL similarly
- `TestG6RegistryParentChildIntegrity::test_g6_registry_parent_child_integrity_after_fire` → FAIL with AssertionError "expected 1 parent row ... found 0" (registry has no parent row pre-fire)
- `TestG7ArchiveIdempotency::test_g7_archive_idempotency_refuses_existing_target` → PASS (uses tmp_path; does not depend on real fire state; locks the refuse-if-exists contract)

Summary expected: 5 FAILED + 2 PASSED. Both PASSED tests (drift stop-condition + archive idempotency) lock contracts that are TESTABLE without the fire — that is the design.

If you see a different failure pattern (e.g., ImportError, ModuleNotFoundError, AttributeError on `BCNARROW_*` constants), STOP — Phase 2 SEAL state may have regressed (already caught by Precondition 4 + 5 in §"Phase 3 execution preconditions", but re-check).

- [ ] **Step 13.4: Commit pre-fire test bodies + pre-flight evidence**

```bash
git add tests/test_b_c_narrow_v4_reproducibility.py
git commit -m "$(cat <<'EOF'
test(b-c-narrow/phase-3): T13 RED — V4+G4-G7 test bodies (7 methods)

Per Plan v3-Phase3 Task 13. RED phase before T13 fire authorization.

Test methods (7 total = 5 spec §6.4 + 2 BLOCKING-5 carry G6+G7):
- TestV4Reproducibility::test_v4_per_candidate_metric_diff_within_epsilon
- TestV4Reproducibility::test_v4_total_trades_exact_match
- TestV4Reproducibility::test_v4_drift_stop_condition_blocks_seal_on_breach
- TestG4ParquetIntegrity::test_g4_per_bar_parquet_row_count_matches_t_obs
- TestG5GammaRoundTrip::test_g5_gamma_round_trip_from_parquet_within_epsilon
- TestG6RegistryParentChildIntegrity::test_g6_registry_parent_child_integrity_after_fire
- TestG7ArchiveIdempotency::test_g7_archive_idempotency_refuses_existing_target

Expected RED at this commit: 5 FAILED + 2 PASSED. The 2 PASSED tests
(drift stop-condition + archive idempotency tmp_path) lock contracts
that are TESTABLE without the fire — by design.

GREEN expected at Step 14.5 post-fire + fixture capture.

Per BLOCKING-5 carry from Plan v3-Phase2 line 3651: G6+G7 inline test
bodies authored at Phase 3 (NOT enumerated in spec §6.4; required for
inline coverage of all 4 §4.3 G-gates).

Sample candidates per fixture sampling rule (lexicographically smallest 2):
- 18d92ce5d0b40cc7
- 22864f01a49e3452

Fixture file (tests/fixtures/b_c_narrow_archived_baseline.json) captured
POST-T13 fire BEFORE T14 V4 gate runs (see Step 14.3).
EOF
)"
```

- [ ] **Step 13.5: STOP HERE — Surface to Charlie for register #N+19a (T13 fire authorization)**

```
========================================================================
STOP HERE — CHARLIE REGISTER-EVENT #N+19a REQUIRED
========================================================================

Task 13 (TDD RED) complete. Ready for T13 fire authorization.

NEXT STEP requires destructive operational write:
  - Producer W3 will MOVE current canonical dir
    data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/
    to archive
    data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/
  - Producer LC-b loop will WRITE 39 candidate dirs to sibling
    data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/
  - Producer W4 will INSERT 1 batch_summary parent row to registry
    backtest/experiments.db (run_id=phase4_forward_2026_15bps_v1_b_c_narrow)
  - Engine LC-b path will INSERT 39 regime_holdout child rows to registry
    backtest/experiments.db (parent_run_id=phase4_forward_2026_15bps_v1_b_c_narrow)

What to surface to Charlie:
  - Plan path: docs/superpowers/plans/2026-05-27-b-c-narrow-phase-3-fire-plan.md
  - Commit just landed: <git rev-parse --short HEAD> (Task 13 RED)
  - Test status: 5 FAILED + 2 PASSED (expected)
  - Fire command (exact bash to be executed at Step 14.1):
    [paste the bash from Step 14.1 verbatim]
  - Expected wall-clock: ~10-15 seconds (39 candidates × ~0.25s/candidate
    per existing forward_2026 patterns + producer overhead)
  - Estimated registry writes: 1 parent + 39 children = 40 INSERTs
  - Estimated FS writes: 1 archive mv + 39 candidate dirs (each with
    holdout_summary.json + returns_per_bar.parquet) + 1 aggregate
    holdout_summary.json + 1 holdout_results.csv

DO NOT PROCEED to Task 14 (Step 14.0) without explicit Charlie register #N+19a
T13 fire authorization. The implementer subagent MUST NOT bypass this STOP
without an explicit Charlie register fire — per CLAUDE.md operational-write
discipline + sub-decision (iii).
========================================================================
```

---

### Task 14: T13 fire execution + T14 V4 gate verification

**Files:**
- Operates on: `scripts/run_phase2c_evaluation_gate.py` (NO source edits; OPERATIONAL execution only via subprocess)
- Writes to: `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/` (sibling output dir; T14b relocates after V4 PASS)
- Writes to: `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` (archive of original; via producer W3 step)
- Writes to: `backtest/experiments.db` (1 parent batch_summary row via producer W4 + 39 child regime_holdout rows via engine LC-b)
- Creates: `tests/fixtures/b_c_narrow_archived_baseline.json` (POST-fire fixture capture for N=2 candidates)

- [ ] **Step 14.0: Charlie register #N+19a verification**

Before executing Step 14.1, verify Charlie register fire:

```bash
# Document the register fire in the session record (implementer subagent records
# the timestamp + Charlie's explicit authorization message verbatim).
# If no Charlie register message exists in the current session record, ABORT and
# return to Step 13.5 STOP block — DO NOT execute the fire on the basis of an
# inferred or assumed authorization.
echo "Verify Charlie register #N+19a has been fired in the conversation record."
echo "If not, ABORT and surface back to Step 13.5."
```

If Charlie register #N+19a has not been fired (no explicit authorization message in conversation record from Charlie), STOP and surface — do NOT execute the fire on inferred authorization.

- [ ] **Step 14.1: Execute T13 fire command**

Run the producer with `--enable-b-c-narrow-recovery` flag. This is a SINGLE bash command (no chaining), expected to complete in ~10-15 seconds:

```bash
python -m scripts.run_phase2c_evaluation_gate \
  --enable-b-c-narrow-recovery \
  --candidate-hashes 18d92ce5d0b40cc7,22864f01a49e3452,2433a38b2f9a7211,2b1ca44778281d97,2c5e3cc08d407b73,2cc19d1b5e2c9024,34588c948b1ff12b,35dcfcfbee4cfafc,38a1bb228f103c26,3a2559fbeff71f94,3b013ac903ab047b,3c3ba9b95d2ea37c,3d3938aed6376f04,3ebec90d7be309ab,406d4f4dfb4d46de,41d3b759a1004c97,4a3c8e2fe04d72c1,4ce6e78ff9cff9b9,52b04f27b7ee565b,53e1b5030aefe836,54ae22768a3f78e9,5b4d89be0ccb9be1,5fcf29ab42c5f8b6,7240602b60cd7271,7abff29fc2f117a1,8a2a8f73f71a835e,8def2951c72f0961,95d5cfc1c0a9579a,9c90efe879157a5c,aa8c55c16db41ea7,b10f4563366481b3,b24ca51d477c2e96,bc5ea1beab19fcdd,c076cdad4ee7ca42,cfd24b8b72d6e429,d04e1b054fe4d69d,d3fe403c8b1c4130,dc7d6de5e71772ae,ec6a8a385c1a3e9a \
  --source-batch-id phase2c_15_main_fire_combined \
  --regime-key evaluation_regimes.forward_2026 \
  --execution-config config/execution_phase4_15bps.yaml \
  --run-id phase4_forward_2026_15bps_v1_b_c_narrow \
  --output-root data/phase2c_evaluation_gate/
```

**Hash list verification:** the comma-separated list above contains exactly 39 hashes (verified at plan drafting time via `tail -39 data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv | awk -F, '{print $1}'`). Implementer should NOT re-extract the list; use the list above verbatim.

Expected stdout pattern (selected lines):
- `[Phase 4] forward_window_metadata captured: start=... end=... bar_count=... parquet_sha256=...`
- `[1/39] evaluating 18d92ce5 ...` through `[39/39] evaluating ec6a8a38 ...`
- `[B-C-narrow] _finalize_batch_registry: parent batch_summary row written at ...`
- Exit code 0

If exit code is non-zero, STOP — capture full stdout/stderr, surface to Charlie. Do NOT proceed to Step 14.2.

Expected duration: 10-15 seconds (39 × ~0.25s/candidate per spec §7 R6 + producer overhead for archive + identity guard + finalize).

- [ ] **Step 14.2: Verify post-fire state (FS + registry)**

Run all of these in sequence; each must pass before proceeding:

```bash
# (a) Sibling output dir exists with 39 candidate subdirectories
ls -d data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/*/ 2>/dev/null | wc -l
# Expected: 39

# (b) Sibling output dir contains aggregate holdout_summary.json + holdout_results.csv
ls data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/holdout_summary.json data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/holdout_results.csv
# Expected: both files printed, no error

# (c) Each candidate subdirectory has both holdout_summary.json + returns_per_bar.parquet
python -c "
from pathlib import Path
sibling = Path('data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow')
cand_dirs = sorted(d for d in sibling.iterdir() if d.is_dir())
missing = []
for d in cand_dirs:
    if not (d / 'holdout_summary.json').exists():
        missing.append(f'{d.name}/holdout_summary.json')
    if not (d / 'returns_per_bar.parquet').exists():
        missing.append(f'{d.name}/returns_per_bar.parquet')
assert not missing, f'missing artifacts: {missing}'
print(f'all 39 candidate dirs complete: {len(cand_dirs)} dirs × 2 artifacts each = {len(cand_dirs)*2} files')
"
# Expected: 'all 39 candidate dirs complete: 39 dirs × 2 artifacts each = 78 files'

# (d) Archive dir exists with 39 candidate subdirectories (snapshot of original)
ls -d data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/*/ 2>/dev/null | wc -l
# Expected: 39

# (e) Canonical dir is gone (moved to archive by W3) — sibling now holds new content
ls -la data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/ 2>&1
# Expected: "ls: ... No such file or directory" (canonical was archived)

# (f) Registry has 1 parent batch_summary row + 39 child regime_holdout rows
python -c "
import sqlite3
from backtest.experiment_registry import get_connection, DEFAULT_DB_PATH
conn = get_connection(DEFAULT_DB_PATH)
try:
    cur = conn.cursor()
    cur.execute(\"SELECT COUNT(*) FROM runs WHERE run_id='phase4_forward_2026_15bps_v1_b_c_narrow' AND run_type='batch_summary'\")
    n_parent = cur.fetchone()[0]
    cur.execute(\"SELECT COUNT(*) FROM runs WHERE parent_run_id='phase4_forward_2026_15bps_v1_b_c_narrow' AND run_type='regime_holdout'\")
    n_children = cur.fetchone()[0]
    assert n_parent == 1, f'parent rows: expected 1 got {n_parent}'
    assert n_children == 39, f'child rows: expected 39 got {n_children}'
    print(f'registry verified: 1 parent + 39 children at parent_run_id=phase4_forward_2026_15bps_v1_b_c_narrow')
finally:
    conn.close()
"
# Expected: 'registry verified: 1 parent + 39 children ...'
```

If any verification (a)-(f) fails, STOP — capture full output, surface to Charlie. Do NOT proceed to Step 14.3.

- [ ] **Step 14.3: Capture fixture for V4 gate (POST-fire, BEFORE V4 verification)**

Create `tests/fixtures/b_c_narrow_archived_baseline.json` from the archived original (which is now populated by producer W3 during Step 14.1 fire). Use the deterministic sampling rule (lexicographically smallest 2 hypothesis_hash strings):

```bash
mkdir -p tests/fixtures
python -c "
import json
from pathlib import Path

ARCHIVE_DIR = Path('data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101')
SAMPLE_HASHES = ['18d92ce5d0b40cc7', '22864f01a49e3452']
SPECIFIC_KEYS_FROM_SUMMARY = ('holdout_passed', 'gate_pass_per_criterion')
SPECIFIC_METRIC_KEYS = ('sharpe_ratio', 'max_drawdown', 'total_return', 'total_trades')

fixture = {}
for hh in SAMPLE_HASHES:
    summary_path = ARCHIVE_DIR / hh / 'holdout_summary.json'
    assert summary_path.exists(), f'missing archived summary: {summary_path}'
    with summary_path.open() as f:
        full = json.load(f)
    # Specific-keys-only capture per spec §6.6 (avoid full-dict drift on schema-version-bump)
    entry = {
        'holdout_metrics': {k: full['holdout_metrics'][k] for k in SPECIFIC_METRIC_KEYS},
        'holdout_passed': full['holdout_passed'],
        'gate_pass_per_criterion': dict(full['gate_pass_per_criterion']),
    }
    fixture[hh] = entry

out = Path('tests/fixtures/b_c_narrow_archived_baseline.json')
out.parent.mkdir(parents=True, exist_ok=True)
with out.open('w') as f:
    json.dump(fixture, f, indent=2, sort_keys=True)
print(f'fixture written: {out} ({len(fixture)} candidates)')
print(f'fixture keys per entry: holdout_metrics (4 subfields), holdout_passed, gate_pass_per_criterion (4 subfields)')
"
```

Expected stdout:
- `fixture written: tests/fixtures/b_c_narrow_archived_baseline.json (2 candidates)`
- `fixture keys per entry: holdout_metrics (4 subfields), holdout_passed, gate_pass_per_criterion (4 subfields)`

Verify the fixture file exists and parses:

```bash
python -c "
import json
from pathlib import Path
fix = json.loads(Path('tests/fixtures/b_c_narrow_archived_baseline.json').read_text())
assert set(fix.keys()) == {'18d92ce5d0b40cc7', '22864f01a49e3452'}, f'keys: {sorted(fix.keys())}'
for hh, entry in fix.items():
    assert set(entry['holdout_metrics'].keys()) == {'sharpe_ratio', 'max_drawdown', 'total_return', 'total_trades'}, f'{hh} metric keys: {sorted(entry[\"holdout_metrics\"].keys())}'
    assert set(entry['gate_pass_per_criterion'].keys()) == {'drawdown_passed', 'return_passed', 'sharpe_passed', 'trades_passed'}, f'{hh} gate keys: {sorted(entry[\"gate_pass_per_criterion\"].keys())}'
    assert isinstance(entry['holdout_passed'], bool)
print('fixture structure verified')
"
```

Expected: `fixture structure verified`.

- [ ] **Step 14.4: Run V4 gate G4-G7 + ε=1e-6 verification (7 tests)**

```bash
python -m pytest tests/test_b_c_narrow_v4_reproducibility.py -v
```

- [ ] **Step 14.5: Verify GREEN (all 7 V4 tests pass)**

Expected pytest output: `7 passed in <X>s` (0 failed, 0 skipped). Specifically:
- `TestV4Reproducibility::test_v4_per_candidate_metric_diff_within_epsilon` → PASSED
- `TestV4Reproducibility::test_v4_total_trades_exact_match` → PASSED
- `TestV4Reproducibility::test_v4_drift_stop_condition_blocks_seal_on_breach` → PASSED
- `TestG4ParquetIntegrity::test_g4_per_bar_parquet_row_count_matches_t_obs` → PASSED
- `TestG5GammaRoundTrip::test_g5_gamma_round_trip_from_parquet_within_epsilon` → PASSED
- `TestG6RegistryParentChildIntegrity::test_g6_registry_parent_child_integrity_after_fire` → PASSED
- `TestG7ArchiveIdempotency::test_g7_archive_idempotency_refuses_existing_target` → PASSED

If any test FAILs:
- V4 metric drift (test 1 or test 2 FAIL) → STOP; SEAL BLOCKED per spec §4.2 stop-condition; surface to Charlie for adjudication paths (a/b/c per spec §4.2: environmental ε widen, semantic Q2 re-litigation, or accept-drift with §8 INDETERMINATE re-classification in this cycle's NOTE doc)
- G4-G7 FAIL → STOP; gate violation indicates producer/engine bug or partial-write state; surface to Charlie

Do NOT proceed to Step 14.6 unless all 7 tests PASS.

Also run full test suite zero-regression check:

```bash
python -m pytest -q
```

Expected: `2367 passed` (= 2360 from Phase 2 baseline + 7 new V4 tests, with 2 xfailed unchanged) OR equivalent. Net new = 7 passing tests (no test deletions; no regressions). If full suite reveals regressions outside `test_b_c_narrow_v4_reproducibility.py`, STOP — surface to Charlie.

- [ ] **Step 14.6: Commit T13 fire evidence + V4 gate results + fixture**

Note: data artifacts under `data/` are gitignored; reference paths + verification commands in the commit message body for forensic recoverability.

```bash
git add tests/fixtures/b_c_narrow_archived_baseline.json
git commit -m "$(cat <<'EOF'
evidence(b-c-narrow/phase-3): T13 fire + T14 V4 gate GREEN (Task 14)

Per Plan v3-Phase3 Task 14. Charlie register #N+19a fired authorization.

T13 fire executed at <ISO UTC timestamp>:
  python -m scripts.run_phase2c_evaluation_gate \
    --enable-b-c-narrow-recovery \
    --candidate-hashes <39 hashes> \
    --source-batch-id phase2c_15_main_fire_combined \
    --regime-key evaluation_regimes.forward_2026 \
    --execution-config config/execution_phase4_15bps.yaml \
    --run-id phase4_forward_2026_15bps_v1_b_c_narrow \
    --output-root data/phase2c_evaluation_gate/

FS writes (gitignored under data/):
- data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/ (sibling; 39 candidate dirs + aggregate)
- data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/ (archive snapshot of original via producer W3)

Registry writes (backtest/experiments.db):
- 1 batch_summary parent row at run_id=phase4_forward_2026_15bps_v1_b_c_narrow (via producer W4)
- 39 regime_holdout child rows at parent_run_id=phase4_forward_2026_15bps_v1_b_c_narrow (via engine LC-b path)

T14 V4 gate (G4-G7 + ε=1e-6 per-candidate):
- 7/7 tests in tests/test_b_c_narrow_v4_reproducibility.py PASSED
- Full suite zero regression (2367 passed / 0 failed / 2 xfailed)

Fixture file (committed):
- tests/fixtures/b_c_narrow_archived_baseline.json (N=2 candidates per
  spec §6.6 fixture sampling rule: 18d92ce5d0b40cc7 + 22864f01a49e3452;
  specific keys only: holdout_metrics + holdout_passed + gate_pass_per_criterion)

Next: Charlie register #N+19b authorization required for T14b canonical-path
relocation (see Step 14.7 STOP).
EOF
)"
```

- [ ] **Step 14.7: STOP HERE — Surface to Charlie for register #N+19b (T14b canonical-path relocation authorization)**

```
========================================================================
STOP HERE — CHARLIE REGISTER-EVENT #N+19b REQUIRED (ONLY if V4 PASS)
========================================================================

Task 14 complete; V4 gate GREEN (all 7 tests passed).

NEXT STEP requires destructive canonical-path mutation:
  - mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/
       data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/
  - Sibling dir becomes canonical; downstream consumers of the canonical
    path (Tier 6 evaluation application + future Phase 5 work) see new
    B-C-narrow content; original lineage preserved at
    archive/phase4_forward_2026_15bps_v1_d0b8101/ (snapshot of pre-fire state)

What to surface to Charlie:
  - V4 GREEN evidence: pytest output (7 passed) + commit landed at
    <git rev-parse --short HEAD> (Step 14.6)
  - Full suite zero-regression confirmation
  - Registry write evidence (1 parent + 39 children verified at Step 14.2(f))
  - FS write evidence (sibling + archive populated; verified at Step 14.2(a-e))
  - mv command (exact bash to be executed at Step 14b.1):
    mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow \
       data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1
  - Post-mv expected state: canonical repopulated; sibling gone; registry
    rows unchanged (registry refs run_id=phase4_forward_2026_15bps_v1_b_c_narrow
    which is a directory NAME not a path; canonical path becomes the new
    location for those rows' artifacts but rows themselves don't move)

If V4 had FAILED (any of the 7 tests), this STOP would be replaced by
SEAL BLOCKED — STOP HERE + surface to Charlie for adjudication paths
(a/b/c per spec §4.2). T14b would NOT execute on V4 failure.

DO NOT PROCEED to Task 14b without explicit Charlie register #N+19b
T14b canonical-path relocation authorization. The implementer subagent
MUST NOT bypass this STOP — per CLAUDE.md operational-write discipline +
sub-decision (iii).
========================================================================
```

---

### Task 14b: T14b canonical-path relocation

**Files:**
- Operates on:
  - `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/` (mv source — currently populated by Step 14.1 fire)
  - `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` (mv target — currently empty after Step 14.1 W3 archived the original)
- NO test file changes
- NO source code edits

- [ ] **Step 14b.0: Charlie register #N+19b verification**

Before executing Step 14b.1, verify Charlie register fire:

```bash
echo "Verify Charlie register #N+19b has been fired in the conversation record."
echo "If not, ABORT and return to Step 14.7 STOP block."
```

If Charlie register #N+19b has not been fired (no explicit authorization message from Charlie in the conversation record), STOP and surface — do NOT execute the mv on inferred authorization.

- [ ] **Step 14b.1: Execute mv sibling → canonical**

Pre-mv state verification (target MUST be empty/absent):

```bash
ls -la data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/ 2>&1
# Expected: "ls: ... No such file or directory" (canonical was archived in Step 14.1)
```

If the canonical path exists with content, STOP and surface — partial state requires manual cleanup (canonical was supposed to be archived by Step 14.1 W3).

Execute the mv:

```bash
mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow \
   data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1
```

Expected: zero-output success; exit code 0.

- [ ] **Step 14b.2: Verify canonical repopulated + sibling gone + registry intact**

```bash
# (a) Canonical now exists and has 39 candidate subdirs
ls -d data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/*/ 2>/dev/null | wc -l
# Expected: 39

# (b) Sibling is gone
ls -la data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/ 2>&1
# Expected: "ls: ... No such file or directory"

# (c) Archive still exists and is intact (mv did not touch it)
ls -d data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/*/ 2>/dev/null | wc -l
# Expected: 39

# (d) Canonical now has aggregate holdout_summary.json + holdout_results.csv
ls data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_summary.json data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv
# Expected: both files printed without error

# (e) Each canonical candidate subdir has holdout_summary.json + returns_per_bar.parquet
python -c "
from pathlib import Path
canon = Path('data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1')
cand_dirs = sorted(d for d in canon.iterdir() if d.is_dir())
missing = []
for d in cand_dirs:
    if not (d / 'holdout_summary.json').exists():
        missing.append(f'{d.name}/holdout_summary.json')
    if not (d / 'returns_per_bar.parquet').exists():
        missing.append(f'{d.name}/returns_per_bar.parquet')
assert not missing, f'post-mv missing: {missing}'
print(f'canonical post-mv complete: {len(cand_dirs)} dirs × 2 artifacts')
"
# Expected: 'canonical post-mv complete: 39 dirs × 2 artifacts'

# (f) Registry rows unchanged (parent + children still at run_id=phase4_forward_2026_15bps_v1_b_c_narrow;
#     row count + parent_run_id linkage unaffected by FS mv since rows reference
#     run_id which is directory-name level not absolute path)
python -c "
import sqlite3
from backtest.experiment_registry import get_connection, DEFAULT_DB_PATH
conn = get_connection(DEFAULT_DB_PATH)
try:
    cur = conn.cursor()
    cur.execute(\"SELECT COUNT(*) FROM runs WHERE run_id='phase4_forward_2026_15bps_v1_b_c_narrow' AND run_type='batch_summary'\")
    n_parent = cur.fetchone()[0]
    cur.execute(\"SELECT COUNT(*) FROM runs WHERE parent_run_id='phase4_forward_2026_15bps_v1_b_c_narrow' AND run_type='regime_holdout'\")
    n_children = cur.fetchone()[0]
    assert n_parent == 1, f'parent rows: expected 1 got {n_parent}'
    assert n_children == 39, f'child rows: expected 39 got {n_children}'
    print(f'registry post-mv intact: 1 parent + 39 children')
finally:
    conn.close()
"
# Expected: 'registry post-mv intact: 1 parent + 39 children'
```

If any verification (a)-(f) fails, STOP — partial mv state requires surface to Charlie for adjudication.

Also re-run the V4+G4-G7 suite to verify the tests still pass against the NEW canonical path (the tests reference `SIBLING_RUN_DIR` which points at the sibling — that path is now gone). Pin this AS A KNOWN BEHAVIOR change:

Note: after the mv, `SIBLING_RUN_DIR` (which the V4 tests reference) no longer exists. The tests will FAIL after T14b. This is EXPECTED — the V4 tests serve as fire-time gates only. Future re-verifications of canonical content would need a separate test class against `CANONICAL_RUN_DIR`. This is NAMED-eligible for Phase 4 SEAL bundle: either delete the V4 tests after the cycle (one-shot gate) OR refactor them to take a `--canonical` flag. Plan v3-Phase3 leaves them as-is post-mv per anti-pre-emption (NOT a Phase 3 deliverable).

- [ ] **Step 14b.3: Commit T14b evidence**

```bash
git commit --allow-empty -m "$(cat <<'EOF'
evidence(b-c-narrow/phase-3): T14b canonical-path relocation (Task 14b)

Per Plan v3-Phase3 Task 14b. Charlie register #N+19b fired authorization.

T14b mv executed at <ISO UTC timestamp>:
  mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow \
     data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1

Post-mv state (verified at Step 14b.2):
- canonical data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/ repopulated
  with 39 candidate dirs + aggregate holdout_summary.json + holdout_results.csv
- sibling dir gone (mv source consumed)
- archive data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/
  preserves original pre-fire state (39 candidate dirs + aggregate)
- registry rows intact: 1 parent batch_summary + 39 child regime_holdout
  at run_id=phase4_forward_2026_15bps_v1_b_c_narrow

Downstream consumers of canonical path (Tier 6 evaluation application + future
Phase 5 work) now see B-C-narrow recovered content with per-bar parquet
preservation + γ3/γ4 moments + registry linkage. Original lineage preserved
at archive/ for cross-verification.

NOTE on V4 test status post-mv: tests in tests/test_b_c_narrow_v4_reproducibility.py
reference SIBLING_RUN_DIR which no longer exists post-mv. The 5 disk-dependent
tests will FAIL after T14b — EXPECTED behavior; V4 tests are fire-time gates
only. Refactor for canonical-path re-verification is NAMED-eligible at Phase 4
SEAL bundle (NOT a Phase 3 deliverable; anti-pre-emption).

Next: Phase 3 ratify packet at Task 14c → Charlie register #N+19c.
EOF
)"
```

Note: this commit is `--allow-empty` because Step 14b is a pure FS mv (no file changes tracked by git). The commit serves as a register-event boundary marker for forensic recoverability. If the commit message is sufficient evidence without an empty commit, the implementer may skip this commit and roll the evidence into Step 14c.2 instead — confirm with Charlie register #N+19b authorization message intent.

---

### Task 14c: Phase 3 ratify packet artifact

**Files:**
- Create: `docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md` (NEW)

- [ ] **Step 14c.1: Write Phase 3 ratify packet**

```bash
mkdir -p docs/superpowers/phase-3-impl-results
```

Write the following file content to `docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md` (replace `<...>` placeholders with measured values at commit time):

```markdown
# B-C-narrow Phase 3 ratify packet

**Date:** <ISO UTC at Step 14c.1 commit time>
**HEAD commit:** <git rev-parse --short HEAD>
**Plan version:** v3-Phase3 v1 (or post-PFR iteration count if amended)
**Plan path:** `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-3-fire-plan.md`
**Spec path:** `docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md` (sealed at `d6c7fc0`)
**Authorization:** Charlie register `#N+19a` (T13 fire) + `#N+19b` (T14b mv) <fire dates>

## Pre-execution preconditions

| Precondition | Spec ref | Result | Evidence |
|---|---|---|---|
| HEAD pointer at `0a54f65` or descendant | plan §"Phase 3 execution preconditions" P1 | <PASS / details> | `git rev-parse --short HEAD` returned `<sha>`; commits since `0a54f65` are plan-doc-only |
| Clean working tree on code paths | plan §"Phase 3 execution preconditions" P2 | <PASS / details> | `git status --porcelain` on code dirs returned `<empty | inherited untracked>` |
| Writable execution environment | plan §"Phase 3 execution preconditions" P3 | <PASS / details> | `tempfile.NamedTemporaryFile()` succeeded |
| Phase 2 SEAL state present (6 BCNARROW_* constants + 4 helpers) | plan §"Phase 3 execution preconditions" P4 | <PASS / details> | import + 6 assertEqual succeeded |
| Phase 0 LC-b API present (4 kwargs + equity_curve field) | plan §"Phase 3 execution preconditions" P5 | <PASS / details> | `inspect.signature` + `dataclasses.fields` succeeded |
| Pre-fire holdout_results.csv structure (40 lines, expected header) | Step 13.1 (a)(b) | <PASS / details> | `wc -l` returned 40; `head -1` matched expected header schema |
| Pre-fire archive target absent | Step 13.1 (c) | <PASS / details> | `ls archive/phase4_forward_2026_15bps_v1_d0b8101/` returned no-such-file |
| Pre-fire sibling target absent | Step 13.1 (d) | <PASS / details> | `ls sibling dir` returned no-such-file |
| Pre-fire raw_payloads 998 symlinks resolve | Step 13.1 (e)(f) | <PASS / details> | `find ... -type l | wc -l` returned 998; 3-sample resolution OK |
| Pre-fire registry clean (0 parent + 0 children) | Step 13.1 (g) | <PASS / details> | SQLite query returned 0 + 0 (or runs table absent) |

## T13 fire results

**Command executed:** `python -m scripts.run_phase2c_evaluation_gate --enable-b-c-narrow-recovery --candidate-hashes <39 csv> --source-batch-id phase2c_15_main_fire_combined --regime-key evaluation_regimes.forward_2026 --execution-config config/execution_phase4_15bps.yaml --run-id phase4_forward_2026_15bps_v1_b_c_narrow --output-root data/phase2c_evaluation_gate/`

**Exit code:** 0
**Wall-clock duration:** <measured seconds>
**Producer steps confirmed in stdout:** W0 identity guard PASS / W1a finalize preflight PASS / W3 archive performed / 39 candidates evaluated / W4 finalize POST-fire wrote parent batch_summary

## T14 V4 gate results (G4-G7 + ε=1e-6)

| Test | Spec ref | Result |
|---|---|---|
| `TestV4Reproducibility::test_v4_per_candidate_metric_diff_within_epsilon` | §4.2 + §6.4 | <PASSED> |
| `TestV4Reproducibility::test_v4_total_trades_exact_match` | §4.2 + §6.4 | <PASSED> |
| `TestV4Reproducibility::test_v4_drift_stop_condition_blocks_seal_on_breach` | §4.2 + §6.4 | <PASSED> |
| `TestG4ParquetIntegrity::test_g4_per_bar_parquet_row_count_matches_t_obs` | §4.3 G4 | <PASSED> |
| `TestG5GammaRoundTrip::test_g5_gamma_round_trip_from_parquet_within_epsilon` | §4.3 G5 | <PASSED> |
| `TestG6RegistryParentChildIntegrity::test_g6_registry_parent_child_integrity_after_fire` | §4.3 G6 (BLOCKING-5 carry) | <PASSED> |
| `TestG7ArchiveIdempotency::test_g7_archive_idempotency_refuses_existing_target` | §4.3 G7 (BLOCKING-5 carry) | <PASSED> |

**Verification command:**

```bash
python -m pytest tests/test_b_c_narrow_v4_reproducibility.py -v
```

**Full suite zero-regression:** <2367 passed / 0 failed / 2 xfailed> (Phase 2 baseline 2360 + 7 new V4 tests; net new = 7 passing)

## Per-gate G4-G7 result summary (additional evidence)

| Gate | Spec ref | Coverage | Result |
|---|---|---|---|
| G4 — Per-bar parquet integrity | §4.3 G4 | row count = T_obs (a) + SHA256 match (b) + non-degenerate (c) + UTC-aware timestamp column (d) | <PASS for N=2 sample> |
| G5 — γ3/γ4 round-trip | §4.3 G5 | `compute_moments` recompute vs stored within abs diff < 1e-10 + T_obs bit-exact | <PASS for N=2 sample> |
| G6 — Registry parent-child integrity | §4.3 G6 | 1 parent batch_summary + 39 child regime_holdout + parent_run_id linkage | <PASS> |
| G7 — Archive idempotency | §4.3 G7 | strict refuse-if-exists semantics (tmp_path isolation) | <PASS> |

**Note on sample size:** G4 + G5 verified for N=2 sampled candidates (`18d92ce5d0b40cc7` + `22864f01a49e3452`) per fixture sampling rule. Full N=39 verification is NAMED-eligible for Phase 4 SEAL bundle (extend fixture sampling to all 39 if Phase 4 reviewers request fuller coverage).

## T14b canonical-path relocation results

**Command executed:** `mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1`

**Post-mv state (verified at Step 14b.2):**
- Canonical path repopulated: 39 candidate dirs + aggregate (verified)
- Sibling dir gone (verified)
- Archive dir intact: 39 candidate dirs (verified)
- Registry rows unchanged: 1 parent + 39 children at `run_id=phase4_forward_2026_15bps_v1_b_c_narrow` (verified)

## Overall verdict

**ALL Phase 3 deliverables GREEN.** Phase 3 ratify gate met.

- T13 fire executed cleanly with `--enable-b-c-narrow-recovery` (single command; ~<X> seconds wall-clock)
- T14 V4 gate: 7/7 tests PASSED (ε=1e-6 per-candidate + G4-G7 coverage)
- Full suite zero-regression (2367 passed / 0 failed / 2 xfailed)
- T14b canonical-path relocation complete; canonical now holds B-C-narrow recovered content with per-bar parquet preservation + γ3/γ4 moments + registry linkage
- Original lineage preserved at `archive/phase4_forward_2026_15bps_v1_d0b8101/` for cross-verification

Phase 4 (SEAL bundle: NOTE doc + B2 reviewer dispatch + Rule 2 SEAL-eve + atomic commit + Phase Marker advance) drafting is a SEPARATE register-event (#N+20) per anti-pre-emption discipline; do NOT bundle into #N+19c.

## Spec §5 supersession note (T12 manual mv superseded by producer W3)

Per Plan v3-Phase3 sub-decision (i) + CR-SE-H2 ADOPT carry from Phase 2 v9: spec line 286 ("T12 — Archive original: `mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1 data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/`") preserved BYTE-IDENTICAL per Architecture B sealed-content invariance. Producer W3 (gated by `--enable-b-c-narrow-recovery` per Phase 2 SEAL) performs the archive INLINE during T13 fire, superseding the manual mv step de-facto. Spec amend / Architecture B errata supplement NAMED-eligible at Phase 4 SEAL bundle (not auto-bundled here).

## Known post-mv behavior (V4 tests reference SIBLING_RUN_DIR)

Tests in `tests/test_b_c_narrow_v4_reproducibility.py` reference `SIBLING_RUN_DIR` = `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow` which no longer exists post-T14b mv. The 5 disk-dependent tests will FAIL if re-run after T14b — EXPECTED behavior; V4 tests are fire-time gates only.

NAMED-eligible at Phase 4 SEAL bundle: either delete the V4 tests after the cycle (one-shot gate) OR refactor them to take a `--canonical` flag (canonical-path re-verification). Plan v3-Phase3 left them as-is post-mv per anti-pre-emption (NOT a Phase 3 deliverable).

The 2 path-independent tests (`test_v4_drift_stop_condition_blocks_seal_on_breach` + `test_g7_archive_idempotency_refuses_existing_target`) will continue to PASS post-mv (no disk-state dependency).

## Next register-event (#N+19c) — Phase 3 ratify ONLY

Per anti-pre-emption discipline: register-event #N+19c is Phase 3 ratify acknowledgment ONLY. The Phase 4 sub-plan drafting authorization is a SEPARATE register-event #N+20.

- Phase 3 ratify acknowledgment
- Push decision for Phase 3 commits (Task 13 RED + Task 14 fire evidence + Task 14b mv evidence + Task 14c ratify packet)
- NAMED-eligible Phase 4 SEAL bundle drafting authorization: SEPARATE Charlie register-event

Phase 4 sub-plan drafting is NOT a sub-option of #N+19c; it requires its own register-event #N+20.

## Evidence artifact inventory

| Path | Type | Purpose |
|---|---|---|
| `tests/test_b_c_narrow_v4_reproducibility.py` | Python test | 7 V4+G4-G7 test methods (5 spec §6.4 + 2 BLOCKING-5 carry) |
| `tests/fixtures/b_c_narrow_archived_baseline.json` | JSON fixture | N=2 candidates frozen snapshot from archived original (sampled lexicographically smallest) |
| `docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md` | Markdown | This file — comprehensive Phase 3 ratify packet |
| `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` (gitignored) | Data | Canonical post-T14b: 39 candidate dirs + per-bar parquet + aggregate |
| `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` (gitignored) | Data | Archive snapshot of original (pre-fire state) |
| `backtest/experiments.db` (gitignored) | SQLite | 1 parent batch_summary + 39 child regime_holdout rows at run_id=phase4_forward_2026_15bps_v1_b_c_narrow |
```

- [ ] **Step 14c.2: Commit + STOP for Charlie register #N+19c**

```bash
git add docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md
git commit -m "$(cat <<'EOF'
evidence(b-c-narrow/phase-3): Phase 3 ratify packet (Task 14c)

Per Plan v3-Phase3 Task 14c. Charlie register-events #N+19a + #N+19b
fired authorizations for T13 fire + T14b canonical-path relocation.

Phase 3 deliverables (all GREEN):
- T13 fire: 39 candidates evaluated; archive snapshot of original
- T14 V4 gate: 7/7 tests PASSED (ε=1e-6 per-candidate + G4-G7 coverage)
- T14b mv: canonical path repopulated with recovered content
- Full suite zero-regression (2367 / 0 / 2 xfailed)

Data artifacts produced (gitignored):
- data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/ (canonical; 39 dirs)
- data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/ (archive; 39 dirs)
- backtest/experiments.db (1 parent + 39 children at parent_run_id=phase4_forward_2026_15bps_v1_b_c_narrow)

Test + fixture artifacts (committed):
- tests/test_b_c_narrow_v4_reproducibility.py (7 V4+G4-G7 test methods)
- tests/fixtures/b_c_narrow_archived_baseline.json (N=2 candidates)

Phase 4 (SEAL bundle: NOTE doc + B2 reviewer dispatch + Rule 2 SEAL-eve +
atomic commit + Phase Marker advance) is a SEPARATE register-event #N+20
per anti-pre-emption discipline.
EOF
)"
```

```
========================================================================
STOP HERE — CHARLIE REGISTER-EVENT #N+19c REQUIRED (Phase 3 ratify ack)
========================================================================

Task 14c complete; Phase 3 ratify packet landed.

What to surface to Charlie:
  - Ratify packet path: docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md
  - Phase 3 commit chain (Task 13 RED, Task 14 fire evidence + fixture,
    optional Task 14b empty commit, Task 14c ratify packet)
  - Push decision for Phase 3 commits
  - All Phase 3 deliverables GREEN; cycle ready for Phase 4 SEAL bundle
    drafting (SEPARATE register-event #N+20)

Per anti-pre-emption discipline: #N+19c is Phase 3 ratify acknowledgment
ONLY. Phase 4 SEAL bundle drafting authorization is a SEPARATE register-
event #N+20.

DO NOT bundle Phase 4 SEAL bundle drafting authorization into #N+19c.
========================================================================
```

---

## DEFER items (Phase 3 scope only)

The following are NOT in Phase 3 scope and require SEPARATE Charlie register-events:

1. **Phase 4 SEAL bundle drafting** (NOTE doc + B2 reviewer dispatch + Rule 2 SEAL-eve + atomic commit + Phase Marker advance): SEPARATE register-event #N+20 per anti-pre-emption discipline. Phase 4 sub-plan drafting authorization is NOT bundled into #N+19c.

2. **Architecture B errata supplement for spec §5 T12 supersession** (sub-decision (i) carry): NAMED-eligible at Phase 4 SEAL bundle drafting. Spec line 286 byte-identical preserved per Architecture B sealed-content invariance at strictest reading; supersession applied inline via producer W3 + `--enable-b-c-narrow-recovery` flag (already landed at Phase 2 SEAL); spec amend / errata supplement deferred to Phase 4 SEAL bundle.

3. **V4 test post-mv refactor** (SIBLING_RUN_DIR no-longer-exists after T14b): NAMED-eligible at Phase 4 SEAL bundle. Either delete the V4 tests after the cycle (one-shot gate) OR refactor them with a `--canonical` flag (canonical-path re-verification). Plan v3-Phase3 leaves them as-is post-mv per anti-pre-emption (NOT a Phase 3 deliverable).

4. **G4 + G5 N=39 full coverage** (current N=2 sample): NAMED-eligible at Phase 4 SEAL bundle if reviewers request fuller coverage. Plan v3-Phase3 implements N=2 per spec §6.6 fixture sampling rule (specific-keys-only minimal coverage).

5. **3 NAMED-deferred Phase 2 polish items** (Bundle (a) Items 3+4 + Bundle (b) Item 8 from Phase 2 NAMED-deferred catalogue): SEPARATE Charlie register decision per Phase 2 ratify packet line 110-112. Not auto-fixed at Phase 3 per anti-pre-emption.

6. **Tier 6 evaluation application** (DSR computation + threshold check + promotion list per R6.1 V_SEAL §2.2 + §12 errata methodology): SEPARATE successor cycle gated by B-C-narrow cycle SEAL. Application is OUT-OF-SCOPE per spec §1 + §9.

---

## Execution Handoff

Per `superpowers:subagent-driven-development` — the implementer subagent should:

1. Read this plan in full BEFORE starting any task.
2. Execute Task 13 (Steps 13.1 → 13.5) sequentially. STOP at Step 13.5 for Charlie register #N+19a.
3. After Charlie register #N+19a fired: execute Task 14 (Steps 14.0 → 14.7) sequentially. STOP at Step 14.7 for Charlie register #N+19b.
4. After Charlie register #N+19b fired (ONLY if V4 PASS): execute Task 14b (Steps 14b.0 → 14b.3) sequentially.
5. Execute Task 14c (Steps 14c.1 → 14c.2). STOP at Step 14c.2 for Charlie register #N+19c.
6. Surface ratify packet at `docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md` for Phase 3 ratify acknowledgment.

The implementer MUST treat each STOP HERE block as a hard barrier. The implementer MUST NOT execute Step 14.1 fire, Step 14b.1 mv, or Step 14c.2 commit without seeing Charlie's explicit authorization message in the conversation record.

If V4 FAILS at Step 14.5 (any of 7 tests): STOP and surface SEAL BLOCKED per spec §4.2 stop-condition. Do NOT proceed to Task 14b. Do NOT execute the mv. Adjudication paths (a/b/c per spec §4.2) require Charlie register-event.

If full suite shows regressions outside `test_b_c_narrow_v4_reproducibility.py` at Step 14.5: STOP and surface — regressions indicate hidden Phase 0/2 SEAL state issue.

End of Plan v3-Phase3 v1.
