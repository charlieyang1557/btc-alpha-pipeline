"""Tests for agents/critic/d7b_live.py — LiveSonnetD7bBackend (D7 Stage 2a).

Covers:
    - compute_cost_usd() math
    - LiveSonnetD7bBackend.mode property
    - Successful API call with mocked response
    - API-level retries (timeout, rate-limit, connection)
    - Content-level errors (bad JSON, zero retries)
    - Leakage audit failure before API call
    - Cost ceiling breach
    - Artifact file writing (prompt, response, traceback)
    - sanitized_signature() truncation
    - _classify_api_exception() mapping
    - Retry count on first success vs after retry

NOTE: Tests that exercise ``LiveSonnetD7bBackend.score()`` must patch
``run_leakage_audit`` to return ``None`` because the real prompt template
contains excluded substrings (e.g. "position" inside "position_sizing")
that correctly trigger the leakage audit. In production, the audit is
the first safety gate; here we are testing the layers beneath it.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from agents.critic.batch_context import (
    DEFAULT_MOMENTUM_FACTORS,
    THEME_ANCHOR_FACTORS,
    THEME_HINTS,
    BatchContext,
)
from agents.critic.d7b_live import (
    D7B_STAGE2A_COST_CEILING_USD,
    D7bLiveAPIError,
    D7bLiveContentError,
    D7bLiveCostCeilingError,
    D7bLiveError,
    D7bLiveLeakageAuditError,
    LiveSonnetD7bBackend,
    SONNET_INPUT_PRICE_PER_MTOK,
    SONNET_OUTPUT_PRICE_PER_MTOK,
    _classify_api_exception,
    compute_cost_usd,
)
from strategies.dsl import StrategyDSL

import anthropic


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_dsl() -> StrategyDSL:
    return StrategyDSL(
        name="test_live_backend",
        description="A momentum test strategy for live backend tests",
        entry=[
            {"conditions": [{"factor": "rsi_14", "op": ">", "value": 30.0}]},
        ],
        exit=[
            {"conditions": [{"factor": "rsi_14", "op": "<", "value": 70.0}]},
        ],
        position_sizing="full_equity",
        max_hold_bars=168,
    )


def _make_batch_context() -> BatchContext:
    return BatchContext(
        prior_factor_sets=(("atr_14", "rsi_14"),),
        prior_hashes=("abc123",),
        batch_position=5,
        theme_hints=THEME_HINTS,
        default_momentum_factors=DEFAULT_MOMENTUM_FACTORS,
        theme_anchor_factors=THEME_ANCHOR_FACTORS,
    )


# Valid D7b response text for mocking.
_VALID_REASONING = (
    "The entry logic uses RSI crossing above a threshold combined with "
    "ATR as a volatility filter. The exit uses RSI crossing below to "
    "capture reversal. Theme alignment is moderate."
)

_VALID_RESPONSE_TEXT = json.dumps({
    "semantic_plausibility": 0.7500,
    "semantic_theme_alignment": 0.6000,
    "structural_variant_risk": 0.2000,
    "reasoning": _VALID_REASONING,
})


def _make_mock_response(
    text: str = _VALID_RESPONSE_TEXT,
    input_tokens: int = 500,
    output_tokens: int = 100,
) -> MagicMock:
    """Build a mock anthropic response object."""
    content_block = SimpleNamespace(text=text)
    usage = SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
    response = MagicMock()
    response.content = [content_block]
    response.usage = usage
    return response


def _make_backend(tmp_path: Path, **overrides) -> LiveSonnetD7bBackend:
    """Build a LiveSonnetD7bBackend with a mocked client."""
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_response()
    defaults = dict(
        raw_payload_dir=tmp_path,
        api_call_number=1,
        retry_base_seconds=0.001,  # Speed up retries in tests.
        _client=mock_client,
    )
    defaults.update(overrides)
    return LiveSonnetD7bBackend(**defaults)


# Patch target for bypassing leakage audit in tests that test post-audit layers.
_PATCH_AUDIT = patch(
    "agents.critic.d7b_live.run_leakage_audit", return_value=None,
)


# ---------------------------------------------------------------------------
# compute_cost_usd tests
# ---------------------------------------------------------------------------


def test_compute_cost_usd_math():
    """Cost = input * $3/M + output * $15/M."""
    cost = compute_cost_usd(input_tokens=1_000_000, output_tokens=1_000_000)
    expected = 3.0 + 15.0
    assert cost == pytest.approx(expected)


def test_compute_cost_usd_small_tokens():
    """Small token counts produce proportionally small cost."""
    cost = compute_cost_usd(input_tokens=1000, output_tokens=200)
    expected = 1000 * 3.0 / 1_000_000 + 200 * 15.0 / 1_000_000
    assert cost == pytest.approx(expected)


def test_compute_cost_usd_zero():
    """Zero tokens produce zero cost."""
    assert compute_cost_usd(0, 0) == 0.0


# ---------------------------------------------------------------------------
# Mode property
# ---------------------------------------------------------------------------


def test_live_backend_mode(tmp_path):
    backend = _make_backend(tmp_path)
    assert backend.mode == "live"


# ---------------------------------------------------------------------------
# Successful score call
# ---------------------------------------------------------------------------


def test_score_success_returns_expected(tmp_path):
    """Mocked successful API response returns expected scores and metadata."""
    backend = _make_backend(tmp_path)
    dsl = _make_dsl()
    ctx = _make_batch_context()

    with _PATCH_AUDIT:
        scores, reasoning, metadata = backend.score(dsl, "momentum", ctx)

    assert scores["semantic_plausibility"] == pytest.approx(0.75)
    assert scores["semantic_theme_alignment"] == pytest.approx(0.60)
    assert scores["structural_variant_risk"] == pytest.approx(0.20)
    assert reasoning == _VALID_REASONING
    assert metadata["retry_count"] == 0
    assert metadata["cost_actual_usd"] > 0


# ---------------------------------------------------------------------------
# API-level errors + retry
# ---------------------------------------------------------------------------


def test_api_timeout_triggers_retry_then_raises(tmp_path):
    """APITimeoutError: retries once, then raises D7bLiveAPIError."""
    backend = _make_backend(tmp_path)
    backend._client.messages.create.side_effect = anthropic.APITimeoutError(
        request=MagicMock()
    )

    with _PATCH_AUDIT:
        with pytest.raises(D7bLiveAPIError) as exc_info:
            backend.score(_make_dsl(), "momentum", _make_batch_context())

    assert exc_info.value.error_code == "api_timeout"
    # Called twice: initial + 1 retry.
    assert backend._client.messages.create.call_count == 2


def test_rate_limit_triggers_retry_then_raises(tmp_path):
    """RateLimitError: retries once, then raises D7bLiveAPIError."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {}
    backend = _make_backend(tmp_path)
    backend._client.messages.create.side_effect = anthropic.RateLimitError(
        message="rate limited",
        response=mock_response,
        body=None,
    )

    with _PATCH_AUDIT:
        with pytest.raises(D7bLiveAPIError) as exc_info:
            backend.score(_make_dsl(), "momentum", _make_batch_context())

    assert exc_info.value.error_code == "api_rate_limit"
    assert backend._client.messages.create.call_count == 2


