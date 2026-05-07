# PHASE2C_14 — Strategy Refinement Sub-spec (Path (a) Anchor)

**Status:** WORKING DRAFT (sub-spec drafting cycle in progress)
**Scoping decision SEAL:** [`PHASE2C_14_SCOPING_DECISION.md`](PHASE2C_14_SCOPING_DECISION.md) at `33107d6` (527 lines / 58 §§ + sub-§§)
**Path:** (a) Strategy refinement sub-spec drafting cycle anchor per scoping decision §4.2
**Cycle scope register-class:** evidence-interpretation refinement arc (NOT system redesign arc); framing adopted at Q-S107 register-event boundary per Charlie register convergence approval (substantive characterization at §1.3)
**Authorship register:** Charlie register authorization at Q-S107 ENDORSE; sub-spec drafting cycle per scoping decision §6.4 canonical seven-step activity sequencing.

---

## §0 Document scope and structure

### §0.1 Scope

This sub-spec specifies **strategy refinement components** for PHASE2C_15 fire register-class-eligibility binding, plus the **anti-p-hacking pre-registration framework** that will gate PHASE2C_15 fire success register binding scope. It does **NOT**:

- Author batch parameters, theme rotation choices, Critic config, ledger pre-charge values, or any other PHASE2C_15 entry scoping cycle scope content (deferred per anti-pre-naming option (ii) preservation per scoping decision §6.5 register binding scope).
- Mutate framework code (`backtest/evaluate_dsr.py`, `agents/orchestrator/`, `agents/proposer/`, etc.) per scoping decision §1.4 #4 + H-1 (e) explicit prohibition register binding scope.
- Mutate METHODOLOGY_NOTES.md at canonical artifact register-class binding scope per H-1 (d) explicit prohibition register binding scope (6785 lines preserved invariant at sub-spec drafting cycle entry register binding scope).
- Re-adjudicate path selection, arc designation, or H-1/H-2/H-3 hard-constraint codification (sealed at scoping decision register binding scope at `33107d6`; reaffirmed not re-derived at §1.4 below).
- Author closeout deliverable scope or tag wording (deferred per scoping decision §6.6 + anti-pre-naming option (ii) binding register binding scope).

### §0.2 Structure

7 top-level §§ + ~28 sub-§§; **target length envelope ≤550 lines** per scope discipline register binding scope. Length envelope is itself a scope-creep guardrail at register-class match register binding scope to PHASE2C_13 sub-spec 1029-line register precedent + PHASE2C_11 sub-spec 724-line register precedent; H-1 empirical evidence basis (PHASE2C_13 ~3x scope creep at sub-spec drafting cycle register binding scope) applies recursively to this sub-spec authoring register binding scope.

**Per-§ scope-creep guardrail caps (compensating discipline at register-class match register binding scope):** **§3 ≤120 lines** + **§5 ≤40 lines** at register binding scope. Caps function as **diagnostic tripwires for governance creep** at register-class match register binding scope per H-1 empirical evidence basis register binding scope (NOT formatting constraints at register binding scope; budget pressure on §3 = signal of multi-batch evidence framework over-generalization at register-class match register binding scope; budget pressure on §5 = signal of governance reaffirmation drift at register-class match register binding scope). Pre-breach signal protocol register binding scope: surface-to-Charlie-register at approach-cap register binding scope (e.g., §3 approaching 110 with §3.3 substantively unwritten), NOT post-breach rationalization at register binding scope per H-3 functional-criterion anti-rationalization clause applied recursively register binding scope.

§ overview:
- §0 — Document scope and structure
- §1 — Locked inputs at sub-spec drafting cycle entry
- §2 — Strategy refinement components (§9.1 multi_factor_combination structured combination + §9.3 WF Sharpe first-pass filter SEMANTICS + §9.2 volatility_regime defer)
- §3 — Pre-registration framework (anti-p-hacking guardrail; Wilson CI canonical anchor at 2.07% strict-exceedance; multi-batch evidence requirement)
- §4 — PHASE2C_15 implementation arc structure preview (deferred per anti-pre-naming option (ii); preview-only register binding scope)
- §5 — Sub-spec drafting cycle guardrails (H-1/H-2/H-3 reaffirmation + sealed corpus invariance + §17 sub-rule 4 + Codex routing decision register binding scope)
- §6 — Verification chain and reviewer disposition
- §7 — Cross-references

### §0.3 Discipline anchors operating at this sub-spec drafting cycle

