# Path A — Funding-Rate Axis Mechanism-First Mine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build + run the bounded, pre-registered one-cycle falsification test of the funding-rate information axis: ingest Binance funding, derive 3 causal funding factors carried onto 1h bars, express the 3 LOCKed funding hypotheses (H1/H2/H3) in the DSL, reuse the Path B verdict harness retargeted to funding, and produce the forward_2026 earned-negative-or-positive verdict.

**Architecture:** Mirror Path B's pipeline exactly, swapping the *data axis* (OHLCV → OHLCV + funding) while holding the *process* fixed. Funding is ingested as a separate 8h-settlement parquet, three causal funding factors are computed on the settlement series and carried onto the 1h bar grid by a backward as-of join (discrete-settlement carry, never interpolation), the 3 hypotheses compile through the existing DSL (no new schema), and the `pathb_*` verdict harness is adapted to `patha_*` for a new funding cohort. Sealed `tier6_dsr_v1` artifacts stay byte-identical throughout.

**Tech Stack:** Python 3.11, pandas/pyarrow (parquet), CCXT (incremental funding), Backtrader (engine), scipy (DSR), pytest (TDD). All UTC.

**Governing LOCK:** [`../specs/2026-05-31-patha-step-minus-1-preregistration-lock.md`](../specs/2026-05-31-patha-step-minus-1-preregistration-lock.md) — **frozen; no task may alter a LOCKed value.** Design spec: [`../specs/2026-05-31-path-a-funding-scoping-design.md`](../specs/2026-05-31-path-a-funding-scoping-design.md).

**Register discipline (CRITICAL):** This plan spans **three separate downstream Charlie register-events** — Phase A (ingestion = first data touch), Phase B+C (build), Phase D (run). **Each phase boundary requires an explicit Charlie register before proceeding.** Per-task commits await Charlie authorization. The plan is the scoping deliverable; authoring it authorizes no execution.

**Baseline:** full suite 2718 passed / 8 skipped / 2 xfailed; pc9 = 2602. Sealed `tier6_dsr_v1/` sha256: `0a7d98…` / `8eecc6…` / `49646c…` / `1803eb…` (re-verify before AND after any Phase D task).

---

## File structure

| File | Responsibility | New/Modify |
|---|---|---|
| `config/schemas.yaml` | add `funding` schema block (8h settlement parquet columns + validation) | Modify |
| `ingestion/funding_bulk_download.py` | Binance Vision bulk `monthly/fundingRate/BTCUSDT/` → parquet (mirrors `bulk_download.py`) | Create |
| `ingestion/funding_incremental_update.py` | CCXT `fetchFundingRateHistory` incremental/forward update | Create |
| `ingestion/funding_reconcile.py` | merge + archive-before-overwrite + source-priority dedup for funding | Create |
| `ingestion/validators.py` | extend to validate the `funding` schema (UTC PK, sorted, per-row interval) | Modify |
| `data/raw/btcusdt_funding_8h.parquet` | canonical funding settlement series (output) | Create (Phase A run) |
| `factors/funding.py` | `funding_sign`, `funding_ewm_30`, `funding_ewm_60`, `funding_pct_rank_270` (causal, on 8h series) | Create |
| `factors/funding_align.py` | backward as-of join: carry 8h funding features onto 1h bar grid (causal) | Create |
| `factors/registry.py` | register the 4 funding factors; `feature_version` bump | Modify |
| `factors/build_features.py` | integrate the funding-feature join into the full-dataset build | Modify |
| `backtest/patha_eval_gauntlet.py` | H1/H2/H3 funding DSL builders + EVAL gauntlet (adapt `pathb_eval_gauntlet.py`) | Create |
| `backtest/patha_holdout_producer.py` | forward_2026 single-run holdout producer (adapt `pathb_holdout_producer.py`) | Create |
| `backtest/patha_moments.py` | CandidateMoments constructor + integrity gate (adapt `pathb_moments.py`) | Create |
| `backtest/patha_dsr_fwer.py` | DSR-FWER N\*=3 over the funding cohort (adapt `pathb_dsr_fwer.py`) | Create |
| `backtest/patha_perleg_mechanism.py` | tiered 24h+72h strong/weak-sane mechanism-sanity (adapt `pathb_perleg_mechanism.py`) | Create |
| `backtest/patha_marginal_diagnostic.py` | fenced funding-marginal-contribution comparison (NEW) | Create |
| `backtest/patha_earned_negative.py` | taxonomy + advisory assembly (adapt `pathb_earned_negative.py`) | Create |
| `backtest/patha_orchestrator.py` | end-to-end run_patha_verdict (adapt `pathb_orchestrator.py`) | Create |
| `scripts/patha_run_verdict.py` | gated forward_2026 verdict run entrypoint (adapt `scripts/pathb_run_verdict.py`) | Create |

Tests live beside the suite: `tests/test_funding_ingestion.py`, `tests/test_funding_factors.py`, `tests/test_funding_align.py`, `tests/test_patha_*.py`.

---

# PHASE A — Funding ingestion  *(downstream Charlie register A — first data touch)*

> Phase A is the first data touch. Do NOT begin until Charlie registers Phase A. The LOCK is already committed (anti-hindsight), so ingesting funding now cannot reverse-fit the hypotheses.

### Task A1: Funding schema block

