# backtest/pathd_orchestrator.py
"""Path D verdict orchestrator (ADVISORY) + hypothesis-class floors (Task C7).

Adapted from backtest/pathc_orchestrator.py. Pure composition over injected stage
callables: per-candidate gauntlet -> holdout_sharpe; build integrity-gated moments;
DSR-FWER at N*=3; train-only tiered per-leg mechanism sanity; earned-negative
taxonomy (with GENERIC under-determined carve-out and tier threading); next-axis
escalation advisory (keyed on n_dsr_pass == 0 — Path D has NO Step-0).

KEY DIVERGENCE from pathc: D1-only orthogonalization.
  The orchestrator + earned_negative wire ``pathd_marginal_diagnostic.oi_marginal_d1``
  + ``contamination_correlations`` ONLY. There is NO D2 (``basis_marginal_d2`` /
  ``redundancy_read`` / ``d2_agrees``). OI is an independent axis — no derived-from
  relation — so Path C's D2-vs-funding/basis comparison is meaningless here. The
  §38.3 inheritance is ONLY the inert-D1-modal + fenced-label-read discipline.

  DESIGN INVARIANT (D2 absence): do NOT add any reference to d2, basis_marginal_d2,
  redundancy_read, or d2_agrees in this module or any pathd_* module. A stray
  reference would crash (those symbols are not in pathd_marginal_diagnostic).

NET-NEW vs pathc:
  - The under-determined carve-out (F3) applies to the GENERIC predicate:
    ``eligible == False AND total_trades < UNDER_DETERMINED_TRADE_THRESHOLD AND
    holdout_sharpe >= 0`` — ANY floor type, NOT zero_fraction-specific.
  - An under-powered-but-SANE H3 is annotated
    ``consistent_with_momentum_or_vol_leakage=True`` in the bundle (assembled by
    pathd_earned_negative.assemble_evidence).
  - The per-leg strong/weak-sane tier is threaded into assemble_evidence to set
    ``verdict_rests_on_weak_sane_only=True`` when any_mechanism_sane rests solely
    on weak-sane legs.

Task C7 hypothesis-class eligibility floors (LOCK Pre-registration 3) live here:
  - H1 (long-biased de-risk overlay): >= 200 DEFENSIVE FLAT-EXIT EPISODES (long->flat
    transitions, the OI-tail-gate firings) over TRAIN — NOT long-bar occupancy
    (H1 is near-always-long, so occupancy is uninformative).
  - H2 / H3 (state-class): zero_fraction < 0.50 AND >= 200 trades over TRAIN.
    NOTE: H2/H3 are expected-INDETERMINATE on zero_fraction (price-trend AND-confirm
    fires <50% of bars; same structural expectation as Path A/C H2/H3).

C7 INTEGRATION:
  - ``resolve_theta(episodes_at_090)`` — θ_oi_hi := 0.90; if train H1 flat-exit
    episodes at θ=0.90 < 200, θ := 0.85 (fixed fallback, never tuned toward Sharpe).
    Evaluated ONCE on train; frozen for H1+H3 JOINTLY (exact-partition invariant).
  - ``h1_floor_eligible(episodes_at_frozen_theta)`` — True iff >= 200.
  - ``h2_derisk_occupancy_eligible(occupancy)`` — True iff >= 0.10.
  All floor checks on the TRAIN window only; under-floor -> INDETERMINATE.

NOTE (OI NaN power disclosure): the OI percentile/regime factors are heavily NaN
in 2024/2025 due to scattered zero-OI-glitch gap-propagation — each zero-OI bar
NaNs the entire rolling-2160 (~90d) percentile window containing it, so the NaN
is data-driven, not a front-loaded burn-in; forward_2026 (the gate) is 0% NaN.
Floor eligibility is computed on the non-NaN subset of train bars; this is a
known power limitation, handled gracefully (NaN-is-False in the DSL compiler;
degenerate/flat equity returns handled by the produce_candidate_holdout guard).
Do not crash on NaN-heavy train subsets.
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np
import pandas as pd

from backtest.pathd_dsr_fwer import run_dsr_fwer, PATHD_N_STAR
from backtest.pathd_earned_negative import (
    UNDER_DETERMINED_TRADE_THRESHOLD,
    assemble_evidence,
)
from backtest.pathd_escalation import d_escalation_advisory

# LOCK Pre-registration 3 floor thresholds (symbolic).
H1_MIN_FLAT_EXIT_EPISODES = 200
H2H3_MIN_TRADES = 200
H2H3_MAX_ZERO_FRACTION = 0.50

INDETERMINATE = "INDETERMINATE"
ELIGIBLE = "ELIGIBLE"


# ---------------------------------------------------------------------------
# C7: resolve_theta + floor eligibility helpers
# ---------------------------------------------------------------------------

def resolve_theta(episodes_at_090: int) -> float:
    """Resolve θ_oi_hi per the deterministic fallback rule (LOCK Pre-reg 1, Task C7).

    θ_oi_hi := 0.90; if the train count of H1 defensive-flat-exit episodes at
    θ=0.90 is < 200, then θ_oi_hi := 0.85 (fixed fallback — never tuned toward
    Sharpe). Evaluated ONCE on train; the resulting θ is frozen for H1 and H3
    JOINTLY (they share the tail boundary as an exact partition at the pct-rank
    boundary).

    DESIGN INVARIANT (C7 integration): the fallback threshold is the same as
    H1_MIN_FLAT_EXIT_EPISODES (200). The caller passes in the episode count
    measured at θ=0.90; this function encapsulates the deterministic rule.

    Args:
        episodes_at_090: The H1 defensive flat-exit episode count over TRAIN,
            measured at θ=0.90 (the default threshold used for the initial count).

    Returns:
        0.90 if ``episodes_at_090 >= 200``; 0.85 (fallback) otherwise.
    """
    if int(episodes_at_090) < H1_MIN_FLAT_EXIT_EPISODES:
        return 0.85
    return 0.90


def h1_floor_eligible(episodes_at_frozen_theta: int) -> bool:
    """H1 event-class eligibility floor: >= 200 defensive flat-exit episodes at the FROZEN θ.

    The floor is always judged at the FROZEN θ (LOCK Pre-reg 1): if the fallback
    fired (θ=0.85 instead of 0.90), episodes are recounted at 0.85 and the floor
    is judged at that count — the strategy and its eligibility floor always share
    one θ. The caller is responsible for passing the episode count at the correct
    (already-frozen) θ.

    Args:
        episodes_at_frozen_theta: Defensive flat-exit episode count over TRAIN, measured
            at whichever θ ``resolve_theta`` resolved to.

    Returns:
        True if ``episodes_at_frozen_theta >= 200``, else False.
    """
    return int(episodes_at_frozen_theta) >= H1_MIN_FLAT_EXIT_EPISODES


def h2_derisk_occupancy_eligible(occupancy: float) -> bool:
    """H2 de-risk-cell occupancy floor: >= 10% of evaluated train bars in de-risk cell.

    The de-risk cell is defined by ``oi_velocity_ewm_240_pctrank_2160 >= 0.80``
    (the regime de-risk boundary — bars in the high-OI-velocity regime where H2
    exits to flat). The check verifies the conditional-separation kill remains
    powered.

    H2 ALSO requires the H2/H3 state-class floor (zero_fraction < 0.50 AND >= 200
    trades over train) — see h2h3_floor(). This function covers only the de-risk-
    occupancy prong, which is H2-specific (H3 has no de-risk cell).

    NOTE: the OI percentile factor is NaN-heavy early in the dataset; the occupancy
    is computed on the non-NaN subset by the caller (so a NaN-dominated train
    segment does not spuriously fail this floor — it correctly produces NaN-free
    occupancy from the available bars).

    Args:
        occupancy: Fraction of evaluated train bars where the OI de-risk condition
            holds (oi_velocity_ewm_240_pctrank_2160 >= 0.80).

    Returns:
        True if ``occupancy >= 0.10``, else False.
    """
    return float(occupancy) >= 0.10


# ---------------------------------------------------------------------------
# Floor helpers (mirror pathc_orchestrator; C7 uses these directly)
# ---------------------------------------------------------------------------

def count_flat_exit_episodes(position: np.ndarray) -> int:
    """Count defensive flat-exit episodes = long->flat transitions in a position series.

    A "long->flat transition" is a bar where the position goes from long (>0) to
    flat (<=0) — the OI-tail-gate firing that de-risks H1's near-always-long book.
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
    ``count_flat_exit_episodes`` sees a SINGLE long->flat transition (the OI
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

    NOTE: H2/H3 are expected-INDETERMINATE on zero_fraction (the price-trend
    AND-confirm fires <50% of bars; same structural expectation as Path A/C).

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
# GENERIC F3 under-determined helper
# ---------------------------------------------------------------------------

def _is_under_determined(
    eligible: bool,
    holdout_sharpe: float,
    holdout_total_trades: int,
    threshold: int = UNDER_DETERMINED_TRADE_THRESHOLD,
) -> bool:
    """True iff the leg qualifies for the GENERIC under-determined carve-out.

    A leg is under-determined when it is floor-INELIGIBLE (eligible==False, for ANY
    floor type — H1 flat-exit-episodes, H2/H3 zero_fraction/trade-count, H2
    de-risk-occupancy) AND returns a thin-sample non-negative forward Sharpe
    (trade count < threshold AND holdout_sharpe >= 0). Such a leg is NOT folded
    into the earned-negative (neither substantive-negative nor Tier-5-eligible)
    and is surfaced as a power gap.

    This is the PATH D GENERALIZATION of Path C's zero_fraction-specific F3
    carve-out: the predicate is ``eligible == False AND ...``, not tied to any
    specific floor condition.

    Args:
        eligible: Whether this candidate passed its hypothesis-class floor (ANY floor).
        holdout_sharpe: The candidate's forward holdout Sharpe.
        holdout_total_trades: The forward holdout trade count.
        threshold: Trade count below which a non-negative Sharpe is "thin-sample".

    Returns:
        True iff the GENERIC power-gap carve-out applies.
    """
    if eligible:
        return False  # eligible legs are never under-determined
    return (holdout_total_trades < threshold) and (holdout_sharpe >= 0.0)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_pathd_verdict(
    *,
    hypotheses: dict[str, Any],
    run_gauntlet: Callable[[str, Any], dict],
    build_moments: Callable[[dict], list],
    run_dsr: Callable[[list], dict] = run_dsr_fwer,
    per_leg: Callable[[], dict],
    floors: dict | None = None,
    oi_marginal: dict | None = None,
) -> dict[str, Any]:
    """Compose the advisory verdict pipeline. Returns the evidence bundle.

    Args:
        hypotheses: Mapping of hypothesis key (e.g. ``"H1"``) to DSL object.
        run_gauntlet: Callable ``(key, dsl) -> {"holdout_sharpe": float,
            "holdout_total_trades": int, ...}`` for the Tier-5 holdout gauntlet
            per candidate. The ``holdout_total_trades`` key is used for the GENERIC
            F3 under-determined check; default 0 if absent (conservative — forces
            under-determined evaluation for floor-ineligible non-negative legs).
        build_moments: Callable ``(holdouts_dict) -> list[CandidateMoments]``.
        run_dsr: Callable ``(cms) -> {"survivors", "rows", "n_star"}``; defaults
            to ``run_dsr_fwer``.
        per_leg: Zero-arg callable returning the per-leg tier dict (produced on
            train-only data by C5 ``compute_per_leg_tiers``).
        floors: Optional Task C7 per-hypothesis eligibility-floor dict. When
            provided, an under-floored (``eligible=False``) candidate is marked
            ``INDETERMINATE`` and EXCLUDED from ``n_tier5_pass`` (LOCK "floors before
            ranking"); the GENERIC F3 carve-out is evaluated for under-floored legs
            with thin-sample non-negative forward Sharpe. When None, the count is
            the raw positive-Sharpe count.
        oi_marginal: Optional fenced OI-marginal diagnostic dict (D1-only; recorded;
            NEVER feeds N* or promotion — it rides along only). Contains per-hypothesis
            D1 only; the contamination_correlations set lives at root
            ``bundle["contamination_correlations"]`` (also fenced). NO D2 field (OI is
            the independent axis).

    Returns:
        Evidence bundle with keys: ``holdouts``, ``n_tier5_pass``, ``n_dsr_pass``,
        ``dsr``, ``per_leg``, ``taxonomy``, ``escalation``, ``floors``,
        ``oi_marginal``, ``under_determined_legs``, ``degenerate_legs``,
        ``consistent_with_momentum_or_vol_leakage``.
    """
    holdouts = {key: run_gauntlet(key, dsl) for key, dsl in hypotheses.items()}

    # --- Degenerate-leg detection ---
    # A degenerate holdout (flat / zero-variance forward equity, gate didn't fire)
    # is flagged ``degenerate=True`` by the producer. It cannot enter the DSR cohort
    # (no testable return distribution). Record it in degenerate_legs, exclude it
    # from build_moments, and do NOT count it as a Tier-5 pass (holdout_sharpe=0.0
    # already fails the strict >0 gate, but we also never pass it to build_moments).
    degenerate_legs: dict[str, bool] = {}
    for key, h in holdouts.items():
        if h.get("degenerate", False):
            degenerate_legs[key] = True

    # LOCK "floors applied BEFORE ranking": when a floors dict is provided, an
    # UNDER-FLOOR (ineligible) candidate is NOT a Tier-5 pass/fail — it is
    # INDETERMINATE and EXCLUDED from n_tier5_pass.
    # GENERIC F3: for under-floor legs, check the under-determined carve-out
    # (thin-sample non-negative Sharpe -> power gap, not earned-negative).
    n_tier5_pass = 0
    under_determined_flags: dict[str, bool] = {}
    for key, h in holdouts.items():
        eligible = True
        if floors is not None:
            eligible = bool(floors.get(key, {}).get("eligible", True))
            if not eligible:
                h["tier5_status"] = INDETERMINATE
                # GENERIC F3: check if this under-floor leg is under-determined
                # (ANY floor type — not zero_fraction-specific).
                hst = float(h.get("holdout_sharpe", 0.0))
                htrades = int(h.get("holdout_total_trades", 0))
                under_determined_flags[key] = _is_under_determined(
                    eligible=False,
                    holdout_sharpe=hst,
                    holdout_total_trades=htrades,
                )
        if eligible and h.get("holdout_sharpe", float("-inf")) > 0:
            n_tier5_pass += 1

    # Pass only non-degenerate holdouts to build_moments — a flat series has no
    # testable return distribution and must not enter the DSR cohort.
    non_degenerate_holdouts = {k: v for k, v in holdouts.items()
                                if not degenerate_legs.get(k, False)}
    cms = build_moments(non_degenerate_holdouts)
    dsr = run_dsr(cms) if cms else {
        "survivors": [], "rows": [], "n_star": PATHD_N_STAR, "n_candidates": 0
    }
    n_dsr_pass = len(dsr["survivors"])

    sanity = per_leg()
    # Build per-leg holdout_sharpes for the §37.3 substantive-vs-vacuous check.
    # Only non-degenerate holdouts contribute (degenerate legs have sharpe=0.0 by
    # instrument repair — they are not measured losses, so they are excluded here
    # to avoid spuriously claiming a substantive basis from a flat equity).
    holdout_sharpes: dict[str, float] = {
        k: float(h.get("holdout_sharpe", 0.0))
        for k, h in holdouts.items()
        if not degenerate_legs.get(k, False)
    }
    taxonomy = assemble_evidence(
        per_leg=sanity,
        n_tier5_pass=n_tier5_pass,
        n_dsr_pass=n_dsr_pass,
        promotion_side_effect=False,
        under_determined_flags=under_determined_flags,
        holdout_sharpes=holdout_sharpes,
    )
    escalation = d_escalation_advisory(
        taxonomy["advisory_taxonomy"],
        n_dsr_pass=n_dsr_pass,
        negative_has_substantive_basis=taxonomy.get("negative_has_substantive_basis", True),
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
        "oi_marginal": oi_marginal,
        "under_determined_legs": taxonomy.get("under_determined_legs", {}),
        "degenerate_legs": degenerate_legs,
        "consistent_with_momentum_or_vol_leakage": taxonomy.get(
            "consistent_with_momentum_or_vol_leakage", False
        ),
    }
