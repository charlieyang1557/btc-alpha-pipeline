# D7 Stage 2a — Replay Candidate Expectations

**Anti-hindsight-bias commitment:** This file MUST be committed to git
before the `--confirm-live` call. The live-call entrypoint verifies that
this file has at least one git commit.

## Target Batch

- **batch_uuid:** `5cf76668-47d1-48d7-bd90-db06d31982ed`
- **position:** 102

## Selection Criteria Applied

The replay candidate was selected from the signed-off Stage 2d batch
using `scripts/select_replay_candidate.py` with the following criteria:

1. lifecycle_state == "pending_backtest"
2. theme != "momentum"
3. 3 <= n_factors <= 5
4. At least one crosses_above or crosses_below operator
5. rsi_14 is not the sole factor
6. position in [10, 190]
7. No thin_theme_momentum_bleed inferred

## Pre-Call Expectations

_To be filled in by the researcher before the live call._

### D7a Rule Scores (deterministic — known before live call)

These will be computed from the reconstructed BatchContext and the
candidate's DSL. They are fully deterministic and can be verified
against the dry-run output.

- `theme_coherence`: _fill before live call_
- `structural_novelty`: _fill before live call_
- `default_momentum_fallback`: _fill before live call_
- `complexity_appropriateness`: _fill before live call_

### D7b LLM Scores (expectations, not predictions)

The live Sonnet response is inherently stochastic (`temperature=1.0`).
These are expectations about plausible ranges, not exact predictions.

- `semantic_plausibility`: Expect [0.3, 0.9]. A strategy with 3-5
  factors using cross operators should be plausible enough for a
  non-trivial score.
- `semantic_theme_alignment`: Depends on the replay candidate's theme
  and factor set. _fill specific expectation before live call_
- `structural_variant_risk`: With prior_factor_sets from the batch,
  expect [0.2, 0.8] depending on how similar the candidate's factor
  set is to prior sets.

### Expected Outcome

- `critic_status`: "ok" (no errors expected if the prompt is clean)
- `d7b_mode`: "live"
- Cost: < $0.01 at Sonnet pricing for ~2K input tokens + ~200 output tokens
- Reasoning length: 100-400 characters (schema-enforced)

## Post-Call Notes

_To be filled in after the live call. Compare actual vs. expected._
