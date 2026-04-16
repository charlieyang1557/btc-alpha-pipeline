"""Base strategy class for the BTC Alpha Pipeline.

All strategies (manual baselines and AI-generated) must subclass
BaseStrategy and override STRATEGY_NAME and WARMUP_BARS.

Keeps the template thin — we don't know what Phase 2 AI strategies
will need, so avoid speculative abstractions.
"""

from __future__ import annotations

from typing import Any

import backtrader as bt


class BaseStrategy(bt.Strategy):
    """Base class for all strategies in the pipeline.

    Subclasses MUST override:
        STRATEGY_NAME: Unique identifier for registry logging.
        WARMUP_BARS: Number of bars before signals are valid.
            Backtrader handles this via prenext()/next() split:
            next() is only called after all indicators have enough data.

    Subclasses SHOULD override:
        get_params_dict(): Returns strategy params as a serializable dict.
        get_metadata(): Returns metadata for registry logging.
    """

    STRATEGY_NAME: str = "unnamed"
    WARMUP_BARS: int = 0

    def get_params_dict(self) -> dict[str, Any]:
        """Return strategy parameters as a JSON-serializable dict.

        Default implementation returns all Backtrader params.
        Override if you need custom serialization.

        Returns:
            Dict of parameter name to value.
        """
        return {k: v for k, v in self.params._getkwargs().items()}

    def get_metadata(self) -> dict[str, Any]:
        """Return strategy metadata for registry logging.

        Returns:
            Dict with strategy_name, warmup_bars, and params.
        """
        return {
            "strategy_name": self.STRATEGY_NAME,
            "warmup_bars": self.WARMUP_BARS,
            "params": self.get_params_dict(),
        }
