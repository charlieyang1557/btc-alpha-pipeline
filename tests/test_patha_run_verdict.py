"""Tests for the Path A verdict RUN wiring (scripts/patha_run_verdict).

PHASE-D GATING (CRITICAL): the real forward_2026 RUN is a separate Charlie
register (Phase D). ``main()`` MUST refuse to execute unless an explicit
not-yet-set authorization flag is passed; building the orchestrator + unit tests
(mocked engine) is the C4-C7 scope. These tests never run a real backtest:
``_run_backtest`` is mocked so run_verdict exercises the real DSL compile + the
producer + the load_candidate_moments integrity gate + the orchestrator + the
sealed-sha256 invariant — but no real engine / forward_2026 / 6852-row data.
"""
from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd
import pytest

import scripts.patha_run_verdict as rv


_counter = itertools.count()


def _fake_backtest_result(**kwargs):
    """A non-degenerate BacktestResult stand-in (varied per call).

    The mock dispatches on the engine's ``start_date`` kwarg so the SAME mock can
    serve (a) the forward_2026 gauntlet + baseline runs (2026 window) and (b) the
    TRAIN-window floor runs (2020-2023 span) with distinct, deterministic series.
    """
    rng = np.random.default_rng(next(_counter) + 1)
    start = kwargs.get("start_date")
    is_train = start is not None and getattr(start, "year", 2026) <= 2024

    class _R:
        pass

    r = _R()
    r.run_id = f"run_{rng.integers(1_000_000)}"

    if is_train:
        # TRAIN-window run: a long-ish 2020-2023 span with many trades, so the
        # H1 flat-exit-episode count and H2/H3 zero_fraction + trade-count floors
        # have something to measure. Alternating long/flat -> ~n/4 episodes.
        n = 2000
        idx = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
        rets = rng.normal(0.0, 0.01, n)
        r.equity_curve = pd.Series(10_000.0 * np.cumprod(1.0 + rets), index=idx)
        # Build 300 disjoint long episodes (each 1-bar-long) -> 300 flat-exits,
        # ~half the bars flat -> zero_fraction high but trades >= 200 (eligible by
        # trade count; the run-script decides H1 vs H2/H3 floor per hypothesis).
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
        # forward_2026 window (gauntlet + baseline).
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
    """A train-window (2020) funding-factor frame the per-leg tiers can consume."""
    n = 800
    idx = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
    rng = np.random.default_rng(7)
    df = pd.DataFrame({
        "open_time_utc": idx,
        "return_1h": rng.normal(0, 0.01, n),
        "funding_pct_rank_270": rng.uniform(0, 1, n),
        "funding_sign": rng.choice([-1.0, 0.0, 1.0], n),
        "funding_ewm_60": rng.normal(0, 0.0001, n),
        "funding_ewm_30_pctrank_270": rng.uniform(0, 1, n),
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
    # main() must NOT execute the real RUN without explicit Phase-D authorization;
    # it returns a non-zero gate code (the __main__ wrapper turns it into SystemExit).
    rc = rv.main([])
    assert rc != 0


def test_main_does_not_invoke_run_verdict_while_gated(monkeypatch):
    # Hard proof the gate short-circuits BEFORE any run_verdict / engine touch.
    def _boom(*a, **k):
        raise AssertionError("run_verdict must NOT be reached while Phase-D gated")

    monkeypatch.setattr(rv, "run_verdict", _boom)
    assert rv.main([]) != 0  # gate fires; run_verdict never called


def test_phase_d_authorized_flag_default_is_false():
    assert rv.PHASE_D_AUTHORIZED is False


# ---------------------------------------------------------------------------
# build_train_frame: two forward horizons (24h + 72h), train-only
# ---------------------------------------------------------------------------


def test_build_train_frame_has_both_forward_horizons(tmp_path):
    train = rv.build_train_frame(rv.load_train_windows(), features_path=_tiny_features(tmp_path))
    assert "fwd_ret_24h" in train.columns
    assert "fwd_ret_72h" in train.columns
    assert len(train) > 0
    # train-only: no 2024/2025/2022 rows leaked.
    assert (train["open_time_utc"].dt.year == 2020).all()


# ---------------------------------------------------------------------------
# run_verdict: sealed-dir refusal + mocked-engine integration + sealed invariant
# ---------------------------------------------------------------------------


def test_run_verdict_refuses_sealed_out_dir(tmp_path):
    with pytest.raises(ValueError, match="sealed"):
        rv.run_verdict(rv.SEALED_DIRS[0], _run_backtest=_fake_backtest_result)


def test_assert_not_sealed_refuses_child_of_sealed_dir():
    # FIX 5: a write into a CHILD of a sealed dir must be refused (defense-in-depth;
    # the sha256 check is the backstop). The bare path-equality check only caught the
    # sealed dir itself, not a sub-path under it.
    import os as _os

    child = rv.SEALED_DIRS[0] / "subdir" / "candidate"
    with pytest.raises(ValueError, match="sealed"):
        rv.assert_not_sealed(child)
    # A sibling that merely shares the sealed dir's name PREFIX (not a path child)
    # must NOT be refused (os.sep boundary check, not str startswith).
    sibling = rv.SEALED_DIRS[0].parent / (rv.SEALED_DIRS[0].name + "_sibling")
    rv.assert_not_sealed(sibling)  # must not raise


def test_run_verdict_refuses_real_engine_without_phase_d_authorization():
    # Defense-in-depth: the public real-run path (no injected engine) must NOT
    # reach the real backtest.engine.run_backtest / write artifacts while Phase D
    # is unauthorized. run_verdict requires an injected engine; the ONLY place the
    # REAL engine is wired is behind the PHASE_D_AUTHORIZED gate in main().
    assert rv.PHASE_D_AUTHORIZED is False  # precondition for this guard to fire
    with pytest.raises((AssertionError, RuntimeError, ValueError),
                       match="(?i)phase.?d|authoriz|inject"):
        rv.run_verdict(rv.PATHA_VERDICT_DIR)  # no _run_backtest -> must refuse


def test_run_verdict_integration_mocked_engine(tmp_path):
    # This injects a MOCK engine (_run_backtest), which is the LEGITIMATE unit-test
    # path — it exercises the DSL compile + producer + integrity gate + orchestrator
    # + sealed-sha256 invariant WITHOUT touching the real engine / forward_2026 data.
    # It does NOT bless a real-engine bypass: the real engine is reached only via the
    # PHASE_D_AUTHORIZED gate in main() (see
    # test_run_verdict_refuses_real_engine_without_phase_d_authorization).
    out = tmp_path / "patha_verdict_v1"
    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_fake_backtest_result,
    )
    assert bundle["taxonomy"]["advisory_taxonomy"] in (
        "mechanism_refuted", "process_refuted_for_this_grid", "b_positive",
    )
    assert "approximation_tempers" in bundle["taxonomy"]
    assert "verdict_rests_on_weak_sane_only" in bundle["taxonomy"]
    assert bundle["escalation"]["authority"] == "charlie_register"
    assert 0 <= bundle["n_tier5_pass"] <= 3
    assert len(bundle["holdouts"]) == 3
    # CONTRACT GAP 1 closed: TRAIN-window floors are computed (not None) and keyed
    # by hypothesis id with the per-class floor fields.
    assert bundle["floors"] is not None
    assert set(bundle["floors"]) == {"H1", "H2", "H3"}
    assert "eligible" in bundle["floors"]["H1"]
    assert "n_flat_exit_episodes" in bundle["floors"]["H1"]  # H1 (long-biased) field
    assert "zero_fraction" in bundle["floors"]["H2"]          # H2/H3 (state) fields
    assert "n_trades" in bundle["floors"]["H2"]
    # CONTRACT GAP 2 closed: the fenced funding-marginal diagnostic is computed
    # (not None) and structurally fenced (never promotion-affecting / in N*).
    assert bundle["funding_marginal"] is not None
    assert set(bundle["funding_marginal"]) == {"H1", "H2", "H3"}
    assert all(
        m["promotion_affecting"] is False and m["in_n_star"] is False
        for m in bundle["funding_marginal"].values()
    )
    assert all("funding_marginal_sharpe" in m for m in bundle["funding_marginal"].values())
    # sealed-artifact invariant recorded + the advisory json written.
    assert "sealed_sha256_invariant" in bundle["meta"]
    assert (out / "patha_verdict_advisory.json").exists()
    written = json.loads((out / "patha_verdict_advisory.json").read_text())
    assert written["taxonomy"]["advisory_taxonomy"] == bundle["taxonomy"]["advisory_taxonomy"]


# ---------------------------------------------------------------------------
# CONTRACT GAP 1 — compute_train_floors (TRAIN-window eligibility floors)
# ---------------------------------------------------------------------------


def _train_mock(n_episodes: int, n_bars: int = 4000):
    """A mock engine returning a TRAIN-window result with `n_episodes` long episodes.

    Each episode is a single 1-bar long trade, disjoint from the next (one flat
    bar between), so it yields exactly `n_episodes` long->flat transitions and a
    ~50% zero_fraction over the occupied prefix.
    """
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
    # H1 uses the flat-exit-episode floor (>= 200); 250 episodes -> eligible.
    from backtest.patha_eval_gauntlet import build_h1_dsl

    floors = rv.compute_train_floors(
        hypotheses={"H1": build_h1_dsl()},
        run_backtest_fn=lambda **kw: _train_mock(250),
        train_windows=rv.load_train_windows(),
        git_sha="TEST",
    )
    assert floors["H1"]["eligible"] is True
    assert floors["H1"]["n_flat_exit_episodes"] == 250


def test_compute_train_floors_h1_under_floor_is_indeterminate():
    from backtest.patha_eval_gauntlet import build_h1_dsl

    floors = rv.compute_train_floors(
        hypotheses={"H1": build_h1_dsl()},
        run_backtest_fn=lambda **kw: _train_mock(50),  # < 200
        train_windows=rv.load_train_windows(),
        git_sha="TEST",
    )
    assert floors["H1"]["eligible"] is False
    assert floors["H1"]["n_flat_exit_episodes"] == 50


def test_compute_train_floors_h2_uses_zero_fraction_and_trade_count():
    # H2/H3 use the state-class floor: zero_fraction < 0.50 AND >= 200 trades.
    from backtest.patha_eval_gauntlet import build_h2_dsl, build_h3_dsl

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


def test_compute_train_floors_h2_eligible_when_mostly_long():
    # FIX 2 LOW: exercise the H2/H3 eligible=TRUE path (the existing test only checks
    # the FIELDS, not the eligible-true branch). A DENSE bar index where the strategy
    # is long most of the time -> zero_fraction < 0.50 AND >= 200 trades -> eligible.
    from backtest.patha_eval_gauntlet import build_h2_dsl, build_h3_dsl

    def _dense_train_mock(**kw):
        # ~300 back-to-back trades over a DENSE 2020 index: each trade is 3 bars long
        # (long), separated by a single 1-bar flat -> ~75% long occupancy ->
        # zero_fraction ~0.25 < 0.50; 300 trades >= 200. -> eligible=True.
        n_trades = 300
        n_bars = n_trades * 4 + 16  # dense, all within the 2020 train window
        idx = pd.date_range("2020-01-01", periods=n_bars, freq="h", tz="UTC")
        eq = pd.Series(10_000.0 * (1 + 1e-5) ** np.arange(n_bars), index=idx)
        trades = []
        for k2 in range(n_trades):
            e = idx[4 * k2]
            x = idx[4 * k2 + 3]  # 3-bar long [entry, exit) then 1 flat bar
            trades.append({
                "entry_time_utc": e.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_time_utc": x.strftime("%Y-%m-%dT%H:%M:%SZ"),
            })

        class _R:
            pass

        r = _R()
        r.run_id = "dense_train"
        r.equity_curve = eq
        r.trades = trades
        r.metrics = {"sharpe_ratio": 0.0, "total_trades": len(trades)}
        r.start_date = idx[0].to_pydatetime()
        r.end_date = idx[-1].to_pydatetime()
        return r

    floors = rv.compute_train_floors(
        hypotheses={"H2": build_h2_dsl(), "H3": build_h3_dsl()},
        run_backtest_fn=_dense_train_mock,
        train_windows=rv.load_train_windows(),
        git_sha="TEST",
    )
    for k in ("H2", "H3"):
        assert floors[k]["eligible"] is True, (
            f"{k} must be eligible: zero_fraction={floors[k]['zero_fraction']} (<0.50) "
            f"AND n_trades={floors[k]['n_trades']} (>=200)"
        )
        assert floors[k]["zero_fraction"] < 0.50
        assert floors[k]["n_trades"] == 300


def test_compute_train_floors_h1_excludes_window_gap_boundary_episode():
    # FIX 1 (MEDIUM): a long->flat transition that occurs ACROSS the 2021->2023
    # train-window discontinuity (the excluded-2022 gap) is a window-gap ARTIFACT,
    # NOT a real funding-tail-gate firing, so it must NOT count toward the H1 floor.
    #
    # Synthetic trades over the contiguous 2020->2023 span:
    #   (a) a GENUINE within-2021 long->flat episode (a real defensive flat-exit that
    #       occurs INSIDE a single train window) -> counts;
    #   (b) a trade that ENTERS in late-2021 (train) but EXITS in 2022 (the excluded
    #       holdout): its position is LONG through the last 2021 train bar, then the
    #       next train bar (2023-01-01) is FLAT -> a spurious long->flat at the window
    #       gap (must NOT count).
    # Buggy code counts 2 (genuine + spurious); fixed code counts 1.
    from backtest.patha_eval_gauntlet import build_h1_dsl

    def _boundary_mock(**kw):
        # Hourly bars across the full contiguous train span (incl. 2022, which the
        # floor masks OUT). The equity index spans 2020-01-01 .. 2023-12-31.
        idx = pd.date_range("2020-01-01", "2023-12-31 23:00", freq="h", tz="UTC")

        def _iso(ts: str) -> str:
            return pd.Timestamp(ts, tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")

        trades = [
            # (a) genuine within-2021 long->flat: the trade exits mid-2021 inside the
            # train window -> exactly 1 real defensive flat-exit episode.
            {"entry_time_utc": _iso("2021-06-01 00:00"),
             "exit_time_utc": _iso("2021-06-01 05:00")},   # long->flat at 2021-06-01 05:00
            # (b) spurious boundary: enters late-2021 train, exits in 2022 holdout. The
            # 2022 bars are masked out of train_idx, so the last 2021 bar is LONG and
            # the next train bar 2023-01-01 00:00 is FLAT -> spurious gap transition.
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
    # Only the genuine within-2021 long->flat episode counts; the 2021->2023
    # window-gap artifact (trade (b) exiting in 2022) must NOT add an episode.
    assert floors["H1"]["n_flat_exit_episodes"] == 1, (
        "the across-window-gap long->flat transition (a trade exiting in the excluded "
        "2022 holdout) must NOT count as an H1 defensive flat-exit episode"
    )


# ---------------------------------------------------------------------------
# CONTRACT GAP 2 — compute_funding_marginal (fenced forward diagnostic)
# ---------------------------------------------------------------------------


def test_compute_funding_marginal_pairs_gated_and_baseline_on_forward_bars():
    idx = pd.date_range("2026-01-01", periods=200, freq="h", tz="UTC")
    gated_eq = pd.Series(10_000.0 * (1 + 0.0002) ** np.arange(200), index=idx)

    def _baseline_engine(**kw):
        # the baseline (no-funding) run; flat-ish so the marginal is well-defined.
        b = pd.Series(10_000.0 * (1 + 0.0001) ** np.arange(200), index=idx)

        class _R:
            pass

        r = _R()
        r.run_id = "b"
        r.equity_curve = b
        r.trades = []
        r.metrics = {"sharpe_ratio": 0.0, "total_trades": 0}
        r.start_date = idx[0].to_pydatetime()
        r.end_date = idx[-1].to_pydatetime()
        return r

    gated_equities = {"H1": gated_eq}
    marg = rv.compute_funding_marginal(
        hypotheses={"H1": object()},
        gated_window_equities=gated_equities,
        run_backtest_fn=_baseline_engine,
        git_sha="TEST",
    )
    assert set(marg) == {"H1"}
    assert marg["H1"]["promotion_affecting"] is False
    assert marg["H1"]["in_n_star"] is False
    assert "funding_marginal_sharpe" in marg["H1"]


# ---------------------------------------------------------------------------
# Sealed tier6_dsr_v1/ byte-invariance (4/4) — the reuse must NOT touch it.
# ---------------------------------------------------------------------------

# Frozen baseline sha256 of the 4 sealed tier6_dsr_v1 artifacts (LOCK §baseline).
_SEALED_TIER6_SHA256 = {
    "tier6_dsr_companion.csv": "0a7d98acfb5791c52c6a6d15bd6285a5a4450a4b6ccc113ac165035616666612",
    "tier6_dsr_results.csv": "8eecc6cd50344e32b25880ac16db3489b24ef65e0095f249039841fbf801acac",
    "tier6_mc_validation.json": "49646c303c9329ad2a9b15be819d5cf8a1101fc1e09b3997aa693c4c06ea2acd",
    "tier6_promotion_list.json": "1803eb44812ba89e7c881e7dfec110d8403e08a232aa4e07acf4881b0093e699",
}


def test_sealed_tier6_dsr_v1_sha256_is_4_of_4_unchanged():
    """The Path A harness reuses tier6_dsr but must NEVER mutate the sealed cohort.
    Assert all 4 sealed tier6_dsr_v1 artifacts are byte-identical to the LOCK baseline."""
    import hashlib

    sealed = rv.PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1"
    if not sealed.exists():
        pytest.skip("sealed tier6_dsr_v1 dir not present in this checkout")
    for fn, expected in _SEALED_TIER6_SHA256.items():
        got = hashlib.sha256((sealed / fn).read_bytes()).hexdigest()
        assert got == expected, f"sealed {fn} sha256 drifted: {got} != {expected}"
