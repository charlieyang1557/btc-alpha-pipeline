# PHASE2C_8.1 — Multi-regime evaluation gate (extended) — closeout

**Arc**: PHASE2C_8.1 — extended multi-regime evaluation gate (n=4 baseline)
**Spec**: [`docs/phase2c/PHASE2C_8_1_PLAN.md`](../phase2c/PHASE2C_8_1_PLAN.md) (committed at `1e85d1d`)
**Implementation arc commit chain**: `1e85d1d..8086adf` (10 commits; pushed to origin/main)
**Verification chain**: three independent layers (production / Codex / permanent in-repo recompute gate); 1400/1400 tests green at `8086adf`
**Schema discriminator**: `phase2c_8_1` (novel regimes); `phase2c_7_1` (inherited regimes)
**Lineage tag**: `wf-corrected-v1` (engine commit `eb1c87f`; uniform across all 4 regimes)

---

## 1. Verdict

PHASE2C_8.1 evaluated 198 carry-forward candidates against four
regimes (two PHASE2C_7.1-inherited fully-out-of-sample regimes:
bear_2022 + validation_2024; two PHASE2C_8.1-novel train-overlap
regimes: eval_2020_v1 + eval_2021_v1) using the corrected walk-
forward engine (`wf-corrected-v1` lineage tag; engine commit
`eb1c87f`) under uniform 4-criterion AND-gate calibration with a
≥20-trade trade-count filter. The arc produces a load-bearing
population-level finding, a candidate-level finding, and three
explicit bounds on what the evidence establishes.

### 1.1 What this arc establishes

**Population-level**: a 21-vs-8 in-sample-caveat asymmetry between
train-overlap and fully-out-of-sample regimes. 21 candidates pass
the AND-gate in both eval_2020_v1 AND eval_2021_v1 jointly;
8 candidates pass the AND-gate in both bear_2022 AND validation_2024
jointly. The 21:8 ratio is observed at population level; the
asymmetry direction matches the in-sample caveat (Concern A; spec
§7.4 + §10.6) prediction that candidates more frequently pass against
regimes their training process touched than against regimes fully
untouched. Full narration at §5.

**Candidate-level**: cohort_a_unfiltered cardinality of 1 (lone
candidate `0845d1d7898412f2`, theme `volume_divergence`, name
`volume_surge_momentum_entry`); cohort_a_filtered cardinality of 0
(zero candidates survive at filtered tier). The lone unfiltered
survivor is excluded from the filtered cohort by a single-trade
margin in bear_2022 (19 trades vs ≥20 threshold). Per-regime
performance is qualitatively heterogeneous: positive returns in three
regimes (+6.8% / +18.3% / +18.6%); substantive negative return in
one regime (-10.2% in eval_2021_v1) accepted by the AND-gate as
currently calibrated. The candidate originates from the audit-only
partition (wf_test_period_sharpe = -0.072 < 0.5 primary threshold),
not the walk-forward-prequalified primary partition. Hybrid
characterization at §6.

**Methodology-evidence base**: canonical findings verified at three
independent verification layers — production comparison pipeline
with full integration test coverage; Codex adversarial review
independent recomputation from source CSVs (one-time external check
at `018d876` resolution cycle); permanent in-repo parallel-
implementation gate at `tests/test_phase2c_8_1_independent_recompute.py`
(stdlib-only; recomputes via independent code path on every CI run).
All three layers reproduce canonical numbers (cohort_a=1; cohort_c=76;
21-vs-8 asymmetry; pass-count distributions) byte-identically. Full
chain documentation at §8.

### 1.2 What this arc does not establish

The findings are bounded by methodology-evidence-hierarchy constraints
intrinsic to PHASE2C_8.1's scope per spec §10.7 out-of-scope
statements. Three explicit bounds:

**No statistical-significance claim**: PHASE2C_8.1's evaluation runs
198 candidates × 4 regimes = 792 unadjusted candidate-regime
evaluations under permissive AND-gate calibration. No Deflated
Sharpe Ratio (DSR), Probability of Backtest Overfitting (PBO),
Combinatorially Purged Cross-Validation (CPCV), or other multiple-
comparisons correction infrastructure operates within the arc. The 21-vs-8 asymmetry is a
population-level pattern observable at the register the data
supports; per-strategy or per-regime statistical significance is
not. Distinguishing whether the lone survivor reflects real cross-
regime signal or population-level random alignment requires
significance machinery deferred per spec §10.7 (Q-B4 territory).

**No deployability claim**: Deployment-time inference about
regime-conditional strategy selection is out-of-scope per spec
§10.7. The lone survivor's permissive AND-gate pass with -10.2%
return in one regime, single-trade-margin filter exclusion in
another regime, and audit-only-partition origin do not constitute
deployment-quality strategy evidence. No candidate identified by
PHASE2C_8.1's evaluation is endorsed for deployment; cross-regime
survival at AND-gate calibration is a screening signal, not a
deployment signal.

**No mechanism proof**: The 21-vs-8 asymmetry is consistent with
in-sample caveat bias (candidate-screening artifacts inflating pass
rates against train-overlap regimes) but is not proof of causal
overfitting at any individual candidate. The audit-only-partition
origin of the lone survivor is consistent with multiple mechanisms
(walk-forward classifier mis-coverage, selection-effect amplification,
trade-frequency interaction with audit-only classification); the
evidence base does not adjudicate which mechanism applies. Mechanism
adjudication is bounded to population-level observation; per spec
§10.7, mechanism investigation is out-of-scope for PHASE2C_8.1.

### 1.3 Verdict register

The verdict synthesis at this register: **PHASE2C_8.1 strengthens
the methodology-evidence base while constraining strategy-evidence
claims**. The two directions are not contradictory; they are
complementary outputs of the same evaluation:

- **Methodology-evidence strengthened**: verification chain at three
  independent layers; canonical numbers triple-verified;
  in-sample-caveat asymmetry pattern observed in the direction Concern
  A predicts; audit-only-partition origin reinforces PHASE2C_7.1's
  audit-only-mirror finding direction at the n=4 register. The
  empirical foundation under PHASE2C_8.1's findings is the strongest
  in the project's PHASE2C closeout history.

- **Strategy-evidence constrained**: cohort_a_filtered=0; lone
  unfiltered survivor's hybrid quality profile (off-by-1 filter
  exclusion + permissive AND-gate accepting negative return + audit-
  only origin); 21-vs-8 asymmetry indicating that train-overlap-
  apparent quality may not generalize to fully-out-of-sample
  evaluation. The evaluation produces fewer high-conviction strategy
  candidates than prior arcs anticipated, not more.

