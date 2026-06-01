# Path C — Markprice (basis axis) Phase A ingestion — data-availability note

**Date:** 2026-05-31 (UTC) · **Branch:** `pathc-basis-scoping` · **Register:** Phase A (first data touch), Charlie-authorized.

The raw parquet (`data/raw/btcusdt_markprice_1h.parquet`) and the auto-generated JSON
validation report (`data/quality/markprice_bulk_validation_*.json`) are **gitignored**
local artifacts (OHLCV convention). This note is the committed provenance record.

## A6 ingestion outcome (`ingestion.markprice_bulk_download --start 2020-01`)
- **55,080 rows**, `2020-01-01 00:00:00Z` → `2026-04-30 23:00:00Z` — the full window **including forward_2026**.
- 76 monthly mark + 76 monthly index 1h kline files parsed (mark=55,296 ∩ index=55,200 → inner-join 55,080).
- Schema: `open_time_utc` `datetime64[ms, UTC]` (unique + sorted PK), `mark_close`/`index_close` `float64` (no NaN), `source` `binance_vision`, `ingested_at_utc` `datetime64[ms, UTC]`. `validate_markprice` → **ok: True** (the wired HARD-CONSTRAINT gate passed before write).
- **10 gaps / ~408 missing hours** flagged, **not interpolated** (futures-kline exchange-outage coverage; FTX-Nov-2022 + post-ETF-Jan-2024 fall within the window — flagged, never cleaned).

## No-peek attestation
The Step −1 LOCK (`5825656`) was committed **before** any basis data was ingested (anti-hindsight commit-order). During A6 only **counts / dates / dtypes / coverage / gap-counts** were inspected — **no 2026 basis value was observed** (the validator and sanity checks operate on structure, not magnitudes). No forward_2026 peek occurred.

## Finding 1 — real-data parser bug (FOUND + FIXED, commit `0fe23f5`)
The first A6 run silently dropped ~4 years of data (kept only 2020-01→2022-05). Root cause: **newer Binance Vision monthly kline CSVs include a header row** (`open_time,open,...`) while older months are headerless; the A2 parser assumed headerless (`header=None`), read the header as data, and skipped every affected month. Fixed by mirroring `bulk_download.py`'s header-autodetection (`_parse_kline_buffer` now branches on whether the first field is numeric); a headed-CSV regression test was added (pc9 → 2793). The re-run produced the correct full-window parquet above. *(Lesson: fixture-based TDD used the old headerless format; the real ingestion run surfaced the format drift — exactly why Phase A is a real-data-touch gate.)*

## Finding 2 — cross-stream coverage (for the Phase B register)
Markprice (futures) and spot (`data/raw/btcusdt_1h.parquet`, 55,105 rows) have **383 markprice-only + 408 spot-only bars** — legitimate differences in futures-vs-spot exchange-outage coverage. The plan's `derive_basis_rel` (Task B0) currently **hard-raises on *any* cross-stream mismatch**, which would break on this real data. **Action at the Phase B register:** B0 must instead **inner-join on the shared `open_time_utc` grid + log the dropped-bar count** (with a sanity threshold that raises only on an implausibly large non-shared fraction), per B2 advisor Finding 6's stated alternative. This is a plan-task refinement discovered via A6; it does not affect Phase A.
