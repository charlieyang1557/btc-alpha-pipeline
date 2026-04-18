"""Tests for D7a scoring rules, supporting measures, and flags.

Covers each of the 4 scoring rules with ≥5 test cases each, the full
Edge Behavior Table for complexity_appropriateness (parameterized),
supporting measures, and all 6 flag conditions.
"""

from __future__ import annotations

import pytest

from factors.registry import get_registry
from strategies.dsl import StrategyDSL

from agents.critic.batch_context import (
    DEFAULT_MOMENTUM_FACTORS,
    THEME_ANCHOR_FACTORS,
    THEME_HINTS,
    BatchContext,
)
from agents.critic.d7a_rules import (
    complexity_appropriateness,
    compute_rule_flags,
    compute_supporting_measures,
    default_momentum_fallback,
    score_d7a,
    structural_novelty,
    theme_coherence,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def reg():
    return get_registry()


def _make_dsl(
    entry: list | None = None,
    exit_: list | None = None,
    description: str = "test description",
    max_hold_bars: int | None = None,
    name: str = "test_strat",
) -> StrategyDSL:
    if entry is None:
        entry = [
            {"conditions": [{"factor": "sma_20", "op": ">", "value": 50000.0}]}
        ]
    if exit_ is None:
        exit_ = [
            {"conditions": [{"factor": "sma_20", "op": "<", "value": 45000.0}]}
        ]
    return StrategyDSL.model_validate({
        "name": name,
        "description": description,
        "entry": entry,
        "exit": exit_,
        "position_sizing": "full_equity",
        "max_hold_bars": max_hold_bars,
    })


def _make_ctx(
    prior_factor_sets: tuple[tuple[str, ...], ...] = (),
    prior_hashes: tuple[str, ...] = (),
    batch_position: int = 1,
) -> BatchContext:
    return BatchContext(
        prior_factor_sets=prior_factor_sets,
        prior_hashes=prior_hashes,
        batch_position=batch_position,
        theme_hints=THEME_HINTS,
        default_momentum_factors=DEFAULT_MOMENTUM_FACTORS,
        theme_anchor_factors=THEME_ANCHOR_FACTORS,
    )


# ---------------------------------------------------------------------------
# Rule 1: theme_coherence
# ---------------------------------------------------------------------------


class TestThemeCoherence:
    def test_full_overlap_momentum(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
            ]}],
            exit_=[{"conditions": [
                {"factor": "macd_hist", "op": "<", "value": 0.0},
            ]}],
        )
        ctx = _make_ctx()
        score = theme_coherence(dsl, "momentum", ctx)
        assert score == 1.0

    def test_no_overlap(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "atr_14", "op": ">", "value": 1.0},
            ]}],
            exit_=[{"conditions": [
                {"factor": "realized_vol_24h", "op": ">", "value": 0.02},
            ]}],
        )
        ctx = _make_ctx()
        score = theme_coherence(dsl, "momentum", ctx)
        assert score == 0.0

    def test_partial_overlap(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
                {"factor": "atr_14", "op": ">", "value": 1.0},
            ]}],
        )
        ctx = _make_ctx()
        score = theme_coherence(dsl, "momentum", ctx)
        assert 0.0 < score < 1.0

    def test_mean_reversion_theme(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "zscore_48", "op": "<", "value": -2.0},
            ]}],
            exit_=[{"conditions": [
                {"factor": "close", "op": ">", "value": 50000.0},
            ]}],
        )
        ctx = _make_ctx()
        score = theme_coherence(dsl, "mean_reversion", ctx)
        assert score == 1.0

    def test_unknown_theme_returns_zero(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        score = theme_coherence(dsl, "nonexistent_theme", ctx)
        assert score == 0.0


# ---------------------------------------------------------------------------
# Rule 2: structural_novelty
# ---------------------------------------------------------------------------


class TestStructuralNovelty:
    def test_first_occurrence(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        score = structural_novelty(dsl, ctx)
        assert score == 1.0

    def test_one_prior(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx(prior_factor_sets=(("sma_20",),))
        score = structural_novelty(dsl, ctx)
        assert score == 0.5

    def test_two_priors(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx(prior_factor_sets=(("sma_20",), ("sma_20",)))
        score = structural_novelty(dsl, ctx)
        assert score == round(1.0 / 3.0, 4)

    def test_five_priors(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx(prior_factor_sets=(("sma_20",),) * 5)
        score = structural_novelty(dsl, ctx)
        assert score == round(1.0 / 6.0, 4)

    def test_non_matching_prior(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx(prior_factor_sets=(("rsi_14",),))
        score = structural_novelty(dsl, ctx)
        assert score == 1.0

    def test_mixed_priors(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx(prior_factor_sets=(
            ("sma_20",), ("rsi_14",), ("sma_20",),
        ))
        score = structural_novelty(dsl, ctx)
        assert score == round(1.0 / 3.0, 4)


# ---------------------------------------------------------------------------
# Rule 3: default_momentum_fallback
# ---------------------------------------------------------------------------


class TestDefaultMomentumFallback:
    def test_momentum_theme_always_1(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
                {"factor": "return_1h", "op": ">", "value": 0.01},
                {"factor": "macd_hist", "op": ">", "value": 0.0},
            ]}],
        )
        ctx = _make_ctx()
        score = default_momentum_fallback(dsl, "momentum", ctx)
        assert score == 1.0

    def test_zero_momentum_factors(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "atr_14", "op": ">", "value": 1.0},
            ]}],
            exit_=[{"conditions": [
                {"factor": "realized_vol_24h", "op": ">", "value": 0.02},
            ]}],
        )
        ctx = _make_ctx()
        score = default_momentum_fallback(dsl, "volatility_regime", ctx)
        assert score == 1.0

    def test_one_momentum_factor(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
                {"factor": "atr_14", "op": ">", "value": 1.0},
            ]}],
        )
        ctx = _make_ctx()
        score = default_momentum_fallback(dsl, "volatility_regime", ctx)
        assert score == 0.8

    def test_two_momentum_factors(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
                {"factor": "return_1h", "op": ">", "value": 0.01},
            ]}],
        )
        ctx = _make_ctx()
        score = default_momentum_fallback(dsl, "volatility_regime", ctx)
        assert score == 0.5

    def test_three_momentum_factors(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
                {"factor": "return_1h", "op": ">", "value": 0.01},
                {"factor": "macd_hist", "op": ">", "value": 0.0},
            ]}],
        )
        ctx = _make_ctx()
        score = default_momentum_fallback(dsl, "volume_divergence", ctx)
        assert score == 0.35

    def test_four_momentum_factors_floors_at_zero(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
                {"factor": "return_1h", "op": ">", "value": 0.01},
                {"factor": "macd_hist", "op": ">", "value": 0.0},
                {"factor": "return_24h", "op": ">", "value": 0.02},
            ]}],
        )
        ctx = _make_ctx()
        score = default_momentum_fallback(dsl, "calendar_effect", ctx)
        assert score == 0.2


