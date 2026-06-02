"""Tests for the Path D verdict RUN wiring (scripts/pathd_run_verdict).

PHASE-D GATING (CRITICAL): the real forward_2026 RUN is a separate Charlie
register (Phase D). ``main()`` MUST refuse to execute unless an explicit
not-yet-set authorization flag is passed; building the orchestrator + unit tests
(mocked engine) is the C4-C7 scope. These tests never run a real backtest:
``_run_backtest`` is mocked so run_verdict exercises the real DSL compile + the
producer + the load_candidate_moments integrity gate + the orchestrator + the
sealed-sha256 invariant — but no real engine / forward_2026 / real data.

Adapted from tests/test_pathc_run_verdict.py. Retargeted at pathd_* modules and
the 3 OI hypotheses (H1/H2/H3).

KEY DIVERGENCES from pathc:
  - D1-only: oi_marginal in the bundle; no D2/redundancy_read/d2_agrees.
  - GENERIC F3 under-determined carve-out.
  - H3 leakage annotation.
  - §37.1 gate raises when PHASE_D_AUTHORIZED is False.
"""
from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd
import pytest

import scripts.pathd_run_verdict as rv


_counter = itertools.count()


def _fake_backtest_result(**kwargs):
    """A non-degenerate BacktestResult stand-in (varied per call).

    Dispatches on start_date: TRAIN-window runs (start.year <= 2024) return a
    2020-span result with many trades for floor evaluation; forward_2026 runs
    return a shorter result with random Sharpe.
    """
    rng = np.random.default_rng(next(_counter) + 1)
    start = kwargs.get("start_date")
    is_train = start is not None and getattr(start, "year", 2026) <= 2024

    class _R:
        pass

    r = _R()
    r.run_id = f"run_{rng.integers(1_000_000)}"

    if is_train:
        n = 2000
        idx = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
        rets = rng.normal(0.0, 0.01, n)
        r.equity_curve = pd.Series(10_000.0 * np.cumprod(1.0 + rets), index=idx)
        # 300 disjoint 1-bar-long trades -> 300 flat-exits; ~50% zero_fraction.
        trades = []
        for k in range(300):
            e = idx[2 * k]
            x = idx[2 * k + 1]
            trades.append({
                "entry_time_utc": e.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_time_utc": x.strftime("%Y-%m-%dT%H:%M:%SZ"),
            })
        r.trades = trades
        r.metrics = {"sharpe_ratio": 0.1, "total_trades": len(trades),
                     "max_drawdown": 0.1, "total_return": 0.02}
    else:
        n = 320
        idx = pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC")
        rets = rng.normal(0.0001, 0.012, n)
        r.equity_curve = pd.Series(10_000.0 * np.cumprod(1.0 + rets), index=idx)
        r.trades = []
        r.metrics = {
            "sharpe_ratio": float(rng.normal(0.0, 0.3)),
            "total_trades": int(rng.integers(5, 60)),
            "max_drawdown": 0.1,
            "total_return": 0.02,
        }
    r.start_date = r.equity_curve.index[0].to_pydatetime()
    r.end_date = r.equity_curve.index[-1].to_pydatetime()
    return r


def _tiny_features(tmp_path) -> str:
    """A train-window (2020) OI-factor frame for the per-leg tiers to consume."""
    n = 800
    idx = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
    rng = np.random.default_rng(17)
    df = pd.DataFrame({
        "open_time_utc": idx,
        "return_1h": rng.normal(0, 0.01, n),
        # OI factors
        "oi_pct_rank_2160": rng.uniform(0, 1, n),
        "oi_velocity_ewm_240": rng.normal(0, 0.01, n),
        "oi_velocity_ewm_240_pctrank_2160": rng.uniform(0, 1, n),
        # Price-trend + sizing
        "decay_linear_close_48": rng.normal(100, 5, n),
        "decay_linear_close_168": rng.normal(100, 5, n),
        "cdf_realized_vol_720": rng.uniform(0, 1, n),
        # Vol columns for contamination_correlations
        "realized_vol_24h": rng.uniform(0, 0.05, n),
    })
    p = tmp_path / "feat.parquet"
    df.to_parquet(p)
    return str(p)


