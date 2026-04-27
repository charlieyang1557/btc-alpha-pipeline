# PHASE2C_7.1 Multi-Regime Evaluation Gate — Closeout

**Arc:** PHASE2C_7.1 — multi-regime extension of PHASE2C_6's evaluation
gate analysis. Path B per [`docs/phase2c/PHASE2C_7_SCOPING_DECISION.md`](../phase2c/PHASE2C_7_SCOPING_DECISION.md).

**Predecessor closeout:** [`docs/closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md`](PHASE2C_6_EVALUATION_GATE_RESULTS.md).

**Implementation spec:** [`docs/phase2c/PHASE2C_7_1_PLAN.md`](../phase2c/PHASE2C_7_1_PLAN.md).

---

## 1. Verdict

PHASE2C_7.1 executed a multi-regime evaluation of PHASE2C_6's
198-candidate batch (`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`),
evaluating the same candidates against the 2024 validation regime
in addition to the 2022 holdout regime PHASE2C_6 already evaluated
against. **Selection power is regime-dependent and not robustly
preserved across the two tested regimes.** Within validation_2024,
the primary pool (`wf_test_period_sharpe > 0.5`) survived the
holdout gate at a higher rate (22/44 = 50.0%) than the audit-only
pool (65/154 = 42.2%); PHASE2C_6's 2022 evaluation showed the
opposite direction (audit-only 12/154 = 7.79% > primary 1/44 =
2.27%). Cross-regime intersection (passed both 2022 and 2024
holdout gates) shows audit-only > primary direction (8/154 = 5.2%
audit-only vs 0/44 = 0.0% primary). The audit-only > primary
direction matches what PHASE2C_6 found within 2022. PHASE2C_6 holdout-survivor
carry-forward to 2024 shows asymmetric pattern: 0/1 primary
(`bf83ffec` failed 2024) and 8/12 audit-only (66.7% carried forward).
The three cuts are different estimands and should not be collapsed
into a single pass/fail verdict; bounds and pre-registration status
detailed in §6, mechanism adjudication remains undetermined within
this batch's two tested regimes.


## 2. Scope and out-of-scope

This section catalogs what PHASE2C_7.1 covers (§2.A), what it
explicitly does not cover (§2.B), and what configuration
infrastructure was read versus modified (§2.C). The scope
catalog complements §1's verdict-distillation register: §1 reads
what the closeout established; §2 names what evidence-and-
infrastructure that establishment was bounded to.

### §2.A — In scope

**Same 198-candidate input universe.** PHASE2C_7.1 evaluates the
same 198 candidates from PHASE2C_6 batch
`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`. Source:
`data/phase2c_evaluation_gate/audit_v1/holdout_results.csv`. The
universe-symmetry assertion at Step 4's `comparison.csv`
construction verified bit-identical hash sets between
`audit_v1` and `audit_2024_v1`. See §3 for the input universe
attestation discipline.

**Two-regime evaluation.** PHASE2C_7.1 evaluates the 198
candidates against two regimes: PHASE2C_6's 2022 holdout regime
(`v2.regime_holdout`) and the validation_2024 regime
(`v2.validation`). Both evaluations apply the same 4-criterion
AND-gate (sharpe ≥ −0.5, max_drawdown ≤ 0.25, total_return ≥
−0.15, total_trades ≥ 5). See §4 for the evaluation gate
discipline.

**Trade-count filtered derived set.** PHASE2C_7.1 produces a
filtered analytical artifact set (`audit_2024_v1_filtered/`,
n=144) by applying the post-evaluation filter
`total_trades >= 20`. The filter is pinned at code-level
constant per §5.3 Rule 1 anti-tuning discipline; the threshold
is not exposed as a runtime parameter. See §4 for filter
specification details.

**Candidate-aligned comparison matrix.** PHASE2C_7.1 produces
the comparison matrix at
`data/phase2c_evaluation_gate/comparison_2022_vs_2024_v1/`,
containing per-candidate diff matrix (`comparison.csv`) and
stratified cross-tab (`comparison.json`, structured as
filter-survivor + filter-excluded × primary + audit_only). The
matrix is the canonical artifact §5/§7/§8 read forward to
produce the closeout's interpretive content.

**Closeout document.** PHASE2C_7.1 produces both the canonical
artifact set (the four directory trees enumerated above) and
this closeout document. The closeout document is self-contained;
the METHODOLOGY_NOTES.md update is a separate follow-on commit
per §10's commit-boundary anchor, not part of PHASE2C_7.1's
closeout-commit deliverables.

### §2.B — Out of scope

The following items are explicitly out of scope for PHASE2C_7.1.
Each is named because a future reader might reasonably expect
the closeout to address it; making the boundary explicit
prevents misread.

**2025 test split.** Preserved touched-once across this arc per
CLAUDE.md hard rule. PHASE2C_7.1 evaluates against 2022 +
validation_2024 only; the 2025 test split is not consumed,
referenced for evaluation, or used as a holdout regime in any
form within this arc.

**Paper trading and live trading.** No paper-trading state, no
live execution, no broker integration, no order routing, no
real-money exposure. PHASE2C_7.1 is local backtest evaluation
only.

**Deployment-readiness evaluation.** No candidate is evaluated
for deployment criteria; no candidate in §7 cohorts (a)/(b)/(c)
is a deployment recommendation per §7's diagnostic-not-
promotional discipline + §9 Q-B3 cohort-deep-dive-as-pre-
registered-question framing.

**DSR / CPCV / MDS computation.** No Deflated Sharpe Ratio, no
Combinatorial Purged Cross-Validation, no Minimum Detectable
Skill. PHASE2C_7.1 produces single-regime + multi-regime
holdout pass/fail outputs; advanced multiple-testing
infrastructure remains follow-up scoping territory per §9
Q-B4.

**Path C calibration variation.** Deferred per PHASE2C_7.0 §5
lean; PHASE2C_7.1 follows Path B's multi-regime evaluation
approach without Path C calibration variation. Calibration
variation remains follow-up scoping territory per §9 Q-B2.

**New regime definitions.** No new regime added to
`config/environments.yaml`; PHASE2C_7.1 reads the existing
`validation` block as-defined. Additional regimes for
mechanism-question disambiguation remain follow-up scoping
territory per §9 Q-B1.

**Strategy promotion.** No candidate is promoted to validation,
test, paper-trading, or live evaluation. §7 cohorts are
diagnostic material per §7 + §9 disciplines; cohort membership
is not a strategy recommendation, not a candidate ranking, and
not a forward-pointer to deployment.

### §2.C — Configuration infrastructure (read-only runtime inheritance)

PHASE2C_7.1 added zero fields to `config/environments.yaml`,
modified zero values, did not bump the schema version. The
config infrastructure was read-only:

**Validation block read as-defined.** The `validation` block
(`splits.validation` with `start: "2024-01-01"`, `end:
"2024-12-31"`, `purpose`, `notes` fields) was read at
evaluation time without modification.

**Read-only runtime inheritance for passing_criteria.** The
`validation` block has no `passing_criteria` field. The engine
inherits passing_criteria from the `regime_holdout` block at
evaluation time per §4 cross-block coupling discipline. This
inheritance is **read-only runtime resolution** — no config
field was added or modified; the engine reads both blocks at
evaluation time and resolves the criteria via the inheritance
rule documented in §4. The IMMUTABLE-config CLAUDE.md hard
rule was preserved across this arc.


## 3. Input universe and partition retention

The PHASE2C_7.1 evaluation gate input universe is the 198-candidate
population from PHASE2C_6 batch
`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`. The same hypotheses, the
same hashes, the same partition split — only the regime varies.
The candidate-aligned discipline is structural: §5's three-cut
adjudication requires that the 198 candidates evaluated against
2024 are *identically* the 198 candidates evaluated against 2022 in
PHASE2C_6, with no resampling, re-extraction, or re-compilation
between arcs.

**Source.** The canonical 198-hash list comes from PHASE2C_6's
audit_v1 aggregate CSV:

```
data/phase2c_evaluation_gate/audit_v1/holdout_results.csv
```

PHASE2C_7.1's producer reads from this file as ground truth rather
than re-extracting from upstream batch metadata. This guarantees
input-universe identity across arcs by construction. The producer
also writes its own per-candidate artifacts under
`data/phase2c_evaluation_gate/audit_2024_v1/`, with the
`hypothesis_hash` field on each artifact mirroring the source
CSV's value.

**Hash axis (per-candidate JSON, not registry).** Candidates match
across arcs by the per-candidate JSON `hypothesis_hash` field, NOT
by the experiments-registry `hypothesis_hash` column. The two
diverge: the producer-side hash is the canonical D3 hash from
PHASE2C_6; the registry-side hash is recomputed by the engine
post-compile via `compute_dsl_hash`. The recomputation is
deterministic but produces a different string identity from the
producer-side hash. Step 4's comparison script uses the
producer-side hash exclusively (sub-step 1.4 V4 lesson; codified
in `scripts/compare_2022_vs_2024.py:_load_run_artifacts`).

**Universe partition (preserved from PHASE2C_6).** The 198
candidates split into:

- Primary universe: `wf_test_period_sharpe > 0.5`, n=44
- Audit-only: `wf_test_period_sharpe <= 0.5`, n=154

The threshold (`> 0.5`, strict) and the partition definition are
identical to PHASE2C_6; PHASE2C_7.1 does not re-calibrate. Each
candidate carries its `wf_test_period_sharpe` from the corrected-
engine canonical CSV (`data/phase2c_walkforward/batch_<batch_id>_corrected/walk_forward_results.csv`),
which is the post-correction WF artifact (engine fix `eb1c87f`,
lineage tag `wf-corrected-v1`).

**Universe symmetry assertion.** Step 4's comparison script asserts
the symmetric difference between PHASE2C_6 audit_v1 hashes and
PHASE2C_7.1 audit_2024_v1 hashes is empty before computing the
cross-tab matrix. The assertion ran clean on the real artifact
sets in Step 4 (`scripts/compare_2022_vs_2024.py
apply_2022_vs_2024_comparison` pre-flight). This is the
empirical anchor that "same 198 candidates" is not a stipulation
but a verified property of the artifact pair.

**Lineage attestation.** All 198 PHASE2C_7.1 per-candidate
artifacts attest under the `single_run_holdout_v1` evaluation
domain with corrected-engine commit `eb1c87f` and lineage tag
`wf-corrected-v1`, and stamp the PHASE2C_7.1 §7 schema fields
(`artifact_schema_version="phase2c_7_1"`, `regime_key="v2.validation"`,
`regime_label="validation_2024"`). The schema-discriminator
extension to `backtest.wf_lineage.check_evaluation_semantics_or_raise`
(sub-step 1.1) validates these artifacts via the new branch;
PHASE2C_6 audit_v1 artifacts continue to validate via the
absent-field legacy branch. Both validation passes ran clean
across all 198+1 PHASE2C_7.1 artifacts at Step 2 V3 verification.

---

## 4. 2024 regime configuration, evaluation gate, and Path B failure-mode taxonomy

**2024 regime source.** The 2024 evaluation regime is defined by
the `validation` block of `config/environments.yaml` (split version
`v2`):

