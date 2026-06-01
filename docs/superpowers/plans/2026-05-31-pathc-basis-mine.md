# Path C — Perp-Spot Basis Axis Mechanism-First Mine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build + run the bounded, pre-registered one-cycle falsification test of the perp-spot **basis** information axis: ingest Binance mark/index 1h klines, derive the native-1h `basis_rel` series + 5 causal basis factors, express the 3 LOCKed basis hypotheses (H1/H2/H3) in the DSL, reuse the Path A verdict harness retargeted to basis, add the **dual-orthogonalization** (D1 vs-momentum + D2 vs-funding) diagnostic, and produce the forward_2026 earned-negative-or-positive verdict.

**Architecture:** Mirror Path A's pipeline exactly, swapping the *data family* (funding → basis) while holding the *process* fixed. Basis is **native 1h** — `basis_rel[t] = (mark_close[t] − spot_close[t]) / spot_close[t]` derived by a same-grid join of mark-price klines to the existing canonical Binance spot 1h close — so there is **NO cross-cadence carry** (the §37.2 funding 8h→1h complexity disappears; it is replaced by a cross-*stream* join-integrity guard). Five causal basis factors compute on the 1h `basis_rel` series, the 3 hypotheses compile through the existing DSL (no new schema), the `patha_*` verdict harness is adapted to `pathc_*` for a new basis cohort, and the funding-marginal diagnostic is extended to the dual D1/D2 orthogonalization (D2 reuses the on-`main` Path A funding-gated strategies). Sealed `tier6_dsr_v1` artifacts stay byte-identical throughout.

**Tech Stack:** Python 3.11, pandas/pyarrow (parquet), CCXT (incremental mark/index), Backtrader (engine), scipy (DSR), pytest (TDD). All UTC.

**Governing LOCK:** [`../specs/2026-05-31-pathc-step-minus-1-preregistration-lock.md`](../specs/2026-05-31-pathc-step-minus-1-preregistration-lock.md) — **frozen; no task may alter a LOCKed value.** Design spec: [`../specs/2026-05-31-path-c-basis-scoping-design.md`](../specs/2026-05-31-path-c-basis-scoping-design.md).

**Register discipline (CRITICAL):** This plan spans **three separate downstream Charlie register-events** — Phase A (ingestion = first data touch), Phase B+C (build), Phase D (run). **Each phase boundary requires an explicit Charlie register before proceeding.** Per-task commits await Charlie authorization. The plan is the scoping deliverable; authoring it authorizes no execution.

**Baseline:** full suite 2895 passed / 9 skipped / 2 xfailed; pc9 = 2780. Sealed `tier6_dsr_v1/` sha256: `0a7d98…` / `8eecc6…` / `49646c…` / `1803eb…` (re-verify before AND after any Phase D task).

---

## File structure

| File | Responsibility | New/Modify |
|---|---|---|
| `config/schemas.yaml` | add `markprice` schema block (mark/index 1h kline columns + validation) | Modify |
| `ingestion/markprice_bulk_download.py` | Binance Vision bulk `monthly/markPriceKlines/BTCUSDT/1h/` + `indexPriceKlines/BTCUSDT/1h/` → parquet (mirrors `bulk_download.py`) | Create |
| `ingestion/markprice_incremental_update.py` | CCXT mark/index incremental/forward update | Create |
| `ingestion/markprice_reconcile.py` | merge + archive-before-overwrite + source-priority dedup for markprice | Create |
| `ingestion/validators.py` | extend to validate the `markprice` schema (UTC PK, sorted, 1h spacing, cross-check tolerance) | Modify |
| `data/raw/btcusdt_markprice_1h.parquet` | canonical mark/index 1h series (output) | Create (Phase A run) |
| `factors/basis_derive.py` | derive native-1h `basis_rel` by same-grid join of mark_close to spot_close + cross-stream join-integrity guard | Create |
| `factors/basis.py` | `basis_sign`, `basis_ewm_240`, `basis_ewm_480`, `basis_pct_rank_2160`, `basis_ewm_240_pctrank_2160` (causal, on the 1h `basis_rel` series) | Create |
| `factors/registry.py` | register the 5 basis factors; `feature_version` bump | Modify |
| `factors/build_features.py` | integrate the basis derivation + factors into the full-dataset build (`input_source="basis"` routing) | Modify |
| `backtest/pathc_eval_gauntlet.py` | H1/H2/H3 basis DSL builders + EVAL gauntlet (adapt `patha_eval_gauntlet.py`) | Create |
| `backtest/pathc_holdout_producer.py` | forward_2026 single-run holdout producer (adapt `patha_holdout_producer.py`) | Create |
| `backtest/pathc_moments.py` | CandidateMoments constructor + integrity gate (adapt `patha_moments.py`) | Create |
| `backtest/pathc_dsr_fwer.py` | DSR-FWER N\*=3 over the basis cohort (adapt `patha_dsr_fwer.py`) | Create |
| `backtest/pathc_perleg_mechanism.py` | tiered 24h+72h strong/weak-sane mechanism-sanity (adapt `patha_perleg_mechanism.py`) | Create |
| `backtest/pathc_marginal_diagnostic.py` | **dual-orthogonalization** D1 (vs momentum) + D2 (vs funding), fenced (extend `patha_marginal_diagnostic.py`) | Create |
| `backtest/pathc_escalation.py` | next-axis escalation advisory keyed on `n_dsr_pass == 0` (adapt `patha_escalation.py`) | Create |
| `backtest/pathc_earned_negative.py` | taxonomy + advisory assembly incl. the F3 under-determined carve-out (adapt `patha_earned_negative.py`) | Create |
| `backtest/pathc_train_sanity.py` | train-only mechanism-sanity table driver (adapt `patha_train_sanity.py`) | Create |
| `backtest/pathc_orchestrator.py` | end-to-end run_pathc_verdict (adapt `patha_orchestrator.py`) | Create |
| `scripts/pathc_run_verdict.py` | gated forward_2026 verdict run entrypoint (adapt `scripts/patha_run_verdict.py`; `PHASE_D_AUTHORIZED` gate + injected `_run_backtest`) | Create |

Tests live beside the suite: `tests/test_markprice_ingestion.py`, `tests/test_basis_derive.py`, `tests/test_basis_factors.py`, `tests/test_pathc_*.py`.

---

# PHASE A — Basis ingestion  *(downstream Charlie register A — first data touch)*

> Phase A is the first data touch. Do NOT begin until Charlie registers Phase A. The LOCK is already committed (anti-hindsight), so ingesting basis now cannot reverse-fit the hypotheses. **No basis VALUES in the forward_2026 window may be inspected during build/test** — fixtures use synthetic values only.

### Task A1: Markprice schema block

