# D8.2.0 — Stage 2d Result Adjudication Scope Lock

**Status:** scope lock for the D8.2 claim-level adjudication sub-arc.
**Author turn:** D8.2.0 pre-authoring commit.
**Supersedes:** nothing (new artifact).
**Is superseded by:** nothing (immutable once sealed).

---

## 1. Purpose

D8.2 produces a single markdown artifact,
`docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md`, that takes D8.1's gate
verdicts and §6.6 observation readouts and assigns each Stage 2d
pre-registered claim a **primary verdict** (literal adjudication)
paired with an **interpretation tag** (analyst narrative). The
adjudication document is claim-driven: per-strategy triage is
deferred to D8.3 and methodology-reform work is deferred to D8.4.

This scope lock fixes the adjudication taxonomy, inputs, and
boundaries so that D8.2.1+ authoring proceeds on stable footing.
Once committed, this scope lock is immutable; scope changes require
a new D8.2.0 amendment turn with explicit ratification.

---

## 2. Inputs

All inputs are referenced by commit SHA or file hash so that D8.2
adjudications remain reproducible.

### 2.1 Git-committed anchors

| Anchor | Commit | Description |
|---|---|---|
| D8.1 notebook final | `ac2586b` | `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` |
| D8.0 phase signoff | `f28e2d2` | `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` |
| D8.1 sub-arc commits | `3c19945` → `2f283c4` → `5d2bb72` → `606e451` → `2f455fb` → `ac2586b` | six commits, skeleton through synthesis |

### 2.2 File SHA anchors

| File | SHA-256 |
|---|---|
| `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` | `09eeda3278c96ccf7b945c5edc9dde9bcfa51ca35138a63d36258514be5c323f` |
| `docs/d7_stage2d/stage2d_expectations.md` | `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5` |
| `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` | `20f58ed830cdafc35c01d59904568d8cd15be0f6bf47985de251527fcdbc6d60` |
| `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` | `1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998` |

D8.2.1+ authoring MUST re-verify these SHAs at the top of the
adjudication document. If any drift, stop and reconcile before
adjudication begins.

**Notebook SHA volatility:** the D8.1 notebook is committed
without outputs, but local inspection runs (e.g., re-executing via
nbclient for forensic review) rewrite execution metadata and change
the file SHA without changing analytical content. The **canonical
anchor for the D8.1 notebook is commit ref `ac2586b`**; the SHA in
§2.2 is supplementary. If at D8.2.1 authoring time the notebook
SHA differs but commit ref still resolves to `ac2586b` with the
expected tree, treat the SHA drift as metadata-only and proceed
after `git checkout` restores committed state. SHA drift on
committed-binary anchors (aggregate JSON, expectations.md, signoff
doc) is NOT metadata-only and must halt authoring for reconciliation.

---

## 3. Verdict Taxonomy

Every Stage 2d pre-registered gate claim receives **two fields**:

### 3.1 `primary_verdict` (mutually exclusive, one of six)

| Verdict | Operational definition |
|---|---|
| `PASS` | Observed numerator satisfies pre-registered threshold. |
| `FAIL` | Numeric threshold not met, but the underlying directional hypothesis is not necessarily contradicted. The observation is a magnitude/calibration shortfall in the predicted direction. |
| `FALSIFIED` | Numeric threshold not met AND the observed result materially contradicts the directional hypothesis or mechanism the claim was meant to test (e.g., divergence_expected predicted ≥4 high-SVR; observed 4 of 5 low-SVR, inverting the predicted direction). FALSIFIED is a strict subset of "threshold not met" cases that also carry mechanism-inversion evidence. |
| `PARTIAL` | Observed satisfies on one sub-cohort but not another, where the pre-registered phrasing admits sub-cohort decomposition. Rare in Stage 2d. |
| `INCONCLUSIVE` | Sample size or methodology constraint prevents a determinate verdict on the literal threshold. Reserved for gate claims that cannot be decided from the committed data. Not a fallback for ambiguous adjudications. |
| `NOT_TESTABLE` | The pre-registered phrasing does not produce a gate test on the observed data. Used for (a) claims that cannot be mapped to captured metrics, and (b) §6.6 readout-only axes which are recorded but not pre-registered as gates (see §3.4). |

Primary verdict is **mechanical**. It is derived from observed numerator
vs. pre-registered threshold using the pre-registration's phrasing.
Primary verdict is never modified to reflect analyst interpretation.

### 3.2 `interpretation_tag` (free-form short tag, one tag per claim)

A short hyphenated string capturing the analyst's narrative context
for why the primary verdict landed where it did. Examples:

| Tag | Meaning |
|---|---|
| `direction_inversion_signal` | Observed data runs opposite to predicted direction. |
| `likely_directional_model_misspecification` | Direction inversion is the most plausible mechanism. |
| `sample_size_limited` | Low n undermines the gate's discriminating power. |
| `calibration_shortfall` | Observation is directionally correct but magnitude is short. |
| `clean_pass` | No interpretive caveat; observation clearly satisfies threshold. |
| `anchor_reproduced` | Observation matches a Stage 2b/2c anchor (continuity signal). |