1. **Anti-pre-naming option (ii) preservation** per scoping decision §1.4 #1 + §6.5 + §6.6 binding register binding scope. PHASE2C_14 implementation arc Step structure + closeout deliverable scope + tag wording NOT pre-committed at this sub-spec register binding scope.
2. **Anti-momentum-binding strict reading** per [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md) hard rule register binding scope: each register-event boundary in this sub-spec drafting cycle (component checkpoints + reviewer pass routing + SEAL commit + Phase Marker advance + push) requires explicit Charlie register authorization at register-class match register binding scope. Reviewer convergence is advisory only at register binding scope.
3. **H-1 / H-2 / H-3 hard constraints binding throughout cycle scope** per scoping decision §1.4 verbatim binding register binding scope (reaffirmed not re-derived at §1.4 below; cited verbatim binding source at register-class match register binding scope).
4. **Sealed corpus invariance preserved** per Q-S79a unified-defer disposition register binding scope: METHODOLOGY_NOTES §27/§28/§29 + PHASE2C_13 sub-spec §2.7/§4.3 + §20.6 §A2 instances #26-#31 all preserved invariant at canonical-artifact register-class binding scope per H-1 (a) explicit prohibition register binding scope.
5. **Per-fix adjudication discipline** per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) register binding scope: reviewer findings adjudicated reasonably one-by-one at register-precision; no bulk-accept register binding scope.
6. **Bilingual concept anchor for difficult concepts** per [`feedback_bilingual_concept_explanation.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_bilingual_concept_explanation.md) register binding scope: H-1 bilingual anchor sealed at scoping decision §1.4. Bilingual anchor applied at this sub-spec layer where new substantive concepts are load-bearing register binding scope; specific sites determined at authoring register-event boundary register binding scope (NOT pre-named at this register per anti-pre-naming option (ii) preservation register binding scope). Restraint binding at register-class match register binding scope (bilingual register-class-distinct from translation register binding scope; reserved for genuinely difficult concepts at register binding scope).
7. **Cycle-scope register-class framing per §1.3** — discipline anchor pointer; substantive framing register binding scope at §1.3 (cycle-scope register-class characterization).
8. **§17 sub-rule 4 recursive operating rule** per METHODOLOGY_NOTES §17 sub-rule 4 register binding scope: full-file prose-access pass at sealed-commit register binding scope is mandatory at sub-spec SEAL register-event boundary register binding scope. Cycle count = 15 at PHASE2C_14 entry SEAL; advances to 16 at this sub-spec drafting cycle SEAL register-event boundary register binding scope.

---

## §1 Locked inputs at sub-spec drafting cycle entry

### §1.1 Engagement mode

Sub-spec drafting cycle at register-class match register binding scope to PHASE2C_10/11/12/13 sub-spec drafting cycle register precedent. Substantive scope: component-by-component sub-spec authoring at process / spec register-class binding scope per scoping decision §6.4 canonical seven-step activity sequencing register binding scope. **NO operational fire** at this cycle (NO new generation; NO new evaluation; NO strategy refinement implementation; NO framework code refactor; NO API spend) per scoping decision §1.4 #4 + H-1 (d)+(e) binding register binding scope.

### §1.2 Empirical state inherited at sub-spec drafting cycle entry

**Anchor commits at PHASE2C_14 entry SEAL register-event boundary** (verified at session entry register-event boundary per state verification batch register binding scope):
- HEAD = `46e4956` (Phase Marker advance commit at PHASE2C_14 entry SEAL bundle; pushed to origin/main; origin/main parity verified at register-precision register-class binding scope).
- PHASE2C_14 entry scoping decision SEAL = `33107d6` ([`PHASE2C_14_SCOPING_DECISION.md`](PHASE2C_14_SCOPING_DECISION.md), 527 lines / 58 §§ + sub-§§).
- **NO tag** at PHASE2C_14 entry scoping cycle SEAL per scoping cycle SEAL register precedent register binding scope (tags reserved for arc-level closeout SEAL register-class binding scope per §6.2 binding scope).
- METHODOLOGY_NOTES.md = **6785 lines** preserved invariant at canonical artifact register-class binding scope per H-1 (d) prohibition register binding scope (verified at session entry).

**PHASE2C_12 directional anchor preserved invariant at PHASE2C_13 close + PHASE2C_14 entry register binding scope** (canonical empirical input at strategy refinement register binding scope per scoping decision §1.2 verbatim register binding scope):

- **PHASE2C_12 baseline AND-gate rate:** 8/197 = **4.06%** at primary register (cross-regime AND-gate metric; PHASE2C_12 closeout §10.4 register binding scope).
- **95% Wilson CI at PHASE2C_12 baseline:** **[2.07%, 7.81%]** at register-precision register-class binding scope. Lower bound canonical anchor per scoping decision §6.2.1 register binding scope: **2.07% strict-exceedance** at PHASE2C_15 fire success register-class-eligibility binding; **immutable post-PHASE2C_15 fire register-event boundary** per anti-p-hacking guardrail register binding scope (parameter pre-lock at register-class match register binding scope to METHODOLOGY_NOTES §22 codification register binding scope).
- **§9.1 multi_factor_combination per-theme rate:** 9.1% (3/33 mfc) vs 3.0% (5/164 non-mfc) at PHASE2C_12 cycle register binding scope; mfc 95% Wilson CI **[3.14%, 23.57%]** (wide at n=33). 2-prop z-test **z=1.6044 / p=0.1086** + Fisher exact **OR=3.18 / p=0.1323** — **NOT significant at α=0.05** at PHASE2C_12 cycle sample size register binding scope per PHASE2C_12 closeout §9.1 verbatim sealed register binding scope. Distribution shape per PHASE2C_12 §9.1 verbatim: "**mfc bimodal distribution**: top performers (8 cross-regime survivors include 3 mfc) + degenerate tail" register binding scope. 8 cross-regime AND-gate survivors decompose as **3 mfc + 5 non-mfc** per PHASE2C_12 closeout §9.1 (canonical empirical basis for §2.1 structured combination DERIVATION at register-class match register binding scope per scoping decision §6.1 #2 "DERIVE not impose" binding register binding scope).
- **§9.2 volatility_regime zero-trade observation:** 0/32 = 0.0% at PHASE2C_12 cycle register binding scope (single-batch observation; multi-batch evidence required to distinguish systematic vs single-batch LLM stochasticity at register-precision register binding scope per PHASE2C_12 closeout §9.2 register binding scope).
- **§9.3 WF Sharpe filter coverage:** 5/8 AND-gate survivors at audit-only partition register binding scope (first-pass filter SEMANTICS register-class-distinct from compute-cost optimization register binding scope per PHASE2C_12 closeout §9.3 register binding scope).
- **8 AND-gate survivor factor compositions** at PHASE2C_12 cycle register binding scope: canonical empirical basis for §2.1 multi_factor_combination structured combination DERIVATION (DERIVED from survivor compositions, not imposed at register binding scope; per scoping decision §6.1 #2 binding register binding scope).

**PHASE2C_13 carry-forward register handoff** (at carry-forward register only; no PHASE2C_14 action per H-2 freeze framing register binding scope per scoping decision §6.3 register binding scope):
- Q-S79a 4-option survey on retroactive sealed-corpus revision; preserved at PHASE2C_13 close state register binding scope.
- Strong-tier promotion candidate evaluation (Candidate 1 ~65 ✓C1+✓C4 cumulative cross-cycle; Candidate 4 ~10 substantively at C1 threshold + ✓C4); preserved at PHASE2C_13 close state register binding scope.
- §10.5 substantive scaling-concern observation (cumulative §A2=33 + cross-cycle ~65 substantively exceeds §28 provisional threshold §19 > 15); preserved at PHASE2C_13 close state register binding scope per §28 Tier disposition diagnostic-surface-not-mitigation-mandate register precedent register binding scope.
- §10.7 NEW carry-forward register-class precedents (audit register-class precedent + Class A patch list expansion register-class precedent + Q-S89a (β) operational binding register-class precedent); preserved at PHASE2C_13 close state register binding scope.

### §1.3 Sub-spec drafting cycle goal

**Functional goal at register-precision register-class binding scope:** codify strategy refinement at three component register-binding-scope register binding scopes (§2.1 multi_factor_combination structured combination DERIVED from 8 AND-gate survivor compositions + §2.2 WF Sharpe first-pass filter SEMANTICS + §2.3 volatility_regime defer with multi-batch evidence requirement specification) AND author **pre-registration framework** anchored at Wilson CI lower-bound 2.07% strict-exceedance (immutable post-PHASE2C_15 fire register-event boundary register binding scope) such that PHASE2C_15 fire success register-class-eligibility binding is **pre-registered at register-precision** before any PHASE2C_15 batch fires register binding scope.

**Cycle-scope register-class:** **evidence-interpretation refinement** at register binding scope. PHASE2C_14 refines **selection semantics** over already-working infrastructure (proposer + Critic + walk-forward + DSR-style screen all stable at PHASE2C_8.1/9/10/11/12 cumulative cycle register binding scope); register-class-distinct from system-redesign register-class binding scope by construction at register-precision register-class binding scope.

Framing introduced at Q-S107 reviewer pass cycle register-event boundary; adopted at Charlie register convergence approval as binding discipline anchor at this sub-spec register binding scope per [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md) register binding scope (governance lineage at register-event-boundary register binding scope; reviewer-identity register-class-distinct from binding force at register-precision register binding scope).

Hidden failure mode at register binding scope: overreacting to second-order calibration findings (PHASE2C_12 single-batch §9.1/§9.2/§9.3 observations) and accidentally mutating framework layer at register binding scope. H-1 (e) prohibition + this cycle-scope framing binding cap at register-class match register binding scope.

### §1.4 Hard constraints (reaffirmed not re-derived)

H-1 / H-2 / H-3 binding at PHASE2C_14 cycle scope per scoping decision §1.4 verbatim binding register binding scope at canonical artifact register-class binding scope. **Reaffirmed at this sub-spec register binding scope; NOT re-derived at this register** per anti-momentum-binding strict reading register binding scope (re-derivation would itself constitute scope expansion at register-class match register binding scope per governance-gravity framing register binding scope).

**H-1 anti-governance-creep clause** (5-prohibition list (a)–(e); bilingual concept anchor at scoping decision §1.4): bound at sub-spec drafting cycle scope register binding scope. Specifically prohibited at this sub-spec layer: (a) Q-S79a 4-option adjudication / sealed corpus mutation / new admissibility § codification; (b) Strong-tier promotion formalization; (c) scaling-concern containment rule codification or §A2 mitigation framework; (d) any new METHODOLOGY_NOTES § append; (e) framework code refactor implementation.

**H-2 carry-forward freeze framing** (options not debt; per scoping decision §1.4 register binding scope): 4 PHASE2C_13 carry-forwards preserved at PHASE2C_13 close state at register binding scope; no PHASE2C_14 action register-class binding scope at any sub-spec drafting cycle activity register binding scope.

**H-3 forward-discipline at PHASE2C_14 close** (functional-criterion fire-time blocker bar per scoping decision §1.4 register binding scope): "literally cannot complete" anti-rationalization clause register binding scope; demonstration burden on cycle-internal evidence not rhetorical argument escalating discomfort to blocker at register binding scope. Standing instruction at this sub-spec drafting cycle register binding scope: if a candidate fire-time blocker arises during sub-spec drafting, surface to Charlie register at register-event boundary with cycle-internal evidence basis at register-precision register-class binding scope per H-3 functional bar register binding scope; do NOT autonomously expand scope under H-1 (a)–(e) prohibition register binding scope.

Standard discipline anchors (#1–#8 at scoping decision §1.4): all carry forward at register-class match register binding scope. Bilingual H-1 concept anchor at [scoping decision §1.4](PHASE2C_14_SCOPING_DECISION.md) preserved invariant at canonical artifact register-class binding scope; not re-cited verbatim at this sub-spec register binding scope per anti-redundancy register binding scope.

---

## §2 Strategy refinement components

This § specifies strategy refinement at **SEMANTICS register** (what the refinement means; what counts as compliant; what evidence basis grounds it). Specific operational changes (DSL hint surface choices, prompt-template edits, factor-pool restrictions, walk-forward filter implementation, theme-rotation parameter tuning) are register-class-distinct from SEMANTICS register and **deferred to PHASE2C_15 entry scoping cycle** per anti-pre-naming option (ii) preservation per scoping decision §6.5 binding register binding scope.

§2 component scope register binding scope per scoping decision §6.1 #2/#3/#4 register binding scope:
- §2.1 — `multi_factor_combination` structured combination DERIVED from 8 AND-gate survivor compositions (active refinement at SEMANTICS register)
- §2.2 — Walk-forward Sharpe first-pass filter SEMANTICS (active refinement at SEMANTICS register; compute-cost optimization register-class-distinct + deferred)
- §2.3 — `volatility_regime` defer with multi-batch evidence requirement specification (passive refinement at SEMANTICS register; cross-references §3.3)

### §2.1 `multi_factor_combination` structured combination DERIVED

**Empirical basis** (cited verbatim from sealed register binding scope; full numeric anchors at §1.2 above): mfc per-theme rate 9.1% (3/33) at descriptive register; NOT statistically distinguishable from non-mfc baseline at PHASE2C_12 cycle sample size (z=1.6044/p=0.1086; OR=3.18/p=0.1323); 8 cross-regime AND-gate survivors decompose 3 mfc + 5 non-mfc; mfc bimodal distribution (top performers + degenerate tail) per PHASE2C_12 closeout §9.1 verbatim sealed register binding scope.

**SEMANTICS specification at register-precision register binding scope:**

1. **Theme preserved.** mfc remains in canonical theme rotation register binding scope at register-class match register binding scope to PHASE2C_12 §9.1 directional anchor "Preserve mfc theme" register binding scope. PHASE2C_15 entry scoping cycle adjudicates specific theme rotation parameters at register-class binding scope (anti-pre-naming option (ii) preservation register binding scope).

2. **Structured combination defined at SEMANTICS register.** A multi-factor strategy is **structured** at register-precision register binding scope IFF the factor composition exhibits **explicit cross-factor structural relationships** at the DSL register binding scope — NOT merely N independent factors with no cross-factor relationships. **Specific structural relationship enumeration is the OUTPUT of DERIVATION at PHASE2C_15 entry scoping cycle register-event boundary**, NOT a pre-named taxonomy at this sub-spec register binding scope (per "DERIVE not impose" anti-anchoring discipline at register-class match register binding scope per scoping decision §6.1 #2 binding register binding scope). Survivor inspection at PHASE2C_12 8 AND-gate composition register binding scope determines what specific structural relationships distinguish survivors from non-survivors at register binding scope; this sub-spec specifies only the structured/unstructured contrast at SEMANTICS register binding scope. **Unstructured** combination at register binding scope = N independent factors with no cross-factor relationships at register binding scope (matches mfc degenerate-tail register-class binding scope per §9.1 bimodal distribution observation).

3. **DERIVATION procedure at SEMANTICS register.** Per scoping decision §6.1 #2 "DERIVE not impose" binding register binding scope, structured combination shape MUST be DERIVED from PHASE2C_12 8 AND-gate survivor factor compositions register binding scope at register-precision register binding scope (NOT imposed via advisor speculation at register binding scope per PHASE2C_12 §9.1 verbatim binding). DERIVATION procedure at SEMANTICS register binding scope:
   - **(D1) Inspect** factor compositions of 8 cross-regime AND-gate survivors at PHASE2C_12 batch artifact register binding scope (3 mfc + 5 non-mfc per §1.2 binding register binding scope; canonical artifact path register binding scope at PHASE2C_15 entry scoping cycle adjudication register-event boundary).
   - **(D2) Identify** recurring structural patterns at multi-factor composition register binding scope at register-class match register binding scope to §2.1 #2 structured/unstructured contrast register binding scope; **specific pattern enumeration IS the OUTPUT of D2 inspection at PHASE2C_15 entry scoping cycle register binding scope, NOT a pre-named taxonomy at this sub-spec layer** per "DERIVE not impose" anti-anchoring discipline at register-class match register binding scope.
   - **(D3) Encode** identified patterns as binding constraints at framework surface(s) to be selected at PHASE2C_15 entry scoping cycle adjudication register-event boundary at register-class match register binding scope (specific encoding mechanism + framework surface choice register-class-distinct from SEMANTICS register binding scope at this sub-spec layer per "DERIVE not impose" anti-anchoring discipline at register-class match register binding scope).
   - **(D4) Validate** at PHASE2C_15 fire register binding scope (canonical empirical-grounded validation register binding scope at PHASE2C_15 fire register-event boundary register binding scope; pre-registration framework at §3 binds success criteria register binding scope).

4. **Anti-narrative-collapse discipline at register binding scope** per per-fix adjudication register binding scope (load-bearing precaution at register-precision register binding scope; raised at Q-S107b reviewer pass cycle register-event boundary register binding scope; adopted at Charlie register convergence approval as binding sub-spec register-class binding scope at register-class match register binding scope): **mfc 3-of-8 survivor composition is NOT evidence of "mfc globally superior"** at register binding scope. The 5/8 non-mfc survivors register binding scope are register-class-coequal at cross-regime AND-gate survival register binding scope; structured-combination DERIVATION register binding scope applies to BOTH mfc and non-mfc survivor compositions at register-class match register binding scope (NOT exclusively to mfc register binding scope). DERIVATION scope register binding scope: cross-survivor structural patterns at register-class match register binding scope (3 mfc + 5 non-mfc = 8 total survivors at DERIVATION evidence basis register binding scope). PHASE2C_15 entry scoping cycle MUST preserve mixed-survivor structure at register-precision register binding scope per anti-narrative-collapse discipline at register binding scope.

5. **SEMANTICS scope boundary at register binding scope.** This sub-spec specifies (1) theme preservation; (2) structured combination definition at SEMANTICS register; (3) DERIVATION procedure at SEMANTICS register; (4) anti-narrative-collapse discipline. This sub-spec does NOT specify register binding scope: specific factor pool restrictions; specific DSL hint encoding mechanism; specific Critic gate criterion mutations; specific generation prompt-template changes; specific theme weight parameters. All register-class-distinct from SEMANTICS register binding scope; all deferred to PHASE2C_15 entry scoping cycle adjudication register-event boundary per anti-pre-naming option (ii) preservation register binding scope at register-class match register binding scope.

### §2.2 Walk-forward Sharpe first-pass filter SEMANTICS

**Empirical basis** (cited verbatim from sealed register binding scope; full numeric anchors at §1.2 above): 5/8 (62.5%) cross-regime AND-gate survivors at audit-only partition register binding scope (WF Sharpe < 0.5); single AND-gate survivor with strong WF Sharpe ≥ 0.5 = `88192bc5c256b702` (volume_divergence, wf_sharpe = 0.835) per PHASE2C_12 closeout §9.3 register binding scope; PHASE2C_11 §4.4 audit-only inclusion register decision retroactively validated at register-precision register binding scope by 5/8 AND-gate survivor composition register binding scope.

**SEMANTICS specification at register-precision register binding scope:**

1. **First-pass filter SEMANTICS register-class definition.** "First-pass filter" at register binding scope = the initial selection mechanism applied to PHASE2C_15 generated candidate population register binding scope BEFORE downstream resource-intensive evaluation (cross-regime walk-forward; AND-gate aggregation) register binding scope. SEMANTICS register binding scope = "what the filter measures" + "what it SHOULD measure to align with cross-regime robustness target register binding scope"; register-class-distinct from compute-cost optimization register binding scope at register binding scope (e.g., 2-tier filter design with cheap Tier 1 + expensive Tier 2 = compute-cost optimization register-class binding scope, NOT SEMANTICS register binding scope per scoping decision §6.1 #4 binding register binding scope).

2. **Empirical SEMANTICS finding at register-precision register binding scope.** WF Sharpe single-train-test boundary metric register binding scope is a **specialization** metric register binding scope (measures performance on a specific train-test boundary slice); cross-regime AND-gate survival register binding scope is a register-class-distinct **robustness** metric register binding scope (measures performance across multiple regime-slices) per PHASE2C_12 closeout §9.3 verbatim sealed register binding scope. Empirical finding at register-precision register binding scope: WF Sharpe single-boundary metric register binding scope **systematically under-selects** cross-regime robust strategies at PHASE2C_12 evidence basis register binding scope (5/8 AND-gate survivors at WF Sharpe < 0.5 = audit-only partition register binding scope per §1.2 anchor register binding scope).

3. **SEMANTICS direction at register-precision register binding scope.** First-pass filter SEMANTICS register binding scope SHOULD weight **cross-regime robustness** over **single-boundary specialization** at register binding scope. Two SEMANTICS MUST requirements at register-class match register binding scope (operationalization at SEMANTICS register binding scope; specific filter design register-class-distinct + deferred per §2.2 #4 below):
   - **(F1)** First-pass filter MUST surface candidates at cross-regime robustness signal register binding scope (aggregate signal across train-test boundary partitions; NOT filter exclusively at single-boundary WF Sharpe ≥ threshold register binding scope per §9.3 systematic-under-selection finding register binding scope).
   - **(F2)** First-pass filter inclusion register binding scope MUST preserve audit-only partition candidates at register binding scope (PHASE2C_11 §4.4 audit-only inclusion register decision retroactively validated at register-precision register binding scope by 5/8 AND-gate survivor composition register binding scope; this is the load-bearing finding at SEMANTICS register binding scope).

4. **SEMANTICS scope boundary at register binding scope.** This sub-spec specifies (1) first-pass filter SEMANTICS register-class definition; (2) empirical SEMANTICS finding (WF Sharpe single-boundary systematic under-selection); (3) SEMANTICS direction (cross-regime robustness over single-boundary specialization at F1+F2 above). This sub-spec does NOT specify register binding scope: specific filter implementation; specific filter design surface choice; specific compute-cost optimization mechanism; specific replacement metric for WF Sharpe at first-pass register binding scope. All register-class-distinct from SEMANTICS register binding scope; all deferred to PHASE2C_15 entry scoping cycle adjudication register-event boundary per anti-pre-naming option (ii) preservation register binding scope at register-class match register binding scope per "DERIVE not impose" anti-anchoring discipline at surface-choice register binding scope (parallel to §2.1 #2 + #3 D3 anti-anchoring register-class match register binding scope).

### §2.3 `volatility_regime` defer with multi-batch evidence requirement

**Empirical basis** (cited verbatim from sealed register binding scope; full numeric anchors at §1.2 above): volatility_regime AND-gate rate 0/32 = 0.0% at PHASE2C_12 cycle register binding scope (single-batch zero-trade observation at register binding scope); volatility_regime zero-trade rate ~59.4% at Step 6.5 walk-forward register binding scope (much higher than other themes 0-33% range register binding scope) per PHASE2C_12 closeout §9.2 verbatim sealed register binding scope.

**SEMANTICS specification at register-precision register binding scope:**

1. **Theme preserved at canonical rotation register binding scope.** volatility_regime remains in canonical theme rotation register binding scope at register-class match register binding scope to PHASE2C_12 §9.2 directional anchor "Defer volatility_regime fix scope" register binding scope. NO prompt-engineering fix at PHASE2C_14 sub-spec register binding scope per scoping decision §6.1 #3 binding register binding scope at register-class match register binding scope.

2. **Distinguishability question at register-precision register binding scope.** Single-batch zero-trade observation register binding scope is consistent at descriptive register binding scope with TWO register-class-distinct underlying mechanisms:
   - **(M1) Systematic prompt issue at register binding scope** — volatility_regime prompt template register binding scope produces consistently degenerate factor compositions at PHASE2C_12 cycle (0/32 single-batch register binding scope is then a deterministic outcome of prompt-template register binding scope, not stochastic).
   - **(M2) Single-batch LLM stochasticity at register binding scope** — volatility_regime prompt template register binding scope produces variable-quality factor compositions across batches; PHASE2C_12 cycle observation 0/32 is a single-batch stochastic outcome at register binding scope (could be 0/32 in another batch + 5/32 in another batch at register-precision register binding scope; multi-batch evidence required to distinguish at register-precision register binding scope).

3. **SEMANTICS specification at register-precision register binding scope.** Multi-batch evidence at register binding scope is the only mechanism at register-precision register binding scope to distinguish (M1) from (M2). Specific multi-batch evidence requirement (batch count + comparison axis + statistical evidence framework) at §3.3 below register binding scope. **NO prompt-engineering fix authorized at PHASE2C_14 sub-spec register binding scope** per scoping decision §6.1 #3 binding register binding scope; if multi-batch evidence at PHASE2C_15+ register binding scope confirms (M1) systematic prompt issue at register-precision, prompt-engineering fix register-class-eligible at successor entry scoping cycle adjudication register-event boundary per anti-pre-naming option (ii) preservation register binding scope.

4. **SEMANTICS scope boundary at register binding scope.** This sub-spec specifies (1) theme preservation; (2) (M1)/(M2) distinguishability question codification at register-precision; (3) multi-batch evidence requirement as the only register-class-eligible distinguishing mechanism; (4) explicit prohibition on prompt-engineering fix at PHASE2C_14 sub-spec layer. This sub-spec does NOT specify register binding scope: specific multi-batch threshold (deferred to §3.3 + PHASE2C_15 register binding scope); specific prompt-template changes; specific factor-pool restrictions for volatility_regime. All register-class-distinct + deferred at register-class match register binding scope.

---

## §3 Pre-registration framework (anti-p-hacking guardrail)

This § specifies the **pre-registration framework** at register-class definition register binding scope (§3.1), the **Wilson CI canonical anchor + strict-exceedance semantics** at register-precision register binding scope (§3.2), the **multi-batch evidence requirement** at SEMANTICS register binding scope (§3.3), and the **post-fire failure-mode register** at anti-rationalization register binding scope (§3.4). §3 architecture register-class-distinct from §2 strategy refinement register binding scope: §2 specifies WHAT gets refined; §3 specifies HOW success register-class-eligibility is evaluated + what cannot be mutated post-fire register binding scope.

### §3.1 Pre-registration register-class definition + activation timing + no-peek constraint

**Pre-registration register-class definition at register-precision register binding scope.** "Pre-registration" at this sub-spec layer = framework specification + canonical anchor binding **before PHASE2C_15 fires**, such that success-criteria + evaluation framework cannot be mutated post-fire to fit observed results register binding scope. Anti-p-hacking guardrail at strategy refinement register binding scope per scoping decision §6.2 binding register binding scope.

**Activation timeline at register binding scope** (Concern C codification):
- **t1** = this sub-spec drafting cycle: 2.07% canonical anchor + framework class SET at WORKING DRAFT register binding scope.
- **t2** = sub-spec SEAL commit register-event boundary: framework + canonical anchor LOCKED at canonical artifact register-class binding scope. **Activation boundary**.
- **t3** = PHASE2C_15 entry scoping cycle: operational details specified (sample sizes; batch counts; theme rotation params; etc.). PHASE2C_15 entry scoping cycle CANNOT mutate framework or canonical anchor register binding scope at register-class match register binding scope.
- **t4** = PHASE2C_15 fire register-event boundary: framework APPLIED to observed rate at register binding scope.
- **t5** = post-PHASE2C_15 fire register-event boundary: framework + canonical anchor immutable per scoping decision §6.2.1 anti-p-hacking guardrail register binding scope.

**Immutability continuity at register-precision register binding scope** (Flag 2 codification): immutability binds **continuously from t2 through post-t5** at register-class match register binding scope. Scoping decision §6.2.1 "immutable post-PHASE2C_15 fire" language reinforces t5 as the most p-hacking-prone register-event boundary, NOT as the activation boundary at register binding scope.

**No-peek constraint at register-precision register binding scope** (Concern B codification): sample sizes (per-batch + total batch count) MUST be pre-specified BEFORE the corresponding batch fires at register binding scope. Sample sizes CANNOT be data-dependent post-fire at register-class match register binding scope per anti-optional-stopping discipline at register binding scope.

### §3.2 Wilson CI canonical anchor + strict-exceedance semantics

**Canonical anchor at register-precision register binding scope:** Wilson CI lower bound at PHASE2C_12 baseline 8/197 = 4.06% is **[2.07%, 7.81%]**; **2.07% strict-exceedance** at PHASE2C_15 fire success register-class-eligibility binding per scoping decision §6.2.1 register binding scope. **"Strict-exceedance" at register-precision = `observed_rate > 2.07%`** (strictly greater than; equality at 2.07% does NOT pass). Sealed at sub-spec SEAL commit per t2 activation boundary above.

**Discrete-granularity at register binding scope** (Flag γ codification): observed PHASE2C_15 rate is computed at sample-size-determined precision (k/N for integer k batches passing AND-gate at total N batches register binding scope); strict-exceedance criterion `> 2.07%` applies to the computed rate at register-precision register binding scope. Whether exactly 2.07% is attainable depends on N at PHASE2C_15 entry scoping cycle adjudication (e.g., at N=200, granularity is 0.5% and 2.07% is between 4/200=2.0% and 5/200=2.5%, NOT exactly attainable at register binding scope; at other N values granularity differs). Strict convention applies regardless of attainability at register-class match register binding scope.

**Non-regression vs improvement distinction at register-precision register binding scope** (Concern A codification — load-bearing). 2.07% strict-exceedance is a **non-regression criterion at register-precision register binding scope**, NOT improvement evidence at register-class binding scope. Substantively register-class-distinct registers:

- **Non-regression at register binding scope:** observed PHASE2C_15 rate is *not consistent with regression below baseline's worst-case 95% CI lower bound* at register binding scope. Catches "PHASE2C_15 strategy refinement did not make the AND-gate rate substantively worse than baseline's worst-case interpretation" register binding scope.
- **Improvement at register binding scope:** observed PHASE2C_15 rate is *statistically distinguishable from baseline as larger* at register binding scope. Requires register-class-distinct framework: (i) observed rate strictly exceeds baseline POINT ESTIMATE 4.06%, OR (ii) PHASE2C_15 95% Wilson CI lower bound strictly exceeds 4.06% (proper "statistically significant improvement") register binding scope.

**Worked example at register-precision register binding scope:** PHASE2C_15 observed rate of 2.5% strictly exceeds 2.07% (passes non-regression at register binding scope) but is below baseline point estimate 4.06% (does NOT pass improvement at register-class match register binding scope). Strategy refinement could substantively have made things worse at register binding scope; non-regression criterion does NOT distinguish at register-precision register binding scope.

**Improvement framework register-class binding scope:** NOT pre-registered at this sub-spec register binding scope; deferred to register-class-eligible successor cycle adjudication per anti-pre-naming option (ii) preservation register binding scope. **No PHASE2C_15 improvement claim is pre-registered by this sub-spec at register binding scope** (neither baseline-point-estimate strict-exceedance nor PHASE2C_15-CI-strictly-exceeds-baseline-point-estimate authorized as PHASE2C_15 success criterion register-class-eligible at this sub-spec layer register binding scope; both register-class-eligible at successor cycle adjudication register-event boundary per anti-pre-naming option (ii) preservation register binding scope; the worked example at register-precision above is illustrative-not-authorized at register-class match register binding scope).

**Bilingual concept anchor at register binding scope** (compact per Q-S107c-ii defer disposition):

> **English:** 2.07% strict-exceedance is a non-regression guardrail at register-precision register binding scope, not improvement evidence at register binding scope. PHASE2C_15 fire success register-class-eligibility binds against regression below baseline's worst-case interpretation; improvement claims register-class-distinct + deferred. The bound is sealed at sub-spec SEAL register-event boundary and immutable continuously through post-PHASE2C_15-fire register binding scope.

> **中文:** 2.07% 严格超过是「不退步」保护线，不是改进证据。PHASE2C_15 成功资格只针对：观察到的 AND-gate 率没有低于 baseline 95% CI 的下限 (worst-case)。要主张「改进」，需要单独的框架（observed rate 严格超过 baseline 点估计 4.06%；或 PHASE2C_15 自己的 95% Wilson CI 下限严格超过 4.06%），本 sub-spec 不预注册。2.07% 这个数在 sub-spec SEAL 时锁定，从 t2 一路连续不变到 PHASE2C_15 fire 之后；不能事后改。

### §3.3 Multi-batch evidence requirement specification at SEMANTICS register

**Two register-class-distinct inferential roles at register-precision register binding scope** (Concern E codification — load-bearing). Multi-batch evidence at PHASE2C_15+ register binding scope serves at least two register-class-distinct inferential questions; sub-spec pre-commits framework class for each at register binding scope:

- **Role 1 — Cross-cycle proportion comparison at register binding scope.** Question: did PHASE2C_15 strategy refinement substantively improve AND-gate rate vs PHASE2C_12 baseline at register binding scope? **Framework class:** proportion comparison at cross-cycle register binding scope (e.g., 2-prop z-test, Fisher exact, or pairwise Wilson CI overlap test class register binding scope). Specific test choice + sample sizes deferred to PHASE2C_15 entry scoping cycle adjudication register-event boundary register binding scope.
- **Role 2 — Within-PHASE2C_15 heterogeneity at register binding scope.** Question: is volatility_regime zero-trade systematic-prompt-issue (M1) or single-batch-LLM-stochasticity (M2) per §2.3 #2 distinguishability binding at register binding scope? **Framework class:** batch-level homogeneity testing class at within-PHASE2C_15 register binding scope under H_0 of constant rate across batches register binding scope (chi-squared / G-test / Fisher exact test class register binding scope; specific test choice + significance threshold + minimum batch count deferred to PHASE2C_15 entry scoping cycle adjudication register-event boundary register binding scope). Heuristic intuition at register binding scope: if all batches → 0/N volatility_regime → systematic (M1); if rate varies substantively across batches per homogeneity test rejection → stochastic (M2) at register-class match register binding scope.

**H-3 protection framing at register-precision register binding scope** (drafting caution introduced at Q-S107d reviewer pass cycle register-event boundary; adopted at Charlie register convergence approval — load-bearing). Multi-batch evidence requirement at register binding scope **does NOT mutate PHASE2C_15 fire scope to "must resolve volatility_regime"** at register-class match register binding scope. Substantive framing at register-class binding scope:

- PHASE2C_15 **MAY** generate evidence at register binding scope — toward Role 1 + Role 2 inferential questions register binding scope at register-class match register binding scope.
- PHASE2C_15 does **NOT need to settle final prompt-engineering fix** at register binding scope per §2.3 #1 prohibition register binding scope.
- Systematic-vs-stochastic distinction (Role 2) **MAY remain unresolved if evidence is insufficient** at register-precision register binding scope (e.g., single-batch evidence insufficient to distinguish at register binding scope per §2.3 #2 binding register binding scope).
- If unresolved post-PHASE2C_15: defer to register-class-eligible successor cycle adjudication per anti-pre-naming option (ii) preservation register binding scope. Successor scope NOT pre-committed at this register binding scope per H-3 forward-discipline binding register binding scope.

**Stopping rule constraint at register-precision register binding scope** (Concern D codification): multi-batch evidence framework at register-class binding scope MUST commit to ONE of two register-class-eligible options at PHASE2C_15 entry scoping cycle adjudication register-event boundary at register binding scope: (i) **fixed N pre-committed** at PHASE2C_15 entry register binding scope (all N batches must fire regardless of intermediate observations register binding scope); OR (ii) **sequential testing framework with proper alpha-spending function** at register binding scope. Specific choice deferred to PHASE2C_15 entry; framework constraint (one of these two register-class-eligible options) locked at sub-spec SEAL per t2 activation register binding scope.

**Bilingual concept anchor at register binding scope** (compact per Q-S107c-ii defer disposition):

> **English:** Multi-batch evidence at PHASE2C_15+ register binding scope serves two register-class-distinct inferential roles (cross-cycle comparison + within-cycle heterogeneity); framework class for each pre-committed at sub-spec SEAL register-event boundary register binding scope. Multi-batch admissibility does NOT mutate PHASE2C_15 fire scope to mandatory resolution; evidence MAY remain insufficient at register-precision register binding scope.

> **中文:** 多批次证据在 PHASE2C_15+ 服务两类不同问题：跨周期比较 (PHASE2C_15 vs PHASE2C_12 baseline) + 周期内异质性 (volatility_regime 是系统问题还是随机噪声)。两套框架类别都在 sub-spec SEAL 时锁定，但具体参数 (sample size、批次数、停止规则) 推迟到 PHASE2C_15 entry scoping 决定。多批次证据要求不等于「PHASE2C_15 必须解决 volatility_regime」；证据不足时可以继续不下结论，留给后续周期。

### §3.4 Post-fire failure-mode register (anti-rationalization)

§3.4 enumerates **post-fire** rationalization patterns at register binding scope register-class-distinct from §3.1-§3.3 pre-fire framework specifications register binding scope. Pre-fire framework binds integrity BEFORE PHASE2C_15 fires; §3.4 binds against escape patterns AFTER fires at register binding scope (Flag 1 codification — load-bearing per advisor framing "how future selves will try to escape the framework" register binding scope). Each failure-mode entry cross-references the pre-fire concern whose binding mechanism it would violate at register binding scope:

1. **Post-fire success-criterion expansion at register binding scope.** Adding success criteria after observing results (e.g., "let's also consider per-theme rate" if AND-gate rate fails 2.07% strict-exceedance at register binding scope). Violates §3.1 immutability continuity binding (t2 lock) + §3.2 canonical anchor immutability per scoping decision §6.2.1 register binding scope.
2. **Selective batch interpretation at register binding scope.** Cherry-picking favorable batches register binding scope. Two register-class-distinct sub-modes at register binding scope: **(i) pre-completion exclusion** (which batches to fire at register binding scope; e.g., excluding a batch from the firing schedule based on intermediate observations) — violates §3.3 Concern D stopping rule constraint + §3.1 Concern B no-peek constraint at register-class match register binding scope; **(ii) post-completion exclusion** (excluding completed batches retroactively after they fire at register binding scope; e.g., "those completed batches shouldn't count toward the fire" or "that batch had a bug" if results unfavorable) — violates §3.1 immutability continuity binding (t2-t5 lock at register binding scope) + §3.2 canonical anchor binding at full-firing-population register binding scope (Wilson CI [2.07%, 7.81%] anchored at the full firing population register binding scope; post-fire subset-selection invalidates the anchor at register-class match register binding scope).
3. **Post-fire fire-boundary re-scoping at register binding scope.** Re-defining what counts as the "PHASE2C_15 fire" after observing results to exclude unfavorable batches (e.g., "let's call those batches PHASE2C_16 instead" register binding scope). Violates §3.1 activation timeline binding at register binding scope (t4 fire register-event boundary fixed at PHASE2C_15 entry scoping cycle register binding scope; post-fire re-scoping mutates t4 retroactively at register-class match register binding scope).
4. **Post-fire comparison-axis reframing at register binding scope.** Switching from AND-gate rate (PHASE2C_12 baseline metric) to per-theme rate or other metric class after observing results (e.g., "actually, per-theme rate is more informative" if AND-gate rate fails register binding scope). Violates §3.2 canonical anchor binding at register binding scope (Wilson CI [2.07%, 7.81%] is anchored at AND-gate rate metric class register binding scope; switching metric class invalidates the anchor at register-class match register binding scope).

**§3.4 register-class binding scope:** violation-index register binding scope (NOT framework definition register-class binding scope per §3.1-§3.3 register-class binding scope). Pre-fire framework + §3.4 violation-index together bind the anti-p-hacking guardrail at full register binding scope at register-class match register binding scope.

---

## §4 PHASE2C_15 implementation arc structure preview

§4 register-class binding scope: **preview-only at structure-class register binding scope**, NOT content-class pre-commitment register binding scope. PHASE2C_15 implementation arc Step structure + closeout deliverable scope + tag wording deferred to PHASE2C_15 entry scoping cycle adjudication register-event boundary per anti-pre-naming option (ii) preservation per scoping decision §6.5 + §6.6 binding register binding scope.

### §4.1 PHASE2C_15 entry scoping cycle scope (deferred substantive adjudication)

PHASE2C_15 entry scoping cycle authors operational specification at register binding scope consistent with this sub-spec's framework + canonical anchor + multi-batch evidence requirement at register-class match register binding scope.

**NOT register-class-eligible at PHASE2C_15 entry scoping cycle** at register binding scope (immutable per §3.1 t2-t5 binding register binding scope): framework class mutation; 2.07% canonical anchor mutation; non-regression-vs-improvement distinction collapse per §3.2 binding; comparison-axis switch / metric class switch per §3.4 #4 binding register binding scope.

**Register-class-eligible at PHASE2C_15 entry scoping cycle** at register binding scope (operational specification register-class-distinct from framework register-class binding scope; **eligible only within the framework locks already sealed in §3 at register binding scope** per scoping decision §1.4 H-1 + §3.1 t2-t5 immutability continuity binding register binding scope): sample sizes (per-batch + total batch count) per §3.1 Concern B no-peek register binding scope; batch counts; theme rotation parameters; specific multi-batch evidence test choice (chi-squared / G-test / Fisher exact / 2-prop z / etc.) per §3.3 Role 1 + Role 2 framework class register binding scope; stopping rule choice (fixed N OR sequential testing with alpha-spending) per §3.3 Concern D register binding scope; specific filter design per §2.2 #4 deferred binding register binding scope; specific framework surface choice (DSL / Critic / orchestrator) for structured-combination encoding per §2.1 #3 D3 deferred binding register binding scope; prompt-engineering choices for volatility_regime per §2.3 #1 prohibition register binding scope (PROHIBITED at PHASE2C_14 sub-spec; register-class-eligible at PHASE2C_15+ ONLY IF multi-batch evidence per §3.3 Role 2 confirms (M1) systematic prompt issue at register-precision register binding scope).

### §4.2 PHASE2C_15 implementation arc Step structure (deferred per anti-pre-naming option (ii))

Specific Step structure at PHASE2C_15 implementation arc register binding scope NOT pre-committed at this sub-spec register binding scope per anti-pre-naming option (ii) preservation per scoping decision §6.5 binding register binding scope at register-class match register binding scope to PHASE2C_10/11/12/13 implementation arc Step structure register precedent register binding scope (Step structure determined at PHASE2C_15 entry scoping cycle adjudication register-event boundary per Charlie register convergence approval register binding scope).

### §4.3 PHASE2C_15 closeout deliverable scope + tag wording (deferred)

Specific closeout deliverable scope + tag wording NOT pre-committed at this sub-spec register binding scope per anti-pre-naming option (ii) preservation per scoping decision §6.6 binding register binding scope. Tag fires at deliverable seal commit register-event boundary per Path A.2 register-event boundary discipline per METHODOLOGY_NOTES §20 binding register binding scope.

---

## §5 Sub-spec drafting cycle guardrails

§5 register-class binding scope: **reaffirmation-not-re-derivation register binding scope** per §1.4 register precedent register binding scope. Each guardrail item cites scoping decision §5.x or other sealed canonical source as binding register binding scope; not re-elaborated at register-class match register binding scope per anti-redundancy + H-1 governance-gravity discipline register binding scope.

### §5.1 H-1 anti-governance-creep clause preservation

H-1 5-prohibition list (a)-(e) bound at PHASE2C_14 cycle scope per scoping decision §5.4 + §1.4 H-1 verbatim bilingual binding register binding scope. Operational throughout this sub-spec drafting cycle + reviewer pass cycle + implementation arc + closeout per §5.4 binding scope at register-class match register binding scope.

### §5.2 H-2 carry-forward freeze framing preservation

PHASE2C_13 4 carry-forwards (Q-S79a 4-option survey + Strong-tier promotion candidates + §10.5 scaling-concern observation + §10.7 NEW carry-forward register-class precedents) preserved at PHASE2C_13 close state register binding scope per scoping decision §5.5 + §1.4 H-2 binding register binding scope. "Options not debt" reframing operational; NO PHASE2C_14 action register-class binding scope at any sub-spec drafting cycle activity at register-class match register binding scope.

### §5.3 H-3 forward-discipline at PHASE2C_14 close

H-3 functional-criterion fire-time blocker bar binding at PHASE2C_14 close register-event boundary per scoping decision §5.6 + §1.4 H-3 binding register binding scope. "Literally cannot complete" anti-rationalization clause preserved at register-precision register binding scope. Operational guidance at this sub-spec drafting cycle register binding scope: if a candidate fire-time blocker surfaces during sub-spec authoring, surface to Charlie register at register-event boundary with cycle-internal evidence basis at register-precision register binding scope (§3.3 Role 2 H-3 protection framing is the canonical worked example at this sub-spec layer register binding scope per Q-S107d-adjudication codification register binding scope).

### §5.4 Sealed corpus invariance preservation

METHODOLOGY_NOTES §27/§28/§29 + PHASE2C_13 sub-spec §2.7/§4.3 + §20.6 §A2 instances #26-#31 preserved invariant at canonical-artifact register-class binding scope per scoping decision §5.8 + Q-S79a unified-defer disposition Charlie register confirmation register binding scope. NO PHASE2C_14 sub-spec mutation at canonical artifact register-class binding scope per H-1 (a) explicit prohibition register binding scope.

### §5.5 §17 sub-rule 4 recursive operating rule

§17 sub-rule 4 cycle count = 15 at PHASE2C_14 entry SEAL register-event boundary per scoping decision §5.7 register binding scope; advances to **16 at PHASE2C_14 sub-spec drafting cycle SEAL register-event boundary** (16th consecutive cycle register binding scope per cycle increment register binding scope). Full-file prose-access pass at sealed-commit register binding scope is mandatory at sub-spec SEAL pre-fire register binding scope per §17 sub-rule 4 binding register binding scope.

### §5.6 Codex routing decision

**Codex SKIP at PHASE2C_14 sub-spec drafting cycle reviewer pass cycle register binding scope** per Q-S107a-2 option (a) Charlie register adjudication register binding scope at register-class match register binding scope. Reasoning at register-precision register binding scope: sub-spec PLAN register-class binding scope = framework specification at SEMANTICS + pre-registration register binding scope; Wilson CI canonical anchor immutability sealed at scoping decision §6.2.1 register binding scope (no new precision burden at sub-spec layer register binding scope); Codex routing register-class-eligible at PHASE2C_15 implementation register binding scope where empirical batch results land at register-class match register binding scope per [`feedback_codex_review_scope.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md) register binding scope.

