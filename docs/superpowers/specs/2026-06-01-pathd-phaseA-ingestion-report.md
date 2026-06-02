# Path D — Phase A OI Ingestion Report (data-availability + §38.1 findings)

**Date:** 2026-06-01 (UTC). **Branch:** `pathd-oi-scoping`. **Register:** Phase A (ingestion, first data touch — Charlie-registered).

This is the Phase A closeout artifact: what the first authorized OI ingestion run (the §38.1 validation gate) found. The raw parquet `data/raw/btcusdt_oi_1h.parquet` is **gitignored** (per the OHLCV/funding/markprice convention); this report is the committed provenance.

## Source + build

- **Source:** Binance Vision bulk `data/futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-YYYY-MM-DD.zip` (daily partitions, ~5-min cadence, header CSV).
- **Build:** `python -m ingestion.oi_bulk_download --pair BTCUSDT --start 2020-09` → 2099 daily files → 5-min frame 603,878 rows → causal `downsample_oi_to_1h` (label='left', closed='left', `.last()`) → **1h frame 50,355 rows**, written to `data/raw/btcusdt_oi_1h.parquet` (1.3 MB). Future-date partitions (2026-06-21…) returned 404 and were skipped gracefully.

## §38.1 re-verification (the four pre-registered build-time unknowns — all RESOLVED)

| Item | Pre-LOCK assumption | Verified at A7 |
|---|---|---|
| History start | in-repo prior `2020-09` (8-month-shorter train) | **CONFIRMED**: 2020-01-01 → HTTP 404; 2020-09-01 → 200; data starts **2020-09-01 00:00 UTC** |
| CSV schema / header | header row present (`create_time,symbol,sum_open_interest,sum_open_interest_value,…`) | **CONFIRMED**: header present; `create_time` is a UTC datetime string (not ms epoch) |
| Cadence | ~5-min | **CONFIRMED**: 5-min snapshots |
| Unit (firewall-critical) | `sum_open_interest` = contracts (signal); `sum_open_interest_value` = USDT notional (cross-check only) | **CONFIRMED**: `sum_open_interest`≈39080 (BTC contracts) vs `sum_open_interest_value`≈456M (USDT); ratio ≈ BTC price → contract-denominated. Firewall mapping holds. |

## Two real-data findings (handled as disclosed, LOCK-untouching instrument repairs)

1. **Exact-duplicate 5-min rows (commit `45ea7163`).** Every 5-min snapshot is duplicated exactly (2020-09-01: 576 rows = 288 unique × 2, **0 differing values**). The downsample already absorbed exact dupes correctly; per §38.2, `parse_metrics_csv` now drops exact-duplicate content rows and **warns + keep-last** if a timestamp ever has *differing* values (a future glitch). On the full dataset: 603,878 → 301,939 unique 5-min rows.
2. **43 zero-OI bars (commit `0f5e87e1`).** `sum_open_interest == 0` on 43/50,355 rows (~0.085%) — glitch snapshots. `validate_oi` previously failed on `<=0`; corrected to mirror the project's zero-volume-bar discipline: **NaN/negative → error; zero → flagged warning, kept** (never removed). The factor layer (Phase B) maps `OI<=0 → NaN` log-change.

## Validated 1h-frame characteristics (`validate_oi` → ok=True)

- **50,355 rows**, 2020-09-01 00:00 → 2026-06-01 00:00 UTC; `datetime64[ms, UTC]`; PK **unique + strictly ascending**; source `binance_vision`; 0 NaN in `sum_open_interest`.
- **Flagged (warnings, not removed):** 43 zero-OI bars; 7 spacing gaps / ~22 missing hours (max gap 11h).
- Coverage: 50,355 / 50,377 expected hours → **22 missing bars** (the gaps; flagged, not interpolated).

## Known OI data characteristics (for downstream phases)

- **OI history starts 2020-09-01** — the OI-informed train window is ~8 months shorter than OHLCV/funding/basis (2020-01); after the 2160-bar (≈90d) warmup, OI factors are first valid ≈2020-12. This is the §12 heightened-under-power handicap (immutable split unchanged; OI factors NaN before availability+warmup).
- **43 zero-OI glitch bars + 7 gaps** — flagged, kept; Phase B factors must handle `OI<=0 → NaN` (the velocity log-change) gracefully.
- No 2026 OI signal **values** were inspected (no-peek; structural validation only).

## Phase A status

A1–A6 built + committed (TDD, per-task; A3 leakage-critical downsample adversarially review-APPROVED — no look-ahead); A7 run clean with 2 disclosed §38.1 instrument repairs. **Next: Phase A boundary 2-leg B2 (Codex + advisor), then STOP for the Phase B register.** No LOCKed value was altered in Phase A.
