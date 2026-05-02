# PHASE2C_11 Step 1 Deliverable — Artifact Inventory + RS-2 Guard Verification + α-Refine + Module Scope

**Status: WORKING DRAFT v2 — post-Charlie-authorized v3.1 sub-spec patches + METHODOLOGY_NOTES §20 v2 precedent doc codification (with advisor L1+L2+L3+L4+L5 fixes); pre-final-reviewer-pass; pre-seal.**

**Anchor:** PHASE2C_11_PLAN.md v3 sealed at commit `c5b740c`; v3.1 in-arc patches (3 sites for Instance 5; 2 sites for Instance 6 reframe; 1 site for Instance 7) applied at this Step 1 cycle per Charlie-register authorization on **P2 + precedent doc** path. Adjudication trail: (i) initial Charlie-register authorization on option (b) reviewer-ratified reframing; (ii) Claude advisor substantive objection at register-precision — bare P2 silently weakens §0.4 anti-p-hacking guardrail; objection surfaced P1 / P2+precedent-doc / bare-P2 trichotomy; (iii) ChatGPT + Claude Code converged with advisor on P2+precedent-doc; (iv) Charlie-register authorization on **P2 + precedent doc** path; (v) Claude advisor substantive pass on §20 v1 wording surfaced 5 concerns (L1: T3/T2 internal contradiction; L2: T1 boundary placement at Step 1 end too tight; L3: missing T5 parameter calibration discipline; L4: one-patch-per-lockpoint promotion to checklist; L5: 4 polish items including instance template + tier-re-evaluation honesty + labeled commit pair definition + reviewer-divergence path); (vi) Charlie-register authorization on β path "approved on both reviewer synthesis β" incorporating L1+L2+L3+L4+L5; (vii) §20 v2 codified with 5 explicit triggers (individually necessary, jointly sufficient) — Instance 6 logged as §20.5 Instance 1 with mandatory 5-field template (anchor citation + per-trigger verification + reviewer convergence record + Charlie-register authorization citation + patch-substance adjudication notes). This deliverable v2 reflects post-patch + post-§20-v2-codification CLEAN status; final ChatGPT structural pass on full bundle + final advisor substantive pass on §20 v2 wording remain operational steps before Charlie-register seal authorization.

**Hard scope per [PHASE2C_11_PLAN §7.1 + §7.2](PHASE2C_11_PLAN.md):** verification + attestation + descriptive characterization only; **NO DSR-style screen computation fires at Step 1.**

---

## §1 Inventory verification — CLEAN at five pillars

Verification script at `/tmp/phase2c_11_step1_verify.py` (transient; not committed; reproducible from the source artifacts at `data/phase2c_evaluation_gate/audit_v1/`).

### §1.1 Directory and JSON existence (PHASE2C_11_PLAN §7.1 Step 1 lockpoint)

- audit_v1 candidate directories : **198** (matches §2.1 lockpoint)
- holdout_summary.json present + parseable : **198 / 198**
- holdout_summary.json missing or unparseable : **0**

### §1.2 RS-2 guard call discipline (PHASE2C_11_PLAN §0.3 + §2.5 + §7.1)

`backtest.wf_lineage.check_evaluation_semantics_or_raise(summary, artifact_path=...)` invoked **before every audit_v1 holdout_summary.json field access**:

- guard pass : **198 / 198**
- guard fail : **0**

This satisfies the RS-2 lockpoint at §0.3 + §7.1: every audit_v1 artifact consumption at Step 1 is gated by the consumer-side helper per Section RS canonical hard prohibition. The same call discipline carries forward to Steps 2-5 per §7.1 RS-2 lockpoint at every step + §4.5 RS-3 lockpoint at `compute_simplified_dsr()` function entry (Step 3).

### §1.3 hypothesis_hash field consistency

Directory name (16-char DSL truncated hash per `agents/hypothesis_hash.py:172-173`) cross-checked against `holdout_summary.json` `hypothesis_hash` field at all 198 candidates:

- mismatches : **0**

### §1.4 Lineage attestation (5-field RS attestation)

All 198 audit_v1 candidates report single-valued attestation fields:

| Field | Distinct value | Count |
|---|---|---|
| `evaluation_semantics` | `single_run_holdout_v1` | 198 |
| `engine_commit` | `eb1c87f` | 198 |
| `engine_corrected_lineage` | `wf-corrected-v1` | 198 |
| `lineage_check` | `passed` | 198 |
| `current_git_sha` | `d6f481a3692d48d95b6cb39af686fa6dfc34f964` | 198 |
| `artifact_schema_version` | absent (legacy PHASE2C_6 schema) | 198 |

