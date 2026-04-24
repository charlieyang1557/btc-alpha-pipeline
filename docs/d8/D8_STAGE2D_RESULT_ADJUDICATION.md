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

Six adjudication entries, one per gate row in §4: §6.2.1, §6.2.2,
§6.3(a), §6.3(b), §6.3 joint, §6.4. Each entry carries the verbatim
pre-registered claim (anchored to expectations.md SHA
`98b87a70...010a5`), the observed result (anchored to aggregate SHA
`09eeda32...c323f` via the cited D8.1 cell), the three-field
adjudication (`primary_verdict`, `interpretation_tag`, optional
`methodology_followup`), an evidence narrative, and — where the
verdict is non-PASS or the mechanism is analytically delicate —
material findings that attach interpretive context without
re-deriving the gate or reinterpreting the claim (Hard rule 5).

Counts are direct; no Wilson CI, binomial p-value, or new
statistical test is introduced (scope lock §4.2 out-of-scope).

### §6.2.1 — Agreement axis gate

**Pre-registered claim** (expectations.md §6.2.1, L73):

> Of the 66 UB agreement-labelled calls, **≥ 52 have SVR ≥ 0.5**.

**Operational definition** (expectations.md):

> `count(call.svr >= 0.5) over {call.universe_b_label == "agreement_expected"} >= 52`

**Observed result** (D8.1 cell 09):

| Quantity | Value |
|---|---|
| Pre-registered denominator | 66 (UB agreement_expected cohort) |
| Pre-registered threshold | count(SVR ≥ 0.5) ≥ 52 |
| Scored subset (no errors) | 64 of 66 (pos 42, pos 87 errored — `critic_status == 'd7b_error'`) |
| Observed numerator | 64 |
| Observed ratio | 64 / 66 |
| Headroom vs threshold | +12 |

All 64 ok-scored agreement positions have SVR ≥ 0.75; the lowest
observed SVR in the cohort is 0.75 (pos 65, 75, 119, 132, 156). No
agreement position fell into the [0.5, 0.75) band or below 0.5.
The two errored positions count in the 66 denominator and contribute
zero to the numerator by pre-registered rule (they are errors, not
successes).

**Adjudication**:

| Field | Value |
|---|---|
| `primary_verdict` | `PASS` |
| `interpretation_tag` | `clean_pass` |
| `methodology_followup` | n/a |

**Evidence narrative.** The gate asks whether the model accepts its
own theme-aligned candidates at confidence ≥ 0.5. The observation
(64/66, +12 headroom) passes literally. The headroom is insensitive
to counterfactual treatment of the two errored positions: under zero-
numerator attribution (the pre-registered rule) the count is 64;
under hypothetical maximum-numerator attribution the count is 66;
both exceed 52. The cohort's SVR distribution is also concentrated
— every ok-scored position sits at SVR ≥ 0.75 — so the verdict is
not near any threshold boundary.

**Material findings.**

1. *Headroom is concentrated, not scattered.* All 64 ok pass
   positions sit at SVR ≥ 0.75; none fall in the [0.5, 0.75) band.
   The PASS is not at risk of flipping on modest noise in the SVR
   estimates.

2. *Errored-position treatment is pre-registered, not interpreted.*
   Pos 42 and pos 87 failed with `critic_status == 'd7b_error'`
   (content-level errors) and are counted in the 66 denominator with
   zero numerator contribution per scope lock convention. Even
   treating both as successes (a counterfactual the pre-registration
   does not license) would not change the verdict.

3. *Scope discipline.* No `methodology_followup` emitted. The
   literal pre-registration is fully satisfied, and D8.2 records no
   interpretive caveat that would justify forwarding to D8.3 or D8.4.

---

### §6.2.2 — Divergence axis gate

**Pre-registered claim** (expectations.md §6.2.2, L77):

> Of the 5 UB divergence-labelled calls, **≥ 4 contradict the
> divergence_expected label with SVR ≥ 0.5**.

