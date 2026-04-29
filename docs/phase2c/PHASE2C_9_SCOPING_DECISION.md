# PHASE2C_9 Scoping Decision


## 1. Scope and verdict

**This document scopes the next implementation arc after PHASE2C_8.1
multi-regime evaluation gate (extended) sealed at origin/main commit
`8154e99` (PHASE2C_8.1 closeout `69e9af9` + METHODOLOGY_NOTES update
`8154e99`; tag `phase2c-8-1-multi-regime-extended-v1`). It compares
four candidate next-arc directions (Q-9.A through Q-9.D) against
explicit decision criteria and surfaces pairwise comparisons, but
does NOT pre-lock substantive theme. Substantive theme selection
ratifies through the scoping deliberation register — not through
pre-cycle reviewer convergence — per anti-pre-naming discipline
codified at METHODOLOGY_NOTES §10.**

**Project state at PHASE2C_9 scoping (2026-04-29).**

- Canonical main: `origin/main` at commit `8154e99`
- Tags on main: `wf-corrected-v1` (corrected WF engine fix at
  `eb1c87f`); `phase2c-7-1-multi-regime-v1` (PHASE2C_7.1 multi-regime
  evaluation gate sealing); `phase2c-8-1-multi-regime-extended-v1`
  (PHASE2C_8.1 multi-regime evaluation gate extended sealing)
- Standing project-discipline corpus: `docs/discipline/METHODOLOGY_NOTES.md`
  at 1899 lines / 15 sections (PHASE2C_8.1 methodology codifications
  applied at `8154e99`)
- Recent shipped arcs:
  - PHASE2C_5: Phase 1 walk-forward closeout +
    corrected-engine erratum
  - Corrected WF Engine project arc:
    `docs/closeout/CORRECTED_WF_ENGINE_SIGNOFF.md`
  - PHASE2C_6: Single-regime (2022) evaluation gate
    closeout
  - PHASE2C_7.0: Scoping decision on Path A vs Path B vs Path C
  - PHASE2C_7.1: Multi-regime evaluation gate (Path B implementation
    arc)
  - PHASE2C_8.0: Scoping decision on Q-B1/Q-B2/Q-B3.a/Q-B3.b/Q-B4
    territory
  - PHASE2C_8.1: Multi-regime evaluation gate (extended; Q-B1
    implementation arc; n=4 evaluation against bear_2022 +
    validation_2024 + eval_2020_v1 + eval_2021_v1)
- Current UTC-month spend (April 2026): ~$8.65 (no API spend on
  PHASE2C_6/_7.1/_8.1 evaluation work — local backtest evaluation only)

**Verdict register (this scoping):**

PHASE2C_9 substantive theme is open. Four candidate directions
surface from PHASE2C_8.1's evidence base (forward-signal cluster
§11.1 / §11.2 / §11.3 / §11.4 + register entries Q-S4-7 / Q-S4-13).
This document compares the four against six decision-criteria axes
and produces structured pairwise reasoning, but does NOT lock the
theme. Theme selection requires Charlie's explicit ratification on
the adjudication framing at §5.

The scoping discipline operates per anti-pre-naming framework
(METHODOLOGY_NOTES §10): informal three-reviewer convergence on
substantive theme before scoping cycle initiates would skip the
scoping deliberation register. PHASE2C_9 scoping cycle deliberates
explicitly on four candidate directions; pre-locking on any of them
forecloses the deliberation.

**Per spec §10.7 + Q-FS4 strictness inherited from PHASE2C_8.1**:
selection of next implementation arc is a scoping cycle's primary
deliberation, not pre-named at prior arc closeouts. PHASE2C_8.1's
§11 forward signals surfaced four candidate methodology-process
codifications (Q-S4-10/14/15/16) without pre-naming successor arcs.
PHASE2C_9 inherits the discipline at the meta-arc level: substantive
theme selection happens in scoping cycle, not in pre-cycle reviewer
alignment.


## 2. Inheritance from PHASE2C_8.1

PHASE2C_8.1's evidence base produces three load-bearing forward
signals + two register-entry methodology bounds that anchor PHASE2C_9
scoping:

### §2.1 — Forward signals from PHASE2C_8.1 closeout

- **§11.1 DSR / PBO / CPCV machinery deferral.** The methodology-
  evidence hierarchy bound at §9.2 + §1.2 + §5.4 + §6.4 (all citing
  Q-S4-7) is the load-bearing methodology-limit forward signal.
  PHASE2C_8.1 produces population-level cardinalities and patterns
  observable at the verification chain's three layers; per-strategy
  or per-regime statistical-significance claims are not defensible
  without DSR / PBO / CPCV infrastructure deferred per spec §10.7
  (Q-B4 territory). Distinguishing whether cohort_a_unfiltered = 1
  reflects real cross-regime signal versus population-level random
  alignment, whether the 21-vs-8 asymmetry exceeds null-hypothesis
  variance, and whether per-candidate profiles meet conventional
  significance thresholds — these are adjudicable only with multiple-
  comparisons-corrected significance machinery.