def test_connection_error_triggers_retry_then_raises(tmp_path):
    """APIConnectionError: retries once, then raises D7bLiveAPIError."""
    backend = _make_backend(tmp_path)
    backend._client.messages.create.side_effect = anthropic.APIConnectionError(
        request=MagicMock()
    )

    with _PATCH_AUDIT:
        with pytest.raises(D7bLiveAPIError) as exc_info:
            backend.score(_make_dsl(), "momentum", _make_batch_context())

    assert exc_info.value.error_code == "api_connection"
    assert backend._client.messages.create.call_count == 2


# ---------------------------------------------------------------------------
# Content-level errors (zero retries)
# ---------------------------------------------------------------------------


def test_content_error_bad_json_raises_zero_retries(tmp_path):
    """Bad JSON in response raises D7bLiveContentError with no retry."""
    bad_response = _make_mock_response(text="NOT JSON {{{{")
    backend = _make_backend(tmp_path)
    backend._client.messages.create.return_value = bad_response

    with _PATCH_AUDIT:
        with pytest.raises(D7bLiveContentError) as exc_info:
            backend.score(_make_dsl(), "momentum", _make_batch_context())

    assert exc_info.value.error_code == "json_decode"
    # Only one call (no retry on content error).
    assert backend._client.messages.create.call_count == 1


# ---------------------------------------------------------------------------
# Leakage audit
# ---------------------------------------------------------------------------


def test_leakage_audit_failure_raises_before_api_call(tmp_path):
    """Leakage audit failure raises D7bLiveLeakageAuditError, no API call."""
    backend = _make_backend(tmp_path)
    # Inject a UUID into the prompt to trigger leakage.
    with patch(
        "agents.critic.d7b_live.build_d7b_prompt",
        return_value="some prompt with 01234567-abcd-ef01-2345-6789abcdef01",
    ):
        with pytest.raises(D7bLiveLeakageAuditError):
            backend.score(_make_dsl(), "momentum", _make_batch_context())

    # API never called.
    assert backend._client.messages.create.call_count == 0


# ---------------------------------------------------------------------------
# Cost ceiling
# ---------------------------------------------------------------------------


