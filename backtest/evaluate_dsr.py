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
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal, Mapping

from scipy.stats import norm

from backtest.wf_lineage import check_evaluation_semantics_or_raise

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

# PHASE2C_11_PLAN §3.2 + Step 2 _step2_inputs.json schema v2 canonical
# eligible-subset count after §4.4 filtering at canonical fire. Required
# for compute_simplified_dsr() dual-gate (b) — caller may pass either
# the full canonical population (len == EXPECTED_N_RAW) or the canonical
# eligible subset (len == EXPECTED_N_ELIGIBLE_AT_CANONICAL); any other
# count signals an n_raw mismatch. Hardcoded per PHASE2C_11 canonical
# anchor; will need re-binding if a successor cycle re-evaluates against
# a different candidate basis.
EXPECTED_N_ELIGIBLE_AT_CANONICAL = 154

# Euler–Mascheroni constant γ_e per §4.3 Step 2 Gumbel approximation.
EULER_MASCHERONI = 0.5772156649015329

# §3.6 disposition Literal cross-section anchor; reused at three dataclass
# fields (PerCandidateDisposition.disposition,
# SimplifiedDSRResult.population_disposition,
# SensitivityRow.argmax_disposition_descriptive) per schema §4.
DispositionLiteral = Literal["signal_evidence", "artifact_evidence", "inconclusive"]


def _fire_rs3_guard_on_path(path: str | Path) -> None:
    """Open ``path`` as JSON, parse, and fire RS-3 guard.

    Helper used by ``compute_simplified_dsr`` per-candidate loop and by the
    RS-3 patches on ``compute_expected_max_sharpe`` / ``evaluate_trials``.
    Per (β-mod) hotfix discipline at PHASE2C_11 Step 3 implementation:
    fail-loud on missing/malformed; never silently skip.
    """
    resolved = Path(path)
    with resolved.open() as f:
        summary = json.load(f)
    check_evaluation_semantics_or_raise(summary, artifact_path=resolved)


def compute_expected_max_sharpe(
    n_trials: int,
    *,
    audit_v1_artifact_paths: list[Path] | None = None,
) -> float:
    """Compute the expected maximum Sharpe threshold for N trials.

    Uses the approximation: SR_threshold = sqrt(2 * ln(N)).
    This is the expected value of the maximum of N independent
    draws from a standard normal distribution (Bonferroni-style bound).

    Args:
        n_trials: Number of independent strategy trials.
        audit_v1_artifact_paths: Optional list of audit_v1 holdout summary
            JSON paths. If supplied (RS-3 patch shape (A) per
            PHASE2C_11_PLAN §2.5 + Step 3 implementation): fire
            ``check_evaluation_semantics_or_raise`` on each path before
            computing the threshold. If ``None`` (default): pre-patch
            behavior preserved — no RS-3 fire, no I/O.

    Returns:
        Threshold Sharpe ratio. Returns 0.0 for N <= 1.

    Raises:
        ValueError: If any supplied path fails RS-3 attestation.
    """
    if audit_v1_artifact_paths is not None:
        for path in audit_v1_artifact_paths:
            _fire_rs3_guard_on_path(path)
    if n_trials <= 1:
        return 0.0
    return math.sqrt(2.0 * math.log(n_trials))


