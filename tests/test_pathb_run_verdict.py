"""Tests for the Path B verdict RUN wiring (scripts/pathb_run_verdict).

The engine backtest + Step-0 are mocked so these never touch real verdict data;
everything else (cost-equivalence guard, real DSL compile, the producer, the
load_candidate_moments integrity gate, the orchestrator, the sealed-sha256
invariant) runs for real.
"""
from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd
import pytest

import scripts.pathb_run_verdict as rv


_counter = itertools.count()


def _fake_backtest_result(**kwargs):
    """A non-degenerate BacktestResult stand-in (varied per call)."""
    rng = np.random.default_rng(next(_counter) + 1)
    n = 320
    idx = pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC")
    rets = rng.normal(0.0001, 0.012, n)
    eq = pd.Series(10_000.0 * np.cumprod(1.0 + rets), index=idx)

    class _R:
        pass

    r = _R()
    r.run_id = f"run_{rng.integers(1_000_000)}"
    r.equity_curve = eq
    r.metrics = {
        "sharpe_ratio": float(rng.normal(0.0, 0.3)),
        "total_trades": int(rng.integers(5, 60)),
        "max_drawdown": 0.1,
        "total_return": 0.02,
    }
    r.start_date = idx[0].to_pydatetime()
    r.end_date = idx[-1].to_pydatetime()
    return r


def _fake_step0(**kwargs):
    return {
        "rows": [
            {"hypothesis_hash": "dead1", "pass_B": False, "deflated_z": -1.2, "sr_per_bar": -0.01},
            {"hypothesis_hash": "dead2", "pass_B": False, "deflated_z": -0.4, "sr_per_bar": 0.0},
        ],
        "n_star": 3,
        "read_only": True,
        "promotion_side_effect": False,
    }


def _tiny_features(tmp_path) -> str:
    """A train-window (2020) factor frame the per-leg sanity can consume."""
    n = 600
    idx = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
    rng = np.random.default_rng(7)
    df = pd.DataFrame({
        "open_time_utc": idx,
        "return_1h": rng.normal(0, 0.01, n),
        "zscore_48": rng.normal(0, 1.5, n),
        "realized_vol_24h": rng.uniform(0.005, 0.05, n),
        "cdf_realized_vol_720": rng.uniform(0, 1, n),
        "intrabar_push": rng.uniform(-1, 1, n),
        "decay_linear_close_48": rng.normal(100, 5, n),
        "decay_linear_close_168": rng.normal(100, 5, n),
    })
    p = tmp_path / "feat.parquet"
    df.to_parquet(p)
    return str(p)


def test_step0_lifted_any_logic():
    # AMENDMENT (Charlie register 2026-05-31): a 'lift' requires DSR-SIGNIFICANCE
    # (pass_B), NOT a mere point-estimate excess (deflated_z_B > 0).
    assert rv._step0_lifted_any([{"pass_B": False, "deflated_z_B": -1.0}]) is False
    assert rv._step0_lifted_any([{"pass_B": True, "deflated_z_B": -1.0}]) is True
    # point-estimate excess > 0 but NOT significant -> NOT a lift (the amendment)
    assert rv._step0_lifted_any([{"pass_B": False, "deflated_z_B": 0.3}]) is False
    # an insignificant point estimate never lifts, regardless of key naming
    assert rv._step0_lifted_any([{"pass_B": False, "deflated_z": 0.3}]) is False


def test_run_verdict_refuses_sealed_out_dir():
    with pytest.raises(ValueError, match="sealed"):
        rv.run_verdict(rv.SEALED_DIRS[0])


def test_run_verdict_integration_mocked_engine(tmp_path):
    out = tmp_path / "pathb_verdict_v1"
    bundle = rv.run_verdict(
        out,
        features_path=_tiny_features(tmp_path),
        _run_backtest=_fake_backtest_result,
        _run_step0=_fake_step0,
    )
    # advisory bundle shape
    assert bundle["taxonomy"]["advisory_taxonomy"] in (
        "mechanism_refuted", "process_refuted_for_this_grid", "b_positive",
    )
    assert "approximation_tempers" in bundle["taxonomy"]
    assert bundle["escalation"]["authority"] == "charlie_register"
    assert 0 <= bundle["n_tier5_pass"] <= 3
    # 3 candidates compiled + scored
    assert len(bundle["holdouts"]) == 3
    # sealed-artifact invariant recorded + the advisory json written
    assert "sealed_sha256_invariant" in bundle["meta"]
    assert (out / "pathb_verdict_advisory.json").exists()
    written = json.loads((out / "pathb_verdict_advisory.json").read_text())
    assert written["taxonomy"]["advisory_taxonomy"] == bundle["taxonomy"]["advisory_taxonomy"]
