# backtest/tier6_bootstrap.py
"""A-1: SD-E-γ stationary-bootstrap variance overlay for the closed-form Tier 6
Deflated Sharpe Ratio.

PATH-2 RE-SCOPE (Erratum E1, AUTHORITATIVE — see spec §12): the cohort's per-bar
return series are SPARSE (zero-fraction 0.70-0.98; low-trade-frequency
strategies), so the §6.1 within-candidate serial-correlation gap is NOT reliably
*measurable* (the per-bar-Sharpe bootstrap is partly ill-posed; long-block
resamples are frequently all-zero/degenerate). A-1 is therefore re-scoped to:
(a) the standing stationary-bootstrap primitive (for future *denser* cohorts),
(b) a verdict-invariance attestation (all SR̂ < SR* → 0/18, SE-independent), and
(c) an evidence-grounded SUITABILITY diagnostic that *demonstrates* (not asserts)
the bootstrap is unsuitable here — per-candidate sparsity + a degeneracy probe
(skip_fraction by block length). DIAGNOSTIC ONLY; NON-AUTHORITATIVE; no parallel
pass/fail track; NO inflation_ratio / serialcorr_increment deliverable.

See design spec
docs/superpowers/specs/2026-05-30-a1-sd-e-gamma-stationary-bootstrap-overlay-design.md.
"""
from __future__ import annotations

