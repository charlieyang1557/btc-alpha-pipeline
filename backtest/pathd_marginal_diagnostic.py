# backtest/pathd_marginal_diagnostic.py
"""Fenced D1-only orthogonalization diagnostic + contamination correlations (Task C6).

PATH C→D KEY DIVERGENCE: D2 is DROPPED entirely. OI is an independent axis — no
derived-from relation — so Path C's D2-vs-funding/basis comparison is meaningless
here. Only D1 (vs no-OI momentum baseline) is ported.

NET-NEW for Path D: a fenced contamination-correlation set measuring Pearson AND
Spearman correlations of ``oi_velocity_ewm_240`` vs return and volatility series.
Measured and reported only; never a control over N* or promotion.

FENCED (DESIGN INVARIANT): every returned record carries ``promotion_affecting=False``
and ``in_n_star=False`` as structural constants — these are never derived from inputs
and no result can flip them.

Pre-registered tolerance (pre-data choice; inherits Path C discipline):
  D1_NONINERT_THRESHOLD = 0.10 — |d1_marginal_sharpe| > this is "non-inert"
    (the OI gate materially changes Sharpe relative to the no-OI baseline).
    Same rationale as Path C: 0.10 Sharpe units ≈ measurement noise on a
    ~100-trade forward window at typical BTC vol.

NOTE on absent D2 machinery:
  ``oi_marginal_d2``, ``basis_marginal_d2``, ``redundancy_read``, ``d2_agrees``,
  ``D2_AGREES_TOLERANCE`` are intentionally NOT present (see A1 regression guard in
  tests/test_pathd_marginal.py). The §38.3 inheritance retained here is the
  "fenced-label-read + inert-D1-is-modal" discipline only.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from backtest.metrics import compute_sharpe_ratio

# ---------------------------------------------------------------------------
# Pre-registered tolerance (pre-data; inherits Path C D1_NONINERT_THRESHOLD value)
# ---------------------------------------------------------------------------

D1_NONINERT_THRESHOLD: float = 0.10

# Series names measured in contamination_correlations (against oi_velocity_ewm_240).
# abs_return_1h is derived locally from return_1h — it is NOT a registered factor.
_CONTAMINATION_SERIES = (
    "return_1h",
    "abs_return_1h",
    "realized_vol_24h",
    "cdf_realized_vol_720",
)


def _per_bar_returns(equity: np.ndarray) -> np.ndarray:
    """Per-bar simple returns from an equity curve (drops the leading NaN)."""
    eq = pd.Series(np.asarray(equity, dtype=np.float64))
    return eq.pct_change().dropna().to_numpy()


def _validate_equity_pair(
    a: np.ndarray | pd.Series,
    b: np.ndarray | pd.Series,
    caller: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Validate that two equity curves cover identical bars; return as np.ndarray pair.

    When pandas Series are passed, requires an IDENTICAL index BEFORE dropping it to
    np.ndarray — two same-length curves on DIFFERENT timestamps are NOT the same bars.
    """
    if isinstance(a, pd.Series) and isinstance(b, pd.Series):
        if not a.index.equals(b.index):
            raise ValueError(
                f"{caller}: the two Series must share an IDENTICAL index "
                f"(same timestamps) — two same-length curves on DIFFERENT bars "
                f"are not the SAME bars; the marginal is only meaningful on aligned bars."
            )
    arr_a = np.asarray(a, dtype=np.float64)
    arr_b = np.asarray(b, dtype=np.float64)
    if arr_a.shape[0] != arr_b.shape[0]:
        raise ValueError(
            f"{caller}: the two equity curves must cover an identical bar count "
            f"({arr_a.shape[0]} vs {arr_b.shape[0]}) — the marginal is only meaningful "
            f"on the SAME bars."
        )
    return arr_a, arr_b


