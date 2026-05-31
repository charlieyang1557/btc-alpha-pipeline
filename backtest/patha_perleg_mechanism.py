# backtest/patha_perleg_mechanism.py
"""Path A tiered (24h + 72h) per-leg mechanism-sanity (Task C5).

Adapts backtest/pathb_perleg_mechanism.py's conditional-forward-return-sign test
to TWO horizons (24h AND 72h) and a strong/weak/refuted tier, per LOCK
Pre-registration 4:

  strong_sane = the hypothesized sign holds at BOTH the 24h and 72h horizon.
  weak_sane   = the hypothesized sign holds at EITHER horizon (floor).
  refuted     = the hypothesized sign holds at NEITHER horizon.

Both horizon signs are recorded so a verdict resting on weak-sane-only legs is
flagged downstream (a single-horizon noise flip cannot silently manufacture
mechanism-sanity).

Per-leg hypothesized signs (LOCK Pre-registration 1 directions):
  H1 funding_extreme_fade        — crowded-long tail (rank >= 0.90 AND sign > 0)
                                    reverses DOWN: sane sign NEGATIVE.
  H2 funding_sign_regime_switch  — permissive regime (funding_ewm_30_pctrank_270 <
                                    0.80) outperforms the de-risk regime AND is
                                    itself positive: sane iff permissive_mean >
                                    derisk_mean AND permissive_mean > 0.
  H3 funding_momentum_continuation — long entry population (funding_ewm_60 > 0 AND
                                    funding_pct_rank_270 <= 0.90 AND
                                    decay_linear_close_48 > decay_linear_close_168)
                                    continues UP: sane sign POSITIVE.

Train-only: callers pass a train-windows frame with fwd_ret_24h / fwd_ret_72h
columns (the per-leg driver guards the window upstream).
"""
from __future__ import annotations

import pandas as pd

# LOCK Pre-registration 1 thresholds (symbolic; do NOT change without a LOCK update).
H1_TAIL_RANK = 0.90
H2_DERISK_PCTRANK = 0.80
H3_TAIL_RANK = 0.90

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


def compute_per_leg_tiers(
    df: pd.DataFrame,
    fwd_24h_col: str = "fwd_ret_24h",
    fwd_72h_col: str = "fwd_ret_72h",
) -> dict:
    """Compute the H1/H2/H3 per-leg tiers on the TRAIN frame at 24h + 72h horizons.

    Args:
        df: Train-only frame with funding factor columns
            (``funding_pct_rank_270``, ``funding_sign``, ``funding_ewm_60``,
            ``funding_ewm_30_pctrank_270``, ``decay_linear_close_48``,
            ``decay_linear_close_168``) plus the two forward-return columns.
        fwd_24h_col / fwd_72h_col: Forward-return column names.

    Returns:
        ``{"H1": <classify_leg dict>, "H2": <classify_h2_leg dict>,
           "H3": <classify_leg dict>}``.
    """
    # H1: the crowded-long tail fades DOWN. Population = rank >= 0.90 AND sign > 0.
    h1_mask = (df["funding_pct_rank_270"] >= H1_TAIL_RANK) & (df["funding_sign"] > 0.0)
    h1 = classify_leg(
        mean_24h=_cond_mean(df, h1_mask, fwd_24h_col),
        mean_72h=_cond_mean(df, h1_mask, fwd_72h_col),
        sane_sign="-",
    )

    # H2: permissive (ewm_30_pctrank < 0.80) vs de-risk (>= 0.80) regime means.
    perm_mask = df["funding_ewm_30_pctrank_270"] < H2_DERISK_PCTRANK
    derisk_mask = df["funding_ewm_30_pctrank_270"] >= H2_DERISK_PCTRANK
    h2 = classify_h2_leg(
        perm_24h=_cond_mean(df, perm_mask, fwd_24h_col),
        derisk_24h=_cond_mean(df, derisk_mask, fwd_24h_col),
        perm_72h=_cond_mean(df, perm_mask, fwd_72h_col),
        derisk_72h=_cond_mean(df, derisk_mask, fwd_72h_col),
    )

    # H3: long-entry population continues UP. Population = ewm_60 > 0 AND
    # rank <= 0.90 (off H1's tail) AND decay_48 > decay_168 (price-trend confirm).
    h3_mask = (
        (df["funding_ewm_60"] > 0.0)
        & (df["funding_pct_rank_270"] <= H3_TAIL_RANK)
        & (df["decay_linear_close_48"] > df["decay_linear_close_168"])
    )
    h3 = classify_leg(
        mean_24h=_cond_mean(df, h3_mask, fwd_24h_col),
        mean_72h=_cond_mean(df, h3_mask, fwd_72h_col),
        sane_sign="+",
    )

    return {"H1": h1, "H2": h2, "H3": h3}
