# D7 Stage 2d — Pre-Registered Expectations (DRAFT)

This file is the Stage 2d aggregate pre-registration anchor. All numeric
commitments below are locked at this file's commit hash. Any modification
after that hash constitutes an E1 re-open requiring new rationale and
reviewer triangulation, not a prose edit.

## Frozen Pre-Registration Anchors

| ID | Axis / Section | Claim (short form) | Denominator | Source |
|----|----------------|--------------------|-------------|--------|
| TBD-A1 | §6.2.1 Agreement (UB) | ≥ 52 at SVR ≥ 0.5 | UB agreement, n=66 | Stage 2b+2c 9/9 anchor |
| TBD-A2 | §6.2.2 Divergence (UB) | ≥ 4 at SVR ≥ 0.5 (contradiction) | UB divergence, n=5 | Stage 2b+2c 6/6 high-SVR contradictions |
| TBD-DIST (a) | §6.3 upper tail | ≥ 90 at SVR ≥ 0.80 | UB full, n=199 | Stage 2c 15/20 at ≥0.80 |
| TBD-DIST (b) | §6.3 lower tail | ≥ 30 at SVR ≤ 0.30 | UB full, n=199 | structural (neutral share) |
| Lock 6.4 | §6.4 Fresh-7 RSI-absent vol_regime | ≥ 2 of 7 at SVR < 0.5 | fresh-7 subset, n=7 | pos 138/143 Stage 2c anchor |

These five values constitute Stage 2d's complete pre-registered numeric
commitments. Any modification after this file's commit hash is created
constitutes an E1 re-open requiring new rationale and reviewer
triangulation, not a prose edit. All subsequent sections treat these
values as read-only.

## Label Universes

- **Universe A (UA):** n=29. Eligible-pool subset where
  `universe_a_label` is non-null. Composition: agreement 11,
  divergence 3, neutral 15.
- **Universe B (UB):** n=199. Full replay-eligible set; every call
  carries `universe_b_label`. Composition: agreement 66, divergence 5,
  neutral 128.

Both universes are anchored in
`docs/d7_stage2d/label_universe_analysis.json`
(SHA256: `ecd52a9e7656d31d13a8e62ec11a7345f8966343172fbfc3f95add2762b3e4a0`;
scope lock commit: `4303d8de2882362ec55c8c581519331c5f6404c6`).

Universe A preserves the Stage 2b/2c eligible-pool frame, while
Universe B applies the Stage 2d derivation across the full
replay-eligible set. Both universes are produced by
`derive_d7_stage2d_label_universes.py` under a single
`label_relationship_rule`; the differing outputs (e.g. UA divergence
positions {17, 73, 74} appearing as `neutral_expected` in UB) arise
from rule inputs that depend on eligibility context, not from a
different rule. The resulting labels are not interchangeable across
universes.

**Mixing rule (MANDATORY):** No claim may aggregate a numerator across
UA and UB, or use a denominator that pools both universes. Denominator
is stated in every §6.* header.

## §6.1 — Aggregate Expectations Across All 199 D7b Calls

All aggregate denominators in this section and §§6.2–6.5 below refer
to the 199 replay-eligible positions as defined in
`label_universe_analysis.json`. Position 116 is the single non-call
position (per Lock 1.5) and does not enter any aggregate count.

## §6.2 — Axis-Specific Label Claims

**Operationalization (Scope Lock v2 Lock 6.2.1 / 6.2.2 verbatim):** all
§6.2 claims use **SVR-only**. Alignment scores are recorded as
observation axes in §6.6 and are not part of §6.2 pass/fail.

### §6.2.1 Agreement Axis — TBD-A1

- **Claim:** Of the 66 UB agreement-labelled calls, **≥ 52 have SVR ≥ 0.5**.
- **Rationale:** Stage 2c observed 8/8 agreement-axis passes and
  Stage 2b observed 1/1 (pos 97), for a combined 9/9 historical anchor
  at SVR ≥ 0.5. A 21-point discount (66 − 52 ≈ 21%) budgets for
  universe expansion variance and non-IID themes.
- **Operational definition:** pass =
  `count(call.svr >= 0.5) over {call.universe_b_label == "agreement_expected"} >= 52`.

### §6.2.2 Divergence Axis — TBD-A2

- **Claim:** Of the 5 UB divergence-labelled calls, **≥ 4 contradict
  the divergence_expected label with SVR ≥ 0.5**.
- **Rationale:** Anchored to the Stage 2b+2c combined 6/6 high-SVR
  contradiction rate across 3 distinct divergence positions observed
  in 2 runs each: pos 17 (0.85, 0.85), pos 73 (0.85, 0.95), and pos 74
  (0.65, 0.75). UB divergence universe expands to 5 positions; 4/5
  allows one-position slippage on the expansion.
- **Operational definition:** pass =
  `count(call.svr >= 0.5) over {call.universe_b_label == "divergence_expected"} >= 4`.

Per-candidate sign-off adjudication under Lock 13.2 is performed
separately and does not alter the aggregate machine-adjudicated rule
defined here.

### §6.2.3 SVR vs Alignment Clarification

SVR is the only §6.2 axis. Alignment is observed per-call and
aggregated in §6.6; any §6.2.* claim evaluated on alignment is a
scope-lock deviation.

## §6.3 — SVR Distribution-Shape Claim (TBD-DIST)

- **Claim (a):** Of all 199 UB calls, **≥ 90 have SVR ≥ 0.80** (upper tail).
- **Claim (b):** Of all 199 UB calls, **≥ 30 have SVR ≤ 0.30** (lower tail).
- **Rationale — upper tail.** Stage 2c's 75% upper-tail rate (15/20 at
  SVR ≥ 0.80) would imply roughly 149 of 199 under naive transport.
  Stage 2d instead pre-registers 90 as a conservative floor to
  accommodate full-batch dilution.
- **Rationale — lower tail.** Universe B has 128/199 neutral-labeled,
  materially higher than Stage 2c's neutral share, so structurally a
  larger low-SVR mass is expected. The ≥30/199 lower bound is
  conservative relative to this structural expectation and remains
  falsifiable.
- **Operational definition:** two independent counts over the 199-call
  set; both (a) and (b) must pass for §6.3 as a whole to pass.

## §6.4 — Fresh-7 RSI-Absent vol_regime Structured Claim

- **Claim:** Of the 7 fresh replay positions in the pre-registered
  fresh-7 subset, **≥ 2 have SVR < 0.5**.
- **Rationale:** Stage 2c positions 138 (SVR 0.30) and 143 (SVR 0.15)
  are both empirically RSI-absent + vol_regime-present (confirmed via
  factor-set inspection of
  `raw_payloads/batch_5cf76668/critic/call_0138_prompt.txt` and
  `call_0143_prompt.txt`). Both land well below 0.5, supporting the
  lower-SVR framing of this stratum and grounding the ≥2/7 threshold
  as a continuation anchor rather than an extrapolation.
