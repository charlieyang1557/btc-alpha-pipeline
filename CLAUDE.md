# CLAUDE.md — BTC Alpha Pipeline

## What This Project Is

A single-person quantitative research system for BTC algorithmic trading strategies.
Built in phases: data infrastructure → backtesting → AI-assisted strategy mining → paper trading → live.
Currently in **Phase 1A**: building and validating the single-run backtesting engine.
Phase 0 (data infrastructure) is complete — validated BTC 1h data from 2020-01 onward.

## Tech Stack

- **Python 3.11+** with dependencies pinned in `pyproject.toml`
- **Parquet** for all time-series market data (research layer)
- **SQLite** for experiment registry and paper trading state (operational layer)
- **CCXT** for exchange API access (incremental data updates, future live trading)
- **Binance Vision** for bulk historical data download
- **Backtrader 1.9.78+** for event-driven backtesting (active in Phase 1)
- **scipy** for statistical computations (Sharpe ratio, etc.)
- **matplotlib** for equity curve visualization (optional, debugging only)
- **Claude API** (Sonnet for generation, Haiku for screening) for AI agents (Phase 2+)

## Project Structure

```
btc-alpha-pipeline/
├── config/              # Execution conventions, date splits, schemas (IMMUTABLE by agents)
├── data/raw/            # Canonical current OHLCV parquet (archive/ holds snapshots)
├── data/raw/archive/    # Pre-reconcile snapshots for reproducibility
├── data/features/       # Precomputed factors (Phase 2)
├── data/quality/        # Auto-generated validation reports
├── ingestion/           # Download, update, reconcile, validate scripts
├── backtest/            # Engine, metrics, experiment registry, trade audit
│   ├── bt_parquet_feed.py      # Parquet → Backtrader data adapter
│   ├── execution_model.py      # Reads execution.yaml, configures Cerebro
│   ├── slippage.py             # SlippageModel (effective 7bps for Phase 1)
│   ├── engine.py               # Single-run harness (Phase 1A), walk-forward (Phase 1B)
│   ├── metrics.py              # Sharpe, drawdown, trade stats
│   ├── trade_audit.py          # Manual trade verification helper
│   ├── experiment_registry.py  # SQLite experiment tracking
│   └── experiments.db          # Auto-populated by engine
├── strategies/          # Manual baselines + AI-generated (Phase 1+)
│   ├── template.py             # Base strategy class
│   └── baseline/               # SMA crossover, momentum, etc.
├── factors/             # Feature computation (Phase 2)
├── agents/              # AI hypothesis + strategy generation (Phase 2+)
├── risk/                # Position sizing and capital allocation (Phase 3+)
├── paper_trading/       # Simulated live execution (Phase 4)
├── tests/               # Automated test suite
└── live/                # Real money execution (Phase 5+)
```

## Document Conflict Priority

If any two documents in this project contradict each other, resolve by this hierarchy (highest priority first):

1. **`config/execution.yaml`** — execution semantics and fee assumptions
2. **`config/environments.yaml`** — date splits and research discipline
3. **`config/schemas.yaml`** — column definitions and validation rules
4. **`CLAUDE.md`** (this file) — hard constraints and prohibitions
5. **`data_dictionary.md`** — human-readable schema reference
6. **`PHASE1_BLUEPRINT.md`** — Phase 1 implementation plan (current phase)
7. **`PHASE0_BLUEPRINT.md`** — Phase 0 reference (completed)

Structured config files are the machine-readable source of truth. This file governs behavior and prohibitions but does not outrank the actual config values. If you encounter a conflict, follow the higher-priority document and flag the inconsistency in a code comment.

## Execution Convention (CRITICAL — READ BEFORE WRITING ANY STRATEGY CODE)

All backtests in this project follow these rules without exception:

1. **Signal timing:** Signals are computed using data available at bar N's close.
2. **Execution timing:** Orders execute at bar N+1's open price. NEVER at bar N's close.
3. **No same-bar execution:** A strategy CANNOT observe a bar's close and execute at that same bar's close. This is look-ahead bias.
4. **Cost model (Phase 1):** Effective cost = **7bps per side** (14bps round trip). This is a simplification of 4bps taker fee + 3bps slippage. Do NOT treat this as a realistic execution simulator — it is an effective cost model for baseline validation. The `fee_model` registry field must be `"effective_7bps_per_side"`.
5. **Stop/limit orders within a bar:** If both stop-loss and take-profit would trigger within the same OHLCV bar, assume the adverse one triggers first (conservative).
6. **Zero-volume fill deferral:** If the designated fill bar has `volume == 0`, defer execution to the next bar with `volume > 0`, using that bar's open price. If deferral exceeds 24 bars (24 hours), cancel the order entirely.
7. **All times are UTC.** No exceptions. No implicit local timezone conversions.

