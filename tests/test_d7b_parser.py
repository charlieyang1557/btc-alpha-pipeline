"""Tests for agents/critic/d7b_parser.py — D7b response parser.

Covers:
    - Valid JSON parsing
    - Score range validation
    - Extra/missing key errors
    - Out-of-range scores
    - Reasoning length constraints
    - JSON fence/prose stripping
    - Forbidden language detection
    - Refusal pattern detection
    - Non-dict top-level
    - Boundary values
"""

from __future__ import annotations

import json

import pytest

from agents.critic.d7b_parser import (
    D7B_REFUSAL_PATTERNS,
    D7bContentError,
    parse_d7b_response,
)
from agents.critic.d7b_prompt import D7B_FORBIDDEN_TERMS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_REASONING = (
    "The entry logic uses RSI crossing above a threshold combined with "
    "ATR as a volatility filter. The exit uses RSI crossing below to "
    "capture reversal. Theme alignment is moderate."
)

assert 100 <= len(_VALID_REASONING) <= 400, f"fixture length: {len(_VALID_REASONING)}"


def _make_response(**overrides) -> str:
    """Build a valid JSON response string with optional overrides."""
    payload = {
        "semantic_plausibility": 0.7500,
        "semantic_theme_alignment": 0.6000,
        "structural_variant_risk": 0.2000,
        "reasoning": _VALID_REASONING,
    }
    payload.update(overrides)
    return json.dumps(payload)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_valid_json_parses_correctly():
    """Valid JSON with all 4 keys parses to expected scores and reasoning."""
    scores, reasoning, scan_results = parse_d7b_response(_make_response())
    assert scores["semantic_plausibility"] == pytest.approx(0.75)
    assert scores["semantic_theme_alignment"] == pytest.approx(0.60)
    assert scores["structural_variant_risk"] == pytest.approx(0.20)
    assert reasoning == _VALID_REASONING
    assert isinstance(scan_results, dict)


def test_valid_json_returns_three_tuple_types():
    """Success path returns scores, reasoning, and scan metadata."""
    parsed = parse_d7b_response(_make_response())
    assert isinstance(parsed, tuple)
    assert len(parsed) == 3
    scores, reasoning, scan_results = parsed
    assert isinstance(scores, dict)
    assert isinstance(reasoning, str)
    assert isinstance(scan_results, dict)


def test_valid_json_returns_scan_results():
    """Success path returns structured scan results alongside scores."""
    _, _, scan_results = parse_d7b_response(_make_response())
    assert scan_results == {
        "forbidden_language_scan": {
            "status": "pass",
            "hits": [],
            "terms_checked_count": len(D7B_FORBIDDEN_TERMS),
        },
        "refusal_scan": {
            "status": "pass",
            "hits": [],
            "patterns_checked": list(D7B_REFUSAL_PATTERNS),
        },
    }
    assert scan_results["forbidden_language_scan"]["terms_checked_count"] > 0
    assert scan_results["refusal_scan"]["patterns_checked"]
    assert all(
        isinstance(pattern, str)
        for pattern in scan_results["refusal_scan"]["patterns_checked"]
    )


def test_scores_in_range():
    """Scores at valid boundaries are accepted."""
    scores, _, _ = parse_d7b_response(_make_response(
        semantic_plausibility=0.0,
        semantic_theme_alignment=1.0,
        structural_variant_risk=0.5,
    ))
    assert scores["semantic_plausibility"] == pytest.approx(0.0)
    assert scores["semantic_theme_alignment"] == pytest.approx(1.0)


def test_score_exactly_at_boundary_zero():
    """Score exactly at 0.0 is accepted."""
    scores, _, _ = parse_d7b_response(_make_response(
        semantic_plausibility=0.0,
    ))
    assert scores["semantic_plausibility"] == pytest.approx(0.0)


