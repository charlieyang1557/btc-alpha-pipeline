"""Tests for backtest/execution_model.py and backtest/slippage.py.

Verifies:
- Next-bar-open execution (fill price == bar N+1 open, not bar N close)
- Commission == 7bps of trade value
- Zero-volume fill deferral
- 24-bar deferral limit → order cancellation
- ConstantSlippage cost model
- configure_cerebro applies correct settings
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import backtrader as bt
import numpy as np
import pandas as pd
import pytest

from backtest.bt_parquet_feed import ParquetFeed
from backtest.execution_model import AlphaBroker, configure_cerebro
from backtest.slippage import ConstantSlippage, load_execution_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_test_parquet(
    tmp_path: Path,
    n_hours: int = 30,
    start: str = "2024-01-01",
    volumes: list[float] | None = None,
) -> tuple[Path, pd.DataFrame]:
    """Create a synthetic parquet file with deterministic prices.

    Prices:
        open  = 100 + i
        high  = 110 + i
        low   =  90 + i
        close = 105 + i

    Args:
        tmp_path: Pytest temporary directory.
        n_hours: Number of hourly bars.
        start: Start date in ISO format.
        volumes: Optional list of volumes (length must match n_hours).

    Returns:
        Tuple of (path to parquet, original DataFrame).
    """
    timestamps = pd.date_range(start=start, periods=n_hours, freq="h", tz="UTC")
    vols = volumes if volumes else [1000.0] * n_hours

    df = pd.DataFrame({
        "open_time_utc": timestamps.astype("datetime64[ms, UTC]"),
        "open": [100.0 + i for i in range(n_hours)],
        "high": [110.0 + i for i in range(n_hours)],
        "low": [90.0 + i for i in range(n_hours)],
        "close": [105.0 + i for i in range(n_hours)],
        "volume": vols,
        "quote_volume": [100_000.0] * n_hours,
        "trade_count": np.arange(5000, 5000 + n_hours, dtype="int64"),
        "ingested_at_utc": pd.Timestamp.now(tz="UTC").floor("ms"),
        "source": pd.array(["binance_vision"] * n_hours, dtype="string"),
    })
    df["ingested_at_utc"] = df["ingested_at_utc"].astype("datetime64[ms, UTC]")

    path = tmp_path / "test.parquet"
    df.to_parquet(path, engine="pyarrow", index=False)
    return path, df


class _BuyOnBar(bt.Strategy):
    """Strategy that buys on bar N and sells on bar M.

    Records fill details for verification.
    """

    params = (
        ("buy_bar", 10),
        ("sell_bar", 20),
    )

    def __init__(self):
        self.bar_idx = 0
        self.fills = []
        self.cancelled = []

    def next(self):
        if self.bar_idx == self.p.buy_bar:
            self.buy()
        elif self.bar_idx == self.p.sell_bar and self.position:
            self.close()
        self.bar_idx += 1

    def notify_order(self, order):
        if order.status == order.Completed:
            self.fills.append({
                "bar_idx": self.bar_idx,
                "price": order.executed.price,
                "size": order.executed.size,
                "comm": order.executed.comm,
                "value": order.executed.value,
                "is_buy": order.isbuy(),
            })
        elif order.status == order.Canceled:
            self.cancelled.append(order.ref)


class _BuyOnBarAndHold(bt.Strategy):
    """Strategy that buys on a specific bar and holds (no sell)."""

    params = (("buy_bar", 2),)

    def __init__(self):
        self.bar_idx = 0
        self.fills = []
        self.cancelled = []

    def next(self):
        if self.bar_idx == self.p.buy_bar:
            self.buy()
        self.bar_idx += 1

    def notify_order(self, order):
        if order.status == order.Completed:
            self.fills.append({
                "bar_idx": self.bar_idx,
                "price": order.executed.price,
                "size": order.executed.size,
                "comm": order.executed.comm,
                "value": order.executed.value,
                "is_buy": order.isbuy(),
            })
        elif order.status == order.Canceled:
            self.cancelled.append(order.ref)


# ---------------------------------------------------------------------------
# Tests: Next-bar-open execution
# ---------------------------------------------------------------------------


class TestNextBarOpen:
    """Verify orders fill at next bar's open, not the signal bar's close."""

    def test_buy_fills_at_next_bar_open(self, tmp_path):
        """Buy on bar 10 → fill at bar 11 open price."""
        path, df = _make_test_parquet(tmp_path, n_hours=30)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_BuyOnBar, buy_bar=10, sell_bar=25)
        configure_cerebro(cerebro)

        results = cerebro.run()
        strat = results[0]

        assert len(strat.fills) >= 1
        buy_fill = strat.fills[0]
        assert buy_fill["is_buy"] is True

        # Bar 10 signal → fill at bar 11 open
        # open[11] = 100 + 11 = 111.0
        assert buy_fill["price"] == pytest.approx(111.0)

    def test_sell_fills_at_next_bar_open(self, tmp_path):
        """Sell on bar 20 → fill at bar 21 open price."""
        path, df = _make_test_parquet(tmp_path, n_hours=30)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_BuyOnBar, buy_bar=10, sell_bar=20)
        configure_cerebro(cerebro)

        results = cerebro.run()
        strat = results[0]

        assert len(strat.fills) == 2
        sell_fill = strat.fills[1]
        assert sell_fill["is_buy"] is False

        # Bar 20 signal → fill at bar 21 open
        # open[21] = 100 + 21 = 121.0
        assert sell_fill["price"] == pytest.approx(121.0)

    def test_fill_price_is_not_signal_bar_close(self, tmp_path):
        """Fill price must NOT equal the signal bar's close."""
        path, df = _make_test_parquet(tmp_path, n_hours=30)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_BuyOnBar, buy_bar=10, sell_bar=25)
        configure_cerebro(cerebro)

        results = cerebro.run()
        strat = results[0]

        buy_fill = strat.fills[0]
        signal_bar_close = 105.0 + 10  # close[10] = 115.0
        assert buy_fill["price"] != signal_bar_close