These rules are defined in `config/execution.yaml` and enforced by `backtest/execution_model.py`.

## Backtrader-Specific Rules (Phase 1)

### Cerebro Configuration (MUST be set for every backtest run)
- `cerebro.broker.set_coc(False)` — disable cheat-on-close
- `cerebro.broker.set_coo(False)` — disable cheat-on-open
- `cerebro.broker.setcommission(commission=0.0007)` — 7bps per side effective cost
- `cerebro.broker.setcash(10000)` — default starting capital

### Common Pitfalls (Claude Code MUST avoid these)
- `self.data.close[0]` is the CURRENT bar's close — NOT the next bar's
- `self.buy()` submits a market order that fills at the NEXT bar's open — this is correct behavior, do not try to "fix" it
- `self.data.datetime.datetime(0)` returns a **naive** datetime — always convert to UTC when comparing with our data
- Backtrader's `PandasData` feed expects the DataFrame index to be datetime — set index before passing
- If `fromdate`/`todate` are timezone-naive, Backtrader may misalign with our UTC data — always use timezone-aware datetime objects
- Backtrader indicators (SMA, etc.) are **bar-based, not time-based** — a 24-period SMA averages the last 24 rows regardless of time gaps between them. This is acceptable for Phase 1 baselines (31 gaps in 55K bars is negligible) but must be documented.

### Warmup Handling
- Each strategy declares `WARMUP_BARS` (number of bars before signals are valid)
- The engine loads data from `start_date` but only begins recording metrics after warmup
- **No trades are allowed during the warmup period**
- Strategies must only emit signals inside Backtrader's `next()` method, NEVER in `prenext()`
- `prenext()` runs while indicators are still warming up — it must remain empty or contain only logging
- The first eligible signal bar is the first bar where `next()` is called
- The first eligible fill is the bar after that signal
- The experiment registry records both `train_start` (data start) and `effective_start` (after warmup)
- Metrics (Sharpe, drawdown, etc.) are computed ONLY on the post-warmup period
- If a strategy attempts to trade during warmup, the engine must block it

## Timestamp & Timezone Rules

- **ALL timestamps in code, data, logs, and configs are UTC.**
- Parquet columns: use timezone-aware `datetime64[ms, UTC]`.
- SQLite columns: store as ISO 8601 strings with `Z` suffix (e.g., `2024-01-15T08:00:00Z`).
- Column naming convention: all time columns end in `_utc` (e.g., `open_time_utc`, `ingested_at_utc`, `created_at_utc`).
- Python code: always use `datetime.now(timezone.utc)`, NEVER `datetime.now()` or `datetime.utcnow()`.
- Pandas: when reading timestamps, always pass `utc=True` or explicitly localize with `.dt.tz_localize('UTC')`.
- **NEVER mix timezone-aware and timezone-naive datetimes.** This will silently corrupt data joins and backtest alignment.

## Data Rules

- `data/raw/btcusdt_1h.parquet` is the **canonical current dataset**. It is overwritten by `reconcile.py` after each update.
- Before overwriting, `reconcile.py` MUST archive the previous version to `data/raw/archive/btcusdt_1h_YYYYMMDDTHHMMSSZ.parquet`.
- Raw data is NEVER modified by any process other than `reconcile.py`. Strategies, agents, and analysis scripts read only.
- `open_time_utc` is the primary key for all OHLCV data. It must be unique and sorted ascending.
- Zero-volume bars are flagged in validation reports but NOT auto-removed. They may indicate exchange downtime or data-quality issues.
- Missing bars (gaps) are flagged but NOT auto-interpolated. Forward-filling is PROHIBITED.
- All data files include `source` ("binance_vision", "ccxt_binance", or "ccxt_binanceus") and `ingested_at_utc` columns.

## Experiment Tracking

- Every backtest run MUST be logged in `backtest/experiments.db` (SQLite).
- Required fields per run: `run_id`, `run_type`, `parent_run_id`, `strategy_name`, `git_commit`, `config_hash`, `split_version`, `data_snapshot_date`, `train_start`, `train_end`, `effective_start`, `warmup_bars`, `validation_start`, `validation_end`, `test_start`, `test_end`, `initial_capital`, `final_capital`, core metrics, `fee_model`.
- `run_type` must be one of: `"single_run"`, `"walk_forward_window"`, `"walk_forward_summary"`
- `fee_model` for Phase 1: `"effective_7bps_per_side"` — do NOT use labels that imply separate fee/slippage modeling
- The experiment registry is the system of record for all research results.
- **Phase 1A single-run mode:** `test_start`/`test_end` map to the engine's date range. `train_start`, `train_end`, `validation_start`, `validation_end` are NULL. This convention changes in Phase 1B when walk-forward introduces real train/test splits.

