# PHASE2C_15 Step 2 sub-spec: operational pipeline specification

**Status:** WORKING DRAFT (sealing fires at sub-spec SEAL register-event boundary post reviewer pass cycle).

**Cycle scope:** specifies how PHASE2C_15 fire executes against the locked PLAN §1 parameters. Implementation arc Step 2 deliverable per Q-S126 framework-fire alignment audit (Step 1) findings + Q-S127 (C) hybrid disposition (audit findings preserved as §1 preface; operational specs at §2+). Z4 minimal-governance-surface discipline binding.

## §1 Step 1 audit findings preface (compact)

Step 1 framework-fire alignment audit completed at 11 verification target scope. Empirical mechanism: sweep-grep + targeted reads across `agents/` + `backtest/` + `scripts/`; pure read-only.

**Classification outcome:** 7 (α) FULLY ALIGNED + 4 (β) MINOR GAPS + 0 (γ) substantive code modification + 0 (δ) PLAN §1.3 conceptual revisit.

**Headline:** framework PHASE2C_15-fire-ready at code register. All gaps are operational-specification-only, addressed at §2+.

| Target | Classification | Gap if (β) |
|---|---|---|
| CG-1 valid_N/success_count/observed_rate provenance | (β) | Not framework primitives; derivable via documented multi-script pipeline; specified at §2.1 |
| CG-2 invalid terminal pre-vs-post AND-gate | (α) | — Only `PENDING_BACKTEST` lifecycle proceeds to evaluation; invalid states drop pre-evaluation at ingest |
| CG-3 PHASE2C_12 8/197 baseline provenance | (β) | Comparison artifact NOT persisted; reconstructed at §3.1 |
| CG-4 AND-gate centralization | (α) | — Single canonical impl at `backtest/engine.py:_evaluate_regime_holdout_pass` line 1367 |
| CG-5 FFH/Fisher inputs reconstructibility | (β) | K-batch partitioning needs explicit aggregation logic; specified at §3.3 |
| Adv-a theme rotation 5-theme exclusion | (α) | — `THEME_CYCLE_LEN` env-var-driven default=5 excludes mfc by construction |
| Adv-b sample-size N_per_batch=200 | (α) | — `STAGE2D_BATCH_SIZE` env-var-driven default=200 |
| Adv-c stopping rule absence | (α) statistical / (β) operational sub | Catastrophic-stop policy specified at §3.2 |
| Adv-d cost tracking | (α) | — `BudgetLedger` SQLite with per-call write_pending → finalize |
| Adv-e determinism | (α) | — Framework treats fire as one-shot; per-call response.txt persisted |
| Adv-f output artifact structure | (β) | K=5 × 4 regimes naming convention specified at §3.4 |

Anchor commits referenced: HEAD `8bc7de3`; PHASE2C_15 PLAN sealed at `df08fa5`; PHASE2C_12 closeout at `1989c85`+ chain; canonical AND-gate at `backtest/engine.py:1367` (`_evaluate_regime_holdout_pass`); canonical AND-gate cohort logic at `scripts/compare_multi_regime.py:317` (`_build_cohort_categorization`).

## §2 Operational pipeline specification

### §2.1 Canonical execution graph

PHASE2C_15 fire executes the following sequence per K=5 batches:

1. **Generation (per batch):** `python -m agents.proposer.stage2d_batch [--with-critic --live-critic]` with env vars locked at PLAN §1.1+§1.2:
   - `PHASE2C_BATCH_SIZE=200` (default; explicit set for clarity)
   - `PHASE2C_THEME_CYCLE_LEN=5` (default; excludes `multi_factor_combination`)
   - No `PHASE2C_SMOKE_THEME_OVERRIDE` (5-theme uniform rotation)
   - Produces: `raw_payloads/batch_{batch_id}/stage2d_summary.json` + per-call `attempt_NNNN_response.txt` + per-candidate registry rows with `lifecycle_state`
   - 5 invocations total → 5 distinct uuid-based `batch_id`s
2. **Evaluation (per regime, cross-batch):** `python -m scripts.run_phase2c_evaluation_gate` invoked once per regime over the **merged post-ingest valid population across the 5 batches** (per C1 register-precision; nominal 1000 attempted ≠ valid_N; valid_N = `lifecycle_state == PENDING_BACKTEST` count post-ingest):
   - Regimes: `bear_2022`, `validation_2024`, `eval_2020_v1`, `eval_2021_v1` (per PHASE2C_12 baseline 4-regime set)
   - 4 invocations total → 4 unfiltered evaluation directories
