"""D6 Stage 2a — live Sonnet Proposer backend.

Calls the Anthropic API via the ``anthropic`` SDK to generate hypothesis
DSL. Reuses the exact same :func:`~agents.proposer.stub_backend.classify_raw_json`
pipeline the stub uses, so model output is parsed identically.

Two-tier failure handling:
    - **Infrastructure failures** (429 Rate Limit, 529 Overloaded,
      connection timeout, network error): exponential backoff with up to
      ``max_retries`` attempts. The pre-charge ledger row stays ``pending``
      across retries.
    - **Model failures** (invalid JSON, refusal, empty 200 response body):
      immediate terminal routing via ``classify_raw_json`` → no retry.
      Counts as 1 ``hypotheses_attempted``.

Raw payload logging:
    Every API call (including retries) writes the full prompt and response
    to ``raw_payloads/batch_{batch_id}/`` for forensic replay.

Token-based cost reconciliation:
    Extracts ``usage.input_tokens`` and ``usage.output_tokens`` from each
    successful response and computes ``actual_cost`` at the current
    claude-sonnet-4-5 pricing tier.

CONTRACT BOUNDARY: this module is the ONLY file in the codebase that
imports ``anthropic``. The orchestrator and ingest modules depend on the
:class:`~agents.proposer.interface.ProposerBackend` Protocol only. The
``agents/orchestrator/`` package MUST NOT import this module or
``anthropic`` — enforced by the mechanical grep test in
``tests/test_orchestrator_ingest.py``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import anthropic

from agents.proposer.interface import (
    BatchContext,
    DSLCandidate,
    ProposerOutput,
)
from agents.proposer.prompt_builder import (
    ProposerPrompt,
    build_prompt,
)
from agents.proposer.stub_backend import classify_raw_json
from factors.registry import FactorRegistry, get_registry


# ---------------------------------------------------------------------------
# Sonnet pricing (claude-sonnet-4-5, as of 2025-06)
# ---------------------------------------------------------------------------

SONNET_MODEL = "claude-sonnet-4-5"
SONNET_INPUT_PRICE_PER_MTOK: float = 3.0
SONNET_OUTPUT_PRICE_PER_MTOK: float = 15.0


def compute_cost_usd(input_tokens: int, output_tokens: int) -> float:
    """Compute actual cost from token counts at Sonnet pricing."""
    return (
        input_tokens * SONNET_INPUT_PRICE_PER_MTOK / 1_000_000
        + output_tokens * SONNET_OUTPUT_PRICE_PER_MTOK / 1_000_000
    )


def estimate_cost_usd(
    *,
    estimated_input_tokens: int = 4000,
    max_output_tokens: int = 2000,
) -> float:
    """Upper-bound cost estimate for pre-charge ledger."""
    return compute_cost_usd(estimated_input_tokens, max_output_tokens)


# ---------------------------------------------------------------------------
# API exception classifier
# ---------------------------------------------------------------------------

_INFRASTRUCTURE_STATUS_CODES = frozenset({429, 529})


def classify_api_exception(
    exc: Exception,
) -> Literal["infrastructure", "model"]:
    """Classify an Anthropic API exception into a retry category.

    ``"infrastructure"`` → transient; caller should retry with backoff.
    ``"model"`` → permanent for this attempt; caller should not retry.
    """
    if isinstance(exc, anthropic.RateLimitError):
        return "infrastructure"
    if isinstance(exc, anthropic.InternalServerError):
        return "infrastructure"
    if isinstance(exc, (anthropic.APIConnectionError, anthropic.APITimeoutError)):
        return "infrastructure"
    if isinstance(exc, anthropic.APIStatusError):
        if exc.status_code in _INFRASTRUCTURE_STATUS_CODES:
            return "infrastructure"
    return "model"


# ---------------------------------------------------------------------------
# Raw payload logger
# ---------------------------------------------------------------------------


def _payload_dir(base_dir: Path, batch_id: str) -> Path:
    d = base_dir / f"batch_{batch_id}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_prompt_payload(
    base_dir: Path, batch_id: str, attempt_k: int, prompt_text: str
) -> Path:
    d = _payload_dir(base_dir, batch_id)
    path = d / f"attempt_{attempt_k:04d}_prompt.txt"
    path.write_text(prompt_text, encoding="utf-8")
    return path


def _write_response_payload(
    base_dir: Path,
    batch_id: str,
    attempt_k: int,
    response_text: str,
    *,
    retry: int | None = None,
) -> Path:
    d = _payload_dir(base_dir, batch_id)
    if retry is not None:
        path = d / f"attempt_{attempt_k:04d}_retry_{retry}_response.txt"
    else:
        path = d / f"attempt_{attempt_k:04d}_response.txt"
    path.write_text(response_text, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Sonnet backend
# ---------------------------------------------------------------------------


@dataclass
class SonnetProposerBackend:
    """Live Sonnet Proposer backend for D6 Stage 2+.

    Implements :class:`~agents.proposer.interface.ProposerBackend`.

    Args:
        registry: Factor registry for DSL validation. Defaults to the
            global registry.
        model: Anthropic model identifier.
        max_output_tokens: Hard cap on output tokens per call.
        max_retries: Number of retry attempts for infrastructure failures
            before giving up and returning an empty output.
        backoff_base_seconds: Base delay for exponential backoff
            (delay = base * 2^retry).
        raw_payload_dir: Root directory for raw payload logging.
            Set to None to disable logging.
        approved_examples: DSL-only example strings for the prompt
            (no metrics, per Stage 1 leakage contract).
        dedup_rate_so_far: Aggregate signal for the prompt.
        critic_rejection_count_last_50: Aggregate signal for the prompt.
        top_factors: Aggregate signal for the prompt.
    """

    registry: FactorRegistry | None = None
    model: str = SONNET_MODEL
    max_output_tokens: int = 2000
    max_retries: int = 3
    backoff_base_seconds: float = 1.0
    raw_payload_dir: Path | None = field(default_factory=lambda: Path("raw_payloads"))
    approved_examples: tuple[str, ...] = ()
    dedup_rate_so_far: float | None = None
    critic_rejection_count_last_50: int | None = None
    top_factors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self._client: anthropic.Anthropic | None = None

    def _get_client(self) -> anthropic.Anthropic:
        if self._client is None:
            self._client = anthropic.Anthropic()
        return self._client

    def _build_prompt(self, context: BatchContext) -> ProposerPrompt:
        return build_prompt(
            context,
            registry=self.registry,
            approved_examples=self.approved_examples,
            dedup_rate_so_far=self.dedup_rate_so_far,
            critic_rejection_count_last_50=self.critic_rejection_count_last_50,
            top_factors=self.top_factors,
        )

    def generate(self, context: BatchContext) -> ProposerOutput:
        """Call Sonnet and classify the response.

        Infrastructure failures (429, 529, timeout, network) are retried
        with exponential backoff up to ``max_retries`` times. After all
        retries are exhausted, returns a ``ProposerOutput`` with empty
        ``candidates`` tuple (which the ingest layer will route to
        ``backend_empty_output``).

        Model failures (bad JSON, refusal, schema violation) are routed
        through ``classify_raw_json`` immediately — no retry.
        """
        reg = self.registry or get_registry()
        prompt = self._build_prompt(context)
        prompt_text = prompt.all_text()

        if self.raw_payload_dir is not None:
            _write_prompt_payload(
                self.raw_payload_dir, context.batch_id,
                context.position, prompt_text,
            )

        messages = [{"role": "user", "content": prompt.user}]

        system_with_menu = prompt.system + "\n\n" + prompt.factor_menu

        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            retry_index = attempt if attempt > 0 else None
            try:
                response = self._get_client().messages.create(
                    model=self.model,
                    max_tokens=self.max_output_tokens,
                    system=system_with_menu,
                    messages=messages,
                )
            except Exception as exc:
                last_exc = exc
                category = classify_api_exception(exc)
                error_text = f"[{category}] {type(exc).__name__}: {exc}"

                if self.raw_payload_dir is not None:
                    _write_response_payload(
                        self.raw_payload_dir, context.batch_id,
                        context.position, error_text,
                        retry=retry_index,
                    )

                if category == "model":
                    return ProposerOutput(
                        candidates=(),
                        cost_estimate_usd=0.0,
                        cost_actual_usd=0.0,
                        backend_name="sonnet",
                        telemetry={
                            "error": error_text,
                            "error_category": "model",
                            "position": context.position,
                            "batch_id": context.batch_id,
                        },
                    )

                if attempt < self.max_retries:
                    delay = self.backoff_base_seconds * (2 ** attempt)
                    time.sleep(delay)
                    continue

                return ProposerOutput(
                    candidates=(),
                    cost_estimate_usd=0.0,
                    cost_actual_usd=0.0,
                    backend_name="sonnet",
                    telemetry={
                        "error": error_text,
                        "error_category": "infrastructure",
                        "retries_exhausted": True,
                        "position": context.position,
                        "batch_id": context.batch_id,
                    },
                )

            raw_text = response.content[0].text if response.content else ""

            if self.raw_payload_dir is not None:
                _write_response_payload(
                    self.raw_payload_dir, context.batch_id,
                    context.position, raw_text,
                    retry=retry_index,
                )

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            actual_cost = compute_cost_usd(input_tokens, output_tokens)
            estimated_cost = estimate_cost_usd(
                estimated_input_tokens=input_tokens,
                max_output_tokens=self.max_output_tokens,
            )

            provenance = {
                "backend": "sonnet",
                "model": self.model,
                "position": context.position,
                "batch_id": context.batch_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "actual_cost_usd": actual_cost,
                "stop_reason": response.stop_reason,
            }

            if not raw_text.strip():
                return ProposerOutput(
                    candidates=(),
                    cost_estimate_usd=estimated_cost,
                    cost_actual_usd=actual_cost,
                    backend_name="sonnet",
                    telemetry={
                        **provenance,
                        "error": "empty_response_body",
                        "error_category": "model",
                    },
                )

            candidate = classify_raw_json(
                raw_text,
                registry=reg,
                error_kind_hint="sonnet_response",
                provenance=provenance,
            )

            return ProposerOutput(
                candidates=(candidate,),
                cost_estimate_usd=estimated_cost,
                cost_actual_usd=actual_cost,
                backend_name="sonnet",
                telemetry=provenance,
            )

        return ProposerOutput(
            candidates=(),
            cost_estimate_usd=0.0,
            cost_actual_usd=0.0,
            backend_name="sonnet",
            telemetry={"error": f"unexpected: {last_exc}"},
        )


__all__ = [
    "SONNET_INPUT_PRICE_PER_MTOK",
    "SONNET_MODEL",
    "SONNET_OUTPUT_PRICE_PER_MTOK",
    "SonnetProposerBackend",
    "classify_api_exception",
    "compute_cost_usd",
    "estimate_cost_usd",
]
