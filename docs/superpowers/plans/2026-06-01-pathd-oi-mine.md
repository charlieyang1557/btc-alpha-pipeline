# Path D — Open-Interest Axis Mechanism-First Mine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build + run the bounded, pre-registered one-cycle falsification test of the **open-interest (OI)** positioning axis: ingest Binance Vision `metrics` OI (header CSV), causally downsample to a 1h `sum_open_interest` series, compute 4 causal OI factors, express the 3 LOCKed OI hypotheses (H1/H2/H3) in the DSL, reuse the Path C verdict harness retargeted to OI, add the **D1-only** orthogonalization + the **fenced contamination-correlation set** (D2 DROPPED — decision A1), and produce the forward_2026 earned-negative-or-positive verdict.

**Architecture:** Mirror Path C's pipeline, swapping the *data family* (basis → OI) while holding the *process* fixed. **Four deliberate divergences from Path C:** (1) the Binance Vision `metrics` CSV carries a **header row** → the parser uses **header-autodetect** (§38.2, the lesson Path C's header-bug earned); (2) OI is **not native-1h** (Binance `metrics` ≈ 5-min) → a NET-NEW **causal 5min→1h downsample** (bar-close = last OI ≤ close) produces the canonical 1h raw; (3) the OI signal series is **`sum_open_interest` (contracts), NOT `sum_open_interest_value` (notional)** — notional velocity mechanically embeds the price return and would defeat the velocity firewall; (4) **D2 is DROPPED** (no derived-from axis for the independent OI) → the diagnostic is **D1-only** plus a **fenced contamination-correlation set** (`oi_velocity` vs price/vol series) that quantifies the disclosed vol/liquidation residual without being a control. Sealed `tier6_dsr_v1` artifacts stay byte-identical throughout.

**Tech Stack:** Python 3.11, pandas/pyarrow (parquet), CCXT (incremental OI, recent-window only), Backtrader (engine), scipy (DSR), pytest (TDD). All UTC.

**Governing LOCK:** [`../specs/2026-06-01-pathd-step-minus-1-preregistration-lock.md`](../specs/2026-06-01-pathd-step-minus-1-preregistration-lock.md) — **frozen; no task may alter a LOCKed value.** Design spec: [`../specs/2026-06-01-path-d-oi-scoping-design.md`](../specs/2026-06-01-path-d-oi-scoping-design.md).

**Register discipline (CRITICAL):** This plan spans **three separate downstream Charlie register-events** — Phase A (ingestion = first data touch), Phase B+C (build), Phase D (run). **Each phase boundary requires an explicit Charlie register before proceeding.** Per-task commits await Charlie authorization. The plan is the scoping deliverable; authoring it authorizes no execution.

**Baseline:** pc9 = 3014 (Path C SEAL). Sealed `tier6_dsr_v1/` sha256: `0a7d98ac` / `8eecc6cd` / `49646c30` / `1803eb44` (re-verify before AND after any Phase D task). Branch `pathd-oi-scoping` (off Path C HEAD `f0dbdf92`); spec `76a0cd7a`, LOCK `736d4c03`.

**2-leg B2 (2026-06-01):** Codex *APPROVE-WITH-CHANGES* + advisor *COMMIT-WITH-CHANGES*; both confirm full LOCK fidelity + sound methodology on the 4 divergences + clean anti-pre-emption + complete register discipline. All findings folded (execution-layer only, no LOCKed value touched): C1/C3 `referenced_factors` expected sets corrected for the LOCKed sizing factor (assert ENTRY factors for the no-extra-price-conjunct check); the under-determined carve-out keyed on the generic `eligible==False AND trades<10 AND sharpe>=0` predicate (not `zero_fraction`); A4 adds the `--oi` validators CLI branch; B5 mirrors the injectable `oi_df` build-route pattern + coverage guard; A3 downsample docstring + boundary semantics clarified; contamination `abs_return_1h` = caller-computed `abs(return_1h)`; A2 required-column defensive check; `oi_sign` noted LOCK-registered-but-referenced-by-no-hypothesis. The 5min→1h downsample is the only leakage surface with no in-repo template — re-verified at the build register against the engine factor-timing convention.

---

## File structure

| File | Responsibility | New/Modify |
|---|---|---|
| `config/schemas.yaml` | add `oi` schema block (1h OI columns + validation) | Modify |
| `ingestion/oi_bulk_download.py` | Binance Vision bulk `futures/um/daily/metrics/BTCUSDT/` (header CSV, ≈5-min) → parse + **causal 1h downsample** → parquet | Create |
| `ingestion/oi_incremental_update.py` | CCXT `fetch_open_interest_history` 1h incremental (recent ~30d top-up only) | Create |
| `ingestion/oi_reconcile.py` | merge + archive-before-overwrite + source-priority dedup for OI | Create |
| `ingestion/validators.py` | extend to validate the `oi` schema (UTC PK, sorted, 1h spacing) | Modify |
| `data/raw/btcusdt_oi_1h.parquet` | canonical 1h-downsampled OI series (output) | Create (Phase A run) |
| `factors/oi.py` | `oi_sign`, `oi_velocity_ewm_240`, `oi_pct_rank_2160`, `oi_velocity_ewm_240_pctrank_2160` (causal, on the 1h `sum_open_interest` series) + `_oi_log_change` helper | Create |
| `factors/registry.py` | widen `input_source` to add `"oi"`; register the 4 OI factors; `feature_version` bump | Modify |
| `factors/build_features.py` | integrate OI factors into the full-dataset build (`input_source="oi"` route + coverage-guarded left-join onto the OHLCV frame) | Modify |
| `backtest/pathd_eval_gauntlet.py` | H1/H2/H3 OI DSL builders + EVAL gauntlet (adapt `pathc_eval_gauntlet.py`) | Create |
| `backtest/pathd_holdout_producer.py` | forward_2026 single-run holdout producer (adapt `pathc_holdout_producer.py`) | Create |
| `backtest/pathd_moments.py` | CandidateMoments constructor + integrity gate + degenerate/flat-equity handling (adapt `pathc_moments.py`) | Create |
| `backtest/pathd_dsr_fwer.py` | DSR-FWER N\*=3 over the OI cohort (adapt `pathc_dsr_fwer.py`) | Create |
| `backtest/pathd_perleg_mechanism.py` | tiered 24h+72h strong/weak-sane mechanism-sanity (adapt `pathc_perleg_mechanism.py`) | Create |
| `backtest/pathd_marginal_diagnostic.py` | **D1-only** (vs momentum) fenced + the **fenced contamination-correlation set**; D2/`redundancy_read` ABSENT (adapt + prune `pathc_marginal_diagnostic.py`) | Create |
| `backtest/pathd_escalation.py` | next-axis escalation advisory keyed on `n_dsr_pass == 0` (adapt `pathc_escalation.py`) | Create |
| `backtest/pathd_earned_negative.py` | taxonomy + advisory assembly incl. the under-determined carve-out + thin-sample-SANE clause (adapt `pathc_earned_negative.py`) | Create |
| `backtest/pathd_train_sanity.py` | train-only mechanism-sanity table driver (adapt `pathc_train_sanity.py`) | Create |
| `backtest/pathd_orchestrator.py` | end-to-end run_pathd_verdict (adapt `pathc_orchestrator.py`) | Create |
| `scripts/pathd_run_verdict.py` | gated forward_2026 verdict run entrypoint (`PHASE_D_AUTHORIZED` gate + injected `_run_backtest`; adapt `scripts/pathc_run_verdict.py`) | Create |

Tests live beside the suite: `tests/test_oi_ingestion.py`, `tests/test_oi_factors.py`, `tests/test_pathd_*.py`.

---

# PHASE A — OI ingestion  *(downstream Charlie register A — first data touch)*

> Phase A is the first data touch. Do NOT begin until Charlie registers Phase A. The LOCK is already committed (anti-hindsight), so ingesting OI now cannot reverse-fit the hypotheses. **No OI VALUES in the forward_2026 window may be inspected during build/test** — fixtures use synthetic values only. Per §38.1, the A7 integration run is the format/availability validation gate (expect a real-data surprise — re-verify the 2020-09 start, the metrics CSV schema/header, the cadence, and the contracts-vs-notional unit).

