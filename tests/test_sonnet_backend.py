"""D6 Stage 2a — Sonnet backend tests (mocked API, no real calls).

Covers:
- ProposerBackend Protocol conformance
- Infrastructure failure → exponential backoff → retries exhausted
- Model failure → immediate terminal, no retry
- Successful response → classify_raw_json → ValidCandidate/InvalidCandidate
- Raw payload logging (prompt + response files created)
- Token-based cost computation
- Empty response body → empty candidates tuple
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import anthropic

from agents.proposer import ProposerBackend
from agents.proposer.interface import BatchContext, ValidCandidate, InvalidCandidate
from agents.proposer.sonnet_backend import (
    SONNET_INPUT_PRICE_PER_MTOK,
    SONNET_OUTPUT_PRICE_PER_MTOK,
    SonnetProposerBackend,
    classify_api_exception,
    compute_cost_usd,
    estimate_cost_usd,
)
from factors.registry import get_registry


ALL_OPS = ("<", "<=", ">", ">=", "==", "crosses_above", "crosses_below")


@pytest.fixture
def registry():
    return get_registry()


@pytest.fixture
def ctx(registry):
    return BatchContext(
        batch_id="test-batch-001",
        position=1,
        batch_size=1,
        allowed_factors=tuple(registry.list_names()),
        allowed_operators=ALL_OPS,
        theme_slot=0,
    )


def _mock_response(text: str, input_tokens: int = 500, output_tokens: int = 200):
    """Build a mock Anthropic Messages response."""
    content_block = SimpleNamespace(text=text, type="text")
    usage = SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens)
    return SimpleNamespace(
        content=[content_block],
        usage=usage,
        stop_reason="end_turn",
        model="claude-sonnet-4-5",
    )


def _valid_dsl_json(registry) -> str:
    first_factor = registry.list_names()[0]
    return json.dumps({
        "name": "test_sonnet_momentum",
        "description": "Enter on return_24h > 2%, exit on return_24h < 0%.",
        "entry": [{"conditions": [{"factor": "return_24h", "op": ">", "value": 0.02}]}],
        "exit": [{"conditions": [{"factor": "return_24h", "op": "<", "value": 0.0}]}],
        "position_sizing": "full_equity",
        "max_hold_bars": None,
    })


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


def test_sonnet_backend_satisfies_protocol():
    backend = SonnetProposerBackend()
    assert isinstance(backend, ProposerBackend)


# ---------------------------------------------------------------------------
# classify_api_exception
# ---------------------------------------------------------------------------


def test_rate_limit_is_infrastructure():
    exc = anthropic.RateLimitError(
        message="rate limited",
        response=MagicMock(status_code=429),
        body=None,
    )
    assert classify_api_exception(exc) == "infrastructure"


def test_internal_server_error_is_infrastructure():
    exc = anthropic.InternalServerError(
        message="overloaded",
        response=MagicMock(status_code=529),
        body=None,
    )
    assert classify_api_exception(exc) == "infrastructure"


def test_connection_error_is_infrastructure():
    exc = anthropic.APIConnectionError(request=MagicMock())
    assert classify_api_exception(exc) == "infrastructure"


def test_timeout_error_is_infrastructure():
    exc = anthropic.APITimeoutError(request=MagicMock())
    assert classify_api_exception(exc) == "infrastructure"


def test_bad_request_is_model():
    exc = anthropic.BadRequestError(
        message="bad request",
        response=MagicMock(status_code=400),
        body=None,
    )
    assert classify_api_exception(exc) == "model"


def test_auth_error_is_model():
    exc = anthropic.AuthenticationError(
        message="invalid key",
        response=MagicMock(status_code=401),
        body=None,
    )
    assert classify_api_exception(exc) == "model"


def test_generic_exception_is_model():
    assert classify_api_exception(ValueError("something")) == "model"


# ---------------------------------------------------------------------------
# Cost computation
# ---------------------------------------------------------------------------


def test_compute_cost_usd():
    cost = compute_cost_usd(input_tokens=1000, output_tokens=500)
    expected = (1000 * 3.0 / 1_000_000) + (500 * 15.0 / 1_000_000)
    assert cost == pytest.approx(expected)


def test_estimate_cost_usd_upper_bound():
    est = estimate_cost_usd(estimated_input_tokens=4000, max_output_tokens=2000)
    assert est == pytest.approx(compute_cost_usd(4000, 2000))


# ---------------------------------------------------------------------------
# Successful response → valid candidate
# ---------------------------------------------------------------------------


def test_valid_sonnet_response(ctx, registry, tmp_path):
    dsl_json = _valid_dsl_json(registry)
    mock_resp = _mock_response(dsl_json, input_tokens=800, output_tokens=150)

    backend = SonnetProposerBackend(
        registry=registry,
        raw_payload_dir=tmp_path / "payloads",
        backoff_base_seconds=0.0,
    )

    with patch.object(backend, "_get_client") as mock_client:
        mock_client.return_value.messages.create.return_value = mock_resp
        output = backend.generate(ctx)

    assert len(output.candidates) == 1
    assert isinstance(output.candidates[0], ValidCandidate)
    assert output.backend_name == "sonnet"
    assert output.cost_actual_usd == pytest.approx(
        compute_cost_usd(800, 150)
    )
    assert output.telemetry["input_tokens"] == 800
    assert output.telemetry["output_tokens"] == 150

    # Payload files exist.
    batch_dir = tmp_path / "payloads" / f"batch_{ctx.batch_id}"
    assert (batch_dir / "attempt_0001_prompt.txt").exists()
    assert (batch_dir / "attempt_0001_response.txt").exists()


def test_invalid_json_sonnet_response(ctx, registry, tmp_path):
    """Bad JSON from Sonnet → InvalidCandidate, no retry."""
    mock_resp = _mock_response("{bad json", input_tokens=600, output_tokens=50)

    backend = SonnetProposerBackend(
        registry=registry,
        raw_payload_dir=tmp_path / "payloads",
        backoff_base_seconds=0.0,
    )

    with patch.object(backend, "_get_client") as mock_client:
        mock_client.return_value.messages.create.return_value = mock_resp
        output = backend.generate(ctx)

    assert len(output.candidates) == 1
    assert isinstance(output.candidates[0], InvalidCandidate)
    assert output.cost_actual_usd > 0


# ---------------------------------------------------------------------------
# Empty response body → empty candidates
# ---------------------------------------------------------------------------


def test_empty_response_body(ctx, registry, tmp_path):
    mock_resp = _mock_response("", input_tokens=500, output_tokens=0)

    backend = SonnetProposerBackend(
        registry=registry,
        raw_payload_dir=tmp_path / "payloads",
        backoff_base_seconds=0.0,
    )

    with patch.object(backend, "_get_client") as mock_client:
        mock_client.return_value.messages.create.return_value = mock_resp
        output = backend.generate(ctx)

    assert len(output.candidates) == 0
    assert output.telemetry["error"] == "empty_response_body"


# ---------------------------------------------------------------------------
# Infrastructure failure → backoff + retry → exhausted → empty
# ---------------------------------------------------------------------------


def test_infrastructure_failure_retries_then_empty(ctx, registry, tmp_path):
    rate_limit = anthropic.RateLimitError(
        message="rate limited",
        response=MagicMock(status_code=429),
        body=None,
    )

    backend = SonnetProposerBackend(
        registry=registry,
        max_retries=3,
        backoff_base_seconds=0.0,
        raw_payload_dir=tmp_path / "payloads",
    )

    with patch.object(backend, "_get_client") as mock_client:
        mock_client.return_value.messages.create.side_effect = rate_limit
        output = backend.generate(ctx)

    # 1 initial + 3 retries = 4 total calls
    assert mock_client.return_value.messages.create.call_count == 4
    assert len(output.candidates) == 0
    assert output.telemetry["retries_exhausted"] is True

    # Response error files for each attempt (retry 0=None, 1, 2, 3)
    batch_dir = tmp_path / "payloads" / f"batch_{ctx.batch_id}"
    assert (batch_dir / "attempt_0001_response.txt").exists()
    assert (batch_dir / "attempt_0001_retry_1_response.txt").exists()
    assert (batch_dir / "attempt_0001_retry_2_response.txt").exists()
    assert (batch_dir / "attempt_0001_retry_3_response.txt").exists()


def test_infrastructure_failure_succeeds_on_retry(ctx, registry, tmp_path):
    """First call fails with 429, second succeeds."""
    rate_limit = anthropic.RateLimitError(
        message="rate limited",
        response=MagicMock(status_code=429),
        body=None,
    )
    dsl_json = _valid_dsl_json(registry)
    mock_resp = _mock_response(dsl_json, input_tokens=700, output_tokens=120)

    backend = SonnetProposerBackend(
        registry=registry,
        max_retries=3,
        backoff_base_seconds=0.0,
        raw_payload_dir=tmp_path / "payloads",
    )

    with patch.object(backend, "_get_client") as mock_client:
        mock_client.return_value.messages.create.side_effect = [
            rate_limit,
            mock_resp,
        ]
        output = backend.generate(ctx)

    assert mock_client.return_value.messages.create.call_count == 2
    assert len(output.candidates) == 1
    assert isinstance(output.candidates[0], ValidCandidate)


# ---------------------------------------------------------------------------
# Model failure → immediate, no retry
# ---------------------------------------------------------------------------


def test_model_failure_no_retry(ctx, registry, tmp_path):
    bad_request = anthropic.BadRequestError(
        message="bad request",
        response=MagicMock(status_code=400),
        body=None,
    )

    backend = SonnetProposerBackend(
        registry=registry,
        max_retries=3,
        backoff_base_seconds=0.0,
        raw_payload_dir=tmp_path / "payloads",
    )

    with patch.object(backend, "_get_client") as mock_client:
        mock_client.return_value.messages.create.side_effect = bad_request
        output = backend.generate(ctx)

    # Only 1 call — no retry for model errors.
    assert mock_client.return_value.messages.create.call_count == 1
    assert len(output.candidates) == 0
    assert output.telemetry["error_category"] == "model"


# ---------------------------------------------------------------------------
# Raw payload logging
# ---------------------------------------------------------------------------


def test_payload_logging_disabled_when_none(ctx, registry):
    """No crash when raw_payload_dir is None."""
    dsl_json = _valid_dsl_json(registry)
    mock_resp = _mock_response(dsl_json)

    backend = SonnetProposerBackend(
        registry=registry,
        raw_payload_dir=None,
        backoff_base_seconds=0.0,
    )

    with patch.object(backend, "_get_client") as mock_client:
        mock_client.return_value.messages.create.return_value = mock_resp
        output = backend.generate(ctx)

    assert len(output.candidates) == 1


def test_prompt_payload_contains_full_text(ctx, registry, tmp_path):
    dsl_json = _valid_dsl_json(registry)
    mock_resp = _mock_response(dsl_json)

    backend = SonnetProposerBackend(
        registry=registry,
        raw_payload_dir=tmp_path / "payloads",
        backoff_base_seconds=0.0,
    )

    with patch.object(backend, "_get_client") as mock_client:
        mock_client.return_value.messages.create.return_value = mock_resp
        backend.generate(ctx)

    prompt_file = (
        tmp_path / "payloads" / f"batch_{ctx.batch_id}" / "attempt_0001_prompt.txt"
    )
    content = prompt_file.read_text(encoding="utf-8")
    assert "quantitative researcher" in content
    assert "return_24h" in content


# ---------------------------------------------------------------------------
# Stub backend still works (regression)
# ---------------------------------------------------------------------------


def test_stub_backend_unaffected_by_sonnet_import(registry):
    """Importing sonnet_backend must not break stub_backend."""
    from agents.proposer.stub_backend import StubProposerBackend

    backend = StubProposerBackend(registry=registry)
    ctx = BatchContext(
        batch_id="stub-batch",
        position=1,
        batch_size=7,
        allowed_factors=tuple(registry.list_names()),
        allowed_operators=ALL_OPS,
        theme_slot=0,
    )
    output = backend.generate(ctx)
    assert len(output.candidates) == 1
    assert isinstance(output.candidates[0], ValidCandidate)