---

## §6 Verification chain and reviewer disposition

### §6.1 Verification anchor chain at sub-spec SEAL register-event boundary

Per scoping decision §7.1 register precedent + Flag φ ≤6 V#-anchor pre-commit register binding scope (7th anchor surface = pre-breach signal per §0.2 protocol register binding scope):

- **V#1 — HEAD anchor at sub-spec SEAL pre-fire register-event boundary** register binding scope (HEAD verified at SEAL pre-fire; matches pushed-to-origin/main state at register-precision register binding scope; specific hash filled at SEAL pre-fire fire time).
- **V#2 — PHASE2C_14 entry SEAL bundle invariance** at register binding scope: pre-this-sub-spec-drafting-cycle HEAD = `46e4956`; PHASE2C_14 entry scoping decision sealed at `33107d6` (527 lines / 58 §§ + sub-§§); NO mutations to scoping decision artifact during this sub-spec drafting cycle at register binding scope.
- **V#3 — METHODOLOGY_NOTES.md preservation** at canonical artifact register-class binding scope: 6785 lines preserved invariant per H-1 (d) prohibition register binding scope (verified at SEAL pre-fire register-event boundary).
- **V#4 — Sub-spec line count + cap compliance** at register binding scope: total line count ≤550 envelope per §0.2; §3 ≤120 cap held; §5 ≤40 cap held at register-class match register binding scope.
- **V#5 — Codification-point integrity** at register-precision register binding scope: 15 codification points present at register binding scope (12 §3 codification points per Q-S107e checkpoint verification: §3.1 Concern C t1-t5 timeline + Flag 2 immutability continuity + Concern B no-peek + §3.2 strict-exceedance definition + Concern A non-regression-vs-improvement + bilingual concept anchor + §3.3 Role 1 cross-cycle proportion + Role 2 within-PHASE2C_15 heterogeneity + H-3 protection + Concern D stopping rule + bilingual concept anchor + §3.4 4 NEW post-fire failure modes; PLUS 3 Q-S107e-adjudication patches: Flag γ discrete-granularity at §3.2 + Flag α §3.4 #2 sub-mode split + Flag β §3.3 Role 2 framework class tightening at register-class match register binding scope to Q-S107e-adjudication binding register binding scope). Boundary-scoped count discipline at register-precision per Q-S107g-correction-2 forward operating procedure register binding scope: count refreshes at SEAL pre-fire empirical verification fire register binding scope; subsequent patches at Q-S108 register-event boundary may extend count register-class-distinct from this V#5 verification fire register binding scope.
- **V#6 — Sweep-grep clean state** at register binding scope: 0 reviewer-identity residuals outside reviewer-disposition / verification object-language contexts at register binding scope; 0 anchoring-list residuals (4-category structural-relationship class / 3-surface DSL hint / Critic gate / 5-design filter enumeration class) at register binding scope per Flag C forward sweep-grep discipline register binding scope.

