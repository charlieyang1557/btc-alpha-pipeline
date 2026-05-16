"""§2.c Cohort weakness — 75th/90th percentile-rank AND-conditions.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §2.c (sealed at
6ee94eb; D3'' lock). Selection-bias caveat binding; percentile_rank uses
scipy percentileofscore kind='weak'; quantile uses numpy.quantile method='linear'.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy import stats

PERCENTILE_RANK_KIND = "weak"
QUANTILE_METHOD = "linear"
COND_1_CUTOFF = 0.75  # cohort median vs broader-universe percentile rank
COND_2_CUTOFF = 0.90  # cohort p75 vs broader-universe percentile rank


def _per_candidate_score_oos(summary_per_regime: dict[str, dict]) -> float:
    """Per sealed §2.c primary OOS-only score: mean(bear_2022_sharpe, validation_2024_sharpe)."""
    s_bear = summary_per_regime.get("bear_2022", {}).get("holdout_metrics", {}).get("sharpe_ratio")
    s_val = summary_per_regime.get("audit_2024", {}).get("holdout_metrics", {}).get("sharpe_ratio")
    if s_bear is None or s_val is None:
        return float("nan")
    if not (isinstance(s_bear, (int, float)) and isinstance(s_val, (int, float))):
        return float("nan")
    if not (np.isfinite(s_bear) and np.isfinite(s_val)):
        return float("nan")
    return float((s_bear + s_val) / 2.0)


def _per_candidate_score_mean_of_4(summary_per_regime: dict[str, dict]) -> float:
    vals: list[float] = []
    for regime in ("bear_2022", "audit_2024", "eval_2020", "eval_2021"):
        s = (
            summary_per_regime.get(regime, {})
            .get("holdout_metrics", {})
            .get("sharpe_ratio")
        )
        if not isinstance(s, (int, float)) or not np.isfinite(s):
            return float("nan")
        vals.append(float(s))
    return float(np.mean(vals))


def _cohort_a_score_oos(row: pd.Series) -> float:
    a = row["holdout_bear_2022_sharpe"]
    b = row["holdout_validation_2024_sharpe"]
    if not (np.isfinite(a) and np.isfinite(b)):
        return float("nan")
    return float((a + b) / 2.0)


def _cohort_a_score_mean_of_4(row: pd.Series) -> float:
    cols = [
        "holdout_bear_2022_sharpe",
        "holdout_validation_2024_sharpe",
        "holdout_eval_2020_v1_sharpe",
        "holdout_eval_2021_v1_sharpe",
    ]
    vals = [row[c] for c in cols]
    if not all(np.isfinite(v) for v in vals):
        return float("nan")
    return float(np.mean(vals))


def _assemble_broader_universe_scores(
    broader_universe_per_regime: dict[str, dict[str, dict]],
    score_fn: Callable[[dict[str, dict]], float],
) -> dict[str, float]:
    """Compute per-candidate score across broader universe; key by hypothesis_hash."""
    # All regimes share the same set of 993 hashes per sealed §1 invariant.
    hashes = set(broader_universe_per_regime["bear_2022"].keys())
    for regime, m in broader_universe_per_regime.items():
        hashes &= set(m.keys())
    out: dict[str, float] = {}
    for h in hashes:
        per_regime = {regime: broader_universe_per_regime[regime][h] for regime in broader_universe_per_regime}
        out[h] = score_fn(per_regime)
    return out


def compute_cohort_weakness(
    cohort_a: pd.DataFrame,
    broader_universe_per_regime: dict[str, dict[str, dict]],
) -> dict[str, Any]:
    """Fire §2.c cohort-weakness indicator per sealed prose."""
    # Broader universe primary scores (OOS-only).
    broader_scores_primary = _assemble_broader_universe_scores(
        broader_universe_per_regime, _per_candidate_score_oos
    )
    broader_arr_primary = np.asarray(
        [v for v in broader_scores_primary.values() if np.isfinite(v)], dtype=float
    )

    # cohort_a primary scores (OOS-only).
    cohort_scores_primary: list[float] = []
    dropped: list[dict[str, Any]] = []
    for _, c in cohort_a.iterrows():
        score = _cohort_a_score_oos(c)
        if not np.isfinite(score):
            dropped.append(
                {
                    "hypothesis_hash": c["hypothesis_hash"],
                    "theme": c["theme"],
                    "reason": "non_finite_oos_score",
                }
            )
            continue
        cohort_scores_primary.append(score)
    cohort_arr_primary = np.asarray(cohort_scores_primary, dtype=float)

    if len(broader_arr_primary) == 0 or len(cohort_arr_primary) == 0:
        return {
            "mode": "§2.c cohort weakness",
            "detected": False,
            "error": "empty score distribution after non-finite exclusion",
        }

    cohort_median = float(np.median(cohort_arr_primary))
    cohort_p75 = float(
        np.quantile(cohort_arr_primary, 0.75, method=QUANTILE_METHOD)
    )

    rank_median = float(
        stats.percentileofscore(
            broader_arr_primary, cohort_median, kind=PERCENTILE_RANK_KIND
        )
        / 100.0
    )
    rank_p75 = float(
        stats.percentileofscore(
            broader_arr_primary, cohort_p75, kind=PERCENTILE_RANK_KIND
        )
        / 100.0
    )

    condition_1 = rank_median < COND_1_CUTOFF
    condition_2 = rank_p75 < COND_2_CUTOFF
    detected = bool(condition_1 and condition_2)

    # Supplementary mean-of-4 view.
    broader_scores_m4 = _assemble_broader_universe_scores(
        broader_universe_per_regime, _per_candidate_score_mean_of_4
    )
    broader_arr_m4 = np.asarray(
        [v for v in broader_scores_m4.values() if np.isfinite(v)], dtype=float
    )
    cohort_arr_m4 = np.asarray(
        [_cohort_a_score_mean_of_4(c) for _, c in cohort_a.iterrows()], dtype=float
    )
    cohort_arr_m4 = cohort_arr_m4[np.isfinite(cohort_arr_m4)]
    if len(broader_arr_m4) and len(cohort_arr_m4):
        cohort_median_m4 = float(np.median(cohort_arr_m4))
        cohort_p75_m4 = float(np.quantile(cohort_arr_m4, 0.75, method=QUANTILE_METHOD))
        rank_median_m4 = float(
            stats.percentileofscore(broader_arr_m4, cohort_median_m4, kind=PERCENTILE_RANK_KIND)
            / 100.0
        )
        rank_p75_m4 = float(
            stats.percentileofscore(broader_arr_m4, cohort_p75_m4, kind=PERCENTILE_RANK_KIND)
            / 100.0
        )
        mean_of_4_supplement = {
            "broader_n_finite": int(len(broader_arr_m4)),
            "cohort_n_finite": int(len(cohort_arr_m4)),
            "cohort_median": cohort_median_m4,
            "cohort_p75": cohort_p75_m4,
            "rank_median": rank_median_m4,
            "rank_p75": rank_p75_m4,
            "condition_1_median_lt_075": bool(rank_median_m4 < COND_1_CUTOFF),
            "condition_2_p75_lt_090": bool(rank_p75_m4 < COND_2_CUTOFF),
            "detected_at_mean_of_4": bool(
                rank_median_m4 < COND_1_CUTOFF and rank_p75_m4 < COND_2_CUTOFF
            ),
        }
    else:
        mean_of_4_supplement = {"error": "empty mean-of-4 score distribution"}

    return {
        "mode": "§2.c cohort weakness",
        "detected": detected,
        "condition_1_median_lt_075": bool(condition_1),
        "condition_2_p75_lt_090": bool(condition_2),
        "primary_oos": {
            "broader_n_finite": int(len(broader_arr_primary)),
            "cohort_n_finite": int(len(cohort_arr_primary)),
            "cohort_mean_score": float(np.mean(cohort_arr_primary)),
            "cohort_median_score": cohort_median,
            "cohort_p75": cohort_p75,
            "cohort_p25": float(np.quantile(cohort_arr_primary, 0.25, method=QUANTILE_METHOD)),
            "cohort_p90": float(np.quantile(cohort_arr_primary, 0.90, method=QUANTILE_METHOD)),
            "rank_median": rank_median,
            "rank_p75": rank_p75,
        },
        "cond_1_cutoff": COND_1_CUTOFF,
        "cond_2_cutoff": COND_2_CUTOFF,
        "percentile_rank_kind": PERCENTILE_RANK_KIND,
        "quantile_method": QUANTILE_METHOD,
        "descriptive": {
            "mean_of_4_supplement": mean_of_4_supplement,
        },
        "dropped_candidates": dropped,
        "register_class": "binding | quantitative (75th/90th percentile-rank AND-conditions) | irreversible-interpretation",
    }
