# PHASE2C_13 Sub-Spec — Methodology Consolidation Cycle (Items 1-7 + §9.0c sub-rule + Carry-forwards A/B/C)

**Status:** SEALED at PHASE2C_13 sub-spec drafting cycle SEAL register-event boundary — triple-reviewer pass cycle CLOSED (ChatGPT structural overlay 8 findings + Claude advisor full-prose-access 6 findings + ChatGPT V#6 strengthening pushback at SEAL pre-fire = 15 patches landed at register-precision; per-fix adjudication discipline operated throughout) + V#-chain 12 anchors fired + 3 catches mitigated real-time (V#9 line drift + V#11/V#12 cluster header bug + V#6 row-level mapping methodology refinement) + final full-file prose-access pass per METHODOLOGY_NOTES §17 sub-rule 4 CLEAN at register-precision + Charlie register Q-S27a Reading (iii) + Q-S27 + Q-S28 SEAL bundle authorization APPROVED at register-event boundary fresh adjudication.

**Anchor:** HEAD `6d76517` (Phase Marker advance commit at PHASE2C_13 entry scoping cycle SEAL bundle) at sub-spec authoring; PHASE2C_13 entry scoping cycle SEALED; tag `phase2c-12-breadth-expansion-v1` at deliverable seal commit `1989c85` per Path A.2 register-event boundary discipline (verified pushed to remote real-time at PHASE2C_13 sub-spec drafting cycle entry per Q-S25 (A) authorization closing §19 instance #1 at register-event boundary detection — see §A2 entry).

**Naming clarification (anti-pre-naming option ii):** This document's filename uses `PHASE2C_13` for sequential filename uniqueness only. The arc this sub-spec ships under is the methodology consolidation arc selected at PHASE2C_13 entry scoping cycle SEAL (`docs/phase2c/PHASE2C_13_SCOPING_DECISION.md` §4). PHASE2C_14 + PHASE2C_15 are referenced at scoping decision §1.4 constraint 8 + §4.4 forward-pointer register but their scope specifications are deferred to their own scoping cycles per §1.4 constraint 8; no PHASE2C_14 / PHASE2C_15 scope pre-commitment in this sub-spec body.

---

## §0 Document scope and structure

### §0.1 Scope

This document is the PHASE2C_13 methodology consolidation arc sub-spec drafting cycle deliverable. It codifies (i) Items 1-7 methodology consolidation (Items 1-6 verbatim from PHASE2C_12 Step 9 closeout `docs/closeout/PHASE2C_12_RESULTS.md` §10.2; Item 7 advisor-added at scoping cycle Q-S15-4 adjudication with binding boundary clause); (ii) §9.0c register-class taxonomy 3-class sub-rule (sub-spec drafting / authorization / reviewer); (iii) Carry-forwards A (cycle-complexity scaling diagnosis), B (framework architectural refactor evaluation only — analysis register, NOT implementation), and C (Strong-tier promotion candidates enumeration + Strong-tier bar codification sub-deliverable refining EXISTING METHODOLOGY_NOTES §13-§20 tier framework). The codification specifies HOW each Item / sub-rule / Carry-forward will be implemented at the PHASE2C_13 implementation arc as appended sections (or fold-ins) to `docs/discipline/METHODOLOGY_NOTES.md` per the §16+ append convention.

Scope binding source: PHASE2C_13 scoping decision §6 carry-forward to sub-spec drafting cycle (Path (ii) selected scope binding per §4.2; Charlie register authorization #1 + #2 + #3 SEAL at convergence). This sub-spec does NOT touch strategy refinement (defer to PHASE2C_14 entry scoping cycle), batch fire planning (defer to PHASE2C_15 entry scoping cycle), or framework code refactor implementation (Carry-forward B = evaluation only at analysis register). PHASE2C_12 §8.2 §9.0c instance enumeration is consumed as authoritative input artifact, NOT re-derived (per scoping decision §1.4 constraint 6).

### §0.2 Structure

- §0 Document scope and structure (this section)
- §1 Goal + immediate context (PHASE2C_13 cycle scope summary; cycle-scope budget; constraints inherited from scoping decision §1.4)
- §2 Items 1-7 codification (7 sub-§: §2.1 Item 1 fire-prep precondition checklist + §2.2 Item 2 framework parameter pre-lock + §2.3 Item 3 Step 7/8 contract standardization + §2.4 Item 4 LOCKED items → executable verification function checklist + §2.5 Item 5 reviewer over-interpretation prevention + §2.6 Item 6 §9.0c instance density mechanism + §2.7 Item 7 real-time §9.0c instance handling with binding boundary clause)
- §3 §9.0c register-class taxonomy 3-class sub-rule operationalization (sub-spec drafting register / authorization register / reviewer register; register-class-distinct mitigation strategies; cross-cycle comparability requirement)
- §4 Carry-forwards A/B/C operationalization (3 sub-§: §4.1 Carry-forward A cycle-complexity scaling diagnosis with (a) quantitative metric tracking + (c) forward observation framing + (b) qualitative root cause analysis defer; §4.2 Carry-forward B framework architectural refactor evaluation register-class clarification at analysis register only; §4.3 Carry-forward C Strong-tier promotion candidates enumeration (C-1) + Strong-tier bar codification sub-deliverable (C-2) as refinement of EXISTING tier framework)
- §5 Implementation arc Steps 1-N specification (per-§ seal pattern per PHASE2C_10 precedent; Items 1-7 + sub-rule + Carry-forwards A/B/C → METHODOLOGY_NOTES § slot mapping with fold-in 4-criteria block)
- §6 Closeout deliverable scope specification (`docs/closeout/PHASE2C_13_RESULTS.md` scope; tag naming convention; successor scoping cycle forward-pointer)
- §7 Verification chain V#1-V#N for sub-spec SEAL pre-fire empirical verification
- §8 Reviewer pass cycle disposition (triple-reviewer at sub-spec; per-fix adjudication discipline; catch density expectation)
- §9 Cross-references (PHASE2C_12 / PHASE2C_10 + PHASE2C_11 / METHODOLOGY_NOTES / CLAUDE.md / feedback memory)
- §A1 Cycle-internal §9.0c instance log (appendix; running register for PHASE2C_13 cycle-internal §9.0c instances per Item 7 (a) lightweight tracking; reviewed at cycle boundary fires per Item 7 (c))
- §A2 Cycle-internal §19 instance log (appendix; running register for PHASE2C_13 cycle-internal §19 instances per cross-cutting §19 finding pattern discipline)

### §0.3 Discipline anchors operating at this cycle

Discipline anchors fired during PHASE2C_13 sub-spec drafting cycle per scoping decision §0.3 + cycle-internal additions:

- **Anchor-prose-access discipline (METHODOLOGY_NOTES §16, instance #N+ at sub-spec drafting cycle accumulation register)** — fires at triple-reviewer pass before sub-spec SEAL. Paste relevant prose excerpts; advisor substantive pass against actual prose; THEN commit. Cumulative instance count register at PHASE2C_13 sub-spec drafting cycle close fed into closeout deliverable.
- **Anti-momentum-binding discipline** — every executable-basis HEAD change requires explicit Charlie register re-confirmation; auth boundaries register-class-distinct, never implicitly carried over. Per [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md) hard rule. Operationalized at scoping cycle through 3 Charlie auth boundaries (Q-S15 → auth #1; Q-S16/Q-S17/Q-S18 → auth #2; Q-S21/Q-S22 post-patch convergence → auth #3 SEAL). Continues at sub-spec drafting cycle through Q-S25 (tag push) + Q-S26 (sub-spec drafting cycle entry) + Q-S29/Q-S30/Q-S31 (meta-plan adjudication) + Q-S27 (sub-spec SEAL commit) + Q-S28 (push) — each register-class-distinct.
- **Anti-pre-naming discipline** — arc designation NOT pre-committed in sub-spec body for PHASE2C_14 + PHASE2C_15 (naming clarification at top of document binding); only PHASE2C_13 (this cycle) named in body content.
- **Empirical verification (METHODOLOGY_NOTES §1)** — file structure citations verified before use. Scoping decision §6 binding scope reproduction at register-precision verified at full-draft self-review (Task 19 register; M7 register-class-compromise scope) + at advisor full-prose-access pass (Task 21 register; out-of-scope-for-Task-19 register-class catch). METHODOLOGY_NOTES §13-§20 line numbers re-verified at V#9.
- **Procedural-confirmation defect class (METHODOLOGY_NOTES §17)** — sub-rule 4 (full-file prose-access pass at sealed-commit register; section-targeted patches do not preclude need for full-file final pass) operating at sub-spec SEAL pre-fire (Task 21 Step 21.6).
- **§19 spec-vs-empirical-reality finding pattern (METHODOLOGY_NOTES §19)** — instances surface as instance #N at §A2 cycle-internal log register; cumulative count at sub-spec drafting cycle close fed into closeout deliverable. PHASE2C_13 entry §19 instance #1 (tag-push divergence) carried forward to §A2 (logged + closed real-time at Q-S25 (A)).
- **Item 7 anti-meta-pattern discipline (REAL-TIME during all tasks)** — surface §9.0c instances at occurrence; mitigate immediately per Item 7 (a) lightweight tracking + (c) boundary-fire mitigation review combined; (b) recursive mini-codification REJECTED. **Boundary clause (binding):** TIMING-only mutation, NOT taxonomy/counting. Item 7 codification at §2.7 of this sub-spec; operating discipline at cycle internal during all tasks (§A1 log register operationalized).
- **§9.0c + §19 log mechanics specification** — pre-Task-1 specification at sub-spec drafting cycle meta-plan; §A1 + §A2 schemas (5-column: # / register-class / surface task+step / mitigation note / Item 7 boundary compliance + closure status) with per-entry boundary compliance check at log register itself.

---

## §1 Goal + immediate context

### §1.1 Goal

**Methodology consolidation cycle (Step 9 §10.1 ratified split scope).**

Reproduces scoping decision §1.2 binding verbatim. PHASE2C_13 sub-spec drafting cycle position within the consolidation arc: post-PHASE2C_13-entry-scoping-cycle-SEAL (anchor `df8ca65` + Phase Marker advance `6d76517`), pre-implementation arc (Steps 1-N specified at §5 of this sub-spec). Sub-spec drafting cycle deliverable is binding scope precision for the implementation arc execution at fresh session post-sub-spec SEAL per pacing discipline.

### §1.2 Immediate context (PHASE2C_13 cycle scope summary)

PHASE2C_13 = methodology consolidation cycle per Step 9 §10.1 ratified split scope (split scope decision: PHASE2C_13 = methodology consolidation; PHASE2C_14 = strategy refinement sub-spec drafting; PHASE2C_15 = first batch fire under refined methodology + strategy). Path (ii) selected at scoping decision §4.2 with binding scope per scoping decision §6 (cited as authoritative scope binding source for this sub-spec):

- 6 items verbatim from PHASE2C_12 Step 9 §10.2 (Item 1 fire-prep precondition checklist; Item 2 framework parameter pre-lock; Item 3 Step 7/8 contract standardization; Item 4 LOCKED items → executable verification function checklist; Item 5 reviewer over-interpretation prevention; Item 6 §9.0c instance density mechanism + register-class taxonomy sub-rule)
- Item 7 (advisor-added at scoping cycle Q-S15-4 adjudication; Charlie-ratified at auth #1 + reaffirmed at auth #2 with ChatGPT-load-bearing boundary clause): real-time §9.0c instance handling at PHASE2C_13 cycle internal (anti-meta-pattern discipline); operationalization of Item 6 continuous-vs-batch register choice applied recursively
- §9.0c register-class taxonomy 3-class sub-rule (sub-spec drafting register / authorization register / reviewer register; mitigation strategies register-class-distinct; bulk-mitigation explicitly rejected)
- Carry-forward A (cycle-complexity scaling diagnosis at Step 9 §10.6 anchor; deliverable framing direction (a) quantitative metric tracking + (c) forward observation framing; (b) qualitative root cause analysis defer until (a) data observed)
- Carry-forward B (framework architectural refactor evaluation at analysis register only; NOT implementation per advisor Observation 3 register-class clarification binding; implementation defers to PHASE2C_14 or later cycle if evaluation indicates need; evidence basis: 7 commits to `backtest/evaluate_dsr.py` at PHASE2C_12 cycle at lines 92/124/129/153)
- Carry-forward C (Strong-tier promotion candidates enumeration from cross-cycle accumulation register: §19 cross-cycle = 20 / §9.0c = 8 / M7 register-class-compromise = 2 / Q10+M6-F2 healthy reasoned-adjudication = 2; **Strong-tier bar codification as sub-deliverable** per advisor Observation 4 — refinement of EXISTING METHODOLOGY_NOTES §13-§20 tier framework per V#10 verification at scoping cycle, NOT new framework creation)
- Append target: `docs/discipline/METHODOLOGY_NOTES.md` per §16+ append convention preserved
- Cycle scope ordering: full sub-spec drafting cycle pattern (PHASE2C_10 + PHASE2C_11 + PHASE2C_12 precedent: scoping decision SEAL → sub-spec drafting cycle → reviewer pass cycle → sub-spec SEAL → implementation arc Steps 1-N for METHODOLOGY_NOTES append → closeout deliverable SEAL)

PHASE2C_12 §8.2 §9.0c instance enumeration consumed as authoritative input artifact (per scoping decision §1.4 constraint 6); NOT re-derived. Contemporaneous PHASE2C_13 cycle-internal §9.0c instances (this cycle's accumulation per Item 7 real-time discipline) tracked at register-class-distinct contemporaneous register at §A1 (NOT historical-consume-vs-contemporaneous-track register collision).

### §1.3 Cycle-scope budget

Sub-spec drafting cycle commit count register: ~5-10 commits at sub-spec drafting register (working draft authoring + reviewer pass cycle iteration patches + SEAL bundle), based on PHASE2C_10 / PHASE2C_11 / PHASE2C_12 precedent. PHASE2C_13 sub-spec drafting cycle commit count is register-class-distinct from implementation arc commit count (which is authored at §5 of this sub-spec at separate register).

Predicted reviewer pass cycle catch density: scoping decision had 8 patches / 421 lines = ~1.66% catch density (substantively higher than typical PHASE2C scoping decisions ~0.5-1.0%); sub-spec is substantively larger artifact (~600-900 lines estimated at scoping decision §6.1 register); predicted catch density 1.5-2.5% → 9-22 patches at reviewer pass cycle. Plan reviewer pass cycle iteration count accordingly per §8 reviewer pass cycle disposition.

Cycle scope flexibility: per scoping decision §1.3, commit-count anchor at "short-to-medium" register; specific commit-count enumeration deferred to Carry-forward A operationalization at §4.1 where register-precision metric tracking is in-scope. Flexibility allowed during sub-spec drafting cycle if register-precision concerns surface during Items 1-7 codification authoring or reviewer pass cycle iteration.

### §1.4 Constraints (8 items VERBATIM from scoping decision §1.4)

Scoping decision §1.4 8-constraint enumeration reproduced VERBATIM with PHASE2C_13 sub-spec drafting cycle bindings. Constraints register-class-distinct from PHASE2C_10 §1.4 with PHASE2C_13-specific bindings preserved.

1. **No new generation** — no batch fire, no Proposer/Critic invocation
2. **No new evaluation** — no Stage 2 evaluation runs, no walk-forward fires
3. **No strategy refinement scope** — defer to PHASE2C_14 sub-spec drafting cycle per §10.1 split scope
4. **No framework code refactor implementation** — Carry-forward B = evaluation only at analysis register; implementation defers to PHASE2C_14 or later cycle if evaluation indicates need (binding per §6.4 [sic — empirical citation drift in scoping decision; the Carry-forward B register-class clarification is empirically at scoping decision §6.5 per actual file structure; §6.4 is Carry-forward A cycle-complexity scaling diagnosis; logged at §A2 instance #2 cycle-internal; verbatim preservation discipline applied — no silent fix to SEALED scoping decision content; reader interpretation: substitute §6.5 for §6.4 in this constraint per intent] register-class clarification)
5. **No API spend** — METHODOLOGY_NOTES append + scoping/sub-spec authoring only
6. **No re-derivation of PHASE2C_12 §8.2 §9.0c instance enumeration** — consume Step 9 deliverable as authoritative input artifact (per §10.3). **Register-class clarification:** this constraint binds historical PHASE2C_12 enumeration register only; PHASE2C_13 cycle accumulating new §9.0c instances at PHASE2C_13 cycle internal per Item 7 (real-time §9.0c handling) is register-class-distinct contemporaneous tracking, NOT re-derivation. PHASE2C_12 historical (consume) vs PHASE2C_13 contemporaneous (track per Item 7) are register-class-distinct registers.
7. **No re-opening PHASE2C_12 disposition decisions** — Step 8 Q22 LOCKED `inconclusive` mechanical disposition is canonical at primary anchor (n_eff=197); no interpretive override at PHASE2C_13 cycle
8. **Return to successor scoping post-cycle** — PHASE2C_14 entry scoping cycle is a separate scoping cycle at fresh session post-PHASE2C_13 SEAL per pacing discipline (PHASE2C_10 + PHASE2C_11 + PHASE2C_12 precedent)

Constraint 4's [sic] correction is the FIRST cycle-internal §19 instance surfaced during sub-spec drafting cycle Task 2 authoring (PHASE2C_13 entry §19 instance #1 was carry-forward at sub-spec scaffolding). §19 instance count at this point: cumulative 2 (1 carry-forward at Task 1 + 1 cycle-internal Task 2). Both closed real-time per Item 7 (a)+(c) operationalization.

---

## §2 Items 1-7 codification

This section specifies HOW each Item will be codified at the PHASE2C_13 implementation arc as appended sections (or fold-ins) to `docs/discipline/METHODOLOGY_NOTES.md` per the §16+ append convention. Each sub-§ below provides:

- **Verbatim source** — quoted from PHASE2C_12 closeout `docs/closeout/PHASE2C_12_RESULTS.md` §10.2 (Items 1-6) or scoping decision §6.2 (Item 7) per scoping decision §1.4 constraint 6 consume-vs-derive register
- **Codification mechanism** — HOW the Item codifies as METHODOLOGY_NOTES § content (sub-§ structure: Principle / Trigger context / Application checklist / Failure-mode signal per PHASE2C_10 §13-§17 precedent for new full-§ entries; or fold-in slot per §5 fold-in 4-criteria for fold-in candidates)
- **METHODOLOGY_NOTES § slot specification (provisional)** — candidate § number for new-§ append, OR existing § slot for fold-in; provisional pending §5 final mapping with fold-in 4-criteria check
- **Tier disposition (provisional)** — Strong / Medium / Weak / fold-in disposition; provisional pending §4.3 Carry-forward C Strong-tier bar codification + §2 sub-§ re-check at §4.3 sub-deliverable register

Provisional status of all §2.1-§2.7 dispositions reflects scoping decision §6.6 (C-2) sub-deliverable scope: Strong-tier promotion CRITERIA codified at §4.3, NOT promotions executed at §2 level. Final per-Item tier confirmation fires at §4.3 sub-deliverable + Task 13 Step 13.4 re-check pass.

### §2.1 Item 1 — Fire-prep precondition checklist codification

**Verbatim source (PHASE2C_12 closeout `docs/closeout/PHASE2C_12_RESULTS.md` §10.2 lines 503-507):**

> **Item 1 — Fire-prep precondition checklist codification.** PHASE2C_12 cycle surfaced 4 fire-time precondition gaps (Step 6.5 WF lineage + framework N mismatch + sensitivity table N_eff + ALLOWED_DUAL_GATE_PAIRS asymmetry). Codify mechanical pre-fire verification step at each Step boundary tracing each Q-LOCKED parameter against framework code site.

**Codification mechanism (4-subsection METHODOLOGY_NOTES § structure per PHASE2C_10 §13-§17 precedent):**

- **Principle** — Fire-prep boundary at each Step requires mechanical pre-fire precondition checklist verification; precondition checks trace each Q-LOCKED parameter at sub-spec → framework code site at fire-time → fire-time empirical state. Without explicit precondition checklist, fire-time state divergence from sub-spec lock surface only at post-fire empirical observation register (= §19 instance class + post-fire scoping cycle adjudication overhead).
- **Trigger context** — Multi-step implementation arc fire boundaries (Step 5 main fire / Step 6.5 WF backtest / Step 7 evaluation gate / Step 8 mechanical disposition fire / etc.) where Q-LOCKED parameters bind sub-spec → framework code interface and where fire-time empirical state must match sub-spec lock for downstream-consumer integrity.
- **Application checklist** — At each Step boundary fire-prep:
  1. Enumerate all Q-LOCKED parameters at sub-spec relevant to this Step
  2. For each Q-LOCKED parameter: trace to framework code site (file:line); verify fire-time framework state matches sub-spec lock value
  3. For framework N + threshold + frozenset + similar parametric values: verify fire-time runtime parameter resolution matches sub-spec lock
  4. For inter-step interface contracts (Step N output → Step N+1 input): verify schema + sample compatibility before fire
  5. Surface any drift detected as §19 instance candidate at register-class-distinct register (specification-vs-empirical-reality at fire-prep boundary)
- **Failure-mode signal** — Fire fires without precondition checklist + post-fire empirical observation surfaces sub-spec → framework code drift = canonical failure mode pattern; PHASE2C_12 cycle 4 instances (Step 6.5 WF lineage + framework N mismatch + sensitivity table N_eff + ALLOWED_DUAL_GATE_PAIRS asymmetry) are concrete evidence basis. Pattern recognition: post-fire empirical observation of "wait, this isn't what the sub-spec specified" = retroactive §19 instance + scoping cycle adjudication overhead that pre-fire checklist would prevent at register-class register-precision.

**METHODOLOGY_NOTES § slot specification (provisional):** new §21 (next available sequential slot per V#10 verification at scoping cycle: §20 is last existing §; new §§ append per §16+ append convention). Candidate § title: "Fire-prep precondition checklist discipline at multi-step implementation arc Step boundaries". Final § number + title authored at §5 implementation arc Steps 1-N specification per fold-in 4-criteria check.

**Tier disposition (provisional):** Medium tier candidate. Evidence basis: 4 PHASE2C_12 cycle instances at single-cycle register; cross-cycle accumulation register fed by historical PHASE2C_8-PHASE2C_11 instance backfill at §4.1 Carry-forward A operationalization. Strong-tier promotion contingent on (i) §4.3 Strong-tier bar criteria codified + (ii) cross-cycle accumulation evidence threshold met per Strong-tier bar; provisional Medium tier pending §4.3 + §2 re-check at Task 13 Step 13.4. Worst-case fallback: Weak tier observation-only with cross-cycle-accumulation-pending status note per METHODOLOGY_NOTES §19 register precedent.

---

### §2.2 Item 2 — Framework parameter pre-lock at sub-spec drafting cycle terminus

**Verbatim source (PHASE2C_12 closeout `docs/closeout/PHASE2C_12_RESULTS.md` §10.2 lines 509-513):**

> **Item 2 — Framework parameter pre-lock at sub-spec drafting cycle.** Add "framework parameter audit" sub-step at sub-spec drafting cycle terminus that mechanically enumerates each Q-LOCKED parameter and traces to framework code site. Prevents handoff-noise propagation that produced §19 instances #5, #6, #8, #10.

**Codification mechanism (4-subsection METHODOLOGY_NOTES § structure):**

- **Principle** — Sub-spec drafting cycle terminus must include explicit framework parameter audit sub-step that enumerates every Q-LOCKED parameter at sub-spec and traces to framework code site (file:line citation + canonical value at sub-spec lock vs runtime resolution at framework). Without explicit audit, sub-spec → framework handoff-noise propagation surfaces only at fire-prep boundary or post-fire empirical observation register (= §19 instance class downstream).
- **Trigger context** — Sub-spec drafting cycle SEAL pre-fire boundary; specifically the canonical framework parameter set (N values; threshold constants; frozenset literals; functional-resolver outputs; per-cycle constants like `PHASE2C_12_N_RAW`, `PHASE2C_12_N_ELIGIBLE_OBSERVED`, `ALLOWED_DUAL_GATE_PAIRS`, `_resolve_n_eff_set()`). Sub-spec authors MUST audit before SEAL commit.
- **Application checklist** — At sub-spec drafting cycle SEAL pre-fire:
  1. Enumerate all Q-LOCKED parameters at sub-spec
  2. For each: cite framework code site (file:line) where parameter is bound
  3. For each: confirm sub-spec lock value = framework code canonical value (no drift)
  4. For framework parameters that are runtime-resolved (e.g., `_resolve_n_eff_set()`): confirm resolution function output set matches sub-spec lock semantics
  5. Surface any drift as §19 instance candidate at register-class-distinct register before SEAL fire
- **Failure-mode signal** — Sub-spec SEAL fires without framework parameter audit + downstream fire-prep / fire-time empirical observation surfaces sub-spec → framework code drift = canonical failure mode pattern. PHASE2C_12 cycle §19 instances #5 (sub-spec Q15 [REVISED] {198,80,40,6} vs framework hardcoded {198,80,40,5}) + #6 (ALLOWED_DUAL_GATE_PAIRS parallel-structure incompleteness) + #8 (sensitivity table primary anchor parameterization) + #10 are concrete evidence basis for the handoff-noise propagation pattern that pre-lock audit prevents.

**METHODOLOGY_NOTES § slot specification (provisional):** new §22 (sequential slot post-§21 Item 1). Candidate § title: "Framework parameter pre-lock audit at sub-spec drafting cycle terminus". Final § number + title authored at §5.

**Tier disposition (provisional):** Strong-tier candidate. Evidence basis: 4 PHASE2C_12 cycle instances at §19 cumulative register (instances #5, #6, #8, #10) — substantively higher single-cycle instance density than Item 1's 4 instances at distinct §19-finding register-class. Cross-cycle accumulation pending Carry-forward A historical backfill at §4.1. Strong-tier promotion contingent on §4.3 bar criteria + §2 re-check pass at Task 13 Step 13.4.

### §2.3 Item 3 — Step 7/8 contract standardization

**Verbatim source (PHASE2C_12 closeout `docs/closeout/PHASE2C_12_RESULTS.md` §10.2 lines 515-518):**

> **Item 3 — Step 7/8 contract standardization.** Codify inter-step contract test (schema + sample + validation) at each Step boundary. Step 7 evaluation gate output schema → Step 8 input contract had no explicit interface spec at PHASE2C_12 fire-time.

**Codification mechanism (4-subsection METHODOLOGY_NOTES § structure):**

- **Principle** — Inter-step interface contracts at multi-step implementation arc Step boundaries (Step N output → Step N+1 input) require explicit schema + sample + validation specification at sub-spec authoring time. Without explicit interface spec, downstream Step consumes upstream output at implicit-contract register, with drift surfacing only at fire-time integration debugging or post-fire empirical observation.
- **Trigger context** — Multi-step implementation arc with chained Step output→input dependencies. Specifically Step 7 evaluation gate runner → Step 8 mechanical disposition fire boundary at PHASE2C_12 cycle was the concrete fire-time contract gap; pattern generalizes to any Step N → Step N+1 boundary.
- **Application checklist** — At sub-spec drafting cycle for each multi-step implementation arc Step boundary:
  1. Identify Step N output artifact(s) (file path + format + schema)
  2. Identify Step N+1 input requirement(s) (consumed file path + expected schema + validation rules)
  3. Author explicit interface spec: schema (field enumeration + type + constraint) + sample (canonical example) + validation (consumer-side check function or schema-validator invocation)
  4. Bind interface spec at sub-spec § for the Step boundary
  5. Implementation arc fire fires interface validation as Step N+1 fire-prep precondition (cross-reference Item 1 fire-prep precondition checklist)
- **Failure-mode signal** — Step N → Step N+1 boundary fires without explicit interface spec + Step N+1 fire-time consumes Step N output at implicit-contract register + integration debugging at fire-time / post-fire register surfaces interface gap = canonical failure mode pattern. PHASE2C_12 Step 7 → Step 8 boundary at fire-time was concrete instance.

**METHODOLOGY_NOTES § slot specification (provisional):** new §23 (sequential slot post-§22 Item 2). Candidate § title: "Inter-step contract standardization at multi-step implementation arc Step boundaries". Final § number + title authored at §5.

**Tier disposition (provisional):** Medium tier candidate. Evidence basis: 1 concrete PHASE2C_12 cycle instance at Step 7→8 boundary; pattern generalizes but cross-cycle accumulation thin (single-instance basis per cycle is typical given implementation arc Step boundaries are register-class-distinct from §19 finding register-class). Strong-tier promotion contingent on §4.3 bar criteria; cross-cycle accumulation evidence at §4.1 backfill may be sparse for this Item.

### §2.4 Item 4 — LOCKED items → executable verification function checklist

**Verbatim source (PHASE2C_12 closeout `docs/closeout/PHASE2C_12_RESULTS.md` §10.2 lines 520-523):**

> **Item 4 — LOCKED items → executable checklist.** Each Q-LOCKED item should configure 1 verification function fired automatically at fire-prep time. Example: `_resolve_n_eff_set()` at Auth #6.x-extension is a verification function pattern; Item 4 codifies this as sub-spec drafting cycle requirement.

**Codification mechanism (4-subsection METHODOLOGY_NOTES § structure):**

- **Principle** — Each Q-LOCKED item at sub-spec MUST map to one executable verification function fired automatically at fire-prep boundary. Pattern: `def verify_Q_<n>() -> bool` returning True if fire-time framework state preserves the Q-LOCKED constraint. Inline mechanical verification at fire-prep prevents drift surfacing at post-fire empirical observation register (= §19 instance class downstream).
- **Trigger context** — Sub-spec drafting cycle Q-LOCKED items enumeration + corresponding implementation arc fire boundaries where Q-LOCKED constraints must hold. Pattern co-evolves with Item 1 fire-prep precondition checklist (Item 1 = manual checklist; Item 4 = executable function for each Q-LOCKED item) and Item 2 framework parameter pre-lock (Item 2 = sub-spec terminus audit; Item 4 = fire-time runtime check).
- **Application checklist** — At sub-spec drafting cycle:
  1. Enumerate every Q-LOCKED item at sub-spec
  2. For each: author corresponding verification function spec (function signature + return semantics + invocation surface at fire-prep boundary)
  3. Implementation arc Step N fires verification function set at fire-prep boundary; any False return blocks fire + surfaces drift at register-class-distinct register
  4. Cross-reference: `_resolve_n_eff_set()` at PHASE2C_12 Auth #6.x-extension is concrete pattern reference; Item 4 codifies this as sub-spec drafting cycle requirement (NOT optional)
- **Failure-mode signal** — Q-LOCKED items at sub-spec without corresponding executable verification functions + fire-time preserves Q-LOCKED state by manual checklist (Item 1) + manual checklist incomplete or skipped + drift surfaces at post-fire empirical observation. PHASE2C_12 §19 instances at framework parameter divergence register (e.g., Q3 LOCKED 198 vs actual 197 valid) are concrete evidence basis where executable verification function would have caught at fire-prep before fire fired.

**METHODOLOGY_NOTES § slot specification (provisional):** new §24 (sequential slot post-§23 Item 3). Candidate § title: "Q-LOCKED item executable verification function discipline at fire-prep boundary". Final § number + title authored at §5.

**Tier disposition (provisional):** Medium-to-Strong tier candidate. Evidence basis: 1 concrete PHASE2C_12 pattern reference (`_resolve_n_eff_set()`) + indirect evidence via Item 2 §19 instances (handoff-noise propagation at framework parameters that executable verification would catch). Topical coupling with Item 1 + Item 2 may inform fold-in vs new-§ decision at §5; if fold-in to §22 (Item 2 framework parameter pre-lock) per topical coherence, Item 4 codifies as Application checklist sub-rule of Item 2 rather than standalone §. Final disposition at §5 fold-in 4-criteria check.

### §2.5 Item 5 — Reviewer over-interpretation prevention

**Verbatim source (PHASE2C_12 closeout `docs/closeout/PHASE2C_12_RESULTS.md` §10.2 lines 525-530):**

> **Item 5 — Reviewer over-interpretation prevention.** Codify register-class explicit declaration in each Step deliverable: "Before interpreting metric X, declare which register-class (intermediate / final / sensitivity)". §9.0c instance #8 (advisor pre-fire prediction wrong) is concrete instance of this defect class. Add reviewer prompt template: "Does this metric belong to mechanical-output register or interpretive-overlay register?"

**Codification mechanism (4-subsection METHODOLOGY_NOTES § structure):**

- **Principle** — Each Step deliverable MUST open with explicit register-class declaration block stating which register-class(es) the deliverable's metrics + outputs operate at (mechanical-output / interpretive-overlay / intermediate / final / sensitivity). Reviewer pass cycle receives explicit register-class context with the deliverable; reviewers operate at register-precision matching the declared register-class. Without explicit declaration, reviewer over-interpretation at wrong register-class is canonical defect class (§9.0c reviewer-register instance class).
- **Trigger context** — Multi-step implementation arc Step deliverables; specifically Step deliverables containing metrics + outputs at multiple register-classes (e.g., mechanical compute output AND interpretive overlay) where reviewer-register confusion is common.
- **Application checklist** — At each Step deliverable authoring:
  1. Enumerate metric + output register-classes present in deliverable (mechanical-output / interpretive-overlay / intermediate / final / sensitivity / etc.)
  2. Author explicit register-class declaration block at deliverable §-opening: "This deliverable operates at <register-class A> register for metrics <list>; <register-class B> register for metrics <list>; <register-class C> register for outputs <list>"
  3. For each metric/output: bind register-class context inline at first reference site
  4. Reviewer pass cycle prompt template includes: "For each metric / output cited in deliverable, verify register-class declaration matches actual register-class semantics; flag any register-class mismatch as §9.0c reviewer-register instance candidate"
- **Failure-mode signal** — Step deliverable without register-class declaration block + reviewer pass cycle interprets metric at wrong register-class + interpretive overlay applied to mechanical compute output (or vice versa) = §9.0c reviewer-register instance class. PHASE2C_12 §9.0c instance #8 (advisor pre-fire prediction wrong on Q22 LOCKED mechanical disposition; advisor predicted artifact_evidence at interpretive register but actual was inconclusive at mechanical register) is concrete evidence basis.

**METHODOLOGY_NOTES § slot specification (provisional):** new §25 (sequential slot post-§24 Item 4). Candidate § title: "Register-class explicit declaration at Step deliverable authoring". Final § number + title authored at §5.

**Tier disposition (provisional):** Strong-tier candidate. Evidence basis: 1 concrete PHASE2C_12 §9.0c instance #8 + topical coupling with §16 anchor-prose-access discipline (METHODOLOGY_NOTES §16 reviewer-engagement register) + cross-cycle accumulation potential (reviewer over-interpretation pattern is common across PHASE2C cycles per scoping decision §10.6 cross-cycle scaling observation). Strong-tier promotion contingent on §4.3 bar criteria + cross-cycle accumulation evidence backfill at §4.1.

### §2.6 Item 6 — §9.0c instance density mechanism + register-class taxonomy sub-rule

**Verbatim source (PHASE2C_12 closeout `docs/closeout/PHASE2C_12_RESULTS.md` §10.2 lines 532-545):**

> **Item 6 — §9.0c instance density mechanism + register-class taxonomy sub-rule.** PHASE2C_12 cycle accumulated 8 §9.0c instances (substantively higher than PHASE2C_10 + PHASE2C_11 at comparable cycle stages). Codify **continuous improvement vs batch improvement** register choice:
> - Each §9.0c instance should trigger immediate process patch (continuous)
> - vs current pattern of carry-forward to next consolidation cycle (batch)
> - **Sub-rule: §9.0c register-class taxonomy.** Single "process failure" bucket collapses register-class distinctions. Codify taxonomy with separate register-class enumeration:
>   - Sub-spec drafting register (instances #1, #2, #6)
>   - Authorization register (instance #3)
>   - Reviewer register (instances #4, #5, #7, #8)
> - Mitigation strategies are register-class-distinct; bulk-mitigation collapses register-class precision.

**Codification mechanism (4-subsection METHODOLOGY_NOTES § structure + cross-reference to §3 of this sub-spec for sub-rule operationalization detail):**

- **Principle** — §9.0c process-design observations require continuous-vs-batch improvement register choice + register-class taxonomy preservation. Continuous improvement = each instance triggers immediate process patch at occurrence. Batch improvement = instances accumulate within cycle + mitigated at next consolidation cycle SEAL. Choice between continuous and batch is register-class-distinct from instance taxonomy preservation: taxonomy MUST preserve register-class distinctions (3-class enumeration: sub-spec drafting / authorization / reviewer); bulk-mitigation collapses register-class precision and is explicitly rejected.
- **Trigger context** — Multi-cycle methodology consolidation arcs accumulating §9.0c instances at substantive density (PHASE2C_12 = 8 instances per cycle = substantively higher than PHASE2C_10 + PHASE2C_11 at comparable cycle stages). Continuous-vs-batch choice fires at cycle-class register; taxonomy preservation fires at instance-class register.
- **Application checklist** — At each PHASE2C cycle:
  1. At cycle-entry: declare continuous-vs-batch choice for §9.0c instance handling at this cycle (default: batch at consolidation cycle terminus; continuous applies recursively per Item 7 if cycle scope binds Item 7 anti-meta-pattern discipline)
  2. At each §9.0c instance surface: assign register-class label (sub-spec drafting / authorization / reviewer)
  3. At cycle-internal log: track cumulative count per register-class (cross-cycle comparability requires register-class-distinct counting, NOT single-bucket counting)
  4. At mitigation: apply register-class-distinct mitigation strategy (bulk-mitigation REJECTED)
  5. Cross-reference §3 of this sub-spec for operationalization detail of register-class taxonomy 3-class sub-rule
- **Failure-mode signal** — Single "process failure" bucket counting + bulk-mitigation strategy = canonical failure mode that collapses register-class precision. Cross-cycle methodology measurement (e.g., PHASE2C_12 vs PHASE2C_11 §9.0c density comparison) requires register-class-distinct counting; without taxonomy preservation, cross-cycle comparability is corrupted. PHASE2C_12 cycle 8 instances at §10.2 enumeration with 3-class register-class assignment is concrete evidence basis for the taxonomy-preservation pattern.

**METHODOLOGY_NOTES § slot specification (provisional):** new §26 (sequential slot post-§25 Item 5). Candidate § title: "§9.0c instance density continuous-vs-batch improvement choice + register-class taxonomy preservation". Cross-reference at codification: link to §3 of this sub-spec for register-class taxonomy 3-class sub-rule operationalization detail. Final § number + title authored at §5.

**Tier disposition (provisional):** Strong-tier candidate. Evidence basis: 8 PHASE2C_12 cycle instances + register-class taxonomy already operationalized at PHASE2C_13 entry (this sub-spec §A1 + closeout §10.2 enumeration); cross-cycle accumulation evidence: PHASE2C_10 + PHASE2C_11 instances at lower density (cross-cycle pattern of accumulation at consolidation arc cycles vs scoping arc cycles). Strong-tier promotion contingent on §4.3 bar criteria. Note: Item 6 is the parent Item that Item 7 operationalizes recursively; Item 6 + Item 7 may co-codify at coupled § slot or paired § slots per §5 fold-in 4-criteria check.

### §2.7 Item 7 — Real-time §9.0c instance handling at PHASE2C_13 cycle internal (CRITICAL: boundary clause preservation)

**Verbatim source (PHASE2C_13 scoping decision `docs/phase2c/PHASE2C_13_SCOPING_DECISION.md` §6.2 lines 272-278):**

> **Item 7** — Real-time §9.0c instance handling at PHASE2C_13 cycle internal. Operationalization of Item 6's continuous-vs-batch register choice applied recursively to PHASE2C_13 itself (anti-meta-pattern discipline; mitigate as surfaced, not carry-forward to next consolidation cycle).
>
> **Boundary clause (binding):** Item 7 changes mitigation TIMING only, NOT taxonomy or counting logic. §9.0c register-class taxonomy (sub-spec drafting / authorization / reviewer) stays invariant across cycles; counting logic stays invariant; only WHEN mitigation is applied changes (real-time vs carry-forward-batch). Cross-cycle comparability preserved.

**Bilingual concept anchor (per discipline anchor #10 — bilingual concept explanation for difficult methodology concepts):**

- **English:** Item 7 applies Item 6's continuous improvement register choice recursively to the PHASE2C_13 cycle authoring this sub-spec. The cycle is codifying methodology while ALSO accumulating new §9.0c instances of its own; Item 7 says: mitigate as surfaced (real-time) instead of carrying to next cycle. **Boundary clause:** TIMING-only mutation. Don't change taxonomy (3 register-classes), don't change counting (cumulative count register). Only change WHEN mitigation fires (real-time vs batch). This protects cross-cycle comparability of §9.0c measurement.
- **中文:** Item 7 把 Item 6 的连续改进选择递归地应用到 PHASE2C_13 cycle 自身。Cycle 在 codify methodology 的同时也在积累自己的 §9.0c instances; Item 7 说: 实时 mitigate (出现就处理) 而不是 carry-forward 到下一 cycle。**Boundary clause (边界条款):** 只能改 TIMING (时机), 不能改 taxonomy (分类) 或 counting (计数)。3 register-classes 不变, cumulative count register 不变, 只改 WHEN mitigation fires (real-time vs batch)。这是为了保护 §9.0c measurement 的 cross-cycle comparability (跨 cycle 可比性)。

**Codification mechanism (4-subsection METHODOLOGY_NOTES § structure + boundary clause preservation as Application checklist load-bearing item):**

- **Principle** — Item 6's continuous-vs-batch choice applies recursively to the methodology consolidation cycle that is itself codifying Item 6. When this recursion fires (cycle codifies §9.0c discipline AND accumulates new §9.0c instances), the cycle MUST mitigate accumulated instances at real-time per Item 7 (anti-meta-pattern: don't ship Item 6 codification while violating Item 6 in the cycle that ships it). **Boundary clause invariant: TIMING-only mutation.** Item 7 changes mitigation TIMING (real-time vs batch); Item 7 does NOT change §9.0c taxonomy (3 register-classes invariant) and does NOT change §9.0c counting logic (cumulative count register invariant). Cross-cycle comparability of §9.0c measurement preserved.
- **Trigger context** — Methodology consolidation cycles that codify §9.0c discipline AND accumulate new §9.0c instances internal to the cycle. PHASE2C_13 is the first concrete instance (codifies Item 6 + Item 7 + accumulates §A1 instances real-time). Pattern recurs at any future methodology consolidation cycle that ships §9.0c-related codification.
- **Application checklist** — At cycle entry that binds Item 7 anti-meta-pattern discipline:
  1. Initialize cycle-internal §9.0c instance log at register-precision schema (5-column: # / register-class / surface task+step / mitigation note / boundary compliance + closure status) — this sub-spec §A1 is the canonical instance template
  2. At each §9.0c instance surface during cycle: log to cycle-internal register at occurrence (Item 7 (a) lightweight tracking)
  3. Apply mitigation per cycle-internal context: (c) boundary-fire mitigation review = mitigate at next cycle boundary fire (scoping SEAL / sub-spec SEAL / closeout SEAL); some instances mitigate immediately (e.g., meta-plan structural patch), some at cycle-boundary fire
  4. **BOUNDARY CLAUSE COMPLIANCE CHECK at every mitigation:** verify mitigation alters TIMING only, NOT taxonomy + NOT counting. Boundary compliance column at log register catches violations at register-precision register-class-distinct from sub-spec SEAL pre-fire V#-chain
  5. (b) recursive mini-codification REJECTED — infinite recursion risk: codifying methodology for §9.0c instances accumulated at cycle that codifies §9.0c instance handling = infinite recursion. Stop at (a) + (c) only.
  6. Cycle SEAL pre-fire: V#-chain anchor verifies Item 7 boundary clause preservation (taxonomy + counting invariant; only TIMING mutated)
- **Failure-mode signal** — Cycle codifies Item 6 + Item 7 while violating Item 6 internally (accumulates §9.0c instances + does NOT mitigate at cycle internal + carries to next cycle) = anti-meta-pattern violation. OR cycle mitigates accumulated instances by altering taxonomy or counting (e.g., reclassifying instance to a different register-class to "fix" it; removing instance from cumulative count to "close" it) = boundary clause violation. Both failure modes corrupt cross-cycle comparability of §9.0c measurement.

**Item 7 scope question (open for sub-spec to codify; Charlie register adjudication required at sub-spec SEAL boundary):**

Per scoping decision §6.2 strict reading: Item 7 binding scope = §9.0c instances only. Per advisor pre-drafting Obs 4 + Claude Code adjudication + PHASE2C_13 entry §A2 instance #1 (tag-push divergence) case study evidence: Item 7 spirit applies broadly to anti-meta-pattern findings including §19 instances.

Sub-spec scope question:
- **Reading (i) — Strict scoping decision wording:** Item 7 scope = §9.0c instances only. §19 instances accumulated at cycle internal carry to next consolidation cycle per default batch register.
- **Reading (ii) — Anti-meta-pattern spirit broad:** Item 7 scope = §9.0c instances + §19 instances + similar process-finding-pattern instances. Cross-cycle anti-meta-pattern discipline applies broadly. Empirical evidence at PHASE2C_13 cycle entry: §A2 instance #1 (tag-push divergence) was mitigated real-time at Q-S25 (A) per anti-meta-pattern spirit operating at register-event boundary detection — concrete case study supports Reading (ii).
- **Reading (iii) — Broaden Item 7 scope, separate register-class log per pattern class:** Item 7 scope explicitly broadened to cover §19 + §9.0c + future process-finding patterns; separate cycle-internal log per pattern class (§A1 for §9.0c + §A2 for §19 + etc.) preserves register-class precision per Item 6 sub-rule.

**Advisor lean (per Q-S31 adjudication register):** Reading (iii) = include §19 with separate log per pattern class. PHASE2C_13 cycle empirically operates Reading (iii) at sub-spec scaffolding (§A1 + §A2 register-class-distinct logs) — Reading (iii) is the as-implemented pattern at PHASE2C_13 cycle internal. Codification at this sub-spec § = ratify Reading (iii) at canonical artifact register if Charlie register endorses; OR explicitly defer Item 7 scope binding to implementation arc § codification + carry-forward to PHASE2C_14+ if Charlie register prefers narrower binding.

**§A2 register-class binding under each Reading (binding clarification per Q-S37 Task 20 P1.4 patch):**

§A2 cycle-internal §19 instance log register-class-distinct from Item 7 codification scope; §A2 register-class binding depends on Q-S27a resolution at sub-spec SEAL fire boundary:
- **Under Reading (i) strict §9.0c-only:** §A2 operates at *cycle-internal observational register* — §19 instance log is empirical observation only, NOT operationalization of Item 7 anti-meta-pattern discipline (which binds §9.0c only). §A2 entries serve as cumulative count register for cross-cycle §19 measurement at canonical-artifact register but are NOT normative precedent for cross-cycle §19 anti-meta-pattern handling at future cycles.
- **Under Reading (ii) §9.0c+§19 narrow:** §A2 operates at *normative-precedent register* — §19 instance log IS operationalization of Item 7 anti-meta-pattern discipline at §19 register-class scope; §A2 entry pattern + boundary compliance column is canonical precedent for PHASE2C_14+ cycles binding Item 7 to §19.
- **Under Reading (iii) §9.0c+§19+future-pattern broad:** §A2 operates at *normative-precedent register PLUS future-pattern-extension register* — §A2 entry pattern is canonical precedent for §19 register-class AND extensible to additional pattern-class registers if surfaced at PHASE2C_14+ (e.g., §A3 register-class-distinct log for future emergent process-finding pattern).

Operating pattern at PHASE2C_13 cycle internal does NOT pre-bind Q-S27a resolution; §A2 binding interpretation fires at sub-spec SEAL boundary register-event-distinct from §A2 entry logging register.

**Operating-pattern-vs-codification gap surface (binding for Q-S27a SEAL adjudication per F1 patch):**

Sub-spec scaffolding empirically operates §A2 with FULL Item 7 mechanism since session #1: §A2 5-column schema includes boundary compliance column + mitigation note structured per Item 7 (a)+(c) + cumulative count register preservation per Item 7 boundary clause. Cumulative §A2 entries (#1-#3 + cluster #4-#10) all logged with full Item 7 schema = empirical operating pattern at Reading (iii) register (§19 instance log IS operationalization of Item 7 anti-meta-pattern discipline at §19 register-class scope + future-pattern-extension).

**Q-S27a Reading (i) selection load-bearing implication:** Reading (i) "strict §9.0c-only" selection at SEAL boundary creates operating-pattern-vs-codification gap — codification says §A2 = "observational only" per Reading (i), but sub-spec body operates §A2 as full Item 7 register-class-distinct log per Reading (iii). Charlie register adjudication at Q-S27a SEAL boundary requires either (a) §A2 schema downgrade to observational-format (remove boundary compliance column + Item 7-(a)+(c) mitigation-note structure) at SEAL pre-fire OR (b) explicit codification of Reading (i)-vs-operating-pattern gap as cycle-internal observation carried forward to PHASE2C_14+ at scoping cycle adjudication register. Reading (ii)/(iii) selection preserves operating pattern at register-precision; no schema downgrade required.

**Anti-momentum-binding strict reading at Q-S27a SEAL boundary:** operating-pattern-vs-codification dependency must be surfaced explicitly to Charlie register at Q-S27a SEAL boundary — anti-momentum-binding strict reading prevents implicit Reading binding inheritance from operating pattern; Charlie register decides at register-event boundary post-V#-chain CLEAN + final full-file prose-pass.

**Charlie register adjudication request at sub-spec SEAL pre-fire (Q-S27 boundary):**

> **Q-S27a (sub-question of Q-S27 SEAL auth):** Item 7 scope codification at this sub-spec — Reading (i) strict §9.0c-only / Reading (ii) §9.0c + §19 narrow / Reading (iii) §9.0c + §19 + future-pattern broad with register-class-distinct logs?

**Q-S27a Charlie register adjudication outcome (RESOLVED at SEAL pre-fire register):** **Reading (iii)** — Item 7 scope codification = §9.0c + §19 + future-pattern broad with register-class-distinct logs per cycle internal scaling pattern (§A1 for §9.0c + §A2 for §19 + future §A_N for future-pattern register-classes if surfaced at PHASE2C_14+ scoping cycle adjudication). Reviewer convergence at Reading (iii) per ChatGPT structural overlay register lean + Claude advisor revised lean (post-Charlie-divergence-adjudication register-class-precision honest re-examination: Criterion 4 maturation discipline binds tier promotion register, NOT scope codification breadth at Weak tier register-class; future-pattern accommodation = forward-extension mechanism at scope register, register-class-distinct from specific future-pattern codification at tier register; anti-pre-naming preserved). Charlie register auth APPROVED at SEAL boundary register-event distinct from prior session leans per anti-momentum-binding strict reading.

**Reading (iii) operating implications at canonical artifact register (post-SEAL):**
- Item 7 scope = §9.0c + §19 + future-pattern register-class-distinct logs (3 pattern register-classes accommodated; specific future patterns NOT pre-committed per anti-pre-naming discipline)
- §A1 (§9.0c) + §A2 (§19) operating at full Item 7 mechanism since PHASE2C_13 cycle session #1 (5-column schema + boundary compliance column + cumulative count register preservation per Item 7 boundary clause invariant)
- Future cycles MAY add new pattern register-class logs (e.g., §A3 for emergent process-finding patterns) per same Item 7 anti-meta-pattern discipline at future scoping cycle adjudication register-event boundary
- Cross-cycle comparability anchor preserved: 3-class taxonomy + counting logic invariant; scope codification breadth at Reading (iii) does NOT mutate Item 7 boundary clause invariant (taxonomy + counting register-class-distinct from scope register-class)

**Boundary clause preservation verification (binding at sub-spec SEAL pre-fire V#-chain):**

V#-chain anchor at sub-spec SEAL fires:
- Item 7 codification at this § preserves boundary clause invariant (taxonomy + counting logic stays invariant across PHASE2C cycles)
- Operationalization mechanism per Application checklist items 1-6 strictly within (a) + (c) combined; (b) explicitly REJECTED
- Boundary compliance column at §A1 + §A2 entry register catches violations at log register itself (NOT just at SEAL pre-fire register)
- Cross-cycle comparability anchor: PHASE2C_13 §A1 + §A2 entry schemas can be cross-referenced at PHASE2C_14+ cycle internal logs without taxonomy/counting drift

**METHODOLOGY_NOTES § slot specification (provisional):** new §27 (sequential slot post-§26 Item 6). Candidate § title: "Item 7 anti-meta-pattern discipline at methodology consolidation cycles (real-time §9.0c instance handling with boundary clause)". Coupling with Item 6 (§26) at adjacent slots reflects parent-recursive operationalization relationship; alternatively fold-in to §26 if §5 fold-in 4-criteria check satisfies all 4 criteria (specifically criterion (d) Item 7 boundary clause compliance). Final § number + title + fold-in vs new-§ disposition authored at §5.

**Tier disposition (provisional):** Weak tier observation-only initially. Evidence basis: 1 PHASE2C_13 cycle instance (this sub-spec is the first concrete Item 7 cycle); cross-cycle accumulation pending PHASE2C_14+ instances. Per scoping decision §6.6 (C-2) Strong-tier bar criteria: Strong-tier promotion requires minimum cross-cycle instance count threshold; Weak tier observation-only with cross-cycle-accumulation-pending status note appropriate at PHASE2C_13 register. Promotion path: Medium-tier promotion at PHASE2C_14 cycle if instance accumulates; Strong-tier promotion at PHASE2C_15+ if cross-cycle accumulation evidence threshold met per §4.3 bar.

---

## §3 §9.0c register-class taxonomy 3-class sub-rule operationalization

This section operationalizes the §9.0c register-class taxonomy 3-class sub-rule introduced at §2.6 Item 6 codification mechanism (cross-reference Item 6 Application checklist item 5). §2.6 states the principle (continuous-vs-batch choice + 3-class taxonomy preservation); §3 operationalizes the taxonomy at register-precision register with mitigation strategy enumeration per register-class + cross-cycle comparability requirement. §3 = cross-cycle codification scope (3-class taxonomy invariant content); cycle-internal running log = §A1 register-class-distinct from §3 (rationale: scoping decision §6.3 + Q-S29 §A1/§A2 placement decision rationale at sub-spec deliverable structural register).

### §3.1 3-class enumeration with PHASE2C_12 instance examples (per scoping decision §6.3 verbatim binding)

**Sub-spec drafting register** — §9.0c instances surfacing at sub-spec authoring activity (e.g., implementer-time mechanics decision absent from sub-spec specification; sub-spec section structural choice ambiguity surfacing at authoring register). PHASE2C_12 cycle examples: instances #1, #2, #6 per Step 9 closeout `docs/closeout/PHASE2C_12_RESULTS.md` §8.2 enumeration.

**Authorization register** — §9.0c instances surfacing at Charlie register authorization boundary (e.g., authorization-routing ambiguity at register-event boundary; authorization scope ambiguity at adjudication register). PHASE2C_12 cycle examples: instance #3 per closeout §8.2 enumeration.

**Reviewer register** — §9.0c instances surfacing at reviewer pass cycle (e.g., reviewer over-interpretation; reviewer suggestion bulk-accept candidate; reviewer pass surface absent from sub-spec specification — meta-pattern at PHASE2C_13 §A1 instance #1). PHASE2C_12 cycle examples: instances #4, #5, #7, #8 per closeout §8.2 enumeration.

### §3.2 Register-class-distinct mitigation strategies (per scoping decision §6.3 binding)

Mitigation strategies are register-class-distinct. Bulk-mitigation (single "process failure" bucket with single mitigation strategy) collapses register-class precision and is explicitly rejected at sub-spec codification register.

**Sub-spec drafting register mitigation strategies:**
- Pre-Task specification of mechanics decisions that would otherwise surface at implementer-time (e.g., §9.0c+§19 log mechanics specification at PHASE2C_13 sub-spec drafting cycle pre-Task-1 per Q-S29 fold)
- Sub-spec section structural choice anchored at scoping decision binding scope (no implementer-time structural ambiguity)
- Items 1-N codification mechanism specified at register-precision (4-subsection structure per PHASE2C_10 §13-§17 precedent for new full-§ entries; or fold-in slot per §5 fold-in 4-criteria for fold-in candidates)
- Mitigation timing: at occurrence during sub-spec drafting cycle authoring (Item 7 (a) lightweight tracking) OR at sub-spec drafting cycle SEAL pre-fire (Item 7 (c) boundary-fire mitigation review)

**Authorization register mitigation strategies:**
- Authorization-routing discipline operating per [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md) hard rule (Charlie-register-only authorization for operational fires; reviewer convergence is advisory only)
- Anti-momentum-binding strict reading at every authorization boundary (no implicit auth carry-over across register-class-distinct boundaries)
- Authorization sub-question surfacing at register-event boundary detection (e.g., Q-S25 tag-push fire authorization surfacing at PHASE2C_13 sub-spec drafting cycle entry register-event boundary)
- Mitigation timing: at register-event boundary occurrence (Item 7 (a) lightweight tracking) — authorization-class instances are typically real-time mitigation per anti-momentum-binding discipline (carry-forward batching of authorization decisions violates anti-momentum-binding)

**Reviewer register mitigation strategies:**
- Reasoned reviewer-suggestion adjudication per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) (no bulk-accept; per-fix verification)
- Reviewer scope clarification at sub-spec specification (e.g., Codex skip at sub-spec drafting cycle register per scoping decision §5.3; ChatGPT structural overlay vs Claude advisor full-prose-access pass register-class distinction)
- Reviewer over-interpretation prevention per Item 5 (register-class explicit declaration in each Step deliverable; cross-reference §2.5)
- Mitigation timing: at reviewer pass cycle iteration (Item 7 (a) lightweight tracking) OR at sub-spec drafting cycle SEAL pre-fire if reviewer-pass-aggregated mitigation is appropriate

**Cross-class anti-pattern (rejected at sub-spec codification register):**
- "Process failure" bulk-bucket counting + single bulk-mitigation strategy = canonical register-class precision collapse. Cross-cycle methodology measurement (e.g., PHASE2C_12 vs PHASE2C_11 §9.0c density comparison per closeout §10.6) requires register-class-distinct counting; bulk counting corrupts cross-cycle comparability anchor.

### §3.3 Cross-cycle comparability requirement (Item 7 boundary clause anchor)

Per Item 7 boundary clause (§2.7 verbatim binding): §9.0c register-class taxonomy stays invariant across PHASE2C cycles; counting logic stays invariant; only WHEN mitigation is applied changes (real-time vs carry-forward-batch). Cross-cycle comparability preserved.

**Operational requirements at register-precision register:**

1. **3-class enumeration invariance** — sub-spec drafting / authorization / reviewer register-class labels stay consistent across PHASE2C cycles. New register-classes MAY be added at future cycles (e.g., implementation arc fire register; deliverable assembly register) only if (i) Charlie register authorizes at scoping cycle adjudication; (ii) added register-class is register-class-distinct from existing 3 classes (no overlap); (iii) cross-cycle comparability anchor preserved at new register-class introduction (i.e., adding new class does NOT corrupt existing 3-class historical instance enumeration at PHASE2C_12 etc.)
2. **Counting logic invariance** — cumulative count register per cycle = sum of all instances logged within cycle (open + closed); instances are NEVER removed from cumulative count (closure status changes; count register preserved). Cross-cycle cumulative comparison reads canonical register-class-distinct counts.
3. **Mitigation timing variance allowed** — Item 7 binding: real-time mitigation per (a)+(c) when cycle binds Item 7 anti-meta-pattern discipline; carry-forward-batch mitigation per default at non-Item-7-binding cycles. Both timing choices preserve invariance #1 + #2.
4. **Boundary compliance check at every mitigation** — each mitigation entry at cycle-internal log MUST include boundary compliance assessment (Y=BOUNDARY VIOLATION if mitigation altered taxonomy/counting; N=clean if mitigation altered TIMING/structure only). Boundary compliance column at log register itself catches violations at register-precision distinct from cycle SEAL pre-fire V#-chain register (the V#-chain anchor is a backup, not primary).
5. **Mitigation-note text register-precision discipline (per F2 patch — boundary-compliance precedent note)** — mitigation-note text correction at log entry register (e.g., correcting self-contradictory claim that fails empirical verification against canonical anchor) preserves N=clean at register-precision IF cumulative count register integrity preserved (instance still present at log; instance # preserved; closure status preserved). Mitigation-note text register-precision discipline operates at register-class-distinct register from taxonomy/counting invariance (Item 7 boundary clause core) — text correction at log register = register-precision-discipline-application register, NOT taxonomy/counting mutation. Cumulative count register integrity is the binding Item 7 boundary clause invariant; mitigation-note text quality discipline operates at separate register-class.
6. **Cluster-format log entries cross-cycle parse register-precision (per F4 patch)** — cluster log entries at cycle-internal log MUST enumerate sub-defect count explicitly at mitigation note (e.g., "#4-#10 cluster representing 7 distinct sub-defects per cluster surface event") for cross-cycle parse register-precision. Cumulative count register integrity at PHASE2C_13 register requires per-defect numbering preserved across cluster (instance # range #4-#10 = 7 instances, NOT 1 instance); cross-cycle reader (PHASE2C_14+) parsing cluster format MUST sum per-defect numbers for cumulative count comparability anchor preservation. Cluster format is acceptable register-class for multi-defect single-surface-event logging when per-defect register-precision content enumerated at mitigation note + cumulative count clarification at closure status register.
7. **Row-level mapping methodology for V#6 verification (per V#6 strengthening at §A2 #15 register)** — V#6 invariant is "1:1 mapping between log entries and boundary assessments" at row-level register — NOT string-count grep proxy. Verification methodology: bounded-section awk extraction (`awk '/^## §A1/,/^## §A2/'` for §A1 + `awk '/^## §A2/,EOF'` for §A2) + row-grep at column-1 instance-numbering pattern (`^\| #[0-9]+`) + closure-column N=clean count cross-check. Row count matches boundary assessment count at register-precision; string-count grep across full file returns row-level + prose summary mentions (register-class-distinct registers). Cluster row + single boundary assessment = 1 mitigation entry per cluster surface event per Item 6 sub-rule register-class-distinct counting; cluster format does NOT violate 1:1 row-to-boundary-assessment mapping at register-precision. **String-count "N=clean" grep proxy method is unreliable and discarded** per ChatGPT advisor SEAL pre-fire pushback at PHASE2C_13 sub-spec drafting cycle SEAL boundary register-event.

### §3.4 Sub-spec implementation arc § slot binding (cross-reference §2.6 + §5)

§3 codification ships at the implementation arc as METHODOLOGY_NOTES § content. Per §2.6 provisional § slot specification: §3 operationalization detail folds-into §26 (Item 6 §) as detailed sub-rule operationalization OR ships as cross-referenced standalone §27a sub-section under §27 (Item 7 §) per coupling with Item 6 + Item 7 parent-recursive operationalization relationship. Final § slot disposition + fold-in vs new-§ choice authored at §5 implementation arc Steps 1-N specification per fold-in 4-criteria check.

---

## §4 Carry-forwards A/B/C operationalization

This section operationalizes the 3 Carry-forwards from scoping decision §6.4-§6.6 binding scope. Each Carry-forward is register-class-distinct: A is methodology-observation register (cycle-complexity scaling diagnosis); B is framework-architectural-evaluation register (analysis only, NOT implementation); C is tier-framework-refinement register (Strong-tier promotion candidates + Strong-tier bar codification sub-deliverable). Sub-spec authors operationalization mechanism for each at register-precision; Charlie register adjudicates at sub-spec SEAL pre-fire boundary.

### §4.1 Carry-forward A — Cycle-complexity scaling diagnosis

Scoping decision §6.4 binding: (a) Quantitative metric tracking + (c) Forward observation framing for PHASE2C_14+; (b) Qualitative root cause analysis DEFER until (a) data observed. Operationalization at §4.1:

#### §4.1.1 (a) Quantitative metric tracking specification

**Metric set (canonical for cross-cycle tracking):**

| Metric | Definition | Data source |
| ------ | ---------- | ----------- |
| Auth boundaries per cycle | Count of explicit Charlie register authorization boundaries fired during cycle (scoping + sub-spec drafting + implementation arc + SEAL bundle inclusive) | Cycle closeout `docs/closeout/PHASE2C_<N>_RESULTS.md` + CLAUDE.md Phase Marker SEAL entry per cycle |
| Commit count per cycle | Count of git commits within cycle scope (cycle-entry-anchor commit through cycle-SEAL-anchor commit inclusive); split by cycle phase (scoping / sub-spec drafting / implementation arc / closeout) | `git log <cycle-entry-anchor>..<cycle-SEAL-anchor>` |
| §19 instance count per cycle | Cumulative count of §19 spec-vs-empirical-reality finding pattern instances at cycle, per cycle phase (scoping / sub-spec drafting / implementation / closeout) | Cycle closeout §-cumulative-count register per cycle (PHASE2C_11 closeout §0.5; PHASE2C_12 closeout §10 + §19 cumulative count) |
| §9.0c instance count per cycle | Cumulative count of §9.0c process-design observation instances at cycle, broken down by 3-class register (sub-spec drafting / authorization / reviewer) | Cycle closeout §8.2-style enumeration per cycle (PHASE2C_12 §8.2 = 8 instances; PHASE2C_10/11 enumeration TBD per backfill) |

**Initial backfill (from CLAUDE.md Phase Marker + cycle closeout deliverables already in repo at PHASE2C_13 sub-spec drafting cycle entry register):**

| Cycle | Auth boundaries | Commit count | §19 instance count | §9.0c instance count |
| ----- | --------------- | ------------ | ------------------ | -------------------- |
| PHASE2C_8.1 | TBD (backfill at implementation arc) | TBD | TBD | TBD |
| PHASE2C_9 | TBD | TBD | 3 (per CLAUDE.md PHASE2C_9 SEAL entry §8.4 mandatory-tracked-fix entry #2) | TBD |
| PHASE2C_10 | TBD | TBD | 3 (cycle-local: scoping=2 + plan-drafting=1) / 6 (cross-cycle cumulative since PHASE2C_9, per CLAUDE.md PHASE2C_10 SEAL entry §19 cycle) | TBD |
| PHASE2C_11 | ~10 (per scoping decision §6.4 reference) | TBD | 10 within-arc (4 sub-spec drafting + 3 Step 1 implementation + 3 Step 4 closeout per CLAUDE.md PHASE2C_11 SEAL entry §0.5 verbatim) | TBD |
| PHASE2C_12 | 16 (per CLAUDE.md PHASE2C_12 SEAL entry "15 explicit Charlie auth boundaries... Auth #7 = 16th = this deliverable seal") | TBD | 10 PHASE2C_12 cycle (per CLAUDE.md PHASE2C_12 SEAL entry "§19 spec-vs-empirical-reality cumulative count = 10 PHASE2C_12 (cross-cycle 20 since PHASE2C_9)") | 8 PHASE2C_12 cycle (per CLAUDE.md PHASE2C_12 SEAL entry "§9.0c process-design observation cumulative count = 8 PHASE2C_12") |
| PHASE2C_13 | (in progress; scoping cycle = 3 + sub-spec drafting cycle current count = 4 inclusive Q-S25 + Q-S26 + Q-S29/30/31 + Q-S32; SEAL bundle Q-S27/Q-S28 pending) | (in progress) | (in progress; current count = 2 closed at §A2) | (in progress; current count = 1 closed at §A1) |

**Backfill scope binding:** PHASE2C_8.1 / PHASE2C_9 / PHASE2C_10 / PHASE2C_11 cycle full backfill (commit count + §9.0c instance count + auth boundary count) is **DEFERRED to implementation arc** (Carry-forward A § seal at PHASE2C_13 implementation arc). Sub-spec drafting cycle scope binds methodology framework + initial partial table from readily-available CLAUDE.md anchors only; full empirical backfill requires per-cycle closeout deliverable empirical reads + git log enumeration which is implementation-arc work register-class-distinct from sub-spec drafting cycle scope.

#### §4.1.2 (c) Forward observation framing for PHASE2C_14+

**Monitoring mechanism for PHASE2C_14+ cycles (anti-pre-naming preserved — this specifies WHAT to monitor without pre-naming PHASE2C_14 scope):**

- Cycle SEAL closeout deliverable MUST include cycle-cumulative metric reporting per the canonical metric set (auth boundaries + commit count + §19 + §9.0c per register-class)
- Cross-cycle delta tracking: each cycle SEAL closeout reports cycle metrics + delta vs prior cycle (PHASE2C_<N> metric vs PHASE2C_<N-1> metric)
- Threshold for "scaling concern" surface (PROVISIONAL — Charlie register adjudicates final threshold at Carry-forward A § seal at implementation arc):
  - Auth boundaries per cycle: >20 = surface as scaling-concern at cycle SEAL register
  - §9.0c instance count per cycle: >12 = surface as scaling-concern (PHASE2C_12 = 8 = baseline; +50% = surface threshold)
  - §19 instance count per cycle: >15 = surface as scaling-concern (PHASE2C_12 = 10 = baseline; +50% = surface threshold)
- Surface mechanism: cycle SEAL closeout deliverable §-cumulative-count register includes "scaling-concern surface" line if any threshold crossed; closeout fires forward-pointer to next consolidation cycle for codification of mitigation if cross-cycle pattern persists

**Anti-pre-naming preserved at this specification:** PHASE2C_14 + PHASE2C_15 scope NOT pre-committed; only specification of WHAT each future cycle's closeout MUST report on (metric reporting requirement) + threshold values for surfacing scaling-concern.

#### §4.1.3 (b) Qualitative root cause analysis DEFER explicit statement

Per scoping decision §6.4 binding: (b) qualitative root cause analysis DEFERS until (a) data observed. Pure diagnosis without action recommendation is limited value at scoping register; (a) data observation may inform whether (b) is in-scope at PHASE2C_13 implementation arc OR carry-forward to PHASE2C_14+ consolidation cycle.

**Defer disposition (binding at sub-spec register):** (b) NOT in scope for PHASE2C_13 sub-spec drafting cycle. Implementation arc Carry-forward A § seal MAY include preliminary (b) prose if (a) backfill data exposes a clear root cause pattern; otherwise (b) carries forward to PHASE2C_14+ consolidation cycle scoping cycle for adjudication.

#### §4.1.4 §6.9 methodology candidate cross-reference (cycle scope iteration-count taxonomy)

Per scoping decision §6.9 binding: scoping cycle iteration-count register-class taxonomy is sub-component of Carry-forward A operationalization. Evidence basis from scoping decision §4.5 adjudication transparency note: PHASE2C_10 / PHASE2C_11 / PHASE2C_12 / PHASE2C_13 scoping cycles exhibit variable iteration patterns (PHASE2C_10/11/12 single-cycle adjudication; PHASE2C_13 = 2 reviewer pass cycles + 3 Charlie register authorization boundaries per scoping decision §4.5 verbatim).

**Methodology candidate codification at §4.1 register:**

- **Tracking metric (sub-component of Carry-forward A canonical set):** scoping cycle iteration count per cycle + iteration causes (substantive divergence on which sub-questions, at which reviewer register)
- **Surface mechanism:** cycle scoping decision SEAL register includes scoping cycle iteration count + iteration cause summary line
- **Cross-cycle comparability:** PHASE2C_10/11/12 baseline = 1-cycle scoping; PHASE2C_13 = 2-cycle scoping; future-cycle iteration count tracked for cross-cycle scaling diagnosis pattern alongside other §4.1.1 metrics
- **Disposition at PHASE2C_13 register:** Weak tier observation-only with cross-cycle-accumulation-pending status note (single 2-cycle data point at PHASE2C_13; cross-cycle accumulation needed for tier promotion); carries forward to PHASE2C_14+ for accumulation evidence at Carry-forward A § seal at implementation arc

### §4.2 Carry-forward B — Framework architectural refactor evaluation (analysis register only)

Scoping decision §6.5 binding: framework architectural refactor **evaluation only** at analysis register; NOT implementation. Implementation defers to PHASE2C_14 or later cycle if PHASE2C_13 evaluation indicates need. Operationalization at §4.2:

#### §4.2.1 Register-class clarification (binding) explicit statement

Per scoping decision §6.5 verbatim binding (advisor Observation 3 + Charlie register auth #2 ratification): Carry-forward B = framework architectural refactor **evaluation only** at analysis register. Implementation defers to PHASE2C_14 sub-spec drafting cycle or later cycle if PHASE2C_13 evaluation indicates need. PHASE2C_13 sub-spec authors evaluation methodology; does NOT modify `backtest/evaluate_dsr.py` or other framework code.

**Anti-implementation guardrail (binding at sub-spec + implementation arc register):**

Implementation arc Carry-forward B § codifies evaluation outcome ONLY:
- "Evaluation indicates refactor needed; deferred to PHASE2C_14 or later cycle" — if evaluation surfaces architectural refactor candidate
- "Evaluation indicates current pattern sustainable through PHASE2C_15" — if evaluation does NOT surface refactor candidate at PHASE2C_13 evidence basis register
- Mid-evaluation sustainability uncertainty — explicit "evaluation inconclusive" disposition with carry-forward to PHASE2C_14+ for additional evidence basis

#### §4.2.2 Evidence basis from PHASE2C_12 (per scoping decision §6.5 binding)

PHASE2C_12 cycle 7 commits to `backtest/evaluate_dsr.py`:
- `8887651` (Step 8 fire-prep auth #6.x β1 narrow)
- `2a5c63a` (Codex hotfix at Step 8 fire-prep)
- `605dfc6` (auth #6.x-extension)
- `995fdb2` (auth #6.x-extension follow-up)
- `3e1ee89` (auth #6.y)
- `08e1488` (Step 8 fire-prep auth #6.y β1 eligible-subset (197, 139) parallel-structure pair)
- + intermediate commits

Cycle-specific framework patches at code site:
- `PHASE2C_12_N_RAW = 197` at line 92
- `PHASE2C_12_N_ELIGIBLE_OBSERVED = 139` at line 124
- `ALLOWED_DUAL_GATE_PAIRS` 4-pair frozenset at line 129
- `_resolve_n_eff_set()` at line 153

#### §4.2.3 Evaluation methodology specification

Implementation arc Carry-forward B § fires the evaluation per:

**Evaluation question (sustainability framing):** Are cycle-specific hardcoded constants at `backtest/evaluate_dsr.py` (PHASE2C_12 4 named constants + per-cycle helper functions) a sustainable architectural pattern across PHASE2C_13+ cycles?

**Alternative architectural patterns considered (without false-binary framing — multiple candidates evaluated, NOT just refactor-vs-status-quo binary):**

1. **Status quo** — per-cycle hardcoded constants at framework code site; cycle-specific helper functions added per cycle. Pros: minimal code change per cycle (additive); concrete cycle-specific values readable inline at code site. Cons: framework code accretes per-cycle constants over time; cross-cycle code site grows; refactor pressure increases per cycle.
2. **Config injection** — cycle parameters externalized to per-cycle YAML/JSON config file; framework code reads config at runtime. Pros: framework code stable across cycles; per-cycle changes isolated to config files. Cons: indirection layer adds cognitive overhead at debugging; runtime config validation requirement.
3. **Cycle-state-machine** — abstract base class for cycle parameters with per-cycle subclass; framework code instantiates per-cycle subclass at runtime. Pros: structural separation of cross-cycle invariant logic from per-cycle parameters. Cons: substantive refactor effort; unclear sustainability advantage over (2) at single-evaluator-per-cycle pattern.
4. **Hybrid** — frequently-changed parameters (N values; threshold constants) externalized to config; rarely-changed structure (helper function set) stays inline. Pros: targeted refactor at highest-churn surface. Cons: hybrid boundary judgment per parameter type.

**Evaluation criteria for "needed refactor":**

- (i) Framework code accretion rate at `backtest/evaluate_dsr.py` per cycle (lines added per cycle for cycle-specific constants + helper functions)
- (ii) Cross-cycle confusion frequency at framework code site (e.g., PHASE2C_12 vs PHASE2C_11 constants visible at same code site = potential reviewer/implementer confusion)
- (iii) Per-cycle change surface area (e.g., if PHASE2C_13 adds 4-5 new constants similar to PHASE2C_12, refactor pressure increases; if PHASE2C_13 adds 0-1 constants, status quo sustainable)
- (iv) Cross-cycle implementation arc § seal cumulative effort (per-cycle framework code change effort across PHASE2C_8-PHASE2C_12 cycles inclusive)

#### §4.2.4 Implementation arc § codification scope

Implementation arc Carry-forward B § ships at PHASE2C_13 implementation arc after Carry-forward A § codification (which provides metric data feeding evaluation criteria (i) + (iv)). § content includes:
- Evaluation methodology summary (this §4.2 codification)
- Alternative pattern enumeration (this §4.2.3 4-candidate enumeration)
- Evaluation against criteria (i)-(iv) at implementation arc empirical evidence basis
- Disposition: refactor-needed / sustainable-through-PHASE2C_15 / inconclusive
- Forward-pointer to PHASE2C_14+ if refactor disposition is "needed" or "inconclusive"

**METHODOLOGY_NOTES § slot:** Carry-forward B implementation arc § codifies as METHODOLOGY_NOTES entry — candidate § slot at new §28 (sequential post-§27 Item 7) or fold-in if §5 fold-in 4-criteria check satisfies. Note: Carry-forward B is meta-evaluation register (evaluating framework code architectural pattern, NOT codifying methodology rule for application); fold-in to existing § scope unlikely (criterion (a) topical match weak); new-§ slot likely. Final disposition at §5.

### §4.3 Carry-forward C — Strong-tier promotion candidates + Strong-tier bar codification

Scoping decision §6.6 binding: (C-1) Strong-tier promotion candidates enumeration + (C-2) Strong-tier bar codification sub-deliverable as REFINEMENT of EXISTING METHODOLOGY_NOTES §13-§20 tier framework per V#10 (NOT new framework creation).

**Bilingual concept anchor (per discipline anchor #10 — Strong-tier bar codification is difficult methodology concept):**

- **English:** Carry-forward C does TWO things. (C-1) lists candidate observations from cross-cycle accumulation that MIGHT deserve Strong-tier status (the highest tier in METHODOLOGY_NOTES at §20-style register reflecting binding operating rule). (C-2) codifies the BAR for Strong-tier promotion — what specific criteria a candidate must meet. PHASE2C_13 sub-spec defines the bar criteria; does NOT promote candidates to Strong-tier (promotion executions happen at implementation arc § seal or later cycle). The bar codification is REFINEMENT of EXISTING tier framework (Weak/Medium/Strong tiers at METHODOLOGY_NOTES §13-§20 already exist per V#10), NOT new framework creation.
- **中文:** Carry-forward C 做两件事。(C-1) 列出 cross-cycle 累积的 candidate observations 可能 deserve Strong-tier (METHODOLOGY_NOTES §20 风格的最高 tier, 反映 binding operating rule)。(C-2) codify Strong-tier promotion 的 bar (具体 criteria 一个 candidate 必须满足)。PHASE2C_13 sub-spec 定义 bar criteria; 不 promote candidates 到 Strong-tier (promotion execution 在 implementation arc § seal 或 later cycle)。Bar codification 是 REFINEMENT of EXISTING tier framework (Weak/Medium/Strong tiers at METHODOLOGY_NOTES §13-§20 已存在 per V#10), 不是 new framework 创造。

#### §4.3.1 (C-1) Strong-tier promotion candidates enumeration

Per scoping decision §6.6 (C-1) candidates from cross-cycle accumulation register at PHASE2C_13 sub-spec drafting cycle entry:

**Candidate 1 — §19 spec-vs-empirical-reality finding pattern broad anti-meta-pattern application**
- Current tier (per METHODOLOGY_NOTES §19): Weak tier observation-only with cross-cycle-pending status note
- Cross-cycle accumulation: 20 instances cumulative cross-cycle since PHASE2C_9 (per CLAUDE.md PHASE2C_12 SEAL entry verbatim)
- Strong-tier promotion rationale: 20-instance cumulative across 4+ cycles (PHASE2C_9 + PHASE2C_10 + PHASE2C_11 + PHASE2C_12) demonstrates pattern saturation; mitigation strategy specifiable (real-time logging + boundary-fire mitigation review per Item 7 (a)+(c) operationalization broadened to §19 per Q-S27a Reading (iii) advisor lean)
- Strong-tier promotion blocker: Q-S27a Charlie register adjudication required at sub-spec SEAL pre-fire (Reading (i) strict §9.0c-only excludes §19 from Item 7 broadening; Readings (ii)/(iii) include §19)

**Candidate 2 — §9.0c process-design observation density pattern**
- Current tier (per METHODOLOGY_NOTES § codification at PHASE2C_13 implementation arc — Item 6 § slot at §26 provisional): not yet codified at PHASE2C_13 cycle entry; codification ships at PHASE2C_13 implementation arc (Items 6 + 7 § seals)
- Cross-cycle accumulation: 8 instances at PHASE2C_12 cycle alone; lower density at PHASE2C_10 + PHASE2C_11 (cross-cycle backfill at §4.1.1 Carry-forward A pending)
- Strong-tier promotion rationale: pattern is direct subject of Item 6 + Item 7 codification at PHASE2C_13 implementation arc; Item 6 codification is operating-rule-articulating (vs observation-only); meets mitigation-strategy-specifiable necessary condition by construction
- Strong-tier promotion blocker: Item 6 + Item 7 § seals at implementation arc must complete before promotion; cross-cycle accumulation evidence at §4.1.1 backfill sparse at non-PHASE2C_12 cycles

**Candidate 3 — M7 register-class-compromise (same-agent fresh-register full-file pass) cross-cycle pattern**
- Current tier (per METHODOLOGY_NOTES §17 codification): Strong-tier-class disposition implicit at §17 sub-rule 4 codification (recursive operating rule); cross-cycle empirical operation pattern observation-only at scoping cycle register
- Cross-cycle accumulation: 2 instances cross-cycle (PHASE2C_12 sub-spec drafting + scoping cycle); §A1 instance #1 at PHASE2C_13 sub-spec drafting cycle entry register-class-similar
- Strong-tier promotion rationale: §17 sub-rule 4 already codified at Strong-tier-class register; cross-cycle empirical pattern observation may codify as additional sub-rule or § entry
- Strong-tier promotion blocker: 2-instance cross-cycle accumulation thin; promotion candidate is observation pattern (vs new operating rule); fold-in to existing §17 likely over new-§ creation

**Candidate 4 — Q10/M6-F2 healthy reasoned-adjudication cycle pattern**
- Current tier: not codified; cross-cycle observation only
- Cross-cycle accumulation: 2 PHASE2C_12 instances + cumulative across cycles per CLAUDE.md PHASE2C_12 SEAL entry
- Strong-tier promotion rationale: pattern reflects substantive reviewer divergence → per-ground substantive verify → adjudicated convergence at Charlie register (NOT bulk-accept)
- Strong-tier promotion blocker: codification overlaps with [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) memory; redundant codification at METHODOLOGY_NOTES register if memory already binds; promotion is not register-class-distinct from existing memory binding

**Candidate enumeration summary:** 4 candidates surfaced; promotion to Strong-tier requires (C-2) bar criteria check + Charlie register adjudication at promotion register-event boundary (post-PHASE2C_13 implementation arc § seal for each candidate). PHASE2C_13 sub-spec scope = enumeration only; promotion executions OUT-OF-SCOPE per scoping decision §1.4 + §6.6 (C-2) binding.

#### §4.3.2 (C-2) Strong-tier bar codification (sub-deliverable)

Per scoping decision §6.6 (C-2) advisor Observation 4 binding + V#10 EXISTING tier framework refinement framing:

**Strong-tier bar criteria (refinement of EXISTING METHODOLOGY_NOTES §13-§20 tier framework, AND-conjoined necessary conditions; sub-spec authors criteria + Charlie register adjudicates final bar values at sub-spec SEAL boundary):**

**Criterion 1 — Minimum cross-cycle instance count threshold (necessary)**
- Strong-tier promotion requires ≥10 instances accumulated across ≥3 PHASE2C cycles (cycle-class register-class-distinct from sub-cycle-phase register; e.g., PHASE2C_12 sub-spec drafting + Step 1 + Step 2 + closeout = 1 cycle for cross-cycle counting purposes)
- Rationale anchor: Medium-tier at METHODOLOGY_NOTES §18 ships at 4/4 PHASE2C interpretive arc closeout saturation per §18 codification; Medium tier requires saturation evidence. Strong tier at §20 ships at single binding operating rule register (e.g., pre-result lockpoint mis-specification exception path). Bar at "≥10 instances + ≥3 cycles" sets register-class-distinct threshold reflecting cross-cycle operating-rule-articulating pattern beyond observation saturation
- Provisional threshold values (Charlie register adjudicates final at SEAL): instance count 10 (anchor: PHASE2C_12 §19 = 10 single-cycle baseline; cross-cycle pattern at 10+ implies saturation across cycles); cycle count 3 (anchor: minimum cross-cycle for "pattern" vs "single-cycle anomaly" register-class distinction)

**Criterion 2 — Mitigation-strategy-specifiable as necessary condition (necessary)**
- Strong-tier promotion requires concrete operating rule articulation (NOT observation-only framing). Operating rule must specify: WHEN the rule applies (trigger context); WHAT the rule prescribes (application checklist); HOW to recognize rule violation (failure-mode signal)
- Rationale anchor: METHODOLOGY_NOTES §20 codification of pre-result lockpoint mis-specification exception path is concrete operating rule. METHODOLOGY_NOTES §19 codification of §19 finding pattern is observation-only at Weak tier register-class. Distinction at operating-rule-articulating vs observation-only register-class is the bar criterion 2 anchor
- Application: candidate observation that has cross-cycle saturation but NO operating rule articulation = Medium tier (per §18 register-class precedent), NOT Strong tier

**Criterion 3 — Cross-cycle register-class consistency requirement (necessary)**
- Strong-tier promotion requires register-class consistency at observation pattern across cycles (e.g., §19 spec-vs-empirical-reality consistently surfaces at sub-spec drafting register vs. inconsistent register-class assignment across cycles). Cross-cycle register-class consistency anchors the operating-rule-articulating disposition (criterion 2)
- Rationale anchor: Item 6 §9.0c register-class taxonomy 3-class sub-rule explicitly requires register-class-distinct counting + register-class-distinct mitigation; same discipline applies to Strong-tier candidate evaluation
- Application: candidate with 20 cumulative cross-cycle instances but 10 at sub-spec drafting register + 5 at authorization register + 5 at reviewer register may NOT satisfy criterion 3 (heterogeneous register-class distribution); single-register-class concentration (e.g., 18 at sub-spec drafting + 2 at others) satisfies criterion 3

**Criterion 4 — Exit criteria from Weak/Medium tier register (necessary)**
- Strong-tier promotion requires the candidate observation has been at Weak or Medium tier for ≥1 prior consolidation cycle (NOT direct Weak→Strong promotion at single cycle). Maturation through tier hierarchy ensures cross-cycle pattern stability
- Rationale anchor: METHODOLOGY_NOTES §13-§20 tier hierarchy reflects maturation register; bypass of intermediate tier corrupts maturation evidence at promotion register
- Application: candidate first observed at PHASE2C_13 cycle (e.g., Item 7 anti-meta-pattern discipline) cannot promote to Strong tier at PHASE2C_13; candidate must enter at Weak tier observation-only initially + accumulate cross-cycle evidence + promote to Medium at later cycle + eventually Strong if criteria 1-3 met

**Strong-tier bar AND-conjunction:** ALL FOUR criteria must hold for Strong-tier promotion. Single criterion failure = candidate stays at Medium tier (or Weak tier if criterion 2 fails — operating rule articulation absent).

#### §4.3.3 §2.1-§2.7 provisional tier disposition re-check against codified bar (per Task 13 Step 13.4)

Re-checking §2.1-§2.7 Items 1-7 provisional tier dispositions against §4.3.2 bar codification:

| Item | §2.x provisional | Criteria check | Final tier (this sub-spec) |
| ---- | --------------- | -------------- | -------------------------- |
| Item 1 (§2.1) | Medium tier | C1: 4 PHASE2C_12 instances (single-cycle); cross-cycle accumulation pending Carry-forward A backfill | Medium tier (cross-cycle accumulation pending; promotion path to Strong contingent on backfill at implementation arc evidence basis) |
| Item 2 (§2.2) | Strong candidate | C1: 4 PHASE2C_12 instances at single-cycle; cross-cycle pending. C2: operating rule articulating (framework parameter audit) ✓. C3: pending backfill. C4: 0 prior consolidation cycle (this is first codification) — FAILS C4 | Medium tier (FAILS C4 maturation criterion at first codification cycle); promotion path to Strong contingent on PHASE2C_14+ cross-cycle accumulation + maturation cycle |
| Item 3 (§2.3) | Medium tier | C1: 1 PHASE2C_12 instance only (sparse); cross-cycle very thin | Weak tier observation-only with cross-cycle-pending status note (sparse evidence at PHASE2C_12 single-instance register fails C1 ≥10 instances threshold; aligns with METHODOLOGY_NOTES §19 Weak-tier register precedent for thin-evidence-basis observation patterns) |
| Item 4 (§2.4) | Medium-to-Strong | C1: pending; C2: operating rule articulating (executable verification function) ✓. C3: Item 4 register-class likely fold-in to Item 2 § scope per §5 fold-in 4-criteria; promotion via Item 2 § path | Medium tier candidate via Item 2 fold-in path; final disposition at §5 |
| Item 5 (§2.5) | Strong candidate | C1: 1 PHASE2C_12 instance; cross-cycle reviewer over-interpretation pattern likely accumulates per scoping decision §10.6. C4: 0 prior cycle — FAILS C4 | Medium tier (FAILS C4); promotion path to Strong contingent on PHASE2C_14+ |
| Item 6 (§2.6) | Strong candidate | C1: 8 PHASE2C_12 instances (single-cycle baseline); cross-cycle pending. C2: operating rule articulating (continuous-vs-batch + 3-class taxonomy) ✓. C3: 3-class taxonomy already operationalized; cross-cycle pending. C4: 0 prior cycle — FAILS C4 | Medium tier (FAILS C4); promotion path to Strong contingent on PHASE2C_14+ |
| Item 7 (§2.7) | Weak observation-only | C1: 1 PHASE2C_13 instance (initial); cross-cycle pending. C4: 0 prior cycle — FAILS C4 | Weak tier observation-only (per §2.7 initial disposition; bar criteria confirm Weak placement); promotion path Weak→Medium at PHASE2C_14 + Medium→Strong at PHASE2C_15+ |

**Re-check summary:** All 7 Items downgrade to Medium tier or lower at PHASE2C_13 sub-spec register (none meet Criterion 4 maturation requirement at first codification cycle). Strong-tier promotions OUT-OF-SCOPE for PHASE2C_13 per scoping decision + bar criterion 4. Promotion path established for each Item via PHASE2C_14+ cross-cycle accumulation evidence at Carry-forward A § seal feeding promotion candidate review at later consolidation cycle.

#### §4.3.4 Strong-tier promotion explicit sub-spec scope guardrail

Per scoping decision §1.4 + Carry-forward C scope binding: PHASE2C_13 sub-spec defines Strong-tier promotion CRITERIA only; does NOT promote any candidate to Strong-tier inside the sub-spec. Promotion executions are OUT-OF-SCOPE at PHASE2C_13 register entirely.

**No Strong-tier promotions authorized AT PHASE2C_13 cycle register (binding; cycle-class-specific scope):** §4.3.3 re-check pass empirically validates ALL 7 Items + sub-rule + Carry-forwards downgrade to Medium tier or lower per criterion 4 maturation requirement failure (every candidate has 0 prior consolidation cycle at PHASE2C_13 first codification register); criterion 4 failure by construction at first codification cycle precludes any Strong-tier promotion at PHASE2C_13 implementation arc § seal register.

**Implementation arc § seal scope for bar criteria checks (PHASE2C_13 cycle scope only):** at each PHASE2C_13 implementation arc § seal authoring (Items 1-7 + sub-rule + Carry-forwards A/B/C), record bar criteria check outcome at register-precision (which criteria pass / fail; cross-cycle accumulation pending state); RECORD ONLY — no promotion execution authorized at PHASE2C_13 register. Promotion register-event boundary fires at PHASE2C_14+ consolidation cycle if cross-cycle accumulation evidence + maturation cycle satisfies all 4 criteria for any candidate.

**Out-of-scope register binding (cycle-class-specific):** Strong-tier promotion executions register-class-distinct from PHASE2C_13 sub-spec drafting cycle SEAL boundary AND from PHASE2C_13 implementation arc § seal boundaries.

**Anti-momentum-binding cross-cycle scope preservation (per F3 patch — cycle-class-distinct authorization preservation):** the no-Strong-tier-promotions binding above scopes EXPLICITLY to PHASE2C_13 cycle register only. PHASE2C_14+ consolidation cycle register-class-distinct authorization decision is NOT pre-bound at PHASE2C_13 register — at PHASE2C_14 cycle entry, candidates codified at PHASE2C_13 satisfy criterion 4 (PHASE2C_13 = prior consolidation cycle for cross-cycle counting purposes); PHASE2C_14 may authorize Strong-tier promotion for any candidate satisfying all 4 bar criteria 1-4 AND-conjoined per Charlie register adjudication at PHASE2C_14 promotion register-event boundary. Promotion authorization at future cycles is register-class-distinct decision per cycle scoping cycle adjudication; PHASE2C_13 cycle binding does NOT carry forward as blanket future-cycle bind. Anti-momentum-binding strict reading: PHASE2C_13 cycle binding is cycle-class-specific register-class boundary, NOT cross-cycle authorization sealing. Anti-pre-naming preserved (no PHASE2C_14 scope pre-commitment at PHASE2C_13 register; only authorization-class boundary preservation at register-class-distinct cross-cycle decision register).

#### §4.3.5 EXISTING tier framework refinement framing (NOT new framework creation; per V#10 anchor)

V#10 verification at scoping decision register: Weak/Medium/Strong tier framework already codified at METHODOLOGY_NOTES §13-§20:
- Medium tier register at §18 line 2349 (per scoping decision V#10 verification)
- Weak tier register at §19 line 2481 (per V#10 verification)
- Strong tier register at §20 line 2551 (per V#10 verification)

Strong-tier bar codification at §4.3.2 = REFINEMENT of EXISTING tier framework (specifying explicit bar criteria for tier hierarchy that already exists at §13-§20). Bar codification at PHASE2C_13 implementation arc appends to existing §20 OR creates new sub-section under §20 register OR creates new § entry that references §13-§20 + adds bar criteria 1-4 enumeration. Final § slot disposition at §5 per fold-in 4-criteria check.

**§20 sub-§ host-slot accommodation framing (per F5 patch):** §20 host slot currently codifies "Path A.2 register-event boundary discipline" content per V#10 verification at scoping cycle. Carry-forward C fold-in to §20 as appendix-style sub-§ "Strong-tier promotion bar criteria" introduces register-class-distinct sub-content at same § slot. Implementation arc Step 9 § seal authoring SHOULD codify §20 internal sub-§ structure to accommodate both register-class-distinct sub-contents:
- **§20.1 (existing register-class):** Path A.2 register-event boundary discipline content (preserved invariant per V#10 anchor binding)
- **§20.2 (new appendix-style register-class):** Strong-tier promotion bar criteria 1-4 + (C-1) candidates enumeration framework + (C-2) bar codification reference

§20 host-slot accommodation register-class precision: BOTH sub-contents at §20 are register-class-coherent under the parent § principle "Strong tier register" (Path A.2 trigger at register-event boundary register; bar criteria for tier-class promotion register). Sub-§ structure at §20 internal preserves register-class distinction at sub-§ register; cross-reference between §20.1 + §20.2 at Application checklist register if appropriate. Final §20 sub-§ structure authored at implementation arc Step 9 § seal register per fold-in 4-criteria check + register-class accommodation discipline.

**Anti-pattern explicit rejection:** Sub-spec does NOT create new tier framework. Tier hierarchy at §13-§20 stays invariant. Bar codification adds criteria for promotion; does NOT replace tier definitions or rename tiers.

---

## §5 Implementation arc Steps 1-N specification

This section specifies the PHASE2C_13 implementation arc Step structure: Items 1-7 + §9.0c register-class taxonomy 3-class sub-rule + Carry-forwards A/B/C → `docs/discipline/METHODOLOGY_NOTES.md` § slot mapping; per-§ seal pattern per PHASE2C_10 precedent; Step count + sequencing dependency with Carry-forward A → Carry-forward B sequencing per §4.2.4 binding. Implementation arc fires at fresh session post-PHASE2C_13 sub-spec SEAL per pacing discipline (PHASE2C_10/11/12 precedent); each Step ships METHODOLOGY_NOTES § content + per-§ seal commit + CLAUDE.md Phase Marker advance per [`feedback_claude_md_freshness.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md).

### §5.1 Items 1-7 + sub-rule + Carry-forwards A/B/C → METHODOLOGY_NOTES § slot mapping (provisional)

Per §2 + §3 + §4 provisional slot specifications + scoping decision §5.4 + §6.7 binding + PHASE2C_10 precedent at §16-§20 + §3.5/§3.6 fold-in. Provisional mapping table; final per-candidate disposition at §5.4 4-criteria check.

| Codification candidate | Sub-spec § anchor | Provisional METHODOLOGY_NOTES § slot | New-§ vs fold-in candidacy |
| ---------------------- | ----------------- | ------------------------------------ | -------------------------- |
| Item 1 — Fire-prep precondition checklist | §2.1 | new §21 | new-§ candidate |
| Item 2 — Framework parameter pre-lock | §2.2 | new §22 | new-§ candidate |
| Item 3 — Step 7/8 contract standardization | §2.3 | new §23 | new-§ candidate |
| Item 4 — LOCKED items → executable verification function | §2.4 | new §24 OR fold-in to §22 (Item 2) | fold-in candidate (topical coupling with Item 2) |
| Item 5 — Reviewer over-interpretation prevention | §2.5 | new §25 | new-§ candidate |
| Item 6 — §9.0c instance density + register-class taxonomy | §2.6 | new §26 | new-§ candidate |
| Item 7 — Real-time §9.0c instance handling (anti-meta-pattern) | §2.7 | new §27 OR fold-in to §26 (Item 6) | fold-in candidate (parent-recursive coupling with Item 6) |
| §9.0c register-class taxonomy 3-class sub-rule | §3 | fold-in to §26 (Item 6) OR cross-referenced sub-§ under §27 (Item 7) | fold-in candidate (operationalization detail of Item 6 principle) |
| Carry-forward A — Cycle-complexity scaling diagnosis | §4.1 | new §28 | new-§ candidate |
| Carry-forward B — Framework architectural refactor evaluation | §4.2 | new §29 | new-§ candidate (meta-evaluation register; weak topical fit to existing §§) |
| Carry-forward C — Strong-tier promotion candidates + bar codification | §4.3 | append to §20 (Strong tier) OR new §30 | fold-in candidate (refinement of EXISTING §13-§20 tier framework per V#10) |

**Total candidates:** 11 codification candidates (7 Items + 1 sub-rule + 3 Carry-forwards). **Provisional § count after fold-in 4-criteria check at §5.4:** estimated 7-9 new §§ + 2-4 fold-ins.

### §5.2 Fold-in 4-criteria block (per Q-S30 Obs 4 Charlie auth APPROVED)

A codification candidate is fold-in eligible iff ALL FOUR criteria below hold (AND-conjunction; strict reading). Single criterion failure → new-§ register. Per Q-S30 Obs 4 Charlie auth APPROVED + meta-plan Task 14 Step 14.1 patch.

**Criterion (a) — Topical match to existing § scope.** Candidate's principle / domain aligns with existing METHODOLOGY_NOTES § parent principle (e.g., PHASE2C_10 §3.5 pre-fire audit pattern aligned topically with §16 anchor-prose-access discipline as failure-mode signal sub-class). Topical match assessed at parent § principle register, NOT at trigger context register (different trigger contexts may share principle register).

**Criterion (b) — Sub-§ depth appropriate (NOT diluting parent § principle).** Candidate codifies as natural sub-§ within parent § structure (typically Failure-mode signal slot or short watch-for paragraph or Application checklist sub-rule item); does NOT require its own 4-subsection (Principle / Trigger context / Application checklist / Failure-mode signal) full structure. If candidate requires 4-subsection authoring at register-precision, sub-§ depth is inappropriate → new-§ register.

**Criterion (c) — Cross-cycle accumulation insufficient for new-§ register.** Candidate has limited cross-cycle instance accumulation (typically Weak tier observation-only at codification register; 1-2 cycle instances). New-§ at full 4-subsection structure would be over-codification at the candidate's evidence basis register. Cross-cycle accumulation threshold for new-§ candidacy: ≥3 cycles with substantive instance density per cycle (anchor: PHASE2C_10 §16/§17/§18/§19 each shipped as new-§ at single-cycle register based on operating rule articulation strength, NOT cross-cycle accumulation alone — criterion (c) interacts with criterion (b) at sub-§ depth assessment).

**Criterion (d) — Item 7 boundary clause compliance.** Fold-in candidate at METHODOLOGY_NOTES § slot must NOT collide cross-cycle codification scope (e.g., 3-class taxonomy invariant content; tier hierarchy invariant content) with cycle-internal operational state (e.g., per-cycle running log; per-cycle instance counts). Mirrors §A1/§A2 vs §3 placement decision at sub-spec deliverable register (per Q-S29 §9.0c+§19 log mechanics specification): fold-in candidates inherit cross-cycle codification scope from parent §; cycle-internal state is register-class-distinct register at appendix slot. **Q-S27a interaction note (preserves SEAL pre-fire deferral):** criterion (d) breadth of "Item 7 boundary clause" reference depends on Q-S27a resolution at sub-spec SEAL — Reading (i) strict §9.0c-only binding constrains (d) check to §9.0c taxonomy + counting invariance; Readings (ii)/(iii) broaden (d) check to §19 + future-pattern boundary preservation. Sub-spec authoring at §5.4 per-candidate (d) check operates at lower-bound Reading (i) register (binding regardless of Q-S27a outcome); broader (ii)/(iii) bindings layer additionally if Charlie register endorses at Q-S27a fire boundary.

**AND-conjunction strict reading:** ALL FOUR criteria must hold for fold-in. If criterion (a) holds but (b) fails (substantive 4-subsection content required), candidate ships as new-§. If (a)+(b)+(c) hold but (d) fails (cross-cycle vs cycle-internal collision risk at fold-in target slot), candidate ships as new-§ at register-class-distinct slot.

### §5.3 Worked example — PHASE2C_10 §3.5/§3.6 fold-in to §16 ### Failure-mode signal

Per PHASE2C_10 Step 2 §3.5/§3.6 fold-in commit `8ed1b34` (CLAUDE.md PHASE2C_10 SEAL entry register; per scoping decision §6.7 reference). Worked example demonstrating all 4 criteria holding AND-conjoined → fold-in disposition:

- **(a) Topical match:** §3.5 pre-fire audit pattern + §3.6 self-first-then-reviewer adjudication discipline both align with §16 anchor-prose-access discipline at parent principle register (anchor-prose-access discipline includes pre-fire audit + reviewer-engagement adjudication as failure-mode signal sub-class). ✓
- **(b) Sub-§ depth:** Both candidates codified as short watch-for paragraphs (~6-10 lines each) under §16 ### Failure-mode signal slot; NOT requiring 4-subsection full structure. ✓
- **(c) Cross-cycle accumulation:** Each candidate had 1 PHASE2C-cycle instance at codification time (PHASE2C_9 for §3.5; PHASE2C_10 scoping cycle for §3.6); insufficient for new-§ at full 4-subsection register; observation-only Weak tier appropriate at fold-in slot. ✓
- **(d) Item 7 boundary clause compliance:** §16 host slot citing §11 + §14 as parent disciplines via cross-reference register; no cross-cycle codification scope vs cycle-internal state collision at fold-in target. Per PHASE2C_10 Step 2 §3.5/§3.6 commit `8ed1b34` register, fold-in shipped as direct in-place append (no temp working draft per ChatGPT execution plan for Weak-tier 1-instance lighter operational footprint). ✓

ALL 4 criteria hold AND-conjoined → fold-in disposition (NOT new-§) per PHASE2C_10 precedent.

### §5.4 Per-candidate fold-in 4-criteria check

Application of §5.2 4-criteria to each candidate at §5.1 mapping table. Per-candidate disposition reasons specified at register-precision; final dispositions feed §5.5 Step count + sequencing.

| Candidate | (a) Topical match | (b) Sub-§ depth | (c) Cross-cycle accumulation | (d) Item 7 boundary clause | Disposition |
| --------- | ----------------- | --------------- | ---------------------------- | -------------------------- | ----------- |
| Item 1 (§2.1) | weak fit to existing §13-§20 (fire-prep discipline distinct from anchor-prose-access / procedural-confirmation registers) | requires 4-subsection (Principle + Trigger + Application checklist + Failure-mode signal substantive content per §2.1 codification mechanism) | 4 PHASE2C_12 instances at single-cycle register; cross-cycle backfill pending §4.1.1 | new-§ register avoids cross-cycle vs cycle-internal collision concern | **new §21** |
| Item 2 (§2.2) | weak fit to existing §§ (framework parameter audit at sub-spec terminus distinct register) | requires 4-subsection (handoff-noise propagation prevention substantive) | 4 PHASE2C_12 §19 instances; cross-cycle pending | new-§ register | **new §22** |
| Item 3 (§2.3) | weak fit (inter-step contract standardization distinct register) | requires 4-subsection | 1 PHASE2C_12 instance (sparse) — could argue (c) holds, but (a)+(b) fail | new-§ register | **new §23** |
| Item 4 (§2.4) | strong fit to §22 (Item 2) — Q-LOCKED executable verification function is operationalization of Item 2 framework parameter pre-lock at runtime register vs sub-spec terminus register ✓ | sub-§ at Application checklist sub-rule item or Trigger context sub-paragraph appropriate ✓ | 1 concrete pattern reference (`_resolve_n_eff_set()`) + indirect via Item 2 §19 instances ✓ | §22 host slot = framework parameter cross-cycle codification scope; Item 4 fold-in at Application checklist sub-rule preserves cross-cycle scope (no cycle-internal state collision) ✓ | **fold-in to §22 at Application checklist sub-rule item or Trigger context sub-paragraph** (parent-operationalization coupling) |
| Item 5 (§2.5) | weak fit to §16 anchor-prose-access discipline (reviewer over-interpretation prevention is reviewer-register but topical register distinct from anchor-prose-access) | requires 4-subsection (register-class declaration block specification + reviewer prompt template) | 1 PHASE2C_12 instance + cross-cycle pattern likely accumulates | new-§ register | **new §25** |
| Item 6 (§2.6) | weak fit (§9.0c instance density continuous-vs-batch + 3-class taxonomy distinct register from existing §§) | requires 4-subsection (continuous-vs-batch + taxonomy preservation substantive content) | 8 PHASE2C_12 instances + cross-cycle pending | new-§ register | **new §26** |
| Item 7 (§2.7) | strong fit to §26 (Item 6) — Item 7 is recursive operationalization of Item 6's continuous-vs-batch choice ✓ | could codify as sub-§ under §26 OR new-§ at adjacent slot — sub-§ depth borderline (Item 7 boundary clause + bilingual anchor + Reading (i)/(ii)/(iii) scope question + Application checklist 6 items = substantive content closer to 4-subsection register than short sub-§) ✗ — **Q-S27a-resolution stability note (per F6 patch):** even with Reading scope question content collapsed to specific Reading at Q-S27a SEAL adjudication outcome, Item 7 codification still requires 4-subsection content body (boundary clause prose + operating discipline at cycle-internal + Application checklist 6 items + bilingual concept anchor + cross-references); 4-subsection content persists post-Q-S27a-resolution → criterion (b) failure stable across Reading (i)/(ii)/(iii) outcomes → new-§ disposition stable post-Q-S27a-resolution | 1 PHASE2C_13 cycle instance — (c) holds | (d) check load-bearing: Item 7 codification IS the boundary clause discipline; fold-in to §26 risks register-class collision (Item 6 = §9.0c discipline cross-cycle invariant; Item 7 = recursion-under-Item-6 register class). New-§ at §27 adjacent to §26 preserves register-class precision | **new §27** (adjacent to §26; criterion (b) failure decisive; Q-S27a-resolution stable) |
| §9.0c sub-rule (§3) | strong fit to §26 (Item 6) — sub-rule IS operationalization detail of Item 6 principle ✓ | sub-§ depth appropriate (taxonomy enumeration + register-class-distinct mitigation strategies + cross-cycle comparability requirement at Application checklist sub-rule items 1-4 of §26 register) ✓ | n/a — sub-rule operationalizes Item 6 evidence basis ✓ | (d) check: §3 cross-cycle codification scope (3-class taxonomy invariant) folds into §26 cross-cycle scope register cleanly ✓ | **fold-in to §26 at Application checklist sub-rule items 1-4 + cross-reference** (operationalization-detail coupling) |
| Carry-forward A (§4.1) | weak fit (cycle-complexity scaling diagnosis distinct register from existing §§) | requires 4-subsection (metric set + backfill table + forward observation framing + threshold values substantive) | n/a — first cycle codification | new-§ register | **new §28** |
| Carry-forward B (§4.2) | weak fit (framework architectural refactor evaluation register; meta-evaluation register-class) | requires 4-subsection (evaluation methodology + alternative pattern enumeration + criteria + disposition substantive) | n/a — first cycle codification; meta-evaluation register | new-§ register; sequencing dependency on Carry-forward A § (per §4.2.4) | **new §29** (ships after §28 per sequencing) |
| Carry-forward C (§4.3) | strong fit to existing §13-§20 tier framework — bar codification IS refinement of existing tier hierarchy per V#10 ✓ | appendix-style sub-§ under existing §20 IS sub-§ depth appropriate ✓ (criterion (b) satisfied because codification ships as sub-§ within existing §20 host slot, NOT new full 4-subsection §; bar criteria 1-4 + 4-candidate enumeration as appendix prose under §20 "Strong tier" host preserves §13-§20 tier framework invariance per V#10 — refinement register, NOT parallel-framework creation; **§20 sub-§ structure framing per F5 patch:** §20.1 = existing Path A.2 register-event boundary discipline content invariant; §20.2 = new appendix-style "Strong-tier promotion bar criteria" sub-§; both register-class-coherent under parent § principle "Strong tier register"; sub-§ structure at §20 internal preserves register-class distinction at implementation arc Step 9 § seal authoring) | n/a — first codification of bar criteria | (d) check: tier framework cross-cycle invariant content; bar codification preserves invariant; §A1/§A2-style cycle-internal state register-class-distinct (kept at sub-spec body §4.3 not METHODOLOGY_NOTES) — boundary preserved ✓ | **fold-in to §20 as appendix-style sub-§ "Strong-tier promotion bar criteria" at §20.2 register** (refinement-of-existing-tier-framework register per V#10 anchor; §20.2 sub-§ at §20 host slot register-class-cleaner than new-§ creating parallel tier framework; §20.1 existing content register-class-distinct preservation) |

**Per-candidate disposition summary:**
- **New-§§ at codification:** 8 new §§ — §21 (Item 1) + §22 (Item 2) + §23 (Item 3) + §25 (Item 5) + §26 (Item 6) + §27 (Item 7) + §28 (Carry-forward A) + §29 (Carry-forward B). Total: 8 new §§.
- **Fold-ins at codification:** 3 fold-ins — Item 4 → §22 Application checklist sub-rule; §9.0c sub-rule (§3) → §26 Application checklist sub-rule items 1-4 + cross-reference; Carry-forward C → §20 appendix-style sub-§ "Strong-tier promotion bar criteria".
- **Total METHODOLOGY_NOTES code-site touches:** 8 new-§ appends + 3 fold-in edits = 11 code-site touches (matches 11-candidate count from §5.1).

Final § slot disposition + per-§ title authored at implementation arc Step entry register per Step ordering at §5.6.

### §5.5 Per-§ seal pattern (PHASE2C_10 precedent)

Per PHASE2C_10 implementation arc precedent at §16/§17/§18/§19/§20 + §3.5/§3.6 fold-in (commits `7959140` / `3eff56a` / `2ac95ab` / `0c6831f` / `8ed1b34` per CLAUDE.md PHASE2C_10 SEAL entry register), each new METHODOLOGY_NOTES § ships at implementation arc with:

1. **Working draft authoring** — temp file at `docs/phase2c/PHASE2C_13_STEP<N>_S<§>_WORKING_DRAFT.md` (mirrors PHASE2C_10 temp file naming) OR direct in-place append for Weak-tier 1-instance lighter operational footprint candidates per PHASE2C_10 §3.5/§3.6 register precedent
2. **Reviewer pass cycle** — advisor full-prose-access pass + ChatGPT structural overlay; Codex skip per scoping decision §5.3 + [`feedback_codex_review_scope.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md). Per-fix adjudication discipline per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) — no bulk-accept
3. **Full-file prose-access pass per §17 sub-rule 4** — recursive operating rule fires at sealed-commit register; section-targeted patches do NOT preclude need for full-file final pass at register-precision
4. **§ seal commit** — single-atomic-commit per METHODOLOGY_NOTES §0.4 discipline (METHODOLOGY_NOTES.md edit + temp file rm in single atomic commit if temp file pattern; direct edit + commit if direct in-place append pattern)
5. **CLAUDE.md Phase Marker advance** — Phase Marker advance at next CLAUDE.md edit cycle per [`feedback_claude_md_freshness.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md); typically bundled with § seal commit OR following commit per per-§ seal pattern at PHASE2C_10 register

### §5.6 Implementation arc Step count + sequencing

**Step enumeration:** 9 content Steps covering 8 new-§ appends + 3 fold-in edits = 11 code-site touches (Steps 2 and 5 each bundle a new-§ with a fold-in per topical coupling at §5.4 disposition; remaining 7 content Steps each ship one new-§ or one fold-in) + Step 10 final full-file prose-access pass + Step 11 audit + Step 12 closeout deliverable seal. Total: 12 Steps at PHASE2C_13 implementation arc.

**Step sequencing dependency (binding):**

- **Step 1 — Item 1 §21 codification** (fire-prep precondition checklist; foundational discipline; no dependencies)
- **Step 2 — Item 2 §22 codification + Item 4 fold-in** (framework parameter pre-lock + executable verification function; Item 4 fold-in at §22 Application checklist register; topical coupling per §5.4 disposition)
- **Step 3 — Item 3 §23 codification** (Step 7/8 contract standardization; cross-references Step 1 fire-prep at Application checklist item 5 per §2.3 register)
- **Step 4 — Item 5 §25 codification** (reviewer over-interpretation prevention; cross-references §16 anchor-prose-access discipline at fold-in references but ships as new-§ per §5.4 disposition)
- **Step 5 — Item 6 §26 codification + §9.0c sub-rule fold-in** (§9.0c instance density + 3-class taxonomy parent + sub-rule operationalization detail at Application checklist register)
- **Step 6 — Item 7 §27 codification** (anti-meta-pattern discipline + boundary clause; ships AFTER §26 per parent-recursive coupling order; cross-references §26 Application checklist sub-rule)
- **Step 7 — Carry-forward A §28 codification** (cycle-complexity scaling diagnosis; metric set + backfill empirical fire — backfill table at §4.1.1 PHASE2C_8.1/9/10/11 cells filled with empirical reads at this Step register; sub-spec scope binds methodology framework only per §4.1.1 binding)
- **Step 8 — Carry-forward B §29 codification** (framework architectural refactor evaluation; ships AFTER §28 per §4.2.4 sequencing dependency — Carry-forward A § provides metric data feeding Carry-forward B evaluation criteria (i) + (iv); evaluation outcome disposition: refactor-needed / sustainable-through-PHASE2C_15 / inconclusive)
- **Step 9 — Carry-forward C fold-in to §20** (Strong-tier promotion bar criteria appendix-style sub-§; ships AFTER Steps 1-6 per criterion 4 maturation requirement at §4.3.3 — bar criteria operate at refinement register of EXISTING §13-§20 tier framework; sub-spec §4.3.3 re-check pass already validates ALL 7 Items downgrade to Medium tier or lower at PHASE2C_13 cycle so no Strong-tier promotion executions at this Step)
- **Step 10 — METHODOLOGY_NOTES.md final full-file prose-access pass** (per §17 sub-rule 4 recursive operating rule fired at cycle-terminus register after all § seals + fold-ins complete; surfaces any cross-§ register-class drift at final register before closeout)
- **Step 11 — `_step_count_check_` audit** (V#-style audit confirming 11 code-site touches landed cleanly; cross-references §5.4 disposition register for empirical cross-check)
- **Step 12 — Closeout deliverable seal** (`docs/closeout/PHASE2C_13_RESULTS.md` per §6 specification; tag `phase2c-13-methodology-consolidation-v1` at deliverable seal commit per Path A.2 register-event boundary discipline; Phase Marker advance to PHASE2C_13 SEALED at this Step register)

**Sequencing-dependency anchor table:**

| Step | Dependency | Rationale |
| ---- | ---------- | --------- |
| 1 | none | foundational §21 entry |
| 2 | Step 1 | Item 4 fold-in to §22 builds on Item 2 register; topical coupling |
| 3 | Step 1 | §23 cross-references Step 1 fire-prep checklist at Application item 5 |
| 4 | none (parallel-eligible with Steps 2-3) | §25 register-class-distinct from §22-§24 cluster |
| 5 | none (parallel-eligible) | §26 + §9.0c sub-rule fold-in cluster register-class-distinct |
| 6 | Step 5 | §27 ships AFTER §26 per parent-recursive coupling |
| 7 | Steps 1-6 | §28 backfill empirical fire requires PHASE2C_13 cycle activity log accumulated through Steps 1-6 |
| 8 | Step 7 | §29 ships AFTER §28 per §4.2.4 dependency (criteria (i)+(iv) data) |
| 9 | Steps 1-6 | Carry-forward C re-check pass anchors validated across §21-§27 codifications |
| 10 | Steps 1-9 | full-file prose pass at cycle-terminus |
| 11 | Step 10 | audit count after all touches landed |
| 12 | Step 11 | closeout deliverable seal at terminus |

**Anti-pre-naming preserved at this specification:** Step ordering authored at register-precision; specific commit count per Step + per-Step deliverable scope authored at implementation arc Step entry register per fresh session post-PHASE2C_13 sub-spec SEAL pacing discipline. PHASE2C_14 + PHASE2C_15 cycle scopes NOT pre-committed at this register.

**Estimated implementation arc commit count:** ~12-25 commits (1-2 commits per Step + reviewer pass cycle iterations + Phase Marker advances; PHASE2C_10 precedent: 5 § seals + ~8-12 patches across §16-§19 + §3.5/§3.6 fold-in cycles per CLAUDE.md PHASE2C_10 SEAL entry register).

---

## §6 Closeout deliverable scope specification

This section specifies the PHASE2C_13 closeout deliverable scope per scoping decision §6.7-§6.8 + PHASE2C_10/11/12 closeout precedent. Closeout deliverable ships at PHASE2C_13 implementation arc Step 12 (per §5.6 sequencing) as the cycle-arc-level SEAL artifact at register-event boundary discipline (Path A.2 per [METHODOLOGY_NOTES §20](../discipline/METHODOLOGY_NOTES.md) Trigger 1 anchor). Annotated tag at deliverable seal commit per Path A.2 register-event boundary discipline; tag fires SEPARATELY from Phase Marker advance commit (tag attaches to deliverable seal commit, NOT Phase Marker housekeeping commit) per PHASE2C_11 SEAL precedent at tag `phase2c-11-statistical-significance-v1` register.

### §6.1 Closeout deliverable filename + scope binding

**Filename:** `docs/closeout/PHASE2C_13_RESULTS.md` per PHASE2C_10/11/12 closeout naming precedent.

**Scope binding (per scoping decision §6.7 + PHASE2C_10 closeout precedent at [`docs/closeout/PHASE2C_10_METHODOLOGY_CONSOLIDATION_SIGNOFF.md`](../closeout/PHASE2C_10_METHODOLOGY_CONSOLIDATION_SIGNOFF.md)):**

- §1 Status / anchor commits / sealed-at register
- §2 PHASE2C_13 cycle scope summary (methodology consolidation arc per Step 9 §10.1 split scope decision)
- §3 Items 1-7 codification outcome (per § seal register at §21-§27 + Item 4 fold-in to §22; tier disposition outcomes per §4.3.3 re-check)
- §4 §9.0c register-class taxonomy 3-class sub-rule operationalization outcome (fold-in to §26 register)
- §5 Carry-forwards A/B/C operationalization outcome (Carry-forward A §28 metric tracking + backfill table empirical fire outcome; Carry-forward B §29 evaluation disposition refactor-needed/sustainable/inconclusive; Carry-forward C §20 fold-in Strong-tier promotion bar criteria + 7-Item re-check pass outcome at §4.3.3 register)
- §6 PHASE2C_13 cycle-internal §9.0c + §19 instance log final closure status (cumulative count register at cycle close + boundary compliance audit outcome per Item 7 boundary clause invariance check)
- §7 Cross-cycle methodology measurement metric reporting (Carry-forward A canonical metric set per §4.1.1: auth boundaries + commit count + §9.0c per-class + §19 + scoping cycle iteration count per §4.1.4)
- §8 Forbidden-phrase compliance audit (anti-pre-naming PHASE2C_14/15 scope leakage scan; tier promotion language scan)
- §9 Lockpoint compliance audit (sub-spec lockpoints preserved at implementation arc Step seals; no mid-arc reopening per scoping decision §1.4 constraint 7)
- §10 Carry-forwards to PHASE2C_14+ (cycle-class-distinct from sub-spec-cycle-internal carry-forward register; cumulative count register handoff for cross-cycle pattern accumulation)
- §11 Forward-pointer to PHASE2C_14 entry scoping cycle (anti-pre-naming preserved; PHASE2C_14 scope NOT pre-committed)

**Scope binding source:** scoping decision §6.7 closeout deliverable scope binding + PHASE2C_10/11/12 closeout precedent register; scoping decision §1.4 constraint 7 anti-momentum-binding extended interpretation prevents in-arc reopening of PHASE2C_12 disposition decisions; closeout deliverable does NOT re-adjudicate Step 8 Q22 LOCKED `inconclusive` mechanical disposition (canonical at primary anchor n_eff=197 per CLAUDE.md PHASE2C_12 SEAL register).

### §6.2 Tag naming convention

**Candidate tag name:** `phase2c-13-methodology-consolidation-v1` per PHASE2C_10 precedent at tag `phase2c-10-methodology-consolidation-v1` (matching naming pattern for methodology consolidation arcs).

**Tag attachment register-event boundary:** annotated tag attaches to closeout deliverable SEAL commit (Step 12 register), NOT Phase Marker advance commit. Per Path A.2 register-event boundary discipline at [METHODOLOGY_NOTES §20](../discipline/METHODOLOGY_NOTES.md) Trigger 1 anchor + PHASE2C_10 + PHASE2C_11 + PHASE2C_12 closeout SEAL register precedent (PHASE2C_11 tag at `5dba0df` closeout seal commit; PHASE2C_12 tag at `1989c85` closeout seal commit per CLAUDE.md SEAL entries verbatim).

**No tag at sub-spec drafting cycle SEAL** per PHASE2C_10/11/12 sub-spec drafting cycle SEAL precedent (Q-S27 sub-spec SEAL is sub-spec-cycle-level register-event boundary, NOT arc-level closeout register-event boundary; tags reserved for arc-level closeout SEAL).

### §6.3 Successor scoping cycle forward-pointer

**Per scoping decision §1.4 constraint 8:** PHASE2C_14 entry scoping cycle is a separate scoping cycle at fresh session post-PHASE2C_13 SEAL per pacing discipline (PHASE2C_10 + PHASE2C_11 + PHASE2C_12 precedent).

**Forward-pointer scope at PHASE2C_13 closeout §11 register:**

- PHASE2C_14 entry scoping cycle authorization required at fresh-session register-event boundary (anti-momentum-binding strict reading; carry-forward auth from PHASE2C_13 closeout SEAL is NOT implied)
- PHASE2C_14 cycle scope NOT pre-committed at PHASE2C_13 closeout register (anti-pre-naming preserved; per scoping decision §1.4 constraint 8 binding)
- Carry-forward register handoff at closeout §10: cumulative count register state (§9.0c per-class counts + §19 cumulative + Carry-forward A metric backfill outcome) hands off to PHASE2C_14 entry scoping cycle as input artifact for cross-cycle pattern accumulation evidence at later Strong-tier promotion review
- Step 9 §10.1 split scope ratification preserved: PHASE2C_14 = strategy refinement sub-spec drafting cycle anchor; PHASE2C_15 = first batch fire under refined methodology + strategy anchor; both deferred to their own scoping cycles per §1.4 constraint 8 binding

**Anti-pre-naming forbidden-phrase scan at closeout §11 register:** the closeout MUST NOT contain language pre-committing PHASE2C_14 scope decisions (e.g., "PHASE2C_14 will codify X" / "PHASE2C_14 fires Y batch"). Forbidden phrases enumerated at §8 forbidden-phrase compliance audit register; absence verified at closeout SEAL pre-fire by grep against canonical forbidden-phrase list.

---

## §7 Verification chain V#1-V#N (sub-spec SEAL pre-fire empirical verification)

This section enumerates V# anchors fired at sub-spec SEAL pre-fire register (Task 21 Step 21.5 per meta-plan; per METHODOLOGY_NOTES §17 sub-rule 4 recursive operating rule + scoping decision §7 V#-chain pattern). V#-chain enumeration at this register specifies WHAT to verify; empirical fire deferred to Task 21 Step 21.5 register-class-distinct from sub-spec authoring register. ALL V# anchors MUST be CLEAN before Task 22 Charlie SEAL auth boundary fires.

### §7.1 V# anchor enumeration

**V#1 — HEAD commit at sub-spec SEAL pre-fire**
- Anchor: `git rev-parse HEAD` at Task 21 Step 21.5 fire register
- Expected: HEAD at sub-spec drafting cycle SEAL bundle prep register (post-reviewer-pass-patches; pre-Charlie-SEAL-auth)
- Drift signal: HEAD divergence from PHASE2C_13 entry scoping cycle SEAL bundle anchor `6d76517` indicates intermediate commits during sub-spec drafting cycle (expected: 0 intermediate commits per Charlie auth (A) full pause selection at Q-S34; reviewer pass cycle Tasks 20-21 fire at session #3+)

**V#2 — Tag `phase2c-12-breadth-expansion-v1` at remote**
- Anchor: `git ls-remote --tags origin phase2c-12-breadth-expansion-v1`
- Expected: tag at PHASE2C_12 closeout seal commit `1989c85` per Path A.2 register-event boundary discipline
- Drift signal: tag absent at remote = §19 instance candidate (tag-push divergence; would re-open PHASE2C_13 entry §19 instance #1 register pattern); PHASE2C_13 entry session Q-S25 (A) closure already mitigated this at register-event boundary

**V#3 — Scoping decision §6 Items 1-7 binding scope verbatim reproduction at §2.1-§2.7**
- Anchor: grep verbatim quoted blocks at sub-spec §2.1-§2.7 against PHASE2C_12 closeout `docs/closeout/PHASE2C_12_RESULTS.md` §10.2 (Items 1-6) + scoping decision `docs/phase2c/PHASE2C_13_SCOPING_DECISION.md` §6.2 (Item 7) source registers
- Expected: VERBATIM match at quoted block register; sub-spec authoring register prose may paraphrase OUTSIDE quoted blocks
- Drift signal: any verbatim divergence within quoted blocks = §19 instance candidate (handoff-noise propagation pattern)

**V#4 — Scoping decision §6.3 §9.0c register-class taxonomy 3-class sub-rule verbatim reproduction at §3**
- Anchor: grep §3.1 3-class enumeration verbatim against scoping decision §6.3 binding scope; grep §3.2 register-class-distinct mitigation strategies verbatim binding language
- Expected: 3-class enumeration (sub-spec drafting / authorization / reviewer) preserved at register-precision; mitigation strategies enumerated per register-class as register-class-distinct (NOT bulk-mitigation)
- Drift signal: bulk-mitigation collapse OR register-class label drift OR cross-cycle comparability requirement absence

**V#5 — Scoping decision §6.4-§6.6 Carry-forwards A/B/C verbatim reproduction at §4.1-§4.3**
- Anchor: grep §4.1 (a)+(b)+(c) Carry-forward A operationalization scope binding against scoping decision §6.4 [sic — actual §6.5 per §1.4 constraint 4 [sic] correction note; §A2 instance #2 register]; grep §4.2 register-class clarification (evaluation only; NOT implementation) against scoping decision §6.5; grep §4.3 (C-1) candidates + (C-2) bar codification + EXISTING tier framework refinement framing against scoping decision §6.6
- Expected: Carry-forward A (a)+(c) operationalization preserved; (b) defer disposition preserved; Carry-forward B evaluation-only register preserved; Carry-forward C tier framework refinement framing per V#10 preserved
- Drift signal: implementation-register leakage at Carry-forward B (any prose suggesting framework code modification at PHASE2C_13 implementation arc beyond evaluation register) = anti-implementation guardrail violation per §4.2.1 binding

**V#6 — Item 7 boundary clause preservation**
- Anchor: grep §2.7 Item 7 boundary clause verbatim binding (TIMING-only mutation; taxonomy + counting logic invariant); grep §3.3 cross-cycle comparability requirement; grep §A1 + §A2 boundary compliance column entries (Y/N values)
- Expected: boundary clause invariant preserved at all 3 register-class-distinct surfaces (Item 7 codification; sub-rule cross-cycle requirement; per-instance log boundary compliance column); ALL §A1+§A2 entries N=clean (no Y=BOUNDARY VIOLATION)
- Drift signal: Y=BOUNDARY VIOLATION at any §A1/§A2 entry = boundary clause violation candidate; cumulative count register drift (instance removed from count instead of closed) = counting logic violation

**V#7 — Carry-forward B evaluation-register preservation (anti-implementation guardrail)**
- Anchor: grep §4.2.1 register-class clarification statement; grep §4.2.4 implementation arc § codification scope (codifies evaluation outcome ONLY; does NOT modify framework code at PHASE2C_13 implementation arc)
- Expected: evaluation-only register preserved at all surfaces; no implementation-register leakage in §4.2 prose
- Drift signal: any §4.2 prose suggesting framework code modification at PHASE2C_13 implementation arc

**V#8 — Carry-forward C tier framework refinement framing preservation (per V#10 anchor; NOT new framework creation)**
- Anchor: grep §4.3.1 (C-1) candidates enumeration register; grep §4.3.2 (C-2) bar criteria 1-4 AND-conjoined; grep §4.3.5 EXISTING tier framework refinement framing + V#10 anchor preservation; grep §4.3.4 Strong-tier promotion explicit sub-spec scope guardrail (codification only at PHASE2C_13; promotion executions OUT-OF-SCOPE)
- Expected: refinement framing preserved; bar codification at REFINEMENT register (NOT new framework creation); ALL 7 Items downgrade to Medium tier or lower per §4.3.3 re-check pass
- Drift signal: any prose suggesting Strong-tier promotion executions at PHASE2C_13 sub-spec body OR new tier framework creation OR tier hierarchy renaming (§13-§20 invariance violation)

**V#9 — METHODOLOGY_NOTES.md §13-§20 tier framework existence empirical re-verify**
- Anchor: `grep -n '^## §1[3-9]\|^## §20' docs/discipline/METHODOLOGY_NOTES.md` at Task 21 Step 21.5 fire register
- Expected: §13-§20 entries present at line numbers consistent with V#10 scoping cycle anchors (Medium tier §18 ~line 2349; Weak tier §19 ~line 2481; Strong tier §20 ~line 2551 per CLAUDE.md PHASE2C_13 entry SEAL register V#10 verification)
- Drift signal: line number drift since scoping cycle V#10 fire = §19 instance candidate at register-class-distinct register (METHODOLOGY_NOTES.md MAY have intermediate edits between PHASE2C_12 closeout SEAL and PHASE2C_13 sub-spec SEAL pre-fire); §13-§20 § header content invariance is the load-bearing anchor for V#10 framing — line number drift acceptable IF § header content invariant preserved (sub-spec V#9 anchor catches line number drift; §13-§20 framework existence is the binding invariant)

**V#10 — Sub-spec line + § count within budget**
- Anchor: `wc -l docs/phase2c/PHASE2C_13_PLAN.md && grep -c '^## ' docs/phase2c/PHASE2C_13_PLAN.md`
- Expected: line count ~600-900 (within scoping decision §6.1 budget; ±20% tolerance per Task 19 Step 19.5 register); § count 10-15 (10 main §§ + appendix §A1 + §A2 = 12 typical)
- Drift signal: line count <500 (under-codified content suspect) OR >1100 (over-codified content suspect; substantive content bloat)

**V#11 — §A1 §9.0c instance log integration into sub-spec deliverable §-cumulative-count register**
- Anchor: grep §A1 table entries; cross-check with V#-chain V#11 anchor at SEAL pre-fire fed into §6 closeout deliverable §6 Item-cumulative-count register
- Expected: ALL §A1 entries logged with 5-column schema (# / register-class / surface task+step / mitigation note / Item 7 boundary compliance + closure status) per Q-S29 §A1/§A2 schema specification; cumulative count register preserved (instances NOT removed from count)
- Drift signal: missing column at any entry = §9.0c instance candidate at sub-spec drafting register (recursive Item 7 anti-meta-pattern instance class)

**V#12 — §A2 §19 instance log integration**
- Anchor: grep §A2 table entries; cross-check PHASE2C_13 entry §19 instance #1 (tag-push divergence; closed real-time at Q-S25 (A)) + Task 2 §19 instance #2 (scoping decision §1.4 constraint 4 [sic] citation drift; closed within sub-spec scope per Q-S33 advisor lean defer)
- Expected: ALL §A2 entries logged; cumulative count preserved; both initial instances closed
- Drift signal: instance count register drift (instance removed instead of closed) OR missing column at any entry

### §7.2 V#-chain fire-time register-class binding

V#-chain fires at Task 21 Step 21.5 register (post-Claude-advisor-full-prose-access-pass + post-per-fix-adjudication; pre-Charlie-SEAL-auth Q-S27 boundary). Per scoping decision §7 verification chain pattern + PHASE2C_11 SEAL pre-fire 9-empirical-verification register precedent + PHASE2C_12 sub-spec drafting cycle SEAL V#1-V#9 + V#10 register-class precedent.

V#-chain register-class-distinct from sub-spec authoring register: empirical fire at Task 21 Step 21.5 surfaces drift ONLY catchable at empirical fire register-class (cross-validation with grep / git CLI / file content checks); sub-spec authoring register (Tasks 1-19) does NOT fire empirical V#-chain (per §17 sub-rule 4 recursive operating rule scope distinction — full-file prose-access pass at sealed-commit register catches prose-level register-precision drift; V#-chain catches empirical-anchor register-precision drift).

**ALL V# anchors must be CLEAN at Task 21 Step 21.5 register before Task 22 Charlie SEAL auth fire.** Any V# drift surfaced at empirical fire = §19 instance candidate (or §9.0c instance candidate if drift is at sub-spec drafting register class) + mitigation per Item 7 (a)+(c) operationalization mechanism + log to §A1/§A2 register at occurrence + re-fire V# anchor at register-precision before Charlie SEAL auth boundary.

### §7.3 V#-chain catch density expectation

Per scoping decision §6 verification chain pattern + PHASE2C_11/12 sub-spec drafting cycle SEAL V#-chain register precedent: V#-chain catches at fire-time typically surface 1-3 register-precision anchor drifts at first fire register; sub-spec authoring register prose-pass at §17 sub-rule 4 typically catches 0-2 prose-level drifts. Cross-cycle pattern: V#-chain register-class-distinct empirical fire is structurally necessary for handoff-noise propagation prevention discipline at sub-spec SEAL pre-fire boundary (PHASE2C_11 SEAL precedent: V#7 register-precision-violation surfaced + Path A patch applied at 4 register-class-distinct sites per CLAUDE.md PHASE2C_11 SEAL entry).

---

## §8 Reviewer pass cycle disposition

This section specifies the triple-reviewer pass cycle disposition at PHASE2C_13 sub-spec drafting cycle reviewer pass register (Tasks 20-21 per meta-plan; fires at session #3+ per pacing discipline post-Checkpoint-3 STRICT pause-default). Per scoping decision §7.2 + handoff §4 step 4 + reviewer-routing precedent at PHASE2C_10/11/12 sub-spec drafting cycle register.

### §8.1 Triple-reviewer disposition

Three reviewer registers operate at PHASE2C_13 sub-spec drafting cycle reviewer pass; Codex skip per scoping decision §5.3 + [`feedback_codex_review_scope.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md) (sub-spec drafting cycle is process/spec deliverable register; Codex adversarial review reserved for substantive code/work register at implementation arc Step seals if applicable).

- **ChatGPT first-pass (structural overlay register)** — fires at Task 20; surfaces structural-overlay defects (compression direction; structural framing; cross-reference register; overall spec coherence). PHASE2C_11/12 cycle precedent: ChatGPT structural-overlay register catches typically include compression direction recommendations + structural option selection (e.g., 4-subsection vs single-section) + cross-reference precision at register-overlay register.
- **Claude advisor full-prose-access pass (substantive register)** — fires at Task 21; substantive prose-pass per [METHODOLOGY_NOTES §16](../discipline/METHODOLOGY_NOTES.md) anchor-prose-access discipline. PHASE2C_11/12 cycle precedent: advisor full-prose-access pass catches register-precision defects + cross-section consistency + factual attribution at canonical-artifact register that ChatGPT structural overlay misses by construction.
- **Claude Code register-precision verification (post-reviewer-pass; pre-Charlie-SEAL)** — fires at Task 21 Step 21.6 + Step 21.5 V#-chain pre-fire empirical verification per §17 sub-rule 4 recursive operating rule. Full-file prose-access pass at sealed-commit register catches any post-patch regression OR section-targeted-patch ripple at cross-section consistency register.

**Codex skip rationale (binding at sub-spec drafting cycle register):** sub-spec drafting cycle deliverable = process/spec content register-class-distinct from substantive code/work register; Codex adversarial review provides marginal value at process/spec register per scoping decision §5.3 binding + memory feedback_codex_review_scope.md hard rule. Codex MAY fire at implementation arc Step boundaries if implementation arc Step seals include substantive code touches (e.g., backtest framework code modifications would route Codex review per memory rule); PHASE2C_13 implementation arc per §5.6 = METHODOLOGY_NOTES.md append + closeout deliverable seal only (no framework code modification per Carry-forward B anti-implementation guardrail at §4.2.1 binding) → Codex skip persists at implementation arc register.

### §8.2 Per-fix adjudication discipline (no bulk-accept)

Per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) hard rule + PHASE2C_10/11/12 reviewer pass cycle precedent: per-fix verification before convergence; no bulk-accept of reviewer findings.

**Per-fix adjudication mechanism at Task 20-21 register:**

1. **Charlie surfaces reviewer findings to Claude Code** — Charlie pastes reviewer (ChatGPT or advisor) finding list at chat register. Claude Code does NOT directly invoke ChatGPT or advisor (per Task 20.0 + Task 21.0 meta-plan binding; this is Charlie's workflow register-class-distinct from Claude Code's).
2. **For each finding (sequentially per finding register):**
   - Read finding rationale verbatim
   - Verify against actual sub-spec text (Read tool at relevant § slot)
   - Reason: APPROVE-as-stated / APPROVE-with-refinement / REJECT-with-rationale / DEFER-to-Charlie
   - Document adjudication decision in chat register (audit trail at conversation register)
3. **APPROVE finding:** apply patch with Edit tool; re-read patched § to verify defect closure
4. **REJECT finding:** document rationale for Charlie register; surface as "reviewer finding REJECTED — rationale: <prose>" at chat register
5. **DEFER finding:** surface to Charlie register-event-distinct boundary for adjudication; do NOT default-resolve at Claude Code register (anti-momentum-binding strict reading)
6. **Healthy reasoned-adjudication cycle pattern recognition** — substantive reviewer divergence at Charlie register adjudication = candidate cycle-internal observation per Carry-forward C §4.3.1 Candidate 4 register; log if applicable

**Anti-pattern explicit rejection:** bulk-accept (e.g., "applying all 8 ChatGPT findings as-stated") collapses per-fix verification register-class-precision; substantive divergence between findings + sub-spec scope binding may exist at finding-class register requiring per-fix adjudication. PHASE2C_10/11/12 cycle precedent: bulk-accept register-class violation NEVER fired; per-fix adjudication operated at all reviewer pass cycles.

### §8.3 Catch density expectation

Per advisor pre-drafting Obs 1 (Q-S26 advisor evaluation register) + scoping decision §6.1 register-precision anchor:

- **Scoping decision** at PHASE2C_13 entry register: 8 patches / 421 lines = ~1.66% catch density (substantively higher than typical PHASE2C scoping decisions ~0.5-1.0% per cross-cycle observation)
- **Sub-spec at PHASE2C_13** (this deliverable): substantively larger artifact (~600-900 lines estimated; current line count register at Task 19 Step 19.5 fire); predicted catch density 1.5-2.5% → **9-22 patches at reviewer pass cycle**

**Iteration count expectation:**

- ChatGPT first-pass (Task 20): 1-2 reviewer pass iterations typical (Task 20 fires once + post-patch re-pass if substantive defects surfaced); per-fix adjudication may surface DEFER-to-Charlie cases requiring register-event-boundary-distinct authorization
- Claude advisor full-prose-access pass (Task 21): 1-2 reviewer pass iterations typical (Task 21 fires once post-Task-20 + post-patch re-pass at Step 21.3 + V#-chain pre-fire empirical verification at Step 21.5 + final full-file prose pass at Step 21.6 per §17 sub-rule 4)
- Total reviewer pass cycle iterations: ~2-4 across Tasks 20-21 register

**Plan reviewer pass cycle iteration count accordingly per per-iteration patch landing register:** patch landing per iteration ~5-12 patches typical; cumulative 9-22 patch budget aligns with ~2-3 iterations on the patches landing distribution.

### §8.4 V#-chain pre-fire empirical verification at Step 21.5

V#-chain fires at Task 21 Step 21.5 per §7.2 binding (post-advisor-pass + post-per-fix-adjudication; pre-Charlie-SEAL-auth Q-S27 boundary). All 12 V# anchors enumerated at §7.1 fire empirical verification at this register; ALL V# CLEAN required before Task 22 Charlie SEAL auth fire.

### §8.5 Reviewer pass cycle SEAL register-event boundary

Reviewer pass cycle terminates at register-event-boundary-distinct boundary from Charlie SEAL auth Q-S27. Specifically:

- Reviewer pass cycle CLOSE = both ChatGPT first-pass + Claude advisor full-prose-access pass converged at substantive register (no outstanding reviewer findings; all surfaced findings adjudicated APPROVE/REJECT/DEFER with adjudication decisions documented at chat register)
- Reviewer pass cycle CLOSE → V#-chain pre-fire empirical verification (Task 21 Step 21.5)
- V#-chain CLEAN → final full-file prose-pass (Task 21 Step 21.6 per §17 sub-rule 4 recursive operating rule)
- Final full-file prose-pass CLEAN → Charlie SEAL auth Q-S27 surface boundary (Task 22 Step 22.1)
- Q-S27 (sub-spec SEAL commit) + Q-S28 (push) auth fires at Charlie register; NO operational fire until explicit Charlie register messages received per anti-momentum-binding hard rule

---

## §9 Cross-references

This section enumerates cross-references to anchor documents that this sub-spec depends on or interacts with at register-precision register. Per scoping decision §8 cross-reference register pattern + handoff §1 read-first context register precedent.

### §9.1 PHASE2C_12 cross-references

- [`docs/closeout/PHASE2C_12_RESULTS.md`](../closeout/PHASE2C_12_RESULTS.md) — PHASE2C_12 breadth-expansion arc closeout deliverable; §10.2 Items 1-6 verbatim source register for §2.1-§2.6 codification (consume-only per scoping decision §1.4 constraint 6); §8.2 §9.0c instance enumeration source register; §10 Carry-forwards binding source register; §10.6 cross-cycle scaling observation source for §4.1 Carry-forward A operationalization
- [`docs/phase2c/PHASE2C_12_SCOPING_DECISION.md`](PHASE2C_12_SCOPING_DECISION.md) — PHASE2C_12 entry scoping decision; cross-cycle precedent register for PHASE2C_13 entry scoping cycle pattern
- [`docs/phase2c/PHASE2C_12_PLAN.md`](PHASE2C_12_PLAN.md) — PHASE2C_12 sub-spec drafting cycle deliverable; cross-cycle precedent register for PHASE2C_13 sub-spec drafting cycle pattern + 6-component sub-spec structure pattern

### §9.2 PHASE2C_10 + PHASE2C_11 cross-references

- [`docs/closeout/PHASE2C_10_METHODOLOGY_CONSOLIDATION_SIGNOFF.md`](../closeout/PHASE2C_10_METHODOLOGY_CONSOLIDATION_SIGNOFF.md) — PHASE2C_10 methodology consolidation arc closeout; cross-cycle precedent register for PHASE2C_13 closeout deliverable structure (per §6.1 binding) + tag naming convention `phase2c-13-methodology-consolidation-v1` per `phase2c-10-methodology-consolidation-v1` precedent (per §6.2 binding)
- [`docs/phase2c/PHASE2C_10_PLAN.md`](PHASE2C_10_PLAN.md) — PHASE2C_10 sub-spec drafting cycle deliverable; cross-cycle precedent register at sub-spec structure pattern + per-§ seal pattern (per §5.5 binding) + reviewer pass cycle pattern
- [`docs/closeout/PHASE2C_11_RESULTS.md`](../closeout/PHASE2C_11_RESULTS.md) — PHASE2C_11 statistical-significance machinery arc closeout; cross-cycle precedent register for §7 V#-chain pattern + §8 reviewer pass cycle disposition pattern + tag attachment register-event boundary discipline (Path A.2)
- [`docs/phase2c/PHASE2C_11_PLAN.md`](PHASE2C_11_PLAN.md) — PHASE2C_11 sub-spec drafting cycle deliverable; cross-cycle precedent register at V#-chain enumeration pattern + Codex skip at sub-spec drafting cycle register precedent

### §9.3 METHODOLOGY_NOTES cross-references

- [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) — append target for PHASE2C_13 implementation arc (per §5.6 Steps 1-12)
  - **§13-§20 tier framework register** — V#10 anchor at scoping decision (Medium tier §18 line 2349; Weak tier §19 line 2481; Strong tier §20 line 2551); §4.3.5 EXISTING tier framework refinement framing binding; §7 V#9 anchor for empirical re-verify at Task 21 Step 21.5
  - **§16 anchor-prose-access discipline** — discipline anchor #1 at §0.3; §17 sub-rule 4 recursive operating rule reference
  - **§17 procedural-confirmation defect class + sub-rule 4 (full-file prose-access pass at sealed-commit register)** — §0.3 discipline anchor + §5.5 per-§ seal pattern Step 3 + §7.2 V#-chain register-class-distinct binding + §8.5 reviewer pass cycle SEAL register-event boundary
  - **§19 spec-vs-empirical-reality finding pattern** — discipline anchor #6 at §0.3; §A2 cycle-internal log register-class-distinct from §19 historical observation register; Carry-forward C §4.3.1 Candidate 1 register
  - **§20 Path A.2 register-event boundary discipline** — §6.2 tag attachment binding (annotated tag at closeout deliverable seal commit, NOT Phase Marker housekeeping commit)
  - **New §§ to be appended at PHASE2C_13 implementation arc** — §21 Item 1 + §22 Item 2 (with Item 4 fold-in) + §23 Item 3 + §25 Item 5 + §26 Item 6 (with §9.0c sub-rule fold-in) + §27 Item 7 + §28 Carry-forward A + §29 Carry-forward B + §20 fold-in Carry-forward C bar criteria (per §5.4 disposition register)

### §9.4 CLAUDE.md cross-references

- [`CLAUDE.md`](../../CLAUDE.md) — project convention + Phase Marker register
  - **Phase Marker (Current phase):** PHASE2C_13 entry scoping cycle SEALED entry (canonical state at sub-spec authoring register; advance to PHASE2C_13 sub-spec drafting cycle SEALED at Task 22 SEAL bundle Step 22.4)
  - **Phase Marker (Prior phase):** PHASE2C_12 breadth-expansion arc SEALED — empirical anchor for §1.2 cycle scope summary + §4.1.1 backfill register + §4.2.2 evidence basis register + §4.3.1 Carry-forward C candidates enumeration
  - **CLAUDE.md "Hard rule for any future WF-consuming work"** — referenced at scoping decision §0 anchor; not directly load-bearing at PHASE2C_13 sub-spec scope but binding at implementation arc IF any framework code consumer touches surface (per §4.2.1 anti-implementation guardrail; PHASE2C_13 implementation arc per §5.6 = METHODOLOGY_NOTES append + closeout only, no framework code touches expected)

### §9.5 Feedback memory cross-references

Per [`MEMORY.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/MEMORY.md) index:

- [`feedback_authorization_routing.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md) — hard rule at §0.3 discipline anchor + §3.2 authorization register mitigation strategies + §8.5 reviewer pass cycle SEAL boundary; Charlie-register-only authorization for operational fires; reviewer convergence is advisory only
- [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) — §3.2 reviewer register mitigation strategies + §8.2 per-fix adjudication discipline (no bulk-accept) + Carry-forward C §4.3.1 Candidate 4 (Q10/M6-F2 healthy reasoned-adjudication cycle pattern)
- [`feedback_codex_review_scope.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md) — §3.2 reviewer register Codex skip rationale + §5.5 per-§ seal pattern reviewer pass + §8.1 Codex skip binding at sub-spec drafting cycle register
- [`feedback_claude_md_freshness.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md) — §5 Phase Marker advance discipline at per-§ seal pattern + §5.6 Step 12 closeout deliverable seal Phase Marker advance
- [`feedback_long_task_pings.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_long_task_pings.md) — notification fire at Task 21 Step 21.7 + Checkpoint 3 surface (per session #2 work completion) + future Codex review fires at implementation arc Step boundaries if applicable
- [`feedback_use_planning_skills_for_complex_tasks.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_use_planning_skills_for_complex_tasks.md) — meta-plan invocation at sub-spec drafting cycle entry per scoping decision §6.1 (Q-S31 hybrid mode register); meta-plan at [`docs/superpowers/plans/2026-05-05-phase2c-13-sub-spec-drafting.md`](../superpowers/plans/2026-05-05-phase2c-13-sub-spec-drafting.md)
- [`feedback_bilingual_concept_explanation.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_bilingual_concept_explanation.md) — discipline anchor #11 at handoff §5; §2.7 Item 7 bilingual anchor + §4.3 Carry-forward C bilingual anchor

### §9.6 Sub-spec deliverable cross-reference (this document)

- [`docs/phase2c/PHASE2C_13_PLAN.md`](PHASE2C_13_PLAN.md) — this sub-spec drafting cycle deliverable (canonical artifact at SEAL register post-Q-S27 fire)
- [`docs/phase2c/PHASE2C_13_SCOPING_DECISION.md`](PHASE2C_13_SCOPING_DECISION.md) — PHASE2C_13 entry scoping decision SEAL artifact at commit `df8ca65`; binding scope source for §1 Goal + §2 Items 1-7 + §3 sub-rule + §4 Carry-forwards A/B/C + §5 implementation arc + §6 closeout + §7 V#-chain + §8 reviewer pass + §9 cross-references registers
- [`docs/superpowers/plans/2026-05-05-phase2c-13-sub-spec-drafting.md`](../superpowers/plans/2026-05-05-phase2c-13-sub-spec-drafting.md) — meta-plan for PHASE2C_13 sub-spec drafting cycle (22-task structure + Charlie auth boundaries + checkpoint structure)

---

## §A1 Cycle-internal §9.0c instance log

PHASE2C_13 cycle-internal running log; appended at occurrence per Item 7 (a) lightweight tracking; reviewed at cycle boundary fires per Item 7 (c). Register-class taxonomy preserved per Item 7 boundary clause (3 classes: sub-spec drafting / authorization / reviewer); cumulative count register preserved (instances logged + counted across cycle, not removed).

| #     | Register-class | Surface task+step | Mitigation note (per Item 7 (a)+(c)) | Item 7 boundary compliance + closure status |
| ----- | -------------- | ----------------- | ------------------------------------- | ------------------------------------------- |
| #1    | reviewer       | PHASE2C_13 sub-spec drafting cycle entry, advisor Obs 2 surface (per meta-plan adjudication register) | (a) Lightweight tracking: meta-plan absent §9.0c log mechanics specification → sub-spec drafting register-class confusion candidate at implementer-time. (c) Boundary-fire mitigation review: §9.0c + §19 log mechanics specification folded pre-Task-1 in meta-plan per Q-S29 Charlie auth APPROVED. | N=clean (mitigation alters meta-plan structure, NOT §9.0c taxonomy or counting); closed |
| #2    | reviewer       | Task 20 ChatGPT first-pass surface, P1.4 finding (Q-S27a register-class implication) | (a) Lightweight tracking: §A2 register-class binding under each Reading (i)/(ii)/(iii) was implicitly load-bearing at sub-spec body but not explicitly stated; ChatGPT structural overlay register surfaced binding gap at sub-spec authoring register. Process-design observation: register-class-implication-load-bearing accumulation from sessions #1+#2 (per session #2 close Observation 4) reached register-precision threshold for explicit prose binding at session #3 reviewer pass. (c) Boundary-fire mitigation review: §A2 register-class clarification block appended to §2.7 Reading enumeration register; per-Reading binding interpretation (observational under (i) / normative-precedent under (ii)/(iii) / normative-precedent + future-pattern-extension under (iii)) explicit prose at §2.7 host slot. Per-fix adjudication APPROVE-with-refinement applied at register-precision; patch landed at register-event boundary detection. | N=clean (mitigation = explicit prose binding at sub-spec §2.7; §9.0c reviewer-register taxonomy preserved; cumulative count register preserved — instance #2 logged + closed); closed |
| #3    | reviewer       | Task 21 advisor full-prose-access pass surface, F1 finding (HIGH severity — §A2 schema empirically operates Reading (iii) at full Item 7 mechanism since session #1; operating-pattern-vs-codification gap material at Q-S27a SEAL boundary) | (a) Lightweight tracking: advisor full-prose-access pass register surfaced operating-pattern-vs-codification gap — §A2 5-column schema (boundary compliance + Item 7 (a)+(c) mitigation-note structure + cumulative count register preservation) IS Reading (iii) operating pattern at structural register; cumulative §A2 entries (#1-#3 individual + #4-#10 cluster) all logged with full Item 7 schema = empirical operating pattern at Reading (iii) register. Reading (i) selection at Q-S27a SEAL boundary creates operating-pattern-vs-codification gap requiring either §A2 schema downgrade OR explicit codification of gap as cycle-internal observation. (c) Boundary-fire mitigation review: explicit operating-pattern-vs-codification gap surface block appended to §2.7 §A2 register-class clarification block (post-P1.4 patch host slot); Reading (i) selection load-bearing implication at SEAL boundary surfaced explicitly; anti-momentum-binding strict reading at Q-S27a SEAL preserved (Charlie register decides at SEAL post-V#-chain CLEAN + final full-file prose-pass). Per-fix adjudication APPROVE-with-refinement applied at register-precision. | N=clean (mitigation = explicit prose binding at §2.7 host slot; §9.0c reviewer-register taxonomy preserved; cumulative count register preserved — instance #3 logged + closed); closed |
| #4    | reviewer       | Task 21 advisor full-prose-access pass surface, F4 finding (LOW severity — §A2 cluster #4-#10 cross-cycle parse register-precision risk) | (a) Lightweight tracking: cluster format is novel at §A2 register-class (first cluster entry at PHASE2C_13 cycle internal logs); cumulative count integrity at PHASE2C_14+ cycle reading register dependent on reader parse discipline (cluster numbering #4-#10 = 7 instances may parse as 1 instance if cluster format unfamiliar). (c) Boundary-fire mitigation review: cumulative count clarification at cluster entry register-precision (representing 7 distinct sub-defects per cluster surface event; cumulative §A2 count = 10 post-Task-20) + §3.3 operational requirement #6 cluster-format register-precision discipline (cluster log entries MUST enumerate sub-defect count explicitly at mitigation note for cross-cycle parse register-precision). Per-fix adjudication APPROVE-with-refinement applied at register-precision. | N=clean (mitigation = cumulative count clarification + §3.3 operational requirement append; §9.0c reviewer-register taxonomy preserved; cumulative count register preserved — instance #4 logged + closed); closed |
| #5    | reviewer       | Task 21 advisor full-prose-access pass surface, F5 finding (LOW severity — §5.4 Carry-forward C (b) appendix-style register-class precision; §20 host-slot accommodation) | (a) Lightweight tracking: §20 host slot codifies "Path A.2 register-event boundary discipline" content per V#10 verification; appendix-style sub-§ "Strong-tier promotion bar criteria" introduces register-class-distinct sub-content at same § slot; need explicit framing for register-class accommodation discipline. (c) Boundary-fire mitigation review: §20 sub-§ host-slot accommodation framing block appended to §4.3.5 EXISTING tier framework refinement framing register; §20.1 (existing Path A.2 content invariant) + §20.2 (new appendix-style bar criteria sub-§) sub-§ structure framing at §4.3.5 + §5.4 Carry-forward C row; both register-class-coherent under parent § principle "Strong tier register"; final §20 sub-§ structure authored at implementation arc Step 9 § seal register. Per-fix adjudication APPROVE-with-refinement applied at register-precision. | N=clean (mitigation = §20 sub-§ structure framing prose + §5.4 row update; §9.0c reviewer-register taxonomy preserved; cumulative count register preserved — instance #5 logged + closed); closed |
| #6    | reviewer       | Task 21 advisor full-prose-access pass surface, F6 finding (LOW severity — §5.4 Item 7 fold-in disposition Q-S27a-resolution stability) | (a) Lightweight tracking: criterion (b) failure rationale at §5.4 Item 7 row partially anchored on "Reading (i)/(ii)/(iii) scope question" content; post-Q-S27a-resolution at SEAL boundary, Reading scope question content collapses to specific Reading content; question whether fold-in disposition stability holds post-resolution. (c) Boundary-fire mitigation review: substantive verify confirms Item 7 codification still requires 4-subsection content body (boundary clause prose + operating discipline at cycle-internal + Application checklist 6 items + bilingual concept anchor + cross-references) regardless of Q-S27a outcome → criterion (b) failure stable across Reading (i)/(ii)/(iii) outcomes → new-§ disposition stable post-Q-S27a-resolution; Q-S27a-resolution stability note appended to §5.4 Item 7 row at register-precision. Per-fix adjudication APPROVE-with-refinement applied at register-precision. | N=clean (mitigation = Q-S27a-resolution stability note at §5.4 row; §9.0c reviewer-register taxonomy preserved; cumulative count register preserved — instance #6 logged + closed); closed |

**§A1 cumulative count register summary at post-Task-21 register:** 6 instances total at PHASE2C_13 sub-spec drafting cycle internal register — #1 (entry session meta-plan log mechanics) + #2 (Task 20 ChatGPT P1.4 Q-S27a register-class) + #3 (Task 21 advisor F1 operating-pattern-vs-codification gap) + #4 (Task 21 advisor F4 cluster cross-cycle parse) + #5 (Task 21 advisor F5 §20 sub-§ accommodation) + #6 (Task 21 advisor F6 Q-S27a-resolution stability); all reviewer-register class; all closed at N=clean register; cumulative count register preserved per Item 7 boundary clause invariant.

## §A2 Cycle-internal §19 instance log

PHASE2C_13 cycle-internal running log; appended at occurrence per Item 7 (a) lightweight tracking; reviewed at cycle boundary fires per Item 7 (c). Single-class register per METHODOLOGY_NOTES §19 (spec-vs-empirical-reality finding pattern); cumulative count register preserved.

| #     | Register-class | Surface task+step | Mitigation note (per Item 7 (a)+(c)) | Item 7 boundary compliance + closure status |
| ----- | -------------- | ----------------- | ------------------------------------- | ------------------------------------------- |
| #1    | spec-vs-empirical-reality | PHASE2C_13 entry session, Q-S25 surface | (a) Lightweight tracking: tag-push divergence (CLAUDE.md prior-cycle Phase Marker doc'd "(P1) bundled push triple-reviewer convergence" but `push.followTags=false` git default left annotated tag `phase2c-12-breadth-expansion-v1` local-only at PHASE2C_12 SEAL bundle push). (c) Boundary-fire mitigation review: explicit `git push origin phase2c-12-breadth-expansion-v1` per Q-S25 (A) Charlie auth APPROVED at PHASE2C_13 sub-spec drafting cycle entry register-event boundary detection. | N=clean (mitigation = real-time tag push at register-event boundary; §19 cumulative count register preserved — instance #1 logged + closed, not removed from count); closed |
| #2    | spec-vs-empirical-reality | Task 2 Step 2.4 surface (sub-spec §1.4 constraint 4 VERBATIM reproduction) | (a) Lightweight tracking: scoping decision §1.4 constraint 4 cites "§6.4 register-class clarification" but §6.4 is empirically Carry-forward A (cycle-complexity scaling) per actual SEALED scoping decision file structure; the Carry-forward B register-class clarification is at §6.5. Citation drift WITHIN scoping decision SEALED artifact. (c) Boundary-fire mitigation review: VERBATIM preservation discipline applied — no silent fix to SEALED scoping decision content (anti-momentum-binding); [sic] correction note added inline at §1.4 constraint 4 reproduction surfacing the drift to readers; reader interpretation note specifies substitute §6.5 for §6.4 per constraint 4 intent. Surface to Charlie at sub-spec SEAL pre-fire register for adjudication on whether scoping decision separately needs amendment fire (out of scope for sub-spec drafting cycle scope; advisory-only surface). | N=clean (sub-spec mitigation = annotation + reader-substitution note; §19 cumulative count register preserved — instance #2 logged + closed for sub-spec drafting cycle scope; scoping decision amendment register-class-distinct from sub-spec drafting cycle scope and out-of-scope per scoping decision §1.4 constraint 7 anti-momentum-binding extended interpretation); closed within sub-spec drafting cycle scope |
| #3    | spec-vs-empirical-reality | Task 19 Step 19.5 surface (full-draft self-review M7 in-scope cumulative line count vs budget check) | (a) Lightweight tracking: scoping decision §6.1 estimated sub-spec budget "600-900 lines" at SOFT-estimate register; empirical line count at Task 19 self-review register = 970 lines (+7.8% over 900 top of soft-estimate band). Per V#10 anchor binding: 600-900 = soft estimate; >1100 = hard bloat threshold for over-codified content suspect. 970 lines < 1100 hard threshold = within acceptable register; over-soft-estimate-band drift tracked observation-only. Substantive content density justified by §5.4 per-candidate fold-in 4-criteria check table (11-row substantive content) + §7.1 V# anchor enumeration (12 V# anchors with substantive bodies per §17 sub-rule 4 register-precision register) + §4 Carry-forwards A/B/C operationalization with bilingual concept anchors. (c) Boundary-fire mitigation review: observation-only at sub-spec drafting cycle SEAL pre-fire register; no content removal warranted (content density structural to sub-spec scope per scoping decision §6 binding). | N=clean (sub-spec content density preserved; cumulative count register preserved — instance #3 logged + closed within sub-spec drafting cycle scope; soft-estimate-band drift acceptable at scope-justified content density register; hard-threshold register-class-distinct register preserved invariant); closed within sub-spec drafting cycle scope |
| #4-#10 (cluster representing 7 distinct sub-defects per cluster surface event; cumulative §A2 count = 10 instances post-Task-20 cluster, NOT 4 instances if cluster parsed as 1 — per §3.3 operational requirement #6 cluster-format register-precision discipline) | spec-vs-empirical-reality | Task 20 ChatGPT first-pass surface event (single surface; 7 sub-defects clustered per Item 7 (a) lightweight tracking discipline + Item 6 sub-rule register-class-distinct counting at PHASE2C_12 §19 register precedent for multi-defect-from-single-source enumeration) | (a) Lightweight tracking: ChatGPT structural overlay register surfaced 7 register-precision defects within sub-spec body — **#4** (P1.1) §5.4 count contradiction "7 new §§" enumerates 8; **#5** (P1.2) §5.6 step-count rationale "1 Step per code-site touch (8+3=11)" inconsistent with 9-content-Step + 3-process/closeout-Step actual sequence (Steps 2 + 5 bundle new-§ + fold-in); **#6** (P1.3) V#10 600-900 soft / >1100 hard tolerance vs §A2 #3 "above V#10 ±20% tolerance band ceiling 960" internal contradiction at sub-spec body register; **#7** (P1.5) §4.3.3 Item 3 final tier ambiguous "Medium tier (...possibly Weak tier)" register-precision violation; **#8** (P1.6) §4.3.4 promotion scope contradiction (text says "promote at § seal if criteria hold" but §4.3.3 re-check shows ALL 7 Items fail C4 by construction at first cycle); **#9** (P2.7) §4.1.1 PHASE2C_10 row §19 column "6 cumulative cross-cycle... vs total cumulative-3" parse difficulty at register; **#10** (P2.8) §5.4 Carry-forward C row criterion (b) marked ✗ but disposition fold-in despite (b) failure. (c) Boundary-fire mitigation review: per-fix adjudication discipline applied per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) hard rule (no bulk-accept); each defect adjudicated APPROVE / APPROVE-with-refinement at register-precision; 7 patches landed at sub-spec body before advisor pass + V#-chain fire. Patches: P1.1 §5.4 → "8 new §§"; P1.2 §5.6 → 9-content-Step + 3-process/closeout-Step rationale; P1.3 §A2 #3 → V#10 600-900 soft / >1100 hard binding; P1.5 §4.3.3 Item 3 → "Weak tier observation-only with cross-cycle-pending" aligning with §19 register precedent; P1.6 §4.3.4 → "no Strong-tier promotions authorized AT PHASE2C_13 cycle register (cycle-class-specific)" binding (§4.3.3 all-fail-C4 by construction); P2.7 §4.1.1 → split "3 (cycle-local) / 6 (cross-cycle cumulative since PHASE2C_9)"; P2.8 §5.4 → criterion (b) ✓ via appendix-style sub-§ at §20 host slot framing. | N=clean cluster (7 sub-defects each at register-precision within Item 7 boundary clause TIMING-only mutation: mitigation = sub-spec text patches at register-precision; §19 taxonomy preserved at single-class register-class register per METHODOLOGY_NOTES §19 framework; cumulative count register preserved — instances #4-#10 logged + closed at register-precision (7 distinct instances; cumulative §A2 count post-Task-20 = 10 instances total summing #1-#3 individual + #4-#10 cluster); cluster surface event = single Task 20 register-event boundary detection; per-defect numbering preserves cross-cycle counting comparability anchor per §3.3 operational requirement #2 + #6); all closed within Task 20 ChatGPT first-pass surface event |
| #11-#12 (cluster representing 2 distinct sub-defects per cluster surface event; cumulative §A2 count = 12 instances post-Task-21 cluster — only F2 + F3 sub-defects of 6 advisor findings register at §A2 §19 register-class; F1 + F4 + F5 + F6 are §A1 §9.0c reviewer-register class per Item 6 sub-rule register-class-distinct counting; F1 + F4 + F5 + F6 = 4 §A1 entries; F2 + F3 = 1 cluster §A2 entry; per Item 6 sub-rule register-class-distinct counting + §3.3 operational requirement #6 cluster-format register-precision discipline) | spec-vs-empirical-reality | Task 21 Claude advisor full-prose-access pass surface event (single surface; 2 sub-defects clustered per Item 7 (a) lightweight tracking discipline; F2 + F3 §19 register-class only; F1 + F4 + F5 + F6 routed to §A1 reviewer-register) | (a) Lightweight tracking: Claude advisor full-prose-access pass surfaced 2 register-precision §19 defects within sub-spec body — **#11** (F2) §A2 #3 mitigation-note rewrite Item 7 boundary compliance question (rewrite of historical log entry text vs TIMING-only mutation register-class boundary clarification needed); **#12** (F3) §4.3.4 P1.6 patch cycle-specificity register-precision (anti-momentum-binding cross-cycle scope preservation: blanket "no Strong-tier promotions" without explicit cycle-class qualifier risks PHASE2C_14+ promotion authorization over-binding). (c) Boundary-fire mitigation review: per-fix adjudication APPROVE-with-refinement applied per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) hard rule; patches: F2 §3.3 → operational requirement #5 mitigation-note text register-precision discipline at register-class-distinct register from taxonomy/counting invariance; F3 §4.3.4 → explicit cycle-class-specific scope qualifier "AT PHASE2C_13 cycle register" + anti-momentum-binding cross-cycle scope preservation prose. | N=clean cluster (2 sub-defects each at register-precision within Item 7 boundary clause TIMING-only mutation: mitigation = sub-spec text patches at register-precision; §19 taxonomy preserved at single-class register-class register; cumulative count register preserved — instances #11-#12 logged + closed at register-precision; cumulative §A2 count post-Task-21 = 12 instances total summing #1-#3 individual + #4-#10 cluster + #11-#12 cluster; per-defect numbering preserves cross-cycle counting comparability anchor per §3.3 operational requirement #2 + #6); all closed within Task 21 advisor pass surface event |

| #13   | spec-vs-empirical-reality | Task 21 Step 21.5 V#-chain pre-fire empirical verification surface (V#9 anchor fire) | (a) Lightweight tracking: METHODOLOGY_NOTES.md §13-§20 line numbers drifted from scoping cycle V#10 anchors — empirical line numbers at SEAL pre-fire register: §13 line 1402 / §14 line 1549 / §15 line 1724 / §16 line 1903 / §17 line 2107 / §18 line 2320 (was 2349; drift -29) / §19 line 2481 (CLEAN; matches anchor) / §20 line 2525 (was 2551; drift -26). § header content invariance verified at grep (all 8 §§ present at expected register-class). (c) Boundary-fire mitigation review: per V#9 explicit binding "line number drift acceptable IF § header content invariant preserved (sub-spec V#9 anchor catches line number drift; §13-§20 framework existence is the binding invariant)" — drift is acceptable at V#9 binding semantic (framework existence preserved); §19 instance logged at register-class-distinct register per V#9 anchor explicit "line number drift since scoping cycle V#10 fire = §19 instance candidate". METHODOLOGY_NOTES.md may have intermediate edits between PHASE2C_12 closeout SEAL and PHASE2C_13 sub-spec SEAL pre-fire (Item 7 boundary clause permits content evolution at append-only register). | N=clean (V#9 drift acceptable per V#9 binding; § header content invariance preserved at empirical fire register; cumulative count register preserved — instance #13 logged + closed; mitigation = observational tracking at register-precision; no schema/taxonomy/counting mutation per Item 7 boundary clause invariant); closed |
| #14   | spec-vs-empirical-reality | Task 21 Step 21.5 V#-chain pre-fire empirical verification surface (V#11+V#12 anchor fire — §A2 cluster #11-#12 header internal contradiction) | (a) Lightweight tracking: §A2 cluster entry header initially authored as "#11-#15 (cluster representing 5 distinct sub-defects)" but body enumeration has only 2 sub-defects (#11 F2 + #12 F3); cumulative count summary block enumerates "#11-#12 cluster (2 sub-defects from Task 21 advisor F2 + F3)". Internal contradiction at cluster header vs body enumeration vs summary register-class. Surfaced at V#-chain pre-fire empirical verification register. (c) Boundary-fire mitigation review: cluster header text correction at register-precision — "#11-#15 (cluster representing 5 distinct sub-defects per cluster surface event; cumulative §A2 count = 11)" → "#11-#12 (cluster representing 2 distinct sub-defects per cluster surface event; cumulative §A2 count = 12)"; mitigation-note text correction at log register per §3.3 operational requirement #5 (mitigation-note text register-precision discipline at register-class-distinct register from taxonomy/counting invariance); cumulative count register integrity preserved (cluster body F2 + F3 = 2 sub-defects; cluster numbering #11-#12 preserved at register-precision). | N=clean (mitigation = log entry header text correction at register-precision; §19 taxonomy preserved at single-class register-class register; cumulative count register integrity preserved per F2 patch §3.3 operational requirement #5 register-precision discipline at register-class-distinct register from taxonomy/counting invariance; instance #14 logged + closed); closed |

| #15   | spec-vs-empirical-reality | Task 21 Step 21.5 V#-chain pre-fire empirical verification surface (V#6 strengthening per ChatGPT advisor pushback at SEAL pre-fire register) | (a) Lightweight tracking: V#6 string-count grep proxy ("N=clean" count = 16 vs expected 13 row-level) surfaced as unreliable verification method — string-count includes 13 row-level closure-column boundary assessments + 3 prose mentions in cumulative count summary blocks. ChatGPT advisor surfaced at SEAL pre-fire register: V#6 invariant is NOT "no Y=BOUNDARY in logs" (necessary but not sufficient) but "1:1 mapping between log entries and boundary assessments". Row-level reconciliation required at register-precision before SEAL fire. (c) Boundary-fire mitigation review: row-level 1:1 mapping verified at register-precision via awk-bounded section grep — §A1 6 row entries / 6 N=clean closure-column boundary assessments ✓; §A2 7 row entries / 7 N=clean closure-column boundary assessments ✓; total 13 row-level boundary assessments covering 20 distinct instances (6 §A1 + 14 §A2 sub-defects via cluster + individual row mix per §3.3 operational requirement #6 cluster-format register-precision discipline). String-count grep proxy method discarded as unreliable per ChatGPT pushback; row-level mapping methodology codified at §3.3 operational requirement #7 (post-patch fold). | N=clean (V#6 strengthened: 13/13 row-level mapping verified; cluster row + single boundary assessment = 1 mitigation entry per cluster surface event per Item 6 sub-rule register-class-distinct counting; mitigation = verification methodology refinement at register-class-distinct register from log content; cumulative count register integrity preserved — instance #15 logged + closed); closed |

**§A2 cumulative count register summary at post-Task-21-Step-21.5 register (post-V#6-strengthening):** 15 instances total at PHASE2C_13 sub-spec drafting cycle internal register — #1 (Q-S25 tag-push) + #2 (Task 2 [sic] citation) + #3 (Task 19 line count) + #4-#10 cluster (7 sub-defects from Task 20 ChatGPT) + #11-#12 cluster (2 sub-defects from Task 21 advisor F2 + F3) + #13 (Task 21 Step 21.5 V#9 line number drift) + #14 (Task 21 Step 21.5 V#11+V#12 cluster header internal contradiction) + #15 (V#6 strengthening row-level 1:1 mapping reconciliation per ChatGPT pushback); all closed at N=clean register; cumulative count register preserved per Item 7 boundary clause invariant.

**V#6 strengthened invariant (row-level mapping methodology)**: V#6 verification fires at row-level 1:1 mapping between log entries and boundary assessments register-class — NOT string-count grep proxy. Row-level reconciliation: §A1 6 rows = 6 boundary assessments (1:1); §A2 7 rows (3 individual + 2 cluster + 2 individual) = 7 boundary assessments (1:1, with cluster rows accommodating multi-instance per single mitigation entry per Item 6 sub-rule + §3.3 operational requirement #6 cluster-format register-precision discipline). 13 row-level boundary assessments cover 20 distinct instances at register-precision. String-count "N=clean" grep across full file returns 16 (13 row-level + 3 summary prose mentions); summary prose mentions are register-class-distinct from log entry register. **Row-level mapping is the load-bearing V#6 invariant; string-count grep proxy method is unreliable and discarded per ChatGPT advisor SEAL pre-fire pushback.**
