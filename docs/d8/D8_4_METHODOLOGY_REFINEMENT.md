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

*Populated in D8.4.3.*

`proposal_confidence`: *(declared in D8.4.3)*

#### Part 1 — Diagnosis

*Populated in D8.4.3.*

#### Part 2 — Root cause

*Populated in D8.4.3.*

#### Part 3a — Proposed revision spec

*Populated in D8.4.3.*

#### Part 3b — Expected behavior change

*Populated in D8.4.3.*

#### Part 4 — Validation plan

*Populated in D8.4.3.*

#### Part 5 — Affected rows or scope-level impact

*Populated in D8.4.3. Row-anchored issue: cohort `{1, 2, 3, 5, 6}`
expected; **pos 3 double-duty (§1.1)** must be restated explicitly.*

#### Part 6 — Issue interaction check

*Populated in D8.4.3.*

---

### 4.3 Issue 3 — Lower-tail calibration

*Populated in D8.4.4.*

`proposal_confidence`: *(declared in D8.4.4)*

#### Part 1 — Diagnosis

*Populated in D8.4.4.*

#### Part 2 — Root cause

*Populated in D8.4.4.*

#### Part 3a — Proposed revision spec

*Populated in D8.4.4.*

#### Part 3b — Expected behavior change

*Populated in D8.4.4.*

#### Part 4 — Validation plan

*Populated in D8.4.4.*

#### Part 5 — Affected rows or scope-level impact

*Populated in D8.4.4. Scope-level issue: no row attribution.*

#### Part 6 — Issue interaction check

*Populated in D8.4.4.*

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
