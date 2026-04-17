"""D6 — Proposer prompt builder + leakage audit.

Constructs the exact prompt that will be sent to Sonnet in Stage 2. In
Stage 1 the prompt is built but never transmitted; its structure is
exercised by unit tests so the leakage contract is enforced before any
live tokens are spent.

**Leakage contract (hard, testable):**
No constructed prompt — system, user, or any substring thereof — may
contain any of the following (CLAUDE.md hard constraint):

- The 2022 regime-holdout year or any 2022 date substring
- The validation period (2024) or test period (2025) as date substrings
- The regime label ``"bear_2022"`` or identifier ``"regime_holdout"``
- Any holdout / validation / test metric name
  (``holdout_sharpe``, ``validation_return``, ``test_drawdown``, ...)
- Any leaderboard entry, ranking, or aggregate downstream result

The audit function :func:`audit_prompt_for_leakage` returns a list of
findings; an empty list means the prompt is clean. The D6 test suite
asserts emptiness across a range of contexts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from agents.proposer.interface import BatchContext
from agents.themes import THEMES
from factors.registry import FactorRegistry, get_registry


# ---------------------------------------------------------------------------
# Leakage-detection patterns (regex, case-insensitive)
# ---------------------------------------------------------------------------

# Each pattern is a raw regex string compiled once at import time.
# Word-boundary (\b) matching replaces the old substring approach so
# variants like "2022:", "2022.", "2022\n", "(2022)", or bare "2022"
# at EOL are all caught.
FORBIDDEN_PATTERNS: tuple[str, ...] = (
    # Year markers for holdout (2022), validation (2024), test (2025)
    r"\b2022\b",
    r"\b2024\b",
    r"\b2025\b",
    # Regime labels and identifiers
    r"\bbear[_\s]2022\b",
    r"\bregime[_\s]holdout\b",
    r"\bbear\s+(market|regime)\b",
    # Bare "holdout" catches compound variants not already covered
    r"\bholdout\b",
    # Leaked metric names (holdout / validation / test)
    r"\bholdout[_\s]sharpe\b",
    r"\bholdout[_\s]return\b",
    r"\bholdout[_\s]drawdown\b",
    r"\bholdout[_\s]max[_\s]dd\b",
    r"\bholdout[_\s]total[_\s]return\b",
    r"\bvalidation[_\s]sharpe\b",
    r"\bvalidation[_\s]return\b",
    r"\bvalidation[_\s]drawdown\b",
    r"\bvalidation\s+period\b",
    r"\btest[_\s]sharpe\b",
    r"\btest[_\s]return\b",
    r"\btest[_\s]drawdown\b",
    r"\btest\s+period\b",
    # Out-of-sample / OOS aliases
    r"\bout[_\s\-]of[_\s\-]sample\b",
    r"\boos[_\s\-]\w+",
    # Downstream aggregate artifacts
    r"\bleaderboard\b",
    r"\bdsr[_\s]threshold\b",
    r"\bdsr[_\s]failed\b",
    r"\bshortlisted\b",
    r"\bpending[_\s]dsr\b",
)

_COMPILED_FORBIDDEN: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE) for p in FORBIDDEN_PATTERNS
)

# Legacy alias kept for any downstream code that referenced the old name.
FORBIDDEN_SUBSTRINGS = FORBIDDEN_PATTERNS


@dataclass(frozen=True)
class ProposerPrompt:
    """Structured prompt returned by :func:`build_prompt`.

    ``system`` and ``user`` mirror the Anthropic SDK's message layout;
    ``factor_menu`` is separated so the Sonnet backend can decide
    whether to inline it or place it in a system-level cache breakpoint.
    """

    system: str
    user: str
    factor_menu: str

    def all_text(self) -> str:
        """Concatenate every prompt component for leakage auditing."""
        return "\n".join((self.system, self.user, self.factor_menu))


def _theme_for_slot(slot: int | None) -> str:
    if slot is None:
        return "unspecified"
    return THEMES[slot % len(THEMES)]


def build_prompt(
    context: BatchContext,
    *,
    registry: FactorRegistry | None = None,
    approved_examples: tuple[str, ...] = (),
    dedup_rate_so_far: float | None = None,
    critic_rejection_count_last_50: int | None = None,
    top_factors: tuple[str, ...] = (),
) -> ProposerPrompt:
    """Construct the Stage 2 Sonnet prompt from frozen-substrate inputs only.

    The caller is responsible for passing only DSL-only example
    strings and non-metric aggregate signals. This function does NOT
    redact; if the caller passes contaminated data it will appear in
    the output verbatim. The leakage audit is the testable safety net.

    DESIGN INVARIANT: approved_examples MUST be raw DSL JSON strings.
    No metrics, ranks, or numeric results may be interleaved. The D6
    test suite asserts this by building prompts across synthetic
    contexts and running :func:`audit_prompt_for_leakage`.
    """
    reg = registry or get_registry()
    factor_menu = reg.menu_for_prompt()

    system_lines = [
        "You are a quantitative researcher proposing BTC trading hypotheses.",
        "Respond ONLY with valid JSON matching the StrategyDSL schema.",
        "Your strategy MUST:",
        "  - Reference only factors from the menu provided by the caller.",
        "  - Use only these operators: "
        + ", ".join(context.allowed_operators) + ".",
        "  - Include a one-sentence economic rationale in `description`.",
        "  - Use long/flat positions only (`position_sizing: \"full_equity\"`).",
        "  - Respect the complexity budget: entry/exit each ≤ 3 condition "
        "groups, each group ≤ 4 conditions, max_hold_bars ≤ 720.",
        "",
        "You MAY NOT propose new factors, new operators, inline arithmetic, "
        "or any grammar outside the schema. Registry and grammar are frozen "
        "for this batch; factor or operator additions require explicit "
        "human review outside this loop.",
    ]
    system = "\n".join(system_lines)

    theme = _theme_for_slot(context.theme_slot)
    approved_block = (
        "\n".join(f"  - {ex}" for ex in approved_examples)
        if approved_examples
        else "  (none yet in this batch)"
    )
    top_factors_block = (
        ", ".join(top_factors) if top_factors else "(no signal yet)"
    )
    dedup_block = (
        f"{dedup_rate_so_far:.3f}" if dedup_rate_so_far is not None else "n/a"
    )
    reject_block = (
        str(critic_rejection_count_last_50)
        if critic_rejection_count_last_50 is not None
        else "n/a"
    )

    user_lines = [
        "Batch context:",
        f"  - batch_id: {context.batch_id}",
        f"  - position: {context.position}/{context.batch_size}",
        f"  - theme (rotating): {theme}",
        "",
        "Recent batch signal (compact, no raw metrics):",
        f"  - dedup rate so far: {dedup_block}",
        f"  - top factors by frequency: {top_factors_block}",
        f"  - critic rejections in last 50: {reject_block}",
        "  - up to 3 example approved hypotheses (DSL only, no metrics):",
        approved_block,
        "",
        f"Propose hypothesis #{context.position}.",
    ]
    user = "\n".join(user_lines)

    return ProposerPrompt(system=system, user=user, factor_menu=factor_menu)


def audit_prompt_for_leakage(
    prompt: ProposerPrompt | str,
    *,
    forbidden: tuple[str, ...] = FORBIDDEN_PATTERNS,
) -> list[str]:
    """Return forbidden patterns that match anywhere in the prompt text.

    An empty list means the prompt is clean. Each entry is the regex
    pattern string that fired. The check is case-insensitive and scans
    the full concatenated prompt text (``system + user + factor_menu``).

    If ``forbidden`` is overridden by the caller (e.g. with additional
    patterns), those strings are compiled on the fly.
    """
    text = prompt.all_text() if isinstance(prompt, ProposerPrompt) else prompt
    if forbidden is FORBIDDEN_PATTERNS:
        compiled = _COMPILED_FORBIDDEN
    else:
        compiled = tuple(re.compile(p, re.IGNORECASE) for p in forbidden)
    return [p.pattern for p in compiled if p.search(text)]


__all__ = [
    "FORBIDDEN_PATTERNS",
    "FORBIDDEN_SUBSTRINGS",
    "ProposerPrompt",
    "THEMES",
    "audit_prompt_for_leakage",
    "build_prompt",
]
