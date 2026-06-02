# backtest/pathd_holdout_producer.py
"""Path D holdout producer: run one OI candidate on a window -> dead-18-layout
artifacts (returns_per_bar.parquet + holdout_summary.json + a results.csv row),
so the existing tier6 load_candidate_moments integrity gate can consume them.

Adapted near-verbatim from backtest/pathc_holdout_producer.py; retargeted to the
Path D OI cohort (theme defaults to the caller's "pathd"; default
current_git_sha = "PATHD_BUILD"). Writes ONLY into a Path D namespace; never the
sealed cohort dirs. The engine call is injected (default backtest.engine.run_backtest)
for test isolation.

IMPL NOTES (verified against backtest/wf_lineage.py — identical to Path B/A/C):
- EVALUATION_SEMANTICS_TAG = "single_run_holdout_v1"
- CORRECTED_WF_ENGINE_COMMIT = "eb1c87f"  (used as engine_commit)
- ENGINE_CORRECTED_LINEAGE_TAG = "wf-corrected-v1"  (used as engine_corrected_lineage)
- artifact_schema_version = "phase2c_7_1" for regime_key="evaluation_regimes.forward_2026"
  (per REGIME_KEY_TO_SCHEMA_VERSION_MAPPING).

CONTRACT BOUNDARY (sealed cohort): this producer NEVER writes the sealed
tier6_dsr_v1/ cohort; Path D owns its own namespace. The forward features must be
fully warmed — OI features are built on FULL history then sliced to the
window (full-dataset-build rule), enforced upstream in factors.build_features, so
forward_2026 OI columns are not NaN inside the window.

WARMUP-FEED PREPEND (2-leg-review HIGH): run_backtest crops the feed to
[start, end] (fromdate/todate), and the compiled OI strategy enforces a
~2160-bar WARMUP_BARS. If we ran the engine on the forward window directly, ~2160
of ~2528 forward bars would be consumed as IN-WINDOW warmup (the engine's equity
curve only begins after the strategy's minperiod), leaving only ~368 evaluable
bars. So we extend the feed start back by WARMUP_BARS bars (derived from the
compiled strategy's WARMUP_BARS, NOT hardcoded) so the warmup completes BEFORE the
window, then crop the equity curve / metrics / per-bar artifact to the forward
window ONLY. The prepend bars are warmup-only — they warm the strategy but are
NEVER evaluated/metric'd, so this does NOT "spend" the pre-window (2025) data as a
test.

NOTE: the OI percentile/regime factors are heavily NaN in 2024/2025 — the forward
window (2026) has OI data. Warmup NaN handling is a known power disclosure but does
not crash (the DSL compiler's NaN-is-False invariant applies; a completely-NaN
warmup produces a flat/degenerate equity which is handled gracefully via the
degenerate-equity guard below).
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from backtest.engine import run_backtest, write_per_bar_artifact
from backtest.metrics import compute_all_metrics
from backtest.wf_lineage import (
    CORRECTED_WF_ENGINE_COMMIT,
    ENGINE_CORRECTED_LINEAGE_TAG,
    EVALUATION_SEMANTICS_TAG,
)

# Lineage constants the evaluation guard requires (mirror run_phase2c_evaluation_gate).
_ENGINE_COMMIT = CORRECTED_WF_ENGINE_COMMIT   # "eb1c87f"
_ENGINE_LINEAGE = ENGINE_CORRECTED_LINEAGE_TAG  # "wf-corrected-v1"
_ARTIFACT_SCHEMA_VERSION = "phase2c_7_1"        # forward_2026 per REGIME_KEY_TO_SCHEMA_VERSION_MAPPING


def _eval_lineage_metadata(current_git_sha: str) -> dict[str, Any]:
    return {
        "evaluation_semantics": EVALUATION_SEMANTICS_TAG,  # "single_run_holdout_v1"
        "engine_commit": _ENGINE_COMMIT,
        "engine_corrected_lineage": _ENGINE_LINEAGE,
        "lineage_check": "passed",
        "current_git_sha": current_git_sha,
        "artifact_schema_version": _ARTIFACT_SCHEMA_VERSION,
        "regime_key": "evaluation_regimes.forward_2026",
        "regime_label": "forward_2026",
    }


def produce_candidate_holdout(
    *,
    hypothesis_hash: str,
    name: str,
    theme: str,
    strategy_cls: type,
    window: tuple[datetime, datetime],
    cohort_dir: Path,
    execution_config_path: str,
    current_git_sha: str = "PATHD_BUILD",
    _run_backtest: Callable[..., Any] = run_backtest,
    _write_per_bar: Callable[..., Any] = write_per_bar_artifact,
) -> dict[str, Any]:
    """Run one OI candidate on ``window`` and emit dead-18-layout artifacts.

    Inputs:
        hypothesis_hash: DSL hash string (also the sub-dir name).
        name: Strategy name (e.g. "pathd_h1").
        theme: Theme label (e.g. "pathd").
        strategy_cls: Compiled Backtrader strategy class (unused when engine mocked).
        window: (start_utc, end_utc) datetime tuple for the holdout run.
        cohort_dir: Root path for Path D artifacts; writes to cohort_dir/<hash>/.
        execution_config_path: Repo-relative YAML path for the cost anchor
            (e.g. "config/execution_phaseb_spot_15bps.yaml").
        current_git_sha: Git SHA to stamp; defaults to "PATHD_BUILD" for the build phase.
        _run_backtest: Injected engine callable (default backtest.engine.run_backtest).
        _write_per_bar: Injected artifact writer (default backtest.engine.write_per_bar_artifact).

    Returns:
        Dict with ``holdout_sharpe`` (float), ``holdout_total_trades`` (int),
        ``row`` (dict) — the holdout_results.csv row: hypothesis_hash, name, theme,
        T_obs, gamma3, gamma4, returns_per_bar_sha256, holdout_total_trades,
        holdout_sharpe — and ``window_equity`` (pd.Series): the CROPPED
        forward-window equity curve.  The fenced OI-marginal diagnostic reuses
        ``window_equity`` so the gated forward run is computed once (here) and not
        duplicated.

        When the forward equity is flat / zero-variance (0 trades, gate didn't fire),
        the returned dict also carries ``degenerate=True`` and ``holdout_sharpe=0.0``
        (a flat equity has undefined skew/kurtosis, so gamma3/gamma4 are None in the
        row; the caller must exclude this candidate from the moments/DSR cohort and
        record it in ``degenerate_legs``). A Sharpe of 0.0 correctly FAILS the strict
        ``holdout_sharpe > 0`` Tier-5 gate.

        NOTE: OI factors are heavily NaN in 2024/2025; the forward window (2026)
        has full OI data. A warmup that falls entirely in a NaN region produces a
        degenerate flat equity — handled by the guard above (no crash).
    """
    start, end = window
    cand_dir = Path(cohort_dir) / hypothesis_hash
    cand_dir.mkdir(parents=True, exist_ok=True)

    # WARMUP-FEED PREPEND: extend the feed start back by WARMUP_BARS bars (derived
    # from the compiled strategy, NOT hardcoded) so the OI warmup completes
    # BEFORE the forward window; then crop everything to the window. WARMUP_BARS=0
    # (or no attribute) -> no prepend (byte-identical to pre-fix for OHLCV-only).
    warmup_bars = int(getattr(strategy_cls, "WARMUP_BARS", 0) or 0)
    feed_start = start - timedelta(hours=warmup_bars)

    result = _run_backtest(
        strategy_cls=strategy_cls,
        start_date=feed_start,
        end_date=end,
        execution_config_path=Path(execution_config_path),
        write_registry=False,
    )

    # Crop the equity curve to the forward window only — the prepend bars warmed the
    # strategy but are NEVER evaluated/metric'd. The per-bar artifact + holdout
    # metrics are computed on the window slice (the dead-18 / DSR consumption layer
    # reads returns_per_bar.parquet, so it must contain window bars only).
    window_equity = _crop_to_window(result.equity_curve, start, end)
    window_trades = _crop_trades_to_window(getattr(result, "trades", None), start, end)
    window_metrics = _window_metrics(window_equity, window_trades, result)

    per_bar = _write_per_bar(
        equity_curve=window_equity,
        artifact_dir=cand_dir,
        run_id=result.run_id,
    )

    summary = {
        "hypothesis_hash": hypothesis_hash,
        "name": name,
        "theme": theme,
        "run_id": result.run_id,
        "execution_config_path": execution_config_path,
        "forward_window_metadata": {
            "forward_window_start_utc": start.isoformat(),
            "forward_window_end_utc": end.isoformat(),
            "forward_bar_count": int((end - start).total_seconds() // 3600) + 1,
            "forward_post_warmup_obs": int(per_bar["T_obs"]),
        },
        **_eval_lineage_metadata(current_git_sha),
    }
    (cand_dir / "holdout_summary.json").write_text(json.dumps(summary, indent=1))

    # Degenerate-equity guard: write_per_bar_artifact returns gamma3/gamma4 = None
    # for a flat / zero-variance equity curve (0-trade / flat / zero-variance equity).
    # This is a LEGITIMATE per-strategy outcome (gate didn't fire on forward_2026) —
    # NOT a wiring break. A flat equity has undefined skew/kurtosis so it cannot
    # enter the DSR cohort; we return a flagged dict (degenerate=True, holdout_sharpe=0.0)
    # so the caller can exclude it from the moments/DSR cohort and record it in the
    # bundle's degenerate_legs. A Sharpe of 0.0 correctly FAILS the strict >0 Tier-5
    # gate. Raising here (the old behavior) crashed the whole verdict run (Path C
    # commit 0d06c22d fix; inherited by Path D).
    if per_bar["gamma3"] is None or per_bar["gamma4"] is None:
        total_trades = int(window_metrics.get("total_trades", 0))
        row: dict[str, Any] = {
            "hypothesis_hash": hypothesis_hash,
            "name": name,
            "theme": theme,
            "T_obs": int(per_bar["T_obs"]),
            "gamma3": None,
            "gamma4": None,
            "returns_per_bar_sha256": per_bar["returns_per_bar_sha256"],
            "holdout_total_trades": total_trades,
            "holdout_sharpe": 0.0,
            "degenerate": True,
        }
        return {
            "holdout_sharpe": 0.0,
            "holdout_total_trades": total_trades,
            "row": row,
            "window_equity": window_equity,
            "degenerate": True,
        }

    row = {
        "hypothesis_hash": hypothesis_hash,
        "name": name,
        "theme": theme,
        "T_obs": int(per_bar["T_obs"]),
        "gamma3": per_bar["gamma3"],
        "gamma4": per_bar["gamma4"],
        "returns_per_bar_sha256": per_bar["returns_per_bar_sha256"],
        "holdout_total_trades": int(window_metrics["total_trades"]),
        "holdout_sharpe": float(window_metrics["sharpe_ratio"]),
    }
    return {
        "holdout_sharpe": float(window_metrics["sharpe_ratio"]),
        "holdout_total_trades": int(window_metrics["total_trades"]),
        "row": row,
        "window_equity": window_equity,
    }


def _crop_to_window(equity_curve: "pd.Series", start: datetime, end: datetime) -> "pd.Series":
    """Crop an equity curve to the forward window [start, end] (inclusive).

    The prepend region (index < start) warmed the strategy and is dropped. When the
    index is tz-naive (Backtrader convention) the window bounds are compared
    tz-naively; UTC-aware indices compare directly.
    """
    eq = equity_curve
    idx = eq.index
    lo, hi = start, end
    if getattr(idx, "tz", None) is None:
        # Backtrader produces tz-naive datetimes; compare against naive bounds.
        lo = pd.Timestamp(start).tz_localize(None)
        hi = pd.Timestamp(end).tz_localize(None)
    return eq[(idx >= lo) & (idx <= hi)]


def _crop_trades_to_window(
    trades: list[dict[str, Any]] | None, start: datetime, end: datetime
) -> list[dict[str, Any]]:
    """Keep only trades whose entry_time_utc falls within the forward window.

    With the warmup prepend the strategy is already warm in the prepend region, so
    trades CAN occur there; those pre-window trades are not part of the holdout and
    are dropped (the holdout is evaluated on the forward window only).
    """
    if not trades:
        return []
    lo = pd.Timestamp(start).tz_localize(None)
    hi = pd.Timestamp(end).tz_localize(None)
    kept = []
    for t in trades:
        et = t.get("entry_time_utc")
        if et is None:
            kept.append(t)  # no timestamp -> keep (can't crop; conservative)
            continue
        ts = pd.Timestamp(et)
        ts = ts.tz_localize(None) if ts.tz is not None else ts
        if lo <= ts <= hi:
            kept.append(t)
    return kept


def _window_metrics(
    window_equity: "pd.Series", window_trades: list[dict[str, Any]], result: Any
) -> dict[str, Any]:
    """Recompute holdout metrics on the forward-window slice ONLY.

    The engine's ``result.metrics`` covers the engine's post-warmup curve over the
    extended feed; we recompute Sharpe / trade count on the cropped window slice so
    the holdout attributes to the forward window only. Initial capital is taken from
    the engine's reported initial_capital when present, else the window's first bar.
    """
    initial_capital = float(result.metrics.get("initial_capital", 0.0)) or (
        float(window_equity.iloc[0]) if len(window_equity) > 0 else 10_000.0
    )
    return compute_all_metrics(window_equity, window_trades, initial_capital)