The verdict register inherits the bounded-negative-claim discipline
established in §5.4 + §6.4 at synthesis level. PHASE2C_8.1 does not
claim "we found a robust strategy" (§6's hybrid lone-survivor
characterization bounds this); does not claim "we falsified
candidate-screening overfitting" (§5's asymmetry-as-evidence-not-
proof bounds this); does not claim "the methodology is broken"
(§6.5's calibration-question-not-calibration-finding bounds this).
The arc claims what the evidence supports: a population-level
asymmetry observable at the register the data supports, a candidate-
level lone-survivor finding bounded by hybrid characterization, and
three explicit methodology-evidence-hierarchy constraints on
extension to per-strategy claims.

### 1.4 Forward signals

PHASE2C_8.1's findings surface methodology-evidence questions that
the arc's scope does not adjudicate. These are tracked in the §10
register as observed-not-adjudicated questions for downstream
methodology consideration; their resolution is not in PHASE2C_8.1's
scope per spec §10.7 out-of-scope statements. §11 surfaces the
empirically-anchored forward signals without pre-naming successor
arcs.

The arc closes with ten tracked-fix register entries (Q-S4-5,
Q-S4-7, Q-S4-9, Q-S4-10, Q-S4-11, Q-S4-12, Q-S4-13, Q-S4-14,
Q-S4-15, Q-S4-16) enumerated at §10. Q-S4-12 carries forward as
pending closeout-commit cycle (CLAUDE.md Phase Marker reconciliation
per D-S5-4). Four entries cluster as methodology-codification
candidates (Q-S4-10, Q-S4-14, Q-S4-15, Q-S4-16) per §10.2;
remaining six entries are empirical-finding-derived, verification
actions, or procedural per the §10 register table. Q-S4-14 records
a methodology-process observation: dual-reviewer review caught
different classes of register defects across drafting cycles
(content-level register defects caught by one reviewer; phrasing-
precision defects caught by the other; bidirectional pattern across
sections). It is a codification candidate for the closeout-commit
cycle, not an empirical finding of PHASE2C_8.1.

The arc closes with the strongest evidence base under any closeout
finding in project history (three-layer verification chain) and a
verdict that holds the bounded-claim register from load-bearing-
cluster sections at synthesis level.

## 2. Scope and methodology

### 2.0 Arc setup

PHASE2C_8.1 evaluates the PHASE2C_6 carry-forward 198-candidate
batch against four regimes at unfiltered + filtered tiers, using
the corrected walk-forward engine (lineage tag `wf-corrected-v1`;
engine commit `eb1c87f`) under uniform calibration (4-criterion
AND-gate + ≥20-trade trade-count filter) per the inherited
PHASE2C_7.1 calibration baseline. Arc scope and methodology are
specified at `docs/phase2c/PHASE2C_8_1_PLAN.md` (committed at
`1e85d1d`); this section documents the operational structure that
produced the canonical findings without re-deriving the spec
rationale.

### 2.1 Four-regime evaluation composition

The n=4 evaluation composition combines two inherited regimes and
two novel regimes:

**Inherited regimes** (PHASE2C_7.1 carry-forward; schema discriminator
`phase2c_7_1`; `in_sample_caveat_applies = false`):

- **bear_2022** (regime_key `v2.regime_holdout`): the v2 split
  version's regime_holdout calendar period. Untouched during
  PHASE2C_5 walk-forward training; provides fully-out-of-sample
  evidence relative to the 198-candidate population. Inherits
  PHASE2C_6 evaluation gate artifacts at canonical path
  `data/phase2c_evaluation_gate/audit_v1`.
- **validation_2024** (regime_key `v2.validation`): the v2 split
  version's validation calendar period. Untouched during PHASE2C_5
  training; provides fully-out-of-sample evidence. Inherits
  PHASE2C_7.1 evaluation gate artifacts at canonical path
  `data/phase2c_evaluation_gate/audit_2024_v1`.

**Novel regimes** (PHASE2C_8.1 introduced; schema discriminator
`phase2c_8_1`; `in_sample_caveat_applies = true`):

- **eval_2020_v1** (regime_key `evaluation_regimes.eval_2020_v1`):
  2020 calendar year. Overlaps the v2 train split (train =
  2020-2021 + 2023 per `config/environments.yaml`); in-sample
  caveat applies. PHASE2C_8.1 producer-emitted at canonical path
  `data/phase2c_evaluation_gate/eval_2020_v1`.
- **eval_2021_v1** (regime_key `evaluation_regimes.eval_2021_v1`):
  2021 calendar year. Overlaps the v2 train split; in-sample
  caveat applies. PHASE2C_8.1 producer-emitted at canonical path
  `data/phase2c_evaluation_gate/eval_2021_v1`.

The two evidentiary categories — fully-out-of-sample (bear_2022 +
validation_2024) versus train-overlap (eval_2020_v1 + eval_2021_v1)
— are tracked at metadata level via the `in_sample_caveat_applies`
boolean field per regime (spec §7.5). The categorization is the
basis for §5's in-sample-caveat asymmetry stratification.

### 2.2 Engine-version invariance (Option A)

PHASE2C_8.0 scoping decision (`f223316`) adjudicated the engine-
version handling for the 198-candidate batch's cross-regime
evaluation as Option A: re-evaluate the same 198 candidates against
all 4 regimes using the same corrected engine commit `eb1c87f`.
The alternative (Option B: per-arc engine version with
heterogeneous evaluation) was adjudicated against because cross-
regime comparison validity requires engine-version invariance —
candidate evaluations across regimes must use identical engine
semantics for cohort-aligned comparison to be defensible.

Option A operationalizes uniformly across all 4 regime evaluations:
each regime's per-candidate JSON artifacts at canonical path
`data/phase2c_evaluation_gate/{regime}_v1/` carries
`engine_commit = "eb1c87f"` and `lineage_tag = "wf-corrected-v1"`
in its lineage attestation. The corrected-engine consumer guard
`check_evaluation_semantics_or_raise()` at `backtest/wf_lineage.py`
validates the lineage on every consumer-side artifact read; lineage
mismatches raise rather than silently propagating.

### 2.3 Calibration baseline (PHASE2C_7.1 carry-forward)

PHASE2C_8.1 inherits PHASE2C_7.1's calibration baseline uniformly
across all 4 regimes; calibration variation (Q-B2 territory per
PHASE2C_8.0 scoping) is explicitly out-of-scope per spec §10.7.

**4-criterion AND-gate** (D2 carry-forward): a candidate passes
the AND-gate in a given regime when all four criteria hold
simultaneously:

- `holdout_sharpe ≥ −0.5`
- `holdout_max_drawdown ≤ 0.25`
- `holdout_total_return ≥ −0.15`
- `holdout_total_trades ≥ 5`

The criteria are calibrated permissively at the inherited baseline;
calibration appropriateness for multi-regime evaluation contexts
is the methodology question surfaced at Q-S4-13 (§6.5).

**Trade-count filter** (D1 carry-forward; ≥20 trades): the filtered
tier excludes per-regime evaluations where the candidate's
`holdout_total_trades < 20`. The filter operates per regime
independently — a candidate may be in the filtered set for some
regimes and not others. The filtered cohort cardinalities at §3.1
+ §3.3 reflect per-regime filter application; the trade-count
filter threshold pinning at ≥20 is per spec §5.1.

### 2.4 Operational machinery layers

PHASE2C_8.1's evaluation operates across four machinery layers:

**Producer layer** (`scripts/run_phase2c_evaluation_gate.py`):
emits per-regime per-candidate `holdout_summary.json` artifacts +
per-regime `holdout_results.csv` summary + lineage attestation
files. Producer is regime-key-agnostic; per-regime invocation
specifies `--regime <regime_key>`. PHASE2C_8.1 extended the
producer to handle the `evaluation_regimes` namespace alongside
the inherited `v2` namespace (commit `9ef9cab`).

**Consumer-guard layer** (`backtest/wf_lineage.py`): validates
producer-emitted artifacts at consumer-side reads. The schema
discriminator chain (`phase2c_7_1` ↔ `phase2c_8_1` ↔ legacy-absent)
is reconciled per spec §6.5. Mixed-discriminator artifact reads
operate transparently at consumer-side; the discriminator is
checked but not used to filter (the comparison logic operates on
metric values, agnostic to schema version).

**Filter layer** (`scripts/filter_evaluation_gate.py`): emits the
filtered-tier artifact subdir per regime by applying the ≥20-trade
threshold. Filter operates per regime independently. The lone
unfiltered cross-regime survivor's bear_2022 single-trade-margin
exclusion (§3.3 + §6) is the operational consequence of the filter
layer applied uniformly.

**Comparison layer** (`scripts/compare_multi_regime.py`): builds
the n-way candidate-aligned comparison matrix from the four
producer + filter artifacts. Comparison schema version
`comparison_schema_v2` (n-way; v1 was 2-way). Cohort categorization,
pass-count distribution, and in-sample-caveat stratification are
emitted at the comparison-summary register. The comparison machinery
is verified at three independent verification layers (full chain
documentation at §8).

### 2.5 In-sample caveat semantics

The `in_sample_caveat_applies` boolean field per regime (spec §7.5)
is the metadata anchor for the in-sample-caveat asymmetry
stratification at §5. Spec §7.5 declares:
`in_sample_caveat_applies = true` for eval_2020_v1 + eval_2021_v1
(train-overlap regimes); `in_sample_caveat_applies = false` for
bear_2022 + validation_2024 (fully-out-of-sample regimes). The
implementation at `scripts/compare_multi_regime.py` derives the
field via the schema discriminator chain (caveat=true iff
schema_version == phase2c_8_1; otherwise caveat=false), which
maps to the spec declaration via the regime-key → schema-version
table. Spec-implementation alignment is confirmed (Q-S4-9 register
entry; alignment verified at drafting cycle without defect).

The in-sample caveat is structural to the candidate-regime selection
scope (PHASE2C_8.0 scoping decision; spec §3.1 + §3.3 + §7.4); the
caveat is captured as metadata, not as a defect. §5's asymmetry
finding interprets the caveat operationally as evidentiary-category
distinction.

### 2.6 Forward references

§2 documents the operational structure that produced the canonical
findings. Per-section forward-pointers:

- §3 cohort categorization (cardinalities + pass-count distribution
  consume the operational structure documented at §2.4 layers)
- §5 in-sample-caveat asymmetry interpretation (consumes §2.5
  in-sample-caveat semantics)
- §6 lone survivor characterization (consumes §2.3 calibration
  baseline as evaluation-criteria context)
- §8 verification chain (full three-layer documentation; verifies
  the operational structure documented at §2.4 layers)
- §10 tracked-fix register (Q-S4-9 in-sample-caveat alignment fold;
  Q-S4-13 calibration methodology question fold)

## 3. Cohort categorization

### 3.0 Cohort definitions

PHASE2C_8.1's 4-regime evaluation produces three cohort cardinalities
at unfiltered + filtered tiers, derived from per-candidate AND-gate
pass counts across the 4 regimes:

- **Cohort (a)**: cross-regime survivors. Unfiltered tier =
  candidates passing the AND-gate in all 4 regimes; filtered tier =
  candidates passing the AND-gate in all 4 regimes AND surviving
  the trade-count filter (≥20 trades) in all 4 regimes.
- **Cohort (b)**: per-regime cross-tab. Distribution of candidates
  by pass-count {0, 1, 2, 3, 4} across the 4 regimes; reported as
  pass-count histogram per tier.
- **Cohort (c)**: failures. Candidates passing the AND-gate in
  zero regimes (per-candidate pass count = 0).

The cohort categorization operates at unfiltered + filtered tiers
symmetrically. The trade-count filter (≥20 trades; PHASE2C_7.1 D1
carry-forward; pinned per spec §5.1) is applied uniformly across
all 4 regimes; per-tier cardinalities differ where candidates whose
trade count falls below 20 in any single regime are excluded from
that regime's filtered set, reducing cross-regime survival
proportionally to candidate trade-frequency heterogeneity across
regimes.

### 3.1 Cohort cardinalities at n=4

| Cohort | Unfiltered tier | Filtered tier |
|---|---|---|
| (a) cross-regime survivors | 1 | 0 |
| (c) failures (passes 0 regimes) | 76 | — |
| Universe | 198 | 198 |

**Cohort (a) unfiltered cardinality = 1**: a single candidate passes
the AND-gate across all 4 regimes simultaneously at unfiltered tier.
The single candidate is hypothesis hash `0845d1d7898412f2`. Detailed
characterization at §6.

**Cohort (a) filtered cardinality = 0**: zero candidates pass the
AND-gate across all 4 regimes simultaneously when the trade-count
filter is applied uniformly. The lone unfiltered survivor is excluded
from the filtered cohort by a single-trade margin in bear_2022 (19
trades vs ≥20 threshold). Detailed characterization at §6.

**Cohort (c) failures cardinality = 76**: 76 candidates pass the
AND-gate in zero regimes (per-candidate pass count = 0 across all
4 regime evaluations). Reported at unfiltered tier; cohort (c)
filtered cardinality is not separately tracked because cohort (c)'s
zero-regime-pass criterion is invariant under filter application
(a candidate passing zero regimes at unfiltered tier passes zero
regimes at filtered tier by trivial implication; filtered tier
introduces additional exclusions but does not produce additional
failures).

**Universe cardinality = 198**: the PHASE2C_6 carry-forward
candidate batch. Universe symmetry across all 4 unfiltered regimes
is verified by construction (each regime evaluation consumes the
same 198-candidate set) and confirmed via cross-regime universe-
symmetry assertion in `scripts/compare_multi_regime.py`. Per spec
§7.4, candidates partition into primary (n=44; wf_test_period_sharpe
> 0.5) + audit-only (n=154; wf_test_period_sharpe ≤ 0.5).

### 3.2 Pass-count distribution

Per-candidate pass count is computed as the number of regimes in
which the candidate passes the AND-gate, ranging {0, 1, 2, 3, 4}.
Distribution histograms at unfiltered + filtered tiers:

| Pass count | Unfiltered tier | Filtered tier |
|---|---|---|
| 0 | 76 | 87 |
| 1 | 55 | 58 |
| 2 | 45 | 38 |
| 3 | 21 | 15 |
| 4 | 1 | 0 |
| Total | 198 | 198 |

Both distributions are right-skewed; the filtered-tier distribution
is more right-skewed than the unfiltered-tier distribution, with
the cohort (c) failures (pass-count = 0) cardinality expanding from
76 unfiltered to 87 filtered (+11). The trade-count filter reduces
cross-regime survival in proportion to candidate trade-frequency
heterogeneity across regimes — candidates whose trade count drops
below 20 in any regime lose that regime's contribution to their
pass-count, shifting density toward lower pass-count buckets.

### 3.3 Per-regime evaluation summary

Per-regime AND-gate pass cardinalities at unfiltered + filtered
tiers (factual context for §5's in-sample-caveat asymmetry
interpretation):

| Regime | Caveat category | Unfiltered universe / passed | Filtered universe / passed |
|---|---|---|---|
| bear_2022 | fully-out-of-sample | 198 / 13 | 146 / 12 |
| validation_2024 | fully-out-of-sample | 198 / 87 | 144 / 79 |
| eval_2020_v1 | train-overlap | 198 / 74 | 140 / 61 |
| eval_2021_v1 | train-overlap | 198 / 38 | 144 / 27 |

The per-regime cardinalities show cross-regime heterogeneity in
AND-gate pass rates. The bear_2022 filtered tier's 12 passes versus
unfiltered tier's 13 passes differs by exactly one candidate — the
lone unfiltered cross-regime survivor `0845d1d7898412f2`, excluded
from the bear_2022 filtered set by a single-trade margin (19 trades
vs ≥20 threshold; detailed at §6).

Cardinality interpretation against the in-sample caveat (Concern A)
is the load-bearing finding at §5; this section documents the
per-regime pass counts as factual basis without extending
interpretation beyond the cardinality enumeration itself.

The 21-vs-8 in-sample-caveat asymmetry derived from cohort
intersection within evidentiary categories (21 candidates passing
both train-overlap regimes jointly; 8 candidates passing both
fully-out-of-sample regimes jointly) is detailed at §5.

### 3.4 Forward references

Cohort cardinalities documented at §3 are interpreted against the
in-sample caveat at §5 (population-level asymmetry register) and
detailed at §6 for the lone unfiltered survivor (candidate-level
hybrid characterization). §3 carries forward the canonical
cardinalities documented at this section to §5's asymmetry
interpretation and §6's lone-survivor characterization without
duplicating their interpretation registers.

The cohort cardinalities at §3 are verified at three independent
verification layers (full chain documentation at §8). Production
comparison pipeline output, Codex adversarial review independent
recomputation, and permanent in-repo independent-recompute gate at
`tests/test_phase2c_8_1_independent_recompute.py` all reproduce the
canonical cardinalities byte-identically.

## 4. Pass-count distribution

### 4.0 Distribution definition

For each of the 198 candidates, the per-candidate pass count at a
given tier is the number of regimes (out of 4) in which the candidate
passes the AND-gate. Pass count ranges {0, 1, 2, 3, 4} per candidate.
The pass-count distribution is the histogram of candidates by their
pass-count value, reported per tier (unfiltered + filtered).

The distribution is the per-regime cross-tab cohort (cohort (b) per
spec §6.6); cohort (a) cross-regime survivors and cohort (c)
failures are derived from the distribution's tails (cohort (a) =
candidates at pass count 4; cohort (c) = candidates at pass count
0; documented at §3.1).