### Task A1: OI schema block

**Files:**
- Modify: `config/schemas.yaml` (add top-level `oi` block, mirroring the `markprice`/`ohlcv` block structure)
- Test: `tests/test_oi_ingestion.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_oi_ingestion.py
import yaml
from pathlib import Path

def test_oi_schema_block_exists():
    schemas = yaml.safe_load(Path("config/schemas.yaml").read_text())
    m = schemas["oi"]
    assert m["primary_key"] == "open_time_utc"
    cols = set(m["columns"].keys())   # columns is a name-keyed MAPPING (mirror the ohlcv/markprice block)
    assert {"open_time_utc", "sum_open_interest", "sum_open_interest_value",
            "source", "ingested_at_utc"} <= cols
    assert set(m["columns"]["source"]["allowed_values"]) >= {"binance_vision", "ccxt_binance"}
```

- [ ] **Step 2: Run to verify it fails** — `python -m pytest tests/test_oi_ingestion.py::test_oi_schema_block_exists -v` → FAIL (KeyError 'oi').

- [ ] **Step 3: Add the `oi` block to `config/schemas.yaml`**

```yaml
# Mirrors the existing `markprice`/`ohlcv` block structure exactly. The canonical
# raw is the causally-downsampled 1h OI; sum_open_interest (CONTRACTS) is the signal
# series, sum_open_interest_value (USDT notional) is stored for the cross-check /
# contamination diagnostic ONLY (its velocity embeds the price return — never the signal).
oi:
  description: "Binance USDT-M perpetual open interest, causally downsampled to 1h for BTCUSDT (OI positioning axis)"
  primary_key: "open_time_utc"
  sort_order: "open_time_utc ASC"
  file_pattern: "data/raw/btcusdt_oi_1h.parquet"
  columns:
    open_time_utc:
      dtype: "datetime64[ms, UTC]"
      nullable: false
      description: "1h bar open time, UTC tz-aware, unique, sorted ascending, hour-aligned (bar-close OI = last OI obs <= this bar's close)"
    sum_open_interest:
      dtype: "float64"
      nullable: false
      description: "Total open interest in CONTRACTS (base/coin-denominated). THE SIGNAL SERIES (firewall-critical: NOT notional)."
    sum_open_interest_value:
      dtype: "float64"
      nullable: true
      description: "Total open interest in USDT notional. Cross-check / contamination-diagnostic ONLY; never the signal (notional velocity embeds price return)."
    ingested_at_utc:
      dtype: "datetime64[ms, UTC]"
      nullable: false
      description: "Timestamp when this row was written"
    source:
      dtype: "string"
      nullable: false
      allowed_values: ["binance_vision", "ccxt_binance"]
      description: "Provenance: binance_vision (bulk) | ccxt_binance (incremental)"
  validation_rules:
    - name: "no_duplicates"
      check: "open_time_utc is unique"
    - name: "sorted_pk"
      check: "open_time_utc strictly ascending"
    - name: "utc_tz_aware"
      check: "open_time_utc is timezone-aware UTC"
    - name: "hour_aligned_1h"
      check: "consecutive open_time_utc differ by exactly 3600000 ms (gaps flagged, not interpolated)"
    - name: "no_forward_fill"
      check: "missing bars flagged in the quality report, never interpolated"
      severity: "warning"
```

- [ ] **Step 4: Run to verify it passes** — PASS.
- [ ] **Step 5: Commit** (await Charlie authorization) — `git add config/schemas.yaml tests/test_oi_ingestion.py` then `git commit -F /tmp/msg.txt` ("feat(pathd): oi schema block").

### Task A2: OI bulk download + parse (Binance Vision metrics, HEADER-autodetect)

**Files:**
- Create: `ingestion/oi_bulk_download.py`
- Test: `tests/test_oi_ingestion.py`

