"""§2.b Cost drag — per-candidate Spearman ρ across cost levels + cohort Wilcoxon.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §2.b (sealed at
6ee94eb; D3 lock). Cost-vector convention ascending [7, 13, 15, 17] locked;
SciPy spearmanr average-rank tie handling accepted implicitly.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ALPHA = 0.05
COST_VECTOR_BPS = (7, 13, 15, 17)


def _spearman_per_candidate(
    hypothesis_hash: str,
    forward_per_cost_bps: dict[int, pd.DataFrame],
) -> tuple[float, list[float]]:
    """Return (rho, sharpes_per_cost) for a single candidate across cost levels."""
    sharpes: list[float] = []
    for bps in COST_VECTOR_BPS:
        df = forward_per_cost_bps[bps]
        row = df[df["hypothesis_hash"] == hypothesis_hash]
        if len(row) != 1:
            sharpes.append(float("nan"))
        else:
            sharpes.append(float(row["holdout_sharpe"].iloc[0]))
    if any(not np.isfinite(s) for s in sharpes):
        return (float("nan"), sharpes)
    if len(set(sharpes)) == 1:
        # Constant Sharpe across cost levels → undefined Spearman ρ (zero variance).
        return (float("nan"), sharpes)
    res = stats.spearmanr(np.asarray(COST_VECTOR_BPS, dtype=float), np.asarray(sharpes))
    return (float(res.correlation), sharpes)


def _wilcoxon_one_sided_less(values: np.ndarray) -> tuple[float, int]:
    finite = values[np.isfinite(values)]
    if len(finite) == 0:
        return (float("nan"), 0)
    nonzero = finite[finite != 0.0]
    if len(nonzero) == 0:
        return (float("nan"), 0)
    res = stats.wilcoxon(nonzero, zero_method="wilcox", alternative="less")
    return (float(res.pvalue), int(len(nonzero)))


def compute_cost_drag(
    cohort_a: pd.DataFrame,
    forward_per_cost_bps: dict[int, pd.DataFrame],
) -> dict[str, Any]:
    """Fire §2.b cost-drag indicator per sealed prose.

    Returns canonical-binary outcome + per-stratum supplements + multi-pair
    magnitude supplements per sealed §2.b descriptive register.
    """
    rho_per_candidate: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for _, c in cohort_a.iterrows():
        h = c["hypothesis_hash"]
        rho, sharpes = _spearman_per_candidate(h, forward_per_cost_bps)
        if not np.isfinite(rho):
            dropped.append(
                {
                    "hypothesis_hash": h,
                    "theme": c["theme"],
                    "sharpes_per_cost": dict(zip(COST_VECTOR_BPS, sharpes)),
                    "reason": "nan_or_zero_variance",
                }
            )
            continue
        rho_per_candidate.append(
            {
                "hypothesis_hash": h,
                "theme": c["theme"],
                "rho": rho,
                "sharpes_per_cost": dict(zip(COST_VECTOR_BPS, sharpes)),
            }
        )

    rho_values = np.asarray([r["rho"] for r in rho_per_candidate], dtype=float)
    p_value, n_eff = _wilcoxon_one_sided_less(rho_values)
    detected = bool(np.isfinite(p_value) and p_value <= ALPHA)

    finite_rho = rho_values[np.isfinite(rho_values)]
    mean_rho = float(np.mean(finite_rho)) if len(finite_rho) else float("nan")
    median_rho = float(np.median(finite_rho)) if len(finite_rho) else float("nan")
    prop_rho_neg = (
        float(np.mean(finite_rho < 0)) if len(finite_rho) else float("nan")
    )
    sd = float(np.std(finite_rho, ddof=1)) if len(finite_rho) > 1 else float("nan")
    cohen_d = mean_rho / sd if np.isfinite(sd) and sd > 0 else float("nan")

    per_stratum: dict[str, dict[str, Any]] = {}
    for stratum_name, theme_filter in (
        ("stratum_a_calendar_effect", lambda t: t == "calendar_effect"),
        ("stratum_b_non_calendar", lambda t: t != "calendar_effect"),
    ):
        sub_rhos = np.asarray(
            [r["rho"] for r in rho_per_candidate if theme_filter(r["theme"])],
            dtype=float,
        )
        p_s, n_s = _wilcoxon_one_sided_less(sub_rhos)
        per_stratum[stratum_name] = {
            "n_input": int(len(sub_rhos)),
            "n_effective": n_s,
            "p_value": p_s,
            "detected_at_alpha_005": bool(np.isfinite(p_s) and p_s <= ALPHA),
        }

    # Multi-pair magnitude supplements per sealed §2.b descriptive register.
    multi_pair_supplements: dict[str, dict[str, Any]] = {}
    for a, b in [(7, 13), (7, 15), (7, 17), (13, 15)]:
        deltas: list[float] = []
        for _, c in cohort_a.iterrows():
            h = c["hypothesis_hash"]
            row_a = forward_per_cost_bps[a].loc[
                forward_per_cost_bps[a]["hypothesis_hash"] == h, "holdout_sharpe"
            ]
            row_b = forward_per_cost_bps[b].loc[
                forward_per_cost_bps[b]["hypothesis_hash"] == h, "holdout_sharpe"
            ]
            if len(row_a) == 1 and len(row_b) == 1:
                deltas.append(float(row_a.iloc[0]) - float(row_b.iloc[0]))
        arr = np.asarray(deltas, dtype=float)
        finite_arr = arr[np.isfinite(arr)]
        if len(finite_arr) >= 1:
            nonzero = finite_arr[finite_arr != 0.0]
            if len(nonzero) > 0:
                try:
                    p = float(
                        stats.wilcoxon(
                            nonzero, zero_method="wilcox", alternative="two-sided"
                        ).pvalue
                    )
                except ValueError:
                    p = float("nan")
            else:
                p = float("nan")
            multi_pair_supplements[f"delta_{a}_minus_{b}"] = {
                "mean": float(np.mean(finite_arr)),
                "median": float(np.median(finite_arr)),
                "wilcoxon_two_sided_p": p,
                "n": int(len(finite_arr)),
            }

    return {
        "mode": "§2.b cost drag",
        "detected": detected,
        "p_value": p_value,
        "n_effective": n_eff,
        "alpha": ALPHA,
        "alternative": "less",
        "zero_method": "wilcox",
        "test": "wilcoxon signed-rank (one-sided) on per-candidate Spearman ρ",
        "cost_vector_bps": list(COST_VECTOR_BPS),
        "descriptive": {
            "mean_rho": mean_rho,
            "median_rho": median_rho,
            "prop_rho_negative": prop_rho_neg,
            "rho_cohen_d": cohen_d,
            "n_input": int(len(rho_values)),
            "n_finite": int(len(finite_rho)),
            "per_stratum": per_stratum,
            "multi_pair_supplements": multi_pair_supplements,
            "rho_per_candidate": rho_per_candidate,
        },
        "dropped_candidates": dropped,
        "register_class": "binding | quantitative (α=0.05) | irreversible-interpretation",
    }
