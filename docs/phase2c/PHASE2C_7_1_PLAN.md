# PHASE2C_7.1 Implementation Specification — Path B

## 1. Scope and verdict

**This document specifies the implementation arc for PHASE2C_7
Path B — multi-regime evaluation of all 198 PHASE2C_6 candidates
against the 2024 validation regime. PHASE2C_7.0 (the scoping
decision) selected Path B; PHASE2C_7.1 implements it.**

**Project state at PHASE2C_7.1 spec drafting (2026-04-27).**

- Canonical main: `origin/main` at commit `f344a0e`
- Tags on main: `wf-corrected-v1` (corrected WF engine fix at
  commit `eb1c87f`), `phase2c-6-evaluation-gate-v1` (PHASE2C_6
  arc completion at `f344a0e`)
- PHASE2C_7.0 scoping decision: [`docs/phase2c/PHASE2C_7_SCOPING_DECISION.md`](PHASE2C_7_SCOPING_DECISION.md)
  (committed at `af8225f` on `claude/phase2c-7-scoping`, pushed to
  origin)
- Path B recommendation source: PHASE2C_7.0 §5 reasoning ladder
  (seven rungs); Charlie's explicit go on Path B given prior turn

**What PHASE2C_7.1 produces.**

A single producer run against all 198 candidates against 2024
validation regime, with a derived trade-count-filtered analytical
artifact, candidate-aligned 2022-vs-2024 comparative analysis, and
closeout document. Detailed implementation plan in §8; substantive
decisions on the trade-count filter pass in §5. Pre-pinned
decisions (D1, D2, D3 settled during PHASE2C_7.1 pre-drafting
adjudication following Charlie's path-B confirmation; the
regime-field schema settled during this spec's pre-drafting
reviewer adjudication):

| decision | resolution |
|---|---|
| **D1 trade-count filter** | Include secondary pass at `total_trades >= 20` in 2024 holdout (per §5) |
| **D2 2024 regime config source** | `config/environments.yaml` v2 split `validation` block as-defined |
| **D3 lineage attestation domain** | Reuse `single_run_holdout_v1`; add regime-context fields per §7 |
| **Regime-field schema** | Three fields stamped on artifacts: `artifact_schema_version`, `regime_key`, `regime_label` (per §7) |

**What PHASE2C_7.1 is NOT.**

- **Not a re-litigation of PHASE2C_7.0.** Path selection is sealed.
  PHASE2C_7.1 implements Path B; it does not revisit Paths A/C/D.
- **Not a methodology amendment.** [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  §1-§7 apply throughout PHASE2C_7.1; new methodology principles
  surfaced during PHASE2C_7.1 work are captured as a follow-up
  update (same hybrid handling as PHASE2C_6 §10).
- **Not a forward decision on next-arc scope.** PHASE2C_7.1's
  closeout will report findings and enumerate open questions; it
  does not pre-commit the next scoping arc's path.
- **Not a 2025 test split touch.** 2025 remains preserved
  touched-once across this arc (per PHASE2C_7.0 §6 universal
  out-of-scope item).

**Document structure.**

§2 names the input universe (198 candidates from PHASE2C_6) and
the canonical hash list source. §3 specifies the 2024 regime
configuration (v2 split validation block as-defined). §4 specifies
the evaluation gate (4-criterion AND-gate, same as PHASE2C_6). §5
specifies the trade-count filter sub-pass (threshold pinned;
empirical justification; pre-specification discipline). §6
specifies the producer artifact (extension to existing script;
CLI flag form; run_id naming). §7 specifies the lineage
attestation (regime-field schema; consumer guard extension). §8
provides the five-step implementation plan with sequential gating.
§9 names pass/fail criteria for the closeout. §10 names risks and
out-of-scope items.

## 2. Input universe

**The input universe is the 198 candidates from PHASE2C_6's batch
`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`.**

The candidates are evaluated under the corrected-engine artifacts
(post-`eb1c87f` engine fix; lineage tag `wf-corrected-v1`). Each
candidate has a stable `hypothesis_hash` that serves as the
canonical identifier across PHASE2C_6 and PHASE2C_7.1 artifacts.

**Canonical hash list source.**

The 198 hypothesis hashes are sourced from PHASE2C_6's audit_v1
canonical aggregate CSV at:

```
data/phase2c_evaluation_gate/audit_v1/holdout_results.csv
```

The `hypothesis_hash` column of this CSV enumerates the 198
candidates. PHASE2C_7.1's producer reads from this canonical
source rather than re-extracting from upstream batch metadata.
This preserves the candidate-aligned discipline: the 198
candidates evaluated against 2024 are identically the 198
candidates evaluated against 2022 in PHASE2C_6.

**Universe partition retained.**

The PHASE2C_6 partition into primary (`wf_test_period_sharpe >
0.5`, n=44) and audit-only (`wf_test_period_sharpe <= 0.5`, n=154)
is preserved in PHASE2C_7.1's artifacts. Each candidate's WF
sharpe and primary-vs-audit-only flag carry forward from PHASE2C_6
into the 2024 evaluation outputs, enabling the §4 Path B
expected observable "primary-vs-audit-only pass-rate comparison
for 2024" without external lookup.

## 3. 2024 regime configuration

**Source.** The 2024 regime is defined by the
`config/environments.yaml` v2 split `validation` block:

```yaml
validation:
  start: "2024-01-01"
  end: "2024-12-31"
  purpose: "Hyperparameter selection, leaderboard ranking (Phase 2B+)"
  notes: "BTC ETF approval era, halving year"
```

**Configuration access.** PHASE2C_7.1's producer extension (per
§6) reads this block via the regime-key parameter `--regime-key
v2.validation`, where the `v2.validation` path resolves to the
config file's `version: "v2"` + split block `validation`.

