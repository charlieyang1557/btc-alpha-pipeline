# tests/test_pathd_perleg.py
"""Path D tiered (24h+72h) mechanism-sanity tests (Task C5).

classify_leg(mean_24h, mean_72h, sane_sign) tiers a single-sign leg into
strong_sane (hypothesized sign at BOTH horizons) / weak_sane (at EITHER) /
refuted (neither). H2's sane condition (permissive_mean > derisk_mean AND
permissive_mean > 0) is tiered by classify_h2_leg.

Retargeted at the 3 OI hypotheses (Path D LOCK Pre-registration):
  H1 oi_extreme_fade           — sane sign NEGATIVE (reversal DOWN).
  H2 oi_regime_gate            — sane iff permissive_mean > derisk_mean AND
                                  permissive_mean > 0.
  H3 oi_momentum_continuation  — sane sign POSITIVE (continuation UP).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.pathd_perleg_mechanism import classify_leg, classify_h2_leg


# ---------------------------------------------------------------------------
# classify_leg — strong / weak / refuted (mirrors test_pathc_perleg.py)
# ---------------------------------------------------------------------------


def test_strong_vs_weak_sane():
    # H3 hypothesized sign POSITIVE.
    assert classify_leg(mean_24h=+0.01, mean_72h=+0.02, sane_sign="+")["tier"] == "strong_sane"
    assert classify_leg(mean_24h=+0.01, mean_72h=-0.02, sane_sign="+")["tier"] == "weak_sane"
    assert classify_leg(mean_24h=-0.01, mean_72h=-0.02, sane_sign="+")["tier"] == "refuted"


def test_classify_leg_negative_sane_sign_h1():
    # H1 hypothesized sign NEGATIVE (reversal DOWN).
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
# classify_h2_leg — two-population permissive vs de-risk
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


def test_h2_records_sane_sign_descriptor():
    out = classify_h2_leg(perm_24h=0.02, derisk_24h=0.0, perm_72h=0.03, derisk_72h=0.01)
    assert out["sane_sign"] == "h2_permissive_beats_derisk_and_positive"
