# D8.3 Scope Lock — Stage 2d Strategy Triage

**Sub-phase:** D8.3.0 (scope lock, immutable upon ratification).

**Document authority:** this file binds all D8.3.x authoring work that
follows. Any item outside this scope lock requires a new ratified
scope amendment committed as a successor sub-phase (D8.3.N+1), never
silent drift.

**Relationship to D8.2:** D8.3 consumes D8.2's claim-level
adjudications as binding context and routes already-scored Stage 2d
candidates into practical strategy-disposition buckets. D8.3 is not
a claim re-adjudication, not a methodology-fix phase, and not a
backtest-selection beauty contest.

---

## 1. Purpose and Binding Force

**D8.3 is evidence-based strategy disposition. It is not a new
research claim adjudication, not a methodology-fix phase, and not a
backtest-selection beauty contest.**

D8.3 authors the canonical Stage 2d strategy-triage document
(`docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md`) by classifying each of
the 197 ok-scored Stage 2d candidates into one of five practical
buckets (§3.1). Every bucket assignment must be anchored to
already-sealed D8.1 or D8.2 evidence; no new LLM calls, no new
backtests, no re-scoring, no methodology fixes.

D8.3's outputs feed:
- **D8.4** (methodology refinement) — METHOD-QUESTION routings
  surface candidates whose triage is blocked by a methodology
  question sealed in D8.2.
- **D8.3.4** (test-retest sub-phase) — pos 138 / 143 RSI-absent
  vol_regime twins receive a dedicated analysis subsection.
- **Future Stage 2e+ or live-fire planning** — KEEP / PRIORITIZE
  candidates form the basis for any downstream strategy activation
  work in later phases.

D8.3 introduces no new verdicts on pre-registered Stage 2d claims.
D8.2 verdicts bind as claim-level context, not as automatic
candidate-level bucket assignments (see §3.4).

---

## 2. Inputs

### 2.1 Git-committed anchors

| Anchor | Commit | Note |
|---|---|---|
| D8.2 adjudication doc (final) | `cd870c3` | `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` |
| D8.2.0 scope lock (reference) | `c78ab10` | `docs/d8/D8_2_SCOPE_LOCK.md` |
| D8.1 notebook (final) | `ac2586b` | `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` |
| D8.0 phase signoff (reference; not amended) | (Stage 2d signoff commit) | `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` |

### 2.2 File SHA anchors (byte-match required at every D8.3.x authoring turn)

