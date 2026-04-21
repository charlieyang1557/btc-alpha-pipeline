# D7 Stage 2d — Scope Lock v2

**Status:** v2 — committable
**Author:** Charlie Yang (with advisor scaffolding)
**Purpose:** Lock the scope, structure, and procedural constraints for D7
Stage 2d before any scope-shaping code is written or any pre-fire
materials are authored. Stage 2d is the D7 critic's production-scale
live fire over the signed-off D6_STAGE2D proposer batch.
**Supersedes:** `D7_STAGE2D_SCOPE_LOCK_v1_DRAFT.md` (not committed; draft
only). See Appendix A for v1 → v2 changelog.
**Based on:**
- `D7_STAGE2C_SCOPE_LOCK_v2.md` (structure template)
- `PHASE2B_D7_STAGE2C_SIGNOFF.md` §9 (carry-forward constraints)
- `PHASE2B_D7_STAGE2A_SIGNOFF.md` (cost / prompt-length warnings)
- `PHASE2B_D6_STAGE2_LESSONS_LEARNED.md` (200-call audit philosophy)
- Stage 2c empirical cost and distribution data
- Read-only batch inspection of
  `raw_payloads/batch_5cf76668-.../stage2d_summary.json` (pre-v2)

---

## 0. Clarification: two distinct "Stage 2d"

For unambiguous reference throughout this document:

- **D6 Stage 2d** = already signed-off 200-attempt Proposer production
  batch `5cf76668-47d1-48d7-bd90-db06d31982ed`. Artifacts are committed
  and frozen. Its `stage2d_summary.json` is a *source-of-truth* for
  this document; it is not itself a D7 Stage 2d artifact.
- **D7 Stage 2d** (this document) = D7b critic's production-scale live
  fire, replaying D7b critique against all D6 Stage 2d source positions.

Henceforth, "Stage 2d" without qualifier means **D7 Stage 2d**.

---

## Lock 1 — Scope, Batch Source, and Source vs Call Counts

### 1.1 Source counts (anchored to D6_STAGE2D batch)

Read-only batch inspection established:

```text
source_record_count       = 200
d7b_call_attempt_count    = 199
skipped_source_invalid_count = 1   (position 116 only)
```

Position 116 has `lifecycle_state != pending_backtest`
(`rejected_complexity` / `invalid_schema`). The current replay
path `agents/critic/replay.py` rejects any target whose lifecycle is
not `pending_backtest`. Therefore position 116 cannot be replayed by
`BatchContext` reconstruction and will not reach D7b.

### 1.2 Fire script constants (hardcoded, not user-configurable)

```text
STAGE2D_SOURCE_N           = 200
STAGE2D_LIVE_D7B_CALL_N    = 199
STAGE2D_SKIPPED_POSITIONS  = [116]
STAGE2D_BATCH_UUID         = "5cf76668-47d1-48d7-bd90-db06d31982ed"
```

Neither `STAGE2D_SOURCE_N` nor `STAGE2D_LIVE_D7B_CALL_N` is
renegotiable once scope lock v2 is signed off.

### 1.3 Execution mode

Replay-only. No live D6 proposer calls. All 199 replayed candidates
are reconstructed from the signed-off D6_STAGE2D batch artifacts via
the same `BatchContext` reconstruction path used in Stage 2b and 2c.

### 1.4 Firing order

Ascending by `position` (1, 2, ..., 200). Within each position, the
batch context is reconstructed using prior history as it was at that
position in the original D6_STAGE2D run.

### 1.5 Position 116 treatment (per Q-B decision)

Position 116 produces a **deterministic skipped source record**, not a
D7b call. Schema for `docs/d7_stage2d/call_116_live_call_record.json`:

```json
{
  "call_index": 116,
  "position": 116,
  "critic_status": "skipped_source_invalid",
  "d7b_call_attempted": false,
  "d7b_error_category": "source_invalid",
  "source_lifecycle_state": "rejected_complexity",
  "source_valid_status": "invalid_schema",
  "actual_cost_usd": 0.0,
  "input_tokens": 0,
  "output_tokens": 0,
  "skip_reason": "source candidate is not pending_backtest and cannot be replayed by BatchContext reconstruction"
}
```

**Taxonomy isolation** (MANDATORY):

- `skipped_source_invalid` is NOT a D7b error.
- `skipped_source_invalid` does NOT count toward rule (a)
  `api_level_consecutive`, rule (b) `error_rate_over_threshold`, or
  rule (c) `content_level_threshold`.
- `skipped_source_invalid` records are NOT part of the error-rate
  numerator or denominator.
- `critic_status_counts` in the aggregate batch record reports
  `ok`, `d7b_error`, and `skipped_source_invalid` as **three
  distinct counters**.

**Double guardrail** (MANDATORY):

- Position 116 is the **only** position permitted to produce
  `critic_status="skipped_source_invalid"`.
- Any other position producing `skipped_source_invalid` triggers a
  hard abort under new rule (g) `unexpected_skipped_source` (see
  Lock 7.7).

### 1.6 Record completeness invariant

After any sign-off-eligible fire (completed or operationally aborted):

- `len(call_*_live_call_record.json files) == 200` (one per source
  position 1..200, including 116)
- `critic_status_counts.ok + critic_status_counts.d7b_error +
  critic_status_counts.skipped_source_invalid == 200`
- `critic_status_counts.skipped_source_invalid == 1` in nominal fire
- `positions covered in call_* records == {1, 2, ..., 200}`
  (set-equal; no gaps, no duplicates)

---

## Lock 2 — Expectations Scope (Hybrid Architecture)

This lock directly addresses the Q1 architectural decision.

**Expectations architecture:** **(d) Hybrid** — structural aggregate
pre-registration + mandatory test-retest grid + deep-dive sampled
candidates.

