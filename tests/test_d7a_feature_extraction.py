"""Tests for D7a feature extraction primitives.

Separated from rule tests because feature extraction correctness is a
prerequisite for rule correctness: if extraction is wrong, every rule
is wrong downstream. See agents/critic/d7a_feature_extraction.py module
docstring for the correctness-contract rationale.
"""

from __future__ import annotations

import pytest

from factors.registry import get_registry
from strategies.dsl import StrategyDSL

from agents.critic.d7a_feature_extraction import (
    THIN_THEMES,
    compute_max_overlap,
    count_conditions,
    count_entry_groups,
    count_exit_groups,
    extract_factors,
    factor_set_tuple,
    get_description_length,
    get_max_hold_bars,
    is_thin_theme_momentum_bleed,
)


# ---------------------------------------------------------------------------
# Fixtures
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
    """Build a StrategyDSL for testing. Uses live registry via default."""
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


# ---------------------------------------------------------------------------
# extract_factors
# ---------------------------------------------------------------------------


class TestExtractFactors:
    def test_single_factor(self, reg):
        dsl = _make_dsl()
        factors = extract_factors(dsl)
        assert factors == ["sma_20"]

    def test_multiple_factors(self, reg):
        dsl = _make_dsl(
            entry=[
                {"conditions": [
                    {"factor": "sma_20", "op": ">", "value": 50000.0},
                    {"factor": "rsi_14", "op": "<", "value": 70.0},
                ]}
            ],
            exit_=[
                {"conditions": [{"factor": "atr_14", "op": ">", "value": 1.0}]}
            ],
        )
        factors = extract_factors(dsl)
        assert factors == ["atr_14", "rsi_14", "sma_20"]

    def test_factor_vs_factor(self, reg):
        dsl = _make_dsl(
            entry=[
                {"conditions": [
                    {"factor": "sma_20", "op": ">", "value": "sma_50"},
                ]}
            ],
        )
        factors = extract_factors(dsl)
        assert "sma_20" in factors
        assert "sma_50" in factors

    def test_deduplication(self, reg):
        dsl = _make_dsl(
            entry=[
                {"conditions": [
                    {"factor": "sma_20", "op": ">", "value": 50000.0},
                ]}
            ],
            exit_=[
                {"conditions": [
                    {"factor": "sma_20", "op": "<", "value": 45000.0},
                ]}
            ],
        )
        factors = extract_factors(dsl)
        assert factors.count("sma_20") == 1

    def test_sorted_output(self, reg):
        dsl = _make_dsl(
            entry=[
                {"conditions": [
                    {"factor": "rsi_14", "op": ">", "value": 30.0},
                    {"factor": "atr_14", "op": ">", "value": 1.0},
                ]}
            ],
            exit_=[
                {"conditions": [{"factor": "sma_20", "op": "<", "value": 45000.0}]}
            ],
        )
        factors = extract_factors(dsl)
        assert factors == sorted(factors)

    def test_many_conditions(self, reg):
        dsl = _make_dsl(
            entry=[
                {"conditions": [
                    {"factor": "sma_20", "op": ">", "value": 50000.0},
                    {"factor": "rsi_14", "op": "<", "value": 70.0},
                    {"factor": "atr_14", "op": ">", "value": 1.0},
                    {"factor": "macd_hist", "op": ">", "value": 0.0},
                ]},
                {"conditions": [
                    {"factor": "return_1h", "op": ">", "value": 0.01},
                ]},
            ],
            exit_=[
                {"conditions": [
                    {"factor": "realized_vol_24h", "op": ">", "value": 0.02},
                ]}
            ],
        )
        factors = extract_factors(dsl)
        assert len(factors) == 6
        assert factors == sorted(
            ["atr_14", "macd_hist", "realized_vol_24h", "return_1h",
             "rsi_14", "sma_20"]
        )


# ---------------------------------------------------------------------------
# count_conditions
# ---------------------------------------------------------------------------


