# PHASE2C_8 Scoping Decision


## 1. Scope and verdict

**This document decides which empirical question to pursue as the
next implementation artifact, after PHASE2C_7.1's regime-dependent
selection-power finding. It does not implement; implementation is
deferred to a follow-up implementation arc once Charlie selects a
path from §3.**

**Project state at PHASE2C_8 scoping (2026-04-27).**

- Canonical main: `origin/main` at commit `76e46d4`
- Tags on main: `wf-corrected-v1` (corrected WF engine fix at
  commit `eb1c87f`), `phase2c-6-evaluation-gate-v1` (PHASE2C_6
  arc completion), `phase2c-7-1-multi-regime-v1` (PHASE2C_7.1
  multi-regime evaluation gate completion at `784936a`)
- PHASE2C_7.1 closeout:
  [`docs/closeout/PHASE2C_7_1_RESULTS.md`](../closeout/PHASE2C_7_1_RESULTS.md)
- PHASE2C_7.1 plan:
  [`docs/phase2c/PHASE2C_7_1_PLAN.md`](PHASE2C_7_1_PLAN.md)
- PHASE2C_7.0 scoping precedent:
  [`docs/phase2c/PHASE2C_7_SCOPING_DECISION.md`](PHASE2C_7_SCOPING_DECISION.md)