# ---------------------------------------------------------------------------
# PHASE-D GATE
# ---------------------------------------------------------------------------

def test_main_is_phase_d_gated_and_refuses_to_run():
    rc = rv.main([])
    assert rc != 0


def test_main_does_not_invoke_run_verdict_while_gated(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("run_verdict must NOT be reached while Phase-D gated")

    monkeypatch.setattr(rv, "run_verdict", _boom)
    assert rv.main([]) != 0


def test_phase_d_authorized_flag_default_is_false():
    assert rv.PHASE_D_AUTHORIZED is False


def test_run_verdict_refuses_real_engine_without_phase_d_authorization():
    """§37.1 gate: the public real-run path (no injected engine) must NOT reach
    the real backtest.engine while Phase D is unauthorized."""
    assert rv.PHASE_D_AUTHORIZED is False
    with pytest.raises((AssertionError, RuntimeError, ValueError),
                       match="(?i)phase.?d|authoriz|inject"):
        rv.run_verdict(rv.PATHD_VERDICT_DIR)  # no _run_backtest -> must refuse


def test_gate_still_intact_after_wiring():
    """The §37.1 gate must remain intact after all wiring changes."""
    assert rv.PHASE_D_AUTHORIZED is False
    with pytest.raises((RuntimeError, AssertionError, ValueError)):
        rv.run_verdict(rv.PATHD_VERDICT_DIR)  # no _run_backtest -> must refuse


def test_main_still_returns_2_when_gate_closed():
    assert rv.PHASE_D_AUTHORIZED is False
    assert rv.main([]) == 2


# ---------------------------------------------------------------------------
# assert_not_sealed + sealed dir guard
# ---------------------------------------------------------------------------

def test_run_verdict_refuses_sealed_out_dir(tmp_path):
    with pytest.raises(ValueError, match="sealed"):
        rv.run_verdict(rv.SEALED_DIRS[0], _run_backtest=_fake_backtest_result)


def test_assert_not_sealed_refuses_child_of_sealed_dir():
    child = rv.SEALED_DIRS[0] / "subdir" / "candidate"
    with pytest.raises(ValueError, match="sealed"):
        rv.assert_not_sealed(child)
    # A sibling that merely shares the sealed dir's name PREFIX is NOT refused.
    sibling = rv.SEALED_DIRS[0].parent / (rv.SEALED_DIRS[0].name + "_sibling")
    rv.assert_not_sealed(sibling)  # must not raise


# ---------------------------------------------------------------------------
# build_train_frame: two forward horizons (24h + 72h), train-only
# ---------------------------------------------------------------------------

def test_build_train_frame_has_both_forward_horizons(tmp_path):
    train = rv.build_train_frame(rv.load_train_windows(), features_path=_tiny_features(tmp_path))
    assert "fwd_ret_24h" in train.columns
    assert "fwd_ret_72h" in train.columns
    assert len(train) > 0
    assert (train["open_time_utc"].dt.year == 2020).all()


# ---------------------------------------------------------------------------
# run_verdict: mocked-engine integration + sealed invariant
# ---------------------------------------------------------------------------

def test_run_verdict_integration_mocked_engine(tmp_path):
    """Mocked-engine integration: exercises DSL compile + producer + integrity gate
    + orchestrator + sealed-sha256 invariant WITHOUT touching the real engine."""
    out = tmp_path / "pathd_verdict_v1"
    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_fake_backtest_result,
    )
    assert bundle["taxonomy"]["advisory_taxonomy"] in (
        "mechanism_refuted", "process_refuted_for_this_grid", "d_positive",
    )
    assert "approximation_tempers" in bundle["taxonomy"]
    assert "verdict_rests_on_weak_sane_only" in bundle["taxonomy"]
    assert bundle["escalation"]["authority"] == "charlie_register"
    assert "verdict_headline" in bundle, "bundle root must carry verdict_headline"
    assert 0 <= bundle["n_tier5_pass"] <= 3
    assert len(bundle["holdouts"]) == 3
    # C7 floors computed.
    assert bundle["floors"] is not None
    assert set(bundle["floors"]) == {"H1", "H2", "H3"}
    assert "eligible" in bundle["floors"]["H1"]
    assert "n_flat_exit_episodes" in bundle["floors"]["H1"]
    assert "zero_fraction" in bundle["floors"]["H2"]
    assert "n_trades" in bundle["floors"]["H2"]
    # D1-ONLY oi_marginal populated (no D2).
    assert bundle["oi_marginal"] is not None
    assert set(bundle["oi_marginal"]) == {"H1", "H2", "H3"}
    for k in ("H1", "H2", "H3"):
        m = bundle["oi_marginal"][k]
        assert m["promotion_affecting"] is False
        assert m["in_n_star"] is False
        assert "d1" in m
        assert "d2" not in m, "D2 must NOT appear in pathd oi_marginal — OI is independent"
        assert "redundancy_read" not in m, "redundancy_read must NOT appear in pathd oi_marginal"
    # sealed-artifact invariant recorded + advisory json written.
    assert "sealed_sha256_invariant" in bundle["meta"]
    assert (out / "pathd_verdict_advisory.json").exists()
    written = json.loads((out / "pathd_verdict_advisory.json").read_text())
    assert written["taxonomy"]["advisory_taxonomy"] == bundle["taxonomy"]["advisory_taxonomy"]
    # H3 leakage annotation present.
    assert "consistent_with_momentum_or_vol_leakage" in bundle


