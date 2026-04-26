"""Hand-coded strategies for WF boundary regression tests.

Each strategy is designed to exercise one specific aspect of the
corrected boundary semantic. All strategies use Backtrader's standard
machinery (no custom prenext, no exotic state) so they're representative
of the project's actual strategy population.
"""
from __future__ import annotations
from datetime import datetime
import backtrader as bt
from strategies.template import BaseStrategy


class TrainOnlyStrategy(BaseStrategy):
    """Trades only inside an absolute-timestamp window strictly inside train.

    Decision logic uses ABSOLUTE timestamps (not bar counts) so the
    strategy's intent — "trade only during a train-period window" — is
    preserved across both engine states. Bar-count fixtures are a trap
    here because the wrapper's pre-test_start next() suppression makes
    the in-strategy bar counter implicitly reset across the boundary,
    converting an intended train-only fixture into a test-period
    fixture under the wrapper. Absolute timestamps are immune to that
    failure mode.

    BUY_OPEN_DATE / BUY_CLOSE_DATE are hardcoded to the T1/T2 WF config:
      train = [2024-01-01, 2024-04-30], test = [2024-05-01, 2024-05-31]
      BUY_OPEN_DATE  = 2024-01-15  (~bar 336, train uptrend ~$123)
      BUY_CLOSE_DATE = 2024-04-15  (~bar 2520, train uptrend ~$275)

    Used by T1 and T2.

    Behavior under broken engine (pre-patch reference): next() fires
    during train. Strategy enters at ~$123, exits at ~$275, banking
    ~$1517 PnL on $10k portfolio (~15% return) with size=10. Both
    legs of the trade are filtered from the test-period trade list
    by the existing trade-time filter, so total_trades=0 — but the
    equity-curve contamination yields total_return ≈ 0.15. T1 fails
    on the return assertion; T2 fails on the return assertion (the
    bug shape: zero visible trades, nonzero reported return).

    Behavior under gated wrapper (post-patch): next() is suppressed
    pre-test_start. The strategy never sees BUY_OPEN_DATE or
    BUY_CLOSE_DATE inside next(). Post-test_start the bar's datetime
    is always >= 2024-05-01 > BUY_CLOSE_DATE > BUY_OPEN_DATE, so
    neither branch fires. No trades anywhere → total_trades=0,
    total_return=0, sharpe_ratio=0. Both T1 and T2 pass.

    T2's two assertions are independently meaningful: total_trades=0
    matches both engine states (broken filters the trade out, patched
    never makes it), and total_return=0 catches the equity-curve
    contamination bug shape that the broken engine produced.

    Replaces TrainProfitTestFlat (retired in plan-amendment commit
    eb45835 during Task 5 T2 resolution). The bar-count approach was
    a fixture trap because _bar_count resets implicitly across the
    wrapper boundary, producing post-test_start trades under the
    wrapper that broke T2's invariant.
    """
    STRATEGY_NAME = "train_only_strategy"
    WARMUP_BARS = 0
    # Backtrader's self.data.datetime.datetime(0) returns NAIVE datetimes
    # (timezone information is stripped). Class attributes are naive to
    # match.
    BUY_OPEN_DATE = datetime(2024, 1, 15)
    BUY_CLOSE_DATE = datetime(2024, 4, 15)
    SIZE = 10  # ensures train-period PnL >> 1% threshold under broken engine

    def __init__(self) -> None:
        self._opened = False
        self._closed = False

    def next(self) -> None:
        # Buy gate is a CLOSED window [BUY_OPEN_DATE, BUY_CLOSE_DATE).
        # The upper bound is load-bearing under the wrapper: without it,
        # the wrapper-suppressed-then-released first next() call (at
        # bar_dt = test_start = 2024-05-01) satisfies bar_dt >= BUY_OPEN
        # and the buy fires post-test_start, defeating the train-only
        # intent. The closed window ensures the buy only fires inside
        # the train period under the broken engine and never under the
        # wrapper.
        bar_dt = self.data.datetime.datetime(0)
        if (
            not self._opened
            and self.BUY_OPEN_DATE <= bar_dt < self.BUY_CLOSE_DATE
        ):
            self.buy(size=self.SIZE)
            self._opened = True
        elif (
            self._opened
            and not self._closed
            and bar_dt >= self.BUY_CLOSE_DATE
        ):
            self.close()
            self._closed = True


