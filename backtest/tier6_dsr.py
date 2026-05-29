"""Tier 6 Deflated Sharpe Ratio evaluation application (post-R6.1-V_SEAL).

Applies the R6.1-locked BLdP-2014 closed-form DSR methodology + §12 Errata (a1)
to the B-C-narrow-recovered phase4_forward_2026_15bps_v1 cohort. See design spec
docs/superpowers/specs/2026-05-29-tier6-dsr-evaluation-application-design.md.

NOT the heuristic screen in evaluate_dsr.py (sqrt(2 ln N)); that module is
untouched. This is the production closed-form DSR per CLAUDE.md HARD CONSTRAINT
"DSR-family preferred" for the Tier 6 promotion class.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOLDOUT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1"

ALPHA = 0.05
N_STAR = 18
EULER_GAMMA = 0.5772156649015329
ANNUALIZATION_BARS_PER_YEAR = 8760  # hourly bars/year; cross-check only

# R5.1 §188 R2.1-EXCLUDED identifiers (pre-registered; not Monday-named).
R21_EXCLUDED = frozenset({"35dcfcfbee4cfafc", "38a1bb228f103c26"})


def is_monday_pattern(name: str) -> bool:
    """Name-substring Monday-pattern predicate (DSL content unavailable).

    Args:
        name: Candidate strategy name.

    Returns:
        True if the lowercased name contains the substring ``monday``.
    """
    return "monday" in str(name).lower()


def derive_cohort(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Partition cohort_a into (locked-18, companion-21).

    locked-18 = 39 - 19 Monday-pattern (name ~ /monday/i) - 2 R2.1-EXCLUDED.

    Args:
        df: The holdout_results.csv DataFrame (39 rows; cols include
            ``hypothesis_hash``, ``name``, ``theme``).

    Returns:
        ``(locked, companion)`` lists of ``hypothesis_hash`` strings.

    Raises:
        ValueError: If the partition is not exactly 18/21 (drift in the
            Monday predicate or R21_EXCLUDED set).
    """
    monday = df["name"].map(is_monday_pattern)
    r21 = df["hypothesis_hash"].isin(R21_EXCLUDED)
    locked = df.loc[~monday & ~r21, "hypothesis_hash"].tolist()
    companion = df.loc[monday | r21, "hypothesis_hash"].tolist()
    if len(locked) != 18 or len(companion) != 21:
        raise ValueError(
            f"cohort partition drift: locked={len(locked)} companion={len(companion)} "
            f"(expected 18/21); check Monday predicate + R21_EXCLUDED"
        )
    return locked, companion


# --------------------------------------------------------------------------
# Task 2: per-candidate moment loader + consume-and-verify
# --------------------------------------------------------------------------
MOMENT_RECOMPUTE_EPS = 1e-6


@dataclass(frozen=True)
class CandidateMoments:
    """Per-candidate moments consumed from holdout artifacts.

    ``gamma4`` is RAW kurtosis (3.0 = Gaussian), matching the engine-stored
    convention and the Mertens ``(gamma4-1)/4`` term. ``sr_per_bar`` is the
    per-bar Sharpe ``mean(r)/std(r, ddof=0)`` over the finite return series.
    ``T`` is the count of finite per-bar returns (total bars, incl. zeros).
    """

    hypothesis_hash: str
    name: str
    theme: str
    sr_per_bar: float
    gamma3: float
    gamma4: float  # RAW kurtosis (3 = Gaussian)
    T: int
    trades: int | None


def _sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file's bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_candidate_moments(hypothesis_hash: str, df: pd.DataFrame) -> CandidateMoments:
    """Load per-candidate moments with consume-and-verify integrity gates.

    Pipeline:
    1. A8 artifact-integrity gate: verify the CSV-stored
       ``returns_per_bar_sha256`` against the on-disk parquet's actual
       SHA-256 BEFORE any recompute. Raises on mismatch.
    2. Independently recompute ``T``, ``gamma3`` (population skew,
       ``bias=True``), ``gamma4`` (RAW kurtosis, ``fisher=False, bias=True``)
       and ``SR_per_bar`` (``mean/std(ddof=0)``) from the parquet ``return``
       column over its finite entries.
    3. Consume the stored ``T_obs/gamma3/gamma4`` and verify each against the
       recompute (raise on >EPS mismatch; T_obs is exact-integer).

    Args:
        hypothesis_hash: Candidate identifier (row key in ``df``).
        df: The holdout_results.csv DataFrame.

    Returns:
        A frozen :class:`CandidateMoments`.

    Raises:
        ValueError: On sha256 integrity mismatch, or stored-vs-recompute
            moment mismatch beyond ``MOMENT_RECOMPUTE_EPS``.
    """
    row = df.loc[df["hypothesis_hash"] == hypothesis_hash].iloc[0]
    pq = HOLDOUT_DIR / hypothesis_hash / "returns_per_bar.parquet"

    # A8: artifact-integrity gate BEFORE recompute.
    stored_sha = str(row["returns_per_bar_sha256"])
    actual_sha = _sha256_file(pq)
    if stored_sha != actual_sha:
        raise ValueError(
            f"sha256 integrity mismatch for {hypothesis_hash}: "
            f"stored={stored_sha} on_disk={actual_sha} (path={pq})"
        )

    r = pd.read_parquet(pq)["return"]
    rf = r[np.isfinite(r)]
    T = int(len(rf))
    g3 = float(skew(rf, bias=True))
    g4 = float(kurtosis(rf, fisher=False, bias=True))  # RAW (3 = Gaussian)
    sr = float(rf.mean() / rf.std(ddof=0))

    for label, stored, recomputed in (
        ("T_obs", int(row["T_obs"]), T),
        ("gamma3", float(row["gamma3"]), g3),
        ("gamma4", float(row["gamma4"]), g4),
    ):
        tol = 0 if label == "T_obs" else MOMENT_RECOMPUTE_EPS
        if abs(stored - recomputed) > tol:
            raise ValueError(
                f"moment mismatch for {hypothesis_hash} {label}: "
                f"stored={stored} recomputed={recomputed}"
            )

    trades = row.get("holdout_total_trades")
    trades = None if pd.isna(trades) else int(trades)
    return CandidateMoments(
        hypothesis_hash, str(row["name"]), str(row["theme"]),
        sr, g3, g4, T, trades,
    )
