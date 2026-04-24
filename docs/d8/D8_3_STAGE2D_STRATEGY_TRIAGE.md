# D8.3 Stage 2d Strategy Triage

**Sub-phase state (this commit):** D8.3.2a — mechanical scaffold
(master-table metadata rows + Appendix A cohort reconciliation + Appendix B
Tier A rule matrix). No bucket assignments, Tier B overrides, rationale, or
`d8_followup` are authored in this commit.

**Document status:** container, framing, schemas, and appendix structure
were authored in the D8.3.1 skeleton commit (`1703d1f`). This D8.3.2a
commit populates the §7 master-table body with 197 rows of mechanical
candidate metadata (theme, UB label, SVR, LLM scores, cohort flags) while
leaving all seven scope-lock §5.3 evidence fields (`bucket`,
`primary_evidence`, `secondary_evidence`, `evidence_anchor`, `rationale`,
`d8_followup`) BLANK. It also populates Appendix A (200-row cohort
reconciliation) and Appendix B (Tier A rule-based eligibility matrix).
Per-candidate bucket assignments, Tier B overrides, test-retest
analysis, and synthesis remain deferred to D8.3.2b–D8.3.5 per scope lock §9.

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

## D8.3.1 / D8.3.2a discipline note

The D8.3.1 skeleton commit (`1703d1f`) left the document blank-by-intent
for candidate-level content. This D8.3.2a commit populates only
**mechanical** metadata: §7 master-table rows carry theme / UB label /
SVR / LLM scores / cohort flags read directly from
`raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json`
and from D8.1 notebook hard literals (`FRESH_7_RSI_ABSENT`,
`STAGE2B_OVERLAP_POSITIONS`, `QUARANTINE_POSITIONS`). The seven scope-lock
§5.3 evidence fields (`bucket`, `primary_evidence`, `secondary_evidence`,
`evidence_anchor`, `rationale`, `d8_followup`) remain BLANK until D8.3.2b
applies the Appendix B rule matrix and any Tier B overrides. Any
candidate bucket authored in D8.3.2b+ must cite a D8.1 / D8.2 evidence
anchor and must not rely on subjective preference. Sections that will
receive further content in later sub-phases are explicitly marked
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

*D8.3.2a populates mechanical metadata and cohort flags for all 197
ok-scored rows; all seven scope-lock §5.3 evidence columns remain
BLANK until D8.3.2b applies the Appendix B rule matrix.*

The master triage table covers all 197 ok-scored positions with one
row per candidate, seven evidence fields per row per §5.3 schema plus
reviewer-convenience mechanical columns (`theme`, `ub_label`, `svr`,
`svr_bucket`, `theme_alignment`, `plausibility`, and five cohort-flag
columns). Quarantined positions (42, 87, 116) do not appear in the
master table; they are accounted for in Appendix A.

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

### 7.4 No-bucket-assignments-in-D8.3.2a restatement

D8.3.2a populates only mechanical metadata and cohort flags for each
of the 197 ok-scored rows. The seven scope-lock §5.3 evidence
columns (`bucket`, `primary_evidence`, `secondary_evidence`,
`evidence_anchor`, `rationale`, `d8_followup`) remain BLANK until
D8.3.2b. **Any non-blank entry in those seven columns committed
before D8.3.2b is a scope violation.** The mechanical metadata
columns to the right of `d8_followup` are sourced directly from
`raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json`
(per-call `candidate_theme`, `pre_registered_label`, `critic_result.d7b_llm_scores`,
`is_stage2b_overlap`) and from D8.1 notebook hard literals
(`FRESH_7_RSI_ABSENT = {3, 43, 68, 128, 173, 188, 198}`;
`STAGE2B_OVERLAP_POSITIONS = {17, 73, 74, 97, 138}`;
`QUARANTINE_POSITIONS = {42, 87, 116}`); no derivation or
interpretation is applied.

### 7.5 Master-table body (D8.3.2a scaffold + D8.3.2b Tier A evidence + D8.3.2c non-rebuttable Tier B overrides + D8.3.3a rebuttable-presumption resolution)

Sorted ascending by `position`. 197 rows. The seven scope-lock §5.3
evidence columns (`bucket`, `primary_evidence`, `secondary_evidence`,
`evidence_anchor`, `rationale`, `d8_followup`) are populated in this
D8.3.2b sub-phase by deterministic Tier A rule application against the
Appendix B rule matrix. `secondary_evidence` remains blank for all 197
rows because every assignment in D8.3.2b is Tier A (scope lock §5.3:
Tier A requires only `primary_evidence`; `secondary_evidence` is
reserved for Tier B overrides, which are deferred to D8.3.2c).

D8.3.2b applies no Tier B overrides. The five §6.2.2 divergence_expected
METHOD-QUESTION rows (pos 1, 2, 3, 5, 6) inherit the §4.3 narrow
rebuttable presumption; any rebuttal belongs to D8.3.3 per scope lock
§9 (D8.3.2c is narrowed to non-rebuttable Tier B overrides only).

D8.3.2c applies exactly two non-rebuttable Tier B overrides, both
DEFER routes: pos 138 (REVIEW → DEFER) and pos 143 (REVIEW → DEFER),
each anchored by D8.2 §8.4 "RSI-absent vol_regime twins" explicit
D8.3 handoff plus D8.2 §6.6(B) LOW-SVR/HIGH-alignment cluster
membership. These two rows carry `d8_followup = D8.3.4` and have
`secondary_evidence` populated per §5.3 dual-anchor discipline. No
KEEP upgrades, no DROP-DUPLICATIVE assignments, and no rebuttable
rebuttals are applied in D8.3.2c.

All five §6.2.2 divergence positions were reviewed under scope lock
§3.4. Pos 6 was overridden to REVIEW; pos 1, 2, 3, and 5 retained
METHOD-QUESTION. Pos 3 was explicitly evaluated as the double-duty
case and retained at METHOD-QUESTION because fresh-7 membership is
a competing observation, not a rebuttal. Pos 6's rationale uses the
bucket/follow-up orthogonality framing: bucket = REVIEW (triage
disposition after Tier B rebuttal), `d8_followup` = D8.4 (advisory
methodology context for divergence-label audit, not bucket-blocking).
The full 5-position adjudication log is recorded in Appendix C.2.

Updated follow-up distribution after D8.3.3a: 4 METHOD-QUESTION rows
(pos 1, 2, 3, 5) → `D8.4`; pos 6 REVIEW → `D8.4` (advisory); 2 DEFER
rows (pos 138, 143) → `D8.3.4`; remaining 190 rows → `none`. Total:
5 `D8.4` + 2 `D8.3.4` + 190 `none` = 197.

SVR-bucket labels below use ASCII boundary tags for machine
readability: `LE_0.30` = SVR ≤ 0.30; `GT_0.30_LT_0.50` = 0.30 < SVR
< 0.50; `GE_0.50_LT_0.80` = 0.50 ≤ SVR < 0.80; `GE_0.80` = SVR ≥
0.80. Cohort-flag columns (`fresh_7`, `divergence_cohort`,
`stage2b_overlap`, `upper_tail`, `lower_tail`) are `Y` when true,
blank when false.