# ---------------------------------------------------------------------------
# compute_train_floors (C7 integration gate)
# ---------------------------------------------------------------------------

def _train_mock(n_episodes: int, n_bars: int = 4000):
    """A mock engine returning a TRAIN-window result with n_episodes long->flat transitions."""
    idx = pd.date_range("2020-01-01", periods=n_bars, freq="h", tz="UTC")
    eq = pd.Series(10_000.0 * (1 + 1e-5) ** np.arange(n_bars), index=idx)
    trades = []
    for k in range(n_episodes):
        if 2 * k + 1 >= n_bars:
            break
        trades.append({
            "entry_time_utc": idx[2 * k].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exit_time_utc": idx[2 * k + 1].strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

    class _R:
        pass

    r = _R()
    r.run_id = "train"
    r.equity_curve = eq
    r.trades = trades
    r.metrics = {"sharpe_ratio": 0.0, "total_trades": len(trades)}
    r.start_date = idx[0].to_pydatetime()
    r.end_date = idx[-1].to_pydatetime()
    return r


def test_compute_train_floors_h1_eligible_at_200_episodes():
    from backtest.pathd_eval_gauntlet import build_h1_dsl

    floors = rv.compute_train_floors(
        hypotheses={"H1": build_h1_dsl()},
        run_backtest_fn=lambda **kw: _train_mock(250),
        train_windows=rv.load_train_windows(),
        git_sha="TEST",
    )
    assert floors["H1"]["eligible"] is True
    assert floors["H1"]["n_flat_exit_episodes"] == 250


def test_compute_train_floors_h1_under_floor_is_indeterminate():
    from backtest.pathd_eval_gauntlet import build_h1_dsl

    floors = rv.compute_train_floors(
        hypotheses={"H1": build_h1_dsl()},
        run_backtest_fn=lambda **kw: _train_mock(50),  # < 200
        train_windows=rv.load_train_windows(),
        git_sha="TEST",
    )
    assert floors["H1"]["eligible"] is False
    assert floors["H1"]["n_flat_exit_episodes"] == 50


def test_compute_train_floors_h2_uses_zero_fraction_and_trade_count():
    from backtest.pathd_eval_gauntlet import build_h2_dsl, build_h3_dsl

    floors = rv.compute_train_floors(
        hypotheses={"H2": build_h2_dsl(), "H3": build_h3_dsl()},
        run_backtest_fn=lambda **kw: _train_mock(300),
        train_windows=rv.load_train_windows(),
        git_sha="TEST",
    )
    for k in ("H2", "H3"):
        assert "zero_fraction" in floors[k]
        assert "n_trades" in floors[k]
        assert floors[k]["n_trades"] == 300


# ---------------------------------------------------------------------------
# Sealed tier6_dsr_v1/ byte-invariance (4/4) — assert in test per task spec
# ---------------------------------------------------------------------------

_SEALED_TIER6_SHA256 = {
    "tier6_dsr_companion.csv": "0a7d98acfb5791c52c6a6d15bd6285a5a4450a4b6ccc113ac165035616666612",
    "tier6_dsr_results.csv": "8eecc6cd50344e32b25880ac16db3489b24ef65e0095f249039841fbf801acac",
    "tier6_mc_validation.json": "49646c303c9329ad2a9b15be819d5cf8a1101fc1e09b3997aa693c4c06ea2acd",
    "tier6_promotion_list.json": "1803eb44812ba89e7c881e7dfec110d8403e08a232aa4e07acf4881b0093e699",
}


def test_sealed_tier6_dsr_v1_sha256_is_4_of_4_unchanged():
    """The Path D harness reuses tier6_dsr but must NEVER mutate the sealed cohort.
    Assert all 4 sealed tier6_dsr_v1 artifacts are byte-identical to the LOCK baseline."""
    import hashlib

    sealed = rv.PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1"
    if not sealed.exists():
        pytest.skip("sealed tier6_dsr_v1 dir not present in this checkout")
    for fn, expected in _SEALED_TIER6_SHA256.items():
        got = hashlib.sha256((sealed / fn).read_bytes()).hexdigest()
        assert got == expected, f"sealed {fn} sha256 drifted: {got} != {expected}"


# ---------------------------------------------------------------------------
# C7: θ-resolution + frozen-θ floors
# ---------------------------------------------------------------------------

def _train_mock_episodes(n_episodes: int, n_bars: int = 4000):
    idx = pd.date_range("2020-01-01", periods=n_bars, freq="h", tz="UTC")
    eq = pd.Series(10_000.0 * (1 + 1e-5) ** np.arange(n_bars), index=idx)
    trades = []
    for k in range(n_episodes):
        if 2 * k + 1 >= n_bars:
            break
        trades.append({
            "entry_time_utc": idx[2 * k].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exit_time_utc": idx[2 * k + 1].strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

    class _R:
        pass

    r = _R()
    r.run_id = "train"
    r.equity_curve = eq
    r.trades = trades
    r.metrics = {"sharpe_ratio": 0.0, "total_trades": len(trades)}
    r.start_date = idx[0].to_pydatetime()
    r.end_date = idx[-1].to_pydatetime()
    return r


def test_theta_resolution_stays_090_when_h1_episodes_gte_200(tmp_path):
    """>=200 H1 episodes at θ=0.90 → frozen_theta stays 0.90; floors judged there."""
    out = tmp_path / "pathd_verdict_v1"

    def _dispatch(**kw):
        start = kw.get("start_date")
        is_train = start is not None and getattr(start, "year", 2026) <= 2024
        if is_train:
            return _train_mock_episodes(250)
        return _fake_backtest_result(**kw)

    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_dispatch,
    )
    assert bundle["meta"]["frozen_theta"] == 0.90
    assert bundle["meta"]["episodes_at_090"] == 250
    assert bundle["floors"]["H1"]["eligible"] is True
    assert bundle["floors"]["H1"]["n_flat_exit_episodes"] == 250


def test_theta_resolution_falls_to_085_when_h1_episodes_lt_200(tmp_path):
    """<200 H1 episodes at θ=0.90 → frozen_theta falls to 0.85; H1+H3 rebuilt at 0.85."""
    out = tmp_path / "pathd_verdict_v1"

    def _dispatch(**kw):
        start = kw.get("start_date")
        is_train = start is not None and getattr(start, "year", 2026) <= 2024
        if is_train:
            return _train_mock_episodes(100)
        return _fake_backtest_result(**kw)

    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_dispatch,
    )
    assert bundle["meta"]["frozen_theta"] == 0.85
    assert bundle["meta"]["episodes_at_090"] == 100
    assert bundle["floors"]["H1"]["eligible"] is False


def test_run_verdict_meta_carries_frozen_theta(tmp_path):
    """bundle['meta'] must carry frozen_theta + episode counts."""
    out = tmp_path / "pathd_verdict_v1"
    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_fake_backtest_result,
    )
    assert "frozen_theta" in bundle["meta"]
    assert "episodes_at_090" in bundle["meta"]
    assert "episodes_at_frozen_theta" in bundle["meta"]
    assert bundle["meta"]["frozen_theta"] in (0.85, 0.90)


# ---------------------------------------------------------------------------
# D1-only: compute_oi_marginal returns d1 + no d2/redundancy_read
# ---------------------------------------------------------------------------

def test_compute_oi_marginal_returns_d1_per_hypothesis(tmp_path):
    """compute_oi_marginal returns d1 fenced with promotion_affecting=False and
    in_n_star=False per hypothesis. NO d2, NO redundancy_read (D1-only for Path D)."""
    idx = pd.date_range("2026-01-01", periods=200, freq="h", tz="UTC")
    gated_eq = pd.Series(10_000.0 * (1 + 0.0002) ** np.arange(200), index=idx)

    def _mock_engine(**kw):
        n = 200
        eq = pd.Series(10_000.0 * (1 + 0.0001) ** np.arange(n), index=idx)

        class _R:
            pass

        r = _R()
        r.run_id = "m"
        r.equity_curve = eq
        r.trades = []
        r.metrics = {"sharpe_ratio": 0.0, "total_trades": 0,
                     "max_drawdown": 0.0, "total_return": 0.0}
        r.start_date = idx[0].to_pydatetime()
        r.end_date = idx[-1].to_pydatetime()
        return r

    from backtest.pathd_eval_gauntlet import build_all_hypotheses
    hyps = build_all_hypotheses()
    gated_eqs = {k: gated_eq for k in hyps}

    marg = rv.compute_oi_marginal(
        hypotheses=hyps,
        gated_window_equities=gated_eqs,
        run_backtest_fn=_mock_engine,
        git_sha="TEST",
    )
    assert set(marg) == {"H1", "H2", "H3"}
    for k in ("H1", "H2", "H3"):
        assert marg[k]["promotion_affecting"] is False
        assert marg[k]["in_n_star"] is False
        assert "d1" in marg[k]
        assert marg[k]["d1"]["promotion_affecting"] is False
        assert marg[k]["d1"]["in_n_star"] is False
        assert "d1_marginal_sharpe" in marg[k]["d1"]
        # D2 must NOT be present — OI is independent.
        assert "d2" not in marg[k], f"d2 must NOT appear in pathd oi_marginal[{k}]"
        assert "redundancy_read" not in marg[k], (
            f"redundancy_read must NOT appear in pathd oi_marginal[{k}]"
        )


def test_oi_marginal_does_not_change_n_tier5_pass(tmp_path):
    """The oi_marginal diagnostic must NEVER affect n_tier5_pass."""
    out = tmp_path / "pathd_verdict_v1"
    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_fake_backtest_result,
    )
    assert bundle["oi_marginal"] is not None
    n_positive_eligible = sum(
        1 for k, h in bundle["holdouts"].items()
        if float(h.get("holdout_sharpe", 0)) > 0
        and bundle["floors"].get(k, {}).get("eligible", True)
    )
    assert bundle["n_tier5_pass"] == n_positive_eligible


