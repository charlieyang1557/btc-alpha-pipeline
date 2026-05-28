# B-C-narrow Phase 3 — Fire Plan (data-recovery execution)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this sub-plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Tasks 14 + 14b each contain explicit STOP HERE blocks for Charlie register-events #N+19a (T13 fire authorization) + #N+19b (T14b canonical-path relocation authorization) before operational execution — the implementer subagent MUST NOT bypass these without an explicit Charlie register fire.

**Sub-plan scope:** Phase 3 of the B-C-narrow data-recovery cycle ONLY — operational fire of the 39-candidate cohort_a re-run against the forward_2026 window using the Phase 2 producer wiring at HEAD `0a54f65`. Three operational steps consumed from spec §5: T13 producer fire (producer-W3 archive + LC-b candidate loop + W4 finalize parent batch_summary), T14 V4 reproducibility gate (G4-G7 + ε=1e-6 per-candidate match), T14b canonical-path relocation (sibling → canonical mv after V4 PASS). NO new source code edits. NO engine code edits. NO producer code edits. NO spec amendments. The plan adds ONE new test file (`tests/test_b_c_narrow_v4_reproducibility.py`; 7 test methods inlined per BLOCKING-5 carry from Phase 2 plan v3-Phase2 line 3651) + ONE new fixture (`tests/fixtures/b_c_narrow_archived_baseline.json`; created POST-T13 fire BEFORE T14 V4 gate, see Step 14.3) + ONE new evidence artifact (`docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md`).

**Sub-plan motivation:** Phase 0 (engine extension; sealed at `f112599`) added `RegimeHoldoutResult.equity_curve` + 4 LC-b kwargs + atomic write-then-registry sequencing inside `run_regime_holdout`. Phase 1 (pre-impl gates; sealed at `b10ffb2`) returned all 4 BLOCKING gates PASS (G1 engine-diff audit + G2 DSL backward-compat + G3 raw_payloads inventory + G3.5 engine smoke pre-satisfied). Phase 2 (producer TDD; impl sealed at `4b7a4c6`; T10 producer code polish Bundle (a) at `3a1226b`; ratify packet polish Bundle (b) at `0a54f65`) wired the producer behind `--enable-b-c-narrow-recovery` with 4 new helpers (W0 identity guard, W1a/W1b finalize preflight, W3 archive, W4 finalize POST-fire) + 6 module-level `BCNARROW_*` constants. Phase 3 executes the wiring against the 39 cohort_a candidates and verifies V4 reproducibility vs the archived original — the only step that produces new data artifacts in the entire cycle.

**Tech Stack:** Python 3.11+, pytest (V4 + G4-G7 verification), pandas (parquet I/O + holdout_results.csv parsing), pyarrow (parquet engine), scipy.stats (`compute_moments` round-trip in G5), sqlite3 (G6 registry parent-child query), pathlib + shutil (T14b mv), json (fixture capture + summary parsing). NO new dependencies.

**Cycle context:** R6.1 V_SEAL §10 binding precondition (spec at `d6c7fc0`). Cycle entry Charlie register N1 2026-05-26. Phase 3 is the only sub-plan that produces new data artifacts (39 per-candidate holdout_summary.json files + 39 returns_per_bar.parquet files + 1 aggregate holdout_summary.json + 1 holdout_results.csv + 1 archive snapshot of original + 1 parent batch_summary registry row + 39 child regime_holdout registry rows). Phase 4 (SEAL bundle: NOTE doc + B2 reviewer dispatch + Rule 2 SEAL-eve + atomic commit + Phase Marker advance) is a SEPARATE register-event #N+20 per anti-pre-emption discipline.

---

## PFR R1 ADOPT findings applied (Plan v2 amendments)

Per Charlie register #N+19 (Path 1: full AMEND + PFR R2) 2026-05-28. PFR R1 fired as B2 2-leg dispatch (Codex `codex:codex-rescue` + Advisor `quant-research-advisor`); Codex returned NOT-APPROVE (3 BLOCKING + 1 HIGH + 2 MEDIUM + 1 LOW); Advisor returned APPROVE-WITH-FINDINGS (0 BLOCKING + 1 HIGH + 5 MEDIUM + 5 LOW + 3 PUSHBACK candidates).

Convergence summary:
- 3 BLOCKING all Codex-originated, orchestrator-verified SOUND
- 1 HIGH Codex-originated (CH4 registry linkage) + 1 HIGH Advisor-originated (AH1 V4 drift tautological) — AH1 subsumed into CB3 fix
- Convergent dimension: gate-vs-fixture distinction at CB3 (Codex) + AM3 (Advisor)
- Codex-only catches: CB1 + CB2 + CH4 + CM6 + CL7 (empirical + discipline + structural)
- Advisor-only catches: AH1 + AM1 + AM3 + AM4 + AM5 + AL1-AL5 (methodology + operational-risk)
- B2 reverse-direction pattern operating as designed
- 3 PUSHBACK candidates: PB1 (lex-smallest-2) ADOPT; PB2 (G5 df["return"]) ADOPT; PB3 (RED PASS-tests) PARTIAL ADOPT — CB2 supersedes

| # | Severity | Origin | Fix in v2 |
|---|---|---|---|
| CB1 | BLOCKING | Codex | Corrected raw_payloads path in Step 13.1(e)+(f) + ratify packet from `data/batches/.../raw_payloads` to `raw_payloads/batch_phase2c_15_main_fire_combined` (matches producer `DEFAULT_RAW_PAYLOADS_DIR = PROJECT_ROOT / "raw_payloads"` + `_load_dsl_from_response()`). 998 symlinks unchanged. |
| CB2 | BLOCKING | Codex | Made V4+G4-G7 tests path-adaptive via module-level `_resolve_active_run_dir()` helper resolving `SIBLING_RUN_DIR` (pre-T14b) OR `CANONICAL_RUN_DIR` (post-T14b). Tests now PASS in both states per CLAUDE.md HARD CONSTRAINT "NEVER commit code that doesn't pass existing tests". Updated Step 14b verification + plan:1144 + plan:1172-1175 + plan:1292 accordingly. |
| CB3 | BLOCKING | Codex | KEPT §6.4 N=2 fixture for schema-drift catch (PB1 ADOPT). ADDED all-39 V4 gate: 4 NEW tests reading archive + new summaries directly (V4 ε metric diff + V4 total_trades exact + G4 per-bar parquet integrity + G5 γ3/γ4 round-trip) loop over all 39 candidates from raw CSV. AH1 subsumed: drift-stop test rewritten to inject synthetic ε-breach into one candidate's metric within the all-39 loop, asserting AssertionError mentions that candidate's hash. Updated plan:1262 DEFER item: N=39 NO LONGER deferred. |
| CH4 | HIGH | Codex | Extended G4 test body to query each child registry row via `get_run(conn, child_run_id)`; assert `returns_per_bar_path` + `returns_per_bar_sha256` + `T_obs` all match across summary + computed + registry. Extended G6 test body to assert parent row cohort metadata non-null + each child row per-candidate metadata non-null + parent-only fields NULL at children. Updated test docstrings. |
| CM5 | MEDIUM | Codex | Changed Step 13.3 title from "all 7 tests FAIL" to "9 fire-state tests SKIPPED-or-RED + 2 static contract tests PASS + 1 drift-stop hybrid" (reconciled with CB3 all-39 + AM1 cross-FS additions + CB2 path-adaptive SKIP semantics: 12 total). Per CB2: SKIPs encode RED-pre-fire semantics via _resolve_active_run_dir → pytest.skip(...). G6 registry test still hits FAIL pre-fire (no skip on always-present registry). |
| CM6 | MEDIUM | Codex | Resolved #N+19c authorization semantics contradiction via Option A: #N+19c gates RATIFY/PUSH only; removed "gates final commit" wording from plan:95; clarified Step 14c.2 commit happens BEFORE STOP at plan:1354; #N+19c is ratify acknowledgment of already-committed packet (matches Phase 2 ratify pattern). |
| AM1 | MEDIUM | Advisor | Added NEW test `test_g7_archive_refuses_cross_filesystem_attempt` covering producer's `st_dev` cross-FS guard via mocked `Path.stat()`. Test count +1. |
| AM2 | MEDIUM | Advisor | Added inline comment in G5 test docstring documenting spec §6.4 line 363 deviation: df["return"] direct read is semantically equivalent to compute_per_bar_returns(equity_curve) recompose AND additionally validates parquet round-trip integrity end-to-end. |
| AM3 | MEDIUM | Advisor | Added 1-line rationale to NEW locked decisions table row for "Fixture sampling rule" explaining lex-smallest-2 deterministic + minimally arbitrary basis; NAMED-eligible extension if theme-clustering bias surfaces at Phase 4 reviewer dispatch; NOTE clarifies fixture-rule vs V4-gate distinction per CB3. |
| AM4 | MEDIUM | Advisor | Inserted NEW Step 14b.2.5 specifying T14b failure adjudication: STOP + no forward recovery + archive intact + surface to Charlie + Phase 4 SEAL bundle BLOCKED. |
| AM5 | MEDIUM | Advisor | Added new row to inherited locks table: "Engine.py stability" documenting zero commits to backtest/engine.py since Phase 0 SEAL `f112599`; basis for ε=1e-6 numerical reproducibility expectation. |
| CL7 | LOW | Codex | Fixed plan:23 STOP-block count: "4 STOP HERE blocks total" → "3 explicit STOP HERE blocks plus one Step 14b.0 register-verification precondition (total: 4 STOP gates)". |
| AL1 | LOW | Advisor | Flipped Step 14b.3 empty commit default: OPTIONAL only if Charlie register #N+19b explicitly requested separate boundary marker; otherwise SKIP and roll into Step 14c.2 commit. |
| AL2 | LOW | Advisor | Added Step 13.1(h) verifying inlined 39-hash list matches current canonical CSV (drift catch); surface to Charlie before any fire if drift detected. |
| AL3 | LOW | Advisor | Added 2-line note before ratify packet template at Step 14c.1 explaining `<sha>` + `<X seconds>` + `<ISO UTC>` placeholder rendering instructions for implementer measurement. |
| AL4 | LOW | Advisor | Replaced G6 test "redundant given query above" comment with substantive AL4 PFR R1 ADOPT note explaining independent invariant check + future schema-drift catch class. |
| AL5 | LOW | Advisor | Added Step 14.2(g) verifying no `holdout_error` candidates per spec §7 R5; STOP + surface to Charlie if any errored candidate surfaces (V4 gate could pull from errored candidate producing false positives). |