**Files:**
- Modify: `config/schemas.yaml` (add top-level `markprice` block, mirroring the `ohlcv` block structure)
- Test: `tests/test_markprice_ingestion.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_markprice_ingestion.py
import yaml
from pathlib import Path

def test_markprice_schema_block_exists():
    schemas = yaml.safe_load(Path("config/schemas.yaml").read_text())
    m = schemas["markprice"]
    assert m["primary_key"] == "open_time_utc"
    cols = set(m["columns"].keys())   # columns is a name-keyed MAPPING (mirror the ohlcv block)
    assert {"open_time_utc", "mark_close", "index_close",
            "source", "ingested_at_utc"} <= cols
    assert set(m["columns"]["source"]["allowed_values"]) >= {"binance_vision", "ccxt_binance"}
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_markprice_ingestion.py::test_markprice_schema_block_exists -v`
Expected: FAIL (KeyError 'markprice').

- [ ] **Step 3: Add the `markprice` block to `config/schemas.yaml`**

```yaml
# Mirrors the existing `ohlcv` block structure exactly: columns is a NAME-KEYED
# MAPPING (not a list), source allowed values live under the source column's
# allowed_values, validation_rules is a list of {name, check, severity?}.
markprice:
  description: "Binance USDT-M perpetual mark price + index price, 1h klines for BTCUSDT (basis axis)"
  primary_key: "open_time_utc"
  sort_order: "open_time_utc ASC"
  file_pattern: "data/raw/btcusdt_markprice_1h.parquet"
  columns:
    open_time_utc:
      dtype: "datetime64[ms, UTC]"
      nullable: false
      description: "Kline open time, UTC tz-aware, unique, sorted ascending, hour-aligned"
    mark_close:
      dtype: "float64"
      nullable: false
      description: "markPriceKlines close (smoothed perp fair value) for the 1h bar ending at open_time_utc+1h"
    index_close:
      dtype: "float64"
      nullable: false
      description: "indexPriceKlines close (multi-venue spot index); cross-check only, not a signal"
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
      check: "consecutive open_time_utc differ by exactly 3600000 ms (±0 tolerance; ms-jitter handled at parse)"
    - name: "no_forward_fill"
      check: "missing bars flagged in the quality report, never interpolated"
      severity: "warning"
```

> **NOTE (B2 advisor Finding 4 — spec→plan narrowing, non-LOCKed):** the schema stores `mark_close` + `index_close` only (not the full mark OHLC the spec §5 lists). `basis_rel` needs only the two closes, so this is a deliberate DoF-minimization touching no LOCKed value; it does not foreclose mark OHLC — a later factor needing it can extend the schema at the ingestion register.

- [ ] **Step 4: Run to verify it passes**

Run: `python -m pytest tests/test_markprice_ingestion.py::test_markprice_schema_block_exists -v`
Expected: PASS.

- [ ] **Step 5: Commit** (await Charlie authorization)

```bash
git add config/schemas.yaml tests/test_markprice_ingestion.py
git commit -F /tmp/msg.txt   # "feat(pathc): markprice schema block"
```

### Task A2: Markprice bulk download (Binance Vision)

**Files:**
- Create: `ingestion/markprice_bulk_download.py`
- Test: `tests/test_markprice_ingestion.py`

- [ ] **Step 1: Write the failing test** (parse a fixture CSV in the real Binance Vision kline format — 12 headerless columns)

```python
# tests/test_markprice_ingestion.py  (append)
import pandas as pd
from ingestion.markprice_bulk_download import parse_kline_csv

def test_parse_markprice_kline_real_format(tmp_path):
    # Binance Vision *PriceKlines: 12 headerless cols
    # open_time, open, high, low, close, volume, close_time, quote_vol, count, taker_base, taker_quote, ignore
    csv = tmp_path / "BTCUSDT-1h-2020-01.csv"
    csv.write_text(
        "1577836800000,7000,7010,6990,7005,0,1577840399999,0,0,0,0,0\n"
        "1577840400000,7005,7020,7000,7012,0,1577843999999,0,0,0,0,0\n"
    )
    df = parse_kline_csv(csv, close_col_name="mark_close")
    assert list(df["open_time_utc"]) == [
        pd.Timestamp("2020-01-01 00:00:00", tz="UTC"),
        pd.Timestamp("2020-01-01 01:00:00", tz="UTC"),
    ]
    assert df["mark_close"].tolist() == [7005.0, 7012.0]
    assert str(df["open_time_utc"].dtype) == "datetime64[ms, UTC]"
    assert (df["source"] == "binance_vision").all()
```

- [ ] **Step 2: Run to verify it fails** — `ModuleNotFoundError`.

- [ ] **Step 3: Implement `parse_kline_csv` + the bulk downloader**

```python
# ingestion/markprice_bulk_download.py
"""Bulk download Binance Vision USDT-M markPrice + indexPrice 1h klines for BTCUSDT.

Mirrors ingestion/bulk_download.py: download monthly ZIPs from data.binance.vision,
parse to parquet. (bulk_download.py does NOT verify checksums — no .CHECKSUM step to
mirror.) Mark/index klines are 12-col headerless; open_time is ms epoch UTC.
Sources:
  data/futures/um/monthly/markPriceKlines/BTCUSDT/1h/  (history from 2020-01)
  data/futures/um/monthly/indexPriceKlines/BTCUSDT/1h/ (history from 2020-01)
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import logging
import pandas as pd

MARK_PREFIX = "data/futures/um/monthly/markPriceKlines/BTCUSDT/1h/"
INDEX_PREFIX = "data/futures/um/monthly/indexPriceKlines/BTCUSDT/1h/"
OUTPUT_PATH = Path("data/raw/btcusdt_markprice_1h.parquet")
_KLINE_COLS = ["open_time", "open", "high", "low", "close", "volume",
               "close_time", "quote_volume", "count", "taker_base", "taker_quote", "ignore"]

def parse_kline_csv(path: Path, close_col_name: str) -> pd.DataFrame:
    """Parse one Binance Vision 12-col headerless kline CSV, keeping only the close.

    Inputs: a headerless CSV with the 12 standard kline columns.
    Output: open_time_utc(datetime64[ms,UTC] PK), <close_col_name>(float64),
      source(string), ingested_at_utc(datetime64[ms,UTC]).
    Null policy: rows with NaN open_time/close are dropped + counted (logged)."""
    raw = pd.read_csv(path, header=None, names=_KLINE_COLS)
    n_in = len(raw)
    raw = raw.dropna(subset=["open_time", "close"])
    n_dropped = n_in - len(raw)
    if n_dropped:
        logging.info("parse_kline_csv: dropped %d NaN row(s) from %s", n_dropped, path.name)
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(raw["open_time"], unit="ms", utc=True).astype("datetime64[ms, UTC]"),
        close_col_name: raw["close"].astype("float64"),
    })
    df["source"] = pd.array(["binance_vision"] * len(df), dtype="string")
    df["ingested_at_utc"] = pd.Timestamp(datetime.now(timezone.utc)).as_unit("ms")
    return df.sort_values("open_time_utc").reset_index(drop=True)
```
(The download/unzip wrapper mirrors `bulk_download.py`'s `main()`: download both `MARK_PREFIX` and `INDEX_PREFIX` monthly ZIPs from `--start 2020-01`, parse each with `close_col_name="mark_close"` / `"index_close"`, **inner-join the two on `open_time_utc`** into the markprice frame, argparse + `--dry-run`, log rows-before/after. **No checksum step.**)

- [ ] **Step 4: Run to verify it passes** — PASS.
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): markprice bulk download + kline parse`.

### Task A3: Markprice validators (incl. cross-check tolerance)

**Files:**
- Modify: `ingestion/validators.py` (add `validate_markprice(df)`)
- Test: `tests/test_markprice_ingestion.py`

- [ ] **Step 1: Write the failing test**

```python
from ingestion.validators import validate_markprice
import pandas as pd