- **Edge case — position 188.** Position 188 is the only fresh-7
  member with `factor_set_prior_occurrences ≥ 1` (specifically 1
  prior). Its Universe B label is `agreement_expected`, and the
  prior-occurrence signal is expected to push its D7b SVR upward —
  analogous to Stage 2b/2c position 73 (RSI-absent vol_regime, prior
  occurrence, SVR 0.85). Position 188 remains in the fresh-7
  denominator; falsifiability of the ≥2/7 claim is carried by the
  other 6 fresh-7 members.
- **Operational definition:** the fresh-7 subset is the hard-coded
  seven-position set `{3, 43, 68, 128, 173, 188, 198}`, established in
  the Stage 2d selection artifacts and including both deep-dive
  members and the two replay-only members (pos 3, pos 43). Self-check
  MUST NOT re-derive this set at runtime from
  `deep_dive_candidates.json` or from `factor_set` parsing. Pass =
  `count(svr < 0.5) over fresh-7 subset >= 2`.

## §6.5 — Theme-Stratified Sub-Claims

Declined. No §6.5 sub-claim is pre-registered. Theme breakdown is
recorded as an observation axis (§6.6) and may be used for post-fire
forensic analysis but carries no pre-registered numerical bound.
Stage 2c 20-call set was not theme-stratified, so any numerical
threshold would be extrapolation beyond the empirical anchor available
at commit time.

## §6.6 — Plausibility / Alignment Observation Axes

Recorded, not pre-registered:

1. **Alignment distribution** — mean, quartiles, and range summaries
   across 199 calls; per-axis (agreement/divergence/neutral) within UB.
2. **SVR–alignment decoupling** — count of calls where
   `svr >= 0.75 AND alignment <= 0.50` and inverse. Stage 2c anchor:
   pos 102 (SVR 0.95 / aln 0.40) is the sole Stage 2c decouple; no
   pre-registered count.
3. **Theme × label contingency** — 6 themes × 3 labels = 18-cell count
   table; read-out only.
4. **Plausibility score distribution** — parallel to (1) for
   plausibility axis.

§6.6 read-outs enter the post-fire acceptance notebook; they do not
gate Stage 2d pass/fail.

## §E3 — Multi-Tier Test-Retest Grid

### Baseline Anchor

Baselines sourced from `docs/d7_stage2d/test_retest_baselines.json`
(SHA256: `5840b90a57206b01e8109ea73b549cf50089964f5cb1f9f7e83b963569adac2f`;
scope lock commit: `4303d8de2882362ec55c8c581519331c5f6404c6`).
Baselines are frozen; any revision requires an E1 re-open.

### Bucket Rubric

Categorical labels inherit Stage 2c sign-off definitions
(`docs/closeout/PHASE2B_D7_STAGE2C_SIGNOFF.md` §6):

- `LOW`: SVR < 0.25
- `MODERATE-LOW`: 0.25 ≤ SVR < 0.50
- `MEDIUM`: middle category, used only where explicitly assigned in a
  row-level expectation; not a default bucket
- `MODERATE-HIGH`: high-side but not peak (empirically 0.70–0.80 in
  Stage 2c data)
- `HIGH`: SVR ≥ 0.85

### Universal Rubric Rules

1. **Bucket preservation** is the primary per-candidate pass/fail gate.
2. **Adjacent-bucket latitude.** Where a row lists two adjacent
   admissible buckets (e.g. `MODERATE-HIGH or HIGH`), landing in either
   bucket counts as bucket preservation for that candidate.
   Non-adjacent admissible buckets are not permitted in §E3.
3. **Threshold-side preservation** (SVR stays on the same side of 0.5
   as baseline runs) is a separate per-candidate binary gate.
4. **Drift magnitude tolerance** is pre-registered at `±0.20` uniformly
   (Stage 2c Tier-1 observed max drift +0.15; +0.05 expansion for
   universe-expansion variance).
   - Drift magnitude is a **readout**, not a gate.
   - Bucket preservation is **the gate**.
   - Threshold-side preservation is a **separate binary gate**.
5. **Drift direction** (up / down / stable) is observed-only. Per
   Lock 3.5, no directional drift sign is pre-registered for any
   candidate unless supported by BOTH Stage 2b and Stage 2c baselines
   showing a consistent magnitude-and-direction pattern. No Tier 1
   candidate satisfies this (see §Tier 1 audit); Tier 2 cannot satisfy
   it by construction.
6. **Axis-specific stability.** SVR, plausibility, alignment tracked
   independently in post-fire readout; §E3 pre-registers SVR bucket
   only.

### Tier 1 — Three-run candidates (n=5)

Stage 2b → Stage 2c → Stage 2d.

| Pos | UA label | 2b SVR | 2c SVR | Expected 2d bucket | Threshold-side preserve | Drift tol | Notes |
|-----|----------|-------:|-------:|--------------------|-------------------------|-----------|-------|
| 17 | divergence_expected | 0.85 | 0.85 | HIGH | Y | ±0.20 | High-SVR contradiction of divergence_expected; flat across 2b→2c (+0.00). |
| 73 | divergence_expected | 0.85 | 0.95 | HIGH | Y | ±0.20 | High-SVR divergence contradiction; +0.10 drift 2b→2c. |
| 74 | divergence_expected | 0.65 | 0.75 | MODERATE-HIGH or HIGH | Y | ±0.20 | Volume-divergence contradiction; +0.10 drift 2b→2c. Adjacent-bucket latitude applied. |
| 97 | agreement_expected | 0.95 | 0.95 | HIGH | Y | ±0.20 | Peak-stable agreement overlap; flat 2b→2c. |
| 138 | neutral | 0.15 | 0.30 | LOW or MODERATE-LOW | Y (below 0.5) | ±0.20 | Per Lock 3.1 no polarity claim — absolute SVR stability only. +0.15 drift 2b→2c. RSI-absent vol_regime anchor for §6.4. Adjacent-bucket latitude applied. |

**Tier 1 bidirectional-drift audit (Lock 3.5):** Of the five Tier 1
candidates, four show flat or single-step drift; pos 138 shows the
only non-trivial magnitude (+0.15), and its RSI-absent vol_regime
membership is handled as a stratum-level claim in §6.4 rather than as
a per-candidate directional drift claim. No Tier 1 candidate carries a
pre-registered drift-sign claim in §E3.

### Tier 2 — Two-run candidates (n=15)

Stage 2c → Stage 2d. Lock 3.5 precludes any directional drift claim
(only one prior run).

