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


def test_load_moments_raises_on_missing_hash():
    # FIX 4: an absent hash must raise ValueError (with the hash in the message),
    # not let .iloc[0] raise a bare IndexError.
    df = _cohort_df()
    with pytest.raises(ValueError, match="no_such_hash_xyz"):
        t6.load_candidate_moments("no_such_hash_xyz", df)


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


# ==========================================================================
# Task 4: Mertens variance + SR* + deflated-z + DSR/PSR + pass rule
# ==========================================================================
def test_mertens_variance_reduces_to_null_at_sr_zero():
    # at SR=0 the skew/kurt terms vanish -> 1/(T-1)
    assert abs(t6.mertens_variance(0.0, 5.0, 80.0, 2491) - 1.0 / 2490) < 1e-15


def test_mertens_variance_guard():
    # A4 (Codex HIGH, supersedes original buggy test):
    # term=0.75 > 0 -> positive, NO raise.
    assert t6.mertens_variance(1.0, 0.0, 0.0, 100) > 0
    # term = 1 - 10 + 0 = -9 < 0 -> raise.
    with pytest.raises(ValueError):
        t6.mertens_variance(2.0, 5.0, 1.0, 100)


def test_mertens_variance_degenerate_t_guard():
    # FIX 1: T must be >= 2 (T-1 division). T=1 and T=0 raise BEFORE any division.
    with pytest.raises(ValueError, match="T must be >= 2"):
        t6.mertens_variance(0.08, 0.0, 3.0, 1)
    with pytest.raises(ValueError, match="T must be >= 2"):
        t6.mertens_variance(0.08, 0.0, 3.0, 0)


def test_mertens_variance_non_finite_sr_guard():
    # FIX 2: non-finite sr (e.g. nan from a flat zero-variance series, 0/0=nan)
    # must raise — the `term <= 0` guard does NOT catch nan (nan <= 0 is False).
    with pytest.raises(ValueError, match="non-finite sr"):
        t6.mertens_variance(float("nan"), 0.0, 3.0, 2491)


def test_evaluate_candidate_degenerate_t_guard():
    # FIX 1: synthetic T=1 candidate propagates the T<2 guard through
    # sr_star -> deflated_z -> mertens_variance.
    with pytest.raises(ValueError, match="T must be >= 2"):
        t6.evaluate_candidate(_synthetic_cm(sr=0.08, g3=0.0, g4=3.0, T=1))


def test_evaluate_candidate_non_finite_sr_guard():
    # FIX 2: a nan sr_per_bar (flat zero-variance return series) raises.
    with pytest.raises(ValueError, match="non-finite sr"):
        t6.evaluate_candidate(_synthetic_cm(sr=float("nan"), g3=0.0, g4=3.0, T=2491))


def test_sr_star_null_scaling():
    er = t6.expected_max_ratio_form_b(18)
    assert abs(t6.sr_star(18, 2491, "B") - math.sqrt(1.0 / 2490) * er) < 1e-12
    er_a = t6.expected_max_ratio_form_a(18)
    assert abs(t6.sr_star(18, 2491, "A") - math.sqrt(1.0 / 2490) * er_a) < 1e-12


def test_sr_star_rejects_unknown_form():
    # FIX 3: unknown form must RAISE, not silently fall back to lenient Form A.
    with pytest.raises(ValueError, match="unknown form"):
        t6.sr_star(18, 2491, "C")


def test_sr_star_degenerate_t_guard():
    # FIX 1: sr_star also guards T < 2 (1/(T-1) division).
    with pytest.raises(ValueError, match="T must be >= 2"):
        t6.sr_star(18, 1, "B")
    with pytest.raises(ValueError, match="T must be >= 2"):
        t6.sr_star(18, 0, "B")


def test_deflated_z_denominator_equals_sqrt_term():
    # A10 DESIGN INVARIANT: sqrt(mertens * (T-1)) == sqrt(term) because
    # mertens = term/(T-1). Assert the denominator equals sqrt(term).
    sr, g3, g4, T = 0.08, 0.5, 10.0, 2491
    term = 1.0 - g3 * sr + ((g4 - 1.0) / 4.0) * sr * sr
    denom = math.sqrt(t6.mertens_variance(sr, g3, g4, T) * (T - 1))
    assert abs(denom - math.sqrt(term)) < 1e-15


def test_dsr_statistic_pass_rule_strong_not_weak():
    # A1 (advisor HIGH-1, supersedes original equivalence test):
    # sr_pass: clean STRONG pass (deflated_z ~ 2.13 >= 1.6449)
    rp = t6.evaluate_candidate(_synthetic_cm(sr=0.08, g3=0.0, g4=3.0, T=2491))
    assert rp["pass_B"] is True
    assert (rp["dsr_statistic_B"] >= 0) == (rp["psr_B"] >= 0.95) == rp["pass_B"]
    # sr_fail: SR_hat > SR* (weak rule WOULD pass) but deflated_z ~ 0.39 < 1.6449
    rf = t6.evaluate_candidate(_synthetic_cm(sr=0.045, g3=0.0, g4=3.0, T=2491))
    assert rf["sr_per_bar"] > rf["sr_star_B"]      # weak rule would pass
    assert rf["pass_B"] is False                    # strong rule fails -> pins strong != weak
    assert rf["psr_B"] < 0.95


def test_evaluate_candidate_emits_both_forms_and_equivalence():
    res = t6.evaluate_candidate(_synthetic_cm(sr=0.08, g3=0.0, g4=3.0, T=2491))
    for form in ("B", "A"):
        assert f"sr_star_{form}" in res
        assert f"deflated_z_{form}" in res
        assert f"psr_{form}" in res
        assert f"dsr_statistic_{form}" in res
        assert f"pass_{form}" in res
        # equivalence: pass <=> dsr_statistic >= 0 <=> psr >= 0.95
        assert (res[f"dsr_statistic_{form}"] >= 0) == res[f"pass_{form}"]
        assert (res[f"psr_{form}"] >= 0.95) == res[f"pass_{form}"]
    assert abs(res["z_pass"] - 1.6449) < 1e-3
    assert res["pass_B"] is True
    # FIX 6: expected-max-ratio keys are uppercase (er_B/er_A), consistent with
    # sr_star_B/psr_B/pass_B. Lowercase er_b/er_a no longer exist.
    assert "er_b" not in res and "er_a" not in res
    assert res["er_B"] == t6.expected_max_ratio_form_b(18)
    assert res["er_A"] == t6.expected_max_ratio_form_a(18)


def test_evaluate_candidate_pass_at_z_pass_threshold():
    # pass_B is True exactly when deflated_z_B >= z(0.95)
    res = t6.evaluate_candidate(_synthetic_cm(sr=0.08, g3=0.0, g4=3.0, T=2491))
    assert (res["deflated_z_B"] >= t6.Z_PASS) == res["pass_B"]