**Operational definition** (expectations.md L85):

> `count(call.svr >= 0.5) over {call.universe_b_label == "divergence_expected"} >= 4`

**Observed result** (D8.1 cell 10):

| Quantity | Value |
|---|---|
| Pre-registered denominator | 5 (UB divergence_expected cohort) |
| Pre-registered threshold | count(SVR ≥ 0.5) ≥ 4 |
| Scored subset (no errors) | 5 of 5 |
| Observed numerator | 1 |
| Observed ratio | 1 / 5 |
| Shortfall vs threshold | −3 |

Per-call SVRs, by `candidate_position` (D8.1 cell 10):
pos 1 → 0.00, pos 2 → 0.15, pos 3 → 0.15, pos 5 → 0.15,
pos 6 → 0.75. One of five at SVR ≥ 0.5 (pos 6); four of five at
SVR ≤ 0.15.

**Adjudication**:

| Field | Value |
|---|---|
| `primary_verdict` | `FALSIFIED` |
| `interpretation_tag` | `likely_directional_model_misspecification` |
| `methodology_followup` | `D8.4` |

**Evidence narrative.** The gate's pre-registered direction is that
the divergence_expected cohort should accumulate at SVR ≥ 0.5, on
the premise that Stage 2b/2c's 6/6 high-SVR contradiction anchor
would transport to the expanded five-position UB cohort modulo
one-position slippage. D8.1 cell 10 records one of five at SVR ≥ 0.5
(pos 6 at SVR 0.75) and four of five at SVR ≤ 0.15 (pos 1 at 0.00,
pos 2/3/5 at 0.15 each). The shortfall is −3 on the numerator;
taken on its own, that is a magnitude miss. But the four sub-
threshold observations are not scattered across the SVR range — they
cluster at the extreme low tail (all at SVR ≤ 0.15), i.e., opposite
of the pre-registered direction. Per scope lock §3.1, a gate that
misses threshold AND whose observation materially contradicts the
directional hypothesis receives `primary_verdict = FALSIFIED`
(strict subset of FAIL carrying mechanism-inversion evidence). §6.3(b)
is the contrasting case: its shortfall is in the predicted direction
and is classified FAIL, not FALSIFIED.

**Material findings.**

1. *Direction inversion, not calibration shortfall.* A magnitude
   miss would present as four of five landing between 0.3 and 0.5
   (or scattered across 0.0–0.8). The observed concentration of
   four of five at SVR ≤ 0.15 is structurally different: the
   critic is not merely declining to call these contradictions at
   the pre-registered confidence, it is actively scoring them as
   near-definitive non-contradictions. The predicted direction was
   SVR ≥ 0.5 dominance; the observed direction is SVR ≤ 0.15
   dominance.

2. *§6.6 cross-reference.* The §6.6(B) SVR-alignment decoupling
   readout (D8.1 cell 19) records 15 positions with `SVR ≤ 0.25`
   and `alignment ≥ 0.75`, including four of the five §6.2.2
   divergence_expected positions: pos 1, pos 2, pos 3, and pos 5.
   This is directly relevant to the §6.2.2 falsification: the model
   does not view most divergence_expected candidates as structurally
   variant, even when their semantic theme alignment remains high.
   Full observation narrative is in §7; here the cross-reference
   only flags that the §6.2.2 FALSIFIED verdict is reinforced by an
   independent §6.6 readout.

3. *Sample-size caveat acknowledged, verdict unchanged.* The
   five-position denominator is small; a FALSIFIED verdict on a
   small cohort is ordinarily weaker evidence than on a large one.
   Two mitigating observations: (a) the four sub-threshold positions
   are tightly packed at SVR ≤ 0.15 rather than spread near the
   threshold, which reduces the probability that the verdict is
   noise-driven; (b) the pre-registered rationale explicitly
   budgeted for a one-position slippage (4/5 accepts 1 failure),
   so the observed 1/5 is three positions below the pre-registration's
   own tolerance. The verdict stands on both grounds.