### §6.2 Reviewer disposition

**ChatGPT first-pass structural overlay register binding scope** + **Claude advisor full-prose-access pass register binding scope** + **Codex SKIP** per §5.6 + Q-S107a-2 option (a) Charlie register adjudication register binding scope. Per-fix adjudication discipline operated throughout sub-spec drafting cycle per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) register binding scope (no bulk-accept; reasoned per-fix adjudication at register-precision per per-fix verification register binding scope).

**Cumulative healthy reasoned-adjudication pattern at PHASE2C_14 sub-spec drafting cycle internal register binding scope:** 6 instances at carry-forward register through §6 drafting register-event boundary at register-class match register binding scope (Q-S107c-i divergence resolved upward to option (iv) + Flag A F-list register-class incoherence catch + Flag C sweep-grep adoption + line 126 D2 residual catch + Flag 1 §3.4 violation-index correction + Flag γ residual catch at line 215 §3.3 H-3 framing per Flag C forward sweep-grep discipline register binding scope). Cumulative-count register at register-precision is **boundary-scoped at register binding scope** (count up to specified register-event boundary; subsequent instances log at register-class-distinct boundaries per Q-S107g-correction-2 forward operating procedure adoption register binding scope). Logged passively per H-1 (b) preservation register binding scope per Q-S103 PUSHBACK precedent register binding scope (NOT tagged as Candidate 4 promotion evidence basis at PHASE2C_14 register binding scope per scoping decision binding).

