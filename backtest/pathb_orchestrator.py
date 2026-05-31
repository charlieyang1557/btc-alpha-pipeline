# backtest/pathb_orchestrator.py
"""Path B verdict orchestrator (ADVISORY).

Pure composition over injected stage callables: per-candidate gauntlet ->
holdout_sharpe; build integrity-gated moments; DSR-FWER at N*=3; train-only
per-leg mechanism sanity; earned-negative taxonomy; A-escalation advisory.
The binding earned-negative read + A-escalation remain a Charlie register.
"""
from __future__ import annotations

from typing import Any, Callable

from backtest.pathb_dsr_fwer import run_dsr_fwer, PATHB_N_STAR
from backtest.pathb_earned_negative import assemble_evidence
from backtest.pathb_escalation import a_escalation_advisory


def run_pathb_verdict(
    *,
    hypotheses: dict[str, Any],
    run_gauntlet: Callable[[str, Any], dict],
    build_moments: Callable[[dict], list],
    run_dsr: Callable[[list], dict] = run_dsr_fwer,
    per_leg: Callable[[], dict],
    step0_lifted_any: bool,
) -> dict[str, Any]:
    """Compose the advisory verdict pipeline. Returns the evidence bundle.

    Args:
        hypotheses: Mapping of hypothesis key (e.g. ``"H1"``) to DSL object.
        run_gauntlet: Callable ``(key, dsl) -> {"holdout_sharpe": float, ...}``
            for the Tier-5 holdout gauntlet per candidate.
        build_moments: Callable ``(holdouts_dict) -> list[CandidateMoments]``
            assembling moments from the produced holdouts.
        run_dsr: Callable ``(cms) -> {"survivors", "rows", "n_star"}``
            running DSR-FWER on moments; defaults to ``run_dsr_fwer``.
        per_leg: Zero-arg callable returning the per-leg/per-hypothesis sanity
            dict (produced on train-only data by ``compute_per_leg_mechanism``).
        step0_lifted_any: True iff Step-0 cost re-score lifted any dead candidate
            above 0 (the §9 A-escalation second prong).

    Returns:
        Evidence bundle with keys: ``holdouts``, ``n_tier5_pass``, ``n_dsr_pass``,
        ``dsr``, ``per_leg``, ``taxonomy`` (assemble_evidence bundle),
        ``escalation`` (a_escalation_advisory bundle).
    """
    holdouts = {key: run_gauntlet(key, dsl) for key, dsl in hypotheses.items()}
    n_tier5_pass = sum(1 for h in holdouts.values() if h["holdout_sharpe"] > 0)

    cms = build_moments(holdouts)
    dsr = run_dsr(cms) if cms else {"survivors": [], "rows": [], "n_star": PATHB_N_STAR, "n_candidates": 0}
    n_dsr_pass = len(dsr["survivors"])

    sanity = per_leg()
    taxonomy = assemble_evidence(
        per_leg=sanity,
        n_tier5_pass=n_tier5_pass,
        n_dsr_pass=n_dsr_pass,
        step0_promotion_side_effect=False,
    )
    escalation = a_escalation_advisory(
        taxonomy["advisory_taxonomy"], step0_lifted_any=step0_lifted_any
    )
    return {
        "holdouts": holdouts,
        "n_tier5_pass": n_tier5_pass,
        "n_dsr_pass": n_dsr_pass,
        "dsr": dsr,
        "per_leg": sanity,
        "taxonomy": taxonomy,
        "escalation": escalation,
    }
