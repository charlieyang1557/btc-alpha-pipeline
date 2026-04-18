"""Phase 2B D6 — Proposer agent package.

This package defines the Proposer contract and its backends:

- ``interface`` — ``ProposerBackend`` Protocol, ``BatchContext``,
  ``ProposerOutput``, and ``DSLCandidate`` I/O schemas shared by every
  backend.
- ``stub_backend`` — ``StubProposerBackend``, a deterministic fixture
  backend that produces the seven D6 Stage 1 acceptance categories
  without any external model calls.
- ``sonnet_backend`` — ``SonnetProposerBackend``, the live Sonnet
  backend added in D6 Stage 2a. This is the ONLY module in the
  codebase that imports ``anthropic``.
- ``prompt_builder`` — ``build_prompt()`` and ``audit_prompt_for_leakage()``
  helpers. Used by both backends and tested in Stage 1 so leakage
  protection is in place before any live tokens are spent.

CONTRACT BOUNDARY: the orchestrator depends only on the interface
module; stub and Sonnet backends are interchangeable implementations
of :class:`~agents.proposer.interface.ProposerBackend`. The orchestrator
must NOT import ``anthropic`` or branch on backend type. See
``agents/orchestrator/ingest.py`` for the mirror-side contract.
"""

from agents.proposer.interface import (
    BatchContext,
    DSLCandidate,
    InvalidCandidate,
    ProposerBackend,
    ProposerOutput,
    ValidCandidate,
)
from agents.proposer.stub_backend import StubProposerBackend

__all__ = [
    "BatchContext",
    "DSLCandidate",
    "InvalidCandidate",
    "ProposerBackend",
    "ProposerOutput",
    "StubProposerBackend",
    "ValidCandidate",
]
