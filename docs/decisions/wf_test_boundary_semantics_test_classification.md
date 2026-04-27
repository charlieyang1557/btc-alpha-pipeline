# WF Boundary Semantics — Test Classification Table

**Generated:** 2026-04-26
**Spec:** `docs/superpowers/specs/2026-04-26-wf-test-boundary-semantics-design.md`

## Classifications

| File | Test/Assertion | Lines | Classification | Notes |
|---|---|---|---|---|
| tests/test_walk_forward.py | TestGenerateWindows::test_basic_windows | 42–56 | not affected | pure unit test of window generation; no backtest run, no metric values |
| tests/test_walk_forward.py | TestGenerateWindows::test_first_window_dates | 58–71 | not affected | verifies date tuples only; no metric values |
| tests/test_walk_forward.py | TestGenerateWindows::test_second_window_dates | 73–86 | not affected | verifies date tuples only; no metric values |
| tests/test_walk_forward.py | TestGenerateWindows::test_no_windows_if_range_too_short | 88–97 | not affected | asserts empty list; no metric values |
| tests/test_walk_forward.py | TestGenerateWindows::test_short_windows | 99–115 | not affected | window count assertion; no metric values |
| tests/test_walk_forward.py | TestGenerateWindows::test_test_end_equals_last_day_of_month | 117–129 | not affected | verifies calendar boundary; no metric values |
| tests/test_walk_forward.py | TestGenerateWindows::test_windows_are_contiguous | 131–142 | not affected | verifies date adjacency; no metric values |
| tests/test_walk_forward.py | TestGenerateWindows::test_full_pipeline_range | 144–158 | not affected | window count range assertion; no metric values |
| tests/test_walk_forward.py | TestWalkForwardRun::test_returns_walk_forward_result | 214–216 | not affected | isinstance check; structural |
| tests/test_walk_forward.py | TestWalkForwardRun::test_correct_number_of_windows | 218–221 | unchanged | asserts `len(windows) == 3`; window count is structural and unaffected by metric semantics |
| tests/test_walk_forward.py | TestWalkForwardRun::test_window_results_are_backtest_results | 223–226 | not affected | isinstance check; structural |
| tests/test_walk_forward.py | TestWalkForwardRun::test_summary_run_id_is_uuid | 228–231 | not affected | UUID format check; structural |
| tests/test_walk_forward.py | TestWalkForwardRegistry::test_total_row_count | 249–252 | not affected | row count = N + 1; structural |
| tests/test_walk_forward.py | TestWalkForwardRegistry::test_window_rows_have_correct_type | 254–257 | not affected | run_type string check; structural |
| tests/test_walk_forward.py | TestWalkForwardRegistry::test_summary_row_exists | 259–262 | not affected | exactly one summary row; structural |
| tests/test_walk_forward.py | TestWalkForwardRegistry::test_window_parent_ids_match_summary | 264–269 | not affected | parent_run_id linkage; structural |
| tests/test_walk_forward.py | TestWalkForwardRegistry::test_summary_parent_id_is_null | 271–274 | not affected | NULL check; structural |
| tests/test_walk_forward.py | TestWalkForwardRegistry::test_window_rows_have_train_dates | 276–281 | not affected | non-NULL date check; structural |
| tests/test_walk_forward.py | TestWalkForwardRegistry::test_window_rows_have_test_dates | 283–288 | not affected | non-NULL test_start/test_end check; structural |
| tests/test_walk_forward.py | TestWalkForwardRegistry::test_window_fee_model | 290–293 | not affected | fee_model string check; structural |
| tests/test_walk_forward.py | TestWalkForwardRegistry::test_window_strategy_name | 295–298 | not affected | strategy_name string check; structural |
| tests/test_walk_forward.py | TestTradeArtifactIsolation::test_all_window_csvs_exist | 324–329 | not affected | file existence check; structural |
| tests/test_walk_forward.py | TestTradeArtifactIsolation::test_csv_row_counts_match_registry | 331–343 | unchanged | asserts CSV row count == registry total_trades; trade CSV isolation behavior is unchanged by the patch (trade filtering is already correct; only equity-curve-based metrics change) |
| tests/test_walk_forward.py | TestTradeArtifactIsolation::test_all_entries_within_test_window | 345–361 | needs sibling test | asserts trade-list entry isolation (entry_time_utc >= test_start); pair with equity-curve isolation assertion covered by T8 in regression set |
| tests/test_walk_forward.py | TestTradeArtifactIsolation::test_all_exits_within_test_window | 363–379 | needs sibling test | asserts trade-list exit isolation (exit_time_utc <= test_end); same pattern; T8 covers |
| tests/test_walk_forward.py | TestWalkForwardSummaryMetrics::test_sharpe_is_finite | 386–389 | unchanged | `math.isfinite(sharpe)` only; holds under both current and corrected semantics |
| tests/test_walk_forward.py | TestWalkForwardSummaryMetrics::test_total_return_is_finite | 391–394 | unchanged | `math.isfinite(ret)` only; holds under both semantics |
| tests/test_walk_forward.py | TestWalkForwardSummaryMetrics::test_max_drawdown_in_range | 396–399 | unchanged | asserts `0.0 <= dd <= 1.0`; range bound is structural, holds post-patch |
| tests/test_walk_forward.py | TestWalkForwardSummaryMetrics::test_total_trades_positive | 401–403 | unchanged | asserts `> 0`; trade count is unaffected by equity-curve semantics change |
| tests/test_walk_forward.py | TestWalkForwardSummaryMetrics::test_win_rate_in_range | 405–408 | unchanged | asserts `0.0 <= wr <= 1.0`; range bound is structural, holds post-patch |
| tests/test_walk_forward.py | TestWalkForwardSummaryMetrics::test_summary_notes_has_metadata | 410–424 | not affected | asserts num_windows, train_months, test_months in notes JSON; no metric values |
| tests/test_walk_forward.py | TestBackwardCompatibility::test_single_run_still_produces_trades | 435–449 | not affected | uses run_backtest single-run path; structurally insulated from WF bug |
| tests/test_walk_forward.py | TestBackwardCompatibility::test_single_run_registry_defaults | 451–479 | not affected | uses run_backtest; verifies Phase 1A registry defaults; no WF metric involvement |
| tests/test_regime_holdout.py | TestPassingCriteriaSpecCases (5 tests: test_sharpe_gate_fails, test_drawdown_gate_fails, test_return_gate_fails, test_trade_count_gate_fails, test_all_four_pass) | 62–85 | not affected | pure unit tests on `_evaluate_regime_holdout_pass`; no engine run; regime holdout unchanged per spec Q3d Option A |
| tests/test_regime_holdout.py | TestPassingCriteriaBoundaries (10 tests) | 88–157 | not affected | exhaustive boundary tests on `_evaluate_regime_holdout_pass`; no engine run; regime holdout unchanged |
| tests/test_regime_holdout.py | TestV2ConfigLoader::test_reads_disjoint_ranges_from_disk | 167–179 | not affected | reads environments.yaml; no engine run |
| tests/test_regime_holdout.py | TestV2ConfigLoader::test_version_is_v2 | 181–186 | not affected | config schema check; no engine run |
| tests/test_regime_holdout.py | TestV2ConfigLoader::test_regime_holdout_block_present_with_4_criteria | 188–202 | not affected | config schema check; no engine run |
| tests/test_regime_holdout.py | TestV2ConfigLoader::test_validation_and_test_placeholders_present | 204–212 | not affected | config schema check; no engine run |
| tests/test_regime_holdout.py | TestV2ConfigLoader::test_loader_rejects_v1_shape | 214–219 | not affected | error-path unit test; no engine run |
| tests/test_regime_holdout.py | TestWalkForwardSkipsTwentyTwo::test_no_window_overlaps_2022 | 227–257 | not affected | window-generation level; no metric values |
| tests/test_regime_holdout.py | TestWalkForwardSkipsTwentyTwo::test_2020_2021_range_produces_sub_windows | 259–267 | not affected | window count and year check; no metric values |
| tests/test_regime_holdout.py | TestWalkForwardSkipsTwentyTwo::test_2023_range_too_short_yields_zero_sub_windows | 269–276 | not affected | asserts empty list; no metric values |
| tests/test_regime_holdout.py | TestTrainAggregationNotStitched::test_mean_sharpe_not_product | 290–308 | not affected | directly calls `_aggregate_walk_forward_metrics` with hardcoded per-window dicts; asserts aggregation math (mean/max/sum) not engine-computed metric values; patch does not touch the aggregation function |
| tests/test_regime_holdout.py | TestRunRegimeHoldoutRegistryRow::test_row_shape_and_lineage | 390–443 | not affected | verifies run_type, parent_run_id, batch_id, hypothesis_hash, regime_holdout_passed encoding, and test_start/test_end strings; regime holdout loads fresh broker with holdout-only data, unaffected by WF boundary bug |
| tests/test_regime_holdout.py | TestRunRegimeHoldoutRegistryRow::test_passed_flag_matches_gate | 444–482 | not affected | verifies INTEGER encoding matches `_evaluate_regime_holdout_pass`; regime holdout unaffected |
| tests/test_regime_holdout.py | TestRunRegimeHoldoutRegistryRow::test_requires_dsl_or_strategy_cls | 484–495 | not affected | error-path structural test |
| tests/test_regime_holdout.py | TestIntegrationTwoSummariesPlusHoldout::test_two_summaries_and_linked_holdout | 555–661 | not affected | calls run_walk_forward and run_regime_holdout; asserts row counts, parent_run_id linkage, train_ranges provenance, and 2022-bar exclusion; no metric value assertions; structural/relational only |
| tests/test_regime_holdout.py | TestIntegrationDslCompiledEndToEnd::test_dsl_compiled_hypothesis_hash_roundtrip | 694–766 | not affected | calls run_walk_forward + run_regime_holdout via DSL compile path; asserts hypothesis_hash, strategy_source, batch_id, parent_run_id, regime_holdout_passed; no WF metric value assertions |
| tests/test_regime_holdout.py | TestRegistryMigration::test_idempotent_create_table | 777–801 | not affected | DB schema migration idempotency; no engine run |
| tests/test_regime_holdout.py | TestRegistryMigration::test_phase1_row_preserved_after_migration | 803–886 | not affected | DB migration row preservation; no engine run |
| tests/test_regime_holdout.py | TestNoHoldoutCli::test_main_has_no_holdout_choice | 900–910 | not affected | source inspection via inspect.getsource; structural |
| tests/test_regime_holdout.py | TestNoHoldoutCli::test_cli_walk_forward_has_no_holdout_hook | 913–922 | not affected | source inspection; structural |
| tests/test_phase1_pipeline.py | TestRegistryFields (all 12 tests: test_run_type, test_fee_model, test_strategy_name, test_strategy_source, test_warmup_bars, test_effective_start_after_warmup, test_total_trades_positive, test_sharpe_is_finite, test_total_return_is_finite, test_max_drawdown_in_range, test_win_rate_in_range, test_initial_capital, test_final_capital_positive, test_phase1a_nulls, test_parent_run_id_null, test_test_dates_match) | 93–182 | not affected | all use run_backtest single-run path; no WF involvement; confirmed by run_backtest call at line 56 |
| tests/test_phase1_pipeline.py | TestResultStructure::test_equity_curve_non_empty | 193–195 | not affected | single-run equity curve; no WF involvement |
| tests/test_phase1_pipeline.py | TestResultStructure::test_equity_curve_length_reasonable | 197–202 | not affected | single-run equity curve length; no WF involvement |
| tests/test_phase1_pipeline.py | TestResultStructure::test_trade_csv_exists | 204–207 | not affected | single-run CSV existence; no WF involvement |
| tests/test_phase1_pipeline.py | TestResultStructure::test_trade_csv_row_count | 209–212 | not affected | single-run CSV count; no WF involvement |
| tests/test_phase1_pipeline.py | TestResultStructure::test_metrics_keys_complete | 214–229 | not affected | structural key check on single-run result |
| tests/test_phase1_pipeline.py | TestTradePriceVerification (all 6 tests) | 237–341 | not affected | cross-references trade fill prices against raw OHLCV; single-run mode; no WF involvement |
| tests/test_engine.py | TestEngineBasic::test_returns_backtest_result | 123–135 | not affected | isinstance + run_id check; single-run |
| tests/test_engine.py | TestEngineBasic::test_produces_trades | 137–147 | not affected | trade count == 1; single-run |
| tests/test_engine.py | TestEngineBasic::test_equity_curve_non_empty | 149–159 | not affected | asserts `len(equity_curve) == 30`; single-run synthetic data; no WF involvement |
| tests/test_engine.py | TestEngineBasic::test_metrics_populated | 161–175 | not affected | structural key check on single-run result |
| tests/test_engine.py | TestTradeTimeSemantics (all 5 tests) | 191–271 | not affected | signal/fill time semantics on single-run; no WF involvement |
| tests/test_engine.py | TestTradeCSV (all 3 tests) | 282–328 | not affected | single-run CSV output; no WF involvement |
| tests/test_engine.py | TestWarmupHandling::test_effective_start_after_warmup | 339–355 | not affected | single-run warmup boundary; no WF involvement |
| tests/test_engine.py | TestWarmupHandling::test_equity_curve_excludes_warmup | 359–372 | not affected | asserts `len == 30 - 9`; single-run warmup; no WF involvement |
| tests/test_engine.py | TestRegistryIntegration::test_registry_write | 383–413 | not affected | single-run registry row shape; no WF involvement |
| tests/test_engine.py | TestRegistryIntegration::test_no_registry_write_when_disabled | 415–429 | not affected | single-run flag behavior; no WF involvement |
| tests/test_dsl_baselines.py | TestDslLoadsAndCompiles::test_loads_validates_compiles (4 parametrized) | 80–89 | not affected | compile-time structural check; uses run_backtest single-run (no WF) |
| tests/test_dsl_baselines.py | TestSMACrossoverParity::test_parity | 129–134 | not affected | uses run_backtest single-run confirmed at line 58; structurally insulated from WF bug |
| tests/test_dsl_baselines.py | TestMomentumParity::test_parity | 138–147 | not affected | same: run_backtest single-run |
| tests/test_dsl_baselines.py | TestVolatilityBreakoutParity::test_parity | 151–160 | not affected | same: run_backtest single-run |
| tests/test_dsl_baselines.py | TestMeanReversionParity::test_parity | 164–173 | not affected | same: run_backtest single-run |
| backtest/engine.py | run_walk_forward docstring: "metrics are computed only on the test portion" | 740–741 | needs update after patch | currently aspirationally stated but implementation is wrong: total_return uses original $10k as denominator, not portfolio value at test_start; docstring will be accurate after the Task 5 patch and should be confirmed at that time |
| backtest/metrics.py | (no source-level WF assertions or invariants) | n/a | not affected | compute_all_metrics is correct as-is; the bug is in the caller (engine.py) passing the wrong initial_capital; this function needs no change |

