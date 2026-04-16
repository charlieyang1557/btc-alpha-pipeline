"""Slippage and cost models for backtest execution.

Phase 1A uses a single effective cost that combines exchange fees and
slippage into one percentage commission: 4bps taker fee + 3bps slippage
= 7bps per side (14bps round trip).

This is deliberately pessimistic and simple. It does NOT model:
- Maker vs taker fee tiers
- Volume-dependent slippage
- Volatility-scaled market impact
- Partial fills

Phase 2+ will upgrade to a volatility-scaled model.

The cost model is applied via Backtrader's setcommission() in percentage
mode. This module defines the model parameters and provides a clean
interface for configuring the broker.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import backtrader as bt
import yaml

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXECUTION_CONFIG_PATH = PROJECT_ROOT / "config" / "execution.yaml"


def load_execution_config(path: Path = EXECUTION_CONFIG_PATH) -> dict[str, Any]:
    """Load execution.yaml configuration.

    Args:
        path: Path to execution.yaml.

    Returns:
        Parsed YAML as a dict.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Execution config not found: {path}")
    with open(path) as f:
        return yaml.safe_load(f)


class ConstantSlippage:
    """Constant percentage cost model for Phase 1A.

    Combines exchange fee and slippage into a single effective commission
    applied per side of each trade.

    Attributes:
        fee_bps: Exchange fee in basis points (e.g. 4.0 for taker).
        slippage_bps: Slippage estimate in basis points (e.g. 3.0).
        total_bps: Combined effective cost per side.

    Usage:
        model = ConstantSlippage.from_config(config)
        model.apply(cerebro.broker)
    """

    def __init__(self, fee_bps: float, slippage_bps: float) -> None:
        """Initialize the cost model.

        Args:
            fee_bps: Exchange fee per side in basis points.
            slippage_bps: Slippage per side in basis points.
        """
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps

    @property
    def total_bps(self) -> float:
        """Total effective cost per side in basis points."""
        return self.fee_bps + self.slippage_bps

    @property
    def effective_commission(self) -> float:
        """Decimal rate for Backtrader setcommission().

        Returns:
            Commission as a decimal fraction (e.g. 0.0007 for 7bps).
        """
        return self.total_bps / 10_000

    @property
    def fee_model_label(self) -> str:
        """Registry fee_model field value.

        Returns:
            String label for experiment registry (e.g. 'effective_7bps_per_side').
        """
        return f"effective_{self.total_bps:g}bps_per_side"

    def apply(self, broker: bt.brokers.BackBroker) -> None:
        """Configure a Backtrader broker with this cost model.

        Sets the broker's commission to the combined effective rate.
        No separate slippage is applied — it's all in the commission.

        Args:
            broker: A Backtrader BackBroker instance (must have setcommission).
        """
        broker.setcommission(commission=self.effective_commission)
        logger.info(
            "Cost model: %s (fee=%.1fbps + slip=%.1fbps = %.1fbps per side)",
            self.fee_model_label,
            self.fee_bps,
            self.slippage_bps,
            self.total_bps,
        )

    @classmethod
    def from_config(
        cls, config: dict[str, Any] | None = None
    ) -> ConstantSlippage:
        """Create from execution.yaml config dict.

        Args:
            config: Parsed execution.yaml. If None, loads from default path.

        Returns:
            Configured ConstantSlippage instance.
        """
        if config is None:
            config = load_execution_config()
        return cls(
            fee_bps=config["cost_model"]["default_fee_bps"],
            slippage_bps=config["cost_model"]["slippage_bps"],
        )