# ---------------------------------------------------------------------------
# Tests: Commission
# ---------------------------------------------------------------------------


class TestCommission:
    """Verify 7bps effective commission is applied correctly."""

    def test_commission_is_7bps(self, tmp_path):
        """Commission on buy should equal 0.07% of trade value."""
        path, df = _make_test_parquet(tmp_path, n_hours=30)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_BuyOnBar, buy_bar=10, sell_bar=20)
        configure_cerebro(cerebro)

        results = cerebro.run()
        strat = results[0]

        buy_fill = strat.fills[0]
        trade_value = abs(buy_fill["size"]) * buy_fill["price"]
        expected_comm = trade_value * 0.0007
        assert buy_fill["comm"] == pytest.approx(expected_comm, rel=1e-6)

    def test_round_trip_commission(self, tmp_path):
        """Buy + sell should incur 14bps total (7bps each side)."""
        path, df = _make_test_parquet(tmp_path, n_hours=30)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_BuyOnBar, buy_bar=10, sell_bar=20)
        configure_cerebro(cerebro)

        results = cerebro.run()
        strat = results[0]

        assert len(strat.fills) == 2
        buy_comm = strat.fills[0]["comm"]
        sell_comm = strat.fills[1]["comm"]

        buy_value = abs(strat.fills[0]["size"]) * strat.fills[0]["price"]
        sell_value = abs(strat.fills[1]["size"]) * strat.fills[1]["price"]

        assert buy_comm == pytest.approx(buy_value * 0.0007, rel=1e-6)
        assert sell_comm == pytest.approx(sell_value * 0.0007, rel=1e-6)


# ---------------------------------------------------------------------------
# Tests: Zero-volume deferral
# ---------------------------------------------------------------------------


