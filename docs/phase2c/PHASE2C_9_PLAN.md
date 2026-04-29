# PHASE2C_9 — Mining-process retrospective (light-touch)

**Implementation specification for PHASE2C_9 Q-9.B — light-touch
mining-process retrospective on the Phase 2B Proposer/Critic generation
cycle that produced the 198-candidate batch
`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` consumed by PHASE2C_6 /
PHASE2C_7.1 / PHASE2C_8.1 evaluation arcs. Scope-bounded retrospective
review at documentation register; pre-registered exit conditions for
post-Q-9.B scoping cycle adjudication.**

- **Spec drafting date**: 2026-04-29
- **Predecessor scoping decision**:
  [`PHASE2C_9_SCOPING_DECISION.md`](PHASE2C_9_SCOPING_DECISION.md)
  (committed at `3e0c99d`)
- **Carry-forward sources**:
  [`docs/closeout/PHASE2C_8_1_RESULTS.md`](../closeout/PHASE2C_8_1_RESULTS.md)
  (commit `69e9af9`; primary empirical anchor) +
  [`docs/closeout/PHASE2C_7_1_RESULTS.md`](../closeout/PHASE2C_7_1_RESULTS.md)
  (PHASE2C_7.1 multi-regime carry-forward)
- **Methodology discipline**:
  [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  (commit `8154e99`; §1–§15 in force; §10 anti-pre-naming + §14
  bidirectional dual-reviewer + §15 anchor-list discipline are
  load-bearing for this arc)

---


## 1. Scope and verdict

**This document specifies the implementation arc for PHASE2C_9 Q-9.B
— light-touch mining-process retrospective. PHASE2C_9.0 (the scoping
decision) compared four candidate next-arc paths (Q-9.A statistical
validation; Q-9.B mining retrospective; Q-9.C gate-calibration
variation; Q-9.D Phase 3 scoping); PHASE2C_9 ratification at the
post-scoping adjudication cycle landed on Q-9.B at light-touch depth.
PHASE2C_9 implements that ratification.**

**Project state at PHASE2C_9 spec drafting (2026-04-29).**

- Canonical main: `origin/main` at commit `3e0c99d`
- Tags on main: `wf-corrected-v1` (corrected WF engine fix at
  `eb1c87f`); `phase2c-7-1-multi-regime-v1`;
  `phase2c-8-1-multi-regime-extended-v1`
- PHASE2C_9.0 scoping decision: committed at `3e0c99d`
- PHASE2C_8.1 closeout (primary empirical anchor):
  [`docs/closeout/PHASE2C_8_1_RESULTS.md`](../closeout/PHASE2C_8_1_RESULTS.md)
  at commit `69e9af9`
- METHODOLOGY_NOTES corpus at commit `8154e99` (§1–§15 in force;
  PHASE2C_8.1 codifications applied)
- Q-9.B ratification source: PHASE2C_9.0 §6 ratified resolution +
  dual-reviewer convergence at adjudication cycle (ChatGPT three
  operational conditions + Claude advisor three carry-forward
  considerations, both at conversational register; this spec carries
  them into canonical implementation specification per
  spec-drafting-as-ratification precedent inherited from
  PHASE2C_8.0 → `1e85d1d`)

**What PHASE2C_9 produces.**

A bounded retrospective document at
[`docs/closeout/PHASE2C_9_RESULTS.md`](../closeout/PHASE2C_9_RESULTS.md)
that:

- Reviews the Phase 2B Proposer prompt design + Critic gate logic +
  theme rotation mechanism that produced the 198-candidate batch
- Maps observed candidate-population properties (cohort cardinalities;
  pass-count distribution; theme-level patterns; lone-survivor
  characterization) back to mining-process structural inputs
- Evaluates evidence against pre-registered exit conditions to produce
  one of three case determinations: Case A (mining plausibly fixable);
  Case B (candidate population structurally weak); Case C (ambiguous)
- Surfaces register-precision findings (with explicit evidence
  mapping) without pre-committing to second-step direction (post-Q-9.B
  scoping cycle is its own deliberation, not pre-named here)

Pre-pinned decisions (carried forward from PHASE2C_9.0 + adjudication
cycle):

| decision | resolution |
|---|---|
| **D1 cycle-boundary semantics** | PHASE2C_9 = Q-9.B alone. Post-Q-9.B adjudication on second-step direction (full Q-9.A / minimal eval / Q-9.C / Q-9.D / pivot) is a separate scoping cycle, not collapsed into PHASE2C_9 scope per anti-pre-naming framework operating at meta-arc level |
| **D2 retrospective depth** | Light-touch register only. Documentation review of prompts + criterion design; theme-rotation mechanism review; pass-count distribution audit; lone-survivor walkthrough. NOT structured re-examination of all 198 candidates; NOT mining-process redesign; NOT new candidate generation; NOT new statistical machinery |
| **D3 input universe** | Code + artifact files only. No new API calls (Anthropic / Claude); no new backtests; no new orchestrator runs. Reads `agents/proposer/*.py`, `agents/critic/*.py`, `agents/themes.py`, `raw_payloads/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/`, and PHASE2C_8.1's per-candidate evaluation artifacts |
| **D4 exit conditions** | Pre-registered before fire (§4). Three case determinations (A/B/C) with operational evidence criteria for each. Case determination is the closeout's primary deliverable |
| **D5 verification framework** | Evidence-mapping discipline at every claim; falsifiability-statement discipline at every case-determination assertion; no narrative without artifact reference (file:line or canonical number citation) |
| **D6 cycle-boundary preservation** | Spec language must not pre-commit to successor scoping cycle's second-step direction even at forward-pointer level. Phrases like "next we will run DSR" or "this confirms Phase 3 progression" are explicitly prohibited. Allowed forward-pointer register: "Case A determination would make Q-9.A defensible as one candidate path among others at post-Q-9.B scoping cycle" |

**What PHASE2C_9 is NOT.**

- **Not a re-litigation of PHASE2C_9.0.** Path selection is sealed
  at Q-9.B (light-touch). PHASE2C_9 implements Q-9.B; it does not
  revisit Q-9.A / Q-9.C / Q-9.D direction options. Those alternative
  paths surface conditionally at post-Q-9.B scoping cycle (which is
  not pre-named here).
- **Not a methodology amendment.**
  [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  §1-§15 (commit `8154e99`) apply throughout PHASE2C_9; new
  methodology principles surfaced during PHASE2C_9 work are captured
  as a follow-up update (same hybrid handling as PHASE2C_8.1 →
  `8154e99` precedent).
- **Not a candidate generation cycle.** No new Proposer or Critic
  invocations; no new API spend; no new batch fires. PHASE2C_9
  operates on existing artifacts only.
- **Not a candidate evaluation cycle.** No new backtests, no new
  evaluation-gate runs, no new statistical-significance machinery.
  PHASE2C_9 reads existing evaluation outputs (PHASE2C_6 + PHASE2C_7.1
  + PHASE2C_8.1) as inputs, does not extend them.
- **Not a 2025 test split touch.** 2025 remains preserved
  touched-once across PHASE2C_9 work (CLAUDE.md hard rule;
  out-of-scope universal in §9).
- **Not a config or code modification cycle.** No edits to
  `config/environments.yaml`, `config/execution.yaml`,
  `agents/proposer/*.py`, `agents/critic/*.py`, or
  `backtest/engine.py`. PHASE2C_9 is a pure retrospective document;
  any code changes informed by retrospective findings are deferred
  to subsequent arcs.
- **Not a forward-decision on successor scoping cycle's second-step direction.**
  PHASE2C_9 closeout reports findings + case determination +
  evidence map; it does not pre-commit any specific second-step
  direction. The post-Q-9.B scoping cycle's deliberation register
  resolves that separately.

**Document structure.**

§2 names the input universe (code references; artifact files;
canonical-number anchors from PHASE2C_8.1). §3 specifies the hard
scope boundaries with explicit ✔/❌ list and operational
disambiguation per Claude advisor's Consideration 2 carry-forward.
§4 pre-registers the three exit conditions (Case A / B / C) with
operational evidence criteria per Claude advisor's Consideration 1
carry-forward. §5 specifies the implementation steps (sequential
gating; six steps with per-step deliverables). §6 specifies the
verification framework (evidence-mapping; falsifiability;
canonical-number cross-checks). §7 specifies cycle-boundary
preservation language per Claude advisor's Consideration 3
carry-forward. §8 names the closeout document structure. §9 names
risks and out-of-scope items.

---


## 2. Input universe

PHASE2C_9 retrospective operates on existing artifacts only. No new
API calls, no new backtests, no new generation. The input universe is
fully enumerated below; any artifact not in this enumeration is
out-of-scope for retrospective review.

### 2.1 Code artifacts (Phase 2B mining-process source)

Proposer:

- [`agents/proposer/interface.py`](../../agents/proposer/interface.py)
  — `ProposerBackend` Protocol + I/O schemas
- [`agents/proposer/sonnet_backend.py`](../../agents/proposer/sonnet_backend.py)
  — Live Sonnet backend (production cycle for batch
  `b6fcbf86-...`)
- [`agents/proposer/prompt_builder.py`](../../agents/proposer/prompt_builder.py)
  — Prompt construction + leakage audit helpers
- [`agents/proposer/stage2c_batch.py`](../../agents/proposer/stage2c_batch.py)
  — Stage 2c batch orchestration (the cycle that produced
  `b6fcbf86-...`)
- [`agents/proposer/stage2d_batch.py`](../../agents/proposer/stage2d_batch.py)
  — Stage 2d batch orchestration (referenced for mechanism
  comparability if relevant)

Critic:

- [`agents/critic/orchestrator.py`](../../agents/critic/orchestrator.py)
  — `run_critic()` orchestrator + reliability fuse
- [`agents/critic/d7a_rules.py`](../../agents/critic/d7a_rules.py)
  — Deterministic D7a rule scoring (4 axes)
- [`agents/critic/d7a_feature_extraction.py`](../../agents/critic/d7a_feature_extraction.py)
  — DSL feature extraction primitives
- [`agents/critic/d7b_prompt.py`](../../agents/critic/d7b_prompt.py)
  — D7b prompt template (frozen at Stage 2a contract boundary)
- [`agents/critic/d7b_live.py`](../../agents/critic/d7b_live.py)
  — Live Sonnet D7b backend
- [`agents/critic/d7b_parser.py`](../../agents/critic/d7b_parser.py)
  — D7b response parser + forbidden-language scan

Theme rotation:

- [`agents/themes.py`](../../agents/themes.py) — Canonical theme
  list (CONTRACT BOUNDARY)

DSL + compiler (read-only reference for retrospective grounding):

- [`strategies/dsl.py`](../../strategies/dsl.py) — DSL pydantic
  schema (complexity budgets)
- [`strategies/dsl_compiler.py`](../../strategies/dsl_compiler.py)
  — DSL → Backtrader compiler
- [`agents/hypothesis_hash.py`](../../agents/hypothesis_hash.py)
  — Canonical DSL hash + dedup

### 2.2 Batch artifact files (PHASE2C_5 generation cycle)

Canonical batch: `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`

- `raw_payloads/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/` —
  per-attempt prompt + response artifacts (404 attempt files;
  attempt_NNNN_prompt.txt + attempt_NNNN_response.txt)
- `agents/spend_ledger.db` — orchestrator-owned ledger; relevant
  query surface for batch-level spend / attempt counts /
  lifecycle-state distribution
- `data/compiled_strategies/<hypothesis_hash>.json` — per-candidate
  DSL compilation manifests (198 files)

### 2.3 Evaluation artifact files (PHASE2C_6 / PHASE2C_7.1 / PHASE2C_8.1)

Per-candidate evaluation outputs feed into population-property
mapping (§5 Step 3 + Step 4):

- `data/phase2c_evaluation_gate/primary_v1/` — PHASE2C_6 primary
  partition (159 candidates)
- `data/phase2c_evaluation_gate/audit_v1/` — PHASE2C_6 audit
  partition (39 candidates)
- `data/phase2c_evaluation_gate/audit_2024_v1_filtered/` —
  PHASE2C_7.1 validation_2024 evaluation (filtered cohort)
- `data/phase2c_evaluation_gate/eval_2020_v1_filtered/` —
  PHASE2C_8.1 eval_2020_v1 evaluation (filtered cohort)
- `data/phase2c_evaluation_gate/eval_2021_v1_filtered/` —
  PHASE2C_8.1 eval_2021_v1 evaluation (filtered cohort)
- `data/phase2c_evaluation_gate/comparison_2022_2024_2020_2021_v1/`
  — PHASE2C_8.1 candidate-aligned multi-regime comparison matrix

### 2.4 Canonical-number anchors (PHASE2C_8.1 closeout-derived)

Empirical anchors that retrospective claims must cross-check against:

| anchor | value | source |
|---|---|---|
| Total candidates | 198 | PHASE2C_8.1 closeout §3.0 |
| Theme distribution | ~40/40/40/39/39 across 5 operational themes | PHASE2C_8.1 closeout §7.1 |
| `cohort_a_unfiltered` cardinality | 1 | PHASE2C_8.1 closeout §3.1 |
| `cohort_a_filtered` cardinality | 0 | PHASE2C_8.1 closeout §3.1 |
| `cohort_c` cardinality | 76 | PHASE2C_8.1 closeout §3.1 |
| Lone-survivor hypothesis hash | `0845d1d7898412f2` | PHASE2C_8.1 closeout §3.1 + §6.0 |
| Lone-survivor theme | `volume_divergence` | PHASE2C_8.1 closeout §7.0 + §6.0 |
| Lone-survivor name | `volume_surge_momentum_entry` | PHASE2C_8.1 closeout §6.0 |
| Lone-survivor partition origin | audit (PHASE2C_6 audit_v1) | PHASE2C_8.1 closeout §6.3 |
| In-sample-caveat asymmetry | 21 vs 8 (train-overlap pass / fully-OOS pass jointly) | PHASE2C_8.1 closeout §5.2 |

These anchors are immutable inputs to retrospective reasoning. Any
retrospective claim that contradicts a canonical anchor without
explicit reconciliation is a verification framework failure (§6).

### 2.5 Operational themes (PHASE2C_5 generation cycle)

Per [`agents/themes.py`](../../agents/themes.py) and CLAUDE.md
"Theme rotation operational boundary":

| theme key | in operational rotation? | candidate count (~) |
|---|---|---|
| `momentum` | yes | 40 |
| `mean_reversion` | yes | 40 |
| `volatility_regime` | yes | 40 |
| `volume_divergence` | yes | 39 |
| `calendar_effect` | yes | 39 |
| `multi_factor_combination` | NO (canonical but not operational) | 0 |

Note: per [`agents/themes.py`](../../agents/themes.py):17–21,
`multi_factor_combination` remains in the canonical THEMES tuple but
is excluded from the Stage 2c/2d operational rotation (`THEME_CYCLE_LEN
= 5`). PHASE2C_9 retrospective treats this as fixed empirical fact;
the operational-vs-canonical theme-list register is not retrospective
scope.

---


## 3. Hard scope boundaries

This section is the load-bearing scope-fix per Claude advisor's
Consideration 2 carry-forward. Each item is explicit (✔ in scope; ❌
out of scope) and operationally disambiguated to prevent register
drift during implementation.

### 3.1 In-scope (✔)

**3.1.1 Proposer prompt design review.** Read
[`agents/proposer/sonnet_backend.py`](../../agents/proposer/sonnet_backend.py),
[`agents/proposer/prompt_builder.py`](../../agents/proposer/prompt_builder.py),
and [`agents/proposer/stage2c_batch.py`](../../agents/proposer/stage2c_batch.py).
Identify:
- System prompt language + constraints
- Theme-injection mechanism (how the rotated theme reaches the prompt)
- Few-shot example pattern (presence; selection logic if any)
- DSL schema constraints surfaced to the LLM
- Leakage-audit guarantees (what the prompt does NOT include)

Operational disambiguation: this is **documentation review**, not
prompt-engineering critique or redesign proposal. Output register
is "what the prompt is and is not designed to elicit," not "what
the prompt should be."

**3.1.2 Critic gate logic review.** Read
[`agents/critic/d7a_rules.py`](../../agents/critic/d7a_rules.py),
[`agents/critic/d7a_feature_extraction.py`](../../agents/critic/d7a_feature_extraction.py),
[`agents/critic/d7b_prompt.py`](../../agents/critic/d7b_prompt.py),
[`agents/critic/d7b_parser.py`](../../agents/critic/d7b_parser.py),
and [`agents/critic/orchestrator.py`](../../agents/critic/orchestrator.py).
Identify:
- D7a rule scoring formulas (4 axes)
- D7a → D7b decision logic (when does D7a alone reject vs route to D7b)
- D7b prompt structure + parser semantics
- Forbidden-language scan triggers
- Reliability fuse (currently unenforced per CLAUDE.md hard rule)

Operational disambiguation: this is **logic review**, not threshold
optimization or rule redesign. Output register is "what the gate
accepts/rejects and on what criteria," not "what the gate should
accept/reject."

**3.1.3 Theme rotation mechanism review.** Read
[`agents/themes.py`](../../agents/themes.py) +
[`agents/proposer/stage2c_batch.py`](../../agents/proposer/stage2c_batch.py)
theme-assignment logic. Cross-check against canonical-number anchor
(§2.4) of 40/40/40/39/39 theme distribution. Identify:
- Theme assignment formula (`THEMES[(k - 1) % len(THEMES)]`)
- Operational-vs-canonical boundary (5-theme rotation excludes
  `multi_factor_combination`)
- Distribution outcome at batch close (40/40/40/39/39)

Operational disambiguation: this is **mechanism documentation**, not
rotation-strategy redesign. Output register is "what the rotation
produces given current implementation," not "what rotation strategy
should be used."

**3.1.4 Candidate-passing criteria audit.** From
[`agents/spend_ledger.db`](../../agents/spend_ledger.db) (read-only
query) and `data/compiled_strategies/<hypothesis_hash>.json`,
characterize the lifecycle-state distribution at batch close:
- How many candidates reached `shortlisted` (vs other terminal
  states)
- Lifecycle-state breakdown (proposer_invalid_dsl / duplicate /
  critic_rejected / train_failed / holdout_failed / dsr_failed /
  shortlisted / budget_exhausted)
- Cross-reference with the 198 candidates that reached PHASE2C_6
  evaluation

Operational disambiguation: this is **distribution characterization**,
not lifecycle-state redesign. Output register is "where in the
mining pipeline candidates were excluded and at what cardinalities,"
not "the pipeline should reject more/fewer candidates."

**3.1.5 Theme × pass-count cross-tab interpretation.** Cross-check
the PHASE2C_8.1 closeout §7 theme-level cross-regime patterns
(per-theme AND-gate pass counts at unfiltered tier across 4 regimes)
against generation-side theme distribution. Identify:
- Whether theme-level pass-count asymmetries (e.g., 25/40 in
  validation_2024 for some theme; 6/40 in bear_2022 for some theme)
  correlate with prompt-side theme content
- Whether the lone-survivor's theme (`volume_divergence`) is a
  high-pass-count theme or a tail-of-distribution theme

Operational disambiguation: this is **factual cross-tab description
+ interpretation hypothesis surfacing**, not statistical-significance
testing. Output register is "what the cross-tab patterns are and
what mining-process inputs plausibly produced them," not "the
cross-tab patterns are statistically significant evidence of X."

**3.1.6 Lone-survivor walkthrough.** Trace
`0845d1d7898412f2` (`volume_surge_momentum_entry`,
theme=`volume_divergence`) from generation through evaluation:
- Locate the corresponding `attempt_NNNN_prompt.txt` +
  `attempt_NNNN_response.txt` in
  `raw_payloads/batch_b6fcbf86-.../`
- Locate the compiled-strategy manifest at
  `data/compiled_strategies/0845d1d7898412f2.json`
- Locate the per-regime evaluation outputs across PHASE2C_6 audit_v1
  + PHASE2C_7.1 + PHASE2C_8.1
- Audit-only partition origin per PHASE2C_8.1 closeout §6.3
- Trade-count vs filter threshold (19 trades in bear_2022 per §6.2;
  ≥20 threshold)

Operational disambiguation: this is **single-candidate trace** for
the empirically-distinguished cohort_a_unfiltered=1 case, not
generic walkthrough of N candidates. Output register is "what the
mining-process produced for this specific candidate and how it
relates to the audit-only / filter-exclusion / hybrid-quality
findings," not "this candidate is/isn't a credible signal."

### 3.2 Out-of-scope (❌)

**3.2.1 ❌ NO new candidate generation.** No Proposer API calls; no
Critic API calls; no batch fires; no new attempt artifacts.

**3.2.2 ❌ NO new candidate evaluation.** No new backtests; no new
evaluation-gate runs; no extension of multi-regime comparison
matrix to additional regimes.

**3.2.3 ❌ NO 198-candidate full re-analysis.** Each-of-198
walkthrough is structured re-examination depth (~4-5 sessions per
PHASE2C_9.0 §3.B), not light-touch (~2-3 sessions). PHASE2C_9
operates at population-distribution + lone-survivor + theme-cohort
register only; per-candidate analysis is bounded to lone-survivor
(`0845d1d7898412f2`) + at most one or two illustrative non-survivors
where they exemplify a population pattern.

**3.2.4 ❌ NO mining-process redesign.** No prompt rewrites; no
gate-threshold adjustments; no theme-rotation strategy revisions; no
lifecycle-state additions. PHASE2C_9 surfaces findings; redesign is
deferred to subsequent arcs (which are not pre-named here).

**3.2.5 ❌ NO statistical-significance machinery.** No DSR; no PBO;
no CPCV; no multiple-comparisons correction; no permutation tests.
Q-9.A territory is explicitly out-of-scope for PHASE2C_9.

**3.2.6 ❌ NO calibration-variation grid.** No AND-gate threshold
ablation; no per-regime-vs-uniform calibration variation. Q-9.C
territory is explicitly out-of-scope for PHASE2C_9.

**3.2.7 ❌ NO Phase 3 progression scoping.** No Phase 3 deliverable
specification; no risk/position-sizing infrastructure scoping; no
phase-progression decision. Q-9.D territory is explicitly
out-of-scope for PHASE2C_9.

**3.2.8 ❌ NO config or code modifications.** No edits to
`config/`, `agents/`, `backtest/`, `strategies/`, `factors/`, or
`scripts/`. PHASE2C_9 is a pure documentation arc.

**3.2.9 ❌ NO 2025 test split touch.** Per CLAUDE.md hard rule;
2025 remains preserved touched-once.

**3.2.10 ❌ NO METHODOLOGY_NOTES amendment within PHASE2C_9.**
Methodology principles surfaced during PHASE2C_9 work are surfaced
at closeout's tracked-fix register; canonical METHODOLOGY_NOTES
update is a follow-up arc (per PHASE2C_8.1 → `8154e99` precedent).

### 3.3 Bright-line summary (one-table reference)

| activity | in-scope? |
|---|---|
| Read Proposer prompt code | ✔ |
| Read Critic gate code | ✔ |
| Read theme rotation code | ✔ |
| Query spend_ledger.db (read-only) | ✔ |
| Read compiled-strategy manifests | ✔ |
| Read per-attempt prompt/response artifacts (sampled) | ✔ |
| Cross-tab theme × pass-count from PHASE2C_8.1 outputs | ✔ |
| Trace `0845d1d7898412f2` end-to-end | ✔ |
| Run new Proposer API call | ❌ |
| Run new Critic API call | ❌ |
| Run new backtest | ❌ |
| Run new evaluation-gate orchestration | ❌ |
| Per-of-198 candidate walkthrough | ❌ |
| Modify any code/config | ❌ |
| Compute DSR / PBO / CPCV | ❌ |
| Vary AND-gate thresholds | ❌ |
| Scope Phase 3 | ❌ |
| Touch 2025 data | ❌ |

---


## 4. Pre-registered exit conditions

Per Claude advisor's Consideration 1 carry-forward: the exit-condition
register requires operational specificity, not gestural framing.
"Structural plausibility" without pre-defined criteria is the
p-hacking-equivalent defect class operating at retrospective register.
This section pre-registers operational evidence criteria for each of
three case determinations BEFORE retrospective evidence collection
begins.

**Pre-registration discipline**: §4 case definitions are frozen at
spec commit. If retrospective evidence surfaces a case pattern that
doesn't fit A/B/C cleanly, the resolution is closeout case=Case C
(ambiguous) + tracked-fix register entry surfacing the pattern, NOT
mid-arc rewriting of §4 to introduce a fourth case. §4 mid-arc
rewrite would defeat pre-registration discipline.

### 4.1 Case A — Mining process plausibly fixable

**Definition**: Retrospective surfaces at least one identifiable
structural defect in mining-process inputs that, if addressed, would
plausibly improve candidate-population quality at register relevant
to deployment-quality strategy generation.

**Qualifying evidence categories (any ONE category satisfied →
Case A is candidate determination)**:

**A.1 — Identifiable Proposer prompt defect.** Concrete examples
of defect register:
- Prompt language steers toward DSL patterns systematically prone
  to overfitting (e.g., complex nested conditions when simpler
  conditions would suffice; specific operator preferences not
  grounded in DSL schema)
- Theme injection mechanism produces prompt-content asymmetry across
  themes (e.g., one theme's prompt is materially richer/poorer than
  others, plausibly explaining theme-level pass-count asymmetries)
- Few-shot examples (if present) exhibit selection bias toward a
  specific candidate property (e.g., examples are all entry-only or
  all exit-only)
- DSL schema constraints surfaced to LLM are misaligned with
  evaluation-time gates (e.g., complexity budget allows DSL forms
  that systematically fail walk-forward validation)

Disqualifying counter-evidence:
- Prompt language is balanced across themes; constraints align with
  DSL schema documented invariants; few-shot example pattern (if
  present) is theme-agnostic in selection logic; no operator-level
  bias surfaced

**A.2 — Identifiable Critic gate defect.** Concrete examples:
- D7a rule scoring formula produces threshold-edge artifacts (e.g.,
  systematically rejects candidates within ε of a bound)
- D7a → D7b routing logic systematically excludes a candidate
  property class (e.g., all `volume_divergence` candidates with X
  property route to D7b but never reach D7b approval)
- D7b prompt structure produces verdicts uncorrelated with downstream
  evaluation outcomes (Critic approves candidates that fail
  walk-forward; Critic rejects candidates that would pass
  walk-forward)
- Forbidden-language scan over-triggers, eliminating valid candidates
  on linguistic-pattern grounds rather than DSL-content grounds

Disqualifying counter-evidence:
- D7a rule formulas have no edge artifacts; D7a → D7b routing is
  property-class-balanced; D7b verdict-vs-evaluation-outcome
  correlation is positive (or at minimum non-negative); forbidden-
  language scan triggers are documented and conservative

**A.3 — Identifiable theme rotation defect.** Concrete examples:
- The 5-theme operational rotation excludes `multi_factor_combination`
  for documented reason, but the exclusion plausibly biased the
  candidate population away from a specific structural pattern that
  would have been deployment-quality
- Theme assignment formula produces order-of-cycle dependencies
  (e.g., earlier-cycle themes systematically receive more attempt
  budget than later-cycle themes due to Proposer-side
  attempt-rejection patterns)
- Theme-rotation `THEMES[(k - 1) % len(THEMES)]` strict-modulo
  policy interacts adversarially with budget-pre-charge ledger
  pattern (e.g., budget-exhaustion concentrates exclusions in
  specific themes)

Disqualifying counter-evidence:
- Theme distribution outcome (40/40/40/39/39) is consistent with
  uniform rotation; no order-of-cycle dependency surfaced; budget
  exhaustion (if any) is theme-balanced; the operational-canonical
  theme-list boundary is documented at CONTRACT BOUNDARY register
  (`agents/themes.py`)

**A.4 — Identifiable AND-gate calibration interaction at
mining-time vs evaluation-time**. Concrete examples:
- Mining-time gate (Critic + lifecycle-state filter) systematically
  passes candidates that mining-time evaluation (train + holdout)
  approves, but those same candidates systematically fail
  evaluation-time gate (PHASE2C_6 4-criterion AND-gate). The
  mining-time / evaluation-time gate misalignment is itself the
  defect (e.g., mining-time gate doesn't predict
  evaluation-time-defensible candidates, despite being designed to)
- Lone-survivor `0845d1d7898412f2`'s hybrid quality profile (audit-only
  origin + filter exclusion by single-trade margin + permissive
  AND-gate accepting -10.2% return) reflects mining-time / evaluation-time
  gate misalignment more than candidate-population coherence

Disqualifying counter-evidence:
- Mining-time → evaluation-time pass-correlation is consistent with
  noise-floor independence (no systematic misalignment surfaces);
  lone-survivor's hybrid quality profile is consistent with
  one-of-N tail event under noise-floor distribution

**Case A determination requires**: at least ONE of A.1 / A.2 / A.3
/ A.4 satisfied with concrete evidence (file:line citations or
canonical-number cross-references) that meets the qualifying
criteria; AND no disqualifying counter-evidence surfaces stronger
than the qualifying evidence; AND the identified defect is plausibly
addressable (i.e., not a fundamental constraint of the LLM-as-Proposer
paradigm).

### 4.2 Case B — Candidate population structurally weak

**Definition**: Retrospective surfaces no identifiable structural
defect in mining-process inputs; observed candidate-population
properties (cohort_a_filtered=0; lone-survivor hybrid quality;
theme-level patterns) are consistent with the candidate population
being structurally weak independent of mining-process inputs.

**Qualifying evidence categories (Case B requires ALL of the
following)**:

**B.1 — Mining-process inputs review surfaces no Case A.1 / A.2 /
A.3 / A.4 defect.** All four Case A categories' qualifying evidence
absent OR present-but-weaker-than-disqualifying-counter-evidence.

**B.2 — Population properties consistent with noise floor.**
Concrete examples:
- cohort_a_filtered=0 outcome is plausibly a one-of-198 sample-size
  artifact at noise floor (i.e., the expected cardinality of
  candidates passing a 4-criterion AND-gate across 4 regimes by
  chance alone, given marginal pass rates per regime, is ≤1)
- Theme-level pass-count distribution shows no systematic
  theme-property correlation; pass-count asymmetries across themes
  are within plausible noise-floor variance
- Pass-count distribution histogram (per PHASE2C_8.1 closeout §4.1)
  is consistent with a near-uniform random-pass distribution rather
  than a structural-pattern distribution

**B.3 — Lone-survivor characterization is tail-event consistent.**
Concrete examples:
- `0845d1d7898412f2`'s hybrid quality (audit-only origin + filter
  exclusion by 1 trade + -10.2% return acceptance) is plausibly
  one-of-N tail event under noise-floor distribution of candidate
  properties; not specific to mining-process input