def oi_marginal_d1(
    hyp_id: str,
    gated_equity: np.ndarray | pd.Series,
    baseline_equity: np.ndarray | pd.Series,
) -> dict:
    """D1 (vs no-OI baseline): fenced OI-marginal Sharpe delta on identical bars.

    Computes ``Sharpe(OI-gated) - Sharpe(no-OI baseline)`` on the SAME forward bars.
    The no-OI baseline is:
      H1 → always-long (no OI filter applied)
      H2 → price-trend-only (no OI regime gate)
      H3 → price-trend-only (no OI continuation filter)

    Args:
        hyp_id: Hypothesis id ("H1" / "H2" / "H3").
        gated_equity: The OI-gated strategy's equity curve.
        baseline_equity: The no-OI baseline's equity curve on the SAME bars.

    Returns:
        Dict: ``hyp_id``, ``gated_sharpe``, ``baseline_sharpe``,
        ``d1_marginal_sharpe`` (gated - baseline), and the FENCE flags
        ``promotion_affecting=False`` and ``in_n_star=False``.

    Raises:
        ValueError: If the two equity curves do not cover an identical bar count,
            or (when pandas Series are passed) do not share an IDENTICAL index.

    Inputs: equity curves (injected — no data access in this module).
    Warmup: N/A (applied by the engine before the forward window is cropped).
    Output: scalar Sharpe delta; fenced flags.
    Null policy: compute_sharpe_ratio handles degenerate/constant returns.
    """
    arr_gated, arr_baseline = _validate_equity_pair(
        gated_equity, baseline_equity, caller="oi_marginal_d1"
    )
    gated_sharpe = compute_sharpe_ratio(_per_bar_returns(arr_gated))
    baseline_sharpe = compute_sharpe_ratio(_per_bar_returns(arr_baseline))
    return {
        "hyp_id": hyp_id,
        "gated_sharpe": gated_sharpe,
        "baseline_sharpe": baseline_sharpe,
        "d1_marginal_sharpe": gated_sharpe - baseline_sharpe,
        # FENCE (structural constants; never derived from inputs).
        "promotion_affecting": False,
        "in_n_star": False,
    }


def d1_noninert(d1_marginal_sharpe: float) -> bool:
    """True if |d1_marginal_sharpe| exceeds the pre-registered inertness threshold.

    Pre-registered threshold: D1_NONINERT_THRESHOLD = 0.10 Sharpe units (see module
    docstring). A D1-non-inert result means the OI gate materially changes the Sharpe
    relative to the no-OI baseline; the diagnostic is substantive. D1-inert means
    both gated and no-OI baseline are near-equivalent (no real gate effect).

    Args:
        d1_marginal_sharpe: The ``d1_marginal_sharpe`` value from oi_marginal_d1.

    Returns:
        bool — True if |d1_marginal_sharpe| > D1_NONINERT_THRESHOLD.
    """
    return abs(d1_marginal_sharpe) > D1_NONINERT_THRESHOLD


def contamination_correlations(df: pd.DataFrame) -> dict:
    """Fenced contamination-correlation set: oi_velocity_ewm_240 vs return/vol series.

    NET-NEW for Path D. Computes Pearson AND Spearman correlations of
    ``df["oi_velocity_ewm_240"]`` against each of:
      - ``return_1h``
      - ``abs_return_1h`` (derived locally as ``df["return_1h"].abs()`` if not a column)
      - ``realized_vol_24h``
      - ``cdf_realized_vol_720``

    Drops NaN pairwise per series (independent pairwise alignment per pair).
    Measured and reported only — never a control over N* or promotion.

    Args:
        df: DataFrame containing at minimum ``oi_velocity_ewm_240`` and ``return_1h``
            (and optionally ``abs_return_1h``, ``realized_vol_24h``,
            ``cdf_realized_vol_720``). Non-NaN rows per pair are used independently.

    Returns:
        Dict with keys:
          ``pearson``  — {series_name: r_value, ...} for the 4 series
          ``spearman`` — {series_name: rho_value, ...} for the 4 series
          ``promotion_affecting`` — always False (structural constant)
          ``in_n_star``           — always False (structural constant)

    Inputs: aligned DataFrame with OI + return/vol columns.
    Warmup: applied upstream; caller must pass the evaluation-window frame only.
    Output: correlation scalars per series; fenced flags.
    Null policy: returns np.nan for any pair with fewer than 2 non-NaN shared rows.
    """
    oi_vel = df["oi_velocity_ewm_240"]

    # Derive abs_return_1h locally — it is NOT a registered factor.
    if "abs_return_1h" in df.columns:
        abs_ret = df["abs_return_1h"]
    else:
        abs_ret = df["return_1h"].abs()

    series_map: dict[str, pd.Series] = {
        "return_1h": df["return_1h"],
        "abs_return_1h": abs_ret,
        "realized_vol_24h": df["realized_vol_24h"],
        "cdf_realized_vol_720": df["cdf_realized_vol_720"],
    }

    pearson_out: dict[str, float] = {}
    spearman_out: dict[str, float] = {}

    for name, other in series_map.items():
        # Pairwise non-NaN alignment.
        combined = pd.DataFrame({"oi": oi_vel, "other": other}).dropna()
        if len(combined) < 2:
            pearson_out[name] = float("nan")
            spearman_out[name] = float("nan")
        else:
            x = combined["oi"].to_numpy()
            y = combined["other"].to_numpy()
            r, _ = stats.pearsonr(x, y)
            rho, _ = stats.spearmanr(x, y)
            pearson_out[name] = float(r)
            spearman_out[name] = float(rho)

    return {
        "pearson": pearson_out,
        "spearman": spearman_out,
        # FENCE (structural constants; never derived from inputs).
        "promotion_affecting": False,
        "in_n_star": False,
    }
