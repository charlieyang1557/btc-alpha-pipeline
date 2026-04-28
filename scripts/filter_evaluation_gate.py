"""Phase 2C evaluation-gate trade-count filter — PHASE2C_7.1 §5 / Step 3.

Post-evaluation analytical filter applied to a primary evaluation_gate
run's per-candidate artifacts. Produces a derived analytical artifact
set under a sibling namespace (e.g. audit_2024_v1 ->
audit_2024_v1_filtered) by including only candidates whose 2024 holdout
trade count satisfies ``holdout_metrics.total_trades >= 20``.

Per §5.1 / §5.3 design contract:

- **No producer re-run.** The filter does not invoke run_regime_holdout
  or any engine code. It reads primary per-candidate JSONs from disk
  and selects the subset to copy into the filtered namespace.
- **Per-candidate JSONs are byte-identical** to the primary artifacts.
  Filtering is selection, not modification.
- **Aggregate is recomputed** over the included subset (counts,
  primary-vs-audit-only partition, by-theme breakdown).
- **Lineage attestation inherits by reference from primary** — the
  filtered aggregate's lineage fields are copied verbatim from the
  primary aggregate. There is no new engine_commit, no new
  current_git_sha, because nothing was newly produced.
- **Threshold is pinned at module-level constant** (§5.3 Rule 1). The
  CLI deliberately does not expose --threshold; a future filter pass
  with a different threshold requires a code change + new commit + new
  pre-specification, not a runtime parameter sweep.

CLI surface:
    --primary-run-id <id>     Primary run name under <output-root>/
                              (e.g. "audit_2024_v1")
    --output-run-id <id>      Filtered run name. Default:
                              "<primary-run-id>_filtered".
    --output-root <path>      Default: data/phase2c_evaluation_gate/
    --force                   Allow overwriting non-empty output dir.

The filter does not interact with the experiments registry, the lineage
guard, or any external service. It is pure local file I/O.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "phase2c_evaluation_gate"

# §5.3 Rule 1: threshold is pinned in code, not a CLI parameter. Updating
# the threshold requires a code change + new commit + new
# pre-specification (Rule 2 anti-tuning). DO NOT expose this as a CLI
# flag or accept it as a function parameter without a new locked
# decision.
MIN_TOTAL_TRADES = 20


# ---------------------------------------------------------------------------
# Filter predicate
# ---------------------------------------------------------------------------


def _passes_filter(per_candidate_summary: dict[str, Any]) -> bool:
    """Apply the trade-count filter to a per-candidate summary dict.

    Returns True iff ``holdout_metrics.total_trades >= MIN_TOTAL_TRADES``.
    holdout_error candidates (whose holdout_metrics is None) return
    False unconditionally — they were not measured against the regime,
    so they cannot satisfy a measurement-derived predicate.
    """
    metrics = per_candidate_summary.get("holdout_metrics")
    if metrics is None:
        return False
    trades = metrics.get("total_trades")
    if trades is None:
        return False
    return int(trades) >= MIN_TOTAL_TRADES


# ---------------------------------------------------------------------------
# Aggregate recomputation
# ---------------------------------------------------------------------------


def _recompute_aggregate(
    primary_aggregate: dict[str, Any],
    included: list[dict[str, Any]],
    primary_total: int,
    primary_run_id: str,
) -> dict[str, Any]:
    """Recompute aggregate counts/partition/theme over the filtered subset.

    Lineage fields (evaluation_semantics, engine_commit,
    engine_corrected_lineage, lineage_check, current_git_sha,
    artifact_schema_version, regime_key, regime_label) are inherited
    from the primary aggregate verbatim per §5.1 (no new attestation).
    Provenance fields (derived_from_run_id, filter_predicate,
    filter_threshold, filter_primary_total, filter_excluded_count) are
    added so a future maintainer can identify the filter that produced
    the artifact.
    """
    # Recompute lifecycle counts.
    counts = {
        "total": len(included),
        "holdout_passed": sum(
            1 for s in included if s["lifecycle_state"] == "holdout_passed"
        ),
        "holdout_failed": sum(
            1 for s in included if s["lifecycle_state"] == "holdout_failed"
        ),
        "holdout_error": sum(
            1 for s in included if s["lifecycle_state"] == "holdout_error"
        ),
    }

    # Reuse the primary's PRIMARY_THRESHOLD = 0.5 partition split.
    primary_part = [s for s in included if s["wf_test_period_sharpe"] > 0.5]
    audit_part = [s for s in included if s["wf_test_period_sharpe"] <= 0.5]

    # Recompute by_theme.
    by_theme: dict[str, dict[str, int]] = {}
    for s in included:
        bucket = by_theme.setdefault(
            s["theme"], {"total": 0, "holdout_passed": 0}
        )
        bucket["total"] += 1
        if s["lifecycle_state"] == "holdout_passed":
            bucket["holdout_passed"] += 1

    aggregate: dict[str, Any] = {
        "run_id": primary_aggregate["run_id"] + "_filtered",
        "source_batch_id": primary_aggregate.get("source_batch_id"),
        "universe": primary_aggregate.get("universe"),
        "explicit_candidate_hashes": (
            primary_aggregate.get("explicit_candidate_hashes")
        ),
        "run_started_utc": primary_aggregate.get("run_started_utc"),
        "run_finished_utc": primary_aggregate.get("run_finished_utc"),
        "counts": counts,
        "primary_universe_holdout_passed": sum(
            1 for s in primary_part
            if s["lifecycle_state"] == "holdout_passed"
        ),
        "primary_universe_total": len(primary_part),
        "audit_only_holdout_passed": sum(
            1 for s in audit_part
            if s["lifecycle_state"] == "holdout_passed"
        ),
        "audit_only_total": len(audit_part),
        "by_theme": by_theme,
    }

    # Provenance — minimal but sufficient to reconstruct what filter ran.
    aggregate["derived_from_run_id"] = primary_run_id
    aggregate["filter_predicate"] = "holdout_metrics.total_trades >= N"
    aggregate["filter_threshold"] = MIN_TOTAL_TRADES
    aggregate["filter_primary_total"] = primary_total
    aggregate["filter_excluded_count"] = primary_total - len(included)

    # Lineage inheritance — copy verbatim, not re-attest.
    for field in (
        "evaluation_semantics", "engine_commit", "engine_corrected_lineage",
        "lineage_check", "current_git_sha", "artifact_schema_version",
        "regime_key", "regime_label",
    ):
        if field in primary_aggregate:
            aggregate[field] = primary_aggregate[field]

    return aggregate


# ---------------------------------------------------------------------------
# CSV row subsetting
# ---------------------------------------------------------------------------


def _write_filtered_csv(
    primary_csv_path: Path,
    output_csv_path: Path,
    included_hashes: set[str],
) -> None:
    """Row-subset the primary CSV to the included hashes (preserves column order)."""
    with open(primary_csv_path) as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames or []
        rows = [r for r in reader if r["hypothesis_hash"] in included_hashes]
    with open(output_csv_path, "w", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


# ---------------------------------------------------------------------------
# Top-level filter
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FilterResult:
    """Return value of apply_trade_count_filter for downstream verification."""
    primary_total: int
    included_count: int
    excluded_count: int
    output_dir: Path


def apply_trade_count_filter(
    *,
    primary_dir: Path,
    output_dir: Path,
    force: bool = False,
) -> FilterResult:
    """Filter a primary evaluation_gate run by ``total_trades >= 20``.

    Reads every per-candidate holdout_summary.json under ``primary_dir``,
    applies :func:`_passes_filter`, copies passing JSONs byte-for-byte
    into ``output_dir``, recomputes the aggregate JSON over the included
    subset, and writes a row-subset of the primary CSV.

    Lineage attestation is inherited verbatim from the primary
    aggregate; no new engine commit or git SHA is computed.

    Args:
        primary_dir: Path containing the primary run (per-candidate
            subdirs + holdout_summary.json + holdout_results.csv).
        output_dir: Destination for the filtered subset. Refuses to
            overwrite a non-empty existing dir unless ``force=True``.
        force: If True, allows overwriting a non-empty existing
            ``output_dir`` (the dir is removed and recreated).

    Returns:
        FilterResult with primary_total, included_count, excluded_count.

    Raises:
        FileExistsError: ``output_dir`` exists, is non-empty, and
            ``force=False``.
        FileNotFoundError: Primary aggregate JSON or CSV missing.
    """
    primary_dir = Path(primary_dir)
    output_dir = Path(output_dir)

    # Overwrite protection.
    if output_dir.exists():
        try:
            non_empty = any(output_dir.iterdir())
        except OSError:
            non_empty = True
        if non_empty:
            if not force:
                raise FileExistsError(
                    f"Output dir {output_dir} exists and is non-empty. "
                    f"Pass force=True or use a different output path."
                )
            shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load primary aggregate (needed for lineage inheritance + run_id).
    primary_agg_path = primary_dir / "holdout_summary.json"
    if not primary_agg_path.exists():
        raise FileNotFoundError(
            f"Primary aggregate not found at {primary_agg_path}"
        )
    primary_aggregate = json.loads(primary_agg_path.read_text())
    primary_run_id = primary_aggregate["run_id"]

    # Walk per-candidate subdirs.
    cand_dirs = sorted(
        p for p in primary_dir.iterdir()
        if p.is_dir() and (p / "holdout_summary.json").exists()
    )
    primary_total = len(cand_dirs)

    included: list[dict[str, Any]] = []
    included_hashes: set[str] = set()
    for cand_dir in cand_dirs:
        cand_path = cand_dir / "holdout_summary.json"
        summary = json.loads(cand_path.read_text())
        if not _passes_filter(summary):
            continue
        # Byte-identical copy preserves §5.1 inherits-by-reference.
        out_cand_dir = output_dir / cand_dir.name
        out_cand_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(cand_path, out_cand_dir / "holdout_summary.json")
        included.append(summary)
        included_hashes.add(summary["hypothesis_hash"])

    # Aggregate recomputation.
    filtered_aggregate = _recompute_aggregate(
        primary_aggregate=primary_aggregate,
        included=included,
        primary_total=primary_total,
        primary_run_id=primary_run_id,
    )
    (output_dir / "holdout_summary.json").write_text(
        json.dumps(filtered_aggregate, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    # CSV row subset.
    primary_csv_path = primary_dir / "holdout_results.csv"
    if primary_csv_path.exists():
        _write_filtered_csv(
            primary_csv_path=primary_csv_path,
            output_csv_path=output_dir / "holdout_results.csv",
            included_hashes=included_hashes,
        )

    return FilterResult(
        primary_total=primary_total,
        included_count=len(included),
        excluded_count=primary_total - len(included),
        output_dir=output_dir,
    )


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "PHASE2C_7.1 §5 filter pass — derive trade-count-filtered "
            "analytical artifact set from a primary evaluation_gate run. "
            "Threshold is pinned at MIN_TOTAL_TRADES = "
            f"{MIN_TOTAL_TRADES} per §5.3 Rule 1; not exposed as CLI flag."
        ),
    )
    parser.add_argument(
        "--primary-run-id",
        type=str,
        required=True,
        help=(
            "Primary run name under <output-root>/ (e.g. audit_2024_v1)."
        ),
    )
    parser.add_argument(
        "--output-run-id",
        type=str,
        default=None,
        help=(
            "Filtered run name. Default: <primary-run-id>_filtered."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=str(DEFAULT_OUTPUT_ROOT),
        help=f"Output root. Default: {DEFAULT_OUTPUT_ROOT}.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Allow overwriting a non-empty <output-root>/<output-run-id>/."
        ),
    )
    return parser


def main() -> int:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        level=logging.INFO,
    )
    args = _build_argparser().parse_args()
    output_run_id = args.output_run_id or f"{args.primary_run_id}_filtered"
    primary_dir = Path(args.output_root).resolve() / args.primary_run_id
    output_dir = Path(args.output_root).resolve() / output_run_id
    print(f"[filter] primary: {primary_dir}")
    print(f"[filter] output:  {output_dir}")
    print(f"[filter] threshold (pinned): total_trades >= {MIN_TOTAL_TRADES}")
    try:
        result = apply_trade_count_filter(
            primary_dir=primary_dir,
            output_dir=output_dir,
            force=args.force,
        )
    except FileExistsError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(
        f"[filter] primary_total={result.primary_total} "
        f"included={result.included_count} "
        f"excluded={result.excluded_count}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
