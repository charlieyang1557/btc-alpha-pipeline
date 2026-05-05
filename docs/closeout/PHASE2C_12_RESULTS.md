# PHASE2C_12 — Breadth-Expansion Arc Closeout Results

**Status:** SEALED at this commit register.
**Tag:** Pending PHASE2C_12 SEAL marker (separate from this deliverable seal).
**Cycle anchor:** PHASE2C_12 = breadth expansion arc per scoping decision §4.4 (`541c0be`).
**Authoring authorization:** Charlie Auth #7 (ratified post-Auth #6.5 Step 8 + ZERO DRIFT verification).

This deliverable consumes the full PHASE2C_12 cycle artifact register (sub-spec
drafting cycle SEAL → Step 1 deliverable SEAL → Step 2 fire-prep deliverable
SEAL → Step 5 main batch fire → Step 6.5 WF backtest → Step 7 cross-regime
evaluation gate → Step 8 mechanical disposition fire → Auth #6.5 baseline
re-fire ZERO DRIFT) and synthesizes substantive cycle findings + methodology
accumulation + forward path recommendation per Charlie 4-stage strategic framing
adjudicated at this register.

---

## §1 Cycle objective + scope

PHASE2C_12 = **breadth expansion arc** per PHASE2C_12 scoping decision §4.4
(`541c0be`). Successor scoping cycle to PHASE2C_11 (statistical-significance
machinery) selected breadth expansion register-class over (a) structured
re-examination, (b) calibration variation, (c) Phase 3 trajectory, (d) other
paths. Sub-spec drafting cycle (`PHASE2C_12_PLAN.md` at `b8e4972`) locked
6 components C1-C6 with 25 Q-questions explicit at canonical artifact §7
LOCKED summary table.

