"""G2 StrategyDSL backward-compat validation (Phase 1 v2 per PFR R1 F1 fix).

Reads 39 cohort_a candidate hashes from holdout_results.csv → maps each via
source_stage2d_summary_*.json to its batch-specific attempt response file →
runs StrategyDSL.model_validate() at the current Pydantic schema (HEAD f112599).
Writes results to g2-dsl-backward-compat-sample.json.

All stdout logging includes ISO 8601 UTC timestamps per CLAUDE.md Coding Standards.
"""
from __future__ import annotations
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from strategies.dsl import StrategyDSL  # noqa: E402
from scripts.run_phase2c_evaluation_gate import _strip_markdown_fence  # noqa: E402


def _ts() -> str:
    """ISO 8601 UTC timestamp prefix for log lines.

    PFR R1 LOW L2 fix v2: this helper applies CLAUDE.md Coding Standards
    "All scripts log to stdout with ISO 8601 UTC timestamps" requirement.
    Used in all print() calls below.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_cohort_a_hashes() -> list[str]:
    """Read holdout_results.csv and return the 39 cohort_a hypothesis_hashes
    in CSV row order.

    PFR R1 F1 fix: cohort selection is anchored to the CSV (authoritative
    cohort_a universe per spec §1 + verified empirically: CSV has 40 lines =
    39 candidates + header).
    """
    csv_path = REPO_ROOT / "data" / "phase2c_evaluation_gate" / "phase4_forward_2026_15bps_v1" / "holdout_results.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"G2 BLOCKING: cohort_a CSV missing at {csv_path}. "
            f"Required for cohort_a enumeration per spec §1."
        )
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        if "hypothesis_hash" not in (reader.fieldnames or []):
            raise ValueError(
                f"G2 BLOCKING: holdout_results.csv missing hypothesis_hash column. "
                f"Fields: {reader.fieldnames}"
            )
        hashes = [row["hypothesis_hash"] for row in reader]
    unique = set(hashes)
    if len(unique) != 39:
        raise ValueError(
            f"G2 BLOCKING: cohort_a universe expected 39 unique hashes; "
            f"got {len(unique)} unique from {len(hashes)} rows. "
            f"Spec §1 lock requires exactly 39."
        )
    return hashes


def build_hash_to_call_index() -> dict[str, tuple[str, int]]:
    """Parse all 5 source_stage2d_summary_*.json files and build a single
    hash → (batch_id, position) index.

    PFR R1 F1 fix: this is the authoritative hash→attempt resolution layer.
    Combined-dir attempt_NNNN_response.txt symlinks use a DIFFERENT (renumbered)
    naming scheme; we resolve via batch-specific paths instead.
    """
    combined_dir = REPO_ROOT / "raw_payloads" / "batch_phase2c_15_main_fire_combined"
    summary_paths = sorted(combined_dir.glob("source_stage2d_summary_*.json"))
    if len(summary_paths) != 5:
        raise FileNotFoundError(
            f"G2 BLOCKING: expected 5 source_stage2d_summary_*.json files; "
            f"got {len(summary_paths)} at {combined_dir}."
        )
    index: dict[str, tuple[str, int]] = {}
    for s in summary_paths:
        data = json.loads(s.read_text())
        batch_id = data["batch_id"]
        for call in data.get("calls", []):
            h = call.get("hypothesis_hash")
            if h is not None:
                index[h] = (batch_id, call["position"])
    return index


def resolve_attempt_path(hsh: str, index: dict[str, tuple[str, int]]) -> Path:
    """Resolve a cohort_a hash to its batch-specific attempt response path."""
    if hsh not in index:
        raise KeyError(
            f"G2 BLOCKING: hash {hsh!r} not found in stage2d call index "
            f"(spans {len(index)} entries across 5 batches). "
            f"Possible cause: cohort_a hash absent from the issued+parsed "
            f"call set, or summary JSON has been mutated."
        )
    batch_id, position = index[hsh]
    return REPO_ROOT / "raw_payloads" / f"batch_{batch_id}" / f"attempt_{position:04d}_response.txt"


def validate_one(hsh: str, response_path: Path) -> dict:
    """Validate a single attempt response → StrategyDSL.

    Returns: {"hypothesis_hash": str, "path": str, "pass": bool, "error": str | None}.
    """
    if not response_path.exists():
        return {
            "hypothesis_hash": hsh,
            "path": str(response_path),
            "pass": False,
            "error": f"FileNotFoundError: attempt path does not exist",
        }
    raw = response_path.read_text(encoding="utf-8")
    payload_text = _strip_markdown_fence(raw)
    try:
        payload = json.loads(payload_text)
        StrategyDSL.model_validate(payload)
        return {
            "hypothesis_hash": hsh,
            "path": str(response_path),
            "pass": True,
            "error": None,
        }
    except Exception as e:
        return {
            "hypothesis_hash": hsh,
            "path": str(response_path),
            "pass": False,
            "error": f"{type(e).__name__}: {e}",
        }


def main() -> int:
    print(f"{_ts()} G2 cohort_a backward-compat validation starting")
    cohort_hashes = load_cohort_a_hashes()
    print(f"{_ts()} cohort_a universe: {len(cohort_hashes)} hashes (expected 39)")
    if len(cohort_hashes) != 39:
        print(f"{_ts()} FAIL: cohort_a size {len(cohort_hashes)} != 39", file=sys.stderr)
        return 2
    index = build_hash_to_call_index()
    print(f"{_ts()} stage2d call index built: {len(index)} entries across 5 batches")
    missing = [h for h in cohort_hashes if h not in index]
    if missing:
        print(
            f"{_ts()} FAIL: {len(missing)} cohort_a hashes not found in call index: "
            f"{missing[:5]}...",
            file=sys.stderr,
        )
        return 2

    results = [validate_one(h, resolve_attempt_path(h, index)) for h in cohort_hashes]
    n_pass = sum(1 for r in results if r["pass"])
    n_fail = len(results) - n_pass

    output_path = REPO_ROOT / "docs" / "superpowers" / "phase-1-gate-results" / "g2-dsl-backward-compat-sample.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({
        "validated_at_utc": _ts(),
        "head_commit": "b8d6523",  # current HEAD; code-state equivalent to f112599 (no code changes since Phase 0 SEAL)
        "cohort": "cohort_a (phase4_forward_2026_15bps_v1)",
        "cohort_source_csv": "data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv",
        "n_total": len(results),
        "n_pass": n_pass,
        "n_fail": n_fail,
        "pass_rate": n_pass / len(results) if results else 0.0,
        "per_attempt": results,
    }, indent=2))

    if n_fail > 0:
        print(
            f"{_ts()} G2 FAIL: {n_fail}/{len(results)} attempts failed validation. "
            f"See {output_path} for per-attempt details.",
            file=sys.stderr,
        )
        return 1

    print(f"{_ts()} G2 PASS: {n_pass}/{len(results)} attempts validate cleanly at HEAD b8d6523")
    print(f"{_ts()} Results written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