| `position` | `bucket` | `primary_evidence` | `secondary_evidence` | `evidence_anchor` | `rationale` | `d8_followup` | `theme` | `ub_label` | `svr` | `svr_bucket` | `theme_alignment` | `plausibility` | `fresh_7` | `divergence_cohort` | `stage2b_overlap` | `upper_tail` | `lower_tail` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | METHOD-QUESTION | aggregate_record.json per_call_records[0]: SVR=0.0, theme_alignment=0.85, plausibility=0.45, UB=divergence_expected, theme=momentum |  | §4.3 narrow rebuttable METHOD-QUESTION presumption (Tier A); Appendix B cell 2 | Pos 1: UB label divergence_expected places this row in the 5-position §6.2.2 divergence cohort under D8.2 FALSIFIED (interpretation_tag = likely_directional_model_misspecification). Scope lock §4.3 narrow rebuttable METHOD-QUESTION presumption applies; triage depends on D8.4 divergence-label definition audit and direction-of-prediction recalibration. SVR = 0.0, theme_alignment = 0.85, plausibility = 0.45, theme momentum; rebuttal requires Tier B override in D8.3.2c. | D8.4 | momentum | divergence_expected | 0.0 | LE_0.30 | 0.85 | 0.45 |  | Y |  |  | Y |
| 2 | METHOD-QUESTION | aggregate_record.json per_call_records[1]: SVR=0.15, theme_alignment=0.95, plausibility=0.75, UB=divergence_expected, theme=mean_reversion |  | §4.3 narrow rebuttable METHOD-QUESTION presumption (Tier A); Appendix B cell 2 | Pos 2: UB label divergence_expected places this row in the 5-position §6.2.2 divergence cohort under D8.2 FALSIFIED (interpretation_tag = likely_directional_model_misspecification). Scope lock §4.3 narrow rebuttable METHOD-QUESTION presumption applies; triage depends on D8.4 divergence-label definition audit and direction-of-prediction recalibration. SVR = 0.15, theme_alignment = 0.95, plausibility = 0.75, theme mean_reversion; rebuttal requires Tier B override in D8.3.2c. | D8.4 | mean_reversion | divergence_expected | 0.15 | LE_0.30 | 0.95 | 0.75 |  | Y |  |  | Y |
| 3 | METHOD-QUESTION | aggregate_record.json per_call_records[2]: SVR=0.15, theme_alignment=0.85, plausibility=0.75, UB=divergence_expected, theme=volatility_regime |  | §4.3 narrow rebuttable METHOD-QUESTION presumption (Tier A); Appendix B cell 2 | Pos 3: UB label divergence_expected places this row in the 5-position §6.2.2 divergence cohort under D8.2 FALSIFIED (interpretation_tag = likely_directional_model_misspecification). Scope lock §4.3 narrow rebuttable METHOD-QUESTION presumption applies; triage depends on D8.4 divergence-label definition audit and direction-of-prediction recalibration. SVR = 0.15, theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime; rebuttal requires Tier B override in D8.3.2c. | D8.4 | volatility_regime | divergence_expected | 0.15 | LE_0.30 | 0.85 | 0.75 | Y | Y |  |  | Y |
| 4 | REVIEW | aggregate_record.json per_call_records[3]: SVR=0.3, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 4: SVR = 0.3 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 5 | METHOD-QUESTION | aggregate_record.json per_call_records[4]: SVR=0.15, theme_alignment=0.85, plausibility=0.75, UB=divergence_expected, theme=calendar_effect |  | §4.3 narrow rebuttable METHOD-QUESTION presumption (Tier A); Appendix B cell 2 | Pos 5: UB label divergence_expected places this row in the 5-position §6.2.2 divergence cohort under D8.2 FALSIFIED (interpretation_tag = likely_directional_model_misspecification). Scope lock §4.3 narrow rebuttable METHOD-QUESTION presumption applies; triage depends on D8.4 divergence-label definition audit and direction-of-prediction recalibration. SVR = 0.15, theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect; rebuttal requires Tier B override in D8.3.2c. | D8.4 | calendar_effect | divergence_expected | 0.15 | LE_0.30 | 0.85 | 0.75 |  | Y |  |  | Y |
| 6 | REVIEW | aggregate_record.json per_call_records[5]: SVR=0.75, theme_alignment=0.95, plausibility=0.85, UB=divergence_expected, theme=momentum | D8.2 §6.2.2 aggregate gate 1/5 observation (pos 6 is sole SVR ≥ 0.5 contributor; only divergence-cohort row above threshold) | Tier B rebuttable rebuttal (D8.3.3a); REVIEW upgrade per §4.3 scope lock framing + dual-anchor (individual evidence strength + §6.2.2 gate structural-redundancy observation) | Pos 6: individual SVR 0.75 + theme_alignment 0.95 + plausibility 0.85 rebuts the §4.3 narrow rebuttable METHOD-QUESTION presumption, and pos 6 is the sole §6.2.2 gate SVR ≥ 0.5 contributor (1/5 observation), together satisfying the §5.3 Tier B dual-anchor threshold. REVIEW (not KEEP) because the divergence_expected label remains disconfirmed at claim-level and the §6.2.2 FALSIFIED verdict binds the cohort-context interpretation. `d8_followup = D8.4` carries methodology-advisory context (not bucket-blocking); bucket = REVIEW is triage disposition, follow-up = D8.4 is divergence-label-audit orthogonal context. | D8.4 | momentum | divergence_expected | 0.75 | GE_0.50_LT_0.80 | 0.95 | 0.85 |  | Y |  |  |  |
| 7 | REVIEW | aggregate_record.json per_call_records[6]: SVR=0.75, theme_alignment=0.9, plausibility=0.65, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 7: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.65, theme mean_reversion. | none | mean_reversion | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.65 |  |  |  |  |  |
| 8 | REVIEW | aggregate_record.json per_call_records[7]: SVR=0.7, theme_alignment=0.85, plausibility=0.65, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 8: SVR = 0.7 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.65, theme volatility_regime. | none | volatility_regime | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.65 |  |  |  |  |  |
| 9 | REVIEW | aggregate_record.json per_call_records[8]: SVR=0.3, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 9: SVR = 0.3 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 10 | REVIEW | aggregate_record.json per_call_records[9]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 10: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 11 | REVIEW | aggregate_record.json per_call_records[10]: SVR=0.75, theme_alignment=0.95, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 11: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.95, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.95 | 0.75 |  |  |  |  |  |
| 12 | REVIEW | aggregate_record.json per_call_records[11]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 12: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 13 | REVIEW | aggregate_record.json per_call_records[12]: SVR=0.7, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 13: SVR = 0.7 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 14 | REVIEW | aggregate_record.json per_call_records[13]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 14: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 15 | REVIEW | aggregate_record.json per_call_records[14]: SVR=0.75, theme_alignment=0.85, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 15: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.65 |  |  |  |  |  |
| 16 | REVIEW | aggregate_record.json per_call_records[15]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 16: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 17 | REVIEW | aggregate_record.json per_call_records[16]: SVR=0.85, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 17: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | neutral | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  | Y | Y |  |
| 18 | REVIEW | aggregate_record.json per_call_records[17]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 18: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 19 | REVIEW | aggregate_record.json per_call_records[18]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 19: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 20 | KEEP | aggregate_record.json per_call_records[19]: SVR=0.9, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=calendar_effect |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 20: SVR = 0.9 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 21 | REVIEW | aggregate_record.json per_call_records[20]: SVR=0.75, theme_alignment=0.9, plausibility=0.7, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 21: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.7, theme momentum. | none | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.7 |  |  |  |  |  |
| 22 | REVIEW | aggregate_record.json per_call_records[21]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 22: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 23 | REVIEW | aggregate_record.json per_call_records[22]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 23: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 24 | KEEP | aggregate_record.json per_call_records[23]: SVR=0.85, theme_alignment=0.7, plausibility=0.35, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 24: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.7, plausibility = 0.35, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.85 | GE_0.80 | 0.7 | 0.35 |  |  |  | Y |  |
| 25 | REVIEW | aggregate_record.json per_call_records[24]: SVR=0.7, theme_alignment=0.85, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 25: SVR = 0.7 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.65 |  |  |  |  |  |
| 26 | REVIEW | aggregate_record.json per_call_records[25]: SVR=0.3, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 26: SVR = 0.3 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.3 | LE_0.30 | 0.9 | 0.75 |  |  |  |  | Y |
| 27 | KEEP | aggregate_record.json per_call_records[26]: SVR=0.85, theme_alignment=0.85, plausibility=0.65, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 27: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.65, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 28 | REVIEW | aggregate_record.json per_call_records[27]: SVR=0.3, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 28: SVR = 0.3 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 29 | REVIEW | aggregate_record.json per_call_records[28]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 29: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 30 | REVIEW | aggregate_record.json per_call_records[29]: SVR=0.35, theme_alignment=0.75, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 6 | Pos 30: SVR = 0.35 sits in the mid-bracket (0.30 < SVR < 0.50) with UB label neutral. No Tier A KEEP/DROP rule fires at this SVR-bucket × UB-label cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.75, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.35 | GT_0.30_LT_0.50 | 0.75 | 0.65 |  |  |  |  |  |
| 31 | REVIEW | aggregate_record.json per_call_records[30]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 31: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 32 | REVIEW | aggregate_record.json per_call_records[31]: SVR=0.95, theme_alignment=0.7, plausibility=0.3, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 32: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.7, plausibility = 0.3, theme mean_reversion. | none | mean_reversion | neutral | 0.95 | GE_0.80 | 0.7 | 0.3 |  |  |  | Y |  |
| 33 | REVIEW | aggregate_record.json per_call_records[32]: SVR=0.15, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 33: SVR = 0.15 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.9, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.15 | LE_0.30 | 0.9 | 0.75 |  |  |  |  | Y |
| 34 | REVIEW | aggregate_record.json per_call_records[33]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 34: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 35 | REVIEW | aggregate_record.json per_call_records[34]: SVR=0.25, theme_alignment=0.75, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 35: SVR = 0.25 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.75, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.25 | LE_0.30 | 0.75 | 0.65 |  |  |  |  | Y |
| 36 | REVIEW | aggregate_record.json per_call_records[35]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 36: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 37 | REVIEW | aggregate_record.json per_call_records[36]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 37: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 38 | REVIEW | aggregate_record.json per_call_records[37]: SVR=0.25, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 38: SVR = 0.25 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.25 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 39 | REVIEW | aggregate_record.json per_call_records[38]: SVR=0.75, theme_alignment=0.7, plausibility=0.45, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 39: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.7, plausibility = 0.45, theme volume_divergence. | none | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.7 | 0.45 |  |  |  |  |  |
| 40 | REVIEW | aggregate_record.json per_call_records[39]: SVR=0.7, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 40: SVR = 0.7 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 41 | KEEP | aggregate_record.json per_call_records[40]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 41: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 43 | REVIEW | aggregate_record.json per_call_records[42]: SVR=0.25, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 43: SVR = 0.25 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.9, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.25 | LE_0.30 | 0.9 | 0.75 | Y |  |  |  | Y |
| 44 | KEEP | aggregate_record.json per_call_records[43]: SVR=0.95, theme_alignment=0.85, plausibility=0.35, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 44: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.35, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.85 | 0.35 |  |  |  | Y |  |
| 45 | REVIEW | aggregate_record.json per_call_records[44]: SVR=0.75, theme_alignment=0.75, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 45: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.75, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.75 | 0.65 |  |  |  |  |  |
| 46 | KEEP | aggregate_record.json per_call_records[45]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 46: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 47 | KEEP | aggregate_record.json per_call_records[46]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 47: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 48 | REVIEW | aggregate_record.json per_call_records[47]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 48: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 49 | KEEP | aggregate_record.json per_call_records[48]: SVR=0.8, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 49: SVR = 0.8 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.8 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 50 | REVIEW | aggregate_record.json per_call_records[49]: SVR=0.3, theme_alignment=0.85, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 50: SVR = 0.3 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.3 | LE_0.30 | 0.85 | 0.65 |  |  |  |  | Y |
| 51 | REVIEW | aggregate_record.json per_call_records[50]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 51: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 52 | REVIEW | aggregate_record.json per_call_records[51]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 52: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | neutral | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 53 | REVIEW | aggregate_record.json per_call_records[52]: SVR=0.7, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 53: SVR = 0.7 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 54 | REVIEW | aggregate_record.json per_call_records[53]: SVR=0.8, theme_alignment=0.65, plausibility=0.35, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 54: SVR = 0.8 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.65, plausibility = 0.35, theme volume_divergence. | none | volume_divergence | neutral | 0.8 | GE_0.80 | 0.65 | 0.35 |  |  |  | Y |  |
| 55 | REVIEW | aggregate_record.json per_call_records[54]: SVR=0.75, theme_alignment=0.85, plausibility=0.7, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 55: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.7, theme calendar_effect. | none | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.7 |  |  |  |  |  |
| 56 | REVIEW | aggregate_record.json per_call_records[55]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 56: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 57 | REVIEW | aggregate_record.json per_call_records[56]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 57: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 58 | REVIEW | aggregate_record.json per_call_records[57]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 58: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 59 | REVIEW | aggregate_record.json per_call_records[58]: SVR=0.85, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 59: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 60 | REVIEW | aggregate_record.json per_call_records[59]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 60: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 61 | REVIEW | aggregate_record.json per_call_records[60]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 61: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 62 | REVIEW | aggregate_record.json per_call_records[61]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 62: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | neutral | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 63 | REVIEW | aggregate_record.json per_call_records[62]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 63: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 64 | REVIEW | aggregate_record.json per_call_records[63]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 64: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 65 | REVIEW | aggregate_record.json per_call_records[64]: SVR=0.75, theme_alignment=0.85, plausibility=0.65, UB=agreement_expected, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW; Q1 adjudicated (Tier A); Appendix B cell 7 | Pos 65: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label agreement_expected; per Q1 Round-1 adjudication, moderate SVR is not KEEP-eligible evidence under scope lock §4.2 Lock 2 and Tier A default is REVIEW. KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.65 |  |  |  |  |  |
| 66 | REVIEW | aggregate_record.json per_call_records[65]: SVR=0.25, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 66: SVR = 0.25 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.25 | LE_0.30 | 0.9 | 0.75 |  |  |  |  | Y |
| 67 | KEEP | aggregate_record.json per_call_records[66]: SVR=0.85, theme_alignment=0.85, plausibility=0.65, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 67: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.65, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 68 | REVIEW | aggregate_record.json per_call_records[67]: SVR=0.9, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 68: SVR = 0.9 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.9 | GE_0.80 | 0.85 | 0.75 | Y |  |  | Y |  |
| 69 | KEEP | aggregate_record.json per_call_records[68]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 69: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 70 | REVIEW | aggregate_record.json per_call_records[69]: SVR=0.85, theme_alignment=0.75, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 70: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.75, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 71 | REVIEW | aggregate_record.json per_call_records[70]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 71: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 72 | REVIEW | aggregate_record.json per_call_records[71]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 72: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 73 | REVIEW | aggregate_record.json per_call_records[72]: SVR=0.95, theme_alignment=0.85, plausibility=0.7, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 73: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.7, theme volatility_regime. | none | volatility_regime | neutral | 0.95 | GE_0.80 | 0.85 | 0.7 |  |  | Y | Y |  |
| 74 | REVIEW | aggregate_record.json per_call_records[73]: SVR=0.7, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 74: SVR = 0.7 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  | Y |  |  |
| 75 | REVIEW | aggregate_record.json per_call_records[74]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW; Q1 adjudicated (Tier A); Appendix B cell 7 | Pos 75: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label agreement_expected; per Q1 Round-1 adjudication, moderate SVR is not KEEP-eligible evidence under scope lock §4.2 Lock 2 and Tier A default is REVIEW. KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 76 | REVIEW | aggregate_record.json per_call_records[75]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 76: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 77 | REVIEW | aggregate_record.json per_call_records[76]: SVR=0.9, theme_alignment=0.4, plausibility=0.3, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 77: SVR = 0.9 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.4, plausibility = 0.3, theme mean_reversion. | none | mean_reversion | neutral | 0.9 | GE_0.80 | 0.4 | 0.3 |  |  |  | Y |  |
| 78 | REVIEW | aggregate_record.json per_call_records[77]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 78: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 79 | REVIEW | aggregate_record.json per_call_records[78]: SVR=0.75, theme_alignment=0.7, plausibility=0.35, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 79: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.7, plausibility = 0.35, theme volume_divergence. | none | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.7 | 0.35 |  |  |  |  |  |
| 80 | KEEP | aggregate_record.json per_call_records[79]: SVR=0.85, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=calendar_effect |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 80: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 81 | REVIEW | aggregate_record.json per_call_records[80]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 81: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 82 | KEEP | aggregate_record.json per_call_records[81]: SVR=0.95, theme_alignment=0.4, plausibility=0.25, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 82: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.4, plausibility = 0.25, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.4 | 0.25 |  |  |  | Y |  |
| 83 | REVIEW | aggregate_record.json per_call_records[82]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 83: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 84 | KEEP | aggregate_record.json per_call_records[83]: SVR=0.95, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 84: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 85 | REVIEW | aggregate_record.json per_call_records[84]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 85: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 86 | REVIEW | aggregate_record.json per_call_records[85]: SVR=0.85, theme_alignment=0.9, plausibility=0.8, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 86: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.8, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.8 |  |  |  | Y |  |
| 88 | REVIEW | aggregate_record.json per_call_records[87]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 88: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 89 | KEEP | aggregate_record.json per_call_records[88]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 89: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 90 | REVIEW | aggregate_record.json per_call_records[89]: SVR=0.8, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 90: SVR = 0.8 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.8 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 91 | REVIEW | aggregate_record.json per_call_records[90]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 91: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 92 | KEEP | aggregate_record.json per_call_records[91]: SVR=0.85, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 92: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 93 | REVIEW | aggregate_record.json per_call_records[92]: SVR=0.7, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 93: SVR = 0.7 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 94 | KEEP | aggregate_record.json per_call_records[93]: SVR=0.95, theme_alignment=0.75, plausibility=0.35, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 94: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.75, plausibility = 0.35, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.75 | 0.35 |  |  |  | Y |  |
| 95 | REVIEW | aggregate_record.json per_call_records[94]: SVR=0.15, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 95: SVR = 0.15 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.15 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 96 | REVIEW | aggregate_record.json per_call_records[95]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 96: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 97 | KEEP | aggregate_record.json per_call_records[96]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 97: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  | Y | Y |  |
| 98 | KEEP | aggregate_record.json per_call_records[97]: SVR=0.85, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=volatility_regime |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 98: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 99 | REVIEW | aggregate_record.json per_call_records[98]: SVR=0.25, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 99: SVR = 0.25 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.25 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 100 | REVIEW | aggregate_record.json per_call_records[99]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 100: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 101 | REVIEW | aggregate_record.json per_call_records[100]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 101: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 102 | KEEP | aggregate_record.json per_call_records[101]: SVR=0.95, theme_alignment=0.4, plausibility=0.2, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 102: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.4, plausibility = 0.2, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.4 | 0.2 |  |  |  | Y |  |
| 103 | REVIEW | aggregate_record.json per_call_records[102]: SVR=0.95, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 103: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 104 | REVIEW | aggregate_record.json per_call_records[103]: SVR=0.85, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 104: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 105 | REVIEW | aggregate_record.json per_call_records[104]: SVR=0.85, theme_alignment=0.85, plausibility=0.7, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 105: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.7, theme calendar_effect. | none | calendar_effect | neutral | 0.85 | GE_0.80 | 0.85 | 0.7 |  |  |  | Y |  |
| 106 | REVIEW | aggregate_record.json per_call_records[105]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 106: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 107 | KEEP | aggregate_record.json per_call_records[106]: SVR=0.95, theme_alignment=0.7, plausibility=0.45, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 107: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.7, plausibility = 0.45, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.7 | 0.45 |  |  |  | Y |  |
| 108 | REVIEW | aggregate_record.json per_call_records[107]: SVR=0.75, theme_alignment=0.85, plausibility=0.7, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 108: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.7, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.7 |  |  |  |  |  |
| 109 | KEEP | aggregate_record.json per_call_records[108]: SVR=0.95, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 109: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 110 | REVIEW | aggregate_record.json per_call_records[109]: SVR=0.85, theme_alignment=0.85, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 110: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.85 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 111 | REVIEW | aggregate_record.json per_call_records[110]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 111: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 112 | KEEP | aggregate_record.json per_call_records[111]: SVR=0.9, theme_alignment=0.75, plausibility=0.35, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 112: SVR = 0.9 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.75, plausibility = 0.35, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.9 | GE_0.80 | 0.75 | 0.35 |  |  |  | Y |  |
| 113 | REVIEW | aggregate_record.json per_call_records[112]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 113: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 114 | REVIEW | aggregate_record.json per_call_records[113]: SVR=0.85, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 114: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 115 | REVIEW | aggregate_record.json per_call_records[114]: SVR=0.85, theme_alignment=0.75, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 115: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.75, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 117 | REVIEW | aggregate_record.json per_call_records[116]: SVR=0.85, theme_alignment=0.3, plausibility=0.2, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 117: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.3, plausibility = 0.2, theme mean_reversion. | none | mean_reversion | neutral | 0.85 | GE_0.80 | 0.3 | 0.2 |  |  |  | Y |  |
| 118 | REVIEW | aggregate_record.json per_call_records[117]: SVR=0.95, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 118: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 119 | REVIEW | aggregate_record.json per_call_records[118]: SVR=0.75, theme_alignment=0.65, plausibility=0.75, UB=agreement_expected, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW; Q1 adjudicated (Tier A); Appendix B cell 7 | Pos 119: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label agreement_expected; per Q1 Round-1 adjudication, moderate SVR is not KEEP-eligible evidence under scope lock §4.2 Lock 2 and Tier A default is REVIEW. KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.65, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.65 | 0.75 |  |  |  |  |  |
| 120 | REVIEW | aggregate_record.json per_call_records[119]: SVR=0.3, theme_alignment=0.85, plausibility=0.7, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 120: SVR = 0.3 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.7, theme calendar_effect. | none | calendar_effect | neutral | 0.3 | LE_0.30 | 0.85 | 0.7 |  |  |  |  | Y |
| 121 | KEEP | aggregate_record.json per_call_records[120]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 121: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 122 | KEEP | aggregate_record.json per_call_records[121]: SVR=0.95, theme_alignment=0.75, plausibility=0.25, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 122: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.75, plausibility = 0.25, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.75 | 0.25 |  |  |  | Y |  |
| 123 | REVIEW | aggregate_record.json per_call_records[122]: SVR=0.3, theme_alignment=0.75, plausibility=0.65, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 123: SVR = 0.3 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.75, plausibility = 0.65, theme volatility_regime. | none | volatility_regime | neutral | 0.3 | LE_0.30 | 0.75 | 0.65 |  |  |  |  | Y |
| 124 | REVIEW | aggregate_record.json per_call_records[123]: SVR=0.3, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 124: SVR = 0.3 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 125 | KEEP | aggregate_record.json per_call_records[124]: SVR=0.85, theme_alignment=0.75, plausibility=0.65, UB=agreement_expected, theme=calendar_effect |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 125: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.75, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | agreement_expected | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 126 | KEEP | aggregate_record.json per_call_records[125]: SVR=0.95, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 126: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 127 | KEEP | aggregate_record.json per_call_records[126]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 127: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 128 | REVIEW | aggregate_record.json per_call_records[127]: SVR=0.3, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 128: SVR = 0.3 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 | Y |  |  |  | Y |
| 129 | REVIEW | aggregate_record.json per_call_records[128]: SVR=0.35, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 6 | Pos 129: SVR = 0.35 sits in the mid-bracket (0.30 < SVR < 0.50) with UB label neutral. No Tier A KEEP/DROP rule fires at this SVR-bucket × UB-label cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.35 | GT_0.30_LT_0.50 | 0.9 | 0.75 |  |  |  |  |  |
| 130 | REVIEW | aggregate_record.json per_call_records[129]: SVR=0.35, theme_alignment=0.85, plausibility=0.7, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 6 | Pos 130: SVR = 0.35 sits in the mid-bracket (0.30 < SVR < 0.50) with UB label neutral. No Tier A KEEP/DROP rule fires at this SVR-bucket × UB-label cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.7, theme calendar_effect. | none | calendar_effect | neutral | 0.35 | GT_0.30_LT_0.50 | 0.85 | 0.7 |  |  |  |  |  |
| 131 | KEEP | aggregate_record.json per_call_records[130]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 131: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 132 | REVIEW | aggregate_record.json per_call_records[131]: SVR=0.75, theme_alignment=0.75, plausibility=0.3, UB=agreement_expected, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW; Q1 adjudicated (Tier A); Appendix B cell 7 | Pos 132: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label agreement_expected; per Q1 Round-1 adjudication, moderate SVR is not KEEP-eligible evidence under scope lock §4.2 Lock 2 and Tier A default is REVIEW. KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.75, plausibility = 0.3, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.75 | 0.3 |  |  |  |  |  |
| 133 | REVIEW | aggregate_record.json per_call_records[132]: SVR=0.15, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 133: SVR = 0.15 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.9, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.15 | LE_0.30 | 0.9 | 0.75 |  |  |  |  | Y |
| 134 | KEEP | aggregate_record.json per_call_records[133]: SVR=0.95, theme_alignment=0.7, plausibility=0.45, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 134: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.7, plausibility = 0.45, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.7 | 0.45 |  |  |  | Y |  |
| 135 | REVIEW | aggregate_record.json per_call_records[134]: SVR=0.85, theme_alignment=0.85, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 135: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.85 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 136 | KEEP | aggregate_record.json per_call_records[135]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 136: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 137 | KEEP | aggregate_record.json per_call_records[136]: SVR=0.95, theme_alignment=0.7, plausibility=0.3, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 137: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.7, plausibility = 0.3, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.7 | 0.3 |  |  |  | Y |  |
| 138 | DEFER | aggregate_record.json per_call_records[137]: SVR=0.25, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=volatility_regime | D8.2 §8.4 "RSI-absent vol_regime twins (pos 138, 143)" explicit D8.3 handoff; D8.2 §6.6(B) LOW-SVR/HIGH-aln cluster membership (line 723) | Tier B override — DEFER pending D8.3.4 RSI-absent vol_regime test-retest (scope lock §3.2 canonical DEFER case) | Pos 138: D8.2 §8.4 explicitly designates pos 138 and pos 143 as "RSI-absent vol_regime twins" requiring test-retest adjudication handed to D8.3, and scope lock §3.2 names this pair as the canonical DEFER case. Under §4.2 Lock 2 dual-anchor Tier B override discipline, the D8.2 §8.4 explicit pointer plus D8.2 §6.6(B) LOW-SVR/HIGH-alignment cluster membership together satisfy the DEFER route. Test-retest interpretation is handed to D8.3.4; any later bucket revision requires a fresh ratified re-triage cycle; theme volatility_regime, stage2b_overlap=Y. | D8.3.4 | volatility_regime | neutral | 0.25 | LE_0.30 | 0.9 | 0.75 |  |  | Y |  | Y |
| 139 | REVIEW | aggregate_record.json per_call_records[138]: SVR=0.95, theme_alignment=0.6, plausibility=0.35, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 139: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.6, plausibility = 0.35, theme volume_divergence. | none | volume_divergence | neutral | 0.95 | GE_0.80 | 0.6 | 0.35 |  |  |  | Y |  |
| 140 | REVIEW | aggregate_record.json per_call_records[139]: SVR=0.8, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 140: SVR = 0.8 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.8 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 141 | REVIEW | aggregate_record.json per_call_records[140]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 141: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 142 | KEEP | aggregate_record.json per_call_records[141]: SVR=0.85, theme_alignment=0.7, plausibility=0.45, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 142: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.7, plausibility = 0.45, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.7 | 0.45 |  |  |  | Y |  |
| 143 | DEFER | aggregate_record.json per_call_records[142]: SVR=0.15, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime | D8.2 §8.4 "RSI-absent vol_regime twins (pos 138, 143)" explicit D8.3 handoff; D8.2 §6.6(B) LOW-SVR/HIGH-aln cluster membership (line 723) | Tier B override — DEFER pending D8.3.4 RSI-absent vol_regime test-retest (scope lock §3.2 canonical DEFER case) | Pos 143: D8.2 §8.4 explicitly designates pos 138 and pos 143 as "RSI-absent vol_regime twins" requiring test-retest adjudication handed to D8.3, and scope lock §3.2 names this pair as the canonical DEFER case; pos 143 is not in the fresh-7 literal set (D8.1 FRESH_7_RSI_ABSENT = {3, 43, 68, 128, 173, 188, 198}), so the twin relationship is anchored by D8.2 §8.4 plus D8.2 §6.6(B) cluster membership rather than fresh-7 flagging. Under §4.2 Lock 2 dual-anchor Tier B override discipline, the D8.2 §8.4 explicit pointer plus §6.6(B) LOW-SVR/HIGH-alignment cluster membership together satisfy the DEFER route. Test-retest interpretation is handed to D8.3.4; any later bucket revision requires a fresh ratified re-triage cycle; theme volatility_regime. | D8.3.4 | volatility_regime | neutral | 0.15 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 144 | REVIEW | aggregate_record.json per_call_records[143]: SVR=0.8, theme_alignment=0.65, plausibility=0.35, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 144: SVR = 0.8 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.65, plausibility = 0.35, theme volume_divergence. | none | volume_divergence | neutral | 0.8 | GE_0.80 | 0.65 | 0.35 |  |  |  | Y |  |
| 145 | REVIEW | aggregate_record.json per_call_records[144]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 145: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 146 | REVIEW | aggregate_record.json per_call_records[145]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 146: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 147 | KEEP | aggregate_record.json per_call_records[146]: SVR=0.95, theme_alignment=0.75, plausibility=0.45, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 147: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.75, plausibility = 0.45, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.75 | 0.45 |  |  |  | Y |  |
| 148 | REVIEW | aggregate_record.json per_call_records[147]: SVR=0.3, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 148: SVR = 0.3 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 149 | KEEP | aggregate_record.json per_call_records[148]: SVR=0.95, theme_alignment=0.7, plausibility=0.35, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 149: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.7, plausibility = 0.35, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.7 | 0.35 |  |  |  | Y |  |
| 150 | REVIEW | aggregate_record.json per_call_records[149]: SVR=0.85, theme_alignment=0.75, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 150: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.75, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 151 | REVIEW | aggregate_record.json per_call_records[150]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 151: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 152 | KEEP | aggregate_record.json per_call_records[151]: SVR=0.95, theme_alignment=0.75, plausibility=0.35, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 152: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.75, plausibility = 0.35, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.75 | 0.35 |  |  |  | Y |  |
| 153 | KEEP | aggregate_record.json per_call_records[152]: SVR=0.85, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=volatility_regime |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 153: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 154 | KEEP | aggregate_record.json per_call_records[153]: SVR=0.9, theme_alignment=0.85, plausibility=0.65, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 154: SVR = 0.9 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.65, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 155 | REVIEW | aggregate_record.json per_call_records[154]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 155: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 156 | REVIEW | aggregate_record.json per_call_records[155]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW; Q1 adjudicated (Tier A); Appendix B cell 7 | Pos 156: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label agreement_expected; per Q1 Round-1 adjudication, moderate SVR is not KEEP-eligible evidence under scope lock §4.2 Lock 2 and Tier A default is REVIEW. KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 157 | KEEP | aggregate_record.json per_call_records[156]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 157: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 158 | REVIEW | aggregate_record.json per_call_records[157]: SVR=0.95, theme_alignment=0.75, plausibility=0.45, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 158: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.75, plausibility = 0.45, theme volatility_regime. | none | volatility_regime | neutral | 0.95 | GE_0.80 | 0.75 | 0.45 |  |  |  | Y |  |
| 159 | KEEP | aggregate_record.json per_call_records[158]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 159: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 160 | KEEP | aggregate_record.json per_call_records[159]: SVR=0.9, theme_alignment=0.85, plausibility=0.7, UB=agreement_expected, theme=calendar_effect |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 160: SVR = 0.9 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.7, theme calendar_effect. | none | calendar_effect | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.7 |  |  |  | Y |  |
| 161 | REVIEW | aggregate_record.json per_call_records[160]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=momentum |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 161: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 162 | KEEP | aggregate_record.json per_call_records[161]: SVR=0.95, theme_alignment=0.75, plausibility=0.4, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 162: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.75, plausibility = 0.4, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.75 | 0.4 |  |  |  | Y |  |
| 163 | REVIEW | aggregate_record.json per_call_records[162]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 163: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 164 | REVIEW | aggregate_record.json per_call_records[163]: SVR=0.75, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 164: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 165 | REVIEW | aggregate_record.json per_call_records[164]: SVR=0.85, theme_alignment=0.65, plausibility=0.35, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 165: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.65, plausibility = 0.35, theme calendar_effect. | none | calendar_effect | neutral | 0.85 | GE_0.80 | 0.65 | 0.35 |  |  |  | Y |  |
| 166 | KEEP | aggregate_record.json per_call_records[165]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 166: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 167 | REVIEW | aggregate_record.json per_call_records[166]: SVR=0.85, theme_alignment=0.75, plausibility=0.65, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 167: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.75, plausibility = 0.65, theme mean_reversion. | none | mean_reversion | neutral | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 168 | REVIEW | aggregate_record.json per_call_records[167]: SVR=0.75, theme_alignment=0.8, plausibility=0.65, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 168: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.8, plausibility = 0.65, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.8 | 0.65 |  |  |  |  |  |
| 169 | KEEP | aggregate_record.json per_call_records[168]: SVR=0.9, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 169: SVR = 0.9 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 170 | REVIEW | aggregate_record.json per_call_records[169]: SVR=0.3, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 170: SVR = 0.3 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 171 | KEEP | aggregate_record.json per_call_records[170]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 171: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 172 | REVIEW | aggregate_record.json per_call_records[171]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 172: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme mean_reversion. | none | mean_reversion | neutral | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 173 | REVIEW | aggregate_record.json per_call_records[172]: SVR=0.75, theme_alignment=0.8, plausibility=0.65, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 173: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.8, plausibility = 0.65, theme volatility_regime. | none | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.8 | 0.65 | Y |  |  |  |  |
| 174 | REVIEW | aggregate_record.json per_call_records[173]: SVR=0.85, theme_alignment=0.65, plausibility=0.35, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 174: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.65, plausibility = 0.35, theme volume_divergence. | none | volume_divergence | neutral | 0.85 | GE_0.80 | 0.65 | 0.35 |  |  |  | Y |  |
| 175 | REVIEW | aggregate_record.json per_call_records[174]: SVR=0.95, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 175: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 176 | KEEP | aggregate_record.json per_call_records[175]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 176: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 177 | REVIEW | aggregate_record.json per_call_records[176]: SVR=0.95, theme_alignment=0.75, plausibility=0.45, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 177: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.75, plausibility = 0.45, theme mean_reversion. | none | mean_reversion | neutral | 0.95 | GE_0.80 | 0.75 | 0.45 |  |  |  | Y |  |
| 178 | REVIEW | aggregate_record.json per_call_records[177]: SVR=0.25, theme_alignment=0.85, plausibility=0.7, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 3 | Pos 178: SVR = 0.25 sits in the lower-tail bracket (SVR ≤ 0.30) but the pre-registered UB label is neutral, so neither the agreement gate nor the §6.3(b) lower-tail gate triggers. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP/DROP-DUPLICATIVE reachable only via Tier B override. theme_alignment = 0.85, plausibility = 0.7, theme volatility_regime. | none | volatility_regime | neutral | 0.25 | LE_0.30 | 0.85 | 0.7 |  |  |  |  | Y |
| 179 | REVIEW | aggregate_record.json per_call_records[178]: SVR=0.85, theme_alignment=0.75, plausibility=0.35, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 179: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.75, plausibility = 0.35, theme volume_divergence. | none | volume_divergence | neutral | 0.85 | GE_0.80 | 0.75 | 0.35 |  |  |  | Y |  |
| 180 | REVIEW | aggregate_record.json per_call_records[179]: SVR=0.75, theme_alignment=0.85, plausibility=0.65, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 180: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.85, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.65 |  |  |  |  |  |
| 181 | KEEP | aggregate_record.json per_call_records[180]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 181: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 182 | REVIEW | aggregate_record.json per_call_records[181]: SVR=0.95, theme_alignment=0.7, plausibility=0.35, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 182: SVR = 0.95 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.7, plausibility = 0.35, theme mean_reversion. | none | mean_reversion | neutral | 0.95 | GE_0.80 | 0.7 | 0.35 |  |  |  | Y |  |
| 183 | KEEP | aggregate_record.json per_call_records[182]: SVR=0.85, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=volatility_regime |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 183: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 184 | REVIEW | aggregate_record.json per_call_records[183]: SVR=0.85, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 184: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 185 | KEEP | aggregate_record.json per_call_records[184]: SVR=0.85, theme_alignment=0.75, plausibility=0.65, UB=agreement_expected, theme=calendar_effect |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 185: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.75, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | agreement_expected | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 186 | KEEP | aggregate_record.json per_call_records[185]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 186: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 187 | REVIEW | aggregate_record.json per_call_records[186]: SVR=0.85, theme_alignment=0.85, plausibility=0.65, UB=neutral, theme=mean_reversion |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 187: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.65, theme mean_reversion. | none | mean_reversion | neutral | 0.85 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 188 | KEEP | aggregate_record.json per_call_records[187]: SVR=0.8, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=volatility_regime |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 188: SVR = 0.8 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | agreement_expected | 0.8 | GE_0.80 | 0.85 | 0.75 | Y |  |  | Y |  |
| 189 | KEEP | aggregate_record.json per_call_records[188]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 189: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 190 | REVIEW | aggregate_record.json per_call_records[189]: SVR=0.7, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 9 | Pos 190: SVR = 0.7 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label neutral. No Tier A KEEP/DROP rule fires at this cell; scope lock §4.2 Lock 2 default-to-REVIEW applies. theme_alignment = 0.9, plausibility = 0.75, theme calendar_effect. | none | calendar_effect | neutral | 0.7 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 191 | KEEP | aggregate_record.json per_call_records[190]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 191: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 192 | KEEP | aggregate_record.json per_call_records[191]: SVR=0.95, theme_alignment=0.85, plausibility=0.65, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 192: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.65, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 193 | REVIEW | aggregate_record.json per_call_records[192]: SVR=0.75, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW; Q1 adjudicated (Tier A); Appendix B cell 7 | Pos 193: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label agreement_expected; per Q1 Round-1 adjudication, moderate SVR is not KEEP-eligible evidence under scope lock §4.2 Lock 2 and Tier A default is REVIEW. KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 194 | REVIEW | aggregate_record.json per_call_records[193]: SVR=0.85, theme_alignment=0.9, plausibility=0.75, UB=neutral, theme=volume_divergence |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 194: SVR = 0.85 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.9, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 195 | KEEP | aggregate_record.json per_call_records[194]: SVR=0.9, theme_alignment=0.85, plausibility=0.65, UB=agreement_expected, theme=calendar_effect |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 195: SVR = 0.9 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 196 | KEEP | aggregate_record.json per_call_records[195]: SVR=0.95, theme_alignment=0.9, plausibility=0.75, UB=agreement_expected, theme=momentum |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 196: SVR = 0.95 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.9, plausibility = 0.75, theme momentum. | none | momentum | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 197 | KEEP | aggregate_record.json per_call_records[196]: SVR=0.85, theme_alignment=0.7, plausibility=0.45, UB=agreement_expected, theme=mean_reversion |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 197: SVR = 0.85 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.7, plausibility = 0.45, theme mean_reversion. | none | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.7 | 0.45 |  |  |  | Y |  |
| 198 | REVIEW | aggregate_record.json per_call_records[197]: SVR=0.9, theme_alignment=0.85, plausibility=0.75, UB=neutral, theme=volatility_regime |  | §4.2 Lock 2 default-to-REVIEW (Tier A); Appendix B cell 12 | Pos 198: SVR = 0.9 is in the upper-tail bracket (SVR ≥ 0.80) but the pre-registered UB label is neutral, so the §6.2.1 agreement gate does not trigger and §6.3(a) upper-tail gate PASS is a distributional finding that does not per se justify KEEP for any individual row. Scope lock §4.2 Lock 2 default-to-REVIEW applies; KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.85, plausibility = 0.75, theme volatility_regime. | none | volatility_regime | neutral | 0.9 | GE_0.80 | 0.85 | 0.75 | Y |  |  | Y |  |
| 199 | KEEP | aggregate_record.json per_call_records[198]: SVR=0.9, theme_alignment=0.85, plausibility=0.75, UB=agreement_expected, theme=volume_divergence |  | SVR ≥ 0.80 ∩ agreement_expected → KEEP (Tier A); Appendix B cell 10 | Pos 199: SVR = 0.9 falls in the upper-tail bracket (SVR ≥ 0.80) and the pre-registered UB label is agreement_expected. D8.1 §6.2.1 agreement gate PASS intersected with §6.3(a) upper-tail gate PASS makes this row KEEP-eligible under the Tier A rule matrix; theme_alignment = 0.85, plausibility = 0.75, theme volume_divergence. | none | volume_divergence | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 200 | REVIEW | aggregate_record.json per_call_records[199]: SVR=0.75, theme_alignment=0.75, plausibility=0.65, UB=agreement_expected, theme=calendar_effect |  | §4.2 Lock 2 default-to-REVIEW; Q1 adjudicated (Tier A); Appendix B cell 7 | Pos 200: SVR = 0.75 sits in the moderate bracket (0.50 ≤ SVR < 0.80) with UB label agreement_expected; per Q1 Round-1 adjudication, moderate SVR is not KEEP-eligible evidence under scope lock §4.2 Lock 2 and Tier A default is REVIEW. KEEP upgrade reachable only via Tier B dual-anchor override in D8.3.2c. theme_alignment = 0.75, plausibility = 0.65, theme calendar_effect. | none | calendar_effect | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.75 | 0.65 |  |  |  |  |  |

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

