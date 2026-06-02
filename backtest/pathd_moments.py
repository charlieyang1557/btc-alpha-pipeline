# backtest/pathd_moments.py
"""Path D moments: assemble the cohort CSV from producer rows, then load each
CandidateMoments through the EXISTING tier6 integrity gate (Decision 3).

Adapted near-verbatim from backtest/pathc_moments.py; retargeted to the Path D
OI cohort namespace. We do NOT recompute moments here —
load_candidate_moments performs the sha256 verification + the independent
gamma3/gamma4/T recompute, so Path D's OI moments meet exactly the same
integrity bar as the dead-18 cohort they are DSR-compared against. Path D owns
its OWN namespace; this never reads the sealed cohort.

Degenerate-equity handling (inherited from Path C commit 0d06c22d): a 0-trade /
flat-equity leg produces gamma3/gamma4=None in the row; such rows are excluded
from the CSV (a flat series has no testable return distribution and cannot enter
the DSR cohort). The caller (``run_pathd_verdict``) records excluded candidates
in ``degenerate_legs`` so they are never silently dropped from the evidence bundle.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from backtest.tier6_dsr import CandidateMoments, load_candidate_moments


def build_cohort_csv(rows: list[dict], cohort_dir: Path) -> pd.DataFrame:
    """Assemble + persist the Path D holdout_results.csv from producer rows.

    Degenerate rows (``degenerate=True``, gamma3/gamma4=None) are silently excluded:
    a flat / zero-variance equity has no testable return distribution and cannot
    enter the DSR cohort.  The caller (``run_pathd_verdict``) records excluded
    candidates in ``degenerate_legs`` so they are never silently dropped from the
    evidence bundle.

    Args:
        rows: List of holdout row dicts (from produce_candidate_holdout return
            value ``row`` fields), each with keys: hypothesis_hash, name, theme,
            T_obs, gamma3, gamma4, returns_per_bar_sha256, holdout_total_trades.
            Rows with ``degenerate=True`` are excluded from the CSV.
        cohort_dir: Root path for Path D artifacts; CSV written as
            cohort_dir/holdout_results.csv.

    Returns:
        The assembled DataFrame containing only non-degenerate rows (also
        persisted to CSV).
    """
    non_degenerate = [r for r in rows if not r.get("degenerate", False)]
    df = pd.DataFrame(non_degenerate) if non_degenerate else pd.DataFrame()
    (Path(cohort_dir) / "holdout_results.csv").write_text(df.to_csv(index=False))
    return df


def load_pathd_moments(
    hashes: list[str], df: pd.DataFrame, cohort_dir: Path
) -> list[CandidateMoments]:
    """Load each OI candidate's moments via the integrity-gated tier6 loader.

    Reuses ``load_candidate_moments`` (Decision 3): sha256 + independent
    gamma3/gamma4/T recompute + lineage guard. Path D never bypasses this gate.

    Args:
        hashes: List of hypothesis_hash strings to load.
        df: The holdout_results.csv DataFrame (from build_cohort_csv).
        cohort_dir: Root path for Path D artifacts (same as in build_cohort_csv).

    Returns:
        List of CandidateMoments, one per hash in the same order as ``hashes``.

    Raises:
        ValueError: On sha256 integrity mismatch, lineage guard failure, or
            stored-vs-recompute moment mismatch (propagated from
            load_candidate_moments).
    """
    return [load_candidate_moments(h, df, holdout_dir=Path(cohort_dir)) for h in hashes]