**Files:**
- Modify: `config/schemas.yaml` (add top-level `funding` block, mirroring the `ohlcv` block structure)
- Test: `tests/test_funding_ingestion.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_funding_ingestion.py
import yaml
from pathlib import Path

def test_funding_schema_block_exists():
    schemas = yaml.safe_load(Path("config/schemas.yaml").read_text())
    f = schemas["funding"]
    assert f["primary_key"] == "open_time_utc"
    cols = set(f["columns"].keys())   # columns is a name-keyed MAPPING (mirror the ohlcv block)
    assert {"open_time_utc", "funding_rate", "funding_interval_hours",
            "source", "ingested_at_utc"} <= cols
    # allowed sources live under the `source` column's allowed_values (mirror ohlcv)
    assert set(f["columns"]["source"]["allowed_values"]) >= {"binance_vision", "ccxt_binance"}
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_funding_ingestion.py::test_funding_schema_block_exists -v`
Expected: FAIL (KeyError 'funding').

- [ ] **Step 3: Add the `funding` block to `config/schemas.yaml`**

```yaml
# Mirrors the existing `ohlcv` block structure exactly: columns is a NAME-KEYED
# MAPPING (not a list), source allowed values live under the source column's
# allowed_values, validation_rules is a list of {name, check, severity?}.
funding:
  description: "Binance USDT-M perpetual funding rate, 8h settlement series for BTCUSDT"
  primary_key: "open_time_utc"
  sort_order: "open_time_utc ASC"
  file_pattern: "data/raw/btcusdt_funding_8h.parquet"
  columns:
    open_time_utc:
      dtype: "datetime64[ms, UTC]"
      nullable: false
      description: "Settlement time (calc_time), UTC tz-aware, unique, sorted ascending"
    funding_rate:
      dtype: "float64"
      nullable: false
      description: "last_funding_rate (settled realized rate) for the interval ending at open_time_utc"
    funding_interval_hours:
      dtype: "int64"
      nullable: false
      constraints: "> 0"
      description: "Funding interval hours, read per-row (8 for BTCUSDT over the window; never hardcoded)"
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
    - name: "positive_interval"
      check: "funding_interval_hours > 0"
    - name: "no_forward_fill"
      check: "missing settlements flagged in the quality report, never interpolated"
      severity: "warning"
```

- [ ] **Step 4: Run to verify it passes**

Run: `python -m pytest tests/test_funding_ingestion.py::test_funding_schema_block_exists -v`
Expected: PASS.

- [ ] **Step 5: Commit** (await Charlie authorization)

```bash
git add config/schemas.yaml tests/test_funding_ingestion.py
git commit -F /tmp/msg.txt   # "feat(patha): funding schema block"
```

### Task A2: Funding bulk download (Binance Vision)

**Files:**
- Create: `ingestion/funding_bulk_download.py`
- Test: `tests/test_funding_ingestion.py`

- [ ] **Step 1: Write the failing test** (parse a fixture CSV in the real Binance Vision funding format)

```python
# tests/test_funding_ingestion.py  (append)
import pandas as pd
from ingestion.funding_bulk_download import parse_funding_csv

def test_parse_funding_csv_real_format(tmp_path):
    # Real Binance Vision fundingRate columns: calc_time(ms), funding_interval_hours, last_funding_rate
    csv = tmp_path / "BTCUSDT-fundingRate-2020-01.csv"
    csv.write_text(
        "calc_time,funding_interval_hours,last_funding_rate\n"
        "1577836800000,8,0.0001\n"
        "1577865600000,8,-0.00005\n"
    )
    df = parse_funding_csv(csv)
    assert list(df["open_time_utc"]) == [
        pd.Timestamp("2020-01-01 00:00:00", tz="UTC"),
        pd.Timestamp("2020-01-01 08:00:00", tz="UTC"),
    ]
    assert df["funding_rate"].tolist() == [0.0001, -0.00005]
    assert df["funding_interval_hours"].tolist() == [8, 8]
    assert str(df["open_time_utc"].dtype) == "datetime64[ms, UTC]"
    assert (df["source"] == "binance_vision").all()
```

- [ ] **Step 2: Run to verify it fails** — `ModuleNotFoundError`.

- [ ] **Step 3: Implement `parse_funding_csv` + the bulk downloader**

