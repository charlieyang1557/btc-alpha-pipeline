# D8.2 — Stage 2d Result Adjudication

**Status:** skeleton (D8.2.1.0). Substantive per-claim adjudication,
§6.6 observation findings, delta-from-D8.0 narrative, and synthesis
are authored in D8.2.1.1+. No adjudication prose in this commit.

**Scope contract:** [docs/d8/D8_2_SCOPE_LOCK.md](D8_2_SCOPE_LOCK.md)
(committed `c78ab10`).

---

## 1. Purpose and Scope

*(To be authored in D8.2.1.1.)*

D8.2 is the claim-level adjudication of Stage 2d pre-registered gates.
Per the scope lock:

- Claim-driven, not strategy-driven
- Six gate claims + §6.6 observation axes + §6 cross-tab + delta-from-D8.0
- Per-candidate triage deferred to D8.3; methodology fixes deferred to D8.4
- D8.0 stands as historical snapshot; D8.2 is the controlling
  adjudication going forward

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

*(To be authored in D8.2.1.1.)*

Brief summary of the D8.1 sub-arc's notebook-driven gate adjudication:
inputs, cell-level decomposition, integrity-check discipline, and the
scope in which verdicts were computed. No new analysis here; this
section is narrative scaffolding for the per-claim rows in §6.

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
