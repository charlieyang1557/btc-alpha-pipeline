# A-1 SD-E-γ Stationary-Bootstrap Variance Overlay — Implementation Plan

> **⚠️ SUPERSEDED IN PART (Path-2 re-scope, 2026-05-30):** Chunk 1 (the bootstrap primitives, Tasks 1–4) was built as planned. Tasks 5–10 (the *inflation-ratio measurement* track) were **superseded** when implementation discovered the cohort returns are sparse (low-trade-frequency) and the per-bar-Sharpe bootstrap measurement is not feasible. The authoritative deliverable is the spec's **§12 Path-2 Erratum E1** (primitive + verdict-invariance attestation + sparsity/degeneracy *suitability diagnostic* + honest "measurement inconclusive" conclusion). See [`docs/phase5/A1_SERIALCORR_BOOTSTRAP_SUITABILITY_NOTE.md`](../../phase5/A1_SERIALCORR_BOOTSTRAP_SUITABILITY_NOTE.md). The Tasks 5–10 below are retained for historical traceability only.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `backtest/tier6_bootstrap.py` — a diagnostic-only, verdict-invariant stationary-bootstrap (Politis–Romano 1994) serial-correlation-robust Sharpe-estimator SE overlay on the sealed closed-form Tier 6 DSR — that measures the per-candidate `inflation_ratio = SE_boot/SE_mertens` on the recovered `phase4_forward_2026_15bps_v1` cohort (18 authoritative + 21 companion) and emits isolated, NON-AUTHORITATIVE artifacts.

**Architecture:** New module imports from (never modifies) `backtest/tier6_dsr.py`, reusing its integrity-gated loaders (`load_candidate_moments`), cohort partitioner (`derive_cohort`), and the sealed `evaluate_candidate`/`mertens_variance` for the baseline quantities. The bootstrap SE is computed by a vectorized-over-replicates resampler; everything is keyed to deterministic per-(candidate, block-length) RNG substreams. No pass/fail track; the 0/18 verdict is mathematically invariant (all `SR̂ − SR* < 0`).

**Tech Stack:** Python 3.11, numpy, pandas, pyarrow, scipy (all already pinned); pytest. No new dependency.

**Spec:** `docs/superpowers/specs/2026-05-30-a1-sd-e-gamma-stationary-bootstrap-overlay-design.md` (v2, Charlie-confirmed). Section refs below (e.g. "spec §3.2") point there.

---

## File Structure

- **Create** `backtest/tier6_bootstrap.py` — the whole module (target ≤ ~450 lines; one responsibility: the serial-correlation-robust SE diagnostic).
- **Create** `tests/test_tier6_bootstrap.py` — the whole test suite.
- **Read-only imports from** `backtest/tier6_dsr.py`: `load_candidate_moments`, `mertens_variance`, `evaluate_candidate`, `derive_cohort`, `_read_cohort_csv`, `CandidateMoments`, `HOLDOUT_DIR`, `EVALUATION_GATE_DIR`, `DEFAULT_COHORT`, `N_STAR`, `ALPHA`, `MOMENT_RECOMPUTE_EPS`, `PROJECT_ROOT`.
- **Create (runtime output)** `data/phase2c_evaluation_gate/tier6_serialcorr_robustness_v1/` — `serialcorr_results.csv`, `serialcorr_companion.csv`, `serialcorr_attestation.json`.