```python
# ingestion/funding_bulk_download.py
"""Bulk download Binance Vision USDT-M funding rate history for BTCUSDT.

Mirrors ingestion/bulk_download.py: download monthly ZIPs from
data.binance.vision, parse to parquet. (NOTE: bulk_download.py does NOT verify
checksums — there is no .CHECKSUM step to mirror.) Funding is an 8h settlement
series; calc_time is the settlement timestamp (UTC ms epoch).
Source: data/futures/um/monthly/fundingRate/BTCUSDT/ (history from 2020-01).
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import logging
import pandas as pd

VISION_PREFIX = "data/futures/um/monthly/fundingRate/BTCUSDT/"
OUTPUT_PATH = Path("data/raw/btcusdt_funding_8h.parquet")

def parse_funding_csv(path: Path) -> pd.DataFrame:
    """Parse one Binance Vision fundingRate CSV into the canonical funding schema.

    Inputs: a CSV with header calc_time,funding_interval_hours,last_funding_rate.
    Output schema: open_time_utc(datetime64[ms,UTC] PK), funding_rate(float64),
      funding_interval_hours(int64), source(string), ingested_at_utc(datetime64[ms,UTC]).
    Null policy: rows with NaN calc_time/last_funding_rate are dropped + counted (logged).
    """
    raw = pd.read_csv(path)
    n_in = len(raw)
    raw = raw.dropna(subset=["calc_time", "last_funding_rate"])     # drop + count NaN rows
    n_dropped = n_in - len(raw)
    if n_dropped:
        logging.info("parse_funding_csv: dropped %d NaN row(s) from %s", n_dropped, path.name)
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(raw["calc_time"], unit="ms", utc=True).astype("datetime64[ms, UTC]"),
        "funding_rate": raw["last_funding_rate"].astype("float64"),
        "funding_interval_hours": raw["funding_interval_hours"].astype("int64"),
    })
    df["source"] = pd.array(["binance_vision"] * len(df), dtype="string")   # schema 'string', not object
    df["ingested_at_utc"] = pd.Timestamp(datetime.now(timezone.utc)).as_unit("ms")
    return df.sort_values("open_time_utc").reset_index(drop=True)
```
(The download/unzip wrapper mirrors `bulk_download.py`'s `main()` with the `VISION_PREFIX` above and `--start 2020-01`; argparse + `--dry-run`; logs rows-before/after. **No checksum step** — `bulk_download.py` does not verify checksums.)

- [ ] **Step 4: Run to verify it passes** — PASS.

- [ ] **Step 5: Commit** (await authorization) — `feat(patha): funding bulk download + CSV parse`.

### Task A3: Funding validators

**Files:**
- Modify: `ingestion/validators.py` (add `validate_funding(df)`)
- Test: `tests/test_funding_ingestion.py`

- [ ] **Step 1: Write the failing test**

```python
from ingestion.validators import validate_funding
import pandas as pd, pytest

def _good():
    return pd.DataFrame({
        "open_time_utc": pd.to_datetime([1577836800000, 1577865600000], unit="ms", utc=True).as_unit("ms"),
        "funding_rate": [0.0001, -0.00005], "funding_interval_hours": [8, 8],
        "source": ["binance_vision"]*2, "ingested_at_utc": pd.to_datetime([0,0], unit="ms", utc=True).as_unit("ms"),
    })

def test_validate_funding_accepts_good():
    report = validate_funding(_good())
    assert report["ok"] is True

def test_validate_funding_rejects_duplicate_pk():
    df = _good(); df.loc[1, "open_time_utc"] = df.loc[0, "open_time_utc"]
    report = validate_funding(df)
    assert report["ok"] is False and "duplicate" in report["errors"][0].lower()

def test_validate_funding_rejects_unsorted():
    df = _good().iloc[::-1].reset_index(drop=True)
    report = validate_funding(df)
    assert report["ok"] is False
```

- [ ] **Step 2: Run to verify it fails** — ImportError.

- [ ] **Step 3: Implement `validate_funding`** (UTC tz-aware, unique+sorted PK, `funding_interval_hours > 0` per row, allowed source; gaps flagged not removed; returns `{"ok": bool, "errors": [...], "warnings": [...], "rows": n}`). Mirror the structure of the existing OHLCV validator; non-zero exit on failure in the CLI path.

- [ ] **Step 4: Run to verify it passes** — PASS.

- [ ] **Step 5: Commit** (await authorization) — `feat(patha): funding validators`.

### Task A4: Funding reconcile + archive

**Files:**
- Create: `ingestion/funding_reconcile.py`
- Test: `tests/test_funding_ingestion.py`

- [ ] **Step 1: Write the failing test** — archive-before-overwrite writes a snapshot to `data/raw/archive/btcusdt_funding_8h_<ts>.parquet`; dedup on `open_time_utc` preferring `binance_vision` over `ccxt_binance`; output is unique+sorted.
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** mirroring `ingestion/reconcile.py` (`archive_file`, `SOURCE_PRIORITY = {"binance_vision": 0, "ccxt_binance": 1}`, merge+dedup+sort). Funding is a distinct file, so no cross-venue OHLCV interaction.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): funding reconcile + archive`.

### Task A5: CCXT incremental funding update

**Files:**
- Create: `ingestion/funding_incremental_update.py`
- Test: `tests/test_funding_ingestion.py` (mock the CCXT client)

- [ ] **Step 1: Write the failing test** — a mocked exchange whose `fetch_funding_rate_history` (CCXT Python snake_case — the SAME name the implementation calls) returns rows normalized to the funding schema (UTC PK, source `ccxt_binance`).
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** mirroring `ingestion/incremental_update.py` (`create_exchange`, paginated `fetch_funding_rate_history(symbol="BTC/USDT:USDT", since=...)`, retry logic, normalize to schema).
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): funding incremental update (CCXT)`.

### Task A6: Phase A integration run (ACTUAL data touch — Charlie-gated)

- [ ] **Step 1:** `python -m ingestion.funding_bulk_download --pair BTCUSDT --start 2020-01` → `data/raw/btcusdt_funding_8h.parquet`.
- [ ] **Step 2:** `python -m ingestion.validators --funding data/raw/btcusdt_funding_8h.parquet --report data/quality/` → assert `ok: True`; document the FTX-Nov-2022 + post-ETF-Jan-2024 characteristics in the report (flagged, not cleaned).
- [ ] **Step 3:** sanity: row count ≈ 3/day × ~6.3y ≈ ~6900 rows; first `open_time_utc` == 2020-01-01T00:00:00Z; all `funding_interval_hours == 8` over the window (assert per-row, log any exception).
- [ ] **Step 4: Commit** the data-availability report (NOT the raw parquet if policy excludes large binaries; follow the OHLCV convention) — await authorization.