| Pos | UA label | 2c SVR | Expected 2d bucket | Threshold-side preserve | Drift tol | Notes |
|-----|----------|-------:|--------------------|-------------------------|-----------|-------|
| 22 | neutral | 0.85 | HIGH | Y | ±0.20 | Short-horizon MR near-repeat. |
| 27 | agreement_expected | 0.85 | HIGH | Y | ±0.20 | Agreement axis anchor. |
| 32 | neutral | 0.90 | HIGH | Y | ±0.20 | DSL awkwardness dampened plausibility in 2c; SVR unaffected. |
| 62 | neutral | 0.95 | HIGH | Y | ±0.20 | Horizon-mix MR variant; peak-SVR in 2c. |
| 72 | neutral | 0.75 | MODERATE-HIGH or HIGH | Y | ±0.20 | Adjacent-bucket latitude applied. |
| 77 | neutral | 0.95 | HIGH | Y | ±0.20 | Low-plausibility / high-SVR case in 2c. |
| 83 | neutral | 0.75 | MODERATE-HIGH or HIGH | Y | ±0.20 | Hybrid vol_regime case. Adjacent-bucket latitude applied. |
| 102 | agreement_expected | 0.95 | HIGH | Y | ±0.20 | SVR–alignment decouple in 2c (aln 0.40 / SVR 0.95); §6.6 observation axis, no §E3 gate. |
| 107 | agreement_expected | 0.95 | HIGH | Y | ±0.20 | Agreement axis anchor. |
| 112 | agreement_expected | 0.85 | HIGH | Y | ±0.20 | Agreement axis anchor. |
| 117 | neutral | 0.85 | HIGH | Y | ±0.20 | MACD exit novelty in 2c; SVR held high-side. |
| 143 | neutral | 0.15 | LOW | Y (below 0.5) | ±0.20 | RSI-absent vol_regime anchor for §6.4; Stage 2c biggest deviation vs prior-run prediction. Absolute SVR stability only. |
| 147 | agreement_expected | 0.95 | HIGH | Y | ±0.20 | Agreement axis anchor. |
| 152 | agreement_expected | 0.95 | HIGH | Y | ±0.20 | Entry-grammar variant; peak-SVR in 2c. |
| 162 | agreement_expected | 0.90 | HIGH | Y | ±0.20 | Quieter faster-repair variant. |

### §E3 Aggregate Readout (not pre-registered as a numeric gate)

Post-fire sign-off will report the number of candidates that preserve
(i) their pre-registered SVR bucket and (ii) their threshold side
relative to 0.5. These counts are descriptive summaries of the
per-candidate rubric outcomes in this section, not separate aggregate
commitments.

Lock 3.5 audit: No pre-registered directional drift claims exist in
§E3; post-fire readout reports observed directions only.

### Delta vs Scope Lock

| Lock ref | Content in §E3 | Status |
|----------|----------------|--------|
| Lock 3.1 | Tier 1 n=5 position set; pos 138 no-polarity carve-out | Honored |
| Lock 3.2 | Tier 2 n=15 position set | Honored |
| Lock 3.4 | 5 evaluation axes | Bucket + threshold pre-registered; drift magnitude as readout; drift direction observed-only; axis-specific stability deferred to post-fire notebook |
| Lock 3.5 | Bidirectional drift rule | Explicit audit; no directional claims |
| Lock 3.6 | No Tier 2.5 | n/a (not invoked) |
| Lock 11.4 | Per-candidate rubric | Row-level structured rubric is present for each candidate, consistent with Lock 11.4 |
| Aggregate pass/fail thresholds | DEFERRED per ruling | Recorded as readout only; no numeric commitment |

### Known Pre-Fire §E3 Defects (Path A documented)

Two §E3 rubric defects were identified pre-fire and retained
under Path A (document-and-adjudicate) rather than re-drafting
the sealed §E3 block. They are recorded here for audit-trail
completeness and for explicit sign-off handling.

**Issue B — MEDIUM gap in `[0.50, 0.70)`.** The sealed §E3
bucket rubric uses `LOW: SVR < 0.25`,
`MODERATE-LOW: 0.25 ≤ SVR < 0.50`,
`MODERATE-HIGH: high-side but not peak (empirically 0.70–0.80
in Stage 2c data)`, and `HIGH: SVR ≥ 0.85`; `MEDIUM` is used
only where explicitly assigned and is not a default bucket. The
interval `[0.50, 0.70)` has no default bucket assignment. No §E3
candidate is pre-registered with a `MEDIUM` bucket. If a
post-fire §E3 outcome lands in `[0.50, 0.70)`, that result is
flagged for per-candidate sign-off adjudication rather than
treated as a self-check failure.

**Issue D — adjacent-bucket disjunctions on pos 72, 74, 83, 138.**
These four candidates retain `OR`-bucket phrasing in the sealed
§E3 rubric (pos 72, 74, 83 as `MODERATE-HIGH or HIGH`; pos 138
as `LOW or MODERATE-LOW`). Sign-off applies adjacent-bucket
latitude per §E3 Universal Rubric Rule #2: the bucket gate
passes if the observed SVR lands in either named bucket.
Non-adjacent disjunctions are not authorized.

**Path A rationale.** Path A (document-and-adjudicate) was
adopted at §E3 authoring time; a re-draft round (Path B) was
judged not worth the cost given that defects are bounded to §E3
row-level grids and do not propagate to §E4, where single-bucket
discipline was enforced throughout.

**Audit trail.** Defects identified on 2026-04-19 during §E3
drafting; Path A selected the same day and ratified by both
advisors. No scope-lock amendment was made; the defects are
instead carried forward as documented contingencies in this
file.

## §E4 — Deep-Dive Per-Candidate Expectations (n=20)

§E4 is a net-new section within this expectations document (no
in-document delta baseline). Twenty positions drafted as fixed-skeleton
deep dives per Lock 11.3. Format template locked at Batch 1 and held
for Batches 2–4 without explicit delta audit. UA metadata line appears
only on fresh-9 pool `{122, 127, 128, 129, 132, 172, 178, 182, 187}`;
remaining eleven omit it.

### Position 1 — momentum_rsi_oversold_reversal

1. **Structural assessment.** Factor set `{rsi_14, return_24h}`.
   Grammar: oversold threshold (`rsi_14 < 30`) AND positive 24h return
   entry; overbought exit (`rsi_14 > 70`). Selector-label:
   momentum-reversal.
2. **Plausibility expectation.** HIGH — textbook oversold-reversal
   construction, economically coherent.
3. **Alignment expectation.** HIGH — description maps directly onto
   DSL clauses.
4. **SVR expectation.** HIGH.
5. **Reconciliation expectation.** UB label `divergence_expected`; a
   HIGH SVR contradicts the UB label at SVR ≥ 0.5 and feeds §6.2.2
   TBD-A2's ≥ 4/5 contradiction count. No grammar or alignment defect
   visible; the two-factor oversold construction is internally
   consistent end-to-end.
6. **Core judgment.** Expect a strong positive critic read driven by
   clean oversold-reversal logic and close prose/DSL alignment.

