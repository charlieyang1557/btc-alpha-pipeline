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
       across Python versions for IEEE 754 doubles at 6 decimal places)
       and tagged with a ``"num:"`` prefix. Factor-name RHS values are
       tagged with ``"fac:"``. The prefix prevents a scalar from
       colliding with a factor literally named e.g. ``"30.000000"``.
    4. ``name`` and ``description`` excluded (cosmetic only).
    5. ``max_hold_bars`` included.
    6. ``position_sizing`` included (see CONTRACT GAP below).
    7. Hash = first 16 hex chars of SHA256 of the canonical JSON.

CONTRACT BOUNDARY: this module is deliberately separate from D2's
:func:`strategies.dsl.canonicalize_dsl`, which is a byte-stable
serialization used for compilation-manifest integrity. D2's form
preserves field ordering, includes ``name``/``description``, and uses
default float repr. Changing D2's form would break existing manifest
drift detection; changing D3's form would break dedup. They serve
opposite purposes and MUST NOT be merged. Any refactor that creates a
shared ``_stable_json`` helper between D2 and D3 is rejected by default
— the independence is the feature, not a redundancy.

D3 trusts the D2 schema to enforce several preconditions that keep its
canonicalization simple:
    - No NaN/Inf scalar thresholds (D2 rejects at schema time via
      ``Condition._validate_value``), so ``f"{v:.6f}"`` is always a
      distinct 6-decimal numeric string.
    - No duplicate ``(factor, op, value)`` conditions within a group
      (D2 rejects at schema time via
      ``ConditionGroup._reject_duplicate_conditions``), so sorting
      conditions never produces ``[A, A, B]`` vs ``[A, B]`` hash drift.
If either precondition is weakened in D2, this file must be revisited.
"""

from __future__ import annotations

import hashlib
import json

from strategies.dsl import StrategyDSL


# ---------------------------------------------------------------------------
# Canonical condition / group representations
# ---------------------------------------------------------------------------


def _canonical_value(v: int | float | str) -> str:
    """Format a condition value for canonical JSON, tagged by type.

    Scalars are emitted as ``"num:<6-decimal>"`` and factor names as
    ``"fac:<name>"``. The type prefix disambiguates the two so a scalar
    ``30.0`` can never collide with a factor literally named
    ``"30.000000"`` (hypothetical today since the registry does not
    register numeric-looking names, but prevents future ambiguity).
    """
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f"num:{float(v):.6f}"
    return f"fac:{v}"


def _canonical_condition(
    factor: str, op: str, value: int | float | str
) -> dict:
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

    Contract — fields INCLUDED in the canonical payload:
        - ``entry``: list of groups, each a sorted list of tagged
          ``{factor, op, value}`` dicts (AND-commutativity). Groups
          themselves sorted by compact-JSON (OR-commutativity).
        - ``exit``: same shape as ``entry``.
        - ``max_hold_bars``: included verbatim (None or 1..720).
        - ``position_sizing``: included verbatim. CONTRACT GAP:
          currently always ``"full_equity"`` per D2's ``Literal``
          restriction, so it contributes zero entropy today. It is
          nevertheless included so that D4+, when sizing widens, does
          not require a dedup-hash schema bump. A strategy that differs
          only in sizing will then hash distinctly. The mirror-side
          marker lives in ``strategies/dsl.py`` on the ``position_sizing``
          field; keep them in sync.

    Contract — fields EXCLUDED from the canonical payload:
        - ``name``: cosmetic label. Two DSLs differing only in name
          are treated as duplicates for dedup purposes.
        - ``description``: cosmetic rationale. Same rationale as name.

    CONTRACT BOUNDARY: the output is suitable for SHA256 hashing via
    :func:`hash_dsl` and for semantic-equivalence comparison via
    :func:`are_equivalent`. It is NOT suitable for compilation-manifest
    storage — D2's :func:`strategies.dsl.canonicalize_dsl` is the
    byte-stable form for that purpose, and the two MUST remain separate
    (see module docstring above).

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

    Contract: exactly **16 lowercase hex characters**, equal to the
    first 16 characters of ``sha256(canonical_json)`` where
    ``canonical_json`` is the UTF-8 encoding of
    :func:`canonicalize_for_hash` output. This format is the dedup key
    used by the orchestrator (D8) to detect duplicate hypotheses within
    a batch and is written verbatim into the ``hypothesis_hash`` column
    of ``batch_summary``. Do not truncate or encode differently.

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
