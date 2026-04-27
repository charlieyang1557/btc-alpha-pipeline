# D7 Stage 2c — Pre-Fire Expectations

**Anchor commit for selection:** `b71ffd1` (docs/d7_stage2c/replay_candidates.json)
**Author:** Charlie Yang
**Purpose:** Pre-register per-candidate and aggregate-level predictions for
the 20-call Stage 2c live-fire probe, so that post-fire adjudication is
mechanical (measured against these predictions), not post-hoc storytelling.
This file MUST be committed before fire (HG3/HG5 enforced by fire script).

## Anti-Hindsight Anchor

The core claim under test in Stage 2c is the Stage 2b N=5 finding
(structural_variant_risk polarity tracks the pre-registered agreement /
divergence label). Stage 2c replicates this at N=20 with a distinct
9-candidate neutral group. Neutral candidates do not carry a per-candidate
polarity prediction; the neutral group carries an **aggregate-level**
prediction only (see below).

Pre-fire commitments locked at this document's git commit timestamp:

- Labels, themes, positions, and firing order are exactly those in
  `replay_candidates.json` at commit `b71ffd1`. They are not renegotiable.
- For every `divergence_expected` candidate (positions 17, 73, 74), D7b's
  `structural_variant_risk` is predicted to fall **below 0.5** (low risk,
  structurally distinct variant).
- For every `agreement_expected` candidate (positions 27, 97, 102, 107,
  112, 147, 152, 162), D7b's `structural_variant_risk` is predicted to
  fall **at or above 0.5** (high risk, shallow variant of priors).
- Neutral candidates (positions 22, 32, 62, 72, 77, 83, 117, 138, 143)
  do not carry per-candidate polarity predictions. Their aggregate-level
  prediction is in the section below.

Despite the Stage 2b contradiction on the three overlap divergence cases
(positions 17, 73, 74), I am preserving the selector-based
pre-registration for Stage 2c. The purpose is to test whether the Stage 2b
contradiction replicates or was partly temperature-1.0 / single-run
variance. If these three candidates again receive high SVR in Stage 2c,
that is evidence against the selector-label prediction, not a reason to
reinterpret the labels after the fact.

## Aggregate Expectations Across All 20 Calls

Expected observation pattern across all 20 calls under nominal conditions
(no API outage, no budget cap breach):

- `completed_call_count == 20`
- `sequence_aborted == false`
- `total_actual_cost_usd < $0.50` (rule (e) cap)
- Every per-call `actual_cost_usd <= $0.05` (rule (d) ceiling)
- `d7b_error` rate across the 20 calls is expected to be at most 10%
  (0-2 errors); higher rates trigger the rule (b) / (c) abort taxonomy.
- Reasoning length in each completed call is expected to be > 100
  characters; shorter reasoning is a soft quality-signal flag for
  sign-off review but does not abort fire.
- 11 of the 20 candidates carry directional polarity predictions (8
  agreement, 3 divergence). Overall consistency rate
  `observed_consistent_with_label == true` is expected to be ≥ 7 / 11
  (Stage 2b's N=5 had 4/4 directional hits; we loosen to 7/11 here to
  accommodate the wider N and the known Sonnet-4.6 variance observed
  in Stage 2b raw payloads).

## Aggregate Prediction for Neutral Group

Stage 2c includes nine `neutral`-labeled candidates (positions 22, 32, 62,
72, 77, 83, 117, 138, 143). Per scope lock §Lock 8, these candidates do
not carry per-candidate polarity predictions; the replication mechanism
for the neutral group is an **aggregate-level** pre-registered claim.

**Pre-fire claim (falsifiable):** Across the 9 neutral candidates, the
empirical `structural_variant_risk` distribution is predicted to have a
moderate-to-high center rather than collapsing toward either extreme. The
median `structural_variant_risk` is predicted to fall inside the interval
`[0.45, 0.70]`. At least 1 of the 9 scores is predicted to fall below
0.5, and at least 4 of the 9 scores are predicted to fall at or above
0.5. If the observed neutral-group median falls outside `[0.45, 0.70]`,
or if no scores fall below 0.5, or if fewer than 4 scores fall at or above
0.5, the pre-registered aggregate claim is considered **falsified**.

This aggregate prediction reflects the full set of per-candidate informal
neutral leans completed before fire: most neutral candidates lean
moderate-to-high, but at least one below-threshold case is still expected.
The goal is to preserve a falsifiable distribution-shape claim without
imposing a stronger bimodal or monotonic subgroup hypothesis than the
candidate-level judgments support.

## Per-Candidate Expectations

### Candidate 1 — Position 17, mean_reversion, divergence_expected
Pre-registered label: `divergence_expected`. This is a Stage 2b overlap
candidate (Stage 2b observed: plaus=0.75, align=0.85, svr=0.85).

**My prediction**: The factor set (BB + RSI + zscore + SMA + vol + return)
is a textbook mean-reversion prototype with no genuine novelty — the
strategy is clean low-buy/high-sell logic betting on exogenous-shock
reversion. I expect `semantic_plausibility` HIGH (~0.75-0.85, story is
internally coherent: filter for active market, detect clear deviation,
exit on normalization); `semantic_theme_alignment` HIGH (~0.80-0.90, the
strategy is explicitly doing "deviation → reversion"); and
`structural_variant_risk` HIGH (~0.75-0.90, consistent with Stage 2b's
0.85 observation — this is primarily a **test-retest replication** of
Stage 2b's finding that D7a's mechanical `divergence_expected` label and
Sonnet's semantic SVR judgment do not align for textbook mean-reversion
prototypes).

**Expected replication outcome (test-retest)**: SVR remains HIGH (>0.7),
replicating Stage 2b. Divergence-label mechanical claim stays contradicted
by D7b semantic claim.

**Alternative outcomes and interpretations**: (a) SVR drifts to medium
(0.4-0.7) → Sonnet temp=1.0 judgment noise is larger than Stage 2b
suggested; Lock 10a test-retest stability concern; (b) SVR collapses
(< 0.4) → Stage 2b finding was position-specific artifact, not stable;
replication fails. Predicted outcome is (a is possible but less likely,
b is unlikely).

**One-sentence core judgment**: Coherent textbook mean-reversion
prototype; predicted to replicate Stage 2b's HIGH SVR, reaffirming D7a/D7b
axis orthogonality.

**Caveat for sign-off reading**: the strategy does not discriminate
between endogenous noise and event-driven shocks; Sonnet may cite this
as a minor plausibility weakness. A 1-week max hold may be insufficient
for event-driven moves. Does not change prediction direction.

### Candidate 2 — Position 22, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.
Contributes to neutral-group aggregate prediction.

**Structural assessment**: Position 22 is a **short-horizon parameter
variant of position 17** — same factor family (BB + RSI + zscore + SMA +
vol + return), same entry skeleton (oversold + vol filter), same exit
Path A (statistical reversion), differing only in time horizon
(`return_1h` vs `return_24h`), max hold (72h vs 168h), and vol threshold
(0.025 vs 0.015). The mechanical label is `neutral` (max_overlap=6
disqualifies divergence; no exact prior disqualifies agreement), but
structurally this is "pos 17's short-horizon twin."

**Plausibility expectation**: HIGH (story is internally coherent: active
market + oversold detection + reversion expectation). One weakness: the
aggressive exit (`return_1h > 0.02` + 72h max hold) may cause premature
forced exits on trades that haven't yet reverted. Sonnet may cite this
as a minor plausibility concern but not severely.

