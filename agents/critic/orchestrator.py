"""D7 orchestrator — ``run_critic()`` entry point.

Critical property: ``run_critic`` NEVER raises. Every failure becomes a
status code. This makes fail-open enforceable at the API level, not just
at the policy level.

The caller is responsible for persisting CriticResult alongside the
candidate. ``run_critic`` does no ledger writes, no disk writes, no
network access.
"""

from __future__ import annotations

import time
from typing import Literal

from agents.critic.batch_context import BatchContext
from agents.critic.d7a_rules import score_d7a
from agents.critic.d7b_backend import D7bBackend
from agents.critic.result import CriticResult
from strategies.dsl import StrategyDSL

CRITIC_VERSION = "d7_v1"

# -----------------------------------------------------------------------
# Reliability fuse configuration (scaffolded in Stage 1, enforced in Stage 2)
# -----------------------------------------------------------------------

CRITIC_RELIABILITY_TIER1_MIN_K = 20
CRITIC_RELIABILITY_TIER1_FAILURE_RATE = 0.50
CRITIC_RELIABILITY_TIER2_MIN_K = 50
CRITIC_RELIABILITY_TIER2_FAILURE_RATE = 0.20
CRITIC_RELIABILITY_FUSE_ENFORCED = False


def compute_reliability_stats(
    critic_ok_count: int,
    critic_d7a_error_count: int,
    critic_d7b_error_count: int,
    critic_both_error_count: int,
) -> dict:
    """Compute reliability rates from raw counts.

    Returns a dict suitable for inclusion in batch summary under
    ``critic_reliability``.
    """
    total = (
        critic_ok_count
        + critic_d7a_error_count
        + critic_d7b_error_count
        + critic_both_error_count
    )
    failure_count = critic_d7a_error_count + critic_d7b_error_count + critic_both_error_count
    failure_rate = failure_count / total if total > 0 else 0.0
    return {
        "critic_total_count": total,
        "critic_ok_count": critic_ok_count,
        "critic_d7a_error_count": critic_d7a_error_count,
        "critic_d7b_error_count": critic_d7b_error_count,
        "critic_both_error_count": critic_both_error_count,
        "critic_failure_count": failure_count,
        "critic_failure_rate": round(failure_rate, 4),
        "fuse_enforced": CRITIC_RELIABILITY_FUSE_ENFORCED,
        "tier1_min_k": CRITIC_RELIABILITY_TIER1_MIN_K,
        "tier1_failure_rate_threshold": CRITIC_RELIABILITY_TIER1_FAILURE_RATE,
        "tier2_min_k": CRITIC_RELIABILITY_TIER2_MIN_K,
        "tier2_failure_rate_threshold": CRITIC_RELIABILITY_TIER2_FAILURE_RATE,
    }


def should_fuse_halt(
    total_count: int,
    failure_rate: float,
) -> bool:
    """Check whether the reliability fuse should halt the batch.

    Returns False unconditionally in Stage 1 (fuse not enforced).
    """
    if not CRITIC_RELIABILITY_FUSE_ENFORCED:
        return False
    if (total_count >= CRITIC_RELIABILITY_TIER1_MIN_K
            and failure_rate >= CRITIC_RELIABILITY_TIER1_FAILURE_RATE):
        return True
    if (total_count >= CRITIC_RELIABILITY_TIER2_MIN_K
            and failure_rate >= CRITIC_RELIABILITY_TIER2_FAILURE_RATE):
        return True
    return False


# -----------------------------------------------------------------------
# run_critic — the single entry point
# -----------------------------------------------------------------------


def run_critic(
    dsl: StrategyDSL,
    theme: str,
    batch_context: BatchContext,
    d7b_backend: D7bBackend,
) -> CriticResult:
    """Score one hypothesis through D7a rules + D7b backend.

    Never raises. Every failure becomes a status code in CriticResult.

    Orchestration contract:
        1. Run all D7a rules. If ANY rule raises, all D7a output is None
           and critic_status ∈ {d7a_error, both_error}.
        2. Call d7b_backend.score(). If backend raises, all D7b output is
           None and critic_status ∈ {d7b_error, both_error}.
        3. Record timing: d7a_ms and d7b_ms separately.
        4. Assemble CriticResult with d7b_mode = d7b_backend.mode.
        5. Return. Never raise.
    """
    d7a_scores = None
    d7a_measures: dict[str, int | None] = {}
    d7a_flags: list[str] = []
    d7a_error = False
    d7b_scores = None
    d7b_reasoning = None
    d7b_metadata: dict = {
        "raw_response_path": None,
        "cost_actual_usd": None,
        "input_tokens": None,
        "output_tokens": None,
        "retry_count": 0,
    }
    d7b_error = False

    # --- D7a ---
    t0 = time.monotonic()
    try:
        d7a_scores, d7a_measures, d7a_flags = score_d7a(
            dsl, theme, batch_context,
        )
    except Exception:
        d7a_error = True
    d7a_ms = round((time.monotonic() - t0) * 1000, 3)

    # --- D7b ---
    t1 = time.monotonic()
    try:
        d7b_scores, d7b_reasoning, d7b_metadata = d7b_backend.score(
            dsl, theme, batch_context,
        )
    except Exception:
        d7b_error = True
    d7b_ms = round((time.monotonic() - t1) * 1000, 3)

    # --- Status ---
    status: Literal["ok", "d7a_error", "d7b_error", "both_error"]
    if d7a_error and d7b_error:
        status = "both_error"
    elif d7a_error:
        status = "d7a_error"
    elif d7b_error:
        status = "d7b_error"
    else:
        status = "ok"

    return CriticResult(
        critic_version=CRITIC_VERSION,
        critic_status=status,
        d7b_mode=d7b_backend.mode,
        d7a_rule_scores=d7a_scores if not d7a_error else None,
        d7a_supporting_measures=d7a_measures if not d7a_error else {},
        d7a_rule_flags=d7a_flags if not d7a_error else [],
        d7b_llm_scores=d7b_scores,
        d7b_reasoning=d7b_reasoning,
        d7b_raw_response_path=d7b_metadata.get("raw_response_path"),
        d7b_cost_actual_usd=d7b_metadata.get("cost_actual_usd"),
        d7b_input_tokens=d7b_metadata.get("input_tokens"),
        d7b_output_tokens=d7b_metadata.get("output_tokens"),
        d7b_retry_count=d7b_metadata.get("retry_count", 0),
        critic_timing_ms={"d7a_ms": d7a_ms, "d7b_ms": d7b_ms},
    )


__all__ = [
    "CRITIC_RELIABILITY_FUSE_ENFORCED",
    "CRITIC_VERSION",
    "compute_reliability_stats",
    "run_critic",
    "should_fuse_halt",
]
