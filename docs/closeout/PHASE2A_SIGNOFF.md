# Phase 2A Sign-Off Note

**Phase 2A sign-off:** 2026-04-17
**Branch:** `claude/setup-structure-validators-JNqoI`
**Test suite:** 590 tests passing, 0 regressions
**Active blueprint:** `PHASE2_BLUEPRINT.md` (v2)

---

## A. Purpose

This document records the signed-off outcome of Phase 2A — the AI-free
infrastructure closeout — and serves as the authoritative bridge into Phase 2B
(the agent loop phase). It is not a rewrite of the blueprint and not a
changelog. It states what Phase 2A proved, what changed during Phase 2A, which
constraints are now frozen for Phase 2B, and which non-obvious semantics future
maintainers must preserve.

---

## B. Deliverable Status

| # | Deliverable | Key File(s) | Status |
|---|------------|-------------|--------|
| D1 | Factor library + registry + `feature_version` governance | `factors/registry.py`, `factors/build_features.py`, `factors/*.py` | Signed off |
| D2 | Strategy DSL + Backtrader compiler + compilation manifest | `strategies/dsl.py`, `strategies/dsl_compiler.py` | Signed off |
| D3 | Hypothesis hash + dedup + canonicalization | `agents/hypothesis_hash.py` | Signed off |
| D4 | Regime holdout integration (2022, orchestrator-internal) | `backtest/engine.py::run_regime_holdout` | Signed off |
| D5 | Baselines in DSL (parity gate) | `strategies/dsl_baselines/*.json`, `tests/test_dsl_baselines.py` | Signed off |

**Full pytest at Phase 2A close:** 590 passed, 0 regressions.

---

## C. What Phase 2A Proved

- A versioned, precomputed core factor registry exists, governed by a SHA256
  `feature_version` derived from canonical per-factor metadata plus compute
  source. Every factor carries a docstring specifying inputs, computation,
  warmup, output dtype, and null policy; every factor has causality tests
  (warmup correctness, known-value assertions, NaN/future-bar invariance).
- The DSL is expressive enough to capture the semantics of all four Phase 1
  baselines without special-case compiler branches. Baselines that could not
  be expressed against the original factor set were closed by expanding D1,
  not by patching the compiler.
- The compiler is generic: entry/exit conditions, cross operators, factor-vs-
  scalar and factor-vs-factor code paths, NaN-false semantics, and manifest
  drift detection are all schema-driven. No baseline-specific branches exist.
- Hypothesis hash canonicalization is deterministic across Python runs and is
  explicitly separated from D2 manifest canonicalization by a mutual
  `CONTRACT BOUNDARY`. Commutative-AND and commutative-OR attack surfaces are
  closed by test.
- Regime holdout is plumbed as an orchestrator-internal engine path. It has
  no CLI surface, is absent from `main()`, and is enforced absent by a
  mechanical ripgrep check.
- All four Phase 1 baselines have accepted DSL parity on 2024 H1: exact
  `total_trades` match and `sharpe_ratio`, `total_return`, `max_drawdown` all
  within 1e-4 relative tolerance against their hand-written counterparts.
- The infrastructure is sufficient foundation for Phase 2B: Proposer output
  can be validated, compiled, hashed for dedup, and run against train +
  holdout windows with no further scaffolding.

---

## D. Retroactive Changes Made During Phase 2A

Phase 2A was not purely additive. Each deliverable revealed gaps that were
corrected at the right layer rather than deferred or patched downstream.

### D3 hardening (schema and canonicalization)

- **Scalar/string disambiguation** at the condition schema level: a condition
  value is either a float (factor-vs-scalar) or a registered factor name
  (factor-vs-factor). Unknown strings are rejected at validation time with a
  suggestion to use a float, closing an ambiguity the original schema allowed.
- **NaN/Inf rejection at schema level**: NaN/Inf thresholds silently collapse
  comparison semantics (NaN → always False; Inf → degenerate) and are now
  rejected during pydantic validation instead of leaking into compiled code.
- **Duplicate condition rejection at schema level**: conditions within a group
  are rejected if their `(factor, op, value)` triples collide after the same
  scalar normalization D3 uses for dedup (`f"{float(v):.6f}"`), preventing
  redundant AND-merged conditions from proliferating in Proposer output.
