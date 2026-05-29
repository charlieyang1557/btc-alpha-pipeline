# B-C-narrow Data-Recovery Cycle — SEAL Note

**Cycle:** B-C-narrow data-recovery successor cycle — recover per-bar return series + per-candidate γ3/γ4 moments + registry linkage for the `phase4_forward_2026_15bps_v1` cohort_a (39 candidates), to satisfy the **R6.1 V_SEAL §10 binding precondition** and unblock post-V_SEAL Tier 6 evaluation application.

**SEAL status:** SEALED (DRAFT pending Phase 4 B2 re-review + Rule-2 SEAL-eve + Charlie atomic-SEAL register).

**Path framing:** Approach D' (producer-edit + minimum bounded engine extension); PV3-SPLIT-BY-PHASE (5 phase-specific sub-plans, each with its own PFR + per-phase ratify + task-level SEAL; Phase Marker advance reserved for THIS arc-level Phase 4 closeout).

**HARD CONSTRAINT compliance anchors:** CLAUDE.md execution convention (signal@close / execute@next-open; effective cost model) untouched; data-integrity rules honored (the original `phase4_forward_2026_15bps_v1` is preserved byte-identical in the committed archive snapshot + git history `7c8f4a7`; no forward-fill/interpolation; reconcile.py untouched); CLAUDE.md "NEVER commit code that doesn't pass existing tests" satisfied at every RED/GREEN boundary (full-suite zero-regression).

**Discipline anchors:** B2 standing rule (2-leg Codex + advisor) LOCKED 2026-05-19, reaffirmed at cumulative scale; 3-layer safety architecture (advisor self-discount + Codex cross-model + orchestrator Mode-A re-verification) operational; anti-pre-emption (only Charlie register authorizes operational fires); Rule-2 SEAL-eve adversarial OPERATIONALLY REQUIRED (re-vindicated this cycle).

---

## §0 — Cycle metadata + Charlie register chain

All dates UTC. Cycle entry → Phase 3 re-fire SEAL spanned 2026-05-26 → 2026-05-29.