- **§11.2 Gate-calibration methodology question (Q-S4-13).** The
  eval_2021_v1 negative-return-passes observation at §6.2 (the lone
  survivor's -10.2% return passing the AND-gate as currently
  calibrated) surfaces a calibration methodology question. The 4-
  criterion AND-gate inherited from PHASE2C_7.1's calibration
  baseline (sharpe ≥ −0.5; max_drawdown ≤ 0.25; total_return ≥ −0.15;
  total_trades ≥ 5) accepts the candidate as passing; whether this
  calibration is appropriate for multi-regime evaluation contexts
  where per-regime negative returns affect cross-regime survival
  interpretation is the open question. Calibration variation (Q-B2
  territory) is out-of-scope per spec §10.7.

- **§11.3 Audit-only partition implication (§6.3).** The lone
  unfiltered cross-regime survivor's audit-only partition origin
  (`wf_test_period_sharpe = -0.072 < 0.5` primary threshold) is
  consistent with multiple mechanisms — walk-forward classifier
  mis-coverage, selection-effect amplification, trade-frequency
  interaction. PHASE2C_8.1 evidence does not adjudicate which
  mechanism applies. The forward signal is the methodology question:
  walk-forward prequalification's coverage of cross-regime survival
  quality is not directly tested by PHASE2C_8.1 scope.

### §2.2 — Register-entry methodology bounds

- **Q-S4-7 (DSR/PBO/CPCV deferral; Q-B4 territory).** Surfaced as
  methodology-evidence bound. Statistical-significance machinery is
  out-of-scope per PHASE2C_8.1 spec §10.7; deferred to Q-B4 follow-up
  scoping. PHASE2C_8.1's findings operate at population-level pattern
  register, not per-strategy significance register.

- **Q-S4-13 (gate-calibration methodology question; Q-B2 territory).**
  Surfaced as methodology question. Calibration variation is out-of-
  scope per PHASE2C_8.1 spec §10.7. The bound, if answered with
  stricter thresholds, would tighten constraints on cohort_a
  cardinality interpretation.

### §2.3 — Empirical-finding-derived implications

PHASE2C_8.1 produced three load-bearing findings that constitute the
substantive evidence base for PHASE2C_9 scoping:

- **Population-level finding**: 21-vs-8 in-sample-caveat asymmetry
  between train-overlap regimes (eval_2020_v1 + eval_2021_v1) and
  fully-out-of-sample regimes (bear_2022 + validation_2024). Direction
  matches Concern A (in-sample caveat) prediction.
- **Candidate-level finding**: cohort_a_unfiltered = 1 (lone candidate
  `0845d1d7898412f2`); cohort_a_filtered = 0 (zero candidates survive
  at filtered tier; lone-survivor excluded by single-trade margin in
  bear_2022).
- **Methodology-evidence**: verification chain at three independent
  layers reproduces canonical numbers byte-identically; permanent
  in-repo recompute gate at
  `tests/test_phase2c_8_1_independent_recompute.py`.

The implications operate in two registers:
- **Methodology-evidence register**: strengthened (verification chain
  + in-sample-caveat asymmetry + audit-only-partition direction
  reinforcement).
- **Strategy-evidence register**: constrained (cohort_a_filtered = 0;
  hybrid lone-survivor profile; 21-vs-8 asymmetry suggests train-
  overlap-apparent quality may not generalize fully out-of-sample).

PHASE2C_9 scoping inherits both registers: the strengthened methodology
base supports more sophisticated analysis (Q-9.A statistical validation
candidate); the constrained strategy register surfaces mining-process
implications (Q-9.B mining retrospective candidate) and gate-calibration
questions (Q-9.C calibration variation candidate); the bounded strategy
register also surfaces forward-progression questions (Q-9.D Phase 3
scoping candidate).


## 3. Four candidate next-arc paths

Each candidate is scoped at register sufficient for adjudication: what
question it addresses, what evidence base it produces, what cost it
incurs, what bounds it closes, and what forward-progress register it
operates in. None are pre-recommended; the recommendation emerges
through §4 decision-criteria reasoning and §5 pairwise comparison.

### Q-9.A — Statistical validation layer (DSR / PBO ± CPCV)

**Question addressed**: Do PHASE2C_8.1's population-level findings
(cohort_a_unfiltered = 1; 21-vs-8 in-sample-caveat asymmetry; cohort_c
= 76; theme-level pass-count distributions) survive multiple-
comparisons correction? Closes Q-S4-7 / Q-B4 territory deferral.

**Evidence base produced**: per-candidate Deflated Sharpe Ratio
(DSR) at the 198-candidate × 4-regime evaluation surface; cohort-
or regime-level Probability of Backtest Overfitting (PBO);
optionally Combinatorially Purged Cross-Validation (CPCV) if
temporal-leakage concerns surface as primary risk.

**Concrete deliverable shape**: implementation arc producing
`data/phase2c_evaluation_gate/statistical_validation_v1/`
artifacts (per-candidate DSR JSON; cohort-level PBO probability
table; optional CPCV grid); closeout document at
`docs/closeout/PHASE2C_9_RESULTS.md` with cohort_a/_filtered/cohort_c
re-classification under multiple-comparisons-corrected verdict.

**Implementation cost**: substantial. DSR/PBO infrastructure does
not currently exist in repo; literature engagement (Bailey-López-de-
Prado 2014/2016 for DSR; Bailey-Borwein-López-de-Prado-Zhu 2014 for
PBO) required; statistical-significance code path needs independent
verification per §13 parallel-implementation discipline. Estimated:
~6-8 implementation sessions (ChatGPT estimate at three-way
convergence cycle).

