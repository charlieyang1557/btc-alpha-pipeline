"""PHASE2C_8.1 §8 Step 4 — multi-regime n-way candidate-aligned comparison.

Reads N regime artifact sets (unfiltered + filtered tier per regime) and
produces a candidate-aligned diff matrix with cohort categorization.
Generalizes PHASE2C_7.1's compare_2022_vs_2024.py (which was 2-way) to
arbitrary n>=2; PHASE2C_8.1 deploys at n=4 (eval_2020_v1 + eval_2021_v1
novel + bear_2022 + validation_2024 inherited).

Cohort definitions (per spec §6.6):
- Cohort (a): cross-regime survivors. Unfiltered tier = candidates passing
  AND-gate in all N regimes; filtered tier = candidates passing AND-gate
  in all N regimes AND surviving trade-count filter in all N regimes.
- Cohort (c): failures. Candidates passing AND-gate in 0 regimes.
- Pass-count distribution: histogram of {0, 1, ..., N} pass counts (cohort
  (b) per-regime cross-tab).

In-sample caveat stratification (per spec §7.4): per-regime metadata
identifies fully-out-of-sample regimes (caveat=false) vs train-overlap
regimes (caveat=true). Cohort analysis stratifies pass counts by these
two evidentiary categories.

Mixed-schema dispatch (per spec §6.5): regime artifacts may carry absent
schema (legacy PHASE2C_6), phase2c_7_1, or phase2c_8_1 discriminators.
The comparison script reads per-candidate JSONs without parsing the
schema discriminator (operates on metric values; agnostic to schema
version per spec §6.5 reconciliation rule).

Lineage. This is a DERIVED ANALYSIS artifact, not an evaluation_gate
producer artifact. It does NOT carry evaluation_semantics / engine_commit.
Records lineage_inputs paths to source artifact dirs for audit
traceability. comparison_schema_version="comparison_schema_v2" is shape-
identity for the n-way schema (v1 was 2-way only).

CLI surface:
    --regime-input <key>=<dir>      regime_key=unfiltered_artifact_dir
                                    (repeated; one per regime)
    --filtered-input <key>=<dir>    regime_key=filtered_artifact_dir
                                    (repeated; one per regime; symmetric
                                    n-way assumes one per regime)
    --output-dir <path>             Comparison output dir
    --force                         Overwrite non-empty output
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backtest.wf_lineage import (  # noqa: E402
    REGIME_KEY_LABEL_MAPPING,
    REGIME_KEY_TO_SCHEMA_VERSION_MAPPING,
    ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1,
)

logger = logging.getLogger(__name__)

COMPARISON_SCHEMA_VERSION = "comparison_schema_v2"
PRIMARY_THRESHOLD = 0.5  # mirrors run_phase2c_evaluation_gate / filter_evaluation_gate


# ---------------------------------------------------------------------------
# Per-regime metadata resolution
# ---------------------------------------------------------------------------


def _resolve_regime_metadata(regime_key: str) -> dict[str, Any]:
    """Derive label / schema_version / in_sample_caveat_applies for a regime_key.

    Pulls from REGIME_KEY_LABEL_MAPPING (label) and
    REGIME_KEY_TO_SCHEMA_VERSION_MAPPING (schema). Caveat is derived
    from schema: phase2c_8_1 → caveat=True (PHASE2C_8.1 novel regimes
    overlap train); phase2c_7_1 → caveat=False (PHASE2C_7.1 inherited
    fully-out-of-sample).
    """
    label = REGIME_KEY_LABEL_MAPPING.get(regime_key)
    schema_version = REGIME_KEY_TO_SCHEMA_VERSION_MAPPING.get(regime_key)
    if label is None or schema_version is None:
        raise ValueError(
            f"regime_key={regime_key!r} is not in REGIME_KEY_LABEL_MAPPING / "
            f"REGIME_KEY_TO_SCHEMA_VERSION_MAPPING. Known: "
            f"{sorted(REGIME_KEY_LABEL_MAPPING)}."
        )
    in_sample_caveat = schema_version == ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1
    return {
        "regime_key": regime_key,
        "label": label,
        "schema_version": schema_version,
        "in_sample_caveat_applies": in_sample_caveat,
    }


# ---------------------------------------------------------------------------
# Regime input descriptor
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RegimeInput:
    """Per-regime input paths + metadata."""

    regime_key: str
    unfiltered_dir: Path
    filtered_dir: Path

    @property
    def metadata(self) -> dict[str, Any]:
        return _resolve_regime_metadata(self.regime_key)

    @property
    def label(self) -> str:
        return self.metadata["label"]


# ---------------------------------------------------------------------------
# Artifact loader (inherited pattern from compare_2022_vs_2024)
# ---------------------------------------------------------------------------


def _expected_count_from_results_csv(run_dir: Path) -> int | None:
    """Derive the producer's canonical universe size for a regime+tier dir.

    Reads `<run_dir>/holdout_results.csv` and returns the row count
    excluding the header. This is the authoritative cardinality for
    cross-checking the per-candidate JSON dir count.

    Returns None if the CSV is absent — caller may then fall back to
    permissive loading (no cardinality assertion). PHASE2C_6/7.1/8.1
    producer artifact dirs always emit holdout_results.csv; absence
    typically signals an unconventional/synthetic input.
    """
    csv_path = run_dir / "holdout_results.csv"
    if not csv_path.exists():
        return None
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            next(reader)  # header
        except StopIteration:
            return 0
        return sum(1 for _ in reader)


def _load_run_artifacts(
    run_dir: Path,
    *,
    expected_count: int | None = None,
) -> dict[str, dict[str, Any]]:
    """Read every per-candidate holdout_summary.json under run_dir.

    Returns dict keyed by hypothesis_hash. Mixed-schema input handled
    transparently — script does not parse schema_discriminator.

    Convention skip: subdirectories whose name starts with underscore
    (e.g., `_smoke/`, `_filtered/`) are non-candidate convention dirs
    that carry aggregate or derived artifacts; they are skipped.

    For all non-convention candidate dirs, the loader is strict:
        - missing holdout_summary.json → raise FileNotFoundError
        - holdout_summary.json without hypothesis_hash → raise ValueError
        - duplicate hypothesis_hash across dirs → raise ValueError

    If expected_count is provided, the loaded universe size must match
    or ValueError is raised. Pass expected_count to assert per-regime
    cardinality against an authoritative source (e.g., row count of
    holdout_results.csv).
    """
    out: dict[str, dict[str, Any]] = {}
    for cand_dir in sorted(run_dir.iterdir()):
        if not cand_dir.is_dir():
            continue
        if cand_dir.name.startswith("_"):
            continue  # Skip _smoke/, _filtered/, and similar convention dirs.
        path = cand_dir / "holdout_summary.json"
        if not path.exists():
            raise FileNotFoundError(
                f"Expected holdout_summary.json under candidate dir "
                f"{cand_dir} (relative to {run_dir}). Non-convention "
                f"directories must contain a per-candidate summary; "
                f"underscore-prefixed dirs are convention-skipped."
            )
        summary = json.loads(path.read_text())
        if "hypothesis_hash" not in summary:
            raise ValueError(
                f"holdout_summary.json at {path} is missing required "
                f"top-level field 'hypothesis_hash'. This loader treats "
                f"non-convention candidate dirs as strict per-candidate "
                f"artifacts; aggregate-style summaries belong under "
                f"underscore-prefixed convention dirs (e.g., '_smoke')."
            )
        h = summary["hypothesis_hash"]
        if h in out:
            raise ValueError(
                f"Duplicate hypothesis_hash {h!r} found under {run_dir}"
            )
        out[h] = summary
    if expected_count is not None and len(out) != expected_count:
        raise ValueError(
            f"Loaded {len(out)} per-candidate summaries from {run_dir}; "
            f"expected {expected_count}. Cardinality mismatch indicates "
            f"a producer regression or partial artifact set."
        )
    return out


# ---------------------------------------------------------------------------
# Per-candidate row construction (n-way)
# ---------------------------------------------------------------------------


def _derive_filter_state(
    in_filtered: bool, holdout_passed: bool | None
) -> str:
    """Tri-valued enum: survivor_passed | survivor_failed | excluded.

    Inherited from compare_2022_vs_2024 pattern. holdout_passed=None
    (error) maps to survivor_failed when in filtered set.
    """
    if not in_filtered:
        return "excluded"
    if holdout_passed is True:
        return "survivor_passed"
    return "survivor_failed"


def _build_per_candidate_row(
    *,
    hypothesis_hash: str,
    regime_keys: list[str],
    unfiltered_artifacts_by_label: dict[str, dict[str, dict[str, Any]]],
    filtered_artifacts_by_label: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    """Build one row joining N regime outcomes for a single candidate.

    Per-regime fields stamped: holdout_<label>_passed,
    holdout_<label>_filter_state, holdout_<label>_total_trades,
    holdout_<label>_sharpe. Aggregate fields: pass_count_unfiltered (int),
    pass_count_filtered (int), partition (primary/audit_only).

    holdout_passed=None (error state) does NOT count toward pass_count;
    only explicit True increments.
    """
    row: dict[str, Any] = {"hypothesis_hash": hypothesis_hash}

    # wf_test_period_sharpe + theme + partition pulled from first regime
    # (invariant across regimes by construction; same candidate, same
    # source_batch_id, same wf metric).
    first_label = _resolve_regime_metadata(regime_keys[0])["label"]
    first_summary = unfiltered_artifacts_by_label[first_label][hypothesis_hash]
    wf_sharpe = float(first_summary.get("wf_test_period_sharpe", 0.0))
    row["theme"] = first_summary.get("theme", "")
    row["wf_test_period_sharpe"] = wf_sharpe
    row["partition"] = (
        "primary" if wf_sharpe > PRIMARY_THRESHOLD else "audit_only"
    )

    pass_count_unfiltered = 0
    pass_count_filtered = 0

    for regime_key in regime_keys:
        meta = _resolve_regime_metadata(regime_key)
        label = meta["label"]
        unfiltered_summary = unfiltered_artifacts_by_label.get(label, {}).get(
            hypothesis_hash
        )
        if unfiltered_summary is None:
            # Absent unfiltered candidate is unexpected at n=4 symmetric;
            # leave fields null + skip pass-count contribution.
            row[f"holdout_{label}_passed"] = None
            row[f"holdout_{label}_filter_state"] = "missing"
            row[f"holdout_{label}_total_trades"] = None
            row[f"holdout_{label}_sharpe"] = None
            row[f"holdout_{label}_in_sample_caveat"] = (
                meta["in_sample_caveat_applies"]
            )
            continue

        holdout_passed = unfiltered_summary.get("holdout_passed")
        m = unfiltered_summary.get("holdout_metrics") or {}
        in_filtered = (
            hypothesis_hash in filtered_artifacts_by_label.get(label, {})
        )
        filter_state = _derive_filter_state(in_filtered, holdout_passed)

        row[f"holdout_{label}_passed"] = holdout_passed
        row[f"holdout_{label}_filter_state"] = filter_state
        row[f"holdout_{label}_total_trades"] = m.get("total_trades")
        row[f"holdout_{label}_sharpe"] = m.get("sharpe_ratio")
        row[f"holdout_{label}_in_sample_caveat"] = (
            meta["in_sample_caveat_applies"]
        )

        if holdout_passed is True:
            pass_count_unfiltered += 1
            if filter_state == "survivor_passed":
                pass_count_filtered += 1

    row["pass_count_unfiltered"] = pass_count_unfiltered
    row["pass_count_filtered"] = pass_count_filtered
    return row


# ---------------------------------------------------------------------------
# Cohort categorization
# ---------------------------------------------------------------------------


def _build_cohort_categorization(
    rows: list[dict[str, Any]], n_regimes: int
) -> dict[str, list[str]]:
    """Categorize candidates into cohort (a) cross-regime survivors and
    cohort (c) failures.

    Cohort (a) unfiltered: pass_count_unfiltered == n_regimes
    Cohort (a) filtered:   pass_count_filtered == n_regimes
    Cohort (c):            pass_count_unfiltered == 0
    """
    cohort_a_unfiltered = [
        r["hypothesis_hash"]
        for r in rows
        if r["pass_count_unfiltered"] == n_regimes
    ]
    cohort_a_filtered = [
        r["hypothesis_hash"]
        for r in rows
        if r["pass_count_filtered"] == n_regimes
    ]
    cohort_c_unfiltered = [
        r["hypothesis_hash"]
        for r in rows
        if r["pass_count_unfiltered"] == 0
    ]
    return {
        "cohort_a_unfiltered": cohort_a_unfiltered,
        "cohort_a_filtered": cohort_a_filtered,
        "cohort_c_unfiltered": cohort_c_unfiltered,
    }


def _build_pass_count_distribution(
    rows: list[dict[str, Any]], n_regimes: int
) -> dict[str, dict[int, int]]:
    """Histogram of pass-counts at unfiltered + filtered tier."""
    unfiltered = {i: 0 for i in range(n_regimes + 1)}
    filtered = {i: 0 for i in range(n_regimes + 1)}
    for r in rows:
        unfiltered[r["pass_count_unfiltered"]] += 1
        filtered[r["pass_count_filtered"]] += 1
    return {"unfiltered": unfiltered, "filtered": filtered}


# ---------------------------------------------------------------------------
# In-sample caveat stratification
# ---------------------------------------------------------------------------


def _stratify_in_sample_caveat(
    per_regime_passes: dict[str, bool],
    regime_keys: list[str],
) -> dict[str, int]:
    """Count pass count split by in_sample_caveat_applies classification.

    Returns:
        - fully_out_of_sample_pass_count: count of caveat=false regimes passed
        - train_overlap_pass_count: count of caveat=true regimes passed
    """
    fos_count = 0
    to_count = 0
    for regime_key in regime_keys:
        meta = _resolve_regime_metadata(regime_key)
        label = meta["label"]
        passed = per_regime_passes.get(label, False)
        if not passed:
            continue
        if meta["in_sample_caveat_applies"]:
            to_count += 1
        else:
            fos_count += 1
    return {
        "fully_out_of_sample_pass_count": fos_count,
        "train_overlap_pass_count": to_count,
    }


# ---------------------------------------------------------------------------
# Top-level comparison
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MultiRegimeComparisonResult:
    n_regimes: int
    n_candidates: int
    cohort_a_cardinality_unfiltered: int
    cohort_a_cardinality_filtered: int
    cohort_c_cardinality_unfiltered: int
    output_dir: Path


def apply_multi_regime_comparison(
    *,
    regime_inputs: list[RegimeInput],
    output_dir: Path,
    force: bool = False,
) -> MultiRegimeComparisonResult:
    """Build the n-way candidate-aligned comparison matrix.

    Args:
        regime_inputs: list of RegimeInput descriptors (one per regime;
            n_regimes = len(regime_inputs); n_regimes must be >= 2).
        output_dir: Destination for comparison_matrix.csv +
            comparison_summary.json.
        force: Allow overwriting non-empty output_dir.

    Raises:
        ValueError: If candidate universes do not exactly match across
            all regimes (universe symmetry assertion); if any filtered
            set contains a hash absent from its unfiltered counterpart.
        FileExistsError: output_dir non-empty without force.
    """
    if len(regime_inputs) < 2:
        raise ValueError(
            f"n_regimes={len(regime_inputs)} < 2; need at least 2 regimes"
        )

    output_dir = Path(output_dir)
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

    # Load all artifacts (unfiltered + filtered per regime).
    # For each tier, derive an authoritative expected_count from
    # holdout_results.csv row count (the producer's canonical universe
    # declaration); pass it to _load_run_artifacts so cardinality
    # mismatches between per-candidate JSON dirs and the producer's CSV
    # surface as a hard error rather than silently propagating.
    unfiltered_arts: dict[str, dict[str, dict[str, Any]]] = {}
    filtered_arts: dict[str, dict[str, dict[str, Any]]] = {}
    regime_keys: list[str] = []
    regime_metadata_records: list[dict[str, Any]] = []

    for ri in regime_inputs:
        meta = _resolve_regime_metadata(ri.regime_key)
        label = meta["label"]
        regime_keys.append(ri.regime_key)
        unf_expected = _expected_count_from_results_csv(ri.unfiltered_dir)
        filt_expected = _expected_count_from_results_csv(ri.filtered_dir)
        unfiltered_arts[label] = _load_run_artifacts(
            ri.unfiltered_dir, expected_count=unf_expected
        )
        filtered_arts[label] = _load_run_artifacts(
            ri.filtered_dir, expected_count=filt_expected
        )
        # Disk-state schema reflection: sample one per-candidate summary
        # to determine the actual schema_discriminator on disk. Legacy
        # PHASE2C_6 artifacts (audit_v1) carry no field; producer-mapping
        # would say phase2c_7_1 hypothetically but disk reads None.
        disk_schema_version: str | None = None
        if unfiltered_arts[label]:
            sample_summary = next(iter(unfiltered_arts[label].values()))
            disk_schema_version = sample_summary.get("artifact_schema_version")
        regime_metadata_records.append({
            "regime_key": ri.regime_key,
            "label": label,
            "schema_version": disk_schema_version,
            "schema_version_per_producer_mapping": meta["schema_version"],
            "in_sample_caveat_applies": meta["in_sample_caveat_applies"],
            "unfiltered_path": str(ri.unfiltered_dir),
            "filtered_path": str(ri.filtered_dir),
            "n_unfiltered": len(unfiltered_arts[label]),
            "n_filtered": len(filtered_arts[label]),
        })

    # Universe symmetry assertion: all regimes' unfiltered sets identical.
    universes = [set(unfiltered_arts[m["label"]]) for m in regime_metadata_records]
    canonical_universe = universes[0]
    for i, u in enumerate(universes[1:], start=1):
        diff = canonical_universe ^ u
        if diff:
            raise ValueError(
                f"Universe mismatch: regime {regime_metadata_records[0]['label']} "
                f"and regime {regime_metadata_records[i]['label']} differ on "
                f"{len(diff)} hashes. Sample: {sorted(diff)[:5]}. Refusing to "
                f"compute comparison over partial intersection."
            )

    # Filtered-subset assertion per regime
    for m in regime_metadata_records:
        label = m["label"]
        filtered_extras = (
            set(filtered_arts[label]) - set(unfiltered_arts[label])
        )
        if filtered_extras:
            raise ValueError(
                f"{label}_filtered contains {len(filtered_extras)} hashes "
                f"absent from {label} unfiltered. Sample: "
                f"{sorted(filtered_extras)[:5]}."
            )

    # Build per-candidate rows
    rows: list[dict[str, Any]] = []
    for h in sorted(canonical_universe):
        rows.append(
            _build_per_candidate_row(
                hypothesis_hash=h,
                regime_keys=regime_keys,
                unfiltered_artifacts_by_label=unfiltered_arts,
                filtered_artifacts_by_label=filtered_arts,
            )
        )

    # Cohort categorization + distribution
    cohorts = _build_cohort_categorization(rows, n_regimes=len(regime_inputs))
    pass_count_dist = _build_pass_count_distribution(
        rows, n_regimes=len(regime_inputs)
    )

    # CSV write
    csv_fields = ["hypothesis_hash", "theme", "partition", "wf_test_period_sharpe"]
    for m in regime_metadata_records:
        label = m["label"]
        csv_fields.extend([
            f"holdout_{label}_passed",
            f"holdout_{label}_filter_state",
            f"holdout_{label}_total_trades",
            f"holdout_{label}_sharpe",
            f"holdout_{label}_in_sample_caveat",
        ])
    csv_fields.extend(["pass_count_unfiltered", "pass_count_filtered"])

    csv_path = output_dir / "comparison_matrix.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({
                k: ("" if r.get(k) is None else r.get(k)) for k in csv_fields
            })

    # In-sample caveat stratification: aggregate across rows
    n_passing_all_fully_out_of_sample = 0
    n_passing_all_train_overlap = 0
    fos_regimes = [
        m["label"] for m in regime_metadata_records
        if not m["in_sample_caveat_applies"]
    ]
    to_regimes = [
        m["label"] for m in regime_metadata_records
        if m["in_sample_caveat_applies"]
    ]
    for r in rows:
        fos_passes = sum(
            1 for label in fos_regimes
            if r.get(f"holdout_{label}_passed") is True
        )
        to_passes = sum(
            1 for label in to_regimes
            if r.get(f"holdout_{label}_passed") is True
        )
        if fos_regimes and fos_passes == len(fos_regimes):
            n_passing_all_fully_out_of_sample += 1
        if to_regimes and to_passes == len(to_regimes):
            n_passing_all_train_overlap += 1

    # JSON summary
    cmp_obj: dict[str, Any] = {
        "comparison_schema_version": COMPARISON_SCHEMA_VERSION,
        "produced_at_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "regime_metadata": regime_metadata_records,
        "totals": {
            "n_candidates": len(rows),
            "n_regimes": len(regime_inputs),
        },
        "cohort_a_unfiltered": cohorts["cohort_a_unfiltered"],
        "cohort_a_filtered": cohorts["cohort_a_filtered"],
        "cohort_c_unfiltered": cohorts["cohort_c_unfiltered"],
        "cohort_a_cardinality_unfiltered": len(cohorts["cohort_a_unfiltered"]),
        "cohort_a_cardinality_filtered": len(cohorts["cohort_a_filtered"]),
        "cohort_c_cardinality_unfiltered": len(cohorts["cohort_c_unfiltered"]),
        "pass_count_distribution": pass_count_dist,
        "in_sample_caveat_stratification": {
            "fully_out_of_sample_regimes": fos_regimes,
            "train_overlap_regimes": to_regimes,
            "n_passing_all_fully_out_of_sample": n_passing_all_fully_out_of_sample,
            "n_passing_all_train_overlap": n_passing_all_train_overlap,
        },
    }
    (output_dir / "comparison_summary.json").write_text(
        json.dumps(cmp_obj, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return MultiRegimeComparisonResult(
        n_regimes=len(regime_inputs),
        n_candidates=len(rows),
        cohort_a_cardinality_unfiltered=len(cohorts["cohort_a_unfiltered"]),
        cohort_a_cardinality_filtered=len(cohorts["cohort_a_filtered"]),
        cohort_c_cardinality_unfiltered=len(cohorts["cohort_c_unfiltered"]),
        output_dir=output_dir,
    )


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------


def _parse_key_dir_pair(token: str) -> tuple[str, Path]:
    """Parse a 'regime_key=path' token; raises ValueError on malformed input."""
    if "=" not in token:
        raise ValueError(
            f"Expected key=dir format; got {token!r}. "
            f"Example: --regime-input v2.regime_holdout=data/foo/audit_v1"
        )
    key, _, raw_path = token.partition("=")
    return key, Path(raw_path)


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "PHASE2C_8.1 §8 Step 4 — multi-regime n-way candidate-aligned "
            "comparison. Reads N regime artifact sets and produces "
            "comparison_matrix.csv + comparison_summary.json with cohort "
            "categorization + in_sample_caveat stratification."
        ),
    )
    parser.add_argument(
        "--regime-input",
        type=str,
        action="append",
        required=True,
        help=(
            "Per-regime unfiltered artifact dir as 'regime_key=path'. "
            "Repeat for each regime (n>=2). Example: "
            "--regime-input v2.regime_holdout=data/phase2c_evaluation_gate/audit_v1"
        ),
    )
    parser.add_argument(
        "--filtered-input",
        type=str,
        action="append",
        required=True,
        help=(
            "Per-regime filtered artifact dir as 'regime_key=path'. "
            "Symmetric n-way assumes one per regime."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Comparison output directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
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

    unfiltered_pairs = dict(
        _parse_key_dir_pair(t) for t in args.regime_input
    )
    filtered_pairs = dict(
        _parse_key_dir_pair(t) for t in args.filtered_input
    )

    if set(unfiltered_pairs) != set(filtered_pairs):
        print(
            f"ERROR: --regime-input and --filtered-input must specify the "
            f"same set of regime_keys. unfiltered keys: "
            f"{sorted(unfiltered_pairs)}; filtered keys: "
            f"{sorted(filtered_pairs)}",
            file=sys.stderr,
        )
        return 2

    regime_inputs = [
        RegimeInput(
            regime_key=key,
            unfiltered_dir=unfiltered_pairs[key],
            filtered_dir=filtered_pairs[key],
        )
        for key in unfiltered_pairs
    ]

    output_dir = Path(args.output_dir).resolve()

    print(f"[compare_multi_regime] n_regimes: {len(regime_inputs)}")
    for ri in regime_inputs:
        print(
            f"[compare_multi_regime]   regime: {ri.regime_key} "
            f"unfiltered={ri.unfiltered_dir} filtered={ri.filtered_dir}"
        )
    print(f"[compare_multi_regime] output_dir: {output_dir}")

    try:
        result = apply_multi_regime_comparison(
            regime_inputs=regime_inputs,
            output_dir=output_dir,
            force=args.force,
        )
    except FileExistsError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(
        f"[compare_multi_regime] n_candidates={result.n_candidates} "
        f"cohort_a_unfiltered={result.cohort_a_cardinality_unfiltered} "
        f"cohort_a_filtered={result.cohort_a_cardinality_filtered} "
        f"cohort_c_unfiltered={result.cohort_c_cardinality_unfiltered}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
