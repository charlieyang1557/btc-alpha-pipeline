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

Five non-gate observation entries corresponding to §4 claim
inventory rows 7–11: four §6.6 observation axes plus one §6
forensic cross-tab. The §6.6 axes are pre-registered observation
readouts without PASS/FAIL thresholds; the forensic cross-tab is a
D8.1 interpretive-input artifact (D8.1 cell 23) that is not a §6.6
axis and is not pre-registered as a gate. Both categories share
`primary_verdict = NOT_TESTABLE` / `interpretation_tag =
observation_only` under scope lock §3.4, but the taxonomic
distinction is preserved in the subsection labels below. Entries
record interpretive evidence that supports or qualifies §6 gate
adjudications without creating a new claim family. Cross-references
back to §6 are authored bidirectionally: §6 entries already
reference §7 axes; §7 entries here close the loop.

Counts are direct from D8.1 cells 18–23 (aggregate SHA
`09eeda32...c323f`); no new statistical test, Wilson CI, or
p-value is introduced (scope lock §4.2).

### §6.6(1) — Alignment distribution by UB label

**Source** (D8.1 cell 18, aggregate SHA `09eeda32...c323f`):
mean `semantic_theme_alignment` (aln) by `pre_registered_label`
over the 197 ok-scored records.

**Observation**:

| UB label            | n   | mean(aln) | median(aln) | stdev(aln) |
|---------------------|-----|-----------|-------------|------------|
| agreement_expected  | 64  | 0.819     | 0.850       | 0.105      |
| divergence_expected | 5   | 0.890     | 0.850       | 0.055      |
| neutral             | 128 | 0.837     | 0.850       | 0.090      |

The divergence_expected cohort has the highest mean alignment
(0.890) but the smallest denominator (n=5); the three cohort means
span only 0.071.

**Adjudication**:

| Field | Value |
|---|---|
| `primary_verdict` | `NOT_TESTABLE` |
| `interpretation_tag` | `observation_only` |

**Material findings.**

1. *Consistent with §6.2.2 mechanism, stated conservatively.* The
   §6.2.2 FALSIFIED adjudication observes that the divergence cohort
   is assessed at low SVR (four of five at SVR ≤ 0.15) despite being
   predicted to score high. §6.6(1) adds the alignment reading for
   the same cohort: the same five positions have the highest mean
   alignment of any cohort (0.890). The observation is that the
   model treats these candidates as thematically coherent while
   scoring them as structurally non-variant. No causal claim is made
   here; this is recorded as corroborating context only, and the
   n=5 caveat is flagged alongside.

2. *Cohort means are tight overall.* All three cohort medians are
   exactly 0.850, and the three means span 0.071 (0.819 to 0.890).
   The alignment axis does not sharply discriminate by UB label;
   its interpretive value is primarily in pair-wise correlation with
   SVR (see §6.6(2)), not in standalone cohort comparison.

---

### §6.6(2) — SVR–alignment decoupling

**Source** (D8.1 cell 19, aggregate SHA `09eeda32...c323f`): joint
distribution of SVR × alignment over the 197 ok-scored records,
isolating two structurally decoupled clusters.

**Observation**:

Two decoupled clusters (no overlap by construction):

- **Cluster (A) — HIGH-SVR / LOW-aln** (`SVR ≥ 0.75` AND `aln ≤ 0.50`):
  4 positions — pos 77, 82, 102, 117. All four carry
  `candidate_theme = mean_reversion`. UB labels: 2 agreement_expected
  (pos 82, 102), 2 neutral (pos 77, 117).

- **Cluster (B) — LOW-SVR / HIGH-aln** (`SVR ≤ 0.25` AND `aln ≥ 0.75`):
  15 positions — pos 1, 2, 3, 5, 33, 35, 38, 43, 66, 95, 99, 133,
  138, 143, 178. Theme mix dominated by volatility_regime (8 of 15);
  UB labels: 4 divergence_expected (pos 1, 2, 3, 5), 11 neutral.

