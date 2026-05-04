# PHASE2C_12 Plan — Breadth Expansion Arc Sub-Spec

**Status: WORKING DRAFT v1 — pre-seal; SEAL pre-fire empirical verification register fires AGAINST this canonical artifact text register before Charlie-register seal authorization per [METHODOLOGY_NOTES §16](../discipline/METHODOLOGY_NOTES.md) anchor-prose-access discipline + handoff §11 step 2 binding.**

**Anchor:** PHASE2C_12 scoping decision sealed at commit `541c0be` ([`docs/phase2c/PHASE2C_12_SCOPING_DECISION.md`](PHASE2C_12_SCOPING_DECISION.md); 895 lines / 9 sections / 35 sub-sections); Phase Marker advance commit `5abb22b` on origin/main.

**v1 framing note:** sub-spec drafting cycle authored Components 1-6 LOCKED + Q1-Q25 LOCKED at conversation-register over single sub-spec authoring cycle session; M5 (ChatGPT structural overlay) + M6 (Claude advisor full-prose-access) + M7 (fresh-register full-file pass per METHODOLOGY_NOTES §17 sub-rule 4) reviewer pass cycle CLOSED at convergence with 3 M5 patches (S1 + S2 + S3) + 1 M6 substantive finding (F2 (ii) cascade at Q15 + Q24) ratified at Charlie-register; 12/12 M7 dimensions CLEAN. 9 empirical verifications fire at SEAL pre-fire register against this canonical artifact text register per advisor §5 prevention discipline + handoff §11 step 2 binding.

---

## §0 Document scope and structure

### §0.1 Scope

This plan covers PHASE2C_12's implementation arc: **breadth expansion at new candidate basis register-class** per scoping decision §4.4 arc designation. New mining configuration at theme rotation 5/6→6/6 with `multi_factor_combination` flip; smoke + main 2-stage batch grid; evaluation at PHASE2C_8.1 register-class scope; comparison against PHASE2C_11 canonical-basis disposition (`b6fcbf86` `artifact_evidence` at simplified DSR-style screen) at register-class-comparable register.

**Scope register-class:**

- **In scope (MVD):** smoke batch (40 candidates, single-theme `multi_factor_combination`) + main batch (198 candidates, 6/6 theme rotation) at PHASE2C_8.1 register-class evaluation against bear_2022 + validation_2024 + eval_2020_v1 + eval_2021_v1; simplified DSR-style screen disposition adjudication per PHASE2C_11 canonical thresholds full-framework reuse.
- **Out of MVD scope:** mechanism deeper investigation (path (a) deferred per scoping §4.3); calibration variation (path (c) deferred); canonical-DSR scope expansion (per §4.7 deferred prerequisite); engine re-run; new factor library expansion; DSL complexity budget shift.
- **Explicitly out of arc scope:** Phase 3 progression decisions; methodology consolidation cycle; successor scoping cycle direction (anti-pre-naming option (ii) preserved per scoping §4.4).

### §0.2 Structure

§1 resolves filename + document-type framing per anti-pre-naming convention. §2 enumerates locked inputs from PHASE2C_11 canonical reuse anchors + canonical THEMES tuple at `agents/themes.py` + Stage 2c/2d operational rotation boundary + RS-guard requirements + scoping arc designation. §3 carries the **load-bearing pre-registration block at register-precision**: Components 1-6 LOCKED bindings exhaustively enumerated at §6.2 6-component sub-spec pre-registration framework register-precision. §4 specifies mining configuration at smoke + main register-class-distinct register-precision binding. §5 specifies materially-different-basis distinction at theme-coverage disjoint distribution register per Component 4 verbatim. §6 specifies evaluation register at Component 5 4-element exhaustive enumeration + Component 6 full-framework reuse PHASE2C_11 binding. §7 enumerates Q1-Q25 LOCKED summary. §8 specifies implementation activity register at sequenced steps. §9 documents reviewer routing + M5/M6/M7 disposition record. §10 specifies the 9 empirical verifications fire-register at SEAL pre-fire (NOT yet fired at this v1 draft register). §11 documents cross-references.

### §0.3 Discipline anchors operating at this drafting cycle

Eight disciplines operate at this plan's drafting cycle and at the implementation arc that follows:

- **Anchor-prose-access discipline (METHODOLOGY_NOTES §16).** Fires at this sub-spec seal register; reviewer pass (M5 + M6 + M7) fired at conversation-register draft access at register-precision. M7 fresh-register full-file pass per §17 sub-rule 4 fires at this canonical artifact register before SEAL commit.
- **Procedural-confirmation defect class (METHODOLOGY_NOTES §17).** Working-draft commit before substantive prose-access pass is the defect class; this plan's seal fires AFTER reviewer pass cycle CLOSED + SEAL pre-fire empirical verification register CLEAN, not before. Application sub-rule 4 fires at this canonical artifact register.
- **Anti-momentum-binding discipline.** Per scoping doc §4.5 + §1 standing instruction: reviewer-lean inputs are scoping-cycle-input not selection. Sub-spec author leans across Q-questions are INPUT register; LOCKED dispositions emerge at substantive register-precision per per-Q Charlie-register adjudication (Q1-Q25 cumulative).
- **Anti-pre-naming discipline (METHODOLOGY_NOTES §10 + scoping §4.4 option (ii)).** Successor cycle direction post-PHASE2C_12 implementation arc is NOT pre-committed at this plan's draft fire; carries forward per scoping §6 deferral.
- **Anti-fishing-license discipline (per scoping §5 guardrails 1 + 2 + 3).** Sub-spec author framing as "register-class-extension test" at PHASE2C_8.1 register-class scope; NOT "search-coverage-defect-finding mandate" or "calibration-defect-finding mandate". Threshold redefinition explicitly banned at sub-spec drafting cycle per Q17 LOCKED (a) reuse disposition.
- **Empirical verification discipline (METHODOLOGY_NOTES §1).** File-structure citations + canonical-formula citations + canonical-project-convention compliance + canonical-artifact-mapping verification fire at SEAL pre-fire empirical verification register-class against this canonical artifact text register per §10 below.
- **Spec-vs-empirical-reality finding pattern (METHODOLOGY_NOTES §19).** Per scoping §6.3 carry-forward register: this sub-spec drafting cycle inherits §19 cumulative-count register at next methodology consolidation cycle; observation-only at this register, NOT load-bearing for current PHASE2C_12 cycle's seal at this register.
- **Section RS corrected-engine consumer-side discipline.** All consumers of WF artifacts must call `check_wf_semantics_or_raise()` from [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py); all consumers of single_run_holdout_v1 attestation domain artifacts must call companion `check_evaluation_semantics_or_raise()`. PHASE2C_12 main batch evaluation consumes audit_v1 single_run_holdout_v1 artifacts at PHASE2C_8.1 register-class scope; consumer-side helper call requirement applies at every implementation step that reads holdout_summary.json or experiments.db runs table per §8 lockpoints.

### §0.4 Process note — anti-p-hacking discipline at sub-spec register

The pre-registration block at §3 is the load-bearing anti-p-hacking guardrail at this arc. Any post-result parameter adjustment to the §3 lockpoints — Component 1 axis selection, Component 2 mining-batch count + smoke PASS criteria, Component 3 generation-cycle parameters, Component 4 materially-different-basis distinction, Component 5 evaluation-slice 4-element enumeration, Component 6 evaluation-threshold framework reuse — is **forbidden at register-precision register** per scoping §5 guardrails 6 + 7 + 8 + 9 cumulative binding.

If post-result review surfaces evidence that a §3 lockpoint was mis-specified at sub-spec drafting cycle, the resolution path is: (a) document the mis-specification at full register-precision; (b) treat affected results as **inconclusive at PHASE2C_12 register**, not as adjusted-pass or adjusted-fail; (c) defer to post-PHASE2C_12 successor cycle for re-specification; (d) Component 4 / Component 5 / Component 6 verification register failure signal binding routes back to scoping cycle adjudication per §6.2 verbatim binding.

This is the discipline that distinguishes PHASE2C_12 from rigor theater: the test commits to its parameters before knowing the answer.

### §0.5 Scoping decision §4.4 arc designation binding

Per scoping decision §4.4 arc designation verbatim: **PHASE2C_12 = breadth expansion arc** (new candidate basis register-class). Scope binding at this sub-spec drafting cycle:

- New mining configuration register-class (theme rotation expansion 5/6→6/6 with `multi_factor_combination`)
- NOT mechanism deeper investigation register-class (path (a) deferred per scoping §4.3)
- NOT calibration variation register-class (path (c) deferred per scoping §4.3)
- NOT canonical-DSR scope expansion register-class (per §4.7 deferred prerequisite path A or path B)
- NOT Phase 3 trajectory authorization register-class (per §6.4 path (f) foreclosed for current survivor set)

Threshold framework redefinition is explicitly out of arc scope at sub-spec drafting cycle register; redefinition would broaden scope beyond §4.4 breadth-expansion arc designation. This binding is LOAD-BEARING at Q17 LOCKED (a) reuse disposition per controlled-experiment principle binding.

---

## §1 Filename and document-type lock (anti-pre-naming option (ii) resolution)

### §1.1 Filename decision

**Filename: `docs/phase2c/PHASE2C_12_PLAN.md`** (this document).