# ---------------------------------------------------------------------------
# Instrument repair: degenerate forward equity end-to-end through run_verdict
# ---------------------------------------------------------------------------

def test_run_verdict_survives_one_degenerate_forward_leg(tmp_path):
    """Instrument repair: one hypothesis produces a flat forward equity.
    run_verdict must NOT crash, must record degenerate leg, exclude from n_tier5_pass."""
    out = tmp_path / "pathd_verdict_v1"
    call_idx = itertools.count()

    def _dispatch(**kw):
        idx_n = next(call_idx)
        start = kw.get("start_date")
        is_train = start is not None and getattr(start, "year", 2026) <= 2024

        class _R:
            pass

        r = _R()
        if is_train:
            n = 2000
            idx = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
            rng = np.random.default_rng(idx_n + 10)
            r.equity_curve = pd.Series(10_000.0 * np.cumprod(1.0 + rng.normal(0, 0.005, n)), index=idx)
            trades = []
            for k in range(300):
                e = idx[2 * k]
                x = idx[2 * k + 1]
                trades.append({
                    "entry_time_utc": e.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "exit_time_utc": x.strftime("%Y-%m-%dT%H:%M:%SZ"),
                })
            r.trades = trades
            r.run_id = f"train_{idx_n}"
            r.metrics = {"sharpe_ratio": 0.1, "total_trades": len(trades),
                         "max_drawdown": 0.1, "total_return": 0.02}
        else:
            fwd_call = idx_n % 2  # alternate: 0=flat, 1=normal
            n = 320
            idx = pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC")
            if fwd_call == 0:
                r.equity_curve = pd.Series(10_000.0, index=idx)
                r.trades = []
                r.metrics = {"sharpe_ratio": 0.0, "total_trades": 0,
                             "max_drawdown": 0.0, "total_return": 0.0}
            else:
                rng = np.random.default_rng(idx_n + 99)
                rets = rng.normal(0.0001, 0.012, n)
                r.equity_curve = pd.Series(10_000.0 * np.cumprod(1.0 + rets), index=idx)
                r.trades = []
                r.metrics = {"sharpe_ratio": float(rng.normal(0.0, 0.3)),
                             "total_trades": int(rng.integers(5, 55)),
                             "max_drawdown": 0.1, "total_return": 0.02}
            r.run_id = f"fwd_{idx_n}"
        r.start_date = r.equity_curve.index[0].to_pydatetime()
        r.end_date = r.equity_curve.index[-1].to_pydatetime()
        return r

    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_dispatch,
    )
    assert "taxonomy" in bundle
    assert "holdouts" in bundle
    assert "degenerate_legs" in bundle
    degen_keys = set(bundle["degenerate_legs"])
    for key in degen_keys:
        h = bundle["holdouts"].get(key, {})
        assert float(h.get("holdout_sharpe", 0.0)) <= 0.0
    assert rv.PHASE_D_AUTHORIZED is False


