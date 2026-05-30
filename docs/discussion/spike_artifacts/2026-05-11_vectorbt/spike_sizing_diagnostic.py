"""Follow-up diagnostic: isolate the $23 final-value diff.

Hypothesis: trade list is byte-equivalent (confirmed). The equity diff must come
from position sizing convention difference, NOT engine semantics.

Test: Compute per-trade gross return (exit_price/entry_price - 1) - 2*fee.
If per-trade returns match exactly across engines, the diff is purely a
sizing/compounding artifact.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import backtrader as bt
import vectorbt as vbt

DATA_PATH = str(Path(__file__).resolve().parents[4] / "data/raw/btcusdt_1h.parquet")
START = "2024-01-01"
END = "2024-04-01"
FAST = 20
SLOW = 50
FEE = 0.0007
INIT_CASH = 10000.0

df = pd.read_parquet(DATA_PATH)
df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True)
df = df.set_index("open_time_utc").sort_index().loc[START:END].copy()
close = df["close"].astype(float)
open_ = df["open"].astype(float)

fast_sma = close.rolling(window=FAST).mean()
slow_sma = close.rolling(window=SLOW).mean()
prev_diff = fast_sma.shift(1) - slow_sma.shift(1)
curr_diff = fast_sma - slow_sma
golden_cross = (prev_diff <= 0) & (curr_diff > 0)
death_cross = (prev_diff >= 0) & (curr_diff < 0)

# -------- vectorbt with EXPLICIT size=np.inf (100% cash) --------
entries = golden_cross.fillna(False).astype(bool).shift(1).fillna(False).astype(bool)
exits = death_cross.fillna(False).astype(bool).shift(1).fillna(False).astype(bool)

pf_inf = vbt.Portfolio.from_signals(
    close=close, entries=entries, exits=exits, price=open_,
    fees=FEE, init_cash=INIT_CASH, freq="1H", size=np.inf,
)
pf_99 = vbt.Portfolio.from_signals(
    close=close, entries=entries, exits=exits, price=open_,
    fees=FEE, init_cash=INIT_CASH, freq="1H",
    size=0.99, size_type="percent",
)

print(f"vectorbt size=inf  final: ${pf_inf.value().iloc[-1]:,.4f}  return: {pf_inf.total_return():.6%}")
print(f"vectorbt size=99%  final: ${pf_99.value().iloc[-1]:,.4f}  return: {pf_99.total_return():.6%}")

# -------- Per-trade return analysis (vectorbt) --------
vbt_trades = pf_inf.trades.records_readable
vbt_per_trade_ret = (
    (vbt_trades["Avg Exit Price"] / vbt_trades["Avg Entry Price"]) * (1 - FEE) ** 2 - 1
)
print(f"\nvectorbt: {len(vbt_trades)} trades")
print(f"  per-trade gross return (price ratio - 2 fee): mean={vbt_per_trade_ret.mean():.6%}, "
      f"sum={vbt_per_trade_ret.sum():.6%}")
print(f"  compounded if 100% reinvested: {(np.prod(1 + vbt_per_trade_ret) - 1):.6%}")
print(f"  vectorbt reported Return per trade (mean): {vbt_trades['Return'].mean():.6%}")
print(f"  vectorbt reported Return per trade (sum):  {vbt_trades['Return'].sum():.6%}")

# -------- Backtrader: write a separate engine + log per-trade return --------
_bt_trades: list[dict] = []
_bt_pending: dict = {}

class SMAxStrat(bt.Strategy):
    params = (("fast", FAST), ("slow", SLOW))
    def __init__(self):
        self.fast_sma = bt.indicators.SMA(self.data.close, period=self.p.fast)
        self.slow_sma = bt.indicators.SMA(self.data.close, period=self.p.slow)
        self.cross = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)
    def next(self):
        if self.cross > 0 and not self.position:
            self.buy()
        elif self.cross < 0 and self.position:
            self.close()
    def notify_order(self, order):
        if order.status == order.Completed:
            dt = pd.Timestamp(bt.num2date(order.executed.dt)).tz_localize("UTC")
            px = float(order.executed.price)
            size = float(order.executed.size)
            commission = float(order.executed.comm)
            if order.isbuy():
                _bt_pending.update(entry_time=dt, entry_price=px, entry_size=size, entry_comm=commission)
            else:
                _bt_trades.append({
                    "entry_time": _bt_pending["entry_time"],
                    "entry_price": _bt_pending["entry_price"],
                    "entry_size": _bt_pending["entry_size"],
                    "entry_comm": _bt_pending["entry_comm"],
                    "exit_time": dt, "exit_price": px,
                    "exit_size": abs(size), "exit_comm": commission,
                })
                _bt_pending.clear()

cerebro = bt.Cerebro()
cerebro.broker.set_coc(False); cerebro.broker.set_coo(False)
cerebro.broker.setcommission(commission=FEE)
cerebro.broker.setcash(INIT_CASH)
bt_df = df.copy(); bt_df.index = bt_df.index.tz_localize(None)
cerebro.adddata(bt.feeds.PandasData(
    dataname=bt_df, datetime=None, open="open", high="high", low="low", close="close", volume="volume",
))
cerebro.addstrategy(SMAxStrat)
cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
cerebro.run()
bt_final_99 = cerebro.broker.getvalue()
print(f"\nBacktrader PercentSizer(99%) final: ${bt_final_99:,.4f}")

bt_tr = pd.DataFrame(_bt_trades)
# Per-trade return — note BT records "size" as integer shares (rounded down)
bt_tr["pnl_gross"] = bt_tr["exit_size"] * (bt_tr["exit_price"] - bt_tr["entry_price"])
bt_tr["pnl_net"] = bt_tr["pnl_gross"] - bt_tr["entry_comm"].abs() - bt_tr["exit_comm"].abs()
bt_tr["cash_in"] = bt_tr["entry_size"] * bt_tr["entry_price"] + bt_tr["entry_comm"].abs()
bt_tr["ret"] = bt_tr["pnl_net"] / bt_tr["cash_in"]
print(f"  BT per-trade ret mean: {bt_tr['ret'].mean():.6%},  sum: {bt_tr['ret'].sum():.6%}")
print(f"  BT compounded (100%): {(np.prod(1 + bt_tr['ret']) - 1):.6%}")

# -------- Compare per-trade returns --------
print("\n" + "=" * 80)
print("PER-TRADE GROSS RETURN COMPARISON (price ratio - 2*fee, ignoring sizing)")
print(f"  vectorbt mean: {vbt_per_trade_ret.mean():.6%},  sum: {vbt_per_trade_ret.sum():.6%}")
print(f"  Backtrader mean: {bt_tr['ret'].mean():.6%}, sum: {bt_tr['ret'].sum():.6%}")
diff = (vbt_per_trade_ret.values - bt_tr["ret"].values)
print(f"  Max abs diff per trade: {np.abs(diff).max():.10f}")
print(f"  Mean abs diff per trade: {np.abs(diff).mean():.10f}")

print("\n--- First 5 trades side-by-side ---")
side = pd.DataFrame({
    "vbt_entry_px": vbt_trades["Avg Entry Price"].head().values,
    "bt_entry_px":  bt_tr["entry_price"].head().values,
    "vbt_exit_px":  vbt_trades["Avg Exit Price"].head().values,
    "bt_exit_px":   bt_tr["exit_price"].head().values,
    "vbt_ret":      vbt_per_trade_ret.head().values,
    "bt_ret":       bt_tr["ret"].head().values,
    "bt_size":      bt_tr["entry_size"].head().values,
    "vbt_size":     vbt_trades["Size"].head().values,
})
print(side.to_string())

print("\n" + "=" * 80)
print("CONCLUSION:")
print("  If per-trade returns match within 1e-6, the $23 equity diff is purely")
print("  a sizing/compounding artifact (integer shares vs fractional, or 99% vs 100%).")
print("  If per-trade returns DIFFER, there's a real engine semantic issue.")