4. *Scope discipline.* D8.2 records the directional contradiction
   and emits `methodology_followup: D8.4`. D8.2 does not author
   the corrective action. Candidates for D8.4 follow-up include
   direction-of-prediction recalibration, divergence-label
   definition audit, and review of how semantic alignment should
   interact with structural-variant scoring; these are enumerated
   only to justify the D8.4 pointer, and their adjudication is
   D8.4's scope, not D8.2's.

### §6.3(a) — Upper-tail distribution gate

**Pre-registered claim** (expectations.md §6.3(a), L99):

> Of all 199 UB calls, **≥ 90 have SVR ≥ 0.80 (upper tail)**.

**Operational definition**: `count(call.svr >= 0.80) over {all 199 UB calls} >= 90`

**Observed result** (D8.1 cell 12):

| Quantity | Value |
|---|---|
| Pre-registered denominator | 199 (UB calls; pos 116 skipped-source excluded per §6.1 Lock) |
| Pre-registered threshold | count(SVR ≥ 0.80) ≥ 90 |
| Scored subset (no errors) | 197 of 199 (pos 42, pos 87 errored) |
| Observed numerator | 111 |
| Observed ratio | 111 / 199 |
| Headroom vs threshold | +21 |

Composition of the 111 upper-tail positions by UB label: 57
`agreement_expected`, 54 `neutral`, 0 `divergence_expected`.

**Adjudication**:

| Field | Value |
|---|---|
| `primary_verdict` | `PASS` |
| `interpretation_tag` | `clean_pass` |
| `methodology_followup` | n/a |

**Evidence narrative.** The gate is a distribution-shape threshold:
at least 90 of 199 ok-scored positions must concentrate at SVR ≥ 0.80.
The observation (111, +21 headroom) passes literally. The two errored
positions count in the 199 denominator and contribute zero to the
numerator; under the counterfactual of max-numerator attribution the
count would be 113, still above 90, so the verdict is insensitive to
the errored-position treatment.

**Material findings.**

1. *Upper-tail composition is agreement + neutral, not divergence.*
   The 111 upper-tail positions decompose into 57 agreement_expected
   and 54 neutral, with zero divergence_expected. The agreement
   contribution is consistent with §6.2.1; the neutral contribution is
   consistent with the §6.6 neutral-stratum SVR readout (D8.1 cell 20).

2. *Upper-tail label composition, corroborating context only.* The
   upper-tail label composition is consistent with the §6.2.2
   adjudication: no divergence_expected position appears in the
   upper tail, while agreement and neutral positions dominate it.
   This is recorded as corroborating context, not as an additional
   gate.

3. *Scope discipline.* No `methodology_followup`. D8.4 calibration
   work, if any, is driven by §6.3(b), not §6.3(a).

---

### §6.3(b) — Lower-tail distribution gate

**Pre-registered claim** (expectations.md §6.3(b), L100):

> Of all 199 UB calls, **≥ 30 have SVR ≤ 0.30 (lower tail)**.

**Operational definition**: `count(call.svr <= 0.30) over {all 199 UB calls} >= 30`

**Observed result** (D8.1 cell 12):

| Quantity | Value |
|---|---|
| Pre-registered denominator | 199 |
| Pre-registered threshold | count(SVR ≤ 0.30) ≥ 30 |
| Scored subset (no errors) | 197 of 199 |
| Observed numerator | 26 |
| Observed ratio | 26 / 199 |
| Shortfall vs threshold | −4 |

Composition of the 26 lower-tail positions by UB label: 22 `neutral`,
4 `divergence_expected`, 0 `agreement_expected`.

**Adjudication**:

| Field | Value |
|---|---|
| `primary_verdict` | `FAIL` |
| `interpretation_tag` | `calibration_shortfall` |
| `methodology_followup` | `D8.4` |

