# D8.2 — Stage 2d Result Adjudication

**Status:** skeleton (D8.2.1.0). Substantive per-claim adjudication,
§6.6 observation findings, delta-from-D8.0 narrative, and synthesis
are authored in D8.2.1.1+. No adjudication prose in this commit.

**Scope contract:** [docs/d8/D8_2_SCOPE_LOCK.md](D8_2_SCOPE_LOCK.md)
(committed `c78ab10`).

---

## 1. Purpose and Scope

D8.2 is the **claim-level adjudication** of Stage 2d pre-registered
expectations. D8.1 produced the mechanical evidence (gate numerators,
observation readouts) in a 28-cell notebook across six per-section
commits; D8.2 converts that evidence into scientific claim verdicts
using the two-field taxonomy (`primary_verdict` +
`interpretation_tag`) locked in the scope contract.

**Governing constitution.** The binding scope contract for this
document is `docs/d8/D8_2_SCOPE_LOCK.md` at commit `c78ab10`. Where
§3 below summarizes the verdict taxonomy for reader convenience, the
scope lock text is authoritative; any conflict is resolved in favor
of the scope lock per its §8 sealing conditions.

**Scope boundary.** D8.2 is claim-driven, not strategy-driven and not
methodology-driven:

- Claim-driven — six gate adjudications (five individual gates plus
  the §6.3 derived joint) and five §6.6 non-gate observation axes
  (including the §6 forensic cross-tab recorded at §6.1 Lock +
  expectations.md)
- **Out of scope:** per-candidate §E3 / §E4 bucket adjudication and
  strategy-level Tier A/B/C/D triage — deferred to **D8.3**
- **Out of scope:** methodology reform (prompt-template refinement,
  cost-field semantics, direction-of-prediction recalibration) —
  deferred to **D8.4**. D8.2 emits `methodology_followup: D8.4`
  pointers only; it does not author the fixes.
- **Out of scope:** amendment of the D8.0 phase signoff at commit
  `f28e2d2`. D8.0 is a historical snapshot; D8.2 is the controlling
  claim-level adjudication going forward. Supersession is narrative,
  not textual — see §8 delta.

**Reader navigation.** §6 contains the six gate adjudications; §7
contains the five §6.6 observation findings; §8 enumerates where
D8.2 supersedes the D8.0 signoff narrative; §9 synthesizes what
Stage 2d teaches at the claim level; §10 hands off to D8.3 / D8.4.

**Durability.** D8.2 is the controlling claim-level adjudication for
Stage 2d. Amendment of D8.2 requires the same ratification cycle
used for the scope lock: explicit Charlie sign-off plus a new
commit referencing the amendment rationale.

---

## 2. Anchored Inputs

All inputs re-verified at D8.2.1.0 preflight. Anchors MUST match at any
D8.2.1.* authoring turn; drift rules per scope lock §7.

| Anchor | Type | Identifier | Verification |
|---|---|---|---|
| D8.1 notebook | commit ref (canonical) | `ac2586b` | re-verify at authoring |
| D8.1 notebook | file SHA (supplementary, metadata-tolerant) | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` | metadata-only drift tolerated per §2 of scope lock |
| D8.0 signoff | file SHA (byte-match required) | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` | `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` |
| Aggregate record | file SHA (byte-match required) | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` | `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` |
| Expectations | file SHA (byte-match required) | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` | `docs/d7_stage2d/stage2d_expectations.md` |
| Scope lock | commit ref (immutable) | `c78ab10` | `docs/d8/D8_2_SCOPE_LOCK.md` |

**Preflight verification (D8.2.1.0):** all four byte-match anchors
confirmed at HEAD `c78ab10`; notebook SHA byte-matched (no metadata
drift at this point).

---

## 3. Verdict Taxonomy (Scope Lock §3 — summary)

Reproduced here for reader convenience. Binding text is the scope lock.

**`primary_verdict`** — mutually exclusive, six classes:

- `PASS` — observed numerator satisfies threshold
- `FAIL` — threshold not met, magnitude/calibration shortfall, no
  directional contradiction
- `FALSIFIED` — threshold not met AND observed materially contradicts
  the directional hypothesis
- `PARTIAL` — one sub-cohort satisfies, another does not (rare)
- `INCONCLUSIVE` — sample/methodology prevents determinate verdict
  (not a fallback for ambiguity)
