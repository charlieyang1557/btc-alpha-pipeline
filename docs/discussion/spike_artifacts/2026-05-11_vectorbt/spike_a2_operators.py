"""Spike A.2: byte-equivalent verification on non-crossover operators.

Tests momentum (threshold > / <) and mean_reversion (z-score with > / < + guard)
between Backtrader and vectorbt under the same N+1 fill discipline.

Strategy specs (from strategies/baseline/):
  momentum:
    PctChange(close, period=24)
    entry: pct_change > +0.02 (default entry_threshold)
    exit:  pct_change < 0.0   (default exit_threshold)
  mean_reversion:
    sma = SMA(close, 48), std = StdDev(close, 48)
    z = (close - sma) / std  (skip if std < 1e-10)
    entry: z < -2.0
    exit:  z > 0.0
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
FEE = 0.0007
INIT_CASH = 10000.0

df = pd.read_parquet(DATA_PATH)
df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True)
df = df.set_index("open_time_utc").sort_index().loc[START:END].copy()
close = df["close"].astype(float)
open_ = df["open"].astype(float)
print(f"Loaded {len(df)} bars from {df.index[0]} to {df.index[-1]}")


def run_backtrader(strat_class) -> pd.DataFrame:
    trades, pending = [], {}

    class Wrapper(strat_class):  # type: ignore[misc]
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

    cerebro = bt.Cerebro()
    cerebro.broker.set_coc(False); cerebro.broker.set_coo(False)
    cerebro.broker.setcommission(commission=FEE)
    cerebro.broker.setcash(INIT_CASH)
    bt_df = df.copy(); bt_df.index = bt_df.index.tz_localize(None)
    cerebro.adddata(bt.feeds.PandasData(
        dataname=bt_df, datetime=None, open="open", high="high", low="low",
        close="close", volume="volume",
    ))
    cerebro.addstrategy(Wrapper)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
    cerebro.run()
    return pd.DataFrame(trades)


def run_vectorbt(entries: pd.Series, exits: pd.Series) -> pd.DataFrame:
    pf = vbt.Portfolio.from_signals(
        close=close,
        entries=entries.shift(1).fillna(False).astype(bool),
        exits=exits.shift(1).fillna(False).astype(bool),
        price=open_,
        fees=FEE,
        init_cash=INIT_CASH,
        freq="1H",
    )
    t = pf.trades.records_readable
    if t.empty:
        return pd.DataFrame(columns=["entry_time", "entry_price", "exit_time", "exit_price"])
    return t.rename(columns={
        "Entry Timestamp": "entry_time", "Avg Entry Price": "entry_price",
        "Exit Timestamp": "exit_time", "Avg Exit Price": "exit_price",
    })[["entry_time", "entry_price", "exit_time", "exit_price"]]


def compare(label_bt, bt_df, label_vbt, vbt_df):
    n_bt, n_vbt = len(bt_df), len(vbt_df)
    print(f"  {label_bt}: {n_bt} trades   |   {label_vbt}: {n_vbt} trades")
    if n_bt != n_vbt:
        print(f"  ⚠️  COUNT MISMATCH")
    n = min(n_bt, n_vbt)
    if n == 0:
        return
    a = bt_df.iloc[:n].reset_index(drop=True)
    b = vbt_df.iloc[:n].reset_index(drop=True)
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
            f"{label_bt}_et": a["entry_time"].head(5).values,
            f"{label_vbt}_et": b["entry_time"].head(5).values,
            f"{label_bt}_ep": a["entry_price"].head(5).astype(float).values,
            f"{label_vbt}_ep": b["entry_price"].head(5).astype(float).values,
        })
        print(side.to_string())


# =================================================================
# Strategy 1: momentum (threshold)
# =================================================================
print("\n" + "=" * 70)
print("Strategy 1: momentum (PctChange(24) > 0.02 entry, < 0.0 exit)")
print("=" * 70)

class BTMomentum(bt.Strategy):
    params = (("lookback", 24), ("entry_thr", 0.02), ("exit_thr", 0.0))
    def __init__(self):
        self.pct = bt.indicators.PctChange(self.data.close, period=self.p.lookback)
    def next(self):
        if self.pct[0] > self.p.entry_thr and not self.position:
            self.buy()
        elif self.pct[0] < self.p.exit_thr and self.position:
            self.close()

bt_mom_trades = run_backtrader(BTMomentum)

pct = close.pct_change(periods=24)
mom_entries = (pct > 0.02).fillna(False)
mom_exits = (pct < 0.0).fillna(False)
vbt_mom_trades = run_vectorbt(mom_entries, mom_exits)

compare("BT", bt_mom_trades, "VBT", vbt_mom_trades)


# =================================================================
# Strategy 2: mean_reversion (z-score)
# =================================================================
print("\n" + "=" * 70)
print("Strategy 2: mean_reversion (z = (close - SMA(48)) / StdDev(48); entry z<-2, exit z>0)")
print("=" * 70)

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
        if z < self.p.entry_z and not self.position:
            self.buy()
        elif z > self.p.exit_z and self.position:
            self.close()

bt_mr_trades = run_backtrader(BTMeanRev)

# vectorbt-side computation (must replicate BT's StdDev exactly)
# bt.indicators.StdDev uses biased variance with `ddof=0` (population) by default.
sma48 = close.rolling(window=48).mean()
std48 = close.rolling(window=48).std(ddof=0)
z = (close - sma48) / std48
mr_entries = (z < -2.0).fillna(False) & (std48 >= 1e-10)
mr_exits = (z > 0.0).fillna(False) & (std48 >= 1e-10)
vbt_mr_trades = run_vectorbt(mr_entries, mr_exits)

compare("BT", bt_mr_trades, "VBT", vbt_mr_trades)
