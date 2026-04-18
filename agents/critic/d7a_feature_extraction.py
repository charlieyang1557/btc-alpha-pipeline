"""D7a feature extraction — primitives for parsing DSL structure.

Separated from ``d7a_rules.py`` so the acceptance notebook can audit
feature extraction independently from rule formulas. If feature
extraction is wrong, every rule is wrong downstream, even if the rule
formulas match the spec bit-for-bit. Treat this separation as a
correctness contract, not a style preference.
"""

from __future__ import annotations

from strategies.dsl import StrategyDSL


# ---------------------------------------------------------------------------
# Canonical predicate: thin_theme_momentum_bleed
# ---------------------------------------------------------------------------
#
# CONTRACT BOUNDARY: This predicate defines the ONLY condition under which
# the ``thin_theme_momentum_bleed`` D7a flag fires. All other modules
# (``d7a_rules.py``, replay selection scripts, audit notebooks) MUST route
# through ``is_thin_theme_momentum_bleed`` rather than reimplementing the
# rule. Drift between two implementations of the same semantic is a
# correctness bug waiting to happen.

THIN_THEMES: frozenset[str] = frozenset({
    "volume_divergence",
    "calendar_effect",
    "volatility_regime",
})


def is_thin_theme_momentum_bleed(
    theme: str,
    n_default_momentum_factors_used: int,
) -> bool:
    """Return True iff the ``thin_theme_momentum_bleed`` flag fires.

    The flag fires when a DSL proposed under a thin theme (a theme with
    sparse native factor vocabulary) leans on two or more default
    momentum factors — a signal that the hypothesis has drifted away
    from the theme's economic intuition toward a generic momentum bet.

    Args:
        theme: The theme the DSL was proposed under.
        n_default_momentum_factors_used: Count of distinct default
            momentum factors referenced in the DSL's factor set.

    Returns:
        True iff ``theme in THIN_THEMES`` and
        ``n_default_momentum_factors_used >= 2``.
    """
    if theme not in THIN_THEMES:
        return False
    return n_default_momentum_factors_used >= 2


def compute_max_overlap(
    f_current: set[str],
    f_priors: list[set[str]] | tuple[set[str], ...],
) -> int:
    """Max count of factors shared between the current factor set and any single prior factor set.

    DESIGN INVARIANT: This returns an integer count, NOT a Jaccard ratio.
    Count is the right primitive for "how many factors are reused"; Jaccard
    normalizes by union size, which produces counterintuitive values at
    different factor-set sizes.

    In selection/replay contexts, f_priors must represent:
    - prior valid candidates only
    - empty factor sets excluded
    - distinct factor sets only

    Args:
        f_current: Factor set of the current candidate.
        f_priors: Prior distinct factor sets.

    Returns:
        Max count of shared factors. 0 if f_priors is empty.
    """
    if not f_priors:
        return 0
    return max(len(f_current & f_prior) for f_prior in f_priors)


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
    "THIN_THEMES",
    "compute_max_overlap",
    "count_conditions",
    "count_entry_groups",
    "count_exit_groups",
    "extract_factors",
    "factor_set_tuple",
    "get_description_length",
    "get_max_hold_bars",
    "is_thin_theme_momentum_bleed",
]
