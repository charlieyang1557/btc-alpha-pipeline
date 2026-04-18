# BTC Alpha Pipeline — Phase 0 Blueprint

## Project Overview

A single-person quantitative research system for discovering, validating, and eventually live-trading algorithmic strategies on BTC markets. The system is designed to eventually incorporate AI agents (LLM-driven hypothesis generation + strategy mining), but Phase 0 focuses exclusively on building the foundational data and backtesting infrastructure.

**Deployment:** Mac Mini (username: `openclaw`) as production server, MacBook Air (username: `yutianyang`) for development.
**Capital scope:** $500-1000 initial live capital (Phase 5+, not yet).
**Primary asset:** BTC/USDT perpetual futures and spot on Binance.

---

## Phase 0 Scope (This Sprint)

Phase 0 builds the minimum infrastructure required to run a correct, reproducible backtest. Nothing more.

### Deliverables (in order):

1. `config/execution.yaml` — Bar execution convention, fee/slippage defaults
2. `config/environments.yaml` — Immutable train/validation/test date splits
3. `config/schemas.yaml` — Required columns, dtypes, primary keys for all data
4. `CLAUDE.md` — Project context + hard constraints for Claude Code
5. `data_dictionary.md` — Schema documentation for all data tables
6. `ingestion/bulk_download.py` — Historical BTC 1h data from Binance Vision
7. `ingestion/validators.py` — Data quality checks (gaps, dupes, partial candles, zero-volume)
8. `ingestion/incremental_update.py` — CCXT-based daily update with exponential backoff
9. `ingestion/reconcile.py` — Archive + API merge, dedup, continuity verification
10. `backtest/experiment_registry.py` — SQLite experiment registry (create + insert + query)
11. `pyproject.toml` — Dependency pinning
12. `requirements.txt` — Flat dependency list (fallback)

### Explicitly NOT in Phase 0:
- Backtrader engine (Phase 1)
- Strategy code of any kind (Phase 1)
- Factor/feature computation (Phase 2)
- AI agents (Phase 2+)
- Paper trading (Phase 4)
- Live trading (Phase 5)
- Docker, TimescaleDB, advanced slippage models
- Any form of "platform" or "framework" abstraction

---

## Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11+ | Ecosystem compatibility |
| Data storage (research) | Parquet files | Fast columnar reads, zero infra |
| Data storage (experiments) | SQLite | Lightweight, queryable, no server |
| Data ingestion (bulk) | Binance Vision CSV archives | Avoids REST API rate limits |
| Data ingestion (incremental) | CCXT (Binance) | Unified exchange API, built-in rate limiter |
| Backtesting (Phase 1) | Backtrader | Event-driven, LLM-friendly `next()` paradigm |
| Quick factor scanning | vectorbt (optional) | Vectorized speed for simple screens |
| AI (future) | Claude API (Sonnet + Haiku) | Strategy generation + hypothesis screening |
| Dependency management | pyproject.toml + uv/pip | Modern, lockable |

---

## Project Directory Structure

```
btc-alpha-pipeline/
├── CLAUDE.md                        # Project context + hard constraints for Claude Code
├── data_dictionary.md               # Schema docs for all data
├── pyproject.toml                   # Dependencies
├── requirements.txt                 # Flat fallback
├── .python-version                  # Pin Python version
├── config/
│   ├── execution.yaml               # Bar execution convention, fees, slippage
│   ├── environments.yaml            # Immutable train/val/test date splits
│   └── schemas.yaml                 # Column specs, dtypes, primary keys
├── data/
│   ├── raw/                         # Canonical current OHLCV parquet files
│   │   ├── btcusdt_1h.parquet       # Primary dataset (overwritten on reconcile)
│   │   └── archive/                 # Pre-reconcile snapshots (btcusdt_1h_YYYYMMDDTHHMMSSZ.parquet)
│   ├── features/                    # Precomputed factors (Phase 2)
│   └── quality/                     # Validation reports (auto-generated)
├── ingestion/
│   ├── bulk_download.py             # Binance Vision historical pull
│   ├── incremental_update.py        # CCXT daily update with backoff
│   ├── reconcile.py                 # Archive + API merge/dedup
│   └── validators.py                # Gap detection, price sanity, schema checks
├── backtest/
│   ├── engine.py                    # Backtrader walk-forward harness (Phase 1)
│   ├── bt_parquet_feed.py           # Backtrader <-> Parquet adapter (Phase 1)
│   ├── execution_model.py           # Execution convention enforcement (Phase 1)
│   ├── slippage.py                  # SlippageModel base + constant model (Phase 1)
│   ├── metrics.py                   # DSR, Sharpe, drawdown calculations (Phase 1)
│   ├── experiment_registry.py       # SQLite experiment tracking
│   └── experiments.db               # SQLite database (auto-created)
├── factors/                         # Phase 2
│   ├── registry.py
│   ├── technical.py
│   └── build_features.py
├── strategies/                      # Phase 1+
│   ├── baseline/
│   ├── ai_generated/
│   └── template.py
├── agents/                          # Phase 2+
│   ├── researcher.py
│   ├── cynic.py
│   └── miner.py
├── risk/                            # Phase 3+
│   └── allocator.py
├── paper_trading/                   # Phase 4
│   ├── simulator.py
│   ├── state.db
│   └── results/
└── live/                            # Phase 5+
    └── README.md
```