> §38.2 lesson (the one Path C's silent header-drop earned): the Binance Vision `metrics` CSV **carries a header row** (`create_time,symbol,sum_open_interest,sum_open_interest_value,...`). Mirror the **most defensive existing parser** — `ingestion/bulk_download.py`'s header-autodetect — NOT the headerless kline assumption.

- [ ] **Step 1: Write the failing test** (parse a fixture CSV in the metrics format — WITH a header)

```python
# tests/test_oi_ingestion.py  (append)
import pandas as pd
from ingestion.oi_bulk_download import parse_metrics_csv

def test_parse_oi_metrics_with_header(tmp_path):
    # Binance Vision metrics: HEADER row + create_time as a UTC datetime string, 5-min cadence.
    csv = tmp_path / "BTCUSDT-metrics-2020-09-01.csv"
    csv.write_text(
        "create_time,symbol,sum_open_interest,sum_open_interest_value,"
        "count_toptrader_long_short_ratio,sum_toptrader_long_short_ratio,"
        "count_long_short_ratio,sum_taker_long_short_vol_ratio\n"
        "2020-09-01 00:00:00,BTCUSDT,12345.6,98765432.1,1.2,1.3,1.1,0.9\n"
        "2020-09-01 00:05:00,BTCUSDT,12350.0,98800000.0,1.2,1.3,1.1,0.9\n"
    )
    df = parse_metrics_csv(csv)
    assert list(df["open_time_utc"]) == [
        pd.Timestamp("2020-09-01 00:00:00", tz="UTC"),
        pd.Timestamp("2020-09-01 00:05:00", tz="UTC"),
    ]
    assert df["sum_open_interest"].tolist() == [12345.6, 12350.0]
    assert df["sum_open_interest_value"].tolist() == [98765432.1, 98800000.0]
    assert str(df["open_time_utc"].dtype) == "datetime64[ms, UTC]"
    assert (df["source"] == "binance_vision").all()
```

- [ ] **Step 2: Run to verify it fails** — `ModuleNotFoundError`.

- [ ] **Step 3: Implement `parse_metrics_csv` + the bulk downloader**

```python
# ingestion/oi_bulk_download.py
"""Bulk download Binance Vision USDT-M open-interest metrics for BTCUSDT.

Mirrors ingestion/bulk_download.py (incl. its HEADER-AUTODETECT — the metrics CSV
carries a header row, unlike the headerless klines; §38.2). Source (daily partitions,
~5-min cadence):
  data/futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-YYYY-MM-DD.zip
Columns (header): create_time, symbol, sum_open_interest, sum_open_interest_value, ...
create_time is a UTC datetime STRING (not ms epoch). We keep the two OI columns;
sum_open_interest (contracts) is the signal, sum_open_interest_value (notional) is a
cross-check only. The parsed 5-min frame is downsampled to 1h by downsample_oi_to_1h
(Task A3) before write.

NOTE (§38.1): the EXACT metrics schema/header/cadence is re-verified at the A7
integration run — the first real ingestion is the format-validation gate.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import logging
import pandas as pd

METRICS_PREFIX = "data/futures/um/daily/metrics/BTCUSDT/"
OUTPUT_PATH = Path("data/raw/btcusdt_oi_1h.parquet")
_REQUIRED = ["create_time", "sum_open_interest", "sum_open_interest_value"]

def parse_metrics_csv(path: Path) -> pd.DataFrame:
    """Parse one Binance Vision metrics CSV (HEADER-autodetect), keeping the OI columns.

    Inputs: a metrics CSV; first line may be a header (`create_time,...`) or data.
    Output: open_time_utc(datetime64[ms,UTC]), sum_open_interest(float64),
      sum_open_interest_value(float64), source(string), ingested_at_utc(datetime64[ms,UTC]).
    Null policy: rows with NaN create_time or sum_open_interest are dropped + counted."""
    # Header-autodetect (mirror bulk_download.py's defensive parser, §38.2): the metrics
    # CSV normally carries a header ("create_time,..."); detect it by testing whether the
    # first field parses as a timestamp (data) vs not (header) — robust to the digits-only
    # trap (a datetime string with separators stripped is all-digit, so a naive isdigit
    # check mis-classifies the data row).
    first = path.read_text().splitlines()[0].split(",")[0].strip()
    has_header = _is_header_field(first)
    raw = pd.read_csv(path, header=0 if has_header else None)
    if not has_header:                       # positional fallback (defensive; metrics normally has a header)
        raw.columns = ["create_time", "symbol", "sum_open_interest", "sum_open_interest_value",
                       "c1", "c2", "c3", "c4"][: raw.shape[1]]
    missing = [c for c in _REQUIRED if c not in raw.columns]   # §38.2 defensive: required cols present
    if missing:
        raise ValueError(f"parse_metrics_csv: missing required columns {missing} in {path.name}")
    n_in = len(raw)
    raw = raw.dropna(subset=["create_time", "sum_open_interest"])
    n_dropped = n_in - len(raw)
    if n_dropped:
        logging.info("parse_metrics_csv: dropped %d NaN row(s) from %s", n_dropped, path.name)
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(raw["create_time"], utc=True).astype("datetime64[ms, UTC]"),
        "sum_open_interest": raw["sum_open_interest"].astype("float64"),
        "sum_open_interest_value": raw["sum_open_interest_value"].astype("float64"),
    })
    df["source"] = pd.array(["binance_vision"] * len(df), dtype="string")
    df["ingested_at_utc"] = pd.Timestamp(datetime.now(timezone.utc)).as_unit("ms")
    return df.sort_values("open_time_utc").reset_index(drop=True)

def _is_header_field(first_field: str) -> bool:
    """True if the first CSV field is a header token (NOT parseable as a timestamp).
    'create_time' -> True (header); '2020-09-01 00:00:00' -> False (data). Robust to the
    digits-only trap that a naive strip-separators-and-isdigit check falls into."""
    try:
        return bool(pd.isna(pd.to_datetime(first_field, utc=True)))
    except (ValueError, TypeError, OverflowError):
        return True
```
(The download/unzip wrapper mirrors `bulk_download.py`'s `main()`: download `METRICS_PREFIX` daily ZIPs from `--start 2020-09` (the in-repo prior; re-verified at A7), parse each, concat, **then call `downsample_oi_to_1h` (Task A3)** before write, argparse + `--dry-run`, log rows-before/after. No checksum step.)

- [ ] **Step 4: Run to verify it passes** — PASS.
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): oi bulk download + metrics parse (header-autodetect)`.

### Task A3: Causal 5min→1h downsample (NET-NEW — the §37.2-safe consumption-grid derivation)

**Files:**
- Modify: `ingestion/oi_bulk_download.py` (add `downsample_oi_to_1h`)
- Test: `tests/test_oi_ingestion.py`

> NET-NEW vs Path C (basis was native-1h). OI ≈ 5-min → the canonical raw is the **causal 1h bar-close** value (the last OI observation at/before each 1h close). Computing factors on the 1h grid avoids the §37.2 cross-cadence-warmup-unit bug. The leakage surface is the downsample itself — guarded by a causality test.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_oi_ingestion.py  (append)
import pandas as pd, numpy as np
from ingestion.oi_bulk_download import downsample_oi_to_1h

def test_downsample_bar_close_is_last_obs_within_bar():
    # row N (bar [N, N+1h)) = the LAST 5-min obs WITHIN the bar (the mark_close analog),
    # stamped at N to align with the OHLCV open_time grid. label='left', closed='left'.
    ts = pd.date_range("2020-09-01 00:00", "2020-09-01 02:00", freq="5min", tz="UTC")
    df5 = pd.DataFrame({"open_time_utc": ts,
                        "sum_open_interest": np.arange(len(ts), dtype="float64"),
                        "sum_open_interest_value": np.arange(len(ts), dtype="float64") * 10.0,
                        "source": "binance_vision"})
    out = downsample_oi_to_1h(df5)
    # bar [01:00, 02:00) -> last within-bar obs is 01:55 (index 23) -> value 23.0
    row01 = out.loc[out.open_time_utc == pd.Timestamp("2020-09-01 01:00", tz="UTC")]
    assert row01["sum_open_interest"].iloc[0] == 23.0
    assert str(out["open_time_utc"].dtype) == "datetime64[ms, UTC]"
    assert (out["open_time_utc"].diff().dropna() == pd.Timedelta("1h")).all()

def test_downsample_row_depends_only_on_within_bar_obs():
    # Causality: row 01:00 (bar [01:00,02:00)) is unchanged when obs at/after the NEXT
    # bar boundary (02:00) are deleted -> it never reads a future bar.
    ts = pd.date_range("2020-09-01 00:00", "2020-09-01 03:00", freq="5min", tz="UTC")
    df5 = pd.DataFrame({"open_time_utc": ts, "sum_open_interest": np.arange(len(ts), dtype="float64"),
                        "sum_open_interest_value": np.zeros(len(ts)), "source": "binance_vision"})
    full = downsample_oi_to_1h(df5)
    truncated = downsample_oi_to_1h(df5[df5.open_time_utc < pd.Timestamp("2020-09-01 02:00", tz="UTC")])
    key = pd.Timestamp("2020-09-01 01:00", tz="UTC")
    v_full = full.loc[full.open_time_utc == key, "sum_open_interest"].iloc[0]
    v_trunc = truncated.loc[truncated.open_time_utc == key, "sum_open_interest"].iloc[0]
    assert v_full == v_trunc
```

- [ ] **Step 2: Run to verify it fails** — ImportError.
- [ ] **Step 3: Implement** (causal resample-to-hour-close)

```python
def downsample_oi_to_1h(df5: pd.DataFrame) -> pd.DataFrame:
    """Causally downsample a ~5-min OI frame to the 1h grid: each 1h bar N (covering
    [N, N+1h)) takes the LAST 5-min observation WITHIN the bar (timestamps strictly
    < N+1h) = the bar-N-close OI (the mark_close analog). Strictly causal — row N uses
    only observations with timestamp < N+1h. No future read; gaps NOT interpolated.

    Inputs: 5-min frame (open_time_utc, sum_open_interest, sum_open_interest_value, source).
    Output: 1h frame (same columns), open_time_utc hour-aligned. Warmup: N/A."""
    s = df5.sort_values("open_time_utc").set_index("open_time_utc")
    # label='left', closed='left' -> each 1h bin is [N, N+1h), stamped at N, and .last()
    # takes the final obs WITHIN the bar = the bar-N-close OI (the mark_close analog),
    # aligned to the OHLCV open_time grid. Causal: row N uses only obs in [N, N+1h).
    agg = s[["sum_open_interest", "sum_open_interest_value"]].resample(
        "1h", label="left", closed="left").last()
    agg = agg.dropna(subset=["sum_open_interest"])           # gaps flagged downstream, not filled
    agg = agg.reset_index().rename(columns={"index": "open_time_utc"})
    agg["open_time_utc"] = agg["open_time_utc"].astype("datetime64[ms, UTC]")
    agg["source"] = pd.array(["binance_vision"] * len(agg), dtype="string")
    agg["ingested_at_utc"] = df5["ingested_at_utc"].iloc[0] if "ingested_at_utc" in df5 \
        else pd.Timestamp(datetime.now(timezone.utc)).as_unit("ms")
    return agg
```

> **DESIGN INVARIANT (the single most leakage-critical alignment — verify at build-time against `mark_close` + the cross-stream guard + the 2-leg B2):** `closed="left", label="left"` makes the 1h bar stamped at `N` cover `[N, N+1h)` and take its `.last()` = the last 5-min OI obs WITHIN the bar — the exact analog of how Path C's `mark_close[N]` aligns to the OHLCV `open_time` grid (a bar-N-close value on row `N`). Row `N` is consumed as the signal at bar `N`'s close per the execution convention, filling at `N+1` open. The delete-future causality test asserts row `N` depends only on obs within `[N, N+1h)` (deleting obs at/after the next-bar boundary leaves it unchanged). The closed-left (within-bar, conservative) vs closed-right (next-boundary snapshot) choice + the exact alignment to `mark_close` is re-verified at the build register against the engine's actual factor-timing convention.

- [ ] **Step 4: Run to verify it passes** — PASS.
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): causal 5min->1h OI downsample`.

### Task A4: OI validators

**Files:**
- Modify: `ingestion/validators.py` (add `validate_oi(df)`)
- Test: `tests/test_oi_ingestion.py`

- [ ] **Step 1: Write the failing test**

```python
from ingestion.validators import validate_oi
import pandas as pd

