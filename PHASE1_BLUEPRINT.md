# BTC Alpha Pipeline — Phase 1 Blueprint

## Phase 1 Target

Build a backtesting engine that can run any strategy against our validated BTC data,
enforce execution conventions from `config/execution.yaml`, and automatically log results
to the experiment registry.

**What "done" looks like for Phase 1A:**
Run a single command → execute SMA crossover on a fixed date range → enforce next-bar-open
execution with 7bps effective cost → log results to experiments.db → manually audit 2-3 trades
to confirm correctness.

**What "done" looks like for Phase 1B:**
Run walk-forward optimization with rolling windows → produce per-window results → aggregate
metrics → log everything with parent/child relationships in the registry.

---

## Phase 1A vs Phase 1B

Phase 1 is split into two subphases to control complexity:

**Phase 1A — Single-Run Engine Validation**
- Prove the backtest engine produces correct results on a fixed date range
- One strategy, one date slice, one result, one registry entry
- Manual trade audit is the go/no-go gate

**Phase 1B — Walk-Forward Orchestration**
- Add rolling walk-forward windows
- Parent/child registry logging
- More baseline strategies
- Post-hoc DSR evaluation

Do NOT start Phase 1B until Phase 1A is fully signed off.

---

## Phase 1A Sign-Off Criteria

All 6 conditions must pass before Phase 1A is considered complete:

1. ✅ `bt_parquet_feed.py` correctly loads the canonical Parquet, with UTC timestamps
   and OHLCV values matching the source file exactly
2. ✅ Single fixed-range backtest runs to completion without errors
3. ✅ SMA crossover generates trades (entry + exit pairs)
4. ✅ Manual trade audit of 2-3 trades confirms:
   - Signal computed on bar N close
   - Order filled at bar N+1 open price
   - 7bps per-side effective cost deducted correctly
   - If fill bar is zero-volume, order deferred to next valid bar
5. ✅ Run automatically written to `experiments.db` with all required fields populated
6. ✅ Results are in a "sane" range — SMA crossover on BTC 1h should NOT show
   Sharpe > 2.0 after fees. If it does, the engine has a bug.

---

## Tech Stack (Phase 1 Additions)

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Backtesting engine | Backtrader 1.9.78+ | Event-driven `next()`, LLM-friendly for Phase 2 |
| Parquet adapter | Custom `bt.feeds.PandasData` subclass | Bridges Phase 0 data to Backtrader |
| Metrics | Custom (scipy for Sharpe) | Core stats only; DSR deferred to Phase 1B |
| Visualization | matplotlib (optional) | Equity curves for debugging, not a deliverable |

---

## Phase 1A Deliverables (in exact order)

### Deliverable 1: Backtrader-Parquet Data Feed
**File:** `backtest/bt_parquet_feed.py`

Custom data feed class that:
- Loads `data/raw/btcusdt_1h.parquet` into a pandas DataFrame
- Maps columns: `open_time_utc` → datetime index, `open/high/low/close/volume` → Backtrader lines
- Supports date range filtering via `fromdate` and `todate` parameters
- Preserves UTC timezone awareness throughout
- Handles the 31 known historical gaps gracefully (Backtrader just skips missing bars)

**Test:** Load Parquet via the feed, verify row count matches direct pandas load for the same
date range. Verify first and last bar prices match the raw data exactly.

### Deliverable 2: Execution Model + Slippage
**Files:** `backtest/execution_model.py`, `backtest/slippage.py`

Reads `config/execution.yaml` and configures a Backtrader Cerebro instance:

**Execution semantics:**
- `broker.set_coc(False)` — disable cheat-on-close
- `broker.set_coo(False)` — disable cheat-on-open
- Orders submitted on bar N fill at bar N+1 open (Backtrader default when cheat modes are off)

**Cost model (Phase 1A):**
- Single effective cost: **7bps per side** (14bps round trip)
- This is a simplification of 4bps taker fee + 3bps slippage
- Implemented via `broker.setcommission(commission=0.0007)` (percentage mode)
- This is NOT a realistic execution simulator — it is an effective cost model for baseline validation
- The `fee_model` field in the registry must be set to `"effective_7bps_per_side"`

