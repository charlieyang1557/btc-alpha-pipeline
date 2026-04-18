"""D7a rule-based scoring — pure, deterministic, [0.0, 1.0]-bounded.

All scoring functions are:
    - Pure (no randomness, no wall-clock, no disk state, no network)
    - Deterministic (same input → same output)
    - Bounded to [0.0, 1.0] with None reserved for unrecoverable errors
    - Rounded to 4 decimal places in output

Rule formulas are frozen at D7 Stage 1. Tuning is D7 v2 work.
"""

from __future__ import annotations

from agents.critic import d7a_feature_extraction as fe
from agents.critic.batch_context import BatchContext
from strategies.dsl import StrategyDSL


# -----------------------------------------------------------------------
# Rule 1: theme_coherence
# -----------------------------------------------------------------------


def theme_coherence(
    dsl: StrategyDSL, theme: str, batch_context: BatchContext,
) -> float:
    """Fraction of DSL factors that are in the theme's hint set.

    Returns 0.0 for empty factor set (no overlap possible).
    """
    factors = set(fe.extract_factors(dsl))
    hints = batch_context.theme_hints.get(theme, frozenset())
    if not factors:
        return 0.0
    overlap = factors & hints
    return round(len(overlap) / len(factors), 4)


# -----------------------------------------------------------------------
# Rule 2: structural_novelty
# -----------------------------------------------------------------------


def structural_novelty(
    dsl: StrategyDSL, batch_context: BatchContext,
) -> float | None:
    """Inverse exponential decay with prior-occurrence count.

    Returns None for empty factor set (degenerate; concept undefined).
    """
    factor_set = fe.factor_set_tuple(dsl)
    if not factor_set:
        return None
    prior_occurrences = batch_context.prior_factor_sets.count(factor_set)
    return round(1.0 / (1.0 + prior_occurrences), 4)


# -----------------------------------------------------------------------
# Rule 3: default_momentum_fallback
# -----------------------------------------------------------------------


def default_momentum_fallback(
    dsl: StrategyDSL, theme: str, batch_context: BatchContext,
) -> float:
    """How much this DSL relies on default momentum factors.

    Penalized only when ``theme != "momentum"``. Returns 0.0 for empty
    factor set.
    """
    default_momentum = batch_context.default_momentum_factors
    factors = set(fe.extract_factors(dsl))
    if not factors:
        return 0.0
    momentum_count = len(factors & default_momentum)

    if theme == "momentum":
        return 1.0

    if momentum_count == 0:
        return 1.0
    elif momentum_count == 1:
        return 0.8
    elif momentum_count == 2:
        return 0.5
    else:
        return round(max(0.0, 0.5 - 0.15 * (momentum_count - 2)), 4)


# -----------------------------------------------------------------------
# Rule 4: complexity_appropriateness (LOCKED formula)
# -----------------------------------------------------------------------


def complexity_appropriateness(dsl: StrategyDSL) -> float:
    """Complexity appropriateness score. LOCKED formula — do not modify.

    Step boundaries are intentional (auditable cliffs, not smoothed).
    """
    n_factors = len(set(fe.extract_factors(dsl)))
    n_conditions = fe.count_conditions(dsl)
    desc_len = fe.get_description_length(dsl)

    if n_conditions == 0:
        return 0.0
    if n_factors == 0:
        return 0.0

    if n_conditions == 1:
        base = 0.7
    elif 2 <= n_conditions <= 4:
        base = 1.0
    else:
        base = max(0.0, 1.0 - 0.15 * (n_conditions - 4))

    if n_factors > 7:
        base *= 0.85

    if desc_len > 500:
        base *= 0.9

    return round(base, 4)


# -----------------------------------------------------------------------
# Supporting measures (raw counts, NOT scores)
# -----------------------------------------------------------------------