class TestZeroVolumeDeferral:
    """Verify orders defer on zero-volume bars."""

    def test_fill_deferred_past_zero_volume(self, tmp_path):
        """Buy on bar 2 with bar 3 zero-volume → fill at bar 4 open."""
        volumes = [1000.0] * 30
        volumes[3] = 0.0  # bar 3 has zero volume

        path, df = _make_test_parquet(tmp_path, n_hours=30, volumes=volumes)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_BuyOnBarAndHold, buy_bar=2)
        configure_cerebro(cerebro)

        results = cerebro.run()
        strat = results[0]

        assert len(strat.fills) == 1
        fill = strat.fills[0]

        # Bar 2 signal → would fill at bar 3, but bar 3 has volume=0
        # So deferred to bar 4 → open[4] = 100 + 4 = 104.0
        assert fill["price"] == pytest.approx(104.0)

    def test_multiple_zero_volume_bars_deferred(self, tmp_path):
        """Multiple consecutive zero-volume bars defer until first valid."""
        volumes = [1000.0] * 30
        volumes[3] = 0.0  # bar 3 zero
        volumes[4] = 0.0  # bar 4 zero
        volumes[5] = 0.0  # bar 5 zero

        path, df = _make_test_parquet(tmp_path, n_hours=30, volumes=volumes)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_BuyOnBarAndHold, buy_bar=2)
        configure_cerebro(cerebro)

        results = cerebro.run()
        strat = results[0]

        assert len(strat.fills) == 1
        fill = strat.fills[0]

        # Deferred past bars 3, 4, 5 → fills at bar 6 open
        # open[6] = 100 + 6 = 106.0
        assert fill["price"] == pytest.approx(106.0)

    def test_24_bar_deferral_cancels_order(self, tmp_path):
        """Order cancelled after 24+ consecutive zero-volume bars."""
        n_hours = 40
        volumes = [1000.0] * n_hours
        # Bars 3 through 27 all zero volume (25 bars > MAX_DEFER_BARS=24)
        for i in range(3, 28):
            volumes[i] = 0.0

        path, df = _make_test_parquet(tmp_path, n_hours=n_hours, volumes=volumes)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_BuyOnBarAndHold, buy_bar=2)
        configure_cerebro(cerebro)

        results = cerebro.run()
        strat = results[0]

        # Order should be cancelled, not filled
        assert len(strat.fills) == 0
        assert len(strat.cancelled) == 1

    def test_normal_volume_no_deferral(self, tmp_path):
        """With all non-zero volume, fill happens on the expected bar."""
        path, df = _make_test_parquet(tmp_path, n_hours=30)
        feed = ParquetFeed.from_parquet(path)

        cerebro = bt.Cerebro()
        cerebro.adddata(feed)
        cerebro.addstrategy(_BuyOnBarAndHold, buy_bar=5)
        configure_cerebro(cerebro)

        results = cerebro.run()
        strat = results[0]

        assert len(strat.fills) == 1
        # Bar 5 signal → bar 6 open = 106.0
        assert strat.fills[0]["price"] == pytest.approx(106.0)


# ---------------------------------------------------------------------------
# Tests: ConstantSlippage model
# ---------------------------------------------------------------------------


class TestConstantSlippage:
    """Test the ConstantSlippage cost model."""

    def test_total_bps(self):
        model = ConstantSlippage(fee_bps=4.0, slippage_bps=3.0)
        assert model.total_bps == 7.0

    def test_effective_commission(self):
        model = ConstantSlippage(fee_bps=4.0, slippage_bps=3.0)
        assert model.effective_commission == pytest.approx(0.0007)

    def test_fee_model_label(self):
        model = ConstantSlippage(fee_bps=4.0, slippage_bps=3.0)
        assert model.fee_model_label == "effective_7bps_per_side"

    def test_from_config(self):
        config = load_execution_config()
        model = ConstantSlippage.from_config(config)
        assert model.fee_bps == 4.0
        assert model.slippage_bps == 3.0
        assert model.total_bps == 7.0


class TestConfigureCerebro:
    """Test configure_cerebro applies correct settings."""

    def test_returns_cost_model(self):
        cerebro = bt.Cerebro()
        cost_model = configure_cerebro(cerebro)
        assert isinstance(cost_model, ConstantSlippage)
        assert cost_model.fee_model_label == "effective_7bps_per_side"

    def test_broker_is_alpha_broker(self):
        cerebro = bt.Cerebro()
        configure_cerebro(cerebro)
        assert isinstance(cerebro.broker, AlphaBroker)

    def test_cash_set(self):
        cerebro = bt.Cerebro()
        configure_cerebro(cerebro, cash=50_000.0)
        assert cerebro.broker.getcash() == pytest.approx(50_000.0)

    def test_default_cash(self):
        cerebro = bt.Cerebro()
        configure_cerebro(cerebro)
        assert cerebro.broker.getcash() == pytest.approx(10_000.0)
