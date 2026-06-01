# backtest/pathc_marginal_diagnostic.py
"""Fenced dual-orthogonalization diagnostic (Task C6, NET-NEW for Path C).

LOCK Pre-registration 3 fences both D1 and D2 as DIAGNOSTIC-ONLY: they isolate
basis's marginal contribution by comparing the basis-gated strategy's net-of-cost
Sharpe against counterfactual equity curves on the SAME forward bars. So any
result attributes to basis's marginal contribution, not confounds.

Two fenced diagnostics:
  D1 (vs momentum): basis_marginal_d1(hyp_id, gated_equity, baseline_equity)
     Sharpe delta = basis-gated minus the IDENTICAL no-basis baseline (H1 =
     always-long; H2/H3 = price-trend-only). Directly mirrors patha_marginal_
     diagnostic.funding_marginal, retargeted from funding to basis.

  D2 (vs funding): basis_marginal_d2(hyp_id, basis_gated_equity, funding_gated_equity)
     Sharpe delta = basis-gated minus the Path-A FUNDING-gated strategy. Measures
     whether higher-frequency basis (1h) adds over the 8h funding it is derived
     from. The funding-gated equity is INJECTED (the actual funding-gated run is
     wired at Phase D using backtest/patha_eval_gauntlet funding builders); this
     module only computes the delta on the injected curves.

FENCED (DESIGN INVARIANT): neither diagnostic ever feeds N* or promotion. Every
returned record always carries ``promotion_affecting=False`` and ``in_n_star=False``
— these flags are structural constants, not derived from inputs, so no result can
flip them.

Pre-registered tolerances for downstream redundancy_read helpers (pre-data choices;
FLAGGED for Charlie ratification before the Phase-D run):
  D2_AGREES_TOLERANCE = 0.10 — |d2_marginal_sharpe| <= this is considered "agree"
    (basis and funding produce nearly identical Sharpe; redundancy candidate).
    Rationale: a 0.10 Sharpe-unit band is ~equivalent to the measurement noise on
    a ~100-trade forward window at typical BTC vol; smaller tolerances risk false
    disagreements from sampling noise, larger tolerances risk masking genuine info.
  D1_NONINERT_THRESHOLD = 0.10 — |d1_marginal_sharpe| > this is "non-inert"
    (basis gate materially changes the Sharpe relative to the pure-momentum baseline;
    the D1 read is substantive, not noise). Same rationale.

Both tolerances are pre-registered and may only be revised via a Charlie-registered
LOCK amendment before any basis-value peek in the evaluation window.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.metrics import compute_sharpe_ratio

# ---------------------------------------------------------------------------
# Pre-registered tolerances (pre-data choices; FLAGGED for Charlie ratification)
# ---------------------------------------------------------------------------

# CONTRACT GAP (Phase D): these tolerance values are PRE-DATA CHOICES locked here
# before any forward_2026 basis values are observed. Charlie must ratify them at the
# Phase-D register event. If revised, the revision is a LOCK amendment with a
# documented rationale (it is NOT acceptable to adjust them post-peek to change the
# redundancy_read verdict).
D2_AGREES_TOLERANCE: float = 0.10
D1_NONINERT_THRESHOLD: float = 0.10


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
    np.ndarray — two same-length curves on DIFFERENT timestamps are NOT the "same bars"
    and the marginal is only meaningful on aligned bars.
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


def basis_marginal_d1(
    hyp_id: str,
    gated_equity: np.ndarray | pd.Series,
    baseline_equity: np.ndarray | pd.Series,
) -> dict:
    """D1 (vs momentum): fenced basis-marginal Sharpe delta on identical bars.

    Computes ``Sharpe(basis-gated) - Sharpe(no-basis baseline)`` on the SAME
    forward bars. The no-basis baseline is:
      H1 → always-long (built by pathc_eval_gauntlet.build_h1_baseline_dsl)
      H2 → price-trend-only (build_h2_baseline_dsl, max_hold=24)
      H3 → price-trend-only (build_h3_baseline_dsl, max_hold=48)

    Args:
        hyp_id: Hypothesis id ("H1" / "H2" / "H3").
        gated_equity: The basis-gated strategy's equity curve.
        baseline_equity: The no-basis baseline's equity curve on the SAME bars.

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
        gated_equity, baseline_equity, caller="basis_marginal_d1"
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


