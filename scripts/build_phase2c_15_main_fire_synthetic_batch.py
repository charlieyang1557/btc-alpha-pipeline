"""Build PHASE2C_15 main-fire synthetic merged batch directory (K=5 variant).

Closeout-register-class utility script (NOT framework-resident) for
PHASE2C_15 implementation arc main fire register.

Register-class-distinct from `build_phase2c_15_smoke_synthetic_batch.py`
per Codex C4 patch on smoke variant: smoke variant is K=2 only by design;
this main-fire variant operates at K=5 per PLAN §1.2 locked parameter
(K=5 batches × N_per_batch=200 = 1000 universe nominal).

Inherits register-precision corrections from 8 Codex patches landed at
smoke variant (C1 CSV-backed symlink + C2 relative symlinks + full
batch IDs + C3 duplicate hash detection + C5 multi-item validation +
C6 explicit error register + C7 stdev/quantile guard + NB #1 OR
orientation metadata).

CLI-parameterized for testability + main-fire batch_ids unknown until
generation completes; default paths point to canonical main-fire
locations.

Operational mechanism (K-agnostic):
- Concatenate walk_forward_results.csv from K source batches
- Renumber positions 1..N (N = sum of per-source row counts)
- Synthesize walk_forward_summary.json aggregating compile/runtime/
  sharpe stats from K source summaries
- Symlink raw_payloads attempt_NNNN_response.txt files at synthetic
  dir with renumbered positions

Output:
- {wf-root}/batch_{synthetic-batch-id}_corrected/
- {raw-payloads-root}/batch_{synthetic-batch-id}/
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_WF_ROOT = PROJECT_ROOT / "data" / "phase2c_walkforward"
DEFAULT_RAW_PAYLOADS_ROOT = PROJECT_ROOT / "raw_payloads"
DEFAULT_SYNTHETIC_BATCH_ID = "phase2c_15_main_fire_combined"
DEFAULT_EXPECTED_K = 5


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Build PHASE2C_15 main-fire K=5 synthetic merged batch directory."
        ),
    )
    p.add_argument(
        "--source-batch-ids",
        nargs="+",
        required=True,
        help=(
            "Source batch UUIDs from main-fire generation (K batches; "
            "K=5 expected per PLAN §1.2)."
        ),
    )
    p.add_argument(
        "--synthetic-batch-id",
        default=DEFAULT_SYNTHETIC_BATCH_ID,
        help=f"Synthetic batch ID (default: {DEFAULT_SYNTHETIC_BATCH_ID}).",
    )
    p.add_argument(
        "--wf-root",
        default=str(DEFAULT_WF_ROOT),
        help="Walk-forward root directory.",
    )
    p.add_argument(
        "--raw-payloads-root",
        default=str(DEFAULT_RAW_PAYLOADS_ROOT),
        help="Raw payloads root directory.",
    )
    p.add_argument(
        "--expected-k",
        type=int,
        default=DEFAULT_EXPECTED_K,
        help=(
            f"Expected K (number of source batches; default: "
            f"{DEFAULT_EXPECTED_K} per PLAN §1.2). Mismatch raises."
        ),
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()

    source_batch_ids: list[str] = list(args.source_batch_ids)
    synthetic_batch_id: str = args.synthetic_batch_id
    wf_root = Path(args.wf_root)
    raw_payloads_root = Path(args.raw_payloads_root)
    expected_k: int = args.expected_k

    # Per Codex C4 register-precedent: explicit K guard (K=5 main-fire by
    # design per PLAN §1.2). Mismatch raises rather than silently merging
    # at unexpected K.
    if len(source_batch_ids) != expected_k:
        raise ValueError(
            f"Expected K={expected_k} source batches per PLAN §1.2; got "
            f"{len(source_batch_ids)}: {source_batch_ids}. Adjust "
            f"--source-batch-ids or --expected-k."
        )

    synthetic_wf_dir = wf_root / f"batch_{synthetic_batch_id}_corrected"
    synthetic_raw_dir = raw_payloads_root / f"batch_{synthetic_batch_id}"

    if synthetic_wf_dir.exists():
        raise FileExistsError(
            f"Synthetic WF dir already exists at {synthetic_wf_dir}. "
            f"Remove manually if rebuild needed."
        )
    if synthetic_raw_dir.exists():
        raise FileExistsError(
            f"Synthetic raw_payloads dir already exists at "
            f"{synthetic_raw_dir}. Remove manually if rebuild needed."
        )

    synthetic_wf_dir.mkdir(parents=True)
    synthetic_raw_dir.mkdir(parents=True)

    print(f"[main-fire setup] K = {expected_k}")
    print(f"[main-fire setup] Synthetic batch_id: {synthetic_batch_id}")
    print(f"[main-fire setup] WF output dir: {synthetic_wf_dir}")
    print(f"[main-fire setup] raw_payloads output dir: {synthetic_raw_dir}")

    # --- Step 1: Concatenate WF csvs with position renumbering ---
    # Per Codex C5: validate CSV header equality across sources; per-source
    # position contiguity 1..N; batch_id preservation per row.
    # Per Codex C1: track per-source CSV positions for downstream symlink
    # construction to avoid attempt-file-vs-CSV-row drift.
    all_rows: list[dict[str, str]] = []
    csv_header: list[str] | None = None
    position_offset = 0
    src_csv_positions: dict[str, list[int]] = {}

    for src_batch_id in source_batch_ids:
        src_csv = (
            wf_root / f"batch_{src_batch_id}_corrected" / "walk_forward_results.csv"
        )
        if not src_csv.exists():
            raise FileNotFoundError(f"Source WF csv missing: {src_csv}")

        with open(src_csv) as f:
            reader = csv.DictReader(f)
            src_fieldnames = reader.fieldnames or []
            if csv_header is None:
                csv_header = src_fieldnames
            elif src_fieldnames != csv_header:
                raise ValueError(
                    f"CSV header drift detected at batch_{src_batch_id}: "
                    f"first source had {csv_header!r}; this source has "
                    f"{src_fieldnames!r}. Cannot safely concatenate."
                )
            rows = list(reader)

        n_src = len(rows)
        src_positions = [int(r["position"]) for r in rows]
        expected_positions = list(range(1, n_src + 1))
        if src_positions != expected_positions:
            raise ValueError(
                f"Per-source position contiguity violated at "
                f"batch_{src_batch_id}: expected 1..{n_src}, got "
                f"first={src_positions[:5]}, last={src_positions[-5:]}."
            )

        new_positions: list[int] = []
        for row in rows:
            original_position = int(row["position"])
            new_position = original_position + position_offset
            row["position"] = str(new_position)
            new_positions.append(new_position)
            if row["batch_id"] != src_batch_id:
                raise ValueError(
                    f"batch_id drift at row position={original_position} in "
                    f"batch_{src_batch_id}: row carries "
                    f"batch_id={row['batch_id']!r}, expected "
                    f"batch_id={src_batch_id!r}."
                )
            all_rows.append(row)

        src_csv_positions[src_batch_id] = new_positions

        print(
            f"[main-fire setup] Concatenated {n_src} rows from "
            f"batch_{src_batch_id[:8]}... (positions "
            f"{position_offset + 1}-{position_offset + n_src})"
        )
        position_offset += n_src

    # Per Codex C3: assert global uniqueness of non-empty hypothesis_hash.
    # At K=5 × N=200 = 1000 universe, collision probability is higher than
    # K=2 × N=50 = 100; this guard substantively load-bearing here.
    seen: set[str] = set()
    duplicates: list[tuple[str, int]] = []
    for r in all_rows:
        h = r["hypothesis_hash"]
        if not h:
            continue
        if h in seen:
            duplicates.append((h, int(r["position"])))
        seen.add(h)
    if duplicates:
        raise ValueError(
            f"Duplicate hypothesis_hash detected across merged CSV rows: "
            f"{duplicates[:5]} (showing first 5 of {len(duplicates)}). "
            f"Cannot safely synthesize merged batch — eval gate is hash-keyed."
        )

    synthetic_csv = synthetic_wf_dir / "walk_forward_results.csv"
    with open(synthetic_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_header)
        writer.writeheader()
        writer.writerows(all_rows)
    non_empty_hashes = [r["hypothesis_hash"] for r in all_rows if r["hypothesis_hash"]]
    print(
        f"[main-fire setup] Wrote {len(all_rows)} rows to {synthetic_csv} "
        f"({len(non_empty_hashes)} non-empty hashes; uniqueness verified)"
    )

    # --- Step 2: Synthesize WF summary JSON ---
    src_summaries: list[dict] = []
    for src_batch_id in source_batch_ids:
        src_summary_path = (
            wf_root / f"batch_{src_batch_id}_corrected" / "walk_forward_summary.json"
        )
        with open(src_summary_path) as f:
            src_summaries.append(json.load(f))

    # Per Codex C5: validate source summary batch_id matches expected +
    # total_candidates matches CSV row count per source.
    for src_batch_id, summary in zip(source_batch_ids, src_summaries):
        if summary.get("batch_id") != src_batch_id:
            raise ValueError(
                f"Source summary batch_id mismatch: expected "
                f"{src_batch_id!r}, got {summary.get('batch_id')!r}."
            )
        n_csv_rows_for_src = len(src_csv_positions[src_batch_id])
        if summary.get("total_candidates") != n_csv_rows_for_src:
            raise ValueError(
                f"Source summary total_candidates mismatch at "
                f"batch_{src_batch_id}: summary reports "
                f"{summary.get('total_candidates')}, CSV has "
                f"{n_csv_rows_for_src} rows."
            )

    agg_compile: dict[str, int] = {}
    agg_runtime: dict[str, int] = {}
    for s in src_summaries:
        for k, v in s["compile_status_counts"].items():
            agg_compile[k] = agg_compile.get(k, 0) + v
        for k, v in s["runtime_status_counts"].items():
            agg_runtime[k] = agg_runtime.get(k, 0) + v

    # Per Codex C7: guard N>=2 for stdev/quantile computation.
    sharpe_values = [
        float(r["wf_test_period_sharpe"])
        for r in all_rows
        if r["compile_status"] == "ok"
        and r["runtime_status"] == "ok"
        and r["wf_test_period_sharpe"]
    ]
    if len(sharpe_values) < 2:
        raise ValueError(
            f"Cannot compute synthetic sharpe distribution: insufficient "
            f"successful candidates (N={len(sharpe_values)}; stdev/quantile "
            f"require N>=2). Synthesize would produce malformed summary."
        )

    threshold = src_summaries[0]["phase1_success_threshold"]
    sharpe_dist = {
        "n": len(sharpe_values),
        "median": statistics.median(sharpe_values),
        "mean": statistics.mean(sharpe_values),
        "stdev": statistics.stdev(sharpe_values),
        "min": min(sharpe_values),
        "p10": statistics.quantiles(sharpe_values, n=10)[0],
        "p25": statistics.quantiles(sharpe_values, n=4)[0],
        "p75": statistics.quantiles(sharpe_values, n=4)[2],
        "p90": statistics.quantiles(sharpe_values, n=10)[8],
        "max": max(sharpe_values),
        "count_gt_0_0": sum(1 for x in sharpe_values if x > 0.0),
        "count_gt_0_5": sum(1 for x in sharpe_values if x > 0.5),
        "count_gt_neg_0_3": sum(1 for x in sharpe_values if x > -0.3),
        "count_above_phase1_threshold": sum(
            1 for x in sharpe_values if x > threshold
        ),
        "phase1_threshold_value_used": threshold,
    }

    # Per Codex C5: lineage parity inclusive of current_git_sha.
    lineage_fields = (
        "corrected_wf_semantics_commit",
        "wf_semantics",
        "lineage_check",
        "git_sha",
        "current_git_sha",
        "phase1_success_threshold",
    )
    for field in lineage_fields:
        vals = {s.get(field) for s in src_summaries}
        if len(vals) > 1:
            raise ValueError(
                f"Source summaries diverge on {field!r}: {vals}. "
                f"Cannot safely synthesize."
            )

    total_elapsed = sum(s["total_elapsed_seconds"] for s in src_summaries)
    total_cand = sum(s["total_candidates"] for s in src_summaries)
    mean_elapsed = total_elapsed / total_cand if total_cand else 0.0

    starts = [s["run_started_utc"] for s in src_summaries]
    finishes = [s["run_finished_utc"] for s in src_summaries]
    started_utc = min(starts)
    finished_utc = max(finishes)

    binary_met = sharpe_dist["count_above_phase1_threshold"] > 0

    synthetic_summary = {
        "batch_id": synthetic_batch_id,
        "synthetic_source_batch_ids": source_batch_ids,
        "synthetic_assembled_utc": (
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ),
        "compile_status_counts": agg_compile,
        "runtime_status_counts": agg_runtime,
        "corrected_wf_semantics_commit": src_summaries[0][
            "corrected_wf_semantics_commit"
        ],
        "current_git_sha": src_summaries[0]["current_git_sha"],
        "git_sha": src_summaries[0]["git_sha"],
        "lineage_check": src_summaries[0]["lineage_check"],
        "mean_elapsed_per_candidate_seconds": round(mean_elapsed, 4),
        "phase1_binary_success_criterion_met": binary_met,
        "phase1_success_threshold": src_summaries[0]["phase1_success_threshold"],
        "run_finished_utc": finished_utc,
        "run_started_utc": started_utc,
        "total_candidates": total_cand,
        "total_elapsed_seconds": round(total_elapsed, 3),
        "wf_semantics": src_summaries[0]["wf_semantics"],
        "wf_test_period_sharpe_distribution": sharpe_dist,
    }

    synthetic_summary_path = synthetic_wf_dir / "walk_forward_summary.json"
    with open(synthetic_summary_path, "w") as f:
        json.dump(synthetic_summary, f, indent=2)
    print(f"[main-fire setup] Wrote synthesized summary to {synthetic_summary_path}")

    # --- Step 3: Symlink raw_payloads with renumbered positions ---
    # Per Codex C1: symlink CSV-backed positions ONLY; do not assume per-
    # source attempt-file dirs are 1:1 aligned with CSV rows. K=5 × N=200
    # universe = 1000 candidates; non-1:1 alignment would silently drop
    # candidates if not explicitly checked.
    # Per Codex C2: relative symlinks for portability + full batch IDs at
    # source_stage2d_summary file names (8-char prefix collision risk
    # higher at K=5 than K=2).
    for src_batch_id in source_batch_ids:
        src_raw_dir = raw_payloads_root / f"batch_{src_batch_id}"
        if not src_raw_dir.exists():
            raise FileNotFoundError(
                f"Source raw_payloads dir missing: {src_raw_dir}"
            )

        response_by_position: dict[int, Path] = {}
        for src_file in src_raw_dir.glob("attempt_*_response.txt"):
            filename = src_file.name
            try:
                orig_position = int(filename.split("_")[1])
            except (ValueError, IndexError):
                continue
            response_by_position[orig_position] = src_file

        new_positions_for_src = src_csv_positions[src_batch_id]
        src_offset = new_positions_for_src[0] - 1
        original_positions = [p - src_offset for p in new_positions_for_src]

        missing = [p for p in original_positions if p not in response_by_position]
        if missing:
            raise FileNotFoundError(
                f"CSV-backed positions missing attempt-response files at "
                f"batch_{src_batch_id}: {missing[:5]} (showing first 5 of "
                f"{len(missing)})."
            )

        n_linked = 0
        for orig_pos, new_pos in zip(original_positions, new_positions_for_src):
            src_file = response_by_position[orig_pos]
            new_filename = f"attempt_{new_pos:04d}_response.txt"
            symlink_path = synthetic_raw_dir / new_filename
            rel_target = os.path.relpath(src_file, start=synthetic_raw_dir)
            symlink_path.symlink_to(rel_target)
            n_linked += 1

        # Per Codex C2: full batch ID (not 8-char prefix) at link name.
        src_stage2d = src_raw_dir / "stage2d_summary.json"
        if src_stage2d.exists():
            link_name = f"source_stage2d_summary_{src_batch_id}.json"
            symlink_path = synthetic_raw_dir / link_name
            rel_target = os.path.relpath(src_stage2d, start=synthetic_raw_dir)
            symlink_path.symlink_to(rel_target)

        print(
            f"[main-fire setup] Symlinked {n_linked} CSV-backed response files "
            f"from batch_{src_batch_id[:8]}... → new positions "
            f"{new_positions_for_src[0]}-{new_positions_for_src[-1]}"
        )

    # --- Step 4: Forensic verification ---
    # Per Codex C6: data/audit assertions promoted to RuntimeError to
    # survive python -O. K-agnostic on counts.
    print()
    print("[main-fire setup] === FORENSIC VERIFICATION ===")
    expected_total = position_offset

    with open(synthetic_csv) as f:
        synth_rows = list(csv.DictReader(f))
    if len(synth_rows) != expected_total:
        raise RuntimeError(
            f"CSV row count drift: synthetic CSV has {len(synth_rows)} rows; "
            f"expected {expected_total} (sum of source CSV row counts)."
        )
    print(f"  CSV row count: {len(synth_rows)} ✓")

    positions = sorted(int(r["position"]) for r in synth_rows)
    expected_positions = list(range(1, expected_total + 1))
    if positions != expected_positions:
        raise RuntimeError(
            f"Position contiguity violated: synthetic CSV positions "
            f"first={positions[:5]}, last={positions[-5:]}; expected "
            f"contiguous 1..{expected_total}."
        )
    print(f"  Position contiguity 1-{expected_total}: ✓")

    per_source_counts: dict[str, int] = {b: 0 for b in source_batch_ids}
    for r in synth_rows:
        if r["batch_id"] in per_source_counts:
            per_source_counts[r["batch_id"]] += 1
    expected_per_source = {
        b: len(src_csv_positions[b]) for b in source_batch_ids
    }
    if per_source_counts != expected_per_source:
        raise RuntimeError(
            f"batch_id preservation violated: synthetic CSV per-source "
            f"counts={per_source_counts}; expected={expected_per_source}."
        )
    print(
        f"  Original batch_id preserved per row: K={expected_k} sources, "
        f"counts={per_source_counts} ✓"
    )

    # Per Codex C1: exhaustive symlink resolution check (not spot-check).
    broken_links: list[tuple[int, str]] = []
    for pos in expected_positions:
        link = synthetic_raw_dir / f"attempt_{pos:04d}_response.txt"
        if not link.exists():
            broken_links.append((pos, "missing"))
            continue
        if not link.is_symlink():
            broken_links.append((pos, "not_a_symlink"))
            continue
        target = link.resolve()
        if not target.exists() or not target.is_file():
            broken_links.append((pos, f"target_missing: {target}"))
    if broken_links:
        raise RuntimeError(
            f"Symlink resolution failed for "
            f"{len(broken_links)} CSV-backed positions: "
            f"{broken_links[:5]} (showing first 5)."
        )
    print(
        f"  Symlink resolution: {len(expected_positions)}/"
        f"{len(expected_positions)} CSV-backed positions resolve ✓"
    )

    response_links = list(synthetic_raw_dir.glob("attempt_*_response.txt"))
    if len(response_links) != expected_total:
        raise RuntimeError(
            f"Symlink count drift: found {len(response_links)} response "
            f"symlinks at {synthetic_raw_dir}; expected {expected_total}."
        )
    print(f"  Symlink count: {len(response_links)} response files ✓")

    with open(synthetic_summary_path) as f:
        synth_sum = json.load(f)
    summary_checks = [
        ("total_candidates", synth_sum.get("total_candidates"), expected_total),
        ("batch_id", synth_sum.get("batch_id"), synthetic_batch_id),
        ("lineage_check", synth_sum.get("lineage_check"), "passed"),
    ]
    for field, actual, expected in summary_checks:
        if actual != expected:
            raise RuntimeError(
                f"Synthetic summary {field!r} drift: actual={actual!r}; "
                f"expected={expected!r}."
            )
    expected_compile_ok = sum(
        s["compile_status_counts"].get("ok", 0) for s in src_summaries
    )
    expected_runtime_ok = sum(
        s["runtime_status_counts"].get("ok", 0) for s in src_summaries
    )
    actual_compile_ok = synth_sum.get("compile_status_counts", {}).get("ok", 0)
    actual_runtime_ok = synth_sum.get("runtime_status_counts", {}).get("ok", 0)
    if actual_compile_ok != expected_compile_ok:
        raise RuntimeError(
            f"Synthetic compile_status_counts.ok drift: "
            f"actual={actual_compile_ok}; expected={expected_compile_ok}."
        )
    if actual_runtime_ok != expected_runtime_ok:
        raise RuntimeError(
            f"Synthetic runtime_status_counts.ok drift: "
            f"actual={actual_runtime_ok}; expected={expected_runtime_ok}."
        )
    print(
        f"  Summary JSON: total_candidates={expected_total}, "
        f"lineage_check=passed, compile_ok={actual_compile_ok}, "
        f"runtime_ok={actual_runtime_ok} ✓"
    )

    print()
    print("[main-fire setup] All forensic checks PASSED")
    print(f"[main-fire setup] Synthetic batch ready at:")
    print(f"  WF: {synthetic_wf_dir}")
    print(f"  raw_payloads: {synthetic_raw_dir}")
    print()
    print("[main-fire setup] Eval gate can now fire with:")
    print(f"  --source-batch-id {synthetic_batch_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