### 4.1 Pass-count histogram

| Pass count | Unfiltered tier | Filtered tier |
|---|---|---|
| 0 | 76 | 87 |
| 1 | 55 | 58 |
| 2 | 45 | 38 |
| 3 | 21 | 15 |
| 4 | 1 | 0 |
| Total | 198 | 198 |

Both distributions are right-skewed (modal class is pass count = 0
at both tiers). Universe cardinality is preserved across tiers
(198 candidates total at both unfiltered and filtered tier; the
filter tier counts a candidate at the pass count that reflects the
candidate's regime-specific filter+AND-gate outcomes, not the
candidate's exclusion from a global filter set; see §3.0 for the
operational distinction).

### 4.2 Filtered-vs-unfiltered shift

The filtered-tier distribution shifts toward lower pass counts
relative to the unfiltered-tier distribution:

| Pass count | Unfiltered | Filtered | Δ (filtered − unfiltered) |
|---|---|---|---|
| 0 | 76 | 87 | +11 |
| 1 | 55 | 58 | +3 |
| 2 | 45 | 38 | −7 |
| 3 | 21 | 15 | −6 |
| 4 | 1 | 0 | −1 |

The shift signs are factually consistent with the trade-count filter's
direction: candidates whose trade count drops below 20 in any single
regime lose that regime's contribution to their pass count, shifting
density from higher pass-count buckets (2/3/4) toward lower pass-count
buckets (0/1). The +11 increase at pass-count = 0 is the largest
single shift; the −1 shift at pass-count = 4 reflects the lone
unfiltered survivor `0845d1d7898412f2`'s exclusion from the filtered
cohort (off-by-1 trade-count margin in bear_2022; detailed at §6.2).

The pre-tier and post-tier sums are equal (76+55+45+21+1 = 198;
87+58+38+15+0 = 198) — the filter operates per-regime within each
candidate's per-regime evaluation, not as a global candidate
exclusion; the universe cardinality is invariant under tier
application.

### 4.3 Forward references

§4 documents the pass-count distribution as factual cross-tab; the
distribution is the basis for cohort categorization at §3.1 and
the in-sample-caveat asymmetry stratification at §5. §6.2 references
the −1 shift at pass-count = 4 as the lone-survivor's filter
exclusion (cardinality-observable). §3.2 reports the same histogram
in its cohort-categorization context.

The pass-count distribution is verified at three independent
verification layers (full chain documentation at §8); Layer 3's
canonical-finding assertion `test_pass_count_distribution_unfiltered`
+ `test_pass_count_distribution_filtered` reproduces the histogram
byte-identically against the production pipeline output.

## 5. In-sample caveat stratification

### 5.0 Headline finding

Across the 198-candidate population evaluated against four regimes,
**21 candidates pass the AND-gate in both train-overlap regimes
(eval_2020_v1, eval_2021_v1) jointly, while 8 candidates pass the
AND-gate in both fully-out-of-sample regimes (bear_2022,
validation_2024) jointly**. The 21:8 ratio is a population-level
asymmetry consistent with the in-sample caveat (Concern A) prediction:
a candidate population whose selection process touched 2020/2021 sub-
windows shows higher pass rates against 2020/2021-overlapping
evaluation regimes than against fully untouched evaluation regimes.

This is the load-bearing empirical finding of PHASE2C_8.1's 4-regime
evaluation. The two evidentiary categories — fully-out-of-sample
versus train-overlap — produce population-level pass-rate divergence
in the direction the in-sample caveat predicts.

### 5.1 The in-sample caveat (Concern A)

PHASE2C_8.1's selected additional regimes (eval_2020_v1, eval_2021_v1)
overlap the v2 split version's train calendar period. The 198-candidate
population's PHASE2C_5 walk-forward training process used sub-windows
of these calendar periods; evaluating the population against
eval_2020_v1 + eval_2021_v1 introduces in-sample evaluation overlap.
The caveat is documented verbatim at spec §7.4 and §10.6:

> 2020/2021 overlap the original train-window context; mitigated by
> walk-forward sub-window discipline, but not equivalent to untouched
> validation/test evidence.

The mechanism is structural rather than incidental. PHASE2C_5
training used sub-windows of 2020 and 2021 historical data; PHASE2C_6's
198-candidate population may carry candidate-screening overfitting
against these regimes. Cross-regime patterns observed in 2020/2021
may reflect candidate-screening artifacts rather than mechanism-
relevant structure.

Mitigation status is partial, not zero. Walk-forward sub-window
discipline operates within each candidate's training process —
training windows are sub-windows of the calendar year, not the full
year; walk-forward cross-validation operates within-regime. The
mitigation reduces the in-sample overlap concern but does not
eliminate it; train-overlap evaluation is not equivalent to fully-
untouched evidence (such as bear_2022 holdout or validation_2024).

The two evidentiary categories operate at distinct evidentiary
registers and are tracked at metadata level via the
`in_sample_caveat_applies` boolean field per regime (spec §7.5):

- **Fully-out-of-sample regimes** (`in_sample_caveat_applies = False`):
  bear_2022 (v2.regime_holdout), validation_2024 (v2.validation).
  These regimes were untouched during PHASE2C_5 training and provide
  fully out-of-sample evidence relative to the 198-candidate
  population.
- **Train-overlap regimes** (`in_sample_caveat_applies = True`):
  eval_2020_v1, eval_2021_v1. These regimes overlap the v2 train
  split with partial walk-forward sub-window mitigation.

Per spec §9 pass/fail criteria discipline, the two evidentiary
categories should not be equated; per spec §10.6, the comparison
register operationally distinguishes them.

### 5.2 Empirical observation: 21-vs-8 asymmetry

For each of the 198 candidates, the AND-gate evaluation produces a
boolean pass/fail flag per regime (passing requires sharpe ≥ −0.5,
max_drawdown ≤ 0.25, total_return ≥ −0.15, total_trades ≥ 5;
inherited from PHASE2C_7.1 calibration baseline). The
in-sample-caveat stratification counts:

- **n_passing_all_train_overlap = 21**: candidates passing the
  AND-gate in both eval_2020_v1 AND eval_2021_v1 (the two train-
  overlap regimes; in-sample caveat applies).
- **n_passing_all_fully_out_of_sample = 8**: candidates passing the
  AND-gate in both bear_2022 AND validation_2024 (the two fully-
  out-of-sample regimes; no in-sample caveat).

The 21:8 ratio (≈2.6×) is the population-level pass-rate asymmetry.
The asymmetry direction matches the in-sample caveat prediction:
candidates more frequently pass against regimes their training
process touched than against regimes fully untouched by their
training process.