### Position 2 — bb_mean_reversion_zscore

1. **Structural assessment.** Factor set
   `{close, bb_upper_24_2, zscore_48, return_24h, sma_24}`. Grammar:
   three-condition AND entry with two OR exits. Selector-label:
   Bollinger/zscore mean-reversion.
2. **Plausibility expectation.** MODERATE-HIGH — sound mean-reversion
   mechanism; the entry gate `close < bb_upper_24_2` is weakly
   selective relative to the stated lower-band narrative, so the
   binding constraint is `zscore_48 < -1.5`.
3. **Alignment expectation.** MODERATE — description says "below lower
   Bollinger band" but DSL checks `bb_upper`; a real prose/DSL
   mismatch.
4. **SVR expectation.** MODERATE-HIGH.
5. **Reconciliation expectation.** UB label `divergence_expected`;
   MODERATE-HIGH SVR (≥ 0.5) contradicts the UB label and feeds §6.2.2
   TBD-A2's ≥ 4/5 count. Below-peak bucket reflects the Bollinger-band
   wording mismatch depressing alignment, not a grammar failure.
6. **Core judgment.** Conceptually sound, but the Bollinger-band
   wording mismatch is likely the main source of SVR drag.

### Position 5 — weekend_mean_reversion

1. **Structural assessment.** Factor set
   `{day_of_week, zscore_48, rsi_14}`. Grammar: calendar-gate AND
   mean-reversion confirmation; exit on weekday return or zscore
   normalization. Selector-label: weekend mean-reversion.
2. **Plausibility expectation.** MODERATE — the mean-reversion logic
   is coherent, but the weekend gate is a weaker structural prior than
   the price-based conditions.
3. **Alignment expectation.** HIGH — description and DSL match
   cleanly.
4. **SVR expectation.** MODERATE-HIGH.
5. **Reconciliation expectation.** UB label `divergence_expected`;
   MODERATE-HIGH SVR (≥ 0.5) feeds §6.2.2 TBD-A2's ≥ 4/5 count.
   Below-peak bucket reflects weaker-prior weight on the calendar gate
   rather than a DSL defect.
6. **Core judgment.** Expect a clean but not fully compelling
   candidate whose score depends more on the credibility of the
   calendar gate than on DSL quality.

### Position 6 — macd_crossover_momentum

1. **Structural assessment.** Factor set
   `{macd_hist, rsi_14, close, sma_20}`. Grammar: MACD-histogram
   crossover entry with RSI floor and SMA trend filter; dual OR exit
   on reverse crossover or RSI collapse. Selector-label: MACD
   crossover momentum.
2. **Plausibility expectation.** HIGH — canonical momentum
   construction with standard confirmation stack.
3. **Alignment expectation.** HIGH — description ("crosses above zero
   signaling momentum shift") matches DSL semantics.
4. **SVR expectation.** HIGH.
5. **Reconciliation expectation.** UB label `divergence_expected`;
   HIGH SVR contradicts at SVR ≥ 0.5 and feeds §6.2.2 TBD-A2's ≥ 4/5
   count. Downward pressure would most likely come from the
   stacked-confirmation design being judged conventional rather than
   especially novel, not from any visible prose/DSL defect.
6. **Core judgment.** Expect a strong critic endorsement driven by
   canonical momentum structure and clean semantic alignment.

### Position 8 — volatility_regime_breakout

1. **Structural assessment.** Factor set
   `{realized_vol_24h, atr_14, close, bb_upper_24_2, volume_zscore_24h, rsi_14, sma_24}`.
   Grammar: 4-condition AND entry (vol-regime gate + breakout + volume
   + momentum) with 3-condition OR exit. Selector-label: vol-regime
   breakout.
2. **Plausibility expectation.** MODERATE-HIGH — vol-regime + breakout
   composition is mechanically coherent; 4-condition entry is narrow
   but each component is standard.
3. **Alignment expectation.** HIGH — description and DSL correspond.
4. **SVR expectation.** MODERATE-HIGH.
5. **Reconciliation expectation.** UB label `neutral`; candidate does
   not feed §6.2.1 or §6.2.2. Contributes to §6.3 distribution, with
   the key uncertainty being whether a MODERATE-HIGH outcome clears
   the SVR ≥ 0.80 upper-tail threshold, and to §6.6 observation axes.
   The critic may endorse the mechanism while treating the
   four-condition entry stack as overfitting-adjacent, which would cap
   the score below peak HIGH, keeping the candidate within
   MODERATE-HIGH rather than crossing into HIGH.
6. **Core judgment.** Coherent vol-regime breakout whose SVR likely
   lands below peak because of entry-condition density rather than
   mechanism failure.

### Position 13 — vol_regime_breakout

1. **Structural assessment.** Factor set
   `{realized_vol_24h, close, sma_50, rsi_14, volume_zscore_24h, sma_20, return_1h}`.
   Grammar: low-realized-vol entry (`realized_vol_24h < 0.025`) AND
   `sma_50` cross-above + RSI floor + volume confirmation; four OR
   exits (vol expansion, RSI overbought, `sma_20` cross-below, adverse
   short-horizon return). Selector-label: vol-regime breakout. RSI
   presence places this outside the hard-coded fresh-7
   `{3, 43, 68, 128, 173, 188, 198}` despite vol_regime theme match —
   the §6.4 fresh-7 operational criterion is RSI-absent vol_regime.
2. **Plausibility expectation.** MODERATE-HIGH — standard
   vol-compression-then-breakout construction with conventional
   momentum and volume confirmation.
3. **Alignment expectation.** HIGH — description and DSL align.
4. **SVR expectation.** MODERATE-HIGH.
5. **Reconciliation expectation.** UB label `neutral`; candidate does
   not feed §6.2.1 or §6.2.2. Contributes to §6.3 distribution
   (MODERATE-HIGH likely clears middle-distribution mass but outcome
   vs the SVR ≥ 0.80 upper-tail threshold is uncertain) and §6.6
   observation axes.
6. **Core judgment.** Standard vol-regime breakout with no grammar or
   alignment defect; expect a competent critic read landing in the
   MODERATE-HIGH zone.

### Position 68 — low_volatility_regime_breakout

1. **Structural assessment.** Factor set
   `{realized_vol_24h, close, sma_50, macd_hist, return_24h, return_168h}`.
   Grammar: very-low realized vol (`< 0.015`) AND `sma_50` cross-above
   + positive MACD histogram + positive 24h return entry; three OR
   exits (vol expansion, `sma_50` cross-below, 7-day return > 10%).
   Selector-label: low-vol regime breakout. RSI-absent,
   vol_regime-present: satisfies §6.4 fresh-7 hard-coded membership.
2. **Plausibility expectation.** MODERATE — vol-compression pattern
   is coherent, but the `< 0.015` threshold is tighter than typical
   and narrows the entry surface.
3. **Alignment expectation.** HIGH — description and DSL match.
4. **SVR expectation.** MODERATE-LOW.
5. **Reconciliation expectation.** UB label `neutral`; structural
   analog to §6.4 anchors pos 138 (SVR 0.30, MODERATE-LOW) and pos 143
   (SVR 0.15, LOW). MODERATE-LOW is the expected continuation of that
   anchor pattern; added MACD + dual-return grammar places pos 68 in
   MODERATE-LOW rather than the pos 143-style LOW bucket. Contributes
   to §6.4's ≥ 2/7 at SVR < 0.5 count. A MODERATE-or-higher outcome
   creates candidate-level tension with the anchor continuation read
   and removes this candidate from the §6.4 contributor count, but
   does not by itself falsify §6.4 since that claim is aggregate
   (≥ 2/7 across fresh-7). Also feeds §6.3 + §6.6 per UB=neutral.
6. **Core judgment.** Expected §6.4 contributor at MODERATE-LOW;
   anchor-consistent with a grammar-density lift over the pos 143 LOW
   member.

### Position 122 — bb_rsi_mean_reversion_oversold

1. **Structural assessment.** Factor set
   `{close, bb_upper_24_2, rsi_14, zscore_48, sma_24, return_24h}`.
   Grammar: `close crosses_below bb_upper_24_2` AND `rsi_14 < 35` AND
   `zscore_48 < -1.5` entry; three OR exits. Selector-label:
   Bollinger/RSI mean-reversion oversold. Factor-set priors = 3
   (repeated mean-reversion grammar).
2. **Plausibility expectation.** HIGH — standard mean-reversion with
   triple-confirmation (band event + RSI oversold + zscore).
3. **Alignment expectation.** MODERATE-HIGH — description references
   "lower Bollinger band"; DSL uses `crosses_below bb_upper`. The
   transient-event grammar makes the band-event a meaningful price
   action regardless of upper/lower naming, partially mitigating the
   narrative mismatch.
4. **SVR expectation.** MODERATE-HIGH.
5. **Reconciliation expectation.** UB label `agreement_expected`;
   MODERATE-HIGH SVR (≥ 0.5) feeds §6.2.1 TBD-A1's ≥ 52/66 count.
   UA=UB congruence is consistent with the priors=3 repeat-structure
   context. Below-peak bucket reflects the band-naming mismatch
   depressing alignment, not a grammar failure.
6. **Core judgment.** Strong mean-reversion structure with minor
   alignment drag from bb_upper/lower-band wording, partially offset
   by the `crosses_below` transient-event operator.
7. **UA metadata.** `universe_a_label`: `agreement_expected`.

### Position 127 — bollinger_squeeze_mean_reversion

1. **Structural assessment.** Factor set
   `{close, bb_upper_24_2, zscore_48, rsi_14, sma_24, return_24h}`.
   Grammar: `close < bb_upper_24_2` AND `zscore_48 < -1.5` AND
   `rsi_14 < 30` entry; three OR exits. Selector-label: Bollinger
   squeeze mean-reversion. Factor-set priors = 4.
2. **Plausibility expectation.** MODERATE-HIGH — mean-reversion
   construction is sound; `close < bb_upper_24_2` gate is weakly
   selective relative to the stated lower-band narrative, so the
   binding constraints are `zscore_48 < -1.5` and `rsi_14 < 30`.
3. **Alignment expectation.** MODERATE — description says "below the
   lower Bollinger band" but DSL checks `bb_upper` via raw `<` (state
   test, not transient event); direct parallel to pos 2's grammar
   defect.