- Volume-divergence theme's distribution behavior is consistent with
  random theme-allocation rather than systematic theme-quality
  asymmetry

Disqualifying counter-evidence:
- Any Case A.1 / A.2 / A.3 / A.4 qualifying evidence at strength
  greater than disqualifying counter-evidence
- Theme-level systematic correlation surfaces (specific themes
  systematically over- or under-perform at register beyond noise
  floor)
- Lone-survivor characterization shows mining-process-specific
  pattern not consistent with tail-event interpretation

**Case B determination requires**: ALL of B.1, B.2, B.3 satisfied
with concrete evidence; AND no disqualifying counter-evidence
surfaces.

### 4.3 Case C — Ambiguous

**Definition**: Retrospective surfaces evidence consistent with
neither Case A nor Case B fully. Qualifying evidence for Case A
exists but is below the qualifying-evidence threshold; OR
qualifying-evidence-for-Case-B exists but disqualifying-counter-
evidence at register comparable to qualifying-evidence surfaces;
OR retrospective evidence is mixed across categories without
clean resolution.

**Qualifying evidence (any ONE → Case C is candidate
determination)**:

**C.1 — Partial qualifying evidence for Case A.** One or more
Case A categories show "weak qualifying evidence" (suggestive but
not concretely demonstrable defect) without clean Case A.x
qualification.