def _good():
    return pd.DataFrame({
        "open_time_utc": pd.to_datetime([1577836800000, 1577840400000], unit="ms", utc=True).as_unit("ms"),
        "mark_close": [7005.0, 7012.0], "index_close": [7004.0, 7011.0],
        "source": ["binance_vision"]*2, "ingested_at_utc": pd.to_datetime([0,0], unit="ms", utc=True).as_unit("ms"),
    })

def test_validate_markprice_accepts_good():
    assert validate_markprice(_good())["ok"] is True

def test_validate_markprice_rejects_duplicate_pk():
    df = _good(); df.loc[1, "open_time_utc"] = df.loc[0, "open_time_utc"]
    r = validate_markprice(df)
    assert r["ok"] is False and "duplicate" in r["errors"][0].lower()

def test_validate_markprice_flags_mark_index_wedge():
    # (mark-index)/index far above a sane perp premium -> warning, not silent pass
    df = _good(); df.loc[0, "mark_close"] = 7004.0 * 2.0
    r = validate_markprice(df)
    assert any("wedge" in w.lower() or "cross-check" in w.lower() for w in r["warnings"])
```

- [ ] **Step 2: Run to verify it fails** — ImportError.
- [ ] **Step 3: Implement `validate_markprice`** (UTC tz-aware, unique+sorted PK, exact 3,600,000 ms spacing with ms-jitter rounded at parse, allowed source; the `(mark_close − index_close)/index_close` cross-check must stay within a pinned tolerance `MARK_INDEX_WEDGE_TOL = 0.05` (5% — a benign perp premium is ≪1%, so 5% bounds a real ingestion bug without false-flagging) → over-tolerance rows are **warnings** not errors; gaps flagged not removed; returns `{"ok": bool, "errors": [...], "warnings": [...], "rows": n}`). Mirror the OHLCV validator structure; non-zero exit on failure in the CLI path.
- [ ] **Step 4: Run to verify it passes** — PASS.
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): markprice validators + cross-check tolerance`.

### Task A4: Markprice reconcile + archive

**Files:**
- Create: `ingestion/markprice_reconcile.py`
- Test: `tests/test_markprice_ingestion.py`

- [ ] **Step 1: Write the failing test** — archive-before-overwrite writes a snapshot to `data/raw/archive/btcusdt_markprice_1h_<ts>.parquet`; dedup on `open_time_utc` preferring `binance_vision` over `ccxt_binance`; output unique+sorted.
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** mirroring `ingestion/reconcile.py` (`archive_file`, `SOURCE_PRIORITY = {"binance_vision": 0, "ccxt_binance": 1}`, merge+dedup+sort). Markprice is a distinct file — no cross-venue OHLCV interaction.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): markprice reconcile + archive`.

### Task A5: CCXT incremental markprice update

**Files:**
- Create: `ingestion/markprice_incremental_update.py`
- Test: `tests/test_markprice_ingestion.py` (mock the CCXT client)

- [ ] **Step 1: Write the failing test** — a mocked exchange whose `fetch_mark_ohlcv` / `fetch_index_ohlcv` (CCXT Python snake_case — the SAME names the implementation calls) return rows normalized to the markprice schema (UTC PK, source `ccxt_binance`), inner-joined on `open_time_utc`.
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** mirroring `ingestion/incremental_update.py` (`create_exchange`, paginated `fetch_mark_ohlcv(symbol="BTC/USDT:USDT", timeframe="1h", since=...)` + `fetch_index_ohlcv(...)`, retry logic, normalize + inner-join to schema).
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): markprice incremental update (CCXT)`.

### Task A6: Phase A integration run (ACTUAL data touch — Charlie-gated)

