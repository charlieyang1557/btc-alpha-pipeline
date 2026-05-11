"""Spike A: 3-way comparison of SMA crossover backtest.

Engines compared:
  1. Manual numpy (oracle — explicit, verifiable by hand)
  2. Backtrader (the project's current engine — set_coc(False) + set_coo(False) + 7bps)
  3. vectorbt (candidate — entries.shift(1) + exits.shift(1) + price=open + fees=0.0007)

Hypothesis under test:
  vectorbt's `Portfolio.from_signals(close=close, entries=entries.shift(1),
  exits=exits.shift(1), price=open, fees=0.0007)` produces a trade list
  byte-equivalent to Backtrader's market-orders-default-fill-on-next-open under
  the same SMA crossover signals on the same OHLCV data.

Strategy: SMA crossover, fast=20, slow=50, long-only, fully-invested-or-flat.
Data: btcusdt_1h.parquet, window 2024-01-01 to 2024-04-01 (≈ 3 months 1h).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import backtrader as bt
import vectorbt as vbt

DATA_PATH = "/Users/yutianyang/Documents/GitHub/btc-alpha-pipeline/data/raw/btcusdt_1h.parquet"
START = "2024-01-01"
END = "2024-04-01"
FAST = 20
SLOW = 50
FEE = 0.0007
INIT_CASH = 10000.0

# ---------- Load data ----------
df_full = pd.read_parquet(DATA_PATH)
df_full["open_time_utc"] = pd.to_datetime(df_full["open_time_utc"], utc=True)
df = df_full.set_index("open_time_utc").sort_index()
df = df.loc[START:END].copy()
print(f"Loaded {len(df)} bars from {df.index[0]} to {df.index[-1]}")
print(f"Columns: {list(df.columns)}")

close = df["close"].astype(float)
open_ = df["open"].astype(float)

# ---------- Compute SMAs + crossover signals (shared across all engines) ----------
fast_sma = close.rolling(window=FAST).mean()
slow_sma = close.rolling(window=SLOW).mean()
prev_diff = fast_sma.shift(1) - slow_sma.shift(1)
curr_diff = fast_sma - slow_sma
golden_cross = (prev_diff <= 0) & (curr_diff > 0)
death_cross = (prev_diff >= 0) & (curr_diff < 0)
print(f"Golden crosses: {golden_cross.sum()}")
print(f"Death crosses: {death_cross.sum()}")

# ---------- ORACLE: Manual numpy simulation ----------
# Signal at bar t close → fill at bar (t+1) open.
oracle_trades = []
in_pos = False
entry_t, entry_px = None, None
for t in range(len(df)):
    if t + 1 >= len(df):
        break
    if not in_pos and bool(golden_cross.iloc[t]):
        entry_t = df.index[t + 1]
        entry_px = float(open_.iloc[t + 1])
        in_pos = True
    elif in_pos and bool(death_cross.iloc[t]):
        exit_t = df.index[t + 1]
        exit_px = float(open_.iloc[t + 1])
        oracle_trades.append(
            {"entry_time": entry_t, "entry_price": entry_px, "exit_time": exit_t, "exit_price": exit_px}
        )
        in_pos = False

oracle_df = pd.DataFrame(oracle_trades)
print(f"\nORACLE: {len(oracle_df)} completed trades")

# ---------- BACKTRADER ----------
_bt_trades: list[dict] = []
_bt_pending_entry: dict = {}

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
            dt = bt.num2date(order.executed.dt)
            dt = pd.Timestamp(dt).tz_localize("UTC")
            px = float(order.executed.price)
            if order.isbuy():
                _bt_pending_entry["entry_time"] = dt
                _bt_pending_entry["entry_price"] = px
            else:
                _bt_trades.append(
                    {
                        "entry_time": _bt_pending_entry["entry_time"],
                        "entry_price": _bt_pending_entry["entry_price"],
                        "exit_time": dt,
                        "exit_price": px,
                    }
                )
                _bt_pending_entry.clear()

cerebro = bt.Cerebro()
cerebro.broker.set_coc(False)
cerebro.broker.set_coo(False)
cerebro.broker.setcommission(commission=FEE)
cerebro.broker.setcash(INIT_CASH)

bt_df = df.copy()
bt_df.index = bt_df.index.tz_localize(None)
data_feed = bt.feeds.PandasData(
    dataname=bt_df,
    datetime=None,
    open="open",
    high="high",
    low="low",
    close="close",
    volume="volume",
)
cerebro.adddata(data_feed)
cerebro.addstrategy(SMAxStrat)
cerebro.addsizer(bt.sizers.PercentSizer, percents=99)

bt_initial = cerebro.broker.getvalue()
cerebro.run()
bt_final = cerebro.broker.getvalue()

bt_df_trades = pd.DataFrame(_bt_trades)
print(f"\nBACKTRADER: {len(bt_df_trades)} completed trades, final value ${bt_final:,.2f}")

# ---------- vectorbt ----------
entries = golden_cross.fillna(False).astype(bool)
exits = death_cross.fillna(False).astype(bool)
entries_shifted = entries.shift(1).fillna(False).astype(bool)
exits_shifted = exits.shift(1).fillna(False).astype(bool)

pf = vbt.Portfolio.from_signals(
    close=close,
    entries=entries_shifted,
    exits=exits_shifted,
    price=open_,
    fees=FEE,
    init_cash=INIT_CASH,
    freq="1H",
)
vbt_trades = pf.trades.records_readable
vbt_final = float(pf.value().iloc[-1])
print(f"\nvectorbt: {len(vbt_trades)} completed trades, final value ${vbt_final:,.2f}")
if not vbt_trades.empty:
    print(f"vectorbt columns: {list(vbt_trades.columns)}")

# ---------- Normalize + compare ----------
def normalize(d, et, ep, xt, xp):
    if d.empty:
        return pd.DataFrame(columns=["entry_time", "entry_price", "exit_time", "exit_price"])
    out = d[[et, ep, xt, xp]].copy()
    out.columns = ["entry_time", "entry_price", "exit_time", "exit_price"]
    out["entry_time"] = pd.to_datetime(out["entry_time"], utc=True)
    out["exit_time"] = pd.to_datetime(out["exit_time"], utc=True)
    out["entry_price"] = out["entry_price"].astype(float)
    out["exit_price"] = out["exit_price"].astype(float)
    return out.reset_index(drop=True)

oracle_n = normalize(oracle_df, "entry_time", "entry_price", "exit_time", "exit_price")
bt_n = normalize(bt_df_trades, "entry_time", "entry_price", "exit_time", "exit_price")

if not vbt_trades.empty:
    et_col = next((c for c in vbt_trades.columns if "Entry Timestamp" in c or c == "Entry Index"), None)
    ep_col = next((c for c in vbt_trades.columns if "Avg Entry Price" in c or "Entry Price" in c), None)
    xt_col = next((c for c in vbt_trades.columns if "Exit Timestamp" in c or c == "Exit Index"), None)
    xp_col = next((c for c in vbt_trades.columns if "Avg Exit Price" in c or "Exit Price" in c), None)
    print(f"vbt detected cols: entry_t={et_col} entry_px={ep_col} exit_t={xt_col} exit_px={xp_col}")
    vbt_n = normalize(vbt_trades, et_col, ep_col, xt_col, xp_col)
else:
    vbt_n = normalize(pd.DataFrame(), "x", "x", "x", "x")

print("\n" + "=" * 80)
print("TRADE-COUNT COMPARISON")
print(f"  Oracle    : {len(oracle_n)} trades")
print(f"  Backtrader: {len(bt_n)} trades")
print(f"  vectorbt  : {len(vbt_n)} trades")

def compare(label_a, a, label_b, b):
    print(f"\n--- {label_a} vs {label_b} ---")
    if len(a) != len(b):
        print(f"  COUNT MISMATCH: {len(a)} vs {len(b)}")
    n = min(len(a), len(b))
    if n == 0:
        return
    aa, bb = a.iloc[:n].reset_index(drop=True), b.iloc[:n].reset_index(drop=True)
    et_ok = (aa["entry_time"] == bb["entry_time"]).all()
    xt_ok = (aa["exit_time"] == bb["exit_time"]).all()
    ep_diff = (aa["entry_price"] - bb["entry_price"]).abs().max()
    xp_diff = (aa["exit_price"] - bb["exit_price"]).abs().max()
    print(f"  entry_time exact match: {et_ok}")
    print(f"  exit_time  exact match: {xt_ok}")
    print(f"  entry_price max abs diff: {ep_diff:.10f}")
    print(f"  exit_price  max abs diff: {xp_diff:.10f}")
    if (not et_ok) or (not xt_ok) or ep_diff > 1e-6 or xp_diff > 1e-6:
        print("  --- first 5 rows side-by-side ---")
        side = pd.concat(
            [
                aa[["entry_time", "entry_price", "exit_time", "exit_price"]].add_prefix(f"{label_a}_"),
                bb[["entry_time", "entry_price", "exit_time", "exit_price"]].add_prefix(f"{label_b}_"),
            ],
            axis=1,
        )
        print(side.head(5).to_string())

compare("Oracle", oracle_n, "Backtrader", bt_n)
compare("Oracle", oracle_n, "vectorbt", vbt_n)
compare("Backtrader", bt_n, "vectorbt", vbt_n)

print("\n" + "=" * 80)
print("PERFORMANCE COMPARISON")
print(f"  Backtrader final: ${bt_final:,.4f}  return: {(bt_final/INIT_CASH - 1):.4%}")
print(f"  vectorbt   final: ${vbt_final:,.4f}  return: {(vbt_final/INIT_CASH - 1):.4%}")
print(f"  vectorbt total_return (engine): {pf.total_return():.4%}")