**C.2 — Mixed qualifying / counter-qualifying evidence for Case
B.** Evidence is consistent with Case B at population-property
register but inconsistent at lone-survivor or theme-level register
(or vice versa).

**C.3 — Light-touch register insufficient for discrimination.**
Light-touch retrospective produces evidence that suggests Case A
or Case B but at strength below the qualification threshold; the
honest read is "structured re-examination would be needed to
discriminate."

**Case C determination requires**: any ONE of C.1 / C.2 / C.3
applicable; AND closeout document explicitly identifies which
sub-register (C.1 / C.2 / C.3) the determination falls in; AND
tracked-fix register entry surfaces the specific evidence
asymmetry that produced the Case C determination.

### 4.4 Case-determination semantics

**One-and-only-one rule**: PHASE2C_9 closeout produces exactly one
case determination (A, B, or C). Multi-case findings (e.g., "Case A
for Proposer prompts; Case B for theme rotation") are explicitly
prohibited at closeout register; if the evidence base supports
multi-case findings, the determination is Case C with sub-registers
documented.

**Reasoning**: case determination is a forward-pointer for
post-Q-9.B scoping cycle. Multi-case findings produce ambiguous
forward-pointer register, which is the same defect class the
exit-condition pre-registration was designed to avoid. Single-case
determination + sub-register documentation under Case C is the
register-precision-preserving resolution.

**Forward-pointer semantics (cycle-boundary preserving)**: case
determinations point at post-Q-9.B scoping cycle's deliberation
register; they DO NOT pre-commit specific second-step direction.

| case | forward-pointer (allowed register) |
|---|---|
| Case A | "Identifiable mining-process defect at category X.Y; post-Q-9.B scoping cycle's deliberation surface includes (a) addressing the identified defect at mining-process redesign register, (b) statistical validation under existing population at Q-9.A register, (c) calibration-variation under existing population at Q-9.C register, (d) phase-progression scoping at Q-9.D register, (e) other paths surfaced at scoping cycle." |
| Case B | "Candidate population is structurally weak at noise-floor consistency; post-Q-9.B scoping cycle's deliberation surface includes (a) phase-progression scoping at Q-9.D register if Phase 3 design is deployable independent of Phase 2C mining outputs, (b) mining-process redesign at scope greater than light-touch retrospective if Phase 3 progression is not deployable independent, (c) other paths surfaced at scoping cycle." |
| Case C | "Light-touch retrospective produced ambiguous evidence at sub-register C.X; post-Q-9.B scoping cycle's deliberation surface includes (a) structured re-examination at depth greater than light-touch, (b) statistical-significance machinery to disambiguate noise-floor vs systematic-pattern at Q-9.A register, (c) calibration-variation at Q-9.C register, (d) other paths surfaced at scoping cycle." |

**Forbidden forward-pointer language** (would defeat cycle-boundary
preservation):
- "Case A confirms Q-9.A is the right next direction"
- "Case B means Phase 3 progression is the next arc"
- "Case A.2 (Critic gate defect) requires immediate Critic redesign
  before any further evaluation work"
- Any phrasing that pre-decides the successor scoping cycle's deliberation

---


## 5. Implementation steps

Sequential gating: each step produces a deliverable that downstream
steps consume. No parallel execution; each step's evidence must land
before the next step initiates.

Target session count: ~2-3 sessions. Cycle-pacing register
preservation: prefer slightly longer than ~2-3 over scope creep.

### 5.1 Step 1 — Code review of mining-process source

**Deliverable**: `docs/closeout/PHASE2C_9_RESULTS.md` §3 (working
draft)

**Activities**:
- Read Proposer code (§2.1): characterize prompt construction +
  theme injection + leakage audit + DSL schema constraint surfacing
- Read Critic code (§2.1): characterize D7a rule formulas + D7a →
  D7b routing + D7b prompt structure + reliability fuse state
- Read theme rotation code (§2.1 + §2.5)

**Output register**: factual mechanism description with file:line
citations. NOT critique; NOT redesign proposal. The output of Step 1
is "what the code does"; Step 4 produces the interpretation
register.

**Gating criterion to enter Step 2**: §3 working draft has
documented mechanism descriptions at file:line citation register
for all of (Proposer prompt; Critic gate; theme rotation).

### 5.2 Step 2 — Artifact-distribution audit

**Deliverable**: `docs/closeout/PHASE2C_9_RESULTS.md` §4 (working
draft)

**Activities**:
- Query `agents/spend_ledger.db` (read-only) for batch
  `b6fcbf86-...`'s lifecycle-state distribution
- Tabulate counts: how many candidates terminated in
  `proposer_invalid_dsl` / `duplicate` / `critic_rejected` /
  `train_failed` / `holdout_failed` / `dsr_failed` / `shortlisted`
  / `budget_exhausted`
- Count compiled-strategy manifests at
  `data/compiled_strategies/` for batch (target: 198 surviving the
  full pipeline to evaluation)
- Cross-check `198` total against canonical anchor (§2.4)

**Output register**: factual lifecycle-state distribution table.

**Gating criterion to enter Step 3**: §4 working draft has
documented lifecycle-state cardinalities; total candidates entering
PHASE2C_6 evaluation matches canonical anchor (198).

### 5.3 Step 3 — Theme × pass-count cross-tab

**Deliverable**: `docs/closeout/PHASE2C_9_RESULTS.md` §5 (working
draft)

**Activities**:
- Read PHASE2C_8.1 closeout §7 theme-level cross-regime pattern
  table (canonical theme-level pass counts at unfiltered tier
  across 4 regimes)
- Build cross-tab: theme (rows) × regime (columns) × pass count
  (cell)
- Cross-tab includes generation-side theme distribution
  (~40/40/40/39/39 per §2.4 anchor) and per-regime pass counts
  per theme
- Identify per-theme pass-count asymmetries
- Cross-check totals against canonical anchors (§2.4)

**Output register**: factual cross-tab + identification of
asymmetries. NOT mechanism interpretation; Step 4 produces
interpretation.

**Gating criterion to enter Step 4**: §5 working draft has the
cross-tab with all canonical anchor cross-checks satisfied.

### 5.4 Step 4 — Lone-survivor walkthrough

**Deliverable**: `docs/closeout/PHASE2C_9_RESULTS.md` §6 (working
draft)

**Activities**:
- Locate `0845d1d7898412f2`'s entry in `raw_payloads/batch_b6fcbf86-.../`
  by attempt-index reverse-lookup or compiled-strategy manifest
  cross-reference
- Read corresponding `attempt_NNNN_prompt.txt` +
  `attempt_NNNN_response.txt`
- Read compiled-strategy manifest at
  `data/compiled_strategies/0845d1d7898412f2.json`
- Cross-reference with PHASE2C_8.1 closeout §6 (lone-survivor
  characterization at evaluation register)
- Document the mining-process trace: what the prompt requested →
  what the LLM proposed → what the compiler produced → what the
  Critic gated → how the candidate reached PHASE2C_6 audit
  partition

**Output register**: factual end-to-end trace. NOT case
determination; Step 6 produces case determination.

**Gating criterion to enter Step 5**: §6 working draft has the
end-to-end trace with all relevant artifacts cited at file:line
register.

### 5.5 Step 5 — Mechanism-vs-observation comparison

**Deliverable**: `docs/closeout/PHASE2C_9_RESULTS.md` §7 (working
draft)

**Activities**:
- Cross-reference Step 1 (mechanism description) with Steps 2-4
  (observation evidence)
- For each Case A category (A.1 / A.2 / A.3 / A.4) defined at §4.1:
  evaluate mechanism description against observation evidence;
  document qualifying-evidence-or-not at register required by §4.1
- For Case B definition at §4.2: evaluate population properties
  against noise-floor consistency criteria
- For Case C sub-registers at §4.3: identify any ambiguity sources
  + their evidence asymmetries

**Output register**: structured evidence map for each case; per-case
qualifying-evidence summary; per-case disqualifying-counter-evidence
summary.

**Gating criterion to enter Step 6**: §7 working draft has
structured evidence maps for all three cases.

### 5.6 Step 6 — Case determination + closeout assembly

**Deliverable**: `docs/closeout/PHASE2C_9_RESULTS.md` (final)

**Activities**:
- Apply case-determination semantics (§4.4 one-and-only-one rule)
  to Step 5's evidence maps
- Document case determination (A / B / C) at closeout §1 verdict
- For Case A: identify which sub-category (A.1 / A.2 / A.3 / A.4)
  applies; document forward-pointer register per §4.4
- For Case B: document population-noise-floor consistency at
  closeout §1 verdict; document forward-pointer register per §4.4
- For Case C: identify which sub-register (C.1 / C.2 / C.3) applies;
  document tracked-fix register entry surfacing the evidence
  asymmetry; document forward-pointer register per §4.4
- Surface tracked-fix register entries (per PHASE2C_8.1 closeout
  §10 precedent)
- Surface methodology-codification candidates (deferred to
  follow-up METHODOLOGY_NOTES update arc per §3.2.10)
- Assemble closeout document at canonical structure (§8)

**Gating criterion to close PHASE2C_9 arc**: closeout document
satisfies §8 structural requirements; case determination passes
verification framework (§6); cycle-boundary-preservation language
audit passes (§7).

---


## 6. Verification framework

Per Claude advisor's prior carry-forward + METHODOLOGY_NOTES §1
empirical verification + §2 meta-claim verification + §11
closeout-assembly discipline. Verification at PHASE2C_9 register is
documentation-grounded (no new statistical machinery required) but
load-bearing.

### 6.1 Evidence-mapping discipline

Every retrospective claim in PHASE2C_9 closeout must cite a specific
source:

- **Code claim**: file:line citation (e.g., `agents/proposer/prompt_builder.py:42-58`)
- **Canonical-number claim**: cross-reference to PHASE2C_8.1 closeout
  section + canonical anchor table (§2.4)
- **Artifact claim**: artifact file path + relevant line/key
  (e.g., `raw_payloads/batch_b6fcbf86-.../attempt_0234_prompt.txt:14`)
- **Interpretation claim**: explicit "this is interpretation, not
  observation" language; cite the observation it interprets

Forbidden in closeout language:
- "It seems like" / "Probably" / "Likely" without evidence map
- "Mining process appears to" without specific code+artifact
  citation
- "The lone survivor's pattern suggests" without §6 walkthrough
  artifact reference
- Unsourced canonical numbers (every cardinality/count must trace
  to either PHASE2C_8.1 anchor or PHASE2C_9 working-draft tabulation)

### 6.2 Falsifiability-statement discipline

Every case-determination assertion at closeout must include explicit
"what would falsify this conclusion" language:

- **Case A**: "This determination would be falsified by [X
  counter-evidence] surfacing at structured re-examination depth"
