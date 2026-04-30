# PHASE2C_9 Step 6 — Sub-spec for case-determination + closeout assembly

**Sub-spec scope**: pre-register §4.4 application framing at
scope-lock + lock §1 verdict + §8 case determination + §9
cross-references and verification structure decisions BEFORE Step 6
fire authors §1 / §8 / §9. Per Step 5 close: Step 6 sub-spec
drafting is its own fire; Step 6 fire is the subsequent session
authoring against the locked sub-spec.

- **Sub-spec drafting date**: 2026-04-29
- **Anchor**: `d548ea2` on `origin/main` (Step 5 sealed)
- **Predecessor**:
  [`PHASE2C_9_PLAN.md`](PHASE2C_9_PLAN.md) at commit `8aa1c66`
  (operational spec; §4.1-§4.4 / §5.6 / §6.2 / §8 verbatim text
  governs)
- **Step 5 evidence-map seal**:
  [`docs/closeout/PHASE2C_9_RESULTS.md`](../closeout/PHASE2C_9_RESULTS.md)
  §7 sealed at `d548ea2`
- **Carry-forward**: Step 5 close advisor primary concern (§4.4
  application register pre-registration) + 4 cumulative
  carry-forward observations + standing instruction codification
  (anchor-prose-access discipline at multi-hundred-line
  interpretive deliverables)

---

## 1. §4.4 application framing — pre-registration at scope-lock

### 1.1 Framing decision

