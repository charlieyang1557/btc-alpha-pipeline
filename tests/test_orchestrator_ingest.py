"""D6 Stage 1 — orchestrator ingest (validate → hash → dedup → lifecycle).

Tests the seven-scenario lifecycle mapping end-to-end and pins the
``sum(terminal_counts) == hypotheses_attempted`` invariant. Also
exercises the complexity-budget classifier directly with synthetic
error lists so both arms of
``_is_purely_complexity_budget`` are covered.
"""

from __future__ import annotations

import json
import subprocess
import uuid
from pathlib import Path

import pytest

from agents.hypothesis_hash import hash_dsl
from agents.orchestrator.ingest import (
    BACKEND_EMPTY_OUTPUT,
    BatchIngestState,
    D6_STAGE1_LIFECYCLE_STATES,
    DUPLICATE,
    INVALID_DSL,
    PENDING_BACKTEST,
    REJECTED_COMPLEXITY,
    _is_purely_complexity_budget,
    assert_lifecycle_invariant_at_batch_close,
    ingest_candidate,
    ingest_output,
    ingest_outputs,
)
from agents.proposer.interface import ProposerOutput
from agents.proposer import (
    BatchContext,
    InvalidCandidate,
    StubProposerBackend,
    ValidCandidate,
)
from agents.proposer.stub_backend import (
    DEFAULT_SCENARIO_SEQUENCE,
    classify_raw_json,
    _VALID_DSL_JSON,
)
from factors.registry import get_registry


ALL_OPS = (
    "<", "<=", ">", ">=", "==", "crosses_above", "crosses_below",
)


@pytest.fixture
def registry():
    return get_registry()


@pytest.fixture
def batch_id():
    return str(uuid.uuid4())


def _ctx(batch_id: str, position: int, batch_size: int, registry) -> BatchContext:
    return BatchContext(
        batch_id=batch_id,
        position=position,
        batch_size=batch_size,
        allowed_factors=tuple(registry.list_names()),
        allowed_operators=ALL_OPS,
        theme_slot=(position - 1) % 6,
    )


# ---------------------------------------------------------------------------
# Seven-scenario end-to-end lifecycle mapping
# ---------------------------------------------------------------------------


EXPECTED_LIFECYCLE: dict[str, str] = {
    "valid": PENDING_BACKTEST,
    "invalid_json": INVALID_DSL,
    "duplicate_of_valid": DUPLICATE,
    "over_complex": REJECTED_COMPLEXITY,
    "factor_out_of_registry": INVALID_DSL,
    "grammar_violation": INVALID_DSL,
    "non_finite_threshold": INVALID_DSL,
}


def test_seven_scenarios_map_to_expected_lifecycle(batch_id, registry):
    backend = StubProposerBackend(registry=registry)
    state = BatchIngestState(batch_id=batch_id)
    outputs = [
        backend.generate(_ctx(batch_id, k, 7, registry))
        for k in range(1, 8)
    ]
    records = ingest_outputs(state, outputs)
    assert len(records) == 7
    for rec in records:
        scenario = rec.provenance["scenario"]
        assert rec.lifecycle_state == EXPECTED_LIFECYCLE[scenario], (
            f"scenario {scenario} routed to {rec.lifecycle_state}, "
            f"expected {EXPECTED_LIFECYCLE[scenario]}"
        )
    # Sum invariant must hold at batch close.
    assert state.hypotheses_attempted == 7
    assert_lifecycle_invariant_at_batch_close(state)


def test_hypotheses_attempted_increments_for_every_candidate(batch_id, registry):
    """DESIGN INVARIANT: invalid DSL is not a free retry."""
    backend = StubProposerBackend(registry=registry)
    state = BatchIngestState(batch_id=batch_id)
    for k in range(1, 8):
        backend.generate(_ctx(batch_id, k, 7, registry))  # no-op for state
    # Force-ingest each candidate.
    for k in range(1, 8):
        out = backend.generate(_ctx(batch_id, k, 7, registry))
        ingest_output(state, out)
    assert state.hypotheses_attempted == 7


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------


def test_dup_detection_uses_d3_hash(batch_id, registry):
    """``valid`` then ``duplicate_of_valid`` → DUPLICATE on the second."""
    first = classify_raw_json(_VALID_DSL_JSON, registry=registry,
                              provenance={"scenario": "valid"})
    second = classify_raw_json(_VALID_DSL_JSON, registry=registry,
                               provenance={"scenario": "duplicate_of_valid"})
    assert isinstance(first, ValidCandidate)
    assert isinstance(second, ValidCandidate)

    state = BatchIngestState(batch_id=batch_id)
    r1 = ingest_candidate(state, first)
    r2 = ingest_candidate(state, second)
    assert r1.lifecycle_state == PENDING_BACKTEST
    assert r2.lifecycle_state == DUPLICATE
    assert r1.hypothesis_hash == r2.hypothesis_hash == hash_dsl(first.dsl)