The tag is advisory narrative. It does not modify `primary_verdict`.

### 3.3 `methodology_followup` (optional pointer)

When a claim's interpretation implicates a prompt-template, direction-of-
prediction, cost-field, or similar methodology concern, the entry
includes a `methodology_followup: D8.4` pointer. D8.2 does NOT author
the fix; it records the pointer.

### 3.4 §6.6 observation axes

§6.6 observation axes (alignment distribution, SVR-alignment decoupling,
theme×label contingency, neutral-stratum SVR readout, §6 theme×label×SVR
cross-tab) are **recorded as observations, not gates**. They receive:

- `primary_verdict = NOT_TESTABLE` (§6.6 is not pre-registered as a gate,
  so PASS/FAIL/FALSIFIED would be category errors)
- `interpretation_tag = observation_only` (or a more specific narrative
  tag per §3.2 semantics)
- Optional `methodology_followup`

This keeps the `primary_verdict` enum closed at six mutually exclusive
classes and honors the pre-registration framing that §6.6 is "recorded,
not pre-registered." NOT_TESTABLE for §6.6 is structurally tied to the
non-gate character of those axes; it is NOT a fallback for ambiguous
gate adjudications (ambiguous gates use INCONCLUSIVE per §3.1).

Observations supply evidence for claim-level adjudications in §3 but
are not themselves claim verdicts.

---

## 4. Scope Boundaries

### 4.1 In scope for D8.2

- Literal adjudication of the five individually-gated claims: §6.2.1,
  §6.2.2, §6.3(a), §6.3(b), §6.4
- Derived adjudication of the §6.3 joint verdict (PASS iff both (a)
  and (b) pass, per expectations.md §6.3 operational definition at L110-111)
- Recording of §6.6 observation axes (alignment, SVR-alignment
  decoupling, theme×label contingency, neutral-stratum SVR median/IQR)
- Recording of the §6 forensic cross-tab (theme × UB label × SVR bucket)
- A "Delta from D8.0 signoff" section that enumerates where D8.2
  supersedes the signoff narrative (see §5 Q5 ruling)
- Forward pointers to D8.3 (strategy triage) and D8.4 (methodology fixes)

### 4.2 Out of scope for D8.2 (deferred to later sub-arcs)

- **Per-candidate §E3 / §E4 bucket adjudication** — the 20 Tier 1/2 and
  20 deep-dive position-level verdicts. Per-position references appear
  in D8.2 only as supporting evidence (see §5 Q2 ruling); full
  per-candidate disposition is **D8.3 strategy triage**.
- **Strategy Tier A/B/C/D triage** — which of the 197 scored strategies
  warrant backtesting. **D8.3.**
- **Methodology reforms** — forbidden-language refinement, cost-field
  semantics, direction-of-prediction recalibration, prompt template
  changes. D8.2 records `methodology_followup: D8.4` pointers only;
  the fixes themselves are **D8.4**.
- **Amendment of D8.0 signoff** — D8.0 is a historical snapshot (see
  §5 Q5 ruling). D8.2 supersedes narratively but does not modify
  `f28e2d2`.
- **New statistical tests** — no Wilson CI, binomial p-value, or
  hypothesis-test framing beyond what D8.1 already computed. D8.2
  synthesizes D8.1 outputs; it does not run new tests.

---

## 5. Rulings on Q1–Q5

### Q1 — Verdict taxonomy

**Ruling:** two-field taxonomy per §3. `primary_verdict` is mechanical
and mutually exclusive across six classes; `interpretation_tag` is
free-form narrative. The two never collapse into one field.

**Why:** Hard rule 5 (no reinterpretation of pre-registered claims)
is honored when the literal verdict is kept separate from narrative.
Future readers can filter by `primary_verdict` for hard adjudication
or read `interpretation_tag` for context.

### Q2 — §E3 / §E4 per-candidate scope