## Date Split Rules

- Train/validation/test date boundaries are defined in `config/environments.yaml`.
- These boundaries are IMMUTABLE during a research phase.
- Strategies may ONLY be trained/optimized on data within the training window.
- Validation data is for hyperparameter selection and early stopping only.
- Test data is touched ONCE for final evaluation. If you peek and iterate, it becomes validation data.

---

## HARD CONSTRAINTS — THINGS CLAUDE CODE MUST NEVER DO

These are non-negotiable rules. Violating any of these invalidates research results.

### Data Integrity
- ❌ NEVER modify `config/environments.yaml` (date splits are immutable)
- ❌ NEVER modify `config/execution.yaml` without explicit human approval
- ❌ NEVER write to `data/raw/btcusdt_1h.parquet` from any script other than `reconcile.py`
- ❌ NEVER forward-fill missing bars or interpolate prices
- ❌ NEVER silently drop or filter rows from raw data
- ❌ NEVER auto-remove zero-volume bars (flag only)

### Execution Integrity
- ❌ NEVER assume same-bar execution (signal on close, execute on same close)
- ❌ NEVER hardcode transaction costs in strategy code — read from execution.yaml
- ❌ NEVER write strategies that access future data (no `shift(-1)` on price data for signals)
- ❌ NEVER use test-set performance to modify strategy parameters
- ❌ NEVER set `cheat_on_close=True` or `cheat_on_open=True` in Backtrader Cerebro
- ❌ NEVER fill orders on zero-volume bars — defer to next valid bar
- ❌ NEVER allow trades during the warmup period
- ❌ NEVER compute metrics (Sharpe, drawdown, etc.) including the warmup period
- ❌ NEVER use Backtrader's naive datetimes without converting to UTC for comparisons

### Code Quality
- ❌ NEVER generate a factor/indicator function without a docstring specifying: inputs, computation method, warmup period, and output schema
- ❌ NEVER skip validation steps when ingesting or updating data
- ❌ NEVER commit code that doesn't pass existing tests

### Library Policy
**Approved core libraries (Phase 0-1):** pandas, numpy, pyarrow, ccxt, requests, pyyaml, backtrader, scipy, matplotlib, and Python stdlib modules (sqlite3, pathlib, argparse, logging, hashlib, datetime, json, zipfile, io, uuid, typing).

**Phase 2+:** anthropic (Claude API)

Any library not listed above requires explicit human approval before use. Standard typing/testing utilities (e.g., `dataclasses`, `typing_extensions`, `pytest`) are allowed without approval.

---

## Coding Standards

- All scripts have `if __name__ == "__main__"` with argparse
- All scripts support `--dry-run` where applicable
- All scripts log to stdout with ISO 8601 UTC timestamps
- All functions have type hints and docstrings
- All data-modifying operations are logged (what changed, row counts before/after)
- Non-zero exit code on any validation failure
- Use `pathlib.Path` for all file paths, never string concatenation
- Config loading: use a shared utility that reads YAML once and passes as dict

## Running the Pipeline

```bash
# Phase 0: Data management
python -m ingestion.bulk_download --pair BTCUSDT --interval 1h --start 2020-01
python -m ingestion.validators --file data/raw/btcusdt_1h.parquet --report data/quality/
python -m ingestion.incremental_update --pair BTCUSDT --interval 1h
python -m ingestion.reconcile --existing data/raw/btcusdt_1h.parquet --new data/raw/btcusdt_1h_update.parquet

# Phase 1A: Single-run backtesting
python -m backtest.engine --strategy sma_crossover --start 2024-01-01 --end 2024-12-31
python -m backtest.trade_audit --run-id <UUID> --trade-index 0 1 2
python -m backtest.experiment_registry --action list
python -m backtest.experiment_registry --action stats

# Phase 1B: Walk-forward (after Phase 1A sign-off)
python -m backtest.engine --strategy sma_crossover --mode walk-forward
python -m backtest.evaluate_dsr --split-version v1
```

## Known Data Characteristics

The canonical dataset (`data/raw/btcusdt_1h.parquet`) has these stable, verified properties:
- Dataset begins at **2020-01-01 00:00 UTC** and is extended via incremental CCXT updates
- **31 known missing hours** across 15 gap windows, all in 2020-2023 (historical exchange outages, verified stable across rebuilds)
- **3 known zero-volume bars** (2020-12-21, 2021-02-11, 2023-03-24) — all adjacent to gaps, all have O=H=L=C (frozen price)
- In currently validated snapshots, no gaps or zero-volume bars have been observed from 2024 onward
- All timestamps are UTC-aware and hour-aligned
- Exact row counts and source coverage boundaries change with each incremental update — check validation reports in `data/quality/` for current snapshot details