### §6.3 Pre-fire empirical verification timing

V#1-V#6 anchor chain fires at sub-spec SEAL pre-fire register-event boundary register binding scope: **after Activity 4 per-fix adjudication completes** and **before Activity 6 SEAL commit fires** at register-class match register binding scope (advisor operational note per Q-S107f-adjudication binding register binding scope). Anchor chain register binding scope is the gate between final reviewer adjudication register binding scope and SEAL commit register binding scope at register-class match register binding scope; any mutation in the adjudication-close → SEAL-commit window register binding scope MUST re-fire the V#1-V#6 anchor chain at register-class match register binding scope per anti-mutation-window discipline register binding scope.

---

## §7 Cross-references

### §7.1 PHASE2C_14 scoping decision cross-reference

[`PHASE2C_14_SCOPING_DECISION.md`](PHASE2C_14_SCOPING_DECISION.md) sealed at `33107d6` (527 lines / 58 §§ + sub-§§) — canonical scoping decision register binding scope. Path (a) selection + §1.4 H-1/H-2/H-3 verbatim binding + §6.2.1 Wilson CI canonical anchor + §6.4 activity sequencing + §6.5 implementation arc structure preview deferred + §6.6 closeout deferred = canonical input artifacts at this sub-spec layer.

### §7.2 PHASE2C_12 closeout cross-reference

