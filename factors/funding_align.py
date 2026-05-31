"""Carry 8h funding features onto the 1h bar grid by a backward as-of join.

DESIGN INVARIANT: bar N (close-time ``c``) receives the most recent settlement
with ``calc_time <= c`` — a discrete-settlement carry-forward, NOT price
interpolation and never a future settlement. Honors the project execution
convention (signal at N's close uses only data available at N's close). The
as-of join keys on the bar's CLOSE (``open_time_utc + bar_interval - 1ms``),
NOT its open: real funding ``calc_time`` jitters a few ms off the nominal 8h
boundary, so a settlement at 08:00:00.001 is known well before the 08:00 bar's
close (08:59:59.999) and must reach that bar, not be delayed to 09:00. A
settlement that settles after the bar's close still cannot reach the bar
(leak-free). Bars before the first settlement carry NaN. All times UTC.
"""

from __future__ import annotations

import pandas as pd


def carry_funding_to_bars(
    bars: pd.DataFrame,
    funding_feat: pd.DataFrame,
    cols: list[str],
    bar_interval: pd.Timedelta = pd.Timedelta(hours=1),
) -> pd.DataFrame:
    """Carry the listed funding-feature columns onto the 1h bar grid.

    Inputs:
        bars: DataFrame with a UTC tz-aware ``open_time_utc`` column (the 1h
            bar grid). Any other columns (e.g. OHLCV) are preserved.
        funding_feat: DataFrame with a UTC tz-aware ``open_time_utc`` settlement
            column (the funding ``calc_time``) plus the feature columns named in
            ``cols``.
        cols: the funding-feature column names to carry.
        bar_interval: the bar period (default 1h). The as-of key is the bar's
            CLOSE = ``open_time_utc + bar_interval - 1ms`` (1ms is the smallest
            representable step here; using close-minus-epsilon keeps the next
            bar's boundary settlement from leaking into this bar).
    Computation: each bar's CLOSE key ``c = open + bar_interval - 1ms`` is
        joined against the settlement ``open_time_utc`` (``calc_time``) by
        ``pd.merge_asof(direction="backward")`` — each bar receives the value
        from the most recent settlement with ``calc_time <= c``. Both frames are
        sorted on the join key (a ``merge_asof`` precondition); sorting the right
        frame is what makes the carry order-independent (a settlement that
        settles after the bar's close cannot affect that bar). The original
        ``open_time_utc``, columns, and row order are restored afterwards.
    Output: ``bars`` (original columns preserved, row count + order unchanged)
        with one carried column per name in ``cols``. The returned frame carries
        a fresh ``RangeIndex`` (any custom index on the caller's ``bars`` is
        NOT preserved — ``merge_asof`` resets the index).
    Null policy: bars whose close precedes the first settlement carry NaN (no
        settlement satisfies ``calc_time <= c``).
    """
    left = bars.sort_values("open_time_utc").reset_index(drop=True)
    # Derive the bar-close as-of key; never overwrite the real open_time_utc.
    # Subtracting a 1ms Timedelta can promote the datetime resolution (e.g.
    # ms -> us); merge_asof requires BOTH join keys to share an identical dtype,
    # so cast the settlement key to the close key's resolution (lossless upcast).
    close_key = left["open_time_utc"] + bar_interval - pd.Timedelta("1ms")
    key_dtype = close_key.dtype
    left = left.assign(_bar_close_key=close_key)
    right = (
        funding_feat[["open_time_utc", *cols]]
        .sort_values("open_time_utc")
        .reset_index(drop=True)
        .rename(columns={"open_time_utc": "_bar_close_key"})
    )
    right["_bar_close_key"] = right["_bar_close_key"].astype(key_dtype)
    merged = pd.merge_asof(
        left, right, on="_bar_close_key", direction="backward"
    )
    # Restore: drop the internal key, keep original open_time_utc + columns/order.
    merged = merged.drop(columns="_bar_close_key")
    return merged
