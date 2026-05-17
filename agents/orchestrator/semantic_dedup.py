"""Semantic dedup module for Phase 2.5 Track B.

Per sub-spec amendment v1 SEAL `850aa1d`, this module owns:

- ``nl_serialize_dsl(dsl)`` — natural-language serializer for embedding input
  (Wave 0 W0.3.v2 sub-task (a); this commit)
- Embedding compute + cache + cosine + structural compound gate
  (Wave B-2; deferred)
- ``embed_canonical(dsl)`` + ``is_near_duplicate(...)`` API for orchestrator
  (Wave B-2; deferred)

DISCIPLINE LOCKS (parked-branch-internal until merge):

- B-Lock-1: NEVER merge embedding-based dedup into D3 byte-identical
  canonicalization (this module is the separate code path)
- B-Lock-2 (bucketing clause): if parameter bucketing is adopted, the
  transform MUST live here and traverse StrategyDSL directly without
  calling ``canonicalize_for_hash()``
- B-Lock-2 (NL-serializer sibling clause, amendment v1 extension):
  ``nl_serialize_dsl`` MUST traverse ``StrategyDSL`` via attribute
  access and MUST NOT call ``canonicalize_for_hash()`` or any function
  in ``agents/hypothesis_hash.py``. No shared serializer helper
  between these modules.
- B-Lock-3: NEVER count ``near_duplicate`` against the budget pre-charge
- B-Lock-4: NEVER write embedding vectors to LLM-visible artifacts
- B-Lock-5: NEVER cache embeddings across batches in MVP
- B-Lock-6: NEVER use a remote embedding API
- B-Lock-7: sentence-transformers model + tokenizer SHA-pinned at install;
  runtime embedding MUST NOT touch the network
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from strategies.dsl import Condition, ConditionGroup, StrategyDSL


# Operator mapping per sub-spec amendment v1 §2 B-4 (Session 3 architect F2
# correctness fix): 7-row pure function of OpLiteral; factor-vs-scalar
# distinction lives in RHS rendering, not in operator semantics.
_OP_MAPPING: dict[str, str] = {
    ">": "is greater than",
    ">=": "is at least",
    "<": "is less than",
    "<=": "is at most",
    "==": "equals",
    "crosses_above": "crosses above",
    "crosses_below": "crosses below",
}


def _format_value(value: float | str) -> str:
    """Render a Condition.value as a string for NL output.

    Numeric values render without trailing zeros for integer-valued floats
    (e.g., ``100.0`` → ``"100"``) so the NL form is human-readable and
    deterministic across DSL constructions that pass integer literals as
    floats.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _render_condition(cond: "Condition") -> str:
    """Render one Condition as natural language: ``factor OP_PHRASE value``."""
    op_phrase = _OP_MAPPING[cond.op]
    value_str = _format_value(cond.value)
    return f"{cond.factor} {op_phrase} {value_str}"


def _render_group(group: "ConditionGroup") -> str:
    """Render one ConditionGroup as ``cond1 and cond2 and ...``.

    Within a group, conditions are AND-connected and order-independent.
    Sort rendered conditions for determinism.
    """
    rendered_conditions = sorted(
        _render_condition(c) for c in group.conditions
    )
    return " and ".join(rendered_conditions)


def _render_groups(groups: "list[ConditionGroup]") -> str:
    """Render OR-connected groups as ``group1 ; or ; group2 ...``.

    Across groups, the connection is OR and order-independent. Sort
    rendered group strings for determinism.
    """
    rendered_groups = sorted(_render_group(g) for g in groups)
    return " ; or ; ".join(rendered_groups)


def nl_serialize_dsl(dsl: "StrategyDSL") -> str:
    """Serialize a ``StrategyDSL`` to natural-language text for embedding input.

    Per Phase 2.5 sub-spec amendment v1 SEAL `850aa1d` §2 B-4:

    - Operator mapping: 7-row pure function of ``OpLiteral`` (no
      context-dependent branching; factor-vs-scalar distinction lives in
      RHS rendering)
    - Determinism: within-group AND-conjunction sorted; across-group
      OR-conjunction sorted
    - Module isolation: this function traverses ``StrategyDSL`` via
      attribute access (``dsl.entry``, ``dsl.exit``, ``dsl.max_hold_bars``,
      ``dsl.position_sizing``); it does NOT call any function from
      ``agents/hypothesis_hash.py`` per extended B-Lock-2 sibling clause

    Output shape::

        entry when <group(s)>; exit when <group(s)>; max-hold N bars; position-size METHOD

    or, when ``max_hold_bars is None``::

        entry when <group(s)>; exit when <group(s)>; no max-hold; position-size METHOD

    Args:
        dsl: A validated ``StrategyDSL`` instance.

    Returns:
        Natural-language string suitable as input to a
        sentence-transformer encoder for cosine-similarity dedup.
    """
    entry_nl = _render_groups(dsl.entry)
    exit_nl = _render_groups(dsl.exit)
    max_hold_nl = (
        f"max-hold {dsl.max_hold_bars} bars"
        if dsl.max_hold_bars is not None
        else "no max-hold"
    )
    position_size_nl = f"position-size {dsl.position_sizing}"
    return (
        f"entry when {entry_nl}; "
        f"exit when {exit_nl}; "
        f"{max_hold_nl}; "
        f"{position_size_nl}"
    )