**No new regime configuration introduced.** PHASE2C_7.1 does not
add new fields to the `validation` block, does not introduce new
regime configuration, and does not modify the `validation` block's
date range or any other field. `config/environments.yaml` is
IMMUTABLE per project rules. The only PHASE2C_7.1-introduced
convention is the artifact-side regime-field naming (per §7), which
lives in producer code and the consumer guard, not in the config.

**Evaluation window.** The 2024 evaluation window is the calendar
year 2024-01-01 through 2024-12-31 (inclusive) at 1H granularity.
Same data infrastructure as PHASE2C_6's 2022 evaluation; the only
variable changing is the date range.

## 4. Evaluation gate

**The evaluation gate is the 4-criterion AND-gate from
PHASE2C_6's `regime_holdout` block, applied to 2024 evaluation
outputs:**

```
sharpe_ratio       >= -0.5
max_drawdown       <= 0.25
total_return       >= -0.15
total_trades       >= 5
```

**Inclusive inequalities** match PHASE2C_6's gate semantics. A
candidate passes if and only if all four conditions hold against
its 2024 holdout metrics.

**Note on gate vs filter distinction.** The 4-criterion gate is
the pass/fail criterion applied to each candidate's 2024
evaluation; it is the same gate PHASE2C_6 used. The trade-count
filter (per §5) is a separate post-evaluation analytical filter
applied to 2024 outputs to control for low-sample Sharpe inflation
in the secondary analytical artifact. The gate's `min_total_trades
= 5` is unchanged; the filter pass adds a higher trade-count
threshold (`>= 20`) for the secondary analytical view only. The
two should not be conflated:

- **Gate (`min_total_trades = 5`):** evaluates whether a
  candidate passes the 2024 holdout. Same as PHASE2C_6.
- **Filter (`>= 20`):** separate post-evaluation cut for the
  secondary analytical artifact. Filters which candidates count
  toward the filtered pass-rate computation in §4 Path B
  observables.

**No gate modification proposed.** PHASE2C_7.1 does not propose
modifying the 4-criterion gate. Path C (gate-calibration variation)
was deferred per PHASE2C_7.0 §5 lean; PHASE2C_7.1 implements Path
B's gate-unchanged comparison only.

## 5. Trade-count filter sub-pass specification

### 5.1 Threshold specification

The trade-count filter excludes candidates whose **2024 holdout
trade count** falls below the threshold. The threshold is pinned
at PHASE2C_7.1 spec time at:

```
total_trades >= 20  (in the 2024 holdout window)
```

**Filter operates on 2024 evaluation outputs, not on PHASE2C_6's
2022 trade counts.** This distinction matters and is load-bearing:

- *(i) — pre-evaluation filter on 2022 trade count (NOT what
  PHASE2C_7.1 does):* Drop candidates from the input universe
  before 2024 evaluation if their PHASE2C_6 2022 trade count was
  below threshold. This would produce a smaller input universe
  (198 minus low-2022-trade candidates) evaluated against 2024.
  This is **not** the model PHASE2C_7.1 uses.

- *(ii) — post-evaluation filter on 2024 trade count (what
  PHASE2C_7.1 does):* Evaluate all 198 candidates against 2024.
  Then in the secondary analytical artifact, exclude candidates
  whose 2024 trade count was below threshold. The primary
  analytical artifact reports the unfiltered 2024 result; the
  secondary analytical artifact reports the filter-passing subset
  result. Both artifacts derive from the same producer run.

The filter answers the question: "Does the anti-selection finding
hold when only candidates with sufficient 2024 trade volume are
counted?" That is a question about 2024 evidence reliability,
which requires filtering on 2024 trade counts, not on 2022 trade
counts. PHASE2C_6's near-miss cluster (4 candidates with positive
2022 holdout Sharpe but trades < 5 in 2022) is the motivating
context — it surfaced the empirical concern that low-trade-count
candidates can produce unreliable Sharpe values. The filter
operationalizes that concern against 2024 evaluation outputs.

**Definition of "trade count" for the filter:** the count of
completed round-trip trades against the 2024 holdout window. Two
artifact paths expose this value, and post-evaluation analysis
code may read either:

- Per-candidate holdout summary JSON: nested at
  `holdout_metrics.total_trades`
- Aggregate CSV: flattened column `holdout_total_trades`

Both paths reference the same underlying value. PHASE2C_6's
evaluation gate trade-count criterion
(`passing_criteria.min_total_trades = 5`) validates against
`holdout_metrics.total_trades` in the per-candidate JSON. Verified
empirically against `data/phase2c_evaluation_gate/audit_v1/`
artifacts.

**Execution model:**

- Single producer run against all 198 candidates with 2024 regime
  configuration. Produces the canonical 2024 evaluation artifact
  set under run_id `<run_id>` (exact run_id naming pinned in §6
  producer artifact specification).
- Post-evaluation analytical artifact generation: the secondary
  analytical artifact (filtered subset) is generated by reading
  the canonical evaluation artifacts and applying the trade-count
  filter as a row-level filter on
  `holdout_metrics.total_trades >= 20` (or equivalently
  `holdout_total_trades >= 20` in CSV). Secondary analytical
  artifact persists under a sibling analysis namespace such as
  `<run_id>_filtered`, explicitly marked as derived from the
  primary `<run_id>` evaluation artifacts.
- Both artifact sets reference the same lineage attestation
  (`single_run_holdout_v1` domain, regime fields per §7, same
  `engine_commit` and `engine_corrected_lineage` per D3) so
  `check_evaluation_semantics_or_raise` validates both
  equivalently. The secondary artifact's lineage is inherited by
  reference from the primary, not independently attested.

**No producer re-run.** The filter pass does not re-execute the
198-candidate evaluation. The secondary artifact set is derived
from the primary evaluation artifacts via post-processing; the
producer runs once.

### 5.2 Empirical justification for the threshold

The threshold `total_trades >= 20` is the working default. This
section provides the empirical context that makes ≥20 defensible
without claiming the threshold is empirically-optimal — the
discipline is the pre-specification (no ad hoc post-hoc
adjustment), not the specific number.

**Reference 1: trade-count distribution from PHASE2C_6 2022 audit
results.**

The 198-candidate trade-count distribution from PHASE2C_6's 2022
audit run (verified empirically against
`data/phase2c_evaluation_gate/audit_v1/holdout_results.csv`):

```
n     = 198
min   = 0
max   = 491
mean  = 59.1
median= 48
p10   = 0
p25   = 18
p50   = 48
p75   = 77
p90   = 126
```

Trade-count cumulative cuts:

```
< 5  trades:  44 candidates (22% of population)
< 10 trades:  44 candidates (22%)  — no candidates fired 5-9 trades
< 20 trades:  52 candidates (26%)
< 30 trades:  73 candidates (37%)
< 50 trades: 102 candidates (52%)
```

A `>= 20` threshold lands just above the 25th percentile (p25 =
18; ≥20 excludes 52 of 198 candidates = 26% of the 2022
population). The threshold excludes the bottom quartile-plus of
trade counts — the population segment where Sharpe estimates are
weakest — while preserving roughly 74% (146 of 198) of the
population for the filtered analytical artifact, if 2024
distribution is similar to 2022.

Note the distributional discontinuity in the 2022 trade-count
tail: 35 candidates fired zero trades, 9 candidates fired 1-4
trades, and zero candidates fired 5-9 trades. Candidates begin
appearing again at 11 trades. This means ≥10 and ≥5 are
operationally near-identical thresholds for this batch — both
exclude the same 44 candidates. ≥20 is the next meaningful
structural step up the distribution, not just an incremental
shift from ≥5 or ≥10. The threshold ladder isn't continuous in
this batch's data; ≥20 is the first threshold that excludes more
than the zero-and-near-zero tail.

This is a defensible position relative to alternative thresholds:

- *≥10 (n=44 excluded, 22% cut):* operationally equivalent to ≥5
  for this batch (zero candidates in the 5-9 range). Excludes
  only the zero-and-near-zero tail. Leaves the 11-19 trade range
  in, which sits near the noise floor where Sharpe estimates are
  unreliable.
- *≥30 (n=73 excluded, 37% cut):* aggressive cut that may exclude
  candidates with legitimately infrequent but reliable signals.
- *≥50 (n=102 excluded, 52% cut):* cuts more than half the
  population; risks excluding genuinely sparse-but-real alpha.

≥20 is the lowest threshold that materially excludes both the
near-miss cluster (PHASE2C_6's 4 candidates at trades < 5, plus
the broader 11-19 range where Sharpe estimates remain unstable),
without aggressively pruning the population.

The 2024 distribution may differ. The threshold is pinned now
based on 2022 distribution; if 2024 produces a substantially
different distribution shape, that observation goes into the
PHASE2C_7.1 closeout's discipline-discussion (per §5.3
pre-specification discipline), not into a mid-arc threshold
revision.

**Reference 2: Sharpe-stability rationale.**

Sharpe ratio computed from N round-trip trades has sampling
uncertainty that, as a rule-of-thumb, decreases on the order of
`1 / sqrt(N)` under reasonable distributional assumptions
(independent trades, finite variance). Moving from N = 5 to N =
20 trades roughly halves the noise scale. This is not a formal
Sharpe standard-error estimate; it is a stability rationale for
excluding the lowest-trade-count tail. The threshold doesn't need
to land at any specific Sharpe-stability inflection point to be
defensible; it needs to be high enough that Sharpe estimates
aren't dominated by sample-size noise. ≥20 satisfies that under
the rule-of-thumb framing.

**Reference 3: project-discipline grounding.**

≥20 is a project-discipline default for this filter pass, not an
empirically-optimal threshold. The discipline that matters is the
pre-specification:

- The threshold is pinned at PHASE2C_7.1 spec time (this
  document).
- The threshold is not adjusted after seeing 2024 evaluation
  results.
- If 2024 results suggest the threshold is wrong, the response is
  a follow-up arc with its own scoping doc, not threshold
  revision in PHASE2C_7.1's closeout.

This discipline (pre-specification + no post-hoc adjustment) is
what protects the filter pass from being a fishing expedition
(picking a threshold that produces convenient results). The
specific number ≥20 is grounded in §5.2 references 1 and 2 above;
the discipline that the number is fixed is grounded in §5.3.

**On reference selection.**

The three references are descriptive context for ≥20, not
derivations from first principles. Per the D1 confirmation
synthesis, ≥20 is a working default; §5.2 makes it defensible
rather than arbitrary, which is sufficient. PHASE2C_7.1 closeout
will report the empirical distribution of 2024 trade counts and
note any sensitivity findings — that's where post-hoc empirical
evidence about the threshold lives, not in §5.2.

### 5.3 Pre-specification discipline

The trade-count filter pass is bound by three rules pinned at
PHASE2C_7.1 spec time:

**Rule 1 — Threshold pinned at PHASE2C_7.1 spec time.**

The threshold value (`total_trades >= 20` in 2024 holdout) is
fixed by this document. PHASE2C_7.1 implementation reads the
threshold from this spec; the implementation does not expose the
threshold as a runtime parameter. Pinning the threshold in the
spec rather than in code makes the threshold choice auditable
from the document layer rather than the producer artifact layer.

**Rule 2 — No threshold adjustment after seeing 2024 evaluation
results.**

Once the producer run completes and the canonical 2024 evaluation
artifacts are written, the threshold is not adjusted. This applies
specifically to:

- *Lowering the threshold to include marginal candidates* if the
  primary 2024 result shows interesting near-miss patterns at
  trades < 20.
- *Raising the threshold to exclude noisy candidates* if the
  filtered subset still shows results that look unstable.
- *Adding a sub-threshold (e.g., trades >= 15)* as an
  intermediate analytical artifact.

Each of these is post-hoc fishing. The filtered analytical
artifact is generated against `total_trades >= 20` exactly as
specified, regardless of what the primary 2024 evaluation shows.

**Rule 3 — Sensitivity findings drive a follow-up arc, not a
mid-arc revision.**

If the PHASE2C_7.1 closeout drafting reveals that the threshold
choice materially affects the conclusions (e.g., the
anti-selection finding holds at ≥20 but reverses at ≥30), that
observation is reported in the closeout as a sensitivity-discussion
item and motivates a separate scoping document for a follow-up
arc. The follow-up arc may revisit the threshold under a
pre-registered question, run additional filtered analytical
artifacts at multiple thresholds, or revise the filter design
entirely. PHASE2C_7.1's threshold remains ≥20 in its own closeout.

**Why this discipline matters.**

The filter pass exists to control for low-sample Sharpe inflation
in the 2024 evaluation. Without pre-specification discipline, the
filter pass becomes a fishing expedition: pick the threshold that
produces convenient results, report convenient results. Pinning
the threshold in §5.1 (with empirical justification in §5.2) and
binding the implementation to that threshold (Rules 1-3) makes the
filter pass *falsifiable* — the result is what it is, regardless
of whether it confirms or contradicts the primary 2024 evaluation
finding.

This is the same pre-registration discipline PHASE2C_6 closeout
§9 carried forward into PHASE2C_7+ for audit-only survivors:
investigation under a pre-registered question, not post-hoc
promotion. Same principle, applied here to threshold choice.

## 6. Producer artifact specification

**Producer extension (not a new script).** PHASE2C_7.1 extends
the existing `scripts/run_phase2c_evaluation_gate.py` to accept a
regime-key parameter, rather than creating a new script. This
preserves single-producer-surface discipline (PHASE2C_6's
discipline pattern; D6 Stage 2c/2d analog with `--stage` flag
sharing).

**CLI flag.** The new flag is:

```
--regime-key v2.validation
```

The flag value resolves to the `validation` block under
`config/environments.yaml`'s `version: "v2"` config. The producer
loads the start/end dates from this block and uses them as the
evaluation window's date range.

**Backward compatibility.** The existing PHASE2C_6 evaluation
mode (against the `regime_holdout` 2022 block) remains accessible
via `--regime-key v2.regime_holdout` after the extension. The
prior PHASE2C_6 invocation pattern (no regime-key flag, defaulting
to 2022) may be deprecated or kept as a backward-compatible
default; this is an implementation choice pinned during Step 1
that does not affect PHASE2C_7.1's correctness.

**Run_id naming.** The canonical run_id for PHASE2C_7.1's primary
2024 evaluation is:

```
audit_2024_v1
```

The filtered secondary analytical artifact (per §5.1, derived from
the primary canonical artifacts) is persisted under a sibling
**analysis namespace**, not a producer run_id:

```
audit_2024_v1_filtered
```

Both artifact sets live under
`data/phase2c_evaluation_gate/<run_id>/`. The naming convention
(`audit_<short_regime>_v<version>` for run_ids, where
`<short_regime>` is a readable short form of the regime — e.g.,
`2024` corresponds to `regime_label=validation_2024`; `<version>`
increments for re-runs) is documented here as the PHASE2C_7+
project convention; future arcs against additional regimes follow
the same pattern.

**Existing PHASE2C_6 run_ids unchanged.** The PHASE2C_6 run_ids
(`smoke_v1`, `primary_v1`, `audit_v1`) are not retroactively
renamed. PHASE2C_7.1 introduces the new naming for new artifacts;
PHASE2C_6 artifacts remain at their original paths.

## 7. Lineage attestation

**Attestation domain.** PHASE2C_7.1's 2024 evaluation artifacts
attest under the same `single_run_holdout_v1` domain as PHASE2C_6,
per D3. No new attestation domain introduced.

**Regime-field schema (new in PHASE2C_7.1).** Each per-candidate
JSON and aggregate JSON carries three new lineage fields:

```
artifact_schema_version: string, fixed value "phase2c_7_1"
                         for artifacts produced by PHASE2C_7.1
                         and any direct-pattern successor arcs
