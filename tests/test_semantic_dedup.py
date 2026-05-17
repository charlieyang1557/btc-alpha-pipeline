"""Wave 0 W0.3.v2 (a) — NL serializer tests for Phase 2.5 Track B.

Per sub-spec amendment v1 SEAL `850aa1d` §2 B-4 contract:
- nl_serialize_dsl(dsl: StrategyDSL) -> str
- Operator mapping: 7-row pure function of OpLiteral
- Deterministic (same DSL → same string)
- Isolated from agents.hypothesis_hash per B-Lock-2 extended NL-serializer
  sibling clause

Test surface enumerated per amendment §2 B-4 (Session 3 expanded per
architect F7):
- test_nl_serializer_deterministic
- test_nl_serializer_isolates_from_hypothesis_hash
- test_nl_serializer_edge_cases_parametrized (7 sub-cases)
"""
from __future__ import annotations

from pathlib import Path

import pytest

from strategies.dsl import StrategyDSL


def _make_dsl(
    *,
    name: str = "test_strategy",
    description: str = "test description",
    entry=None,
    exit_=None,
    max_hold_bars: int | None = None,
    position_sizing: str = "full_equity",
) -> StrategyDSL:
    """Build a StrategyDSL with sensible defaults for testing.

    Mirrors tests/test_hypothesis_hash.py::_make_dsl helper pattern.
    """
    if entry is None:
        entry = [
            {"conditions": [
                {"factor": "sma_20", "op": ">", "value": "sma_50"},
            ]}
        ]
    if exit_ is None:
        exit_ = [
            {"conditions": [
                {"factor": "sma_20", "op": "<", "value": "sma_50"},
            ]}
        ]
    return StrategyDSL.model_validate({
        "name": name,
        "description": description,
        "entry": entry,
        "exit": exit_,
        "position_sizing": position_sizing,
        "max_hold_bars": max_hold_bars,
    })


def test_nl_serializer_deterministic():
    """Same StrategyDSL → same NL string across two calls.

    Per amendment §2 B-4 contract: deterministic serialization.
    """
    from agents.orchestrator.semantic_dedup import nl_serialize_dsl

    dsl = _make_dsl()
    s1 = nl_serialize_dsl(dsl)
    s2 = nl_serialize_dsl(dsl)
    assert s1 == s2
    assert isinstance(s1, str)
    assert len(s1) > 0


def test_nl_serializer_isolates_from_hypothesis_hash():
    """semantic_dedup.py source MUST NOT import from agents.hypothesis_hash.

    Per amendment §4 B-Lock-2 extended NL-serializer call-graph rule:
    no shared serializer helper between hypothesis_hash.py and
    semantic_dedup.py; semantic_dedup must traverse StrategyDSL directly.
    """
    semantic_dedup_path = (
        Path(__file__).resolve().parent.parent
        / "agents"
        / "orchestrator"
        / "semantic_dedup.py"
    )
    source = semantic_dedup_path.read_text(encoding="utf-8")
    forbidden_imports = (
        "from agents.hypothesis_hash",
        "from agents import hypothesis_hash",
        "import agents.hypothesis_hash",
    )
    for forbidden in forbidden_imports:
        assert forbidden not in source, (
            f"semantic_dedup.py contains forbidden import {forbidden!r}; "
            f"per B-Lock-2 NL-serializer sibling clause, NL serializer must "
            f"traverse StrategyDSL directly without importing from "
            f"hypothesis_hash module."
        )


# ---------------------------------------------------------------------------
# Edge-case parametrized tests (7 cases per amendment §2 B-4 test surface)
# ---------------------------------------------------------------------------


@pytest.fixture
def serialize():
    """Import-shielded fixture for nl_serialize_dsl."""
    from agents.orchestrator.semantic_dedup import nl_serialize_dsl
    return nl_serialize_dsl


def test_nl_serializer_edge_case_a_multi_param_factor(serialize):
    """Edge case (a): multi-parameter factor names like bb_upper_24_2 render verbatim."""
    dsl = _make_dsl(
        entry=[{"conditions": [{"factor": "bb_upper_24_2", "op": ">", "value": "close"}]}],
        exit_=[{"conditions": [{"factor": "bb_upper_24_2", "op": "<", "value": "close"}]}],
    )
    nl = serialize(dsl)
    assert "bb_upper_24_2" in nl, (
        f"NL output must contain factor name 'bb_upper_24_2' verbatim. Got: {nl!r}"
    )


