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

*Populated in D8.4.2.*

`proposal_confidence`: *(declared in D8.4.2)*

#### Part 1 — Diagnosis

*Populated in D8.4.2.*

#### Part 2 — Root cause

*Populated in D8.4.2.*

#### Part 3a — Proposed revision spec

*Populated in D8.4.2.*

#### Part 3b — Expected behavior change

*Populated in D8.4.2.*

#### Part 4 — Validation plan

*Populated in D8.4.2.*

#### Part 5 — Affected rows or scope-level impact

*Populated in D8.4.2. Row-anchored issue: cohort `{1, 2, 3, 5, 6}`
expected; **pos 3 double-duty (§1.1)** must be restated explicitly.*

#### Part 6 — Issue interaction check

*Populated in D8.4.2.*

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