| File | SHA-256 |
|---|---|
| `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` | `89d54c9821bb754d17b7085dbe6f344403da5b49824236aa8f1ee301003b4914` |
| `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` |
| `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` |
| `docs/d7_stage2d/stage2d_expectations.md` | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` |
| `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` |

Pre-authoring re-verification is mandatory at every D8.3.x turn. If
any anchor SHA drifts, D8.3 authoring halts until the drift is
investigated and either ratified or reverted.

### 2.3 Cohort accountability (primary triage universe)

| Cohort | Size | Role in D8.3 |
|---|---|---|
| Source positions | 200 | Full Stage 2d source universe (audit reference only) |
| UB call cohort | 199 | Excludes pos 116 (skipped-source); claim-level denominator in §6.2 / §6.3 |
| Ok-scored universe | 197 | Excludes pos 42 / 87 (d7b_error) and pos 116; **primary D8.3 triage universe** |
| Quarantine (structural exclusions) | 3 | Pos 42, 87, 116 — routed to Appendix A quarantine, not the main triage table |

---

## 3. Strategy Triage Bucket Taxonomy

### 3.1 Bucket enum (five buckets, mutually exclusive)

Every row in the D8.3 master triage table assigns exactly one of:

| Bucket | Short meaning |
|---|---|
| `KEEP` | Candidate has strong evidence of practical research value and no unresolved methodology blocker |
| `REVIEW` | Candidate has mixed signal and deserves human inspection before keep/drop |
| `DEFER` | Candidate is valid, but decision depends on later non-methodological work (e.g., test-retest, cohort comparison) |
| `DROP-DUPLICATIVE` | Candidate is validly scored but has high structural variant risk and no offsetting reason to keep |
| `METHOD-QUESTION` | Candidate's triage is blocked because the scoring or labeling logic itself is under question (needs D8.4 input) |

No sixth bucket. Structural exclusions (pos 42 / 87 / 116) are not
bucketed — they are quarantined (§3.3).

### 3.2 Bucket definitions (binding)

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
depends on any of the six D8.2-sealed D8.4 methodology issues (§4.3).
This bucket has the highest downstream consequence and is subject
to 100% spot-check (§6.3).

METHOD-QUESTION is reserved for candidates whose disposition
materially depends on a known D8.4 methodology issue. It must cite
the specific D8.4 issue. Ambiguous-but-triable candidates go to
REVIEW, not METHOD-QUESTION.

### 3.3 Quarantine (structural exclusions)

Pos 42, 87, 116 have no valid D7b scores and are not
strategy-triageable. They are not bucketed; they are quarantined in
Appendix A (cohort reconciliation) with the following exclusion
reason codes:

| Position | `exclusion_reason` | Excluded from |
|---|---|---|
| 42 | `d7b_error` | 197 scored universe |
| 87 | `d7b_error` | 197 scored universe |
| 116 | `skipped_source_invalid` | 199 UB cohort (and 197 scored universe) |

Quarantine does not imply failure or rejection — it reflects that
these positions lack the evidence required for any triage
determination.

Positions 42 and 87 remain members of the 199-call UB cohort for
pre-registered aggregate-denominator accounting, but they are
excluded from D8.3 strategy triage because no D7b score exists.
Position 116 is excluded from both the 199-call UB cohort and the
197 scored universe.

### 3.4 Rebuttable METHOD-QUESTION presumption (narrow — 5 divergence positions only)

The five §6.2.2 divergence_expected cohort positions start as
METHOD-QUESTION by default per D8.2 §6.2.2 FALSIFIED
(interpretation_tag `likely_directional_model_misspecification`).
This default is **rebuttable**: D8.3 may route a divergence cohort
member elsewhere only with an explicit evidence-based override
justifying why METHOD-QUESTION is insufficient for that specific
candidate. The rebuttal burden is on the override, not on the default.

**Narrow reading.** The rebuttable-presumption framing applies only
to the five §6.2.2 divergence_expected positions (pos 1, 2, 3, 5, 6).
Other D8.2-verdict-derived concerns (e.g., §6.3(b) lower-tail
members, §6 forensic cross-tab cell members) follow the general
Tier A / Tier B discipline in §5 — equally rigorous, but without the
specific "rebuttable presumption" semantics.

**Pos 3 double-duty clause.** Pos 3 is an expected high-scrutiny
candidate because it is both a §6.2.2 divergence cohort member and
a §6.4 fresh-7 PASS contributor (under opposite directional
hypotheses). Its final bucket is decided only in D8.3.3 under Tier B
override discipline with full 100% METHOD-QUESTION spot-check.
Scope lock does not pre-bake pos 3's bucket — only the scrutiny
level.

---

## 4. Scope Boundaries

### 4.1 In scope for D8.3

- Triage of the 197 ok-scored candidates into the five buckets
  defined in §3.1, with 7-field evidence schema per §5.
- Quarantine accounting for pos 42 / 87 / 116 in Appendix A.
- Dedicated test-retest analysis for pos 138 / 143 RSI-absent
  vol_regime twins (D8.3.4).
- Synthesis of bucket-level findings and routing pointers to D8.4
  (METHOD-QUESTION) and any follow-up D8.3.x sub-phases (DEFER).
- Default-to-REVIEW discipline: **if a candidate lacks enough
  evidence for KEEP or DROP, default to REVIEW, not subjective
  preference.**

### 4.2 Out of scope for D8.3 (deferred or forbidden)

- **No new LLM calls.** D8.3 relies exclusively on D8.1 / D8.2 /
  Stage 2d aggregate artifacts.
- **No new backtests.** D8.3 does not run or consume new Backtrader
  runs.
- **No production code changes.** Strategy logic, DSL, prompt
  templates, and scoring pipelines are unchanged by D8.3.
- **No re-scoring of candidates.** D8.3 consumes existing SVR /
  alignment / plausibility scores as-is.
- **No re-adjudication of D8.2 claim verdicts.** D8.3 consumes D8.2
  verdicts as binding context; it does not revise them.
- **No amendment of D8.0, D8.1, or D8.2.** These artifacts are sealed.
- **No methodology fixes.** Every methodology question surfaces as a
  METHOD-QUESTION bucket routing; D8.4 owns methodology decisions.
- **No Phase 3+ trading decisions.** D8.3 is research-layer triage;
  capital allocation is out of scope.
- **No pre-committed bucket count targets.** D8.3 has no
  pre-committed target count for any bucket. Bucket counts are
  outputs, not goals. Authoring MUST NOT balance toward a perceived
  "right" KEEP / REVIEW / DROP distribution.
- **No silent re-scoring.** D8.3 MUST NOT recompute any d7b_llm_score
  value (SVR, alignment, plausibility). D8.3 MUST NOT apply SVR
  thresholds different from `docs/d7_stage2d/stage2d_expectations.md`.
  Any perceived need for re-scoring is a D8.4 methodology question
  surfaced via METHOD-QUESTION bucket.

### 4.3 D8.4-known methodology issues (binding METHOD-QUESTION anchors)

A candidate MUST be routed to METHOD-QUESTION if its triage depends
on any of the six D8.2-sealed D8.4 issues:

1. Divergence-label definition audit (§6.2.2 `methodology_followup`)
2. Direction-of-prediction recalibration (§6.2.2 interpretation_tag)
3. Lower-tail calibration (§6.3(b) `methodology_followup`)
4. Joint-shape asymmetric-calibration implications (§6.3 joint
   `methodology_followup`)
5. Forensic cross-tab methodology implications / prompt / label
   discipline (§7 forensic cross-tab `methodology_followup`, §8.4)
6. Documentation drift — expectations.md "6 themes" vs operational 5
   (§5 methodology recap)

---

## 5. Evidence Anchor Schema (7-field per-row structure)

Every row in the D8.3 master triage table populates these seven
fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `position` | int | always | 1-200 from Stage 2d source universe |
| `bucket` | enum | always | One of the five §3.1 buckets |
| `primary_evidence` | str | always | e.g., `"D8.1 cell 12 SVR=0.89"` |
| `secondary_evidence` | str | Tier B only | e.g., `"D8.2 §6.2.2 FALSIFIED cohort"` |
| `evidence_anchor` | str | always | Rule invoked, e.g., `"SVR≥0.80 → KEEP (Tier A)"` or `"Tier B override — rebuttable presumption"` |
| `rationale` | str (prose, ≤3 sentences) | always | Human-readable justification citing only artifact data |
| `d8_followup` | enum | always | One of: `D8.4`, `D8.3.4`, `none` |

**Tier A (rule-governed, deterministic)** — bucket follows from a
deterministic rule (SVR threshold, cohort membership, d7b_error,
skipped_source). `primary_evidence` alone is sufficient;
`secondary_evidence` may be `null`.

**Tier B (discretionary override or ambiguity resolution)** —
bucket departs from Tier A default or resolves an ambiguous case.
Requires both `primary_evidence` and `secondary_evidence` with
explicit anchors, plus a rationale naming why the Tier A default is
insufficient.

Forbidden in rationale prose: "gut feel", "seems", "looks like",
"probably", "generally speaking", theme-level generalizations
ungrounded in the specific candidate's evidence.

Required in rationale prose: specific SVR / alignment / plausibility
values with position number; cohort membership if relevant; UB
label if relevant; cross-reference to §6 verdict or §7 observation
if relevant.

---

## 6. Authoring Discipline

### 6.1 Tier A / Tier B distinction

Every bucket assignment is explicitly labeled Tier A or Tier B in
the `evidence_anchor` field. A Tier A assignment invokes a
deterministic rule (catalogued in Appendix B rule matrix). A Tier B
assignment overrides Tier A or resolves a case the rule matrix does
not cover.

### 6.2 Spot-check discipline

- **100% of METHOD-QUESTION bucket rows** are spot-checked by
  triangulated review (Claude advisor + ChatGPT critic) during
  D8.3.x Round 1 or Round 2 review.
- **10% of other Tier B / override assignments** are randomly
  sampled for triangulated review each review round. If 10% yields
  a non-integer, round up.
- Rebuttable-presumption overrides on the five §6.2.2 divergence
  positions count as Tier B override for spot-check purposes.

### 6.3 Hard rule inheritance

- **Hard rule 5** (no reinterpretation of pre-registered claims)
  extends into D8.3 unchanged. D8.3 consumes D8.2 verdicts; it does
  not reinterpret pre-registered Stage 2d claims.
- **"No silent re-scoring"** (§4.2) applies throughout. Any
  perceived SVR discrepancy or threshold disagreement surfaces as a
  METHOD-QUESTION, never as a D8.3 rescoring.

### 6.4 Default-to-REVIEW rule

**If a candidate lacks enough evidence for KEEP or DROP, default
to REVIEW, not subjective preference.** This rule applies at every
bucket assignment. The absence of evidence is never a reason to
assign KEEP or DROP-DUPLICATIVE.

---

## 7. Output Artifact Structure

D8.3 produces `docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md` with:

### 7.1 Master triage table
One row per ok-scored candidate (197 rows), seven columns per §5.
Sorted by position ascending. Source of truth for all D8.3 bucket
assignments.

### 7.2 Per-bucket subsections
One subsection per bucket (KEEP / REVIEW / DEFER / DROP-DUPLICATIVE
/ METHOD-QUESTION):
- Narrative summary of the bucket's population (size, themes, SVR
  distribution).
- Tier A rule-assigned members listed first, in position order.
- Tier B discretionary / override members with short rationale
  paragraphs (≤5 lines each, citing the 7-field row).
- Forward pointers (D8.4 for METHOD-QUESTION, D8.3.x for DEFER).

### 7.3 Dedicated D8.3.4 test-retest analysis
Section titled `"RSI-absent vol_regime test-retest: pos 138 / 143 and
fresh-7 context"`, covering overlap stability, §6.4 membership
implications, and disposition for pos 138 / 143.