*Populated in D8.3.2a.*

Full 200-row reconciliation: 197 ok-scored rows (cross-referenced to
master table §7) plus 3 quarantined rows (pos 42, 87, 116) with
`exclusion_reason`, `excluded_from`, and evidence anchor to the
D8.1 / D8.2 source. Row total MUST equal 200.

Cohort accounting check (from scope lock §6.1): 200 fired calls − 1
`skipped_source_invalid` (pos 116) = **199-call UB cohort**; 199-call
UB cohort − 2 `d7b_error` (pos 42, 87) = **197 ok-scored universe**.
Pos 42 and 87 are members of the 199 UB cohort for pre-registered
aggregate-denominator accounting but are excluded from the 197 scored
universe because no SVR score exists. Pos 116 is excluded from both.

| `position` | `status` | `excluded_from` | `exclusion_reason` | `evidence_anchor` |
|---|---|---|---|---|
| 1 | ok_scored | n/a | included — see §7 master table row `position = 1` (theme `momentum`, UB `divergence_expected`, SVR `0.0`). | §7 master table |
| 2 | ok_scored | n/a | included — see §7 master table row `position = 2` (theme `mean_reversion`, UB `divergence_expected`, SVR `0.15`). | §7 master table |
| 3 | ok_scored | n/a | included — see §7 master table row `position = 3` (theme `volatility_regime`, UB `divergence_expected`, SVR `0.15`). | §7 master table |
| 4 | ok_scored | n/a | included — see §7 master table row `position = 4` (theme `volume_divergence`, UB `neutral`, SVR `0.3`). | §7 master table |
| 5 | ok_scored | n/a | included — see §7 master table row `position = 5` (theme `calendar_effect`, UB `divergence_expected`, SVR `0.15`). | §7 master table |
| 6 | ok_scored | n/a | included — see §7 master table row `position = 6` (theme `momentum`, UB `divergence_expected`, SVR `0.75`). | §7 master table |
| 7 | ok_scored | n/a | included — see §7 master table row `position = 7` (theme `mean_reversion`, UB `neutral`, SVR `0.75`). | §7 master table |
| 8 | ok_scored | n/a | included — see §7 master table row `position = 8` (theme `volatility_regime`, UB `neutral`, SVR `0.7`). | §7 master table |
| 9 | ok_scored | n/a | included — see §7 master table row `position = 9` (theme `volume_divergence`, UB `neutral`, SVR `0.3`). | §7 master table |
| 10 | ok_scored | n/a | included — see §7 master table row `position = 10` (theme `calendar_effect`, UB `neutral`, SVR `0.75`). | §7 master table |
| 11 | ok_scored | n/a | included — see §7 master table row `position = 11` (theme `momentum`, UB `neutral`, SVR `0.75`). | §7 master table |
| 12 | ok_scored | n/a | included — see §7 master table row `position = 12` (theme `mean_reversion`, UB `neutral`, SVR `0.75`). | §7 master table |
| 13 | ok_scored | n/a | included — see §7 master table row `position = 13` (theme `volatility_regime`, UB `neutral`, SVR `0.7`). | §7 master table |
| 14 | ok_scored | n/a | included — see §7 master table row `position = 14` (theme `volume_divergence`, UB `neutral`, SVR `0.85`). | §7 master table |
| 15 | ok_scored | n/a | included — see §7 master table row `position = 15` (theme `calendar_effect`, UB `neutral`, SVR `0.75`). | §7 master table |
| 16 | ok_scored | n/a | included — see §7 master table row `position = 16` (theme `momentum`, UB `neutral`, SVR `0.75`). | §7 master table |
| 17 | ok_scored | n/a | included — see §7 master table row `position = 17` (theme `mean_reversion`, UB `neutral`, SVR `0.85`). | §7 master table |
| 18 | ok_scored | n/a | included — see §7 master table row `position = 18` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 19 | ok_scored | n/a | included — see §7 master table row `position = 19` (theme `volume_divergence`, UB `neutral`, SVR `0.75`). | §7 master table |
| 20 | ok_scored | n/a | included — see §7 master table row `position = 20` (theme `calendar_effect`, UB `agreement_expected`, SVR `0.9`). | §7 master table |
| 21 | ok_scored | n/a | included — see §7 master table row `position = 21` (theme `momentum`, UB `neutral`, SVR `0.75`). | §7 master table |
| 22 | ok_scored | n/a | included — see §7 master table row `position = 22` (theme `mean_reversion`, UB `neutral`, SVR `0.75`). | §7 master table |
| 23 | ok_scored | n/a | included — see §7 master table row `position = 23` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 24 | ok_scored | n/a | included — see §7 master table row `position = 24` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 25 | ok_scored | n/a | included — see §7 master table row `position = 25` (theme `calendar_effect`, UB `neutral`, SVR `0.7`). | §7 master table |
| 26 | ok_scored | n/a | included — see §7 master table row `position = 26` (theme `momentum`, UB `neutral`, SVR `0.3`). | §7 master table |
| 27 | ok_scored | n/a | included — see §7 master table row `position = 27` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 28 | ok_scored | n/a | included — see §7 master table row `position = 28` (theme `volatility_regime`, UB `neutral`, SVR `0.3`). | §7 master table |
| 29 | ok_scored | n/a | included — see §7 master table row `position = 29` (theme `volume_divergence`, UB `neutral`, SVR `0.75`). | §7 master table |
| 30 | ok_scored | n/a | included — see §7 master table row `position = 30` (theme `calendar_effect`, UB `neutral`, SVR `0.35`). | §7 master table |
| 31 | ok_scored | n/a | included — see §7 master table row `position = 31` (theme `momentum`, UB `neutral`, SVR `0.75`). | §7 master table |
| 32 | ok_scored | n/a | included — see §7 master table row `position = 32` (theme `mean_reversion`, UB `neutral`, SVR `0.95`). | §7 master table |
| 33 | ok_scored | n/a | included — see §7 master table row `position = 33` (theme `volatility_regime`, UB `neutral`, SVR `0.15`). | §7 master table |
| 34 | ok_scored | n/a | included — see §7 master table row `position = 34` (theme `volume_divergence`, UB `neutral`, SVR `0.75`). | §7 master table |
| 35 | ok_scored | n/a | included — see §7 master table row `position = 35` (theme `calendar_effect`, UB `neutral`, SVR `0.25`). | §7 master table |
| 36 | ok_scored | n/a | included — see §7 master table row `position = 36` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 37 | ok_scored | n/a | included — see §7 master table row `position = 37` (theme `mean_reversion`, UB `neutral`, SVR `0.85`). | §7 master table |
| 38 | ok_scored | n/a | included — see §7 master table row `position = 38` (theme `volatility_regime`, UB `neutral`, SVR `0.25`). | §7 master table |
| 39 | ok_scored | n/a | included — see §7 master table row `position = 39` (theme `volume_divergence`, UB `neutral`, SVR `0.75`). | §7 master table |
| 40 | ok_scored | n/a | included — see §7 master table row `position = 40` (theme `calendar_effect`, UB `neutral`, SVR `0.7`). | §7 master table |
| 41 | ok_scored | n/a | included — see §7 master table row `position = 41` (theme `momentum`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 42 | d7b_error | 197-scored universe (still member of 199-call UB cohort per scope lock §3.3) | D7b call failed; `critic_result.d7b_llm_scores is None`; theme = `mean_reversion`. Inside 199 UB cohort for aggregate-denominator accounting; outside 197 scored universe because no SVR score exists. | aggregate_record.json per_call_records[41] |
| 43 | ok_scored | n/a | included — see §7 master table row `position = 43` (theme `volatility_regime`, UB `neutral`, SVR `0.25`). | §7 master table |
| 44 | ok_scored | n/a | included — see §7 master table row `position = 44` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 45 | ok_scored | n/a | included — see §7 master table row `position = 45` (theme `calendar_effect`, UB `neutral`, SVR `0.75`). | §7 master table |
| 46 | ok_scored | n/a | included — see §7 master table row `position = 46` (theme `momentum`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 47 | ok_scored | n/a | included — see §7 master table row `position = 47` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 48 | ok_scored | n/a | included — see §7 master table row `position = 48` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 49 | ok_scored | n/a | included — see §7 master table row `position = 49` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.8`). | §7 master table |
| 50 | ok_scored | n/a | included — see §7 master table row `position = 50` (theme `calendar_effect`, UB `neutral`, SVR `0.3`). | §7 master table |
| 51 | ok_scored | n/a | included — see §7 master table row `position = 51` (theme `momentum`, UB `neutral`, SVR `0.75`). | §7 master table |
| 52 | ok_scored | n/a | included — see §7 master table row `position = 52` (theme `mean_reversion`, UB `neutral`, SVR `0.95`). | §7 master table |
| 53 | ok_scored | n/a | included — see §7 master table row `position = 53` (theme `volatility_regime`, UB `neutral`, SVR `0.7`). | §7 master table |
| 54 | ok_scored | n/a | included — see §7 master table row `position = 54` (theme `volume_divergence`, UB `neutral`, SVR `0.8`). | §7 master table |
| 55 | ok_scored | n/a | included — see §7 master table row `position = 55` (theme `calendar_effect`, UB `neutral`, SVR `0.75`). | §7 master table |
| 56 | ok_scored | n/a | included — see §7 master table row `position = 56` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 57 | ok_scored | n/a | included — see §7 master table row `position = 57` (theme `mean_reversion`, UB `neutral`, SVR `0.75`). | §7 master table |
| 58 | ok_scored | n/a | included — see §7 master table row `position = 58` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 59 | ok_scored | n/a | included — see §7 master table row `position = 59` (theme `volume_divergence`, UB `neutral`, SVR `0.85`). | §7 master table |
| 60 | ok_scored | n/a | included — see §7 master table row `position = 60` (theme `calendar_effect`, UB `neutral`, SVR `0.75`). | §7 master table |
| 61 | ok_scored | n/a | included — see §7 master table row `position = 61` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 62 | ok_scored | n/a | included — see §7 master table row `position = 62` (theme `mean_reversion`, UB `neutral`, SVR `0.95`). | §7 master table |
| 63 | ok_scored | n/a | included — see §7 master table row `position = 63` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 64 | ok_scored | n/a | included — see §7 master table row `position = 64` (theme `volume_divergence`, UB `neutral`, SVR `0.75`). | §7 master table |
| 65 | ok_scored | n/a | included — see §7 master table row `position = 65` (theme `calendar_effect`, UB `agreement_expected`, SVR `0.75`). | §7 master table |
| 66 | ok_scored | n/a | included — see §7 master table row `position = 66` (theme `momentum`, UB `neutral`, SVR `0.25`). | §7 master table |
| 67 | ok_scored | n/a | included — see §7 master table row `position = 67` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 68 | ok_scored | n/a | included — see §7 master table row `position = 68` (theme `volatility_regime`, UB `neutral`, SVR `0.9`). | §7 master table |
| 69 | ok_scored | n/a | included — see §7 master table row `position = 69` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 70 | ok_scored | n/a | included — see §7 master table row `position = 70` (theme `calendar_effect`, UB `neutral`, SVR `0.85`). | §7 master table |
| 71 | ok_scored | n/a | included — see §7 master table row `position = 71` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 72 | ok_scored | n/a | included — see §7 master table row `position = 72` (theme `mean_reversion`, UB `neutral`, SVR `0.75`). | §7 master table |
| 73 | ok_scored | n/a | included — see §7 master table row `position = 73` (theme `volatility_regime`, UB `neutral`, SVR `0.95`). | §7 master table |
| 74 | ok_scored | n/a | included — see §7 master table row `position = 74` (theme `volume_divergence`, UB `neutral`, SVR `0.7`). | §7 master table |
| 75 | ok_scored | n/a | included — see §7 master table row `position = 75` (theme `calendar_effect`, UB `agreement_expected`, SVR `0.75`). | §7 master table |
| 76 | ok_scored | n/a | included — see §7 master table row `position = 76` (theme `momentum`, UB `neutral`, SVR `0.95`). | §7 master table |
| 77 | ok_scored | n/a | included — see §7 master table row `position = 77` (theme `mean_reversion`, UB `neutral`, SVR `0.9`). | §7 master table |
| 78 | ok_scored | n/a | included — see §7 master table row `position = 78` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 79 | ok_scored | n/a | included — see §7 master table row `position = 79` (theme `volume_divergence`, UB `neutral`, SVR `0.75`). | §7 master table |
| 80 | ok_scored | n/a | included — see §7 master table row `position = 80` (theme `calendar_effect`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 81 | ok_scored | n/a | included — see §7 master table row `position = 81` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 82 | ok_scored | n/a | included — see §7 master table row `position = 82` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 83 | ok_scored | n/a | included — see §7 master table row `position = 83` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 84 | ok_scored | n/a | included — see §7 master table row `position = 84` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 85 | ok_scored | n/a | included — see §7 master table row `position = 85` (theme `calendar_effect`, UB `neutral`, SVR `0.75`). | §7 master table |
| 86 | ok_scored | n/a | included — see §7 master table row `position = 86` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 87 | d7b_error | 197-scored universe (still member of 199-call UB cohort per scope lock §3.3) | D7b call failed; `critic_result.d7b_llm_scores is None`; theme = `mean_reversion`. Inside 199 UB cohort for aggregate-denominator accounting; outside 197 scored universe because no SVR score exists. | aggregate_record.json per_call_records[86] |
| 88 | ok_scored | n/a | included — see §7 master table row `position = 88` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 89 | ok_scored | n/a | included — see §7 master table row `position = 89` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 90 | ok_scored | n/a | included — see §7 master table row `position = 90` (theme `calendar_effect`, UB `neutral`, SVR `0.8`). | §7 master table |
| 91 | ok_scored | n/a | included — see §7 master table row `position = 91` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 92 | ok_scored | n/a | included — see §7 master table row `position = 92` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 93 | ok_scored | n/a | included — see §7 master table row `position = 93` (theme `volatility_regime`, UB `neutral`, SVR `0.7`). | §7 master table |
| 94 | ok_scored | n/a | included — see §7 master table row `position = 94` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 95 | ok_scored | n/a | included — see §7 master table row `position = 95` (theme `calendar_effect`, UB `neutral`, SVR `0.15`). | §7 master table |
| 96 | ok_scored | n/a | included — see §7 master table row `position = 96` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 97 | ok_scored | n/a | included — see §7 master table row `position = 97` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 98 | ok_scored | n/a | included — see §7 master table row `position = 98` (theme `volatility_regime`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 99 | ok_scored | n/a | included — see §7 master table row `position = 99` (theme `volume_divergence`, UB `neutral`, SVR `0.25`). | §7 master table |
| 100 | ok_scored | n/a | included — see §7 master table row `position = 100` (theme `calendar_effect`, UB `neutral`, SVR `0.85`). | §7 master table |
| 101 | ok_scored | n/a | included — see §7 master table row `position = 101` (theme `momentum`, UB `neutral`, SVR `0.95`). | §7 master table |
| 102 | ok_scored | n/a | included — see §7 master table row `position = 102` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 103 | ok_scored | n/a | included — see §7 master table row `position = 103` (theme `volatility_regime`, UB `neutral`, SVR `0.95`). | §7 master table |
| 104 | ok_scored | n/a | included — see §7 master table row `position = 104` (theme `volume_divergence`, UB `neutral`, SVR `0.85`). | §7 master table |
| 105 | ok_scored | n/a | included — see §7 master table row `position = 105` (theme `calendar_effect`, UB `neutral`, SVR `0.85`). | §7 master table |
| 106 | ok_scored | n/a | included — see §7 master table row `position = 106` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 107 | ok_scored | n/a | included — see §7 master table row `position = 107` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 108 | ok_scored | n/a | included — see §7 master table row `position = 108` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 109 | ok_scored | n/a | included — see §7 master table row `position = 109` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 110 | ok_scored | n/a | included — see §7 master table row `position = 110` (theme `calendar_effect`, UB `neutral`, SVR `0.85`). | §7 master table |
| 111 | ok_scored | n/a | included — see §7 master table row `position = 111` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 112 | ok_scored | n/a | included — see §7 master table row `position = 112` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.9`). | §7 master table |
| 113 | ok_scored | n/a | included — see §7 master table row `position = 113` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 114 | ok_scored | n/a | included — see §7 master table row `position = 114` (theme `volume_divergence`, UB `neutral`, SVR `0.85`). | §7 master table |
| 115 | ok_scored | n/a | included — see §7 master table row `position = 115` (theme `calendar_effect`, UB `neutral`, SVR `0.85`). | §7 master table |
| 116 | skipped_source_invalid | both 199-call UB cohort and 197-scored universe | Source candidate was not pending_backtest and could not be replayed by BatchContext reconstruction; `critic_result is None`; `d7b_call_attempted=False`; `source_valid_status=invalid_schema`. | aggregate_record.json per_call_records[115] |
| 117 | ok_scored | n/a | included — see §7 master table row `position = 117` (theme `mean_reversion`, UB `neutral`, SVR `0.85`). | §7 master table |
| 118 | ok_scored | n/a | included — see §7 master table row `position = 118` (theme `volatility_regime`, UB `neutral`, SVR `0.95`). | §7 master table |
| 119 | ok_scored | n/a | included — see §7 master table row `position = 119` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.75`). | §7 master table |
| 120 | ok_scored | n/a | included — see §7 master table row `position = 120` (theme `calendar_effect`, UB `neutral`, SVR `0.3`). | §7 master table |
| 121 | ok_scored | n/a | included — see §7 master table row `position = 121` (theme `momentum`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 122 | ok_scored | n/a | included — see §7 master table row `position = 122` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 123 | ok_scored | n/a | included — see §7 master table row `position = 123` (theme `volatility_regime`, UB `neutral`, SVR `0.3`). | §7 master table |
| 124 | ok_scored | n/a | included — see §7 master table row `position = 124` (theme `volume_divergence`, UB `neutral`, SVR `0.3`). | §7 master table |
| 125 | ok_scored | n/a | included — see §7 master table row `position = 125` (theme `calendar_effect`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 126 | ok_scored | n/a | included — see §7 master table row `position = 126` (theme `momentum`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 127 | ok_scored | n/a | included — see §7 master table row `position = 127` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 128 | ok_scored | n/a | included — see §7 master table row `position = 128` (theme `volatility_regime`, UB `neutral`, SVR `0.3`). | §7 master table |
| 129 | ok_scored | n/a | included — see §7 master table row `position = 129` (theme `volume_divergence`, UB `neutral`, SVR `0.35`). | §7 master table |
| 130 | ok_scored | n/a | included — see §7 master table row `position = 130` (theme `calendar_effect`, UB `neutral`, SVR `0.35`). | §7 master table |
| 131 | ok_scored | n/a | included — see §7 master table row `position = 131` (theme `momentum`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 132 | ok_scored | n/a | included — see §7 master table row `position = 132` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.75`). | §7 master table |
| 133 | ok_scored | n/a | included — see §7 master table row `position = 133` (theme `volatility_regime`, UB `neutral`, SVR `0.15`). | §7 master table |
| 134 | ok_scored | n/a | included — see §7 master table row `position = 134` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 135 | ok_scored | n/a | included — see §7 master table row `position = 135` (theme `calendar_effect`, UB `neutral`, SVR `0.85`). | §7 master table |
| 136 | ok_scored | n/a | included — see §7 master table row `position = 136` (theme `momentum`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 137 | ok_scored | n/a | included — see §7 master table row `position = 137` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 138 | ok_scored | n/a | included — see §7 master table row `position = 138` (theme `volatility_regime`, UB `neutral`, SVR `0.25`). | §7 master table |
| 139 | ok_scored | n/a | included — see §7 master table row `position = 139` (theme `volume_divergence`, UB `neutral`, SVR `0.95`). | §7 master table |
| 140 | ok_scored | n/a | included — see §7 master table row `position = 140` (theme `calendar_effect`, UB `neutral`, SVR `0.8`). | §7 master table |
| 141 | ok_scored | n/a | included — see §7 master table row `position = 141` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 142 | ok_scored | n/a | included — see §7 master table row `position = 142` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 143 | ok_scored | n/a | included — see §7 master table row `position = 143` (theme `volatility_regime`, UB `neutral`, SVR `0.15`). | §7 master table |
| 144 | ok_scored | n/a | included — see §7 master table row `position = 144` (theme `volume_divergence`, UB `neutral`, SVR `0.8`). | §7 master table |
| 145 | ok_scored | n/a | included — see §7 master table row `position = 145` (theme `calendar_effect`, UB `neutral`, SVR `0.75`). | §7 master table |
| 146 | ok_scored | n/a | included — see §7 master table row `position = 146` (theme `momentum`, UB `neutral`, SVR `0.85`). | §7 master table |
| 147 | ok_scored | n/a | included — see §7 master table row `position = 147` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 148 | ok_scored | n/a | included — see §7 master table row `position = 148` (theme `volatility_regime`, UB `neutral`, SVR `0.3`). | §7 master table |
| 149 | ok_scored | n/a | included — see §7 master table row `position = 149` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 150 | ok_scored | n/a | included — see §7 master table row `position = 150` (theme `calendar_effect`, UB `neutral`, SVR `0.85`). | §7 master table |
| 151 | ok_scored | n/a | included — see §7 master table row `position = 151` (theme `momentum`, UB `neutral`, SVR `0.75`). | §7 master table |
| 152 | ok_scored | n/a | included — see §7 master table row `position = 152` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 153 | ok_scored | n/a | included — see §7 master table row `position = 153` (theme `volatility_regime`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 154 | ok_scored | n/a | included — see §7 master table row `position = 154` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.9`). | §7 master table |
| 155 | ok_scored | n/a | included — see §7 master table row `position = 155` (theme `calendar_effect`, UB `neutral`, SVR `0.75`). | §7 master table |
| 156 | ok_scored | n/a | included — see §7 master table row `position = 156` (theme `momentum`, UB `agreement_expected`, SVR `0.75`). | §7 master table |
| 157 | ok_scored | n/a | included — see §7 master table row `position = 157` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 158 | ok_scored | n/a | included — see §7 master table row `position = 158` (theme `volatility_regime`, UB `neutral`, SVR `0.95`). | §7 master table |
| 159 | ok_scored | n/a | included — see §7 master table row `position = 159` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 160 | ok_scored | n/a | included — see §7 master table row `position = 160` (theme `calendar_effect`, UB `agreement_expected`, SVR `0.9`). | §7 master table |
| 161 | ok_scored | n/a | included — see §7 master table row `position = 161` (theme `momentum`, UB `neutral`, SVR `0.75`). | §7 master table |
| 162 | ok_scored | n/a | included — see §7 master table row `position = 162` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 163 | ok_scored | n/a | included — see §7 master table row `position = 163` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 164 | ok_scored | n/a | included — see §7 master table row `position = 164` (theme `volume_divergence`, UB `neutral`, SVR `0.75`). | §7 master table |
| 165 | ok_scored | n/a | included — see §7 master table row `position = 165` (theme `calendar_effect`, UB `neutral`, SVR `0.85`). | §7 master table |
| 166 | ok_scored | n/a | included — see §7 master table row `position = 166` (theme `momentum`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 167 | ok_scored | n/a | included — see §7 master table row `position = 167` (theme `mean_reversion`, UB `neutral`, SVR `0.85`). | §7 master table |
| 168 | ok_scored | n/a | included — see §7 master table row `position = 168` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 169 | ok_scored | n/a | included — see §7 master table row `position = 169` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.9`). | §7 master table |
| 170 | ok_scored | n/a | included — see §7 master table row `position = 170` (theme `calendar_effect`, UB `neutral`, SVR `0.3`). | §7 master table |
| 171 | ok_scored | n/a | included — see §7 master table row `position = 171` (theme `momentum`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 172 | ok_scored | n/a | included — see §7 master table row `position = 172` (theme `mean_reversion`, UB `neutral`, SVR `0.95`). | §7 master table |
| 173 | ok_scored | n/a | included — see §7 master table row `position = 173` (theme `volatility_regime`, UB `neutral`, SVR `0.75`). | §7 master table |
| 174 | ok_scored | n/a | included — see §7 master table row `position = 174` (theme `volume_divergence`, UB `neutral`, SVR `0.85`). | §7 master table |
| 175 | ok_scored | n/a | included — see §7 master table row `position = 175` (theme `calendar_effect`, UB `neutral`, SVR `0.95`). | §7 master table |
| 176 | ok_scored | n/a | included — see §7 master table row `position = 176` (theme `momentum`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 177 | ok_scored | n/a | included — see §7 master table row `position = 177` (theme `mean_reversion`, UB `neutral`, SVR `0.95`). | §7 master table |
| 178 | ok_scored | n/a | included — see §7 master table row `position = 178` (theme `volatility_regime`, UB `neutral`, SVR `0.25`). | §7 master table |
| 179 | ok_scored | n/a | included — see §7 master table row `position = 179` (theme `volume_divergence`, UB `neutral`, SVR `0.85`). | §7 master table |
| 180 | ok_scored | n/a | included — see §7 master table row `position = 180` (theme `calendar_effect`, UB `neutral`, SVR `0.75`). | §7 master table |
| 181 | ok_scored | n/a | included — see §7 master table row `position = 181` (theme `momentum`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 182 | ok_scored | n/a | included — see §7 master table row `position = 182` (theme `mean_reversion`, UB `neutral`, SVR `0.95`). | §7 master table |
| 183 | ok_scored | n/a | included — see §7 master table row `position = 183` (theme `volatility_regime`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 184 | ok_scored | n/a | included — see §7 master table row `position = 184` (theme `volume_divergence`, UB `neutral`, SVR `0.85`). | §7 master table |
| 185 | ok_scored | n/a | included — see §7 master table row `position = 185` (theme `calendar_effect`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 186 | ok_scored | n/a | included — see §7 master table row `position = 186` (theme `momentum`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 187 | ok_scored | n/a | included — see §7 master table row `position = 187` (theme `mean_reversion`, UB `neutral`, SVR `0.85`). | §7 master table |
| 188 | ok_scored | n/a | included — see §7 master table row `position = 188` (theme `volatility_regime`, UB `agreement_expected`, SVR `0.8`). | §7 master table |
| 189 | ok_scored | n/a | included — see §7 master table row `position = 189` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 190 | ok_scored | n/a | included — see §7 master table row `position = 190` (theme `calendar_effect`, UB `neutral`, SVR `0.7`). | §7 master table |
| 191 | ok_scored | n/a | included — see §7 master table row `position = 191` (theme `momentum`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 192 | ok_scored | n/a | included — see §7 master table row `position = 192` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 193 | ok_scored | n/a | included — see §7 master table row `position = 193` (theme `volatility_regime`, UB `agreement_expected`, SVR `0.75`). | §7 master table |
| 194 | ok_scored | n/a | included — see §7 master table row `position = 194` (theme `volume_divergence`, UB `neutral`, SVR `0.85`). | §7 master table |
| 195 | ok_scored | n/a | included — see §7 master table row `position = 195` (theme `calendar_effect`, UB `agreement_expected`, SVR `0.9`). | §7 master table |
| 196 | ok_scored | n/a | included — see §7 master table row `position = 196` (theme `momentum`, UB `agreement_expected`, SVR `0.95`). | §7 master table |
| 197 | ok_scored | n/a | included — see §7 master table row `position = 197` (theme `mean_reversion`, UB `agreement_expected`, SVR `0.85`). | §7 master table |
| 198 | ok_scored | n/a | included — see §7 master table row `position = 198` (theme `volatility_regime`, UB `neutral`, SVR `0.9`). | §7 master table |
| 199 | ok_scored | n/a | included — see §7 master table row `position = 199` (theme `volume_divergence`, UB `agreement_expected`, SVR `0.9`). | §7 master table |
| 200 | ok_scored | n/a | included — see §7 master table row `position = 200` (theme `calendar_effect`, UB `agreement_expected`, SVR `0.75`). | §7 master table |

### Appendix B — Rule-Based Bucket Eligibility Matrix

*Populated in D8.3.2a.*

Matrix of Tier A rules, expressed as (SVR bucket × UB label) →
default bucket, with the specific scope-lock / D8.1 anchor that
grounds each rule. Every Tier A row in the master table (§7) will
cite a rule from this matrix when D8.3.2b populates the `bucket`
and `evidence_anchor` columns.

Matrix construction rulings (ratified by cross-advisor Round 1
adjudication immediately prior to this commit):

- **Q1 (`[0.50, 0.80)` × `agreement_expected`):** Tier A default =
  **REVIEW**, not KEEP. `SVR ∈ [0.50, 0.80)` is moderate evidence;
  KEEP is reserved for the high-confidence bracket `SVR ≥ 0.80`
  intersected with `agreement_expected`. Lenient-read upgrade to
  KEEP is reachable only via Tier B override with dual-anchor
  justification in D8.3.2b.
- **Q2 (fresh-7 promotion):** fresh-7 membership is a **cohort
  flag for audit**, not a Tier A bucket modifier. Pos 3
  (double-duty `divergence_cohort` ∩ `fresh_7`) is governed by the
  §4.3 narrow rebuttable presumption; no separate fresh-7 rule
  exists in this matrix. Fresh-7 narrative belongs to §9
  (D8.3.4).
- **Q3 (matrix format):** flat table, one row per `(SVR bucket ×
  UB label)` cell, per Process Note 16 narrow-reading discipline.

| SVR bucket | UB label | n | Tier A default | Rule citation |
|---|---|---|---:|---|---|
| ≤ 0.30 | `agreement_expected` | 0 | (unpopulated) | cell has no observations |
| ≤ 0.30 | `divergence_expected` | 4 | **METHOD-QUESTION** | scope lock §4.3 narrow rebuttable (pos 1, 2, 3, 5) |
| ≤ 0.30 | `neutral` | 22 | **REVIEW** | scope lock §4.2 default-to-REVIEW (Lock 2) |
| (0.30, 0.50) | `agreement_expected` | 0 | (unpopulated) | cell has no observations |
| (0.30, 0.50) | `divergence_expected` | 0 | (unpopulated) | cell has no observations |
| (0.30, 0.50) | `neutral` | 3 | **REVIEW** | scope lock §4.2 default-to-REVIEW (Lock 2) |
| [0.50, 0.80) | `agreement_expected` | 7 | **REVIEW** | scope lock §4.2 default-to-REVIEW (Lock 2); KEEP reachable only via Tier B override |
| [0.50, 0.80) | `divergence_expected` | 1 | **METHOD-QUESTION** | scope lock §4.3 narrow rebuttable (pos 6) |
| [0.50, 0.80) | `neutral` | 49 | **REVIEW** | scope lock §4.2 default-to-REVIEW (Lock 2) |
| ≥ 0.80 | `agreement_expected` | 57 | **KEEP** | D8.1 §6.2.1 agreement gate PASS ∩ §6.3(a) upper-tail gate PASS; high-confidence structural-redundancy confirmation |
| ≥ 0.80 | `divergence_expected` | 0 | (unpopulated) | cell has no observations |
| ≥ 0.80 | `neutral` | 54 | **REVIEW** | scope lock §4.2 default-to-REVIEW (Lock 2) |

**Predicted Tier A default tally (to be applied in D8.3.2b):**
**57 KEEP / 135 REVIEW / 5 METHOD-QUESTION / 0 DEFER / 0
DROP-DUPLICATIVE = 197 rows.** DEFER and DROP-DUPLICATIVE are
reachable only via Tier B overrides per scope lock §3.2 bucket
definitions. Quarantined positions (42, 87, 116) are outside the
matrix — see Appendix A.

### Appendix C — Discretionary Override Log

*Populated incrementally: D8.3.2c (non-rebuttable Tier B overrides)
and D8.3.3 (rebuttable-presumption resolution).*

Per-override record for every Tier B assignment and every
rebuttable-presumption override. Each entry includes position,
bucket, dual-anchor citation (primary + secondary), rationale, and
spot-check outcome (for the 100% METHOD-QUESTION subset and the 10%
round-up sample of other Tier B).

Fixed column schema for Appendix C entries (D8.3.1-locked; sub-phases
populate rows, do not alter header):

| `position` | `default_bucket` | `override_bucket` | `override_reason` | `evidence_anchor` | `reviewer_check` |
|---|---|---|---|---|---|
| *int* | *enum of 5 buckets or `rebuttable_MQ`* | *enum of 5 buckets* | *string* | *string (D8.1/D8.2 citation)* | *string: `spot_checked` / `sampled_10pct` / `not_sampled`* |

This schema matters for pos 3 (double-duty) and every rebuttable
presumption override on the five §6.2.2 divergence positions
(pos 1, 2, 3, 5, 6).

#### C.1 D8.3.2c non-rebuttable Tier B overrides (2 rows)

Both rows are DEFER routes anchored by the D8.2 §8.4 "RSI-absent
vol_regime twins" explicit D8.3 handoff paired with D8.2 §6.6(B)
LOW-SVR/HIGH-alignment cluster membership. Both rows carry
`reviewer_check = spot_checked` (100% spot-check applied given the
small override count).

| `position` | `default_bucket` | `override_bucket` | `override_reason` | `evidence_anchor` | `reviewer_check` |
|---|---|---|---|---|---|
| 138 | REVIEW | DEFER | RSI-absent vol_regime twin (pos 138, 143) with explicit D8.2 §8.4 test-retest handoff to D8.3; scope lock §3.2 canonical DEFER case | D8.2 §8.4 "RSI-absent vol_regime twins" (pointer to D8.3 test-retest); D8.2 §6.6(B) LOW-SVR/HIGH-aln cluster membership (line 723); scope lock §3.2 canonical DEFER definition | spot_checked |
| 143 | REVIEW | DEFER | RSI-absent vol_regime twin (pos 138, 143) with explicit D8.2 §8.4 test-retest handoff to D8.3; scope lock §3.2 canonical DEFER case; pos 143 NOT fresh-7 literal — anchor is §6.6(B) cluster, not §6.4 fresh-7 set | D8.2 §8.4 "RSI-absent vol_regime twins" (pointer to D8.3 test-retest); D8.2 §6.6(B) LOW-SVR/HIGH-aln cluster membership (line 723); scope lock §3.2 canonical DEFER definition | spot_checked |

#### C.2 D8.3.3a rebuttable-presumption resolution (5 rows, full adjudication log)

Scope lock §3.4 narrow rebuttable METHOD-QUESTION presumption applied
to all five §6.2.2 divergence-cohort positions (pos 1, 2, 3, 5, 6).
Per scope lock §6.2 discipline, 100% spot-check applied; all five
positions carry `reviewer_check = spot_checked`. Four positions upheld
the METHOD-QUESTION default; pos 6 was overridden to REVIEW under
§5.3 Tier B dual-anchor discipline. Schema extended with a `decision`
column (values: `upheld` / `overridden`) per D8.3.3a ratification for
mechanical auditability of upheld-vs-overridden status.

| `position` | `default_bucket` | `decision` | `override_bucket` | `rationale` | `evidence_anchor` | `reviewer_check` |
|---|---|---|---|---|---|---|
| 1 | METHOD-QUESTION | upheld | METHOD-QUESTION | SVR = 0.0 in LE_0.30 bracket with divergence_expected label disconfirmation; no sufficient dual-anchor rebuttal was identified under the D8.3.3a evidence standard (individual SVR well below §6.2.2 0.5 threshold and no §6.4 or stage2b_overlap secondary anchor applies). §4.3 narrow rebuttable presumption default stands; D8.4 divergence-label audit owns final interpretation. | primary: aggregate_record.json per_call_records[0] SVR=0.0, theme_alignment=0.85, plausibility=0.45; secondary: §4.3 narrow rebuttable default (no rebuttal anchor available) | spot_checked |
| 2 | METHOD-QUESTION | upheld | METHOD-QUESTION | SVR = 0.15 in LE_0.30 bracket with divergence_expected label disconfirmation; no sufficient dual-anchor rebuttal was identified under the D8.3.3a evidence standard. §4.3 narrow rebuttable presumption default stands; D8.4 divergence-label audit owns final interpretation. | primary: aggregate_record.json per_call_records[1] SVR=0.15, theme_alignment=0.95, plausibility=0.75; secondary: §4.3 narrow rebuttable default | spot_checked |
| 3 | METHOD-QUESTION | upheld | METHOD-QUESTION | Double-duty case: member of §6.2.2 divergence cohort (FALSIFIED) and §6.4 fresh-7 cohort (PASS contributor, SVR<0.5). Fresh-7 membership is a competing cohort-level observation, not an individual-strength rebuttal anchor; §6.4 PASS contribution co-occurs with pos 43 and 128 but does not satisfy §5.3 dual-anchor discipline for pos 3 specifically. Directional conflict (§6.2.2 FALSIFIED vs §6.4 PASS) remains unresolved and is handed to D8.4 divergence-label audit per scope lock §3.4 framing. | primary: aggregate_record.json per_call_records[2] SVR=0.15, theme_alignment=0.85, plausibility=0.75, fresh_7=Y; secondary: scope lock §3.4 pos 3 explicit adjudication clause; §4.3 narrow rebuttable default | spot_checked |
| 5 | METHOD-QUESTION | upheld | METHOD-QUESTION | SVR = 0.15 in LE_0.30 bracket with divergence_expected label disconfirmation; no sufficient dual-anchor rebuttal was identified under the D8.3.3a evidence standard. §4.3 narrow rebuttable presumption default stands; D8.4 divergence-label audit owns final interpretation. | primary: aggregate_record.json per_call_records[4] SVR=0.15, theme_alignment=0.85, plausibility=0.75; secondary: §4.3 narrow rebuttable default | spot_checked |
| 6 | METHOD-QUESTION | overridden | REVIEW | Tier B rebuttable rebuttal under §5.3 dual-anchor discipline: (1) individual evidence strength — SVR 0.75 in GE_0.50_LT_0.80 bracket + theme_alignment 0.95 + plausibility 0.85 (highest evidence quality among the 5 divergence positions); (2) pos 6 is the sole §6.2.2 aggregate gate SVR ≥ 0.5 contributor (1/5 observation) — the structural-redundancy observation that drove the §6.2.2 single contribution belongs to pos 6 specifically, rebutting the default presumption. REVIEW (not KEEP) because divergence_expected label disconfirmation binds at claim-level context regardless of individual SVR. `d8_followup = D8.4` retained as methodology-advisory (not bucket-blocking): bucket = REVIEW is triage disposition, follow-up = D8.4 is divergence-label-audit orthogonal context. | primary: aggregate_record.json per_call_records[5] SVR=0.75, theme_alignment=0.95, plausibility=0.85; secondary: D8.2 §6.2.2 aggregate gate 1/5 observation (pos 6 is sole SVR ≥ 0.5 contributor; only divergence-cohort row above threshold) | spot_checked |

### Appendix D — SHA Verification Log

*Populated incrementally; closed in D8.3.5.*

Per-turn byte-match verification history. Each entry records:
sub-phase (D8.3.x), expected SHAs, observed SHAs, match status. Any
mismatch is a foundation break and is recorded with remediation
notes.

**D8.3.2a pre-authoring 7-anchor verification (2026-04-24):** all
seven anchors byte-match.

| # | Artifact | Expected SHA | Observed SHA | Match |
|---|---|---|---|---|
| 1 | `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` | ✓ |
| 2 | `docs/d7_stage2d/stage2d_expectations.md` | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` | ✓ |
| 3 | `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` | ✓ |
| 4 | `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` @ `ac2586b` | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` | ✓ |
| 5 | `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` | `89d54c9821bb754d17b7085dbe6f344403da5b49824236aa8f1ee301003b4914` | `89d54c9821bb754d17b7085dbe6f344403da5b49824236aa8f1ee301003b4914` | ✓ |
| 6 | `docs/d8/D8_3_SCOPE_LOCK.md` | `f0a5598b34342fb72277d5b344152e0efd6f05bd918699e880b776ead633439c` | `f0a5598b34342fb72277d5b344152e0efd6f05bd918699e880b776ead633439c` | ✓ |
| 7 | `docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md` (pre-D8.3.2a) | `eccea5ed629d5ad0d16155695c9cb710facba166ae3c3f05691e712b6a1aca78` | `eccea5ed629d5ad0d16155695c9cb710facba166ae3c3f05691e712b6a1aca78` | ✓ |

#### D8.3.2b pre-authoring SHA re-verification (2026-04-24)

Mandatory 7-anchor byte-match re-verification per scope lock §2 before
applying Tier A rule matrix to the §7.5 master-table body.

| Anchor | Expected (from D8.3.2a seal, this file's row = then-current) | Observed 2026-04-24 pre-D8.3.2b |
|---|---|---|
| `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` | `1fb1161c...8c5e998` | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` ✓ |
| `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` | `09eeda32...5c323f` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` ✓ |
| `docs/d7_stage2d/stage2d_expectations.md` | `98b87a70...4010a5` | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` ✓ |
| `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` | `20f58ed8...dbc6d60` | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` ✓ |
| `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` | `89d54c98...03b4914` | `89d54c9821bb754d17b7085dbe6f344403da5b49824236aa8f1ee301003b4914` ✓ |
| `docs/d8/D8_3_SCOPE_LOCK.md` | `f0a5598b...33439c` | `f0a5598b34342fb72277d5b344152e0efd6f05bd918699e880b776ead633439c` ✓ |
| `docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md` | `8fffbdca...489a42` (D8.3.2a seal) | `8fffbdcac55dc554607a326dc4f25ae6506f3dad144403645cede5abba489a42` ✓ |

All 7 anchors byte-match. D8.3.2b Tier A rule application proceeds against
the locked inputs.

#### D8.3.2b post-authoring invariant verification

| Invariant | Expected | Observed |
|---|---|---|
| §7.5 master-table row count | 197 | 197 |
| Quarantine absence (pos 42, 87, 116) | absent | absent |
| Bucket distribution | 57 KEEP / 135 REVIEW / 5 METHOD-QUESTION / 0 DEFER / 0 DROP-DUPLICATIVE | 57 / 135 / 5 / 0 / 0 |
| METHOD-QUESTION positions | [1, 2, 3, 5, 6] | [1, 2, 3, 5, 6] |
| `d8_followup` = `D8.4` count | 5 (one per METHOD-QUESTION row) | 5 |
| `d8_followup` = `none` count | 192 (KEEP + REVIEW) | 192 |
| `secondary_evidence` blank count | 197 (all Tier A) | 197 |
| Forbidden language in rationale prose | 0 occurrences | 0 |
| Rationale sentence count per row | ≤ 3 | 3 max observed |

#### D8.3.2c pre-authoring SHA re-verification (2026-04-24)

Mandatory 7-anchor byte-match re-verification per scope lock §2 before
applying non-rebuttable Tier B overrides to the §7.5 master-table body
and populating Appendix C.

| Anchor | Expected (from D8.3.2b seal) | Observed 2026-04-24 pre-D8.3.2c |
|---|---|---|
| `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` | `1fb1161c...8c5e998` | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` ✓ |
| `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` | `09eeda32...5c323f` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` ✓ |
| `docs/d7_stage2d/stage2d_expectations.md` | `98b87a70...4010a5` | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` ✓ |
| `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` | `20f58ed8...dbc6d60` | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` ✓ |
| `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` | `89d54c98...03b4914` | `89d54c9821bb754d17b7085dbe6f344403da5b49824236aa8f1ee301003b4914` ✓ |
| `docs/d8/D8_3_SCOPE_LOCK.md` | `f0a5598b...33439c` | `f0a5598b34342fb72277d5b344152e0efd6f05bd918699e880b776ead633439c` ✓ |
| `docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md` | `51738028...6010f31` (D8.3.2b seal) | `51738028222ad78eb76d4beb570d80e05f3c1101216ca368a7854f29f6010f31` ✓ |

All 7 anchors byte-match. D8.3.2c non-rebuttable Tier B override
application proceeds against the locked inputs.

#### D8.3.2c scope-lock note (Path B — strict scope lock)

D8.3.2c scope is narrowed to non-rebuttable Tier B overrides only.
Rebuttable-presumption resolution on the five §6.2.2 divergence
positions (pos 1, 2, 3, 5, 6), including pos 3's double-duty final
bucket assignment, is deferred to D8.3.3 per scope lock §9 literal
sub-phase plan. This is the operational split used throughout
D8.3.2c authoring:

- D8.3.2c — non-rebuttable Tier B override application in master
  table + Appendix C.1
- D8.3.3 — per-bucket narrative (§8) + rebuttable-presumption
  resolution (including pos 3 and pos 6) + Appendix C.2
- D8.3.4 — pos 138/143 RSI-absent vol_regime test-retest analysis
  (§9)
- D8.3.5 — synthesis (§10) + forward pointers (§11) + appendices
  finalization

#### D8.3.2c post-authoring invariant verification

| Invariant | Expected | Observed |
|---|---|---|
| §7.5 master-table row count | 197 | 197 |
| Quarantine absence (pos 42, 87, 116) | absent | absent |
| Bucket distribution | 57 KEEP / 133 REVIEW / 2 DEFER / 0 DROP-DUPLICATIVE / 5 METHOD-QUESTION | 57 / 133 / 2 / 0 / 5 |
| DEFER positions | [138, 143] | [138, 143] |
| METHOD-QUESTION positions | [1, 2, 3, 5, 6] | [1, 2, 3, 5, 6] |
| `d8_followup` = `D8.4` count | 5 (METHOD-QUESTION) | 5 |
| `d8_followup` = `D8.3.4` count | 2 (DEFER pos 138, 143) | 2 |
| `d8_followup` = `none` count | 190 (57 KEEP + 133 REVIEW) | 190 |
| `secondary_evidence` populated count | 2 (pos 138, 143 Tier B DEFER) | 2 |
| `secondary_evidence` blank count | 195 (all Tier A rows) | 195 |
| Appendix C.1 override row count | 2 | 2 |
| Pos 138 rationale cites §8.4 + §6.6(B) | yes | yes |
| Pos 143 rationale cites §8.4 + §6.6(B); NOT fresh-7 | yes (fresh-7 explicitly negated) | yes |
| Pos 3 bucket still METHOD-QUESTION (D8.3.3 adjudication pending) | METHOD-QUESTION | METHOD-QUESTION |
| Pos 6 bucket still METHOD-QUESTION (D8.3.3 adjudication pending) | METHOD-QUESTION | METHOD-QUESTION |
| Forbidden language in rationale prose | 0 occurrences | 0 |
| Rationale sentence count per row | ≤ 3 | 3 max observed |

#### D8.3.3a pre-authoring SHA re-verification (2026-04-24)

Mandatory 7-anchor byte-match re-verification per scope lock §2 before
applying rebuttable-presumption resolution to the §7.5 master-table
body and populating Appendix C.2.

| Anchor | Expected (from D8.3.2c seal) | Observed 2026-04-24 pre-D8.3.3a |
|---|---|---|
| `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` | `1fb1161c...8c5e998` | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` ✓ |
| `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` | `09eeda32...5c323f` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` ✓ |
| `docs/d7_stage2d/stage2d_expectations.md` | `98b87a70...4010a5` | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` ✓ |
| `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` | `20f58ed8...dbc6d60` | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` ✓ |
| `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` | `89d54c98...03b4914` | `89d54c9821bb754d17b7085dbe6f344403da5b49824236aa8f1ee301003b4914` ✓ |
| `docs/d8/D8_3_SCOPE_LOCK.md` | `f0a5598b...33439c` | `f0a5598b34342fb72277d5b344152e0efd6f05bd918699e880b776ead633439c` ✓ |
| `docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md` | `ebb6205f...98cc3c` (D8.3.2c seal) | `ebb6205fe7e46fb0f9d9da177dd03084fc2dcc4d355f7bfde7daa2e51798cc3c` ✓ |

All 7 anchors byte-match. D8.3.3a rebuttable-presumption resolution
proceeds against the locked inputs.

#### D8.3.3a adjudication summary

All five §6.2.2 divergence-cohort positions (pos 1, 2, 3, 5, 6) were
explicitly evaluated under scope lock §3.4 narrow rebuttable
METHOD-QUESTION presumption. One override applied (pos 6 → REVIEW);
four upheld (pos 1, 2, 3, 5 stay METHOD-QUESTION). Pos 6's rebuttal
rationale adopts bucket/follow-up orthogonality: bucket = REVIEW is
triage disposition; `d8_followup = D8.4` is methodology-advisory
context (not bucket-blocking). Full adjudication log recorded in
Appendix C.2 with extended 7-column schema including a `decision`
column (`upheld` / `overridden`) for mechanical auditability.

#### D8.3.3a post-authoring invariant verification

| Invariant | Expected | Observed |
|---|---|---|
| §7.5 master-table row count | 197 | 197 |
| Quarantine absence (pos 42, 87, 116) | absent | absent |
| Bucket distribution | 57 KEEP / 134 REVIEW / 2 DEFER / 0 DROP-DUPLICATIVE / 4 METHOD-QUESTION | 57 / 134 / 2 / 0 / 4 |
| DEFER positions | [138, 143] | [138, 143] |
| METHOD-QUESTION positions | [1, 2, 3, 5] | [1, 2, 3, 5] |
| Pos 6 bucket | REVIEW (was METHOD-QUESTION) | REVIEW |
| `d8_followup` = `D8.4` count | 5 (pos 1, 2, 3, 5 MQ + pos 6 REVIEW-advisory) | 5 |
| `d8_followup` = `D8.3.4` count | 2 (DEFER pos 138, 143) | 2 |
| `d8_followup` = `none` count | 190 | 190 |
| `secondary_evidence` populated count | 3 (pos 6, 138, 143 Tier B) | 3 |
| `secondary_evidence` blank count | 194 | 194 |
| Appendix C.2 row count | 5 | 5 |
| Appendix C.2 `decision` = `overridden` count | 1 (pos 6) | 1 |
| Appendix C.2 `decision` = `upheld` count | 4 (pos 1, 2, 3, 5) | 4 |
| Pos 6 rationale cites §6.2.2 gate + orthogonality framing | yes | yes |
| Pos 3 double-duty explicitly adjudicated in C.2 | yes | yes |
| Pos 3 double-duty flags preserved (fresh_7=Y, divergence_cohort=Y) | yes | yes |
| Pos 138 stage2b_overlap=Y preserved | yes | yes |
| Forbidden language in rationale prose | 0 occurrences | 0 |
| Rationale sentence count per row | ≤ 3 | 3 max observed |
