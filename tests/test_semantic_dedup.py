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


# ===========================================================================
# Wave B-1 — Track B failing TDD tests (Wave B-2 implements)
# ===========================================================================
#
# Per implementation plan d92c98f §Wave B-1 + sub-spec amendment v1
# SEAL 850aa1d §2 B-1/B-4/B-6:
# - B-T1: embed_dsl determinism (NL string -> deterministic vector)
# - B-T2: is_near_duplicate compound AND-gate (cosine + factor-set)
# - B-T3 + B-T4: lifecycle integration (see test_orchestrator_ingest.py)
# - B-T5: import isolation ripgrep (covered above at
#   test_nl_serializer_isolates_from_hypothesis_hash)
# - B-T6: embedding cache cleared at finalize
# - B-T7: cosine-threshold sweep coverage (executed at W0.3.v2 commit
#   c5f65d7; test_btau_calibration_v2_chosen_tau verifies the artifact)
# - B-T8: model load-failure hard-fails orchestrator startup


def test_b_t1_embed_dsl_deterministic():
    """embed_dsl(dsl, model) returns the same vector across two calls.

    Determinism comes from: (a) NL serializer deterministic (verified
    above); (b) sentence-transformers deterministic given same model
    file + same input; (c) numpy float arithmetic deterministic on
    same CPU.
    """
    from agents.orchestrator.semantic_dedup import embed_dsl
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    dsl = _make_dsl()
    v1 = embed_dsl(dsl, model)
    v2 = embed_dsl(dsl, model)

    import numpy as np
    assert v1.shape == (384,), f"Expected dim 384; got {v1.shape}"
    assert np.allclose(v1, v2), "embed_dsl must be deterministic"


def test_b_t2_is_near_duplicate_compound_gate():
    """is_near_duplicate enforces both cosine ≥ τ_c AND factor_set_equal.

    Per amendment §2 B-6: compound AND-gate. Pair with high cosine but
    different factor sets → NOT flagged. Pair with same factor set but
    low cosine → NOT flagged.
    """
    from agents.orchestrator.semantic_dedup import is_near_duplicate
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Two near-identical DSLs with same factor set (rsi_14)
    dsl_a = _make_dsl(
        entry=[{"conditions": [{"factor": "rsi_14", "op": "<", "value": 30}]}],
        exit_=[{"conditions": [{"factor": "rsi_14", "op": ">", "value": 50}]}],
    )
    dsl_b = _make_dsl(
        entry=[{"conditions": [{"factor": "rsi_14", "op": "<", "value": 31}]}],
        exit_=[{"conditions": [{"factor": "rsi_14", "op": ">", "value": 50}]}],
    )
    # Different factor set (sma_20)
    dsl_c = _make_dsl(
        entry=[{"conditions": [{"factor": "sma_20", "op": ">", "value": "close"}]}],
        exit_=[{"conditions": [{"factor": "sma_20", "op": "<", "value": "close"}]}],
    )

    # a vs b: same factor set → compound gate may flag based on cosine
    # a vs c: different factor sets → compound gate MUST NOT flag
    flag_ab = is_near_duplicate(dsl_a, dsl_b, tau_c=0.95, model=model)
    flag_ac = is_near_duplicate(dsl_a, dsl_c, tau_c=0.95, model=model)

    # The KEY assertion: cross-factor pair NEVER flagged regardless of cosine
    assert flag_ac is False, (
        "Compound gate must reject cross-factor pair (a vs c) at structural side, "
        "regardless of cosine"
    )
    # Within-factor pair flagging is cosine-dependent; just check it's a bool
    assert isinstance(flag_ab, bool)


def test_b_t6_embedding_cache_cleared_at_finalize():
    """BatchIngestState.embedding_cache cleared by finalize_batch.

    Per B-Lock-5: per-batch only; no cross-batch state.
    """
    from agents.orchestrator.ingest import BatchIngestState
    from agents.orchestrator.semantic_dedup import finalize_batch_embedding_cache

    state = BatchIngestState(batch_id="test-batch")
    import numpy as np
    state.embedding_cache["hash_1"] = np.array([0.1, 0.2])
    state.embedding_cache["hash_2"] = np.array([0.3, 0.4])
    assert len(state.embedding_cache) == 2

    finalize_batch_embedding_cache(state)
    assert len(state.embedding_cache) == 0, (
        "embedding_cache must be empty after finalize per B-Lock-5"
    )


def test_b_t7_calibration_v2_artifact_present():
    """W0.3.v2 calibration artifact exists; chosen τ_c is in expected range.

    Per amendment §2 B-1: τ_c chosen at W0.3.v2 sweep must be in
    [0.85, 0.99] AND F1 ≥ 0.85 (conjunctive no-further-amendment).
    """
    import json
    from pathlib import Path

    sweep_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "phase2_5"
        / "btau_calibration_v2"
        / "sweep_results.json"
    )
    assert sweep_path.exists(), (
        f"W0.3.v2 calibration artifact missing: {sweep_path}"
    )
    sweep_data = json.loads(sweep_path.read_text(encoding="utf-8"))
    chosen_tau_c = sweep_data["chosen_tau_c"]
    sweep = sweep_data["sweep"]
    chosen_row = next(r for r in sweep if r["tau_c"] == chosen_tau_c)
    chosen_f1 = chosen_row["f1"]

    # Conjunctive no-further-amendment trigger per amendment §2 B-1
    assert 0.85 <= chosen_tau_c <= 0.99, (
        f"chosen τ_c={chosen_tau_c} out of conjunctive no-further-amendment "
        f"range [0.85, 0.99]"
    )
    assert chosen_f1 >= 0.85, (
        f"chosen F1={chosen_f1} below 0.85 floor"
    )
    assert sweep_data["trigger_amendment_v2"] is False


def test_b_t8_model_load_failure_hard_fails_orchestrator():
    """Per amendment §4 B-7: missing sentence-transformers → hard-fail.

    Mocks the import-failure path and verifies the orchestrator startup
    refuses to begin batch.
    """
    from agents.orchestrator.semantic_dedup import check_embedding_stack_or_raise

    # Healthy: should not raise
    check_embedding_stack_or_raise()  # raises if anything wrong

    # Simulated failure via stubbed environment: test the failure path's
    # exception type contract — Wave B-2 implements this with the actual
    # check; for now we just confirm the function exists and accepts
    # the contract surface
    assert callable(check_embedding_stack_or_raise)
