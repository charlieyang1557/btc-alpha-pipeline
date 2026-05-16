"""§2.a Signal decay — Wilcoxon signed-rank one-sided test on paired Δ.

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §2.a (sealed at
6ee94eb; D3 lock). All thresholds and formulas frozen at §2.2 operationalization
freeze; no methodology codification at this register.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ALPHA = 0.05


def _paired_baseline_oos(row: pd.Series) -> float:
    """training_test_sharpe[i] = mean(bear_2022, validation_2024) per sealed §2.a primary baseline."""
    a = row["holdout_bear_2022_sharpe"]
    b = row["holdout_validation_2024_sharpe"]
    return float(np.mean([a, b]))


def _paired_baseline_mean_of_4(row: pd.Series) -> float:
    """Sealed §2.a mean-of-4 supplementary baseline (all 4 regime holdout Sharpes)."""
    cols = [
        "holdout_bear_2022_sharpe",
        "holdout_validation_2024_sharpe",
        "holdout_eval_2020_v1_sharpe",
        "holdout_eval_2021_v1_sharpe",
    ]
    return float(np.mean([row[c] for c in cols]))


def _wilcoxon_one_sided_less(deltas: np.ndarray) -> tuple[float, int]:
    """Sealed §2.a SciPy invocation: wilcoxon(..., zero_method='wilcox', alternative='less').

    Returns (p_value, n_effective_after_zero_method_exclusion).
    """
    finite = deltas[np.isfinite(deltas)]
    if len(finite) == 0:
        return (float("nan"), 0)
    nonzero = finite[finite != 0.0]
    if len(nonzero) == 0:
        return (float("nan"), 0)
    res = stats.wilcoxon(
        nonzero, zero_method="wilcox", alternative="less"
    )
    return (float(res.pvalue), int(len(nonzero)))


def compute_signal_decay(
    cohort_a: pd.DataFrame,
    forward_07bps: pd.DataFrame,
) -> dict[str, Any]:
    """Fire §2.a signal-decay indicator per sealed prose.

    Returns canonical-binary outcome dict per sealed §2.a output canonical
    register: {detected, p_value, n_effective, descriptive supplements,
    dropped_candidates, per_stratum, mean_of_4_supplement}.
    """
    merged = cohort_a.merge(
        forward_07bps[["hypothesis_hash", "holdout_sharpe"]].rename(
            columns={"holdout_sharpe": "forward_sharpe_07bps"}
        ),
        on="hypothesis_hash",
        how="left",
    )

    # Primary baseline (OOS-only: bear_2022 + validation_2024 mean).
    merged["training_test_sharpe"] = merged.apply(_paired_baseline_oos, axis=1)
    merged["delta"] = merged["forward_sharpe_07bps"] - merged["training_test_sharpe"]

    # Track per §6 FB any non-finite-pair drops (NaN protocol per sealed §2.a).
    dropped = merged[~np.isfinite(merged["delta"])][
        [
            "hypothesis_hash",
            "theme",
            "holdout_bear_2022_sharpe",
            "holdout_validation_2024_sharpe",
            "forward_sharpe_07bps",
            "delta",
        ]
    ].to_dict(orient="records")

    deltas = merged["delta"].to_numpy(dtype=float)
    p_value, n_eff = _wilcoxon_one_sided_less(deltas)

    detected = bool(np.isfinite(p_value) and p_value <= ALPHA)

    # Descriptive supplements (sealed §2.a) — exclude non-finite first.
    finite_deltas = deltas[np.isfinite(deltas)]
    mean_delta = float(np.mean(finite_deltas)) if len(finite_deltas) else float("nan")
    median_delta = float(np.median(finite_deltas)) if len(finite_deltas) else float("nan")
    prop_delta_neg = (
        float(np.mean(finite_deltas < 0)) if len(finite_deltas) else float("nan")
    )
    sd = float(np.std(finite_deltas, ddof=1)) if len(finite_deltas) > 1 else float("nan")
    cohen_d = mean_delta / sd if np.isfinite(sd) and sd > 0 else float("nan")

    # Per-stratum supplements (Stratum A=calendar_effect, Stratum B=non-calendar).
    per_stratum: dict[str, dict[str, Any]] = {}
    for stratum_name, mask in (
        ("stratum_a_calendar_effect", merged["theme"] == "calendar_effect"),
        ("stratum_b_non_calendar", merged["theme"] != "calendar_effect"),
    ):
        d = merged.loc[mask, "delta"].to_numpy(dtype=float)
        finite_d = d[np.isfinite(d)]
        p_s, n_s = _wilcoxon_one_sided_less(d)
        per_stratum[stratum_name] = {
            "n_input": int(mask.sum()),
            "n_effective": n_s,
            "p_value": p_s,
            "detected_at_alpha_005": bool(
                np.isfinite(p_s) and p_s <= ALPHA
            ),
            "mean_delta": float(np.mean(finite_d)) if len(finite_d) else float("nan"),
            "median_delta": float(np.median(finite_d)) if len(finite_d) else float("nan"),
        }

    # Mean-of-4 supplementary baseline (train-overlap-inclusive).
    merged["training_test_sharpe_mean_of_4"] = merged.apply(
        _paired_baseline_mean_of_4, axis=1
    )
    merged["delta_mean_of_4"] = (
        merged["forward_sharpe_07bps"] - merged["training_test_sharpe_mean_of_4"]
    )
    deltas_m4 = merged["delta_mean_of_4"].to_numpy(dtype=float)
    p_m4, n_m4 = _wilcoxon_one_sided_less(deltas_m4)
    finite_m4 = deltas_m4[np.isfinite(deltas_m4)]
    mean_of_4_supplement = {
        "p_value": p_m4,
        "n_effective": n_m4,
        "mean_delta": float(np.mean(finite_m4)) if len(finite_m4) else float("nan"),
        "median_delta": float(np.median(finite_m4)) if len(finite_m4) else float("nan"),
    }

    return {
        "mode": "§2.a signal decay",
        "detected": detected,
        "p_value": p_value,
        "n_effective": n_eff,
        "alpha": ALPHA,
        "alternative": "less",
        "zero_method": "wilcox",
        "test": "wilcoxon signed-rank (one-sided)",
        "descriptive": {
            "mean_delta": mean_delta,
            "median_delta": median_delta,
            "prop_delta_negative": prop_delta_neg,
            "paired_cohen_d": cohen_d,
            "n_input": int(len(deltas)),
            "n_finite": int(len(finite_deltas)),
            "per_stratum": per_stratum,
            "mean_of_4_supplement": mean_of_4_supplement,
        },
        "dropped_candidates": dropped,
        "register_class": "binding | quantitative (α=0.05) | irreversible-interpretation",
    }
