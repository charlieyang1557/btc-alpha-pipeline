"""Hand-coded strategies for WF boundary regression tests.

Each strategy is designed to exercise one specific aspect of the
corrected boundary semantic. All strategies use Backtrader's standard
machinery (no custom prenext, no exotic state) so they're representative
of the project's actual strategy population.
"""
from __future__ import annotations
import backtrader as bt
from strategies.template import BaseStrategy


class TrainProfitTestFlat(BaseStrategy):
    """Buys on the second next() call, closes 24 next() calls later, then idle.

    Decision logic uses the strategy's own bar-count tracking (not absolute
    timestamps and not test_start coupling) to be robust to whatever WF
    window configuration the test invokes. Intent: trade early in the
    feed (which under broken engine = train period; under wrapper =
    suppressed). Under broken engine, these trades fire pre-test_start
    and contaminate test metrics. Under gated wrapper, next() is
    suppressed pre-test_start so the trades never fire and only the
    first 26 post-test_start bars contain the buy/close window.

    Used by T1 (test return excludes train PnL): under broken engine,
    train trades produce PnL that contaminates "test return"; under
    wrapper, no train trades → clean test return.

    Used by T2 (zero test trades implies zero test return): under
    wrapper, the buy fires on the second post-test_start next() and
    closes 24 bars later — but with a flat-test-period synthetic price,
    the trade has zero PnL. Combined with synthetic data that produces
    flat test prices, T2's "zero test return" assertion holds because
    no trades net any PnL.

    Note for fixture authors: this strategy assumes the test author
    constructs synthetic data such that (a) under broken engine, the
    buy fires at feed bar 0/1 (during train period with profitable
    trajectory) and closes at bar 25 (still in train, still profitable);
    (b) under wrapper, _bar_count starts incrementing at the first
    post-test_start next() call, so the buy fires deep in test where
    prices are flat. Both scenarios are exercised by `make_trending_then_flat`
    fixture data.
    """
    STRATEGY_NAME = "train_profit_test_flat"
    WARMUP_BARS = 0

    def __init__(self) -> None:
        self._bar_count = 0

    def next(self) -> None:
        self._bar_count += 1
        if self._bar_count == 2 and not self.position:
            self.buy()
        elif self._bar_count == 26 and self.position:
            self.close()


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