**Alignment expectation**: HIGH (the story remains "deviation → reversion
in an active market," which is core mean-reversion).

**SVR intuition (informal, for neutral-group aggregate context)**: I
expect Sonnet to read this as a recycled skeleton with parameter swap,
not a genuinely new construction. If forced to guess, I lean HIGH SVR
(aligned with pos 17's 0.85 baseline).

**One-sentence core judgment**: Same mean-reversion skeleton as pos 17,
parameter swap not structural novelty — still textbook oversold bounce.

### Candidate 3 — Position 27, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.

**My prediction**: `semantic_plausibility` HIGH (the oversold
mean-reversion story is coherent); `semantic_theme_alignment` HIGH (same
deviation-then-reversion narrative); `structural_variant_risk`
MODERATE-HIGH. This is not a near-duplicate of pos 17: the factor set is
identical, and the broad BB + zscore + RSI + reversion-exit spine is the
same, but the volatility-regime gate changes materially from high-vol
entry in pos 17 to low-vol / compression entry here
(`realized_vol_24h < 0.03`). That is a real market-regime assumption
change, not a cosmetic operator tweak.

**Reconciliation expectation**: SVR >= 0.5 satisfies the
`agreement_expected` rubric; label direction confirmed. The scientific
claim is weaker than a narrow near-duplicate control: I expect elevated
SVR because of the identical factor set and shared mean-reversion
skeleton, but with real regime-drift risk because the volatility gate
changes the market state being selected.

**Cross-candidate implication**: pos 17 (divergence_expected, predicted
HIGH SVR) and pos 27 (agreement_expected, predicted MODERATE-HIGH SVR)
are still predicted to land on the high side of the threshold despite
opposite mechanical labels. The revised claim is not "near-identical
input, near-identical output"; it is that a high-overlap agreement
candidate with a materially different regime gate should still preserve
enough semantic overlap to satisfy the agreement rubric.

**One-sentence core judgment**: Exact repeat of pos 17's factor set, but
not exact repeat of market-regime logic; predicted
MODERATE-HIGH SVR as a high-overlap agreement candidate with
regime-gate divergence.

### Candidate 4 — Position 32, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.

**Structural assessment**: Position 32 is a **structural variant of pos
17's mean-reversion skeleton**, with two meaningful differences: (1)
entry uses `close crosses_below bb_upper_24_2` instead of static
`close < bb_upper_24_2`, introducing a dynamic trigger rather than a
state filter; (2) drops `realized_vol_24h`, removing the "active market"
regime filter. It also adds a drawdown-style entry gate
(`return_24h < -0.02`). The factor set has max_overlap=6 (all 6 factors
exist in pos 17's set), but the operator change, factor drop, and
drawdown gate are not cosmetic.

**Plausibility expectation**: MODERATE-HIGH. The `crosses_below` trigger
improves story coherence (catches the moment of breakdown rather than a
static below-threshold state), but removing the vol filter introduces a
meaningful weakness: the strategy has no guard against continuously
declining markets and may ride a falling knife through sustained
downtrends. Sonnet may cite this as a moderate plausibility concern.

**Alignment expectation**: HIGH. All factors (BB, RSI, zscore, SMA,
return, close) are mean-reversion-canonical; entry and exit both encode
deviation-to-reversion logic. No momentum or trend-following contamination.

**SVR intuition (informal, for neutral-group aggregate context)**:
MODERATE. Unlike pure parameter-swap variants, pos 32 introduces a
meaningful structural change — a dynamic entry trigger and a dropped
regime filter — without adding a genuinely new trading concept. I
expect Sonnet to partially reward this rather than treat it as either a
pure recycled template or fully novel construction.

**One-sentence core judgment**: Strategy with a new structural element
(dynamic entry trigger) but same core mean-reversion skeleton; buy
logic is sound but vulnerable to prolonged downtrends due to dropped
vol filter.

### Candidate 5 — Position 62, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.

**Structural assessment**: Position 62 is a **horizon-mix variant of pos
17**, but not a literal superset. It keeps the BB + RSI + zscore + SMA +
return mean-reversion family, drops pos 17's `realized_vol_24h` active
market filter, and adds `return_1h` as a short-horizon take-profit exit.
Entry logic is close to the pos 17 oversold skeleton (`close <
bb_upper_24_2`, `rsi_14 < 35`, `zscore_48 < -1.5`) but uses
`return_24h < -0.02` instead of a volatility filter. Exit path B
(`return_1h > 0.025`) is a short-horizon take-profit shortcut, and max
hold is 72 bars.

**Plausibility expectation**: HIGH. Core story remains coherent:
detect an oversold deviation, then exit either on SMA/RSI recovery or on
the first meaningful short-horizon bounce. The missing volatility filter
is the main weakness relative to pos 17, because the entry has less
protection against quiet drift or sustained downtrend regimes.

**Alignment expectation**: HIGH. The strategy is clearly mean-reversion
overall: entry uses BB, RSI, zscore, and negative 24h return to identify
deviation, while exit path A encodes reversion toward the moving average.
The short-horizon take-profit path adds mild momentum flavor, but it is
still subordinate to the mean-reversion setup.

**SVR intuition (informal, for neutral-group aggregate context)**:
MODERATE-HIGH. Position 62 changes the horizon mix and removes the
volatility filter, so it is not a pure textbook repeat of pos 17. It also
does not add a genuinely new concept; it remains another BB/RSI/zscore
oversold-bounce construction with a faster profit exit.

**One-sentence core judgment**: Mean-reversion core with a short-horizon
take-profit exit; less regime-filtered than pos 17, but still playing the
same oversold-bounce game.

### Candidate 6 — Position 72, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.

**Structural assessment**: Position 72 is an **extreme-oversold variant
of pos 17's mean-reversion skeleton**. Entry thresholds are tightened on
RSI and volatility (`rsi_14 < 30` vs pos 17's 35;
`realized_vol_24h > 0.03` vs 0.015), while the zscore threshold remains
the same (`zscore_48 < -1.5`). `sma_24` is dropped. Exit path A uses
`rsi_14 crosses_above 50` as a dynamic trigger plus zscore normalization,
and exit path B accepts a 4% 24h return target.
Factor set is 6 (vs pos 17's 7); max_overlap=6, meaning the 6 factors
form a strict subset of a prior position.

**Plausibility expectation**: HIGH. The strategy design is coherent and
more selective than pos 17 on RSI and realized-volatility stress: it fires
under sharper oversold / volatility-spike conditions, then exits on either
recovery confirmation or a clear profit target. One concern: without SMA
as a trend anchor, the strategy has less guard against sustained
downtrends and could enter progressively deeper drawdowns on a falling
knife. This is a narrow concern and does not undermine the overall
coherence.

**Alignment expectation**: HIGH. Core factors (BB, RSI, zscore, vol,
close, return) all encode deviation-reversion. The story remains
mean-reversion throughout — specifically "extreme deviation, bet on
partial reversion." No momentum or trend-following factors are present.

**SVR intuition (informal, for neutral-group aggregate context)**: HIGH.
The candidate's changes relative to pos 17 are threshold tightening,
factor reduction (drop SMA), and exit styling (dynamic `crosses_above`
trigger plus return target). These are adjustments to the same underlying
mean-reversion skeleton, not a change in how the strategy enters a
position or what market phenomenon it targets. The entry logic remains
the same family: threshold-based oversold detection. I expect Sonnet to
recognize this as the same template with different knobs, not a new
construction.

**One-sentence core judgment**: Extreme-oversold variant wanting more
market panic before entering — same skeleton as pos 17 with tighter
parameters, not a new strategy concept.

### Candidate 7 — Position 73, volatility_regime, divergence_expected
Pre-registered label: `divergence_expected`. Predicted
`structural_variant_risk` < 0.5. Stage 2b observed high SVR for this same
source position (`structural_variant_risk = 0.85`), so this is a direct
test-retest conflict case.

**Structural assessment**: Position 73 is a volatility-regime /
trend-confirmed continuation strategy. The factor family is `close`,
`macd_hist`, `realized_vol_24h`, `return_168h`, and `sma_50`. Entry uses
`realized_vol_24h crosses_above 0.025` as the regime-shift trigger, with
`close > sma_50` and `macd_hist > 0` as directional confirmation. Exit
uses either volatility compression plus SMA breakdown
(`realized_vol_24h < 0.015` and `close crosses_below sma_50`) or a
long-horizon profit target (`return_168h > 0.08`). Max hold is 336 bars.

**My prediction**: `semantic_plausibility` MODERATELY HIGH. The strategy
has a coherent vol-expansion plus trend-confirmation story, with clear
regime-breakdown and profit-target exits. `semantic_theme_alignment` is
HIGH because volatility expansion is the primary entry trigger, even
though the payoff mechanism is trend continuation. I expect
`structural_variant_risk` MODERATE-HIGH, but with lower confidence than
the first-pass prose implied.

**Test-retest expectation (partial replication)**: I expect elevated SVR
relative to the 0.5 threshold, broadly supporting the Stage 2b observation
that D7a's `divergence_expected` label can be contradicted by D7b's
semantic judgment. I do not want to overstate exact replication: the
factor family is outside the dense mean-reversion cluster, and the
Stage 2b baseline supports overlap, but temperature-1.0 judgment noise
could produce meaningful downward drift.

**Reconciliation expectation**: If Stage 2c SVR remains above 0.5, this
supports the Stage 2b contradiction for this candidate. If SVR drops
below 0.5, the Stage 2b finding is refuted for pos 73 specifically, while
the overall divergence-axis pattern still depends on pos 17 and pos 74.

**Cross-candidate implication (divergence axis)**: The Stage 2c
divergence axis has three candidates (pos 17, 73, 74), all Stage 2b
overlaps. My predictions are asymmetric: pos 17 full-strength
replication, pos 73 elevated but with drift room, and pos 74 stable
moderate-level replication. This asymmetry is a testable claim about
factor-family-dependent judgment stability.

**One-sentence core judgment**: Vol-regime / trend-confirmed
continuation strategy; predicted MODERATE-HIGH SVR with lower confidence
than pos 17 because exact replication should not be overstated.

### Candidate 8 — Position 74, volume_divergence, divergence_expected
Pre-registered label: `divergence_expected`. Predicted
`structural_variant_risk` < 0.5. Stage 2b observed high-side SVR for this
same source position (`structural_variant_risk = 0.65`), but I am keeping
the selector-based divergence prediction to test whether that contradiction
repeats.

**Structural assessment**: Position 74 is a volume-confirmed breakout
strategy. Entry requires triple confirmation: `volume_zscore_24h > 2.0`
as the unusual-volume trigger, `close crosses_above sma_20` as the dynamic
price breakout trigger, and `rsi_14 < 60` as a not-fully-saturated
breakout participation filter.
Exit uses either volume fade plus SMA breakdown (`volume_zscore_24h <
-0.5` and `close crosses_below sma_20`) as a failed-breakout detector, or
a long-horizon profit target (`return_168h > 0.10`). The 5-factor set has
`max_overlap_with_priors=2` in the locked selector output, and this is the
only `volume_divergence` theme candidate in Stage 2c.

**My prediction**: `semantic_plausibility` HIGH. The entry logic is
coherent and reflects mature breakout-strategy thinking: volume leads,
price confirms, and the RSI cap avoids buying a fully saturated move,
while still allowing participation in a partially advanced breakout.
Exit logic is symmetric and sensible. I expect `semantic_theme_alignment`
MODERATELY HIGH: volume is the primary entry trigger and not merely an
auxiliary filter, but the actual profit mechanism resembles
volume-confirmed breakout / momentum continuation more than a pure
divergence narrative. I expect `structural_variant_risk` MEDIUM.

**Test-retest expectation (stable partial-contradiction replication)**:
I expect Sonnet to continue reading pos 74 as a MEDIUM / elevated-but-not
peak SVR case, roughly near the Stage 2b baseline rather than as a strong
lift story. This is a refinement of the factor-family-density hypothesis:
Stage 2b's baseline SVR values may already reflect the family-density
effect, with pos 17 in the dense mean-reversion family, pos 73 in a
sparser volatility-regime archetype, and pos 74 in a singleton theme slot
for volume divergence.

**Reconciliation expectation**: If Stage 2c SVR stays above 0.5, the
Stage 2b finding is replicated for this candidate: the
`divergence_expected` label is contradicted by D7b semantic judgment. If
SVR drops below 0.5, pos 74 would be the single divergence-axis case where
Stage 2c agrees with the label, an informative outcome indicating Stage
2b's 0.65 may have been upper-bound judgment noise rather than stable
archetype judgment.

**Cross-candidate implication (divergence axis consolidated)**: Across
pos 17, 73, and 74, my predictions are that all three replicate Stage 2b
directionally (SVR above 0.5, contradicting the `divergence_expected`
label), while each preserves its own approximate absolute level: pos 17
full-strength replication, pos 73 elevated with drift room, and pos 74
stable moderate-level replication. This asymmetric pattern encodes the
factor-family-density hypothesis: Stage 2b's observed SVR may already
reflect family-density effects, and Stage 2c should replicate these
baselines rather than amplify the pattern further.

**One-sentence core judgment**: Volume-confirmed breakout with a
not-fully-saturated participation filter and singleton theme positioning
in the batch; predicted to stably replicate Stage 2b's moderate high-side
SVR, completing the divergence-axis partial-contradiction replication
pattern.

### Candidate 9 — Position 77, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.

**Structural assessment**: Position 77 is a **softer / calmer variant of
the pos 17 mean-reversion skeleton**. The 6-factor set (`bb_upper_24_2`,
`close`, `realized_vol_24h`, `return_24h`, `rsi_14`, `sma_24`) is a
strict subset of pos 17's set, with `zscore_48` the distinctive drop;
the set also shares five factors with positions 8 and 22, placing it
well inside a dense MR cluster. Entry uses `close crosses_below
bb_upper_24_2` as a dynamic trigger (rather than a static threshold),
`realized_vol_24h < 0.025` as a **low-volatility** regime gate — the
opposite direction from pos 17's active-market filter — and `rsi_14 <
40` as a milder oversold confirmation (looser than pos 17's `< 35`).
Exit path A is a dynamic recovery (`close crosses_above sma_24` with
RSI recovery); exit path B is a realized 24h return target
(`return_24h > 0.04`). Max hold is 120 bars.
`factor_set_prior_occurrences` is 0 at this position.

**Plausibility expectation**: HIGH. This is a complete, internally
coherent mean-reversion story — entry captures an orderly downward
deviation under calmer market conditions, and exit takes either a
short-term mean recovery or a realized return capture. The setup is
less dramatic than the pos 17 / pos 72 extreme-oversold variants, but
the trade shape is logically sound and canonical for a calmer
mean-reversion play. One minor concern: the co-occurrence of `close
crosses_below bb_upper_24_2`, low realized volatility, and `rsi_14 <
40` may be a relatively low-frequency triggering condition, but this
is a viability-of-trigger concern and not a logical inconsistency.

**Alignment expectation**: HIGH. The strategy is unmistakably
mean-reversion throughout — deviation detection via BB and RSI,
reversion target via SMA, and return-based profit capture. No momentum,
volume, or regime-timing economic driver enters the story. Omitting
`zscore_48` relative to the dominant BB / RSI / zscore cluster is a
factor-reduction rather than a theme shift; the core
deviation-to-reversion narrative is preserved in full.

**SVR intuition (informal, for neutral-group aggregate context)**:
HIGH. This is still a recycled mean-reversion skeleton — factor-set
overlap (strict subset of pos 17, dense overlap with positions 8 and
22), canonical MR factor family, and shared exit structure together
make the construction read as a softer variant of the same familiar
template rather than a genuinely new configuration. The `crosses_below`
entry change shares the operator-family shift observed in pos 32, and
I acknowledge it applies a moderate pull away from pure HIGH. Unlike
pos 32, however — where that same operator change reads as a clear
rewrite of the entry trigger inside an otherwise intact skeleton — in
pos 77 the same shift reads as **part of a broader softening**: calmer
vol regime, looser RSI, dropped zscore. The net effect is "gentler
template," not "entry-logic rewritten." The volatility-regime direction
flip does not make the construction structurally new; it makes it a
calmer version of the same script. High overlap, textbook MR factor
family, and preserved deviation-reversion economic story together
dominate the moderate entry-operator pull.

The fact that a later candidate (position 107) exactly repeats this
factor set is not evidence available to D7b at position 77
(`factor_set_prior_occurrences = 0` at this position), so it does not
enter the prediction mechanism. It does, however, raise my confidence
as experiment author that pos 77 belongs to a reusable, non-novel MR
template family — consistent with the HIGH-leaning SVR intuition.

**One-sentence core judgment**: Softer / calmer variant of the
familiar mean-reversion template — easier to enter than the harsher
versions, and precisely that gentleness makes it look even more like a
recycled setup rather than a new construction.

### Candidate 10 — Position 83, volatility_regime, neutral
Pre-registered label: neutral. No per-candidate polarity prediction.
Contributes to neutral-group aggregate prediction. This is the first
non-mean-reversion candidate in the Stage 2c neutral group.

**Structural assessment**: Position 83 is a compression-breakout strategy
wrapped in a low-volatility precondition. The 5-factor set (`close`,
`realized_vol_24h`, `rsi_14`, `sma_50`, `volume_zscore_24h`) has
factor_set_prior_occurrences = 0 and max_overlap_with_priors = 3. Entry
requires four confirmations: `realized_vol_24h < 0.015` as a compression
filter, `close crosses_above sma_50` as a dynamic trend trigger,
`rsi_14 > 52` as a light directional confirmation, and
`volume_zscore_24h > 0.5` as a participation check. Exit uses either an
overheat-style condition combining elevated volatility and momentum, or
`close crosses_below sma_50` as a trend-break detector. Max hold is 240
bars.

**Plausibility expectation**: HIGH. The story is coherent end-to-end: the
`realized_vol_24h < 0.015` compression is intuitive as a setup phase; the
SMA crossover gives directional confirmation rather than a blind bet on
regime shift; `volume_zscore_24h > 0.5` ensures the breakout is not
entirely hollow by requiring at least some participation; and the exit
logic is sensible on both paths — reduce exposure on overheat, step aside
on trend break. The construction combines volatility, trend, and
participation cues, which makes it less clean than a single-mechanism
strategy, but not incoherent or weak enough to justify downgrading
plausibility.

**Alignment expectation**: MODERATE-HIGH. `realized_vol_24h` participates
on both sides of the trade — compression on entry, expansion on exit — so
volatility state is not just decorative, and the compression-to-expansion
arc is genuinely regime-shaped. That said, the actual trade trigger is
`close crosses_above sma_50`, which is canonically a trend-following
switch, and `rsi_14 > 52` plus `volume_zscore_24h > 0.5` function more as
light trend-and-participation confirmations than as pure regime
instrumentation. The cleanest one-line read is: regime sets the stage,
trend pulls the trigger. The theme therefore reads as a trend breakout
wrapped in a low-volatility precondition rather than a pure
volatility-regime construction. I therefore expect some alignment
downgrade from pure HIGH on hybrid-structure grounds.

**SVR intuition (informal, for neutral-group aggregate context)**:
MODERATE-HIGH. This candidate still reads as a familiar breakout-style
template at its core: the close / SMA / volatility / volume mix is not
structurally exotic, and reconstructed overlap context suggests nearby
related forms exist. At the same time, the low-volatility entry setup does
more than add surface decoration: it changes the timing logic from a
generic breakout read toward a compression-breakout framing, which is not
the same as a trivial threshold tweak. The light-touch RSI and volume
confirmations also give the candidate some specific flavor, even if they
do not fundamentally change the skeleton. The net read is: mostly
familiar template reuse, but not plain old-script recycling. I therefore
expect SVR to lean upward while stopping short of a fully maximal
recycled-template judgment.

**One-sentence core judgment**: A familiar breakout skeleton wrapped in a
meaningful low-volatility setup, with light hybrid trend / volume
confirmation logic — not a new construction, but also not plain old-script
reuse.

### Candidate 11 — Position 97, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5. This is a Stage 2b overlap candidate
(Stage 2b observed: plaus=0.75, align=0.90, svr=0.95) and is the only
agreement-axis overlap in Stage 2c. Framed primarily as a **test-retest
replication** case, with the `agreement_expected` label satisfied as a
direct consequence.

**Structural assessment**: Position 97 is an **overbought
mean-reversion** strategy — the first short-direction trade shape in the
Stage 2c batch, where all prior MR candidates (pos 17, 22, 32, 62, 72,
77) encoded the oversold bounce. The 6-factor set (`bb_upper_24_2`,
`close`, `return_24h`, `rsi_14`, `sma_24`, `zscore_48`) has
`factor_set_prior_occurrences = 1` — the first non-zero value in the batch
— and `max_overlap_with_priors = 6`. Entry requires four overextension
confirmations: `close >= bb_upper_24_2` as a static upper-band breach,
`zscore_48 > 1.8` as a strong statistical-deviation filter,
`rsi_14 > 68` as momentum overheat, and `return_24h > 0.02` as realized
recent-advance confirmation. Exit path A is zscore normalization plus
`close crosses_below sma_24`; exit path B is negative `return_24h` plus
RSI breakdown. Max hold is 120 bars.

**Plausibility expectation**: HIGH. The trade story — "a move that ran
too far in one direction will give some of it back" — is directly
analogous to the oversold-bounce story that dominates the batch, only
mirrored. The entry does not stretch on any single factor; it stacks four
independent overextension confirmations (band breach, statistical z-score,
RSI heat, realized return), each reading as a distinct verification that
the market is genuinely overheated rather than drifting in normal range.
Exit logic is symmetric: normalize to mean and confirm with SMA breakdown,
or detect an early reversal via negative return and RSI breakdown. One
caveat carried over from Stage 2b reasoning: the short-like overbought
logic is expressed as a long entry shape in the DSL, which is a
modeling-surface constraint rather than a logical flaw, but it may cause
Sonnet to continue noting this as a mild plausibility clip — consistent
with the mild plausibility discount already seen in Stage 2b relative to
alignment and SVR.

**Alignment expectation**: HIGH. BB, zscore, and RSI together form the
canonical statistical-overextension trio; `sma_24` provides the
mean-reversion target; `return_24h` ties the entry and exit sides
together. Every factor encodes deviation-then-reversion, and the
short-direction inversion does not shift the economic theme — "overheated
move reverts" is a direct mirror of "oversold move reverts," both squarely
inside the mean-reversion family. This is textbook mean-reversion
vocabulary throughout. Stage 2b's 0.90 alignment score is expected to
replicate closely.

**Test-retest expectation (Lock 10a)**: MODERATE-HIGH. Stage 2b's 0.95
SVR is a near-ceiling score, so the natural test-retest expectation is
replication in the same high-risk region with some room for modest
downward drift but none for upward movement. I expect the score to remain
comfortably above the 0.5 threshold while landing slightly below the
Stage 2b ceiling rather than replicating the 0.95 point estimate exactly.
Two forces pull the score back from the ceiling: (a) temperature-1.0
judgment noise, which is expected to produce modest downward drift on any
near-ceiling baseline; and (b) the short-direction inversion is genuinely
rarer across the batch than the oversold variants, and Sonnet may grant a
small novelty credit for the directional flip even while reading the
structural skeleton as familiar. This candidate is predicted to match
Stage 2b's reasoning pattern closely: the Stage 2b explanation — that
variant risk is high **because the same factor set was already present
and only thresholds/operators appeared to change** — is expected to be
reached again in Stage 2c via a similar path, though possibly stated as a
short-direction mirror rather than a direct repeat.

**Reconciliation expectation**: SVR >= 0.5 satisfies the
`agreement_expected` rubric; the categorical label prediction is confirmed
as a consequence of the test-retest prediction. The scientific claim is
not "near-identical input, near-identical output" — the direction
inversion and short-like long-entry constraint are real semantic shifts —
but rather that a candidate carrying a real prior factor-set occurrence
and a canonical overextension-trio skeleton should still preserve enough
structural overlap to satisfy the agreement rubric robustly.

**Cross-candidate implication (narrow)**: C11 is the single
agreement-axis overlap in Stage 2c; its test-retest behavior should be
interpreted on its own terms and not pre-committed to any broader pattern
across later agreement candidates.

**One-sentence core judgment**: First short-direction variant in the
batch, built on the canonical statistical-overextension trio with a real
prior factor-set occurrence; logic inverted but core unchanged, predicted
to stay in the same high-risk SVR region observed in Stage 2b with modest
downward drift from the 0.95 ceiling.

### Candidate 12 — Position 102, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.
Not a Stage 2b overlap candidate. Framed as a **label-replication** case:
the question is whether D7b's semantic SVR judgment supports the
selector's `agreement_expected` label on a highly recycled candidate
lacking any Stage 2b baseline.

**Structural assessment**: Position 102 is a **highly recycled
mean-reversion candidate**. The 7-factor set (`bb_upper_24_2`, `close`,
`realized_vol_24h`, `return_24h`, `rsi_14`, `sma_24`, `zscore_48`) is an
**exact 7-factor repeat of positions 17 and 27**, giving
`factor_set_prior_occurrences = 2` — the first occurrence of a
two-prior-set in the batch — and `max_overlap_with_priors = 7`, the first
Stage 2c candidate with both a two-prior exact repeat and maximal selector
overlap (`max_overlap_with_priors = 7`). Entry requires
`close crosses_above bb_upper_24_2`, `rsi_14 < 35`,
`realized_vol_24h < 0.032`, and `zscore_48 < -1.2`. Exit path A is
`close crosses_above sma_24` with RSI recovery; exit path B is
`return_24h > 0.028` with zscore recovery. Max hold is 120 bars.

The entry condition reads with an **internal inconsistency at the
literal-DSL level**: `close crosses_above bb_upper_24_2` describes an
upper-band breakout, but `rsi_14 < 35` and `zscore_48 < -1.2` describe a
deeply oversold state, and the exit logic (SMA recovery, zscore recovery)
completes the oversold-bounce story. The plausible intended construction
is an oversold-bounce variant with a `crosses_above` trigger on a
lower-band factor, but preregistration discipline requires reading the
DSL as written rather than patching naming assumptions into the candidate.
Worksheet Section C flags this identically as "lower-band naming issue or
a logic inconsistency."

**Plausibility expectation**: MODERATE-LOW. The intended story is visible
— oversold setup, rebound confirmation, recovery exit — but when the DSL
is read literally, the entry-side trigger contradicts the oversold body of
the entry conditions. The story coheres only under a charitable naming-fix
reading, which is not a judgment Sonnet is expected to silently perform. I
expect Sonnet to either (a) explicitly call out the inconsistency in its
reasoning, which directly clips plausibility, or (b) paper over it by
describing the intended story, which still typically costs plausibility
even when Sonnet is willing to read past the surface contradiction. Either
way, plausibility is expected to land meaningfully below the HIGH tier
that a cleanly written version of the same candidate would receive.

**Alignment expectation**: MODERATE-HIGH. The factor family
(`bb_upper_24_2`, `rsi_14`, `zscore_48`, `sma_24`, plus `return_24h` and
the low-volatility filter) is canonical mean-reversion vocabulary, and
the economic theme being attempted remains deviation-to-reversion
throughout. The question is not whether this is mean reversion — it
clearly is — but whether the DSL renders the theme cleanly. The literal
entry-condition contradiction damages thematic clarity without
redirecting the theme toward a different family, which is the precise
pattern that warrants a downgrade from HIGH to MODERATE-HIGH: theme is
preserved, but purity is compromised.

**SVR expectation**: HIGH. The recurrence signal here is the strongest in
the batch to date. The 7-factor set is an **exact repeat** of two prior
positions (17 and 27), with `factor_set_prior_occurrences = 2` and
`max_overlap_with_priors = 7` — both batch firsts. The MR skeleton
(BB-band + zscore + RSI + SMA with vol filter and return exit) is already
densely occupied by earlier candidates. The odd entry-trigger wording
does not redeem recurrence: a suspicious-looking condition reads more
like a likely naming or logic issue than as genuine structural novelty,
and I do not treat "written oddly" as equivalent to "written new." The
DSL-level mismatch is expected to land its cost on plausibility, not on
SVR. I therefore expect Sonnet to read the candidate's structure as a
highly recycled MR template with thresholds and operators lightly adjusted
on top of a fully repeated factor set — the same reasoning pattern Stage
2b identified on pos 97 ("the same factor set was already present and
only thresholds/operators appeared to change"), applied here to a more
severely recycled case.

**Reconciliation expectation**: SVR >= 0.5 satisfies the
`agreement_expected` rubric; the categorical label prediction is
confirmed. This prediction is made independently of any broader pattern
across prior-occurrence counts or across later agreement-labeled
candidates, consistent with Lock 8 narrow-claim discipline. C12's HIGH
judgment is driven by its own structural facts: an exact 7-factor repeat
against two priors, maximal overlap at 7, and the decision to treat the
DSL-level mismatch as a plausibility cost rather than as structural
novelty.

**One-sentence core judgment**: Exact repeated factor set and maximal
overlap dominate; the odd entry reads more like a likely naming or logic
issue than genuine novelty — theme stays mean-reversion, SVR stays HIGH
on the strength of the 7-factor repeat, and plausibility takes the clear
hit for the DSL-level inconsistency.

### Candidate 13 — Position 107, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.
Not a Stage 2b overlap candidate. Framed as a **label-replication** case:
the question is whether D7b's semantic SVR judgment supports the
selector's `agreement_expected` label on a familiar, internally coherent
recycled MR candidate.

**Structural assessment**: Position 107 is a **canonical oversold-bounce
mean-reversion candidate** built on the dominant MR factor cluster. The
6-factor set (`bb_upper_24_2`, `close`, `realized_vol_24h`, `return_24h`,
`rsi_14`, `sma_24`) is an **exact factor-set repeat of position 77**,
giving `factor_set_prior_occurrences = 1` and
`max_overlap_with_priors = 6`; the same six factors also overlap fully
with position 17, placing the candidate inside the already-dense MR
cluster of the batch. Entry requires `close <= bb_upper_24_2`,
`rsi_14 < 35`, `realized_vol_24h > 0.015`, and `return_24h < -0.02`.
Exit path A is `close crosses_above sma_24` with RSI recovery; exit path
B is `return_24h > 0.035` with high RSI. Max hold is 168 bars.

**Plausibility expectation**: HIGH. The trade story is complete and
internally coherent: identify a price deviation downward (BB-band touch
plus deep RSI oversold plus a meaningful negative 24h return), confirm
the market is active rather than dead (`realized_vol_24h > 0.015`), buy
the dip, and exit either on mean recovery or on realized profit capture.
Each entry condition reads as a distinct verification of the oversold
setup; no single factor is being asked to carry the whole story. Worksheet
Section C notes the absence of `zscore_48` relative to the BB / RSI /
zscore canonical trio, but RSI and the drawdown gate (`return_24h <
-0.02`) substantively cover the same deviation-detection function, so the
omission costs little plausibility in practice.

**Alignment expectation**: HIGH. The factor family (`bb_upper_24_2`,
`rsi_14`, `sma_24`, `return_24h`, plus `close` and the
realized-volatility filter) is canonical mean-reversion vocabulary. Every
entry condition encodes deviation-detection and every exit condition
encodes reversion-or-realized-recovery. There is no meaningful momentum,
trend-following, or regime-timing contamination. The economic story is
unambiguously deviation-to-reversion throughout.

**SVR expectation**: HIGH. The exact factor-set recurrence with position
77, together with the broader overlap with the already-dense MR cluster
around position 17, makes this read as a familiar template whose
differences are mainly threshold and operator adjustments rather than
meaningful structural novelty. The strict RSI threshold (`< 35`), the
active-market vol filter (`> 0.015`), and the drawdown gate
(`return_24h < -0.02`) all line up closely with the strict
oversold-bounce parameter range used elsewhere in the MR cluster, so the
candidate reads less as a new construction and more as another parameter
setting on the same skeleton. Worksheet Section D notes that the
threshold-band entry differs from position 77's `crosses_below` entry and
that high-volatility confirmation differs from position 77's
low-volatility stabilization; these differences create some surface
distinction but do not outweigh the exact factor-set recurrence and the
underlying familiarity of the MR skeleton. I do not treat threshold and
operator variation on a fully repeated factor set as structural novelty.

**Reconciliation expectation**: SVR >= 0.5 satisfies the
`agreement_expected` rubric; the categorical label prediction is
confirmed. This is an independent candidate-level judgment and should not
be read as implying any broader monotonic rule across
`factor_set_prior_occurrences` levels or across later agreement-labeled
candidates, consistent with Lock 8 narrow-claim discipline. C13's HIGH
judgment rests on its own structural facts: exact factor-set recurrence
with one prior, full six-factor overlap with the MR cluster anchor at pos
17, and threshold/operator settings that remain well within the familiar
strict oversold-bounce range.

**One-sentence core judgment**: A familiar, internally coherent, cleanly
written oversold-bounce mean-reversion template — the only real changes
from the recurring skeleton are threshold and operator adjustments, which
do not constitute structural novelty; theme, plausibility, and SVR all
land cleanly at HIGH.

### Candidate 14 — Position 112, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.
Not a Stage 2b overlap candidate. Framed as a **label-replication** case:
the question is whether D7b's semantic SVR judgment supports the
selector's `agreement_expected` label on a heavily repeated, internally
coherent recycled MR candidate.

**Structural assessment**: Position 112 is a **strict oversold-bounce
mean-reversion candidate under a low-volatility-collapse regime filter**.
The 7-factor set (`bb_upper_24_2`, `close`, `realized_vol_24h`,
`return_24h`, `rsi_14`, `sma_24`, `zscore_48`) is an **exact 7-factor
repeat of positions 17, 27, and 102**, giving
`factor_set_prior_occurrences = 3` — the highest prior-occurrence count
observed up to this point in firing order — and
`max_overlap_with_priors = 7`, matching the maximal-overlap level. Entry
requires `close < bb_upper_24_2`, `zscore_48 < -1.8`,
`realized_vol_24h < 0.015`, and `rsi_14 < 35`. Exit path A is zscore
and RSI normalization; exit path B is `return_24h > 0.035` with
`close crosses_above sma_24`. Max hold is 120 bars.

**Plausibility expectation**: HIGH. The trade story is complete and
internally coherent: identify a deep oversold deviation (`zscore_48 <
-1.8` and `rsi_14 < 35` together encode strong statistical and momentum
oversold confirmation), restrict entry to a quiet-market regime
(`realized_vol_24h < 0.015`), and exit either on mean recovery or on
realized profit capture confirmed by an SMA crossover. Each entry
condition reads as a distinct verification of the setup; the four
conditions all point in a consistent direction without contradiction. One
mild concern: the simultaneous co-occurrence of `realized_vol_24h <
0.015`, `zscore_48 < -1.8`, and `rsi_14 < 35` is a relatively rare
market state, so the strategy may have a low trigger frequency — but this
is a viability-of-trigger concern, not a logical-coherence concern, and
is not severe enough to warrant a downgrade.

**Alignment expectation**: HIGH. The factor family (`bb_upper_24_2`,
`zscore_48`, `rsi_14`, `sma_24`, plus `close`, `return_24h`, and
`realized_vol_24h`) is canonical mean-reversion vocabulary, with
BB/zscore/RSI/SMA forming the textbook statistical-overextension and
reversion-target spine. The low-volatility filter operates as a regime
gate on entry without redirecting the underlying theme — the economic
story remains unambiguously deviation-to-reversion throughout, and the
volatility condition serves as state-selection rather than as an
alternative economic driver. Worksheet Section C raises the question of
whether the volatility-collapse framing should be read as an embedded
regime filter; in this candidate's structure, the regime filter is one of
four entry conditions and clearly subordinate to the oversold-bounce core,
so theme purity is preserved.

**SVR expectation**: HIGH. The recurrence signal is strong:
`factor_set_prior_occurrences = 3` is the highest value observed up to
this point in firing order, and `max_overlap_with_priors = 7` matches the
maximal level. The 7-factor MR skeleton (BB-band + zscore + RSI + SMA
with vol filter and return exit) is by now densely populated by earlier
candidates, and C14's entry conditions sit firmly within the strict
oversold-bounce parameter range used elsewhere in the cluster. The
specific changes relative to the recurring skeleton — a stricter zscore
threshold (`< -1.8`) and a low-volatility-collapse entry gate (`< 0.015`)
instead of an active-market filter — read as market-state packaging on a
familiar template, not as structural novelty: the underlying trade is the
same oversold-bounce setup, executed in a quieter regime with deeper
statistical-overextension confirmation. I do not treat threshold
tightening or regime-gate flavoring on a fully repeated factor set as
structural novelty. Worksheet Section D notes that the stricter zscore
threshold and the volatility-collapse entry distinguish this from
high-volatility versions; this surface distinction does not outweigh the
three-prior exact factor-set repeat or the underlying familiarity of the
MR skeleton.

**Reconciliation expectation**: SVR >= 0.5 satisfies the
`agreement_expected` rubric; the categorical label prediction is
confirmed. This is an independent candidate-level judgment and should not
be read as implying any monotonic rule across
`factor_set_prior_occurrences` levels, recurrence depth, or later
agreement-labeled candidates, consistent with Lock 8 narrow-claim
discipline. C14's HIGH judgment rests on its own structural facts: exact
7-factor recurrence against three priors, maximal selector overlap at 7,
strict oversold-bounce parameter settings drawn from the existing
cluster's parameter range, a coherent and contradiction-free DSL, and a
regime filter that operates as a market-state selector rather than as a
theme-shifting component.

**One-sentence core judgment**: A cleanly written, heavily recycled
classic MR candidate — the 7-factor skeleton is crowded, the story is
familiar, and the low-volatility-collapse angle is packaging rather than
new structure; theme, plausibility, and SVR all land cleanly at HIGH.

### Candidate 15 — Position 117, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.
Contributes to neutral-group aggregate prediction.

**Structural assessment**: Position 117 is an **oversold-bounce
mean-reversion candidate with a MACD-based exit module**. The 7-factor set
(`bb_upper_24_2`, `close`, `macd_hist`, `realized_vol_24h`, `return_24h`,
`rsi_14`, `zscore_48`) has `factor_set_prior_occurrences = 0` and
`max_overlap_with_priors = 6`; reconstructed overlap context shows
six-factor overlaps with positions 17 and 72, placing the candidate
inside the dense oversold-MR cluster. Entry requires
`close crosses_above bb_upper_24_2`, `rsi_14 < 38`,
`realized_vol_24h > 0.016`, and `zscore_48 < -1.2`. Exit path A is RSI
and zscore normalization; exit path B is `return_24h > 0.035` with
`macd_hist crosses_below 0`. Max hold is 168 bars.

The entry condition exhibits the **same family of literal-DSL
inconsistency** previously observed: `close crosses_above bb_upper_24_2`
describes an upper-band breakout while `rsi_14 < 38` and `zscore_48 <
-1.2` describe an oversold state, and the exit logic (RSI/zscore
normalization, MACD-confirmed momentum fade) completes the oversold-bounce
story. The plausible intended construction is an oversold-bounce variant
with a `crosses_above` trigger on a lower-band factor, but preregistration
discipline requires reading the DSL as written rather than patching naming
assumptions into the candidate.

**Plausibility expectation**: MEDIUM. The intended story is visible —
`rsi_14 < 38`, `zscore_48 < -1.2`, and the active-volatility filter
together support the read that the market has gone through a weak,
disordered, deviated phase and the strategy is trying to catch a recovery.
Read literally, however, the entry-side trigger contradicts the oversold
body of the entry conditions. The story coheres only under a charitable
naming-fix reading, which is not a judgment Sonnet is expected to silently
perform. The plausibility cost here is real but moderated by the
MACD-based exit leg, which adds a layer of trade-management context and
makes the overall strategy easier to interpret than the entry-side trigger
alone would suggest. I do not patch probable naming glitches at judgment
time, so plausibility cannot land at HIGH and instead settles at MEDIUM.

**Alignment expectation**: MODERATE-HIGH. The body of the strategy is
unambiguously mean-reversion: the entry conditions (BB / RSI / zscore /
vol) are canonical oversold-bounce vocabulary, and exit path A (RSI and
zscore normalization) is the textbook reversion-confirmation exit. But
`macd_hist` is a genuine cross-family factor — momentum / trend grammar —
and it is not a decorative addition: it sits in exit path B as the
explicit "exit when the rebound's momentum fades" leg. The construction
is therefore still MR at its core but no longer the cleanest textbook MR
candidate; it is a hybrid version with a momentum-flavored exit module.
Worksheet Section C flags this same point. The hybrid load is meaningful
but still secondary to the strategy's clearly mean-reversion core, so
alignment lands at MODERATE-HIGH rather than dropping further.

**SVR intuition (informal, for neutral-group aggregate context)**:
MODERATE-HIGH. The candidate sits squarely inside a familiar oversold-BB
mean-reversion family — `max_overlap_with_priors = 6`, six-factor overlaps
with positions 17 and 72 in the reconstructed context, and an entry body
drawn directly from the dense MR cluster's parameter range. That core
remains highly recycled. But this is not a purely threshold-only recycled
candidate: `macd_hist` is placed in exit path B as a **genuine
cross-family exit-module change**, not as a cosmetic wrapper. The novelty
credit is earned by the MACD exit module, not by the entry-side
`crosses_above` weirdness — written oddly is not the same as written new,
and the entry literal inconsistency does not buy the candidate any
structural-variant credit. The combined picture is a familiar MR skeleton
plus a real exit-grammar addition, which lifts the candidate above pure
threshold-only recycling but keeps it well within the high-overlap MR
neighborhood. SVR therefore lands at MODERATE-HIGH: above the 0.5
threshold, but a step below the cleanly recycled exact-repeat candidates.

**One-sentence core judgment**: A familiar oversold-bounce mean-reversion
candidate whose entry carries the same family of literal awkwardness as
earlier mismatched candidates and whose real novelty comes from a
MACD-based exit module rather than from the entry weirdness — theme stays
MR, plausibility takes a real but softened hit, and SVR lands above the
threshold but a notch below the cleanly recycled HIGH cluster.

### Candidate 16 — Position 138, volatility_regime, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.
Contributes to neutral-group aggregate prediction. This is also a Stage 2b
overlap candidate (Stage 2b observed: plaus=0.75, align=0.90, svr=0.15)
and the only overlap candidate carrying a neutral label. Framed primarily
as a **test-retest replication** case, with neutral-group aggregate
evidence as a secondary role.

**Structural assessment**: Position 138 is a **volatility-led breakout
candidate** organized around a vol / volume / SMA triplet. The 5-factor
set (`close`, `realized_vol_24h`, `return_24h`, `sma_20`,
`volume_zscore_24h`) has `factor_set_prior_occurrences = 0` and
`max_overlap_with_priors = 4`; reconstructed overlap context shows
five-factor overlaps with positions 88 and 93 only when RSI or MACD is
added, which means there is no tight match in the prior set without
expanding the comparison factor list. Entry requires
`realized_vol_24h > 0.03` (volatility expansion),
`close crosses_above sma_20` (price breakout above the trend line), and
`volume_zscore_24h > 1` (volume confirmation). Exit path A is volatility
compression plus `close crosses_below sma_20`; exit path B is
`return_24h > 0.03`. Max hold is 72 bars. Position bucket is `late`.

**Plausibility expectation**: HIGH. The trade story is clean and
internally coherent: the market transitions from quiet to active,
volatility and volume expand together, price breaks above the trend line,
and the strategy rides the breakout for a delimited window before either
compression-and-trend-break exits the trade or a realized return target
captures the move. The three entry conditions mix volatility, volume, and
trend grammar, but they do not contradict each other — they reinforce the
same setup along three independent axes. I expect Stage 2c plausibility to
land at HIGH, slightly above or at the Stage 2b 0.75 score, with mild
upward drift room because the Stage 2b score already incorporated whatever
surface concerns Sonnet might raise, such as entering on already elevated
rather than just emerging volatility.

**Alignment expectation**: MODERATE-HIGH. `realized_vol_24h` is the
genuine anchor: it appears as the entry-side regime expansion gate and as
the exit-side compression detector, so volatility state participates on
both sides of the trade lifecycle rather than serving as decoration. But
the construction is not a pure regime-switch strategy — it visibly imports
breakout, momentum, and volume-confirmation grammar through the SMA
crossover and the volume z-score filter. The theme stays primarily
`volatility_regime`, but with genuine hybrid load, which is the precise
pattern that warrants a downgrade from HIGH to MODERATE-HIGH. Worksheet
Section C flags this identically. I expect Stage 2c alignment to land at
MODERATE-HIGH, with slight downward drift from Stage 2b's near-high 0.90
alignment score.

**Test-retest expectation (Lock 10a)**: MODERATE-LOW. Stage 2b's 0.15 SVR
is a clear LOW reading, and the Stage 2b reasoning explicitly attributed
it to the candidate avoiding the RSI-heavy prior structures that dominate
the batch and instead organizing around a relatively independent
vol / volume / SMA triplet. Stage 2c Sonnet evaluates the same source
position with identical prior history visible, so the information that
drove Stage 2b's LOW reading remains directly available. I expect Sonnet
to reach the same structural reading via the same reasoning path: this
candidate's differences are not threshold tweaks on a familiar skeleton
but a genuine factor-construction difference relative to the dominant MR
cluster. The expected SVR therefore lands at MODERATE-LOW — preserving the
LOW-side directional reading and remaining below the 0.5 threshold, with
modest upward drift room from the 0.15 baseline acknowledged for two
reasons: (a) temperature-1.0 judgment noise applied to a near-floor
baseline has more room above than below; and (b) Sonnet might give partial
recurrence credit if it identifies looser overlaps with the vol / volume /
SMA neighborhood (positions 88 and 93 in the reconstructed context) that
the Stage 2b reasoning did not emphasize.

**SVR intuition for neutral-group aggregate context**: The test-retest
expectation above is also the informal SVR intuition for neutral-group
aggregate purposes. C16 is the clearest below-threshold lean in the
neutral group and therefore makes an important contribution to the lower
side of the neutral-group aggregate distribution. This dual reading does
not change the prediction direction — it only notes that C16's role in
the Stage 2c evidence structure spans both the Lock 10a test-retest grid
and the Lock 8 neutral-group aggregate mechanism.

**Reconciliation expectation**: As a `neutral`-labeled candidate, C16
carries no per-candidate polarity prediction under Lock 8; its informal
MODERATE-LOW lean contributes to the neutral-group aggregate-level claim
rather than to a per-candidate label-rubric check. As a Stage 2b overlap
candidate, C16's predicted MODERATE-LOW SVR — preserving the LOW-side
reading from Stage 2b with modest upward drift acknowledgment — is
interpreted as test-retest stability evidence under Lock 10a. The two
evaluation mechanisms operate independently: Lock 10a looks at directional
preservation relative to Stage 2b; Lock 8's aggregate condition looks at
the distributional shape across all nine neutral candidates.

**One-sentence core judgment**: A coherent volatility-led breakout with a
real hybrid load on alignment, organized around a vol / volume / SMA
triplet that genuinely sits apart from the dense RSI-heavy MR prior
cluster — predicted to preserve Stage 2b's LOW-side reading at
MODERATE-LOW with mild upward drift from the 0.15 baseline, sustaining the
neutral-group aggregate condition by anchoring the below-threshold side.

### Candidate 17 — Position 143, volatility_regime, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.
Contributes to neutral-group aggregate prediction.

**Structural assessment**: Position 143 is a **layered volatility-led
breakout candidate with explicit short-horizon momentum confirmation and
long-horizon trend-extension framing**. The 6-factor set (`close`,
`realized_vol_24h`, `return_168h`, `return_24h`, `sma_20`,
`volume_zscore_24h`) has `factor_set_prior_occurrences = 0` and
`max_overlap_with_priors = 5`. Entry requires
`realized_vol_24h > 0.035` (strict volatility expansion),
`close crosses_above sma_20` (price breakout above the trend line),
`volume_zscore_24h > 1` (volume confirmation), and `return_24h > 0.01`
(short-horizon momentum confirmation). Exit path A is
`close crosses_below sma_20` with lower realized volatility (compression
plus trend break); exit path B is `return_168h > 0.08` (long-horizon
trend-extension target). Max hold is 168 bars. Position bucket is `late`.

**Plausibility expectation**: HIGH. The trade story is complete and
internally coherent. The four entry conditions all push in the same
direction: the market has shifted from ordinary to highly active state,
and price, volume, and short-term return are all confirming the same
breakout direction simultaneously — this reads less like an early setup
and more like an already confirmed expanding move. The exit logic is
symmetric and lifecycle-complete: if price falls back below `sma_20` and
volatility cools, that signals the expansion has stalled and the trade
exits on trend break; alternatively, if the 168-hour return reaches 0.08,
the trade takes profit on a longer-horizon trend-extension target. The
strategy mixes volatility, breakout, volume, and momentum vocabulary, but
these grammars reinforce rather than contradict each other, and they are
layered across distinct time horizons rather than stacked redundantly on
the same axis.

**Alignment expectation**: MODERATE-HIGH. `realized_vol_24h` is the
genuine theme anchor: entry uses volatility expansion to define the regime
shift, and exit path A uses lower realized volatility to detect the regime
cooling, so volatility state participates as the backbone of the trade
lifecycle rather than as decoration. But the construction is not a pure
regime-switch strategy. The `close crosses_above sma_20` breakout grammar,
the `volume_zscore_24h > 1` volume-confirmation filter, the
`return_24h > 0.01` short-horizon momentum gate, and the
`return_168h > 0.08` long-horizon trend-extension exit together push the
strategy into a volatility + breakout + volume + momentum hybrid. The
theme stays primarily `volatility_regime`, but with genuine multi-grammar
load that warrants a downgrade from HIGH to MODERATE-HIGH. Worksheet
Section C flags this same trend-extension profile.

**SVR intuition (informal, for neutral-group aggregate context)**:
MODERATE-HIGH. The candidate is not an exact repeat
(`factor_set_prior_occurrences = 0`) and is not a threshold-only recycle,
but reconstructed overlap context shows five-factor overlaps with
positions 88, 93, and 138, indicating that the candidate sits inside a
familiar vol / volume / SMA breakout neighborhood rather than as a fully
isolated construction. It therefore does not read as genuinely novel. But
it also does not read as the most cleanly recycled vol-breakout candidate
either, because the addition of `return_24h` as a short-horizon momentum
gate and `return_168h` as a long-horizon exit target is not a cosmetic
adjustment — these additions make the trade lifecycle multi-layered,
mixing immediate breakout confirmation with planned trend-extension
capture. The combined picture is **a familiar volatility-breakout family
member written as a layered hybrid variant**: more structured than a clean
neighborhood recycle, less independent than a genuinely new construction.
SVR therefore lands at MODERATE-HIGH — comfortably above the 0.5
threshold, but below the cleanly recycled HIGH cluster.

**One-sentence core judgment**: A coherent, lifecycle-complete
volatility-led breakout written as a layered hybrid variant — vol remains
the theme anchor, but short-horizon momentum confirmation and long-horizon
trend-extension framing make the construction more structured than a clean
neighborhood recycle, so plausibility is high, alignment carries genuine
hybrid load, and SVR lands at MODERATE-HIGH inside the familiar
vol-breakout neighborhood.

### Candidate 18 — Position 147, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.
Not a Stage 2b overlap candidate. Framed as a **label-replication** case:
the question is whether D7b's semantic SVR judgment supports the
selector's `agreement_expected` label on the most heavily repeated,
internally clean recycled MR candidate up to this point in the batch.

**Structural assessment**: Position 147 is a **clean canonical
oversold-bounce mean-reversion candidate in an active-volatility regime**.
The 7-factor set (`bb_upper_24_2`, `close`, `realized_vol_24h`,
`return_24h`, `rsi_14`, `sma_24`, `zscore_48`) is an **exact 7-factor
repeat of positions 17, 27, 102, and 112**, giving
`factor_set_prior_occurrences = 4` — the highest prior-occurrence count
observed up to this point in firing order — and `max_overlap_with_priors =
7`, matching the maximal-overlap level. Entry requires
`close < bb_upper_24_2`, `zscore_48 < -1.5`, `rsi_14 < 35`, and
`realized_vol_24h > 0.025`. Exit path A is `close crosses_above sma_24`
with RSI recovery; exit path B is `return_24h > 0.025`. Max hold is
168 bars. Position bucket is `late`.

**Plausibility expectation**: HIGH. The trade story is fully canonical and
internally coherent. The four entry conditions (`zscore_48 < -1.5`,
`rsi_14 < 35`, `realized_vol_24h > 0.025`, `close < bb_upper_24_2`)
jointly support a single textbook story: in an active-volatility
environment, a meaningful oversold deviation has occurred, so a
mean-reversion bounce is the expected response. The exit logic is
symmetric and equally textbook: either price recovers to the moving
average and RSI normalizes, or the 24-hour return reaches a profit target
and the trade takes the realized gain. There is no DSL-level inconsistency
anywhere in the construction, and no hybrid grammar contaminates the
story. The candidate reads as one of the cleanest versions of the dominant
oversold-bounce template in the batch.

**Alignment expectation**: HIGH. The factor set is essentially the
complete canonical mean-reversion vocabulary: BB, zscore, RSI, SMA,
volatility, and return all serve the same deviation-to-reversion theme.
`realized_vol_24h > 0.025` operates strictly as a market-state filter —
selecting the regime in which the oversold-bounce story applies — rather
than as a theme-shifting component. There is no visible momentum,
breakout, or trend-following contamination anywhere in the candidate.
Theme purity is therefore as high as this batch has produced.

**SVR expectation**: HIGH. The recurrence signal is the strongest in the
batch so far: `factor_set_prior_occurrences = 4` is the maximum observed
value up to this point in firing order, and `max_overlap_with_priors = 7`
matches the maximal level. The 7-factor MR skeleton (BB-band + zscore +
RSI + SMA with volatility filter and return exit) has by now appeared as
an exact factor set four times before in the proposer's prior history, and
C18's entry conditions sit firmly within the strict oversold-bounce
parameter range used elsewhere in this cluster. The candidate is not
merely living inside a dense MR neighborhood; it *is* a repeated
factor-set member of that neighborhood. Worksheet Section D notes that the
exact DSL is not identical across repeats because max hold, return target,
and the elevated-volatility threshold differ; but these are
parameter-level tuning differences, not structural rewrites, and I do not
treat parameter tuning on a fully repeated factor set as structural
novelty. The construction is therefore expected to read as a highly
recycled canonical MR template throughout.

**Reconciliation expectation**: SVR >= 0.5 satisfies the
`agreement_expected` rubric; the categorical label prediction is
confirmed. This is an independent candidate-level judgment and should not
be read as implying any monotonic rule across `factor_set_prior_occurrences`
levels, recurrence depth, or later agreement-labeled candidates,
consistent with Lock 8 narrow-claim discipline. The HIGH judgment here is
driven by this candidate's own clean canonical MR structure and its
repeated exact factor-set recurrence, not by any pre-committed rule that
higher prior-occurrence counts must map to higher SVR. C18's HIGH judgment
rests on its own structural facts: exact 7-factor recurrence against four
priors, maximal selector overlap at 7, fully canonical MR factor
vocabulary with no hybrid load, a coherent and contradiction-free DSL with
no plausibility-clipping issues, and entry conditions firmly inside the
cluster's standard oversold-bounce parameter range.

**One-sentence core judgment**: A clean, textbook, fully canonical
7-factor oversold-bounce mean-reversion repeat — exact factor-set
recurrence against four priors and maximal overlap dominate; the remaining
differences are parameter-level tuning, not structural novelty; theme,
plausibility, and SVR all land cleanly at HIGH.

### Candidate 19 — Position 152, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.
Not a Stage 2b overlap candidate. Framed as a **label-replication** case:
the question is whether D7b's semantic SVR judgment supports the
selector's `agreement_expected` label on a heavily repeated MR-cluster
member that carries a more visible entry-grammar adjustment than the
cleanest canonical repeats.

**Structural assessment**: Position 152 is an **oversold-bounce
mean-reversion candidate with a crossing-style entry trigger and a
low-volatility stabilization filter**. The 7-factor set (`bb_upper_24_2`,
`close`, `realized_vol_24h`, `return_24h`, `rsi_14`, `sma_24`,
`zscore_48`) is an **exact 7-factor repeat of positions 17, 27, 102, 112,
and 147**, giving `factor_set_prior_occurrences = 5` — the highest
prior-occurrence count observed up to this point in firing order — and
`max_overlap_with_priors = 7`, matching the maximal-overlap level. Entry
requires `close crosses_below bb_upper_24_2`, `rsi_14 < 35`,
`realized_vol_24h < 0.025`, and `zscore_48 < -1.5`. Exit path A is
`close crosses_above sma_24` with RSI recovery; exit path B is
`return_24h > 0.02`. Max hold is 120 bars. Position bucket is `late`.

**Plausibility expectation**: MODERATE-HIGH. The trade story is readable
end-to-end: `rsi_14 < 35` and `zscore_48 < -1.5` jointly describe a
meaningfully oversold market, `realized_vol_24h < 0.025` indicates that
the setup is not a panic-driven rebound attempt but rather a recovery in a
more stabilized regime, and the exit logic is textbook (mean recovery via
SMA crossover plus RSI normalization, or realized-return profit capture).
The mild discount from HIGH comes from the `close crosses_below
bb_upper_24_2` entry grammar — the condition is logically compatible with
the oversold body (price having dropped from above the band into below it
can coexist with a weak market state), but the crossing-style trigger
reads slightly awkwardly relative to cleaner static-threshold framings.
The awkwardness is not inference-dependent and the intended story is fully
readable, so plausibility takes only a small clip rather than the heavier
penalties applied where the DSL was literally inconsistent.

**Alignment expectation**: HIGH. The factor set is the complete canonical
mean-reversion vocabulary — BB, zscore, RSI, SMA, volatility, and return
all serve the same deviation-to-reversion theme. Worksheet Section C
explicitly notes that the volatility-contraction filter "fits the
stabilization story in the description," which confirms it operates as a
market-state regime filter rather than as a theme-shifting hybrid
component. There is no momentum, breakout, or trend-following
contamination anywhere in the construction; the strategy reads cleanly as
mean reversion throughout, and the low-volatility framing only specifies
what kind of oversold condition the bounce is being looked for in.

**SVR expectation**: MODERATE-HIGH. The recurrence signal is at the
batch's highest level so far: `factor_set_prior_occurrences = 5` is the
maximum observed up to this point in firing order, and
`max_overlap_with_priors = 7` matches the maximal level — this candidate
is firmly inside the densely populated 7-factor MR cluster. Worksheet
Section D notes two LOW reasons: the crossing-style entry and the
volatility-contraction filter. These two reasons carry asymmetric weight
in the SVR judgment. The volatility-contraction filter is a regime-flavor
choice on a familiar template — Section C itself confirms it fits the
stabilization story — and does not by itself constitute structural
novelty. Against the backdrop of this heavily repeated 7-factor MR
cluster, the use of `crosses_below bb_upper_24_2` reads as a more visible
entry-grammar adjustment than a pure parameter or threshold tweak. The
candidate therefore does not read as the cleanest canonical repeat of the
cluster's template; it reads as a member of the same cluster carrying a
real entry-grammar variant. SVR lifts above the 0.5 threshold comfortably
on the strength of recurrence, but lands a step below the cleanly recycled
HIGH cluster on the strength of the entry-grammar shift.

**Reconciliation expectation**: SVR >= 0.5 satisfies the
`agreement_expected` rubric; the categorical label prediction is
confirmed. This is an independent candidate-level judgment and should not
be read as implying any monotonic rule across `factor_set_prior_occurrences`
levels, recurrence depth, or later agreement-labeled candidates,
consistent with Lock 8 narrow-claim discipline. The MODERATE-HIGH judgment
here is driven by this candidate's own structural facts — exact 7-factor
recurrence against five priors, maximal selector overlap at 7, fully
canonical MR factor vocabulary, and a more visible entry-grammar adjustment
that distinguishes it from the cleanest canonical repeats — and not by any
pre-committed rule mapping prior-occurrence counts to SVR levels.

**One-sentence core judgment**: A heavily repeated 7-factor MR cluster
member whose crossing-style entry grammar lifts it out of the
cleanest-canonical-repeat tier without removing it from the cluster —
theme stays textbook MR, plausibility takes a small awkwardness clip, and
SVR lands at MODERATE-HIGH on the strength of recurrence balanced against
a real entry-grammar variant.

### Candidate 20 — Position 162, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.
Not a Stage 2b overlap candidate. Framed as a **label-replication** case:
the question is whether D7b's semantic SVR judgment supports the
selector's `agreement_expected` label on the most heavily repeated
MR-cluster member in the batch, written as a quieter, faster-repair
variant profile.

**Structural assessment**: Position 162 is an **oversold-bounce
mean-reversion candidate in a subdued-volatility regime with a shorter
holding profile**. The 7-factor set (`bb_upper_24_2`, `close`,
`realized_vol_24h`, `return_24h`, `rsi_14`, `sma_24`, `zscore_48`) is an
**exact 7-factor repeat of positions 17, 27, 102, 112, 147, and 152**,
giving `factor_set_prior_occurrences = 6` — the maximum prior-occurrence
count observed in the batch — and `max_overlap_with_priors = 7`, matching
the maximal-overlap level. Entry requires `close < bb_upper_24_2`,
`zscore_48 < -1.5`, `rsi_14 < 35`, and `realized_vol_24h < 0.025`. Exit
path A is `close crosses_above sma_24` with RSI recovery; exit path B is
`return_24h > 0.03`. Max hold is 96 bars — the shortest among late
exact-set repeats. Position bucket is `late`.

**Plausibility expectation**: HIGH. The trade story is fully readable and
internally coherent. `zscore_48 < -1.5` and `rsi_14 < 35` jointly describe
a meaningfully oversold market state, and `realized_vol_24h < 0.025`
specifies that the setup is being looked for in a calmer regime rather
than in a panic-driven crash. The exit logic is textbook: either price
recovers to the moving average and RSI normalizes, or the 24-hour return
reaches a profit target and the trade captures the realized gain. There is
no DSL-level inconsistency anywhere in the construction, no grammar
conflict, and no mismatch between entry conditions and the exit path. The
subdued-volatility framing is not awkward — it simply specifies the regime
where the strategy expects a stabilized oversold repair rather than the
most turbulent rebound window.

**Alignment expectation**: HIGH. The factor set is the complete canonical
mean-reversion vocabulary: BB, zscore, RSI, SMA, return, and volatility
all serve the same deviation-to-reversion theme. `realized_vol_24h <
0.025` operates as a market-state filter specifying the kind of
environment in which this MR setup is expected to work, not as a
theme-shifting hybrid component. There is no momentum, breakout, or
trend-following contamination anywhere in the candidate; the strategy
reads cleanly as mean reversion from entry to exit.

**SVR expectation**: MODERATE-HIGH. The recurrence signal is the strongest
in the batch: `factor_set_prior_occurrences = 6` is the maximum observed,
`max_overlap_with_priors = 7` matches the maximal level, and the candidate
has exact 7-factor recurrence against six priors. It is therefore firmly
inside the densely populated canonical MR cluster and is not a new
structure. Worksheet Section D notes two LOW reasons: the shortest max
hold among late exact-set repeats, and the subdued-volatility filter.
Taken individually, each of these is a parameter-level adjustment — a
shorter hold window, a different volatility direction — and would not by
itself constitute structural novelty. Taken together, however, they
combine into a readable operational identity: the candidate is not written
as the cleanest canonical repeat of the cluster's template, but as a
**quieter, faster-repair variant profile** — shorter holds looking for a
stabilized oversold repair under subdued volatility, rather than the
stressed-rebound version of the same oversold-bounce skeleton. Any novelty
here is not at the factor-set or grammar level, but at the
operational-identity level created by the combined parameter choices. SVR
therefore lifts comfortably above the 0.5 threshold on the strength of
maximal recurrence, but lands a step below the cleanest canonical repeats
on the strength of a real variant identity.

**Reconciliation expectation**: SVR >= 0.5 satisfies the
`agreement_expected` rubric; the categorical label prediction is
confirmed. This is an independent candidate-level judgment and should not
be read as implying any monotonic rule across `factor_set_prior_occurrences`
levels, recurrence depth, or later agreement-labeled candidates,
consistent with Lock 8 narrow-claim discipline. The MODERATE-HIGH judgment
here is driven by this candidate's own structural facts — exact 7-factor
recurrence against six priors, maximal selector overlap at 7, fully
canonical MR factor vocabulary, and a readable variant identity emerging
from the combination of subdued-volatility framing and shorter holding
profile — and not by any pre-committed rule mapping prior-occurrence
counts to SVR levels.

**One-sentence core judgment**: The most heavily repeated canonical
7-factor MR cluster member in the batch, written as a quieter,
faster-repair variant rather than as the cleanest standard repeat — theme
stays textbook MR, plausibility stays HIGH, and SVR lands at MODERATE-HIGH
on recurrence balanced against a real operational variant identity.