- **Contract markers formalized**: `CONTRACT GAP`, `CONTRACT BOUNDARY`, and
  `DESIGN INVARIANT` are documented in `CLAUDE.md` with placement rules and
  are grep-discoverable across the codebase.

### D4 clarification (holdout warmup semantics)

The claim that holdout warmup is "naturally served by late-2021 bars" was
incorrect: `ParquetFeed.from_parquet(fromdate=2022-01-01, todate=2022-12-31)`
loads only 2022 rows, so the first `WARMUP_BARS` bars of 2022 serve as warmup
and are not signal-eligible. This was documented as a `DESIGN INVARIANT` on
`run_regime_holdout` and an associated `CONTRACT GAP` was placed on
`_evaluate_regime_holdout_pass`, rather than silently rewriting the feed
loader to prepend pre-window history. Trusted Phase 1A engine semantics were
preserved intentionally; the holdout passing thresholds in
`config/environments.yaml` are calibrated to these semantics.

### D5 retroactive D1 factor expansion

Expressing the four Phase 1 baselines as DSL required factors that were not
present in the original 14-factor registry. The correct response was to
promote them as D1-level registry expansions (with docstrings, warmup, and
causality tests) — not to add compiler special cases. Factors retroactively
promoted:

- `close`
- `sma_24`
- `bb_upper_24_2`
- `zscore_48`

Each factor was added with its full D1 contract: top-level named compute
function, registry entry with warmup / inputs / output dtype / null policy,
and the three parametrized causality tests (`computes_without_error`,
`null_policy_compliance`, `future_bar_invariance`) plus at least one
known-value assertion. The factor parquet was rebuilt with a new
`feature_version`. No baseline-specific code was introduced in
`strategies/dsl_compiler.py`.

---

## E. Hard Constraints Preserved Going Into Phase 2B

These are project-level constraints, not suggestions. Phase 2B code that
violates any of these is a blueprint violation and must be rejected in review.

- **Factor registry is frozen at batch start.** The Proposer may only use the
  human-approved factor registry available at batch start. The Proposer may
  not propose new factors inside the batch loop, and the orchestrator must
  not grow the registry mid-batch.
- **DSL grammar is frozen at batch start.** The Proposer may not propose new
  operators, new comparison forms, inline arithmetic, or any grammar outside
  the frozen pydantic schema. Extensions require a new D2 schema revision,
  human review, and a new batch.
- **Invalid DSL outputs count.** A Proposer call that returns schema-invalid
  DSL still increments `hypotheses_attempted` and is terminally marked
  `proposer_invalid_dsl`. Budget and lifecycle accounting never silently
  discards a returned proposal.
- **No holdout/validation/test leakage into prompts.** Regime holdout (2022),
  validation (2024), and test (2025) metrics, bars, or derived statistics
  must never appear in Proposer or Critic prompt context — even after the
  fact, even as aggregate.
- **Regime holdout remains orchestrator-internal only.** No CLI flag, no
  public engine entrypoint, no ad-hoc re-runs. The `CONTRACT BOUNDARY` on
  `run_regime_holdout` and the ripgrep self-check enforce this.
- **Compiler special cases remain forbidden.** If a hypothesis cannot be
  expressed in DSL, the DSL schema is revised under D2 governance. The
  compiler stays generic.
- **D2 manifest canonicalization and D3 dedup canonicalization remain
  separate.** The mutual `CONTRACT BOUNDARY` in `strategies/dsl_compiler.py`
  and `agents/hypothesis_hash.py` must be preserved; merging them would
  silently couple drift detection and semantic equivalence.

**Rationale for freezing factor registry and DSL grammar at batch start:**
the agent must search within a fixed research space, not modify the space
itself. Allowing the agent to expand either would make `hypotheses_attempted`
incomparable across a batch, invalidate DSR N, and turn deduplication into a
moving target. Registry and grammar changes are model-class / research-
substrate changes that require human review outside the batch loop.

---

## F. Design Invariants and Contract Boundaries Discovered in Phase 2A

These are the non-obvious semantics future readers are most likely to
"fix" incorrectly.

