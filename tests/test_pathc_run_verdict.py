"""Tests for the Path C verdict RUN wiring (scripts/pathc_run_verdict).

PHASE-D GATING (CRITICAL): the real forward_2026 RUN is a separate Charlie
register (Phase D). ``main()`` MUST refuse to execute unless an explicit
not-yet-set authorization flag is passed; building the orchestrator + unit tests
(mocked engine) is the C4-C7 scope. These tests never run a real backtest:
``_run_backtest`` is mocked so run_verdict exercises the real DSL compile + the
producer + the load_candidate_moments integrity gate + the orchestrator + the
sealed-sha256 invariant — but no real engine / forward_2026 / real data.

Adapted from tests/test_patha_run_verdict.py. Retargeted at pathc_* modules and
the 3 basis hypotheses (H1/H2/H3). The F3 under-determined carve-out and the §37.1
gate are verified.
"""
from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd
import pytest

import scripts.pathc_run_verdict as rv


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
    """A train-window (2020) basis-factor frame for the per-leg tiers to consume."""
    n = 800
    idx = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
    rng = np.random.default_rng(17)
    df = pd.DataFrame({
        "open_time_utc": idx,
        "return_1h": rng.normal(0, 0.01, n),
        # Basis factors
        "basis_pct_rank_2160": rng.uniform(0, 1, n),
        "basis_sign": rng.choice([-1.0, 0.0, 1.0], n),
        "basis_ewm_240_pctrank_2160": rng.uniform(0, 1, n),
        "basis_ewm_480": rng.normal(0, 0.001, n),
        # Price-trend + sizing
        "decay_linear_close_48": rng.normal(100, 5, n),
        "decay_linear_close_168": rng.normal(100, 5, n),
        "cdf_realized_vol_720": rng.uniform(0, 1, n),
    })
    p = tmp_path / "feat.parquet"
    df.to_parquet(p)
    return str(p)


# ---------------------------------------------------------------------------
# PHASE-D GATE
# ---------------------------------------------------------------------------

def test_main_is_phase_d_gated_and_refuses_to_run():
    # main() must NOT execute the real RUN without explicit Phase-D authorization.
    rc = rv.main([])
    assert rc != 0


def test_main_does_not_invoke_run_verdict_while_gated(monkeypatch):
    # Hard proof the gate short-circuits BEFORE any run_verdict / engine touch.
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
        rv.run_verdict(rv.PATHC_VERDICT_DIR)  # no _run_backtest -> must refuse


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
    out = tmp_path / "pathc_verdict_v1"
    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_fake_backtest_result,
    )
    assert bundle["taxonomy"]["advisory_taxonomy"] in (
        "mechanism_refuted", "process_refuted_for_this_grid", "c_positive",
    )
    assert "approximation_tempers" in bundle["taxonomy"]
    assert "verdict_rests_on_weak_sane_only" in bundle["taxonomy"]
    assert bundle["escalation"]["authority"] == "charlie_register"
    assert 0 <= bundle["n_tier5_pass"] <= 3
    assert len(bundle["holdouts"]) == 3
    # C7 CONTRACT GAP 1: TRAIN-window floors are computed (not None) and keyed
    # by hypothesis id with the per-class floor fields.
    assert bundle["floors"] is not None
    assert set(bundle["floors"]) == {"H1", "H2", "H3"}
    assert "eligible" in bundle["floors"]["H1"]
    assert "n_flat_exit_episodes" in bundle["floors"]["H1"]
    assert "zero_fraction" in bundle["floors"]["H2"]
    assert "n_trades" in bundle["floors"]["H2"]
    # C6 CONTRACT GAP 2: basis_marginal is None until C6 is implemented.
    assert bundle["basis_marginal"] is None
    # sealed-artifact invariant recorded + the advisory json written.
    assert "sealed_sha256_invariant" in bundle["meta"]
    assert (out / "pathc_verdict_advisory.json").exists()
    written = json.loads((out / "pathc_verdict_advisory.json").read_text())
    assert written["taxonomy"]["advisory_taxonomy"] == bundle["taxonomy"]["advisory_taxonomy"]


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
    from backtest.pathc_eval_gauntlet import build_h1_dsl

    floors = rv.compute_train_floors(
        hypotheses={"H1": build_h1_dsl()},
        run_backtest_fn=lambda **kw: _train_mock(250),
        train_windows=rv.load_train_windows(),
        git_sha="TEST",
    )
    assert floors["H1"]["eligible"] is True
    assert floors["H1"]["n_flat_exit_episodes"] == 250