def _good_oi():
    return pd.DataFrame({
        "open_time_utc": pd.to_datetime([1577836800000, 1577840400000], unit="ms", utc=True).as_unit("ms"),
        "sum_open_interest": [12345.6, 12350.0], "sum_open_interest_value": [9.8e7, 9.9e7],
        "source": ["binance_vision"]*2, "ingested_at_utc": pd.to_datetime([0,0], unit="ms", utc=True).as_unit("ms"),
    })

def test_validate_oi_accepts_good():
    assert validate_oi(_good_oi())["ok"] is True

def test_validate_oi_rejects_duplicate_pk():
    df = _good_oi(); df.loc[1, "open_time_utc"] = df.loc[0, "open_time_utc"]
    r = validate_oi(df)
    assert r["ok"] is False and "duplicate" in r["errors"][0].lower()

def test_validate_oi_rejects_negative_oi():
    df = _good_oi(); df.loc[0, "sum_open_interest"] = -1.0
    r = validate_oi(df)
    assert r["ok"] is False
```

- [ ] **Step 2: Run to verify it fails** — ImportError.
- [ ] **Step 3: Implement `validate_oi`** (UTC tz-aware, unique+sorted PK, allowed source, `sum_open_interest > 0`, exact 3,600,000 ms spacing with gaps flagged-not-removed; returns `{"ok": bool, "errors": [...], "warnings": [...], "rows": n}`). Mirror the `validate_markprice` structure. **AND wire the CLI (B2 Codex+advisor — `validators.py main()` currently accepts only `--file`/`--funding`; `--markprice` was defined but never wired):** add a `--oi <path>` argparse branch, update to mutually-exclusive-one-of `{--file, --funding, --markprice, --oi}`, dispatch to `validate_oi`, non-zero exit on failure — so the A7 `python -m ingestion.validators --oi ...` step runs. Add a CLI-routing test.
- [ ] **Step 4: Run to verify it passes** — PASS.
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): oi validators`.

### Task A5: OI reconcile + archive

**Files:** Create `ingestion/oi_reconcile.py`; Test `tests/test_oi_ingestion.py`.

- [ ] **Step 1: Write the failing test** — archive-before-overwrite writes a snapshot to `data/raw/archive/btcusdt_oi_1h_<ts>.parquet`; dedup on `open_time_utc` preferring `binance_vision` over `ccxt_binance`; output unique+sorted.
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** mirroring `ingestion/markprice_reconcile.py` (`archive_file`, `SOURCE_PRIORITY = {"binance_vision": 0, "ccxt_binance": 1}`, merge+dedup+sort). OI is a distinct file — no cross-venue OHLCV interaction.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): oi reconcile + archive`.

### Task A6: CCXT incremental OI update (recent-window top-up only)

**Files:** Create `ingestion/oi_incremental_update.py`; Test `tests/test_oi_ingestion.py` (mock the CCXT client).

> Binance's OI-history endpoint returns only ~30 days, so CCXT is a **recent-window top-up** (bulk Vision is the sole full-history path). Fetch at `'1h'` period directly (already on the consumption grid — no downsample needed for the incremental).

- [ ] **Step 1: Write the failing test** — a mocked exchange whose `fetch_open_interest_history(symbol="BTC/USDT:USDT", timeframe="1h", since=...)` returns rows normalized to the `oi` schema (UTC PK, `sum_open_interest` from the CCXT `openInterestAmount`/`info` field, source `ccxt_binance`). Document at the test site that the exact CCXT field mapping is re-verified at A7.
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** mirroring `ingestion/markprice_incremental_update.py` (`create_exchange`, paginated `fetch_open_interest_history`, retry logic, normalize to the `oi` schema; **use the contract/base-asset OI field, not the USDT notional** — assert the mapped `sum_open_interest` is the contract amount). Cap the lookback to the endpoint's ~30d window; log if `since` predates it.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): oi incremental update (CCXT, recent-window)`.

### Task A7: Phase A integration run (ACTUAL data touch — Charlie-gated; the §38.1 validation gate)

- [ ] **Step 1:** `python -m ingestion.oi_bulk_download --pair BTCUSDT --start 2020-09` → `data/raw/btcusdt_oi_1h.parquet`. **Re-verify (§38.1/§13): the metrics CSV header + column names, the native cadence (≈5-min), the `sum_open_interest`=contracts vs `sum_open_interest_value`=notional unit mapping, and the true history start** (the LOCK's `2020-09` is an in-repo prior). If the start, schema, or unit differs from the assumption, STOP and report to Charlie (a real-data surprise is the expected §38.1 outcome — handle as a disclosed instrument repair, LOCK params untouched).
- [ ] **Step 2:** `python -m ingestion.validators --oi data/raw/btcusdt_oi_1h.parquet --report data/quality/` → assert `ok: True`; document the 2020-09 start (train-window shrinkage vs the 2020-01 spot start), FTX-Nov-2022, and any partition gaps (flagged, not cleaned).
- [ ] **Step 3:** sanity: row count ≈ 24/day × (2020-09 → 2026-04) ≈ ~49k rows; first `open_time_utc` ≈ 2020-09; consecutive spacing exactly 3,600,000 ms (log exceptions); **cross-stream coverage** vs the spot parquet's `open_time_utc` over the overlap (Task B5 asserts this). **Do NOT inspect 2026 OI values** (no-peek).
- [ ] **Step 4: Commit** the data-availability report (NOT the raw parquet if policy excludes large binaries; follow the OHLCV convention) — await authorization.

> **STOP — Phase A register boundary.** Report ingestion results (esp. the §38.1 re-verification outcome) to Charlie; await Phase B register.

---

# PHASE B — OI feature pipeline  *(part of downstream register B — build)*

> All OI factors compute on the 1h `sum_open_interest` series (the CONTRACTS column — firewall-critical). Velocity factors use the log-change; the level percentile uses the level. `_oi_log_change` is a non-registered helper (causal: `log(OI[t]) − log(OI[t−1])`, a backward `shift(1)`).

### Task B1: `oi_sign` factor (+ `_oi_log_change` helper)

**Files:** Create `factors/oi.py`; Test `tests/test_oi_factors.py`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_oi_factors.py
import pandas as pd, numpy as np
from factors.oi import oi_sign

def test_oi_sign_is_sign_of_log_change():
    # OI rising -> +1; falling -> -1; flat -> 0. First bar NaN (no prior).
    oi = pd.Series([100.0, 110.0, 105.0, 105.0])
    out = oi_sign(pd.DataFrame({"sum_open_interest": oi}))
    assert np.isnan(out.iloc[0])
    assert out.iloc[1:].tolist() == [1.0, -1.0, 0.0]
```

- [ ] **Step 2: Run to verify it fails** — ImportError.
- [ ] **Step 3: Implement** (top-level named, causal)

```python
# factors/oi.py
"""Open-interest factors computed on the native-1h sum_open_interest (CONTRACTS)
series (causal, rolling over 1h bars). The CONTRACTS column is the firewall-critical
input: the USDT-notional column's log-change embeds the price return and would defeat
the velocity firewall, so it is NEVER used here. All factors are top-level named
callables, rolling/causal only (pass G1-G4)."""
from __future__ import annotations
import numpy as np
import pandas as pd

def _oi_log_change(df: pd.DataFrame) -> pd.Series:
    """log(OI[t]) - log(OI[t-1]) on sum_open_interest (CONTRACTS). Causal (backward
    shift(1)); first bar NaN. The flow-of-new-positioning primitive (helper, not registered)."""
    oi = df["sum_open_interest"].astype("float64")
    return np.log(oi) - np.log(oi.shift(1))

def oi_sign(df: pd.DataFrame) -> pd.Series:
    """Sign of the OI log-change (inflow=+1 / outflow=-1 / flat=0). Inputs:
    sum_open_interest. Warmup: 1 bar. Output: {-1.0,0.0,1.0}. Null: first bar NaN."""
    return np.sign(_oi_log_change(df)).astype("float64")
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): oi_sign factor + _oi_log_change helper`.

### Task B2: `oi_velocity_ewm_240`

**Files:** Modify `factors/oi.py`; Test `tests/test_oi_factors.py`.

- [ ] **Step 1: Write the failing test** — `oi_velocity_ewm_240(df)` equals `_oi_log_change(df).ewm(span=240, adjust=False).mean()`; assert `adjust=False`; assert causality (delete-future invariance at row N).
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement**

```python
def oi_velocity_ewm_240(df: pd.DataFrame) -> pd.Series:
    """Causal EWM (span=240 bars ~10d, adjust=False) of the OI log-change = the
    flow-of-new-positioning velocity (the anti-endogeneity firewall quantity).
    Inputs: sum_open_interest. Warmup: ~240 bars. Null: NaN before first obs."""
    return _oi_log_change(df).ewm(span=240, adjust=False).mean()
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): oi_velocity_ewm_240`.

### Task B3: `oi_pct_rank_2160` (level percentile)

**Files:** Modify `factors/oi.py`; Test `tests/test_oi_factors.py`.

- [ ] **Step 1: Write the failing test** — rolling causal percentile rank of the current OI **level** within the trailing 2160-bar window; value in `[0,1]`; at row N uses only `[N-2159, N]`; delete-future invariance; `min_periods=2160` warmup yields NaN before the window fills.

```python
from factors.oi import oi_pct_rank_2160
def test_oi_pct_rank_causal_and_bounded():
    import numpy as np, pandas as pd
    s = pd.Series(np.r_[np.full(2159, 100.0), [500.0]])   # last value = window max
    out = oi_pct_rank_2160(pd.DataFrame({"sum_open_interest": s}))
    assert out.iloc[-1] == 1.0
    assert out.iloc[:2159].isna().all()           # warmup
    assert not np.isnan(out.iloc[2159])
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** (rolling window, causal percentile = fraction of window ≤ current; explicit count loop NOT `.mean()`, so the G1 AST scanner does not reject it)