4. **SVR expectation.** MODERATE-HIGH.
5. **Reconciliation expectation.** UB label `agreement_expected`;
   MODERATE-HIGH SVR (≥ 0.5) feeds §6.2.1 TBD-A1's ≥ 52/66 count.
   UA=UB congruence consistent with the priors=4 repeat-structure
   context. Below-peak bucket reflects the bb_upper wording defect
   depressing alignment — parallel diagnosis to pos 2.
6. **Core judgment.** Sound mean-reversion carrying the same
   alignment defect as pos 2, without the pos 122 mitigating
   `crosses_below` operator.
7. **UA metadata.** `universe_a_label`: `agreement_expected`.

### Position 128 — low_vol_regime_breakout

1. **Structural assessment.** Factor set
   `{realized_vol_24h, close, ema_12, volume_zscore_24h, return_24h}`.
   Grammar: realized vol `< 0.015` AND `close crosses_above ema_12`
   AND volume confirmation entry; three OR exits (vol expansion,
   `ema_12` cross-below, 24h return > 5%). Selector-label: low-vol
   regime breakout. RSI-absent, vol_regime-present: satisfies §6.4
   fresh-7 hard-coded membership.
2. **Plausibility expectation.** MODERATE — vol-compression coherent;
   shares pos 68's tight `< 0.015` entry surface, with simpler
   post-threshold grammar (no MACD, no dual-return) placing this
   closer to the pos 143 anchor in overall structural density.
3. **Alignment expectation.** HIGH — description and DSL correspond.
4. **SVR expectation.** MODERATE-LOW.
5. **Reconciliation expectation.** UB label `neutral`. §6.4 anchors
   pos 138 (SVR 0.30) and pos 143 (SVR 0.15) split MODERATE-LOW/LOW
   at n=2; MODERATE-LOW pre-registers below-0.5 landing without
   over-committing to the LOW tail. Contributes to §6.4's ≥ 2/7
   count. A MODERATE-or-higher outcome creates candidate-level
   tension and removes this candidate from §6.4 contributors but
   does not by itself falsify §6.4 (aggregate claim). Also feeds
   §6.3 + §6.6.
6. **Core judgment.** Expected §6.4 contributor at MODERATE-LOW,
   with the anchor-continuation read outweighing the cleaner entry
   grammar.
7. **UA metadata.** `universe_a_label`: `neutral`.

### Position 129 — volume_divergence_momentum_shift

1. **Structural assessment.** Factor set
   `{volume_zscore_24h, close, ema_26, rsi_14}`. Grammar:
   `volume_zscore_24h crosses_above 1.0` AND `close < ema_26` AND
   `rsi_14 < 40` entry; three OR exits (`ema_26` cross-above,
   `rsi_14 > 70`, `volume_zscore_24h < -0.5`). Selector-label:
   volume-divergence momentum shift.
2. **Plausibility expectation.** MODERATE-LOW — volume-first
   reversal with RSI-oversold and below-EMA filters: three-axis
   narrow selectivity on individually weak priors.
3. **Alignment expectation.** HIGH — DSL narrates what it checks;
   description factors all present in grammar.
4. **SVR expectation.** MODERATE-LOW.
5. **Reconciliation expectation.** UB label `neutral`. A
   MODERATE-LOW outcome places the candidate in the lower-SVR
   region of the §6.3 distribution without pre-registering it
   specifically into the SVR ≤ 0.30 tail. Not fresh-7
   (RSI-present); no §6.4 duty. Also feeds §6.3 + §6.6.
