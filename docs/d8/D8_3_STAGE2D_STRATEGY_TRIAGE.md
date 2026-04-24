# D8.3 Stage 2d Strategy Triage

**Sub-phase state (this commit):** D8.3.1 — framing skeleton only.

**Document status:** blank-by-intent for candidate-level content. The
container, framing, schemas, and appendix structure are authored here;
per-candidate bucket assignments, Tier B overrides, test-retest
analysis, and synthesis are intentionally deferred to the D8.3.2–D8.3.5
sub-phases per the scope lock §9 plan.

**Governing authority:** [`docs/d8/D8_3_SCOPE_LOCK.md`](./D8_3_SCOPE_LOCK.md)
(sealed commit `a6630e8`, file SHA
`f0a5598b34342fb72277d5b344152e0efd6f05bd918699e880b776ead633439c`, 453
lines). Any divergence from scope lock text is a defect in this document,
not a revision of scope.

**Relationship to sealed D8 layers:**
- D8.0 phase signoff (`1fb1161c...c5e998`) — unchanged; provides the
  phase-closeout operational record and artifact integrity findings.
- D8.1 aggregate analysis notebook (`20f58ed8...c6bc6d60` at `ac2586b`) —
  unchanged; provides cohort-level numerical facts.
- D8.2 claim-level adjudication (`89d54c98...003b4914`) — unchanged;
  provides the claim-level verdict taxonomy that constrains METHOD-QUESTION
  routing in §4.3 of the scope lock.

D8.3 does **not** re-adjudicate any of these. It consumes them as binding
context and routes already-scored Stage 2d candidates into practical
strategy-disposition buckets.

---

## D8.3.1 discipline note — blank by intent

This document starts as a container for evidence-based disposition.
Candidate assignments are intentionally blank until D8.3.2. Any candidate
bucket must cite a D8.1 / D8.2 evidence anchor and must not rely on
subjective preference. No section in this D8.3.1 commit makes a
candidate-level disposition decision. Sections that will receive
per-candidate content in later sub-phases are explicitly marked
"Populated in D8.3.X" at their heading.

---

## 1. Purpose and Scope

### 1.1 Purpose (verbatim from scope lock §1)

> **D8.3 is evidence-based strategy disposition. It is not a new
> research claim adjudication, not a methodology-fix phase, and not a
> backtest-selection beauty contest.**

D8.3 authors this document by classifying each of the 197 ok-scored
Stage 2d candidates into one of five practical buckets (§4) using
evidence anchored in D8.1 and D8.2. No new LLM calls, no new backtests,
no re-scoring, no methodology fixes.

### 1.2 What D8.3 produces

- A master triage table assigning exactly one bucket to each of the
  197 ok-scored candidates (§7 schema; rows populated in D8.3.2).
- Per-bucket analytical subsections synthesising the rationale for
  each bucket's population (§8; populated in D8.3.3).
- A dedicated test-retest analysis for the RSI-absent vol_regime twin
  candidates pos 138 / 143 (§9; populated in D8.3.4).
- A synthesis of bucket-level findings and forward pointers into D8.4
  (METHOD-QUESTION routings) and any downstream Stage 2e+ or live-fire
  planning (§10–§11; populated in D8.3.5).
- Four appendices covering cohort reconciliation, rule-based bucket
  eligibility, discretionary overrides, and per-turn SHA verification.

### 1.3 What D8.3 does not do

Per scope lock §4.2:

- No new LLM calls, no new backtests, no production code changes.
- No re-scoring of candidates; no new SVR / alignment / plausibility
  values.
- No re-adjudication of D8.2 claim verdicts.
- No amendment of D8.0, D8.1, or D8.2 sealed text.
- No methodology fixes. Methodology questions surface as
  METHOD-QUESTION bucket routings; D8.4 owns methodology decisions.
- No Phase 3+ trading decisions. D8.3 is research-layer triage only.
- No pre-committed target count for any bucket. Bucket counts are
  outputs, not goals.
- No silent re-scoring: any perceived SVR threshold or score
  discrepancy surfaces as METHOD-QUESTION, never as D8.3 rescoring.

---

## 2. Anchored Inputs

Per scope lock §2.2, the following six file SHAs MUST byte-match at
the start of every D8.3.x authoring turn. Any mismatch is a
foundation break and blocks authoring until reconciled. SHA values
recorded here reflect the state at D8.3.1 authoring:

| # | Path | Expected SHA256 |
|---|---|---|
| 1 | `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` |
| 2 | `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` |
| 3 | `docs/d7_stage2d/stage2d_expectations.md` | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` |
| 4 | `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` (at commit `ac2586b`) | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` |
| 5 | `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` | `89d54c9821bb754d17b7085dbe6f344403da5b49824236aa8f1ee301003b4914` |
| 6 | `docs/d8/D8_3_SCOPE_LOCK.md` | `f0a5598b34342fb72277d5b344152e0efd6f05bd918699e880b776ead633439c` |

The per-turn byte-match history is recorded in Appendix D.

---

## 3. Governing Authority — D8.3.0 Scope Lock

D8.3.0 was sealed in commit `a6630e8` with file SHA
`f0a5598b34342fb72277d5b344152e0efd6f05bd918699e880b776ead633439c`
(453 lines). It is the binding constitution for every D8.3.x
sub-phase.

The following elements of the scope lock are reproduced or referenced
in this document for operational convenience, but the scope lock file
itself is the source of truth. Any inconsistency between this
document and the scope lock resolves in favour of the scope lock.

- §1 Purpose (reproduced verbatim in §1.1 above).
- §3 Strategy Triage Bucket Taxonomy (copied in §4 below).
- §3.3 Quarantine (referenced in §6 below).
- §3.4 Rebuttable METHOD-QUESTION presumption (referenced in §8.5
  stub).
- §4.3 Six D8.4 methodology issues (referenced in §8.5 stub).
- §5 Evidence Anchor Schema (copied in §7 below).
- §6 Authoring Discipline (referenced in §5 below).

Any D8.3.x authoring turn MUST re-read the scope lock before making
disposition decisions. Paraphrase is not sufficient; cite by section
and sub-phase as needed.

---

## 4. Bucket Taxonomy

Copied from scope lock §3. Five buckets, mutually exclusive. Every row
in the master triage table assigns exactly one bucket.

### 4.1 Bucket enum

| Bucket | Short meaning |
|---|---|
| `KEEP` | Candidate has strong evidence of practical research value and no unresolved methodology blocker |
| `REVIEW` | Candidate has mixed signal and deserves human inspection before keep/drop |
| `DEFER` | Candidate is valid, but decision depends on later non-methodological work (e.g., test-retest, cohort comparison) |
| `DROP-DUPLICATIVE` | Candidate is validly scored but has high structural variant risk and no offsetting reason to keep |
| `METHOD-QUESTION` | Candidate's triage is blocked because the scoring or labeling logic itself is under question (needs D8.4 input) |

No sixth bucket. Structural exclusions (pos 42 / 87 / 116) are not
bucketed — they are quarantined (§6).

### 4.2 Bucket definitions (binding)

**`KEEP`.** Candidate has explicit evidence of practical research
value: low/moderate SVR with acceptable plausibility and alignment,
or strategically important fresh-7 / overlap behavior, or membership
in a D8.2-passed claim cohort. Requires no unresolved D8.4
methodology blocker. Requires primary_evidence + evidence_anchor +
rationale.

**`REVIEW`.** Candidate has mixed signal — some KEEP-ward evidence,
some DROP-ward evidence — and a reviewer should inspect before final
disposition. **If a candidate lacks enough evidence for KEEP or
DROP, default to REVIEW, not subjective preference.** REVIEW is the
correct home for genuinely ambiguous usable records; it is not a
catch-all for "I don't want to decide."

**`DEFER`.** Candidate is validly scored and not blocked by a D8.4
methodology question, but its disposition depends on later
non-methodological work. Examples: pos 138 / 143 pending D8.3.4
test-retest outcome; cross-cohort comparison that will mature in a
later D8.3.x sub-phase.

**`DROP-DUPLICATIVE`.** Candidate is validly scored but high
structural variant risk with no offsetting reason to keep. High SVR
alone is **not** sufficient for DROP-DUPLICATIVE — an explicit
rationale such as "high SVR plus high prior overlap" or "high SVR
with no special cohort membership and no unique theme coverage" is
required. The primary_reason must name the structural redundancy
explicitly.

