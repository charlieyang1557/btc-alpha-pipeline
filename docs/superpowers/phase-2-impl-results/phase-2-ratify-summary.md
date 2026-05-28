# B-C-narrow Phase 2 ratify packet

**Date:** 2026-05-28T04:27:45Z
**HEAD commit:** `eda6535`
**Plan version:** v3-Phase2 v11 SEAL-CANDIDATE (sealed at commit `d9b0718`)
**Plan path:** `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-2-producer-tdd-plan.md`
**Spec path:** `docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md` (sealed at `d6c7fc0`)
**Authorization:** Charlie register `EXEC-SUBAGENT-ALL-PHASE-2` 2026-05-27

## Pre-execution preconditions

| Precondition | Result | Evidence |
|---|---|---|
| Clean working tree (PFR R2 HIGH-2/NEW-2 fix v3 carryforward) | PASS (with NOTE) | `git status --porcelain` returned only untracked artifacts (`.codex/`, `AGENTS.md`, `backtest/engine.py,cover`, `coverage.json`, 4 pre-existing untracked plan docs under `docs/superpowers/plans/`). Zero modified tracked files in `backtest/`, `tests/`, `config/`, `scripts/`, `strategies/`, `factors/`. |
| Writable execution environment | PASS | All pytest invocations created tmp_path fixtures successfully without permission errors. |
| Phase 0 SEAL chain present | PASS | LC-b API (`run_id_override` + `source_batch_id` + `parent_run_id_override` + `artifact_dir`) imported and exercised by Test 21 (`test_lcb_e2e_real_engine_writes_parquet_and_registry`) against real `run_regime_holdout` engine call. |
| Phase 1 ratify gate met | PASS | Phase 1 ratify packet sealed at `b10ffb2` (all 4 BLOCKING gates G1+G2+G3+G3.5 PASS per `docs/superpowers/phase-1-gate-results/phase-1-ratify-summary.md`). |

NOTE on untracked working tree: same set of pre-existing untracked artifacts present at Phase 1 ratify (per `phase-1-ratify-summary.md` line 14-17 NOTE) plus the 4 plan documents from the parallel R5.1/R5.2/R6.1 cycle planning work. None of these are imported by any test or by `scripts/run_phase2c_evaluation_gate.py` and cannot affect Phase 2 GREEN-phase semantics.

## Test results

| Test class | Items collected | PASS | FAIL | Status |
|---|---|---|---|---|
| `TestBCNarrowPhase2ProducerEdits` (test_phase2c_evaluation_gate_runner.py) | 32 | 32 | 0 | **GREEN** |
| `TestT1_4_B1_SignatureBackwardCompat` (test_t1_4_backward_compat.py) | 4 | 4 | 0 | **GREEN** |
| Full pytest suite | 2362 | 2360 | 0 (+ 2 xfailed) | **zero regression** |

### Plan template stale-count NOTE (NAMED-eligible post-Task-12 polish)

Plan Step 12.1 expected at lines 3543-3546: "26/26 Phase 2 tests PASS" and "Full suite: 2354 pass / 0 failed / 2 xfailed". Plan Step 12.2 template at line 3574 said `"25 | 25 | 0"` for Phase 2 class and line 3576 said `"2354"` for full suite. **Actual measured is 32 collected (26 distinct test methods + 6 parametrize-expansions: Test 17 identity-guard ×4 fields + Test 25 argparse mutex ×4 combos = 26 methods → 32 collected items)** and **2360 passing in full suite**.

The plan-template predicted-vs-actual discrepancy reflects two factors:
- Plan author predicted +26 net new (the count of distinct test methods authored at Task 9) but pytest reports parametrize-expansions as discrete collected items; both Test 17 and Test 25 use `@pytest.mark.parametrize` with 4 cases each, so 26 methods expand to 32 collected.
- The full suite baseline calculation `b10ffb2 + 26 → 2354` is off by 6 for the same parametrize-expansion reason: `b10ffb2 + 32 → 2360` is the correct arithmetic.

Plan template lines 3543-3546 (Step 12.1) + 3574/3576 (Step 12.2) are stale per AR-SE-R2-L3 / CR-SE-R3-L3 review class (plan-template-vs-measured-output drift in the template-skeleton dimension); **NAMED-eligible for post-Task-12 plan-quality polish at a separate Charlie register-event**. NOT auto-fixed at Task 12 per anti-pre-emption discipline (Task 12 is evidence-artifact production only; plan amendments require Charlie register authorization).

