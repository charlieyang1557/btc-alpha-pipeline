"""Canonical theme list for Proposer rotation (Phase 2B).

CONTRACT BOUNDARY: this is the single source of truth for the theme
list. Both ``agents.proposer.prompt_builder`` and the orchestrator's
future theme-rotation logic MUST import from here. The list must not
be duplicated in any other module; if a second copy is introduced the
rotation strategy can silently diverge from the prompt text.

D6 accepts ``theme_slot`` on :class:`~agents.proposer.interface.BatchContext`
and indexes this list; it does NOT decide rotation strategy. The
orchestrator owns theme assignment (``theme = THEMES[(k - 1) % len(THEMES)]``
per CLAUDE.md).
"""

from __future__ import annotations

# Note: Stage 2c/2d operational rotation currently uses the first 5
# themes only (THEME_CYCLE_LEN = 5 in stage2c_batch.py and
# stage2d_batch.py). multi_factor_combination remains canonical but is
# not in current operational rotation pending separate validation.
# See CLAUDE.md "Theme rotation operational boundary" for rationale.
THEMES: tuple[str, ...] = (
    "momentum",
    "mean_reversion",
    "volatility_regime",
    "volume_divergence",
    "calendar_effect",
    "multi_factor_combination",
)

__all__ = ["THEMES"]
