# tests/test_patha_perleg.py
"""Path A tiered (24h+72h) mechanism-sanity tests (Task C5).

classify_leg(mean_24h, mean_72h, sane_sign) tiers a single-sign leg (H1 reversal
sane=NEGATIVE; H3 continuation sane=POSITIVE) into strong_sane (hypothesized sign
at BOTH horizons) / weak_sane (at EITHER) / refuted (neither). H2's sane sign is
the two-population condition permissive_mean > derisk_mean AND permissive_mean > 0,
tiered the same way at both horizons by classify_h2_leg.

The per-leg driver compute_per_leg_tiers evaluates the conditional forward-return
sign at BOTH a 24-bar and a 72-bar horizon on the TRAIN frame (adapts Path B's
_leg_mean_sign to two horizons) and records both horizon signs + the tier.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import backtest.patha_perleg_mechanism as pm
from backtest.patha_perleg_mechanism import classify_leg, classify_h2_leg


# ---------------------------------------------------------------------------
# classify_leg (single-sign legs: H1 NEGATIVE, H3 POSITIVE)
# ---------------------------------------------------------------------------


def test_strong_vs_weak_sane():
    # H3 hypothesized sign POSITIVE
    assert classify_leg(mean_24h=+0.01, mean_72h=+0.02, sane_sign="+")["tier"] == "strong_sane"
    assert classify_leg(mean_24h=+0.01, mean_72h=-0.02, sane_sign="+")["tier"] == "weak_sane"
    assert classify_leg(mean_24h=-0.01, mean_72h=-0.02, sane_sign="+")["tier"] == "refuted"


def test_classify_leg_negative_sane_sign_h1():
    # H1 hypothesized sign NEGATIVE (reversal / de-risk overlay).
    assert classify_leg(mean_24h=-0.01, mean_72h=-0.02, sane_sign="-")["tier"] == "strong_sane"
    assert classify_leg(mean_24h=-0.01, mean_72h=+0.02, sane_sign="-")["tier"] == "weak_sane"
    assert classify_leg(mean_24h=+0.01, mean_72h=+0.02, sane_sign="-")["tier"] == "refuted"


def test_classify_leg_records_both_horizon_signs():
    out = classify_leg(mean_24h=+0.01, mean_72h=-0.02, sane_sign="+")
    assert out["mean_24h"] == 0.01
    assert out["mean_72h"] == -0.02
    assert out["sane_24h"] is True
    assert out["sane_72h"] is False
    assert out["sane_sign"] == "+"


def test_classify_leg_zero_mean_is_not_sane():
    # A zero conditional mean does not match either + or - hypothesized sign.
    assert classify_leg(mean_24h=0.0, mean_72h=0.0, sane_sign="+")["tier"] == "refuted"
    assert classify_leg(mean_24h=0.0, mean_72h=0.0, sane_sign="-")["tier"] == "refuted"


# ---------------------------------------------------------------------------
# classify_h2_leg (two-population: permissive_mean > derisk_mean AND permissive>0)
# ---------------------------------------------------------------------------


def test_h2_strong_when_permissive_beats_derisk_and_positive_at_both():
    out = classify_h2_leg(perm_24h=0.02, derisk_24h=0.0, perm_72h=0.03, derisk_72h=0.01)
    assert out["tier"] == "strong_sane"


def test_h2_weak_when_only_one_horizon():
    # 24h sane (perm>derisk AND perm>0); 72h not (perm <= derisk).
    out = classify_h2_leg(perm_24h=0.02, derisk_24h=0.0, perm_72h=0.01, derisk_72h=0.02)
    assert out["tier"] == "weak_sane"


def test_h2_refuted_when_permissive_not_positive():
    # perm > derisk but perm <= 0 -> not sane at either horizon.
    out = classify_h2_leg(perm_24h=-0.01, derisk_24h=-0.05, perm_72h=-0.02, derisk_72h=-0.06)
    assert out["tier"] == "refuted"


# ---------------------------------------------------------------------------
# compute_per_leg_tiers driver (train frame, two horizons)
# ---------------------------------------------------------------------------


def _train_frame(n: int = 400) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    return pd.DataFrame({
        "open_time_utc": pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC"),
        "funding_pct_rank_270": rng.uniform(0, 1, n),
        "funding_sign": rng.choice([-1.0, 0.0, 1.0], n),
        "funding_ewm_60": rng.normal(0, 0.0001, n),
        "funding_ewm_30_pctrank_270": rng.uniform(0, 1, n),
        "decay_linear_close_48": rng.normal(100, 5, n),
        "decay_linear_close_168": rng.normal(100, 5, n),
        "fwd_ret_24h": rng.normal(0, 0.01, n),
        "fwd_ret_72h": rng.normal(0, 0.01, n),
    })


def test_compute_per_leg_tiers_produces_all_three_with_tiers():
    out = pm.compute_per_leg_tiers(_train_frame())
    assert set(out) == {"H1", "H2", "H3"}
    for leg in out.values():
        assert leg["tier"] in {"strong_sane", "weak_sane", "refuted"}
        assert "mean_24h" in leg or "perm_24h" in leg  # both horizons recorded


def test_compute_per_leg_tiers_h1_uses_negative_sane_sign():
    out = pm.compute_per_leg_tiers(_train_frame())
    assert out["H1"]["sane_sign"] == "-"
    assert out["H3"]["sane_sign"] == "+"


def test_h1_strong_sane_with_crafted_reversal_data():
    # H1 tail population (rank >= 0.90 AND sign > 0) has NEGATIVE forward return at
    # both horizons -> the crowded-long fade is sane at both -> strong_sane.
    n = 100
    rank = np.r_[np.full(50, 0.5), np.full(50, 0.95)]
    sign = np.r_[np.full(50, -1.0), np.full(50, 1.0)]
    fwd = np.r_[np.zeros(50), np.full(50, -0.02)]  # tail bars revert DOWN
    df = pd.DataFrame({
        "open_time_utc": pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC"),
        "funding_pct_rank_270": rank,
        "funding_sign": sign,
        "funding_ewm_60": np.zeros(n),
        "funding_ewm_30_pctrank_270": np.full(n, 0.5),
        "decay_linear_close_48": np.zeros(n),
        "decay_linear_close_168": np.zeros(n),
        "fwd_ret_24h": fwd,
        "fwd_ret_72h": fwd,
    })
    out = pm.compute_per_leg_tiers(df)
    assert out["H1"]["tier"] == "strong_sane"