The Stage 2c-style "per-candidate prose for all candidates" approach is
explicitly **rejected as infeasible** at this scale. The D6 Stage 2
lessons document establishes the precedent: at production scale,
exhaustive per-candidate review is replaced by (a) full aggregate audit
+ (b) structural invariant audit + (c) sampled deep-dive + (d) notebook-
based reconstruction verification.

Stage 2d expectations file must contain:

### 2.1 Full-batch aggregate pre-registration (all 199 D7b calls)
Covers: completion / cost / error-rate / reasoning-length gates;
axis-specific label rubric claims (Lock 6); SVR distribution shape
claims; theme-level sub-claims; factor-family claims including the
RSI-absent vol-regime follow-up.

Position 116 is **excluded** from all aggregate denominators. Every
aggregate claim denominator is `199`, not `200`, unless explicitly
framed as source-level audit.

### 2.2 Mandatory test-retest grid (20 Stage 2c overlap candidates)
Covers: the 5 Stage 2b ∩ Stage 2c ∩ Stage 2d three-run candidates
+ the 15 Stage 2c ∩ Stage 2d two-run candidates. Structured
per-candidate rubric (not fresh prose; Stage 2c prose is the
baseline authority). See Lock 3 for rubric.

### 2.3 Deep-dive sampled candidates (N=20, stratified)
Covers: 20 fresh (i.e., not-yet-Stage-2c-evaluated) candidates selected
via stratified sampling (Lock 4). These receive Stage 2c-style
per-candidate prose.

### 2.4 Remaining candidates: schema-level only
The remaining `199 - 20 - 20 = 159` replay-eligible candidates receive
no per-candidate prose expectations. They are covered only by
aggregate/schema gates (Lock 6). Their individual scores enter
post-fire descriptive tables, not pre-fire narrative claims.

### 2.5 Total prose load budget
~20 deep-dive candidates with fresh prose + lightweight test-retest
rubric block per overlap candidate. Comparable to Stage 2c's total
authoring effort (one conversation), not a multi-week effort.

---

## Lock 3 — Multi-Tier Test-Retest Grid

The Stage 2c `Lock 10a` structure was a 5-candidate test-retest grid
against Stage 2b. Stage 2d upgrades this to a **three-tier grid**. All
three tiers use **Universe A** labels (frozen from Stage 2b/2c
selector decisions) for historical comparability. Universe A / Universe
B distinctions are defined in Lock 6.