- [ ] **Step 1:** `python -m ingestion.markprice_bulk_download --pair BTCUSDT --start 2020-01` → `data/raw/btcusdt_markprice_1h.parquet`.
- [ ] **Step 2:** `python -m ingestion.validators --markprice data/raw/btcusdt_markprice_1h.parquet --report data/quality/` → assert `ok: True`; document FTX-Nov-2022 + post-ETF-Jan-2024 basis-compression characteristics in the report (flagged, not cleaned).
- [ ] **Step 3:** sanity: row count ≈ 24/day × ~6.3y ≈ ~55k rows (≈ the spot parquet's 55,105); first `open_time_utc == 2020-01-01T00:00:00Z`; consecutive spacing exactly 3,600,000 ms (log any exception); **cross-stream coverage** matches the spot parquet's `open_time_utc` over the overlap (Task B0 asserts this). **Do NOT inspect 2026 basis values** (no-peek).
- [ ] **Step 4: Commit** the data-availability report (NOT the raw parquet if policy excludes large binaries; follow the OHLCV convention) — await authorization.

> **STOP — Phase A register boundary.** Report ingestion results to Charlie; await Phase B register.

---

# PHASE B — Basis derivation + feature pipeline  *(part of downstream register B — build)*

### Task B0: Native-1h `basis_rel` derivation + cross-stream join-integrity (`factors/basis_derive.py`)

**Files:** Create `factors/basis_derive.py`; Test `tests/test_basis_derive.py`.

> This REPLACES Path A's 8h→1h carry. Basis is native-1h, so the derivation is a *same-grid* join of mark to spot — no `merge_asof`, no carry. The new leakage surface is **cross-stream alignment** (futures mark grid vs spot grid), guarded here (B2 advisor Finding 6).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_basis_derive.py
import pandas as pd, pytest
from factors.basis_derive import derive_basis_rel

def _mark():
    return pd.DataFrame({"open_time_utc": pd.to_datetime(
        ["2020-01-01 00:00","2020-01-01 01:00"], utc=True), "mark_close": [7005.0, 7012.0]})
def _spot():
    return pd.DataFrame({"open_time_utc": pd.to_datetime(
        ["2020-01-01 00:00","2020-01-01 01:00"], utc=True), "close": [7000.0, 7000.0]})

def test_basis_rel_same_grid_join():
    out = derive_basis_rel(_mark(), _spot())
    assert out["basis_rel"].tolist() == pytest.approx([(7005-7000)/7000, (7012-7000)/7000])

def test_basis_rel_raises_on_cross_stream_misalignment():
    mark = _mark()
    spot = _spot().iloc[:1]   # spot missing the 01:00 bar -> one-bar misalignment
    with pytest.raises(ValueError, match="cross-stream"):
        derive_basis_rel(mark, spot)

def test_basis_rel_raises_on_zero_overlap():
    mark = _mark()  # 2020-01-01 00:00 / 01:00
    spot = pd.DataFrame({"open_time_utc": pd.to_datetime(
        ["2021-01-01 00:00","2021-01-01 01:00"], utc=True), "close": [30000.0, 30000.0]})
    with pytest.raises(ValueError, match="cross-stream"):   # no overlapping window
        derive_basis_rel(mark, spot)
```

- [ ] **Step 2: Run to verify it fails** — ImportError.
- [ ] **Step 3: Implement** (same-grid inner-join, raise on misalignment)

```python
# factors/basis_derive.py
"""Derive the native-1h perp-spot basis series.

DESIGN INVARIANT (no carry): basis_rel[t] = (mark_close[t] - spot_close[t]) / spot_close[t],
joined on open_time_utc at the SAME 1h grid (mark and spot are both bar-N-close values;
orders fill at N+1 open per the execution convention). The only leakage surface is
cross-STREAM alignment (futures mark grid vs spot grid), guarded by an explicit
exact-coverage assertion: a one-bar misalignment RAISES rather than silently pairing
mark@t with spot@t±1 (the §37.2-class silent unit bug, one venue-pair removed)."""
from __future__ import annotations
import pandas as pd

def derive_basis_rel(mark: pd.DataFrame, spot: pd.DataFrame) -> pd.DataFrame:
    """mark has (open_time_utc, mark_close); spot has (open_time_utc, close).
    Returns (open_time_utc, basis_rel) on the shared grid. Raises ValueError if the
    two streams do not share identical open_time_utc coverage over the overlap."""
    m = mark[["open_time_utc", "mark_close"]].sort_values("open_time_utc").reset_index(drop=True)
    s = spot[["open_time_utc", "close"]].rename(columns={"close": "spot_close"}) \
            .sort_values("open_time_utc").reset_index(drop=True)
    lo = max(m["open_time_utc"].min(), s["open_time_utc"].min())
    hi = min(m["open_time_utc"].max(), s["open_time_utc"].max())
    if lo > hi:                                          # B2 Codex robustness: no overlap -> raise, not empty
        raise ValueError("cross-stream: no overlapping window between mark and spot")
    # NOTE: set() de-dups silently, but the markprice + spot PK-uniqueness validators
    # (Task A3 / OHLCV) already guarantee unique open_time_utc, so no row is lost here.
    m_o = set(m.loc[(m.open_time_utc >= lo) & (m.open_time_utc <= hi), "open_time_utc"])
    s_o = set(s.loc[(s.open_time_utc >= lo) & (s.open_time_utc <= hi), "open_time_utc"])
    if m_o != s_o:
        missing = (m_o ^ s_o)
        raise ValueError(f"cross-stream grid misalignment: {len(missing)} non-shared bar(s) in overlap")
    merged = m.merge(s, on="open_time_utc", how="inner")
    merged["basis_rel"] = (merged["mark_close"] - merged["spot_close"]) / merged["spot_close"]
    return merged[["open_time_utc", "basis_rel"]]
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): native-1h basis_rel derivation + cross-stream guard`.

### Task B1: `basis_sign` factor

**Files:** Create `factors/basis.py`; Test `tests/test_basis_factors.py`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_basis_factors.py
import pandas as pd
from factors.basis import basis_sign

def test_basis_sign():
    s = pd.Series([0.002, -0.001, 0.0, 0.0005])
    out = basis_sign(pd.DataFrame({"basis_rel": s}))
    assert out.tolist() == [1.0, -1.0, 0.0, 1.0]
```

- [ ] **Step 2: Run to verify it fails** — ImportError.
- [ ] **Step 3: Implement** (top-level named, causal, no future ops)

```python
# factors/basis.py
"""Perp-spot basis factors computed on the native-1h basis_rel series (causal,
rolling over 1h bars — NO carry; basis is native-1h). All factors are top-level
named callables, rolling/causal only (pass G1-G4). Input: a DataFrame with a
'basis_rel' column on the 1h grid (from factors.basis_derive)."""
from __future__ import annotations
import numpy as np
import pandas as pd

def basis_sign(df: pd.DataFrame) -> pd.Series:
    """Sign of the basis. Inputs: basis_rel. Warmup: 0.
    Output: {-1.0, 0.0, 1.0}. Null policy: NaN basis_rel -> NaN."""
    return np.sign(df["basis_rel"]).astype("float64")
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): basis_sign factor`.

### Task B2: `basis_ewm_240` and `basis_ewm_480`

**Files:** Modify `factors/basis.py`; Test `tests/test_basis_factors.py`.

- [ ] **Step 1: Write the failing test** — `basis_ewm_240(df)` equals `df["basis_rel"].ewm(span=240, adjust=False).mean()`; assert `adjust=False`; assert causality (value at row N independent of rows > N — delete-future invariance).
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement**

```python
def basis_ewm_240(df: pd.DataFrame) -> pd.Series:
    """Causal EWM of basis_rel, span=240 bars (~10 days = Path A's 30 settlements x8),
    adjust=False. Inputs: basis_rel. Warmup: ~240 bars. Null: NaN before first obs."""
    return df["basis_rel"].ewm(span=240, adjust=False).mean()

def basis_ewm_480(df: pd.DataFrame) -> pd.Series:
    """Causal EWM of basis_rel, span=480 bars (~20 days = Path A's 60 settlements x8), adjust=False."""
    return df["basis_rel"].ewm(span=480, adjust=False).mean()
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): basis_ewm_240/480`.

### Task B3: `basis_pct_rank_2160`

**Files:** Modify `factors/basis.py`; Test `tests/test_basis_factors.py`.

- [ ] **Step 1: Write the failing test** — rolling causal percentile rank of the current basis within the trailing 2160-bar window; value in `[0, 1]`; at row N uses only `[N-2159, N]`; delete-future invariance; `min_periods=2160` warmup yields NaN before the window fills.