**Adjudication**:

| Field | Value |
|---|---|
| `primary_verdict` | `NOT_TESTABLE` |
| `interpretation_tag` | `observation_only` |

**Material findings.**

1. *Cluster (B) contains four of the five §6.2.2 divergence cohort
   positions.* Pos 1, 2, 3, 5 all land in cluster (B); pos 6 (the
   one §6.2.2 cohort member with SVR ≥ 0.5) does not, because its
   SVR (0.75) exceeds the cluster (B) threshold of `SVR ≤ 0.25`.
   This is the bidirectional completion of the §6.2.2 → §6.6(B)
   cross-reference: §6.2.2 records the directional contradiction;
   §6.6(2) records that the contradiction coincides with a broader
   LOW-SVR/HIGH-aln decoupling cluster, not an isolated divergence-
   cohort artifact.

2. *Cluster (B) overlaps §6.3(b) lower tail.* All four
   divergence_expected cluster-(B) members (pos 1, 2, 3, 5) also
   appear in the §6.3(b) lower-tail (SVR ≤ 0.30) count of 26. This
   overlap is mechanical: cluster (B) requires SVR ≤ 0.25, which
   is a strict subset of SVR ≤ 0.30. Recorded as an observation
   of how the §6.6(B) cluster and the §6.3(b) low-tail mass
   co-locate; no additional verdict is derived.

3. *Cluster (A) is theme-homogeneous (mean_reversion).* All four
   cluster-(A) positions are mean_reversion-themed. This observation
   interacts with §6 cross-tab finding 1 (mean_reversion × neutral
   SVR-skew HIGH) rather than with any §6 gate verdict. Cluster (A)
   is not pre-registered against any claim; the pattern is recorded
   for D8.2 interpretive input only.

---

### §6.6(3) — Theme × UB label contingency

**Source** (D8.1 cell 20, aggregate SHA `09eeda32...c323f`): counts
over the 197 ok-scored records, cross-tabulated by
`candidate_theme` × `pre_registered_label`.

**Observation**:

| theme              | agree | diverg | neutral | row n |
|--------------------|-------|--------|---------|-------|
| momentum           | 14    | 2      | 23      | 39    |
| mean_reversion     | 20    | 1      | 17      | 38    |
| volatility_regime  | 5     | 1      | 34      | 40    |
| volume_divergence  | 16    | 0      | 24      | 40    |
| calendar_effect    | 9     | 1      | 30      | 40    |

Within-row percentages of note: mean_reversion runs ~53%
agreement-heavy (20 / 38); volatility_regime runs 85% neutral-heavy
(34 / 40); volume_divergence has zero divergence_expected candidates
(0 / 40).

**Adjudication**:

| Field | Value |
|---|---|
| `primary_verdict` | `NOT_TESTABLE` |
| `interpretation_tag` | `observation_only` |

**Material findings.**

1. *mean_reversion is agreement-heavy.* The mean_reversion row has
   the highest within-row agreement share (~53%) among the five
   themes. This is consistent with §6 cross-tab finding 1 (mean_
   reversion × neutral SVR-skew HIGH): mean_reversion candidates,
   even in the neutral stratum, exhibit high SVR. Recorded as
   observation only; no claim is made about whether mean_reversion
   is "overfit" to agreement.

2. *volatility_regime is neutral-heavy.* 85% of volatility_regime
   candidates are neutral-labelled (34 of 40). This is the
   structural explanation for the §6.4 fresh-7 subset being drawn
   from volatility_regime and being mostly neutral-labelled (5 of 7
   fresh-7 entries carry UB = neutral). No §6.4 verdict is affected;
   the theme-label coupling is recorded here to anchor §6.4's
   cohort shape.