### 3.1 Tier 1 — Three-run candidates (5 candidates)
Positions: `{17, 73, 74, 97, 138}`
Runs: Stage 2b → Stage 2c → Stage 2d
Expectations: per-candidate stability claim with **both** Stage 2b and
Stage 2c baselines visible. Drift direction is **bidirectional**
(carry-forward from Stage 2c's falsified downward-drift sub-claim).
Required per-candidate fields: expected SVR region (categorical),
drift tolerance magnitude (numeric), threshold-side preservation
required (boolean).

**pos 138 clarification:** pos 138 was `neutral`-labeled in both
Stage 2b and Stage 2c. It has no directional label-rubric prediction
at Tier 1; its Tier 1 expectation is absolute-SVR-stability only
(Stage 2b 0.15 → Stage 2c 0.30 → Stage 2d ?), not a polarity claim.
The other 4 Tier 1 candidates (17, 73, 74, 97) do carry directional
label-rubric predictions under Universe A.

### 3.2 Tier 2 — Two-run candidates (15 candidates)
Positions: `{22, 27, 32, 62, 72, 77, 83, 102, 107, 112, 117, 143, 147,
152, 162}`
Runs: Stage 2c → Stage 2d
Expectations: per-candidate stability claim with Stage 2c baseline.
Same bidirectional drift rule as Tier 1.

### 3.3 Tier 3 — Fresh-run candidates (~179)
All remaining replay-eligible positions (i.e., positions in 1..200
minus {116} minus Stage 2c 20 positions) that are not selected for
deep-dive. No per-candidate polarity pre-registration. Covered only
by aggregate claims (Lock 6).

### 3.4 Evaluation axes (per Tier 1 / Tier 2 candidate)
For each overlap candidate, sign-off evaluates:
- **Threshold-side preservation**: SVR stays on same side of 0.5 as
  previous run(s)
- **Categorical preservation**: SVR stays in same categorical bucket
  (HIGH / MODERATE-HIGH / MEDIUM / MODERATE-LOW / LOW)
- **Drift magnitude**: absolute numerical delta vs baseline
- **Drift direction**: up / down / stable (NOT predicted; observed)
- **Axis-specific stability**: plausibility, alignment, SVR tracked
  independently

### 3.5 Bidirectional-drift rule (MANDATORY carry-forward)
No Stage 2d pre-registration may claim a directional drift sign
(upward or downward) for any overlap candidate unless directly
supported by:
- Both Stage 2b and Stage 2c baselines showing a consistent
  magnitude-and-direction pattern, AND
- An explicit mechanism-level justification (not "temperature noise
  will drift X").

### 3.6 No Tier 2.5 (per Q-A decision)
The 9 fresh eligible-pool candidates
`{122, 127, 128, 129, 132, 172, 178, 182, 187}` carry Universe A
labels but have no prior D7b score baseline. They are **not** a
separate test-retest tier. They are instead **eligible for deep-dive
sampling** (Lock 4). When included in deep-dive, their Universe A
label is recorded as metadata on the candidate's deep-dive entry,
not as a separate rubric family.

---

## Lock 4 — Deep-Dive Candidate Sampling (N=20, Stratified)

### 4.1 Sampling strata (refined against batch inspection)

Deep-dive candidates must span the following strata. Each stratum
must have at least the minimum count; no stratum may exceed its
maximum. Total across strata = 20.

Feasibility counts from batch inspection:

| Stratum | Intent | Fresh pool | Min | Max |
|---|---|---:|---:|---:|
| RSI-absent `volatility_regime` | Test the Stage 2c C16/C17 low-SVR sub-pattern on fresh candidates | 7 | 3 | 5 |
| RSI-present `volatility_regime` | Control for RSI-absent claim | 29 | 2 | 4 |
| MR high-recurrence / high-overlap | Extend Stage 2c agreement-cluster pattern (broadened from exact-7-factor-only) | broad | 3 | 5 |
| Early-position 1-50 fresh | Early-batch behavior (Stage 2c started at pos 17) | 46 | 2 | 4 |
| Late-position 163-200 fresh | Late-batch behavior under larger prior history | 38 | 2 | 4 |
| Rare-families themes (`momentum`, `volume_divergence`, `calendar_effect`) | Theme coverage beyond MR and vol_regime | ~119 | 2 | 4 |

Fresh RSI-absent vol_regime positions (from inspection):
`{3, 43, 68, 128, 173, 188, 198}` (7 total).

**MR high-recurrence stratum, refined wording:** MR candidates not in
Stage 2c with strong recurrence signal —  including exact 7-factor
repeats where available (pos 197), and high-overlap near-repeats
(`max_overlap_with_priors >= 5`) otherwise. This broadening was
required because the exact 7-factor cluster has only 1 fresh member
(197), insufficient to hit the min-3 minimum.

### 4.2 Exclusion rules
- The 20 Stage 2c candidates are automatically excluded (they are
  already covered by Lock 3 test-retest grid).
- Position 116 is automatically excluded (skipped source).

### 4.3 Prioritization rule for fresh eligible-pool candidates
The 9 fresh eligible-pool candidates
`{122, 127, 128, 129, 132, 172, 178, 182, 187}` are **preferred
within relevant strata** but not mandatorily included. At least
`3 / 9` must appear among the final 20 deep-dive selections (to
avoid fully ignoring their Universe A anchor), but a higher count
is allowed if they naturally fit multiple strata.

### 4.4 D6 anomaly-flag handling
The only D6 anomaly flag in the D6_STAGE2D batch is batch-level
(`rsi_14_dominance` over first 50 valid calls), not candidate-level.

Batch-level anomaly flags may **inform** stratum-selection heuristics
(e.g., the early-position stratum 1-50 overlaps with the
`rsi_14_dominance` flag region), but do not automatically include
any candidate. No candidate is "auto-included" based on batch-level
anomaly flags unless the anomaly names specific candidate positions.

### 4.5 Selection commit anchor
Deep-dive selection is committed as a separate JSON file
`docs/d7_stage2d/deep_dive_candidates.json`. The commit must occur
after `replay_candidates.json` is committed and before
`test_retest_baselines.json` is committed. See Lock 11.4 for full
commit ordering.

### 4.6 Anti-hindsight for deep-dive selection
Selection may use Stage 2b and Stage 2c results to stratify
(because those are signed-off baseline data). Selection may NOT use
any Stage 2d simulation, dry-run evidence, or pilot run evidence.

---

## Lock 5 — Carry-Forward Constraints from Stage 2c (MANDATORY)

From `PHASE2B_D7_STAGE2C_SIGNOFF.md` §9. All six constraints are
binding on Stage 2d scope, expectations, and sign-off.

### 5.1 Top-skew allowed for aggregate distributions
Aggregate pre-registrations MAY NOT assume moderate-centered
distributions. Distribution-shape claims must use quantile-based
boundaries or tail-count claims, not fixed-median-point intervals.
See Lock 6.

### 5.2 No pre-committed directional drift sign
See Lock 3.5. Applies batch-wide, not just to overlap candidates.

### 5.3 RSI-absence in vol_regime candidates is a structured claim
The C16/C17 low-SVR RSI-absent sub-pattern must be tested explicitly
as a falsifiable claim scoped to fresh candidates only, not as a
prose intuition or universal rule. See Lock 6.3.

### 5.4 Operational-identity / grammar / factor-set variants are
distinguished in SVR prose

When deep-dive prose discusses structural novelty, it must distinguish
between:
- factor-set level (which factors are present)
- grammar level (which operators / structural patterns are used)
- operational-identity level (parameter / horizon / regime-gate
  combinations that together form a distinguishable trade profile)

This was the Stage 2c C20 framing that worked; it becomes mandatory.

### 5.5 Selector labels ≠ semantic judgments
Stage 2d may NOT treat D7a selector label and D7b semantic SVR as
interchangeable. Every claim must specify which is being measured.

### 5.6 Explicit falsification accounting
Stage 2d sign-off must separately adjudicate:
- operational pass/fail
- per-claim pre-registered adjudication
- each failing claim explicitly listed without softening

No post-hoc reinterpretation of falsified claims.

---

## Lock 6 — Aggregate Claims Architecture

### 6.1 Label universes (foundational distinction)

Stage 2d operates on two distinct label universes. Each universe is
used for different scientific purposes; they MUST NOT be mixed in
any single denominator.

Both universes are derived by `scripts/derive_d7_stage2d_label_universes.py`
(Lock 11.2) and anchored in the committed artifact
`docs/d7_stage2d/label_universe_analysis.json`:

**Universe A — Stage 2b/2c eligible-pool (size = 29)**
- Definition: candidates eligible under the Stage 2b/2c selector's
  eligibility filters (as implemented in `select_replay_candidate.py`).
- Label counts: `agreement_expected = 11`, `divergence_expected = 3`,
  `neutral = 15`.
- Role: **frozen labels for Tier 1 / Tier 2 test-retest comparability.**
  These labels preserve direct semantic comparability with Stage 2b and
  Stage 2c selector decisions.
- The 9 fresh eligible-pool candidates `{122, 127, 128, 129, 132, 172,
  178, 182, 187}` are the Universe A members not in Stage 2c.

**Universe B — Full replay-eligible pending-backtest (size = 199)**
- Definition: all positions in 1..200 with
  `lifecycle_state == pending_backtest`, i.e., all D7b-replayable
  positions excluding position 116.
- Label counts: `agreement_expected = 66`, `divergence_expected = 5`,
  `neutral = 128`.
- Role: **aggregate axis claims for the full-batch D7b run.**
- WARNING: Universe B labels differ from Stage 2b/2c frozen labels for
  some overlap positions. Positions 17, 73, 74 are
  `divergence_expected` under Universe A but `neutral` under Universe
  B. These label conflicts are documented in
  `label_universe_analysis.json`.

**Mixing rule (MANDATORY):** Stage 2d pre-registration and sign-off
must NEVER place candidates from Universe A and Universe B into a
single denominator. Every aggregate claim denominator must specify
its universe.

### 6.2 Axis-specific label claims (replacing Stage 2c's single X/Y)

Stage 2c's `Lock 6.1` style "`>= X / Y` overall" was falsified in spirit
because 8/8 agreement + 0/3 divergence produced a pass-looking 8/11
while masking complete divergence-axis collapse. Stage 2d replaces
this with three independent axis claims under Universe B:

**6.2.1 Agreement-axis claim (Universe B, denominator = 66)**
At least `TBD-A1` of 66 `agreement_expected` candidates have
`SVR >= 0.5`.

**6.2.2 Divergence-axis stress test (Universe B, denominator = 5)**
The 5 `divergence_expected` candidates are adjudicated **individually
and explicitly** in sign-off. No single threshold is pre-registered
as "pass"; the claim is "expected observation" per Stage 2b/2c
replication pattern. Given Stage 2b+2c combined showed 6/6
divergence-axis contradiction (SVR >= 0.5 despite label),
Stage 2d's default expectation is that `>= TBD-A2` of the 5 Universe
B divergence candidates will have `SVR >= 0.5`.

**6.2.3 Overall directional consistency (SECONDARY operational metric)**
Combined 66 + 5 = 71 directional candidates. `observed_consistent_
with_label` rate reported for operational reference. NOT the
scientific headline. NOT used to offset axis-specific failures.

**TBD-A1 and TBD-A2 resolution:** Advisor drafts numeric values
during expectations authoring once the aggregate claim prose is being
written. Values must be justified against Stage 2b+2c empirical
rates.

### 6.3 SVR distribution-shape claim (Universe B, denominator = 199)

Instead of median-point interval (falsified in Stage 2c), use
quantile-based OR tail-count boundaries. Final numeric form is
**TBD-DIST**, resolved during expectations authoring after pilot
inspection of Stage 2c distribution shape and expected Universe B
mixing effects.

Candidate forms (advisor to propose one during expectations
authoring):
- Q1 / Q3 SVR interval pre-registration
- Tail count pre-registration (e.g., `# SVR >= 0.8` in range,
  `# SVR < 0.3` in range)
- Or a combination

TBD-DIST may not be left unresolved at expectations commit. Whatever
form is chosen must be falsifiable.

### 6.4 RSI-absent vol_regime structured claim (Universe B, fresh-only)

**Scope narrowing (per Q-B/F revision):** The claim is restricted to
**fresh** RSI-absent vol_regime candidates. The 7 fresh candidates
are `{3, 43, 68, 128, 173, 188, 198}` (from batch inspection).

**Claim:** Among the 7 fresh RSI-absent vol_regime candidates, at
least `2` are predicted to have `SVR < 0.5`.

**Rationale:** Stage 2c data showed RSI-absent vol_regime is NOT a
universal LOW-SVR cohort (pos 73 is RSI-absent vol_regime and scored
0.95 in both Stage 2b and Stage 2c). The pattern is narrower: late
vol/volume/SMA triplets without RSI. A narrow `2/7` claim is
consistent with Stage 2c's 2/2 observed (pos 138 at 0.30, pos 143 at
0.15) without over-generalizing to a stratum-wide rule.

The 20 Stage 2c candidates ARE NOT part of this claim's denominator
(pos 73 and pos 138 excluded; frozen test-retest candidates only
enter Lock 3).

### 6.5 Theme-stratified sub-claims
Theme-level SVR distribution claims allowed (e.g., "MR theme under
Universe B median SVR in [X, Y]"). Each sub-claim must be
independently falsifiable. Must not aggregate opposite-polarity
themes.

### 6.6 Plausibility / alignment distribution claims
Not required to pre-register (Stage 2c data shows these are noisier
than SVR). Can be listed as post-fire observation axes without
pre-commitment.

---

## Lock 7 — Abort Rules (Inherited from Stage 2c with Additions)

### 7.1 Rule (a) — `api_level_consecutive`
Abort if 2 consecutive `api_level` D7b errors.
**Inherited unchanged.**

### 7.2 Rule (b) — `error_rate_over_threshold`
Abort if `d7b_error` rate `> 40%` at `K >= 3` completed D7b calls.
Denominator is completed D7b calls only (excludes
`skipped_source_invalid`). **Inherited unchanged** (ratio; scales
naturally).

### 7.3 Rule (c) — `content_level_threshold`
Abort if absolute count of `content_level` errors `>= 4`.
**Inherited unchanged** from Stage 2c launch prompt v2 Amendment 7.
Rationale for not scaling to N=200: content-level errors indicate
prompt/parser issues, which should abort fast regardless of N.

### 7.4 Rule (d) — per-call cost ceiling
Abort if single-call actual cost `> $0.08`.
Stage 2c observed max per-call cost `$0.019452` at pos 162.
Stage 2a warned pos 200 may have ~9000 input tokens → up to
~$0.03/call. `$0.08` gives ~4× margin.

### 7.5 Rule (e) — total cost cap
Abort if cumulative cost `> $8.00`.
Projected Stage 2d cost: $3.60-$4.40 expected, $5.00-$6.00 worst-
case full-prompt. `$8.00` leaves prompt-inflation margin.

### 7.6 Rule (f) — reasoning-length (DEFERRED)
Per Q-decision TBD-J: **Deferred. Not added as hard abort in v2.**
Reasoning length remains a soft warning in per-call records and a
sign-off observation axis. Min-length soft threshold 100 chars
preserved from Stage 2c.

### 7.7 Rule (g) — `unexpected_skipped_source` (NEW for Stage 2d)

**Trigger:** A position OTHER than 116 produces
`critic_status="skipped_source_invalid"`.

**Rationale:** The Q-B guardrail locks pos 116 as the single expected
source-invalid position. Any other position producing this status
indicates (a) D6_STAGE2D batch state changed since inspection, (b)
replay-path code changed, or (c) lifecycle-state corruption. All
three scenarios require immediate halt and investigation before
continuing.

**Behavior:** Fire script aborts immediately with
`abort_reason="unexpected_skipped_source"` and logs the triggering
position. No retry. Post-abort investigation required before any
re-fire.

### 7.8 `skipped_source_invalid` taxonomy isolation (MANDATORY)
Per Lock 1.5, `skipped_source_invalid` records:
- Do NOT count toward rule (a) consecutive-api threshold
- Do NOT contribute to rule (b) error rate numerator or denominator
- Do NOT count toward rule (c) content-level threshold
- DO trigger rule (g) if produced at any position other than 116

---

## Lock 8 — Narrow-Claim Discipline (Inherited from Stage 2c)

Carry-forward from Stage 2c `Lock 8`. Unchanged in Stage 2d.

- No sub-group hypothesis pre-commitment (prior_occ monotonicity,
  theme-family trends, etc.) unless directly tested as a
  structured aggregate claim in Lock 6.
- Deep-dive per-candidate prose stays at candidate-level judgment;
  cross-candidate comparisons are either not present or explicitly
  framed as post-fire observations, never pre-fire predictions.
- Narrow-claim protection sentence mandatory in deep-dive
  Reconciliation paragraphs.
- The RSI-absent vol_regime claim in Lock 6.4 is the single
  aggregate sub-group claim pre-committed; no other sub-group
  claims may be added without new scope lock revision.

---

## Lock 9 — Cost Envelope

### 9.1 Empirical basis
Stage 2c measured:
- 20 calls, total `$0.315765`, avg `$0.0158/call`
- Late position (162): `$0.019452`
- Input tokens: avg `3569`, late position `~4600`

Stage 2a warned:
- Pos 200 prompt linear-extrapolates to ~9000 input tokens
- Input:output cost ratio ~7:1

### 9.2 Stage 2d projection
- Expected average cost: `$0.018-$0.022/call` (99 calls average)
- Expected total cost: `$3.60-$4.40`
- Worst-case full-prompt inflation: `$5.00-$6.00`
- Per-call ceiling under rule (d): `$0.08`
- Total ceiling under rule (e): `$8.00`

### 9.3 Prompt compression (per Q-decision TBD-K)
**Deferred. Stage 2d fires with full prompts.**
Rationale: Stage 2c's sub-linear empirical growth suggests full
prompts are tractable; adding compression would introduce a new
uncontrolled variable right before the final D7 production fire.
Cost envelope absorbs the worst-case full-prompt scenario.

### 9.4 Budget impact
- Remaining Phase 2B budget at Stage 2d start: ~$27 (of $30 cap)
- Stage 2d expected: $4 (~15% of remaining)
- Stage 2d hard cap: $8 (~30% of remaining)
- Post-Stage 2d remaining budget: ~$19-$23 for D8 and beyond

**Verdict: Stage 2d is comfortably within Phase 2B budget.**

---

## Lock 10 — Fire Script Architecture

### 10.1 New fire script mandatory
Stage 2c explicitly documents that its fire script is not
parameterized and not to be extended. Stage 2d requires a **new,
parallel, script:** `scripts/run_d7_stage2d_batch.py`.

### 10.2 Architectural parallels to `run_d7_stage2c_batch.py`
- `STAGE2D_SOURCE_N = 200` and `STAGE2D_LIVE_D7B_CALL_N = 199`
  hardcoded
- `STAGE2D_BATCH_UUID` hardcoded
- `STAGE2D_SKIPPED_POSITIONS = [116]` hardcoded
- Stub mode (`--stub`) and live mode (`--confirm-live`)
- Abort rule taxonomy per Lock 7 including new rule (g)
- Same per-call forensic record format plus skipped-source schema
  (Lock 1.5)
- Same aggregate batch record format with Stage 2d-specific fields
- Same pre-fire integrity gates
- Same stub/live write isolation

### 10.2a Three-JSON selection architecture (per Q-C decision)
Stage 2d uses **three distinct JSON anchor files**, all committed
before expectations, with distinct roles:

1. **`docs/d7_stage2d/replay_candidates.json`** — consumed by the fire
   script. Contains all 199 replay-eligible candidates from
   D6_STAGE2D batch in firing-order position ascending, plus position
   116 flagged `is_skipped_source=true`. This is the full source-
   position list (200 entries, 199 replayable).

2. **`docs/d7_stage2d/deep_dive_candidates.json`** — consumed by the
   expectations file and self-check script. Contains exactly 20
   stratified deep-dive candidates (Lock 4). **Fire script ignores
   this file.**

3. **`docs/d7_stage2d/test_retest_baselines.json`** — consumed by the
   expectations file and self-check script. Contains Stage 2b and/or
   Stage 2c SVR / plausibility / alignment scores, indexed by
   position, for all 20 overlap candidates. **Fire script ignores
   this file.**

### 10.2b Fourth pre-fire artifact (derivation source-of-truth)
**`docs/d7_stage2d/label_universe_analysis.json`** — consumed by the
scope lock (this document), the expectations file, and the self-
check script. Generated deterministically by
`scripts/derive_d7_stage2d_label_universes.py`. Contains Universe A
and Universe B definitions, counts, members, and Stage 2c label
conflicts. **Fire script ignores this file.**

### 10.3 Stage 2d-specific additions to the fire script
- Deep-dive candidate list input (read-only; not used in firing-
  order decisions)
- Multi-tier test-retest baseline file (read-only; not used in
  firing-order decisions)
- Stratum metadata in aggregate record (for post-fire theme-level
  stats)
- Expected cost tracking with projected-vs-actual per-50-calls
  checkpoint (mid-batch cost sanity; logs but does not abort)
- Position 116 deterministic skip handling (Lock 1.5)
- Aggregate record must report three `critic_status_counts`: `ok`,
  `d7b_error`, `skipped_source_invalid`

### 10.4 Anti-drift contract
The fire script and the D7b prompt template must be **frozen at fire
time**. Prompt template changes require a new scope lock revision
(v3) and a new expectations commit.

### 10.5 Stage 2c artifact preservation
Before Stage 2d fires, all Stage 2c raw payloads for the 20 overlap
positions must be archived under a new subdirectory:
`raw_payloads/batch_5cf76668-.../critic/stage2c_archive/`
mirroring the `stage2a_archive/` and `stage2b_archive/` convention.

---

## Lock 11 — Expectations File Structure and Commit Ordering

### 11.1 Required sections (enforced by self-check)
- `## Anti-Hindsight Anchor`
- `## Label Universes` (new; references `label_universe_analysis.json`)
- `## Aggregate Expectations Across All 199 D7b Calls`
- `## Axis-Specific Label Claims` (new; addresses Lock 6.2)
- `## SVR Distribution-Shape Claim` (new; addresses Lock 6.3)
- `## RSI-Absent Vol_Regime Structured Claim` (new; addresses Lock 6.4)
- `## Multi-Tier Test-Retest Grid`
  - subsection `### Tier 1 (Stage 2b ∩ 2c ∩ 2d)` — 5 candidates
  - subsection `### Tier 2 (Stage 2c ∩ 2d)` — 15 candidates
- `## Deep-Dive Candidate Expectations` — 20 candidates with prose
- `## Remaining Candidates (Schema-Level Only)` — brief note only
- `## Position 116 Treatment` — brief reference to Lock 1.5

### 11.1.a Authoring convention notes (amended 2026-04-19 post-E4 seal)

The following deviations from §11.1 canonical headers were adopted
during E2-E4 authoring and are preserved as sealed content:

- Prefixes `§6.1`, `§6.2`, `§6.3`, `§6.4`, `§6.5`, `§6.6`, `§E3`,
  `§E4`, `§E5` may precede the canonical header text for visual
  organization and cross-reference within the expectations file.
  Gate 2 (self-check required-headers match) permits optional prefix
  matching the pattern `§\d+\.\d+\s*—\s*` or `§E\d+\s*—\s*`.

- Additional sections beyond the Lock 11.1 canonical list:
  - `## §6.5 — Theme-Stratified Sub-Claims` — records the Lock 6.5
    decline-to-pre-register decision; no numerical commitment.
  - `## §6.6 — Plausibility / Alignment Observation Axes` —
    observation-axis specification used by sign-off notebook for
    post-fire descriptive read-outs; not pre-registered gates.

- Additional header `## Frozen Pre-Registration Anchors` was adopted
  at E2 authoring as the expectations-file prefix equivalent to
  Lock 11.1 `## Anti-Hindsight Anchor`. Gate 2 accepts either literal.

Amendment audit trail: Lock 11.1 compliance gap surfaced at E5 gather
time (2026-04-19) via self_check.py Gate 2 design. Charlie ruled
Option C (amend scope lock to match DRAFT rather than amend DRAFT to
match scope lock) preserving sealed §E2/§E3/§E4 content. Both
advisors ratified.

### 11.2 Derivation script (per Q-C decision)
`scripts/derive_d7_stage2d_label_universes.py` is a new, read-only,
deterministic script. Inputs: signed-off D6_STAGE2D batch artifacts.
Outputs: `docs/d7_stage2d/label_universe_analysis.json`.

Schema of `label_universe_analysis.json`:
```text
source_batch_uuid
derivation_script_commit
derivation_timestamp_utc
source_n = 200
replay_eligible_n = 199
non_call_positions = [116]
universe_a:
  definition
  size = 29
  counts: { agreement_expected, divergence_expected, neutral }
  candidate_positions
universe_b:
  definition
  size = 199
  counts: { agreement_expected, divergence_expected, neutral }
  candidate_positions
stage2c_overlap_label_comparison:
  [
    { position, stage2c_frozen_label, universe_b_label, conflict_bool }
    ...
  ]
fresh_eligible_pool_positions = [122, 127, 128, 129, 132, 172, 178, 182, 187]
```

The script must NOT mutate any source batch artifact. It must be
idempotent: given the same source batch, it must produce a
byte-identical output file.

### 11.3 Per-candidate prose format (deep-dive only)
Stage 2c-style structure:
- Structural assessment
- Plausibility expectation (categorical)
- Alignment expectation (categorical)
- SVR expectation (categorical)
- Reconciliation expectation (narrow-claim protection)
- One-sentence core judgment
- **New metadata field:** Universe A label if the candidate is in the
  9 fresh eligible-pool set (per Lock 3.6)

### 11.4 Per-candidate rubric format (test-retest, Tier 1 / Tier 2)
Compact, structured fields (not prose):
- Position, Universe A label, Stage 2b SVR (if applicable), Stage 2c
  SVR
- Stage 2d expected SVR region (categorical)
- Threshold-side preservation required: Y/N
- Drift magnitude tolerance (numeric)
- Notes: any Tier-specific considerations

### 11.5 Commit workflow (MANDATORY ORDERING)

```text
label_universe_analysis.json commit
  <= replay_candidates.json commit
  <= deep_dive_candidates.json commit
  <= test_retest_baselines.json commit
  < scope_lock_v2.md commit (THIS DOCUMENT)
  < expectations.md commit
  < live fire start
```

Requirements:
- All four pre-fire artifact commits precede the scope lock v2
  commit.
- Scope lock v2 precedes expectations commit.
- Expectations commit precedes live fire start.
- No `git commit --amend` after any commit in this ordering.
- Self-check script must pass before expectations commit.

---

## Lock 12 — Self-Check Script

A Stage 2d-specific `stage2d_self_check.py` must pass before the
expectations commit. Gates:

1. Expectations file exists and is valid UTF-8
2. All required section headers present (Lock 11.1)
3. `label_universe_analysis.json` exists and is referenced by
   expectations; SHA256 recorded
4. `replay_candidates.json` has 200 entries, 199 replay-eligible,
   one with `is_skipped_source=true` at position 116
5. `deep_dive_candidates.json` has exactly 20 entries, all
   positions are replay-eligible (not 116), none overlap with
   Stage 2c 20 positions
6. `test_retest_baselines.json` has exactly 20 entries covering
   Stage 2c 20 positions with baseline scores populated
7. Tier 1 grid has exactly 5 candidates with matching position set
   `{17, 73, 74, 97, 138}`
8. Tier 2 grid has exactly 15 candidates with matching position set
9. Deep-dive section has exactly 20 candidates, all 20 positions
   present in `deep_dive_candidates.json`
10. At least 3 of 9 fresh eligible-pool positions appear in
    deep-dive 20 (per Lock 4.3)
11. Axis-specific claim has TBD-A1, TBD-A2 resolved to numeric values
12. SVR distribution claim has TBD-DIST resolved to numeric form
13. RSI-absent vol_regime claim references fresh 7-candidate set and
    has numeric threshold (locked at `2`)
14. No sub-group hypothesis language in deep-dive prose (inherit
    Stage 2c detector, with exception for Lock 6.4)
15. Threshold expressions not broken across lines
16. Position 116 treatment section present; references
    `call_116_live_call_record.json` schema
17. Universe A / Universe B references in expectations cite
    `label_universe_analysis.json`; no hardcoded count drift

---

## Lock 13 — Sign-Off Gate Family Structure

Stage 2d sign-off document must adjudicate:

### 13.1 Operational gates (mirror Stage 2c Part 1)
- Pre-fire integrity
- Fire execution
- Artifact completeness including 200-record invariant (Lock 1.6)
- Cost envelope
- Position 116 skip record presence and schema compliance
- Zero unexpected `skipped_source_invalid` records (rule (g) check)

### 13.2 Scientific gates (axis-separated per Lock 6)
- Universe B agreement-axis pass count / threshold
- Universe B divergence-axis individual adjudication (5 candidates)
- Universe B overall directional consistency (SECONDARY)
- SVR distribution-shape claim
- RSI-absent vol_regime fresh-7 structured claim
- Theme-stratified sub-claims
- Multi-tier test-retest adjudication (Tier 1 + Tier 2)
  - Threshold-side preservation
  - Categorical preservation
  - Drift magnitude
  - Drift direction (observed, not predicted)
- Deep-dive candidate accuracy (exact category, threshold-side)

### 13.3 Falsification enumeration
Explicit list of every falsified claim. No post-hoc interpretation.

### 13.4 Stage 2d → D8 handoff
Carry-forward constraints crystallized. Phase 2B D7 track closed.

---

## Summary of Locked Decisions

| ID | Topic | Locked decision |
|---|---|---|
| Q-A | Fresh eligible-pool treatment | (a) included in deep-dive selection pool; no Tier 2.5; Universe A label as metadata; min 3/9 must appear among deep-dive 20 |
| Q-B | Position 116 non-call handling | (b) `call_116_live_call_record.json` with `critic_status="skipped_source_invalid"`, full schema per Lock 1.5; double guardrail via rule (g) |
| Q-C | Label universe derivation | (a) new `scripts/derive_d7_stage2d_label_universes.py`; committed `label_universe_analysis.json`; no hardcoded counts; no overloading of `select_replay_candidate.py` |
| TBD-G | Content-level abort threshold | `4` (unchanged) |
| TBD-H | Per-call cost ceiling | `$0.08` |
| TBD-I | Total cost cap | `$8.00` |
| TBD-J | Reasoning-length hard abort | Deferred; soft warning only |
| TBD-K | Prompt compression | Deferred; fire with full prompts |

## Open TBD Items (resolved during expectations authoring)

| ID | Topic | Resolution trigger |
|---|---|---|
| TBD-A1 | Agreement-axis pass threshold (Universe B, denom 66) | Advisor drafts during expectations authoring; justified against Stage 2b+2c empirical rates |
| TBD-A2 | Divergence-axis expected-replication count (Universe B, denom 5) | Same as TBD-A1; Stage 2b+2c showed 6/6 contradiction, default expectation ≥ 3/5 |
| TBD-DIST | SVR distribution-shape claim form | Advisor drafts during expectations authoring; must be quantile or tail-count, not median-point |

These three items must be resolved before the expectations commit and
must appear as numeric values (not "TBD") in the committed expectations
file. Self-check gates 11 and 12 enforce this.

---

## Not in Stage 2d Scope (explicitly out-of-scope)

- Refactoring Stage 2b or Stage 2c fire scripts for shared helpers.
  Stage 2c sign-off locked the duplication; Stage 2d maintains it.
- Prompt template redesign. Any prompt change invalidates test-retest
  comparability with Stage 2b and 2c.
- D7a formula or flag changes. D7a is frozen since Stage 1.
- D8 policy design or integration. Stage 2d is D7's final fire; D8 is
  a separate deliverable.
- Backtest evaluation on any D7b-approved candidate. Stage 2d records
  critic judgment; it does not trigger downstream evaluation.
- Cross-batch comparison (other proposer batches). Stage 2d is locked
  to batch `5cf76668-...`.
- Addressing the 5 prompt-compression strategies listed in Stage 2a
  sign-off. Deferred per TBD-K.
- Resolving the Stage 2c "divergence axis 0/3" question. Stage 2d
  provides more divergence-axis data points (3 Tier 1 + additional
  Universe B divergence candidates beyond Stage 2b/2c overlap) but
  does not commit to resolving the interpretation question.

---

## Approval Checklist (Charlie's final review before commit)

Before this v2 is committed as `docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md`,
verify:

- [ ] All 3 blocking refinements from v1 review are incorporated
- [ ] Q-A, Q-B, Q-C decisions locked and correctly applied
- [ ] 6 carry-forward constraints from Stage 2c §9 present (Lock 5)
- [ ] Axis-specific claims replace Stage 2c-style overall X/Y (Lock 6.2)
- [ ] Label universe distinction foundational (Lock 6.1)
- [ ] RSI-absent vol_regime claim narrowed to fresh-7 set with `2/7`
      threshold (Lock 6.4)
- [ ] MR stratum broadened; rare-families stratum defined (Lock 4.1)
- [ ] Position 116 skipped-source schema and rule (g) specified
      (Lock 1.5, Lock 7.7)
- [ ] Three-JSON + one-derivation-artifact architecture (Lock 10.2a,
      10.2b)
- [ ] Commit ordering for 5 pre-fire artifacts + expectations +
      fire start (Lock 11.5)
- [ ] 17-gate self-check coverage (Lock 12)
- [ ] Open TBD items A1, A2, DIST explicitly deferred to expectations
      authoring (Summary table)

---

## Appendix A. v1 → v2 Changelog

v1 was an advisor draft, not committed. v2 is the committable version.
Substantive changes from v1:

**Blocking refinement 1 — N=200 source vs 199 D7b calls**
- v1: "200 D7b calls"
- v2: `STAGE2D_SOURCE_N=200`, `STAGE2D_LIVE_D7B_CALL_N=199`,
  `STAGE2D_SKIPPED_POSITIONS=[116]`
- Added: Position 116 skipped-source schema (Lock 1.5)
- Added: Rule (g) `unexpected_skipped_source` (Lock 7.7)
- Added: 200-record completeness invariant (Lock 1.6)

**Blocking refinement 2 — Label universes**
- v1: single "label distribution" TBD-A
- v2: Lock 6.1 foundational distinction between Universe A (eligible-
  pool, 29 candidates) and Universe B (full replay-eligible, 199
  candidates); no mixing permitted
- Added: `label_universe_analysis.json` as fourth pre-fire artifact
- Added: `derive_d7_stage2d_label_universes.py` as derivation source-
  of-truth

**Blocking refinement 3 — Axis-specific claims**
- v1: "overall directional consistency `>= X / Y`"
- v2: Lock 6.2 three independent axis claims: agreement (denom 66),
  divergence (denom 5, individual adjudication), overall (secondary
  operational metric only)
- Rationale: Stage 2c 8/11 was a pass-looking mask over complete
  divergence-axis collapse; Stage 2d must expose this separately

**Stratum refinement**
- v1: "MR exact 7-factor cluster members not in Stage 2c" (infeasible;
  fresh pool = 1)
- v2: "MR high-recurrence / high-overlap candidates not in Stage 2c,
  including exact repeats and `max_overlap >= 5` near-repeats"
  (Lock 4.1)
- v1: "rare or anomalous factor families" (underspecified)
- v2: "rare-families themes (`momentum`, `volume_divergence`,
  `calendar_effect`)" (Lock 4.1)
- v1: "D6 anomaly-flagged candidates automatically included"
- v2: batch-level anomaly `rsi_14_dominance` informs strata but does
  not auto-include (Lock 4.4); no candidate-level anomaly flags exist

**Q-A decision applied (fresh eligible-pool)**
- Added: Lock 3.6 (no Tier 2.5)
- Added: Lock 4.3 (prioritization rule, min 3/9)

**Q-B decision applied (pos 116)**
- Full schema in Lock 1.5
- Taxonomy isolation in Lock 7.8
- Rule (g) in Lock 7.7

**Q-C decision applied (derivation script)**
- Added: Lock 11.2 script spec
- Added: Lock 10.2b as fourth artifact
- Updated: Lock 11.5 commit ordering includes
  `label_universe_analysis.json` first

**RSI-absent vol_regime claim**
- v1: Option B moderate "Q3 < 0.6"
- v2: fresh-7 narrow claim "at least 2/7 have SVR < 0.5" (Lock 6.4)
- Rationale: pos 73 (RSI-absent vol_regime, SVR 0.95) disqualifies
  Q3 < 0.6 as a universal claim

**TBD table**
- TBD-A → upgraded to A1 (agreement) and A2 (divergence), deferred
  to expectations authoring
- New: TBD-DIST for SVR distribution-shape claim form
- TBD-B/C/D/E (v1 numeric quantile intervals): absorbed into TBD-DIST;
  resolved during expectations authoring
- TBD-F (RSI-absent vol_regime): locked to `2/7` fresh-cohort claim
- Picks G/H/I/J/K locked per Charlie's inline responses

**Self-check script**
- v1: 10 gates
- v2: 17 gates, including position 116 schema gate, Universe
  reference gate, fresh-eligible-pool min-3 gate, three TBD
  resolution gates

---

**End of Scope Lock v2.**

**Committable at:** `docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md`

Upon commit, this document becomes the authoritative contract for
Stage 2d scope. All subsequent Stage 2d work (label derivation
script, replay_candidates.json authoring, deep_dive_candidates.json
authoring, test_retest_baselines.json authoring, expectations
authoring, fire script implementation, self-check script
implementation, and sign-off) must conform to this lock.
