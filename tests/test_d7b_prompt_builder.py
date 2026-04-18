"""Tests for agents/critic/d7b_prompt.py — D7b prompt builder + leakage audit.

Covers:
    - build_d7b_prompt() output content (DSL, theme, prior factor sets)
    - _format_prior_factor_sets() dedup and ordering
    - run_leakage_audit() positive and negative cases
    - D7B_FORBIDDEN_TERMS membership
"""

from __future__ import annotations

import pytest

from agents.critic.batch_context import (
    DEFAULT_MOMENTUM_FACTORS,
    THEME_ANCHOR_FACTORS,
    THEME_HINTS,
    BatchContext,
)
from agents.critic.d7b_prompt import (
    D7B_FORBIDDEN_TERMS,
    _dedup_prior_factor_sets,
    _format_prior_factor_sets,
    build_d7b_prompt,
    run_leakage_audit,
)
from strategies.dsl import StrategyDSL


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_dsl(**overrides) -> StrategyDSL:
    """Build a minimal valid StrategyDSL for prompt-builder tests."""
    base = {
        "name": "test_strat",
        "description": "A simple momentum test strategy for prompt building",
        "entry": [
            {"conditions": [{"factor": "rsi_14", "op": ">", "value": 30.0}]},
        ],
        "exit": [
            {"conditions": [{"factor": "rsi_14", "op": "<", "value": 70.0}]},
        ],
        "position_sizing": "full_equity",
        "max_hold_bars": 168,
    }
    base.update(overrides)
    return StrategyDSL(**base)


def _make_batch_context(
    prior_factor_sets=(),
    prior_hashes=(),
    batch_position=5,
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
# build_d7b_prompt tests
# ---------------------------------------------------------------------------


def test_prompt_contains_dsl_pretty_print():
    """build_d7b_prompt includes the DSL JSON pretty-printed."""
    dsl = _make_dsl()
    ctx = _make_batch_context()
    prompt = build_d7b_prompt(dsl, "momentum", ctx)
    assert '"rsi_14"' in prompt
    assert '"test_strat"' in prompt


def test_prompt_includes_theme_name():
    """build_d7b_prompt includes the theme name verbatim."""
    dsl = _make_dsl()
    ctx = _make_batch_context()
    prompt = build_d7b_prompt(dsl, "volatility_regime", ctx)
    assert "volatility_regime" in prompt


def test_prompt_includes_prior_factor_sets_formatted():
    """Prior factor sets are rendered as a bulleted list."""
    dsl = _make_dsl()
    ctx = _make_batch_context(
        prior_factor_sets=(("atr_14", "rsi_14"), ("return_24h",)),
    )
    prompt = build_d7b_prompt(dsl, "momentum", ctx)
    assert "- {atr_14, rsi_14}" in prompt
    assert "- {return_24h}" in prompt


def test_prompt_empty_prior_factor_sets_renders_none():
    """Empty prior_factor_sets renders as _(none)_."""
    dsl = _make_dsl()
    ctx = _make_batch_context(prior_factor_sets=())
    prompt = build_d7b_prompt(dsl, "momentum", ctx)
    assert "_(none)_" in prompt


# ---------------------------------------------------------------------------
# _format_prior_factor_sets / _dedup_prior_factor_sets tests
# ---------------------------------------------------------------------------


def test_format_prior_factor_sets_deduplicates():
    """Duplicate factor sets (regardless of internal order) appear once."""
    pfs = (
        ("rsi_14", "atr_14"),
        ("atr_14", "rsi_14"),
    )
    result = _format_prior_factor_sets(pfs)
    # After dedup and sort, only one entry remains.
    assert result.count("- {") == 1
    assert "atr_14, rsi_14" in result


def test_format_prior_factor_sets_preserves_first_seen_order():
    """First-seen order across distinct sets is preserved."""
    pfs = (
        ("return_24h",),
        ("rsi_14", "atr_14"),
        ("macd_hist",),
    )
    result = _format_prior_factor_sets(pfs)
    lines = result.strip().split("\n")
    assert len(lines) == 3
    assert "return_24h" in lines[0]
    assert "atr_14, rsi_14" in lines[1]
    assert "macd_hist" in lines[2]


def test_dedup_sorts_factors_within_each_set():
    """_dedup_prior_factor_sets sorts factors alphabetically within sets."""
    pfs = (("rsi_14", "atr_14", "macd_hist"),)
    deduped = _dedup_prior_factor_sets(pfs)
    assert deduped == [("atr_14", "macd_hist", "rsi_14")]


# ---------------------------------------------------------------------------
# run_leakage_audit tests
# ---------------------------------------------------------------------------


def test_leakage_audit_clean_prompt_returns_none():
    """A clean prompt passes leakage audit (returns None)."""
    dsl = _make_dsl()
    ctx = _make_batch_context()
    prompt = build_d7b_prompt(dsl, "momentum", ctx)
    assert run_leakage_audit(prompt) is None


def test_leakage_audit_catches_uuid_pattern():
    """UUIDs in the prompt are detected."""
    text = "Some prompt text with uuid 01234567-abcd-ef01-2345-6789abcdef01 leaked."
    result = run_leakage_audit(text)
    assert result is not None
    assert "UUID leaked" in result


def test_leakage_audit_catches_year_dates():
    """Year-date patterns (2022-2026) are detected."""
    text = "Some prompt text referring to 2024-03-15 date."
    result = run_leakage_audit(text)
    assert result is not None
    assert "date leaked" in result


def test_leakage_audit_catches_directive_words_outside_enumeration():
    """Directive words outside the forbidden-language block are caught."""
    # Construct minimal text without the enumeration block.
    text = "I recommend you evaluate this strategy carefully."
    result = run_leakage_audit(text)
    assert result is not None
    assert "directive language outside enumeration block" in result


def test_leakage_audit_does_not_flag_directives_inside_enumeration_block():
    """Directive words INSIDE the enumeration block are exempt."""
    dsl = _make_dsl()
    ctx = _make_batch_context()
    prompt = build_d7b_prompt(dsl, "momentum", ctx)
    # The prompt template has the enumeration block with words like
    # "accept", "reject", "approve", etc. These should NOT trigger.
    assert run_leakage_audit(prompt) is None


# ---------------------------------------------------------------------------
# D7B_FORBIDDEN_TERMS tests
# ---------------------------------------------------------------------------


def test_d7b_forbidden_terms_is_frozenset():
    assert isinstance(D7B_FORBIDDEN_TERMS, frozenset)


def test_d7b_forbidden_terms_contains_expected():
    """Spot-check key members."""
    assert "accept" in D7B_FORBIDDEN_TERMS
    assert "reject" in D7B_FORBIDDEN_TERMS
    assert "approve" in D7B_FORBIDDEN_TERMS
    assert "should be used" in D7B_FORBIDDEN_TERMS
    assert "green light" in D7B_FORBIDDEN_TERMS
    assert "discard" in D7B_FORBIDDEN_TERMS
