# PHASE2C_11 Plan — Statistical-Significance Machinery (Q-9.A) Sub-Spec

**Status: WORKING DRAFT v3 (post-canonical-artifact-mapping rewrite) — pre-seal; anchor-prose-access discipline (METHODOLOGY_NOTES §16) fires at this sub-spec seal register before seal.**

**Anchor:** PHASE2C_11 scoping decision sealed at commit `3cfa357` ([`docs/phase2c/PHASE2C_11_SCOPING_DECISION.md`](PHASE2C_11_SCOPING_DECISION.md)); Phase Marker advance commit `d894e69` on origin/main.

**v3 framing note:** prior in-session-only working drafts (v1 + v2; not committed) authored at structural-summary register against unverified canonical-source claims. Empirical verification at canonical-artifact register surfaced four substantive verification gaps documented at §0.5 as §19 spec-vs-empirical-reality finding pattern instances. v3 is the substantive rewrite at canonical-artifact-register-verified scope. **Primary MVD scope at v3 is simplified DSR-style multiple-testing Sharpe deflation screen against audit_v1 scalar register** (not full Bailey-López de Prado canonical DSR; canonical formulation deferred to post-PHASE2C_11 prerequisite work register per §4.1 + §4.7). The selection register at PHASE2C_11_SCOPING_DECISION.md §4.2 named "DSR machinery as MVD"; that selection is preserved at simplified-DSR-variant register-class. Canonical Bailey-López de Prado is *deferred prerequisite*, NOT primary MVD scope at PHASE2C_11.

---

## §0 Document scope and structure

### §0.1 Scope

This plan covers PHASE2C_11's implementation arc: statistical-significance machinery applied to the PHASE2C_8.1 evaluated candidate set at audit_v1 evaluation register.

**Scope register-class (revised at v3 per canonical-artifact register reality):**

- **In scope (MVD):** **simplified DSR-style multiple-testing Sharpe deflation screen** against audit_v1 candidate set (n=198) using `holdout_summary.json` scalar metrics. Specifically: per-candidate Sharpe scalar + cross-trial Sharpe variance + Bonferroni-style heuristic threshold per existing [`backtest/evaluate_dsr.py`](../../backtest/evaluate_dsr.py) precedent + extension with cross-trial-Sharpe-variance-based deflation. **NOT full Bailey-López de Prado canonical DSR** (per-candidate skewness/kurtosis/autocorrelation correction requires per-trade returns not available at audit_v1 register; see §0.5 Instance 1 + Instance 4 + §2.3 + §4.1).
- **Deferred prerequisite (post-PHASE2C_11 if results warrant):** canonical Bailey-López de Prado DSR with skewness/kurtosis/autocorrelation correction. Requires either (a) verified DSL-canonical-hash ↔ run_id mapping infrastructure between audit_v1 (16-char) and experiments.db (64-char) hash schemes OR (b) audit_v1 evaluation re-run with `--persist-trades` flag to produce per-candidate trade CSVs at audit_v1 register. See §4.1 + §4.7.
- **Stretch register (if MVD lands clean):** PBO machinery if simplified MVD spec lands clean and bandwidth permits per scoping doc §6.1.
- **Explicitly out of MVD scope:** canonical Bailey-López de Prado DSR (deferred per above); CPCV; Stationary Bootstrap (Politis-Romano 1994); engine re-run at audit_v1 with --persist-trades.
- **Explicitly out of arc scope:** new mining batches, new strategy generation, new evaluation runs at calibration-varied gates, mechanism-reconstruction work at depth greater than PHASE2C_9 §3 light-touch register, Phase 3 progression decisions.

### §0.2 Structure

§1 resolves filename + document-type framing per anti-pre-naming convention. §2 enumerates locked inputs from PHASE2C_8.1 + audit_v1-only canonical-artifact register (corrected at v3). §3 carries the pre-registration block at register-precision: candidate population + trial count + return metric + Sharpe estimation method + null/deflation assumptions + pass/fail interpretation, all locked BEFORE any result is computed. §4 specifies the simplified DSR-style screen formula + edge-case handling + explicit canonical-DSR deferral. §5 adjudicates trial-count treatment with §3.7 backlog cross-reference. §6 specifies result interpretation with explicit signal-evidence / artifact-evidence / inconclusive boundaries pre-registered, plus symmetric register-class discipline + §3.8 + §3.2 backlog cross-references. §7 specifies the implementation activity register with RS guard call lockpoints. §8 specifies reviewer routing including Codex requirement at code/spec interface. §9 documents cross-references.

### §0.3 Discipline anchors operating at this drafting cycle

Seven disciplines operate at this plan's drafting cycle and at the implementation arc that follows:

- **Anchor-prose-access discipline (METHODOLOGY_NOTES §16).** Fires at this sub-spec seal register; dual-reviewer pass requires reviewer access to actual prose, not summary or structural overview alone.
- **Procedural-confirmation defect class (METHODOLOGY_NOTES §17).** Working-draft commit before substantive prose-access pass is the defect class; this plan's seal fires AFTER dual-reviewer pass clears, not before. Application sub-rule 4 (full-file prose-access pass at sealed-commit register) applies.
- **Anti-momentum-binding discipline.** Per scoping doc §4.5: reviewer-lean inputs are scoping-cycle-input not selection. At sub-spec register: technical-decision lean is input not lock; per-axis pre-registration produces values at register satisfaction.
- **Anti-pre-naming discipline.** Successor cycle direction post-PHASE2C_11 implementation arc is NOT pre-committed at this plan's draft fire; carries forward per scoping doc §6 deferral.
- **Empirical verification discipline (METHODOLOGY_NOTES §1; PHASE2C_11 v1→v2→v3 rewrite operationalized this discipline at four canonical-artifact-register layers per §0.5).** File-structure citations + canonical-formula citations + data availability claims + canonical-project-convention compliance + canonical-artifact-mapping verification fired at canonical artifact register before sub-spec authoring fire. The v1→v2→v3 rewrite chain is the empirical anchor for this discipline at PHASE2C_11 register.
- **Spec-vs-empirical-reality finding pattern (METHODOLOGY_NOTES §19).** Per §0.5, four substantive instances at PHASE2C_11 sub-spec authoring register-class document the catch-class coverage architecture's verification register enumeration gap.
- **Section RS corrected-engine consumer-side discipline (RS-1; per [TECHNIQUE_BACKLOG.md §2.2.3](../../strategies/TECHNIQUE_BACKLOG.md) + CLAUDE.md "Hard rule for any future WF-consuming work").** All consumers of WF artifacts must call `check_wf_semantics_or_raise(summary, artifact_path=...)` from [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py); all consumers of single_run_holdout_v1 attestation domain artifacts must call companion `check_evaluation_semantics_or_raise()`. PHASE2C_11 consumes audit_v1 single_run_holdout_v1 artifacts; consumer-side helper call requirement applies at every Step that reads audit_v1 holdout_summary.json or experiments.db runs table per §7.1 lockpoints.

### §0.4 Process note — anti-p-hacking discipline at sub-spec register

The pre-registration block at §3 is the load-bearing anti-p-hacking guardrail at this arc. Any post-result parameter adjustment to the §3 lockpoints — candidate population, trial count, return metric, Sharpe estimation method, null/deflation assumptions, pass/fail interpretation — is **forbidden at register-precision register** per scoping doc §4.2.

If post-result review surfaces evidence that a §3 lockpoint was mis-specified at sub-spec drafting cycle, the resolution path is: (a) document the mis-specification at full register-precision; (b) treat affected results as **inconclusive at PHASE2C_11 register**, not as adjusted-pass or adjusted-fail; (c) defer to post-PHASE2C_11 successor cycle for re-specification.

This is the discipline that distinguishes PHASE2C_11 from rigor theater: the test commits to its parameters before knowing the answer.

### §0.5 §19 instance documentation — four canonical-artifact-register verification gaps

This sub-spec authoring cycle produced **four** §19 spec-vs-empirical-reality finding pattern instances. Each surfaced more fundamental defect than the prior; each fired at a distinct *verification register-class*. Documented at observation-only register; load-bearing for §19 cross-cycle accumulation register-class characterization at successor methodology consolidation cycle.

**Instance 1 (v1 → v2 rewrite; canonical-artifact register):**
- Spec-stated claim (v1 §2.3): "per-candidate return time series NOT exposed at evaluation gate artifact register"
- Empirical reality: per-trade returns ARE available at `data/results/trades_<run_id>.csv` (mining-batch outputs)
- Verification register: canonical-artifact register (filesystem inventory)
- Resolution: v1 invalidated; v2 substantive rewrite at canonical-formulation register