- **Case B**: "This determination would be falsified by [Y
  pattern] surfacing at noise-floor consistency checks"
- **Case C**: "This determination would be falsified by [Z
  resolution] of the ambiguity sources at deeper retrospective
  register"

Falsifiability statements convert reflexive interpretation into
explicit evidence claims that post-Q-9.B scoping cycle can target
directly if it elects to.

### 6.3 Canonical-number cross-checks

§2.4 canonical anchors are the empirical baseline; every PHASE2C_9
finding must either (a) reproduce the anchor or (b) explicitly
reconcile any apparent mismatch.

Examples of required cross-checks:
- Step 2 lifecycle-state distribution: total candidates entering
  evaluation must equal `198` (anchor)
- Step 3 cross-tab: per-theme totals must approximate anchor
  distribution `~40/40/40/39/39`
- Step 4 lone-survivor: hash must equal `0845d1d7898412f2`; theme
  must equal `volume_divergence`; partition origin must be `audit`
  (PHASE2C_6 audit_v1)

Any cross-check failure halts the arc at the failing step until
reconciled.

### 6.4 Cycle-boundary-preservation language audit

Before closeout commit, full closeout document is read for forbidden
forward-pointer language (§4.4): "next we will run DSR" /
"this confirms Phase 3 progression" / "Case A.2 requires immediate
Critic redesign" / etc. Any forbidden language is rewritten to
allowed-register equivalent before commit.