```python
from factors.basis import basis_pct_rank_2160
def test_basis_pct_rank_causal_and_bounded():
    import numpy as np, pandas as pd
    s = pd.Series(np.r_[np.zeros(2159), [5.0]])   # 2160 rows; last value is the max of its window
    out = basis_pct_rank_2160(pd.DataFrame({"basis_rel": s}))
    assert out.iloc[-1] == 1.0
    assert out.iloc[:2159].isna().all()           # warmup: indices 0..2158 NaN (min_periods=2160)
    assert not np.isnan(out.iloc[2159])
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** (rolling window, causal percentile = fraction of window ≤ current value; explicit count loop NOT `.mean()`, so the G1 AST scanner does not reject it)

```python
def basis_pct_rank_2160(df: pd.DataFrame) -> pd.Series:
    """Causal rolling percentile rank of basis_rel over the trailing 2160 bars
    (~90 days = Path A's 270 settlements x8). At bar N: fraction of [N-2159, N] with
    value <= value[N]. Inputs: basis_rel. Warmup: 2160 bars (NaN before). Output:
    [0.0, 1.0]. No future ops (rolling, right-closed). Uses an explicit count loop,
    NOT .mean(), so the G1 AST scanner does not reject it."""
    def _rank(window: np.ndarray) -> float:
        last = window[-1]
        count = sum(1 for v in window if v <= last)
        return count / len(window)
    return df["basis_rel"].rolling(window=2160, min_periods=2160).apply(_rank, raw=True)
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): basis_pct_rank_2160`.

### Task B4: `basis_ewm_240_pctrank_2160` (the H2 regime factor)

**Files:** Modify `factors/basis.py`; Test `tests/test_basis_factors.py`.

- [ ] **Step 1: Write the failing test** — causal rolling-2160 percentile of `basis_ewm_240`; same known-value + causality + warmup pattern as B3; the percentile's `min_periods=2160` dominates the inner 240-EWM warmup (LOCK §warmup).
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** (compose B2 then the B3 percentile pattern)

```python
def basis_ewm_240_pctrank_2160(df: pd.DataFrame) -> pd.Series:
    """Causal rolling-2160 percentile of basis_ewm_240 (the H2 regime axis).
    Inputs: basis_rel. Warmup: 2160 bars (the percentile min_periods dominates the
    240-EWM warmup). Output: [0.0, 1.0]. No future ops."""
    ewm = df["basis_rel"].ewm(span=240, adjust=False).mean()
    def _rank(window: np.ndarray) -> float:
        last = window[-1]
        return sum(1 for v in window if v <= last) / len(window)
    return ewm.rolling(window=2160, min_periods=2160).apply(_rank, raw=True)
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): basis_ewm_240_pctrank_2160 (H2 regime factor)`.

### Task B5: Register basis factors + build integration

**Files:** Modify `factors/registry.py`, `factors/build_features.py`; Test `tests/test_basis_factors.py`, `tests/test_factors.py`.

- [ ] **Step 1: Write the failing test** — **(a, B2 CONVERGENT BLOCKER fix)** `FactorSpec(name="basis_sign", input_source="basis", ...)` constructs WITHOUT raising. *(Current `factors/registry.py` `__post_init__` raises `ValueError` unless `input_source ∈ {"ohlcv","funding"}` — verified at `registry.py:116`; this is the one build-breaker both B2 legs caught. The widen + its test belong to THIS task, mirroring how Path A added `"funding"`.)* **(b)** the 5 basis factors appear in `registry.list_names()`; each passes G1 (AST no-future-ops) and G2 (future-bar invariance); `EXPECTED_FACTORS` in `tests/test_factors.py` updated; `feature_version` changes when a basis compute fn changes.
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: (a) Widen the `input_source` contract FIRST (B2 blocking fix — both legs).** In `factors/registry.py`, widen `FactorSpec.input_source`'s `Literal` type AND the `__post_init__` allow-set from `{"ohlcv","funding"}` to `{"ohlcv","funding","basis"}` (mirror Path A's `"funding"` addition). This is a CONTRACT GAP boundary — the widening test (Step 1a) ships in this same task. **(b) Add the `"basis"` build-routing branch** in `factors/build_features.py`: `input_source="basis"` factors must NOT flow through the standard OHLCV `build_features_df` path (no `basis_rel` column there); instead `derive_basis_rel(mark, spot)` (Task B0) onto the 1h grid → compute the basis factors on it → join (native-1h, same grid — NOT `merge_asof`) onto the 1h feature frame; OHLCV factors compute unchanged. **(c) Register** the 5 basis factors in `_bootstrap_core_factors()` (import `factors.basis`), each `null_policy="nan_before_warmup_only"` + declared warmup, tagged `input_source="basis"`. Update `EXPECTED_FACTORS`.
- [ ] **Step 4: Run** the leakage-guard suite + factor suite — `python -m pytest tests/test_leakage_guards.py tests/test_basis_factors.py tests/test_basis_derive.py tests/test_factors.py -q` → all green. Rebuild the feature parquet (full dataset; `feature_version` bump).
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): register basis factors + build integration`.

---

# PHASE C — Hypotheses + verdict harness  *(rest of downstream register B — build)*

> Phase C is mostly **adaptation** of the existing, tested `patha_*` harness to `pathc_*` retargeted at the basis cohort + the LOCKed basis hypotheses. Where a module is a near-verbatim rename, the task says so; the genuinely-new logic (3 basis DSL builders, the **D2 vs-funding** leg) gets full TDD.

### Task C1: H1 basis DSL builder (NO time-stop from the outset)

**Files:** Create `backtest/pathc_eval_gauntlet.py`; Test `tests/test_pathc_gauntlet.py`.

- [ ] **Step 1: Write the failing test** — `build_h1_dsl()` returns a `StrategyDSL` whose entry/exit/sizing match the LOCK: long on the complement of (`basis_pct_rank_2160 >= θ` AND `basis_sign > 0`), **NO `max_hold`** (exit ONLY via the tail-gate — LOCK Note A / Amendment-A1 inheritance), vol-CDF ternary sizing band `[0.3,0.8)→1.0 else 0.5`. Use `θ = 0.90` as the build-time default (the deterministic-rule fallback to 0.85 is resolved on TRAIN at run-time, Task C7/D1 — NOT baked into the builder). Assert it compiles (`compile_dsl_to_strategy(dsl, write_manifest=False)`) and uses only registered factors.