The discrepancy does NOT affect the Phase 2 ratify verdict: all 26 distinct Phase 2 test methods PASS, all 6 parametrize-expansions PASS, full suite shows zero regression vs `b10ffb2` baseline.

## 4 BLOCKING-carry fixes verified

| # | BLOCKING-carry from Phase 0 plan v2 PFR R2 | Status | Evidence |
|---|---|---|---|
| **BLOCKING-1** | R9 finalizer architectural call-order flaw (v2 placed `_finalize_batch_registry` AFTER children written, which then refuses or deletes them). | **FIXED** | Task 10 implementation (`86f75ff`) split R9 into TWO helpers in `scripts/run_phase2c_evaluation_gate.py`: (PRE-flight) `_finalize_batch_registry_preflight_or_raise()` at scripts:1197+ (refuse-if-exists; `--force-rerun-existing` opt-in DELETEs WHERE parent_run_id) and (POST-fire) `_finalize_batch_registry()` at scripts:1292+ (writes parent batch_summary row only). Verified by Phase 2 tests: `test_finalize_batch_registry_writes_parent_row_only`, `test_finalize_batch_registry_parent_idempotency_refuses_duplicate`, `test_finalize_batch_registry_compensating_cleanup_on_partial_failure`, `test_preflight_refuses_before_archive_when_parent_exists`, `test_archive_step_creates_archive_dir_if_absent`, `test_archive_step_refuses_existing_archive_target`, `test_w1_reorder_force_rerun_existing_without_force_leaves_registry_intact` — ALL PASS. |
| **BLOCKING-3** | `_finalize_batch_registry` queries SQLite before `create_table` runs → OperationalError on missing `runs` table. | **FIXED** | Task 10 implementation (`86f75ff`) at `scripts/run_phase2c_evaluation_gate.py:1392` calls `create_table(conn)` immediately before `insert_run(conn, parent_row)` at scripts:1393 inside POST-fire `_finalize_batch_registry`. Per CR2-B2 v3 + CR4-B1 v5 + AR-SE-M3 v9 locks: preflight `_finalize_batch_registry_preflight_or_raise` is TRULY read-only (3-path early-exit via sqlite_master; does NOT call create_table — preserves CB1 dry-run read-only invariant). Twin functions; opposite create_table behavior; differentiated docstrings at scripts:1197-1220 and scripts:1292-1311. Verified by `test_dry_run_with_b_c_narrow_recovery_leaves_state_untouched` (PASS) and `test_finalize_batch_registry_parent_cohort_metadata_complete` (PASS). |
| **BLOCKING-4** | Phase 0 plan v2 test code referenced `_parse_args` — function does NOT exist in `scripts/run_phase2c_evaluation_gate.py`. Actual function is `_build_argparser()` at scripts:726. | **FIXED** | Task 9 (`9a94f39`) added explicit test `test_build_argparser_callable_no_parse_args` in `tests/test_phase2c_evaluation_gate_runner.py::TestBCNarrowPhase2ProducerEdits` that asserts `_build_argparser` is callable AND `_parse_args` is not present in module. ALL 32 Phase 2 producer-edit tests reference `_build_argparser()` (zero references to nonexistent `_parse_args` symbol). Test PASSES at HEAD `eda6535`. |
| **BLOCKING-6** | Phase 0 plan v2 §6.5 "Plan v1 computes exact via grep" for T1.4 4-tuple update — grep-based counting is methodologically wrong per `tests/test_t1_4_backward_compat.py:67-80` §8.1 METHODOLOGY DIVERGENCE NOTE. | **FIXED** | Task 11 (`dd6669d`) used AST classifier at `TestT1_4_B1_SignatureBackwardCompat._enumerate_call_sites()` (tests/test_t1_4_backward_compat.py:422-488) NOT grep. AST classifier dry-run output post-Phase-2-commits (per Task 11 commit message body): 4-tuple **`(prod_count=4, test_count=49, scripts_count=0, dynamic_count=23)`** — **unchanged from prior lock** (no drift; Phase 2 added zero new `_write_to_registry` callers in `backtest/`; new tests use `unittest.mock.patch`; producer's `_finalize_batch_registry` uses `insert_run` NOT `_write_to_registry`; no new dynamic `_write_to_registry(**args)` pattern). Verified by `TestT1_4_B1_SignatureBackwardCompat::test_4_tuple_matches_locked_values` (PASS at HEAD `eda6535`). |

## Phase 2 implementation summary

Producer modifications confined to `scripts/run_phase2c_evaluation_gate.py` (Task 10 sealed at `86f75ff`):
- **9 modify-zones** per plan File Structure table
- **4 NEW helpers:** `_validate_b_c_narrow_recovery_identity_or_raise`, `_archive_canonical_pre_flight`, `_finalize_batch_registry_preflight_or_raise`, `_finalize_batch_registry`
- **2 NEW CLI flags:** `--enable-b-c-narrow-recovery` (default False), `--force-rerun-existing` (default False; mutex with `--dry-run`)

Test extension confined to `tests/test_phase2c_evaluation_gate_runner.py` (Task 9 sealed at `9a94f39`):
- **26 NEW test methods** in `TestBCNarrowPhase2ProducerEdits` class
- Parametrize-expansions: Test 17 ×4 identity fields + Test 25 ×4 argparse mutex combos = **32 collected items**

T1.4 baseline maintenance confined to `tests/test_t1_4_backward_compat.py` (Task 11 sealed at `dd6669d` + line-ref consistency fix at `eda6535`):
- `_B1_LOCKED_4TUPLE` unchanged (no drift per AST classifier)
- `ALLOWED_KWARGS` extended (db_path removed from forbidden set per CB6 single-source DB lock)
- `BASELINE` advanced 2204 → 2236 (B3.4 driver guard)
- B3.4 forbidden-kwarg amendment (v4 → v5)

## Commit chain

| Phase | Commit | Description |
|---|---|---|
| Phase 0 SEAL | `f112599` | engine extension (RegimeHoldoutResult.equity_curve + 4 LC-b kwargs + LC-b internal LineageContext + atomic write-then-registry) |
| Phase 1 SEAL | `b10ffb2` | Phase 1 ratify packet (G1+G2+G3+G3.5 all PASS) |
| Plan v3-Phase2 SEAL | `d9b0718` | Plan v11 SEAL-CANDIDATE (acknowledged at Charlie register #N+13) |
| Task 9 (RED) | `9a94f39` | 26 failing producer-edit tests added |
| Task 10 (GREEN) | `86f75ff` | producer implementation: 9 modify-zones + 4 helpers + 2 CLI flags |
| Task 11 (T1.4 maint) | `dd6669d` | T1.4 baseline maintenance per AST classifier (no drift) |
| Task 11 (consistency) | `eda6535` | T1.4 line-reference consistency fix (code-quality Important) |
| Task 12 (this packet) | THIS COMMIT | Phase 2 ratify packet artifact |

## Overall verdict

**ALL Phase 2 deliverables GREEN.** Phase 2 ratify gate met.

- 32/32 `TestBCNarrowPhase2ProducerEdits` PASS (26 distinct methods + 6 parametrize-expansions)
- 4/4 `TestT1_4_B1_SignatureBackwardCompat` PASS (AST 4-tuple `(4, 49, 0, 23)` unchanged — no drift)
- 2360/2360 full suite PASS + 2 xfailed (zero regression vs `b10ffb2` baseline + 32 net new passing)
- All 4 BLOCKING-carry items from Phase 0 plan v2 PFR R2 verified fixed (BLOCKING-1 R9 split + BLOCKING-3 create_table precondition + BLOCKING-4 `_build_argparser` reference + BLOCKING-6 AST classifier methodology)

Phase 3 fire (T13 producer run + T14 V4 reproducibility gate + T14b canonical-path relocation) drafting is a **SEPARATE register-event (#N+3)** per anti-pre-emption discipline; do NOT bundle into #N+2.

## Next register-event (#N+2) — Phase 2 ratify ONLY

Per anti-pre-emption discipline: register-event #N+2 is Phase 2 ratify acknowledgment ONLY. The Phase 3 fire-plan drafting authorization is a SEPARATE register-event #N+3.

- Phase 2 ratify acknowledgment
- Push decision for Phase 2 implementation commits (`9a94f39` Task 9 + `86f75ff` Task 10 + `dd6669d` Task 11 + `eda6535` consistency fix + Task 12 ratify packet)
- NAMED-eligible plan-quality polish for stale 25/2354 → 32/2360 numbers in plan template (lines 3543-3546, 3574, 3576): SEPARATE Charlie register decision

Phase 3 fire sub-plan drafting is NOT a sub-option of #N+2; it requires its own register-event #N+3.

## Evidence artifact inventory

| Path | Type | Purpose |
|---|---|---|
| `docs/superpowers/phase-2-impl-results/phase-2-ratify-summary.md` | Markdown | This file — comprehensive Phase 2 ratify packet documenting GREEN-phase verification + 4 BLOCKING-carry fix evidence |