| # | Register (Charlie) | Decision class |
|---|---|---|
| N1 | B-C-narrow data-recovery cycle entry (Approach D' + PV3-SPLIT-BY-PHASE) 2026-05-26 | Cycle entry |
| #N+1 | Phase 1 ratify | Phase sign-off |
| #N+2 → #N+18 | Phase 0/1/2 drafting + PFR + EXEC + task-level SEALs | Sub-phase execution |
| #N+19 → #N+19′′′′′′′ | Phase 3 plan v1→v8 PFR R1–R5 + SEAL-eve R1–R2 + re-SEAL | Phase 3 plan SEAL |
| #N+19a / #N+19b / #N+19c | Phase 3 FIRST fire (T13 + V4 GREEN) → reverted | Operational fire (reverted) |
| Option A | revert-to-pre-fire + patch-plan + re-fire 2026-05-29 | Recovery / re-plan |
| Q1=(a), Q2=(a), Option A (archive-binding) | re-fire patch adjudications 2026-05-29 | Design adjudication |
| #N+19a′ / #N+19b′ / #N+19c′ | Phase 3 RE-fire (T13 + V4 GREEN + zero-regression) + ratify ack | Operational fire (committed) |
| #N+20 | Phase 4 cycle SEAL (Path A) — this note | Arc-level closeout |

**Orchestrator-adjudication-error instances this cycle:** see §9 (Codex V2 hallucination caught by Layer-3 at Phase-3 re-review; advisor own-anchoring discounted per standing discipline).

---

## §1 — Substantive scope

**Driver:** R6.1 V_SEAL §10 binding precondition. The original `phase4_forward_2026_15bps_v1` cohort_a artifact (39 candidates) was produced WITHOUT per-bar return series, per-candidate γ3/γ4 (skew/kurtosis) moments, or experiment-registry linkage — which forced 4-of-7 R6.1 §8 Tier-6 dimensions to INDETERMINATE-on-data-unavailability and blocked Tier 6 evaluation application.

**In scope:** re-run the 39 cohort_a candidates against the forward_2026 window with (a) per-bar return series persisted (39 `returns_per_bar.parquet`), (b) per-candidate γ3/γ4 + `T_obs` computed and stored, (c) experiment-registry linkage (1 parent `batch_summary` + 39 child `regime_holdout` rows), (d) ε=1e-6 reproducibility vs the original verified, (e) the original preserved.

**Out of scope (anti-pre-emption preserved):** the Tier 6 evaluation application itself (next eligible-not-named successor); any methodology re-lock; cohort changes; cost-anchor changes. No spec amendment beyond the data-recovery design spec.

---

## §2 — Contract locks (execution outcomes)

| Contract / decision | Lock | SEAL site |
|---|---|---|
| Cycle architecture | Approach D' (producer-edit + minimum engine extension) | Charlie register N1 |
| Plan split | PV3-SPLIT-BY-PHASE (5 sub-plans, per-phase PFR+SEAL) | Charlie register 2026-05-26 |
| LineageContext construction | pattern (b) engine-internal from producer-passed scalars; `cost_anchor_id` DERIVED in `__post_init__` (NOT a signature kwarg) | Phase 0 |
| Engine extension | `RegimeHoldoutResult.equity_curve` (12th field) + 4 LC-b kwargs (`run_id_override`, `source_batch_id`, `parent_run_id_override`, `artifact_dir`, all default None) + atomic write-then-registry sequencing | Phase 0 `f112599` |
| Producer wiring | `--enable-b-c-narrow-recovery` + `--force-rerun-existing` (mutex with `--dry-run`); R9 split PRE-flight guard / POST-fire parent-only finalizer; W0 identity guard / W3 archive / W4 finalize | Phase 2 |
| Re-fire patch (Q1) | t1_4 A3/A4/A5 byte-identity rescoped to the **archived original** vs `7c8f4a7` | Phase 3 v9.1 |
| Re-fire patch (Q2) | canonical eval-gate dir stays **git-tracked** → commit recovered canonical + archive (3-leg adjudication: Codex a/0.8 + orchestrator a + advisor c → a) | Phase 3 v9.1 |
| Re-fire patch (Option A) | archive-binding = `git show 7c8f4a7:<canonical>` vs archive **on-disk** (no commit-SHA placeholder) | Phase 3 v9.1 |

---

## §3 — Engineering deliverables by phase

| Phase | SEAL commit | Adversarial rounds | Test delta | Substantive content |
|---|---|---|---|---|
| **0 Engine extension** | `f112599` | PFR R1–R4 (R4 convergent) | +13 (TestBCNarrowPhase0EngineExtension); pc9 2191→2204 | `RegimeHoldoutResult.equity_curve`; 4 LC-b kwargs; atomic write-then-registry; `_compute_sha256_file` + `_resolve_canonical_parquet_path` helpers; fail-closed preflight scalar validation. 6 Codex BLOCKINGs absorbed; 5 NOTE-deferred to Phase 2/3. |
| **1 Pre-impl gates** | `b10ffb2` | PFR R1–R2 | observation only (no code) | G1 engine-diff audit (4-category framework; 0 NUMERICAL-PATH → ε=1e-6 achievable); G2 StrategyDSL backward-compat (N=39, 100% validate); G3 raw_payloads inventory (998 symlinks resolve, target-confined); G3.5 equity_curve smoke (pre-satisfied by Phase 0). |
| **2 Producer TDD** | `0a54f65` (impl `86f75ff`) | PFR R1–R11 + SEAL-eve | +26 producer tests; pc9 2204→2236; T1.4 AST-classifier maintenance | `--enable-b-c-narrow-recovery` + `--force-rerun-existing`; R9 split (PRE-flight read-only guard + POST-fire parent-only finalizer; 39 children written by engine); W0 identity guard; W3 idempotent archive (refuse-if-exists + same-FS guard); `_CSV_FIELDS` ext (γ3/γ4/T_obs/returns_per_bar_path/sha256); LC-b threading + γ3/γ4 merge into inline per-candidate JSON. |
| **3 Fire / data-recovery** | `9d54b6b` | PFR R1–R5 + SEAL-eve R1–R2 + (re-fire) B2 re-review + Rule-2 SEAL-eve | +12 V4 tests; pc9 2236→2248 | T13 fire (39 candidates) + T14 V4 reproducibility gate + T14b canonical relocation. FIRST fire executed + reverted (Option A) after 3 sealed-plan defects surfaced; v9/v9.1 re-fire errata; RE-fire executed clean. See §5–§8. |

---

## §4 — Validation results

- **V4 reproducibility gate: 12/12 PASSED** (both fire attempts) — ε=1e-6 per-candidate metric diff + total_trades exact + per-bar parquet integrity + γ3/γ4 round-trip + G6 registry parent-child + G7 archive idempotency/cross-FS. The recovered cohort reproduces the original within ε=1e-6.
- **Relocated full-suite zero-regression gate (Step 14b.2.8): 2372 passed, 2 xfailed, 0 failed, 0 errors** (Mode-A `pytest -q`, HEAD `9d54b6b`-descended). Satisfies CLAUDE.md "NEVER commit code that doesn't pass existing tests".
- **Recovery aggregate (deterministic across both fire attempts):** 39 candidates, 20 holdout_passed / 19 holdout_failed / **0 holdout_error**.
- **Cumulative adversarial dispatches this cycle:** Phase 0 (4 PFR) + Phase 1 (2 PFR) + Phase 2 (11 PFR + SEAL-eve) + Phase 3 (5 PFR + 2 SEAL-eve + 2-leg re-review + Rule-2 SEAL-eve) — B2 2-leg (Codex + advisor) throughout. **0 verified orchestrator hallucinations** (Layer-3 Mode-A discipline); 1 Codex reviewer hallucination caught (§9).

---

## §5 — Recovered canonical data artifact + per-bar return series

The recovered cohort is committed at `ff0c576` under `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/`: 39 per-candidate `holdout_summary.json` (now carrying γ3/γ4/T_obs/returns_per_bar_path/sha256 + `run_id=phase4_forward_2026_15bps_v1_b_c_narrow`) + 39 NEW `returns_per_bar.parquet` (per-bar return series, the primary recovery target) + aggregate `holdout_summary.json` + `holdout_results.csv`. The engine writes the per-bar artifact BEFORE the registry row (Phase 0 atomic sequencing), so each registry row references the just-written parquet path/sha/T_obs.

## §6 — γ3/γ4 moment computation + registry linkage

Per-candidate γ3 (skew) / γ4 (kurtosis) + `T_obs` (finite-return count via `np.isfinite`, excluding the leading-NaN bar) computed by the engine and merged into the inline per-candidate JSON by the producer. Registry linkage (`backtest/experiments.db`, gitignored): 1 parent `batch_summary` row at `run_id=phase4_forward_2026_15bps_v1_b_c_narrow` (engine_commit `eb1c87f`, 8 strategy-specific fields NULL at parent per spec §3.2.3) + 39 child `regime_holdout` rows at that `parent_run_id` (written by the engine inside `run_regime_holdout`).

## §7 — Archive snapshot of pre-fire original

The producer W3 step (`shutil.move`) relocated the pre-fire canonical to `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/`, committed at `6d4bb7f` (41 files, **byte-identical to `7c8f4a7`** — verified). The original is therefore preserved in two places: the committed archive AND git history. `test_t1_4_backward_compat.py` A3/A4/A5 byte-identity is rescoped (Q1=a + Option A) to verify the archive vs `7c8f4a7` (`git show 7c8f4a7:<canonical>` vs archive on-disk); A1/A6/A2 unchanged (validate the recovered canonical's evaluation-semantics, which pass — the validator never reads `run_id`/γ3/γ4/T_obs/parquet).

## §8 — Re-fire / zero-regression verification (Gaps 1/2/2b)

The FIRST fire (v8 plan) executed GREEN (V4 12/12) but the Step 14.5 full-suite gate surfaced **3 sealed-plan defects**: **Gap 1** — the canonical eval-gate dir is git-TRACKED (the entire `data/phase2c_evaluation_gate/` tree, 10,366 files / 45 dirs, is tracked), not gitignored as the plan assumed → the fire deletes/mutates 41 tracked files + breaks t1_4 byte-identity; **Gap 2** — the V4 file's +12 tests break the t1_4 pc9 baseline gate (2236→2248); **Gap 2b** — Step 13.3 ran the V4 file in isolation → missed Gap 2. Per Charlie register **Option A**, the fire was reverted to the green SEAL tree `b96d3a8` (canonical restored; 40 registry rows deleted; RED commit reverted `bccbc47`), the plan was patched (v9 re-fire errata `cb59a55` → B2 re-review both APPROVE/SOUND → v9.1 polish `0025afd` → Rule-2 SEAL-eve CLEAR → re-SEAL `38e1291`), and the RE-fire executed clean through the corrected §V9.4 sequence (RED `5e77e63` → fire → V4 12/12 → fixture `9cabc9b` → mv → archive commit `6d4bb7f` → t1_4 rescope + canonical commit `ff0c576` → relocated full-suite gate **2372 GREEN** → ratify `9d54b6b`). A **DESIGN INVARIANT** was codified: t1_4's `_per_candidate_dirs()` runs at pytest *collection* time, so no full-suite may run while the canonical is absent — the zero-regression gate was relocated to post-mv (Step 14b.2.8).

---

## §9 — Finding-class observations (NAME-only; eligible-not-named for §36 codification)

Per anti-pre-emption, the following §-candidates from this cycle are queued NAME-only here; codification into `docs/discipline/METHODOLOGY_NOTES.md` (next free top-level = **§36** container "Cross-cycle findings codified at B-C-narrow cycle SEAL boundary") is a SEPARATE downstream Charlie register-event (codification cycle, B2-standing-rule SEAL-class discipline), NOT this SEAL commit:

1. **Line-citation-drift → quoted-text-anchor invariant** — an edit-catalogue citing plan-body line numbers drifts with every insert (the v9 errata's own §V9.9 insert re-drifted the v9.1 numbers); durable fix = quoted-text / table-row locators, not line numbers. (Extends `feedback_invariant_level_vs_enumeration`.)
2. **Collection-time crash discovery** — a parametrize decorator that reads a filesystem path crashes the *whole* pytest collection when that path is transiently absent; gates must be sequenced around the absence window.
3. **3-leg design adjudication** (Codex + orchestrator + advisor) where the advisor's own verified fact undercut its directional lean → convergence to the other option.
4. **Reviewer-hallucination caught by Layer-3** — a Codex finding (claimed wrong test-file path) was a hallucination; orchestrator grep-verification (citation discipline) refuted it (PUSHBACK).
5. **Rule-2 SEAL-eve re-vindication** — the SEAL-eve adversarial round again caught defects (the v8 SEAL-eve R1 architectural BLOCKINGs) that standard PFR rounds + static review missed.
6. **Execution-time-discovery → revert → patch → re-fire pattern** — a sealed plan's factual error (canonical git-tracking) surfaced only at execution; the disciplined response is revert-to-green + B2-reviewed errata + re-SEAL + re-fire, not in-place salvage.

## §10 — Orchestrator-adjudication-error recurrence

| # | Finding | Cycle phase | Caught by |
|---|---|---|---|
| 1 | Codex V2 hallucinated a `tests/backtest/test_v4_evaluation_gate.py` reference that does not exist in the plan | Phase 3 v9 re-review | orchestrator Layer-3 grep (PUSHBACK; no action) |

(Advisor own-anchoring at implementation-review iteration class discounted per standing discipline `feedback_advisor_own_anchoring_implementation_review`; 0 verified orchestrator hallucinations.)

## §11 — Eligible-not-named successors (NOT bound)

- **post-V_SEAL Tier 6 evaluation application** — NOW UNBLOCKED (the B-C-narrow binding precondition is satisfied: per-bar series + γ3/γ4 + registry linkage recovered + V4-verified + committed). Next eligible-not-named successor under the R6.1 Path α invariant.
- **§36 METHODOLOGY_NOTES codification batch** (the §9 candidates) — eligible at a separate codification register-event.
- All other carry-forward backlog (B-C-extended SEAL bundle components, R6.1/R5.x memory codification, RW/WY framework reopen, paper-trading deployment, etc.) remains eligible at separate Charlie register-events per anti-pre-emption.

---

## §12 — V_SEAL closure

- **§12.1 Register-event verbatim:** (Charlie #N+20 atomic-SEAL register text to be recorded at the SEAL commit.)
- **§12.2 Charlie register chain:** see §0 (cycle entry N1 → Phase 0/1/2/3 sub-phase registers → Option A re-plan → #N+19a′/b′/c′ re-fire → #N+20 cycle SEAL).
- **§12.3 Locked substantive content recap:** see §2 (contract locks) + §5–§8 (deliverables).
- **§12.4 Bundle + Option 1A atomic binding:** the SEAL commit atomically stages the NOTE + CLAUDE.md Phase Marker advance + `docs/phase_marker_history.md` (Option 1A binding; the **20th cumulative trigger**). Arc-level closeout → MAY carry an arc-level git tag (precedent: `phase4-forward-test-v1`, `phase5-diagnostic-execution-v1`; tag text at Charlie/orchestrator discretion).
- **§12.5 Artifact signature:**
  - Path: `docs/phase5/B_C_NARROW_DATA_RECOVERY_NOTE.md`
  - Cycle: B-C-narrow data-recovery (R6.1 V_SEAL §10 binding precondition)
  - Sealed by: Charlie register #N+20 (Phase 4 atomic SEAL)
  - Cycle entry: Charlie register N1 2026-05-26
  - Cycle SEAL ratify: 2026-05-29 (pending Phase 4 B2 re-review + Rule-2 SEAL-eve)
  - Phase seal commits: Phase 0 `f112599` / Phase 1 `b10ffb2` / Phase 2 `0a54f65` / Phase 3 `9d54b6b`
  - Re-fire commit chain: `cb59a55` → `0025afd` → `38e1291` → `5e77e63` → `9cabc9b` → `6d4bb7f` → `ff0c576` → `9d54b6b`
  - Adversarial round count (cycle): Phase 0 R1–R4 + Phase 1 R1–R2 + Phase 2 R1–R11+SEAL-eve + Phase 3 R1–R5 + SEAL-eve R1–R2 + re-fire B2 + Rule-2 SEAL-eve
  - Rule-2 SEAL-eve vindication: re-vindicated this cycle (Phase 3 v8 SEAL-eve R1 caught 2 architectural BLOCKINGs missed by 5 PFR rounds)
  - Cycle saturation: reached (Phase 3 re-review B2 LOW-floor + Rule-2 SEAL-eve CLEAR)

**End of SEAL artifact.**