---

## Data Schema

### Raw OHLCV (btcusdt_1h.parquet)

| Column | Type | Description |
|--------|------|-------------|
| `open_time_utc` | datetime64[ms, UTC] | Candle open time, **PRIMARY KEY**, always UTC timezone-aware |
| `open` | float64 | Open price (USDT) |
| `high` | float64 | High price (USDT) |
| `low` | float64 | Low price (USDT) |
| `close` | float64 | Close price (USDT) |
| `volume` | float64 | Base asset volume (BTC) |
| `quote_volume` | float64 | Quote asset volume (USDT) |
| `trade_count` | int64 | Number of trades in candle |
| `ingested_at_utc` | datetime64[ms, UTC] | When this row was ingested |
| `source` | string | "binance_vision" or "ccxt_api" |

**Constraints:**
- `open_time_utc` is unique (no duplicates)
- Consecutive rows must differ by exactly 3600000ms (1 hour)
- All prices > 0
- `high` >= max(`open`, `close`) and `low` <= min(`open`, `close`)
- Volume >= 0

### Experiment Registry (experiments.db)

Single table: `runs`

| Column | Type | Description |
|--------|------|-------------|
| `run_id` | TEXT PRIMARY KEY | UUID |
| `strategy_name` | TEXT | e.g., "sma_crossover_20_50" |
| `strategy_source` | TEXT | "manual" / "ai_generated" / "mutated_from_X" |
| `git_commit` | TEXT | Short SHA of current commit |
| `config_hash` | TEXT | SHA256 of execution.yaml + environments.yaml + schemas.yaml |
| `data_snapshot_date` | TEXT | Date of last data update used |
| `feature_version` | TEXT | e.g., "v1" or "none" (Phase 0) |
| `split_version` | TEXT | e.g., "v1" — from environments.yaml version field |
| `train_start` | TEXT | ISO date |
| `train_end` | TEXT | ISO date |
| `validation_start` | TEXT | ISO date (NULL if not used) |
| `validation_end` | TEXT | ISO date (NULL if not used) |
| `test_start` | TEXT | ISO date |
| `test_end` | TEXT | ISO date |
| `total_return` | REAL | Decimal (0.15 = 15%) |
| `sharpe_ratio` | REAL | Annualized |
| `max_drawdown` | REAL | Decimal (0.20 = 20%) |
| `total_trades` | INTEGER | |
| `win_rate` | REAL | Decimal |
| `avg_trade_duration_hours` | REAL | |
| `fee_model` | TEXT | e.g., "taker_4bps_slip_3bps" |
| `notes` | TEXT | Free text |
| `review_status` | TEXT | "pending" / "approved" / "rejected" |
| `review_reason` | TEXT | Why approved/rejected |
| `created_at_utc` | TEXT | ISO timestamp |

---

## Validation Rules (validators.py)

The validator must check ALL of the following and produce a structured report:

### Timestamp Integrity
- [ ] All `open_time_utc` values are timezone-aware UTC
- [ ] No duplicate `open_time_utc` values
- [ ] No gaps: consecutive rows differ by exactly 1 hour
- [ ] If gaps exist, report exact missing intervals
- [ ] No partial candle at end of dataset (last candle must be complete)
- [ ] Timestamps align to exact hour boundaries (minute=0, second=0)

