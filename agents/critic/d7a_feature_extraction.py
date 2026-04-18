"""D7a feature extraction — primitives for parsing DSL structure.

Separated from ``d7a_rules.py`` so the acceptance notebook can audit
feature extraction independently from rule formulas. If feature
extraction is wrong, every rule is wrong downstream, even if the rule
formulas match the spec bit-for-bit. Treat this separation as a
correctness contract, not a style preference.
"""

from __future__ import annotations

from strategies.dsl import StrategyDSL


def extract_factors(dsl: StrategyDSL) -> list[str]:
    """Return sorted list of distinct factor names referenced in the DSL.

    Scans both entry and exit condition groups. Factors appearing as
    ``condition.factor`` (LHS) or as a string ``condition.value`` (RHS,
    factor-vs-factor) are both included. Returns a sorted list for
    determinism.
    """
    factors: set[str] = set()
    for group in list(dsl.entry) + list(dsl.exit):
        for cond in group.conditions:
            factors.add(cond.factor)
            if isinstance(cond.value, str):
                factors.add(cond.value)
    return sorted(factors)


def count_conditions(dsl: StrategyDSL) -> int:
    """Count total conditions across all entry and exit groups."""
    total = 0
    for group in list(dsl.entry) + list(dsl.exit):
        total += len(group.conditions)
    return total


def count_entry_groups(dsl: StrategyDSL) -> int:
    """Count entry condition groups (OR-connected)."""
    return len(dsl.entry)


def count_exit_groups(dsl: StrategyDSL) -> int:
    """Count exit condition groups (OR-connected)."""
    return len(dsl.exit)


def get_description_length(dsl: StrategyDSL) -> int:
    """Return the length of the DSL description string."""
    return len(dsl.description)


def get_max_hold_bars(dsl: StrategyDSL) -> int | None:
    """Return max_hold_bars from the DSL (may be None)."""
    return dsl.max_hold_bars


def factor_set_tuple(dsl: StrategyDSL) -> tuple[str, ...]:
    """Return the canonical sorted factor-set tuple for dedup/saturation.

    Empty tuple for DSLs with no factors (degenerate case).
    """
    return tuple(extract_factors(dsl))


__all__ = [
    "count_conditions",
    "count_entry_groups",
    "count_exit_groups",
    "extract_factors",
    "factor_set_tuple",
    "get_description_length",
    "get_max_hold_bars",
]
