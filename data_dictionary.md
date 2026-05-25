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

### 2.x B-C-extended Scope-B columns (T1.x SEAL bundle; 9 new columns)

Per T1.x migration to support B-C-extended `b_c_extended_v1` artifact lineage.
Production source: `MIGRATION_COLUMNS` at
[`backtest/experiment_registry.py:121-170`](backtest/experiment_registry.py).
Test mirror: `_T1X_NEW_COLUMNS` at
[`tests/test_t1_4_backward_compat.py:51`](tests/test_t1_4_backward_compat.py)
with `len == 9` invariant. Full spec:
[`docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md`](docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md)
§4 Migration notes.

The 9 columns divide into three subgroups by sealed comment delimiters:

| Column | Type | MIGRATION_COLUMNS line | Subgroup | Description |
|--------|------|---|---|---|
| `cost_anchor_id` | TEXT | :147 | Phase B (R3.1d V_SEAL) | Forensic discriminator for Phase B Tier 5/6 SPOT evaluation; resolved via `execution_config_path → cost_anchor_id` mapping (6-row table at [`artifact_schema.py:71-77`](backtest/artifact_schema.py)); legacy Phase 1-2 backfilled as `legacy_perp_inspired_7bps_v0`. |
| `returns_per_bar_path` | TEXT | :155 | T1.1 FIX-B1 per-bar artifact linkage | Relative path to per-bar returns parquet artifact (Contract 2.0.5 field 13); value is `"returns_per_bar.parquet"`; persisted by `engine._write_to_registry()` when `lineage_context` is provided. |
| `returns_per_bar_sha256` | TEXT | :156 | T1.1 FIX-B1 per-bar artifact linkage | SHA256 hex digest of `returns_per_bar.parquet` (Contract 2.0.5 field 14); recomputed at read time and compared to this value as 4-step validation step 3. |
| `T_obs` | INTEGER | :157 | T1.1 FIX-B1 per-bar artifact linkage | Count of finite per-bar return observations in `returns_per_bar.parquet`; positive int (bool rejected); validated against actual parquet row count at read (4-step step 4). See §4.2. |
| `regime_key` | TEXT | :166 | SYS-fix-1 LineageContext (B3/B4) | Regime identity key (e.g. `"v2.regime_holdout"`); persisted from `LineageContext` when provided; NULL for pre-SYS-fix-1 runs. |
| `current_git_sha` | TEXT | :167 | SYS-fix-1 LineageContext (B3/B4) | Full-repo git SHA captured at run time; distinct from `engine_commit` (artifact header); persisted from `LineageContext`. |
| `execution_config_path` | TEXT | :168 | SYS-fix-1 LineageContext (B3/B4) | Canonicalized repo-relative POSIX path to execution config YAML (e.g. `"config/execution.yaml"`); canonicalization via `canonicalize_execution_config_path()` at [`artifact_schema.py:91-193`](backtest/artifact_schema.py). |
| `execution_config_sha256` | TEXT | :169 | SYS-fix-1 LineageContext (B3/B4) | SHA256 hex digest of the execution config YAML file; content-addressable hash for forensic reproducibility of cost assumptions. |
| `parquet_data_sha256` | TEXT | :170 | SYS-fix-1 LineageContext (B3/B4) | SHA256 hex digest of the source OHLCV data parquet file; content-addressable hash for forensic reproducibility of the input data used in this run. |

**Backward compatibility:** all 9 columns are nullable; pre-T1.x rows have
NULL values; pre-T1.x consumers continue to work unmodified. New T1.x writers
MUST populate all 9 when `lineage_context` is provided. See
[`docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md`](docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md)
§4.5 for the 4-statement backward-compat set.

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

## 4. B-C-extended per-bar artifact (`b_c_extended_v1`)