**Bound closure**: Q-S4-7 directly closed; Q-S4-13 not addressed;
mining-process implication not addressed; phase-progression not
addressed.

**Information-gain register**: bounded by small-sample regime at
N=198 candidates × 4 regimes = 792 evaluations. DSR/PBO machinery has
well-known small-sample issues; likely outcomes are "0 of 198 survive
correction" (which we somewhat already infer from cohort_a_filtered
= 0) or "k survive where k is small enough to inherit selection-
effect concerns from Codex review-response trajectory."

**Risk register**: small-sample DSR can return false-positive
significance under specific parameter regimes (e.g., when test-period
volatility is mismeasured); CPCV at N=198 has limited combinatorial
support; multiple-comparisons-correction itself involves analyst
choices (k-of-n threshold; correction family selection) that affect
outcome and require pre-registration to avoid post-hoc selection.

**Forward-progress register**: LOW. Operates retrospectively on
existing batch-1 candidate population; does not progress beyond
PHASE2C evaluation cycle.

**2025 test split touched-once preservation (CLAUDE.md hard rule)**:
NOT TOUCHED. Operates on existing 2022 + 2024 + eval_2020_v1 +
eval_2021_v1 evaluation outputs only.

### Q-9.B — Mining-process retrospective (Phase 2B Proposer/Critic)

**Question addressed**: Why did PHASE2C Phase 2B Proposer/Critic
produce a 198-candidate batch where cohort_a_filtered = 0 and the
lone unfiltered cross-regime survivor has a hybrid quality profile
(off-by-1 filter exclusion + permissive AND-gate accepting -10.2%
return + audit-only partition origin)? Mining-process implication
inferred from PHASE2C_8.1 findings.

**Evidence base produced**: structured retrospective on batch-1
mining-process artifacts. Possible scopes (need scoping cycle
adjudication):
- Light-touch documentation review of Proposer/Critic prompt design,
  candidate-passing criteria, and theme rotation outputs
- Structured re-examination of high-pass-count candidates against
  mining-process inputs (which themes / proposals / critic verdicts
  produced cohort_c=76 vs cohort_a=0)
- Mining-process redesign scoping for batch-2 (informed by batch-1
  retrospective findings)

**Concrete deliverable shape**: closeout document at
`docs/closeout/PHASE2C_9_MINING_RETROSPECTIVE.md` with retrospective
findings; potentially Phase 2B specification revisions for batch-2;
no new evaluation artifacts required (operates on existing
mining-process artifacts at `agents/spend_ledger.db` + raw_payloads/
+ batch CSVs).

**Implementation cost**: variable. Light-touch retrospective is
~2-3 sessions; structured re-examination is ~4-5 sessions; mining-
process redesign scoping is additional ~3-4 sessions. Cost scales
with retrospective depth.

**Bound closure**: NONE direct on Q-S4-N register entries. Informal
closure of mining-process implication of cohort_a_filtered = 0;
informs batch-2 mining design.

**Information-gain register**: HIGH at appropriate retrospective
depth. Mining-process insights are actionable for batch-2 design
(theme rotation; prompt engineering; AND-gate calibration in
candidate-passing criteria); they do not require statistical-
significance machinery to be load-bearing.

