# B-C-narrow Phase 2 — Producer TDD Sub-Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this sub-plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Sub-plan scope:** Phase 2 of B-C-narrow data-recovery cycle ONLY — producer edits at `scripts/run_phase2c_evaluation_gate.py` (9 modify-zones + 4 NEW helpers + 2 NEW CLI flags per cumulative v1-v8 amend cycle; see File Structure table for current breakdown) under strict TDD discipline. NO engine code edits (Phase 0 sealed at `f112599`). NO data writes outside test tmp_path. NO new test files (Phase 3-4 will add `tests/test_b_c_narrow_recovery.py` + `tests/test_b_c_narrow_v4_reproducibility.py` per spec §6.1).

**Sub-plan motivation:** Phase 0 (engine extension; sealed at task level 2026-05-27 per Charlie register `SEAL-TASK-LEVEL`) added `RegimeHoldoutResult.equity_curve` + 4 LC-b kwargs + LC-b internal `LineageContext` construction + atomic write-then-registry sequencing in `run_regime_holdout`. Phase 1 (pre-impl gates; sealed at task level 2026-05-27) returned all 4 BLOCKING gates PASS (G1 engine-diff audit + G2 DSL backward-compat + G3 raw_payloads inventory + G3.5 engine extension smoke pre-satisfied). Phase 2 wires the producer to consume Phase 0's LC-b API and finalize the cohort registry layout. Phase 2 also lands the 4 BLOCKING-carry items deferred from Phase 0 plan v2 PFR R2 — BLOCKING-1 R9 architectural call-order fix + BLOCKING-3 `create_table` precondition + BLOCKING-4 `_parse_args` → `_build_argparser` reference correction + BLOCKING-6 T1.4 grep methodology replaced with AST classifier output. Per Charlie register PV3-SPLIT-BY-PHASE 2026-05-26: per-phase ratify + SEAL discipline preserved.

**Tech Stack:** Python 3.11+, pytest, SQLite (`backtest.experiment_registry`), pathlib, shutil, pandas, argparse. NO new dependencies.

**Cycle context:** R6.1 V_SEAL §10 binding precondition (`d6c7fc0` spec doc); cycle entry Charlie register N1 2026-05-26. Phase 2 is the LARGEST sub-plan (substantively) of the 5-phase B-C-narrow arc (Phase 0 sealed → Phase 1 sealed → Phase 2 this sub-plan → Phase 3 fire → Phase 4 cycle SEAL). Phase 3-4 sub-plans drafted SEPARATELY per Charlie register chain (anti-pre-emption).

---

## Codex BLOCKING-carry fixes addressed in this sub-plan (4 from Phase 0 plan v2 PFR R2)