**`METHOD-QUESTION`.** Candidate's triage is blocked because the
scoring or labeling logic itself is under question. Routes to D8.4
methodology refinement. Includes all candidates whose disposition
depends on any of the six D8.2-sealed D8.4 methodology issues (scope
lock §4.3). This bucket has the highest downstream consequence and is
subject to 100% spot-check (§5.4).

METHOD-QUESTION is reserved for candidates whose disposition
materially depends on a known D8.4 methodology issue. It must cite
the specific D8.4 issue. Ambiguous-but-triable candidates go to
REVIEW, not METHOD-QUESTION.

METHOD-QUESTION is not a weak REVIEW bucket; it requires an
explicit D8.4-dependent methodology issue.

### 4.3 Rebuttable METHOD-QUESTION presumption (narrow)

Per scope lock §3.4, the five §6.2.2 divergence_expected cohort
positions (pos 1, 2, 3, 5, 6) start as METHOD-QUESTION by default,
rebuttable only with an explicit evidence-based override. Other
D8.2-derived concerns (e.g., §6.3(b) lower-tail members, §6 forensic
cross-tab cell members) follow the general Tier A / Tier B discipline
without the specific rebuttable-presumption semantics. Pos 3 is
flagged high-scrutiny due to its double-duty status (§6.2.2
divergence cohort ∩ §6.4 fresh-7 PASS contributor under opposite
directional hypotheses), but scope lock does not pre-bake pos 3's
bucket. Full mechanics are in scope lock §3.4.

This D8.3.1 commit asserts the rule. Per-candidate application to pos
1 / 2 / 3 / 5 / 6 is deferred to D8.3.3 with 100% spot-check discipline.

---

## 5. Methodology Recap

### 5.1 Tier A — rule-governed bucket eligibility

Tier A routings apply a deterministic rule over evidence already
sealed in D8.1 / D8.2. The per-rule matrix is Appendix B (populated
in D8.3.2). Examples of Tier A rule shapes (non-exhaustive, to be
codified in Appendix B):

- Candidates with `pre_registered_label = agreement_expected` and
  `svr >= 0.5` within the §6.2.1 PASS cohort receive a rule-governed
  KEEP-ward candidacy anchor (specific bucket still requires
  per-candidate evidence).
- Candidates matching scope lock §4.3's six D8.4 issue anchors receive
  a rule-governed METHOD-QUESTION routing.
- Candidates with `exclusion_reason` ∈ {`d7b_error`,
  `skipped_source_invalid`} are quarantined per §6 and do not receive
  bucket assignments.

### 5.2 Tier B — discretionary with dual-anchor justification

Tier B routings apply when a Tier A rule does not uniquely fix the
bucket. Each Tier B assignment MUST populate both
`primary_evidence` and `secondary_evidence` fields in the master
table (§7 schema); a single-anchor Tier B routing is invalid. The
discretionary override log (Appendix C, populated in D8.3.3) records
every Tier B override for audit.

Rebuttable-presumption overrides on the five §6.2.2 divergence
positions count as Tier B overrides for spot-check purposes (scope
lock §6.2).

### 5.3 7-field evidence-anchor schema

Every row in the master triage table populates exactly seven fields.
Copied from scope lock §5:

| Field | Type | Required | Description |
|---|---|---|---|
| `position` | int | yes | Stage 2d candidate position (1–200) |
| `bucket` | enum | yes | One of the five buckets in §4.1; `quarantined` for pos 42/87/116 (Appendix A only) |
| `primary_evidence` | string | yes | Principal evidence anchor justifying the bucket, cited by D8.1 / D8.2 section + notebook cell / adjudication table row |
| `secondary_evidence` | string | conditional | Required for Tier B and rebuttable-presumption-override rows; optional for pure Tier A rows |
| `evidence_anchor` | string | yes | Machine-citable reference (e.g., `D8.1 cell 12`, `D8.2 §6.2.1 row 64`, `stage2d_aggregate_record pos 47`) |
| `rationale` | string | yes | Plain-language justification mapping evidence to bucket, ≤ 3 sentences |
| `d8_followup` | string | conditional | Required for METHOD-QUESTION (cites specific D8.4 issue from scope lock §4.3) and DEFER (cites downstream sub-phase) rows |

### 5.4 Spot-check discipline

Per scope lock §6.2:

- **100% of METHOD-QUESTION bucket rows** are spot-checked by
  triangulated review (Claude advisor + ChatGPT critic) during
  D8.3.x Round 1 or Round 2 review.
