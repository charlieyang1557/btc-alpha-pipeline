"""§2.f Regime change — empirical quantile band on T(block) = std(log-returns).

Sealed prose at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md §2.f (sealed at
c536231; D3''''' lock). Reference universe 2020-2024 (test_2025 EXCLUDED per
touch-once spirit); 17 non-overlapping 2528-bar blocks anchored at
2020-01-01T00:00Z; forward block = single Q1 2026 [2026-01-01..2026-04-16T07].
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from phase5.io import (
    EXPECTED_PARQUET_SHA256,
    FORWARD_WINDOW_BARS,
    FORWARD_WINDOW_END_INCLUSIVE,
    FORWARD_WINDOW_START,
    REFERENCE_BLOCK_COUNT_EXPECTED,
    REFERENCE_BLOCK_SIZE_BARS,
    REFERENCE_UNIVERSE_END_INCLUSIVE,
    REFERENCE_UNIVERSE_START,
    verify_parquet_sha256,
)

QUANTILE_METHOD = "linear"
LOWER_QUANTILE = 0.025
UPPER_QUANTILE = 0.975


def _log_returns(closes: np.ndarray) -> np.ndarray:
    return np.diff(np.log(closes))


def _block_std_log_returns(closes: np.ndarray) -> float:
    """T(block) = std of consecutive log-returns within block; ddof=1 (sample std)."""
    lr = _log_returns(closes)
    if len(lr) < 2:
        return float("nan")
    return float(np.std(lr, ddof=1))


def _calendar_q1_blocks(parquet_df: pd.DataFrame) -> list[dict[str, Any]]:
    """5 calendar-aligned Q1 blocks (2020-2024); each 2528 bars starting Jan 1.

    Sealed §2.f descriptive supplement only; not primary judgment input.
    """
    out: list[dict[str, Any]] = []
    for year in (2020, 2021, 2022, 2023, 2024):
        start = pd.Timestamp(f"{year}-01-01T00:00:00", tz="UTC")
        block = parquet_df[parquet_df["open_time_utc"] >= start].head(REFERENCE_BLOCK_SIZE_BARS)
        if len(block) != REFERENCE_BLOCK_SIZE_BARS:
            out.append({"year": year, "n_bars": len(block), "t_value": float("nan")})
            continue
        t = _block_std_log_returns(block["close"].to_numpy(dtype=float))
        out.append(
            {
                "year": year,
                "n_bars": int(len(block)),
                "start": str(block["open_time_utc"].iloc[0]),
                "end": str(block["open_time_utc"].iloc[-1]),
                "t_value": t,
            }
        )
    return out


def compute_regime_change(parquet_df: pd.DataFrame) -> dict[str, Any]:
    """Fire §2.f regime-change indicator per sealed prose.

    Pre-execution gate: parquet sha256 re-verify against sealed §1/§2.f anchor.
    Defensive re-check; should already have been verified at orchestrator entry.
    """
    matches, actual_sha = verify_parquet_sha256()
    if not matches:
        return {
            "mode": "§2.f regime change",
            "detected": None,
            "execution_suspended": True,
            "suspension_cause": "parquet_sha256_mismatch",
            "expected_sha256": EXPECTED_PARQUET_SHA256,
            "actual_sha256": actual_sha,
        }

    df = parquet_df.sort_values("open_time_utc").reset_index(drop=True)

    # Reference universe slice (2020-01-01 to 2024-12-31 inclusive).
    ref = df[
        (df["open_time_utc"] >= REFERENCE_UNIVERSE_START)
        & (df["open_time_utc"] <= REFERENCE_UNIVERSE_END_INCLUSIVE)
    ].reset_index(drop=True)

    # Non-overlapping 2528-bar blocks anchored at 2020-01-01T00:00Z.
    n_blocks = len(ref) // REFERENCE_BLOCK_SIZE_BARS
    if n_blocks != REFERENCE_BLOCK_COUNT_EXPECTED:
        return {
            "mode": "§2.f regime change",
            "detected": None,
            "execution_suspended": True,
            "suspension_cause": "block_count_mismatch",
            "expected_blocks": REFERENCE_BLOCK_COUNT_EXPECTED,
            "actual_blocks": n_blocks,
            "reference_universe_bars": int(len(ref)),
        }

    block_records: list[dict[str, Any]] = []
    ref_T_values: list[float] = []
    for i in range(n_blocks):
        start_idx = i * REFERENCE_BLOCK_SIZE_BARS
        end_idx = start_idx + REFERENCE_BLOCK_SIZE_BARS
        block = ref.iloc[start_idx:end_idx]
        t = _block_std_log_returns(block["close"].to_numpy(dtype=float))
        ref_T_values.append(t)
        block_records.append(
            {
                "block_index": i,
                "start": str(block["open_time_utc"].iloc[0]),
                "end": str(block["open_time_utc"].iloc[-1]),
                "n_bars": int(len(block)),
                "t_value": t,
            }
        )

    # Forward block.
    forward = df[
        (df["open_time_utc"] >= FORWARD_WINDOW_START)
        & (df["open_time_utc"] <= FORWARD_WINDOW_END_INCLUSIVE)
    ].reset_index(drop=True)
    if len(forward) != FORWARD_WINDOW_BARS:
        return {
            "mode": "§2.f regime change",
            "detected": None,
            "execution_suspended": True,
            "suspension_cause": "forward_window_bar_count_mismatch",
            "expected_bars": FORWARD_WINDOW_BARS,
            "actual_bars": int(len(forward)),
        }
    forward_T = _block_std_log_returns(forward["close"].to_numpy(dtype=float))

    ref_T_arr = np.asarray(ref_T_values, dtype=float)
    q_lower = float(np.quantile(ref_T_arr, LOWER_QUANTILE, method=QUANTILE_METHOD))
    q_upper = float(np.quantile(ref_T_arr, UPPER_QUANTILE, method=QUANTILE_METHOD))

    detected = bool(forward_T < q_lower or forward_T > q_upper)

    # Calendar-aligned Q1 supplement.
    q1_blocks = _calendar_q1_blocks(df)
    q1_t_values = np.asarray(
        [b["t_value"] for b in q1_blocks if np.isfinite(b["t_value"])], dtype=float
    )
    if len(q1_t_values) > 0:
        # Forward Q1 empirical percentile rank in historical Q1 distribution.
        # Share of historical Q1 blocks with T <= forward_Q1_T.
        forward_q1_rank = float(np.mean(q1_t_values <= forward_T))
    else:
        forward_q1_rank = float("nan")

    # Supplements A/B/C/D per sealed §2.f descriptive register (forward-block scope).
    forward_lr = _log_returns(forward["close"].to_numpy(dtype=float))
    sigma_block = float(np.std(forward_lr, ddof=1))
    if sigma_block > 0 and len(forward_lr) > 0:
        ups = int(np.sum(forward_lr > sigma_block))
        downs = int(np.sum(forward_lr < -sigma_block))
        downside_tail_ratio = (downs / ups) if ups > 0 else float("nan")
    else:
        downside_tail_ratio = float("nan")

    # Lag-1 autocorrelation of forward log-returns.
    if len(forward_lr) >= 2:
        lag1 = float(np.corrcoef(forward_lr[:-1], forward_lr[1:])[0, 1])
    else:
        lag1 = float("nan")

    # Trend slope: linear regression slope of log(close) ~ normalized time.
    if len(forward) >= 2:
        y = np.log(forward["close"].to_numpy(dtype=float))
        x = np.linspace(0.0, 1.0, len(y))
        slope = float(np.polyfit(x, y, deg=1)[0])
    else:
        slope = float("nan")

    # HODL Sharpe (annualized) at forward block.
    if len(forward_lr) >= 2 and np.std(forward_lr, ddof=1) > 0:
        # Annualized assuming 24*365 hours/year for 1h bars.
        hodl_sharpe = float(
            np.mean(forward_lr) / np.std(forward_lr, ddof=1) * np.sqrt(24 * 365)
        )
    else:
        hodl_sharpe = float("nan")

    return {
        "mode": "§2.f regime change",
        "detected": detected,
        "execution_suspended": False,
        "forward_T": forward_T,
        "reference_T_values": ref_T_values,
        "reference_block_count": n_blocks,
        "reference_universe_bars": int(len(ref)),
        "reference_block_size_bars": REFERENCE_BLOCK_SIZE_BARS,
        "leftover_reference_hours": int(len(ref) - n_blocks * REFERENCE_BLOCK_SIZE_BARS),
        "forward_window_bars": int(len(forward)),
        "quantile_band": {
            "lower_q025": q_lower,
            "upper_q975": q_upper,
            "method": QUANTILE_METHOD,
            "convention": "strict-inequality boundary (equality NOT detected)",
        },
        "reference_T_stats": {
            "min": float(np.min(ref_T_arr)),
            "max": float(np.max(ref_T_arr)),
            "mean": float(np.mean(ref_T_arr)),
            "median": float(np.median(ref_T_arr)),
            "std": float(np.std(ref_T_arr, ddof=1)),
        },
        "calendar_aligned_q1_supplement": {
            "blocks": q1_blocks,
            "forward_q1_empirical_percentile_rank": forward_q1_rank,
            "register": "descriptive — seasonality-artifact vs regime-change disambiguation at §6 narrative",
        },
        "descriptive_supplements": {
            "supplement_a_lag1_autocorrelation_forward_block": lag1,
            "supplement_b_trend_slope_log_close_normalized_time_forward_block": slope,
            "supplement_c_downside_tail_ratio_forward_block": downside_tail_ratio,
            "supplement_d_forward_block_hodl_sharpe_annualized": hodl_sharpe,
        },
        "block_records": block_records,
        "register_class": "binding | quantitative (non-parametric quantile band α=0.05 symmetric 95%) | irreversible-interpretation",
    }
