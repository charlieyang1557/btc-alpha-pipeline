"""D6 — Proposer contract (backend-agnostic).

Defines the I/O schemas every Proposer backend must conform to:

- :class:`BatchContext` — the frozen substrate plus orchestrator-supplied
  metadata handed in per call.
- :class:`ValidCandidate` / :class:`InvalidCandidate` — the two variants of
  :class:`DSLCandidate`. A backend must report an invalid candidate as
  such (raw_json + parse_error) rather than discarding it; the
  orchestrator counts it as ``hypotheses_attempted`` and assigns a
  terminal lifecycle state.
- :class:`ProposerOutput` — one or more candidates returned by a single
  generate call, with optional structured cost telemetry.
- :class:`ProposerBackend` — Protocol with a single ``generate`` method.
  Stub and Sonnet backends both implement it; the orchestrator depends
  only on this Protocol.

CONTRACT BOUNDARY: the orchestrator and budget ledger MUST NOT branch on
backend type or import any Sonnet-specific library. Any integration code
that needs to distinguish stub from Sonnet belongs in the backend itself,
not the caller. See ``agents/proposer/__init__.py`` for the mirror-side
contract.

DESIGN INVARIANT: ``allowed_factors`` and ``allowed_operators`` on
:class:`BatchContext` are the frozen research substrate. A backend MUST
NOT propose a factor outside ``allowed_factors`` or an operator outside
``allowed_operators``. If a proposal would require either, the backend
MUST emit an :class:`InvalidCandidate` (factor-out-of-registry or
grammar-violating); it MUST NOT return a suggestion, request, or hint
that a new factor or operator should be added. Registry and grammar
growth is a D1/D2 contract change requiring human review outside the
batch loop, per PHASE2A_SIGNOFF.md §E.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from strategies.dsl import StrategyDSL


# ---------------------------------------------------------------------------
# Input schema
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BatchContext:
    """Input handed to ``ProposerBackend.generate`` for one call.

    Fields:
        batch_id: UUID of the current batch, assigned by the orchestrator.
        position: 1-indexed hypothesis position within the batch (``k`` in
            blueprint pseudocode).
        batch_size: Total hypotheses this batch intends to attempt.
        allowed_factors: Sorted list of registered factor names at batch
            start. This is the frozen factor registry for the batch's
            lifetime. The Proposer MAY NOT reference factors outside this
            list.
        allowed_operators: Frozen DSL operator grammar
            (``("<", "<=", ">", ">=", "==", "crosses_above",
            "crosses_below")`` at Phase 2B). The Proposer MAY NOT use any
            operator outside this list.
        theme_slot: Optional rotating theme identifier for this call
            (integer index into D8's ``THEMES`` list). D6 accepts and
            forwards but does NOT decide rotation strategy; the
            orchestrator owns theme assignment.
        budget_remaining: ``{"batch_usd": float, "monthly_usd": float}``
            snapshot at call time. Informational; the budget gate is
            enforced pre-call by the orchestrator, not by the backend.
        batch_metadata: Optional free-form dict for additional signals
            (dedup rate, top factors, approved examples — all strictly
            non-metric per D6 prompt contamination rules).
    """

    batch_id: str
    position: int
    batch_size: int
    allowed_factors: tuple[str, ...]
    allowed_operators: tuple[str, ...]
    theme_slot: int | None = None
    budget_remaining: dict[str, float] = field(default_factory=dict)
    batch_metadata: dict[str, object] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Candidate variants
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ValidCandidate:
    """A candidate whose raw output parsed AND validated against D2 schema.

    ``dsl`` is a validated :class:`~strategies.dsl.StrategyDSL`; the
    orchestrator can compile, hash, and dedup it directly.
    ``provenance`` carries backend metadata (backend name, seed, token
    counts, stub case tag, etc.) for auditability but does not affect
    lifecycle routing.
    """

    dsl: StrategyDSL
    provenance: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class InvalidCandidate:
    """A candidate whose raw output failed to produce a valid DSL.

    ``raw_json`` is the exact string the backend returned (or attempted to
    return). It MUST be preserved so the orchestrator can log it for
    post-hoc audit. ``parse_error`` is a human-readable explanation of
    why validation failed (pydantic ValidationError string, JSON decode
    error, etc.).

    ``error_kind`` is a coarse tag the backend sets when it knows the
    reason a priori (e.g. the stub deliberately emitting an
    over-complex case). The orchestrator MUST NOT rely on ``error_kind``
    to route lifecycle state — it classifies errors mechanically from
    the raw JSON itself (see ``agents/orchestrator/ingest.py``) so that
    Sonnet output is handled identically to stub output. ``error_kind``
    is audit telemetry only.
    """

    raw_json: str
    parse_error: str
    error_kind: str | None = None
    provenance: dict[str, object] = field(default_factory=dict)


DSLCandidate = ValidCandidate | InvalidCandidate


# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProposerOutput:
    """One call's worth of output: a list of candidates plus telemetry.

    A backend MAY return more than one candidate per call (the stub does
    this to cover all seven Stage 1 categories in a single batch). Each
    candidate increments ``hypotheses_attempted`` when ingested.
    """

    candidates: tuple[DSLCandidate, ...]
    cost_estimate_usd: float = 0.0
    cost_actual_usd: float = 0.0
    backend_name: str = ""
    telemetry: dict[str, object] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Backend protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class ProposerBackend(Protocol):
    """Contract every Proposer backend must satisfy.

    Stub and Sonnet backends both implement this. The orchestrator holds
    one ``ProposerBackend`` instance and calls ``generate`` per
    hypothesis slot.
    """

    def generate(self, context: BatchContext) -> ProposerOutput:
        """Produce one call's worth of candidates.

        Must NEVER raise for ordinary parse/validation failures — those
        are represented as :class:`InvalidCandidate` entries in the
        returned output. Exceptions are reserved for infrastructure
        failures (network error for Sonnet, misconfiguration, etc.) and
        the orchestrator pre-charge ledger handles them via the
        crash-safe ``pending`` row pattern.
        """
        ...


__all__ = [
    "BatchContext",
    "DSLCandidate",
    "InvalidCandidate",
    "ProposerBackend",
    "ProposerOutput",
    "ValidCandidate",
]