The `artifact_schema_version` absent across all 198 confirms the audit_v1 evaluation gate uses the legacy PHASE2C_6 schema branch of `check_evaluation_semantics_or_raise()` (per docstring: "Absent — legacy PHASE2C_6 schema. Validates the original five fields below."). PHASE2C_8.1 schema discriminator `phase2c_8_1` is not present at audit_v1 — that discriminator applies to the multi-regime extension artifacts (`audit_2024_v1`, `eval_2020_v1`, `eval_2021_v1`), which are out of MVD scope per §3.3 multi-regime sensitivity register only.

Single distinct `current_git_sha` confirms all 198 evaluations were run from the same source-tree state.

### §1.5 Distribution descriptors (descriptive register only per §3.3)

| Descriptor | Distribution |
|---|---|
| `lifecycle_state` | `holdout_failed`: 185 ; `holdout_passed`: 13 |
| `theme` | `calendar_effect`: 40 ; `volume_divergence`: 40 ; `volatility_regime`: 40 ; `momentum`: 39 ; `mean_reversion`: 39 |
| Total | **198** |

Theme distribution confirms 5-theme operational rotation per CLAUDE.md "Theme rotation operational boundary (Stage 2c/2d)" anchor (40+40+40+39+39 = 198).

Holdout pass rate 13/198 ≈ 6.6%; lifecycle_state distribution descriptive only — does NOT enter primary DSR-style screen at Step 3 (which operates on Sharpe scalars per §3.3 lockpoint regardless of lifecycle_state).

### §1.6 Sharpe scalar empirical distribution (descriptive only at Step 1)

Computed across all 198 candidates from `holdout_summary.json` `holdout_metrics.sharpe_ratio` field (per §3.3 lockpoint):

| Statistic | Value |
|---|---|
| n | 198 |
| min | -2.7147 |
| median | -0.7228 |
| max | **1.2624** |
| mean | -0.6731 |
| std (ddof=1) | 0.7683 |

Trade count distribution (per §4.4(1) edge-case filter):

- min `total_trades` : 0
- median : 48
- max : 491
- candidates with `total_trades < 5` (pre-registered §4.4(1) exclusion) : **44**
- eligible-subset N after §4.4(1) exclusion : **154**

These are **descriptive-only at Step 1**; Step 3 DSR-style screen has not fired. Reported here for forward-traceability per §7.1 deliverable scope.

---

## §2 §19 spec-vs-empirical-reality finding pattern instances surfaced at Step 1

Per [PHASE2C_11_PLAN §0.4 + §7.3] hard rule: **NO mid-arc spec adjustment at primary register without explicit Charlie-register authorization.** Step 1 surfaced four spec defects for reviewer routing per §8.1 (three substantive + one self-§19 self-correction at this deliverable); both reviewers (ChatGPT + Claude advisor) converged on option (b) reviewer-ratified reframing; Charlie-register authorized the patch slate. v3.1 patches applied at sub-spec; v2 deliverable reflects post-patch dispositions.

**Cumulative §19 instance count at PHASE2C_11 cycle through Step 1 v2 deliverable register: 8** (4 at v1→v2→v3 sub-spec drafting per §0.5 + 3 substantive at this Step 1 + 1 self-§19 at Step 1 deliverable v1 register correcting "four sites" to "three sites" for Instance 5 — see §2.1 disposition).

### §2.1 Instance 5 — Bonferroni threshold numerical-approximation defect

**Verification register:** canonical-numerical-precision register.

**Self-§19 correction at this deliverable (v1 → v2):** Step 1 deliverable v1 stated "cited at four sites" for Instance 5; empirical grep at canonical-artifact register (`grep -n "3\.0688" PHASE2C_11_PLAN.md`) shows **three sites only** (lines 230 §3.5, 248 §3.6, 303 §4.3); §6.1 line 466 contains only the formula `sqrt(2*ln(198))` without numeric. v1 over-counted by one site at structural-summary register without canonical-artifact verification — same defect class as v3 sub-spec instances per §0.5 forward-pointing observation. v2 deliverable corrects to three sites; this self-§19 is logged at the cumulative §19 instance count for cross-cycle tracking register.

**Spec-stated claim at v3** (sub-spec §3.5 + §3.6 + §4.3 Step 1; cited at three sites):

> "Bonferroni-style threshold ... `SR_threshold_Bonferroni = sqrt(2 * ln(N))` at N=198. Threshold value **≈ 3.0688** at N=198."

**Empirical reality** (computed by `math.sqrt(2.0 * math.log(198))` per spec formula):