def evaluate_trials(
    sharpe_ratios: dict[str, float],
    *,
    audit_v1_artifact_paths: list[Path] | None = None,
) -> dict[str, Any]:
    """Evaluate a set of strategy Sharpe ratios against the multiple-testing threshold.

    Args:
        sharpe_ratios: Mapping of strategy_name (or run_id) to Sharpe ratio.
        audit_v1_artifact_paths: Optional list of audit_v1 holdout summary
            JSON paths. If supplied (RS-3 patch shape (A) per
            PHASE2C_11_PLAN §2.5 + Step 3 implementation): fire
            ``check_evaluation_semantics_or_raise`` on each path before
            computing the evaluation. If ``None`` (default): pre-patch
            behavior preserved.

    Returns:
        Dict with evaluation results:
            n_trials, threshold, best_strategy, best_sharpe,
            worst_sharpe, mean_sharpe, survives, rankings.

    Raises:
        ValueError: If any supplied path fails RS-3 attestation.
    """
    if audit_v1_artifact_paths is not None:
        for path in audit_v1_artifact_paths:
            _fire_rs3_guard_on_path(path)

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
# PHASE2C_11 Step 3 — Simplified DSR-style screen (canonical formula register)
# ---------------------------------------------------------------------------
#
# Frozen dataclasses + compute_simplified_dsr() per
# PHASE2C_11_STEP3_SCHEMA_DRAFT.md (sealed at commit dbcf19d) §1-§4 +
# PHASE2C_11_PLAN §4.3 + §4.5 + §5.4 + §3.6 + §6 + §2.5.
#
# Implementation contract:
#   - Inputs: list[CandidateInput] + n_trials (= EXPECTED_N_RAW for canonical
#     fire); function output is SimplifiedDSRResult.
#   - Dual-gate at function entry: n_trials == EXPECTED_N_RAW AND
#     len(candidates) ∈ {EXPECTED_N_RAW, EXPECTED_N_ELIGIBLE_AT_CANONICAL};
#     ValueError on mismatch.
#   - RS-3 guard per candidate.audit_v1_artifact_path before any formula
#     computation per §2.5 + §4.5 fail-loud lockpoint; per (β-mod)
#     adjudication at TDD-RED hotfix register, no silent skip on missing
#     path.
#   - JSON re-read per candidate (option (i) Charlie-locked); no caching.
#   - Formula: §4.3 Step 1 Bonferroni → Step 2 Gumbel → Step 3 SE/z/p →
#     Step 4 5-region §3.6 AND-gate routing → Step 5 argmax population
#     disposition → §4.4(4) + §1.5 degenerate-state dual-handling →
#     §5.4 sensitivity table at N_eff ∈ {198, 80, 40, 5} → §6.6
#     bonferroni_cross_check.


@dataclass(frozen=True)
class PerCandidateDisposition:
    """Per-candidate canonical-formula-register record.

    See PHASE2C_11_STEP3_SCHEMA_DRAFT.md §2 + PHASE2C_11_PLAN §4.3 Steps 3-4
    + §3.6 conservative AND-gate routing. One instance per eligible candidate.

    Fields propagated unchanged from CandidateInput: hypothesis_hash,
    sharpe_ratio, total_trades, audit_v1_artifact_path. Computed at canonical
    formula register: standard_error, z_score, p_value, bonferroni_pass,
    dsr_style_pass, disposition.

    The disposition Literal is one of three values per §4 cross-section
    consistency: "signal_evidence", "artifact_evidence", "inconclusive".
    The §3.6 AND-gate routes 5 distinct (Bonferroni × DSR-style × p-region)
    combinations to these 3 dispositions per P-L1 5-region correction at
    schema seal.
    """

    hypothesis_hash: str
    sharpe_ratio: float
    total_trades: int
    standard_error: float
    z_score: float
    p_value: float
    bonferroni_pass: bool
    dsr_style_pass: bool
    disposition: DispositionLiteral
    audit_v1_artifact_path: str


@dataclass(frozen=True)
class SensitivityRow:
    """One row of the §5.4 sensitivity table.

    See PHASE2C_11_STEP3_SCHEMA_DRAFT.md §3 + PHASE2C_11_PLAN §5.4. One
    instance per N_eff value in {198, 80, 40, 5}.

    Primary disposition uses N_eff=198 per §3.2 lockpoint; sensitivity
    rows at N_eff ∈ {80, 40, 5} are §5.4 descriptive sensitivity probe;
    sensitivity rows do NOT mutate primary lockpoint.

    Sensitivity narrative interpretation is deferred to Step 4 deliverable
    register; this dataclass emits raw sensitivity values + register labels
    only.
    """

    n_eff: int
    bonferroni_threshold: float
    expected_max_sharpe_null: float
    argmax_p_value: float
    argmax_disposition_descriptive: DispositionLiteral
    register_label: Literal["primary", "sensitivity"]


