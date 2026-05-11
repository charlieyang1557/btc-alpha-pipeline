"""Spike A.2b: investigate mean_reversion 23-vs-24 trade count mismatch.

Spike A.2 found:
  - momentum: 36 vs 36, byte-equivalent
  - mean_reversion: 23 (BT) vs 24 (VBT), first 23 match exactly

Hypotheses:
  H1: vectorbt fires an entry signal on a warmup-edge bar that BT's
      prenext()/next() split skips
  H2: vectorbt has different StdDev ddof from BT
  H3: end-of-window edge — vectorbt closes a position BT didn't get to
  H4: std<1e-10 guard fires differently due to float precision
"""

from __future__ import annotations

import sys
import numpy as np
import pandas as pd
import backtrader as bt
import vectorbt as vbt

PROJECT_ROOT = "/Users/yutianyang/Documents/GitHub/btc-alpha-pipeline"
DATA_PATH = f"{PROJECT_ROOT}/data/raw/btcusdt_1h.parquet"
START = "2024-01-01"
END = "2024-04-01"
FEE = 0.0007
INIT_CASH = 10000.0

df = pd.read_parquet(DATA_PATH)
df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True)
df = df.set_index("open_time_utc").sort_index().loc[START:END].copy()
close = df["close"].astype(float)
open_ = df["open"].astype(float)
print(f"Window: {df.index[0]} to {df.index[-1]} ({len(df)} bars)")

# ---- Backtrader: record EVERY order attempt, not just executed ----
bt_orders, pending = [], {}

class BTMeanRev(bt.Strategy):
    params = (("period", 48), ("entry_z", -2.0), ("exit_z", 0.0))
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)
        self.std = bt.indicators.StdDev(self.data.close, period=self.p.period)
    def next(self):
        s = self.std[0]
        if s < 1e-10:
            return
        z = (self.data.close[0] - self.sma[0]) / s
        bar_dt = pd.Timestamp(self.data.datetime.datetime(0)).tz_localize("UTC")
        if z < self.p.entry_z and not self.position:
            bt_orders.append({"bar": bar_dt, "side": "BUY_signal", "z": z})
            self.buy()
        elif z > self.p.exit_z and self.position:
            bt_orders.append({"bar": bar_dt, "side": "SELL_signal", "z": z})
            self.close()
    def notify_order(self, order):
        if order.status == order.Completed:
            dt = pd.Timestamp(bt.num2date(order.executed.dt)).tz_localize("UTC")
            px = float(order.executed.price)
            if order.isbuy():
                pending["et"], pending["ep"] = dt, px
            else:
                bt_trades.append({
                    "entry_time": pending["et"], "entry_price": pending["ep"],
                    "exit_time": dt, "exit_price": px,
                })
                pending.clear()

bt_trades = []
cerebro = bt.Cerebro()
cerebro.broker.set_coc(False); cerebro.broker.set_coo(False)
cerebro.broker.setcommission(commission=FEE)
cerebro.broker.setcash(INIT_CASH)
bt_df = df.copy(); bt_df.index = bt_df.index.tz_localize(None)
cerebro.adddata(bt.feeds.PandasData(dataname=bt_df, datetime=None,
    open="open", high="high", low="low", close="close", volume="volume"))
cerebro.addstrategy(BTMeanRev)
cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
cerebro.run()

bt_trades_df = pd.DataFrame(bt_trades)
bt_orders_df = pd.DataFrame(bt_orders)
print(f"\nBacktrader: {len(bt_orders_df)} signal events, {len(bt_trades_df)} completed trades")

# ---- vectorbt: compute signals & match each bar by bar ----
sma48 = close.rolling(window=48).mean()
std48 = close.rolling(window=48).std(ddof=0)
z_full = (close - sma48) / std48
guard = std48 >= 1e-10
entries_at_close = (z_full < -2.0).fillna(False) & guard
exits_at_close = (z_full > 0.0).fillna(False) & guard

# vectorbt's "fire at signal" timestamps (i.e. signal at bar t close)
vbt_entry_signals = list(entries_at_close[entries_at_close].index)
vbt_exit_signals = list(exits_at_close[exits_at_close].index)
print(f"vectorbt-side: {entries_at_close.sum()} raw entry signals, "
      f"{exits_at_close.sum()} raw exit signals (at signal bar)")

# ---- Cross-check BT's signal-fire bars vs VBT's raw signals ----
bt_signal_bars = list(bt_orders_df["bar"])

print("\n--- Diagnostic: first 5 BT signal events ---")
print(bt_orders_df.head().to_string())

print("\n--- Diagnostic: first 5 VBT entry-signal bars ---")
for b in vbt_entry_signals[:5]:
    z_val = z_full.loc[b]
    print(f"  {b}  z={z_val:.6f}")

# Side-by-side: align by bar timestamp
all_bars = sorted(set(bt_signal_bars) | set(vbt_entry_signals) | set(vbt_exit_signals))
diffs = []
for b in all_bars:
    bt_here = bt_orders_df.loc[bt_orders_df["bar"] == b, "side"].tolist()
    vbt_entry = b in entries_at_close.index and bool(entries_at_close.loc[b])
    vbt_exit = b in exits_at_close.index and bool(exits_at_close.loc[b])
    diffs.append({
        "bar": b,
        "bt_signal": ",".join(bt_here) if bt_here else "",
        "vbt_entry": vbt_entry,
        "vbt_exit": vbt_exit,
        "z": float(z_full.loc[b]) if b in z_full.index else None,
    })

diffs_df = pd.DataFrame(diffs)
# Only show rows where BT and VBT disagree
mismatched = diffs_df[
    ((diffs_df["bt_signal"].str.contains("BUY", na=False)) & (~diffs_df["vbt_entry"])) |
    ((diffs_df["bt_signal"].str.contains("SELL", na=False)) & (~diffs_df["vbt_exit"])) |
    ((diffs_df["bt_signal"] == "") & (diffs_df["vbt_entry"] | diffs_df["vbt_exit"]))
]
print(f"\n--- Bar-by-bar signal mismatches: {len(mismatched)} ---")
if not mismatched.empty:
    print(mismatched.to_string())
else:
    print("  (none — signal sets identical at bar-level)")

# ---- Run vectorbt portfolio for trade-list comparison ----
pf = vbt.Portfolio.from_signals(
    close=close,
    entries=entries_at_close.shift(1).fillna(False).astype(bool),
    exits=exits_at_close.shift(1).fillna(False).astype(bool),
    price=open_, fees=FEE, init_cash=INIT_CASH, freq="1H",
)
vbt_t = pf.trades.records_readable
if not vbt_t.empty:
    vbt_trades = vbt_t.rename(columns={
        "Entry Timestamp": "entry_time", "Avg Entry Price": "entry_price",
        "Exit Timestamp": "exit_time", "Avg Exit Price": "exit_price",
    })[["entry_time", "entry_price", "exit_time", "exit_price"]]
else:
    vbt_trades = pd.DataFrame()

print(f"\nVBT trades: {len(vbt_trades)},  BT trades: {len(bt_trades_df)}")
print("\n--- Last 3 BT trades ---")
print(bt_trades_df.tail(3).to_string())
print("\n--- Last 3 VBT trades ---")
print(vbt_trades.tail(3).to_string())

# Check what's in the EXTRA VBT trade
if len(vbt_trades) > len(bt_trades_df):
    print(f"\n--- VBT has {len(vbt_trades) - len(bt_trades_df)} extra trade(s) ---")
    extra = vbt_trades.iloc[len(bt_trades_df):]
    print(extra.to_string())
