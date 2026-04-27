# Walk-Forward Test-Boundary Semantics — Design Specification

**Status:** Approved design, pre-implementation. Ready for `writing-plans` skill.
**Date:** 2026-04-26
**Authors:** Charlie (decisions), Claude Code (drafting), with adversarial input from ChatGPT and Claude advisor across 6 sub-questions.
**Predecessor evidence:**
- Codex adversarial review (2026-04-26): identified the carry-in bug class. Output preserved at `/tmp/.../boeabk2v3.output`.
- Magnitude audit (2026-04-26): empirical quantification across all 792 Phase 2C Tier 3 windows. 82.1% of windows affected, median window has 92% of reported PnL coming from train-period accumulation.
- Phase 2C Phase 1 closeout (`docs/closeout/PHASE2C_5_PHASE1_RESULTS.md`, sealed at commit `861d186`): records the now-invalidated 48/198 binary success criterion.

**Companion artifacts:**
- Canonical decision file: `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md` (to be written from this design).
- Test classification table: `docs/decisions/wf_test_boundary_semantics_test_classification.md` (produced during step 1 of execution sequence).
- Erratum files (post-patch): `docs/closeout/PHASE1_ENGINE_ERRATUM.md`, `docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`.

---

## Read-First: Function-level Rules Summary

This section is the load-bearing reference artifact. Reading it should answer "which engine function does what, under which boundary semantic, and which downstream consumer invokes it" without needing to read any of the question-shaped sections.

### Boundary semantics by engine function

| Engine function | Boundary semantic | Warmup served from | Rationale |
|---|---|---|---|
| `run_walk_forward` | (iii) — fresh strategy at `test_start`, fresh $10,000, warmup-history-only | pre-`test_start` history (no signal dead zone) | Test windows are 3 months; losing WARMUP_BARS hours could be 7-8% of evaluation period for high-warmup strategies. Pre-history warmup keeps the test window fully evaluable. |
| `run_regime_holdout` | unchanged — fresh strategy at `holdout_start`, fresh $10,000, warmup-from-inside | inside the holdout window (~50-bar dead zone at start of 2022) | Holdout window is 1 year (~8,760 bars); losing ~50 bars is negligible (~0.6%). Matches Phase 1A single-run convention everywhere. Documented as Phase 2A D4 design invariant. |
| `run_backtest` (single-run) | mathematically correct as-is — fresh broker at `start_date` with declared `cash`, no boundary trimming | inside the backtest window | Single run; no train/test boundary exists. Already correct under any semantic. |
| Future Phase 4 lifetime simulator (TBD — see FP3) | continuity / carry-in semantic (separate metric family) | TBD — see FP3 | Deployment-performance forecasting requires the actual lifetime equity curve including carry-in. Not built yet; tracked as separate apparatus, not as a mode of the existing engine functions. |

### Consumer-to-function mapping

| Consumer | Invokes | Uses metric semantic |
|---|---|---|
| Phase 2C funnel (`run_phase2c_batch_walkforward.py`) | `run_walk_forward` | (iii) — research filter |
| Phase 2 regime-holdout AND-gate (per CLAUDE.md) | `run_regime_holdout` | unchanged regime-holdout semantic |
| Phase 1A single-run baselines | `run_backtest` | single-run, no boundary issue |
| Phase 2A DSL parity tests | `run_backtest` (single-run) | single-run, structurally insulated from WF bug |
| Future DSR / PBO / CPCV / MDS (per TECHNIQUE_BACKLOG §2.2.2-§2.2.4 + §2.4.1) | `run_walk_forward` outputs | depends on (iii) being canonical |
| Future Phase 4 paper-trading harness | future lifetime simulator (TBD — see FP3) | continuity semantic, separate apparatus |

### Hard prohibition

No DSR, PBO, CPCV, MDS, or strategy-shortlist decision may consume `run_walk_forward` outputs computed under the pre-correction engine. This is a metric-semantics contract, not a performance optimization.

Pre-correction WF metrics in sealed prior closeouts (Phase 1, Phase 1A, Phase 2A signoffs) are explicitly under re-validation per the Q3a propagation plan; references to those closeouts must be paired with the corresponding erratum once re-validation completes. Phase 1A single-run trade-audit claims are explicitly marked unaffected. Phase 2A DSL parity claims are explicitly marked unaffected because they use single-run mode. Any Phase 2A text that cites WF readiness or WF-derived conclusions is cross-referenced to the corrected engine semantics.

Old closeouts remain historical records, but their WF metric values are superseded. Any future citation of pre-correction WF numbers must cite the corresponding erratum alongside the original closeout.

---

## Section Q1 — Canonical metric semantic: research filter (flatten-at-boundary)