- Methodology principles in force:
  [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  §1-§12 (post-update commit `76e46d4`)
- CLAUDE.md Phase Marker reflects PHASE2C_7.1 closure with
  follow-up scoping decision pending

**PHASE2C_7.1 finding recap (bounded one-paragraph form).**

In batch `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`, evaluated against
two regimes (`v2.regime_holdout` = bear_2022; `v2.validation` =
validation_2024), the corrected WF gate's selection power is
regime-dependent and not robustly preserved across the two tested
regimes. Three §5 cuts in PHASE2C_7.1: within-2024 inversion
(primary 22/44 = 50.0% > audit-only 65/154 = 42.2%; opposite of
PHASE2C_6's 2022 anti-selection direction); cross-regime intersection
mirror (audit-only 8/154 = 5.2% > primary 0/44 = 0.0%; matches
2022 anti-selection direction); PHASE2C_6 carry-forward asymmetry
(audit-only 8/12 = 66.7% > primary 0/1; sole 2022 primary survivor
`bf83ffec` failed 2024). Three cuts are different estimands; not
collapsed into a single pass/fail verdict. Mechanism adjudication
(regime-mismatch / pattern-overfit / calibration-coupling) remains
undetermined within this batch's two tested regimes. Full bounded
interpretation in PHASE2C_7.1 closeout §6 ("Bounded claims firewall").

**What PHASE2C_8 is NOT.**

- **Not a re-litigation of PHASE2C_7.1.** PHASE2C_7.1's empirical
  results are sealed (tag `phase2c-7-1-multi-regime-v1`). PHASE2C_8
  inherits them as input, not as open questions to re-examine.
- **Not an implementation plan.** PHASE2C_8.0 is a scoping decision
  enumerating candidate paths and recommending one. Implementation
  details (regime selection, evaluation parameters, orchestration
  structure, closeout content) are deferred to the follow-up
  implementation arc named in §8 once a path is selected.
- **Not a methodology amendment.**
  [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  §1-§12 are project-standing principles. PHASE2C_8 applies them;
  it does not revise them. New methodology principles surfaced
  during PHASE2C_8 work are captured as a follow-up update (same
  hybrid handling as PHASE2C_6's §10 → commit `536f737` and
  PHASE2C_7.1's §10 → commit `76e46d4`).
- **Not a forward decision on DSR/CPCV/MDS investment, candidate
  promotion, test-split consumption, or `config/environments.yaml`
  modification.** These remain explicit non-decisions per PHASE2C_7.1
  closeout §9.C and CLAUDE.md hard rules (2025 test split touched-
  once; IMMUTABLE-config).
- **Not a collapse of Q-B3 into a single investigation framing.**
  §3 surfaces Q-B3.a (cross-regime extension; structurally dependent
  on Q-B1's evidence base) and Q-B3.b (within-existing-evidence;
  Q-B1-independent) as distinct investigation scopes within the
  Q-B3 sub-section. PHASE2C_8.0 scoping treats them as structurally
  distinct candidate paths, not as variants of one question.

**Document structure.**

§2 enumerates the open empirical questions inherited from PHASE2C_7.1
§9 (Q-A1 through Q-A5 substantive questions; Q-B1 through Q-B4
follow-up scoping questions). §3 enumerates four candidate next-arc
paths (Q-B1 multi-regime evaluation at n≥3; Q-B2 calibration variation
within a regime; Q-B3 cohort (a) deep-dive with two distinct
investigation scopes Q-B3.a cross-regime extension and Q-B3.b
within-existing-evidence; Q-B4 DSR infrastructure investment) with
uniform comparison structure including explicit mechanism-question
scope per path. §4 names five decision criteria (mechanism-question
coverage; evidence-base requirements; operational scope; path
dependencies; 2025 test split touched-once preservation) and
adjudicates each path against each criterion. §5 carries the
recommended scoping decision (Q-B1) with four pairwise alternative
comparisons (Q-B1 vs Q-B2; Q-B1 vs Q-B3.a; Q-B1 vs Q-B3.b; Q-B1 vs
Q-B4) and closes with falsifiability framing (what evidence would
shift the recommendation). §6 enumerates in-scope deliverables for
the recommended path and explicit out-of-scope items including
non-recommended paths. §7 names project-discipline patterns carried
forward from PHASE2C_7.1 plus methodology self-application
(METHODOLOGY_NOTES §1-§12 conditional-boundary application to this
administrative scoping document). §8 provides the one-paragraph
follow-up implementation arc skeleton with administrative identifier
and exact next steps.


## 2. Open empirical questions inherited from PHASE2C_7.1 §9

PHASE2C_7.1's closeout §9 enumerates two distinct categories of
inherited material that PHASE2C_8.0 scoping must address. §9.A names
five open empirical questions ("Q-A1" through "Q-A5") that
PHASE2C_7.1's evidence base could not answer; §9.B names four
follow-up scoping decisions ("Q-B1" through "Q-B4") that follow-up
scoping needed to consider before any implementation arc begins.

PHASE2C_8.0 scoping treats these categories differently:

- **Q-A questions are inherited as open.** They are NOT closed out by
  this scoping decision; PHASE2C_8.0 does not adjudicate the
  underlying mechanism candidates or theme-dependence claims. Each
  Q-A question is restated here in bounded form with the type of
  evidence that would advance it; §3 path comparison maps each Q-B
  candidate path to which Q-A questions it addresses and which it
  leaves open.
- **Q-B questions are adjudicated by this scoping decision.** They
  are decisions PHASE2C_8.0 must make: which candidate path to pursue
  as the next implementation artifact. §3 enumerates the Q-B paths
  with mechanism-question-scope framing; §4 names decision criteria;
  §5 carries the recommended scoping decision.

This distinction is structurally important. A future reader landing
at §2 looking for "what does PHASE2C_8 close out?" sees Q-B questions
specifically; a reader looking for "what does PHASE2C_8 inherit as
unanswered?" sees Q-A questions specifically.

### §2.A — Open empirical questions (Q-A): inherited as open

**Q-A1 — Three-mechanism candidate explanation empirically
underdetermined.**

PHASE2C_7.1 §6 category 3 names regime-mismatch, pattern-overfit, and
calibration-coupling as three explanations that all produce §5's
regime-dependent pattern. Distinguishing among them at population
level requires either multi-regime evaluation at n≥3 (which would
distinguish regime-mismatch from regime-independent mechanisms) or
calibration variation within a regime (which would distinguish
calibration-coupling from regime-or-pattern mechanisms). The empirical
underdetermination is structural at n=2 regimes. *Addressed by:* Q-B1
(regime axis) + Q-B2 (calibration axis). *Inherited as open by
PHASE2C_8.0.*

**Q-A2 — Within-2024 partition direction theme-dependence: regime-
specific or theme-specific?**

PHASE2C_7.1 §8 surfaces calendar_effect's within-theme inversion
(primary 3/7 = 42.9% < audit_only 21/33 = 63.6%, −20.7pp gap in
audit-only direction) against §5's 4-of-5-themes-match population
direction. Whether calendar_effect inverts in additional regimes
(regime-specific) or whether the WF gate underrates calendar_effect
candidates structurally (theme-specific) is empirically undetermined
from n=2 regimes. *Addressed by:* Q-B1 (multi-regime extension
distinguishes regime-specific vs theme-specific). *Inherited as open
by PHASE2C_8.0.*

**Q-A3 — Cross-regime intersection theme-clustering: generalize or
batch-specific?**

PHASE2C_7.1 §7 cohort (a)'s 5+2+1 distribution across themes (5
calendar_effect + 2 volume_divergence + 1 momentum) is observable in
this batch. Whether this clustering pattern persists across additional
regimes or different candidate populations is undetermined; n=8
cross-regime intersection survivors carry single-candidate-flip
sensitivity. *Addressed by:* Q-B1 (additional cross-regime intersection
populations). *Inherited as open by PHASE2C_8.0.*

**Q-A4 — Failure-mode signature persistence vs shift: mechanism
meaning?**

PHASE2C_7.1 §8 surfaces two distinct cross-regime patterns:
volatility_regime's non-engagement signature persists (18/40 → 19/40
zero-trades); mean_reversion's 2022 active-loss shifts to 2024 mixed
(drawdown-failure halved, trade-count failures emerge). Whether
persistence-vs-shift maps to mechanism distinctions is empirically
underdetermined within this batch. Candidate framings include
"persistence indicates alpha-thesis-misalignment with regime structure"
and "shift indicates regime-specific entry-condition misfit," but
neither is supported or refuted by this batch's evidence. *Addressed
by:* Q-B1 (persistence verified across additional regimes) or Q-B2
(calibration shift surfaces signature changes). *Inherited as open by
PHASE2C_8.0.*

**Q-A5 — PHASE2C_6 carry-forward asymmetry: primary structurally
weaker on cross-regime than audit_only, or small-n sampling?**

PHASE2C_7.1 §5 cut 3 shows 0/1 primary carry-forward versus 8/12
audit_only carry-forward (66.7%) — directional asymmetry, but the
primary n=1 makes the magnitude bound. Per §6 category 1, the
audit_only n=12 carries single-candidate-flip sensitivity (10/14 =
71.4% / 8/14 = 57.1%); the primary n=1 is even more sensitive.
Whether primary candidates structurally have lower cross-regime
carry-forward than audit_only candidates, or whether the 0/1 outcome
is small-n sampling, is empirically undetermined. *Addressed by:*
Q-B1 (multi-regime evaluation at n≥3 against larger primary populations
clarifies structural-vs-sampling). *Inherited as open by PHASE2C_8.0.*

### §2.B — Follow-up scoping decisions (Q-B): adjudicated by PHASE2C_8.0

**Q-B1 — Multi-regime evaluation at n≥3.**

PHASE2C_7.1 §9.B raised the question of whether to invest in multi-
regime evaluation infrastructure (orchestration, regime-attestation
discipline, candidate-aligned cross-regime artifact pipeline) given
the mechanism-question structure §6 names. Q-B1 evaluates the same
198 candidates against additional historical regimes (n≥3 total
regimes including PHASE2C_7.1's two), producing the multi-regime
cross-regime evidence base needed for population-level mechanism
adjudication. The 2025 test split is preserved touched-once
(CLAUDE.md hard rule); additional regimes come from additional
historical regimes selected by a future scoping decision document
within the implementation arc, not from the test split. *Adjudicated
by §3 + §5.*

**Q-B2 — Calibration variation within a regime (Path C revisit).**

PHASE2C_7.0 deferred Path C (gate-calibration variation) in favor of
Path B (multi-regime evaluation full population). PHASE2C_7.1's §8
calendar_effect within-theme inversion + §7 cohort (a) clustering
surface descriptive patterns that the WF gate's selection power
against validation_2024 cannot be fully characterized as calibration-
coupled, regime-coupled, or pattern-coupled from the available
evidence. Whether to prioritize Path C calibration variation now or
defer further is the scoping decision Q-B2 raises. *Adjudicated by
§3 + §5.*

**Q-B3 — Cohort (a) deep-dive as pre-registered question.**

PHASE2C_7.1 §9.B raised Q-B3 with cross-regime extension framings
("do cohort (a) candidates carry forward to a third regime?"; "do
cohort (a) candidates' theme-clustering pattern persist across
additional regimes?"). PHASE2C_8.0 scoping surfaces Q-B3 as two
structurally distinct investigation scopes:

- **Q-B3.a (cross-regime extension; Q-B1-dependent).** Investigates
  whether cohort (a)'s 8 cross-regime survivors carry forward to a
  third regime, and whether theme-clustering generalizes. Requires
  Q-B1's evidence base (third regime evaluation must exist before
  cohort (a) carry-forward can be tested). Structurally downstream
  of Q-B1.
- **Q-B3.b (within-existing-evidence; Q-B1-independent).** Investigates
  cohort (a) candidates against existing PHASE2C_7.1 artifact set —
  trade-pattern characteristics, structural-property contrasts with
  cohort (b), descriptive analysis under a pre-registered question
  not requiring additional regime evidence. Independent of Q-B1.

The two scopes are not variants of one question; they are
structurally distinct investigation patterns with different evidence
bases, different operational scopes, and different mechanism-question
relationships. *Both Q-B3.a and Q-B3.b adjudicated by §3 + §5; §4
decision criteria treat them separately within Q-B3's row.*

PHASE2C_7.1 §9.B Q-B3 surfaced only scope (a) variants; PHASE2C_8.0
scoping surfaces scope (b) explicitly because Q-B1-independence
makes it a structurally distinct candidate path with smaller
operational scope and different research-yield profile.

**Q-B4 — DSR infrastructure investment given continued n=1 primary
cross-regime.**

PHASE2C_6.6 §9 raised the DSR (Deflated Sharpe Ratio) infrastructure
question against PHASE2C_6's n=1 primary 2022-survivor (`bf83ffec`).
PHASE2C_7.1 has 22 primary 2024-survivors but 0 primary cross-regime
survivors. The DSR question shifts structure rather than answers:
from "is single-regime DSR meaningful at n=1 primary survivor?" to
"what evidence base does cross-regime DSR require?" The PHASE2C_7.1
data does not answer the DSR question; it surfaces an additional
dimension (cross-regime evidence structure) that follow-up scoping
weighs against alternative infrastructure investments. Q-B4 has
structural dependency on Q-B1: the DSR question's framing shifts
based on what the cross-regime evidence base looks like; Q-B4
adjudication after Q-B1's output is more rigorously bounded than
Q-B4 before Q-B1. *Adjudicated by §3 + §5; structural dependency on
Q-B1 surfaced.*


## 3. Candidate next-arc paths

Four paths are enumerated below. Each is described using uniform
seven-subfield structure to enable side-by-side comparison:

- **Mechanism question scope** (per Refinement 1): which mechanism
  question the path addresses (regime axis / calibration axis /
  cohort investigation / meta-infrastructure). Names what the path
  CAN distinguish among the three mechanism candidates (regime-
  mismatch / pattern-overfit / calibration-coupling).
- **Scope:** what the path executes operationally.
- **Information value:** what evidence the path generates.
- **Cost:** compute, time, API spend, drafting+adjudication overhead.
- **What it answers:** which Q-A questions from §2.A the path
  addresses.
- **What it does NOT answer:** which Q-A questions remain open.
- **Dependency:** upstream/downstream of which other Q-B paths.

Q-B3 (cohort (a) deep-dive) is treated with an internal split per
Sub-option II.X — Q-B3.a (cross-regime extension; Q-B1-dependent)
and Q-B3.b (within-existing-evidence; Q-B1-independent) are
structurally distinct investigation scopes within the Q-B3 sub-
section. Each scope receives full subfield treatment.

### Q-B1 — Multi-regime evaluation at n≥3

**Mechanism question scope.** Regime axis. Distinguishes regime-
mismatch from regime-independent mechanisms (pattern-overfit OR
calibration-coupling combined). If the WF gate's selection power
varies systematically across additional regimes in the same
direction as PHASE2C_7.1's two-regime variation, regime-mismatch is
supported as the operating mechanism. If selection power varies
arbitrarily across additional regimes (no systematic regime
character), regime-independent mechanisms are candidates and Q-B2's
calibration-axis variation becomes more informative for
disambiguation. Q-B1 does NOT distinguish pattern-overfit from
calibration-coupling — both are regime-independent mechanisms that
look similar under regime-axis variation alone.

**Scope.** Evaluate the same 198 candidates from batch
`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` against additional historical
regimes (n≥3 total regimes including PHASE2C_7.1's two: bear_2022
and validation_2024). The specific additional regimes are NOT
pre-named here; selection of additional regimes is itself a scoping
decision within the follow-up implementation arc, not a PHASE2C_8.0
scoping commitment. Same 4-criterion AND-gate as PHASE2C_7.1 (sharpe
≥ −0.5, max_drawdown ≤ 0.25, total_return ≥ −0.15, total_trades ≥
5). Same producer infrastructure as PHASE2C_7.1 with extension to
n≥3 regime orchestration + candidate-aligned cross-regime
comparison-matrix machinery extended from 2-regime to n-regime
structure.

**Information value.** Tells whether the WF gate's regime-
dependence pattern from PHASE2C_7.1 (selection power varies between
bear_2022 and validation_2024) is regime-axis-systematic or
arbitrary across additional regimes. The candidate-aligned cross-
regime evidence base supports population-level mechanism
adjudication — primary partition (n=44) and audit-only partition
(n=154) cross-regime carry-forward rates can be computed at n≥3,
clarifying whether PHASE2C_6's n=1 primary cross-regime survivor is
structural-vs-sampling per Q-A5.

**Cost.** Moderate-to-high. Per-regime evaluation at 198 candidates
× ~1.2s ≈ 4 minutes wall-clock per regime (per PHASE2C_7.1 audit_v1
timing). For one additional regime: ~4 minutes. For multi-regime
extension at e.g. 4-5 total regimes: ~12-20 minutes wall-clock total.
No API spend (local backtest evaluation). Drafting + adjudication
overhead similar to PHASE2C_7.1 closeout (~10-15 sessions for the
follow-up implementation arc closeout). 2025 test split preserved
touched-once (CLAUDE.md hard rule).

**What it answers.** Q-A1 (mechanism candidate explanation) —
partially, by distinguishing regime-mismatch from regime-independent
mechanisms. Q-A2 (within-2024 partition direction theme-dependence)
— directly, by testing whether calendar_effect's within-theme
inversion persists or varies across additional regimes. Q-A3 (cross-
regime intersection theme-clustering) — directly, by extending
cross-regime intersection populations beyond n=8. Q-A4 (failure-
mode signature persistence vs shift) — partially, by extending
failure-mode evidence base across regimes. Q-A5 (PHASE2C_6 carry-
forward asymmetry) — partially, by clarifying structural-vs-
sampling at larger primary populations.

**What it does NOT answer.** Q-A1 calibration-coupling distinction
— Q-B1 cannot disambiguate pattern-overfit from calibration-coupling
within regime-independent mechanisms; Q-B2's calibration-axis
variation is needed for that distinction. Q-A4 mechanism meaning
beyond persistence-vs-shift descriptive observation — mechanism
interpretation requires either Q-B2 calibration variation or
follow-up theory work, not multi-regime evidence alone.

**Dependency.** Independent of Q-B2 in scope (different mechanism
axes). Upstream of Q-B3.a (cross-regime extension cohort
investigation requires Q-B1's third-regime evidence base before
cohort (a) carry-forward can be tested). Upstream of Q-B4 (DSR
infrastructure investment scope evolves with cross-regime evidence
base size; Q-B4 adjudication after Q-B1's output is more rigorously
bounded). Independent of Q-B3.b (within-existing-evidence cohort
investigation does not require Q-B1's evidence base).

### Q-B2 — Calibration variation within a regime (Path C revisit)

**Mechanism question scope.** Calibration axis. Distinguishes
calibration-coupling from regime-or-pattern mechanisms. If the WF
gate's selection power varies substantially as the gate threshold
varies (e.g., 0.0 / 0.25 / 0.5 / 0.75 / 1.0 calibrations against
the same regime), calibration-coupling is supported as the operating
mechanism. If selection power stays stable across calibrations,
calibration-coupling is ruled out and regime-mismatch or pattern-
overfit are candidates; Q-B1's regime-axis variation becomes more
informative for disambiguation. Q-B2 does NOT distinguish regime-
mismatch from pattern-overfit — both are regime-or-pattern
mechanisms that look similar under calibration-axis variation alone.

**Scope.** Re-evaluate the same 198 candidates against PHASE2C_7.1's
existing two regimes (bear_2022 and validation_2024) under varied
WF gate calibrations. Example calibrations: thresholds at 0.0, 0.25,
0.75, 1.0 instead of 0.5; rank-based filters (top-N by WF Sharpe);
multi-criterion combinations (WF Sharpe AND WF return AND WF
drawdown). Exact calibration set deferred to the follow-up
implementation arc if Q-B2 is selected. Same per-candidate
evaluation infrastructure as PHASE2C_7.1; new scoring-and-partition
logic.

**Information value.** Tells whether PHASE2C_7.1's regime-dependent
finding is specific to the `wf_test_period_sharpe > 0.5` calibration
or persists across calibrations. If a different calibration restores
selection power within bear_2022 or validation_2024, the finding is
calibration-specific; if no calibration restores selection power,
the finding is calibration-robust within both tested regimes,
strengthening the regime-mismatch or pattern-overfit candidates.

**Cost.** Low to moderate depending on number of calibrations tested.
Each calibration variation reuses existing per-candidate evaluation
data; only the partition-and-scoring logic changes. Per-calibration
evaluation: ~minutes wall-clock for 198-candidate re-partitioning.
For 4-5 calibrations across 2 regimes: ~tens of minutes total. No
API spend. Drafting + adjudication overhead similar to PHASE2C_7.1
(~8-12 sessions; smaller than Q-B1 because no new regime
orchestration infrastructure).

**What it answers.** Q-A1 (mechanism candidate explanation) —
partially, by distinguishing calibration-coupling from regime-or-
pattern mechanisms. Q-A4 (failure-mode signature persistence vs
shift) — partially, by surfacing calibration-shift effects on
failure-mode signatures.

**What it does NOT answer.** Q-A1 regime-mismatch vs pattern-overfit
distinction — Q-B2 cannot disambiguate within regime-or-pattern
mechanisms; Q-B1's regime-axis variation is needed. Q-A2 (within-
2024 partition direction theme-dependence) — calibration variation
within bear_2022/validation_2024 doesn't address whether theme-
dependence is regime-specific or theme-specific. Q-A3 (cross-regime
intersection theme-clustering) — not addressed; calibration
variation doesn't extend cross-regime cohort populations.

**Dependency.** Independent of Q-B1 in scope (different mechanism
axes). Independent of Q-B3.a/Q-B3.b (cohort investigations are
orthogonal to calibration variation). Independent of Q-B4 (DSR
infrastructure scope is meta-infrastructure; calibration variation
doesn't change DSR scope).

### Q-B3 — Cohort (a) deep-dive (two distinct investigation scopes)

Q-B3 is treated with internal split per Sub-option II.X. Q-B3.a
and Q-B3.b are structurally distinct investigation scopes; the
seven-subfield treatment is provided separately for each scope.

#### Q-B3.a — Cross-regime extension cohort investigation

**Mechanism question scope.** Cohort cross-regime carry-forward
investigation. Does NOT distinguish among the three mechanism
candidates at population level; produces descriptive evidence about
cohort (a)'s 8 cross-regime survivors specifically. If most cohort
(a) candidates carry forward to a third regime, the cohort-level
generalization claim is partially supported (necessary but not
sufficient evidence; would require additional regimes for stronger
claims). If few cohort (a) candidates carry forward, the cohort
(a) intersection survival was likely batch-and-two-regime-specific.

**Scope.** Pre-register specific investigation questions about
cohort (a) (e.g., "do cohort (a) candidates carry forward to a
third regime?"; "do cohort (a) candidates' theme-clustering
pattern persist across additional regimes?"). Evaluate cohort (a)'s
8 candidates (`9dc5c373`, `c200a95d`, `0845d1d7`, `94b3d1fd`,
`1d6a587a`, `f4977b3e`, `7f296ee9`, `18c2a5f7` per PHASE2C_7.1 §7
cohort (a) enumeration) against the additional regime(s) Q-B1
produces. Compare carry-forward rate against PHASE2C_7.1's 8/12 =
66.7% audit-only carry-forward baseline.

**Information value.** Tells whether cohort (a)'s cross-regime
intersection survival generalizes beyond the bear_2022 ∩
validation_2024 intersection. Suggestive evidence about
regime-orthogonal alpha for the cohort specifically, not at
population level.

**Cost.** Minimal. 8 candidates × ~1.2s/candidate ≈ 10 seconds
wall-clock per additional regime. No API spend. Drafting +
adjudication overhead minimal (~2-4 sessions; cohort-level
descriptive analysis is bounded).

**What it answers.** Q-A3 (cross-regime intersection theme-
clustering) — directly, by testing whether cohort (a)'s 5+2+1
theme distribution persists. Q-A1 — minimally; cohort-level
evidence doesn't address population-level mechanism distinction.

**What it does NOT answer.** Q-A1 at population level (cohort-only
investigation). Q-A2 (within-2024 partition direction). Q-A4
(failure-mode signature). Q-A5 (carry-forward asymmetry; cohort (a)
is cross-regime-survivor population; carry-forward asymmetry concerns
2022-survivor → 2024 cross-regime structure).

**Dependency.** Q-B1-dependent — third-regime evidence base must
exist before cohort (a) cross-regime carry-forward can be tested.
Structurally downstream of Q-B1. Independent of Q-B2/Q-B3.b/Q-B4.

#### Q-B3.b — Within-existing-evidence cohort investigation

**Mechanism question scope.** Cohort within-existing-evidence
investigation. Does NOT distinguish among the three mechanism
candidates at any level; produces descriptive evidence about cohort
(a) characteristics within PHASE2C_7.1's existing artifact set. The
mechanism question is structurally outside Q-B3.b's scope; Q-B3.b's
research yield is descriptive analysis (cohort-level structural
properties), not mechanism adjudication.

**Scope.** Pre-register investigation questions about cohort (a)
characteristics derivable from existing PHASE2C_7.1 artifacts (e.g.,
"what trade-pattern characteristics distinguish cohort (a) from
cohort (b) Q-B3 candidates that failed cross-regime?"; "what
structural properties (DSL complexity, factor usage, signal-firing
frequency) distinguish cohort (a) from non-survivors?"). Operate on
existing PHASE2C_7.1 artifact set: per-candidate `holdout_summary.json`
files; `comparison.csv` row-level data; per-candidate compilation
manifests at `data/compiled_strategies/<hash>.json`. No new
evaluation runs required.

**Information value.** Tells whether cohort (a) candidates share
structural properties that distinguish them from cohorts (b) and
(c). Suggestive evidence about what the WF gate × cross-regime
intersection selects for descriptively, not mechanism-causally.

**Cost.** Minimal. No new evaluation runs (cost ~0 wall-clock for
data collection; existing artifacts already produced). Drafting +
adjudication overhead similar to a small intermediate arc (~3-5
sessions for the follow-up implementation arc closeout).

**What it answers.** Q-A3 (cross-regime intersection theme-
clustering) — partially, by surfacing structural-property
correlates of theme clustering within existing evidence.

**What it does NOT answer.** Q-A1 (mechanism candidate explanation).
Q-A2 (within-2024 partition direction theme-dependence). Q-A3
generalization beyond the batch (Q-B3.a addresses this; Q-B3.b
operates within the batch). Q-A4 (failure-mode signature). Q-A5
(carry-forward asymmetry).

**Dependency.** Q-B1-independent (operates within existing PHASE2C_7.1
artifact set). Independent of Q-B2/Q-B3.a/Q-B4. The structurally
smallest intermediate arc; could potentially run in parallel with
or before any other Q-B path.

### Q-B4 — DSR infrastructure investment given continued n=1 primary cross-regime

**Mechanism question scope.** Meta-infrastructure. Does NOT
distinguish among the three mechanism candidates at any level. The
mechanism question is structurally outside Q-B4's scope; Q-B4's
research yield is infrastructure investment readiness given current
evidence base, not empirical mechanism adjudication.

**Scope.** Build DSR (Deflated Sharpe Ratio) infrastructure as
originally planned in PHASE2C_6 closeout §9 first decision, applied
to PHASE2C_7.1's primary cross-regime survivor population (n=0:
`bf83ffec` failed validation_2024; PHASE2C_7.1 §5 cut 3). DSR
computation deflates observed Sharpe against a null distribution
accounting for multiple-testing exposure.

**Information value.** Minimal under current conditions. n=0
primary cross-regime survivor population produces no meaningful
batch-level inference; DSR computation against n=0 is structurally
undefined or trivially bounded. The DSR infrastructure investment
question is whether to build the infrastructure NOW (with current
n=0 cross-regime evidence base) versus DEFER until cross-regime
evidence base grows (Q-B1 adds regime-axis populations; cohort
analysis from Q-B3 adds cohort-level populations).

**Cost.** Implementation cost moderate (DSR computation, multiple-
testing null-distribution bookkeeping, integration with experiment
registry). Drafting + adjudication overhead moderate (~6-8 sessions
for implementation + closeout). The cost is paid regardless of
whether DSR produces meaningful inference; the question is whether
the infrastructure investment timing is right.

**What it answers.** Q-A5 (PHASE2C_6 carry-forward asymmetry)
— partially, by adding multiple-testing-aware framing to the n=1
PHASE2C_6 dual-pass + n=0 PHASE2C_7.1 cross-regime contrast. The
DSR infrastructure outputs would not produce a definitive answer
to Q-A5 at current evidence base size; rather, would frame the
asymmetry under multiple-testing-correctness. Most other Q-A
questions are not addressed by Q-B4.

**What it does NOT answer.** Q-A1 (mechanism candidate explanation).
Q-A2 (within-2024 partition direction). Q-A3 (cross-regime
intersection theme-clustering). Q-A4 (failure-mode signature).
Q-A5 at meaningful evidence base — DSR's value scales with
hypotheses-evaluated and dual-pass population size; current
evidence base is structurally below DSR's effective range.

**Dependency.** Q-B1-dependent — DSR question's framing shifts
based on what the cross-regime evidence base looks like. Q-B4
adjudication after Q-B1's output is more rigorously bounded than
Q-B4 before Q-B1 (per Meta-3). Q-B4 before Q-B1 produces DSR
infrastructure with n=0 cross-regime evidence base; Q-B4 after
Q-B1 produces DSR infrastructure with n≥0 cross-regime evidence
base scaled by Q-B1's regime extension. Structurally downstream of
Q-B1 (parallel to Q-B3.a's downstream relationship). Independent
of Q-B2/Q-B3.


## 4. Decision criteria

The five paths in §3 (Q-B1, Q-B2, Q-B3.a, Q-B3.b, Q-B4) differ along
five dimensions that matter for choosing among them. This section
names the criteria explicitly, adjudicates each path against each
criterion, and provides a Q-A × Q-B mechanism-question coverage
matrix that maps §2.A's open empirical questions to which paths
address them.

### Axis 1 — Mechanism-question coverage

The most load-bearing axis. Per Meta-1, different paths address
different mechanism candidates among the three named in PHASE2C_7.1
§6 category 3 (regime-mismatch / pattern-overfit / calibration-
coupling). The path-comparison adjudication weighs which mechanism
candidate is most load-bearing for closing Q-A1 (mechanism-candidate
explanation) and which paths advance toward closing it.

**Per-path mechanism-question coverage** (cross-references §3
Mechanism question scope subfield + What it answers / What it does
NOT answer subfields per path):

- **Q-B1 (regime axis):** distinguishes regime-mismatch from regime-
  independent mechanisms. Advances Q-A1 partially (regime-mismatch
  vs regime-independent disambiguation). Does NOT distinguish
  pattern-overfit from calibration-coupling within regime-
  independent mechanisms; that disambiguation requires Q-B2.
- **Q-B2 (calibration axis):** distinguishes calibration-coupling
  from regime-or-pattern mechanisms. Advances Q-A1 partially
  (calibration-coupling vs regime-or-pattern disambiguation). Does
  NOT distinguish regime-mismatch from pattern-overfit within
  regime-or-pattern mechanisms; that disambiguation requires Q-B1.
- **Q-B3.a (cohort cross-regime extension):** does NOT distinguish
  among the three mechanism candidates at population level. Cohort-
  level evidence (8 cohort (a) candidates' carry-forward to a third
  regime) is necessary but not sufficient evidence for population-
  level mechanism adjudication.
- **Q-B3.b (cohort within-existing-evidence):** does NOT distinguish
  among the three mechanism candidates at any level. Within-batch
  descriptive cohort characterization investigates structural
  properties of cohort (a) without addressing mechanism causation.
- **Q-B4 (meta-infrastructure):** does NOT distinguish among the
  three mechanism candidates at any level. DSR adjudication is
  multiple-testing-correction infrastructure; it bounds inferential
  claims on existing evidence base, not mechanism candidates.

**Q-A × Q-B mechanism-question coverage matrix.**

| Q-A question | Q-B1 | Q-B2 | Q-B3.a | Q-B3.b | Q-B4 |
|--------------|:----:|:----:|:------:|:------:|:----:|
| **Q-A1** Three-mechanism candidate explanation | partial (regime axis) | partial (calibration axis) | none (cohort-level only) | none | none |
| **Q-A2** Within-2024 partition direction theme-dependence | direct (regime extension distinguishes regime-specific vs theme-specific) | none (calibration variation within existing regimes) | partial (cohort-level theme persistence) | none | none |
| **Q-A3** Cross-regime intersection theme-clustering | direct (additional cross-regime intersection populations) | none | direct (cohort theme-clustering generalization) | partial (within-batch theme correlates) | none |
| **Q-A4** Failure-mode signature persistence vs shift | partial (multi-regime persistence verification) | partial (calibration shift surfaces signature changes) | none | none | none |
| **Q-A5** PHASE2C_6 carry-forward asymmetry | partial (multi-regime n≥3 against larger primary populations clarifies structural-vs-sampling) | none | none | none | partial-degenerate (DSR at n=0 cross-regime) |

Cell legend: **direct** = path's primary purpose advances this Q-A;
**partial** = path produces some evidence but does not fully advance
or distinguish; **partial-degenerate** = path technically advances
but conditions (e.g., n=0) render the evidence uninformative;
**none** = path does not advance this Q-A.

**Cross-reading the matrix.** Q-A1 is advanced only partially by
Q-B1 (regime axis) and Q-B2 (calibration axis); both advance distinct
mechanism-axis components, neither fully closes Q-A1 alone. Q-A2 /
Q-A3 / Q-A5 are advanced primarily by Q-B1. Q-B3.a partially advances
Q-A3 (cohort-level extension); Q-B3.b partially advances Q-A3
(within-batch correlates). Q-B4 partially-degenerately advances Q-A5
(current evidence base too small for DSR meaningfulness).

The matrix shows Q-B1 has the broadest mechanism-question coverage
(advances Q-A1, Q-A2, Q-A3, Q-A5; partial Q-A4). Q-B2 has narrower
coverage (Q-A1 + Q-A4 only). Q-B3.a, Q-B3.b, Q-B4 have minimal
mechanism-question coverage.

### Axis 2 — Evidence-base requirements

Each path requires a different evidence base. Some paths consume
existing PHASE2C_7.1 artifacts only; some require new evaluation
runs producing new artifacts; some require both.

**Per-path evidence-base requirements** (cross-references §3
Scope + Cost subfields per path):

- **Q-B1:** Requires NEW evaluation runs against additional
  historical regimes (n≥3 total). Consumes existing PHASE2C_7.1
  batch (`b6fcbf86-...`) as candidate input universe; produces new
  per-regime artifacts at `data/phase2c_evaluation_gate/<regime>_v1/`
  paths. Comparison-matrix machinery extends from 2-regime to
  n-regime structure.
- **Q-B2:** Requires NEW partition-and-scoring logic but NO new
  evaluation runs. Consumes existing PHASE2C_7.1 per-candidate
  evaluation data (already computed at `audit_v1/` and
  `audit_2024_v1/`); applies new calibration thresholds at
  partition-scoring time. Produces new comparison artifacts at
  `data/phase2c_evaluation_gate/calibration_v1/` paths.
- **Q-B3.a:** Requires Q-B1's outputs (third-regime evaluation
  artifacts at `data/phase2c_evaluation_gate/<third_regime>_v1/`).
  Without Q-B1's artifacts, Q-B3.a cannot operationally proceed.
- **Q-B3.b:** Requires NO new evaluation runs. Consumes existing
  PHASE2C_7.1 artifact set: per-candidate `holdout_summary.json`
  files at `audit_2024_v1/<hash>/` and `audit_v1/<hash>/` paths;
  comparison.csv row-level data at
  `comparison_2022_vs_2024_v1/comparison.csv`; per-candidate
  compilation manifests at `data/compiled_strategies/<hash>.json`.
  No artifact gap for Q-B3.b operational start.
- **Q-B4:** Requires DSR infrastructure code + tests + integration
  with experiment registry. Consumes existing batch_summary +
  hypothesis-attempted counts; produces DSR-deflated Sharpe outputs
  + multiple-testing null-distribution artifacts at
  `agents/dsr_*/` paths.

### Axis 3 — Operational scope (structural complexity + session count)

Per Observation FFF, cost framing distinguishes structural complexity
from session-count estimates. Both are operational considerations
that affect path-comparison adjudication.

| Path | Structural complexity | Session count | Compute time | New infrastructure required |
|------|----------------------:|:-------------:|:------------:|:---------------------------:|
| Q-B1 | High | 10-15 | ~12-20 min/regime, n≥3 regimes | Multi-regime orchestration + n-regime comparison matrix |
| Q-B2 | Medium-high | 8-12 | tens of minutes (partition-only) | Calibration parameterization + partition-scoring framework |
| Q-B3.a | Medium (downstream of Q-B1) | 2-4 (after Q-B1) | ~10 sec/regime for 8 candidates | None new (extends Q-B1 outputs) |
| Q-B3.b | Low | 3-5 | 0 (no evaluation runs) | None (descriptive analysis on existing artifacts) |
| Q-B4 | Low-medium | 6-8 | n/a | DSR infrastructure code + tests |

Q-B1 has the highest operational scope; Q-B3.b has the lowest. This
axis adjudicates intermediate-arc-throughput vs full-mechanism-arc
considerations: Q-B3.b is the smallest intermediate arc available;
Q-B1 is the full-mechanism-arc with broadest coverage but highest
operational scope.

### Axis 4 — Path dependencies

Per Meta-3 + Observation GGG, dependency cross-references are
operational (artifact-level specificity), not just structural.

**Path dependency graph:**

- **Q-B1**: Independent (no upstream dependencies). Upstream of
  Q-B3.a (third-regime artifacts at
  `data/phase2c_evaluation_gate/<third_regime>_v1/`) and Q-B4
  (DSR adjudication framing shifts with cross-regime evidence
  base size).
- **Q-B2**: Independent (no upstream dependencies; uses existing
  PHASE2C_7.1 per-candidate evaluation data only).
- **Q-B3.a**: Q-B1-dependent (consumes Q-B1's third-regime
  evaluation artifacts). Structurally downstream of Q-B1.
  Independent of Q-B2/Q-B3.b/Q-B4.
- **Q-B3.b**: Independent (operates within existing PHASE2C_7.1
  artifact set; no upstream dependencies). Could run in parallel
  with or before any other Q-B path.
- **Q-B4**: Q-B1-dependent (DSR adjudication framing shifts based
  on what the cross-regime evidence base looks like; Q-B4 after
  Q-B1's output is more rigorously bounded). Structurally
  downstream of Q-B1 (parallel to Q-B3.a's downstream
  relationship). Independent of Q-B2/Q-B3.

**Sequencing implications.** Q-B1 unlocks Q-B3.a + Q-B4 as
downstream paths; Q-B2/Q-B3.b are independent and can run in any
order. The sequencing structure suggests two natural orderings if
multiple paths are pursued sequentially:

1. Q-B1 first → Q-B3.a or Q-B4 second (full mechanism + cohort or
   meta-infrastructure follow-on).
2. Q-B3.b first → Q-B1 second (small intermediate arc + full
   mechanism).

Q-B2 fits orthogonally in either ordering; the calibration axis is
independent of regime axis and cohort investigation.

### Axis 5 — 2025 test split touched-once preservation (CLAUDE.md hard rule)

This axis is a universal constraint, not a per-path discriminator.
All five paths preserve the 2025 test split touched-once per
CLAUDE.md hard rule.

- **Q-B1**: Additional historical regimes selected for multi-regime
  evaluation come from regimes other than the 2025 test split.
  Specific additional regimes are NOT pre-named here; selection is
  itself a scoping decision within the follow-up implementation arc
  per §3 anti-pre-naming.
- **Q-B2**: Calibration variation is within bear_2022 and
  validation_2024 only; does not consume 2025 test split.
- **Q-B3.a**: Operates on Q-B1's additional regimes; same 2025
  preservation constraint applies via Q-B1.
- **Q-B3.b**: Within-existing-evidence; PHASE2C_7.1 artifact set
  does not include 2025 test split data.
- **Q-B4**: DSR meta-infrastructure; consumes batch_summary +
  hypothesis-attempted counts only; does not consume 2025 test
  split data.

The constraint is structural: any path that proposed to evaluate
against 2025 would violate the CLAUDE.md hard rule and would not be
admissible as a candidate path under PHASE2C_8.0 scoping. None of
the five paths under consideration violate this constraint.

### Decision-criteria summary

| Axis | Q-B1 | Q-B2 | Q-B3.a | Q-B3.b | Q-B4 |
|------|:----:|:----:|:------:|:------:|:----:|
| **1. Mechanism-question coverage** | Highest (regime axis; 4 of 5 Q-A questions) | Medium (calibration axis; 2 of 5 Q-A) | Low (cohort-level only) | Lowest (descriptive within-batch) | None (meta-infrastructure) |
| **2. Evidence-base requirements** | New multi-regime artifacts | Partition-only on existing artifacts | Q-B1 outputs required | Existing artifacts only | DSR infrastructure code |
| **3. Operational scope** | Highest (10-15 sessions; multi-regime orchestration) | Medium-high (8-12 sessions) | Medium (2-4 sessions, after Q-B1) | Lowest (3-5 sessions; smallest intermediate arc) | Low-medium (6-8 sessions) |
| **4. Path dependencies** | Independent (upstream of Q-B3.a + Q-B4) | Independent | Q-B1-dependent (downstream) | Independent | Q-B1-dependent (downstream) |
| **5. 2025 test split touched-once** | Preserved | Preserved | Preserved (via Q-B1) | Preserved (existing artifacts) | Preserved |

Q-B1 emerges as the path with broadest mechanism-question coverage
at highest operational scope; Q-B3.b emerges as the smallest
intermediate arc with lowest mechanism-question contribution.
Q-B2's calibration-axis scope is narrower than Q-B1's regime-axis
scope. Q-B3.a + Q-B4 have structural Q-B1-dependency that constrains
their independent prioritization. Axis 5 is universal-preserved
across all paths.

§5 carries the recommended scoping decision based on this multi-axis
adjudication.


## 5. Recommendation

**Recommended scoping decision: Q-B1 — additional-regime evaluation
before calibration variation, cohort deep-dive, or DSR
infrastructure.**

This recommendation is the post-adjudication scoping decision based
on the multi-axis comparison in §4. The pairwise comparisons below
adjudicate Q-B1 against each alternative explicitly, with Q-B1 vs
Q-B3.b receiving the most careful treatment because Q-B3.b is the
structurally most distinct alternative (smallest intermediate arc
with within-existing-evidence scope vs Q-B1's full-mechanism-arc with
multi-regime evidence base). The closing sub-paragraph names what
evidence would shift the recommendation.

### Pairwise comparison 1: Q-B1 vs Q-B2 (regime axis vs calibration axis)

Both Q-B1 and Q-B2 are empirically-extending paths that advance Q-A1
(three-mechanism candidate explanation), but they advance distinct
mechanism-axis components.

- **Q-B1 advances:** regime-mismatch vs regime-independent
  disambiguation (regime-axis variation across additional regimes
  at n≥3). Does NOT distinguish pattern-overfit from calibration-
  coupling within regime-independent mechanisms.
- **Q-B2 advances:** calibration-coupling vs regime-or-pattern
  disambiguation (calibration-axis variation across thresholds
  within bear_2022 and validation_2024). Does NOT distinguish
  regime-mismatch from pattern-overfit within regime-or-pattern
  mechanisms.

The mechanism-axis priority adjudication: regime-axis variation has
broader Q-A coverage than calibration-axis variation per §4 axis 1
(Q-B1 advances 4 of 5 Q-A questions; Q-B2 advances 2 of 5 Q-A
questions). Q-B1's regime-axis evidence base also feeds Q-B3.a +
Q-B4 as downstream paths per §4 axis 4; Q-B2 is independent of
those downstream paths.

**Q-B1 over Q-B2 because:** regime-axis variation has broader
mechanism-question coverage, broader Q-A advancement (4 of 5 vs 2
of 5), and unlocks downstream paths (Q-B3.a + Q-B4) for sequencing.
Q-B2 remains a defensible alternative if calibration-coupling
evidence surfaces independently as the primary mechanism candidate
(see closing conditional-shift sub-paragraph).

### Pairwise comparison 2: Q-B1 vs Q-B3.a (full mechanism arc vs cohort cross-regime extension)

Q-B3.a is structurally downstream of Q-B1 per §4 axis 4. The
comparison is structurally about ordering, not about path
selection: Q-B3.a cannot operationally proceed without Q-B1's
third-regime evidence base.

- **Q-B1 produces:** the multi-regime evidence base that Q-B3.a
  consumes. Operational artifact:
  `data/phase2c_evaluation_gate/<third_regime>_v1/` paths.
- **Q-B3.a consumes:** Q-B1's third-regime evaluation artifacts to
  investigate cohort (a)'s 8 cross-regime survivors' carry-forward
  to a third regime. Cannot proceed without Q-B1's outputs.

**Q-B1 over Q-B3.a because:** Q-B3.a structural dependency makes
"Q-B3.a first" operationally impossible. Q-B1 first is the natural
sequencing per §4 axis 4. Q-B3.a remains a defensible follow-up
path after Q-B1 lands as the implementation arc.

### Pairwise comparison 3: Q-B1 vs Q-B3.b (full mechanism arc vs smallest intermediate arc)

This is the structurally most distinct comparison and receives the
most careful treatment. Q-B3.b is the smallest intermediate arc
available — within-existing-evidence cohort characterization with no
new evaluation runs, no multi-regime infrastructure, no Q-B1
dependency. Q-B1 is the full-mechanism arc — multi-regime evaluation
at n≥3 with broadest Q-A coverage, broadest infrastructure
investment, and largest operational scope.

The trade is **mechanism-question advance vs intermediate-arc
throughput.**

**Q-B1's contribution:**

- Advances 4 of 5 Q-A questions (Q-A1 partial, Q-A2 direct, Q-A3
  direct, Q-A4 partial, Q-A5 partial) per §4 axis 1.
- Produces multi-regime evidence base (PHASE2C_7.1 closeout §6
  category 3 mechanism question becomes empirically advanceable
  for the regime-axis component).
- Unlocks Q-B3.a + Q-B4 as downstream paths per §4 axis 4.
- Operational scope: highest (10-15 sessions per §4 axis 3;
  multi-regime orchestration + n-regime comparison matrix
  infrastructure required).

**Q-B3.b's contribution:**

- Advances 0-1 of 5 Q-A questions (partial Q-A3 within-batch
  correlates only) per §4 axis 1.
- Produces descriptive cohort characterization within existing
  PHASE2C_7.1 artifact set; no new evaluation runs.
- Independent of all other Q-B paths; could run in parallel with
  or before Q-B1.
- Operational scope: lowest (3-5 sessions per §4 axis 3;
  smallest intermediate arc available).

**Adjudication rationale.** Q-B3.b's intermediate-arc-throughput
value is real but bounded — at 0-1 of 5 Q-A advancement, Q-B3.b
produces descriptive evidence without advancing the mechanism
question that PHASE2C_7.1 §6 category 3 named as the central
unresolved issue. PHASE2C_7.1's closeout established that mechanism
adjudication is empirically underdetermined within the two tested
regimes; Q-B3.b's within-existing-evidence scope cannot resolve
this underdetermination because the underdetermination is inherent
to the n=2 regime evidence base, not to descriptive cohort
properties within the batch.

Q-B1's full-mechanism scope addresses the underdetermination
directly by extending the regime evidence base to n≥3. The
operational-scope cost (10-15 sessions vs 3-5) is real but
proportional to the research yield (4 of 5 Q-A advancement vs 0-1
of 5).

A defensible alternative framing: pursue Q-B3.b first as a small
intermediate arc, THEN Q-B1 second. This sequencing is not ruled
out by the recommended scoping decision; it is a different scoping
posture (intermediate-arc-throughput-first rather than mechanism-
question-advance-first). The recommended Q-B1 lean is based on
mechanism-question advance being the more load-bearing PHASE2C_8
research yield given PHASE2C_7.1's closeout.

**Q-B1 over Q-B3.b because:** the load-bearing PHASE2C_8 research
yield is mechanism-question advance (Q-A1 disambiguation), not
descriptive cohort characterization. Q-B3.b would produce evidence
about cohort (a) characteristics without advancing the mechanism
question; Q-B1 advances the mechanism question directly.

Q-B3.b remains a defensible alternative if cohort (a) structural
properties surface independently as a research-yield-justifying
investigation (see closing conditional-shift sub-paragraph).

### Pairwise comparison 4: Q-B1 vs Q-B4 (full mechanism arc vs DSR meta-infrastructure)

Q-B4 is structurally downstream of Q-B1 per §4 axis 4. The DSR
adjudication framing shifts based on what the cross-regime evidence
base looks like; Q-B4 before Q-B1 produces DSR infrastructure with
n=0 cross-regime evidence base; Q-B4 after Q-B1 produces DSR
infrastructure with cross-regime evidence base scaled by Q-B1's
regime extension.

- **Q-B1 produces:** cross-regime evidence base (regime axis
  extended from n=2 to n≥3); DSR adjudication scope evolves with
  the larger evidence base.
- **Q-B4 consumes:** the cross-regime evidence base size to
  determine DSR meaningfulness scaling. Operational at any
  cross-regime evidence size, but more rigorously bounded after
  Q-B1's output.

**Q-B1 over Q-B4 because:** Q-B4's adjudication is more rigorously
bounded after Q-B1's output; running Q-B4 first produces DSR
infrastructure operating on n=0 cross-regime evidence base, which
is structurally below DSR's effective range. Q-B1 first ensures
Q-B4's adjudication operates on meaningful evidence base size.

Q-B4 remains a defensible follow-up path after Q-B1 lands;
DSR-mandatory thresholds for cross-regime evidence base size could
be re-evaluated within the follow-up implementation arc per §4
axis 4 sequencing.

### What evidence would shift this recommendation

The recommended scoping decision (Q-B1) is post-adjudication based
on the multi-axis comparison in §4 + pairwise comparisons above.
The recommendation is conditional on the current evidence base; the
following types of evidence would shift the recommendation toward
an alternative path.

**None of these conditions is currently satisfied by PHASE2C_7.1;
they are explicit revision triggers for future scoping, not caveats
to the current recommendation.** Each shift condition names what
new evidence would emerge AFTER PHASE2C_7.1's existing evidence
base — not interpretations of PHASE2C_7.1's existing evidence base
that would weaken the current recommendation. The recommendation
register holds as post-adjudication commitment under PHASE2C_7.1's
current evidence; the conditional-shift framing operates as
falsifiability discipline that bounds the recommendation's evidence
base for future scoping cycles.

**Shift toward Q-B2 (calibration variation) if:** an exploratory
analysis surfaces calibration-coupling evidence as the primary
mechanism candidate. Example: a quick within-bear_2022 calibration
check (e.g., evaluating WF gate at thresholds 0.0 / 0.25 / 0.75 /
1.0 alongside the canonical 0.5) shows substantial selection-power
shift across thresholds. This would reframe Q-A1's three-mechanism
question with calibration-coupling as more load-bearing than
regime-mismatch; Q-B2 would then become the higher-yield path.

**Shift toward Q-B3.b (cohort within-existing-evidence) if:**
cohort (a)'s 8 candidates surface structural distinctness in
PHASE2C_7.1 existing evidence that warrants deeper descriptive
investigation. Example: cohort (a)'s 5 calendar_effect candidates
share trade-pattern characteristics that distinguish them from
cohort (b)'s 22 primary 2024-survivors. Identifying this
distinctness is itself research-yield-justifying as a precursor
investigation; Q-B3.b would surface from intermediate-arc-throughput
to recommended-arc status.

**Shift toward Q-B3.a (cohort cross-regime extension) if:** Q-B1's
output produces a third-regime evaluation that surfaces unexpected
cohort (a) carry-forward patterns. This is a sequencing decision
within Q-B1 + Q-B3.a: Q-B3.a as immediate Q-B1 follow-on becomes
higher-yield than Q-B4 if cohort-level evidence is more
load-bearing than DSR meta-infrastructure.

**Shift toward Q-B4 (DSR infrastructure) if:** the follow-up
implementation arc's output produces sufficient cross-regime
evidence base to make DSR meaningfulness scaling structurally
productive. This is a sequencing decision after Q-B1 lands; Q-B4
becomes higher-yield as the cross-regime evidence base size grows.

**Shift toward "no PHASE2C_8 implementation arc" if:** the
follow-up implementation arc design surfaces operational constraints
(e.g., regime-source data availability, infrastructure investment
cost overruns) that make Q-B1 operational scope infeasible within
PHASE2C_8 scoping. This is a structural shift, not a substantive
shift; the recommendation register holds Q-B1 as the substantively
preferred path conditional on feasibility.

The recommendation register is post-adjudication commitment under
current evidence base; the conditional-shift framing is the
falsifiability discipline that bounds the recommendation's evidence
base. Per METHODOLOGY_NOTES §1 + §2 + §6, the recommendation is
auditable + falsifiable + bounded.


## 6. In-scope and out-of-scope for the recommended PHASE2C_8.1 implementation arc

The recommended scoping decision is Q-B1 (per §5). The PHASE2C_8.1
follow-up implementation arc operates on Q-B1's scope. This section
catalogs what is in-scope for PHASE2C_8.1, the universal constraints
that apply across all PHASE2C_8.1 work, and what is out-of-scope.

### In-scope for PHASE2C_8.1

- **Multi-regime evaluation orchestration extension.** Extend
  PHASE2C_7.1's two-regime evaluation infrastructure (regime-
  attestation discipline; per-regime artifact directory pattern;
  candidate-aligned cross-regime comparison-matrix machinery) to
  n≥3 regime structure. Existing producer scripts at
  `scripts/run_phase2c_evaluation_gate.py` extend with multi-regime
  orchestration; existing comparison scripts at
  `scripts/compare_2022_vs_2024.py` extend to n-regime comparison.
- **Regime selection within the implementation arc.** Selection of
  which additional historical regimes to evaluate against is itself
  a scoping decision within the PHASE2C_8.1 drafting cycle. Specific
  regime selection is NOT pre-named in PHASE2C_8.0 scoping;
  PHASE2C_8.1's first sub-step is regime-source scoping.
- **Same 198-candidate input universe.** PHASE2C_8.1 evaluates the
  same 198 candidates from PHASE2C_6 batch
  `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`. Source:
  PHASE2C_7.1 closeout's input universe (`audit_v1` /
  `audit_2024_v1` paths). New per-regime artifacts produced at
  `data/phase2c_evaluation_gate/<regime>_v1/` directory pattern.
- **Same 4-criterion AND-gate.** Sharpe ≥ −0.5; max_drawdown ≤
  0.25; total_return ≥ −0.15; total_trades ≥ 5. Per PHASE2C_7.1 §4
  + `config/environments.yaml splits.regime_holdout.passing_criteria`.
- **Trade-count filter at `>= 20`.** Per PHASE2C_7.1 §5.3 Rule 1
  pre-specification anti-tuning discipline. Filter pinned at code-
  level constant; not a runtime parameter.
- **Candidate-aligned cross-regime comparison matrix at n≥3.**
  Comparison artifact pattern from PHASE2C_7.1
  (`comparison_2022_vs_2024_v1/`) extended to n-regime structure.
  New artifact path TBD within PHASE2C_8.1 drafting (e.g.,
  `comparison_n_regime_v1/` per PHASE2C_8.1 scoping).
- **Per-regime artifact attestation discipline.** PHASE2C_7.1
  closeout's schema discriminator pattern (artifact_schema_version
  + regime_key + regime_label + run_id) applies to each new regime
  artifact set.
- **PHASE2C_8.1 closeout drafting + commit.** Closeout document at
  `docs/closeout/PHASE2C_8_1_RESULTS.md` (path TBD per drafting
  cycle naming); follows PHASE2C_7.1's 11-section pattern adapted
  for n≥3 regime evidence base; mandatory adversarial review per
  METHODOLOGY_NOTES §12.

### Universal constraints (apply across all PHASE2C_8.1 work)

- **Closeout discipline.** PHASE2C_8.1 closeout document follows the
  PHASE2C_6.6 + PHASE2C_7.1 closeout pattern (bounded framing,
  explicit non-claims, empirically-grounded findings, methodology
  principles applied per METHODOLOGY_NOTES §1 + §2 + §6 + §7 + §10
  conditional applicability).
- **Lineage discipline.** Section RS of
  `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md` applies to all
  multi-regime artifacts. Existing `check_evaluation_semantics_or_raise`
  guard applies for single-run holdout attestation domain (PHASE2C_6 +
  PHASE2C_7.1 pattern).
- **Methodology principles application.**
  [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
  §1-§12 apply throughout PHASE2C_8.1, with conditional-boundary
  application: §1 (empirical verification at framing-summary stage),
  §2 (meta-claim verification on framing claims), §6 (commit messages
  not canonical), §7 (asymmetric confidence reporting at multi-regime
  scale), §9 (Path-2 outline-first drafting if PHASE2C_8.1 closeout's
  load-bearing interpretive section carries multi-direction findings),
  §10 (anti-pre-naming for forward-pointers), §11 (closeout-assembly
  checklist if PHASE2C_8.1 has multi-cycle drafting), §12 (mandatory
  adversarial review on closeout commit).
- **Schema discriminator continuity.** PHASE2C_7.1's artifact schema
  pattern (`phase2c_7_1`) extends to PHASE2C_8.1 with new
  discriminator value (`phase2c_8_1`); cross-arc schema-name
  consistency preserved per V6 verification.

### Out-of-scope for PHASE2C_8.1

#### Q-B path alternatives explicitly deferred

The §5 recommendation lands Q-B1 as the recommended scoping decision.
The other Q-B paths are deferred per scoping decision; they could
surface in subsequent scoping cycles if the conditional-shift
triggers in §5 emerge. This is non-rejection framing — Q-B2 / Q-B3.a
/ Q-B3.b / Q-B4 are not structurally inferior; they are defensible
alternatives that PHASE2C_8.0 scoping prioritized after multi-axis
adjudication.

- **Q-B2 (calibration variation within a regime; Path C revisit)
  deferred.** Not in PHASE2C_8.1 scope. Could surface in a
  subsequent scoping cycle if calibration-coupling evidence
  emerges as the primary mechanism candidate per §5 conditional-
  shift sub-paragraph.
- **Q-B3.a (cohort cross-regime extension) deferred.** Not in
  PHASE2C_8.1 scope. Q-B3.a is structurally downstream of
  PHASE2C_8.1's Q-B1 scope — Q-B3.a could surface as a follow-on
  arc after PHASE2C_8.1 lands per §5 conditional-shift framing.
- **Q-B3.b (cohort within-existing-evidence) deferred.** Not in
  PHASE2C_8.1 scope. Could surface in a subsequent scoping cycle
  if cohort (a) structural-distinctness evidence emerges as
  research-yield-justifying per §5 conditional-shift sub-paragraph.
- **Q-B4 (DSR infrastructure investment) deferred.** Not in
  PHASE2C_8.1 scope. Q-B4 is structurally downstream of PHASE2C_8.1's
  Q-B1 output (DSR adjudication framing shifts with cross-regime
  evidence base size). Q-B4 could surface as a follow-on arc after
  PHASE2C_8.1 lands per §5 conditional-shift framing.

#### Universal out-of-scope items (apply to all PHASE2C_8.1 work)

- **2025 test split is preserved touched-once.** The 2025 test
  split per `config/environments.yaml`'s touched-once discipline is
  reserved for final evaluation per project-standing methodology.
  PHASE2C_8.1's additional historical regimes for multi-regime
  evaluation come from regimes other than the 2025 test split;
  selection of additional regimes is itself a scoping decision
  within PHASE2C_8.1 drafting per the in-scope item above.
  Touching 2025 during PHASE2C_8.1 would burn the test-split's
  one-shot status on a question multi-regime additional-historical-
  regime evaluation can answer.
- **`config/environments.yaml` modification is out-of-scope.** The
  IMMUTABLE-config CLAUDE.md hard rule preserved across PHASE2C_8.1.
  PHASE2C_7.1's read-only runtime inheritance pattern (validation
  block inherits passing_criteria from regime_holdout block at
  evaluation time) extends to PHASE2C_8.1's additional regimes if
  any selected additional regimes have implicit cross-block
  inheritance dependencies. No new fields added to
  `config/environments.yaml`; no schema version bumps.
- **Theme-targeted candidate generation is deferred.** Generation
  paths informed by PHASE2C_7.1's by-theme findings (calendar_effect
  within-theme inversion; mean_reversion drawdown-attenuation;
  volatility_regime non-engagement; momentum within-theme inversion;
  volume_divergence stable cross-regime) are not in PHASE2C_8.1
  scope. Candidate-generation paths are deferred until multi-regime
  evidence about which patterns generalize is available; PHASE2C_8.1
  produces that evidence base. PHASE2C_7.1 §9.C non-decision
  carries forward.
- **DSR / CPCV / MDS execution beyond Q-B4 deferral.** Q-B4 is
  deferred per the §6.A explicit deferral; DSR execution is
  out-of-scope for PHASE2C_8.1. PHASE2C_7.1 §9.C non-decision
  carries forward.
- **Strategy promotion.** No candidate is promoted to validation,
  test, paper-trading, or live evaluation as a result of
  PHASE2C_8.1 work. PHASE2C_7.1 §9.C non-decision carries forward.
- **Audit-only post-hoc promotion is out-of-scope.** Cohort (a)'s
  8 cross-regime survivors from PHASE2C_7.1 are diagnostic material;
  PHASE2C_8.1's Q-B1 evaluation extends the diagnostic evidence
  base but does not promote any cohort (a) candidate to actionable
  status. The pre-registered-question discipline from PHASE2C_6.6
  + PHASE2C_7.1 carries forward.
- **Methodology amendments not empirically motivated by PHASE2C_8.1
  are out-of-scope.** New METHODOLOGY_NOTES.md sections, revised
  4-criterion gate definitions, or modifications to lineage
  discipline beyond what PHASE2C_8.1's empirical findings
  demonstrate are out-of-scope for PHASE2C_8.1. Discipline lessons
  surfaced during PHASE2C_8.1 work are captured as a follow-up
  update to METHODOLOGY_NOTES.md after the closeout (same hybrid
  handling as PHASE2C_6.6 → `536f737` and PHASE2C_7.1 → `76e46d4`).

### Note on PHASE2C_8.1 closeout shape

PHASE2C_8.1's closeout will follow PHASE2C_7.1's 11-section structure
(scope/verdict, scope catalog, input universe attestation, evaluation
gate spec, primary findings adjudication, bounded claims firewall,
cohort enumeration, by-theme interpretation, mechanism implications +
follow-up scoping questions, methodology-discipline observations,
references and reproducibility). Adjustments for n≥3 regime evidence
base are appropriate at PHASE2C_8.1 closeout drafting. Whether
PHASE2C_8.1 produces multi-direction findings (regime-axis +
cohort-level + carry-forward cuts) requiring Path-2 outline-first
drafting per METHODOLOGY_NOTES §9 is a PHASE2C_8.1 framing-cycle
decision, not pre-committed in PHASE2C_8.0 scoping.


## 7. Required discipline carry-forward from PHASE2C_7.1

The PHASE2C_6 → PHASE2C_7.0 → PHASE2C_7.1 → PHASE2C_7.1.7 arc
sequence + the METHODOLOGY_NOTES update (commit `76e46d4`) surfaced
and codified discipline patterns that PHASE2C_8 inherits as standing
project context. This section enumerates the patterns and how each applies to
the follow-up implementation arc. These are project-
discipline principles that operate at the recommended-Q-B1
implementation arc level; §6 names path-specific scope obligations,
while §7 names path-independent discipline patterns plus
methodology principles per their conditional-boundary structure.

### 1. Cohort survivors as diagnostic material, not strategy recommendations

PHASE2C_6 closeout §9 framed the 12 audit-only survivors as
diagnostic evidence about gate divergence. PHASE2C_7.1 closeout §7
extended this to cohort (a) (8 cross-regime survivors), cohort (b)
(22 primary 2024-survivors), and cohort (c) (13 PHASE2C_6 holdout-
survivors with 2024 outcomes). Both arc closures preserved
diagnostic-material framing without strategy-recommendation
implications.

This framing carries forward unchanged. Any evidence the
follow-up implementation arc produces about cohort survivors at multi-regime
evidence base — whether cohort (a) candidates carry forward to a
third regime, whether new cross-regime intersection cohorts emerge
under n≥3 evaluation, whether failure-mode signatures persist or
shift — is diagnostic, not actionable. The carry-forward is
structural: the implementation arc must not treat any cohort as candidates
that earned promotion through cross-regime survival.

### 2. Pre-registered questions, not post-hoc fishing

PHASE2C_6 closeout §9 codified pre-registered-question discipline
for cohort investigation. PHASE2C_7.1 closeout §9 extended this to
cross-regime intersection cohorts. Both arcs treated cohort
investigation under explicit pre-registered framings, not
opportunistic post-hoc analysis.

This discipline applies to the follow-up implementation arc unchanged. New questions
raised mid-arc about candidate properties, by-theme patterns,
mechanism candidates, or cohort generalization must be addressed
via pre-registered follow-up framings rather than opportunistic
analysis of arc outputs. The follow-up implementation arc's regime-source
selection within the implementation arc per §6 in-scope counts as
an explicit pre-registration step; subsequent investigation
questions surfaced during the follow-up implementation arc work can be captured as
follow-up scoping for subsequent arcs.

### 3. Bounded framing throughout

PHASE2C_6.6 maintained "in this batch, against 2022 regime, this
gate calibration" bounding. PHASE2C_7.1 extended bounds to multi-
direction multi-regime claims with three-cuts-as-different-estimands
discipline ("regime-dependent and not robustly preserved across the
two tested regimes" — never "the WF gate works/fails in 2024").
Both arcs preserved interpretation-scope bounds.

The follow-up implementation arc's findings carry the same discipline. Claims should be
bounded to the regimes evaluated (n≥3 specific regimes selected
within the follow-up implementation arc), the candidate population evaluated (the same
198-candidate input universe), and the gate calibrations used (the
canonical 4-criterion AND-gate). Generic statements about "WF
methodology" or "candidate alpha quality at multi-regime scale"
remain out-of-bounds without explicit empirical scope. Per
METHODOLOGY_NOTES §9 (Path-2 outline-first drafting), if the follow-up implementation arc
closeout's headline-bearing interpretive section carries multi-
direction findings (likely under multi-regime evaluation), the
bounded-framing discipline extends to multi-direction-aware
register: each direction-cut is a different estimand and should
not be collapsed into a single verdict.

### 4. Scaling-step discipline (METHODOLOGY_NOTES §4)

PHASE2C_6's smoke (4) → primary (44) → audit (198) sequence and
PHASE2C_7.1's smoke (5) → audit_2024 (198) → audit_2024_filtered
(144) sequence demonstrate scaling-step discipline operationally.
Each step's data treated as supporting only its own scope of
claim; intermediate-step data not over-extended to claims requiring
later-step evidence.

The follow-up implementation arc's evaluation across n≥3 regimes will likely have an
analogous scaling-step structure (e.g., per-regime smoke validation
before full-population n≥3 evaluation). Each step's data must be
treated as supporting only its own scope of claim; cross-regime
claims require all regime evaluations to complete before population-
level multi-regime claims can land.

### 5. No "WF methodology is broken" or "WF gate is regime-coupled" generalizations

PHASE2C_6 explicitly disclaimed that the within-batch finding does
not imply walk-forward methodology is broken. PHASE2C_7.1 extended
this disclaimer to multi-regime context — the regime-dependent
finding does not imply regime-mismatch is the operating mechanism;
mechanism adjudication remains undetermined per §6 category 3.

Whatever the follow-up implementation arc finds — whether the regime-dependent pattern
generalizes across additional regimes, whether mechanism candidates
disambiguate, whether cohort generalization holds — the follow-up implementation arc
must maintain the methodology-vs-metric + within-batch-vs-
generalization distinctions. The "WF gate is regime-coupled"
generalization is the new over-claim that the follow-up implementation arc must
foreclose at multi-regime scale; "the WF gate's regime-dependence
extends across the n=3 (or more) regimes evaluated in this arc"
is the canonical bounded form.

### 6. METHODOLOGY_NOTES §1-§12 application (post-update commit `76e46d4`)

The follow-up implementation arc inherits the twelve principles codified in
[`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
(commit `76e46d4`). Application is conditional on the follow-up
implementation arc's actual scope structure per the cost-portfolio observation in MN §8:

**Apply by current scope (the follow-up implementation arc = high-load closeout with
multi-regime evaluation + load-bearing finding sections):**

- **§1 Empirical verification for factual claims** (with WHEN/HOW
  axes per the §1 strengthening): every specific number in
  the follow-up implementation arc prose traces to canonical data; recompute-before-
  prose at framing-summary stage applies to data-density sections;
  V7 grep-able citation discipline applies to every numerical
  claim.
- **§2 Meta-claim verification discipline:** confident process
  claims ("we've verified," "the framing is pinned") need
  empirical discipline; applies to the follow-up implementation arc framing claims +
  recommendation reasoning + meta-attestations.
- **§3 Regime-aware calibration bands:** expected-behavior bands
  set in the follow-up implementation arc dispatches or analyses must reference the
  actual regime structure being evaluated. Cross-regime calibration
  bands at n≥3 require regime-specific framing.
- **§4 Scale-step discipline:** detailed in §7 carry-forward item
  4 above.
- **§5 Precondition verification for structural and organizational
  principles:** structural recommendations during the follow-up implementation arc
  drafting and review must verify preconditions for the specific
  case.
- **§6 Commit messages not canonical result layers:** if the follow-up implementation arc
  commit messages carry preliminary characterizations refined by
  closeout-time empirical verification, the closeout is canonical
  and silent correction in the closeout is the discipline.
- **§7 Asymmetric confidence reporting on multi-sample claims:**
  if the follow-up implementation arc findings span sub-samples of different sizes
  (per-regime populations, per-cohort populations), each sub-claim
  calibrates to its own supporting sample.
- **§10 Anti-pre-naming as standing discipline:** the follow-up implementation arc's
  forward-pointer prose (§9-equivalent follow-up scoping section,
  §10-equivalent methodology observations) uses generic phrasing
  ("follow-up scoping" / "subsequent arc closeouts") — does not
  pre-name PHASE2C_9, PHASE2C_8.2, or specific future-arc
  identifiers in body prose. Meta-attestation verification at-
  assembly (not at-section-seal) catches residual-reference
  falsifications.

**Apply if scope shifts (the follow-up implementation arc = current scope satisfies
preconditions):**

- **§9 Path-2 outline-first drafting for load-bearing interpretive
  sections:** applies if the follow-up implementation arc's headline-bearing section
  (typically §5) carries multi-direction findings. Multi-regime
  evaluation at n≥3 likely produces multi-direction findings (per-
  regime cuts + cross-regime intersection cuts + carry-forward
  cuts); §9 likely applies. Headline classification step at §9
  Application checklist item 1 is the trigger: any of multiple
  internally-consistent readings, multi-regime adjudications, or
  multi-cut estimand distinctions warrants Path-2 outline-first.
- **§11 Closeout-assembly checklist as running drafting-cycle
  pattern:** applies if the follow-up implementation arc has multi-cycle drafting (likely
  given scope's multiple sections + multiple regime evaluations).
  Tracked-fix vs blocking-defect distinction applies to fixes
  surfaced mid-cycle. Byte-identical reproducibility check applies
  to closeout-assembly outputs.
- **§12 Internal verification and adversarial review as
  complementary defect-class coverage:** applies if the follow-up implementation arc is
  high-load closeout (likely given scope: load-bearing finding
  sections + numerical claims at body-prose resolution + cross-
  section adjudication register). Mandatory adversarial review
  (Codex `codex review`) before merge/tag; findings folded as
  separate review-response commit; V1-V7 re-run post-fold.

The conditional-boundary structure protects the follow-up implementation arc from
applying disciplines that don't fit its actual scope. If the follow-up implementation arc's
scope evolves during drafting (e.g., reduced to single-regime
calibration variation), §9 + §11 + §12 conditional-boundaries
re-evaluate — possibly applies-if-shifts becomes does-not-apply,
or vice versa. The cost-portfolio observation per MN §8 makes the
conditional structure operational.

### 7. Touched-once 2025 preservation

The 2025 test split's touched-once status is preserved across
the implementation arc's work. The follow-up implementation arc's additional historical regimes for
multi-regime evaluation come from regimes other than the 2025 test
split per §6 in-scope. (Operational prohibition detailed in §6
out-of-scope; project-discipline basis in
`config/environments.yaml`'s split semantics and `CLAUDE.md`'s
date-split and research-discipline rules.)

### 8. Engine corrected lineage continuity

PHASE2C_7.1's wf-corrected-v1 engine (commit `eb1c87f`; tag
`wf-corrected-v1`) + lineage discipline at
[`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) carry
forward to the follow-up implementation arc. All multi-regime evaluation artifacts
must consume corrected-engine WF outputs; existing
`check_evaluation_semantics_or_raise()` guard applies for single-
run holdout attestation domain. Section RS of
[`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md)
applies to all the follow-up implementation arc artifacts consuming corrected-engine
outputs.

### 9. Schema discriminator continuity

PHASE2C_7.1's artifact schema discriminator pattern (`phase2c_7_1`)
extends to the follow-up implementation arc with new discriminator value (`phase2c_8_1`).
Schema fields preserved across continuity:
`artifact_schema_version`, `regime_key`, `regime_label`, `run_id`,
`engine_corrected_lineage`, `evaluation_semantics`. New regime
attestation per evaluation requires the discriminator pattern
applied uniformly. V6 verification (schema-name consistency) at the follow-up
implementation arc's closeout-assembly catches drift.


## 8. Exact next implementation artifact (PHASE2C_8.1)

PHASE2C_8.1 is the implementation arc following PHASE2C_8.0's
recommended scoping decision (Q-B1 — additional-regime evaluation
at n≥3 per §5). This section provides PHASE2C_8.1's one-paragraph
skeleton + 5-step deliverable structure. Spec-level detail (regime
selection rationale, exact n value, calibration set if extended,
specific orchestration commands) is deferred to PHASE2C_8.1
itself; the skeleton here names structure + bounded duration +
success criteria cross-references, not prescriptive specifications.

**PHASE2C_8.1 skeleton.**

PHASE2C_8.1 extends PHASE2C_7.1's two-regime evaluation
infrastructure to n≥3 regime structure. Producer artifact at
[`scripts/run_phase2c_evaluation_gate.py`](../../scripts/run_phase2c_evaluation_gate.py)
(extended for multi-regime orchestration with `--regime-key` flag
already implemented in PHASE2C_7.1 sub-step 1.3). Comparison
artifact at
[`scripts/compare_2022_vs_2024.py`](../../scripts/compare_2022_vs_2024.py)
(extended to n-regime comparison structure). Scope envelope:
evaluate the same 198 candidates from batch
`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` against additional historical
regimes (n≥3 total regimes including PHASE2C_7.1's two: bear_2022
and validation_2024). Specific additional regimes are NOT pre-named
in PHASE2C_8.0 scoping; regime-source selection is PHASE2C_8.1's
first sub-step per §6 in-scope item. The 2025 test split is
preserved touched-once per CLAUDE.md hard rule. Same 4-criterion
AND-gate (sharpe ≥ −0.5; max_drawdown ≤ 0.25; total_return ≥
−0.15; total_trades ≥ 5) per PHASE2C_7.1 §4 + canonical config.
Trade-count filter at `>= 20` per PHASE2C_7.1 §5.3 Rule 1
anti-tuning discipline. Success criteria: per-regime pass rates
(primary + audit-only partitions across n≥3 regimes); cross-regime
intersection populations at n≥3; cross-regime carry-forward
asymmetry resolution at larger primary populations per §3 Q-B1
mechanism question scope. Rough duration: ~10-15 sessions total
work-cycle (compute is ~12-20 minutes wall-clock for n≥3 regime
evaluations; the bulk is drafting + adjudication + closeout +
adversarial review).

**5-step deliverable structure.**

PHASE2C_8.1's deliverable sequence follows PHASE2C_7.1's structural
pattern with multi-regime extensions:

1. **Step 1 — Regime-source selection + lineage discriminator
   extension.** Sub-step 1.1: scoping decision for which additional
   historical regimes to evaluate against (regime-source selection
   is itself a scoping sub-cycle within PHASE2C_8.1). Sub-step 1.2:
   schema discriminator extension from `phase2c_7_1` to
   `phase2c_8_1` per §7 carry-forward item 9. Sub-step 1.3:
   producer flag + lineage check extension if any additional regime
   keys require new schema-discriminator handling beyond PHASE2C_7.1's
   `--regime-key` parameterization. Sub-step 1.4: smoke run against
   each additional regime (5-candidate subset analogous to
   PHASE2C_7.1 sub-step 1.4) verifying lineage discipline +
   producer correctness.
2. **Step 2 — Full 198-candidate evaluation across additional
   regimes.** Per-regime evaluation of the full 198-candidate batch
   against each additional historical regime selected in Step 1.
   Per-regime artifact set at
   `data/phase2c_evaluation_gate/<regime_v1>/`. Same single-run
   holdout attestation domain pattern as PHASE2C_7.1's audit_2024_v1.
   Per-regime aggregate pass rates + per-candidate
   `holdout_summary.json` files.
3. **Step 3 — Trade-count filtered secondary pass per regime.**
   Apply the canonical `total_trades >= 20` filter to each
   additional regime's evaluation outputs (parallel structure to
   PHASE2C_7.1's `audit_2024_v1_filtered/`). Per-regime filtered
   artifact set; per-regime filtered aggregate pass rates.
4. **Step 4 — Multi-regime comparison matrix at n≥3.** Extend
   PHASE2C_7.1's 2-regime comparison machinery (which produced
   `comparison_2022_vs_2024_v1/`) to n-regime structure. Comparison
   artifact at
   `data/phase2c_evaluation_gate/comparison_n_regime_v1/` (path TBD
   per PHASE2C_8.1 drafting). Per-candidate diff matrix across n≥3
   regimes; stratified cross-tabs per regime; cross-regime
   intersection populations enumerated; carry-forward chains
   (PHASE2C_6 2022-survivor → PHASE2C_7.1 2024 outcomes →
   PHASE2C_8.1 third-regime outcomes) computed.
5. **Step 5 — Closeout drafting + adversarial review + commit.**
   Closeout document at
   `docs/closeout/PHASE2C_8_1_RESULTS.md` (path TBD per
   PHASE2C_8.1 drafting cycle); follows PHASE2C_7.1's 11-section
   structure adapted for n≥3 evidence base per §6 closing note.
   Adjudication sequence applies §10-codified disciplines: §1
   recompute-before-prose at framing-summary stage; §9 Path-2
   outline-first drafting if headline-bearing section carries
   multi-direction findings (likely); §11 closeout-assembly
   checklist for multi-cycle drafting; §12 mandatory adversarial
   review before merge/tag. Commit + push + tag per PHASE2C_7.1
   pattern.

**Cross-cutting note.** PHASE2C_8.1's spec must include: the
per-regime producer commands (multi-regime orchestration + smoke
verification per regime); the success-criteria verification queries
(analogous to PHASE2C_7.1 closeout §11's reproducibility queries);
the lineage-attestation pattern (single-run holdout domain
extension per regime; existing
[`check_evaluation_semantics_or_raise()`](../../backtest/wf_lineage.py)
guard applies); the closeout document path under `docs/closeout/`;
and the adjudication sequence (which sections drafted first, dual-
AI review pattern, mandatory adversarial review at closeout commit
per METHODOLOGY_NOTES §12). PHASE2C_7.1's arc structure is the
canonical reference for these meta-decisions; PHASE2C_8.1 inherits
+ extends to n≥3 regime evidence base.