- `NOT_TESTABLE` — claim not mappable to observed data, OR §6.6
  readout-only axis (non-gate)

**`interpretation_tag`** — free-form advisory narrative. Does NOT
modify primary_verdict.

**`methodology_followup`** — optional `D8.4` pointer when a claim
implicates methodology reform.

§6.6 axes: `primary_verdict = NOT_TESTABLE`, default
`interpretation_tag = observation_only`.

---

## 4. Claim Inventory

The eleven adjudication rows authored in D8.2.1.2–D8.2.1.3. Verdicts
are placeholders in the skeleton (`TBD`); D8.2.1.2 fills gate rows
with values consistent with D8.1's committed outputs, and D8.2.1.3
fills §6.6 rows.

| # | Claim | Section owner | primary_verdict | interpretation_tag | methodology_followup |
|---|---|---|---|---|---|
| 1 | §6.2.1 agreement | D8.2.1.2 | TBD | TBD | TBD |
| 2 | §6.2.2 divergence | D8.2.1.2 | TBD | TBD | TBD |
| 3 | §6.3(a) upper tail | D8.2.1.2 | TBD | TBD | TBD |
| 4 | §6.3(b) lower tail | D8.2.1.2 | TBD | TBD | TBD |
| 5 | §6.3 joint (derived) | D8.2.1.2 | TBD | TBD | TBD |
| 6 | §6.4 fresh-7 | D8.2.1.2 | TBD | TBD | TBD |
| 7 | §6.6 alignment distribution | D8.2.1.3 | TBD | TBD | TBD |
| 8 | §6.6 SVR-alignment decoupling | D8.2.1.3 | TBD | TBD | TBD |
| 9 | §6.6 theme × UB label contingency | D8.2.1.3 | TBD | TBD | TBD |
| 10 | §6.6 neutral-stratum SVR readout | D8.2.1.3 | TBD | TBD | TBD |
| 11 | §6 theme × label × SVR cross-tab | D8.2.1.3 | TBD | TBD | TBD |

---

## 5. Methodology Recap

D8.2's gate verdicts derive from D8.1's computed evidence. This
section records the methodology by which that evidence was produced
so §6 adjudications can be read with full provenance. No new
analysis is performed here; claim verdicts remain D8.1's mechanical
outputs, adjudicated under the scope lock taxonomy.

**D8.1 sub-arc structure.** Six per-section commits authored a
28-cell Jupyter notebook at
`docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb`:

- `3c19945` D8.1.2 — skeleton + integrity harness
- `2f283c4` D8.1.3 — §§0–1 (inputs, schema, denominator derivation)
- `5d2bb72` D8.1.4 — §6.2 agreement/divergence + §6.3 tail gates
  (cells 09, 10, 12, 13)
- `606e451` D8.1.5 — §6.4 fresh-7 gate (cells 15, 16)
- `2f455fb` D8.1.6 — §6.6 observation readouts (cells 18–21)
- `ac2586b` D8.1.7 — §6 forensic cross-tab + §7 synthesis (cells 23,
  25, 26, 27); D8.1 sub-arc closed

Every commit ran ~10 integrity checks (denominator invariants,
per-call SVR parity, bucket closure, summary consistency); the
notebook is stored restored-without-outputs per Phase 2B convention.

**Denominator discipline.** Three denominator populations recur
throughout D8.1 and are carried into §6 without re-derivation:

- **200 source positions** — the full Stage 2d source universe,
  every candidate position pre-registered in
  `stage2d_expectations.md` regardless of scoring outcome, including
  position 116
- **199-call UB cohort denominator** — the 200 source positions
  minus position 116 (skipped-source exclusion per §6.1 Lock; pos
  116 uses the 17-key `position` shape rather than the 18-key
  `candidate_position` shape carried by the other 199)
- **197 scored universe denominator** — the 199 UB cohort minus
  positions 42 and 87, which returned `d7b_error` without SVR. These
  two error records remain counted in the 199 UB denominator and
  contribute zero to any SVR-indexed numerator; they are excluded
  only from SVR-indexed cross-tabs (e.g., the §6 theme × label × SVR
  forensic cross-tab at cell 23 uses the 197 scored universe)

No-imputation rule — D8.1 never fills an absent SVR and never
substitutes a per-call score for a missing aggregate; missing values
flow through as structural zeros in gate numerators. §6 adjudications
inherit this discipline without exception.