@dataclass(frozen=True)
class SimplifiedDSRResult:
    """PHASE2C_11 Step 3 canonical output: simplified DSR-style screen result.

    Primary disposition uses N_eff=198 per §3.2 lockpoint; sensitivity rows
    in ``sensitivity_table`` use N_eff ∈ {80, 40, 5} per §5.4 descriptive
    sensitivity probe; primary lockpoint NOT mutated by sensitivity
    computation.

    Reproducibility lockpoint: same SimplifiedDSRInputs + same n_trials →
    byte-identical SimplifiedDSRResult (modulo floating-point formatting
    across platforms; tolerance 1e-9 for floats).

    Consumed by Step 4 deliverable authoring at canonical phrasing register
    per PHASE2C_11_PLAN §6.7.
    """

    per_candidate: tuple[PerCandidateDisposition, ...]
    population_disposition: DispositionLiteral
    population_argmax_hash: str
    n_trials: int
    n_eligible: int
    n_raw: int
    bonferroni_threshold: float
    expected_max_sharpe_null: float
    sharpe_var_used: float
    sensitivity_table: tuple[SensitivityRow, ...]
    bonferroni_cross_check: Mapping[str, bool | float]
    excluded_candidates_summary: tuple[tuple[str, int], ...]
    degenerate_state: Literal["none", "n_eligible_zero", "var_zero"] | None
    rs_guard_call_count: int

    # Field docstring lockpoints (per schema §1 P-T1 + P-T3):
    #
    # rs_guard_call_count:
    #   audit-trail count of check_evaluation_semantics_or_raise()
    #   invocations at function entry. Expected value at canonical fire =
    #   n_eligible; full 198-coverage of audit_v1 paths is achieved jointly
    #   via Step 2 RS-2 (n_raw=198) + Step 3 RS-3 (n_eligible=154); excluded
    #   candidate paths visited at Step 2 only, not re-visited at Step 3
    #   because excluded candidates are not consumed at canonical formula
    #   register. Future-caller forward-pointer: if a future Step 3 caller
    #   bypasses Step 2 loader (e.g., constructs SimplifiedDSRInputs directly
    #   via fixture), the n_eligible RS-3 fire alone does NOT cover excluded
    #   candidates' paths — those callers MUST handle audit_v1 access
    #   patterns separately.
    #
    # per_candidate ordering:
    #   Ordering is stable with respect to SimplifiedDSRInputs.eligible_
    #   candidates; reordering inputs does NOT change population_disposition
    #   (argmax is order-independent) but DOES change per_candidate field
    #   iteration order. Two distinct invariants: (i) population_disposition
    #   reproducible across input shuffling; (ii) per_candidate iteration
    #   tracks input order.


def _gumbel_expected_max(sharpe_var: float, n: int) -> float:
    """§4.3 Step 2 Gumbel approximation for E[max SR | null].

    E[max] = sqrt(Var(SR)) * (
                (1 - γ_e) * Φ⁻¹(1 - 1/N)
              + γ_e       * Φ⁻¹(1 - 1/(N · e))
             )

    where γ_e is the Euler–Mascheroni constant and Φ⁻¹ is the standard
    normal inverse CDF (scipy.stats.norm.ppf). Linear in sqrt(Var); zero
    when Var=0 (degenerate var_zero path handled upstream by caller).
    """
    if n <= 1 or sharpe_var <= 0:
        return 0.0
    sqrt_var = math.sqrt(sharpe_var)
    phi_inv_main = float(norm.ppf(1.0 - 1.0 / n))
    phi_inv_shift = float(norm.ppf(1.0 - 1.0 / (n * math.e)))
    return sqrt_var * (
        (1.0 - EULER_MASCHERONI) * phi_inv_main
        + EULER_MASCHERONI * phi_inv_shift
    )