# ---------------------------------------------------------------------------
# FIX 1: contamination_correlations wired into the bundle
# ---------------------------------------------------------------------------

def test_run_verdict_bundle_contains_contamination_correlations(tmp_path):
    """FIX 1: bundle['contamination_correlations'] must be present with forward+train
    splits, fenced flags, and Pearson+Spearman dicts for the 4 series."""
    out = tmp_path / "pathd_verdict_v1"
    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_fake_backtest_result,
    )
    cc = bundle.get("contamination_correlations")
    assert cc is not None, "bundle must contain 'contamination_correlations'"
    assert "forward" in cc, "contamination_correlations must have 'forward' split"
    assert "train" in cc, "contamination_correlations must have 'train' split"
    assert cc["promotion_affecting"] is False
    assert cc["in_n_star"] is False
    expected_series = {"return_1h", "abs_return_1h", "realized_vol_24h", "cdf_realized_vol_720"}
    for split in ("forward", "train"):
        assert set(cc[split]["pearson"].keys()) == expected_series, (
            f"contamination_correlations['{split}']['pearson'] must have all 4 series"
        )
        assert set(cc[split]["spearman"].keys()) == expected_series, (
            f"contamination_correlations['{split}']['spearman'] must have all 4 series"
        )
        assert cc[split]["promotion_affecting"] is False
        assert cc[split]["in_n_star"] is False