### 7.4 Appendices (four)

- **Appendix A — Cohort & quarantine reconciliation.** 200 / 199 /
  197 accountability + pos 42 / 87 / 116 quarantine table with
  `exclusion_reason` codes and `excluded_from` columns.
- **Appendix B — Rule-based bucket eligibility matrix.** Tier A rule
  decision tree mapping (SVR × UB label × cohort membership) → default
  bucket. Lookupable reference for every Tier A assignment.
- **Appendix C — Discretionary override log.** Every Tier B override
  with full justification chain (position, default-Tier-A bucket,
  override bucket, rebuttal rationale, dual anchors, spot-check
  verification status).
- **Appendix D — SHA verification log.** Per-commit file SHA across
  D8.3 sub-arc commits; anchor SHAs byte-matched at each authoring
  turn.

---

## 8. Rulings on Q1–Q10 (plus S1–S4 additions)

| # | Ruling |
|---|---|
| Q1 — Cohort scope | 197 ok-scored = primary triage universe; pos 42 / 87 / 116 → Appendix A quarantine with separate `exclusion_reason` codes. No sixth bucket. |
| Q2 — Evidence schema | 7-field schema (§5). Required: position, bucket, primary_evidence, secondary_evidence (Tier B only), evidence_anchor, rationale, d8_followup. |
| Q3 — Bucket definitions | Five buckets as §3.1. Definitions binding as §3.2. Default-to-REVIEW rule locked. |
| Q4 — Pos 138 / 143 test-retest | Explicit D8.3.4 sub-phase with dedicated subsection per §7.3. |
| Q5 — D8.2 verdict binding force | Binding as claim-level context, not automatic candidate-level bucket. Rebuttable METHOD-QUESTION presumption applies narrowly to the five §6.2.2 divergence positions only (§3.4). |
| Q6 — D8.4 coupling | METHOD-QUESTION routes exactly per the six D8.4 issues in §4.3. |
| Q7 — Guardrails | Every assignment cites ≥1 evidence anchor; Tier B overrides require ≥2 anchors with explicit justification. Forbidden / required rationale language per §5. |
| Q8 — Hard rule inheritance | Hard rule 5 extends; "no silent re-scoring" locked per §4.2 / §6.3. |
| Q9 — Output shape | Master table (197 rows, 7 fields) + per-bucket subsections + D8.3.4 subsection + four appendices A–D. |
| Q10 — Sub-phase granularity | D8.3.0 → D8.3.5 per §9 sub-phase plan. |
| S1 — Anchored inputs | 5 SHA anchors, byte-match at every turn (§2.2). |
| S2 — Out of scope | 9-item explicit list (§4.2), including "no silent re-scoring". |
| S3 — Sealing conditions | D8.3.0 scope lock immutable; master-table cells immutable post-D8.3.3 except post-D8.4 re-triage (§11). |
| S4 — Cost | Zero LLM spend; zero production code changes; ~6-9 authoring turns across D8.3.0 → D8.3.5. |