def test_dup_detection_does_not_cross_batches(registry):
    """Two fresh BatchIngestStates have independent seen_hashes."""
    state_a = BatchIngestState(batch_id="batch-a")
    state_b = BatchIngestState(batch_id="batch-b")
    cand = classify_raw_json(_VALID_DSL_JSON, registry=registry)
    ra = ingest_candidate(state_a, cand)
    rb = ingest_candidate(state_b, cand)
    assert ra.lifecycle_state == PENDING_BACKTEST
    assert rb.lifecycle_state == PENDING_BACKTEST


# ---------------------------------------------------------------------------
# Complexity classifier
# ---------------------------------------------------------------------------


def test_classifier_all_complexity_returns_true():
    errors = [
        {"type": "too_long", "loc": ("entry",)},
        {"type": "too_long", "loc": ("exit", 0, "conditions")},
        {"type": "string_too_long", "loc": ("description",)},
        {"type": "less_than_equal", "loc": ("max_hold_bars",)},
    ]
    assert _is_purely_complexity_budget(errors) is True


def test_classifier_mixed_errors_returns_false():
    errors = [
        {"type": "too_long", "loc": ("entry",)},
        {"type": "value_error", "loc": ("entry", 0, "conditions", 0, "value")},
    ]
    assert _is_purely_complexity_budget(errors) is False


def test_classifier_empty_errors_returns_false():
    assert _is_purely_complexity_budget([]) is False


def test_classifier_complexity_type_on_non_complexity_field_returns_false():
    """``too_long`` on a non-budget field is not a budget violation."""
    errors = [{"type": "too_long", "loc": ("some_unrelated_field",)}]
    assert _is_purely_complexity_budget(errors) is False


# ---------------------------------------------------------------------------
# Invariant guard
# ---------------------------------------------------------------------------


def test_invariant_raises_on_unknown_state(batch_id):
    """An unknown state that still sums correctly must still raise.

    We inflate ``hypotheses_attempted`` alongside the unknown count so
    the sum-matches arm passes and we reach the second (unknown-state)
    guard cleanly.
    """
    state = BatchIngestState(batch_id=batch_id)
    state.hypotheses_attempted = 1
    state.lifecycle_counts["martian_state"] = 1
    with pytest.raises(AssertionError, match="sum"):
        assert_lifecycle_invariant_at_batch_close(state)

    # Now arrange sums to balance against the known terminal set so the
    # first guard passes and the unknown-state guard fires instead.
    state.hypotheses_attempted = 2
    state.lifecycle_counts[PENDING_BACKTEST] = 2  # known sum == attempted
    # ``martian_state`` remains; unknown-state guard must reject.
    with pytest.raises(AssertionError, match="unknown state"):
        assert_lifecycle_invariant_at_batch_close(state)


def test_invariant_raises_when_counts_dont_match_attempts(batch_id):
    state = BatchIngestState(batch_id=batch_id)
    state.hypotheses_attempted = 3
    state.lifecycle_counts[PENDING_BACKTEST] = 1  # only one counted
    with pytest.raises(AssertionError, match="sum\\(terminal_counts\\)="):
        assert_lifecycle_invariant_at_batch_close(state)


def test_invariant_holds_on_empty_batch(batch_id):
    state = BatchIngestState(batch_id=batch_id)
    assert_lifecycle_invariant_at_batch_close(state)  # 0 == 0


def test_d6_stage1_lifecycle_states_is_closed_set():
    """The Stage 1 lifecycle set is exactly the five expected values."""
    assert set(D6_STAGE1_LIFECYCLE_STATES) == {
        INVALID_DSL, REJECTED_COMPLEXITY, DUPLICATE, PENDING_BACKTEST,
        BACKEND_EMPTY_OUTPUT,
    }


# ---------------------------------------------------------------------------
# Empty ProposerOutput accounting (Issue 1)
# ---------------------------------------------------------------------------


def test_empty_proposer_output_counts_as_one_attempt(batch_id):
    """A Sonnet call yielding zero candidates is not a free retry."""
    state = BatchIngestState(batch_id=batch_id)
    empty_output = ProposerOutput(candidates=())
    records = ingest_output(state, empty_output)
    assert state.hypotheses_attempted == 1
    assert len(records) == 1
    assert records[0].lifecycle_state == BACKEND_EMPTY_OUTPUT
    assert state.lifecycle_counts[BACKEND_EMPTY_OUTPUT] == 1
    assert records[0].error_kind == "empty_output"
    assert_lifecycle_invariant_at_batch_close(state)


# ---------------------------------------------------------------------------
# Contract: orchestrator must not import anthropic
# ---------------------------------------------------------------------------


def test_orchestrator_package_never_imports_anthropic():
    """Mechanical grep — reviewed by humans but enforced in CI."""
    root = Path(__file__).resolve().parent.parent / "agents" / "orchestrator"
    assert root.is_dir()
    result = subprocess.run(
        ["grep", "-rIn", "-e", "import anthropic", "-e", "from anthropic",
         str(root)],
        capture_output=True,
        text=True,
    )
    # grep returns 1 with empty stdout when no match; that's what we want.
    assert result.stdout == "", (
        f"orchestrator package imports anthropic:\n{result.stdout}"
    )
