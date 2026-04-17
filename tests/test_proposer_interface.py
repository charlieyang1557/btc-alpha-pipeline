"""D6 Stage 1 — ProposerBackend Protocol + I/O schemas.

These tests pin the backend-agnostic contract that both the stub and
(future) Sonnet backends must satisfy. If any of these fail, the
Sonnet integration in Stage 2 has a broken foundation; do not proceed.
"""

from __future__ import annotations

from typing import get_type_hints

import pytest

from agents.proposer import (
    BatchContext,
    DSLCandidate,
    InvalidCandidate,
    ProposerBackend,
    ProposerOutput,
    StubProposerBackend,
    ValidCandidate,
)


# ---------------------------------------------------------------------------
# BatchContext
# ---------------------------------------------------------------------------


def test_batch_context_is_frozen():
    """BatchContext is immutable so a backend cannot mutate caller state."""
    ctx = BatchContext(
        batch_id="b",
        position=1,
        batch_size=7,
        allowed_factors=("return_24h",),
        allowed_operators=(">",),
    )
    with pytest.raises((AttributeError, Exception)):
        ctx.position = 2  # type: ignore[misc]


def test_batch_context_defaults_are_empty_dicts_not_shared():
    """``budget_remaining`` and ``batch_metadata`` default to per-instance dicts."""
    a = BatchContext(
        batch_id="a", position=1, batch_size=1,
        allowed_factors=(), allowed_operators=(),
    )
    b = BatchContext(
        batch_id="b", position=1, batch_size=1,
        allowed_factors=(), allowed_operators=(),
    )
    a.batch_metadata["x"] = 1
    assert "x" not in b.batch_metadata


# ---------------------------------------------------------------------------
# Candidate variants
# ---------------------------------------------------------------------------


def test_candidate_union_covers_both_variants():
    hints = get_type_hints(ProposerOutput)
    # DSLCandidate alias resolves to ValidCandidate | InvalidCandidate.
    from agents.proposer import interface as iface
    assert iface.DSLCandidate.__args__ == (ValidCandidate, InvalidCandidate)
    # ProposerOutput.candidates is a tuple of that union.
    assert hints["candidates"] == tuple[DSLCandidate, ...]


def test_invalid_candidate_preserves_raw_json():
    inv = InvalidCandidate(
        raw_json="{bad",
        parse_error="json_decode_error: foo",
        error_kind="invalid_json",
        provenance={"backend": "stub"},
    )
    assert inv.raw_json == "{bad"
    assert inv.parse_error.startswith("json_decode_error")
    assert inv.error_kind == "invalid_json"
    assert inv.provenance == {"backend": "stub"}


# ---------------------------------------------------------------------------
# ProposerBackend Protocol
# ---------------------------------------------------------------------------


def test_stub_backend_satisfies_protocol():
    """runtime_checkable Protocol conformance for the stub backend."""
    backend: ProposerBackend = StubProposerBackend()
    assert isinstance(backend, ProposerBackend)


def test_non_backend_does_not_satisfy_protocol():
    class NotABackend:
        pass

    assert not isinstance(NotABackend(), ProposerBackend)


def test_object_with_wrong_signature_still_satisfies_structural_protocol():
    """runtime_checkable Protocol only checks method presence, not signature.

    Documented here so it is not mistaken for a safety net — the real
    signature enforcement is at call-site via :class:`BatchContext` /
    :class:`ProposerOutput` typing.
    """

    class WrongSig:
        def generate(self, x, y, z):  # noqa: D401
            ...

    assert isinstance(WrongSig(), ProposerBackend)
