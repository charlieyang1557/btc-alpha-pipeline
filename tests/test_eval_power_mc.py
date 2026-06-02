"""Tests for the Monte-Carlo gate-power validation (backtest/eval_power_mc.py).

The headline test is test_injection_preserves_sampling_variability_regression:
it pins sd(sr_hat) ~= 1/sqrt(T-1) so the advisor-caught BLOCKING DGP bug (a
re-meaning recipe that collapsed sd(sr_hat) to ~2e-17 and produced a falsely-
confirmatory step function) can never silently return.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from backtest import eval_power, eval_power_mc


def test_injection_preserves_sampling_variability_regression():
    """BLOCKING-bug guard: at sr_true=0 the realized sr_hat must carry its full
    ~1/sqrt(T-1) sampling spread, NOT collapse to ~0 (the broken DGP)."""
    T, M = 2527, 4000
    rng = np.random.default_rng(1)
    res = eval_power_mc.detection_rate(
        lambda r: eval_power_mc.inject_iid_gaussian(T, 0.0, r), 0.0, T, M, rng
    )
    expected = 1.0 / math.sqrt(T - 1)  # ~0.0199
    assert res["sr_hat_sd"] == pytest.approx(expected, rel=0.15)
    assert res["sr_hat_sd"] > 0.01  # the broken recipe gave ~2e-17


def test_injection_hits_population_sharpe():
    """E[sr_hat] ~= injected sr_true_pb (adding a constant does not bias level)."""
    T = 2527
    rng = np.random.default_rng(2)
    sr_pb = 4.0 / math.sqrt(8760)
    res = eval_power_mc.detection_rate(
        lambda r: eval_power_mc.inject_iid_gaussian(T, sr_pb, r), 0.0, T, 3000, rng
    )
    assert res["sr_hat_mean"] == pytest.approx(sr_pb, abs=sr_pb * 0.05 + 5e-4)


def test_detection_at_zero_is_alpha_for_nstar1():
    """detection@(true=0) ~= alpha = 5% at N*=1 (sr_star=0 = the raw one-sided
    z(0.95) threshold)."""
    T = 2527
    rng = np.random.default_rng(3)
    ss = eval_power_mc._sr_star_for(1, T)  # 0.0
    res = eval_power_mc.detection_rate(
        lambda r: eval_power_mc.inject_iid_gaussian(T, 0.0, r), ss, T, 4000, rng
    )
    assert 0.03 <= res["detection_rate"] <= 0.07


def test_nstar3_null_is_more_conservative_than_alpha():
    """The DSR multiplicity hurdle (sr_star>0) makes detection@null << 5% at
    N*=3 — the gate is strictly MORE conservative than a raw 5% test under the
    null (an insight, not a bug)."""
    T = 2527
    rng = np.random.default_rng(33)
    ss = eval_power_mc._sr_star_for(3, T)
    res = eval_power_mc.detection_rate(
        lambda r: eval_power_mc.inject_iid_gaussian(T, 0.0, r), ss, T, 4000, rng
    )
    assert res["detection_rate"] < 0.03


def test_iid_detection_at_mde_near_80():
    """Arm-1 self-consistency: detection at the analytical 80%-power MDE ~= 80%."""
    T, n_star = 2527, 1
    ss = eval_power_mc._sr_star_for(n_star, T)
    mde_pb = eval_power.mde_per_bar(ss, T, eval_power_mc.OBS_G3, eval_power_mc.OBS_G4)
    rng = np.random.default_rng(4)
    res = eval_power_mc.detection_rate(
        lambda r: eval_power_mc.inject_iid_gaussian(T, mde_pb, r), ss, T, 4000, rng
    )
    assert 0.74 <= res["detection_rate"] <= 0.86


def test_deployable_1p5_is_below_floor():
    """The wall: a deployable 1.5 ann Sharpe detects far below 50%."""
    T, ppy, n_star = 2527, 8760, 3
    ss = eval_power_mc._sr_star_for(n_star, T)
    sr_pb = 1.5 / math.sqrt(ppy)
    rng = np.random.default_rng(5)
    res = eval_power_mc.detection_rate(
        lambda r: eval_power_mc.inject_iid_gaussian(T, sr_pb, r), ss, T, 4000, rng
    )
    assert res["detection_rate"] < 0.20


def test_bootstrap_arm_recovers_mde():
    """Arm-2 real-data power at the analytical MDE (advisor measured ~80.6% on
    the real fat-tailed/vol-clustered substrate; loose band for seed/block)."""
    T, n_star = 2527, 1
    ss = eval_power_mc._sr_star_for(n_star, T)
    mde_pb = eval_power.mde_per_bar(ss, T, eval_power_mc.OBS_G3, eval_power_mc.OBS_G4)
    source0, sigma_src = eval_power_mc._load_real_returns0()
    rng = np.random.default_rng(6)
    res = eval_power_mc.detection_rate(
        lambda r: eval_power_mc.inject_bootstrap(source0, sigma_src, T, mde_pb, r),
        ss, T, 4000, rng,
    )
    assert 0.68 <= res["detection_rate"] <= 0.90


def test_no_sealed_writer_calls():
    """CONTRACT BOUNDARY: no call to a sealed-dir writer (allow the prohibition
    comment, which is stripped before the scan)."""
    src = (eval_power_mc.PROJECT_ROOT / "backtest/eval_power_mc.py").read_text()
    code = "\n".join(
        ln for ln in src.splitlines() if not ln.lstrip().startswith("#")
    )
    for forbidden in (
        "evaluate_cohort(",
        "emit_artifacts(",
        "bootstrap_sharpe_se(",
        "_read_cohort_csv(",
        "run_cohort_suitability(",
    ):
        assert forbidden not in code


def test_bootstrap_recovers_injected_sharpe():
    """B2-fix guard: resampling the FULL distribution recovers the injected
    population Sharpe. The source-window bug sampled only the first T (COVID)
    bars and gave sr_hat ~0.026 vs the injected ~0.045 (~half)."""
    T = 2527
    src0, sig = eval_power_mc._load_real_returns0()
    sr_pb = 4.0 / math.sqrt(8760)
    rng = np.random.default_rng(8)
    res = eval_power_mc.detection_rate(
        lambda r: eval_power_mc.inject_bootstrap(src0, sig, T, sr_pb, r),
        0.0, T, 3000, rng,
    )
    assert res["sr_hat_mean"] == pytest.approx(sr_pb, rel=0.10)


def test_generalized_resampler_matches_primitive_when_lengths_equal():
    """Pin: the generalized resampler is byte-identical to the tier6 primitive
    when source_len == out_len (the guarantee it is a faithful generalization)."""
    from backtest.tier6_bootstrap import stationary_bootstrap_indices

    T = 500
    a = eval_power_mc._stationary_bootstrap_from_source(
        T, T, 24, np.random.default_rng(7)
    )
    b = stationary_bootstrap_indices(T, 24, np.random.default_rng(7))
    assert np.array_equal(a, b)
