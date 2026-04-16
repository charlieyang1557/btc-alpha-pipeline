# Data Dictionary — BTC Alpha Pipeline

## Overview

This document describes all data tables, columns, and conventions used in the project.
It serves as the authoritative reference for both human developers and AI agents (Claude Code).

**Golden rule:** If a column name, dtype, or convention is not documented here, it does not exist in the project.

---

## 1. Raw OHLCV Data

**File:** `data/raw/btcusdt_1h.parquet`
**Granularity:** 1-hour candles
**Asset:** BTC/USDT (Binance spot)
**History:** 2020-01-01 to present
**Primary key:** `open_time_utc`

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `open_time_utc` | datetime64[ms, UTC] | 2024-01-15 08:00:00+00:00 | Candle open time. Always UTC. Always hour-aligned. |
| `open` | float64 | 42850.50 | Opening price in USDT |
| `high` | float64 | 43100.00 | Highest price during the hour |
| `low` | float64 | 42800.25 | Lowest price during the hour |
| `close` | float64 | 43050.75 | Closing price in USDT |
| `volume` | float64 | 1234.567 | BTC volume traded |
| `quote_volume` | float64 | 53000000.00 | USDT volume traded |
| `trade_count` | int64 | 45000 | Number of individual trades |
| `ingested_at_utc` | datetime64[ms, UTC] | 2026-04-15 10:30:00+00:00 | When we wrote this row |
| `source` | string | "binance_vision" | Data provenance: acquisition method + venue |

**Source values:**
- `"binance_vision"` — Bulk historical archive from Binance global (highest fidelity, preferred).
- `"ccxt_binance"` — CCXT API against Binance global (live incremental updates).
- `"ccxt_binanceus"` — CCXT API against Binance.US (separate venue with different liquidity and order flow; must NOT be merged with Binance global data — use a separate dataset path).

**Important notes:**
- `open_time_utc` identifies the START of the candle. A candle with `open_time_utc = 08:00` covers the period 08:00:00.000 to 08:59:59.999.
- Binance Vision provides raw Unix timestamps in milliseconds. These are converted to timezone-aware UTC datetimes during ingestion.
- Zero-volume bars exist and are flagged in quality reports. They may indicate exchange downtime or data-quality issues.
- Gaps (missing bars) exist and are flagged. They are NOT forward-filled.
- `binance_vision` is preferred over `ccxt_binance` when both cover the same timestamps. The reconcile script enforces this priority during deduplication.

---

## 2. Experiment Registry

**File:** `backtest/experiments.db` (SQLite)
**Table:** `runs`

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `run_id` | TEXT (UUID) | "a1b2c3d4-..." | Unique identifier per backtest run |
| `strategy_name` | TEXT | "sma_crossover_20_50" | Human-readable strategy identifier |
| `strategy_source` | TEXT | "manual" | "manual" / "ai_generated" / "mutated_from_X" |
| `git_commit` | TEXT | "abc1234" | Short SHA of code version |
| `config_hash` | TEXT | "sha256:..." | Hash of execution.yaml + environments.yaml + schemas.yaml |
| `data_snapshot_date` | TEXT (ISO) | "2026-04-15" | Date of the data used |
| `feature_version` | TEXT | "v1" | Feature set version, or "none" |
| `split_version` | TEXT | "v1" | Version from environments.yaml |
| `train_start` | TEXT (ISO) | "2020-01-01" | Training period start |
| `train_end` | TEXT (ISO) | "2023-12-31" | Training period end |
| `validation_start` | TEXT (ISO) | "2024-01-01" | Validation period start (NULL if not used) |
| `validation_end` | TEXT (ISO) | "2024-12-31" | Validation period end (NULL if not used) |
| `test_start` | TEXT (ISO) | "2025-01-01" | Test period start |
| `test_end` | TEXT (ISO) | "2025-12-31" | Test period end |
| `total_return` | REAL | 0.15 | 15% total return |
| `sharpe_ratio` | REAL | 1.2 | Annualized Sharpe ratio |
| `max_drawdown` | REAL | 0.20 | 20% max drawdown |
| `total_trades` | INTEGER | 48 | Total trades executed |
| `win_rate` | REAL | 0.55 | 55% win rate |
| `avg_trade_duration_hours` | REAL | 72.5 | Average holding period |
| `fee_model` | TEXT | "taker_4bps_slip_3bps" | Fee model description |
| `notes` | TEXT | "First run with new data" | Free text notes |
| `review_status` | TEXT | "pending" | "pending" / "approved" / "rejected" (NULL ok in Phase 0) |
| `review_reason` | TEXT | "Passed DSR at N=50" | Reason for review decision (NULL ok in Phase 0) |
| `created_at_utc` | TEXT (ISO) | "2026-04-15T10:30:00Z" | When this run was logged |

---

## 3. Validation Reports

**Directory:** `data/quality/`
**Format:** JSON files named `{check_type}_validation_YYYYMMDD.json`

Each report contains:
```json
{
  "check_date_utc": "2026-04-15T10:30:00Z",
  "file_checked": "data/raw/btcusdt_1h.parquet",
  "row_count": 52560,
  "date_range": {"start": "2020-01-01T00:00:00Z", "end": "2026-04-14T23:00:00Z"},
  "checks": {
    "no_duplicates": {"passed": true, "details": null},
    "no_gaps": {"passed": false, "details": {"gaps_found": 3, "missing_hours": ["..."]}},
    "hour_aligned": {"passed": true, "details": null},
    "ohlc_consistency": {"passed": true, "details": null},
    "zero_volume_bars": {"count": 5, "timestamps": ["..."]},
    "price_anomalies": {"count": 0, "details": null}
  },
  "overall_status": "WARNING"  
}
```

**`overall_status` values:**
- `PASS` — all checks passed, no anomalies detected
- `WARNING` — non-fatal issues found (gaps, zero-volume bars, price anomalies); data is usable but flagged
- `FAIL` — fatal issues found (schema mismatch, null prices, duplicate primary keys); data should NOT be used until fixed

---

## Naming Conventions

- All time columns end in `_utc`
- All percentage values stored as decimals (0.15 = 15%, not 15)
- All prices are in USDT
- All volumes: `volume` = base asset (BTC), `quote_volume` = quote asset (USDT)
- Strategy names use snake_case with parameters: `sma_crossover_20_50`
- Feature versions use `v1`, `v2`, etc.