## Counts

- unchanged: 7
- needs sibling test: 2 (covered by T8 in regression set)
- needs update after patch: 1
- not affected: 67
- TOTAL: 77

## Verification

Each classification was verified by reading the actual test code, not assumed.

**Non-obvious classification decisions:**

1. `test_csv_row_counts_match_registry` (tests/test_walk_forward.py:331–343) is classified **unchanged** rather than "needs sibling test" because it asserts CSV row count == registry `total_trades`. The trade CSV isolation logic in `_save_trade_csv` and the trade-filtering step in `run_walk_forward` are not changed by the patch; only equity-curve initial-capital semantics change. The count equality relationship holds under both current and corrected engine.

2. `TestTrainAggregationNotStitched::test_mean_sharpe_not_product` (tests/test_regime_holdout.py:290–308) appears to assert numeric metric values (sharpe=0.5, return=0.05, etc.) but is classified **not affected** because it calls `_aggregate_walk_forward_metrics` directly with hardcoded per-window input dicts — it does not go through the engine. The patch changes how `ec_test` initial capital is supplied before calling `compute_all_metrics`, not the aggregation function itself.

3. The "not affected" classification for all tests in `tests/test_dsl_baselines.py` was verified by confirming the `_run` helper at lines 56–64 calls `run_backtest` (not `run_walk_forward`). The parity tests run single-run mode on both baseline and DSL-compiled strategies.

