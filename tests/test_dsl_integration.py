"""D2 integration tests — compile + run through Backtrader.

These tests are kept separate from :mod:`tests.test_dsl` so the pure
schema/helper suite stays fast. The integration tests here:

- Compile a DSL to a BaseStrategy subclass and run it in Backtrader on
  synthetic data to confirm the crosses_above single-fire contract
  survives the compile + next() path end-to-end (not just at the helper).
- Round-trip the Phase 1 ``SMACrossover`` baseline through the DSL
  compiler and assert parity with the hand-written version
  (total_trades exact; Sharpe/return/max_dd within 1e-4).
- Exercise the manifest drift detector for each of the four drift-sensitive
  fields.
- Test max_hold_bars behavior.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import backtrader as bt
import numpy as np
import pandas as pd
import pytest

from backtest.engine import run_backtest
from factors.registry import FactorRegistry, FactorSpec, get_registry
from strategies.baseline.sma_crossover import SMACrossover
from strategies.dsl import StrategyDSL, canonicalize_dsl, compute_dsl_hash
from strategies.dsl_compiler import (
    ManifestDriftError,
    _build_manifest,
    _compute_compiler_sha,
    _manifest_to_json_dict,
    compile_dsl_to_strategy,
    write_compilation_manifest,
)
from strategies.template import BaseStrategy


# ---------------------------------------------------------------------------
# Top-level test factor compute callables (registry forbids nested funcs)
# ---------------------------------------------------------------------------


def _passthrough_value(df: pd.DataFrame) -> pd.Series:
    """Return the 'value' column verbatim, typed float64.

    Used in synthetic integration tests where the OHLCV feed carries a
    pre-computed factor in a custom column.
    """
    return df["value"].astype("float64")


def _passthrough_other(df: pd.DataFrame) -> pd.Series:
    """Return the 'other' column verbatim, typed float64.

    Companion to :func:`_passthrough_value` for factor-vs-factor tests.
    """
    return df["other"].astype("float64")


# ---------------------------------------------------------------------------
# Helper: build a synthetic feed + features and run the compiled strategy.
# ---------------------------------------------------------------------------


class _OrderCounter(bt.Analyzer):
    """Counts completed buy/sell fills. Simpler than the engine's
    TradeCollector — we don't need trade matching for fire-count tests.
    """

    def __init__(self) -> None:
        super().__init__()
        self.buys: list[datetime] = []
        self.sells: list[datetime] = []

    def notify_order(self, order):
        if order.status != order.Completed:
            return
        dt = bt.num2date(order.executed.dt)
        if order.isbuy():
            self.buys.append(dt)
        else:
            self.sells.append(dt)


def _run_on_synthetic(
    strategy_cls,
    ohlcv: pd.DataFrame,
    extra_cols: dict[str, np.ndarray] | None = None,
) -> _OrderCounter:
    """Run ``strategy_cls`` on ``ohlcv`` through Backtrader.

    ``ohlcv`` must be indexed by naive UTC datetimes with columns
    ``open``, ``high``, ``low``, ``close``, ``volume``. Additional
    lines in ``extra_cols`` (e.g. the ``value`` column for
    factor-vs-scalar tests) are plumbed through as custom Backtrader
    lines so the strategy can still use the feature-parquet override.
    """
    cerebro = bt.Cerebro()
    feed = bt.feeds.PandasData(
        dataname=ohlcv,
        datetime=None,
        open="open", high="high", low="low",
        close="close", volume="volume",
        openinterest=-1,
    )
    cerebro.adddata(feed)
    cerebro.broker.setcash(10_000.0)
    cerebro.broker.set_coc(False)
    cerebro.broker.set_coo(False)
    cerebro.broker.setcommission(commission=0.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.addstrategy(strategy_cls)
    cerebro.addanalyzer(_OrderCounter, _name="counter")
    results = cerebro.run()
    return results[0].analyzers.counter


def _synthetic_ohlcv_flat(n: int, start: str = "2024-01-01") -> pd.DataFrame:
    """Flat-price OHLCV feed, naive-UTC indexed."""
    idx = pd.date_range(start=start, periods=n, freq="1h")
    return pd.DataFrame(
        {
            "open": np.full(n, 100.0),
            "high": np.full(n, 101.0),
            "low": np.full(n, 99.0),
            "close": np.full(n, 100.0),
            "volume": np.full(n, 1000.0),
        },
        index=idx,
    )


def _features_for(timestamps: pd.DatetimeIndex, **factor_cols) -> pd.DataFrame:
    """Build a features DataFrame keyed by tz-aware ``open_time_utc``."""
    ts_utc = timestamps.tz_localize("UTC") if timestamps.tz is None else timestamps
    return pd.DataFrame({"open_time_utc": ts_utc, **factor_cols})


# ===========================================================================
# 1. End-to-end crosses_above single-fire test.
# ===========================================================================


class TestCrossesAboveIntegration:
    def _build_registry(self) -> FactorRegistry:
        reg = FactorRegistry()
        reg.register(
            FactorSpec(
                name="value",
                category="test",
                warmup_bars=0,
                inputs=["value"],
                output_dtype="float64",
                compute=_passthrough_value,
                docstring="synthetic passthrough factor",
            )
        )
        return reg

    def test_crosses_above_scalar_fires_exactly_once_through_compiler(
        self, tmp_path
    ):
        """**MANDATORY end-to-end test**: a value that jumps above 50
        on bar 30 and stays above for 50 more bars must produce
        exactly ONE buy fill when run through the compiled strategy.
        """
        reg = self._build_registry()

        n = 80
        ohlcv = _synthetic_ohlcv_flat(n)
        values = np.concatenate([np.full(30, 10.0), np.full(n - 30, 60.0)])
        features_df = _features_for(ohlcv.index, value=values)

        dsl = StrategyDSL.model_validate(
            {
                "name": "cross_once",
                "description": "value crosses 50",
                "entry": [
                    {
                        "conditions": [
                            {
                                "factor": "value",
                                "op": "crosses_above",
                                "value": 50.0,
                            }
                        ]
                    }
                ],
                # Exit condition that will never be true on this feed,
                # so we can count entries in isolation.
                "exit": [
                    {
                        "conditions": [
                            {
                                "factor": "value",
                                "op": "<",
                                "value": -1.0,
                            }
                        ]
                    }
                ],
                "position_sizing": "full_equity",
            },
            context={"registry": reg},
        )

        strategy_cls = compile_dsl_to_strategy(
            dsl, reg, manifest_dir=tmp_path
        )

        # Bind the override inputs at strategy-param level.
        class Bound(strategy_cls):  # type: ignore[misc,valid-type]
            params = (
                ("features_df_override", features_df),
                ("registry_override", reg),
            )

        counter = _run_on_synthetic(Bound, ohlcv)
        assert len(counter.buys) == 1, (
            f"Expected exactly 1 buy over 50-bar stays-above run; "
            f"got {len(counter.buys)}"
        )
        assert len(counter.sells) == 0


# ===========================================================================
# 2. max_hold_bars forces exit.
# ===========================================================================


class TestMaxHoldBars:
    def test_max_hold_bars_forces_close(self, tmp_path):
        reg = FactorRegistry()
        reg.register(
            FactorSpec(
                name="value",
                category="test",
                warmup_bars=0,
                inputs=["value"],
                output_dtype="float64",
                compute=_passthrough_value,
                docstring="synthetic",
            )
        )

        n = 60
        ohlcv = _synthetic_ohlcv_flat(n)
        values = np.concatenate([np.full(10, 10.0), np.full(n - 10, 60.0)])
        features_df = _features_for(ohlcv.index, value=values)

        dsl = StrategyDSL.model_validate(
            {
                "name": "max_hold_test",
                "description": "entry then forced exit",
                "entry": [
                    {"conditions": [{"factor": "value", "op": "crosses_above", "value": 50.0}]}
                ],
                "exit": [
                    # Never true on this feed; exit should come from max_hold_bars.
                    {"conditions": [{"factor": "value", "op": "<", "value": -1.0}]}
                ],
                "position_sizing": "full_equity",
                "max_hold_bars": 5,
            },
            context={"registry": reg},
        )

        strategy_cls = compile_dsl_to_strategy(
            dsl, reg, manifest_dir=tmp_path
        )

        class Bound(strategy_cls):  # type: ignore[misc,valid-type]
            params = (
                ("features_df_override", features_df),
                ("registry_override", reg),
            )

        counter = _run_on_synthetic(Bound, ohlcv)
        assert len(counter.buys) >= 1
        # After the forced exit, entry may re-fire if the condition is
        # satisfied on a later bar. Either way we must see at least one
        # close, and the first close must follow the first buy within
        # max_hold_bars worth of bars (fill bar + max_hold_bars).
        assert len(counter.sells) >= 1
        first_buy = counter.buys[0]
        first_sell = counter.sells[0]
        hours_held = (first_sell - first_buy).total_seconds() / 3600.0
        # Signal-at-N, fill-at-N+1: hold cap of 5 signal bars → ≤ 5h
        assert hours_held <= 6.0, f"held {hours_held}h, cap was 5 bars"


# ===========================================================================
# 3. Compile-time structural checks.
# ===========================================================================


class TestCompileStructural:
    def test_compile_returns_base_strategy_subclass(self, tmp_path):
        reg = get_registry()
        dsl = StrategyDSL.model_validate(
            {
                "name": "struct_test",
                "description": "structural",
                "entry": [{"conditions": [{"factor": "sma_20", "op": ">", "value": "sma_50"}]}],
                "exit": [{"conditions": [{"factor": "sma_20", "op": "<", "value": "sma_50"}]}],
                "position_sizing": "full_equity",
            }
        )
        cls = compile_dsl_to_strategy(dsl, reg, manifest_dir=tmp_path)
        assert issubclass(cls, BaseStrategy)
        assert cls.STRATEGY_NAME == "struct_test"
        # max_warmup(sma_20=19, sma_50=49) == 49
        assert cls.WARMUP_BARS == 49
        assert set(cls._FACTORS_USED) == {"sma_20", "sma_50"}

    def test_compile_sets_warmup_from_referenced_factors(self, tmp_path):
        reg = get_registry()
        # Only reference sma_20 on both sides; warmup should be 19.
        dsl = StrategyDSL.model_validate(
            {
                "name": "warmup_test",
                "description": "only sma_20",
                "entry": [{"conditions": [{"factor": "sma_20", "op": ">", "value": 1.0}]}],
                "exit": [{"conditions": [{"factor": "sma_20", "op": "<", "value": 0.0}]}],
                "position_sizing": "full_equity",
            }
        )
        cls = compile_dsl_to_strategy(dsl, reg, manifest_dir=tmp_path)
        assert cls.WARMUP_BARS == 19


# ===========================================================================
# 4. Round-trip SMA crossover baseline vs DSL-compiled.
# ===========================================================================


RAW_PARQUET = Path(__file__).resolve().parent.parent / "data" / "raw" / "btcusdt_1h.parquet"
FEATURES_PARQUET = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "features"
    / "btcusdt_1h_features.parquet"
)


@pytest.mark.skipif(
    not RAW_PARQUET.exists() or not FEATURES_PARQUET.exists(),
    reason="requires canonical raw + feature parquets",
)
class TestRoundTripSMA:
    """The golden round-trip test.

    Runs ``SMACrossover(fast=20, slow=50)`` and the DSL-compiled
    equivalent across 2024 H1 and asserts:
    - total_trades exact match
    - Sharpe, total_return, max_drawdown within 1e-4
    """

    def _run(self, strategy_cls, params=None):
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 6, 30, 23, tzinfo=timezone.utc)
        return run_backtest(
            strategy_cls=strategy_cls,
            start_date=start,
            end_date=end,
            strategy_params=params or {},
            write_registry=False,
        )

    def test_round_trip_parity(self, tmp_path):
        baseline_result = self._run(
            SMACrossover,
            params={"fast_period": 20, "slow_period": 50},
        )

        dsl = StrategyDSL.model_validate(
            {
                "name": "sma_crossover_dsl",
                "description": "SMA 20/50 crossover expressed in DSL",
                "entry": [
                    {"conditions": [
                        {"factor": "sma_20", "op": "crosses_above", "value": "sma_50"}
                    ]}
                ],
                "exit": [
                    {"conditions": [
                        {"factor": "sma_20", "op": "crosses_below", "value": "sma_50"}
                    ]}
                ],
                "position_sizing": "full_equity",
            }
        )
        compiled = compile_dsl_to_strategy(
            dsl, registry=get_registry(), manifest_dir=tmp_path
        )
        dsl_result = self._run(compiled)

        b = baseline_result.metrics
        d = dsl_result.metrics

        assert d["total_trades"] == b["total_trades"], (
            f"trade count mismatch: baseline={b['total_trades']}, "
            f"dsl={d['total_trades']}"
        )
        assert abs(d["sharpe_ratio"] - b["sharpe_ratio"]) < 1e-4, (
            f"sharpe: baseline={b['sharpe_ratio']:.6f}, "
            f"dsl={d['sharpe_ratio']:.6f}"
        )
        assert abs(d["total_return"] - b["total_return"]) < 1e-4, (
            f"return: baseline={b['total_return']:.6f}, "
            f"dsl={d['total_return']:.6f}"
        )
        assert abs(d["max_drawdown"] - b["max_drawdown"]) < 1e-4, (
            f"max_dd: baseline={b['max_drawdown']:.6f}, "
            f"dsl={d['max_drawdown']:.6f}"
        )


# ===========================================================================
# 5. Compilation manifest + drift detection.
# ===========================================================================


class TestManifest:
    def _sample_dsl(self) -> StrategyDSL:
        return StrategyDSL.model_validate(
            {
                "name": "manifest_sample",
                "description": "sample for manifest tests",
                "entry": [{"conditions": [
                    {"factor": "sma_20", "op": ">", "value": "sma_50"}
                ]}],
                "exit": [{"conditions": [
                    {"factor": "sma_20", "op": "<", "value": "sma_50"}
                ]}],
                "position_sizing": "full_equity",
            }
        )

    def test_manifest_written_on_first_compile(self, tmp_path):
        dsl = self._sample_dsl()
        reg = get_registry()
        compile_dsl_to_strategy(dsl, reg, manifest_dir=tmp_path)
        dsl_hash = compute_dsl_hash(dsl)
        path = tmp_path / f"{dsl_hash}.json"
        assert path.exists()
        stored = json.loads(path.read_text())
        assert stored["canonical_dsl_string"] == canonicalize_dsl(dsl)
        assert stored["compiler_sha"] == _compute_compiler_sha()
        assert "feature_version" in stored
        assert "factor_snapshot" in stored

    def test_manifest_idempotent_on_matching_recompile(self, tmp_path):
        dsl = self._sample_dsl()
        reg = get_registry()
        compile_dsl_to_strategy(dsl, reg, manifest_dir=tmp_path)
        # Second compile with identical context should NOT raise.
        compile_dsl_to_strategy(dsl, reg, manifest_dir=tmp_path)

    def test_drift_compiler_sha_raises(self, tmp_path):
        dsl = self._sample_dsl()
        reg = get_registry()
        dsl_hash = compute_dsl_hash(dsl)

        # Write a manifest with an intentionally-wrong compiler_sha.
        write_compilation_manifest(
            dsl,
            reg,
            manifest_dir=tmp_path,
            dsl_hash=dsl_hash,
            compiler_sha="deadbeef" * 8,
        )
        with pytest.raises(ManifestDriftError, match="compiler_sha"):
            compile_dsl_to_strategy(dsl, reg, manifest_dir=tmp_path)

    def test_drift_canonical_dsl_raises(self, tmp_path):
        dsl = self._sample_dsl()
        reg = get_registry()
        dsl_hash = compute_dsl_hash(dsl)

        path = tmp_path / f"{dsl_hash}.json"
        # Write a manifest that pretends the DSL was different.
        live = _build_manifest(dsl, reg)
        payload = _manifest_to_json_dict(live)
        payload["canonical_dsl_string"] = '{"faked":"mismatch"}'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))

        with pytest.raises(ManifestDriftError, match="canonical_dsl"):
            compile_dsl_to_strategy(
                dsl, reg, manifest_dir=tmp_path, dsl_hash=dsl_hash
            )

    def test_drift_feature_version_raises(self, tmp_path):
        dsl = self._sample_dsl()
        reg = get_registry()
        dsl_hash = compute_dsl_hash(dsl)

        path = tmp_path / f"{dsl_hash}.json"
        live = _build_manifest(dsl, reg)
        payload = _manifest_to_json_dict(live)
        payload["feature_version"] = "0" * 64
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))

        with pytest.raises(ManifestDriftError, match="feature_version"):
            compile_dsl_to_strategy(
                dsl, reg, manifest_dir=tmp_path, dsl_hash=dsl_hash
            )

    def test_drift_factor_snapshot_raises(self, tmp_path):
        dsl = self._sample_dsl()
        reg = get_registry()
        dsl_hash = compute_dsl_hash(dsl)

        path = tmp_path / f"{dsl_hash}.json"
        live = _build_manifest(dsl, reg)
        payload = _manifest_to_json_dict(live)
        # Pretend the factor snapshot differs (extra fake factor).
        payload["factor_snapshot"] = payload["factor_snapshot"] + [
            {"name": "ghost", "warmup_bars": 0}
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))

        with pytest.raises(ManifestDriftError, match="factor_snapshot"):
            compile_dsl_to_strategy(
                dsl, reg, manifest_dir=tmp_path, dsl_hash=dsl_hash
            )

    def test_delete_and_recompile_works(self, tmp_path):
        """After explicit human-acknowledged deletion, recompile succeeds.

        This is the only supported recovery path from drift.
        """
        dsl = self._sample_dsl()
        reg = get_registry()
        dsl_hash = compute_dsl_hash(dsl)
        path = tmp_path / f"{dsl_hash}.json"

        # Plant a drifted manifest.
        live = _build_manifest(dsl, reg)
        payload = _manifest_to_json_dict(live)
        payload["compiler_sha"] = "bad" * 20
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))

        # Delete — the supported remediation.
        path.unlink()

        # Now compile cleanly.
        compile_dsl_to_strategy(dsl, reg, manifest_dir=tmp_path)
        assert path.exists()
