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
- **43 zero-OI glitch bars + 7 gaps** — flagged, kept. **Phase-B obligation (both 2-leg-B2 legs):** a single zero-OI bar poisons `oi_log_change` at TWO bars (`t`: log(0)=−inf; `t+1`: uses OI[t]), and a zero *level* is a spurious all-time-low that would distort `oi_pct_rank_2160` if not NaN'd first — so the factor layer must map `OI<=0 → NaN` and a dedicated **zero-poison NaN-propagation test** must verify NaN flows correctly through all 4 OI factors (the level-percentile, the velocity-EWM, the nested velocity-percentile, the sign). This is load-bearing because the **majority of zero bars fall in the 2024/2025 validation/test regimes** (advisor count-only finding: 30 in 2024, 5 in 2025 — a glitch-bar count, NOT a signal-value peek). Also confirm at Phase B that the zero-OI bars carry ~zero *notional* (a true glitch vs a different corruption class).
- No 2026 OI signal **values** were inspected (no-peek; structural validation only).

## Phase A status

A1–A6 built + committed (TDD, per-task; A3 leakage-critical downsample adversarially review-APPROVED — no look-ahead); A7 run clean with 2 disclosed §38.1 instrument repairs. Phase A boundary 2-leg B2 complete (Codex APPROVE + advisor PROCEED; folds at `7cd628e7`); integrity verified (only ingestion/docs/schemas/tests touched; sealed `tier6_dsr_v1` 4/4 unchanged). No LOCKed value was altered in Phase A.

---

## Phase B addendum — percentile-NaN power disclosure (advisor 2-leg-B2, 2026-06-02; anti-hindsight, pre-result)

The Phase-B zero-poison NaN'ing (`OI<=0 → NaN`, the correct conservative handling) has a second-order **eval-power** effect the LOCK §49 under-power framing did not quantify: because the rolling-2160 percentile NaNs the **entire 90-day window** whenever it contains a zero-OI bar, each of the 43 zeros blows a ~90-day hole in `oi_pct_rank_2160` AND the H2 regime factor `oi_velocity_ewm_240_pctrank_2160`. Measured NaN fraction (a data-**coverage** statistic — NOT a signal-value peek; advisor-verified on the built features):

| Window | `oi_pct_rank_2160` NaN | `oi_velocity_ewm_240_pctrank_2160` NaN |
|---|---|---|
| 2024 (validation) | ~48.5% | ~48.6% |
| 2025 (test) | ~74.8% | ~74.8% |
| **forward_2026 (Tier-5 gate)** | **0.0%** | **0.0%** |

**Implication (pre-registered, anti-hindsight):** the verdict-deciding **forward_2026 gate is UNCONTAMINATED** (the last zero-OI bar is in 2025; the 90-day percentile window clears before 2026-01-01). But H2/H3 train/eval floor eligibility (`zero_fraction<0.50`, ≥200 trades, the H2 ≥10% de-risk-cell occupancy) computed on the non-NaN subset is at **materially higher INDETERMINATE risk** than LOCK §48–49 framed — compounding the pre-disclosed 2020-09 train handicap. This makes the §37.3 substantive-measured-loss path and/or the `UNDER_DETERMINED_TRADE_THRESHOLD=10` genuinely-under-determined tag the **more likely Phase-C/D outcome**. This is a power disclosure (data coverage), NOT a defect; the NaN'ing is the correct conservative choice (dropping breaks the native-1h grid; zero-filling fabricates a spurious all-time-low). Carry into the Phase C register.

## Phase B status

B1–B4 factor module (`44f63266`) + B5 registration/build-integration (`0d35bcea`); real-data feature build clean (`feature_version` regenerated, 37 factors, OI route `shared=49239 bars`, 22 gaps→NaN). Phase B boundary 2-leg B2: **Codex APPROVE-WITH-CHANGES + advisor PROCEED-WITH-CHANGES**; folds — coverage-guard docstrings corrected (the Codex HIGH adjudicated: per-bar integrity is enforced by the A3 causal downsample + the exact `validate="one_to_one"` join, not a per-bar raise that would false-positive on the 22 real gaps and miss a value-mislabel; advisor concurred), `oi_velocity_ewm_240_pctrank_2160` warmup 2160→2161 (inner log-change NaN at bar 0), this power disclosure. Pre-existing env-driven `test_tier6_dsr` byte-repro failure confirmed NOT Path D's (fails at base; sealed sha256 4/4 unchanged; no tier6 files touched). No LOCKed value altered in Phase B.
