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


def _synthetic_ohlcv(n_bars: int, base_price: float = 100.0) -> pd.DataFrame:
    """Deterministic hourly OHLCV; an up-then-down ramp so intrabar_push
    and rsi_14 both vary enough to exercise the entry + sizing ladder.

    ``base_price`` scales the level (drift/range are proportional, so the
    oscillation is meaningful at any scale). At the default 100.0 the output
    is byte-identical to the original generator (3.0 == 100*0.03, 1.0 ==
    100*0.01); a BTC-scale ``base_price`` (e.g. 78_000) exercises the
    fractional-unit sizing path.
    """
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    rows = []
    price = base_price
    for i in range(n_bars):
        # Oscillate so RSI dips below threshold periodically.
        drift = math.sin(i / 5.0) * (base_price * 0.03)
        o = price
        c = price + drift
        h = max(o, c) + base_price * 0.01
        low = min(o, c) - base_price * 0.01
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
    # Position notional well below full-equity: the fractional self.buy emit at
    # frac <= 0.75 scales the 99% sizing. Full-equity (~99%) would buy
    # ~ cash / price units; a 0.75 band buys ~0.75 * 0.99 of that.
    first_size, first_price = captured["sizes"][0]
    full_equity_units = 100_000.0 / first_price
    assert 0 < first_size < 0.80 * full_equity_units


def test_compiled_sizing_fractional_at_btc_price(tmp_path):
    """Regression for the bug Section-C's price=100 engine test missed: a
    SizingSpec must produce FRACTIONAL trades at BTC-scale unit prices.

    order_target_percent routed sizing through CommInfoBase.getsize =
    int(cash // price), which floors a sub-1-unit target to ZERO whole units
    at BTC prices (~$78k) with modest cash ($10k) -> NO trades at all. The
    fractional self.buy emit fixes it (BTC trades in fractional units).
    """
    registry = get_registry()
    raw = _synthetic_ohlcv(900, base_price=78_000.0)  # BTC-scale price
    raw_path = tmp_path / "raw.parquet"
    raw.to_parquet(raw_path, index=False)
    features_df = build_features_df(raw, registry)

    dsl = StrategyDSL(
        name="ternary_btc",
        description="ternary sizing at BTC-scale price (fractional units)",
        entry=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op="<", value=55.0)])],
        exit=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op=">", value=60.0)])],
        position_sizing=SizingSpec(
            factor="intrabar_push",
            bands=[{"lower": -10.0, "upper": 10.0, "size": 0.5}],
            default_size=0.5,
        ),
        max_hold_bars=24,
    )
    strat_cls = compile_dsl_to_strategy(dsl, registry=registry, write_manifest=False)

    cerebro = bt.Cerebro()
    configure_cerebro(cerebro, cash=10_000.0)  # modest cash -> sub-1-unit BTC targets
    cerebro.adddata(ParquetFeed.from_parquet(raw_path))

    captured = {"sizes": []}

    class _Rec(bt.Analyzer):
        def notify_order(self, order):
            if order.status == order.Completed and order.isbuy():
                captured["sizes"].append(
                    (float(order.executed.size), float(order.executed.price))
                )

    cerebro.addstrategy(strat_cls, features_df_override=features_df)
    cerebro.addanalyzer(_Rec, _name="rec")
    cerebro.run()

    # The whole point: fractional sizing trades at BTC prices (int-floor gave 0).
    assert len(captured["sizes"]) >= 1, "fractional sizing must trade at BTC prices"
    first_size, first_price = captured["sizes"][0]
    assert first_price > 1_000.0           # BTC-scale price confirmed
    assert 0.0 < first_size < 1.0          # a fractional BTC unit (not int-floored to 0)


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
    sizing emit (fractional ``self.buy``) still fills on a bar boundary.
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
    """default_size=0.0 with a band that never matches -> frac=0.0 at every
    entry, which emits NO order (the fractional self.buy is guarded by
    ``size > 0.0``). Verify the run completes, no fill occurs, and capital is
    unchanged (the stamped _entry_bar is harmless while the position stays flat).
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


# ---------------------------------------------------------------------------
# FIX 1 regression (2-leg B2 CRITICAL HARD CONSTRAINT): the funding-warmup
# bar-equivalent conversion (input_period_bars) must leave OHLCV-only strategies'
# WARMUP_BARS BYTE-UNCHANGED. OHLCV factors default to input_period_bars=1, so
# their bar-equivalent warmup is identical to warmup_bars.
# ---------------------------------------------------------------------------


def _ohlcv_only_sma_dsl() -> StrategyDSL:
    """A simple OHLCV-only long/flat DSL: sma_20 vs sma_50 (factor-vs-factor).

    Its max warmup factor is sma_50 (warmup_bars=49), so WARMUP_BARS must be 49
    both before and after the input_period_bars fix — OHLCV factors are
    input_period_bars=1 (no bar-equivalent inflation).
    """
    return StrategyDSL(
        name="ohlcv_only_sma_warmup_regression",
        description="OHLCV-only sma_20 vs sma_50 long/flat; WARMUP_BARS-unchanged regression for the funding bar-equivalent fix.",
        entry=[ConditionGroup(conditions=[Condition(factor="sma_20", op=">", value="sma_50")])],
        exit=[ConditionGroup(conditions=[Condition(factor="sma_20", op="<=", value="sma_50")])],
        position_sizing="full_equity",
    )


def test_ohlcv_only_warmup_bars_unchanged_by_funding_fix():
    cls = compile_dsl_to_strategy(_ohlcv_only_sma_dsl(), write_manifest=False)
    # sma_50 warmup_bars=49 (0-indexed registry convention) * input_period_bars=1.
    assert cls.WARMUP_BARS == 49, (
        f"OHLCV-only WARMUP_BARS must stay 49 (sma_50); got {cls.WARMUP_BARS}. "
        f"The funding input_period_bars conversion leaked into OHLCV factors."
    )