---

## 9. Sub-phase plan

| Sub-phase | Scope | Estimated commits |
|---|---|---|
| D8.3.0 | Scope lock (this document) | 1 |
| D8.3.1 | Skeleton + purpose + methodology recap + bucket criteria spec | 1–2 |
| D8.3.2 | Master triage table — all 197 per-candidate assignments | 1–2 |
| D8.3.3 | Per-bucket subsections (KEEP / REVIEW / DEFER / DROP-DUPLICATIVE / METHOD-QUESTION) and Tier B / rebuttable-presumption resolution (including pos 3) | 1–2 |
| D8.3.4 | RSI-absent vol_regime test-retest: pos 138 / 143 and fresh-7 context | 1 |
| D8.3.5 | Synthesis + forward pointers + appendices A–D | 1 |
| **Total** | | **6–9 commits** |

Each sub-phase is ratified through Round 1 / Round 2 review before
commit, analogous to the D8.2 sub-arc discipline.

---

## 10. Acceptance criteria for D8.3

D8.3 is considered complete when **all** of the following hold:

1. `docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md` exists with master table
   covering exactly 197 rows, each populating all required 7 fields.
2. Every row's `bucket` value is one of the five buckets in §3.1.
3. Every row cites at least one evidence anchor; Tier B rows cite
   at least two.
