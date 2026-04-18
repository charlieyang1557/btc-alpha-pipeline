# D7 Stage 2b Expectations

## Anti-Hindsight Anchor

These expectations are locked before any Stage 2b live Sonnet calls are fired.
They are derived only from the signed-off Stage 2d replay batch, the locked
Stage 2b candidate selector output, the D7a rule fields, and the Stage 2a
single-call evidence. They do not use any Stage 2b live D7b outputs.

The locked replay source is batch `5cf76668-47d1-48d7-bd90-db06d31982ed`.
The locked candidate list is `docs/d7_stage2b/replay_candidates.json`.
The firing order is the `firing_order` order in that JSON and is not to be
reshuffled after seeing any response.

## Aggregate Expectations Across All 5 Calls

The batch should complete all five calls without a startup abort, unless a
hard-fail gate correctly prevents firing before the first live request. The
expected critic status is `ok` for every completed live call. Any `d7b_error`
is evidence to preserve, not retry around.

Expected cost is low: each call should remain below the $0.05 per-call ceiling,
and the full five-call sequence should remain below the $0.10 Stage 2b cap.
The aggregate record should report ordered lists for costs, token counts,
reasoning lengths, wall-clock seconds, statuses, D7a scores, D7b scores, and
agreement/divergence reconciliation. These are sequence records, not
distribution summaries.

The three scan-result fields must be populated on every per-call record:
`leakage_audit_result`, `forbidden_language_scan_result`, and
`refusal_scan_result`. On `ok` calls, all three should be structured pass
records. On any parser/content error, the leakage audit should still be
populated and the parser-dependent scans should be explicit `not_reached`
records rather than null.

Agreement/divergence adjudication is intentionally mechanical. For
`divergence_expected`, D7b is expected to assign
`structural_variant_risk < 0.5`. For `agreement_expected`, D7b is expected to
assign `structural_variant_risk >= 0.5`. For `neutral`, there is no directional
prediction.

## Per-Candidate Expectations

### Candidate 1 — Position 17, mean_reversion, divergence_expected

Hash: `17396a8e291dae75`.

This candidate uses a broad mean-reversion factor set with Bollinger, RSI,
z-score, volatility, return, close, and SMA inputs. D7a selected it as an
expected divergence case. The pre-registered expectation is that live D7b may
judge the semantic structure as less variant-like than the rule layer implies,
so the mechanical reconciliation target is
`structural_variant_risk < 0.5`.

### Candidate 2 — Position 73, volatility_regime, divergence_expected

Hash: `ab3c1725e1cf4890`.

This is the Stage 2a replay position and remains in the Stage 2b sequence as a
volatility-regime divergence probe. It uses close, MACD histogram,
realized-volatility, long return, and SMA structure. Stage 2a live evidence
showed D7b could view this as highly variant-like; nevertheless, the locked
pre-registered Stage 2b label is `divergence_expected`, so the mechanical
reconciliation target remains `structural_variant_risk < 0.5`.

### Candidate 3 — Position 74, volume_divergence, divergence_expected

Hash: `eb019d8da279abb2`.

This candidate follows immediately after the Stage 2a position but changes the
theme and factor mix toward volume divergence with close, long return, RSI,
SMA, and volume z-score. It is expected to test whether D7b distinguishes
adjacent firing-order context from semantic factor-set structure. The
mechanical reconciliation target is `structural_variant_risk < 0.5`.

### Candidate 4 — Position 97, mean_reversion, agreement_expected

Hash: `1f8cbe2ba01c13a9`.

This candidate returns to mean reversion and has one prior occurrence of its
factor set with high overlap. D7a and the selector label pre-register this as
an agreement case where D7b should also identify elevated structural variant
risk. The mechanical reconciliation target is
`structural_variant_risk >= 0.5`.

### Candidate 5 — Position 138, volatility_regime, neutral

Hash: `9da35eee117da577`.

This late-bucket volatility-regime candidate uses close, realized volatility,
return, SMA, and volume z-score. It is included for coverage across firing
order, theme, and factor structure rather than for a directional D7a/D7b
agreement claim. The pre-registered label is `neutral`, so no
structural-variant-risk direction is predicted.