### 6.5 Independent-recompute gate (light-touch register)

PHASE2C_9 retrospective produces no new canonical numbers; the
canonical-number anchors are inherited from PHASE2C_8.1. No new
independent-recompute test is required (the `tests/` corpus already
verifies PHASE2C_8.1 numbers at
`tests/test_phase2c_8_1_independent_recompute.py`).

The light-touch verification register is therefore:
documentation-grounded evidence-mapping + falsifiability-statement +
canonical-number cross-check + cycle-boundary-preservation language
audit. No new test file is required.

If during Step 5 / Step 6 a new canonical number surfaces (e.g., a
specific sub-distribution count at Step 3's cross-tab that becomes
load-bearing for case determination), the load-bearing number is
captured at closeout §X.X with explicit "this is a PHASE2C_9 derived
canonical number" framing, and a tracked-fix register entry is
surfaced for follow-up arc consideration of independent-recompute
test for the new number. PHASE2C_9 itself does not add the test.

---


## 7. Cycle-boundary preservation

Per Claude advisor's Consideration 3 carry-forward: spec language and
closeout language must not pre-commit to the successor scoping
cycle's second-step direction even at forward-pointer level. This section specifies the
preservation discipline operationally.

### 7.1 Allowed forward-pointer register

The allowed forward-pointer register is "Case X determination
forward-points at post-Q-9.B scoping cycle's deliberation surface;
the deliberation surface includes (a, b, c, d, e), without
pre-commitment to any specific direction."