For context (auxiliary; full cohort categorization narrated in §3):
cohort intersection at n=4 is 1 candidate unfiltered, 0 at filtered
tier; cohort failures (passes 0 regimes) is 76; pass-count distribution
is right-skewed across both tiers. These cohort cardinalities provide
context for the 21-vs-8 finding but are not §5's load-bearing claim;
the load-bearing claim is the in-sample-caveat asymmetry itself.

### 5.3 What this asymmetry establishes

The 21-vs-8 finding establishes a population-level pattern at the
register the empirical evidence supports:

- **Pass-rate divergence between evidentiary categories**: The 21:8
  ratio is a directly observed population-level statistic; canonical
  numbers verified byte-identical across three independent code
  paths (production comparison pipeline; Codex adversarial review
  recomputation; permanent in-repo independent-recompute gate at
  `tests/test_phase2c_8_1_independent_recompute.py`).
- **Direction consistency with in-sample caveat prediction**: The
  asymmetry direction (train-overlap > fully-out-of-sample) is the
  direction Concern A predicts. The empirical observation is
  qualitatively consistent with the structural mechanism (candidate-
  screening artifacts may inflate pass rates against train-overlap
  regimes).
- **Evidentiary integrity at the methodology-evidence hierarchy
  register**: The in-sample caveat is intrinsic to the candidate-
  regime selection scope (per spec §3.3 selection rationale; §3.1
  S3 = MED scoring rationale); the 21-vs-8 finding operationally
  confirms the structural concern observed at scoping time.

### 5.4 What this asymmetry does NOT establish

The 21-vs-8 finding does not extend to claims the evidence cannot
support. Three explicit bounds:

- **No causal overfitting proof**: The asymmetry is consistent with
  in-sample caveat bias (candidate-screening artifacts inflating
  pass rates on train-overlap regimes) but is not proof of causal
  overfitting at any individual candidate. Some of the 21 train-
  overlap-passers may pass on real cross-regime structure; some
  of the 8 fully-out-of-sample-passers may fail train-overlap from
  noise rather than mechanism. Per-candidate causal attribution is
  beyond the evidence base.
- **No statistical-significance claim**: PHASE2C_8.1 does not run
  Deflated Sharpe Ratio (DSR), Probability of Backtest Overfitting
  (PBO), Combinatorially Purged Cross-Validation (CPCV), or any
  other multiple-comparisons correction. With 198 candidates ×
  4 regimes = 792 unadjusted hypothesis tests, no per-strategy
  significance claim is defensible from this evidence base. The
  21-vs-8 population-level pattern is observable; per-strategy
  significance is not. DSR / PBO / CPCV infrastructure is deferred
  to a future arc (PHASE2C_8.0 §5 follow-up scoping Q-B4 territory;
  explicitly out-of-scope per spec §10.7).
- **No regime-specific deployability claim**: Deployment-time
  inference about regime-conditional strategy selection is out-of-scope
  for PHASE2C_8.1's evaluation. A candidate passing both train-overlap
  regimes but failing both fully-out-of-sample regimes is consistent
  with multiple readings — train-overlap artifact, regime-conditional
  edge, walk-forward sub-window insufficiency, or sample-size variance.
  Per spec §10.7 out-of-scope statements, regime classification
  infrastructure is not part of PHASE2C_8.1's implementation surface;
  the evidence base does not support per-regime deployability claims
  at this scope.

The asymmetry is a population-level evidentiary signal observable
at the register the data supports. Extension to per-candidate
significance, per-candidate causal claims, or per-regime
deployability claims requires verification machinery not present
in PHASE2C_8.1's scope.

### 5.5 Verification chain backing

The 21-vs-8 canonical numbers are verified at three independent
verification layers (full chain documentation in §8): the production
comparison pipeline at `scripts/compare_multi_regime.py` (with
integration test coverage); Codex adversarial review independent
recomputation from source CSVs (one-time external check at commit
`018d876` resolution cycle); the permanent in-repo parallel-
implementation gate at `tests/test_phase2c_8_1_independent_recompute.py`
(stdlib-only; recomputes via independent code path on every CI run).
All three layers reproduce the 21:8 numbers byte-identically. The
finding's empirical foundation is the strongest of any finding in
the project's PHASE2C closeout history.

The 21-vs-8 in-sample-caveat asymmetry is reported with the bounds
of §5.4 explicit: empirically observed, qualitatively consistent
with in-sample caveat prediction, not statistically significance-
tested, not causally attributed at per-candidate register, not
extended to per-regime deployability claims.

## 6. Lone survivor characterization

### 6.0 Headline finding

Of the 198 candidates evaluated against four regimes at unfiltered
tier, **exactly one candidate passes the AND-gate in all four regimes
simultaneously**: hypothesis hash `0845d1d7898412f2`, theme
`volume_divergence`, name `volume_surge_momentum_entry`, batch
position 39. At filtered tier (after applying the trade-count filter
of ≥20 trades per regime), **zero candidates pass**: the lone
unfiltered survivor is excluded from the filtered cohort.

The lone survivor's per-regime evaluation profile combines elements
that resist clean categorical narration. The honest characterization
is hybrid: a candidate that survives all four regimes at the AND-gate
level, fails the filtered tier on a single-trade margin in one
regime, exhibits qualitatively mixed performance across regimes
(positive returns in three; negative return in one), and originates
from the audit-only partition rather than the walk-forward-prequalified
primary partition.

### 6.1 Per-regime evaluation profile

The candidate's per-regime metrics are extracted from the four
producer `holdout_results.csv` files at canonical paths:

| regime | category | trades | sharpe | max_dd | total_return | passed AND-gate | in filtered set |
|---|---|---|---|---|---|---|---|
| bear_2022 | fully-OOS | 19 | 0.508 | 0.095 | +6.80% | True | False |
| validation_2024 | fully-OOS | 23 | 1.053 | 0.172 | +18.3% | True | True |
| eval_2020_v1 | train-overlap | 27 | 0.813 | 0.245 | +18.6% | True | True |
| eval_2021_v1 | train-overlap | 29 | -0.358 | 0.232 | -10.2% | True | True |