> **STOP — Phase A register boundary.** Report ingestion results to Charlie; await Phase B register.

---

# PHASE B — Funding-feature pipeline  *(part of downstream register B — build)*

### Task B1: `funding_sign` factor

**Files:**
- Create: `factors/funding.py`
- Test: `tests/test_funding_factors.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_funding_factors.py
import pandas as pd
from factors.funding import funding_sign

def test_funding_sign():
    s = pd.Series([0.0002, -0.0001, 0.0, 0.00005])
    out = funding_sign(pd.DataFrame({"funding_rate": s}))
    assert out.tolist() == [1.0, -1.0, 0.0, 1.0]
```

- [ ] **Step 2: Run to verify it fails** — ImportError.

- [ ] **Step 3: Implement** (top-level named, causal, no future ops)

```python
# factors/funding.py
"""Funding-rate factors computed on the 8h settlement series (causal, rolling
over settlement units). Carried onto 1h bars downstream by factors.funding_align.
All factors are top-level named callables, rolling/causal only (pass G1-G4).
Input: a DataFrame with a 'funding_rate' column indexed by settlement.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

def funding_sign(df: pd.DataFrame) -> pd.Series:
    """Sign of the settled funding rate. Inputs: funding_rate. Warmup: 0.
    Output: {-1.0, 0.0, 1.0}. Null policy: NaN funding_rate -> NaN."""
    return np.sign(df["funding_rate"]).astype("float64")
```

- [ ] **Step 4: Run to verify it passes** — PASS.
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): funding_sign factor`.

### Task B2: `funding_ewm_30` and `funding_ewm_60`

**Files:** Modify `factors/funding.py`; Test `tests/test_funding_factors.py`.

- [ ] **Step 1: Write the failing test** — `funding_ewm_30(df)` equals `df["funding_rate"].ewm(span=30, adjust=False).mean()`; assert `adjust=False`; assert causality (value at row N independent of rows > N — delete-future invariance).
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement**

```python
def funding_ewm_30(df: pd.DataFrame) -> pd.Series:
    """Causal EWM of settled funding, span=30 settlements (~10 days), adjust=False.
    Inputs: funding_rate. Warmup: ~30 settlements. Null policy: NaN before first obs."""
    return df["funding_rate"].ewm(span=30, adjust=False).mean()

def funding_ewm_60(df: pd.DataFrame) -> pd.Series:
    """Causal EWM of settled funding, span=60 settlements (~20 days), adjust=False."""
    return df["funding_rate"].ewm(span=60, adjust=False).mean()
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): funding_ewm_30/60`.

### Task B3: `funding_pct_rank_270`

**Files:** Modify `factors/funding.py`; Test `tests/test_funding_factors.py`.

- [ ] **Step 1: Write the failing test** — rolling causal percentile rank of the current funding within the trailing 270-settlement window; value in `[0, 1]`; at row N uses only `[N-269, N]`; delete-future invariance; min-periods warmup yields NaN before the window fills.

```python
from factors.funding import funding_pct_rank_270
def test_funding_pct_rank_causal_and_bounded():
    import numpy as np, pandas as pd
    s = pd.Series(np.r_[np.zeros(299), [5.0]])   # 300 rows; last value is the max of its window
    out = funding_pct_rank_270(pd.DataFrame({"funding_rate": s}))
    assert out.iloc[-1] == 1.0
    assert out.iloc[:269].isna().all()           # warmup: indices 0..268 NaN (min_periods=270)
    assert not np.isnan(out.iloc[269])           # first valid value at index 269
    # causality: truncating future rows leaves earlier values unchanged
    trunc = funding_pct_rank_270(pd.DataFrame({"funding_rate": s.iloc[:280]}))
    assert trunc.iloc[270] == out.iloc[270]
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** (rolling window, causal percentile = fraction of window ≤ current value)

```python
def funding_pct_rank_270(df: pd.DataFrame) -> pd.Series:
    """Causal rolling percentile rank of the settled funding rate over the trailing
    270 settlements (~90 days). At settlement N: fraction of [N-269, N] with value
    <= value[N]. Inputs: funding_rate. Warmup: 270 settlements (NaN before).
    Output: [0.0, 1.0]. No future ops (rolling, right-closed). NOTE: uses an explicit
    count loop, NOT `.mean()`, so the G1 AST scanner (which bans bare
    .mean()/.std()/.sum() on a window) does not reject it."""
    def _rank(window: np.ndarray) -> float:
        last = window[-1]
        count = sum(1 for v in window if v <= last)
        return count / len(window)
    return df["funding_rate"].rolling(window=270, min_periods=270).apply(_rank, raw=True)
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): funding_pct_rank_270`.

### Task B4: 8h→1h causal carry-forward (`factors/funding_align.py`)

**Files:** Create `factors/funding_align.py`; Test `tests/test_funding_align.py`.