**Risk register**: retrospective-on-self bias (current Claude session
re-examining PHASE2C work cycle's own outputs); structured re-
examination requires pre-defined questions to avoid post-hoc rationalization.

**Forward-progress register**: MEDIUM. Informs batch-2 mining design
(forward) but does not directly progress Phase 3+. If retrospective
finds mining-process needs significant redesign, batch-2 fire is
deferred until redesign completes.

**2025 test split touched-once preservation**: NOT TOUCHED.

### Q-9.C — Gate-calibration variation study

**Question addressed**: Is the inherited 4-criterion AND-gate
(sharpe ≥ −0.5; max_drawdown ≤ 0.25; total_return ≥ −0.15;
total_trades ≥ 5) appropriately calibrated for multi-regime
evaluation contexts? Closes Q-S4-13 / Q-B2 territory deferral.

**Evidence base produced**: cohort-cardinality sensitivity analysis
under varied calibration thresholds. Possible variation axes:
- Sharpe threshold (−0.5 baseline; ablate −0.3, 0.0, +0.3)
- Total-return threshold (−0.15 baseline; ablate −0.05, 0.0, +0.05)
- Trade-count filter (≥20 baseline; ablate ≥10, ≥30, ≥50)
- Per-regime vs cross-regime calibration (current is uniform across
  regimes; ablate per-regime thresholds)

**Concrete deliverable shape**: implementation arc producing
`data/phase2c_evaluation_gate/calibration_variation_v1/` artifacts
(grid of cohort cardinalities under varied calibration); closeout
document at `docs/closeout/PHASE2C_9_RESULTS.md` with cohort_a/_filtered
sensitivity table + adjudication on whether current calibration is
appropriate.

**Implementation cost**: bounded. Calibration variation reuses
existing evaluation infrastructure (`scripts/compare_multi_regime.py`
+ `compare_multi_regime.py:_apply_multi_regime`); new code is
limited to calibration-variation orchestration script + cohort-
cardinality grid generation. Estimated: ~3-4 implementation sessions.

**Bound closure**: Q-S4-13 directly closed; Q-S4-7 not addressed;
mining-process implication not addressed; phase-progression not
addressed.

**Information-gain register**: MEDIUM. Calibration sensitivity
provides tighter bounds on cohort_a cardinality interpretation; if
calibration is highly sensitive (cohort_a varies substantially under
mild threshold changes), interpretation of cohort_a_filtered = 0
becomes less load-bearing; if calibration is robust, the existing
cohort_a interpretation strengthens.

**Risk register**: post-hoc calibration optimization (selecting
calibration that produces favored cohort cardinality) is a real
defect class — needs pre-registration of calibration variation grid
before evaluation runs to avoid p-hacking-equivalent at calibration
register. Current calibration is inherited from PHASE2C_7.1, which
is the historically-locked baseline; variation study should treat
inherited as anchor, not as one of N variations.

**Forward-progress register**: LOW. Operates retrospectively on
existing batch-1 candidate population; does not progress beyond
PHASE2C evaluation cycle.

**2025 test split touched-once preservation**: NOT TOUCHED.

### Q-9.D — Phase 3 progression scoping

**Question addressed**: Should the project progress to Phase 3
(risk/position-sizing) before continuing PHASE2C evaluation cycle on
batch-1, or should evaluation cycle continue first? Phase progression
question raised by 0 candidates deployable from batch-1 per
PHASE2C_8.1 bounds.

**Evidence base produced**: Phase 3 scoping document at
`docs/phase3/PHASE3_SCOPING_DECISION.md` with:
- Phase 3 target deliverable (risk/position-sizing infrastructure;
  capital allocation; portfolio-level construction)
- Dependencies on Phase 2C deliverables (does Phase 3 require any
  candidates from PHASE2C, or operates on baselines?)
- Sequencing question (Phase 3 first vs Phase 2C continuation first)
- Feasibility under no-deployable-candidates-from-batch-1 constraint
  (Phase 3 design may proceed with hand-written baselines + paper-
  trading-relevant strategies independent of Phase 2C mining outputs)

**Concrete deliverable shape**: scoping document only (not
implementation). Phase 3 implementation is a separate downstream
arc; PHASE2C_9 = Q-9.D is the scoping cycle that decides whether
Phase 3 implementation initiates next, or whether PHASE2C evaluation
cycle continues with one of Q-9.A/B/C.

**Implementation cost**: bounded for scoping-only deliverable.
Estimated: ~2-3 sessions for Phase 3 scoping document drafting.
Phase 3 implementation cost is substantial and not in PHASE2C_9
scope; that's a future scoping cycle's deliberation.

**Bound closure**: NONE direct on Q-S4-N register entries. Closure
of meta-arc question "does PHASE2C evaluation cycle continue or does
the project progress to Phase 3+?"

**Information-gain register**: HIGH at meta-arc level (does the
project sequence onward to risk/position-sizing or continue
evaluation refinement?); LOW at within-PHASE2C-arc register (no new
PHASE2C-arc evaluation produced).

**Risk register**: Phase 3 scoping under bounded Phase 2C deliverables
may surface dependencies (Phase 3 design may need at least one
deployment-candidate-quality strategy from Phase 2C; if cohort_a_filtered
= 0 holds under all examined calibrations + statistical corrections,
Phase 3 design proceeds with baselines only). The dependency
question is itself a scoping output.

**Forward-progress register**: HIGHEST among the four candidates.
Only direction that progresses beyond PHASE2C evaluation cycle.

**2025 test split touched-once preservation**: NOT YET TOUCHED.
Phase 3 design preserves test split (test-once preservation extends
across phases).

### §3.5 — Hybrid combinations (deliberately surfaced)

The four candidates are not strictly mutually exclusive; hybrid
combinations are possible. Worth flagging at scoping register before
adjudication:

- **Q-9.A + Q-9.C hybrid (statistical validation under varied
  calibration)**: closes both Q-S4-7 and Q-S4-13; cost is
  approximately additive; information-gain is multiplicative if
  calibration variation × statistical-significance-correction
  surface produces structurally distinct findings under different
  calibration regimes.
- **Q-9.A + Q-9.B hybrid (statistical validation + mining
  retrospective)**: closes Q-S4-7 and addresses mining-process
  implication; cost is additive; information-gain depends on whether
  statistical-significance findings inform mining retrospective
  questions (e.g., if "k of 198 survive correction" is small enough
  to constrain mining-process redesign considerations).
- **Q-9.B + Q-9.D hybrid (mining retrospective + Phase 3 scoping)**:
  addresses mining-process implication and surfaces phase-progression
  question; cost is bounded; information-gain crosses retrospective
  + forward-progression registers.
- **Q-9.C + Q-9.D hybrid (gate calibration + Phase 3 scoping)**:
  closes Q-S4-13 and surfaces phase-progression; cost is bounded;
  information-gain register similar to Q-9.B + Q-9.D.

Hybrid combinations expand the candidate space from 4 to ~10 (4
single + ~6 pairwise). Triple+ combinations are within combinatorial
reach but operationally substantial; likely impractical for single
implementation arc. Adjudication framing at §5 should explicitly
consider whether single-direction lock or pairwise hybrid is the
right register for PHASE2C_9.


## 4. Decision criteria

Six axes evaluate each candidate. The axes are not equally weighted;
weighting is itself an adjudication question surfaced at §5.

### Axis 1 — Closure of PHASE2C_8.1 methodology-evidence bounds

PHASE2C_8.1 produced two methodology-evidence bounds at register
level (Q-S4-7 + Q-S4-13). Each bound represents an open methodology
question that constrains current verdict register interpretation.
Closing a bound improves the methodology-evidence base:

| Candidate | Q-S4-7 closure | Q-S4-13 closure | Net |
|---|---|---|---|
| Q-9.A | Direct | None | 1/2 |
| Q-9.B | None | None | 0/2 |
| Q-9.C | None | Direct | 1/2 |
| Q-9.D | None | None | 0/2 |
| Q-9.A + Q-9.C hybrid | Direct | Direct | 2/2 |

Q-9.B and Q-9.D close mining-process implications and phase-
progression questions respectively, but neither maps to a Q-S4-N
register entry as direct bound closure.

### Axis 2 — Information gain at canonical-finding register

Information gain is the marginal evidence the candidate produces
relative to PHASE2C_8.1's existing canonical findings:

| Candidate | Information-gain register | Notes |
|---|---|---|
| Q-9.A | BOUNDED | Small-sample regime at N=198; likely 0 or near-0 survivors at correction; partly anticipated from cohort_a_filtered=0 |
| Q-9.B | HIGH (depth-conditional) | Mining-process insights actionable for batch-2; high gain at structured-re-examination depth |
| Q-9.C | MEDIUM | Calibration sensitivity tightens cohort_a interpretation bounds |
| Q-9.D | HIGH at meta-level / LOW at PHASE2C-arc | Phase-progression decision is high-leverage; within-PHASE2C-arc gain is none |

The information-gain register is conditional on candidate scope
(e.g., Q-9.B's information gain scales with retrospective depth;
Q-9.D's information gain depends on phase-progression question
framing). Conditional information-gain is not pre-comparable across
candidates without scope-fixing.

### Axis 3 — Implementation cost (sessions + structural complexity)

| Candidate | Cost register | Estimate |
|---|---|---|
| Q-9.A | SUBSTANTIAL | ~6-8 sessions; DSR/PBO infrastructure new; CPCV conditional adds ~2-4 |
| Q-9.B | VARIABLE | ~2-3 sessions (light) to ~7-9 sessions (with redesign scoping) |
| Q-9.C | BOUNDED | ~3-4 sessions; reuses existing infrastructure |
| Q-9.D | BOUNDED for scoping-only | ~2-3 sessions; Phase 3 implementation cost is downstream |

Q-9.A's cost is the highest among the four; the cost reflects
infrastructure-build overhead (statistical-significance machinery
does not exist in repo yet). Q-9.B / Q-9.C / Q-9.D scopes are
relatively bounded under their respective single-direction framings.

### Axis 4 — Risk of self-deception / methodology defect

Each candidate carries methodology-defect risk register:

- **Q-9.A**: small-sample DSR false-positive significance under
  parameter regimes; CPCV combinatorial support at N=198; multiple-
  comparisons-correction analyst-choice register requires pre-
  registration. Risk register: MEDIUM (real but well-catalogued).
- **Q-9.B**: retrospective-on-self bias; structured re-examination
  needs pre-defined questions to avoid post-hoc rationalization.
  Risk register: LOW (no new statistical machinery; primarily
  documentation discipline).
- **Q-9.C**: post-hoc calibration optimization (p-hacking-equivalent
  at calibration register); needs pre-registration of variation grid
  before evaluation runs. Risk register: MEDIUM (real defect class;
  mitigatable by pre-registration discipline).
- **Q-9.D**: dependency surface unclear (does Phase 3 require Phase
  2C deployment-candidate-quality strategies?); phase-progression
  decision register requires honest assessment of bounded Phase 2C
  deliverables. Risk register: LOW (forward-progression on
  documented Phase 3+ markers; risk register is at conditional
  scoping output, not at scoping process).

Q-9.A and Q-9.C carry the highest methodology-defect risk among the
four; both require pre-registration discipline to mitigate. Q-9.B
and Q-9.D carry lower methodology-defect risk by their respective
register profiles.

### Axis 5 — Forward-progress value

Forward-progress register: does the candidate progress beyond
PHASE2C evaluation cycle, or operate retrospectively?

| Candidate | Forward-progress register |
|---|---|
| Q-9.A | LOW — retrospective on existing batch-1 |
| Q-9.B | MEDIUM — informs batch-2 mining design |
| Q-9.C | LOW — retrospective on existing batch-1 |
| Q-9.D | HIGHEST — only direction that progresses beyond PHASE2C |

Forward-progress is structurally distinct from information-gain.
A candidate can have high information gain at retrospective register
(e.g., Q-9.B) but low forward-progress value if information does not
translate to forward-arc progression.

### Axis 6 — 2025 test split touched-once preservation (CLAUDE.md hard rule)

CLAUDE.md "Date Split Rules" hard rule: "Test data is touched ONCE
for final evaluation. If you peek and iterate, it becomes validation
data."

| Candidate | 2025 test split preservation |
|---|---|
| Q-9.A | NOT TOUCHED — operates on existing 2022+2024+eval_2020+eval_2021 |
| Q-9.B | NOT TOUCHED — retrospective on mining-process artifacts |
| Q-9.C | NOT TOUCHED — operates on existing evaluations |
| Q-9.D | NOT YET TOUCHED — Phase 3 design preserves split |

All four candidates preserve the 2025 test split touched-once rule.
This axis does not differentiate among the four; it functions as a
hard-rule check that all candidates pass.


## 5. Pairwise comparison + adjudication framing

### §5.1 — Pairwise comparison: Q-9.A vs Q-9.B

| Axis | Q-9.A | Q-9.B |
|---|---|---|
| Bound closure | Q-S4-7 direct | None direct |
| Information gain | BOUNDED (small-sample) | HIGH (depth-conditional) |
| Cost | SUBSTANTIAL (~6-8 sessions) | VARIABLE (~2-9 sessions) |
| Methodology-defect risk | MEDIUM | LOW |
| Forward-progress | LOW | MEDIUM |

**Reasoning**: Q-9.B has higher information gain at appropriate
retrospective depth, lower implementation cost at light-touch scope,
lower methodology-defect risk, and higher forward-progress register.
Q-9.A's structural advantage is direct bound closure on Q-S4-7,
which Q-9.B cannot provide. The pairwise tradeoff is "retrospective
gain + actionable batch-2 input (Q-9.B)" vs "methodology-evidence-
bound closure (Q-9.A)."

If the highest-leverage question is "does PHASE2C_8.1's evidence
base survive multiple-comparisons correction," Q-9.A is structurally
correct. If the highest-leverage question is "what should batch-2
mining-process design look like," Q-9.B is structurally correct.

### §5.2 — Pairwise comparison: Q-9.A vs Q-9.C

| Axis | Q-9.A | Q-9.C |
|---|---|---|
| Bound closure | Q-S4-7 direct | Q-S4-13 direct |
| Information gain | BOUNDED | MEDIUM |
| Cost | SUBSTANTIAL | BOUNDED |
| Methodology-defect risk | MEDIUM | MEDIUM |
| Forward-progress | LOW | LOW |

**Reasoning**: Q-9.C has lower implementation cost, comparable
methodology-defect risk, and addresses a different methodology-
evidence bound (Q-S4-13 calibration question). Q-9.A's direct closure
on Q-S4-7 is structurally distinct from Q-9.C's direct closure on
Q-S4-13. The pairwise tradeoff is "Q-S4-7 closure (statistical-
significance machinery) at higher cost" vs "Q-S4-13 closure
(calibration variation) at lower cost."

