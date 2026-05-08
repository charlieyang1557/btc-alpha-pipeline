"""Build PHASE2C_15 smoke synthetic merged batch directory.

Closeout-register-class utility script (NOT framework-resident) for
PHASE2C_15 implementation arc Step 4 smoke fire register.

Per Q-S141 ENDORSE (mb-b synthetic merged batch directory): merges
PHASE2C_15 smoke K=2 batches (4c9634cd... + 49682edb...) into single
synthetic batch dir at canonical path so run_phase2c_evaluation_gate.py
can fire over merged universe at register-class match to Step 2 sub-spec
§3.3 selected lean (single merged-universe evaluation, 4 invocations).

Operational mechanism:
- Concatenate walk_forward_results.csv from both source batches
- Renumber positions 1-100 (b1: 1-50, b2: 51-100); preserve original
  batch_id per row (column already in csv schema)
- Synthesize walk_forward_summary.json aggregating compile/runtime/sharpe
  stats from both source summaries
- Symlink raw_payloads attempt_NNNN_response.txt files at synthetic dir
  with renumbered positions

Output:
- data/phase2c_walkforward/batch_phase2c_15_smoke_combined_corrected/
- raw_payloads/batch_phase2c_15_smoke_combined/

§19 instance #2 (multi-batch_id eval gate gap) operational resolution.
Logged at carry-forward register; finalized at PHASE2C_15 closeout
deliverable §A2 register-event boundary.
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import statistics
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_BATCH_IDS = [
    "4c9634cd-ef2b-4f5c-a78a-c558c24c0a7b",
    "49682edb-9493-4c69-bf67-2f32c22d3864",
]
SYNTHETIC_BATCH_ID = "phase2c_15_smoke_combined"

WF_ROOT = PROJECT_ROOT / "data" / "phase2c_walkforward"
RAW_PAYLOADS_ROOT = PROJECT_ROOT / "raw_payloads"


def main() -> int:
    synthetic_wf_dir = WF_ROOT / f"batch_{SYNTHETIC_BATCH_ID}_corrected"
    synthetic_raw_dir = RAW_PAYLOADS_ROOT / f"batch_{SYNTHETIC_BATCH_ID}"

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

    print(f"[mb-b setup] Synthetic batch_id: {SYNTHETIC_BATCH_ID}")
    print(f"[mb-b setup] WF output dir: {synthetic_wf_dir}")
    print(f"[mb-b setup] raw_payloads output dir: {synthetic_raw_dir}")

    # --- Step 1: Concatenate WF csvs with position renumbering ---
    # Per Codex C5: validate CSV header equality across sources; per-source
    # position contiguity 1..N; batch_id preservation per row.
    # Per Codex C1: track per-source CSV positions for downstream symlink
    # construction to avoid attempt-file-vs-CSV-row drift.
    all_rows: list[dict[str, str]] = []
    csv_header: list[str] | None = None
    position_offset = 0
    # Per-source CSV row positions (post-renumbering): used at Step 3 to
    # symlink only CSV-backed positions, not all attempt files in source dir.
    src_csv_positions: dict[str, list[int]] = {}

    for src_batch_id in SOURCE_BATCH_IDS:
        src_csv = (
            WF_ROOT / f"batch_{src_batch_id}_corrected" / "walk_forward_results.csv"
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
        # Validate per-source position contiguity 1..N before offsetting
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
            # batch_id column already preserves original generation uuid
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
            f"[mb-b setup] Concatenated {n_src} rows from "
            f"batch_{src_batch_id[:8]}... (positions "
            f"{position_offset + 1}-{position_offset + n_src})"
        )
        position_offset += n_src

    # Per Codex C3: assert global uniqueness of non-empty hypothesis_hash
    # across all merged CSV rows. Compile-failed rows may carry empty hash;
    # uniqueness check applies to non-empty values only.
    non_empty_hashes = [r["hypothesis_hash"] for r in all_rows if r["hypothesis_hash"]]
    seen: set[str] = set()
    duplicates: list[tuple[str, int]] = []  # (hash, position)
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

    # Write concatenated csv
    synthetic_csv = synthetic_wf_dir / "walk_forward_results.csv"
    with open(synthetic_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_header)
        writer.writeheader()
        writer.writerows(all_rows)
    print(
        f"[mb-b setup] Wrote {len(all_rows)} rows to {synthetic_csv} "
        f"({len(non_empty_hashes)} non-empty hashes; uniqueness verified)"
    )

    # --- Step 2: Synthesize WF summary JSON ---
    src_summaries: list[dict] = []
    for src_batch_id in SOURCE_BATCH_IDS:
        src_summary = (
            WF_ROOT / f"batch_{src_batch_id}_corrected" / "walk_forward_summary.json"
        )
        with open(src_summary) as f:
            src_summaries.append(json.load(f))

    # Per Codex C5: validate source summary batch_id matches expected +
    # total_candidates matches CSV row count per source.
    for src_batch_id, summary in zip(SOURCE_BATCH_IDS, src_summaries):
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

    # Aggregate compile/runtime status
    agg_compile: dict[str, int] = {}
    agg_runtime: dict[str, int] = {}
    for s in src_summaries:
        for k, v in s["compile_status_counts"].items():
            agg_compile[k] = agg_compile.get(k, 0) + v
        for k, v in s["runtime_status_counts"].items():
            agg_runtime[k] = agg_runtime.get(k, 0) + v

    # Aggregate sharpe distribution from concatenated csv (more accurate than
    # combining per-source distributions which would lose distributional info).
    # Per Codex C7: guard N>=2 for stdev/quantile computation; raise clear
    # error with sample size if guard fails.
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

    # Per Codex C7: parameterize threshold from validated source summaries
    # rather than hardcoding 0.5. Lineage parity check below ensures all
    # sources agree on phase1_success_threshold value.
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

    # Verify lineage parity across source summaries (guard against drift).
    # Per Codex C5: include current_git_sha in lineage parity check.
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

    # Total elapsed: sum
    total_elapsed = sum(s["total_elapsed_seconds"] for s in src_summaries)
    total_cand = sum(s["total_candidates"] for s in src_summaries)
    mean_elapsed = total_elapsed / total_cand if total_cand else 0.0

    # Run timestamps: earliest start + latest finish
    starts = [s["run_started_utc"] for s in src_summaries]
    finishes = [s["run_finished_utc"] for s in src_summaries]
    started_utc = min(starts)
    finished_utc = max(finishes)

    # Per Codex C7: derive binary success from validated threshold field,
    # not from hardcoded count_gt_0_5 dict key.
    binary_met = sharpe_dist["count_above_phase1_threshold"] > 0

    synthetic_summary = {
        "batch_id": SYNTHETIC_BATCH_ID,
        "synthetic_source_batch_ids": SOURCE_BATCH_IDS,
        "synthetic_assembled_utc": (
            datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
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
    print(f"[mb-b setup] Wrote synthesized summary to {synthetic_summary_path}")

    # --- Step 3: Symlink raw_payloads attempt files with renumbered positions ---
    # Note: only attempt_NNNN_response.txt files needed (eval gate uses these).
    # Prompts are not consumed by eval gate; skip to keep synthetic dir minimal.
    #
    # Per Codex C1: symlink CSV-backed positions ONLY. Smoke happened to be
    # 50/50 aligned (every CSV row had a corresponding attempt file at the
    # same source position). Main-fire and any future cycle should not inherit
    # this alignment assumption — eval gate resolves attempt files by
    # synthetic position which must map 1:1 to CSV row positions.
    #
    # Per Codex C2: use relative symlinks for portability across repo
    # archive/move; use full batch IDs at source_stage2d_summary file names
    # to avoid 8-char prefix collisions.
    for src_batch_id in SOURCE_BATCH_IDS:
        src_raw_dir = RAW_PAYLOADS_ROOT / f"batch_{src_batch_id}"
        if not src_raw_dir.exists():
            raise FileNotFoundError(
                f"Source raw_payloads dir missing: {src_raw_dir}"
            )

        # Build map: original_position → src attempt-response file
        response_by_position: dict[int, Path] = {}
        for src_file in src_raw_dir.glob("attempt_*_response.txt"):
            filename = src_file.name  # "attempt_NNNN_response.txt"
            try:
                orig_position = int(filename.split("_")[1])
            except (ValueError, IndexError):
                # Skip malformed filenames silently; proceed with usable ones
                continue
            response_by_position[orig_position] = src_file

        # CSV-backed positions for this source (post-renumbering at Step 1)
        new_positions_for_src = src_csv_positions[src_batch_id]
        # Source-frame positions: subtract source's offset from new positions
        # to get original positions in source dir's frame
        src_offset = new_positions_for_src[0] - 1  # offset = first_new_pos - 1
        original_positions = [p - src_offset for p in new_positions_for_src]

        # Verify every CSV-backed position has a corresponding attempt file
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
            # Per Codex C2: relative symlink for portability
            rel_target = os.path.relpath(src_file, start=synthetic_raw_dir)
            symlink_path.symlink_to(rel_target)
            n_linked += 1

        # Also symlink stage2d_summary.json from each source for forensic
        # traceability at the synthetic raw_payloads register.
        # Per Codex C2: use full batch ID (not 8-char prefix) at link name.
        src_stage2d = src_raw_dir / "stage2d_summary.json"
        if src_stage2d.exists():
            link_name = f"source_stage2d_summary_{src_batch_id}.json"
            symlink_path = synthetic_raw_dir / link_name
            rel_target = os.path.relpath(src_stage2d, start=synthetic_raw_dir)
            symlink_path.symlink_to(rel_target)

        print(
            f"[mb-b setup] Symlinked {n_linked} CSV-backed response files "
            f"from batch_{src_batch_id[:8]}... → new positions "
            f"{new_positions_for_src[0]}-{new_positions_for_src[-1]}"
        )

    # --- Step 4: Forensic verification ---
    # Per Codex C6: data/audit assertions promoted to explicit
    # ValueError/RuntimeError with offending values to survive python -O.
    # Internal sanity asserts (e.g., row batch_id check at concat loop)
    # remain as asserts where they guard internal data-integrity invariants
    # already validated at insertion site.
    # Per Codex C1/C4: forensic checks parameterized over actual K
    # (len(SOURCE_BATCH_IDS)) and actual total row count; not hardcoded to
    # K=2 N=50.
    print()
    print("[mb-b setup] === FORENSIC VERIFICATION ===")
    expected_total = position_offset  # total rows after concat loop

    # Verify CSV row count
    with open(synthetic_csv) as f:
        synth_rows = list(csv.DictReader(f))
    if len(synth_rows) != expected_total:
        raise RuntimeError(
            f"CSV row count drift: synthetic CSV has {len(synth_rows)} rows; "
            f"expected {expected_total} (sum of source CSV row counts)."
        )
    print(f"  CSV row count: {len(synth_rows)} ✓")

    # Verify position contiguity 1..N
    positions = sorted(int(r["position"]) for r in synth_rows)
    expected_positions = list(range(1, expected_total + 1))
    if positions != expected_positions:
        raise RuntimeError(
            f"Position contiguity violated: synthetic CSV positions "
            f"first={positions[:5]}, last={positions[-5:]}; expected "
            f"contiguous 1..{expected_total}."
        )
    print(f"  Position contiguity 1-{expected_total}: ✓")

    # Verify batch_id preservation per source (K-agnostic)
    per_source_counts: dict[str, int] = {b: 0 for b in SOURCE_BATCH_IDS}
    for r in synth_rows:
        if r["batch_id"] in per_source_counts:
            per_source_counts[r["batch_id"]] += 1
    expected_per_source = {
        b: len(src_csv_positions[b]) for b in SOURCE_BATCH_IDS
    }
    if per_source_counts != expected_per_source:
        raise RuntimeError(
            f"batch_id preservation violated: synthetic CSV per-source "
            f"counts={per_source_counts}; expected={expected_per_source}."
        )
    print(
        f"  Original batch_id preserved per row: "
        f"{per_source_counts} ✓"
    )

    # Verify symlink resolution: ALL CSV-backed positions resolve, not just
    # spot-check sample (per Codex C1 — exhaustive verification catches
    # subtle drift the spot-check would miss).
    broken_links: list[tuple[int, str]] = []  # (position, reason)
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
        f"  Symlink resolution: {len(expected_positions)}/{len(expected_positions)} "
        f"CSV-backed positions resolve ✓"
    )

    # Verify total symlink count == expected (no extra/missing files)
    response_links = list(synthetic_raw_dir.glob("attempt_*_response.txt"))
    if len(response_links) != expected_total:
        raise RuntimeError(
            f"Symlink count drift: found {len(response_links)} response "
            f"symlinks at {synthetic_raw_dir}; expected {expected_total} "
            f"(one per CSV-backed position)."
        )
    print(f"  Symlink count: {len(response_links)} response files ✓")

    # Verify summary JSON parseable + key fields (K-agnostic on counts)
    with open(synthetic_summary_path) as f:
        synth_sum = json.load(f)
    summary_checks = [
        ("total_candidates", synth_sum.get("total_candidates"), expected_total),
        ("batch_id", synth_sum.get("batch_id"), SYNTHETIC_BATCH_ID),
        ("lineage_check", synth_sum.get("lineage_check"), "passed"),
        ("wf_semantics", synth_sum.get("wf_semantics"), "corrected_test_boundary_v1"),
    ]
    for field, actual, expected in summary_checks:
        if actual != expected:
            raise RuntimeError(
                f"Synthetic summary {field!r} drift: actual={actual!r}; "
                f"expected={expected!r}."
            )
    # compile_ok/runtime_ok counts may be < total if any source had failures;
    # validate they sum to source totals at register-precision.
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
    print("[mb-b setup] All forensic checks PASSED")
    print(f"[mb-b setup] Synthetic batch ready at:")
    print(f"  WF: {synthetic_wf_dir}")
    print(f"  raw_payloads: {synthetic_raw_dir}")
    print()
    print("[mb-b setup] Eval gate can now fire with:")
    print(f"  --source-batch-id {SYNTHETIC_BATCH_ID}")
    print(f"  --universe audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