> sqrt(2 * ln(198)) = sqrt(2 * 5.28827...) = sqrt(10.57654...) = **3.25216...**

The cited approximation `≈ 3.0688` is empirically incorrect. The formula lockpoint `sqrt(2 * ln(N))` is correct canonical math; only the four-site cited numerical approximation is wrong.

**Defect-class characterization:** docs-typo magnitude at canonical-numerical-precision register; the spec lockpoint is the FORMULA, not the cited approximation. Step 3 implementation will compute the threshold from the formula directly per §4.3 Step 1; the result is 3.2522, not 3.0688.

**Disposition (v2 post-patch):** **PATCHED at v3.1 sub-spec per Charlie-authorized reviewer ratification.** Both reviewers ratified docs-typo characterization (no §0.4 inconclusive trigger); patch applied at all 3 sites with explicit `(v3.1 patch ...)` annotation preserving audit trail. Step 3 + Step 4 result narrative will cite the corrected approximation.

**Forward-pointing observation:** this instance empirically validates the §0.5 verification register enumeration claim — canonical-numerical-precision register catches a defect class that canonical-formula register does not (the formula was correct; only the numerical approximation was wrong). Plus the v1→v2 self-§19 at this deliverable empirically reinforces: even at observer/auditor register, structural-summary claims about site counts can drift from canonical-artifact register without explicit grep firing.

### §2.2 Instance 6 — JSON-vs-CSV cross-validation tolerance defect

**Verification register:** canonical-numerical-precision register.

**Spec-stated lockpoint** (sub-spec §3.4 + §4.4(5)):

> "If per-candidate scalar disagrees between holdout_summary.json and holdout_results.csv aggregate row by **|delta| > 1e-9** floating-point precision, candidate excluded from primary computation; discrepancy documented at result register."

**Empirical reality** at audit_v1 register:

- `holdout_results.csv` stores scalars at **6-decimal precision** (e.g., `-0.288674`, `0.463763`).
- `holdout_summary.json` stores full-precision floats (e.g., `0.1360599286363915`).
- Empirical max |delta| observed across 198 candidates × 5 scalar fields: **~5e-7** (consistent with CSV 6-decimal rounding).
- **All 198 candidates have at least one scalar with |delta| > 1e-9.**
- Total scalar disagreements at |delta| > 1e-9 : **488** (across 4 cross-validated columns × ~122 unique candidates with rounding-distinguishable scalars).

Strict literal application of the §3.4 + §4.4(5) lockpoint would **exclude all 198 candidates from primary computation**. This is absurd: the canonical scalar register is the JSON (per §3.3); the CSV is an aggregate convenience artifact rounded to 6 decimals at engine output time. The cross-validation was intended as a sanity check for genuine divergence (corrupted JSON, stale CSV), not for floating-point precision policing of CSV's storage register.

**Defect-class characterization:** lockpoint-substance defect at canonical-numerical-precision register. The §3.4 + §4.4(5) tolerance was set at `|delta| > 1e-9` apparently inherited from v2's per-trade-derived-Sharpe vs engine-output-Sharpe cross-validation register-class (which operated at canonical-DSR scope). At simplified MVD scope, no per-trade derivation operates (per §3.4 explicit statement), so the cross-validation register is JSON (full precision) vs CSV (6-decimal precision); a tolerance of 1e-9 is incompatible with this pair.

**Disposition (v2 post-patch):** **PATCHED at v3.1 sub-spec per Charlie-authorized option (b) reviewer-ratified reframing.** Both reviewers (ChatGPT structural + Claude advisor substantive) converged on option (b); ChatGPT specified "tolerance to 1e-6 or 1e-5"; advisor recommended R1 verification first to confirm 1e-9 lockpoint actually present (verification fired at canonical artifact register and confirmed 1e-9 at lines 224/350 — scenario A); Charlie-register authorized the patch slate. Adjudication on tolerance value: **1e-6 selected** (over 1e-5) — empirical max |Δ| ≈ 5e-7 (CSV 6-decimal storage rounding floor); 1e-6 sits one order of magnitude above the empirical floor (catches storage rounding cleanly without permitting genuine engine-output divergence). v3.1 patch reframes §3.4 + §4.4(5) cross-check as **descriptive consistency sanity-check, NOT primary-exclusion lockpoint substance**; JSON remains canonical scalar source per §3.3 (unchanged); discrepancies at |Δ| > 1e-6 are documented + reviewer-routed for substantive interpretation, not auto-excluded. Re-verification at 1e-6 register: **0 disagreements across 198 candidates × 5 cross-validated columns** — cross-validation CLEAN at patched register.