4. Pos 42 / 87 / 116 appear only in Appendix A quarantine, never in
   the master table.
5. All five §6.2.2 divergence cohort positions are either
   METHOD-QUESTION or have logged rebuttable-presumption overrides
   in Appendix C.
6. Pos 138 / 143 receive dedicated D8.3.4 analysis with final bucket
   disposition recorded.
7. 100% of METHOD-QUESTION rows and 10% of other Tier B rows have
   been triangulated-reviewed; spot-check status logged in Appendix C.
8. Appendices A, B, C, D all populated.
9. D8.2 adjudication doc SHA, D8.1 notebook SHA, aggregate JSON SHA,
   expectations SHA, and D8.0 signoff SHA byte-matched against §2.2
   anchors at the final commit.
10. No new LLM calls logged against `agents/spend_ledger.db` during
    D8.3 sub-arc.
11. No edits to D8.0, D8.1, or D8.2 artifacts during D8.3 sub-arc.

---

## 11. Sealing conditions

- **D8.3.0 scope lock immutable** upon ratification and commit.
  Future amendments require a successor sub-phase with explicit
  ratification — never silent drift inside D8.3.1–D8.3.5.
- **Master triage table cells immutable post-D8.3.3 commit**, with
  one exception: a post-D8.4 re-triage sub-phase (D8.3.6+, not yet
  authorized) may update METHOD-QUESTION rows whose blocking
  methodology issue is resolved by D8.4. Any such re-triage must be
  committed as a separate sub-phase with full Round 1 / Round 2
  review and logged in Appendix C.
- **Appendix C discretionary override log append-only** across the
  D8.3 sub-arc.
- **No silent edits to bucket values** post-commit. Correction of a
  committed bucket value requires a new sub-phase commit with the
  prior value cited and the revision rationale anchored to artifact
  evidence.

---