Examples (allowed):
- "Case A.2 (Critic gate defect) at sub-category register; post-Q-9.B
  scoping cycle's deliberation surface includes (i) addressing the
  identified defect at mining-process redesign register, (ii)
  statistical validation at Q-9.A register, (iii) calibration
  variation at Q-9.C register, (iv) phase-progression scoping at
  Q-9.D register, (v) other paths surfaced at scoping cycle."
- "Case B determination at noise-floor consistency register;
  post-Q-9.B scoping cycle's deliberation surface includes (a, b,
  c) per §4.4."

### 7.2 Forbidden forward-pointer register

Forbidden language (would defeat preservation):
- "PHASE2C_10 will run X"
- "Case A means we proceed to Q-9.A"
- "Case B confirms Phase 3 is the next arc"
- "The next arc should be Y"
- "This determination requires Z"
- Any phrasing that pre-decides the successor scoping cycle's deliberation

If forbidden language surfaces in closeout draft, §6.4 audit
flags it for rewrite before commit.

### 7.3 Closeout structure constraint

PHASE2C_9 closeout's §1 verdict section explicitly carries the
following structural elements:

- Case determination (A / B / C, with sub-register if applicable)
- Per-case evidence summary
- Falsifiability statement
- Forward-pointer register (allowed-register only)
- Tracked-fix register entries surfaced
- Methodology-codification candidates surfaced (deferred to
  follow-up arc)