```python
def oi_pct_rank_2160(df: pd.DataFrame) -> pd.Series:
    """Causal rolling percentile rank of the OI LEVEL (sum_open_interest) over the
    trailing 2160 bars (~90 days). At bar N: fraction of [N-2159, N] with value <=
    value[N]. Inputs: sum_open_interest. Warmup: 2160 bars (NaN before). Output:
    [0.0,1.0]. Explicit count loop, NOT .mean(), so the G1 AST scanner does not reject it."""
    def _rank(window: np.ndarray) -> float:
        last = window[-1]
        return sum(1 for v in window if v <= last) / len(window)
    return df["sum_open_interest"].astype("float64").rolling(
        window=2160, min_periods=2160).apply(_rank, raw=True)
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): oi_pct_rank_2160`.

### Task B4: `oi_velocity_ewm_240_pctrank_2160` (the H2 regime factor)

**Files:** Modify `factors/oi.py`; Test `tests/test_oi_factors.py`.

- [ ] **Step 1: Write the failing test** — causal rolling-2160 percentile of `oi_velocity_ewm_240`; same known-value + causality + warmup pattern as B3; the percentile's `min_periods=2160` dominates the inner 240-EWM warmup (LOCK §warmup).
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** (compose B2 then the B3 percentile pattern)

```python
def oi_velocity_ewm_240_pctrank_2160(df: pd.DataFrame) -> pd.Series:
    """Causal rolling-2160 percentile of oi_velocity_ewm_240 (the H2 regime axis).
    Inputs: sum_open_interest. Warmup: 2160 bars (the percentile min_periods dominates
    the 240-EWM warmup). Output: [0.0,1.0]. No future ops."""
    vel = _oi_log_change(df).ewm(span=240, adjust=False).mean()
    def _rank(window: np.ndarray) -> float:
        last = window[-1]
        return sum(1 for v in window if v <= last) / len(window)
    return vel.rolling(window=2160, min_periods=2160).apply(_rank, raw=True)
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): oi_velocity_ewm_240_pctrank_2160 (H2 regime factor)`.

### Task B5: Register OI factors + build integration (input_source widen + coverage-guarded join)

**Files:** Modify `factors/registry.py`, `factors/build_features.py`; Test `tests/test_oi_factors.py`, `tests/test_factors.py`, `tests/test_oi_build_routing.py`.

- [ ] **Step 1: Write the failing test** — **(a, CONTRACT-WIDEN, both-B2-legs blocker)** `FactorSpec(name="oi_sign", input_source="oi", ...)` constructs WITHOUT raising. *(Current `factors/registry.py` `__post_init__` raises unless `input_source ∈ {"ohlcv","funding","basis"}` — verified at `registry.py:116`; widen to add `"oi"` mirroring how Path A/C added their sources; the widen test ships in THIS task — the CONTRACT GAP.)* **(b)** the 4 OI factors appear in `registry.list_names()`; each passes G1 (AST no-future-ops) and G2 (future-bar invariance); `EXPECTED_FACTORS` in `tests/test_factors.py` updated; `feature_version` changes when an OI compute fn changes. **(c, coverage guard)** the `"oi"` build route raises if the OI 1h grid and the OHLCV 1h grid disagree by ≥1 bar over the overlap (the cross-stream join-integrity guard, parallel to Path C's `derive_basis_rel`).
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: (a) Widen the `input_source` contract FIRST.** In `factors/registry.py`, widen `FactorSpec.input_source`'s allow-set (and `Literal`/type if present) from `{"ohlcv","funding","basis"}` to add `"oi"`. CONTRACT GAP boundary — the widen test (Step 1a) ships here. **(b) Add the `"oi"` build route mirroring the existing injectable-frame pattern (B2 Codex):** add an `oi_df` parameter to `build_features_df(...)` (testable via injection, exactly like `funding_df`/`markprice_df`) and an `oi_path` to `build_features(...)` + the CLI (production loading at the top level, NOT inside the compute branch); when OI factors are present → compute the 4 OI factors on `oi_df`'s `sum_open_interest` column → **assert OI 1h `open_time_utc` coverage matches the OHLCV frame over the overlap (else RAISE — the §37.2-class silent-misalignment guard, OI-vs-OHLCV)** → left-join the OI factor columns onto the 1h OHLCV feature frame by `open_time_utc` (native-1h, same grid — NOT `merge_asof`); OHLCV/funding/basis factors compute unchanged. **(c) Register** the 4 OI factors in `_bootstrap_core_factors()` (import `factors.oi`), each `null_policy="nan_before_warmup_only"` + declared warmup (1, 240, 2160, 2160), tagged `input_source="oi"`. Update `EXPECTED_FACTORS`. *(NOTE: `oi_sign` is LOCK-registered for factor-family completeness/diagnostic; unlike Path C's `basis_sign` it is referenced by NO hypothesis — OI is directionless, so H1 carries no sign conjunct. Built + registered per the LOCK; it gates nothing.)*
- [ ] **Step 4: Run** the leakage-guard + factor suites — `python -m pytest tests/test_leakage_guards.py tests/test_oi_factors.py tests/test_oi_build_routing.py tests/test_factors.py -q` → all green. Rebuild the feature parquet (full dataset; `feature_version` bump). *(The OI-informed rows begin ~2020-09 + 2160-bar warmup ≈ 2020-12; earlier rows carry NaN OI factors — the immutable split is unchanged, §12 handicap.)*
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): register oi factors + build integration (input_source widen + coverage guard)`.

---

# PHASE C — Hypotheses + verdict harness  *(rest of downstream register B — build)*

> Phase C is mostly **adaptation** of the tested `pathc_*` harness to `pathd_*` retargeted at the OI cohort + the LOCKed OI hypotheses. The key DIVERGENCE: the dual D1/D2 diagnostic becomes **D1-only + the fenced contamination-correlation set** (decision A1/B2) — Task C6.

### Task C1: H1 OI DSL builder (NO time-stop, NO sign conjunct — simpler than Path C H1)

**Files:** Create `backtest/pathd_eval_gauntlet.py`; Test `tests/test_pathd_gauntlet.py`.

> H1 is **simpler than Path C's**: OI is directionless (no `oi_sign` conjunct), so the flat-tail is the single condition `oi_pct_rank_2160 ≥ θ`. H1 is a long-biased de-risk OVERLAY — long on the complement, NOT price-trend-gated (its D1 baseline is **always-long**, like Path C/A H1).

- [ ] **Step 1: Write the failing test** — `build_h1_dsl(theta=0.90)` returns a `StrategyDSL`: long when `oi_pct_rank_2160 < θ` (the ~90% complement), flat when `≥ θ`; **NO `max_hold`** (exit ONLY via the tail-gate — LOCK Note A); **NO price-trend conjunct, NO `oi_sign` conjunct**; vol-CDF ternary sizing `[0.3,0.8)→1.0 else 0.5`. Compiles via `compile_dsl_to_strategy(dsl, write_manifest=False)`; uses only registered factors.

```python
# tests/test_pathd_gauntlet.py
from backtest.pathd_eval_gauntlet import build_h1_dsl, referenced_factors
from strategies.dsl_compiler import compile_dsl_to_strategy

def test_h1_dsl_matches_lock_and_compiles():
    dsl = build_h1_dsl(theta=0.90)
    assert dsl.position_sizing != "full_equity"               # ternary SizingSpec
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)   # REAL compiler API; must not raise
    assert cls is not None
    # referenced_factors() also includes the sizing factor (it walks position_sizing), so
    # assert the ENTRY-condition factors for the exact "level-tail only, no sign/price-trend" check.
    entry_facs = {c.factor for g in dsl.entry for c in g.conditions}
    assert entry_facs == {"oi_pct_rank_2160"}                  # ONLY the level tail (no sign, no price-trend)
    assert "cdf_realized_vol_720" in referenced_factors(dsl)   # LOCKed ternary sizing present
    assert getattr(dsl, "max_hold_bars", None) in (None, 0)    # H1 has NO time-stop
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement `build_h1_dsl(theta=0.90)`** with the REAL DSL API. ENTRY = single group `[oi_pct_rank_2160 < θ]` (long on the complement); EXIT = single group `[oi_pct_rank_2160 ≥ θ]`. **NO `max_hold`** (LOCK Note A). Ternary `SizingSpec`. (Because there is no `oi_sign`/price conjunct, NO De Morgan is needed — simpler than Path C H1.) Also implement `referenced_factors(dsl)` (walks `dsl.entry`/`dsl.exit`/`dsl.position_sizing`).
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): H1 oi DSL builder (no time-stop, level-tail overlay)`.

### Task C2: H2 OI DSL builder

**Files:** Modify `backtest/pathd_eval_gauntlet.py`; Test `tests/test_pathd_gauntlet.py`.

- [ ] **Step 1: Write the failing test** — `build_h2_dsl()`: long when (regime permissive: `oi_velocity_ewm_240_pctrank_2160 < 0.80`) AND (`decay_linear_close_48 > decay_linear_close_168`); flat in the de-risk regime; `max_hold_bars=24`; compiles; uses `oi_velocity_ewm_240_pctrank_2160` (B4) + the decay-MA cross.
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** `build_h2_dsl()` — permissive gate `oi_velocity_ewm_240_pctrank_2160 < 0.80` AND the decay-MA cross (factor-vs-factor); exit on de-risk (`≥ 0.80`) / trend roll-over (`48 ≤ 168`) / `max_hold_bars=24`.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): H2 oi DSL builder`.