**Anti-p-hacking discipline preserved:** patch does NOT change any pass/fail criterion at §3.6 or §6.1 (Bonferroni threshold + DSR-style p < 0.05 + conservative AND-gate all unchanged); patch operates at eligibility/scope register (which candidates participate), and at patched register the eligibility scope is the full n=198 (vs 0 under literal 1e-9 reading). Both interpretations are pre-result; the substantive computation lockpoints (formula, threshold, p-value, AND-gate) are unchanged.

**Codification at canonical discipline register (METHODOLOGY_NOTES §20 v2; first precedent; advisor L1+L2+L3+L4+L5 fixes incorporated):** to prevent Instance 6's reframe from operating as an undocumented case-by-case exception to §0.4, this Step 1 cycle bundles METHODOLOGY_NOTES §20 codification — a Strong-tier operating rule articulating **five explicit triggers** (T1 pre-result register at end-of-Step-2 boundary; T2 structural infeasibility at canonical-artifact register with by-construction 100% input exclusion under literal application; T3 no substantive pass/fail criterion changes — boundary clarification at structurally-degenerate-filter binding-action register; T4 full audit trail v* → v*.1 with labeled commit pair definition; T5 patch parameter calibrated to canonical-artifact register-precision floor — anti-loosening discipline) under which an in-arc patch is admissible without weakening the post-hoc adjustment defect class §0.4 forbids. Instance 6 verified at all five triggers; logged at §20.5 cumulative instance register as Instance 1 with mandatory 5-field template (anchor citation + per-trigger verification + reviewer convergence record + Charlie-register authorization citation + patch-substance adjudication notes). Future similar cases gated by §20 5-trigger verification, not case-by-case judgment. This codification (v2 incorporating advisor synthesis fixes) was the load-bearing condition for Charlie-register authorization on P2+precedent-doc path; bare P2 path was rejected per advisor + Charlie convergence on §0.4 integrity grounds.

**Forward-pointing observation:** this instance also empirically validates the §0.5 verification register enumeration claim — the lockpoint was checked at canonical-formula register (formula reads as plausible) but not at canonical-numerical-precision register against the actual CSV storage format (which would have caught the tolerance/precision incompatibility). Notably, v3 §0.5 Instance 3 logged that advisor β-Refine had flagged `|delta| < 1e-6` "might be tight at numerical-precision register"; v3 author tightened to 1e-9 instead of loosening; this Step 1 verification empirically reverses the v3-tightening direction toward the advisor's prior 1e-6 register lean. Pattern: pre-empirical caution can pull lockpoints in the opposite direction of what canonical-artifact verification would recommend.

### §2.3 Instance 7 — α-Refine claim "246 runs > 198 distinct hashes" at canonical-numerical-precision register

**Verification register:** canonical-numerical-precision register (additionally canonical-artifact register at experiments.db schema).

**Spec-stated claim** (PHASE2C_11_PLAN §7.1 α-Refine deliverable + Phase Marker citation):

> "empirical multi-run hypothesis_hash distribution at experiments.db (**246 runs > 198 distinct hashes** at bear_2022 partition)"

**Empirical reality** at experiments.db `runs` table for `batch_id = b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`:

| Field | Value |
|---|---|
| total `regime_holdout` rows | **854** |
| distinct `hypothesis_hash` values | **198** |
| total batch rows (all run_types) | **854** (all `regime_holdout`) |
| hash format | 64-char SHA256 (5/5 sample) — confirms §0.5 Instance 4 hash-scheme finding |
| audit_v1 hash format (separate artifact) | 16-char DSL truncated |

Multiplicity distribution at `regime_holdout` partition (n_runs_per_hash → count_of_hashes):

| Runs per hash | Count of hashes | Subtotal rows |
|---|---|---|
| 4 | 149 | 596 |
| 5 | 39 | 195 |
| 6 | 7 | 42 |
| 7 | 3 | 21 |
| **Total** | **198** | **854** |

The cited "246 runs" figure is empirically incorrect; actual is **854 regime_holdout rows / 198 distinct 64-char-SHA256 hashes** with multiplicity 4–7 per hash.

**Defect-class characterization:** docs-typo magnitude at canonical-numerical-precision register; descriptive forward-pointing observation register only at simplified MVD scope (per §2.4 cross-register mapping is OUT-OF-MVD-SCOPE).

