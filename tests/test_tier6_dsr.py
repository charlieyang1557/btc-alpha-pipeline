"""Tests for backtest.tier6_dsr — Tier 6 closed-form DSR evaluation application.

TDD throughout. Synthetic known-value inputs only for the math layer; the
cohort-derivation tests assert membership/composition (factual, not pass/fail).
No real-cohort PASS/FAIL outcome is asserted here.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest
from scipy.stats import kurtosis, skew

from backtest import tier6_dsr as t6


# --------------------------------------------------------------------------
# Shared fixtures / helpers
# --------------------------------------------------------------------------
def _cohort_df() -> pd.DataFrame:
    base = t6.HOLDOUT_DIR / "holdout_results.csv"
    return pd.read_csv(base)


def _synthetic_cm(sr: float, g3: float, g4: float, T: int) -> "t6.CandidateMoments":
    return t6.CandidateMoments("synthetic", "synthetic", "test", sr, g3, g4, T, None)


# ==========================================================================
# Task 1: Cohort derivation
# ==========================================================================
def test_derive_cohort_partitions_39_into_18_and_21():
    df = _cohort_df()
    assert len(df) == 39
    locked, companion = t6.derive_cohort(df)
    assert len(locked) == 18
    assert len(companion) == 21
    assert set(locked).isdisjoint(set(companion))
    assert set(locked) | set(companion) == set(df["hypothesis_hash"])


def test_locked_cohort_theme_composition():
    df = _cohort_df()
    locked, _ = t6.derive_cohort(df)
    sub = df[df["hypothesis_hash"].isin(locked)]
    comp = sub["theme"].value_counts().to_dict()
    assert comp == {"volume_divergence": 6, "momentum": 6,
                    "calendar_effect": 3, "mean_reversion": 2, "volatility_regime": 1}


def test_r21_excluded_are_not_monday_and_in_companion():
    df = _cohort_df()
    locked, companion = t6.derive_cohort(df)
    for h in ("35dcfcfbee4cfafc", "38a1bb228f103c26"):
        assert h in companion
        assert h not in locked


def test_is_monday_pattern():
    assert t6.is_monday_pattern("monday_morning_reversal") is True
    assert t6.is_monday_pattern("weekend_vol_compression_monday_breakout_160") is True
    assert t6.is_monday_pattern("MONDAY_DIP") is True
    assert t6.is_monday_pattern("friday_close_weekend_positioning") is False
    assert t6.is_monday_pattern("ema_crossover_momentum_acceleration") is False


def test_constants_locked_values():
    assert t6.ALPHA == 0.05
    assert t6.N_STAR == 18
    assert t6.EULER_GAMMA == 0.5772156649015329
    assert t6.R21_EXCLUDED == frozenset({"35dcfcfbee4cfafc", "38a1bb228f103c26"})


def test_derive_cohort_raises_on_partition_drift():
    df = _cohort_df()
    # Remove one locked candidate -> partition no longer 18/21 -> raise.
    locked, _ = t6.derive_cohort(df)
    dropped = df[df["hypothesis_hash"] != locked[0]]
    with pytest.raises(ValueError, match="cohort partition drift"):
        t6.derive_cohort(dropped)