def test_compute_train_floors_h1_under_floor_is_indeterminate():
    from backtest.pathc_eval_gauntlet import build_h1_dsl

    floors = rv.compute_train_floors(
        hypotheses={"H1": build_h1_dsl()},
        run_backtest_fn=lambda **kw: _train_mock(50),  # < 200
        train_windows=rv.load_train_windows(),
        git_sha="TEST",
    )
    assert floors["H1"]["eligible"] is False
    assert floors["H1"]["n_flat_exit_episodes"] == 50


def test_compute_train_floors_h2_uses_zero_fraction_and_trade_count():
    from backtest.pathc_eval_gauntlet import build_h2_dsl, build_h3_dsl

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


def test_compute_train_floors_h1_excludes_window_gap_boundary_episode():
    """Window-gap boundary fix: a trade entering in 2021 train but exiting in the
    2022 holdout produces a spurious long->flat at the 2021->2023 discontinuity.
    The per-window episode counting must exclude that artifact."""
    from backtest.pathc_eval_gauntlet import build_h1_dsl

    def _boundary_mock(**kw):
        idx = pd.date_range("2020-01-01", "2023-12-31 23:00", freq="h", tz="UTC")

        def _iso(ts: str) -> str:
            return pd.Timestamp(ts, tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")

        trades = [
            # (a) genuine within-2021 long->flat (real defensive flat-exit).
            {"entry_time_utc": _iso("2021-06-01 00:00"),
             "exit_time_utc": _iso("2021-06-01 05:00")},
            # (b) spurious boundary: enters late-2021 train, exits 2022 holdout.
            {"entry_time_utc": _iso("2021-12-31 20:00"),
             "exit_time_utc": _iso("2022-03-15 00:00")},
        ]

        class _R:
            pass

        r = _R()
        r.run_id = "boundary"
        r.equity_curve = pd.Series(
            10_000.0 * (1 + 1e-6) ** np.arange(len(idx)), index=idx
        )
        r.trades = trades
        r.metrics = {"sharpe_ratio": 0.0, "total_trades": len(trades)}
        r.start_date = idx[0].to_pydatetime()
        r.end_date = idx[-1].to_pydatetime()
        return r

    floors = rv.compute_train_floors(
        hypotheses={"H1": build_h1_dsl()},
        run_backtest_fn=_boundary_mock,
        train_windows=rv.load_train_windows(),
        git_sha="TEST",
    )
    assert floors["H1"]["n_flat_exit_episodes"] == 1, (
        "the across-window-gap long->flat transition (a trade exiting in the excluded "
        "2022 holdout) must NOT count as an H1 defensive flat-exit episode"
    )


# ---------------------------------------------------------------------------
# Sealed tier6_dsr_v1/ byte-invariance (4/4) — the pathc reuse must NOT touch it.
# ---------------------------------------------------------------------------

_SEALED_TIER6_SHA256 = {
    "tier6_dsr_companion.csv": "0a7d98acfb5791c52c6a6d15bd6285a5a4450a4b6ccc113ac165035616666612",
    "tier6_dsr_results.csv": "8eecc6cd50344e32b25880ac16db3489b24ef65e0095f249039841fbf801acac",
    "tier6_mc_validation.json": "49646c303c9329ad2a9b15be819d5cf8a1101fc1e09b3997aa693c4c06ea2acd",
    "tier6_promotion_list.json": "1803eb44812ba89e7c881e7dfec110d8403e08a232aa4e07acf4881b0093e699",
}


def test_sealed_tier6_dsr_v1_sha256_is_4_of_4_unchanged():
    """The Path C harness reuses tier6_dsr but must NEVER mutate the sealed cohort.
    Assert all 4 sealed tier6_dsr_v1 artifacts are byte-identical to the LOCK baseline."""
    import hashlib

    sealed = rv.PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1"
    if not sealed.exists():
        pytest.skip("sealed tier6_dsr_v1 dir not present in this checkout")
    for fn, expected in _SEALED_TIER6_SHA256.items():
        got = hashlib.sha256((sealed / fn).read_bytes()).hexdigest()
        assert got == expected, f"sealed {fn} sha256 drifted: {got} != {expected}"
