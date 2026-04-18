"""D7b live Sonnet backend (D7 Stage 2a).

Single-call forensic probe implementation. Calls Anthropic's Sonnet via
the ``anthropic`` SDK and returns structured scores, reasoning, and
forensic metadata. Fail-open: any content-level error raises, and the
orchestrator converts the raise to ``critic_status='d7b_error'``.

CONTRACT BOUNDARY: Prompt caching is disabled for all D7b Stage 2 calls.
Do not enable without a new locked decision.

CONTRACT BOUNDARY: This module instantiates its OWN
``anthropic.Anthropic()`` client — independent of the D6 Proposer's
client. Cost accounting, rate-limit state, and per-client configuration
stay orthogonal across the two subsystems.

Retry discipline (LOCKED):
    - API-level errors only (connection, timeout, rate limit, 5xx):
      one retry with exponential backoff (base 1s, max 4s).
    - Content-level errors (malformed JSON, schema violation, refusal):
      ZERO retries. These are forensic signals we want to preserve.
"""

from __future__ import annotations

import json
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import anthropic

from agents.critic.batch_context import BatchContext
from agents.critic.d7b_backend import D7bBackend
from agents.critic.d7b_parser import D7bContentError, parse_d7b_response
from agents.critic.d7b_prompt import build_d7b_prompt, run_leakage_audit
from strategies.dsl import StrategyDSL


# ---------------------------------------------------------------------------
# Sonnet pricing (matches D6 proposer; must remain in sync)
# ---------------------------------------------------------------------------

SONNET_MODEL = "claude-sonnet-4-5"
SONNET_INPUT_PRICE_PER_MTOK: float = 3.0
SONNET_OUTPUT_PRICE_PER_MTOK: float = 15.0

# Single-call cost ceiling for Stage 2a (LOCKED).
D7B_STAGE2A_COST_CEILING_USD: float = 0.05


def compute_cost_usd(input_tokens: int, output_tokens: int) -> float:
    """Compute actual USD cost from token counts at Sonnet pricing."""
    return (
        input_tokens * SONNET_INPUT_PRICE_PER_MTOK / 1_000_000
        + output_tokens * SONNET_OUTPUT_PRICE_PER_MTOK / 1_000_000
    )


# ---------------------------------------------------------------------------
# Exceptions surfaced to the orchestrator
# ---------------------------------------------------------------------------


class D7bLiveError(Exception):
    """Base class for all D7b live errors that should yield critic_status=d7b_error."""

    error_code: str = "unknown"

    def __init__(self, error_code: str, detail: str):
        super().__init__(f"{error_code}: {detail}")
        self.error_code = error_code
        self.detail = detail

    def sanitized_signature(self) -> str:
        """Format: ``<error_code>: <detail>`` truncated to 200 chars."""
        msg = f"{self.error_code}: {self.detail}"
        if len(msg) > 200:
            msg = msg[:197] + "..."
        return msg


class D7bLiveAPIError(D7bLiveError):
    """API-level failure after retry exhaustion."""


class D7bLiveContentError(D7bLiveError):
    """Content-level failure (parse, schema, forbidden language, refusal)."""


class D7bLiveLeakageAuditError(D7bLiveError):
    """Leakage audit failed BEFORE send — never reaches the API."""

    def __init__(self, detail: str):
        super().__init__("leakage_audit_fail", detail)


class D7bLiveCostCeilingError(D7bLiveError):
    """Measured cost exceeded the single-call ceiling."""

    def __init__(self, measured_cost: float, ceiling: float):
        super().__init__(
            "cost_ceiling_exceeded",
            f"measured ${measured_cost:.6f} > ceiling ${ceiling:.6f}",
        )


# API exceptions we retry exactly once.
API_LEVEL_EXCEPTIONS = (
    anthropic.APIConnectionError,
    anthropic.APITimeoutError,
    anthropic.RateLimitError,
    anthropic.InternalServerError,
)