Resolution per anti-pre-naming option (ii). Convention precedent (PHASE2C_6/7/8/9/10/11 _PLAN.md) + single-arc scope + cross-reference grep stability.

### §1.2 Document-type framing

This plan's deliverable register is **arc-level implementation spec at technical-spec register-class**. Authorship register is canonical-spec (load-bearing structural commitments + technical lockpoints). Verification register is sequential-routing reviewer pass (M5 ChatGPT structural-overlay + M6 Claude advisor full-prose-access + M7 fresh-register full-file pass per METHODOLOGY_NOTES §17 sub-rule 4); Codex skipped per scoping-doc + sub-spec register precedent + [`feedback_codex_review_scope.md`](../../) memory.

Discipline alignment: §10 anti-pre-naming applies to filename + successor cycle direction. §16 anchor-prose-access applies at this plan's seal cycle. §17 procedural-confirmation defect class applies. §1 + §19 disciplines applied at sub-spec drafting cycle.

---

## §2 Locked inputs

### §2.1 PHASE2C_11 canonical reuse anchors (full-framework reuse per Q17 LOCKED + S2 patch)

**Per Component 6 LOCKED + Q17 LOCKED + M5-S2 patch full-framework reuse binding:** PHASE2C_12 inherits PHASE2C_11 simplified DSR-style framework at five register-class-distinct elements, all at canonical PHASE2C_11 register-precedent verbatim.

| Element | Source | Reused value at PHASE2C_12 main register |
|---|---|---|
| Formula | [`backtest/evaluate_dsr.py:956-1278`](../../backtest/evaluate_dsr.py) `compute_simplified_dsr()` canonical implementation | unchanged (function consumed verbatim) |
| N choice | [PHASE2C_11_PLAN §3.2](PHASE2C_11_PLAN.md) lockpoint | N_raw = N_eff = 198 (conservative default; matches main batch count Q3 LOCKED) |
| Threshold values | [PHASE2C_11_PLAN §3.6](PHASE2C_11_PLAN.md) | pass threshold `p < 0.05`; fail-AND-gate threshold `p ≥ 0.5`; Bonferroni threshold `√(2·ln(198)) = 3.252158` (6-decimal explanatory-prose register; formula computed at runtime) |
| Routing logic | [PHASE2C_11_PLAN §3.6](PHASE2C_11_PLAN.md) conservative AND-gate | signal_evidence: BOTH (`p < 0.05` AND `SR_max > Bonferroni`); artifact_evidence: BOTH (`p ≥ 0.5` AND `SR_max ≤ Bonferroni`); inconclusive: anything else |
| Disposition labels | PHASE2C_11 register-precedent | `signal_evidence` / `artifact_evidence` / `inconclusive` |

**PHASE2C_11 canonical disposition (comparison anchor):** at canonical mining batch_id `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` audit_v1 evaluation register (n_raw=198; n_eligible=154 post-§4.4 trade-margin filter), `population_disposition = artifact_evidence` per [PHASE2C_11_RESULTS.md §1.1](../closeout/PHASE2C_11_RESULTS.md) §3.6 conservative AND-gate routing. Numerical anchors: `SR_max = 0.9602178531387877`; `argmax_p_value = 0.999997737801711`; `bonferroni_threshold = 3.25215836966607`; `expected_max_sharpe_null = 2.01225257627714` (Gumbel approximation). PHASE2C_12 main batch register-class-comparable comparison fires at this canonical anchor register-precision.

### §2.2 Canonical THEMES tuple (anti-fishing-license boundary; Component 4 register-class anchor)

Source of truth: [`agents/themes.py`](../../agents/themes.py) THEMES tuple at lines 22-29:

```python
THEMES: tuple[str, ...] = (
    "momentum",
    "mean_reversion",
    "volatility_regime",
    "volume_divergence",
    "calendar_effect",
    "multi_factor_combination",
)
```

**Cardinality: 6 themes.** `multi_factor_combination` is canonical 6th theme at this register-precision; preserved at canonical anchor across `agents/themes.py` + `expectations.md` + `blueprint/PHASE2_BLUEPRINT.md` per CLAUDE.md F7 verification reads.

### §2.3 Stage 2c/2d operational rotation boundary (current state pre-PHASE2C_12 fire)

Source: [`agents/proposer/stage2c_batch.py:93`](../../agents/proposer/stage2c_batch.py) + [`agents/proposer/stage2d_batch.py:112`](../../agents/proposer/stage2d_batch.py) — `THEME_CYCLE_LEN = 5` (multi_factor_combination excluded from current operational rotation).

Implementation surfaces for Q9 + Q10 LOCKED:
- `_theme_for_position(k: int) -> str` at [`agents/proposer/stage2c_batch.py:156-158`](../../agents/proposer/stage2c_batch.py) + [`agents/proposer/stage2d_batch.py:198-200`](../../agents/proposer/stage2d_batch.py) — uses `THEMES[(k - 1) % THEME_CYCLE_LEN]`

**Per CLAUDE.md "Theme rotation operational boundary" verbatim:** "exclusion is operational practice, not canonical specification; canonical anchors retain the 6-theme list; flip preserved for future decision when there's a specific Phase 2C reason; flip would require small 6th-theme-only smoke batch to verify candidate quality first."

PHASE2C_12 satisfies the flip-precondition at register-precision: Component 1 axis selection grounds in §6.7 register-class-comparable comparison binding (specific Phase 2C reason satisfied per scoping §6.3 carry-forward entry 1 F7 verification CLEAN); Component 2 Q1 smoke batch at 40 candidates 100% `multi_factor_combination` satisfies F7 smoke-batch-precondition.

### §2.4 RS-guard consumer-side discipline binding

Per [TECHNIQUE_BACKLOG.md §2.2.3](../../strategies/TECHNIQUE_BACKLOG.md) + CLAUDE.md "Hard rule for any future WF-consuming work" + PHASE2C_11 RS-1/RS-2/RS-3 patch precedent:

- Any consumer of WF artifacts MUST call `check_wf_semantics_or_raise(summary, artifact_path=...)` from [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py)
- Any consumer of single_run_holdout_v1 attestation domain artifacts MUST call companion `check_evaluation_semantics_or_raise()`

PHASE2C_12 main batch evaluation consumes audit_v1 single_run_holdout_v1 artifacts at PHASE2C_8.1 register-class scope; consumer-side helper call requirement applies at every implementation step that reads `holdout_summary.json` OR `experiments.db` runs table per §8 implementation activity register lockpoints.

### §2.5 Scoping arc designation + dominant uncertainty binding

Per scoping decision §4.4 + §4.1 verbatim:

- **Arc designation:** PHASE2C_12 = breadth expansion arc at new candidate basis register-class (NOT mechanism investigation; NOT calibration variation; NOT canonical-DSR scope expansion; NOT Phase 3 trajectory)
- **§4.1 dominant uncertainty:** candidate-basis-representativeness uncertainty (the §6.7 explicit-naming hypothetical's open question — would different candidate basis produce register-class-comparable comparison disposition or different disposition?)
- **§1.3 cycle-scope budget:** "Medium" register (multi-arc commitment at order-of-PHASE2C_8.1-or-PHASE2C_11 scale; not unbounded)

### §2.6 No new factor library, no new DSL complexity budget, no new evaluation framework

Per scoping §5 guardrail 6 + §4.4 arc designation + Q17 LOCKED:

- Factor library scope = canonical Phase 2A registered factors at [`factors/registry.py`](../../factors/registry.py); NOT expanded at PHASE2C_12
- DSL complexity budget = CLAUDE.md canonical (entry/exit groups ≤ 3; conditions per group ≤ 4; max_hold_bars ≤ 720; name ≤ 64 chars; description ≤ 300 chars); NOT shifted at PHASE2C_12
- Evaluation framework = PHASE2C_11 simplified DSR-style screen at full-framework reuse per Q17 LOCKED + Component 6 §C6.3 PATCH S2 5-element binding; NOT redefined at PHASE2C_12

---

## §3 Pre-registration block (anti-p-hacking guardrail; load-bearing)

This section is the **load-bearing anti-p-hacking guardrail** per scoping §5 guardrails 6 + 7 + 8 + 9 cumulative binding. All values pre-registered here are LOCKED at sub-spec SEAL register before any mining fires. Post-result adjustment forbidden per §0.4.

Components 1-6 are exhaustively enumerated at scoping §6.2 6-component sub-spec pre-registration framework register-precision register. Each Component's LOCKED bindings at sub-spec drafting cycle are documented at register-precision register-binding.

### §3.1 Component 1 LOCKED — Axis selection

**Locked specification: Theme rotation expansion 5/6 → 6/6 with `multi_factor_combination`.**

Authorized at Charlie-register; triple convergence with ChatGPT M3 + Claude advisor M3 + sub-spec author at scoping cycle register.

| Sub-binding | Locked specification |
|---|---|
| Axis | Theme rotation expansion 5/6 → 6/6 with `multi_factor_combination` |
| F7 verification | CLEAN per CLAUDE.md flip-authorization wording at §2.3 |
| Register-class distinction from `b6fcbf86` | Theme-coverage register (theme-cardinality + theme-content) |
| Component 4 register-class satisfied | §6.2 register-class #2 — disjoint theme-coverage distribution |
| F7 sub-precondition | Smoke batch (6th-theme-only, bounded count) — folds into Component 2 |
| ChatGPT binding condition | If smoke fails candidate-quality/mechanics criteria → STOP and surface back to Charlie-register adjudication |

### §3.2 Component 2 LOCKED — Mining-batch count + Smoke PASS criteria

**Locked specification: 2-stage small grid pre-registered at count = 2 (smoke + main).**

§5 guardrail 6 expansion ban binding; single-batch INSUFFICIENT per F7 smoke-batch-precondition.

| Sub-binding | Locked specification |
|---|---|
| Mining-batch count | 2 (smoke + main) |
| Stage 1 = smoke batch | Gate-fire register (PASS/FAIL adjudication only; NOT canonical-disposition input) |
| Stage 2 = main batch | Test-fire register (canonical-disposition input); CONDITIONAL on smoke PASS |
| Smoke-fail-stop binding | If smoke fails → stop and surface back to Charlie-register adjudication; main batch does NOT fire |
| Anti-§5-guardrail-6 binding | Smoke + main is LOCKED grid; no post-result smoke re-roll; no post-smoke main batch count expansion; no multi-main-batch rolling |
| Q1 Smoke count | **40 candidates** (matches PHASE2C_8.1 canonical per-theme cardinality) |
| Q2 Smoke PASS criteria | **Composite AND-gate (A) + (B) + (C); (D) deferred** — DSL-validity rate + Critic-approved/`pending_backtest` rate + Compilation-cleanliness rate (all approved DSLs) |
| Q2 Threshold framework | **Canonical-baseline-relative with bounded-tolerance ≥ 0.9× canonical baseline rate per criterion** (specific canonical baseline rates verified at SEAL pre-fire empirical verification register #1) |
| Q3 Main count | **198 candidates** (register-class-comparable to canonical `b6fcbf86` exact N; clean integer per-theme distribution 33·6=198; Bonferroni √(2·ln(198))=3.252158 N-matched) |
| Q4 Smoke-fail-stop adjudication scope | **(b) Escalation back to scoping cycle adjudication** — smoke-FAIL at axis #1 IS Component 4 verification register failure signal at theme-coverage register-precision; sub-spec discipline does NOT carry §4.1 register adjudication authority |
| Q5 Smoke-PASS to main transition | **(i) Charlie-register gate at smoke-vs-main boundary** — smoke-PASS adjudication at pre-registered criteria = reviewer convergence (necessary input); main batch fire = substantive operational fire requiring Charlie-register authorization per `feedback_authorization_routing.md`; Charlie cannot redefine smoke-PASS criteria post-smoke (anti-p-hacking preserved at pre-registration register) |

### §3.3 Component 3 LOCKED — Generation-cycle parameter pre-registration

**Locked specification: DSL complexity budget at CLAUDE.md canonical bounds; theme weights pre-registered per smoke + main register-class-distinct register; generation-cycle counts pre-registered.**

| Sub-binding | Locked specification |
|---|---|
| DSL complexity budget — entry/exit groups | `≤ 3` (CLAUDE.md canonical; applies to BOTH smoke + main batches) |
| DSL complexity budget — conditions per group | `≤ 4` |
| DSL complexity budget — `max_hold_bars` | `≤ 720` |
| DSL complexity budget — `name` | `≤ 64 chars` |
| DSL complexity budget — `description` | `≤ 300 chars` |
| Smoke batch theme weight | 100% `multi_factor_combination` (single-theme per Component 2 Stage 1 + CLAUDE.md flip-precondition) |
| Q6 Main batch theme weight distribution | **Uniform 6/6 = 1/6 each (33 candidates per theme; 33·6=198 clean integer distribution)** |
| Q7 Smoke generation-cycle count | **40 generation cycles at 1 candidate per cycle** (matches PHASE2C_8.1 register-precedent; statistical independence assumption preserved) |
| Q8 Main generation-cycle count | **198 generation cycles at 1 candidate per cycle** (register-class-comparable comparison at canonical PHASE2C_11 simplified-register screen binding preserved) |
| Q9 Smoke theme operationalization | **(β) Conditional theme override at proposer entry register** — `_theme_for_position` function override at smoke fire returning `multi_factor_combination` regardless of position; THEMES tuple invariant preserved at multi-source canonical anchor register; conditional logic bounded at smoke fire register |
| Q10 Main rotation flip operationalization | **(β) Configuration parameter at engine entry register** — `THEME_CYCLE_LEN` becomes config-driven (env var OR config.yaml); 6 at PHASE2C_12 main batch fire; canonical Stage 2c/2d invariant preserved at code register; persistence decision at successor scoping cycle adjudication register-class-distinct from sub-spec implementation register; **Q10 reviewer divergence cycle resolved at (β) per advisor pushback + ChatGPT post-pushback re-adjudication; final triple convergence at (β)** |

### §3.4 Component 4 LOCKED — Materially-different-basis distinction

**Locked specification: Disjoint theme-coverage distribution (§6.2 Component 4 register-class #2 verbatim).**

| Sub-binding | Locked specification |
|---|---|
| Distinction register-class selected | Disjoint theme-coverage distribution |
| PHASE2C_12 main batch theme-coverage spec | 6-theme rotation at uniform 1/6 per theme; 33 candidates × 6 themes = 198; themes = canonical THEMES tuple at `agents/themes.py` |
| Canonical `b6fcbf86` theme-coverage reference | 5-theme operational rotation; per-theme distribution 40/40/40/39/39 = 198; `multi_factor_combination` excluded per Stage 2c/2d operational rotation register |
| Verification Check 1 (theme-cardinality) | Post-main-batch theme-cardinality = 6 distinct themes |
| Verification Check 2 (theme-content) | Theme distribution includes `multi_factor_combination` AND 5 canonical Stage 2c/2d themes |
| Q11 Verification Check 3 (per-theme cardinality) | **Per-theme cardinality = 33 ± 2 (range 31-35)** — bounded register-precision tolerance accommodates 6th-theme novelty + LLM proposer non-determinism at register-class-comparable-to-canonical-baseline register |
| Verification Check 4 (`multi_factor_combination` operational verification) | `multi_factor_combination` per-theme cardinality = 33 ± 2; canonical `b6fcbf86` has 0; verification binds end-to-end Q9 + Q10 code-surface modification register at operational fire |
| Q12 Verification register failure consequence | **Escalate to scoping cycle adjudication per §6.2 Component 4 verification register failure signal binding verbatim — sub-spec discipline burden returns cycle to scoping cycle adjudication; in-arc retry explicitly banned; one-cycle-falsifiability preserved at single-cycle register-precision** |
| Q13 Empirical verification carry-forward | Approved (3 verification targets folded into 9-cumulative empirical verification register at §10) |

### §3.5 Component 5 LOCKED — Evaluation-slice 4-element exhaustive enumeration

**Locked specification: 4-element exhaustive enumeration at register-precision register per §6.2 Component 5 verbatim.**

| Element | Locked specification |
|---|---|
| Element 1 — Primary slice (Q14 γ) | **Full N=198 main batch population at primary disposition register** (PHASE2C_11 conservative N_eff = N_raw lockpoint preserved); §4.4-filter-equivalent subset (n_eligible ≈ 154) at secondary descriptive register |
| Element 2 — Secondary slices (5 enumerated) | (a) Per-theme disposition descriptive (6 themes × 33±2 per-theme cohort); (b) Smoke quality-mechanics descriptive ((A)+(B)+(C) rates); (c) **Q15 [REVISED at M6-F2 (ii) cascade]: N_eff sensitivity ∈ {198, 80, 40, 6} pre-registered at sub-spec SEAL — descriptive only; semantic-reuse register at "number of operational themes" per PHASE2C_11 §5.3 + §5.4 binding (PHASE2C_11 N_eff=5 ↔ 5 themes; PHASE2C_12 N_eff=6 ↔ 6 themes)**; (d) PHASE2C_11 canonical-basis comparison descriptive (vs `b6fcbf86` `artifact_evidence` at SR_max=0.9602178531387877; argmax_p_value=0.999997737801711); (e) Per-candidate disposition tally descriptive |
| Element 3 — Inclusion/exclusion filters (4 pre-registered) | Filter A: **Q16 (α) PHASE2C_11 §4.4 edge-case filter reused: `T_c < 5` EXCLUDED** (per [PHASE2C_11_PLAN §4.4 line 346 verbatim](PHASE2C_11_PLAN.md); n_eligible parallel to PHASE2C_11 n=154/198 retention rate; SEAL pre-fire empirical verification #7 CLEAN at Path A patch); Filter B: lifecycle state filter (exclude `proposer_invalid_dsl`/`duplicate`/`critic_rejected`/`train_failed`); Filter C: engine-version filter via `check_evaluation_semantics_or_raise()` corrected-engine guard; Filter D: compilation-cleanliness filter (exclude ManifestDriftError) |
| Element 4 — Aggregation rule (4 register-class-distinct registers) | Smoke = gate-fire register (PASS/FAIL only; NOT primary aggregation input); Main = test-fire register (canonical-disposition input at simplified DSR-style screen); Cross-batch concordance check = smoke-PASS-as-precondition-for-main register-class-distinct from aggregation; Within-main candidate aggregation via PHASE2C_11_PLAN §3.6 conservative AND-gate routing — **Component 6 LOCKED at (a) reuse fixes Element 4 aggregation at §3.6 routing verbatim** |

### §3.6 Component 6 LOCKED — Evaluation-threshold pre-registration

**Locked specification: (a) reuse PHASE2C_11 canonical thresholds at full-framework reuse register-precision per §6.2 Component 6 verbatim binding.**

Substantive ground: controlled-experiment principle binding per Charlie-register dual-reviewer convergence (ChatGPT药物试验类比 + Claude controlled-experiment isolation principle). PHASE2C_12 isolates ONE variable (candidate basis); threshold redefinition would confound new-basis effect with threshold-redefinition effect, breaking the breadth-expansion test register-class-isolation property. PHASE2C_11 simplified DSR-style screen limitation acknowledged but is a register-class-distinct successor path per §6.4 canonical-DSR scope expansion register, NOT within PHASE2C_12 §4.4 breadth-expansion arc designation scope.

| Q | LOCKED disposition |
|---|---|
| Q17 | (a) reuse PHASE2C_11 canonical thresholds at full register-precision (full-framework reuse per §2.1 5-element binding) |
| Q18 | N=198 per PHASE2C_11 §3.2 lockpoint (conservative N_eff = N_raw at primary register) |
| Q19 | p<0.05 pass threshold per §3.6 verbatim (signal-evidence pass criterion at simplified-register screen) |
| Q20 [PATCH S1] | **Bonferroni fail criterion = SR_max ≤ √(2·ln(198)) = 3.252158**; **DSR-style fail criterion = argmax_p_value ≥ 0.5**. `artifact_evidence` requires BOTH fail criteria under PHASE2C_11 §3.6 conservative AND-gate routing |
| Q21 | PHASE2C_11_PLAN §3.6 conservative AND-gate routing verbatim |
| Q22 | `signal_evidence` / `artifact_evidence` / `inconclusive` per PHASE2C_11 register-precedent |
| Q23 [PATCH S3] | Component 6 binding scope = **main register only**. Smoke PASS criteria from Component 2 Q2 are **candidate-quality gate thresholds**, NOT evaluation-threshold-register thresholds under Component 6. They are **excluded from §5 guardrail 9 scope** except insofar as **post-smoke mutation remains banned under Component 2's pre-registration binding**. Register-class-distinct semantics: smoke = candidate-quality gate (Component 2 Q2 quality-mechanics composite AND-gate); main = evaluation threshold (Component 6 simplified DSR-style screen) |
| Q24 [M6-F2 (ii)] | N_eff sensitivity ∈ **{198, 80, 40, 6}** per PHASE2C_11 §5.4 sensitivity table specification at semantic-reuse register (PHASE2C_11 N_eff=5 grounded at "number of operational themes" register per §5.3; PHASE2C_12 native register at 6 themes → N_eff=6 at parallel register-precision register-binding); descriptive register only; primary reads N_eff=198 only |
| Q25 | §3.6 P5 patch verbatim (statistical-evidence vs tradable-edge distinction preserved; signal at simplified register ≠ deployment-warrant ≠ Phase 3 authorization ≠ canonical-formulation-confirmed) |

### §3.7 §5 guardrail 9 LOAD-BEARING binding at Component 6

| Guardrail 9 mutation class | Pre-registration binding at PHASE2C_12 sub-spec SEAL |
|---|---|
| Changing p-value cutoffs post-mining (e.g., "actually use p<0.10 instead of p<0.05") | EXPLICITLY BANNED |
| Altering multiple-testing correction logic post-mining (e.g., different N choice for Bonferroni √(2·ln(N))) | EXPLICITLY BANNED |
| Modifying fail-AND-gate decision-rule threshold post-mining (e.g., 0.4 instead of 0.5) | EXPLICITLY BANNED |
| Switching reuse-vs-redefine framework post-mining | EXPLICITLY BANNED |

Threshold framework changes post-mining require **a new scoping cycle adjudication** per §6.2 Component 6 binding, NOT in-arc patch.

### §3.8 Anti-§5-guardrail bindings cumulative across Components

| # | Guardrail | Binding state at PHASE2C_12 sub-spec |
|---|---|---|
| 1 | Do not convert interesting results into deployment confidence | Active across all components |
| 2 | Do not let path (g) win by default just because it sounds rigorous | Active at scoping register (per scoping §3 path-by-path evaluation) |
| 3 | Do not let path (g) become "more mining feels safer" anti-pattern | Active at Component 1 axis selection + Component 2 batch count |
| 4 | Do not authorize Phase 3 unless current ambiguity is explicitly accepted | Active at successor cycle scoping register |
| 5 | §3 per-path evaluation register-precision over reviewer-lean inheritance (anti-momentum-binding) | Active at all reviewer adjudication registers (per Q10 + M6-F2 reviewer divergence cycle precedents) |
| 6 | Post-result expansion ban at 5-component candidate-generation register | Active at Components 1-3 + Component 5 Element 3 |
| 7 | One-cycle-falsifiability is selection floor | Active at Components 2 + 4 + 5 |
| 8 | Post-result reinterpretation ban at evaluation-slice register | LOAD-BEARING at Component 5 |
| 9 | Post-result evaluation-threshold mutation ban at evaluation-threshold register | **LOAD-BEARING at Component 6 per §3.7** |

### §3.9 Pre-registration verification gate

Before any PHASE2C_12 mining fires at implementation arc:

1. This §3 block must be sealed at sub-spec register (sub-spec sealed at SEAL commit; reviewer authorization at sealed register per §9 reviewer routing).
2. Implementation arc must NOT fire mining before this §3 block seals.
3. SEAL pre-fire empirical verification register §10 must complete CLEAN before SEAL commit fires.
4. RS guard calls per §2.4 must operate before any audit_v1 artifact consumption at main batch evaluation register.
5. If implementation arc surfaces evidence that a §3 lockpoint was mis-specified, resolution path per §0.4.

---

## §4 Mining specification

### §4.1 Smoke batch specification (Stage 1 gate-fire register)

| Parameter | Value |
|---|---|
| Batch role | Stage 1 gate-fire register (PASS/FAIL adjudication only) |
| Candidate count | 40 (per Q1 LOCKED) |
| Theme weight | 100% `multi_factor_combination` (single-theme; per Component 2 Stage 1 + CLAUDE.md flip-precondition) |
| Generation-cycle count | 40 cycles at 1 candidate per cycle (per Q7 LOCKED) |
| DSL complexity budget | CLAUDE.md canonical (per §3.3 entries) |
| Theme operationalization | (β) Conditional theme override at proposer entry register: `_theme_for_position` function override at smoke fire returning `multi_factor_combination` regardless of position; THEMES tuple invariant preserved (per Q9 LOCKED) |
| Smoke PASS criteria | Composite AND-gate (A) + (B) + (C); canonical-baseline-relative ≥ 0.9× per criterion (per Q2 LOCKED) |
| Smoke PASS criterion (A) | DSL-validity rate ≥ 0.9× canonical baseline (verified at SEAL pre-fire #1) |
| Smoke PASS criterion (B) | Critic-approved/`pending_backtest` rate ≥ 0.9× canonical baseline |
| Smoke PASS criterion (C) | Compilation-cleanliness rate (all approved DSLs) ≥ 0.9× canonical baseline |
| Smoke FAIL consequence | Stop and surface back to Charlie-register adjudication; main batch does NOT fire (per Q4 LOCKED) |
| Smoke PASS → main transition | Charlie-register gate at smoke-vs-main boundary (per Q5 LOCKED); reviewer convergence necessary input but not sufficient authorization |

### §4.2 Main batch specification (Stage 2 test-fire register)

| Parameter | Value |
|---|---|
| Batch role | Stage 2 test-fire register (canonical-disposition input at simplified DSR-style screen) |
| Candidate count | 198 (per Q3 LOCKED) |
| Theme weight | Uniform 6/6 = 1/6 each; 33 candidates per theme × 6 themes = 198 clean integer distribution (per Q6 LOCKED) |
| Generation-cycle count | 198 cycles at 1 candidate per cycle (per Q8 LOCKED) |
| DSL complexity budget | CLAUDE.md canonical (per §3.3 entries; identical to smoke) |
| Theme operationalization | (β) Configuration parameter at engine entry register: `THEME_CYCLE_LEN` config-driven (env var OR config.yaml); `THEME_CYCLE_LEN = 6` at PHASE2C_12 main batch fire; canonical Stage 2c/2d invariant preserved at code register; persistence decision at successor scoping cycle adjudication (per Q10 LOCKED) |
| Main batch fire condition | Smoke PASS at composite AND-gate per §4.1 + Charlie-register authorization at smoke-vs-main boundary |

### §4.3 Mining configuration anti-§5-guardrail bindings

| Guardrail | Binding |
|---|---|
| §5 guardrail 6 | Mining-batch count locked at 2; no post-smoke main expansion; no smoke re-roll on FAIL; no post-mining DSL complexity budget shift; no post-mining theme weight redistribution; no post-mining generation-cycle count adjustment |
| §5 guardrail 7 | One-cycle-falsifiability preserved at smoke + main 2-stage register-precision |
| §5 guardrail 8 | Smoke (gate-fire) vs main (test-fire) semantics pre-registered; post-result re-labeling banned |

---

## §5 Materially-different-basis specification (Component 4)

### §5.1 Distinction register-class

Per Component 4 LOCKED + scoping §6.2 register-class #2 verbatim: **disjoint theme-coverage distribution**.

PHASE2C_12 main batch theme-coverage spec is register-class-distinct from canonical `b6fcbf86` at theme-coverage register-precision register:

| Register | PHASE2C_12 main | Canonical `b6fcbf86` |
|---|---|---|
| Theme cardinality | 6 distinct themes | 5 distinct themes |
| Theme content | All 6 canonical THEMES tuple themes including `multi_factor_combination` | 5 canonical Stage 2c/2d operational rotation themes; `multi_factor_combination` excluded |
| Per-theme distribution | 33 candidates per theme × 6 themes = 198 (uniform) | 40/40/40/39/39 = 198 (5-theme rotation residue from 198 mod 5) |
| `multi_factor_combination` count | 33 (with ±2 tolerance per Q11) | 0 |

### §5.2 Verification checks at post-main-batch operational register

Per Component 4 verification register binding + Q11/Q12/Q13 LOCKED:

| Check | Specification | Failure consequence |
|---|---|---|
| 1 — Theme cardinality | Post-main-batch theme-cardinality = 6 distinct themes | Per Q12: escalate to scoping cycle adjudication |
| 2 — Theme content | Theme distribution includes `multi_factor_combination` AND 5 canonical Stage 2c/2d themes | Per Q12: escalate to scoping cycle adjudication |
| 3 — Per-theme cardinality (Q11) | Per-theme cardinality = 33 ± 2 (range 31-35) | Per Q12: escalate to scoping cycle adjudication |
| 4 — `multi_factor_combination` operational verification | `multi_factor_combination` per-theme cardinality = 33 ± 2; canonical `b6fcbf86` has 0; binds end-to-end Q9 + Q10 code-surface modification register at operational fire | Per Q12: escalate to scoping cycle adjudication |

### §5.3 Verification register failure signal binding

Per scoping §6.2 Component 4 verification register failure signal verbatim + Q12 LOCKED:

If post-mining new candidate basis matches canonical-basis distribution at register-precision register (i.e., new mining reproduces `b6fcbf86` at register-class-comparable distribution; OR theme-cardinality fails; OR per-theme cardinality fails; OR `multi_factor_combination` operational verification fails) — **the "materially different basis" pre-registration condition fails; sub-spec discipline burden returns cycle to scoping cycle adjudication rather than proceeding to evaluation register; in-arc retry explicitly banned; one-cycle-falsifiability preserved at single-cycle register-precision.**

### §5.4 Anti-§5-guardrail bindings explicit at Component 4

| Guardrail | Binding |
|---|---|
| §5 guardrail 6 | Material-different-basis distinction pre-registered at sub-spec SEAL; post-mining "actually use different distinction register-class" explicitly banned |
| §5 guardrail 7 | Verification register failure signal triggers escalation; one-cycle-falsifiability preserved at single-cycle register-precision (no in-arc retry) |
| §5 guardrail 8 | Component 4 verification check criteria pre-registered at sub-spec SEAL; post-mining reinterpretation of verification check outcomes explicitly banned |

---

## §6 Evaluation specification (Component 5 + Component 6)

### §6.1 Evaluation-slice 4-element exhaustive enumeration (Component 5)

Per Component 5 LOCKED + scoping §6.2 Component 5 verbatim 4-element exhaustive enumeration register-precision register:

#### §6.1.1 Element 1 — Primary slice

**Q14 (γ) LOCKED:** Full N=198 main batch population at primary disposition register; PHASE2C_11 conservative N_eff = N_raw lockpoint preserved per §3.2 reuse binding. §4.4-filter-equivalent subset (n_eligible ≈ 154 at register-class-comparable canonical `b6fcbf86` register) at secondary descriptive register only.

#### §6.1.2 Element 2 — Secondary slices (5 enumerated)

| (#) | Secondary slice | Register-class |
|---|---|---|
| (a) | Per-theme disposition descriptive | 6 themes × 33±2 per-theme cohort; descriptive register only |
| (b) | Smoke quality-mechanics descriptive | (A)+(B)+(C) rates; descriptive register only |
| (c) | **Q15 [REVISED]:** N_eff sensitivity ∈ **{198, 80, 40, 6}** | Pre-registered at sub-spec SEAL; descriptive register only; semantic-reuse at "number of operational themes" per PHASE2C_11 §5.3 + §5.4 binding (PHASE2C_11 N_eff=5 ↔ 5 themes; PHASE2C_12 N_eff=6 ↔ 6 themes) |
| (d) | PHASE2C_11 canonical-basis comparison descriptive | vs `b6fcbf86` `artifact_evidence` at SR_max=0.9602178531387877; argmax_p_value=0.999997737801711; descriptive register only |
| (e) | Per-candidate disposition tally descriptive | Per-candidate `signal_evidence` / `artifact_evidence` / `inconclusive` count; descriptive register only |

#### §6.1.3 Element 3 — Inclusion/exclusion filters (4 pre-registered)

| Filter | Specification | Source |
|---|---|---|
| A | **Q16 (α) LOCKED [Path A patch at SEAL pre-fire #7]:** PHASE2C_11 §4.4 edge-case filter reused: **`T_c < 5` EXCLUDED** per [PHASE2C_11_PLAN §4.4 line 346 verbatim](PHASE2C_11_PLAN.md); n_eligible parallel to PHASE2C_11 n=154/198 retention rate (~78%) at register-class-comparable register-precision register | PHASE2C_11 §4.4 reuse |
| B | Lifecycle state filter (exclude `proposer_invalid_dsl`/`duplicate`/`critic_rejected`/`train_failed`) | CLAUDE.md hypothesis lifecycle states |
| C | Engine-version filter via `check_evaluation_semantics_or_raise()` corrected-engine guard | RS-guard binding per §2.4 |
| D | Compilation-cleanliness filter (exclude ManifestDriftError) | CLAUDE.md DSL Compiler Integrity |

Filter logic + threshold values + register-class-eligibility scope pre-registered at this sub-spec drafting cycle BEFORE mining fires; post-hoc filter parameter adjustment EXPLICITLY BANNED per §5 guardrail 6 binding.

#### §6.1.4 Element 4 — Aggregation rule

| Register | Aggregation rule |
|---|---|
| Smoke | Gate-fire register (PASS/FAIL only); NOT primary aggregation input |
| Main | Test-fire register (canonical-disposition input at simplified DSR-style screen) |
| Cross-batch concordance check | Smoke-PASS-as-precondition-for-main; register-class-distinct from aggregation |
| Within-main candidate aggregation | Per PHASE2C_11_PLAN §3.6 conservative AND-gate routing verbatim — **LOCKED at Component 6 (a) reuse disposition** per §3.6 + §6.2 below |

### §6.2 Component 5 anti-§5-guardrail bindings explicit (LOAD-BEARING register-class)

| Guardrail | Binding |
|---|---|
| §5 guardrail 6 | Element 3 filter logic + thresholds pre-registered at sub-spec SEAL; post-mining filter parameter adjustment EXPLICITLY BANNED |
| §5 guardrail 7 | Single primary disposition register (Element 1 main batch only); single aggregation rule register (Element 4); one-cycle-falsifiability preserved |
| **§5 guardrail 8 (LOAD-BEARING)** | Component 5 binding lives at this guardrail register. Post-result re-labeling of secondary slices (a)-(e) as primary slice EXPLICITLY BANNED; smoke-vs-main register-class-distinct semantics pre-registered at register-precision; 4-register-class post-hoc selection ban (subsets / batches / configurations / reporting slices) all pre-registered exhaustive at Element 1-4 |

### §6.3 Evaluation-threshold full-framework reuse (Component 6)

Per Component 6 LOCKED + Q17 LOCKED (a) reuse + S2 patch full-framework reuse binding: PHASE2C_12 inherits PHASE2C_11 simplified DSR-style framework at five register-class-distinct elements per §2.1 above (formula + N choice + threshold values + routing logic + disposition labels).

#### §6.3.1 Substantive ground for (a) reuse — controlled-experiment principle binding

PHASE2C_12 isolates ONE variable (candidate basis) at breadth-expansion arc designation. Threshold redefinition would confound new-basis effect with threshold-redefinition effect, breaking the breadth-expansion test register-class-isolation property. Four substantive grounds:

1. **§6.7 register-class-comparable comparison binding (LOAD-BEARING).** PHASE2C_12 evaluates a NEW candidate basis against the SAME evaluation framework as PHASE2C_11 canonical disposition. If thresholds are redefined, "different result" becomes confounded between (i) new candidate basis register-class effect AND (ii) threshold-redefinition register-class effect. Reuse holds the threshold framework constant across canonical vs new-basis register, allowing the breadth-expansion finding to bind at register-class-comparable register-precision register.

2. **Anti-fishing-license discipline.** Threshold redefinition at sub-spec drafting cycle creates a register surface for "calibrate thresholds to give better disposition outcomes" even WITH pre-registration. Reuse forecloses this register surface entirely.

3. **§4.7 canonical Bailey-López de Prado DSR deferred prerequisite preservation.** Canonical-DSR scope expansion is its OWN register-class-eligible successor path per scoping §6.4 (Path A or Path B prerequisite work register). Threshold redefinition at PHASE2C_12 sub-spec drafting cycle without canonical-DSR work register firing would be arbitrary at simplified-register-class scope. Canonical-DSR scope expansion is a register-class-distinct successor path; PHASE2C_12 breadth expansion arc does NOT subsume it.

4. **Anti-§5-guardrail-6 + Anti-§4.4-arc-designation discipline.** PHASE2C_12 sub-spec is bound at §4.4 arc designation = breadth expansion arc (new candidate basis register-class only). Threshold redefinition would add a register-class axis (evaluation-threshold variation) beyond breadth expansion, broadening sub-spec scope beyond the §4.4 arc designation.

#### §6.3.2 Counter-considerations evaluated

- **Counter 1 (post-result-thinking inversion):** "Maybe theme rotation 6/6 produces less correlation among candidates → maybe N_eff treatment could be less conservative?" **Adjudication:** This is exactly the kind of post-result-thinking that §5 guardrail 9 + §3.2 conservative N_eff lockpoint discipline are designed to bound. Pre-register reuse → conservative N_eff = N_raw = 198 stays at primary register. Sensitivity register at N_eff ∈ {198, 80, 40, 6} per Q24 already covers descriptive-only correlation-sensitivity probe at semantic-reuse register.
- **Counter 2 (multi_factor_combination novelty):** "Maybe multi_factor_combination at 6th theme has different statistical properties → different per-theme N treatment?" **Adjudication:** §3.2 lockpoint operates on TOTAL N (raw N=198), not per-theme N. Per-theme cohort is descriptive-register only per Component 5 Element 2 secondary slices.

### §6.4 Q23 Component 6 binding scope main-only register

**Component 6 binding scope = main register only.** Smoke PASS criteria from Component 2 Q2 are **candidate-quality gate thresholds**, NOT evaluation-threshold-register thresholds under Component 6. They are **excluded from §5 guardrail 9 scope** except insofar as **post-smoke mutation remains banned under Component 2's pre-registration binding**.

Register-class-distinct semantics:
- **Smoke** = candidate-quality gate (Component 2 Q2 quality-mechanics composite AND-gate at canonical-baseline-relative ≥ 0.9× per criterion)
- **Main** = evaluation threshold (Component 6 simplified DSR-style screen at full-framework reuse PHASE2C_11)

### §6.5 Component 6 verification register failure signal

Per scoping §6.2 Component 6 verbatim binding + parallel to Component 4 Q12 + Component 5 verification register failure signal (three register-class-distinct sub-spec-vs-scoping-cycle clean separation patterns at register-precision register-binding):

If sub-spec drafting cycle adjudicates that evaluation-threshold pre-registration cannot be locked at register-class-eligible scope BEFORE mining fires (threshold framework reuse-or-redefine binding unmet OR threshold class enumeration incomplete), **path (g) selection is escalated back to scoping cycle adjudication per §5 guardrail 7 binding** — NOT loosened to post-hoc-threshold-mutation register.

At PHASE2C_12 sub-spec drafting cycle: this verification register failure signal does NOT fire (Q17 LOCKED (a) reuse at register-class-eligible scope; threshold class enumeration COMPLETE per §3.6 + §6.3 above).

---

## §7 Q1-Q25 LOCKED summary

| Q | LOCKED disposition | Source register |
|---|---|---|
| Q1 | Smoke count = 40 | §3.2 Component 2 |
| Q2 | Composite AND-gate (A)+(B)+(C); canonical-baseline-relative threshold ≥ 0.9× per criterion | §3.2 Component 2 |
| Q3 | Main count = 198 | §3.2 Component 2 |
| Q4 | Smoke-fail-stop = (b) escalation to scoping cycle | §3.2 Component 2 |
| Q5 | Smoke-PASS to main = (i) Charlie-register gate at smoke-vs-main boundary | §3.2 Component 2 |
| Q6 | Uniform 6/6 = 1/6 each (33 per theme) | §3.3 Component 3 |
| Q7 | Smoke = 40 cycles at 1 candidate per cycle | §3.3 Component 3 |
| Q8 | Main = 198 cycles at 1 candidate per cycle | §3.3 Component 3 |
| Q9 | Smoke theme operationalization = (β) conditional theme override at proposer entry | §3.3 Component 3 |
| Q10 | Main rotation flip operationalization = (β) config parameter at engine entry [reviewer convergence at (β) post-Q10 divergence cycle] | §3.3 Component 3 |
| Q11 | Per-theme cardinality tolerance = ±2 (range 31-35) | §3.4 Component 4 |
| Q12 | Verification failure → escalate to scoping cycle | §3.4 Component 4 |
| Q13 | Empirical verification carry-forward approved | §3.4 Component 4 |
| Q14 | Primary slice = (γ) full N=198 primary + §4.4-filter subset secondary descriptive | §3.5 Component 5 |
| Q15 [REVISED M6-F2 (ii)] | Pre-register N_eff sensitivity ∈ **{198, 80, 40, 6}** at sub-spec SEAL (semantic-reuse at "number of operational themes" register) | §3.5 Component 5 |
| Q16 [Path A patch] | Filter A threshold = (α) reuse PHASE2C_11 §4.4 edge-case filter: **`T_c < 5` EXCLUDED** per PHASE2C_11_PLAN §4.4 line 346 verbatim; n_eligible parallel to PHASE2C_11 n=154/198 | §3.5 Component 5 |
| Q17 | (a) reuse PHASE2C_11 canonical thresholds at full register-precision (full-framework reuse 5-element binding) | §3.6 Component 6 |
| Q18 | N=198 per PHASE2C_11 §3.2 lockpoint | §3.6 Component 6 |
| Q19 | p<0.05 pass threshold per §3.6 verbatim | §3.6 Component 6 |
| Q20 [PATCH S1] | Bonferroni fail = SR_max ≤ 3.252158; DSR-style fail = argmax_p_value ≥ 0.5; artifact_evidence requires BOTH | §3.6 Component 6 |
| Q21 | PHASE2C_11_PLAN §3.6 conservative AND-gate routing verbatim | §3.6 Component 6 |
| Q22 | `signal_evidence` / `artifact_evidence` / `inconclusive` per PHASE2C_11 register-precedent | §3.6 Component 6 |
| Q23 [PATCH S3] | Component 6 main-only scope; smoke = candidate-quality gate orthogonal register-class | §3.6 + §6.4 Component 6 |
| Q24 [M6-F2 (ii)] | N_eff sensitivity ∈ **{198, 80, 40, 6}** semantic-reuse register | §3.6 Component 6 |
| Q25 | §3.6 P5 patch verbatim (statistical-evidence vs tradable-edge distinction preserved) | §3.6 Component 6 |

**Cumulative count:** 25 Q-questions LOCKED across Components 1-6.

---

## §8 Implementation activity register

### §8.1 Sequenced steps (post-SEAL operational fire register; out of sub-spec drafting cycle scope)

PHASE2C_12 implementation arc fires at post-SEAL operational register per `feedback_authorization_routing.md` Charlie-register gate at every operational fire boundary. Steps below are register-precision register-binding for post-SEAL implementation arc; NOT fired at this sub-spec drafting cycle register.

| Step | Activity | Authorization gate |
|---|---|---|
| 1 | Q9/Q10 code-surface modification register (smoke theme override at proposer entry; THEME_CYCLE_LEN config-driven at engine entry) | Charlie-register authorization at code-surface modification fire |
| 2 | Smoke batch fire (40 candidates, 100% multi_factor_combination); RS-guard call on every artifact consumption | Charlie-register authorization at smoke fire |
| 3 | Smoke PASS criteria adjudication at composite AND-gate (A)+(B)+(C); canonical-baseline-relative ≥ 0.9× per criterion | Per §4.1 smoke PASS criteria; reviewer convergence necessary input |
| 4 | Smoke-PASS-to-main transition at Charlie-register gate per Q5 LOCKED | Charlie-register authorization at smoke-vs-main boundary |
| 5 | Main batch fire (198 candidates, uniform 6/6 theme rotation); RS-guard call on every artifact consumption | Charlie-register authorization at main fire |
| 6 | Component 4 verification checks 1-4 at post-main-batch operational register | Per §5.2 verification checks; failure → escalate to scoping cycle adjudication per Q12 |
| 7 | PHASE2C_8.1 register-class evaluation gate fire (bear_2022 + validation_2024 + eval_2020_v1 + eval_2021_v1) | Per PHASE2C_8.1 spec; corrected-engine `eb1c87f` + `wf-corrected-v1` lineage |
| 8 | Simplified DSR-style screen disposition adjudication via `compute_simplified_dsr()` reused at full-framework register | Per Q17 + §3.6 Component 6 LOCKED |
| 9 | Closeout deliverable authoring at `docs/closeout/PHASE2C_12_RESULTS.md` per closeout-arc precedent (PHASE2C_11_RESULTS.md structural-template register) | Closeout reviewer pass + Charlie-register seal at closeout register |

### §8.2 Step gating criteria

- No mining fires before sub-spec SEAL (this plan's seal commit + Phase Marker advance commit + push)
- No main batch fires before smoke PASS at composite AND-gate criteria + Charlie-register authorization
- No evaluation gate fires before main batch operational fire CLEAN at Component 4 verification checks
- No closeout deliverable seals before reviewer pass cycle CLOSED + Charlie-register seal authorization

### §8.3 No result computation before sub-spec SEAL

Per §0.4 + §5 guardrails 6 + 9: no PHASE2C_12 mining, evaluation, or disposition computation fires before this sub-spec SEAL register clears at canonical artifact register + SEAL pre-fire empirical verification register CLEAN + Charlie-register seal authorization.

---

## §9 Reviewer routing + M5/M6/M7 disposition record

### §9.1 Reviewer pass cycle architecture

Sequential routing locked per [PHASE2C_11_PLAN §8 + scoping decision §7.2 precedent](PHASE2C_11_SCOPING_DECISION.md) + handoff §16:

| Pass | Reviewer | Pass scope | Status at this v1 draft register |
|---|---|---|---|
| M5 | ChatGPT first-pass | Structural overlay: section completeness; cross-reference precision; table format consistency; §6.2 Component 6 verbatim binding compliance; §5 guardrail 9 LOAD-BEARING binding completeness; anti-§5-guardrail-cross-reference completeness; Q-question framework register-class consistency | CLOSED at conversation-register draft pass |
| M6 | Claude advisor full-prose-access | Substantive prose-access pass per METHODOLOGY_NOTES §16 anchor-prose-access discipline; wording precision at lockpoint citations; substantive register-class-eligibility | CLOSED at conversation-register patched draft pass |
| M7 | Fresh-register full-file pass per METHODOLOGY_NOTES §17 sub-rule 4 | Cross-section consistency / cross-reference precision / table format consistency / §6.2 verbatim binding compliance / guardrail 9 completeness / Q-question framework consistency / reuse-vs-redefine register-binding precision / verification register failure signal parallel / bilingual register-class / main-only binding clarity / cascade completeness / §6.5 + Q15 + Q24 cascade-update consistency | CLOSED at 12/12 CLEAN |
| Codex | Skipped per scoping-doc + sub-spec register precedent ([`feedback_codex_review_scope.md`](../../) memory; [PHASE2C_10 + PHASE2C_11 scoping cycle precedent](PHASE2C_10_SCOPING_DECISION.md)) | Not applicable at sub-spec drafting cycle | N/A |

### §9.2 M5 ChatGPT first-pass findings (CLOSED)

Verdict: mostly CLEAN, with 2 required patches and 1 optional clarity patch before advisor M6.

| Finding | Severity | Disposition | Patch reference |
|---|---|---|---|
| S1 — Tighten Q20 fail criterion wording | M5 marked "Required"; advisor reframed as wording (M5 over-stated severity) | ACCEPTED with precision adjustment to 6 decimals (`3.252158`) per advisor pushback (ChatGPT proposed 14 decimals; advisor flagged precision-overshoot at explanatory-prose register) | Applied at Q20 (§3.6) |
| S2 — Reuse scope explicit framework binding | Load-bearing | ACCEPTED — 5-element framework reuse statement (formula + N choice + threshold values + routing logic + disposition labels) at §C6.3; anti-register-leakage binding at register-precision | Applied at §2.1 + §6.3 PATCH S2 |
| S3 — Q23 smoke criteria explicit register-class | Clarity (M5 "Optional") | ACCEPTED — register-class-distinct framing explicit (smoke = candidate-quality gate; main = evaluation threshold); cross-reference Component 2 pre-registration anti-mutation binding | Applied at Q23 (§3.6) + §6.4 |

### §9.3 M6 Claude advisor full-prose-access findings (CLOSED)

| Finding | Severity | Disposition |
|---|---|---|
| F1 — §C6.3 Ground 1 substantive observation (controlled-experiment principle pre-registration register binding subtlety) | Observation | NOT patch-required; carry-forward only at register-precision register; current §6.3.1 prose adequate |
| **F2 — Q15/Q24 N_eff sensitivity completeness gap** | **MEDIUM substantive** | **(ii) ratified at Charlie-register: {198, 80, 40, 6} semantic reuse at "number of operational themes" register-precision per PHASE2C_11 §5.3 + §5.4 binding** |
| F3 — Q19+Q20 partial overlap (p≥0.5 appears in both) | Clarity (LOW) | NOT patch-required at sub-spec drafting register; ChatGPT S1 patch implicitly addresses via Q20 restructure; defer further restructure to canonical-artifact authoring at Step 7 if substantive |

### §9.4 M7 fresh-register full-file pass findings (CLOSED)

12 verification dimensions at fresh-register full-file pass per METHODOLOGY_NOTES §17 sub-rule 4: 12/12 CLEAN. No new findings.

| # | Dimension | Status |
|---|---|---|
| 1 | Cross-section consistency: §C6.0 bilingual framing → §C6.3 substantive case → §C6.4 Q17-Q25 dispositions → §C6.5 cascade table | CLEAN |
| 2 | Cross-reference precision: §C6.1 cites scoping decision lines 779-796; §C6.3 cites §6.7 + §4.4 + §4.7 + §6.4 + §5 guardrails | CLEAN |
| 3 | Table format consistency at Components 1-5 LOCKED bindings tables | CLEAN |
| 4 | §6.2 Component 6 verbatim binding compliance: 3 threshold classes covered; reuse-or-redefine binding at Q17; mixed reuse-and-redefine ban preserved | CLEAN |
| 5 | §5 guardrail 9 LOAD-BEARING completeness; register-class-distinct framing across guardrails 6 + 8 + 9 preserved | CLEAN |
| 6 | Q-question framework consistency Q17-Q25 vs Q1-Q16 register-precedent | CLEAN |
| 7 | Reuse-vs-redefine register-binding precision; counter-considerations evaluated | CLEAN |
| 8 | Verification register failure signal parallel to Component 4 Q12 + Component 5 | CLEAN |
| 9 | Bilingual concept explanation register-class per `feedback_bilingual_concept_explanation.md` | CLEAN |
| 10 | Main-only binding clarity (Q23 PATCH S3) | CLEAN |
| 11 | Cross-component cascade completeness (§C6.5) | CLEAN |
| 12 | §C6.5 + Q15 + Q24 cascade-update consistency post-M6-F2-(ii) patch | CLEAN |

### §9.5 M7 register-class compromise observation (carry-forward; NOT blocking)

Per [scoping decision §7.2 M6 advisor pass register-class compromise note](PHASE2C_12_SCOPING_DECISION.md) precedent: M7 fresh-register full-file pass was executed by **same agent that authored Component 6 draft + applied patches** (Claude Code as sub-spec author at fresh-register state per session entry pre-fire audit). Per METHODOLOGY_NOTES §17 sub-rule 4, M7 ideally fires at register-class-distinct from sub-spec author register. PHASE2C_12 sub-spec M7 has parallel register-class-compromise at fresh-register-via-same-agent register.

**Procedural impurity at attribution register; substantive analysis quality preserved at content register.** Non-blocking. Carry-forward to next methodology consolidation cycle as register-class-eligible methodology refinement candidate (joining METHODOLOGY_NOTES §16 sub-rule "WHO reads prose at WHICH register" codification candidate per scoping cycle §6.3 entry 4).

---

## §10 Empirical verification register (SEAL pre-fire; NOT yet fired at this v1 draft register)

Per advisor §5 prevention discipline + METHODOLOGY_NOTES §1 + §19 binding + handoff §11 step 2 binding: **9 cumulative empirical verifications fire AGAINST this canonical artifact text register at SEAL pre-fire register before Charlie-register seal authorization**. Per Charlie + ChatGPT + advisor convergence at handoff Option (B) authorization: verifications fire at Step 7 SEAL pre-fire register only (NOT at conversation-register draft register; NOT at reviewer pass cycle register; clean single-shot pipeline: draft → critique → stabilize → verify → seal).

### §10.1 9-verification register-binding

| # | Verification target | Component source | Verification register |
|---|---|---|---|
| 1 | Canonical baseline rates for criteria (A) DSL-validity + (B) Critic-approved/`pending_backtest` + (C) Compilation-cleanliness at canonical PHASE2C_8.1 `b6fcbf86` mining batch register | Component 2 Q2 + §4.1 smoke PASS criteria | PHASE2C_8.1 `b6fcbf86` artifact register; verify canonical baseline rates at register-precision binding for ≥ 0.9× threshold register-binding |
| 2 | PHASE2C_8.1 `b6fcbf86` actually used 1-candidate-per-cycle generation pattern | Component 3 Q7 + Q8 | `experiments.db` query OR `data/batches/<batch_id>/` artifact register; per-batch generation-cycle vs candidate count match at 1:1 ratio |
| 3 | `b6fcbf86` actual theme distribution: `multi_factor_combination` count = 0 + per-theme distribution at register-class-comparable cardinality (40/40/40/39/39 per CLAUDE.md PHASE2C_9 Step 2 anchor) | Component 4 Q13 | `experiments.db` OR `data/batches/<batch_id>/` artifact register |
| 4 | Canonical THEMES tuple at `agents/themes.py` = 6 themes with `multi_factor_combination` as 6th theme at canonical anchor register | Component 4 Q13 | `agents/themes.py` empirical state; cross-verify against `expectations.md` + `blueprint/PHASE2_BLUEPRINT.md` per CLAUDE.md F7 verification reads |
| 5 | Q9 specific function/code-location for conditional theme override (`_theme_for_position` or equivalent at proposer entry register-precision) | Component 3 Q9 | `agents/proposer/stage2c_batch.py:156-158` + `agents/proposer/stage2d_batch.py:198-200` empirical state; verify `_theme_for_position(k: int) -> str` function exists at cited line ranges |
| 6 | Q10 specific config-driven implementation surface (env var name OR config.yaml key + default value semantic at PHASE2C_12 main batch fire register) | Component 3 Q10 | Sub-spec adjudicates specific implementation surface at sub-spec SEAL pre-fire — DEFERRED at this canonical artifact: implementation surface adjudicated at post-SEAL §8.1 Step 1 fire register; verification deferred to post-SEAL implementation arc |
| 7 | PHASE2C_11 §4.4 edge-case filter actual threshold value verbatim | Component 5 Q16 | **VERIFIED CLEAN at Path A patch register: PHASE2C_11_PLAN §4.4 line 346 verbatim = "Low trade count (`T_c < 5`): candidate excluded"** — actual filter is `T_c < 5` EXCLUDED (NOT "≥20 trades"; "≥20 trades" is PHASE2C_8.1 audit_v1_filtered cohort, register-class-distinct from PHASE2C_11 §4.4 primary). n_eligible at PHASE2C_11 = 154/198 (per closeout MD §3 + Step 3 deliverable §5.1). Path A patch applied at §3.5 + §6.1.3 + §7 Q16 + this row at §10.1 V#7 to resolve handoff §10 V#7 spec-vs-empirical-reality finding pattern instance #1 at PHASE2C_12 sub-spec drafting cycle canonical-artifact register. |
| 8 | PHASE2C_11_PLAN §3.6 verbatim text — pass threshold + fail threshold + inconclusive register | Component 6 Q19 + Q20 + Q21 | `docs/phase2c/PHASE2C_11_PLAN.md` lines 244-256 |
| 9 | `compute_simplified_dsr()` implementation surface verification — function signature + numerical inputs (N_eff=198, pass p<0.05, fail p≥0.5, Bonferroni √(2·ln(198))) match §3.6 prose register-binding at register-precision | Component 6 reuse-binding implementation register | `backtest/evaluate_dsr.py:956-1278` empirical verification at sub-spec SEAL pre-fire |

### §10.2 Verification fire timing

Per handoff Option (B) authorization + advisor sequencing rationale (clean single-shot pipeline; verification not part of drafting; verification is part of commit validation):

1. v1 canonical artifact authored CLEAN at this register (this commit's draft register; pre-SEAL)
2. SEAL pre-fire: 9 empirical verifications fire AGAINST canonical artifact text register
3. If any verification surfaces register-precision-violation: patch applied at canonical artifact register OR escalate to Charlie-register adjudication per §0.4 resolution path
4. If 9/9 CLEAN: Charlie-register seal authorization fires
5. Seal commit at this canonical artifact + Phase Marker advance separate commit per §7.4-precedent + push + dual-channel ping

### §10.3 Verification register failure consequence

Per §0.4 resolution path: if any of 9 verifications surfaces canonical-artifact-register-precision-violation at SEAL pre-fire register, the affected lockpoint is treated as inconclusive at PHASE2C_12 sub-spec drafting cycle register; resolution path per §0.4 (a) document at full register-precision; (b) treat affected lockpoint as inconclusive; (c) defer to post-SEAL successor cycle for re-specification; (d) Component 4/5/6 verification register failure signal binding routes back to scoping cycle adjudication if substantive at register-class register.

---

## §11 Cross-references

### §11.1 PHASE2C_12 cross-references

- [`docs/phase2c/PHASE2C_12_SCOPING_DECISION.md`](PHASE2C_12_SCOPING_DECISION.md) — scoping decision MD sealed at `541c0be`; 895 lines / 9 sections / 35 sub-sections; §6.2 6-component sub-spec pre-registration framework + §4.4 arc designation (breadth expansion) + §4.1 dominant uncertainty + §5 9-guardrail enumeration verbatim binding source

### §11.2 PHASE2C_11 cross-references

- [`docs/phase2c/PHASE2C_11_PLAN.md`](PHASE2C_11_PLAN.md) — sub-spec v3.2 sealed at `8bc12de`; 726 lines / 9 sections / 35 sub-sections; §3.2 trial count lockpoint + §3.6 conservative AND-gate routing + §4 simplified DSR-style screen specification + §5.4 sensitivity table specification — full-framework reuse anchor source per Q17 + §2.1
- [`docs/closeout/PHASE2C_11_RESULTS.md`](../closeout/PHASE2C_11_RESULTS.md) — closeout MD sealed at `5dba0df`; primary register disposition = `artifact_evidence` at simplified DSR-style screen; §1-§9 numerical anchors + canonical disposition register-class-comparable comparison anchor source
- [`docs/phase2c/PHASE2C_11_STEP3_DELIVERABLE.md`](PHASE2C_11_STEP3_DELIVERABLE.md) — Step 3 deliverable sealed at `6315ec0`; numerical-anchor register; result artifact at `data/phase2c_evaluation_gate/audit_v1/_step3_result.json` sha256=`64f733833e3cc47d32fc3a81c3f603c54c478c2064b455d161dbab6dff82ae03`
- [`docs/phase2c/PHASE2C_11_SCOPING_DECISION.md`](PHASE2C_11_SCOPING_DECISION.md) — sub-spec pre-registration paragraph framework precedent

### §11.3 PHASE2C_10 cross-references

- [`docs/phase2c/PHASE2C_10_SCOPING_DECISION.md`](PHASE2C_10_SCOPING_DECISION.md) — anti-pre-naming option (ii) precedent at sub-spec SEAL register-binding scope
- [`docs/closeout/PHASE2C_10_METHODOLOGY_CONSOLIDATION_SIGNOFF.md`](../closeout/PHASE2C_10_METHODOLOGY_CONSOLIDATION_SIGNOFF.md) — methodology consolidation cycle precedent

### §11.4 PHASE2C_8.1 cross-references

- [`docs/phase2c/PHASE2C_8_1_PLAN.md`](PHASE2C_8_1_PLAN.md) — multi-regime evaluation gate spec; PHASE2C_12 main batch evaluates at PHASE2C_8.1 register-class scope
- [`docs/closeout/PHASE2C_8_1_RESULTS.md`](../closeout/PHASE2C_8_1_RESULTS.md) — extended multi-regime results closeout; canonical mining batch_id `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` reference register

### §11.5 PHASE2C_9 cross-references

- [`docs/closeout/PHASE2C_9_RESULTS.md`](../closeout/PHASE2C_9_RESULTS.md) — mining-process retrospective; §8.4 factor-set repetition rate ~28.79% empirical evidence at cross-trial dependency register-binding source

### §11.6 METHODOLOGY_NOTES cross-references

- [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) §§1, 10, 16, 17, 19, 20 — discipline anchors at §0.3 + §10 SEAL pre-fire empirical verification register binding source

### §11.7 TECHNIQUE_BACKLOG cross-references

- [`strategies/TECHNIQUE_BACKLOG.md`](../../strategies/TECHNIQUE_BACKLOG.md) §2.2.3 — RS corrected-engine consumer-side discipline binding source

### §11.8 Code module cross-references

- [`agents/themes.py`](../../agents/themes.py) — canonical THEMES tuple (6 themes); Component 4 register-class anchor; SEAL pre-fire empirical verification #4 source
- [`agents/proposer/stage2c_batch.py`](../../agents/proposer/stage2c_batch.py) `THEME_CYCLE_LEN = 5` at line 93 + `_theme_for_position(k: int)` at lines 156-158 — Q9 + Q10 implementation surface; SEAL pre-fire empirical verification #5 source
- [`agents/proposer/stage2d_batch.py`](../../agents/proposer/stage2d_batch.py) `THEME_CYCLE_LEN = 5` at line 112 + `_theme_for_position(k: int)` at lines 198-200 — Q9 + Q10 implementation surface
- [`backtest/evaluate_dsr.py:956-1278`](../../backtest/evaluate_dsr.py) — `compute_simplified_dsr()` canonical implementation; full-framework reuse anchor per Q17; SEAL pre-fire empirical verification #9 source
- [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) — RS-guard consumer-side discipline source per §2.4

### §11.9 Decision document cross-references

- [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md) Section RS — corrected-engine consumption discipline binding source

### §11.10 Memory cross-references

- [`feedback_authorization_routing.md`](../../) — Charlie-register gate at every operational fire boundary
- [`feedback_reviewer_suggestion_adjudication.md`](../../) — per-finding adjudication discipline at reviewer cycle (operationalized at Q10 + M6-F2 reviewer divergence cycles)
- [`feedback_codex_review_scope.md`](../../) — Codex skip at sub-spec drafting cycle register precedent
- [`feedback_bilingual_concept_explanation.md`](../../) — bilingual concept explanation register-class binding at §6.3 + scoping decision cycle precedent
- [`feedback_long_task_pings.md`](../../) — dual-channel ping at SEAL fire boundary
- [`feedback_use_planning_skills_for_complex_tasks.md`](../../) — sub-spec drafting cycle as planning-skill instance precedent

---

**End of PHASE2C_12 sub-spec canonical artifact v1 draft.** SEAL pre-fire empirical verification register (§10) fires next at Charlie-register authorization; if 9/9 CLEAN, Charlie-register seal authorization → SEAL commit + Phase Marker advance separate commit per §7.4-precedent + push + dual-channel ping per `feedback_long_task_pings.md`.