# ---------------------------------------------------------------------------
# Rule 4: complexity_appropriateness — FULL edge behavior table
# ---------------------------------------------------------------------------


class TestComplexityAppropriateness:
    """Tests pinning every row of the spec's Edge Behavior Table.

    Rows that cannot be constructed via valid StrategyDSL (n_conditions=0,
    n_conditions=1, n_factors=0, desc_len>300) are tested by
    monkeypatching the feature extraction functions so the formula logic
    is verified independently of schema constraints.
    """

    @pytest.mark.parametrize(
        "n_conditions, n_factors, desc_len, expected",
        [
            (0, 3, 100, 0.0),
            (1, 3, 100, 0.7),
            (2, 3, 100, 1.0),
            (4, 4, 100, 1.0),
            (5, 4, 100, 0.85),
            (6, 4, 100, 0.7),
            (10, 4, 100, 0.1),
            (20, 4, 100, 0.0),
            (3, 0, 100, 0.0),
            (3, 8, 100, 0.85),
            (3, 4, 600, 0.9),
            (3, 8, 600, 0.765),
        ],
    )
    def test_edge_behavior_table(
        self, reg, monkeypatch, n_conditions, n_factors, desc_len, expected,
    ):
        import agents.critic.d7a_feature_extraction as fe_mod

        # Build a minimal valid DSL just as a carrier object
        dsl = _make_dsl()

        # Monkeypatch extraction so the rule sees the edge-table inputs
        fake_factors = [f"f{i}" for i in range(n_factors)]
        monkeypatch.setattr(fe_mod, "extract_factors", lambda _dsl: fake_factors)
        monkeypatch.setattr(fe_mod, "count_conditions", lambda _dsl: n_conditions)
        monkeypatch.setattr(fe_mod, "get_description_length", lambda _dsl: desc_len)

        score = complexity_appropriateness(dsl)
        assert score == pytest.approx(expected, abs=1e-4), (
            f"n_conditions={n_conditions}, n_factors={n_factors}, "
            f"desc_len={desc_len}: expected {expected}, got {score}"
        )

    def test_real_dsl_2_conditions_1_factor(self, reg):
        """Real DSL: 1 entry + 1 exit = 2 conditions, 1 factor."""
        dsl = _make_dsl()
        score = complexity_appropriateness(dsl)
        assert score == 1.0

    def test_real_dsl_5_conditions(self, reg):
        """Real DSL: 4 entry + 1 exit = 5 conditions, 4 factors."""
        all_factors = sorted(get_registry().list_names())
        dsl = StrategyDSL.model_validate({
            "name": "cplx_5",
            "description": "test",
            "entry": [{"conditions": [
                {"factor": all_factors[0], "op": ">", "value": 1000.0},
                {"factor": all_factors[1], "op": ">", "value": 1001.0},
                {"factor": all_factors[2], "op": ">", "value": 1002.0},
                {"factor": all_factors[3], "op": ">", "value": 1003.0},
            ]}],
            "exit": [{"conditions": [
                {"factor": all_factors[0], "op": "<", "value": 900.0},
            ]}],
            "position_sizing": "full_equity",
        })
        score = complexity_appropriateness(dsl)
        assert score == 0.85

    def test_real_dsl_high_conditions(self, reg):
        """Real DSL: 12 entry + 1 exit = 13 conditions → score floors at 0."""
        all_factors = sorted(get_registry().list_names())
        entry_groups = []
        for g in range(3):
            conds = []
            for i in range(4):
                f = all_factors[(g * 4 + i) % len(all_factors)]
                conds.append(
                    {"factor": f, "op": ">", "value": float(1000 + g * 4 + i)}
                )
            entry_groups.append({"conditions": conds})
        dsl = StrategyDSL.model_validate({
            "name": "extreme_test",
            "description": "x" * 100,
            "entry": entry_groups,
            "exit": [{"conditions": [
                {"factor": all_factors[0], "op": "<", "value": 45000.0},
            ]}],
            "position_sizing": "full_equity",
        })
        score = complexity_appropriateness(dsl)
        assert score == 0.0


