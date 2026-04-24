# D8.4 Scope Lock — Stage 2d Methodology Refinement

**Sub-phase:** D8.4.0 (scope lock, immutable upon ratification).

**Document authority:** this file binds all D8.4.x authoring work that
follows. Any item outside this scope lock requires a new ratified
scope amendment committed as a successor sub-phase (D8.4.N+1), never
silent drift.

**Relationship to D8.3:** D8.4 consumes D8.3's strategy-triage
artifact as binding context — specifically the rows routed to the
`METHOD-QUESTION` bucket, plus the six sealed methodology issues
catalogued in `docs/d8/D8_3_SCOPE_LOCK.md` §4.3. D8.4 is a
**proposal-only methodology phase**: it specifies how each
methodology issue should be revised and what evidence would validate
the revision. D8.4 does not execute the revisions, does not re-fire
Stage 2d, and does not modify production code.

---

## 1. Purpose and Binding Force

**D8.4 is a methodology proposal phase. It is not a methodology
implementation phase, not a re-fire phase, and not a re-adjudication
of Stage 2d claims.**

D8.4 authors a single canonical methodology-refinement document
(`docs/d8/D8_4_METHODOLOGY_REFINEMENT.md`) that addresses each of the
six D8.2-sealed methodology issues catalogued in
`docs/d8/D8_3_SCOPE_LOCK.md` §4.3. For each issue, D8.4 produces a
fixed five-part analysis (§5) anchored to already-sealed Stage 2d
evidence (D8.1 / D8.2 / D8.3 / aggregate JSON / raw payloads / D7a
flags / D7b reasoning). No new LLM calls, no new backtests, no
production code changes, no scoring-pipeline edits.

D8.4 outputs feed:
- **A future Stage 2e or Stage 2d-rerun phase (not yet authorized)** —
  D8.4's proposed revisions form the candidate slate for any
  downstream methodology-implementation work, subject to a fresh
  authorization gate.
- **D8.3 post-D8.4 re-triage (D8.3.6+, not yet authorized)** — once
  D8.4 resolves a methodology issue and that resolution has been
  validated in a later phase, the affected `METHOD-QUESTION` rows in
  the D8.3 master table become eligible for re-triage.
- **No automatic propagation.** D8.4's proposals do **not** silently
  update D8.3 bucket assignments, D8.2 verdicts, or any sealed Stage
  2d artifact.

D8.4 introduces no new verdicts on pre-registered Stage 2d claims.
D8.2 verdicts and D8.3 bucket assignments bind as context, not as
license to revise sealed conclusions.

### 1.1 D8.4 cannot do (compact advisory)

> **D8.4 cannot:**
> - claim a methodology fix is validated
> - alter D8.3 bucket assignments, `d8_followup` values, Appendix C
>   override logs, or the D8.3 final bucket distribution
>   (57/134/2/0/4)
> - re-run Stage 2d or any subset of it
> - amend `docs/d7_stage2d/stage2d_expectations.md`
> - edit Critic code, DSL, registry, or any production code
> - introduce new LLM judgments (Proposer, Critic, or otherwise)
> - retire any `METHOD-QUESTION` bucket disposition (re-triage is
>   a separate post-D8.4 sub-phase)
> - retroactively recharacterize D8.0, D8.1, D8.2, or D8.3 verdicts

### 1.2 Load-bearing framings inherited from D8.3 (preserved verbatim)

These items are quintuplication-protected drift risks. Any D8.4
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
  artifact form per D8.3 §5.3 dual-anchor", not to "no
  test-retest evidence exists." D8.4 must not silently restate this.

---

## 2. Inputs

### 2.1 Git-committed anchors

| Anchor | Commit | Note |
|---|---|---|
| D8.3 strategy triage doc (final seal) | `0b371cd` | `docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md` |
| D8.3.0 scope lock (reference, binding) | (D8.3.0 commit) | `docs/d8/D8_3_SCOPE_LOCK.md` |
| D8.2 adjudication doc (final) | `cd870c3` | `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` |
| D8.1 notebook (final) | `ac2586b` | `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` |
| D8.0 phase signoff (reference; not amended) | (Stage 2d signoff commit) | `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` |

