"""PHASE2C_7.1 §8 Step 4 — candidate-aligned 2022-vs-2024 comparison.

Reads three artifact sets:
    - PHASE2C_6 audit_v1                 (2022 evaluation, 198 candidates)
    - PHASE2C_7.1 audit_2024_v1          (2024 evaluation, 198 candidates)
    - PHASE2C_7.1 audit_2024_v1_filtered (2024 evaluation, total_trades>=20
                                          subset, 144 candidates)

Produces a candidate-aligned diff matrix:
    - comparison.csv    one row per candidate with both regimes' outcomes
    - comparison.json   stratified cross-tab (filter_survivor + filter_excluded)
                        x partition (primary / audit_only) x 2x2 (2022 x 2024)

Hash axis. Per §8 Step 4 + Step 2 review: candidates match by per-candidate
JSON's ``hypothesis_hash`` field, NOT registry-row ``hypothesis_hash``.
The producer-side and engine-side hashes diverge under PHASE2C_7.1 because
the engine recomputes via ``compute_dsl_hash`` post-compile.

Universe symmetry. Per Step 4 review M2: ``audit_v1`` and
``audit_2024_v1`` MUST contain identical 198-candidate sets by
construction (§2 spec). Apply asserts the symmetric difference is empty
before computing the cross-tab; mismatch raises with offending hashes.
``audit_2024_v1_filtered`` ⊆ ``audit_2024_v1`` by construction (the
filter is post-evaluation selection, not regeneration).

Schema version. ``comparison_schema_version="comparison_schema_v1"`` is
shape-identity — describes the artifact shape, not the arc that produced
it. Future arcs producing the same shape reuse v1; arcs that change
the shape (e.g., adding a third regime axis) bump to v2.

Lineage. This is a DERIVED ANALYSIS artifact, not an evaluation_gate
producer artifact. It does NOT carry ``evaluation_semantics`` /
``engine_commit`` (the comparison itself does not attest a regime
evaluation). It records ``lineage_inputs`` paths to the source
artifact dirs so future audits can trace which data went in.
``check_evaluation_semantics_or_raise`` is NOT applicable to comparison
artifacts (different attestation domain).

Interpretation. Step 4 produces the matrix; Step 5 closeout reads the
matrix and adjudicates "is selection power preserved across regimes?"
This script writes data, not findings.

CLI surface:
    --audit-v1-dir <path>                 PHASE2C_6 audit_v1 dir
    --audit-2024-v1-dir <path>            PHASE2C_7.1 audit_2024_v1 dir
    --audit-2024-v1-filtered-dir <path>   audit_2024_v1_filtered dir
    --output-dir <path>                   Comparison output dir
    --force                               Overwrite non-empty output
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

COMPARISON_SCHEMA_VERSION = "comparison_schema_v1"
PRIMARY_THRESHOLD = 0.5  # mirrors run_phase2c_evaluation_gate / filter_evaluation_gate

CSV_FIELDS: tuple[str, ...] = (
    "hypothesis_hash",
    "theme",
    "partition",
    "wf_test_period_sharpe",
    "holdout_2022_passed",
    "holdout_2024_passed",
    "holdout_2024_filter_state",
    "holdout_2022_total_trades",
    "holdout_2024_total_trades",
    "holdout_2022_sharpe",
    "holdout_2024_sharpe",
)


# ---------------------------------------------------------------------------
# Artifact loader
# ---------------------------------------------------------------------------


def _load_run_artifacts(run_dir: Path) -> dict[str, dict[str, Any]]:
    """Read every per-candidate holdout_summary.json under ``run_dir``.

    Returns a dict keyed by per-candidate JSON's ``hypothesis_hash``
    field (NOT registry-row hash). The value is the full per-candidate
    summary dict.
    """
    out: dict[str, dict[str, Any]] = {}
    for cand_dir in sorted(run_dir.iterdir()):
        if not cand_dir.is_dir():
            continue
        path = cand_dir / "holdout_summary.json"
        if not path.exists():
            continue
        summary = json.loads(path.read_text())
        h = summary["hypothesis_hash"]
        if h in out:
            raise ValueError(
                f"Duplicate hypothesis_hash {h!r} found under {run_dir}"
            )
        out[h] = summary
    return out


# ---------------------------------------------------------------------------
# Per-candidate row + filter_state derivation
# ---------------------------------------------------------------------------


def _derive_filter_state(
    in_filtered: bool,
    holdout_2024_passed: bool | None,
) -> str:
    """Tri-valued enum: survivor_passed | survivor_failed | excluded.

    Per Step 4 review M1 + Q3(a) refinement: explicit enum, not nullable
    bool. The three states are mutually exclusive and collectively
    exhaustive across the 198-candidate population.
    """
    if not in_filtered:
        return "excluded"
    if holdout_2024_passed is True:
        return "survivor_passed"
    return "survivor_failed"


def _per_candidate_row(
    summary_22: dict[str, Any],
    summary_24: dict[str, Any],
    in_filtered: bool,
) -> dict[str, Any]:
    """Build one candidate-aligned row joining 2022 + 2024 outcomes."""
    h = summary_22["hypothesis_hash"]
    wf = float(summary_22.get("wf_test_period_sharpe", 0.0))
    partition = "primary" if wf > PRIMARY_THRESHOLD else "audit_only"
    m22 = summary_22.get("holdout_metrics") or {}
    m24 = summary_24.get("holdout_metrics") or {}
    return {
        "hypothesis_hash": h,
        "theme": summary_22.get("theme", ""),
        "partition": partition,
        "wf_test_period_sharpe": wf,
        "holdout_2022_passed": summary_22.get("holdout_passed"),
        "holdout_2024_passed": summary_24.get("holdout_passed"),
        "holdout_2024_filter_state": _derive_filter_state(
            in_filtered, summary_24.get("holdout_passed"),
        ),
        "holdout_2022_total_trades": m22.get("total_trades"),
        "holdout_2024_total_trades": m24.get("total_trades"),
        "holdout_2022_sharpe": m22.get("sharpe_ratio"),
        "holdout_2024_sharpe": m24.get("sharpe_ratio"),
    }


# ---------------------------------------------------------------------------
# Cross-tab construction
# ---------------------------------------------------------------------------


def _empty_2x2_cells() -> dict[str, int]:
    return {
        "passed_2022_passed_2024": 0,
        "passed_2022_failed_2024": 0,
        "failed_2022_passed_2024": 0,
        "failed_2022_failed_2024": 0,
    }


def _empty_partition_cross_tab() -> dict[str, dict[str, int]]:
    return {
        "primary": _empty_2x2_cells(),
        "audit_only": _empty_2x2_cells(),
    }


def _cell_label(passed_22: bool | None, passed_24: bool | None) -> str | None:
    """Map (2022, 2024) outcome pair to a cross-tab cell name.

    holdout_error candidates (passed=None) cannot be classified; return
    None so the caller can choose to skip them. holdout_error rows
    nonetheless appear in the per-candidate CSV (with null pass fields)
    so the closeout has visibility into them, but they don't contribute
    to cross-tab cell counts.
    """
    if passed_22 is None or passed_24 is None:
        return None
    if passed_22 and passed_24:
        return "passed_2022_passed_2024"
    if passed_22 and not passed_24:
        return "passed_2022_failed_2024"
    if not passed_22 and passed_24:
        return "failed_2022_passed_2024"
    return "failed_2022_failed_2024"


def _build_cross_tabs(
    rows: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    """Stratify rows by filter_state and build two partition-x-2x2 cross-tabs."""
    survivor = _empty_partition_cross_tab()
    excluded = _empty_partition_cross_tab()
    for r in rows:
        cell = _cell_label(r["holdout_2022_passed"], r["holdout_2024_passed"])
        if cell is None:
            continue
        target = (
            survivor if r["holdout_2024_filter_state"] != "excluded"
            else excluded
        )
        target[r["partition"]][cell] += 1
    return survivor, excluded


# ---------------------------------------------------------------------------
# Top-level comparison
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ComparisonResult:
    n_candidates: int
    n_filter_survivor: int
    n_filter_excluded: int
    output_dir: Path


def apply_2022_vs_2024_comparison(
    *,
    audit_v1_dir: Path,
    audit_2024_v1_dir: Path,
    audit_2024_v1_filtered_dir: Path,
    output_dir: Path,
    force: bool = False,
) -> ComparisonResult:
    """Build the 2022-vs-2024 candidate-aligned diff matrix.

    Args:
        audit_v1_dir: PHASE2C_6 audit_v1 artifact dir.
        audit_2024_v1_dir: PHASE2C_7.1 audit_2024_v1 artifact dir.
        audit_2024_v1_filtered_dir: audit_2024_v1_filtered artifact dir.
        output_dir: Destination for comparison.csv + comparison.json.
        force: Allow overwriting non-empty output_dir.

    Raises:
        ValueError: If audit_v1 and audit_2024_v1 candidate universes
            do not exactly match (M2 universe symmetry assertion), or
            if filtered dir contains a hash absent from audit_2024_v1.
        FileExistsError: output_dir non-empty without force.
    """
    audit_v1_dir = Path(audit_v1_dir)
    audit_2024_v1_dir = Path(audit_2024_v1_dir)
    audit_2024_v1_filtered_dir = Path(audit_2024_v1_filtered_dir)
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

    # Load three artifact sets.
    art_22 = _load_run_artifacts(audit_v1_dir)
    art_24 = _load_run_artifacts(audit_2024_v1_dir)
    art_24f = _load_run_artifacts(audit_2024_v1_filtered_dir)

    # M2: universe symmetry assertion.
    set_22 = set(art_22)
    set_24 = set(art_24)
    diff = set_22 ^ set_24
    if diff:
        raise ValueError(
            f"audit_v1 and audit_2024_v1 candidate universes do not "
            f"match (symmetric difference contains {len(diff)} hashes). "
            f"Sample mismatch hashes: {sorted(diff)[:5]}. Refusing to "
            f"compute cross-tab over partial intersection."
        )

    # Filtered subset must be a subset of audit_2024_v1.
    filtered_extras = set(art_24f) - set_24
    if filtered_extras:
        raise ValueError(
            f"audit_2024_v1_filtered contains {len(filtered_extras)} "
            f"hashes absent from audit_2024_v1. Sample: "
            f"{sorted(filtered_extras)[:5]}. Filter is post-evaluation "
            f"selection; filtered set must be a subset of audit_2024_v1."
        )

    # Build per-candidate rows.
    filtered_hashes = set(art_24f)
    rows: list[dict[str, Any]] = []
    for h in sorted(set_22):
        rows.append(_per_candidate_row(
            summary_22=art_22[h],
            summary_24=art_24[h],
            in_filtered=h in filtered_hashes,
        ))

    # CSV write.
    csv_path = output_dir / "comparison.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: ("" if r[k] is None else r[k]) for k in CSV_FIELDS})

    # Cross-tab JSON.
    survivor, excluded = _build_cross_tabs(rows)
    n_survivor = sum(1 for r in rows if r["holdout_2024_filter_state"] != "excluded")
    n_excluded = sum(1 for r in rows if r["holdout_2024_filter_state"] == "excluded")

    cmp_obj: dict[str, Any] = {
        "comparison_schema_version": COMPARISON_SCHEMA_VERSION,
        "produced_at_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "lineage_inputs": {
            "audit_v1_path": str(audit_v1_dir),
            "audit_2024_v1_path": str(audit_2024_v1_dir),
            "audit_2024_v1_filtered_path": str(audit_2024_v1_filtered_dir),
        },
        "totals": {
            "n_candidates": len(rows),
            "n_filter_survivor": n_survivor,
            "n_filter_excluded": n_excluded,
        },
        "filter_survivor_cross_tab": survivor,
        "filter_excluded_cross_tab": excluded,
    }
    (output_dir / "comparison.json").write_text(
        json.dumps(cmp_obj, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return ComparisonResult(
        n_candidates=len(rows),
        n_filter_survivor=n_survivor,
        n_filter_excluded=n_excluded,
        output_dir=output_dir,
    )


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "PHASE2C_7.1 §8 Step 4 — candidate-aligned 2022-vs-2024 "
            "comparison cross-tab. Produces matrix only; interpretation "
            "lives in Step 5 closeout."
        ),
    )
    parser.add_argument(
        "--audit-v1-dir", type=str, required=True,
        help="PHASE2C_6 audit_v1 artifact dir (2022 evaluation).",
    )
    parser.add_argument(
        "--audit-2024-v1-dir", type=str, required=True,
        help="PHASE2C_7.1 audit_2024_v1 artifact dir (2024 evaluation).",
    )
    parser.add_argument(
        "--audit-2024-v1-filtered-dir", type=str, required=True,
        help=(
            "audit_2024_v1_filtered artifact dir (2024 evaluation, "
            "total_trades>=20 subset)."
        ),
    )
    parser.add_argument(
        "--output-dir", type=str, required=True,
        help="Comparison output dir (comparison.csv + comparison.json).",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite non-empty output dir.",
    )
    return parser


def main() -> int:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        level=logging.INFO,
    )
    args = _build_argparser().parse_args()
    print(f"[compare] audit_v1: {args.audit_v1_dir}")
    print(f"[compare] audit_2024_v1: {args.audit_2024_v1_dir}")
    print(f"[compare] audit_2024_v1_filtered: {args.audit_2024_v1_filtered_dir}")
    print(f"[compare] output: {args.output_dir}")
    try:
        result = apply_2022_vs_2024_comparison(
            audit_v1_dir=Path(args.audit_v1_dir),
            audit_2024_v1_dir=Path(args.audit_2024_v1_dir),
            audit_2024_v1_filtered_dir=Path(args.audit_2024_v1_filtered_dir),
            output_dir=Path(args.output_dir),
            force=args.force,
        )
    except (ValueError, FileExistsError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(
        f"[compare] n_candidates={result.n_candidates} "
        f"survivor={result.n_filter_survivor} "
        f"excluded={result.n_filter_excluded}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