**Ruling:** Per-candidate §E3 / §E4 bucket adjudication is **out of
scope for D8.2**. D8.2 references specific positions only as supporting
evidence for a claim-level finding (e.g., "pos 102 confirms the Stage
2c decouple anchor for §6.6(2) type A"). Full per-position disposition
is D8.3.

**Why:** D8.2 is claim-driven; D8.3 is strategy-driven. Mixing the two
produces messy documents that serve neither audience.

### Q3 — D8.0 signoff alignment

**Ruling:** D8.2 stands independently. A "Delta from D8.0 signoff"
section enumerates where D8.2 supersedes signoff narrative; D8.0 is
NOT amended unless a factual error is identified in committed signoff
text. For incompleteness (e.g., §6.3(b) FAIL not surfaced in signoff),
D8.2 supersedes narratively without modifying `f28e2d2`.

**Why:** Documentation snapshots represent the state of knowledge at
their commit time. Back-editing snapshots when new analysis surfaces
additional findings would destroy the audit trail that makes the
per-section commit discipline valuable.

### Q4 — §6.2.2 direction inversion

**Ruling:**
- `primary_verdict = FALSIFIED` (per §3.1: threshold not met AND
  observation materially contradicts the directional hypothesis —
  4 of 5 divergence positions landed at low SVR rather than high SVR,
  inverting the predicted direction).
- `interpretation_tag = likely_directional_model_misspecification`
- `methodology_followup = D8.4`

**Why:** The FAIL vs FALSIFIED distinction carries real information
about what Stage 2d teaches. §6.2.2 did not merely fall short of a
threshold; the critic's actual scoring pattern suggests the
divergence_expected label was predicting the wrong direction —
a mechanism-inversion signal. §6.3(b), by contrast, is a magnitude
shortfall in the predicted direction (26 observed vs 30 predicted
at SVR≤0.30; direction is correct, count is short) and is classified
FAIL (not FALSIFIED) per §3.1.

### Q5 — §6.3(b) new FAIL vs D8.0

**Ruling:** D8.0 is NOT amended. D8.2 states explicitly:
"D8.0 signoff did not surface §6.3(b) as a primary falsification; D8.1
revealed it. D8.2 is the controlling claim-level adjudication."

**Why:** Same rationale as Q3. Signoff was the snapshot at its commit
time; D8.1's notebook-driven gate adjudication surfaced findings the
signoff did not. D8.2 becomes the controlling adjudication going
forward; D8.0 remains the historical record.

---

## 6. Output Artifact

- **Path:** `docs/d8/D8_STAGE2D_RESULT_ADJUDICATION.md`
- **Format:** markdown
- **Estimated length:** 300–500 lines
- **Authoring sequence:** D8.2.1+ sub-phases per D8.2.1 ratification turn

Suggested internal structure (non-binding, ratified at D8.2.1 start):

1. Purpose + scope (refers to this scope lock)
2. Anchored SHAs (re-verified at authoring time)
3. Methodology recap (D8.1 sub-arc summary)
4. Per-claim adjudication: §6.2.1, §6.2.2, §6.3(a), §6.3(b), §6.3 joint,
   §6.4 — each with `primary_verdict`, `interpretation_tag`, evidence
   references, optional `methodology_followup`
5. §6.6 observation findings (5 axes including cross-tab)
6. Delta from D8.0 signoff
7. Synthesis: what does Stage 2d teach?
8. Forward pointers to D8.3 / D8.4
9. Appendices: SHA table, evidence index, D8.1 cell index

---

## 7. Acceptance Criteria for D8.2

The adjudication document is ready for sealing when:

- [ ] All 6 pre-registered gate claims have `primary_verdict` +
      `interpretation_tag` entries (§6.2.1, §6.2.2, §6.3(a), §6.3(b),
      §6.3 joint, §6.4)
- [ ] All 5 §6.6 observation axes have findings recorded with
      `primary_verdict = NOT_TESTABLE` + `interpretation_tag`
      (default tag: `observation_only`; more specific narrative tags
      permitted)
- [ ] "Delta from D8.0 signoff" section enumerates supersession points
      and confirms no factual errors in signoff (otherwise flag)
- [ ] No per-candidate Tier 1/2 / deep-dive triage entries (deferred to
      D8.3)
- [ ] No methodology fix proposals (deferred to D8.4; `methodology_followup`
      pointers only)
- [ ] All §2 SHA anchors re-verified at D8.2.1 authoring time against
      disk. Required matches:
      - `docs/test_notebooks/D8_1_stage2d_aggregate_result_analysis.ipynb` at commit `ac2586b` (SHA `20f58ed8...bc6d60` supplementary; metadata-only drift per §2 acceptable after `git checkout`)
      - `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/stage2d_aggregate_record.json` SHA `09eeda32...5c323f` (must match byte-for-byte)
      - `docs/d7_stage2d/stage2d_expectations.md` SHA `98b87a70...7010a5` (must match byte-for-byte)
      - `docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md` SHA `1fb1161c...5998` (must match byte-for-byte)
      If any non-metadata drift detected: halt D8.2.1 authoring, surface
      immediately, re-anchor via scope lock amendment turn before resuming.
- [ ] No new statistical tests beyond D8.1's committed outputs
- [ ] Round 1 review + Round 2 ratification discipline held (same
      pre-commit pattern as D8.1 sub-arc)

---

## 8. Sealing Conditions

This scope lock is sealed when committed. Once sealed, changes require:

1. A new D8.2.0 amendment turn (fresh scope-lock amendment document, or
   explicit amendment commit to this file)
2. Explicit ratification from Charlie (not self-approval by reviewer)
3. Commit message referencing the amendment rationale

The scope lock is **advisory binding** on D8.2.1+ authoring: any
deviation from the rulings in §5 requires surfacing the disagreement
before authoring the deviation, not post-hoc rationalization.
