# D7 Stage 2a Replay Candidate — Pre-Live Qualitative Expectations

**Candidate:** batch `5cf76668-47d1-48d7-bd90-db06d31982ed`,
position `73`, theme `volatility_regime`  
**Factor set:** `close`, `macd_hist`, `realized_vol_24h`,
`return_168h`, `sma_50`  
**D7a observations (from dry-run):** `theme_coherence=0.2`,
`structural_novelty=1.0`, `default_momentum_fallback=0.8`,
`complexity_appropriateness=0.7`, flag `n_conditions_heavy`  
**Structural properties:** 6 conditions, 1 entry group, 2 exit groups,
336-bar max hold, `factor_set_prior_occurrences=0` (first-time factor
set in batch)

**Authored by:** Charlie, 2026-04-18 (before live call)  
**Purpose:** Anti-hindsight-bias anchor.

## Format Adherence Expectations

- Parses cleanly on first attempt.
- Exactly 4 top-level keys, no extras.
- Reasoning length within `[100, 400]` Unicode characters.

## Reasoning Style Expectations

- Descriptive, not directive; no accept / reject / approve / recommend
  language.
- References specific factors and operators from the DSL.
- Mentions `realized_vol_24h` or volatility context.
  The theme anchor is present; omission would be a noteworthy miss.

## Score Distribution Expectations — Qualitative Bounds Only

- No score pegged at `0.0` or `1.0` on any axis.
- `semantic_plausibility`: mid-range. The strategy has defensible
  volatility-regime logic: entry on volatility expansion, exit on price
  breaking below SMA trend support. However, `n_conditions=6` and the
  presence of `macd_hist` in a non-momentum theme add complication.
- `semantic_theme_alignment`: mid-range. Theme anchor
  `realized_vol_24h` is present, but factor overlap with theme hints is
  only `0.2`.
- `structural_variant_risk`: expected low, near `0.0`.
  This axis has reversed polarity. `factor_set_prior_occurrences=0`
  means this is a first-time factor set; a calibrated critic should
  score it as structurally distinct. A score `>= 0.5` on this axis is
  evidence of polarity misread.

## Refusal Avoidance Expectations

- No "I cannot evaluate", "insufficient context", or similar refusal
  patterns.
- Low confidence should produce conservative mid-range scores with
  uncertainty in reasoning, not a refusal.

## Failure Modes I Would Find Informative

These are not blockers by themselves; they are diagnostic signals for
Stage 2b prompt / parser / calibration work.

- All three scores equal `0.5`: D7b collapsing to default rather than
  reading the hypothesis.
- Reasoning does not mention `realized_vol_24h`: missing the theme
  anchor signal.
- Reasoning does not mention `macd_hist` or the thin-theme bleed risk:
  missing the semantic complement to D7a's structural
  `default_momentum_fallback=0.8`.
- Reasoning is generic volatility-strategy prose without DSL specifics:
  pattern-matching on theme rather than reading the hypothesis.
- `structural_variant_risk >= 0.5`: polarity misread.