**§4.4 is applied as a MECHANICAL DECISION RULE OVER THRESHOLD
EVALUATIONS at the case-selection layer.** §8 author has **no
discretionary synthesis; bounded comparison only** — threshold
satisfaction is evaluated using descriptive evidence from §7
without introducing new analysis, but threshold language at
§4.1 / §4.2 / §4.3 ("stronger than" / "no disqualifying counter-
evidence") requires bounded comparison evaluation against §7's
already-characterized qualifying-vs-disqualifying register. §8
prose narrates the derivation chain that maps §7 evidence-map
output through §4.1 / §4.2 / §4.3 threshold evaluations + §4.4
multi-case-findings rule to the determination output.

**Two failure modes to avoid** (per dual-reviewer round 1
adjudication):

1. **Fake determinism**: pretending §4.1 / §4.2 / §4.3 thresholds
   are bivalent without authorization for the comparison-boundary
   bounded-judgment they require ("stronger than" comparing
   qualifying vs disqualifying). Pretending the answer is obvious
   when comparison is required is the silent-bias failure.
2. **Accidental synthesis**: making the comparison judgment
   without an explicit evaluation rule, which contradicts the
   mechanical-procedure framing. Re-characterizing §7's
   qualifying-vs-disqualifying balance at §8 instead of inheriting
   §7's characterization is framing (b) leakage.

The §1.X evidence-comparison rule below resolves both failure
modes by authorizing bounded comparison against pre-described
evidence with explicit ambiguity → Case C routing.

Justification (per spec-text reading at PHASE2C_9_PLAN.md §4.4
verbatim):

- §4.4 verbatim text: *"if the evidence base supports multi-case
  findings, the determination is Case C with sub-registers
  documented"* — this is a deterministic rule consuming §7
  evidence-base output, not a heuristic admitting interpretive
  weighting.
- §4.4 reasoning prose: *"Single-case determination + sub-register
  documentation under Case C is the register-precision-preserving
  resolution"* — explicitly names mechanical-procedure as
  register-precision-preserving over interpretive-synthesis.
- §4.1 / §4.2 / §4.3 case-determination criteria use bivalent
  threshold language ("satisfied" / "stronger than" / "no
  disqualifying counter-evidence surfaces"); the §7 evidence map
  sealed at `d548ea2` already characterized qualifying-vs-
  disqualifying register at descriptive register per spec §5.5
  deliverable. §8 reads that characterization and applies the
  threshold rule, not weighs across thresholds.

### 1.2 §8 author responsibilities under framing (a)

§8 author MUST:

1. Read §7 per-sub-register evidence maps (§7.0.1-§7.0.4 / §7.1.1-§7.1.3
   / §7.2.1-§7.2.3) + cross-sub-register summaries (§7.0.5 / §7.1.4
   / §7.2.4) + §7.3 cross-case evidence-base summary
2. **Inherit §7's qualifying-vs-disqualifying characterization
   verbatim**. §8 does NOT re-characterize §7's balance findings;
   §8 reads §7 §X.X cross-sub-register summary tables as the
   canonical characterization input. Re-characterization at §8
   is framing (b) leakage even under nominal framing (a) lock.

   **Verbatim-inheritance scope** (per Flag 1 dual-reviewer round
   2 disposition): §8 cites §7.0.X / §7.1.X / §7.2.X by section
   reference; MAY quote ≤2 sentences per sub-register
   characterization with explicit attribution
   (e.g., *"per §7.0.4 A.4 sub-register characterization: '[verbatim
   quoted text]'"*); MUST NOT paraphrase the characterization
   itself. Paraphrase-creep is re-characterization risk and is
   forbidden under the §1.2 verbatim-inheritance discipline.
   Cross-reference + ≤2-sentence quoted attribution is the
   authorized §8 representation register; longer quotes risk
   converting §8 prose into §7-restatement and lose §8's
   derivation-chain function.
3. For Case A: apply §4.1 determination criterion mechanically
   against §7.0 sub-register evidence per the §1.X evidence-
   comparison rule — *"at least ONE of A.1 / A.2 / A.3 / A.4
   satisfied with concrete evidence ... that meets the qualifying
   criteria; AND no disqualifying counter-evidence surfaces
   stronger than the qualifying evidence; AND the identified
   defect is plausibly addressable"*
4. For Case B: apply §4.2 determination criterion mechanically per
   the §1.X evidence-comparison rule — *"ALL of B.1, B.2, B.3
   satisfied with concrete evidence; AND no disqualifying
   counter-evidence surfaces"*
5. For Case C: apply §4.3 determination criterion mechanically per
   the §1.X evidence-comparison rule — *"any ONE of C.1 / C.2 /
   C.3 applicable; AND closeout document explicitly identifies
   which sub-register (C.1 / C.2 / C.3) the determination falls
   in; AND tracked-fix register entry surfaces the specific
   evidence asymmetry that produced the Case C determination"*
6. Apply §4.4 one-and-only-one rule mechanically: if exactly one
   Case is satisfied → that Case; if multi-case findings (multiple
   Cases satisfied) → Case C per §4.4 multi-case-findings rule;
   if no Case cleanly satisfied at descriptive register but at
   least one Case C sub-register applies → Case C per §4.3 "any
   ONE applicable" criterion.

§8 author MUST NOT:

- **Re-characterize** §7's qualifying-vs-disqualifying evidence at
  the case-selection layer (§7.0.5 / §7.1.4 / §7.2.4 cross-sub-
  register summary tables are the canonical characterizations
  inherited verbatim; §8 does not re-weight)
- **Introduce new analysis, metrics, or interpretation** beyond §7
  descriptions when applying §4.1 / §4.2 / §4.3 threshold language
  per §1.X evidence-comparison rule
- Substitute interpretive synthesis for bounded threshold-comparison
  rule application
- Pre-empt the case selection by §1 verdict prose (§1 verdict
  reports the §8 mechanical-procedure output; it does not perform
  the procedure)
- Add fourth-case-equivalent ("Case A leaning toward C.1" /
  "Case C with strong A.4 component") framings — per §4.4
  one-and-only-one rule, the determination is exactly ONE Case

### 1.3 §8 author residual discretion (downstream of case-selection)

§8 author has bounded discretion at downstream documentation
layers:

1. **Sub-register documentation selection** (under Case A or Case
   C): which A.x or C.x applies given §7 evidence map. This is
   descriptive matching, not interpretive synthesis — the §7
   evidence map at §7.0.5 / §7.2.4 cross-sub-register summary
   tables already lists which sub-registers apply per §7 evidence
   base.
2. **Falsifiability statement composition** (per spec §6.2): Case
   A / Case B / Case C falsifiability statement template per
   spec §6.2; §8 author composes the specific counter-evidence
   description.
3. **Forward-pointer register composition** (per spec §4.4
   allowed-register table): Case A / Case B / Case C row text per
   spec §4.4; §8 author composes against the per-Case allowed-
   register template.
4. **Tracked-fix register entry composition** (per spec §4.3 +
   §6.5 + §7.4 + PHASE2C_8.1 §10 precedent): §8 author surfaces
   tracked-fix entries from §7.4 register-precision observations
   + Step 5 / 6 emergent register-precision findings.
5. **Methodology-codification candidate listing** (per spec
   §3.2.10 follow-up-arc deferral): §8 author lists candidates
   surfaced during PHASE2C_9 work; canonical METHODOLOGY_NOTES
   update is follow-up arc, not §8 territory.
6. **§1.4 verdict-register composition** ("what this arc
   establishes / does not establish"): §8 author composes verdict
   register against §1.0-§1.3 outputs.

### 1.4 Framing falsifiability

This framing decision (mechanical-procedure under §4.4) would be
falsified by spec-text reading surfacing language at §4.4 / §4.1-§4.3
that explicitly authorizes §8 author interpretive synthesis at the
case-selection layer. Per the spec-text reading at sub-spec drafting
register, no such language surfaces; spec text is consistent with
mechanical-procedure framing.

If at Step 6 fire the §8 author encounters a §7 evidence-map output
that does not cleanly map to A / B / C under mechanical-procedure
application, the resolution per spec §4 pre-registration discipline
is "closeout case = Case C + tracked-fix register entry surfacing
the pattern" (per spec §4 verbatim: *"If retrospective evidence
surfaces a case pattern that doesn't fit A/B/C cleanly, the
resolution is closeout case=Case C (ambiguous) + tracked-fix
register entry surfacing the pattern"*), NOT mid-Step-6 framing
revision.

### 1.5 Evidence-comparison rule (required for §4.1 / §4.2 / §4.3 threshold application)

When applying §4.1 / §4.2 / §4.3 threshold language such as
"stronger than" / "no disqualifying counter-evidence" /
"comparable to" / "weaker than" / "satisfied with concrete
evidence", the §8 author evaluation MUST:

1. **Use ONLY evidence explicitly documented in §7.** §7's
   per-sub-register prose at §7.0.1-§7.0.4 / §7.1.1-§7.1.3 /
   §7.2.1-§7.2.3 + cross-sub-register summary tables at §7.0.5 /
   §7.1.4 / §7.2.4 + §7.3 cross-case summary table are the
   canonical inputs.
2. **NOT introduce new analysis, metrics, or interpretation
   beyond §7 descriptions.** Re-reading §3-§6 mechanism or
   observation register to re-characterize §7's qualifying-vs-
   disqualifying balance is forbidden under framing (a). §7 is
   the canonical evidence base; §8 inherits, does not re-derive.
3. **Treat ambiguity or unresolved comparison as: NOT satisfying
   clean qualification criteria.** Where §7 characterizes a
   qualifying-vs-disqualifying balance as "interpretively
   ambiguous at light-touch register" (e.g., §7.0.4 A.4
   sub-register), the §1.X evidence-comparison rule resolves the
   ambiguity by routing to "NOT cleanly satisfied" at the §4.1
   "stronger than" register. Ambiguity does NOT satisfy "no
   disqualifying counter-evidence stronger than qualifying"
   because §7 has not produced the directional comparison that
   "stronger than" requires.

**Implication**: ambiguous or balanced evidence at any §7 sub-
register routes to "Case A.x not cleanly satisfied" (or "Case B.x
not cleanly satisfied"). Combined with §4.4 multi-case-findings
rule, ambiguity at multiple sub-registers routes to Case C
**structurally** rather than as a fallback. Case C is the
**correct mechanical output of ambiguity under the §1.X rule**,
not a default-case escape valve.

**Reading (i) vs Reading (ii) hard-case resolution at §7.0.4 A.4**:

The hard case is §7.0.4 A.4 sub-register's "interpretively
ambiguous balance" finding. Two readings of §4.1 "stronger than"
threshold:

- **Reading (i)**: "stronger than" requires §7 to produce a
  directional comparison. §7 didn't (light-touch register).
  Therefore §4.1 criterion not satisfied at A.4; Case A not
  satisfied at A.4.
- **Reading (ii)**: "stronger than" is one-sided. If disqualifying
  is not stronger than qualifying, §4.1 holds. §7 ambiguity =
  neither stronger nor weaker; therefore disqualifying is not
  stronger than → §4.1 satisfied at A.4.

**Sub-spec resolves: Reading (i) is canonical** per §1.X point 3:
ambiguity does NOT satisfy "stronger than" comparison register
because §7 has not produced the directional comparison that
"stronger than" requires. §4.1 fails at A.4 under §1.X rule.

This resolution is consistent with the spec §4.4 "register-
precision-preserving resolution" framing: ambiguity at light-touch
register routes mechanically to Case C, not to interpretive
synthesis at §8 to disambiguate.

### 1.6 §4.4 application falsifiability (chain-falsifiability)

Per spec §6.2 falsifiability-statement discipline, the case
determination assertion at §1 verdict + §8.0 must include explicit
"what would falsify this conclusion" language. Under framing (a),
the falsifiability statement is **chain-falsifiability**: the
determination would be falsified by changes to the §7 evidence
map characterization that, when fed mechanically through §4.1 /
§4.2 / §4.3 + §4.4 + §1.5 evidence-comparison rule, would produce
a different case determination.

Falsifiability statement structure under framing (a):

- **Case A determination** (if surfaces): *"This determination
  would be falsified by [X counter-evidence] surfacing at
  structured re-examination depth that would, when fed mechanically
  through §4.1 + §4.4 + §1.5 evidence-comparison rule, change the
  §7.0.X sub-register's qualifying-vs-disqualifying characterization
  from 'qualifying stronger than disqualifying' to 'disqualifying
  comparable to or stronger than qualifying'."*
- **Case B determination** (if surfaces): *"This determination
  would be falsified by [Y pattern] surfacing at noise-floor
  consistency checks that would, when fed mechanically through
  §4.2 + §4.4 + §1.5 evidence-comparison rule, change the §7.1
  evidence base from 'all of B.1, B.2, B.3 satisfied' to 'at
  least one of B.1, B.2, B.3 not satisfied'."*
- **Case C determination** (if surfaces): *"This determination
  would be falsified by [Z resolution] of the ambiguity sources
  at deeper retrospective register that would, when fed mechanically
  through §4.1 / §4.2 + §4.4 + §1.5 evidence-comparison rule,
  produce clean satisfaction of Case A or Case B at descriptive
  register without multi-case findings."*

Falsifiability statements at §1 / §8 must be specific (not
gestural): cite specific §7.X.X sub-register + specific
counter-evidence / pattern / resolution mechanism + specific
mechanical-rule pathway producing different determination.

**Per-link-point counterfactual structure** (per Flag 2
dual-reviewer round 2 disposition): chain falsifiability under
framing (a) operates across three link-points; the §1 / §8.0
falsifiability statement MUST surface counterfactuals at each
applicable link-point per the determined Case:

1. **§7 characterization layer link-point**: counterfactual
   evidence at §3-§6 register that, when fed into §7 evidence-map
   construction, would produce a different §7 sub-register
   qualifying-vs-disqualifying characterization (e.g., for Case C
   determination at §7.0.4 A.4: structured re-examination of
   ingest-layer mechanism that would convert §7.0.4 A.4
   "interpretively ambiguous balance" → "qualifying stronger than
   disqualifying" or "disqualifying stronger than qualifying").
2. **§4.1 / §4.2 / §4.3 threshold layer link-point**: counterfactual
   change in threshold-criterion satisfaction at the §1.5
   evidence-comparison rule application register (e.g., for Case
   C determination at §7.0.4 A.4: §1.5 rule 3 ambiguity-routing
   resolution that would, if Reading (ii) were canonical instead
   of Reading (i), produce different §4.1 satisfaction at A.4).
3. **§4.4 multi-case-findings rule layer link-point**: counterfactual
   change in multi-case-findings determination (e.g., for Case C
   determination: if exactly one Case were cleanly satisfied at
   §1 + §2 link-points, the §4.4 rule would not trigger Case C).

§8.0 falsifiability statement enumerates per-link-point
counterfactuals applicable to the determined Case; weakest-link
single-counterfactual framing is NOT authorized under chain
framing per Flag 2 disposition. Each link-point counterfactual
must be specific (not gestural) per §1 / §8.0 specificity
discipline.

PHASE2C_8.1 §1 verdict's integrated-falsifiability-statement
precedent does NOT apply under chain framing; chain requires
explicit per-link-point structure.

---

## 2. §1 Verdict structure lock

Per spec §8 canonical structure §1 sub-section enumeration:

- §1.0 Case determination (A / B / C with sub-register)
- §1.1 Per-case evidence summary
- §1.2 Falsifiability statement
- §1.3 Forward-pointer register (allowed-register only)
- §1.4 Verdict register (what this arc establishes / does not
  establish)

### 2.1 §1.0 Case determination

**Format**: explicit single-Case statement + sub-register if
applicable. Examples:

- "Case A.X — [defect category]" (Case A with sub-register)
- "Case B" (Case B; no sub-register required per spec §4.2)
- "Case C — sub-register C.X applicable; [evidence-asymmetry
  description]" (Case C with sub-register per spec §4.3
  requirement)

**Length**: 1-3 sentences. Mechanical-procedure output reporting,
not synthesis.

### 2.2 §1.1 Per-case evidence summary

**Format**: cite §7 evidence map per sub-register; report
qualifying-evidence + disqualifying-counter-evidence at descriptive
register; cross-reference §7.X.X for full evidence detail.

**Length**: 1-2 paragraphs. Summary register, not re-statement of
§7.

### 2.3 §1.2 Falsifiability statement

**Format**: per spec §6.2 template per Case:

- Case A: *"This determination would be falsified by [X
  counter-evidence] surfacing at structured re-examination depth"*
- Case B: *"This determination would be falsified by [Y pattern]
  surfacing at noise-floor consistency checks"*
- Case C: *"This determination would be falsified by [Z resolution]
  of the ambiguity sources at deeper retrospective register"*

**Composition discipline**: counter-evidence / pattern / resolution
text must be specific, not gestural. "Statistical-significance
machinery would falsify B.2 noise-floor claim" is gestural; "DSR
test on the cohort_a_unfiltered = 1 outcome with marginal-pass-rate
null distribution producing p < 0.05 would falsify B.2 noise-floor-
consistency claim at significance-test register" is specific.

**Length**: 1 paragraph per Case applicable.

### 2.4 §1.3 Forward-pointer register

**Format**: per spec §4.4 allowed-register table per Case;
mechanical composition against the per-Case template.

**Forbidden**: per spec §4.4 + §7.2 forbidden-language register —
no PHASE2C_10 / successor-arc pre-naming; no "next we will run X" /
"this confirms Y is the next arc" / "this requires Z" framing; no
deliberation-register pre-convergence on successor-cycle direction.

**Length**: 1 paragraph; quote the spec §4.4 allowed-register row
text directly + apply to PHASE2C_9 specifics.

### 2.5 §1.4 Verdict register

**Format**: explicit "what this arc establishes" + "what this arc
does not establish" framing. Per spec §3.2 hard scope boundaries +
§9 risks-and-out-of-scope items.

**What PHASE2C_9 ESTABLISHES**:
- §3 mechanism reconstruction at file:line citation register
- §4 artifact-distribution audit at canonical-anchor cross-check
  register
- §5 theme × pass-count cross-tab reproducing PHASE2C_8.1 §7.1
- §6 lone-survivor walkthrough at end-to-end mining-process trace
  register
- §7 evidence maps for Case A.1-A.4 / B.1-B.3 / C.1-C.3
- §8 case determination per §4.4 mechanical-procedure application
- 4 cumulative methodology-codification candidates surfaced for
  follow-up METHODOLOGY_NOTES update arc

**What PHASE2C_9 DOES NOT ESTABLISH**:
- New candidate generation or evaluation outputs (per §3.2.1 +
  §3.2.2)
- Statistical-significance discrimination of noise-floor-vs-
  systematic-pattern (Q-9.A territory; out-of-scope per §3.2.5)
- Calibration-variation grid outputs (Q-9.C territory; out-of-scope
  per §3.2.6)
- Phase 3 progression scoping (Q-9.D territory; out-of-scope per
  §3.2.7)
- Mining-process redesign proposals (out-of-scope per §3.2.4)
- Successor scoping cycle direction (per §4.4 + §7.4 anti-pre-
  naming discipline)
- Ingest-layer mechanism reconstruction (out-of-scope per §3 +
  §7.4 register-precision Obs 2 carry-forward; tracked-fix register
  candidate)

**Length**: 1 paragraph each for establishes / does-not-establish.

---

## 3. §8 Case determination structure lock

Per spec §8 canonical structure §8 sub-section enumeration:

- §8.0 Determination
- §8.1 Sub-register (if Case A or Case C)
- §8.2 Forward-pointer register
- §8.3 Tracked-fix register entries surfaced
- §8.4 Methodology-codification candidates surfaced

### 3.1 §8.0 Determination

**Format**: §1.0 single-Case statement + extended derivation chain
narration showing how §4.4 mechanical procedure was applied to §7
evidence map. Specifically:

1. Quote §7.X cross-sub-register summary tables verbatim (§7.0.5 /
   §7.1.4 / §7.2.4)
2. Quote §4.1 / §4.2 / §4.3 determination criteria verbatim
3. Apply §4.4 mechanical rule against the §7 + §4.1-§4.3 inputs
4. State the determination output

**Discipline**: derivation chain prose only; no interpretive
synthesis at case-selection layer; reproduces the §7 → §4.4 →
determination derivation explicitly so any reviewer can verify
mechanical-procedure application.

**Length**: 2-4 paragraphs.

### 3.2 §8.1 Sub-register documentation

**Required for**: Case A (sub-register A.x) and Case C (sub-register
C.x). NOT required for Case B (per spec §4.2 — Case B has no
sub-register requirement).

**Format**: cite the §7 sub-register evidence map directly; report
qualifying-vs-disqualifying register summary verbatim from §7.X.X
prose.

**Length**: 1-2 paragraphs per applicable sub-register.

### 3.3 §8.2 Forward-pointer register

**Format**: §1.3 forward-pointer register, expanded with explicit
cross-references to spec §4.4 allowed-register table row text.

**Length**: 1-2 paragraphs.

### 3.4 §8.3 Tracked-fix register entries surfaced

**Format**: enumerated list of tracked-fix entries surfaced during
PHASE2C_9 work. Per PHASE2C_8.1 §10 register precedent, tracked-fix
entries appear at §8.3 closeout register; if §10 separate section
emerges per §8 author downstream-documentation discretion (e.g.,
when entry count or entry register justifies separate section), §8.3
+ §10 cross-reference at sub-section header. Default: §8.3 enumerated
list at sub-spec scope.

**Numbering convention (pre-registered at sub-spec scope-lock)**:
**Q-9-N** (PHASE2C_9 arc, sequential N starting from 1). Adapts
PHASE2C_8.1's Q-S4-N pattern (Stage 4 = §4 deliverable cycle of
PHASE2C_8.1) to PHASE2C_9 arc-level register. The "Q-9.B" label is
NOT used (per spec §1 cycle-boundary semantics: PHASE2C_9 = Q-9.B
alone at arc-scope; tracked-fix entries are at PHASE2C_9 arc-scope,
not at sub-cycle Q-9.B-scope).