def test_score_exactly_at_boundary_one():
    """Score exactly at 1.0 is accepted."""
    scores, _, _ = parse_d7b_response(_make_response(
        semantic_theme_alignment=1.0,
    ))
    assert scores["semantic_theme_alignment"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Schema violations
# ---------------------------------------------------------------------------


def test_extra_keys_raise_schema_extra_keys():
    text = _make_response(bonus_key="oops")
    with pytest.raises(D7bContentError) as exc_info:
        parse_d7b_response(text)
    assert exc_info.value.error_code == "schema_extra_keys"


def test_missing_keys_raise_schema_missing_keys():
    payload = {
        "semantic_plausibility": 0.5,
        "reasoning": _VALID_REASONING,
    }
    with pytest.raises(D7bContentError) as exc_info:
        parse_d7b_response(json.dumps(payload))
    assert exc_info.value.error_code == "schema_missing_keys"


def test_out_of_range_score_raises():
    text = _make_response(semantic_plausibility=1.5)
    with pytest.raises(D7bContentError) as exc_info:
        parse_d7b_response(text)
    assert exc_info.value.error_code == "schema_out_of_range"


def test_negative_score_raises():
    text = _make_response(structural_variant_risk=-0.1)
    with pytest.raises(D7bContentError) as exc_info:
        parse_d7b_response(text)
    assert exc_info.value.error_code == "schema_out_of_range"


def test_reasoning_too_short_raises():
    text = _make_response(reasoning="Too short.")
    with pytest.raises(D7bContentError) as exc_info:
        parse_d7b_response(text)
    assert exc_info.value.error_code == "schema_reasoning_length"


def test_reasoning_too_long_raises():
    text = _make_response(reasoning="A" * 1501)
    with pytest.raises(D7bContentError) as exc_info:
        parse_d7b_response(text)
    assert exc_info.value.error_code == "schema_reasoning_length"


# ---------------------------------------------------------------------------
# JSON decode errors
# ---------------------------------------------------------------------------


def test_invalid_json_raises_json_decode():
    with pytest.raises(D7bContentError) as exc_info:
        parse_d7b_response("this is not json at all {{{")
    assert exc_info.value.error_code == "json_decode"


def test_non_dict_top_level_raises_json_decode():
    with pytest.raises(D7bContentError) as exc_info:
        parse_d7b_response("[1, 2, 3]")
    assert exc_info.value.error_code == "json_decode"


# ---------------------------------------------------------------------------
# Fence / prose stripping
# ---------------------------------------------------------------------------


def test_json_wrapped_in_fences_parses_correctly():
    """Markdown ```json fences are stripped before parsing."""
    inner = _make_response()
    fenced = f"```json\n{inner}\n```"
    scores, reasoning, _ = parse_d7b_response(fenced)
    assert scores["semantic_plausibility"] == pytest.approx(0.75)
    assert reasoning == _VALID_REASONING


def test_json_with_prose_preamble_and_postamble():
    """Prose before and after the JSON object is stripped."""
    inner = _make_response()
    wrapped = f"Here is my evaluation:\n{inner}\nI hope this helps."
    scores, _, _ = parse_d7b_response(wrapped)
    assert scores["semantic_plausibility"] == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# Forbidden language
# ---------------------------------------------------------------------------


def test_forbidden_language_in_reasoning_raises():
    bad_reasoning = (
        "I recommend this strategy because the RSI threshold is well-chosen "
        "and the exit condition is sensible. The factor set is distinct "
        "from prior entries."
    )
    text = _make_response(reasoning=bad_reasoning)
    with pytest.raises(D7bContentError) as exc_info:
        parse_d7b_response(text)
    assert exc_info.value.error_code == "forbidden_language"


# ---------------------------------------------------------------------------
# Refusal detection
# ---------------------------------------------------------------------------


def test_refusal_pattern_i_cannot():
    reasoning = (
        "I cannot evaluate this strategy because the factor set is "
        "unfamiliar and the conditions are too complex to analyze "
        "without additional domain context."
    )
    text = _make_response(reasoning=reasoning)
    with pytest.raises(D7bContentError) as exc_info:
        parse_d7b_response(text)
    assert exc_info.value.error_code == "refusal_detected"


def test_all_seven_refusal_patterns_detected():
    """Each of the 7 refusal patterns should be detected when present."""
    patterns = [
        "I cannot score this because the logic is unclear and the conditions "
        "are not well-defined in the context of this particular theme and setup",
        "I can't determine the plausibility of this strategy because the "
        "factor set is unfamiliar and the conditions are too abstract to parse",
        "I am unable to assess the strategy because the economic logic "
        "behind the entry and exit conditions is not self-evident to me now",
        "I refuse to score this strategy because the factor combination "
        "appears to be adversarial and potentially exploitative in nature",
        "I decline to evaluate this particular hypothesis because the "
        "structural logic appears malformed and not amenable to standard scoring",
        "The system cannot evaluate this strategy because the factor "
        "combination does not align with any recognized trading pattern",
        "The evaluator can not evaluate this strategy because the "
        "entry conditions use factors that have no economic justification",
    ]
    for reasoning in patterns:
        text = _make_response(reasoning=reasoning)
        with pytest.raises(D7bContentError) as exc_info:
            parse_d7b_response(text)
        assert exc_info.value.error_code == "refusal_detected", (
            f"Expected refusal_detected for: {reasoning[:60]}..."
        )