def _route_disposition(
    bonferroni_pass: bool,
    dsr_style_pass: bool,
    p_value: float,
) -> DispositionLiteral:
    """§3.6 conservative AND-gate routing per §4.3 Step 4 + P-L1 5-region.

    Region 1: bonferroni_pass AND dsr_style_pass → signal_evidence
    Region 2: NOT bonferroni_pass AND NOT dsr_style_pass AND p ≥ 0.5 → artifact_evidence
    Region 3: bonferroni_pass AND NOT dsr_style_pass → inconclusive (Bonferroni-only)
    Region 4: NOT bonferroni_pass AND dsr_style_pass → inconclusive (DSR-only)
    Region 5: NOT bonferroni_pass AND NOT dsr_style_pass AND p < 0.5 → inconclusive (intermediate-p)
    """
    if bonferroni_pass and dsr_style_pass:
        return "signal_evidence"
    if (not bonferroni_pass) and (not dsr_style_pass) and p_value >= 0.5:
        return "artifact_evidence"
    return "inconclusive"


def compute_simplified_dsr(
    candidates: list[CandidateInput],
    n_trials: int,
    *,
    excluded_candidates: list[CandidateExclusion] | None = None,
) -> SimplifiedDSRResult:
    """PHASE2C_11 Step 3 simplified DSR-style screen.

    Per PHASE2C_11_PLAN §4.3 procedure + §4.5 API surface. Computes the
    Bonferroni-style threshold, Gumbel-approximation E[max SR | null], per-
    candidate p-values, §3.6 AND-gate dispositions, population disposition
    via argmax, and §5.4 sensitivity table.

    Dual-gate (§3.2 + Step 2 §5.3 forward-flag) at function entry; raises
    ValueError on either failure (per P-L3 invariant-as-state anti-pattern
    correction). After dual-gate but before RS-3 fire, validates that every
    candidate has a finite ``sharpe_ratio`` (Codex first-fire #4 defensive
    enforcement add — non-finite Sharpe at the Step 3 API entry would
    silently collapse the result via NaN-propagated ``sharpe_var``; raise
    fail-loud with Step 2 enum-aligned ``missing_sharpe`` token instead).
    RS-3 guard fires per candidate.audit_v1_artifact_path BEFORE any
    formula computation (§2.5 + §4.5 fail-loud lockpoint).

    Args:
        candidates: Eligible candidate list (post-§4.4 filter at canonical
            fire). May be the full population (len == EXPECTED_N_RAW) for
            synthetic tests, or the canonical eligible subset (len ==
            EXPECTED_N_ELIGIBLE_AT_CANONICAL) at canonical fire.
        n_trials: N for multiple-testing correction; MUST equal
            EXPECTED_N_RAW per §3.2 lockpoint.
        excluded_candidates: Optional Step 2 ``CandidateExclusion`` list
            from ``load_audit_v1_candidates(...).excluded_candidates`` —
            consumed solely to populate ``SimplifiedDSRResult.excluded_
            candidates_summary`` per schema P-T2 (Codex first-fire #1).
            When ``None`` (synthetic fixture-driven fires that bypass the
            Step 2 loader), the summary is an empty tuple — this is a
            valid degraded audit, NOT a schema violation; "expected counts
            at canonical fire sum to 44" per schema §1 line 51 is a
            canonical-fire invariant, NOT an all-fires invariant.

    Returns:
        SimplifiedDSRResult — canonical Step 3 output.

    Raises:
        ValueError: On dual-gate failure (n_trials != EXPECTED_N_RAW OR
            len(candidates) ∉ {EXPECTED_N_RAW,
            EXPECTED_N_ELIGIBLE_AT_CANONICAL}), on any candidate with
            non-finite ``sharpe_ratio`` (``missing_sharpe (§4.4(3))``
            diagnostic), or on any candidate's RS-3 attestation failure.
    """
    # ----- Dual-gate (§3.2 + Step 2 §5.3 forward-flag) -----
    if n_trials != EXPECTED_N_RAW:
        raise ValueError(
            f"Dual-gate (a) failure: n_trials={n_trials} != "
            f"EXPECTED_N_RAW={EXPECTED_N_RAW} per PHASE2C_11_PLAN §3.2 "
            f"lockpoint."
        )
    n_input = len(candidates)
    allowed_lengths = {EXPECTED_N_RAW, EXPECTED_N_ELIGIBLE_AT_CANONICAL}
    if n_input not in allowed_lengths:
        raise ValueError(
            f"Dual-gate (b) failure: len(candidates)={n_input} not in "
            f"{sorted(allowed_lengths)} (canonical full population "
            f"EXPECTED_N_RAW={EXPECTED_N_RAW} or canonical eligible subset "
            f"EXPECTED_N_ELIGIBLE_AT_CANONICAL="
            f"{EXPECTED_N_ELIGIBLE_AT_CANONICAL}) per PHASE2C_11_PLAN §3.2 "
            f"+ Step 2 §5.3 forward-flag. Caller passed an n_raw mismatch."
        )

    # ----- Patch #4 (Codex first-fire): non-finite sharpe_ratio fail-loud
    # at API boundary; align Step 2 CandidateExclusion.reason='missing_sharpe'
    # enum (§4.4(3)). Fires before RS-3 to avoid I/O on doomed input. ------
    for c in candidates:
        if not math.isfinite(c.sharpe_ratio):
            raise ValueError(
                f"missing_sharpe (§4.4(3)): candidate "
                f"hypothesis_hash={c.hypothesis_hash!r} has non-finite "
                f"sharpe_ratio={c.sharpe_ratio!r}; aligns Step 2 "
                f"CandidateExclusion.reason='missing_sharpe' enum. "
                f"Production callers must pre-filter via "
                f"load_audit_v1_candidates() (which routes non-finite "
                f"Sharpe values to excluded_candidates at Step 2)."
            )

    # ----- Patch #1 (Codex first-fire): build excluded_candidates_summary
    # from optional Step 2 CandidateExclusion list. Sorted by reason key
    # per P-T2 lock; empty tuple when caller didn't provide context (valid
    # degraded audit at synthetic fixture fires). -----
    if excluded_candidates is not None:
        excluded_summary: tuple[tuple[str, int], ...] = tuple(
            sorted(Counter(e.reason for e in excluded_candidates).items())
        )
    else:
        excluded_summary = tuple()

    # ----- RS-3 guard per candidate (fail-loud per §2.5 + §4.5) -----
    rs_guard_call_count = 0
    for c in candidates:
        _fire_rs3_guard_on_path(c.audit_v1_artifact_path)
        rs_guard_call_count += 1

    # ----- Sharpe distribution descriptors -----
    sharpes = [c.sharpe_ratio for c in candidates]
    n_eligible = len(candidates)

    if n_eligible == 0:
        # §1.5 dual-handling: n_eligible_zero degenerate state.
        # NOTE: unreachable under the current §3.2 dual-gate (which forces
        # len(candidates) ∈ {198, 154}); preserved as defensive coverage
        # for future API expansion (e.g., a Step-2-aware entry point that
        # accepts SimplifiedDSRInputs directly per future §4.5 update).
        # Codex first-fire #3 flagged this dead branch; minimal-mutation
        # disposition is to retain the path with explicit unreachability
        # docstring rather than drop the schema-sealed Literal value.
        return _build_degenerate_result(
            degenerate_state="n_eligible_zero",
            n_trials=n_trials,
            n_eligible=0,
            sharpe_var=0.0,
            rs_guard_call_count=rs_guard_call_count,
            excluded_candidates_summary=excluded_summary,
        )

    if n_eligible >= 2:
        sharpe_var = statistics.variance(sharpes)
    else:
        sharpe_var = float("nan")

    if math.isnan(sharpe_var):
        return _build_degenerate_result(
            degenerate_state="n_eligible_zero",
            n_trials=n_trials,
            n_eligible=n_eligible,
            sharpe_var=0.0,
            rs_guard_call_count=rs_guard_call_count,
            excluded_candidates_summary=excluded_summary,
        )

    # ----- §4.3 Step 1: Bonferroni-style threshold -----
    bonferroni_threshold = math.sqrt(2.0 * math.log(n_trials))

    if sharpe_var == 0.0:
        # §1.5 dual-handling: var_zero degenerate state.
        # Bonferroni threshold still well-defined; emit per-candidate
        # records with SE/z/p as defensive defaults (z=0, p=0.5,
        # disposition=inconclusive) per existing helper.
        per_candidate_records = tuple(
            _build_degenerate_per_candidate_record(c, bonferroni_threshold)
            for c in candidates
        )
        argmax_idx = sharpes.index(max(sharpes))
        argmax_candidate = candidates[argmax_idx]
        # Patch #5 (Codex first-fire): emit the §5.4 4-row sensitivity
        # table even in var_zero. Per-row formula compute fires normally
        # (Bonferroni / Gumbel / SE / z / p — Gumbel returns 0.0 at
        # sharpe_var=0 per _gumbel_expected_max guard; SE is var-
        # independent; z and p remain finite); per-row disposition is
        # forced to "inconclusive" because population-level screen is
        # undefined under var_zero per §3.6 + §4.4(4). Schema §1 line 49
        # specifies 4 rows at N_eff ∈ {198, 80, 40, 5} unconditionally;
        # var_zero must not drop the table per Codex first-fire #5
        # adjudication (advisor refinement: per-row compute over Codex's
        # proposed hardcoded argmax_p_value=0.5 placeholder).
        sensitivity_rows: list[SensitivityRow] = []
        for n_eff in (EXPECTED_N_RAW, 80, 40, 5):
            bonf_thr_row = math.sqrt(2.0 * math.log(n_eff))
            e_max_row = _gumbel_expected_max(0.0, n_eff)
            if argmax_candidate.total_trades > 1:
                se_row = math.sqrt(1.0 / (argmax_candidate.total_trades - 1))
                z_row = (argmax_candidate.sharpe_ratio - e_max_row) / se_row
                p_row = float(norm.sf(z_row))
            else:
                p_row = 1.0
            label_row: Literal["primary", "sensitivity"] = (
                "primary" if n_eff == EXPECTED_N_RAW else "sensitivity"
            )
            sensitivity_rows.append(SensitivityRow(
                n_eff=n_eff,
                bonferroni_threshold=bonf_thr_row,
                expected_max_sharpe_null=e_max_row,
                argmax_p_value=p_row,
                argmax_disposition_descriptive="inconclusive",
                register_label=label_row,
            ))
        # Patch #6 (Codex first-fire): MappingProxyType wrap on
        # bonferroni_cross_check — schema field type is Mapping[str, bool|
        # float] (schema §1 line 50); MappingProxyType conforms while
        # preventing post-construction mutation that frozen=True alone does
        # not catch.
        bonferroni_cross_check_var_zero: Mapping[str, bool | float] = (
            MappingProxyType({
                "sr_max": float(max(sharpes)),
                "bonferroni_threshold": bonferroni_threshold,
                "bonferroni_pass": bool(max(sharpes) > bonferroni_threshold),
                "dsr_style_pass": False,
                "criteria_agree": bool(
                    (max(sharpes) > bonferroni_threshold) is False
                ),
            })
        )
        return SimplifiedDSRResult(
            per_candidate=per_candidate_records,
            population_disposition="inconclusive",
            population_argmax_hash=candidates[argmax_idx].hypothesis_hash,
            n_trials=n_trials,
            n_eligible=n_eligible,
            n_raw=n_trials,
            bonferroni_threshold=bonferroni_threshold,
            expected_max_sharpe_null=0.0,
            sharpe_var_used=0.0,
            sensitivity_table=tuple(sensitivity_rows),
            bonferroni_cross_check=bonferroni_cross_check_var_zero,
            excluded_candidates_summary=excluded_summary,
            degenerate_state="var_zero",
            rs_guard_call_count=rs_guard_call_count,
        )

    # ----- §4.3 Step 2: Gumbel approximation E[max SR | null] -----
    expected_max_sharpe_null = _gumbel_expected_max(sharpe_var, n_trials)

    # ----- §4.3 Step 3 + 4: per-candidate SE/z/p + 5-region routing -----
    per_candidate_records = tuple(
        _build_per_candidate_record(
            candidate=c,
            expected_max_sharpe_null=expected_max_sharpe_null,
            bonferroni_threshold=bonferroni_threshold,
        )
        for c in candidates
    )

    # ----- §4.3 Step 5: population disposition via argmax -----
    sharpe_max = max(sharpes)
    argmax_idx = sharpes.index(sharpe_max)  # first-occurrence tie-break
    argmax_record = per_candidate_records[argmax_idx]
    population_disposition: DispositionLiteral = argmax_record.disposition
    population_argmax_hash = candidates[argmax_idx].hypothesis_hash

    # ----- §5.4 sensitivity table (descriptive only) -----
    sensitivity_rows: list[SensitivityRow] = []
    argmax_candidate = candidates[argmax_idx]
    for n_eff in (EXPECTED_N_RAW, 80, 40, 5):
        bonf_thr = math.sqrt(2.0 * math.log(n_eff))
        e_max = _gumbel_expected_max(sharpe_var, n_eff)
        if argmax_candidate.total_trades > 1:
            se = math.sqrt(1.0 / (argmax_candidate.total_trades - 1))
            z = (argmax_candidate.sharpe_ratio - e_max) / se
            p = float(norm.sf(z))
        else:
            p = 1.0
        bonf_pass_row = bool(argmax_candidate.sharpe_ratio > bonf_thr)
        dsr_pass_row = bool(p < 0.05)
        disp_row = _route_disposition(bonf_pass_row, dsr_pass_row, p)
        label: Literal["primary", "sensitivity"] = (
            "primary" if n_eff == EXPECTED_N_RAW else "sensitivity"
        )
        sensitivity_rows.append(SensitivityRow(
            n_eff=n_eff,
            bonferroni_threshold=bonf_thr,
            expected_max_sharpe_null=e_max,
            argmax_p_value=p,
            argmax_disposition_descriptive=disp_row,
            register_label=label,
        ))

    # ----- §6.6 bonferroni_cross_check (Patch #6: MappingProxyType wrap) -----
    bonferroni_pass_overall = bool(sharpe_max > bonferroni_threshold)
    dsr_style_pass_overall = bool(argmax_record.dsr_style_pass)
    bonferroni_cross_check: Mapping[str, bool | float] = MappingProxyType({
        "sr_max": float(sharpe_max),
        "bonferroni_threshold": float(bonferroni_threshold),
        "bonferroni_pass": bonferroni_pass_overall,
        "dsr_style_pass": dsr_style_pass_overall,
        "criteria_agree": bool(
            bonferroni_pass_overall == dsr_style_pass_overall
        ),
    })

    return SimplifiedDSRResult(
        per_candidate=per_candidate_records,
        population_disposition=population_disposition,
        population_argmax_hash=population_argmax_hash,
        n_trials=n_trials,
        n_eligible=n_eligible,
        n_raw=n_trials,
        bonferroni_threshold=bonferroni_threshold,
        expected_max_sharpe_null=expected_max_sharpe_null,
        sharpe_var_used=sharpe_var,
        sensitivity_table=tuple(sensitivity_rows),
        bonferroni_cross_check=bonferroni_cross_check,
        excluded_candidates_summary=excluded_summary,
        degenerate_state="none",
        rs_guard_call_count=rs_guard_call_count,
    )