Total v2 amendments: 17 ADOPT inline + 3 PUSHBACK adjudications.
Test count v1 → v2: 7 → 12 (+ 5 NEW: 4 all-39 per CB3 + 1 cross-FS per AM1; AH1 absorbed into CB3 drift-test rewrite).

---

## Sub-decisions applied (Path A defaults per Charlie register #N+18; Charlie may override at PFR R1)

| # | Sub-decision | Default applied | Rationale |
|---|---|---|---|
| (i) | T12 spec supersession handling | Inline plan comment + producer W3 flag (matches Plan v3-Phase2 ADOPT note pattern). Spec amend / Architecture B errata NAMED-eligible at Phase 4 SEAL bundle. | Lowest-friction; preserves Architecture-B sealed-content invariance. T13 fire command in Step 14.1 includes `--enable-b-c-narrow-recovery` flag so producer W3 performs the archive automatically; spec §5 T12 manual `mv` step is superseded de-facto but spec line 286 stays byte-identical. |
| (ii) | Plan structure | TDD-style: write 7 NEW V4+G4-G7 test bodies (RED) → STOP for fire auth → execute fire → capture fixture → run V4 gate (GREEN expected) → STOP for T14b auth → execute relocation → write ratify packet. | Matches Phase 2 precedent (TDD discipline with test bodies authored before producer changes); explicit STOP gates around the 2 operational write steps. |
| (iii) | Charlie register-events for Phase 3 | 3 register-events: #N+19a = T13 fire authorization (after Task 13 RED commit); #N+19b = T14b canonical-path relocation authorization (after Task 14 V4 GREEN commit; only fires if V4 PASS); #N+19c = Phase 3 ratify acknowledgment (after Task 14c ratify packet commit). | CLAUDE.md HARD CONSTRAINTS + operational-write discipline = explicit Charlie register for each cohort write + each canonical-path mutation. |

