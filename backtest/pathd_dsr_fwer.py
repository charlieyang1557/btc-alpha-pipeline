# backtest/pathd_dsr_fwer.py
"""Step DSR-FWER for the Path D OI grid (per-candidate, NOT cohort-partition).

Adapted near-verbatim from backtest/pathc_dsr_fwer.py; retargeted to the Path D
OI cohort. evaluate_cohort hard-requires the locked 18/21 partition via
derive_cohort (raises if len != 18/21). The Path D 3-variant OI grid is a
DIFFERENT cohort, so this module loops evaluate_candidate(cm, n_star=PATHD_N_STAR)
per candidate and selects survivors = rows with pass_B is True (the authoritative
Form B gate).

CandidateMoments are built UPSTREAM by backtest.pathd_moments.load_pathd_moments
from Path D's OWN forward_2026 holdout artifacts (sr_per_bar / gamma3 / gamma4 /
T). That loader REUSES tier6 load_candidate_moments (the sha256 + moment-recompute
integrity gate, Decision 3) but with holdout_dir pointed at Path D's OWN namespace
— so Path D's OI moments meet the SAME integrity bar as the dead-18 cohort
while NEVER reading the sealed cohort's artifacts. This module only does the
per-candidate DSR math (REUSED from tier6.evaluate_candidate, Form B, frozen
Z_PASS) on already-built moments.

CONTRACT BOUNDARY: PATHD_N_STAR is identical to PATHC_N_STAR, PATHA_N_STAR, and
PATHB_N_STAR (all = the Step -1 LOCK N* = 3: 3 hypotheses × 1 pre-registered
variant each, no sweep). They are kept as separate symbols (one per Path) so a
future change to one Path's inferential family does not silently alter the other;
a regression test asserts they currently agree.
"""
from __future__ import annotations

from backtest.tier6_dsr import CandidateMoments, evaluate_candidate

# Step -1 LOCK: N* = 3 (minimal OI grid — 3 hypotheses × 1 variant each, no
# sweep). Equal to backtest.pathc_dsr_fwer.PATHC_N_STAR and
# backtest.patha_dsr_fwer.PATHA_N_STAR; referenced symbolically.
PATHD_N_STAR = 3


def _dsr_rows(candidates: list[CandidateMoments], n_star: int = PATHD_N_STAR) -> list[dict]:
    """Per-candidate DSR rows via evaluate_candidate (NOT evaluate_cohort).

    Args:
        candidates: The Path D OI grid's per-candidate moments.
        n_star: Step -1 locked multiplicity (default PATHD_N_STAR).

    Returns:
        One evaluate_candidate result dict per candidate, in input order.
    """
    return [evaluate_candidate(cm, n_star=n_star) for cm in candidates]


def run_dsr_fwer(
    candidates: list[CandidateMoments], n_star: int = PATHD_N_STAR
) -> dict:
    """Run the DSR-FWER screen; survivors are the authoritative Form B passes.

    Args:
        candidates: The Path D OI grid's per-candidate moments.
        n_star: Step -1 locked multiplicity (default PATHD_N_STAR).

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