6. **Core judgment.** Structurally plausible narrow volume-driven
   reversal; MODERATE-LOW pre-registers below-median landing
   without deep-LOW commitment.
7. **UA metadata.** `universe_a_label`: `neutral`.

### Position 132 — oversold_bbands_mean_reversion

1. **Structural assessment.** Factor set
   `{close, bb_upper_24_2, rsi_14, realized_vol_24h, sma_24, return_24h}`.
   Grammar: `close crosses_below bb_upper_24_2` AND `rsi_14 < 30`
   AND `realized_vol_24h > 0.02` entry; three OR exits (`sma_24`
   cross-above, `rsi_14 >= 50`, `return_24h > 0.025`).
   Selector-label: oversold bbands mean-reversion. Factor-set
   priors = 2 (repeated mean-reversion grammar).
2. **Plausibility expectation.** MODERATE-HIGH — oversold + vol
   filter stack reinforces mechanism despite the band-naming
   grammar defect.
3. **Alignment expectation.** MODERATE — description says oversold
   lower-band entry but DSL checks `bb_upper` via `crosses_below`;
   same defect family as pos 127, with the transient-event
   operator paralleling pos 122's partial mitigation.
4. **SVR expectation.** MODERATE-HIGH.
5. **Reconciliation expectation.** UB label `agreement_expected`;
   MODERATE-HIGH SVR (≥ 0.5) feeds §6.2.1 TBD-A1's ≥ 52/66 count.
   UA=UB congruence plus priors = 2 reinforces the §6.2.1
   expectation. Same family as pos 122/127; `realized_vol_24h`
   filter is the SVR-bucket differentiator relative to pos 127,
   offsetting the alignment defect at SVR level.
6. **Core judgment.** Member of the `bb_upper`-as-lower-band
   defect cluster with corroborating vol filter; MODERATE-HIGH SVR
   with MODERATE alignment captures the split between mechanism
   strength and prose fidelity.
7. **UA metadata.** `universe_a_label`: `agreement_expected`.

### Position 172 — bollinger_upper_fade_mean_reversion_172

