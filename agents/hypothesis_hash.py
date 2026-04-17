"""D3 — Hypothesis hash and dedup canonicalization.

Produces a deterministic hash for any :class:`strategies.dsl.StrategyDSL`
that is **semantic-equivalence-aware**: two DSLs expressing the same
trading logic produce the same hash even if conditions are reordered,
floats use different representations, or cosmetic fields (``name``,
``description``) differ.

Canonical form rules (from PHASE2_BLUEPRINT D3):
    1. Conditions sorted within each ConditionGroup (AND commutativity).
    2. ConditionGroups sorted within entry/exit (OR commutativity).
    3. All floats formatted as ``f"{value:.6f}"`` strings (deterministic
       across Python versions for IEEE 754 doubles at 6 decimal places).
    4. ``name`` and ``description`` excluded (cosmetic only).
    5. ``max_hold_bars`` included.
    6. Hash = SHA256 of canonical JSON, first 16 hex chars.

This module is deliberately separate from D2's
:func:`strategies.dsl.canonicalize_dsl`, which is a byte-stable
serialization used for compilation manifest integrity. D2's form
preserves field ordering, includes ``name``/``description``, and uses
default float repr. Changing D2's form would break existing manifest
drift detection; changing D3's form would break dedup. They serve
opposite purposes and must not be merged.
"""

from __future__ import annotations

import hashlib
import json

from strategies.dsl import StrategyDSL


# ---------------------------------------------------------------------------
# Canonical condition / group representations
# ---------------------------------------------------------------------------


def _canonical_value(v: float | str) -> str:
    """Format a condition value for canonical JSON.

    Floats are formatted to 6 decimal places (``f"{v:.6f}"``).
    Strings (factor names) are passed through unchanged.
    """
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f"{float(v):.6f}"
    return str(v)


def _canonical_condition(factor: str, op: str, value: float | str) -> dict:
    """Build a canonical dict for one condition."""
    return {"factor": factor, "op": op, "value": _canonical_value(value)}


def _canonical_condition_sort_key(cond_dict: dict) -> tuple:
    """Sort key for a single canonical condition."""
    return (cond_dict["factor"], cond_dict["op"], cond_dict["value"])


def _canonical_group(conditions: list[dict]) -> list[dict]:
    """Sort conditions within a group by (factor, op, value)."""
    return sorted(conditions, key=_canonical_condition_sort_key)


def _canonical_group_sort_key(group: list[dict]) -> str:
    """Sort key for a group: its compact JSON form after internal sort."""
    return json.dumps(group, sort_keys=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def canonicalize_for_hash(dsl: StrategyDSL) -> str:
    """Deterministic JSON serialization for dedup hashing.

    Produces a canonical string where:
    - AND-conditions within each group are sorted alphabetically.
    - OR-groups within entry/exit are sorted lexicographically.
    - All float values use ``f"{v:.6f}"`` formatting.
    - ``name`` and ``description`` are excluded.
    - ``max_hold_bars`` and ``position_sizing`` are included.

    The output is suitable for SHA256 hashing. It is NOT suitable for
    compilation manifest storage (use D2's ``canonicalize_dsl`` for that).

    Args:
        dsl: A validated StrategyDSL instance.

    Returns:
        Compact JSON string with sorted keys and no whitespace variance.
    """
    def canonicalize_groups(groups):
        result = []
        for g in groups:
            conds = [
                _canonical_condition(c.factor, c.op, c.value)
                for c in g.conditions
            ]
            result.append(_canonical_group(conds))
        result.sort(key=_canonical_group_sort_key)
        return result

    payload = {
        "entry": canonicalize_groups(dsl.entry),
        "exit": canonicalize_groups(dsl.exit),
        "max_hold_bars": dsl.max_hold_bars,
        "position_sizing": dsl.position_sizing,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def hash_dsl(dsl: StrategyDSL) -> str:
    """Compute the D3 hypothesis hash for dedup.

    Returns the first 16 hex characters of the SHA256 digest of
    :func:`canonicalize_for_hash`. This is the dedup key used by the
    orchestrator to detect duplicate hypotheses within a batch.

    Args:
        dsl: A validated StrategyDSL instance.

    Returns:
        16-character lowercase hex string.
    """
    canonical = canonicalize_for_hash(dsl)
    full_hex = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return full_hex[:16]


def are_equivalent(dsl_a: StrategyDSL, dsl_b: StrategyDSL) -> bool:
    """Check if two DSLs represent the same trading strategy.

    Two DSLs are equivalent iff they produce the same D3 hash, meaning
    they differ only in condition/group ordering, float representation,
    or cosmetic fields (name, description).

    Args:
        dsl_a: First DSL.
        dsl_b: Second DSL.

    Returns:
        True if the DSLs are semantically equivalent for dedup purposes.
    """
    return hash_dsl(dsl_a) == hash_dsl(dsl_b)


__all__ = [
    "canonicalize_for_hash",
    "hash_dsl",
    "are_equivalent",
]
