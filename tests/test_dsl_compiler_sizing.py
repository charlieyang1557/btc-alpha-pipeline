"""Tests for factor-conditioned position sizing helpers in dsl_compiler.

Covers:
- ``_extract_factor_names`` includes ``position_sizing.factor`` (Task 16 warmup
  discipline requirement).
- ``_compile_sizing`` band ladder, NaN fallback, and ``prev_row`` isolation.
- End-to-end engine integration: SizingSpec-compiled strategy runs through the
  real Phase-1 engine, size ladder is applied (PercentSizer bypassed), fills
  occur at N+1 open, and zero-size default safely no-ops the entry.
"""
import math
from datetime import datetime, timedelta, timezone

import backtrader as bt
import pandas as pd
import pytest

from backtest.bt_parquet_feed import ParquetFeed
from backtest.execution_model import configure_cerebro
from factors.build_features import build_features_df
from factors.registry import get_registry
from strategies.dsl import Condition, ConditionGroup, SizingSpec, StrategyDSL
from strategies.dsl import canonicalize_dsl
from strategies.dsl_compiler import (
    ManifestDriftError,
    _compile_sizing,
    _extract_factor_names,
    compile_dsl_to_strategy,
    write_compilation_manifest,
)
from agents.hypothesis_hash import hash_dsl


def _entry():
    return [ConditionGroup(conditions=[Condition(factor="rsi_14", op="<", value=30.0)])]


def _exit():
    return [ConditionGroup(conditions=[Condition(factor="rsi_14", op=">", value=70.0)])]


def _spec():
    return SizingSpec(
        factor="intrabar_push",
        bands=[
            {"lower": -1.0, "upper": 0.0, "size": 0.25},
            {"lower": 0.0, "upper": 1.0, "size": 0.75},
        ],
        default_size=0.5,
    )


def test_extract_factor_names_includes_sizing_factor():
    dsl = StrategyDSL(
        name="x",
        description="sizing factor must appear in warmup-driving factor list",
        entry=_entry(),
        exit=_exit(),
        position_sizing=_spec(),
    )
    names = _extract_factor_names(dsl)
    assert "rsi_14" in names
    assert "intrabar_push" in names  # sizing factor included
    assert names == sorted(names)


def test_extract_factor_names_full_equity_no_extra():
    dsl = StrategyDSL(
        name="x",
        description="full equity adds no sizing factor",
        entry=_entry(),
        exit=_exit(),
        position_sizing="full_equity",
    )
    assert _extract_factor_names(dsl) == ["rsi_14"]


def test_compile_sizing_band_ladder():
    factor_index = {"intrabar_push": 0}
    fn = _compile_sizing(_spec(), factor_index)
    # value -0.5 -> first band [-1,0) -> 0.25
    assert fn((-0.5,), (0.0,)) == 0.25
    # value 0.5 -> second band [0,1) -> 0.75
    assert fn((0.5,), (0.0,)) == 0.75
    # value 5.0 -> no band -> default 0.5
    assert fn((5.0,), (0.0,)) == 0.5
    # half-open: upper edge 0.0 falls into the SECOND band [0,1), not first
    assert fn((0.0,), (0.0,)) == 0.75


def test_compile_sizing_nan_uses_default():
    factor_index = {"intrabar_push": 0}
    fn = _compile_sizing(_spec(), factor_index)
    assert fn((float("nan"),), (0.0,)) == 0.5  # NaN -> default, never a band


# ---------------------------------------------------------------------------
# Task 17: End-to-end engine integration tests
# ---------------------------------------------------------------------------


def _synthetic_ohlcv(n_bars: int) -> pd.DataFrame:
    """Deterministic hourly OHLCV; an up-then-down ramp so intrabar_push
    and rsi_14 both vary enough to exercise the entry + sizing ladder.
    """
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    rows = []
    price = 100.0
    for i in range(n_bars):
        # Oscillate so RSI dips below threshold periodically.
        drift = math.sin(i / 5.0) * 3.0
        o = price
        c = price + drift
        h = max(o, c) + 1.0
        low = min(o, c) - 1.0
        rows.append(
            {
                "open_time_utc": start + timedelta(hours=i),
                "open": o,
                "high": h,
                "low": low,
                "close": c,
                "volume": 1000.0 + i,
                "quote_volume": (1000.0 + i) * c,
                "trade_count": 10,
            }
        )
        price = c
    df = pd.DataFrame(rows)
    df["open_time_utc"] = df["open_time_utc"].astype("datetime64[ms, UTC]")
    return df