```python
# tests/test_pathc_gauntlet.py
from backtest.pathc_eval_gauntlet import build_h1_dsl, referenced_factors
from strategies.dsl_compiler import compile_dsl_to_strategy

def test_h1_dsl_matches_lock_and_compiles():
    dsl = build_h1_dsl(theta=0.90)
    assert dsl.position_sizing != "full_equity"               # ternary SizingSpec
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)   # REAL compiler API; must not raise
    assert cls is not None
    facs = referenced_factors(dsl)
    assert {"basis_pct_rank_2160", "basis_sign"} <= facs
    assert len(dsl.entry) == 2                                  # the two De Morgan OR-groups
    assert getattr(dsl, "max_hold_bars", None) in (None, 0)     # H1 has NO time-stop
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement `build_h1_dsl(theta=0.90)`** with the REAL DSL API (`SizingSpec` `strategies/dsl.py`; `Condition.value` for factor-vs-scalar; OR-groups = a list of `ConditionGroup`; compile via `compile_dsl_to_strategy(dsl, write_manifest=False)`). **The DSL has NO `NOT` operator**, so H1's "flat when (`basis_pct_rank_2160 ≥ θ` AND `basis_sign > 0`), long otherwise" is **De Morgan**: ENTRY = two OR-groups `[basis_pct_rank_2160 < θ]` OR `[basis_sign <= 0]` (the ~90% long complement; `sign ≤ 0` covers {−1, 0}); EXIT = the single tail-gate group `(basis_pct_rank_2160 ≥ θ AND basis_sign > 0)`. **NO `max_hold`** (LOCK Note A). Ternary `SizingSpec` per LOCK. Also implement `referenced_factors(dsl)` (walks `dsl.entry` / `dsl.exit` / `dsl.position_sizing`).
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): H1 basis DSL builder (no time-stop)`.

### Task C2: H2 basis DSL builder

**Files:** Modify `backtest/pathc_eval_gauntlet.py`; Test `tests/test_pathc_gauntlet.py`.

- [ ] **Step 1: Write the failing test** — `build_h2_dsl()`: long when (regime permissive: `basis_ewm_240_pctrank_2160 < 0.80`) AND (`decay_linear_close_48 > decay_linear_close_168`); flat in de-risk regime; `max_hold_bars=24`; compiles; uses `basis_ewm_240_pctrank_2160` (registered in B4) + the decay-MA cross.
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** `build_h2_dsl()` using `basis_ewm_240_pctrank_2160 < 0.80` as the permissive gate AND the decay-MA cross as the directional confirm (factor-vs-factor), exit on de-risk / trend roll-over / `max_hold_bars=24`.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): H2 basis DSL builder`.

### Task C3: H3 basis DSL builder (strict partition)

**Files:** Modify `backtest/pathc_eval_gauntlet.py`; Test `tests/test_pathc_gauntlet.py`.

- [ ] **Step 1: Write the failing test** — `build_h3_dsl()`: long when `basis_ewm_480 > 0` AND `basis_pct_rank_2160 < θ` (**strict** `<`, B2 Codex 2e) AND `decay_linear_close_48 > decay_linear_close_168`; exits per LOCK incl. `basis_pct_rank_2160 ≥ θ`; `max_hold_bars=48`; compiles. Assert H1/H3 are an **exact partition** on the pct-rank axis: H3 `< θ` vs H1 tail `≥ θ` (boundary bar `= θ` belongs to H1 only — no overlap).

```python
def test_h3_strict_partition_vs_h1():
    from backtest.pathc_eval_gauntlet import build_h3_dsl, referenced_factors
    dsl = build_h3_dsl(theta=0.90)
    facs = referenced_factors(dsl)
    assert {"basis_ewm_480", "basis_pct_rank_2160", "decay_linear_close_48", "decay_linear_close_168"} <= facs
    # H3 entry uses STRICT '<' on basis_pct_rank_2160 (partition with H1's '>=')
    assert any(c.op == "<" and c.factor == "basis_pct_rank_2160" for g in dsl.entry for c in g.conditions)
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** `build_h3_dsl(theta=0.90)` (entry: `basis_ewm_480 > 0` AND `basis_pct_rank_2160 < θ` AND trend; OR-group exits: `basis_ewm_480 <= 0` OR trend roll-over OR `basis_pct_rank_2160 >= θ` OR `max_hold_bars=48`).
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): H3 basis DSL builder (strict partition)`.

### Task C4: Adapt the verdict harness modules (`patha_* → pathc_*`)

**Files:** Create `backtest/pathc_holdout_producer.py`, `pathc_moments.py`, `pathc_dsr_fwer.py`, `pathc_earned_negative.py`, `pathc_escalation.py`, `pathc_train_sanity.py`, `pathc_orchestrator.py`; Tests `tests/test_pathc_*.py`.

- [ ] **Step 1:** For each, copy the corresponding `patha_*` module, retarget the cohort to the 3 basis hypotheses + the basis feature columns, keep `PATHC_N_STAR = 3` (= `PATHA_N_STAR`), reuse `tier6_dsr.evaluate_candidate` + Form B + frozen `Z_PASS` unchanged. **Sealed `tier6_dsr_v1` is byte-untouched** (assert sha256 in the test). The §37.1 gate (`PHASE_D_AUTHORIZED` + injected `_run_backtest`) is preserved in `scripts/pathc_run_verdict.py` (Task D-gate) — re-verify it raises while unauthorized.
- [ ] **Step 1b (escalation prong):** `backtest/pathc_escalation.py` adapts `patha_escalation.py` verbatim: prong-(ii) keys on **`n_dsr_pass == 0`** (no basis variant lifted above `pass_B` → next-axis escalation warranted). Signature `c_escalation_advisory(taxonomy, n_dsr_pass)`. Test `n_dsr_pass=0` (warranted) vs `>0` (not).
- [ ] **Step 1c (F3 under-determined carve-out, advisor F3):** Extend `pathc_earned_negative.assemble_evidence(...)`: a leg that is floor-INDETERMINATE on `zero_fraction` AND returns a **thin-sample non-negative** forward Sharpe (trade count below a pre-registered substantive-read threshold AND `holdout_sharpe >= 0`) is tagged `under_determined=True` and is **NOT** folded into the earned-negative (neither substantive-negative nor Tier-5-eligible) — surfaced in the advisory bundle as a power gap. Test: (a) under-floor + measured loss → substantive negative; (b) under-floor + thin-sample non-negative → `under_determined`.
- [ ] **Step 1d (tier threading):** thread the per-leg strong/weak-sane tier (Task C5) into `assemble_evidence` → `verdict_rests_on_weak_sane_only=True` when `any_mechanism_sane` rests solely on weak-sane legs. Test both cases.
- [ ] **Step 2:** Port each `patha_*` test to `pathc_*` (mechanism IDs H1/H2/H3 basis names; same structural assertions).
- [ ] **Step 3:** Run `python -m pytest tests/test_pathc_*.py -q` → green; assert sealed `tier6_dsr_v1` sha256 4/4 unchanged.
- [ ] **Step 4: Commit** (await authorization) — `feat(pathc): adapt verdict harness patha->pathc`.

### Task C5: Tiered 24h+72h mechanism-sanity (`pathc_perleg_mechanism.py`)

**Files:** Create `backtest/pathc_perleg_mechanism.py`; Test `tests/test_pathc_perleg.py`.

- [ ] **Step 1: Write the failing test** — for each leg, the train-only conditional-return sign is computed at **both** 24-bar and 72-bar horizons; both-sign → `strong_sane`; exactly-one → `weak_sane`; neither → `refuted`; per-leg record carries both horizon signs + the tier. H1 sane-sign NEGATIVE (reversal); H2 = permissive-mean > de-risk-mean AND permissive-mean > 0; H3 sane-sign POSITIVE.

```python
# tests/test_pathc_perleg.py
from backtest.pathc_perleg_mechanism import classify_leg
def test_strong_vs_weak_sane():
    assert classify_leg(mean_24h=+0.01, mean_72h=+0.02, sane_sign="+")["tier"] == "strong_sane"
    assert classify_leg(mean_24h=+0.01, mean_72h=-0.02, sane_sign="+")["tier"] == "weak_sane"
    assert classify_leg(mean_24h=-0.01, mean_72h=-0.02, sane_sign="+")["tier"] == "refuted"
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** `classify_leg` + the per-leg driver (adapt `patha_perleg_mechanism.py` verbatim — horizon-agnostic; only the cohort wiring changes).
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): tiered 24h+72h mechanism sanity`.

### Task C6: Dual-orthogonalization diagnostic (D1 vs-momentum + **D2 vs-funding**)

**Files:** Create `backtest/pathc_marginal_diagnostic.py`; Test `tests/test_pathc_marginal.py`.

> D1 is Path A's `funding_marginal` pattern (renamed basis_marginal). **D2 is NET-NEW**: compares the basis-gated strategy to the *funding-gated* Path A strategy on identical bars, to measure whether higher-frequency basis adds over the 8h funding it is derived from (the §1 redundancy test). Both legs are fenced (`promotion_affecting=False, in_n_star=False`). The conjunction inference rule + the D2-disagree branch live here.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathc_marginal.py
import numpy as np
from backtest.pathc_marginal_diagnostic import basis_marginal_d1, basis_marginal_d2, redundancy_read

def test_d1_is_fenced_diagnostic():
    gated    = np.array([1.0, 1.01, 1.00, 1.02])
    baseline = np.array([1.0, 1.02, 1.03, 1.05])
    out = basis_marginal_d1("H2", gated_equity=gated, baseline_equity=baseline)
    assert out["d1_marginal_sharpe"] < 0
    assert out["promotion_affecting"] is False and out["in_n_star"] is False

def test_d2_and_redundancy_conjunction():
    basis_eq   = np.array([1.0, 1.01, 1.005, 1.02])
    funding_eq = np.array([1.0, 1.01, 1.006, 1.02])   # ~equal to basis -> agree
    d2 = basis_marginal_d2("H2", basis_gated_equity=basis_eq, funding_gated_equity=funding_eq)
    assert d2["promotion_affecting"] is False and d2["in_n_star"] is False
    # redundancy confirmed ONLY by conjunction (agree AND non-inert D1)
    assert redundancy_read(d2_agrees=True,  d1_noninert=True)  == "redundancy_confirmed"
    assert redundancy_read(d2_agrees=True,  d1_noninert=False) == "vacuous"           # jointly-inert
    assert redundancy_read(d2_agrees=False, d1_noninert=True)  == "basis_adds_signal" # D2-disagree branch
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement.** `basis_marginal_d1(hyp_id, gated_equity, baseline_equity)` = Sharpe delta vs the no-basis baseline (H2/H3: the price-trend strategy WITHOUT the basis gate; H1: always-long), fenced. `basis_marginal_d2(hyp_id, basis_gated_equity, funding_gated_equity)` = Sharpe delta vs the Path A funding-gated strategy on identical bars (reuse the on-`main` `backtest/patha_eval_gauntlet` funding builders + `data/raw/btcusdt_funding_8h.parquet`), fenced. `redundancy_read(d2_agrees, d1_noninert)`: `"redundancy_confirmed"` iff `d2_agrees AND d1_noninert`; `"vacuous"` iff `d2_agrees AND NOT d1_noninert`; `"basis_adds_signal"` iff `NOT d2_agrees AND d1_noninert` (the D2-disagree branch — surfaced, NOT auto-promoted). Both records assert never feed N\* or promotion.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): dual-orthogonalization D1/D2 diagnostic`.