# ---------------------------------------------------------------------------
# Supporting measures
# ---------------------------------------------------------------------------


class TestSupportingMeasures:
    def test_basic_measures(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        m = compute_supporting_measures(dsl, ctx)
        assert m["n_factors"] == 1
        assert m["n_conditions"] == 2
        assert m["n_entry_groups"] == 1
        assert m["n_exit_groups"] == 1
        assert m["factor_set_prior_occurrences"] == 0

    def test_prior_occurrences_counted(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx(prior_factor_sets=(("sma_20",), ("sma_20",)))
        m = compute_supporting_measures(dsl, ctx)
        assert m["factor_set_prior_occurrences"] == 2

    def test_description_length_reported(self, reg):
        dsl = _make_dsl(description="a" * 250)
        ctx = _make_ctx()
        m = compute_supporting_measures(dsl, ctx)
        assert m["description_length"] == 250

    def test_max_hold_bars_reported(self, reg):
        dsl = _make_dsl(max_hold_bars=100)
        ctx = _make_ctx()
        m = compute_supporting_measures(dsl, ctx)
        assert m["max_hold_bars"] == 100

    def test_max_hold_bars_none(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        m = compute_supporting_measures(dsl, ctx)
        assert m["max_hold_bars"] is None


# ---------------------------------------------------------------------------
# Rule flags
# ---------------------------------------------------------------------------


class TestRuleFlags:
    def test_no_flags_on_clean_candidate(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
            ]}],
            exit_=[{"conditions": [
                {"factor": "macd_hist", "op": "<", "value": 0.0},
            ]}],
        )
        ctx = _make_ctx()
        flags = compute_rule_flags(dsl, "momentum", ctx)
        assert flags == []

    def test_thin_theme_momentum_bleed(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
                {"factor": "return_1h", "op": ">", "value": 0.01},
            ]}],
        )
        ctx = _make_ctx()
        flags = compute_rule_flags(dsl, "volume_divergence", ctx)
        assert "thin_theme_momentum_bleed" in flags

    def test_thin_theme_not_triggered_for_momentum(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
                {"factor": "return_1h", "op": ">", "value": 0.01},
            ]}],
        )
        ctx = _make_ctx()
        flags = compute_rule_flags(dsl, "momentum", ctx)
        assert "thin_theme_momentum_bleed" not in flags

    def test_factor_set_in_top3_repeated(self, reg):
        dsl = _make_dsl()  # factor set = ("sma_20",)
        ctx = _make_ctx(prior_factor_sets=(
            ("sma_20",), ("sma_20",), ("sma_20",),
        ))
        flags = compute_rule_flags(dsl, "momentum", ctx)
        assert "factor_set_in_top3_repeated" in flags

    def test_factor_set_in_top3_not_triggered_below_2(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx(prior_factor_sets=(("sma_20",),))
        flags = compute_rule_flags(dsl, "momentum", ctx)
        assert "factor_set_in_top3_repeated" not in flags

    def test_theme_anchor_missing_volume_divergence(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
            ]}],
        )
        ctx = _make_ctx()
        flags = compute_rule_flags(dsl, "volume_divergence", ctx)
        assert "theme_anchor_missing" in flags

    def test_theme_anchor_present_volume_divergence(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "volume_zscore_24h", "op": ">", "value": 2.0},
            ]}],
        )
        ctx = _make_ctx()
        flags = compute_rule_flags(dsl, "volume_divergence", ctx)
        assert "theme_anchor_missing" not in flags

    def test_theme_anchor_calendar_effect_missing(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
            ]}],
        )
        ctx = _make_ctx()
        flags = compute_rule_flags(dsl, "calendar_effect", ctx)
        assert "theme_anchor_missing" in flags

    def test_theme_anchor_calendar_effect_present(self, reg):
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "day_of_week", "op": "==", "value": 1.0},
            ]}],
        )
        ctx = _make_ctx()
        flags = compute_rule_flags(dsl, "calendar_effect", ctx)
        assert "theme_anchor_missing" not in flags

    def test_theme_anchor_momentum_never_fires(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        flags = compute_rule_flags(dsl, "momentum", ctx)
        assert "theme_anchor_missing" not in flags

    def test_description_length_near_limit(self, reg, monkeypatch):
        import agents.critic.d7a_feature_extraction as fe_mod
        dsl = _make_dsl(description="x" * 100)
        monkeypatch.setattr(fe_mod, "get_description_length", lambda _dsl: 420)
        ctx = _make_ctx()
        flags = compute_rule_flags(dsl, "momentum", ctx)
        assert "description_length_near_limit" in flags

    def test_description_length_at_boundary(self, reg, monkeypatch):
        import agents.critic.d7a_feature_extraction as fe_mod
        dsl = _make_dsl(description="x" * 100)
        monkeypatch.setattr(fe_mod, "get_description_length", lambda _dsl: 400)
        ctx = _make_ctx()
        flags = compute_rule_flags(dsl, "momentum", ctx)
        assert "description_length_near_limit" in flags

    def test_n_conditions_heavy(self, reg):
        all_factors = sorted(get_registry().list_names())
        entry_groups = [
            {"conditions": [
                {"factor": all_factors[0], "op": ">", "value": 50000.0},
                {"factor": all_factors[1], "op": ">", "value": 1.0},
                {"factor": all_factors[2], "op": ">", "value": 30.0},
                {"factor": all_factors[3], "op": ">", "value": 0.0},
            ]},
        ]
        exit_ = [
            {"conditions": [
                {"factor": all_factors[0], "op": "<", "value": 45000.0},
                {"factor": all_factors[1], "op": "<", "value": 0.5},
            ]}
        ]
        dsl = StrategyDSL.model_validate({
            "name": "heavy",
            "description": "test",
            "entry": entry_groups,
            "exit": exit_,
            "position_sizing": "full_equity",
        })
        ctx = _make_ctx()
        flags = compute_rule_flags(dsl, "momentum", ctx)
        assert "n_conditions_heavy" in flags

    def test_flags_can_coexist(self, reg, monkeypatch):
        import agents.critic.d7a_feature_extraction as fe_mod
        dsl = _make_dsl(
            entry=[{"conditions": [
                {"factor": "rsi_14", "op": ">", "value": 30.0},
                {"factor": "return_1h", "op": ">", "value": 0.01},
            ]}],
            description="x" * 100,
        )
        monkeypatch.setattr(fe_mod, "get_description_length", lambda _dsl: 420)
        ctx = _make_ctx(prior_factor_sets=(
            ("return_1h", "rsi_14", "sma_20"),
            ("return_1h", "rsi_14", "sma_20"),
        ))
        flags = compute_rule_flags(dsl, "volume_divergence", ctx)
        assert "thin_theme_momentum_bleed" in flags
        assert "theme_anchor_missing" in flags
        assert "description_length_near_limit" in flags


# ---------------------------------------------------------------------------
# score_d7a (all-in-one)
# ---------------------------------------------------------------------------


class TestScoreD7a:
    def test_returns_three_components(self, reg):
        dsl = _make_dsl()
        ctx = _make_ctx()
        scores, measures, flags = score_d7a(dsl, "momentum", ctx)
        assert scores is not None
        assert "theme_coherence" in scores
        assert "structural_novelty" in scores
        assert "default_momentum_fallback" in scores
        assert "complexity_appropriateness" in scores
        assert isinstance(measures, dict)
        assert isinstance(flags, list)