def _build_per_candidate_record(
    *,
    candidate: CandidateInput,
    expected_max_sharpe_null: float,
    bonferroni_threshold: float,
) -> PerCandidateDisposition:
    """Construct one PerCandidateDisposition at canonical formula register.

    §4.3 Step 3 + Step 4. Defensive on T_c <= 1 (unreachable in production
    given §4.4(1) MIN_TRADES_FOR_PRIMARY filter, but kept finite-output).
    """
    t_c = candidate.total_trades
    if t_c > 1:
        se = math.sqrt(1.0 / (t_c - 1))
        z = (candidate.sharpe_ratio - expected_max_sharpe_null) / se
        p = float(norm.sf(z))
    else:
        se = float("inf")
        z = 0.0
        p = 1.0
    bonf_pass = bool(candidate.sharpe_ratio > bonferroni_threshold)
    dsr_pass = bool(p < 0.05)
    disposition = _route_disposition(bonf_pass, dsr_pass, p)
    return PerCandidateDisposition(
        hypothesis_hash=candidate.hypothesis_hash,
        sharpe_ratio=candidate.sharpe_ratio,
        total_trades=t_c,
        standard_error=se,
        z_score=z,
        p_value=p,
        bonferroni_pass=bonf_pass,
        dsr_style_pass=dsr_pass,
        disposition=disposition,
        audit_v1_artifact_path=candidate.audit_v1_artifact_path,
    )


