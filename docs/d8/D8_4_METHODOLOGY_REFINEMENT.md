# D8.4 Methodology Refinement — Stage 2d Issue Specifications

**Sub-phase:** D8.4.1 (skeleton; per-issue analysis to be populated in
D8.4.2 – D8.4.7).

**Document authority:** `docs/d8/D8_4_SCOPE_LOCK.md`, sealed at commit
`7841a89`, SHA-256
`43f7e09851e86788677af2518379a35a9e5d565de80fff9c66e8a6c4037f8bac`.
All authoring under D8.4.x is bound by that scope lock; any item
outside its scope requires a successor scope-lock amendment, never
silent drift.

**Status:** D8.4 is a **proposal-only methodology phase**. It
diagnoses methodology issues, proposes revision specifications,
records expected behavior changes, and defines validation plans. It
does not implement code changes, edit `expectations.md`, re-run Stage
2d, create new LLM calls, validate fixes, or revise D8.3 bucket
assignments. See scope lock §1, §1.1, §3.2, and §3.3 (Locks A–D).

**Skeleton-only commit notice (D8.4.1).** D8.4.1 is skeleton-only:
no Diagnosis, Root cause, Proposed revision spec, Expected behavior
change, Validation plan, Affected scope, or Issue interaction
content is populated for any issue in this commit. Per-issue analysis
begins in D8.4.2 (Issue 1) and proceeds through D8.4.7 (Issue 6).

---

## 1. Purpose

D8.4 authors per-issue methodology analyses for the six D8.2-sealed
methodology issues catalogued in `docs/d8/D8_3_SCOPE_LOCK.md` §4.3.
For each issue, D8.4 produces a fixed seven-part analysis (Parts 1,
2, 3a, 3b, 4, 5, 6 plus a declared `proposal_confidence` label per
scope lock §5 and §5.1) anchored exclusively to already-sealed Stage
2d evidence — D8.1 cells, D8.2 verdicts, D8.3 master triage rows,
the Stage 2d aggregate JSON, raw payloads, D7a flag outputs, D7b
verbal reasoning, `expectations.md`, and the Stage 2d signoff record.
No new LLM calls, no new backtests, no production code changes.

D8.4 outputs feed:
- **Future Stage 2e or Stage 2d-rerun phase (not yet authorized)** —
  proposed revisions form the candidate slate for downstream
  methodology-implementation work, subject to a fresh authorization
  gate.
- **D8.3 post-D8.4 re-triage (D8.3.6+, not yet authorized)** — once a
  methodology issue is resolved and validated in a later phase, the
  affected `METHOD-QUESTION` rows in the D8.3 master table become
  eligible for re-triage. D8.4 itself never re-buckets.

D8.4 introduces no new verdicts on pre-registered Stage 2d claims.
D8.2 verdicts and D8.3 bucket assignments bind as context, not as
license to revise sealed conclusions.

### 1.1 Load-bearing framings (preserved verbatim from scope lock §1.2)

These items are quintuplication-protected drift risks. Any D8.4.x
authoring that touches them must preserve them as-is:

- **Pos 143 fresh-7 negation.** The fresh-7 literal set is
  `{3, 43, 68, 128, 173, 188, 198}`. Pos 143 is **not** a fresh-7
  literal. Any D8.4 discussion of pos 138 / 143 or the RSI-absent
  vol_regime twins must preserve this negation explicitly.
- **Pos 3 double-duty.** Pos 3 is simultaneously a §6.2.2
  divergence_expected cohort member and a §6.4 fresh-7 PASS
  contributor under opposite directional hypotheses. D8.4 issues 1
  and 2 must acknowledge pos 3's double-duty status; collapsing pos
  3 to a single cohort is a drift defect.
- **D8.3.2c DEFER wording.** Pos 138 / 143 DEFER disposition is
  pinned to "not yet test-retest evaluated against `test_retest_tier`
  artifact form per D8.3 §5.3 dual-anchor", not to "no test-retest
  evidence exists." D8.4 must not silently restate this.

---

## 2. Inputs (anchors mirrored from scope lock §2.2)

### 2.1 Git-committed anchors

