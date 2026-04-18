"""D7b prompt builder + leakage audit (D7 Stage 2a).

CONTRACT BOUNDARY: No ordinal identity or timestamps may enter the
prompt. See Deliverable 2 exclusion list.

CONTRACT: The prompt template is frozen within a run. No post-hoc
patching after inspecting a response. Prompt changes are a new-stage
decision, not a cleanup.

``prior_factor_sets`` serialization (LOCKED):
    - deduplicated
    - alphabetical within each set
    - first-seen order across the list
    - no occurrence counts, no call indices, no theme labels
    - empty list renders as exactly ``_(none)_``
"""

from __future__ import annotations

import json
import re

from agents.critic.batch_context import BatchContext
from strategies.dsl import StrategyDSL


# ---------------------------------------------------------------------------
# Forbidden-language list (shared with parser; whole-word case-insensitive)
# ---------------------------------------------------------------------------

D7B_FORBIDDEN_TERMS: frozenset[str] = frozenset({
    "accept", "reject", "approve", "approved", "veto",
    "pass", "fail", "passing", "failing",
    "recommend", "recommended", "recommendation",
    "should be used", "should not be used",
    "do not use", "keep", "discard",
    "green light", "red flag", "go-ahead", "go ahead",
})


# ---------------------------------------------------------------------------
# The frozen prompt template (LOCKED)
# ---------------------------------------------------------------------------

_PROMPT_TEMPLATE = """You are a quantitative research critic evaluating a proposed trading strategy
hypothesis. Your task is to score it on three semantic dimensions.

## Input

You will receive:
- A strategy DSL (already validated against a strict grammar \u2014 do not comment on syntax)
- The theme this strategy was proposed under
- The theme's hint factor vocabulary
- A list of structurally distinct factor sets seen in prior hypotheses within the same research batch

## Your task

Produce a single JSON object with exactly four top-level keys:

```
{{
  "semantic_plausibility": 0.0000,
  "semantic_theme_alignment": 0.0000,
  "structural_variant_risk": 0.0000,
  "reasoning": "..."
}}
```

All three score values must be floats in [0.0, 1.0], rounded to 4 decimal places.
The reasoning value must be a single string of 100 to 400 characters.
(Length is measured in Unicode characters, not tokens.)

### Score definitions

1. **semantic_plausibility** (0.0 = low, 1.0 = high)
   Is the strategy's internal logic coherent? Does the entry/exit condition
   structure support a defensible trading story?

2. **semantic_theme_alignment** (0.0 = low, 1.0 = high)
   Does the strategy's description and factor choice align with the economic
   intuition of the stated theme?

3. **structural_variant_risk** (0.0 = LOW risk, 1.0 = HIGH risk)
   \u26a0\ufe0f  This axis is REVERSED relative to the other two. \u26a0\ufe0f
   Does this look like a threshold or operator tweak of a factor set already
   present in the prior list, or a genuinely different structural bet?
   - 0.0 = structurally distinct from all priors (LOW risk of being a shallow variant)
   - 1.0 = clearly a shallow variant of a prior factor set (HIGH risk)

### Reasoning contract

Your reasoning MUST:
- Describe the logic behind each of the three scores
- Be analytical and descriptive
- Reference specific factors, operators, or structural choices in the DSL

### Forbidden-language contract (ENUMERATION BLOCK)

Your reasoning MUST NOT use any of the following words or phrases:
{forbidden_language_list}

Your reasoning MUST NOT:
- Defer to a human or other system
- Refuse to score

### Output contract

- Respond with a single JSON object
- No markdown code fences (no ```json, no ```)
- No preamble, no postamble, no explanation text outside the JSON
- Exactly four top-level keys: the three score keys and "reasoning"
- Any additional top-level keys, renamed keys, or missing keys will be
  treated as a contract violation

### Refusal preemption

You must produce all three numerical scores and a reasoning string.
If your confidence is low, use conservative mid-range scores (around 0.5)
and explain the uncertainty in the reasoning field. "I cannot evaluate this"
is NOT a valid response. Refusal to score is a contract violation.

---

## Strategy DSL to evaluate

This DSL has already passed strict syntactic validation. Focus only on
semantic, economic, and structural logic. Do not comment on JSON syntax.

```
{pretty_printed_dsl}
```

## Theme

{theme}

### Theme hint factors

The following factors are associated with this theme:
{theme_hint_factors_bulleted}

## Prior factor sets in this batch

The following structurally distinct factor sets have been proposed earlier
in the same batch. They are listed in order of first appearance.

{prior_factor_sets_bulleted}

---

Produce the JSON object now."""


# ---------------------------------------------------------------------------
# Interpolation helpers
# ---------------------------------------------------------------------------


def _pretty_print_dsl(dsl: StrategyDSL) -> str:
    """Pretty-print DSL with indent=2, preserving declared field order."""
    return json.dumps(
        dsl.model_dump(),
        indent=2,
        sort_keys=False,
        ensure_ascii=False,
    )


def _format_theme_hint_factors(theme_hints: dict, theme: str) -> str:
    """Render the theme's hint factor set as a bulleted, alphabetical list."""
    factors = theme_hints.get(theme, frozenset())
    if not factors:
        return "_(none)_"
    return "\n".join(f"- {f}" for f in sorted(factors))