import argparse
import csv
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
    DEFAULT_COHORT,
    EVALUATION_GATE_DIR,
    HOLDOUT_DIR,
    N_STAR,
    PROJECT_ROOT,
    CandidateMoments,
    _read_cohort_csv,
    _sha256_file,
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
# The sealed authoritative Tier 6 DSR artifacts (byte-immutable; A-1 re-checks
# their sha256 before writing and never touches them — spec §7/§8.1).
SEALED_TIER6_DSR_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1"
# Per Erratum E1.4: the re-scoped banner reflects the sparse-cohort conclusion.
ARTIFACT_BANNER = (
    "diagnostic; NON-AUTHORITATIVE; measurement inconclusive on sparse cohort; "
    "verdict invariant (0/18, SE-independent)"
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


def _bootstrap_sharpe_stats(
    returns: np.ndarray,
    expected_block_len: float,
    n_replicates: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, float]:
    """Shared Politis-Romano (B,T) resampler → per-replicate Sharpe + skip frac.

    DRY core (spec §E1.5) for ``bootstrap_sharpe_se`` (strict; raises on high
    skip) and ``bootstrap_skip_fraction`` (degeneracy measurement; never raises).

    Validates the finite-filtered length-T input contract (spec §3.2; the real
    parquet has a leading-NaN bar), the ``expected_block_len >= 1`` and the
    ``n_replicates >= 2`` guards, then builds a ``(B, T)`` resample index matrix
    (T-loop, vectorized across B), gathers, and computes
    ``SR_b = mean/std(ddof=0)`` per replicate. A replicate with zero resample
    variance (``std == 0``, the degenerate case) is dropped and counted.

    The ``(B,T)`` resampler is DISTRIBUTION-equivalent to the single-resample
    :func:`stationary_bootstrap_indices`, NOT same-RNG-stream identical (it
    consumes the generator per time-step across B). The L=1 plain-bootstrap
    equivalence test validates distributional correctness.

    Args:
        returns: Finite-filtered length-T per-bar return array.
        expected_block_len: Mean block length ``L`` (``p = 1/L``); must be >= 1.
        n_replicates: Number of bootstrap replicates ``B`` (must be >= 2).
        rng: A ``numpy`` generator (determinism is the caller's responsibility).

    Returns:
        ``(sr_b_valid, skip_fraction)`` where ``sr_b_valid`` is the float64
        array of per-replicate Sharpe estimates over the non-degenerate
        replicates, and ``skip_fraction`` is ``n_skip / B`` (the fraction of
        zero-variance replicates).

    Raises:
        ValueError: On a non-finite / sub-length-2 ``returns`` array,
            ``expected_block_len < 1``, or ``n_replicates < 2``. Does NOT raise
            on a high skip fraction (that is the strict primitive's policy).
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
    sr_b = means[valid] / stds[valid]
    return sr_b, n_skip / B


def bootstrap_sharpe_se(
    returns: np.ndarray,
    expected_block_len: float,
    n_replicates: int,
    rng: np.random.Generator,
) -> float:
    """Stationary-bootstrap SE of the per-bar Sharpe estimator (strict primitive).

    ``returns`` MUST be the finite-filtered length-T array (spec §3.2; the real
    parquet has a leading-NaN bar). Delegates the (B,T) resample to
    :func:`_bootstrap_sharpe_stats`, then returns ``std({SR_b}, ddof=1)`` over
    the non-degenerate replicates. If more than 0.1% of replicates are dropped
    (zero resample variance), the input is degenerate and we RAISE. This is the
    standing capability for future *denser* cohorts; the sparse-cohort
    degeneracy *measurement* lives in :func:`bootstrap_skip_fraction`.
    """
    sr_b, skip_fraction = _bootstrap_sharpe_stats(
        returns, expected_block_len, n_replicates, rng
    )
    if skip_fraction > DEGENERATE_REPLICATE_FRACTION:
        B = int(n_replicates)
        n_skip = round(skip_fraction * B)
        raise ValueError(f"{n_skip}/{B} degenerate (zero-variance) bootstrap replicates")
    return float(sr_b.std(ddof=1))


def bootstrap_skip_fraction(
    returns: np.ndarray,
    expected_block_len: float,
    n_replicates: int,
    rng: np.random.Generator,
) -> float:
    """Degeneracy probe (spec §E1.5): the fraction of zero-variance replicates.

    Same Politis-Romano resampler as :func:`bootstrap_sharpe_se` (via the shared
    :func:`_bootstrap_sharpe_stats`), but returns the ``skip_fraction`` directly
    and does **NOT** raise on a high skip — it IS the degeneracy *measurement*
    that demonstrates (per Erratum E1) that the per-bar-Sharpe bootstrap is
    ill-posed on this sparse, low-trade-frequency cohort. The finite-input /
    length / ``L >= 1`` / ``B >= 2`` guards are retained (inherited from the
    shared core).

    Returns:
        ``n_skip / n_replicates`` in ``[0.0, 1.0]``.
    """
    _, skip_fraction = _bootstrap_sharpe_stats(
        returns, expected_block_len, n_replicates, rng
    )
    return skip_fraction


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


# ==========================================================================
# Path-2 (Erratum E1) — suitability diagnostic: sparsity + degeneracy probe
# ==========================================================================
# Re-scoped per-candidate record columns (spec §E1.4) — NO inflation_* /
# serialcorr_increment_* / pass_* columns. ``skip_L{L}`` for each grid L.
# NOTE: deflated_z_B is carried in the per-candidate RECORD dict (for the tie-back
# cross-check) but is deliberately NOT in this on-disk CSV schema — `excess` already
# conveys the verdict (excess < 0), and a z-stat column in a NON-AUTHORITATIVE
# diagnostic could misread as a gate. extrasaction="ignore" drops it (+ the internal
# deflated_z_degenerate flag) from the CSV.
_SUITABILITY_FIELDS: list[str] = [
    "hypothesis_hash", "name", "theme", "T", "nonzero_count", "zero_fraction",
    "sr_per_bar", "sr_star_B", "excess",
] + [f"skip_L{L}" for L in BLOCK_LEN_GRID]


@dataclass(frozen=True)
class CohortSuitabilityResult:
    """Path-2 suitability-diagnostic result for the locked-18 + companion-21 cohort.

    ``authoritative`` / ``companion`` are lists of per-candidate suitability
    record dicts (schema = ``_SUITABILITY_FIELDS`` plus a possible
    ``deflated_z_degenerate`` flag). ``attestation`` is the §E1.4 cohort-level
    attestation dict (verdict-invariance + sparsity/degeneracy summaries +
    sealed-artifact sha256 + provenance). All fields are diagnostic and
    NON-AUTHORITATIVE; there is no parallel pass/fail track.
    """

    authoritative: list[dict]
    companion: list[dict]
    attestation: dict


def _load_finite_returns(hypothesis_hash: str, holdout_dir: Path = HOLDOUT_DIR) -> np.ndarray:
    """Load the finite-filtered length-T per-bar ``return`` array for a candidate.

    Mirrors the sealed ``load_candidate_moments`` consumption convention
    (``rf = r[np.isfinite(r)]``); the real parquet carries a leading-NaN first
    bar (``raw_len = T + 1``), so the finite filter yields the length-``T`` array
    the bootstrap input contract (spec §3.2) requires.

    Args:
        hypothesis_hash: Candidate identifier (``<hash>/`` subdir).
        holdout_dir: Cohort directory holding ``<hash>/returns_per_bar.parquet``
            (default ``HOLDOUT_DIR``; a non-default ``--cohort`` flows here).

    Returns:
        A float64 1-D array of the finite per-bar returns (length ``T``).
    """
    pq = holdout_dir / hypothesis_hash / "returns_per_bar.parquet"
    r = pd.read_parquet(pq)["return"].to_numpy()
    return np.asarray(r[np.isfinite(r)], dtype=np.float64)


def _sealed_tier6_dsr_sha256() -> dict[str, str]:
    """Return ``{filename: sha256}`` over every file under the sealed tier6_dsr_v1 dir.

    Used to (a) record the sealed-artifact fingerprint in the attestation and
    (b) re-check byte-immutability before A-1 writes (spec §7/§8.1). A-1 never
    writes under this directory; it only reads to fingerprint.

    Returns:
        A dict keyed by file basename → hex sha256, deterministically ordered
        by filename.
    """
    files = sorted(p for p in SEALED_TIER6_DSR_DIR.iterdir() if p.is_file())
    return {p.name: _sha256_file(p) for p in files}


def _git_source_commit() -> str:
    """Return the current ``git rev-parse HEAD`` (or ``"unknown"`` if unavailable)."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def evaluate_candidate_suitability(
    cm: CandidateMoments,
    returns: np.ndarray,
    *,
    block_grid: tuple[int, ...] = BLOCK_LEN_GRID,
    n_replicates: int,
    base_seed: int,
) -> dict:
    """Build one candidate's Path-2 suitability record (sparsity + degeneracy probe).

    Records (spec §E1.3/§E1.4):

    - identity: ``hypothesis_hash``, ``name``, ``theme``, ``T``;
    - sparsity: ``nonzero_count`` (count of nonzero finite returns),
      ``zero_fraction`` (= ``1 - nonzero_count/T``);
    - invariance numerics: ``sr_per_bar``, ``sr_star_B`` (= ``sr_star(N*, T,
      "B")``), ``excess`` (= ``sr_per_bar - sr_star_B``; moment-independent of
      the bootstrap), ``deflated_z_B`` (for the sealed tie-back cross-check;
      wrapped so a Mertens-degenerate term yields ``NaN`` + a flag rather than
      crashing);
    - degeneracy probe: ``skip_L{L}`` for each ``L`` in ``block_grid`` (via
      :func:`bootstrap_skip_fraction` on an order-independent
      ``substream_rng(hash, L, base_seed)`` stream; does NOT raise on high skip).

    NO ``inflation_*`` / ``serialcorr_increment_*`` / ``pass_*`` columns (the
    measurement deliverable is superseded by Erratum E1).

    Args:
        cm: The candidate's moments (must satisfy ``len(returns) == cm.T`` and
            all-finite ``returns``).
        returns: The finite-filtered length-T per-bar return array.
        block_grid: Block lengths for the degeneracy probe (default
            ``BLOCK_LEN_GRID``).
        n_replicates: Bootstrap replicate count for the probe.
        base_seed: Base seed for the per-cell ``substream_rng``.

    Returns:
        A suitability record dict containing every ``_SUITABILITY_FIELDS`` key
        plus a ``deflated_z_degenerate`` boolean flag.

    Raises:
        ValueError: If ``len(returns) != cm.T`` or ``returns`` is not all-finite
            (the bootstrap input contract; spec §3.2).
    """
    r = np.asarray(returns, dtype=np.float64)
    if r.shape[0] != cm.T:
        raise ValueError(
            f"returns length {r.shape[0]} != cm.T {cm.T} for {cm.hypothesis_hash}"
        )
    if not np.all(np.isfinite(r)):
        raise ValueError(
            f"non-finite returns for {cm.hypothesis_hash}: pass the finite-filtered array"
        )

    nonzero_count = int(np.count_nonzero(r))
    zero_fraction = float(1.0 - nonzero_count / cm.T)
    sr_star_b = sr_star(N_STAR, cm.T, "B")
    excess = float(cm.sr_per_bar - sr_star_b)

    # deflated_z_B for the sealed tie-back; degenerate-Mertens -> NaN + flag.
    try:
        dz_b = float(deflated_z(cm.sr_per_bar, sr_star_b, cm.gamma3, cm.gamma4, cm.T))
        dz_degenerate = False
    except ValueError:
        dz_b = float("nan")
        dz_degenerate = True

    rec: dict = {
        "hypothesis_hash": cm.hypothesis_hash,
        "name": cm.name,
        "theme": cm.theme,
        "T": cm.T,
        "nonzero_count": nonzero_count,
        "zero_fraction": zero_fraction,
        "sr_per_bar": float(cm.sr_per_bar),
        "sr_star_B": float(sr_star_b),
        "excess": excess,
        "deflated_z_B": dz_b,
        "deflated_z_degenerate": dz_degenerate,
    }
    for L in block_grid:
        rng = substream_rng(cm.hypothesis_hash, L, base_seed)
        rec[f"skip_L{L}"] = float(
            bootstrap_skip_fraction(r, L, n_replicates, rng)
        )
    return rec


