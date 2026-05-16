"""§2.e Success-metric mismatch — Wilcoxon per stratum at Bonferroni α=0.025.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §2.e (sealed at
92880f8; D3'''' lock). 15bps primary at PLAN-§1.5-alignment register; 7bps
supplementary at descriptive register; BH step-up + uncorrected at general
discipline lock supplements not eligible for post-hoc promotion.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ALPHA_PRIMARY = 0.025  # Bonferroni-corrected per stratum
BH_FDR_Q = 0.05
UNCORRECTED_ALPHA = 0.05


def _wilcoxon_greater(values: np.ndarray) -> tuple[float, int]:
    finite = values[np.isfinite(values)]
    if len(finite) == 0:
        return (float("nan"), 0)
    nonzero = finite[finite != 0.0]
    if len(nonzero) == 0:
        return (float("nan"), 0)
    res = stats.wilcoxon(nonzero, zero_method="wilcox", alternative="greater")
    return (float(res.pvalue), int(len(nonzero)))


def _per_stratum_wilcoxon(
    cohort_a: pd.DataFrame, forward_df: pd.DataFrame
) -> dict[str, dict[str, Any]]:
    merged = cohort_a[["hypothesis_hash", "theme"]].merge(
        forward_df[["hypothesis_hash", "holdout_sharpe"]],
        on="hypothesis_hash",
        how="left",
    )
    out: dict[str, dict[str, Any]] = {}
    for stratum_name, mask in (
        ("stratum_a_calendar_effect", merged["theme"] == "calendar_effect"),
        ("stratum_b_non_calendar", merged["theme"] != "calendar_effect"),
    ):
        sharpes = merged.loc[mask, "holdout_sharpe"].to_numpy(dtype=float)
        p, n_eff = _wilcoxon_greater(sharpes)
        finite = sharpes[np.isfinite(sharpes)]
        out[stratum_name] = {
            "n_input": int(mask.sum()),
            "n_effective": n_eff,
            "p_value": p,
            "mean_forward_sharpe": float(np.mean(finite)) if len(finite) else float("nan"),
            "median_forward_sharpe": float(np.median(finite)) if len(finite) else float("nan"),
            "prop_positive_sharpe": float(np.mean(finite > 0)) if len(finite) else float("nan"),
            "detected_at_bonferroni_alpha_0025": bool(np.isfinite(p) and p <= ALPHA_PRIMARY),
            "detected_at_uncorrected_alpha_005": bool(
                np.isfinite(p) and p <= UNCORRECTED_ALPHA
            ),
        }
    return out


def _bh_step_up_evaluation(p_a: float, p_b: float, q: float = BH_FDR_Q) -> dict[str, Any]:
    """Benjamini-Hochberg step-up at FDR q on K=2 hypotheses per sealed §2.e supplement A."""
    if not (np.isfinite(p_a) and np.isfinite(p_b)):
        return {"both_rejected": False, "smallest_rejected": False, "error": "non_finite_p"}
    p_max = max(p_a, p_b)
    p_min = min(p_a, p_b)
    both_rejected = p_max <= q
    smallest_rejected = (not both_rejected) and (p_min <= q / 2.0)
    return {
        "both_rejected": both_rejected,
        "smallest_rejected": smallest_rejected,
        "p_max": p_max,
        "p_min": p_min,
        "q": q,
    }


def compute_success_metric_mismatch(
    cohort_a: pd.DataFrame,
    forward_15bps: pd.DataFrame,
    forward_07bps: pd.DataFrame,
) -> dict[str, Any]:
    """Fire §2.e success-metric-mismatch indicator per sealed prose."""

    # Primary: 15bps PLAN-§1.5-alignment register.
    per_stratum_15bps = _per_stratum_wilcoxon(cohort_a, forward_15bps)
    p_a = per_stratum_15bps["stratum_a_calendar_effect"]["p_value"]
    p_b = per_stratum_15bps["stratum_b_non_calendar"]["p_value"]
    detected = bool(
        per_stratum_15bps["stratum_a_calendar_effect"]["detected_at_bonferroni_alpha_0025"]
        or per_stratum_15bps["stratum_b_non_calendar"]["detected_at_bonferroni_alpha_0025"]
    )

    bh_15bps = _bh_step_up_evaluation(p_a, p_b)

    # 7bps supplementary at descriptive register.
    per_stratum_07bps = _per_stratum_wilcoxon(cohort_a, forward_07bps)
    p_a_07 = per_stratum_07bps["stratum_a_calendar_effect"]["p_value"]
    p_b_07 = per_stratum_07bps["stratum_b_non_calendar"]["p_value"]
    bh_07bps = _bh_step_up_evaluation(p_a_07, p_b_07)

    return {
        "mode": "§2.e success-metric mismatch",
        "detected": detected,
        "primary_15bps": {
            "alpha_bonferroni_per_stratum": ALPHA_PRIMARY,
            "per_stratum": per_stratum_15bps,
            "test": "wilcoxon signed-rank (one-sided greater) per stratum",
            "zero_method": "wilcox",
            "detection_logic": "Cell (2) of 4-cell scaffolding (PLAN §1.5 fail-to-reject sealed; Wilcoxon rejects in either stratum at Bonferroni α=0.025)",
        },
        "descriptive_supplement_A_BH_15bps": bh_15bps,
        "descriptive_supplement_B_uncorrected_15bps": {
            "stratum_a_detected": per_stratum_15bps["stratum_a_calendar_effect"][
                "detected_at_uncorrected_alpha_005"
            ],
            "stratum_b_detected": per_stratum_15bps["stratum_b_non_calendar"][
                "detected_at_uncorrected_alpha_005"
            ],
            "alpha": UNCORRECTED_ALPHA,
        },
        "supplementary_07bps": {
            "per_stratum": per_stratum_07bps,
            "bh_step_up": bh_07bps,
            "register": "descriptive — PHASE2C-research cost basis cross-check",
        },
        "register_class": "binding | quantitative (Wilcoxon Bonferroni α=0.025/stratum at 15bps PLAN-§1.5-alignment register) | irreversible-interpretation",
    }