3. *volume_divergence has zero divergence_expected calls.* Zero of
   40 volume_divergence candidates carry UB = divergence_expected.
   This is a candidate-selection observation, not a model-behavior
   observation: D7's candidate generator produced no volume_divergence
   proposals that the divergence-labelling convention flagged as
   divergence-expected. A possible D8.4 question — whether the
   labelling convention or the candidate generator should be tuned
   to produce some volume_divergence ∩ divergence_expected cases for
   future runs — is only flagged as a pointer, not adjudicated here.

4. *Row sizes are roughly balanced (38–40).* No theme row is
   pathologically sparse; the contingency-table shape is not
   dominated by sample-size imbalance across themes.

---

### §6.6(4) — Neutral-stratum SVR readout

**Source** (D8.1 cell 21, aggregate SHA `09eeda32...c323f`): SVR
distribution restricted to the 128 ok-scored records with
`pre_registered_label = neutral`.

**Observation**:

| Statistic | Value |
|---|---|
| n            | 128   |
| median(SVR)  | 0.750 |
| mean(SVR)    | 0.705 |

The neutral-stratum SVR median (0.75) sits above the pre-registered
agreement threshold of 0.5 and in the MOD-HIGH bucket [0.50, 0.80).

**Adjudication**:

| Field | Value |
|---|---|
| `primary_verdict` | `NOT_TESTABLE` |
| `interpretation_tag` | `observation_only` |

**Material findings.**

1. *Observation only; no comparison to Stage 2c descriptive
   heritage.* The Stage 2c critic produced a neutral-stratum SVR
   descriptive band in a different context (smaller cohort, distinct
   prompt + framing). Per hard rule 5, D8.2 does not compare the
   Stage 2d neutral median against that Stage 2c band; doing so
   would reinterpret the Stage 2d pre-registration, which anchored
   the neutral stratum as observation-only. The median 0.75 is
   recorded on its own terms.

2. *Context for §6.3(a) upper-tail composition.* The 54 neutral
   positions contributing to the §6.3(a) upper tail (SVR ≥ 0.80)
   are consistent with a neutral-stratum distribution whose median
   sits at 0.75: a neutral median above the §6.3(a) upper-tail
   floor of 0.80 would imply a majority upper-tail contribution,
   which the observed split (54 of 128 at SVR ≥ 0.80 ≈ 42%) does
   not quite reach but approaches. Recorded as corroborating
   context only; §6.3(a) is already PASS on its own count.

---

### §6 forensic cross-tab — Theme × UB label × SVR bucket

**Source** (D8.1 cell 23, aggregate SHA `09eeda32...c323f`): three-
way contingency over the 197 ok-scored records, cross-tabulated by
`candidate_theme` × `pre_registered_label` × SVR bucket. Buckets
are LOW `[0.00, 0.20)`, MOD-LOW `[0.20, 0.50)`, MOD-HIGH
`[0.50, 0.80)`, HIGH `[0.80, 1.01]`.

**Observation** (rows with notable skew):

| theme × UB            | cell n | HIGH-bucket n | HIGH %  |
|-----------------------|--------|---------------|---------|
| momentum × agreement       | 14 | 13 | 93%  |
| mean_reversion × neutral   | 17 | 12 | 71%  |
| calendar_effect × agreement|  9 |  6 | 67%  |
| volatility_regime × neutral| 34 |  6 | 18%  |

Full cell enumeration is in D8.1 cell 23 output; only the rows with
analytically relevant skews are reproduced here.

**Adjudication**:

| Field | Value |
|---|---|
| `primary_verdict` | `NOT_TESTABLE` |
| `interpretation_tag` | `observation_only` |
| `methodology_followup` | `D8.4` |

**Material findings.**

1. *mean_reversion × neutral SVR-skew HIGH (71%).* 12 of 17
   mean_reversion × neutral positions land in the HIGH bucket. This
   is the three-way completion of the §6.6(3) observation
   (mean_reversion agreement-heavy) and the §6.6(2)(A) observation
   (cluster (A) all mean_reversion): even when mean_reversion
   candidates carry a neutral UB label, their SVR sits high. The
   pattern is recorded as an observation; no verdict on
   mean_reversion as a theme is derived.