**Disposition (v2 post-patch):** **PATCHED at v3.1 sub-spec §7.1.** α-Refine description corrected to actual empirical numbers (854 regime_holdout rows / 198 distinct 64-char SHA256 hashes; multiplicity distribution {4: 149; 5: 39; 6: 7; 7: 3}); explicit forward-pointing for §4.7 deferred prerequisite work register added (Path A canonical-hash mapping must resolve which experiments.db run is "the" canonical run for a given audit_v1 candidate given 4–7 multiplicity profile). No §0.4 inconclusive trigger at simplified MVD scope (descriptive deliverable, not lockpoint substance).

**Forward-pointing observation:** four §19 instances were documented at v3 sub-spec drafting cycle (§0.5 Instance 1-4); this Step 1 surfaces three additional instances (§2.1 / §2.2 / §2.3 herein). Cumulative §19 instance count at PHASE2C_11 cycle through Step 1 register = **7**. Of these, 5 fired at canonical-numerical-precision register specifically (§0.5 Instance 3 + Instance 4 numerical components + §2.1 + §2.2 + §2.3). The catch-class coverage observation at §0.5 ("canonical-numerical-precision register catches distinct defect class; comprehensive coverage requires explicit per-register firing decision") is empirically reinforced at Step 1 implementation register.

---

## §3 α-Refine deliverable — empirical experiments.db hypothesis_hash distribution

Per [PHASE2C_11_PLAN §7.1 α-Refine extension]:

> "Step 1 deliverable additionally documents the empirical multi-run hypothesis_hash distribution at experiments.db ... Note: this is descriptive register only at simplified MVD scope; cross-register mapping to experiments.db is out-of-scope per §2.4."

**Empirical observations at experiments.db `runs` table for `batch_id = b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`:**

1. **Hash scheme confirmed:** all 5 sampled `hypothesis_hash` values are 64-char SHA256 strings; none is a 16-char prefix. This empirically confirms §0.5 Instance 4 finding ("audit_v1 hash `95bf56e74564ea34` is NOT a prefix of any experiments.db hash"). Cross-register identifier mapping between audit_v1 (16-char DSL) and experiments.db (64-char SHA256) is **non-trivial**: hash equality / prefix-match cannot link the two registers.

2. **Run multiplicity at regime_holdout partition:** 854 rows / 198 distinct hashes; multiplicity ranges 4–7 per hash; mode = 4 (149 of 198 hashes; 75.3%). The 4-run-per-hash mode is consistent with v2 split's 4 train windows × 1 regime_holdout output per window per candidate (interpretive-register; not load-bearing at simplified MVD).

3. **Run-type uniformity:** all 854 batch rows are `run_type = 'regime_holdout'`; no `walk_forward_window` / `walk_forward_summary` / `single_run` rows at this batch. The walk-forward training arc artifacts live at separate batches (n=1800 walk_forward_window + n=434 walk_forward_summary across all batches per global run_type counts).

4. **Partition semantic mismatch (per §0.5 Instance 4 + §2.3 herein):** experiments.db `regime_holdout` runs are train-window-output evaluations (4-7 windows per candidate); audit_v1 `holdout_summary.json` is single-run bear_2022 evaluation per candidate (1 evaluation per candidate). The two are different evaluation-register-classes and **cannot be cross-validated at scalar register without prerequisite work** (per §0.5 Instance 4 + §4.7 deferred prerequisite work register). This empirically reaffirms why audit_v1 is the canonical input for PHASE2C_11 simplified DSR-style screen, and why experiments.db is OUT-OF-MVD-SCOPE per §2.4.

**Forward-pointing for §4.7 deferred prerequisite work register:** if successor cycle authorizes canonical Bailey-López de Prado DSR scope, Path A (DSL-canonical-hash ↔ run_id mapping) requires building the audit_v1-16-char ↔ experiments.db-64-char identifier bridge, AND requires resolving the 4–7 multiplicity-per-candidate question (which experiments.db run is "the" canonical run for a given audit_v1 candidate?). Path B (audit_v1 re-run with `--persist-trades`) avoids both questions but requires engine re-run effort. Both paths are out-of-scope at PHASE2C_11; documented for successor-cycle planning.

---

## §4 Module scope decision — extend `backtest/evaluate_dsr.py`

Per [PHASE2C_11_PLAN §4.5] adjudication (locked at sub-spec register):

> "Adjudication: extend `backtest/evaluate_dsr.py` with new function `compute_simplified_dsr()` per §4.3 procedure; existing `compute_expected_max_sharpe()` and `evaluate_trials()` preserved structurally with RS-3 guard call additions per §2.5."

**Step 1 ratification of module scope decision:**