3. **Filter tier (per regime):** `python -m scripts.filter_evaluation_gate` per regime to produce filtered tier dirs (precondition for `compare_multi_regime.py`)
   - 4 invocations total → 4 filtered evaluation directories
4. **Cross-regime comparison (single):** `python -m scripts.compare_multi_regime` over merged 4-regime universe:
   - 1 invocation → cross-batch aggregate `comparison_summary.json` + `comparison_matrix.csv` containing per-candidate `holdout_{label}_passed` booleans + `pass_count_unfiltered`
   - `cohort_a_cardinality_unfiltered` = total `success_count` (Role 1 numerator)
5. **Per-batch partitioning (Role 2 input):** post-hoc partitioning of `comparison_matrix.csv` rows by `hypothesis_hash` → `batch_id` mapping (resolved from 5 `stage2d_summary.json` files); produces K=5 per-batch `(success_k, valid_N_k - success_k)` tuples for K×2 contingency table
6. **Statistical computation (Role 1 + Role 2):**
   - Role 1 success criterion: `observed_rate = success_count / valid_N`; success iff `observed_rate > 0.0207` per PLAN §1.3
   - Role 1 auxiliary: 2-sided Fisher exact at α=0.05 vs PHASE2C_12 baseline (8, 197) per PLAN §1.4
   - Role 2 omnibus: Fisher-Freeman-Halton on K×2 contingency (exact if tractable; Monte Carlo B=10000 fallback) per PLAN §1.5
   - Role 2 supplementary: pairwise Fisher exact (10 pairs at K=5) descriptive only per PLAN §1.5
7. **Closeout artifact assembly:** results consolidated at `docs/closeout/PHASE2C_15_RESULTS.md` (canonical naming TBD per anti-pre-naming option (ii)).

### §2.2 valid_N / success_count / observed_rate provenance (CG-1 closure)

Per PLAN §1.3 verbatim binding:
- `valid_N` = candidates with `lifecycle_state == PENDING_BACKTEST` (ingested + valid DSL + non-duplicate + non-rejected_complexity + non-empty); summed across K=5 batches
- `success_count` = `cohort_a_cardinality_unfiltered` from `compare_multi_regime.py` over 4 regimes (= candidates passing `regime_holdout_passed=True` in **all 4 regimes**)
- `observed_rate` = `success_count / valid_N`