def _dedup_prior_factor_sets(
    prior_factor_sets: tuple[tuple[str, ...], ...],
) -> list[tuple[str, ...]]:
    """Dedup while preserving first-seen order; sort factors within each set."""
    seen: set[tuple[str, ...]] = set()
    out: list[tuple[str, ...]] = []
    for fs in prior_factor_sets:
        key = tuple(sorted(fs))
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _format_prior_factor_sets(
    prior_factor_sets: tuple[tuple[str, ...], ...],
) -> str:
    """Render prior factor sets per the LOCKED rules.

    - deduplicated (on the sorted-tuple representation)
    - alphabetical within each set
    - first-seen order across the list
    - no counts, no indices, no themes
    - empty renders exactly ``_(none)_``
    """
    deduped = _dedup_prior_factor_sets(prior_factor_sets)
    if not deduped:
        return "_(none)_"
    lines = []
    for fs in deduped:
        factors_str = ", ".join(fs)
        lines.append(f"- {{{factors_str}}}")
    return "\n".join(lines)


def _format_forbidden_language_list() -> str:
    """Render forbidden terms as a bulleted list (for the enumeration block)."""
    # Deterministic alphabetical order.
    terms = sorted(D7B_FORBIDDEN_TERMS)
    return "\n".join(f'- "{t}"' for t in terms)


# ---------------------------------------------------------------------------
# Public: build_d7b_prompt
# ---------------------------------------------------------------------------


def build_d7b_prompt(
    dsl: StrategyDSL,
    theme: str,
    batch_context: BatchContext,
) -> str:
    """Construct the frozen D7b user-message prompt.

    The prompt is a single user-message string. There is no system prompt.
    """
    pretty_dsl = _pretty_print_dsl(dsl)
    theme_hint_bulleted = _format_theme_hint_factors(
        batch_context.theme_hints, theme,
    )
    prior_bulleted = _format_prior_factor_sets(batch_context.prior_factor_sets)
    forbidden_bulleted = _format_forbidden_language_list()

    return _PROMPT_TEMPLATE.format(
        forbidden_language_list=forbidden_bulleted,
        pretty_printed_dsl=pretty_dsl,
        theme=theme,
        theme_hint_factors_bulleted=theme_hint_bulleted,
        prior_factor_sets_bulleted=prior_bulleted,
    )


# ---------------------------------------------------------------------------
# Leakage audit (LOCKED)
# ---------------------------------------------------------------------------


# Substrings that must not appear anywhere in the rendered prompt.
_EXCLUDED_SUBSTRINGS: tuple[str, ...] = (
    "batch_id",
    "batch_position",
    "call_index",
    "holdout",
    "validation_start",
    "validation_end",
    "validation_sharpe",
    "validation_return",
    "test_start",
    "test_end",
    "backtest_result",
    "sharpe",
    "total_return",
    "max_drawdown",
    "equity_curve",
    "pnl",
    "profit",
    "approved_examples",
    # D7a score key names
    "theme_coherence",
    "structural_novelty",
    "default_momentum_fallback",
    "complexity_appropriateness",
    # D7a flag names
    "empty_factor_set",
    "thin_theme_momentum_bleed",
    "factor_set_in_top3_repeated",
    "theme_anchor_missing",
    "description_length_near_limit",
    "n_conditions_heavy",
)

# UUID pattern (8-4-4-4-12 hex).
_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)

# ISO year prefixes that indicate date leakage.
_YEAR_RE = re.compile(r"\b(2022|2023|2024|2025|2026)-\d{2}-\d{2}")

# Directive words that may appear ONLY inside the forbidden-language block.
# Uses exact forms rather than word-root + \w* to avoid false positives
# on normal English (e.g., "passed" in "has already passed validation").
_DIRECTIVE_WORDS_RE = re.compile(
    r"\b(recommend|recommended|recommendation|approve|approved|reject|rejected"
    r"|accept|accepted|pass\b|fail\b|passing|failing)\b",
    re.IGNORECASE,
)


def _strip_forbidden_language_block(prompt_text: str) -> str:
    """Remove the forbidden-language enumeration block for leakage audit.

    The forbidden-language contract block deliberately lists directive
    words verbatim. The audit must exempt those lines so they do not
    trigger the directive-leakage rule.
    """
    pattern = re.compile(
        r"### Forbidden-language contract \(ENUMERATION BLOCK\).*?### Output contract",
        re.DOTALL,
    )
    return pattern.sub("### Output contract", prompt_text)


def run_leakage_audit(prompt_text: str) -> str | None:
    """Run the exclusion audit on a built prompt.

    Returns:
        ``None`` if the audit passes. Otherwise a human-readable detail
        string describing the first hit. Caller raises with this detail.
    """
    # UUIDs anywhere in the prompt
    m = _UUID_RE.search(prompt_text)
    if m:
        return f"UUID leaked: {m.group(0)}"

    # Year-prefixed dates
    m = _YEAR_RE.search(prompt_text)
    if m:
        return f"date leaked: {m.group(0)}"

    # Substring exclusions
    lower = prompt_text.lower()
    for forbidden in _EXCLUDED_SUBSTRINGS:
        if forbidden.lower() in lower:
            return f"excluded substring leaked: {forbidden!r}"

    # Directive words outside the enumeration block
    stripped = _strip_forbidden_language_block(prompt_text)
    m = _DIRECTIVE_WORDS_RE.search(stripped)
    if m:
        return (
            f"directive language outside enumeration block: "
            f"{m.group(0)!r} at pos {m.start()}"
        )

    return None


__all__ = [
    "D7B_FORBIDDEN_TERMS",
    "build_d7b_prompt",
    "run_leakage_audit",
]
