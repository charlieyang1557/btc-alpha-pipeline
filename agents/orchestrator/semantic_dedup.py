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


__all__ = ["nl_serialize_dsl"]