### Task C3: H3 OI DSL builder (strict partition; no embedded price conjunct beyond the decay cross)

**Files:** Modify `backtest/pathd_eval_gauntlet.py`; Test `tests/test_pathd_gauntlet.py`.

- [ ] **Step 1: Write the failing test** — `build_h3_dsl(theta=0.90)`: long when `oi_velocity_ewm_240 > 0` AND `oi_pct_rank_2160 < θ` (**strict** `<`) AND `decay_linear_close_48 > decay_linear_close_168`; exits per LOCK incl. `oi_pct_rank_2160 ≥ θ`; `max_hold_bars=48`; compiles. Assert H1/H3 are an **exact partition** on the pct-rank axis (H3 `< θ` vs H1 tail `≥ θ`). Assert the ONLY price leg is the decay cross (no second momentum conjunct — the graft fix).

```python
def test_h3_strict_partition_and_no_extra_price_conjunct():
    from backtest.pathd_eval_gauntlet import build_h3_dsl, referenced_factors
    dsl = build_h3_dsl(theta=0.90)
    # The "no extra price conjunct" check is on ENTRY conditions; referenced_factors() also
    # includes the LOCKed sizing factor cdf_realized_vol_720 (all 3 hypotheses size on it).
    entry_facs = {c.factor for g in dsl.entry for c in g.conditions}
    assert entry_facs == {"oi_velocity_ewm_240", "oi_pct_rank_2160",
                          "decay_linear_close_48", "decay_linear_close_168"}   # EXACTLY these — no 2nd price filter
    assert "cdf_realized_vol_720" in referenced_factors(dsl)                    # LOCKed ternary sizing present
    assert any(c.op == "<" and c.factor == "oi_pct_rank_2160" for g in dsl.entry for c in g.conditions)
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** `build_h3_dsl(theta=0.90)` (entry: `oi_velocity_ewm_240 > 0` AND `oi_pct_rank_2160 < θ` AND the decay cross — and NOTHING else; OR-group exits: `oi_velocity_ewm_240 <= 0` OR trend roll-over OR `oi_pct_rank_2160 >= θ` OR `max_hold_bars=48`).
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): H3 oi DSL builder (strict partition, no extra price conjunct)`.

### Task C4: Adapt the verdict harness modules (`pathc_* → pathd_*`)

**Files:** Create `backtest/pathd_holdout_producer.py`, `pathd_moments.py`, `pathd_dsr_fwer.py`, `pathd_earned_negative.py`, `pathd_escalation.py`, `pathd_train_sanity.py`, `pathd_orchestrator.py`; Tests `tests/test_pathd_*.py`.

- [ ] **Step 1:** For each, copy the corresponding `pathc_*` module, retarget the cohort to the 3 OI hypotheses + the OI feature columns, keep `PATHD_N_STAR = 3`, reuse `tier6_dsr.evaluate_candidate` + Form B + frozen `Z_PASS` unchanged. **Sealed `tier6_dsr_v1` byte-untouched** (assert sha256 in the test). `pathd_moments` inherits Path C's degenerate/flat-equity handling (`0d06c22d`: a 0-trade leg → Tier-5 non-pass, excluded from DSR, recorded). The §37.1 gate (`PHASE_D_AUTHORIZED` + injected `_run_backtest`) is preserved in `scripts/pathd_run_verdict.py` (Task D-gate) — re-verify it raises while unauthorized.
- [ ] **Step 1b (escalation prong):** `pathd_escalation.py` adapts `pathc_escalation.py` verbatim: prong keys on **`n_dsr_pass == 0`**. Signature `d_escalation_advisory(taxonomy, n_dsr_pass)`. Test `n_dsr_pass=0` (warranted) vs `>0` (not).
- [ ] **Step 1c (under-determined carve-out + thin-sample-SANE):** the under-determined carve-out ALREADY exists in `pathc_earned_negative.assemble_evidence` (verbatim-inherited) and keys on the **generic** predicate `eligible == False AND total_trades < UNDER_DETERMINED_TRADE_THRESHOLD(=10) AND holdout_sharpe >= 0` — **any floor, NOT specifically `zero_fraction`** (B2 Codex; LOCK Pre-reg 3) → tagged `under_determined=True`, NOT folded into the earned-negative. The **net-new** OI-specific addition: an under-powered-but-SANE H3 is annotated `consistent_with_momentum_or_vol_leakage=True` (NOT OI-mechanism evidence). Test: (a) under-floor + measured loss → substantive negative; (b) under-floor + thin-sample non-negative → `under_determined` (verify it triggers regardless of WHICH floor failed); (c) under-powered-but-SANE H3 → the leakage annotation.
- [ ] **Step 1d (tier threading — verify inherited):** the per-leg strong/weak-sane tier threading + `verdict_rests_on_weak_sane_only` ALREADY exist in `pathc_earned_negative` (verbatim-inherited; B2 advisor); verify they carry the OI cohort (`verdict_rests_on_weak_sane_only=True` when `any_mechanism_sane` rests solely on weak-sane legs). Test both cases.
- [ ] **Step 2:** Port each `pathc_*` test to `pathd_*` (mechanism IDs H1/H2/H3 OI names; same structural assertions).
- [ ] **Step 3:** Run `python -m pytest tests/test_pathd_*.py -q` → green; assert sealed `tier6_dsr_v1` sha256 4/4 unchanged.
- [ ] **Step 4: Commit** (await authorization) — `feat(pathd): adapt verdict harness pathc->pathd`.

