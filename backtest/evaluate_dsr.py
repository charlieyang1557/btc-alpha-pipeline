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
import logging
import math
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


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
