"""Execution model enforcing config/execution.yaml conventions.

Provides:
- AlphaBroker: Custom Backtrader broker with zero-volume fill deferral.
- configure_cerebro(): Applies fee, execution, and broker settings to a Cerebro.

Execution semantics (from execution.yaml):
- Signal computed on bar N close.
- Order fills at bar N+1 open (cheat_on_close=False, cheat_on_open=False).
- Single effective cost: 7bps per side (4bps fee + 3bps slippage).
- Zero-volume bars: defer fill to next bar with volume > 0.
  If deferral exceeds 24 bars, cancel the order.

Usage:
    cerebro = bt.Cerebro()
    configure_cerebro(cerebro)
    cerebro.adddata(feed)
    cerebro.addstrategy(MyStrategy)
    results = cerebro.run()
"""

from __future__ import annotations

import logging
from typing import Any

import backtrader as bt
from backtrader.order import Order

from backtest.slippage import ConstantSlippage, load_execution_config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_CASH = 10_000.0
MAX_DEFER_BARS = 24  # Cancel order after this many zero-volume deferrals


class AlphaBroker(bt.brokers.BackBroker):
    """Custom broker that defers fills on zero-volume bars.

    When the designated fill bar has volume == 0, the order is not executed
    and remains pending until the next bar with volume > 0. If the deferral
    exceeds MAX_DEFER_BARS (24 bars = 24 hours for 1h data), the order is
    cancelled to prevent stale fills after prolonged exchange outages.

    This logic belongs in the broker layer, NOT in strategy code. Strategies
    must never contain execution deferral logic.
    """

    params = (
        ("max_defer_bars", MAX_DEFER_BARS),
    )

    def __init__(self) -> None:
        super().__init__()
        self._defer_counts: dict[int, int] = {}

    def _try_exec(self, order: Order) -> None:
        """Override to check volume before attempting execution.

        If the current bar has zero volume, the order is deferred (left
        pending). After max_defer_bars consecutive zero-volume bars, the
        order is cancelled.

        Args:
            order: The pending order to attempt execution on.
        """
        data = order.data

        if data.volume[0] <= 0:
            ref = order.ref
            count = self._defer_counts.get(ref, 0) + 1
            self._defer_counts[ref] = count

            if count > self.p.max_defer_bars:
                logger.warning(
                    "Order %d cancelled: deferred %d bars on zero-volume",
                    ref,
                    count,
                )
                order.cancel()
                self.notify(order)
                self._defer_counts.pop(ref, None)
            else:
                logger.debug(
                    "Order %d deferred (bar %d/%d): zero volume at %s",
                    ref,
                    count,
                    self.p.max_defer_bars,
                    data.datetime.datetime(0),
                )
            return

        # Non-zero volume bar — proceed with normal execution
        self._defer_counts.pop(order.ref, None)
        super()._try_exec(order)


def configure_cerebro(
    cerebro: bt.Cerebro,
    config: dict[str, Any] | None = None,
    cash: float = DEFAULT_CASH,
) -> ConstantSlippage:
    """Apply execution.yaml settings to a Cerebro instance.

    Configures:
    - AlphaBroker with zero-volume fill deferral
    - Commission: 7bps per side effective cost
    - cheat_on_close = False (no same-bar execution)
    - cheat_on_open = False (standard next-bar-open fills)
    - Initial cash

    Args:
        cerebro: Backtrader Cerebro instance to configure.
        config: Parsed execution.yaml dict. Loads from default path if None.
        cash: Initial cash amount (default $10,000).

    Returns:
        The ConstantSlippage cost model instance (for registry logging).
    """
    if config is None:
        config = load_execution_config()

    # Install custom broker via Backtrader's official API
    broker = AlphaBroker()
    cerebro.setbroker(broker)

    # Enforce execution timing
    cerebro.broker.set_coc(False)  # No cheat-on-close
    cerebro.broker.set_coo(False)  # No cheat-on-open

    # Apply cost model
    cost_model = ConstantSlippage.from_config(config)
    cost_model.apply(cerebro.broker)

    # Set initial capital
    cerebro.broker.setcash(cash)

    logger.info(
        "Cerebro configured: cash=%.2f, coc=False, coo=False, %s",
        cash,
        cost_model.fee_model_label,
    )

    return cost_model