**Instance 2 (v2 → v3 rewrite; canonical-project-convention register):**
- Spec-stated claim (v2): consumer-side helper call requirement absent from sub-spec
- Empirical reality: TECHNIQUE_BACKLOG.md §2.2.3 + CLAUDE.md "Hard rule" mandate consumer-side helper calls (`check_wf_semantics_or_raise()` / `check_evaluation_semantics_or_raise()`) at every consumer of WF / single-run-holdout artifacts
- Verification register: canonical-project-convention register (project documentation cross-check)
- Resolution: RS-1 / RS-2 / RS-3 patches added at v3

**Instance 3 (advisor β-Refine recommendation at structural-precision register):**
- Spec-stated claim (advisor full-prose-access pass): |delta| < 1e-6 cross-validation tolerance might be tight at numerical-precision register; recommended β-Refine direction
- Empirical reality: advisor recommendation operated at structural-precision register without firing canonical-numerical-precision verification at `backtest/metrics.py` Sharpe computation register
- Verification register: canonical-numerical-precision register (empirical sanity probe at canonical-artifact register)
- Resolution: β verification probe fired; surfaced Instance 4 directly

**Instance 4 (v2 → v3 rewrite; canonical-artifact-mapping register; LOAD-BEARING for sub-spec scope):**
- Spec-stated claim (v2 §2.4): partition mapping policy queries `experiments.db` `runs` table by hypothesis_hash to produce canonical run_id per audit_v1 candidate
- Empirical reality at canonical-artifact register:
  - audit_v1 hypothesis_hash = 16-char truncated DSL canonical hash per `agents/hypothesis_hash.py:172-173`
  - experiments.db hypothesis_hash = 64-char SHA256 of *different canonical input*
  - The two hash schemes are independent identifier registers; audit_v1 hash `95bf56e74564ea34` is NOT a prefix of any experiments.db hash
  - audit_v1 evaluation gate produces ONLY `holdout_summary.json` (scalar metrics) per candidate; NO per-trade CSVs
  - Trade CSVs at `data/results/trades_<run_id>.csv` belong to mining-batch walk-forward / regime_holdout runs at *different evaluation register-class* (multi-period train/test boundaries, not single bear_2022 holdout)
  - Strategy name population matches across audit_v1 and experiments.db (167 unique names ∩ 167; some name collisions due to auto-generated names)
- Verification register: canonical-artifact-mapping register (cross-artifact identifier scheme cross-check + per-artifact-register data availability cross-check)
- Resolution: v3 substantive rewrite at simplified DSR-style screen scope; canonical Bailey-López de Prado DSR moved to deferred prerequisite per §0.1 + §4.1 + §4.7

**Verification register enumeration observation (forward-pointing for §19 cross-cycle accumulation register-class characterization at successor methodology consolidation cycle):**

The four instances at this cycle empirically support a structural observation: catch-class coverage at sub-spec authoring requires *explicit verification register enumeration* before draft authoring fires:

- **Canonical-artifact register**: do referenced files/databases exist with claimed structure?
- **Canonical-project-convention register**: does spec align with CLAUDE.md hard rules + TECHNIQUE_BACKLOG.md?
- **Canonical-mapping register**: do referenced cross-artifact identifiers map correctly?
- **Canonical-formula register**: do formulas match published references? (γ concern routed to Codex Step 3 per §8.2)
- **Canonical-numerical-precision register**: do empirical values fit lockpoint tolerances?

Each register catches distinct defect class. Comprehensive coverage requires each register firing. The defect class of "spec authoring at structural-summary register without canonical-source verification" can operate at any register-class; comprehensive coverage requires explicit per-register firing decision.

This observation is forward-pointing for §19 cross-cycle empirical record + potential §16 ### Failure-mode signal extension at successor methodology consolidation cycle scoping consideration. NOT load-bearing for current PHASE2C_11 cycle's seal at this register; documented for forward-looking discipline.

---

## §1 Filename and document-type lock (anti-pre-naming option (ii) resolution)

### §1.1 Filename decision

**Filename: `docs/phase2c/PHASE2C_11_PLAN.md`** (this document).

Resolution per anti-pre-naming option (ii). Convention precedent (PHASE2C_6/7/8/9/10 _PLAN.md) + single-arc scope + cross-reference grep stability.

### §1.2 Document-type framing

This plan's deliverable register is **arc-level implementation spec at technical-spec register-class**. Authorship register is canonical-spec (load-bearing structural commitments + technical lockpoints). Verification register is dual-reviewer pass (ChatGPT structural + Claude advisor substantive prose-access) plus Codex adversarial review at the code/spec interface per scoping doc §7.2 + feedback-codex-review-scope memory.

Discipline alignment: §10 anti-pre-naming applies to filename + successor cycle direction. §16 anchor-prose-access applies at this plan's seal cycle. §17 procedural-confirmation defect class applies. §1 + §15 + §19 disciplines applied at v1→v2→v3 rewrite chain per §0.5.

---

## §2 Locked inputs

### §2.1 Candidate universe

**Canonical candidate population: PHASE2C_8.1 evaluated candidate set, n=198 distinct DSL-canonical-hash candidates** at audit_v1 evaluation register, identifier scheme = 16-char truncated DSL canonical hash per `agents/hypothesis_hash.py`.

Source artifact citations:

- **Aggregate CSV:** [`data/phase2c_evaluation_gate/audit_v1/holdout_results.csv`](../../data/phase2c_evaluation_gate/audit_v1/holdout_results.csv) (198 candidate rows + header)
- **Per-candidate JSON:** [`data/phase2c_evaluation_gate/audit_v1/<hypothesis_hash>/holdout_summary.json`](../../data/phase2c_evaluation_gate/audit_v1/) — 198 directories; each contains scalar metrics (sharpe_ratio, total_return, max_drawdown, total_trades, wf_test_period_sharpe), evaluation_semantics, engine_commit, source_batch_id, lifecycle_state, lineage_check, name, theme, position
- **Filtered set (post-trade-margin filter):** [`audit_v1_filtered/`](../../data/phase2c_evaluation_gate/audit_v1_filtered/) (148 candidates ≥20 trades)
- **Multi-regime artifacts (PHASE2C_8.1):** `audit_2024_v1`, `eval_2020_v1`, `eval_2021_v1` directories — same n=198 at additional regimes; descriptive register only at PHASE2C_11

### §2.2 Source batch and engine lineage

- **source_batch_id:** `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` (Phase 2C Phase 1 walk-forward; corrected-engine canonical)
- **engine_commit:** `eb1c87f` (corrected WF engine; tag `wf-corrected-v1`)
- **engine_corrected_lineage:** `wf-corrected-v1`
- **evaluation_semantics:** `single_run_holdout_v1` (PHASE2C_6 attestation domain)

All n=198 candidates share these lineage fields; verified at PHASE2C_8.1 closeout register. Section RS corrected-engine consumer-side helper call requirement applies (per §0.3 anchor + §7.1 Step lockpoints).

### §2.3 Available data per candidate (canonical artifact register verified at v3)

**Per-candidate scalar metrics (`holdout_summary.json`):** sharpe_ratio, total_return, max_drawdown, total_trades, wf_test_period_sharpe.

**Per-candidate per-trade returns at audit_v1 register: NOT AVAILABLE.** Per Instance 4 of §0.5: audit_v1 evaluation gate produces ONLY scalar holdout_summary.json output per candidate; per-trade CSVs are NOT generated at audit_v1 register-class.

**Per-trade returns at experiments.db register: AVAILABLE for mining-batch walk-forward / regime_holdout runs**, but at *different evaluation register-class* than audit_v1:
- Path: `data/results/trades_<run_id>.csv` keyed to experiments.db run_id (UUID format)
- Hash scheme mismatch: experiments.db hypothesis_hash (64-char SHA256) ≠ audit_v1 hypothesis_hash (16-char DSL); no trivial cross-register mapping
- Semantic mismatch: mining-batch trades span 2020-2024 walk-forward windows; audit_v1 holdout = single-run bear_2022 only
- Therefore: experiments.db trade CSVs are NOT canonical-artifact-register inputs for PHASE2C_11 audit_v1 DSR computation

**Implication:** canonical Bailey-López de Prado DSR (which requires per-trade skewness/kurtosis/autocorrelation correction inputs) is **infeasible at audit_v1 register without prerequisite work** (DSL-canonical mapping infrastructure OR audit_v1 re-run with --persist-trades). v3 MVD scope at simplified DSR-style screen reflects this canonical-artifact register reality honestly per §0.1 + §4.1.

### §2.4 Partition mapping at simplified MVD register (revised at v3)

