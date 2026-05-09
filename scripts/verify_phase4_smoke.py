"""Phase 4 smoke-fire artifact verifier.

Asserts 9 conditions on a Phase 4 evaluation gate run output to confirm
the artifact is structurally complete + lineage-consistent + cost-config-
referenced + forward-window-self-auditing.

Used at the §4 Step 6 smoke verification register (1 run) and the §6
production verification register (4 runs at 07/13/15/17 bps). The same
9 assertions apply at both registers; --candidate-count distinguishes
smoke (1) from production (39).

Re-authored at Mac Mini session 2026-05-09 per Charlie register
authorization (the Phase 4 implementation arc commit `7dd3b7a` was
overclaimed in the Mac Mini session entry brief as containing this
script; descriptive `git show 7dd3b7a --stat` revealed it did not —
§31 P1 instance #4 carry-forward observation logged forward-only).

Usage (CLI):
    python scripts/verify_phase4_smoke.py <run_id> --cost-bps 15

Usage (Python):
    from verify_phase4_smoke import verify, VerificationFailure
    try:
        verify("phase4_smoke_15bps_v0", cost_bps=15)
    except VerificationFailure as exc:
        ...

Exits 0 on success (prints PASS lines per assertion + final summary line).
Exits 1 on any assertion failure (prints FAIL message to stderr).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "phase2c_evaluation_gate"
DEFAULT_PARQUET = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"

ALLOWED_COST_BPS = (7, 13, 15, 17)

EXPECTED_REGIME_KEY = "evaluation_regimes.forward_2026"
EXPECTED_REGIME_LABEL = "forward_2026"
EXPECTED_EVALUATION_SEMANTICS = "single_run_holdout_v1"
EXPECTED_ARTIFACT_SCHEMA_VERSION = "phase2c_7_1"
EXPECTED_FORWARD_WINDOW_START_UTC = "2026-01-01T00:00:00Z"

# ISO 8601 UTC: YYYY-MM-DDTHH:MM:SS[.fff]Z (no offsets — must end in Z)
_ISO_UTC_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)
_HEX64_PATTERN = re.compile(r"^[0-9a-f]{64}$")

# Lifecycle states for which an empty holdout_sharpe column is permitted.
# holdout_error: pipeline raised; per-candidate metrics block absent.
# holdout_failed: included per Mac Mini session brief §4 Step 6 spec
# (conservative — empty in practice arises only on holdout_error path,
# but the brief grants both).
_LIFECYCLE_PERMITTING_NULL_SHARPE = frozenset(
    {"holdout_failed", "holdout_error"}
)


class VerificationFailure(AssertionError):
    """Raised by verify() when any of the 9 assertions fails.

    Subclasses AssertionError so callers using either
    pytest.raises(AssertionError) or pytest.raises(VerificationFailure)
    work without coupling.
    """


def _fail(condition_index: int, condition_name: str, msg: str) -> None:
    raise VerificationFailure(
        f"[FAIL #{condition_index}] {condition_name}: {msg}"
    )


def _say_pass(condition_index: int, condition_name: str, msg: str = "") -> None:
    suffix = f" — {msg}" if msg else ""
    print(f"[PASS #{condition_index}] {condition_name}{suffix}")


def verify(
    run_id: str,
    *,
    cost_bps: int,
    expected_candidate_count: int = 1,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    parquet_path: Path = DEFAULT_PARQUET,
) -> None:
    """Run all 9 assertions on the artifact at output_root / run_id.

    Args:
        run_id: subdir name under output_root.
        cost_bps: expected per-side cost in bps (7, 13, 15, or 17);
            verifier compares the artifact's execution_config_path +
            sha256 against the corresponding execution_phase4_<XX>bps.yaml.
        expected_candidate_count: rows expected in holdout_results.csv
            (1 for smoke; 39 for the canonical Phase 4 production
            cohort_a).
        output_root: directory containing run subdirs (default:
            data/phase2c_evaluation_gate).
        parquet_path: canonical input parquet whose sha256 must match
            the artifact's forward_window_metadata.parquet_data_sha256.

    Raises:
        VerificationFailure: on any of the 9 assertion failures.
        ValueError: on cost_bps outside the allowed set (defensive).
    """
    if cost_bps not in ALLOWED_COST_BPS:
        raise ValueError(
            f"cost_bps={cost_bps} not in {ALLOWED_COST_BPS}"
        )

    run_dir = output_root / run_id
    summary_path = run_dir / "holdout_summary.json"
    csv_path = run_dir / "holdout_results.csv"

    # Assertion 1 — both files present
    if not summary_path.exists():
        _fail(1, "artifacts present", f"missing {summary_path}")
    if not csv_path.exists():
        _fail(1, "artifacts present", f"missing {csv_path}")
    _say_pass(1, "artifacts present", f"summary + CSV at {run_dir}")

    with summary_path.open("r", encoding="utf-8") as f:
        summary: dict[str, Any] = json.load(f)

    # Assertion 2 — lineage anchors (4 fields)
    expected_lineage = {
        "regime_key": EXPECTED_REGIME_KEY,
        "regime_label": EXPECTED_REGIME_LABEL,
        "evaluation_semantics": EXPECTED_EVALUATION_SEMANTICS,
        "artifact_schema_version": EXPECTED_ARTIFACT_SCHEMA_VERSION,
    }
    for k, expected_v in expected_lineage.items():
        actual_v = summary.get(k)
        if actual_v != expected_v:
            _fail(
                2,
                "lineage anchors",
                f"{k}: expected {expected_v!r}, got {actual_v!r}",
            )
    _say_pass(
        2,
        "lineage anchors",
        f"regime_key={EXPECTED_REGIME_KEY}, "
        f"regime_label={EXPECTED_REGIME_LABEL}, "
        f"semantics={EXPECTED_EVALUATION_SEMANTICS}, "
        f"schema={EXPECTED_ARTIFACT_SCHEMA_VERSION}",
    )

    # Assertion 3 — execution_config_path mentions execution_phase4_<XX>bps.yaml
    expected_config_filename = f"execution_phase4_{cost_bps:02d}bps.yaml"
    actual_config_path = summary.get("execution_config_path")
    if actual_config_path is None:
        _fail(3, "execution_config_path", "field missing from summary")
    if expected_config_filename not in actual_config_path:
        _fail(
            3,
            "execution_config_path",
            f"expected substring {expected_config_filename!r}; "
            f"got {actual_config_path!r}",
        )
    _say_pass(3, "execution_config_path", actual_config_path)

    # Assertion 4 — execution_config_sha256 matches the file
    config_file = PROJECT_ROOT / "config" / expected_config_filename
    if not config_file.exists():
        _fail(
            4,
            "execution_config_sha256",
            f"config file not found: {config_file}",
        )
    expected_sha256 = hashlib.sha256(config_file.read_bytes()).hexdigest()
    actual_sha256 = summary.get("execution_config_sha256")
    if actual_sha256 != expected_sha256:
        _fail(
            4,
            "execution_config_sha256",
            f"expected {expected_sha256}, got {actual_sha256}",
        )
    _say_pass(4, "execution_config_sha256", expected_sha256[:16] + "...")

    # forward_window_metadata block must be present
    fwm = summary.get("forward_window_metadata")
    if fwm is None:
        _fail(
            5,
            "forward_window_metadata",
            "block missing from summary (Phase 4 fires must emit it)",
        )

    # Assertion 5 — forward_window_start_utc PLAN-locked
    actual_start = fwm.get("forward_window_start_utc")
    if actual_start != EXPECTED_FORWARD_WINDOW_START_UTC:
        _fail(
            5,
            "forward_window_start_utc",
            f"expected {EXPECTED_FORWARD_WINDOW_START_UTC!r}; "
            f"got {actual_start!r}",
        )
    _say_pass(5, "forward_window_start_utc", str(actual_start))

    # Assertion 6 — forward_window_end_utc parseable ISO 8601 UTC
    actual_end = fwm.get("forward_window_end_utc")
    if not isinstance(actual_end, str) or not _ISO_UTC_PATTERN.match(actual_end):
        _fail(
            6,
            "forward_window_end_utc",
            f"not a valid ISO 8601 UTC timestamp ending in Z: {actual_end!r}",
        )
    _say_pass(6, "forward_window_end_utc", str(actual_end))

    # Assertion 7 — forward_bar_count > 0
    actual_bar_count = fwm.get("forward_bar_count")
    if not isinstance(actual_bar_count, int) or isinstance(actual_bar_count, bool):
        _fail(
            7,
            "forward_bar_count",
            f"expected int; got {type(actual_bar_count).__name__}={actual_bar_count!r}",
        )
    if actual_bar_count <= 0:
        _fail(
            7,
            "forward_bar_count",
            f"expected positive int; got {actual_bar_count!r}",
        )
    _say_pass(7, "forward_bar_count", str(actual_bar_count))

    # Assertion 8 — parquet_data_sha256 is 64-char hex matching current parquet
    actual_parquet_sha = fwm.get("parquet_data_sha256")
    if not isinstance(actual_parquet_sha, str) or not _HEX64_PATTERN.match(
        actual_parquet_sha
    ):
        _fail(
            8,
            "parquet_data_sha256",
            f"not a valid 64-char hex string: {actual_parquet_sha!r}",
        )
    if not parquet_path.exists():
        _fail(
            8,
            "parquet_data_sha256",
            f"current parquet not found at {parquet_path}; cannot verify match",
        )
    expected_parquet_sha = hashlib.sha256(parquet_path.read_bytes()).hexdigest()
    if actual_parquet_sha != expected_parquet_sha:
        _fail(
            8,
            "parquet_data_sha256",
            f"artifact has {actual_parquet_sha} but current parquet "
            f"hashes to {expected_parquet_sha}; parquet was changed since "
            f"the run (cross-artifact consistency invariant violated)",
        )
    _say_pass(8, "parquet_data_sha256", actual_parquet_sha[:16] + "...")

    # Assertion 9 — CSV row count + finite holdout_sharpe per row
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if len(rows) != expected_candidate_count:
        _fail(
            9,
            "holdout_results.csv rows",
            f"expected {expected_candidate_count} row(s), got {len(rows)}",
        )

    for i, row in enumerate(rows):
        sharpe_str = (row.get("holdout_sharpe") or "").strip()
        lifecycle = (row.get("lifecycle_state") or "").strip()
        if sharpe_str == "":
            if lifecycle not in _LIFECYCLE_PERMITTING_NULL_SHARPE:
                _fail(
                    9,
                    "holdout_results.csv rows",
                    f"row {i}: holdout_sharpe empty but "
                    f"lifecycle_state={lifecycle!r} (permitted-null lifecycles: "
                    f"{sorted(_LIFECYCLE_PERMITTING_NULL_SHARPE)})",
                )
            continue
        try:
            val = float(sharpe_str)
        except ValueError:
            _fail(
                9,
                "holdout_results.csv rows",
                f"row {i}: holdout_sharpe={sharpe_str!r} not parseable as float",
            )
        if not math.isfinite(val):
            _fail(
                9,
                "holdout_results.csv rows",
                f"row {i}: holdout_sharpe={sharpe_str!r} parsed to "
                f"non-finite {val!r} (lifecycle_state={lifecycle!r})",
            )
    _say_pass(
        9,
        "holdout_results.csv rows",
        f"{len(rows)} row(s); sharpes finite or empty-with-permitted-lifecycle",
    )

    print(
        f"\n[verify_phase4_smoke] ALL 9 assertions PASS at run_dir={run_dir}"
    )


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Verify a Phase 4 evaluation gate run artifact (9 assertions: "
            "files present, lineage anchors, exec config path/sha256, "
            "forward_window_metadata block, finite holdout sharpes)."
        ),
    )
    p.add_argument("run_id", help="Run id (subdir under --output-root)")
    p.add_argument(
        "--cost-bps",
        type=int,
        choices=ALLOWED_COST_BPS,
        required=True,
        help=(
            "Expected per-side cost in bps; verifier compares against "
            "config/execution_phase4_<XX>bps.yaml file content."
        ),
    )
    p.add_argument(
        "--candidate-count",
        type=int,
        default=1,
        dest="candidate_count",
        help=(
            "Expected number of rows in holdout_results.csv "
            "(default 1 for smoke; 39 for canonical production cohort_a)."
        ),
    )
    p.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=(
            "Directory containing run subdirs "
            "(default: data/phase2c_evaluation_gate)."
        ),
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    try:
        verify(
            args.run_id,
            cost_bps=args.cost_bps,
            expected_candidate_count=args.candidate_count,
            output_root=args.output_root,
        )
    except VerificationFailure as exc:
        print(f"\n{exc}", file=sys.stderr)
        print("[verify_phase4_smoke] FAILED", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
