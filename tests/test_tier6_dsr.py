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


# ==========================================================================
# Task 2: Moment loader + consume-with-verify (+ A8 sha256 integrity gate)
# ==========================================================================
def test_load_moments_matches_recompute_and_raw_kurtosis():
    df = _cohort_df()
    h = "7abff29fc2f117a1"  # ema_crossover_momentum_acceleration
    cm = t6.load_candidate_moments(h, df)
    # recompute from parquet
    r = pd.read_parquet(t6.HOLDOUT_DIR / h / "returns_per_bar.parquet")["return"]
    rf = r[np.isfinite(r)]
    assert cm.T == len(rf)
    assert abs(cm.gamma3 - float(skew(rf, bias=True))) < t6.MOMENT_RECOMPUTE_EPS
    # RAW kurtosis (3=normal), NOT excess
    assert abs(cm.gamma4 - float(kurtosis(rf, fisher=False, bias=True))) < t6.MOMENT_RECOMPUTE_EPS
    assert abs(cm.gamma4 - float(kurtosis(rf, fisher=True, bias=True))) > 1.0  # != excess
    assert abs(cm.sr_per_bar - rf.mean() / rf.std(ddof=0)) < 1e-12


def test_load_moments_raises_on_stored_recompute_mismatch():
    # if stored gamma deviates from recompute beyond EPS, raise (forensic guard)
    df = _cohort_df()
    h = "7abff29fc2f117a1"
    bad = df.copy()
    bad.loc[bad.hypothesis_hash == h, "gamma4"] = 999.0
    with pytest.raises(ValueError, match="moment mismatch"):
        t6.load_candidate_moments(h, bad)


def test_load_moments_raises_on_t_obs_mismatch():
    df = _cohort_df()
    h = "7abff29fc2f117a1"
    bad = df.copy()
    bad.loc[bad.hypothesis_hash == h, "T_obs"] = 1
    with pytest.raises(ValueError, match="moment mismatch"):
        t6.load_candidate_moments(h, bad)


def test_load_moments_a8_sha256_gate_raises_on_mismatch():
    # A8: verify CSV-stored returns_per_bar_sha256 against on-disk parquet sha256
    # BEFORE recompute; raise on mismatch (artifact-integrity gate).
    df = _cohort_df()
    h = "7abff29fc2f117a1"
    bad = df.copy()
    bad.loc[bad.hypothesis_hash == h, "returns_per_bar_sha256"] = "deadbeef" * 8
    with pytest.raises(ValueError, match="sha256"):
        t6.load_candidate_moments(h, bad)


def test_load_moments_fields_present():
    df = _cohort_df()
    h = "7abff29fc2f117a1"
    cm = t6.load_candidate_moments(h, df)
    assert cm.hypothesis_hash == h
    assert cm.name == "ema_crossover_momentum_acceleration"
    assert cm.theme == "momentum"
    assert cm.trades == 12  # holdout_total_trades
    # frozen dataclass — cannot mutate
    with pytest.raises(Exception):
        cm.gamma3 = 0.0  # type: ignore[misc]


# ==========================================================================
# Task 3: Expected-max ratios (Form A + Form B) + monotonicity + guard
# ==========================================================================
def test_expected_max_ratios_at_18():
    assert abs(t6.expected_max_ratio_form_a(18) - 2.4043) < 1e-3
    assert abs(t6.expected_max_ratio_form_b(18) - 1.8539) < 1e-3


def test_expected_max_ratios_monotonic_increasing():
    for f in (t6.expected_max_ratio_form_a, t6.expected_max_ratio_form_b):
        vals = [f(n) for n in (2, 5, 10, 18, 30)]
        assert all(b > a for a, b in zip(vals, vals[1:]))


def test_form_degenerate_guard():
    with pytest.raises(ValueError):
        t6.expected_max_ratio_form_b(1)
    with pytest.raises(ValueError):
        t6.expected_max_ratio_form_a(1)
    with pytest.raises(ValueError):
        t6.expected_max_ratio_form_b(0)
    with pytest.raises(ValueError):
        t6.expected_max_ratio_form_a(0)