PHASE2C_9 closeout does NOT carry:
- Recommended next arc selection
- Implementation specification for the successor scoping cycle
- Deliberation register on which post-Q-9.B direction is preferable
- Pre-named successor arc identifier in closeout body (cross-
  reference at §10 footer permitted with anti-pre-naming framing
  per §7.2 forbidden-language register; canonical place stating
  the prohibition is §7.2)

### 7.4 Anti-pre-naming framing forward

The §10 anti-pre-naming discipline at METHODOLOGY_NOTES extends to
PHASE2C_9 → post-Q-9.B successor cycle transition:

- Substantive theme of post-Q-9.B arc is NOT pre-named at PHASE2C_9
  closeout
- Theme selection ratifies through post-Q-9.B scoping cycle
  deliberation register, not through PHASE2C_9 closeout
  pre-convergence
- Reviewer convergence at PHASE2C_9 closeout review register on a
  preferred successor-cycle direction is itself a defect class (the same
  pattern as the walked-back Q-9.A pre-convergence at PHASE2C_9
  scoping cycle); resist informal reviewer convergence as substitute
  for scoping cycle deliberation

---


## 8. Closeout document structure

Canonical structure for `docs/closeout/PHASE2C_9_RESULTS.md`:

```
# PHASE2C_9 — Mining-process retrospective (light-touch) — Results

## 1. Verdict
   1.0 Case determination (A / B / C with sub-register)
   1.1 Per-case evidence summary
   1.2 Falsifiability statement
   1.3 Forward-pointer register (allowed-register only)
   1.4 Verdict register (what this arc establishes / does not establish)

## 2. Scope and methodology
   2.0 Arc setup
   2.1 Input universe (mirror of PHASE2C_9_PLAN.md §2)
   2.2 Hard scope boundaries (mirror of PHASE2C_9_PLAN.md §3)
   2.3 Pre-registered exit conditions (mirror of PHASE2C_9_PLAN.md §4)
   2.4 Verification framework (mirror of PHASE2C_9_PLAN.md §6)

## 3. Mining-process source review (Step 1 deliverable)
   3.1 Proposer prompt mechanism
   3.2 Critic gate logic
   3.3 Theme rotation mechanism

## 4. Artifact-distribution audit (Step 2 deliverable)
   4.0 Lifecycle-state distribution
   4.1 Compiled-strategy manifest count
   4.2 Canonical-number cross-check

## 5. Theme × pass-count cross-tab (Step 3 deliverable)
   5.0 Cross-tab construction
   5.1 Per-theme pass-count asymmetry observations
   5.2 Canonical-number cross-checks

## 6. Lone-survivor walkthrough (Step 4 deliverable)
   6.0 Generation-side trace
   6.1 Compilation manifest
   6.2 Critic gate trace
   6.3 Evaluation-side trace cross-reference

## 7. Mechanism-vs-observation comparison (Step 5 deliverable)
   7.0 Case A evidence map (A.1 / A.2 / A.3 / A.4)
   7.1 Case B evidence map (B.1 / B.2 / B.3)
   7.2 Case C evidence map (C.1 / C.2 / C.3 if applicable)

## 8. Case determination (Step 6 deliverable)
   8.0 Determination
   8.1 Sub-register (if Case A or Case C)
   8.2 Forward-pointer register
   8.3 Tracked-fix register entries surfaced
   8.4 Methodology-codification candidates surfaced

## 9. Cross-references and verification
   9.0 PHASE2C_9_PLAN.md cross-references
   9.1 PHASE2C_8.1 canonical anchor cross-references
   9.2 Verification framework audit (evidence-mapping; falsifiability;
       canonical-number; cycle-boundary language)
```