The Q-9.A + Q-9.C hybrid (§3.5) closes both bounds; cost is roughly
additive; this is a structurally clean hybrid pattern.

### §5.3 — Pairwise comparison: Q-9.A vs Q-9.D

| Axis | Q-9.A | Q-9.D |
|---|---|---|
| Bound closure | Q-S4-7 direct | None direct |
| Information gain | BOUNDED | HIGH at meta / LOW at arc |
| Cost | SUBSTANTIAL | BOUNDED for scoping-only |
| Methodology-defect risk | MEDIUM | LOW |
| Forward-progress | LOW | HIGHEST |

**Reasoning**: Q-9.D has the highest forward-progress register;
Q-9.A operates retrospectively. The pairwise tradeoff is
"methodology-evidence base improvement on existing batch-1 (Q-9.A)"
vs "phase-progression beyond PHASE2C evaluation cycle (Q-9.D)."

The structural tension: Q-9.D may surface dependencies on Phase 2C
deliverable quality that Q-9.A's findings would inform. If Phase 3
design genuinely requires deployment-candidate-quality strategies
from Phase 2C, Q-9.D's scoping output may include "Phase 3 deferred
until Q-9.A or alternative produces defensible candidates" — in
which case Q-9.D scoping is itself a forward-pointer back to
Q-9.A/B/C scope.