class StatefulTestStrategy(BaseStrategy):
    """Increments a counter every `next()` call. Never trades.

    Used by T3 to verify decision-state isolation: under (iii),
    next() is suppressed during train (pre-test_start bars), so
    `_train_phase_counter` should be 0 at the first test-period
    next() call. Under (i) — the broken engine — next() fires
    during train too, so the counter reflects all pre-test_start
    iterations when the test period is first entered.

    Capture is timestamp-driven: the class-level `_test_start_date`
    must be set by the test before calling run_walk_forward so that
    the strategy knows which bar is the test-period boundary.
    """
    STRATEGY_NAME = "stateful_test_strategy"
    WARMUP_BARS = 0
    # Class-level capture: set to counter value at first test-period bar.
    _captured_first_next_counter: int | None = None
    # Test must set this before run to define the test-period boundary.
    _test_start_date: "datetime | None" = None

    def __init__(self) -> None:
        self._train_phase_counter: int = 0
        self._captured: bool = False

    def next(self) -> None:
        # Capture the counter value at the first bar on or after
        # _test_start_date (the boundary between train and test).
        # Under broken engine: next() fires during train, so by the
        # time we first see test_start_date, counter > 0.
        # Under patched engine: next() suppressed during train, so
        # counter = 0 at the first test-period bar.
        if not self._captured and type(self)._test_start_date is not None:
            from datetime import datetime as _dt
            bar_dt = self.data.datetime.datetime(0)
            test_start = type(self)._test_start_date
            # Compare as naive datetimes (Backtrader strips timezone).
            if isinstance(test_start, _dt) and test_start.tzinfo is not None:
                test_start_naive = test_start.replace(tzinfo=None)
            else:
                test_start_naive = test_start
            if bar_dt >= test_start_naive:
                type(self)._captured_first_next_counter = self._train_phase_counter
                self._captured = True
        self._train_phase_counter += 1


class IndicatorWarmupStrategy(BaseStrategy):
    """50-bar SMA strategy. Buys when close > SMA, exits on cross-down.

    Used by T4 to verify warmup-history-only behavior: indicator must
    be valid at first test-period bar (warmup served from pre-test
    history), and broker equity at test_start must equal initial_capital
    (no warmup-period trades affecting accounting).
    """
    STRATEGY_NAME = "indicator_warmup_strategy"
    WARMUP_BARS = 50

    def __init__(self) -> None:
        self.sma = bt.indicators.SMA(self.data.close, period=50)
        # _MinperiodGate-style warmup gating: ensure next() doesn't
        # fire until SMA is valid.
        # (Backtrader auto-derives minperiod from SMA; explicit gate
        # not strictly needed here, but kept for parallel structure
        # with DSL-compiled strategies.)

    def next(self) -> None:
        if not self.position and self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.position and self.data.close[0] < self.sma[0]:
            self.close()


class TrainProfitable(BaseStrategy):
    """Profits early in feed (bar-count 2 buy, bar-count 26 close).

    Used by T5 (cross-strategy comparability) — paired with TrainLosing.
    Bar-count tracking via self._bar_count (not absolute timestamps) so
    the strategy's intent is robust to whatever WF window configuration
    the test invokes. Under broken engine, fires during train period
    with profit (rising synthetic prices). Under wrapper, suppressed
    pre-test_start; trades fire post-test_start where prices are flat
    (zero PnL).

    Both TrainProfitable and TrainLosing must produce identical test-
    window starting equity ($10k) under the wrapper, regardless of
    pre-test_start behavior.
    """
    STRATEGY_NAME = "train_profitable"
    WARMUP_BARS = 0

    def __init__(self) -> None:
        self._bar_count = 0

    def next(self) -> None:
        self._bar_count += 1
        if self._bar_count == 2 and not self.position:
            self.buy()
        elif self._bar_count == 26 and self.position:
            self.close()


class TrainLosing(BaseStrategy):
    """Loses by buying late in train trajectory (bar-count 50 buy, 75 close).

    Paired with TrainProfitable for T5. Different bar-count thresholds
    produce different PnL outcomes under broken engine (TrainProfitable
    captures the early train uptrend; TrainLosing buys after the trend
    has played out and sells flat or down). Under wrapper, both are
    suppressed pre-test_start; identical test-window starting equity
    ($10k) regardless.
    """
    STRATEGY_NAME = "train_losing"
    WARMUP_BARS = 0

    def __init__(self) -> None:
        self._bar_count = 0

    def next(self) -> None:
        self._bar_count += 1
        if self._bar_count == 50 and not self.position:
            self.buy()
        elif self._bar_count == 75 and self.position:
            self.close()