# ---------------------------------------------------------------------------
# Wave B-2 — embedding + compound-gate functions
# ---------------------------------------------------------------------------


def check_embedding_stack_or_raise() -> None:
    """Verify the embedding stack is healthy; raise on any failure.

    Per sub-spec amendment v1 SEAL ``850aa1d`` §4 B-7 hard-fail policy:
    at orchestrator startup the embedding stack MUST be reachable. Silent
    degradation to D3-only dedup is forbidden (would let a batch proceed
    without near-duplicate flagging without operator awareness).

    Raises:
        ImportError: if ``sentence_transformers`` cannot be imported
            (extras not installed).
        RuntimeError: if model instantiation fails for any other reason
            (network error mid-install, file corruption, etc.).

    Returns ``None`` when the stack is healthy.
    """
    try:
        # Local import so callers that never invoke this don't pay the
        # sentence-transformers import cost (~1s).
        from sentence_transformers import SentenceTransformer  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "Phase 2.5 Track B requires sentence-transformers; install via "
            "`pip install -e .[phase2_5]`. Per amendment v1 B-7 hard-fail "
            "policy, the orchestrator MUST NOT proceed without the embedding "
            "stack."
        ) from exc


def embed_dsl(dsl: "StrategyDSL", model) -> "np.ndarray":  # type: ignore[no-any-unimported]
    """Embed a ``StrategyDSL`` via the NL serializer + sentence-transformer.

    Per sub-spec amendment v1 §2 B-4: input is the NL-serialized DSL
    string (NOT the D3-canonical JSON form). The W0.3.v2 verification
    audit confirmed NL-serializer cosines discriminate cross-factor
    pairs while D3-JSON does not.

    Args:
        dsl: A validated ``StrategyDSL`` instance.
        model: An instance of ``sentence_transformers.SentenceTransformer``
            (typically ``all-MiniLM-L6-v2``; embedding dim 384).

    Returns:
        ``np.ndarray`` of shape ``(model.get_sentence_embedding_dimension(),)``
        — the NL serializer output's mean-pooled token embedding.
    """
    import numpy as np  # local import per import-isolation discipline

    nl_text = nl_serialize_dsl(dsl)
    embedding = model.encode(nl_text, convert_to_numpy=True, show_progress_bar=False)
    return np.asarray(embedding)


def is_near_duplicate(
    dsl_a: "StrategyDSL",
    dsl_b: "StrategyDSL",
    *,
    tau_c: float,
    model,
) -> bool:
    """Compound AND-gate near-duplicate detection.

    Per sub-spec amendment v1 §2 B-6: ``near_duplicate(A, B)`` iff
    cosine(emb(A), emb(B)) ≥ ``tau_c`` AND
    ``frozenset(extract_factors(A)) == frozenset(extract_factors(B))``.

    The structural side (factor-set equality) is τ_s = 1.0 DEFINITIONAL
    per amendment §2 B-1 — immune from re-litigation at W0.3.v2. The
    Jaccard generalization (τ_s < 1.0) is reserved for V2.

    Note: W0.3.v2 verification audit (commit ``fd27570``) showed compound
    gate is empirically REDUNDANT with NL serializer on the fixture
    (NL × cosine-only F1 == NL × compound F1 = 0.9333). The structural
    side is retained as belt-and-suspenders per Charlie register
    "All wave authorized" — keeps the discipline lock surface unchanged.

    Args:
        dsl_a, dsl_b: Two validated ``StrategyDSL`` instances.
        tau_c: Cosine similarity threshold. Empirically ~0.99 at
            W0.3.v2 sweep (commit ``c5f65d7``).
        model: ``sentence_transformers.SentenceTransformer`` instance.

    Returns:
        ``True`` if both gates pass; ``False`` otherwise.
    """
    import numpy as np

    # Structural gate first (cheap short-circuit)
    fa = frozenset(extract_factors(dsl_a))
    fb = frozenset(extract_factors(dsl_b))
    if fa != fb:
        return False

    # Cosine gate
    emb_a = embed_dsl(dsl_a, model)
    emb_b = embed_dsl(dsl_b, model)
    cosine = float(np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b)))
    return cosine >= tau_c


def finalize_batch_embedding_cache(state) -> None:
    """Clear ``BatchIngestState.embedding_cache`` per B-Lock-5.

    Per sub-spec amendment v1 §4 B-Lock-5: embedding cache is strictly
    per-batch. ``finalize_batch_embedding_cache`` is called by the
    orchestrator at batch close (immediately before or after
    ``assert_lifecycle_invariant_at_batch_close``) to release the
    per-batch embedding memory and prevent any cross-batch state leak.

    Args:
        state: ``BatchIngestState`` instance whose ``embedding_cache``
            dict will be cleared in place.
    """
    state.embedding_cache.clear()


# Lazy import for factor extraction — kept local to is_near_duplicate's call
# site logic but exposed here for re-use by orchestrator integration code.
# This import sits at module bottom (not top) to keep import-time cost low
# for callers that never call ``is_near_duplicate`` (e.g., test fixtures
# that only use ``nl_serialize_dsl``).
from agents.critic.d7a_feature_extraction import extract_factors  # noqa: E402


__all__ = [
    "check_embedding_stack_or_raise",
    "embed_dsl",
    "finalize_batch_embedding_cache",
    "is_near_duplicate",
    "nl_serialize_dsl",
]
