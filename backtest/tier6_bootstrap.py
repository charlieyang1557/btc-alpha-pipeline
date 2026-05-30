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
    # Draw only the T-1 transitions actually consumed (no wasted position-0 draw).
    u = rng.random(T - 1)
    fresh = rng.integers(0, T, size=T - 1)
    for i in range(1, T):
        idx[i] = fresh[i - 1] if u[i - 1] < p else (idx[i - 1] + 1) % T
    return idx


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


def mertens_se(sr: float, gamma3: float, gamma4: float, T: int) -> float:
    """i.i.d. baseline SE of the Sharpe estimator = sqrt(mertens_variance(...)).

    Args:
        sr: Per-bar Sharpe estimate.
        gamma3: Population skew of per-bar returns.
        gamma4: RAW kurtosis (3 = Gaussian).
        T: Count of finite per-bar returns (must be >= 2).

    Returns:
        sqrt(Mertens 2002 asymptotic variance of the Sharpe estimator); positive.

    Raises:
        ValueError: Propagated from ``mertens_variance`` (T <= 1, non-finite sr,
            or asymptotic-breakdown numerator term <= 0).
    """
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