### Task C7: Hypothesis-class floors (deterministic θ + frozen-θ floor)

**Files:** Modify `backtest/pathc_orchestrator.py`; Test `tests/test_pathc_floors.py`.

- [ ] **Step 1: Write the failing test** — H1 eligibility keys on the **count of defensive flat-exit episodes** (long→flat transitions driven by the basis tail-gate) ≥ 200 on train; the **deterministic θ rule** is applied first (`θ:=0.90; if H1 episodes at 0.90 < 200 → θ:=0.85`), and the H1 floor is then judged at the **frozen θ** (recounted at 0.85 if the fallback fired — LOCK Finding 6); H2/H3 on `zero_fraction < 0.50` AND ≥ 200 trades on train, **and H2 additionally requires de-risk-cell occupancy ≥ 10% of evaluated train bars** (LOCK Pre-reg 3 / H2 row — keeps the conditional-separation kill powered; B2 advisor Finding 2); floors on the TRAIN window only; under-floor → `INDETERMINATE`.

```python
# tests/test_pathc_floors.py
from backtest.pathc_orchestrator import resolve_theta, h1_floor_eligible, h2_derisk_occupancy_eligible
def test_deterministic_theta_and_frozen_floor():
    # 150 episodes at 0.90 -> fallback to 0.85; floor re-judged at 0.85
    assert resolve_theta(episodes_at_090=150) == 0.85
    assert resolve_theta(episodes_at_090=250) == 0.90
    # eligibility judged at the FROZEN theta (recount at 0.85)
    assert h1_floor_eligible(episodes_at_frozen_theta=210) is True
    assert h1_floor_eligible(episodes_at_frozen_theta=180) is False   # INDETERMINATE

def test_h2_derisk_occupancy_floor():
    # the ~0.80 de-risk band gives ~0.20 occupancy by construction (comfortably above)
    assert h2_derisk_occupancy_eligible(occupancy=0.20) is True
    assert h2_derisk_occupancy_eligible(occupancy=0.08) is False   # <10% -> kill under-powered, INDETERMINATE
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** `resolve_theta(episodes_at_090)` and `h1_floor_eligible(episodes_at_frozen_theta)` (**net-new** — Path A used a fixed θ=0.90 with no fallback), `h2_derisk_occupancy_eligible(occupancy)` (≥ 0.10, LOCK H2 row — **net-new**), and the H2/H3 `zero_fraction`+trade-count floor (reuse Path A). The orchestrator resolves θ once on train, freezes it for H1+H3 jointly, then judges all floors at the frozen θ.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(pathc): hypothesis-class floors + deterministic theta`.

> **STOP — Phase B/C register boundary.** Full suite green + sealed sha256 4/4 unchanged + 2-leg B2 on the build. Await Phase D register.

---

# PHASE D — Run (forward_2026 verdict)  *(downstream register C — verdict run)*