### §5.4 — Pairwise comparison: Q-9.B vs Q-9.C

| Axis | Q-9.B | Q-9.C |
|---|---|---|
| Bound closure | None direct | Q-S4-13 direct |
| Information gain | HIGH (depth-conditional) | MEDIUM |
| Cost | VARIABLE | BOUNDED |
| Methodology-defect risk | LOW | MEDIUM |
| Forward-progress | MEDIUM | LOW |

**Reasoning**: Q-9.B has higher information gain at appropriate depth,
lower methodology-defect risk, and higher forward-progress register
(informs batch-2 mining design); Q-9.C provides direct bound closure
on Q-S4-13 and bounded implementation cost. The pairwise tradeoff is
"actionable batch-2 mining design + lower defect risk (Q-9.B)" vs
"calibration-question closure + bounded cost (Q-9.C)."

If the highest-leverage register is "batch-2 design input + retrospective
methodology insight," Q-9.B is structurally correct. If the highest-
leverage register is "tighten cohort_a interpretation under varied
calibration," Q-9.C is structurally correct.

### §5.5 — Pairwise comparison: Q-9.B vs Q-9.D

| Axis | Q-9.B | Q-9.D |
|---|---|---|
| Bound closure | None direct | None direct |
| Information gain | HIGH (depth-conditional) | HIGH at meta |
| Cost | VARIABLE | BOUNDED for scoping-only |
| Methodology-defect risk | LOW | LOW |
| Forward-progress | MEDIUM | HIGHEST |