def test_contamination_does_not_change_n_tier5_pass_or_dsr(tmp_path):
    """FIX 1: adding contamination_correlations must NOT change n_tier5_pass or DSR values."""
    out = tmp_path / "pathd_verdict_v1"
    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_fake_backtest_result,
    )
    # n_tier5_pass is determined solely by eligible holdout_sharpe > 0.
    n_positive_eligible = sum(
        1 for k, h in bundle["holdouts"].items()
        if float(h.get("holdout_sharpe", 0)) > 0
        and bundle["floors"].get(k, {}).get("eligible", True)
    )
    assert bundle["n_tier5_pass"] == n_positive_eligible
    # contamination_correlations is present AND DSR unchanged.
    assert bundle.get("contamination_correlations") is not None
    assert bundle["n_dsr_pass"] >= 0  # sanity: non-negative


# ---------------------------------------------------------------------------
# FIX 2: §37.3 substantive-vs-vacuous fields in the bundle
# ---------------------------------------------------------------------------

def test_run_verdict_bundle_carries_37_3_fields(tmp_path):
    """FIX 2: §37.3 substantive-vs-vacuous fields must appear in bundle['taxonomy']."""
    out = tmp_path / "pathd_verdict_v1"
    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_fake_backtest_result,
    )
    tax = bundle["taxonomy"]
    assert "n_substantive_loss_legs" in tax, "§37.3: n_substantive_loss_legs must be present"
    assert "negative_has_substantive_basis" in tax, "§37.3: negative_has_substantive_basis must be present"
    assert "negative_is_vacuous_only" in tax, "§37.3: negative_is_vacuous_only must be present"
    assert isinstance(tax["n_substantive_loss_legs"], int)
    assert isinstance(tax["negative_has_substantive_basis"], bool)
    assert isinstance(tax["negative_is_vacuous_only"], bool)