# Step -1 human-locked hypothesis param (illustrative symbol; the real
# value is fixed in the locked spec, not chosen here).
THETA_PUSH = 0.0


def test_compiled_sizing_runs_through_engine(tmp_path):
    registry = get_registry()
    raw = _synthetic_ohlcv(900)  # > max sizing/condition warmup
    raw_path = tmp_path / "raw.parquet"
    raw.to_parquet(raw_path, index=False)

    features_df = build_features_df(raw, registry)

    spec = SizingSpec(
        factor="intrabar_push",
        bands=[
            {"lower": -10.0, "upper": THETA_PUSH, "size": 0.25},
            {"lower": THETA_PUSH, "upper": 10.0, "size": 0.75},
        ],
        default_size=0.5,
    )
    dsl = StrategyDSL(
        name="ternary_engine",
        description="ternary sizing compiled through the Phase 1 engine",
        entry=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op="<", value=55.0)])],
        exit=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op=">", value=60.0)])],
        position_sizing=spec,
        max_hold_bars=24,
    )

    strat_cls = compile_dsl_to_strategy(
        dsl, registry=registry, write_manifest=False
    )

    cerebro = bt.Cerebro()
    configure_cerebro(cerebro, cash=100_000.0)  # installs PercentSizer
    feed = ParquetFeed.from_parquet(raw_path)
    cerebro.adddata(feed)

    captured = {"sizes": []}

    class _SizeRecorder(bt.Analyzer):
        def notify_order(self, order):
            if order.status == order.Completed and order.isbuy():
                captured["sizes"].append(
                    (order.executed.size, order.executed.price)
                )

    cerebro.addstrategy(strat_cls, features_df_override=features_df)
    cerebro.addanalyzer(_SizeRecorder, _name="rec")
    cerebro.run()

    # At least one buy executed.
    assert len(captured["sizes"]) >= 1
    # Position notional well below full-equity: order_target_percent at
    # <= 0.75 bypasses the 99% PercentSizer. Full-equity (~99%) would buy
    # ~ cash / price units; a 0.75 target buys at most ~0.76 of that.
    first_size, first_price = captured["sizes"][0]
    full_equity_units = 100_000.0 / first_price
    assert 0 < first_size < 0.80 * full_equity_units


def test_compiled_sizing_fills_at_next_open(tmp_path):
    """Sanity: fills land on a bar-boundary price, not an interpolated or
    arbitrary value.

    NOTE (limitation): ``_synthetic_ohlcv`` chains prices so that
    ``close[i] == open[i+1]``; the close-price set is therefore a subset of
    ``open_prices``. This assertion confirms each fill price IS a real bar
    open value, but it cannot by itself exclude a hypothetical close-fill on
    this data. The actual N+1-open (no-same-bar-execution) contract is
    enforced upstream by ``configure_cerebro`` (``set_coc(False)`` /
    ``set_coo(False)``) and is regression-covered by the engine/execution
    test suite; this case adds a sizing-path-specific smoke check that the
    sizing emit (``order_target_percent``) still fills on a bar boundary.
    A future cleanup could decouple opens from closes in the generator to
    make this assertion independently discriminating.
    """
    registry = get_registry()
    raw = _synthetic_ohlcv(900)
    raw_path = tmp_path / "raw.parquet"
    raw.to_parquet(raw_path, index=False)
    features_df = build_features_df(raw, registry)

    dsl = StrategyDSL(
        name="ternary_open",
        description="verify N+1 open fill under sizing emit",
        entry=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op="<", value=55.0)])],
        exit=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op=">", value=60.0)])],
        position_sizing=SizingSpec(
            factor="intrabar_push",
            bands=[{"lower": -10.0, "upper": 10.0, "size": 0.5}],
            default_size=0.5,
        ),
    )
    strat_cls = compile_dsl_to_strategy(dsl, registry=registry, write_manifest=False)

    cerebro = bt.Cerebro()
    configure_cerebro(cerebro, cash=100_000.0)
    cerebro.adddata(ParquetFeed.from_parquet(raw_path))

    open_prices = set(round(float(o), 6) for o in raw["open"])
    fills = {"prices": []}

    class _OpenChecker(bt.Analyzer):
        def notify_order(self, order):
            if order.status == order.Completed:
                fills["prices"].append(round(float(order.executed.price), 6))

    cerebro.addstrategy(strat_cls, features_df_override=features_df)
    cerebro.addanalyzer(_OpenChecker, _name="oc")
    cerebro.run()

    assert fills["prices"], "expected at least one fill"
    for px in fills["prices"]:
        assert px in open_prices  # filled at a bar OPEN, never close-only