- **Holdout warmup uses Phase 1A feed-window semantics.** The 2022 parquet
  window is loaded in isolation; pre-window history is not prepended. The
  first `WARMUP_BARS` bars of 2022 are not signal-eligible. This is
  acceptable — and preferable — because D4 preserved trusted Phase 1A engine
  semantics rather than reopening Phase 1 core behavior. Any future change
  to this loader must re-validate the passing thresholds in
  `environments.yaml` in the same PR (flagged by `CONTRACT GAP` at
  `_evaluate_regime_holdout_pass`).
- **Cross operators cost exactly +1 warmup bar relative to continuous
  operators.** `effective_minperiod = warmup_bars + (2 if uses_cross else 1)`,
  unconditionally `>= 2`. This is not a tuning knob; it tracks the arity of
  the comparison helpers and CrossOver's own lookback.
- **Compiled `WARMUP_BARS` and hand-written `WARMUP_BARS` differ by one in
  reporting convention only.** The registry uses a 0-indexed "first N
  positions are NaN" convention (`sma_50.warmup_bars = 49`); hand-written
  baselines use a 1-indexed "N bars needed" convention (`SMA(50).WARMUP_BARS
  = 50`). Runtime gating is controlled by `effective_minperiod` plus the
  internal minperiod gate indicator and matches across both implementations.
  D5 parity tests confirm the convention difference does not affect runtime
  behavior, only reporting.
- **Factor registry changes are model-class / research-substrate changes.**
  Adding, removing, or editing a factor is not a routine code change. It
  requires human review outside the batch loop, a `feature_version` bump,
  and a parquet rebuild. This was true for the four retroactive D5
  promotions and remains true going forward.

**Contract markers in service of future maintenance:**

- `CONTRACT GAP` — a test or mechanism that should exist but doesn't yet,
  with an explicit trigger condition.
- `CONTRACT BOUNDARY` — a deliberate separation between two mechanisms that
  look mergeable but must stay separate. Mutual cross-references required.
- `DESIGN INVARIANT` — a non-obvious design decision future readers might
  mistake for a bug.

Placement rules are in `CLAUDE.md`. Future maintainers should grep for these
markers before "cleaning up" semantics that look redundant.

---

## G. Evidence Summary

- **Test suite:** 590 passed, 0 regressions at Phase 2A close.
- **Acceptance notebooks:** `phase2A deliverable test.ipynb` (covers D3, D4,
  D5 acceptance evidence alongside the earlier D1/D2 notebooks in-tree).
- **Mechanical checks:**
  - No holdout CLI exposure — `run_regime_holdout` is not wired into
    `argparse`, `main()`, or any user-facing entrypoint. `CONTRACT BOUNDARY`
    in `backtest/engine.py` enforces absence by ripgrep.
  - No compiler baseline-specific branches — `strategies/dsl_compiler.py`
    contains no baseline name, parameter value, or baseline-class reference;
    all compilation is schema-driven.
- **Baseline DSL parity (2024 H1):** exact `total_trades` match and
  `sharpe_ratio` / `total_return` / `max_drawdown` within 1e-4 relative
  tolerance across all four baselines (SMA crossover, momentum, volatility
  breakout, mean reversion).

---

## H. Phase 2B Readiness

Phase 2A is complete. Phase 2B may begin.

**Recommended sequencing:**

1. Begin Phase 2B with **D6 Proposer**.
2. Use a **dry-run-first approach**:
   - First prove Proposer + Orchestrator plumbing end-to-end using
     deterministic stub outputs (fixed canned DSL, fixed cost estimates,
     fixed hashes) so that lifecycle transitions, spend-ledger pending rows,
     dedup, manifest writes, train + holdout runs, and batch finalization
     can all be exercised without network variability.
   - Only then swap in the real Sonnet Proposer backend.

The rationale is to separate AI variability from infrastructure /
accounting / lifecycle debugging, and to avoid burning API cost while the
loop plumbing is still being verified. Once the stubbed end-to-end dry run
is green, the live run inherits a validated harness and the only remaining
variable is Proposer output quality.

Phase 2A is the AI-free infrastructure closeout. Phase 2B is the agent loop
phase. Factor and grammar immutability across a batch is a hard constraint,
not a preference.