2. *volatility_regime × neutral SVR-skew contrast.* 18% of
   volatility_regime × neutral positions land in the HIGH bucket,
   ~4× lower than the mean_reversion × neutral share (71%). The two
   themes, both heavily neutral-labelled (§6.6(3)), behave
   differently at the SVR level. This contrast is recorded because
   it affects D8.4's calibration scope: a uniform SVR-calibration
   adjustment across themes would not match the observed
   theme-conditional behavior. Recorded as observation only; no
   calibration action is prescribed here.

3. *momentum × agreement concentration (93%).* 13 of 14 momentum
   agreement positions sit at SVR ≥ 0.80. This is consistent with
   the §6.2.1 agreement-axis PASS and adds no new gate evidence;
   it is retained here as a cross-tab cell rather than re-
   adjudicating §6.2.1.

4. *Scope guardrail.* The cross-tab is forensic, not a new claim
   family. No threshold is pre-registered over any theme × label ×
   bucket cell; all observations here are `NOT_TESTABLE`.

---

## 8. Delta from D8.0 Signoff

### 8.0 Preamble

D8.0 (`docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md`, SHA
`1fb1161cc1721878731b27604bac9653aac2ef5d6cf0a83900818d7398c5e998`)
remains the historically valid phase signoff for Stage 2d at the time
it was written. Per scope lock Q3/Q5 rulings, D8.0 is **not amended**:
D8.2 controls the claim-level adjudication narrative going forward;
it does not supersede D8.0's operational signoff, artifact-integrity
findings, or phase-closeout status. D8.2 only refines the claim-level
narrative where the D8.1 aggregate analysis provided evidence that
was not available at D8.0 signoff time. Operational, audit, budget,
and raw-payload retention findings in D8.0 are not touched by D8.2.

### 8.1 Delta table

| # | Claim / item | D8.0 position | D8.2 position | Disposition |
|---|---|---|---|---|
| 1 | §6.2.1 agreement axis | "Agreement-axis patterns replicated at scale" (§3, informal) | `PASS / pre_registered_claim_upheld` on 64/66 UB calls | REFINED |
| 2 | §6.2.2 divergence axis | "Carried forward for D8+ re-adjudication" (L104) — narrative flag, no verdict | `FALSIFIED / likely_directional_model_misspecification` on 1/5 at SVR≥0.5 | REFINED |
| 3 | §6.3(a) upper-tail distribution | Not adjudicated as a standalone gate | `PASS / pre_registered_claim_upheld` on 111/199 at SVR≥0.80 | NEW |
| 4 | §6.3(b) lower-tail distribution | Not surfaced as a gate; not explicitly flagged | `FAIL / calibration_shortfall` on 26/199 at SVR≤0.30 | NEW |
| 5 | §6.3 joint distributional pattern | No joint framing at signoff | Derived `PARTIAL / asymmetric_calibration` from upper-PASS + lower-FAIL | NEW |
| 6 | §6.4 fresh-7 RSI-absent vol-regime | Pos 138 RSI-absent pattern noted (L149) | Formal gate adjudicated `PASS / pre_registered_claim_upheld` at 3/7 | REFINED |
| 7 | §6.6 observation axes (4) | Treated as informal supporting evidence | Formal `NOT_TESTABLE / observation_only` taxonomy per scope lock §3.4 | REFINED |
| 8 | §6 forensic cross-tab (theme × UB × SVR bucket) | Not present | `NOT_TESTABLE / observation_only` with `methodology_followup: D8.4` | NEW |
| 9 | Multi-axis convergent evidence for §6.2.2 | Divergence reversal mentioned but not cross-referenced | Documented as 4-axis corroboration: §6.2.2 + §6.3(a) + §6.3(b) + §6.6(2)(B) | NEW |
| 10 | Pos 3 double-duty | Not called out | Recorded: same SVR=0.15 observation supports §6.2.2 FALSIFIED and §6.4 PASS under opposite directional hypotheses | NEW |
| 11 | Neutral-stratum vs Stage 2c interval | D8.0 (L105/L140) declared Stage 2c neutral-interval claim falsified at median | §6.6(4) records neutral-stratum median as observation only; declines Stage 2c comparison per hard rule 5 (no reinterpretation of pre-registered claims) | REFRAMED |