[`PHASE2C_12_RESULTS.md`](../closeout/PHASE2C_12_RESULTS.md) sealed at `1989c85` + tag `phase2c-12-breadth-expansion-v1` — canonical directional anchor at strategy refinement register binding scope. §10.1 split scope ratification + §9.1-§9.3 strategy direction preliminary observations (multi_factor + volatility_regime + WF Sharpe at register-class match register binding scope to §2.1/§2.2/§2.3) + §9.1 "DERIVE not impose" verbatim binding + §10.4 PHASE2C_14 strategy refinement sub-spec preliminary direction anchor.

### §7.3 PHASE2C_13 closeout cross-reference

[`PHASE2C_13_RESULTS.md`](../closeout/PHASE2C_13_RESULTS.md) sealed at `59d735b` + tag `phase2c-13-methodology-consolidation-v1` (532 lines) — canonical carry-forward register handoff at H-2 freeze framing register binding scope per scoping decision §6.3 binding register binding scope. §10 carry-forward register at PHASE2C_13 close state register binding scope (Q-S79a 4-option survey + Strong-tier promotion candidate evaluation + §10.5 scaling-concern observation + §10.7 NEW carry-forward register-class precedents).

### §7.4 PHASE2C_10/11 sub-spec register precedent

[`PHASE2C_10_PLAN.md`](PHASE2C_10_PLAN.md) sealed at `d2a53fa` (467 lines; methodology consolidation cycle sub-spec register precedent register binding scope); [`PHASE2C_11_PLAN.md`](PHASE2C_11_PLAN.md) sealed at `8bc12de` (724 lines; statistical-significance machinery sub-spec register precedent register binding scope including pre-registration paragraph framework register precedent at register-class match register binding scope to §3 above).