Per-batch versions (Role 2 input): `valid_N_k` = batch k's PENDING_BACKTEST count; `success_count_k` = `cohort_a_cardinality_unfiltered ∩ batch k's hypothesis_hashes`.

## §3 Decisions per audit findings

### §3.1 PHASE2C_12 comparison artifact reconstruction (Observation 1 ADOPT)

Reconstruct PHASE2C_12 comparison artifact at canonical location `data/phase2c_evaluation_gate/comparison_phase2c_12_v1/` per Observation 1 lean (ii) empirical reconstruction.

**Procedure (Step 2 implementation arc activity register; pre-PHASE2C_15-fire):**
1. Verify presence of 4 PHASE2C_12 unfiltered tier dirs at `data/phase2c_evaluation_gate/phase2c_12_{audit,audit_2024,eval_2020,eval_2021}_v1/` (audit confirmed).
2. Generate PHASE2C_12 filtered tier dirs (if absent) via `filter_evaluation_gate.py` per regime — 4 invocations producing `phase2c_12_*_v1_filtered/` dirs.
3. Run `compare_multi_regime.py` over 4 PHASE2C_12 unfiltered + filtered tier dirs → emit `comparison_phase2c_12_v1/{comparison_summary.json, comparison_matrix.csv}`.
4. Verify (per Obs 2 extended HARD STOP at byte-level on two registers): (i) `cohort_a_cardinality_unfiltered == 8` AND `n_candidates == 197` at byte-level match to PHASE2C_12 closeout `docs/closeout/PHASE2C_12_RESULTS.md:111` cite (§3.2 register), AND (ii) per-regime unfiltered pass counts `== (28, 82, 65, 43)` at byte-level match to PHASE2C_12 closeout §3.1 cite (`bear_2022 / validation_2024 / eval_2020 / eval_2021`). Both must pass for verification clear; either failure = HARD STOP requiring adjudication before PHASE2C_15 fire (per C4 no-tolerance + Obs 2 per-regime mask-drift closure).
5. Persist comparison artifact + commit at canonical location.

PHASE2C_15 PLAN §1.4 Fisher exact comparison consumes this canonical artifact at byte-level rather than prose-only citation, closing apples-to-apples register-precision question.

**Retroactive-authority clarification (C6 ADOPT)**: the reconstructed PHASE2C_12 comparison artifact is reference-only and does not retroactively alter PHASE2C_12 canonical closeout claims. PHASE2C_12_RESULTS.md remains the canonical authority on PHASE2C_12 results; the reconstructed artifact serves byte-level reproducibility of PHASE2C_15 PLAN §1.4 comparison input.

### §3.2 Catastrophic-stop policy (Observation 2 ADOPT lean (α) strict inclusion)

If a `stage2d_batch` catastrophic stop fires mid-batch in PHASE2C_15 (parse-rate gate / single-mode failure / cardinality violation / cumulative spend cap):

- Truncated batch counts toward `valid_N` at observed truncated `valid_N_k` (= count of `PENDING_BACKTEST` lifecycle states up to `truncated_at` index)
- `success_count_k` over observed truncated cohort
- **No re-fire** on catastrophic stop; truncated batch is included in PHASE2C_15 cohort as-fired
- Truncated batch is **K-counted** (counts as one of the K=5 batches)

**No replacement batch is generated for a catastrophically stopped batch** (C2 ADOPT). The K=5 batch count is fixed at PLAN §1.1; truncation does not authorize a 6th compensating batch. This closes the loophole at register-precision where future reinterpretation might argue for replacement-batch generation as "non-mutating because K stays 5 for the originally-fired register" or similar gaming.

Rationale: anti-rationalization discipline at §3.4 violation-index sub-mode (i) pre-completion exclusion + sub-mode (ii) post-completion exclusion. Catastrophic stop = framework's accurate signal that empirical conditions don't allow the planned fire; respecting the signal at empirical register honors anti-rationalization discipline. Re-fire would be a stop-condition-conditional decision, opening selective-interpretation gaming vector.

If truncation happens at `k=1` (parse-rate gate fires at first 5 calls): `valid_N_k` may be 0 or near-zero for that batch. Role 2 K×2 contingency includes the truncated row at empirical state. Role 1 numerator + denominator both reflect truncation.

### §3.3 K-batch partitioning convention (CG-5 closure)

Lean: **single merged-universe evaluation + post-hoc per-batch partitioning** (audit CG-5 option (iii) at closeout-register aggregation):

1. Run evaluation gate ONCE per regime over merged 1000-candidate universe (4 invocations total per §2.1 step 2)
2. Run `compare_multi_regime.py` ONCE over merged 4-regime universe (1 invocation per §2.1 step 4)
3. Partition `comparison_matrix.csv` rows by `hypothesis_hash` → `batch_id` mapping: lookup table built from 5 `stage2d_summary.json` files reading per-call `lifecycle_state` + `hypothesis_hash` fields
4. Produce 5 per-batch `(success_count_k, valid_N_k)` tuples → K×2 contingency table

Operational simplicity vs alternative options:
- (i) 5× compare runs per batch: more invocations, 5 separate comparison artifacts (artifact sprawl)
- (ii) Modify `compare_multi_regime.py` to partition by batch_id: code modification → (γ) gap class (audit found zero (γ); preserving zero-γ classification favors no-code-change option)
- (iii) Closeout-register aggregation [SELECTED]: 4 evaluation + 1 comparison invocations + post-hoc partitioning script

Partitioning script lives at closeout-register; not framework-resident.

**Pre-fire universe symmetry verification (Obs 3 ADOPT)**: before invoking `compare_multi_regime.py`, verify all 4 per-regime evaluation outputs contain the merged post-ingest valid population at `hypothesis_hash` parity. Universe symmetry assertion at `compare_multi_regime.py:494` enforces this at runtime; pre-fire verification by reading each per-regime `holdout_results.csv` row count + cross-checking `hypothesis_hash` set membership across the 4 regimes. Parity failure = substantive evidence of evaluation-stage drift (e.g., one regime had evaluation failure on some candidates) requiring adjudication before comparison fires.

**Partitioning observational invariant (C3 ADOPT)**: per-batch partitioning is observational only and does NOT alter the merged-universe Role 1 computation. Role 1 numerator (`success_count`) and denominator (`valid_N`) are computed over the merged-universe at `compare_multi_regime.py` output register-class; per-batch partitioning at closeout-register-class produces Role 2 K×2 contingency input only. Role 1 ↔ Role 2 register separation crisp; future reinterpretation cannot mutate Role 1 computation by partitioning operations.

### §3.4 Naming convention (Adv-f closure)

| Artifact class | Path convention |
|---|---|
| Generation per-batch | `raw_payloads/batch_{uuid}/` (5 distinct uuids; uuid-based per `stage2d_batch.py:947`) |
| Per-regime evaluation merged | `data/phase2c_evaluation_gate/phase2c_15_{regime_label}_v1/` (4 dirs total: bear_2022, audit_2024, eval_2020, eval_2021) |
| Per-regime filtered tier | `data/phase2c_evaluation_gate/phase2c_15_{regime_label}_v1_filtered/` (4 dirs total) |
| Cross-regime comparison | `data/phase2c_evaluation_gate/comparison_phase2c_15_v1/` (single dir; merged 4-regime cross-batch comparison) |
| PHASE2C_12 reconstructed comparison | `data/phase2c_evaluation_gate/comparison_phase2c_12_v1/` (per §3.1; pre-PHASE2C_15-fire activity) |
| Per-batch partitioning output | `data/phase2c_evaluation_gate/comparison_phase2c_15_v1/per_batch_partition.json` (post-hoc partitioning artifact; K×2 contingency input) |

Per-batch evaluation-gate scoped naming (`phase2c_15_b{1..5}_*`) NOT used per §3.3 selected lean (single merged evaluation; no per-batch evaluation invocation). If future cycle needs per-batch evaluation, naming can extend.

### §3.5 Engine lineage compliance (audit §3 #6 closure)

All PHASE2C_15 evaluation invocations consume corrected-engine artifacts only per CLAUDE.md "Hard rule for any future WF-consuming work":
- `backtest.wf_lineage.check_wf_semantics_or_raise()` fires at WF-consuming sites
- `backtest.wf_lineage.check_evaluation_semantics_or_raise()` fires at single-run holdout consumption sites (per PHASE2C_6 attestation domain `single_run_holdout_v1` precedent)

These guards are embedded in `compute_simplified_dsr` via RS-3 patch at PHASE2C_11; PHASE2C_15 evaluation pipeline inherits the discipline through `run_phase2c_evaluation_gate.py` → `run_regime_holdout` → engine code path at `engine_commit=eb1c87f` / `wf-corrected-v1` tag.

**V-2 verification result (fired at Step 2 register per Obs 4 ADOPT)**: `git log eb1c87f..HEAD -- backtest/` enumerated **1 commit**:
- `08e1488` "feat(phase2c-12-step8): GREEN auth #6.y — eligible-subset (197, 139) parallel-structure pair" — adds `PHASE2C_12_N_ELIGIBLE_OBSERVED = 139` constant + `ALLOWED_DUAL_GATE_PAIRS` extension + docstring updates at `backtest/evaluate_dsr.py`

**Classification per C5 metadata-vs-semantic distinction**:
- In `backtest/evaluate_dsr.py` register-class: **semantic-affecting** (extends dual-gate allowlist for `compute_simplified_dsr` API entry; new accepted `(n_trials, n_input)` pairs)
- In **PHASE2C_15-relevant call chain register-class**: **NOT in the call path**. PHASE2C_15 evaluation pipeline = `backtest/engine.py` regime evaluation + `scripts/run_phase2c_evaluation_gate.py` + `scripts/compare_multi_regime.py`. `backtest/evaluate_dsr.py` is the simplified-DSR-screen used at PHASE2C_11 Step 3 (statistical-significance-machinery register-class), register-class-distinct from cross-regime AND-gate cohort path.

**Classification outcome**: **(V-2-clean) at PHASE2C_15-relevant scope**. Zero semantic-affecting mutations between `eb1c87f` (corrected-engine commit) and HEAD `8bc7de3` in PHASE2C_15 evaluation call chain.

**Forward-binding rule (C5 ADOPT)**: if subsequent commits between Step 2 SEAL and PHASE2C_15 fire mutate `backtest/engine.py` regime evaluation logic OR `scripts/run_phase2c_evaluation_gate.py` OR `scripts/compare_multi_regime.py` → audit-of-mutations adjudication required before fire-prep authorization. Doc/comment-only mutations at any path: no escalation. Mutations at `backtest/evaluate_dsr.py` outside PHASE2C_15 call chain: no escalation per V-2 register-class-distinct scope precedent.

### §3.6 Fire-time stop-conditions + critic mode disposition

Per PLAN §1.1 Fixed N pre-committed semantics at statistical register: no interim analysis at α=0.05; no early-stopping by observed_rate. Catastrophic-stop policy per §3.2 applies at operational register only.

**Critic mode disposition (post-V-1 verification at Step 2 register; state-α confirmed per Obs 1 ADOPT)**: PHASE2C_15 fires **WITHOUT critic mode** (no `--with-critic --live-critic`). Measurement parity with PHASE2C_12 baseline (8, 197) preserved at register-precision per V-1 verification finding: critic verdict is observational metadata at proposer-side; AND-gate evaluation operates on `lifecycle_state == PENDING_BACKTEST` cohort regardless of critic verdict.

**State-α / state-β / state-γ framing** (per Obs 1 substantive decomposition; preserved at register-precision for forward reference):
- **state-α**: critic observational only; parity preserved without critic mode at PHASE2C_15 — **CONFIRMED**
- **state-β**: critic cohort-gating; parity would require critic mode — REJECTED at empirical register
- **state-γ**: critic upstream cohort mutation; deeper semantic divergence — REJECTED at empirical register

**V-1 verification trace** (read-only forensic at Step 2 register):
- `scripts/run_phase2c_evaluation_gate.py:139-204` — `_load_corrected_candidates` reads `walk_forward_results.csv` rows; `_resolve_candidate_universe` applies `--universe primary|audit` (WF Sharpe filter or all candidates); zero critic-aware filtering logic
- `scripts/compare_multi_regime.py` — reads `holdout_*_passed` boolean from per-candidate JSONs; zero critic-aware logic
- `scripts/run_phase2c_batch_walkforward.py` — zero critic-aware logic
- `agents.orchestrator.ingest` lifecycle states: `PENDING_BACKTEST`, `INVALID_DSL`, `REJECTED_COMPLEXITY`, `DUPLICATE`, `BACKEND_EMPTY_OUTPUT`. **No `CRITIC_REJECTED` / `CRITIC_APPROVED` state**. Critic verdict attaches as `critic_result_dict` metadata to per-call records at `stage2d_batch.py:1239+`, NEVER mutating `lifecycle_state`

**P-3 prerequisite resolution**: V-1 fired pre-SEAL per Obs 1+4 ADOPT; state-α confirmed; CONTRACT GAP closed. PHASE2C_15 budget calculus K=5 × ~$2-3 ≈ **$10-15 fits within `STAGE2D_CUMULATIVE_CAP_USD=$30`** ceiling with comfortable margin. No budget-cap-raise required; no critic mode required.

## §4 Cycle-scope binding (pointers)

- PHASE2C_14 sub-spec [`PHASE2C_14_PLAN.md`](PHASE2C_14_PLAN.md) §3.1-§3.4 framework class continues to bind through PHASE2C_15 fire register-event boundary
- PHASE2C_15 sub-spec [`PHASE2C_15_PLAN.md`](PHASE2C_15_PLAN.md) §1 parameter values continue to bind (immutable post-PLAN-SEAL)
- Sealed corpus invariance per PHASE2C_15 entry scoping decision §6.4 (METHODOLOGY_NOTES §27/§28/§29 + PHASE2C_13 sub-spec §2.7/§4.3 + §20.6 §A2 instances #26-#31 not modified)
- Anti-pre-naming option (ii) preserved: implementation arc Step 3+ scope NOT pre-committed at this register; adjudicates at register-class-distinct register-event boundaries within arc

## §5 Anchors

- HEAD at WORKING DRAFT register: `8bc7de3` (post Phase Marker advance at PHASE2C_15 sub-spec drafting cycle SEAL)
- PHASE2C_15 sub-spec PLAN SEAL: `df08fa5` ([`PHASE2C_15_PLAN.md`](PHASE2C_15_PLAN.md), 63 lines)
- PHASE2C_15 entry scoping decision SEAL: `14183e6` ([`PHASE2C_15_SCOPING_DECISION.md`](PHASE2C_15_SCOPING_DECISION.md), 31 lines)
- PHASE2C_14 sub-spec SEAL: `18fa2a1` ([`PHASE2C_14_PLAN.md`](PHASE2C_14_PLAN.md), 352 lines)
- METHODOLOGY_NOTES.md: 6785 lines invariant per H-1 (d) preservation
- Step 1 audit transcript register: this conversation register at Q-S126 ENDORSE → audit-completion register-event boundary; findings preserved at §1 preface
- Canonical AND-gate impl: [`backtest/engine.py:1367`](../../backtest/engine.py) `_evaluate_regime_holdout_pass`
- Canonical cohort logic: [`scripts/compare_multi_regime.py:317`](../../scripts/compare_multi_regime.py) `_build_cohort_categorization`
- PHASE2C_12 closeout 8/197 cite: [`docs/closeout/PHASE2C_12_RESULTS.md:111`](../closeout/PHASE2C_12_RESULTS.md)

---

**End of Step 2 sub-spec WORKING DRAFT.**