**Evidence narrative.** The gate asks whether the model produces
enough low-SVR observations to populate the distribution's lower
tail. The pre-registered direction is that some subset of UB calls
should express clear structural non-agreement at SVR ≤ 0.30. The
observation (26 / 199, −4 shortfall) misses threshold by a margin
of 4. Unlike §6.2.2, the directional prediction is not inverted:
the lower tail exists and is populated (26 > 0) in the predicted
direction of the signal (low SVR on neutral and divergence_expected
positions). It is only under-populated relative to threshold. Per
scope lock §3.1, this is a calibration shortfall, not a mechanism
inversion; `primary_verdict` is `FAIL`, not `FALSIFIED`.

**Material findings.**

1. *FAIL, not FALSIFIED.* The pre-registered hypothesis is that the
   lower tail would accumulate ≥ 30 positions at SVR ≤ 0.30. The
   observation is 26, short by 4 in the predicted direction. This
   contrasts with §6.2.2, where the shortfall is accompanied by
   observation in the wrong direction. Drifting §6.3(b) into
   FALSIFIED language would collapse the scope lock §3.1
   distinction; discipline requires retaining FAIL here.

2. *Composition is informative without being interpretive.* The 26
   lower-tail positions are 22 neutral and 4 divergence_expected,
   with zero agreement_expected. The four divergence_expected
   entries are pos 1, 2, 3, 5 — the same four driving §6.2.2's
   FALSIFIED verdict. The neutral entries populate a stratum for
   which no gate-level pre-registered expectation applies; their
   count is recorded as an observation, not re-adjudicated.

3. *Shortfall margin is modest but material.* A 4-position shortfall
   on a 199-position denominator is small in relative terms (~2 pp)
   but exceeds any reasonable symmetric-error allowance on a gate
   pre-registered without Wilson CI. The gate is pre-registered at
   ≥ 30, not at ≥ 30 ± anything. Scope lock §4.2 forbids introducing
   post-hoc CIs, so the −4 is evaluated literally.

4. *Scope discipline.* `methodology_followup: D8.4` is emitted
   because lower-tail calibration is a direct input to D8.4 critic-
   calibration work. Candidates enumerated to justify the pointer
   include SVR-scale calibration review, neutral-stratum behavior
   audit, and mid-tail (0.30 < SVR < 0.80) population analysis;
   these are listed only to justify the D8.4 pointer, and their
   adjudication is D8.4's scope, not D8.2's.

---

### §6.3 joint — Distribution-shape derived verdict

**Pre-registered claim** (expectations.md §6.3, L110–111):

> Both (a) and (b) must pass for §6.3 as a whole to pass.

**Operational definition**: conjunction over the two sub-claims.

**Observed result** (derived from §6.3(a) and §6.3(b)):

| Quantity | Value |
|---|---|
| §6.3(a) component verdict | `PASS` (111 / 199, +21 headroom) |
| §6.3(b) component verdict | `FAIL` (26 / 199, −4 shortfall) |
| Joint conjunction | `PASS ∧ FAIL = FAIL` |

**Adjudication**:

| Field | Value |
|---|---|
| `primary_verdict` | `FAIL` |
| `interpretation_tag` | `derived_joint_failure` |
| `methodology_followup` | inherits from §6.3(b) → `D8.4` |

**Evidence narrative.** The joint verdict is a pure derivation from
the two component verdicts under the pre-registered conjunction rule.
§6.3(a) passes; §6.3(b) fails; the conjunction fails. No new
evidence is introduced. The `interpretation_tag` records that the
failure is structurally derived, not an independently observed
distributional property.

**Material finding.** *Derivation only; no new evidence.* The
`methodology_followup` is inherited from §6.3(b) because the failing
sub-claim is where the calibration signal lives; §6.3(a) contributes
no D8.4 pointer of its own.

---