Walk-forward test-period metric (the prequalification context for
PHASE2C_5's primary cohort selection): `wf_test_period_sharpe =
-0.072`, below the 0.5 threshold that defines the primary partition.
The candidate is in the audit-only partition (n=154), not the
primary partition (n=44).

### 6.2 The hybrid narration

Four observations characterize the lone survivor without forcing
the data into pre-defined categorical buckets:

**(i) Survives all four unfiltered regimes**: The candidate passes
the 4-criterion AND-gate (sharpe ≥ −0.5; max_drawdown ≤ 0.25;
total_return ≥ −0.15; total_trades ≥ 5; inherited from PHASE2C_7.1
calibration baseline) in each of the four regime evaluations. This
is the headline structural finding: out of 198 candidates evaluated,
this is the only candidate whose evaluation profile clears the
AND-gate threshold across the full 4-regime evaluation matrix.

**(ii) Excluded from filtered cohort by a single-trade margin in
bear_2022**: The trade-count filter (≥20 trades per regime; PHASE2C_7.1
D1 carry-forward) excludes the candidate from the bear_2022 filtered
set. The candidate's bear_2022 trade count is 19 — one trade below
the ≥20 threshold. If the threshold were 18 instead of 20, the
filtered cohort cardinality would be 1 instead of 0. The "zero
candidates survive at filtered tier" structural finding hinges on
a 1-trade margin in a single regime; the structural collapse claim
is bounded by this margin.

**(iii) Eval_2021_v1 passes despite -10.2% return**: The AND-gate
criteria are calibrated permissively — `total_return ≥ −0.15` accepts
returns down to -15% loss; `sharpe ≥ -0.5` accepts negative-Sharpe
performance. The candidate's eval_2021_v1 profile (sharpe -0.358;
return -10.2%; max_drawdown 0.232) clears every AND-gate threshold
narrowly: -0.358 ≥ -0.5 (passes by 0.142); -0.102 ≥ -0.15 (passes
by 0.048); 0.232 ≤ 0.25 (passes by 0.018); 29 ≥ 5 (passes
substantially). The candidate's "passes all four regimes" claim is
technically correct but qualitatively heterogeneous — three regimes
of positive return (+6.8% / +18.3% / +18.6%) and one regime of
substantial negative return (-10.2%) are merged at the AND-gate
boolean register.

**(iv) Audit-only partition origin**: The candidate's
`wf_test_period_sharpe` is -0.072, below the 0.5 primary threshold.
The PHASE2C_5 walk-forward evaluation classified this candidate as
audit-only — the partition reserved for low-quality candidates that
clear basic structural thresholds but do not demonstrate convincing
walk-forward performance. The lone cross-regime survivor in PHASE2C_8.1's
4-regime evaluation is therefore not from the walk-forward-prequalified
primary cohort; it is from the audit-only cohort whose walk-forward
performance was insufficient for primary selection.

### 6.3 Audit-only partition implication

The audit-only origin is the most consequential observation for
methodology-evidence-hierarchy register. PHASE2C_7.1 surfaced an
audit-only-mirror finding direction (audit-only cohort exhibited
distinct cross-regime patterns relative to primary cohort);
PHASE2C_8.1's lone-survivor finding reinforces this direction at
the n=4 register.

The pattern is structurally consequential: the strongest cross-regime
survival signal in the entire 198-candidate population came from a
candidate that walk-forward classification considered low-quality.
This may reflect one or more of:

- **Walk-forward classifier mis-coverage**: Walk-forward prequalification
  may filter signal that survives multi-regime testing. If
  cross-regime stability is a quality dimension that walk-forward
  test-period sharpe does not fully capture, the audit-only cohort
  may contain candidates whose multi-regime profile exceeds what
  walk-forward classification predicts.
- **Selection-effect amplification**: With cohort_a unfiltered
  cardinality of 1 across 198 candidates evaluated against 4 regimes
  (792 unadjusted candidate-regime evaluations under permissive
  AND-gate calibration), the observation is structurally consistent
  with both real cross-regime signal and population-level random
  alignment. Distinguishing the two interpretations requires
  multiple-comparisons-corrected significance machinery (DSR / PBO /
  CPCV) that PHASE2C_8.1's scope does not include; the evidence
  base does not adjudicate signal-vs-alignment for the lone
  survivor.
- **Trade-frequency interaction with audit-only classification**:
  The candidate's trade counts (19 / 23 / 27 / 29) are at the lower
  end of viable population for the AND-gate's `total_trades ≥ 5`
  threshold. Audit-only classification correlates with lower
  walk-forward trade frequency in this candidate; whether the
  correlation generalizes across the audit-only cohort is not
  determined by this evidence base.

The audit-only partition origin is observed; the mechanism that
produces it — classifier mis-coverage versus selection-effect noise
versus trade-frequency interaction — is not adjudicated by PHASE2C_8.1's
evidence base. Per spec §10.7 out-of-scope statements, mechanism
adjudication is not part of PHASE2C_8.1's implementation surface;
the observation is surfaced; mechanism adjudication is bounded to
the population-level pattern.

### 6.4 Bounds on what this finding establishes

The lone-survivor finding does not extend to claims the evidence
cannot support:

- **No statistical-significance claim**: 1-of-198 cohort_a
  cardinality at unfiltered tier is consistent with both real
  cross-regime structure and population-level random alignment.
  Without DSR / PBO / CPCV or other multiple-comparisons correction
  infrastructure (deferred per spec §10.7 + Q-B4 territory; see §9
  methodology-evidence hierarchy), no significance claim about the
  candidate is defensible.
- **No deployability claim**: A candidate passing four regimes at
  permissive AND-gate calibration with one regime of substantive
  negative return is not equivalent to a deployment-quality strategy
  signal. Deployment-time inference about strategy selection is
  out-of-scope for PHASE2C_8.1's evaluation per spec §10.7.
- **No mechanism claim about audit-only origin**: The audit-only
  partition origin is observed; whether it reflects walk-forward
  classifier mis-coverage, selection-effect noise, trade-frequency
  interaction, or some combination is not adjudicated by this
  evidence base.

### 6.5 Tracked-fix register entries surfaced from §6

Two register entries surface from §6 drafting (folded at §10
tracked-fix register):

- **Q-S4-11**: lone survivor scenario interpretation. Resolution:
  hybrid 4-bullet narration per §6.2 above; no forced (a/b/c) clean
  categorical assignment; observed-mechanism-not-adjudicated
  framing per §6.3 + §6.4 third bullet.
- **Q-S4-13**: gate calibration methodology question raised by
  eval_2021_v1 negative-return-passes pattern (§6.2 observation iii).
  The 4-criterion AND-gate inherited from PHASE2C_7.1 calibration
  baseline accepts a -10.2% return as passing when accompanied by
  within-threshold sharpe / max_drawdown / trade count. The candidate
  passes the AND-gate as the gate is currently calibrated; the
  methodology question is whether the calibration thresholds (return
  ≥ -0.15; sharpe ≥ -0.5; max_drawdown ≤ 0.25) are appropriate for
  multi-regime evaluation contexts where per-regime negative returns
  affect cross-regime survival interpretation. PHASE2C_8.1's evidence
  does not establish the AND-gate calibration as defective; the
  observation surfaces a calibration question, not a calibration
  finding. Per spec §10.7 out-of-scope statements, calibration
  variation (Q-B2 territory) is out-of-scope for PHASE2C_8.1; surface
  the question explicitly.

### 6.6 Verification chain backing

The per-regime metrics narrated in §6.1 are extracted directly from
the four producer `holdout_results.csv` files at canonical paths
(full chain documentation in §8). The same CSVs are read by the
permanent in-repo independent-recompute gate at
`tests/test_phase2c_8_1_independent_recompute.py`, which verifies
the cohort_a_unfiltered membership (`["0845d1d7898412f2"]`) and
cohort_a_filtered cardinality (0) byte-identically against the
production comparison pipeline output. The lone survivor's identity
and per-regime metrics are verified at three independent verification
layers; the hybrid narration in §6.2 stands on the verified
empirical foundation.

## 7. Theme-level cross-regime patterns

### 7.0 Theme distribution

The 198-candidate population partitions across 5 themes per the
PHASE2C_5 proposal-theme rotation (calendar_effect, mean_reversion,
momentum, volatility_regime, volume_divergence). Theme allocation
across the batch is near-uniform: 40/40/40/39/39 per theme; theme
assignment is metadata carried forward from the PHASE2C_5 candidate
generation cycle. The theme distribution is documented at
`docs/phase2c/PHASE2C_8_1_PLAN.md` §3 + spec-level cross-reference;
this section reports per-theme cross-regime pass counts as factual
basis without mechanism interpretation.

### 7.1 Theme-level AND-gate pass counts (unfiltered tier)

Per-theme AND-gate pass counts at unfiltered tier across all 4
regimes:

| Theme | Total | bear_2022 | validation_2024 | eval_2020_v1 | eval_2021_v1 |
|---|---|---|---|---|---|
| calendar_effect | 40 | 6 | 24 | 26 | 10 |
| volume_divergence | 40 | 4 | 25 | 23 | 12 |
| volatility_regime | 40 | 0 | 4 | 10 | 2 |
| momentum | 39 | 3 | 21 | 12 | 6 |
| mean_reversion | 39 | 0 | 13 | 3 | 8 |

The numbers are extracted from the four producer
`holdout_results.csv` files at canonical paths; per-theme
aggregations are computed from per-candidate `theme` field +
per-regime `holdout_passed` flag (verified at three independent
verification layers per §8).

### 7.2 Cross-regime theme-level observations

Three factual cross-regime observations from the per-theme pass-
count table (no mechanism interpretation; observations limited to
the data documented at §7.1):

**Observation A — bear_2022 pass rates are uniformly low across
themes**: maximum theme pass count in bear_2022 is 6/40 (calendar_effect);
volatility_regime and mean_reversion show 0/40 and 0/39 zero-pass
counts. The bear_2022 regime's overall pass count of 13/198 (§3.3)
distributes across calendar_effect + volume_divergence + momentum
(6+4+3 = 13); volatility_regime + mean_reversion contribute zero.

**Observation B — validation_2024 pass rates are highest across
themes**: maximum theme pass count in validation_2024 is 25/40
(volume_divergence). The validation_2024 regime's overall pass
count of 87/198 (§3.3) is well-distributed: calendar_effect 24,
volume_divergence 25, momentum 21, mean_reversion 13, volatility_regime
4.

**Observation C — eval_2020_v1 vs eval_2021_v1 pass-rate divergence**:
the two train-overlap regimes (both `in_sample_caveat_applies = true`
per spec §7.4) produce different per-theme pass counts. eval_2020_v1's
overall pass count is 74/198 with theme distribution skewed toward
calendar_effect (26) + volume_divergence (23); eval_2021_v1's overall
pass count is 38/198 with more even theme distribution (12 / 10 /
8 / 6 / 2). Within-train-overlap pass-rate heterogeneity is observed
at theme-level cross-tab.

The observations are factual cross-regime cardinality reports;
mechanism interpretation (why a theme passes more in one regime
than another) is not in scope for §7. The in-sample-caveat
asymmetry interpretation (population-level train-overlap vs fully-
out-of-sample asymmetry) is at §5; per-theme mechanism-relevant
prose is out-of-scope per spec §10.7.

### 7.3 Lone survivor theme connection

The lone unfiltered cross-regime survivor `0845d1d7898412f2` (§6) is
of theme `volume_divergence`. The volume_divergence theme's
unfiltered AND-gate pass counts per regime are 4 / 25 / 23 / 12;
the lone survivor passes the AND-gate in all 4 regimes but is one
of only 4 volume_divergence candidates passing in bear_2022.

This is a factual cross-section reference between §7 and §6 (the
lone-survivor's theme is volume_divergence; volume_divergence has
distinct per-regime pass count profile). The lone-survivor's
identity within the volume_divergence theme is documented at §6;
the volume_divergence theme's pass-count profile is documented at
§7.1; the cross-section linkage is at this sub-section. No
interpretation register beyond the factual cross-section reference.

### 7.4 Forward references

§7 documents theme-level pass-count cross-tabs as factual basis;
mechanism interpretation is not in scope. The in-sample-caveat
asymmetry interpretation (cross-regime evidentiary-category
asymmetry) is at §5. The lone-survivor characterization (candidate-
level hybrid narration) is at §6. Per-regime cardinalities at §7.1
are cross-tab-consistent with per-regime totals at §3.3 (both
should sum to the same per-regime totals; verified by construction).

The theme-level pass counts at §7.1 are verified at three independent
verification layers (full chain documentation at §8); the production
comparison pipeline emits per-candidate theme metadata in
`comparison_matrix.csv` at the same canonical path that backs §3
+ §5 + §6 cross-references.

## 8. Verification chain

### 8.0 Three-layer verification structure

PHASE2C_8.1's canonical findings are verified at three independent
verification layers. Each layer reads producer artifacts at canonical
paths and computes (or asserts) the same canonical numbers via a
different code path. Cross-layer agreement on canonical numbers
(byte-identical reproduction) is the verification chain's load-bearing
property: the chain is robust to defects local to any single layer
because two parallel layers exist for cross-checking.

The three layers, in order of independence from the production
pipeline:

- **Layer 1 — Production comparison pipeline**: emits canonical
  comparison artifacts; carries 32 unit + integration tests in
  `tests/test_compare_multi_regime.py`.
- **Layer 2 — Codex adversarial review independent recomputation**:
  one-time external check at adversarial-review cycle; recomputed
  canonical numbers from source CSVs via Codex's independent code
  path.
- **Layer 3 — Permanent in-repo independent-recompute gate**:
  `tests/test_phase2c_8_1_independent_recompute.py` recomputes
  canonical numbers via stdlib `csv` only on every CI run; zero
  source-code overlap with Layer 1.

### 8.1 Layer 1 — Production comparison pipeline

The production pipeline at `scripts/compare_multi_regime.py` (commit
`da1859d`; hardened at commit `018d876`) builds the n-way
candidate-aligned comparison matrix from the four producer regime
artifact directories. Producer-side artifact emission is at
`scripts/run_phase2c_evaluation_gate.py` (per-regime per-candidate
JSON + per-regime `holdout_results.csv` + lineage attestation).
Filter-tier artifact emission is at
`scripts/filter_evaluation_gate.py` (per-regime ≥20-trade
filtered subdirectory).

The production pipeline's comparison output:
- `data/phase2c_evaluation_gate/comparison_2022_2024_2020_2021_v1/comparison_matrix.csv`
  (199 rows = 1 header + 198 candidates × 25 columns)
- `data/phase2c_evaluation_gate/comparison_2022_2024_2020_2021_v1/comparison_summary.json`
  (cohort categorization + pass-count distribution + in-sample-caveat
  stratification + per-regime metadata + lineage attestation)

Layer 1 test coverage at `tests/test_compare_multi_regime.py`
(32 tests; 19 original + 13 added at commit `018d876` as part of
Q-S4-6/Q-S4-8 hardening response to Codex adversarial review):

- TestResolveRegimeMetadata (5 tests): regime metadata resolution
- TestPerCandidateRowNWay (3 tests): per-candidate row construction
- TestCohortCategorization (4 tests): cohort categorization correctness
- TestInSampleCaveatStratification (2 tests): caveat stratification
- TestCliFlagParsing (4 tests): CLI parsing
- TestIntegrationN4OnDisk (1 test): end-to-end against canonical
  paths with pinned canonical numbers (cohort_a_unfiltered ==
  ["0845d1d7898412f2"]; cardinality (1, 0); cohort_c == 76;
  pass-count distribution unfiltered/filtered; 21-vs-8 caveat
  stratification)
- TestLoaderStrictness (6 tests): convention-skip preservation +
  raise on missing summary / missing hypothesis_hash / duplicate
  hash / cardinality mismatch
- TestExpectedCountFromResultsCsv (3 tests): CSV row-count
  derivation
- TestApplyMultiRegimeFailurePaths (4 tests): universe mismatch +
  filtered-subset violation + cardinality mismatch + malformed
  candidate JSON

### 8.2 Layer 2 — Codex adversarial review

Codex adversarial review at the implementation arc's hardening
cycle independently recomputed canonical numbers from source CSVs
using a different code path than the production pipeline. The
review verdict was `needs-attention` (not blocked); two findings
were surfaced:

- **Q-S4-6 (HIGH)**: loader silent-skip in `_load_run_artifacts`
  could allow producer regressions to silently propagate. Closed
  at commit `018d876` (loader strictness tightened: raise on
  missing `holdout_summary.json` and missing `hypothesis_hash`
  field for non-convention candidate dirs; added `expected_count`
  parameter for cardinality assertion).
- **Q-S4-8 (MEDIUM)**: integration test did not pin canonical
  numbers. Closed at commit `018d876` (canonical-number pins
  added at `TestIntegrationN4OnDisk.test_4_regime_e2e_produces_198_rows`
  + 13 synthetic-failure-path tests added).

Codex independently recomputed all canonical findings (cohort_a=1;
cohort_c=76; pass-count distribution; 21-vs-8 caveat stratification)
from source CSVs and confirmed byte-identical agreement with
production pipeline output. The verification was a one-time external
check; Layer 3 converts the same recomputation into a permanent
in-repo verification gate.

### 8.3 Layer 3 — Permanent in-repo independent-recompute gate

The independent-recompute gate at
`tests/test_phase2c_8_1_independent_recompute.py` (commit `8086adf`)
reads the four producer `holdout_results.csv` files directly using
stdlib `csv` only. Zero source-code overlap with the production
pipeline (`scripts/compare_multi_regime.py`); the gate cannot share
defects with Layer 1 because it does not import any module Layer 1
depends on.

Layer 3 implementation: 304 lines; stdlib only (`csv`, `pathlib`).
Defensive layers:
- Per-regime CSV row-count assertions (universe-size drift
  detection; expected counts pinned: bear_2022 unfiltered/filtered
  198/146; validation_2024 198/144; eval_2020_v1 198/140;
  eval_2021_v1 198/144)
- Universe symmetry assertion across 4 unfiltered regimes (must
  hold by construction)
- Per-candidate pass-count recomputation (independent of Layer 1)
- Cohort cardinality + pass-count distribution + in-sample-caveat
  stratification recomputation

Layer 3 test count: 7 canonical-finding assertions, each emitting
informative failure messages naming the changed canonical number
+ corrective action:
- universe cardinality 198
- cohort_a_unfiltered == ["0845d1d7898412f2"]
- cohort_a_filtered == []
- cohort_c_unfiltered cardinality == 76
- pass_count_distribution unfiltered == {0:76, 1:55, 2:45, 3:21, 4:1}
- pass_count_distribution filtered == {0:87, 1:58, 2:38, 3:15, 4:0}
- 21-vs-8 in-sample-caveat asymmetry
  (n_passing_all_train_overlap=21; n_passing_all_fully_out_of_sample=8)

Layer 3 runs in CI on every change; future regressions to the
production comparison pipeline that produce self-consistent-but-
wrong canonical numbers are caught because Layer 3 computes from a
different code path.

### 8.4 Cross-layer canonical-number agreement

Canonical findings reproduce byte-identically across all three
verification layers (excluding `produced_at_utc` timestamp in
JSON). The agreement was verified empirically at the commit `018d876`
hardening cycle: regenerated comparison artifacts to `/tmp` via
production pipeline; diffed against canonical artifacts at
`data/phase2c_evaluation_gate/comparison_2022_2024_2020_2021_v1/`;
result was byte-identical CSV + byte-identical JSON (excluding
timestamp).

Layer 3's 7 assertions reproduce the same canonical numbers via
independent code path; production tests + independent-recompute
gate together demonstrate cross-layer agreement on the same data
set.

### 8.5 Test count at implementation arc closure

Full project test suite at PHASE2C_8.1 implementation arc closure
(commit `8086adf`): **1400 / 1400 tests green**. The verification-
chain hardening cycle's contributions are verified:

- Step 4 hardening commit `018d876` produced 1393 / 1393 tests green;
  added 13 new tests across 3 classes (TestLoaderStrictness 6 tests
  + TestExpectedCountFromResultsCsv 3 tests + TestApplyMultiRegimeFailurePaths
  4 tests) per Q-S4-6/Q-S4-8 hardening response.
- Independent-recompute-gate commit `8086adf` produced 1400 / 1400
  tests green; added 7 new tests (TestPhase2c81IndependentRecompute
  with 7 canonical-finding assertions per §8.3).

The 1400 → 1393 → +7 arithmetic confirms Layer 3's gate addition
is the only contribution at the `8086adf` commit; full chain
verification at the implementation arc closure passes.

### 8.6 Verification chain methodology principle

The three-layer verification chain operationally instantiates the
parallel-implementation-verification methodology principle (Q-S4-10
register entry; codification candidate for the closeout-commit
cycle). The principle: independent-implementation verification
tests have different epistemic standing than snapshot tests against
the same code path. Layer 3's stdlib-only constraint is the load-
bearing property — by sharing no code with Layer 1, defects local
to Layer 1 cannot mask Layer 3's verification. The verification
chain is genuinely additive, not redundant.

### 8.7 Forward references

§8 documents the verification machinery that backs canonical findings
narrated at §1 + §3 + §5 + §6. Each load-bearing-cluster section
references §8 briefly with forward-pointer ("(full chain documentation
in §8)" pattern at §5.5 + §6.6 + §1.1). §10 register entries Q-S4-10
(parallel-implementation methodology codification) and Q-S4-14
(bidirectional dual-reviewer pattern codification) are
methodology-codification candidates emerging from PHASE2C_8.1 work
that touch the verification chain documented at §8 directly.

## 9. Methodology-evidence hierarchy bounds

### 9.0 Section purpose

§9 documents the methodology-evidence hierarchy that PHASE2C_8.1's
4-regime evaluation operates within. §1.2 + §5.4 + §6.4 apply
specific bounds to specific findings (verdict synthesis / 21-vs-8
asymmetry / lone-survivor characterization respectively); §9
consolidates the underlying methodology-evidence register as
standalone documentation. The four anchors below are not re-bounds
of specific findings; they are the methodology-evidence framework
within which all PHASE2C_8.1 findings should be read.

### 9.1 What PHASE2C_8.1 establishes

PHASE2C_8.1's evaluation produces three classes of findings, each
at the evidence register the methodology supports:

- **Population-level cardinalities**: cohort_a_unfiltered = 1;
  cohort_a_filtered = 0; cohort_c = 76; pass-count distributions
  per tier. These are direct counts derived from per-candidate
  AND-gate evaluation across 4 regimes; the evidence register is
  empirical-cardinality.
- **Population-level asymmetry**: 21-vs-8 in-sample-caveat
  stratification (n_passing_all_train_overlap = 21;
  n_passing_all_fully_out_of_sample = 8). The evidence register is
  population-level pattern observation; the asymmetry direction
  matches Concern A (spec §7.4 + §10.6) prediction.
- **Candidate-level identification**: hypothesis hash
  `0845d1d7898412f2` as lone unfiltered cross-regime survivor;
  per-regime evaluation profile + theme + audit-only partition
  origin documented at §6. The evidence register is
  identification-level (which specific candidate; what its profile
  shows), not significance-level (whether the candidate's profile
  is statistically distinct from null).

The three finding classes share a common evidence register:
empirically-derived cardinalities and patterns observable from
direct evaluation outputs; verified at three independent
verification layers per §8. The methodology produces filtering
(which candidates clear which thresholds in which regimes) and
stratification (how findings distribute across evidentiary
categories), not significance testing.

### 9.2 What the methodology cannot establish without DSR / PBO / CPCV

The methodology-evidence hierarchy is bounded by the absence of
multiple-comparisons-corrected significance machinery. Per spec
§10.7, Deflated Sharpe Ratio (DSR), Probability of Backtest
Overfitting (PBO), and Combinatorially Purged Cross-Validation
(CPCV) infrastructure is out-of-scope for PHASE2C_8.1; deferred to
follow-up scoping (PHASE2C_8.0 §5 Q-B4 territory).

Without this infrastructure, the methodology cannot distinguish:

- Whether a candidate's cross-regime survival reflects real
  cross-regime signal versus population-level random alignment.
  With 198 candidates × 4 regimes = 792 unadjusted candidate-regime
  evaluations under permissive AND-gate calibration, the cardinality
  distributions are consistent with both interpretations;
  significance testing under multiple-comparisons correction is
  required to adjudicate.
- Whether a population-level pattern (e.g., the 21-vs-8 asymmetry)
  exceeds chance variation. The asymmetry's direction is
  qualitatively consistent with the in-sample caveat prediction;
  whether the magnitude exceeds null-hypothesis variance under
  permissive AND-gate calibration is a question DSR / PBO / CPCV
  would address but PHASE2C_8.1's machinery does not.
- Whether per-candidate or per-regime claims meet significance
  thresholds at any conventional level. Per-strategy claims about
  edge or robustness are not defensible from this evidence base;
  the methodology produces filtering, not significance certification.

The bound is not a methodology defect — it is the methodology's
intrinsic register. PHASE2C_8.1's scope per spec §10.7 explicitly
excludes DSR / PBO / CPCV infrastructure; the closeout's findings
operate at the register the included machinery supports.

### 9.3 Why cohort_a_filtered = 0 constrains strategy claims

The cohort_a_filtered = 0 finding documented at §3 and characterized
at §6 is structurally consequential for strategy-evidence claims.
Zero candidates survive all 4 regimes at the trade-count-filtered
tier. At face value, this is the strongest possible falsification
register for "robust cross-regime strategy" claims from PHASE2C_8.1's
198-candidate population.

The constraint operates at three levels:

- **Direct constraint**: no candidate has demonstrated cross-regime
  AND-gate passage with adequate trade-frequency floor in all 4
  regimes simultaneously. Strategy claims requiring cross-regime
  robustness with trade-frequency floor are unsupported by direct
  evidence at PHASE2C_8.1 scope.
- **Bounded constraint**: the lone unfiltered survivor's exclusion
  from cohort_a_filtered hinges on a single-trade margin in
  bear_2022 (19 trades vs ≥20 threshold; §6.2). The structural
  collapse claim is bounded by this margin; cohort_a_filtered = 0
  is real-and-precarious rather than real-and-robust.
- **Calibration-question constraint**: the AND-gate calibration
  permissively admits a candidate with -10.2% return in eval_2021_v1
  (§6.2 observation iii); cohort_a_unfiltered = 1 may itself reflect
  permissive calibration rather than substantively-strong cross-
  regime signal. Q-S4-13 surfaces the calibration question; the
  constraint on strategy claims tightens further if the calibration
  question resolves toward stricter thresholds.

The cohort_a_filtered = 0 finding is neither pure-collapse evidence
("no strategies work") nor pure-fragility evidence ("nothing's
robust"); it is constraint-level evidence operating at three nested
register levels. Strategy claims at PHASE2C_8.1 scope must operate
within these constraints.

### 9.4 Why 21-vs-8 is evidence of caveat bias but not causal proof

The 21-vs-8 in-sample-caveat asymmetry documented at §5 operates at
the population-level pattern register. The asymmetry direction
(train-overlap pass rate > fully-out-of-sample pass rate) matches
Concern A's prediction (candidate-screening artifacts inflating
pass rates against train-overlap regimes); the magnitude is
observable at population level.

The asymmetry establishes evidence for in-sample caveat bias. It
does not establish causal proof of overfitting at any specific
candidate. The distinction operates at three levels:

- **Direction-consistency-not-proof**: the asymmetry direction
  matches Concern A's prediction, but direction-consistency at
  population level does not adjudicate causal mechanism at
  candidate level. Some of the 21 train-overlap-passers may pass
  on real cross-regime structure; some of the 8 fully-out-of-
  sample-passers may fail train-overlap evaluation from sample-
  size variance rather than mechanism-relevant absence.
- **Magnitude-observation-not-significance**: the 21:8 ratio
  (≈2.6×) is observable; whether it exceeds null-hypothesis
  variance under permissive AND-gate calibration is a significance
  question DSR / PBO / CPCV would address but the methodology does
  not. The asymmetry's magnitude is empirical, not significance-
  certified.
- **Asymmetry-pattern-not-mechanism-adjudication**: the asymmetry
  is consistent with multiple mechanisms (candidate-screening
  artifacts; walk-forward sub-window insufficiency; sample-size
  interaction; combinations). PHASE2C_8.1's evidence does not
  adjudicate which mechanism produces the observed asymmetry; per
  spec §10.7, mechanism investigation is out-of-scope.

The asymmetry is observable; its direction matches caveat
prediction; its causal interpretation requires additional
infrastructure not present at this scope. The closeout narrates the
asymmetry as evidentiary observation, not as caveat-bias
falsification or proof.

### 9.5 Forward references

§9 documents the methodology-evidence hierarchy as standalone
register; specific findings bounded against this hierarchy at
§1.2 (synthesis) + §5.4 (population-level finding) + §6.4
(candidate-level finding). §10 register entries Q-S4-7 (DSR-
deferred bound) and Q-S4-13 (calibration methodology question)
are tracked-fix codifications of methodology-evidence hierarchy
limits surfaced during PHASE2C_8.1 evaluation; their resolution is
out-of-scope per spec §10.7.

The methodology-evidence hierarchy framing at §9 is the load-
bearing methodology-limit register for PHASE2C_8.1. Future readers
encountering specific PHASE2C_8.1 findings should read those
findings within the §9 hierarchy: empirically-derived cardinalities
and patterns observable from direct evaluation outputs at three
verification layers; significance, mechanism, and per-candidate
deployability questions deferred to future arcs with appropriate
infrastructure.

## 10. Tracked-fix register

### 10.0 Register framing

The PHASE2C_8.1 work cycle produced ten tracked-fix register
entries (Q-S4-5 through Q-S4-16, with gaps). The entry count is
larger than prior closeout cycles (PHASE2C_7.1 closeout had ~3-4
register entries at equivalent stage). The expansion reflects the
discipline pattern operating at finer granularity, not methodology
breakdown — six mid-cycle empirical-verification catches and four
distinct codification candidates were surfaced during Step 5
drafting itself, beyond the implementation-arc-derived entries.

Each entry below records: status (current state of the entry's
resolution); resolution (what action was taken or is deferred);
verdict impact (whether the entry affects PHASE2C_8.1's verdict
register); codification candidate (whether the entry warrants
METHODOLOGY_NOTES update at closeout-commit cycle).

### 10.1 Register table

| Entry | Status | Resolution | Verdict impact | Codification candidate |
|---|---|---|---|---|
| Q-S4-5 | Resolved at closeout drafting | Steps 2/3 commit messages cited bear_2022 7.6% (15/198) and validation_2024 21.7% (43/198) numbers that diverge from disk-canonical (6.6% / 43.9%). Closeout cites disk-canonical values per METHODOLOGY_NOTES §6 (commit messages are not canonical result layers); commits are not amended. | None — disk-canonical values used in closeout prose; commit-message divergence is procedural-not-substantive. | No (procedural; existing METHODOLOGY_NOTES §6 covers the principle). |
| Q-S4-7 | Surfaced as methodology-evidence bound | Statistical-significance machinery (DSR / PBO / CPCV) is out-of-scope per spec §10.7; deferred to Q-B4 follow-up scoping. PHASE2C_8.1's findings operate at population-level pattern register, not per-strategy significance register. | Bounds the verdict — see §1.2 + §5.4 + §6.4 + §9.2. The verdict is constrained by this bound; no claim made that this evidence base could not support. | No (the bound is intrinsic to PHASE2C_8.1's scope; future arc with DSR/PBO/CPCV machinery will register the bound's resolution). |
| Q-S4-9 | Verified at §2 drafting cycle | Spec §7.5 declaration of `in_sample_caveat_applies` semantics matches `compare_multi_regime.py:_resolve_regime_metadata` implementation via the schema discriminator chain. Alignment verified at §2.5 drafting cycle without defect; entry remains documented as verification action with documented result. | None — alignment confirmed; methodology semantic integrity holds. | No (verification action complete; no methodology codification needed). |
| Q-S4-10 | Codification candidate | Parallel-implementation verification principle: independent-implementation verification tests (Layer 3 in §8) have different epistemic standing than snapshot tests against the same code path. The verification chain at three layers (§8) operationally instantiates the principle; codification candidate for METHODOLOGY_NOTES update at closeout-commit cycle. | None — methodology principle, not finding bound. | Yes (separate METHODOLOGY_NOTES update commit candidate per 76e46d4 precedent vs fold into closeout commit per D-S5-2 deferred decision). |
| Q-S4-11 | Resolved at §6 drafting | Lone survivor `0845d1d7898412f2` scenario interpretation. Original (a/b/c) framing inadequate; hybrid 4-bullet narration applied at §6.2 (survives all 4 unfiltered + filtered exclusion off-by-1 + permissive AND-gate accepts -10.2% return + audit-only partition origin). | None directly — characterization-level finding folded at §6 prose; verdict bounded at §1.2 + §6.4. | No (characterization-level finding; no methodology codification needed). |
| Q-S4-12 | Pending closeout-commit cycle | CLAUDE.md Phase Marker reconciliation per `feedback_claude_md_freshness.md` user-memory rule. Phase Marker currently does not reflect PHASE2C_8.0 scoping or PHASE2C_8.1 spec/implementation/closeout. Resolution: fold CLAUDE.md update into closeout commit per D-S5-4 adjudication (escape hatch: separate commit if edit grows beyond phase-marker/state reconciliation). | None directly — operational continuity; future Claude sessions read updated CLAUDE.md correctly. | No (existing `feedback_claude_md_freshness.md` codifies the principle). |
| Q-S4-13 | Surfaced as methodology question | Calibration methodology question raised by eval_2021_v1 negative-return-passes pattern (-10.2% return + within-threshold sharpe / max_drawdown / trade count → AND-gate accepts as passing per inherited PHASE2C_7.1 calibration). The candidate passes the AND-gate as currently calibrated; whether the calibration thresholds are appropriate for multi-regime evaluation contexts is a methodology question. Calibration variation (Q-B2 territory) is out-of-scope per spec §10.7. | Bounds the verdict — surfaces a calibration question that, if answered with stricter thresholds, would tighten constraints on cohort_a cardinality interpretation (see §9.3 third constraint level). | No directly (PHASE2C_8.1 evidence does not establish calibration as defective; methodology question, not codification candidate). |
| Q-S4-14 | Codification candidate | Bidirectional dual-reviewer register-precision pattern: register-precision verification at high-load drafting cycles operates as bidirectional dual-reviewer check, not directive arbitration. Each reviewer (ChatGPT structural / Claude advisor structural-with-register-overlay) has different sensitivities at different axes; both checks must fire before sealing. Distinct from directive arbitration at non-register sealing decisions. | None — methodology process observation, not empirical finding. | Yes (codification candidate for METHODOLOGY_NOTES update at closeout-commit cycle; structurally distinct from Q-S4-10 / Q-S4-15 / Q-S4-16). |
| Q-S4-15 | Codification candidate | Per-section cross-reference grep checklist enrichment: full-assembly verification's canonical-number checklist needs explicit per-section cross-reference grep, not just top-level numerical-claim grep. Eleven cross-section observations (VVVV through FFFFF) accumulated across drafting cycles; pattern indicates per-section grep is structurally load-bearing for full-assembly canonical-number consistency. | None directly — closeout-assembly methodology refinement, not finding bound. | Yes (codification candidate as METHODOLOGY_NOTES §11 closeout-assembly-checklist sub-discipline at closeout-commit cycle). |
| Q-S4-16 | Operationalized and codification candidate | Anchor-list empirical-verification discipline: advisor-supplied numerical or structural anchors require pre-drafting verification before prose. Six mid-cycle empirical-verification catches at Step 5 (§3.3 cardinality / §2.5 cross-section semantics / §8.5 historical detail / §7 speculative cardinalities / §9 section-count audit / §1.2-§5.4-§6.3-§6.4 cross-section terminology) operationally validated the discipline. Cross-section terminology fix at D-S5-8 was first explicit operationalization. | None directly — methodology-process discipline; affects future drafting cycles' register-precision quality. | Yes (codification candidate for METHODOLOGY_NOTES update at closeout-commit cycle; operationalized status distinguishes from purely-codification-candidate Q-S4-10/Q-S4-14/Q-S4-15). |

### 10.2 Codification-candidate clustering

Four entries are codification candidates (Q-S4-10 / Q-S4-14 /
Q-S4-15 / Q-S4-16); the remaining six are not. The four candidates
share structural common ground — all are methodology-process
principles surfaced from PHASE2C_8.1 work cycle that may warrant
METHODOLOGY_NOTES update at closeout-commit cycle:

- **Q-S4-10**: parallel-implementation verification principle
- **Q-S4-14**: bidirectional dual-reviewer register-precision pattern
- **Q-S4-15**: per-section cross-reference grep checklist enrichment
- **Q-S4-16**: anchor-list empirical-verification discipline (already
  operationalized)

The four candidates are not equivalent: Q-S4-16's status is
operationalized-and-codification-candidate (D-S5-8 was first
operational demonstration); the other three remain purely-
codification-candidates pending METHODOLOGY_NOTES update.
Whether the four codifications fold into a single update commit
(76e46d4 precedent) or separate commits depends on cross-reference
density at closeout-commit cycle (D-S5-2 deferred decision).

### 10.3 Verdict impact summary

Two entries directly bound the verdict register: Q-S4-7
(statistical-significance machinery deferral) and Q-S4-13
(calibration methodology question with constraint-tightening
potential). The remaining eight entries do not bound the verdict;
they record verification actions, characterization-level findings,
operational-continuity actions, or methodology-process
codification candidates.

The verdict register at §1 is constrained by Q-S4-7's
methodology-evidence hierarchy bound (per §9.2) and tightened by
Q-S4-13's calibration-question constraint level (per §9.3).
Both bounds are operationalized at the verdict register; no
register entry surfaces a finding the verdict has not already
bounded.

### 10.4 Forward references

§10's register entries are referenced operationally throughout the
closeout: Q-S4-5 at §1 verdict register; Q-S4-7 at §1.2 + §5.4 +
§6.4 + §9.2 bounds; Q-S4-9 at §2.5; Q-S4-10 at §8.6; Q-S4-11 at
§6.2; Q-S4-13 at §6.5 + §9.3; Q-S4-14 at §1.4. The four
codification candidates (Q-S4-10/14/15/16) feed forward to
closeout-commit-cycle METHODOLOGY_NOTES update decision per D-S5-2.
Q-S4-12 (CLAUDE.md reconciliation) feeds forward to closeout-commit
cycle per D-S5-4. Q-S4-15's per-section cross-reference grep
discipline applies at full-assembly verification cycle.

## 11. Forward signals

### 11.0 Section purpose

§11 surfaces forward signals from PHASE2C_8.1's evidence base —
methodology questions, empirical observations, and codification
candidates that carry forward as open questions rather than as
resolutions or commitments. Per spec §10.7 + Q-FS4 strictness,
selection of next implementation arc is post-PHASE2C_8.1 closure
and is not pre-named at this section.

Each forward signal below anchors at an empirical finding or
register entry already documented in this closeout. None of the
signals are framed as recommendations or as next-arc commitments;
they are forward-pointing observations from the work cycle that
warrant adjudication at future scoping decisions.

### 11.1 DSR / PBO / CPCV machinery deferral

The methodology-evidence hierarchy bound at §9.2 + §1.2 + §5.4 +
§6.4 (all citing Q-S4-7) is the load-bearing methodology-limit
forward signal: PHASE2C_8.1 produces population-level cardinalities
and patterns observable at the verification chain's three layers
(§8); per-strategy or per-regime statistical-significance claims
are not defensible without DSR / PBO / CPCV infrastructure deferred
per spec §10.7 (Q-B4 territory).

The forward signal is the bound itself. Distinguishing whether
cohort_a_unfiltered = 1 reflects real cross-regime signal versus
population-level random alignment, whether the 21-vs-8 asymmetry
exceeds null-hypothesis variance, and whether per-candidate
profiles meet conventional significance thresholds — these are
adjudicable only with multiple-comparisons-corrected significance
machinery. PHASE2C_8.1's evidence does not adjudicate these
questions; future scoping decisions adjudicate when DSR / PBO /
CPCV infrastructure becomes scope-appropriate.

### 11.2 Gate-calibration methodology question (Q-S4-13)

The eval_2021_v1 negative-return-passes observation at §6.2 (the
lone survivor's -10.2% return passing the AND-gate as currently
calibrated) surfaces a calibration methodology question registered
at Q-S4-13. The 4-criterion AND-gate inherited from PHASE2C_7.1's
calibration baseline (sharpe ≥ −0.5; max_drawdown ≤ 0.25; total_return
≥ −0.15; total_trades ≥ 5) accepts the candidate as passing; whether
this calibration is appropriate for multi-regime evaluation contexts
where per-regime negative returns affect cross-regime survival
interpretation is the open question.

The forward signal is the question, not its answer. PHASE2C_8.1
evidence does not establish the AND-gate calibration as defective;
the observation surfaces a calibration question that is out-of-scope
per spec §10.7 (Q-B2 calibration variation territory). If the
question is adjudicated toward stricter thresholds at future scoping,
constraints on cohort_a cardinality interpretation tighten further
(see §9.3 third constraint level).

### 11.3 Audit-only partition implication (§6.3)

The lone unfiltered cross-regime survivor's audit-only partition
origin (`wf_test_period_sharpe = -0.072 < 0.5` primary threshold;
§6.1 + §6.3) is consistent with multiple mechanisms — walk-forward
classifier mis-coverage, selection-effect amplification, trade-
frequency interaction. PHASE2C_8.1 evidence does not adjudicate
which mechanism applies (§9.4 mechanism adjudication bound).

The forward signal is the methodology question: walk-forward
prequalification's coverage of cross-regime survival quality is
not directly tested by PHASE2C_8.1 scope. If walk-forward
classification systematically excludes candidates with cross-regime
profiles that survive multi-regime evaluation, the prequalification
methodology has a coverage gap; if the audit-only origin is
selection-effect amplification across the larger n=154 audit-only
sample versus n=44 primary, the observation reflects sample-size
arithmetic rather than methodology gap. The mechanism adjudication
is a methodology research direction surfaced from PHASE2C_8.1
evidence; it is not pre-named as future-arc commitment.

### 11.4 Methodology-process codification candidates (Q-S4-10 / Q-S4-14 / Q-S4-15 / Q-S4-16)

Four methodology-process principles surfaced from PHASE2C_8.1 work
cycle warrant METHODOLOGY_NOTES update consideration at closeout-
commit cycle:

- **Parallel-implementation verification** (Q-S4-10; §8.6): independent-
  implementation tests have different epistemic standing than
  snapshot tests against the same code path; the three-layer
  verification chain operationally instantiates the principle.
- **Bidirectional dual-reviewer register-precision** (Q-S4-14; §1.4):
  register-precision verification operates as bidirectional dual-
  reviewer check, not directive arbitration; both reviewers'
  checks must fire before sealing.
- **Per-section cross-reference grep checklist enrichment**
  (Q-S4-15): full-assembly verification's canonical-number checklist
  needs explicit per-section cross-reference grep, not just
  top-level numerical-claim grep; eleven cross-section observations
  (VVVV-FFFFF) accumulated across drafting cycles support the
  codification.
- **Anchor-list empirical-verification discipline** (Q-S4-16):
  advisor-supplied numerical or structural anchors require pre-
  drafting verification; six mid-cycle empirical-verification
  catches at Step 5 (§3.3 / §2.5 / §8.5 / §7 / §9 section-count /
  §1.2-§5.4-§6.3-§6.4 cross-section terminology) operationally
  validated the discipline.

The four codifications are not equivalent: Q-S4-16 is operationalized-
and-codification-candidate (D-S5-8 was first explicit demonstration);
the other three remain purely-codification-candidates pending update.
Whether the four fold into a single METHODOLOGY_NOTES update commit
(76e46d4 precedent) or separate commits is the D-S5-2 deferred
decision; both options remain open at this closeout.

### 11.5 Inheritance to verdict register

§11's forward signals operate within the verdict register established
at §1.3 — methodology-evidence base strengthened (verification chain
at three independent layers; in-sample-caveat asymmetry observed in
the direction Concern A predicts; cross-section terminology
discipline operationalized in real-time); strategy-evidence
constrained (cohort_a_filtered = 0; lone unfiltered survivor's
hybrid quality profile; mechanism adjudication deferred). The
forward signals carry the same dual register: methodology-process
principles strengthened (Q-S4-10/14/15/16 codification candidates;
empirical-verification discipline at anchor-inheritance level
demonstrated); strategy-deployability questions deferred (DSR / PBO /
CPCV infrastructure; calibration question; audit-only partition
mechanism adjudication).

The closeout closes with these signals as observations from
PHASE2C_8.1's work cycle, not as commitments to specific successor
arcs. Selection of next implementation arc is post-PHASE2C_8.1
closure per spec §10.7 + Q-FS4 strictness; not pre-named at this
closeout.
