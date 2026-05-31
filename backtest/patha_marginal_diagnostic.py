# backtest/patha_marginal_diagnostic.py
"""Fenced funding-marginal-contribution diagnostic (Task C6, NEW for Path A).

LOCK Pre-registration 3 fences this as a DIAGNOSTIC ONLY: it isolates funding's
marginal contribution by comparing the funding-gated strategy's net-of-cost Sharpe
against the IDENTICAL no-funding baseline (H2/H3 = the price-trend-only book; H1 =
always-long) on the SAME forward bars. So any A-result attributes to funding's
marginal contribution, not Path B's already-dead decay-MA leg (H2/H3) or
buy-and-hold (H1).

FENCED (DESIGN INVARIANT): this never feeds N* or promotion. The returned record
always carries ``promotion_affecting=False`` and ``in_n_star=False`` — these flags
are structural constants, not derived from inputs, so no result can flip them. The
orchestrator records this diagnostic but the taxonomy/DSR/escalation never read it.

Both equity curves must cover the SAME bars (identical length); the marginal is
``Sharpe(gated_per_bar_returns) - Sharpe(baseline_per_bar_returns)`` using the
project's annualized Sharpe (backtest.metrics.compute_sharpe_ratio).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.metrics import compute_sharpe_ratio


def _per_bar_returns(equity: np.ndarray) -> np.ndarray:
    """Per-bar simple returns from an equity curve (drops the leading NaN)."""
    eq = pd.Series(np.asarray(equity, dtype=np.float64))
    return eq.pct_change().dropna().to_numpy()


def funding_marginal(
    hyp_id: str,
    gated_equity: np.ndarray | pd.Series,
    baseline_equity: np.ndarray | pd.Series,
) -> dict:
    """Compute the fenced funding-marginal Sharpe delta on identical bars.

    Args:
        hyp_id: Hypothesis id ("H1" / "H2" / "H3").
        gated_equity: The funding-gated strategy's equity curve.
        baseline_equity: The IDENTICAL no-funding baseline's equity curve, on the
            SAME bars (H2/H3 = price-trend-only; H1 = always-long).

    Returns:
        A dict: ``hyp_id``, ``gated_sharpe``, ``baseline_sharpe``,
        ``funding_marginal_sharpe`` (gated - baseline), and the FENCE flags
        ``promotion_affecting=False`` and ``in_n_star=False``.

    Raises:
        ValueError: If the two equity curves do not cover an identical bar count.
    """
    gated = np.asarray(gated_equity, dtype=np.float64)
    baseline = np.asarray(baseline_equity, dtype=np.float64)
    if gated.shape[0] != baseline.shape[0]:
        raise ValueError(
            f"funding_marginal: gated ({gated.shape[0]}) and baseline "
            f"({baseline.shape[0]}) must cover an identical bar count — the "
            f"marginal is only meaningful on the SAME bars."
        )

    gated_sharpe = compute_sharpe_ratio(_per_bar_returns(gated))
    baseline_sharpe = compute_sharpe_ratio(_per_bar_returns(baseline))
    return {
        "hyp_id": hyp_id,
        "gated_sharpe": gated_sharpe,
        "baseline_sharpe": baseline_sharpe,
        "funding_marginal_sharpe": gated_sharpe - baseline_sharpe,
        # FENCE (structural constants; never derived from inputs).
        "promotion_affecting": False,
        "in_n_star": False,
    }
