# backtest/pathc_moments.py
"""Path C moments: assemble the cohort CSV from producer rows, then load each
CandidateMoments through the EXISTING tier6 integrity gate (Decision 3).

Adapted near-verbatim from backtest/patha_moments.py; retargeted to the Path C
basis cohort namespace. We do NOT recompute moments here —
load_candidate_moments performs the sha256 verification + the independent
gamma3/gamma4/T recompute, so Path C's basis moments meet exactly the same
integrity bar as the dead-18 cohort they are DSR-compared against. Path C owns
its OWN namespace; this never reads the sealed cohort.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from backtest.tier6_dsr import CandidateMoments, load_candidate_moments


def build_cohort_csv(rows: list[dict], cohort_dir: Path) -> pd.DataFrame:
    """Assemble + persist the Path C holdout_results.csv from producer rows.

    Args:
        rows: List of holdout row dicts (from produce_candidate_holdout return
            value ``row`` fields), each with keys: hypothesis_hash, name, theme,
            T_obs, gamma3, gamma4, returns_per_bar_sha256, holdout_total_trades.
        cohort_dir: Root path for Path C artifacts; CSV written as
            cohort_dir/holdout_results.csv.

    Returns:
        The assembled DataFrame (also persisted to CSV).
    """
    df = pd.DataFrame(rows)
    (Path(cohort_dir) / "holdout_results.csv").write_text(df.to_csv(index=False))
    return df


def load_pathc_moments(
    hashes: list[str], df: pd.DataFrame, cohort_dir: Path
) -> list[CandidateMoments]:
    """Load each basis candidate's moments via the integrity-gated tier6 loader.

    Reuses ``load_candidate_moments`` (Decision 3): sha256 + independent
    gamma3/gamma4/T recompute + lineage guard. Path C never bypasses this gate.

    Args:
        hashes: List of hypothesis_hash strings to load.
        df: The holdout_results.csv DataFrame (from build_cohort_csv).
        cohort_dir: Root path for Path C artifacts (same as in build_cohort_csv).

    Returns:
        List of CandidateMoments, one per hash in the same order as ``hashes``.

    Raises:
        ValueError: On sha256 integrity mismatch, lineage guard failure, or
            stored-vs-recompute moment mismatch (propagated from
            load_candidate_moments).
    """
    return [load_candidate_moments(h, df, holdout_dir=Path(cohort_dir)) for h in hashes]