```yaml
validation:
  start: "2024-01-01"
  end:   "2024-12-31"
  purpose: "Hyperparameter selection, leaderboard ranking (Phase 2B+)"
  notes: "BTC ETF approval era, halving year"
```

The window is the calendar year 2024 at 1H granularity, the same
data-infrastructure setup PHASE2C_6 used against 2022. PHASE2C_7.1
did not modify `config/environments.yaml`; the IMMUTABLE-config
constraint (CLAUDE.md hard rule) was preserved.

**Regime naming.** The PHASE2C_7.1 §7 schema convention names this
regime `validation_2024` (`regime_label` value derived from
`REGIME_KEY_LABEL_MAPPING["v2.validation"]`). All references to the
2024 evaluation regime in this closeout, in artifact lineage fields,
and in downstream cross-arc references should use the config-
canonical name `validation_2024`, NOT "the 2024 regime," "the
post-halving regime," or "the recovery regime." The naming
discipline is structural — character-typing the regime in prose
forecloses regime-name traceability and risks readers attributing
the §5 finding to a regime characterization the data does not
adjudicate.

**Cross-block passing_criteria inheritance.** The `validation`
block in `config/environments.yaml` does not carry its own
`passing_criteria` field; the engine inherits the gate criteria
from the canonical `regime_holdout` block at evaluation time. The
producer emits an INFO-level log line on every per-candidate
evaluation documenting the inheritance:

```
Regime evaluation regime_key=v2.validation: passing_criteria
inherited from regime_holdout block (no passing_criteria field on
validation block in environments.yaml; cross-block coupling per
PHASE2C_7.1 §3)
```

198 such log lines fired during Step 2 (one per candidate;
verified via /tmp/audit_2024_v1_stdout.log grep against
"passing_criteria inherited"). The inheritance discipline (§3 of
the spec / Q1 of the design adjudication) keeps a single source
of truth for "what does it mean to pass a single-regime holdout"
across all current attestation domains; future arcs that
introduce regime-specific gate calibration would explicitly
override `passing_criteria` in the relevant block rather than
silently diverge.

**Evaluation gate (4-criterion AND).** The same gate as PHASE2C_6,
applied verbatim to 2024 holdout outputs:

```
sharpe_ratio       >= -0.5
max_drawdown       <= 0.25
total_return       >= -0.15
total_trades       >=  5
```

Inclusive inequalities; a candidate passes if and only if all
four conditions hold against its 2024 holdout metrics. No gate
modification was proposed for PHASE2C_7.1 (Path C calibration
variation was deferred per PHASE2C_7.0 §5 lean).

**Trade-count filter (post-evaluation, pinned).** Step 3
introduced a post-evaluation analytical filter at
`total_trades >= 20` (in 2024 holdout). The filter is
implemented at `MIN_TOTAL_TRADES = 20` as a module-level constant
in `scripts/filter_evaluation_gate.py`; the threshold is NOT
exposed as a CLI flag (PHASE2C_7.1 spec §5.3 Rule 1 pre-
specification anti-tuning discipline). The filter operates on
2024 evaluation outputs, NOT on 2022 trade counts: the question
the filter answers is "does selection-power finding hold when
restricting to candidates with sufficient 2024 trade volume?",
which requires filtering on 2024 trade counts. PHASE2C_6's
near-miss cluster (4 candidates with positive 2022 holdout Sharpe
but trade counts below 5 against 2022) was the empirical concern
that motivated the filter; the implementation surfaces it as a
filtered-subset analytical view (`audit_2024_v1_filtered/`,
n=144) alongside the canonical unfiltered view (`audit_2024_v1/`,
n=198). §5 reads both views.

**Threshold justification (cross-reference).** The choice of
`>= 20` is justified in [PHASE2C_7.1 spec §5.2](../phase2c/PHASE2C_7_1_PLAN.md)
on three empirical anchors: (i) 25th percentile of the
full-distribution trade count, (ii) structural step above the
5-9-trades distributional gap that motivated the near-miss
cluster, and (iii) Sharpe-stability rule-of-thumb at sqrt(N).
The closeout does not reproduce the full justification; readers
investigating the threshold choice grep §5.2 directly.

**Path B failure-mode taxonomy (PHASE2C_7.0 §4 anchor).** Before
PHASE2C_7.1 ran, the scoping decision document
([`docs/phase2c/PHASE2C_7_SCOPING_DECISION.md`](../phase2c/PHASE2C_7_SCOPING_DECISION.md))
named three a priori failure-mode branches for the Path B 2024
evaluation:

| branch  | predicate (within-2024 partition pass-rate) | reading |
|---------|---------------------------------------------|---------|
| mirror  | audit-only > primary in 2024 (matches 2022) | anti-selection is systematic across regimes |
| invert  | primary > audit-only in 2024                | anti-selection is 2022-specific, not generalized |
| null    | primary ≈ audit-only in 2024 (similar pass rates) | gate has no detectable selection-power effect against 2024 |

The taxonomy was constructed to anticipate the within-regime cut
specifically; cross-regime intersection and PHASE2C_6 carry-forward
cuts were not explicitly enumerated in the a priori taxonomy
because they require both arcs' artifacts to compute. The
empirical result (per §5) matches "invert" in the within-2024 cut
direction, but the cross-regime intersection cut and carry-forward
cut both run in the "mirror" direction — a configuration the a
priori taxonomy did not pre-name. §5 treats the joint reading as
the load-bearing closeout finding; this section anchors the
taxonomy reference for §5 line 29's "matches the 'invert' branch
in direction" claim.


## 5. Selection-power adjudication

The empirical comparison between PHASE2C_6 (2022 evaluation) and
PHASE2C_7.1 (2024 evaluation) of the same 198-candidate batch is the
closeout's load-bearing finding. The corrected WF gate's selection
power against either regime in isolation — and across both regimes
in intersection — admits more than one directional reading depending
on which data cut is examined. §5 lays out three complementary cuts
before adjudicating their joint meaning. These are different
estimands: 2024-only selection power, cross-regime robustness, and
2022-survivor carry-forward. They should not be collapsed into one
pass/fail verdict.

**Within-regime 2024 (the cut that PHASE2C_6 prompted Path B to
collect).** In the unfiltered 198-candidate population, the primary
universe (`wf_test_period_sharpe > 0.5`) passed the 2024 holdout gate
at 22/44 = 50.0%; the audit-only pool (`wf_test_period_sharpe <= 0.5`)
passed at 65/154 = 42.2%. Direction: primary > audit-only by +7.8
percentage points. The PHASE2C_6 anti-selection direction
(audit-only > primary by −5.5pp against 2022) does NOT replicate
within 2024 in the same direction; relative to the §4 Path B
failure-mode taxonomy, this matches the "invert" branch in direction.
Under the trade-count filter (`total_trades >= 20`, n=144 survivors),
the gap compresses to 19/32 = 59.4% primary versus 60/112 = 53.6%
audit-only, +5.8pp primary direction — direction preserved, magnitude
reduced. Within either filter state, the gate produces a population
that passes 2024 at a higher rate than the population it rejected.

**Cross-regime intersection (the cut PHASE2C_6 anti-selection finding
points to).** Restricting to candidates that passed BOTH 2022 and
2024 holdout gates, the population breakdown is 0/44 = 0% primary
and 8/154 = 5.2% audit-only. Direction: audit-only > primary by
+5.2pp — same direction as PHASE2C_6's 2022 anti-selection finding,
distinct cut. All 8 cross-regime survivors are audit-only candidates
with negative or near-zero corrected WF Sharpe; the corrected WF
gate produced zero candidates that survived both regime stress tests
within this batch. The within-regime 2024 inversion (primary > audit
in 2024-alone) does NOT extend to cross-regime selection (primary
disappears entirely under the AND-of-two-regimes filter).