def _summarize(values: list[float]) -> dict:
    """Return ``{min, median, max}`` over a non-empty list of floats."""
    if not values:
        raise ValueError("_summarize requires a non-empty list")
    arr = np.asarray(values, dtype=np.float64)
    return {
        "min": float(np.min(arr)),
        "median": float(np.median(arr)),
        "max": float(np.max(arr)),
    }


def _build_attestation(
    cohort: str,
    authoritative: list[dict],
    companion: list[dict],
    *,
    n_replicates: int,
    base_seed: int,
) -> dict:
    """Build the §E1.4 cohort-level suitability attestation dict.

    The verdict-invariance is established over the AUTHORITATIVE locked-18 only
    (``all_excess_negative`` / ``max_excess`` / ``verdict_invariant``), matching
    the sealed 0/18 gate. The sparsity + degeneracy summaries span the FULL
    cohort (authoritative + companion) — the methodologically honest "bootstrap
    is unreliable here" evidence (the sparsest, most-degenerate candidate sits
    in the companion partition on this cohort).

    Args:
        cohort: The cohort directory name.
        authoritative: The locked-18 suitability records.
        companion: The companion-21 suitability records.
        n_replicates: Bootstrap replicate count used for the probe.
        base_seed: Base seed used for the per-cell substreams.

    Returns:
        The attestation dict (spec §E1.4 schema; conclusion
        ``"measurement_inconclusive_sparse_cohort"``).
    """
    excesses = [r["excess"] for r in authoritative]
    all_rows = [*authoritative, *companion]
    max_excess = float(max(excesses))
    sparsity_summary = {
        "zero_fraction": _summarize([r["zero_fraction"] for r in all_rows]),
        "nonzero_count": _summarize([float(r["nonzero_count"]) for r in all_rows]),
    }
    degeneracy_summary = {
        f"skip_L{L}": _summarize([r[f"skip_L{L}"] for r in all_rows])
        for L in BLOCK_LEN_GRID
    }
    return {
        "cohort": cohort,
        "base_seed": int(base_seed),
        "n_replicates": int(n_replicates),
        "block_len_grid": list(BLOCK_LEN_GRID),
        "n_authoritative": len(authoritative),
        "n_companion": len(companion),
        # verdict_invariant (the conclusion: 0/18 is SE-independent) follows
        # directly from all_excess_negative (the evidence: every excess < 0, so no
        # SE>0 can flip a negative numerator to a pass). Both surfaced — evidence +
        # derived claim — equal by construction on this cohort.
        "all_excess_negative": bool(all(e < 0 for e in excesses)),
        "max_excess": max_excess,
        "verdict_invariant": bool(all(e < 0 for e in excesses)),
        "sparsity_summary": sparsity_summary,
        "degeneracy_summary": degeneracy_summary,
        "conclusion": "measurement_inconclusive_sparse_cohort",
        "banner": ARTIFACT_BANNER,
        "sealed_tier6_dsr_v1_sha256": _sealed_tier6_dsr_sha256(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": _git_source_commit(),
    }


def run_cohort_suitability(
    cohort: str = DEFAULT_COHORT,
    *,
    n_replicates: int = DEFAULT_N_REPLICATES,
    base_seed: int = BASE_SEED,
) -> CohortSuitabilityResult:
    """Run the Path-2 suitability diagnostic over the locked-18 + companion-21 cohort.

    Reads the cohort ``holdout_results.csv``, derives the 18/21 partition via
    :func:`derive_cohort`, and for each candidate: loads its moments through the
    sealed sha256 + ``single_run_holdout_v1`` lineage integrity gates
    (:func:`load_candidate_moments`), loads the finite-filtered length-T return
    array (:func:`_load_finite_returns`), and builds a suitability record
    (:func:`evaluate_candidate_suitability`). Assembles the §E1.4 attestation,
    fingerprinting the sealed Tier 6 DSR artifacts (which it never modifies).

    Args:
        cohort: Cohort directory name under ``data/phase2c_evaluation_gate/``.
        n_replicates: Bootstrap replicate count for the degeneracy probe.
        base_seed: Base seed for the per-cell substreams.

    Returns:
        A :class:`CohortSuitabilityResult`.

    Raises:
        ValueError: Propagated from ``derive_cohort`` (partition drift) or from
            ``load_candidate_moments`` (data-integrity failures), or if the
            cohort directory / CSV is absent (surfaces as ``OSError`` →
            wrapped by the CLI).
    """
    holdout_dir = EVALUATION_GATE_DIR / cohort
    df = _read_cohort_csv(holdout_dir=holdout_dir)
    locked, companion = derive_cohort(df)

    def _records(hashes: list[str]) -> list[dict]:
        out: list[dict] = []
        for h in hashes:
            cm = load_candidate_moments(h, df, holdout_dir=holdout_dir)
            returns = _load_finite_returns(h, holdout_dir)
            out.append(
                evaluate_candidate_suitability(
                    cm, returns, n_replicates=n_replicates, base_seed=base_seed
                )
            )
        return out

    authoritative = _records(locked)
    companion_rows = _records(companion)
    attestation = _build_attestation(
        cohort, authoritative, companion_rows,
        n_replicates=n_replicates, base_seed=base_seed,
    )
    return CohortSuitabilityResult(authoritative, companion_rows, attestation)


# --------------------------------------------------------------------------
# Emitters (spec §E1.4)
# --------------------------------------------------------------------------
def _write_csv(path: Path, rows: list[dict]) -> None:
    """Write ``rows`` to ``path`` as CSV with a leading ``# <banner>`` line.

    Emits the ``ARTIFACT_BANNER`` as a leading comment line (so a reader sees
    the NON-AUTHORITATIVE / inconclusive disclosure first and pandas can skip it
    with ``comment="#"``), then the ``_SUITABILITY_FIELDS`` header + rows.
    ``extrasaction="ignore"`` drops the row-only ``deflated_z_degenerate`` flag
    from the persisted schema (it is internal; the spec §E1.4 column set is
    exactly ``_SUITABILITY_FIELDS``).

    Args:
        path: Output CSV path.
        rows: Suitability record dicts.
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(f"# {ARTIFACT_BANNER}\n")
        w = csv.DictWriter(
            f, fieldnames=_SUITABILITY_FIELDS, extrasaction="ignore", restval=""
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)


def emit_artifacts(res: CohortSuitabilityResult, out_dir: Path | None = None) -> dict[str, Path]:
    """Write the 3 Path-2 suitability artifacts (spec §E1.4) to ``out_dir``.

    - ``suitability_diagnostic.csv`` (18 authoritative rows),
    - ``suitability_companion.csv`` (21 companion rows; NON-AUTHORITATIVE),
    - ``suitability_attestation.json`` (banner + §E1.4 attestation).

    Both CSVs carry the leading ``# <banner>`` comment line; the JSON carries
    the banner as a top-level field. NO ``inflation_*`` / ``serialcorr_*`` /
    ``pass_*`` columns.

    Args:
        res: The cohort suitability result.
        out_dir: Output directory (default ``OUT_DIR`` when None).

    Returns:
        A dict mapping artifact name → written ``Path``.
    """
    out = OUT_DIR if out_dir is None else Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    diag = out / "suitability_diagnostic.csv"
    comp = out / "suitability_companion.csv"
    att = out / "suitability_attestation.json"
    _write_csv(diag, res.authoritative)
    _write_csv(comp, res.companion)
    att.write_text(json.dumps(res.attestation, indent=2))
    return {"diagnostic": diag, "companion": comp, "attestation": att}


# --------------------------------------------------------------------------
# CLI + UTC logging (mirrors backtest/tier6_dsr.py)
# --------------------------------------------------------------------------
def _build_log_formatter() -> logging.Formatter:
    """Return a logging formatter that emits UTC ISO-8601 timestamps.

    Sets ``converter = time.gmtime`` so ``%(asctime)s`` renders in UTC with an
    explicit trailing ``Z``. Mirrors ``backtest/tier6_dsr.py``.
    """
    fmt = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03dZ %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    fmt.converter = time.gmtime
    return fmt


def _configure_logging() -> None:
    """Attach a UTC stdout stream handler to the module logger (idempotent)."""
    if logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_build_log_formatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the Path-2 suitability diagnostic.

    Runs :func:`run_cohort_suitability` on ``--cohort`` and emits the 3 §E1.4
    artifacts (unless ``--dry-run``). Before writing, re-checks the sealed
    ``tier6_dsr_v1/`` sha256 against the fingerprint captured in the attestation
    and ABORTS (exit 1) if anything changed mid-run. NO cost-anchor preflight
    (A-1 makes no promotion decision; the lineage + sha256 integrity gates in
    ``load_candidate_moments`` are the relevant consumption discipline).

    Args:
        argv: Optional argument vector (defaults to ``sys.argv[1:]``).

    Returns:
        ``0`` on success, ``1`` on any validation/integrity/immutability failure
        (surfaced as a clear log line, not a raw traceback).
    """
    parser = argparse.ArgumentParser(
        prog="python -m backtest.tier6_bootstrap",
        description=(
            "A-1 Path-2 (Erratum E1) suitability diagnostic: sparsity + "
            "degeneracy probe over the Tier 6 cohort. DIAGNOSTIC ONLY; "
            "NON-AUTHORITATIVE; verdict invariant (0/18, SE-independent)."
        ),
    )
    parser.add_argument(
        "--cohort", default=DEFAULT_COHORT,
        help=(
            "Cohort directory name under data/phase2c_evaluation_gate/ "
            f"(default: {DEFAULT_COHORT})."
        ),
    )
    parser.add_argument(
        "--n-replicates", type=int, default=DEFAULT_N_REPLICATES,
        help=f"Bootstrap replicates for the degeneracy probe (default: {DEFAULT_N_REPLICATES}).",
    )
    parser.add_argument(
        "--seed", type=int, default=BASE_SEED,
        help=f"Base seed for the per-cell substreams (default: {BASE_SEED}).",
    )
    parser.add_argument(
        "--out-dir", default=None,
        help=(
            "Output directory for the 3 artifacts (default: "
            "data/phase2c_evaluation_gate/tier6_serialcorr_robustness_v1). "
            "Ignored under --dry-run."
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Compute the cohort suitability but write NO artifacts.",
    )
    args = parser.parse_args(argv)

    _configure_logging()

    out_dir = Path(args.out_dir) if args.out_dir is not None else OUT_DIR
    write = not args.dry_run

    logger.info(
        "tier6_bootstrap (A-1 Path-2 suitability) start: cohort=%s "
        "n_replicates=%d seed=%d out_dir=%s dry_run=%s",
        args.cohort, args.n_replicates, args.seed, out_dir, args.dry_run,
    )

    # Capture sealed-artifact fingerprint BEFORE the run — only when we will write
    # (the immutability gate guards the write; dry-run touches nothing). Spec §7/§8.1.
    sealed_before = None
    if write:
        try:
            sealed_before = _sealed_tier6_dsr_sha256()
        except OSError as exc:
            logger.error("tier6_bootstrap FAILED (cannot fingerprint sealed artifacts): %s", exc)
            return 1

    try:
        result = run_cohort_suitability(
            cohort=args.cohort,
            n_replicates=args.n_replicates,
            base_seed=args.seed,
        )
    except (ValueError, OSError) as exc:
        logger.error("tier6_bootstrap FAILED (validation/lineage/integrity): %s", exc)
        return 1

    # Re-check the sealed artifacts are byte-immutable before writing.
    if write and _sealed_tier6_dsr_sha256() != sealed_before:
        logger.error(
            "tier6_bootstrap ABORT: sealed tier6_dsr_v1/ artifacts changed during "
            "the run (sha256 mismatch) — refusing to write A-1 artifacts."
        )
        return 1

    att = result.attestation
    logger.info(
        "tier6_bootstrap done: authoritative=%d companion=%d all_excess_negative=%s "
        "max_excess=%.6f verdict_invariant=%s conclusion=%s",
        len(result.authoritative), len(result.companion),
        att["all_excess_negative"], att["max_excess"],
        att["verdict_invariant"], att["conclusion"],
    )

    if write:
        paths = emit_artifacts(result, out_dir=out_dir)
        logger.info(
            "tier6_bootstrap wrote: %s",
            ", ".join(str(p) for p in paths.values()),
        )
    else:
        logger.info("tier6_bootstrap dry-run: no artifacts written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