**Zero-volume fill rejection:**
- If the designated fill bar has `volume == 0`, defer execution to the next bar with `volume > 0`,
  using that bar's open price
- If deferral exceeds 24 bars (24 hours), cancel the order entirely
- **Implementation:** Subclass `bt.brokers.BackBroker` and override the order matching logic
  to check `volume > 0` before filling. This belongs in `execution_model.py`, NOT in strategy code.
  Strategies must never contain execution deferral logic — the broker layer owns fill semantics.
- This affects only 3 bars in the entire dataset, but the logic must be correct

**Test:** Create a minimal strategy that buys on bar 10 and sells on bar 20.
Verify: fill price == bar 11 open (not bar 10 close), and commission == 7bps of trade value.

### Deliverable 3: Single-Run Engine
**File:** `backtest/engine.py`

A minimal backtest runner for Phase 1A. NOT a walk-forward orchestrator.

**Inputs:**
- Strategy class
- Strategy params dict
- Start date (datetime)
- End date (datetime)
- Whether to write to registry (bool, default True)

**What it does:**
1. Load data via `bt_parquet_feed.py` for the specified date range
2. Configure Cerebro via `execution_model.py`
3. Set initial capital (default $10,000 for baseline testing)
4. Run the strategy
5. Extract trade list and equity curve from Backtrader analyzers
6. Pass results to `metrics.py` for computation
7. Write one row to `experiments.db` if registry write is enabled
8. **Save trade log** to `data/results/trades_{run_id}.csv` containing:
   - `trade_id` — sequential integer
   - `entry_signal_time_utc` — bar N close timestamp (when signal was generated)
   - `entry_time_utc` — bar N+1 open timestamp (**actual fill time**, not signal time)
   - `entry_price` — actual fill price (should equal bar N+1 open)
   - `entry_bar_volume` — volume of the fill bar (must be > 0)
   - `exit_signal_time_utc` — bar M close timestamp (when exit signal was generated)
   - `exit_time_utc` — bar M+1 open timestamp (**actual fill time**)
   - `exit_price` — actual fill price
   - `exit_bar_volume` — volume of the fill bar
   - `size` — position size in base asset
   - `entry_commission` — commission on entry fill
   - `exit_commission` — commission on exit fill
   - `total_commission` — entry_commission + exit_commission
   - `pnl` — profit/loss after commissions
   - `pnl_pct` — percentage return after commissions
   This file is used by both `trade_audit.py` and automated tests.
9. Return a result object with: trades list, equity curve, metrics dict, path to trade CSV

**What it does NOT do (yet):**
- Walk-forward windows (Phase 1B)
- Multiple strategies in one run
- Parameter optimization
- Any form of "platform" abstraction

**Warmup handling (CRITICAL):**
- Each strategy declares its warmup period (number of bars)
- The engine loads data starting from `start_date` but only begins recording metrics
  after `warmup_bars` have passed
- **No trades are allowed during the warmup period**
- Warmup is enforced via Backtrader's native `prenext()`/`next()` split: strategies must
  only emit signals inside `next()`, never in `prenext()`. `prenext()` must remain empty
  or contain only logging. The first eligible signal bar is the first bar where `next()` is called.
- The experiment registry records both `train_start` (data start) and `effective_start`
  (after warmup) so results are auditable
- Metrics (Sharpe, drawdown, etc.) are computed only on the post-warmup period

**Registry semantics for Phase 1A single-run mode:**
- For Phase 1A, the engine's `start_date`/`end_date` map to `test_start`/`test_end` in the registry
- `train_start`, `train_end`, `validation_start`, `validation_end` are set to NULL
- This convention changes in Phase 1B when walk-forward introduces real train/test splits

**Test:** Run with a 50-bar warmup strategy, verify no trades in first 50 bars,
verify metrics exclude the warmup period.

