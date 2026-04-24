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

### 7.5 Master-table body (D8.3.2a population)

Sorted ascending by `position`. 197 rows; the seven scope-lock §5.3
evidence columns are blank per §7.4.

SVR-bucket labels below use ASCII boundary tags for machine
readability: `LE_0.30` = SVR ≤ 0.30; `GT_0.30_LT_0.50` = 0.30 < SVR
< 0.50; `GE_0.50_LT_0.80` = 0.50 ≤ SVR < 0.80; `GE_0.80` = SVR ≥
0.80. Cohort-flag columns (`fresh_7`, `divergence_cohort`,
`stage2b_overlap`, `upper_tail`, `lower_tail`) are `Y` when true,
blank when false.

| `position` | `bucket` | `primary_evidence` | `secondary_evidence` | `evidence_anchor` | `rationale` | `d8_followup` | `theme` | `ub_label` | `svr` | `svr_bucket` | `theme_alignment` | `plausibility` | `fresh_7` | `divergence_cohort` | `stage2b_overlap` | `upper_tail` | `lower_tail` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  | momentum | divergence_expected | 0.0 | LE_0.30 | 0.85 | 0.45 |  | Y |  |  | Y |
| 2 |  |  |  |  |  |  | mean_reversion | divergence_expected | 0.15 | LE_0.30 | 0.95 | 0.75 |  | Y |  |  | Y |
| 3 |  |  |  |  |  |  | volatility_regime | divergence_expected | 0.15 | LE_0.30 | 0.85 | 0.75 | Y | Y |  |  | Y |
| 4 |  |  |  |  |  |  | volume_divergence | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 5 |  |  |  |  |  |  | calendar_effect | divergence_expected | 0.15 | LE_0.30 | 0.85 | 0.75 |  | Y |  |  | Y |
| 6 |  |  |  |  |  |  | momentum | divergence_expected | 0.75 | GE_0.50_LT_0.80 | 0.95 | 0.85 |  | Y |  |  |  |
| 7 |  |  |  |  |  |  | mean_reversion | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.65 |  |  |  |  |  |
| 8 |  |  |  |  |  |  | volatility_regime | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.65 |  |  |  |  |  |
| 9 |  |  |  |  |  |  | volume_divergence | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 10 |  |  |  |  |  |  | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 11 |  |  |  |  |  |  | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.95 | 0.75 |  |  |  |  |  |
| 12 |  |  |  |  |  |  | mean_reversion | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 13 |  |  |  |  |  |  | volatility_regime | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 14 |  |  |  |  |  |  | volume_divergence | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 15 |  |  |  |  |  |  | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.65 |  |  |  |  |  |
| 16 |  |  |  |  |  |  | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 17 |  |  |  |  |  |  | mean_reversion | neutral | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  | Y | Y |  |
| 18 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 19 |  |  |  |  |  |  | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 20 |  |  |  |  |  |  | calendar_effect | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 21 |  |  |  |  |  |  | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.7 |  |  |  |  |  |
| 22 |  |  |  |  |  |  | mean_reversion | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 23 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 24 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.85 | GE_0.80 | 0.7 | 0.35 |  |  |  | Y |  |
| 25 |  |  |  |  |  |  | calendar_effect | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.65 |  |  |  |  |  |
| 26 |  |  |  |  |  |  | momentum | neutral | 0.3 | LE_0.30 | 0.9 | 0.75 |  |  |  |  | Y |
| 27 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 28 |  |  |  |  |  |  | volatility_regime | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 29 |  |  |  |  |  |  | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 30 |  |  |  |  |  |  | calendar_effect | neutral | 0.35 | GT_0.30_LT_0.50 | 0.75 | 0.65 |  |  |  |  |  |
| 31 |  |  |  |  |  |  | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 32 |  |  |  |  |  |  | mean_reversion | neutral | 0.95 | GE_0.80 | 0.7 | 0.3 |  |  |  | Y |  |
| 33 |  |  |  |  |  |  | volatility_regime | neutral | 0.15 | LE_0.30 | 0.9 | 0.75 |  |  |  |  | Y |
| 34 |  |  |  |  |  |  | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 35 |  |  |  |  |  |  | calendar_effect | neutral | 0.25 | LE_0.30 | 0.75 | 0.65 |  |  |  |  | Y |
| 36 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 37 |  |  |  |  |  |  | mean_reversion | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 38 |  |  |  |  |  |  | volatility_regime | neutral | 0.25 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 39 |  |  |  |  |  |  | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.7 | 0.45 |  |  |  |  |  |
| 40 |  |  |  |  |  |  | calendar_effect | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 41 |  |  |  |  |  |  | momentum | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 43 |  |  |  |  |  |  | volatility_regime | neutral | 0.25 | LE_0.30 | 0.9 | 0.75 | Y |  |  |  | Y |
| 44 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.85 | 0.35 |  |  |  | Y |  |
| 45 |  |  |  |  |  |  | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.75 | 0.65 |  |  |  |  |  |
| 46 |  |  |  |  |  |  | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 47 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 48 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 49 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.8 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 50 |  |  |  |  |  |  | calendar_effect | neutral | 0.3 | LE_0.30 | 0.85 | 0.65 |  |  |  |  | Y |
| 51 |  |  |  |  |  |  | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 52 |  |  |  |  |  |  | mean_reversion | neutral | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 53 |  |  |  |  |  |  | volatility_regime | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 54 |  |  |  |  |  |  | volume_divergence | neutral | 0.8 | GE_0.80 | 0.65 | 0.35 |  |  |  | Y |  |
| 55 |  |  |  |  |  |  | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.7 |  |  |  |  |  |
| 56 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 57 |  |  |  |  |  |  | mean_reversion | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 58 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 59 |  |  |  |  |  |  | volume_divergence | neutral | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 60 |  |  |  |  |  |  | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 61 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 62 |  |  |  |  |  |  | mean_reversion | neutral | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 63 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 64 |  |  |  |  |  |  | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 65 |  |  |  |  |  |  | calendar_effect | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.65 |  |  |  |  |  |
| 66 |  |  |  |  |  |  | momentum | neutral | 0.25 | LE_0.30 | 0.9 | 0.75 |  |  |  |  | Y |
| 67 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 68 |  |  |  |  |  |  | volatility_regime | neutral | 0.9 | GE_0.80 | 0.85 | 0.75 | Y |  |  | Y |  |
| 69 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 70 |  |  |  |  |  |  | calendar_effect | neutral | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 71 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 72 |  |  |  |  |  |  | mean_reversion | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 73 |  |  |  |  |  |  | volatility_regime | neutral | 0.95 | GE_0.80 | 0.85 | 0.7 |  |  | Y | Y |  |
| 74 |  |  |  |  |  |  | volume_divergence | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  | Y |  |  |
| 75 |  |  |  |  |  |  | calendar_effect | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 76 |  |  |  |  |  |  | momentum | neutral | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 77 |  |  |  |  |  |  | mean_reversion | neutral | 0.9 | GE_0.80 | 0.4 | 0.3 |  |  |  | Y |  |
| 78 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 79 |  |  |  |  |  |  | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.7 | 0.35 |  |  |  |  |  |
| 80 |  |  |  |  |  |  | calendar_effect | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 81 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 82 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.4 | 0.25 |  |  |  | Y |  |
| 83 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 84 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 85 |  |  |  |  |  |  | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 86 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.8 |  |  |  | Y |  |
| 88 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 89 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 90 |  |  |  |  |  |  | calendar_effect | neutral | 0.8 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 91 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 92 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 93 |  |  |  |  |  |  | volatility_regime | neutral | 0.7 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 94 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.75 | 0.35 |  |  |  | Y |  |
| 95 |  |  |  |  |  |  | calendar_effect | neutral | 0.15 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 96 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 97 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  | Y | Y |  |
| 98 |  |  |  |  |  |  | volatility_regime | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 99 |  |  |  |  |  |  | volume_divergence | neutral | 0.25 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 100 |  |  |  |  |  |  | calendar_effect | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 101 |  |  |  |  |  |  | momentum | neutral | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 102 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.4 | 0.2 |  |  |  | Y |  |
| 103 |  |  |  |  |  |  | volatility_regime | neutral | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 104 |  |  |  |  |  |  | volume_divergence | neutral | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 105 |  |  |  |  |  |  | calendar_effect | neutral | 0.85 | GE_0.80 | 0.85 | 0.7 |  |  |  | Y |  |
| 106 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 107 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.7 | 0.45 |  |  |  | Y |  |
| 108 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.7 |  |  |  |  |  |
| 109 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 110 |  |  |  |  |  |  | calendar_effect | neutral | 0.85 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 111 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 112 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.9 | GE_0.80 | 0.75 | 0.35 |  |  |  | Y |  |
| 113 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 114 |  |  |  |  |  |  | volume_divergence | neutral | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 115 |  |  |  |  |  |  | calendar_effect | neutral | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 117 |  |  |  |  |  |  | mean_reversion | neutral | 0.85 | GE_0.80 | 0.3 | 0.2 |  |  |  | Y |  |
| 118 |  |  |  |  |  |  | volatility_regime | neutral | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 119 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.65 | 0.75 |  |  |  |  |  |
| 120 |  |  |  |  |  |  | calendar_effect | neutral | 0.3 | LE_0.30 | 0.85 | 0.7 |  |  |  |  | Y |
| 121 |  |  |  |  |  |  | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 122 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.75 | 0.25 |  |  |  | Y |  |
| 123 |  |  |  |  |  |  | volatility_regime | neutral | 0.3 | LE_0.30 | 0.75 | 0.65 |  |  |  |  | Y |
| 124 |  |  |  |  |  |  | volume_divergence | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 125 |  |  |  |  |  |  | calendar_effect | agreement_expected | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 126 |  |  |  |  |  |  | momentum | agreement_expected | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 127 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 128 |  |  |  |  |  |  | volatility_regime | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 | Y |  |  |  | Y |
| 129 |  |  |  |  |  |  | volume_divergence | neutral | 0.35 | GT_0.30_LT_0.50 | 0.9 | 0.75 |  |  |  |  |  |
| 130 |  |  |  |  |  |  | calendar_effect | neutral | 0.35 | GT_0.30_LT_0.50 | 0.85 | 0.7 |  |  |  |  |  |
| 131 |  |  |  |  |  |  | momentum | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 132 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.75 | 0.3 |  |  |  |  |  |
| 133 |  |  |  |  |  |  | volatility_regime | neutral | 0.15 | LE_0.30 | 0.9 | 0.75 |  |  |  |  | Y |
| 134 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.7 | 0.45 |  |  |  | Y |  |
| 135 |  |  |  |  |  |  | calendar_effect | neutral | 0.85 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 136 |  |  |  |  |  |  | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 137 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.7 | 0.3 |  |  |  | Y |  |
| 138 |  |  |  |  |  |  | volatility_regime | neutral | 0.25 | LE_0.30 | 0.9 | 0.75 |  |  | Y |  | Y |
| 139 |  |  |  |  |  |  | volume_divergence | neutral | 0.95 | GE_0.80 | 0.6 | 0.35 |  |  |  | Y |  |
| 140 |  |  |  |  |  |  | calendar_effect | neutral | 0.8 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 141 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 142 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.7 | 0.45 |  |  |  | Y |  |
| 143 |  |  |  |  |  |  | volatility_regime | neutral | 0.15 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 144 |  |  |  |  |  |  | volume_divergence | neutral | 0.8 | GE_0.80 | 0.65 | 0.35 |  |  |  | Y |  |
| 145 |  |  |  |  |  |  | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 146 |  |  |  |  |  |  | momentum | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 147 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.75 | 0.45 |  |  |  | Y |  |
| 148 |  |  |  |  |  |  | volatility_regime | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 149 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.7 | 0.35 |  |  |  | Y |  |
| 150 |  |  |  |  |  |  | calendar_effect | neutral | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 151 |  |  |  |  |  |  | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 152 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.75 | 0.35 |  |  |  | Y |  |
| 153 |  |  |  |  |  |  | volatility_regime | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 154 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 155 |  |  |  |  |  |  | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 156 |  |  |  |  |  |  | momentum | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 157 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 158 |  |  |  |  |  |  | volatility_regime | neutral | 0.95 | GE_0.80 | 0.75 | 0.45 |  |  |  | Y |  |
| 159 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 160 |  |  |  |  |  |  | calendar_effect | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.7 |  |  |  | Y |  |
| 161 |  |  |  |  |  |  | momentum | neutral | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 162 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.75 | 0.4 |  |  |  | Y |  |
| 163 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 164 |  |  |  |  |  |  | volume_divergence | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.75 |  |  |  |  |  |
| 165 |  |  |  |  |  |  | calendar_effect | neutral | 0.85 | GE_0.80 | 0.65 | 0.35 |  |  |  | Y |  |
| 166 |  |  |  |  |  |  | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 167 |  |  |  |  |  |  | mean_reversion | neutral | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 168 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.8 | 0.65 |  |  |  |  |  |
| 169 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 170 |  |  |  |  |  |  | calendar_effect | neutral | 0.3 | LE_0.30 | 0.85 | 0.75 |  |  |  |  | Y |
| 171 |  |  |  |  |  |  | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 172 |  |  |  |  |  |  | mean_reversion | neutral | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 173 |  |  |  |  |  |  | volatility_regime | neutral | 0.75 | GE_0.50_LT_0.80 | 0.8 | 0.65 | Y |  |  |  |  |
| 174 |  |  |  |  |  |  | volume_divergence | neutral | 0.85 | GE_0.80 | 0.65 | 0.35 |  |  |  | Y |  |
| 175 |  |  |  |  |  |  | calendar_effect | neutral | 0.95 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 176 |  |  |  |  |  |  | momentum | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 177 |  |  |  |  |  |  | mean_reversion | neutral | 0.95 | GE_0.80 | 0.75 | 0.45 |  |  |  | Y |  |
| 178 |  |  |  |  |  |  | volatility_regime | neutral | 0.25 | LE_0.30 | 0.85 | 0.7 |  |  |  |  | Y |
| 179 |  |  |  |  |  |  | volume_divergence | neutral | 0.85 | GE_0.80 | 0.75 | 0.35 |  |  |  | Y |  |
| 180 |  |  |  |  |  |  | calendar_effect | neutral | 0.75 | GE_0.50_LT_0.80 | 0.85 | 0.65 |  |  |  |  |  |
| 181 |  |  |  |  |  |  | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 182 |  |  |  |  |  |  | mean_reversion | neutral | 0.95 | GE_0.80 | 0.7 | 0.35 |  |  |  | Y |  |
| 183 |  |  |  |  |  |  | volatility_regime | agreement_expected | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 184 |  |  |  |  |  |  | volume_divergence | neutral | 0.85 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 185 |  |  |  |  |  |  | calendar_effect | agreement_expected | 0.85 | GE_0.80 | 0.75 | 0.65 |  |  |  | Y |  |
| 186 |  |  |  |  |  |  | momentum | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 187 |  |  |  |  |  |  | mean_reversion | neutral | 0.85 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 188 |  |  |  |  |  |  | volatility_regime | agreement_expected | 0.8 | GE_0.80 | 0.85 | 0.75 | Y |  |  | Y |  |
| 189 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 190 |  |  |  |  |  |  | calendar_effect | neutral | 0.7 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 191 |  |  |  |  |  |  | momentum | agreement_expected | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 192 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.95 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 193 |  |  |  |  |  |  | volatility_regime | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.9 | 0.75 |  |  |  |  |  |
| 194 |  |  |  |  |  |  | volume_divergence | neutral | 0.85 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 195 |  |  |  |  |  |  | calendar_effect | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.65 |  |  |  | Y |  |
| 196 |  |  |  |  |  |  | momentum | agreement_expected | 0.95 | GE_0.80 | 0.9 | 0.75 |  |  |  | Y |  |
| 197 |  |  |  |  |  |  | mean_reversion | agreement_expected | 0.85 | GE_0.80 | 0.7 | 0.45 |  |  |  | Y |  |
| 198 |  |  |  |  |  |  | volatility_regime | neutral | 0.9 | GE_0.80 | 0.85 | 0.75 | Y |  |  | Y |  |
| 199 |  |  |  |  |  |  | volume_divergence | agreement_expected | 0.9 | GE_0.80 | 0.85 | 0.75 |  |  |  | Y |  |
| 200 |  |  |  |  |  |  | calendar_effect | agreement_expected | 0.75 | GE_0.50_LT_0.80 | 0.75 | 0.65 |  |  |  |  |  |

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