### Price Integrity
- [ ] All OHLC prices > 0
- [ ] `high` >= `open` and `high` >= `close` for every row
- [ ] `low` <= `open` and `low` <= `close` for every row
- [ ] No single-bar price change exceeds 50% (flag as anomaly, don't auto-remove)
- [ ] No price is exactly 0.0

### Volume Integrity
- [ ] Volume >= 0 for all rows
- [ ] Flag zero-volume bars (do NOT auto-remove; log to quality report)
- [ ] Flag bars where volume drops >95% vs rolling 24h median (possible partial)

### Schema Integrity
- [ ] All required columns present with correct dtypes
- [ ] No null/NaN values in core market fields (open, high, low, close, volume, quote_volume, trade_count)
- [ ] `source` column populated for every row

### Reconciliation Checks (reconcile.py)
- [ ] After merging archive + API data: no duplicate `open_time_utc`
- [ ] Overlap period between archive and API: prices match within 0.01%
- [ ] Final dataset is sorted by `open_time_utc` ascending
- [ ] Row count matches expected hours between first and last timestamp

---

## Ingestion Specifications

### bulk_download.py
1. Download BTC/USDT 1h kline CSVs from `https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1h/`
2. Parse all monthly ZIP files from 2020-01 to latest available
3. Concatenate, rename columns to match schema
4. Add `source = "binance_vision"` and `ingested_at_utc = now()`
5. Ensure `open_time_utc` is timezone-aware UTC (Binance provides ms timestamps)
6. Run validators.py on result
7. Save to `data/raw/btcusdt_1h.parquet`
8. Save validation report to `data/quality/bulk_validation_YYYYMMDD.json`

### incremental_update.py
1. Read existing `data/raw/btcusdt_1h.parquet`
2. Find latest `open_time_utc`
3. Use CCXT to fetch candles from (latest + 1h) to now
4. Enable CCXT built-in rate limiter: `ccxt.binance({'enableRateLimit': True})`
5. Add custom exponential backoff ONLY for `ccxt.NetworkError` or `ccxt.RateLimitExceeded`: start 1s, max 60s, max retries 5
6. Add `source = "ccxt_api"` and `ingested_at_utc = now()`
7. Pass new rows through validators.py
8. Call reconcile.py to merge

### reconcile.py
1. Load existing parquet + new rows
2. **Archive the current canonical file** to `data/raw/archive/btcusdt_1h_YYYYMMDDTHHMMSSZ.parquet` before any modification
3. Concat and sort by `open_time_utc`
4. Deduplicate on `open_time_utc` (keep `binance_vision` source if conflict)
5. Verify no gaps in final dataset
6. Remove any partial candle at the very end (if last candle open_time + 1h > current time)
7. Save merged result as the new canonical file: `data/raw/btcusdt_1h.parquet`
8. Log reconciliation stats: rows_before, rows_added, rows_deduped, gaps_found

---

## Phase 1 Preview (For Context Only — Not Built in Phase 0)

Phase 1 builds the Backtrader walk-forward engine and runs baseline strategies.

**Baseline strategies (intentionally simple):**
- SMA crossover (20/50)
- Simple momentum (N-day return threshold)
- Mean reversion on z-score
- Volatility breakout (Bollinger band)

**Purpose of baselines:** Validate the pipeline, not generate alpha. If SMA crossover shows Sharpe > 3.0, your pipeline has a bug.

**Backtrader-Parquet adapter:** A custom `bt.feeds.PandasData` subclass that loads Parquet → DataFrame → Backtrader feed, mapping columns correctly.

---

## Implementation Notes for Claude Code

When implementing Phase 0, follow this exact order:
1. Create project structure (all directories)
2. Write config files (execution.yaml, environments.yaml, schemas.yaml)
3. Write CLAUDE.md and data_dictionary.md
4. Write validators.py (test with synthetic data)
5. Write bulk_download.py (test with 1 month of data first)
6. Write incremental_update.py
7. Write reconcile.py
8. Write experiment_registry.py
9. Write pyproject.toml
10. Run full pipeline: download → validate → reconcile → verify
11. Commit everything with descriptive messages

Every script must:
- Have a `if __name__ == "__main__"` block with argparse
- Support `--dry-run` flag where applicable
- Log to stdout with timestamps
- Return non-zero exit code on failure
- Include docstrings on all functions
