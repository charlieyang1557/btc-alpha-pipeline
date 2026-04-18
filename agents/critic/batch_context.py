"""D7 BatchContext — immutable per-call context for the critic.

Constructed fresh for each D7 call from D6 state. Must NOT be cached
across calls.

Key invariants:
    - ``prior_factor_sets`` excludes the current call and excludes any
      prior call with empty factor set (matches D6 Stage 2d
      ``valid_with_empty_factor_set_count`` exclusion policy).
    - All dict/frozenset fields are immutable snapshots taken at batch
      start. They do NOT change mid-batch.
    - ``theme_anchor_factors`` encodes the flag condition from D7a
      Deliverable 5 (theme_anchor_missing).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet


# Canonical theme-hint mapping — matches D6 THEME_HINTS.
# CONTRACT BOUNDARY: telemetry-only in D6; structural input in D7a.
THEME_HINTS: dict[str, FrozenSet[str]] = {
    "momentum": frozenset({
        "return_1h", "return_24h", "return_168h", "rsi_14", "macd_hist",
    }),
    "mean_reversion": frozenset({
        "zscore_48", "bb_upper_24_2", "sma_20", "sma_50", "close",
    }),
    "volatility_regime": frozenset({
        "atr_14", "realized_vol_24h", "bb_upper_24_2",
    }),
    "volume_divergence": frozenset({"volume_zscore_24h"}),
    "calendar_effect": frozenset({"day_of_week", "hour_of_day"}),
}

DEFAULT_MOMENTUM_FACTORS: FrozenSet[str] = frozenset({
    "rsi_14", "return_1h", "return_24h", "macd_hist",
})

THEME_ANCHOR_FACTORS: dict[str, FrozenSet[str]] = {
    "volume_divergence": frozenset({"volume_zscore_24h"}),
    "calendar_effect": frozenset({"day_of_week", "hour_of_day"}),
    "volatility_regime": frozenset({"realized_vol_24h", "atr_14"}),
    "momentum": frozenset(),
    "mean_reversion": frozenset(),
}


@dataclass(frozen=True)
class BatchContext:
    """Immutable per-call context for D7 critic scoring.

    ``prior_factor_sets`` is a tuple of sorted-factor tuples from
    ``pending_backtest`` calls earlier in the batch, excluding empty
    factor sets. ``batch_position`` is 1-indexed.
    """

    prior_factor_sets: tuple[tuple[str, ...], ...]
    prior_hashes: tuple[str, ...]
    batch_position: int
    theme_hints: dict[str, FrozenSet[str]]
    default_momentum_factors: FrozenSet[str]
    theme_anchor_factors: dict[str, FrozenSet[str]]


def build_batch_context(
    *,
    prior_factor_sets: tuple[tuple[str, ...], ...],
    prior_hashes: tuple[str, ...],
    batch_position: int,
) -> BatchContext:
    """Construct a BatchContext with canonical snapshots."""
    return BatchContext(
        prior_factor_sets=prior_factor_sets,
        prior_hashes=prior_hashes,
        batch_position=batch_position,
        theme_hints=THEME_HINTS,
        default_momentum_factors=DEFAULT_MOMENTUM_FACTORS,
        theme_anchor_factors=THEME_ANCHOR_FACTORS,
    )


__all__ = [
    "BatchContext",
    "DEFAULT_MOMENTUM_FACTORS",
    "THEME_ANCHOR_FACTORS",
    "THEME_HINTS",
    "build_batch_context",
]