- **10% of other Tier B / override assignments** are randomly
  sampled for triangulated review each review round. If 10% yields
  a non-integer, round up.
- Rebuttable-presumption overrides on the five §6.2.2 divergence
  positions count as Tier B overrides for spot-check purposes.

### 5.5 Hard rule inheritance

- **Hard rule 5** (no reinterpretation of pre-registered claims)
  extends into D8.3 unchanged. D8.3 consumes D8.2 verdicts; it does
  not reinterpret pre-registered Stage 2d claims.
- **No silent re-scoring** applies throughout. Any perceived SVR
  discrepancy or threshold disagreement surfaces as a
  METHOD-QUESTION, never as a D8.3 rescoring.

### 5.6 Default-to-REVIEW

Repeated for emphasis: **if a candidate lacks enough evidence for
KEEP or DROP, default to REVIEW, not subjective preference.** REVIEW
is the correct home for genuinely ambiguous usable records.

---

## 6. Cohort Accountability

The cohort boundaries are fixed by the sealed Stage 2d aggregate
record (anchor #2 in §2) and the D8.2 adjudication (anchor #5). D8.3
does not alter any denominator.

| Universe | Count | Content |
|---|---|---|
| Stage 2d source positions | 200 | All Stage 2d candidates, including skipped and errored |
| UB call cohort | 199 | 200 minus pos 116 (`skipped_source_invalid`) |
| Ok-scored universe (primary triage universe) | 197 | 199 minus pos 42 and pos 87 (`d7b_error`) |
| Quarantined | 3 | pos 42, pos 87, pos 116 |

Per scope lock §3.3:

| Position | `exclusion_reason` | Excluded from |
|---|---|---|
| 42 | `d7b_error` | 197 scored universe |
| 87 | `d7b_error` | 197 scored universe |
| 116 | `skipped_source_invalid` | 199 UB cohort (and 197 scored universe) |

Positions 42 and 87 remain members of the 199-call UB cohort for
pre-registered aggregate-denominator accounting, but they are
excluded from D8.3 strategy triage because no D7b score exists.
Position 116 is excluded from both the 199-call UB cohort and the
197 scored universe.

Full per-row cohort reconciliation is Appendix A (populated in D8.3.2).

---

## 7. Master Triage Table

*Populated in D8.3.2.*

The master triage table covers all 197 ok-scored positions with one
row per candidate, seven fields per row per §5.3 schema. Quarantined
positions (42, 87, 116) do not appear in the master table; they are
accounted for in Appendix A.

### 7.1 Column header (fixed in D8.3.1)

The fixed header below contains the seven required evidence fields
per §5.3 schema in the exact order `position | bucket |
primary_evidence | secondary_evidence | evidence_anchor | rationale |
d8_followup`. These seven columns MUST appear in the D8.3.2
master-table population; the `evidence_anchor` column name matches
the canonical scope-lock §5 field name. Optional extra metadata
columns (e.g., `theme`, `svr`) are permitted to the right of
`d8_followup` for reviewer convenience, but they MUST NOT displace
any of the seven required columns.

| `position` | `bucket` | `primary_evidence` | `secondary_evidence` | `evidence_anchor` | `rationale` | `d8_followup` |
|---|---|---|---|---|---|---|
| *int 1–200 (minus 42, 87, 116)* | *enum: KEEP / REVIEW / DEFER / DROP-DUPLICATIVE / METHOD-QUESTION* | *string* | *string (conditional)* | *string* | *string, ≤3 sentences* | *string (conditional)* |

### 7.2 Row ordering discipline

Rows MUST be sorted by `position` ascending. Sub-grouping by bucket
occurs only in §8 per-bucket analytical subsections, not in the
master table.

### 7.3 Row count invariant

Total master-table rows MUST equal 197. Any deviation is a defect.
The invariant is re-checked at D8.3.2 close and at D8.3.5 synthesis.

### 7.4 No-assignments-in-D8.3.1 restatement

No rows are populated in this D8.3.1 commit. The table body is
intentionally blank until D8.3.2. **Any non-placeholder candidate
row added before D8.3.2 is a scope violation.**

---

## 8. Per-Bucket Analysis

*Populated in D8.3.3.*

Each subsection analyses the bucket's population after D8.3.2 closes
and presents: bucket count, Tier A vs Tier B composition, salient
sub-cohorts (e.g., divergence cohort members inside METHOD-QUESTION),
and any cross-cutting observations. No new claims are adjudicated;
analysis is evidence-anchored per §5.

### 8.1 KEEP
*Populated in D8.3.3.*

### 8.2 REVIEW
*Populated in D8.3.3.*

### 8.3 DEFER
*Populated in D8.3.3.*

### 8.4 DROP-DUPLICATIVE
*Populated in D8.3.3.*

### 8.5 METHOD-QUESTION
*Populated in D8.3.3, with:*
- 100% triangulated spot-check per §5.4.
- Per-candidate citation of the specific scope lock §4.3 methodology
  issue (D8.4 anchor) that governs the routing.
- Explicit resolution of the rebuttable-presumption overrides for
  pos 1 / 2 / 3 / 5 / 6, including pos 3's double-duty treatment.

---

## 9. RSI-Absent Vol_Regime Test-Retest (pos 138 / 143)

*Populated in D8.3.4.*

Pos 138 and pos 143 are the fresh-7 RSI-absent vol_regime twin
candidates flagged in D8.0 (§L149 routing) for dedicated test-retest
analysis. D8.3.4 authors this subsection using only D8.1 / D8.2
evidence anchors; no new backtests or LLM calls. Bucket assignment
for pos 138 and pos 143 is deferred until D8.3.4 concludes; both
positions receive `DEFER` provisionally in D8.3.2 with
`d8_followup = "D8.3.4 test-retest"` per §5.3 schema.

---

## 10. Synthesis

*Populated in D8.3.5.*

Bucket-level synthesis, cross-bucket observations, lineage-integrity
re-affirmations, and closing adjudication for the D8.3 sub-arc.

---

## 11. Forward Pointers

*Populated in D8.3.5.*

- METHOD-QUESTION routings → D8.4 methodology-refinement sub-arc.
- DEFER routings (other than pos 138 / 143) → downstream D8.3.x or
  Stage 2e+ planning.
- KEEP routings → Stage 2e+ or live-fire planning inputs.
- DROP-DUPLICATIVE routings → no downstream routing required;
  archival only.

---

## Appendices

### Appendix A — Cohort and Quarantine Reconciliation

*Populated in D8.3.2.*

Full 200-row reconciliation: 197 ok-scored rows (cross-referenced to
master table §7) plus 3 quarantined rows (pos 42, 87, 116) with
`exclusion_reason`, `excluded_from`, and evidence anchor to the
D8.1 / D8.2 source. Row total MUST equal 200.

### Appendix B — Rule-Based Bucket Eligibility Matrix

*Populated in D8.3.2.*

Matrix of Tier A rules (§5.1) × eligible buckets, with the specific
scope-lock anchor that grounds each rule. Provides auditable mapping
from rule input → rule output. Every Tier A row in the master table
(§7) cites a rule from this matrix.

### Appendix C — Discretionary Override Log

*Populated in D8.3.3.*

Per-override record for every Tier B assignment and every
rebuttable-presumption override. Each entry includes position,
bucket, dual-anchor citation (primary + secondary), rationale, and
spot-check outcome (for the 100% METHOD-QUESTION subset and the 10%
round-up sample of other Tier B).

Fixed column schema for Appendix C entries (D8.3.1-locked; D8.3.3
populates rows, does not alter header):

| `position` | `default_bucket` | `override_bucket` | `override_reason` | `evidence_anchor` | `reviewer_check` |
|---|---|---|---|---|---|
| *int* | *enum of 5 buckets or `rebuttable_MQ`* | *enum of 5 buckets* | *string* | *string (D8.1/D8.2 citation)* | *string: `spot_checked` / `sampled_10pct` / `not_sampled`* |

This schema matters for pos 3 (double-duty) and every rebuttable
presumption override on the five §6.2.2 divergence positions
(pos 1, 2, 3, 5, 6).

### Appendix D — SHA Verification Log

*Populated incrementally; closed in D8.3.5.*

Per-turn 6-anchor byte-match verification history. Each entry
records: sub-phase (D8.3.x), turn timestamp or commit ref, all six
expected SHAs, all six observed SHAs, match status. Any mismatch is a
foundation break and is recorded with remediation notes.
