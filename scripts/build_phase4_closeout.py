"""Phase 4 closeout assembly script.

Reads 4 cost-run artifacts (07/13/15/17 bps), re-derives per-stratum
forward-Sharpe positivity counts from `holdout_results.csv` (the
authoritative source — STOP-surface prose is NOT authoritative per
ChatGPT lock 1 at Task 5 entry brief), applies one-sided binomial test
at strict thresholds at 15bps ONLY, and writes a closeout MD applying
PHASE4_PLAN §1.5 interpretation guard mechanically (4 cases).

Per PHASE4_PLAN §1.5:
- H_0: fraction of candidates with positive forward Sharpe = 0.5
- H_a: fraction > 0.5
- One-sided binomial; Bonferroni-adjusted α=0.025/stratum (family-wise α=0.05)
- Strict thresholds (verified against scipy.stats.binom.sf via
  tests/test_phase4_closeout.py sanity-check):
    Stratum A (calendar_effect, n=22): ≥17/22 (achieved α=0.0085)
    Stratum B (non-calendar, n=17):    ≥13/17 (achieved α=0.0245)
- Phase 4 success iff at least one stratum rejects H_0 at 15bps.

Per PHASE4_PLAN §1.4 dual-report:
- 15bps: realistic base, success-criterion basis
- 7bps:  PHASE2C_15-comparability dual-report (descriptive only)
- 13/17bps: sensitivity bands (descriptive only)

Stratum membership is sourced from the sealed cohort_a reference CSV
at data/phase4_scoping/cohort_a_candidate_reference.csv (sealed at
PHASE4_PLAN §1.3 register, commit 11b39f2). Do NOT re-classify from
any other source per Mac Mini Task 5 brief.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

from scipy.stats import binom

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REFERENCE_CSV = (
    PROJECT_ROOT / "data" / "phase4_scoping"
    / "cohort_a_candidate_reference.csv"
)
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "phase2c_evaluation_gate"
DEFAULT_CLOSEOUT_PATH = (
    PROJECT_ROOT / "docs" / "closeout" / "PHASE4_RESULTS.md"
)

# ---------------------------------------------------------------------------
# Constants — PHASE4_PLAN §1.4 + §1.5 anchors (verified by self-tests)
# ---------------------------------------------------------------------------

CALENDAR_THEME = "calendar_effect"

# §1.5 binomial thresholds — hard-coded per PLAN; sanity-checked at
# test register against scipy.stats.binom.sf to lock the arithmetic
# identity that justifies them.
ALPHA_PER_STRATUM = 0.025  # Bonferroni-adjusted; family-wise α=0.05
STRATUM_A_N = 22
STRATUM_A_THRESHOLD = 17
STRATUM_B_N = 17
STRATUM_B_THRESHOLD = 13

# §1.4 dual-report cost bands; success criterion at 15bps only.
COST_BPS_LIST: tuple[int, ...] = (7, 13, 15, 17)
SUCCESS_CRITERION_COST_BPS = 15


# ---------------------------------------------------------------------------
# Stratum classification + membership loading
# ---------------------------------------------------------------------------


def classify_stratum(theme: str) -> str:
    """calendar_effect → 'A'; everything else → 'B' (PHASE4_PLAN §1.3)."""
    return "A" if theme == CALENDAR_THEME else "B"


def load_cohort_a_membership(reference_csv: Path) -> dict[str, str]:
    """Return {hypothesis_hash: 'A'|'B'} from the sealed reference CSV.

    The reference CSV is the canonical PHASE4_PLAN §1.3 stratification
    source (sealed at commit 11b39f2). Do NOT re-classify from
    walk_forward_results.csv or any other source.
    """
    membership: dict[str, str] = {}
    with reference_csv.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            membership[row["hypothesis_hash"]] = classify_stratum(row["theme"])
    return membership


# ---------------------------------------------------------------------------
# Count derivation (forward-Sharpe positivity per stratum)
# ---------------------------------------------------------------------------


def derive_counts_per_stratum(
    csv_path: Path, membership: dict[str, str]
) -> dict[str, dict[str, int]]:
    """Read holdout_results.csv; count per-stratum positive forward Sharpe.

    Per PLAN §1.5 H_a operationalization: a candidate is "positive" iff
    its forward Sharpe is strictly > 0. Non-finite (NaN, inf), missing,
    unparseable, zero, or negative values are all classified as
    non-positive. Stratum denominators are locked at PLAN §1.3 (n_A=22,
    n_B=17); unusable forward-Sharpe data does NOT reduce the
    denominator (preserves the locked n; the count is total cohort_a
    members in stratum, not total candidates with usable data).

    Counting rules:
      - Total per stratum: every row whose hypothesis_hash is in
        membership (rows for hashes NOT in membership are skipped —
        defensive against stray rows; in practice the runner produces
        exactly the cohort_a 39 rows so the skip path is never taken).
      - Positive per stratum: rows where holdout_sharpe parses as a
        finite float > 0.

    Returns {"A": {"positive": int, "total": int},
             "B": {"positive": int, "total": int}}.
    """
    counts: dict[str, dict[str, int]] = {
        "A": {"positive": 0, "total": 0},
        "B": {"positive": 0, "total": 0},
    }
    with csv_path.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            h = row.get("hypothesis_hash") or ""
            stratum = membership.get(h)
            if stratum is None:
                continue
            counts[stratum]["total"] += 1
            sharpe_str = (row.get("holdout_sharpe") or "").strip()
            if sharpe_str == "":
                continue
            try:
                v = float(sharpe_str)
            except ValueError:
                continue
            if not math.isfinite(v):
                continue
            if v > 0:
                counts[stratum]["positive"] += 1
    return counts


# ---------------------------------------------------------------------------
# Binomial test
# ---------------------------------------------------------------------------


def evaluate_stratum(
    *, k: int, n: int, threshold: int
) -> dict[str, Any]:
    """One-sided binomial test against H_0: p = 0.5.

    Returns dict with k, n, threshold, p_value, passed (bool).
    p_value = P[X ≥ k | n, p=0.5] = scipy.stats.binom.sf(k-1, n, 0.5).
    passed = (k >= threshold). Equivalent to (p_value ≤ ALPHA_PER_STRATUM)
    by construction of the threshold (verified at test register).
    """
    p_value = float(binom.sf(k - 1, n, 0.5))
    return {
        "k": k,
        "n": n,
        "threshold": threshold,
        "p_value": p_value,
        "passed": k >= threshold,
    }


# ---------------------------------------------------------------------------
# Interpretation guard — PHASE4_PLAN §1.5 verbatim wording (4 cases)
# ---------------------------------------------------------------------------


def build_interpretation_guard(*, a_pass: bool, b_pass: bool) -> str:
    """Return the pre-registered PHASE4_PLAN §1.5 claim wording verbatim.

    Returns the verbatim claim text only — no structural prefix, no
    framing elaboration. Structural labeling happens at the consumer
    (markdown section header / sentence prefix) per Mac Mini Task 5
    PATCH 2 adjudication: function is the mechanical verbatim surface;
    the closeout MD provides reading context.

    4 cases (3 verbatim from PLAN §1.5 + 1 implicit-4th-case from the
    Mac Mini Task 5 entry brief):
      A only: "calendar-effect candidates show forward persistence;
               non-calendar candidates do not."
      B only: "non-calendar candidates show forward persistence;
               calendar-effect candidates do not."
      Both:   "two independent stratum-level persistence results,
               NOT a strengthened cohort-level claim."
      Neither: "no forward persistence detected at PLAN §1.5 success
                criterion."
    """
    if a_pass and b_pass:
        return (
            "two independent stratum-level persistence results, "
            "NOT a strengthened cohort-level claim."
        )
    if a_pass and not b_pass:
        return (
            "calendar-effect candidates show forward persistence; "
            "non-calendar candidates do not."
        )
    if b_pass and not a_pass:
        return (
            "non-calendar candidates show forward persistence; "
            "calendar-effect candidates do not."
        )
    return "no forward persistence detected at PLAN §1.5 success criterion."


# ---------------------------------------------------------------------------
# Per-cost block assembly
# ---------------------------------------------------------------------------


def _read_summary(run_dir: Path) -> dict[str, Any]:
    with (run_dir / "holdout_summary.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def build_per_cost_block(
    output_root: Path, membership: dict[str, str]
) -> dict[int, dict[str, Any]]:
    """For each cost in COST_BPS_LIST, derive per-stratum counts +
    capture summary metadata."""
    out: dict[int, dict[str, Any]] = {}
    for bps in COST_BPS_LIST:
        run_dir = output_root / f"phase4_forward_2026_{bps:02d}bps_v1"
        csv_path = run_dir / "holdout_results.csv"
        summary = _read_summary(run_dir)
        counts = derive_counts_per_stratum(csv_path, membership)
        out[bps] = {
            "run_id": summary["run_id"],
            "counts": counts,
            "summary": summary,
        }
    return out


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_closeout_md(
    *,
    per_cost: dict[int, dict[str, Any]],
    head_sha: str,
) -> str:
    fifteen = per_cost[SUCCESS_CRITERION_COST_BPS]
    a_eval = evaluate_stratum(
        k=fifteen["counts"]["A"]["positive"],
        n=fifteen["counts"]["A"]["total"],
        threshold=STRATUM_A_THRESHOLD,
    )
    b_eval = evaluate_stratum(
        k=fifteen["counts"]["B"]["positive"],
        n=fifteen["counts"]["B"]["total"],
        threshold=STRATUM_B_THRESHOLD,
    )
    guard = build_interpretation_guard(
        a_pass=a_eval["passed"], b_pass=b_eval["passed"]
    )
    fwm = fifteen["summary"]["forward_window_metadata"]

    lines: list[str] = []
    lines.append("# PHASE 4 — Forward Persistence Test Results")
    lines.append("")
    lines.append(
        "**Status:** WORKING DRAFT (pending SEAL authorization at Charlie register)"
    )
    lines.append("")
    lines.append("**Cycle scope:** forward persistence test of PHASE2C_15 cohort_a candidates over 2026-01-01 forward window per PHASE4_PLAN §1.1-§1.5. Re-derives per-stratum forward-Sharpe positivity counts from the 4 cost-run artifacts (07/13/15/17 bps) and applies the pre-registered §1.5 binomial test at 15bps to the success-criterion register.")
    lines.append("")
    lines.append("## §1 Phase 4 result")
    lines.append("")
    lines.append(
        "Per PHASE4_PLAN §1.5 interpretation guard, applied mechanically to the observed disjunction at 15bps:"
    )
    lines.append("")
    lines.append(f"> {guard}")
    lines.append("")
    lines.append("## §2 Success-criterion register at 15bps (PHASE4_PLAN §1.5 basis)")
    lines.append("")
    a_status = "**REJECT H_0**" if a_eval["passed"] else "**FAIL TO REJECT H_0**"
    b_status = "**REJECT H_0**" if b_eval["passed"] else "**FAIL TO REJECT H_0**"
    lines.append(
        f"- Stratum A (calendar_effect): {a_eval['k']}/{a_eval['n']} positive "
        f"forward Sharpe at 15bps; threshold ≥{STRATUM_A_THRESHOLD}/{STRATUM_A_N}; "
        f"binomial p={a_eval['p_value']:.4f} (one-sided vs p₀=0.5); {a_status}."
    )
    lines.append(
        f"- Stratum B (non-calendar): {b_eval['k']}/{b_eval['n']} positive "
        f"forward Sharpe at 15bps; threshold ≥{STRATUM_B_THRESHOLD}/{STRATUM_B_N}; "
        f"binomial p={b_eval['p_value']:.4f} (one-sided vs p₀=0.5); {b_status}."
    )
    lines.append(
        f"- Bonferroni-adjusted α={ALPHA_PER_STRATUM} per stratum; family-wise α≈0.033 "
        f"(conservative under nominal 0.05 due to binomial discreteness)."
    )
    lines.append("")
    lines.append("## §3 Per-cost dual-report (descriptive supplement per PHASE4_PLAN §1.4)")
    lines.append("")
    lines.append(
        "Per PHASE4_PLAN §1.5, the success criterion is evaluated at 15bps only. The 7/13/17bps "
        "registers are descriptive supplements: 7bps for PHASE2C_15-comparability (research-time "
        "cost basis), 13/17bps for sensitivity bands ±2bps around the 15bps base. These rows do "
        "NOT enter the §1 success/failure determination."
    )
    lines.append("")
    lines.append("| Cost | Stratum A positive | Stratum B positive | Note |")
    lines.append("|---|---|---|---|")
    for bps in COST_BPS_LIST:
        c = per_cost[bps]["counts"]
        marker = "**success-criterion basis**" if bps == SUCCESS_CRITERION_COST_BPS else "descriptive"
        lines.append(
            f"| {bps:02d}bps | {c['A']['positive']}/{c['A']['total']} | "
            f"{c['B']['positive']}/{c['B']['total']} | {marker} |"
        )
    lines.append("")
    lines.append(
        "The 7bps threshold hit (Stratum A 17/22 at the research-time cost basis) is "
        "descriptive only and cannot be used to satisfy, weaken, rescue, or "
        "reinterpret the Phase 4 success criterion, which is evaluated only at "
        "the realistic 15bps basis per PLAN §1.4 + §1.5."
    )
    lines.append("")
    lines.append("## §4 Locked anchors")
    lines.append("")
    lines.append(f"- Forward window: `{fwm['forward_window_start_utc']}` → `{fwm['forward_window_end_utc']}`")
    lines.append(f"- Forward bar count: {fwm['forward_bar_count']}")
    lines.append(f"- Parquet sha256 (cross-artifact-invariant across all 4 fires): `{fwm['parquet_data_sha256']}`")
    lines.append(f"- Engine lineage: `{fifteen['summary']['engine_commit']}` (`{fifteen['summary']['engine_corrected_lineage']}`)")
    lines.append(f"- HEAD at closeout authoring: `{head_sha}`")
    lines.append(
        f"- Cohort_a stratification (sealed at PHASE4_PLAN §1.3 register; "
        f"reference CSV at `data/phase4_scoping/cohort_a_candidate_reference.csv` "
        f"committed at `11b39f2`): A={STRATUM_A_N} (calendar_effect), B={STRATUM_B_N} (non-calendar)."
    )
    lines.append(
        f"- Per-stratum-cost-fire artifacts share identical parquet sha256, identical forward "
        f"window, identical bar count; only `execution_config_*` differs across fires "
        f"(verified at production fire register-event boundary cross-artifact consistency check)."
    )
    lines.append(
        f"- Stratum denominators locked at PLAN §1.3 (n_A={STRATUM_A_N}, n_B={STRATUM_B_N}); "
        f"candidates with non-finite, missing, zero, or negative forward Sharpe are classified "
        f"as non-positive and remain in the denominator (the locked n is total cohort_a members "
        f"in stratum, not total candidates with usable Sharpe data)."
    )
    lines.append("")
    lines.append("## §5 Run artifacts")
    lines.append("")
    for bps in COST_BPS_LIST:
        run_id = per_cost[bps]["run_id"]
        lines.append(
            f"- {bps:02d}bps: [data/phase2c_evaluation_gate/{run_id}/](../../data/phase2c_evaluation_gate/{run_id}/)"
        )
    lines.append("")
    lines.append("Each contains `holdout_summary.json` (aggregate + lineage + forward_window_metadata + execution_config sha256) and `holdout_results.csv` (39 rows; one per cohort_a candidate). The 4 fires were verified end-to-end via [scripts/verify_phase4_smoke.py](../../scripts/verify_phase4_smoke.py) at fire register; 9/9 assertions PASS at every fire.")
    lines.append("")
    lines.append("## §6 Carry-forwards (forward-only log; finalize at successor methodology consolidation cycle)")
    lines.append("")
    lines.append(
        "- §31 P1 (convergence-reinforces-convergent-errors pattern): 5 instances cumulative across "
        "PHASE4 implementation arc. #1: ≥17/22 PLAN threshold convergence; #2: `holdout_sharpe` "
        "field-name convergence; #3: `end:null` engine consumer crash (structural-assumption); #4: "
        "`verify_phase4_smoke.py committed in 7dd3b7a` overclaim (commit-contents); #5: `--universe audit` "
        "returns 39 vs actually 993 (structural-assumption ×2). Sub-class accumulation through #5: "
        "1 numerical / 1 identifier / 2 structural-assumption / 1 commit-contents. Task 7 reassessment "
        "candidate (NOT pre-committed at this register per anti-pre-naming discipline; reassessment "
        "at successor cycle adjudication boundary). Logged forward-only at carry-forward register."
    )
    lines.append(
        "- Six-dimension machine-residency discipline empirically validated at MacBook ↔ Mac Mini "
        "transition: (1) `raw_payloads/` directory state, (2) HTTPS credential availability, (3) test "
        "fixture artifact state, (4) Python environment composition, (5) parquet sha256 anchor state, "
        "(6) geo-restriction fingerprint. Forward arc planning should pre-check all six at session "
        "entry rather than mid-sequence-resolve."
    )
    lines.append(
        "- Pre-registered §1.5 wording authored at PLAN drafting cycle held under closeout pressure. "
        "Trim-direction discipline at PLAN drafting was substantively expensive at the time but "
        "produced clean closeout wording at the register-event boundary where it bound."
    )
    lines.append("")
    lines.append("## §7 Anti-pre-naming preserved")
    lines.append("")
    lines.append(
        "Phase 5+ trajectory NOT pre-committed at this register. Successor scoping is its own "
        "register-event boundary per anti-pre-naming. Task 7 §32 codification reassessment: "
        "default = NO codification per asymmetric framing; reassess at fresh-cycle boundary "
        "post-this-SEAL."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _resolve_head_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(PROJECT_ROOT)
        ).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "(unknown)"


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Build PHASE4_RESULTS.md closeout from 4 cost-run artifacts "
            "(07/13/15/17 bps). Re-derives counts from holdout_results.csv "
            "(authoritative); applies §1.5 binomial test at 15bps; renders "
            "interpretation guard mechanically."
        ),
    )
    p.add_argument(
        "--reference-csv",
        type=Path,
        default=DEFAULT_REFERENCE_CSV,
        help=(
            f"Sealed cohort_a stratification source "
            f"(default: {DEFAULT_REFERENCE_CSV.relative_to(PROJECT_ROOT)})"
        ),
    )
    p.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=(
            "Directory containing phase4_forward_2026_*bps_v1 subdirs "
            f"(default: {DEFAULT_OUTPUT_ROOT.relative_to(PROJECT_ROOT)})"
        ),
    )
    p.add_argument(
        "--output-md",
        type=Path,
        default=DEFAULT_CLOSEOUT_PATH,
        help=(
            f"Closeout MD output path "
            f"(default: {DEFAULT_CLOSEOUT_PATH.relative_to(PROJECT_ROOT)})"
        ),
    )
    p.add_argument(
        "--head-sha",
        type=str,
        default=None,
        help="Override git HEAD SHA (auto-detected if omitted)",
    )
    p.add_argument(
        "--print",
        action="store_true",
        help="Print rendered MD to stdout instead of writing to --output-md",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    head_sha = args.head_sha or _resolve_head_sha()

    membership = load_cohort_a_membership(args.reference_csv)
    per_cost = build_per_cost_block(args.output_root, membership)
    md = render_closeout_md(per_cost=per_cost, head_sha=head_sha)

    if args.print:
        print(md)
        return 0

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(md, encoding="utf-8")
    print(
        f"[build_phase4_closeout] Wrote {args.output_md} "
        f"({len(md)} bytes)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