def test_compiled_sizing_zero_default_is_safe_noop(tmp_path):
    """default_size=0.0 with a band that never matches -> every entry emits
    order_target_percent(target=0.0), which places NO order. Verify the run
    completes, no fill occurs, and capital is unchanged (the stamped
    _entry_bar is harmless while the position stays flat).
    """
    registry = get_registry()
    raw = _synthetic_ohlcv(900)
    raw_path = tmp_path / "raw.parquet"
    raw.to_parquet(raw_path, index=False)
    features_df = build_features_df(raw, registry)

    dsl = StrategyDSL(
        name="ternary_zero",
        description="zero-size default declines entries as a safe no-op",
        entry=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op="<", value=55.0)])],
        exit=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op=">", value=60.0)])],
        position_sizing=SizingSpec(
            factor="intrabar_push",
            # intrabar_push lives in [-1, 1]; this band never matches, so the
            # sizing factor always falls through to default_size=0.0.
            bands=[{"lower": 100.0, "upper": 200.0, "size": 0.75}],
            default_size=0.0,
        ),
    )
    strat_cls = compile_dsl_to_strategy(dsl, registry=registry, write_manifest=False)

    cerebro = bt.Cerebro()
    configure_cerebro(cerebro, cash=100_000.0)
    cerebro.adddata(ParquetFeed.from_parquet(raw_path))

    fills = {"n": 0}

    class _FillCounter(bt.Analyzer):
        def notify_order(self, order):
            if order.status == order.Completed:
                fills["n"] += 1

    cerebro.addstrategy(strat_cls, features_df_override=features_df)
    cerebro.addanalyzer(_FillCounter, _name="fc")
    cerebro.run()

    assert fills["n"] == 0  # no order ever placed
    assert cerebro.broker.getvalue() == pytest.approx(100_000.0)  # capital intact


# ---------------------------------------------------------------------------
# Task 18: Manifest + D3-hash drift on sizing change
# ---------------------------------------------------------------------------


def _dsl_with_default(default_size: float) -> StrategyDSL:
    return StrategyDSL(
        name="drift",
        description="sizing drift detection strategy",
        entry=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op="<", value=30.0)])],
        exit=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op=">", value=70.0)])],
        position_sizing=SizingSpec(
            factor="intrabar_push",
            bands=[{"lower": 0.0, "upper": 1.0, "size": 0.5}],
            default_size=default_size,
        ),
    )


def test_manifest_drift_on_sizing_change(tmp_path):
    registry = get_registry()
    dsl_a = _dsl_with_default(0.5)
    dsl_b = _dsl_with_default(0.6)

    # Same dsl_hash filename key forces a drift comparison on the second
    # write (we pin the key so the manifest path collides deliberately).
    shared_key = "deadbeefdeadbeef"
    write_compilation_manifest(
        dsl_a, registry, manifest_dir=tmp_path, dsl_hash=shared_key
    )
    with pytest.raises(ManifestDriftError, match="canonical_dsl mismatch"):
        write_compilation_manifest(
            dsl_b, registry, manifest_dir=tmp_path, dsl_hash=shared_key
        )


def test_canonical_dsl_differs_on_sizing_change():
    assert canonicalize_dsl(_dsl_with_default(0.5)) != canonicalize_dsl(
        _dsl_with_default(0.6)
    )


def test_d3_hash_differs_on_sizing_change():
    assert hash_dsl(_dsl_with_default(0.5)) != hash_dsl(_dsl_with_default(0.6))
