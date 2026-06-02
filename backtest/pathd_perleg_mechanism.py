# backtest/pathd_perleg_mechanism.py
"""Path D tiered (24h + 72h) per-leg mechanism-sanity (Task C5).

Near-verbatim adapt of backtest/pathc_perleg_mechanism.py retargeted at the 3 OI
hypotheses (H1 oi_extreme_fade / H2 oi_regime_gate / H3 oi_momentum_continuation).

Tier logic (horizon-agnostic; only cohort and factor IDs change):
  strong_sane = the hypothesized sign holds at BOTH the 24h and 72h horizon.
  weak_sane   = the hypothesized sign holds at EITHER horizon (floor).
  refuted     = the hypothesized sign holds at NEITHER horizon.

Per-leg hypothesized signs (LOCK Pre-registration directions):
  H1 oi_extreme_fade         — extreme-high-OI tail reverses DOWN: sane sign NEGATIVE.
  H2 oi_regime_gate          — permissive regime (oi_pctrank low) outperforms de-risk
                                AND is itself positive: sane iff permissive_mean >
                                derisk_mean AND permissive_mean > 0.
  H3 oi_momentum_continuation — long-entry population (OI trending up + momentum
                                positive) continues UP: sane sign POSITIVE.

Train-only: callers pass a train-windows frame with fwd_ret_24h / fwd_ret_72h
columns (the per-leg driver guards the window upstream).
"""
from __future__ import annotations

import pandas as pd

STRONG_SANE = "strong_sane"
WEAK_SANE = "weak_sane"
REFUTED = "refuted"


def _sane_at(mean: float, sane_sign: str) -> bool:
    """True iff ``mean`` matches the hypothesized ``sane_sign`` ('+' or '-')."""
    if sane_sign == "+":
        return mean > 0.0
    if sane_sign == "-":
        return mean < 0.0
    raise ValueError(f"sane_sign must be '+' or '-'; got {sane_sign!r}")


def _tier(sane_24h: bool, sane_72h: bool) -> str:
    """Map (sane@24h, sane@72h) to a strong/weak/refuted tier."""
    if sane_24h and sane_72h:
        return STRONG_SANE
    if sane_24h or sane_72h:
        return WEAK_SANE
    return REFUTED


def classify_leg(mean_24h: float, mean_72h: float, sane_sign: str) -> dict:
    """Tier a single-sign leg from its 24h + 72h conditional mean forward returns.

    Args:
        mean_24h: Conditional mean forward return over a 24-bar horizon.
        mean_72h: Conditional mean forward return over a 72-bar horizon.
        sane_sign: Hypothesized sign — ``"+"`` (continuation UP, e.g. H3) or
            ``"-"`` (reversal DOWN, e.g. H1).

    Returns:
        A dict: ``tier`` (strong_sane/weak_sane/refuted), ``mean_24h``,
        ``mean_72h``, ``sane_24h``, ``sane_72h``, ``sane_sign``.
    """
    sane_24h = _sane_at(mean_24h, sane_sign)
    sane_72h = _sane_at(mean_72h, sane_sign)
    return {
        "tier": _tier(sane_24h, sane_72h),
        "mean_24h": float(mean_24h),
        "mean_72h": float(mean_72h),
        "sane_24h": bool(sane_24h),
        "sane_72h": bool(sane_72h),
        "sane_sign": sane_sign,
    }


def classify_h2_leg(
    perm_24h: float, derisk_24h: float, perm_72h: float, derisk_72h: float
) -> dict:
    """Tier the H2 regime-gate leg from its two-population means at both horizons.

    H2 is sane at a horizon iff the permissive-regime mean BEATS the de-risk-regime
    mean AND is itself positive (the regime gate adds value AND the long is real).

    Args:
        perm_24h / perm_72h: Permissive-regime mean forward return at 24h / 72h.
        derisk_24h / derisk_72h: De-risk-regime mean forward return at 24h / 72h.

    Returns:
        A dict: ``tier``, the four means, ``sane_24h``, ``sane_72h``, and
        ``sane_sign="h2_permissive_beats_derisk_and_positive"`` (descriptive).
    """
    sane_24h = (perm_24h > derisk_24h) and (perm_24h > 0.0)
    sane_72h = (perm_72h > derisk_72h) and (perm_72h > 0.0)
    return {
        "tier": _tier(sane_24h, sane_72h),
        "perm_24h": float(perm_24h),
        "derisk_24h": float(derisk_24h),
        "perm_72h": float(perm_72h),
        "derisk_72h": float(derisk_72h),
        "sane_24h": bool(sane_24h),
        "sane_72h": bool(sane_72h),
        "sane_sign": "h2_permissive_beats_derisk_and_positive",
    }


def _cond_mean(df: pd.DataFrame, mask: pd.Series, fwd_col: str) -> float:
    """Conditional mean forward return over ``mask`` (0.0 on an empty population)."""
    sub = df.loc[mask, fwd_col]
    if sub.empty:
        return 0.0
    return float(sub.mean())
