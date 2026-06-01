# tests/test_pathc_holdout_producer.py
"""Path C producer artifact-layout tests (mock engine — no real backtest).

Adapted from tests/test_patha_holdout_producer.py; retargeted to the Path C
basis cohort (theme="pathc"). The engine is mocked so this never runs a real
forward_2026 backtest.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from backtest.pathc_holdout_producer import produce_candidate_holdout


def _fake_result(run_id: str = "r1"):
    idx = pd.date_range("2026-01-01", periods=50, freq="h", tz="UTC")
    eq = pd.Series(10_000.0 * (1 + 0.0001) ** np.arange(50), index=idx)

    class R:  # minimal BacktestResult stand-in
        pass

    r = R()
    r.run_id = run_id
    r.equity_curve = eq
    r.metrics = {"sharpe_ratio": 0.5, "total_trades": 12, "max_drawdown": 0.1,
                 "total_return": 0.05, "initial_capital": 10_000.0}
    r.trades = []
    r.start_date = idx[0].to_pydatetime()
    r.end_date = idx[-1].to_pydatetime()
    return r


def test_producer_writes_dead18_layout(tmp_path):
    dsl_hash = "abc123"
    out = produce_candidate_holdout(
        hypothesis_hash=dsl_hash,
        name="pathc_h1",
        theme="pathc",
        strategy_cls=object,  # unused — engine is mocked
        window=(datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 4, 16, 7, tzinfo=timezone.utc)),
        cohort_dir=tmp_path,
        execution_config_path="config/execution_phaseb_spot_15bps.yaml",
        _run_backtest=lambda **kw: _fake_result(),
    )
    cand_dir = tmp_path / dsl_hash
    assert (cand_dir / "returns_per_bar.parquet").exists()
    summary = json.loads((cand_dir / "holdout_summary.json").read_text())
    assert summary["evaluation_semantics"] == "single_run_holdout_v1"
    assert summary["theme"] == "pathc"
    # holdout_sharpe is RECOMPUTED on the cropped forward-window slice,
    # not passed through from result.metrics; with WARMUP_BARS=0 (object strategy)
    # there is no prepend so the full _fake_result curve is the window. Assert it
    # equals compute_all_metrics on that same curve.
    from backtest.metrics import compute_all_metrics

    expected = compute_all_metrics(_fake_result().equity_curve, [], 10_000.0)["sharpe_ratio"]
    assert out["holdout_sharpe"] == pytest.approx(expected)
    assert out["row"]["hypothesis_hash"] == dsl_hash
    assert out["row"]["theme"] == "pathc"
    assert "returns_per_bar_sha256" in out["row"]


def test_producer_returns_window_equity_for_marginal_diagnostic(tmp_path):
    # The fenced basis-marginal diagnostic needs the gated strategy's
    # CROPPED forward-window equity curve to pair against the no-basis baseline's
    # equity on the SAME bars. The producer already computes it internally; it must
    # also RETURN it (the gauntlet reuses it so the gated forward run is not
    # duplicated). With WARMUP_BARS=0 (object strategy) there is no prepend, so the
    # returned window equity equals the full _fake_result curve.
    fake = _fake_result()
    out = produce_candidate_holdout(
        hypothesis_hash="we1",
        name="pathc_h1",
        theme="pathc",
        strategy_cls=object,
        window=(datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 4, 16, 7, tzinfo=timezone.utc)),
        cohort_dir=tmp_path,
        execution_config_path="config/execution_phaseb_spot_15bps.yaml",
        _run_backtest=lambda **kw: fake,
    )
    assert "window_equity" in out
    assert isinstance(out["window_equity"], pd.Series)
    # full _fake_result curve is the window when WARMUP_BARS=0.
    pd.testing.assert_series_equal(out["window_equity"], fake.equity_curve)


def test_producer_default_git_sha_is_pathc_build(tmp_path):
    out = produce_candidate_holdout(
        hypothesis_hash="g1",
        name="pathc_h2",
        theme="pathc",
        strategy_cls=object,
        window=(datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 4, 16, 7, tzinfo=timezone.utc)),
        cohort_dir=tmp_path,
        execution_config_path="config/execution_phaseb_spot_15bps.yaml",
        _run_backtest=lambda **kw: _fake_result(),
    )
    assert out["row"]["name"] == "pathc_h2"
    summary = json.loads((tmp_path / "g1" / "holdout_summary.json").read_text())
    assert summary["current_git_sha"] == "PATHC_BUILD"


def test_producer_prepends_warmup_and_evaluates_full_window(tmp_path):
    # The producer must feed the engine PRE-WINDOW history (window_start -
    # WARMUP_BARS bars) so the basis WARMUP_BARS completes BEFORE the forward
    # window, then crop the holdout metrics/artifacts to the forward window only.
    # Without the prepend, ~WARMUP_BARS of the window is consumed as in-window
    # warmup and the holdout covers only window - WARMUP_BARS bars.
    import datetime as _dt

    warmup = 100  # synthetic WARMUP_BARS (the real value is ~2160; small here for speed)
    window_bars = 200
    win_start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    win_end = win_start + _dt.timedelta(hours=window_bars - 1)

    class _WarmStrat:
        WARMUP_BARS = warmup
        STRATEGY_NAME = "pathc_warm"

    seen = {}

    def _mock_engine(**kw):
        # The producer must extend the feed start back by WARMUP_BARS bars.
        seen["start_date"] = kw["start_date"]
        seen["end_date"] = kw["end_date"]
        # Engine returns an equity curve spanning the FULL extended range (prepend +
        # window). The prepend bars are warmup-only and must be cropped out.
        feed_start = kw["start_date"]
        feed_end = kw["end_date"]
        n = int((feed_end - feed_start).total_seconds() // 3600) + 1
        idx = pd.date_range(feed_start, periods=n, freq="h", tz="UTC")
        eq = pd.Series(10_000.0 * (1 + 0.0001) ** np.arange(n), index=idx)

        class R:
            pass

        r = R()
        r.run_id = "warm"
        r.equity_curve = eq
        r.metrics = {"sharpe_ratio": 0.5, "total_trades": 7}
        r.start_date = feed_start
        r.end_date = feed_end
        r.trades = []
        return r

    out = produce_candidate_holdout(
        hypothesis_hash="warm1",
        name="pathc_warm",
        theme="pathc",
        strategy_cls=_WarmStrat,
        window=(win_start, win_end),
        cohort_dir=tmp_path,
        execution_config_path="config/execution_phaseb_spot_15bps.yaml",
        _run_backtest=_mock_engine,
    )
    # Feed start was pushed back by exactly WARMUP_BARS bars; end is the window end.
    assert seen["start_date"] == win_start - _dt.timedelta(hours=warmup)
    assert seen["end_date"] == win_end

    summary = json.loads((tmp_path / "warm1" / "holdout_summary.json").read_text())
    fwm = summary["forward_window_metadata"]
    # The holdout covers the FULL forward window, NOT window - WARMUP_BARS.
    assert fwm["forward_window_start_utc"] == win_start.isoformat()
    assert fwm["forward_window_end_utc"] == win_end.isoformat()
    # T_obs ~ full window (window_bars - 1 for the leading pct_change NaN), NOT
    # window_bars - warmup. The prepend was warmup-only, not evaluated.
    assert fwm["forward_post_warmup_obs"] >= window_bars - 1
    assert fwm["forward_post_warmup_obs"] > window_bars - warmup


def test_producer_zero_warmup_is_unchanged(tmp_path):
    # Regression: a strategy with WARMUP_BARS=0 (or no attribute) must behave as
    # before — feed start == window start (no prepend).
    seen = {}

    def _mock_engine(**kw):
        seen["start_date"] = kw["start_date"]
        return _fake_result()

    win_start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    win_end = datetime(2026, 4, 16, 7, tzinfo=timezone.utc)
    produce_candidate_holdout(
        hypothesis_hash="zw",
        name="pathc_h1",
        theme="pathc",
        strategy_cls=object,  # no WARMUP_BARS attribute -> treated as 0
        window=(win_start, win_end),
        cohort_dir=tmp_path,
        execution_config_path="config/execution_phaseb_spot_15bps.yaml",
        _run_backtest=_mock_engine,
    )
    assert seen["start_date"] == win_start  # no prepend when warmup is 0


def test_producer_raises_on_degenerate_equity(tmp_path):
    idx = pd.date_range("2026-01-01", periods=50, freq="h", tz="UTC")
    flat = pd.Series(10_000.0, index=idx)  # zero-variance -> gamma None

    class R:
        pass

    r = R()
    r.run_id = "r"
    r.equity_curve = flat
    r.metrics = {"sharpe_ratio": 0.0, "total_trades": 0}
    r.start_date = idx[0].to_pydatetime()
    r.end_date = idx[-1].to_pydatetime()
    with pytest.raises(ValueError, match="degenerate per-bar returns"):
        produce_candidate_holdout(
            hypothesis_hash="deg",
            name="pathc_h1",
            theme="pathc",
            strategy_cls=object,
            window=(r.start_date, r.end_date),
            cohort_dir=tmp_path,
            execution_config_path="config/execution_phaseb_spot_15bps.yaml",
            _run_backtest=lambda **kw: r,
        )