4. `TestIntegrationTwoSummariesPlusHoldout::test_two_summaries_and_linked_holdout` (tests/test_regime_holdout.py:555–661) calls `run_walk_forward` but is classified **not affected** because its assertions are purely structural (row counts, parent linkage, train_ranges provenance in JSON notes, and 2022-year exclusion on dates). There are no metric value assertions anywhere in this test body.

5. The engine.py docstring at lines 740–741 is the only item classified **needs update after patch**. It is not a test with a failing assertion; rather it is documentation that states "metrics are computed only on the test portion" — a claim that is aspirationally correct but technically false under the current (buggy) `compute_all_metrics(ec_test, trades_test, cash)` call where `cash=$10,000` is the original initial capital rather than the portfolio value at `test_start`. After Task 5's patch fixes the initial-capital argument, the docstring will be accurate. No update is needed now; a post-patch verification step should confirm this.

6. The "needs update after patch" count is **1**, which is well below the spec's escalation threshold of 8. No scope re-evaluation is required.

7. The plan's sample showed "unchanged: 10" but actual table row counting yields 7. The discrepancy is because the plan's pre-execution guess over-counted: `test_correct_number_of_windows`, `test_csv_row_counts_match_registry`, and the 5 `TestWalkForwardSummaryMetrics` tests are the correct set of 7. The plan did not include `test_total_trades_positive` and `test_win_rate_in_range` in its explicit sample rows, but those are indeed correctly classified here. The plan's "10" was an estimate that included overlap with rows placed in "not affected" after code inspection.
