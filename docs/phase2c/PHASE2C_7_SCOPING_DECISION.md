# PHASE2C_7 Scoping Decision

## 1. Scope and verdict

**This document decides what empirical question PHASE2C should
answer next, after PHASE2C_6's negative selection-power finding.
It does not implement; implementation is deferred to PHASE2C_7.1
once Charlie selects a path from §3.**

**Project state at PHASE2C_7 scoping (2026-04-27).**

- Canonical main: `origin/main` at commit `f344a0e`
- Tags on main: `wf-corrected-v1` (corrected WF engine fix at
  commit `eb1c87f`), `phase2c-6-evaluation-gate-v1` (PHASE2C_6
  arc completion at `f344a0e`)
- PHASE2C_6 closeout:
  [`docs/closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md`](../closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md)
- PHASE2C_6 plan:
  [`docs/phase2c/PHASE2C_6_EVALUATION_GATE_PLAN.md`](PHASE2C_6_EVALUATION_GATE_PLAN.md)
- Methodology principles in force:
  [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  §1-§7
- CLAUDE.md Phase Marker reflects PHASE2C_6 closure with
  PHASE2C_7+ scoping decision pending

**PHASE2C_6 finding recap (bounded one-paragraph form).**

In batch `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`, against the 2022
regime holdout 4-criterion AND-gate, the corrected WF gate
(`wf_test_period_sharpe > 0.5`) did not enrich for holdout
survival. Audit-only candidates survived at a higher rate
(12/154 = 7.79%) than primary candidates (1/44 = 2.27%). This
finding is bounded to this batch, this regime, and this gate
calibration; it does not establish methodology-level conclusions
about WF as a methodology, about candidate alpha quality, or about
deployment readiness for any candidate. Full bounded interpretation
is in PHASE2C_6 closeout §6 ("What this finding does NOT
establish").

**What PHASE2C_7 is NOT.**

- **Not a re-litigation of PHASE2C_6.** PHASE2C_6's empirical
  results are sealed. PHASE2C_7 inherits them as input, not as
  open questions to re-examine.
- **Not an implementation plan.** PHASE2C_7 is a scoping decision
  enumerating candidate paths and recommending one. Implementation
  details (script structure, evaluation parameters, calibration
  sets, closeout content) are deferred to PHASE2C_7.1 once a path
  is selected.
- **Not a methodology amendment.**
  `docs/discipline/METHODOLOGY_NOTES.md` §1-§7 are project-standing
  principles. PHASE2C_7 applies them; it does not revise them.
  New methodology principles surfaced during PHASE2C_7 work are
  captured as a follow-up update (same hybrid handling as
  PHASE2C_6's §10 + commit `536f737`).
- **Not a forward decision on DSR/CPCV/MDS investment, candidate
  promotion, or test-split consumption.** These remain explicit
  non-decisions per PHASE2C_6 closeout §9.

**Document structure.**

§2 enumerates the four open empirical questions inherited from
PHASE2C_6 §9. §3 enumerates four candidate next-arc paths (A
multi-regime survivors, B multi-regime full-population, C
gate-calibration variation, D DSR despite n=1) with uniform
six-subfield comparison. §4 names decision criteria including a
Question×Path matrix. §5 carries a substantive lean (Path B) with
seven-rung reasoning ladder; final selection deferred to Charlie's
explicit go signal. §6 enumerates conditional in-scope deliverables
per path and universal out-of-scope items. §7 names
project-discipline patterns carried forward from PHASE2C_6. §8
provides one-paragraph PHASE2C_7.1 implementation skeletons per
path.

## 2. Open empirical questions inherited from PHASE2C_6 §9

PHASE2C_6's closeout §9 enumerates four open empirical questions
that the within-batch evaluation could not answer. Each is
restated here in bounded form, with what evidence would answer it
and what evidence the current data does NOT supply. The four
questions structure the path comparison in §3 — each candidate
path is evaluated against which of these questions it addresses
and which it leaves open.

**Q1 — Does the within-batch anti-selection generalize beyond
2022, or is it 2022-specific?**

PHASE2C_6 establishes that within batch b6fcbf86, against the 2022
regime holdout, the corrected WF gate (`wf_test_period_sharpe >
0.5`) did not enrich for holdout survival; the audit-only pool
survived at a higher rate (12/154 = 7.79%) than the primary pool
(1/44 = 2.27%). Whether this anti-selection holds against other
regimes is empirically open. Two specific sub-explanations
(regime-mismatch and pattern-overfit, named in PHASE2C_6 closeout
§5's mechanism-pointer paragraph) would make different forward
predictions: regime-mismatch predicts that a regime more similar
to the 2020-2021 walk-forward training windows would restore
selection power; pattern-overfit predicts that anti-selection
persists across regimes.

*What evidence would answer it.* Multi-regime evaluation. Same 198
candidates evaluated against an additional regime (e.g., 2024
validation per `config/environments.yaml`'s v2 split) produces a
candidate-aligned comparison: the 2022 anti-selection rate vs the
new-regime anti-selection rate, with the candidate population held
constant. If the anti-selection persists, evidence for systematic
effect (pattern-overfit-leaning); if it diminishes or reverses,
evidence for regime-coupled effect (regime-mismatch-leaning).

*What the current data does NOT supply.* Any direct evidence about
selection-power against regimes other than 2022. PHASE2C_6 ran
against 2022 only by design (single-regime evaluation gate per
its scoping document).

**Q2 — Is the AND-gate (WF > 0.5 AND holdout_passed) empirically
meaningful as a selection criterion, or is its dual-pass population
too small to be informative?**

PHASE2C_6's primary survivor population — the dual-pass population,
candidates passing both the WF gate AND the 2022 holdout — is n=1
(`bf83ffec`, the borderline calendar_effect candidate). With n=1,
no comparative claim about AND-gating's selection power can be
made — the dual-pass population is too small to support deflation,
significance testing, or comparative analysis. Whether AND-gating
becomes empirically meaningful at larger sample sizes is open.
This question concerns within-regime AND-gating, not cross-regime
survivorship intersections.

*What evidence would answer it.* A larger candidate population
evaluated against any single regime where the WF gate AND that
regime's holdout produces n >> 1, enabling within-population
statistical claims about the dual-pass cohort relative to
single-pass cohorts. Q2 is a within-regime conjunction question;
cross-regime intersection (passing 2022 AND 2024) is a different
question and does not address Q2.

*What the current data does NOT supply.* Any meaningful sample
size for within-2022 AND-gate analysis. The n=1 result is not a
finding about AND-gating; it is a finding that this batch's
intersection happens to be 1.

**Q3 — Is the 4-criterion gate's trade-count threshold (`total_trades
>= 5`) appropriately calibrated, or does it reject candidates that
generated profitable but infrequent signals?**

PHASE2C_6's near-miss cluster identified four candidates
(`06c3b4a2`, `d8e92ae4`, `e12477c9`, `b4dbd6c5`) that exhibited
positive 2022 holdout Sharpe with in-bound drawdown and return,
failing only the trade-count criterion (1-4 trades). Whether the
n=5 minimum is the right threshold for this kind of work is
empirically open. The threshold's purpose (preventing spurious
low-sample passes) is real, but whether 5 is the correct threshold
or whether 1-4 trades represents genuine infrequent alpha is
underdetermined by this batch.

*What evidence would answer it.* Either (a) gate-calibration
variation against the same candidates and same regime to test how
the headline finding shifts as the trade-count threshold varies,
or (b) longer holdout windows that increase opportunity for trade
realization in low-frequency candidates, allowing them to
accumulate trade counts that satisfy any reasonable threshold.
(a) is cheaper and more direct; (b) is more informative about
whether the candidates' alpha persists at longer time horizons.

*What the current data does NOT supply.* Any evidence about how
the headline finding shifts under different trade-count thresholds.
PHASE2C_6 used the canonical n=5 threshold from
`config/environments.yaml` and did not vary it.

**Q4 — What do the 12 audit-only survivors represent
diagnostically?**

PHASE2C_6's audit-only survivors (12 candidates that passed the
2022 holdout despite being rejected by the corrected WF gate at
`wf_test_period_sharpe <= 0.5`) are not strategy recommendations.
PHASE2C_6 closeout §9's fourth open question explicitly framed
them as diagnostic material: empirical evidence about what the
corrected WF metric and the 2022 regime holdout each select for,
and how those selection criteria diverge. Whether these candidates
generalize to other regimes, whether they share structural
properties that distinguish them from the WF-rejected
non-survivors, and whether any pre-registered question about them
is worth answering empirically is open.

*What evidence would answer it.* Multi-regime evaluation of the
12 audit-only survivors specifically (Path A's scope) tests
whether their 2022 survival was regime-orthogonal or
regime-specific. If most also pass 2024, that is necessary but
not sufficient evidence for regime-orthogonal alpha and would
require additional regimes to establish further (potentially
actionable as a hypothesis for further investigation under a
pre-registered question). If few pass 2024, evidence that 2022
survival was 2022-specific (diagnostic value preserved but not
actionable).

*What the current data does NOT supply.* Any second-regime
evidence about these 12 candidates. PHASE2C_6 evaluated them
against 2022 only.

**Note on Q4 discipline.** PHASE2C_6 closeout §9 explicitly
flagged that "treating them as candidates for further study would
require a separate pre-registered question, not post-hoc promotion
because they survived 2022." This discipline carries forward to
PHASE2C_7+: any path that evaluates the 12 audit-only survivors
must do so under a pre-registered question (e.g., "do these 12
candidates pass 2024 validation?"), not as a fishing expedition
to find candidates that look promising across regimes.

## 3. Candidate next-arc paths

Four paths are enumerated below. Each is described using the same
six subfields to enable side-by-side comparison: scope (what the
path executes), information value (what evidence it generates),
cost (compute, time, API spend), what it answers (which open
questions from §2 it addresses), what it does NOT answer (questions
that remain open after the path completes), dependency
(upstream/downstream of which other paths in the evidence graph).

### Path A — Multi-regime evaluation of the 13 PHASE2C_6 survivors against 2024 validation

**Scope.** Evaluate the 13 candidates that passed the 2022 regime
holdout (1 primary survivor + 12 audit-only survivors, enumerated
in PHASE2C_6 closeout §7) against the 2024 validation regime per
`config/environments.yaml`'s v2 split. Same evaluation gate as
PHASE2C_6 (4-criterion AND-gate, same thresholds). New artifact
attestation domain extension or new run_id under existing
`single_run_holdout_v1` domain (depending on whether 2024 evaluation
is treated as the same attestation type as 2022).

**Information value.** Tells us whether the 13 candidates that
passed the 2022 holdout are 2022-specific or generalize. If most
of the 13 also pass 2024, the 2022 survival was at least partly
regime-orthogonal. If few or none pass 2024, the 2022 survival was
likely 2022-specific. Suggestive evidence about the regime-mismatch
vs pattern-overfit mechanism question for the survivor cohort
only, not at population level.

**Cost.** Minimal. 13 candidates × ~1.2s/candidate ≈ 16 seconds
wall-clock for the evaluation run. No API spend. Plus closeout and
review overhead similar to PHASE2C_6 (~3-4 hours of drafting +
adjudication).

**What it answers.** Q1 (does within-batch anti-selection
generalize) — partially, for the survivor cohort only. Q4 (what do
the audit-only survivors represent diagnostically) — substantially,
by showing whether they pass another regime's gate.

**What it does NOT answer.** Q1 for the full population (the 185
non-survivors are not evaluated, so we don't know if any of them
would pass 2024 even if some 2022-survivors fail 2024). Q2
(AND-gate empirical underdetermination) — not addressed because
n=1 dual-pass population from PHASE2C_6 doesn't change. Q3
(trade-count threshold calibration) — not addressed.

**Dependency.** Independent of paths C and D. Strict subset of
Path B; if Path B runs, Path A's evidence is contained within it.

### Path B — Multi-regime evaluation of all 198 candidates against 2024 validation

**Scope.** Evaluate all 198 batch candidates against the 2024
validation regime, mirroring PHASE2C_6's audit_v1 universe-scope
but with regime swapped from 2022 to 2024. Same evaluation gate
(4-criterion AND-gate). Same producer script
(`scripts/run_phase2c_evaluation_gate.py`) with `--universe audit`
flag and a 2024-regime configuration. Optionally include a
pre-specified trade-count filter (e.g. ≥20 or ≥50) as a secondary
analysis pass; this is not a separate path, it is a robustness
check on the primary full-population result, with the threshold
choice committed at PHASE2C_7.1 implementation rather than left
ad hoc.

**Information value.** Tells us whether the WF gate's
anti-selection from PHASE2C_6 is 2022-specific or systematic
across regimes. The candidate-aligned comparison (same 198
candidates, two regimes) preserves the WF × holdout matrix
needed to recompute selection-power against 2024 directly.
Distinguishes regime-mismatch from pattern-overfit at the
population level rather than the survivor-only level.

**Cost.** Moderate. 198 candidates × ~1.2s/candidate ≈ 4 minutes
wall-clock (per PHASE2C_6 audit run timing). No API spend (local
backtest evaluation). Plus closeout and review overhead similar to
PHASE2C_6 (~6-10 hours of drafting + adjudication, larger than A
because the comparative analysis is more substantive).

**What it answers.** Q1 (does within-batch anti-selection
generalize) — directly, for both populations. Q4 (audit-only
survivors as diagnostic material) — by extending diagnostic
analysis to a second regime. Partial input to Q2 (AND-gate
empirical underdetermination): Path B produces a 2024-regime
dual-pass population (WF gate AND 2024 holdout), independent of
and comparable to PHASE2C_6's 2022 dual-pass count of 1. Two
independent single-regime dual-pass populations, not a
cross-regime intersection.

**What it does NOT answer.** Q3 (trade-count threshold
calibration) — not directly addressed unless the in-path filter
sub-decision is exercised. Mechanism distinction beyond two
regimes (a third regime would help further but is out of scope
here).

**Dependency.** Superset of Path A. Upstream of Path C —
gate-calibration variation analysis (Path C) is more
informationally valuable after multi-regime evidence is
established, because gate calibration's selection power may differ
across regimes.

### Path C — Revisit the WF selection criterion via gate-calibration variation

**Scope.** Re-run the PHASE2C_6 evaluation against the same 198
candidates (same 2022 regime), varying the WF gate calibration
(threshold, criterion structure). Example calibrations: thresholds
at 0.0, 0.25, 0.75, 1.0 instead of 0.5; rank-based filters (top-N
by WF Sharpe); multi-criterion combinations (WF Sharpe AND WF
return AND WF drawdown). Each variation produces a new primary
universe whose holdout pass-rate can be compared against
PHASE2C_6's. Exact calibration set deferred to PHASE2C_7.1 if
Path C is chosen.

**Information value.** Tells us whether PHASE2C_6's anti-selection
finding is specific to the `wf_test_period_sharpe > 0.5`
calibration or persists across calibrations. If a different
calibration restores selection power, the finding is calibration-
specific; if no calibration restores selection power, the finding
is calibration-robust within 2022.

**Cost.** Low to moderate depending on number of calibrations
tested. Each calibration variation is essentially free
computationally (data already exists; only the partition logic
changes). Closeout overhead similar to PHASE2C_6 (~4-6 hours).

**What it answers.** Q3 (trade-count threshold calibration) —
directly, if calibration variations include trade-count
modifications. Partial input to Q1 (does within-batch
anti-selection generalize) — for the calibration dimension
specifically, not the regime dimension.

**What it does NOT answer.** Q1 across regimes (still 2022 only).
Q2 (AND-gate empirical underdetermination at n=1) — not
addressed. Mechanism question (regime-mismatch vs pattern-overfit)
— calibration variation can distinguish calibration-coupled vs
calibration-invariant effects within 2022, but cannot disambiguate
regime-mismatch from pattern-overfit when the effect is
calibration-invariant.

**Dependency.** Independent of Paths A and B in scope but
informationally downstream of Path B. Without multi-regime
evidence (Path B), calibration variation cannot distinguish
whether observed anti-selection is regime-specific or
calibration-induced, making its conclusions structurally
ambiguous. If Path B runs first and shows anti-selection persists
across regimes, Path C's calibration variation becomes more
meaningful (calibration-invariance of a systematic effect). If
Path B is skipped, Path C's findings remain ambiguous between
"calibration is fine, this regime is hostile" and "calibration is
the problem."

### Path D — Continue Option A with DSR despite n=1

**Scope.** Build DSR (Deflated Sharpe Ratio) infrastructure as
originally planned in PHASE2C_6's closeout §9 first decision,
applied to PHASE2C_6's primary survivor population (n=1 dual-pass:
`bf83ffec`). The DSR computation deflates observed Sharpe against
a null distribution accounting for multiple-testing exposure.

**Information value.** Minimal under current conditions (n=1
dual-pass). Produces infrastructure but no meaningful batch-level
inference.

**Cost.** High. DSR infrastructure is non-trivial (multiple-testing
correction logic, null distribution estimation, integration with
existing experiment registry). 1-2 weeks of design + implementation
+ test work. No API spend.

**What it answers.** Q2 (AND-gate empirical underdetermination) —
mathematically pathological to address with n=1. The path's stated
question would technically be addressed by producing a DSR-deflated
Sharpe for `bf83ffec`, but the deflation is degenerate at n=1.

**What it does NOT answer.** Q1 (regime generalization) — not
addressed; same regime, same candidates. Q3 (trade-count threshold)
— not addressed. Q4 (audit-only survivors as diagnostic) — DSR
on the 1 primary survivor doesn't characterize the 12 audit-only
survivors.

**Dependency.** Independent of A, B, C in scope; informationally
downstream of all three. DSR is most useful when a meaningful
population to deflate exists, which this batch does not supply.
Running Path D before Path A or B means committing infrastructure
work without knowing if the population PHASE2C_7+ produces will
be large enough for DSR to be informative.

## 4. Decision criteria

The four paths in §3 differ along several dimensions that matter
for choosing among them. This section names the criteria
explicitly, then provides a Question × Path matrix that maps each
of §2's open questions to which paths address it and how.

**Per-path expected observables.**

For each path, what specific empirical outputs would the path
produce that subsequent reasoning could attach to? The criterion
is testability — paths whose outputs are well-specified are easier
to evaluate against the open questions; paths whose outputs are
diffuse produce ambiguous evidence.

- **Path A:** 13 per-candidate holdout summaries against 2024;
  aggregate pass-rate (k of 13); per-candidate hd_sh, dd, ret,
  trades on 2024; survivor-overlap with PHASE2C_6 2022 survivors.
- **Path B:** 198 per-candidate holdout summaries against 2024;
  aggregate pass-rate (k of 198); primary-vs-audit-only pass-rate
  comparison for 2024; candidate-aligned 2022 vs 2024 distribution
  shift; rank stability of WF Sharpe vs 2024 holdout Sharpe across
  the 198. (Optional secondary pass: same observables on the
  trade-count-filtered subset.)
- **Path C:** Per-calibration aggregate pass-rates against 2022
  (k of N where N depends on calibration); rank stability across
  calibration variants; identification of any calibration that
  restores selection power.
- **Path D:** DSR-deflated Sharpe for `bf83ffec` (single
  observation); DSR infrastructure code + tests.

**Failure modes per path.**

What result would invalidate the path's usefulness? Naming this
explicitly forces honesty about what each path can and cannot
prove.

- **Path A:** All 13 fail 2024 → cohort was 2022-specific; Q1 for
  the cohort is resolved toward pattern-overfit-leaning, but Q1
  for the population remains open. All 13 pass 2024 → cohort
  survives both 2022 and 2024; Q1 for the cohort is resolved
  toward survival across these two regimes specifically, which is
  necessary but not sufficient evidence for regime-orthogonal
  alpha and would require additional regimes to establish further
  (potential pre-registered follow-up hypothesis), but Q1 for the
  population remains open. Path A cannot fully resolve Q1 either
  way.
- **Path B:** Primary-vs-audit-only relationship in 2024 mirrors
  2022 (audit-only > primary) → anti-selection is systematic, not
  2022-specific. Relationship inverts in 2024 (primary > audit-only)
  → anti-selection was 2022-specific. Relationship is null in
  2024 — two interpretations to distinguish empirically: (a) low
  absolute pass rates in both pools with similar primary-vs-
  audit-only ratio → 2024 regime is hostile to the population
  overall, separate from any gate selection effect; (b) moderate-
  to-high pass rates in both pools with similar primary-vs-
  audit-only ratio → WF gate has no discernible selection-power
  effect against 2024, neither anti nor pro. Both are informative
  for PHASE2C_7+ scoping but suggest different next-arc directions.
- **Path C:** All calibrations show similar anti-selection →
  calibration-invariant within 2022 (Q3 partially answered in
  one direction). Some calibration restores selection power →
  calibration-coupled (Q3 partially answered in other direction).
  Either is informative within 2022, but the regime-vs-calibration
  ambiguity persists without Path B.
- **Path D:** Produces DSR module + DSR-deflated Sharpe for n=1.
  No failure mode in the empirical sense — the result is the
  result. The path's weakness is upstream: the n=1 input is the
  problem, not the deflation logic.

**Cost dimensions.**

Compute is not the binding cost on any path; review and closeout
overhead is. This is a project-discipline observation from
PHASE2C_6 (which had ~4 minutes wall-clock for the audit run but
~6-10 hours of drafting and adjudication before the closeout
sealed). The right cost framing is total work-cycle hours, not
just compute time.

| path | compute | review/closeout | total work-cycle |
|------|--------:|----------------:|-----------------:|
| A | ~16 sec | ~3-4 hours | ~3-4 hours |
| B | ~4 min | ~6-10 hours | ~6-10 hours |
| C | trivial | ~4-6 hours | ~4-6 hours |
| D | n/a | 1-2 weeks | 1-2 weeks |

**Methodological propriety constraints.**

- **Touched-once discipline.** The 2025 test split is preserved
  touched-once across all four paths. No path may evaluate
  against 2025. (Detailed in §6 out-of-scope.)
- **Candidate-aligned comparison.** For the §5 lean (Path B), the
  comparison preserves the variable of interest (regime) by holding
  the candidate population constant. Paths A, C, D do not preserve
  this discipline — A reduces the population, C varies the
  calibration, D evaluates a single-candidate population.
- **Pre-registered questions.** Per PHASE2C_6 §9 discipline carry-
  forward, the 12 audit-only survivors must not be promoted
  post-hoc. Any path that evaluates them must do so under a
  pre-registered question, named at scoping rather than chosen
  after seeing results.

**Question × Path matrix.**

| Question | Path A | Path B | Path C | Path D |
|----------|:------:|:------:|:------:|:------:|
| **Q1** Does within-batch anti-selection generalize beyond 2022? | partial (cohort only, n=13) | direct (population, n=198) | none (same regime) | none (same regime) |
| **Q2** Is AND-gating empirically meaningful at scale? | none (n=1 unchanged) | partial (independent 2024 dual-pass population) | none | partial-degenerate (DSR at n=1) |
| **Q3** Is the trade-count threshold appropriately calibrated? | none | partial (if filter sub-decision exercised) | direct (calibration variation) | none |
| **Q4** What do the 12 audit-only survivors represent diagnostically? | direct (cohort's 2024 fate) | direct (cohort's 2024 fate within full comparative analysis) | none | none |

Cell legend: **direct** = path's primary purpose is answering this question; **partial** = path produces some evidence but doesn't fully resolve; **partial-degenerate** = path technically addresses but mathematical/empirical conditions render the answer uninformative; **none** = path does not address this question.

**Cross-reading the matrix.**

- Q1 is addressed by Paths A and B; B more fully than A. Paths C
  and D do not address Q1.
- Q2 is partially addressed by Paths B and D; Path A does not
  change the within-2022 n=1 dual-pass condition. B's contribution
  is the strongest (independent 2024 dual-pass population); D's
  is degenerate.
- Q3 is addressed primarily by Path C; B partially if the
  filter sub-decision is exercised.
- Q4 is addressed by Paths A and B (with B containing A's
  evidence as a strict subset).

**Decision summary.** The matrix shows Path B's structural
dominance for Q1 (the upstream question per §5 Rung 1) and its
partial-or-better coverage of Q2 and Q4. Path B does not address
Q3 directly without the optional filter sub-decision; Q3 remains
the strongest case for Path C as a follow-up arc after Path B
resolves Q1.

## 5. Recommendation

**We lean Path B (multi-regime evaluation of all 198 candidates
against 2024 validation) as the primary mechanism test, with the
pre-specified trade-count filter sub-decision (Path B's secondary
robustness check) deferred to PHASE2C_7.1 implementation.
Path A is a strict subset and does not warrant separate
execution. Path C is informationally downstream of Path B and is
deferred. Path D is structurally weak under current conditions
and is deferred. Final selection deferred to Charlie's explicit
go signal.**

The reasoning ladder below walks the trade-off explicitly. Each
rung is a structural argument grounded in the §3 path comparison
and the §2 question definitions.

**Rung 1 — Path B addresses the most upstream open question (Q1).**

§2's Q1 (does within-batch anti-selection generalize beyond 2022)
is the question whose answer is upstream of the others under this
batch's evidence state. If Q1 resolves toward "anti-selection is
2022-specific," PHASE2C_7+ scoping shifts toward gate calibration
revisitation (Path C) or toward generation work (deferred) rather
than further multi-regime evaluation. If Q1 resolves toward
"anti-selection persists across regimes," the questions about WF
metric replacement and AND-gate calibration become differently
weighted. Resolving Q1 first is the highest-leverage information
acquisition.

Path B addresses Q1 directly at population level. Path A addresses
Q1 partially (survivor cohort only, n=13). Paths C and D do not
address Q1 at all. Path B is the only path that produces
population-level evidence on the most upstream question.

**Rung 2 — Path B preserves the WF × holdout matrix needed for
candidate-aligned comparison.**

PHASE2C_6's load-bearing finding is the comparative anti-selection
across the 198-candidate population. Reproducing or refuting that
finding under a different regime requires the same 198-candidate
population evaluated against the new regime — the candidate-aligned
comparison preserves the variable of interest (regime) without
confounding with population changes. Path B explicitly maintains
this discipline. Path A reduces the population to 13 (loses
non-survivors). Paths C and D vary calibration or scope
respectively, neither of which is candidate-aligned for the
2022 vs 2024 comparison.

**Rung 3 — Path A is a strict subset of Path B; running A
separately is information-redundant.**

Path A's evidence (whether the 13 survivors generalize to 2024) is
contained within Path B's output. If Path B runs, the 13-survivor
sub-analysis can be performed as a slice of Path B's results
without an independent run. Running A first and then B duplicates
work; running B alone produces both A's evidence and the additional
185-candidate evidence Path A doesn't supply.

**Rung 4 — Path C's information value is structurally downstream
of Path B.**

Calibration variation at fixed regime (Path C) cannot distinguish
calibration-induced anti-selection from regime-induced
anti-selection. Without multi-regime evidence (Path B), Path C's
findings carry the structural ambiguity §3 names: "calibration is
fine, this regime is hostile" vs "calibration is the problem"
remain indistinguishable. Path B resolves enough of this ambiguity
to make Path C's calibration variation meaningfully interpretable
in a follow-up arc.

**Rung 5 — Path D is mathematically pathological at n=1.**

DSR (Deflated Sharpe Ratio) infrastructure is methodologically
valid, but its application to PHASE2C_6's n=1 dual-pass population
produces no meaningful batch-level inference. Building DSR
infrastructure now commits 1-2 weeks of work to produce a
deflation-engine that has no usable input from this batch. The
infrastructure may be valuable in future arcs with larger
populations, but PHASE2C_7+ scoping should not commit
infrastructure work to address a question (Q2) that this batch
cannot answer at any cost.

**Rung 6 — Path B's cost is acceptable and bounded.**

Compute cost is approximately 4 minutes wall-clock (per PHASE2C_6
audit run timing for 198 candidates). No API spend. Drafting and
review overhead is similar to PHASE2C_6 (~6-10 hours), driven by
the comparative analysis depth rather than the compute work.
Total arc cost is manageable within a single work cycle.

Path A's cost is lower (~16 seconds compute, ~3-4 hours review)
but with strictly less information. Cost-information ratio favors
Path B by a wide margin.

**Rung 7 — The trade-count filter sub-decision (Path B's secondary
robustness check) is recommended but not mandatory; its threshold
is not yet pinned.**

PHASE2C_6's near-miss cluster (4 candidates with positive 2022
holdout Sharpe but trades < 5) raises two related issues: whether
the holdout trade-count gate is too strict for infrequent but
profitable candidates, and whether Sharpe-based pass-rates are
reliable when trade counts are low. Path B's secondary analysis
pass — re-running the anti-selection calculation on a filtered
subset (e.g., `total_trades >= 20` in the 2024 holdout) — is
recommended as a pre-specified secondary pass, with the threshold
pinned at PHASE2C_7.1 implementation rather than chosen post-hoc.
The pre-specification discipline (no ad hoc threshold choice after
seeing the primary result) is the non-negotiable; the filter pass
itself is recommended.

**Bounded recommendation.**

Path B is the structurally dominant choice under the current
evidence state. The lean is substantive, not hedged: Path B
addresses Q1 (the upstream question), preserves candidate
alignment for the comparative claim, contains Path A's evidence
as a strict subset, is upstream of Path C in the dependency graph,
and avoids Path D's n=1 pathology. The arc cost is bounded and
within a single work cycle.

Final selection deferred to Charlie's explicit go signal. If
Charlie selects a different path, the reasoning ladder above is
the substantive trade-off the alternative selection should
address. If Charlie approves Path B, the next deliverable is the
PHASE2C_7.1 implementation specification with the trade-count
filter threshold pinned if the filter pass is included.

## 6. In-scope and out-of-scope for PHASE2C_7

Scope is bound by the path Charlie selects. This section enumerates
in-scope and out-of-scope items conditionally on path selection,
plus universal constraints that apply to all paths.

**In-scope (conditional on path selection).**

- **If Path A is selected:** Multi-regime evaluation of the 13
  PHASE2C_6 holdout-survivors against 2024 validation.
  Per-candidate holdout summaries, aggregate pass-rate, cohort-vs-
  PHASE2C_6 survivor overlap analysis. Implementation artifact at
  PHASE2C_7.1.
- **If Path B is selected:** Multi-regime evaluation of all 198
  PHASE2C_6 candidates against 2024 validation. Per-candidate
  holdout summaries, aggregate pass-rate, candidate-aligned
  2022-vs-2024 comparative analysis, primary-vs-audit-only
  pass-rate comparison for 2024, optional secondary trade-count-
  filtered pass with pre-specified threshold. Implementation
  artifact at PHASE2C_7.1.
- **If Path C is selected:** Gate-calibration variation against
  the same 198 PHASE2C_6 candidates and 2022 regime, with
  calibration set pinned at PHASE2C_7.1. Per-calibration aggregate
  pass-rates, rank stability across calibration variants.
  Implementation artifact at PHASE2C_7.1.
- **If Path D is selected:** DSR (Deflated Sharpe Ratio)
  infrastructure design + implementation + tests. The
  infrastructure is applied to PHASE2C_6's n=1 dual-pass population
  for completeness, with explicit acknowledgment that the n=1
  application is degenerate and produces no meaningful batch-level
  inference (per §3 Path D scope and §5 Rung 5). Implementation
  artifact at PHASE2C_7.1.

**Universal constraints (apply to all paths).**

- **Closeout discipline.** Whichever path is selected, the work
  cycle ends with a closeout document at
  `docs/closeout/PHASE2C_7_<path-suffix>_RESULTS.md` following the
  PHASE2C_6 closeout pattern (bounded framing, explicit non-claims,
  empirically-grounded findings, methodology principles applied).
- **Lineage discipline.** Section RS of
  `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md` applies to all
  paths consuming corrected-engine artifacts. Path B and Path C
  consume corrected-engine WF outputs and produce single-run
  holdout artifacts; existing `check_evaluation_semantics_or_raise`
  guard applies. Path A consumes corrected-engine WF outputs as
  filtered-by-PHASE2C_6-survivors and produces single-run holdout
  artifacts; same guard applies. Path D consumes the single-run
  holdout artifacts under the same attestation domain.
- **Methodology principles application.**
  `docs/discipline/METHODOLOGY_NOTES.md` §1-§7 apply throughout
  PHASE2C_7, particularly §1 (empirical verification), §3 (regime-
  aware calibration), §4 (scaling-step discipline if the chosen
  path involves multi-step evaluation), and §7 (asymmetric
  confidence reporting if results span different sample sizes).

**Out-of-scope (applies to all paths).**

- **2025 test split is preserved touched-once across all four
  paths; no path may evaluate against 2025.** The 2025 test split
  per `config/environments.yaml`'s touched-once discipline is
  reserved for final evaluation per project-standing methodology.
  Touching 2025 during PHASE2C_7 would burn the test-split's
  one-shot status on a question the validation split (2024) can
  answer.
- **Theme-targeted candidate generation is deferred.**
  Generation paths informed by PHASE2C_6's by-theme findings
  (calendar_effect's higher pass rate, mean_reversion's
  engaged-and-lost mode, volatility_regime's non-engagement mode,
  momentum and volume_divergence's within-theme inversion) are
  not in scope for PHASE2C_7. Candidate-generation paths are
  deferred until PHASE2C_7's evaluation work informs what
  generation should target. Premature generation work risks
  encoding 2022-specific patterns into proposer prompts before
  multi-regime evidence about which patterns generalize is
  available.
- **DSR execution beyond design discussion is out-of-scope for
  Paths A, B, C.** Only Path D explicitly engages DSR
  infrastructure work. Other paths may surface DSR-relevant
  observations (e.g., dual-pass population size for Q2), but
  building DSR infrastructure is not part of A/B/C scope.
- **Methodology amendments not empirically motivated by the
  chosen path are out-of-scope.** Adding new METHODOLOGY_NOTES.md
  sections, revising the 4-criterion gate definition, or
  modifying lineage discipline beyond what the chosen path's
  empirical findings demonstrate is out-of-scope. Discipline
  lessons surfaced during PHASE2C_7 work can be captured as a
  follow-up update to METHODOLOGY_NOTES.md after the closeout,
  not as part of the closeout itself (same hybrid handling as
  PHASE2C_6).
- **Audit-only post-hoc promotion is out-of-scope.** PHASE2C_6's
  12 audit-only survivors must not be promoted as actionable
  candidates based on PHASE2C_7 results without a pre-registered
  question framing the investigation. If Path A or Path B finds
  that some audit-only survivors also pass 2024 holdout, this
  is diagnostic evidence about gate divergence between WF and
  the regime holdout, not evidence that the candidates should
  be advanced beyond the pre-registered PHASE2C_7 diagnostic
  evaluation into test, paper-trading, or live work. The
  pre-registered-question discipline from PHASE2C_6 §9 carries
  forward.

**Note on closeout shape.**

The PHASE2C_7 closeout will follow the PHASE2C_6 closeout's
11-section structure (scope/verdict, lineage integrity, primary
result, audit/full-population result, selection-power adjudication
or equivalent for the chosen path, non-claims, survivor
enumeration if applicable, by-theme interpretation if applicable,
implications for PHASE2C_8+, methodology-discipline observation,
references and reproducibility). Adjustments to the structure for
the specific path chosen are appropriate at PHASE2C_7.1 closeout
drafting.

## 7. Required discipline carry-forward from PHASE2C_6

The PHASE2C_6 arc surfaced and codified discipline patterns that
PHASE2C_7 inherits as standing project context. This section
enumerates the patterns and the specific PHASE2C_7 application
of each. These are project-discipline principles independent of
which path Charlie selects; §6 names path-conditional scope
obligations, while §7 names path-independent discipline patterns.

**1. Audit-only survivors are diagnostic material, not strategy
recommendations.**

PHASE2C_6 closeout §9 framed the 12 audit-only survivors as
diagnostic evidence about gate divergence (what WF and the regime
holdout each select for, and how those selection criteria
diverge). This framing carries forward to PHASE2C_7 unchanged. Any
PHASE2C_7 evidence about audit-only survivors — whether they
pass 2024, whether they share structural properties, whether they
would pass alternative gate calibrations — is diagnostic, not
actionable. The carry-forward is structural: PHASE2C_7 must not
treat audit-only survivors as candidates that earned promotion
through PHASE2C_6's holdout pass.

**2. Pre-registered questions, not post-hoc fishing.**

PHASE2C_6 closeout §9 codified that "treating [audit-only
survivors] as candidates for further study would require a
separate pre-registered question, not post-hoc promotion because
they survived 2022." This discipline applies to PHASE2C_7's
investigation of audit-only survivors specifically and to all
PHASE2C_7 work generally. Any new question raised mid-arc — about
candidate properties, about by-theme patterns, about gate
calibration sensitivity — must be addressed via a pre-registered
follow-up, not via opportunistic analysis of PHASE2C_7 outputs.

**3. Bounded framing throughout.**

PHASE2C_6 maintained "in this batch, against 2022 regime, this
gate calibration" bounding throughout the closeout. PHASE2C_7
findings carry the same discipline: claims should be bounded to
the regimes evaluated (2022 + 2024 if Path B), the candidate
populations evaluated (full 198 or 13-subset depending on path),
and the gate calibrations used. Generic statements about "the WF
methodology" or "candidate alpha quality" remain out-of-bounds
without explicit empirical scope. The phrase "did not enrich for
holdout survival in this batch" is the canonical bounded form;
"WF gate is broken" is the over-claim it forecloses.

**4. Scaling-step discipline (METHODOLOGY_NOTES.md §4).**

If PHASE2C_7's chosen path involves multi-step evaluation (e.g.,
Path B's primary pass plus optional secondary trade-count-filtered
pass; Path C's multiple calibration variants), each step's data
must be treated as supporting only its own scope of claim.
Intermediate step data should not be over-extended to claims that
require the later step's evidence. PHASE2C_6's smoke (4) → primary
(44) → audit (198) sequence is the canonical example: each step
added necessary information that earlier steps could not supply.
PHASE2C_7's analogous sequence (whatever it ends up being) should
follow the same discipline.

**5. No "WF methodology is broken" claims.**

PHASE2C_6 explicitly disclaimed in §6 (interpretation-scope bounds)
that the within-batch finding does not imply walk-forward
methodology is broken. Whatever PHASE2C_7 finds — whether the
anti-selection generalizes to 2024, whether calibration variation
restores selection power, whether the cohort survives — PHASE2C_7
must maintain the same disclaimer. The methodology-vs-metric
distinction (a correctly-computed metric can fail to predict a
property; that does not retroactively make the metric incorrect)
is project-standing context.

**6. METHODOLOGY_NOTES.md §1-§7 application.**

PHASE2C_7 inherits the seven principles codified in
`docs/discipline/METHODOLOGY_NOTES.md`:

- **§1 Empirical verification for factual claims** — every
  specific number (counts, ranks, percentages, candidate hashes)
  in PHASE2C_7 prose must trace to an empirical query against
  canonical data, not plausible reasoning.
- **§2 Meta-claim verification discipline** — confident process
  claims ("we've verified," "the framing is pinned") need the
  same empirical discipline as artifact-level claims.
- **§3 Regime-aware calibration bands** — any expected-behavior
  bands set in PHASE2C_7 dispatches or analyses must reference
  the actual regime structure being evaluated.
- **§4 Scale-step discipline for empirical evaluations** —
  detailed in carry-forward item 4 above.
- **§5 Precondition verification for structural and organizational
  principles** — structural recommendations during PHASE2C_7's
  drafting and review must verify the principle's preconditions
  hold for the specific case, not just appeal to general principles.
- **§6 Commit messages are not canonical result layers** — if
  PHASE2C_7's commit messages carry preliminary characterizations
  that turn out to be refined by closeout-time empirical
  verification, the closeout is canonical and silent correction
  in the closeout is the discipline (not erratum-style
  acknowledgment of the commit message).
- **§7 Asymmetric confidence reporting on multi-sample claims** —
  if PHASE2C_7 findings span sub-samples of different sizes,
  each sub-claim's confidence calibrates to its own supporting
  sample, not smoothed to a uniform claim across asymmetric
  samples.

**7. Touched-once 2025 preservation.**

The 2025 test split's touched-once status is preserved across
all four paths. PHASE2C_7 does not consume 2025. (Operational
prohibition detailed in §6 out-of-scope; project-discipline
basis in `config/environments.yaml`'s split semantics and
`CLAUDE.md`'s date-split and research-discipline rules.)

## 8. Exact next implementation artifact (PHASE2C_7.1)

PHASE2C_7.1 is the implementation arc following Charlie's
selection of a path from §3. Its exact spec depends on the path
chosen; this section provides one-paragraph skeletons per path so
that the decision criteria in §4 connect concretely to forward
work. Each skeleton names a file path, scope envelope, success
criteria (cross-referenced to §4's expected observables rather
than restated), and rough duration. Spec-level detail is deferred
to PHASE2C_7.1 itself.

**If Path A is selected.** Producer artifact at
`scripts/run_phase2c_survivor_multiregime.py` (or equivalent thin
wrapper around the existing `scripts/run_phase2c_evaluation_gate.py`
with a 13-candidate hash list and 2024-regime configuration). Scope
envelope: evaluate the 13 PHASE2C_6 holdout-survivors (1 primary
+ 12 audit-only, hashes enumerated in PHASE2C_6 closeout §7)
against the 2024 validation regime per `config/environments.yaml`
v2 split, using the same 4-criterion AND-gate. Success criteria:
§4 Path A expected observables (aggregate pass-rate, per-candidate
2024 metrics; the survivor-overlap observable is trivial-by-
construction for Path A and not load-bearing) produced and
persisted under `data/phase2c_evaluation_gate/<run_id>_v1/` with
single-run holdout attestation. Rough duration: ~3-4 hours total
work-cycle including drafting, review, and closeout (compute is
~16 seconds).

**If Path B is selected.** Producer artifact at
`scripts/run_phase2c_full_multiregime.py` (or extension to
`scripts/run_phase2c_evaluation_gate.py` to accept a 2024-regime
configuration with `--universe audit`). Scope envelope: evaluate
all 198 PHASE2C_6 candidates against 2024 validation, with
optional pre-specified trade-count-filtered secondary pass per §3
Path B scope. Success criteria: §4 Path B expected observables
produced — including the candidate-aligned 2022-vs-2024
comparative analysis and the primary-vs-audit-only 2024 pass-rate
comparison — and persisted under
`data/phase2c_evaluation_gate/<run_id>_v1/` with single-run
holdout attestation. The optional filter sub-pass produces a
parallel artifact set under a sibling run_id. Rough duration:
~6-10 hours total work-cycle (compute is ~4 minutes).

**If Path C is selected.** Producer artifact at
`scripts/run_phase2c_wf_sensitivity.py` (or extension to existing
machinery to accept calibration-set parameters). Scope envelope:
re-run the PHASE2C_6 evaluation against the same 198 candidates
and 2022 regime under multiple WF gate calibrations, with the
calibration set pinned at PHASE2C_7.1 spec. Success criteria: §4
Path C expected observables produced for each calibration variant.
Rough duration: ~4-6 hours total work-cycle (compute is trivial
per variant; aggregate depends on number of variants tested).

**If Path D is selected.** Implementation artifact spans multiple
files: DSR module under `backtest/dsr.py` (or equivalent location
following project structure), tests under `tests/test_dsr.py`,
integration with `backtest/experiment_registry.py`. Scope envelope:
DSR computation, multiple-testing correction logic, null
distribution estimation, applied to PHASE2C_6's n=1 dual-pass
population for completeness (with the explicit acknowledgment per
§3 Path D and §6 in-scope that this application is degenerate).
Success criteria: §4 Path D expected observables, with DSR module
verified against a published reference implementation (Bailey-
López de Prado or equivalent) at PHASE2C_7.1 spec time, not as a
finding produced during implementation. Scope guardrails per
ChatGPT's D12 reduction precedent (sqrt(2*ln(N)) heuristic over
full Bailey-López de Prado formula) apply unless PHASE2C_7.1 spec
explicitly justifies expansion. Rough duration: 1-2 weeks total
work-cycle.

**Cross-cutting note.** Each path's PHASE2C_7.1 spec must include:
the producer-side run command, the success-criteria verification
queries (analogous to PHASE2C_6 closeout §11's reproducibility
queries), the lineage-attestation pattern (single-run holdout
domain extension or new attestation domain depending on path), the
closeout document path under `docs/closeout/`, and the adjudication
sequence (which sections drafted first, dual-AI review pattern,
plus Codex adversarial review trigger if scope-overshoot risk
warrants external row-level verification per PHASE2C_6 §10's
discipline observation). PHASE2C_6's arc structure is the canonical
reference for these meta-decisions.