| Anchor | Commit | Note |
|---|---|---|
| D8.4 scope lock (this sub-arc's governing document) | `7841a89` | `docs/d8/D8_4_SCOPE_LOCK.md` |
| D8.3 strategy triage doc (final seal) | `0b371cd` | `docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md` |
| D8.3.0 scope lock (reference, binding) | (D8.3.0 commit) | `docs/d8/D8_3_SCOPE_LOCK.md` |
| D8.2 adjudication doc (final) | `cd870c3` | `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` |
| D8.1 notebook (final) | `ac2586b` | `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` |
| D8.0 phase signoff (reference; not amended) | (Stage 2d signoff commit) | `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` |

### 2.2 File SHA anchors (8-anchor byte-match required at every D8.4.x authoring turn)

| File | SHA-256 |
|---|---|
| `docs/d8/D8_4_SCOPE_LOCK.md` | `43f7e09851e86788677af2518379a35a9e5d565de80fff9c66e8a6c4037f8bac` |
| `docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md` | `542c359977c1a19c6e2958b92ad9cb34b47f60606061694e875de91f2cc26b6f` |
| `docs/d8/D8_3_SCOPE_LOCK.md` | `f0a5598b34342fb72277d5b344152e0efd6f05bd918699e880b776ead633439c` |
| `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` | `89d54c9821bb754d17b7085dbe6f344403da5b49824236aa8f1ee301003b4914` |
| `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` |
| `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` |
| `docs/d7_stage2d/stage2d_expectations.md` | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` |
| `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` |

Pre-authoring re-verification of all eight SHAs is mandatory at every
D8.4.x turn (scope lock §6.4). SHA drift halts authoring until the
drift is investigated and either ratified or reverted.

---

## 3. Methodology-Issue Inventory (binding restatement of D8.3 §4.3)

The six D8.4 methodology issues are **exactly** those catalogued in
`docs/d8/D8_3_SCOPE_LOCK.md` §4.3. The list is restated below for
in-document reference; **if this restatement and D8.3 §4.3 ever
diverge, D8.3 §4.3 governs** (scope lock §2.3). No seventh issue may
be added inside D8.4 (Lock D); newly surfaced methodology questions
become forward-pointer items in §5 (synthesis) and §6 (forward
pointers), never in-scope analysis.

| # | Issue | D8.3 §4.3 anchor | One-line summary |
|---|---|---|---|
| 1 | Divergence-label definition audit | §6.2.2 `methodology_followup` | The divergence_expected cohort definition needs an audit against how D7b interprets and labels divergence; row-anchored to the §6.2.2 cohort `{1, 2, 3, 5, 6}`. **Pos 3 carries double-duty status** (§6.2.2 cohort member and §6.4 fresh-7 PASS contributor under opposite directional hypotheses; see §1.1) and must be analyzed as such, not collapsed. |
| 2 | Direction-of-prediction recalibration | §6.2.2 interpretation_tag (`likely_directional_model_misspecification`) | The directional-prediction calibration needs recalibration consistent with the `likely_directional_model_misspecification` interpretation; row-anchored to the same §6.2.2 cohort `{1, 2, 3, 5, 6}`, with **pos 3 double-duty** (§1.1) explicitly preserved. |
| 3 | Lower-tail calibration | §6.3(b) `methodology_followup` | The §6.3(b) lower-tail gate (SVR ≤ 0.30) failed at 26/199 actual vs ≥ 40/199 pre-registered floor with `calibration_shortfall` interpretation; the lower-tail calibration needs revision. Scope-level issue with no row attribution per §5 Part 5 row-attribution rule (scope lock §5). |
| 4 | Joint-shape asymmetric-calibration implications | §6.3 joint `methodology_followup` | The asymmetric upper- vs lower-tail calibration of the joint pre-registered claim has methodology implications requiring an explicit specification; scope-level issue with no row attribution. |
| 5 | Forensic cross-tab methodology / prompt / label discipline | §7 forensic cross-tab `methodology_followup`, §8.4 | The forensic cross-tab construction, the D7b prompt design, and the pre-registered label discipline together produce cell-level methodology questions; cross-tab issue cites cell-level evidence with no row positions. |
| 6 | Documentation drift | §5 methodology recap (expectations.md "6 themes" vs operational 5) | `expectations.md` lists six themes whereas operational pipeline runs five; documentation-only issue with no row attribution. The actual `expectations.md` edit belongs to a later authorized phase, not D8.4 (scope lock §3.2). |

**Issue-count invariant.** Six issues, exactly. No fifth-issue
collapse, no seventh-issue inclusion. This invariant is one of the
acceptance criteria for D8.4 (scope lock §9 #18).

---

## 4. Per-Issue Methodology Analysis (Populated in D8.4.2 – D8.4.7)

Each subsection below uses the fixed seven-part structure mandated by
scope lock §5 (Parts 1, 2, 3a, 3b, 4, 5, 6) plus a declared
`proposal_confidence` label per §5.1. Authoring order matches the §3
inventory enumeration unless ratified otherwise.

Forbidden language inherited from scope lock §5.1: "gut feel",
"seems", "looks like", "probably", "generally speaking". Part 3b
forbidden phrasings additionally exclude past-tense outcome claims
("improved", "fixed", "resolved"), magnitude claims without a paired
Part 4 reference, and constructions implying the revision has
already produced an effect. Required Part 3b pattern: "is intended
to ...", "expected to ...", "the revision targets ...".

`proposal_confidence` is an internal coherence signal only; it is
**not validation evidence** and may not be cited downstream as proof
that a fix works (scope lock §5.1 downstream-citation prohibition).

### 4.1 Issue 1 — Divergence-label definition audit

The §6.2.2 divergence axis gate's `FALSIFIED` outcome (1/5 vs ≥ 4/5)
is diagnosed as a definitional ambiguity in the `divergence_expected`
label, which packages cohort membership, score-threshold expectation,
and directional interpretation into a single label without separating
them. The proposed revision spec calls for a definitional split along
those three components, with a corresponding prompt-scaffold
clarification scoped narrowly to divergence-label interpretation. The
spec is forward-looking, no validation has been performed, and the
recalibration of the directional-interpretation component remains
coupled to Issue 2's scope and is not authored here.

`proposal_confidence`: **medium** — diagnosis-to-spec internal
coherence is anchored to D8.2 §6.2.2's `FALSIFIED` verdict and the
directional inversion observed across `{1, 2, 3, 5, 6}` (four of five
at SVR ≤ 0.15, one at 0.75), and the proposed three-component split
addresses the diagnosed conflation directly. Confidence is not `high`
because (i) the revision spec leaves D7b prompt-scaffold details to a
downstream phase, (ii) no validation has been run, and (iii) Issue 2's
direction-of-prediction recalibration may surface dependencies that
revise the spec. Confidence is not `low` because the diagnosis grounds
in named D8.2 / D8.1 anchors and the revision shape addresses the
diagnosed gap directly. The label reflects diagnosis-to-spec internal
coherence only and is not validation evidence (scope lock §5.1).

#### Part 1 — Diagnosis

D8.2 §6.2.2 records `primary_verdict = FALSIFIED` with
`interpretation_tag = likely_directional_model_misspecification` and
`methodology_followup = D8.4` against the pre-registered claim
(expectations.md L77) that ≥ 4 of 5 UB `divergence_expected` calls
would carry SVR ≥ 0.5. D8.1 cell 10 records the observed result:
1/5 at SVR ≥ 0.5, with per-call SVRs across cohort `{1, 2, 3, 5, 6}`
of 0.00, 0.15, 0.15, 0.15, 0.75 — four positions clustered at
SVR ≤ 0.15 (the extreme low tail), one at 0.75. The shortfall is
structurally directional, not magnitude-only: a calibration-only miss
would scatter across the SVR range, whereas the observed
concentration at SVR ≤ 0.15 inverts the pre-registered direction.

The diagnosis names the L77–85 definition of `divergence_expected` as
the locus of the methodological gap, not the D7b scoring and not the
labelling pipeline. The aggregate-record `universe_b_label` for
`{1, 2, 3, 5, 6}` is mechanically correct against the L77–85 wording;
the labels do what the definition specifies. D7b's interpretation
operates *through* the L77–85 definition (plus the prompt
scaffolding inherited from it), so D7b's contribution to the
`FALSIFIED` outcome cannot be cleanly separated from the definition
itself within D8.4's evidence state.

The specific definitional gap is that L77–85 binds three propositions
into a single label without distinguishing them:

1. **Cohort membership component** — what evidence places a candidate
   in the `divergence_expected` cohort.
2. **Score-threshold expectation component** — what SVR threshold
   outcome the cohort is pre-registered to satisfy
   (`SVR ≥ 0.5` per the L85 operational definition).
3. **Directional interpretation component** — whether the
   pre-registered direction is that `divergence_expected` predicts
   high SVR (the L77 reading) or whether `divergence_expected` is a
   semantic that D7b interprets as predicting *low* SVR (consistent
   with the four-of-five SVR ≤ 0.15 concentration and the
   `likely_directional_model_misspecification` interpretation tag).

The `FALSIFIED` outcome contradicts the conjunction of (2) and (3) as
pre-registered. Whether (1) cohort membership is correctly defined,
whether (2) the score threshold is correctly chosen, and whether (3)
the predicted direction is correctly oriented are three separate
questions that the current label conflates.

#### Part 2 — Root cause

The root cause is **definitional**: the L77–85 packaging of the three
components into a single `divergence_expected` label prevents the
`FALSIFIED` verdict from identifying which component the data
contradicts. Per scope lock §5, this is a definitional gap-type, not
a calibration gap-type (Issues 3 and 4 own calibration), not a
prompt-design gap-type as primary cause (Issue 5 owns prompt and
label discipline at the cell level), and not a documentation
gap-type (Issue 6 owns documentation drift).

Two secondary dependencies are noted but explicitly not claimed as
root causes:

- **Prompt-design dependency.** The D7b prompt scaffolding inherits
  the L77–85 definition's compression of the three components.
  Revising the definition requires a corresponding clarification in
  the prompt scaffold so the critic sees the components distinctly.
  This is a downstream consequence of the definitional fix, not an
  independent root cause; Issue 5 retains the broader prompt and
  label discipline scope, including cell-level methodology questions.
- **Documentation dependency.** The L79–83 rationale invokes Stage
  2b/2c transport without naming which of the three components is
  asserted to transport. Issue 6 retains documentation drift as a
  category; here the dependency is noted only because the
  definitional split surfaces a documentation obligation as a
  downstream consequence.

Issue 1 names the definitional boundary; it does not author the root
causes of Issues 2, 5, or 6.

#### Part 3a — Proposed revision spec

The revision is a definitional edit to expectations.md §6.2.2 that
splits the `divergence_expected` label into the three components
named in Part 1, plus a corresponding clarification in the D7b prompt
scaffold scoped narrowly to divergence-label interpretation. The
revision is **not** a label-taxonomy overhaul, **not** a
scoring-pipeline logic change, and **not** a recalibration of any
existing D7b score axis (recalibration of direction-of-prediction is
Issue 2's scope).

The revised definition is required to specify, at minimum:

1. **Membership criteria.** What evidence (semantic, structural,
   cross-axis) qualifies a candidate for `divergence_expected`,
   stated independently of any score-threshold expectation.
2. **Score-threshold expectation.** What SVR threshold outcome the
   cohort is pre-registered to satisfy, stated as a falsifiable
   numeric gate that does not implicitly assume a direction.
3. **Directional interpretation.** Which way the pre-registered
   direction runs (high-SVR-dominance vs low-SVR-dominance), stated
   explicitly so that a falsified outcome can be attributed to a
   specific direction. Issue 1 names the requirement that this
   component be specified; the recalibration of how D7b's score axes
   adjudicate the direction is **Issue 2's scope**, not Issue 1's.
   The revision spec does not assume that a direction-of-prediction
   score axis already exists in D7b's output orthogonal to SVR;
   Issue 2 is where the recalibrated mapping is authored.
4. **Adjudication mapping.** Which D7b score axis adjudicates the
   score-threshold expectation (SVR for the threshold gate). The
   adjudication of the directional-interpretation component is
   deferred to Issue 2, as above.

The spec is stated at definitional precision: it names *what the
revised definition must specify*, not *which line of expectations.md
to edit*. The actual expectations.md edit and the corresponding
prompt-scaffold patch are downstream-phase work (scope lock §3.2);
they do not happen in D8.4.

#### Part 3b — Expected behavior change

The revision **is intended to** make the cohort-membership,
score-threshold-expectation, and directional-interpretation
components of `divergence_expected` separately falsifiable, so that a
future cohort outcome can attribute a contradiction to a specific
component rather than collapsing it into a single label-level
verdict. The revision **targets** the structural pattern observed in
§6.2.2, where the four-of-five SVR ≤ 0.15 concentration is consistent
with a directional inversion that the current label form cannot
distinguish from a score-threshold shortfall or a membership defect.
The revision **is expected to** make future divergence-axis
adjudications more explicitly attributable by component, conditional
on the revised definition surviving downstream review and validation.

No claim is made here that the revision works, eliminates the
misspecification, resolves the directional ambiguity, or improves D7b
performance. Whether the revision produces the intended separation is
for a later validation phase to determine.

#### Part 4 — Validation plan

Validation does not happen in D8.4. D8.4.2 specifies the validation
form only.

The primary candidate validation form is a labelled-audit replay: the
revised three-component definition is applied to the original
`divergence_expected` cohort `{1, 2, 3, 5, 6}` against a frozen copy
of the Stage 2d candidate set and aggregate metadata, with each
cohort member's outcome attributed to the cohort-membership
component, the score-threshold component, or the
directional-interpretation component under the revised definition.
The replay is a future validation procedure; it is not a retroactive
reinterpretation of D8.2's `FALSIFIED` verdict.

A secondary candidate validation form is a synthetic sanity check:
hand-constructed candidates with known divergence semantics, scored
against the revised definition, to confirm that the three components
behave as the spec intends.

**Necessary condition.** The revised definition can be applied to the
five cohort members without ambiguity, with each member's outcome
attributable to a single named component (or to a named combination,
if the components interact).

**Sufficient condition.** Across a future fire under the revised
definition, the cohort outcome is falsifiable per-component, and a
contradiction can be attributed to a specific component without
requiring post-hoc reconstruction.

The necessary condition is the minimum bar for the revision to be
adopted in any downstream phase; the sufficient condition is the
minimum bar for the revision to be considered validated.

#### Part 5 — Affected rows or scope-level impact

Row attribution: cohort `{1, 2, 3, 5, 6}` exactly, per scope lock §5
Part 5 row-attribution rule. No expansion, no contraction.

**Pos 3 double-duty** (per scope lock §1.2 and §1.1 of this
document). Pos 3 is simultaneously a §6.2.2 divergence-cohort member
(low SVR contributing to the `FALSIFIED` verdict under the
pre-registered high-SVR directional hypothesis) and a §6.4 fresh-7
PASS contributor (low SVR satisfying the PASS gate under the
opposite directional hypothesis). The two roles attach the same
SVR = 0.15 observation to **opposite directional hypotheses**; they
are **not resolvable inside Issue 1 alone** and must remain
**explicitly separated** as competing cohort-level observations under
different directional hypotheses. Issue 1's definitional split
clarifies the label boundary and creates the structural conditions
under which the two hypotheses can be named independently, but the
interpretive resolution of pos 3's double-duty remains coupled to
Issue 2's direction-of-prediction recalibration and to D8.4
synthesis. Issue 1 must not collapse pos 3 into a single-hypothesis
framing.

This restatement is the second site of pos 3 double-duty under the
≥ 2-site preservation floor stipulated in §1.1 (the first site is
§1.1 itself; this is the second).

Pos 138 and pos 143 are not cited under Issue 1: the divergence-label
definition audit does not materially touch RSI-absent vol_regime
test-retest framing, and the §5 Part 5 row-attribution rule restricts
pos 138 / 143 citation to issues that materially touch that framing.
The pos 143 fresh-7 negation restatement obligation does not activate
in §4.1.

#### Part 6 — Issue interaction check

**Upstream dependencies.** None. Issue 1's definitional split is
upstream of every other issue it interacts with; no other issue's
revision is a prerequisite for Issue 1's spec.

**Downstream dependencies.** Issue 1 interacts directly with
**Issue 2 (Direction-of-prediction recalibration)**: the same
five-position cohort `{1, 2, 3, 5, 6}` underlies both, and Issue 2's
recalibration consumes the directional-interpretation component that
Issue 1's revision spec requires the definition to specify.
**D8.4.2 does not solve Issue 2.** This is a cross-reference only;
no joint fix is proposed and no merged analysis is performed.
Issue 2's authoring is deferred to D8.4.3.

Issue 1 interacts indirectly with **Issue 5 (Forensic cross-tab /
prompt / label discipline)** via the prompt-design surface: the
L77–85 definition and the D7b prompt scaffolding share the same
definitional boundary, so Issue 1's revision spec includes a
prompt-scaffold clarification scoped narrowly to divergence-label
interpretation. The broader prompt-discipline scope, including
cell-level methodology questions, remains Issue 5's scope; Issue 1's
prompt-scaffold clarification does not assume or pre-empt Issue 5.

**Conflicts.** No conflicts are anticipated between Issue 1's
revision spec and the anticipated revisions for Issues 3, 4, or 6,
which operate on calibration, joint-shape, and documentation planes
respectively. The dependency direction Issue 1 → Issues 2 / 5 is
clean; the dependency direction Issue 1 ↔ Issues 3 / 4 / 6 is empty
in either direction at D8.4.2's evidence state.

---

### 4.2 Issue 2 — Direction-of-prediction recalibration

Issue 2 authors a methodology proposal addressing the
direction-of-prediction recalibration gap surfaced by D8.2 §6.2.2's
`likely_directional_model_misspecification` interpretation_tag. Where
Issue 1 (D8.4.2) names the definitional boundary by splitting the
`divergence_expected` label into cohort-membership,
score-threshold-expectation, and directional-interpretation
components, Issue 2 operationalizes the directional-interpretation
component into a D7b output mechanism. Issue 2 consumes Issue 1's
three-component split as upstream input; it does not re-author the
split. The scope of Issue 2 is the specification of how D7b's
score-axis structure should carry direction-of-prediction
information, given that Issue 1 defers the choice of D7b axis to this
issue.

`proposal_confidence`: **medium-low**. The diagnosis-to-spec internal
coherence holds: D8.2 §6.2.2's verdict and interpretation_tag bind
the diagnostic target to direction-of-prediction misspecification,
and the revision spec names the structural mechanism (an explicit
direction-of-prediction adjudication surface on D7b) that would carry
direction information separable from SVR. But revision shape
selection has irreducible spec-level uncertainty: multiple candidate
shapes (new output field; composite rule over existing axes;
prompt-scaffold change) are internally coherent, and D7b's production
output schema is downstream of D8.4 scope, so the revision is
spec-only with higher downstream-uncertainty than Issue 1's
definitional split. The label is calibrated as `medium-low` rather
than `medium` to flag this honestly without drifting toward
`low`-territory, where the diagnosis itself would have to be in
question. The label reflects diagnosis-to-spec internal coherence
only and is not validation evidence (scope lock §5.1).

#### Part 1 — Diagnosis

The direction-of-prediction misspecification surfaced by D8.2 §6.2.2
is a structural absence, not a calibration error. D8.2 §6.2.2's
primary verdict is `FALSIFIED` for the divergence_expected cohort:
1/5 PASS at SVR ≥ 0.5 against a pre-registered floor of ≥ 4/5, with
per-call SVRs `pos 1 = 0.00`, `pos 2 = 0.15`, `pos 3 = 0.15`,
`pos 5 = 0.15`, and `pos 6 = 0.75`. The §6.2.2 interpretation_tag
attached to this verdict is `likely_directional_model_misspecification`,
which binds the diagnostic gap-type to direction-of-prediction
rather than to score-threshold calibration alone.

Issue 2's diagnostic scope is distinct from Issue 1's. Issue 1
diagnosed the L77–85 label conflation (the definitional gap that
allows three components — cohort membership, score-threshold
expectation, and directional interpretation — to be collapsed into a
single label). Issue 2 diagnoses **how D7b's score-axis structure
fails to carry a direction-of-prediction signal orthogonal to SVR**.
The label conflation is upstream context for Issue 2; the score-axis
structural absence is the Issue 2 target.

The structural absence is observable in two layers. At the
**output-schema layer**, D7b's three scoring axes
(`structural_variant_risk`, `semantic_theme_alignment`,
`semantic_plausibility`) are all magnitude-only fields on the `[0, 1]`
interval; none carries a sign or direction structure that could
distinguish a `predicts_high_SVR` claim from a `predicts_low_SVR`
claim. At the **elicitation layer**, the D7b prompt template does
not ask the critic to commit to a direction-of-prediction; the
prompt's reasoning surface treats direction as implicit context
rather than as a scoring target.

The four-of-five SVR ≤ 0.15 concentration observed in the §6.2.2
cohort is consistent with directional inversion of the
pre-registered claim, as Issue 1 noted. A calibration-only miss
would scatter across the SVR range, whereas the observed
concentration at SVR ≤ 0.15 inverts the pre-registered direction. But
the current methodology cannot **attribute** the observed pattern to
directional inversion specifically: a candidate at SVR = 0.15 could
indicate (a) cohort-membership defect, (b) score-threshold shortfall
under the pre-registered direction, or (c) directional inversion. The
Issue 1 three-component split surfaces the conflation; Issue 2
diagnoses the absence of a D7b mechanism that would let the
methodology adjudicate among (a)/(b)/(c) given the same SVR
observation.

The pos 3 observation in D8.2 §6.4 corroborates the diagnostic claim
at the per-row level. Pos 3 at SVR = 0.15 contributes to the §6.2.2
cohort under one directional hypothesis (FALSIFIED) and contributes
to the §6.4 fresh-7 PASS under the opposite directional hypothesis.
The same SVR observation supports opposite directional readings under
the current methodology, with no D7b output surface that
distinguishes them. This is the per-row signature of the
output-schema absence.

#### Part 2 — Root cause

The Issue 2 root cause is named as a **prompt-design** gap-type per
scope lock §5, with **calibration** as a secondary downstream
consequence. D7b does not output direction because the prompt does
not elicit it; the absence at the output-schema layer is downstream
of the absence at the elicitation layer. If the prompt asked for
direction (whether as an explicit field or via a structured
reasoning-step schema), the calibration question — how D7b's
direction expression maps to SVR-bearing cohort adjudication — would
be the next problem, but it is not the current problem.

The calibration component is secondary, not co-primary. Even with a
direction signal in D7b's output, mapping the direction expression
to the §6.2.2 cohort verdict requires a calibration spec (specifically,
the joint-rule shape that combines direction with SVR threshold at
adjudication time). This is a downstream consequence of the
elicitation gap closing, not an independent root cause. Naming both
as co-primary would conflate two distinct gap-types and violate
scope lock §5's distinct-attribution requirement.

The gap-type attribution carves cleanly against adjacent issues. The
**definitional gap-type** (label conflation at L77–85) is Issue 1's
scope; Issue 2 inherits the definitional split as input but does
not re-author it. The **broader prompt-discipline scope** (cell-level
methodology, theme-taxonomy alignment, label-mention consistency
across the full taxonomy) is Issue 5's scope; Issue 2's prompt-design
touch is narrowly scoped to direction-of-prediction elicitation only.
The **lower-tail calibration gap** (the §6.3(b) `calibration_shortfall`
at 26/199 actual vs ≥ 40/199 floor) is Issue 3's scope; Issue 2's
secondary calibration component does not pre-empt Issue 3's
calibration analysis.

#### Part 3a — Proposed revision spec

The revision specifies that D7b's methodology must carry an
**explicit direction-of-prediction adjudication surface**. The
preferred shape is a new D7b output field paired with definition and
mapping; equivalent structured alternatives that expose a
machine-checkable direction surface remain admissible. The revision
does not assume D7b currently has such a surface; the requirement is
forward-looking, not a re-discovery of an existing axis.

**Revision spec (four points):**

1. **Explicit direction-of-prediction adjudication surface on D7b.**
   The methodology requires D7b's output to expose a direction signal
   that is machine-checkable and structurally separable from
   magnitude. The likely implementation shape is a new D7b output
   field carrying direction information; equivalent structured
   alternatives remain admissible if they expose a machine-checkable
   direction surface. The structural requirement is that direction
   information must be **separable from magnitude**: a downstream
   adjudicator must be able to read direction from the output without
   inferring it from SVR or from any other magnitude axis. One
   example of a value space satisfying this requirement is the
   discrete set `{predicts_high_SVR, predicts_low_SVR,
   no_direction_claimed}`; continuous signed forms or other
   structured encodings that carry direction separable from magnitude
   are also admissible. The spec does not lock the value-space form;
   it locks the structural property.
2. **Mapping to Issue 1's three-component split.** The new direction
   surface carries Issue 1's *directional-interpretation component*
   exclusively. Cohort membership and score-threshold expectation
   remain on existing surfaces (cohort assignment for membership;
   SVR threshold rule for score-threshold expectation). The mapping
   makes Issue 1's three-component split implementable: each
   component has a designated D7b surface, and a contradiction
   between cohort outcome and pre-registered direction can be
   attributed to the relevant component.
3. **D7b prompt elicitation requirement.** The D7b prompt must
   explicitly elicit direction-of-prediction at the scoring step.
   Scaffold form (a chain-of-thought field, a structured
   reasoning-step schema, or a direct declarative field) is left to
   downstream implementation; the spec-level requirement is that
   elicitation be present, so the new direction surface has substance
   rather than being a structurally empty field. The elicitation
   touch is narrowly scoped to direction-of-prediction; broader
   prompt-discipline questions remain Issue 5's scope.
4. **Adjudication mapping requirement.** The `divergence_expected`
   cohort verdict is computed against the direction surface
   **jointly** with SVR threshold, not against SVR alone. The
   spec-level requirement is that the joint-rule form be specified;
   the precise calibrated mapping (which combinations of direction
   and SVR threshold produce PASS vs FAIL) is part of the secondary
   calibration follow-up rather than part of Issue 2's spec.

**The revision spec does not:**

- Pretend that D7b currently has a direction-of-prediction axis. The
  surface is a future requirement, not a re-discovered existing
  output.
- Specify the value-space form (discrete vs continuous, categorical
  vs ordinal). The example `{predicts_high_SVR, predicts_low_SVR,
  no_direction_claimed}` is illustrative; the structural requirement
  is direction-separable-from-magnitude.
- Author the D7b prompt revision itself. The elicitation requirement
  is named at the spec level; prompt-discipline authoring is Issue 5.
- Modify D7b production code, prompt templates, or output schemas.
  D7b is downstream of D8.4 scope; D8.4 produces methodology specs
  only.
- Specify the calibrated joint-rule mapping at adjudication time.
  Point 4 names the joint-rule shape requirement; the calibrated
  mapping itself is downstream of Issue 2 (secondary calibration
  component).

The revision spec closes against Issue 1's open spec point cleanly:
Issue 1's Part 3a "Adjudication mapping" point 4 required that the
methodology specify which D7b axis carries direction-of-prediction.
Issue 2's revision shape (explicit direction-of-prediction
adjudication surface, likely a new field) satisfies that requirement
as an explicit named surface, not as a derived composite rule. The
dependency direction Issue 1 → Issue 2 is closed: Issue 1 specifies
the requirement that direction must be specified; Issue 2 picks the
mechanism that specifies it.

The revision spec names what the revised methodology must specify
(an explicit direction-of-prediction adjudication surface, a mapping
to the three-component split, an elicitation requirement, and a
joint-rule shape requirement). It does not name implementation
files, prompt-template line numbers, output-schema field names in
production code, or production-code edits.

#### Part 3b — Expected behavior change

The revision **is intended to** make direction-of-prediction
adjudicable as a distinct output of the D7b methodology, so that
future divergence-axis cohort outcomes can be attributed to direction
independent of SVR threshold and cohort membership. The revision
**targets** the structural absence diagnosed in Part 1 — that D7b's
current three-axis output cannot carry a direction signal separable
from magnitude. The revision **is expected to** make future cohort
verdicts decomposable along the direction axis, conditional on the
revised D7b output structure surviving downstream design review and
validation.

The forward-looking behavior is stated as a structural attribute of
the future methodology's output surface ("decomposable along the
direction axis"), not as an outcome-quality claim. The revision does
not eliminate the directional ambiguity, correct the
misspecification, resolve pos 3's double-duty, or improve D7b
performance. No claim is made that the revised methodology would
produce a different verdict on the D8.2 cohort. Whether the revision
produces the intended structural separation is established only by
the validation procedure specified in Part 4, not by Part 3b's
forward-looking statement.

D8.2's `FALSIFIED` verdict stands at its evidence state; the revision
is forward-looking only and does not retroactively recharacterize
the D8.2 adjudication. The Part 3b forward-looking phrasing names a
structural attribute the revised methodology *would expose*; it does
not claim the D8.2 cohort *would have passed* under the revised
methodology, and it does not claim the D8.2 verdict was incorrect at
its evidence state.

#### Part 4 — Validation plan

Validation does not happen in D8.4. D8.4.3 specifies the validation
form only; the validation procedure executes downstream, at the
phase where the revised D7b methodology is implemented and exercised
against an evidence set.

**Necessary validation form: synthetic sanity check.** Hand-construct
candidates with known directional semantics — some pre-engineered
to predict high SVR, some to predict low SVR, some directionally
agnostic — and process them through the revised D7b prompt + new
direction surface. The necessary condition is that the new
direction surface's distribution distinguishes the three categories.
This is a structural validation of the elicitation surface itself,
not a cohort-level claim. Without this check, an absent direction
signal in any subsequent re-fire could indicate either a methodology
failure or a cohort-level property, with no way to discriminate.

**Sufficient validation form (conditional on the synthetic check):
re-fire aggregate under revised D7b spec.** A frozen copy of the
Stage 2d candidate set and aggregate metadata, with the D7b layer
only re-fired under the revised prompt and the new direction
surface. The sufficient condition is that per-axis attribution
surfaces direction as separable from SVR threshold — that the
divergence_expected cohort under the recalibrated methodology can
be adjudicated with direction attributed to the new surface and
score-threshold expectation attributed to SVR independently.

The synthetic sanity check is necessary; the re-fire is sufficient
for downstream methodology adoption only if the synthetic check
passes. Necessary and sufficient conditions are distinct and both
must be specified for the validation plan to be complete.

The re-fire is a future validation procedure for the recalibrated
methodology; it is not a retroactive reinterpretation of D8.2's
`FALSIFIED` verdict. D8.2's adjudication stands at its evidence
state. The frozen copy of the Stage 2d candidate set and aggregate
metadata is preserved as input to a forward-looking validation; the
D8.2 adjudication record is not modified.

The validation plan does not establish: that the revised methodology
produces a different verdict on the D8.2 cohort; that pos 3's
double-duty is resolved by the revision; that the recalibrated
direction-of-prediction is correctly mapped to cohort outcomes (the
calibrated joint-rule mapping is downstream of Issue 2's spec).
Validation establishes only that the revised methodology produces a
machine-checkable direction surface separable from magnitude.

#### Part 5 — Affected rows or scope-level impact

Row attribution: cohort `{1, 2, 3, 5, 6}` per scope lock §5 Part 5.
Identical to Issue 1's row attribution. No expansion; no contraction.
Issue 2 is a row-anchored issue under the §5 Part 5 row-attribution
rule.

**Pos 3 double-duty restatement (third preservation site after §1.1
and §4.1 Part 5; the ≥2-site preservation floor declared by scope
lock §1.2 is satisfied).** Pos 3 contributes to the §6.2.2 cohort
under the high-SVR-expected directional hypothesis and contributes to
the §6.4 fresh-7 PASS observation under the opposite directional
hypothesis. The same SVR = 0.15 observation attaches to **opposite
directional hypotheses** under the two roles.

Issue 2 recalibrates the *direction-of-prediction component* of the
`divergence_expected` label per the three-component split surfaced
by Issue 1. This recalibration **does not adjudicate** which of pos
3's two directional hypotheses is correct. The two hypotheses remain
explicitly separated under the revised methodology. Adjudication
between them requires test-retest evidence under the recalibrated
methodology or new evidence outside the Stage 2d candidate set, both
of which are out of scope for D8.4.

**Forbidden framings (literal negative list, not paraphrased):**

- "Issue 2 resolves pos 3's double-duty by picking one direction."
- "The recalibrated methodology selects between the two
  hypotheses."
- "Pos 3's directional ambiguity is closed by the revision."

Each of these phrasings would collapse the pos 3 double-duty by
asserting that Issue 2's revision picks one of the two directional
hypotheses over the other. Scope lock §1.2 declares the double-duty
a preservation obligation; Issue 2's recalibration of the directional
interpretation component does not, and structurally cannot,
adjudicate pos 3's competing hypotheses without test-retest or new
evidence. The forbidden framings are listed literally so that any
future editor scanning for them can verify they do not appear in the
authored prose.

Pos 138 and pos 143 are not cited under Issue 2: direction-of-prediction
recalibration does not materially touch RSI-absent vol_regime
test-retest framing, and the §5 Part 5 row-attribution rule restricts
pos 138 / 143 citation to issues that materially touch that framing.
The pos 143 fresh-7 negation restatement obligation does not activate
in §4.2.

The scope-level impact: Issue 2's revision does not change which
rows are in scope for the divergence_expected cohort; positions 1,
2, 3, 5, and 6 remain the affected rows. The revision changes how a
future re-fire would *adjudicate* the direction-of-prediction
attached to those rows, not which rows are adjudicated.

#### Part 6 — Issue interaction check

**Upstream dependencies.** Issue 2 is downstream of **Issue 1
(Divergence-label definition audit)**. Issue 2 consumes Issue 1's
*directional-interpretation component* from the three-component split
as its diagnostic substrate; Part 3a point 2 cites this consumption
explicitly. Issue 2 operationalizes one of Issue 1's three components
into a D7b mechanism; it does not re-author the definitional boundary
Issue 1 establishes. **D8.4.3 does not re-author Issue 1.** The
three-component split, the L77–85 label-conflation diagnosis, and
the definitional gap-type attribution remain Issue 1's scope. The
dependency direction Issue 1 → Issue 2 is the first cross-issue
dependency in the D8.4 arc and is closed by Issue 2's revision shape
pick.

**Downstream dependencies.** Issue 2 has potential downstream
interactions with **Issue 3 (Lower-tail calibration)** and **Issue 4
(Joint-shape asymmetric-calibration implications)**. The mechanism
in both cases is the joint-rule requirement (Issue 2 Part 3a point
4): if the recalibrated joint rule (combining direction with SVR
threshold) changes which candidates fall into the §6.3(b) lower tail,
the lower-tail count is a function of the joint rule rather than of
SVR alone. This may mechanically change both the lower-tail calibration
analysis (Issue 3) and the joint-shape asymmetric calibration analysis
(Issue 4). At D8.4.3's evidence state, the interaction is **potential,
not claimed**: Issue 3's authoring (D8.4.4) and Issue 4's authoring
(D8.4.5) will assess whether the joint rule materially changes their
respective scopes. Issue 2 surfaces the interaction; it does not
resolve it.

Issue 2 has an indirect downstream interaction with **Issue 5
(Forensic cross-tab methodology / prompt / label discipline)** via
the prompt elicitation requirement (Part 3a point 3). Issue 2's
prompt-design touch is narrowly scoped to direction-of-prediction
elicitation only; the broader prompt-discipline scope remains Issue
5's. The dependency is indirect: Issue 5's authoring may incorporate
Issue 2's elicitation requirement as a constraint, but Issue 2 does
not pre-empt Issue 5's scope.

**Conflicts at D8.4.3's evidence state.** None observed.
Specifically, the cross-spec coherence check between Issue 1 and
Issue 2 holds: Issue 1's Part 3a "Adjudication mapping" point 4
required that the methodology specify which D7b axis carries
direction-of-prediction; Issue 2's revision shape (explicit
direction-of-prediction adjudication surface, likely a new D7b
output field) satisfies this requirement as an explicit named
surface. Issue 1's Part 5 row attribution `{1, 2, 3, 5, 6}` and pos
3 double-duty preservation framing are identical to Issue 2's Part
5 framing.

**Foreseeable conflicts at D8.4.4+.** If Issue 3's lower-tail
recalibration produces a count or threshold framing that contradicts
Issue 2's joint-rule shape requirement (Part 3a point 4), the
conflict surfaces in D8.4.4 Part 6 or in §5 Synthesis. Similarly, if
Issue 4's joint-shape asymmetric calibration analysis contradicts
the joint-rule shape requirement, the conflict surfaces in D8.4.5
Part 6 or in §5 Synthesis. D8.4.3 surfaces the *potential* for these
conflicts at the joint-rule mechanism; it does not resolve them. The
epistemic-humility qualifier "at D8.4.3's evidence state" applies to
both the no-conflict-observed claim and the foreseeable-conflict
notice.

---

### 4.3 Issue 3 — Lower-tail calibration

Issue 3 authors a methodology proposal addressing the lower-tail
prevalence floor-calibration gap surfaced by D8.2 §6.3(b)'s
`calibration_shortfall` interpretation tag. The §6.3(b) gate asks
whether the model produces enough low-SVR observations to populate
the distribution's lower tail at the pre-registered prevalence floor;
the gate failed at 26 / 199 observed against a pre-registered floor of
≥ 30 / 199, a shortfall of −4. The diagnostic target of Issue 3 is
the floor-calibration methodology that produced the ≥ 30 / 199 figure
at pre-registration time, not the SVR ≤ 0.30 cut-point itself (whose
documented derivation in `expectations.md` L105–107 is not in
question). Issue 3 is a scope-level issue per scope lock §5 Part 5;
no row-attribution citations appear in the analysis, and the
composition observation in D8.2 §6.3(b) detailed record (22 neutral,
4 divergence_expected; L459–461) is recorded as composition fact, not
as row-attribution evidence for Issue 3.

`proposal_confidence`: **medium**. The diagnosis-to-spec internal
coherence holds: the §6.3(b) detailed-record numerics
(L444 / L446 / L453 / L455 / L457) bind the diagnostic target to the
lower-tail prevalence floor with `calibration_shortfall` as the
interpretation tag (L467), and the revision spec names a structural
mechanism (re-derive future floors under an explicitly specified
calibration model and specify the pre-registration methodology that
produced them) that addresses the diagnosed gap. The shortfall is
**modest** — 26 / 199 against a ≥ 30 / 199 floor is −4 in absolute
terms, ~2 percentage points on the 199-position denominator, and
~13% relative to the floor itself; the observed magnitude does not
support the rhetorical force of "the floor was substantially
overestimated", and the diagnosis is accordingly framed as a
methodology under-specification rather than a large overestimation.
The proposal is forward-looking only and is not validated, and the
choice between point-floor and interval-floor form is a downstream
design question. The label is calibrated to `medium` to reflect
internal coherence under a modest-magnitude observed miss; it is not
validation evidence and MUST NOT be cited as proof that the proposed
methodology works (scope lock §5.1, strict semantics).

#### Part 1 — Diagnosis

The §6.3(b) lower-tail prevalence floor was not upheld by Stage 2d
evidence at its calibrated level. D8.2 §6.3(b) detailed record
(L444 / L446 / L453 / L455 / L457 / L467) records the pre-registered
claim verbatim from `expectations.md` L100 ("≥ 30 have SVR ≤ 0.30"),
with operational definition `count(call.svr <= 0.30) over {all 199 UB
calls} >= 30`, observed numerator 26, observed ratio 26 / 199, and
shortfall vs threshold −4. The interpretation tag attached at L467
is `calibration_shortfall`. Cross-anchored to
`expectations.md` L100 ("Of all 199 UB calls, **≥ 30 have SVR ≤
0.30** (lower tail).") and `expectations.md` L107 ("The ≥ 30 / 199
lower bound is …").

**Diagnostic target.** The diagnostic target is the
floor-calibration methodology that produced the ≥ 30 / 199 figure at
pre-registration. The SVR ≤ 0.30 cut-point itself is documented at
`expectations.md` L105–107 with a neutral-stratum-share rationale and
is not the diagnostic target. The pre-registered floor was not upheld
at its calibrated level under Stage 2d evidence; D8.4.4 does not
retroactively label the floor wrong, does not retroactively label
D8.2's `FAIL` verdict wrong, and does not claim a different floor
would have produced a `PASS` on the Stage 2d cohort.

D8.2's `FAIL` verdict and `calibration_shortfall` interpretation tag
stand at their evidence state.

**Numeric-anchor drift note (five-point structured).** A drift
between D8.2's per-claim detailed adjudication and its later summary /
appendix presentations was surfaced during D8.4.4 pre-authoring
cross-check and independently confirmed by a Codex read-only
verification pass. The five points below record the discovery, the
inherited drift sites in D8.4 itself, the anchor decision adopted by
D8.4.4, the scope discipline that governs the surfacing, and the
forward pointer for a post-D8 documentation-correction sub-phase.

1. **Discovery.** D8.2 has internal numeric drift between its
   §6.3(b) detailed record (≥ 30 / 199 floor, shortfall −4;
   L444 / L446 / L453 / L457) and its later §9 / appendix summary
   presentations (≥ 40 / 199 floor; L1043 row 4, L1073, L1228).
   Codex independent verification (read-only) confirmed the
   §6.3(b) discrepancy and surfaced three additional drifts of the
   same class in §6.2.1, §6.3(a), and §6.3 joint (catalogued at
   §4.3 Part 6 forward pointer below).
2. **Inherited drift sites in D8.4.** [`docs/d8/D8_4_METHODOLOGY_REFINEMENT.md:121`](D8_4_METHODOLOGY_REFINEMENT.md#L121)
   (D8.4.1 §3 inventory, sealed at commit `eaf8d63`) and
   [`docs/d8/D8_4_METHODOLOGY_REFINEMENT.md:529`](D8_4_METHODOLOGY_REFINEMENT.md#L529)
   (D8.4.3 §4.2 Part 2 cross-reference, sealed at commit
   `95109f7`) carry the drifted ≥ 40 / 199 anchor by inheritance
   from D8.2 §9.1 row 4 (L1043). The D8.4.1 inventory and D8.4.3
   cross-reference both stand at their evidence state per scope
   lock §10 immutability and are not edited by D8.4.4.
3. **Anchor decision.** D8.4.4 §4.3 anchors every numeric to D8.2
   §6.3(b) detailed record (L444 / L446 / L453 / L455 / L457 / L467)
   and `expectations.md` L100 / L107. Pre-registered floor:
   ≥ 30 / 199. Observed: 26 / 199. Shortfall: −4. Interpretation tag:
   `calibration_shortfall`. This is consumption of the per-claim
   authoritative source per D8.4 scope lock §1, not re-adjudication
   of D8.2's verdict.
4. **Scope discipline.** Prior sealed sites (D8.4.1 inventory,
   D8.4.3 §4.2 Part 2 cross-reference) stand at their evidence state
   per D8.4 scope lock §10 immutability; D8.4 does not edit D8.2
   internal text per scope lock §3.2 ("No edits to D8.0, D8.1, D8.2,
   or D8.3 artifacts"). The drift is observed-and-surfaced, not
   edited. D8.2's `FAIL` verdict and `calibration_shortfall`
   interpretation tag stand at their evidence state.
5. **Forward pointer.** The four-drift family (§6.2.1 floor,
   §6.3(a) floor, §6.3(b) floor, §6.3 joint verdict tag) is
   catalogued at §4.3 Part 6 below as a single forward-pointer
   entry routed to a post-D8 documentation-correction sub-phase.
   That sub-phase is distinct from Issue 6's `expectations.md` "6
   themes vs 5" scope; the four-drift catalog is not a seventh
   methodology issue (Lock D, scope lock §3.3, held).

#### Part 2 — Root cause

**Gap-type attribution: calibration (primary, single attribution per
scope lock §5).** The §6.3(b) `FAIL` is a calibration gap-type. The
pre-registered floor of ≥ 30 / 199 was set by a methodology whose
calibration provenance is not recorded with sufficient specificity
to support stress-testing the floor value. `expectations.md` L105–107
documents a neutral-stratum-share rationale ("Universe B has 128 / 199
neutral-labeled, larger low-SVR mass is expected"), but the
inferential step from "neutral share is large" to "≥ 30 / 199 is the
right lower-tail prevalence floor" is not specified. The shortfall
observed at Stage 2d (−4 on 199, ~2 percentage points) is the
consequence of pre-registering a floor without an explicit
calibration model: there is no recorded basis for adjudicating
whether ≥ 30 / 199 was the right floor, whether a different
calibration source would have produced a different floor, or what
prior information the floor consumed.

**Documentation gap-type rejection.** A documentation gap-type
attribution ("the floor's provenance was simply not written down,
but the methodology was sound") is rejected as Issue 3's primary
attribution because `expectations.md` L105–107 already documents
*some* rationale (the neutral-stratum-share argument). The gap is
not absence-of-documentation; the gap is **under-specification of
the calibration model itself** — the documented rationale does not
specify the inferential step from prior information to floor value.
Documentation-of-existing-state drift in `expectations.md` (the "6
themes vs 5" mismatch) is Issue 6's exclusive scope. Issue 3's
documented-provenance requirement (Part 3a point 4) is a
calibration-spec internal requirement, not a documentation-drift
gap-type — the distinction is articulated in Part 6 below and does
not pre-empt or expand Issue 6.

**Definitional gap-type rejection.** Issue 1 owns definitional gaps
at the divergence-label boundary (`expectations.md` L77–85). §6.3(b)
operates on a definitionally-clean cut-point (SVR ≤ 0.30) over a
definitionally-clean cohort (all 199 UB calls). No L77–L85-class
definitional ambiguity is at play.

**Prompt-design gap-type rejection.** Issue 5 owns prompt-discipline
scope (cell-level methodology, theme-taxonomy alignment, label-mention
consistency across the full taxonomy). §6.3(b) is a structural-shape
gate on the SVR distribution; no prompt-design surface produces or
fails to produce the floor.

The calibration attribution is single, not co-primary. Naming
documentation, definitional, or prompt-design as co-primary would
conflate gap-types and violate scope lock §5's distinct-attribution
requirement.

#### Part 3a — Proposed revision spec

The revision specifies that future lower-tail prevalence floors must
be derived under an explicitly specified calibration model and that
the methodology producing those floors must itself be specified at
pre-registration time. The revision shape is **(I + IV) combination**
per the D8.4.4 outline:

- **(I)** re-derive future lower-tail prevalence floors under an
  explicitly specified calibration model.
- **(IV)** specify the pre-registration methodology that produces
  those floors.

Standalone (I) leaves the methodological gap open (a re-derived
floor without a documented method has the same provenance gap as the
original). Standalone (IV) does not instantiate (a method without a
re-derived floor is procedural-only). The combination addresses both.
Revision shape (II) — raise or lower the floor without specifying a
methodology — is rejected because it would re-introduce the same gap
at a different value. Revision shape (III) — consume Issue 4's joint-
shape calibration into Issue 3's revision spec — is rejected because
it would cross the Issue 3 ↔ Issue 4 boundary (Lock D, scope lock
§3.3); the rejection is independently grounded in Issue 3's own
scope (calibration methodology that produces the floor, not joint-
rule consumption), not solely in Issue 4 boundary protection.

**Revision spec (four points):**

1. **Calibration sources (structural property locked, source choice
   not locked).** A future lower-tail prevalence floor must be
   derived from at least one of: (a) a historical reference cohort
   (e.g., a prior Stage 2-class fire or a comparable evidence set
   with documented composition), (b) a theoretical bound on
   lower-tail prevalence given the stratum composition, or (c) an
   empirical-Bayes prior over the lower-tail mass conditional on
   Universe B composition. The spec **does not lock** which of
   (a) / (b) / (c) is chosen; it locks the structural requirement
   that the floor must be derived from one of these (or an
   equivalent named source) rather than asserted without provenance.
   This mirrors the structural-property-not-form discipline applied
   in D8.4.3 §4.2 Part 3a point 1 (value-space form not locked;
   structural requirement locked).
2. **Floor form (point vs interval).** The spec admits both a point
   floor (e.g., "≥ N at SVR ≤ 0.30") and an interval floor (e.g.,
   "between N₁ and N₂ at SVR ≤ 0.30"). The form choice is downstream
   and depends on the calibration source — empirical-Bayes naturally
   produces an interval, a theoretical bound naturally produces a
   point. The spec **does not lock** point vs interval; it requires
   the form to follow from the calibration source.
3. **Per-fire applicability (next future fire only).** The
   methodology must specify how it applies to a future Stage
   2-class fire's pre-registration of lower-tail-prevalence
   expectations without ad-hoc derivation at fire time. Application
   to fires beyond the next is **out of D8.4 scope**; multi-fire
   applicability is forward-pointed to Stage 2e+ planning. This
   narrowing is deliberate — committing the methodology to all
   future fires inside D8.4 would commit Stage 2e+'s scope, which
   scope lock §10 forbids; narrowing to the next fire keeps the
   spec instantiable without overreach.
4. **Documented provenance (calibration-spec internal requirement).**
   Each future floor must carry documented provenance: which
   calibration source produced it, what prior information it
   consumed, what inferential step it used. This is a
   **calibration-spec internal requirement** — provenance is part of
   the calibration spec, not a separable documentation concern. It
   is not a documentation-drift gap-type, does not pre-empt Issue 6
   (whose scope is `expectations.md` "6 themes vs 5"), and does not
   expand Issue 6 mid-arc. The distinction is reinforced in Part 6
   below.

**The revision spec does not:**

- Propose a specific replacement floor value (e.g., "≥ 26", "≥ 25",
  "between 24 and 32"). The spec is methodology-level; the value is
  downstream of the chosen calibration source.
- Edit `expectations.md`, D8.2 verdicts, D8.3 buckets, or any
  sealed Stage 2d artifact. D8.4 is proposal-only per scope lock §1
  and Lock A.
- Adjudicate the SVR ≤ 0.30 cut-point. The cut-point's documented
  derivation in `expectations.md` L105–107 is outside Issue 3's
  scope.
- Claim the proposed methodology is corrected, validated, or fixed
  (Lock A). The revision is a proposed calibration methodology, not
  a corrected one.
- Pre-empt Issue 4's authoring at D8.4.5. Issue 4's framing question
  is forward-pointed to D8.4.5's pre-authorization gate (Part 6
  below).

#### Part 3b — Expected behavior change

The revision **is intended to** make a future lower-tail prevalence
floor traceable to a named calibration source and a documented
inferential step, so that a future-fire shortfall (or surplus) can be
diagnosed as a calibration-source mismatch rather than as an
unprovenanced methodology drift. The revision **targets** the
under-specified calibration-methodology gap diagnosed in Part 1. The
revision **is expected to** make future floor-vs-observed comparisons
interpretable along the calibration-source axis, conditional on the
revised methodology surviving downstream design review and validation.

The forward-looking behavior is stated as a structural attribute of
the future methodology's specification ("traceable to a named
calibration source"), not as an outcome-quality claim. The revision
**does not** correct the §6.3(b) shortfall, eliminate calibration
error, or guarantee a future fire would `PASS`. No claim is made that
the revised methodology would produce a different verdict on the
Stage 2d cohort. Whether the revision produces the intended
structural traceability is established only by the validation
procedure specified in Part 4 below, not by Part 3b's forward-looking
statement.

D8.2's `FAIL` verdict and `calibration_shortfall` interpretation tag
stand at their evidence state. The revision is forward-looking only
and does not retroactively recharacterize the D8.2 adjudication. The
Part 3b forward-looking phrasing names a structural attribute the
revised methodology *would expose*; it does not claim the §6.3(b)
gate *would have passed* under the revised methodology, and it does
not claim the D8.2 verdict was incorrect at its evidence state.

#### Part 4 — Validation plan

Validation does not happen in D8.4. D8.4.4 specifies the validation
form only; the validation procedure executes downstream, at the
phase where the revised lower-tail-calibration methodology is
implemented and exercised against an evidence set.

**Necessary validation form: synthetic / simulation sanity check.**
Construct synthetic Universe-B-composition draws under controlled
lower-tail-prevalence parameters and process them through the
revised calibration methodology. The necessary condition is that the
revised methodology produces calibration sources and floors traceable
to the controlled parameters — i.e., the methodology is
self-describing under controlled inputs. This is a structural
validation of the calibration spec itself, not a cohort-level claim
about Stage 2d or any future cohort.

**Sufficient validation form (conditional on the synthetic check):
out-of-sample replication on a fresh Stage 2-class cohort.**
Out-of-sample replication is structurally privileged over re-firing
on the same Stage 2d evidence the calibration was derived from:
re-firing on the same evidence carries a circularity risk (the
calibration's method is being tested against the data it was
calibrated to fit). A fresh-cohort replication breaks the
circularity. The sufficient condition is that the revised
methodology produces a floor whose calibration source can be cited
and whose observed-vs-floor comparison can be diagnosed along the
source axis.

The synthetic sanity check is necessary; the out-of-sample
replication is **sufficient to support a downstream adoption
decision, not to prove future calibration performance**. Same-evidence
replay against the Stage 2d cohort may be used as a reproducibility
or sanity check only, not as primary validation evidence — the
circularity discipline is what privileges out-of-sample replication
over same-evidence re-fire for calibration questions.

The validation plan does not establish: that the revised methodology
produces a different verdict on the Stage 2d cohort; that calibration
error is eliminated; that the proposed methodology will outperform
the pre-registered methodology on any specific future fire.
Validation establishes only that the revised methodology produces a
calibration-source-traceable floor and that observed-vs-floor
comparisons under the revised methodology are diagnosable along the
calibration-source axis.

#### Part 5 — Affected rows or scope-level impact

Scope-level. **No row attribution.** Per scope lock §5 Part 5, Issue
3 is a scope-level issue; row-attribution citations would be a
defect under the §5 Part 5 rule. The §6.3(b) lower-tail composition
recorded at D8.2 L459–461 (22 neutral, 4 divergence_expected, 0
agreement_expected) is composition fact recorded by D8.2 itself, not
row-attribution evidence for Issue 3. Issue 3's proposed revision
operates on the pre-registration methodology that produces the floor,
not on individual rows.

Pos 138 and pos 143 are not cited under Issue 3: lower-tail
calibration does not materially touch RSI-absent vol_regime
test-retest framing, and the §5 Part 5 row-attribution rule restricts
pos 138 / 143 citation to issues that materially touch that framing.
The pos 143 fresh-7 negation restatement obligation does not
activate in §4.3.

Pos 3 is not cited under Issue 3: Issue 3 does not touch the
divergence-label cohort interpretation or the score-axis structure.
The pos 3 double-duty preservation obligation (scope lock §1.2,
≥ 2-site floor) is satisfied by §1.1, §4.1 Part 5, and §4.2 Part 5;
Issue 3's scope does not interact with the double-duty surface.

The scope-level impact: Issue 3's revision operates on the
pre-registration methodology that produces the lower-tail prevalence
floor; it does not change the §6.3(b) cut-point (SVR ≤ 0.30), does
not change the §6.3(b) cohort (all 199 UB calls), and does not
re-bucket any D8.3 candidate.

#### Part 6 — Issue interaction check

**Upstream dependencies.** None. Issue 3's calibration-methodology
revision is upstream of any issue that consumes a calibrated floor;
no other issue's revision is a prerequisite for Issue 3's spec.

**Downstream dependencies — Issue 2 (Direction-of-prediction
recalibration).** Per D8.4.3 §4.2 Part 6 (sealed at commit
`95109f7`), Issue 2's joint-rule shape requirement (D8.4.3 §4.2
Part 3a point 4) may mechanically change which candidates fall into
the §6.3(b) lower tail under a recalibrated joint rule, which would
change the lower-tail count as a function of the joint rule rather
than of SVR alone. **Issue 2 does not control the D8.4.4 revision
shape under the selected (I + IV) path** — Issue 3's revision
operates on the calibration methodology that produces the floor, not
on the joint rule that produces the lower-tail count. Later
synthesis (§5 of `D8_4_METHODOLOGY_REFINEMENT.md`) may need to
reconcile Issue 2's joint-rule surface with Issue 3's
floor-calibration methodology; D8.4.4 surfaces the potential
reconciliation point without resolving it.

**Downstream dependencies — Issue 4 (Joint-shape calibration
implications).** The Issue 3 ↔ Issue 4 boundary is set against the
**authoritative D8.2 §6.3 joint adjudication** at
[`docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md:537-538`](D8_STAGE2D_RESULT_ADJUDICATION.md#L537),
which records `primary_verdict = FAIL` and `interpretation_tag =
derived_joint_failure`. Codex independent verification surfaced that
the D8.2 §9 / appendix presentations at L1044 and L1229 use
`PARTIAL` / `asymmetric_calibration`, and that the Issue 4 framing
inherited into D8.3 §4.3, D8.4 scope lock §2.3 issue 4, and
[`D8_4_METHODOLOGY_REFINEMENT.md:122`](D8_4_METHODOLOGY_REFINEMENT.md#L122)
("Joint-shape asymmetric-calibration implications") was sourced from
the D8.2 summary-layer presentation rather than from the detailed
adjudication. **Issue 4 title/framing note.** The formal D8.2
detailed joint adjudication records `FAIL / derived_joint_failure`.
Later D8.2 summary rows use `PARTIAL / asymmetric_calibration`, and
D8.3 / D8.4 inherited the issue title "Joint-shape
asymmetric-calibration implications" from that summary-layer
framing. D8.4.4 does not decide whether the inherited Issue 4 title
remains analytically useful. D8.4.5 must adjudicate the Issue 4
framing against the authoritative detailed joint record before
authoring Issue 4 prose.

**Issue 3's revision shape (I + IV) stands regardless of D8.4.5's
adjudication outcome.** The rejection of revision shape (III)
(joint-rule consumption into Issue 3) was independently justified by
Issue 3's own scope (calibration methodology that produces the floor,
not joint-rule consumption), not solely by Issue 4 boundary
protection.

**Downstream dependencies — Issue 6 (Documentation drift).** Part
3a point 4's documented-provenance requirement is **internal to the
calibration methodology spec, not a documentation-drift gap-type**.
Issue 6's exclusive scope is documentation-of-existing-state drift
in `expectations.md` (specifically, the "6 themes vs 5" mismatch
recorded at `docs/d8/D8_3_SCOPE_LOCK.md` §4.3 issue 6). Issue 3's
documented-provenance requirement is documentation-of-future-
methodology — a different artifact (the calibration spec itself,
not yet written), a different scope (internal completeness of a
proposed methodology spec, not drift between a written document and
its intended state), and a different remediation path (specifying
the methodology, not editing `expectations.md`). No Issue 6
expansion. Lock D held.

**Conflicts at D8.4.4's evidence state.** None observed within Issue
3's scope. Foreseeable conflict: if D8.4.5 adjudicates Issue 4 in a
way that reframes "asymmetric calibration" as a calibration-
methodology question rather than a joint-shape question, the Issue
3 ↔ Issue 4 boundary may need synthesis-level reconciliation at §5
of `D8_4_METHODOLOGY_REFINEMENT.md`. D8.4.4 surfaces the *potential*
without resolving.

**Forward-pointer catalog — D8.2 §9 / appendix internal-presentation
drift (single forward-pointer entry, four rows, Lock D held).** The
following four drifts between D8.2's per-claim detailed adjudication
subsections (governing) and D8.2's §9 / appendix summary
presentations (inherited drift) are surfaced for routing to a
post-D8 documentation-correction sub-phase. The catalog is a single
forward-pointer entry; the four rows are observations within that
single entry, not four separate methodology issues. The catalog is
distinct from Issue 6's `expectations.md` "6 themes vs 5" scope
(different artifact, different drift class) and is not a seventh
methodology issue (Lock D, scope lock §3.3).

| # | Gate / verdict | D8.2 detailed (governing) | D8.2 §9 / appendix (drift) |
|---|---|---|---|
| 1 | §6.2.1 agreement floor | ≥ 52 / 66 (L236; +12 headroom) | ≥ 50 / 66 (L1040, L1225) |
| 2 | §6.3(a) upper-tail floor | ≥ 90 / 199 (L388–395; +21 headroom) | ≥ 60 / 199 (L1042, L1227) |
| 3 | §6.3(b) lower-tail floor | ≥ 30 / 199 (L444–457; −4 shortfall) | ≥ 40 / 199 (L1043, L1073, L1228) |
| 4 | §6.3 joint verdict + tag | `FAIL` / `derived_joint_failure` (L529–545) | `PARTIAL` / `asymmetric_calibration` (L1044, L1229) |

All four are inherited drift between the detailed §6.x adjudication
subsections and the §9 / appendix summary presentations inside the
same sealed D8.2 doc. D8.4 does not edit D8.2 (scope lock §3.2);
prior sealed D8.4 sites that inherited the drift (D8.4.1 §3
inventory line 121; D8.4.3 §4.2 Part 2 cross-reference line 529)
stand at their evidence state per scope lock §10. Drifts are
observed-and-surfaced, not edited. The catalog routes to a
**post-D8 documentation-correction sub-phase** — implementation
owner: future research-layer documentation phase; validation owner:
that future phase; explicit non-promise: D8.4 does not commit any
future phase's scope per scope lock §10.

---

### 4.4 Issue 4 — Paired-floor calibration coherence under derived joint failure

Issue 4 authors a methodology proposal addressing the paired-floor
calibration coherence question surfaced by the observed component
pattern at the §6.3 joint surface: §6.3(a) PASS at +21 headroom
alongside §6.3(b) FAIL at −4 shortfall, under a structurally-derived
joint failure tagged `derived_joint_failure` per D8.2 §6.3 joint
detailed record at L529–545. The §6.3 joint verdict itself is
structurally derived from the §6.3(b) component failure under the
conjunction rule (D8.2 L541–545: "the failure is structurally
derived, not an independently observed methodological gap"); D8.4.5
does not re-adjudicate the joint verdict and does not treat the
verdict tag as carrying independent methodology content beyond what
§6.3(b) carries. The diagnostic target of Issue 4 is the
**paired-floor calibration coherence** of the pre-registration
methodology that produced the upper and lower floors jointly: did
the methodology calibrate upper and lower floors against compatible
inferential steps under a single coherent calibration framework, or
did it produce systematically asymmetric floors as a separable
methodology gap from Issue 3's lower-tail-specific question? Issue 4
is a scope-level issue per scope lock §5 Part 5; no row-attribution
citations appear in the analysis, and the §6.3(a) upper-tail count
(111 observations at SVR ≥ 0.80) and §6.3(b) lower-tail composition
(D8.2 L459–461) are recorded as composition fact, not as
row-attribution evidence for Issue 4.

**Framing-correction note (single paragraph, title-level inheritance
form per D8.4.5 framing constraint 7).** D8.4.5 retitles Issue 4
from the inherited "Joint-shape asymmetric-calibration implications"
to "Paired-floor calibration coherence under derived joint failure".
The inherited title was sourced from the D8.2 §9 / appendix
summary-layer tag `asymmetric_calibration` (D8.2 L1044, L1229),
which is drift from the authoritative D8.2 §6.3 joint detailed
record at L529–545 (`primary_verdict = FAIL`,
`interpretation_tag = derived_joint_failure`). The four-drift
catalog at [`D8_4_METHODOLOGY_REFINEMENT.md` §4.3 Part 6](D8_4_METHODOLOGY_REFINEMENT.md#L1284)
(D8.4.4, sealed at `86d69b1`) records the tag drift as observation
row 4; D8.4.5 cross-references that catalog row rather than
re-cataloguing the same drift, preserving single-entry catalog
discipline (Lock D held). Prior sealed sites (D8.3 §4.3, D8.4
scope-lock §2.3, D8.4.1 §3 inventory line 122) retain the inherited
title and stand at their evidence state per scope-lock §10.
"Asymmetric" remains a defensible descriptive term for the observed
component-outcome pattern (upper +21 headroom alongside lower −4
shortfall) but is not the formal D8.2 interpretation tag. The
corrected title makes the analytical object — paired-floor
calibration coherence — visible up front, addressing Round 1
reviewer feedback that any title naming only the formal anchor would
hide the substantive scope from face-value reading.

`proposal_confidence`: **medium**. The diagnosis-to-spec internal
coherence holds, anchored on the empirically clean observed
paired-pattern asymmetry — §6.3(a) PASS at +21 headroom (D8.2
L388–395) alongside §6.3(b) FAIL at −4 shortfall (D8.2 L444–457) —
under a structurally-derived joint failure (D8.2 L529–545,
`derived_joint_failure`). The diagnosis-to-spec chain runs:
observed paired asymmetry at the §6.3 joint surface →
paired-floor calibration coherence gap at the pre-registration
methodology layer → paired-floor calibration methodology spec under
revision shape (I + IV) at the paired-floor unit. The revision
shape is structurally parallel to D8.4.4 / Issue 3's (I + IV) at the
single-floor unit, applied to a different unit of calibration. The
(Y) Reduced framing operates on what Issue 4 *claims about itself*
— no independent verdict tag, formal anchor is `derived_joint_failure`
not `asymmetric_calibration`, paired-floor coherence is the
analytical object not the joint verdict — and does not weaken the
empirical grounding of the diagnostic. Per scope lock §5.1 strict
semantics, `proposal_confidence` reflects diagnosis-to-spec internal
coherence and is not validation evidence; the label MUST NOT be
cited as proof that the proposed methodology works. The label
calibrates to `medium` to reflect internal coherence; it does not
extend to claim-space breadth.

#### Part 1 — Diagnosis

The §6.3 joint verdict is `FAIL` under `interpretation_tag =
derived_joint_failure` per D8.2 §6.3 joint detailed record at
L529–545. D8.2 L541–545 explicit narrative records the derivation:
"the failure is structurally derived, not an independently observed
methodological gap." The joint verdict adds no independent evidence
beyond §6.3(b)'s component failure; the conjunction
`PASS ∧ FAIL = FAIL` mechanically resolves the joint outcome from
the component verdicts.

But the **observed component pattern** at the joint surface carries
information that neither component verdict captures alone. D8.2
§6.3(a) detailed record at L382–438 records `primary_verdict = PASS`
with observed 111 / 199 against pre-registered floor ≥ 90 / 199 —
**+21 headroom**. D8.2 §6.3(b) detailed record at L440–510 records
`primary_verdict = FAIL` with observed 26 / 199 against pre-registered
floor ≥ 30 / 199 — **−4 shortfall**, `interpretation_tag =
calibration_shortfall`. Reading the two component outcomes jointly,
the methodology that produced the calibration profile produced an
upper tail wildly over-floor and a lower tail just-under-floor. That
asymmetric realization of paired floors is the diagnostic target of
Issue 4: it is observable at the joint surface, attributable to the
pre-registration methodology that produced both floors jointly, and
not derivable from either component verdict alone (each component
verdict reports a single-tail outcome against a single floor, not
the cross-tail relationship between paired floors).

**Diagnostic target.** The pre-registration methodology that
produced the **paired floors** — ≥ 90 / 199 at SVR ≥ 0.80 (upper)
and ≥ 30 / 199 at SVR ≤ 0.30 (lower). Specifically: did the
methodology derive both floors from a single coherent calibration
framework with consistent inferential steps, or did it derive each
floor under independent steps that produced systematically
asymmetric prevalence predictions? `expectations.md` L99 and L105–107
document the cut-points (SVR ≥ 0.80 upper, SVR ≤ 0.30 lower) and a
neutral-stratum-share rationale for the lower floor; the upper-floor
provenance and the paired-floor coherence between them are not
specified at the level required to adjudicate whether the +21 / −4
asymmetric realization reflects framework-internal asymmetry the
methodology accepted at pre-registration or framework-external drift
the methodology did not anticipate.

**What Issue 4 does NOT diagnose.** The §6.3(b) lower-tail-specific
calibration (Issue 3's exclusive scope at D8.4.4), the SVR ≤ 0.30
cut-point (out of D8.4 scope; documented in `expectations.md`
L105–107 with its own rationale), the SVR ≥ 0.80 cut-point (out of
D8.4 scope; documented in `expectations.md` L99 with its own
rationale), the formal joint verdict (which is structurally derived
per D8.2 L541–545; D8.4.5 does not re-adjudicate), and
direction-of-prediction × SVR adjudication-time joint rules (Issue
2's exclusive scope at D8.4.3).

D8.2's `FAIL` verdict at §6.3(b) and `derived_joint_failure`
interpretation tag at §6.3 joint stand at their evidence state.
D8.2's `PASS` verdict at §6.3(a) stands at its evidence state.

#### Part 2 — Root cause

**Gap-type attribution: calibration (primary, single attribution per
scope lock §5).** The Issue 4 root cause is named as a calibration
gap-type at the **paired-floor coherence layer**. Issue 3 (D8.4.4)
diagnosed the calibration gap-type at the **single-floor layer**
(specifically the lower-tail floor methodology behind ≥ 30 / 199 at
SVR ≤ 0.30). Issue 4 diagnoses a different unit of calibration: the
methodology that produces both upper and lower floors jointly, and
whether it anchors them against a coherent calibration framework
that constrains their cross-tail relationship, or whether the upper
and lower floors were derived under independent inferential steps
that produce systematic asymmetry as a structural property of the
methodology.

**Why the calibration gap-type repeats but is not Issue 3
expansion.** The gap-type attribution carves cleanly against Issue
3 by the **unit of calibration**: Issue 3 = single floor methodology
(one floor, one SVR threshold, one inferential step from prior
information to floor value); Issue 4 = paired-floor methodology
coherence (two floors jointly, the framework that links them, and
the inferential consistency between their derivations). The boundary
is mechanically enforceable at the prose-anchor level per D8.4.5
framing constraint 5: Issue 3 cites §6.3(b) only; Issue 4 cites
§6.3(a) + §6.3(b) jointly + §6.3 joint detailed record. Issue 3's
revision spec at the single-floor layer does not pre-empt Issue 4's
revision spec at the paired-floor layer; the two revisions operate
on different calibration units and may reconcile or coexist at
synthesis level (§5 of `D8_4_METHODOLOGY_REFINEMENT.md`).

**Documentation gap-type rejection.** Issue 6 owns
documentation-of-existing-state drift in `expectations.md` ("6
themes vs 5"). The four-drift forward-pointer catalog at D8.4.4 §4.3
Part 6 (cross-referenced in the framing-correction note) routes D8.2
§9 / appendix internal drift to a post-D8 documentation-correction
sub-phase. Neither of these catches Issue 4's substantive scope.
Paired-floor calibration coherence is a methodology-spec question at
the pre-registration layer; it is not documentation drift in
`expectations.md` (Issue 6) and it is not D8.2 internal-presentation
drift (D8.4.4 catalog row 4). Naming documentation as a co-primary
attribution would conflate the paired-floor methodology question
with documentation-of-existing-state drift and violate scope lock
§5's distinct-attribution requirement.

**Definitional gap-type rejection.** Issue 1 owns definitional gaps
at the divergence-label boundary in `expectations.md` L77–85.
§6.3(a) and §6.3(b) operate on definitionally-clean cut-points
(SVR ≥ 0.80 upper, SVR ≤ 0.30 lower) over a definitionally-clean
cohort (all 199 UB calls). No L77–L85-class definitional ambiguity
is at play in the paired-floor methodology layer.

**Prompt-design gap-type rejection.** Issue 5 owns prompt-discipline
scope (cell-level methodology, theme-taxonomy alignment,
label-mention consistency across the full taxonomy). §6.3 is a
structural-shape gate family on the SVR distribution; no
prompt-design surface produces or fails to produce the paired floors.

The calibration attribution is single, not co-primary. Same
distinct-attribution discipline as D8.4.4 / Issue 3, applied at the
paired-floor unit instead of the single-floor unit.

#### Part 3a — Proposed revision spec

The revision specifies that future paired floors must be derived
under a coherent calibration framework with documented internal
consistency at pre-registration time and a documented diagnostic
procedure for asymmetric outcomes at post-fire time. The revision
shape is **(I + IV) combination at the paired-floor layer**:

- **(I)** re-derive future paired floors (upper and lower jointly)
  under a single coherent calibration framework.
- **(IV)** specify the pre-registration methodology that produces
  the paired floors, with internal-consistency machinery at
  pre-registration time and a diagnostic procedure at post-fire time.

The revision shape is structurally parallel to Issue 3's (I + IV) at
the single-floor layer, applied to a different unit of calibration.
Standalone (I) leaves the methodological gap open (paired floors
re-derived without a documented framework have the same coherence
gap as the original). Standalone (IV) does not instantiate (a method
without re-derived paired floors is procedural-only). The
combination addresses both. Revision shape (II) — adjust upper
and/or lower floor values without specifying a methodology — is
rejected because it would re-introduce the same gap at different
values. Revision shape (III) — fold paired-floor coherence into
Issue 3's single-floor revision — is rejected because it would
collapse the unit-of-calibration distinction that carves the Issue
3 / Issue 4 boundary; the rejection is independently grounded in
Issue 4's own scope (the analytical object is paired-floor
coherence, not a per-tail methodology question), not solely in Issue
3 boundary protection.

**Revision spec (five points):**

1. **Coherent paired-floor calibration framework (structural
   property locked, source choice not locked).** The methodology
   must derive upper and lower floors from a single coherent
   calibration framework — for example: (a) a historical reference
   cohort with both upper and lower tails populated and their
   relative prevalences documented, (b) a theoretical bound
   consistent across tails (e.g., a paired-tail prevalence model
   under stratum-composition assumptions that constrains both
   tails), or (c) an empirical-Bayes prior that calibrates both
   tails jointly from a shared posterior over the full SVR
   distribution. The spec **does not lock** which framework is
   chosen; it locks the structural requirement that upper and lower
   floors must come from a single framework rather than from
   independent inferential steps that would produce systematic
   asymmetry as a structural property of the methodology. This
   mirrors D8.4.4 §4.3 Part 3a point 1 structural-property-not-form
   discipline, applied at the paired-floor layer.

2. **Pre-registration internal-consistency check on paired-floor
   predictions.** The methodology must specify, at pre-registration
   time, an internal-consistency check on the framework's own
   predictions: predicted upper-tail prevalence and predicted
   lower-tail prevalence are derived from the same underlying
   distributional assumptions and do not imply contradictory base
   rates, marginal-probability sums, or framework parameters. The
   check operates on the framework's *pre-registered predictions
   only*, not on observed-vs-floor comparisons. The spec **does not
   lock** the form of the consistency check (sum-to-known-total
   constraint on the predicted prevalences, ratio-bound on the
   predicted upper/lower prevalence ratio under the framework's
   stated assumptions, posterior-marginal compatibility check under
   the framework's prior, or other equivalently named test); it
   locks the structural requirement that *some* such check exists at
   pre-registration time, operating on predictions only. **The check
   operates on the framework's pre-registered predictions only and
   does not import observation. Post-fire observation is the scope
   of point 5.**

3. **Per-fire applicability (next future fire only).** The
   methodology must specify how it applies to a future Stage
   2-class fire's pre-registration of paired-floor expectations
   without ad-hoc derivation at fire time. Application to fires
   beyond the next is **out of D8.4 scope**; multi-fire
   applicability is forward-pointed to Stage 2e+ planning. This
   narrowing is deliberate — committing the methodology to all
   future fires inside D8.4 would commit Stage 2e+'s scope, which
   scope lock §10 forbids; narrowing to the next fire keeps the
   spec instantiable without overreach. Same narrowing as Issue 3
   Part 3a point 3.

4. **Documented provenance (calibration-spec internal requirement).**
   Each future paired floor must carry documented provenance for
   **both** floors and the framework that produced them jointly:
   which calibration framework produced the pair, what prior
   information it consumed, what inferential step linked the
   predicted prevalences to the floor values, and what consistency
   check (per point 2) was applied. This is a **calibration-spec
   internal requirement** — provenance is part of the calibration
   spec, not a separable documentation concern. It is not a
   documentation-drift gap-type, does not pre-empt or expand Issue
   6 (whose scope is `expectations.md` "6 themes vs 5"), and does
   not pre-empt or expand the four-drift forward-pointer catalog at
   D8.4.4 §4.3 Part 6 (whose scope is D8.2 §9 / appendix
   internal-presentation drift). The distinction is reinforced in
   Part 6 below.

5. **Post-fire asymmetry diagnostic.** The methodology must specify
   a post-fire diagnostic procedure for cases where the paired-floor
   framework produces asymmetric headroom/shortfall outcomes (such
   as the +21 / −4 pattern observed at Stage 2d). The diagnostic
   adjudicates between (a) framework-internal asymmetry the
   methodology accepted at pre-registration — i.e., the framework
   predicted asymmetric prevalences and the observation realized
   that prediction within tolerance — and (b) framework-external
   drift — i.e., the framework predicted symmetric or near-symmetric
   prevalences and the observation diverged from those predictions.
   The spec **does not lock** the form of the diagnostic
   (predicted-vs-observed difference under the framework's posterior,
   residual-against-predicted-distribution test, or other equivalently
   named procedure); it locks the structural requirement that *some*
   such diagnostic exists at post-fire time, operating on observed
   headroom/shortfall outcomes. **The diagnostic operates on
   observed headroom/shortfall outcomes only and does not
   retroactively change the pre-registered floors. Pre-registration
   internal-consistency is the scope of point 2.**

**The revision spec does not:**

- Propose specific replacement floor values for upper or lower (the
  spec is methodology-level; the values are downstream of the chosen
  calibration framework).
- Re-adjudicate the formal joint verdict — which is structurally
  derived per D8.2 L541–545 and stands at its evidence state.
- Treat `asymmetric_calibration` as the formal interpretation tag
  (it remains a descriptive term for the observed component pattern,
  not the formal D8.2 anchor).
- Edit `expectations.md`, D8.2 verdicts, D8.3 buckets, or any sealed
  Stage 2d artifact (Lock A).
- Adjudicate the SVR ≥ 0.80 or SVR ≤ 0.30 cut-points (out of D8.4
  scope; cut-points are documented in `expectations.md` L99 and
  L105–107 with their own rationales).
- Pre-empt Issue 3's lower-tail floor methodology revision (Issue 3
  owns the single-floor methodology layer; Issue 4 owns the
  paired-floor coherence layer; the boundary is the unit of
  calibration).
- Pre-empt Issue 2's joint-rule shape requirement (Issue 2 operates
  at adjudication time on direction × SVR; Issue 4 operates at
  pre-registration time on paired-floor calibration; different
  layer, different mechanism).

#### Part 3b — Expected behavior change

The revision **is intended to** make future paired floors traceable
to a single coherent calibration framework, with documented
internal-consistency at pre-registration time (Part 3a point 2) and
a documented diagnostic procedure for asymmetric outcomes at
post-fire time (Part 3a point 5). The revision **targets** the
under-specified paired-floor calibration coherence diagnosed in
Part 1. The revision **is expected to** make future upper-vs-lower
observed-pattern asymmetries diagnosable as either
(a) framework-internal asymmetry the methodology accepted at
pre-registration, via the Part 3a point 5 post-fire diagnostic, or
(b) framework-external drift the methodology did not anticipate, via
the same diagnostic, conditional on the revised methodology
surviving downstream design review and validation.

The pre-registration check (Part 3a point 2) gives the methodology
its consistency-at-spec-time guarantee; the post-fire diagnostic
(Part 3a point 5) gives the methodology its
diagnosable-at-observation-time capability. Both are needed for the
diagnostic capability above to have implementable spec hooks. The
two points operate at different temporal layers (ex-ante vs ex-post)
and do not collapse into each other — the pre-registration check
cannot diagnose post-fire asymmetry (it cannot import observation,
per the closing sentence of Part 3a point 2), and the post-fire
diagnostic cannot retroactively revise pre-registered floors (it
operates on observation only, per the closing sentence of Part 3a
point 5).

The forward-looking behavior is stated as a structural attribute of
the future methodology's specification ("traceable to a single
calibration framework", "internal-consistency at pre-registration",
"diagnostic capability at post-fire"), not as an outcome-quality
claim. The revision **does not** correct the §6.3(a) headroom, the
§6.3(b) shortfall, the joint conjunction outcome, or guarantee a
future fire would `PASS` at the joint surface. No claim is made that
the revised methodology would produce a different verdict on the
Stage 2d cohort. Whether the revision produces the intended
structural traceability is established only by the validation
procedure specified in Part 4 below, not by Part 3b's forward-looking
statement.

D8.2's `FAIL` verdict at §6.3(b) and `derived_joint_failure`
interpretation tag at §6.3 joint stand at their evidence state.
D8.2's `PASS` verdict at §6.3(a) stands at its evidence state. The
revision is forward-looking only and does not retroactively
recharacterize the D8.2 adjudications. The Part 3b forward-looking
phrasing names structural attributes the revised methodology *would
expose*; it does not claim the §6.3(b) gate or the §6.3 joint
verdict *would have passed* under the revised methodology, and it
does not claim D8.2's verdicts were incorrect at their evidence
state.

#### Part 4 — Validation plan

Validation does not happen in D8.4. D8.4.5 specifies the validation
form only; the validation procedure executes downstream, at the
phase where the revised paired-floor calibration methodology is
implemented and exercised against an evidence set.

**Necessary validation form: synthetic / simulation sanity check at
the paired-floor layer.** Construct synthetic
Universe-B-composition draws under controlled paired-tail-prevalence
parameters and process them through the revised paired-floor
calibration framework. The necessary condition is that the framework
produces calibrated paired floors traceable to the controlled
parameters AND triggers the pre-registration internal-consistency
check (Part 3a point 2) at the calibrated values AND, if the
controlled parameters introduce asymmetry, triggers the post-fire
asymmetry diagnostic (Part 3a point 5) at observation time. This is
a structural validation of the calibration spec itself at both
temporal layers (ex-ante consistency and ex-post diagnosability),
not a cohort-level claim about Stage 2d or any future cohort.
Without this check, an absent consistency-check trigger or absent
diagnostic trigger in any subsequent re-fire could indicate either
a methodology failure or a cohort-level property, with no way to
discriminate between them.

**Sufficient validation form (conditional on the synthetic check):
out-of-sample replication on a fresh Stage 2-class cohort.**
Out-of-sample replication is structurally privileged over re-firing
on the same Stage 2d evidence the calibration was derived from.
Re-firing on the same evidence carries a circularity risk: the
calibration's framework is being tested against the data it was
calibrated to fit. A fresh-cohort replication breaks the
circularity. The sufficient condition is that the revised
methodology produces paired floors whose calibration framework can
be cited and whose observed-vs-floor comparisons can be diagnosed
along the framework axis at both tails, with the post-fire
diagnostic surfacing whether the observed asymmetry (if any) was
framework-internal or framework-external. The same circularity
discipline applied at D8.4.4 / Issue 3 Part 4 holds here, applied
to the paired-floor layer.

The synthetic sanity check is necessary; the out-of-sample
replication is **sufficient to support a downstream adoption
decision, not to prove future calibration performance**. Same-evidence
replay against the Stage 2d cohort may be used as a reproducibility
or sanity check only, not as primary validation evidence — the
circularity discipline is what privileges out-of-sample replication
over same-evidence re-fire for paired-floor coherence questions, in
the same way it privileges out-of-sample replication for single-floor
calibration questions at D8.4.4.

The validation plan does not establish: that the revised methodology
produces a different verdict at §6.3(a), §6.3(b), or §6.3 joint on
the Stage 2d cohort; that paired-floor asymmetry is eliminated; that
future fires will `PASS` at the joint surface. Validation establishes
only that the revised methodology produces a calibration-framework-
traceable paired floor with an active pre-registration consistency
check and an active post-fire asymmetry diagnostic.

#### Part 5 — Affected rows or scope-level impact

Scope-level. **No row attribution.** Per scope lock §5 Part 5,
Issue 4 is a scope-level issue (mirrors D8.4.4 / Issue 3);
row-attribution citations would be a defect under the §5 Part 5
rule. The §6.3(a) **upper-tail count: 111 observations at SVR ≥ 0.80
across the 197 scored subset** (D8.2 L388–395) and §6.3(b)
lower-tail composition (D8.2 L459–461: 22 neutral, 4
divergence_expected, 0 agreement_expected) are composition fact
recorded by D8.2 itself, not row-attribution evidence for Issue 4.
Issue 4's proposed revision operates on the pre-registration
methodology that produces paired floors and the post-fire diagnostic
that interprets observed asymmetry; it does not operate on
individual rows.

Pos 138 and pos 143 are not cited under Issue 4: paired-floor
calibration coherence does not materially touch RSI-absent
vol_regime test-retest framing, and the §5 Part 5 row-attribution
rule restricts pos 138 / 143 citation to issues that materially
touch that framing. The pos 143 fresh-7 negation restatement
obligation does not activate in §4.4.

Pos 3 is not cited under Issue 4: Issue 4 does not touch the
divergence-label cohort interpretation or the score-axis structure.
The pos 3 double-duty preservation obligation (scope lock §1.2,
≥ 2-site floor) is satisfied by §1.1, §4.1 Part 5, and §4.2 Part 5;
Issue 4's scope does not interact with the double-duty surface.

The scope-level impact: Issue 4's revision operates on the
pre-registration methodology that produces paired prevalence floors
and on the post-fire diagnostic that interprets observed asymmetry;
it does not change the §6.3(a) or §6.3(b) cut-points (SVR ≥ 0.80,
SVR ≤ 0.30), does not change the §6.3 cohort (all 199 UB calls),
and does not re-bucket any D8.3 candidate.

#### Part 6 — Issue interaction check

**Upstream dependencies.** None. Issue 4's paired-floor calibration
coherence revision is upstream of any issue consuming a calibrated
paired-floor framework; no other issue's revision is a prerequisite
for Issue 4's spec.

**Downstream dependencies — Issue 2 (Direction-of-prediction
recalibration).** Issue 2's joint-rule shape requirement (D8.4.3
§4.2 Part 3a point 4, sealed at commit `95109f7`) operates on
direction-of-prediction × SVR threshold at **adjudication time**.
Issue 4's paired-floor calibration coherence operates on the
**pre-registration methodology** that produces upper and lower
floors at SVR thresholds, plus the **post-fire diagnostic** that
interprets observed asymmetry. Different layer, different
mechanism, no scope overlap (per D8.4.5 framing constraint 6).
Synthesis (§5 of `D8_4_METHODOLOGY_REFINEMENT.md`) may surface joint
reconciliation if Issue 2's recalibrated joint rule changes which
candidates fall into either tail under a revised joint adjudication,
but Issue 4 surfaces the potential reconciliation point without
resolving it.

**Downstream dependencies — Issue 3 (Lower-tail calibration).**
Issue 3 (sealed at commit `86d69b1`) owns the **single-floor
lower-tail methodology** at the gate level (§6.3(b) only,
`calibration_shortfall` tag). Issue 4 owns the **paired-floor
calibration coherence** at the cross-tail level (§6.3(a) + §6.3(b)
jointly + §6.3 joint detailed record, `derived_joint_failure` tag).
The boundary is held by anchor scope per D8.4.5 framing constraint
5: Issue 3 cites §6.3(b) only; Issue 4 cites §6.3(a) + §6.3(b)
jointly + §6.3 joint detailed record. The boundary is mechanically
enforceable at the prose-anchor level. **Issue 3's revision shape
(I + IV) at the single-floor layer does not pre-empt Issue 4's
revision shape (I + IV) at the paired-floor layer** — the two
revisions operate at different units of calibration. Synthesis may
need to reconcile the single-floor framework (Issue 3) with the
paired-floor framework (Issue 4) if both are adopted; D8.4.5
surfaces the reconciliation point without resolving.

**Downstream dependencies — Issue 6 (Documentation drift).** Part
3a point 4's documented-provenance requirement is **internal to the
calibration methodology spec, not a documentation-drift gap-type**.
Issue 6's exclusive scope is documentation-of-existing-state drift
in `expectations.md` (specifically, the "6 themes vs 5" mismatch
recorded at `docs/d8/D8_3_SCOPE_LOCK.md` §4.3 issue 6). Issue 4's
documented-provenance requirement is documentation-of-future-
methodology — a different artifact (the paired-floor calibration
spec itself, not yet written), a different scope (internal
completeness of a proposed methodology spec, not drift between a
written document and its intended state), and a different
remediation path (specifying the methodology, not editing
`expectations.md`). No Issue 6 expansion. Lock D held. Same
distinction discipline as D8.4.4 / Issue 3 Part 6 Issue 6 section.

**Forward-pointer cross-reference (NOT new catalog).** Per D8.4.5
framing constraint 8, Issue 4's framing-correction note (preamble
above) cross-references D8.4.4 §4.3 Part 6 forward-pointer catalog
row 4 (`§6.3 joint verdict + tag: FAIL / derived_joint_failure
detailed vs PARTIAL / asymmetric_calibration drift`). Issue 4 does
**NOT** create a new drift catalog or a new forward-pointer entry
for the same drift. Single-entry catalog discipline preserved
across the D8.4 sub-arc (Lock D held, scope lock §3.3).

**Conflicts at D8.4.5's evidence state.** None observed within
Issue 4's scope. Foreseeable conflict: if synthesis (§5) surfaces
incompatibilities between Issue 3's single-floor framework and
Issue 4's paired-floor framework — for example, if a paired-floor
framework adopted under Issue 4's revision implies a different
single-floor calibration source than Issue 3's revision adopted —
reconciliation routes to synthesis-level work, not to Issue 4
prose. D8.4.5 surfaces the *potential* reconciliation point without
resolving. The epistemic-humility qualifier "at D8.4.5's evidence
state" applies to both the no-conflict-observed claim and the
foreseeable-conflict notice.

---

### 4.5 Issue 5 — Forensic cross-tab methodology / prompt / label discipline

Issue 5 authors a methodology proposal addressing the
**theme-conditional surfacing mechanism under-specification** in the
coupled methodology surface comprising forensic cross-tab
construction, D7b prompt design, and pre-registered label discipline.
The diagnostic target is layer-agnostic at diagnosis time: D8.2 §6
forensic cross-tab evidence (L870–928) records cell-level
theme-conditional skews (specifically `mean_reversion × neutral` at
12 / 17 HIGH = 71% contrasted with `volatility_regime × neutral` at
6 / 34 HIGH = 18%, both neutral-label cells under different themes)
but does not adjudicate which methodology layer should be revised.
Issue 5 is a cross-tab methodology issue per scope-lock §5 Part 5
("cross-tab issue 5 cites cell-level evidence with no row
positions"); no row-attribution citations appear in the analysis.
Issue 5 is **not** a row-level issue, **not** a single-tail or
paired-tail calibration issue (Issues 3 and 4 own calibration),
**not** a divergence-label definitional issue (Issue 1 owns L77–85
definitional gap), **not** a direction-of-prediction recalibration
issue (Issue 2 owns D7b score-axis structure for direction), and
**not** a documentation-of-existing-state drift issue (Issue 6 owns
`expectations.md` "6 themes vs 5").

`proposal_confidence`: **medium-low**.

Rationale (absolute, non-comparative per scope-lock §5.1 strict
semantics): the diagnosis-to-spec internal coherence holds at the
cell-level methodology layer — D8.2 §6 forensic cross-tab L880–886
records empirically clean cell-level observations with notable
theme-conditional skews (`mean_reversion × neutral` 71% HIGH vs
`volatility_regime × neutral` 18% HIGH, both neutral-label cells
under different themes), and D8.2 L909–917 records a
calibration-adjacent implication: uniform SVR calibration across
themes would not match the observed theme-conditional behavior. The
diagnosis-to-spec chain runs: observed theme-conditional cell-level
skew → theme-conditional surfacing mechanism under-specification at
the methodology design layer → multi-surface methodology revision
spec at the prompt + label + cross-tab construction coupled layer
with the load-bearing layer left open at the spec level. The label
calibrates to `medium-low` because the load-bearing methodology
layer is not yet identified at the spec level — the revision spec
admits multiple methodology layers as compatible with the structural
requirement, and which layer carries the load is downstream design
work conditional on Stage 2e+ scope and prompt-design /
label-taxonomy / cross-tab-construction trade-off analysis. The
label is internal-coherence signal under multi-layer methodology
uncertainty at the spec level; per scope-lock §5.1 it is not
validation evidence and MUST NOT be cited as proof that the proposed
methodology works.

#### Part 1 — Diagnosis

**Citation-form note (preamble, single paragraph).** Scope-lock §2.3
issue 5 (line 131) and D8.4.1 §3 inventory (line 123) cite the
forensic cross-tab anchor as "§7 forensic cross-tab
`methodology_followup`, §8.4". D8.2's own internal subsection header
at L870 reads "§6 forensic cross-tab — Theme × UB label × SVR
bucket". The cross-tab content is physically located at L870–928
inside D8.2's §7 container ("§6.6 Observation Findings"), with the
internal header preserving the §6 claim-family framing. Both
citation forms point to the same cross-tab content via different
reference frames (physical container vs claim-family). D8.4.6 prose
uses "D8.2 §6 forensic cross-tab" (matching D8.2's own internal
header, the load-bearing citation form), with the L870–928 physical
location cited explicitly. Scope-lock's "§7" framing references the
§7 container per D8.2's TOC structure; this is reference-frame
variation across two accurate citation forms, not anchor drift, and
does not require entry into the four-drift forward-pointer catalog
at D8.4.4 §4.3 Part 6 (which is reserved for D8.2 §9 / appendix
internal-presentation drift).

**Authoritative anchors (D8.2 detailed records, never §9 / appendix
summary tags):**

- **D8.2 §6 forensic cross-tab detailed record (L870–928):**
  - Source: D8.1 cell 23, three-way contingency over 197 ok-scored
    records, cross-tabulated by `candidate_theme` ×
    `pre_registered_label` × SVR bucket (LOW `[0.00, 0.20)`, MOD-LOW
    `[0.20, 0.50)`, MOD-HIGH `[0.50, 0.80)`, HIGH `[0.80, 1.01]`)
  - Cell-level observations with notable skews (D8.2 L880–886):
    - `momentum × agreement`: 14 cell, **13 HIGH (93%)**
    - `mean_reversion × neutral`: 17 cell, **12 HIGH (71%)**
    - `calendar_effect × agreement`: 9 cell, **6 HIGH (67%)**
    - `volatility_regime × neutral`: 34 cell, **6 HIGH (18%)**
  - Adjudication: `primary_verdict = NOT_TESTABLE`,
    `interpretation_tag = observation_only`,
    `methodology_followup = D8.4` (D8.2 L894–896)
  - Material findings (D8.2 L900–928): four enumerated observations
    including the `mean_reversion × neutral` SVR-skew vs
    `volatility_regime × neutral` SVR-skew contrast; D8.2 L909–917
    records a calibration-adjacent implication that uniform SVR
    calibration across themes would not match the observed
    theme-conditional behavior; D8.2 L925–927 explicitly notes the
    cross-tab is forensic, not a new claim family — no threshold is
    pre-registered over any theme × label × bucket cell

- **D8.2 §6.6(3) detailed record (L762–822):** Theme × UB label
  contingency over 197 ok-scored records, supporting the cell-level
  observations in §6 forensic cross-tab. `NOT_TESTABLE /
  observation_only` per §6.6 framework.

- **D8.2 §6.6(2) detailed record (L706–760):** SVR–alignment
  decoupling cluster observations, supporting the cell-level
  structure that the cross-tab surfaces.

**Diagnostic statement.** Issue 5 diagnoses a methodology question
that the D8.2 §6 forensic cross-tab `NOT_TESTABLE / observation_only`
adjudication does not carry forward as a verdict but does carry
forward as a `methodology_followup = D8.4` pointer (D8.2 L896, §8.4
L1018–1020). The cross-tab is forensic, not a new claim family — no
threshold is pre-registered over any theme × label × bucket cell, and
all observations are `NOT_TESTABLE` per L925–927.

But the cell-level observations carry methodology content that the
existing methodology surface (prompt design, label taxonomy, and
cross-tab construction collectively) does not anticipate.
Specifically, `mean_reversion × neutral` (17 cell, 12 HIGH = 71%) and
`volatility_regime × neutral` (34 cell, 6 HIGH = 18%) are both
neutral-label cells under different themes, and produce dramatically
different SVR-bucket distributions — a ~4× difference in HIGH-bucket
share. The model's actual scoring behavior partitions neutral by
theme, but the pre-registered methodology surfaces this partitioning
post-hoc through the forensic cross-tab construction, not at design
time at any of the coupled methodology layers (prompt elicitation,
label taxonomy, cross-tab construction).

**Diagnostic target (theme-conditional surfacing mechanism,
layer-agnostic at diagnosis time).** The theme-conditional surfacing
mechanism in the coupled methodology surface comprising:

1. **Forensic cross-tab construction methodology.** Whether the
   cross-tab construction (theme × UB label × SVR bucket) anticipates
   or accommodates theme-conditional behavior within label categories.
2. **D7b prompt design.** Whether the D7b prompt elicits scoring
   information that distinguishes theme-conditional behavior within
   label categories.
3. **Pre-registered label discipline.** Whether the
   `pre_registered_label` taxonomy at the cell-level granularity
   anticipates that themes within a label category may behave
   structurally differently at SVR level.

The diagnostic target is layer-agnostic: D8.2 evidence records the
observation (theme-conditional cell-level skews) and the
calibration-adjacent implication (uniform calibration adjustment
across themes would not match the observed behavior at L909–917),
but does not adjudicate which methodology layer should be revised.
The diagnosis names the under-specification of the theme-conditional
surfacing mechanism across the coupled methodology surface; layer
attribution is downstream design work, not a diagnosis-stage
question.

**What Issue 5 does NOT diagnose.** Lower-tail or upper-tail
prevalence floor calibration (Issues 3 and 4 own calibration);
divergence-label L77–85 definitional gap (Issue 1's exclusive scope);
direction-of-prediction recalibration on D7b score axes (Issue 2's
exclusive scope at D8.4.3); documentation drift in `expectations.md`
"6 themes vs 5" (Issue 6's exclusive scope); the formal joint
verdict at §6.3 (Issue 4's framing scope, structurally derived per
D8.2 L541–545).

D8.2's `NOT_TESTABLE / observation_only` adjudication on the §6
forensic cross-tab stands at its evidence state. Adjacent gate
verdicts (§6.2.1 PASS, §6.2.2 FALSIFIED, §6.3(a) PASS, §6.3(b) FAIL,
§6.3 joint FAIL / `derived_joint_failure`, §6.4 PASS) all stand at
their evidence state.

#### Part 2 — Root cause

**Gap-type attribution: theme-conditional surfacing mechanism
under-specification (primary, single attribution per scope-lock §5;
no methodology layer pre-selected at diagnosis time).** The Issue 5
root cause is named as a methodology surfacing gap. D8.2 §6 forensic
cross-tab evidence (L870–928) shows that theme-conditional behavior
within label categories is methodologically load-bearing — the
`mean_reversion × neutral` 71% HIGH vs `volatility_regime × neutral`
18% HIGH contrast at neutral-label cells under different themes
(D8.2 L880–886) demonstrates that the model's scoring methodology
produces theme-conditional SVR distributions within label categories.
But the current methodology does not specify whether that behavior
should be surfaced at the prompt elicitation layer, the
label-taxonomy layer, or the cross-tab construction layer. The root
cause is therefore **under-specification of the theme-conditional
surfacing mechanism**, not a proven prompt-only failure or a proven
label-discipline-only failure or a proven cross-tab-construction-only
failure.

**Why no single layer is primary at diagnosis time.** D8.2
establishes that the methodology surfaces theme-conditional behavior
post-hoc through the forensic cross-tab construction (the cross-tab
is *where* the partitioning becomes visible), but it does not
establish whether the prompt, label taxonomy, or cross-tab
construction is the **correct load-bearing revision layer**. D8.2
L909–917 records a calibration-adjacent implication: uniform SVR
calibration across themes would not match the observed
theme-conditional behavior. This is evidence about what a
calibration-layer revision would not adequately resolve, not
evidence about which surfacing-layer revision is structurally
primary. D8.4.6 therefore locks the structural requirement that
theme-conditional surfacing must exist at some named methodology
layer, while leaving the implementation layer open at the spec
level.

**Calibration gap-type rejection.** Issues 3 and 4 own calibration
(single-floor and paired-floor respectively). The Issue 5 cell-level
methodology questions are not calibration questions in the Issues 3
/ 4 sense — they are about what the methodology surface (prompt +
label + cross-tab construction) elicits and surfaces at design
time, not about pre-registered prevalence floors. D8.2 L909–917's
calibration-adjacent implication flags the *adjacency* between
Issue 5's theme-conditional surfacing question and the calibration
scope owned by Issues 3 / 4: a uniform calibration adjustment would
not resolve the theme-conditional behavior, which means Issue 5's
surfacing methodology must be in place before any calibration
revision can be theme-conditional. Adjacency, not co-primary
attribution.

**Definitional gap-type rejection.** Issue 1 owns definitional gaps
at the L77–85 divergence-label boundary. The cross-tab cell-level
observations do not surface an L77–L85-class definitional ambiguity;
they surface a theme × label × SVR cell-level partitioning that the
existing label taxonomy does not anticipate.

**Direction-of-prediction gap-type rejection.** Issue 2 owns
direction-of-prediction recalibration via the D7b score-axis
structure. The cross-tab cell-level observations do not surface a
direction-of-prediction question — they surface a theme-conditional
magnitude question on SVR distributions within label categories.

**Documentation gap-type rejection.** Issue 6 owns documentation
drift in `expectations.md` "6 themes vs 5". The Issue 5 cell-level
methodology questions are about the theme-conditional surfacing
mechanism at the methodology design layer, not about
documentation-of-existing-state drift in `expectations.md`.

The theme-conditional surfacing mechanism attribution is
single-primary, not co-primary across calibration / definitional /
direction / documentation. Same distinct-attribution discipline as
D8.4.4 / D8.4.5, applied at the cross-tab cell-level methodology
unit instead of the gate-level or paired-gate-level units.

#### Part 3a — Proposed revision spec

Revision shape: **multi-surface coupled revision at the prompt +
label + cross-tab construction layer with load-bearing layer left
open at the spec level.** Issue 5 differs structurally from Issues
1–4 because the methodology surface is three-coupled (prompt design
+ label taxonomy + cross-tab construction) and the load-bearing
revision could plausibly live at any of the three (or at an
equivalent named methodology layer not enumerated). The Round 1b
outline locks the **structural requirement** — that the methodology
must surface theme-conditional behavior within label categories at
some elicitation, taxonomy, or construction layer — without
pre-locking which layer carries the load.

This is a different revision-shape pattern than D8.4.4 / D8.4.5's
(I + IV). Issues 3 and 4 had clearly-bounded calibration units
(single floor / paired floors); Issue 5's cross-tab is a forensic
surface over a three-coupled-surface methodology. The
structural-property-not-form discipline (D8.4.3 §4.2 Part 3a point
1; D8.4.4 / D8.4.5 mirrors) applies at a higher granularity here:
the spec locks "theme-conditional surfacing must exist at some
methodology layer", not "the cross-tab construction must be
theme-aware".

**Revision spec (three points):**

1. **Theme-conditional surfacing requirement (structural property
   locked, layer choice not locked).** The methodology must surface
   theme-conditional behavior within label categories at one or more
   of: (a) prompt elicitation layer (the D7b prompt asks the critic
   to commit to theme-conditional context); (b) label taxonomy layer
   (the pre-registered label encodes theme as an orthogonal
   structural axis); (c) cross-tab construction layer (the forensic
   cross-tab construction is theme-aware at construction time, with
   pre-registered theme-conditional readout rules or diagnostic
   structure); or (d) an equivalent named methodology layer that
   surfaces theme-conditional behavior within label categories at
   design time rather than post-hoc as observation. The spec **does
   not lock** which of (a) / (b) / (c) / (d) is chosen; it locks the
   structural requirement that theme-conditional surfacing exists at
   some named methodology layer rather than emerging only post-hoc
   as observation in the cross-tab. This mirrors D8.4.4 / D8.4.5
   structural-property-not-form discipline at the multi-surface
   methodology unit, generalized via the open-set qualifier (d) for
   parity with D8.4.4 §4.3 Part 3a point 1 ("or an equivalent named
   source") and D8.4.5 §4.4 Part 3a point 1 (analogous open-set
   framing).

2. **Per-fire applicability (next future fire only).** Same
   narrowing as Issues 3 and 4 Part 3a point 3 (D8.4.4 §4.3 Part 3a
   point 3; D8.4.5 §4.4 Part 3a point 3). The methodology must
   specify how it applies to a future Stage 2-class fire's
   pre-registration of theme-conditional surfacing without ad-hoc
   derivation at fire time. Application to fires beyond the next is
   **out of D8.4 scope**; multi-fire applicability is forward-pointed
   to Stage 2e+ planning.

3. **Documented provenance (methodology-spec internal
   requirement).** The chosen layer's methodology must carry
   documented provenance: which layer is chosen (or which equivalent
   named methodology layer is chosen per (d)), what prior
   information justifies the choice, what inferential or design step
   links the chosen layer to the surfacing requirement. Same
   calibration-spec-internal-requirement discipline as Issues 3 and
   4 Part 3a point 4, generalized to methodology-spec-internal-
   requirement for Issue 5's broader surface. Does not pre-empt or
   expand Issue 6 (whose scope is `expectations.md` "6 themes vs
   5"). Does not pre-empt or expand the four-drift forward-pointer
   catalog at D8.4.4 §4.3 Part 6 (whose scope is D8.2 §9 / appendix
   internal-presentation drift).

**The revision spec does not:**

- Re-adjudicate the §6 forensic cross-tab `NOT_TESTABLE /
  observation_only` adjudication (which stands at its evidence
  state)
- Edit `expectations.md`, D8.2 verdicts, D8.3 buckets, the D7b
  prompt template, the label taxonomy, or any sealed Stage 2d
  artifact (Lock A)
- Pre-lock which methodology layer carries the revision load (the
  layer choice is downstream design work)
- Pre-empt Issue 1's prompt-scaffold clarification narrowly scoped
  to divergence-label interpretation (D8.4.2 §4.1 Part 3a)
- Pre-empt Issue 2's prompt elicitation requirement narrowly scoped
  to direction-of-prediction (D8.4.3 §4.2 Part 3a point 3)
- Pre-empt Issue 6's documentation drift in `expectations.md`

#### Part 3b — Expected behavior change

The revision **is intended to** make future cross-tab observations
diagnosable as either (a) theme-conditional patterns the methodology
anticipated and surfaced at the chosen design-time layer (whichever
of prompt / label / cross-tab construction / equivalent named layer
carries the load), or (b) cross-tab observations that surface
unanticipated patterns requiring further methodology refinement.
The revision **targets** the theme-conditional surfacing mechanism
gap diagnosed in Part 1. The revision **is expected to** make future
cell-level methodology questions interpretable along the
theme-conditional surfacing axis, conditional on the revised
methodology surviving downstream design review and validation.

The forward-looking phrasing preserves Part 2's open-layer
attribution: Part 3b does not commit to a specific design-time layer
that Part 2 leaves open. The revised methodology's behavior is
expected to surface theme-conditional patterns at *whichever*
methodology layer carries the load (per Part 3a's open-set
qualifier), not at a pre-selected layer.

Forward-looking behavior stated as a structural attribute of the
future methodology's specification, not as an outcome-quality claim.
The revision **does not** correct the §6 forensic cross-tab
observation, eliminate cell-level surprises, or guarantee future
cross-tab observations will all be anticipated. Forbidden phrasings
(per scope-lock §5 and §5.1): "fixes the cross-tab", "eliminates
cell-level surprises", "anticipates all theme-conditional
behavior", any past-tense or magnitude claim. Required phrasing
pattern: "is intended to ...", "expected to ...", "the revision
targets ...".

D8.2's `NOT_TESTABLE / observation_only` adjudication on §6 forensic
cross-tab and adjacent gate verdicts all stand at their evidence
state. The revision is forward-looking only.

#### Part 4 — Validation plan

Validation does not happen in D8.4. D8.4.6 specifies the validation
form only.

**Necessary validation form: synthetic / simulation sanity check at
the methodology surface.** Construct synthetic candidates with
controlled theme × label characteristics (e.g., synthetic
mean_reversion × neutral with controlled SVR distribution; synthetic
volatility_regime × neutral with deliberately-different SVR
distribution). Process them through the revised methodology
(whichever layer carries the load per Part 3a). The necessary
condition is that **the chosen methodology layer surfaces the
controlled theme-conditional pattern at design time** — i.e., the
methodology surface is self-describing under controlled inputs.
**This validation checks the methodology surface (whether the
chosen layer surfaces theme-conditional behavior as required), not
D7b scoring quality** (which would be a model-performance
validation, not a methodology-adequacy validation).

**Sufficient validation form (conditional on the synthetic check):
out-of-sample replication on a fresh Stage 2-class cohort.** Same
circularity discipline as Issues 3 and 4 Part 4 — out-of-sample
replication is structurally privileged over re-firing on the same
Stage 2d evidence the cross-tab was constructed from. The sufficient
condition is that the revised methodology produces a cross-tab
whose theme-conditional surfacing layer can be cited (per Part 3a
point 3 documented provenance) and whose cell-level observations can
be diagnosed along the surfacing axis. Validation again operates on
the methodology surface, not on D7b scoring quality.

The synthetic sanity check is necessary; the out-of-sample
replication is **sufficient to support a downstream adoption
decision, not to prove future cross-tab interpretability**.
Same-evidence replay against the Stage 2d cohort may be used as a
reproducibility / sanity check only.

The validation plan does not establish: that the revised methodology
produces a different §6 forensic cross-tab adjudication on the
Stage 2d cohort; that all theme-conditional patterns are
anticipated; that future cross-tab observations will all be
expected; or that D7b scoring quality is improved (D7b scoring is
downstream of the methodology surface that Issue 5 revises).

#### Part 5 — Affected rows or scope-level impact

Cross-tab. **Cell-level evidence with no row positions.** Per
scope-lock §5 Part 5 ("cross-tab issue 5 cites cell-level evidence
with no row positions"), Issue 5 cites the cross-tab cells (theme ×
UB label × SVR bucket) recorded in D8.2 §6 forensic cross-tab
L880–886. Cell counts: `momentum × agreement` 14 cell / 13 HIGH;
`mean_reversion × neutral` 17 cell / 12 HIGH; `calendar_effect ×
agreement` 9 cell / 6 HIGH; `volatility_regime × neutral` 34 cell /
6 HIGH. These are cell composition facts recorded by D8.2 itself,
not row-attribution evidence for Issue 5. Asserting row positions
for Issue 5 would be a defect under §5 Part 5.

Pos 138 and pos 143 are not cited under Issue 5: cross-tab
methodology / prompt / label discipline does not materially touch
RSI-absent vol_regime test-retest framing at the row-attribution
level. The pos 143 fresh-7 negation restatement obligation does not
activate in §4.5.

Pos 3 is not cited under Issue 5: Issue 5 does not touch the
divergence-label cohort interpretation or the score-axis structure.
The pos 3 double-duty preservation obligation (scope-lock §1.2,
≥ 2-site floor) is satisfied at §1.1, §4.1 Part 5, and §4.2 Part 5
per scope-lock §5 Part 5 "issues 1 or 2" restriction; Issue 5's
scope does not interact with the double-duty surface (mirrors
D8.4.4 §4.3 Part 5 and D8.4.5 §4.4 Part 5 sealed convention —
non-citation declarations at scope-level / cross-tab issue Part 5
sites do not count toward the satisfaction floor).

The cross-tab-level impact: Issue 5's revision operates on the
prompt design + label taxonomy + cross-tab construction methodology
that produces cell-level observations; it does not change the §6
forensic cross-tab adjudication, does not change which cells exist,
and does not re-bucket any D8.3 candidate.

#### Part 6 — Issue interaction check

**Upstream dependencies.** None. Issue 5's prompt + label +
cross-tab revision is upstream of any issue consuming the cross-tab
evidence base; no other issue's revision is a prerequisite for
Issue 5's spec.

**Downstream dependencies — Issue 1.** D8.4.2 §4.1 Part 3a includes
a "prompt-scaffold clarification scoped narrowly to divergence-label
interpretation" (sealed at commit `3a8314d`, §4.1 lines 394–401).
Issue 5's broader prompt + label + cross-tab methodology scope
inherits the narrowly-scoped Issue 1 clarification as input but does
not re-author it. The boundary discipline holds across the broader
Part 2 framing: Issue 1 owns divergence-label-specific prompt
scaffolding (a layer-specific scope that is one of the surfaces
Issue 5 ranges over); Issue 5 owns the broader theme-conditional
surfacing mechanism question across the prompt + label + cross-tab
coupled surface (layer-agnostic at diagnosis per Part 2).
Mechanically enforceable in the prose-anchor level: Issue 1's
prompt-scaffold reference cites L77–85 specifically; Issue 5's
methodology-surface reference cites the cell-level granularity
across the coupled surface.

**Downstream dependencies — Issue 2.** D8.4.3 §4.2 Part 3a point 3
includes a "D7b prompt elicitation requirement" narrowly scoped to
direction-of-prediction (sealed at commit `95109f7`, §4.2 lines
570–578). Issue 5's broader methodology-surface scope inherits the
narrowly-scoped Issue 2 elicitation requirement as input but does
not re-author it. Same boundary discipline as Issue 1: Issue 2 owns
direction-of-prediction-specific prompt elicitation (a layer-
specific scope at the prompt elicitation layer); Issue 5 owns the
broader theme-conditional surfacing mechanism across the coupled
methodology surface. The boundary holds under the broader Part 2
framing because Issue 5's scope is layer-agnostic at diagnosis:
Issue 2's prompt-elicitation-specific scope is contained within
Issue 5's broader methodology-surface scope at one of the four
candidate revision layers (Part 3a (a)).

**Downstream dependencies — Issues 3 and 4.** Issues 3 and 4 own
calibration (single-floor and paired-floor). Issue 5's prompt +
label + cross-tab revision does not pre-empt or interact with
calibration scope. The cross-tab cells inform calibration adjacent
issues — D8.2 §6 forensic cross-tab L909–917 records a
calibration-adjacent implication that uniform SVR calibration
across themes would not match the observed theme-conditional
behavior — but Issue 5 surfaces the cross-tab methodology question
at the theme-conditional surfacing mechanism layer (layer-agnostic
at diagnosis), not at the calibration layer. **Adjacency, not
co-primary attribution:** the theme-conditional surfacing question
is structurally upstream of any theme-conditional calibration
question that Issues 3 / 4 might consider in synthesis (§5 of
`D8_4_METHODOLOGY_REFINEMENT.md`); reconciliation routes to
synthesis-level work, not to Issue 5 prose.

**Downstream dependencies — Issue 6.** Part 3a point 3
documented-provenance requirement is **internal to the methodology
spec, not a documentation-drift gap-type**. Issue 6's exclusive
scope is documentation-of-existing-state drift in `expectations.md`
"6 themes vs 5". Issue 5's documented-provenance requirement is
documentation-of-future-methodology — same distinction discipline
as D8.4.4 / D8.4.5 Part 6 Issue 6 sections.

**Forward-pointer (no new catalog).** Per Lock D and the D8.4
single-document discipline, Issue 5 does NOT create a new drift
catalog. The four-drift forward-pointer catalog at D8.4.4 §4.3
Part 6 (cross-referenced in D8.4.5 §4.4 framing-correction note)
covers D8.2 §9 / appendix internal drift; no Issue 5 drift surfaces
have been observed at outline drafting time. The scope-lock §2.3 /
D8.4.1 §3 inventory citation form "§7 forensic cross-tab" vs D8.2's
internal header "§6 forensic cross-tab" is a citation-form question
at different reference frames, not a tag or numeric drift; addressed
at the Part 1 preamble note above.

**Conflicts at D8.4.6's evidence state.** None observed within
Issue 5's scope. Foreseeable conflict: if synthesis (§5 of
`D8_4_METHODOLOGY_REFINEMENT.md`) surfaces incompatibilities between
Issue 5's chosen methodology layer (downstream design choice across
(a) / (b) / (c) / (d)) and Issues 1, 2, 3, or 4's revisions,
reconciliation routes to synthesis-level work, not to Issue 5
prose. D8.4.6 surfaces the *potential* without resolving.

---

### 4.6 Issue 6 — Operational-vs-documentation alignment under-specification (no resolution layer pre-selected at diagnosis time)

**Inheritance / framing-correction note.** Scope lock §2.3 inherits
this issue under the framing "Documentation drift, expectations.md '6
themes' vs operational 5". Pre-outline anchor verification at D8.4.7
surfaced that the inheritance framing structurally compresses the
diagnostic shape. Documented and canonical sources converge on six
themes across four anchors: `docs/d7_stage2d/stage2d_expectations.md`
line 159 ("6 themes × 3 labels = 18-cell count table"); the
`THEMES: tuple[str, ...]` definition in `agents/themes.py`
(`momentum`, `mean_reversion`, `volatility_regime`,
`volume_divergence`, `calendar_effect`,
`multi_factor_combination`); `CLAUDE.md` line 226 ("THEMES is the
canonical 6-theme list defined in D6"); and
`blueprint/PHASE2_BLUEPRINT.md` line 657 (six-theme `THEMES` list).
The Stage 2d operational fire at D8.2 §6.6(3) lines 762-822 records
five themes observed in the ok-scored cohort with
`multi_factor_combination` producing zero calls, classified as
`primary_verdict = NOT_TESTABLE`,
`interpretation_tag = observation_only`. The drift is between
(multi-source documented and canonical methodology) and (single-source
operational-fire observation), with the resolution layer not
pre-selected at diagnosis time. Lock C held: the broaden operates on
scope-lock §2.3 inheritance framing, not on D8.2 §6.6(3) evidence
state; the `NOT_TESTABLE / observation_only` adjudication stands at
its evidence state. The retitling is structurally analogous to D8.4.5
§4.4 title retirement (inherited
`asymmetric_calibration` → scope-explicit
`Paired-floor calibration coherence under derived joint failure`)
and to D8.4.6 §4.5 Part 2 broadening (prompt-design-primary →
theme-conditional surfacing mechanism under-specification with no
methodology layer pre-selected at diagnosis time); three instances
across the D8.4 sub-arc now form a discipline pattern (Process Note
43 candidate, recorded for D8.4.10 closeout). Prior sealed sites
(scope-lock §2.3 inventory, D8.4.1 §3 inventory) retain the
inherited title and stand at their evidence state per scope lock §10
immutability.

`proposal_confidence`: **medium-low**.

Diagnosis-to-spec internal coherence holds at the operational-vs-
documentation alignment surface. The diagnosis-to-spec chain runs:
multi-source documented and canonical convergence on six themes →
single-source operational-fire observation of five themes with
`multi_factor_combination` zero-call observation → operational-vs-
documentation alignment under-specification at the methodology-design
layer → adjudication-and-routing spec describing how each candidate
resolution layer would be tested, authorized, and sequenced if
selected, with no resolution layer pre-selected at diagnosis time.
The label calibrates to medium-low because the load-bearing
resolution layer is not yet identified at the spec level; open-
resolution-layer uncertainty at the spec level distinguishes Issue 6
from issues with clearly bounded resolution layers. Rationale
anchored on absolute terms per scope lock §5.1 strict semantics: the
label is internal-coherence signal under open-resolution-layer
uncertainty at the spec level; per scope lock §5.1 it is not
validation evidence and MUST NOT be cited as proof that the proposed
adjudication-and-routing spec works.

#### Part 1 — Diagnosis

The diagnostic surface is operational-vs-documentation alignment
under-specification observed at D8.2 §6.6(3) Theme × UB label
contingency (lines 762-822). The documented and canonical methodology
specifies six themes: this specification is recoverable from four
distinct anchors that converge byte-equivalently on the six-theme
list. (1) `docs/d7_stage2d/stage2d_expectations.md` line 159
specifies "6 themes × 3 labels = 18-cell count table" as the
pre-registered cross-tab structure. (2) The
`THEMES: tuple[str, ...]` definition in `agents/themes.py`
enumerates the six themes (`momentum`, `mean_reversion`,
`volatility_regime`, `volume_divergence`, `calendar_effect`,
`multi_factor_combination`) as the canonical operational
identifiers, marked with a `CONTRACT BOUNDARY` comment that names
the six-theme tuple as the binding canonical list. (3) `CLAUDE.md`
line 226 records the canonical specification ("THEMES is the
canonical 6-theme list defined in D6") at the project-instruction
level. (4) `blueprint/PHASE2_BLUEPRINT.md` line 657 lists the
six-theme `THEMES` list at the blueprint planning-document level.
All four anchors specify the same six themes; no inconsistency among
documented or canonical sources is observed.

The Stage 2d operational fire produced 199 UB calls, of which 197
records constitute the ok-scored cohort referenced at §6.6(3) (and
referenced upstream at D8.2 §3). D8.2 §6.6(3) records the Theme × UB
label contingency for the ok-scored cohort: five themes are observed
in the contingency table (`momentum`, `mean_reversion`,
`volatility_regime`, `volume_divergence`, `calendar_effect`); the
sixth canonical theme `multi_factor_combination` produces zero calls
in the observed fire. D8.2 adjudicates the §6.6(3) observation as
`primary_verdict = NOT_TESTABLE`,
`interpretation_tag = observation_only`, preserving evidence-state
without pre-attributing the gap to any specific resolution layer.

The under-specification surface is the alignment relationship between
documented + canonical methodology and the operational fire, not any
specific defect within either side. Documented + canonical sources
are internally consistent (all four anchors specify six themes
identically). The operational fire is internally consistent (the
ok-scored cohort observation is faithfully recorded at §6.6(3) with
explicit cell counts and `NOT_TESTABLE` adjudication). What is
under-specified is the methodology-design relationship between the
two: whether the documented six-theme specification is intended to be
operationally enforced (such that any fire that produces fewer themes
indicates an operational-pipeline defect), is intended as an
upper-bound specification (such that any fire that produces a subset
is operationally valid), is intended to be revised based on observed
operational behavior, or is intended to remain as-is with the
operational variance accepted as design tolerance. Each of these
methodology-design positions is consistent with the observed evidence
at this diagnosis stage; none is pre-selected by D8.2's
`NOT_TESTABLE / observation_only` adjudication.

#### Part 2 — Root cause

Gap-type attribution: **operational-vs-documentation alignment
under-specification (primary, single attribution per scope lock §5;
no resolution layer pre-selected at diagnosis time)**. The
under-specification is at the methodology-design layer, operating on
the relationship between documented + canonical methodology and
operational-fire observation, not within either side independently.
The single-primary attribution discipline is satisfied at one unit:
the alignment surface between the two sides. Distinct from Issue 5's
theme-conditional surfacing mechanism under-specification (Issue 5
operates on the design-time vs post-hoc surfacing question across
prompt + label + cross-tab construction; Issue 6 operates on the
documented-vs-operational alignment question across multi-source
documentation and single-source observation). Distinct from Issues
3 and 4's calibration units (single-floor vs paired-floor); Issue 6
is not a calibration question. Distinct from Issues 1 and 2's
divergence-label and direction-of-prediction units; Issue 6 is not a
classification or directional question.

Candidate resolution layers, layer-agnostic at diagnosis time, with
open-set qualifier:

- (a) **Documentation update.** The six-theme specification is
  over-specified relative to operational design intent; documented +
  canonical sources are revised to reflect the operationally
  realized theme set. Resolution sub-cases include reducing to five
  themes if `multi_factor_combination` is genuinely never
  operationally produced; documenting `multi_factor_combination` as
  optional or theoretical; or annotating the six-theme list with
  operational-realization caveats.
- (b) **Operational-path investigation or enforcement.** The
  documented six-theme specification is intended to be operationally
  enforced; the operational pipeline should produce all six themes
  but did not in the observed Stage 2d fire. Resolution sub-cases
  include investigating why `multi_factor_combination` produced zero
  calls (proposer-side selection bias, candidate-generation gap,
  prompt-conditional theme exclusion, or other operational
  mechanism); enforcing six-theme coverage at the operational layer;
  or instrumenting the operational pipeline to detect theme-coverage
  gaps as part of fire validation.
- (c) **Candidate-generation investigation.** A subset of
  operational-path framing focused specifically on the candidate-
  generation surface: the proposer or candidate-surfacing mechanism
  should produce candidates spanning all six themes but did not for
  `multi_factor_combination` in the observed fire. Resolution
  sub-cases include investigating the proposer's theme-conditional
  candidate-generation behavior; checking whether
  `multi_factor_combination` requires more complex candidate
  conditions that are not satisfied at the proposer level; or
  examining whether prompt-design properties bias candidate
  generation away from `multi_factor_combination`.
- (d) **Methodology-acceptance / no-edit.** The operational variance
  observed at §6.6(3) is consistent with the six-theme specification
  as design-tolerance: the documented six-theme list specifies the
  set of *possible* operational themes, not the set of *required*
  operational themes; any given fire may legitimately produce a
  subset. Resolution sub-cases include accepting the observed
  variance as in-tolerance; documenting the design-tolerance
  interpretation explicitly; or specifying minimum theme-coverage
  expectations across multi-fire aggregates rather than per-fire.
- (e) **Equivalent named framing not yet enumerated.** The candidate
  list (a)-(d) is not asserted to be exhaustive at diagnosis time.
  An equivalent named framing not yet articulated may be the correct
  resolution layer; the open-set qualifier preserves the under-
  specification at the spec level rather than constraining
  resolution to the four enumerated framings.

No layer pre-selected at diagnosis time. D8.4.7 surfaces the under-
specification and routes to the appropriate sub-phase or authorized
future work for layer-resolution. The four candidate framings (a),
(b), (c), (d) each pre-select a different methodology-design
position; without a resolution-layer-selection adjudication, none is
load-bearing for D8.4.7's diagnosis. The structural-property-not-
form discipline parallel to D8.4.4 §4.3 Part 3a point 1, D8.4.5 §4.4
Part 3a point 1, and D8.4.6 §4.5 Part 3a point 1 (d) is satisfied at
this Part 2 layer-agnostic enumeration: the structural property
(operational-vs-documentation alignment under-specification with no
resolution layer pre-selected at diagnosis time) is locked; the
resolution-layer choice is not locked.

#### Part 3a — Proposed revision spec

D8.4.7 produces an adjudication-and-routing spec, not a methodology-
revision spec. The structural shape of the proposed revision is
documentation-routing rather than methodology-rewrite: D8.4.7 does
not propose a specific edit to the documented six-theme
specification, the operational pipeline, or the methodology-design
contract; D8.4.7 proposes the spec for how the candidate resolution
layers would be tested, authorized, and sequenced if any one of them
were selected.

Five framing options enumerated for routing-spec authoring,
corresponding one-to-one to Part 2 candidate resolution layers:

1. **Documentation-completeness framing (corresponds to candidate
   (a)).** The adjudication asks whether the documented six-theme
   specification is over-specified relative to operational design
   intent; if so, the documentation update routes to a
   documentation-correction sub-phase (post-D8.4 sub-arc) where the
   four documented + canonical anchors are updated coherently with
   explicit cross-anchor consistency verification.
2. **Operational-path framing (corresponds to candidate (b)).** The
   adjudication asks whether the operational pipeline should produce
   all six themes and failed to do so in Stage 2d; if so, the
   operational-path investigation or enforcement routes to an
   operational-pipeline sub-phase where the candidate-generation,
   proposer-selection, and theme-coverage surfaces are investigated
   for the mechanism that produced zero `multi_factor_combination`
   calls.
3. **Candidate-generation framing (corresponds to candidate (c)).**
   The adjudication asks whether the proposer or candidate-surfacing
   mechanism is the locus of the under-specification; if so, the
   candidate-generation investigation routes to a proposer-mechanism
   sub-phase examining theme-conditional candidate-generation
   behavior.
4. **Methodology-acceptance framing (corresponds to candidate (d)).**
   The adjudication asks whether the observed operational variance
   is in-tolerance for the six-theme specification interpreted as
   design-tolerance; if so, the methodology-acceptance routes to an
   acknowledgment sub-phase recording the design-tolerance
   interpretation explicitly without methodology revision.
5. **Open-set framing (corresponds to candidate (e)).** The
   adjudication acknowledges that the four enumerated framings may
   not exhaust the resolution-layer space; if a not-yet-enumerated
   framing is the correct resolution layer, the routing-spec
   accommodates the un-enumerated framing by deferring resolution-
   layer selection to authorized future work without committing to
   the (a)/(b)/(c)/(d) enumeration as exhaustive.

The adjudication spec consumes the Stage 2d 5-theme observation as
evidence but does not let that observation pre-select the resolution
layer. The observation motivates the adjudication question; the
framing choice remains deferred to a future authorized phase.
Validation-form pre-registration at Part 4 operates pre-replication.

#### Part 3b — Expected behavior change

The expected behavior change at the methodology-design layer is the
disambiguation of the operational-vs-documentation alignment
relationship: post-resolution, one of the four enumerated framings or
an equivalent un-enumerated framing carries the load of the alignment
specification, with the chosen framing's resolution applied to the
documented + canonical sources, the operational pipeline, the
methodology-design contract, or some combination per the chosen
framing's scope.

D8.4.7 does not commit to a specific behavior change because Part 2
leaves the resolution layer open. The revised methodology's behavior
is expected to surface a coherent operational-vs-documentation
alignment specification at whichever methodology-design layer carries
the load (per Part 3a's open-set qualifier), not at a pre-selected
layer. Cross-Part coherence pattern parallel to D8.4.6 §4.5 Part 3b
layer-agnostic-vs-implementation non-collapse and to D8.4.5 §4.4 Part
3b temporal-boundary non-collapse.

Out-of-scope explicitly:

1. **Selecting any specific resolution layer.** Lock A (proposal-
   only): D8.4.7 surfaces the under-specification and routes to the
   appropriate sub-phase or authorized future work; D8.4.7 does not
   pre-select among the (a)/(b)/(c)/(d)/(e) candidate framings.
   Resolution-layer selection is deferred to authorized future
   sub-phase per Lock A.
2. **Editing documented sources.** Lock B (no edits to D8.0 / D8.1 /
   D8.2 / D8.3 sealed artifacts and, by extension, no edits to the
   four documented + canonical anchors at this sub-phase): D8.4.7
   does not edit `docs/d7_stage2d/stage2d_expectations.md`,
   `agents/themes.py`, `CLAUDE.md`, or
   `blueprint/PHASE2_BLUEPRINT.md`. If the documentation-completeness
   framing is selected at the authorized future sub-phase, those
   edits route to a post-D8.4 documentation-correction sub-phase, not
   to D8.4.7.
3. **Editing the operational pipeline.** Lock A (proposal-only) and
   Lock B (no-edit): D8.4.7 does not modify candidate generation,
   proposer-selection, theme-assignment, or any other operational
   pipeline surface. If the operational-path or candidate-generation
   framings are selected at the authorized future sub-phase, those
   edits route to an operational-pipeline sub-phase, not to D8.4.7.
4. **Re-running Stage 2d or any new operational fire.** Lock A
   (proposal-only): D8.4.7 does not propose new operational fires or
   re-runs of sealed Stage 2d. The observed §6.6(3) evidence stands
   at its evidence state; resolution-layer selection operates on the
   observed evidence plus authorized future work, not on new
   operational data.

#### Part 4 — Validation plan

**Structural-distinction acknowledgment.** Issue 6's revision is
documentation-routing-spec rather than methodology-revision-spec. The
validation form structurally cannot mirror Issues 3, 4, and 5's
necessary (synthetic / controlled) plus sufficient (out-of-sample /
natural) pattern, which couples two evidential surfaces of the same
methodology behavior. Issue 6's validation operates on two distinct
artifacts: the adjudication artifact (this sub-phase) and the
operational behavior or documentation revision under whichever
framing is selected (authorized future sub-phase). The two surfaces
do not compose the way Issues 3, 4, and 5's necessary and sufficient
surfaces compose; the adjudication-completeness check operates on
the routing spec, the framing-specific verification operates on the
chosen-framing's behavior. Acknowledging the structural distinction
explicitly avoids the artifact-mixing failure mode where a
methodology-revision Part 4 pattern is applied to a documentation-
routing Part 4 substantive shape.

The validation form has two layers:

1. **Adjudication-artifact completeness check (this sub-phase).** The
   routing spec is complete iff it enumerates all candidate
   resolution layers, each with a testable framing, no layer pre-
   selected, no observation imported as resolution-layer pre-
   selection, and scope boundaries explicit at Part 3b out-of-scope
   items. The completeness check is satisfied at D8.4.7 if Part 2
   enumerates (a)-(e) layer-agnostic with open-set qualifier; Part 3a
   enumerates the five framings with one-to-one correspondence to
   Part 2 candidates and explicit observation-consumption-without-
   resolution-pre-selection language; Part 3b enumerates the four
   out-of-scope items with explicit Lock A and Lock B citations; and
   Part 6 enumerates the three drift classes with explicit Lock D
   preservation language. Completeness is the validation criterion
   for the adjudication artifact; the artifact does not need to
   prove that any specific resolution-layer choice is correct, only
   that the routing spec is complete.
2. **Framing-specific downstream verification (authorized future
   sub-phase, conditional on resolution-layer selection).** Once a
   resolution layer is selected at authorized future work, framing-
   specific verification operates on the operational behavior or
   documentation revision under that framing. The verification form
   depends on the framing: documentation-completeness framing
   verifies cross-anchor consistency post-update; operational-path
   framing verifies that the operational pipeline produces all six
   themes post-investigation or post-enforcement; candidate-
   generation framing verifies that the proposer or candidate-
   surfacing mechanism produces theme-balanced candidates post-
   investigation; methodology-acceptance framing verifies that the
   design-tolerance interpretation is documented coherently; open-
   set framing verifies the un-enumerated framing's specific
   verification surface as articulated at the future selection.

Issue 6 validates routing-spec completeness at this sub-phase;
methodology-behavior verification is deferred to authorized future
work per Lock A.

#### Part 5 — Affected rows or scope-level impact

Scope-level. No row attribution per scope lock §5 Part 5 (row
attribution is restricted to Issues 1 or 2; pos 3 and pos 138 / 143
double-duty preservation obligation is satisfied at §1.1 + §4.1 Part
5 + §4.2 Part 5). Issue 6 operates at scope level: the (multi-source
documented + canonical) ↔ (single-source operational fire) alignment
surface, not specific row identifiers. The
`multi_factor_combination` zero-call observation is a theme-level
cohort-cardinality observation, not a per-row diagnostic anchor.
Pos 138 / 143 not cited (operational-vs-documentation alignment
under-specification does not materially touch RSI-absent
`vol_regime` test-retest framing). Pos 3 not cited (Issue 6 does not
touch divergence-label cohort interpretation or score-axis
structure; double-duty preservation obligation satisfied at §1.1 +
§4.1 Part 5 + §4.2 Part 5 per scope lock §5 Part 5 "issues 1 or 2"
restriction; non-citation declaration at §4.6 Part 5 does not count
toward satisfaction floor; mirrors D8.4.4 §4.3 Part 5, D8.4.5 §4.4
Part 5, and D8.4.6 §4.5 Part 5 sealed convention).

#### Part 6 — Issue interaction check

Three drift classes now distinguished across the D8.4 sub-arc, with
Lock D six-issue boundary preserved by distinguishing rather than
merging:

- **D8.4.4 §4.3 Part 6 forward-pointer catalog (internal-presentation
  drift class).** D8.2 §9 / appendix summary tables at lines 1043,
  1073, and 1228 carry numeric and tag drift relative to the per-
  claim authoritative records at §6.2.1 (≥52/66 detailed vs ≥50/66
  summary), §6.3(a) (≥90/199 detailed vs ≥60/199 summary), §6.3(b)
  (≥30/199 detailed vs ≥40/199 summary), and §6.3 joint
  (FAIL / `derived_joint_failure` detailed vs PARTIAL /
  `asymmetric_calibration` summary). The four-row catalog routes to
  a post-D8 documentation-correction sub-phase at single-entry
  forward-pointer discipline. Drift class: internal-presentation
  drift within D8.2 between detailed records and summary tables; not
  a methodology-design gap.
- **D8.4.6 §4.5 Part 1 preamble (reference-frame variation class).**
  Scope-lock §2.3 issue 5 (line 131) and D8.4.1 §3 inventory (line
  123) cite the forensic cross-tab anchor as "§7 forensic cross-
  tab", while D8.2's own internal subsection header at line 870
  reads "§6 forensic cross-tab"; D8.4.6 prose uses "D8.2 §6 forensic
  cross-tab" matching D8.2's own internal header. Two accurate
  citation forms point to the same cross-tab content via different
  reference frames (physical container vs claim-family). Drift
  class: reference-frame variation across two accurate citation
  forms; not anchor drift; no new drift catalog entry; no
  methodology-design gap.
- **D8.4.7 (this sub-phase, documented/canonical-vs-operational-fire
  alignment drift class).** Documented + canonical sources (four
  anchors) converge on six themes; the Stage 2d operational fire at
  §6.6(3) records five themes observed with
  `multi_factor_combination` zero-call. Drift class: alignment
  surface between (multi-source documented + canonical) and (single-
  source operational fire); operational-vs-documentation alignment
  under-specification at the methodology-design layer with no
  resolution layer pre-selected at diagnosis time.

The three drift classes are structurally distinct: internal-
presentation drift operates within a single sealed artifact (D8.2)
between its detailed and summary representations; reference-frame
variation operates across multiple accurate citations of the same
content via different framing conventions; documented/canonical-vs-
operational-fire alignment drift operates across the multi-source
documentation + canonical surface and the single-source operational
observation surface. No merging into a unified drift catalog; no
seventh issue surfaced; the D8.4.4 §4.3 Part 6 four-drift catalog
remains reserved for D8.2 §9 / appendix internal-presentation drift;
the D8.4.6 §4.5 reference-frame variation acknowledgment remains
non-cataloguing; the D8.4.7 documented-vs-operational alignment is
its own distinct class. Lock D six-issue boundary held.

Forward-pointer routing for Issue 6 resolution-layer selection
deferred to authorized future sub-phase (post-D8.4 sub-arc). Routing
sub-cases by chosen framing: documentation-completeness framing, if
selected, routes to a post-D8 documentation-correction sub-phase
(distinct from D8.4.4 §4.3 Part 6 four-drift catalog; the four-drift
catalog operates on D8.2 internal-presentation drift, while Issue 6
documentation-completeness operates on documented + canonical anchor
revision); operational-path framing or candidate-generation framing,
if selected, routes to an operational-pipeline sub-phase examining
the candidate-generation, proposer-selection, or theme-coverage
surfaces; methodology-acceptance framing, if selected, routes to an
acknowledgment sub-phase recording the design-tolerance
interpretation explicitly without methodology revision; open-set
framing, if selected, routes to whichever sub-phase the un-
enumerated framing's resolution requires.

Conflicts at D8.4.7's evidence state: none observed against Issues
1, 2, 3, 4, or 5. Issue 6 operates at the operational-vs-
documentation alignment surface, which is structurally distinct from
Issues 1's divergence-label definition unit, Issue 2's direction-of-
prediction unit, Issue 3's single-floor calibration unit, Issue 4's
paired-floor calibration unit, and Issue 5's theme-conditional
surfacing mechanism unit. Potential interactions: Issue 5's theme-
conditional surfacing mechanism under-specification and Issue 6's
operational-vs-documentation alignment under-specification both
involve theme-related observations at D8.2 §6.6, but at structurally
distinct units (Issue 5 at the cell-level methodology layer per
§6.6(3) skews and adjacent material findings; Issue 6 at the theme-
cardinality alignment layer per the
`multi_factor_combination` zero-call observation). The two issues
do not collapse: Issue 5's resolution operates on the design-time
vs post-hoc surfacing question across prompt + label + cross-tab
construction; Issue 6's resolution operates on the documented-vs-
operational alignment question across multi-source documentation
and single-source observation. Reconciliation between Issue 5 and
Issue 6 resolutions, if both proceed to authorized future work,
routes to synthesis-level work, not to Issue 6 prose. D8.4.7
surfaces the *potential* interaction without resolving.

---

## 5. Synthesis

D8.4.8 collapses synthesis, forward pointers, and sub-arc closeout
into a single commit per Option C-collapsed (Charlie authorization
2026-04-25) after a candid mid-arc review surfaced that the locked
Bucket-1 sub-sequence was generating protocol-of-protocol
elaboration disproportionate to substantive output for the lighter-
density issues. The substantive findings and per-issue concrete
next actions are recorded below in plain prose; the issue-
interaction matrix follows; sub-arc seal and forward pointers
collapse into §6; Appendix D.2 records the SHA log.

### 5.1 Substantive findings and concrete next actions per issue

**Issue 1 — Divergence-label definition audit (sealed at `3a8314d`).**
The pre-registered divergence-label definition at
`stage2d_expectations.md` L77-85 carries a definitional gap that
allows record-set ambiguity at the cohort interpretation layer.
Concrete next action: decide whether the L77-85 definition needs an
amendment for the next Stage 2-class fire. Probably yes; ~1 hour to
draft a proposed amendment that closes the cohort-interpretation
ambiguity. Decision owner: Charlie. Sequencing: before next Stage 2-
class operational fire, not blocking on D8.4 closeout.

**Issue 2 — Direction-of-prediction recalibration (sealed at
`95109f7`).** D7b prompt does not elicit direction (long/short) at
the candidate level, leaving the directional interpretation to
downstream framing rather than to the Critic's pre-registered
output. Concrete next action: either fold direction-of-prediction
elicitation into the next D7b prompt iteration, or accept current
behavior with explicit documentation that direction is downstream-
inferred. Binary decision, not investigation. Decision owner:
Charlie. Sequencing: at next D7b prompt revision touch.

**Issue 3 — Lower-tail calibration (sealed at `86d69b1`).** The
pre-registered ≥30/199 lower-tail floor was missed by 4 (observed
26/199, shortfall 4, `calibration_shortfall` tag). Two paths:
(a) re-derive the floor against an explicit calibration model
before the next fire so subsequent floors are anchored on a stated
methodology rather than inherited heuristic; (b) accept the 26/199
outcome as in-tolerance and continue with the existing floor
heuristic. Binary decision. Decision owner: Charlie. Sequencing:
before next pre-registration of any Stage 2-class floor; can be
folded with Issue 4's decision since they share the calibration
question.

**Issue 4 — Paired-floor calibration coherence under derived joint
failure (sealed at `50e4731`).** Same calibration question as
Issue 3 at the paired surface (≥90/199 upper PASS with +21
headroom alongside ≥30/199 lower FAIL with -4 shortfall, joint
PASS ∧ FAIL = FAIL `derived_joint_failure`). Concrete next action:
collapses into Issue 3's calibration-model decision. If Issue 3
chooses to re-derive against an explicit calibration model, the
paired-floor coherence is naturally addressed; if Issue 3 accepts
in-tolerance, Issue 4 is also accepted as in-tolerance.

**Issue 5 — Forensic cross-tab methodology / prompt / label
discipline (sealed at `7d6378b`).** Cell-level theme-conditional
skews observed at D8.2 §6 forensic cross-tab (most notably
`mean_reversion × neutral` 71% HIGH and `volatility_regime ×
neutral` 18% HIGH). Operational question: does this theme-
conditional pattern materially affect what the pipeline produces
downstream (selection of strategies for shortlisting, alpha-
generation pathways)? If yes, the pattern shapes the next D7b
prompt or label-discipline revision; if no, the pattern stays at
evidence state as a forensic note. Concrete next action: a one-
session look at whether the cell-level skew correlates with
shortlist outcomes — if `mean_reversion × neutral` HIGH-SVR
candidates are systematically over- or under-represented in
shortlists, the pattern matters; if not, accept as forensic-only.
Decision owner: Charlie. Sequencing: before next D7b prompt or
label-discipline revision touch; not blocking.

**Issue 6 — Operational-vs-documentation alignment under-
specification (sealed at `03112aa`).** Stage 2d operational fire
produced 5 themes; documented + canonical methodology specifies 6
themes; `multi_factor_combination` produced zero calls in the
observed fire. Concrete next action: read the proposer logs and
the D6 prompt to identify why `multi_factor_combination` produced
no candidates. If candidates were generated and filtered, find the
filter; if candidates were never generated, the prompt is the
locus. ~30 minutes of work as a focused investigation. Outcome
routes to one of: (a) fix the filter or prompt to surface the
sixth theme; (b) document the design-tolerance interpretation
(operational variance accepted as in-spec); (c) document
`multi_factor_combination` as optional or theoretical in the
canonical four-anchor sources. Decision owner: Charlie. Sequencing:
30-minute task, can be done immediately or before next Stage 2-
class fire.

### 5.2 Issue-interaction matrix

Recording artifact only per scope lock §7.3. The matrix has 15
unique pairs across the 6 issues; most cells are "no substantive
interaction" because the issues operate at structurally distinct
methodological units.

| Pair | Interaction shape |
|---|---|
| 1 × 2 | No interaction (definitional vs prompt-elicitation units) |
| 1 × 3 | No interaction (definitional vs calibration units) |
| 1 × 4 | No interaction |
| 1 × 5 | No interaction (definitional vs cross-tab) |
| 1 × 6 | No interaction (definitional vs alignment) |
| 2 × 3 | No interaction (prompt vs calibration) |
| 2 × 4 | No interaction |
| 2 × 5 | Potential weak interaction (prompt-elicitation revision could affect cell-level cross-tab structure if direction-of-prediction is folded into label scheme); evidence does not require resolution |
| 2 × 6 | Potential weak interaction (prompt revision is one resolution layer for Issue 6 candidate (b)/(c); not a co-issue) |
| 3 × 4 | **Substantive interaction** (paired-floor coherence question collapses into single-floor calibration-model decision; Issue 4 resolves with Issue 3) |
| 3 × 5 | No interaction (calibration vs cross-tab structure) |
| 3 × 6 | No interaction |
| 4 × 5 | No interaction |
| 4 × 6 | No interaction |
| 5 × 6 | Potential weak interaction (both touch theme-related observations at D8.2 §6.6, but at distinct units — Issue 5 cell-level methodology, Issue 6 theme-cardinality alignment); evidence does not require resolution |

Substantive interaction count: 1 (Issue 3 × Issue 4).
Potential weak interactions: 3 (2 × 5, 2 × 6, 5 × 6).
No-interaction cells: 11.

The 6 issues cohere as a system in the sense that they are
substantively distinct rather than overlapping; the framework
produced disjoint methodology questions that can be resolved
independently except for the Issue 3 × Issue 4 calibration-model
collapse.

### 5.3 Aggregate `proposal_confidence` distribution

Issue 1: medium; Issue 2: medium; Issue 3: medium; Issue 4: medium;
Issue 5: medium-low; Issue 6: medium-low. Distribution: 4×medium +
2×medium-low. Per scope lock §5.1 strict semantics, each issue's
`proposal_confidence` is internal-coherence signal, not validation
evidence. The aggregate distribution is informational only and does
not constitute aggregate validation evidence. Lighter labels at
Issues 5 and 6 reflect open-resolution-layer uncertainty at their
respective spec levels (multi-layer methodology uncertainty for
Issue 5; open-resolution-layer uncertainty for Issue 6); they do
not signal that those issues' diagnostic findings are weaker than
Issues 1-4's findings.

### 5.4 Newly surfaced out-of-scope methodology questions (deferred)

Surfaced during D8.4 sub-arc but explicitly out of scope for
D8.4 per scope lock §3.2 / §10:

- D8.2 §9 / appendix internal-presentation drift four-row catalog
  (D8.4.4 §4.3 Part 6) — routes to post-D8 documentation-
  correction sub-phase
- Bucket 3 production-code findings from Codex audit (10
  findings) — routes to separate ~30-60 minute triage session per
  Claude advisor recommendation; **NOT bundled into D8.4 closeout**
- Future protocol iteration with "lightweight track" for
  definitional or documentation-class issues whose substantive
  scope fits in a paragraph (recorded as design observation; no
  commitment)

---

## 6. Forward Pointers and Sub-arc Seal

### 6.1 Per-issue forward pointers

Per-issue receiving phase / decision owner / sequencing collapsed
into §5.1 substantive findings above (each issue's "Concrete next
action" + "Decision owner" + "Sequencing" lines). Explicit non-
promise: D8.4 does not commit any future phase's scope; each per-
issue concrete next action is a recommendation Charlie can adopt,
modify, or decline.

### 6.2 Bucket 3 production-code triage routing

Codex independent verification at D8.4.7 surfaced 10 production-
code findings (Bucket 3). These are deferred to a separate ~30-60
minute triage session per the discipline that Bucket 3 should not
be bundled into D8.4 closeout. Triage prompt template (Claude
advisor recommendation):

- **Fix now:** patch the file, commit, done. Highest priority for
  `bulk_download.py` canonical-write-without-archive (HIGH severity;
  the operational guardrail dissipates after D8.4 closes) and
  `dsl_compiler.py` filename-inconsistency-with-CLAUDE.md-spec
  (will silently bite future code that trusts the spec).
- **Fix at next data refresh / next code touch:** defer until the
  file is being opened anyway. Probably right for parquet-feed
  fabrication and `incremental_update` fallback (only fire under
  specific conditions).
- **Accept as documented risk:** write 1-2 sentences in CLAUDE.md
  or a code comment naming the risk and why. Probably right for
  broad-catch strategy import and git metadata try/except: pass
  (low severity, low blast radius).

Per finding: ~3-5 minutes to triage. Total session: ~30-45 minutes.
The `bulk_download` fix itself is ~15-20 minutes of code (add
archive-before-canonical-write).

### 6.3 Process Notes 36-44 brief summary

Process Notes captured during the D8.4 sub-arc — the genuinely
useful disciplines that prevented real defects, recorded here as
brief text (3-5 sentences each) rather than canonical text commits
per Option C-collapsed simplification. Sub-clauses, sub-refinements,
and three-layer framings are recoverable from the conversation
transcript if a future sub-arc of similar shape requires them.

- **PN 36 (numeric anchor cross-check, authoring):** Authors
  cross-check numeric anchors against per-claim authoritative
  sources before drafting prose, not against summary-table
  inheritance. Caught the ≥30/199 vs ≥40/199 drift at D8.4.4 R1
  before any prose was authored. Generalizes to: pre-execution
  gates inheriting canonical composition must verify against
  sealed source (Bash invocation extraction, sealed commit body
  text, or sealed appendix), not against recollection.
- **PN 37 (reviewer numeric anchor cross-check):** Reviewers verify
  authored numeric anchors against same authoritative sources;
  catches drift that survives author-side checks. Operating cleanly
  across all six issue prose ratifications.
- **PN 38 (sub-phase-boundary independent verification):** Round 2
  prose ratification requires verbatim inline prose-paste in the
  conversation transcript, not on-disk content + line-index map.
  The conversation transcript is the canonical record of what was
  ratified; on-disk-only ratification creates audit-trail gaps.
- **PN 39 (convergence-check explicitness):** Parallel reviewer
  verdicts must convert procedural-acknowledgment-class responses
  to explicit per-item PASS/FAIL via Option A discipline before
  convergence-check. Discipline-fatigue signal observed: comparative-
  framing residuals against scope-lock §5.1 reproduced at decreasing
  severity across iterations.
- **PN 40 (temporal-boundary discipline):** Methodology specs
  preserve explicit non-collapse statements between temporal layers
  (ex-ante pre-registration vs ex-post observation) and between
  spec-internal layers (layer-agnostic vs implementation). Generalized
  scope-coherence pattern.
- **PN 41 (chain-trust verification):** Chain-trust applies to
  reviewer claims, reviewer recommendations, implementer's prior
  precedent citations, implementer's own pre-execution-gate
  composition, and reviewer's own recollection-based proposals.
  Symmetric application across all five sub-clauses.
- **PN 42 (operational guardrails):** Production-code findings with
  HIGH severity that are dormant only because of runtime context
  (no data refresh during sub-arc) require explicit invocation +
  modification gating during the sub-arc, with follow-through in a
  separate triage session before the gating dissipates. Applied to
  `bulk_download.py` canonical-write-without-archive at D8.4.7.
- **PN 43 (scope-lock inheritance broaden discipline):** Three-
  instance discipline pattern observed: D8.4.5 §4.4 title retirement
  (`asymmetric_calibration` → scope-explicit), D8.4.6 §4.5 Part 2
  broaden (prompt-design-primary → theme-conditional surfacing),
  D8.4.7 §4.6 issue retitle (Documentation drift → operational-vs-
  documentation alignment under-specification). Inherited scope-lock
  framings can be broadened within issue substantive boundary when
  pre-outline anchor verification surfaces structural compression.
- **PN 44 (SHA gate three-layer composition):** SHA gate composition
  has three layers — (a) scope-lock-anchored textual canonical;
  (b) sub-phase-specific active-edit target extension; (c) sub-
  phase-specific evidence extensions. Layer (b) emerged at D8.4.4
  R2 as additive practice without explicit scope-lock amendment.
  Future sub-arcs inheriting D8.4 patterns either textually seal
  layer (b) or accept behavioral-provenance discipline.

### 6.4 Mid-arc review and Option C-collapsed adoption

Mid-arc review at D8.4.7 → D8.4.8 boundary (Claude advisor stepping
out of role; ChatGPT concurrence; implementer concurrence; Charlie
authorization) surfaced that the locked Bucket-1 sub-sequence was
generating protocol-of-protocol elaboration disproportionate to
substantive output for definitional / documentation-class issues
(Issues 1, 2, 6 lighter than Issues 3, 4, 5). Option C-collapsed
adopted: single closeout commit (this commit) instead of three
sub-phases (synthesis / forward pointers / closeout) at full Bucket-
1 cadence. Substantive findings preserved; protocol-of-protocol
elaboration absorbed into the brief Process Notes summary above.
Worth recording for future sub-arc design: the Bucket-1 sub-sequence
is structurally appropriate for calibration / paired-floor / cross-
tab methodology depth; a lightweight track is worth designing for
definitional / documentation-class issues.

### 6.5 Sub-arc seal

D8.4 methodology refinement sub-arc closes with this commit. Issues
1-6 sealed at their per-issue commits. The substantive findings,
concrete next actions, and Bucket 3 routing-to-separate-session
constitute the operational output of the sub-arc. Phase 2C strategy
mining is the next priority.

---

## 7. Phase 2C Priority Statement

The pipeline's purpose is BTC algorithmic trading alpha. D8.4 was
methodology refinement on a Stage 2d critic forensic exercise and
is now closed. The next priority is Phase 2C strategy mining; the
methodology questions surfaced at Issues 1-6 are recommendations
Charlie can adopt, modify, or decline at the appropriate operational
touch points (D7b prompt revision, pre-registration for next Stage
2-class fire, or as separate focused investigations). No sub-phase
commitment beyond this commit.

---

## Appendix D — D8.4 Sub-arc SHA Log

*Populated incrementally across D8.4.x commits and finalized in
D8.4.10.*

### D.1 D8.4.1 pre-authoring SHA verification (8-anchor gate)

The 8-anchor pre-authoring SHA gate (scope lock §6.4) was run before
D8.4.1 authoring. All eight anchors byte-matched the values locked in
§2.2; no drift was detected. The gate output is recorded here so the
gate is in-document, not chat-only.

| File | Pre-authoring SHA-256 (D8.4.1 turn) | Status |
|---|---|---|
| `docs/d8/D8_4_SCOPE_LOCK.md` | `43f7e09851e86788677af2518379a35a9e5d565de80fff9c66e8a6c4037f8bac` | match |
| `docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md` | `542c359977c1a19c6e2958b92ad9cb34b47f60606061694e875de91f2cc26b6f` | match |
| `docs/d8/D8_3_SCOPE_LOCK.md` | `f0a5598b34342fb72277d5b344152e0efd6f05bd918699e880b776ead633439c` | match |
| `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` | `89d54c9821bb754d17b7085dbe6f344403da5b49824236aa8f1ee301003b4914` | match |
| `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` | match |
| `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` | match |
| `docs/d7_stage2d/stage2d_expectations.md` | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` | match |
| `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` | match |

Subsequent D8.4.x sub-phases append their own pre-authoring gate
records under D.2, D.3, ... in the same format.

### D.2 D8.4 sub-arc commit SHA log

Sub-arc closed at D8.4.8 per Option C-collapsed (sub-phases D8.4.9
and D8.4.10 absorbed into this commit; original 11-sub-phase plan
collapsed to 9 actual commits).

| Sub-phase | Commit | Date (UTC) | Notes |
|---|---|---|---|
| D8.4.0 (scope lock) | `7841a89` | 2026-04-24 | Methodology refinement scope locked |
| D8.4.1 (skeleton) | `eaf8d63` | 2026-04-24 | Skeleton commit; per-issue analysis deferred to D8.4.2-D8.4.7 |
| D8.4.2 (Issue 1) | `3a8314d` | 2026-04-24 | Divergence-label definition audit |
| D8.4.3 (Issue 2) | `95109f7` | 2026-04-24 | Direction-of-prediction recalibration |
| D8.4.4 (Issue 3) | `86d69b1` | 2026-04-24 | Lower-tail calibration |
| D8.4.5 (Issue 4) | `50e4731` | 2026-04-24 | Paired-floor calibration coherence under derived joint failure |
| D8.4.6 (Issue 5) | `7d6378b` | 2026-04-25 | Forensic cross-tab methodology / prompt / label discipline |
| D8.4.7 (Issue 6) | `03112aa` | 2026-04-25 | Operational-vs-documentation alignment under-specification |
| D8.4.8 (closeout) | *(this commit)* | 2026-04-25 | Synthesis + forward pointers + sub-arc seal collapsed per Option C-collapsed |
