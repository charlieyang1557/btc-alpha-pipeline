"""D7 Critic module — rule-based gate (D7a) + LLM critic (D7b).

Public API:
    - ``CriticResult`` — frozen multi-dimensional score breakdown.
    - ``run_critic()`` — orchestrator entry point (never raises).
    - ``BatchContext`` — immutable per-call context.
    - ``build_batch_context()`` — convenience constructor.
"""

from agents.critic.batch_context import BatchContext, build_batch_context
from agents.critic.orchestrator import run_critic
from agents.critic.result import CriticResult

__all__ = [
    "BatchContext",
    "CriticResult",
    "build_batch_context",
    "run_critic",
]