- Existing module surveyed at `backtest/evaluate_dsr.py` (275 lines):
  - `compute_expected_max_sharpe(n_trials)` at line 39 — implements `sqrt(2 * ln(N))` per Bonferroni heuristic.
  - `evaluate_trials(sharpe_ratios)` at line 57 — applies threshold to a Sharpe-ratio dict.
  - `query_sharpe_ratios(...)` at line 110 — queries experiments.db (NOT used at PHASE2C_11; audit_v1 input register is filesystem JSON, not experiments.db).
  - `print_report(evaluation)` at line 162 — text reporter.
  - `main()` at line 215 — CLI entry.
- Module docstring already explicitly disclaims canonical Bailey-López de Prado DSR (lines 12-17): *"It does NOT implement the full Bailey-López de Prado Deflated Sharpe Ratio... If production-grade DSR is needed, it will be a dedicated effort with proper statistical review."* This aligns with §4.1 simplified-DSR-variant register-class lockpoint.
- Step 3 implementation extends this module with `compute_simplified_dsr()` per §4.3 procedure; existing functions gain RS-3 guard call additions before any audit_v1 input consumption (per §2.5 lockpoint).
- New module `backtest/dsr.py` is NOT created at PHASE2C_11 simplified MVD scope (per §4.5: "Canonical Bailey-López de Prado at deferred prerequisite scope WOULD warrant new module `backtest/dsr.py` if/when canonical scope fires at successor cycle; not at PHASE2C_11 simplified register").

**Module scope decision adjudicated CLEAN at Step 1.**

---

## §5 Step 1 closure verdict + reviewer routing

### §5.1 Closure status against §7.2 Step 1 gating criteria (v2 post-patch)

| §7.2 criterion | Status |
|---|---|
| artifact inventory clean | **CLEAN** (§1.1) |
| lineage verification clean | **CLEAN** (§1.4) |
| RS-2 guard call demonstrated | **CLEAN** (§1.2 — 198/198 pass) |
| cross-validation diagnostics clean | **CLEAN at v3.1 patched register** (§2.2 — re-verification at 1e-6 tolerance produced 0 disagreements across 198 × 5 columns; v3.1 reframing as descriptive consistency sanity-check ratified by Charlie-authorized option (b)) |
| α-Refine deliverable component complete | **CLEAN at v3.1 patched register** (§2.3 + §3 — empirical numbers corrected to 854/198 with multiplicity profile; Path A/B forward-pointing added) |
| module scope decision adjudicated | **CLEAN** (§4) |
| reviewer authorization at sealed register | **PENDING** (post-patch reviewer pass on this v2 deliverable; ChatGPT structural + advisor substantive; Codex skip per §8.1) |

**Net: Step 1 inventory pillars CLEAN at all six register layers under v3.1 patched register; Charlie-register authorized v3.1 patch slate per option (b) reviewer-ratified reframing; reviewer pass on this v2 deliverable + Charlie-register seal authorization remain operational steps before Step 2 fires.**

### §5.1.1 v3.1 patch audit trail

| Patch | Site | v3 → v3.1 | Authorization |
|---|---|---|---|
| Instance 5 patch (1/3) | §3.5 line 230 | `≈ 3.0688` → `≈ 3.2522` + audit annotation | ChatGPT + advisor + Charlie-register |
| Instance 5 patch (2/3) | §3.6 line 248 | `≈ 3.0688` → `≈ 3.2522` + audit annotation | ChatGPT + advisor + Charlie-register |
| Instance 5 patch (3/3) | §4.3 line 303 | `≈ 3.0688` → `≈ 3.2522` + audit annotation | ChatGPT + advisor + Charlie-register |
| Instance 6 patch (1/2) | §3.4 line 224 | tolerance `1e-9` → `1e-6` + reframe to descriptive consistency sanity-check (NOT primary-exclusion); JSON canonical preserved | ChatGPT (1e-6 or 1e-5 range) + advisor (R1 verify-first; option (b) lean if scenario A; P2+precedent-doc objection at §0.4 integrity register) + Charlie-register (P2+precedent-doc ratified after advisor objection; tolerance adjudication 1e-6 by Claude Code per `feedback_reviewer_suggestion_adjudication.md`); admissible under **METHODOLOGY_NOTES §20 v2** (5 triggers; advisor L1-L5 fixes incorporated) at §20.5 Instance 1 |
| Instance 6 patch (2/2) | §4.4(5) line 350 | tolerance `1e-9` → `1e-6`; auto-exclusion removed; discrepancies reviewer-routed | same as Instance 6 patch (1/2); admissible under **METHODOLOGY_NOTES §20 v2** (5 triggers; advisor L1-L5 fixes incorporated) at §20.5 Instance 1 |
| METHODOLOGY_NOTES §20 v2 codification | new section appended after §19 | Strong-tier operating rule + **5 explicit triggers** (individually necessary, jointly sufficient) + §20.5 cumulative instance register with mandatory 5-field template + Instance 6 logged as Instance 1; advisor L1+L2+L3+L4+L5 fixes incorporated (T3/T2 contradiction resolved; T1 boundary at Step-2-end with explicit input-observation trade-off; T5 parameter calibration discipline added; one-patch-per-lockpoint promoted to Application checklist; polish items applied) | Charlie-register authorization on P2+precedent-doc path + β path "approved on both reviewer synthesis β" (this commit cycle); bundled per §20 Application checklist item 7 (codification fires at first instance) |
| Instance 7 patch | §7.1 line 572 | "246 runs > 198 distinct hashes" → "854 regime_holdout rows / 198 distinct 64-char SHA256 hashes; multiplicity {4: 149; 5: 39; 6: 7; 7: 3}" + Path A/B forward-pointer | ChatGPT + advisor + Charlie-register |

