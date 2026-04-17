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

from dataclasses import dataclass

from agents.proposer.interface import BatchContext
from factors.registry import FactorRegistry, get_registry


# Canonical D8 theme list. D6 accepts ``theme_slot`` from
# :class:`BatchContext` and indexes this list; it does NOT decide
# rotation strategy. See CLAUDE.md "Theme rotation" rule.
THEMES: tuple[str, ...] = (
    "momentum",
    "mean_reversion",
    "volatility_regime",
    "volume_divergence",
    "calendar_effect",
    "multi_factor_combination",
)


# Substrings whose appearance anywhere in a constructed prompt
# constitutes leakage. Matched case-insensitively.
FORBIDDEN_SUBSTRINGS: tuple[str, ...] = (
    # Holdout / validation / test period date markers
    "2022-",
    "2022/",
    "2022 ",
    "bear_2022",
    "regime_holdout",
    "regime holdout",
    "2024-",
    "2024/",
    "2024 ",
    "2025-",
    "2025/",
    "2025 ",
    # Leaked metric names
    "holdout_sharpe",
    "holdout_return",
    "holdout_drawdown",
    "holdout_max_dd",
    "holdout_total_return",
    "validation_sharpe",
    "validation_return",
    "validation_drawdown",
    "test_sharpe",
    "test_return",
    "test_drawdown",
    # Downstream aggregate artifacts
    "leaderboard",
    "dsr_threshold",
    "dsr_failed",
    "shortlisted",
)


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
    forbidden: tuple[str, ...] = FORBIDDEN_SUBSTRINGS,
) -> list[str]:
    """Return a list of forbidden substrings that appear in the prompt.

    An empty list means the prompt is clean. The check is
    case-insensitive and scans the full concatenated prompt text
    (``system + user + factor_menu``). A non-empty return value is a
    hard leak and the test suite asserts against it.
    """
    text = prompt.all_text() if isinstance(prompt, ProposerPrompt) else prompt
    lowered = text.lower()
    return [s for s in forbidden if s.lower() in lowered]


__all__ = [
    "FORBIDDEN_SUBSTRINGS",
    "ProposerPrompt",
    "THEMES",
    "audit_prompt_for_leakage",
    "build_prompt",
]
