"""D6 Stage 1 — ingest a :class:`ProposerOutput` into lifecycle state.

At Stage 1, ingestion is the entire orchestrator: it validates each
candidate, hashes valid ones, checks for duplicates against prior
candidates in the same batch, and assigns exactly one terminal
lifecycle state per attempted hypothesis.

Lifecycle states active in D6 Stage 1 (reduced from D8's full 8-state
set; the rest arrive with D7 Critic and D8 full batch loop):

    - ``invalid_dsl``         — malformed JSON, unknown factor,
                                disallowed operator, non-finite
                                threshold, duplicate-condition
                                violation, or any other schema failure
                                that is NOT purely a complexity-budget
                                violation.
    - ``rejected_complexity`` — schema validation failed and every
                                reported error is a complexity-budget
                                violation (entry/exit groups > 3,
                                conditions per group > 4, max_hold_bars
                                > 720, name/description over length).
    - ``duplicate``           — valid DSL whose D3 hash matches a DSL
                                earlier in the same batch.
    - ``pending_backtest``    — valid unique DSL. **In D6 Stage 1 this
                                is treated as terminal** because
                                Critic (D7), train backtest (D8), and
                                holdout (D4 via D8) are not yet wired
                                into the loop. When D7/D8 land, this
                                state is demoted to transient and the
                                hypothesis flows onward.

CONTRACT BOUNDARY: this module imports only from ``agents.proposer``
and ``agents.hypothesis_hash`` plus stdlib + pydantic. It MUST NOT
import ``anthropic`` or any backend-specific library; the dependency
on Proposer is via the :class:`ProposerBackend` Protocol only. The
D6 Stage 1 test suite enforces this mechanically via a ripgrep check
over ``agents/orchestrator/``.

DESIGN INVARIANT (``hypotheses_attempted`` counting rule):
Every candidate in a :class:`ProposerOutput` increments
``hypotheses_attempted`` exactly once, regardless of whether it is a
:class:`ValidCandidate` or :class:`InvalidCandidate`, and regardless of
its eventual lifecycle state. This matches the blueprint's hard rule:
invalid DSL is not a free retry. Unissued slots (budget exhausted before
proposing) are tracked separately by the orchestrator in
``batch_summary.unissued_slots`` and are NOT ingested here.

DESIGN INVARIANT (invariant check timing):
:func:`assert_lifecycle_invariant_at_batch_close` is intended to be
called ONLY at batch close. Mid-batch the sum of terminal counts can
legitimately equal ``hypotheses_attempted`` in Stage 1 (because there
is no transient state yet), but enforcing the check mid-batch would
violate the blueprint contract once ``pending_dsr`` becomes transient
in later phases. Treat it as batch-close-only from day one.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from agents.hypothesis_hash import hash_dsl
from agents.proposer.interface import (
    DSLCandidate,
    InvalidCandidate,
    ProposerOutput,
    ValidCandidate,
)

# ---------------------------------------------------------------------------
# Lifecycle states (D6 Stage 1 subset; full list arrives with D7/D8/D9)
# ---------------------------------------------------------------------------

INVALID_DSL = "invalid_dsl"
REJECTED_COMPLEXITY = "rejected_complexity"
DUPLICATE = "duplicate"
PENDING_BACKTEST = "pending_backtest"

D6_STAGE1_LIFECYCLE_STATES: tuple[str, ...] = (
    INVALID_DSL,
    REJECTED_COMPLEXITY,
    DUPLICATE,
    PENDING_BACKTEST,
)


# ---------------------------------------------------------------------------
# Complexity-budget error classifier
# ---------------------------------------------------------------------------

# Pydantic error-type strings that correspond to "above the upper bound"
# violations. (Below-minimum violations like ``too_short`` /
# ``string_too_short`` / ``greater_than_equal`` are treated as
# generic schema failures, not complexity-budget violations.)
_COMPLEXITY_ERROR_TYPES: frozenset[str] = frozenset({
    "too_long",
    "string_too_long",
    "less_than_equal",
})

# D2 fields governed by the complexity budget. An error's ``loc`` must
# contain one of these segments to qualify.
_COMPLEXITY_FIELDS: frozenset[str] = frozenset({
    "entry",
    "exit",
    "conditions",
    "max_hold_bars",
    "name",
    "description",
})


def _is_purely_complexity_budget(errors: list[dict]) -> bool:
    """True iff every reported validation error is a complexity violation.

    A DSL that violates both complexity AND some other rule (e.g., 4
    entry groups AND a NaN threshold) returns False and is routed to
    ``invalid_dsl``. This keeps ``rejected_complexity`` a clean,
    interpretable signal: only emitted when the sole blocker is that
    the proposal overshoots the budget.
    """
    if not errors:
        return False
    for e in errors:
        etype = e.get("type", "")
        if etype not in _COMPLEXITY_ERROR_TYPES:
            return False
        loc = e.get("loc") or ()
        hits_complexity_field = any(
            isinstance(seg, str) and seg in _COMPLEXITY_FIELDS
            for seg in loc
        )
        if not hits_complexity_field:
            return False
    return True


# ---------------------------------------------------------------------------
# Batch state + per-hypothesis record
# ---------------------------------------------------------------------------


@dataclass
class HypothesisRecord:
    """Audit trail for one attempted hypothesis.

    Kept in-memory for D6 Stage 1; persisted to experiment_registry.db
    later in D8 via a dedicated writer. Keeping the schema stable now
    avoids a painful migration later.
    """

    batch_id: str
    position: int
    lifecycle_state: str
    hypothesis_hash: str | None
    error_kind: str | None
    parse_error: str | None
    provenance: dict


@dataclass
class BatchIngestState:
    """Running state of one batch being ingested, Stage 1 scope.

    Fields:
        batch_id: UUID of the batch, assigned by the orchestrator.
        hypotheses_attempted: Monotonically increases by 1 per
            ingested candidate.
        seen_hashes: Set of D3 hashes seen so far in this batch. A
            hash appearing twice routes the second occurrence to
            ``duplicate``.
        lifecycle_counts: Running terminal-state counts, keyed by
            lifecycle-state name.
        records: Per-hypothesis audit records in ingestion order.
    """

    batch_id: str
    hypotheses_attempted: int = 0
    seen_hashes: set[str] = field(default_factory=set)
    lifecycle_counts: dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    records: list[HypothesisRecord] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core ingestion
# ---------------------------------------------------------------------------


def ingest_candidate(
    state: BatchIngestState, candidate: DSLCandidate
) -> HypothesisRecord:
    """Assign exactly one terminal lifecycle state to one candidate.

    Increments ``state.hypotheses_attempted`` unconditionally. Returns
    the per-hypothesis audit record and also appends it to
    ``state.records``.
    """
    state.hypotheses_attempted += 1
    position = state.hypotheses_attempted

    if isinstance(candidate, InvalidCandidate):
        validation_errors = candidate.provenance.get("validation_errors") or []
        if _is_purely_complexity_budget(validation_errors):
            lifecycle = REJECTED_COMPLEXITY
        else:
            lifecycle = INVALID_DSL
        record = HypothesisRecord(
            batch_id=state.batch_id,
            position=position,
            lifecycle_state=lifecycle,
            hypothesis_hash=None,
            error_kind=candidate.error_kind,
            parse_error=candidate.parse_error,
            provenance=dict(candidate.provenance),
        )
    elif isinstance(candidate, ValidCandidate):
        h = hash_dsl(candidate.dsl)
        if h in state.seen_hashes:
            lifecycle = DUPLICATE
        else:
            state.seen_hashes.add(h)
            lifecycle = PENDING_BACKTEST
        record = HypothesisRecord(
            batch_id=state.batch_id,
            position=position,
            lifecycle_state=lifecycle,
            hypothesis_hash=h,
            error_kind=None,
            parse_error=None,
            provenance=dict(candidate.provenance),
        )
    else:  # pragma: no cover — guarded by type system
        raise TypeError(f"unknown candidate type: {type(candidate).__name__}")

    state.lifecycle_counts[record.lifecycle_state] += 1
    state.records.append(record)
    return record


def ingest_output(
    state: BatchIngestState, output: ProposerOutput
) -> list[HypothesisRecord]:
    """Ingest every candidate from one :class:`ProposerOutput` in order."""
    return [ingest_candidate(state, c) for c in output.candidates]


def ingest_outputs(
    state: BatchIngestState, outputs: Iterable[ProposerOutput]
) -> list[HypothesisRecord]:
    """Ingest multiple outputs in sequence (e.g., one per generate call)."""
    records: list[HypothesisRecord] = []
    for out in outputs:
        records.extend(ingest_output(state, out))
    return records


# ---------------------------------------------------------------------------
# Batch-close invariant
# ---------------------------------------------------------------------------


def assert_lifecycle_invariant_at_batch_close(state: BatchIngestState) -> None:
    """Assert sum(terminal lifecycle counts) == hypotheses_attempted.

    Must only be called at batch close. In D6 Stage 1 all four active
    lifecycle states are terminal, so the sum is simply total. In later
    phases, transient states (``pending_dsr``) are resolved to terminal
    ones by D9's ``finalize_batch()`` before this check runs; calling
    it mid-batch would therefore produce a false positive.

    Raises:
        AssertionError: if the invariant does not hold.
    """
    terminal_total = sum(
        state.lifecycle_counts.get(s, 0) for s in D6_STAGE1_LIFECYCLE_STATES
    )
    if terminal_total != state.hypotheses_attempted:
        raise AssertionError(
            "Lifecycle invariant violated: "
            f"sum(terminal_counts)={terminal_total} != "
            f"hypotheses_attempted={state.hypotheses_attempted} "
            f"(counts={dict(state.lifecycle_counts)})"
        )
    # Also guard against unknown states sneaking in.
    unknown = set(state.lifecycle_counts) - set(D6_STAGE1_LIFECYCLE_STATES)
    if unknown:
        raise AssertionError(
            f"Lifecycle invariant violated: unknown state(s) {unknown!r} "
            f"in counts {dict(state.lifecycle_counts)}. "
            f"Stage 1 lifecycle set: {D6_STAGE1_LIFECYCLE_STATES}"
        )


__all__ = [
    "BatchIngestState",
    "D6_STAGE1_LIFECYCLE_STATES",
    "DUPLICATE",
    "HypothesisRecord",
    "INVALID_DSL",
    "PENDING_BACKTEST",
    "REJECTED_COMPLEXITY",
    "assert_lifecycle_invariant_at_batch_close",
    "ingest_candidate",
    "ingest_output",
    "ingest_outputs",
]