**Reasoning**: Both have low methodology-defect risk and address
non-closure-of-bound questions. Q-9.B addresses "why did batch-1
mining-process produce hybrid quality candidates"; Q-9.D addresses
"does the project progress to Phase 3 or continue PHASE2C cycle."
The pairwise tradeoff is "actionable batch-2 mining-design (Q-9.B)"
vs "phase-progression scoping (Q-9.D)."

Hybrid Q-9.B + Q-9.D is structurally clean: mining retrospective
informs phase-progression scoping (e.g., if batch-1 mining produces
no deployment-quality candidates, Phase 3 design proceeds with
baselines independent of Phase 2C mining; if mining redesign would
plausibly produce deployment-quality candidates, Phase 3 may defer).

### §5.6 — Pairwise comparison: Q-9.C vs Q-9.D

| Axis | Q-9.C | Q-9.D |
|---|---|---|
| Bound closure | Q-S4-13 direct | None direct |
| Information gain | MEDIUM | HIGH at meta / LOW at arc |
| Cost | BOUNDED | BOUNDED for scoping-only |
| Methodology-defect risk | MEDIUM | LOW |
| Forward-progress | LOW | HIGHEST |

**Reasoning**: Q-9.D has higher forward-progress register; Q-9.C
closes Q-S4-13 bound. The pairwise tradeoff is similar to Q-9.A vs
Q-9.D — methodology-evidence base improvement on existing batch-1
vs phase-progression beyond PHASE2C cycle.

### §5.7 — Adjudication framing

The pairwise comparisons do not produce a single dominating direction.
Each candidate has distinct strength registers:

- **Q-9.A**: structural completeness on methodology-evidence base
  (Q-S4-7 closure + statistical-significance literature canonicalization)
- **Q-9.B**: actionable input for batch-2 mining design + lowest
  methodology-defect risk
- **Q-9.C**: bounded-cost closure of Q-S4-13 + complement to Q-9.A
- **Q-9.D**: highest forward-progress register + only direction
  that progresses beyond PHASE2C

**Adjudication question 1**: Is the highest-leverage register
"closing PHASE2C_8.1's methodology-evidence bounds" (favors Q-9.A
and/or Q-9.C and/or hybrid), "informing batch-2 mining design"
(favors Q-9.B), or "progressing to Phase 3" (favors Q-9.D)?

The three registers are structurally distinct. Different operational
priorities favor different candidates.

**Adjudication question 2**: Is single-direction lock the right
register, or is a pairwise hybrid more appropriate?

Hybrid combinations (Q-9.A + Q-9.C closing both bounds; Q-9.B + Q-9.D
addressing mining-and-phase-progression at meta level) expand the
candidate space and have structurally clean compositions. Single-
direction lock has bounded scope but skips structural complementarity.

**Adjudication question 3**: Cost-vs-value tradeoff at 2026-04-29
project state.

Implementation cost varies significantly: Q-9.D scoping-only is
~2-3 sessions; Q-9.A is ~6-8 sessions; Q-9.A + Q-9.C hybrid is
~9-12 sessions. The cost-vs-information-gain tradeoff at current
project state requires Charlie's adjudication; the scoping doc
surfaces the tradeoff but does not pre-resolve it.

**Adjudication question 4**: Pre-registration discipline application.

Q-9.A and Q-9.C both carry methodology-defect risk that requires
pre-registration mitigation (Q-9.A: multiple-comparisons-correction
analyst choices; Q-9.C: calibration variation grid). If selected,
the pre-registration discipline is itself an implementation step
that scoping ratification authorizes; it should not be deferred to
implementation-arc cycle.


## 6. Open scoping decisions surfaced for ratification

The following decisions require Charlie's explicit ratification
before PHASE2C_9 implementation arc cycle initiates. None are
pre-recommended; ratification reasoning appears in scoping cycle
adjudication, not in implementation arc cycle.

### §6.1 — Substantive theme selection

Among Q-9.A / Q-9.B / Q-9.C / Q-9.D, or hybrid combination thereof,
which substantive theme does PHASE2C_9 implementation arc operate
within?

Default operational lean (per §5 reasoning): no single direction
dominates. Charlie's adjudication on §5's four adjudication
questions resolves the substantive theme.

### §6.2 — Scope boundary within selected theme

If Q-9.A selected: DSR + PBO scope-locked, or DSR + PBO + CPCV
conditional? Full 198 vs subset (cohort_a/_filtered/_c only)?
Candidate-level vs cohort-level deliverable register?

If Q-9.B selected: light-touch retrospective vs structured re-
examination vs mining-process redesign scoping?

If Q-9.C selected: which calibration variation axes (sharpe /
total-return / trade-count / per-regime)? Pre-registration grid
size? Inherited-baseline anchor preservation?

If Q-9.D selected: Phase 3 scoping doc structure (target deliverable;
dependency surface; sequencing question; baselines-vs-candidates
feasibility)?

If hybrid: which sub-decisions inherit from each direction's scope
locking?