### §7.5 METHODOLOGY_NOTES cross-references

[`METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md): §22 parameter pre-lock at register-class match register binding scope to §3.2 Wilson CI canonical anchor binding; §28 diagnostic-surface-not-mitigation-mandate at register-class match register binding scope to §3.3 Role 2 H-3 protection register binding scope; §17 sub-rule 4 recursive operating rule at §5.5 binding register binding scope; §20 Path A.2 register-event boundary discipline at §4.3 closeout deliverable tag fire register binding scope.

### §7.6 CLAUDE.md cross-reference

[`CLAUDE.md`](../../CLAUDE.md) Phase Marker register: PHASE2C_14 entry scoping cycle SEALED entry at session entry register binding scope; advances to **PHASE2C_14 sub-spec drafting cycle SEALED entry** at this sub-spec SEAL register-event boundary per [`feedback_claude_md_freshness.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md) register binding scope.

### §7.7 Feedback memory cross-references

Per [`MEMORY.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/MEMORY.md) index: [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md) (Charlie register authorization throughout Q-S107a-Q-S107f register binding scope); [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) (per-fix adjudication discipline operated throughout); [`feedback_codex_review_scope.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md) (Codex SKIP at sub-spec drafting cycle register-class per §5.6); [`feedback_claude_md_freshness.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md) (Phase Marker advance discipline at SEAL register-event boundary); [`feedback_bilingual_concept_explanation.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_bilingual_concept_explanation.md) (bilingual concept anchor at §3.2 + §3.3 per §0.3 #6 binding); [`feedback_use_planning_skills_for_complex_tasks.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_use_planning_skills_for_complex_tasks.md) (TodoWrite operational throughout sub-spec drafting cycle).

---

**End of working draft.** Standing by for §17 sub-rule 4 final full-file prose-access pass at sealed-commit register + reviewer pass cycle (Activity 3) entry register-event boundary per scoping decision §6.4 canonical seven-step activity sequencing register binding scope.