**Commit cadence (matches the Tier 6 cycle's chunk-review pattern):** commit at the 3 chunk boundaries + a final whole-module commit, NOT per-task. Each commit is gated on Charlie's authorization (foundation commit bundles spec + this plan; implementation commits per chunk). Chunks:
- **Chunk 1 (Tasks 1–4):** primitives — bootstrap indices, bootstrap SE, mertens_se, substream RNG.
- **Chunk 2 (Tasks 5–6):** per-candidate record + cohort runner.
- **Chunk 3 (Tasks 7–9):** emitters + CLI + integration/governance tests + real run.

---

## Task 1: Module scaffold + constants

**Files:**
- Create: `backtest/tier6_bootstrap.py`
- Test: `tests/test_tier6_bootstrap.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_tier6_bootstrap.py
import numpy as np
import pytest
from backtest import tier6_bootstrap as tb


def test_module_constants():
    assert tb.BLOCK_LEN_GRID == (1, 6, 12, 24, 48, 96)
    assert tb.BASE_SEED == 20260529
    assert tb.DEFAULT_N_REPLICATES == 5000
    assert tb.OUT_DIR.name == "tier6_serialcorr_robustness_v1"
    assert tb.OUT_DIR.parent.name == "phase2c_evaluation_gate"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_tier6_bootstrap.py::test_module_constants -v`
Expected: FAIL with `ModuleNotFoundError` / `AttributeError`.

- [ ] **Step 3: Write minimal implementation**

```python
# backtest/tier6_bootstrap.py
"""A-1: SD-E-γ stationary-bootstrap variance overlay for the closed-form Tier 6
Deflated Sharpe Ratio. DIAGNOSTIC ONLY — verdict-invariant (all SR̂ < SR*); no
parallel pass/fail track. Measures per-candidate inflation_ratio = SE_boot/
SE_mertens on the recovered phase4_forward_2026_15bps_v1 cohort. See design spec
docs/superpowers/specs/2026-05-30-a1-sd-e-gamma-stationary-bootstrap-overlay-design.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from backtest.tier6_dsr import (
    ALPHA,
    DEFAULT_COHORT,
    EVALUATION_GATE_DIR,
    HOLDOUT_DIR,
    MOMENT_RECOMPUTE_EPS,
    N_STAR,
    PROJECT_ROOT,
    CandidateMoments,
    _read_cohort_csv,
    deflated_z,
    derive_cohort,
    load_candidate_moments,
    mertens_variance,
    sr_star,
)

logger = logging.getLogger("tier6_bootstrap")

BLOCK_LEN_GRID: tuple[int, ...] = (1, 6, 12, 24, 48, 96)
BASE_SEED = 20260529
DEFAULT_N_REPLICATES = 5000
DEGENERATE_REPLICATE_FRACTION = 0.001  # >0.1% zero-variance replicates -> raise
OUT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_serialcorr_robustness_v1"
ARTIFACT_BANNER = (
    "diagnostic; NON-AUTHORITATIVE; no parallel pass/fail track; "
    "verdict invariant (all SR_hat < SR_star)"
)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_tier6_bootstrap.py::test_module_constants -v`
Expected: PASS.

---

## Task 2: `stationary_bootstrap_indices` — single reference resample

**Files:**
- Modify: `backtest/tier6_bootstrap.py`
- Test: `tests/test_tier6_bootstrap.py`

Spec §3.2. This is the clear reference implementation (used to pin block structure); `bootstrap_sharpe_se` (Task 3) uses a vectorized variant validated against it.

- [ ] **Step 1: Write the failing tests**

```python
def test_bootstrap_indices_shape_and_range():
    rng = np.random.default_rng(0)
    idx = tb.stationary_bootstrap_indices(100, 12, rng)
    assert idx.shape == (100,)
    assert idx.min() >= 0 and idx.max() < 100


def test_bootstrap_indices_deterministic():
    a = tb.stationary_bootstrap_indices(50, 6, np.random.default_rng(7))
    b = tb.stationary_bootstrap_indices(50, 6, np.random.default_rng(7))
    np.testing.assert_array_equal(a, b)


def test_bootstrap_indices_L1_is_all_fresh_draws():
    # L=1 -> p=1 -> every position is an independent fresh start (no runs).
    rng = np.random.default_rng(1)
    idx = tb.stationary_bootstrap_indices(2000, 1, rng)
    # consecutive-increment fraction should be ~ chance (1/T), not block-like.
    inc = np.mean((idx[1:] - idx[:-1]) % 2000 == 1)
    assert inc < 0.05


def test_bootstrap_indices_largeL_has_long_runs():
    rng = np.random.default_rng(2)
    idx = tb.stationary_bootstrap_indices(2000, 200, rng)
    inc = np.mean((idx[1:] - idx[:-1]) % 2000 == 1)
    assert inc > 0.8  # ~ 1 - 1/200


def test_bootstrap_indices_rejects_tiny_T():
    with pytest.raises(ValueError):
        tb.stationary_bootstrap_indices(1, 6, np.random.default_rng(0))
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k bootstrap_indices -v`
Expected: FAIL (`AttributeError: ... stationary_bootstrap_indices`).

- [ ] **Step 3: Implement**

```python
def stationary_bootstrap_indices(
    T: int, expected_block_len: float, rng: np.random.Generator
) -> np.ndarray:
    """One Politis-Romano stationary-bootstrap resample index array of length T.

    Geometric block lengths (mean ``expected_block_len``), circular wrap. With
    ``p = 1/expected_block_len``: start at a uniform index; each subsequent
    position advances ``(prev+1) % T`` with prob ``1-p`` or jumps to a fresh
    uniform start with prob ``p``.
    """
    if T < 2:
        raise ValueError(f"T must be >= 2; got {T}")
    if expected_block_len < 1:
        raise ValueError(f"expected_block_len must be >= 1; got {expected_block_len}")
    p = 1.0 / expected_block_len
    idx = np.empty(T, dtype=np.int64)
    idx[0] = int(rng.integers(0, T))
    u = rng.random(T)
    fresh = rng.integers(0, T, size=T)
    for i in range(1, T):
        idx[i] = fresh[i] if u[i] < p else (idx[i - 1] + 1) % T
    return idx
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k bootstrap_indices -v`
Expected: PASS (5 tests).

---

## Task 3: `bootstrap_sharpe_se` — vectorized-over-replicates SE

**Files:**
- Modify: `backtest/tier6_bootstrap.py`
- Test: `tests/test_tier6_bootstrap.py`

Spec §3.2 (input contract: finite-filtered length-T; SR_b = mean/std(ddof=0); SE_boot = std(ddof=1)) + §3.5. Vectorized over B replicates for performance (a per-resample Python loop over 1.17M resamples is infeasible).

- [ ] **Step 1: Write the failing tests**

```python
def _ar1(n, phi, seed):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(n)
    x = np.empty(n)
    x[0] = e[0]
    for i in range(1, n):
        x[i] = phi * x[i - 1] + e[i]
    return x


def test_boot_se_iid_matches_analytic():
    # i.i.d. Gaussian: SE_boot(L=1) ~ 1/sqrt(T-1) (the null Sharpe SE).
    rng_data = np.random.default_rng(42)
    r = rng_data.standard_normal(3000)
    se = tb.bootstrap_sharpe_se(r, 1, 4000, np.random.default_rng(123))
    analytic = 1.0 / np.sqrt(len(r) - 1)
    assert abs(se / analytic - 1.0) < 0.08


def test_boot_se_positive_autocorr_inflates():
    r = _ar1(3000, 0.5, seed=9)
    se1 = tb.bootstrap_sharpe_se(r, 1, 4000, np.random.default_rng(5))
    se24 = tb.bootstrap_sharpe_se(r, 24, 4000, np.random.default_rng(5))
    assert se24 > se1 * 1.10  # positive AR(1) inflates the block-bootstrap SE


def test_boot_se_deterministic():
    r = _ar1(1000, 0.3, seed=3)
    a = tb.bootstrap_sharpe_se(r, 12, 2000, np.random.default_rng(11))
    b = tb.bootstrap_sharpe_se(r, 12, 2000, np.random.default_rng(11))
    assert a == b


def test_boot_se_rejects_nonfinite_input():
    r = np.array([np.nan, 1.0, 2.0, 3.0])  # leading-NaN like the real parquet
    with pytest.raises(ValueError, match="finite"):
        tb.bootstrap_sharpe_se(r, 6, 100, np.random.default_rng(0))


def test_boot_se_rejects_flat_series():
    with pytest.raises(ValueError):
        tb.bootstrap_sharpe_se(np.zeros(500), 6, 100, np.random.default_rng(0))
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k boot_se -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

```python
def bootstrap_sharpe_se(
    returns: np.ndarray,
    expected_block_len: float,
    n_replicates: int,
    rng: np.random.Generator,
) -> float:
    """Stationary-bootstrap SE of the per-bar Sharpe estimator.

    ``returns`` MUST be the finite-filtered length-T array (spec §3.2; the real
    parquet has a leading-NaN bar). Vectorized over replicates: builds a
    ``(B, T)`` resample index matrix (T-loop, vectorized across B), gathers,
    computes ``SR_b = mean/std(ddof=0)`` per replicate, returns
    ``std({SR_b}, ddof=1)``. Replicates with zero resample variance are dropped;
    if more than 0.1% are dropped the input is degenerate and we raise.
    """
    r = np.asarray(returns, dtype=np.float64)
    T = r.shape[0]
    if T < 2:
        raise ValueError(f"T must be >= 2; got {T}")
    if not np.all(np.isfinite(r)):
        raise ValueError("non-finite returns: pass the finite-filtered length-T array")
    if expected_block_len < 1:
        raise ValueError(f"expected_block_len must be >= 1; got {expected_block_len}")
    p = 1.0 / expected_block_len
    B = int(n_replicates)
    if B < 2:
        raise ValueError(f"n_replicates must be >= 2 (std ddof=1 needs >=2); got {B}")
    # NOTE: this (B,T) resampler is DISTRIBUTION-equivalent to the single-resample
    # stationary_bootstrap_indices, NOT same-RNG-stream identical (it consumes the
    # generator per time-step across B). The L=1 plain-bootstrap equivalence test
    # validates distributional correctness. n_skip below is a raise-only degeneracy
    # tripwire (==0 at T~2500), intentionally not surfaced in the per-row record.
    idx = np.empty((B, T), dtype=np.int64)
    idx[:, 0] = rng.integers(0, T, size=B)
    for i in range(1, T):
        jump = rng.random(B) < p
        fresh = rng.integers(0, T, size=B)
        idx[:, i] = np.where(jump, fresh, (idx[:, i - 1] + 1) % T)
    samples = r[idx]                       # (B, T)
    means = samples.mean(axis=1)
    stds = samples.std(axis=1, ddof=0)     # sealed SR convention
    valid = stds > 0.0
    n_skip = int((~valid).sum())
    if n_skip > DEGENERATE_REPLICATE_FRACTION * B:
        raise ValueError(f"{n_skip}/{B} degenerate (zero-variance) bootstrap replicates")
    sr_b = means[valid] / stds[valid]
    return float(sr_b.std(ddof=1))
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k boot_se -v`
Expected: PASS (5 tests). (`test_boot_se_iid_matches_analytic` runs B=4000 over T=3000 — a few seconds.)

---

## Task 4: `mertens_se` + per-(candidate, L) substream RNG

**Files:**
- Modify: `backtest/tier6_bootstrap.py`
- Test: `tests/test_tier6_bootstrap.py`

Spec §3.1 (mertens_se) + §3.4 (determinism: pinned hash→int + entropy-keyed substreams; ban `hash()`/spawn-order).

- [ ] **Step 1: Write the failing tests**

```python
def test_mertens_se_matches_sqrt_variance():
    from backtest.tier6_dsr import mertens_variance
    sr, g3, g4, T = 0.01, -0.2, 8.0, 2500
    assert tb.mertens_se(sr, g3, g4, T) == np.sqrt(mertens_variance(sr, g3, g4, T))


def test_substream_rng_stable_and_keyed():
    a = tb.substream_rng("abc123", 24)
    b = tb.substream_rng("abc123", 24)
    # same key -> identical stream
    assert a.random() == b.random()
    # different block_len -> different stream
    assert tb.substream_rng("abc123", 24).random() != tb.substream_rng("abc123", 48).random()
    # different hash -> different stream
    assert tb.substream_rng("abc123", 24).random() != tb.substream_rng("def456", 24).random()
    # different base_seed -> different stream (PFR: --seed must not be a no-op)
    assert tb.substream_rng("abc123", 24, 1).random() != tb.substream_rng("abc123", 24, 2).random()


def test_substream_rng_order_independent():
    # building stream for (hashB, 24) does not depend on whether (hashA, 24) was built first
    s1 = tb.substream_rng("hashB", 24).random()
    _ = tb.substream_rng("hashA", 24).random()
    s2 = tb.substream_rng("hashB", 24).random()
    assert s1 == s2
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k "mertens_se or substream" -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

```python
def mertens_se(sr: float, gamma3: float, gamma4: float, T: int) -> float:
    """i.i.d. baseline SE of the Sharpe estimator = sqrt(mertens_variance)."""
    return float(np.sqrt(mertens_variance(sr, gamma3, gamma4, T)))


def _stable_hash_int(hypothesis_hash: str) -> int:
    """Deterministic, process-independent hash->int (spec §3.4). NOT builtin hash()."""
    return int.from_bytes(hashlib.sha256(hypothesis_hash.encode()).digest()[:8], "big")


def substream_rng(
    hypothesis_hash: str, block_len: int, base_seed: int = BASE_SEED
) -> np.random.Generator:
    """Independent RNG for a (candidate, block_len) cell, keyed by explicit entropy.

    Order-independent (no SeedSequence.spawn): entropy is ``[base_seed,
    stable_hash_int, block_len]`` so reordering candidates or extending
    BLOCK_LEN_GRID never perturbs an existing cell's stream. ``base_seed`` is
    threaded from the CLI ``--seed`` (PFR HIGH: it must NOT be a no-op).
    """
    seq = np.random.SeedSequence(
        [int(base_seed), _stable_hash_int(hypothesis_hash), int(block_len)]
    )
    return np.random.default_rng(seq)
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k "mertens_se or substream" -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Chunk 1 commit** (Charlie-authorized)

```bash
git add backtest/tier6_bootstrap.py tests/test_tier6_bootstrap.py
git commit -m "feat(tier6-bootstrap): A-1 primitives — stationary bootstrap SE + mertens_se + deterministic substream RNG"
```

---

## Task 5: `evaluate_candidate_bootstrap` — per-candidate record

**Files:**
- Modify: `backtest/tier6_bootstrap.py`
- Test: `tests/test_tier6_bootstrap.py`

Spec §3.1, §4.4 (degenerate parity), §8.3 (L1 baseline decomposition). Reuses sealed `evaluate_candidate` for `sr_star_B`/`deflated_z_B`/`excess`.

- [ ] **Step 1: Write the failing tests**

```python
def _fake_cm(sr=0.01, g3=-0.2, g4=8.0, T=2500, h="abc123"):
    return tb.CandidateMoments(h, "nm", "th", sr, g3, g4, T, 100)


def test_evaluate_candidate_bootstrap_schema_and_identity():
    cm = _fake_cm()
    r = _ar1(cm.T, 0.4, seed=4)
    rec = tb.evaluate_candidate_bootstrap(cm, r, n_replicates=2000, base_seed=tb.BASE_SEED)
    for L in tb.BLOCK_LEN_GRID:
        assert rec[f"se_boot_L{L}"] > 0
        assert rec[f"inflation_L{L}"] == pytest.approx(rec[f"se_boot_L{L}"] / rec["se_mertens"])
    # identity: inflation = deflated_z / robust_se_z_context (shared numerator)
    z = rec["deflated_z_B"]
    zc = rec["robust_se_z_context_L24"]
    assert rec["inflation_L24"] == pytest.approx(z / zc, rel=1e-9)
    # serialcorr increment relative to L1 baseline
    assert rec["serialcorr_increment_L24"] == pytest.approx(
        rec["inflation_L24"] / rec["inflation_L1"]
    )
    assert rec["mertens_degenerate_flag"] is False


def test_evaluate_candidate_bootstrap_degenerate_parity():
    # term = 1 - 2*1 + ((3-1)/4)*1 = -0.5 <= 0 -> mertens_se/deflated_z raise ->
    # record has NaN se_mertens/deflated_z/inflation + flag, but SE_boot still
    # computed, no crash. (Verified term=-0.5 against mertens_variance.)
    cm = _fake_cm(sr=1.0, g3=2.0, g4=3.0, T=2500)
    r = _ar1(cm.T, 0.2, seed=2)
    rec = tb.evaluate_candidate_bootstrap(cm, r, n_replicates=500, base_seed=tb.BASE_SEED)
    assert rec["mertens_degenerate_flag"] is True
    assert np.isnan(rec["se_mertens"])
    assert np.isnan(rec["deflated_z_B"])
    assert np.isnan(rec["inflation_L24"])
    assert rec["se_boot_L24"] > 0
```

(Note: pick `(sr,g3,g4)` in the degenerate test that actually drives `mertens_variance` term ≤ 0 — verify with a one-off `python -c` against `mertens_variance` while writing; the engine raises when `1 - g3*sr + ((g4-1)/4)*sr^2 <= 0`.)

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k evaluate_candidate_bootstrap -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

```python
def evaluate_candidate_bootstrap(
    cm: CandidateMoments,
    returns: np.ndarray,
    *,
    block_grid: tuple[int, ...] = BLOCK_LEN_GRID,
    n_replicates: int = DEFAULT_N_REPLICATES,
    base_seed: int = BASE_SEED,
) -> dict:
    """Per-candidate diagnostic record (spec §3.1/§4.4/§8.3). No pass/fail.

    Degenerate-safe (PFR CRITICAL-1): ``evaluate_candidate(cm)`` is NOT called —
    it would raise on a non-positive Mertens term before we could flag it. SR* is
    moment-independent (``sr_star(N*, T, "B")``), so ``sr_star_B`` + ``excess`` are
    always computable. ``se_mertens`` + ``deflated_z_B`` go through
    ``mertens_variance`` and are wrapped: on a non-positive term they become NaN +
    ``mertens_degenerate_flag=True`` (never crash). The bootstrap SE is always
    well-defined regardless of the asymptotic term.
    """
    r = np.asarray(returns, dtype=np.float64)
    if r.shape[0] != cm.T:
        raise ValueError(f"returns length {r.shape[0]} != cm.T {cm.T} for {cm.hypothesis_hash}")
    if not np.all(np.isfinite(r)):
        raise ValueError("non-finite returns: pass the finite-filtered length-T array")

    sr_star_b = sr_star(N_STAR, cm.T, "B")  # moment-independent -> degenerate-safe
    excess = cm.sr_per_bar - sr_star_b
    rec: dict = {
        "hypothesis_hash": cm.hypothesis_hash,
        "name": cm.name,
        "theme": cm.theme,
        "T": cm.T,
        "sr_per_bar": cm.sr_per_bar,
        "gamma3": cm.gamma3,
        "gamma4": cm.gamma4,
        "sr_star_B": sr_star_b,
        "excess": excess,
        "g4_high_flag": bool(cm.gamma4 >= 50.0),
    }
    try:
        se_m = mertens_se(cm.sr_per_bar, cm.gamma3, cm.gamma4, cm.T)
        rec["se_mertens"] = se_m
        rec["deflated_z_B"] = deflated_z(cm.sr_per_bar, sr_star_b, cm.gamma3, cm.gamma4, cm.T)
        rec["mertens_degenerate_flag"] = False
    except ValueError:
        se_m = float("nan")
        rec["se_mertens"] = se_m
        rec["deflated_z_B"] = float("nan")
        rec["mertens_degenerate_flag"] = True

    inflations: dict[int, float] = {}
    for L in block_grid:
        se_b = bootstrap_sharpe_se(
            r, L, n_replicates, substream_rng(cm.hypothesis_hash, L, base_seed)
        )
        rec[f"se_boot_L{L}"] = se_b
        infl = se_b / se_m if np.isfinite(se_m) and se_m > 0 else float("nan")
        rec[f"inflation_L{L}"] = infl
        inflations[L] = infl
    finite_infl = [v for v in inflations.values() if np.isfinite(v)]
    rec["inflation_band_min"] = min(finite_infl) if finite_infl else float("nan")
    rec["inflation_band_max"] = max(finite_infl) if finite_infl else float("nan")
    base_infl = inflations.get(1, float("nan"))
    for L in block_grid:
        if L == 1:
            continue
        rec[f"serialcorr_increment_L{L}"] = (
            inflations[L] / base_infl if np.isfinite(base_infl) and base_infl > 0 else float("nan")
        )
    se_b24 = rec["se_boot_L24"]
    rec["robust_se_z_context_L24"] = excess / se_b24 if se_b24 > 0 else float("nan")
    return rec
```

(Fix the `g4_high_flag` line to simply `bool(cm.gamma4 >= 50.0)` — drop the spurious `base.get(...)` clause; shown here as a reminder to keep it clean.)

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k evaluate_candidate_bootstrap -v`
Expected: PASS.

---

## Task 6: `run_cohort_bootstrap` — load 18+21 + attestation + sealed-hash capture

**Files:**
- Modify: `backtest/tier6_bootstrap.py`
- Test: `tests/test_tier6_bootstrap.py`

Spec §4.5. Reuses `_read_cohort_csv` + `derive_cohort` + `load_candidate_moments` (sha256 + lineage gates). Reads the finite-filtered `return` array AFTER the integrity gate.

- [ ] **Step 1: Write the failing test** (uses the real cohort; integration-style but fast at low replicates)

```python
def test_run_cohort_bootstrap_counts_and_attestation():
    res = tb.run_cohort_bootstrap(n_replicates=300, base_seed=tb.BASE_SEED)
    assert len(res.authoritative) == 18
    assert len(res.companion) == 21
    assert res.attestation["all_excess_negative"] is True
    assert res.attestation["max_excess"] < 0
    assert res.attestation["verdict_invariant"] is True
    assert res.attestation["n_replicates"] == 300
    # every authoritative row has the 6 inflation columns
    for row in res.authoritative:
        for L in tb.BLOCK_LEN_GRID:
            assert f"inflation_L{L}" in row
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k run_cohort_bootstrap -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

```python
@dataclass(frozen=True)
class CohortBootstrapResult:
    authoritative: list[dict]
    companion: list[dict]
    attestation: dict


def _load_finite_returns(hypothesis_hash: str, holdout_dir: Path) -> np.ndarray:
    """Finite-filtered length-T return array (after load_candidate_moments' gate)."""
    pq = holdout_dir / hypothesis_hash / "returns_per_bar.parquet"
    r = pd.read_parquet(pq)["return"].to_numpy(dtype=np.float64)
    return r[np.isfinite(r)]


def _sealed_tier6_dsr_sha256() -> dict[str, str]:
    """sha256 of every file under the sealed tier6_dsr_v1/ dir (immutability gate)."""
    sealed = PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1"
    out: dict[str, str] = {}
    for f in sorted(sealed.glob("*")):
        if f.is_file():
            out[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def run_cohort_bootstrap(
    cohort: str = DEFAULT_COHORT,
    *,
    n_replicates: int = DEFAULT_N_REPLICATES,
    base_seed: int = BASE_SEED,
) -> CohortBootstrapResult:
    holdout_dir = EVALUATION_GATE_DIR / cohort
    df = _read_cohort_csv(holdout_dir=holdout_dir)
    locked, companion = derive_cohort(df)

    def _one(h: str) -> dict:
        cm = load_candidate_moments(h, df, holdout_dir=holdout_dir)  # sha256 + lineage gate
        r = _load_finite_returns(h, holdout_dir)
        if len(r) != cm.T:
            raise ValueError(f"finite-return length {len(r)} != cm.T {cm.T} for {h}")
        return evaluate_candidate_bootstrap(
            cm, r, n_replicates=n_replicates, base_seed=base_seed
        )

    auth = [_one(h) for h in locked]
    comp = [{**_one(h), "non_authoritative": True} for h in companion]

    excesses = [row["excess"] for row in auth]
    all_infl = [row[f"inflation_L{L}"] for row in auth for L in BLOCK_LEN_GRID]
    finite_infl = [v for v in all_infl if np.isfinite(v)]
    by_block = {
        f"L{L}": float(np.nanmedian([row[f"inflation_L{L}"] for row in auth]))
        for L in BLOCK_LEN_GRID
    }
    incr_by_block = {
        f"L{L}": float(np.nanmedian([row[f"serialcorr_increment_L{L}"] for row in auth]))
        for L in BLOCK_LEN_GRID if L != 1
    }
    try:
        source_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        source_commit = "unknown"
    attestation = {
        "banner": ARTIFACT_BANNER,
        "cohort": cohort,
        "base_seed": base_seed,
        "n_replicates": n_replicates,
        "block_len_grid": list(BLOCK_LEN_GRID),
        "hash_to_int_rule": "int.from_bytes(sha256(hash)[:8], 'big')",
        "n_authoritative": len(auth),
        "n_companion": len(comp),
        "all_excess_negative": bool(all(e < 0 for e in excesses)),
        "max_excess": float(max(excesses)),
        "verdict_invariant": bool(all(e < 0 for e in excesses)),
        "inflation_ratio_summary": {
            "min": float(min(finite_infl)) if finite_infl else float("nan"),
            "median": float(np.median(finite_infl)) if finite_infl else float("nan"),
            "max": float(max(finite_infl)) if finite_infl else float("nan"),
            "by_block_len_median": by_block,
        },
        "serialcorr_increment_summary": {"by_block_len_median": incr_by_block},
        "sealed_tier6_dsr_v1_sha256": _sealed_tier6_dsr_sha256(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": source_commit,
    }
    return CohortBootstrapResult(auth, comp, attestation)
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k run_cohort_bootstrap -v`
Expected: PASS.

- [ ] **Step 5: Chunk 2 commit** (Charlie-authorized)

```bash
git add backtest/tier6_bootstrap.py tests/test_tier6_bootstrap.py
git commit -m "feat(tier6-bootstrap): A-1 per-candidate record + cohort runner (18+21) + attestation + sealed-hash capture"
```

---

## Task 7: Emitters (CSV + attestation JSON) + isolation

**Files:**
- Modify: `backtest/tier6_bootstrap.py`
- Test: `tests/test_tier6_bootstrap.py`

Spec §6. Mirror `tier6_dsr._write_csv` style (`csv.DictWriter`, explicit field order, `extrasaction="ignore"`, banner row/field).

- [ ] **Step 1: Write the failing test** (writes to a tmp dir)

```python
def test_emit_artifacts(tmp_path):
    import json
    import pandas as pd
    res = tb.run_cohort_bootstrap(n_replicates=200, base_seed=tb.BASE_SEED)
    tb.emit_artifacts(res, out_dir=tmp_path)
    # banner is a leading "# ..." comment line -> read with comment="#"
    rows = pd.read_csv(tmp_path / "serialcorr_results.csv", comment="#")
    assert len(rows) == 18
    assert "inflation_L24" in rows.columns
    comp = pd.read_csv(tmp_path / "serialcorr_companion.csv", comment="#")
    assert len(comp) == 21
    att = json.loads((tmp_path / "serialcorr_attestation.json").read_text())
    assert att["verdict_invariant"] is True
    assert "NON-AUTHORITATIVE" in att["banner"]
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k emit_artifacts -v`
Expected: FAIL.

- [ ] **Step 3: Implement** (define `_RESULT_FIELDS` to match the spec §6 schema; write the banner as the JSON `banner` field and a leading `# <banner>` comment line in each CSV).

```python
import csv

_RESULT_FIELDS = (
    ["hypothesis_hash", "name", "theme", "T", "sr_per_bar", "gamma3", "gamma4",
     "sr_star_B", "excess", "deflated_z_B", "se_mertens"]
    + [f"se_boot_L{L}" for L in BLOCK_LEN_GRID]
    + [f"inflation_L{L}" for L in BLOCK_LEN_GRID]
    + [f"serialcorr_increment_L{L}" for L in BLOCK_LEN_GRID if L != 1]
    + ["inflation_band_min", "inflation_band_max", "robust_se_z_context_L24",
       "g4_high_flag", "mertens_degenerate_flag"]
)


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        f.write(f"# {ARTIFACT_BANNER}\n")
        w = csv.DictWriter(f, fieldnames=_RESULT_FIELDS, extrasaction="ignore", restval="")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def emit_artifacts(res: CohortBootstrapResult, out_dir: Path | None = None) -> None:
    # PFR: resolve OUT_DIR at runtime (not a def-time default arg) so a test that
    # monkeypatches tb.OUT_DIR is honored.
    out_dir = out_dir if out_dir is not None else OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(out_dir / "serialcorr_results.csv", res.authoritative)
    _write_csv(out_dir / "serialcorr_companion.csv", res.companion)
    (out_dir / "serialcorr_attestation.json").write_text(json.dumps(res.attestation, indent=2))
```

(Note: `pandas.read_csv(..., comment="#")` is needed by any later consumer because of the banner line; record this in the spec/consumer docs. Tests above read with `csv.DictReader`, which treats the `#` line as a row — so either skip the first line in the test or use `pandas.read_csv(path, comment="#")`. Use `pandas.read_csv(path, comment="#")` in the test to validate the banner+data contract.)

- [ ] **Step 4: Adjust the test to read with `pandas.read_csv(path, comment="#")`; run to verify pass**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k emit_artifacts -v`
Expected: PASS.

---

## Task 8: CLI `main()`

**Files:**
- Modify: `backtest/tier6_bootstrap.py`
- Test: `tests/test_tier6_bootstrap.py`

Spec §4.7. Mirror `tier6_dsr` CLI (UTC logging, argparse, try/except → return 1). NO cost-anchor preflight.

- [ ] **Step 1: Write the failing tests**

```python
def test_cli_dry_run_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(tb, "OUT_DIR", tmp_path / "out")
    rc = tb.main(["--n-replicates", "100", "--dry-run"])
    assert rc == 0
    assert not (tmp_path / "out").exists()


def test_cli_bad_cohort_returns_1():
    rc = tb.main(["--cohort", "does_not_exist_cohort", "--n-replicates", "50"])
    assert rc == 1
```

- [ ] **Step 2: Run to verify fail**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k cli -v`
Expected: FAIL.

- [ ] **Step 3: Implement** the `_build_log_formatter`/`_configure_logging` (copy the pattern from `tier6_dsr`) + `main`:

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m backtest.tier6_bootstrap",
        description="A-1 SD-E-γ stationary-bootstrap variance overlay (diagnostic; NON-AUTHORITATIVE).",
    )
    parser.add_argument("--cohort", default=DEFAULT_COHORT)
    parser.add_argument("--n-replicates", type=int, default=DEFAULT_N_REPLICATES)
    parser.add_argument("--seed", type=int, default=BASE_SEED)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    _configure_logging()
    out_dir = Path(args.out_dir) if args.out_dir else OUT_DIR
    logger.info("tier6_bootstrap start: cohort=%s n_replicates=%d seed=%d dry_run=%s",
                args.cohort, args.n_replicates, args.seed, args.dry_run)
    try:
        res = run_cohort_bootstrap(cohort=args.cohort, n_replicates=args.n_replicates, base_seed=args.seed)
    except (ValueError, OSError, FileNotFoundError) as exc:
        logger.error("tier6_bootstrap FAILED: %s", exc)
        return 1
    if not args.dry_run:
        # sealed-artifact immutability gate (spec §7/§8.1) BEFORE writing.
        if _sealed_tier6_dsr_sha256() != res.attestation["sealed_tier6_dsr_v1_sha256"]:
            logger.error("tier6_bootstrap ABORT: sealed tier6_dsr_v1 changed mid-run")
            return 1
        emit_artifacts(res, out_dir=out_dir)
    logger.info("tier6_bootstrap done: auth=%d companion=%d max_excess=%.6f written=%s",
                len(res.authoritative), len(res.companion),
                res.attestation["max_excess"], not args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_tier6_bootstrap.py -k cli -v`
Expected: PASS.

---

## Task 9: Governance tests — tie-back + byte-immutability + identity

**Files:**
- Modify: `tests/test_tier6_bootstrap.py`

Spec §7 (tie-back regression; sealed-artifact immutability; identity). These pin the load-bearing governance guarantees.

- [ ] **Step 1: Write the failing tests**

```python
def test_tieback_deflated_z_matches_sealed():
    # numerical tie-back: recomputed sealed deflated_z_B == sealed CSV within EPS.
    import pandas as pd
    from backtest.tier6_dsr import MOMENT_RECOMPUTE_EPS
    sealed = pd.read_csv(
        tb.PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1/tier6_dsr_results.csv"
    ).set_index("hypothesis_hash")
    res = tb.run_cohort_bootstrap(n_replicates=100, base_seed=tb.BASE_SEED)
    for row in res.authoritative:
        sealed_z = float(sealed.loc[row["hypothesis_hash"], "deflated_z_B"])
        assert abs(row["deflated_z_B"] - sealed_z) <= MOMENT_RECOMPUTE_EPS


def test_sealed_artifacts_untouched_after_run(tmp_path):
    before = tb._sealed_tier6_dsr_sha256()
    res = tb.run_cohort_bootstrap(n_replicates=100, base_seed=tb.BASE_SEED)
    tb.emit_artifacts(res, out_dir=tmp_path / "out")
    after = tb._sealed_tier6_dsr_sha256()
    assert before == after  # sealed tier6_dsr_v1/ byte-identical


def test_all_excess_negative_verdict_invariant():
    res = tb.run_cohort_bootstrap(n_replicates=100, base_seed=tb.BASE_SEED)
    assert all(row["excess"] < 0 for row in res.authoritative)
    assert res.attestation["max_excess"] == pytest.approx(-0.004436, abs=1e-4)
```

- [ ] **Step 2: Run to verify pass** (these should pass against the existing implementation)

Run: `python -m pytest tests/test_tier6_bootstrap.py -k "tieback or untouched or verdict_invariant" -v`
Expected: PASS.

- [ ] **Step 3: Run the WHOLE new test file**

Run: `python -m pytest tests/test_tier6_bootstrap.py -v`
Expected: ALL PASS.

- [ ] **Step 4: Run the full suite (no regressions; sealed module/tests untouched)**

Run: `python -m pytest -q`
Expected: prior baseline + the new tier6_bootstrap tests, 0 failed. Confirm `git status` shows `backtest/tier6_dsr.py` and `tests/test_tier6_dsr.py` unmodified.

---

## Task 10: Real cohort run → emit artifacts

**Files:**
- Create (output): `data/phase2c_evaluation_gate/tier6_serialcorr_robustness_v1/*`

- [ ] **Step 1: Dry run**

Run: `python -m backtest.tier6_bootstrap --dry-run`
Expected: exit 0; log shows `auth=18 companion=21 max_excess≈-0.0044 written=False`; no dir created.

- [ ] **Step 2: Real run (default n_replicates=5000)**

Run: `python -m backtest.tier6_bootstrap`
Expected: exit 0; 3 artifacts in `data/phase2c_evaluation_gate/tier6_serialcorr_robustness_v1/`.

- [ ] **Step 3: Eyeball the result**

Run: `python -c "import json; d=json.load(open('data/phase2c_evaluation_gate/tier6_serialcorr_robustness_v1/serialcorr_attestation.json')); print(d['verdict_invariant'], d['max_excess'], d['inflation_ratio_summary'])"`
Expected: `True`, a negative `max_excess`, and per-block median inflation ratios (the empirical §6.1 measurement — expect `≈1` at L1, rising with L if serial correlation is present).

- [ ] **Step 4: Confirm sealed artifacts still byte-identical**

Run: `git status --short data/phase2c_evaluation_gate/tier6_dsr_v1/ backtest/tier6_dsr.py`
Expected: empty (nothing modified).

- [ ] **Step 5: Chunk 3 commit** (Charlie-authorized) — module + emitters + CLI + tests + result artifacts

```bash
git add backtest/tier6_bootstrap.py tests/test_tier6_bootstrap.py data/phase2c_evaluation_gate/tier6_serialcorr_robustness_v1/
git commit -m "feat(tier6-bootstrap): A-1 emitters + CLI + governance tests + real cohort run (verdict invariant, inflation measured)"
```

---

## Self-Review (done by plan author)

**Spec coverage:** §3.1 quantities → Tasks 3–5; §3.2 bootstrap + finite-T contract → Tasks 2–3; §3.3 block grid → Task 1 + used throughout; §3.4 determinism → Task 4; §3.5 replicates + stability → Task 3 (stability test added below); §4 architecture units → Tasks 1–8; §5 inputs/gates → Task 6 (`load_candidate_moments` + finite filter); §6 artifacts → Task 7; §7 tests (tie-back, immutability, NaN, degenerate, L1-equiv, identity) → Tasks 3,5,9 + stability note; §8 governance → Tasks 6,9; §8.3 L1 decomposition → Task 5.

**Gap found + fixed:** the spec §7 "replicate-doubling stability at L=96" test was not an explicit task step. **Add to Task 3 Step 1:**
```python
def test_boot_se_stability_doubling_replicates():
    # at the largest L (highest-variance SE); 8k vs 16k for headroom under tol
    # (PFR MEDIUM-1: 4k-vs-8k had only ~2x margin on the deployed seeds).
    r = _ar1(2500, 0.4, seed=8)
    se_a = tb.bootstrap_sharpe_se(r, 96, 8000, np.random.default_rng(1))
    se_b = tb.bootstrap_sharpe_se(r, 96, 16000, np.random.default_rng(2))
    assert abs(se_a / se_b - 1.0) < 0.05
```
And a spec §7 "L=1 ≈ plain i.i.d. bootstrap" explicit equivalence test — **add to Task 3:**
```python
def test_boot_se_L1_matches_plain_iid_bootstrap():
    r = _ar1(2000, 0.0, seed=6)  # phi=0 -> i.i.d.
    rng = np.random.default_rng(20)
    # plain i.i.d. bootstrap SE of the Sharpe
    B, T = 4000, len(r)
    sr_b = []
    for _ in range(B):
        s = r[rng.integers(0, T, T)]
        sr_b.append(s.mean() / s.std(ddof=0))
    plain = float(np.std(sr_b, ddof=1))
    boot = tb.bootstrap_sharpe_se(r, 1, B, np.random.default_rng(21))
    assert abs(boot / plain - 1.0) < 0.10
```

**Placeholder scan:** the Task 5 implementation has a deliberately-flagged cleanup (`g4_high_flag` line — drop the spurious clause to `bool(cm.gamma4 >= 50.0)`); the degenerate-test moment values must be verified to actually trip `mertens_variance` while writing (noted inline). No other placeholders.

**Type consistency:** `CohortBootstrapResult(authoritative, companion, attestation)` used consistently (Tasks 6–9); `evaluate_candidate_bootstrap` record keys (`se_boot_L{L}`, `inflation_L{L}`, `serialcorr_increment_L{L}`, `robust_se_z_context_L24`, `excess`, `deflated_z_B`, `mertens_degenerate_flag`) match `_RESULT_FIELDS` (Task 7) and the tests (Tasks 5–9). `substream_rng(hash, block_len)` signature consistent (Tasks 4–5).

---

## PFR Patch Log (B2 plan review — advisor + Codex, 2026-05-30)
Both legs convergent; all load-bearing claims verified before patching (degenerate term arithmetic, sealed import names, `max_excess −0.004436450`, leading-NaN, microbenchmarks). Dispositions (all in-place above):

| # | Finding (leg) | Severity | Disposition |
|---|---|---|---|
| C-1 | `evaluate_candidate_bootstrap` called sealed `evaluate_candidate(cm)` before the degenerate guard → it raises on a non-positive Mertens term → degenerate path unreachable (Codex CRITICAL) | CRITICAL | **PATCHED** — degenerate-safe restructure: compute `sr_star_B`/`excess` via moment-independent `sr_star()`, wrap `mertens_se`+`deflated_z` (NaN+flag on raise); `evaluate_candidate` import dropped |
| H-1 | degenerate-test fixture `(0.9,0.0,1.0)` gives term `+1.0` → vacuous green no-op (both legs) | HIGH | **PATCHED** — `(1.0,2.0,3.0)` (term −0.5, verified raises); unconditional asserts |
| H-2 | `base_seed`/`--seed` not threaded into `substream_rng` → CLI flag is a no-op (Codex) | HIGH | **PATCHED** — `substream_rng(hash, L, base_seed)`; threaded CLI→cohort→candidate→substream; test added |
| H-3 | `_read_cohort_csv` missing from import scaffold → `NameError` (Codex) | HIGH | **PATCHED** — added `_read_cohort_csv`, `deflated_z`, `sr_star` to imports |
| H-4 | `g4_high_flag` ships buggy `base.get(...) and ...` clause (both) | HIGH | **PATCHED** — `bool(cm.gamma4 >= 50.0)` (matches sealed `annotate_flags`) |
| M-1 | attestation schema incomplete vs spec §6 (Codex) | MEDIUM | **PATCHED** — full `{min,median,max,by_block_len}` + `serialcorr_increment_summary` + `generated_at_utc` + `source_commit` |
| M-2 | `evaluate_candidate_bootstrap` lacked its own `len==cm.T`/finite guard (Codex) | MEDIUM | **PATCHED** — entry guard added |
| M-3 | L96 stability tol had only ~2× margin on deployed seeds (advisor) | MEDIUM | **PATCHED** — 8k-vs-16k (more headroom) |
| M-4 | vectorized resampler ≠ same-RNG-stream as scalar reference (Codex) | MEDIUM | **PATCHED** — documented distribution-equivalence; L1 test validates |
| L-1 | `B < 2` → `std(ddof=1)` NaN (Codex) | LOW | **PATCHED** — `B >= 2` guard |
| L-2 | emit test used `csv.DictReader` over a bannered CSV (both) | LOW | **PATCHED** — `pd.read_csv(comment="#")` |
| L-3 | `emit_artifacts` def-time `out_dir=OUT_DIR` binding gotcha (advisor) | LOW | **PATCHED** — `out_dir=None` → runtime resolve |
| L-4 | `n_skip` raise-only tripwire, not surfaced (advisor MEDIUM-2) | LOW | **ACCEPTED** — documented as intentional (==0 at T~2500); no machinery |

Performance (Codex microbench): ~0.3 s per `(B=5000, T=2500)` cell → full run ~minutes; CI tests stay <30 s. Memory ~100 MB transient per cell (acceptable, sequential).

## Execution Handoff
Plan complete and PFR-patched. After Charlie's foundation-commit authorization (spec + this plan), execute via **subagent-driven-development** (fresh subagent per task, two-stage review per chunk — matching the Tier 6 cycle's TDD-subagent cadence), then a final whole-module B2 review + Rule-2 SEAL-eve before the A-1 SEAL.
