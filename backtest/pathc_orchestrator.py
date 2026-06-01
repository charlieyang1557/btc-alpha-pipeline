# backtest/pathc_orchestrator.py
"""Path C verdict orchestrator (ADVISORY) + hypothesis-class floors (Task C7).

Adapted from backtest/patha_orchestrator.py. Pure composition over injected stage
callables: per-candidate gauntlet -> holdout_sharpe; build integrity-gated moments;
DSR-FWER at N*=3; train-only tiered per-leg mechanism sanity; earned-negative
taxonomy (with F3 under-determined carve-out and 1d tier threading); next-axis
escalation advisory (keyed on n_dsr_pass == 0 — Path C has NO Step-0). The binding
earned-negative read + escalation remain a Charlie register.

Task C7 hypothesis-class eligibility floors (LOCK Pre-registration 3) live here:
  - H1 (long-biased overlay): >= 200 DEFENSIVE FLAT-EXIT EPISODES (long->flat
    transitions, the basis-tail-gate firings) over TRAIN — NOT long-bar occupancy
    (H1 is near-always-long, so occupancy is uninformative).
  - H2 / H3 (state-class): zero_fraction < 0.50 AND >= 200 trades over TRAIN.
    NOTE: H2/H3 are PRE-REGISTERED as expected-INDETERMINATE on zero_fraction
    (price-trend AND-confirm fires <50% of bars; Path A H2/H3 measured 0.62/0.67).
Under-floor -> INDETERMINATE (not a Tier-5 pass/fail); the verdict run records the
INDETERMINATE status rather than scoring an under-floored variant as a Tier-5
pass/fail.

C7 INTEGRATION POINT: ``resolve_theta`` (determine θ_basis_hi per the deterministic
fallback rule: 0.90 if H1 flat-exit episodes >= 200, else 0.85) and
``h2_derisk_occupancy_eligible`` (B2 Finding 6 >= 10% de-risk occupancy check)
are Task C7 deliverables. The current stubs preserve the full patha orchestrator
structure so C7 can slot in:

  - ``resolve_theta(h1_episodes)`` → θ float (C7 will refine).
  - ``h2_derisk_occupancy_eligible(zero_fraction_derisk)`` → bool (C7 will add).

Both stubs are currently pass-through (no behavioral effect) so the orchestrator
is usable without C7; C7 implements the deterministic logic.
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np
import pandas as pd

from backtest.pathc_dsr_fwer import run_dsr_fwer, PATHC_N_STAR
from backtest.pathc_earned_negative import (
    UNDER_DETERMINED_TRADE_THRESHOLD,
    assemble_evidence,
)
from backtest.pathc_escalation import c_escalation_advisory

# LOCK Pre-registration 3 floor thresholds (symbolic).
H1_MIN_FLAT_EXIT_EPISODES = 200
H2H3_MIN_TRADES = 200
H2H3_MAX_ZERO_FRACTION = 0.50

INDETERMINATE = "INDETERMINATE"
ELIGIBLE = "ELIGIBLE"


# ---------------------------------------------------------------------------
# C7 integration stubs (Task C7 will refine to deterministic-θ + h2-occupancy)
# ---------------------------------------------------------------------------

def resolve_theta(h1_episodes: int) -> float:
    """C7 stub: resolve θ_basis_hi per the deterministic fallback rule.

    LOCK Pre-registration 1: θ_basis_hi = 0.90; if H1 flat-exit episodes < 200
    (the floor threshold), θ_basis_hi = 0.85 (the fixed fallback). H1 and H3
    JOINTLY share this boundary (exact partition at the pct-rank boundary).

    Task C7 will implement the full deterministic rule (evaluate once on train,
    freeze for H1+H3 jointly). This stub passes through to 0.90 and is
    replaced by C7 without changing the orchestrator's call signature.

    Args:
        h1_episodes: The H1 defensive flat-exit episode count over TRAIN.

    Returns:
        0.90 (default) or 0.85 (fallback when h1_episodes < 200).
    """
    from backtest.pathc_eval_gauntlet import H1_TAIL_RANK_DEFAULT
    # DESIGN INVARIANT (C7 integration): the fallback threshold is the same as
    # H1_MIN_FLAT_EXIT_EPISODES (200). C7 passes in the measured count;
    # this function encapsulates the deterministic rule so patha_run_verdict
    # (or its pathc equivalent) calls resolve_theta(measured_h1_episodes)
    # rather than inlining the if/else.
    if h1_episodes < H1_MIN_FLAT_EXIT_EPISODES:
        return 0.85
    return float(H1_TAIL_RANK_DEFAULT)


def h2_derisk_occupancy_eligible(zero_fraction_derisk: float) -> bool:
    """C7 stub: B2 Finding 6 >= 10% de-risk-cell occupancy check.

    The 0.80 band gives ~20% de-risk occupancy by construction (causal
    rolling-2160 percentile > 0.80 corresponds to ~20% of bars); this check
    verifies the conditional-separation kill remains powered. Task C7 will
    implement the full check against the measured de-risk fraction.

    Args:
        zero_fraction_derisk: Fraction of train bars in the de-risk regime
            (basis_ewm_240_pctrank_2160 >= 0.80).

    Returns:
        True if occupancy >= 0.10, else False.
    """
    return float(zero_fraction_derisk) >= 0.10


# ---------------------------------------------------------------------------
# Floor helpers (mirror patha_orchestrator; C7 will use these directly)
# ---------------------------------------------------------------------------

def count_flat_exit_episodes(position: np.ndarray) -> int:
    """Count defensive flat-exit episodes = long->flat transitions in a position series.

    A "long->flat transition" is a bar where the position goes from long (>0) to
    flat (<=0) — the basis-tail-gate firing that de-risks H1's near-always-long book.
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
    ``count_flat_exit_episodes`` sees a SINGLE long->flat transition (the basis
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
    bars = idx.tz_localize(None) if getattr(idx, "tz", None) is not None else idx
    for t in trades:
        ent = t.get("entry_time_utc")
        ext = t.get("exit_time_utc")
        if ent is None:
            continue
        lo = pd.Timestamp(ent)
        lo = lo.tz_localize(None) if lo.tz is not None else lo
        if ext is None:
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


def h1_floor_from_episodes(episodes: int) -> dict:
    """H1 eligibility floor from a PRE-COUNTED flat-exit-episode total.

    Lets the caller count episodes PER CONTIGUOUS TRAIN WINDOW and sum them (so a
    long->flat transition manufactured across the excluded-2022 window gap is never
    counted), then apply the >= 200 floor on that summed total.

    Args:
        episodes: The total defensive flat-exit-episode count over TRAIN.

    Returns:
        A dict: ``eligible`` (bool), ``flat_exit_episodes`` (int), ``status``
        (``ELIGIBLE`` or ``INDETERMINATE``), ``threshold``.
    """
    eligible = episodes >= H1_MIN_FLAT_EXIT_EPISODES
    return {
        "eligible": eligible,
        "flat_exit_episodes": int(episodes),
        "threshold": H1_MIN_FLAT_EXIT_EPISODES,
        "status": ELIGIBLE if eligible else INDETERMINATE,
    }


def h1_floor(position: np.ndarray) -> dict:
    """H1 eligibility floor: >= 200 defensive flat-exit episodes over TRAIN.

    For the TRAIN-window floor the caller should instead count per contiguous window
    (via ``h1_floor_from_episodes``) so a transition across the excluded-2022 window
    gap is not spuriously counted.

    Args:
        position: H1's per-bar TRAIN position series.

    Returns:
        A dict: ``eligible`` (bool), ``flat_exit_episodes`` (int), ``status``
        (``ELIGIBLE`` or ``INDETERMINATE``), ``threshold``.
    """
    return h1_floor_from_episodes(count_flat_exit_episodes(position))


def h2h3_floor(zero_fraction: float, total_trades: int) -> dict:
    """H2/H3 eligibility floor: zero_fraction < 0.50 AND >= 200 trades over TRAIN.

    NOTE: H2/H3 are PRE-REGISTERED as expected-INDETERMINATE on zero_fraction
    (the price-trend AND-confirm fires <50% of bars; Path A H2/H3 measured
    zero_fraction 0.62/0.67 at a wide-open 0.80 band; the basis de-risk band at
    0.80 is structurally similar).

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


# ---------------------------------------------------------------------------
# F3 under-determined helper
# ---------------------------------------------------------------------------

def _is_under_determined(
    eligible: bool,
    holdout_sharpe: float,
    holdout_total_trades: int,
    threshold: int = UNDER_DETERMINED_TRADE_THRESHOLD,
) -> bool:
    """True iff the leg qualifies for the F3 under-determined carve-out.

    A leg is under-determined when it is floor-INELIGIBLE AND returns a
    thin-sample non-negative forward Sharpe (trade count < threshold AND
    holdout_sharpe >= 0). Such a leg is NOT folded into the earned-negative
    (neither substantive-negative nor Tier-5-eligible) and is surfaced as a
    power gap per LOCK Pre-registration 3 §37.3 + B2 advisor Finding 3.

    Args:
        eligible: Whether this candidate passed its hypothesis-class floor.
        holdout_sharpe: The candidate's forward holdout Sharpe.
        holdout_total_trades: The forward holdout trade count.
        threshold: Trade count below which a non-negative Sharpe is "thin-sample".

    Returns:
        True iff the F3 power-gap carve-out applies.
    """
    if eligible:
        return False  # eligible legs are never under-determined
    return (holdout_total_trades < threshold) and (holdout_sharpe >= 0.0)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_pathc_verdict(
    *,
    hypotheses: dict[str, Any],
    run_gauntlet: Callable[[str, Any], dict],
    build_moments: Callable[[dict], list],
    run_dsr: Callable[[list], dict] = run_dsr_fwer,
    per_leg: Callable[[], dict],
    floors: dict | None = None,
    basis_marginal: dict | None = None,
) -> dict[str, Any]:
    """Compose the advisory verdict pipeline. Returns the evidence bundle.

    Args:
        hypotheses: Mapping of hypothesis key (e.g. ``"H1"``) to DSL object.
        run_gauntlet: Callable ``(key, dsl) -> {"holdout_sharpe": float,
            "holdout_total_trades": int, ...}`` for the Tier-5 holdout gauntlet
            per candidate. The ``holdout_total_trades`` key is used for the F3
            under-determined check; default 0 if absent (conservative — forces
            under-determined evaluation for floor-ineligible non-negative legs).
        build_moments: Callable ``(holdouts_dict) -> list[CandidateMoments]``.
        run_dsr: Callable ``(cms) -> {"survivors", "rows", "n_star"}``; defaults
            to ``run_dsr_fwer``.
        per_leg: Zero-arg callable returning the per-leg tier dict (produced on
            train-only data by C5 ``compute_per_leg_tiers``).
        floors: Optional Task C7 per-hypothesis eligibility-floor dict. When
            provided, an under-floored (``eligible=False``) candidate is marked
            ``INDETERMINATE`` and EXCLUDED from ``n_tier5_pass`` (LOCK "floors before
            ranking"); the F3 carve-out is evaluated for under-floored legs with
            thin-sample non-negative forward Sharpe. When None, the count is the raw
            positive-Sharpe count.
        basis_marginal: Optional fenced basis-marginal diagnostic dict
            (recorded; NEVER feeds N* or promotion — it rides along only).

    Returns:
        Evidence bundle with keys: ``holdouts``, ``n_tier5_pass``, ``n_dsr_pass``,
        ``dsr``, ``per_leg``, ``taxonomy``, ``escalation``, ``floors``,
        ``basis_marginal``, ``under_determined_legs``.
    """
    holdouts = {key: run_gauntlet(key, dsl) for key, dsl in hypotheses.items()}

    # LOCK "floors applied BEFORE ranking": when a floors dict is provided, an
    # UNDER-FLOOR (ineligible) candidate is NOT a Tier-5 pass/fail — it is
    # INDETERMINATE and EXCLUDED from n_tier5_pass.
    # Sub-fix 1c: for under-floor legs, also check the F3 under-determined
    # carve-out (thin-sample non-negative Sharpe -> power gap, not earned-negative).
    n_tier5_pass = 0
    under_determined_flags: dict[str, bool] = {}
    for key, h in holdouts.items():
        eligible = True
        if floors is not None:
            eligible = bool(floors.get(key, {}).get("eligible", True))
            if not eligible:
                h["tier5_status"] = INDETERMINATE
                # F3: check if this under-floor leg is under-determined.
                hst = float(h.get("holdout_sharpe", 0.0))
                htrades = int(h.get("holdout_total_trades", 0))
                under_determined_flags[key] = _is_under_determined(
                    eligible=False,
                    holdout_sharpe=hst,
                    holdout_total_trades=htrades,
                )
        if eligible and h.get("holdout_sharpe", float("-inf")) > 0:
            n_tier5_pass += 1

    cms = build_moments(holdouts)
    dsr = run_dsr(cms) if cms else {
        "survivors": [], "rows": [], "n_star": PATHC_N_STAR, "n_candidates": 0
    }
    n_dsr_pass = len(dsr["survivors"])

    sanity = per_leg()
    taxonomy = assemble_evidence(
        per_leg=sanity,
        n_tier5_pass=n_tier5_pass,
        n_dsr_pass=n_dsr_pass,
        promotion_side_effect=False,
        under_determined_flags=under_determined_flags,
    )
    escalation = c_escalation_advisory(
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
        "basis_marginal": basis_marginal,
        "under_determined_legs": taxonomy.get("under_determined_legs", {}),
    }
