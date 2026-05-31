"""Carry 8h funding features onto the 1h bar grid by a backward as-of join.

DESIGN INVARIANT: bar N (close-time ``c``) receives the most recent settlement
with ``calc_time <= c`` — a discrete-settlement carry-forward, NOT price
interpolation and never a future settlement. Honors the project execution
convention (signal at N's close uses only data available at N's close). Bars
before the first settlement carry NaN. All times UTC.
"""

from __future__ import annotations

import pandas as pd


def carry_funding_to_bars(
    bars: pd.DataFrame,
    funding_feat: pd.DataFrame,
    cols: list[str],
) -> pd.DataFrame:
    """Carry the listed funding-feature columns onto the 1h bar grid.

    Inputs:
        bars: DataFrame with a UTC tz-aware ``open_time_utc`` column (the 1h
            bar grid). Any other columns (e.g. OHLCV) are preserved.
        funding_feat: DataFrame with a UTC tz-aware ``open_time_utc`` settlement
            column plus the feature columns named in ``cols``.
        cols: the funding-feature column names to carry.
    Computation: ``pd.merge_asof(direction="backward")`` keyed on
        ``open_time_utc`` — each bar at close ``c`` receives the value from the
        most recent settlement with ``open_time_utc <= c``. Both frames are
        sorted on the key (a ``merge_asof`` precondition); sorting the right
        frame is what makes the carry order-independent (future settlements
        cannot affect an earlier bar).
    Output: ``bars`` (original columns preserved, row count + order unchanged)
        with one carried column per name in ``cols``.
    Null policy: bars before the first settlement carry NaN (no settlement
        satisfies ``calc_time <= c``).
    """
    left = bars.sort_values("open_time_utc")
    right = funding_feat[["open_time_utc", *cols]].sort_values("open_time_utc")
    merged = pd.merge_asof(left, right, on="open_time_utc", direction="backward")
    return merged