Length expectation: ~600-1000 lines. Bounded scope (light-touch
register) does not require PHASE2C_8.1's ~3500-line closeout
register; over-length signals scope creep.

---


## 9. Risks and out-of-scope items

### 9.1 Risk register

**R1 — Scope creep into structured re-examination depth.** Light-
touch register requires explicit rejection of per-of-198 walkthrough
during Steps 3-5; if any step surfaces evidence requiring deeper
inspection, the resolution is "surface as Case C (C.3 register) +
tracked-fix entry," NOT "expand light-touch to structured re-
examination." Mitigation: §3 hard-scope-boundaries at three-fold
register (in-scope ✔; out-of-scope ❌; bright-line summary table).

**R2 — Pre-registration discipline drift.** Mid-arc rewriting of §4
exit conditions to fit emerging evidence defeats pre-registration.
Mitigation: §4 frozen at spec commit; §4.4 case-determination
semantics make explicit that mid-arc §4 rewrite is forbidden;
emergent evidence patterns route to Case C with sub-register
documentation.

**R3 — Cycle-boundary-preservation drift.** Closeout reviewers (or
spec drafters) may default to forward-pointer language that
pre-commits successor-cycle direction. Mitigation: §7 explicit allowed-
vs-forbidden language register; §6.4 closeout-document audit before
commit.

**R4 — Retrospective-on-self bias.** Current Claude session
re-examining PHASE2C work cycle's own outputs introduces
narrative-fitting risk (interpretation drift toward conclusions
that justify prior arc decisions). Mitigation: §6.1 evidence-
mapping discipline (every claim cited); §6.2 falsifiability-
statement discipline (every case determination has explicit
falsifying counter-evidence); cross-reviewer adjudication at
closeout register (ChatGPT + Claude advisor + Charlie per
established dual-reviewer protocol).

**R5 — Implementation cost overrun.** Target ~2-3 sessions; risk of
overrun if Steps 3-5 require more inspection than light-touch
admits. Mitigation: explicit "halt and surface as Case C" gating
at Step 5 if mechanism-vs-observation comparison surfaces evidence
requiring deeper register; this preserves session count while
preserving evidence integrity.

**R6 — Methodology-codification candidate accumulation.**
Retrospective work may surface multiple methodology-codification
candidates (per §3.2.10 follow-up-arc handling). Risk: candidates
not surfaced at closeout register get lost. Mitigation: §6 closeout
structure §8.4 explicitly lists methodology-codification candidates
even when they are deferred; closeout commit includes "follow-up
METHODOLOGY_NOTES update arc cross-reference" line.

### 9.2 Out-of-scope items (universal across PHASE2C_9 arc)

- New API calls (Anthropic / Claude / external)
- New backtests or evaluation-gate runs
- Code modifications (any file under `agents/`, `backtest/`,
  `strategies/`, `factors/`, `scripts/`, `config/`)
- 2025 test split touch
- DSR / PBO / CPCV / multiple-comparisons-correction / permutation
  tests
- AND-gate threshold variation
- Phase 3 progression scoping
- Mining-process redesign proposals
- METHODOLOGY_NOTES amendment within arc (deferred to follow-up)
- Successor scoping cycle substantive theme pre-naming
- Per-of-198 candidate walkthrough (lone-survivor trace + at most
  one or two illustrative non-survivors permitted)

---


## 10. Cross-references

- PHASE2C_9.0 scoping decision:
  [`docs/phase2c/PHASE2C_9_SCOPING_DECISION.md`](PHASE2C_9_SCOPING_DECISION.md)
  (commit `3e0c99d`)
- PHASE2C_8.1 closeout (primary empirical anchor):
  [`docs/closeout/PHASE2C_8_1_RESULTS.md`](../closeout/PHASE2C_8_1_RESULTS.md)
  (commit `69e9af9`; tag `phase2c-8-1-multi-regime-extended-v1`)
- PHASE2C_8.1 plan (template precedent):
  [`docs/phase2c/PHASE2C_8_1_PLAN.md`](PHASE2C_8_1_PLAN.md)
  (commit `1e85d1d`)
- METHODOLOGY_NOTES discipline corpus:
  [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  (commit `8154e99`; §1–§15 in force)
- CLAUDE.md project state: PHASE2C_8.1 closeout reconciliation
  + Phase Marker at PHASE2C_9 scoping cycle (commit `3e0c99d`)
- Canonical batch raw payloads:
  `raw_payloads/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9/`
- Canonical theme list:
  [`agents/themes.py`](../../agents/themes.py)
- Canonical AND-gate criteria:
  `config/environments.yaml` (`splits.regime_holdout.passing_criteria`)