- [ ] **Step 1: Write the failing test** — given an 8h funding-feature frame and a 1h bar grid, each 1h bar at close `c` receives the most recent settlement with `calc_time ≤ c`; bars before the first settlement are NaN; **causality**: deleting/reversing/shuffling settlements after a bar leaves that bar's carried value bit-identical.

```python
# tests/test_funding_align.py
import pandas as pd
from factors.funding_align import carry_funding_to_bars

def test_carry_is_backward_asof_and_causal():
    feat = pd.DataFrame({
        "open_time_utc": pd.to_datetime(["2020-01-01 00:00","2020-01-01 08:00"], utc=True),
        "funding_ewm_30": [0.1, 0.2],
    })
    bars = pd.DataFrame({"open_time_utc": pd.to_datetime(
        ["2020-01-01 00:00","2020-01-01 03:00","2020-01-01 08:00","2020-01-01 09:00"], utc=True)})
    out = carry_funding_to_bars(bars, feat, ["funding_ewm_30"])
    assert out["funding_ewm_30"].tolist() == [0.1, 0.1, 0.2, 0.2]   # carried within window
    # causality: a future settlement cannot change an earlier bar
    out2 = carry_funding_to_bars(bars.iloc[:2], feat.iloc[:1], ["funding_ewm_30"])
    assert out2["funding_ewm_30"].tolist() == [0.1, 0.1]
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** with `pd.merge_asof(direction="backward")`

```python
# factors/funding_align.py
"""Carry 8h funding features onto the 1h bar grid by a backward as-of join.
DESIGN INVARIANT: bar N (close-time c) receives the most recent settlement with
calc_time <= c — a discrete-settlement carry-forward, NOT price interpolation and
never a future settlement. Honors the project execution convention (signal at N
close uses only data available at N's close)."""
from __future__ import annotations
import pandas as pd

def carry_funding_to_bars(bars: pd.DataFrame, funding_feat: pd.DataFrame,
                          cols: list[str]) -> pd.DataFrame:
    """bars, funding_feat both have UTC 'open_time_utc'; returns bars with `cols`
    carried backward-as-of. Bars before the first settlement -> NaN."""
    left = bars.sort_values("open_time_utc")
    right = funding_feat[["open_time_utc", *cols]].sort_values("open_time_utc")
    merged = pd.merge_asof(left, right, on="open_time_utc", direction="backward")
    return merged
```

- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Add a dedicated causality sentinel test** (mirror Path B G2): for a random funding-feature series, the carried value at every bar is bit-identical when settlements after that bar are deleted, reversed, and shuffled.
- [ ] **Step 6: Commit** (await authorization) — `feat(patha): causal 8h->1h funding carry`.

### Task B5: Register funding factors + build integration

**Files:** Modify `factors/registry.py`, `factors/build_features.py`; Test `tests/test_funding_factors.py`, `tests/test_factors.py`.

- [ ] **Step 1: Write the failing test** — the 4 funding factors appear in `registry.list_names()`; each passes G1 (AST no-future-ops) and G2 (future-bar invariance); `EXPECTED_FACTORS` in `tests/test_factors.py` updated to include them; `feature_version` changes when a funding compute fn changes.
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Register** the 4 funding factors in `_bootstrap_core_factors()` (import `factors.funding`), each `null_policy="nan_before_warmup_only"` + declared warmup. **CRITICAL (Codex): funding factors must NOT flow through the standard `build_features_df` OHLCV path** — it computes every registered factor on the OHLCV frame (`factors/build_features.py:89-98`), which has no `funding_rate` column and would error. Tag funding factors (e.g. a new `FactorSpec.input_source` field, default `"ohlcv"`, set `"funding"` for these) so the build ROUTES them: compute funding factors on the 8h settlement frame, then `carry_funding_to_bars` onto the 1h feature frame; OHLCV factors compute unchanged. Update `EXPECTED_FACTORS`.
- [ ] **Step 4: Run** the leakage-guard suite + factor suite — `python -m pytest tests/test_leakage_guards.py tests/test_funding_factors.py tests/test_factors.py -q` → all green. Rebuild the feature parquet (full dataset; `feature_version` bump).
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): register funding factors + build integration`.

---

# PHASE C — Hypotheses + verdict harness  *(rest of downstream register B — build)*

> Phase C is mostly **adaptation** of the existing, tested `pathb_*` harness to `patha_*` retargeted at the funding cohort + the LOCKed funding hypotheses. Where a module is a near-verbatim rename, the task says so; the genuinely-new logic (3 funding DSL builders, tiered sanity, marginal diagnostic) gets full TDD.

### Task C1: H1 funding DSL builder

**Files:** Create `backtest/patha_eval_gauntlet.py`; Test `tests/test_patha_gauntlet.py`.

- [ ] **Step 1: Write the failing test** — `build_h1_dsl()` returns a DSL `StrategyDSL` whose entry/exit/sizing match the LOCK: long on the complement of (`funding_pct_rank_270 >= 0.90` AND `funding_sign > 0`), `max_hold_bars=72`, vol-CDF ternary sizing band `[0.3,0.8]→1.0 else 0.5`. Assert it compiles (existing `dsl_compiler`) and uses only registered factors.