> Phase D produces the actual verdict — a separate Charlie register, gated by `scripts/pathc_run_verdict.py`'s `PHASE_D_AUTHORIZED` flag + injected `_run_backtest` (the §37.1 function-boundary gate; the flag stays `False` in the repo). Re-verify sealed `tier6_dsr_v1` sha256 BEFORE and AFTER.

### Task D1: Train-only mechanism-sanity table + θ resolution

- [ ] **Step 1:** Resolve θ on train (Task C7 deterministic rule) and freeze it for H1+H3.
- [ ] **Step 2:** Run `pathc_perleg_mechanism` on the train window (2020-21+2023) → per-leg conditional-return signs at 24h+72h + strong/weak/refuted tiers. Assert each leg's eligibility floor at the frozen θ. **No validation/test/forward touch.**
- [ ] **Step 3: Commit** the train-sanity artifact (await authorization).

### Task D2: Walk-forward train + forward_2026 Tier-5 holdout + dual diagnostic

- [ ] **Step 1:** Walk-forward on train (`check_wf_semantics_or_raise`, `corrected_test_boundary_v1`).
- [ ] **Step 2:** Produce the **forward_2026** single-run holdout (`pathc_holdout_producer`, `check_evaluation_semantics_or_raise`, `single_run_holdout_v1`) → `holdout_sharpe` per hypothesis at 15 bps.
- [ ] **Step 3:** Run the dual-orthogonalization diagnostic (Task C6): D1 (vs no-basis baseline) + D2 (vs the funding-gated Path A strategy) on forward_2026; record `redundancy_read` per hypothesis.
- [ ] **Step 4: Commit** the holdout + dual-diagnostic artifacts (await authorization).

### Task D3: DSR-FWER N\*=3 + taxonomy + advisory

- [ ] **Step 1:** Build `pathc_moments` (CandidateMoments + integrity gate) from the forward holdout per-bar returns.
- [ ] **Step 2:** `pathc_dsr_fwer` at N\*=3 → `pass_B` survivors.
- [ ] **Step 3:** `pathc_earned_negative.assemble_evidence(...)` → taxonomy verdict (mechanism / process-refuted / c-positive), with the per-leg strong/weak-sane tiers threaded (`verdict_rests_on_weak_sane_only`), the **F3 under-determined carve-out** for any thin-sample non-negative INDETERMINATE leg, the dual D1/D2 diagnostic + `redundancy_read`, and the post-ETF basis-compression temper in the advisory bundle; escalation via `pathc_escalation.c_escalation_advisory(taxonomy, n_dsr_pass)` keyed on `n_dsr_pass == 0`.
- [ ] **Step 4:** Write `data/phase2c_evaluation_gate/pathc_verdict_v1/pathc_verdict_advisory.json`.
- [ ] **Step 5:** Re-verify sealed `tier6_dsr_v1` sha256 4/4 unchanged.
- [ ] **Step 6: Commit** the verdict artifact (await authorization).

### Task D4: Verdict read + cycle SEAL

- [ ] **Step 1:** 2-leg B2 on the verdict result (Codex + advisor).
- [ ] **Step 2:** Present the advisory verdict to Charlie for the **binding earned-negative-or-positive read** (Charlie register; never auto-fire). If `c_positive`: 2025 OOS confirmation required AND must survive the §9 Finding D dual-orthogonalization before any promotion. If earned-negative: the cross-frequency localization (NOT family-level — OI still required) is recorded; the next axis (OI = the noted successor) is a *separate* future register (anti-pre-emption).
- [ ] **Step 3:** On Charlie's read: Phase Marker advance (CLAUDE.md + `docs/phase_marker_history.md`, atomic) + METHODOLOGY_NOTES lessons + `superpowers:finishing-a-development-branch`.

---

## Self-review (against the LOCK + spec)

- **Spec/LOCK coverage:** Pre-reg 1 (3 hypotheses, exact params, exact partition, deterministic θ) → Tasks C1/C2/C3 + the basis factors B1–B4 + the deterministic-θ floor C7. Pre-reg 2 (15bps, forward_2026 Tier-5, DSR-FWER N\*=3) → D2/D3 + C4. Pre-reg 3 (cost-aware, floors incl. the H2 de-risk-cell **≥10% occupancy floor** → C7, single-factor sizing, native-1h causal derivation, dual-orthogonalization fenced) → B0/C6/C7 + sizing in C1; the `input_source="basis"` registry contract-widen → B5 Step 3a. Pre-reg 4 (taxonomy incl. F3 under-determined, tiered sanity, escalation, localization) → C4/C5/D3. Ingestion design (spec §5) → Phase A. Harness reuse (spec §4) → C4. Basis≈funding reframe / D2 (spec §1, §9 Finding D) → C6. **No gap found** (B2-confirmed: every Pre-reg 1–4 maps to a task; no LOCKed value altered).
- **Placeholder scan:** ingestion download wrapper (A2) + reconcile (A4) + incremental (A5) reference the existing OHLCV modules as the pattern rather than re-printing them in full — acceptable (near-verbatim mirrors of tested code); the genuinely-new logic (kline parse, validators+cross-check, basis_rel derivation, factors, DSL builders, dual diagnostic, deterministic-θ floor) has full code/tests. No "TBD"/"handle edge cases" placeholders.
- **Type/name consistency:** factor names (`basis_sign`, `basis_ewm_240`, `basis_ewm_480`, `basis_pct_rank_2160`, `basis_ewm_240_pctrank_2160`), `derive_basis_rel(mark, spot)`, `classify_leg(mean_24h, mean_72h, sane_sign)`, `basis_marginal_d1(hyp_id, gated_equity, baseline_equity)`, `basis_marginal_d2(hyp_id, basis_gated_equity, funding_gated_equity)`, `redundancy_read(d2_agrees, d1_noninert)`, `referenced_factors(dsl)`, `c_escalation_advisory(taxonomy, n_dsr_pass)`, `resolve_theta(episodes_at_090)`, `h1_floor_eligible(episodes_at_frozen_theta)`, `h2_derisk_occupancy_eligible(occupancy)`, `compile_dsl_to_strategy(dsl, write_manifest=False)`, `PATHC_N_STAR=3`, `build_h1/h2/h3_dsl(theta=0.90)` — used consistently across tasks. H1 has NO `max_hold` everywhere; H3 uses strict `<` everywhere.
- **Register boundaries:** Phase A / B+C / D STOP markers present; per-task commits gated on Charlie authorization; the §37.1 `PHASE_D_AUTHORIZED` gate guards the real run.

---

## Execution handoff

This plan is the scoping cycle's final deliverable. Per the register discipline, **execution does not begin until Charlie registers Phase A**. When execution is authorized, the recommended approach is **subagent-driven-development** (fresh subagent per task + two-stage review), with a 2-leg B2 at each phase boundary (Charlie-instructed). Ingestion (Phase A), build (Phase B/C), and run (Phase D) are each their own Charlie register-event.