### Task C5: Tiered 24h+72h mechanism-sanity (`pathd_perleg_mechanism.py`)

**Files:** Create `backtest/pathd_perleg_mechanism.py`; Test `tests/test_pathd_perleg.py`.

- [ ] **Step 1: Write the failing test** — for each leg, the train-only conditional-return sign is computed at **both** 24-bar and 72-bar horizons; both-sign → `strong_sane`; exactly-one → `weak_sane`; neither → `refuted`; per-leg record carries both horizon signs + the tier. H1 sane-sign NEGATIVE (reversal); H2 = permissive-mean > de-risk-mean AND permissive-mean > 0; H3 sane-sign POSITIVE.

```python
# tests/test_pathd_perleg.py
from backtest.pathd_perleg_mechanism import classify_leg
def test_strong_vs_weak_sane():
    assert classify_leg(mean_24h=+0.01, mean_72h=+0.02, sane_sign="+")["tier"] == "strong_sane"
    assert classify_leg(mean_24h=+0.01, mean_72h=-0.02, sane_sign="+")["tier"] == "weak_sane"
    assert classify_leg(mean_24h=-0.01, mean_72h=-0.02, sane_sign="+")["tier"] == "refuted"
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** `classify_leg` + the per-leg driver (adapt `pathc_perleg_mechanism.py` verbatim — horizon-agnostic; only the cohort wiring changes).
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): tiered 24h+72h mechanism sanity`.

### Task C6: D1-only marginal diagnostic + the fenced contamination-correlation set (the KEY Path C→D divergence)

**Files:** Create `backtest/pathd_marginal_diagnostic.py`; Test `tests/test_pathd_marginal.py`.

> **DIVERGENCE from Path C (decision A1/B2):** D1 is the inherited vs-momentum leg (renamed `oi_marginal_d1`). **D2 is DROPPED** — for the independent OI axis there is no derived-from relation, so `basis_marginal_d2` / `redundancy_read` / `d2_agrees` are **NOT** ported (assert ABSENT). The §38.3 inheritance is ONLY the "fenced-label-read-against-the-gate + inert-D1-is-modal" discipline. **NET-NEW:** the **fenced contamination-correlation set** (decision B2) quantifies the vol/liquidation residual.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathd_marginal.py
import numpy as np, pandas as pd, importlib
from backtest.pathd_marginal_diagnostic import (
    oi_marginal_d1, d1_noninert, D1_NONINERT_THRESHOLD, contamination_correlations)

def test_d1_is_fenced_diagnostic():
    gated    = np.array([1.0, 1.01, 1.00, 1.02])
    baseline = np.array([1.0, 1.02, 1.03, 1.05])
    out = oi_marginal_d1("H2", gated_equity=gated, baseline_equity=baseline)
    assert out["d1_marginal_sharpe"] < 0
    assert out["promotion_affecting"] is False and out["in_n_star"] is False

def test_d1_noninert_threshold():
    assert D1_NONINERT_THRESHOLD == 0.10
    assert d1_noninert(0.2) is True
    assert d1_noninert(0.05) is False     # inert -> modal "OI gate inert" read

def test_d2_machinery_absent():
    mod = importlib.import_module("backtest.pathd_marginal_diagnostic")
    for gone in ("oi_marginal_d2", "basis_marginal_d2", "redundancy_read", "d2_agrees"):
        assert not hasattr(mod, gone)     # A1: D2 dropped, asserted unwired

def test_contamination_correlations_fenced_and_reported():
    n = 200
    rng_like = np.linspace(-1, 1, n)
    df = pd.DataFrame({
        "oi_velocity_ewm_240": rng_like,
        "return_1h": rng_like * 0.5,
        "abs_return_1h": np.abs(rng_like * 0.5),
        "realized_vol_24h": np.abs(rng_like),
        "cdf_realized_vol_720": (rng_like + 1) / 2,
    })
    out = contamination_correlations(df)
    assert set(out["pearson"]) == {"return_1h", "abs_return_1h", "realized_vol_24h", "cdf_realized_vol_720"}
    assert "spearman" in out
    assert out["promotion_affecting"] is False and out["in_n_star"] is False
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement.** `oi_marginal_d1(hyp_id, gated_equity, baseline_equity)` = Sharpe delta vs the no-OI baseline (H2/H3: the price-trend strategy WITHOUT the OI gate; H1: always-long), fenced (`promotion_affecting=False, in_n_star=False`) — copy `pathc_marginal_diagnostic.basis_marginal_d1`, rename. `D1_NONINERT_THRESHOLD = 0.10`; `d1_noninert(d1_marginal_sharpe)` = `abs(...) > 0.10`. **Do NOT port `basis_marginal_d2` / `redundancy_read` / `d2_agrees`.** `contamination_correlations(df)` computes Pearson AND Spearman of `oi_velocity_ewm_240` vs `{return_1h, abs_return_1h, realized_vol_24h, cdf_realized_vol_720}` (where `abs_return_1h` is computed locally by the caller as `df['return_1h'].abs()` — NOT a registered factor; only `return_1h`/`realized_vol_24h`/`cdf_realized_vol_720` are registered) over the aligned non-NaN bars (caller passes the per-hypothesis signal-active forward bars and, separately, the train bars), returning `{"pearson": {...}, "spearman": {...}, "promotion_affecting": False, "in_n_star": False}` — measured-and-reported-only, never a control.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): D1-only diagnostic + fenced contamination-correlation set (D2 dropped)`.

### Task C7: Hypothesis-class floors (deterministic θ + frozen-θ floor + H2 de-risk occupancy)

**Files:** Modify `backtest/pathd_orchestrator.py`; Test `tests/test_pathd_floors.py`.

- [ ] **Step 1: Write the failing test** — H1 eligibility keys on the **count of defensive flat-exit episodes** (long→flat transitions driven by the OI level-tail) ≥ 200 on train; the **deterministic θ rule** applied first (`θ:=0.90; if H1 episodes at 0.90 < 200 → θ:=0.85`), the H1 floor judged at the **frozen θ**; H2/H3 on `zero_fraction < 0.50` AND ≥ 200 trades on train, **and H2 additionally requires de-risk-cell occupancy ≥ 10% of evaluated train bars**; floors on the TRAIN window only; under-floor → `INDETERMINATE`.

```python
# tests/test_pathd_floors.py
from backtest.pathd_orchestrator import resolve_theta, h1_floor_eligible, h2_derisk_occupancy_eligible
def test_deterministic_theta_and_frozen_floor():
    assert resolve_theta(episodes_at_090=150) == 0.85
    assert resolve_theta(episodes_at_090=250) == 0.90
    assert h1_floor_eligible(episodes_at_frozen_theta=210) is True
    assert h1_floor_eligible(episodes_at_frozen_theta=180) is False
