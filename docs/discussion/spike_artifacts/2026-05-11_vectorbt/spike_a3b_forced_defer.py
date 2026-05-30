"""Spike A.3b: FORCE a signal to land on the 2023-03-24 12:00 zero-volume bar.

Goal: verify AlphaBroker and our preprocessing produce semantically equivalent
deferred trades when a signal actually hits a zero-volume bar.

Approach: bypass SMA crossover. Inject a synthetic entry signal at bar
2023-03-24 11:00 (signal at close of 11:00 → fill bar would be 12:00 → zero
volume → must defer).
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
ZERO_VOL_BAR = pd.Timestamp("2023-03-24 12:00:00", tz="UTC")
START = "2023-03-22"
END = "2023-03-27"
FEE = 0.0007
INIT_CASH = 10000.0

df = pd.read_parquet(DATA_PATH)
df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True)
df = df.set_index("open_time_utc").sort_index().loc[START:END].copy()
print(f"Window: {df.index[0]} to {df.index[-1]} ({len(df)} bars)")
print(f"Bar at {ZERO_VOL_BAR}: volume = {df.loc[ZERO_VOL_BAR, 'volume']}")

# Construct synthetic signals:
#   entry signal at 11:00 → fill bar 12:00 (zero-vol) → defer expected
#   exit signal 24 bars later (well after deferral resolves)
ENTRY_SIG_BAR = pd.Timestamp("2023-03-24 11:00:00", tz="UTC")  # signal at close
EXIT_SIG_BAR = pd.Timestamp("2023-03-25 06:00:00", tz="UTC")   # ~20h later

entries_at_close = pd.Series(False, index=df.index)
exits_at_close = pd.Series(False, index=df.index)
entries_at_close.loc[ENTRY_SIG_BAR] = True
exits_at_close.loc[EXIT_SIG_BAR] = True
print(f"Synthetic entry signal at {ENTRY_SIG_BAR}")
print(f"Synthetic exit  signal at {EXIT_SIG_BAR}")

# =================================================================
# Backtrader with AlphaBroker
# =================================================================
trades, pending = [], {}

class SyntheticStrat(bt.Strategy):
    """Fires synthetic signals at hardcoded bar timestamps."""
    def __init__(self):
        self.entry_bar = ENTRY_SIG_BAR.tz_localize(None)
        self.exit_bar = EXIT_SIG_BAR.tz_localize(None)
    def next(self):
        dt_naive = self.data.datetime.datetime(0)
        if dt_naive == self.entry_bar and not self.position:
            self.buy()
        elif dt_naive == self.exit_bar and self.position:
            self.close()
    def notify_order(self, order):
        if order.status == order.Completed:
            dt = pd.Timestamp(bt.num2date(order.executed.dt)).tz_localize("UTC")
            px = float(order.executed.price)
            if order.isbuy():
                pending["et"], pending["ep"] = dt, px
                print(f"  BT BUY  filled at {dt}  price={px}")
            else:
                trades.append({"entry_time": pending["et"], "entry_price": pending["ep"],
                               "exit_time": dt, "exit_price": px})
                pending.clear()
                print(f"  BT SELL filled at {dt}  price={px}")
        elif order.status == order.Cancelled:
            print(f"  BT order CANCELLED (deferral exceeded {MAX_DEFER_BARS} bars)")

print("\n--- Backtrader with AlphaBroker ---")
cerebro = bt.Cerebro()
cerebro.broker = AlphaBroker()
cerebro.broker.set_coc(False); cerebro.broker.set_coo(False)
cerebro.broker.setcommission(commission=FEE)
cerebro.broker.setcash(INIT_CASH)
bt_df = df.copy(); bt_df.index = bt_df.index.tz_localize(None)
cerebro.adddata(bt.feeds.PandasData(dataname=bt_df, datetime=None,
    open="open", high="high", low="low", close="close", volume="volume"))
cerebro.addstrategy(SyntheticStrat)
cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
cerebro.run()
bt_trades = pd.DataFrame(trades)
print(f"\nBacktrader trades:")
print(bt_trades.to_string() if not bt_trades.empty else "  (none)")

# =================================================================
# vectorbt with preprocessing-based deferral
# =================================================================
def defer_signal_to_next_valid_bar(
    raw_signal: pd.Series,
    volume_series: pd.Series,
    max_defer: int = MAX_DEFER_BARS,
) -> pd.Series:
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
                target = -1
                break
            target += 1
        if target >= 0 and target < n:
            out[target] = True
    return pd.Series(out, index=raw_signal.index)

# Shift signals to N+1 (signal at bar t close → fill at t+1)
entries_raw = entries_at_close.shift(1).fillna(False).astype(bool)
exits_raw   = exits_at_close.shift(1).fillna(False).astype(bool)
print(f"\nRaw entries (at fill bar): {list(entries_raw[entries_raw].index)}")
print(f"Raw exits   (at fill bar): {list(exits_raw[exits_raw].index)}")

entries_def = defer_signal_to_next_valid_bar(entries_raw, df["volume"])
exits_def   = defer_signal_to_next_valid_bar(exits_raw,   df["volume"])
print(f"After defer entries: {list(entries_def[entries_def].index)}")
print(f"After defer exits:   {list(exits_def[exits_def].index)}")

print("\n--- vectorbt with preprocessing-defer ---")
pf = vbt.Portfolio.from_signals(
    close=df["close"], entries=entries_def, exits=exits_def, price=df["open"],
    fees=FEE, init_cash=INIT_CASH, freq="1H",
)
vbt_t = pf.trades.records_readable
if not vbt_t.empty:
    vbt_trades = vbt_t.rename(columns={
        "Entry Timestamp": "entry_time", "Avg Entry Price": "entry_price",
        "Exit Timestamp": "exit_time", "Avg Exit Price": "exit_price",
    })[["entry_time", "entry_price", "exit_time", "exit_price"]]
else:
    vbt_trades = pd.DataFrame()
print(f"vectorbt trades:")
print(vbt_trades.to_string() if not vbt_trades.empty else "  (none)")

# =================================================================
# Compare
# =================================================================
print("\n" + "=" * 70)
print("COMPARISON")
if len(bt_trades) != len(vbt_trades):
    print(f"  COUNT MISMATCH: BT={len(bt_trades)} VBT={len(vbt_trades)}")
elif len(bt_trades) == 0:
    print("  Both empty — no comparison possible")
else:
    a = bt_trades.reset_index(drop=True)
    b = vbt_trades.reset_index(drop=True)
    a["entry_time"] = pd.to_datetime(a["entry_time"], utc=True)
    a["exit_time"]  = pd.to_datetime(a["exit_time"],  utc=True)
    b["entry_time"] = pd.to_datetime(b["entry_time"], utc=True)
    b["exit_time"]  = pd.to_datetime(b["exit_time"],  utc=True)
    et = (a["entry_time"] == b["entry_time"]).all()
    xt = (a["exit_time"]  == b["exit_time"]).all()
    ep_d = abs(a["entry_price"].astype(float).iloc[0] - b["entry_price"].astype(float).iloc[0])
    xp_d = abs(a["exit_price"].astype(float).iloc[0]  - b["exit_price"].astype(float).iloc[0])
    print(f"  entry_time match: {et}  exit_time match: {xt}")
    print(f"  entry_price diff: {ep_d:.10f}")
    print(f"  exit_price  diff: {xp_d:.10f}")
    if et and xt and ep_d < 1e-6 and xp_d < 1e-6:
        print(f"\n  ✅ AlphaBroker deferral semantic REPRODUCED in vectorbt preprocessing.")
        print(f"     Entry signal at {ENTRY_SIG_BAR} → fill bar would be 12:00 (zero-vol)")
        print(f"     → deferred to next valid bar (vectorbt + Backtrader agreed)")