### §6.4 — Fresh-7 RSI-absent vol_regime gate

**Pre-registered claim** (expectations.md §6.4, L116, with subset from L138):

> Of the 7 fresh replay positions ({3, 43, 68, 128, 173, 188, 198}),
> **≥ 2 have SVR < 0.5**.

**Operational definition**: `count(call.svr < 0.5) over {call.candidate_position in {3, 43, 68, 128, 173, 188, 198}} >= 2`

**Observed result** (D8.1 cell 16):

| Quantity | Value |
|---|---|
| Pre-registered denominator | 7 (fresh-7 RSI-absent volatility_regime subset) |
| Pre-registered threshold | count(SVR < 0.5) ≥ 2 |
| Scored subset (no errors) | 7 of 7 |
| Observed numerator | 3 |
| Observed ratio | 3 / 7 |
| Headroom vs threshold | +1 |

Per-position SVRs (D8.1 cell 16):

| pos | SVR  | UB label              | theme              |
|-----|------|-----------------------|--------------------|
| 3   | 0.15 | divergence_expected   | volatility_regime  |
| 43  | 0.25 | neutral               | volatility_regime  |
| 68  | 0.90 | neutral               | volatility_regime  |
| 128 | 0.30 | neutral               | volatility_regime  |
| 173 | 0.75 | neutral               | volatility_regime  |
| 188 | 0.80 | agreement_expected    | volatility_regime  |
| 198 | 0.90 | neutral               | volatility_regime  |

Three positions (pos 3, 43, 128) at SVR < 0.5; four positions (pos
68, 173, 188, 198) at SVR ≥ 0.5.

**Adjudication**:

| Field | Value |
|---|---|
| `primary_verdict` | `PASS` |
| `interpretation_tag` | `clean_pass` |
| `methodology_followup` | n/a |

**Evidence narrative.** The gate asks whether the fresh-7 RSI-
absent volatility_regime subset exhibits at least two low-SVR
positions, confirming the RSI-absence signal is detectable outside
the Stage 2b/2c overlap cohort. The observation (3/7, +1 headroom)
passes literally: three positions with SVR < 0.5 (pos 3 at 0.15,
pos 43 at 0.25, pos 128 at 0.30).

**Material findings.**

1. *Pos 3 serves two gates under different directional hypotheses.*
   Pos 3 (SVR 0.15, divergence_expected, volatility_regime) is
   simultaneously a member of the §6.2.2 divergence cohort and the
   §6.4 fresh-7 subset. In §6.2.2 its low SVR contributes to the
   FALSIFIED verdict (a predicted-high cohort observed low); in
   §6.4 the same observation contributes to the PASS numerator (a
   predicted-low-detectable subset observed low). The same SVR
   reading serves both because the two gates test different
   directional hypotheses; no reinterpretation is required.

2. *Pos 188 edge note.* Pos 188 (SVR 0.80, agreement_expected,
   volatility_regime) is in the fresh-7 subset but scores in the
   upper tail. It is an agreement_expected position, so high SVR is
   consistent with its UB label. The §6.4 threshold is pre-registered
   as `count(SVR < 0.5) ≥ 2` — a lower-bound count, not a 7-way
   split — so pos 188's high SVR does not reduce the numerator.
   Recorded as observation, not cause for concern.

3. *Headroom is thin (+1).* Unlike §6.2.1 and §6.3(a) where headroom
   is large, §6.4 passes by a single position margin on a 7-position
   denominator. The verdict is literal-threshold PASS; the thinness
   of headroom is noted as an observational caveat but does not
   change the adjudication. No `methodology_followup` is emitted
   because the gate's pre-registration was designed for low-n fresh-
   position validation and the observed margin is within that design.

4. *Scope discipline.* D8.3 test-retest analysis may exercise other
   fresh positions (e.g., pos 138/143); §6.4's gate-level verdict
   here is independent of that downstream work and is recorded
   without waiting on it.

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
