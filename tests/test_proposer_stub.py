"""D6 Stage 1 — deterministic stub backend covers all seven categories.

Each of the seven Stage 1 acceptance scenarios must produce the exact
Valid/Invalid split expected by the lifecycle ingest logic, and two
calls with the same scenario must be byte-identical (the foundation of
duplicate detection).
"""

from __future__ import annotations

import pytest

from agents.proposer import BatchContext, ValidCandidate, InvalidCandidate
from agents.proposer.stub_backend import (
    DEFAULT_SCENARIO_SEQUENCE,
    StubProposerBackend,
    _SCENARIO_TO_RAW,
    _VALID_DSL_JSON,
    _strip_markdown_fence,
    classify_raw_json,
)
from factors.registry import get_registry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def registry():
    return get_registry()


@pytest.fixture
def backend(registry):
    return StubProposerBackend(registry=registry)


def _ctx(position: int, batch_size: int, registry) -> BatchContext:
    return BatchContext(
        batch_id="stub-batch",
        position=position,
        batch_size=batch_size,
        allowed_factors=tuple(registry.list_names()),
        allowed_operators=(
            "<", "<=", ">", ">=", "==", "crosses_above", "crosses_below",
        ),
        theme_slot=(position - 1) % 6,
    )


# ---------------------------------------------------------------------------
# Scenario → Valid/Invalid classification
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "scenario,expected_cls",
    [
        ("valid", ValidCandidate),
        ("invalid_json", InvalidCandidate),
        ("duplicate_of_valid", ValidCandidate),  # semantically valid
        ("over_complex", InvalidCandidate),
        ("factor_out_of_registry", InvalidCandidate),
        ("grammar_violation", InvalidCandidate),
        ("non_finite_threshold", InvalidCandidate),
    ],
)
def test_each_scenario_maps_to_expected_candidate_class(
    scenario, expected_cls, registry
):
    raw = _SCENARIO_TO_RAW[scenario]
    cand = classify_raw_json(
        raw, registry=registry, error_kind_hint=scenario
    )
    assert isinstance(cand, expected_cls), (
        f"scenario {scenario} -> {type(cand).__name__}, "
        f"expected {expected_cls.__name__}"
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_valid_and_duplicate_of_valid_emit_identical_raw_json():
    """Duplicate detection depends on byte-identical raw JSON across calls."""
    assert _SCENARIO_TO_RAW["valid"] == _SCENARIO_TO_RAW["duplicate_of_valid"]
    assert _SCENARIO_TO_RAW["valid"] == _VALID_DSL_JSON


def test_two_backends_with_same_sequence_produce_byte_identical_outputs(
    registry,
):
    b1 = StubProposerBackend(registry=registry)
    b2 = StubProposerBackend(registry=registry)
    for k in range(1, len(DEFAULT_SCENARIO_SEQUENCE) + 1):
        ctx = _ctx(k, len(DEFAULT_SCENARIO_SEQUENCE), registry)
        o1 = b1.generate(ctx)
        o2 = b2.generate(ctx)
        assert len(o1.candidates) == 1 and len(o2.candidates) == 1
        c1, c2 = o1.candidates[0], o2.candidates[0]
        if isinstance(c1, InvalidCandidate):
            assert isinstance(c2, InvalidCandidate)
            assert c1.raw_json == c2.raw_json
        else:
            assert isinstance(c1, ValidCandidate) and isinstance(c2, ValidCandidate)
            # DSLs compare by canonicalization downstream; model_dump
            # gives us a simple equality check here.
            assert c1.dsl.model_dump() == c2.dsl.model_dump()


# ---------------------------------------------------------------------------
# Cycle / wrap-around
# ---------------------------------------------------------------------------


def test_scenario_sequence_wraps_around(backend, registry):
    """position 8 == position 1 scenario (seven-scenario cycle)."""
    o1 = backend.generate(_ctx(1, 14, registry))
    o8 = backend.generate(_ctx(8, 14, registry))
    assert o1.telemetry["scenario"] == o8.telemetry["scenario"] == "valid"


def test_unknown_scenario_rejected_at_construction(registry):
    with pytest.raises(ValueError, match="unknown scenarios"):
        StubProposerBackend(
            scenario_sequence=("valid", "not_a_real_scenario"),
            registry=registry,
        )


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


def test_provenance_includes_scenario_and_position(backend, registry):
    out = backend.generate(_ctx(1, 7, registry))
    cand = out.candidates[0]
    prov = cand.provenance
    assert prov["backend"] == "stub"
    assert prov["scenario"] == "valid"
    assert prov["position"] == 1
    assert prov["batch_id"] == "stub-batch"


def test_cost_telemetry_defaults_to_zero(backend, registry):
    out = backend.generate(_ctx(1, 7, registry))
    assert out.cost_estimate_usd == 0.0
    assert out.cost_actual_usd == 0.0
    assert out.backend_name == "stub"


def test_cost_per_call_propagates_to_output(registry):
    backend = StubProposerBackend(
        registry=registry, cost_per_call_usd=0.02,
    )
    out = backend.generate(_ctx(1, 7, registry))
    assert out.cost_estimate_usd == 0.02
    assert out.cost_actual_usd == 0.02


# ---------------------------------------------------------------------------
# Stage 2a calibration patch — markdown code-fence stripper
# ---------------------------------------------------------------------------
#
# Stage 2a revealed that Sonnet wraps JSON in ```json ... ``` fences. The
# parser strips the fence in memory before ``json.loads``; disk payloads
# and ``InvalidCandidate.raw_json`` retain the original fenced text for
# forensic integrity.


_INNER_JSON = _VALID_DSL_JSON  # already a compact JSON string


@pytest.mark.parametrize(
    "raw,expected",
    [
        # Sonnet's exact Stage 2a format
        (
            f"```json\n{_INNER_JSON}\n```",
            _INNER_JSON,
        ),
        # Fence with no language tag
        (
            f"```\n{_INNER_JSON}\n```",
            _INNER_JSON,
        ),
        # Whitespace before "json" tag
        (
            f"```  json\n{_INNER_JSON}\n```",
            _INNER_JSON,
        ),
        # Leading prose before the fence
        (
            f"Here is the JSON:\n\n```json\n{_INNER_JSON}\n```",
            _INNER_JSON,
        ),
        # Trailing prose after the fence
        (
            f"```json\n{_INNER_JSON}\n```\n\nLet me know if you need anything.",
            _INNER_JSON,
        ),
        # No fence: passthrough unchanged
        (_INNER_JSON, _INNER_JSON),
        # Uppercase language tag (case-insensitive)
        (
            f"```JSON\n{_INNER_JSON}\n```",
            _INNER_JSON,
        ),
    ],
)
def test_strip_markdown_fence_variants(raw, expected):
    assert _strip_markdown_fence(raw) == expected


def test_classify_raw_json_accepts_fenced_sonnet_output(registry):
    """A fenced but otherwise valid Sonnet response must become ValidCandidate."""
    fenced = f"```json\n{_INNER_JSON}\n```"
    cand = classify_raw_json(fenced, registry=registry)
    assert isinstance(cand, ValidCandidate)


def test_invalid_candidate_preserves_original_raw_json_including_fence(
    registry,
):
    """Forensic integrity: InvalidCandidate.raw_json must be byte-identical
    to the original input, fences included. Only json.loads sees the
    stripped form."""
    # Fenced but malformed inside (trailing comma + missing brace)
    bad_inner = (
        '{"name":"bad","description":"trailing comma",'
        '"entry":[{"conditions":[{"factor":"return_24h","op":">","value":0.02,}]}'
    )
    fenced = f"```json\n{bad_inner}\n```"
    cand = classify_raw_json(fenced, registry=registry)
    assert isinstance(cand, InvalidCandidate)
    assert cand.raw_json == fenced, (
        "InvalidCandidate.raw_json must retain the fence for forensic replay"
    )


def test_disk_file_bytes_unchanged_after_classification(tmp_path, registry):
    """Disk integrity: classify_raw_json must not rewrite the raw-payload
    file; the stripper operates only on its in-memory return value."""
    fenced = f"```json\n{_INNER_JSON}\n```"
    response_file = tmp_path / "attempt_0001_response.txt"
    response_file.write_text(fenced, encoding="utf-8")
    original_bytes = response_file.read_bytes()

    # Run the classifier on the same string the file was written with.
    cand = classify_raw_json(fenced, registry=registry)
    assert isinstance(cand, ValidCandidate)

    # Disk file must be byte-for-byte unchanged.
    assert response_file.read_bytes() == original_bytes