Each entry:

- Entry ID (Q-9-N format; sequential N starting from 1)
- Description (1-2 sentences)
- Surface origin (Step X §Y.Z carry-forward; or §8 emergent finding)
- Resolution disposition (deferred to follow-up arc / open
  tracked-fix / scope-boundary clarification)

**Mandatory entries from Step 5 carry-forward** (per §7.4
register-precision observations):

1. **Q-9-01 — Ingest-layer mechanism reconstruction as structured
   re-examination scope**: per §7.4 register-precision Obs 2;
   surfaced at §7.0.2 A.2 + §7.0.4 A.4 + §7.2.3 C.3 sub-register
   evidence base; out-of-§3-reconstruction-scope per spec §3.1
   in-scope enumeration; explicit "this is tracked-fix register,
   not pre-named successor-arc" framing per spec §7.2 anti-pre-
   naming discipline. Resolution disposition: deferred to follow-up
   structured re-examination arc (not pre-named).

**Mandatory entries from spec §4.3 Case C requirement** (if Case C
determination):

2. **Q-9-02 — Evidence asymmetry that produced Case C
   determination**: per spec §4.3 *"tracked-fix register entry
   surfaces the specific evidence asymmetry that produced the Case
   C determination"* requirement.

   **Slot-vs-content discipline** (per Concern K dual-reviewer
   round 3 disposition): Q-9-02's *slot* is pre-registered at
   sub-spec scope (entry ID + structure forced by spec §4.3 if
   Case C). Q-9-02's *content* (specific evidence-asymmetry
   description per applicable C.x sub-register; cross-reference to
   §1.5 evidence-comparison rule application that mechanically
   produced Case C output) is §8-author-derived at Step 6 fire,
   NOT pre-staged at sub-spec. Sub-spec pre-registers the
   minimum-content requirement (specific C.x sub-register +
   specific evidence-asymmetry mechanism + §1.5 rule pathway
   citation); §8 author at Step 6 fire authors the content
   against the §7 evidence map freshly per Flag 3 authoring-
   against-§7-fresh discipline (§5.2 Activity 2). Resolution
   disposition: documentation-register; closeout-of-arc completion.

