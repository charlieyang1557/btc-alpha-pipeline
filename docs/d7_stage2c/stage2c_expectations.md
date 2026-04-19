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
empirical `structural_variant_risk` distribution is predicted to have no
significant skew toward either side of 0.5. Concretely: the median
`structural_variant_risk` across the 9 neutral candidates is predicted to
fall inside the interval `[0.35, 0.65]`, and at least 2 of the 9 scores
are predicted to fall below 0.5 while at least 2 are predicted to fall
at or above 0.5. If the observed neutral-group median falls outside
`[0.35, 0.65]`, or if fewer than 2 scores straddle either side of the
threshold, the pre-registered aggregate claim is considered **falsified**
and the replication verdict is downgraded accordingly.

This aggregate prediction is intentionally wide to avoid overfitting to
Stage 2b's single neutral data point. The purpose is to falsify the null
hypothesis ("Sonnet systematically pushes all neutral candidates in one
direction"), not to pin down a tight posterior.

## Per-Candidate Expectations

### Candidate 1 — Position 17, mean_reversion, divergence_expected
Pre-registered label: `divergence_expected`. Predicted
`structural_variant_risk` < 0.5. Overlaps Stage 2b position 17
(test-retest reconciliation performed in sign-off — see scope lock §Lock 10a).

### Candidate 2 — Position 22, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.
Contributes to neutral-group aggregate prediction.

### Candidate 3 — Position 27, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.

### Candidate 4 — Position 32, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.

### Candidate 5 — Position 62, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.

### Candidate 6 — Position 72, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.

### Candidate 7 — Position 73, volatility_regime, divergence_expected
Pre-registered label: `divergence_expected`. Predicted
`structural_variant_risk` < 0.5. Overlaps Stage 2b position 73 —
test-retest reconciliation required.

### Candidate 8 — Position 74, volume_divergence, divergence_expected
Pre-registered label: `divergence_expected`. Predicted
`structural_variant_risk` < 0.5. Overlaps Stage 2b position 74 —
test-retest reconciliation required. This is the only `volume_divergence`
theme candidate in the selection.

### Candidate 9 — Position 77, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.

### Candidate 10 — Position 83, volatility_regime, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.

### Candidate 11 — Position 97, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5. Overlaps Stage 2b position 97 —
test-retest reconciliation required.

### Candidate 12 — Position 102, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.

### Candidate 13 — Position 107, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.

### Candidate 14 — Position 112, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.

### Candidate 15 — Position 117, mean_reversion, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.

### Candidate 16 — Position 138, volatility_regime, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.
Overlaps Stage 2b position 138 — test-retest reconciliation in sign-off.

### Candidate 17 — Position 143, volatility_regime, neutral
Pre-registered label: `neutral`. No per-candidate polarity prediction.

### Candidate 18 — Position 147, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.

### Candidate 19 — Position 152, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.

### Candidate 20 — Position 162, mean_reversion, agreement_expected
Pre-registered label: `agreement_expected`. Predicted
`structural_variant_risk` >= 0.5.
