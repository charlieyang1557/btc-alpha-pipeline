"""D7b abstract backend interface.

D7b score dimensions (FROZEN):
    - ``semantic_plausibility``: 0.0 = low, 1.0 = high
    - ``semantic_theme_alignment``: 0.0 = low, 1.0 = high
    - ``structural_variant_risk``: 0.0 = LOW risk (distinct), 1.0 = HIGH
      risk (shallow variant). REVERSE POLARITY relative to all other axes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from agents.critic.batch_context import BatchContext
from strategies.dsl import StrategyDSL

D7B_SCORE_KEYS = (
    "semantic_plausibility",
    "semantic_theme_alignment",
    "structural_variant_risk",
)


class D7bBackend(ABC):
    """Abstract D7b critic backend.

    ``structural_variant_risk`` is the only reverse-polarity axis: 0.0 =
    low risk (structurally distinct), 1.0 = high risk (shallow variant).
    """

    @property
    @abstractmethod
    def mode(self) -> Literal["stub", "live"]:
        ...

    @abstractmethod
    def score(
        self,
        dsl: StrategyDSL,
        theme: str,
        batch_context: BatchContext,
    ) -> tuple[dict[str, float], str, dict]:
        """Score one hypothesis.

        Returns:
            (scores, reasoning, metadata)
            scores: dict with keys exactly D7B_SCORE_KEYS
            reasoning: human-readable string
            metadata: dict with keys {
                "raw_response_path", "cost_actual_usd",
                "input_tokens", "output_tokens", "retry_count",
                "scan_results",
            }
        """
        ...


__all__ = ["D7B_SCORE_KEYS", "D7bBackend"]