1. **Structural assessment.** Factor set
   `{close, bb_upper_24_2, rsi_14, return_24h, sma_24}`. Grammar:
   `close crosses_below bb_upper_24_2` AND `rsi_14 > 65` AND
   `return_24h > 0.02` entry; three OR exits (`close <= sma_24`,
   `rsi_14 < 55`, `return_24h < -0.03`). Selector-label: bollinger
   upper fade mean-reversion. Unlike pos 2/122/127/132 (`bb_upper`
   narrated as lower band), pos 172's `close crosses_below
   bb_upper_24_2` is load-bearing fade-from-overbought —
   `rsi_14 > 65` plus positive `return_24h` confirm overbought
   entry context; DSL narrates what it checks.
2. **Plausibility expectation.** MODERATE-HIGH — coherent
   three-axis fade construction, internally consistent.
3. **Alignment expectation.** HIGH — no band-naming defect; DSL
   matches description.
4. **SVR expectation.** MODERATE-HIGH.
5. **Reconciliation expectation.** UB label `neutral`;
   MODERATE-HIGH lands in the upper-neutral band of the §6.3
   distribution. Not fresh-7; no §6.4 duty. Also feeds §6.3 + §6.6.
6. **Core judgment.** Load-bearing `bb_upper` fade, distinct from
   defect-cluster pos 2/122/127/132 despite primitive overlap;
   MODERATE-HIGH reflects clean construction at the
   ambiguous-reconciliation margin.
7. **UA metadata.** `universe_a_label`: `neutral`.

### Position 173 — volatility_regime_breakout_173

1. **Structural assessment.** Factor set
   `{realized_vol_24h, close, ema_12, macd_hist, volume_zscore_24h, return_24h}`.
   Grammar: `realized_vol_24h > 0.05` AND `close crosses_above
   ema_12` AND `macd_hist > 0.0` AND `volume_zscore_24h > 1.0`
   entry; three OR exits (`ema_12` cross-below, `macd_hist < 0`,
   `return_24h > 0.06`). Selector-label: high-vol regime breakout.
   RSI-absent, vol_regime-present: satisfies §6.4 fresh-7
   hard-coded membership. HIGH-vol continuation posture is
   structurally distinct from low-vol compression anchors pos
   138/143 and fresh-7 peers pos 68/128.
2. **Plausibility expectation.** MODERATE-HIGH — four-axis
   confirmation chain (vol regime + EMA cross + MACD positivity +
   volume z-score) is internally consistent with no construction
   defect.
3. **Alignment expectation.** HIGH — DSL matches description;
   vol_regime + MACD + volume confirmation narrated and checked.
4. **SVR expectation.** MODERATE-LOW.
5. **Reconciliation expectation.** UB label `neutral`. Fresh-7
   membership brings §6.4 duty — pos 173 contributes to §6.4's
   ≥ 2/7 at SVR < 0.5 count. Anchors pos 138/143 and peers pos
   68/128 are low-vol compression; pos 173 is high-vol breakout,
   so anchor applicability is weaker. MODERATE-LOW pre-registers
   below-0.5 landing on thematic §6.4 continuation grounds despite
   the posture mismatch, with SVR held below plausibility by this
   weaker-anchor calibration rather than by construction defect.
   A MODERATE-or-higher outcome would create candidate-level
   tension with this continuation read and remove pos 173 from
   the expected §6.4 contributor count, but that tension is less
   direct than for the low-vol fresh-7 cases and would not alone
   falsify §6.4. Also feeds §6.3 + §6.6.
6. **Core judgment.** Fresh-7 anchor-continuation with
   pre-registered weaker anchor applicability; MODERATE-LOW
   preserves §6.4 contribution without over-committing on the
   structural posture mismatch.

### Position 178 — vol_contraction_breakout_178

1. **Structural assessment.** Factor set
   `{realized_vol_24h, close, sma_50, atr_14, rsi_14, sma_20, return_168h}`.
   Grammar: `realized_vol_24h < 0.015` AND `close crosses_above
   sma_50` AND `atr_14 < 1200.0` AND `rsi_14 > 45.0` entry; three
   OR exits (`realized_vol_24h > 0.03`, `sma_20` cross-below,
   `return_168h > 0.08`). Selector-label: vol contraction
   breakout. Structural near-identity to pos 68, differing only by
   `rsi_14 > 45.0` filter; RSI-presence excludes fresh-7
   membership.
2. **Plausibility expectation.** MODERATE-LOW — coherent
   compression-breakout construction; `rsi_14 > 45` is a weak
   filter ("not oversold" is not selective).
3. **Alignment expectation.** HIGH — DSL matches description.
4. **SVR expectation.** MODERATE-LOW.
5. **Reconciliation expectation.** UB label `neutral`. A
   MODERATE-LOW outcome places the candidate in the lower-SVR
   region of the §6.3 distribution without pre-registering it
   specifically into the SVR ≤ 0.30 tail. Not fresh-7
   (RSI-present); no §6.4 duty despite thematic vol_regime
   overlap. Also feeds §6.3 + §6.6.
6. **Core judgment.** Low-vol compression breakout with an added
   weak RSI gate; MODERATE-LOW reflects coherent structure without
   the stronger anchor-continuation pressure that applies to
   fresh-7 members.
7. **UA metadata.** `universe_a_label`: `neutral`.

### Position 182 — bollinger_squeeze_reversion_182

1. **Structural assessment.** Factor set
   `{close, bb_upper_24_2, rsi_14, realized_vol_24h, zscore_48, sma_24, return_168h}`.
   Grammar: `close < bb_upper_24_2` AND `rsi_14 < 35.0` AND
   `realized_vol_24h > 0.025` AND `zscore_48 < -1.5` entry; three
   OR exits (`close crosses_above sma_24`, `rsi_14 > 55.0`,
   `return_168h > 0.04`). Selector-label: bb_upper defect cluster,
   elevated-volatility oversold variant (`realized_vol_24h > 0.025`
   gate distinguishes from low-vol pos 187 twin). Fresh-9 pool
   member.
2. **Plausibility expectation.** MODERATE — the oversold mechanism
   is coherent (`rsi_14 < 35` and `zscore_48 < -1.5` co-firing),
   but `close < bb_upper_24_2` is weakly selective relative to the
   stated lower-band narrative; the elevated-vol filter adds one
   meaningful constraint without curing the defect.
3. **Alignment expectation.** MODERATE. DSL assembly is
   syntactically clean but the bb_upper construction defect —
   shared with pos 2/122/127/132/187/197 — creates semantic drift
   between the oversold-breakdown selector label and the actual
   gating surface.
4. **SVR expectation.** MODERATE-LOW.
5. **Reconciliation expectation.** UA label `neutral`, UB label
   `neutral`; a MODERATE-LOW outcome places the candidate in the
   lower-SVR region of the §6.3 distribution without
   pre-registering it specifically into the SVR ≤ 0.30 tail, and
   feeds §6.6's defect-cluster observations. No §6.4 duty (not
   fresh-7). Paired with pos 187 as a vol-regime-direction contrast
   within the defect cluster: same four-axis oversold grammar,
   opposite volatility filter, same defect-driven downward
   pressure.
6. **Core judgment.** bb_upper defect-cluster oversold candidate
   with elevated-vol modifier; defect drags SVR despite clean
   oversold overdetermination.
7. **UA metadata.** `universe_a_label`: `neutral`.

### Position 187 — bollinger_squeeze_reversion_187

1. **Structural assessment.** Factor set
   `{close, bb_upper_24_2, zscore_48, rsi_14, realized_vol_24h, sma_24}`.
   Grammar: `close < bb_upper_24_2` AND `zscore_48 < -1.5` AND
   `rsi_14 < 35.0` AND `realized_vol_24h < 0.02` entry; three OR
   exits (`close crosses_above sma_24`, `rsi_14 > 55.0`,
   `realized_vol_24h > 0.04`). Selector-label: bb_upper defect
   cluster, low-volatility oversold variant
   (`realized_vol_24h < 0.02` gate distinguishes from elevated-vol
   pos 182 twin). Fresh-9 pool member.
2. **Plausibility expectation.** MODERATE — the oversold mechanism
   is coherent, but `close < bb_upper_24_2` is weakly selective
   relative to the stated lower-band narrative; the low-vol filter
   narrows the firing surface more aggressively than the
   elevated-vol variant but does not cure the defect.
3. **Alignment expectation.** MODERATE. DSL clean; defect-driven
   semantic drift identical to pos 182; the `< 0.02` vol gate is
   the sole direction-distinguishing element from its twin.
4. **SVR expectation.** MODERATE-LOW.
5. **Reconciliation expectation.** UA label `neutral`, UB label
   `neutral`; a MODERATE-LOW outcome places the candidate in the
   lower-SVR region of the §6.3 distribution without
   pre-registering it specifically into the SVR ≤ 0.30 tail, and
   feeds §6.6's defect-cluster observations. No §6.4 duty. Paired
   with pos 182 as a vol-regime-direction contrast within the
   defect cluster.
6. **Core judgment.** bb_upper defect-cluster oversold candidate
   with low-vol modifier; pos 182 twin with opposite vol direction,
   same defect-driven bucket.
7. **UA metadata.** `universe_a_label`: `neutral`.

### Position 188 — volatility_breakout_expansion_188

1. **Structural assessment.** Factor set
   `{realized_vol_24h, close, ema_12, volume_zscore_24h, macd_hist, return_24h}`.
   Grammar: `realized_vol_24h > 0.025` AND `close crosses_above
   ema_12` AND `volume_zscore_24h > 1.0` AND `macd_hist > 0.0`
   entry; three OR exits (`realized_vol_24h < 0.015`,
   `macd_hist crosses_below 0.0`, `return_24h < -0.025`).
   Selector-label: volatility-regime breakout with momentum
   confirmation. RSI-absent, vol_regime-present: satisfies §6.4
   fresh-7 hard-coded membership. §6.4 edge-case member:
   prior-occurrence signal aligned with Stage 2b/2c position 73
   (RSI-absent vol_regime, SVR 0.85 analog); priors = 1.
2. **Plausibility expectation.** MODERATE-HIGH — clean four-axis
   breakout grammar: vol-regime gate, price-cross trigger, volume
   confirmation, momentum confirmation. No construction defect;
   each conjunct contributes independent gating signal.
3. **Alignment expectation.** HIGH — DSL matches the
   selector-label cleanly; no defect family; `crosses_above`
   compiles to the two-bar form per compiler rules.
4. **SVR expectation.** MODERATE-HIGH.
5. **Reconciliation expectation.** UB label `agreement_expected`;
   MODERATE-HIGH SVR (≥ 0.5) feeds §6.2.1 TBD-A1's ≥ 52/66 count.
   Sealed §6.4 treats pos 188 as a fresh-7 denominator member
   only, not a ≥ 2/7 contributor; the pos 73 analog (SVR 0.85
   point estimate) resolves to MODERATE-HIGH at §E4
   bucket-granularity. An SVR < 0.5 outcome would constitute §6.4
   edge-case falsification (denominator-only framing contradicted);
   a MEDIUM outcome (0.50–0.70) would register as a candidate-level
   miss indicating priors = 1 signal weaker than the pos 73 analog
   suggested.
6. **Core judgment.** Sole fresh-7 prior-occurrence edge case;
   MODERATE-HIGH SVR reflects the Stage 2b/2c pos 73 analog
   resolved at bucket-granularity rather than a new commitment.

### Position 197 — bb_squeeze_mean_reversion_197

1. **Structural assessment.** Factor set
   `{close, bb_upper_24_2, zscore_48, rsi_14, realized_vol_24h, sma_24, return_24h}`.
   Grammar: `close <= bb_upper_24_2` AND `zscore_48 < -1.2` AND
   `rsi_14 < 35.0` AND `realized_vol_24h < 0.03` entry; three OR
   exits (`close crosses_above sma_24`, `rsi_14 > 55.0`,
   `return_24h > 0.02`). Selector-label: bb_upper defect cluster,
   oversold variant. Non-fresh-9; priors = 7 (maximum factor-set
   reoccurrence count in §E4 deep-dive set).
2. **Plausibility expectation.** MODERATE-HIGH — heavy
   prior-occurrence weight supports reinforcement of the
   mean-reversion grammar despite the bb_upper defect. The `<=`
   variant of bb_upper is functionally identical to the `<` variant
   within the defect family.
3. **Alignment expectation.** MODERATE. DSL clean; defect-driven
   semantic drift identical to other bb_upper cluster members.
   Priors = 7 does not repair alignment — alignment is a
   per-candidate structural read, not a prior-occurrence lift.
4. **SVR expectation.** MODERATE-HIGH.
5. **Reconciliation expectation.** UB label `agreement_expected`;
   MODERATE-HIGH SVR (≥ 0.5) feeds §6.2.1 TBD-A1's ≥ 52/66 count.
   Priors = 7 (the heaviest-repeat in the deep-dive set) combined
   with UB `agreement_expected` supports MODERATE-HIGH within the
   bb_upper defect-capped range. No §6.4 duty (not fresh-7).
6. **Core judgment.** Heavy-repeat mean-reversion candidate with
   persistent bb_upper-defect alignment drag; MODERATE-HIGH
   reflects reinforcement strength capped by the defect.

### Position 198 — volatility_breakout_regime_198

1. **Structural assessment.** Factor set
   `{realized_vol_24h, macd_hist, close, sma_50, return_24h}`.
   Grammar: `realized_vol_24h > 0.04` AND `macd_hist > 0.0` AND
   `close > sma_50` AND `return_24h > 0.015` entry; three OR exits
   (`realized_vol_24h < 0.025`, `macd_hist crosses_below 0.0`,
   `return_24h < -0.03`). Selector-label: high-volatility breakout
   with trend-filter and return-magnitude confirmation. RSI-absent,
   vol_regime-present: satisfies §6.4 fresh-7 hard-coded
   membership.
2. **Plausibility expectation.** MODERATE-HIGH — HIGH-vol gate
   (`> 0.04`), positive momentum histogram, trend filter, and
   realized-return magnitude form a coherent breakout grammar. The
   `close > sma_50` conjunct is the weakest anchor: a 50-period
   moving average is a broad trend filter, not a precise
   price-structure marker, and its gating contribution is weaker
   than e.g. a Bollinger band or explicit resistance break.
3. **Alignment expectation.** HIGH — DSL matches the
   selector-label cleanly; no defect family; each conjunct parses
   to its declared role.
4. **SVR expectation.** MODERATE-LOW.
5. **Reconciliation expectation.** UB label `neutral`; a
   MODERATE-LOW outcome places the candidate in the lower-SVR
   region of the §6.3 distribution without pre-registering it
   specifically into the SVR ≤ 0.30 tail, and feeds §6.6's
   aggregate candidate-level observations and §6.4's ≥ 2/7
   contributor count (fresh-7 member with expected below-0.5
   outcome). Weaker-anchor framing parallels pos 173: both are
   RSI-absent fresh-7 HIGH-vol breakouts with one load-bearing
   grammar weakness, here the `close > sma_50` broad trend-filter
   state-test. A MODERATE-or-higher outcome would register as
   candidate-level tension rather than automatic §6.4 failure,
   since §6.4 requires ≥ 2/7 contributors from the fresh-7 pool,
   not pos 198 specifically.
6. **Core judgment.** Fresh-7 HIGH-vol breakout candidate
   paralleling pos 173; `sma_50` trend-filter is the broad-anchor
   weakness driving SVR below 0.5 despite otherwise clean
   construction.

## Remaining Candidates (Schema-Level Only)

Of the 200 Stage 2d positions, 199 produce D7b calls and one
(position 116) produces a skipped-source record per Lock 1.5.
Of the 199 D7b call positions, 20 are pre-registered with full
per-candidate prose in §E4 Deep-Dive Per-Candidate Expectations,
and 20 form the Multi-Tier Test-Retest Grid in §E3 (Tier 1 n=5 +
Tier 2 n=15, with partial overlap possible per Lock 3.2).

The remaining ~160 D7b call positions carry no per-candidate
prose pre-registration. Sign-off adjudication for these positions
is schema-level only: each call is captured in the standard
per-call record (`call_NNN_live_call_record.json` per Lock 1.6
filename invariant) and contributes to aggregate counts under
§6.1-6.4 per its observed UB label and SVR outcome. No
per-candidate bucket pre-registration exists for these positions;
they are governed solely by the aggregate claims.

## Position 116 Treatment — brief reference to Lock 1.5

Position 116 is the single non-call position in the 200-element
Stage 2d sequence. Per Lock 1.5 (D7_STAGE2D_SCOPE_LOCK_v2 §1.5),
position 116 produces a **deterministic skipped-source record**,
not a D7b call. The record is written to
`docs/d7_stage2d/call_116_live_call_record.json` with the
following Lock 1.5 schema:

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

**Taxonomy isolation** (per Lock 1.5):

- `skipped_source_invalid` is NOT a D7b error.
- `skipped_source_invalid` does NOT count toward abort rule (a)
  `api_level_consecutive`, rule (b) `error_rate_over_threshold`,
  or rule (c) `content_level_threshold`.
- `skipped_source_invalid` records are NOT part of the error-rate
  numerator or denominator.
- `critic_status_counts` in the aggregate batch record reports
  `ok`, `d7b_error`, and `skipped_source_invalid` as **three
  distinct counters**.

**Double guardrail** (per Lock 1.5, Lock 7.7):

- Position 116 is the **only** position permitted to produce
  `critic_status="skipped_source_invalid"`.
- Any other position producing `skipped_source_invalid` triggers
  a hard abort under rule (g) `unexpected_skipped_source` (Lock
  7.7).

**Aggregate-count exclusion** (per §6.1 anchor): Position 116 is
excluded from all aggregate counts in §6.1–§6.4. All §6.1–§6.4
aggregate denominators and numerators are evaluated over the 199
D7b-call positions only. §E3 and §E4 pre-registrations enumerate
D7b-call positions exclusively; no §E3 or §E4 entry references
position 116.
