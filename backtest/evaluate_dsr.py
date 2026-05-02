"""Post-hoc multiple-testing evaluation for backtest Sharpe ratios.

When N strategies are evaluated, the best Sharpe is biased upward
because it is the maximum of N draws. This script provides a
heuristic correction using the expected maximum Sharpe threshold:

    SR_threshold = sqrt(2 * ln(N))

where N is the number of independent trials. If SR_max < SR_threshold,
the best strategy does NOT survive multiple-testing correction.

THIS IS AN APPROXIMATE SCREEN — a conservative (Bonferroni-style)
heuristic, not a definitive statistical certification. It does NOT
implement the full Bailey–López de Prado Deflated Sharpe Ratio,
which requires careful handling of skewness, kurtosis, and
autocorrelation. If production-grade DSR is needed, it will be a
dedicated effort with proper statistical review.

Usage:
    python -m backtest.evaluate_dsr --split-version v1
    python -m backtest.evaluate_dsr --split-version v1 --run-type single_run
    python -m backtest.evaluate_dsr --split-version v1 --strategy sma_crossover
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# PHASE2C_11_PLAN §3.4 + §4.4(5) v3.1 reframed register lockpoint.
# Cross-validation operates as DESCRIPTIVE consistency sanity-check (NOT
# primary-exclusion lockpoint substance). Discrepancies above the
# threshold are documented + reviewer-routed; candidates are NOT
# auto-excluded unless materially larger than CSV 6-decimal storage
# precision floor (~5e-7). Tolerance value calibrated per METHODOLOGY_NOTES
# §20 Trigger 5 (canonical-artifact register-precision floor; one OOM
# above empirical CSV storage floor).
JSON_VS_CSV_TOLERANCE = 1e-6

# §4.4(1) pre-registered exclusion threshold for low trade count.
MIN_TRADES_FOR_PRIMARY = 5

# §3.2 lockpoint: PHASE2C_11_PLAN audit_v1 candidate count.
EXPECTED_N_RAW = 198


def compute_expected_max_sharpe(n_trials: int) -> float:
    """Compute the expected maximum Sharpe threshold for N trials.

    Uses the approximation: SR_threshold = sqrt(2 * ln(N)).
    This is the expected value of the maximum of N independent
    draws from a standard normal distribution (Bonferroni-style bound).

    Args:
        n_trials: Number of independent strategy trials.

    Returns:
        Threshold Sharpe ratio. Returns 0.0 for N <= 1.
    """
    if n_trials <= 1:
        return 0.0
    return math.sqrt(2.0 * math.log(n_trials))


def evaluate_trials(
    sharpe_ratios: dict[str, float],
) -> dict[str, Any]:
    """Evaluate a set of strategy Sharpe ratios against the multiple-testing threshold.

    Args:
        sharpe_ratios: Mapping of strategy_name (or run_id) to Sharpe ratio.

    Returns:
        Dict with evaluation results:
            n_trials, threshold, best_strategy, best_sharpe,
            worst_sharpe, mean_sharpe, survives, rankings.
    """
    if not sharpe_ratios:
        return {
            "n_trials": 0,
            "threshold": 0.0,
            "best_strategy": None,
            "best_sharpe": None,
            "worst_sharpe": None,
            "mean_sharpe": None,
            "survives": False,
            "rankings": [],
        }

    n = len(sharpe_ratios)
    threshold = compute_expected_max_sharpe(n)

    # Sort by Sharpe descending
    rankings = sorted(
        sharpe_ratios.items(), key=lambda x: x[1], reverse=True
    )

    best_name, best_sharpe = rankings[0]
    worst_sharpe = rankings[-1][1]
    mean_sharpe = sum(sharpe_ratios.values()) / n

    survives = best_sharpe > threshold

    return {
        "n_trials": n,
        "threshold": threshold,
        "best_strategy": best_name,
        "best_sharpe": best_sharpe,
        "worst_sharpe": worst_sharpe,
        "mean_sharpe": mean_sharpe,
        "survives": survives,
        "rankings": [
            {"strategy": name, "sharpe": sr} for name, sr in rankings
        ],
    }


def query_sharpe_ratios(
    split_version: str,
    run_type: str = "walk_forward_summary",
    strategy_name: str | None = None,
    db_path: Path | None = None,
) -> dict[str, float]:
    """Query Sharpe ratios from the experiment registry.

    Args:
        split_version: Filter by split_version (e.g. "v1").
        run_type: Filter by run_type (default "walk_forward_summary").
        strategy_name: Optional filter by strategy_name.
        db_path: Path to experiments.db. Uses default if None.

    Returns:
        Dict mapping "strategy_name (run_id[:8])" to Sharpe ratio.
        Excludes runs with NULL sharpe_ratio.
    """
    from backtest.experiment_registry import create_table, get_connection

    conn = get_connection(db_path)
    try:
        create_table(conn)

        query = (
            "SELECT run_id, strategy_name, sharpe_ratio "
            "FROM runs "
            "WHERE split_version = ? AND run_type = ? "
            "AND sharpe_ratio IS NOT NULL"
        )
        params: list[Any] = [split_version, run_type]

        if strategy_name:
            query += " AND strategy_name = ?"
            params.append(strategy_name)

        query += " ORDER BY sharpe_ratio DESC"

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
    finally:
        conn.close()

    result: dict[str, float] = {}
    for row in rows:
        # Use "strategy_name (run_id[:8])" as key for uniqueness
        key = f"{row['strategy_name']} ({row['run_id'][:8]})"
        result[key] = float(row["sharpe_ratio"])

    return result


def print_report(evaluation: dict[str, Any]) -> None:
    """Print a human-readable DSR evaluation report.

    Args:
        evaluation: Dict from evaluate_trials().
    """
    n = evaluation["n_trials"]

    if n == 0:
        print("\n  No trials found matching the query filters.")
        print("  Check --split-version, --run-type, and --strategy flags.\n")
        return

    threshold = evaluation["threshold"]
    best = evaluation["best_sharpe"]
    survives = evaluation["survives"]

    print(f"\n{'='*65}")
    print(f"  MULTIPLE-TESTING EVALUATION (Heuristic Approximation)")
    print(f"{'='*65}")
    print()
    print(f"  NOTE: This is an approximate screen using the expected")
    print(f"  maximum Sharpe threshold SR* = sqrt(2 * ln(N)), NOT the")
    print(f"  full Bailey-López de Prado Deflated Sharpe Ratio.")
    print()
    print(f"  Trials (N):           {n}")
    print(f"  Threshold SR*:        {threshold:.4f}")
    print(f"  Best Sharpe:          {best:.4f}")
    print(f"  Worst Sharpe:         {evaluation['worst_sharpe']:.4f}")
    print(f"  Mean Sharpe:          {evaluation['mean_sharpe']:.4f}")
    print()

    verdict = "SURVIVES" if survives else "DOES NOT SURVIVE"
    print(f"  Best strategy {verdict} multiple-testing correction")
    if survives:
        print(f"  ({best:.4f} > {threshold:.4f})")
    else:
        print(f"  ({best:.4f} <= {threshold:.4f})")

    print(f"\n  {'Rank':<6s} {'Sharpe':>8s}  {'Strategy'}")
    print(f"  {'-'*6} {'-'*8}  {'-'*40}")
    for i, entry in enumerate(evaluation["rankings"], start=1):
        marker = " *" if i == 1 and survives else ""
        print(f"  {i:<6d} {entry['sharpe']:>8.4f}  {entry['strategy']}{marker}")

    print(f"\n{'='*65}\n")


# ---------------------------------------------------------------------------
# PHASE2C_11 Step 2 input loading (simplified DSR-style screen inputs)
# ---------------------------------------------------------------------------
#
# References:
#   PHASE2C_11_PLAN §4.2 (inputs required); §4.4 (edge case handling);
#   §3.3 (JSON canonical scalar source); §3.4 + §4.4(5) v3.1 reframed
#   register (descriptive sanity-check at 1e-6 tolerance, NOT primary-
#   exclusion); §3.2 (n_raw=198 lockpoint); RS-2 lockpoint at every
#   audit_v1 artifact consumption per Section RS canonical hard
#   prohibition (backtest/wf_lineage.check_evaluation_semantics_or_raise).


@dataclass(frozen=True)
class CandidateInput:
    """Per-candidate input for the simplified DSR-style screen.

    See PHASE2C_11_PLAN §4.2 (inputs table) + §4.5 API surface. Fields:
        hypothesis_hash: 16-char DSL truncated hash (audit_v1 register).
        sharpe_ratio: per-candidate Sharpe scalar (canonical from
            audit_v1 holdout_summary.json holdout_metrics.sharpe_ratio
            per §3.3 lockpoint; consumed unchanged from engine output).
        total_trades: per-candidate trade count, used by §4.4(1)
            edge-case filter.
        audit_v1_artifact_path: absolute path to the source
            holdout_summary.json file for traceability.
        name, theme, lifecycle_state: descriptive fields carried forward
            for Step 4 result interpretation register only.
    """

    hypothesis_hash: str
    sharpe_ratio: float
    total_trades: int
    audit_v1_artifact_path: str
    name: str
    theme: str
    lifecycle_state: str


@dataclass(frozen=True)
class CandidateExclusion:
    """Per-candidate exclusion record per §4.4 edge-case filter.

    The ``reason`` field is one of the pre-registered exclusion reasons
    from §4.4 plus the safe-validation companion class introduced for
    audit clarity per Codex review HIGH-finding-#3:

      - "low_trade_count" (§4.4(1); 0 < T_c < MIN_TRADES_FOR_PRIMARY)
      - "zero_trades" (§4.4(2); T_c == 0)
      - "missing_sharpe" (§4.4(3); sharpe_ratio missing/null/non-finite
        in JSON)
      - "missing_trades" (companion to §4.4(3) for audit-trail
        precision; total_trades missing/null/non-finite/non-integral
        in JSON. Equivalent to "the canonical T_c scalar cannot be
        validated"; pre-registered §4.4 outcome — exclusion — is
        preserved.)

    JSON-vs-CSV discrepancy (§4.4(5) v3.1 reframed) does NOT produce
    auto-exclusion under v3.1 lockpoint; it produces a descriptive
    discrepancy entry in ``SimplifiedDSRInputs.discrepancies_documented``
    only.
    """

    hypothesis_hash: str
    reason: str
    total_trades: int | None
    sharpe_ratio: float | None


@dataclass(frozen=True)
class SimplifiedDSRInputs:
    """PHASE2C_11 Step 2 deliverable: simplified DSR-style screen inputs.

    Produced by ``load_audit_v1_candidates``. All fields are pre-result
    descriptive register only — no DSR-style screen disposition fires
    here. Step 3 ``compute_simplified_dsr`` (forthcoming) consumes
    ``eligible_candidates`` + ``n_raw`` to produce the screen result.

    Fields:
        eligible_candidates: candidates surviving §4.4 edge-case
            filtering; eligible for Step 3 simplified DSR-style screen.
        excluded_candidates: candidates failing §4.4(1)/(2)/(3); each
            entry documents the exclusion reason at register-precision.
        n_raw: full canonical population per §3.2 lockpoint
            (= len(eligible) + len(excluded)).
        n_eligible: eligible-subset size after §4.4 filtering.
        sharpe_*: cross-trial Sharpe distribution descriptors over
            ``eligible_candidates`` (mean, var (ddof=1), std (ddof=1),
            min, max, median).
        discrepancies_documented: JSON-vs-CSV discrepancies at
            |delta| > JSON_VS_CSV_TOLERANCE per §3.4 + §4.4(5) v3.1
            reframed register; descriptive only — candidates are NOT
            auto-excluded. Each entry: {"hypothesis_hash", "column",
            "json_value", "csv_value", "delta"}.
    """

    eligible_candidates: list[CandidateInput]
    excluded_candidates: list[CandidateExclusion]
    n_raw: int
    n_eligible: int
    sharpe_mean: float
    sharpe_var: float
    sharpe_std: float
    sharpe_min: float
    sharpe_max: float
    sharpe_median: float
    discrepancies_documented: list[dict[str, Any]] = field(default_factory=list)


# Mapping CSV columns → JSON paths for §3.4 + §4.4(5) v3.1 cross-check.
# JSON path is a tuple traversed from the loaded summary dict.
_CSV_TO_JSON: dict[str, tuple[str, ...]] = {
    "holdout_sharpe": ("holdout_metrics", "sharpe_ratio"),
    "holdout_max_drawdown": ("holdout_metrics", "max_drawdown"),
    "holdout_total_return": ("holdout_metrics", "total_return"),
    "holdout_total_trades": ("holdout_metrics", "total_trades"),
    "wf_test_period_sharpe": ("wf_test_period_sharpe",),
}


def _resolve_json_path(summary: dict[str, Any], path: tuple[str, ...]) -> Any:
    cursor: Any = summary
    for key in path:
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(key)
        if cursor is None:
            return None
    return cursor


def _safe_float(value: Any) -> float | None:
    """Parse ``value`` to a finite float, returning ``None`` for any
    missing / empty / non-numeric / non-finite input.

    Non-finite floats (``NaN``, ``inf``, ``-inf``) are rejected per
    Codex review HIGH-finding-#2: they would otherwise silently enter
    the eligible-subset Sharpe statistics and poison ``fmean`` /
    ``variance`` / ``min`` / ``max`` computations. NaN propagation
    through the simplified DSR-style screen at Step 3 would corrupt
    the canonical screen output.
    """
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _safe_int_count(value: Any) -> int | None:
    """Parse ``value`` to a non-negative integer trade count, returning
    ``None`` for any missing / empty / non-numeric / non-finite /
    non-integral / negative input.

    Defensive helper per Codex review MEDIUM-finding-#5: ``int(...)``
    on raw JSON / CSV values raises on non-numeric strings, NaN, and
    non-integral floats; this helper applies the canonical-input-
    register precision policy (engine emits trade counts as integers;
    anything else is malformed input).
    """
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    if parsed < 0:
        return None
    rounded = int(parsed)
    if float(rounded) != parsed:
        # Rejects non-integral floats like 4.5 (engine would never
        # emit a fractional trade count).
        return None
    return rounded


def load_audit_v1_candidates(
    audit_v1_dir: Path,
    csv_path: Path,
    *,
    expected_n_raw: int | None = None,
) -> SimplifiedDSRInputs:
    """Load PHASE2C_11 Step 2 simplified DSR-style screen inputs.

    Per PHASE2C_11_PLAN §7.1 Step 2 + §4.2 + §4.4 + §3.3 + §3.4 v3.1
    reframed register:

    1. Iterate every per-candidate directory under ``audit_v1_dir``;
       load ``holdout_summary.json``.
    2. RS-2 lockpoint: call
       ``backtest.wf_lineage.check_evaluation_semantics_or_raise(...)``
       on every loaded summary BEFORE field access. If any candidate
       fails the RS-2 attestation, raise ``ValueError`` (no silent
       skip) — failure indicates upstream data corruption requiring
       investigation, not a routine exclusion.
    3. §3.3 lockpoint: read ``holdout_metrics.sharpe_ratio`` unchanged
       from engine output as the canonical scalar.
    4. §4.4 edge-case filtering. Per pre-registered §4.4 spec ordering
       (1)/(2)/(3) the canonical reason classes are low_trade_count
       (T_c<5) → zero_trades (T_c==0) → missing_sharpe (null SR).
       Code-level resolution per Codex review HIGH-finding-#3: safe
       scalar validation precedes semantic classification because
       missing/non-finite values cannot be classified by their value.
       Resolution policy:
        (a) if ``total_trades`` is missing / non-numeric / non-finite
            / non-integral / negative → reason="missing_trades"
        (b) elif ``sharpe_ratio`` is missing / non-numeric / non-finite
            → reason="missing_sharpe"
        (c) elif ``total_trades == 0`` → reason="zero_trades"
            (§4.4(2); zero-trade is the more-specific subclass of
            §4.4(1) low_trade_count and is recorded distinctly for
            audit clarity)
        (d) elif ``total_trades < MIN_TRADES_FOR_PRIMARY`` → reason=
            "low_trade_count" (§4.4(1))
       Eligibility outcome (eligible vs excluded) is invariant under
       this resolution; only the audit-trail reason label distinguishes
       the overlap cases. The pre-registered exclusion *outcome* per
       §4.4 (1)/(2)/(3) is fully preserved.
    5. §3.4 + §4.4(5) v3.1 reframed register: cross-check JSON
       against ``holdout_results.csv`` aggregate row at ``csv_path``.
       Discrepancies at ``|delta| > JSON_VS_CSV_TOLERANCE`` (1e-6) are
       recorded in ``discrepancies_documented`` for descriptive
       reviewer routing; candidates are NOT auto-excluded under v3.1
       lockpoint. Per Codex review HIGH-finding-#4: missing CSV row
       for an eligible candidate, missing CSV column value, and
       missing JSON path value are themselves consistency observations
       and are recorded as discrepancy entries with ``kind`` = one of
       {"missing_csv_row", "missing_csv_value", "missing_json_value",
       "delta_above_tolerance"} rather than silently skipped.
    6. Compute cross-trial Sharpe distribution descriptors over the
       eligible subset.

    Args:
        audit_v1_dir: directory containing per-candidate
            ``<hypothesis_hash>/holdout_summary.json`` subdirectories.
        csv_path: path to ``holdout_results.csv`` aggregate file used
            for §3.4 + §4.4(5) cross-check.
        expected_n_raw: when not None, the loader hard-fails with
            ``ValueError`` unless the resolved ``n_raw`` (= eligible +
            excluded) equals this value. Production PHASE2C_11 cycles
            pass ``EXPECTED_N_RAW`` (= 198) per §3.2 lockpoint to
            prevent silent miscount when a candidate directory is
            absent or extra. Synthetic tests opt out by leaving the
            default ``None``. Per Codex review CRITICAL-finding-#1.

    Returns:
        SimplifiedDSRInputs with eligible candidates, excluded candidate
        list, cross-trial scalars, and documented JSON-vs-CSV
        discrepancies.

    Raises:
        ValueError: if any candidate's holdout_summary.json fails the
            RS-2 attestation check (Section RS canonical hard
            prohibition); or if ``expected_n_raw`` is set and the
            resolved n_raw does not match.
        FileNotFoundError: if audit_v1_dir or csv_path do not exist.
    """
    # Late import keeps module import-time cheap and avoids forcing
    # wf_lineage on consumers that don't use the audit_v1 loader.
    from backtest.wf_lineage import check_evaluation_semantics_or_raise

    audit_v1_dir = Path(audit_v1_dir)
    csv_path = Path(csv_path)
    if not audit_v1_dir.is_dir():
        raise FileNotFoundError(f"audit_v1 directory not found: {audit_v1_dir}")
    if not csv_path.is_file():
        raise FileNotFoundError(f"holdout_results.csv not found: {csv_path}")

    # Build CSV index keyed by hypothesis_hash for §3.4 cross-check.
    csv_index: dict[str, dict[str, str]] = {}
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_index[row["hypothesis_hash"]] = row

    eligible: list[CandidateInput] = []
    excluded: list[CandidateExclusion] = []
    discrepancies: list[dict[str, Any]] = []

    for cand_dir in sorted(p for p in audit_v1_dir.iterdir() if p.is_dir()):
        json_path = cand_dir / "holdout_summary.json"
        if not json_path.is_file():
            # Step 1 verification confirmed all 198 directories carry
            # holdout_summary.json; absence here indicates corruption.
            raise FileNotFoundError(
                f"holdout_summary.json missing at {json_path}"
            )
        summary = json.loads(json_path.read_text(encoding="utf-8"))

        # RS-2 lockpoint: refuse processing if attestation check fails.
        # Raises ValueError; do NOT silently skip.
        check_evaluation_semantics_or_raise(
            summary, artifact_path=str(json_path),
        )

        h = summary.get("hypothesis_hash") or cand_dir.name
        metrics = summary.get("holdout_metrics") or {}
        sharpe = _safe_float(metrics.get("sharpe_ratio"))
        trades = _safe_int_count(metrics.get("total_trades"))

        # §4.4 edge cases — see docstring resolution policy. Safe scalar
        # validation precedes semantic classification because missing /
        # non-finite values cannot be classified by their value.
        if trades is None:
            excluded.append(CandidateExclusion(
                hypothesis_hash=h,
                reason="missing_trades",
                total_trades=None,
                sharpe_ratio=sharpe,
            ))
            continue
        if sharpe is None:
            # §4.4(3) missing/null sharpe (or non-finite / non-numeric
            # per _safe_float defensive policy).
            excluded.append(CandidateExclusion(
                hypothesis_hash=h,
                reason="missing_sharpe",
                total_trades=trades,
                sharpe_ratio=None,
            ))
            continue
        if trades == 0:
            # §4.4(2) zero-trade (Sharpe undefined at trade-level even
            # if engine emitted 0.0 scalar). More-specific subclass of
            # §4.4(1) low_trade_count; recorded distinctly for audit
            # clarity.
            excluded.append(CandidateExclusion(
                hypothesis_hash=h,
                reason="zero_trades",
                total_trades=trades,
                sharpe_ratio=sharpe,
            ))
            continue
        if trades < MIN_TRADES_FOR_PRIMARY:
            # §4.4(1) low trade count (0 < T_c < MIN_TRADES_FOR_PRIMARY).
            excluded.append(CandidateExclusion(
                hypothesis_hash=h,
                reason="low_trade_count",
                total_trades=trades,
                sharpe_ratio=sharpe,
            ))
            continue

        # §3.4 + §4.4(5) v3.1 cross-check: descriptive only at v3.1
        # reframed register — discrepancies documented but candidate
        # NOT auto-excluded. Per Codex HIGH-finding-#4: missing rows /
        # values are themselves consistency observations and are
        # recorded as typed discrepancy entries.
        csv_row = csv_index.get(h)
        if csv_row is None:
            discrepancies.append({
                "hypothesis_hash": h,
                "kind": "missing_csv_row",
                "column": None,
                "json_value": None,
                "csv_value": None,
                "delta": None,
            })
        else:
            for col, json_path_keys in _CSV_TO_JSON.items():
                raw_csv = csv_row.get(col, "")
                raw_json = _resolve_json_path(summary, json_path_keys)
                csv_val = _safe_float(raw_csv)
                json_val = _safe_float(raw_json)
                if csv_val is None and json_val is None:
                    # Both sides absent: treat as missing-on-both
                    # (could be e.g. wf_test_period_sharpe legitimately
                    # null in older partitions); record once for audit.
                    discrepancies.append({
                        "hypothesis_hash": h,
                        "kind": "missing_both",
                        "column": col,
                        "json_value": None,
                        "csv_value": None,
                        "delta": None,
                    })
                    continue
                if csv_val is None:
                    discrepancies.append({
                        "hypothesis_hash": h,
                        "kind": "missing_csv_value",
                        "column": col,
                        "json_value": json_val,
                        "csv_value": None,
                        "delta": None,
                    })
                    continue
                if json_val is None:
                    discrepancies.append({
                        "hypothesis_hash": h,
                        "kind": "missing_json_value",
                        "column": col,
                        "json_value": None,
                        "csv_value": csv_val,
                        "delta": None,
                    })
                    continue
                delta = abs(csv_val - json_val)
                if delta > JSON_VS_CSV_TOLERANCE:
                    discrepancies.append({
                        "hypothesis_hash": h,
                        "kind": "delta_above_tolerance",
                        "column": col,
                        "json_value": json_val,
                        "csv_value": csv_val,
                        "delta": delta,
                    })

        eligible.append(CandidateInput(
            hypothesis_hash=h,
            sharpe_ratio=sharpe,
            total_trades=trades,
            audit_v1_artifact_path=str(json_path),
            name=str(summary.get("name", "")),
            theme=str(summary.get("theme", "")),
            lifecycle_state=str(summary.get("lifecycle_state", "")),
        ))

    n_raw = len(eligible) + len(excluded)
    n_eligible = len(eligible)

    # CRITICAL #1: enforce §3.2 lockpoint (n_raw == EXPECTED_N_RAW for
    # production PHASE2C_11 cycles). Synthetic tests pass
    # ``expected_n_raw=None`` to opt out.
    if expected_n_raw is not None and n_raw != expected_n_raw:
        raise ValueError(
            f"n_raw lockpoint violation: expected {expected_n_raw} "
            f"candidates per §3.2, found {n_raw} at "
            f"{audit_v1_dir}. Refusing to silently miscount; "
            f"investigate missing/extra candidate directories."
        )

    if n_eligible == 0:
        # Degenerate eligible set; no Sharpe distribution computable.
        # §4.4(4) Var(SR) == 0 / undefined will be re-checked by Step 3
        # against this state.
        return SimplifiedDSRInputs(
            eligible_candidates=eligible,
            excluded_candidates=excluded,
            n_raw=n_raw,
            n_eligible=0,
            sharpe_mean=float("nan"),
            sharpe_var=float("nan"),
            sharpe_std=float("nan"),
            sharpe_min=float("nan"),
            sharpe_max=float("nan"),
            sharpe_median=float("nan"),
            discrepancies_documented=discrepancies,
        )

    sharpes = [c.sharpe_ratio for c in eligible]
    sharpe_mean = statistics.fmean(sharpes)
    sharpe_var = statistics.variance(sharpes) if len(sharpes) > 1 else 0.0
    sharpe_std = math.sqrt(sharpe_var) if sharpe_var > 0 else 0.0

    return SimplifiedDSRInputs(
        eligible_candidates=eligible,
        excluded_candidates=excluded,
        n_raw=n_raw,
        n_eligible=n_eligible,
        sharpe_mean=sharpe_mean,
        sharpe_var=sharpe_var,
        sharpe_std=sharpe_std,
        sharpe_min=min(sharpes),
        sharpe_max=max(sharpes),
        sharpe_median=statistics.median(sharpes),
        discrepancies_documented=discrepancies,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point for multiple-testing evaluation.

    Returns:
        Exit code: 0 on success.
    """
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Post-hoc multiple-testing evaluation of backtest Sharpe ratios. "
            "Uses SR* = sqrt(2*ln(N)) as an approximate threshold."
        ),
    )
    parser.add_argument(
        "--split-version",
        type=str,
        required=True,
        help="Filter runs by split_version (e.g. v1)",
    )
    parser.add_argument(
        "--run-type",
        type=str,
        default="walk_forward_summary",
        help="Filter by run_type (default: walk_forward_summary)",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default=None,
        help="Optional: filter by strategy_name",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Path to experiments.db (uses default if omitted)",
    )
    args = parser.parse_args()

    db_path = Path(args.db) if args.db else None

    sharpe_ratios = query_sharpe_ratios(
        split_version=args.split_version,
        run_type=args.run_type,
        strategy_name=args.strategy,
        db_path=db_path,
    )

    evaluation = evaluate_trials(sharpe_ratios)
    print_report(evaluation)

    return 0


if __name__ == "__main__":
    sys.exit(main())