### 8.2 Per-item rationale (non-table entries)

1. **Row 1 (§6.2.1 REFINED).** D8.0 described agreement-axis behavior
   narratively; D8.2 pins the verdict to the literal pre-registered
   threshold (≥50/66 at SVR≥0.5) and records 64/66 as `PASS`.
2. **Row 2 (§6.2.2 REFINED).** D8.0 L104 explicitly deferred
   re-adjudication to D8+. D8.2 discharges that deferral by applying
   the scope lock §3.1 FAIL-vs-FALSIFIED distinction and labelling the
   outcome `FALSIFIED` (directional contradiction, not magnitude
   shortfall). The taxonomy separation is new; the directional
   reversal itself was already observed in D8.0.
3. **Rows 3, 4, 5 (§6.3 NEW).** D8.1 is the first artifact to compute
   the full distributional pattern at the pre-registered SVR tails;
   D8.0 predates that computation.
4. **Row 6 (§6.4 REFINED).** The specific pos 138 RSI-absent pattern
   is already identified in D8.0 L149; what is new in D8.2 is the
   formal gate adjudication (3/7 PASS) that places that pattern in the
   aggregate 7-call fresh-7 context.
5. **Row 7 (§6.6 REFINED).** D8.0 treated §6.6 axes as supporting
   evidence under informal wording. D8.2 formalizes their status as
   structurally non-gate observations under scope lock §3.4; this is a
   taxonomy upgrade, not a verdict reversal.
6. **Row 11 (Stage 2c comparison REFRAMED).** D8.0 L105/L140 concluded
   the Stage 2c neutral-stratum interval was falsified at median. D8.2
   does not contest that finding — it declines to re-adjudicate it
   here because the Stage 2c claim was not pre-registered as a Stage
   2d gate, and reinterpreting it inside D8.2 would violate hard rule
   5. The D8.0 finding stands as an observation about Stage 2c; D8.2
   records the Stage 2d neutral-stratum median as §6.6(4) without
   comparative framing.

### 8.3 Scope of D8.2 control

D8.2 controls the **scientific claim-level narrative** of Stage 2d
gate and observation outcomes going forward; it does not supersede
D8.0's operational signoff, artifact-integrity findings, or
phase-closeout status. Specifically unchanged:

- Operational signoff (D8.0 §1-§2, §5-§7, §10-§13 — execution,
  budget, audit, raw-payload retention, and phase-close decisions).
- Phase 2B D7 Stage 2d's status as signed-off — D8.2 does not reopen
  Stage 2d's phase-gate.
- D8.0's sign-off verdict ("PASS WITH FALSIFICATIONS", L163) remains
  the phase verdict. D8.2 refines what "WITH FALSIFICATIONS" means at
  the per-claim level; it does not recast the phase verdict.

### 8.4 Not superseded — handed off instead

Items D8.0 flagged for post-signoff follow-up that D8.2 does **not**
resolve (remain owned by downstream deliverables):

- **Overlap test–retest** for pos 138 / 143 (RSI-absent vol_regime
  twins) — deferred to **D8.3** per §6.4 methodology pointer.
- **Pos 138 RSI-absent pattern** interpretive follow-up — deferred to
  **D8.3** (test-retest) and **D8.4** (methodology refinement) per
  §6.4 and §6.6(2) methodology pointers.
- **§6 forensic cross-tab** methodology implications (prompt / label
  discipline) — deferred to **D8.4** per §7 forensic-cross-tab
  `methodology_followup`.

No D8.0 finding is silently dropped in D8.2.

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