**Optional entries** (per §8 author discretion at downstream
documentation layer):

3. Additional tracked-fix entries surfaced during Step 6
   case-determination derivation (§7 numbering-convention
   observations; cumulative-11 selection-criterion documentation
   pattern; etc.).

**Length**: 3-5 entries typical; 1-2 paragraphs per entry.

### 3.5 §8.4 Methodology-codification candidates surfaced

**Format**: enumerated list per spec §3.2.10 follow-up-arc
deferral. Each candidate:

- Candidate description (1-2 sentences)
- Surface origin (Step X / dual-reviewer cycle / carry-forward
  observation)
- Codification register (§N+ METHODOLOGY_NOTES section candidate)

**Mandatory methodology-codification candidate entries (4
cumulative; not tracked-fix entries — distinct from §3.4 §8.3
register per Concern adjacency-disambiguation)** from Step 5 close
carry-forward:

**Status-register precision** (per Concern L dual-reviewer round 3
disposition): the four candidates are not uniform in status
register; pre-registering status per candidate so §8 author
authors at the right register:

- **operationalized + codification-pending**: discipline already
  operating at advisor register; canonical METHODOLOGY_NOTES
  codification pending follow-up arc
- **observation-only + cross-cycle-pending**: surfaced at
  observation register; cross-cycle accumulation needed before
  codification threshold reached