### Deliverable 4: Metrics Module
**File:** `backtest/metrics.py`

Computes metrics from Backtrader results. Core metrics only for Phase 1A:

| Metric | Computation | Notes |
|--------|------------|-------|
| `total_return` | (final_value / initial_value) - 1 | Decimal (0.15 = 15%) |
| `sharpe_ratio` | annualized, assuming hourly returns, rf=0 | `mean(returns) / std(returns) * sqrt(8760)` |
| `max_drawdown` | max peak-to-trough decline in equity curve | Decimal (0.20 = 20%) |
| `max_drawdown_duration_hours` | longest time spent below previous peak | Hours |
| `total_trades` | count of round-trip trades | |
| `win_rate` | winning trades / total trades | Decimal |
| `avg_trade_duration_hours` | mean holding period per trade | |
| `avg_trade_return` | mean return per trade after costs | Decimal |
| `profit_factor` | gross profits / gross losses | >1 means net profitable |

**NOT in Phase 1A:**
- Deflated Sharpe Ratio (requires multiple trials — Phase 1B `evaluate_dsr.py`)
- Rolling Sharpe or rolling drawdown
- Calmar ratio, Sortino ratio (nice-to-have, not core)

**Test:** Compute Sharpe ratio on a known return series and verify against hand calculation.

### Deliverable 5: Experiment Registry Updates
**File:** `backtest/experiment_registry.py` (update from Phase 0)

Add these fields to the `runs` table:

| New Field | Type | Description |
|-----------|------|-------------|
| `run_type` | TEXT | `"single_run"` / `"walk_forward_window"` / `"walk_forward_summary"` |
| `parent_run_id` | TEXT (nullable) | Links walk-forward windows to parent run (NULL for single runs) |
| `effective_start` | TEXT (ISO date) | Start of metrics computation (after warmup) |
| `warmup_bars` | INTEGER | Number of warmup bars declared by strategy |
| `initial_capital` | REAL | Starting capital for the run |
| `final_capital` | REAL | Ending capital |
| `profit_factor` | REAL | Gross profits / gross losses |
| `avg_trade_return` | REAL | Mean per-trade return |

Update `fee_model` convention: use `"effective_7bps_per_side"` for Phase 1A runs.
Do NOT use `"taker_4bps_slip_3bps"` which implies separate fee/slippage modeling.

**Phase 1A logging:** Each engine run produces exactly one row with `run_type = "single_run"`.

### Deliverable 6: Strategy Template
**File:** `strategies/template.py`

Minimal base class. Keep it thin — we don't know what Phase 2 AI strategies will need.

```python
class BaseStrategy(bt.Strategy):
    """Base class for all strategies in the pipeline."""
    
    # Subclasses MUST override these:
    STRATEGY_NAME = "unnamed"
    WARMUP_BARS = 0  # Number of bars before signals are valid
    
    def get_params_dict(self):
        """Return strategy parameters as a serializable dict."""
        ...
    
    def get_metadata(self):
        """Return strategy metadata for registry logging."""
        ...
```

**Responsibilities:**
- Strategy name declaration
- Warmup period declaration
- Parameter serialization for registry
- Metadata (source, version)