def compute_supporting_measures(
    dsl: StrategyDSL, batch_context: BatchContext,
) -> dict[str, int | None]:
    """Compute D7a supporting measures (raw inputs for D8 policy).

    Empty factor set → ``factor_set_prior_occurrences = None``.
    """
    factors = fe.extract_factors(dsl)
    factor_set = fe.factor_set_tuple(dsl)
    if not factor_set:
        prior_occ: int | None = None
    else:
        prior_occ = batch_context.prior_factor_sets.count(factor_set)
    return {
        "factor_set_prior_occurrences": prior_occ,
        "n_factors": len(set(factors)),
        "n_conditions": fe.count_conditions(dsl),
        "description_length": fe.get_description_length(dsl),
        "max_hold_bars": fe.get_max_hold_bars(dsl),
        "n_entry_groups": fe.count_entry_groups(dsl),
        "n_exit_groups": fe.count_exit_groups(dsl),
    }


# -----------------------------------------------------------------------
# Rule flags (symbolic observation tags, NOT gate signals)
# -----------------------------------------------------------------------


def compute_rule_flags(
    dsl: StrategyDSL, theme: str, batch_context: BatchContext,
) -> list[str]:
    """Compute D7a rule flags. Flags are observation tags, NOT gate signals."""
    flags: list[str] = []
    factors = set(fe.extract_factors(dsl))
    n_conditions = fe.count_conditions(dsl)
    desc_len = fe.get_description_length(dsl)

    # empty_factor_set
    if not factors:
        flags.append("empty_factor_set")

    # thin_theme_momentum_bleed
    thin_themes = {"volume_divergence", "calendar_effect", "volatility_regime"}
    if theme in thin_themes:
        momentum_overlap = len(factors & batch_context.default_momentum_factors)
        if momentum_overlap >= 2:
            flags.append("thin_theme_momentum_bleed")

    # factor_set_in_top3_repeated
    if factors:
        factor_set = fe.factor_set_tuple(dsl)
        fs_counts: dict[tuple[str, ...], tuple[int, int]] = {}
        for i, fs in enumerate(batch_context.prior_factor_sets):
            if fs not in fs_counts:
                fs_counts[fs] = (0, i)
            fs_counts[fs] = (fs_counts[fs][0] + 1, fs_counts[fs][1])
        qualified = {
            fs: (count, first_pos)
            for fs, (count, first_pos) in fs_counts.items()
            if count >= 2
        }
        if qualified:
            top3 = sorted(
                qualified.keys(),
                key=lambda fs: (-qualified[fs][0], qualified[fs][1]),
            )[:3]
            if factor_set in top3:
                flags.append("factor_set_in_top3_repeated")

    # theme_anchor_missing
    anchor_set = batch_context.theme_anchor_factors.get(theme, frozenset())
    if anchor_set and not (factors & anchor_set):
        flags.append("theme_anchor_missing")

    # description_length_near_limit
    if 400 <= desc_len < 500:
        flags.append("description_length_near_limit")

    # n_conditions_heavy
    if n_conditions >= 6:
        flags.append("n_conditions_heavy")

    return flags


# -----------------------------------------------------------------------
# All-in-one D7a scorer
# -----------------------------------------------------------------------


def score_d7a(
    dsl: StrategyDSL, theme: str, batch_context: BatchContext,
) -> tuple[dict[str, float] | None, dict[str, int | None], list[str]]:
    """Run all D7a rules and return (scores, supporting_measures, flags).

    Returns ``(None, measures, flags)`` only if an unrecoverable error
    occurs in rule computation. Under normal conditions scores are always
    populated (individual score entries may be None for degenerate inputs
    like empty factor set — those go into the dict as-is).
    """
    scores: dict[str, float | None] = {
        "theme_coherence": theme_coherence(dsl, theme, batch_context),
        "structural_novelty": structural_novelty(dsl, batch_context),
        "default_momentum_fallback": default_momentum_fallback(
            dsl, theme, batch_context,
        ),
        "complexity_appropriateness": complexity_appropriateness(dsl),
    }
    measures = compute_supporting_measures(dsl, batch_context)
    flags = compute_rule_flags(dsl, theme, batch_context)

    # Convert None-valued scores: the CriticResult dict type is
    # dict[str, float] | None (all-or-nothing). Individual None scores
    # (structural_novelty on empty factor set) are kept in the dict.
    # The dict itself is None only on error.
    return scores, measures, flags  # type: ignore[return-value]


__all__ = [
    "complexity_appropriateness",
    "compute_rule_flags",
    "compute_supporting_measures",
    "default_momentum_fallback",
    "score_d7a",
    "structural_novelty",
    "theme_coherence",
]