def test_h2_derisk_occupancy_floor():
    assert h2_derisk_occupancy_eligible(occupancy=0.20) is True
    assert h2_derisk_occupancy_eligible(occupancy=0.08) is False
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** `resolve_theta(episodes_at_090)`, `h1_floor_eligible(episodes_at_frozen_theta)`, `h2_derisk_occupancy_eligible(occupancy)` (≥ 0.10), and the H2/H3 `zero_fraction`+trade-count floor (reuse Path C). The orchestrator resolves θ once on train, freezes it for H1+H3 jointly, then judges all floors at the frozen θ.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathd): hypothesis-class floors + deterministic theta`.

> **STOP — Phase B/C register boundary.** Full suite green + sealed sha256 4/4 unchanged + 2-leg B2 on the build. Await Phase D register.

---

# PHASE D — Run (forward_2026 verdict)  *(downstream register C — verdict run)*

> Phase D produces the actual verdict — a separate Charlie register, gated by `scripts/pathd_run_verdict.py`'s `PHASE_D_AUTHORIZED` flag + injected `_run_backtest` (the §37.1 function-boundary gate; the flag stays `False` in the repo). A pre-fire **PFR** (§38.4: trace the end-to-end gated entrypoint, not just modules) precedes the authorized run. Re-verify sealed `tier6_dsr_v1` sha256 BEFORE and AFTER.

### Task D1: Train-only mechanism-sanity table + θ resolution

- [ ] **Step 1:** Resolve θ on train (Task C7 deterministic rule) and freeze it for H1+H3.
- [ ] **Step 2:** Run `pathd_perleg_mechanism` on the train window (immutable 2020-2021+2023 split; OI factors NaN before ~2020-12 post-warmup) → per-leg conditional-return signs at 24h+72h + strong/weak/refuted tiers. Assert each leg's eligibility floor at the frozen θ. **No validation/test/forward touch.**
- [ ] **Step 3: Commit** the train-sanity artifact (await authorization).

### Task D2: Walk-forward train + forward_2026 Tier-5 holdout + D1 + contamination set

- [ ] **Step 1:** Walk-forward on train (`check_wf_semantics_or_raise`, `corrected_test_boundary_v1`).
- [ ] **Step 2:** Produce the **forward_2026** single-run holdout (`pathd_holdout_producer`, `check_evaluation_semantics_or_raise`, `single_run_holdout_v1`) → `holdout_sharpe` per hypothesis at 15 bps.
- [ ] **Step 3:** Run the **D1** diagnostic (vs no-OI baseline) + the **contamination-correlation set** (Task C6) on forward_2026 (and train, reported separately); record `d1_noninert` per hypothesis. **No D2 / `redundancy_read`** (dropped).
- [ ] **Step 4: Commit** the holdout + D1 + contamination artifacts (await authorization).

### Task D3: DSR-FWER N\*=3 + taxonomy + advisory

- [ ] **Step 1:** Build `pathd_moments` (CandidateMoments + integrity gate + degenerate-equity handling) from the forward holdout per-bar returns.
- [ ] **Step 2:** `pathd_dsr_fwer` at N\*=3 → `pass_B` survivors.
- [ ] **Step 3:** `pathd_earned_negative.assemble_evidence(...)` → taxonomy verdict (mechanism / process-refuted / d-positive), with the per-leg strong/weak-sane tiers threaded, the under-determined carve-out + thin-sample-SANE H3 leakage annotation, the D1 read (inert-modal) + the fenced contamination correlations, and the vol/liquidation residual + the 2020-09-under-power disclosure in the advisory bundle; escalation via `pathd_escalation.d_escalation_advisory(taxonomy, n_dsr_pass)` keyed on `n_dsr_pass == 0`.
- [ ] **Step 4:** Write `data/phase2c_evaluation_gate/pathd_verdict_v1/pathd_verdict_advisory.json`.
- [ ] **Step 5:** Re-verify sealed `tier6_dsr_v1` sha256 4/4 unchanged.
- [ ] **Step 6: Commit** the verdict artifact (await authorization).

### Task D4: Verdict read + cycle SEAL

- [ ] **Step 1:** 2-leg B2 on the verdict result (Codex + advisor).
- [ ] **Step 2:** Present the advisory verdict to Charlie for the **binding earned-negative-or-positive read** (Charlie register; never auto-fire). If `d_positive`: 2025 OOS confirmation required AND must survive the D1 attribution + the contamination disclosure before any promotion (and even then is not cleanly OI-vs-vol attributable). If earned-negative: the localization (independent positioning member, NOT family-level — liquidations/cross-sectional/short-legs/OI-scaled-sizing still untried) is recorded; the next axis is a *separate* future register (anti-pre-emption); the post-Path-D strategic fork (cross-sectional pivot vs equities/options) is the deferred dedicated-session item.
- [ ] **Step 3:** On Charlie's read: Phase Marker advance (CLAUDE.md + `docs/phase_marker_history.md`, atomic) + METHODOLOGY_NOTES lessons + `superpowers:finishing-a-development-branch`.

---

## Self-review (against the LOCK + spec)

- **Spec/LOCK coverage:** Pre-reg 1 (3 hypotheses, exact params, exact partition, deterministic θ, 4 factors incl. the nested H2 regime factor, `sum_open_interest` contracts, causal 1h downsample) → Tasks C1/C2/C3 + B1–B4 + the deterministic-θ floor C7 + A3 downsample + B5 (contracts input + widen). Pre-reg 2 (15bps, forward_2026 Tier-5, DSR-FWER N\*=3) → D2/D3 + C4. Pre-reg 3 (cost-aware, floors incl. the H2 ≥10% occupancy → C7, single-factor sizing, causal OI derivation, **D1-only** + the fenced contamination set, D2 asserted unwired, the labeling tolerances `D1_NONINERT_THRESHOLD=0.10` / `UNDER_DETERMINED_TRADE_THRESHOLD=10`) → A3/B5/C6/C7; the `input_source="oi"` registry contract-widen → B5 Step 3a. Pre-reg 4 (taxonomy incl. under-determined + thin-sample-SANE, tiered sanity, escalation, localization) → C4/C5/D3. Ingestion design (spec §5; header-autodetect §38.2; §38.1 first-run-validation) → Phase A (A2 header-autodetect, A7 re-verify). Harness reuse (spec §4) → C4. D1-only + contamination (spec §9; A1/B2) → C6. **No gap found:** every Pre-reg 1–4 maps to a task; no LOCKed value altered.
- **Placeholder scan:** ingestion reconcile (A5) + incremental (A6) + the harness adapts (C4) reference the existing tested `pathc_*`/`markprice_*` modules as the pattern rather than re-printing them — acceptable (near-verbatim mirrors of tested code); the genuinely-new logic (header-autodetect parse, causal downsample, the 4 OI factors, the H1/H2/H3 builders, the D1-only + contamination diagnostic, the deterministic-θ floor, the input_source widen) has full code/tests. No "TBD"/"handle edge cases" placeholders.
- **Type/name consistency:** factor names (`oi_sign`, `oi_velocity_ewm_240`, `oi_pct_rank_2160`, `oi_velocity_ewm_240_pctrank_2160`) + the `_oi_log_change` helper; `parse_metrics_csv(path)`, `downsample_oi_to_1h(df5)`, `validate_oi(df)`; `classify_leg(mean_24h, mean_72h, sane_sign)`; `oi_marginal_d1(hyp_id, gated_equity, baseline_equity)`, `d1_noninert(x)`, `D1_NONINERT_THRESHOLD=0.10`, `contamination_correlations(df)` (NO `oi_marginal_d2`/`redundancy_read`/`d2_agrees`); `referenced_factors(dsl)`, `d_escalation_advisory(taxonomy, n_dsr_pass)`, `resolve_theta(episodes_at_090)`, `h1_floor_eligible(episodes_at_frozen_theta)`, `h2_derisk_occupancy_eligible(occupancy)`, `compile_dsl_to_strategy(dsl, write_manifest=False)`, `PATHD_N_STAR=3`, `build_h1/h2/h3_dsl(theta=0.90)` — used consistently. H1 has NO `max_hold` and NO sign/price conjunct everywhere; H3 uses strict `<` everywhere; the OI signal column is `sum_open_interest` (contracts) everywhere.
- **Register boundaries:** Phase A / B+C / D STOP markers present; per-task commits gated on Charlie authorization; the §37.1 `PHASE_D_AUTHORIZED` gate guards the real run; the A7 integration run is the §38.1 format-validation gate.

---

## Execution handoff

This plan is the scoping cycle's final deliverable. Per the register discipline, **execution does not begin until Charlie registers Phase A**. When execution is authorized, the recommended approach is **subagent-driven-development** (fresh subagent per task + two-stage review), with a 2-leg B2 at each phase boundary (Charlie-instructed). Ingestion (Phase A), build (Phase B/C), and run (Phase D) are each their own Charlie register-event.