### 2.2 File SHA anchors (byte-match required at every D8.4.x authoring turn)

| File | SHA-256 |
|---|---|
| `docs/d8/D8_3_STAGE2D_STRATEGY_TRIAGE.md` | `542c359977c1a19c6e2958b92ad9cb34b47f60606061694e875de91f2cc26b6f` |
| `docs/d8/D8_3_SCOPE_LOCK.md` | `f0a5598b34342fb72277d5b344152e0efd6f05bd918699e880b776ead633439c` |
| `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md` | `89d54c9821bb754d17b7085dbe6f344403da5b49824236aa8f1ee301003b4914` |
| `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` |
| `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` |
| `docs/d7_stage2d/stage2d_expectations.md` | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` |
| `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` |

Pre-authoring re-verification is mandatory at every D8.4.x turn. If
any anchor SHA drifts, D8.4 authoring halts until the drift is
investigated and either ratified or reverted.

### 2.3 Methodology-issue universe (binding triage anchor)

The six methodology issues in scope are **exactly** those catalogued
in `docs/d8/D8_3_SCOPE_LOCK.md` §4.3, restated here for reference
(the D8.3 scope-lock §4.3 list is the source of truth; if these two
restatements ever diverge, D8.3 §4.3 governs):

1. **Divergence-label definition audit** — §6.2.2 `methodology_followup`
2. **Direction-of-prediction recalibration** — §6.2.2 interpretation_tag
   `likely_directional_model_misspecification`
3. **Lower-tail calibration** — §6.3(b) `methodology_followup`
4. **Joint-shape asymmetric-calibration implications** — §6.3 joint
   `methodology_followup`
5. **Forensic cross-tab methodology / prompt / label discipline** —
   §7 forensic cross-tab `methodology_followup`, §8.4
6. **Documentation drift** — `expectations.md` "6 themes" vs operational
   5 (§5 methodology recap)

No seventh issue may be added inside D8.4. A new methodology issue
discovered during D8.4 authoring surfaces as a **D8.4 follow-up
pointer** in the synthesis section, not as an in-scope analysis.

---

## 3. Scope Boundaries

### 3.1 In scope for D8.4

- Per-issue methodology analysis using the fixed five-part structure
  (§5), one analysis section per issue, six total.
- Synthesis section consolidating cross-issue themes and any newly
  surfaced (out-of-scope) methodology questions for forward
  pointers.
- Forward-pointer section identifying which downstream phase owns
  each proposed revision's implementation and validation.
- Closeout section sealing the D8.4 sub-arc with full SHA log and
  invariant verification.

### 3.2 Out of scope for D8.4 (deferred or forbidden)

- **No new LLM calls.** D8.4 relies exclusively on D8.1 / D8.2 / D8.3
  / Stage 2d aggregate / raw payloads / D7a flags / D7b reasoning.
- **No new backtests.** D8.4 does not run or consume new Backtrader
  runs.
- **No production code changes.** Strategy logic, DSL, prompt
  templates, scoring pipelines, expectations.md, and registry/config
  files are unchanged by D8.4.
- **No methodology implementation.** D8.4 specifies revisions; it
  does not apply them. A revision proposed by D8.4 is not a
  validated fix.
- **No re-fire of Stage 2d.** Stage 2d is sealed (D7 Stage 2d signoff).
  D8.4 does not author or schedule a re-fire.
- **No re-scoring of candidates.** D8.4 consumes existing SVR /
  alignment / plausibility scores as-is.
- **No re-adjudication of D8.2 claim verdicts.** D8.2 verdicts bind
  as context.
- **No edits to D8.3 master triage table.** D8.3 bucket assignments
  are sealed under D8.3.0 §11 sealing conditions. Any D8.3 re-triage
  belongs to a separate authorized sub-phase.
- **No re-bucketing of D8.3 candidates.** D8.4 does not revise D8.3
  bucket assignments, `d8_followup` values, Appendix C override
  logs, or the D8.3 final bucket distribution (57/134/2/0/4). Any
  post-D8.4 re-triage requires a separately ratified post-D8.4
  cycle. This applies with particular force to pos 1, 2, 3, 5, 6
  (touched by issues 1 and 2) and pos 138, 143 (touched by any
  test-retest framing under any issue).
- **No silent amendment of expectations.md.** Documentation-drift
  issue (#6) proposes a fix; the actual edit belongs to a later
  authorized phase.
- **No edits to D8.0, D8.1, D8.2, or D8.3 artifacts** during D8.4
  sub-arc. These are sealed.
- **No Phase 3+ trading decisions.** D8.4 is research-layer
  methodology proposal; capital allocation is out of scope.
- **No fix-validation conflation.** D8.4 must explicitly distinguish
  "proposed methodology revision" from "validation evidence." The
  per-issue five-part structure (§5) enforces this separation by
  giving each its own slot.

### 3.3 Hard locks (additional D8.4-specific)

- **Lock A — Proposal-only.** D8.4 proposes methodology revisions; it
  does not execute them. No revision proposed in D8.4 may be
  characterized as "applied," "fixed," or "validated" within D8.4
  itself. Each revision must be paired with a forward-phase pointer
  identifying who implements and who validates.
- **Lock B — Specification vs validation separation.** Each per-issue
  section must distinguish (a) the proposed methodology fix from
  (b) the evidence that would validate the fix in a future phase.
  Proposing a fix is not the same as demonstrating it works.
- **Lock C — No silent retroactive recasting.** D8.4 must not
  retroactively recharacterize sealed D8.2 verdicts or D8.3 bucket
  assignments as "wrong." A D8.2 FALSIFIED verdict remains
  FALSIFIED; D8.4 may propose how to recalibrate the methodology
  going forward but does not revoke the sealed verdict.
- **Lock D — Six-issue boundary.** No seventh methodology issue
  enters D8.4. Newly surfaced methodology questions become
  forward-pointer items in synthesis, deferred to a future phase.

---

## 4. Evidence Scope (permissive but offline-only)

D8.4 may consult the following sealed artifacts:

| Artifact | Use in D8.4 |
|---|---|
| D8.1 notebook | Cell-level numeric anchors for any per-issue diagnosis |
| D8.2 adjudication doc | Claim-level verdicts + interpretation tags + methodology_followup tags |
| D8.3 strategy triage doc | METHOD-QUESTION rows + Tier A/B taxonomy + Appendix C overrides |
| Stage 2d aggregate JSON | Per-call records, themes, scores, pre-registered labels |
| Raw payloads | D7b prompt / response artifacts (forensic only — never re-prompted) |
| D7a flags | Rule-based pre-registered scoring outputs |
| D7b reasoning | LLM verbal rationale captured in aggregate records |
| Stage 2d expectations.md | Pre-registered claim definitions + scoring thresholds |
| D7 Stage 2d signoff | Phase-level pre-registration record |

D8.4 must **not** consult or generate:

- New LLM calls (Proposer, Critic, or otherwise)
- New Backtrader runs
- Production code (DSL, registry, scoring pipeline edits)
- Any artifact outside the list above

---

## 5. Per-Issue Output Discipline (fixed five-part structure)

Each of the six methodology issues receives its own subsection in
`docs/d8/D8_4_METHODOLOGY_REFINEMENT.md`. Every per-issue subsection
must contain **exactly** the following five parts in the order
specified, each with its own header. Part 3 is split into two
mandatory subfields (3a / 3b) per ChatGPT Round 1; both subfields
must be present.

| Part | Header | Content |
|---|---|---|
| 1 | **Diagnosis** | What is broken or under-specified, anchored to specific D8.1 cells / D8.2 verdicts / D8.3 rows / aggregate-JSON fields. Cite numeric values and artifact locations. |
| 2 | **Root cause** | Why the methodology produces the diagnosed behavior. Distinguish definitional gaps, calibration gaps, prompt-design gaps, and documentation gaps. |
| 3a | **Proposed revision spec** | Exact methodology change proposed. Must be specific enough that a downstream implementation phase could apply it without further interpretation. |
| 3b | **Expected behavior change** | What the revision is *intended* to change in future fires. Must be phrased as expected behavior, never as validated result. |
| 4 | **Validation plan** | What evidence in a future phase would validate the proposed revision. Must distinguish necessary from sufficient conditions, and must specify what artifact would carry the validation evidence (e.g., a re-fire aggregate, a synthetic-data sanity check, a held-out cohort comparison). |
| 5 | **Affected rows or scope-level impact** | Row-anchored issues 1 and 2 MUST cite exactly the §6.2.2 divergence_expected cohort positions {1, 2, 3, 5, 6}; cross-tab issue 5 cites cell-level evidence with no row positions; scope-level issues 3, 4, 6 cite scope structures with no row positions. Asserting row attributions on issues 3, 4, 5, or 6 is a defect. Asserting any positions outside {1, 2, 3, 5, 6} on issues 1 or 2 is a defect. Pos 138 / 143 may be cited only under issues that materially touch RSI-absent vol_regime test-retest framing, and citation must preserve the §1.2 DEFER wording. **Pos 143 fresh-7 negation MUST be restated explicitly** at every Part 5 site that mentions pos 143 or RSI-absent vol_regime twins (≥2 D8.4 sites total: §1.2 + each affected Part 5). **Pos 3 double-duty status MUST be restated explicitly** at every Part 5 site under issues 1 or 2 that mentions pos 3 (≥2 D8.4 sites total: §1.2 + each affected Part 5). |
| 6 | **Issue interaction check** | Upstream dependencies on other D8.4 issues; downstream effects on other D8.4 issues; possible conflicts with other proposed revisions. Required to prevent six isolated fixes that contradict each other. |

**No part may be omitted.** A part may be marked `"none"` only with
an explicit one-sentence rationale (e.g., "no D8.3 rows affected
because this issue is documentation-only"). The header itself is
mandatory.

### 5.1 `proposal_confidence` field

Each per-issue subsection carries a `proposal_confidence` label of
`low` / `medium` / `high`, declared at the top of the subsection.

**Strict semantics.** `proposal_confidence` reflects confidence that
the proposed revision (Part 3a) follows from D8 evidence (Parts 1–2).
It is **not validation evidence** and MUST NOT be described as proof
that the fix works. A `high` label means the diagnosis-to-spec chain
is internally coherent; it does not mean the fix has been tested.

**No downstream citation as evidence.** No D8.4.x sub-phase, no
synthesis section, no forward pointer, and no future phase
consuming D8.4 outputs may cite `proposal_confidence` as if it were
empirical evidence that a revision works. The label is an internal
coherence signal only; downstream artifacts that want to cite D8.4
for validation purposes must cite Part 4 (validation plan) and the
sealed D8 evidence anchors directly, never the confidence label.
Phrasing such as "high-confidence fix" or "validated by
proposal_confidence=high" is forbidden in any document that
consumes D8.4.

**Forbidden language in any of the five parts** (inherited from D8.3
§5): "gut feel", "seems", "looks like", "probably", "generally
speaking". Required: specific artifact citations, position numbers,
numeric values where applicable, and explicit references to D8.1
cells / D8.2 sections / D8.3 rows / aggregate JSON paths.

**Forbidden language specific to Part 3b (expected behavior change).**
Part 3b describes intended behavior under the revision. The
following phrasings are forbidden because they recast intention as
demonstrated outcome:
- "this change will reduce false falsifications"
- "this fix eliminates the calibration shortfall"
- "the revision corrects the divergence misspecification"
- any past-tense construction implying the revision has already
  produced an effect (e.g., "improved", "fixed", "resolved")
- any claim quantifying the magnitude of the behavior change
  without a paired Part 4 validation reference

Required Part 3b phrasing pattern: "is intended to ...", "expected
to ...", "the revision targets ...". The intention/outcome
distinction must be linguistically explicit, not implied.

**Forbidden conflations** (D8.4-specific):
- Conflating Part 3a / 3b (proposed revision + expected behavior)
  with Part 4 (validation evidence) — a proposal is not validation.
- Conflating Part 3a (spec) with Part 3b (expected change) — the
  spec is what changes; the expected change is what behavior the
  spec is intended to produce.
- Conflating "this would fix it" with "we have shown it fixes it" —
  D8.4 has shown nothing in this sense; only proposed.
- Treating a pattern observed in already-sealed evidence as
  validating a fix that targets that same evidence — circular.

---

## 6. Authoring Discipline

### 6.1 Anchor citations

Every numeric or claim-level statement must cite either a sealed
artifact location (e.g., `D8.2 §6.2.2`, `D8.1 cell 12`, `D8.3 row 1`,
`stage2d_aggregate_record.json per_call_records[k]`) or a sealed
scope-lock anchor (e.g., `D8.3.0 §3.4`). Uncited numeric statements
are not permitted.

### 6.2 Spot-check discipline

- **100% of per-issue subsections** are spot-checked by triangulated
  review (Claude advisor + ChatGPT critic) during D8.4.x Round 1 or
  Round 2 review.
- **100% of forward-pointer items** in synthesis are spot-checked
  for scope-discipline (each pointer must name the receiving phase
  and must not commit a future phase's scope).

### 6.3 Hard rule inheritance

- **D8.3 hard rule 5** (no reinterpretation of pre-registered claims)
  extends into D8.4 unchanged.
- **"No silent re-scoring"** (D8.3.0 §4.2) extends into D8.4
  unchanged.
- **D8.3.0 §11 sealing conditions** for the D8.3 master triage table
  remain in force throughout D8.4 — no D8.3 row is edited by D8.4.

### 6.4 Pre-authoring SHA gate

Every D8.4.x authoring turn re-verifies the seven anchor SHAs in
§2.2 before any edit. SHA drift halts authoring until investigated
and explicitly reconciled.

---

## 7. Output Artifact Structure

D8.4 produces `docs/d8/D8_4_METHODOLOGY_REFINEMENT.md` with the
following sections:

### 7.1 Skeleton (D8.4.1)
- Document title + scope-lock pointer
- §1 Purpose (consumes D8.3 §4.3 issue list)
- §2 Inputs (anchors mirrored from this scope lock §2)
- §3 Methodology-issue inventory (binding restatement of D8.3 §4.3
  with a one-line per-issue summary)
- Placeholder per-issue subsection headers (six)
- Placeholder synthesis + forward pointers + closeout sections

### 7.2 Per-issue methodology analysis (D8.4.2 – D8.4.7)
Six subsections, one per issue, each populating the fixed five-part
structure (§5). Authoring order matches the D8.3 §4.3 enumeration
unless ratified otherwise.

### 7.3 Synthesis (D8.4.8)
- Cross-issue themes (where multiple issues share root causes or
  remediation paths)
- **Issue-interaction matrix** — table consolidating every Part 6
  Issue interaction check across the six issues, surfacing any
  upstream/downstream conflicts that emerge only at synthesis level.
  **Recording artifact only**: the matrix records observed
  interactions among issues already authored under §5. It MUST NOT
  propose joint or cross-issue fixes (e.g., "joint revision for
  issues 1+2"); each issue's revision spec lives in its own §5
  Part 3a, not in synthesis. Newly surfaced cross-issue questions
  go to forward pointers (§7.4), not to the matrix as proposals.
- Newly surfaced (out-of-scope) methodology questions deferred to a
  future phase
- Aggregate impact on D8.3 METHOD-QUESTION rows + scope-level
  implications
- Aggregate `proposal_confidence` distribution across the six
  issues (informational, not a gating metric)

### 7.4 Forward pointers (D8.4.9)
Per-issue forward pointer specifying:
- Receiving phase (e.g., "Stage 2e implementation", "D8.3.6+
  re-triage", "documentation-only edit phase")
- Implementation owner (research vs ops vs documentation)
- Validation owner
- Explicit non-promise: D8.4 does not commit any future phase's
  scope; pointers are routing labels, not authorizations.

### 7.5 Closeout (D8.4.10)
- Full SHA log across D8.4 sub-arc commits (mirroring D8.3 Appendix D
  discipline)
- Invariant verification log (post-authoring disk-verified checks)
- D8.4 sub-arc seal entry

---

## 8. Sub-phase plan

| Sub-phase | Scope | Estimated commits |
|---|---|---|
| D8.4.0 | Scope lock (this document) | 1 |
| D8.4.1 | Skeleton + purpose + methodology-issue inventory | 1 |
| D8.4.2 | Issue 1 — Divergence-label definition audit (5-part) | 1 |
| D8.4.3 | Issue 2 — Direction-of-prediction recalibration (5-part) | 1 |
| D8.4.4 | Issue 3 — Lower-tail calibration (5-part) | 1 |
| D8.4.5 | Issue 4 — Joint-shape asymmetric-calibration (5-part) | 1 |
| D8.4.6 | Issue 5 — Forensic cross-tab methodology / prompt / labels (5-part) | 1 |
| D8.4.7 | Issue 6 — Documentation drift (5-part) | 1 |
| D8.4.8 | Synthesis | 1 |
| D8.4.9 | Forward pointers | 1 |
| D8.4.10 | Closeout (SHA log + invariants + seal) | 1 |
| **Total** | | **~10–12 commits, flexible** |

The sub-phase count is a guideline, not a hard gate. A per-issue
analysis may be split across multiple commits if the issue's
analysis grows; conversely, two adjacent low-density issues may be
consolidated into a single commit with explicit scope justification
in the commit message. Material restructuring (e.g., merging or
splitting issues) requires a successor scope-lock amendment.

Each sub-phase is ratified through Round 1 / Round 2 review before
commit, analogous to the D8.3 sub-arc discipline.

---

## 9. Acceptance criteria for D8.4

D8.4 is considered complete when **all** of the following hold:

1. `docs/d8/D8_4_METHODOLOGY_REFINEMENT.md` exists with skeleton +
   six per-issue subsections + synthesis + forward pointers +
   closeout.
2. Each of the six per-issue subsections populates the fixed
   structure (§5): Parts 1, 2, 3a, 3b, 4, 5, 6 with no missing
   parts, plus a declared `proposal_confidence` label.
3. Every numeric or claim-level statement in the document cites a
   sealed artifact location.
4. No part conflates "proposed revision" (3a/3b) with "validation
   evidence" (4) — Lock B held.
5. No methodology revision is characterized as "applied," "fixed,"
   or "validated" within D8.4 (Lock A held).
6. No `proposal_confidence` label is described as proof that a fix
   works (§5.1 strict semantics held).
7. Pos 143 fresh-7 negation preserved at every D8.4 site that
   touches pos 138 / 143 or RSI-absent vol_regime twins (§1.2).
8. Pos 3 double-duty preserved at every D8.4 site that touches
   issues 1 or 2 (§1.2).
9. No D8.0, D8.1, D8.2, or D8.3 artifact has been edited during
   D8.4 sub-arc.
10. No re-bucketing of D8.3 candidates (§3.2 expanded out-of-scope).
11. No new LLM calls logged against `agents/spend_ledger.db` during
    D8.4 sub-arc.
12. No production code changes during D8.4 sub-arc.
13. Synthesis (§7.3) explicitly enumerates any newly surfaced
    methodology questions and routes them to forward pointers, not
    to in-scope analysis.
14. Synthesis (§7.3) includes the issue-interaction matrix
    consolidating Part 6 across all six issues.
15. Forward pointers (§7.4) name a receiving phase + implementation
    owner + validation owner per issue, with explicit non-promise
    language.
16. All seven anchor SHAs in §2.2 byte-match at the final D8.4
    commit.
17. Closeout (§7.5) records the full SHA log and post-authoring
    invariant verification.
18. Six issues authored — exactly six. No fifth-issue collapse
    (e.g., merging documentation drift into another issue) and no
    seventh-issue inclusion (newly surfaced questions go to
    forward pointers, not in-scope analysis).
19. Row-attribution fidelity: row-anchored issues (1, 2) cite
    positions; scope-level issues (3, 4, 6) cite scope structures;
    cross-tab issue (5) cites cell-level evidence; no false row
    attributions on scope-level issues.

---

## 10. Sealing conditions

- **D8.4.0 scope lock immutable** upon ratification and commit.
  Future amendments require a successor sub-phase with explicit
  ratification — never silent drift inside D8.4.1–D8.4.10.
- **Per-issue section content immutable post-commit** within the
  D8.4 sub-arc. Once a per-issue subsection (any of the six) is
  committed under D8.4.2 – D8.4.7, none of its seven structural
  parts (1, 2, 3a, 3b, 4, 5, 6) may be silently revised in a later
  D8.4.x commit. Correction requires a successor sub-phase
  (D8.4.N+) with the prior content cited and the revision rationale
  anchored to artifact evidence — analogous to D8.3.0 §11
  master-table immutability post-D8.3.3, not analogous to a
  free-edit document.
- **Forward pointers are routing labels, not authorizations.** No
  forward pointer in D8.4 commits a future phase's scope; that scope
  is authorized in the future phase's own scope lock.
- **No silent edits to D8.3 artifacts.** Any D8.3 re-triage prompted
  by D8.4 outputs is an independent post-D8.4 sub-phase requiring
  its own authorization gate.
- **No silent expectations.md edits.** Documentation-drift
  remediation (issue #6) is proposed in D8.4; the actual edit
  belongs to a later authorized phase.

### 10.1 Pre-commit diff sealing check (D8.4.0)

Before the D8.4.0 commit, `git diff --cached --stat` MUST show only:

- `docs/d8/D8_4_SCOPE_LOCK.md`

No production code, notebooks, raw payloads, expectations files,
D8.1 / D8.2 / D8.3 artifacts, or prior scope locks may be staged.
This check is mandatory because D8.4 is methodology-adjacent and
accidental code/notebook drift carries higher risk than in D8.3.

### 10.2 Per-sub-phase diff sealing check (D8.4.1 – D8.4.10)

Before every D8.4.x commit, `git diff --cached --stat` MUST show
only:

- `docs/d8/D8_4_METHODOLOGY_REFINEMENT.md` (and its scope-lock
  document if updated under a successor amendment, which is
  forbidden inside D8.4 by §10 sealing conditions)

No edit to any other tracked file may be staged within a D8.4.x
commit. This rule has no exceptions inside the D8.4 sub-arc.

---

## 11. Pre-authorization context (informational)

D8.4 is authorized following:
- D8.3 sealed at commit `0b371cd` (D8.3.5 final commit, 9-commit
  sub-arc).
- ChatGPT advisor's pre-authorization round ratifying Q1–Q5 plus
  Locks A–D (this scope lock §3.3).
- Claude advisor's adjudication confirming D8.4 starts with a fresh
  scope lock (not an amendment of D8.3).
- All seven anchor SHAs (§2.2) verified byte-match against D8.3
  sealed state at scope-lock authoring time.

This scope lock is the governing document for D8.4. If any future
D8.4.x sub-phase encounters a scope question not addressed here, the
correct response is to halt and author a successor scope-lock
amendment, never to drift silently.
