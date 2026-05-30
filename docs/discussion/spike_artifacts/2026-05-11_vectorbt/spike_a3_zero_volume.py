"""Spike A.3: 24-bar zero-volume deferral.

Goal:
  Verify that a vectorbt-side preprocessing implementation of the project's
  AlphaBroker zero-volume deferral produces semantically equivalent trades
  to AlphaBroker (defined in backtest/execution_model.py).

Strategy:
  1. Pick a window containing the 2023-03-24 zero-volume bar (a known event
     in the dataset per CLAUDE.md).
  2. Use SMA crossover signals (simplest).
  3. Run Backtrader with AlphaBroker (real deferral).
  4. Run vectorbt with a preprocessing function that mirrors AlphaBroker's
     deferral semantic: if signal would fill at bar t+1 with volume==0, defer
     entry/exit to next bar with volume>0; if not found in 24 bars, cancel.
  5. Compare trade lists.
"""

from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import backtrader as bt
import vectorbt as vbt

PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
sys.path.insert(0, PROJECT_ROOT)

from backtest.execution_model import AlphaBroker, MAX_DEFER_BARS

DATA_PATH = f"{PROJECT_ROOT}/data/raw/btcusdt_1h.parquet"
START = "2023-03-15"   # ~1 week before the zero-vol bar
END = "2023-04-15"     # ~3 weeks after
FAST = 20
SLOW = 50
FEE = 0.0007
INIT_CASH = 10000.0

df = pd.read_parquet(DATA_PATH)
df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True)
df = df.set_index("open_time_utc").sort_index().loc[START:END].copy()
close = df["close"].astype(float)
open_ = df["open"].astype(float)
volume = df["volume"].astype(float)
print(f"Loaded {len(df)} bars from {df.index[0]} to {df.index[-1]}")
zero_vol_bars = df.index[volume == 0]
print(f"Zero-volume bars in window: {len(zero_vol_bars)} -> {list(zero_vol_bars)}")

fast_sma = close.rolling(window=FAST).mean()
slow_sma = close.rolling(window=SLOW).mean()
prev_diff = fast_sma.shift(1) - slow_sma.shift(1)
curr_diff = fast_sma - slow_sma
golden_cross = (prev_diff <= 0) & (curr_diff > 0)
death_cross = (prev_diff >= 0) & (curr_diff < 0)
print(f"Golden crosses: {golden_cross.sum()},   Death crosses: {death_cross.sum()}")
print(f"  Golden cross dates: {list(golden_cross[golden_cross].index)}")
print(f"  Death cross dates:  {list(death_cross[death_cross].index)}")

# =================================================================
# Backtrader with AlphaBroker (real project broker)
# =================================================================
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
            if order.isbuy():
                pending["et"], pending["ep"] = dt, px
            else:
                trades.append({"entry_time": pending["et"], "entry_price": pending["ep"],
                               "exit_time": dt, "exit_price": px})
                pending.clear()

trades, pending = [], {}
cerebro = bt.Cerebro()
cerebro.broker = AlphaBroker()        # ← KEY: use project's custom broker
cerebro.broker.set_coc(False); cerebro.broker.set_coo(False)
cerebro.broker.setcommission(commission=FEE)
cerebro.broker.setcash(INIT_CASH)
bt_df = df.copy(); bt_df.index = bt_df.index.tz_localize(None)
cerebro.adddata(bt.feeds.PandasData(
    dataname=bt_df, datetime=None, open="open", high="high", low="low",
    close="close", volume="volume",
))
cerebro.addstrategy(SMAxStrat)
cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
cerebro.run()
bt_trades = pd.DataFrame(trades)
print(f"\nBacktrader-AlphaBroker: {len(bt_trades)} trades")
if not bt_trades.empty:
    print(bt_trades.to_string())


# =================================================================
# vectorbt with preprocessing-based deferral
# =================================================================
def defer_signal_to_next_valid_bar(
    raw_signal: pd.Series,
    volume_series: pd.Series,
    max_defer: int = MAX_DEFER_BARS,
) -> pd.Series:
    """Given a boolean signal at bar t (meaning: fill at bar t),
    if volume[t] == 0, defer to next bar with volume > 0, up to max_defer bars.

    Returns a new boolean signal with deferred fire-times.
    """
    sig = raw_signal.to_numpy().copy()
    vol = volume_series.to_numpy()
    n = len(sig)
    out = np.zeros(n, dtype=bool)
    for t in range(n):
        if not sig[t]:
            continue
        target = t
        while target < n and vol[target] == 0:
            if (target - t) >= max_defer:
                target = -1     # cancel
                break
            target += 1
        if target >= 0 and target < n:
            out[target] = True
    return pd.Series(out, index=raw_signal.index)

