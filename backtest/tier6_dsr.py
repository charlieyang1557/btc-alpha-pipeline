"""Tier 6 Deflated Sharpe Ratio evaluation application (post-R6.1-V_SEAL).

Applies the R6.1-locked BLdP-2014 closed-form DSR methodology + §12 Errata (a1)
to the B-C-narrow-recovered phase4_forward_2026_15bps_v1 cohort. See design spec
docs/superpowers/specs/2026-05-29-tier6-dsr-evaluation-application-design.md.

NOT the heuristic screen in evaluate_dsr.py (sqrt(2 ln N)); that module is
untouched. This is the production closed-form DSR per CLAUDE.md HARD CONSTRAINT
"DSR-family preferred" for the Tier 6 promotion class.
"""
from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

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
