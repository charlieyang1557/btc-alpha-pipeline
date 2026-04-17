"""D5 — Baselines in DSL: parity tests.

Phase 2A sign-off gate. Each of the 4 Phase 1 hand-written baselines is
re-expressed as a DSL JSON under ``strategies/dsl_baselines/``. These
tests compile each DSL and run it side-by-side with the hand-written
version on 2024 H1 data (the same range used by D2's TestRoundTripSMA).

Acceptance criteria per baseline:
    - ``total_trades``: exact match
    - ``sharpe_ratio``, ``total_return``, ``max_drawdown``: within 1e-4
      relative tolerance (via ``pytest.approx(expected, rel=1e-4)``)

If any baseline fails, the DSL + factor set is insufficient and Phase 2A
cannot be signed off.

These tests require the canonical raw OHLCV parquet and the feature
parquet to exist on disk. They are skipped (not failed) in CI or
lightweight environments without data.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from backtest.engine import run_backtest
from factors.registry import get_registry
from strategies.baseline.mean_reversion import MeanReversion
from strategies.baseline.momentum import Momentum
from strategies.baseline.sma_crossover import SMACrossover
from strategies.baseline.volatility_breakout import VolatilityBreakout
from strategies.dsl import StrategyDSL
from strategies.dsl_compiler import compile_dsl_to_strategy


RAW_PARQUET = Path(__file__).resolve().parent.parent / "data" / "raw" / "btcusdt_1h.parquet"
FEATURES_PARQUET = (
    Path(__file__).resolve().parent.parent
    / "data" / "features" / "btcusdt_1h_features.parquet"
)
DSL_DIR = Path(__file__).resolve().parent.parent / "strategies" / "dsl_baselines"


_skip = pytest.mark.skipif(
    not RAW_PARQUET.exists() or not FEATURES_PARQUET.exists(),
    reason="requires canonical raw + feature parquets",
)

START = datetime(2024, 1, 1, tzinfo=timezone.utc)
END = datetime(2024, 6, 30, 23, tzinfo=timezone.utc)


def _run(strategy_cls, params=None):
    """Run a strategy on 2024 H1 without writing to the registry."""
    return run_backtest(
        strategy_cls=strategy_cls,
        start_date=START,
        end_date=END,
        strategy_params=params or {},
        write_registry=False,
    )


def _load_dsl(name: str) -> StrategyDSL:
    """Load and validate a DSL JSON from dsl_baselines/."""
    path = DSL_DIR / f"{name}.json"
    raw = json.loads(path.read_text())
    return StrategyDSL.model_validate(raw)


# ---------------------------------------------------------------------------
# Schema validation — each DSL loads without errors
# ---------------------------------------------------------------------------


class TestDslLoadsAndCompiles:
    @pytest.mark.parametrize("name", [
        "sma_crossover", "momentum", "volatility_breakout", "mean_reversion",
    ])
    def test_loads_validates_compiles(self, name, tmp_path):
        dsl = _load_dsl(name)
        reg = get_registry()
        cls = compile_dsl_to_strategy(dsl, reg, manifest_dir=tmp_path)
        assert cls.STRATEGY_NAME is not None
        assert cls.WARMUP_BARS >= 0
        assert len(cls._FACTORS_USED) >= 1


# ---------------------------------------------------------------------------
# Parity tests — hand-written vs DSL-compiled on 2024 H1
# ---------------------------------------------------------------------------


def _assert_parity(baseline_metrics, dsl_metrics, label):
    """Assert exact trade count and 1e-4 relative tolerance on 3 numerics."""
    assert dsl_metrics["total_trades"] == baseline_metrics["total_trades"], (
        f"{label}: trade count mismatch — "
        f"baseline={baseline_metrics['total_trades']}, "
        f"dsl={dsl_metrics['total_trades']}"
    )
    assert dsl_metrics["sharpe_ratio"] == pytest.approx(
        baseline_metrics["sharpe_ratio"], rel=1e-4
    ), (
        f"{label}: sharpe mismatch — "
        f"baseline={baseline_metrics['sharpe_ratio']:.6f}, "
        f"dsl={dsl_metrics['sharpe_ratio']:.6f}"
    )
    assert dsl_metrics["total_return"] == pytest.approx(
        baseline_metrics["total_return"], rel=1e-4
    ), (
        f"{label}: total_return mismatch — "
        f"baseline={baseline_metrics['total_return']:.6f}, "
        f"dsl={dsl_metrics['total_return']:.6f}"
    )
    assert dsl_metrics["max_drawdown"] == pytest.approx(
        baseline_metrics["max_drawdown"], rel=1e-4
    ), (
        f"{label}: max_drawdown mismatch — "
        f"baseline={baseline_metrics['max_drawdown']:.6f}, "
        f"dsl={dsl_metrics['max_drawdown']:.6f}"
    )


@_skip
class TestSMACrossoverParity:
    def test_parity(self, tmp_path):
        baseline = _run(SMACrossover, params={"fast_period": 20, "slow_period": 50})
        dsl = _load_dsl("sma_crossover")
        compiled = compile_dsl_to_strategy(dsl, get_registry(), manifest_dir=tmp_path)
        dsl_result = _run(compiled)
        _assert_parity(baseline.metrics, dsl_result.metrics, "sma_crossover")


@_skip
class TestMomentumParity:
    def test_parity(self, tmp_path):
        baseline = _run(
            Momentum,
            params={"lookback_period": 24, "entry_threshold": 0.02, "exit_threshold": 0.0},
        )
        dsl = _load_dsl("momentum")
        compiled = compile_dsl_to_strategy(dsl, get_registry(), manifest_dir=tmp_path)
        dsl_result = _run(compiled)
        _assert_parity(baseline.metrics, dsl_result.metrics, "momentum")


@_skip
class TestVolatilityBreakoutParity:
    def test_parity(self, tmp_path):
        baseline = _run(
            VolatilityBreakout,
            params={"bb_period": 24, "num_std": 2.0},
        )
        dsl = _load_dsl("volatility_breakout")
        compiled = compile_dsl_to_strategy(dsl, get_registry(), manifest_dir=tmp_path)
        dsl_result = _run(compiled)
        _assert_parity(baseline.metrics, dsl_result.metrics, "volatility_breakout")


@_skip
class TestMeanReversionParity:
    def test_parity(self, tmp_path):
        baseline = _run(
            MeanReversion,
            params={"zscore_period": 48, "entry_z": -2.0, "exit_z": 0.0},
        )
        dsl = _load_dsl("mean_reversion")
        compiled = compile_dsl_to_strategy(dsl, get_registry(), manifest_dir=tmp_path)
        dsl_result = _run(compiled)
        _assert_parity(baseline.metrics, dsl_result.metrics, "mean_reversion")