- **observation-only + codification-candidate**: surfaced at
  observation register; codification candidate at within-cycle
  threshold reached (no cross-cycle accumulation required)

Per-candidate status:

1. **Procedural-confirmation defect class instance #2** at advisor
   register (Step 5 first-commit pattern with "verified on
   record" against own self-resolution); corrected via
   anchor-prose-access discipline standing instruction
   codification.
   **Status**: operationalized (correction operating throughout
   Step 5 follow-up patch + Step 6 sub-spec drafting cycle) +
   codification-pending (canonical METHODOLOGY_NOTES update arc).
2. **Spec-vs-empirical-reality within-cycle count at 3**:
   PHASE2C_10 pre-naming caught at PHASE2C_9 spec drafting + Stage
   2c→Stage 2d attribution patched at Step 2 + 16-char-vs-64-char
   hash spec divergence; cross-cycle accumulation pending.
   **Status**: observation-only + cross-cycle-pending (within-
   cycle count alone below codification threshold; cross-cycle
   accumulation register required to reach threshold).
3. **Cumulative §7 carry-forward register at 11 observations
   stress-tested §7 scope at Step 5**: selection-criterion question
   resolved as "all 11 enter" by spec-silence + inclusion-discipline
   reasoning; documentation pattern reusable for future
   N-observation evidence-mapping deliverables.
   **Status**: observation-only + codification-candidate
   (selection-criterion documentation pattern operationalized at
   §7.0 introduction + §7.0.0 inventory table; reusable pattern
   surfaced; codification candidate within-cycle).
4. **Anchor-prose-access discipline at multi-hundred-line
   interpretive deliverables**: codified standing instruction at
   advisor-anchor register; codification candidate at §16+ scoping
   cycle.
   **Status**: operationalized (standing instruction operating at
   Step 5 follow-up + Step 6 sub-spec drafting cycle; instance
   #1 + instance #2 corrections completed) + codification-pending
   (canonical METHODOLOGY_NOTES §16+ section candidate).

**Optional emergent entries** (Step 6 cycle): any additional
methodology candidates surfaced during §8 / §9 authoring or §6.4
cycle-boundary-preservation language audit at final-commit
register. **Format**: matches the four mandatory entries
(description + surface origin + codification register) per
Concern M acknowledgment carry-forward; emergent entries
authored at §8 closeout-cycle by §8 author; no pre-staging.

**Length**: 4-6 entries typical; 1-2 paragraphs per entry.

---

## 4. §9 Cross-references and verification structure lock

Per spec §8 canonical structure §9 sub-section enumeration:

- §9.0 PHASE2C_9_PLAN.md cross-references
- §9.1 PHASE2C_8.1 canonical anchor cross-references
- §9.2 Verification framework audit (evidence-mapping;
  falsifiability; canonical-number; cycle-boundary language)

### 4.1 §9.0 PHASE2C_9_PLAN.md cross-references

**Format**: enumerated list of PHASE2C_9_PLAN.md sections that
PHASE2C_9_RESULTS.md mirrors or applies; per-section anchor at
section-text register.

**Length**: 1 paragraph or compact table.

### 4.2 §9.1 PHASE2C_8.1 canonical anchor cross-references

**Format**: enumerated list of PHASE2C_8.1 closeout canonical
anchors consumed at PHASE2C_9 evidence base (per spec §2.4); each
anchor anchored at PHASE2C_8.1 closeout section-anchor register.

**Length**: 1 paragraph or compact table.

### 4.3 §9.2 Verification framework audit

**Format**: per spec §6 verification framework — checklist at
final-commit register:

- [ ] §6.1 Evidence-mapping discipline: every claim cited at file:line
  / canonical-anchor / §X-cross-reference register
- [ ] §6.2 Falsifiability-statement discipline: case-determination
  assertion includes "what would falsify this conclusion" language
- [ ] §6.3 Canonical-number cross-checks: §7 / §8 references reproduce
  PHASE2C_8.1 canonical anchors
- [ ] §6.4 Cycle-boundary-preservation language audit: closeout-document
  scope; no PHASE2C_10 / successor-arc pre-naming; no forbidden
  forward-pointer language
- [ ] §6.5 Independent-recompute gate: light-touch register; no new
  canonical numbers requiring test ✓ (PHASE2C_9 produces no new
  numbers)

**Length**: checklist + 1 paragraph audit narrative per item.

---

## 5. Step 6 fire procedure (next session)

### 5.1 Pre-fire prerequisites

- This sub-spec sealed at sub-spec commit (after dual-reviewer pass)
- §7 evidence map sealed at `d548ea2` (Step 5 final state)
- CLAUDE.md Phase Marker advanced Step 5 → Step 6 active (separate
  Phase Marker delta commit before §8 authoring per Step 5 / Step
  6 / etc. precedent)

### 5.2 Step 6 fire activities (sequenced)

**Phase Marker reconciliation events** (two distinct events; per
Concern J pre-registration at sub-spec scope-lock):

- **Event A — Phase Marker advance Step 5 → Step 6 active**: at
  Step 6 fire-start; standalone commit before §8 authoring (mirrors
  Step 1-5 Phase Marker advance precedent at e59cbda / 6351c04 /
  adc65cb / 95d138f / df3901e)
- **Event B — Phase Marker reconciliation Step 6 → PHASE2C_9
  sealed + Completed list update**: at closeout-commit cycle
  (after Step 6 final commit + dual-reviewer pass + tag commit)

Activity sequence:

1. **Event A**: CLAUDE.md Phase Marker advance (Step 5 sealed →
   Step 6 active) standalone commit
2. Apply §4.4 mechanical procedure + §1.5 evidence-comparison rule
   to §7 evidence map per §1 sub-spec; produce Case determination
   at descriptive-derivation register

   **Authoring-against-§7-fresh discipline** (per Flag 3
   dual-reviewer round 2 disposition): §8 author at Step 6 fire
   re-applies the §1.5 evidence-comparison rule against §7 evidence
   map (sealed at `d548ea2`) FRESHLY. Sub-spec drafting cycle's
   sanity-check output (the verification-of-rule-operability
   exercise that produced "Case C with C.1 + C.2 + C.3 sub-registers"
   at sub-spec authoring time) is **NOT copied or referenced** at
   §8 authoring register. §8 prose stands or falls on its own
   §7→§4.1/§4.2/§4.3→§1.5→§4.4 derivation chain composition.
   Sanity-check output may be cross-referenced **post-hoc** at §8
   closeout-prose-audit register (per Activity 10 §6.4 audit cycle)
   to verify rule-application consistency between sub-spec drafting
   and §8 authoring; mismatched outputs at audit register surface
   a tracked-fix entry candidate. Discipline rationale: prevents
   sanity-check-as-§8-derivation-chain leakage, which would convert
   §8 dual-reviewer cadence at Step 6 fire from substantive to
   confirmatory (same defect class as Step 5 first-commit pattern
   "verified on record" against own self-resolution).
3. Author §8.0 Determination (derivation chain narration per §3.1
   sub-spec)
4. Author §8.1 Sub-register documentation (if Case A or Case C
   per §3.2 sub-spec)
5. Author §8.2 Forward-pointer register (per §3.3 sub-spec)
6. Author §8.3 Tracked-fix register entries (per §3.4 sub-spec;
   minimum 1 entry from Q-9-01; Q-9-02 if Case C determination)
7. Author §8.4 Methodology-codification candidates (per §3.5
   sub-spec; minimum 4 entries from Step 5 close cumulative
   carry-forward)
8. Author §1 Verdict (after §8 authored; §1 reports §8 output per
   §2 sub-spec)
9. Author §9 Cross-references and verification audit (per §4
   sub-spec)
10. §6.4 cycle-boundary-preservation language audit at full
    closeout-document scope
11. Dual-reviewer pass per anchor-prose-access discipline standing
    instruction (paste prose excerpts including §1 verdict + §8
    case determination + §9 verification audit; advisor substantive
    pass; THEN commit)
12. Final commit: Step 6 sealed; PHASE2C_9 closeout final
13. **Event B**: CLAUDE.md Phase Marker reconciliation Step 6 →
    PHASE2C_9 sealed + Completed list update standalone commit
14. Tag commit (`phase2c-9-mining-retrospective-v1` candidate;
    naming subject to scope-lock at tagging cycle); push if
    user-authorized

### 5.3 Step 6 fire gating criteria (per spec §5.6 + §6 + §7)

- Case determination per §4.4 mechanical procedure ✓
- §1 / §8 / §9 sub-section structure per spec §8 canonical structure
  ✓
- §6 verification framework checklist ✓
- §7 cycle-boundary preservation language audit at closeout-document
  scope ✓
- Tracked-fix register entries surface §7.4 register-precision
  observations (mandatory minimum 1 entry; per §4.3 Case C if
  applicable mandatory minimum 2 entries) ✓
- Methodology-codification candidates surface 4 cumulative
  carry-forward observations from Step 5 close (mandatory minimum)
  ✓

---

## 6. Sub-spec verification framework

Per anchor-prose-access discipline standing instruction codified at
Step 5 close: this sub-spec is reviewed at substantive register
before sub-spec seal. Sequencing per established dual-reviewer
cadence:

1. Sub-spec drafted (this commit)
2. ChatGPT first-pass adjudication
3. Claude advisor substantive pass at sub-spec scope-lock register
4. Adjudicate per MEMORY.md `feedback_reviewer_suggestion_adjudication.md`
   (reasoned, not bulk-accept)
5. Apply patches + re-verify
6. Sub-spec sealed at sub-spec commit
7. Step 6 fire authorized at next session against locked sub-spec

**Sub-spec scope discipline** (per spec §3 hard scope boundaries
governing PHASE2C_9 arc):

- Sub-spec is documentation register; no new mechanism description
  / artifact audit / cross-tab / lone-survivor analysis
- Sub-spec MUST NOT pre-empt §8 case-selection (§4.4 application is
  mechanical at Step 6 fire against §7 + §4.1-§4.3; sub-spec only
  pre-registers the framing semantics, NOT the case output)
- Sub-spec MUST NOT pre-name PHASE2C_10 / successor-arc per spec
  §7.2 forbidden-language register
- Sub-spec MUST NOT modify spec §4 / §5.6 / §6 / §8 — sub-spec
  applies the spec semantics; spec text is canonical

---

## 7. Cross-references

- PHASE2C_9 Plan:
  [`PHASE2C_9_PLAN.md`](PHASE2C_9_PLAN.md) (commit `8aa1c66`)
- Step 5 evidence-map seal:
  [`docs/closeout/PHASE2C_9_RESULTS.md`](../closeout/PHASE2C_9_RESULTS.md)
  §7 (commit `d548ea2`)
- PHASE2C_9.0 Scoping decision:
  [`PHASE2C_9_SCOPING_DECISION.md`](PHASE2C_9_SCOPING_DECISION.md)
  (commit `3e0c99d`)
- PHASE2C_8.1 closeout (canonical anchor + tracked-fix Q-S4-N
  pattern precedent):
  [`docs/closeout/PHASE2C_8_1_RESULTS.md`](../closeout/PHASE2C_8_1_RESULTS.md)
  (commit `69e9af9`; tag `phase2c-8-1-multi-regime-extended-v1`)
- Methodology corpus:
  [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  (commit `8154e99`; §1-§15 in force)
