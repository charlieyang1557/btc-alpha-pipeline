"""D7b response parser (D7 Stage 2a).

Robust fence/prose stripping reused from the D6 Stage 2a lesson:
Sonnet sometimes wraps JSON in markdown code fences or adds a prose
preamble/postamble. The parser strips both and validates strict schema.

Error codes (LOCKED — must match agents/critic/d7b_live.py taxonomy):

    - ``json_decode``
    - ``schema_extra_keys``
    - ``schema_missing_keys``
    - ``schema_out_of_range``
    - ``schema_reasoning_length``
    - ``forbidden_language``
    - ``refusal_detected``

Every path that fails raises :class:`D7bContentError` with a structured
``error_code`` and a sanitized ``detail``. The parser never returns
partially-valid output.
"""

from __future__ import annotations

import json
import re

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from agents.critic.d7b_prompt import D7B_FORBIDDEN_TERMS


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class D7bContentError(Exception):
    """Content-level parse/schema/policy failure."""

    def __init__(self, error_code: str, detail: str):
        super().__init__(f"{error_code}: {detail}")
        self.error_code = error_code
        self.detail = detail


# ---------------------------------------------------------------------------
# Strict schema
# ---------------------------------------------------------------------------


class StrictD7bResponse(BaseModel):
    """Schema for a valid D7b response.

    Exactly four top-level keys: the three score keys + ``reasoning``.
    ``extra='forbid'`` rejects any additional top-level key.
    """

    model_config = ConfigDict(extra="forbid")

    semantic_plausibility: float = Field(ge=0.0, le=1.0)
    semantic_theme_alignment: float = Field(ge=0.0, le=1.0)
    structural_variant_risk: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(min_length=100, max_length=800)


# ---------------------------------------------------------------------------
# Fence + prose stripping
# ---------------------------------------------------------------------------


_FENCE_RE = re.compile(
    r"^\s*```(?:json|JSON)?\s*\n(.*?)\n```\s*$",
    re.DOTALL,
)


def _strip_fences(text: str) -> str:
    """Remove a single wrapping ```json...``` or ```...``` fence."""
    m = _FENCE_RE.match(text)
    if m:
        return m.group(1)
    return text


def _strip_prose(text: str) -> str:
    """Strip prose preamble/postamble around a JSON object.

    Finds the first ``{`` and its matching ``}`` and returns the substring
    between them (inclusive). If no matched pair exists, returns the
    original text untouched.
    """
    first = text.find("{")
    if first < 0:
        return text
    depth = 0
    for i in range(first, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[first : i + 1]
    return text


# ---------------------------------------------------------------------------
# Forbidden-language + refusal detection
# ---------------------------------------------------------------------------


def _word_boundary_pattern(term: str) -> re.Pattern:
    """Build a case-insensitive word-boundary regex for a term.

    For multi-word phrases like ``"should be used"``, collapse internal
    whitespace to a ``\\s+`` class.
    """
    escaped = re.escape(term)
    # ``re.escape`` turns ``" "`` into ``"\\ "``; relax to whitespace.
    escaped = escaped.replace(r"\ ", r"\s+")
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


_FORBIDDEN_PATTERNS: dict[str, re.Pattern] = {
    t: _word_boundary_pattern(t) for t in D7B_FORBIDDEN_TERMS
}


# Refusal patterns (case-insensitive whole-phrase, not strict word-boundary
# because these are idiomatic fragments).
_REFUSAL_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\bi cannot\b", re.IGNORECASE),
    re.compile(r"\bi can't\b", re.IGNORECASE),
    re.compile(r"\bunable to\b", re.IGNORECASE),
    re.compile(r"\brefuse to\b", re.IGNORECASE),
    re.compile(r"\bdecline to\b", re.IGNORECASE),
    re.compile(r"\bcannot evaluate\b", re.IGNORECASE),
    re.compile(r"\bcan not evaluate\b", re.IGNORECASE),
)


def _scan_forbidden(text: str) -> tuple[str, int] | None:
    """Scan for forbidden terms. Returns ``(term, position)`` if found."""
    for term, pattern in _FORBIDDEN_PATTERNS.items():
        m = pattern.search(text)
        if m:
            return (term, m.start())
    return None


def _scan_refusal(text: str) -> tuple[str, int] | None:
    """Scan for refusal patterns. Returns ``(pattern, position)`` if found."""
    for pattern in _REFUSAL_PATTERNS:
        m = pattern.search(text)
        if m:
            return (m.group(0), m.start())
    return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


_SCORE_KEYS: frozenset[str] = frozenset({
    "semantic_plausibility",
    "semantic_theme_alignment",
    "structural_variant_risk",
})

_ALL_REQUIRED: frozenset[str] = _SCORE_KEYS | frozenset({"reasoning"})


def parse_d7b_response(raw_text: str) -> tuple[dict[str, float], str]:
    """Parse a live D7b response into ``(scores, reasoning)``.

    Raises :class:`D7bContentError` on any failure with a structured
    ``error_code``. Never returns partially-valid output.
    """
    text = raw_text.strip()
    text = _strip_fences(text)
    text = _strip_prose(text)

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise D7bContentError(
            "json_decode",
            str(exc)[:160],
        ) from exc

    if not isinstance(payload, dict):
        raise D7bContentError(
            "json_decode",
            f"top-level must be object, got {type(payload).__name__}",
        )

    keys = set(payload.keys())
    extra = keys - _ALL_REQUIRED
    if extra:
        raise D7bContentError(
            "schema_extra_keys",
            f"unexpected key(s): {sorted(extra)}",
        )
    missing = _ALL_REQUIRED - keys
    if missing:
        raise D7bContentError(
            "schema_missing_keys",
            f"missing key(s): {sorted(missing)}",
        )

    try:
        validated = StrictD7bResponse(**payload)
    except ValidationError as exc:
        # Classify into the taxonomy.
        errors = exc.errors()
        # Prefer the first error for detail.
        first = errors[0] if errors else {}
        loc = first.get("loc", ())
        err_type = first.get("type", "")
        msg = first.get("msg", str(exc))

        if loc and loc[0] == "reasoning":
            code = "schema_reasoning_length"
        elif "greater_than_equal" in err_type or "less_than_equal" in err_type:
            code = "schema_out_of_range"
        elif "extra_forbidden" in err_type:
            code = "schema_extra_keys"
        elif "missing" in err_type:
            code = "schema_missing_keys"
        else:
            # Default: range/type mismatch on a score field.
            code = "schema_out_of_range"

        loc_str = ".".join(str(p) for p in loc) if loc else "?"
        raise D7bContentError(
            code,
            f"{loc_str}: {msg}"[:160],
        ) from exc

    reasoning = validated.reasoning

    hit = _scan_forbidden(reasoning)
    if hit is not None:
        term, pos = hit
        raise D7bContentError(
            "forbidden_language",
            f"{term!r} at position {pos}",
        )

    refusal_hit = _scan_refusal(reasoning)
    if refusal_hit is not None:
        phrase, pos = refusal_hit
        raise D7bContentError(
            "refusal_detected",
            f"{phrase!r} at position {pos}",
        )

    scores = {
        "semantic_plausibility": validated.semantic_plausibility,
        "semantic_theme_alignment": validated.semantic_theme_alignment,
        "structural_variant_risk": validated.structural_variant_risk,
    }
    return scores, reasoning


__all__ = [
    "D7bContentError",
    "StrictD7bResponse",
    "parse_d7b_response",
]