```python
# tests/test_patha_gauntlet.py
from backtest.patha_eval_gauntlet import build_h1_dsl, referenced_factors
from strategies.dsl_compiler import compile_dsl_to_strategy

def test_h1_dsl_matches_lock_and_compiles():
    dsl = build_h1_dsl()
    assert dsl.position_sizing != "full_equity"               # ternary SizingSpec
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)  # REAL compiler API; must not raise
    assert cls is not None
    # H1 is long on the COMPLEMENT of the extreme tail (De Morgan: 2 OR entry-groups);
    # exit = the tail-gate group; NO time-stop (LOCK Amendment A1).
    facs = referenced_factors(dsl)   # helper walks dsl.entry / dsl.exit / dsl.position_sizing
    assert {"funding_pct_rank_270", "funding_sign"} <= facs
    assert len(dsl.entry) == 2       # the two De Morgan OR-groups
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement `build_h1_dsl()`** with the REAL DSL API (`SizingSpec` `strategies/dsl.py:193-214`; `Condition.value` for factor-vs-scalar; OR-groups = a list of `ConditionGroup`; compile via `compile_dsl_to_strategy(dsl, write_manifest=False)`, NOT `compile_strategy`). **The DSL has NO `NOT` operator** (advisor F1), so H1's "flat when (`funding_pct_rank_270 ≥ 0.90` AND `funding_sign > 0`), long otherwise" is expressed by **De Morgan**: ENTRY = two OR-groups `[funding_pct_rank_270 < 0.90]` OR `[funding_sign <= 0]` (the ~90% long complement; `sign ≤ 0` covers {−1, 0}); EXIT = the single tail-gate group `(funding_pct_rank_270 ≥ 0.90 AND funding_sign > 0)`. **NO time-stop** (LOCK Amendment A1 — H1 exits ONLY via the tail-gate; `build_h1_dsl` sets no `max_hold`). Ternary `SizingSpec` per LOCK. Also implement `referenced_factors(dsl)` (walks `dsl.entry` / `dsl.exit` / `dsl.position_sizing`) for the tests.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): H1 funding DSL builder`.

### Task C2: H2 funding DSL builder

**Files:** Modify `backtest/patha_eval_gauntlet.py`; Test `tests/test_patha_gauntlet.py`.

- [ ] **Step 1: Write the failing test** — `build_h2_dsl()`: long when (regime permissive: `funding_ewm_30` rolling-270-percentile `< 0.80`) AND (`decay_linear_close_48 > decay_linear_close_168`); flat in de-risk regime; `max_hold_bars=24`; compiles. (Note: the regime percentile is itself a registered funding factor — see Step 3.)
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement.** Add a registered funding factor `funding_ewm_30_pctrank_270` (causal rolling percentile of `funding_ewm_30`, same `funding_pct_rank` pattern) in `factors/funding.py` + registry (TDD it like B3 — known-value + causality), then `build_h2_dsl()` uses `funding_ewm_30_pctrank_270 < 0.80` as the permissive gate AND the decay-MA cross as the directional confirm, factor-vs-factor.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): H2 funding DSL builder + ewm-pctrank factor`.

### Task C3: H3 funding DSL builder

**Files:** Modify `backtest/patha_eval_gauntlet.py`; Test `tests/test_patha_gauntlet.py`.

- [ ] **Step 1: Write the failing test** — `build_h3_dsl()`: long when `funding_ewm_60 > 0` AND `funding_pct_rank_270 <= 0.90` AND `decay_linear_close_48 > decay_linear_close_168`; exits per LOCK; `max_hold_bars=48`; compiles via `compile_dsl_to_strategy`. Assert H1/H3 are near-complementary on the funding tail: H3 `funding_pct_rank_270 ≤ 0.90` vs H1 `≥ 0.90`. **Tie-break note (both B2 legs):** they overlap at *exactly* 0.90 — measure-zero on a continuous percentile; H1's flat-gate takes precedence there, and H3 additionally requires `funding_ewm_60 > 0` + trend, so the boundary is immaterial. LOCK `≤`/`≥` values kept as-is.
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** `build_h3_dsl()` (OR-group exits: `funding_ewm_60 <= 0` OR trend roll-over OR `funding_pct_rank_270 > 0.90` OR time-stop 48).
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): H3 funding DSL builder`.

### Task C4: Adapt the verdict harness modules (`pathb_* → patha_*`)

**Files:** Create `backtest/patha_holdout_producer.py`, `patha_moments.py`, `patha_dsr_fwer.py`, `patha_earned_negative.py`, `patha_orchestrator.py`; Tests `tests/test_patha_*.py`.