class TestCountConditions:
    def test_single_entry_single_exit(self, reg):
        dsl = _make_dsl()
        assert count_conditions(dsl) == 2

    def test_multiple_conditions_per_group(self, reg):
        dsl = _make_dsl(
            entry=[
                {"conditions": [
                    {"factor": "sma_20", "op": ">", "value": 50000.0},
                    {"factor": "rsi_14", "op": "<", "value": 70.0},
                ]}
            ],
        )
        assert count_conditions(dsl) == 3

    def test_multiple_groups(self, reg):
        dsl = _make_dsl(
            entry=[
                {"conditions": [
                    {"factor": "sma_20", "op": ">", "value": 50000.0},
                ]},
                {"conditions": [
                    {"factor": "rsi_14", "op": ">", "value": 30.0},
                ]},
            ],
            exit_=[
                {"conditions": [
                    {"factor": "sma_20", "op": "<", "value": 45000.0},
                ]},
                {"conditions": [
                    {"factor": "rsi_14", "op": "<", "value": 70.0},
                ]},
            ],
        )
        assert count_conditions(dsl) == 4

    def test_max_complexity(self, reg):
        dsl = _make_dsl(
            entry=[
                {"conditions": [
                    {"factor": "sma_20", "op": ">", "value": 50000.0},
                    {"factor": "rsi_14", "op": "<", "value": 70.0},
                    {"factor": "atr_14", "op": ">", "value": 1.0},
                    {"factor": "macd_hist", "op": ">", "value": 0.0},
                ]},
                {"conditions": [
                    {"factor": "return_1h", "op": ">", "value": 0.01},
                    {"factor": "return_24h", "op": ">", "value": 0.05},
                ]},
                {"conditions": [
                    {"factor": "sma_50", "op": ">", "value": 40000.0},
                ]},
            ],
            exit_=[
                {"conditions": [
                    {"factor": "sma_20", "op": "<", "value": 45000.0},
                ]},
            ],
        )
        assert count_conditions(dsl) == 8

    def test_single_condition(self, reg):
        dsl = _make_dsl(
            exit_=[
                {"conditions": [{"factor": "rsi_14", "op": ">", "value": 70.0}]}
            ],
        )
        assert count_conditions(dsl) == 2


# ---------------------------------------------------------------------------
# Group counts
# ---------------------------------------------------------------------------


class TestGroupCounts:
    def test_entry_groups(self, reg):
        dsl = _make_dsl()
        assert count_entry_groups(dsl) == 1
        assert count_exit_groups(dsl) == 1

    def test_multiple_entry_groups(self, reg):
        dsl = _make_dsl(
            entry=[
                {"conditions": [{"factor": "sma_20", "op": ">", "value": 50000.0}]},
                {"conditions": [{"factor": "rsi_14", "op": ">", "value": 30.0}]},
            ],
        )
        assert count_entry_groups(dsl) == 2
        assert count_exit_groups(dsl) == 1


# ---------------------------------------------------------------------------
# Description length + max_hold_bars
# ---------------------------------------------------------------------------


class TestDescriptionAndHoldBars:
    def test_description_length(self, reg):
        dsl = _make_dsl(description="a" * 100)
        assert get_description_length(dsl) == 100

    def test_short_description(self, reg):
        dsl = _make_dsl(description="x")
        assert get_description_length(dsl) == 1

    def test_max_hold_bars_none(self, reg):
        dsl = _make_dsl(max_hold_bars=None)
        assert get_max_hold_bars(dsl) is None

    def test_max_hold_bars_set(self, reg):
        dsl = _make_dsl(max_hold_bars=720)
        assert get_max_hold_bars(dsl) == 720


# ---------------------------------------------------------------------------
# factor_set_tuple
# ---------------------------------------------------------------------------