entries_raw_shifted = golden_cross.shift(1).fillna(False).astype(bool)
exits_raw_shifted = death_cross.shift(1).fillna(False).astype(bool)

# Defer to next non-zero-volume bar
entries_deferred = defer_signal_to_next_valid_bar(entries_raw_shifted, volume)
exits_deferred = defer_signal_to_next_valid_bar(exits_raw_shifted, volume)

# Check if any deferrals actually happened in this window
def show_deferrals(raw, deferred, label):
    raw_idx = list(raw[raw].index)
    def_idx = list(deferred[deferred].index)
    if raw_idx != def_idx:
        print(f"  {label}: deferrals occurred")
        for r, d in zip(raw_idx, def_idx):
            if r != d:
                print(f"    raw {r}  ->  deferred {d}")
    else:
        print(f"  {label}: no deferrals needed (no zero-volume bars in signal path)")

print("\nVectorbt preprocessing-side deferral:")
show_deferrals(entries_raw_shifted, entries_deferred, "entries")
show_deferrals(exits_raw_shifted, exits_deferred, "exits")

pf = vbt.Portfolio.from_signals(
    close=close,
    entries=entries_deferred,
    exits=exits_deferred,
    price=open_,
    fees=FEE,
    init_cash=INIT_CASH,
    freq="1H",
)
vbt_t = pf.trades.records_readable
if not vbt_t.empty:
    vbt_trades = vbt_t.rename(columns={
        "Entry Timestamp": "entry_time", "Avg Entry Price": "entry_price",
        "Exit Timestamp": "exit_time", "Avg Exit Price": "exit_price",
    })[["entry_time", "entry_price", "exit_time", "exit_price"]]
else:
    vbt_trades = pd.DataFrame(columns=["entry_time", "entry_price", "exit_time", "exit_price"])
print(f"\nvectorbt with preproc-deferral: {len(vbt_trades)} trades")
if not vbt_trades.empty:
    print(vbt_trades.to_string())

# Compare
print("\n" + "=" * 70)
print("COMPARISON: BT-AlphaBroker vs vectorbt-preproc-defer")
n = min(len(bt_trades), len(vbt_trades))
if n == 0:
    print("  No trades to compare in this window")
else:
    a = bt_trades.iloc[:n].reset_index(drop=True)
    b = vbt_trades.iloc[:n].reset_index(drop=True)
    a["entry_time"] = pd.to_datetime(a["entry_time"], utc=True)
    a["exit_time"]  = pd.to_datetime(a["exit_time"],  utc=True)
    b["entry_time"] = pd.to_datetime(b["entry_time"], utc=True)
    b["exit_time"]  = pd.to_datetime(b["exit_time"],  utc=True)
    et = (a["entry_time"] == b["entry_time"]).all()
    xt = (a["exit_time"]  == b["exit_time"]).all()
    ep_d = (a["entry_price"].astype(float) - b["entry_price"].astype(float)).abs().max()
    xp_d = (a["exit_price"].astype(float)  - b["exit_price"].astype(float)).abs().max()
    print(f"  entry_time match: {et}  exit_time match: {xt}")
    print(f"  entry_price max abs diff: {ep_d:.10f}")
    print(f"  exit_price  max abs diff: {xp_d:.10f}")
    if not et or not xt or ep_d > 1e-6 or xp_d > 1e-6:
        side = pd.DataFrame({
            "BT_et": a["entry_time"], "VBT_et": b["entry_time"],
            "BT_ep": a["entry_price"].astype(float), "VBT_ep": b["entry_price"].astype(float),
            "BT_xt": a["exit_time"],  "VBT_xt": b["exit_time"],
            "BT_xp": a["exit_price"].astype(float),  "VBT_xp": b["exit_price"].astype(float),
        })
        print(side.to_string())
