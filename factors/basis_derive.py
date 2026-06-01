"""Derive native-1h perp-spot basis from markprice and spot streams.

DESIGN INVARIANT: ``basis_rel[t] = (mark_close[t] - spot_close[t]) /
spot_close[t]`` — same-grid inner join on ``open_time_utc``, NO carry
or interpolation across bars. ``mark_close[t]`` and ``spot_close[t]`` are
both bar-N-close values; orders fill at bar N+1 open per the project execution
convention. The only leakage surface is cross-STREAM alignment (futures mark
grid vs spot grid); this module guards it with an inner join + sanity threshold.

Non-shared bar policy:
- Inner-join on the shared ``open_time_utc`` grid (bars missing in either
  stream are silently dropped).
- The non-shared fraction = (markprice-only count + spot-only count) /
  (size of the full union of both streams' ``open_time_utc`` sets) is logged
  at INFO and compared against ``CROSS_STREAM_DROP_TOL`` (5%).
- Raise ``ValueError("cross-stream ...")`` if fraction > 5% OR if there is
  zero overlap (no shared timestamps). This catches gross alignment bugs
  (unit/timezone errors) while passing legitimate small exchange-outage
  differences (~1.4% observed in real data).
"""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)

# Sanity threshold: if the fraction of non-shared bars across the union of the
# overlap window exceeds this value, the alignment is too broken to be explained
# by legitimate exchange-outage differences and likely indicates a bug (e.g.
# unit mismatch, timezone error). Real data shows ~1.4% legitimate non-shared.
CROSS_STREAM_DROP_TOL: float = 0.05


def derive_basis_rel(
    mark: pd.DataFrame,
    spot: pd.DataFrame,
) -> pd.DataFrame:
    """Derive native-1h ``basis_rel`` by inner-joining markprice and spot streams.

    Inputs:
        mark: DataFrame with UTC tz-aware ``open_time_utc`` and ``mark_close``
            columns (futures markprice 1h bar-close values).
        spot: DataFrame with UTC tz-aware ``open_time_utc`` and ``close``
            columns (spot 1h bar-close values).
    Computation:
        1. Sort both inputs on ``open_time_utc``.
        2. Compute the non-shared fraction = (markprice-only count +
           spot-only count) / (size of the full union of both streams'
           ``open_time_utc`` sets) for the sanity check.
        3. Log the count of markprice-only and spot-only bars at INFO.
        4. Raise ``ValueError("cross-stream ...")`` if there is zero overlap
           (no shared timestamp) or if non-shared fraction > CROSS_STREAM_DROP_TOL.
        5. Inner-join on ``open_time_utc`` and compute
           ``basis_rel = (mark_close - spot_close) / spot_close``.
    Output:
        DataFrame with columns ``["open_time_utc", "basis_rel"]``, sorted
        ascending by ``open_time_utc``, reset RangeIndex.
    Null policy:
        No NaNs introduced by construction (inner join on shared bars only;
        any NaN in ``mark_close`` or ``close`` propagates to ``basis_rel``).
        ``spot_close == 0`` yields ``basis_rel = NaN`` (not inf).
    Causality:
        Trivially causal: same-grid join with no rolling window or shift.
        ``basis_rel[t]`` depends only on ``mark_close[t]`` and
        ``spot_close[t]``. Bars strictly after ``t`` in either input have no
        effect on the value at ``t``.
    """
    # Sort both streams on the join key.
    mark = mark.sort_values("open_time_utc").reset_index(drop=True)
    spot = spot.sort_values("open_time_utc").reset_index(drop=True)

    # Guard against intra-stream duplicate timestamps, which would cause silent
    # row-multiplication on the inner merge (the 5% cross-stream set-union guard
    # does NOT catch INTRA-stream duplicates).
    if not mark["open_time_utc"].is_unique:
        raise ValueError(
            "cross-stream: duplicate open_time_utc in markprice stream — "
            "each timestamp must appear at most once."
        )
    if not spot["open_time_utc"].is_unique:
        raise ValueError(
            "cross-stream: duplicate open_time_utc in spot stream — "
            "each timestamp must appear at most once."
        )

    mark_times: pd.Index = pd.Index(mark["open_time_utc"])
    spot_times: pd.Index = pd.Index(spot["open_time_utc"])

    shared_times = mark_times.intersection(spot_times)
    n_shared = len(shared_times)

    if n_shared == 0:
        raise ValueError(
            "cross-stream alignment error: zero shared open_time_utc timestamps "
            "between markprice and spot streams. Check for timezone or unit mismatch."
        )

    # Compute non-shared fraction over the total union of both streams' timestamps.
    # Using the full union (not windowed) ensures that one stream being a strict
    # subset of the other (e.g. spot covers only t[0..4] while mark covers t[0..99])
    # is still detected as a gross misalignment.
    union_times = mark_times.union(spot_times)
    n_union = len(union_times)

    n_mark_only = len(mark_times) - n_shared
    n_spot_only = len(spot_times) - n_shared
    n_non_shared = n_mark_only + n_spot_only

    non_shared_fraction = n_non_shared / n_union if n_union > 0 else 1.0

    logger.info(
        "derive_basis_rel: markprice-only bars dropped=%d, spot-only bars dropped=%d, "
        "non-shared fraction=%.4f (tolerance=%.2f), shared bars kept=%d",
        n_mark_only,
        n_spot_only,
        non_shared_fraction,
        CROSS_STREAM_DROP_TOL,
        n_shared,
    )

    if non_shared_fraction > CROSS_STREAM_DROP_TOL:
        raise ValueError(
            f"cross-stream alignment error: non-shared bar fraction {non_shared_fraction:.4f} "
            f"exceeds tolerance {CROSS_STREAM_DROP_TOL:.2f}. "
            f"markprice-only={n_mark_only}, spot-only={n_spot_only}, "
            f"union={n_union}. Check for timezone or unit mismatch."
        )

    # Inner join: keep only the shared timestamps.
    # validate="one_to_one" enforces that neither side has duplicate join keys,
    # providing a second-layer guard even if the assertions above are somehow bypassed.
    merged = pd.merge(
        mark[["open_time_utc", "mark_close"]],
        spot[["open_time_utc", "close"]],
        on="open_time_utc",
        how="inner",
        validate="one_to_one",
    )
    merged = merged.sort_values("open_time_utc").reset_index(drop=True)
    spot_close = merged["close"].replace(0, float("nan"))
    merged["basis_rel"] = (merged["mark_close"] - spot_close) / spot_close

    return merged[["open_time_utc", "basis_rel"]]