def test_nl_serializer_edge_case_b_max_hold_bars_none(serialize):
    """Edge case (b1): max_hold_bars=None renders as 'no max-hold'."""
    dsl = _make_dsl(max_hold_bars=None)
    nl = serialize(dsl)
    assert "no max-hold" in nl, (
        f"max_hold_bars=None must render as 'no max-hold'. Got: {nl!r}"
    )


def test_nl_serializer_edge_case_b_max_hold_bars_finite(serialize):
    """Edge case (b2): max_hold_bars=10 renders as 'max-hold 10 bars'."""
    dsl = _make_dsl(max_hold_bars=10)
    nl = serialize(dsl)
    assert "max-hold 10 bars" in nl, (
        f"max_hold_bars=10 must render as 'max-hold 10 bars'. Got: {nl!r}"
    )


def test_nl_serializer_edge_case_c_position_sizing(serialize):
    """Edge case (c): position_sizing renders verbatim."""
    dsl = _make_dsl()
    nl = serialize(dsl)
    assert "position-size full_equity" in nl, (
        f"position_sizing must render as 'position-size full_equity'. Got: {nl!r}"
    )


def test_nl_serializer_edge_case_d_crosses_above_numeric_rhs(serialize):
    """Edge case (d): crosses_above with numeric RHS (schema-valid but odd).

    Per amendment §2 B-4: operator mapping is pure function of OpLiteral;
    'crosses_above' renders as 'crosses above' regardless of RHS type
    (numeric or factor name).
    """
    dsl = _make_dsl(
        entry=[{"conditions": [{"factor": "sma_20", "op": "crosses_above", "value": 100.0}]}],
    )
    nl = serialize(dsl)
    assert "crosses above" in nl, (
        f"op='crosses_above' must render as 'crosses above'. Got: {nl!r}"
    )
    assert "100" in nl, (
        f"numeric RHS 100.0 must appear in output. Got: {nl!r}"
    )


def test_nl_serializer_edge_case_e_multiple_or_groups(serialize):
    """Edge case (e): entry with 2 OR-connected groups renders with 'or' separator."""
    dsl = _make_dsl(
        entry=[
            {"conditions": [{"factor": "sma_20", "op": ">", "value": "sma_50"}]},
            {"conditions": [{"factor": "rsi_14", "op": "<", "value": 30.0}]},
        ],
    )
    nl = serialize(dsl)
    # Should contain both groups; OR connection should be visible
    assert "sma_20" in nl and "rsi_14" in nl, (
        f"Both OR-connected factors must appear. Got: {nl!r}"
    )
    assert ";" in nl, (
        f"OR groups must be separated by ';'. Got: {nl!r}"
    )


def test_nl_serializer_edge_case_f_and_conjunction_within_group(serialize):
    """Edge case (f): AND-conjunction within a group renders with 'and' separator."""
    dsl = _make_dsl(
        entry=[
            {"conditions": [
                {"factor": "sma_20", "op": ">", "value": "sma_50"},
                {"factor": "rsi_14", "op": "<", "value": 30.0},
            ]},
        ],
    )
    nl = serialize(dsl)
    assert "and" in nl.lower(), (
        f"AND-conjunction must include 'and' separator. Got: {nl!r}"
    )


def test_nl_serializer_edge_case_g_operator_mapping_pure(serialize):
    """Edge case (g): each operator maps to its declared phrase regardless of RHS type.

    Per amendment §2 B-4 (Session 3 architect F2 correctness fix):
    operator mapping is one row per OpLiteral; factor-vs-scalar
    distinction lives in RHS rendering, NOT in operator.
    """
    expected_mappings = {
        ">": "is greater than",
        ">=": "is at least",
        "<": "is less than",
        "<=": "is at most",
        "==": "equals",
        "crosses_above": "crosses above",
        "crosses_below": "crosses below",
    }
    for op, phrase in expected_mappings.items():
        # Test with numeric RHS (factor-vs-scalar)
        dsl = _make_dsl(
            entry=[{"conditions": [{"factor": "sma_20", "op": op, "value": 50.0}]}],
        )
        nl = serialize(dsl)
        assert phrase in nl, (
            f"op={op!r} with numeric RHS must render as {phrase!r}. Got: {nl!r}"
        )
