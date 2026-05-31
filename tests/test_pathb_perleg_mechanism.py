# tests/test_pathb_perleg_mechanism.py
"""H2 per-leg mechanism_sane producer + H1/H3 signs (feeds C8 per-leg kill)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import backtest.pathb_perleg_mechanism as pm


def _train_frame() -> pd.DataFrame:
    n = 400
    rng = np.random.default_rng(7)
    fast_decay = rng.normal(0.5, 0.1, n)
    slow_decay = rng.normal(0.5, 0.1, n)
    return pd.DataFrame({
        "open_time_utc": pd.date_range("2020-01-01", periods=n, freq="h"),
        "zscore_48": rng.normal(0, 1, n),
        "realized_vol_24h": np.abs(rng.normal(0.02, 0.01, n)),
        "fwd_ret": rng.normal(0, 0.01, n),
        "intrabar_push": rng.normal(0, 0.3, n),     # H1 driver
        "volume_zscore_24h": rng.normal(0, 1, n),   # kept (harmless)
        "decay_linear_close_48": fast_decay,         # H3 fast decay-MA
        "decay_linear_close_168": slow_decay,        # H3 slow decay-MA
    })


def test_per_leg_booleans_present_and_independent():
    out = pm.compute_per_leg_mechanism(_train_frame())
    # H2 split into two independently-killable legs (spec C8).
    assert set(["h2_low_leg_sane", "h2_high_leg_sane"]).issubset(out)
    assert isinstance(out["h2_low_leg_sane"], bool)
    assert isinstance(out["h2_high_leg_sane"], bool)
    # H1 / H3 signs also produced.
    assert "h1_sane" in out and "h3_sane" in out


def test_low_leg_uses_zscore_below_neg1_and_low_vol_only():
    df = _train_frame()
    out = pm.compute_per_leg_mechanism(df)
    vol_med = df["realized_vol_24h"].median()
    low_mask = (df["zscore_48"] < pm.THETA_Z_LOW) & (df["realized_vol_24h"] <= vol_med)
    high_mask = (df["zscore_48"] > pm.THETA_Z_HIGH) & (df["realized_vol_24h"] > vol_med)
    # No overlap between leg masks (disjoint conditional populations).
    assert not (low_mask & high_mask).any()
    # The reported low-leg sign equals the sign of mean fwd_ret over the low mask.
    expected = bool(df.loc[low_mask, "fwd_ret"].mean() > 0)
    assert out["h2_low_leg_sane_raw_positive"] == expected


def test_high_leg_sane_requires_positive_continuation():
    # H2 HIGH is a TREND (sign-flip) leg: long when z>+1 in high-vol, so it is
    # sane iff the conditional mean forward return is POSITIVE (continuation UP).
    # This regression guards against the v2 sign-inversion bug.
    df = _train_frame()
    out = pm.compute_per_leg_mechanism(df)
    vol_med = df["realized_vol_24h"].median()
    high_mask = (df["zscore_48"] > pm.THETA_Z_HIGH) & (df["realized_vol_24h"] > vol_med)
    expected = bool(high_mask.any() and df.loc[high_mask, "fwd_ret"].mean() > 0)
    assert out["h2_high_leg_sane"] == expected


def test_h1_fades_down_push_expects_reversion_not_continuation():
    # Spec §3 H1: H1 FADES a one-sided down-push (long), sane iff reversion UP
    # (positive fwd ret on the intrabar_push < THETA_PUSH population). NOT
    # continuation. Regression against the H1 direction-inversion bug.
    df = _train_frame()
    out = pm.compute_per_leg_mechanism(df)
    h1_mask = df["intrabar_push"] < pm.THETA_PUSH
    expected = bool(h1_mask.any() and df.loc[h1_mask, "fwd_ret"].mean() > 0)
    assert out["h1_sane"] == expected


def test_empty_leg_population_is_not_sane():
    df = _train_frame()
    df["zscore_48"] = 0.0  # no bar satisfies < -1 or > +1
    out = pm.compute_per_leg_mechanism(df)
    assert out["h2_low_leg_sane"] is False
    assert out["h2_high_leg_sane"] is False


def test_sane_true_paths_with_crafted_positive_means():
    # Closes the True-path vacuity gap: with crafted data each leg's conditional
    # population has a POSITIVE mean forward return, so every *_sane must be True.
    # rows 0-3: H2-high (z>1, high-vol) + H1 (push<-0.6) + H3 (fast>slow), all +fwd.
    # rows 4-7: H2-low (z<-1, low-vol), +fwd. rows 8-11: neutral filler.
    df = pd.DataFrame({
        "open_time_utc": pd.date_range("2020-01-01", periods=12, freq="h"),
        "zscore_48":              [2, 2, 2, 2,  -2, -2, -2, -2,  0, 0, 0, 0],
        "realized_vol_24h":       [0.9, 0.9, 0.9, 0.9,  0.1, 0.1, 0.1, 0.1,  0.5, 0.5, 0.5, 0.5],
        "fwd_ret":                [0.02, 0.02, 0.02, 0.02,  0.03, 0.03, 0.03, 0.03,  0.0, 0.0, 0.0, 0.0],
        "intrabar_push":          [-1.0, -1.0, -1.0, -1.0,  0.0, 0.0, 0.0, 0.0,  0.0, 0.0, 0.0, 0.0],
        "volume_zscore_24h":      [1.0, 1.0, 1.0, 1.0,  0.0, 0.0, 0.0, 0.0,  0.0, 0.0, 0.0, 0.0],
        # H3 driver: rows 0-3 fast(2.0) > slow(1.0) => h3_mask True; rows 4-11: 0>0 False.
        "decay_linear_close_48":  [2.0, 2.0, 2.0, 2.0,  0.0, 0.0, 0.0, 0.0,  0.0, 0.0, 0.0, 0.0],
        "decay_linear_close_168": [1.0, 1.0, 1.0, 1.0,  0.0, 0.0, 0.0, 0.0,  0.0, 0.0, 0.0, 0.0],
    })
    out = pm.compute_per_leg_mechanism(df)
    # vol_med = 0.5; high_mask = rows 0-3 (z=2,vol=0.9>0.5), mean fwd 0.02>0 -> True
    assert out["h2_high_leg_sane"] is True
    # low_mask = rows 4-7 (z=-2,vol=0.1<=0.5), mean fwd 0.03>0 -> True
    assert out["h2_low_leg_sane"] is True
    # h1_mask = rows 0-3 (push=-1.0 < -0.6), mean fwd 0.02>0 -> True (reversion UP)
    assert out["h1_sane"] is True
    # h3_mask = rows 0-3 (decay_48=2.0 > decay_168=1.0), mean fwd 0.02>0 -> True
    assert out["h3_sane"] is True
