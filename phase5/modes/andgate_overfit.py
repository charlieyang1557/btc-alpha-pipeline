"""§2.d AND-gate overfit — TOST equivalence test at Binomial-exact noise scale.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §2.d (sealed at
20252cc; D3''' lock). Two One-Sided Tests (TOST) primary at Approach C;
Approach A Jaccard supplements at ±1σ perturbation. Pre-execution gate:
canonical-fresh ≡ pre-computed-audit cross-validation across 993 × 4 = 3972
pass-pattern bits (FB #16).
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from phase5.io import (
    ANDGATE_MAX_DRAWDOWN,
    ANDGATE_MIN_SHARPE,
    ANDGATE_MIN_TOTAL_RETURN,
    ANDGATE_MIN_TOTAL_TRADES,
    PHASE2C_15_REGIMES,
)

ALPHA = 0.05
EPSILON_K = 2  # k=2 in ε = k·√(N·p·(1−p)) per sealed §2.d substantive prior
PERTURBATION_K = 1  # k=1 in Approach A σ-of-distribution perturbation


def _candidate_passes_canonical_fresh(metrics: dict) -> tuple[bool | None, dict[str, bool | None]]:
    """Compute canonical-fresh AND-gate sub-criterion evaluation.

    Returns (overall_pass, per_field_pass_dict). overall_pass is None if any
    input field is non-finite/missing; per-field None if that specific field
    is missing.
    """
    sharpe = metrics.get("sharpe_ratio")
    dd = metrics.get("max_drawdown")
    ret = metrics.get("total_return")
    trades = metrics.get("total_trades")

    def _ok_finite(v):
        return isinstance(v, (int, float)) and np.isfinite(v)

    per_field = {
        "sharpe_ratio": (sharpe >= ANDGATE_MIN_SHARPE) if _ok_finite(sharpe) else None,
        "max_drawdown": (dd <= ANDGATE_MAX_DRAWDOWN) if _ok_finite(dd) else None,
        "total_return": (ret >= ANDGATE_MIN_TOTAL_RETURN) if _ok_finite(ret) else None,
        "total_trades": (trades >= ANDGATE_MIN_TOTAL_TRADES) if _ok_finite(trades) else None,
    }
    if any(v is None for v in per_field.values()):
        return (None, per_field)
    return (all(per_field.values()), per_field)


def _verify_audit_consistency(
    broader_universe_per_regime: dict[str, dict[str, dict]],
) -> dict[str, Any]:
    """Pre-execution gate: canonical-fresh ≡ pre-computed-audit per FB #16.

    Cross-validates canonical-fresh AND-gate evaluation against the top-level
    holdout_passed field stored in each per-candidate holdout_summary.json.
    Mismatch at any candidate × regime bit suspends §2.d execution.
    """
    discrepancies: list[dict[str, Any]] = []
    total_bits = 0
    matched_bits = 0
    for regime in PHASE2C_15_REGIMES:
        for h, summary in broader_universe_per_regime[regime].items():
            metrics = summary.get("holdout_metrics", {})
            audit = summary.get("holdout_passed")
            canonical, _per_field = _candidate_passes_canonical_fresh(metrics)
            total_bits += 1
            if canonical is None and audit is None:
                # Both undefined → consistent absence.
                matched_bits += 1
                continue
            if canonical == audit:
                matched_bits += 1
            else:
                discrepancies.append(
                    {
                        "hypothesis_hash": h,
                        "regime": regime,
                        "canonical_fresh": canonical,
                        "audit_stored": audit,
                        "metrics": metrics,
                    }
                )
    return {
        "total_bits": total_bits,
        "matched_bits": matched_bits,
        "discrepancy_count": len(discrepancies),
        "discrepancies": discrepancies,
        "all_match": len(discrepancies) == 0,
    }


def _per_regime_pass_rate(
    regime_summary: dict[str, dict],
) -> tuple[float, int, int]:
    """Return (p_r, count_pass_r, count_finite_r) for one regime."""
    count_finite = 0
    count_pass = 0
    for h, summary in regime_summary.items():
        metrics = summary.get("holdout_metrics", {})
        canonical, _ = _candidate_passes_canonical_fresh(metrics)
        if canonical is None:
            continue
        count_finite += 1
        if canonical:
            count_pass += 1
    if count_finite == 0:
        return (float("nan"), 0, 0)
    return (count_pass / count_finite, count_pass, count_finite)


def _intersection_count(
    broader_universe_per_regime: dict[str, dict[str, dict]],
) -> int:
    """N = candidates with all 4 AND-gate input fields finite in ALL 4 regimes."""
    finite_per_regime: dict[str, set[str]] = {}
    for regime, m in broader_universe_per_regime.items():
        finite_per_regime[regime] = set()
        for h, summary in m.items():
            metrics = summary.get("holdout_metrics", {})
            canonical, _ = _candidate_passes_canonical_fresh(metrics)
            if canonical is not None:
                finite_per_regime[regime].add(h)
    intersection = set.intersection(*finite_per_regime.values())
    return len(intersection)


def _all_regimes_pass(
    summaries_for_h: dict[str, dict],
    field_thresholds: dict[str, dict[str, float]] | None = None,
) -> bool | None:
    """Return True if candidate passes AND-gate in ALL regimes; None if any input non-finite.

    field_thresholds optional override per regime; if None, uses sealed
    standard thresholds.
    """
    for regime, summary in summaries_for_h.items():
        metrics = summary.get("holdout_metrics", {})
        if field_thresholds is None:
            canonical, _ = _candidate_passes_canonical_fresh(metrics)
            if canonical is None:
                return None
            if not canonical:
                return False
        else:
            t = field_thresholds[regime]
            sharpe = metrics.get("sharpe_ratio")
            dd = metrics.get("max_drawdown")
            ret = metrics.get("total_return")
            trades = metrics.get("total_trades")
            for v in (sharpe, dd, ret, trades):
                if not (isinstance(v, (int, float)) and np.isfinite(v)):
                    return None
            ok = (
                sharpe >= t["min_sharpe"]
                and dd <= t["max_drawdown"]
                and ret >= t["min_total_return"]
                and trades >= t["min_total_trades"]
            )
            if not ok:
                return False
    return True


def _sigma_per_field_per_regime(
    broader_universe_per_regime: dict[str, dict[str, dict]],
) -> dict[str, dict[str, float]]:
    """Per-regime standard deviation per AND-gate input metric (for Approach A perturbation)."""
    out: dict[str, dict[str, float]] = {}
    for regime, m in broader_universe_per_regime.items():
        sharpes, dds, rets, trades = [], [], [], []
        for h, summary in m.items():
            metrics = summary.get("holdout_metrics", {})
            s = metrics.get("sharpe_ratio")
            d = metrics.get("max_drawdown")
            r = metrics.get("total_return")
            t = metrics.get("total_trades")
            if all(isinstance(v, (int, float)) and np.isfinite(v) for v in (s, d, r, t)):
                sharpes.append(s)
                dds.append(d)
                rets.append(r)
                trades.append(t)
        out[regime] = {
            "sharpe": float(np.std(sharpes, ddof=1)),
            "max_drawdown": float(np.std(dds, ddof=1)),
            "total_return": float(np.std(rets, ddof=1)),
            "total_trades": float(np.std(trades, ddof=1)),
        }
    return out


def _perturbed_cohort(
    broader_universe_per_regime: dict[str, dict[str, dict]],
    sigmas: dict[str, dict[str, float]],
    direction: str,  # "stricter" or "looser"
) -> set[str]:
    """Compute perturbed cohort (candidates passing perturbed AND-gate in all 4 regimes)."""
    if direction not in ("stricter", "looser"):
        raise ValueError(direction)
    sign = +1.0 if direction == "stricter" else -1.0
    thresholds: dict[str, dict[str, float]] = {}
    for regime, s in sigmas.items():
        # Stricter: raise floor + lower ceiling; looser: reverse.
        thresholds[regime] = {
            "min_sharpe": ANDGATE_MIN_SHARPE + sign * PERTURBATION_K * s["sharpe"],
            "max_drawdown": ANDGATE_MAX_DRAWDOWN - sign * PERTURBATION_K * s["max_drawdown"],
            "min_total_return": ANDGATE_MIN_TOTAL_RETURN + sign * PERTURBATION_K * s["total_return"],
            "min_total_trades": max(
                0.0,
                ANDGATE_MIN_TOTAL_TRADES + sign * PERTURBATION_K * s["total_trades"],
            ),
        }
        # Domain-validity clipping.
        thresholds[regime]["max_drawdown"] = max(0.0, min(1.0, thresholds[regime]["max_drawdown"]))

    hashes = set(broader_universe_per_regime[PHASE2C_15_REGIMES[0]].keys())
    for regime, m in broader_universe_per_regime.items():
        hashes &= set(m.keys())

    cohort: set[str] = set()
    for h in hashes:
        per_regime = {regime: broader_universe_per_regime[regime][h] for regime in PHASE2C_15_REGIMES}
        ok = _all_regimes_pass(per_regime, thresholds)
        if ok:
            cohort.add(h)
    return cohort


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def _cramers_v_pairwise(
    broader_universe_per_regime: dict[str, dict[str, dict]],
) -> dict[str, float]:
    """Pairwise Cramér's V on per-regime pass indicators (descriptive supplement)."""
    out: dict[str, float] = {}
    # Build pass-per-regime per candidate (drop any with NaN in any regime).
    hashes = set(broader_universe_per_regime[PHASE2C_15_REGIMES[0]].keys())
    for regime, m in broader_universe_per_regime.items():
        hashes &= set(m.keys())
    pass_matrix: dict[str, dict[str, bool]] = {}
    for h in hashes:
        per_regime_pass: dict[str, bool] = {}
        keep = True
        for regime in PHASE2C_15_REGIMES:
            metrics = broader_universe_per_regime[regime][h].get("holdout_metrics", {})
            canonical, _ = _candidate_passes_canonical_fresh(metrics)
            if canonical is None:
                keep = False
                break
            per_regime_pass[regime] = canonical
        if keep:
            pass_matrix[h] = per_regime_pass

    regimes = PHASE2C_15_REGIMES
    n = len(pass_matrix)
    for i, r1 in enumerate(regimes):
        for r2 in regimes[i + 1 :]:
            a = np.array([pass_matrix[h][r1] for h in pass_matrix], dtype=int)
            b = np.array([pass_matrix[h][r2] for h in pass_matrix], dtype=int)
            # 2x2 contingency.
            ct = np.array(
                [
                    [int(((a == 0) & (b == 0)).sum()), int(((a == 0) & (b == 1)).sum())],
                    [int(((a == 1) & (b == 0)).sum()), int(((a == 1) & (b == 1)).sum())],
                ]
            )
            chi2, _, _, _ = stats.chi2_contingency(ct, correction=False)
            v = math.sqrt(chi2 / (n * (min(ct.shape) - 1))) if n > 0 else float("nan")
            out[f"{r1}_vs_{r2}"] = float(v)
    return out