**NOT in the template:**
- Signal abstraction layers
- Custom DSL methods
- Position management helpers (let strategies use Backtrader's native API)
- Anything that tries to predict Phase 2 agent patterns

### Deliverable 7: SMA Crossover Baseline
**File:** `strategies/baseline/sma_crossover.py`

The simplest possible trend-following strategy:
- Compute 20-period and 50-period simple moving averages
- Buy when fast SMA crosses above slow SMA (golden cross)
- Sell (close position) when fast SMA crosses below slow SMA (death cross)
- Always fully invested or fully flat (no partial positions)
- `WARMUP_BARS = 50` (slow SMA needs 50 bars to initialize)

**Expected behavior after fees:**
- Modest negative to slightly positive returns on BTC 1h
- Sharpe ratio between -0.5 and 1.5 (roughly)
- If Sharpe > 2.0, the engine probably has a fee or execution bug
- If total trades < 5 over a year, the crossover logic may be wrong
- If total trades > 500 over a year, something is triggering too often

### Deliverable 8: Trade Audit Helper
**File:** `backtest/trade_audit.py`

A human-facing inspection tool for manual trade verification. Reads from the trade log CSV
generated by the engine (`data/results/trades_{run_id}.csv`) and cross-references against
the raw OHLCV data.

```python
def audit_trade(run_id, trade_index, df, context_bars=5):
    """
    Load trade record from data/results/trades_{run_id}.csv,
    cross-reference against raw OHLCV DataFrame,
    print the signal bar, fill bar, surrounding context,
    and fee verification.
    """
```

**Output for each trade:**
- Signal bar: timestamp, OHLCV, what signal was generated
- Fill bar: timestamp, open price (expected fill), actual fill price from trade log
- Price match: does fill price == fill bar open? (YES/NO)
- Commission: expected (7bps * trade value) vs actual deducted
- Context: 5 bars before and after the fill, with source column
- Zero-volume check: was the fill bar a zero-volume bar?

**Usage:**
```bash
python -m backtest.trade_audit --run-id <UUID> --trade-index 0 1 2
```

**Note:** This is a human debugging/reporting tool, NOT part of the automated test suite.
`test_phase1_pipeline.py` asserts against trade records directly.

### Deliverable 9: Simple Momentum Baseline
**File:** `strategies/baseline/momentum.py`

Second baseline to cross-validate the engine:
- Compute N-period return (e.g., 24-bar = 24-hour return)
- Go long when return exceeds threshold (e.g., +2%)
- Go flat when return drops below exit threshold (e.g., 0%)
- `WARMUP_BARS = 24`

This tests different execution patterns than SMA crossover:
- More frequent trading (threshold-based vs crossover-based)
- Different holding periods
- Different signal generation logic

### Deliverable 10: End-to-End Pipeline Test
**File:** `tests/test_phase1_pipeline.py`

Automated test that:
1. Runs SMA crossover through `engine.py` on a fixed date range (2024-01-01 to 2024-06-30)
2. Verifies the run was logged to `experiments.db`
3. Verifies all required fields are populated (non-NULL where expected)
4. Verifies `run_type == "single_run"`
5. Verifies `fee_model == "effective_7bps_per_side"`
6. Verifies `warmup_bars == 50`
7. Verifies `effective_start` is 50 bars after `test_start`
8. Verifies `total_trades > 0`
9. Verifies `sharpe_ratio` is a finite number (not NaN/Inf)
10. Reads `data/results/trades_{run_id}.csv` directly, loads raw OHLCV data, and verifies
    for the first trade: `entry_price == raw_df.loc[entry_time_utc, 'open']` (confirming
    that `entry_time_utc` is the actual fill bar and fill price matches that bar's open)

**Note:** This test asserts against trade records and raw data directly. It does NOT
shell out to `trade_audit.py`, which is a human-facing inspection tool.

---

## Phase 1B Deliverables (After 1A Sign-Off)

### Deliverable 11: Walk-Forward Wrapper
**File:** `backtest/engine.py` (extend)

Adds walk-forward mode to the engine:
- Read rolling window config from `environments.yaml`
- For each window: run single-run engine, collect results
- Create one `walk_forward_window` row per window in registry
- Create one `walk_forward_summary` row with aggregate metrics
- Link via `parent_run_id`

### Deliverable 12: Post-Hoc DSR Evaluation
**File:** `backtest/evaluate_dsr.py`

Standalone script that:
- Queries `experiments.db` for all runs matching a `split_version`
- Extracts Sharpe ratios
- Computes Deflated Sharpe Ratio: adjusts significance threshold based on number of trials
- Reports which strategies survive the DSR filter

### Deliverable 13: Additional Baselines (Optional)
**Files:** `strategies/baseline/volatility_breakout.py`, `strategies/baseline/mean_reversion.py`

Only if needed for further engine validation. These are not required for Phase 1 sign-off.

---

## Execution Order for Claude Code

### Phase 1A (implement in this exact order, stop after each for review):

1. `backtest/bt_parquet_feed.py` — test: load data, verify prices match
2. `backtest/execution_model.py` + `backtest/slippage.py` — test: minimal buy/sell strategy,
   verify fill prices and fees
3. `backtest/engine.py` (single-run mode only) — test: run on fixed date range, get result object
4. `backtest/metrics.py` — test: verify Sharpe against hand calculation
5. `backtest/experiment_registry.py` (add new fields) — test: verify schema, insert, query
6. `strategies/template.py` — minimal base class
7. `strategies/baseline/sma_crossover.py` — run on 2024-01-01 to 2024-12-31
8. `backtest/trade_audit.py` — audit first 3 trades from SMA run
9. **HUMAN: Manual trade audit — go/no-go gate for Phase 1A**
10. `strategies/baseline/momentum.py` — second baseline to cross-validate
11. `tests/test_phase1_pipeline.py` — automated end-to-end test

### Phase 1B (only after 1A sign-off):

12. Walk-forward wrapper in `engine.py`
13. `backtest/evaluate_dsr.py`
14. Additional baselines if needed

---

## Manual Trade Audit Procedure

This is the most important validation step in Phase 1A.

After Deliverable 8 (trade_audit.py) is built and SMA crossover has been run:

1. **Select 3 trades:** First trade, a mid-run trade, and the last trade
2. **For each trade, verify:**
   - Open the raw Parquet data around the trade timestamp
   - Confirm the signal bar: was the SMA crossover condition true at this bar's close?
   - Confirm the fill bar: is it exactly 1 bar later?
   - Confirm fill price: does it match the fill bar's `open` price exactly?
   - Confirm commission: is 7bps of trade value deducted?
   - Confirm the fill bar has `volume > 0`
3. **If ANY trade fails verification:** Stop. Debug the execution model before proceeding.
4. **If all trades pass:** Phase 1A sign-off criteria #4 is met.

**Time estimate:** 15-20 minutes with the audit helper tool.

---

## Implementation Notes for Claude Code

### Backtrader Configuration Checklist
- `cerebro.broker.set_coc(False)` — no cheat-on-close
- `cerebro.broker.set_coo(False)` — no cheat-on-open  
- `cerebro.broker.setcommission(commission=0.0007)` — 7bps per side
- `cerebro.broker.setcash(10000)` — default starting capital
- `cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)` — trade statistics
- `cerebro.addanalyzer(bt.analyzers.DrawDown)` — drawdown tracking

### Common Backtrader Pitfalls
- `self.data.close[0]` is the CURRENT bar's close (bar N)
- `self.data.open[0]` is the CURRENT bar's open (bar N) — NOT the next bar
- `self.buy()` submits a market order that fills at NEXT bar's open
- `self.data.datetime.datetime(0)` returns a naive datetime — convert to UTC
- Backtrader's `PandasData` feed expects the DataFrame index to be datetime
- If `fromdate`/`todate` are timezone-naive, Backtrader may misalign with UTC data

### File Dependencies
```
bt_parquet_feed.py    → depends on: data/raw/btcusdt_1h.parquet
execution_model.py    → depends on: config/execution.yaml
slippage.py           → depends on: config/execution.yaml
engine.py             → depends on: bt_parquet_feed, execution_model, metrics, experiment_registry
                        outputs to: experiments.db, data/results/trades_{run_id}.csv
metrics.py            → depends on: (standalone, no project deps)
experiment_registry.py → depends on: config/environments.yaml, config/execution.yaml, config/schemas.yaml
template.py           → depends on: (standalone Backtrader base class)
sma_crossover.py      → depends on: template.py
trade_audit.py        → depends on: data/results/trades_{run_id}.csv, data/raw/btcusdt_1h.parquet
momentum.py           → depends on: template.py
test_phase1_pipeline  → depends on: engine.py, data/results/trades_{run_id}.csv, experiments.db
```