def basis_marginal_d2(
    hyp_id: str,
    basis_gated_equity: np.ndarray | pd.Series,
    funding_gated_equity: np.ndarray | pd.Series,
) -> dict:
    """D2 (vs funding): fenced basis-vs-funding marginal Sharpe delta on identical bars.

    NET-NEW Path C element. Measures whether higher-frequency basis (1h cadence)
    adds over the 8h funding signal it is derived from by computing
    ``Sharpe(basis-gated) - Sharpe(funding-gated)`` on the SAME bars.

    The funding-gated equity is INJECTED — the actual funding-gated backtest reuses
    backtest/patha_eval_gauntlet funding builders and data/raw/btcusdt_funding_8h.parquet
    and is wired at Phase D. This module only computes the delta on the injected curves.

    D2-agree branch (|d2_marginal_sharpe| <= D2_AGREES_TOLERANCE AND D1 non-inert):
      basis and funding are redundant at both frequencies → "redundancy_confirmed"
      per Pre-reg 3 conjunction (see redundancy_read).
    D2-disagree branch (|d2_marginal_sharpe| > D2_AGREES_TOLERANCE AND D1 non-inert):
      basis carries marginal information over 8h funding; does NOT auto-promote
      (still Tier-5 + DSR + 2025 OOS gated) but blocks the cross-frequency
      redundancy read. Surfaced to Charlie's binding read.

    Args:
        hyp_id: Hypothesis id ("H1" / "H2" / "H3").
        basis_gated_equity: The basis-gated strategy's equity curve.
        funding_gated_equity: The Path-A funding-gated strategy's equity curve
            on the SAME bars (injected; real run is at Phase D).

    Returns:
        Dict: ``hyp_id``, ``basis_sharpe``, ``funding_sharpe``,
        ``d2_marginal_sharpe`` (basis - funding), and the FENCE flags
        ``promotion_affecting=False`` and ``in_n_star=False``.

    Raises:
        ValueError: If the two equity curves do not cover an identical bar count,
            or (when pandas Series are passed) do not share an IDENTICAL index.

    Inputs: equity curves (injected — no data access in this module).
    Warmup: N/A (applied by the engine before the forward window is cropped).
    Output: scalar Sharpe delta; fenced flags.
    Null policy: compute_sharpe_ratio handles degenerate/constant returns.
    """
    arr_basis, arr_funding = _validate_equity_pair(
        basis_gated_equity, funding_gated_equity, caller="basis_marginal_d2"
    )
    basis_sharpe = compute_sharpe_ratio(_per_bar_returns(arr_basis))
    funding_sharpe = compute_sharpe_ratio(_per_bar_returns(arr_funding))
    return {
        "hyp_id": hyp_id,
        "basis_sharpe": basis_sharpe,
        "funding_sharpe": funding_sharpe,
        "d2_marginal_sharpe": basis_sharpe - funding_sharpe,
        # FENCE (structural constants; never derived from inputs).
        "promotion_affecting": False,
        "in_n_star": False,
    }


def d2_agrees(d2_marginal_sharpe: float) -> bool:
    """True if |d2_marginal_sharpe| is within the pre-registered tolerance.

    Pre-registered tolerance: D2_AGREES_TOLERANCE = 0.10 Sharpe units (see module
    docstring). A D2-agree means basis-gated and funding-gated produce nearly
    identical Sharpe; the cross-frequency signal is a candidate for redundancy.

    Args:
        d2_marginal_sharpe: The ``d2_marginal_sharpe`` value from basis_marginal_d2.

    Returns:
        bool — True if |d2_marginal_sharpe| <= D2_AGREES_TOLERANCE.
    """
    return abs(d2_marginal_sharpe) <= D2_AGREES_TOLERANCE


def d1_noninert(d1_marginal_sharpe: float) -> bool:
    """True if |d1_marginal_sharpe| exceeds the pre-registered inertness threshold.

    Pre-registered threshold: D1_NONINERT_THRESHOLD = 0.10 Sharpe units (see module
    docstring). A D1-non-inert result means the basis gate materially changes the
    Sharpe relative to the pure-momentum baseline; the diagnostic is substantive.
    D1-inert means both gated and no-basis baseline are near-equivalent — any D2
    agreement is vacuous (no real gate effect to agree about).

    Args:
        d1_marginal_sharpe: The ``d1_marginal_sharpe`` value from basis_marginal_d1.

    Returns:
        bool — True if |d1_marginal_sharpe| > D1_NONINERT_THRESHOLD.
    """
    return abs(d1_marginal_sharpe) > D1_NONINERT_THRESHOLD


def redundancy_read(d2_agrees: bool, d1_noninert: bool) -> str:  # type: ignore[override]
    """Pinned inference rule from LOCK Pre-registration 3 / Pre-reg 4 §9 Finding D.

    Redundancy is confirmed ONLY by the CONJUNCTION: D2-agree AND D1-non-inert.
    Mutual agreement under jointly-inert D1 is vacuous and licenses no
    redundancy/generalization read.

    Truth table:
      (True,  True)  -> "redundancy_confirmed":  basis ≈ funding AND gate is substantive
      (True,  False) -> "vacuous":               agreement is vacuous (D1 inert)
      (False, True)  -> "basis_adds_signal":     D2-disagree + D1 non-inert; basis
                                                  carries marginal info over 8h funding;
                                                  does NOT auto-promote but blocks the
                                                  cross-frequency redundancy read
      (False, False) -> "vacuous":               both inert; inconclusive

    Args:
        d2_agrees: True if |d2_marginal_sharpe| <= D2_AGREES_TOLERANCE.
        d1_noninert: True if |d1_marginal_sharpe| > D1_NONINERT_THRESHOLD.

    Returns:
        str — one of "redundancy_confirmed", "vacuous", "basis_adds_signal".
    """
    if d2_agrees and d1_noninert:
        return "redundancy_confirmed"
    if not d2_agrees and d1_noninert:
        return "basis_adds_signal"
    # Both remaining combos (True/False and False/False) are vacuous:
    # agreement under inert D1 is uninformative; disagreement under inert D1 is
    # also uninformative (no real gate effect to disagree about).
    return "vacuous"
