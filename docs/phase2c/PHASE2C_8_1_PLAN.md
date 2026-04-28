# PHASE2C_8.1 — Multi-regime evaluation gate (extended)

**Implementation specification for PHASE2C_8 Q-B1 — additional-regime
evaluation at n≥3 against the 198-candidate batch from PHASE2C_6;
extends PHASE2C_7.1's two-regime evaluation gate to n=4 baseline
composition (eval_2020_v1 + eval_2021_v1 novel; bear_2022 +
validation_2024 inherited per Option A engine-version invariance).**

- **Spec drafting date**: 2026-04-27
- **Predecessor scoping decision**: [`PHASE2C_8_SCOPING_DECISION.md`](PHASE2C_8_SCOPING_DECISION.md)
  (committed at `f223316`)
- **Carry-forward source**: [`PHASE2C_7_1_PLAN.md`](PHASE2C_7_1_PLAN.md)
  + [`docs/closeout/PHASE2C_7_1_RESULTS.md`](../closeout/PHASE2C_7_1_RESULTS.md)
- **Methodology discipline**:
  [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  (commit `76e46d4`; §1–§12 in force)

---


## 1. Scope and verdict

**This document specifies the implementation arc for PHASE2C_8 Q-B1
— additional-regime evaluation at n≥3 against the same 198-candidate
batch from PHASE2C_6. PHASE2C_8.0 (the scoping decision) recommended
Q-B1; PHASE2C_8.1 implements it.**

**Project state at PHASE2C_8.1 spec drafting (2026-04-27).**

- Canonical main: `origin/main` at commit `f223316`
- Tags on main: `wf-corrected-v1` (corrected WF engine fix at
  commit `eb1c87f`), `phase2c-6-evaluation-gate-v1` (PHASE2C_6
  arc completion), `phase2c-7-1-multi-regime-v1` (PHASE2C_7.1
  multi-regime evaluation gate completion at `784936a`)
- PHASE2C_8.0 scoping decision:
  [`docs/phase2c/PHASE2C_8_SCOPING_DECISION.md`](PHASE2C_8_SCOPING_DECISION.md)
  (committed at `f223316` on `origin/main`)
- PHASE2C_7.1 closeout (precedent + carry-forward source):
  [`docs/closeout/PHASE2C_7_1_RESULTS.md`](../closeout/PHASE2C_7_1_RESULTS.md)
- PHASE2C_7.1 plan (template precedent):
  [`docs/phase2c/PHASE2C_7_1_PLAN.md`](PHASE2C_7_1_PLAN.md)
- METHODOLOGY_NOTES post-update (commit `76e46d4`):
  [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  §1-§12 in force
- Q-B1 recommendation source: PHASE2C_8.0 §5 ("Recommended
  scoping decision: Q-B1 — additional-regime evaluation before
  calibration variation, cohort deep-dive, or DSR infrastructure")

**What PHASE2C_8.1 produces.**

Multi-regime evaluation across n≥3 historical regimes (including
PHASE2C_7.1's two: bear_2022 and validation_2024) against all 198
PHASE2C_6 candidates, with regime-source selection sub-cycle in §3,
candidate-aligned multi-regime comparison matrix at n-regime
structure, and closeout document. Detailed implementation plan in
§8 (5-step structure with sequential gating); regime-source
selection sub-cycle in §3 (the first substantive decision point of
PHASE2C_8.1 spec drafting). Pre-pinned decisions (carried forward
from PHASE2C_7.1 + PHASE2C_8.0 + adjudicated during this spec's
pre-drafting reviewer cycle):

| decision | resolution |
|---|---|
| **D1 trade-count filter** | Pinned at `total_trades >= 20` per PHASE2C_7.1 §5.3 Rule 1 (carryforward; not a runtime parameter) |
| **D2 4-criterion AND-gate** | sharpe ≥ −0.5; max_drawdown ≤ 0.25; total_return ≥ −0.15; total_trades ≥ 5 (PHASE2C_7.1 §4 unchanged; per `config/environments.yaml splits.regime_holdout.passing_criteria`) |
| **D3 schema discriminator** | Extension `phase2c_7_1` → `phase2c_8_1`; same schema fields (`artifact_schema_version`, `regime_key`, `regime_label`, `run_id`, `engine_corrected_lineage`, `evaluation_semantics`) per PHASE2C_7.1 §7 |
| **D4 regime-source criteria** | 5 soft criteria + 1 veto criterion (2025 test split touched-once); criteria-before-selection discipline per §3.1; selection sub-cycle adjudicated within §3 |
| **D5 sequential gating** | Step 1.1 → 1.2 → 1.3 → 1.4 → 2 → 3 → 4 → 5 per §8 |
| **D6 §3 sub-cycle within spec** | Regime-source selection happens within PHASE2C_8.1 spec drafting §3 (not as a separate scoping document); preserves PHASE2C_8.0 §3 anti-pre-naming anchor + avoids document proliferation |

**What PHASE2C_8.1 is NOT.**

- **Not a re-litigation of PHASE2C_8.0.** Path selection is sealed
  at Q-B1. PHASE2C_8.1 implements Q-B1; it does not revisit Q-B2
  / Q-B3 / Q-B4. Any of those alternative paths could surface in
  subsequent scoping cycles per PHASE2C_8.0 §5 conditional-shift
  triggers; but they are not within PHASE2C_8.1 scope.
- **Not a methodology amendment.**
  [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  §1-§12 (post-update commit `76e46d4`) apply throughout
  PHASE2C_8.1; new methodology principles surfaced during PHASE2C_8.1
  work are captured as a follow-up update (same hybrid handling as
  PHASE2C_6.6 → `536f737` and PHASE2C_7.1 → `76e46d4`).
- **Not a forward decision on the next-arc scope.** PHASE2C_8.1's
  closeout will report findings + enumerate open questions; it
  does not pre-commit any subsequent arc's path. Successor-arc
  identifiers are not pre-named per §10 anti-pre-naming carryforward.
- **Not a 2025 test split touch.** 2025 remains preserved
  touched-once across PHASE2C_8.1 work (CLAUDE.md hard rule;
  veto criterion in §3.1; out-of-scope universal in §10).
- **Not a `config/environments.yaml` modification.** The
  IMMUTABLE-config CLAUDE.md hard rule preserved across PHASE2C_8.1.
  If selected additional regimes lack canonical config-block
  coverage, the §3 sub-cycle adjudication surfaces this as a
  selection-failure mode (post-hoc config addition would be
  separately scoped, not within PHASE2C_8.1).
- **Not a regime-source selection that pre-bakes mechanism
  conclusions.** The §3 criteria-before-selection discipline
  prevents regime-selection from becoming post-hoc narrative
  fitting (per §10 risks). Criteria define what makes a defensible
  candidate regime; selection adjudicates candidates against
  criteria; mechanism conclusions emerge from PHASE2C_8.1's
  empirical results, not from the regime-selection process.

**Document structure.**

§2 names the input universe (198 candidates from PHASE2C_6 batch
`b6fcbf86-...`, identical to PHASE2C_7.1 §2). §3 specifies the
additional regime selection sub-decision + per-regime configurations
(four sub-sections: §3.1 criteria; §3.2 decision framework; §3.3
recommended additional regimes post-adjudication; §3.4 per-regime
config). §4 specifies the evaluation gate (4-criterion AND-gate;
unchanged from PHASE2C_7.1). §5 specifies the trade-count filter
sub-pass (pinned at >=20 per PHASE2C_7.1 §5.3 Rule 1). §6 specifies
the producer artifact (multi-regime orchestration extension to
existing `scripts/run_phase2c_evaluation_gate.py` with `--regime-key`
flag chain; per-regime artifact directory pattern). §7 specifies
the lineage attestation (schema discriminator extension
`phase2c_7_1` → `phase2c_8_1`). §8 provides the 5-step
implementation plan with sequential gating. §9 names pass/fail
criteria for closeout. §10 names risks (5: regime-source selection
deadlock, multi-regime infrastructure complexity, cross-regime
intersection sparsity, closeout-drafting load expansion, post-hoc
narrative fitting) and out-of-scope items (universal across the arc).

---


---


## 2. Input universe

**The input universe is the 198 candidates from PHASE2C_6's batch
`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`. PHASE2C_8.1 evaluates the
same 198-candidate population against additional historical regimes
(n≥3 total regimes including PHASE2C_7.1's two: bear_2022 and
validation_2024).**

The candidates are evaluated under the corrected-engine artifacts
(post-`eb1c87f` engine fix; lineage tag `wf-corrected-v1`). Each
candidate has a stable `hypothesis_hash` that serves as the
canonical identifier across PHASE2C_6, PHASE2C_7.1, and PHASE2C_8.1
artifacts.

**Candidate population vs evaluation runs distinction.**

PHASE2C_8.1's input universe specification distinguishes two
operational concepts:

- **Candidate population** (unchanged from PHASE2C_7.1): the 198
  hypothesis-hash-identified candidates from PHASE2C_6's batch.
  Population does NOT expand in PHASE2C_8.1; the same 198
  candidates are evaluated against additional regimes.
- **Evaluation runs** (extended from PHASE2C_7.1): per-regime
  evaluation runs against the 198-candidate population. PHASE2C_7.1
  produced 2 evaluation runs (`audit_v1` against bear_2022;
  `audit_2024_v1` against validation_2024). PHASE2C_8.1 produces
  n≥3 evaluation runs across the additional regimes selected via
  §3 sub-cycle, including the two existing PHASE2C_7.1 runs as
  the baseline regime evidence.

The distinction matters operationally for §6 (producer artifact
specification) and §8 Step 2 (full evaluation across additional
regimes). §6 specifies how the producer extends to n≥3 evaluation
runs; §8 Step 2 specifies the per-regime artifact production
sequence. The candidate population stays constant; the evaluation
runs scale.

**Canonical hash list source.**

The 198 hypothesis hashes are sourced from PHASE2C_6's audit_v1
canonical aggregate CSV at:

```
data/phase2c_evaluation_gate/audit_v1/holdout_results.csv
```

The `hypothesis_hash` column of this CSV enumerates the 198
candidates. PHASE2C_8.1's producer reads from this canonical source
rather than re-extracting from upstream batch metadata. This
preserves the candidate-aligned discipline carryforward from
PHASE2C_7.1: the 198 candidates evaluated against PHASE2C_8.1's
additional regimes are identically the 198 candidates evaluated
against bear_2022 in PHASE2C_6 + validation_2024 in PHASE2C_7.1.

**Universe partition retained.**

The PHASE2C_6 partition into primary (`wf_test_period_sharpe >
0.5`, n=44) and audit-only (`wf_test_period_sharpe <= 0.5`, n=154)
is preserved in PHASE2C_8.1's artifacts. Each candidate's WF
sharpe and primary-vs-audit-only flag carry forward from PHASE2C_6
into PHASE2C_8.1's per-regime evaluation outputs, enabling
primary-vs-audit-only pass-rate comparison per additional regime
without external lookup. The candidate-aligned cross-regime
comparison machinery in §6 + §8 Step 4 builds on this preserved
partition.

**Lineage anchor.**

PHASE2C_8.1 inherits the corrected-engine lineage chain from
PHASE2C_7.1:

- **batch_id**: wf_corrected_v1 (PHASE2C_6 batch
  `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` re-evaluated under
  corrected engine; carryforward across all subsequent arcs)
- **WF lineage tag**: `wf-corrected-v1` (corrected engine commit
  `eb1c87f`; sealed at PHASE2C_7.1)
- **Engine corrected lineage attestation**:
  [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py)
  `check_evaluation_semantics_or_raise()` guard applies to all
  PHASE2C_8.1 single-run holdout artifacts. Section RS of
  [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md)
  applies to all PHASE2C_8.1 artifacts consuming corrected-engine
  outputs.
- **Source data sources** (PHASE2C_6 carryforward; reference for
  audit completeness): CCXT BTC/USDT 1h OHLCV at
  `data/raw/btcusdt_1h.parquet`; Binance Vision archived feed at
  `data/raw/btcusdt_1h_archive.parquet` (carryforward across arcs;
  same data sources used for PHASE2C_6 + PHASE2C_7.1 + PHASE2C_8.1).

PHASE2C_8.1 does NOT re-evaluate the corrected-engine lineage; it
inherits the lineage as project-standing context per §7 PHASE2C_8.0
scoping decision discipline carry-forward item 8 (engine corrected
lineage continuity).

---


---


## 3. Regime-source selection criteria and framework

PHASE2C_8.1 selects additional historical regimes for evaluation
against the 198-candidate population per the Q-B1 mechanism question
(regime-mismatch vs pattern-overfit vs calibration-coupling). The
selection is structured as a two-stage adjudication: §3.1 specifies
the criteria; §3.2 specifies the framework that applies the criteria
to candidate regime sources.

The §3 sub-cycle is structured as Stage A + Stage B. Stage A locks
the criteria and framework forward-pointing — without naming specific
candidate regimes. Stage B (§3.3) applies the locked criteria and
framework to enumerate the n-2 = 2 additional regimes selected for
PHASE2C_8.1 evaluation, producing per-candidate criteria-application
traceability.

Anti-pre-naming discipline applies throughout §3.1 + §3.2: candidate
regime identifiers (calendar years + macro-condition labels) are
reserved for §3.3 post-adjudication. Backward citations to existing
PHASE2C_7.1 evaluation runs (`v2.regime_holdout` = bear_2022;
`v2.validation` = validation_2024) are permitted as factual references
to scoped/shipped regime evaluations, not as pre-naming.

---

### 3.1 Selection criteria

PHASE2C_8.1's regime-source selection adjudicates candidate historical
regimes against six criteria: one structural veto criterion and five
soft scoring criteria. The veto criterion eliminates structurally-
invalid candidates; the five soft criteria score remaining candidates
on a per-criterion 0-to-1 scale with weighted aggregation.

#### 3.1.0 Structural veto criterion

**V1 — 2025 test split touched-once compliance.**

Any candidate regime whose calendar boundaries overlap with the 2025
test split defined in [`config/environments.yaml`](../../config/environments.yaml)
(v2 split version) is structurally invalid as a PHASE2C_8.1 evaluation
regime. The 2025 test split is the project's touched-once test split
per CLAUDE.md hard rule: "Test data is touched ONCE for final
evaluation. If you peek and iterate, it becomes validation data."

The veto is categorical: a candidate either overlaps the 2025 split
boundary (veto-fail; structurally eliminated at Stage 1) or does not
(veto-pass; advances to Stage 2 soft scoring). Veto status admits no
partial fulfillment.

The veto criterion is the only structural veto. Other criteria score
on the soft scale; extreme failure on a soft criterion (e.g., score-
zero on data availability) acts as de-facto elimination at the
ranking stage but is captured at the scoring layer, not the veto
layer. The single-veto structure preserves the framework's two-stage
analytical clarity.

#### 3.1.1 Soft criterion 1 — macro distinctness

**S1 — Macro distinctness from existing PHASE2C_7.1 evaluation regimes.**

Each candidate regime is scored on whether it presents a distinctly
different macro context from the two PHASE2C_7.1 evaluation regimes
(bear_2022; validation_2024). Macro distinctness is assessed against
three sub-axes:

- Volatility regime distinctness (does the candidate's realized
  volatility band differ from bear_2022's high-volatility post-Luna
  collapse band and validation_2024's moderate-volatility post-halving
  band?)
- Trend regime distinctness (does the candidate's price-direction
  pattern — bull / bear / sideways / mixed — differ from
  bear_2022's strong-bear pattern and validation_2024's mixed-trend
  pattern?)
- Macro-condition distinctness (does the candidate's broader
  macro-financial context — interest rate regime, equity correlation,
  flow patterns — differ from bear_2022 and validation_2024?)

Per-candidate score on S1 ranges from 0.0 (fully duplicative of
existing PHASE2C_7.1 regimes; no incremental macro context) to 1.0
(fully distinct from existing regimes on all three sub-axes). Scoring
is qualitative-but-traceable: each sub-axis assessment cites
documented macro-condition characterization for the candidate regime
and the existing PHASE2C_7.1 regimes.

#### 3.1.2 Soft criterion 2 — data availability

**S2 — OHLCV data availability over the candidate regime's calendar
boundaries.**

Each candidate regime is scored on whether 1h OHLCV data is available
for the full calendar boundaries of the regime, sourced from the
project's canonical data sources (CCXT BTC/USDT 1h at
[`data/raw/btcusdt_1h.parquet`](../../data/raw/btcusdt_1h.parquet);
Binance Vision archived feed at
[`data/raw/btcusdt_1h_archive.parquet`](../../data/raw/btcusdt_1h_archive.parquet)).
Per-candidate score on S2 ranges from 0.0 (no data available; regime
calendar boundaries fall outside available data) to 1.0 (full
calendar-aligned data available with no documented gaps or
zero-volume bar concentrations exceeding the project's known-data-
characteristics baseline of 31 missing hours + 3 zero-volume bars in
2020-2023).

S2 score-zero acts as de-facto elimination at Stage 3 ranking: a
regime with no available data cannot be evaluated regardless of its
score on other criteria. The de-facto elimination is captured at the
ranking stage; structural veto status is reserved for V1.

#### 3.1.3 Soft criterion 3 — config availability

**S3 — Config block availability or feasibility of new config block.**

Each candidate regime is scored on whether an existing config block
exists in [`config/environments.yaml`](../../config/environments.yaml)
that defines the regime's calendar boundaries, or whether a new
config block can be added without modifying immutable date splits
(train / validation / test split boundaries per CLAUDE.md hard rule).
Per-candidate score on S3 ranges from 0.0 (no existing config block;
new config block would require modifying immutable date splits) to
1.0 (existing config block available, or new config block can be
added entirely outside the immutable train / validation / test split
boundaries).

The S3 criterion enforces CLAUDE.md's hard rule that
`config/environments.yaml` date split boundaries are immutable during
a research phase. Adding a new candidate-regime config block that
re-uses the same calendar period as an existing immutable boundary
violates the hard rule; such candidates score 0.0 on S3.

#### 3.1.4 Soft criterion 4 — population sufficiency

**S4 — Trade-population sufficiency under the candidate regime
calendar.**

Each candidate regime is scored on whether the 198-candidate
population is expected to produce sufficient trades over the
candidate regime's calendar boundaries to enable per-candidate
metric computation under PHASE2C_7.1's pinned trade-count filter
(>= 20 trades). Per-candidate score on S4 ranges from 0.0 (regime
calendar duration is too short for the population to produce
sufficient trades; expected trade-population per candidate is < 20)
to 1.0 (regime calendar duration is comfortably sufficient for
trade-population >= 20 per candidate; expected median trades per
candidate exceeds 50).

S4 scoring uses PHASE2C_7.1's per-candidate trade counts as a
calibration baseline: bear_2022 produced median ~75 trades per
candidate over a 12-month period; validation_2024 produced median
~85 trades per candidate over a 12-month period. Candidate regimes
of comparable duration (~6-12 months) score positively; shorter-
duration candidates score lower; very short-duration candidates
(< 3 months) score near zero.

#### 3.1.5 Soft criterion 5 — mechanism-relevance distinctness

**S5 — Mechanism-relevance distinctness for Q-B1 mechanism question.**

Each candidate regime is scored on whether the regime advances at
least one of the three mechanism-question candidates (regime-mismatch
/ pattern-overfit / calibration-coupling) by producing evidence that
distinguishes among them. Per-candidate score on S5 is assessed
against three sub-questions:

- (i) Does this regime differ from existing PHASE2C_7.1 evaluation
  regimes (bear_2022; validation_2024) in ways that distinguish
  regime-mismatch from pattern-overfit? (A regime that produces yet-
  another distinct cohort pattern provides regime-mismatch evidence;
  a regime that produces a pattern matching one of the existing two
  regimes provides pattern-overfit evidence.)
- (ii) Does this regime produce non-monotonic candidate behavior
  consistent with pattern-overfit? (A regime where the same candidate
  passes in some regimes and fails in others — i.e., non-monotonic
  across regime axis — supports pattern-overfit; a regime where a
  candidate's behavior is monotonic across regimes is more consistent
  with regime-mismatch.)
- (iii) Does this regime indirectly probe calibration-coupling via
  expected gate-pass-rate distinctions? (A regime where the calibration-
  coupling hypothesis predicts a specific gate-pass-rate pattern — e.g.,
  thresholds calibrated to one regime fail to generalize to another —
  provides calibration-coupling evidence.)

Per-candidate score on S5 ranges from 0.0 (regime advances no
mechanism-question candidate; produces only redundant evidence) to
1.0 (regime advances at least two of the three mechanism-question
candidates; mechanism-question advancement is the candidate's
primary justification).

S5 is the criterion that ties most directly to PHASE2C_8.0 §5's
recommendation rationale (Q-B1 over Q-B2 because the regime axis
distinguishes mechanism candidates more than the calibration axis).
Per Stage 2 weighted scoring (§3.2), S5 carries the highest single-
criterion weight (0.40) to preserve the rationale at the framework
level.

---

### 3.2 Selection framework

PHASE2C_8.1's regime-source selection framework is a three-stage
structure that applies §3.1 criteria to candidate regime sources:

#### Stage 1 — Veto check

Each candidate regime is checked against the V1 structural veto
criterion. Candidates failing V1 (calendar boundaries overlap with
the 2025 test split) are structurally eliminated. Candidates passing
V1 advance to Stage 2.

The veto check is binary and categorical; veto status admits no
partial fulfillment.

#### Stage 2 — Soft scoring

Each Stage-1-surviving candidate is scored on the five soft criteria
(S1-S5) per the per-criterion operational definitions in §3.1.
Per-criterion scores range from 0.0 to 1.0 on a continuous scale.

Per-candidate aggregate score is computed as the weighted sum:

```
aggregate_score = (S1 × 0.15) + (S2 × 0.15) + (S3 × 0.15)
                + (S4 × 0.15) + (S5 × 0.40)
```

The weight structure (Option β per Ask 1 adjudication):

- S5 (mechanism-relevance distinctness): 0.40
- S1-S4 (macro distinctness; data availability; config availability;
  population sufficiency): 0.15 each
- Sum of weights: 1.00

The weighting structure preserves PHASE2C_8.0 §5's recommendation
rationale at the framework level: mechanism-relevance distinctness
is the criterion most directly tied to Q-B1's mechanism question;
weighting it at 0.40 (vs 0.15 for the other criteria) reflects its
load-bearing structural role. Equal weights (0.20 × 5) would dilute
S5's structural significance; the chosen weighting preserves it.

Per-candidate aggregate scores range from 0.00 (all criteria score
zero) to 1.00 (all criteria score one).

#### Stage 3 — Rank-order selection

Stage-2-scored candidates are rank-ordered by aggregate score
(descending). The top k = 2 candidates are selected for PHASE2C_8.1
evaluation as the additional historical regimes; combined with the
two existing PHASE2C_7.1 evaluation regimes (bear_2022;
validation_2024), the n-target is n = 4 baseline (Option II per
Ask 2 adjudication).

The n = 4 target reflects PHASE2C_8.0 §5's structural reasoning:
n = 3 minimum is too fragile (one additional regime can still
produce degenerate patterns; mechanism-question distinguishability
at n = 3 has only 1 sub-comparison which is statistically weak);
n = 4 baseline allows basic cross-regime structure checks (3 sub-
comparisons; 1 baseline pattern + 2 deviations) without over-
expanding scope or budget.

Score-zero outcomes on any single criterion act as de-facto
elimination at Stage 3 ranking: a candidate scoring 0.0 on any
criterion will have aggregate score lower than candidates scoring
positively on all criteria; the de-facto elimination is captured
naturally by the rank-order structure.

**Score-zero de-facto elimination is not a second structural veto.**
The framework retains exactly one structural veto: V1 (2025 test
split touched-once compliance), adjudicated at Stage 1. Score-zero
outcomes on soft criteria S1-S5 are scoring outcomes resolved inside
Stages 2 and 3 — Stage 2 produces the per-criterion 0.0 score; Stage
3 ranking captures the consequent de-facto elimination via aggregate-
score rank-order. The structural distinction matters operationally:
a soft criterion may shift from score-zero to non-zero as evidence
surfaces (e.g., archived datasets become available; new config blocks
are added defensibly outside immutable splits) without any change to
the framework; a structural veto is categorical and cannot shift.
Treating score-zero soft outcomes as structural veto would conflate
"currently fails" with "axiomatically fails" and reduce the
conditional-claim discipline at the criteria level.

Tie-breaking for Stage 3 ranking: if two or more candidates produce
equal aggregate scores at the top-k = 2 boundary, the tie is broken
by S5 score (higher S5 wins; preserves mechanism-relevance prioritization);
if S5 scores are also equal, by S1 score (higher S1 wins; preserves
macro distinctness as secondary priority).

#### Stage A → Stage B handoff

Stage A locks the criteria (V1 + S1-S5) and framework (3-stage; weights
fixed; n = 4 target; tie-breaking specified). Stage B (§3.3)
applies the locked criteria and framework to enumerate specific
candidate regime sources, producing per-candidate criteria-
application traceability and the recommended top-k = 2 selection
with rationale.

The Stage A → Stage B handoff is structured to preserve anti-pre-
naming discipline at Stage A and enable backward-referencing
adjudication at Stage B. Stage A's prose contains no candidate
regime identifiers (no calendar years; no macro-condition labels);
Stage B's prose enumerates candidate regimes by identifier with
per-candidate scoring traceability.

---


---


## 3.3 Candidate-regime adjudication

Stage B applies the §3.1 + §3.2 locked criteria and framework to
specific historical regime sources. Anti-pre-naming discipline lifts
at §3.3 per Stage A → Stage B handoff: candidate regime identifiers
(calendar years + macro-condition labels) appear in §3.3 prose;
selection adjudication produces the top-k = 2 additional regimes
(combined with PHASE2C_7.1's bear_2022 + validation_2024 baseline,
n = 4 total target).

### 3.3.1 Candidates evaluated

Three calendar-year windows from the canonical raw data history are
evaluated: 2020, 2021, and 2023. The candidate set is bounded by:

- **Lower bound**: Canonical raw data history starts 2020-01-01
  ([`data/raw/btcusdt_1h.parquet`](../../data/raw/btcusdt_1h.parquet)).
  Earlier calendar years lack source data and fail S2 (data
  availability) at score-zero.
- **Upper bound — V1 structural veto**: 2025 calendar-year window
  overlaps the v2 test split per
  [`config/environments.yaml`](../../config/environments.yaml).
  Touching 2025 violates CLAUDE.md hard rule "Test data is touched
  ONCE for final evaluation." 2025 fails V1 categorically and is
  structurally eliminated.
- **2026 partial-year exclusion**: 2026 is the current operational
  year (today's date 2026-04-27); only ~4 months of 2026 data is
  available. Partial-year evaluation fails S4 (population
  sufficiency) at score-near-zero — expected per-candidate trade
  count over ~4 months is insufficient relative to the >= 20 trade-
  count filter calibration baseline. 2026 is excluded from the
  candidate set on partial-year grounds, not on V1 veto grounds
  (2026 is not a touched-once test split).

The candidate set {2020, 2021, 2023} is the bounded V1-passing
candidate population for Stage B adjudication. 2022 and 2024 are
already PHASE2C_7.1 evaluation regimes (bear_2022 and validation_2024
respectively) and are not re-considered as candidates (carry-forward
inheritance per Observation YYY → Option A).

### 3.3.2 Per-candidate V1 + S1-S5 adjudication

Per-candidate scoring against the locked criteria. Qualitative-band
mapping to numeric scores per the §3.2 Stage 2 0-to-1 continuous
scale: HIGH ≈ 0.85; MED ≈ 0.55; LOW ≈ 0.25.

| Candidate | V1 | S1 | S2 | S3 | S4 | S5 | Lean |
|---|---|---|---|---|---|---|---|
| 2020 | PASS | HIGH | HIGH | MED | HIGH | HIGH | SELECT |
| 2021 | PASS | HIGH | HIGH | MED | HIGH | HIGH | SELECT |
| 2023 | PASS | MED | HIGH | MED | HIGH | MED | BACKUP |

Per-criterion adjudication evidence per candidate:

#### 2020 calendar-year window

- **V1 (2025 touched-once compliance)**: PASS. 2020-01-01 to 2020-12-31
  does not overlap the 2025 test split.
- **S1 (macro distinctness)**: HIGH. The 2020 macro context is
  structurally distinct from bear_2022 (post-Luna collapse; sustained
  high-volatility bear) and validation_2024 (post-halving / ETF-
  approval; moderate-volatility mixed trend). 2020 contains the
  COVID-19 crash (Q1 2020 dramatic dislocation) and the post-crash
  recovery rally (Q4 2020 strong upward trend); volatility regime is
  bimodal-extreme; macro-financial context features unique pandemic-
  driven dynamics absent from 2022 or 2024.
- **S2 (data availability)**: HIGH. 1h OHLCV data starts 2020-01-01
  per CLAUDE.md "Known Data Characteristics"; full calendar year
  available with documented gaps + zero-volume bars in 2020 (subset
  of the 31 known missing hours + 3 zero-volume bars in 2020-2023)
  not exceeding the project's known-data-characteristics baseline.
- **S3 (config availability)**: MED. No existing config block for
  2020-only evaluation; new config block can be added to
  [`config/environments.yaml`](../../config/environments.yaml) as a
  parallel evaluation-only block without modifying the immutable train
  block boundaries (which include 2020-2021 + 2023 calendar period as
  training periods). The new block coexists with the train block;
  CLAUDE.md hard rule on date split immutability is not violated.
- **S4 (population sufficiency)**: HIGH. Full-year duration
  comfortably matches PHASE2C_7.1's bear_2022 and validation_2024
  per-candidate trade-count baseline (median ~75-85 trades per
  candidate over 12-month windows); expected median per-candidate
  trade count exceeds 50.
- **S5 (mechanism-relevance distinctness)**: HIGH. Three sub-question
  evaluation:
  - (i) Regime-mismatch vs pattern-overfit distinguishability: 2020's
    pandemic-driven extreme regime is structurally different from
    both bear_2022 and validation_2024 across volatility / trend /
    macro-financial axes; produces incremental regime-axis evidence.
  - (ii) Pattern-overfit indicators via non-monotonic candidate
    behavior: 2020's bimodal volatility (Q1 crash + Q4 rally) creates
    candidate-behavior conditions where pattern-overfit candidates
    are likely to show non-monotonic pass/fail relative to other
    regimes.
  - (iii) Calibration-coupling indirect probe: 2020's extreme volatility
    band differs sharply from 2022 / 2024 calibration baselines;
    candidates whose gates are calibration-coupled to PHASE2C_6 train
    distribution are likely to show distinctive gate-pass-rate
    distortions in 2020.

#### 2021 calendar-year window

- **V1**: PASS. 2021-01-01 to 2021-12-31 does not overlap the 2025 test
  split.
- **S1**: HIGH. The 2021 macro context features the cycle-peak bull
  market (Q4 2021 ATH), parabolic upward trend with mid-year sharp
  correction (May 2021 selloff), and high-volatility bull regime
  with sustained directional bias. Structurally distinct from
  bear_2022 (sustained bear) and validation_2024 (mixed trend);
  bull-cycle macro context is absent from both PHASE2C_7.1 regimes.
- **S2**: HIGH. Full calendar-year 1h OHLCV data available; no
  documented unusual data quality concerns specific to 2021 beyond
  the known-data-characteristics baseline.
- **S3**: MED. No existing config block for 2021-only evaluation;
  new evaluation-only config block addable per S3 reasoning identical
  to 2020.
- **S4**: HIGH. Full-year duration matches per-candidate trade-count
  baseline; expected median per-candidate trade count exceeds 50.
- **S5**: HIGH. Three sub-question evaluation:
  - (i) Regime-mismatch vs pattern-overfit distinguishability: 2021's
    cycle-peak bull regime is structurally different from both
    bear_2022 (bear) and validation_2024 (mixed); produces incremental
    regime-axis evidence on the bull side.
  - (ii) Pattern-overfit indicators: 2021's parabolic-then-correction
    pattern creates candidate-behavior conditions distinct from the
    range-bound and mixed regimes; non-monotonic candidate pass/fail
    likely if pattern-overfit is operative.
  - (iii) Calibration-coupling indirect probe: 2021's high-volatility
    bull regime tests whether candidate gates calibrated against
    PHASE2C_6 train distribution generalize to bull conditions
    distinct from the 2024 mixed-trend distribution.

#### 2023 calendar-year window

- **V1**: PASS. 2023-01-01 to 2023-12-31 does not overlap the 2025
  test split.
- **S1**: MED. The 2023 macro context features post-FTX-collapse
  recovery (Q1 2023 banking-crisis-spillover dislocation; rest-of-
  year sustained recovery with upward bias). Recovery-regime
  characterization shares partial macro-condition overlap with
  validation_2024 (both post-stress recovery periods with mixed-to-
  upward trend); macro distinctness from validation_2024 is
  structurally weaker than 2020 / 2021's distinctness from both
  PHASE2C_7.1 regimes.
- **S2**: HIGH. Full calendar-year 1h OHLCV data available; no
  documented unusual data quality concerns specific to 2023 beyond
  the known-data-characteristics baseline.
- **S3**: MED. No existing config block for 2023-only evaluation;
  new evaluation-only config block addable per S3 reasoning identical
  to 2020 / 2021.
- **S4**: HIGH. Full-year duration matches per-candidate trade-count
  baseline; expected median per-candidate trade count exceeds 50.
- **S5**: MED. Three sub-question evaluation:
  - (i) Regime-mismatch vs pattern-overfit distinguishability: 2023's
    recovery regime is structurally less distinct from validation_2024
    (both recovery / mixed); regime-axis evidence is partially
    duplicative.
  - (ii) Pattern-overfit indicators: 2023's range-bound-with-upward-bias
    pattern creates moderate non-monotonic conditions but with reduced
    contrast against validation_2024.
  - (iii) Calibration-coupling indirect probe: 2023's recovery
    volatility band is closer to validation_2024 calibration baseline;
    calibration-coupling distortion signals are weaker.

### 3.3.3 Weighted scores

Per-candidate aggregate score per the §3.2 Stage 2 weighted-sum
formula: `aggregate_score = (S1 × 0.15) + (S2 × 0.15) + (S3 × 0.15)
+ (S4 × 0.15) + (S5 × 0.40)`.

| Candidate | S1 | S2 | S3 | S4 | S5 | Aggregate |
|---|---|---|---|---|---|---|
| 2020 | 0.85 | 0.85 | 0.55 | 0.85 | 0.85 | 0.805 |
| 2021 | 0.85 | 0.85 | 0.55 | 0.85 | 0.85 | 0.805 |
| 2023 | 0.55 | 0.85 | 0.55 | 0.85 | 0.55 | 0.640 |

Aggregate computation example (2020):
```
(0.85 × 0.15) + (0.85 × 0.15) + (0.55 × 0.15) + (0.85 × 0.15) + (0.85 × 0.40)
= 0.1275 + 0.1275 + 0.0825 + 0.1275 + 0.3400
= 0.8050
```

Rank order (descending aggregate): 2020 (0.805) ≈ 2021 (0.805) > 2023
(0.640).

### 3.3.4 Top-2 selection

The top-k = 2 candidates by aggregate weighted score are **2020 and
2021**. Both are selected as additional regimes for PHASE2C_8.1
evaluation. Combined with PHASE2C_7.1's bear_2022 + validation_2024
baseline regimes, the n-target n = 4 baseline is met:

| Regime | Source arc | Calendar window | Macro characterization |
|---|---|---|---|
| eval_2020_v1 | PHASE2C_8.1 | 2020-01-01 to 2020-12-31 | COVID crash + recovery; bimodal-extreme volatility |
| eval_2021_v1 | PHASE2C_8.1 | 2021-01-01 to 2021-12-31 | Cycle-peak bull; parabolic + mid-year correction |
| bear_2022 | PHASE2C_6 / 7.1 carry-forward | 2022-01-01 to 2022-12-31 | Post-Luna sustained bear; high volatility |
| validation_2024 | PHASE2C_7.1 carry-forward | 2024-01-01 to 2024-12-31 | Post-halving / ETF; moderate-volatility mixed trend |

The four regimes span four structurally distinct macro contexts:
extreme-volatility crash + recovery (2020); parabolic bull (2021);
sustained bear (2022); mixed-trend recovery (2024). The breadth
preserves Q-B1's mechanism-question distinguishability — across the
four regimes, regime-mismatch vs pattern-overfit vs calibration-
coupling candidates produce structurally distinguishable evidence
patterns at population level.

Tie-breaking note: 2020 and 2021 are tied at aggregate score 0.805.
Per §3.2 Stage 3 tie-breaking specification (S5 first, S1 second),
both candidates also tie at S5 = 0.85 and S1 = 0.85. The tie at
top-k = 2 boundary is non-operational because both candidates fit
within the selection window; both are selected.

Selection rationale (consolidated):

- 2020 and 2021 are jointly selected because their high aggregate
  scores (0.805 each) reflect strong performance on all five soft
  criteria with mechanism-relevance (S5) at HIGH for both — directly
  serving Q-B1's mechanism-question advance.
- The selected pair maximizes macro-context diversity: 2020's
  pandemic-driven bimodal regime + 2021's parabolic-bull regime
  occupy macro axes that PHASE2C_7.1's bear_2022 + validation_2024
  do not span.
- The selected pair preserves engine-version invariance (Option A
  per Observation YYY): both are evaluated under the corrected
  WF engine at lineage tag wf-corrected-v1; existing PHASE2C_7.1
  runs are re-used without re-evaluation.
- Per §3.2 Stage 3 ranking, score-zero outcomes are absent across
  both selected candidates and the non-selected 2023 candidate; no
  de-facto elimination at ranking layer is operative.

**In-sample evaluation caveat.** 2020 and 2021 overlap the original
train-window context per the v2 split version
([`config/environments.yaml`](../../config/environments.yaml); train
= 2020-2021 + 2023). The 198-candidate population's PHASE2C_5
walk-forward training process used sub-windows of these calendar
periods. Evaluating the population against full-calendar-year 2020
and 2021 is therefore not equivalent to evaluating against
fully-untouched validation/test evidence (as bear_2022 holdout and
validation_2024 are). The in-sample concern is mitigated by
walk-forward sub-window discipline (each candidate's training
windows are sub-windows of the calendar year, not the full year;
walk-forward cross-validation operates within-regime), but not
fully eliminated. The caveat is preserved at §3.3 selection
rationale + carried forward to §10 risks taxonomy where it surfaces
as a distinct epistemic concern: 2020/2021 overlap the original
train-window context; mitigated by walk-forward sub-window
discipline, but not equivalent to untouched validation/test
evidence.

### 3.3.5 Non-selected rationale

**2023 calendar-year window — backup regime, not selected for n = 4
baseline.**

Rationale for 2023's ranking below the top-k = 2 boundary:

- **S1 (macro distinctness): MED**. 2023's recovery-regime
  characterization shares partial macro-condition overlap with
  validation_2024 (both post-stress recovery periods with mixed-to-
  upward trend). The macro-axis distinctness from validation_2024 is
  weaker than 2020's distinctness (extreme-volatility bimodal) or
  2021's distinctness (parabolic bull).
- **S5 (mechanism-relevance): MED**. The S5 sub-question (i)
  (regime-mismatch vs pattern-overfit distinguishability) is weaker
  for 2023 because the regime-axis evidence is partially duplicative
  of validation_2024 — both recovery regimes with similar macro
  characterization. The S5 sub-question (iii) (calibration-coupling
  indirect probe) is also weaker because 2023's volatility band is
  closer to validation_2024 baseline; calibration-coupling distortion
  signals are reduced.
- **Aggregate score 0.640 vs top-2 0.805**: the 0.165 aggregate-score
  gap is driven by S1 + S5 differences (S1 0.55 vs 0.85; S5 0.55 vs
  0.85). Per the §3.2 Stage 2 weighting, S5's 0.40 weight makes the
  S5-MED penalty operationally large (−0.12 aggregate vs HIGH); S1's
  0.15 weight makes the S1-MED penalty smaller (−0.045 aggregate vs
  HIGH). Combined penalty against either 2020 or 2021 baseline is
  −0.165 aggregate.

2023 is retained as a backup regime in case operational concerns
during PHASE2C_8.1 implementation reveal that 2020 or 2021 cannot be
evaluated cleanly (e.g., new data-quality issue surfaces; config
block modification cannot be added without violating immutability;
unanticipated implementation blocker). The backup status is documented
here as a forward-pointing fallback; activation of backup status would
require a new adjudication cycle to confirm 2023's per-criterion
scores still hold against the operational concern that triggered the
fallback.

### 3.3.6 Conditional-shift note

The selection {2020, 2021} as top-2 additional regimes is conditional
on the criteria + framework + scoring evidence locked at this Stage B
sub-cycle. Five conditional-shift triggers would invalidate or modify
the selection:

- **Shift trigger 1 — Engine-version drift during PHASE2C_8.1
  execution.** If the corrected WF engine version changes during
  implementation (e.g., bug fix lands; lineage tag advances beyond
  wf-corrected-v1), Option A's engine-version invariance assumption
  breaks per Observation YYY adjudication. Re-evaluation of bear_2022
  + validation_2024 under the new engine version becomes necessary;
  selection {2020, 2021} adjudication may need to re-rank if
  re-evaluation produces structurally different baseline regime
  characterizations.
- **Shift trigger 2 — Data quality issue surfaces in 2020 or 2021.**
  If S2 (data availability) downgrades from HIGH to LOW or score-zero
  for 2020 or 2021 (e.g., previously-undocumented data corruption
  surfaces; canonical data history revision occurs), the affected
  candidate's aggregate score drops sharply. Backup regime 2023
  would advance into the top-2 selection.
- **Shift trigger 3 — Config block addition blocked by immutability
  re-interpretation.** If S3 (config availability) re-interpretation
  determines that adding a parallel evaluation-only config block
  over a calendar period that overlaps the train block does
  constitute "modifying immutable date splits" (current S3 = MED
  reflects the parallel-block-not-modifying interpretation), all
  three candidates' S3 scores drop to 0.0; the structural veto
  status of immutability re-interpretation needs adjudication; the
  candidate pool may need to expand beyond V1-passing calendar
  windows.
- **Shift trigger 4 — Mechanism-question framing revision.** If the
  Q-B1 mechanism-question framing revises (e.g., a fourth mechanism
  candidate surfaces; the three current candidates are subdivided),
  S5 scoring per candidate may need re-adjudication; candidates
  scoring HIGH on S5 under the current framing may score MED or LOW
  under the revised framing.
- **Shift trigger 5 — Population sufficiency calibration revision.**
  If S4 (population sufficiency) calibration baseline is revised
  (e.g., the >= 20 trade-count filter is replaced by a higher threshold;
  the expected median per-candidate trade count threshold is raised),
  candidate scoring on S4 may shift; partial-year exclusions (e.g.,
  2026) may need re-evaluation against the new threshold.

The conditional-shift framing preserves the framework's
falsifiability and identifies operational signals that would trigger
re-adjudication. None of the five triggers are anticipated as
imminent at PHASE2C_8.1 implementation initiation.

---


---


## 3.4 Per-regime config specification

PHASE2C_8.1's n=4 baseline composition contains two PHASE2C_8.1-novel
regimes (eval_2020_v1 + eval_2021_v1) requiring new config blocks +
artifact paths + lineage attestation. The two PHASE2C_7.1-inherited
regimes (bear_2022 + validation_2024) re-use existing config blocks +
artifact paths per Option A engine-version invariance.

§3.4 specifies per-regime operational config for the two novel regimes;
inherited regimes' config is referenced backward to PHASE2C_7.1 plan §3
without restatement.

### 3.4.1 eval_2020_v1 — pandemic-driven bimodal regime

**Regime name (canonical config-block label):** `eval_2020_v1`

**Regime window (UTC):**
- Start: 2020-01-01 00:00:00 UTC
- End: 2020-12-31 23:00:00 UTC
- Duration: 366 calendar days × 24 hours = 8,784 expected 1h bars
  (subject to known-data-characteristics gaps + zero-volume bars
  per CLAUDE.md "Known Data Characteristics")

**Macro characterization:** Pandemic-driven bimodal volatility; Q1
2020 COVID-19 crash + Q4 2020 post-crash recovery rally; structurally
distinct from PHASE2C_7.1's bear_2022 + validation_2024 across
volatility / trend / macro-financial axes.

**Data sources (carry-forward from PHASE2C_6 + PHASE2C_7.1):**
- Primary: CCXT BTC/USDT 1h OHLCV at
  [`data/raw/btcusdt_1h.parquet`](../../data/raw/btcusdt_1h.parquet)
  (canonical current dataset)
- Reference: Binance Vision archived feed at
  [`data/raw/btcusdt_1h_archive.parquet`](../../data/raw/btcusdt_1h_archive.parquet)
  (audit completeness reference)

**Config block addition target:**
[`config/environments.yaml`](../../config/environments.yaml) under
the `evaluation_regimes` section (parallel to existing
`regime_holdout` and `validation` blocks). The new block is
evaluation-only; it does not modify the immutable train / validation
/ test split boundaries (CLAUDE.md hard rule preserved).

Proposed config block structure (illustrative; final wording at §6
producer artifact specification):
```yaml
evaluation_regimes:
  eval_2020_v1:
    start_date: "2020-01-01T00:00:00Z"
    end_date: "2020-12-31T23:00:00Z"
    macro_characterization: "pandemic_bimodal"
    arc_of_origin: "PHASE2C_8.1"
    schema_discriminator: "phase2c_8_1"
```

**Canonical artifact path (PHASE2C_8.1 evaluation runs):**
- Output directory:
  `data/phase2c_evaluation_gate/eval_2020_v1/`
- Key files (per PHASE2C_7.1 audit_2024_v1 pattern):
  - `holdout_results.csv` — per-candidate metrics (sharpe / max_drawdown
    / total_return / total_trades) under eval_2020_v1 window
  - `holdout_results_filtered.csv` — trade-count-filtered subset
    (>= 20 trades per candidate; PHASE2C_7.1 §5.3 Rule 1 carry-forward)
  - `holdout_summary.json` — aggregate pass/fail counts per cohort
    (primary / audit-only) + 4-criterion AND-gate pass count
  - `lineage_attestation.json` — engine version + commit + lineage
    tag + schema_discriminator + arc_of_origin

**Calibration config:** None required at PHASE2C_8.1 implementation
(per Q-B1 scope: regime axis evaluation, not calibration axis).
PHASE2C_8.1 evaluates the 198-candidate population at PHASE2C_6's
calibration baseline (4-criterion AND-gate; >= 20 trade-count filter)
across all 4 regimes uniformly.

**Schema discriminator:** `phase2c_8_1` (per D3 carry-forward +
extension; advances from PHASE2C_7.1's `phase2c_7_1`).

### 3.4.2 eval_2021_v1 — cycle-peak parabolic-bull regime

**Regime name (canonical config-block label):** `eval_2021_v1`

**Regime window (UTC):**
- Start: 2021-01-01 00:00:00 UTC
- End: 2021-12-31 23:00:00 UTC
- Duration: 365 calendar days × 24 hours = 8,760 expected 1h bars
  (subject to known-data-characteristics gaps + zero-volume bars
  per CLAUDE.md "Known Data Characteristics")

**Macro characterization:** Cycle-peak bull market; Q4 2021 ATH;
parabolic upward trend with mid-year sharp correction (May 2021
selloff); high-volatility bull regime with sustained directional
bias. Structurally distinct from PHASE2C_7.1's bear_2022 + validation_2024
on the bull / cycle-peak axis.

**Data sources (carry-forward from PHASE2C_6 + PHASE2C_7.1):**
- Primary: CCXT BTC/USDT 1h OHLCV at
  [`data/raw/btcusdt_1h.parquet`](../../data/raw/btcusdt_1h.parquet)
- Reference: Binance Vision archived feed at
  [`data/raw/btcusdt_1h_archive.parquet`](../../data/raw/btcusdt_1h_archive.parquet)

**Config block addition target:**
[`config/environments.yaml`](../../config/environments.yaml) under
the `evaluation_regimes` section. Same structural pattern as
eval_2020_v1; evaluation-only block; immutable splits preserved.

Proposed config block structure (illustrative):
```yaml
evaluation_regimes:
  eval_2021_v1:
    start_date: "2021-01-01T00:00:00Z"
    end_date: "2021-12-31T23:00:00Z"
    macro_characterization: "parabolic_bull"
    arc_of_origin: "PHASE2C_8.1"
    schema_discriminator: "phase2c_8_1"
```

**Canonical artifact path (PHASE2C_8.1 evaluation runs):**
- Output directory:
  `data/phase2c_evaluation_gate/eval_2021_v1/`
- Key files (parallel pattern to eval_2020_v1):
  - `holdout_results.csv`
  - `holdout_results_filtered.csv`
  - `holdout_summary.json`
  - `lineage_attestation.json`

**Calibration config:** None required (same reasoning as eval_2020_v1;
PHASE2C_6 calibration baseline applied uniformly across all 4 regimes).

**Schema discriminator:** `phase2c_8_1` (per D3).

### 3.4.3 PHASE2C_7.1-inherited regimes (Option A re-use)

Per Observation YYY → Option A adjudication (engine-version invariance
load-bearing), PHASE2C_7.1's bear_2022 + validation_2024 evaluation
runs are re-used as PHASE2C_8.1's baseline regimes without
re-evaluation. The inherited regimes carry their existing config +
artifact paths + schema discriminator forward to PHASE2C_8.1's
multi-regime comparison matrix.

#### bear_2022 (PHASE2C_6 / PHASE2C_7.1 carry-forward)

- **Regime name (canonical config-block label):** `bear_2022` (existing
  v2.regime_holdout split)
- **Regime window:** 2022-01-01 00:00:00 UTC to 2022-12-31 23:00:00 UTC
- **Macro characterization:** Post-Luna sustained bear; high volatility
- **Data sources:** Carry-forward from PHASE2C_6
  ([`data/raw/btcusdt_1h.parquet`](../../data/raw/btcusdt_1h.parquet) +
  [`data/raw/btcusdt_1h_archive.parquet`](../../data/raw/btcusdt_1h_archive.parquet))
- **Existing artifact paths (PHASE2C_6 audit_v1 + PHASE2C_7.1 carry-forward):**
  - `data/phase2c_evaluation_gate/audit_v1/holdout_results.csv`
  - `data/phase2c_evaluation_gate/audit_v1/holdout_summary.json`
- **Schema discriminator:** `phase2c_7_1` (PHASE2C_7.1-tagged; not advanced
  to phase2c_8_1 because the runs are not re-evaluated)
- **Re-use status:** Option A; engine-version invariance load-bearing;
  no re-evaluation under PHASE2C_8.1; existing runs feed into
  PHASE2C_8.1's multi-regime comparison matrix at §8 Step 4

#### validation_2024 (PHASE2C_7.1 carry-forward)

- **Regime name (canonical config-block label):** `validation_2024`
  (existing v2.validation split)
- **Regime window:** 2024-01-01 00:00:00 UTC to 2024-12-31 23:00:00 UTC
- **Macro characterization:** Post-halving / ETF-approval; moderate-
  volatility mixed trend
- **Data sources:** Carry-forward from PHASE2C_7.1
  ([`data/raw/btcusdt_1h.parquet`](../../data/raw/btcusdt_1h.parquet) +
  [`data/raw/btcusdt_1h_archive.parquet`](../../data/raw/btcusdt_1h_archive.parquet))
- **Existing artifact paths (PHASE2C_7.1 audit_2024_v1):**
  - `data/phase2c_evaluation_gate/audit_2024_v1/holdout_results.csv`
  - `data/phase2c_evaluation_gate/audit_2024_v1_filtered/holdout_results_filtered.csv`
  - `data/phase2c_evaluation_gate/audit_2024_v1/holdout_summary.json`
- **Schema discriminator:** `phase2c_7_1` (PHASE2C_7.1-tagged; not
  advanced to phase2c_8_1)
- **Re-use status:** Option A; same as bear_2022

### 3.4.4 n=4 baseline composition with cross-arc inheritance

PHASE2C_8.1's 4-regime baseline composition consolidates per-regime
config:

| Regime | Source arc | Schema disc. | Calendar window | Re-evaluate? |
|---|---|---|---|---|
| eval_2020_v1 | PHASE2C_8.1 | phase2c_8_1 | 2020-01-01 to 2020-12-31 | Yes (novel) |
| eval_2021_v1 | PHASE2C_8.1 | phase2c_8_1 | 2021-01-01 to 2021-12-31 | Yes (novel) |
| bear_2022 | PHASE2C_6 / 7.1 | phase2c_7_1 | 2022-01-01 to 2022-12-31 | No (Option A) |
| validation_2024 | PHASE2C_7.1 | phase2c_7_1 | 2024-01-01 to 2024-12-31 | No (Option A) |

The mixed schema discriminator (phase2c_7_1 + phase2c_8_1 across the
4 regimes) is operationally reconciled via per-run metadata at §6
producer artifact specification + §8 Step 4 multi-regime comparison
matrix consumer logic. Per-run metadata captures schema_discriminator
+ arc_of_origin + lineage_tag; the cross-regime comparison matrix
consumes per-run metrics regardless of discriminator value.

Engine-version invariance (Option A per Observation YYY adjudication)
is the load-bearing assumption for cross-arc run re-use. The
assumption is captured at §7 lineage attestation: "PHASE2C_7.1
evaluation runs (bear_2022 + validation_2024) under wf-corrected-v1
engine version are re-used in PHASE2C_8.1's multi-regime comparison
matrix as evidentiary-equivalent runs. Engine-version change during
PHASE2C_8.1 execution invalidates this re-use; re-evaluation under
the new engine version is required if engine version drifts."

The schema_discriminator difference (phase2c_7_1 vs phase2c_8_1) is
metadata-only; the underlying evaluation semantics, scoring methodology,
and gate criteria are unchanged across discriminators (per D2
4-criterion AND-gate carry-forward + D1 trade-count filter
carry-forward).

### 3.4.5 Forward references

§3.4 per-regime config specifications feed three downstream sections:

- **§6 producer artifact specification**: §6 specifies the producer
  script that generates the eval_2020_v1 + eval_2021_v1 evaluation
  runs against the 198-candidate population; consumes §3.4 per-regime
  config; emits artifacts to the canonical paths specified at §3.4
- **§7 lineage attestation**: §7 attests engine-version invariance
  for Option A re-use of bear_2022 + validation_2024; references
  §3.4.3's PHASE2C_7.1-inherited regime specification
- **§8 Step 4 multi-regime comparison matrix**: §8 Step 4 consumes
  per-regime metrics from all 4 regimes' artifact paths (§3.4.1 +
  §3.4.2 for novel regimes; §3.4.3 for inherited regimes) and
  produces the multi-regime comparison matrix

§3.4 closes the §3 sub-cycle (Stage A §3.1 + §3.2 + Stage B §3.3 +
§3.4 consolidated). The locked criteria + framework + selected
regimes + per-regime config form the §3 substantive content; §4-§10
drafting cycles operate at mechanical-codification register against
this §3 anchor.

---


---


## 4. Evaluation gate

PHASE2C_8.1's evaluation gate inherits PHASE2C_7.1 D2's 4-criterion
AND-gate substantively unchanged. The gate applies per-regime to
each of the n=4 regimes (eval_2020_v1, eval_2021_v1, bear_2022,
validation_2024) producing per-candidate per-regime pass/fail
outcomes. Cross-regime intersection logic (which candidates pass in
all n regimes; cross-regime pass-rate comparison) is §8 Step 4
territory; §4's scope is per-regime gate semantics only.

### 4.1 The four criteria (D2 carry-forward)

Each candidate's per-regime evaluation produces four metrics, each
gated against a threshold per the AND-gate:

- **Sharpe ratio threshold**: `sharpe >= -0.5`
  - Operationalization: per-regime sharpe ratio computed over the
    candidate's trades within the regime calendar window
  - Threshold rationale: PHASE2C_7.1 D2 carry-forward; preserves
    PHASE2C_6 evaluation gate calibration

- **Maximum drawdown threshold**: `max_drawdown <= 0.25`
  - Operationalization: per-regime max drawdown computed over the
    candidate's equity curve within the regime calendar window
  - Threshold rationale: PHASE2C_7.1 D2 carry-forward

- **Total return threshold**: `total_return >= -0.15`
  - Operationalization: per-regime total return computed over the
    candidate's trades within the regime calendar window
  - Threshold rationale: PHASE2C_7.1 D2 carry-forward

- **Total trades threshold**: `total_trades >= 5`
  - Operationalization: per-regime total trades count within the
    regime calendar window
  - Threshold rationale: PHASE2C_7.1 D2 carry-forward; distinct
    from §5 trade-count filter (which applies a separate >= 20
    threshold for filtering primary-cohort statistical significance)

The gate is conjunctive: a candidate passes the per-regime gate if
and only if all four criteria pass simultaneously. Failure on any
single criterion produces per-regime fail.

### 4.2 Per-regime AND-gate application semantics

PHASE2C_8.1's per-regime application semantics:

- Each candidate is evaluated against each of the n=4 regimes
  independently
- Per-regime evaluation produces 4 per-regime metrics + 1 per-regime
  AND-gate pass/fail outcome per candidate
- The 198-candidate population × 4-regime baseline produces 198 × 4 =
  792 per-candidate per-regime pass/fail outcomes
- Per-regime outcomes feed §8 Step 4 multi-regime comparison matrix
  consumer logic for cross-regime intersection analysis

Per-regime AND-gate application is metric-level + threshold-level
identical across all 4 regimes. No per-regime threshold tuning;
no per-regime metric definition variation. Uniform application
preserves cross-regime comparability per §3.4.4 schema-discriminator-
agnostic comparison framing.

### 4.3 Per-regime evaluation outputs

Per-regime evaluation produces canonical artifact files per §3.4
artifact path specification:

- `holdout_results.csv`: per-candidate per-regime metrics (sharpe,
  max_drawdown, total_return, total_trades) + per-candidate per-regime
  AND-gate pass/fail outcome
- `holdout_summary.json`: aggregate per-regime pass-counts by cohort
  (primary n=44 / audit-only n=154); 4-criterion AND-gate pass count

The per-regime artifact files at `data/phase2c_evaluation_gate/<regime>_v1/`
follow PHASE2C_7.1 audit_2024_v1 pattern preservation per §3.4.

### 4.4 Forward references

§4's per-regime AND-gate output feeds three downstream sections:

- **§5 trade-count filter**: §5 specifies the >= 20 trade-count
  filter that operates on §4's per-regime outputs to produce the
  filtered subset (primary-cohort statistical significance threshold)
- **§8 Step 4 multi-regime comparison matrix**: §8 Step 4 consumes
  per-regime AND-gate pass/fail outcomes across all n=4 regimes;
  produces cross-regime intersection analysis (which candidates pass
  in all n regimes; cross-regime pass-rate comparison; cohort-stratified
  cross-regime matrix)
- **§9 pass/fail criteria**: §9 references §4's per-regime gate as
  the per-regime evaluation building block; §9 specifies higher-order
  pass/fail criteria over the cross-regime evaluation evidence

§4 is a carry-forward section; substantive content matches
PHASE2C_7.1 plan §4 modulo per-regime application semantics.

---

## 5. Trade-count filter

PHASE2C_8.1's trade-count filter inherits PHASE2C_7.1 §5.3 Rule 1
substantively unchanged: filter to candidates with `total_trades >= 20`
per regime to produce the primary-cohort statistical-significance
filtered subset. The filter operates per-regime on §4's per-regime
AND-gate outputs.

### 5.1 Trade-count threshold (D1 carry-forward)

Filter rule: a candidate's per-regime evaluation is included in the
filtered subset if and only if `total_trades >= 20` for that regime.
The threshold is pre-specified before evaluation execution and locked
across all n=4 regimes.

Threshold rationale (PHASE2C_7.1 §5.3 Rule 1 carry-forward):
- Below 20 trades per regime: per-candidate metrics carry insufficient
  statistical power for population-level inference
- 20-trade threshold: lower bound at which sharpe, max_drawdown,
  total_return are computed against ≥ 20 trade samples; preserves
  per-candidate metric stability across regimes
- Threshold value invariant across regimes; preserves cross-regime
  comparability per §3.4.4 schema-discriminator-agnostic comparison

### 5.2 Pre-specification discipline

The trade-count filter threshold is pre-specified at PHASE2C_8.1
spec drafting time (this document) and locked across the arc.
Threshold tuning post-evaluation would constitute selection-effect
introduction; the pre-specification discipline preserves §10 risks
falsifiability against post-hoc threshold revision.

PHASE2C_7.1 plan §5.3 Rule 1 established the >= 20 threshold;
PHASE2C_8.1 inherits the threshold without re-litigation. Conditional-
shift trigger 5 (population sufficiency calibration revision) per §3.3.6
captures the falsifiability path: if the threshold is revised, the
revision triggers re-adjudication of §3.3 candidate-regime scoring
(S4 population sufficiency rubric) + §5 threshold rationale.

### 5.3 Per-regime filter application

Per-regime filter application produces per-regime filtered subsets
of the 198-candidate population:

- Per-regime filtered subset = candidates where `total_trades >= 20`
  in that regime
- Per-regime filtered subset cardinality varies across regimes
  (depends on per-regime trade-count distribution; longer/more-volatile
  regimes produce higher trade counts; shorter/less-volatile regimes
  produce lower trade counts)
- Per-regime filtered subset is independent of cross-regime
  intersection (a candidate may pass the trade-count filter in one
  regime and fail in another; cross-regime intersection is §8 Step 4
  territory)

PHASE2C_7.1 baseline trade-count distributions: bear_2022 produced
median ~75 trades per candidate; validation_2024 produced median ~85
trades per candidate. Both distributions comfortably exceed the 20-
trade threshold for primary cohort (n=44 candidates) and produce
filtered subsets with strong statistical power. PHASE2C_8.1's
eval_2020_v1 + eval_2021_v1 expected trade-count distributions
(per §3.3 S4 baseline calibration scoring) similarly exceed 20-trade
threshold; expected per-regime filtered subset cardinalities are in
the 150-180 range across all 4 regimes (subject to regime-specific
trade-count distribution).

### 5.4 Filtered vs unfiltered artifact paths

Per-regime artifact paths produce both filtered and unfiltered
output per §3.4 PHASE2C_7.1 audit_2024_v1 pattern:

- `holdout_results.csv` (unfiltered): per-candidate per-regime
  metrics for all 198 candidates including those with trade-count
  below 20 threshold
- `holdout_results_filtered.csv` (filtered): per-candidate per-regime
  metrics for the trade-count-filtered subset (>= 20 trades) only

The filtered subset feeds primary-cohort statistical-significance
analysis at §8 Step 4; the unfiltered subset feeds audit-completeness
analysis (preserves the full 198-candidate evaluation evidence for
audit-only cohort + low-trade-count cohort tracking).

PHASE2C_7.1 audit_2024_v1_filtered subdirectory pattern is preserved
at `data/phase2c_evaluation_gate/audit_2024_v1_filtered/` for
validation_2024 inherited regime; PHASE2C_8.1's eval_2020_v1 +
eval_2021_v1 follow the same pattern with `_filtered` subdirectory or
filename suffix per §6 producer artifact specification.

### 5.5 Forward references

§5's trade-count filter output feeds three downstream sections:

- **§6 producer artifact specification**: §6 specifies the producer
  script that emits both filtered and unfiltered per-regime artifacts;
  consumes §5 filter rule
- **§8 Step 4 multi-regime comparison matrix**: §8 Step 4 consumes
  filtered subsets per regime for primary-cohort cross-regime intersection
  analysis; consumes unfiltered subsets for audit-completeness reporting
- **§9 pass/fail criteria**: §9 references §5's filter as the
  primary-cohort statistical-significance building block; §9 specifies
  higher-order pass/fail criteria over the cross-regime filtered
  evidence

§5 is a carry-forward section; substantive content matches
PHASE2C_7.1 plan §5 modulo per-regime application semantics.

---


---


## 6. Producer artifact specification

PHASE2C_8.1's producer module emits per-regime evaluation artifacts
for the n=4 baseline composition (eval_2020_v1 + eval_2021_v1 novel;
bear_2022 + validation_2024 inherited). The producer extends
PHASE2C_7.1 plan §6's single-additional-regime producer to multi-
regime per-regime emission with mixed-discriminator metadata
reconciliation.

§6 specifies the producer module's responsibilities, per-regime
artifact directory structure, inherited-run re-use protocol,
filtered + unfiltered artifact paths, comparison-matrix input
contract, and runtime guards against scope-violation operations.

### 6.1 Producer module overview

PHASE2C_8.1's producer module is a Python script consuming:

- §3.4 per-regime config (eval_2020_v1 + eval_2021_v1 calendar
  windows + macro characterization + schema discriminator + arc-of-
  origin)
- §4 evaluation gate (4-criterion AND-gate; per-regime application)
- §5 trade-count filter (>= 20 trade-count threshold; per-regime
  application; filtered + unfiltered paths)
- PHASE2C_6 198-candidate population (canonical hash-list source at
  `data/phase2c_evaluation_gate/audit_v1/holdout_results.csv`)
- Corrected-engine artifacts (lineage tag wf-corrected-v1; engine
  commit eb1c87f; `check_evaluation_semantics_or_raise()` guard
  available at [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py))

The producer emits per-regime artifacts for eval_2020_v1 and
eval_2021_v1 only. PHASE2C_7.1-inherited regimes (bear_2022 +
validation_2024) are re-used at their existing artifact paths
without regeneration per Option A engine-version invariance.

The producer's per-regime evaluation pass operates as: (1) load
198 candidates from PHASE2C_6 canonical hash list; (2) for each
candidate × each novel regime (eval_2020_v1 + eval_2021_v1), execute
single-run holdout evaluation against the regime calendar window
under the corrected-engine artifacts; (3) compute the 4-criterion
AND-gate metrics + AND-gate pass/fail outcome per candidate per
regime; (4) emit per-regime artifacts (filtered + unfiltered CSV +
summary JSON + lineage attestation JSON) to the canonical paths.

### 6.2 Per-regime directory structure

PHASE2C_8.1 per-regime artifact directories follow PHASE2C_7.1
audit_2024_v1 pattern preservation:

```
data/phase2c_evaluation_gate/
├── audit_v1/                            # PHASE2C_6 (bear_2022 evaluation; inherited)
│   ├── holdout_results.csv
│   └── holdout_summary.json
├── audit_2024_v1/                       # PHASE2C_7.1 (validation_2024 evaluation; inherited)
│   ├── holdout_results.csv
│   └── holdout_summary.json
├── audit_2024_v1_filtered/              # PHASE2C_7.1 filtered subset (inherited)
│   └── holdout_results_filtered.csv
├── eval_2020_v1/                        # PHASE2C_8.1 novel (eval_2020_v1)
│   ├── holdout_results.csv
│   ├── holdout_summary.json
│   └── lineage_attestation.json
├── eval_2020_v1_filtered/               # PHASE2C_8.1 novel filtered subset
│   └── holdout_results_filtered.csv
├── eval_2021_v1/                        # PHASE2C_8.1 novel (eval_2021_v1)
│   ├── holdout_results.csv
│   ├── holdout_summary.json
│   └── lineage_attestation.json
├── eval_2021_v1_filtered/               # PHASE2C_8.1 novel filtered subset
│   └── holdout_results_filtered.csv
└── comparison_2022_2024_2020_2021_v1/   # PHASE2C_8.1 multi-regime comparison matrix
    ├── comparison_matrix.csv
    └── comparison_summary.json
```

Per-regime canonical filename convention (inherited from PHASE2C_7.1):

- `holdout_results.csv`: per-candidate per-regime metrics +
  per-candidate per-regime AND-gate pass/fail outcome (unfiltered;
  all 198 candidates included regardless of trade count)
- `holdout_summary.json`: aggregate per-regime pass-counts by cohort
  (primary n=44 / audit-only n=154); 4-criterion AND-gate pass count;
  trade-count filtered subset cardinality
- `holdout_results_filtered.csv` (in `_filtered` subdirectory):
  per-candidate per-regime metrics for the trade-count-filtered
  subset (>= 20 trades per regime)
- `lineage_attestation.json`: engine version + commit + lineage tag +
  schema_discriminator + arc_of_origin + producer-module commit +
  corrected-lineage attestation guard signature

Filtered subdirectory pattern (eval_2020_v1_filtered/) is preserved
per PHASE2C_7.1 audit_2024_v1_filtered/ precedent (per Q-D23
deferred to §6 resolution).

### 6.3 Inherited-runs re-use protocol

PHASE2C_7.1-inherited regimes (bear_2022 + validation_2024) are
re-used at their existing artifact paths without regeneration per
Option A engine-version invariance:

- `data/phase2c_evaluation_gate/audit_v1/holdout_results.csv`
  (PHASE2C_6 / PHASE2C_7.1 carry-forward; bear_2022 evaluation)
- `data/phase2c_evaluation_gate/audit_2024_v1/holdout_results.csv`
  (PHASE2C_7.1; validation_2024 evaluation)
- `data/phase2c_evaluation_gate/audit_2024_v1_filtered/holdout_results_filtered.csv`
  (PHASE2C_7.1; validation_2024 filtered subset)

The re-use protocol:

1. **Read existing artifacts** from canonical paths above; do not
   regenerate
2. **Validate engine-version consistency** at producer-module runtime
   via `check_evaluation_semantics_or_raise()` guard against the
   inherited artifacts' lineage_attestation.json (where present;
   PHASE2C_6 + PHASE2C_7.1 attestation files at the corresponding
   paths). The validation confirms wf-corrected-v1 lineage tag
   carry-forward
3. **Reject re-use on engine-version mismatch**: if any inherited
   artifact's lineage_attestation indicates engine version different
   from PHASE2C_8.1's runtime engine, the producer module raises
   `EngineVersionMismatchError` and halts. Re-evaluation under the
   new engine version is required before continuing
4. **Stage inherited metrics as comparison-matrix inputs**: the
   inherited per-regime metrics feed §8 Step 4 multi-regime
   comparison matrix consumer logic without separate re-evaluation

The re-use protocol preserves Option A invariance. Engine-version
drift (e.g., a corrected-WF-engine bug fix lands during PHASE2C_8.1
execution) triggers re-evaluation discipline; existing inherited
runs remain valid only under the same engine version.

### 6.4 Filtered + unfiltered artifact emission

Per-regime artifact emission produces both filtered and unfiltered
outputs per §5.4:

- **Unfiltered (`holdout_results.csv`)**: per-candidate per-regime
  metrics for all 198 candidates regardless of trade-count
- **Filtered (`holdout_results_filtered.csv` in `_filtered/`
  subdirectory)**: per-candidate per-regime metrics for candidates
  passing trade-count filter (>= 20 trades per regime)

Per-regime filter application semantics (per §5.3):

- Filter is applied per-regime; a candidate may pass filter in one
  regime but fail in another
- Per-regime filter outcome is captured in the unfiltered CSV's
  metadata (boolean `trade_count_filter_passed_<regime>` column for
  each regime evaluated)
- Filtered subset cardinality varies across regimes; per-regime
  filtered subset feeds primary-cohort statistical-significance
  analysis at §8 Step 4

### 6.5 Per-run metadata (mixed-discriminator reconciliation)

Per-run lineage_attestation.json captures mixed-discriminator
metadata per §3.4.4 cross-arc inheritance + Option A engine-version
invariance:

```json
{
  "regime": "eval_2020_v1",
  "schema_discriminator": "phase2c_8_1",
  "arc_of_origin": "PHASE2C_8.1",
  "lineage_tag": "wf-corrected-v1",
  "engine_commit": "eb1c87f",
  "producer_module_commit": "<runtime-resolved>",
  "corrected_lineage_attestation_guard_signature": "<runtime-computed>",
  "calendar_window": {
    "start": "2020-01-01T00:00:00Z",
    "end": "2020-12-31T23:00:00Z"
  },
  "candidate_count": 198,
  "primary_cohort_count": 44,
  "audit_only_cohort_count": 154,
  "trade_count_filter_threshold": 20,
  "and_gate_thresholds": {
    "sharpe": -0.5,
    "max_drawdown": 0.25,
    "total_return": -0.15,
    "total_trades": 5
  }
}
```

Mixed-discriminator metadata reconciliation rule:

- **Novel regimes (eval_2020_v1 + eval_2021_v1)**: schema_discriminator
  = `phase2c_8_1`; arc_of_origin = `PHASE2C_8.1`
- **Inherited regimes (bear_2022 + validation_2024)**: schema_discriminator
  = `phase2c_7_1`; arc_of_origin = `PHASE2C_7.1` (carried forward
  from existing artifact metadata)
- **Lineage tag**: `wf-corrected-v1` invariant across all 4 regimes
  (engine-version invariance load-bearing for cross-arc evidentiary
  equivalence)

The §8 Step 4 multi-regime comparison matrix consumer logic operates
on metric values agnostic to schema discriminator; comparison logic
does not branch on discriminator value. Per-run metadata enables
provenance auditing without affecting comparison semantics.

### 6.6 Comparison-matrix input contract

§8 Step 4 multi-regime comparison matrix consumer interface specifies
the input contract:

- **Input data sources** (4 per-regime artifacts):
  1. `data/phase2c_evaluation_gate/audit_v1/holdout_results.csv`
     (bear_2022 inherited; phase2c_7_1 discriminator)
  2. `data/phase2c_evaluation_gate/audit_2024_v1/holdout_results.csv`
     (validation_2024 inherited; phase2c_7_1 discriminator)
  3. `data/phase2c_evaluation_gate/eval_2020_v1/holdout_results.csv`
     (eval_2020_v1 novel; phase2c_8_1 discriminator)
  4. `data/phase2c_evaluation_gate/eval_2021_v1/holdout_results.csv`
     (eval_2021_v1 novel; phase2c_8_1 discriminator)
- **Filtered input contract** (4 per-regime filtered artifacts):
  parallel paths in `_filtered/` subdirectories (where present;
  PHASE2C_6 audit_v1 may not have separate filtered subdirectory
  per PHASE2C_6 artifact precedent — check at runtime + degrade
  gracefully if filtered file absent)
- **Per-candidate identity preservation**: hypothesis_hash column
  is the canonical identifier across all 4 regime CSVs; cross-regime
  intersection at §8 Step 4 operates on hypothesis_hash join
- **Cohort-aligned comparison**: primary (n=44) / audit-only (n=154)
  partition is preserved per §2 universe partition; cross-regime
  comparison can stratify by cohort

Output contract (§8 Step 4 produces):

- `comparison_matrix.csv`: per-candidate × 4-regime AND-gate pass/fail
  matrix; cohort flag per candidate; cross-regime intersection
  pass-flag (passes all 4); cross-regime pass-rate per cohort
- `comparison_summary.json`: aggregate cross-regime statistics +
  cohort-stratified pass rates + cross-regime intersection cardinality

### 6.7 Hard guards (runtime-enforced)

The producer module enforces three hard guards at runtime:

**Guard 1 — No config mutation**:
[`config/environments.yaml`](../../config/environments.yaml) is
read-only at producer module runtime. The producer reads existing
config blocks (eval_2020_v1 + eval_2021_v1 if pre-added; bear_2022
+ validation_2024 inherited) and rejects any operation that would
modify the config file. The CLAUDE.md hard rule on date split
immutability is enforced at producer module level via filesystem
permission check + YAML structural diff comparison against last-
known-good baseline.

**Guard 2 — No 2025 touch**:
The producer module's regime-window evaluation is bounded by V1
veto check at runtime. Any attempt to evaluate against a regime
window overlapping the 2025 test split boundary (per
`config/environments.yaml` v2.test) raises `TestSplitTouchError`
and halts. The guard preserves CLAUDE.md hard rule "Test data is
touched ONCE for final evaluation."

**Guard 3 — Engine-version invariance**:
Producer module runtime engine version is verified against the
inherited artifacts' lineage_attestation per §6.3 re-use protocol.
Engine-version mismatch raises `EngineVersionMismatchError` and
halts. The guard preserves Option A engine-version invariance
load-bearing assumption.

The three guards collectively enforce the spec's structural
constraints at runtime; misconfiguration or scope-creep operations
are rejected before producing artifacts.

### 6.8 Forward references

§6's producer artifact specification feeds three downstream sections:

- **§7 lineage attestation**: §7 specifies the attestation discipline
  for lineage_attestation.json content; §6 references the file
  structure operationally
- **§8 Step 2 (full evaluation across additional regimes)**: §8
  Step 2 invokes the producer module operationally to emit per-regime
  artifacts for eval_2020_v1 + eval_2021_v1
- **§8 Step 4 (multi-regime comparison matrix)**: §8 Step 4 consumes
  §6.6 comparison-matrix input contract; produces the comparison
  matrix output

§6 is the spec arc's first novel-multi-regime extension section.
The producer artifact specification operationalizes §3.4 per-regime
config + §4 + §5 carry-forward criteria + Option A engine-version
invariance + mixed-discriminator metadata reconciliation into a
runnable producer module specification.

---


---


## 7. Lineage attestation

PHASE2C_8.1's lineage attestation captures four load-bearing
properties of the multi-regime evaluation: (1) engine-version
invariance preserves Option A re-use validity; (2) inherited-run
re-use validation is enforced at producer-module runtime; (3) mixed
schema discriminator chain documents arc-of-origin without affecting
comparison logic; (4) in-sample evaluation caveat (Concern A) is
preserved as methodology-evidence hierarchy property of the n=4
baseline.

§7 specifies the attestation discipline at spec level; §6.7 Guard 3
enforces the runtime invariance check. The two-layer structure (spec
attestation + runtime guard) preserves the conditional-claim
discipline: invariance is asserted at spec level + verified at
runtime; drift detection triggers re-evaluation requirement.

### 7.1 Engine-version invariance attestation (Option A)

PHASE2C_8.1's multi-regime baseline composition includes two
PHASE2C_7.1-inherited regimes (bear_2022 + validation_2024) re-used
without regeneration per Option A. The re-use validity rests on
engine-version invariance — both arcs run under the corrected WF
engine at lineage tag wf-corrected-v1 (commit eb1c87f). PHASE2C_8.1's
producer module operates under the same engine version; existing
inherited runs are evidentiary-equivalent to runs produced fresh
under PHASE2C_8.1.

Engine-version invariance attestation:

- **Lineage tag**: `wf-corrected-v1` (sealed at PHASE2C_7.1 closeout
  per CLAUDE.md Phase Marker corrected lineage entry)
- **Engine commit**: `eb1c87f` (corrected WF engine fix per
  PHASE2C_5 erratum + Corrected WF Engine Project Arc closeout at
  [`docs/closeout/CORRECTED_WF_ENGINE_SIGNOFF.md`](../closeout/CORRECTED_WF_ENGINE_SIGNOFF.md))
- **Attestation guard**:
  [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py)
  `check_evaluation_semantics_or_raise()` validates single-run
  holdout artifacts against `single_run_holdout_v1` attestation
  domain; applied to all PHASE2C_8.1 single-run holdout artifacts
- **Runtime enforcement**: §6.7 Guard 3 raises
  `EngineVersionInvarianceError` on engine-version mismatch detected
  at producer-module runtime against inherited artifacts'
  lineage_attestation

Conditional-claim discipline preserved: Option A re-use validity is
conditional on engine-version invariance; engine-version drift during
PHASE2C_8.1 execution invalidates Option A; re-evaluation under the
new engine version becomes required. The two-layer structure (spec
attestation at §7.1 + runtime guard at §6.7 Guard 3) operationalizes
the conditional bound — invariance is enforced at runtime; drift
detection triggers re-evaluation requirement; Option A is not a
static assertion but a conditional claim with explicit
falsifiability.

If engine-version drift is detected at runtime:

- §6.7 Guard 3 raises EngineVersionInvarianceError; producer module
  halts
- Inherited artifacts (bear_2022 + validation_2024 at
  `data/phase2c_evaluation_gate/{audit_v1, audit_2024_v1,
  audit_2024_v1_filtered}/`) are no longer evidentiary-equivalent
  to runs produced under the new engine version
- Option A re-use is invalidated; PHASE2C_8.1's n=4 baseline
  composition requires re-evaluation of inherited regimes under
  the new engine version before continuing
- Re-evaluation produces new artifact paths (with versioning suffix
  to distinguish from existing _v1 paths) + advances lineage tag
  to wf-corrected-v2 or successor

### 7.2 Inherited-run re-use validation

Inherited-run re-use validation is enforced at producer-module
runtime via §6.3 4-step re-use protocol. §7.2 captures the
validation discipline at spec attestation level:

- **Step 1 (read existing artifacts)**: Producer module reads from
  canonical inherited paths
  (`data/phase2c_evaluation_gate/{audit_v1, audit_2024_v1,
  audit_2024_v1_filtered}/`) without regeneration
- **Step 2 (validate engine-version consistency)**: Producer module
  invokes `check_evaluation_semantics_or_raise()` guard against
  inherited artifacts' lineage_attestation (where present); the
  guard validates wf-corrected-v1 lineage tag carry-forward
- **Step 3 (reject re-use on mismatch)**: Engine-version mismatch
  raises `EngineVersionInvarianceError` per §6.7 Guard 3;
  PHASE2C_8.1 execution halts before consuming inherited artifacts
- **Step 4 (stage inherited metrics as comparison-matrix inputs)**:
  Validated inherited artifacts are staged for §8 Step 4 multi-
  regime comparison matrix consumer logic

Validation discipline preserves Option A invariance:
- Inherited artifacts are validated before consumption (not retroactively)
- Mismatch detection halts PHASE2C_8.1 execution before producing
  invalid downstream comparison matrix
- Validation discipline is uniform across both inherited regimes
  (bear_2022 + validation_2024); no per-regime exception

The validation discipline is structurally distinct from re-evaluation
— validation confirms invariance at point-of-use; re-evaluation
produces new artifacts under new engine version. PHASE2C_8.1
defaults to validation-then-consume; re-evaluation is required only
on validation failure.

### 7.3 Mixed-discriminator schema chain documentation

PHASE2C_8.1's n=4 baseline composition carries mixed schema
discriminators per §3.4.4 + §6.5 reconciliation rule:

- **Inherited regimes**:
  - bear_2022: `phase2c_7_1` discriminator; `arc_of_origin = PHASE2C_7.1`
  - validation_2024: `phase2c_7_1` discriminator; `arc_of_origin = PHASE2C_7.1`
- **Novel regimes**:
  - eval_2020_v1: `phase2c_8_1` discriminator; `arc_of_origin = PHASE2C_8.1`
  - eval_2021_v1: `phase2c_8_1` discriminator; `arc_of_origin = PHASE2C_8.1`

Schema discriminator chain documentation:

- **Chain progression**: PHASE2C_6 evaluation gate → PHASE2C_7.1
  multi-regime evaluation gate → PHASE2C_8.1 multi-regime evaluation
  gate. Each arc advances the discriminator (`phase2c_6` →
  `phase2c_7_1` → `phase2c_8_1`) at producer-module commit.
  PHASE2C_8.1 introduces `phase2c_8_1` discriminator for novel
  regimes; inherited regimes retain their origin discriminator.
- **Per-arc origin documentation**: lineage_attestation.json captures
  schema_discriminator + arc_of_origin (per §6.5 schema example).
  The two fields are operationally redundant for novel regimes
  (PHASE2C_8.1 → phase2c_8_1) but distinct semantics (discriminator
  versions schema; arc-of-origin attributes evaluation execution).
- **Cross-arc reconciliation rule**: §8 Step 4 multi-regime comparison
  matrix consumer logic operates on metric values agnostic to schema
  discriminator. Comparison logic does not branch on discriminator
  value; per-run metadata enables provenance auditing without
  affecting comparison semantics. Reconciliation rule is metadata-
  only (per §6.5).

The schema discriminator chain documents arc-of-origin progression
at attestation level; metadata reconciliation operates at producer-
module level. The two layers preserve provenance auditability
without coupling comparison semantics to discriminator values.

Schema discriminator advancement is bounded: PHASE2C_8.1 advances
the chain to `phase2c_8_1`. Future arc advancement is a separate
decision; PHASE2C_8.1 does not pre-name successor discriminators
(Q-FS4 strictness per §10 anti-pre-naming discipline).

### 7.4 In-sample evaluation caveat (Concern A)

PHASE2C_8.1's selected additional regimes (eval_2020_v1 +
eval_2021_v1) overlap the v2 split version's train calendar period
(train = 2020-2021 + 2023 per
[`config/environments.yaml`](../../config/environments.yaml)). The
198-candidate population's PHASE2C_5 walk-forward training process
used sub-windows of these calendar periods. Evaluating PHASE2C_8.1's
4-regime comparison matrix against eval_2020_v1 + eval_2021_v1
introduces in-sample evaluation overlap.

In-sample evaluation caveat (Concern A; carry-forward from §3.3
selection rationale):

- **Concern phrasing**: 2020/2021 overlap the original train-window
  context; mitigated by walk-forward sub-window discipline, but not
  equivalent to untouched validation/test evidence.
- **Mechanism**: PHASE2C_5 training process used sub-windows of
  2020 and 2021 historical data; PHASE2C_6's 198-candidate population
  may carry candidate-screening overfitting against these regimes.
  Cross-regime patterns observed in 2020/2021 may reflect candidate-
  screening artifacts rather than mechanism-relevant structure.
- **Mitigation status**: Partial. Walk-forward sub-window discipline
  operates within each candidate's training process — training
  windows are sub-windows of the calendar year, not the full year;
  walk-forward cross-validation operates within-regime. The
  mitigation is not zero, but not equivalent to fully-untouched
  evidence (such as bear_2022 holdout or validation_2024).
- **Methodology-evidence hierarchy**: The in-sample caveat is
  intrinsic to the candidate-regime selection scope (per §3.3
  selection rationale + §3.1 S3 = MED rationale); it is captured
  at framework level via S3 = MED scoring + spec-level attestation
  at §7.4. The caveat is structural, not a defect.

Comparison register (per §3.3.4 in-sample caveat):

- **Inherited regimes (fully untouched evidence)**: bear_2022 was
  the v2.regime_holdout split (designed for holdout evaluation);
  validation_2024 was the v2.validation split (untouched during
  PHASE2C_5 training). These regimes provide fully out-of-sample
  evidence relative to the 198-candidate population.
- **Novel regimes (train-overlap evaluation)**: eval_2020_v1 +
  eval_2021_v1 overlap the v2 train split; partial mitigation via
  walk-forward sub-windows.

§8 Step 4 multi-regime comparison matrix should distinguish these
two evidentiary categories operationally — fully-out-of-sample
baseline (bear_2022 + validation_2024) vs train-overlap evaluation
(eval_2020_v1 + eval_2021_v1). §9 pass/fail criteria should not
equate the two evidentiary categories. §10 risk #6 expands the
caveat operationally with explicit risk treatment.

The Concern A caveat preserves PHASE2C_8.1's evidentiary integrity:
findings derived from 4-regime evaluation are interpreted with the
in-sample caveat applied to 2020/2021 evidence; cross-regime patterns
are evaluated against the methodology-evidence hierarchy distinction.

### 7.5 Lineage attestation file content

Per-regime lineage_attestation.json files at canonical paths
(`data/phase2c_evaluation_gate/{regime}_v1/lineage_attestation.json`)
capture the full attestation register per §6.5 schema example. §7.5
specifies the attestation file's load-bearing fields:

- `schema_discriminator`: phase2c_7_1 (inherited) or phase2c_8_1
  (novel) per §7.3
- `arc_of_origin`: PHASE2C_7.1 (inherited) or PHASE2C_8.1 (novel)
  per §7.3
- `lineage_tag`: `wf-corrected-v1` (invariant across all 4 regimes)
  per §7.1
- `engine_commit`: `eb1c87f` (invariant) per §7.1
- `producer_module_commit`: <runtime-resolved git SHA at producer-
  module invocation>
- `corrected_lineage_attestation_guard_signature`: <runtime-computed
  signature from `check_evaluation_semantics_or_raise()` validation>
- `calendar_window`: per-regime calendar boundaries per §3.4
- `candidate_count`: 198 (invariant across all 4 regimes; preserves
  cross-regime cohort alignment)
- `primary_cohort_count`: 44 (invariant per §2 universe partition)
- `audit_only_cohort_count`: 154 (invariant per §2 universe
  partition)
- `trade_count_filter_threshold`: 20 (invariant per §5 D1 carry-
  forward)
- `and_gate_thresholds`: per §4 D2 carry-forward (sharpe ≥ −0.5;
  max_drawdown ≤ 0.25; total_return ≥ −0.15; total_trades ≥ 5)
- `in_sample_caveat_applies`: boolean (true for eval_2020_v1 +
  eval_2021_v1; false for bear_2022 + validation_2024)

The `in_sample_caveat_applies` field is PHASE2C_8.1-novel; it
distinguishes train-overlap evaluation regimes from fully-out-of-
sample evaluation regimes at metadata level. §8 Step 4 + §9 + §10
consume the field operationally.

### 7.6 Forward references

§7's lineage attestation feeds three downstream sections:

- **§8 Step 4 multi-regime comparison matrix**: §8 Step 4 consumes
  per-regime lineage_attestation.json metadata to apply the
  in-sample caveat at comparison-matrix construction; differentiates
  fully-out-of-sample evidence (bear_2022 + validation_2024) from
  train-overlap evidence (eval_2020_v1 + eval_2021_v1)
- **§9 pass/fail criteria**: §9 references the in_sample_caveat_applies
  metadata field when specifying pass/fail criteria; criteria do not
  equate the two evidentiary categories
- **§10 risks taxonomy**: §10 risk #6 expands Concern A in-sample
  evaluation overlap with explicit risk treatment; per the §10
  carry-forward register at /tmp/PHASE2C_8_1_section10_carryforward.md
  classification (methodology-evidence hierarchy risk; partial
  mitigation status)

§7 is the second novel-multi-regime extension section. The lineage
attestation discipline operationalizes §6 producer artifact
specification's mixed-discriminator metadata + Option A engine-version
invariance + inherited-run re-use validation + Concern A in-sample
caveat into a coherent attestation register at spec level.

---


---


## 8. Implementation plan

PHASE2C_8.1's implementation plan operationalizes the multi-regime
evaluation gate as a 5-step sequential gating structure. Each step
has explicit completion criteria + handoff to next step; sub-step
gating within Step 1 preserves PHASE2C_8.0 §8 inheritance.

The plan consumes §3 sub-cycle output (regime selection + per-regime
config) + §4 evaluation gate criteria + §5 trade-count filter + §6
producer artifact specification + §7 lineage attestation
collectively. Implementation operates against the locked spec
content; no re-litigation of upstream decisions.

### 8.1 Step 1 — Setup (sub-step gated)

Step 1 is sub-step gated into four sub-steps; each sub-step has
explicit completion criteria + handoff to next sub-step. Step 1
closes when Step 1.4 smoke verification passes; Step 2 cannot begin
until Step 1 closes.

#### Step 1.1 — Regime-source scoping (operationally completed at §3 sub-cycle)

- **Scope**: Identification of candidate additional regimes;
  application of selection criteria; selection adjudication
- **Status**: Operationally completed at §3 sub-cycle (Stage A
  criteria + framework at §3.1 + §3.2; Stage B candidate-regime
  adjudication at §3.3 + §3.4)
- **Output (already produced)**: 2 selected additional regimes
  (eval_2020_v1 + eval_2021_v1) + 1 backup regime (2023) + per-regime
  config specification at §3.4
- **Implementation work required**: None at Step 1.1; the §3
  sub-cycle's Stage A + Stage B output is the canonical Step 1.1
  output
- **Completion criterion**: §3 sub-cycle assembly closed (Stage A +
  Stage B + per-regime config sealed in spec document)
- **Handoff to Step 1.2**: Step 1.2 schema discriminator extension
  consumes §3.4's eval_2020_v1 + eval_2021_v1 per-regime config

#### Step 1.2 — Schema discriminator extension

- **Scope**: Add `phase2c_8_1` schema discriminator to producer-
  module + closeout-document discriminator chain handling
- **Implementation work**: Add `phase2c_8_1` constant to producer
  module's discriminator handling; update closeout-document parser
  to recognize chain progression `phase2c_7_1 → phase2c_8_1`;
  preserve per-arc origin metadata reading
- **Output**: Producer module + closeout parser handle 2-element
  discriminator chain (phase2c_7_1 inherited; phase2c_8_1 novel)
- **Completion criterion**: Unit tests pass for both discriminator
  values + cross-arc reconciliation rule (per §6.5)
- **Handoff to Step 1.3**: Step 1.3 producer flag extension consumes
  the discriminator chain handling for per-regime evaluation flag
  routing

#### Step 1.3 — Producer flag extension

- **Scope**: Extend producer module CLI flag interface to support
  per-regime evaluation invocation
- **Implementation work**: Add `--regime <regime_name>` flag (accepts
  `eval_2020_v1` or `eval_2021_v1`); flag routes producer to the
  per-regime config block at `config/environments.yaml`; flag
  triggers per-regime artifact emission to canonical paths per §6.2;
  flag enforces §6.7 hard guards (no config mutation; no 2025 touch;
  engine-version invariance)
- **Output**: Producer module accepts `--regime eval_2020_v1` and
  `--regime eval_2021_v1` invocations
- **Completion criterion**: Flag-routed invocation against canonical
  hash list at
  `data/phase2c_evaluation_gate/audit_v1/holdout_results.csv`
  produces non-empty per-regime output without raising any hard-
  guard errors
- **Handoff to Step 1.4**: Step 1.4 smoke verification consumes
  the flag-routed producer module

#### Step 1.4 — Smoke verification per regime

- **Scope**: Per-regime smoke verification — 5-candidate subset
  evaluation against each novel regime (eval_2020_v1 + eval_2021_v1)
  to confirm producer-module correctness before full 198-candidate
  evaluation
- **Implementation work**: Select 5 candidates from canonical hash
  list (deterministic — first 5 by hypothesis_hash sort); invoke
  producer with `--regime eval_2020_v1 --candidate-subset <5-hashes>`;
  verify per-regime artifact emission produces well-formed CSV +
  summary JSON + lineage attestation JSON; repeat for `--regime
  eval_2021_v1`
- **Output**: 5-candidate × 2-regime smoke artifact set at
  `data/phase2c_evaluation_gate/{eval_2020_v1, eval_2021_v1}/_smoke/`
  subdirectory (preserves canonical paths from full-evaluation
  contamination)
- **Completion criterion**: Smoke artifacts well-formed per §6.5
  schema; lineage attestation guards pass; manual inspection
  confirms per-candidate metric reasonability (no NaN explosions;
  no zero-trade-count for all 5 candidates)
- **Handoff to Step 2**: Smoke verification passes; Step 2 full
  evaluation can proceed

Step 1 closes when all four sub-steps close. Step 2 cannot begin
until Step 1 closes per sequential gating discipline.

### 8.2 Step 2 — Full 198-candidate evaluation across additional regimes

- **Scope**: Full 198-candidate population evaluation against
  eval_2020_v1 + eval_2021_v1 (novel regimes only; inherited
  bear_2022 + validation_2024 re-used per §7.2 4-step validation
  protocol)
- **Inputs**:
  - 198-candidate population from canonical hash list at
    `data/phase2c_evaluation_gate/audit_v1/holdout_results.csv`
  - Per-regime config (eval_2020_v1 + eval_2021_v1) per §3.4
  - 4-criterion AND-gate per §4
  - Producer module (Step 1.3 + Step 1.4 verified)
- **Implementation work**:
  1. Invoke `producer --regime eval_2020_v1` against full 198-candidate
     population
  2. Invoke `producer --regime eval_2021_v1` against full 198-candidate
     population
  3. Verify §6.7 Guard 3 (engine-version invariance) passes against
     inherited artifacts at runtime
  4. Verify §7.2 4-step inherited-run re-use validation passes for
     bear_2022 + validation_2024 artifacts
- **Outputs**:
  - `data/phase2c_evaluation_gate/eval_2020_v1/holdout_results.csv`
    (198 rows; unfiltered)
  - `data/phase2c_evaluation_gate/eval_2020_v1/holdout_summary.json`
    (per-regime aggregate pass-counts)
  - `data/phase2c_evaluation_gate/eval_2020_v1/lineage_attestation.json`
    (12-field per §7.5)
  - Parallel paths for eval_2021_v1
- **Completion criterion**: Both novel-regime artifact sets emitted;
  per-regime AND-gate pass-count + summary JSON computed correctly;
  lineage attestation files include `in_sample_caveat_applies = true`
  (per §7.4 classification); no hard-guard errors raised
- **Handoff to Step 3**: Step 3 trade-count filtered secondary pass
  consumes Step 2's per-regime unfiltered outputs

### 8.3 Step 3 — Trade-count filtered secondary pass per regime

- **Scope**: Apply `total_trades >= 20` trade-count filter (per §5)
  to Step 2's per-regime unfiltered outputs; emit filtered artifact
  paths
- **Inputs**:
  - Step 2 per-regime unfiltered outputs (`holdout_results.csv` for
    eval_2020_v1 + eval_2021_v1)
  - §5 trade-count filter threshold (20 trades; pre-specified;
    invariant across regimes)
- **Implementation work**:
  1. Read per-regime unfiltered CSV
  2. Apply per-regime filter: candidates where `total_trades >= 20`
     in that regime
  3. Emit filtered subset to `_filtered/` subdirectory
- **Outputs**:
  - `data/phase2c_evaluation_gate/eval_2020_v1_filtered/holdout_results_filtered.csv`
  - `data/phase2c_evaluation_gate/eval_2021_v1_filtered/holdout_results_filtered.csv`
- **Completion criterion**: Filtered artifacts emitted; per-regime
  filtered subset cardinality reported (expected range 150-180 per
  §5.3 baseline calibration); no hard-guard errors raised
- **Handoff to Step 4**: Step 4 multi-regime comparison matrix
  consumes Step 3's filtered subsets + Step 2's unfiltered outputs

### 8.4 Step 4 — Multi-regime comparison matrix at n=4

- **Scope**: Construct multi-regime comparison matrix consuming all
  4 regimes' per-candidate evaluation outputs; produce cross-regime
  intersection analysis + cohort-stratified pass-rate comparison
- **Inputs** (per §6.6 input contract):
  - Inherited regimes: bear_2022 (`audit_v1/holdout_results.csv`) +
    validation_2024 (`audit_2024_v1/holdout_results.csv` +
    `audit_2024_v1_filtered/holdout_results_filtered.csv`)
  - Novel regimes: eval_2020_v1 (Step 2 + Step 3 outputs) +
    eval_2021_v1 (Step 2 + Step 3 outputs)
  - Per-regime lineage_attestation.json metadata (per §7.5; including
    `in_sample_caveat_applies` field per regime)
- **Implementation work**:
  1. Verify §7.2 4-step inherited-run re-use validation against
     bear_2022 + validation_2024 inherited artifacts
  2. Construct per-candidate × 4-regime AND-gate pass/fail matrix
     using hypothesis_hash join across regimes
  3. Compute cross-regime intersection pass-flag per candidate
     (passes all 4 regimes vs subsets)
  4. Stratify by cohort (primary n=44 / audit-only n=154) per §2
     universe partition
  5. Compute per-cohort cross-regime pass-rates
  6. Stratify by `in_sample_caveat_applies` classification
     (fully-out-of-sample baseline {bear_2022, validation_2024} vs
     train-overlap evaluation {eval_2020_v1, eval_2021_v1}) per §7.4
- **Outputs**:
  - `data/phase2c_evaluation_gate/comparison_2022_2024_2020_2021_v1/comparison_matrix.csv`
    (per-candidate × 4-regime matrix; cohort flag; intersection
    pass-flag; in_sample_caveat_applies per regime)
  - `data/phase2c_evaluation_gate/comparison_2022_2024_2020_2021_v1/comparison_summary.json`
    (aggregate cross-regime statistics; cohort-stratified pass-rates;
    cross-regime intersection cardinality; train-overlap vs fully-
    out-of-sample stratification)
- **Completion criterion**: Comparison matrix CSV + summary JSON
  emitted; cross-regime intersection cardinality reported per cohort
  + per evidentiary category (fully-out-of-sample vs train-overlap);
  per-candidate identity preservation verified (198 rows in
  comparison matrix; hypothesis_hash join produces no duplicates or
  missing entries)
- **Handoff to Step 5**: Step 5 closeout drafting consumes Step 4
  comparison matrix + summary as the canonical multi-regime evidence
  base

### 8.5 Step 5 — Closeout drafting + adversarial review + commit

- **Scope**: Draft PHASE2C_8.1 closeout consuming Step 4 comparison
  matrix evidence; run adversarial review (Codex review pattern per
  PHASE2C_7.1 precedent); fold review findings; commit + tag arc
- **Inputs**:
  - Step 4 comparison matrix + summary
  - PHASE2C_8.1 spec document (this document; sealed)
  - PHASE2C_7.1 closeout structure precedent ([`docs/closeout/PHASE2C_7_1_RESULTS.md`](../closeout/PHASE2C_7_1_RESULTS.md))
- **Implementation work**:
  1. Draft closeout sections per PHASE2C_7.1 precedent (§1 verdict
     + §2 input universe + §3 evaluation runs + §4 gate criteria +
     §5 cross-regime findings + §6 cohort analysis + §7 lineage
     attestation + §8 methodology notes + §9 follow-up scoping +
     §10 risks)
  2. Methodology-evidence hierarchy framing per §7.4 in-sample
     caveat: §5 cross-regime findings should distinguish fully-out-
     of-sample evidence from train-overlap evidence operationally
  3. Run dual-AI review cycle on closeout draft (ChatGPT + Claude
     advisor per established discipline)
  4. Run adversarial Codex review on closeout draft per PHASE2C_7.1
     precedent
  5. Fold review findings into closeout
  6. Commit closeout to `docs/closeout/PHASE2C_8_1_RESULTS.md`;
     commit comparison matrix artifacts
  7. Tag arc per cross-arc convention (e.g.,
     `phase2c-8-1-multi-regime-extended-v1`); push commit + tag
- **Outputs**:
  - `docs/closeout/PHASE2C_8_1_RESULTS.md` (closeout document)
  - Comparison matrix artifacts at canonical paths (Step 4 outputs
    committed to repository)
  - Tag `phase2c-8-1-multi-regime-extended-v1` (or equivalent per
    cross-arc convention)
  - CLAUDE.md Phase Marker reconciliation in same arc per
    [`feedback_claude_md_freshness.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md)
    user-memory feedback rule
- **Completion criterion**: Closeout committed + tagged + pushed +
  CLAUDE.md updated; arc closes
- **Handoff**: PHASE2C_8.1 arc closure; future-arc scoping decision
  enabled (post-closeout; not part of PHASE2C_8.1 scope per Q-FS4
  strictness)

### 8.6 Sequential gating discipline

The 5-step structure is sequential — each step's completion
criterion gates the next step's initiation:

- Step 1 (sub-step gated) → Step 2 (full evaluation cannot begin
  until Step 1.4 smoke verification passes)
- Step 2 → Step 3 (filtered secondary pass cannot begin until full
  evaluation completes)
- Step 3 → Step 4 (comparison matrix cannot begin until filtered
  outputs are available)
- Step 4 → Step 5 (closeout drafting cannot begin until comparison
  matrix is available as evidence base)

Sub-step gating within Step 1:
- Step 1.1 (already complete at §3 sub-cycle) → Step 1.2 → Step 1.3 →
  Step 1.4

The sequential gating discipline preserves PHASE2C_8.0 §8 inheritance
+ enables roll-back at sub-step granularity if any sub-step fails
to complete (e.g., Step 1.4 smoke verification fails → roll back to
Step 1.3 producer-flag extension; revise; re-attempt Step 1.4).

### 8.7 Forward references

§8's implementation plan feeds two downstream sections:

- **§9 pass/fail criteria**: §9 specifies higher-order pass/fail
  criteria over §8 implementation plan completion (regime-source
  selection adjudicated; cross-arc inheritance reconciled; in-sample
  caveat preserved; mixed-discriminator metadata reconciled;
  comparison matrix completeness; closeout completeness)
- **§10 risks taxonomy**: §10 specifies risks operating against §8
  implementation plan execution (regime-source-selection failure;
  multi-regime infrastructure complexity; cross-regime intersection
  sparsity; closeout drafting scope expansion; regime-selection
  becoming post-hoc narrative fitting; Concern A in-sample evaluation
  overlap)

§8 is the spec arc's largest section because it integrates upstream
content into a runnable implementation sequence. The integration is
mechanical-codification at established register; substantive content
is pre-resolved at §3-§7.

---


---


## 9. Pass/fail criteria

PHASE2C_8.1's pass/fail criteria operationalize the §8 implementation
plan's completion criteria as a structured checklist for closeout-
time verification. Criteria are organized into two categories: **pass
criteria** (empirical fact verifiable at closeout time) and
**documentation criteria** (artifact existence verifiable at closeout
commit time). Both criteria types must satisfy for arc closure;
neither category subsumes the other.

§9 inherits PHASE2C_7.1 plan §9 substantively + extends with multi-
regime application semantics + post-codification METHODOLOGY_NOTES
discipline application criteria.

### 9.1 Pass criteria (empirical fact verifiable at closeout time)

#### P1 — Engine-version invariance attested

- **Criterion**: §6.7 Guard 3 raised no `EngineVersionInvarianceError`
  during PHASE2C_8.1 producer module execution; inherited PHASE2C_7.1
  artifacts at `data/phase2c_evaluation_gate/{audit_v1, audit_2024_v1,
  audit_2024_v1_filtered}/` validated against wf-corrected-v1 lineage
  tag at runtime per §7.2 4-step protocol
- **Verification method**: Producer module execution log review;
  lineage_attestation.json files at canonical paths confirm
  engine_commit = eb1c87f + lineage_tag = wf-corrected-v1 across all
  4 regimes
- **Failure mode**: Engine-version drift detected at runtime →
  re-evaluation under new engine version required → PHASE2C_8.1 arc
  closure deferred until re-evaluation completes

#### P2 — All n=4 regime evaluations complete

- **Criterion**: 4 per-regime artifact sets emitted at canonical paths:
  - eval_2020_v1 + eval_2020_v1_filtered (PHASE2C_8.1 novel)
  - eval_2021_v1 + eval_2021_v1_filtered (PHASE2C_8.1 novel)
  - audit_v1 (PHASE2C_6 / PHASE2C_7.1 inherited; bear_2022)
  - audit_2024_v1 + audit_2024_v1_filtered (PHASE2C_7.1 inherited;
    validation_2024)
- **Verification method**: Filesystem inventory; per-regime artifact
  set has holdout_results.csv + holdout_summary.json + (where novel)
  lineage_attestation.json
- **Failure mode**: Missing artifact at canonical path → producer
  module re-invocation required → arc closure deferred until artifact
  set complete

#### P3 — 198-candidate identity preserved across all regimes

- **Criterion**: hypothesis_hash join across all 4 per-regime
  unfiltered CSVs produces 198 rows × 4 regimes = 792 per-candidate
  per-regime entries with no duplicates or missing entries; primary
  cohort n=44 + audit-only cohort n=154 partition preserved per §2
- **Verification method**: Comparison matrix construction at §8 Step
  4; cardinality check at output: comparison_matrix.csv has 198 rows;
  cohort flag distribution = {primary: 44, audit-only: 154}
- **Failure mode**: Identity loss → §8 Step 4 fails completion
  criterion → roll-back to Step 2 + Step 3 with diagnosis

#### P4 — Cross-regime comparison matrix produced

- **Criterion**: comparison_matrix.csv + comparison_summary.json
  emitted at
  `data/phase2c_evaluation_gate/comparison_2022_2024_2020_2021_v1/`;
  cross-regime intersection cardinality reported per cohort + per
  evidentiary category (fully-out-of-sample {bear_2022,
  validation_2024} vs train-overlap {eval_2020_v1, eval_2021_v1}
  per §7.4 in-sample caveat classification)
- **Verification method**: Comparison artifact files exist at
  canonical paths; cardinality reports include 4-way stratification
  (cohort × in_sample_caveat_applies)
- **Failure mode**: Comparison matrix construction fails → §8 Step 4
  fails completion criterion → diagnosis at Step 4 inputs (Step 2 +
  Step 3 outputs validated)

#### P5 — In-sample caveat classification preserved

- **Criterion**: Per-regime lineage_attestation.json files include
  `in_sample_caveat_applies` boolean field per §7.5 12-field
  specification; eval_2020_v1 + eval_2021_v1 = true; bear_2022 +
  validation_2024 = false
- **Verification method**: lineage_attestation.json files inspected
  at canonical paths; field value matches §7.4 classification
- **Failure mode**: Field missing or value incorrect → §7.5 schema
  validation fails → producer module fix required

#### P6 — Regime-source selection adjudicated and documented

- **Criterion**: §3.3 Stage B candidate-regime adjudication produced
  defensible top-2 selection with auditable per-criterion scoring
  + non-selected backup rationale + conditional-shift falsifiability
  discipline; §3.4 per-regime config specification operational
- **Verification method**: Spec document §3 sub-cycle assembly
  closed; §3.3 V1/S1-S5 table + aggregate scores + selection rationale
  + non-selected rationale present; §3.4 per-regime config (eval_2020_v1
  + eval_2021_v1) named with calendar windows + data sources +
  schema discriminator
- **Failure mode**: Selection adjudication incomplete → §3 sub-cycle
  re-engagement required

#### P7 — Mixed-discriminator metadata reconciliation operational

- **Criterion**: Per-run metadata captures schema_discriminator
  (phase2c_7_1 for inherited; phase2c_8_1 for novel) + arc_of_origin
  (PHASE2C_7.1 vs PHASE2C_8.1) + lineage_tag (wf-corrected-v1
  invariant); §8 Step 4 comparison logic operates agnostic to
  schema discriminator per §6.5 reconciliation rule
- **Verification method**: lineage_attestation.json files inspected
  + comparison matrix construction confirmed agnostic to discriminator
  (no branching on discriminator value in §8 Step 4 implementation)
- **Failure mode**: Discriminator branching detected in comparison
  logic → §6.5 reconciliation rule violation → §8 Step 4 implementation
  fix required

### 9.2 Documentation criteria (artifact existence verifiable at closeout commit time)

#### D1 — Spec document committed

- **Criterion**: `docs/phase2c/PHASE2C_8_1_PLAN.md` (this document)
  committed to repository main branch
- **Verification method**: `git log` shows commit landing the spec
  document on main

#### D2 — Closeout document committed

- **Criterion**: `docs/closeout/PHASE2C_8_1_RESULTS.md` committed
  with full evidentiary content (per §8 Step 5)
- **Verification method**: `git log` shows closeout commit; closeout
  contains §1-§N structure inheriting from PHASE2C_7.1 closeout
  precedent

#### D3 — Comparison matrix artifacts committed

- **Criterion**: comparison_matrix.csv + comparison_summary.json at
  `data/phase2c_evaluation_gate/comparison_2022_2024_2020_2021_v1/`
  committed to repository
- **Verification method**: Filesystem inventory; `git log` shows
  artifact paths in commit

#### D4 — Per-regime artifact paths committed

- **Criterion**: Novel-regime per-regime artifacts (eval_2020_v1 +
  eval_2021_v1 + their _filtered/ subdirectories) committed
- **Verification method**: Filesystem inventory; `git log` shows
  artifact paths

#### D5 — Tag applied

- **Criterion**: Tag `phase2c-8-1-multi-regime-extended-v1` (or
  equivalent per Q-D33 naming) applied to closeout commit + pushed
  to origin
- **Verification method**: `git tag --list` includes the tag; remote
  origin reflects the tag

#### D6 — CLAUDE.md Phase Marker reconciled

- **Criterion**: CLAUDE.md Phase Marker section updated in same arc
  per `feedback_claude_md_freshness.md` user-memory rule; current
  phase + completed list + current batch_id + active blueprint
  fields reflect PHASE2C_8.1 closure
- **Verification method**: `git log` for CLAUDE.md shows update
  landing in arc closure commit; Phase Marker text inspection
  confirms reconciliation

#### D7 — Adversarial review run + findings folded

- **Criterion**: Adversarial Codex review run on closeout per
  PHASE2C_7.1 precedent; review findings folded into closeout (or
  documented as carry-forward register if non-blocking); review-run
  identifier (e.g., Codex review ID) referenced in closeout
- **Verification method**: Closeout cites Codex review ID; review
  findings either folded operationally (verbatim or re-framed) or
  documented as deferred items

### 9.3 Failure modes and roll-back

Failure on any P1-P7 pass criterion or D1-D7 documentation criterion
defers arc closure until criterion satisfies. Roll-back semantics
per §8.6 sequential gating discipline:

- Pass criterion failure at P1 (engine-version invariance) → §8 Step
  1.4 + Step 2 + Step 4 roll-back; re-evaluation under new engine
  version required
- Pass criterion failure at P2-P7 → §8 corresponding step roll-back
  + diagnosis; specific failure determines roll-back depth (sub-step
  vs full step)
- Documentation criterion failure → closeout-stage fix required;
  no §8 implementation roll-back

### 9.4 Forward-pointer to PHASE2C_8.1 closeout drafting cycle

§9 pass/fail criteria operationalize the closeout-time verification
checklist. PHASE2C_8.1 closeout drafting (§8 Step 5) consumes the
§9 checklist as the closeout-completion verification framework.
The full METHODOLOGY_NOTES post-codification discipline applies at
closeout drafting register per the lifecycle-stage trigger
(PHASE2C_8.1 closeout is the first high-load closeout under the
post-codification discipline).

§9 is structurally distinct from §10:
- §9 pass/fail criteria are completion checks (binary; criterion
  satisfies or doesn't)
- §10 risks taxonomy is risk surface enumeration (continuous;
  risks may materialize partially)

---

## 10. Risks taxonomy

PHASE2C_8.1's risks taxonomy enumerates six risks operating against
§8 implementation plan execution. Risks are organized into five
risk classes per the PHASE2C_8.0 §6 reference (methodology-evidence
hierarchy / data-quality / implementation-defect / interpretation-
overreach / scope-creep). Risk #6 (Concern A in-sample evaluation
overlap) is methodology-evidence hierarchy class with verbatim
phrasing inherited from §3.3 + §7.4 per Q-D29 preservation
discipline.

§10 treats each risk with: phrasing / mechanism / mitigation status
/ classification / forward signal.

### 10.1 Risk #1 — Regime-source-selection failure

- **Phrasing**: Selected additional regimes (eval_2020_v1 +
  eval_2021_v1) prove operationally defective at implementation
  time (e.g., per-regime trade-count distribution falls below
  expected range; data-quality issue surfaces; config block
  addition blocked by immutability re-interpretation).
- **Mechanism**: §3.3 selection adjudication scored S2 (data
  availability) + S4 (population sufficiency) at HIGH; if
  implementation-time evidence diverges sharply from §3.3 scoring,
  the selected regimes may not produce the expected evaluation
  evidence base.
- **Mitigation status**: Partial. §3.3 backup regime (2023) is
  documented as forward-pointing fallback; activation requires new
  §3.3 sub-cycle adjudication. §3.3.6 conditional-shift triggers
  capture five trigger conditions for selection invalidation.
- **Classification**: Implementation-defect class; mitigated by
  backup-regime forward-pointing.
- **Forward signal**: §8 Step 1.4 smoke verification surfaces
  per-regime data-quality + population issues before Step 2 full
  evaluation; backup regime activation discipline at §3.3.6.

### 10.2 Risk #2 — Multi-regime infrastructure complexity

- **Phrasing**: §6 producer artifact specification + §7 lineage
  attestation + §8 Step 4 multi-regime comparison matrix collectively
  introduce multi-regime infrastructure complexity that exceeds
  PHASE2C_7.1's two-regime infrastructure; implementation defects
  may surface at integration boundaries.
- **Mechanism**: PHASE2C_7.1 had n=2 regimes; PHASE2C_8.1 has n=4
  regimes with mixed schema discriminators + cross-arc inheritance
  + in-sample caveat classification. The infrastructure expansion
  introduces new defect classes at integration boundaries (e.g.,
  hypothesis_hash join correctness across 4 CSVs; cohort-stratified
  pass-rate computation across 4 regimes; in-sample caveat
  stratification at output level).
- **Mitigation status**: Partial. §6.7 hard guards (no config
  mutation; no 2025 touch; engine-version invariance) + §6.5
  mixed-discriminator reconciliation rule + §7.2 4-step inherited-
  run re-use validation + §8.6 sequential gating discipline
  collectively constrain the integration surface; defects may still
  surface at boundaries not covered by the named guards.
- **Classification**: Implementation-defect class; mitigated by hard
  guards + reconciliation rules + sequential gating.
- **Forward signal**: §8 Step 1 sub-step gating surfaces integration
  defects before Step 2; §8 Step 4 P3 cardinality check surfaces
  hypothesis_hash join correctness; §8 Step 5 closeout adversarial
  review surfaces residual defects pre-commit.

### 10.3 Risk #3 — Cross-regime intersection sparsity

- **Phrasing**: At n=4 baseline, the cross-regime intersection set
  (candidates passing AND-gate in all 4 regimes) may be empty or
  very small (e.g., n < 5); if so, primary-cohort cross-regime
  evidence becomes statistically weak.
- **Mechanism**: Single-regime AND-gate pass rates at PHASE2C_6
  (bear_2022) + PHASE2C_7.1 (validation_2024) were ~5-12% per
  regime. At n=4 with independence assumption, expected
  intersection cardinality ≈ 198 × 0.08^4 ≈ 0.08 candidates (effectively
  zero). With positive correlation across regimes (likely if
  candidates have genuine cross-regime mechanism), intersection
  may produce 1-5 candidates.
- **Mitigation status**: None at design level; intersection
  sparsity is empirical outcome. Mitigated at interpretation level:
  §10 interpretation-overreach class capture (Risk #5 below).
- **Classification**: Methodology-evidence hierarchy class; risk is
  intrinsic to multi-regime evaluation at n=4.
- **Forward signal**: §8 Step 4 P4 verification reports intersection
  cardinality; §8 Step 5 closeout interprets intersection-sparse
  evidence with appropriate epistemic caveats per Risk #5 mitigation.

### 10.4 Risk #4 — Closeout drafting scope expansion

- **Phrasing**: PHASE2C_8.1 closeout drafting cycle scope may
  expand beyond §8 Step 5 specification due to multi-direction
  findings + post-codification METHODOLOGY_NOTES discipline
  application + adversarial review fold cycle.
- **Mechanism**: PHASE2C_7.1 closeout drafting cycle expanded to
  multiple cycles (PHASE2C_7.1.1-7.1.7) with §10 + §9 + §11 + §12
  discipline applications; PHASE2C_8.1 closeout may follow similar
  expansion pattern. Scope expansion is structural (multi-direction
  findings warrant outline-first drafting per §9 of METHODOLOGY_NOTES);
  not defect.
- **Mitigation status**: Partial. §11 closeout-assembly checklist
  + §9 Path-2 outline-first drafting + §12 complementary defect-class
  coverage operate at PHASE2C_8.1 closeout register; the discipline
  application is structural framing, not scope reduction.
- **Classification**: Scope-creep class; mitigated by lifecycle-stage
  discipline application.
- **Forward signal**: §8 Step 5 anticipates multi-cycle closeout
  drafting per PHASE2C_7.1 precedent; closeout cycles operate against
  the same discipline framework.

### 10.5 Risk #5 — Regime-selection becoming post-hoc narrative fitting

- **Phrasing**: PHASE2C_8.1 selection adjudication at §3.3 may
  produce evidence that supports a specific mechanism candidate
  (regime-mismatch / pattern-overfit / calibration-coupling) which
  becomes a self-reinforcing narrative at closeout interpretation;
  the selection adjudication's structural rationale (S5 mechanism-
  relevance distinctness) may be retroactively interpreted as
  supporting the chosen mechanism candidate beyond evidence weight.
- **Mechanism**: Q-B1 mechanism question at PHASE2C_8.0 §5 framed
  the regime axis as distinguishing among three mechanism candidates;
  PHASE2C_8.1 evaluation produces evidence that's interpreted against
  these candidates. Interpretation framing risks retroactive
  alignment between selected regimes' empirical patterns and
  mechanism candidate predictions, even when alignment is partial
  or noisy.
- **Mitigation status**: Partial. §10 anti-pre-naming discipline at
  §3.3 (Stage A → Stage B handoff) + §3.3.6 conditional-shift
  triggers + §7.4 in-sample caveat classification + §10 risk #5
  capture itself collectively constrain the post-hoc narrative
  fitting. Closeout drafting per §9 + §11 + §12 discipline
  application surfaces the risk at adversarial review pre-commit.
- **Classification**: Interpretation-overreach class; mitigated by
  multi-layer discipline application.
- **Forward signal**: §8 Step 5 closeout drafting applies §1
  empirical verification + §9 Path-2 outline-first drafting + §12
  adversarial review at high-load closeout register; risk #5
  surfacing in closeout flagged + treated explicitly.

### 10.6 Risk #6 — Concern A in-sample evaluation overlap

- **Phrasing**: 2020/2021 overlap the original train-window context;
  mitigated by walk-forward sub-window discipline, but not equivalent
  to untouched validation/test evidence.
- **Mechanism**: PHASE2C_5 training process used sub-windows of
  2020 and 2021 historical data; PHASE2C_6's 198-candidate population
  may carry candidate-screening overfitting against these regimes.
  Cross-regime patterns observed in 2020/2021 may reflect candidate-
  screening artifacts rather than mechanism-relevant structure. The
  in-sample evaluation overlap is structural to the candidate-regime
  selection scope (selected regimes 2020 + 2021 are part of v2 train
  split per `config/environments.yaml`).
- **Mitigation status**: Partial. Walk-forward sub-window discipline
  operates within each candidate's training process — training
  windows are sub-windows of the calendar year, not the full year;
  walk-forward cross-validation operates within-regime. The
  mitigation is not zero, but not equivalent to fully-untouched
  evidence (such as bear_2022 holdout or validation_2024). §7.5
  `in_sample_caveat_applies` boolean field per regime captures the
  classification at metadata level; §8 Step 4 stratifies output by
  caveat-applies vs caveat-not-applies.
- **Classification**: Methodology-evidence hierarchy class; risk is
  intrinsic to candidate-regime selection scope.
- **Forward signal**: §3.3.4 in-sample evaluation caveat → §7.4
  in-sample caveat classification + comparison register → §8 Step
  4 caveat-stratified output → §10 risk #6 (this entry) → §8 Step
  5 closeout interpretation with caveat preserved.

### 10.7 Out-of-scope statements

PHASE2C_8.1 explicitly excludes:

- **2025 test split touched-once compliance**: 2025 calendar-year
  evaluation against 198-candidate population is structurally
  prohibited per V1 veto + CLAUDE.md hard rule. Any future
  evaluation against 2025 requires separate scoping decision +
  test-split touched-once consumption (one-time evaluation; no
  re-iteration).
- **PHASE2C_8.0 scoping decision re-litigation**: Q-B1 selection
  over Q-B2 / Q-B3.a / Q-B3.b / Q-B4 was adjudicated at PHASE2C_8.0
  scoping decision (`docs/phase2c/PHASE2C_8_SCOPING_DECISION.md`
  committed at f223316). PHASE2C_8.1 operates against the locked
  scoping decision; alternative-path scoping is not in scope.
- **Calibration variation (Q-B2 territory)**: PHASE2C_8.1's
  4-criterion AND-gate + >= 20 trade-count filter inherit
  PHASE2C_7.1's calibration baseline uniformly across all 4
  regimes. Calibration tuning per regime is Q-B2 scope (deferred
  to follow-up scoping decision per PHASE2C_8.0 §5 conditional-shift
  triggers).
- **Cohort deep-dive (Q-B3 territory)**: PHASE2C_8.1's primary
  (n=44) + audit-only (n=154) cohort partition is preserved at
  metadata level; cohort-internal analysis (e.g., per-candidate
  case studies) is out-of-scope and reserved for Q-B3 follow-up
  scoping if warranted.
- **DSR infrastructure (Q-B4 territory)**: PHASE2C_8.1's evaluation
  uses single-regime gate + cross-regime intersection at §8 Step
  4; statistical significance via DSR / PBO / CPCV methodology is
  out-of-scope and reserved for Q-B4 follow-up scoping.
- **Future-arc scoping**: PHASE2C_8.1 closeout's §9 may surface
  follow-up scoping questions; selection of next implementation
  arc is post-PHASE2C_8.1 closure; not pre-named per Q-FS4
  strictness.

The out-of-scope statements operationally bound PHASE2C_8.1's
implementation surface; deviation from the bounded surface requires
new scoping decision (successor administrative identifier; not
pre-named at PHASE2C_8.1 spec time per Q-FS4 strictness).

---