**PHASE2C_6 survivor carry-forward.** The 13 PHASE2C_6 holdout-
survivors split into 1 primary (`bf83ffec`, the headline "borderline
hd_sh=+0.014" candidate from PHASE2C_6.6 §5) and 12 audit-only
candidates. The primary survivor's 2024 carry-forward is 0/1 = 0%
(`bf83ffec` failed 2024 with hd_sh=−0.633 despite >= 20 trades).
The audit-only survivors' 2024 carry-forward is 8/12 = 66.7%. The
single primary candidate that survived 2022 did not survive 2024;
two-thirds of the audit-only cohort (n=12; magnitude bounded
in §6) that survived 2022 also survived 2024. The audit-only cohort's cross-regime carry-forward
rate is more than 60 percentage points higher than the primary's
cross-regime carry-forward rate — bounded by the small primary
n=1, but the direction is unambiguous: candidates the gate flagged
as worse outperformed the gate's lone winner on cross-regime
robustness.

**Adjudication of the joint reading.** These three cuts are not
contradictory — they answer three different questions of selection
power, and the answers are honest in each direction:

1. *Does the corrected WF gate enrich for 2024-survivors when
2024 is evaluated in isolation?* Yes, modestly (+5.8 to +7.8pp
primary direction depending on filter state). The within-regime
2024 selection-power direction is opposite to PHASE2C_6's 2022
anti-selection direction.

2. *Does the corrected WF gate enrich for cross-regime survivors
(survived both 2022 and 2024)?* No — the primary partition contains
zero cross-regime survivors, the audit-only partition contains 8.
Direction matches PHASE2C_6's 2022 anti-selection finding.

3. *Does PHASE2C_6's 2022 anti-selection finding generalize beyond
2022?* The within-regime answer is "no, it inverts in 2024 alone."
The cross-regime answer is "yes, it persists in the 2022∩2024
intersection direction." Both readings are sustained by the same
198-candidate evidence base; collapsing to one direction would be
premature.

**Bounded conclusion (asymmetric confidence).** Within this batch
of 198 candidates, evaluated against two regimes (2022 bear, 2024
post-halving / ETF-approval), the corrected WF gate's selection
power is regime-dependent and not robustly preserved across the
two tested regimes. The within-2024 direction inverts relative to
PHASE2C_6's 2022 anti-selection; the cross-regime intersection
direction mirrors 2022 anti-selection. Magnitude claims are
bounded by partition sizes (primary n=44, audit-only n=154) and
by the n=2 regime evidence base — the within-2024 +7.8pp gap and
the cross-regime −5.2pp gap are sensitive to a small number of
candidates flipping outcome (e.g., a single primary candidate
switching to a 2024-pass would not change the within-2024 direction
but a single primary cross-regime survivor would change the
cross-regime direction). The finding is "selection power is
regime-dependent and not robustly preserved across the two tested
regimes" — neither "the gate works" nor "the gate anti-selects"
is a complete reading of the data.

The within-regime 2024 cut and the cross-regime intersection cut
should both appear in any further use of this evidence base. A
selection-power claim against 2024 alone is not a selection-power
claim across regimes; the claim "the gate enriches for 2024-survivors"
is empirically supported within this batch, but the claim "the gate
enriches for cross-regime robustness" is empirically refuted within
this batch. §6 (what this finding does NOT establish) and §9
(implications for PHASE2C_7+ scoping) elaborate on the bounds.


## 6. What this finding does NOT establish

§5 establishes that within batch `b6fcbf86`, evaluated against two
regimes (`v2.regime_holdout` = bear_2022; `v2.validation` = validation_2024),
the corrected WF gate's selection power is regime-dependent and not
robustly preserved across the two tested regimes. §6 enumerates the
bounds of that finding. **§6 bounds the §5 conclusion; it does not
weaken or revise it.** The §5 headline holds within its stated
bounds; §6's job is to surface what those bounds permit a reader
to conclude and what they do not.

The bounds split into four categories: data-scope (what the batch
covers), interpretation-scope (what §5 does and does not imply
about adjacent project work), mechanism-scope (what §5 does and
does not say about *why* the regime-dependence occurs), and
pre-registration-scope (the a priori status of the three §5 cuts
relative to PHASE2C_7.0's Path B failure-mode taxonomy).

**Data-scope bounds.**

This finding describes one batch (`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`),
two regimes (`v2.regime_holdout` and `v2.validation`), and one gate
calibration (`wf_test_period_sharpe > 0.5` for partition; the
4-criterion AND-gate inherited from the regime_holdout block per
§4 cross-block coupling). It does not extend to:

- *Other batches.* A second batch sampling the same prompt-themed
  candidate space could produce a different primary/audit-only
  pass-rate relationship purely from sampling variance. The within-
  batch n=44 primary universe is small; PHASE2C_6.6 §5 noted a
  single primary survivor flip would shift its 2022 ratio
  meaningfully, and the n=44 sensitivity carries forward to
  PHASE2C_7.1 §5's within-2024 cuts as well.

- *Other regimes.* The two tested regimes (bear_2022 calendar year;
  validation_2024 calendar year) are distinct market shapes but
  represent two samples from a population of possible regimes. The
  2025 test split is preserved touched-once across this arc per
  CLAUDE.md hard rule; future regimes would require a follow-up
  arc (§10) and are not part of this evidence base.

- *Other gate calibrations.* The `> 0.5` threshold is inherited
  from the Phase 2C Phase 1 binary criterion and was not varied
  in PHASE2C_7.1. Path C calibration variation was deferred per
  PHASE2C_7.0 §5; whether selection power is calibration-
  invariant within either regime is undetermined by this batch.

- *Generalization to "the gate works/fails across regimes in
  general."* Two regimes are not a sufficient evidence base for
  general-regime claims. METHODOLOGY_NOTES §7 codifies the
  asymmetric-confidence rule for n=2 evidence: directional claims
  hold for the tested regimes; population-level claims about
  selection-power-across-regimes-in-general do not. §5's
  "regime-dependent and not robustly preserved across the two
  tested regimes" framing carries the bound explicitly; readings
  that drop the "two tested regimes" qualifier are unsupported.

- *Audit-only carry-forward sample size.* The PHASE2C_6 audit-only
  carry-forward rate (§5: 8/12 = 66.7%) describes the 12 audit-only
  candidates that survived the 2022 holdout and were re-evaluated
  against 2024. The rate is sensitive to single-candidate flips: two
  additional carry-forwards would shift the rate to 10/14 = 71.4%;
  two failures would shift to 8/14 = 57.1%. The direction
  (audit-only carry-forward exceeds primary carry-forward of 0/1)
  is robust to single-candidate flips at this evidence level; the
  magnitude is not. Magnitude claims about audit-only carry-forward
  should be read with the n=12 caveat in mind.

**Interpretation-scope bounds.**

§5 describes the corrected WF metric's selection power against the
two tested regimes. It does not imply that:

- *The corrected engine work was wasted or wrong.* The engine fix
  (commit `eb1c87f`, lineage `wf-corrected-v1`) corrected a
  semantic bug in walk-forward test-period metric computation. The
  metric values produced post-fix are the accurate measurements of
  what the metric is defined to measure. §5's finding is about
  what the correctly-measured metric *predicts*, not about whether
  the measurement was correct. A correctly-computed metric can
  have regime-dependent predictive power without that being a
  defect of the metric's computation.

- *Walk-forward methodology is broken.* §5 speaks to one binary
  criterion (`wf_test_period_sharpe > 0.5`) applied to one set of
  WF outputs against two regime samples. Walk-forward methodology
  comprises many design choices: window sizing, train/test split
  semantics, metric aggregation, the binary criterion applied to
  outputs. Other design choices within walk-forward methodology
  are not addressed by this batch. Generalizing from "this binary
  criterion's selection power is regime-dependent across these
  two regimes" to "walk-forward methodology is broken" is an
  unwarranted extension §6 explicitly forbids.

- *Phase 2C generated no actionable strategies.* The closeout
  describes selection-power against two regimes; it does not
  evaluate any candidate against the 2025 test split, against
  forward live data, or against any deployment-readiness criterion.
  No deployment claim, paper-trading claim, or "this strategy
  works" claim is made or implied in this closeout. Specific
  candidates flagged in §7 (the 8 cross-regime survivors, the 22
  primary 2024-survivors, the 5 PHASE2C_6 carry-forward failures)
  are diagnostic enumerations under pre-registered-question
  discipline, not strategy recommendations.

- *Future regime holdouts will show similar patterns.* The
  within-batch result is empirically observed for two regimes;
  whether it generalizes is precisely the open question that §10
  forward-points to multi-regime work at n≥3 to address. The §5
  finding does not predict outcomes for additional regimes — it
  describes the two tested regimes specifically.

**Mechanism-scope bounds.**

§5 describes an empirical pattern (regime-dependence with
within-2024 inversion versus cross-regime intersection mirror).
§5 does not commit to a mechanism explanation. §6 makes explicit
that the data leaves the mechanism question undetermined:

- *The data does not distinguish regime-mismatch from pattern-overfit
  from calibration-coupling.* Three candidate explanations could
  produce the empirical pattern observed:

  1. *Regime-mismatch.* The corrected WF gate, as calibrated, may
     enrich for candidates fit to a regime-of-training that
     resembles validation_2024 more than bear_2022. Within-2024
     selection power and cross-regime anti-selection would both
     follow.

  2. *Pattern-overfit.* The corrected WF gate may identify
     candidates with strategy-pattern fits to the train period
     that generalize selectively. Within-2024 selection power and
     cross-regime anti-selection would both follow.

  3. *Calibration-coupling.* The `> 0.5` threshold may select for
     candidates whose Sharpe magnitudes are regime-dependent in
     a way the threshold is calibrated to one regime's
     distribution. Within-2024 selection power and cross-regime
     anti-selection would both follow.

  All three explanations produce the §5 empirical pattern.
  Distinguishing them requires either (a) Path C calibration
  variation within a regime (deferred per PHASE2C_7.0 §5), or
  (b) multi-regime evaluation at n≥3 (not part of this arc).

- *The gate is "calibrated for validation_2024-like regimes."*
  This framing pre-commits to the calibration-coupling mechanism
  explanation §6 explicitly does not adjudicate. The gate's
  empirical behavior on validation_2024 is observable; *why* it
  behaves that way is not, within this batch.

- *Macro-regime characterization.* "validation_2024 was a bull
  regime," "the post-halving regime," "the ETF-approval regime,"
  or any regime-character-typing is mechanism-adjacent
  speculation §6 forbids. The closeout uses the config-canonical
  name `validation_2024` and bounds claims to that named regime
  without character-typing it. Future arcs that test additional
  regimes would surface regime-characterization questions
  empirically; this arc does not.

**Pre-registration-scope bounds.**

§5's three cuts have different a priori status relative to the
PHASE2C_7.0 Path B failure-mode taxonomy (cataloged in §4 of this
closeout):

| §5 cut                          | a priori status            |
|---------------------------------|----------------------------|
| within-2024 partition pass-rate | pre-registered             |
| cross-regime intersection       | post-hoc structurally     |
| PHASE2C_6 survivor carry-forward| post-hoc structurally     |

The within-2024 cut is pre-registered: the Path B failure-mode
taxonomy explicitly enumerated mirror / invert / null branches as
the primary observable. §5's "matches the invert branch in
direction" claim is appropriately framed against this a priori
taxonomy.

The cross-regime intersection cut and the PHASE2C_6 carry-forward
cut are post-hoc structurally: derivable from pre-committed
artifacts (Step 4 cross-tab matrix, candidate-aligned by
construction), but the cuts themselves were not enumerated in the
Path B taxonomy. **"Post-hoc structurally" does not mean "invalid"
— it means valid descriptive analysis with lower evidential
priority than the pre-registered observable.** Both cuts are
reproducible from the canonical artifacts and survive V7
traceability. Their analytical validity is not in question; their
*evidential weight under pre-registration discipline* is.

§5's "regime-dependent and not robustly preserved" headline is
supported by all three cuts read together. Each cut is
informationally independent: the within-2024 cut establishes that
selection power is not regime-invariant; the cross-regime
intersection cut establishes that the within-2024 inversion does
not generalize to cross-regime survival; the PHASE2C_6 carry-
forward cut establishes that PHASE2C_6's primary survivor did not
carry forward and PHASE2C_6's audit-only survivors carried forward
at 8/12. The headline is supported by the conjunction of these
informationally-independent observables. No single cut is required
to sustain the headline.

The pre-registration distinction matters for downstream consumers.
A claim that referenced only the within-2024 cut would inherit
pre-registered evidential weight; a claim that referenced only the
cross-regime intersection cut or the PHASE2C_6 carry-forward cut
would inherit post-hoc structurally weight (valid descriptive,
lower a priori). Future-arc citations of §5 should preserve the
distinction explicitly. The §5 closeout itself satisfies the
discipline by surfacing all three cuts together; downstream
citations that compress to one cut should preserve the cut's
status alongside the magnitude claim.


## 7. Cohort enumerations

§5's three cuts surface three candidate populations the closeout
reader needs visibility into. §7 enumerates each cohort per-candidate.
The enumeration is diagnostic material for §9 mechanism reading —
not strategy recommendations, not deployment guidance, and not
candidate rankings. No cohort or candidate enumerated below should
be interpreted as actionable; each appears because it is observable
in the canonical data, and the closeout's job is to make it
inspectable.

The three cohorts and their derivation cuts:

| cohort | derivation cut | a priori status | n |
|--------|----------------|------------------|---|
| (a) Cross-regime survivors | passed 2022 AND 2024 | post-hoc structurally | 8 |
| (b) Primary 2024-survivors that failed 2022 | within-2024 partition cut | pre-registered | 22 |
| (c) PHASE2C_6 holdout-survivors and 2024 outcomes | PHASE2C_6 carry-forward cut | post-hoc structurally | 13 |

Pre-registration status carries forward from §6 category 4: the
within-2024 cut was pre-registered as a Path B failure-mode
observable; the cross-regime intersection cut and the PHASE2C_6
carry-forward cut were post-hoc structurally (valid descriptive
analysis, lower a priori evidential priority). §7's per-cohort
framing notes the status explicitly.

### Cohort (a) — Cross-regime survivors (passed both regimes)

This cohort is derived from §5's cross-regime intersection cut,
which is post-hoc structurally per §6 category 4 — valid
descriptive analysis, lower evidential priority than the
pre-registered within-2024 observable. It is listed first because
it directly represents the cross-regime intersection cut. All 8
candidates are in the audit-only partition (`wf_test_period_sharpe
<= 0.5`).

The cohort's empirical bounds: WF Sharpe range −1.5107 to +0.4345;
6 of 8 candidates carry WF Sharpe ≤ 0; theme distribution 5
calendar_effect + 2 volume_divergence + 1 momentum. No primary
candidate (`wf_test_period_sharpe > 0.5`) appears in this cohort
within this batch.

V7 anchor: rows derivable from `comparison.csv` filter
`holdout_2022_passed=True AND holdout_2024_passed=True`.

| hash | theme | name | partition | wf_sharpe | hd22_sh | hd22_dd | hd22_ret | hd22_t | hd24_sh | hd24_dd | hd24_ret | hd24_t | filter_state |
|------|-------|------|-----------|----------:|--------:|--------:|---------:|-------:|--------:|--------:|---------:|-------:|--------------|
| `9dc5c373` | calendar_effect | weekend_effect_momentum_185 | audit_only | +0.4345 | -0.0457 | 0.1656 | -0.0164 | 78 | -0.4533 | 0.1080 | -0.0603 | 74 | survivor_passed |
| `c200a95d` | calendar_effect | weekday_momentum_calendar_150 | audit_only | +0.1963 | +0.3555 | 0.1506 | +0.0624 | 126 | +0.2832 | 0.2236 | +0.0402 | 122 | survivor_passed |
| `0845d1d7` | volume_divergence | volume_surge_momentum_entry | audit_only | -0.0716 | +0.5082 | 0.0952 | +0.0680 | 19 | +1.0529 | 0.1722 | +0.1829 | 23 | survivor_passed |
| `94b3d1fd` | calendar_effect | monday_morning_accumulation | audit_only | -0.1918 | +0.4790 | 0.1205 | +0.0705 | 34 | -0.0458 | 0.2450 | -0.0285 | 42 | survivor_passed |
| `1d6a587a` | calendar_effect | monday_weakness_friday_strength | audit_only | -0.2025 | +0.5856 | 0.1507 | +0.1087 | 52 | +0.0258 | 0.2406 | -0.0154 | 80 | survivor_passed |
| `f4977b3e` | volume_divergence | volume_spike_momentum_entry | audit_only | -0.7527 | +0.3474 | 0.1587 | +0.0504 | 65 | +0.2472 | 0.2354 | +0.0284 | 96 | survivor_passed |
| `7f296ee9` | calendar_effect | weekend_volatility_compression_monday_breakout_125 | audit_only | -0.8983 | +0.7223 | 0.1340 | +0.1188 | 24 | +0.7550 | 0.1259 | +0.1434 | 37 | survivor_passed |
| `18c2a5f7` | momentum | ema_crossover_momentum_surge | audit_only | -1.5107 | +0.9602 | 0.0785 | +0.1248 | 20 | +1.6259 | 0.0974 | +0.2373 | 24 | survivor_passed |

This cohort is diagnostic material for §9 mechanism reading; no
recommendation is implied. The 8 candidates are observable in the
cross-regime intersection cell of Step 4's cross-tab; their
mechanism (regime-mismatch / pattern-overfit / calibration-coupling
per §6 category 3) is undetermined within this batch.

### Cohort (b) — Primary 2024-survivors that failed 2022

This cohort is derived from §5's within-2024 partition cut, which
was pre-registered as the primary observable in Path B's
failure-mode taxonomy (§4). All 22 candidates are in the primary
partition (`wf_test_period_sharpe > 0.5`); each failed the 2022
holdout gate and passed the 2024 holdout gate.

The cohort's empirical bounds: WF Sharpe range +0.5464 to +1.6325
(by primary-partition definition `> 0.5`); median +1.0231; theme
distribution 8 volume_divergence + 7 mean_reversion + 3
calendar_effect + 3 momentum + 1 volatility_regime. The volume_
divergence + mean_reversion themes account for 15 of 22 candidates
(68%) in this cohort.

V7 anchor: rows derivable from `comparison.csv` filter
`partition=primary AND holdout_2022_passed=False AND
holdout_2024_passed=True`.

| hash | theme | name | wf_sharpe | hd22_sh | hd22_dd | hd22_ret | hd22_t | hd24_sh | hd24_dd | hd24_ret | hd24_t |
|------|-------|------|----------:|--------:|--------:|---------:|-------:|--------:|--------:|---------:|-------:|
| `cc295177` | volume_divergence | volume_divergence_reversal | +1.6325 | -0.6742 | 0.4601 | -0.2997 | 62 | +1.6205 | 0.1396 | +0.4005 | 43 |
| `212dd310` | calendar_effect | monday_morning_contrarian_fade | +1.4431 | +0.0732 | 0.2654 | -0.0048 | 13 | -0.0815 | 0.2158 | -0.0274 | 11 |
| `fa1cac01` | volume_divergence | volume_divergence_reversal | +1.3909 | -0.5258 | 0.4219 | -0.2314 | 44 | +1.1319 | 0.0771 | +0.1964 | 27 |
| `80d0d983` | mean_reversion | bb_zscore_reversion_192 | +1.3418 | -0.7852 | 0.3221 | -0.2732 | 75 | +0.6081 | 0.2131 | +0.1295 | 65 |
| `f8e9655e` | momentum | momentum_acceleration_rsi_181 | +1.3351 | -1.4622 | 0.2978 | -0.2463 | 76 | +0.0688 | 0.2261 | -0.0066 | 99 |
| `4f3eb681` | volume_divergence | volume_divergence_reversal | +1.2792 | -1.2702 | 0.5307 | -0.4833 | 52 | +1.1958 | 0.1991 | +0.3787 | 36 |
| `98775adb` | volume_divergence | volume_divergence_momentum_169 | +1.1242 | -1.1393 | 0.4329 | -0.3232 | 53 | +1.0748 | 0.2213 | +0.2321 | 54 |
| `95bf56e7` | momentum | macd_momentum_reversal | +1.1040 | -1.4889 | 0.5214 | -0.4269 | 16 | +1.7295 | 0.0696 | +0.2274 | 22 |
| `0e926e65` | mean_reversion | bollinger_mean_reversion_oversold_142 | +1.0284 | -1.3028 | 0.4885 | -0.4028 | 122 | +0.6336 | 0.2222 | +0.1427 | 111 |
| `5f1d7f3b` | volume_divergence | volume_divergence_momentum_fade_134 | +1.0256 | -1.5891 | 0.6144 | -0.5153 | 66 | -0.0113 | 0.1770 | -0.0301 | 64 |
| `138c8bbe` | calendar_effect | weekend_momentum_fade_200 | +1.0231 | -0.4388 | 0.2738 | -0.0955 | 14 | +0.3748 | 0.1570 | +0.0455 | 11 |
| `500a3fd4` | volume_divergence | volume_divergence_momentum_144 | +1.0165 | -0.8464 | 0.5174 | -0.3818 | 32 | +1.7581 | 0.1621 | +0.7787 | 32 |
| `812216d4` | mean_reversion | bb_squeeze_oversold_reversal | +0.9485 | -1.0153 | 0.4763 | -0.3761 | 67 | +0.5954 | 0.2039 | +0.1480 | 68 |
| `3e366757` | mean_reversion | bollinger_mean_reversion_182 | +0.9378 | -0.7189 | 0.3446 | -0.2546 | 92 | +0.8538 | 0.2015 | +0.2106 | 88 |
| `4f48338d` | volatility_regime | low_vol_regime_breakout | +0.9286 | +0.3841 | 0.2524 | +0.0723 | 33 | -0.4469 | 0.2337 | -0.1327 | 32 |
| `910cf4fe` | volume_divergence | volume_divergence_momentum_179 | +0.8459 | -1.2253 | 0.0975 | -0.0654 | 11 | +0.8392 | 0.0133 | +0.0258 | 6 |
| `79f4d112` | mean_reversion | bb_mean_reversion_oversold_187 | +0.8096 | -1.2909 | 0.4227 | -0.3678 | 79 | +0.7981 | 0.1928 | +0.1903 | 83 |
| `43a948f5` | volume_divergence | volume_divergence_rsi_reversal_124 | +0.7350 | -1.1727 | 0.4950 | -0.4101 | 77 | +1.5518 | 0.2186 | +0.5701 | 76 |
| `c22ec5e4` | calendar_effect | monday_dip_buy | +0.6885 | -0.1422 | 0.4109 | -0.1093 | 58 | +0.3037 | 0.1719 | +0.0423 | 48 |
| `2b1860c6` | mean_reversion | bollinger_overshoot_mean_revert_122 | +0.6116 | -0.9909 | 0.4366 | -0.3511 | 96 | +0.4143 | 0.2367 | +0.0806 | 94 |
| `56def67e` | mean_reversion | bollinger_mean_reversion_172 | +0.5694 | -1.4088 | 0.4692 | -0.4110 | 100 | +0.4272 | 0.2360 | +0.0824 | 97 |
| `9031d823` | momentum | macd_momentum_reversal_capture | +0.5464 | -1.8791 | 0.6019 | -0.5709 | 72 | +1.8746 | 0.1797 | +0.8331 | 57 |

The full 22-candidate enumeration is included in the closeout
because the diagnostic-enumeration discipline applies symmetrically
across the three cohorts. Truncating to a "top N" subset would
inject an ordering decision (which dimension is salient — WF
Sharpe? hd24 Sharpe? theme distribution?) that is mechanism-
adjacent. Full enumeration preserves reader-side reproducibility
of cohort membership.

This cohort is diagnostic material for §9 mechanism reading; no
recommendation is implied. The 22 candidates passed §5's
pre-registered within-2024 cut but did not survive 2022. Whether
their 2024 success reflects regime-fit, pattern-overfit, or
calibration-coupling is §9's question to read forward, not §7's
to claim.

### Cohort (c) — PHASE2C_6 holdout-survivors and 2024 outcomes

This cohort is derived from §5's PHASE2C_6 carry-forward cut,
which is post-hoc structurally per §6 category 4 — valid
descriptive analysis, lower evidential priority than the
pre-registered within-2024 observable. The cohort enumerates the
13 PHASE2C_6 holdout-survivors (1 primary `bf83ffec` + 12
audit-only) and their 2024 outcomes.

**Cohort overlap with cohort (a).** Cohort (c) overlaps cohort
(a) by 8 candidates: the 8 audit-only candidates that passed both
regimes are simultaneously the cross-regime intersection (cohort
(a)) and the carry-forward subset that survived 2024 holdout
(cohort (c)). Cohort (a) is structurally a subset of cohort (c) —
not a separate population. The cohort tables list the 8
overlapping candidates once (in cohort (a)) rather than twice;
the 5 cohort (c) failures below are the candidates that survived
2022 but did not survive 2024.

Of the 13: 8 passed the 2024 holdout gate (these 8 are cohort (a)
enumerated above) and 5 failed. The 5 failures split 1 primary +
4 audit-only. The 5 failure rows are listed below; the 8 pass rows
are not duplicated from cohort (a) above (cross-reference the
cohort (a) table for those candidates' metrics).

The cohort's empirical bounds: theme distribution 6 calendar_effect
+ 4 volume_divergence + 3 momentum. Carry-forward rate by
partition: 0/1 = 0% primary (`bf83ffec` failed 2024); 8/12 = 66.7%
audit-only.

V7 anchor: rows derivable from `comparison.csv` filter
`holdout_2022_passed=True`. The 5 failures below additionally
satisfy `holdout_2024_passed=False`.

| hash | theme | name | partition | wf_sharpe | hd22_sh | hd24_sh | hd24_t | filter_state |
|------|-------|------|-----------|----------:|--------:|--------:|-------:|--------------|
| `bf83ffec` | calendar_effect | monday_weakness_tuesday_rebound_130 | primary | +1.1381 | +0.0138 | -0.6328 | 22 | survivor_failed |
| `ab7584d2` | volume_divergence | volume_divergence_breakout_159 | audit_only | -0.2073 | +0.3979 | -1.7651 | 34 | survivor_failed |
| `b2ddd47c` | volume_divergence | volume_divergence_breakout_momentum | audit_only | -1.5763 | -0.4851 | -0.5577 | 24 | survivor_failed |
| `61395958` | momentum | macd_rsi_momentum_confirmation_156 | audit_only | -1.9047 | -0.1666 | +0.7487 | 82 | survivor_failed |
| `37c0661e` | momentum | macd_momentum_surge_166 | audit_only | -2.1931 | +0.0702 | +0.4132 | 71 | survivor_failed |

Two rows in the failure subset (61395958, 37c0661e) carry positive
2024 holdout Sharpe but failed the 2024 gate. Per-criterion gate
failure resolution is in each candidate's `audit_2024_v1/<hash>/
holdout_summary.json` `gate_pass_per_criterion` field (the gate
is a 4-criterion AND; positive Sharpe alone does not satisfy the
gate when drawdown, return, or trade-count criteria fail). Their
trade counts (82 and 71) and 2024 holdout metrics are diagnostic
material for §9 mechanism reading.

This cohort is diagnostic material for §9 mechanism reading; no
recommendation is implied. The 5 failures are observable in
Step 4's cross-tab `passed_2022_failed_2024` cells (1 in primary,
4 in audit_only). Why these candidates passed 2022 but failed
2024 is undetermined within this batch.

### Closing diagnostic-discipline note

The three cohorts above enumerate 8 + 22 + 13 = 43 candidate
slots, with 8 candidates (cohort (a) = first 8 of cohort (c))
appearing in two cohorts by structural overlap. The deduplicated
candidate count across the three cohorts is 35 unique candidates
out of the 198-candidate batch. The remaining 163 candidates do
not appear in any §7 cohort because they did not satisfy any of
the three derivation cuts; their per-candidate data is in the
canonical `comparison.csv` for any reader who needs to inspect
specific candidates outside the §7 cohorts.

The per-cohort framing repeats the diagnostic-not-promotional
discipline because the failure mode it prevents is reader-side
drift: reading a cohort table in isolation, a future closeout
consumer could over-interpret cohort membership as a candidate
recommendation. The repetition is intentional discipline anchor,
not boilerplate redundancy.

§9 reads forward implications of the §5 cuts and §7 cohort
enumerations for mechanism questions and PHASE2C_8+ scoping. §10
forward-points to follow-up arc designs that would address the
mechanism questions §6 category 3 names as undetermined within
this batch.


## 8. By-theme cross-regime interpretation

The 5-theme rotation that produced this batch's 198 candidates shows
distinct patterns across the two tested regimes (`v2.regime_holdout`
= bear_2022; `v2.validation` = validation_2024). This section treats
each theme separately because the failure mechanisms diverge in ways
grouping would erase, then synthesizes the patterns the by-theme
view contributes beyond §5's population-level finding. All claims
are bounded to this batch, against these two regimes; nothing in
this section establishes general theme properties across other
regimes or other batches. Mechanism reading is forbidden per §6
category 3; this section names what the by-theme view shows
descriptively, not why the patterns hold.

**Per-theme anchor table (V7 grep-able from `comparison.csv` +
aggregate JSONs):**

| theme | n | 2022 pass | 2024 pass | 2024 filtered (≥20) | pp | pf | fp | ff | excl |
|-------|---|-----------|-----------|---------------------|---:|---:|---:|---:|----:|
| volume_divergence | 40 | 4/40 = 10.0% | 25/40 = 62.5% | 23/36 = 63.9% | 2 | 2 | 23 | 13 | 4 |
| calendar_effect | 40 | 6/40 = 15.0% | 24/40 = 60.0% | 19/26 = 73.1% | 5 | 1 | 19 | 15 | 14 |
| momentum | 39 | 3/39 = 7.7% | 21/39 = 53.8% | 20/35 = 57.1% | 1 | 2 | 20 | 16 | 4 |
| mean_reversion | 39 | 0/39 = 0.0% | 13/39 = 33.3% | 13/26 = 50.0% | 0 | 0 | 13 | 26 | 13 |
| volatility_regime | 40 | 0/40 = 0.0% | 4/40 = 10.0% | 4/21 = 19.0% | 0 | 0 | 4 | 36 | 19 |

(Cells: pp = passed_2022_passed_2024; pf = passed_2022_failed_2024;
fp = failed_2022_passed_2024; ff = failed_2022_failed_2024; excl =
filter-excluded. Rows ordered by 2024 pass-rate descending. Cross-tab
sanity: pp totals 8 = cohort (a); pf totals 5 = cohort (c) failures;
totals 198. ✓)

**volume_divergence (n=40; 2022 4/40 = 10.0%; 2024 25/40 = 62.5%;
filtered 23/36 = 63.9%; cohort (a) 2; partition primary 8/12 = 66.7%
vs audit_only 17/28 = 60.7%, +6.0pp primary direction).** The theme
with the largest absolute swing in pass rate across the two tested
regimes (4 → 25 of 40) and the second-highest 2024 pass rate.
PHASE2C_6.6 §8 named volume_divergence's 2022 failure-mode signature
as drawdown-dominated (29/40 candidates failed the 25% drawdown
criterion). The 2024 profile shows drawdown-failure attenuated to
10/40, with 7/40 return-failure and 10/40 sharpe-failure. The
descriptor *drawdown-attenuated* is bounded statistical observation,
not mechanism claim — what changed in the failure-mode profile is
visible at the per-candidate JSON level; why it changed is §6
category 3 territory and remains undetermined within this batch.
Within-theme partition direction (primary 66.7% > audit_only 60.7%)
matches §5 population-level direction (+6.0pp). Cohort (a) cross-
regime survivors: 2 (`0845d1d7`, `f4977b3e`).

**calendar_effect (n=40; 2022 6/40 = 15.0%; 2024 24/40 = 60.0%;
filtered 19/26 = 73.1%; cohort (a) 5; partition primary 3/7 = 42.9%
vs audit_only 21/33 = 63.6%, −20.7pp — REVERSES §5 direction).**
Calendar_effect has the highest 2022 pass rate (6/40) and the
second-highest 2024 pass rate (24/40); both are the strongest
within-batch single-regime survival rates among the 5 themes.
Within-theme partition direction REVERSES §5 population-level
direction: primary partition (42.9%) passes 2024 at a lower rate
than audit_only partition (63.6%), a −20.7pp gap in the audit-only
direction. Calendar_effect contributes 5 of 8 cohort (a)
cross-regime survivors (`9dc5c373`, `c200a95d`, `94b3d1fd`,
`1d6a587a`, `7f296ee9`) — the largest cross-regime intersection
count among the 5 themes. Both observations (within-theme
partition inversion AND cohort (a) dominance) are descriptive
structural patterns within this batch and these two regimes.
Mechanism claims about calendar_effect (regime-orthogonal,
calibrated-for-validation_2024-like-regimes, regime-robust) are
forbidden per §6 category 3.

**momentum (n=39; 2022 3/39 = 7.7%; 2024 21/39 = 53.8%; filtered
20/35 = 57.1%; cohort (a) 1; partition primary 3/3 = 100% vs
audit_only 18/36 = 50.0%, +50pp — sensitivity high at primary
n=3).** Momentum's primary partition contains only 3 candidates.
All 3 passed 2024 (3/3 = 100%); 18 of 36 audit_only candidates
passed 2024 (50.0%). The within-theme +50pp gap matches §5
population-level direction but the primary n=3 makes the magnitude
sensitivity high — a single primary candidate flipping outcome
would shift the gap to 67% / 33%. PHASE2C_6.6 §8 had momentum's
2022 within-theme inversion (0/3 primary, 3/36 audit-only). The
2024 inversion direction (primary > audit) flips relative to 2022
at the within-theme level; the magnitude is sensitive to the n=3
primary partition. Failure-mode profile: 2022 dominated by
drawdown/sharpe/return failures (29/29/30 of 39); 2024 attenuated
to 16/2/2 dd/sh/ret with 1 zero-trade. Drawdown-failure rate
roughly halved; sharpe-failure and return-failure rates dropped
substantially. The descriptor *drawdown-attenuated* applies; the
mechanism is undetermined. Cohort (a) cross-regime survivors: 1
(`18c2a5f7`, the candidate with the highest 2022 holdout Sharpe
in the entire batch at hd22_sh=+0.960, ranked at WF Sharpe
−1.5107 by the gate).

**mean_reversion (n=39; 2022 0/39 = 0.0%; 2024 13/39 = 33.3%;
filtered 13/26 = 50.0%; cohort (a) 0; partition primary 7/14 =
50.0% vs audit_only 6/25 = 24.0%, +26pp — primary direction).**
Mean_reversion's failure-mode signature SHIFTED across regimes,
not attenuated. PHASE2C_6.6 §8 named the 2022 signature as
*active-loss dominant*: across the 39 candidates, 26 failed
drawdown, 27 failed Sharpe, 26 failed return — active-loss
dominant across the engaging subset (35/39); 4/39 fired <5 trades
during 2022. The 2024 signature is mixed: 13 drawdown failures,
12 zero-trades, 13 trade-count failures, 2 sharpe failures, 2
return failures. The drawdown-failure rate halved (26 → 13);
trade-count failures emerged as a comparable signature category
(13/39 candidates fired below 5 trades against 2024). Mean_reversion
2024 candidates fired less and lost less than mean_reversion 2022
candidates — descriptive register, not mechanism claim. Within-
theme partition direction matches §5 (primary 50.0% > audit_only
24.0%, +26pp). Cohort (a): 0 cross-regime survivors. The 13 2024
survivors include 0 candidates that survived 2022 — mean_reversion's
2024 survivor population is entirely disjoint from any 2022 survivor.

**volatility_regime (n=40; 2022 0/40 = 0.0%; 2024 4/40 = 10.0%;
filtered 4/21 = 19.0%; cohort (a) 0; partition primary 1/8 = 12.5%
vs audit_only 3/32 = 9.4%, +3.1pp — primary direction).**
Volatility_regime's failure-mode signature *non-engagement* persists
across regimes. PHASE2C_6.6 §8 noted 18 of 40 volatility_regime
candidates fired zero trades during 2022 (45% non-engagement). The
2024 profile is structurally identical: 19 of 40 fired zero trades
(47.5% non-engagement). The non-engagement signature is the
dominant failure mode in both tested regimes. Of the 19 candidates
that did engage in 2024, 4 passed; the 21 that engaged but didn't
pass split across drawdown / sharpe / return failures. The
filter-exclusion rate for volatility_regime is the highest among
the 5 themes (19/40 = 47.5%, matching the zero-trade count).
Within-theme partition direction matches §5 (primary 12.5% >
audit_only 9.4%, +3.1pp). Cohort (a): 0 cross-regime survivors.

**Closing synthesis.**

The by-theme view contributes four structural observations beyond
§5's population-level finding. None of the four implies a
theme-level mechanism; all four describe what the multi-regime cuts
show within this batch and these two regimes.

*Within-2024 partition direction is theme-dependent.* §5's
population-level "primary > audit_only" direction (50.0% vs
42.2%, +7.8pp) holds at the population level but is NOT uniform
across themes. Four of five themes match the §5 direction
(volume_divergence +6.0pp; momentum +50pp at n=3 sensitivity;
mean_reversion +26pp; volatility_regime +3.1pp). Calendar_effect
inverts the direction (primary 42.9% < audit_only 63.6%, −20.7pp
in the audit-only direction). The §5 population-level direction
is consistent with the majority of themes but masks a
theme-specific inversion the by-theme view surfaces.

*Cohort (a) cross-regime survivors cluster in three themes.* The 8
candidates passing both regimes split as 5 calendar_effect + 2
volume_divergence + 1 momentum. Mean_reversion (n=39) and
volatility_regime (n=40) contribute zero cohort (a) candidates
between them. Calendar_effect dominates the cross-regime
intersection count (5 of 8 = 62.5%), but §8 does not interpret
that dominance as mechanism evidence. The observation is
descriptive structural heterogeneity; §6 category 3 forbids
mechanism claims about calendar_effect's distinctive position
within this batch and these two regimes.

*Failure-mode signatures differ across themes in their
regime-persistence pattern.* Volatility_regime's non-engagement
signature persists from 2022 to 2024 (18/40 → 19/40 zero-trades).
Mean_reversion's 2022 active-loss signature shifted to a 2024
mixed signature (drawdown-failure halved; trade-count failures
emerged as comparable category). Volume_divergence and momentum
showed drawdown-attenuated 2024 profiles relative to their 2022
drawdown-dominated profiles. Calendar_effect's failure profile is
the lowest in absolute count across both regimes — calendar_effect
has the highest 2022 pass rate (6/40) and the second-highest
2024 pass rate (24/40), with correspondingly low failure counts
in both regimes. The signature shifts are descriptive
profile-level observations; mechanism reading is §9's territory.

*Bounded contribution beyond §5.* The by-theme view shows
regime-dependence direction is theme-dependent (4 of 5 themes
match §5 direction; 1 inverts) and the cross-regime intersection
clusters by theme rather than spreading uniformly. §5's headline
("regime-dependent and not robustly preserved across the two
tested regimes") holds at population level; §8 surfaces
theme-level heterogeneity that §5's population-level cuts could
not. The contribution is descriptive structural observation, not
adjudication of mechanism. Per §6 category 3, the data does not
distinguish among regime-mismatch / pattern-overfit / calibration-
coupling explanations for the within-theme patterns observed; §9
reads the implications forward for follow-up arc design.


## 9. Implications for follow-up scoping

This section enumerates open questions §5/§7/§8 raise and decisions
follow-up scoping will need to consider. **Mechanisms named in this
section are hypotheses for follow-up, not conclusions from this
arc.** §9 does not make recommendations or pre-commit follow-up
arc designs; the methodology discipline established in earlier
closeouts and codified in [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
§7 (asymmetric-confidence rule for n=2 evidence) holds throughout:
direction-of-asymmetry claims are confident at n=2; mechanism
claims among the three §6 category 3 candidates require either
Path C calibration variation or multi-regime evaluation at n≥3 to
distinguish, and neither is part of this arc.

### 9.A — Open questions this arc raises but does not answer

**Q-A1: Three-mechanism candidate explanation — empirically
underdetermined.** §6 category 3 names regime-mismatch,
pattern-overfit, and calibration-coupling as three explanations
that all produce §5's regime-dependent pattern. Distinguishing
among them requires either (a) Path C calibration variation
within a regime, which would distinguish calibration-coupled
effects from regime-coupled or pattern-coupled effects, or (b)
multi-regime evaluation at n≥3, which would distinguish
regime-mismatch from pattern-overfit at population level. Neither
path is part of this arc. The empirical underdetermination is
structural at n=2 regimes; PHASE2C_7.1's evidence base is
sufficient for the direction-of-asymmetry claims §5 makes
(within-2024 partition direction inverts relative to PHASE2C_6's
2022 anti-selection; cross-regime intersection direction mirrors
2022 anti-selection) but insufficient for mechanism-among-three
claims. Per METHODOLOGY_NOTES §7, this is the canonical
asymmetric-confidence pattern.

**Q-A2: Within-2024 partition direction theme-dependence —
regime-specific or theme-specific?** §8 surfaces calendar_effect's
within-theme inversion (primary 3/7 = 42.9% < audit_only 21/33 =
63.6%, −20.7pp gap in audit-only direction) against §5's 4-of-5-
themes-match population direction. The inversion is observable in
this batch and these two regimes; whether calendar_effect inverts
in additional regimes (regime-specific calendar_effect inversion)
or whether the WF gate underrates calendar_effect candidates
structurally (theme-specific selection) is empirically
undetermined from n=2 regimes. Distinguishing these candidate
framings would require multi-regime evaluation across additional
regimes selected by a future scoping document.

**Q-A3: Cross-regime intersection theme-clustering — generalize or
batch-specific?** Cohort (a)'s 5+2+1 distribution across themes
(5 calendar_effect + 2 volume_divergence + 1 momentum) is
observable in this batch. Whether this clustering pattern persists
across additional regimes or different candidate populations is
undetermined. The cohort (a) sample is n=8; cross-regime
clustering claims would require larger cross-regime intersection
populations to test, which structurally requires either larger
batches or multi-regime evaluation generating new
cross-regime-intersection cohorts.

**Q-A4: Failure-mode signature persistence vs shift — what does
each pattern indicate?** §8 surfaces two distinct cross-regime
patterns: volatility_regime's non-engagement signature persists
(18/40 → 19/40 zero-trades); mean_reversion's 2022 active-loss
shifts to 2024 mixed (drawdown-failure halved, trade-count
failures emerge). Whether persistence-vs-shift maps to mechanism
distinctions is empirically underdetermined within this batch.
Candidate framings include "persistence indicates alpha-thesis-
misalignment with regime structure" and "shift indicates
regime-specific entry-condition misfit," but neither is supported
or refuted by this batch's evidence — both are candidate
hypotheses for follow-up adjudication, not adjudicated mechanism
claims. Distinguishing among candidate framings would require
either Path C calibration variation or multi-regime evaluation at
n≥3.

**Q-A5: PHASE2C_6 carry-forward asymmetry — primary structurally
weaker on cross-regime than audit_only?** §5's 0/1 primary
carry-forward versus 8/12 audit_only carry-forward (66.7%) shows
directional asymmetry, but the primary n=1 makes the magnitude
bound. Per §6 category 1, the audit_only n=12 carries
single-candidate-flip sensitivity (10/14 = 71.4% / 8/14 = 57.1%);
the primary n=1 is even more sensitive. Whether primary
candidates structurally have lower cross-regime carry-forward
than audit_only candidates, or whether the 0/1 outcome is
small-n sampling, is empirically undetermined. Multi-regime
evaluation at n≥3 against larger primary populations would
clarify the structural-vs-sampling question.

### 9.B — Decisions follow-up scoping will need to consider

§9 names these decisions; it does NOT recommend or pre-commit any
of them. Follow-up scoping is a separately scoped, separately
reviewed process; PHASE2C_7.1's contribution to follow-up scoping
is the question enumeration above, not the decision adjudication
below.

**Q-B1: Multi-regime evaluation at n≥3.** §6 category 3 mechanism
question requires either Path C calibration variation or
multi-regime evaluation at n≥3 to disambiguate. Path C is
within-regime; multi-regime at n≥3 is across-regime. Different
mechanism questions are addressable by different paths; follow-up
scoping would weigh which path addresses which mechanism most
directly. The 2025 test split is preserved touched-once
throughout this discussion (CLAUDE.md hard rule); additional
regimes would come from additional historical regimes selected by
a future scoping document, with specific regime selection
rationale being follow-up scoping territory. The question §9
raises is whether to invest in multi-regime evaluation
infrastructure (orchestration, regime-attestation discipline,
candidate-aligned cross-regime artifact pipeline) given the
mechanism-question structure §6 names.

**Q-B2: Calibration variation within a regime (Path C revisit).**
Path C was deferred per PHASE2C_7.0 §5 in favor of Path B. §8's
calendar_effect within-theme inversion + cohort (a) clustering
surface descriptive patterns that the WF gate's selection power
against validation_2024 cannot be fully characterized as
calibration-coupled, regime-coupled, or pattern-coupled from the
available evidence. Whether to prioritize Path C calibration
variation now or defer further is follow-up scoping territory;
the operational rationale would depend on what mechanism
question Path C is being asked to address. PHASE2C_7.1's
contribution is making the calendar_effect pattern visible (§8)
and naming the three-mechanism candidate explanation (§6 category
3); the Path C decision proper is follow-up scoping work.

**Q-B3: Cohort (a) deep-dive as a pre-registered question.** The
8 cohort (a) candidates enumerated in §7 are diagnostic material
per §7's framing, not strategy recommendations. Whether to
investigate this cohort under a pre-registered question (e.g.,
"do cohort (a) candidates carry forward to a third regime?";
"do cohort (a) candidates' theme-clustering pattern persist
across additional regimes?") is a follow-up scoping decision.
This mirrors PHASE2C_6.6 §9's framing for the 12 audit-only
survivors: diagnostic material requires explicit pre-registered
investigation, not post-hoc promotion based on cross-regime
survival within a single batch. Cohort (a) candidates have not
been evaluated against validation, test, or forward live data;
no deployment claim, paper-trading claim, or "this strategy
works" claim is made or implied.

**Q-B4: DSR infrastructure investment given continued n=1
primary cross-regime.** PHASE2C_6.6 §9 raised the DSR (Deflated
Sharpe Ratio) infrastructure question against PHASE2C_6's n=1
primary 2022-survivor (`bf83ffec`). PHASE2C_7.1 has 22 primary
2024-survivors but 0 primary cross-regime survivors. The DSR
question shifts structure rather than answers: from "is
single-regime DSR meaningful at n=1 primary survivor?" to "what
evidence base does cross-regime DSR require?" The PHASE2C_7.1
data does not answer the DSR question; it surfaces an additional
dimension (cross-regime evidence structure) that follow-up
scoping would weigh against alternative infrastructure
investments (multi-regime evaluation per Q-B1; calibration
variation per Q-B2).

### 9.C — Explicit non-decisions

This closeout does NOT recommend:

- That the WF gate be replaced or supplemented with alternative
  selection signals.
- That any specific theme (calendar_effect, mean_reversion,
  volume_divergence, momentum, volatility_regime) be prioritized,
  deprioritized, or removed from future Proposer batches.
- That cohort (a), cohort (b), or cohort (c) candidates be
  promoted to validation, test, paper-trading, or live evaluation.
- That DSR infrastructure investment be cancelled or accelerated.
- That a specific follow-up arc be initiated; nor that follow-up
  be deferred.
- That the trade-count filter threshold be revised from `>= 20`
  (§5.3 Rule 1 pre-specification anti-tuning discipline holds).
- That `config/environments.yaml` be modified for additional
  regimes (the IMMUTABLE-config CLAUDE.md hard rule holds; any
  modification would be a separately scoped decision).

**Discipline closing.** The §9 forward-pointers above are
*hypotheses for follow-up scoping*, not *conclusions from
PHASE2C_7.1*. PHASE2C_7.1 produced the artifact set + closeout
with the three-cut adjudication §5 carries; follow-up arc design
is separately scoped, separately reviewed, separately committed.
Anti-pre-naming carries forward — §9 references "follow-up
scoping" or "a follow-up arc" generically rather than naming
specific arc identifiers, regimes, or strategies. §10 names
methodology forward-pointers (operational scaffolding for
disciplines that survived this arc). The two sections together
form the closing forward-pointing arc; neither prescribes the
next arc's design.


## 10. Methodology-discipline observations

This section enumerates methodology principles that surfaced or
strengthened during PHASE2C_7.1's drafting cycles. The register
distinguishes from §9: §10's principles are claims about *how the
work was done* that subsequent arcs should preserve, not hypotheses
for follow-up. Mechanism implications and forward-pointing
adjudications belong in §9; §10 catalogs operational discipline
patterns that survived this arc.

Each observation cross-references the relevant
[`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
section that supplied the canonical principle, identifies whether
PHASE2C_7.1 strengthened or refined the principle (rather than
introducing a new one), and forward-points to a recommended
METHODOLOGY_NOTES.md update.

**Observation 1 — Recompute-before-prose discipline.**

Per METHODOLOGY_NOTES.md §1's empirical-verification principle,
factual claims trace to canonical sources. PHASE2C_7.1 surfaced a
stage-specificity refinement: data-density section drafting
recomputes canonical numerical claims against artifact data
(`comparison.csv`, aggregate JSONs) at framing-summary stage,
before prose drafts. Three concrete catches within this arc:

- §7 framing summary's "7 of 8 cohort (a) candidates carry WF≤0"
  recomputed to actual "6 of 8" against `comparison.csv` — a
  1-of-8 precision-overshoot caught pre-prose.
- §8 framing summary lacked the calendar_effect within-theme
  inversion observation; recompute against per-theme partition
  data surfaced it as a load-bearing structural observation that
  became §8 closing synthesis bullet 1.
- §8 framing summary's "all candidates engaged-and-lost"
  universalized past the data; recompute confirmed 35/39
  engaged-and-lost + 4/39 fired <5 trades, tightening the framing.

Strengthens METHODOLOGY_NOTES.md §1 by adding "framing-summary
stage as the recompute checkpoint" specificity. The catch-window
shifts earlier in the drafting cycle relative to PHASE2C_6.7's
post-prose Codex catch of the "bit-identical" defect. Cost: one
canonical-artifact-recompute per data-density section. Payoff:
precision-overshoot defects surface before they harden into prose.
Recommended for METHODOLOGY_NOTES.md §1 update post-closeout.

**Observation 2 — Path-2 outline-first drafting for load-bearing interpretive sections.**

PHASE2C_7.1 drafted §5 (selection-power adjudication) FIRST as a
standalone cycle before §3/§4 (evidence-context), §6 (bounded-
claims firewall), §7 (cohort enumeration), §8 (by-theme), and §9
(mechanism implications) — all of which depend on §5's framing
holding stable. The §5 framing established the three-cut
adjudication ("regime-dependent and not robustly preserved across
the two tested regimes"); §3/§4/§6/§7/§8/§9 then drafted as
evidence-and-bounds sections that supported §5's framing without
re-litigating the adjudication.

The structural rationale: load-bearing interpretive sections with
multi-direction findings need framing-first treatment because
evidence sections drafted ahead of framing carry pre-commit risk.
PHASE2C_6.6 was single-regime with a single-direction headline
(anti-selection against 2022 within this batch); §5 framing was
simpler and Path-2 outline-first wasn't structurally necessary.
PHASE2C_7.1's multi-regime evidence base required Path-2
outline-first because §5's headline carries multi-direction
findings (within-2024 inversion + cross-regime intersection mirror
+ PHASE2C_6 carry-forward asymmetry) that §3-§8 had to support
collectively.

This is a new methodology principle. Recommended for
METHODOLOGY_NOTES.md as a candidate new section codifying when
Path-2 outline-first drafting applies — specifically, for
load-bearing interpretive sections with multi-direction findings.
Single-direction findings do not structurally require Path-2;
prior arcs' single-direction sections drafted cleanly without it.

**Observation 3 — V7 grep-able citation discipline.**

Per METHODOLOGY_NOTES.md §1, factual claims trace to canonical
artifacts. PHASE2C_7.1's V7 discipline operationalizes this with
grep-ability as the operational specificity: every numerical
claim in closeout prose carries a back-pointer to a canonical
artifact field (JSON path or CSV row+field), grep-able by a
future reader investigating the claim. Specific examples in §5:
`comparison.json .filter_survivor_cross_tab.audit_only.passed_2022_passed_2024=8`;
`comparison.csv` row `bf83ffec97485f47.holdout_2024_sharpe = -0.6327...`.

V7 enforcement at section-seal turns caught zero precision-
overshoot defects post-enforcement, compared to PHASE2C_6.7's
post-prose Codex catch of the "bit-identical" defect. The
discipline catches the defect class structurally rather than
relying on adversarial review to surface it. Adversarial review
remains complementary — it catches what V7 misses (e.g., framing
overstatements, register drift, scope creep) — but the precision-
overshoot subclass is now structurally pre-empted.

Strengthens METHODOLOGY_NOTES.md §1 by adding the grep-able-
citation specificity. Recommended for METHODOLOGY_NOTES.md §1
update post-closeout.

**Observation 4 — Anti-pre-naming discipline carryforward.**

Per PHASE2C_7.0 §6's anti-pre-naming discipline (§9 forward-
pointers reference "follow-up scoping" generically rather than
specific arc identifiers), PHASE2C_7.1 §9 tested cleanly through
the highest-pre-naming-risk section. Body prose grep returned
zero "PHASE2C_8" references. Subsection 9.B Q-B1 originally named
specific historical regimes ("2018 bear / 2020 COVID drawdown /
2021 bull peak") as illustrative examples; both reviewers caught
the pre-naming + pre-characterization risk, and Charlie's
directive replaced with "additional historical regimes selected
by a future scoping document."

Discipline pattern strengthens with each arc. PHASE2C_6.6 §9 used
"PHASE2C_7+ scoping" phrasing for forward-pointers (mild
pre-naming via the "+" suffix); PHASE2C_7.1 §9 tightened to
"follow-up scoping" generic phrasing. The §10 surfacing of
anti-pre-naming as standing discipline makes it explicit for
future arcs rather than relying on per-arc rediscovery.

Anti-pre-naming is structural discipline, not empirical
verification. Recommended for METHODOLOGY_NOTES.md as a candidate
new section codifying the principle. The actual section structure
(new section vs strengthening existing) is METHODOLOGY_NOTES.md
update territory, not §10 territory.

**Observation 5 — Closeout-assembly checklist as running drafting-cycle pattern.**

PHASE2C_7.1 surfaced an explicit closeout-assembly checklist
pattern: tracked non-blocking assembly fixes accumulate in a
running list during drafting cycles, and closeout-assembly
applies all fixes uniformly at the unified assembly stage. Six
fixes accumulated across §3-§9 drafting cycles, including: a
§5 cross-reference (line 29 §3→§4 referent fix), all section
drafting-notes appendices stripping, §7 per-candidate row
population from per-candidate JSON files, §7 cohort (b) full
22-row table population at assembly, §7 cohort population
scripts produce byte-identical output across runs, and §5 line
56-57 inline caveat addition.

The pattern existed implicitly in PHASE2C_6.6 — fixes surfaced
during drafting cycles got mixed mid-cycle and assembly-time
treatment ad-hoc. PHASE2C_7.1 makes the batch-for-assembly
pattern operational with the running checklist. Each tracked
fix carries a specific location and fix shape; closeout-assembly
verification applies them uniformly without per-section re-seal
cost.

The framing matters: tracked fixes are non-blocking assembly
work, not unresolved defects deferred. Each entry on the
checklist has a known shape and a known location; the
assembly-stage application is operational completion, not
defect resolution. The pattern lets drafting cycles preserve
forward momentum without re-opening sealed sections for small
cross-reference fixes that accumulate naturally across cycles.

Recommended for METHODOLOGY_NOTES.md as a candidate new section
codifying closeout-assembly-as-batch-fix-stage discipline.

**Closing forward-pointer.**

Per the prior pattern (PHASE2C_6.6 closeout commit → separate
METHODOLOGY_NOTES.md update commit at `536f737`), this closeout
recommends a follow-on METHODOLOGY_NOTES.md update commit
absorbing the principles enumerated above. PHASE2C_7.1's closeout
commit contains only this closeout document; the METHODOLOGY_NOTES.md
update is a separate follow-on commit, separately scoped and
separately reviewed. The update commit is recommended by this
closeout but not guaranteed until separately reviewed and
committed; §10's enumeration is its input, not its
authorization.


## 11. References and reproducibility

This section provides runnable commands and queries to reproduce
PHASE2C_7.1's load-bearing claims from the canonical artifact
set. The coverage is at load-bearing-claim level, not exhaustive
sentence-level — the queries below reproduce the verdict (§1)
and supporting cuts (§5/§7/§8/§3 universe symmetry); supporting
sentences in §3-§10 trace via the V7 citations embedded in each
section's prose.

All commands and queries below assume the working directory is
the `btc-alpha-pipeline` repo root (`cd /path/to/btc-alpha-pipeline`
before running). Queries assume the canonical artifact set is
present at `data/phase2c_evaluation_gate/`; if artifacts are not
present, run the §11.A commands first to regenerate them
deterministically.

### §11.A — Run commands

The four runs that produce PHASE2C_7.1's canonical artifact set:

```bash
# Step 1c — smoke vs validation_2024 (4 candidates)
python scripts/run_phase2c_evaluation_gate.py \
  --source-batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \
  --candidate-hashes 0bf34de1,812216d4,9436a54b,cc295177 \
  --run-id smoke_2024_v1 --regime-key v2.validation

# Step 2 — full audit vs validation_2024 (198 candidates)
python scripts/run_phase2c_evaluation_gate.py \
  --source-batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \
  --universe audit --run-id audit_2024_v1 --regime-key v2.validation

# Step 3 — trade-count filter (post-evaluation analytical pass)
python scripts/filter_evaluation_gate.py \
  --primary-run-id audit_2024_v1 \
  --output-run-id audit_2024_v1_filtered

# Step 4 — candidate-aligned 2022-vs-2024 comparison
python scripts/compare_2022_vs_2024.py \
  --audit-v1-dir data/phase2c_evaluation_gate/audit_v1 \
  --audit-2024-v1-dir data/phase2c_evaluation_gate/audit_2024_v1 \
  --audit-2024-v1-filtered-dir data/phase2c_evaluation_gate/audit_2024_v1_filtered \
  --output-dir data/phase2c_evaluation_gate/comparison_2022_vs_2024_v1
```

### §11.B — Reproducibility queries

Six query blocks, each reproducing a load-bearing claim category.
Each query terminates with `# expected: <value>` trailing comment;
paste-and-run, compare output to expected.

**Query 1 — §1/§5 within-2024 partition cut.**

```python
import json
agg = json.load(open(
    "data/phase2c_evaluation_gate/audit_2024_v1/holdout_summary.json"
))
print(f"primary 2024:    "
      f"{agg['primary_universe_holdout_passed']}/"
      f"{agg['primary_universe_total']} = "
      f"{agg['primary_universe_holdout_passed']/agg['primary_universe_total']*100:.1f}%")
print(f"audit_only 2024: "
      f"{agg['audit_only_holdout_passed']}/"
      f"{agg['audit_only_total']} = "
      f"{agg['audit_only_holdout_passed']/agg['audit_only_total']*100:.1f}%")
# expected: primary 2024:    22/44 = 50.0%
#           audit_only 2024: 65/154 = 42.2%
```

**Query 2 — §1/§5 cross-regime intersection cut.**

```python
import json
cmp = json.load(open(
    "data/phase2c_evaluation_gate/comparison_2022_vs_2024_v1/comparison.json"
))
def pp_count(partition):
    s = cmp["filter_survivor_cross_tab"][partition]["passed_2022_passed_2024"]
    x = cmp["filter_excluded_cross_tab"][partition]["passed_2022_passed_2024"]
    return s + x
print(f"primary cross-regime:    {pp_count('primary')}/44")
print(f"audit_only cross-regime: {pp_count('audit_only')}/154")
# expected: primary cross-regime:    0/44
#           audit_only cross-regime: 8/154
```

**Query 3 — §1/§5/§7 cohort enumerations.**

```python
import csv
rows = list(csv.DictReader(open(
    "data/phase2c_evaluation_gate/comparison_2022_vs_2024_v1/comparison.csv"
)))
cohort_a = [r for r in rows
            if r["holdout_2022_passed"] == "True"
            and r["holdout_2024_passed"] == "True"]
cohort_b = [r for r in rows
            if r["partition"] == "primary"
            and r["holdout_2022_passed"] == "False"
            and r["holdout_2024_passed"] == "True"]
cohort_c = [r for r in rows if r["holdout_2022_passed"] == "True"]
cohort_c_pass24 = [r for r in cohort_c if r["holdout_2024_passed"] == "True"]
cohort_c_fail24 = [r for r in cohort_c if r["holdout_2024_passed"] == "False"]
print(f"cohort (a) cross-regime survivors: {len(cohort_a)}")
print(f"cohort (b) primary 2024 survivors that failed 2022: {len(cohort_b)}")
print(f"cohort (c) PHASE2C_6 holdout-survivors: {len(cohort_c)} "
      f"({len(cohort_c_pass24)} passed 2024 + "
      f"{len(cohort_c_fail24)} failed 2024)")
# expected: cohort (a) cross-regime survivors: 8
#           cohort (b) primary 2024 survivors that failed 2022: 22
#           cohort (c) PHASE2C_6 holdout-survivors: 13 (8 passed 2024 + 5 failed 2024)
```

**Query 4 — §8 per-theme cross-regime cross-tab.**

```python
import csv
from collections import defaultdict
rows = list(csv.DictReader(open(
    "data/phase2c_evaluation_gate/comparison_2022_vs_2024_v1/comparison.csv"
)))
xtab = defaultdict(lambda: {"pp": 0, "pf": 0, "fp": 0, "ff": 0})
for r in rows:
    p22 = r["holdout_2022_passed"] == "True"
    p24 = r["holdout_2024_passed"] == "True"
    cell = ("pp" if p22 and p24 else
            "pf" if p22 and not p24 else
            "fp" if not p22 and p24 else "ff")
    xtab[r["theme"]][cell] += 1
for t in sorted(xtab):
    c = xtab[t]
    print(f"{t:<22} pp={c['pp']:>2} pf={c['pf']:>2} "
          f"fp={c['fp']:>2} ff={c['ff']:>2}")
# expected:
#   calendar_effect        pp= 5 pf= 1 fp=19 ff=15
#   mean_reversion         pp= 0 pf= 0 fp=13 ff=26
#   momentum               pp= 1 pf= 2 fp=20 ff=16
#   volatility_regime      pp= 0 pf= 0 fp= 4 ff=36
#   volume_divergence      pp= 2 pf= 2 fp=23 ff=13
```

**Query 5 — §3 universe-symmetry assertion (regression check).**

```python
import csv
rows_22 = list(csv.DictReader(open(
    "data/phase2c_evaluation_gate/audit_v1/holdout_results.csv"
)))
rows_24 = list(csv.DictReader(open(
    "data/phase2c_evaluation_gate/audit_2024_v1/holdout_results.csv"
)))
hashes_22 = {r["hypothesis_hash"] for r in rows_22}
hashes_24 = {r["hypothesis_hash"] for r in rows_24}
sym_diff = hashes_22 ^ hashes_24
print(f"audit_v1 hashes: {len(hashes_22)}")
print(f"audit_2024_v1 hashes: {len(hashes_24)}")
print(f"symmetric difference: {len(sym_diff)} (expected 0)")
# expected: audit_v1 hashes: 198
#           audit_2024_v1 hashes: 198
#           symmetric difference: 0 (expected 0)
```

**Query 6 — §4 comparison schema version + lineage validation.**

```python
import json
from pathlib import Path
from backtest.wf_lineage import (
    check_evaluation_semantics_or_raise,
    ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1,
)
# §4 derived analysis attestation: comparison.json carries
# comparison_schema_version = "comparison_schema_v1"
cmp_path = Path("data/phase2c_evaluation_gate/comparison_2022_vs_2024_v1/comparison.json")
cmp = json.load(open(cmp_path))
assert cmp["comparison_schema_version"] == "comparison_schema_v1"
print(f"comparison schema: {cmp['comparison_schema_version']}")
# expected: comparison schema: comparison_schema_v1

# §3/§4 schema-discriminator round-trip:
# new schema branch validates audit_2024_v1 + audit_2024_v1_filtered
# legacy absent-field branch validates audit_v1
# Regression: PHASE2C_6 artifacts (no artifact_schema_version field)
# still validate under the absent-field branch of the schema
# discriminator. This guards against future schema-evolution
# breakage where new required fields would invalidate existing
# artifacts.
base = Path("data/phase2c_evaluation_gate")
counts = {"new_schema": 0, "legacy_schema": 0}
for run in ["audit_v1", "audit_2024_v1", "audit_2024_v1_filtered"]:
    run_dir = base / run
    paths = [run_dir / "holdout_summary.json"] + sorted(
        run_dir.glob("*/holdout_summary.json"))
    for p in paths:
        d = json.load(open(p))
        check_evaluation_semantics_or_raise(d, artifact_path=str(p))
        if d.get("artifact_schema_version") == ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1:
            counts["new_schema"] += 1
        else:
            counts["legacy_schema"] += 1
print(f"validated: new_schema={counts['new_schema']} "
      f"legacy_schema={counts['legacy_schema']}")
# expected: comparison schema: comparison_schema_v1
#           validated: new_schema=345 legacy_schema=199
# (345 = 199 audit_2024_v1 [198 per-candidate + 1 aggregate]
#       + 145 audit_2024_v1_filtered [144 per-candidate + 1 aggregate]
#       + 1 smoke if applicable; smoke not included in this loop.
#  199 = 198 audit_v1 per-candidate + 1 aggregate.)
```

### §11.C — Lineage round-trip

Query 6 above performs the lineage round-trip validation across
the three production artifact sets. The three structural
properties verified:

- New schema branch (`artifact_schema_version="phase2c_7_1"`)
  validates `audit_2024_v1/` + `audit_2024_v1_filtered/`
  artifacts.
- Legacy absent-field branch validates PHASE2C_6 `audit_v1/`
  artifacts (regression: legacy artifacts continue to validate
  without modification).
- Comparison artifact (`comparison_2022_vs_2024_v1/comparison.json`)
  carries `comparison_schema_version="comparison_schema_v1"` per
  §4 derived-analysis attestation.

If any artifact fails to validate, `check_evaluation_semantics_or_raise`
raises `ValueError` with the failing field; the round-trip query
exits non-zero.

### §11.D — Cross-references

**Closeout documents (cross-arc):**
- PHASE2C_6 closeout: [`docs/closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md`](PHASE2C_6_EVALUATION_GATE_RESULTS.md)
- PHASE2C_7.0 scoping decision: [`docs/phase2c/PHASE2C_7_SCOPING_DECISION.md`](../phase2c/PHASE2C_7_SCOPING_DECISION.md)
- PHASE2C_7.1 implementation spec: [`docs/phase2c/PHASE2C_7_1_PLAN.md`](../phase2c/PHASE2C_7_1_PLAN.md)

**Discipline anchors:**
- Methodology principles: [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) — §1 empirical-verification, §7 asymmetric-confidence rule for n=2 evidence
- Walk-forward boundary semantics: [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md) Section RS (corrected-engine consumption discipline)
- Project hard rules: `CLAUDE.md` (immutable config; touched-once 2025; lineage attestation; bounded-claim discipline)

**Canonical config:**
- Date splits + regime blocks: `config/environments.yaml` (immutable per CLAUDE.md hard rule; v2 schema)
- Execution semantics: `config/execution.yaml` (effective-7bps cost model, immutable per CLAUDE.md hard rule)

**Engine + lineage:**
- Engine: `backtest/engine.py` — corrected-engine commit `eb1c87f`, lineage tag `wf-corrected-v1`; `_load_regime_block_config` parameterized regime loader; `_resolve_passing_criteria_with_inheritance` cross-block coupling resolver
- Lineage helper: `backtest/wf_lineage.py` — schema discriminator (`check_evaluation_semantics_or_raise`); `REGIME_KEY_LABEL_MAPPING` constant (regime key → label mapping referenced in §3/§4); `ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1` constant

**Producer scripts:**
- Step 1/2 producer: `scripts/run_phase2c_evaluation_gate.py` (extends with `--regime-key` flag and three new lineage fields)
- Step 3 filter: `scripts/filter_evaluation_gate.py` (`MIN_TOTAL_TRADES = 20` pinned per §5.3 Rule 1)
- Step 4 comparison: `scripts/compare_2022_vs_2024.py` (universe symmetry assertion + cross-tab construction)

**Canonical artifact directories (read by reproducibility queries):**
- `data/phase2c_evaluation_gate/audit_v1/` — PHASE2C_6 baseline (read-only; not modified by this arc)
- `data/phase2c_evaluation_gate/audit_2024_v1/` — Step 2 producer artifact
- `data/phase2c_evaluation_gate/audit_2024_v1_filtered/` — Step 3 derived analytical artifact
- `data/phase2c_evaluation_gate/comparison_2022_vs_2024_v1/` — Step 4 comparison matrix
- `data/phase2c_evaluation_gate/smoke_2024_v1/` — Step 1c smoke (optional; reproduces only the 4-candidate smoke verification)