**Decision.** Canonical walk-forward test-window metrics use *flatten-at-boundary, test-period-only* semantics. Each test window is treated as an independent out-of-sample evaluation interval. Returns, Sharpe, max drawdown, total trades, win rate, profit factor, average trade duration, and average trade return are computed exclusively from broker activity inside `[test_start, test_end)`.

**What this metric measures.** "If this strategy is re-evaluated on a fresh, unseen test period, do its test-period decisions make money?" Answer is bounded to the strategy's choices in the test window — uncontaminated by train-period accumulation, train-opened positions, or any state inherited from earlier engine activity.

**What this metric does NOT measure.** It does not estimate continuous deployment performance. It does not measure what a strategy's account equity would look like under uninterrupted live operation. Those questions belong to a separate apparatus (future Phase 4 paper-trading harness or equivalent) using its own metric family that retains carry-in semantics. The two metric families serve different purposes; they are not interchangeable.

**Why this semantic for this purpose.** The walk-forward funnel is a research filter — its output drives candidate selection, DSR multiple-testing correction, PBO ranking-stability tests, regime-holdout AND-gating, and the Phase 1 binary verdict. Every one of these consumers requires that "test-window performance" be a property of test-window decisions only. Allowing train-period PnL to leak into test metrics means the funnel selects strategies that benefited from train-period accumulation rather than strategies that make good test-period decisions. The empirical magnitude audit confirmed this is not theoretical: under the broken semantic, 36 of 48 binary winners had carry-in PnL dominating their reported Sharpe, and the median window's reported PnL was 92% train-period accumulation.

---

## Section Q2 — Equity baseline at test_start: re-instantiate strategy with fresh capital

**Decision.** At each walk-forward test window, the strategy is freshly instantiated. The Backtrader broker is initialized with $10,000 of cash at `test_start`. No position, no equity, no strategy-local decision/accounting state, and no broker activity from train carries into test. Pre-test history is loaded into the data feed only for indicator/factor warmup and may not influence broker accounting.

**Concretely, at every test window:**
1. Load enough pre-test bars for indicator/factor warmup. The amount is determined by the strategy's declared `WARMUP_BARS`.
2. Instantiate a fresh strategy object — no inherited fields, counters, timers, position memory, pending-order state, or "just exited" flags.
3. Initialize the broker at `test_start` with `cash=$10,000`. No inherited equity from train-period activity.
4. The strategy's `next()` method does not fire on bars before `test_start`. Indicators may consume pre-test data for warmup; the strategy's decision logic begins at `test_start`.
5. All metrics (return, Sharpe, drawdown, trades, win rate, etc.) are computed exclusively from bars at or after `test_start`.

**Why re-instantiate (option iii) over fresh-capital-but-continuing-state (option i).** Option (i) would reset broker capital but allow the strategy's internal state — `_entry_bar`, indicator memory, "just got out of a position" flags, max-hold timers — to carry from train. For DSL-compiled strategies that read factors from a parquet on each `next()` call, this carryover is small but nonzero. For strategies with stateful entry/exit logic — including the 166/198 batch-1 candidates using `crosses_above`/`crosses_below` and most candidates using `max_hold_bars` — the carryover affects the first several test-period decisions in ways that are concentrated, not uniform. Option (iii) closes this contamination path by construction.

**Allowed-vs-forbidden state at the boundary.**
- **Allowed:** indicator/factor warmup state populated by pre-test data (SMA values, RSI values, volatility readings, Bollinger bands, etc.).
- **Forbidden:** decision/accounting state (open positions, broker equity above $10,000, `_entry_bar` counters, pending orders, lifecycle flags, "just exited" memory).

**Implementation note (constraint, not prescription).** The semantic requirement is (iii): no strategy decision/accounting state crosses the `test_start` boundary. T3 (state-carryover regression test, defined in Section Q3c) is the enforcement mechanism. Any implementation that makes T3 pass satisfies this part of the design. The implementation may use any approach that satisfies T3: a fresh per-window engine call with explicit strategy re-instantiation, a gated strategy wrapper, a feed-level warmup/execution split, or another pattern selected during implementation planning. One candidate, a single Cerebro call spanning `[test_start - WARMUP_BARS, test_end]` with `next()` suppressed until `test_start`, is appealing for minimalism but only achieves (iii) if the strategy's internal state at `test_start` matches a fresh instantiation. Backtrader instantiates strategies once per Cerebro call, so a single-call approach that merely suppresses `next()` during warmup may still leave custom strategy fields, pending-order state, or lifecycle counters populated by warmup activity. Indicator/factor warmup state is allowed; decision/accounting state is not. If T3 cannot be made to pass under that approach, the implementation must use explicit re-instantiation or another design that does. The writing-plans phase owns the final implementation choice.