def _build_degenerate_per_candidate_record(
    candidate: CandidateInput,
    bonferroni_threshold: float,
) -> PerCandidateDisposition:
    """Construct one PerCandidateDisposition under var_zero degenerate state.

    SE is well-defined for T_c >= 2 (1/(T_c - 1)); z and p are undefined
    (E[max|null] = 0 under var_zero); set z=0, p=0.5 (consistent with
    z=0 under symmetric null), bonferroni_pass = SR > threshold,
    dsr_style_pass = False, disposition = inconclusive.
    """
    t_c = candidate.total_trades
    if t_c > 1:
        se = math.sqrt(1.0 / (t_c - 1))
    else:
        se = float("inf")
    bonf_pass = bool(candidate.sharpe_ratio > bonferroni_threshold)
    return PerCandidateDisposition(
        hypothesis_hash=candidate.hypothesis_hash,
        sharpe_ratio=candidate.sharpe_ratio,
        total_trades=t_c,
        standard_error=se,
        z_score=0.0,
        p_value=0.5,
        bonferroni_pass=bonf_pass,
        dsr_style_pass=False,
        disposition="inconclusive",
        audit_v1_artifact_path=candidate.audit_v1_artifact_path,
    )


def _build_degenerate_result(
    *,
    degenerate_state: Literal["n_eligible_zero", "var_zero"],
    n_trials: int,
    n_eligible: int,
    sharpe_var: float,
    rs_guard_call_count: int,
    excluded_candidates_summary: tuple[tuple[str, int], ...] = (),
) -> SimplifiedDSRResult:
    """Construct a SimplifiedDSRResult for n_eligible_zero (no candidates).

    Patch #1 (Codex first-fire): accepts ``excluded_candidates_summary``
    kw-only so degenerate-path callers can thread the Step 2 exclusion
    summary through (preserving audit-trail even on degenerate fires).
    Patch #6: ``bonferroni_cross_check`` wrapped in MappingProxyType to
    conform schema field type ``Mapping[str, bool | float]`` and prevent
    post-construction mutation.
    """
    return SimplifiedDSRResult(
        per_candidate=tuple(),
        population_disposition="inconclusive",
        population_argmax_hash="",
        n_trials=n_trials,
        n_eligible=n_eligible,
        n_raw=n_trials,
        bonferroni_threshold=0.0,
        expected_max_sharpe_null=0.0,
        sharpe_var_used=sharpe_var,
        sensitivity_table=tuple(),
        bonferroni_cross_check=MappingProxyType({
            "sr_max": 0.0,
            "bonferroni_threshold": 0.0,
            "bonferroni_pass": False,
            "dsr_style_pass": False,
            "criteria_agree": True,
        }),
        excluded_candidates_summary=excluded_candidates_summary,
        degenerate_state=degenerate_state,
        rs_guard_call_count=rs_guard_call_count,
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
