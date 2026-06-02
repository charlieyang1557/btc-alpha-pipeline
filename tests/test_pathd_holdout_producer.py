# tests/test_pathd_holdout_producer.py
"""Path D producer artifact-layout tests (mock engine — no real backtest).

Adapted from tests/test_pathc_holdout_producer.py; retargeted to the Path D
OI cohort (theme="pathd"). The engine is mocked so this never runs a real
forward_2026 backtest.

Includes the degenerate-equity guard (inherited from Path C commit 0d06c22d):
a flat / zero-variance equity must NOT raise, and must return degenerate=True.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from backtest.pathd_holdout_producer import produce_candidate_holdout


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
    dsl_hash = "pathd_abc123"
    out = produce_candidate_holdout(
        hypothesis_hash=dsl_hash,
        name="pathd_h1",
        theme="pathd",
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
    assert summary["theme"] == "pathd"
    from backtest.metrics import compute_all_metrics

    expected = compute_all_metrics(_fake_result().equity_curve, [], 10_000.0)["sharpe_ratio"]
    assert out["holdout_sharpe"] == pytest.approx(expected)
    assert out["row"]["hypothesis_hash"] == dsl_hash
    assert out["row"]["theme"] == "pathd"
    assert "returns_per_bar_sha256" in out["row"]


def test_producer_default_git_sha_is_pathd_build(tmp_path):
    out = produce_candidate_holdout(
        hypothesis_hash="g1",
        name="pathd_h2",
        theme="pathd",
        strategy_cls=object,
        window=(datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 4, 16, 7, tzinfo=timezone.utc)),
        cohort_dir=tmp_path,
        execution_config_path="config/execution_phaseb_spot_15bps.yaml",
        _run_backtest=lambda **kw: _fake_result(),
    )
    assert out["row"]["name"] == "pathd_h2"
    summary = json.loads((tmp_path / "g1" / "holdout_summary.json").read_text())
    assert summary["current_git_sha"] == "PATHD_BUILD"


def test_producer_degenerate_returns_flagged_not_raises(tmp_path):
    """Instrument repair (Path C 0d06c22d inherited): a flat/zero-variance forward
    equity must NOT raise. Return degenerate=True, holdout_sharpe=0.0."""
    idx = pd.date_range("2026-01-01", periods=50, freq="h", tz="UTC")
    flat = pd.Series(10_000.0, index=idx)  # zero-variance -> gamma None

    class R:
        pass

    r = R()
    r.run_id = "rdeg"
    r.equity_curve = flat
    r.metrics = {"sharpe_ratio": 0.0, "total_trades": 0}
    r.start_date = idx[0].to_pydatetime()
    r.end_date = idx[-1].to_pydatetime()
    r.trades = []

    out = produce_candidate_holdout(
        hypothesis_hash="deg_pathd",
        name="pathd_h1",
        theme="pathd",
        strategy_cls=object,
        window=(r.start_date, r.end_date),
        cohort_dir=tmp_path,
        execution_config_path="config/execution_phaseb_spot_15bps.yaml",
        _run_backtest=lambda **kw: r,
    )
    assert out["degenerate"] is True
    assert out["holdout_sharpe"] == 0.0
    assert "row" in out
    assert isinstance(out["window_equity"], pd.Series)


def test_producer_degenerate_sharpe_fails_tier5_gate(tmp_path):
    """Degenerate holdout_sharpe=0.0 must NOT pass the strict > 0 Tier-5 gate."""
    idx = pd.date_range("2026-01-01", periods=50, freq="h", tz="UTC")
    flat = pd.Series(10_000.0, index=idx)

    class R:
        pass

    r = R()
    r.run_id = "rdeg2"
    r.equity_curve = flat
    r.metrics = {"sharpe_ratio": 0.0, "total_trades": 0}
    r.start_date = idx[0].to_pydatetime()
    r.end_date = idx[-1].to_pydatetime()
    r.trades = []

    out = produce_candidate_holdout(
        hypothesis_hash="deg2_pathd",
        name="pathd_h2",
        theme="pathd",
        strategy_cls=object,
        window=(r.start_date, r.end_date),
        cohort_dir=tmp_path,
        execution_config_path="config/execution_phaseb_spot_15bps.yaml",
        _run_backtest=lambda **kw: r,
    )
    assert not (out["holdout_sharpe"] > 0)