**Alternative (option ii) explicitly rejected.** "Preserve broker equity at test_start, position flattened" — strategy keeps train-period winnings as starting capital but loses its position — is a hybrid that fails the cross-strategy comparability property. Two strategies entering the same test window with $42k vs $7k of train-period equity would have different position-sizing capacity for identical trade signals, making their test-window Sharpes non-comparable. This is exactly the bias the canonical semantic exists to prevent.

---

## Section Q3a — Sealed-baseline propagation: full re-run + bounded qualitative adjudication (Option C-lite)

**Decision.** After the engine patch lands and the regression test set passes, all four sealed Phase 1B baselines are re-run under the corrected engine on the v2 split. Numerical deltas are documented per baseline. A bounded qualitative adjudication is performed against WF-dependent claims only. Sealed closeouts themselves are NOT edited; corrections live in erratum files that point forward from the original closeouts.

**What gets re-run.**
- All 4 sealed Phase 1B baselines on the v2 split: `sma_crossover` (the calibration anchor sanity check 2 used at 1e-15 precision), `momentum`, `mean_reversion`, `volatility_breakout`.
- Phase 2C Phase 1's Tier 3 sweep over all 198 batch-1 candidates (the largest affected artifact).

**What gets documented.**
- A delta table per baseline: sealed `wf_sharpe`, `wf_total_return`, `wf_max_drawdown`, `wf_total_trades` vs. corrected counterparts. Same column set for the Phase 2C corrected vs. original distribution stats.
- For each baseline that has a sealed qualitative claim attached, one sentence per baseline: *survives* / *weakened* / *reversed* / *not affected* under the corrected numbers.
- A one-paragraph summary stating whether Phase 1's foundational "walk-forward kills the single-year Sharpe illusion" claim still holds qualitatively under the corrected engine.

