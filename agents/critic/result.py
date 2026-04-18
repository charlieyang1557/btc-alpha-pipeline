"""D7 CriticResult — frozen multi-dimensional score breakdown.

Schema is frozen at D7 Stage 1 sign-off. Adding fields is allowed;
renaming or removing fields breaks D8 policy compatibility and requires
migration.

Key semantics:
    - ``critic_status`` and ``d7b_mode`` are orthogonal.
    - ``None`` score dict means "unknown" (error). ``{k: 0.0}`` means
      "measured as bad". D8 policy must handle ``None`` explicitly.
    - ``d7a_rule_flags`` is always a list (never ``None``).
    - ``structural_variant_risk`` is the ONLY reverse-polarity axis:
      0.0 = low risk (structurally distinct), 1.0 = high risk (shallow
      variant). Every other score axis is 0.0 = bad, 1.0 = good. D8
      policy authors must respect this when aggregating or filtering.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class CriticResult:
    """Multi-dimensional critic output for one hypothesis.

    ``structural_variant_risk`` is the only reverse-polarity score axis
    in the entire CriticResult schema: 0.0 = low risk, 1.0 = high risk.
    All other score axes are 0.0 = bad, 1.0 = good.
    """

    # Versioning
    critic_version: str

    # Status (per-call health) — orthogonal to d7b_mode
    critic_status: Literal["ok", "d7a_error", "d7b_error", "both_error"]

    # Mode (batch-level D7b configuration) — orthogonal to critic_status
    d7b_mode: Literal["stub", "live"]

    # D7a (rule-based) outputs
    d7a_rule_scores: dict[str, float] | None
    d7a_supporting_measures: dict[str, int | None]
    d7a_rule_flags: list[str]

    # D7b (LLM-based) outputs
    d7b_llm_scores: dict[str, float] | None
    d7b_reasoning: str | None
    d7b_raw_response_path: str | None
    d7b_cost_actual_usd: float | None
    d7b_input_tokens: int | None
    d7b_output_tokens: int | None
    d7b_retry_count: int

    # Timing
    critic_timing_ms: dict[str, float] = field(
        default_factory=lambda: {"d7a_ms": 0.0, "d7b_ms": 0.0}
    )

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict."""
        return {
            "critic_version": self.critic_version,
            "critic_status": self.critic_status,
            "d7b_mode": self.d7b_mode,
            "d7a_rule_scores": self.d7a_rule_scores,
            "d7a_supporting_measures": self.d7a_supporting_measures,
            "d7a_rule_flags": list(self.d7a_rule_flags),
            "d7b_llm_scores": self.d7b_llm_scores,
            "d7b_reasoning": self.d7b_reasoning,
            "d7b_raw_response_path": self.d7b_raw_response_path,
            "d7b_cost_actual_usd": self.d7b_cost_actual_usd,
            "d7b_input_tokens": self.d7b_input_tokens,
            "d7b_output_tokens": self.d7b_output_tokens,
            "d7b_retry_count": self.d7b_retry_count,
            "critic_timing_ms": dict(self.critic_timing_ms),
        }

    @classmethod
    def from_dict(cls, d: dict) -> CriticResult:
        """Deserialize from a JSON-compatible dict."""
        return cls(
            critic_version=d["critic_version"],
            critic_status=d["critic_status"],
            d7b_mode=d["d7b_mode"],
            d7a_rule_scores=d["d7a_rule_scores"],
            d7a_supporting_measures=d["d7a_supporting_measures"],
            d7a_rule_flags=list(d["d7a_rule_flags"]),
            d7b_llm_scores=d["d7b_llm_scores"],
            d7b_reasoning=d["d7b_reasoning"],
            d7b_raw_response_path=d["d7b_raw_response_path"],
            d7b_cost_actual_usd=d["d7b_cost_actual_usd"],
            d7b_input_tokens=d["d7b_input_tokens"],
            d7b_output_tokens=d["d7b_output_tokens"],
            d7b_retry_count=d["d7b_retry_count"],
            critic_timing_ms=dict(d.get("critic_timing_ms", {})),
        )


__all__ = ["CriticResult"]