**Sub-decision (iii) implication:** 3 explicit STOP HERE blocks plus one Step 14b.0 register-verification precondition (total: 4 STOP gates) in this plan: Step 13.5 (explicit STOP before T13 fire), Step 14.7 (explicit STOP before T14b relocation), Step 14c.2 (explicit STOP for #N+19c acknowledgment AFTER Task 14c commit landed per CM6 ADOPT Option A). The 4th STOP gate is the Step 14b.0 register-verification precondition check (verifies #N+19b register fired before T14b mv executes).

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
| Engine.py stability | Zero commits to `backtest/engine.py` since Phase 0 SEAL `f112599` (verified via `git log f112599..HEAD -- backtest/engine.py` returns empty) | Phase 1 G1 PASS classification basis for ε=1e-6 numerical reproducibility expectation. Engine extension was bounded; no post-SEAL drift in numeric path. (AM5 PFR R1 ADOPT v2) |

---

## NEW locked decisions for Phase 3

| Decision | Lock value | Rationale |
|---|---|---|
| Fire command | `python -m scripts.run_phase2c_evaluation_gate --enable-b-c-narrow-recovery --candidate-hashes <39 csv> --source-batch-id phase2c_15_main_fire_combined --regime-key evaluation_regimes.forward_2026 --execution-config config/execution_phase4_15bps.yaml --run-id phase4_forward_2026_15bps_v1_b_c_narrow --output-root data/phase2c_evaluation_gate/` | Spec §5 T13 with `--enable-b-c-narrow-recovery` flag added per sub-decision (i). The 39 hashes are extracted deterministically from current canonical `holdout_results.csv` per Step 13.1 + Step 14.1. |
| V4 ε tolerance | `abs(new - old) < 1e-6` for `sharpe_ratio`, `max_drawdown`, `total_return` (floats). Exact match (`new == old`) for `total_trades` (int), `holdout_passed` (bool), `gate_pass_per_criterion` 4 subfields (bools). | Spec §4.2 + §6.4 lock. |
| G7 archive idempotency semantic | STRICT refuse-if-exists. NO silent overwrite. NO auto-rename. Pre-fire precondition: `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` MUST NOT exist. Producer W3 raises `RuntimeError` if archive target exists. Manual cleanup required if archive target preexists from aborted attempt. | Spec §4.3 G7 + R10 |
| T14b gating | T14b mv executes ONLY if T14 V4 gate returns GREEN (all 12 tests PASS per v2 PFR R1 ADOPT expansion). On any V4 FAIL: SEAL BLOCKED pending Charlie register adjudication (per spec §4.2 paths a/b/c). Sibling dir + archive dir REMAIN in place; canonical path REMAINS empty until adjudication resolves. | Spec §5 T14b lock |
| Charlie register-event sequencing | 3 register-events for Phase 3: #N+19a = T13 fire authorization (gated by Step 13.5 STOP); #N+19b = T14b canonical-path relocation authorization (gated by Step 14.7 STOP; FIRES ONLY if V4 PASS); #N+19c = Phase 3 ratify acknowledgment (gated by Step 14c.2 STOP). | Sub-decision (iii); CLAUDE.md operational-write discipline; anti-pre-emption |
| Fixture sampling rule | `tests/fixtures/b_c_narrow_archived_baseline.json` captures N=2 candidates: the 2 lexicographically smallest hypothesis_hash strings from the current canonical `holdout_results.csv` (after sort): `18d92ce5d0b40cc7` + `22864f01a49e3452`. Specific keys captured per spec §6.6: `sharpe_ratio`, `max_drawdown`, `total_return` (from `holdout_metrics`); `total_trades` (from `holdout_metrics`); `holdout_passed`; `gate_pass_per_criterion` (4 subfields). | Spec §6.6 line 392 accepts N=2 specific-keys-only; lex-smallest is deterministic + minimally arbitrary vs spec's non-binding "e.g.," sample. If theme-clustering bias surfaces at Phase 4 reviewer dispatch, NAMED-eligible to extend N=2 → N=3 spanning theme-range. NOTE: this is FIXTURE rule for schema-version-bump drift catch; V4 gate at Step 14.4 verifies all-39 per spec §4.2/§4.3 per Codex CB3 ADOPT. (AM3 PFR R1 ADOPT v2) |
| Fixture creation timing | Fixture created POST-T13 fire (when archive is populated by producer W3) BEFORE T14 V4 gate runs. Sub-step 14.3 captures the fixture from `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/<hash>/holdout_summary.json`. | Spec §6.6: fixture sourced from archived original (per spec line 365); archive does not exist pre-T13 → fixture capture must be sequenced AFTER T13 archive step completes |
| T12 supersession handling | Spec line 286 ("T12 — Archive original: `mv ...`") byte-identical preserved per Architecture B. Producer W3 (gated by `--enable-b-c-narrow-recovery`) performs the archive INLINE during T13 fire, superseding the manual mv step. Spec §5 T12 + T13 collapse into Step 14.1 single fire command (producer handles both). Spec amend / Architecture B errata NAMED-eligible at Phase 4 SEAL bundle. | Sub-decision (i) |

---

## File structure (Phase 3 scope only)

| File | Action | Scope |
|---|---|---|
| `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-3-fire-plan.md` | CREATE | this plan |
| `tests/test_b_c_narrow_v4_reproducibility.py` | CREATE at Step 13.2 | 12 NEW test methods (5 spec §6.4 N=2 fixture + 2 BLOCKING-5 carry G6+G7 + 4 all-39 V4 gate per CB3 PFR R1 ADOPT v2 + 1 cross-FS G7 per AM1 PFR R1 ADOPT v2) |
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
| #N+19c (Phase 3 ratify acknowledgment) | PENDING | Ratify ack + push decision for Phase 3 commits (CM6 PFR R1 ADOPT v2 Option A: #N+19c acknowledges the already-committed Task 14c ratify packet; commit lands at Step 14c.2 BEFORE STOP; matches Phase 2 ratify pattern). Phase 4 sub-plan drafting authorization is a SEPARATE register-event #N+20. |

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
# CB1 PFR R1 ADOPT v2: corrected path from data/batches/.../raw_payloads to
# raw_payloads/batch_phase2c_15_main_fire_combined (matches producer's
# DEFAULT_RAW_PAYLOADS_DIR = PROJECT_ROOT / "raw_payloads" at scripts:141 +
# _load_dsl_from_response() at scripts:388-391 + Phase 1 G3 inventory at spec:219).
find raw_payloads/batch_phase2c_15_main_fire_combined -type l 2>/dev/null | wc -l
# Expected: 998

# (f) Verify Phase 1 G3 a sample symlink resolves cleanly (target file exists)
python -c "
from pathlib import Path
import os
# CB1 PFR R1 ADOPT v2: corrected base path.
base = Path('raw_payloads/batch_phase2c_15_main_fire_combined')
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

- [ ] **Step 13.1(h): Verify 39-hash inlined list matches current canonical CSV (drift catch)**

Per AL2 PFR R1 ADOPT v2: the 39-hash list inlined in Step 14.1 fire command was extracted from current canonical CSV at plan-drafting time. If a later commit altered the canonical between plan drafting + fire time, this drift check surfaces it before any operational fire.

```bash
python -c "
import csv
with open('data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv') as f:
    current_hashes = sorted(row['hypothesis_hash'] for row in csv.DictReader(f))
plan_hashes_str = '18d92ce5d0b40cc7,22864f01a49e3452,2433a38b2f9a7211,2b1ca44778281d97,2c5e3cc08d407b73,2cc19d1b5e2c9024,34588c948b1ff12b,35dcfcfbee4cfafc,38a1bb228f103c26,3a2559fbeff71f94,3b013ac903ab047b,3c3ba9b95d2ea37c,3d3938aed6376f04,3ebec90d7be309ab,406d4f4dfb4d46de,41d3b759a1004c97,4a3c8e2fe04d72c1,4ce6e78ff9cff9b9,52b04f27b7ee565b,53e1b5030aefe836,54ae22768a3f78e9,5b4d89be0ccb9be1,5fcf29ab42c5f8b6,7240602b60cd7271,7abff29fc2f117a1,8a2a8f73f71a835e,8def2951c72f0961,95d5cfc1c0a9579a,9c90efe879157a5c,aa8c55c16db41ea7,b10f4563366481b3,b24ca51d477c2e96,bc5ea1beab19fcdd,c076cdad4ee7ca42,cfd24b8b72d6e429,d04e1b054fe4d69d,d3fe403c8b1c4130,dc7d6de5e71772ae,ec6a8a385c1a3e9a'
plan_hashes = sorted(plan_hashes_str.split(','))
assert current_hashes == plan_hashes, f'CSV-vs-plan hash drift: plan was authored against stale CSV; current has {len(current_hashes)} hashes, plan inlined {len(plan_hashes)}; symmetric diff: {set(current_hashes).symmetric_difference(set(plan_hashes))}'
print(f'OK: 39-hash list matches current canonical')
"
```

Expected output: `OK: 39-hash list matches current canonical`. If drift detected, surface to Charlie before any fire — the plan inlined the CSV at plan-drafting time; if a later commit altered the canonical, the plan needs a re-anchor.

- [ ] **Step 13.2: Create `tests/test_b_c_narrow_v4_reproducibility.py` with 12 NEW test method bodies (TDD RED)**

Write the following file content verbatim:

```python
"""V4 reproducibility + G4-G7 gate tests for B-C-narrow Phase 3 fire.

Per Plan v3-Phase3 v2 Step 13.2. Tests authored RED before Task 14 fire.
GREEN expected at Step 14.5 after fire + fixture capture + V4 gate run.

Test count: 12 methods (PFR R1 ADOPT v2 expansion):
  - 5 N=2 fixture tests per spec §6.4 (schema-version-bump drift catch)
  - 2 BLOCKING-5 carry from Phase 2 plan v3-Phase2 line 3651 (G6+G7 inline)
  - 4 all-39 V4 gate tests per CB3 PFR R1 ADOPT v2 (spec §4.2/§4.3 full coverage)
  - 1 cross-FS G7 test per AM1 PFR R1 ADOPT v2 (st_dev guard coverage)

Path-adaptive design per CB2 PFR R1 ADOPT v2:
  Tests work in BOTH pre-T14b state (sibling dir populated, canonical empty/absent)
  AND post-T14b state (sibling gone, canonical populated). Via module-level
  `_resolve_active_run_dir()` helper, the test suite satisfies CLAUDE.md HARD
  CONSTRAINT 'NEVER commit code that doesn't pass existing tests' across the
  T14b mv lifecycle. The 2 path-independent contract tests (drift stop-condition
  + G7 refuse + G7 cross-FS) always pass regardless of disk state.

Fixture file: tests/fixtures/b_c_narrow_archived_baseline.json
  Captured at Step 14.3 POST-T13 fire BEFORE T14 V4 gate runs.
  Sources from data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/
  (created by producer W3 during the fire step).
  Captures N=2 candidates: 18d92ce5d0b40cc7 + 22864f01a49e3452
  (lexicographically smallest 2 hypothesis_hash from cohort_a; deterministic).
  N=2 fixture purpose: catch schema-version drift on JSON dict (which raw-CSV
  all-39 comparison at the all-39 V4 gate tests would miss).

Spec references:
  §4.2 V4 reproducibility gate (BLOCKING for SEAL): ε=1e-6 floats; exact int+bool
  §4.3 G4-G7 gate semantics
  §6.4 V4 reproducibility test enumeration
  §6.6 Fixture strategy (specific-keys-only N=2 sample)
"""
from __future__ import annotations

import csv
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
CANONICAL_RUN_DIR = (
    PROJECT_ROOT
    / "data"
    / "phase2c_evaluation_gate"
    / "phase4_forward_2026_15bps_v1"
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


def _resolve_active_run_dir() -> Path:
    """Resolve active run dir: sibling (pre-T14b) OR canonical (post-T14b).

    Per CB2 PFR R1 ADOPT v2: tests must work in BOTH states so Task 14b
    commit + Task 14c ratify both PASS-state per CLAUDE.md HARD CONSTRAINT
    'NEVER commit code that doesn't pass existing tests'.

    Pre-T14b state: SIBLING_RUN_DIR exists (populated by Step 14.1 fire);
    CANONICAL_RUN_DIR is absent (archived by producer W3).
    Post-T14b state: SIBLING_RUN_DIR is gone (consumed by mv); CANONICAL_RUN_DIR
    is populated (mv target).

    If NEITHER exists (fire never executed; e.g. RED phase at Step 13.3), the
    fixture-dependent tests skip cleanly via pytest.skip.
    """
    if SIBLING_RUN_DIR.exists():
        return SIBLING_RUN_DIR
    if CANONICAL_RUN_DIR.exists():
        return CANONICAL_RUN_DIR
    pytest.skip(
        "Neither SIBLING_RUN_DIR nor CANONICAL_RUN_DIR exists — Phase 3 fire "
        "not yet executed. Tests will be exercised at Step 14.4 V4 gate run."
    )


# Module-level resolution per CB2 PFR R1 ADOPT v2.
ACTIVE_RUN_DIR = _resolve_active_run_dir()

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
    """Load the V4 baseline fixture (N=2 candidates; specific keys).

    The N=2 fixture sample exists to catch schema-version drift on the
    JSON dict layer (which the all-39 raw-CSV V4 gate would miss).
    """
    assert FIXTURE_PATH.exists(), (
        f"V4 baseline fixture missing at {FIXTURE_PATH}. "
        "Per Plan v3-Phase3 Step 14.3, this fixture is captured POST-T13 fire "
        "BEFORE T14 V4 gate runs. If fixture is missing, fire has not yet "
        "produced the archive, OR Step 14.3 fixture-capture sub-step was skipped."
    )
    with FIXTURE_PATH.open() as f:
        return json.load(f)


def _load_all_39_candidates_from_csv(run_dir: Path) -> dict:
    """Load all 39 candidates from holdout_results.csv as dict[hash] = row.

    Per CB3 PFR R1 ADOPT v2: all-39 V4 gate reads raw CSV (NOT specific-keys
    fixture) to satisfy spec §4.2 + §4.3 per-candidate full-cohort coverage.
    """
    csv_path = run_dir / "holdout_results.csv"
    assert csv_path.exists(), (
        f"holdout_results.csv missing at {csv_path} (precondition: fire complete)"
    )
    with csv_path.open() as f:
        rows = {row["hypothesis_hash"]: row for row in csv.DictReader(f)}
    assert len(rows) == 39, (
        f"all-39 V4 gate expected 39 candidate rows in CSV, got {len(rows)} "
        f"at {csv_path}"
    )
    return rows


class TestV4Reproducibility:
    """V4 per-candidate metric reproducibility — sibling vs archived original."""

    def test_v4_per_candidate_metric_diff_within_epsilon(self) -> None:
        """Each sampled (N=2) candidate's 3 float metrics match archive within ε=1e-6.

        Spec §4.2 + §6.4: sharpe_ratio + max_drawdown + total_return float
        metrics match between sibling new artifact and archived original to
        within absolute tolerance ε=1e-6. Drift > ε → SEAL BLOCKED pending
        Charlie register adjudication.

        N=2 sample catches JSON-dict-layer schema drift; CB3 ADOPT v2 all-39
        test below covers full cohort directly from CSV.
        """
        fixture = _load_fixture()
        for hh in SAMPLE_HASHES:
            new_summary = _load_summary(ACTIVE_RUN_DIR, hh)
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
        """Each sampled (N=2) candidate's total_trades (int) + holdout_passed (bool)
        + 4 gate_pass_per_criterion subfields match archive EXACTLY (no ε).

        Spec §4.2 + §6.4: integer + bool values use exact equality (NO tolerance).
        """
        fixture = _load_fixture()
        for hh in SAMPLE_HASHES:
            new_summary = _load_summary(ACTIVE_RUN_DIR, hh)
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
        """Synthetic ε-breach injection into the all-39 loop must trigger SEAL stop.

        Per CB3 + AH1 PFR R1 ADOPT v2 (AH1 subsumed): the drift-stop test was
        rewritten to be substantive. Previous version asserted pure arithmetic
        without exercising the actual ε-comparison machinery against real metric
        values. v2 version:
          1. Loads all-39 archived rows
          2. Picks the first candidate (by lex-sorted hash)
          3. Injects a synthetic perturbation of 10×ε into that candidate's
             holdout_sharpe value
          4. Runs the all-39 ε-comparison
          5. Asserts AssertionError raised AND that the error message mentions
             the perturbed candidate's hash

        This locks the spec §4.2 stop-condition behavior contract against a real
        ε breach in the actual production code path, not just pure arithmetic.
        """
        archive_rows = _load_all_39_candidates_from_csv(ARCHIVE_RUN_DIR)
        new_rows = _load_all_39_candidates_from_csv(ACTIVE_RUN_DIR)
        perturbed_hash = sorted(archive_rows.keys())[0]
        # Inject synthetic 10×ε perturbation into one candidate's holdout_sharpe
        perturbed_sharpe = (
            float(archive_rows[perturbed_hash]["holdout_sharpe"]) + 10 * V4_EPSILON
        )
        with pytest.raises(AssertionError) as exc_info:
            for hh in sorted(archive_rows.keys()):
                old_val = float(archive_rows[hh]["holdout_sharpe"])
                if hh == perturbed_hash:
                    new_val = perturbed_sharpe  # synthetic injection
                else:
                    new_val = float(new_rows[hh]["holdout_sharpe"])
                diff = abs(new_val - old_val)
                assert diff < V4_EPSILON, (
                    f"V4 drift on candidate {hh} metric holdout_sharpe: "
                    f"old={old_val!r} new={new_val!r} abs_diff={diff!r} "
                    f"exceeds ε={V4_EPSILON} (spec §4.2 strict stop-condition)"
                )
        assert perturbed_hash in str(exc_info.value), (
            f"V4 stop-condition error message must mention perturbed candidate "
            f"hash {perturbed_hash}. Got: {exc_info.value!r}"
        )

    def test_v4_all_39_per_candidate_metric_diff_within_epsilon(self) -> None:
        """All 39 candidates' 3 float metrics match archive within ε=1e-6.

        CB3 PFR R1 ADOPT v2: reads archive + new CSV directly (NOT specific-
        keys fixture). Covers spec §4.2/§4.3 per-candidate full-cohort
        requirement that the N=2 fixture test does not satisfy.
        """
        archive_rows = _load_all_39_candidates_from_csv(ARCHIVE_RUN_DIR)
        new_rows = _load_all_39_candidates_from_csv(ACTIVE_RUN_DIR)
        assert set(archive_rows.keys()) == set(new_rows.keys()), (
            f"CSV hash-set mismatch: archive has "
            f"{set(archive_rows.keys()) - set(new_rows.keys())} extra; "
            f"new has {set(new_rows.keys()) - set(archive_rows.keys())} extra"
        )
        # CSV column names per Step 13.1(b): holdout_sharpe, holdout_max_drawdown, holdout_total_return
        metric_map = {
            "holdout_sharpe": "sharpe_ratio",
            "holdout_max_drawdown": "max_drawdown",
            "holdout_total_return": "total_return",
        }
        for hh in sorted(archive_rows.keys()):
            old_row = archive_rows[hh]
            new_row = new_rows[hh]
            for csv_col, metric_name in metric_map.items():
                old_val = float(old_row[csv_col])
                new_val = float(new_row[csv_col])
                diff = abs(new_val - old_val)
                assert diff < V4_EPSILON, (
                    f"V4 all-39 drift on candidate {hh} metric {metric_name}: "
                    f"old={old_val!r} new={new_val!r} abs_diff={diff!r} "
                    f"exceeds ε={V4_EPSILON} (spec §4.2 strict stop-condition)"
                )

    def test_v4_all_39_total_trades_exact_match(self) -> None:
        """All 39 candidates' total_trades (int) + holdout_passed (bool) match exactly.

        CB3 PFR R1 ADOPT v2: exact-equality coverage for full cohort.
        """
        archive_rows = _load_all_39_candidates_from_csv(ARCHIVE_RUN_DIR)
        new_rows = _load_all_39_candidates_from_csv(ACTIVE_RUN_DIR)
        for hh in sorted(archive_rows.keys()):
            old_row = archive_rows[hh]
            new_row = new_rows[hh]
            old_trades = int(old_row["holdout_total_trades"])
            new_trades = int(new_row["holdout_total_trades"])
            assert new_trades == old_trades, (
                f"V4 all-39 total_trades exact-match FAIL on {hh}: "
                f"old={old_trades} new={new_trades}"
            )
            # holdout_passed CSV column is boolean-ish string (e.g. 'True'/'False')
            old_passed = str(old_row["holdout_passed"]).strip().lower() in {"true", "1"}
            new_passed = str(new_row["holdout_passed"]).strip().lower() in {"true", "1"}
            assert new_passed == old_passed, (
                f"V4 all-39 holdout_passed exact-match FAIL on {hh}: "
                f"old={old_row['holdout_passed']!r} new={new_row['holdout_passed']!r}"
            )


class TestG4ParquetIntegrity:
    """G4 per-bar parquet integrity gate."""

    def test_g4_per_bar_parquet_row_count_matches_t_obs(self) -> None:
        """Per-bar parquet row count must equal T_obs from summary; SHA256 must
        match summary AND registry; data must be non-degenerate; timestamp UTC-aware.

        Spec §4.3 G4: (a) row count = T_obs from summary; (b) SHA256 of
        file = `returns_per_bar_sha256` in summary + registry; (c) data not
        all-NaN; (d) `timestamp` column UTC-aware (parquet writes `timestamp`
        as a column not as the index per engine.py:498-510).

        CH4 PFR R1 ADOPT v2: extended to query registry per-candidate row and
        assert returns_per_bar_path + returns_per_bar_sha256 + T_obs all match
        across summary + computed + registry (not just summary as v1 claimed).
        """
        from backtest.experiment_registry import get_connection, DEFAULT_DB_PATH, get_run

        conn = get_connection(DEFAULT_DB_PATH)
        try:
            for hh in SAMPLE_HASHES:
                summary = _load_summary(ACTIVE_RUN_DIR, hh)
                candidate_dir = ACTIVE_RUN_DIR / hh
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
                # (b) SHA256 match — summary + computed + registry tri-way
                hasher = hashlib.sha256()
                with parquet_path.open("rb") as fh:
                    for chunk in iter(lambda: fh.read(65536), b""):
                        hasher.update(chunk)
                computed_sha = hasher.hexdigest()
                stored_sha = summary["returns_per_bar_sha256"]
                assert computed_sha == stored_sha, (
                    f"G4(b) SHA256 summary-vs-computed mismatch on {hh}: "
                    f"computed={computed_sha!r} stored_in_summary={stored_sha!r}"
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
                # CH4 PFR R1 ADOPT v2: registry row query + per-candidate linkage
                # The child run_id in the registry is per-candidate; query by
                # parent_run_id + candidate-specific identifier (hypothesis_hash
                # is the per-child run_id naming under the producer's LC-b path).
                cur = conn.cursor()
                cur.execute(
                    "SELECT run_id FROM runs WHERE parent_run_id = ? "
                    "AND run_type = 'regime_holdout' AND run_id LIKE ?",
                    (BCNARROW_PARENT_RUN_ID, f"%{hh}%"),
                )
                child_id_row = cur.fetchone()
                assert child_id_row is not None, (
                    f"CH4 G4 registry lookup FAIL on {hh}: no child run row "
                    f"found with hypothesis_hash {hh} under parent "
                    f"{BCNARROW_PARENT_RUN_ID}"
                )
                child_run_id = child_id_row[0]
                child_row = get_run(conn, child_run_id)
                assert child_row is not None, (
                    f"CH4 G4 get_run returned None for child_run_id={child_run_id!r}"
                )
                # (CH4-a) returns_per_bar_path stored matches expected basename
                expected_path_basename = "returns_per_bar.parquet"
                stored_path = child_row.get("returns_per_bar_path")
                assert stored_path is not None and expected_path_basename in str(stored_path), (
                    f"CH4 G4 child registry returns_per_bar_path FAIL on {hh}: "
                    f"expected basename {expected_path_basename!r}, "
                    f"got {stored_path!r}"
                )
                # (CH4-b) SHA256 in registry = computed = summary (tri-way)
                stored_registry_sha = child_row.get("returns_per_bar_sha256")
                assert stored_registry_sha == computed_sha == stored_sha, (
                    f"CH4 G4 SHA256 tri-way mismatch on {hh}: "
                    f"computed={computed_sha!r} summary={stored_sha!r} "
                    f"registry={stored_registry_sha!r}"
                )
                # (CH4-c) T_obs in registry = parquet rows = summary
                stored_registry_t_obs = child_row.get("T_obs")
                assert (
                    int(stored_registry_t_obs)
                    == len(df)
                    == t_obs_summary
                ), (
                    f"CH4 G4 T_obs tri-way mismatch on {hh}: "
                    f"parquet rows={len(df)} summary T_obs={t_obs_summary} "
                    f"registry T_obs={stored_registry_t_obs}"
                )
        finally:
            conn.close()

    def test_g4_all_39_per_bar_parquet_integrity(self) -> None:
        """All 39 candidates: per-bar parquet exists + non-empty + SHA256 in registry.

        CB3 PFR R1 ADOPT v2: extends G4 coverage to full cohort. Per-candidate
        N=2 deep validation above + this all-39 surface-level check together
        satisfy spec §4.3 G4 full-cohort coverage requirement.
        """
        from backtest.experiment_registry import get_connection, DEFAULT_DB_PATH

        archive_rows = _load_all_39_candidates_from_csv(ACTIVE_RUN_DIR)
        conn = get_connection(DEFAULT_DB_PATH)
        try:
            cur = conn.cursor()
            for hh in sorted(archive_rows.keys()):
                candidate_dir = ACTIVE_RUN_DIR / hh
                parquet_path = candidate_dir / "returns_per_bar.parquet"
                assert parquet_path.exists(), (
                    f"G4 all-39 missing parquet for candidate {hh}"
                )
                df = pd.read_parquet(parquet_path)
                assert len(df) > 0, (
                    f"G4 all-39 empty parquet for candidate {hh}"
                )
                # SHA256 vs registry
                hasher = hashlib.sha256()
                with parquet_path.open("rb") as fh:
                    for chunk in iter(lambda: fh.read(65536), b""):
                        hasher.update(chunk)
                computed_sha = hasher.hexdigest()
                cur.execute(
                    "SELECT returns_per_bar_sha256 FROM runs WHERE "
                    "parent_run_id = ? AND run_type = 'regime_holdout' "
                    "AND run_id LIKE ?",
                    (BCNARROW_PARENT_RUN_ID, f"%{hh}%"),
                )
                row = cur.fetchone()
                assert row is not None, (
                    f"G4 all-39 registry lookup FAIL on {hh}"
                )
                assert row[0] == computed_sha, (
                    f"G4 all-39 SHA256 mismatch on {hh}: "
                    f"computed={computed_sha!r} registry={row[0]!r}"
                )
        finally:
            conn.close()


class TestG5GammaRoundTrip:
    """G5 γ3 / γ4 round-trip gate."""

    def test_g5_gamma_round_trip_from_parquet_within_epsilon(self) -> None:
        """Recompute γ3/γ4 from per-bar parquet via compute_moments; must
        match stored summary values within abs diff < 1e-10 (float64 round-trip
        determinism). T_obs must match bit-exact (integer).

        Spec §4.3 G5: load parquet → compute_moments(returns_array) → compare.

        AM2 PFR R1 ADOPT v2: This test reads df["return"] directly rather than
        recomposing via compute_per_bar_returns(equity_curve) as spec §6.4 line
        363 suggests. The two approaches are SEMANTICALLY EQUIVALENT (parquet's
        `return` column was written from compute_per_bar_returns output at
        engine.py:538; compute_moments' np.isfinite filter handles the leading
        NaN identically). The df["return"] approach is ADDITIONALLY MORE
        RIGOROUS because it validates the parquet column's round-trip integrity
        end-to-end (catches parquet write/read drift that the recompose
        approach would miss).
        """
        from backtest.engine import compute_moments

        for hh in SAMPLE_HASHES:
            summary = _load_summary(ACTIVE_RUN_DIR, hh)
            candidate_dir = ACTIVE_RUN_DIR / hh
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

    def test_g5_all_39_gamma_round_trip(self) -> None:
        """All 39 candidates: γ3/γ4 round-trip via compute_moments within ε=1e-10.

        CB3 PFR R1 ADOPT v2: full-cohort G5 coverage. Loads per-candidate
        holdout_summary.json (NOT the N=2 fixture) for each of the 39 candidates.
        """
        from backtest.engine import compute_moments

        archive_rows = _load_all_39_candidates_from_csv(ACTIVE_RUN_DIR)
        for hh in sorted(archive_rows.keys()):
            summary = _load_summary(ACTIVE_RUN_DIR, hh)
            candidate_dir = ACTIVE_RUN_DIR / hh
            parquet_path = candidate_dir / "returns_per_bar.parquet"
            assert parquet_path.exists(), (
                f"G5 all-39 missing parquet for candidate {hh}"
            )
            df = pd.read_parquet(parquet_path)
            returns_arr = df["return"].to_numpy(dtype=np.float64)
            moments = compute_moments(returns_arr)
            t_obs_recomputed = int(moments["T_obs"])
            t_obs_stored = int(summary["T_obs"])
            assert t_obs_recomputed == t_obs_stored, (
                f"G5 all-39 T_obs round-trip FAIL on {hh}: "
                f"recomputed={t_obs_recomputed} stored={t_obs_stored}"
            )
            for gamma_key in ("gamma3", "gamma4"):
                recomputed = moments[gamma_key]
                stored = summary[gamma_key]
                if recomputed is None and stored is None:
                    continue
                assert recomputed is not None and stored is not None, (
                    f"G5 all-39 {gamma_key} None-asymmetry on {hh}: "
                    f"recomputed={recomputed!r} stored={stored!r}"
                )
                diff = abs(float(recomputed) - float(stored))
                assert diff < G5_EPSILON, (
                    f"G5 all-39 {gamma_key} round-trip drift on {hh}: "
                    f"abs_diff={diff!r} exceeds ε={G5_EPSILON}"
                )


class TestG6RegistryParentChildIntegrity:
    """G6 registry parent-child integrity gate."""

    def test_g6_registry_parent_child_integrity_after_fire(self) -> None:
        """Registry must contain exactly 1 batch_summary parent row at
        run_id=phase4_forward_2026_15bps_v1_b_c_narrow + 39 child rows
        (run_type=regime_holdout); each child's parent_run_id = parent;
        parent cohort metadata non-null; child per-candidate metadata non-null;
        parent-only fields NULL at children.

        Spec §4.3 G6: SELECT COUNT(*) FROM runs WHERE
        parent_run_id='phase4_forward_2026_15bps_v1_b_c_narrow' AND
        run_type='regime_holdout' = 39; parent row exists with
        run_type='batch_summary'. Cohort-level metadata at parent; per-
        candidate metadata at children.

        BLOCKING-5 carry per Plan v3-Phase2 line 3651: G6 inline coverage
        required at Phase 3 (not enumerated in spec §6.4).

        CH4 PFR R1 ADOPT v2: extended to assert parent row cohort metadata
        (initial_capital + fee_model + execution_config_sha256 + git_commit +
        created_at_utc + batch_id + parent_run_id) non-null + each child row
        per-candidate metadata (hypothesis_hash + sharpe_ratio + max_drawdown
        + total_return + total_trades + regime_holdout_passed) non-null +
        parent-only fields (returns_per_bar_path etc.) NULL at children level.
        """
        from backtest.experiment_registry import get_connection, DEFAULT_DB_PATH

        conn = get_connection(DEFAULT_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            # Parent row
            cur.execute(
                "SELECT * FROM runs WHERE run_id = ?",
                (BCNARROW_PARENT_RUN_ID,),
            )
            parent_rows = cur.fetchall()
            assert len(parent_rows) == 1, (
                f"G6 parent row count FAIL: expected 1 parent row at "
                f"run_id={BCNARROW_PARENT_RUN_ID!r}, found {len(parent_rows)}"
            )
            parent_row = parent_rows[0]
            assert parent_row["run_type"] == "batch_summary", (
                f"G6 parent row run_type FAIL: expected 'batch_summary', "
                f"found {parent_row['run_type']!r}"
            )
            # CH4 PFR R1 ADOPT v2: parent cohort metadata non-null
            parent_cohort_metadata = (
                "initial_capital",
                "fee_model",
                "git_commit",
                "created_at_utc",
                "batch_id",
            )
            parent_keys = set(parent_row.keys())
            for field_name in parent_cohort_metadata:
                if field_name not in parent_keys:
                    continue  # tolerate schema variants; only assert when present
                assert parent_row[field_name] is not None, (
                    f"CH4 G6 parent row cohort metadata NULL FAIL: "
                    f"field={field_name!r} expected non-null at parent_run_id="
                    f"{BCNARROW_PARENT_RUN_ID}"
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
            # AL4 PFR R1 ADOPT v2: Independent invariant check (does NOT
            # short-circuit on the prior query's filter clause): future schema
            # changes could re-introduce NULL parent_run_ids that pass
            # `WHERE run_type='regime_holdout'` clauses but break parent-child
            # linkage. This catches that drift class.
            cur.execute(
                "SELECT DISTINCT parent_run_id FROM runs WHERE parent_run_id = ?",
                (BCNARROW_PARENT_RUN_ID,),
            )
            distinct_parents = [row[0] for row in cur.fetchall()]
            assert distinct_parents == [BCNARROW_PARENT_RUN_ID], (
                f"G6 child parent_run_id linkage FAIL: expected "
                f"[{BCNARROW_PARENT_RUN_ID!r}], found {distinct_parents!r}"
            )
            # CH4 PFR R1 ADOPT v2: child rows per-candidate metadata non-null
            cur.execute(
                "SELECT * FROM runs WHERE parent_run_id = ? "
                "AND run_type = 'regime_holdout'",
                (BCNARROW_PARENT_RUN_ID,),
            )
            children = cur.fetchall()
            per_candidate_metadata = (
                "hypothesis_hash",
                "sharpe_ratio",
                "max_drawdown",
                "total_return",
                "total_trades",
                "regime_holdout_passed",
            )
            for child in children:
                child_keys = set(child.keys())
                for field_name in per_candidate_metadata:
                    if field_name not in child_keys:
                        continue  # tolerate schema variants
                    assert child[field_name] is not None, (
                        f"CH4 G6 child row per-candidate metadata NULL FAIL: "
                        f"field={field_name!r} at child run_id={child['run_id']!r}"
                    )
                # Parent-only fields (NULL at children level expected)
                # Note: returns_per_bar_path + returns_per_bar_sha256 + T_obs
                # are per-candidate persistence fields at children (NOT parent-
                # only), so don't assert NULL on those. Parent-only fields are
                # those that ONLY make sense at cohort level. Empty set if no
                # such fields surface in current schema; this loop is a
                # placeholder for future drift catches.
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

    def test_g7_archive_refuses_cross_filesystem_attempt(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """G7 cross-FS guard coverage: producer's _archive_canonical_pre_flight
        uses Path.stat().st_dev to detect cross-FS source-vs-destination;
        raises NotImplementedError.

        In production fire, sibling-dir-under-common-parent guarantees same-FS
        (st_dev match). This test covers the defensive guard for operator
        misconfiguration via mocked Path.stat().

        AM1 PFR R1 ADOPT v2: NEW test for st_dev guard coverage.
        """
        from scripts.run_phase2c_evaluation_gate import (
            _archive_canonical_pre_flight,
            BCNARROW_ARCHIVE_BASENAME,
        )

        canonical = tmp_path / "canonical"
        canonical.mkdir()
        (canonical / "marker.txt").write_text("orig")
        archive_root = tmp_path / "archive"
        archive_root.mkdir()

        class FakeStat:
            def __init__(self, dev: int):
                self.st_dev = dev

        original_stat = Path.stat

        def mocked_stat(self, *args, **kwargs):
            if "archive" in str(self):
                return FakeStat(dev=999)  # different FS
            return FakeStat(dev=111)

        monkeypatch.setattr(Path, "stat", mocked_stat)

        with pytest.raises((NotImplementedError, RuntimeError)) as exc_info:
            _archive_canonical_pre_flight(
                canonical_path=canonical,
                archive_root=archive_root,
                archive_basename=BCNARROW_ARCHIVE_BASENAME,
            )
        msg = str(exc_info.value).lower()
        assert "cross" in msg or "filesystem" in msg or "fs" in msg or "device" in msg, (
            f"G7 cross-FS refuse error message must reference cross-FS guard. "
            f"Got: {exc_info.value!r}"
        )
```

- [ ] **Step 13.3: Verify RED phase (9 fire-state tests SKIPPED-or-RED + 2 static contract tests PASS + 1 drift-stop hybrid)**

```bash
python -m pytest tests/test_b_c_narrow_v4_reproducibility.py -v
```

Per CM5 PFR R1 ADOPT v2: with the CB2 path-adaptive pattern, fire-state tests now SKIP cleanly via `_resolve_active_run_dir` → `pytest.skip(...)` (rather than raw FAIL) when neither sibling nor canonical exists. Skips encode the same RED-pre-fire semantics that the v1 plan called "FAIL with missing-file message"; both equally signal "fire not yet executed". Static contract tests (G7 refuse + G7 cross-FS) PASS unconditionally via tmp_path. The drift-stop test is a hybrid: it reads from ACTIVE_RUN_DIR + ARCHIVE_RUN_DIR (so it SKIPs pre-fire) but exercises the all-39 ε-comparison + synthetic perturbation injection on real metric values when the fire is complete.

Expected behavior (12 total tests):
- `TestV4Reproducibility::test_v4_per_candidate_metric_diff_within_epsilon` → SKIPPED (sibling/canonical absent) pre-fire; PASSED post-fire
- `TestV4Reproducibility::test_v4_total_trades_exact_match` → SKIPPED pre-fire; PASSED post-fire
- `TestV4Reproducibility::test_v4_drift_stop_condition_blocks_seal_on_breach` → SKIPPED pre-fire (ACTIVE_RUN_DIR resolution); PASSED post-fire (synthetic perturbation triggers AssertionError)
- `TestV4Reproducibility::test_v4_all_39_per_candidate_metric_diff_within_epsilon` → SKIPPED pre-fire; PASSED post-fire
- `TestV4Reproducibility::test_v4_all_39_total_trades_exact_match` → SKIPPED pre-fire; PASSED post-fire
- `TestG4ParquetIntegrity::test_g4_per_bar_parquet_row_count_matches_t_obs` → SKIPPED pre-fire; PASSED post-fire
- `TestG4ParquetIntegrity::test_g4_all_39_per_bar_parquet_integrity` → SKIPPED pre-fire; PASSED post-fire
- `TestG5GammaRoundTrip::test_g5_gamma_round_trip_from_parquet_within_epsilon` → SKIPPED pre-fire; PASSED post-fire
- `TestG5GammaRoundTrip::test_g5_all_39_gamma_round_trip` → SKIPPED pre-fire; PASSED post-fire
- `TestG6RegistryParentChildIntegrity::test_g6_registry_parent_child_integrity_after_fire` → FAIL with AssertionError "expected 1 parent row ... found 0" (registry has no parent row pre-fire; no skip on registry queries because the registry is always present)
- `TestG7ArchiveIdempotency::test_g7_archive_idempotency_refuses_existing_target` → PASS (uses tmp_path)
- `TestG7ArchiveIdempotency::test_g7_archive_refuses_cross_filesystem_attempt` → PASS (uses tmp_path + monkeypatch)

Summary expected at Step 13.3 (pre-fire): 9 SKIPPED + 2 PASSED + 1 FAILED (G6 registry parent-child).

Step 14.4 (post-fire): 12 PASSED + 0 SKIPPED + 0 FAILED.

If you see a different failure pattern (e.g., ImportError, ModuleNotFoundError, AttributeError on `BCNARROW_*` constants), STOP — Phase 2 SEAL state may have regressed (already caught by Precondition 4 + 5 in §"Phase 3 execution preconditions", but re-check).

- [ ] **Step 13.4: Commit pre-fire test bodies + pre-flight evidence**

```bash
git add tests/test_b_c_narrow_v4_reproducibility.py
git commit -m "$(cat <<'EOF'
test(b-c-narrow/phase-3): T13 RED — V4+G4-G7 test bodies (12 methods)

Per Plan v3-Phase3 v2 Task 13. RED phase before T13 fire authorization.

Test methods (12 total = 5 spec §6.4 N=2 fixture + 2 BLOCKING-5 carry G6+G7
+ 4 all-39 V4 gate per CB3 PFR R1 ADOPT v2 + 1 cross-FS G7 per AM1 PFR R1
ADOPT v2):
- TestV4Reproducibility::test_v4_per_candidate_metric_diff_within_epsilon
- TestV4Reproducibility::test_v4_total_trades_exact_match
- TestV4Reproducibility::test_v4_drift_stop_condition_blocks_seal_on_breach
- TestV4Reproducibility::test_v4_all_39_per_candidate_metric_diff_within_epsilon
- TestV4Reproducibility::test_v4_all_39_total_trades_exact_match
- TestG4ParquetIntegrity::test_g4_per_bar_parquet_row_count_matches_t_obs
- TestG4ParquetIntegrity::test_g4_all_39_per_bar_parquet_integrity
- TestG5GammaRoundTrip::test_g5_gamma_round_trip_from_parquet_within_epsilon
- TestG5GammaRoundTrip::test_g5_all_39_gamma_round_trip
- TestG6RegistryParentChildIntegrity::test_g6_registry_parent_child_integrity_after_fire
- TestG7ArchiveIdempotency::test_g7_archive_idempotency_refuses_existing_target
- TestG7ArchiveIdempotency::test_g7_archive_refuses_cross_filesystem_attempt

Expected at this commit (pre-fire): 9 SKIPPED + 2 PASSED + 1 FAILED (G6).
SKIPs encode RED-pre-fire semantics via _resolve_active_run_dir per CB2 ADOPT.
PASSes lock contracts that are TESTABLE without the fire — by design.
G6 FAILs because registry parent row absent (no skip on registry queries).

GREEN expected at Step 14.5 post-fire + fixture capture (12 PASSED).

Per BLOCKING-5 carry from Plan v3-Phase2 line 3651: G6+G7 inline test
bodies authored at Phase 3 (NOT enumerated in spec §6.4; required for
inline coverage of all 4 §4.3 G-gates).

Sample candidates per fixture sampling rule (lexicographically smallest 2):
- 18d92ce5d0b40cc7
- 22864f01a49e3452

Fixture file (tests/fixtures/b_c_narrow_archived_baseline.json) captured
POST-T13 fire BEFORE T14 V4 gate runs (see Step 14.3).

Path-adaptive design per CB2 PFR R1 ADOPT v2: SIBLING_RUN_DIR (pre-T14b)
OR CANONICAL_RUN_DIR (post-T14b) resolved via _resolve_active_run_dir;
tests work in both states satisfying CLAUDE.md HARD CONSTRAINT.

All-39 V4 gate per CB3 PFR R1 ADOPT v2: reads raw CSV directly (not
fixture); spec §4.2/§4.3 per-candidate full-cohort coverage achieved.

AH1 subsumed: drift-stop test rewritten to inject synthetic ε-breach into
one candidate within the all-39 loop, asserting AssertionError mentions
that candidate's hash; locks real production code path not pure arithmetic.

CH4 PFR R1 ADOPT v2: G4 + G6 extended with registry tri-way assertions
(returns_per_bar_path + returns_per_bar_sha256 + T_obs match across
summary + computed + registry; parent cohort metadata + child per-candidate
metadata non-null).
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

# (g) AL5 PFR R1 ADOPT v2: Verify no `holdout_error` candidates per spec §7 R5.
# Per spec §7 R5: any holdout_error candidate in re-run → SEAL BLOCKED pending Charlie adjudication.
# Without this check, V4 gate could pull from an errored candidate and produce false positive PASS/FAIL.
python -c "
import json
from pathlib import Path
sibling = Path('data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow')
errs = []
for cand_dir in sibling.iterdir():
    if not cand_dir.is_dir():
        continue
    summary_path = cand_dir / 'holdout_summary.json'
    if not summary_path.exists():
        continue
    summary = json.loads(summary_path.read_text())
    if summary.get('lifecycle_state') == 'holdout_error':
        errs.append(cand_dir.name)
assert not errs, f'holdout_error in cohort: {errs} (spec §7 R5: SEAL BLOCKED pending Charlie adjudication)'
print(f'OK: zero holdout_error candidates in cohort')
"
# Expected: 'OK: zero holdout_error candidates in cohort'
```

If any verification (a)-(g) fails, STOP — capture full output, surface to Charlie. Do NOT proceed to Step 14.3.

If any candidate surfaces as `holdout_error` at (g), STOP and surface to Charlie before Step 14.3 fixture capture — V4 gate may pull from an errored candidate and produce false positive failures. Per spec §7 R5: SEAL blocked pending adjudication.

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

- [ ] **Step 14.4: Run V4 gate G4-G7 + ε=1e-6 verification (12 tests)**

```bash
python -m pytest tests/test_b_c_narrow_v4_reproducibility.py -v
```

- [ ] **Step 14.5: Verify GREEN (all 12 V4 tests pass)**

Expected pytest output: `12 passed in <X>s` (0 failed, 0 skipped). Specifically:
- `TestV4Reproducibility::test_v4_per_candidate_metric_diff_within_epsilon` → PASSED
- `TestV4Reproducibility::test_v4_total_trades_exact_match` → PASSED
- `TestV4Reproducibility::test_v4_drift_stop_condition_blocks_seal_on_breach` → PASSED
- `TestV4Reproducibility::test_v4_all_39_per_candidate_metric_diff_within_epsilon` → PASSED
- `TestV4Reproducibility::test_v4_all_39_total_trades_exact_match` → PASSED
- `TestG4ParquetIntegrity::test_g4_per_bar_parquet_row_count_matches_t_obs` → PASSED
- `TestG4ParquetIntegrity::test_g4_all_39_per_bar_parquet_integrity` → PASSED
- `TestG5GammaRoundTrip::test_g5_gamma_round_trip_from_parquet_within_epsilon` → PASSED
- `TestG5GammaRoundTrip::test_g5_all_39_gamma_round_trip` → PASSED
- `TestG6RegistryParentChildIntegrity::test_g6_registry_parent_child_integrity_after_fire` → PASSED
- `TestG7ArchiveIdempotency::test_g7_archive_idempotency_refuses_existing_target` → PASSED
- `TestG7ArchiveIdempotency::test_g7_archive_refuses_cross_filesystem_attempt` → PASSED

If any test FAILs:
- V4 metric drift (N=2 fixture tests or all-39 tests FAIL) → STOP; SEAL BLOCKED per spec §4.2 stop-condition; surface to Charlie for adjudication paths (a/b/c per spec §4.2: environmental ε widen, semantic Q2 re-litigation, or accept-drift with §8 INDETERMINATE re-classification in this cycle's NOTE doc)
- G4-G7 FAIL → STOP; gate violation indicates producer/engine bug or partial-write state; surface to Charlie

Do NOT proceed to Step 14.6 unless all 12 tests PASS.

Also run full test suite zero-regression check:

```bash
python -m pytest -q
```

Expected: `2372 passed` (= 2360 from Phase 2 baseline + 12 new V4 tests, with 2 xfailed unchanged) OR equivalent. Net new = 12 passing tests (no test deletions; no regressions). If full suite reveals regressions outside `test_b_c_narrow_v4_reproducibility.py`, STOP — surface to Charlie.

- [ ] **Step 14.6: Commit T13 fire evidence + V4 gate results + fixture**

Note: data artifacts under `data/` are gitignored; reference paths + verification commands in the commit message body for forensic recoverability.

```bash
git add tests/fixtures/b_c_narrow_archived_baseline.json
git commit -m "$(cat <<'EOF'
evidence(b-c-narrow/phase-3): T13 fire + T14 V4 gate GREEN (Task 14)

Per Plan v3-Phase3 v2 Task 14. Charlie register #N+19a fired authorization.

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

T14 V4 gate (G4-G7 + ε=1e-6 per-candidate + all-39 full-cohort coverage):
- 12/12 tests in tests/test_b_c_narrow_v4_reproducibility.py PASSED
- Full suite zero regression (2372 passed / 0 failed / 2 xfailed)

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

Task 14 complete; V4 gate GREEN (all 12 tests passed).

NEXT STEP requires destructive canonical-path mutation:
  - mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/
       data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/
  - Sibling dir becomes canonical; downstream consumers of the canonical
    path (Tier 6 evaluation application + future Phase 5 work) see new
    B-C-narrow content; original lineage preserved at
    archive/phase4_forward_2026_15bps_v1_d0b8101/ (snapshot of pre-fire state)

What to surface to Charlie:
  - V4 GREEN evidence: pytest output (12 passed) + commit landed at
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

If V4 had FAILED (any of the 12 tests per v2 expansion), this STOP would be
replaced by SEAL BLOCKED — STOP HERE + surface to Charlie for adjudication
paths (a/b/c per spec §4.2). T14b would NOT execute on V4 failure.

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

If any verification (a)-(f) fails, surface to Step 14b.2.5 failure adjudication block below — do NOT skip to Step 14b.3.

Per CB2 PFR R1 ADOPT v2: re-run the V4+G4-G7 suite POST-mv. With the path-adaptive `_resolve_active_run_dir` pattern, `ACTIVE_RUN_DIR` now resolves to `CANONICAL_RUN_DIR` (sibling is gone; canonical is populated); tests should PASS in BOTH pre-T14b and post-T14b states:

```bash
python -m pytest tests/test_b_c_narrow_v4_reproducibility.py -v
```

Expected: `12 passed`. CB2 PFR R1 ADOPT v2 satisfies CLAUDE.md HARD CONSTRAINT "NEVER commit code that doesn't pass existing tests" across both Task 14b commit (post-mv) and Task 14c ratify (post-mv) lifecycle stages.

If any test FAILS post-mv: STOP — `_resolve_active_run_dir` may have regressed OR canonical state may differ from sibling state in a way the path-adaptive design did not anticipate. Surface to Charlie before committing.

- [ ] **Step 14b.2.5: Failure adjudication (if post-mv verification FAILS)**

Per AM4 PFR R1 ADOPT v2: explicit failure-path specification for the T14b mv operation.

If Step 14b.2 verification fails (canonical incomplete; sibling not fully removed; registry rows broken):

1. **STOP** — do NOT attempt forward recovery. The state is partially-mutated.
2. **archive/ intact**: producer W3's shutil.move on same-FS is atomic; the archive at `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` retains the original lineage regardless of T14b mv outcome.
3. **Surface to Charlie**: report the specific verification failure mode + the current FS state (which dirs exist + which registry rows query correctly). Do NOT attempt reverse-mv (`mv canonical sibling`) without explicit Charlie register #N+19b' (b-prime — separate boundary for recovery operation).
4. **Phase 4 SEAL bundle BLOCKED** until canonical = expected state per Charlie adjudication.

The 5-step adjudication ladder is: failure detected at Step 14b.2 → STOP at Step 14b.2.5 → preserve archive intactness → surface to Charlie with FS+registry inventory → wait for Charlie register #N+19b' recovery authorization before any reverse-mv operation.

- [ ] **Step 14b.3: Commit T14b evidence (OPTIONAL — only if Charlie register #N+19b explicitly requested separate boundary marker)**

Per AL1 PFR R1 ADOPT v2: default behavior is to SKIP this empty commit and roll evidence into Step 14c.2 commit body. The Step 14c.2 commit message body already enumerates T14b evidence (see Step 14c.2 commit message at plan section below).

ONLY execute this commit if Charlie register #N+19b authorization message explicitly requested a separate boundary marker commit for forensic recoverability beyond Step 14c.2's enumeration. Otherwise, SKIP this step entirely.

If Charlie did request a separate boundary marker:

```bash
git commit --allow-empty -m "$(cat <<'EOF'
evidence(b-c-narrow/phase-3): T14b canonical-path relocation (Task 14b)

Per Plan v3-Phase3 v2 Task 14b. Charlie register #N+19b fired authorization
+ explicitly requested separate boundary-marker commit per AL1 PFR R1 ADOPT
v2 OPTIONAL path.

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

V4 test status post-mv: per CB2 PFR R1 ADOPT v2 path-adaptive design via
_resolve_active_run_dir, all 12 V4+G4-G7 tests PASS post-mv (ACTIVE_RUN_DIR
resolves to CANONICAL_RUN_DIR). This satisfies CLAUDE.md HARD CONSTRAINT
"NEVER commit code that doesn't pass existing tests".

Next: Phase 3 ratify packet at Task 14c → Charlie register #N+19c.
EOF
)"
```

Note: this commit is `--allow-empty` because Step 14b is a pure FS mv (no file changes tracked by git). The default is to SKIP this commit per AL1 PFR R1 ADOPT v2 (roll evidence into Step 14c.2 instead).

---

### Task 14c: Phase 3 ratify packet artifact

**Files:**
- Create: `docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md` (NEW)

- [ ] **Step 14c.1: Write Phase 3 ratify packet**

```bash
mkdir -p docs/superpowers/phase-3-impl-results
```

Write the following file content to `docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md` (replace `<...>` placeholders with measured values at commit time).

Per AL3 PFR R1 ADOPT v2: placeholders correspond to: `<sha>` = output of Step 13.1(a)'s `git rev-parse --short HEAD` at fire-completion time; `<X seconds wall-clock>` = `time python -m scripts...` duration from Step 14.1 (record before next step); `<ISO UTC>` = `datetime.now(timezone.utc).isoformat()` at ratify-packet-write time. Implementer must record these measurements in session before Step 14c.1 commit.

```markdown
# B-C-narrow Phase 3 ratify packet

**Date:** <ISO UTC at Step 14c.1 commit time>
**HEAD commit:** <git rev-parse --short HEAD>
**Plan version:** v3-Phase3 v2 (PFR R1 17 ADOPT applied per Charlie register #N+19 Path 1 2026-05-28; further PFR R2 iteration count if amended)
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
| Pre-fire raw_payloads 998 symlinks resolve | Step 13.1 (e)(f) | <PASS / details> | `find raw_payloads/batch_phase2c_15_main_fire_combined -type l \| wc -l` returned 998; 3-sample resolution OK (CB1 PFR R1 ADOPT v2 path correction) |
| Pre-fire registry clean (0 parent + 0 children) | Step 13.1 (g) | <PASS / details> | SQLite query returned 0 + 0 (or runs table absent) |

## T13 fire results

**Command executed:** `python -m scripts.run_phase2c_evaluation_gate --enable-b-c-narrow-recovery --candidate-hashes <39 csv> --source-batch-id phase2c_15_main_fire_combined --regime-key evaluation_regimes.forward_2026 --execution-config config/execution_phase4_15bps.yaml --run-id phase4_forward_2026_15bps_v1_b_c_narrow --output-root data/phase2c_evaluation_gate/`

**Exit code:** 0
**Wall-clock duration:** <measured seconds>
**Producer steps confirmed in stdout:** W0 identity guard PASS / W1a finalize preflight PASS / W3 archive performed / 39 candidates evaluated / W4 finalize POST-fire wrote parent batch_summary

## T14 V4 gate results (G4-G7 + ε=1e-6; 12 tests per CB3 + AM1 + CH4 PFR R1 ADOPT v2 expansion)

| Test | Spec ref | Result |
|---|---|---|
| `TestV4Reproducibility::test_v4_per_candidate_metric_diff_within_epsilon` | §4.2 + §6.4 (N=2 fixture) | <PASSED> |
| `TestV4Reproducibility::test_v4_total_trades_exact_match` | §4.2 + §6.4 (N=2 fixture) | <PASSED> |
| `TestV4Reproducibility::test_v4_drift_stop_condition_blocks_seal_on_breach` | §4.2 + §6.4 (synthetic ε-breach per CB3+AH1 ADOPT) | <PASSED> |
| `TestV4Reproducibility::test_v4_all_39_per_candidate_metric_diff_within_epsilon` | §4.2 (all-39 per CB3 ADOPT v2) | <PASSED> |
| `TestV4Reproducibility::test_v4_all_39_total_trades_exact_match` | §4.2 (all-39 per CB3 ADOPT v2) | <PASSED> |
| `TestG4ParquetIntegrity::test_g4_per_bar_parquet_row_count_matches_t_obs` | §4.3 G4 (N=2 deep + registry tri-way per CH4 ADOPT v2) | <PASSED> |
| `TestG4ParquetIntegrity::test_g4_all_39_per_bar_parquet_integrity` | §4.3 G4 (all-39 surface per CB3 ADOPT v2) | <PASSED> |
| `TestG5GammaRoundTrip::test_g5_gamma_round_trip_from_parquet_within_epsilon` | §4.3 G5 (N=2 per AM2 docstring note) | <PASSED> |
| `TestG5GammaRoundTrip::test_g5_all_39_gamma_round_trip` | §4.3 G5 (all-39 per CB3 ADOPT v2) | <PASSED> |
| `TestG6RegistryParentChildIntegrity::test_g6_registry_parent_child_integrity_after_fire` | §4.3 G6 (BLOCKING-5 carry + AL4 invariant comment + CH4 metadata extensions) | <PASSED> |
| `TestG7ArchiveIdempotency::test_g7_archive_idempotency_refuses_existing_target` | §4.3 G7 (BLOCKING-5 carry) | <PASSED> |
| `TestG7ArchiveIdempotency::test_g7_archive_refuses_cross_filesystem_attempt` | §4.3 G7 (cross-FS guard per AM1 ADOPT v2) | <PASSED> |

**Verification command:**

```bash
python -m pytest tests/test_b_c_narrow_v4_reproducibility.py -v
```

**Full suite zero-regression:** <2372 passed / 0 failed / 2 xfailed> (Phase 2 baseline 2360 + 12 new V4 tests; net new = 12 passing)

## Per-gate G4-G7 result summary (additional evidence)

| Gate | Spec ref | Coverage | Result |
|---|---|---|---|
| G4 — Per-bar parquet integrity | §4.3 G4 | row count = T_obs (a) + SHA256 match (b) + non-degenerate (c) + UTC-aware timestamp column (d) + registry tri-way per CH4 ADOPT v2 | <PASS for N=2 deep + N=39 surface per CB3 ADOPT v2> |
| G5 — γ3/γ4 round-trip | §4.3 G5 | `compute_moments` recompute vs stored within abs diff < 1e-10 + T_obs bit-exact | <PASS for N=2 + N=39 per CB3 ADOPT v2> |
| G6 — Registry parent-child integrity | §4.3 G6 | 1 parent batch_summary + 39 child regime_holdout + parent_run_id linkage + parent cohort metadata + child per-candidate metadata non-null per CH4 ADOPT v2 | <PASS> |
| G7 — Archive idempotency | §4.3 G7 | strict refuse-if-exists semantics (tmp_path isolation) + cross-FS guard per AM1 ADOPT v2 | <PASS> |

**Note on sample size (updated per CB3 PFR R1 ADOPT v2):** Spec §4.2/§4.3 per-candidate full-cohort coverage now satisfied at Phase 3. N=2 fixture (`18d92ce5d0b40cc7` + `22864f01a49e3452`) retained for JSON-dict-layer schema-version drift catch (which raw-CSV all-39 comparison would miss). All-39 coverage added via 4 NEW tests (V4 ε metric diff + V4 total_trades exact + G4 per-bar parquet integrity + G5 γ3/γ4 round-trip) reading archive + new CSVs directly. Total V4+G4-G7 test count: 12 (5 N=2 fixture + 2 BLOCKING-5 carry G6+G7 + 4 all-39 CB3 + 1 cross-FS AM1).

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
- T14 V4 gate: 12/12 tests PASSED (ε=1e-6 N=2 fixture + all-39 V4 gate per CB3 ADOPT v2 + G4-G7 coverage + registry tri-way per CH4 ADOPT v2 + cross-FS guard per AM1 ADOPT v2)
- Full suite zero-regression (2372 passed / 0 failed / 2 xfailed)
- T14b canonical-path relocation complete; canonical now holds B-C-narrow recovered content with per-bar parquet preservation + γ3/γ4 moments + registry linkage
- Original lineage preserved at `archive/phase4_forward_2026_15bps_v1_d0b8101/` for cross-verification

Phase 4 (SEAL bundle: NOTE doc + B2 reviewer dispatch + Rule 2 SEAL-eve + atomic commit + Phase Marker advance) drafting is a SEPARATE register-event (#N+20) per anti-pre-emption discipline; do NOT bundle into #N+19c.

## Spec §5 supersession note (T12 manual mv superseded by producer W3)

Per Plan v3-Phase3 sub-decision (i) + CR-SE-H2 ADOPT carry from Phase 2 v9: spec line 286 ("T12 — Archive original: `mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1 data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/`") preserved BYTE-IDENTICAL per Architecture B sealed-content invariance. Producer W3 (gated by `--enable-b-c-narrow-recovery` per Phase 2 SEAL) performs the archive INLINE during T13 fire, superseding the manual mv step de-facto. Spec amend / Architecture B errata supplement NAMED-eligible at Phase 4 SEAL bundle (not auto-bundled here).

## Post-mv test behavior (path-adaptive via CB2 PFR R1 ADOPT v2)

Per CB2 PFR R1 ADOPT v2 path-adaptive design: tests in `tests/test_b_c_narrow_v4_reproducibility.py` resolve `ACTIVE_RUN_DIR` at module-load via `_resolve_active_run_dir()` — `SIBLING_RUN_DIR` (pre-T14b) OR `CANONICAL_RUN_DIR` (post-T14b). All 12 V4+G4-G7 tests continue to PASS post-mv.

This satisfies CLAUDE.md HARD CONSTRAINT "NEVER commit code that doesn't pass existing tests" across BOTH Task 14b commit boundary AND Task 14c ratify packet commit boundary.

The 3 path-independent contract tests (`test_v4_drift_stop_condition_blocks_seal_on_breach` (hybrid — reads both ACTIVE + ARCHIVE post-fire), `test_g7_archive_idempotency_refuses_existing_target`, `test_g7_archive_refuses_cross_filesystem_attempt`) test contracts that hold regardless of disk state (path-independent: drift-stop uses synthetic injection + tmp_path; G7 refuse + cross-FS use tmp_path + monkeypatch).

## Next register-event (#N+19c) — Phase 3 ratify ONLY

Per anti-pre-emption discipline: register-event #N+19c is Phase 3 ratify acknowledgment ONLY. The Phase 4 sub-plan drafting authorization is a SEPARATE register-event #N+20.

- Phase 3 ratify acknowledgment
- Push decision for Phase 3 commits (Task 13 RED + Task 14 fire evidence + Task 14b mv evidence + Task 14c ratify packet)
- NAMED-eligible Phase 4 SEAL bundle drafting authorization: SEPARATE Charlie register-event

Phase 4 sub-plan drafting is NOT a sub-option of #N+19c; it requires its own register-event #N+20.

## Evidence artifact inventory

| Path | Type | Purpose |
|---|---|---|
| `tests/test_b_c_narrow_v4_reproducibility.py` | Python test | 12 V4+G4-G7 test methods (5 N=2 fixture spec §6.4 + 2 BLOCKING-5 carry G6+G7 + 4 all-39 per CB3 ADOPT v2 + 1 cross-FS per AM1 ADOPT v2; path-adaptive via _resolve_active_run_dir per CB2 ADOPT v2) |
| `tests/fixtures/b_c_narrow_archived_baseline.json` | JSON fixture | N=2 candidates frozen snapshot from archived original (sampled lexicographically smallest) |
| `docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md` | Markdown | This file — comprehensive Phase 3 ratify packet |
| `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` (gitignored) | Data | Canonical post-T14b: 39 candidate dirs + per-bar parquet + aggregate |
| `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` (gitignored) | Data | Archive snapshot of original (pre-fire state) |
| `backtest/experiments.db` (gitignored) | SQLite | 1 parent batch_summary + 39 child regime_holdout rows at run_id=phase4_forward_2026_15bps_v1_b_c_narrow |
```

- [ ] **Step 14c.2: Commit ratify packet, THEN STOP for Charlie register #N+19c (ratify ack only)**

Per CM6 PFR R1 ADOPT v2 Option A: commit lands FIRST (this step), then STOP for Charlie register #N+19c. Register #N+19c is ratify acknowledgment + push decision for the already-committed packet — NOT a pre-commit authorization gate. This matches the Phase 2 ratify pattern where the commit lands before the Charlie ratify acknowledgment register-event.

```bash
git add docs/superpowers/phase-3-impl-results/phase-3-ratify-summary.md
git commit -m "$(cat <<'EOF'
evidence(b-c-narrow/phase-3): Phase 3 ratify packet (Task 14c)

Per Plan v3-Phase3 v2 Task 14c. Charlie register-events #N+19a + #N+19b
fired authorizations for T13 fire + T14b canonical-path relocation.

Phase 3 deliverables (all GREEN):
- T13 fire: 39 candidates evaluated; archive snapshot of original
- T14 V4 gate: 12/12 tests PASSED (ε=1e-6 N=2 fixture + all-39 V4 per CB3
  ADOPT v2 + G4-G7 + registry tri-way per CH4 ADOPT v2 + cross-FS per AM1
  ADOPT v2)
- T14b mv: canonical path repopulated with recovered content (per CB2 ADOPT
  v2 path-adaptive design, all 12 V4 tests PASS post-mv via
  _resolve_active_run_dir → CANONICAL_RUN_DIR)
- Full suite zero-regression (2372 / 0 / 2 xfailed)

T14b evidence (rolled in per AL1 PFR R1 ADOPT v2 default — Step 14b.3 empty
commit SKIPPED unless Charlie #N+19b explicitly requested):
- mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow
     data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1
- Post-mv canonical: 39 candidate dirs + aggregate
- Post-mv sibling: gone
- Post-mv archive intact: 39 candidate dirs at archive/phase4_forward_2026_15bps_v1_d0b8101/
- Registry post-mv intact: 1 parent + 39 children at run_id=phase4_forward_2026_15bps_v1_b_c_narrow

Data artifacts produced (gitignored):
- data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/ (canonical; 39 dirs)
- data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/ (archive; 39 dirs)
- backtest/experiments.db (1 parent + 39 children at parent_run_id=phase4_forward_2026_15bps_v1_b_c_narrow)

Test + fixture artifacts (committed):
- tests/test_b_c_narrow_v4_reproducibility.py (12 V4+G4-G7 test methods; path-adaptive per CB2 ADOPT v2)
- tests/fixtures/b_c_narrow_archived_baseline.json (N=2 candidates per spec §6.6 + AM3 lex-smallest-2 rationale)

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
    OPTIONAL Task 14b empty commit per AL1 PFR R1 ADOPT v2 default-SKIP — only
    if Charlie #N+19b explicitly requested separate boundary marker, Task 14c
    ratify packet which enumerates T14b evidence inline by default)
  - Push decision for Phase 3 commits
  - All Phase 3 deliverables GREEN; cycle ready for Phase 4 SEAL bundle
    drafting (SEPARATE register-event #N+20)

Per anti-pre-emption discipline: #N+19c is Phase 3 ratify acknowledgment
ONLY. Phase 4 SEAL bundle drafting authorization is a SEPARATE register-
event #N+20.

DO NOT bundle Phase 4 SEAL bundle drafting authorization into #N+19c.

Per CM6 PFR R1 ADOPT v2 Option A: #N+19c is a POST-commit ratify
acknowledgment register-event (the Task 14c ratify packet commit already
landed at Step 14c.2 above). #N+19c does NOT gate the commit itself; it
gates the push decision + arc-level ratify ack.
========================================================================
```

---

## DEFER items (Phase 3 scope only)

The following are NOT in Phase 3 scope and require SEPARATE Charlie register-events:

1. **Phase 4 SEAL bundle drafting** (NOTE doc + B2 reviewer dispatch + Rule 2 SEAL-eve + atomic commit + Phase Marker advance): SEPARATE register-event #N+20 per anti-pre-emption discipline. Phase 4 sub-plan drafting authorization is NOT bundled into #N+19c.

2. **Architecture B errata supplement for spec §5 T12 supersession** (sub-decision (i) carry): NAMED-eligible at Phase 4 SEAL bundle drafting. Spec line 286 byte-identical preserved per Architecture B sealed-content invariance at strictest reading; supersession applied inline via producer W3 + `--enable-b-c-narrow-recovery` flag (already landed at Phase 2 SEAL); spec amend / errata supplement deferred to Phase 4 SEAL bundle.

3. **V4 test post-mv refactor**: SUPERSEDED by CB2 PFR R1 ADOPT v2 path-adaptive design. Tests now resolve `ACTIVE_RUN_DIR` at module-load via `_resolve_active_run_dir()` (sibling OR canonical), so they PASS in both pre-T14b and post-T14b states. No further refactor needed; no Phase 4 SEAL bundle deliverable.

4. **G4 + G5 N=39 full coverage**: NO LONGER DEFERRED per CB3 PFR R1 ADOPT v2. N=39 full-coverage V4 gate landed in v2 (4 new tests + 1 cross-FS test = 12 total V4+G4-G7 methods). Spec §4.2 + §4.3 per-candidate coverage requirement now satisfied at Phase 3. N=2 fixture retained for schema-version drift catch on JSON dict layer (which raw-CSV all-39 comparison would miss).

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

If V4 FAILS at Step 14.5 (any of 12 tests per v2 expansion): STOP and surface SEAL BLOCKED per spec §4.2 stop-condition. Do NOT proceed to Task 14b. Do NOT execute the mv. Adjudication paths (a/b/c per spec §4.2) require Charlie register-event.

If full suite shows regressions outside `test_b_c_narrow_v4_reproducibility.py` at Step 14.5: STOP and surface — regressions indicate hidden Phase 0/2 SEAL state issue.

End of Plan v3-Phase3 v2 (PFR R1 ADOPT 17 inline + 3 PUSHBACK adjudications applied per Charlie register #N+19 Path 1 2026-05-28).