**What gets explicitly excluded from re-evaluation.**
- Single-run trade semantics (Phase 1A's manual trade audit framework — independent of WF bug).
- DSL parity tests (Phase 2A — uses single-run mode, structurally insulated).
- Proposer/critic infrastructure (Phase 2B D6/D7 — independent of WF metric semantics).
- Theme rotation, budget ledger, hypothesis-hash dedup logic (independent of WF metrics).
- Phase 2C batch-1 proposer-only artifacts (the proposer outputs are unchanged; only their downstream WF evaluation changes).
- Architectural-integrity findings 4.1–4.3 from `PHASE2C_5_PHASE1_RESULTS.md` (DSL re-extraction, compiler renderer faithfulness, hash-space cleanliness) are independent of engine WF semantics and require no re-validation. Finding 4.4 (engine bit-determinism) survives as a determinism property but its calibration-anchor interpretation requires erratum noting that the reproduced baseline values were themselves under the broken semantic.

**Aggregation rules under corrected semantic.** The summary aggregation rules from CLAUDE.md (mean Sharpe across windows, mean return, max drawdown, sum of trades) are inherited from pre-correction context. Under the corrected semantic, these rules remain mechanically applicable — T9 enforces mechanical correctness — but their *interpretation* should be verified during sealed-baseline re-run. If the corrected per-window distributions suggest a different aggregation is more meaningful, that's a separate design conversation outside this arc.

**Erratum file pattern.** Two new files, neither modifies existing closeouts:
- `docs/closeout/PHASE1_ENGINE_ERRATUM.md` — lists original sealed WF-dependent numbers from `PHASE1_SIGNOFF.md`, plus any WF-dependent references in later closeouts. Phase 1A single-run trade-audit claims are explicitly marked unaffected. Phase 2A DSL parity claims are explicitly marked unaffected because they use single-run mode.
- `docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md` — same structure for the Phase 2C closeout. Includes the corrected distribution stats, corrected binary verdict count, and a qualitative adjudication of the closeout's two headline findings (RSI hypothesis falsification framing and theme-quality differential).

**Hard stop on scope expansion.** If any qualitative claim does NOT survive the corrected numbers, the erratum records this as `superseded — warrants separate re-evaluation outside this engine-fix arc`, **flags any downstream backlog entry whose validity depends on the superseded claim**, and the current arc does not re-litigate Phase 1's conclusions. A separate decision is opened for any superseded finding before any further phase work depends on it.

**Artifact versioning.** Corrected reruns must write to new artifact paths and must not overwrite pre-correction artifacts. Pre-correction artifacts are retained only as superseded evidence.

---

## Section Q3b — Test-suite audit ordering: targeted enumeration → failing tests → patch → triage (Option C-plus)

**Decision.** Before any engine patch is written, perform a targeted upfront audit of test surfaces that could encode WF or regime-holdout boundary semantics. Then write the new bug-catching regression tests (T1-T10 from Section Q3c) — they must fail against the current engine. Patch the engine until those tests pass. Then run the full test suite and triage any other failures.

**Targeted enumeration scope.** Audit only files whose tests touch WF or regime-holdout output, equity-curve semantics, or boundary handling:
- `tests/test_walk_forward.py`
- `tests/test_regime_holdout.py`
- `tests/test_phase1_pipeline.py`
- `tests/test_engine.py`
- `tests/test_dsl_baselines.py` (expected classification: not affected — single-run mode only, structurally insulated; verify rather than assume)
- `backtest/engine.py` (source-side check for assertions or invariants embedded in code comments)
- `backtest/metrics.py` (source-side check)

For each test in the targeted scope, classify exactly one of:
- **unchanged** — passes under both current and corrected engine; no action.
- **needs sibling test** — asserts a partial property (e.g., trade-list isolation) that should be paired with a new test asserting the complementary property (e.g., equity-curve isolation).
- **needs update after patch** — currently asserts a value that will change under the new semantic; update only after corrected values are in hand.
- **not affected** — touches WF code paths but tests structural property independent of metric values.

The classification table lives in `docs/decisions/wf_test_boundary_semantics_test_classification.md` (sibling file to the canonical decision doc, not embedded). The decision doc references the sibling file. Future updates to the classification table don't churn the decision doc. It serves as the audit record showing the test-surface blast radius was enumerated, not assumed.

**The full test suite is NOT audited upfront.** The targeted scope captures every test that could plausibly encode WF semantics. Full-suite triage happens reactively after the engine patch lands. If the targeted enumeration's classification was honest, the full-suite triage produces few additional surprises. If unexpected failures surface in the full suite, they're investigated case-by-case with the question "is this a real engine regression or a test that was wrong?" — never auto-classified as "test was wrong."

**The phased sequencing is the contract for this work item; deviations require an explicit decision-doc amendment, not unilateral implementer choice.** See Section S for the full execution sequence.

**What the enumeration explicitly catches.** The trade-isolation tests at `tests/test_walk_forward.py:345-379` are the canonical example. They assert `entry_time_utc >= test_start` and `exit_time_utc <= test_end` for every trade in the test-window CSV. They pass under the current engine because the engine filters trades by entry time — they look like they cover boundary isolation. They never check equity-curve isolation. The enumeration step catches this kind of pattern: tests that assert partial properties and present as complete coverage. Such tests get classified "needs sibling test" and the sibling tests (T8, T10) are added in the regression set per Q3c.

---

## Section Q3c — Regression test set: T1–T10

**Decision.** Ten regression tests are written before any engine patch. T1–T9 live in `tests/test_walk_forward_boundary_semantics.py` (new file) and assert properties of the corrected `run_walk_forward` semantic. T10 lives in `tests/test_regime_holdout.py` (existing file) and asserts the structural property of `run_regime_holdout` that distinguishes its boundary semantic from `run_walk_forward`'s. Each test must fail against the current (broken) engine *before* the patch begins; passing tests pre-patch indicates either the test is wrong or the bug doesn't manifest in that test's setup.

### T1 — `test_test_period_return_excludes_train_period_pnl`
*Property:* canonical `wf_total_return` reflects only test-period broker activity, not cumulative final-equity-over-original-capital.
*Setup:* a deterministic strategy that earns large profit during train (e.g., buy-and-hold capturing a strong train-period trend) and is flat or losing during test. Independently compute test-only return from a test-period equity curve that starts at $10,000 at `test_start`, includes only test-period broker activity, and uses the same mark-to-market convention as `run_backtest`. Assert `wf_total_return` matches the test-only return, not the cumulative.
*Catches:* the exact bug. sma_crossover Window 4 reported +154% on −$9,874 of test trade PnL — T1 asserts this can't happen.

### T2 — `test_zero_test_trades_implies_zero_test_return`
*Property:* if no trades open during the test window AND no position exists at or after `test_start`, canonical `wf_total_return` = 0.0 and `wf_sharpe` = 0.0.
*Setup:* a strategy whose entry conditions are train-period-specific so no trades fire during test, and confirmed to have no position at test_start.
*Catches:* the 7 visible-zero rows from Codex's finding (positions 2, 8, 17, 43, 98, 173, 190 — trades=0 with non-zero return).

### T3 — `test_no_strategy_state_carryover_from_train_to_test`
*Property:* strategy decision/accounting state at the first test bar matches a fresh instantiation, not whatever state the strategy held at end-of-train.
*Setup:* a custom test strategy class with explicit decision-state fields (`_train_phase_counter` incremented during train, a "just exited" flag set during train, `_entry_bar` set to a known train value). Assert at the first post-`test_start` `next()` call that decision-state fields are zero/None/uninitialized.
*Catches:* the trap where the engine implements (i) (fresh capital + continuing strategy state) while believing it implemented (iii) (fresh strategy + fresh capital). Indicator/factor warmup state is allowed; decision/accounting state is not — T3 enforces this distinction.
*Forward-pointer:* if anyone later refactors the engine to a single-Cerebro-call approach with `next()` suppression, T3 catches the residual state-carryover that approach risks.

### T4 — `test_warmup_history_populates_indicators_without_affecting_metrics`
*Property:* pre-test bars satisfy indicator warmup (so the strategy can decide on the first test bar) but pre-test broker activity, trades, and equity do not enter test-window metrics.
*Setup:* a strategy with a 50-bar SMA. Test window starts at `test_start`. Pre-test history of ≥50 bars exists in the data feed. Assert: (a) the strategy can compute the SMA at the first test bar (warmup is satisfied), (b) zero trades opened before `test_start` are counted in `wf_total_trades`, (c) the first canonical test equity-curve observation at or after `test_start` equals `initial_capital` ($10,000).
*Catches:* the over-correction failure mode where someone "fixes" the bug by stripping pre-test data entirely, which would break warmup. T4 asserts pre-test data is allowed for indicators but not for accounting.

### T5 — `test_two_strategies_with_different_train_pnl_have_same_test_starting_capital`
*Property:* cross-strategy test-window comparability.
*Setup:* Strategy_A profits in train, Strategy_B loses in train, both running the same test window. Assert at `test_start` that both strategies' `initial_capital` = $10,000 and both equity curves start at $10,000.
*Catches:* the canonical pre-correction failure mode where 36/48 binary winners had carry-in PnL dominating their reported Sharpe.

### T6 — `test_canonical_metric_is_deterministic_across_runs`
*Property:* same strategy, same window, same data, run twice → identical metrics to floating-point precision.
*Setup:* run any deterministic strategy through `run_walk_forward` twice, compare summary metrics field-by-field.
*Catches:* implementation regressions that introduce non-determinism. Bit-determinism was one of the four architectural-integrity findings in `PHASE2C_5_PHASE1_RESULTS.md` §4.4 — T6 ensures the corrected engine preserves it.

### T7 — `test_test_window_metrics_independent_of_train_window_choice`
*Property:* fixed test window, vary train window *beyond the warmup horizon*; canonical `wf_*` metrics for the test window are bit-identical across train choices.
*Setup:* keep `(test_start, test_end)` constant. Run the same strategy multiple times with different `train_start` values, all chosen such that the warmup window `[test_start - WARMUP_BARS, test_start]` is fully populated in every variant. Assert `wf_total_return`, `wf_sharpe`, `wf_max_drawdown`, `wf_total_trades` for the test window are bit-identical across train choices.
*Note:* variations *within* the warmup horizon legitimately change indicator state at test_start and are not covered by T7.
*Catches:* the subtle reintroduction of the bug class where someone changes train-range handling and accidentally re-leaks train state into test metrics through a path the other tests don't cover.

### T8 — `test_equity_curve_starts_at_initial_capital_at_test_start`
*Property:* explicit equity-curve isolation. The first equity-curve observation at or after `test_start` equals `initial_capital`.
*Setup:* any strategy. Run `run_walk_forward`. For each window, assert the first canonical test equity-curve observation at or after `test_start` equals `initial_capital` ($10,000).
*Catches:* the framing-completion gap that allowed the original bug. The existing `test_all_entries_within_test_window` and `test_all_exits_within_test_window` at `test_walk_forward.py:345-379` assert trade-list isolation but never check equity-curve isolation. T8 closes the asymmetry.

### T9 — `test_summary_aggregation_uses_corrected_per_window_metrics`
*Property:* `walk_forward_summary` correctly aggregates from corrected per-window metrics, not from cached/legacy fields or stale aggregation logic.
*Setup:* construct two windows with known corrected per-window metrics (mock or controlled). Assert the summary's aggregation matches the v2 disjoint-train-window rules:
- `sharpe_ratio`: arithmetic mean of per-window Sharpe values
- `total_return`: arithmetic mean of per-window returns (unless a later decision changes this)
- `max_drawdown`: maximum/worst per-window drawdown
- `total_trades`: sum of per-window trades
*Catches:* the layer downstream of per-window correctness. Phase 2C's `walk_forward_results.csv` consumes summary metrics, not per-window metrics. Even if windows are correctly fixed at the per-window level, a bug in `_aggregate_walk_forward_metrics` could re-poison candidate-level results.

### T10 — `test_regime_holdout_equity_curve_starts_at_initial_capital`
*Lives in:* `tests/test_regime_holdout.py` (not the new WF semantics file).
*Property:* `run_regime_holdout` runs as holdout-window-only fresh-capital evaluation; no pre-holdout broker equity or position state enters the holdout metric path.
*Setup:* invoke `run_regime_holdout` with any deterministic strategy. Assert at the first post-warmup bar of 2022 that broker equity = `initial_capital` ($10,000) and no position is open from any prior period.
*Catches:* the failure mode where someone "fixes" `run_regime_holdout` to match `run_walk_forward`'s new semantic (warmup-from-pre-history) without realizing that breaks the 4-condition gate calibration. T10 protects the documented asymmetry per Q3d.
*Note:* the asymmetry is intentional. T10 asserts the structural property (fresh capital, no inherited state) shared by both engine functions; what differs is *how* warmup is served, which is implied by the parquet feed bounds and not separately asserted.

**Test discipline.** Every test in T1–T10 must fail against the current engine before patch work begins. Verification of failure-against-current-engine is itself a checkpoint — if a test passes against the broken engine, either the test setup doesn't actually exercise the bug or the test is asserting the wrong property. Each pre-patch failure is recorded with one line of provenance.

**What the test set does NOT cover.**
- "The engine produces good Sharpe values for any specific strategy" — sealed-baseline re-validation under Q3a.
- "DSR/PBO produce correct multiple-testing corrections" — downstream Phase 3 work.
- "Other boundary-contamination bugs in factors/, DSL compiler, or other layers" — outside this arc; tracked as FP1.

The set is sufficient for the engine bug class. It is not a proof of engine correctness across all properties. Adversarial review (step 9a, before patch ships) is the protection against bugs the regression set doesn't cover.

---

## Section Q3d — `run_regime_holdout` scope: unchanged (Option A) + T10

**Decision.** The new boundary semantic from Q1+Q2 applies to `run_walk_forward` only. `run_regime_holdout` is NOT modified. Its existing semantic — holdout-window-only data feed, fresh $10k starting capital, warmup served from inside the window with the first ~WARMUP_BARS bars not signal-eligible — is preserved as the documented Phase 2A D4 design invariant.

**Why `run_regime_holdout` is not affected by the WF bug.** `run_regime_holdout` does not run a continuous train+test backtest with post-hoc trimming. It calls `run_backtest` with `fromdate=2022-01-01` and `todate=2022-12-31` — the data feed contains only holdout-period bars. The broker is initialized at `2022-01-01` with `cash=$10,000` and no prior positions. `total_return = (final_capital / $10,000) - 1` is mathematically correct because there's no train period to leak from; the entire run IS the holdout period.

**Why the warmup-from-inside semantic is intentional.** The DESIGN INVARIANT block at `engine.py:1192-1237` documents three reasons:
1. Matches Phase 1A single-run engine behavior — every run in the registry uses the same feed-loading rule.
2. The 4-condition gate (min_sharpe, max_drawdown, min_total_return, min_total_trades) remains operationally meaningful over an 8,700-bar year minus ~50 warmup bars. Losing the first few days does not change whether a strategy survives a bear regime.
3. Modifying `ParquetFeed` or `run_backtest` to prepend pre-window history purely for holdout runs would touch code paths used by every existing backtest. That is explicitly out of scope for D4.

A `CONTRACT GAP` at `engine.py:1175-1183` already documents: "If a later phase modifies the holdout feed loader to prepend pre-window history, the effective sample grows to the full 8760 bars and these thresholds — especially min_total_trades=5 — should be re-validated in the same PR that introduces the feed change." This decision doc affirms that contract gap as the canonical forward-pointer for any future unification.

**T10 as the asymmetry anchor.** Q3c's T10 asserts the structural property `run_regime_holdout` shares with `run_walk_forward` (fresh $10k, no inherited broker state). It does NOT assert the warmup-from-inside property — that's implied by the parquet feed bounds and not separately needed. T10's purpose is to catch the failure mode where someone reads the new WF semantic and "fixes" `run_regime_holdout` to match, breaking the calibrated 4-condition thresholds in the process.

**Out of scope for this arc.**
- Unifying `run_walk_forward` and `run_regime_holdout` warmup semantics (deferred — see FP2).
- Re-validating Phase 2A D4 sealed sign-off.
- Modifying `config/environments.yaml` regime-holdout block.

---

## Section S — Interactions and Sequencing

The six locked answers (Q1, Q2, Q3a, Q3b, Q3c, Q3d) have a strict execution order. This section makes the order explicit and distinguishes gates from checkpoints.

**Definitions.**
- **Gate:** if it fails, the work stops and is not allowed to proceed to the next step. Patch acceptance requires all gates to clear.
- **Checkpoint:** must be executed; outcomes are documented; outcomes do not block patch commit but do block downstream consumer work.

### Patch acceptance gates (must clear before patch ships)

| Step | Action | Failure handling |
|---|---|---|
| 1 | **Targeted enumeration** of WF/regime-holdout test surface (Q3b). Produce classification table; commit to `docs/decisions/wf_test_boundary_semantics_test_classification.md`. | If enumeration reveals a test surface materially larger than expected (>8 affected tests with value-pegged assertions), pause and re-evaluate scope. |
| 2 | **Write T1–T10 regression tests** (Q3c). Verify each fails against the current (pre-patch) engine. Record one-line provenance per test. | If any test passes against the pre-patch engine, either the test setup doesn't exercise the bug or the test is asserting the wrong property. Stop and resolve before proceeding. |
| 3 | **Patch engine** to satisfy (iii) for `run_walk_forward`. Iterate until T1–T10 pass. Apply test updates per the classification table for "needs update after patch" entries. | If T1–T10 cannot be made to pass under a chosen implementation approach, switch to a different implementation. The semantic requirement is fixed; the implementation is flexible. |
| 4 | **Run targeted-scope tests.** All tests in the enumeration scope must pass. | Failures here are real regressions in the patched code; debug and re-iterate. |
| 5 | **Run full pytest suite.** Triage any failures: real regression, or stale test that was asserting the pre-correction value? | Each failure is classified as "real regression" (debug, re-iterate) or "stale test, update assertion" (document the update with rationale, then patch the test). Auto-classification as "stale test" without rationale is forbidden. |
| 9a | **Adversarial review of patched engine + regression tests + test classification table.** Use `/codex:adversarial-review` with patch + tests + classification in scope. | Material findings must be resolved or explicitly accepted as known issues before patch ships. The mechanism that caught the original bug is not skipped for the fix of that same bug class. |

### Post-patch validation checkpoints (must clear before downstream consumer work uses corrected-engine outputs)

**Parallelism note.** Steps 6, 7, 8, and 9b are post-patch validation checkpoints that may run in parallel after the patch ships. The order presented here is logical (re-runs feed errata which feed adversarial review; backlog dependency-flagging is independent of the others) but does not represent a strict execution sequence. Step 9b is the only checkpoint with explicit dependencies (it consumes the erratum content produced by steps 6 and 7). Steps 6, 7, and 8 are mutually independent and can run concurrently.

**Step 8 framing note.** Step 8 was originally framed as a "narrow gate" at engine commit, but logically requires the corrected-engine commit SHA to exist (which means the engine commit must have already happened). Step 8 is therefore structurally a post-patch task. Its narrow-gate property is preserved: it is an observable, bounded, hard-required verification — but it gates *downstream consumer work* (DSR/PBO/CPCV/MDS implementation, Phase 2C re-interpretation, strategy shortlist decisions), not the engine commit itself.

| Step | Action | Outcome handling |
|---|---|---|
| 6 | **Re-run sealed Phase 1B baselines** (Q3a Option C-lite). All four baselines on v2 split. Document numerical deltas. Write `docs/closeout/PHASE1_ENGINE_ERRATUM.md`. | Findings recorded. If qualitative claims survive, note in erratum and proceed. If a claim does NOT survive, record as superseded; flag downstream backlog entries whose validity depends on the superseded claim; warrant separate re-evaluation outside this arc. |
| 7 | **Re-run Phase 2C Tier 3** (all 198 batch-1 candidates) under the corrected engine. Write to a new artifact path (do not overwrite pre-correction artifacts). Write `docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`. | Corrected distribution stats and binary verdict count documented. If the corrected distribution materially differs from pre-correction, flag for separate research-direction conversation. |
| 8 | **Update TECHNIQUE_BACKLOG.md dependency-flagging** for the four named entries (PBO §2.2.2, DSR §2.2.3, CPCV §2.2.4, MDS §2.4.1). Each entry adds a "Depends on: corrected WF test-period semantics per `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`, commit `<corrected-engine-commit-SHA>`" line. Narrow scope: this verification covers only these four entries, not the backlog as a whole. | If the four entries lack the dependency lines, add them. ~5-minute task. Hard-required before downstream consumer work; not a soft outcome. |
| 9b | **Adversarial review of erratum files and regenerated artifacts.** Runs after steps 6 and 7 complete. | Findings folded into a final commit if material; documented as forward-pointers if non-blocking. |

### Hard rule

The engine patch may be committed after patch acceptance gates (1, 2, 3, 4, 5, 9a) clear. No DSR/PBO/CPCV/MDS implementation, Phase 2C re-interpretation, strategy shortlist, or research-direction decision may use corrected-engine outputs until the post-patch validation checkpoints (6, 7, 8, 9b) are completed or explicitly deferred by a separate decision.

---

## Section FP — Forward-pointers

Items intentionally outside the scope of this engine-fix arc. Each is flagged here so it doesn't get lost; none are commitments.

### FP1 — Boundary-contamination audit of factors and DSL compiler
The engine WF bug was a boundary-contamination defect at the engine-orchestration layer. The same class of bug could in principle exist at the factor-computation layer (e.g., a factor computed using future data, a rolling window that crosses a boundary) or the DSL compiler layer (e.g., subtle interactions between cross operators and warmup at the train→test transition). A separate scoped work item to audit the factor pipeline and DSL compiler for boundary-contamination defects should be opened before any further phase work depends on those layers.

### FP2 — `run_regime_holdout` unification with `run_walk_forward`
The two functions have different warmup semantics for principled reasons (Q3d). Eventually, when the regime-holdout 4-condition gate thresholds need recalibration for an unrelated reason (per the CONTRACT GAP at `engine.py:1175-1183`), unifying the two semantics under a single canonical rule may become attractive. The existing CONTRACT GAP serves as the canonical forward-pointer.

### FP3 — Future Phase 4 lifetime simulator + in-scope metric naming
The (b) continuity / carry-in semantic from Q1's brainstorm is not implemented in this arc. When Phase 4 is scoped, a separate lifetime-simulator apparatus should be built — distinct code path, distinct metric family, distinct purpose ("forecast deployment performance" vs. the WF funnel's "filter candidates"). Future deployment metrics should use names like `lifetime_return`, `lifetime_sharpe`, `continuity_return`, `continuity_sharpe`.