**Simplified MVD scope avoids cross-register mapping problem entirely.** Primary partition mapping at v3:

- audit_v1 hypothesis_hash (16-char DSL) → audit_v1/<hash>/holdout_summary.json (direct directory mapping)
- Per-candidate Sharpe scalar = holdout_metrics.sharpe_ratio (consumed unchanged from engine output)
- No cross-mapping to experiments.db required at simplified MVD register
- No per-trade CSVs consumed at simplified MVD register

**Step 1 partition audit deliverable per §7.1**: verify all 198 audit_v1 directories contain holdout_summary.json with required scalar fields; verify lineage_check = 'passed' at all 198 candidates per Section RS guard; document any missing/malformed candidates with exclusion reason.

**Cross-register mapping (audit_v1 ↔ experiments.db) explicitly out of MVD scope.** If post-PHASE2C_11 successor cycle adjudicates canonical Bailey-López de Prado DSR scope, the mapping infrastructure is prerequisite work register; not in PHASE2C_11 implementation arc.

### §2.5 Existing DSR module — RS-3 patch

[`backtest/evaluate_dsr.py`](../../backtest/evaluate_dsr.py) implements a Bonferroni-style heuristic screen using `SR_threshold = sqrt(2 * ln(N))`. The module's docstring explicitly notes: *"It does NOT implement the full Bailey–López de Prado Deflated Sharpe Ratio... If production-grade DSR is needed, it will be a dedicated effort with proper statistical review."*

**RS-3 patch lockpoint (per [TECHNIQUE_BACKLOG.md §2.2.3](../../strategies/TECHNIQUE_BACKLOG.md) corrected-engine dependency):** the existing `evaluate_dsr.py` heuristic screen MUST be updated to call `check_evaluation_semantics_or_raise()` from [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) before its first use against any audit_v1 holdout_summary.json artifacts (single_run_holdout_v1 attestation domain). PHASE2C_11 implementation arc operationalizes this update at Step 2 / Step 3 (any function consuming audit_v1 summaries fires the consumer-side helper before reading scalars).

PHASE2C_11 simplified DSR-style screen (per §4) extends `evaluate_dsr.py` with new function `compute_simplified_dsr()` that operates at audit_v1 scalar register with RS-3 guard call lockpoint. Existing `compute_expected_max_sharpe()` and `evaluate_trials()` functions also gain RS-3 guard calls before consuming any audit_v1 input.

### §2.6 No new mining, no new strategy generation, no new evaluation, no engine re-run

Per scoping doc §0.1 + §1.4 constraints + §6.1 hard scope:

- No new mining batches (no API spend; no Proposer/Critic invocations)
- No new strategy generation
- No new evaluation runs at calibration-varied gates (path (c) work explicitly out of PHASE2C_11 scope)
- No mechanism-reconstruction work at depth greater than PHASE2C_9 §3 light-touch register (path (a) work explicitly out of PHASE2C_11 scope)
- **No engine re-run at audit_v1 with --persist-trades** (Instance 4 §0.5 prerequisite work; explicitly deferred to post-PHASE2C_11 if canonical DSR scope warrants)

Implementation arc operates against existing audit_v1 scalar artifacts only; computation is local-CPU statistical machinery (no external API; no new data collection; no engine invocation).

---

## §3 Pre-registration block (anti-p-hacking guardrail; load-bearing)

This section is the **load-bearing anti-p-hacking guardrail** per scoping doc §4.2. All values pre-registered here are LOCKED before any computation fires. Post-result adjustment forbidden per §0.4.

### §3.1 Candidate population

**Lockpoint: candidate population = PHASE2C_8.1 audit_v1 set, n=198 distinct DSL-canonical-hash candidates.**

Rationale: full population pre-trade-margin-filter is canonical because filter is downstream gate. The simplified DSR-style screen tests whether mining-process output produces signal distinguishable from null at the multiple-testing-adjusted register; underlying population is n=198.

**Sensitivity register (descriptive-only, NOT primary):** secondary computation against n=148 audit_v1_filtered set MAY be authored at sub-spec implementation arc as supplementary register; pass/fail interpretation per §6 lockpoints applies to n=198 primary register only.

**Subset application (canonical filter, pre-registered at §4.4):** candidates with `total_trades < 5` excluded from primary computation per §4.4 edge-case handling. Eligible-subset N reported at primary register; exclusion is pre-registered, not post-hoc adjustment.

### §3.2 Trial count

**Lockpoint: raw trial count N_raw = 198** (per §3.1, before §4.4 subset filter).

**Effective trial count N_eff:** see §5 adjudication. Conservative default policy: when correlation/dependency treatment is uncertain, **N_eff defaults to N_raw = 198** — most conservative for screen computation; produces highest deflation; produces lowest probability of signal-evidence pass; produces most-skeptical reading.

**P4 register-precision lockpoint:** primary uses raw N=198 as conservative over-deflation. Sensitivity register cannot override primary. If sensitivity register surfaces N_eff < 198 that would change pass/fail disposition, discrepancy documented at result register; primary register reads N_eff = 198.

### §3.3 Return metric

**Lockpoint: per-candidate Sharpe ratio sourced from audit_v1 `holdout_summary.json` `holdout_metrics.sharpe_ratio` field, consumed unchanged from engine output.**

Rationale: this is the canonical scalar at audit_v1 evaluation register at single_run_holdout_v1 attestation domain. The engine (`eb1c87f` corrected lineage) computed Sharpe at canonical formulation; PHASE2C_11 consumes engine output unchanged.

**Per-trade return time series at audit_v1 register: NOT AVAILABLE per §2.3** — therefore skewness/kurtosis/autocorrelation correction inputs cannot be computed at audit_v1 register; canonical Bailey-López de Prado DSR formulation is deferred prerequisite work per §0.1.

**Multi-regime sensitivity register only:** per-regime Sharpe scalars from `audit_2024_v1`, `eval_2020_v1`, `eval_2021_v1` available; multi-regime aggregation (mean / min / median across regimes) MAY be computed at sensitivity register; descriptive-only.

### §3.4 Sharpe estimation method

**Lockpoint: Sharpe ratio consumed unchanged from audit_v1 `holdout_summary.json` `holdout_metrics.sharpe_ratio` field.** Engine output at corrected lineage `eb1c87f` is canonical at PHASE2C_11 register; no re-computation from per-trade returns at primary register (per-trade returns not available per §2.3).

**No per-trade-derived Sharpe cross-validation at simplified MVD register.** v2 §3.4 cross-validation tolerance lockpoint (|delta| < 1e-6 between per-trade-derived and engine-output Sharpe) was authored against canonical Bailey-López de Prado scope; at simplified MVD scope, no per-trade derivation operates at primary register, so cross-validation operates at engine-vs-engine register only (i.e., audit_v1 evaluation engine output).

**Cross-validation register at simplified MVD (v3.1 reframed per Step 1 §19 Instance 6 + Charlie-authorized option (b) reviewer ratification; admissible under METHODOLOGY_NOTES §20 documented exception path with all five §20 triggers verified at canonical-artifact register — T1 pre-result Step 1 register; T2 structural infeasibility 1e-9 vs 6-decimal CSV by-construction 100% exclusion; T3 no substantive pass/fail criterion change; T4 full audit trail v3 commit `c5b740c` → v3.1; T5 tolerance 1e-6 calibrated to canonical-artifact register-precision floor ~5e-7):** per-candidate scalar consumed from audit_v1 holdout_summary.json (canonical source per §3.3) + cross-checked against `holdout_results.csv` aggregate CSV row for same hypothesis_hash. **The cross-check operates at descriptive consistency sanity-check register, NOT primary-exclusion lockpoint substance.** If per-candidate JSON-vs-CSV scalar differs by |delta| > 1e-6, the discrepancy is documented at result register and reviewer-routed for substantive interpretation; candidate is NOT auto-excluded from primary computation unless the discrepancy is materially larger than CSV's 6-decimal storage register-precision (~5e-7 max rounding). Rationale: prior v3 lockpoint at |delta| > 1e-9 was authored against canonical Bailey-López de Prado per-trade-derived register-class (where JSON full-precision vs JSON full-precision cross-check is the comparison); at simplified MVD scope, the cross-validation comparison is JSON full-precision vs CSV 6-decimal-rounded — the 1e-9 tolerance was incompatible with CSV storage register and would have excluded all 198 candidates by construction. The 1e-6 threshold preserves anti-p-hacking discipline (CSV-storage rounding artifacts at ~5e-7 register pass; genuine engine-output divergence at ≥1e-6 surfaces for adjudication) while keeping the cross-check as descriptive sanity, not primary lockpoint. **JSON remains the canonical scalar source per §3.3 lockpoint (unchanged).**