**Gate outputs and observation axes.** D8.1 emitted six gate
adjudications (five individual plus the §6.3 derived joint) and five
§6.6 observation axes (alignment distribution, SVR–alignment
decoupling, theme × UB label contingency, neutral-stratum SVR
readout, and the §6 theme × label × SVR forensic cross-tab). Each
row in §4's claim inventory maps to one D8.1 cell output, cited by
cell index in the §6 / §7 evidence fields.

**Taxonomy application in §6.** Per the scope lock, each gate row
in §6 is stamped with a `primary_verdict` from the closed six-class
enum (`PASS` / `FAIL` / `FALSIFIED` / `PARTIAL` / `INCONCLUSIVE` /
`NOT_TESTABLE`) and an advisory `interpretation_tag`. Observation
axes in §7 receive `primary_verdict = NOT_TESTABLE` because §6.6 is
not pre-registered as a gate; the NOT_TESTABLE assignment there is
structural, not a fallback. Ambiguous gate adjudications — none are
expected in D8.2 given D8.1's clean integrity-check run — would use
`INCONCLUSIVE` with explicit rationale, never NOT_TESTABLE.

**D8.0 delta policy.** D8.2 supersedes the D8.0 phase signoff
narrative where D8.1 surfaced claim-level findings that the signoff
did not record (notably §6.3(b) lower-tail FAIL). Per scope lock
Q3 / Q5 rulings, D8.2 does not amend D8.0 at commit `f28e2d2`; it
stands independently and records the supersession points explicitly
in §8. Hard rule 5 (no reinterpretation of pre-registered claims)
binds both documents: D8.2's job is adjudication, not
pre-registration rewrite.

---

## 6. Per-Claim Adjudication — Pre-Registered Gates

*(To be authored in D8.2.1.2.)*

One subsection per gate row from §4 (rows 1–6). Each subsection:

- **Claim text** (verbatim from `stage2d_expectations.md`)
- **Threshold** (pre-registered)
- **Observed** (from D8.1 cell output)
- **`primary_verdict`** (per §3.1 taxonomy)
- **`interpretation_tag`**
- **Evidence** (D8.1 cell references; no new computation)
- **`methodology_followup`** (if applicable)

§6.3 joint is derived from §6.3(a) and §6.3(b); subsection makes the
derivation explicit.

---

## 7. §6.6 Observation Findings

*(To be authored in D8.2.1.3.)*

One subsection per §6.6 axis (§4 rows 7–11). Each subsection:

- **Axis description**
- **Observed summary** (D8.1 cell output reference)
- **`primary_verdict = NOT_TESTABLE`** (structural, non-gate)
- **`interpretation_tag`** (default `observation_only`; more specific
  narrative tags permitted)
- **Evidence role** — how the observation supports or qualifies a
  §6 gate adjudication

---

## 8. Delta from D8.0 Signoff

*(To be authored in D8.2.1.4.)*

Enumeration of where D8.2's claim-level adjudications supersede or
extend the D8.0 phase signoff narrative. Per scope lock Q3/Q5 rulings:
D8.0 is not amended; D8.2 is controlling going forward.

Expected itemization:

- §6.3(b) lower-tail FAIL — not surfaced in D8.0 signoff; D8.1 revealed
- §6.2.2 divergence FALSIFIED — D8.2 sharpens D8.0's narrative using
  the FAIL-vs-FALSIFIED distinction locked in scope lock §3.1
- Any other supersession points identified during D8.2.1.2 authoring

---

## 9. Synthesis — What Does Stage 2d Teach?

*(To be authored in D8.2.1.5.)*

Claim-level synthesis. What Stage 2d validates, what it falsifies,
where calibration shortfalls sit, and how the §6.6 observations qualify
gate verdicts. No strategy triage; no methodology prescriptions.

---

## 10. Forward Pointers

*(To be authored in D8.2.1.5.)*

- **D8.3** — strategy triage (per-candidate §E3/§E4 adjudication,
  Tier A/B/C/D assignment)
- **D8.4** — methodology fixes (prompt template, forbidden-language
  refinement, cost-field semantics, direction-of-prediction recalibration
  — scoped by `methodology_followup` pointers emitted in §6)

---

## Appendices

*(To be authored in D8.2.1.5.)*

- A. SHA verification log (anchors at authoring time)
- B. D8.1 cell index (cell → claim row mapping)
- C. Evidence references (per-claim citation table)