**In-scope for this arc:** rename (or document) `run_walk_forward`'s output fields as `wf_test_period_*` (e.g., `wf_test_period_sharpe`, `wf_test_period_return`, `wf_test_period_max_drawdown`, `wf_test_period_total_trades`) to prevent name collision when FP3 is eventually built. Bounded scope: applied to all files in the engine commit's diff that touch WF metric field names. Out-of-scope: retroactive renaming in sealed closeout text — those reference the old names and stay as historical record; errata note the new names.

### FP4 — Property-based testing infrastructure
T1-T10 are example-based tests. A property-based test of the form "for any valid strategy and any valid (train, test) window pair, the test-window equity at `test_start` equals `initial_capital`" would be stronger coverage than T1-T10 individually. Adopting a property-based testing framework (Hypothesis library or equivalent) is a separate infrastructure investment, deferred until the test suite is mature enough to justify the dependency.

### FP5 — Re-validation of any superseded qualitative claim
Per the Q3a hard stop, if step 6's qualitative adjudication identifies a sealed Phase 1 claim that does NOT survive the corrected numbers, a separable decision is opened for that claim. The shape of that decision is not pre-specified here — it depends on which claim, which downstream work depends on it, and what the corrected numbers actually show.

### FP6 — Adversarial-review-driven follow-ups
Steps 9a and 9b's adversarial reviews may surface findings that are non-blocking but worth tracking. Each such finding gets a forward-pointer of its own.