### §3.5 Null / deflation assumptions (simplified DSR-style screen)

**Lockpoint: simplified DSR-style multiple-testing Sharpe deflation screen** combining:

1. **Bonferroni-style threshold (existing `evaluate_dsr.py` precedent):** `SR_threshold_Bonferroni = sqrt(2 * ln(N))` at N=198. Threshold value ≈ 3.2522 at N=198. (v3.1 patch per Step 1 §19 Instance 5 + Charlie-authorized reviewer ratification: prior cited approximation `≈ 3.0688` was empirically incorrect; formula lockpoint unchanged; only the cited numerical approximation corrected.)
2. **Cross-trial-Sharpe-variance-based deflation:** under null hypothesis, per-trial Sharpe ratios are independent draws from distribution centered at zero with variance estimated from empirical cross-trial Sharpe variance. The deflation factor adjusts the maximum observed Sharpe for multiple-testing bias.

**Pre-registered conservative omissions (data not available at audit_v1 register per §2.3):**

- **Skewness correction:** NOT APPLIED at primary register (per-trade returns not available; canonical Bailey-López de Prado correction deferred per §0.1)
- **Kurtosis correction:** NOT APPLIED at primary register (same reason)
- **Autocorrelation correction:** NOT APPLIED at primary register (same reason)
- **Cross-trial correlation in N_eff:** N_eff defaults to N_raw at primary register per §3.2

**Composite conservative-when-uncertain policy (revised at v3):** simplified DSR-style screen with raw N_eff + Bonferroni cross-check + cross-trial-Sharpe-variance deflation = bounded disambiguation register-class. Pass at simplified register provides bounded evidence at multiple-testing register; null result at simplified register does NOT entail "no signal exists in any register-class" (per §6.2 away-from-signal underclaiming guardrail).

**Honest register-class characterization:** the simplified screen operates at *bounded disambiguation register-class* relative to canonical Bailey-López de Prado. If primary register surfaces inconclusive result at simplified register, successor cycle adjudication MAY pursue canonical formulation as deferred prerequisite work register (per §0.1 + §4.7).

### §3.6 Pass/fail interpretation

**Lockpoint: pre-registered at this register, BEFORE computation fires.**

**Pass threshold (signal evidence at simplified register):** primary screen p-value < 0.05 at N=198 OR maximum observed Sharpe > Bonferroni threshold sqrt(2 × ln(198)) ≈ 3.2522. Both criteria reported; primary disposition = pass if BOTH cross-validate (conservative AND-gate at register-precision register). (v3.1 patch per Step 1 §19 Instance 5; cited numerical approximation corrected; formula lockpoint unchanged.)

**Fail threshold (artifact evidence at simplified register):** primary screen p-value ≥ 0.5 at N=198 AND maximum observed Sharpe ≤ median expected null Sharpe. Conservative AND-gate; both criteria must indicate artifact for primary disposition = fail.

**Inconclusive register:** any disposition not meeting strict pass-AND-gate or strict fail-AND-gate at simplified register. Includes: pass-by-one-criterion-only (p < 0.05 but Sharpe < Bonferroni; OR Sharpe > Bonferroni but p ≥ 0.05); intermediate p-values; criteria disagreement.

**Per scoping doc §5 guardrail 1 + §6.2 symmetric register-class discipline:** inconclusive is NOT pass-by-other-name and NOT fail-by-other-name. Successor cycle adjudication required.

**Statistical-evidence vs tradable-edge distinction (P5 patch):** signal evidence at PHASE2C_11 simplified register = signal-distinguishable-from-null at multiple-testing register at *bounded disambiguation register-class*. **NOT** = deployment-warrant. **NOT** = Phase 3 authorization. **NOT** = canonical-formulation-confirmed (which is deferred prerequisite per §0.1). Pass at PHASE2C_11 simplified register clears the existence-register at bounded-disambiguation register-class only; canonical-formulation confirmation + downstream adjudication (mechanism / calibration / Phase 3) are register-classes downstream of PHASE2C_11.

### §3.7 Pre-registration verification gate

Before any simplified DSR-style screen computation fires at implementation arc:

1. This §3 block must be sealed at sub-spec register (sub-spec sealed; reviewer authorization at sealed register).
2. Implementation arc must NOT fire computation before this §3 block seals.
3. Step 1 partition audit per §2.4 must complete before Step 2/3 fires.
4. RS guard calls (per §0.3 + §7.1) must operate before any audit_v1 artifact consumption.
5. If implementation arc surfaces evidence that a §3 lockpoint was mis-specified, resolution path per §0.4.

---

## §4 Simplified DSR-style screen specification

### §4.1 Formula source + canonical-DSR deferral

**Existing project precedent:** [`backtest/evaluate_dsr.py`](../../backtest/evaluate_dsr.py) Bonferroni-style heuristic screen using `SR_threshold = sqrt(2 * ln(N))`.

**Canonical reference (deferred prerequisite per §0.1):** Bailey, D. H., & López de Prado, M. (2014). "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality." *Journal of Portfolio Management*, 40(5), 94-107.

**v3 register lockpoint:** PHASE2C_11 implements **simplified DSR-style multiple-testing Sharpe deflation screen** at primary MVD register; **NOT** full Bailey-López de Prado canonical DSR. Canonical formulation deferred to post-PHASE2C_11 successor cycle if results warrant scope expansion + prerequisite work register fires (DSL-canonical mapping infrastructure OR audit_v1 --persist-trades engine re-run).

**Honest naming discipline (per ChatGPT P1 + canonical-artifact register reality):** result narratives at PHASE2C_11 primary register MUST refer to "DSR-style multiple-testing Sharpe deflation screen" or "simplified DSR variant"; MUST NOT refer to "canonical DSR" or "Bailey-López de Prado DSR" at primary register. Canonical-DSR phrasing reserved for deferred prerequisite scope per §4.7.

### §4.2 Inputs required (simplified MVD)

| Input | Source | Notes |
|---|---|---|
| `SR_c` per candidate | audit_v1 `holdout_summary.json` `holdout_metrics.sharpe_ratio` | Per-candidate Sharpe scalar (canonical from engine output) |
| `T_c` per candidate | same JSON `holdout_metrics.total_trades` | Per-candidate trade count (used for §4.4 edge-case filter) |
| `SR_observed` | array of SR_c across N eligible candidates | Cross-trial Sharpe distribution |
| `SR_max` | max(SR_observed) | Maximum observed Sharpe |
| `Var(SR)` | var(SR_observed across N candidates, ddof=1) | Cross-trial Sharpe variance (null distribution variance estimate) |
| `N` | 198 (per §3.2 lockpoint) | Trial count |

No per-trade returns; no skewness; no kurtosis; no autocorrelation. Simplified MVD operates at scalar register only.

### §4.3 Computation procedure (simplified DSR-style screen)

**Step 1 — Bonferroni-style threshold:**

```
SR_threshold_Bonferroni = sqrt(2 * ln(N))
```

At N=198: ≈ 3.2522. Observed `SR_max > SR_threshold_Bonferroni` indicates signal-distinguishable at Bonferroni heuristic register. (v3.1 patch per Step 1 §19 Instance 5; cited numerical approximation corrected; formula lockpoint unchanged.)

**Step 2 — Expected maximum Sharpe under null (Gumbel approximation; canonical Bailey-López de Prado E[max] without per-candidate skew/kurt/autocorrelation correction):**

```
E[max SR | null] = sqrt(Var(SR)) * ((1 - gamma_euler) * Phi^-1(1 - 1/N) + gamma_euler * Phi^-1(1 - 1/(N * e)))
```

where `gamma_euler ≈ 0.5772`, `Phi^-1` = inverse standard normal CDF, `e` = Euler's number.

**Step 3 — Per-candidate simplified DSR-style p-value:**

```
SE(SR_c) = sqrt(1 / (T_c - 1))   # simplified SE without skew/kurt/autocorrelation correction
z_c = (SR_c - E[max SR | null]) / SE(SR_c)
p_c = 1 - Phi(z_c)
```

Note: this SE formula assumes IID returns under null + no autocorrelation correction. Canonical Bailey-López de Prado SE formula with skewness/kurtosis/autocorrelation correction is deferred per §4.1.

**Step 4 — Per-candidate disposition per §3.6:**

```
Bonferroni_pass(c) = (SR_c > SR_threshold_Bonferroni)
DSR_style_pass(c) = (p_c < 0.05)
if Bonferroni_pass AND DSR_style_pass: signal_evidence
elif (NOT Bonferroni_pass) AND (NOT DSR_style_pass) AND (p_c >= 0.5): artifact_evidence
else: inconclusive
```

