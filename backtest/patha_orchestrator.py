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
import pandas as pd

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


def position_series_from_trades(
    index: "pd.DatetimeIndex", trades: list[dict]
) -> np.ndarray:
    """Reconstruct a per-bar long/flat (1/0) position series over ``index``.

    The engine (backtest.engine.TradeCollector) records completed trades with
    ``entry_time_utc`` / ``exit_time_utc`` ISO strings but exposes no explicit
    per-bar position channel. For the TRAIN-window floors we reconstruct the
    long/flat occupancy: a bar is LONG (1) iff it falls in some trade's half-open
    ``[entry_time, exit_time)`` interval, else FLAT (0). The half-open interval is
    the key DESIGN INVARIANT for back-to-back trades: when one trade's exit_time
    equals the next trade's entry_time there is NO flat bar between them, so
    ``count_flat_exit_episodes`` sees a SINGLE long->flat transition (the funding
    signal fired once), not two — matching the LOCK's "defensive flat-exit
    episodes" semantics.

    Args:
        index: The bar index (the train-window equity-curve DatetimeIndex).
        trades: Completed-trade records, each with ``entry_time_utc`` /
            ``exit_time_utc`` (ISO 8601 UTC strings, the engine's format).

    Returns:
        An int ndarray of 1 (long) / 0 (flat), aligned to ``index``.
    """
    idx = pd.DatetimeIndex(index)
    pos = np.zeros(len(idx), dtype=np.int64)
    if len(idx) == 0 or not trades:
        return pos
    # Normalize to tz-naive UTC wall-time once: the trade ISO strings carry a Z so
    # they parse tz-aware; strip both sides so a tz-aware OR a Backtrader-naive
    # index compares cleanly against the trade bounds.
    bars = idx.tz_localize(None) if getattr(idx, "tz", None) is not None else idx
    for t in trades:
        ent = t.get("entry_time_utc")
        ext = t.get("exit_time_utc")
        if ent is None:
            continue
        lo = pd.Timestamp(ent)
        lo = lo.tz_localize(None) if lo.tz is not None else lo
        if ext is None:
            # An open-at-window-end trade: long from entry to the last bar inclusive.
            hi = bars[-1] + pd.Timedelta(hours=1)
        else:
            hi = pd.Timestamp(ext)
            hi = hi.tz_localize(None) if hi.tz is not None else hi
        mask = (bars >= lo) & (bars < hi)  # half-open [entry, exit)
        pos[np.asarray(mask)] = 1
    return pos


def zero_fraction_from_positions(position: np.ndarray) -> float:
    """Fraction of bars that are FLAT (position == 0) over the series.

    Args:
        position: Per-bar position series (>0 = long, <=0 = flat).

    Returns:
        ``count(flat bars) / len`` in [0, 1]. An EMPTY series returns 1.0 —
        a degenerate no-bar strategy is treated as fully inactive (under the
        H2/H3 ``zero_fraction < 0.50`` floor), never as spuriously active.
    """
    pos = np.asarray(position, dtype=np.float64)
    if pos.shape[0] == 0:
        return 1.0
    return float(np.sum(pos <= 0.0) / pos.shape[0])


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
        floors: Optional Task C7 per-hypothesis eligibility-floor dict. When
            provided, an under-floored (``eligible=False``) candidate is marked
            ``INDETERMINATE`` and EXCLUDED from ``n_tier5_pass`` (LOCK "floors before
            ranking"); when None, the count is the raw positive-Sharpe count.
        funding_marginal: Optional fenced funding-marginal diagnostic dict
            (recorded; NEVER feeds N* or promotion — it rides along only).

    Returns:
        Evidence bundle with keys: ``holdouts``, ``n_tier5_pass``, ``n_dsr_pass``,
        ``dsr``, ``per_leg``, ``taxonomy``, ``escalation``, ``floors``,
        ``funding_marginal``.
    """
    holdouts = {key: run_gauntlet(key, dsl) for key, dsl in hypotheses.items()}

    # LOCK Pre-registration 3 "floors applied BEFORE ranking": when a floors dict is
    # provided, an UNDER-FLOOR (ineligible) candidate is NOT a Tier-5 pass/fail — it
    # is INDETERMINATE and EXCLUDED from n_tier5_pass (and from DSR/taxonomy pass
    # counting, which key off n_tier5_pass / the DSR survivors). The under-floor
    # status rides on the holdout record so the advisory bundle records WHY a
    # positive-Sharpe candidate was not counted. When floors is None (build phase,
    # before TRAIN-window floors are computed at Phase D) the count is the raw
    # positive-Sharpe count — byte-identical to pre-fix behavior.
    n_tier5_pass = 0
    for key, h in holdouts.items():
        eligible = True
        if floors is not None:
            eligible = bool(floors.get(key, {}).get("eligible", True))
            if not eligible:
                h["tier5_status"] = INDETERMINATE
        if eligible and h["holdout_sharpe"] > 0:
            n_tier5_pass += 1

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