def _pass_pattern_distribution(
    broader_universe_per_regime: dict[str, dict[str, dict]],
) -> dict[str, int]:
    """16-cell 2^4 pass-pattern distribution per sealed §2.d descriptive supplement.

    NOT eligible for post-hoc reinterpretation per D2''' Point 2 lock.
    """
    out: dict[str, int] = {}
    hashes = set(broader_universe_per_regime[PHASE2C_15_REGIMES[0]].keys())
    for regime, m in broader_universe_per_regime.items():
        hashes &= set(m.keys())
    for h in hashes:
        bits: list[str] = []
        skip = False
        for regime in PHASE2C_15_REGIMES:
            metrics = broader_universe_per_regime[regime][h].get("holdout_metrics", {})
            canonical, _ = _candidate_passes_canonical_fresh(metrics)
            if canonical is None:
                skip = True
                break
            bits.append("1" if canonical else "0")
        if skip:
            continue
        key = "".join(bits)
        out[key] = out.get(key, 0) + 1
    return out


def compute_andgate_overfit(
    cohort_a: pd.DataFrame,
    broader_universe_per_regime: dict[str, dict[str, dict]],
) -> dict[str, Any]:
    """Fire §2.d AND-gate-overfit indicator per sealed prose.

    Pre-execution gate: canonical-fresh ≡ pre-computed-audit consistency
    across 993 × 4 pass-pattern bits. If mismatch detected, suspends §2.d
    primary judgment per sealed prose.
    """
    audit = _verify_audit_consistency(broader_universe_per_regime)
    if not audit["all_match"]:
        return {
            "mode": "§2.d AND-gate overfit",
            "detected": None,
            "execution_suspended": True,
            "suspension_cause": "audit_consistency_gate_failed",
            "audit_consistency": audit,
        }

    # Per-regime pass rates + intersection N.
    per_regime_pass_rates: dict[str, dict[str, float | int]] = {}
    p_vec: list[float] = []
    for regime in PHASE2C_15_REGIMES:
        p_r, count_pass, count_finite = _per_regime_pass_rate(
            broader_universe_per_regime[regime]
        )
        per_regime_pass_rates[regime] = {
            "p_r": p_r,
            "count_pass": count_pass,
            "count_finite": count_finite,
        }
        p_vec.append(p_r)
    N = _intersection_count(broader_universe_per_regime)
    p_product = float(np.prod(p_vec))
    exp = N * p_product
    obs = len(cohort_a)  # 39 cohort_a cardinality per sealed §1
    sigma = math.sqrt(N * p_product * (1.0 - p_product))
    epsilon = EPSILON_K * sigma

    # TOST equivalence test on |obs - exp|.
    abs_diff = abs(obs - exp)
    # H_0: |obs - exp| ≥ ε; H_1: |obs - exp| < ε. Detection = reject H_0.
    # Under Binomial(N, p_product), Z = (obs - exp)/sigma ~ N(0,1) approx.
    # TOST: reject H_0 iff abs_diff/sigma < EPSILON_K - z_alpha (one-sided z at α=0.05)
    # Equivalence test: max of two one-sided p-values.
    if sigma == 0.0:
        tost_p_lower = float("nan")
        tost_p_upper = float("nan")
        tost_p_value = float("nan")
        tost_reject_h0 = False
    else:
        z_lower = (obs - (exp - epsilon)) / sigma  # = (obs - exp + ε)/σ
        z_upper = ((exp + epsilon) - obs) / sigma  # = (ε - (obs - exp))/σ
        # One-sided tests: lower-bound test rejects if obs - exp > -ε at α/2 (effective);
        # symmetric TOST at α uses two one-sided tests each at α.
        tost_p_lower = float(stats.norm.sf(z_lower))  # P(Z >= z_lower) — small means reject
        tost_p_upper = float(stats.norm.sf(z_upper))
        tost_p_value = max(tost_p_lower, tost_p_upper)
        tost_reject_h0 = tost_p_value <= ALPHA

    detected = bool(tost_reject_h0)

    # Approach A: σ-perturbation cohort + Jaccard.
    sigmas = _sigma_per_field_per_regime(broader_universe_per_regime)
    cohort_a_set = set(cohort_a["hypothesis_hash"].tolist())
    stricter_cohort = _perturbed_cohort(broader_universe_per_regime, sigmas, "stricter")
    looser_cohort = _perturbed_cohort(broader_universe_per_regime, sigmas, "looser")
    jaccard_stricter = _jaccard(cohort_a_set, stricter_cohort)
    jaccard_looser = _jaccard(cohort_a_set, looser_cohort)

    # Cramér's V pairwise.
    cramers_v = _cramers_v_pairwise(broader_universe_per_regime)

    # Pass-pattern distribution (D2''' Point 2 lock — descriptive only).
    pass_dist = _pass_pattern_distribution(broader_universe_per_regime)

    return {
        "mode": "§2.d AND-gate overfit",
        "detected": detected,
        "execution_suspended": False,
        "tost_p_value": tost_p_value,
        "tost_p_lower": tost_p_lower,
        "tost_p_upper": tost_p_upper,
        "alpha": ALPHA,
        "obs": obs,
        "exp": exp,
        "abs_diff": abs_diff,
        "epsilon": epsilon,
        "epsilon_k": EPSILON_K,
        "p_product": p_product,
        "intersection_count_N": N,
        "per_regime_pass_rates": per_regime_pass_rates,
        "approach_a_jaccard": {
            "stricter_cohort_size": len(stricter_cohort),
            "looser_cohort_size": len(looser_cohort),
            "jaccard_cohort_a_vs_stricter": jaccard_stricter,
            "jaccard_cohort_a_vs_looser": jaccard_looser,
            "perturbation_k": PERTURBATION_K,
        },
        "descriptive": {
            "cramers_v_pairwise": cramers_v,
            "pass_pattern_distribution_16cells": pass_dist,
        },
        "audit_consistency": {
            "all_match": audit["all_match"],
            "total_bits": audit["total_bits"],
            "matched_bits": audit["matched_bits"],
            "discrepancy_count": audit["discrepancy_count"],
        },
        "register_class": "binding | quantitative (TOST α=0.05 Binomial-exact ε=2σ; Approach A Jaccard) | irreversible-interpretation",
    }