**Step 5 — Population-level disposition for SR_max:**

```
c_max = argmax(SR_observed)
population_disposition = disposition(c_max) per Step 4
```

The population-level result tests: is the **best** observed Sharpe statistically distinguishable from the expected best Sharpe under null + above Bonferroni threshold (conservative AND-gate)?

### §4.4 Edge case handling

Locked at sub-spec register:

1. **Low trade count (`T_c < 5`):** candidate excluded from primary computation. Pre-registered exclusion threshold; not post-hoc adjustment.
2. **Zero Sharpe (`SR_c = 0` due to no trades; T_c = 0):** candidate excluded.
3. **Missing or null Sharpe:** if `holdout_metrics.sharpe_ratio` missing/null, candidate excluded.
4. **Cross-trial variance Var(SR) = 0:** if exactly zero across eligible subset (extreme degenerate), screen undefined; result reported as inconclusive per §3.6.
5. **JSON-vs-CSV cross-validation discrepancy (per §3.4 v3.1 reframed register):** if scalar disagrees between holdout_summary.json and holdout_results.csv aggregate row by |delta| > 1e-6 (i.e., materially larger than CSV's 6-decimal storage register-precision rounding floor of ~5e-7), discrepancy documented at result register and reviewer-routed for substantive interpretation; candidate NOT auto-excluded unless the discrepancy is materially larger than storage-precision artifact. JSON remains canonical scalar source per §3.3. (v3.1 patch per Step 1 §19 Instance 6 + Charlie-authorized option (b) reviewer ratification; admissible under METHODOLOGY_NOTES §20 documented exception path with all five §20 triggers verified at canonical-artifact register including T5 parameter calibration discipline at canonical-artifact register-precision floor; cross-check reframed from primary-exclusion lockpoint to descriptive consistency sanity-check.)

### §4.5 Module scope decision (revised at v3)

**Adjudication: extend [`backtest/evaluate_dsr.py`](../../backtest/evaluate_dsr.py) with new function `compute_simplified_dsr()` per §4.3 procedure; existing `compute_expected_max_sharpe()` and `evaluate_trials()` preserved structurally with RS-3 guard call additions per §2.5.**

Rationale (revised from v2): at simplified MVD register, the new computation extends the heuristic screen module rather than introducing new module. Canonical Bailey-López de Prado at deferred prerequisite scope WOULD warrant new module `backtest/dsr.py` if/when canonical scope fires at successor cycle; not at PHASE2C_11 simplified register.

**API surface (locked at sub-spec register):**

```python
def compute_simplified_dsr(
    candidates: list[CandidateInput],  # per §4.2 inputs
    n_trials: int,                      # = 198 per §3.2 lockpoint
) -> SimplifiedDSRResult
```

where `CandidateInput` carries (hypothesis_hash, SR_c, T_c, audit_v1_artifact_path) and `SimplifiedDSRResult` carries per-candidate disposition + population-level disposition + Bonferroni cross-check + sensitivity table.

**RS guard call at function entry (RS-3):** `compute_simplified_dsr()` MUST call `check_evaluation_semantics_or_raise()` from `backtest/wf_lineage.py` for every audit_v1_artifact_path consumed; refuse processing if attestation domain check fails.

### §4.6 PBO stretch register (if simplified MVD lands clean)

If §4.1-§4.5 simplified DSR-style screen specification lands clean and implementation Step 4 (summary tables) surfaces results that warrant additional discipline at multiple-testing register, **PBO MAY fire at stretch register** per scoping doc §6.1.

PBO computation procedure pre-registered at this register (lockpoints if PBO fires):

- **Combinatorial structure:** combinatorially symmetric cross-validation per Bailey-López de Prado canonical
- **In-sample / out-of-sample split:** N=198 candidates split combinatorially over per-candidate Sharpe scalars; PBO measures rank consistency between IS and OOS
- **Pre-registered PBO threshold:** PBO < 0.5 at primary register = signal evidence; PBO ≥ 0.5 = artifact evidence (rank consistency below random)
- **RS guard:** PBO computation MUST call `check_evaluation_semantics_or_raise()` at every audit_v1 artifact consumption per RS-2 lockpoint

**PBO fires only if:** (a) simplified MVD lands clean (no spec drift; reviewer authorization); (b) implementation arc has bandwidth at stretch register; (c) Charlie-register authorization explicit at MVD seal cycle. If any condition fails, PBO deferred to post-PHASE2C_11 successor cycle.

### §4.7 Canonical Bailey-López de Prado DSR — explicitly deferred prerequisite

**Out of MVD scope at PHASE2C_11.** Per §0.1 + §0.5 Instance 4: canonical Bailey-López de Prado DSR formulation requires per-candidate skewness/kurtosis/autocorrelation correction inputs computed from per-trade return time series. Per-trade returns at audit_v1 register are NOT AVAILABLE per §2.3 canonical-artifact register reality.

**Prerequisite work register for canonical DSR (deferred to post-PHASE2C_11 if successor cycle authorizes):**

- **Path A:** DSL-canonical-hash ↔ run_id mapping infrastructure between audit_v1 (16-char) and experiments.db (64-char) hash schemes. Substantial implementation work + carries semantic register-class shift (mining-batch trade time periods ≠ audit_v1 bear_2022 holdout time periods).
- **Path B:** Engine re-run at audit_v1 with `--persist-trades` flag (verify engine supports this flag; re-run 198 candidates; produce per-trade CSVs at audit_v1 register; verify re-run scalars match original audit_v1 scalars at canonical-artifact-consistency register).

Either prerequisite path is multi-arc work at successor cycle scope. Out of PHASE2C_11 register-class.

**CPCV explicitly out of MVD scope** per scoping doc §6.1; deferred to post-PHASE2C_11 if PBO results warrant.

**Stationary Bootstrap (Politis-Romano 1994) explicitly out of MVD scope** per backlog §2.2.1 (Phase 3 register placement; not Phase 2 register).

---

## §5 Trial-count adjudication

### §5.1 Raw N

**Raw N = 198** per §3.1 lockpoint; full PHASE2C_8.1 audit_v1 candidate population at distinct DSL-canonical-hash count; pre-trade-margin-filter; pre-§4.4 subset filter.

### §5.2 Correlation / dependency treatment (B-1 patch — backlog cross-reference)

PHASE2C_8.1 candidates were generated by mining process operating against:

- **5/6 theme rotation** (CLAUDE.md operational boundary)
- **Bounded factor library** (Phase 2A; registered factors at `factors/registry.py`)
- **Bounded DSL complexity budget** (entry/exit groups ≤ 3; conditions per group ≤ 4)

These structural properties induce cross-trial correlation. PHASE2C_9 §8.4 carry-forward register documented factor-set repetition rate ~28.79% across canonical mining batch — direct empirical evidence of cross-trial dependency.

**B-1 backlog cross-reference (per [TECHNIQUE_BACKLOG.md §3.7](../../strategies/TECHNIQUE_BACKLOG.md) Independent weak-signal composition):** "If features are correlated (which is almost always the case among quant signals), the multiplicative combination overstates joint confidence. Verify independence empirically (correlation matrix on raw signal series) before relying on multiplicative aggregation. In particular, signals derived from price / volume of the same asset are rarely independent."

This principle directly supports v3 §3.2 conservative N_eff = N_raw policy at primary register: PHASE2C_11 candidates derive from same OHLCV register; cross-trial dependency is real per §8.4 empirical evidence + backlog principle. Conservative N_eff treatment is the more-skeptical reading at canonical-discipline register.

**Conservative default lockpoint per §3.2:** N_eff defaults to N_raw = 198 at primary register.

### §5.3 Effective N at sensitivity register

**Sensitivity register only (NOT primary):** alternative N_eff values for sensitivity table per §5.4:

- N_eff = N_raw = 198 (conservative default; matches §3.2 primary lockpoint)
- N_eff = 5 (number of operational themes; very aggressive de-correlation)
- N_eff = 40 (~ 198 / 5 themes; aggressive de-correlation)
- N_eff = 80 (intermediate; moderate correlation proxy)

Descriptive-register only; primary uses N_eff = 198.

### §5.4 Sensitivity table specification

| N_eff | Bonferroni threshold | DSR-style p-value (max) | Disposition | Register |
|---|---|---|---|---|
| 198 (PRIMARY per §3.2) | sqrt(2*ln(198))≈3.07 | computed | per §3.6 | primary |
| 80 (sensitivity) | sqrt(2*ln(80))≈2.79 | computed | descriptive | sensitivity |
| 40 (sensitivity) | sqrt(2*ln(40))≈2.72 | computed | descriptive | sensitivity |
| 5 (sensitivity) | sqrt(2*ln(5))≈1.79 | computed | descriptive | sensitivity |

**Primary register reads ONLY N_eff = 198 row.** Other rows descriptive-only.

### §5.5 Conservative-when-uncertain policy at simplified MVD register

Composite policy at simplified MVD register:

- N_eff lockpoint = N_raw = 198 (most-skeptical reading)
- No skewness/kurtosis/autocorrelation correction (data unavailable at audit_v1 register; canonical-DSR deferred per §4.7)
- Strict pre-registered pass threshold = 0.05 (no "approaching significance" lenience per §6.2)
- Conservative AND-gate at §3.6 (both Bonferroni AND DSR-style p-value must indicate signal for primary signal disposition; both must indicate artifact for primary artifact disposition; otherwise inconclusive)

**Honest register-class characterization:** simplified MVD operates at *bounded disambiguation register-class* (per §3.5 + §6 + §0.5 Instance 4). Bounds set by canonical-artifact register reality at audit_v1 + simplified-formulation register-precision. Pass at simplified register provides bounded evidence; canonical-formulation confirmation is deferred prerequisite per §4.7.

This is the discipline that distinguishes simplified statistical-significance machinery from rigor theater: bounded register-class is acknowledged honestly at result interpretation register; pass at simplified register is NOT claimed as canonical-DSR pass.

---

## §6 Result interpretation

### §6.1 Pre-registered interpretation framework

Pre-registered at this register per §3.6 + §0.4 + scoping doc §5 guardrails:

**Signal evidence at simplified register:** primary screen p-value < 0.05 AND SR_max > sqrt(2*ln(198)) at N=198 (conservative AND-gate). Candidate Sharpe statistically distinguishable from null at simplified-formulation register-class.

**Artifact evidence at simplified register:** primary screen p-value ≥ 0.5 AND SR_max ≤ median expected null Sharpe at N=198 (conservative AND-gate). Candidate Sharpe consistent with selection-from-noise null at simplified-formulation register-class.

**Inconclusive register:** any disposition not meeting strict signal-AND-gate or strict artifact-AND-gate. Includes: pass-by-one-criterion-only; intermediate p-values; criteria disagreement.

### §6.2 Symmetric register-class discipline (γ patch + P5 patch)

**Both directions of register-class confusion at result interpretation register addressed:**

**Toward-signal overclaiming forbidden phrases (per scoping doc §5 guardrail 1):**

- "approaching significance"
- "trending toward signal"
- "marginal evidence"
- "directional support"
- "would be significant with more data"
- "consistent with signal at moderate-confidence register"

**Away-from-signal underclaiming forbidden phrases (γ patch):**

- "no signal exists"
- "definitively artifact"
- "mining process produces no signal"
- "Phase 3 trajectory permanently foreclosed"
- "candidate set is provably noise"

**Asymmetric concern at simplified register-class:** PHASE2C_11 simplified MVD tests existence at *bounded disambiguation register-class* — bounds set by §3 lockpoints + simplified-formulation register-precision per §3.5 + §4.1 + §4.7. Pass = signal distinguishable at simplified register; fail = not distinguishable at simplified register. Neither extreme inference (signal exists / no signal exists) is warranted by simplified-formulation alone — the test operates at bounded register-class.

**P5 patch — statistical evidence vs tradable edge:** signal evidence at simplified register does NOT authorize:

- Phase 3 progression
- Real-money deployment
- Deployment confidence at any operational register
- Mechanism-question closure (path (a)'s domain remains open)
- Calibration-question closure (path (c)'s domain remains open)
- Canonical-DSR-confirmed status (deferred prerequisite per §4.7)

**B-2 backlog cross-reference (per [TECHNIQUE_BACKLOG.md §3.8](../../strategies/TECHNIQUE_BACKLOG.md) Five-criteria anti-overfitting checklist):** Phase 3 deployment-readiness gate requires 5 additional criteria beyond statistical significance: (1) strong explainability + economic story; (2) fixed specificity (pre-specified parameter values); (3) low-dimensional composition (~5-6 core features); (4) long-term robustness (multi-year subsamples); (5) large sample (~1000+ trades minimum). Signal evidence at PHASE2C_11 simplified register satisfies NONE of these criteria automatically; backlog 5-criteria gate operates at distinct register-class downstream of PHASE2C_11.

**B-3 backlog cross-reference (per [TECHNIQUE_BACKLOG.md §3.2](../../strategies/TECHNIQUE_BACKLOG.md) Risk premium vs. genuine alpha distinction):** "Claimed excess return is often uncompensated tail risk in disguise (short vol structures, crash-sensitive longs). A high Sharpe before the tail event tells you nothing." Signal evidence at PHASE2C_11 simplified register does NOT distinguish genuine alpha from disguised tail risk; this distinction operates at separate register-class (Phase 3 deployment review per backlog framing).

### §6.3 Signal evidence interpretation register

If primary register lands at signal evidence (Bonferroni pass AND DSR-style p < 0.05 at N=198):

- Statistical-significance disambiguation resolves toward signal-distinguishable-from-null at simplified-formulation register-class
- Mechanism question (path (a)) becomes downstream-of-bounded-existence-resolved at this register; deeper mechanism reconstruction MAY warrant attention at successor cycle
- Calibration question (path (c)) downstream concern; calibration robustness investigation MAY warrant successor cycle
- **Canonical-DSR confirmation register (deferred prerequisite per §4.7)** becomes register-class-eligible for successor cycle adjudication; canonical Bailey-López de Prado at audit_v1 register-class would address skewness/kurtosis/autocorrelation correction-omission concerns from simplified register
- Phase 3 trajectory adjudication (path (f)) NOT register-class-authorized at PHASE2C_11 simplified register; explicit Charlie-register adjudication at successor cycle determines whether bounded simplified-register evidence + canonical-DSR confirmation + B-2 5-criteria gate + B-3 risk-premium-distinction are sufficient for Phase 3 progression

**Important register precision:** signal evidence at simplified register = signal-distinguishable-from-null at *bounded simplified-formulation register-class* at conservative N_eff. Does NOT entail tradable-edge register-class or canonical-formulation-confirmed register-class.

### §6.4 Artifact evidence interpretation register

If primary register lands at artifact evidence (Bonferroni fail AND DSR-style p ≥ 0.5 at N=198):

- Statistical-significance disambiguation resolves toward artifact at simplified-formulation register-class
- Mechanism / calibration / breadth / Phase 3 questions become downstream-of-non-result
- Path (f) Phase 3 trajectory at current candidate set is **foreclosed** for the current survivor set unless a later cycle identifies a different validated candidate basis (per scoping doc §4.3 path (f) wording)
- Successor cycle adjudication: either (a) accept artifact resolution at simplified register + retrospective on mining process at deeper register OR (b) breadth expansion at path (g) to identify potentially different validated candidate basis OR (c) canonical-DSR scope expansion (deferred prerequisite per §4.7) — though canonical confirmation of artifact register is unlikely to overturn simplified-register artifact reading

**Per §6.2 away-from-signal underclaiming guardrail:** artifact evidence at simplified register does NOT entail "no signal exists in any candidate set"; it entails "candidate set surveyed at PHASE2C_11 simplified register did not produce signal at simplified-formulation + conservative N_eff register." Different candidate basis OR canonical-formulation register MAY produce different result.

### §6.5 Inconclusive interpretation register

If primary register lands at inconclusive (any disposition not meeting strict pass-AND-gate or strict fail-AND-gate):

- Multiple-criteria disagreement OR intermediate p-values OR Bonferroni-vs-DSR-style disagreement
- Existence question unresolved at PHASE2C_11 simplified register
- **Successor cycle paths register-class-eligible (NOT pre-committed):**
  - Canonical-DSR scope expansion (deferred prerequisite per §4.7) — may resolve simplified-register inconclusive at canonical-formulation register
  - Mechanism deeper investigation (path (a))
  - Calibration variation (path (c))
  - Breadth expansion (path (g))
  - Phase 3 deferred until existence resolves

**Per anti-pre-naming option (ii):** specific successor path NOT pre-committed at PHASE2C_11 closeout; successor scoping cycle adjudicates at register satisfaction.

### §6.6 Bonferroni vs DSR-style cross-check disposition

Bonferroni heuristic + DSR-style p-value compute at primary register per §3.6 conservative AND-gate. If criteria disagree (one pass + one fail), disposition = inconclusive per §6.5.

Disagreement disposition documented at result table register; do not silently choose more-favorable result. Disagreement is itself empirical evidence at bounded simplified-register-class.

### §6.7 Result narrative canonical phrasing

If primary register lands at:

- **Signal evidence:** *"PHASE2C_11 primary register: signal evidence at simplified DSR-style screen (Bonferroni pass + DSR-style p < 0.05 at N=198, conservative N_eff). Existence-register resolves toward signal-distinguishable-from-null at bounded simplified-formulation register-class. Canonical Bailey-López de Prado confirmation deferred prerequisite. Tradable-edge + Phase 3 register-classes downstream and not authorized by this result. Successor cycle adjudication required."*
- **Artifact evidence:** *"PHASE2C_11 primary register: artifact evidence at simplified DSR-style screen (Bonferroni fail + DSR-style p ≥ 0.5 at N=198, conservative N_eff). Existence-register resolves toward not-distinguishable-from-null at simplified-formulation register-class. Different candidate basis at successor cycle MAY produce different result. Successor cycle adjudication required for retrospective at deeper register OR breadth expansion."*
- **Inconclusive:** *"PHASE2C_11 primary register: inconclusive at simplified DSR-style screen (criteria disagreement OR intermediate p-values at N=198). Existence question unresolved at PHASE2C_11 simplified register. Successor cycle adjudication required; canonical-DSR scope expansion (deferred prerequisite) is one register-class-eligible successor path."*

These are the canonical phrasings; result documentation operates against these or substantively-equivalent register-precise alternatives. Forbidden phrases per §6.2 explicitly excluded.

---

## §7 Implementation activity register

### §7.1 Sequenced steps (5 steps; revised at v3 from v2's 6 steps; Step 1.5 partition mapping audit dissolved at simplified MVD per §2.4)

The implementation arc operates against this 5-step sequence; each step seals at clean register before the next fires.

**Step 1 — Artifact inventory + RS guard verification (RS-2 lockpoint).** Verify all 198 audit_v1 candidate directories contain `holdout_summary.json`; verify lineage_check = 'passed' at all 198 candidates; verify engine_commit field = 'eb1c87f'; cross-check aggregate `holdout_results.csv` row count + scalar consistency vs JSON files (per §3.4 + §4.4(5) cross-validation). **RS-2 lockpoint:** before any audit_v1 artifact consumption, call `check_evaluation_semantics_or_raise()` from `backtest/wf_lineage.py` per Section RS canonical hard prohibition (per §0.3 + §2.5 + backlog §2.2.3). Step 1 deliverable: artifact inventory record + lineage verification + cross-validation diagnostics + module scope decision (extend `evaluate_dsr.py` per §4.5).

**α-Refine deliverable extension (per advisor concern; v3.1 empirical correction per Step 1 §19 Instance 7):** Step 1 deliverable additionally documents the empirical multi-run hypothesis_hash distribution at experiments.db: at `batch_id = b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`, the `runs` table contains **854 `regime_holdout` rows mapping to 198 distinct 64-char SHA256 hypothesis_hash values**, with multiplicity distribution {4 runs/hash: 149 hashes; 5 runs/hash: 39; 6 runs/hash: 7; 7 runs/hash: 3}. The 64-char SHA256 hash scheme at experiments.db is independent from the 16-char DSL truncated hash scheme at audit_v1 per §0.5 Instance 4 (no prefix-match identifier mapping). Prior v3 cited figure "246 runs > 198 distinct hashes" was empirically incorrect at canonical-artifact register; v3.1 corrects to 854/198 with explicit multiplicity profile. Note: this is descriptive register only at simplified MVD scope; cross-register mapping to experiments.db is out-of-scope per §2.4. Forward-pointing for §4.7 deferred prerequisite work register: if successor cycle authorizes canonical Bailey-López de Prado DSR scope, the 4–7 multiplicity-per-candidate distribution is load-bearing for partition mapping infrastructure planning (Path A canonical-hash mapping must resolve which experiments.db run is "the" canonical run for a given audit_v1 candidate).

**Step 2 — Compute simplified DSR-style screen inputs.** Load per-candidate Sharpe scalars from audit_v1 holdout_summary.json files; compute cross-trial mean + variance + max + min summary statistics; identify edge cases per §4.4 (low trade count exclusions; missing/null Sharpe; cross-validation failures); produce input statistics record. **RS-2 lockpoint:** call `check_evaluation_semantics_or_raise()` per audit_v1 artifact consumption. Pre-registered subset application: candidates with `T_c < 5` excluded per §4.4. Step 2 deliverable: input statistics record (cross-trial scalars; eligible subset N; excluded candidate list with exclusion reasons).

**Step 3 — Simplified DSR-style screen calculation.** Implement extension to `backtest/evaluate_dsr.py` `compute_simplified_dsr()` per §4.3 procedure; compute per-candidate disposition per §3.6; compute population-level disposition for SR_max per §4.3 Step 5; compute Bonferroni cross-check per §6.6; compute sensitivity table per §5.4. **RS-3 lockpoint:** function entry calls `check_evaluation_semantics_or_raise()` per §4.5 API surface. Step 3 deliverable: computation record + per-candidate disposition table + population-level result + sensitivity table + Bonferroni-vs-DSR-style cross-check.

**Step 4 — Summary tables.** Author result summary documents:
- Primary result table (per-candidate simplified DSR-style screen at N=198)
- Population-level summary (SR_max + DSR-style p-value + Bonferroni threshold + disposition per §3.6)
- Sensitivity table (varied N_eff per §5.4; descriptive)
- Bonferroni-vs-DSR-style cross-check
- Per-criterion result interpretation per §6 (signal evidence / artifact evidence / inconclusive)
- Symmetric register-class discipline phrasing per §6.7 canonical phrasings
- §6.2 forbidden phrases discipline applied at result narrative

Step 4 deliverable: closeout MD draft (provisionally `docs/closeout/PHASE2C_11_RESULTS.md`).

**Step 5 — Reviewer / adversarial checks.** Closeout MD draft passes through dual-reviewer cycle (ChatGPT + Claude advisor substantive prose-access pass per anchor-prose-access discipline) + Codex adversarial review on code/spec interface per §8 routing. Patches applied; full-file pass per §17 sub-rule 4; reviewer authorization at sealed register; closeout MD seals. Step 5 deliverable: sealed closeout MD + reviewer authorization records.

### §7.2 Step gating criteria

Each step seals at:

- **Step 1:** artifact inventory clean; lineage verification clean; RS-2 guard call demonstrated; cross-validation diagnostics clean; α-Refine deliverable component complete; module scope decision adjudicated; reviewer authorization at sealed register.
- **Step 2:** input statistics record clean; cross-validation per §3.4 + §4.4(5) clean; eligible subset N documented; excluded candidate list complete; RS-2 guard calls operational; reviewer authorization at sealed register.
- **Step 3:** simplified DSR-style screen computation reproducible (same inputs → same outputs); RS-3 guard call at function entry verified; Codex adversarial review on computation code clean; reviewer authorization at sealed register.
- **Step 4:** result tables complete per §6 framework; pre-registered interpretation applied per §3.6 lockpoints (no post-hoc adjustment); symmetric register-class discipline per §6.2 + §6.7 applied; forbidden phrases discipline verified; dual-reviewer pass clean.
- **Step 5:** closeout MD sealed; tag commit candidate `phase2c-11-statistical-significance-v1` at sealed register; Charlie-register authorization for tag + push.

### §7.3 No result computation before §3 + §4 seal

**Hard rule per §3.7 + §0.4:** Steps 2-5 MUST NOT fire before this sub-spec (§3 pre-registration block + §4 simplified DSR-style screen specification) seals at register-precision register.

Step 1 (artifact inventory + RS guard verification) MAY fire before sub-spec seal as preparation work since it doesn't compute results — it verifies artifact existence + RS guard discipline. However, Step 1 produces inputs to subsequent steps; result computation defers to sub-spec seal.

If implementation Step 1 surfaces evidence that §2 / §3 / §4 contains specification defects, resolution path per §0.4: document defect at full register; treat affected results as inconclusive; defer to post-PHASE2C_11 successor cycle for re-specification. NO mid-arc spec adjustment at primary register.

### §7.4 Phase Marker advance + tag

At Step 5 seal: CLAUDE.md Phase Marker advance to "PHASE2C_11 SEALED" with closeout result summary; tag commit candidate `phase2c-11-statistical-significance-v1` per project tag convention.

---

## §8 Reviewer routing

### §8.1 Reviewer architecture per arc step

| Activity | ChatGPT | Claude advisor | Codex |
|---|---|---|---|
| Sub-spec drafting (this plan) | first-pass | substantive prose-access | skip per scoping-doc register precedent |
| Step 1 artifact inventory + RS guard verification | structural | substantive | **fires** if RS guard implementation involves new code; skip if pure verification |
| Step 2 compute simplified DSR-style screen inputs | structural | substantive | **fires** (computation code + cross-validation logic) |
| Step 3 simplified DSR-style screen calculation | structural | substantive | **fires** (canonical formula implementation; load-bearing; RS guard call verification) |
| Step 4 summary tables | first-pass | substantive prose-access | fires if code-driven; skip if MD-only |
| Step 5 closeout MD | first-pass | substantive prose-access | adjudicated at closeout register per §11 closeout-assembly checklist |

### §8.2 Codex routing — required at code/spec interface (P6 patch preserved)

Per `feedback_codex_review_scope.md` user-memory rule + scoping doc §7.2: Codex adversarial review fires on substantive code/work. PHASE2C_11 implementation arc has substantive code work at Steps 2-3 (simplified DSR-style screen computation + RS guard call discipline); **Codex review fires at Step 3 seal at minimum** before Step 4 (result summary tables) consumes the computation outputs.

**Codex adversarial review focus at Step 3:**

- Simplified DSR-style screen formula implementation correctness against §4.3 specification
- Edge case handling per §4.4 (low trade count; zero variance; missing values; JSON-vs-CSV cross-validation failure)
- Numerical stability (Gumbel approximation; small/large N; near-zero variance)
- **RS guard call verification (RS-3):** function entry calls `check_evaluation_semantics_or_raise()` per §4.5 API surface; refuses processing if attestation domain check fails
- Test coverage at Step 3 register
- Cross-reference precision against §4.3 + §4.4 + §5.4 lockpoints
- Cross-validation logic per §3.4 + §4.4(5) (JSON-vs-CSV scalar agreement)

**Step 2 Codex routing:** fires on computation code that produces Step 3 inputs (Sharpe loading + cross-trial moments + edge case filtering + RS guard calls).

Codex routing at Step 4 / Step 5 adjudicated at Step 3 seal.

### §8.3 No result computation before sub-spec seal

Per §7.3: Steps 2-5 MUST NOT fire before this sub-spec seals. Reviewer routing at this sub-spec drafting cycle:

- ChatGPT first-pass at substantive register (this plan's prose; technical-spec content; pre-registration lockpoints)
- Claude advisor substantive prose-access pass (full prose access; not summary; per §16 anchor-prose-access discipline)
- Codex skipped per scoping-doc register precedent + this plan is spec/deliberation document, not code
- Both reviewers authorize seal; patches surfaced applied; sub-spec seals
- Implementation arc Step 1 fires post-seal

### §8.4 Pre-registration adversarial check

At sub-spec dual-reviewer pass: reviewers should adversarially scrutinize the §3 pre-registration block:

- Is §3.1 candidate population lockpoint defensible at conservative-when-uncertain register?
- Is §3.2 trial count lockpoint genuinely conservative?
- Is §3.3 return metric lockpoint canonical at audit_v1 evaluation register?
- Is §3.4 Sharpe estimation method consumed unchanged from engine output?
- Is §3.5 null/deflation assumptions honestly bounded at simplified-formulation register-class?
- Is §3.6 pass/fail interpretation conventional thresholds with conservative AND-gate?

The adversarial scrutiny ensures PHASE2C_11 is not rigor theater. Pre-registration that survives adversarial pass = real anti-p-hacking gate.

---

## §9 Cross-references

### §9.1 PHASE2C_11 cross-references

- [PHASE2C_11_SCOPING_DECISION.md](PHASE2C_11_SCOPING_DECISION.md) — scoping decision sealed at `3cfa357`; §4.2 selection + §6.1 scope register + §6.2 pre-registered framing decisions are this plan's inputs
- CLAUDE.md Phase Marker — current state at PHASE2C_11 scoping cycle SEALED; Phase Marker reconciliation update fires at this plan's seal arc per discipline rule

### §9.2 PHASE2C_10 cross-references

- [PHASE2C_10_PLAN.md](PHASE2C_10_PLAN.md) — structural reference for sub-spec/plan documentation cycle structure
- [docs/closeout/PHASE2C_10_METHODOLOGY_CONSOLIDATION_SIGNOFF.md](../closeout/PHASE2C_10_METHODOLOGY_CONSOLIDATION_SIGNOFF.md) — methodology consolidation infrastructure operating at this sub-spec register
- METHODOLOGY_NOTES.md §16 + §17 + §19 disciplines (operative at v1→v2→v3 rewrite chain per §0.5)

### §9.3 PHASE2C_8.1 cross-references

- [PHASE2C_8_1_PLAN.md](PHASE2C_8_1_PLAN.md) — extended multi-regime evaluation gate spec
- [docs/closeout/PHASE2C_8_1_RESULTS.md](../closeout/PHASE2C_8_1_RESULTS.md) — n=198 candidate set source register

### §9.4 PHASE2C_9 cross-references

- [docs/closeout/PHASE2C_9_RESULTS.md](../closeout/PHASE2C_9_RESULTS.md) — §8.2 forward-pointer + Q-9.A + B.2/B.3 sub-paths source

### §9.5 METHODOLOGY_NOTES cross-references

- [docs/discipline/METHODOLOGY_NOTES.md](../discipline/METHODOLOGY_NOTES.md) — §1-§19; §16 anchor-prose-access (operative at sub-spec seal); §17 procedural-confirmation defect class; §1 empirical verification (operationalized at four canonical-source-register layers per §0.5); §19 spec-vs-empirical-reality finding pattern (four cumulative instances at PHASE2C_11 cycle per §0.5)

### §9.6 TECHNIQUE_BACKLOG cross-references

- [strategies/TECHNIQUE_BACKLOG.md §2.2.3](../../strategies/TECHNIQUE_BACKLOG.md) — DSR Section RS corrected-engine dependency (RS-1/RS-2/RS-3 source per §0.3 + §2.5 + §7.1 lockpoints)
- [strategies/TECHNIQUE_BACKLOG.md §3.7](../../strategies/TECHNIQUE_BACKLOG.md) — Independent weak-signal composition (B-1 cross-reference at §5.2 supporting conservative N_eff policy)
- [strategies/TECHNIQUE_BACKLOG.md §3.8](../../strategies/TECHNIQUE_BACKLOG.md) — Five-criteria anti-overfitting checklist (B-2 cross-reference at §6.2 + §6.3 reinforcing P5 patch)
- [strategies/TECHNIQUE_BACKLOG.md §3.2](../../strategies/TECHNIQUE_BACKLOG.md) — Risk premium vs. genuine alpha distinction (B-3 cross-reference at §6.2)
- [strategies/TECHNIQUE_BACKLOG.md §2.2.2 PBO](../../strategies/TECHNIQUE_BACKLOG.md) — confirms §4.6 stretch register framing
- [strategies/TECHNIQUE_BACKLOG.md §2.2.4 CPCV](../../strategies/TECHNIQUE_BACKLOG.md) — confirms §4.7 out-of-MVD framing
- [strategies/TECHNIQUE_BACKLOG.md §2.2.1 Stationary Bootstrap](../../strategies/TECHNIQUE_BACKLOG.md) — Phase 3 register placement; deferred per §4.7

### §9.7 Code module cross-references

- [`backtest/evaluate_dsr.py`](../../backtest/evaluate_dsr.py) — existing heuristic Bonferroni screen; extension target per §4.5; RS-3 guard call addition required per §2.5
- [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) — `check_wf_semantics_or_raise()` + `check_evaluation_semantics_or_raise()` consumer-side helpers (Section RS source)
- [`backtest/metrics.py`](../../backtest/metrics.py) — Sharpe ratio computation per `eb1c87f` corrected engine; canonical at audit_v1 evaluation register
- [`agents/hypothesis_hash.py:172-173`](../../agents/hypothesis_hash.py) — DSL canonical hash truncation to 16 chars (audit_v1 hash scheme source)

### §9.8 Decision document cross-references

- [docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md) Section RS — canonical hard prohibition source for RS-1/RS-2/RS-3

### §9.9 Canonical reference (deferred prerequisite per §4.7)

- Bailey, D. H., & López de Prado, M. (2014). "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality." *Journal of Portfolio Management*, 40(5), 94-107. **Canonical formulation deferred prerequisite at PHASE2C_11; out of MVD scope per §0.1 + §4.7.**

---

**End of working draft v3.** Anchor-prose-access discipline dual-reviewer pass at this sub-spec seal register next operational step. No simplified DSR-style screen computation fires before this sub-spec seals (per §3.7 + §7.3 hard rule).