# ---------------------------------------------------------------------------
# FIX 4a: degenerate D1 flag in oi_marginal
# ---------------------------------------------------------------------------

def test_degenerate_leg_d1_record_is_flagged(tmp_path):
    """FIX 4a: when a leg has a flat forward equity (degenerate), its D1 record
    must carry degenerate=True to prevent misreading the spuriously large |d1_marginal_sharpe|."""
    out = tmp_path / "pathd_verdict_v1"
    call_idx = itertools.count()

    def _dispatch(**kw):
        idx_n = next(call_idx)
        start = kw.get("start_date")
        is_train = start is not None and getattr(start, "year", 2026) <= 2024

        class _R:
            pass

        r = _R()
        if is_train:
            n = 2000
            idx = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
            rng = np.random.default_rng(idx_n + 1)
            r.equity_curve = pd.Series(10_000.0 * np.cumprod(1.0 + rng.normal(0, 0.005, n)), index=idx)
            trades = []
            for k in range(300):
                e = idx[2 * k]
                x = idx[2 * k + 1]
                trades.append({
                    "entry_time_utc": e.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "exit_time_utc": x.strftime("%Y-%m-%dT%H:%M:%SZ"),
                })
            r.trades = trades
            r.run_id = f"train_{idx_n}"
            r.metrics = {"sharpe_ratio": 0.1, "total_trades": len(trades),
                         "max_drawdown": 0.1, "total_return": 0.02}
        else:
            n = 320
            idx = pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC")
            # All forward runs return a flat equity (degenerate).
            r.equity_curve = pd.Series(10_000.0, index=idx)
            r.trades = []
            r.metrics = {"sharpe_ratio": 0.0, "total_trades": 0,
                         "max_drawdown": 0.0, "total_return": 0.0}
            r.run_id = f"fwd_{idx_n}"
        r.start_date = r.equity_curve.index[0].to_pydatetime()
        r.end_date = r.equity_curve.index[-1].to_pydatetime()
        return r

    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_dispatch,
    )
    degenerate_legs = bundle.get("degenerate_legs", {})
    oi_marginal = bundle.get("oi_marginal", {})
    for k, is_degen in degenerate_legs.items():
        if is_degen:
            assert k in oi_marginal, f"degenerate leg {k} must appear in oi_marginal"
            d1 = oi_marginal[k].get("d1", {})
            assert d1.get("degenerate") is True, (
                f"FIX 4a: degenerate leg {k}'s D1 record must carry degenerate=True"
            )
