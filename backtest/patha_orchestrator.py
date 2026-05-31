# backtest/patha_orchestrator.py
"""Path A verdict orchestrator (ADVISORY) + hypothesis-class floors (Task C7).

Adapted from backtest/pathb_orchestrator.py. Pure composition over injected stage
callables: per-candidate gauntlet -> holdout_sharpe; build integrity-gated moments;
DSR-FWER at N*=3; train-only tiered per-leg mechanism sanity; earned-negative
taxonomy; next-axis escalation advisory (keyed on n_dsr_pass == 0 — Path A has NO
Step-0). The binding earned-negative read + escalation remain a Charlie register.

Task C7 hypothesis-class eligibility floors (LOCK Pre-registration 3) live here:
  - H1 (long-biased overlay): >= 200 DEFENSIVE FLAT-EXIT EPISODES (long->flat
    transitions, the funding-signal firings) over TRAIN — NOT long-bar occupancy
    (H1 is near-always-long, so occupancy is uninformative).
  - H2 / H3 (state-class): zero_fraction < 0.50 AND >= 200 trades over TRAIN.
Under-floor -> INDETERMINATE (not a Tier-5 pass/fail); the verdict run records the
INDETERMINATE status rather than scoring an under-floored variant as a Tier-5
pass/fail.
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np

from backtest.patha_dsr_fwer import run_dsr_fwer, PATHA_N_STAR
from backtest.patha_earned_negative import assemble_evidence
from backtest.patha_escalation import a_escalation_advisory

# LOCK Pre-registration 3 floor thresholds (symbolic).
H1_MIN_FLAT_EXIT_EPISODES = 200
H2H3_MIN_TRADES = 200
H2H3_MAX_ZERO_FRACTION = 0.50

INDETERMINATE = "INDETERMINATE"
ELIGIBLE = "ELIGIBLE"


def count_flat_exit_episodes(position: np.ndarray) -> int:
    """Count defensive flat-exit episodes = long->flat transitions in a position series.

    A "long->flat transition" is a bar where the position goes from long (>0) to
    flat (<=0) — the funding-signal firing that de-risks H1's near-always-long book.
    Flat->long ENTRIES are NOT counted (they are not defensive exits).

    Args:
        position: Per-bar position series (>0 = long, <=0 = flat) over the train window.

    Returns:
        The count of long->flat transitions.
    """
    pos = np.asarray(position, dtype=np.float64)
    if pos.shape[0] < 2:
        return 0
    is_long = pos > 0.0
    # transition at bar i: was long at i-1, flat at i.
    return int(np.sum(is_long[:-1] & ~is_long[1:]))


def h1_floor(position: np.ndarray) -> dict:
    """H1 eligibility floor: >= 200 defensive flat-exit episodes over TRAIN.

    Args:
        position: H1's per-bar TRAIN position series.

    Returns:
        A dict: ``eligible`` (bool), ``flat_exit_episodes`` (int), ``status``
        (``ELIGIBLE`` or ``INDETERMINATE``), ``threshold``.
    """
    episodes = count_flat_exit_episodes(position)
    eligible = episodes >= H1_MIN_FLAT_EXIT_EPISODES
    return {
        "eligible": eligible,
        "flat_exit_episodes": episodes,
        "threshold": H1_MIN_FLAT_EXIT_EPISODES,
        "status": ELIGIBLE if eligible else INDETERMINATE,
    }


def h2h3_floor(zero_fraction: float, total_trades: int) -> dict:
    """H2/H3 eligibility floor: zero_fraction < 0.50 AND >= 200 trades over TRAIN.

    Args:
        zero_fraction: Fraction of TRAIN bars with zero position (inactivity).
        total_trades: TRAIN trade count.

    Returns:
        A dict: ``eligible`` (bool), ``zero_fraction``, ``total_trades``,
        ``status`` (``ELIGIBLE`` or ``INDETERMINATE``), thresholds.
    """
    eligible = (zero_fraction < H2H3_MAX_ZERO_FRACTION) and (total_trades >= H2H3_MIN_TRADES)
    return {
        "eligible": eligible,
        "zero_fraction": float(zero_fraction),
        "total_trades": int(total_trades),
        "max_zero_fraction": H2H3_MAX_ZERO_FRACTION,
        "min_trades": H2H3_MIN_TRADES,
        "status": ELIGIBLE if eligible else INDETERMINATE,
    }


def run_patha_verdict(
    *,
    hypotheses: dict[str, Any],
    run_gauntlet: Callable[[str, Any], dict],
    build_moments: Callable[[dict], list],
    run_dsr: Callable[[list], dict] = run_dsr_fwer,
    per_leg: Callable[[], dict],
    floors: dict | None = None,
    funding_marginal: dict | None = None,
) -> dict[str, Any]:
    """Compose the advisory verdict pipeline. Returns the evidence bundle.

    Args:
        hypotheses: Mapping of hypothesis key (e.g. ``"H1"``) to DSL object.
        run_gauntlet: Callable ``(key, dsl) -> {"holdout_sharpe": float, ...}``
            for the Tier-5 holdout gauntlet per candidate.
        build_moments: Callable ``(holdouts_dict) -> list[CandidateMoments]``.
        run_dsr: Callable ``(cms) -> {"survivors", "rows", "n_star"}``; defaults
            to ``run_dsr_fwer``.
        per_leg: Zero-arg callable returning the per-leg tier dict (produced on
            train-only data by ``compute_per_leg_tiers``).
        floors: Optional Task C7 per-hypothesis eligibility-floor dict (recorded;
            an under-floored variant's INDETERMINATE status rides along).
        funding_marginal: Optional fenced funding-marginal diagnostic dict
            (recorded; NEVER feeds N* or promotion — it rides along only).

    Returns:
        Evidence bundle with keys: ``holdouts``, ``n_tier5_pass``, ``n_dsr_pass``,
        ``dsr``, ``per_leg``, ``taxonomy``, ``escalation``, ``floors``,
        ``funding_marginal``.
    """
    holdouts = {key: run_gauntlet(key, dsl) for key, dsl in hypotheses.items()}
    n_tier5_pass = sum(1 for h in holdouts.values() if h["holdout_sharpe"] > 0)

    cms = build_moments(holdouts)
    dsr = run_dsr(cms) if cms else {"survivors": [], "rows": [], "n_star": PATHA_N_STAR, "n_candidates": 0}
    n_dsr_pass = len(dsr["survivors"])

    sanity = per_leg()
    taxonomy = assemble_evidence(
        per_leg=sanity,
        n_tier5_pass=n_tier5_pass,
        n_dsr_pass=n_dsr_pass,
        promotion_side_effect=False,
    )
    escalation = a_escalation_advisory(
        taxonomy["advisory_taxonomy"], n_dsr_pass=n_dsr_pass
    )
    return {
        "holdouts": holdouts,
        "n_tier5_pass": n_tier5_pass,
        "n_dsr_pass": n_dsr_pass,
        "dsr": dsr,
        "per_leg": sanity,
        "taxonomy": taxonomy,
        "escalation": escalation,
        "floors": floors,
        "funding_marginal": funding_marginal,
    }