| # | BLOCKING-carry from Phase 0 plan v2 | Fix applied in this sub-plan |
|---|---|---|
| **BLOCKING-1** | R9 finalizer call-order architectural flaw: original v2 wiring placed `_finalize_batch_registry` AFTER children written, which then refuses or deletes them. | **Task 10**: R9 split into TWO halves — (PRE-flight) `_finalize_batch_registry_preflight_or_raise()` BEFORE candidate loop checks parent_run_id absence (refuse-if-exists; `--force-rerun-existing` opt-in DELETEs WHERE parent_run_id); (POST-fire) `_finalize_batch_registry()` AFTER candidate loop writes the parent batch_summary row only. Children written by engine inside `run_regime_holdout` per Phase 0 sequencing. |
| **BLOCKING-3** | `_finalize_batch_registry` queries SQLite before `create_table` runs → OperationalError on missing `runs` table. | **Task 10 Step 10.4**: `_finalize_batch_registry()` (POST-fire ONLY) imports `create_table` + `get_connection` + `insert_run` from `backtest.experiment_registry` and calls `create_table(conn)` before `insert_run(conn, parent_row_dict)`. Idempotent at POST-fire path. Per v3 CR2-B2 + v5 CR4-B1 + v9 AR-SE-M3 corrections: `_finalize_batch_registry_preflight_or_raise()` (preflight) is TRULY read-only — 3-path early-exit via sqlite_master; does NOT call create_table (would commit DDL → violate CB1 read-only invariant on dry-run path). v1/v2 design said both functions called create_table unconditionally; v3+ split into preflight (no create_table) + POST-fire (with create_table). v9 AR-SE-M3 row update restores ADOPT-trail self-consistency. |
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
| PFR R1 main() PRE-flight chain order (NEW v2 lock per CB1) | (1) identity-guard + idempotency PRE-check (read-only) → (2) existing dry-run exit → (3) archive (destructive) → (4) candidate loop with LC-b kwargs → (5) finalize POST-fire parent row | Charlie register #N+3 (Path 1 AMEND) 2026-05-27 + Codex BLOCKING-1 |
| PFR R1 recovery identity guard (NEW v2 lock per CB2) | When `--enable-b-c-narrow-recovery` set: args.run_id MUST equal BCNARROW_PARENT_RUN_ID; args.regime_key MUST equal BCNARROW_REGIME_KEY; args.execution_config MUST canonicalize to BCNARROW_EXECUTION_CONFIG_PATH; args.source_batch_id MUST equal BCNARROW_SOURCE_BATCH_ID | Charlie register #N+3 + Codex BLOCKING-2 |
| PFR R1 returns_per_bar_path semantics lock (NEW v2 lock per CB5) | Producer stores `"returns_per_bar.parquet"` (bare filename — matches engine's child registry row stamp at engine.py:526+656); resolution context implicit per per-candidate JSON location | Charlie register #N+3 + Advisor BLOCKING-2 |
| PFR R1 SHA single-source lock (NEW v2 lock per CB6) | Producer queries engine-written child registry row via `get_run(conn, child_run_id)` post-engine-return and copies `returns_per_bar_path` + `returns_per_bar_sha256` directly — NO recomputation | Charlie register #N+3 + Advisor BLOCKING-3 |
| PFR R1 cohort_metadata derivation lock (NEW v2 lock per CB3) | `initial_capital = 10_000.0` (engine.run_regime_holdout cash default at engine.py:2324); `fee_model = ConstantSlippage.from_config(execution_config).fee_model_label` (= "effective_15bps_per_side" for 15bps anchor per slippage.py:94-100) — derived NOT hardcoded; matches children's fee_model | Charlie register #N+3 + Codex BLOCKING-3 |
| PFR R1 engine_commit registry stamping (NEW v2 lock per CB4) | Parent row `git_commit` = CORRECTED_WF_ENGINE_COMMIT ("eb1c87f") via engine's OVERRIDE pattern at engine.py:1328-1348; `current_git_sha` = fire-time head_sha (separate column); engine_commit ALSO written to notes JSON for explicit forensic recoverability (registry has no engine_commit column per experiment_registry.py:54-103) | Charlie register #N+3 + Codex BLOCKING-4 |

---

## PFR R1 ADOPT findings applied (Plan v2 amendments)

Per Charlie register #N+3 (Path 1: full AMEND + PFR R2) 2026-05-27. PFR R1 fired as B2 2-leg dispatch (Codex `codex:codex-rescue` + Advisor `quant-research-advisor`); both legs returned NOT-APPROVE; all cited file:line claims orchestrator-verified at HEAD `9b52754` (zero hallucinations from either leg).

**Convergence summary:**
- Both legs flagged 3 BLOCKING semantic-fields (initial_capital + fee_model + LC-b mock keys), expressed as 2 BLOCKING + 1 HIGH at convergent severity.
- Codex-only BLOCKING (4 of 6): dry-run safety (CB1), identity guard (CB2), engine_commit/git_commit semantic (CB4), fee_model literal (subsumed CB3).
- Advisor-only BLOCKING (2 of 6): returns_per_bar_path divergence (CB5), SHA recomputation (CB6).
- Reverse-direction catch: Advisor's empirical-code-verification dimension surfaced CB5+CB6 that Codex's structural-contract dimension missed; vice-versa, Codex's dry-run + identity dimensions caught CB1+CB2 that Advisor missed.
- 1 PUSHBACK on Advisor HIGH-5 (batch_id parent vs children divergence): spec §3.2.3 line 117 EXPLICITLY locks `parent.batch_id = parent_run_id`; deviation would require spec amend (separate Charlie register), NOT plan-level fix.

| # | Severity | Origin | Fix in v2 |
|---|---|---|---|
| CB1 | BLOCKING | Codex BLOCKING-1 + Advisor HIGH-1 | Reorder Step 10.8 main() wiring: (0) identity guard → (1) idempotency PRE-check (read-only) → (2) existing dry-run exit → (3) archive (destructive) → (4) candidate loop → (5) finalize POST. Added Tests 15+16 for dry-run + duplicate-rows no-mutation invariants. |
| CB2 | BLOCKING | Codex BLOCKING-2 | NEW `_validate_b_c_narrow_recovery_identity_or_raise()` validates 4 cohort identity fields (run_id, regime_key, execution_config_path, source_batch_id) BEFORE any mutation. Added Test 17 parametrized over wrong-value-per-field. |
| CB3 | BLOCKING | Codex BLOCKING-3 + Advisor HIGH-6 | cohort_metadata derives `initial_capital = 10_000.0` (engine cash default per engine.py:2324) + `fee_model = ConstantSlippage.from_config(execution_config).fee_model_label` (= "effective_15bps_per_side" per slippage.py:94-100); NO hardcoded "phase4_15bps_v1"; NO hardcoded 100000.0. Updated test_finalize_batch_registry_parent_cohort_metadata_complete + added Test 18 for parent-vs-child consistency. |
| CB4 | BLOCKING | Codex BLOCKING-4 | parent_row["git_commit"] = CORRECTED_WF_ENGINE_COMMIT ("eb1c87f") matching engine's OVERRIDE pattern at engine.py:1328-1348; parent_row["current_git_sha"] = head_sha (separate column); engine_commit ALSO written to notes JSON for explicit forensic recoverability. Updated test_finalize_batch_registry_parent_cohort_metadata_complete. |
| CB5 | BLOCKING | Advisor BLOCKING-2 | Producer stores `"returns_per_bar.parquet"` (bare filename) in summary JSON + CSV; matches engine's child registry row stamp (engine.py:526 + 656). Added Test 19 asserting producer summary.returns_per_bar_path == engine-written child row's returns_per_bar_path. |
| CB6 | BLOCKING | Advisor BLOCKING-3 | Producer queries engine-written child registry row via `get_run(conn, child_run_id)` post-engine-return and copies returns_per_bar_path + returns_per_bar_sha256 directly. No recomputation; engine's atomic write is single source. Updated Test 4 to verify producer SHA == registry child row SHA. |
| H1 | HIGH | Advisor BLOCKING-1 (downgraded post-verification) | Test mocks for `compute_per_bar_returns` updated to `pd.Series([float('nan')] + [0.01] * 2527)` (length 2528, first NaN — matches production at engine.py:394-396); compute_moments mock T_obs=2527 (post-NaN-filter count). 5 test stubs updated. |
| H2 | HIGH | Advisor HIGH-2 | Producer imports `DEFAULT_DB_PATH` explicitly from `backtest.experiment_registry`; threads as explicit default to `_finalize_batch_registry*`. Added Test 20 verifying DEFAULT_DB_PATH constant value (regression guard). |
| H3 | HIGH | Advisor HIGH-3 | Module-top NEW-symbol imports (Step 9.1) wrapped in try/except so collection succeeds at RED phase; individual tests fail with explicit error rather than collection error masking pre-existing test failures in file. |
| M1 | MEDIUM | Codex HIGH-1 + Advisor MEDIUM-1 | Removed `mean`+`std` from all 5 compute_moments mock returns; added Test 22 asserting actual `compute_moments` return keys are exactly {"gamma3","gamma4","T_obs"} (API surface lock). |
| M2 | MEDIUM | Advisor HIGH-4 (downgraded) | Test 9 docstring annotated: exercises DELETE behavior (field-agnostic), not realistic engine-written row shape; realistic e2e deferred to Phase 3 (`tests/test_b_c_narrow_recovery.py`). |
| M3 | MEDIUM | Advisor MEDIUM-3 | `_finalize_batch_registry*` refactored to explicit `conn = get_connection(...); try: with conn: ... finally: conn.close()` pattern; no file handle leak. |
| M4 | MEDIUM | Advisor MEDIUM-4 | Added Test 21 invoking REAL `run_regime_holdout` (no mock) with `dsl_bollinger_zscore_reversion` fixture; verifies LC-b path end-to-end (parquet exists; child registry row LC-stamped; equity_curve populated). |
| M5 | MEDIUM | Advisor MEDIUM-5 | NEW module-level constants at scripts:117 (near `PHASE4_FORWARD_2026_REGIME_KEY`): `BCNARROW_PARENT_RUN_ID` + `BCNARROW_ARCHIVE_BASENAME` + `BCNARROW_SOURCE_BATCH_ID` + `BCNARROW_REGIME_KEY` + `BCNARROW_EXECUTION_CONFIG_PATH`. All literals reference constants. |
| L1 | LOW | Codex LOW-1 | Plan Step 9.3 wording "NameError on import" → "ImportError on import" (Python correct error class). |
| L2 | LOW | Advisor LOW-1 | Removed spurious `# noqa: E402` from new imports in Step 10.1 (E402 directive doesn't apply — no non-import code precedes). |
| L3 | LOW | Advisor LOW-2 | `_finalize_batch_registry` docstring: "Children (39 rows)" → "Child rows (one per evaluated candidate)" (drops cohort_a-specific magic number). |

**Total v2 amendments: 17 ADOPT inline + 1 PUSHBACK (advisor HIGH-5) noted for separate spec adjudication.**

**Test count v1 → v2: 14 → 22 (+ 8 new tests for CB1+CB2+CB3+CB5+H2+M1+M4 + parametrized Test 17 covers all 4 identity-guard fields).**

---

## PFR R2 ADOPT findings applied (Plan v3 amendments)

Per Charlie register #N+4 (Path 1: full AMEND-RE-PFR-R3) 2026-05-27. PFR R2 fired as B2 2-leg dispatch on v2 (`1119a29`); Codex returned NOT-APPROVE (2 BLOCKING + 1 MEDIUM + 2 LOW); Advisor returned APPROVE-WITH-FINDINGS (4 MEDIUM + 2 LOW); B2 reverse-direction confirmed at this iteration (Codex's structural-contract dimension caught 2 BLOCKING that Advisor's empirical-code-verification dimension missed; Advisor caught 3 MEDIUM + 1 LOW that Codex missed). All cited file:line claims orchestrator-verified.

**16 of 17 R1 ADOPT fixes verified correctly applied** in v2. Only CB6 had a secondary-order issue (retained Tests 1/2/3/7/14 not updated to insert child registry row → producer's `get_run` raises). Both legs CONFIRMED **PUSHBACK on Advisor R1 HIGH-5 is SOUND** after independent re-read of spec §3.2.3 line 117 lock.

| # | Severity | Origin | Fix in v3 |
|---|---|---|---|
| CR2-B1 | BLOCKING | Codex PFR R2 BLOCKING-1 | Tests 1/2/3/7/14 (LC-b active mock-engine tests) updated to use shared `_make_fake_engine_with_registry` helper which mirrors Phase 0 engine behavior — creates parquet AND inserts child registry row with LC-stamped fields. Without this, producer's CB6 `get_run(conn, child_run_id)` query raises RuntimeError at GREEN phase. |
| CR2-B2 | BLOCKING | Codex PFR R2 BLOCKING-2 | `_finalize_batch_registry_preflight_or_raise` refactored to be TRULY read-only: (Path 1) DB file absent → treat clean state; (Path 2) DB present but runs table absent → treat clean state; (Path 3) runs table present → query counts WITHOUT calling create_table. The destructive create_table call REMOVED from preflight (was committing DDL even on --dry-run path → violated CB1 read-only invariant). create_table call PRESERVED in POST-fire `_finalize_batch_registry` (which runs after dry-run exit). Test 15 strengthened to assert DB file is unchanged on dry-run path. |
| MR2-1 | MEDIUM | Codex PFR R2 MEDIUM-1 + Advisor PFR R2 MEDIUM-2 (CONVERGENT) | Producer's CB6 read at Step 10.5 refactored from `with get_connection(...) as conn:` → explicit `conn = get_connection(...); try: child_row = get_run(conn, child_run_id); finally: conn.close()` pattern. Matches M3 discipline applied to `_finalize_batch_registry*` in v2. Tests 19+21 cross-validation `with get_connection(...)` blocks also updated to same pattern. |
| MR2-2 | MEDIUM | Advisor PFR R2 MEDIUM-1 | Test 20 hardcoded absolute path `/Users/yutianyang/Documents/GitHub/btc-alpha-pipeline` replaced with `from backtest.experiment_registry import PROJECT_ROOT; expected = PROJECT_ROOT / "backtest" / "experiments.db"`. Test now portable across environments while preserving H2 regression-guard goal. |
| MR2-3 | MEDIUM | Advisor PFR R2 MEDIUM-3 | NEW Test 24 `test_parent_git_commit_matches_child_git_commit_engine_consistency` asserts parent.git_commit == child.git_commit (both = "eb1c87f" via CB4 OVERRIDE pattern). Locks the engine-consistency interpretation of spec §3.2.3 line 117 against future "fixes" that would silently re-align parent.git_commit to literal spec value (506285b). The spec-literal-vs-OVERRIDE tension itself is NAMED-eligible-for-separate-spec-amend-cycle (not in Phase 2 scope per anti-pre-emption). |
| MR2-4 | MEDIUM | Advisor PFR R2 MEDIUM-4 | NEW Test 23 `test_parent_batch_id_diverges_from_child_batch_id_per_spec_lock` asserts parent.batch_id (= BCNARROW_PARENT_RUN_ID) != child.batch_id (= BCNARROW_SOURCE_BATCH_ID). Anti-fragility test locks spec §3.2.3 line 117 PUSHBACK-SOUND invariant against future PRs that would silently align the two via "consistency cleanup". |
| LR2-1 | LOW | Codex PFR R2 LOW-1 + Advisor PFR R2 LOW-1 (CONVERGENT) | Re-add `# noqa: E402` to all new imports in Step 10.1. v2's L2 rationale ("no non-import code precedes") was FACTUALLY WRONG — verified: scripts:89-90 contain `PROJECT_ROOT = ...` + `sys.path.insert(...)` BEFORE the imports block at scripts:92-103; existing imports use noqa for this reason; Ruff at pyproject.toml:61-62 selects E rules so new imports without noqa would fail lint. |
| LR2-2 | LOW | Codex PFR R2 LOW-2 | All CB4 references to engine OVERRIDE pattern citation updated from stale `engine.py:1314` → actual `engine.py:1328-1348`. Codex Mode A verified: line 1314 is inside T_obs revalidation comment; actual OVERRIDE `run_data["git_commit"] = lineage_context.engine_commit` is at engine.py:1348. Affects ~5 plan sites (header table + Step 10.4 docstring + Step 10.5 docstring + Test 6 assertion comment). |
| LR2-3 | LOW (optional) | Advisor PFR R2 LOW-2 | Test 15 dry-run added defensive `if db_path.exists():` check after main() to verify preflight executed against the patched db (catches silent db_path bypass bugs). Not strictly required but inexpensive to add. |

**Total v3 amendments: 9 ADOPT inline (2 BLOCKING + 4 MEDIUM + 3 LOW).**

**Test count v2 → v3: 22 → 24 (+ 2 new tests for MR2-3 git_commit consistency + MR2-4 batch_id asymmetry locks; Tests 1/2/3/7/14 fake_run_regime_holdout uses NEW shared helper but test count unchanged).**

**Convergence/divergence summary**: B2 reverse-direction value reaffirmed at PFR R2 — Codex's structural-contract dimension caught the 2 BLOCKING (CB6 retained-tests break + dry-run create_table mutation) that Advisor's empirical-code-verification dimension missed; Advisor caught the 4 MEDIUM (Test 20 portability + CB4 spec tension + batch_id asymmetry test + CB6 conn leak) that Codex missed. Both legs operationally load-bearing per [feedback_reviewer_routing_subagent_default.md] B2 LOCKED 2026-05-19. Cycle approaching but not at saturation; expected v3 → PFR R3 → cycle saturation (R3 should produce only LOW findings per Phase 0 R3-R5 pattern).

---

## PFR R3 ADOPT findings applied (Plan v4 amendments)

Per Charlie register #N+5 (Path 1: full AMEND-RE-PFR-R4) 2026-05-27. PFR R3 fired as B2 2-leg dispatch on v3 (`02592eb`); Codex returned NOT-APPROVE (1 BLOCKING + 1 MEDIUM + 1 LOW); Advisor returned APPROVE-WITH-FINDINGS (4 MEDIUM + 3 LOW); B2 reverse-direction value re-confirmed (Codex caught CR3-B1 stale inline test bodies via reading code blocks; Advisor caught MR3-1 monkeypatch ineffectiveness via empirical Python execution).

**Both legs RE-VERIFIED PUSHBACK on Advisor R1 HIGH-5 SOUND at R3** — spec §3.2.3 line 117 lock unchanged; Test 23 anti-fragility guard added in v3.

**v3 amend completeness**: 8/9 R2 ADOPT fixes correctly applied; CR2-B1 had a SECONDARY-order oversight — helper + detailed template instructions were added in v3 but the actual Test bodies in Step 9.2 main code block were NOT inline-rewritten (relied on template-only fix). v4 corrects this by inline-rewriting the affected test bodies.

**Meta-discipline learning** (cumulative pattern across v2 + v3 amends): "add helper + template + detailed instructions" pattern is fragile when test bodies in main code block remain unfixed. Implementer reading the test bodies may miss the v2/v3 ADOPT sections' templates. v4 onward: inline-rewrite affected code directly; reserve detailed-instructions sections for design notes only, not as substitute for inline fix.

| # | Severity | Origin | Fix in v4 |
|---|---|---|---|
| CR3-B1 | BLOCKING | Codex PFR R3 BLOCKING-1 | Inline-rewrite Tests 1/2/3/7/14 in Step 9.2 main code block to use `_make_fake_engine_with_registry(...)` helper via `side_effect=self._make_fake_engine_with_registry(...)` + add `db_path=db_path` kwarg to `_evaluate_one_candidate` calls. REPLACES the stale v2 inline `fake_run_regime_holdout` patterns at plan lines 458 / 523 / 784 / 1133 / 1409. The v3 CR2-B1 detailed application instructions section is preserved as design rationale but the test bodies are now the actual source-of-truth (not templates). |
| MR3-1 | MEDIUM | Advisor PFR R3 MEDIUM-1 (empirically verified via Python execution) | Test 15 monkeypatch target changed from `"backtest.experiment_registry.DEFAULT_DB_PATH"` → `"scripts.run_phase2c_evaluation_gate.DEFAULT_DB_PATH"`. Per `from X import Y` binding semantics: when producer does `from backtest.experiment_registry import DEFAULT_DB_PATH`, it creates a LOCAL binding in `scripts.run_phase2c_evaluation_gate`; monkeypatching the experiment_registry module's attribute does NOT redirect the producer's local binding. Without this fix, Test 15 silently passes against real DB (3.8MB at backtest/experiments.db) rather than tmp_path → CB1 dry-run no-mutation invariant not actually verified. |
| MR3-2 | MEDIUM | Codex PFR R3 MEDIUM-1 | Remove stale prose claiming preflight calls `create_table`. v4 attempt INCOMPLETE — cited line numbers (168/2045/2664/2848) were inaccurate per Advisor PFR R4 MEDIUM-1; updated 4 OTHER sites instead. v5 CR4-B1 + MR4-1 fix: actual stale docstring at lines 2090-2091 corrected (per PFR R4 ADOPT below); change-log citations updated to factually correct sites. |
| MR3-3 | MEDIUM | Advisor PFR R3 MEDIUM-2 | Strengthen Test 24 docstring to ALSO explicitly lock `current_git_sha = head_sha` interpretation under NAMED-eligible-for-separate-spec-amend framework (parallel to MR2-3's git_commit tension). Spec literal `current_git_sha (=506285b)` reflects spec drafting staleness; plan uses head_sha (operationally correct per registry convention). Test 24 now explicitly asserts BOTH parent-child engine-consistency on git_commit AND head_sha derivation for current_git_sha. |
| MR3-4 | MEDIUM | Codex PFR R3 LOW-1 (elevated for consistency with MR2-1) | Inline-update Tests 19+21 from `with get_connection(db_path) as conn:` → explicit `conn = get_connection(db_path); try: ...; finally: conn.close()` pattern. Matches MR2-1 producer CB6 read pattern + M3 _finalize_batch_registry* pattern. Consistency across all sqlite conn usage in test code. |
| LR3-1 | LOW | Advisor PFR R3 LOW-1 | Step 9.4 commit message refreshed: headline "22 tests" → "24 tests"; final line "All 14 tests FAIL" → "All 24 tests FAIL"; 10 missing bullet categories appended for Tests 15-24. |
| LR3-2 | LOW | Advisor PFR R3 LOW-2 | Producer's Step 10.1 import block: REMOVE unused `PROJECT_ROOT as REGISTRY_PROJECT_ROOT` alias. Test 20 has its own import (per MR2-2 v3 fix); producer body never references REGISTRY_PROJECT_ROOT. Would fail Ruff F401 if enforced. |
| LR3-3 | LOW | Advisor PFR R3 LOW-3 | Add defensive docstring note to `_finalize_batch_registry_preflight_or_raise` (CR2-B2): "Path 3 assumes runs table has parent_run_id column (true for any DB created via create_table per experiment_registry.py:58+124+167). Theoretical edge case: pre-Phase-1A DB without MIGRATION_COLUMNS would raise OperationalError on COUNT query — no such DB exists in this project; defensive note only." |

**Total v4 amendments: 8 ADOPT inline (1 BLOCKING + 4 MEDIUM + 3 LOW).**

**Test count v3 → v4: 24 unchanged (Tests 1/2/3/7/14 inline-rewritten using existing v3 helper; no new tests added at R3).**

**Cycle status**: PFR R1 17 ADOPT → R2 9 ADOPT → R3 8 ADOPT. Cycle approaching but not at saturation. Per Phase 0 v3→v4→v3.5 precedent: R4 should produce predominantly LOW or APPROVE → Rule 2 SEAL-eve adversarial dispatch (OPERATIONALLY REQUIRED per cumulative 26+ instance empirical pattern) → SEAL. If R4 surfaces new BLOCKING/HIGH, another v5 amend cycle.

---

## PFR R4 ADOPT findings applied (Plan v5 amendments)

Per Charlie register #N+6 (Path 1: full AMEND-RE-PFR-R5) 2026-05-27. PFR R4 fired as B2 2-leg dispatch on v4 (`1ee1a26`); Codex returned APPROVE-WITH-FINDINGS (1 MEDIUM + 1 LOW); Advisor returned APPROVE-WITH-FINDINGS (1 BLOCKING + 1 MEDIUM + 2 LOW). **CONVERGENT BLOCKING**: both legs surfaced the SAME doc-vs-implementation contradiction at plan lines 2090-2091 (preflight docstring still claims `create_table` despite v3 CR2-B2 fix removing it from body) — Codex tier MEDIUM-1; Advisor tier BLOCKING-1. **Adopted Advisor's BLOCKING tier per risk assessment** (implementer reading docstring may re-add create_table → CB1 dry-run regression returns).

7/8 R3 ADOPT verified correctly applied at v4 per both legs. Only MR3-2 incomplete (my v4 edit updated 4 sites that were NOT stale create_table claims; missed the actual preflight function docstring at lines 2090-2091). Root cause: Codex R3 cited wrong line numbers (168/2045/2664/2848); I copied citations into v4 amend without re-grep verification.

**Meta-lesson surfaced by Advisor R4 senior-quant perspective**: "At PFR adoption time, line-number citations should be re-grep-verified by the implementer when applying the fix (not just by the reviewer when surfacing it)." Recurring pattern across reviews: reviewer cites line X → implementer applies fix at line X → line numbers shifted in intervening edits → fix lands at wrong place. NAMED-eligible-for-feedback-memory-codification at separate Charlie register-event (anti-pre-emption: not in Phase 2 plan scope).

**Both legs RE-VERIFIED PUSHBACK on Advisor R1 HIGH-5 SOUND at R4** — spec §3.2.3 line 117 lock; Test 23 anti-fragility guard.

| # | Severity | Origin | Fix in v5 |
|---|---|---|---|
| CR4-B1 | BLOCKING | Convergent — Codex PFR R4 MEDIUM-1 + Advisor PFR R4 BLOCKING-1 | Fix preflight docstring at plan lines 2090-2091. Replace "Open db via get_connection(db_path); ensure runs table exists (create_table is idempotent per BLOCKING-3 fix)" with explicit "TRULY read-only on read path — does NOT call create_table" + 3-path early-exit logic explanation in docstring (matches body comment block at lines 2110-2174). Eliminates doc-vs-implementation contradiction; prevents future implementer from re-adding create_table (which would reintroduce CB1 dry-run mutation regression). |
| MR4-1 | MEDIUM | Advisor PFR R4 MEDIUM-1 | Update MR3-2 change-log table row (line 120) — replace inaccurate citations (168/2045/2664/2848) with explicit acknowledgment that v4 attempt was INCOMPLETE; mark that CR4-B1 v5 fix corrects the actual stale site at lines 2090-2091. Audit-trail integrity per recurring re-grep-at-adoption discipline. |
| LR4-1 | LOW | Codex PFR R4 LOW-1a | Plan line 137 (CR2-B1 detailed application instructions section preamble) "currently use" → past tense / design-rationale framing. Implementer reading after v4 CR3-B1 inline rewrite should not see contradicting "currently use" claim. |
| LR4-2 | LOW | Codex PFR R4 LOW-1b | Plan line 200 (File Structure table) "22 test methods" → "24 test methods". Stale count from before R2 added Tests 23+24. |
| LR4-3 | LOW | Codex PFR R4 LOW-1c | Plan line 2905 (Step 12.1 confirm step; v5 amend imprecisely cited "2852" — corrected to actual location 2905 per LR5-3 v6) "14 tests GREEN" → "24 tests GREEN". Stale count from v1 enumeration. |
| LR4-4 | LOW | Advisor PFR R4 LOW-1 | LR3-3 defensive note citation `experiment_registry.py:167` → either drop (since :58 + :124 already cover parent_run_id column) or replace with `:56` (run_id TEXT PRIMARY KEY which COUNT WHERE run_id = ? query depends on). Lean: replace with `:56` for completeness. |
| LR4-5 | LOW | Advisor PFR R4 LOW-2 | POST-fire `_finalize_batch_registry` docstring (plan lines 2196-2210) updated to explicitly contrast vs preflight: "DISTINCT FROM PREFLIGHT: POST-fire DOES call create_table... Twin functions; opposite create_table behavior; differentiated docstrings." Eliminates twin-function-trap risk for future implementers reading near-identical docstrings. |

**Total v5 amendments: 7 ADOPT inline (1 BLOCKING + 1 MEDIUM + 5 LOW).**

**Test count v4 → v5: 24 unchanged (no new tests at R4; only textual/citation polish + 1 docstring contradiction fix).**

**Cycle status updated**: PFR R1 17 → R2 9 → R3 8 → R4 7. Steady saturation trajectory; all v5 fixes are TEXTUAL (no implementation churn). Predicted R5 → LOW-only or APPROVE → Rule 2 SEAL-eve adversarial dispatch (OPERATIONALLY REQUIRED per cumulative 26+ instance empirical pattern) → Plan SEAL.

---

## PFR R5 ADOPT findings applied (Plan v6 amendments)

Per Charlie register #N+7 (Path 1: full AMEND-RE-PFR-R6 + option (a) argparse rejection for CR5-B1) 2026-05-27. PFR R5 fired as B2 2-leg dispatch on v5 (`49ffc74`); Codex returned NOT-APPROVE (1 BLOCKING + 1 LOW); Advisor returned APPROVE-WITH-FINDINGS (3 LOW). **B2 reverse-direction value AGAIN load-bearing at R5** — Codex caught a real CB1 invariant breach (`--dry-run --enable-b-c-narrow-recovery --force-rerun-existing` combination would DELETE registry rows BEFORE dry-run exit) that Advisor's saturation-expectation lens missed.

**Both legs RE-VERIFIED PUSHBACK on Advisor R1 HIGH-5 SOUND at R5**.

**Saturation-expectation Mode A bias surfaced**: Advisor's own R5 risk disclosure flagged "cycle-saturation expectation pressure (R5 expected to be clean)" — Advisor resisted for textual-stale-count finding (LR5-2) but didn't apply the resistance to CLI flag combinatorics dimension. Codex (without saturation prior) independently caught the BLOCKING via fresh re-derivation. NAMED-eligible-for-feedback-memory-codification at separate Charlie register-event: "Saturation-expectation pressure ≠ saturation evidence; reviewers should re-derive each dimension fresh regardless of prior cycle trajectory."

7/7 v5 R4 ADOPT fixes verified correctly applied at v5 per both legs. The R5 BLOCKING is a NEW dimension (CLI flag combination semantics) not caught at R1-R4 because no prior round had attacked the operator-flag-combinatorics surface.

| # | Severity | Origin | Fix in v6 |
|---|---|---|---|
| CR5-B1 | BLOCKING | Codex PFR R5 BLOCKING-1 | Add argparse mutual-exclusion guard rejecting `--dry-run` + `--force-rerun-existing` combination (option (a) per Charlie register). Operator must consciously choose between dry-run (intent-validation) AND force-rerun-existing (destructive cleanup) — never both. Fail-fast at argparse before any mutation. Matches R9-B-guarded "Charlie manual confirm if parent_run_id re-used" intent. Added Test 25 `test_argparse_rejects_dry_run_plus_force_rerun_existing_combination` (parametrized over single-flag-each + both-flags-set; asserts argparse rejects both-flags-set + no DB mutation). |
| LR5-1 | LOW | Codex PFR R5 LOW-1 | Test class docstring (grep-anchor: `25 methods total in v6`) "14 methods" → "25 methods total in v6+v7 (LR6-2 PFR R6 ADOPT correction: prescription had said '24 in v5' but implementer correctly went to '25' since CR5-B1 added Test 25 in same v6 cycle)". LR7-3 PFR R7 ADOPT v8 systemic-fix correction: prior literal line-number cite "378 (now 404)" was stale at v7 (actual then was 433; now 463 at v8) — per recurring whack-a-mole pattern, citation switched to grep-anchor phrasing per Codex R6 systemic discipline proposal to eliminate brittle line-number coupling. |
| LR5-2 | LOW | Advisor PFR R5 LOW-1 | Plan body (grep-anchor: `all 25 new tests use mocking`) "all 14 new tests use mocking" → "all 25 new tests use mocking" (LR6-2 PFR R6 ADOPT correction: prescription had said '24' but actual is '25'). LR7-3 PFR R7 ADOPT v8 systemic-fix: prior literal line-number cite "2824 (now 2962)" was stale at v7 (actual was 3061; now shifted further at v8) — switched to grep-anchor phrasing. |
| LR5-3 | LOW | Advisor PFR R5 LOW-2 | LR4-3 change-log row citation (grep-anchor: `Step 12.1: Confirm 25 tests GREEN`) "Plan line 2852 (Step 12.1 confirm step)" → grep-anchor reference. LR6-2 PFR R6 ADOPT correction: v6 amend imprecisely cited '2905' (Step 10.11 commit message location); Advisor R6 LOW-2 caught the mis-cite via fresh grep; v7 corrected to '3043' (which was stale at v7 — actual then 3142); LR7-3 PFR R7 ADOPT v8 systemic-fix switched to grep-anchor phrasing per Codex R6 systemic discipline proposal. Recurring re-grep-at-adoption-time meta-lesson per Advisor R4 senior-quant perspective at THREE cycle layers (v5 LR5-3, v6 LR6-2, v7 LR7-3) demonstrably structural failure mode → grep-anchor switch is the fix. Audit-trail integrity. |
| LR5-4 | LOW | Advisor PFR R5 LOW-3 (optional) | Docstring at plan lines 2169-2170 — replace "see CREATE_TABLE_SQL at experiment_registry.py:58 + MIGRATION_COLUMNS at :124 + run_id PRIMARY KEY at :56" with explicit "see parent_run_id in CREATE_TABLE_SQL at experiment_registry.py:58 + in MIGRATION_COLUMNS at :124 + run_id PRIMARY KEY at :56" — disambiguates whether :58/:124 point to the constants themselves or to the parent_run_id row within them (the latter is the intended semantic). |

**Total v6 amendments: 5 ADOPT inline (1 BLOCKING + 4 LOW).**

**Test count v5 → v6: 24 → 25 (+ 1 new Test 25 for CR5-B1 argparse guard).**

**Cycle status updated**: PFR R1 17 → R2 9 → R3 8 → R4 7 → R5 5 (1 BLOCKING + 4 LOW). Cycle still NOT at true saturation; v5 amend was textual but v6 adds 1 real code change (CLI guard) + 1 new test. Predicted R6 → LOW-only or APPROVE → Rule 2 SEAL-eve adversarial dispatch → Plan SEAL.

---

## PFR R6 ADOPT findings applied (Plan v7 amendments)

Per Charlie register #N+8 (Path 1: full AMEND-RE-PFR-R7 + option (b) no-op mocks for CR6-B1) 2026-05-27. PFR R6 fired as B2 2-leg dispatch on v6 (`0ce7066`); Codex returned NOT-APPROVE (1 BLOCKING + 2 LOW); Advisor returned APPROVE-WITH-FINDINGS (1 HIGH + 2 MEDIUM + 2 LOW). **CONVERGENT BLOCKING/HIGH on Test 25 fixture insufficiency** — both legs caught it independently via Test 15 fixture pattern comparison; Codex tier BLOCKING (test would fail at GREEN unavoidably); Advisor tier HIGH. **Adopted Codex tier** per "GREEN gate unachievable" risk.

**B2 reverse-direction value AGAIN at R6** — Advisor explicitly resisted saturation-expectation per their own R5 meta-lesson and produced:
- HIGH-1 / Codex BLOCKING-1 convergent (Test 25 fixture)
- MEDIUM-1 (multiple stale 24-count sites + LR5-3 mis-cite — Codex framed as LOW-1)
- **MEDIUM-2 NEW DIMENSION (Codex missed)**: no partial-state recovery runbook for W3-succeeds-W5/W6-fails operator failure mode (operator-runbook lens dimension)

**Both legs RE-VERIFIED PUSHBACK on Advisor R1 HIGH-5 SOUND at R6**.

**Cycle trajectory non-monotonic**: R5 = 5 ADOPT, R6 = 5 ADOPT. Per Advisor senior-quant analysis: "fix produces new fragile surface" dynamic — CR5-B1 in v6 added Test 25 which itself has fixture gap caught at R6. Once Test 25 fixture closed in v7, expected R7 = LOW-only/APPROVE → Rule 2 SEAL-eve adversarial dispatch (OPERATIONALLY REQUIRED per cumulative 26+ instance empirical pattern) → Plan SEAL.

| # | Severity | Origin | Fix in v7 |
|---|---|---|---|
| CR6-B1 | BLOCKING | Convergent — Codex PFR R6 BLOCKING-1 + Advisor PFR R6 HIGH-1 | Fix Test 25 fixture per option (b) per Charlie register: add `patch("scripts.run_phase2c_evaluation_gate._archive_canonical_pre_flight")` as no-op mock to all 4 parametrized cases. Test 25 specifically targets argparse mutex surface, NOT recovery flow — mocking out downstream W3/W4/W5/W6 keeps test scope tight while allowing should_pass cases to reach the "assert e.code != 2" check without uncaught FileNotFoundError. Add additional mocks for `_capture_phase4_forward_window_metadata`, `_evaluate_one_candidate`, `_write_aggregate_csv`, `_write_aggregate_summary`, `_finalize_batch_registry` to cover all downstream side-effects reachable via should_pass paths. |
| MR6-1 | MEDIUM | Codex PFR R6 LOW-1 elevated + Advisor PFR R6 MEDIUM-1 | Whack-a-mole stale-count cleanup at remaining sites missed by LR5-x (Codex enumerated: 176, 177, 254, 1910, 3084, 3119, 3137). Plus correct Advisor's MEDIUM-1 catch: LR5-3 row mis-cites "line 2905" — Step 12.1 confirm step is actually at line 3043 (line 2905 is in Step 10.11 commit message). Plus update Step 9.4 commit headline (line 1910) "24 failing producer-edit tests (T9; v4 post-PFR R3)" → "25 failing producer-edit tests (T9; v6+v7 post-PFR R6 ADOPT)". This is the 4th cycle of stale-count whack-a-mole (LR3-1 22→24 in v4 + LR4-3 14→24 in v5 + LR5-2 14→25 in v6 + MR6-1 24→25 in v7); per Advisor MEDIUM-1 proposed systemic discipline fix — NAMED-eligible-for-feedback-memory-codification: "When test count changes across PFR rounds, run grep audit for all variant count phrasings + add `# COUNT TARGET (PFR Rn)` markers per-site to make the discipline explicit." NOT in Phase 2 plan scope. |
| MR6-2 | MEDIUM | Advisor PFR R6 MEDIUM-2 (NEW DIMENSION — Codex missed) | Add explicit "Partial-state recovery runbook" subsection to Task 10 covering W3-succeeds-W5/W6-fails failure mode. Operator runbook steps: (1) inspect `archive/phase4_forward_2026_15bps_v1_d0b8101/` to verify state; (2) manually `mv archive/phase4_forward_2026_15bps_v1_d0b8101/ ./phase4_forward_2026_15bps_v1/` to restore canonical; (3) re-run producer with `--force-rerun-existing` flag to clean partial registry rows and retry. Acknowledges destructive-without-atomic-rollback as accepted trade-off for single-operator scope (vs over-engineered try/except-with-rollback wrapper). |
| LR6-1 | LOW | Codex PFR R6 LOW-2 | Normalize Step 10/Step 12 handoff wording to match File Structure table. Step 10 lead-in says "7 modify-zones (per File Structure table)" → "9 modify-zones (per File Structure table)" matching plan line 253. Step 12 ratify handoff at line 3140 "7 modify-zones + 3 NEW functions" → "9 modify-zones + 4 NEW helpers" — count drift due to v2 ADOPT adding `_validate_b_c_narrow_recovery_identity_or_raise` (4th NEW helper). |
| LR6-2 | LOW | Advisor PFR R6 LOW-1 | Update LR5-1 + LR5-2 change-log table row prescription text from "24" → "25" — implementer correctly chose 25 in v6 (Test 25 added in same v6 amend per CR5-B1); change-log audit trail should reflect actual implementation. Plus update LR5-3 row citation per MR6-1: "Plan line 2905" → "Plan line 3043 (Step 12.1 actual location; v6 cite was mis-direction)". |

**Total v7 amendments: 5 ADOPT inline (1 BLOCKING + 2 MEDIUM + 2 LOW).**

**Test count v6 → v7: 25 unchanged (CR6-B1 fixes existing Test 25 fixture; no new tests).**

**Cycle status (post v7 prediction)**: R6 = 5 → R7 expected = LOW-only or APPROVE (per Advisor "Test 25 fixture closure → cycle saturation" prediction). If R7 saturates → Rule 2 SEAL-eve adversarial dispatch is OPERATIONALLY REQUIRED next register-event per [feedback_advisor_own_anchoring_implementation_review.md] cumulative 26+ instance empirical pattern. Phase 0 was 5 PFR rounds; Phase 2 at 7 rounds exceeds Phase 0 but with monotonic-after-R5 trajectory (the R5/R6 plateau at 5 was attributable to "fix produces new fragile surface" dynamic with Test 25; v7 closes that surface).

---

## PFR R7 ADOPT findings applied (Plan v8 amendments)

Per Charlie register #N+9 (Path 2: AMEND-THEN-SEAL-EVE-DIRECT — apply 5 ADOPT inline, commit v8, fire Rule 2 SEAL-eve adversarial dispatch directly skipping standard PFR R8) 2026-05-27. PFR R7 fired as B2 2-leg dispatch on v7 (`78651c6`); Codex returned NOT-APPROVE (2 MEDIUM + 2 LOW); Advisor returned APPROVE-WITH-FINDINGS-LOW-ONLY (2 LOW). **No BLOCKING/HIGH at R7** — cycle saturation near.

**B2 reverse-direction value AGAIN at R7**:
- Codex caught MR6-2 runbook command missing `--force` flag (real operator-workflow bug; runbook command as written would abort at `_check_overwrite_protection` before `--force-rerun-existing` cleanup runs) — Advisor missed via "runbook already added" confidence
- Advisor caught change-log cite-staleness within R6 ADOPT cycle itself (LR5-x cites in change log point to wrong line numbers — recurring fractal pattern at the change-log layer) — Codex framed similar issues at body sites but missed the change-log internal layer
- Convergent on File Structure line 283 stale "24 test methods" (5th cycle of whack-a-mole pattern) — Codex MEDIUM-1, Advisor LOW-1; **adopted Codex MEDIUM tier** (5 cycles of same pattern is structural discipline failure, deserves elevated tier)

**Both legs RE-VERIFIED PUSHBACK on Advisor R1 HIGH-5 SOUND at R7**.

**Cycle decision per Charlie Path 2**: skip standard PFR R8; fire Rule 2 SEAL-eve adversarial dispatch directly on v8. Rationale: SEAL-eve is more adversarial than PFR R8 + Rule 2 OPERATIONALLY REQUIRED regardless; saves redundant round. Advisor R7 senior-quant explicitly recommends this trajectory.

| # | Severity | Origin | Fix in v8 |
|---|---|---|---|
| CR7-M1 | MEDIUM | Codex PFR R7 MEDIUM-1 + Advisor PFR R7 LOW-1 (tier elevated to MEDIUM per 5th-cycle structural discipline failure) | Fix File Structure table row (line 283) — "(24 test methods in v4; 14 from v1 enumeration + 8 NEW per PFR R1 ADOPT for CB1/CB2/CB3/CB5/H2/M1/M4 + 2 NEW per PFR R2 ADOPT for MR2-3/MR2-4..." → "(25 test methods in v6+v7; 14 from v1 enumeration + 8 NEW per PFR R1 ADOPT for CB1/CB2/CB3/CB5/H2/M1/M4 + 2 NEW per PFR R2 ADOPT for MR2-3/MR2-4 + 1 NEW per PFR R5 ADOPT for CR5-B1...". 5th cycle of stale-count whack-a-mole; per Codex R6 systemic discipline proposal, NAMED-eligible-for-feedback-memory-codification "When test count changes across PFR rounds, use grep-anchor cites not line-number cites" at separate Charlie register-event. |
| CR7-M2 | MEDIUM | Codex PFR R7 MEDIUM-2 (NEW dimension — Advisor missed) | Fix partial-state recovery runbook commands (plan lines 3009-3011) to include `--force` flag alongside `--force-rerun-existing`. After W5/W6 failure the B-C-narrow `run_dir` is non-empty; `_check_overwrite_protection` at scripts:844-861 (invoked at scripts:929-931) would ABORT retry BEFORE `--force-rerun-existing` cleanup runs. The two flags have DISTINCT scopes: `--force-rerun-existing` cleans registry rows; `--force` allows overwrite of non-empty `run_dir`. Document both in runbook with explicit scope disambiguation. |
| LR7-1 | LOW | Codex PFR R7 LOW-1 | Top scope header line 5 stale v1-era counts "5 substantive zones + 2 NEW functions + 1 NEW CLI flag" → current "9 modify-zones + 4 NEW helpers + 2 NEW CLI flags". |
| LR7-2 | LOW | Codex PFR R7 LOW-2 | Stale `2352` at line 2972 contradicts computed `2353` (2328 + 25 = 2353). Replace with `2353` for consistency. |
| LR7-3 | LOW | Advisor PFR R7 LOW-2 | Change-log cite-staleness within R6 ADOPT cycle: LR5-1 cite "(now 404)" → "(now 433)"; LR5-2 cite "(now 2962)" → "(now 3061)"; LR5-3 cite "Plan line 3043" → "Plan line 3142". Plus per Codex R6 systemic discipline proposal (NAMED-eligible-for-feedback-memory-codification at separate Charlie register): future PFR cite addendums should use grep-anchor phrasing not literal line numbers ("see grep for 'X methods total'") to eliminate brittle line-number coupling. |

**Total v8 amendments: 5 ADOPT inline (2 MEDIUM + 3 LOW; no BLOCKING/HIGH).**

**Test count v7 → v8: 25 unchanged.**

**Cycle status update**: PFR R1 17 → R2 9 → R3 8 → R4 7 → R5 5 → R6 5 → R7 5 (2 MEDIUM + 3 LOW; no BLOCKING/HIGH). v8 = SEAL-candidate per Charlie Path 2 register; next register-event is Rule 2 SEAL-eve adversarial dispatch (B2 2-leg with MAX adversarial directive) NOT standard PFR R8. Per [feedback_advisor_own_anchoring_implementation_review.md] cumulative 26+ instance empirical pattern, SEAL-eve is OPERATIONALLY REQUIRED final-line-of-defense before SEAL artifact draft.

---

## SEAL-eve ADOPT findings applied (Plan v9 amendments)

Per Charlie register #N+10 (Path 1: full v9 amend with all 10 ADOPT + dispatch SEAL-eve R2 for second-round adversarial verification) 2026-05-27. SEAL-eve fired as Rule 2 adversarial B2 2-leg dispatch on v8 (`ff43945`); Codex returned NOT-APPROVE-V9-AMEND-REQUIRED (2 BLOCKING + 1 HIGH + 1 MEDIUM); Advisor returned APPROVE-WITH-FINDINGS-LOW-ONLY-FLOOR (3 MEDIUM + 4 LOW). **B2 reverse-direction value FULLY VINDICATED at SEAL-eve** — exactly as Advisor's R5/R6/R7 meta-lessons predicted.

**Tier divergence on W1 ordering** (Codex BLOCKING-2 vs Advisor MEDIUM-1; same finding): adopted as HIGH (CR-SE-H1) — between Codex's BLOCKING (audit-trail break) and Advisor's MEDIUM (recovery via re-run with `--force`) tiers. Real state-inconsistency window but recoverable; HIGH severity is appropriate per "halfway between" adjudication.

**Codex caught 3 NEW dimensions** Advisor missed via structural-discipline lens:
- CR-SE-B1: Test 15 doesn't actually enforce dry-run no-mutation invariant (CR2-B2 ADOPT didn't actually land in test body)
- CR-SE-H2: Phase 3 archive handoff inconsistent (plan W3 producer-gated vs spec §5 T12 manual `mv`; spec T13 lacks new flag)
- CR-SE-M1: B-C merge block inserted OUTSIDE candidate-level try/except (violates spec R5 contract; failures abort whole producer instead of `lifecycle_state='holdout_error'`)

**Advisor caught 3 META-LESSON recurrence** Codex missed via execution-trace lens:
- AR-SE-M2: Tests 5+6+8+9 stale fixture values (`100000.0` + `"phase4_15bps_v1"`); v2 ADOPT addressed Tests 6+8 only; Tests 5+9 NOT addressed → 6th cycle of CR3-B1 meta-lesson recurrence
- AR-SE-M3: BLOCKING-3 row at line 20 still says "UNCONDITIONALLY" — describes v1/v2 design; contradicts CR2-B2 v3 preflight/POST-fire split
- LR-SE-1: grep-anchor fix doesn't cover version-strings (Step 9.4 commit headline `v7 post-PFR R6 ADOPT` stale)

**Both legs RE-VERIFIED PUSHBACK on Advisor R1 HIGH-5 SOUND at SEAL-eve**.

**Cycle invariant established**: every round (R1 through SEAL-eve) surfaced NEW dimensions. Saturation expectation wrong 4 times (R5, R6, R7, SEAL-eve). As long as adversarial review continues, new dimensions emerge. Charlie's Path 1 register (full v9 + SEAL-eve R2) explicitly accepts this cycle invariant and chooses additional adversarial verification over Path 2 inline-finalize termination.

| # | Severity | Origin | Fix in v9 |
|---|---|---|---|
| CR-SE-B1 | BLOCKING | Codex SEAL-eve BLOCKING-1 | Strengthen Test 15 to actually enforce dry-run DB no-mutation invariant: assert `not db_path.exists()` for absent-DB case (or snapshot pre-existing DB bytes/schema and assert unchanged); do NOT call `create_table(conn)` inside Test 15 assertion path (the call would create the runs table → mask the very mutation the test is meant to detect). |
| CR-SE-H1 | HIGH (Codex BLOCKING-2 + Advisor MEDIUM-1 → adjudicated HIGH) | Codex SEAL-eve BLOCKING-2 + Advisor SEAL-eve MEDIUM-1 (convergent at finding; tier divergent) | Reorder main() wiring: move `_check_overwrite_protection` BEFORE W1 destructive DELETE. New order: W0 identity guard (read-only) → existing `_check_overwrite_protection` (read-only refusal on non-empty `run_dir` without `--force`) → W1 idempotency + DELETE (destructive, gated by `--force-rerun-existing`) → existing dry-run exit → W3 archive PRE-flight (destructive) → ... eliminates state-inconsistency window where `--force-rerun-existing` without `--force` on non-empty run_dir would DELETE registry rows then abort at overwrite gate. |
| CR-SE-H2 | HIGH | Codex SEAL-eve HIGH-1 | Plan v9 explicitly resolves Phase 3 archive handoff inconsistency. Add note to File Structure or Task 12 ratify section: "Plan v8 W3 producer-gated archive (under `--enable-b-c-narrow-recovery`) SUPERSEDES spec §5 T12 manual `mv` archive command. Phase 3 fire-plan command MUST include `--enable-b-c-narrow-recovery` flag (the spec T13 producer command at spec line 289 was written before W3 producer-archive design was added in v1; updated at this register-event but spec text retained per Architecture-B sealed-content invariance). NAMED-eligible-for-spec-amend at Phase 3 register OR Phase 4 SEAL bundle as errata supplement." |
| CR-SE-M1 | MEDIUM | Codex SEAL-eve MEDIUM-1 | Move B-C merge block at Step 10.5 INSIDE candidate-level `try/except` boundary. Currently block runs AFTER `_per_candidate_summary(...)` at lines 538-548, OUTSIDE the existing `try/except` at lines 508-534. v9 fix: move B-C merge logic INTO the `try` block (after `holdout_result = run_regime_holdout(...)` succeeds) so `compute_per_bar_returns` / `compute_moments` / `get_run(conn, child_run_id)` failures produce `lifecycle_state='holdout_error'` per spec R5 contract rather than aborting the whole producer. |
| AR-SE-M2 | MEDIUM | Advisor SEAL-eve MEDIUM-2 | Inline-rewrite Tests 5 + Test 9 fixture values: `"initial_capital": 100000.0` → `10_000.0`; `"fee_model": "phase4_15bps_v1"` → `"effective_15bps_per_side"`. v2 ADOPT only addressed Tests 6 + 8 of the 4 affected tests; v9 closes the 6th cycle of CR3-B1 meta-lesson recurrence by applying to Tests 5 + 9 inline. |
| AR-SE-M3 | MEDIUM | Advisor SEAL-eve MEDIUM-3 | Update BLOCKING-3 row at line 20 of header table — current "UNCONDITIONALLY" wording describes v1/v2 design where `_finalize_batch_registry` always called create_table. v3 CR2-B2 split into preflight (TRULY read-only; NO create_table) + POST-fire (DOES call create_table). New row text: "Task 10 Step 10.4: `_finalize_batch_registry()` (POST-fire ONLY) imports `create_table` + `get_connection` + `insert_run` from `backtest.experiment_registry` and calls `create_table(conn)` before `insert_run(conn, parent_row_dict)`. Preflight `_finalize_batch_registry_preflight_or_raise()` is TRULY read-only per CR2-B2 v3 — 3-path early-exit via sqlite_master; does NOT call create_table. Idempotent at POST-fire path." |
| LR-SE-1 | LOW | Advisor SEAL-eve LOW-1 | Step 9.4 commit message headline version-string update: `(T9; v7 post-PFR R6 ADOPT)` → `(T9; v9 post-SEAL-eve R1 ADOPT)`. 6th cycle of staleness recurrence at version-string layer (grep-anchor fix doesn't cover version-strings). |
| LR-SE-2 | LOW | Advisor SEAL-eve LOW-2 | Test 16 docstring update: existing wording overclaims "raises RuntimeError BEFORE archive PRE-flight runs" but test body only calls preflight directly, doesn't exercise main() ordering. Update docstring to match what body actually tests (preflight raises on pre-existing parent; canonical filesystem untouched is trivially true since preflight is filesystem-read-only). |
| LR-SE-3 | LOW | Advisor SEAL-eve LOW-3 | Test 21 vestigial `btc_parquet_path` fixture in signature — engine resolves canonical via `_resolve_canonical_parquet_path()`; fixture never used. Drop from signature. |
| LR-SE-4 | LOW | Advisor SEAL-eve LOW-4 | Locked decisions table cross-check (informational; no action required per advisor). |

**Total v9 amendments: 10 ADOPT inline (1 BLOCKING + 2 HIGH + 3 MEDIUM + 4 LOW).**

**Test count v8 → v9: 25 unchanged (all v9 fixes ordering/contract/textual/citation polish).**

**Cycle status update**: SEAL-eve R1 produced 10 ADOPT findings (largest scope since R1's 17). v9 closes all 10 inline. Next register-event: SEAL-eve R2 dispatch per Charlie Path 1 — additional adversarial verification before SEAL artifact draft. Per cycle invariant pattern, SEAL-eve R2 may surface additional NEW dimensions; Path 1 explicitly accepts this for additional rigor over Path α inline-finalize termination.

---

## SEAL-eve R2 ADOPT findings applied (Plan v10 amendments)

Per Charlie register #N+11 (Path 1: full v10 amend + dispatch SEAL-eve R3) 2026-05-27. SEAL-eve R2 fired as Rule 2 adversarial B2 2-leg dispatch on v9 (`551c58c`); Codex returned NOT-APPROVE-V10 (1 HIGH + 1 MEDIUM + 3 LOW); Advisor returned NOT-APPROVE-V10 (1 BLOCKING + 3 MEDIUM + 3 LOW). **CONVERGENT BLOCKING on CR-SE-M1 incompleteness** (Codex tier MEDIUM-1; Advisor tier BLOCKING-1; adjudicated BLOCKING per Advisor risk assessment — implementer applying both blocks would double-execute computation per candidate).

**Cycle invariant DEFINITIVELY ESTABLISHED at 9 rounds**: every prediction of saturation has been WRONG. Advisor R2 senior-quant: "Every round surfaces NEW dimensions. The structural cause: fixing dimension X creates new exposure surface at dimension Y." This R2 round's BLOCKING is 7th cycle CR3-B1 meta-lesson recurrence — v9 added new inside-try block (CR-SE-M1 fix) but did NOT DELETE the old outside-try block at plan:2783-2842; the same template-vs-inline failure mode at producer code body layer.

**Charlie Path 1 re-affirmation**: previous register chose Path 1 (standard amend + SEAL-eve R2); this register also Path 1 (standard amend + SEAL-eve R3) — explicit acceptance of cycle invariant + preference for additional rigor over Path α inline-finalize termination per R6.1 §2.2 narrow patch precedent.

**B2 reverse-direction at SEAL-eve R2**:
- Codex caught HIGH-1 (CR-SE-H1 W1a/W1b split has no main() entrypoint regression test) — Advisor missed
- Advisor caught 3 NEW dimensions Codex missed: cross-FS shutil.move partial-move; canonical basename hardcoded 5× (M5 missed); identity guard doesn't validate --candidate-hashes

**7 of 10 v9 SEAL-eve R1 ADOPT verified correctly applied**; 3 didn't land cleanly:
- CR-SE-M1 partial (NEW block added; OLD block not deleted → convergent BLOCKING)
- LR-SE-2 not applied (Test 16 docstring unchanged at site)
- LR-SE-3 not applied (Test 21 signature unchanged at site)

**Both legs RE-VERIFIED PUSHBACK on Advisor R1 HIGH-5 SOUND at SEAL-eve R2** (10th re-verification across cycle).

| # | Severity | Origin | Fix in v10 |
|---|---|---|---|
| CR-SE-R2-B1 | BLOCKING | Convergent — Codex SEAL-eve R2 MEDIUM-1 + Advisor SEAL-eve R2 BLOCKING-1 (tier adjudicated BLOCKING) | DELETE OLD outside-try B-C-merge code block at plan:2783-2842; keep ONLY the NEW inside-try v9 code block at plan:2703-2779; update Step 10.5 sub-step 3 instruction at plan:2697 to unambiguously direct implementer to the INSIDE-try version. Add explicit "(v9 CR-SE-M1 superseded; this block intentionally removed)" marker where the OLD block was, OR delete the block entirely. Eliminates 7th-cycle CR3-B1 meta-lesson recurrence at producer code body layer. |
| CR-SE-R2-H1 | HIGH | Codex SEAL-eve R2 HIGH-1 | NEW Test 26 — `test_w1_reorder_force_rerun_existing_without_force_leaves_registry_intact`. Main() entrypoint regression test for CR-SE-H1 W1a/W1b state-inconsistency window fix: setup pre-existing parent + child rows + non-empty `run_dir` + `--force-rerun-existing` WITHOUT `--force`; invoke `main()`; assert `main()` returns overwrite-protection rc != 0; assert registry rows REMAIN (NOT deleted by W1b); assert `_archive_canonical_pre_flight` was NOT called. Locks the v9 reorder invariant against future regression. |
| CR-SE-R2-M1 | MEDIUM | Codex SEAL-eve R2 LOW-1 elevated + Advisor SEAL-eve R2 MEDIUM-1 (CONVERGENT) | Inline-apply LR-SE-2 at Test 16 docstring (line 1470-1472) — rewrite to state the test directly exercises `_finalize_batch_registry_preflight_or_raise`; no main() / archive ordering claim (since Test 26 now covers the ordering). |
| CR-SE-R2-M2 | MEDIUM | Codex SEAL-eve R2 LOW-2 elevated + Advisor SEAL-eve R2 MEDIUM-1 (CONVERGENT) | Inline-apply LR-SE-3 at Test 21 signature (line 1664) — remove `btc_parquet_path` from fixture signature (engine resolves canonical via `_resolve_canonical_parquet_path()`). |
| AR-SE-R2-M3 | MEDIUM | Advisor SEAL-eve R2 MEDIUM-2 (NEW DIMENSION) | Add same-FS pre-check at `_archive_canonical_pre_flight` per option (a): `if Path(canonical_path).stat().st_dev != Path(archive_root).resolve().parent.stat().st_dev: raise NotImplementedError(...)`. Defensive against cross-FS shutil.move partial-move (atomic only on same-FS via os.rename; falls back to copy+delete on cross-FS which is NOT atomic). For this project's `data/phase2c_evaluation_gate/` and sibling `data/phase2c_evaluation_gate/archive/` → same FS by construction (sibling dirs under common parent); but defensive check guards against operator misconfiguring `--output-root` to different mount. |
| AR-SE-R2-M4 | MEDIUM | Advisor SEAL-eve R2 MEDIUM-3 (NEW DIMENSION) | Extract `BCNARROW_CANONICAL_BASENAME = "phase4_forward_2026_15bps_v1"` as 6th module constant near other BCNARROW_* constants at scripts:117. Use at W3 producer site (currently hardcoded literal at plan:3045). Test fixtures may retain inline literals (test-fixture-local acceptable). |
| AR-SE-R2-L1 | LOW | Advisor SEAL-eve R2 LOW-1 (NEW DIMENSION) | Identity guard doesn't validate `--candidate-hashes`. NAMED-eligible-for-Phase-3-fire-plan-operator-runbook (defer per Advisor's option c). Out-of-scope for v10 plan amend; document in Phase 3 plan as operator-discipline requirement. |
| AR-SE-R2-L2 | LOW | Advisor SEAL-eve R2 LOW-2 | Replace W1a ternary-expression-as-statement with explicit `if/else`. Current `_finalize_batch_registry_preflight_or_raise(...) if not args.force_rerun_existing else None` → standard `if not args.force_rerun_existing: _finalize_batch_registry_preflight_or_raise(...)` block. Readability fix. |
| AR-SE-R2-L3 | LOW | Advisor SEAL-eve R2 LOW-3 | Uncaught RuntimeError/ValueError from W0/W1a/W1b leaves operator with raw traceback (vs CR5-B1 mutex which uses parser.error for clean exit). NAMED-eligible-for-Phase-3-fire-plan-operator-UX-polish (defer). Out-of-scope for v10. |
| CR-SE-R2-L4 | LOW | Codex SEAL-eve R2 LOW-3 | ADOPT-trail count/version phrasings stale at lines 353 ("v6+v7" should be "v6+") + line 503 ("v6"). Update to version-neutral phrasing OR current v10 to close. |

**Total v10 amendments: 8 inline + 2 NAMED-defer = 10 ADOPT (1 BLOCKING + 1 HIGH + 4 MEDIUM + 4 LOW).**

**Test count v9 → v10: 25 → 26 (+ NEW Test 26 for CR-SE-R2-H1 W1 reorder regression).**

**Cycle status**: PFR R1 17 → R2 9 → R3 8 → R4 7 → R5 5 → R6 5 → R7 5 → SEAL-eve R1 10 → SEAL-eve R2 9 (1 BLOCKING + 1 HIGH + 4 MEDIUM + 4 LOW). Cycle invariant CONFIRMED: every adversarial round surfaces new dimensions. Charlie Path 1 (this register) explicitly continues — additional SEAL-eve R3 verification round.

---

### CR2-B1 detailed application instructions (Tests 1/2/3/7/14 → use shared helper)

The 5 LC-b active mock-engine tests (Tests 1/2/3/7/14) WERE updated in v4 per CR3-B1 to use the new `_make_fake_engine_with_registry` helper method (defined in v3 at the top of TestBCNarrowPhase2ProducerEdits class). v3 ADOPT design rationale: each test in v2 used an inline `def fake_run_regime_holdout(**kwargs): ...; return stub_holdout_result` pattern that did NOT insert the child registry row; without the helper, the producer's CB6 path would have raised `RuntimeError("child registry row missing for run_id=...")` at GREEN phase. v4 inline-rewrite (per CR3-B1 PFR R3 meta-discipline learning — "add helper + template + detailed instructions" is fragile when test bodies remain stale; inline-rewrite affected code directly).

**Update template per affected test**:

```python
    def test_<name>(self, stub_holdout_result, stub_candidate, tmp_path):
        """..."""
        _require_b_c_narrow_symbols()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        artifact_dir_root = output_dir
        db_path = tmp_path / "test_<name>.db"  # NEW: explicit db_path for LC-b path

        # Test 1 only: capture kwargs to assert LC-b kwarg threading
        captured_kwargs: dict = {}  # only for Test 1; omit for Tests 2/3/7/14

        with patch(
            "scripts.run_phase2c_evaluation_gate.run_regime_holdout",
            side_effect=self._make_fake_engine_with_registry(
                stub_result=stub_holdout_result,
                db_path=db_path,
                captured_kwargs=captured_kwargs,  # Test 1 only; omit kwarg otherwise
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
                db_path=db_path,  # NEW: explicit db_path for hermetic test
            )

        # ... test-specific assertions ...
```

**Per-test specifics**:
- **Test 1** (`test_evaluate_one_candidate_threads_4_lcb_kwargs_to_run_regime_holdout`): pass `captured_kwargs={}` to helper; assert 4 LC-b kwargs in captured. Skip the inline `def fake_run_regime_holdout` (use helper instead).
- **Test 2** (`test_evaluate_one_candidate_uses_equity_curve_from_extended_result`): use helper; assert producer fed stub `holdout_result.equity_curve` to `compute_per_bar_returns` via mock.assert_called_once_with check.
- **Test 3** (`test_evaluate_one_candidate_merges_moments_into_summary`): use helper; assert summary dict has gamma3/gamma4/T_obs.
- **Test 7** (`test_finalize_batch_registry_child_run_id_deterministic_scheme`): use helper; assert child run_id_override follows `f"{parent_run_id}_{hypothesis_hash}"` scheme via captured_kwargs.
- **Test 14** (`test_schema_domain_routing_evaluation_for_summary_b_c_extended_for_parquet`): use helper; assert summary has additive B-C-narrow fields + passes check_evaluation_semantics_or_raise.

Per-test artifact_dir mkdir + parquet write code that was inline in v2 (e.g., `artifact_dir = artifact_dir_root / stub_candidate["hypothesis_hash"]; artifact_dir.mkdir(parents=True); (artifact_dir / "returns_per_bar.parquet").write_bytes(b"x")`) is now handled by the helper — REMOVE the inline mkdir/write_bytes from each test body since the helper does it.

---

## File Structure (Phase 2 scope only)

| File | Action | Scope |
|---|---|---|
| `scripts/run_phase2c_evaluation_gate.py` | MODIFY | 9 modify-zones (per Task 10; v2 expanded per PFR R1 ADOPT):<br>• **Imports** (Step 10.1): add `create_table`, `get_connection`, `insert_run`, `get_run`, `DEFAULT_DB_PATH` from `backtest.experiment_registry` (H2); `compute_moments`, `compute_per_bar_returns`, `CORRECTED_WF_ENGINE_COMMIT` from `backtest.engine` (CB4) and `backtest.wf_lineage` (already imported); `load_execution_config`, `ConstantSlippage` from `backtest.execution_model` (CB3 fee_model derivation); `shutil` for archive `move`<br>• **NEW module-level constants** (Step 10.1b; near scripts:117 PHASE4_FORWARD_2026_REGIME_KEY): `BCNARROW_PARENT_RUN_ID = "phase4_forward_2026_15bps_v1_b_c_narrow"` + `BCNARROW_ARCHIVE_BASENAME = "phase4_forward_2026_15bps_v1_d0b8101"` + `BCNARROW_SOURCE_BATCH_ID = "phase2c_15_main_fire_combined"` + `BCNARROW_REGIME_KEY = "evaluation_regimes.forward_2026"` + `BCNARROW_EXECUTION_CONFIG_PATH = "config/execution_phase4_15bps.yaml"` (M5)<br>• **`_build_argparser`** (Step 10.2): add `--enable-b-c-narrow-recovery` + `--force-rerun-existing` boolean flags<br>• **NEW `_validate_b_c_narrow_recovery_identity_or_raise()`** (Step 10.3a; CB2): 4-field cohort identity guard called BEFORE any mutation<br>• **NEW `_archive_canonical_pre_flight()`** (Step 10.3b): destructive archive of canonical → archive_root / BCNARROW_ARCHIVE_BASENAME (refuse-if-exists)<br>• **NEW `_finalize_batch_registry_preflight_or_raise()`** (Step 10.4a): R9 PRE-flight idempotency guard (TRULY read-only per CR2-B2 v3 — 3-path early-exit logic via sqlite_master; refuse-if-exists; `--force-rerun-existing` DELETE WHERE parent_run_id) + explicit `try/finally conn.close()` (M3). NOTE: `create_table` REMOVED from preflight per CR2-B2 v3 (was violating CB1 read-only invariant on dry-run path); create_table runs ONLY in POST-fire `_finalize_batch_registry`.<br>• **NEW `_finalize_batch_registry()`** (Step 10.4b): POST-fire parent row write via `insert_run`; cohort_metadata derived (CB3); parent.git_commit = CORRECTED_WF_ENGINE_COMMIT (CB4 OVERRIDE pattern); engine_commit also in notes JSON; explicit `try/finally conn.close()` (M3)<br>• **`_evaluate_one_candidate`** signature + body (Step 10.5; lines 480-573): add 4 LC-b kwargs (2 NEW); compute moments from equity_curve; query engine-written child registry row for returns_per_bar_path + returns_per_bar_sha256 (CB5 bare filename + CB6 single-source); merge into inline JSON write at lines 550-556<br>• **`_CSV_FIELDS`** (Step 10.6; lines 581-595): add 5 new fields (gamma3, gamma4, T_obs, returns_per_bar_path, returns_per_bar_sha256)<br>• **`_write_aggregate_csv`** (Step 10.7; lines 598-637): emit 5 new fields per row<br>• **`main()`** (Step 10.8; lines 864-1072): REORDERED wiring per CB1 — (0) identity guard (CB2) → (1) idempotency PRE-check (read-only) → (2) existing `_check_overwrite_protection` + dry-run exit (preserved verbatim) → (3) archive PRE-flight (destructive; AFTER dry-run) → (4) existing forward_window_metadata capture → (5) candidate loop with LC-b kwargs threaded → (6) finalize POST-fire parent row (after candidate loop + existing CSV write at line 996; before aggregate JSON write at line 1053) |
| `tests/test_phase2c_evaluation_gate_runner.py` | EXTEND | NEW `TestBCNarrowPhase2ProducerEdits` class (25 test methods in v6+v7; 14 from v1 enumeration + 8 NEW per PFR R1 ADOPT for CB1/CB2/CB3/CB5/H2/M1/M4 + 2 NEW per PFR R2 ADOPT for MR2-3/MR2-4 + 1 NEW per PFR R5 ADOPT for CR5-B1; all bodies full runnable code per Charlie no敷衍 + Phase 0 precedent) |
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

- [ ] **Step 9.1: Verify required imports present at top of `tests/test_phase2c_evaluation_gate_runner.py`** (H3 lazy-import wrapper applied per PFR R1)

```bash
head -50 tests/test_phase2c_evaluation_gate_runner.py
```

Required imports (add at module top if missing). Per H3 fix: NEW-symbol imports are wrapped in `try/except ImportError` so that at RED phase the test file STILL COLLECTS successfully (individual NEW-test tests fail with explicit AttributeError, but pre-existing tests in the file remain visible). Without this wrapper, a single missing NEW symbol fails the whole module collection and hides any pre-existing test regressions:

```python
import json
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# Existing-symbol imports (these symbols exist at Phase 0 SEAL):
from backtest.engine import RegimeHoldoutResult, compute_moments, compute_per_bar_returns
from backtest.experiment_registry import (
    DEFAULT_DB_PATH,  # H2: explicit import for db_path co-location lock + Test 20 regression guard
    create_table,
    get_connection,
    get_run,
    insert_run,
)
from scripts.run_phase2c_evaluation_gate import (
    _CSV_FIELDS,
    _build_argparser,
    _evaluate_one_candidate,
    _write_aggregate_csv,
    _write_aggregate_summary,
)

# H3 fix: NEW-symbol imports wrapped so collection succeeds at RED phase.
# At RED phase these symbols don't exist; tests using them fail individually
# (with explicit error via the _require_new helper below), but the test file
# still collects and ALL OTHER existing tests remain visible.
try:
    from scripts.run_phase2c_evaluation_gate import (
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
```

Note: At RED phase (pre-Task-10), the `try/except` block sets `_BC_NARROW_SYMBOLS_AVAILABLE = False`. Tests in `TestBCNarrowPhase2ProducerEdits` MUST call `_require_b_c_narrow_symbols()` as the first line of each test body — this fails the test with an explicit RED-phase message rather than obscure AttributeError. Pre-existing 9+ tests in the file (lines 110+) collect + run unaffected (H3 fix per Advisor PFR R1).

- [ ] **Step 9.2: Append `TestBCNarrowPhase2ProducerEdits` class to `tests/test_phase2c_evaluation_gate_runner.py`**

Add the following class. Each test body is FULL runnable code — no placeholders, no `# similar to above`, no comment-only methods.

```python
# tests/test_phase2c_evaluation_gate_runner.py — APPEND at end (before any trailing teardowns)


class TestBCNarrowPhase2ProducerEdits:
    """Phase 2 producer-edit tests — 26 methods total in v10 (14 base from v1 enumeration:
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
    # CR3-B1 PFR R3 ADOPT (v4): stale v1 body REMOVED (it asserted producer recomputes
    # SHA from file — superseded by CB5+CB6 v2 rewrite that has producer query the
    # engine-written child registry row for both path + SHA). Test 4 is now the rewritten
    # version `test_evaluate_one_candidate_summary_path_sha_from_engine_registry_row` at
    # the v2 ADOPT section below (line ~1159). DO NOT re-add the v1 body here.

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
```

### v2 PFR R1 ADOPT updates to Step 9.2 (apply BEFORE Step 9.3)

Per Charlie register #N+3 (Path 1 — full AMEND). The test class TestBCNarrowPhase2ProducerEdits
gets in-place updates to existing Tests 4 + 6 + 8 + 9 (per CB3/CB4/CB5/CB6/M2) and 8 NEW tests
(Tests 15-22) appended at end. Implementer applies inline edits to existing tests, then appends
the 8 NEW tests to the same class.

#### Universal update for ALL tests in the class (H3 PFR R1)

Add `_require_b_c_narrow_symbols()` as the FIRST line of every test body in
TestBCNarrowPhase2ProducerEdits. This converts collection-time ImportError on missing NEW
symbols (which would hide ALL pre-existing tests in the file) into per-test AssertionError
with an explicit RED-phase message:

```python
def test_<name>(self, ...):
    """..."""
    _require_b_c_narrow_symbols()  # H3 PFR R1: fail explicit if NEW symbols absent
    # ... rest of test body unchanged ...
```

Apply to all 14 existing tests (Tests 1-14). Replace 14 occurrences.

#### Test 4 REWRITE: `test_evaluate_one_candidate_summary_path_sha_from_engine_registry_row`

**Rename** from `test_evaluate_one_candidate_summary_includes_returns_per_bar_path_sha`.
**Rewrite** per CB5+CB6: producer reads bare filename + SHA from engine-written child
registry row (single source), NOT by recomputing from file.

```python
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
            child_row = get_run(conn, f"{self.PARENT_RUN_ID}_{stub_candidate['hypothesis_hash']}")
        assert summary["returns_per_bar_path"] == child_row["returns_per_bar_path"]
        assert summary["returns_per_bar_sha256"] == child_row["returns_per_bar_sha256"]
```

#### Test 6 UPDATE: cohort_metadata derived values per CB3+CB4

Update cohort_metadata fixture per CB3 (derived initial_capital + fee_model) + CB4 (git_commit
= engine_commit; current_git_sha separate; engine_commit also in notes JSON). Key assertions:

```python
        # CB3 PFR R1 ADOPT: derived values match engine defaults
        assert row.get("initial_capital") == 10_000.0    # engine cash default per engine.py:2324
        assert row.get("fee_model") == "effective_15bps_per_side"  # cost_model.fee_model_label
        # CB4 PFR R1 ADOPT: git_commit = engine_commit (OVERRIDE pattern per engine.py:1328-1348)
        assert row.get("git_commit") == "eb1c87f"        # CORRECTED_WF_ENGINE_COMMIT
        assert row.get("current_git_sha") == "f112599"   # fire-time HEAD (separate column)
        # CB4 PFR R1 ADOPT: engine_commit in notes JSON for forensic recoverability
        notes = json.loads(row.get("notes") or "{}")
        assert notes.get("engine_commit") == "eb1c87f"
```

Update the `cohort_metadata` fixture in Test 6 body: replace `"initial_capital": 100000.0` →
`10_000.0`; replace `"fee_model": "phase4_15bps_v1"` → `"effective_15bps_per_side"`.

#### Test 8 UPDATE + Test 9 UPDATE

For Test 8 (`test_finalize_batch_registry_parent_idempotency_refuses_duplicate`): update
cohort_metadata fixture to use CB3 derived values (`initial_capital=10_000.0`,
`fee_model="effective_15bps_per_side"`). Body assertion behavior unchanged.

For Test 9 (`test_finalize_batch_registry_compensating_cleanup_on_partial_failure`): add
docstring note per M2:

```python
        """Verify --force-rerun-existing DELETEs rows WHERE parent_run_id = '...'
        AND WHERE run_id = '...' (parent itself) before re-fire allowed.

        M2 PFR R1 NOTE: this test exercises the DELETE WHERE query behavior, which
        is field-agnostic — children inserted here are hand-rolled minimal-shape
        rows (NOT realistic engine-written rows with full LC-stamped fields).
        The cleanup mechanism works the same way regardless of row shape, so this
        test is sufficient for verifying the DELETE behavior. Realistic engine-
        written partial-fire state exercise is deferred to the Phase 3 E2E test
        suite (tests/test_b_c_narrow_recovery.py per spec §6.1)."""
```

#### NEW Tests 15-22 (append after existing Test 14)

```python
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
```

---

- [ ] **Step 9.3: Run all 26 new tests — they MUST FAIL (RED)** (L1 PFR R1 fix: wording)

```bash
cd /Users/yutianyang/Documents/GitHub/btc-alpha-pipeline
python -m pytest tests/test_phase2c_evaluation_gate_runner.py::TestBCNarrowPhase2ProducerEdits -v
```

Expected: Per H3 PFR R1 fix, the test file STILL COLLECTS even when NEW symbols are absent (the `try/except ImportError` wrapper in Step 9.1 prevents collection-time failure). Each of the 26 tests fails with explicit AssertionError from `_require_b_c_narrow_symbols()` showing the underlying `ImportError on import` (L1 PFR R1 — wording fixed from "NameError" since Python's missing-symbol error class is `ImportError`, not `NameError`). Some tests may also FAIL with `TypeError: _evaluate_one_candidate() got an unexpected keyword argument 'artifact_dir_root'` or `AttributeError` on missing `_CSV_FIELDS` entries.

If ALL 26 tests pass at this point → SOMETHING WRONG (Task 10 already implemented OR tests are no-ops). Halt and inspect.

- [ ] **Step 9.4: Commit failing tests**

```bash
git add tests/test_phase2c_evaluation_gate_runner.py
git commit -m "test(b-c-narrow/phase-2): add 25 failing producer-edit tests (T9; v9 post-SEAL-eve R1 ADOPT)

Per Plan v3-Phase2 v9 Task 9 (Charlie register chain #N+3 Path 1 + #N+4 Path 1 + #N+5 Path 1 + #N+6 Path 1 + #N+7 Path 1 + #N+8 Path 1 + #N+9 Path 2 + #N+10 Path 1).
26 RED-phase tests = 14 v1 enumeration + 8 NEW per PFR R1 ADOPT + 2 NEW per PFR R2 ADOPT (Tests 23+24 for MR2-3/MR2-4) + 1 NEW per PFR R5 ADOPT (Test 25 for CR5-B1) + 1 NEW per SEAL-eve R2 ADOPT (Test 26 for CR-SE-R2-H1 W1 reorder regression):
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

All 26 tests FAIL at this commit (RED phase). T10 implements producer edits to bring GREEN.

PFR R1 ADOPT additions (Tests 15-22 — 8 tests):
- Test 15 (CB1): --dry-run + --enable-b-c-narrow-recovery no-mutation invariant
- Test 16 (CB1): pre-existing parent row → preflight refuses BEFORE archive
- Test 17 (CB2): identity guard rejects each wrong-value field (parametrized 4 cases)
- Test 18 (CB3): parent metadata derived from engine defaults consistency
- Test 19 (CB5): producer summary.returns_per_bar_path == registry child row value
- Test 20 (H2): DEFAULT_DB_PATH constant regression guard
- Test 21 (M4): LC-b e2e real engine writes parquet + registry
- Test 22 (M1): compute_moments return-keys API surface lock

PFR R2 ADOPT additions (Tests 23-24 — 2 tests):
- Test 23 (MR2-4): parent.batch_id ≠ child.batch_id asymmetry lock per spec §3.2.3 line 117
- Test 24 (MR2-3 + MR3-3): parent.git_commit == child.git_commit engine-consistency lock + current_git_sha distinct-fields invariant"
```

---

### Task 10: Implement producer edits (TDD GREEN)

**Files:**
- Modify: `scripts/run_phase2c_evaluation_gate.py` (9 modify-zones per File Structure table above)

This is the largest task. Implementation order: imports → CLI flags → archive step → finalize step → `_evaluate_one_candidate` → CSV fields → CSV writer → `_aggregate_summary_dict` (NOT touched per spec §3.2.2 — cohort fields already cohort-level) → `main()` wiring → GREEN.

- [ ] **Step 10.1: Add imports (v2 per CB3 + CB4 + H2 + L2 PFR R1 ADOPT)**

Edit `scripts/run_phase2c_evaluation_gate.py` near top of file (after existing imports, around line 87-103). Add:

```python
import shutil  # B-C-narrow Phase 2: archive PRE-flight uses shutil.move

# B-C-narrow Phase 2 v3: producer-side moments compute helpers (Phase 0 SEAL chain f112599).
# v2 per CB6 PFR R1: REMOVED _compute_sha256_file import — producer no longer recomputes
# SHA; queries engine-written child registry row via get_run instead.
# v3 per LR2-1 PFR R2 ADOPT: re-added `# noqa: E402` (lines 89-90 contain non-import code
# `PROJECT_ROOT` + `sys.path.insert` per scripts:89-90; existing imports lines 92-103 use noqa
# for this reason; Ruff at pyproject.toml:61-62 selects E rules).
from backtest.engine import (  # noqa: E402
    compute_moments,
    compute_per_bar_returns,
)
# CB3 PFR R1: fee_model derivation from execution_config — producer reads cost_model.fee_model_label
# (matches engine's children-row stamp at engine.py:1278). NO hardcoded fee_model literal.
from backtest.execution_model import ConstantSlippage, load_execution_config  # noqa: E402
# CB4 PFR R1 + LR2-2 PFR R2: engine_commit OVERRIDE constant for parent row git_commit stamping
# (mirror engine.py:1328-1348 OVERRIDE pattern — `run_data["git_commit"] = lineage_context.engine_commit`
# at engine.py:1348).
from backtest.wf_lineage import CORRECTED_WF_ENGINE_COMMIT  # noqa: E402
# H2 PFR R1: DEFAULT_DB_PATH explicit import for parent-child co-location regression guard
# (Test 20). Producer's `db_path: Path | None = None` kwarg defaults to None → get_connection's
# default → DEFAULT_DB_PATH; engine's run_regime_holdout's db_path defaults likewise. Importing
# the constant explicitly makes the contract visible to the reader.
from backtest.experiment_registry import (  # noqa: E402
    DEFAULT_DB_PATH,
    create_table,
    get_connection,
    get_run,
    insert_run,
)
# LR3-2 PFR R3 ADOPT (v4): REMOVED `PROJECT_ROOT as REGISTRY_PROJECT_ROOT` alias —
# unused in producer body (Test 20 has its own import per MR2-2 v3 fix). Would
# trigger Ruff F401 unused-import if enforced.
```

**LR2-1 PFR R2 ADOPT (v3 correction):** v2 incorrectly removed `# noqa: E402` claiming "no non-import code precedes the imports block" — that claim was FACTUALLY WRONG. Verified at HEAD `9b52754`: scripts:89-90 contain `PROJECT_ROOT = Path(__file__).resolve().parent.parent` and `sys.path.insert(0, str(PROJECT_ROOT))` BEFORE the imports block at scripts:92-103. Existing imports at lines 92-103 carry `# noqa: E402` because of this preceding non-import code. Ruff at `pyproject.toml:61-62` selects E rules; new imports without noqa would fail lint. v3 re-adds noqa to all new imports.

**LR2-2 PFR R2 ADOPT (v3 correction):** Codex Mode A verified actual engine OVERRIDE location: `run_data["git_commit"] = lineage_context.engine_commit` is at `backtest/engine.py:1348`; the citation `engine.py:1328-1348` in v2 was inside an unrelated T_obs revalidation comment. v3 updates all CB4 plan sites (5 locations) to cite `engine.py:1328-1348` (the OVERRIDE block) — see Step 10.4 docstring, Step 10.5 producer body docstring, Test 6 assertion comment.

**Placement:** AFTER the existing `from backtest.engine import run_regime_holdout, RegimeHoldoutResult` block at line 92, AFTER the existing `from backtest.wf_lineage import (...)` block at lines 93-102, and AFTER the existing `from strategies.dsl import StrategyDSL` at line 103. The new imports are additive; existing imports preserved verbatim.

Verify imports resolve cleanly:

```bash
python -c "from scripts.run_phase2c_evaluation_gate import compute_moments, compute_per_bar_returns, ConstantSlippage, load_execution_config, CORRECTED_WF_ENGINE_COMMIT, DEFAULT_DB_PATH, create_table, get_connection, get_run, insert_run; print('v2 imports OK')"
```

Expected: `v2 imports OK`.

- [ ] **Step 10.1b: Add module-level constants block (NEW per M5 PFR R1 ADOPT)**

Add the following constants block immediately after `PHASE4_FORWARD_2026_REGIME_KEY = "evaluation_regimes.forward_2026"` at scripts:117 and BEFORE any function definitions. These named constants replace inline literals throughout the v2 producer + tests:

```python
# ---------------------------------------------------------------------------
# B-C-narrow recovery cycle locked identity constants (per Plan v3-Phase2 v2
# PFR R1 ADOPT M5). All B-C-narrow recovery wiring references these constants;
# NO inline literals. Operator misuse is caught at identity guard (CB2) which
# compares CLI args to these locked values.
#
# Source-of-truth locks (DO NOT change without spec amend):
# - BCNARROW_PARENT_RUN_ID:        spec §2 Q4 + §3.2.3
# - BCNARROW_ARCHIVE_BASENAME:     spec §2 Q3 (uses original `current_git_sha`=d0b8101)
# - BCNARROW_SOURCE_BATCH_ID:      spec §1 + G3 inventory (combined synthetic dir)
# - BCNARROW_REGIME_KEY:           spec §1 cohort_a forward_2026
# - BCNARROW_EXECUTION_CONFIG_PATH: spec §2 Q5 cost anchor lock
# ---------------------------------------------------------------------------
BCNARROW_PARENT_RUN_ID: str = "phase4_forward_2026_15bps_v1_b_c_narrow"
BCNARROW_ARCHIVE_BASENAME: str = "phase4_forward_2026_15bps_v1_d0b8101"
BCNARROW_SOURCE_BATCH_ID: str = "phase2c_15_main_fire_combined"
BCNARROW_REGIME_KEY: str = PHASE4_FORWARD_2026_REGIME_KEY  # alias for clarity at recovery sites
BCNARROW_EXECUTION_CONFIG_PATH: str = "config/execution_phase4_15bps.yaml"
# AR-SE-R2-M4 SEAL-eve R2 ADOPT v10: canonical artifact basename — extracted from
# hardcoded literals at 5 sites (W3 producer call + 4 test fixtures). M5 PFR R1
# ADOPT extracted other BCNARROW_* constants but missed this one; v10 closes
# constant-extraction discipline gap.
BCNARROW_CANONICAL_BASENAME: str = "phase4_forward_2026_15bps_v1"
```

Verify the constants resolve:

```bash
python -c "from scripts.run_phase2c_evaluation_gate import BCNARROW_PARENT_RUN_ID, BCNARROW_ARCHIVE_BASENAME, BCNARROW_SOURCE_BATCH_ID, BCNARROW_REGIME_KEY, BCNARROW_EXECUTION_CONFIG_PATH; print('M5 constants OK')"
```

Expected: `M5 constants OK`.

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
            "manual cleanup required). MUTUALLY EXCLUSIVE with --dry-run per "
            "CR5-B1 PFR R5 ADOPT (v6) — combination rejected at argparse "
            "(operator must consciously choose intent-validation vs destructive cleanup)."
        ),
    )
```

**CR5-B1 PFR R5 ADOPT (v6): argparse mutual-exclusion guard.** Add the following block IMMEDIATELY AFTER `args = _build_argparser().parse_args()` at scripts:881, BEFORE the existing `if args.universe is None and args.candidate_hashes is None:` check at scripts:883:

```python
    # CR5-B1 PFR R5 ADOPT (v6): reject --dry-run + --force-rerun-existing combination.
    # W1 preflight runs BEFORE dry-run exit (per CB1 v3 ordering) and DELETEs registry
    # rows when force_rerun_existing=True; combining with --dry-run would mutate state
    # BEFORE the dry-run exit, violating CB1 read-only invariant. Operator must consciously
    # choose intent-validation (dry-run) vs destructive cleanup (force-rerun-existing).
    if args.dry_run and args.force_rerun_existing:
        parser = _build_argparser()
        parser.error(
            "--dry-run and --force-rerun-existing are MUTUALLY EXCLUSIVE "
            "(CR5-B1 PFR R5 ADOPT v6). Combining them would DELETE registry rows "
            "BEFORE dry-run exits — violating the CB1 read-only invariant. "
            "Choose ONE: --dry-run (intent-validation, no mutation) OR "
            "--force-rerun-existing (destructive cleanup of prior partial state)."
        )
```

Note: `parser.error()` writes the message to stderr + exits with code 2 — fail-fast at argparse-time, before any state-mutating code runs.

- [ ] **Step 10.3a: Add NEW `_validate_b_c_narrow_recovery_identity_or_raise()` function (CB2 PFR R1 ADOPT)**

Per Codex BLOCKING-2: when `--enable-b-c-narrow-recovery` is set, operator could pass mismatched cohort identity (wrong `--run-id`, wrong regime, wrong execution-config, wrong source-batch). Without a fail-fast guard, the archive + DB mutation runs against the wrong cohort silently.

Add the identity guard function in the producer at the same grouped location as `_archive_canonical_pre_flight` (after `_check_overwrite_protection()` at line 861, before `def main():` at line 864). This guard runs FIRST in the recovery PRE-flight chain (per CB1 reorder lock).

```python
def _validate_b_c_narrow_recovery_identity_or_raise(
    run_id: str,
    regime_key: str,
    execution_config_path: Path | None,
    source_batch_id: str,
) -> None:
    """B-C-narrow Phase 2 (CB2 PFR R1 ADOPT): identity guard for recovery flow.

    When --enable-b-c-narrow-recovery is set, this guard validates 4 cohort
    identity fields against locked constants BEFORE any mutation (archive,
    DB write). Fail-fast with explicit per-field rationale.

    Required values (locked at scripts:118-122 module-level constants):
    - run_id == BCNARROW_PARENT_RUN_ID
    - regime_key == BCNARROW_REGIME_KEY
    - execution_config_path canonicalizes to BCNARROW_EXECUTION_CONFIG_PATH
    - source_batch_id == BCNARROW_SOURCE_BATCH_ID

    Order in recovery PRE-flight chain (per CB1 lock):
    1. This guard (read-only)
    2. _finalize_batch_registry_preflight_or_raise (read-only)
    3. (existing) _check_overwrite_protection
    4. (existing) dry-run exit if args.dry_run
    5. _archive_canonical_pre_flight (destructive — first mutation)

    Raises:
        ValueError: with multi-line explicit message listing every wrong field
            and the required value. Operator runs producer with corrected flags.
    """
    errors: list[str] = []
    if run_id != BCNARROW_PARENT_RUN_ID:
        errors.append(
            f"--run-id={run_id!r} must equal {BCNARROW_PARENT_RUN_ID!r} "
            f"(B-C-narrow cohort lock per spec §2 Q4)"
        )
    if regime_key != BCNARROW_REGIME_KEY:
        errors.append(
            f"--regime-key={regime_key!r} must equal {BCNARROW_REGIME_KEY!r} "
            f"(B-C-narrow cohort_a is forward_2026 per spec §1)"
        )
    if execution_config_path is None:
        errors.append(
            f"--execution-config must be {BCNARROW_EXECUTION_CONFIG_PATH!r} "
            f"(cost anchor lock per spec §2 Q5); got None"
        )
    else:
        # Canonicalize: resolve absolute path then take repo-relative form.
        ec_path_obj = Path(execution_config_path).resolve()
        try:
            ec_path_repo_rel = str(ec_path_obj.relative_to(PROJECT_ROOT))
        except ValueError:
            # Path is outside repo root — keep as absolute for the error message
            ec_path_repo_rel = str(ec_path_obj)
        if ec_path_repo_rel != BCNARROW_EXECUTION_CONFIG_PATH:
            errors.append(
                f"--execution-config={ec_path_repo_rel!r} must equal "
                f"{BCNARROW_EXECUTION_CONFIG_PATH!r} (cost anchor lock per spec §2 Q5)"
            )
    if source_batch_id != BCNARROW_SOURCE_BATCH_ID:
        errors.append(
            f"--source-batch-id={source_batch_id!r} must equal "
            f"{BCNARROW_SOURCE_BATCH_ID!r} (combined synthetic dir per "
            f"spec §1 + Phase 1 G3 inventory)"
        )
    if errors:
        raise ValueError(
            "B-C-narrow recovery identity guard (CB2 PFR R1 ADOPT): refusing to "
            "mutate state due to inconsistent cohort identity. The "
            "--enable-b-c-narrow-recovery flag locks the recovery flow to the "
            "specific cohort_a artifact at "
            f"data/phase2c_evaluation_gate/{BCNARROW_ARCHIVE_BASENAME}/ "
            "(per spec §1 + §2 + §3.2.3). All 4 identity fields must match:\n"
            "  - " + "\n  - ".join(errors)
        )
```

- [ ] **Step 10.3b: Add NEW `_archive_canonical_pre_flight()` function**

Add the function in the producer at a stable location — RECOMMENDED: AFTER `_validate_b_c_narrow_recovery_identity_or_raise()` (Step 10.3a) and BEFORE `def main():` at line 864. This keeps R9 helpers grouped with main() preconditions.

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
    # AR-SE-R2-M3 SEAL-eve R2 ADOPT v10: same-FS pre-check before shutil.move.
    # shutil.move is atomic via os.rename ONLY when source + target are on the same
    # filesystem; falls back to copy + delete on cross-FS, which is NOT atomic.
    # Project's data/phase2c_evaluation_gate/ and sibling data/phase2c_evaluation_gate/archive/
    # are same-FS by construction (sibling dirs under common parent). Defensive check
    # guards against operator misconfiguring --output-root to different mount point.
    if canonical_path.stat().st_dev != archive_root.resolve().stat().st_dev:
        raise NotImplementedError(
            f"B-C-narrow archive PRE-flight (AR-SE-R2-M3 v10 cross-FS guard): "
            f"canonical_path {canonical_path} and archive_root {archive_root} are on "
            f"DIFFERENT filesystems (st_dev mismatch). shutil.move falls back to "
            f"non-atomic copy+delete on cross-FS, exposing partial-move failure mode. "
            f"This project's archive convention assumes same-FS (sibling dirs under "
            f"common parent). Operator must ensure --output-root targets same FS as "
            f"the canonical artifact, OR raise spec-amend register for cross-FS support."
        )
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

**CB1 PFR R1 NOTE:** This archive function is DESTRUCTIVE (irreversible from operator's normal mental model). Per CB1 ordering lock, it runs LAST in the PRE-flight chain — AFTER identity guard (Step 10.3a) AND idempotency PRE-check (Step 10.4a) AND existing dry-run exit (scripts:933-944). The wiring sequence in main() (Step 10.8 below) enforces this order.

- [ ] **Step 10.4: Add NEW `_finalize_batch_registry_preflight_or_raise()` + `_finalize_batch_registry()` functions**

Add both functions AFTER `_archive_canonical_pre_flight()` (so all R9 helpers are grouped pre-main):

```python
def _finalize_batch_registry_preflight_or_raise(
    parent_run_id: str,
    force_rerun_existing: bool,
    db_path: Path | None = None,
) -> None:
    """B-C-narrow Phase 2: PRE-flight idempotency guard for parent_run_id (R9-B-guarded).

    Per spec §3.2.3 + BLOCKING-1 R9 PRE-flight split + CR2-B2 v3 + CR4-B1 v5 fix:

    TRULY read-only on read path — does NOT call create_table. The function is
    expected to fire BEFORE the existing dry-run exit (per CB1 ordering); a
    create_table call here would commit DDL (CREATE TABLE IF NOT EXISTS + ALTER
    TABLE migrations per experiment_registry.py:207-219), violating the
    "read-only PRE-flight check before dry-run exit" invariant. The 3-path
    early-exit logic uses sqlite_master read-only detection:

    - Path 1 (DB file absent): treat as clean state; return immediately (no I/O).
    - Path 2 (DB present but runs table absent): treat as clean state; return
      (sqlite_master SELECT is purely read-only).
    - Path 3 (runs table present): query parent + child row counts WITHOUT
      calling create_table.
      - If no rows present: clean state; return.
      - If rows present AND force_rerun_existing=False: raise RuntimeError (refuse).
      - If rows present AND force_rerun_existing=True: DELETE all matching rows
        (children + parent) inside a `with conn:` transaction (commits on success;
        rolls back on exception).

    create_table runs ONLY in POST-fire _finalize_batch_registry (which runs AFTER
    dry-run exit per CB1 wiring), so production write path still ensures table
    existence — just not on the preflight read path.

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
    # CR2-B2 PFR R2 ADOPT (v3): TRULY read-only preflight on the read path.
    # v2 called create_table(conn) here unconditionally; that function commits DDL
    # (CREATE TABLE IF NOT EXISTS + ALTER TABLE migrations per experiment_registry.py:207-219)
    # — violates CB1 "read-only PRE-flight check before dry-run exit" invariant when
    # --dry-run --enable-b-c-narrow-recovery would silently CREATE the runs table on
    # an empty / absent DB. v3 fix: 3-path early-exit logic.
    #
    # Path 1 (DB file absent): treat as clean state; return immediately (no I/O).
    # Path 2 (DB present but runs table absent): treat as clean state; return.
    # Path 3 (runs table present): query counts; raise OR DELETE (DELETE is destructive
    #     and runs only on --force-rerun-existing opt-in; not on dry-run path).
    #
    # The create_table call is PRESERVED in POST-fire _finalize_batch_registry (which
    # runs AFTER dry-run exit), so production write path still ensures the table.
    #
    # LR3-3 PFR R3 ADOPT (v4) DEFENSIVE NOTE: Path 3 assumes runs table has parent_run_id
    # + run_id columns. True for any DB created via create_table (see CREATE_TABLE_SQL
    # at experiment_registry.py — specifically: parent_run_id row in CREATE_TABLE_SQL
    # at :58 + parent_run_id row in MIGRATION_COLUMNS at :124 + run_id TEXT PRIMARY KEY
    # at :56 — LR4-4 PFR R4 ADOPT v5 fix replaced stale :167 citation which actually
    # points to current_git_sha column NOT parent_run_id; LR5-4 PFR R5 ADOPT v6 phrasing
    # precision disambiguated whether :58/:124 point to the constants themselves vs the
    # parent_run_id row within them — latter is intended). Theoretical
    # edge case: pre-Phase-1A legacy DB without parent_run_id column would raise
    # OperationalError on COUNT query — NO such DB exists in this project (no
    # pre-Phase-1A schema preserved); defensive note only. If a future cycle introduces
    # legacy-schema DBs, wrap Path 3 in try/except OperationalError → treat as clean.
    effective_db_path = db_path if db_path is not None else DEFAULT_DB_PATH

    # Path 1: DB file absent → clean state (no file I/O at all).
    if not effective_db_path.exists():
        return

    # M3 PFR R1 fix: explicit try/finally conn.close() pattern; `with conn:` commits
    # on success / rolls back on exception but does NOT close the file handle.
    conn = get_connection(effective_db_path)
    try:
        # Path 2: DB present but runs table absent → clean state.
        # Use sqlite_master read-only query to detect — does NOT trigger CREATE TABLE.
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='runs'"
        )
        if cursor.fetchone() is None:
            # runs table does not exist; no prior rows possible → clean state.
            return

        # Path 3: runs table present → query counts (read-only) + raise/DELETE.
        with conn:
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
            # force_rerun_existing=True: DELETE children + parent (single transaction via `with conn:`)
            conn.execute("DELETE FROM runs WHERE parent_run_id = ?", (parent_run_id,))
            conn.execute("DELETE FROM runs WHERE run_id = ?", (parent_run_id,))
    finally:
        conn.close()


def _finalize_batch_registry(
    parent_run_id: str,
    cohort_metadata: dict[str, Any],
    db_path: Path | None = None,
) -> None:
    """B-C-narrow Phase 2: POST-fire parent batch_summary row write (R9 POST-fire half).

    Per spec §3.2.3 + PFR R1 v2 ADOPT (CB3 + CB4 + L3) + LR4-5 v5 contrast:

    DISTINCT FROM PREFLIGHT: POST-fire DOES call create_table(conn) before insert
    (BLOCKING-3 fix), guaranteeing the runs table exists. The companion preflight
    function `_finalize_batch_registry_preflight_or_raise` is TRULY read-only and
    does NOT call create_table (per CR2-B2 v3) — POST-fire runs AFTER dry-run
    exit so create_table mutation here is acceptable. Twin functions; opposite
    create_table behavior; differentiated docstrings.

    - Open db via get_connection(db_path); call create_table(conn) — ensures
      runs table exists (BLOCKING-3 fix); committed DDL is fine here because
      POST-fire path is past the dry-run gate per CB1 wiring.
    - Build parent row dict with cohort-level fields populated + per-candidate
      metric fields NULL.
    - CB4: parent.git_commit = CORRECTED_WF_ENGINE_COMMIT ("eb1c87f") matching
      engine's OVERRIDE pattern at engine.py:1328-1348 (lc.engine_commit OVERRIDE-writes
      to runs.git_commit column). cohort_metadata["current_git_sha"] populates the
      separate current_git_sha column (fire-time HEAD).
    - CB4 forensic: engine_commit ALSO written to `notes` JSON for explicit
      recoverability (registry has no engine_commit column per
      experiment_registry.py:54-103).
    - insert_run(conn, parent_row_dict).

    Child rows (one per evaluated candidate) are written by engine inside
    run_regime_holdout's _write_to_registry call (Phase 0 sequencing per
    spec §3.1.2). This function writes ONLY the 1 parent row.
    (L3 PFR R1 fix: changed "Children (39 rows)" → generic "child rows per
    evaluated candidate" to drop cohort_a-specific magic number.)

    Args:
        parent_run_id: e.g., BCNARROW_PARENT_RUN_ID
            ("phase4_forward_2026_15bps_v1_b_c_narrow").
        cohort_metadata: dict with required keys (CB3 PFR R1 lock):
            execution_config_path, execution_config_sha256, parquet_data_sha256,
            regime_key, cost_anchor_id, current_git_sha, effective_start,
            initial_capital, fee_model. initial_capital MUST equal engine's
            cash default (10_000.0 per engine.py:2324); fee_model MUST be
            derived via ConstantSlippage.from_config(...).fee_model_label
            (per slippage.py:94-100; matches child rows' fee_model via engine.py:1278).
        db_path: SQLite registry path. Default None → get_connection's default
            (DEFAULT_DB_PATH = backtest/experiments.db per experiment_registry.py:46).
            Default-None co-locates the parent row with engine-written children
            (engine uses same default inside _write_to_registry).
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

    # CB4 PFR R1: parent_row notes JSON includes engine_commit for explicit
    # forensic recoverability. Registry has no engine_commit column; the
    # value is OVERRIDE-stamped into git_commit column (mirrors engine pattern).
    notes_payload = {
        "engine_commit": CORRECTED_WF_ENGINE_COMMIT,
        "cohort": "b_c_narrow_recovery",
        "spec_reference": "docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md (sealed at d6c7fc0)",
    }

    parent_row = {
        "run_id": parent_run_id,
        "run_type": "batch_summary",
        "parent_run_id": None,
        "strategy_name": "cohort_summary",
        "strategy_source": "b_c_narrow_recovery",
        # CB4 PFR R1: git_commit = engine_commit (matches engine OVERRIDE at engine.py:1328-1348).
        # current_git_sha is the separate fire-time HEAD per spec §2 disambiguation table.
        "git_commit": CORRECTED_WF_ENGINE_COMMIT,
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
        "notes": json.dumps(notes_payload),
        # Per-candidate metric fields NULL at parent (spec §3.2.3):
        "sharpe_ratio": None,
        "max_drawdown": None,
        "total_return": None,
        "total_trades": None,
        "hypothesis_hash": None,
        "returns_per_bar_path": None,
        "returns_per_bar_sha256": None,
        "T_obs": None,
        # batch_id = parent_run_id per spec §3.2.3 line 117 EXPLICIT LOCK.
        # PFR R1 PUSHBACK (Advisor HIGH-5): plan follows spec verbatim; if downstream
        # Tier 6 queries are confused by parent.batch_id ≠ children.batch_id, that is a
        # spec-level discussion at separate Charlie register, NOT a Phase 2 plan fix.
        "batch_id": parent_run_id,
    }
    # M3 PFR R1 fix: explicit try/finally conn.close() pattern.
    conn = get_connection(db_path)
    try:
        with conn:
            create_table(conn)  # BLOCKING-3: ensure runs table exists before insert
            insert_run(conn, parent_row)
    finally:
        conn.close()
```

- [ ] **Step 10.5: Edit `_evaluate_one_candidate` — signature + LC-b threading + moments merge + registry-query for path/SHA (v2 per CB5+CB6)**

Edit `scripts/run_phase2c_evaluation_gate.py` at function definition starting line 480.

**Signature change (lines 480-489; v2 expanded):** add 3 NEW kwargs at end (default None preserves backward-compat for all legacy callers). The NEW `db_path` kwarg enables hermetic test isolation AND lets the producer query the same registry the engine wrote to (CB6 single-source SHA lookup).

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
    # B-C-narrow Phase 2 v2 per CB6: db_path threading for registry-query single-source SHA
    # (None → engine + producer both use DEFAULT_DB_PATH; tests pass tmp_path for isolation).
    db_path: Path | None = None,
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

2. Modify the `run_regime_holdout(...)` call at lines 512-519. Add 4 LC-b kwargs + thread `db_path` (passing None when not active is safe per Phase 0 single-gate `lcb_active = artifact_dir is not None`):

```python
        holdout_result = run_regime_holdout(
            dsl=dsl,
            batch_id=source_batch_id,
            parent_run_id=f"phase2c_eval_gate_{run_id}",
            regime_key=regime_key,
            execution_config_path=execution_config_path,
            env_config=env_config_override,
            db_path=db_path,  # CB6: thread to engine so producer's get_run uses same DB
            # B-C-narrow Phase 2 LC-b 4 kwargs (None when artifact_dir_root is None;
            # engine's single-gate lcb_active = artifact_dir is not None → no LC-b path):
            run_id_override=child_run_id_override,
            source_batch_id=source_batch_id if lcb_active else None,
            parent_run_id_override=parent_run_id_override if lcb_active else None,
            artifact_dir=candidate_artifact_dir,
        )
```

3. Add moments compute + registry-derived path+SHA + B-C-narrow field merge AFTER `summary = _per_candidate_summary(...)` block at lines 538-548, BEFORE `candidate_dir = output_dir / candidate["hypothesis_hash"]` at line 550.

**CR-SE-M1 SEAL-eve v9 ADOPT**: the B-C merge block MUST be INSIDE the candidate-level `try/except` boundary (existing try/except at lines 508-534) per spec R5 contract: candidate-level failures produce `lifecycle_state='holdout_error'` + continue to next candidate, NOT abort the whole producer. v1-v8 placed the merge block AFTER the existing try/except → any `compute_per_bar_returns` / `compute_moments` / `get_run(conn, child_run_id)` exception would abort the producer mid-cohort. v9 fix: move merge logic INTO the `try` block (immediately after `holdout_result = run_regime_holdout(...)` succeeds, BEFORE setting `lifecycle_state = "holdout_passed"/"holdout_failed"`).

**v9 fixed structure** (the merge logic moves INSIDE the try block):

```python
    try:
        dsl = _load_dsl_from_response(source_batch_id, candidate["position"])
        holdout_result = run_regime_holdout(
            dsl=dsl,
            batch_id=source_batch_id,
            parent_run_id=f"phase2c_eval_gate_{run_id}",
            regime_key=regime_key,
            execution_config_path=execution_config_path,
            env_config=env_config_override,
            db_path=db_path,
            run_id_override=child_run_id_override,
            source_batch_id=source_batch_id if lcb_active else None,
            parent_run_id_override=parent_run_id_override if lcb_active else None,
            artifact_dir=candidate_artifact_dir,
        )
        # CR-SE-M1 SEAL-eve v9: B-C-narrow merge logic INSIDE try/except — failures
        # in moments compute or registry query → caught as candidate-level
        # 'holdout_error' per spec R5 contract, not whole-producer abort.
        if lcb_active:
            from backtest.engine import compute_per_bar_returns, compute_moments
            returns = compute_per_bar_returns(holdout_result.equity_curve)
            moments = compute_moments(returns)
            # Query engine-written child registry row for path + SHA (CB5+CB6 single-source)
            child_run_id_for_query = child_run_id_override
            _conn = get_connection(db_path)
            try:
                child_row = get_run(_conn, child_run_id_for_query)
            finally:
                _conn.close()
            if child_row is None:
                raise RuntimeError(
                    f"B-C-narrow CB5+CB6: child registry row missing for "
                    f"run_id={child_run_id_for_query!r} after run_regime_holdout returned."
                )
            # Hold moments + path + SHA for merge into summary (set AFTER summary built)
            _bc_narrow_fields = {
                "gamma3": moments.get("gamma3"),
                "gamma4": moments.get("gamma4"),
                "T_obs": moments.get("T_obs"),
                "returns_per_bar_path": child_row.get("returns_per_bar_path"),
                "returns_per_bar_sha256": child_row.get("returns_per_bar_sha256"),
            }
        else:
            _bc_narrow_fields = None
        lifecycle_state = (
            "holdout_passed" if holdout_result.regime_holdout_passed
            else "holdout_failed"
        )
        error_message: str | None = None
    except Exception:
        holdout_result = None
        _bc_narrow_fields = None  # candidate failure → no B-C-narrow merge
        lifecycle_state = "holdout_error"
        error_message = traceback.format_exc()
        # (existing logger.warning preserved)
        ...
    finished = datetime.now(timezone.utc)
    wall_clock = (finished - started).total_seconds()

    summary = _per_candidate_summary(
        candidate=candidate,
        head_sha=head_sha,
        source_batch_id=source_batch_id,
        run_id=run_id,
        regime_key=regime_key,
        holdout_result=holdout_result,
        lifecycle_state=lifecycle_state,
        error_message=error_message,
        wall_clock_seconds=wall_clock,
    )
    # CR-SE-M1 v9: merge B-C-narrow fields if captured in try block (None if
    # candidate failed → no merge; summary lacks fields → backward-compat-safe
    # per existing None-handling in _write_aggregate_csv at Step 10.7).
    if _bc_narrow_fields is not None:
        summary.update(_bc_narrow_fields)
```

The remainder of `_evaluate_one_candidate` (inline JSON write at lines 550-573) is **NOT changed** — `summary` now includes B-C-narrow fields when LC-b path completed cleanly, OR omits them when candidate failed (consistent with spec R5 contract that error-path summaries have NULL metric fields).

**CR-SE-R2-B1 SEAL-eve R2 ADOPT v10 deletion**: the OLD outside-try B-C-merge code block that was here in v1-v9 (added at v1; never removed when CR-SE-M1 v9 added the new INSIDE-try block above) is **INTENTIONALLY REMOVED**. The INSIDE-try block at the `try:` body above (lines ~2703-2779) is the canonical source-of-truth. Implementer must NOT re-introduce an outside-try B-C-merge block. Per CR3-B1 7th-cycle meta-lesson recurrence — when adding new code, DELETE the superseded code in the same edit; do not leave both alongside.

Producer no longer imports or calls `_compute_sha256_file` (v1 used it; v2 removed per CB6 single-source discipline).

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

- [ ] **Step 10.8: Wire identity guard + PRE-flight + archive + POST-fire into `main()` (v2 per CB1+CB2+CB3 PFR R1 ADOPT — REORDERED)**

Edit `scripts/run_phase2c_evaluation_gate.py` `main()` function (lines 864-1072). 

**v9 wiring chain per CR-SE-H1 SEAL-eve ADOPT REORDER** (CB1 lock preserved — read-only checks before dry-run exit; destructive ops after dry-run exit; W1 destructive DELETE now AFTER _check_overwrite_protection read-only refusal):

| Wiring | When | Operation | File:line target | Side-effect type |
|---|---|---|---|---|
| W0 | After argparse (~line 881) + after lineage guard (~line 903) | Identity guard (`_validate_b_c_narrow_recovery_identity_or_raise`) | Insert AFTER lineage guard + AFTER `--regime-key` check at line 901, BEFORE `_load_corrected_candidates` at line 905 | READ-ONLY (raises ValueError) |
| W1a (NEW per CR-SE-H1 v9) | After W0; BEFORE existing `_check_overwrite_protection` at line 929 | Idempotency READ-ONLY check ONLY (call `_finalize_batch_registry_preflight_or_raise(force_rerun_existing=False, ...)` regardless of operator's actual flag value — read-only refusal-detection only) | Insert after W0 | READ-ONLY |
| (existing) | At line 929 | `_check_overwrite_protection(run_dir, args.force)` — refuses non-empty `run_dir` without `--force` | PRESERVED VERBATIM | READ-ONLY (returns 1 to abort) |
| W1b (NEW per CR-SE-H1 v9) | After `_check_overwrite_protection` at line 929; BEFORE dry-run exit at line 933 | Idempotency DELETE if `--force-rerun-existing` (call `_finalize_batch_registry_preflight_or_raise(force_rerun_existing=True, ...)` IF `args.force_rerun_existing`) — destructive DELETE only here, AFTER both identity guard + overwrite-protection passed | Insert between scripts:929 and scripts:933 | DESTRUCTIVE (DELETE only if `--force-rerun-existing`) |
| W2 | (existing) `if args.dry_run` exit at line 933-944 | PRESERVED VERBATIM | (existing behavior) |
| W3 | After `run_dir.mkdir` at line 946 | Archive PRE-flight (`_archive_canonical_pre_flight`) | Insert AFTER `run_dir.mkdir` and BEFORE forward_window_metadata capture at line 954 | DESTRUCTIVE (shutil.move; runs AFTER dry-run exit only) |
| W4 | (existing) forward_window_metadata capture at lines 954-973 | PRESERVED VERBATIM | (existing behavior) |
| W5 | (existing) candidate loop at lines 975-991 | Thread `artifact_dir_root` + `parent_run_id_override` + `db_path` kwargs to `_evaluate_one_candidate` | MODIFIED |
| W6 | (existing) After hashlib computation at lines 1016-1051; BEFORE aggregate JSON write at line 1053 | `_finalize_batch_registry` POST-fire (parent batch_summary row) | Insert between line 1051 and 1053 | WRITE (insert_run) |

**CR-SE-H1 SEAL-eve REORDER rationale**: prior v2-v8 design ran W1 (destructive DELETE gated by `--force-rerun-existing`) BEFORE `_check_overwrite_protection`. Codex SEAL-eve BLOCKING-2 caught the state-inconsistency window: operator passes `--force-rerun-existing` WITHOUT `--force` on non-empty `run_dir` → W1 DELETEs registry rows, then `_check_overwrite_protection` aborts → DB cleaned, filesystem dirty. v9 fix: split W1 into W1a (read-only detection) + W1b (destructive DELETE). W1a runs before `_check_overwrite_protection`; W1b runs AFTER it. If overwrite-protection refuses, W1b's DELETE never executes — operator's state remains intact for diagnosis.

---

**W0 + W1a — read-only PRE-flight chain BEFORE existing `_check_overwrite_protection` (CR-SE-H1 v9 reorder):**

Insert after the lineage guard at line 903 + after the existing `--regime-key` validation at line 901, BEFORE `_load_corrected_candidates(args.source_batch_id)` at line 905:

```python
    head_sha = enforce_corrected_engine_lineage()

    # B-C-narrow Phase 2 (v2 PFR R1 ADOPT + v9 CR-SE-H1 REORDER) — read-only
    # PRE-flight chain gated by --enable-b-c-narrow-recovery. Per CB1 lock +
    # CR-SE-H1: identity guard (W0) + idempotency READ-ONLY check (W1a) fire
    # BEFORE existing _check_overwrite_protection (which is read-only refusal
    # on non-empty run_dir without --force). W1b destructive DELETE moves
    # AFTER _check_overwrite_protection per CR-SE-H1 to eliminate state-
    # inconsistency window (DB cleaned + FS dirty if --force-rerun-existing
    # without --force on non-empty run_dir).
    if args.enable_b_c_narrow_recovery:
        # W0 — CB2: identity guard validates 4 cohort identity fields
        # (run_id, regime_key, execution_config, source_batch_id) against
        # BCNARROW_* constants. Raises ValueError BEFORE any mutation if any
        # field mismatches. Operator misuse caught fast.
        # NOTE: --run-id arg is needed for the identity check; _resolve_run_id
        # is the lookup helper. If --run-id absent, _resolve_run_id mints a
        # UUID4 (scripts:840-841) — identity guard catches that as wrong run_id.
        bcnarrow_proposed_run_id = _resolve_run_id(args)
        _validate_b_c_narrow_recovery_identity_or_raise(
            run_id=bcnarrow_proposed_run_id,
            regime_key=args.regime_key,
            execution_config_path=args.execution_config,
            source_batch_id=args.source_batch_id,
        )
        # W1a (CR-SE-H1 v9; AR-SE-R2-L2 v10 style fix): READ-ONLY idempotency check ONLY.
        # Always pass force_rerun_existing=False here regardless of operator's actual
        # flag value — the destructive DELETE is deferred to W1b which runs AFTER
        # _check_overwrite_protection. W1a's role: refuse fast if parent_run_id pre-
        # exists AND operator did NOT pass --force-rerun-existing. If operator DID
        # pass --force-rerun-existing, skip W1a refusal check (operator has explicitly
        # authorized DELETE; W1b will handle it). If operator did NOT pass --force-
        # rerun-existing AND parent exists, W1a raises RuntimeError below and we never
        # reach _check_overwrite_protection.
        # AR-SE-R2-L2 v10 SEAL-eve R2 ADOPT: replaced ternary-expression-as-statement
        # form with explicit if/else for readability — prior `func(...) if cond else None`
        # pattern was readability-fragile.
        if not args.force_rerun_existing:
            _finalize_batch_registry_preflight_or_raise(
                parent_run_id=bcnarrow_proposed_run_id,
                force_rerun_existing=False,  # W1a is read-only-detection only
                db_path=None,
            )
        # else: operator authorized DELETE via --force-rerun-existing; skip W1a
        # refusal check; W1b at line ~3014 below will handle the DELETE.

    all_candidates = _load_corrected_candidates(args.source_batch_id)
```

**W1b — DESTRUCTIVE DELETE AFTER `_check_overwrite_protection` (CR-SE-H1 v9 NEW):**

Insert AFTER existing `rc = _check_overwrite_protection(run_dir, args.force)` at scripts:929 + the `if rc is not None: return rc` at scripts:930-931, BEFORE existing `if args.dry_run:` at scripts:933:

```python
    rc = _check_overwrite_protection(run_dir, args.force)
    if rc is not None:
        return rc

    # W1b (CR-SE-H1 v9): destructive DELETE — runs ONLY when --force-rerun-existing
    # is set AND we've passed the read-only refusal gates (identity guard W0 + W1a
    # idempotency-detect + _check_overwrite_protection). If any prior gate would
    # have refused the request, W1b never executes — no DB mutation occurs.
    # Eliminates Codex SEAL-eve BLOCKING-2 state-inconsistency window where
    # --force-rerun-existing without --force on non-empty run_dir would DELETE
    # registry rows then abort at overwrite gate.
    if args.enable_b_c_narrow_recovery and args.force_rerun_existing:
        _finalize_batch_registry_preflight_or_raise(
            parent_run_id=bcnarrow_proposed_run_id,
            force_rerun_existing=True,  # actual DELETE branch
            db_path=None,
        )
```

---

**W2 — existing dry-run exit (PRESERVED VERBATIM):**

No code change. The existing `if args.dry_run:` block at scripts:933-944 runs unchanged. With CB1 reorder, W0+W1 already ran (validating intent) but W3 (archive) has NOT yet run, so dry-run exits with NO state mutation.

---

**W3 — archive PRE-flight (DESTRUCTIVE; AFTER dry-run exit per CB1):**

Insert AFTER `run_dir.mkdir(parents=True, exist_ok=True)` at line 946 and BEFORE the existing `forward_window_metadata` capture at line 954:

```python
    run_dir.mkdir(parents=True, exist_ok=True)
    run_started_utc = _utc_now_iso()

    # B-C-narrow Phase 2 (v2 per CB1 PFR R1 ADOPT) — DESTRUCTIVE archive.
    # Runs AFTER dry-run exit (W2 preserved); operator confirmed by reaching here.
    # Per CB1: archive is LAST step of PRE-flight chain so that any earlier
    # read-only refusal (identity guard W0, idempotency check W1, dry-run W2)
    # leaves the canonical artifact in place.
    if args.enable_b_c_narrow_recovery:
        canonical_phase4_path = Path(args.output_root).resolve() / "phase4_forward_2026_15bps_v1"
        archive_root = Path(args.output_root).resolve() / "archive"
        _archive_canonical_pre_flight(
            canonical_path=canonical_phase4_path,
            archive_root=archive_root,
            archive_basename=BCNARROW_ARCHIVE_BASENAME,  # M5 PFR R1: named constant
        )
```

---

**W5 — modified candidate loop (thread artifact_dir_root + parent_run_id_override + db_path):**

Modify the existing loop at scripts:975-991:

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
            # CB6 v2 PFR R1: db_path threading for registry-query single-source SHA.
            # None → producer + engine both use DEFAULT_DB_PATH (co-located).
            db_path=None,
        )
        summaries.append(s)
```

---

**W6 — POST-fire parent batch_summary row (CB3 v2 — DERIVED metadata, NOT hardcoded):**

Insert AFTER scripts:1051 (`aggregate["forward_window_metadata"] = ...`) and BEFORE scripts:1053 (`_write_aggregate_summary` call):

```python
    # B-C-narrow Phase 2 POST-fire (v2 PFR R1 per CB3 + CB4):
    # Write parent batch_summary row. Children (one per evaluated candidate)
    # already written by engine inside run_regime_holdout's _write_to_registry
    # call (Phase 0 sequencing per spec §3.1.2). This block writes ONLY the parent.
    if args.enable_b_c_narrow_recovery:
        if forward_window_metadata is None:
            # Should be unreachable post-CB2 identity guard (regime_key locked to
            # forward_2026 → forward_window_metadata always captured). Defensive
            # raise per HARD CONSTRAINT — never silently fall through.
            raise RuntimeError(
                "B-C-narrow finalize POST-fire: forward_window_metadata missing "
                "despite passing identity guard. Possible regression in "
                "forward_window_metadata capture at scripts:954-973."
            )
        # CB3 PFR R1 ADOPT: derive fee_model from cost_model.fee_model_label
        # (matches children's fee_model via engine.py:1278). NO hardcoded "phase4_15bps_v1".
        _exec_cfg = load_execution_config(args.execution_config)
        _cost_model = ConstantSlippage.from_config(_exec_cfg)
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
            # CB3 PFR R1 ADOPT: initial_capital = engine cash default (engine.py:2324 = 10_000.0).
            # Producer's _evaluate_one_candidate does NOT pass cash override; engine uses default
            # → children rows have initial_capital = 10_000.0. Parent MUST match for consistency.
            # (PUSHBACK candidate: could be None/NULL at parent since cohort summary != per-strategy
            # backtest; locked to 10_000.0 for strict match per Codex BLOCKING-3 fix.)
            "initial_capital": 10_000.0,
            # CB3 PFR R1 ADOPT: derive from cost_model.fee_model_label (slippage.py:94-100).
            # For execution_phase4_15bps.yaml → total_bps = 15 → "effective_15bps_per_side".
            # NO hardcoded literal.
            "fee_model": _cost_model.fee_model_label,
        }
        _finalize_batch_registry(
            parent_run_id=run_id,
            cohort_metadata=cohort_metadata,
            db_path=None,  # DEFAULT_DB_PATH; co-located with engine-written children
        )
        logger.info(
            "[B-C-narrow] _finalize_batch_registry: parent batch_summary row written at "
            "run_id=%s (engine_commit=%s, fee_model=%s, cohort_metadata fields=%d)",
            run_id, CORRECTED_WF_ENGINE_COMMIT, _cost_model.fee_model_label, len(cohort_metadata),
        )
```

---

**Re-validate placement of W6:**

```bash
grep -n "_exec_cfg_bytes\|aggregate\[\"forward_window_metadata\"\]\|_write_aggregate_summary" scripts/run_phase2c_evaluation_gate.py | head -10
```

Expected: `_exec_cfg_bytes` defined around line 1023; `aggregate["forward_window_metadata"]` around 1051; `_write_aggregate_summary` call around 1053. Place W6 block between lines 1051 and 1053.

- [ ] **Step 10.9: Run all 26 Phase 2 tests — must PASS (GREEN)**

```bash
python -m pytest tests/test_phase2c_evaluation_gate_runner.py::TestBCNarrowPhase2ProducerEdits -v
```

Expected: 26/26 PASS.

If any test FAILS, inspect — likely culprits:
- import error in producer (Step 10.1 missed an import)
- typo in CLI flag dest names (Step 10.2; argparse converts `--enable-b-c-narrow-recovery` → `enable_b_c_narrow_recovery` and `--force-rerun-existing` → `force_rerun_existing`)
- `_finalize_batch_registry` raising on missing `cohort_metadata` key — check the required_keys set vs test fixture
- `_evaluate_one_candidate` merge block not running (verify `lcb_active` gate)

- [ ] **Step 10.10: Full test suite zero-regression**

```bash
python -m pytest -q
```

Expected: zero regression vs pre-Phase-2 baseline (HEAD `b10ffb2`: 2328 pass / 0 failed / 2 xfailed per Phase 0 SEAL note) + 26 net new passing Phase 2 tests. Total expected: 2354 pass / 0 failed / 2 xfailed (binding contract is zero regression + 25 new passing; the 2353 integer is informational).

The T1.4 `test_4_tuple_matches_locked_values` test (at `tests/test_t1_4_backward_compat.py:490`) may FAIL at this step because the AST classifier now sees additional test/scripts-side `_write_to_registry` callers (if any added). Task 11 handles T1.4 baseline maintenance — if T1.4 fails at Step 10.10, proceed to Step 10.11 (commit Task 10) WITHOUT fixing T1.4 here. Task 11 commit closes the T1.4 baseline gap atomically.

- [ ] **Step 10.11: Commit producer edits**

```bash
git add scripts/run_phase2c_evaluation_gate.py
git commit -m "feat(b-c-narrow/phase-2): implement producer edits with --enable-b-c-narrow-recovery flag (T10)

Per Plan v3-Phase2 Task 10 + spec §3.2 + 4 Codex BLOCKING-carry fixes from Phase 0 plan v2:

- BLOCKING-1 R9 architectural call-order split: PRE-flight (archive + finalize_preflight) BEFORE candidate loop; POST-fire (finalize) AFTER children written by engine
- BLOCKING-3 create_table precondition: _finalize_batch_registry (POST-fire ONLY) calls create_table(conn) before insert; preflight is TRULY read-only per CR2-B2 v3 (3-path early-exit via sqlite_master; NO create_table call in preflight to preserve CB1 dry-run invariant)
- BLOCKING-4 _build_argparser reference correction: all tests reference _build_argparser (NOT _parse_args)
- NEW CLI flags: --enable-b-c-narrow-recovery (default False; gates 3 NEW behaviors) + --force-rerun-existing (default False; R9-B-guarded DELETE opt-in)
- NEW _archive_canonical_pre_flight(): shutil.move with refuse-if-exists guard
- NEW _finalize_batch_registry_preflight_or_raise(): refuse-if-exists OR DELETE WHERE parent_run_id
- NEW _finalize_batch_registry(): writes ONLY 1 parent batch_summary row via insert_run; 39 child rows written by engine
- _evaluate_one_candidate: +2 LC-b kwargs (artifact_dir_root, parent_run_id_override); threads 4 LC-b scalars (run_id_override, source_batch_id, parent_run_id_override, artifact_dir) to engine; computes γ3/γ4/T_obs from equity_curve; merges B-C-narrow fields into inline per-candidate JSON write
- _CSV_FIELDS: +5 fields (gamma3, gamma4, T_obs, returns_per_bar_path, returns_per_bar_sha256)
- _write_aggregate_csv: emits 5 new fields with backward-compat None→empty-string pattern
- main(): wires archive PRE-flight + finalize PRE-flight guard + LC-b kwargs threading + finalize POST-fire (all gated by --enable-b-c-narrow-recovery for backward-compat)

Tests: 26/26 Phase 2 tests GREEN. T1.4 baseline maintenance pending Task 11. Full suite zero regression except for expected T1.4 4-tuple drift (Task 11 closes)."
```

---

### Partial-state recovery runbook (MR6-2 PFR R6 ADOPT v7)

**Context**: Task 10 W3 archive PRE-flight is destructive (canonical → archive via `shutil.move`). If W5 candidate loop crashes mid-loop OR W6 finalize POST-fire raises after some child rows written, operator lands in half-mutated state. This subsection documents the manual recovery steps; the design is acknowledged as destructive-without-atomic-rollback (single-operator scope; over-engineered try/except-with-rollback wrapper rejected as out-of-scope per anti-pre-emption).

**Failure-mode matrix** (post-W3-success):

| Failure point | State after failure | Recovery steps |
|---|---|---|
| W5 candidate loop crashes mid-loop (e.g., engine OOM, unexpected DSL error, parquet I/O error) | canonical archived; partial child rows in registry (0..38); NO parent row; `run_dir` partially populated (per-candidate dirs + partial CSV) | (1) `ls data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` to verify archive intact + `sqlite3 backtest/experiments.db "SELECT COUNT(*) FROM runs WHERE parent_run_id='phase4_forward_2026_15bps_v1_b_c_narrow';"` to confirm partial child count;<br>(2) `mv data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/ data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` to restore canonical;<br>(3) re-run producer with BOTH `--force-rerun-existing` AND `--force` flags (CR7-M2 PFR R7 ADOPT v8 fix): `--force-rerun-existing` cleans registry rows (R9-B-guarded DELETE WHERE parent_run_id); `--force` allows overwrite of non-empty `run_dir` (`_check_overwrite_protection` at scripts:844-861 invoked at scripts:929-931 would otherwise abort retry on the non-empty run_dir). The two flags have DISTINCT scopes — both required for partial-state recovery. |
| W6 finalize POST-fire raises (e.g., SQLite I/O error, schema constraint violation) | canonical archived; all 39 child rows in registry; NO parent row; `run_dir` fully populated (per-candidate dirs + CSV + JSON) | Same recovery steps (1)-(3) above with BOTH `--force-rerun-existing` AND `--force`. The partial state is detected by W1 preflight on re-fire (parent_run_id has child rows but no parent → idempotency check would raise without `--force-rerun-existing`); `--force-rerun-existing` DELETEs children + (absent) parent; `--force` allows the fully-populated run_dir to be overwritten cleanly. |
| W3 archive succeeds + W4 forward_window_metadata capture fails (parquet I/O error before any candidate written) | canonical archived; NO registry rows yet; no parquet artifacts in canonical dir | Same recovery: manual `mv` archive back + `--force-rerun-existing` is harmless (no rows to delete; preflight Path 1 returns clean) + re-fire. |

**Operator discipline**:
- DO NOT attempt to manually edit `backtest/experiments.db` to clean partial child rows — use `--force-rerun-existing` which is the audited cleanup path.
- DO NOT delete the `archive/phase4_forward_2026_15bps_v1_d0b8101/` directory without first restoring canonical — that is the only intact copy of the original artifact lineage.
- After recovery, verify `current_git_sha` in the resulting parent row matches the recovery-time HEAD, not the prior failed-attempt HEAD.

**Design trade-off acknowledgment**: a try/except wrapper around W3-through-W6 with full rollback would require: (a) snapshotting the registry transactionally, (b) tracking partial parquet writes per-candidate, (c) restoring canonical-from-archive on failure. This is engineering for a low-probability failure surface in a single-operator project. The manual runbook above is the accepted trade-off. Future cycle (Phase 3 or Phase 4) MAY revisit this if multi-operator concurrency or higher reliability is required — out of Phase 2 scope per anti-pre-emption.

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
- `test_count`: 49 (Phase 2 added zero direct `_write_to_registry` calls in tests — all 25 new tests use mocking via `unittest.mock.patch` OR call `_evaluate_one_candidate` which internally calls `run_regime_holdout` which internally calls `_write_to_registry`; the AST classifier counts only DIRECT call sites in `tests/`, so test_count stays 49 UNLESS a new test directly invokes `_write_to_registry`)
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

Expected: 2354 pass / 0 failed / 2 xfailed (26 net new passing vs pre-Phase-2 baseline). Zero regression.

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

- [ ] **Step 12.1: Confirm 26 tests GREEN + full suite zero regression + T1.4 baseline updated (or unchanged)**

```bash
python -m pytest tests/test_phase2c_evaluation_gate_runner.py::TestBCNarrowPhase2ProducerEdits -v
python -m pytest tests/test_t1_4_backward_compat.py::TestT1_4_B1_SignatureBackwardCompat -v
python -m pytest -q
```

Expected:
- 26/26 Phase 2 tests PASS
- T1.4 B1 class PASSES (4-tuple verified)
- Full suite: 2354 pass / 0 failed / 2 xfailed (zero regression vs `b10ffb2` baseline + 26 net new passing)

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
| TestBCNarrowPhase2ProducerEdits | 25 | 25 | 0 | GREEN |
| TestT1_4_B1_SignatureBackwardCompat | (existing) | (all) | 0 | GREEN |
| Full suite (b10ffb2 baseline + 25 new) | 2353 | 2353 | 0 (+ 2 xfailed) | zero regression |

## 4 BLOCKING-carry fixes verified

| # | BLOCKING-carry | Status |
|---|---|---|
| BLOCKING-1 | R9 architectural call-order split (PRE-flight + POST-fire halves) | FIXED — verified by `test_finalize_batch_registry_writes_parent_row_only` + `test_archive_step_*` + `test_finalize_batch_registry_*_idempotency` tests |
| BLOCKING-3 | `_finalize_batch_registry` create_table precondition | FIXED — `_finalize_batch_registry` (POST-fire) calls `create_table(conn)` before insert; `_finalize_batch_registry_preflight_or_raise` (preflight) does NOT call create_table per CR2-B2 v3 (3-path early-exit via sqlite_master; preserves CB1 dry-run read-only invariant) |
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

Phase 2 deliverables: 25/25 TestBCNarrowPhase2ProducerEdits PASS; full suite
zero regression vs b10ffb2 baseline + 26 net new passing. T1.4 baseline
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
- 25 Phase 2 producer-edit tests GREEN
- T1.4 B1 4-tuple unchanged (or updated per AST classifier; whichever applies)
- Full test suite zero regression vs pre-Phase-2 baseline + 26 net new passing
- Producer modifications confined to `scripts/run_phase2c_evaluation_gate.py` (9 modify-zones + 4 NEW helpers: `_validate_b_c_narrow_recovery_identity_or_raise` + `_archive_canonical_pre_flight` + `_finalize_batch_registry_preflight_or_raise` + `_finalize_batch_registry`) + 1 test file extension
- All 4 BLOCKING-carry items from Phase 0 plan v2 PFR R2 verified fixed (BLOCKING-1 + BLOCKING-3 + BLOCKING-4 + BLOCKING-6)

**Do NOT surface Phase 3 fire-plan drafting authorization as a sub-option of #N+2.** Per anti-pre-emption discipline, Phase 3 drafting requires its own register-event #N+3 — fire that as a SEPARATE Charlie message after #N+2 is resolved.

Phase 2 sealed at task level (no Phase Marker advance per [feedback_claude_md_freshness.md] mid-cycle discipline — arc-level closeout reserved for Phase 4 cycle SEAL).

---

## DEFER items (Phase 2 scope only)

**Phase-2-internal:** NONE. All 4 BLOCKING-carry items from Phase 0 plan v2 PFR R2 (BLOCKING-1 + BLOCKING-3 + BLOCKING-4 + BLOCKING-6) addressed inline in Tasks 10-11.

**Phase 3+ blockers DEFERRED** to respective sub-plans per spec §5 enumeration:

- **Phase 3** (T13 producer fire + T14 V4 reproducibility gate + T14b canonical-path relocation): 39-candidate cohort_a re-run with `parquet_data_sha256` populated + per-bar artifacts + γ3/γ4 moments + V4 reproducibility gate (ε=1e-6). Drafting requires Charlie register-event #N+3 after Phase 2 ratify.

  **CR-SE-H2 SEAL-eve v9 ADOPT clarification**: Plan v8 W3 producer-gated archive (under `--enable-b-c-narrow-recovery`) SUPERSEDES sealed spec §5 T12 manual `mv` archive command. The spec T12 manual `mv` was written in spec v1-v3 before the producer W3 design was added in plan v1. Phase 3 fire-plan command MUST include `--enable-b-c-narrow-recovery` flag (the spec T13 example at spec line 289 was written before the new CLI flag was added; updated at Phase 3 plan drafting). Spec text retained per Architecture-B sealed-content invariance discipline (sealed-content NOT modified in place); this Phase 3 inheritance handoff documented here at Phase 2 SEAL plan + NAMED-eligible-for-spec-amend at Phase 3 register OR Phase 4 SEAL bundle as errata supplement per Architecture-B precedent. The producer W3 + `--enable-b-c-narrow-recovery` design has 7 PFR rounds + SEAL-eve adversarial dispatch verification; the spec T12/T13 manual-mv description was written pre-design.
- **Phase 4** (T15 NOTE doc + T16 SEAL bundle + Phase Marker advance per Option 1A atomic): B-C-narrow data-recovery cycle SEAL artifact + arc-level closeout. Drafting requires Charlie register-event #N+4 after Phase 3 SEAL.
- **BLOCKING-5 G4-G7 test bodies** (per Codex R2 Phase 0 plan v2 finding): G4 per-bar parquet integrity + G5 γ3/γ4 round-trip + G6 registry parent-child integrity + G7 archive idempotency. All 4 gates are POST-impl gates that fire at Phase 3 (per spec §4.3). Bodies inlined in Plan v3-Phase3 (not Phase 2 scope).

Each sub-plan requires separate Charlie register-event for drafting authorization per anti-pre-emption discipline.

---

## Execution Handoff

Plan v3-Phase2 v1 saved to `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-2-producer-tdd-plan.md`.

After Plan v3-Phase2 B2 2-leg PFR returns APPROVE (or APPROVE-WITH-FINDINGS at LOW-only floor) → use **superpowers:subagent-driven-development** per Charlie register PV3-SPLIT-BY-PHASE: dispatch fresh subagent per task (T9 → T10 → T11 → T12) with two-stage review OR orchestrator-manual execution per Charlie register-event-by-register-event.

After Phase 2 SEALED (Task 12 ratify) → request Charlie register-event for Plan v3-Phase3 sub-plan drafting authorization (separate fire — anti-pre-emption discipline preserved).
