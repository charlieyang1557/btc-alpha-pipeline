# WF Test-Boundary Semantics Decision

**Status:** Accepted. Locked at commit `bd513e5` (design spec).
**Date:** 2026-04-26
**Design doc:** `docs/superpowers/specs/2026-04-26-wf-test-boundary-semantics-design.md`
**Implementation plan:** `docs/superpowers/plans/2026-04-26-wf-test-boundary-semantics-plan.md`

## Decision

Canonical walk-forward test-window metrics use **flatten-at-boundary, test-period-only** semantics. At each WF test window:

1. Strategy is freshly instantiated.
2. Broker is initialized at `test_start` with $10,000 cash.
3. No position, no equity, no decision/accounting state from train carries into test.
4. Pre-test history is loaded only for indicator/factor warmup; pre-test broker activity is forbidden.
5. All metrics (return, Sharpe, drawdown, trades, win rate, profit factor) are computed exclusively from broker activity inside `[test_start, test_end)`.

## Function-level scope

| Engine function | Rule applies? |
|---|---|
| `run_walk_forward` | YES (corrected per this decision) |
| `run_regime_holdout` | NO (already correct; warmup-from-inside, fresh-capital — see DESIGN INVARIANT at `engine.py:1192-1237`) |
| `run_backtest` (single-run) | NO (mathematically correct as-is) |

## Hard prohibition

No DSR, PBO, CPCV, MDS, strategy-shortlist, or research-direction decision may consume `run_walk_forward` outputs computed under the pre-correction engine. Pre-correction WF metrics in sealed prior closeouts (Phase 1, Phase 1A, Phase 2A signoffs) are under re-validation; references to those closeouts must be paired with the corresponding erratum.

## Related artifacts

- Design spec (full reasoning): `docs/superpowers/specs/2026-04-26-wf-test-boundary-semantics-design.md`
- Test classification table: `docs/decisions/wf_test_boundary_semantics_test_classification.md`
- Phase 1 erratum: `docs/closeout/PHASE1_ENGINE_ERRATUM.md`
- Phase 2C erratum: `docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`

## Forward-pointers

See spec Section FP for FP1 (factor/compiler boundary audit), FP2 (regime_holdout unification), FP3 (Phase 4 lifetime simulator + in-scope metric renaming), FP4 (property-based testing), FP5 (qualitative-claim re-validation), FP6 (adversarial-review follow-ups), FP7 (test-suite completeness audit).
