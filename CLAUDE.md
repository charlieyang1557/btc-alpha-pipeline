# CLAUDE.md — BTC Alpha Pipeline

## What This Project Is

A single-person quantitative research system for BTC algorithmic trading strategies.
Built in phases: data infrastructure → backtesting → AI-assisted strategy mining → paper trading → live.
Currently in **Phase 0**: building the foundational data pipeline and experiment tracking.

## Tech Stack

- **Python 3.11+** with dependencies pinned in `pyproject.toml`
- **Parquet** for all time-series market data (research layer)
- **SQLite** for experiment registry and paper trading state (operational layer)
- **CCXT** for exchange API access (incremental data updates, future live trading)
- **Binance Vision** for bulk historical data download
- **Backtrader** for event-driven backtesting (Phase 1+)
- **Claude API** (Sonnet for generation, Haiku for screening) for AI agents (Phase 2+)

## Project Structure

```
btc-alpha-pipeline/
├── config/           # Execution conventions, date splits, schemas (IMMUTABLE by agents)
├── data/raw/         # Canonical current OHLCV parquet (archive/ holds snapshots)
├── data/raw/archive/ # Pre-reconcile snapshots for reproducibility
├── data/features/    # Precomputed factors (Phase 2)
├── data/quality/     # Auto-generated validation reports
├── ingestion/        # Download, update, reconcile, validate scripts
├── backtest/         # Engine, metrics, experiment registry (Phase 1+)
├── factors/          # Feature computation (Phase 2)
├── strategies/       # Manual baselines + AI-generated (Phase 1+)
├── agents/           # AI hypothesis + strategy generation (Phase 2+)
├── risk/             # Position sizing and capital allocation (Phase 3+)
├── paper_trading/    # Simulated live execution (Phase 4)
└── live/             # Real money execution (Phase 5+)
```

## Document Conflict Priority

If any two documents in this project contradict each other, resolve by this hierarchy (highest priority first):

1. **`config/execution.yaml`** — execution semantics and fee assumptions
2. **`config/environments.yaml`** — date splits and research discipline
3. **`config/schemas.yaml`** — column definitions and validation rules
4. **`CLAUDE.md`** (this file) — hard constraints and prohibitions
5. **`data_dictionary.md`** — human-readable schema reference
6. **`PHASE0_BLUEPRINT.md`** — implementation plan and specifications

Structured config files are the machine-readable source of truth. This file governs behavior and prohibitions but does not outrank the actual config values. If you encounter a conflict, follow the higher-priority document and flag the inconsistency in a code comment.

## Execution Convention (CRITICAL — READ BEFORE WRITING ANY STRATEGY CODE)

All backtests in this project follow these rules without exception:

1. **Signal timing:** Signals are computed using data available at bar N's close.
2. **Execution timing:** Orders execute at bar N+1's open price. NEVER at bar N's close.
3. **No same-bar execution:** A strategy CANNOT observe a bar's close and execute at that same bar's close. This is look-ahead bias.
4. **Default fees:** Taker fee = 4bps per side (8bps round trip). Configurable in `config/execution.yaml`.
5. **Default slippage:** 3bps per side. Configurable in `config/execution.yaml`.
6. **Stop/limit orders within a bar:** If both stop-loss and take-profit would trigger within the same OHLCV bar, assume the adverse one triggers first (conservative).
7. **All times are UTC.** No exceptions. No implicit local timezone conversions.

These rules are defined in `config/execution.yaml` and enforced by `backtest/execution_model.py`.

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
- All data files include `source` ("binance_vision" or "ccxt_api") and `ingested_at_utc` columns.

## Experiment Tracking

- Every backtest run MUST be logged in `backtest/experiments.db` (SQLite).
- Required fields per run: `run_id`, `strategy_name`, `git_commit`, `config_hash`, `split_version`, `data_snapshot_date`, `train_start`, `train_end`, `validation_start`, `validation_end`, `test_start`, `test_end`, core metrics.
- The experiment registry is the system of record for all research results.

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

### Code Quality
- ❌ NEVER generate a factor/indicator function without a docstring specifying: inputs, computation method, warmup period, and output schema
- ❌ NEVER skip validation steps when ingesting or updating data
- ❌ NEVER commit code that doesn't pass existing tests

### Library Policy
**Approved core libraries (Phase 0):** pandas, numpy, pyarrow, ccxt, requests, pyyaml, and Python stdlib modules (sqlite3, pathlib, argparse, logging, hashlib, datetime, json, zipfile, io, uuid, typing).

**Phase 1+:** backtrader, vectorbt, scipy, matplotlib
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
# Phase 0: Initial data load
python -m ingestion.bulk_download --pair BTCUSDT --interval 1h --start 2020-01
python -m ingestion.validators --file data/raw/btcusdt_1h.parquet --report data/quality/
python -m ingestion.incremental_update --pair BTCUSDT --interval 1h
python -m ingestion.reconcile --existing data/raw/btcusdt_1h.parquet --new data/raw/btcusdt_1h_update.parquet

# Check experiment registry
python -m backtest.experiment_registry --action list
python -m backtest.experiment_registry --action stats
```