### FP7 — Test-suite completeness audit against engine invariants
The original bug survived because tests asserted easy partial properties (trade-list isolation) while missing the harder load-bearing property (equity-curve isolation). The pattern — "tests assert what's easy to assert, and the easy assertions look like complete coverage" — is a generic risk that probably exists elsewhere in the suite. A meta-level audit of "for each load-bearing property in the engine, does the test suite assert it directly or only assert components that imply it?" would be a substantial project but probably catches more than just the WF bug class.

---

## Approvals and provenance

This design was reached through a 6-question brainstorm with adversarial input at every lock-in:
- Q1 (canonical semantic): both reviewers + TECHNIQUE_BACKLOG internal evidence converged on (a).
- Q2 (equity baseline): both reviewers locked (iii) re-instantiation.
- Q3a (sealed-baseline propagation): both reviewers pushed back from initial "Option B" recommendation to Option C-lite.
- Q3b (test-suite audit ordering): both reviewers proposed C-plus enumeration enhancement.
- Q3c (regression tests): both reviewers proposed extra tests; T1-T9 plus T10 in regime_holdout file.
- Q3d (regime_holdout scope): both reviewers locked Option A; T10 added per Claude advisor's discipline argument.

Cross-cutting decisions reached through the four-batch consolidation pass:
- Step 8 narrow-gate framing — verify four named backlog entries reference corrected-engine commit SHA. Operationally placed as a post-patch validation checkpoint (since it requires the commit SHA to exist), but with hard-required not soft-outcome semantics; gates downstream consumer work, not engine commit itself.
- Step 9 split into 9a (gate, patch+tests+classification) and 9b (checkpoint, erratum files).
- FP3 in-scope metric renaming with bounded scope.
- Section RS positioned at top as load-bearing reference artifact.

Spec amendments (post-initial-commit):
- Cross-references added to RS table TBD entries pointing to FP3.
- Parallelism note added to post-patch validation block.
- Step 8 re-categorized from patch-acceptance-gate to post-patch-validation-checkpoint to resolve the chicken-and-egg of needing the commit SHA before verification could happen. Discipline preserved (hard-required, narrow scope, observable verification); placement corrected.