regime_key:              string, sourced from --regime-key CLI
                         flag value (e.g., "v2.validation")
regime_label:            string, derived from the documented
                         mapping below (e.g., "validation_2024")
```

The `artifact_schema_version` field is the explicit discriminator
that the consumer guard uses to route validation logic. Its
presence on an artifact is necessary and sufficient evidence that
the artifact carries the new regime-field schema. PHASE2C_6
artifacts (which predate this schema) do not carry the field; the
consumer guard treats absence-of-field as the legacy validation
path.

**Regime label mapping.** PHASE2C_7.1 documents the mapping from
`regime_key` to `regime_label` as a project-discipline convention.
The mapping for the regimes currently in use:

| `regime_key` | `regime_label` | `config/environments.yaml` block |
|---|---|---|
| `v2.regime_holdout` | `bear_2022` | `regime_holdout` block (`label: "bear_2022"`) |
| `v2.validation` | `validation_2024` | `validation` block (no `label` field) |

The `bear_2022` label is config-canonical (the `regime_holdout`
block's `label` field). The `validation_2024` label is a
PHASE2C_7.1 project convention since the `validation` block has no
`label` field; the convention documented here is the single
source of truth and future arcs adding new regimes append entries
to this table.

**Backfill for PHASE2C_6 artifacts (not done; not required).**
PHASE2C_6's per-candidate and aggregate artifacts on disk are not
modified. They do not carry `artifact_schema_version`,
`regime_key`, or `regime_label`. Cross-version analysis code (per
§8 Step 4) branches on the presence of `artifact_schema_version`:
if absent, the artifact is PHASE2C_6 and the analysis code uses
the artifact's run_id and provenance to determine regime context
(e.g., artifacts under `data/phase2c_evaluation_gate/audit_v1/`
are PHASE2C_6 against the 2022 regime); if present, the artifact
is PHASE2C_7.1+ and the analysis code reads `regime_key` /
`regime_label` directly. No retroactive field synthesis or
backfill on PHASE2C_6 artifacts.

**Consumer guard extension.**
`backtest.wf_lineage.check_evaluation_semantics_or_raise()` is
extended with a discriminator check:

- If `artifact_schema_version` is absent: legacy validation path
  (PHASE2C_6 schema). Validates `evaluation_semantics`,
  `engine_commit`, `engine_corrected_lineage`, `lineage_check`,
  `current_git_sha` only. Same behavior as the pre-PHASE2C_7.1
  implementation.
- If `artifact_schema_version == "phase2c_7_1"`: new validation
  path. Requires the same fields as legacy plus `regime_key` and
  `regime_label`, with `regime_label` validated against the
  documented mapping for the given `regime_key`.
- If `artifact_schema_version` is present but unrecognized: raises
  `ValueError`. Future arcs that introduce new schemas (e.g.,
  `"phase2c_8"`) extend the discriminator branching at that time.

Implementation note: the consumer guard's discriminator branching
is unit-tested explicitly per §8 Step 1 test categories. Both
validation paths (legacy and new) are exercised against canonical
artifacts (PHASE2C_6 audit_v1 sample for legacy; PHASE2C_7.1 smoke
run sample for new).

## 8. Implementation plan

PHASE2C_7.1 implementation proceeds in five sequential steps. Each
step has explicit success criteria and produces a verifiable
artifact before the next step begins. The plan inherits the
scaling-step discipline from METHODOLOGY_NOTES.md §4 (smoke
verification before full-scale execution; intermediate evidence
not over-extended to claims requiring later-step data).

**Step 1 — Producer extension and tests.**

Extend `scripts/run_phase2c_evaluation_gate.py` to accept a
`--regime-key v2.validation` flag (or equivalent regime-key
parameterization per §6) that loads the 2024 validation regime
configuration from `config/environments.yaml` v2 split. Required
tests: (a) regime-parameterization unit test confirming that
`--regime-key v2.validation` loads the correct date range and
regime parameters; (b) lineage-stamping unit test confirming that
the regime context is correctly recorded on the per-candidate
artifact and on the aggregate JSON (exact field name and naming
convention pinned in §6/§7; PHASE2C_6 artifacts did not carry an
explicit regime field, so the schema decision is part of
PHASE2C_7.1 implementation); (c) end-to-end smoke test against ≤5
candidates against 2024 analogous to PHASE2C_6.3 smoke (4
candidates) — verifies the extension produces well-formed
artifacts under the expected attestation domain. Success
criterion: all three test categories pass; the smoke run produces
5 per-candidate JSONs + aggregate artifact under
`single_run_holdout_v1` domain with regime context recorded per
the §6/§7 schema; `check_evaluation_semantics_or_raise` validates
all artifacts.

**Step 2 — Full 198-candidate primary run against 2024.**

Run the extended producer against all 198 PHASE2C_6 candidates
using `--regime-key v2.validation` with `--universe audit`. Canonical
artifact path under `data/phase2c_evaluation_gate/<run_id>/` (run_id
pinned in §6). Lineage attestation: single_run_holdout_v1 domain,
regime fields per §7, same `engine_commit` and
`engine_corrected_lineage` per D3. Success criterion: 198
per-candidate JSONs + aggregate JSON + aggregate CSV produced;
`check_evaluation_semantics_or_raise` validates all artifacts; no
unexplained producer/runtime failures; any per-candidate error
rows must be recorded, bounded, and included in aggregate counts.
Step 2 must complete with clean artifacts before Step 3 begins.

**Step 3 — Generate pre-specified trade-count-filtered secondary
analysis from the same 2024 evaluation results (`total_trades >=
20`); do not re-run evaluation.**

Per §5.1's execution model: post-evaluation filter on 2024 trade
count, model (ii). Read the canonical 2024 evaluation artifacts
from Step 2; apply the row-level filter
`holdout_metrics.total_trades >= 20` (or equivalently
`holdout_total_trades >= 20` in CSV). Persist the filtered
analytical artifact under a sibling analysis namespace
`<run_id>_filtered`, explicitly marked as derived from the primary
`<run_id>` evaluation artifacts. Per §5.3 Rules 1-3: threshold is
fixed at 20 regardless of what the primary 2024 evaluation shows;
no post-hoc threshold adjustment. Success criterion: filtered
artifact set produced; lineage inherited by reference from the
primary artifacts; row count of filtered set matches the predicate
applied.

**Step 4 — Candidate-aligned 2022 vs 2024 comparative analysis
artifact generation.**

Produce the comparative analysis outputs per §4 Path B expected
observables (cross-reference to PHASE2C_7.0 §4): primary-vs-
audit-only pass-rate comparison for 2024 (analogous to
PHASE2C_6's headline finding); candidate-aligned 2022-vs-2024
distribution shift; rank stability of WF Sharpe vs 2024 holdout
Sharpe across the 198; WF × holdout matrix recomputation against
2024. The same observables computed against the filtered subset
from Step 3. Output artifact: a comparative analysis summary
under `data/phase2c_evaluation_gate/<run_id>/comparative_analysis.json`
(or equivalent — exact path pinned during Step 4 implementation).
Success criterion split into two verification levels: (a)
internal consistency — all observables computable from the
canonical artifacts; summary statistics (e.g.,
primary-vs-audit-only pass-rate) recompute cleanly from
per-candidate JSONs without numerical drift; (b) external
row-level verification — independent script or external
adversarial review (Codex pattern per PHASE2C_6.7's row-diff
catch) clears before Step 5 closeout drafting begins. Both levels
required; internal consistency alone is necessary but not
sufficient (PHASE2C_6.6 internal review missed the
precision-overshoot that PHASE2C_6.7 Codex review caught).

**Step 5 — Closeout drafting per PHASE2C_6 11-section pattern.**

Draft `docs/closeout/PHASE2C_7_PATH_B_RESULTS.md` (or equivalent
suffix per §6 universal closeout-discipline constraint) following
PHASE2C_6 closeout's 11-section structure (scope/verdict, lineage
integrity, primary result, audit/full-population result,
selection-power adjudication or equivalent for Path B's
comparative finding, non-claims, survivor enumeration if
applicable, by-theme interpretation if applicable, implications
for next scoping arc, methodology-discipline observation,
references and reproducibility). Apply the same Path 2 outline-first
dual-AI review methodology PHASE2C_6.6 closeout used. Apply the
V1-V5 pre-commit verification protocol (cross-references resolve,
file paths exist, numbers consistent across sections, question
definitions consistent, bounded-framing audit) before sealing.
Success criterion: closeout sealed and committed; all V1-V5 checks
pass; reviewer adjudication trail (ChatGPT + Claude) holds for
each section; if Codex adversarial review fires per PHASE2C_7.0
§8's cross-cutting note (scope-overshoot risk warranting external
row-level verification per PHASE2C_6 §10's discipline observation),
findings folded before push. The closeout's implications section
addresses next scoping arc rather than pre-naming a specific phase
number.

## 9. Pass/fail criteria for closeout

PHASE2C_7.1's closeout (per §8 Step 5) seals when the criteria
below are met. Each criterion cross-references the section where
its underlying observable is specified, so a closeout reviewer
can audit each criterion against canonical artifacts directly.

**Required artifact production (per §8 Steps 2-4).**

- 198 per-candidate JSONs + 1 aggregate JSON + 1 aggregate CSV
  produced under `data/phase2c_evaluation_gate/audit_2024_v1/`.
- Filtered analytical artifact set produced under
  `data/phase2c_evaluation_gate/audit_2024_v1_filtered/` (sibling
  analysis namespace per §6, derived from primary canonical
  artifacts per §5.1).
- Comparative analysis artifact at
  `data/phase2c_evaluation_gate/audit_2024_v1/comparative_analysis.json`
  (or equivalent path pinned during Step 4) with §4 Path B
  expected observables computable from canonical sources (per §8
  Step 4 success criterion (a)).

**Required lineage attestation (per §7).**

- All 198 per-candidate JSONs and the aggregate JSON carry
  `artifact_schema_version="phase2c_7_1"`,
  `regime_key="v2.validation"`,
  `regime_label="validation_2024"`, plus the legacy lineage
  fields (`evaluation_semantics`, `engine_commit`,
  `engine_corrected_lineage`, `lineage_check`, `current_git_sha`).
- `check_evaluation_semantics_or_raise` validates every artifact
  via the new validation path without raising.
- Filtered artifact set inherits lineage by reference per §5.1;
  no independent attestation required.

**Required §4 Path B observables (cross-reference to PHASE2C_7.0 §4).**

The closeout's §3-§5 (analogous to PHASE2C_6 closeout's §3-§5)
must report:

- Aggregate 2024 pass-rate (k of 198) with primary-vs-audit-only
  breakdown.
- Candidate-aligned 2022-vs-2024 pass-rate comparison (PHASE2C_6
  audit_v1 numbers vs PHASE2C_7.1 audit_2024_v1 numbers, same 198
  candidates).
- Rank stability of WF Sharpe vs 2024 holdout Sharpe across the
  198 (analogous to PHASE2C_6 closeout §5's "10 of 13 survivors
  have wf_test_period_sharpe ≤ 0" finding for 2022).
- Filtered-subset pass-rates (against the `total_trades >= 20`
  cohort per §5.1).

**Required closeout document structure (per §8 Step 5).**

- 11-section structure inherited from PHASE2C_6 closeout, with
  PHASE2C_7.1-specific path-B framing in section titles.
- Bounded-framing language per §10 risks/out-of-scope; no claims
  beyond what the data supports.
- V1-V6 pre-commit verification clears (per §8 Step 5 success
  criterion).

**Required pre-commit verification (per §8 Step 5 + V6 extension).**

V1 cross-references resolve. V2 file paths exist. V3 numbers
consistent (198/44/154/13/1/12 from PHASE2C_6; new 2024 numbers
from this arc). V4 definition consistency. V5 bounded-framing
audit. V6 schema-name consistency for `artifact_schema_version`,
`regime_key`, `regime_label` across §6/§7/§8 of this spec and
across the closeout document's references.

**Required reviewer adjudication trail (per §8 Step 5).**

Section-by-section dual-AI review (ChatGPT + Claude) for each
load-bearing section of the closeout. Reviewer-divergence
adjudication explicit per the project pattern. Codex adversarial
review fires per PHASE2C_7.0 §8's cross-cutting note if
scope-overshoot risk warrants external row-level verification per
PHASE2C_6 §10's discipline observation.

**Failure conditions.**

If any of the following occur during PHASE2C_7.1 execution, the
closeout does not seal and the failure is reported as a
PHASE2C_7.1 implementation issue requiring follow-up before path
selection for the next arc:

- Producer run produces unexplained errors beyond the bounded
  failure-mode surface specified in §8 Step 2.
- `check_evaluation_semantics_or_raise` raises on any artifact in
  the canonical run.
- Comparative analysis (§8 Step 4) cannot reproduce numerical
  values from per-candidate JSONs (internal consistency fails).
- External adversarial verification (Step 4 success criterion (b))
  surfaces a precision-overshoot or row-level discrepancy that
  cannot be folded as a §10 risk.
- V1-V6 pre-commit verification fails on any check.

## 10. Risks and out-of-scope

**Out-of-scope items inherited from PHASE2C_7.0 §6.**

The five universal out-of-scope items from PHASE2C_7.0 §6 carry
forward to PHASE2C_7.1 unchanged. Cross-referenced rather than
restated:

- 2025 test split is preserved touched-once across PHASE2C_7;
  PHASE2C_7.1 does not evaluate against 2025 (per PHASE2C_7.0 §6).
- Theme-targeted candidate generation is deferred (per
  PHASE2C_7.0 §6).
- DSR execution beyond design discussion is out-of-scope (per
  PHASE2C_7.0 §6); Path D was not selected.
- Methodology amendments not empirically motivated by PHASE2C_7.1
  findings are out-of-scope (per PHASE2C_7.0 §6).
- Audit-only post-hoc promotion is out-of-scope (per PHASE2C_7.0
  §6); the 12 audit-only survivors from PHASE2C_6 are evaluated
  against 2024 as part of the full 198-candidate population, but
  individual audit-only-survivor advancement is not in scope.

**PHASE2C_7.1-specific out-of-scope items.**

- **Path A standalone execution.** Path A's evidence is contained
  within Path B's output (PHASE2C_7.0 §5 Rung 3); PHASE2C_7.1
  does not run Path A separately. The 13-survivor sub-analysis is
  available as a slice of Path B's results during Step 4
  comparative analysis if needed.
- **Path C calibration variation.** Deferred per PHASE2C_7.0 §5
  Rung 4. PHASE2C_7.1 does not vary the 4-criterion gate
  calibration; gate stays as PHASE2C_6's exact specification.
- **Multi-regime evaluation beyond 2024.** PHASE2C_7.1 evaluates
  against the 2024 validation regime only. A third or fourth
  regime would be out-of-scope for this arc; future arcs may
  add additional regimes under separate scoping decisions.
- **Schema migration of PHASE2C_6 artifacts.** Per §7,
  PHASE2C_6's existing artifacts are not modified to add the new
  schema fields. Cross-version analysis code branches on
  `artifact_schema_version` presence (per §7 backfill paragraph);
  no retroactive PHASE2C_6 artifact rewrite.
- **Producer-script refactoring beyond regime parameterization.**
  §6 specifies a regime-key extension; broader refactoring of
  `scripts/run_phase2c_evaluation_gate.py` (e.g., consolidating
  CLI surface, removing legacy paths, restructuring config
  loading) is out-of-scope. Step 1 implementation should be
  narrow.

**Risks (named for PHASE2C_7.1 closeout's risk register if
realized).**

- **2024 data infrastructure issue.** If the 2024 calendar year
  has data gaps or quality issues not yet surfaced (the canonical
  data has 31 known historical gaps concentrated in 2020-2023, but
  2024 has not been stress-tested in PHASE2C_6), Step 2 may
  surface unexpected per-candidate failures. Mitigation: §8 Step 1
  smoke run against ≤5 candidates surfaces such issues before
  full-scale Step 2 execution.
- **Backward-compatibility regression.** §6 specifies that the
  existing PHASE2C_6 invocation pattern remains accessible after
  the producer extension. Step 1 unit tests must cover both the
  new regime-key path and the legacy backward-compat path.
  Regression in the legacy path would invalidate PHASE2C_6
  reproducibility. Mitigation: Step 1 test category (a) covers
  legacy path explicitly.
- **Schema discriminator edge cases.** §7's three-branch
  discriminator (absent / `phase2c_7_1` / unrecognized) covers
  current schemas. If a future arc introduces additional schemas
  before the consumer guard's discriminator branching is updated,
  artifacts under the new schema raise `ValueError` until the
  guard catches up. Mitigation: schema introduction in future
  arcs requires consumer guard extension as part of that arc's
  scope.
- **Filter pass surfacing inconvenient sensitivity.** §5.3 binds
  PHASE2C_7.1 to no post-hoc threshold adjustment. If the 2024
  primary result is clean and the filtered subset shows
  qualitatively different results (e.g., anti-selection reverses
  in one but not the other), the discipline holds: report both,
  do not adjust the threshold mid-arc, defer to follow-up arc per
  §5.3 Rule 3. The risk is procedural (resisting the temptation to
  adjust), not technical.
- **Comparative analysis numerical precision.** §8 Step 4
  internal-consistency check may surface floating-point precision
  differences between row-level computation and aggregate
  computation. Mitigation: standard floating-point tolerance
  conventions (relative tolerance 1e-9 for sum-of-products vs
  direct-sum comparisons); precision-overshoot beyond tolerance
  surfaces in Step 4 success criterion (b) external adversarial
  check.

**Known unknowns explicitly named.**

- Whether PHASE2C_6's anti-selection finding generalizes to 2024
  is the empirical question PHASE2C_7.1 answers. The closeout's
  §5 (or analogous selection-power adjudication section) reports
  the answer; it is not pre-judged in this spec.
- Whether the trade-count filter pass changes the headline
  finding's direction is empirically open. §5.3 Rules 1-3 hold
  regardless of which direction the filter pass surfaces.
- Whether PHASE2C_7.1 closeout's findings motivate a future
  scoping document is decided after PHASE2C_7.1 seals;
  PHASE2C_7.1 does not pre-name the next arc's scope.