### §6.3 — Implementation arc session-count expectation

Per CLAUDE.md spend pattern (April 2026: ~$8.65), session-count
forecasts at the scoping register inform timing planning. Q-9.A
forecast: ~6-8 sessions; Q-9.B variable ~2-9 sessions; Q-9.C
~3-4 sessions; Q-9.D scoping-only ~2-3 sessions.

Hybrid combinations roughly additive: Q-9.A + Q-9.C is ~9-12
sessions; Q-9.B + Q-9.D is ~4-12 sessions.

### §6.4 — Pre-registration discipline pre-commitment

If Q-9.A or Q-9.C selected (or hybrid containing either): does
scoping ratification authorize the pre-registration discipline as
implementation-arc obligation, or does pre-registration require
separate ratification cycle?

Lean: pre-registration is intrinsic to the candidate's methodology-
defect risk mitigation, not separable; scoping ratification
authorizes pre-registration as part of the candidate's scope.

### §6.5 — Anti-pre-naming framing forward

PHASE2C_9 scoping cycle deliberates on substantive theme
explicitly; theme selection ratifies through scoping deliberation
register, not through pre-cycle reviewer convergence. Future arcs
inherit the discipline at meta-arc level: substantive theme selection
for new work cycles requires scoping cycle deliberation, not informal
reviewer alignment as substitute.

This document does NOT pre-name PHASE2C_10 or beyond. Selection of
post-PHASE2C_9 next arc is the next scoping cycle's deliberation.


## 7. Out-of-scope / out-of-this-scoping-cycle

The following are explicitly NOT in scope for PHASE2C_9 scoping cycle
ratification:

- **Implementation specifics**: per anti-pre-naming framework, this
  document scopes alternatives but does not pre-commit to
  implementation steps. Implementation arc cycle's spec-drafting
  produces concrete steps.
- **Phase 3 implementation**: Q-9.D's deliverable is scoping-only;
  Phase 3 implementation is downstream of any Q-9.D scoping output.
- **Batch-2 mining process implementation**: Q-9.B's deliverable is
  retrospective + scoping; batch-2 mining-process implementation
  is downstream of any Q-9.B scoping output.
- **DSR/PBO/CPCV literature engagement deliverable**: if Q-9.A
  selected, the implementation arc spec specifies the literature
  engagement scope; this scoping doc does not pre-commit to it.
- **Calibration variation grid pre-specification**: if Q-9.C
  selected, the implementation arc spec specifies the variation
  grid; this scoping doc does not pre-commit to specific axes or
  thresholds.
- **Cross-arc cost optimization**: each candidate's cost forecast
  is at scoping register; implementation arc cycles produce concrete
  session-by-session work distribution.

The scoping cycle's primary deliverable is the substantive theme
ratification. Implementation specifics derive downstream from the
ratified theme.


## 8. Scoping cycle next steps

After this document commits, the scoping cycle adjudication phase
initiates:

1. **Charlie's review of the four candidates + decision criteria
   + pairwise comparisons**: scoping cycle's primary deliberation
   surface. Reading this document with fresh eyes; identifying which
   candidate(s) align with current project priority register.
2. **Adjudication on §5's four adjudication questions**: which
   register is highest-leverage; single-direction vs hybrid; cost-
   vs-value tradeoff; pre-registration discipline.
3. **Substantive theme ratification**: selection of Q-9.A / Q-9.B /
   Q-9.C / Q-9.D / hybrid as PHASE2C_9 implementation arc theme.
4. **Open-decisions resolution at §6**: scope boundary; session-count
   expectation; pre-registration pre-commitment.
5. **Spec drafting cycle authorization**: post-ratification, spec
   drafting cycle initiates with concrete implementation steps per
   PHASE2C_8.1 → 1e85d1d precedent format.

Until ratification, implementation arc cycle is held; spec drafting
does not initiate. Anti-pre-naming framework requires deliberation
register completion before downstream cycles initiate.


## 9. Cross-references

- PHASE2C_8.1 closeout: `docs/closeout/PHASE2C_8_1_RESULTS.md`
  (commit `69e9af9`; tag `phase2c-8-1-multi-regime-extended-v1`)
- PHASE2C_8.0 scoping precedent: `docs/phase2c/PHASE2C_8_SCOPING_DECISION.md`
  (commit `f223316`)
- METHODOLOGY_NOTES.md: `docs/discipline/METHODOLOGY_NOTES.md`
  (commit `8154e99`; §10 anti-pre-naming + §11 closeout-assembly +
  §13 parallel-implementation + §14 bidirectional dual-reviewer +
  §15 anchor-list discipline references)
- CLAUDE.md Phase Marker: project state at PHASE2C_8.1 closeout
  (commit `bdbc64d` reconciled at `8154e99` via PHASE2C_8.1 closeout
  fold)
- Spec §10.7 + Q-FS4 strictness inheritance:
  `docs/phase2c/PHASE2C_8_1_PLAN.md` (PHASE2C_8.1 spec; commit
  `1e85d1d`)
- Q-S4-7 + Q-S4-13 register entries: PHASE2C_8.1 closeout §10.1
  (canonical register table)
- §11.1 / §11.2 / §11.3 / §11.4 forward signals: PHASE2C_8.1 closeout
  §11
