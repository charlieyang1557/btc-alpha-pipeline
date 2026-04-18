"""Tests for agents/critic/d7b_live.py error class taxonomy (D7 Stage 2a).

Covers:
    - D7bLiveError.sanitized_signature() method
    - D7bLiveAPIError subclasses D7bLiveError
    - D7bLiveContentError subclasses D7bLiveError
    - D7bLiveLeakageAuditError sets error_code correctly
    - D7bLiveCostCeilingError formats message correctly
    - Error class hierarchy
"""

from __future__ import annotations

import pytest

from agents.critic.d7b_live import (
    D7bLiveAPIError,
    D7bLiveContentError,
    D7bLiveCostCeilingError,
    D7bLiveError,
    D7bLiveLeakageAuditError,
)


# ---------------------------------------------------------------------------
# D7bLiveError base
# ---------------------------------------------------------------------------


def test_d7b_live_error_has_sanitized_signature():
    """D7bLiveError instances have a sanitized_signature method."""
    err = D7bLiveError("test_code", "some detail")
    sig = err.sanitized_signature()
    assert isinstance(sig, str)
    assert "test_code" in sig
    assert "some detail" in sig


def test_d7b_live_error_has_error_code():
    err = D7bLiveError("my_code", "detail")
    assert err.error_code == "my_code"


def test_d7b_live_error_has_detail():
    err = D7bLiveError("my_code", "my detail")
    assert err.detail == "my detail"


# ---------------------------------------------------------------------------
# D7bLiveAPIError
# ---------------------------------------------------------------------------


def test_d7b_live_api_error_subclasses_d7b_live_error():
    """D7bLiveAPIError is a subclass of D7bLiveError."""
    assert issubclass(D7bLiveAPIError, D7bLiveError)


def test_d7b_live_api_error_instance():
    err = D7bLiveAPIError("api_timeout", "timed out after 30s")
    assert isinstance(err, D7bLiveError)
    assert err.error_code == "api_timeout"


# ---------------------------------------------------------------------------
# D7bLiveContentError
# ---------------------------------------------------------------------------


def test_d7b_live_content_error_subclasses_d7b_live_error():
    """D7bLiveContentError is a subclass of D7bLiveError."""
    assert issubclass(D7bLiveContentError, D7bLiveError)


def test_d7b_live_content_error_instance():
    err = D7bLiveContentError("json_decode", "Unexpected character")
    assert isinstance(err, D7bLiveError)
    assert err.error_code == "json_decode"


# ---------------------------------------------------------------------------
# D7bLiveLeakageAuditError
# ---------------------------------------------------------------------------


def test_leakage_audit_error_sets_error_code():
    """D7bLiveLeakageAuditError sets error_code to 'leakage_audit_fail'."""
    err = D7bLiveLeakageAuditError("UUID leaked: 01234567-...")
    assert err.error_code == "leakage_audit_fail"


def test_leakage_audit_error_preserves_detail():
    detail = "UUID leaked: 01234567-abcd-ef01-2345-6789abcdef01"
    err = D7bLiveLeakageAuditError(detail)
    assert err.detail == detail


def test_leakage_audit_error_subclasses_d7b_live_error():
    err = D7bLiveLeakageAuditError("detail")
    assert isinstance(err, D7bLiveError)


# ---------------------------------------------------------------------------
# D7bLiveCostCeilingError
# ---------------------------------------------------------------------------


def test_cost_ceiling_error_formats_message_correctly():
    """D7bLiveCostCeilingError formats measured and ceiling costs."""
    err = D7bLiveCostCeilingError(measured_cost=0.065, ceiling=0.05)
    assert err.error_code == "cost_ceiling_exceeded"
    assert "0.065" in err.detail
    assert "0.05" in err.detail


def test_cost_ceiling_error_subclasses_d7b_live_error():
    err = D7bLiveCostCeilingError(0.1, 0.05)
    assert isinstance(err, D7bLiveError)


def test_cost_ceiling_error_sanitized_signature():
    err = D7bLiveCostCeilingError(0.123456, 0.05)
    sig = err.sanitized_signature()
    assert "cost_ceiling_exceeded" in sig
    assert len(sig) <= 200