**Per `feedback_authorization_routing.md` hard rule:** Charlie-register authorization the canonical authority for these operational fires; reviewer convergence advisory only.

**Per `feedback_reviewer_suggestion_adjudication.md`:** ChatGPT specified "1e-6 or 1e-5"; Claude Code adjudicated 1e-6 (vs 1e-5) on register-precision grounds — empirical max |Δ| ≈ 5e-7 sits one order of magnitude below 1e-6, so 1e-6 catches CSV 6-decimal rounding cleanly without being so lax as to mask genuine engine-output divergence (1e-5 would permit 20× the empirical rounding floor). Adjudication recorded for audit register.

### §5.2 Reviewer routing per §8.1

Per [PHASE2C_11_PLAN §8.1] table for "Step 1 artifact inventory + RS guard verification" row:

| Reviewer | Routing | Rationale |
|---|---|---|
| ChatGPT | structural | Standard structural pass on Step 1 deliverable MD + §19 finding adjudication framing |
| Claude advisor | substantive | Substantive pass on §2 finding adjudication + §0.4/§7.3 hard-rule application + Instance 6 lockpoint-substance characterization |
| Codex | **SKIP** | Per §8.1 "fires if RS guard implementation involves new code; skip if pure verification". No new RS guard code at Step 1; only existing `check_evaluation_semantics_or_raise()` invocation. Per `feedback_codex_review_scope.md` user-memory: scoping/verification deliverables skip Codex. |

### §5.3 Adversarial pre-registration check per §8.4

Reviewers should adversarially scrutinize whether the §19 finding adjudication framing is itself rigor theater:

- Does §2.1 Instance 5 framing as "docs-typo magnitude" understate the defect-class? Counterargument: the spec lockpoint substance is the formula `sqrt(2*ln(N))`, which is correct; only the cited approximation is wrong. Step 3 implementation operates from formula, not from cited approximation. Counter-counterargument: the cited approximation appears at four sites including §3.6 + §6.1 pass/fail interpretation register, and any reader of the spec at face value would believe the threshold is 3.0688; this is more than a docs typo if it changes how a reader interprets the pass/fail criterion at sub-spec read register.
- Does §2.2 Instance 6 framing as "lockpoint-substance defect" overstate the defect-class? Counterargument: the cross-validation lockpoint at §3.4 + §4.4(5) is a sanity check, not a primary computation lockpoint; the canonical scalar register is the JSON per §3.3, which is uniformly available + RS-attestation-clean across all 198 candidates. Counter-counterargument: §0.4 hard rule explicitly forbids mid-arc adjustment of any §3 lockpoint regardless of how peripheral the lockpoint feels in retrospect; the discipline is the discipline.
- Does §2.3 Instance 7 framing as "no §0.4 trigger" understate the defect at canonical-numerical-precision register? Counterargument: the α-Refine deliverable operates at descriptive register only per §7.1 explicit statement; the empirical numbers update; lockpoint substance unaffected. Counter-counterargument: 246 vs 854 is a 3.5x discrepancy in claim magnitude; if other "descriptive-register-only" claims in the spec are similarly off by 3.5x, the spec's empirical anchor at canonical-numerical-precision register is questionable.

These adversarial questions are surfaced for reviewer routing; Step 1 deliverable does NOT pre-resolve them.

### §5.4 Step 2 fire gate (v2 post-patch)

Per [PHASE2C_11_PLAN §7.3] hard rule: "Steps 2-5 MUST NOT fire before this sub-spec ... seals at register-precision register." Sub-spec sealed at v3 commit `c5b740c` with v3.1 in-arc patches authorized by Charlie-register at this Step 1 cycle (option (b) reviewer-ratified reframing; both reviewers converged; Charlie ratified patch slate).

