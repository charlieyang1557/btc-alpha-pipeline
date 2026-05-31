# backtest/pathb_perleg_mechanism.py
"""H2 per-leg mechanism_sane producer + H1/H3 conditional forward-return signs.

H2 is a two-sided mean-reversion hypothesis whose LOW and HIGH legs have
distinct mechanisms (oversold-in-calm vs overbought-in-stress). They must be
killable INDEPENDENTLY (spec C8 per-leg kill), so this producer computes the
conditional forward-return sign for each leg SEPARATELY on the train artifact:

  LOW  leg: zscore_48 < THETA_Z_LOW (-1) AND low-vol regime  -> mean-revert: expect UP (positive fwd ret)
  HIGH leg: zscore_48 > THETA_Z_HIGH (+1) AND high-vol regime -> TREND sign-flip: expect continuation UP (positive fwd ret)

H1/H3 are single-leg and produce one sign each. Threshold values (THETA_Z_*) are
Step -1 human-locked and referenced symbolically here.

H3 = decay_trend_persistence (spec D2/§3): long while the fast decay-MA leads
the slow one (decay_linear_close_48 > decay_linear_close_168). Sane iff the
conditional mean forward return is POSITIVE (trend continues UP).

Train-only: callers pass a train-windows frame (Task 25 guards the window).
"""
from __future__ import annotations

import pandas as pd

# Step -1 human-locked hypothesis param values (symbolic; locked in Step -1).
THETA_Z_LOW = -1.0
THETA_Z_HIGH = 1.0
THETA_PUSH = -0.6   # H1 FADES a one-sided DOWN-push -> negative threshold


def _leg_mean_sign(df: pd.DataFrame, mask: pd.Series, fwd_col: str) -> tuple[bool, bool]:
    """Return (population_nonempty, mean_fwd_ret_positive) for a conditional leg.

    Args:
        df: The train frame.
        mask: Boolean Series selecting the conditional leg population.
        fwd_col: Forward-return column name.

    Returns:
        (nonempty, positive): ``nonempty`` is True iff the leg has >= 1 bar;
        ``positive`` is True iff the leg's mean forward return is > 0 (False on
        an empty population).
    """
    sub = df.loc[mask, fwd_col]
    if sub.empty:
        return False, False
    return True, bool(sub.mean() > 0)


def compute_per_leg_mechanism(
    df: pd.DataFrame, fwd_col: str = "fwd_ret"
) -> dict:
    """Compute per-leg + per-hypothesis mechanism-sanity booleans on the train data.

    Args:
        df: Train artifact frame with columns ``zscore_48``,
            ``realized_vol_24h``, ``intrabar_push``, ``volume_zscore_24h`` and
            ``fwd_col``.
        fwd_col: Forward-return column (default ``"fwd_ret"``).

    Returns:
        A dict of booleans:
          - ``h2_low_leg_sane`` / ``h2_high_leg_sane``: leg has population AND
            its conditional mean forward return is POSITIVE (low leg = revert
            UP; high leg = trend-continuation UP — both sane iff fwd ret > 0,
            per spec §3 H2 kill (a)/(b)).
          - ``h2_low_leg_sane_raw_positive`` / ``h2_high_leg_sane_raw_positive``:
            the unadjusted "mean fwd ret > 0" flags (diagnostic).
          - ``h1_sane``: H1 FADES a down-push (intrabar_push < THETA_PUSH); sane
            iff the conditional mean forward return is POSITIVE (reversion UP).
          - ``h3_sane``: H3 = decay_trend_persistence (spec D2/§3) — decay-trend
            cross driver (decay_linear_close_48 > decay_linear_close_168); sane
            iff the conditional mean forward return is POSITIVE (trend continues UP).
    """
    vol_med = df["realized_vol_24h"].median()

    low_mask = (df["zscore_48"] < THETA_Z_LOW) & (df["realized_vol_24h"] <= vol_med)
    high_mask = (df["zscore_48"] > THETA_Z_HIGH) & (df["realized_vol_24h"] > vol_med)

    low_nonempty, low_pos = _leg_mean_sign(df, low_mask, fwd_col)
    high_nonempty, high_pos = _leg_mean_sign(df, high_mask, fwd_col)

    # H2 LOW = mean-reversion (long when z<-1 in low-vol; expect UP, positive).
    # H2 HIGH = TREND sign-flip (long when z>+1 in high-vol; expect continuation
    # UP, positive). Per spec §3 H2 kill (a)/(b), EACH leg is sane iff its
    # conditional mean forward return is > 0 (a wrong-signed leg cannot pass).
    h2_low_sane = bool(low_nonempty and low_pos)
    h2_high_sane = bool(high_nonempty and high_pos)

    # H1: FADE a one-sided down-push (microstructure mean-reversion, spec §3 H1)
    # — long when intrabar_push < THETA_PUSH; sane iff the conditional mean
    # forward return is POSITIVE (reversion UP). NOT continuation (spec §3 H1's
    # kill clause explicitly forbids flipping H1 to momentum).
    h1_mask = df["intrabar_push"] < THETA_PUSH
    h1_nonempty, h1_pos = _leg_mean_sign(df, h1_mask, fwd_col)
    h1_sane = bool(h1_nonempty and h1_pos)

    # H3 (decay_trend_persistence, spec D2/§3): trend leg — long while the fast
    # decay-MA leads the slow one (decay_linear_close_48 > decay_linear_close_168).
    # Sane iff the conditional mean forward return is POSITIVE (trend continues UP).
    h3_mask = df["decay_linear_close_48"] > df["decay_linear_close_168"]
    h3_nonempty, h3_pos = _leg_mean_sign(df, h3_mask, fwd_col)
    h3_sane = bool(h3_nonempty and h3_pos)

    return {
        "h2_low_leg_sane": h2_low_sane,
        "h2_high_leg_sane": h2_high_sane,
        "h2_low_leg_sane_raw_positive": low_pos,
        "h2_high_leg_sane_raw_positive": high_pos,
        "h2_low_leg_population": int(low_mask.sum()),
        "h2_high_leg_population": int(high_mask.sum()),
        "h1_sane": h1_sane,
        "h3_sane": h3_sane,
    }
