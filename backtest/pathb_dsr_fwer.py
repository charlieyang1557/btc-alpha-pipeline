# backtest/pathb_dsr_fwer.py
"""Step 5 DSR-FWER for the Path B grid (per-candidate, NOT cohort-partition).

evaluate_cohort hard-requires the locked 18/21 partition via derive_cohort
(raises if len != 18/21). The Path B 3-9-variant grid is a DIFFERENT cohort, so
this module loops evaluate_candidate(cm, n_star=PATHB_N_STAR) per candidate and
selects survivors = rows with pass_B is True (the authoritative Form B gate).

CandidateMoments are constructed UPSTREAM (in the eval harness) from Path B's
OWN per-bar validation returns (sr_per_bar / gamma3 / gamma4 / T) — NOT via
load_candidate_moments, which loads the sealed cohort's holdout artifacts. Path
B owns its candidates, builds its own moments, and never reads the dead-18
cohort here.

PATHB_N_STAR is Step -1 LOCK: N* = 3 (minimal grid — 3 hypotheses × 1 variant
each, no sweep); referenced symbolically.
"""
from __future__ import annotations

from backtest.tier6_dsr import CandidateMoments, evaluate_candidate

# Step -1 LOCK: N* = 3 (minimal grid — 3 hypotheses × 1 variant each, no sweep).
PATHB_N_STAR = 3


def _dsr_rows(candidates: list[CandidateMoments], n_star: int = PATHB_N_STAR) -> list[dict]:
    """Per-candidate DSR rows via evaluate_candidate (NOT evaluate_cohort).

    Args:
        candidates: The Path B grid's per-candidate moments.
        n_star: Step -1 locked multiplicity (default PATHB_N_STAR).

    Returns:
        One evaluate_candidate result dict per candidate, in input order.
    """
    return [evaluate_candidate(cm, n_star=n_star) for cm in candidates]


def run_dsr_fwer(
    candidates: list[CandidateMoments], n_star: int = PATHB_N_STAR
) -> dict:
    """Run the DSR-FWER screen; survivors are the authoritative Form B passes.

    Args:
        candidates: The Path B grid's per-candidate moments.
        n_star: Step -1 locked multiplicity (default PATHB_N_STAR).

    Returns:
        A dict with ``rows`` (all per-candidate DSR rows), ``survivors`` (rows
        with ``pass_B is True``), ``n_candidates`` and ``n_star``.
    """
    rows = _dsr_rows(candidates, n_star=n_star)
    survivors = [r for r in rows if r["pass_B"] is True]
    return {
        "rows": rows,
        "survivors": survivors,
        "n_candidates": len(candidates),
        "n_star": n_star,
    }
