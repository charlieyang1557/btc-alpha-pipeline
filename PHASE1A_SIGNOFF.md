# Phase 1A Sign-Off Note

**Sign-off date:** 2026-04-16
**Branch:** `claude/setup-structure-validators-JNqoI`
**Test suite:** 264 tests passing

---

## Completed Deliverables

| # | Deliverable | File(s) | Status |
|---|------------|---------|--------|
| D1 | Parquet → Backtrader feed | `backtest/bt_parquet_feed.py` | Done (Phase 0) |
| D2 | Execution model + slippage | `backtest/execution_model.py`, `backtest/slippage.py` | Done (Phase 0) |
| D3 | Single-run engine | `backtest/engine.py` | Done |
| D4 | Core metrics | `backtest/metrics.py` | Done |
| D5 | Experiment registry (Phase 1A schema) | `backtest/experiment_registry.py` | Done |
| D6 | Base strategy template | `strategies/template.py` | Done |
| D7 | SMA crossover baseline | `strategies/baseline/sma_crossover.py` | Done |
| D8 | Trade audit tool | `backtest/trade_audit.py` | Done |
| D9 | Momentum baseline | `strategies/baseline/momentum.py` | Done |
| D10 | End-to-end pipeline test | `tests/test_phase1_pipeline.py` | Done |

---

## Key Verification Conclusions

### Trade Time Semantics (Critical)
- `entry_signal_time_utc` = bar N close (when signal was computed)
- `entry_time_utc` = bar N+1 open (when order filled)
- Verified: signal-to-fill is exactly 1 bar apart in all tests
- Verified: fill price matches raw OHLCV open at fill bar for first and last trades

### Execution Model
- 7bps effective cost per side confirmed via commission checks on real trades
- `cheat_on_close=False`, `cheat_on_open=False` enforced
- Zero-volume deferral implemented and tested (up to 24-bar cancellation)
- PercentSizer used for fractional BTC sizing ($10K capital vs $40-70K BTC)

### Warmup Handling
- `EquityCurveCollector.prenext()` overridden to skip warmup bars
- Equity curve and metrics computed only on post-warmup period
- `effective_start` recorded in registry (50 hours after data start for SMA crossover)

### Baseline Strategy Results (2024-01-01 to 2024-12-31)
| Strategy | Trades | Sharpe | Return | Win Rate | PF |
|----------|--------|--------|--------|----------|----|
| SMA crossover (20/50) | 43 | -0.520 | -10.19% | 0.33 | 0.85 |
| Momentum (24-bar, +2%) | 58 | -0.215 | -4.45% | 0.34 | 0.93 |

Both strategies produce negative Sharpe — expected for naive baselines after 14bps round-trip costs. This validates the engine is not biased toward profitable results.

### Registry Integrity
- All Phase 1A fields populated: run_type, fee_model, warmup_bars, effective_start, initial/final capital
- Phase 1A conventions: train/validation fields NULL, test_start/test_end = engine date range
- `fee_model = "effective_7bps_per_side"` consistently applied

### Trade Audit (Manual Verification)
- SMA crossover trades #1, #22, #43 audited — all checks passed
- Momentum trades #1, #58 audited — all checks passed
- Checks: price match, commission match, volume > 0, 1-bar signal-to-fill separation

---

## Known Limitations

1. **Long/flat only trade collector.** `TradeCollector` uses FIFO entry matching and assumes single-position long/flat strategies. Does not support partial exits, scaling, short positions, or overlapping positions. Adequate for Phase 1 baselines; must be extended for Phase 2+ complex strategies.

2. **7bps is an effective cost model, not a realistic execution simulator.** The 7bps-per-side cost (4bps taker + 3bps slippage) is a simplification. Real slippage depends on order size, book depth, and market conditions. This is documented in `config/execution.yaml` and accepted for baseline validation.

3. **31 historical missing bars are known and accepted.** All in 2020-2023 period (exchange outages). Backtrader indicators are bar-based not time-based, so a 24-period SMA averages the last 24 rows regardless of time gaps. Negligible for 55K+ bar dataset. No gaps observed from 2024 onward.

4. **TradeCollector entry matching is O(n×m) linear search.** `_get_bar_volume()` scans backward through data feed. Acceptable for Phase 1 trade volumes (< 100 trades per run). Would need optimization for high-frequency strategies.

5. **WARMUP_BARS as property.** SMA crossover and momentum use `@property` for WARMUP_BARS (derived from strategy params). This is a Backtrader-compatible pattern but means the value is instance-level, not class-level.

---

## Go Decision

**Proceed to Phase 1B (walk-forward).**

Phase 1B constraint: walk-forward is an orchestration layer wrapping the already-validated single-run engine. Each window calls `run_backtest()` unchanged. The engine execution path, trade semantics, and registry conventions from Phase 1A must not be modified.