**Cycle hypothesis (operational, not strategic):** flipping theme rotation
from PHASE2C_11's 5/6 operational themes to PHASE2C_12's 6/6 (adding
`multi_factor_combination` to operational rotation) under canonical-baseline
generation parameters produces **disjoint theme-coverage distribution**
(register-class #2 distinguishability per §6.2 Component 4) with measurable
impact on cross-regime survival rates relative to PHASE2C_11 baseline.

**Test methodology (locked at sub-spec drafting cycle):** N=197 candidate
walk-forward batch fired under uniform 6-theme rotation; 4-regime cross-regime
evaluation gate per PHASE2C_8.1 framework reuse; PHASE2C_11 simplified
DSR-style screen reused per Q21 framework reuse + Q22 LOCKED disposition logic.

**Scope boundaries:**
- IN scope: 197 candidate walk-forward fire + 4-regime evaluation + cross-regime
  AND-gate analysis + Step 8 mechanical disposition compute.
- OUT of scope (deferred to PHASE2C_13+): canonical Bailey–López de Prado DSR
  per PHASE2C_11 §4.7 deferred prerequisite; PBO; CPCV; per-trade-Sharpe
  validation; engine code-path validation across Step 7 evaluation gate
  runner versions.

---

## §2 Step 1–8 timeline + auth boundary register

PHASE2C_12 cycle accumulated **25 commits** between PHASE2C_11 SEAL (`5dba0df`)
and this deliverable seal commit. Implementation arc structured into 9 explicit
steps per sub-spec §8.1.

### §2.1 Implementation arc steps + canonical commits

| Step | Description | Canonical commit(s) | Auth boundary |
|---|---|---|---|
| Scoping decision SEAL | Breadth expansion arc designation | `541c0be` + `5abb22b` | Pre-cycle |
| Sub-spec drafting cycle SEAL | `PHASE2C_12_PLAN.md` v1 + V#7 Path A patch | `b8e4972` + `e961cc5` | Auth #1 |
| Step 1 — Q9/Q10 code surface | Theme rotation 6/6 + smoke override | `38e012e` (RED) → `d46e24f` (Q9) → `cc4c056` (Q10) → `3543fab` (Codex hotfix) → `4e112a3` (deliverable) → `cdc7048` (PM advance) | Auth #1-extended |
| Step 2 fire-prep | 3-surface coupled patch + `--live-critic` + ledger pre-charge | `af5419e` (RED) → `7c682fd` (S1) → `30d3bfd` (S2+S3) → `1f68f37` (Codex hotfix) → `4f95c7c` (deliverable) → `a6b1c1a` (PM advance) | Auth #2 |
| Step 2 smoke fire | 40 candidates (100% mfc) | (operational artifact at `raw_payloads/`) | Auth #3 |
| Step 5 main fire | 197 candidates uniform 6/6 | (batch_id `7f2f7d3e-df22-4ef7-9d7a-6f1733fe5c67`) | Auth #4 |
| Step 6 Component 4 verification | Disjoint theme-coverage distribution | (verification artifact) | Auth #5 |
| Step 6.5 WF backtest | 197 candidates corrected-engine WF | (artifacts at `data/phase2c_12_wf/_corrected/`) | Auth #5.5 |
| Step 7 evaluation gate | 4-regime cross-regime evaluation | `data/phase2c_evaluation_gate/phase2c_12_*` | Auth #5.5-extension |
| Step 8 fire-prep + Auth #6.x | `PHASE2C_12_N_RAW=197` + paired-pair allowlist | `a1d1889` (RED) → `8887651` (GREEN) → `2a5c63a` (Codex hotfix) | Auth #6.x |
| Step 8 fire-prep + Auth #6.x-extension | Cycle-conditional N_eff `{197, 80, 40, 6}` | `605dfc6` (RED) → `995fdb2` (GREEN) | Auth #6.x-extension |
| Step 8 fire-prep + Auth #6.y | Eligible-subset `(197, 139)` parallel-structure pair | `3e1ee89` (RED) → `08e1488` (GREEN) | Auth #6.y |
| Step 8 mechanical disposition fire | `compute_simplified_dsr()` over 139 eligible candidates | `_step8_result.json` (sha256 `38dbf532...`) | Auth #6 + #6.y re-confirm |
| Step 6.5 baseline re-fire | PHASE2C_11 (198, 154) at HEAD `08e1488` | `_auth_6_5_baseline_refire.json` (sha256 `9e1dc894...`) | Auth #6.5 |
| Step 9 closeout deliverable | This document | This commit | Auth #7 |

### §2.2 Auth boundary register cumulative count

PHASE2C_12 cycle issued **15 explicit Charlie auth boundaries** at fire-time
discovery + scope-expansion register: Auths #1, #1-extended, #2, #3, #4, #5,
#5.5, #5.5-extension, #5-reconfirm, #6, #6.x β1 narrow, #6.x-extension,
#6, #6.y, #6.5. Auth #7 (this deliverable seal) is the 16th boundary.
Each boundary corresponds to substantive scope decision; none are procedural
acknowledgments.

This boundary count is substantively higher than PHASE2C_10 (~6) and
PHASE2C_11 (~10) at comparable cycle stages — empirical evidence that
PHASE2C_12 cycle complexity (breadth expansion arc + 3 multi-commit code
change arcs at framework register + 4 fire-time precondition surfaces)
required higher discipline-fire rate than prior cycles at comparable
substantive scope.

---

## §3 Step 7 cross-regime AND-gate substantive findings

Step 7 evaluation gate fired 197 candidates against 4 regimes (`bear_2022`
audit_v1 / `validation_2024` audit_2024_v1 / `eval_2020_v1` / `eval_2021_v1`)
per PHASE2C_8.1 framework reuse + Q-β statistical test ratification.

### §3.1 Per-regime pass counts

| Regime | n | Passers | Pass rate |
|---|---|---|---|
| audit_v1 (bear_2022) | 197 | 28 | 14.21% |
| audit_2024_v1 (validation_2024) | 197 | 82 | 41.62% |
| eval_2020_v1 | 197 | 65 | 32.99% |
| eval_2021_v1 | 197 | 43 | 21.83% |

### §3.2 AND-gate (all 4 regimes) survivors

**8 of 197 candidates passed all 4 regimes** = 4.06% AND-gate rate.

Survivor hashes:
- `0d6140752d7a6d5c` — `triple_momentum_alignment_156` (multi_factor_combination, wf_sharpe=0.221)
- `6c819d7c52f52133` — `multi_factor_trend_strength_confirmation` (multi_factor_combination, wf_sharpe=−0.857)
- `7f31373c16fe3f7d` — `triple_ema_macd_momentum_convergence_162` (multi_factor_combination, wf_sharpe=−0.125)
- `88192bc5c256b702` — (volume_divergence, wf_sharpe=0.835)
- `0d61... + abaab255d0baa88c + be652bcdeb40a902 + c3269370da971824 + e69248b60f2a8a0c` (5 non-mfc)

### §3.3 AND-gate theme breakdown

| Theme | Total | AND-gate passers | Rate |
|---|---|---|---|
| momentum | 33 | 1 | 3.0% |
| mean_reversion | 33 | 1 | 3.0% |
| volatility_regime | 32 | 0 | 0.0% |
| volume_divergence | 33 | 2 | 6.1% |
| calendar_effect | 33 | 1 | 3.0% |
| **multi_factor_combination** | **33** | **3** | **9.1%** |

`multi_factor_combination` shows highest per-theme AND-gate rate at descriptive
register. `volatility_regime` shows zero AND-gate contribution (single-batch
observation; multi-batch evidence required to distinguish systematic theme
issue from LLM stochasticity per §9 strategy direction caveat).

### §3.4 Statistical tests per Q-β ratification

**Cross-cycle comparison (PHASE2C_12 vs PHASE2C_11 AND-gate rate):**
- PHASE2C_12: 8/197 = 4.06% (95% Wilson CI: [2.07%, 7.81%])
- PHASE2C_11: 1/198 = 0.51% (95% Wilson CI: [0.09%, 2.80%])
- 2-proportion z-test: z = 2.3681, two-tailed p = 0.0179
- Fisher exact test: odds ratio = 8.34, p = 0.0200
- Both tests at marginal-to-substantive significance (p < 0.05); concordant
  conclusion: PHASE2C_12 AND-gate rate is statistically distinguishable
  from PHASE2C_11 baseline at conventional 0.05 cutoff.

**Theme comparison (mfc vs non-mfc within PHASE2C_12):**
- mfc: 3/33 = 9.09% (95% Wilson CI: [3.14%, 23.57%])
- non-mfc: 5/164 = 3.05%
- 2-proportion z-test: z = 1.6044, p = 0.1086
- Fisher exact test: odds ratio = 3.18, p = 0.1323
- Both tests above conventional 0.05 cutoff; mfc per-theme advantage at
  descriptive register but **NOT statistically distinguishable from non-mfc
  baseline** at sample size n_mfc=33. Wide 95% Wilson CI [3.14%, 23.57%]
  reflects small-sample uncertainty; multi-batch evidence required.

### §3.5 PHASE2C_11 §4.4 audit-only inclusion register retroactive validation

PHASE2C_11 §4.4 expanded canonical evaluation cohort from primary universe
(WF Sharpe ≥ 0.5) to full audit_v1 (n=154 eligible). PHASE2C_12 8 AND-gate
survivors include **5 candidates from audit-only partition** (WF Sharpe < 0.5):
- `6c819d7c52f52133` (wf_sharpe = −0.857; AND-gate survivor despite negative WF)
- 4 additional audit-only members in 5/8 AND-gate composition

This empirically validates PHASE2C_11 §4.4 audit-only inclusion decision at
retroactive register: **5/8 = 62.5% of PHASE2C_12 cross-regime survivors
would have been excluded under primary-universe-only filter**. WF Sharpe
single-train-test boundary metric is a **specialization metric**, not a
robustness metric; cross-regime survival is the register-class-distinct
robustness metric. PHASE2C_11 §4.4 framework reuse at PHASE2C_12 surfaces
this distinction substantively.

---

## §4 Step 8 mechanical disposition fire output

Step 8 mechanical disposition fired at HEAD `08e1488` (post Auth #6.x β1
narrow + #6.x-extension + #6.y eligible-subset patches) with fire pair
`(n_trials=197, n_input=139)` per Auth #6.y eligible-subset register.

### §4.1 Canonical disposition output

| Field | Value |
|---|---|
| `n_raw` | 197 |
| `n_eligible` | 139 (post Q16 [Path A patch] T_c<5 filter) |
| `n_excluded` | 58 (low_trade_count=11, zero_trades=47) |
| `n_trials` | 197 |
| `bonferroni_threshold` | 3.250601 |
| `expected_max_sharpe_null` (Gumbel) | 2.486804 |
| `sharpe_var_used` | 0.811489 |
| `population_argmax_hash` | `38a03883db818c1e` |
| `population_argmax_sharpe` | 2.798131 |
| `population_argmax_z_score` | 0.880565 |
| `population_argmax_p_value` | 0.189277 |
| **`POPULATION_DISPOSITION`** | **`inconclusive`** |
| `bonferroni_pass` | False (sr_max 2.798 < bonf 3.251) |
| `dsr_style_pass` | False (z=0.881 → p=0.189 ≥ 0.05) |
| `criteria_agree` | True |
| `degenerate_state` | none |

### §4.2 Per-candidate disposition counts

| Disposition | Count |
|---|---|
| `artifact_evidence` | 138 |
| `inconclusive` | 1 (= argmax candidate) |
| `signal_evidence` | 0 |

### §4.3 Sensitivity table (cycle-conditional N_eff per Q15 [REVISED])

Per `_resolve_n_eff_set(n_trials=197) = (197, 80, 40, 6)`:

| n_eff | label | bonferroni_threshold | expected_max_sharpe_null | argmax_p_value | argmax_disposition |
|---|---|---|---|---|---|
| 197 | **primary** | 3.250601 | 2.486804 | 0.189277 | **inconclusive** |
| 80 | sensitivity | 2.960414 | 2.207991 | 0.047542 | inconclusive |
| 40 | sensitivity | 2.716203 | 1.972343 | 0.009754 | signal_evidence |
| 6 | sensitivity | 1.893018 | 1.171202 | 0.000002 | signal_evidence |

Sensitivity rows are **descriptive only** per PHASE2C_11_PLAN §5.4 lockpoint;
primary register disposition stays at `inconclusive`.

### §4.4 Q22 LOCKED routing applied (mechanical, no interpretive override)

Population disposition routed at primary anchor (n_eff=197) per Q22 LOCKED:
- Bonferroni AND-gate: argmax sharpe 2.798 < threshold 3.251 → fail
- DSR-style AND-gate: argmax p-value 0.189 ≥ 0.05 → fail
- Both AND-gates agree (`criteria_agree=True`)
- Argmax z=0.881 positive (above null expectation 2.487) but p-value in
  intermediate region (0.05 < p < 0.5) → Region 5 routing → `inconclusive`
  (intermediate-p sub-region per Q22 LOCKED 4-region routing structure)

### §4.5 Artifact

- Path: [data/phase2c_evaluation_gate/phase2c_12_audit_v1/_step8_result.json](../../data/phase2c_evaluation_gate/phase2c_12_audit_v1/_step8_result.json)
- Size: 70,401 bytes
- sha256: `38dbf5321376770a56a6b6ca994532462dd57d33fc2cce442627471ecb3d9266`

---

## §5 Cross-cycle comparison vs PHASE2C_11

### §5.1 Disposition-register cross-cycle table

| Cycle | n_trials | n_eligible | sharpe_var | argmax_sharpe | bonferroni_threshold | argmax_p | population_disposition |
|---|---|---|---|---|---|---|---|
| PHASE2C_11 | 198 | 154 | 0.530693 | (≤ 2.012) | 3.252158 | ≥ 0.5 | `artifact_evidence` |
| PHASE2C_12 | 197 | 139 | 0.811489 | 2.798131 | 3.250601 | 0.189 | `inconclusive` |

### §5.2 Substantive directional observation

**PHASE2C_11**: argmax sharpe ≤ expected_max_sharpe_null (positive z-score
≤ 0; argmax p-value ≥ 0.5) → `artifact_evidence` (consistent with random
under null hypothesis; argmax not even better than chance under multiple-
testing null).

**PHASE2C_12**: argmax sharpe 2.798 > expected_max_sharpe_null 2.487
(z = 0.881 positive; argmax p-value 0.189 in intermediate region) →
`inconclusive` (argmax above null expectation but not above Bonferroni
correction at conservative N=197 anchor).

**Cross-cycle disposition spectrum directional improvement**: PHASE2C_11
produced argmax indistinguishable from null (artifact_evidence). PHASE2C_12
produced argmax measurably above null but not above multiple-testing
correction (inconclusive intermediate-p). The cross-regime AND-gate
rate (8/197 vs 1/198) cross-cycle 2-prop z-test (p=0.0179) is statistically
distinguishable at the AND-gate metric register but **does NOT propagate
to disposition register signal_evidence**: AND-gate metric and population_
disposition Q22 LOCKED routing are register-class-distinct.

This is the substantive cycle finding: PHASE2C_12 hypothesis (theme
rotation 6/6 + adding `multi_factor_combination`) produced **directional
positive evidence at AND-gate metric register** but **not statistically
strong enough at disposition register** to cross signal_evidence threshold
under conservative multiple-testing correction at N=197.

---

## §6 Engine confound caveat (re-framed per Auth #6.5 ZERO DRIFT)

**Pre-Auth-#6.5 framing (load-bearing caveat):** Step 7 evaluation gate
baseline (4 regimes) used different head_sha values across PHASE2C_11
canonical artifacts (`d6f481a3` / `bdcf62d8` / `06fae09d` etc.) vs PHASE2C_12
fire commit `a6b1c1aa`. Cross-cycle comparison potentially confounded by
engine code differences across these commits.

**Post-Auth-#6.5 re-framing:** Auth #6.5 baseline re-fire at HEAD `08e1488`
verified PHASE2C_11 canonical Step 3 disposition (n_trials=198, n_eligible=154)
**bit-for-bit identical to canonical `_step3_result.json` (sealed at `f82d040`)
across all 17 compared fields**. ZERO DRIFT detected.

This shifts engine confound register-class:

**§6.1 Step 8 disposition framework register: confound structurally absent.**
The 7 commits to `evaluate_dsr.py` between PHASE2C_11 Step 3 SEAL and PHASE2C_12
Step 8 fire (`8887651`, `2a5c63a`, `605dfc6`, `995fdb2`, `3e1ee89`, `08e1488`)
preserve PHASE2C_11 canonical disposition exactly. `_resolve_n_eff_set(198)`
returns `(198, 80, 40, 5)` unchanged; ALLOWED_DUAL_GATE_PAIRS contains
PHASE2C_11 pairs unchanged; Bonferroni + Gumbel formulas identical; Q22
LOCKED routing identical. **Cross-cycle disposition comparison at §5 is
NOT confounded by Step 8 framework code differences.**

**§6.2 Step 7 evaluation gate runner register: confound not directly verified.**
Auth #6.5 verifies framework `evaluate_dsr.py` only, not
`scripts/run_phase2c_evaluation_gate.py` runner code. The PHASE2C_11
audit_v1 + audit_2024_v1 + eval_2020_v1 + eval_2021_v1 runs used different
commits across artifacts (`d6f481a3`/`bdcf62d8`/`06fae09d`); PHASE2C_12 runs
used commit `a6b1c1aa`. Whether these commits represent substantive runner
code changes is **not directly verified at this deliverable register**.

The `evaluation_semantics = "single_run_holdout_v1"` and
`artifact_schema_version = "phase2c_7_1"` fields are stable across all
PHASE2C_11 + PHASE2C_12 evaluation gate artifacts, suggesting low risk of
runner code substantive divergence. PHASE2C_8.1 Step 4 verification chain at
three independent layers including permanent in-repo recompute gate at
[`tests/test_phase2c_8_1_independent_recompute.py`](../../tests/test_phase2c_8_1_independent_recompute.py)
provides additional structural-equality evidence at the evaluation gate
runner register, but this evidence is descriptive at sub-register precision —
not a register-precision Auth #6.5-equivalent verification.

**§6.3 Net engine confound disposition:** Step 8 disposition register
comparison at §5 is structurally unconfounded. AND-gate rate cross-cycle
comparison at §3.4 is descriptively unconfounded but not register-precision-
verified at runner register. Both register-class disclaimers preserved
explicit at this register.

---

## §7 Sub-spec text ambiguity carry-forward

Sub-spec §6.1.3 Element 1 text: "(γ) full N=197 main batch + n_eligible≈154
secondary descriptive". This text was authored at sub-spec drafting cycle
under PHASE2C_11 framework reuse assumption (eligible≈154 carried from
PHASE2C_11 canonical fire). At Step 8 fire-time, PHASE2C_12 actual n_eligible
observed = 139 (NOT ≈154); sub-spec text predicted PHASE2C_11-anchor that
did not hold under PHASE2C_12 empirical Q16 [Path A patch] T_c<5 filter
output.

Additionally, the phrase "full N=197 main batch" was ambiguous between
two register-class interpretations:
- **(a)** "n_trials = 197 (Bonferroni multiple-testing count anchor)"
- **(b)** "input candidate count to compute_simplified_dsr() = 197"

Reading (a) is consistent with PHASE2C_11 canonical fire pattern (n_trials=198
with n_input=154 eligible). Reading (b) would require passing all 197
candidates including 58 excluded (structurally inadmissible per Q16
[Path A patch] LOCKED filter).

**Resolution at Step 8 fire-time (Auth #6.y register):** Reading (a) is
canonical; PHASE2C_12 fire pair = (n_trials=197, n_input=139) parallel
to PHASE2C_11 (198, 154).

**Carry-forward observation:** sub-spec text register-ambiguity that survived
3 dual-reviewer pass cycles + V#1-V#9 empirical verification at sub-spec
drafting cycle. This is **§19 instance #10 root cause**: handoff-noise
propagation between PHASE2C_11 framework reuse anchor (eligible≈154) and
PHASE2C_12 actual empirical (eligible=139) was not caught at sub-spec drafting
register; surfaced only at Step 8 fire-time when ALLOWED_DUAL_GATE_PAIRS
rejected canonical (197, 139) parallel-structure pair.

PHASE2C_13 methodology consolidation cycle should codify a **framework
parameter audit sub-step** at sub-spec drafting cycle terminus that
mechanically traces each Q-LOCKED parameter against framework code site —
prevents recurrence of this register-class defect.

---

## §8 §19 + §9.0c instance enumeration at PHASE2C_12 cycle SEAL

### §8.1 §19 spec-vs-empirical-reality cumulative count = 10 (PHASE2C_12 cycle)

| # | Instance | Surface register | Resolution |
|---|---|---|---|
| 1 | V#7 Path A patch — PHASE2C_11 §4.4 line 346 verbatim "T_c < 5" actual filter (NOT "≥20 trades" PHASE2C_8.1 cohort) | Sub-spec drafting V#7 empirical verification | Path A patch at 4 sites |
| 2 | Line-number drift between sub-spec citation + canonical artifact | Sub-spec drafting cycle | Path A patch revision |
| 3 | Q9 proposer-entry-register semantic ambiguity (smoke override site) | Step 1 implementation | Step 1 code surface fix at `d46e24f` |
| 4 | STAGE2D_BATCH_SIZE=200 vs Q3 N=198 carry-forward | Step 1 implementation | Carry-forward to Step 2 fire-prep |
| 5 | Batch size config-driven Step 2 blocker (200 vs 197 framework hard limit) | Step 2 fire-prep | Surface (1) `_resolve_batch_size()` at `7c682fd` |
| 6 | Ledger pre-charge coupling at Critic cost (PHASE2C_3 + PHASE2C_5 carry-forward) | Step 2 fire-prep | Surface (3) `--live-critic` ledger wrap at `30d3bfd` |
| 7 | Q3 LOCKED main batch=198 candidates vs actual 197 valid (rejected_complexity at pos=75) | Step 8 fire-prep | `PHASE2C_12_N_RAW = 197` constant + paired-pair allowlist at `8887651` |
| 8 | Sub-spec Q15 [REVISED] N_eff `{198, 80, 40, 6}` for PHASE2C_12 cycle but framework code hardcoded `{198, 80, 40, 5}` (5 themes anchor) | Auth #6.x extension | Cycle-conditional `_resolve_n_eff_set()` at `995fdb2` |
| 9 | Sensitivity table primary anchor hardcoded EXPECTED_N_RAW=198 (Codex Finding B) | Auth #6.x extension | Parameterized to fire's n_trials at `995fdb2` |
| 10 | ALLOWED_DUAL_GATE_PAIRS parallel-structure incompleteness (auth #6.x β1 narrow added (197, 197) only; missed (197, 139) eligible-subset parallel to PHASE2C_11 (198, 154)) | Step 8 fire-time | Auth #6.y `(PHASE2C_12_N_RAW, PHASE2C_12_N_ELIGIBLE_OBSERVED)` at `08e1488` |

**Cross-cycle cumulative § 19 count: 20** (10 PHASE2C_12 + 4 PHASE2C_10 +
3 PHASE2C_11 sub-spec drafting + 3 PHASE2C_11 implementation/closeout).

### §8.2 §9.0c process-design observation cumulative count = 8 (PHASE2C_12 cycle)

| # | Instance | Register class | Codification candidate |
|---|---|---|---|
| 1 | Sub-spec drafting cycle structural-overlay reviewer pass operating without empirical verification fire | Sub-spec drafting | Codified — V#1-V#9 empirical verification fire register at sub-spec drafting cycle |
| 2 | Same-agent fresh-register full-file pass at sub-spec drafting cycle | Sub-spec drafting | Carry-forward: cross-cycle accumulation |
| 3 | Authorization-routing momentum (auth #1 implicit-cover Step 2 fire-prep) | Authorization register | Codified — anti-momentum-binding strict reading at Auth #6 + #6.y register |
| 4 | Reviewer divergence on Q10 operationalization site (entry vs config-driven) | Reviewer register | Resolved — Charlie register adjudication |
| 5 | Pre-fire structure validation gap (β1 narrow scope didn't audit allowlist parallel-structure with PHASE2C_11) | Multi-reviewer convergence | Folded into §16 ### Failure-mode signal |
| 6 | Fire-time discovery handoff-noise propagation (eligible≈154 PHASE2C_11 anchor → PHASE2C_12 actual 139) | Sub-spec drafting → fire-time | §7 carry-forward observation; PHASE2C_13 methodology candidate |
| 7 | Multi-reviewer convergence on β1 narrow scope at auth #6.x didn't audit ALLOWED_DUAL_GATE_PAIRS for parallel-structure completeness with PHASE2C_11 | Multi-reviewer + Charlie register convergence | §10 PHASE2C_13 methodology consolidation cycle Item 6 |
| 8 | Advisor pre-fire interpretive overlay on mechanical Q22 LOCKED compute output (predicted artifact_evidence; actual inconclusive at fire-time) | Reviewer register | §10 Item 5 reviewer over-interpretation prevention + Item 6 §9.0c register-class taxonomy |

**§9.0c register-class taxonomy candidate (per Item 6 sub-rule):**
8 instances span heterogeneous register classes — sub-spec drafting (#1, #2, #6),
authorization register (#3), reviewer register (#4, #5, #7, #8). Single-bucket
"process failure" framing collapses register-class distinctions; PHASE2C_13
codification should preserve register-class precision per Item 6 sub-rule.

**Cross-cycle cumulative § 9.0c count: not authoritatively established at this
register.** PHASE2C_10 + PHASE2C_11 cycle §9.0c instance counts were
codification candidates, not formal registers. PHASE2C_13 methodology
consolidation cycle Item 6 should establish authoritative cross-cycle § 9.0c
register.

---

## §9 Strategy direction observation (preliminary; full sub-spec at PHASE2C_14)

This section documents **preliminary** strategy direction observations from
PHASE2C_12 cycle empirical evidence; full strategy refinement specification
deferred to PHASE2C_14 sub-spec drafting cycle per §10 split scope.

### §9.1 Priority 1 — `multi_factor_combination` substantive evidence

**Evidence at descriptive register:**
- mfc per-theme AND-gate rate 9.1% (3/33) vs non-mfc 3.0% (5/164)
- mfc 95% Wilson CI [3.14%, 23.57%] (wide; small sample n=33)
- 2-prop z-test mfc vs non-mfc: z=1.6044, p=0.1086 (NOT significant at 0.05)
- Fisher exact: OR=3.18, p=0.1323 (NOT significant)
- mfc bimodal distribution: top performers (8 cross-regime survivors include 3 mfc) + degenerate tail

**Substantive observation:** mfc shows directional positive signal at descriptive
register, but per-theme advantage is **NOT statistically distinguishable from
non-mfc baseline** at PHASE2C_12 cycle sample size. Single-batch evidence
insufficient to confirm systematic theme advantage; multi-batch evidence
required.

**PHASE2C_14 strategy refinement spec direction (preliminary):** Preserve
mfc theme + investigate **structured combination constraints** to address
bimodal distribution (degenerate tail). Specific structured-combination
shape should be **derived from PHASE2C_12 8 AND-gate survivor factor
compositions** (empirical-grounded), not imposed ex ante via advisor speculation
(per adjudication: "DERIVE not impose").

### §9.2 Priority 2 — `volatility_regime` zero-trade observation

**Evidence at descriptive register:**
- volatility_regime AND-gate rate 0/32 = 0.0% (zero contribution)
- volatility_regime zero-trade rate ~59.4% at Step 6.5 WF (much higher than
  other themes 0-33%)

**Substantive observation:** volatility_regime appears to be cycle's "broken
theme" at descriptive register, but distinguishing **systematic prompt issue**
from **single-batch LLM stochasticity** requires multi-batch evidence per
advisor caveat.

**PHASE2C_14 strategy refinement spec direction (preliminary):** Defer
volatility_regime fix scope to PHASE2C_15 multi-batch sample evidence; do
NOT apply prompt-engineering fixes at PHASE2C_14 sub-spec without
distinguishing evidence basis.

### §9.3 Priority 3 — WF Sharpe weight reduction

**Evidence at descriptive register:**
- 5/8 (62.5%) AND-gate survivors are audit-only partition members (WF Sharpe < 0.5)
- Single AND-gate survivor with strong WF Sharpe ≥ 0.5: `88192bc5c256b702`
  (volume_divergence, wf_sharpe = 0.835)
- WF Sharpe single-train-test boundary metric is **specialization** metric;
  cross-regime survival is register-class-distinct **robustness** metric

**Substantive observation:** WF Sharpe single-boundary metric **systematically
under-selects** cross-regime robust strategies in PHASE2C_12 evidence basis.
PHASE2C_11 §4.4 audit-only inclusion register decision is **retroactively
validated** by 5/8 AND-gate composition.

**PHASE2C_14 strategy refinement spec direction (preliminary):** First-pass
filter semantics should weight cross-regime robustness over single-boundary
specialization. Specific filter design (2-tier with cheap Tier 1 + expensive
Tier 2 cross-regime evaluation) is implementation-detail; PHASE2C_14 sub-spec
should focus on filter SEMANTICS first (what does first-pass measure)
before optimization (compute cost).

---

## §10 PHASE2C_13 methodology consolidation cycle entry recommendation

### §10.1 Cycle naming + scope split decision

Per Charlie 4-stage strategic framing + Claude Code adjudication + ChatGPT
ratification + advisor convergence, PHASE2C_13 entry adopts **split scope**
per PHASE2C_10/11 cycle scope discreteness precedent:

- **PHASE2C_13** = methodology consolidation cycle (process / spec only;
  no batch fire; no strategy refinement scope)
- **PHASE2C_14** = strategy refinement sub-spec drafting cycle (3 priorities)
- **PHASE2C_15** = first batch fire under refined methodology + strategy

**Cost-benefit:** 3 cycles vs 1 longer time-to-validation; benefit is each
cycle has clean discrete scope; methodology fixes don't get coupled to
strategy refinement debates; precedent consistency preserved.

### §10.2 PHASE2C_13 methodology consolidation cycle scope (6 items + sub-rule)

**Item 1 — Fire-prep precondition checklist codification.** PHASE2C_12
cycle surfaced 4 fire-time precondition gaps (Step 6.5 WF lineage + framework
N mismatch + sensitivity table N_eff + ALLOWED_DUAL_GATE_PAIRS asymmetry).
Codify mechanical pre-fire verification step at each Step boundary tracing
each Q-LOCKED parameter against framework code site.

**Item 2 — Framework parameter pre-lock at sub-spec drafting cycle.** Add
"framework parameter audit" sub-step at sub-spec drafting cycle terminus
that mechanically enumerates each Q-LOCKED parameter and traces to framework
code site. Prevents handoff-noise propagation that produced §19 instances
#5, #6, #8, #10.

**Item 3 — Step 7/8 contract standardization.** Codify inter-step contract
test (schema + sample + validation) at each Step boundary. Step 7 evaluation
gate output schema → Step 8 input contract had no explicit interface spec
at PHASE2C_12 fire-time.

**Item 4 — LOCKED items → executable checklist.** Each Q-LOCKED item should
configure 1 verification function fired automatically at fire-prep time.
Example: `_resolve_n_eff_set()` at Auth #6.x-extension is a verification
function pattern; Item 4 codifies this as sub-spec drafting cycle requirement.

**Item 5 — Reviewer over-interpretation prevention.** Codify register-class
explicit declaration in each Step deliverable: "Before interpreting metric X,
declare which register-class (intermediate / final / sensitivity)". §9.0c
instance #8 (advisor pre-fire prediction wrong) is concrete instance of
this defect class. Add reviewer prompt template: "Does this metric belong
to mechanical-output register or interpretive-overlay register?"

**Item 6 — §9.0c instance density mechanism + register-class taxonomy
sub-rule.** PHASE2C_12 cycle accumulated 8 §9.0c instances (substantively
higher than PHASE2C_10 + PHASE2C_11 at comparable cycle stages). Codify
**continuous improvement vs batch improvement** register choice:
- Each §9.0c instance should trigger immediate process patch (continuous)
- vs current pattern of carry-forward to next consolidation cycle (batch)
- **Sub-rule: §9.0c register-class taxonomy.** Single "process failure"
  bucket collapses register-class distinctions. Codify taxonomy with
  separate register-class enumeration:
  - Sub-spec drafting register (instances #1, #2, #6)
  - Authorization register (instance #3)
  - Reviewer register (instances #4, #5, #7, #8)
- Mitigation strategies are register-class-distinct; bulk-mitigation
  collapses register-class precision.

### §10.3 PHASE2C_13 cycle process improvement opportunities anchor

§8.2 instance enumeration is the **canonical evidence basis** for PHASE2C_13
methodology consolidation cycle Items 1-6. PHASE2C_13 sub-spec drafting cycle
operates on §8.2 enumeration as input artifact (not re-derived from cycle
re-examination).

### §10.4 PHASE2C_14 strategy refinement sub-spec preliminary direction anchor

§9.1-§9.3 preliminary observations are the **canonical evidence basis** for
PHASE2C_14 strategy refinement sub-spec drafting cycle. PHASE2C_14 sub-spec
operates on §9 observations as input artifact + adds:
- Pre-registration register: success criteria with CI-based comparison
  (PHASE2C_12 baseline 8/197 = 4.06% as **estimate**, not anchor; 95% Wilson
  CI [2.07%, 7.81%] as bounds; PHASE2C_15 fire success = rate above CI lower
  bound)
- Multi-batch evidence requirement specification (when can theme issues be
  attributed to systematic vs stochastic at register-precision)
- Filter semantics specification (first-pass measures what; only after
  semantics codified, optimize compute cost)

### §10.5 PHASE2C_15 fire scope (deferred specification)

PHASE2C_15 = first batch fire under refined methodology + strategy. Scope
specification is **deferred to PHASE2C_14 sub-spec drafting cycle** per
anti-pre-naming option (ii). PHASE2C_13 + PHASE2C_14 work establishes the
specification basis; PHASE2C_15 fire executes under that specification.

### §10.6 Cross-cycle scaling observation

PHASE2C cycles accumulating cycle-complexity scaling (PHASE2C_8 ~ PHASE2C_12
each substantively more complex than prior at comparable substantive scope).
PHASE2C_13 methodology consolidation cycle should explicit address: is
process discipline keeping pace with substantive complexity, or are §19 +
§9.0c instances accumulating because process-design is not scaling?

---

## §11 Anchors

### §11.1 Sub-spec + planning artifacts

- [PHASE2C_12_PLAN.md](../phase2c/PHASE2C_12_PLAN.md) — sub-spec drafting cycle SEAL at `b8e4972`
- [PHASE2C_12_SCOPING_DECISION.md](../phase2c/PHASE2C_12_SCOPING_DECISION.md) — scoping decision SEAL at `541c0be`
- [PHASE2C_12_STEP1_DELIVERABLE.md](../phase2c/PHASE2C_12_STEP1_DELIVERABLE.md) — Step 1 SEAL at `4e112a3`
- [PHASE2C_12_STEP2_DELIVERABLE.md](../phase2c/PHASE2C_12_STEP2_DELIVERABLE.md) — Step 2 fire-prep SEAL at `4f95c7c`

### §11.2 Operational artifacts

- [`data/phase2c_evaluation_gate/phase2c_12_audit_v1/_step8_result.json`](../../data/phase2c_evaluation_gate/phase2c_12_audit_v1/_step8_result.json) — Step 8 disposition output (sha256 `38dbf532...`)
- [`data/phase2c_evaluation_gate/audit_v1/_auth_6_5_baseline_refire.json`](../../data/phase2c_evaluation_gate/audit_v1/_auth_6_5_baseline_refire.json) — Auth #6.5 ZERO DRIFT verification (sha256 `9e1dc894...`)
- 4-regime evaluation gate artifacts: `data/phase2c_evaluation_gate/phase2c_12_audit_v1/`, `phase2c_12_audit_2024_v1/`, `phase2c_12_eval_2020_v1/`, `phase2c_12_eval_2021_v1/`
- Main batch fire batch_id: `7f2f7d3e-df22-4ef7-9d7a-6f1733fe5c67`

### §11.3 Framework code register at PHASE2C_12 SEAL

- HEAD commit at this deliverable seal: `08e1488` + this commit
- `backtest/evaluate_dsr.py` at line 92 (`PHASE2C_12_N_RAW = 197`)
- `backtest/evaluate_dsr.py` at line 124 (`PHASE2C_12_N_ELIGIBLE_OBSERVED = 139`)
- `backtest/evaluate_dsr.py` at line 129 (`ALLOWED_DUAL_GATE_PAIRS` 4-pair frozenset)
- `backtest/evaluate_dsr.py` at line 153 (`_resolve_n_eff_set()`)
- 7 commits to evaluate_dsr.py in PHASE2C_12 cycle: `8887651`, `2a5c63a`, `605dfc6`, `995fdb2`, `3e1ee89`, `08e1488` (auth #6.x β1 + Codex hotfix + #6.x-extension RED + GREEN + #6.y RED + GREEN)

### §11.4 Engine + walk-forward register

- Engine commit at PHASE2C_12 cycle: `eb1c87f`
- Engine tag: `wf-corrected-v1`
- Engine guard helpers: `backtest/wf_lineage.py` (`check_wf_semantics_or_raise()` + `check_evaluation_semantics_or_raise()`)

---

**END OF PHASE2C_12 RESULTS DOCUMENT**

Forward-pointer (§10): PHASE2C_13 entry scoping cycle (methodology
consolidation cycle ratification) is the next arc after PHASE2C_12 SEAL at
fresh session post-this-deliverable per pacing discipline. Successor
scoping cycle adjudicates PHASE2C_13 sub-spec drafting cycle scope from
this document §8.2 + §10 register.
