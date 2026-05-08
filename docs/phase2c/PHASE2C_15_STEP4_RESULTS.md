# PHASE2C_15 Implementation Arc Step 4 — Smoke Pipeline Rehearsal Results

**Status:** WORKING DRAFT — Step 4 deliverable authored under Q-S147 Charlie register authorization; reviewer pass cycle + Codex utility-script pass pending before final SEAL bundle authorization.

**Cycle scope:** Path 3 per Q-S136 (A) Charlie register authorization — PHASE2C_15 smoke pipeline rehearsal at K=2 × N=50 = 100 universe register over 7-step canonical execution graph per Step 2 sub-spec [`PHASE2C_15_STEP2_PLAN.md`](PHASE2C_15_STEP2_PLAN.md) §2.1. Operational rehearsal of statistical machinery + framework + pipeline + discipline architecture under first-time-fire conditions; SUSPENDED INTERPRETATION discipline preserved throughout per Q-S136 framing (smoke is rehearsal; main fire is measurement; smoke results do NOT inform main fire pre-registered claim).

---

## §1 Cycle activity summary — Q-S136 → Q-S147 register-event boundary chain

**13 Charlie register authorization boundaries** at Step 4 cycle internal + SEAL cycle entry combined (Q-S136 → Q-S147 inclusive of fractional Q-S139.5 §19 instance #1 resolution boundary):

| Boundary | Disposition | Convergence pattern | Substantive scope |
|---|---|---|---|
| Q-S136 | Path 3 smoke fire | Direct convergence | Smoke pipeline rehearsal at suspended interpretation register-class |
| Q-S137 | smoke-γ K=2 × N=50 | Direct convergence | Universe sizing for rehearsal-coverage rationale |
| Q-S138 | (go-A) generation only | Per-fix engagement (advisor refined from go-B) | Generation-step scoping over full pipeline at single Q-S boundary |
| Q-S139 | (eval-A) full pipeline through step 6 | Direct convergence | Evaluation-step scoping over full pipeline through statistical computation |
| Q-S139.5 | (prereq-B) WF as register-class-distinct | Direct convergence | §19 instance #1 resolution (WF backtest dependency surfacing) |
| Q-S140 | (go-WF-seq-α) sequential canonical naming | Direct convergence | WF backtest sequencing + canonical artifact naming |
| Q-S141 | (mb-b) synthetic merged batch | Per-fix engagement (advisor refined from mb-c) | §19 instance #2 resolution (multi-batch_id eval gate gap) |
| Q-S142 | (eg-seq-staged) per-regime checkpoint | Per-fix engagement (advisor refined from eg-seq) | Per-regime evaluation gate firing with staged checkpoints |
| Q-S143 | (filter-seq-bundled) sequential + bundled | Direct convergence | Filter tier × 4 regimes operational |
| Q-S144 | (comp-fire) single-shot | Direct convergence | Cross-regime comparison single-shot fire |
| Q-S145 | (stat-bundled) single bundle | Direct convergence | Per-batch partitioning + Role 1/Role 2 statistics in single utility |
| Q-S146 | (seal-B) pacing pause | Direct convergence | Pacing-discipline pause before Step 4 SEAL cycle |
| Q-S147 | Step 4 SEAL cycle entry; Codex routing (β) | Per-fix engagement (Claude Code refined from (α) to (β)) | Convergence-after-divergence at Q-S sub-question register-class |

3 reviewer divergence resolutions all at substantive register at Step 4 cycle internal (Q-S138 + Q-S141 + Q-S142); 4th convergence-after-divergence instance fired at Q-S147 sub-question 2 (Codex routing) at Step 4 SEAL cycle entry. Per-fix engagement caught register-imprecision at advisor + Claude Code register; convergence emerged post engagement. Pattern operating as designed per `feedback_reviewer_suggestion_adjudication.md`.

---

## §2 Substantive smoke results at SUSPENDED INTERPRETATION (per Q-S136 framing)

**Discipline anchor (load-bearing):** Smoke fire results are operational rehearsal of statistical machinery, NOT pre-registered measurement against PHASE2C_14 sub-spec §3.2 Wilson CI 2.07% strict-exceedance threshold. The pre-registered Role 1 success criterion applies to **main fire register-class only** (K=5 × N=200 = 1000). Smoke results do **NOT** inform main fire pre-registered claim per Q-S136 suspended interpretation discipline. This framing is cited verbatim at `data/phase2c_evaluation_gate/comparison_phase2c_15_smoke_v1/statistical_summary.json` `interpretation_register` + `interpretation_note` fields.

**Cohort A (4-of-4 cross-regime AND-gate survivors):**

| Metric | Value | Interpretation |
|---|---|---|
| `cohort_a_unfiltered` | 2 / 100 = **0.0200** (2.00%) | REHEARSAL — not pre-registered |
| `cohort_a_filtered` | 2 / 100 = **0.0200** (2.00%) | (same 2 survivors after filter) |
| Pre-registered threshold | 0.0207 (2.07%) | binds to main fire register-class only |
| Role 1 strict-exceedance | False (smoke 0.0200 < 0.0207) | rehearsal; suspended |

**Survivor hashes:** `1a09fba35b3b48bb` + `5bc3697383b11d6c` (one per smoke batch).

**Role 1 auxiliary Fisher exact 2-sided vs PHASE2C_12 baseline (8, 197):**

| Field | Value |
|---|---|
| Contingency table | `[[8, 189], [2, 98]]` |
| Odds ratio | 2.0741 |
| p-value (2-sided) | 0.5038 |
| Interpretation | descriptive only — smoke not pre-registered; not significant at α=0.05 |

**Role 2 omnibus FFH at K=2 (collapses to single 2×2 Fisher exact mathematically):**

| Field | Value |
|---|---|
| K | 2 |
| Contingency table | `[[1, 49], [1, 49]]` |
| Odds ratio | 1.0000 |
| p-value (2-sided) | 1.0000 |
| Interpretation | rehearsal — no batch-level heterogeneity |

**Pass-count distribution `{0, 1, 2, 3, 4}` (unfiltered):** `{28, 33, 25, 12, 2}` — sum = 100 ✓.

**Per-regime pass rates (unfiltered, n=100 per regime):**

| Regime | Passed | Schema | In-sample caveat |
|---|---|---|---|
| bear_2022 | 18 | `phase2c_7_1` | False |
| validation_2024 | 47 | `phase2c_7_1` | False |
| eval_2020_v1 | 45 | `phase2c_8_1` | True |
| eval_2021_v1 | 17 | `phase2c_8_1` | True |

**In-sample caveat stratification (per `comparison_summary.json`):**
- Fully out-of-sample regimes (bear_2022 + validation_2024): **8 candidates** passing both
- Train-overlap regimes (eval_2020_v1 + eval_2021_v1): **11 candidates** passing both

**Suspended-interpretation register reaffirmation:** Smoke 2.00% < pre-registered 2.07% threshold is observational at smoke register-class only; does NOT inform main fire register-class pre-registered claim. Main fire is the measurement-class register-event boundary where the pre-registered Role 1 success criterion applies; smoke is the rehearsal-class register-event boundary where statistical machinery is operationally validated. Per advisor Q-S145 Observation 2 framing: "smoke is rehearsal; main fire is measurement; smoke result does NOT inform main fire pre-registered claim."

---

## §3 §19 spec-vs-empirical-reality instance enumeration (Step 4 cycle internal)

Two §19 instances surfaced + operationally resolved at Step 4 cycle internal:

**§19 #1 — WF backtest dependency at 7-step canonical execution graph:**
- **Surface:** sub-spec [`PHASE2C_15_STEP2_PLAN.md`](PHASE2C_15_STEP2_PLAN.md) §2.1 7-step canonical execution graph enumerated generation → per-regime evaluation as adjacent steps but did not enumerate WF backtest as prerequisite step at register-precision register-class binding.
- **Empirical fire:** detected at Q-S139 advisor pre-fire register; WF backtest produces `data/phase2c_walkforward/batch_<batch_id>_corrected/walk_forward_results.csv` which is the canonical input consumed by `run_phase2c_evaluation_gate.py`; absent WF artifact dir, eval gate cannot fire.
- **Operational resolution:** Q-S139.5 (prereq-B) authorization at fresh register-event boundary; WF backtest authorized as register-class-distinct prerequisite step ahead of per-regime evaluation; sequential cadence (one batch at a time) per Q-S140 (go-WF-seq-α).
- **Carry-forward register binding:** logged to closeout deliverable §A2 register-event boundary at this Step 4 SEAL cycle.

**§19 #2 — Multi-batch_id evaluation gate gap:**
- **Surface:** `run_phase2c_evaluation_gate.py` is single-batch-source by construction (consumes single `data/phase2c_walkforward/batch_<batch_id>_corrected/` dir); sub-spec specified merged-universe evaluation register-class at K=2 smoke + K=5 main fire.
- **Empirical fire:** detected at Q-S140 forward-binding analysis; specification mismatch surfaced at register-precision when 2-batch evaluation pattern needed canonical artifact directory to drive single eval gate invocation per regime.
- **Operational resolution:** Q-S141 (mb-b) authorization for synthetic merged batch directory pattern at canonical paths `data/phase2c_walkforward/batch_phase2c_15_smoke_combined_corrected/` + `raw_payloads/batch_phase2c_15_smoke_combined/` (symlink-based composition); utility script `scripts/build_phase2c_15_smoke_synthetic_batch.py` encodes mechanism (CSV concatenation + position renumbering + symlink construction + lineage parity guard). See §6 for substantive code register documentation.
- **Carry-forward register binding:** logged to closeout deliverable §A2 register-event boundary at this Step 4 SEAL cycle; mechanism transfers to main fire register-class as K=5 variant.

Both §19 instances surfaced at empirical fire register, NOT at sub-spec drafting register; per-fix engagement at advisor pre-fire register caught the gaps before pipeline state corruption. Pattern matches §19 catch-class register-precedent at PHASE2C_12/13 cycles per [METHODOLOGY_NOTES](../discipline/METHODOLOGY_NOTES.md) §19.

---

## §4 Lineage parity — single canonical engine_commit across all artifacts

**Engine lineage anchor (load-bearing):** single canonical `engine_commit = eb1c87f` (`wf-corrected-v1` tag) preserved across all PHASE2C_15 smoke artifacts at register-precision; (V-2-clean) at PHASE2C_15-relevant scope from Step 2 §3.5 forward-binding rule continues to bind through this Step 4 SEAL register-event boundary.

| Artifact | `corrected_wf_semantics_commit` | `wf_semantics` | `lineage_check` |
|---|---|---|---|
| `batch_4c9634cd-..._corrected/walk_forward_summary.json` | `eb1c87f` | `corrected_test_boundary_v1` | `passed` |
| `batch_49682edb-..._corrected/walk_forward_summary.json` | `eb1c87f` | `corrected_test_boundary_v1` | `passed` |
| `batch_phase2c_15_smoke_combined_corrected/walk_forward_summary.json` | `eb1c87f` | `corrected_test_boundary_v1` | `passed` |

**Schema versions per producer-code identity:**

| Regime | `schema_version` | Producer code identity |
|---|---|---|
| bear_2022, validation_2024 | `phase2c_7_1` | PHASE2C_7.1 multi-regime evaluation gate consumer |
| eval_2020_v1, eval_2021_v1 | `phase2c_8_1` | PHASE2C_8.1 train-overlap regime consumer |
| `comparison_summary.json` | `comparison_schema_v2` | `compare_multi_regime.py` n-way generalization |
| `per_batch_partition.json` | `phase2c_15_smoke_partition_v1` | new closeout utility script (this cycle) |
| `statistical_summary.json` | `phase2c_15_smoke_statistical_v1` | new closeout utility script (this cycle) |

Schema versioning per producer-code identity register at register-class match register binding scope to PHASE2C_8.1 register-precedent; new closeout utility schemas explicitly versioned with `phase2c_15_smoke_*_v1` suffix at smoke register-class binding to preserve cycle-scoped framing (main fire variants will be register-class-distinct).

**Pre-Step-4-SEAL engine drift check:** HEAD = `25380e2` (UNCHANGED since Step 3 SEAL bundle); `git log eb1c87f..HEAD -- backtest/engine.py scripts/run_phase2c_evaluation_gate.py scripts/compare_multi_regime.py` empirically clean at Step 2 §3.5 forward-binding scope; no engine drift requiring audit-of-mutations adjudication.

---

## §5 Forensic checkpoint summary — 7-step canonical execution graph

12 forensic checkpoint logs persisted at `logs/phase2c_15_smoke/` providing per-segment + bundled forensic audit trail across the empirical pipeline (canonical 7-step execution graph augmented at runtime by 2 §19-inserted prerequisite segments — WF backtest at §19 #1 resolution + synthetic merged batch at §19 #2 resolution; canonical graph segments shown in parentheses below):

| Sequence | Operation | Log files | Outcome |
|---|---|---|---|
| 1 (canonical Step 1) | Generation × 2 batches (N=50 each) | `smoke_batch_{1,2}_*.log` | clean; ~$1.10 API spend |
| 2 (§19 #1 prerequisite) | WF backtest × 2 batches (sequential) | `wf_batch_{1,2}_*.log` | clean; lineage_check=passed both |
| 3 (§19 #2 prerequisite) | Synthetic merged batch setup | `synthetic_batch_setup_*.log` | clean; 7-fold forensic verification all PASS |
| 4 (canonical Step 2) | Per-regime evaluation × 4 (sequential) | `eval_gate_{bear_2022,validation_2024,eval_2020,eval_2021}_*.log` | clean; per-regime checkpoint at Q-S142 (eg-seq-staged) |
| 5 (canonical Step 3) | Filter tier × 4 regimes (bundled) | `filter_tier_*.log` | clean; threshold pinned `MIN_TOTAL_TRADES = 20` |
| 6 (canonical Step 4) | Cross-regime comparison (single-shot) | `compare_multi_regime_*.log` | clean; `n_candidates=100` |
| 7 (canonical Steps 5+6) | Per-batch partitioning + statistics (bundled) | `partitioning_stats_*.log` | clean; 9-criterion bundled forensic check ALL PASS (9/9) |

Per-step + bundled forensic checkpoint discipline per Step 2 sub-spec §2.1 step-completion rule. Q-S142 per-regime checkpoint pattern (advisor refinement from naive sequential) caught register-imprecisions early at per-regime register; pattern transfers to main fire register-class as 4-regime checkpoint.

---

## §6 Closeout utility scripts — substantive code register documentation

Two closeout-register-class utility scripts authored at this Step 4 cycle internal at canonical paths under `scripts/`. Both encode operational mechanism transferring to main fire register-class via main-fire variant derivation. Smoke-naming preserved at file-name register binding to cycle-scoped framing.

**`scripts/build_phase2c_15_smoke_synthetic_batch.py` (527 lines post-Codex-patch)** — §19 instance #2 operational resolution:
- Concatenates `walk_forward_results.csv` from K source batches with position renumbering; preserves original `batch_id` per row at canonical CSV schema register; validates CSV header equality across sources + per-source position contiguity 1..N + global non-empty `hypothesis_hash` uniqueness across merged rows (raises `ValueError` on duplicate)
- Synthesizes `walk_forward_summary.json` aggregating compile/runtime status + sharpe distribution from concatenated CSV; lineage parity guard across source summaries (raises `ValueError` on divergence at `corrected_wf_semantics_commit`/`wf_semantics`/`lineage_check`/`git_sha`/`current_git_sha`/`phase1_success_threshold`); validates source summary `batch_id` matches expected + source `total_candidates == len(rows)`; guards `len(sharpe_values) >= 2` for stdev/quantile computation; derives binary success criterion from validated `phase1_success_threshold` field rather than hardcoded value
- Symlinks `attempt_NNNN_response.txt` files (eval gate consumes these only) at synthetic raw_payloads dir — symlinks **only CSV-backed positions** (not all attempt files in source dir; per Codex C1 catch-class for main-fire transfer at non-aligned source dirs); **relative-path symlinks** for repo portability (per Codex C2)
- Symlinks source `stage2d_summary.json` files at synthetic raw_payloads dir as `source_stage2d_summary_<full_batch_id>.json` for forensic traceability (full UUID; not 8-char prefix; per Codex C2 prefix-collision avoidance)
- K-agnostic exhaustive forensic verification: CSV row count vs expected total; position contiguity 1..N; `batch_id` preservation per row (per-source counts vs `src_csv_positions`); **exhaustive** symlink resolution at all CSV-backed positions (not spot-check; per Codex C1); total symlink count vs expected total; summary JSON parseable + key fields validated; explicit `RuntimeError` on any drift at audit register (no `assert` data-validation per Codex C6 to survive `python -O`)
- Mechanism transfers to main fire variant: K=5 × N=200 = 1000 universe; main fire variant is register-class-distinct file path (e.g., `build_phase2c_15_main_fire_synthetic_batch.py`) inheriting smoke variant mechanism (CSV concat + lineage parity + symlink construction); patched smoke variant is K-agnostic at concatenation + verification register, providing cleaner baseline for main-fire derivation

**`scripts/build_phase2c_15_smoke_partitioning_stats.py` (470 lines post-Codex-patch)** — Per Q-S145 (stat-bundled) single bundled invocation:
- Output-exists guard at top of `main()`: raises `FileExistsError` if `per_batch_partition.json` or `statistical_summary.json` already exists at canonical paths (per Codex C6; prevents silent overwrite)
- Reads `comparison_matrix.csv` (smoke compare output; 100 rows); raises `RuntimeError` on empty matrix (per Codex C6 audit-friendliness register)
- Builds `hypothesis_hash → batch_id` lookup from K source `stage2d_summary.json` files (symlinked at synthetic raw_payloads dir); detects duplicate hashes across source summaries (raises `RuntimeError` reporting both batch IDs per Codex C3); validates non-duplicate hashes within `comparison_matrix.csv` itself; raises `RuntimeError` on any unmapped row reporting first 5 unmapped hashes
- **Explicit K=2 smoke guard**: raises `NotImplementedError` if `len(batch_ids) != 2` (per Codex C4); main-fire K=5 variant requires register-class-distinct script with FFH r×c omnibus implementation per PLAN §1.5 framework
- Partitions by `batch_id` into K=2 contingency table at `valid_N`/`cohort_a_unfiltered`/`cohort_a_filtered` per batch
- Role 1 strict-exceedance: `observed_rate` vs PLAN §1.3 threshold 0.0207 (suspended at smoke per Q-S136 framing); `exceeds_threshold = False` interpreted as "rehearsal — not pre-registered"
- Role 1 auxiliary Fisher exact 2-sided vs PHASE2C_12 baseline `(8, 197)` via `scipy.stats.fisher_exact` over `[[8, 189], [2, 98]]` contingency; output JSON includes `contingency_table_row_labels` + `odds_ratio_orientation` field disambiguating OR semantics (table-row-0-over-table-row-1 = PHASE2C_12 odds relative to PHASE2C_15 smoke; per Codex non-blocking observation #1 to prevent downstream consumer misreporting)
- Role 2 omnibus FFH at K=2 collapses to single 2×2 Fisher exact via `scipy.stats.fisher_exact` over per-batch contingency `[[s_1, n_1-s_1], [s_2, n_2-s_2]]`; mathematical equivalence cited at output JSON (`table_dimensions_note`); transfers to K=5 main fire as 5×2 contingency — main fire variant implementation register (FFH r×c exact via scipy capability vs Monte Carlo fallback) surfaces at main fire authorization register-event boundary per PLAN §1.5 framework
- 9-criterion bundled forensic check: hash coverage 100/100; batch split 50/50; success totals match comparison_summary; Role 1 math reproducible (`rate = cohort_a / N`); Role 1 auxiliary Fisher exact valid; Role 2 K×2 contingency consistent; Role 2 FFH valid; output artifacts written; suspended interpretation cited at output schema
- Output: `per_batch_partition.json` + `statistical_summary.json` at canonical paths under `data/phase2c_evaluation_gate/comparison_phase2c_15_smoke_v1/`
- Mechanism transfers to main fire variant: K=5 × 5×2 contingency + 10-pair supplementary Fisher exact (K choose 2 = 10) per Q-S145 forward-binding observation

Both scripts are cycle-scoped at smoke register-class (NOT framework-resident); main fire variants at register-class-distinct paths will substantively derive from these. Codex routing at Q-S147 sub-question 2 (β) authorized adversarial pass at code register-class scope on these 2 scripts; deliverable MD itself routed at process/spec register-class via ChatGPT structural overlay + Claude advisor full-prose-access.

**Codex pass outcome:** PASS WITH PATCHES; 7 findings + 2 non-blocking observations surfaced. **All 8 ACCEPT patches landed at register-precision per per-fix adjudication discipline** (no bulk-accept; per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md)) post Charlie register ENDORSE on convergence at scope option (A): C1 (CSV-backed symlink construction) + C2 (relative symlinks + full batch IDs) + C3 (duplicate hash detection at both scripts) + C4 (explicit K=2 smoke guard with `NotImplementedError`) + C5 (multi-item validation: CSV header equality + position contiguity + lineage parity expansion + total_candidates check) + C6 PARTIAL (data-validation `assert` → explicit `ValueError`/`RuntimeError`; preserve internal sanity asserts; output-exists guard at script 2) + C7 (stdev N≥2 guard + `phase1_success_threshold` parameterization) + non-blocking #1 (OR orientation metadata field at output JSON). Non-blocking #2 (sorted-symlink ordering) NO-PATCH disposition per per-fix engagement (rows carry batch IDs explicitly; not correctness bug). Total post-patch line count: 997 (script 1: 327→527; script 2: 386→470); growth justified at substantive register-precision per Codex finding correspondence.

---

## §7 Methodology observations (carry-forward register)

Substantive methodology observations from Step 4 cycle internal at register-class match register binding scope to [METHODOLOGY_NOTES](../discipline/METHODOLOGY_NOTES.md) §16-§29 codification convention. Forward-only logging per H-1 (b) preservation; observations carry forward to next methodology consolidation cycle adjudication boundary.

**Observation 1 — Per-fix adjudication discipline operating at Q-S sub-question register-class:** Q-S147 sub-question 2 (Codex routing) demonstrated per-fix adjudication discipline operates at multi-part Q-S register-class as well as Q-S primary disposition register-class. Pattern transfers cleanly: reviewer divergence at sub-question → per-fix engagement at substantive register → convergence emerges post engagement. Mechanism functioning as register-precision-correction at advisor + Claude Code register. Carry-forward observation per advisor Q-S147 framing.

**Observation 2 — Convergence-after-divergence pattern: 6 cumulative instances at PHASE2C_15 Step 4:** Q-S138 (advisor refined go-B → go-A) + Q-S141 (advisor refined mb-c → mb-b) + Q-S142 (advisor refined eg-seq → eg-seq-staged) + Q-S147 sub-question 2 (Claude Code refined α → β post advisor 5-argument substantive engagement) + deliverable reviewer pass C3 vs A1 (cross-reviewer divergence at 12-vs-13 boundary count resolved at advisor A1 per empirical table-row verification) + Codex pass scope adjudication (advisor + ChatGPT + Claude Code converged at (A) all-patches-before-SEAL post substantive engagement on (B) faster-SEAL alternative). Pattern operating across reviewer register-classes (advisor + Claude Code + ChatGPT + Codex) per `feedback_reviewer_suggestion_adjudication.md` per-fix discipline (no bulk-accept; engage substantive arguments; refine position when stronger). Carry-forward register binding for next methodology consolidation cycle Strong-tier promotion adjudication per [METHODOLOGY_NOTES §20.6](../discipline/METHODOLOGY_NOTES.md) bar criteria framework.

**Observation 3 — §19 instance handling pattern operating at register-precision:** §19 #1 (WF dependency) + §19 #2 (multi-batch_id eval gate gap) both surfaced at empirical fire register at Step 4 cycle internal, NOT at sub-spec drafting register. Per-fix engagement at advisor pre-fire register caught the gaps before pipeline state corruption. Pattern matches PHASE2C_12/13 cycle-internal §19 catch-class precedent. Carry-forward register binding: §19 cumulative count register at PHASE2C_15 = 2 instances at Step 4 cycle internal; finalized at PHASE2C_15 closeout deliverable §6 register-event boundary per Q-S46 OPTION (a) precedent.

**Observation 4 — K-batch register-class transitions surface operational-specification gaps single-batch register cannot expose:** §19 #2 (multi-batch_id eval gate gap) surfaced because K=2 smoke pipeline rehearsal exposed `run_phase2c_evaluation_gate.py` single-batch-source assumption that K=1 PHASE2C_8.1 register-precedent framework operating at single-batch register-class did not expose. K=5 main fire would have surfaced same gap; smoke pipeline rehearsal at K=2 is the cheaper register-event boundary at which to catch K-batch gaps. Carry-forward observation: smoke pipeline rehearsal at K≥2 catches K-batch operational gaps that K=1 register cannot expose; this is the substantive value-add of multi-batch smoke rehearsal.

**Observation 5 — Suspended interpretation discipline operational throughout cycle:** Q-S136 framing preserved at sub-spec drafting register + cycle internal register + closeout utility scripts register + statistical_summary.json `interpretation_register` field + this deliverable §2 register. Discipline anchor operating end-to-end at register-precision register-class binding. Carry-forward observation: discipline anchor preservation across cycle-internal register-class transitions is a register-class-distinct catch class from §19 spec-vs-empirical-reality drift register-class.

---

## §8 Forward-binding to main fire (Q-S148+ register-event boundary)

**Main fire is register-class-distinct from smoke:** measurement-class vs rehearsal-class. Discipline anchors at main fire are stricter at register-precision register-class binding:

- **Pre-registered Role 1 success criterion** binds at main fire register-class only (smoke 2.00% < 2.07% threshold is observational at smoke register-class only; does NOT inform main fire pre-registered claim per Q-S136 framing)
- **No suspended interpretation discipline at main fire** — main fire IS the measurement-class register-event boundary the cycle has been working toward
- **Measurement-class reviewer pass cycle** at register-class match register binding to PHASE2C_12 closeout register-precedent
- **§3.4 violation-index post-fire patterns** become operationally-relevant at main fire register-event boundary (4 register-class-distinct anti-rationalization patterns: success-criterion expansion / selective batch interpretation / fire-boundary re-scoping / comparison-axis reframing); watch for these patterns at any post-fire deliverable framing per [`PHASE2C_14_PLAN.md`](PHASE2C_14_PLAN.md) §3.4

**Main fire scope estimate:**
- Universe: K=5 × N=200 = 1000 candidates (5-theme rotation per Q-S120; uniform 1/5 weighting)
- API spend: ~$11 estimated (within $30 PHASE2C_15 cumulative cap; ~$22 headroom)
- Wall time: ~4-5 hours rough operational estimate (sequential generation + WF + per-regime eval + filter + comparison + statistics; subject to API latency + Backtrader runtime variability — actual main fire wall time will calibrate empirically)
- Scope binding: PHASE2C_14 sub-spec §3.1-§3.4 framework class (immutable through fire register-event boundary per t2-t5 immutability); PHASE2C_15 PLAN §1 locked parameter values (Q-S119/120/121); Step 2 sub-spec §3.1-§3.6 substantive decisions; PHASE2C_12 comparison artifact reconstruction reference-only (canonical authority remains [`PHASE2C_12_RESULTS.md`](../closeout/PHASE2C_12_RESULTS.md))

**Q-S148+ main fire authorization** at fresh register-event boundary post-Step-4-SEAL per pacing discipline + anti-momentum-binding strict reading per `feedback_authorization_routing.md`. Charlie register authorization required at Q-S148 entry; Step 4 SEAL register-event boundary does NOT imply Q-S148 main fire authorization at successor register-event boundary.

**Substantive throughput register transition signal:** PHASE2C_15 implementation arc is approaching the substantive throughput register transition at Q-S148+ main fire authorization. 16+ governance cycles + Path 1 forensic closure + V-1/V-2 verifications + Step 4 smoke pipeline rehearsal all converged at fire-time register-class match register binding. Main fire produces the empirical AND-gate rate vs 2.07% pre-registered threshold at register-class-distinct register from prior governance cycles; different discipline anchors apply at fire-time and post-fire-evaluation register per [`PHASE2C_14_PLAN.md`](PHASE2C_14_PLAN.md) §3.4 violation-index 4-pattern register.

---

## §9 Anchors

- **Step 2 sub-spec §2.1 7-step canonical execution graph:** [`docs/phase2c/PHASE2C_15_STEP2_PLAN.md`](PHASE2C_15_STEP2_PLAN.md) sealed at `e1aba42`
- **PLAN §1 locked parameter values (Q-S119/120/121):** [`docs/phase2c/PHASE2C_15_PLAN.md`](PHASE2C_15_PLAN.md) sealed at `df08fa5`
- **Framework class (PHASE2C_14 sub-spec §3.1-§3.4):** [`docs/phase2c/PHASE2C_14_PLAN.md`](PHASE2C_14_PLAN.md) sealed at `18fa2a1`
- **PHASE2C_12 baseline (8, 197) for Role 1 auxiliary Fisher exact:** [`docs/closeout/PHASE2C_12_RESULTS.md`](../closeout/PHASE2C_12_RESULTS.md) line 111 + reconstructed canonical artifact at `data/phase2c_evaluation_gate/comparison_phase2c_12_v1/` per Step 3 SEAL
- **Engine lineage anchor:** `eb1c87f` (`wf-corrected-v1`); (V-2-clean) at PHASE2C_15-relevant scope from Step 2 §3.5 forward-binding rule
- **Authorization register at Step 4 cycle internal + SEAL cycle entry combined:** Q-S136 → Q-S147 chain (13 Charlie register authorization boundaries cumulative inclusive of fractional Q-S139.5; per-boundary explicit Charlie register authorization per [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md))
- **Reviewer pass cycle** (Step 4 SEAL cycle entry adjudication closed at convergence): ChatGPT structural overlay first-pass + Claude advisor full-prose-access pass at Q-S147 register-event boundary; triple convergence at (β) post per-fix engagement on Codex routing sub-question; Codex routing scoped to 2 utility scripts at code register-class only per `feedback_codex_review_scope.md` register-class disambiguation

---

## §A2 §19 cumulative count register at Step 4 SEAL register-event boundary

**Cumulative §19 instances at PHASE2C_15 cycle:** 2 instances at Step 4 cycle internal:

| # | Instance | Surface | Operational resolution |
|---|---|---|---|
| 1 | WF backtest dependency at 7-step canonical execution graph | Q-S139 advisor pre-fire register | Q-S139.5 (prereq-B) authorization |
| 2 | Multi-batch_id evaluation gate gap | Q-S140 forward-binding analysis | Q-S141 (mb-b) synthetic merged batch directory pattern |

Per Q-S46 sub-question 2 OPTION (a) precedent: §19 cumulative count register at PHASE2C_15 cycle finalized at PHASE2C_15 closeout deliverable §6 register-event boundary; this Step 4 SEAL register-event boundary preserves §19 instances at carry-forward register binding.

---

**End of Step 4 deliverable WORKING DRAFT.** SEAL bundle pending Q-S147 ENDORSE convergence at Charlie register binding (deliverable seal commit + 2 utility scripts at canonical paths + Phase Marker advance commit + bundled push; NO tag per Step deliverable SEAL precedent at PHASE2C_13 Step 1-11 + PHASE2C_12 Step 1-2 register precedent).