- [ ] **Step 1:** For each, copy the corresponding `pathb_*` module, retarget the cohort to the 3 funding hypotheses + the funding feature columns, keep `PATHA_N_STAR = 3` (= `PATHB_N_STAR`), reuse `tier6_dsr.evaluate_candidate` + Form B + frozen `Z_PASS` unchanged. **Sealed `tier6_dsr_v1` is byte-untouched** (assert sha256 in the test).
- [ ] **Step 1b (escalation prong, advisor F3):** Create `backtest/patha_escalation.py` adapting `pathb_escalation.py`, but **redefine prong-(ii)**: Path A has NO Step-0 diagnostic (Path B's re-scored the dead-18; Path A is a fresh cohort). The escalation second prong keys on **`n_dsr_pass == 0`** (no funding variant lifted above `pass_B` → next-axis escalation warranted), NOT on `step0_lifted_any`. Signature: `a_escalation_advisory(taxonomy, n_dsr_pass)`. Test the prong on `n_dsr_pass=0` (warranted) vs `>0` (not).
- [ ] **Step 1c (tier threading, advisor F4):** Extend `patha_earned_negative.assemble_evidence(...)` to accept the per-leg strong/weak-sane tier (from Task C5) and set `verdict_rests_on_weak_sane_only = True` in the advisory bundle when the taxonomy's `any_mechanism_sane` rests solely on weak-sane legs. Test both cases.
- [ ] **Step 2:** Port each `pathb_*` test to `patha_*` (mechanism IDs H1/H2/H3 funding names; same structural assertions).
- [ ] **Step 3:** Run `python -m pytest tests/test_patha_*.py -q` → green; assert sealed `tier6_dsr_v1` sha256 4/4 unchanged.
- [ ] **Step 4: Commit** (await authorization) — `feat(patha): adapt verdict harness pathb->patha`.

### Task C5: Tiered 24h+72h mechanism-sanity (`patha_perleg_mechanism.py`)

**Files:** Create `backtest/patha_perleg_mechanism.py`; Test `tests/test_patha_perleg.py`.

- [ ] **Step 1: Write the failing test** — for each leg, the train-only conditional-return sign is computed at **both** 24-bar and 72-bar horizons; a leg with the hypothesized sign at both → `strong_sane`; at exactly one → `weak_sane`; neither → `refuted`. The per-leg record carries both horizon signs + the tier. H1 sane-sign is NEGATIVE (reversal); H2 = permissive-mean > de-risk-mean AND permissive-mean > 0; H3 sane-sign is POSITIVE.

```python
# tests/test_patha_perleg.py
from backtest.patha_perleg_mechanism import classify_leg
def test_strong_vs_weak_sane():
    # H3 hypothesized sign POSITIVE
    assert classify_leg(mean_24h=+0.01, mean_72h=+0.02, sane_sign="+")["tier"] == "strong_sane"
    assert classify_leg(mean_24h=+0.01, mean_72h=-0.02, sane_sign="+")["tier"] == "weak_sane"
    assert classify_leg(mean_24h=-0.01, mean_72h=-0.02, sane_sign="+")["tier"] == "refuted"
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** `classify_leg` + the per-leg driver (adapt `pathb_perleg_mechanism.py`'s `_leg_mean_sign`, evaluated at two horizons; record both).
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): tiered 24h+72h mechanism sanity`.

### Task C6: Fenced funding-marginal-contribution diagnostic

**Files:** Create `backtest/patha_marginal_diagnostic.py`; Test `tests/test_patha_marginal.py`.

- [ ] **Step 1: Write the failing test** — `funding_marginal(hyp_id, gated_equity, baseline_equity)` returns the Sharpe delta (funding-gated minus no-funding baseline) on identical bars, and is flagged `promotion_affecting=False, in_n_star=False`. The baseline for H2/H3 = the price-trend/always-long strategy WITHOUT the funding gate; for H1 = always-long.

```python
# tests/test_patha_marginal.py
import numpy as np
from backtest.patha_marginal_diagnostic import funding_marginal
def test_marginal_is_fenced_diagnostic():
    # identical-bar equity curves; the funding-gated variant underperforms the
    # no-funding baseline here (the fencing lives in computing both Sharpes on the SAME bars)
    gated    = np.array([1.0, 1.01, 1.00, 1.02])
    baseline = np.array([1.0, 1.02, 1.03, 1.05])
    out = funding_marginal("H2", gated_equity=gated, baseline_equity=baseline)
    assert out["funding_marginal_sharpe"] < 0         # funding hurt here
    assert out["promotion_affecting"] is False and out["in_n_star"] is False
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** the comparison (compute the no-funding baseline strategy from the same DSL with the funding predicate removed, run through the engine on the same bars, diff the net-of-cost Sharpe). Emit a `funding_marginal` record per hypothesis; assert it never feeds N\* or promotion.
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): fenced funding-marginal diagnostic`.

### Task C7: Hypothesis-class floors

**Files:** Modify `backtest/patha_orchestrator.py`; Test `tests/test_patha_floors.py`.

- [ ] **Step 1: Write the failing test** — H1 eligibility keys on the **count of defensive flat-exit episodes** (long→flat transitions driven by the funding gate) ≥ 200 on train; H2/H3 on `zero_fraction < 0.50` AND ≥ 200 trades on train; floors computed on the TRAIN window only; under-floor → `INDETERMINATE` (not a Tier-5 pass/fail).
- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** the floor checks (H1 counts flat-exit episodes from the position series; H2/H3 reuse the Path B occupancy+trade-count floor).
- [ ] **Step 4: Run to verify it passes.**
- [ ] **Step 5: Commit** (await authorization) — `feat(patha): hypothesis-class floors`.

> **STOP — Phase B/C register boundary.** Full suite green + sealed sha256 4/4 unchanged + 2-leg B2 on the build. Await Phase D register.

---

# PHASE D — Run (forward_2026 verdict)  *(downstream register C — verdict run)*

> Phase D produces the actual verdict. It is the verdict-producing operational run — a separate Charlie register. Re-verify sealed `tier6_dsr_v1` sha256 BEFORE and AFTER.

### Task D1: Train-only mechanism-sanity table

- [ ] **Step 1:** Run `patha_perleg_mechanism` on the train window (2020-21+2023) → per-leg conditional-return signs at 24h+72h + strong/weak/refuted tiers. **No validation/test/forward touch.**
- [ ] **Step 2:** Record the table; assert each leg's eligibility floor (Task C7) on train.
- [ ] **Step 3: Commit** the train-sanity artifact (await authorization).

### Task D2: Walk-forward train + forward_2026 Tier-5 holdout

- [ ] **Step 1:** Walk-forward on train (`check_wf_semantics_or_raise`, `corrected_test_boundary_v1`).
- [ ] **Step 2:** Produce the **forward_2026** single-run holdout (`patha_holdout_producer`, `check_evaluation_semantics_or_raise`, `single_run_holdout_v1`) → `holdout_sharpe` per hypothesis at 15 bps.
- [ ] **Step 3:** Run the fenced funding-marginal diagnostic (Task C6) on forward_2026.
- [ ] **Step 4: Commit** the holdout + diagnostic artifacts (await authorization).

### Task D3: DSR-FWER N\*=3 + taxonomy + advisory

- [ ] **Step 1:** Build `patha_moments` (CandidateMoments + integrity gate) from the forward holdout per-bar returns.
- [ ] **Step 2:** `patha_dsr_fwer` at N\*=3 → `pass_B` survivors.
- [ ] **Step 3:** `patha_earned_negative.assemble_evidence(...)` → taxonomy verdict (mechanism / process-refuted / b-positive), with the per-leg strong/weak-sane tiers threaded in (sets `verdict_rests_on_weak_sane_only`), the funding-marginal diagnostic, and the funding-decay temper in the advisory bundle; escalation via `patha_escalation.a_escalation_advisory(taxonomy, n_dsr_pass)` keyed on `n_dsr_pass == 0` (no Step-0 for Path A).
- [ ] **Step 4:** Write `data/phase2c_evaluation_gate/patha_verdict_v1/patha_verdict_advisory.json`.
- [ ] **Step 5:** Re-verify sealed `tier6_dsr_v1` sha256 4/4 unchanged.
- [ ] **Step 6: Commit** the verdict artifact (await authorization).

### Task D4: Verdict read + cycle SEAL

- [ ] **Step 1:** 2-leg B2 on the verdict result (Codex + advisor).
- [ ] **Step 2:** Present the advisory verdict to Charlie for the **binding earned-negative-or-positive read** (Charlie register; never auto-fire). If `b_positive`: 2025 OOS confirmation required before any promotion. If earned-negative: next-axis escalation (OI/basis/short legs/continuous sizing) is a *separate* future register (anti-pre-emption).
- [ ] **Step 3:** On Charlie's read: Phase Marker advance (CLAUDE.md + `docs/phase_marker_history.md`, atomic) + METHODOLOGY_NOTES lessons + `superpowers:finishing-a-development-branch`.

---

## Self-review (against the LOCK + spec)

- **Spec/LOCK coverage:** Pre-reg 1 (3 hypotheses, exact params) → Tasks C1/C2/C3 + the funding factors B1–B3 + the H2 ewm-pctrank in C2. Pre-reg 2 (15bps, forward_2026 Tier-5, DSR-FWER N\*=3) → D2/D3 + C4. Pre-reg 3 (cost-aware, floors, single-factor sizing, causal carry, fenced diagnostic) → B4/C6/C7 + sizing in C1. Pre-reg 4 (taxonomy, tiered sanity, escalation) → C5/D3. Ingestion design (spec §5) → Phase A. Harness reuse (spec §4) → C4. **No gap found.**
- **Placeholder scan:** ingestion download/checksum wrapper (A2) + reconcile (A4) + incremental (A5) reference the existing OHLCV modules as the pattern rather than re-printing them in full — acceptable (they are near-verbatim mirrors of tested code); the genuinely-new logic (parse, validate, factors, carry, DSL builders, tiered sanity, marginal diagnostic) has full code/tests. No "TBD"/"handle edge cases" placeholders.
- **Type/name consistency:** factor names (`funding_sign`, `funding_ewm_30`, `funding_ewm_60`, `funding_pct_rank_270`, `funding_ewm_30_pctrank_270`), `carry_funding_to_bars(bars, funding_feat, cols)`, `classify_leg(mean_24h, mean_72h, sane_sign)`, `funding_marginal(hyp_id, gated_equity, baseline_equity)`, `referenced_factors(dsl)`, `a_escalation_advisory(taxonomy, n_dsr_pass)`, `compile_dsl_to_strategy(dsl, write_manifest=False)` (the REAL compiler API), `PATHA_N_STAR=3`, `build_h1/h2/h3_dsl()` — used consistently across tasks (B2-corrected: no `compile_strategy`/`dsl.referenced_factors()`/scalar `funding_marginal` aliases remain).
- **Register boundaries:** Phase A / B+C / D STOP markers present; per-task commits gated on Charlie authorization.

---

## Execution handoff

This plan is the scoping cycle's final deliverable. Per the register discipline, **execution does not begin until Charlie registers Phase A**. When execution is authorized, the recommended approach is **subagent-driven-development** (fresh subagent per task + two-stage review), with a 2-leg B2 at each phase boundary (Charlie-instructed). Ingestion (Phase A), build (Phase B/C), and run (Phase D) are each their own Charlie register-event.