def _classify_api_exception(exc: Exception) -> str:
    """Map an anthropic exception to a Stage 2a error_code."""
    if isinstance(exc, anthropic.APITimeoutError):
        return "api_timeout"
    if isinstance(exc, anthropic.RateLimitError):
        return "api_rate_limit"
    if isinstance(exc, anthropic.APIConnectionError):
        return "api_connection"
    if isinstance(exc, anthropic.InternalServerError):
        return "api_server_error"
    return "api_connection"  # default for unknown transport errors


# ---------------------------------------------------------------------------
# LiveSonnetD7bBackend
# ---------------------------------------------------------------------------


@dataclass
class LiveSonnetD7bBackend(D7bBackend):
    """Live Sonnet D7b critic backend.

    Instantiates its own anthropic.Anthropic() client — independent of
    the D6 Proposer client. Keeps cost accounting, rate-limit state,
    and per-client configuration orthogonal across subsystems.

    CONTRACT BOUNDARY: Prompt caching is disabled for all D7b Stage 2
    calls. Do not enable without a new locked decision.

    Args:
        raw_payload_dir: Root directory for raw payload logging. The
            critic subdirectory ``critic/`` is created underneath.
        api_call_number: Zero-padded call index used in artifact file
            names (``call_<NNNN>_prompt.txt``). For Stage 2a single-call
            probes this equals the replay candidate's original Stage 2d
            position.
        temperature: Explicit parameter, not inherited from D6. Default 1.0.
        max_tokens: Output cap per call. Default 500.
        cost_ceiling_usd: Single-call cost ceiling. Default $0.05.
        retry_base_seconds: Base delay for the one API-level retry.
        _client: Injectable for tests. Production instantiates a fresh
            ``anthropic.Anthropic()`` on first use.
    """

    MODEL: str = SONNET_MODEL
    MAX_TOKENS: int = 500
    TEMPERATURE: float = 1.0

    raw_payload_dir: Path = field(default_factory=lambda: Path("raw_payloads"))
    api_call_number: int = 1
    temperature: float = 1.0
    max_tokens: int = 500
    cost_ceiling_usd: float = D7B_STAGE2A_COST_CEILING_USD
    retry_base_seconds: float = 1.0
    batch_id: str | None = None
    _client: anthropic.Anthropic | None = None

    @property
    def mode(self) -> Literal["stub", "live"]:
        return "live"

    def _get_client(self) -> anthropic.Anthropic:
        if self._client is None:
            self._client = anthropic.Anthropic()
        return self._client

    def _critic_dir(self) -> Path:
        if self.batch_id is None:
            d = self.raw_payload_dir / "critic"
        else:
            d = self.raw_payload_dir / f"batch_{self.batch_id}" / "critic"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _prompt_path(self) -> Path:
        return self._critic_dir() / f"call_{self.api_call_number:04d}_prompt.txt"

    def _response_path(self) -> Path:
        return self._critic_dir() / f"call_{self.api_call_number:04d}_response.json"

    def _traceback_path(self) -> Path:
        return self._critic_dir() / f"call_{self.api_call_number:04d}_traceback.txt"

    def _write_traceback(self, error: Exception, raw_bytes: bytes | str | None) -> Path:
        path = self._traceback_path()
        tb = traceback.format_exc()
        parts = [
            f"error_type: {type(error).__name__}",
            f"error_message: {error}",
            "",
            "traceback:",
            tb,
        ]
        if raw_bytes is not None:
            if isinstance(raw_bytes, bytes):
                try:
                    raw_text = raw_bytes.decode("utf-8", errors="replace")
                except Exception:  # pragma: no cover - defensive
                    raw_text = repr(raw_bytes)
            else:
                raw_text = raw_bytes
            parts.extend(["", "raw_response:", raw_text])
        path.write_text("\n".join(parts), encoding="utf-8")
        return path

    def _api_call(self, prompt_text: str) -> tuple[str, object, int]:
        """Call Sonnet with one API-level retry.

        Returns ``(raw_text, usage, retry_count)``. Raises ``D7bLiveAPIError``
        on exhaustion.
        """
        last_exc: Exception | None = None
        for attempt in range(2):  # attempt 0 = first, attempt 1 = retry
            try:
                response = self._get_client().messages.create(
                    model=self.MODEL,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt_text}],
                )
                raw_text = response.content[0].text if response.content else ""
                return raw_text, response.usage, attempt
            except API_LEVEL_EXCEPTIONS as exc:
                last_exc = exc
                if attempt == 0:
                    delay = min(self.retry_base_seconds * 2, 4.0)
                    time.sleep(delay)
                    continue
                code = _classify_api_exception(exc)
                raise D7bLiveAPIError(
                    code,
                    f"{type(exc).__name__}: {str(exc)[:160]}",
                ) from exc
        # Unreachable — loop always returns or raises.
        raise D7bLiveAPIError(  # pragma: no cover
            "api_connection", f"unexpected exit: {last_exc!r}"
        )

    def score(
        self,
        dsl: StrategyDSL,
        theme: str,
        batch_context: BatchContext,
    ) -> tuple[dict[str, float], str, dict]:
        """Build prompt → send to Sonnet → parse response.

        Raises on any content-level error. The orchestrator's fail-open
        policy converts raises to ``critic_status = 'd7b_error'``.

        On content-level errors that occur AFTER a successful API call
        (e.g. schema_reasoning_length), cost and token fields are still
        captured on ``self._last_api_metadata`` so the orchestrator can
        recover them for ledger finalization.
        """
        self._last_api_metadata: dict | None = None

        prompt_text = build_d7b_prompt(dsl, theme, batch_context)

        # Leakage audit BEFORE writing the prompt file or calling the API.
        audit = run_leakage_audit(prompt_text)
        if audit is not None:
            raise D7bLiveLeakageAuditError(audit)

        # Write prompt BEFORE calling API (forensic preservation on crash).
        prompt_path = self._prompt_path()
        prompt_path.write_text(prompt_text, encoding="utf-8")

        try:
            raw_text, usage, retry_count = self._api_call(prompt_text)
        except D7bLiveAPIError as exc:
            self._write_traceback(exc, None)
            raise

        # Persist raw response BEFORE parsing (preserves malformed payloads).
        response_path = self._response_path()
        response_path.write_text(raw_text, encoding="utf-8")

        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens
        actual_cost = compute_cost_usd(input_tokens, output_tokens)

        # Capture cost/token metadata BEFORE any downstream check that
        # may raise. This lets the orchestrator recover billed-but-failed
        # calls via ``getattr(backend, '_last_api_metadata', None)``.
        self._last_api_metadata = {
            "raw_response_path": str(response_path),
            "cost_actual_usd": actual_cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "retry_count": retry_count,
        }

        if actual_cost > self.cost_ceiling_usd:
            exc = D7bLiveCostCeilingError(actual_cost, self.cost_ceiling_usd)
            self._write_traceback(exc, raw_text)
            raise exc

        try:
            scores, reasoning, scan_results = parse_d7b_response(raw_text)
        except D7bContentError as exc:
            self._write_traceback(exc, raw_text)
            raise D7bLiveContentError(exc.error_code, exc.detail) from exc

        metadata = dict(self._last_api_metadata)
        metadata["scan_results"] = scan_results
        return scores, reasoning, metadata


__all__ = [
    "API_LEVEL_EXCEPTIONS",
    "D7B_STAGE2A_COST_CEILING_USD",
    "D7bLiveAPIError",
    "D7bLiveContentError",
    "D7bLiveCostCeilingError",
    "D7bLiveError",
    "D7bLiveLeakageAuditError",
    "LiveSonnetD7bBackend",
    "SONNET_INPUT_PRICE_PER_MTOK",
    "SONNET_MODEL",
    "SONNET_OUTPUT_PRICE_PER_MTOK",
    "compute_cost_usd",
]
