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

### 4.4 Issue 4 — Joint-shape asymmetric-calibration implications

*Populated in D8.4.5.*

`proposal_confidence`: *(declared in D8.4.5)*

#### Part 1 — Diagnosis

*Populated in D8.4.5.*

#### Part 2 — Root cause

*Populated in D8.4.5.*

#### Part 3a — Proposed revision spec

*Populated in D8.4.5.*

#### Part 3b — Expected behavior change

*Populated in D8.4.5.*

#### Part 4 — Validation plan

*Populated in D8.4.5.*

#### Part 5 — Affected rows or scope-level impact

*Populated in D8.4.5. Scope-level issue: no row attribution.*

#### Part 6 — Issue interaction check

*Populated in D8.4.5.*

---

### 4.5 Issue 5 — Forensic cross-tab methodology / prompt / label discipline

*Populated in D8.4.6.*

`proposal_confidence`: *(declared in D8.4.6)*

#### Part 1 — Diagnosis

*Populated in D8.4.6.*

#### Part 2 — Root cause

*Populated in D8.4.6.*

#### Part 3a — Proposed revision spec

*Populated in D8.4.6.*

#### Part 3b — Expected behavior change

*Populated in D8.4.6.*

#### Part 4 — Validation plan

*Populated in D8.4.6.*

#### Part 5 — Affected rows or scope-level impact

*Populated in D8.4.6. Cross-tab issue: cell-level evidence, no row
positions.*

#### Part 6 — Issue interaction check

*Populated in D8.4.6.*

---

### 4.6 Issue 6 — Documentation drift

*Populated in D8.4.7.*

`proposal_confidence`: *(declared in D8.4.7)*

#### Part 1 — Diagnosis

*Populated in D8.4.7.*

#### Part 2 — Root cause

*Populated in D8.4.7.*

#### Part 3a — Proposed revision spec

*Populated in D8.4.7.*

#### Part 3b — Expected behavior change

*Populated in D8.4.7.*

#### Part 4 — Validation plan

*Populated in D8.4.7.*

#### Part 5 — Affected rows or scope-level impact

*Populated in D8.4.7. Documentation-only issue: no row attribution.*

#### Part 6 — Issue interaction check

*Populated in D8.4.7.*

---

## 5. Synthesis

*Populated in D8.4.8.*

Cross-issue themes, the **issue-interaction matrix** (recording
artifact only — MUST NOT propose joint or cross-issue fixes per scope
lock §7.3), newly surfaced (out-of-scope) methodology questions
deferred to a future phase, aggregate impact on D8.3
METHOD-QUESTION rows + scope-level implications, and the aggregate
`proposal_confidence` distribution across the six issues
(informational, not gating).

---

## 6. Forward Pointers

*Populated in D8.4.9.*

Per-issue forward pointer specifying receiving phase, implementation
owner, validation owner, and explicit non-promise that D8.4 does not
commit any future phase's scope.

---

## 7. Closeout

*Populated in D8.4.10.*

Full SHA log across the D8.4 sub-arc commits (mirroring D8.3 Appendix
D discipline), invariant verification log, and D8.4 sub-arc seal
entry.

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

| Sub-phase | Commit | Document SHA | Date (UTC) |
|---|---|---|---|
| D8.4.0 | `7841a89` | scope lock at `43f7e09851e86788677af2518379a35a9e5d565de80fff9c66e8a6c4037f8bac` | 2026-04-24 |
| D8.4.1 | *(this commit)* | *(captured in D8.4.10)* | 2026-04-24 |
| D8.4.2 | *(D8.4.2)* | *(D8.4.10)* | *(D8.4.10)* |
| D8.4.3 | *(D8.4.3)* | *(D8.4.10)* | *(D8.4.10)* |
| D8.4.4 | *(D8.4.4)* | *(D8.4.10)* | *(D8.4.10)* |
| D8.4.5 | *(D8.4.5)* | *(D8.4.10)* | *(D8.4.10)* |
| D8.4.6 | *(D8.4.6)* | *(D8.4.10)* | *(D8.4.10)* |
| D8.4.7 | *(D8.4.7)* | *(D8.4.10)* | *(D8.4.10)* |
| D8.4.8 | *(D8.4.8)* | *(D8.4.10)* | *(D8.4.10)* |
| D8.4.9 | *(D8.4.9)* | *(D8.4.10)* | *(D8.4.10)* |
| D8.4.10 | *(D8.4.10)* | *(D8.4.10)* | *(D8.4.10)* |