class TestFactorSetTuple:
    def test_returns_sorted_tuple(self, reg):
        dsl = _make_dsl(
            entry=[
                {"conditions": [
                    {"factor": "rsi_14", "op": ">", "value": 30.0},
                    {"factor": "atr_14", "op": ">", "value": 1.0},
                ]}
            ],
        )
        fst = factor_set_tuple(dsl)
        assert isinstance(fst, tuple)
        assert fst == ("atr_14", "rsi_14", "sma_20")

    def test_empty_factor_set_impossible_via_schema(self, reg):
        # StrategyDSL requires at least one condition with a factor,
        # so empty factor set can't arise via normal schema validation.
        # But factor_set_tuple should return () for a hypothetical edge.
        dsl = _make_dsl()
        fst = factor_set_tuple(dsl)
        assert len(fst) > 0


# ---------------------------------------------------------------------------
# Thin-theme momentum-bleed predicate (canonical contract)
# ---------------------------------------------------------------------------


# Pinning assertion at module scope: if the THIN_THEMES membership ever
# drifts, this assertion fires at import time and every downstream test
# that references the name surfaces the breakage loudly. Changing this
# membership is a locked-decision boundary shared with d7a_rules and
# the selection script; don't update silently.
assert THIN_THEMES == frozenset({
    "volume_divergence",
    "calendar_effect",
    "volatility_regime",
}), (
    "THIN_THEMES drift: updating this set is a locked-decision boundary; "
    "coordinate with d7a_rules.compute_rule_flags and "
    "scripts/select_replay_candidate.py before changing it."
)


class TestIsThinThemeMomentumBleed:
    def test_is_thin_theme_momentum_bleed_thin_theme_two_momentum_fires(self):
        for theme in THIN_THEMES:
            assert is_thin_theme_momentum_bleed(theme, 2) is True

    def test_is_thin_theme_momentum_bleed_thin_theme_one_momentum_does_not_fire(self):
        for theme in THIN_THEMES:
            assert is_thin_theme_momentum_bleed(theme, 1) is False
            assert is_thin_theme_momentum_bleed(theme, 0) is False

    @pytest.mark.parametrize("theme", ["momentum", "mean_reversion"])
    @pytest.mark.parametrize("n_momentum", [0, 1, 2, 5, 10])
    def test_is_thin_theme_momentum_bleed_non_thin_theme_never_fires(
        self, theme, n_momentum,
    ):
        assert is_thin_theme_momentum_bleed(theme, n_momentum) is False

    def test_is_thin_theme_momentum_bleed_thin_theme_many_momentum_fires(self):
        for theme in THIN_THEMES:
            for n in (2, 3, 5, 10, 100):
                assert is_thin_theme_momentum_bleed(theme, n) is True


# ---------------------------------------------------------------------------
# compute_max_overlap
# ---------------------------------------------------------------------------


class TestComputeMaxOverlap:
    def test_empty_priors_returns_zero(self):
        assert compute_max_overlap({"a", "b", "c"}, []) == 0
        assert compute_max_overlap({"a", "b", "c"}, ()) == 0
        assert compute_max_overlap(set(), []) == 0

    def test_single_prior_with_zero_overlap_returns_zero(self):
        assert compute_max_overlap({"a", "b"}, [{"c", "d"}]) == 0

    def test_single_prior_with_partial_overlap_returns_count(self):
        assert compute_max_overlap({"a", "b", "c"}, [{"a", "d", "e"}]) == 1
        assert compute_max_overlap({"a", "b", "c", "d"}, [{"a", "b", "e"}]) == 2

    def test_multiple_priors_returns_max_not_sum_or_average(self):
        priors = [{"a"}, {"a", "b"}, {"a", "b", "c"}]
        assert compute_max_overlap({"a", "b", "c", "d"}, priors) == 3

    def test_current_subset_of_prior_returns_current_length(self):
        assert compute_max_overlap({"a", "b"}, [{"a", "b", "c", "d"}]) == 2

    def test_current_superset_of_prior_returns_prior_length(self):
        assert compute_max_overlap({"a", "b", "c", "d"}, [{"a", "b"}]) == 2

    def test_identical_sets_returns_full_size(self):
        assert compute_max_overlap({"a", "b", "c"}, [{"a", "b", "c"}]) == 3

    def test_returns_integer_not_ratio(self):
        result = compute_max_overlap({"a", "b"}, [{"a", "b"}])
        assert isinstance(result, int)
        assert result == 2