**Step 2 fire-gate disposition: AUTHORIZED PENDING (i) reviewer pass on this v2 deliverable + (ii) Charlie-register seal authorization on Step 1 deliverable + sub-spec patch commit.**

Sequence to operational fire:

1. **Reviewer pass on v2 deliverable** — ChatGPT structural + Claude advisor substantive (per §8.1 routing); Codex skip (no new RS guard code; pure verification + post-patch documentation update).
2. **Charlie-register seal authorization** — bundling sub-spec v3.1 patch commit + Step 1 deliverable v2 commit per §7.4 audit-trail discipline; per `feedback_authorization_routing.md` hard rule, only Charlie-register messages constitute authorization for operational fires.
3. **Step 2 fires post-seal** — `compute simplified DSR-style screen inputs` per §7.1 Step 2 lockpoints; eligible-subset N (post-§4.4(1) `T_c < 5` exclusion) = 154 candidates anticipated based on Step 1 distribution descriptors at §1.6.

**Note on §0.4 strict-path interaction with v3.1 patches + METHODOLOGY_NOTES §20 codification:** §0.4 strict path applies to "post-result review surfaces evidence that a §3 lockpoint was mis-specified". The v3.1 patches operate at **pre-result register** (no DSR-style screen results computed; only Step 1 inventory verification fired). The advisor's substantive objection at register-precision was load-bearing: bare in-arc reframe without explicit codification would silently weaken §0.4 at first ambiguous case, converting the strict literal reading into case-by-case judgment register. METHODOLOGY_NOTES §20 v2 codification at this same arc closes that gap by articulating **five explicit triggers** (advisor L1+L2+L3+L4+L5 fixes incorporated post-§20-v1 substantive pass) under which an in-arc patch is admissible without weakening the post-hoc adjustment defect class §0.4 forbids. Instance 6 verified at all five §20 triggers (T1 pre-result Step 1 strict; T2 structural infeasibility 1e-9 vs 6-decimal CSV by-construction 100% exclusion; T3 no substantive pass/fail criterion change with boundary clarification at structurally-degenerate-filter; T4 full audit trail labeled commit pair v3 `c5b740c` → v3.1; T5 tolerance 1e-6 calibrated to canonical-artifact register-precision floor ~5e-7); logged at §20.5 cumulative instance register as Instance 1 with mandatory 5-field template. Charlie-register authorization on **P2+precedent-doc** path (rejecting bare P2) is canonical; this deliverable records the full adjudication trail at register-precision per §5.1.1 + §1 anchor.

---

## §6 Cross-references

- [PHASE2C_11_PLAN.md](PHASE2C_11_PLAN.md) — sub-spec at v3 sealed at commit `c5b740c`; this Step 1 deliverable verifies §2.1-§2.6 inputs + §3 pre-registration lockpoints (verifies + surfaces defects) + §4.5 module scope decision.
- [PHASE2C_11_SCOPING_DECISION.md](PHASE2C_11_SCOPING_DECISION.md) — scoping decision sealed at `3cfa357`.
- [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) lines 263-394 — `check_evaluation_semantics_or_raise()` consumer-side helper (RS-2 guard).
- [`backtest/evaluate_dsr.py`](../../backtest/evaluate_dsr.py) lines 39-107 — existing Bonferroni heuristic screen module (extension target per §4.5).
- [`agents/hypothesis_hash.py:172-173`](../../agents/hypothesis_hash.py) — DSL canonical hash truncation (audit_v1 hash scheme source).
- [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) §19 — spec-vs-empirical-reality finding pattern (3 substantive instances at this Step 1 cycle + 1 self-§19 in deliverable v1 → v2; cumulative count at PHASE2C_11 = 8 through Step 1).
- [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) **§20** — Pre-result lockpoint mis-specification documented exception path under arc-level anti-p-hacking guardrails; **§20 v2 codified at this Step 1 arc** (incorporating advisor L1+L2+L3+L4+L5 fixes from substantive pass on §20 v1 wording); **5 explicit triggers** (individually necessary, jointly sufficient) + §20.5 cumulative instance register with mandatory 5-field template + Instance 6 (this cycle) as §20.5 Instance 1; Strong tier; Charlie-register authorized on P2+precedent-doc path + β path.
- [CLAUDE.md "Hard rule for any future WF-consuming work"](../../CLAUDE.md) — RS-2/RS-3 consumer-side helper call requirement source.

---

**End of working draft.** Reviewer routing per §5.2 + Charlie-register adjudication per §5.4 next operational step.