**Attestation domain:** per-bar return series preservation artifacts (distinct
from evaluation + walk-forward domains; see
[`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md)
for those domains).

**Schema version:** `b_c_extended_v1` (Contract 2.0.2 LOCK; sealed at
[`backtest/artifact_schema.py:42`](backtest/artifact_schema.py))

**Artifact directory pattern:**
`data/phase2c_evaluation_gate/<run_id_or_batch_dir>/<hypothesis_hash>/`

**Files per artifact:**
- Per-bar return series: `returns_per_bar.parquet`
- Moment summary: location locked at T1.2 implementation (extends
  `holdout_summary.json` per Contract 2.0.5)

**Full spec:** [`docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md`](docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md)
§1 Schema spec + §1.5b T_obs + §1.6 4-step validation discipline.

### 4.1 14 header fields (Contract 2.0.5)

Per parent plan v5 §2.0.5 lines 144-159 (authoritative source); summary form
here for data-dictionary cross-reference.

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | `artifact_schema_version` | string | LOCKED to `"b_c_extended_v1"` for future per-bar artifacts (no T1.6 production producer currently stamps this; CONTRACT GAP per `B_C_EXTENDED_V1_SCHEMA_SPEC.md` §1.5 — emission deferred to B-C-narrow successor cycle); consumer validates via `check_b_c_extended_semantics_or_raise()` ([`artifact_schema.py:654`](backtest/artifact_schema.py)). |
| 2 | `run_id` | string | UUID for this engine run; aliases `runs.run_id` in the experiment registry per Contract 2.0.3 triple-linkage (one of three required resolution keys). |
| 3 | `hypothesis_hash` | string | Canonical DSL hash identifying the strategy hypothesis; one of three required Contract 2.0.3 triple-linkage resolution keys. |
| 4 | `source_batch_id` | string | Orchestrator batch identifier; aliases `runs.batch_id` in the experiment registry per Contract 2.0.3 triple-linkage (one of three required resolution keys). |
| 5 | `parent_run_id` | Optional[string] | UUID of the parent walk-forward window run, if any; `None` is valid for standalone single-run callers without a parent context. |
| 6 | `regime_key` | string | Regime identity key (e.g. `"v2.regime_holdout"`); identifies the evaluation regime for which this artifact was produced. |
| 7 | `engine_commit` | string | Short git SHA of the engine code version used to produce this artifact; engine-level reproducibility anchor. |
| 8 | `current_git_sha` | string | Full-repo git SHA captured at run time; full-repository reproducibility anchor (broader scope than `engine_commit`). |
| 9 | `execution_config_path` | string | Canonicalized repo-relative POSIX path to execution config YAML (e.g. `"config/execution.yaml"`); canonicalization rule per Contract 2.0.4 + [`artifact_schema.py:91-193`](backtest/artifact_schema.py). |
| 10 | `execution_config_sha256` | string | SHA256 hex digest of the execution config YAML file; content-addressable hash enabling forensic verification of cost assumptions used in this run. |
| 11 | `parquet_data_sha256` | string | SHA256 hex digest of the source OHLCV parquet file; content-addressable hash enabling forensic verification of the input data used in this run. |
| 12 | `cost_anchor_id` | string | Cost anchor resolved from `execution_config_path` via 6-row mapping table at [`artifact_schema.py:71-77`](backtest/artifact_schema.py); identifies Phase B Tier 5/6 cost assumption (Contract 2.0.4). |
| 13 | `returns_per_bar_path` | string | Relative path to the per-bar parquet file within the artifact directory `<run_id_or_batch_dir>/<hypothesis_hash>/`; value is `"returns_per_bar.parquet"`. |
| 14 | `returns_per_bar_sha256` | string | SHA256 hex digest of `returns_per_bar.parquet`; recomputed at read time and compared to this value as 4-step validation step 3. |

### 4.2 T_obs — required-adjacent 15th field

Per sub-plan SEAL-eve Round 1 Codex F1 MEDIUM. Sealed at
[`backtest/artifact_schema.py:307-309`](backtest/artifact_schema.py) (declaration)
+ [`:815-827`](backtest/artifact_schema.py) (validation; presence + type +
positivity).

| Field | Type | Description |
|-------|------|-------------|
| `T_obs` | positive int (bool rejected) | Count of finite per-bar return observations stored in `returns_per_bar.parquet`; per-bar-content-shape attribute (not part of the 14-field header metadata table); validated at read time against actual parquet row count (4-step step 4); registry-persisted via [`MIGRATION_COLUMNS:157`](backtest/experiment_registry.py). |

### 4.3 Per-bar return series file (`returns_per_bar.parquet`)

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | timestamp[us, UTC] | Bar open time (UTC-aware microsecond precision); tz-naive Backtrader index localized to UTC at write time per FIX-T1.1-H2. |
| `portfolio_value` | float64 | Portfolio equity value at this bar (USDT); directly from the engine equity curve slice. |
| `return` | float64 | Per-bar return computed from consecutive `portfolio_value` entries via `pct_change()`; first bar is NaN (excluded, so not counted in `T_obs`). |

**Integrity invariants:**
- File MUST exist at resolved `returns_per_bar_path` (4-step validation step 1)
- Path MUST be confined to artifact's containing directory (no `..` escapes;
  step 2)
- SHA256 of read file MUST match stored `returns_per_bar_sha256` (step 3)
- Finite-row-count MUST equal stored `T_obs` (step 4)

### 4.4 Cross-references

- Full schema spec:
  [`docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md`](docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md)
- Extension protocol for future schema versions:
  [`docs/decisions/SCHEMA_VERSION_EXTENSION_PROTOCOL.md`](docs/decisions/SCHEMA_VERSION_EXTENSION_PROTOCOL.md)
- WF + evaluation domain semantics (companion domains):
  [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md)
- HARD CONSTRAINTS: [`CLAUDE.md`](CLAUDE.md) Conservative-Anchor Gate
  Integrity section (line ~270+)

---

## Naming Conventions

- All time columns end in `_utc`
- All percentage values stored as decimals (0.15 = 15%, not 15)
- All prices are in USDT
- All volumes: `volume` = base asset (BTC), `quote_volume` = quote asset (USDT)
- Strategy names use snake_case with parameters: `sma_crossover_20_50`
- Feature versions use `v1`, `v2`, etc.