def test_cost_ceiling_exceeded_raises(tmp_path):
    """Cost exceeding ceiling raises D7bLiveCostCeilingError."""
    # Use huge token counts to exceed the ceiling.
    expensive_response = _make_mock_response(
        input_tokens=100_000, output_tokens=100_000,
    )
    backend = _make_backend(tmp_path, cost_ceiling_usd=0.001)
    backend._client.messages.create.return_value = expensive_response

    with _PATCH_AUDIT:
        with pytest.raises(D7bLiveCostCeilingError) as exc_info:
            backend.score(_make_dsl(), "momentum", _make_batch_context())

    assert exc_info.value.error_code == "cost_ceiling_exceeded"


# ---------------------------------------------------------------------------
# Artifact file writing
# ---------------------------------------------------------------------------


def test_prompt_file_written_before_api_call(tmp_path):
    """Prompt file is written before the API call."""
    backend = _make_backend(tmp_path)

    with _PATCH_AUDIT:
        backend.score(_make_dsl(), "momentum", _make_batch_context())

    prompt_path = tmp_path / "critic" / "call_0001_prompt.txt"
    assert prompt_path.exists()
    content = prompt_path.read_text(encoding="utf-8")
    assert "rsi_14" in content  # DSL factor appears in prompt


def test_response_file_written_after_api_call(tmp_path):
    """Response file is written after a successful API call."""
    backend = _make_backend(tmp_path)

    with _PATCH_AUDIT:
        backend.score(_make_dsl(), "momentum", _make_batch_context())

    response_path = tmp_path / "critic" / "call_0001_response.json"
    assert response_path.exists()
    content = response_path.read_text(encoding="utf-8")
    assert "semantic_plausibility" in content


def test_traceback_file_written_on_content_error(tmp_path):
    """Traceback file is written when a content error occurs."""
    bad_response = _make_mock_response(text="NOT JSON")
    backend = _make_backend(tmp_path)
    backend._client.messages.create.return_value = bad_response

    with _PATCH_AUDIT:
        with pytest.raises(D7bLiveContentError):
            backend.score(_make_dsl(), "momentum", _make_batch_context())

    traceback_path = tmp_path / "critic" / "call_0001_traceback.txt"
    assert traceback_path.exists()
    content = traceback_path.read_text(encoding="utf-8")
    assert "D7bContentError" in content or "error_type" in content


# ---------------------------------------------------------------------------
# sanitized_signature
# ---------------------------------------------------------------------------


def test_sanitized_signature_truncates_to_200_chars():
    """sanitized_signature() truncates long messages to 200 chars."""
    long_detail = "x" * 300
    err = D7bLiveError("test_code", long_detail)
    sig = err.sanitized_signature()
    assert len(sig) <= 200
    assert sig.endswith("...")


def test_sanitized_signature_short_message():
    """Short messages are returned as-is without truncation."""
    err = D7bLiveError("api_timeout", "connection reset")
    sig = err.sanitized_signature()
    assert sig == "api_timeout: connection reset"
    assert len(sig) <= 200


# ---------------------------------------------------------------------------
# _classify_api_exception
# ---------------------------------------------------------------------------


def test_classify_timeout():
    exc = anthropic.APITimeoutError(request=MagicMock())
    assert _classify_api_exception(exc) == "api_timeout"


def test_classify_rate_limit():
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.headers = {}
    exc = anthropic.RateLimitError(
        message="rate limited", response=mock_resp, body=None,
    )
    assert _classify_api_exception(exc) == "api_rate_limit"


def test_classify_connection():
    exc = anthropic.APIConnectionError(request=MagicMock())
    assert _classify_api_exception(exc) == "api_connection"


def test_classify_server_error():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.headers = {}
    exc = anthropic.InternalServerError(
        message="server error", response=mock_resp, body=None,
    )
    assert _classify_api_exception(exc) == "api_server_error"


def test_classify_unknown_defaults_to_api_connection():
    """Unknown exception types default to api_connection."""
    assert _classify_api_exception(RuntimeError("unknown")) == "api_connection"


# ---------------------------------------------------------------------------
# Retry count
# ---------------------------------------------------------------------------


def test_retry_count_is_zero_on_first_success(tmp_path):
    """retry_count in metadata is 0 when the first attempt succeeds."""
    backend = _make_backend(tmp_path)
    with _PATCH_AUDIT:
        _, _, metadata = backend.score(
            _make_dsl(), "momentum", _make_batch_context(),
        )
    assert metadata["retry_count"] == 0


def test_retry_count_is_one_after_one_retry(tmp_path):
    """retry_count is 1 when the first attempt fails but retry succeeds."""
    success_response = _make_mock_response()
    backend = _make_backend(tmp_path)
    backend._client.messages.create.side_effect = [
        anthropic.APIConnectionError(request=MagicMock()),
        success_response,
    ]

    with _PATCH_AUDIT:
        _, _, metadata = backend.score(
            _make_dsl(), "momentum", _make_batch_context(),
        )
    assert metadata["retry_count"] == 1
