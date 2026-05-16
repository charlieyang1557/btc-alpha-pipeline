"""Phase 5 diagnostic execution orchestrator (session-1 scope: §2.a-§2.f + §3.1 + §3.2).

Loads sealed §1 inputs, fires per-mode §2.x indicators, assembles §3.1 multi-mode
composite labels + §3.2 Case A disposition, writes structured outputs.

Sealed sub-spec at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md (sub-spec drafting
cycle SEAL at commit 49ae7e3). Sealed §4.1 hard scope binding: derived
statistics + diagnostic computations from existing sealed artifacts ARE
allowed; acquisition of new empirical data is NOT allowed.

Usage:
    python -m phase5.execute_diagnostic --dry-run
    python -m phase5.execute_diagnostic --output-dir data/phase5_diagnostic/execution_session_1_v1

Dry-run mode validates sealed input joins, candidate counts, schema
assumptions + executes §2-§3 procedures with stdout-only report; writes
no artifacts. Production mode (no --dry-run) writes JSON + markdown artifacts
to --output-dir only if dry-run pre-execution gates clean.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from phase5.io import (
    BROADER_UNIVERSE_SIZE,
    COHORT_A_SIZE,
    EXPECTED_PARQUET_SHA256,
    PHASE2C_15_REGIMES,
    SealedInputs,
    load_all_sealed_inputs,
)
from phase5.labels.ambiguity_disposition import evaluate_case_a
from phase5.labels.multi_mode_rules import assemble_multi_mode_labels
from phase5.modes.andgate_overfit import compute_andgate_overfit
from phase5.modes.cohort_weakness import compute_cohort_weakness
from phase5.modes.cost_drag import compute_cost_drag
from phase5.modes.regime_change import compute_regime_change
from phase5.modes.signal_decay import compute_signal_decay
from phase5.modes.success_metric_mismatch import compute_success_metric_mismatch


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("phase5.execute_diagnostic")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)sZ [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    handler.formatter.converter = lambda *args: datetime.now(timezone.utc).timetuple()  # type: ignore
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def verify_schema_and_counts(inputs: SealedInputs, logger: logging.Logger) -> dict[str, Any]:
    """Verify sealed §1 invariants per ChatGPT pre-execution validation gate."""
    report: dict[str, Any] = {}

    # cohort_a invariants.
    cohort_size = len(inputs.cohort_a)
    expected_cohort_cols = {
        "hypothesis_hash",
        "theme",
        "holdout_bear_2022_sharpe",
        "holdout_validation_2024_sharpe",
        "holdout_eval_2020_v1_sharpe",
        "holdout_eval_2021_v1_sharpe",
        "holdout_bear_2022_passed",
        "holdout_validation_2024_passed",
        "holdout_eval_2020_v1_passed",
        "holdout_eval_2021_v1_passed",
        "wf_test_period_sharpe",
        "factors_used",
        "batch_id",
        "filtered",
    }
    missing_cohort_cols = expected_cohort_cols - set(inputs.cohort_a.columns)
    stratum_a_size = int((inputs.cohort_a["theme"] == "calendar_effect").sum())
    stratum_b_size = int((inputs.cohort_a["theme"] != "calendar_effect").sum())
    report["cohort_a"] = {
        "size": cohort_size,
        "size_expected": COHORT_A_SIZE,
        "size_ok": cohort_size == COHORT_A_SIZE,
        "stratum_a_calendar_effect_size": stratum_a_size,
        "stratum_b_non_calendar_size": stratum_b_size,
        "stratum_a_expected": 22,
        "stratum_b_expected": 17,
        "missing_columns": sorted(missing_cohort_cols),
    }

    # Forward-test invariants.
    forward_report: dict[str, dict[str, Any]] = {}
    for bps, df in inputs.forward_per_cost_bps.items():
        forward_report[f"{bps:02d}bps"] = {
            "row_count": len(df),
            "row_count_ok": len(df) == COHORT_A_SIZE,
            "has_holdout_sharpe": "holdout_sharpe" in df.columns,
            "has_hypothesis_hash": "hypothesis_hash" in df.columns,
        }
    report["forward_test_cost_sweep"] = forward_report

    # Cross-cost-sweep hypothesis_hash invariance (sealed §1: all 4 cost-runs
    # evaluated on identical 2026 forward-test candidate set).
    hash_sets = [
        set(df["hypothesis_hash"].tolist())
        for df in inputs.forward_per_cost_bps.values()
    ]
    cross_invariance = all(s == hash_sets[0] for s in hash_sets)
    report["forward_test_cross_cost_hash_invariance"] = cross_invariance

    # cohort_a ⊆ forward-test invariance.
    cohort_hashes = set(inputs.cohort_a["hypothesis_hash"].tolist())
    cohort_in_forward = all(
        cohort_hashes == set(df["hypothesis_hash"].tolist())
        for df in inputs.forward_per_cost_bps.values()
    )
    report["cohort_a_equals_forward_test_set"] = cohort_in_forward

    # Broader-universe invariants.
    bu_report: dict[str, dict[str, Any]] = {}
    for regime, m in inputs.broader_universe_per_regime.items():
        bu_report[regime] = {
            "candidate_count": len(m),
            "count_ok": len(m) == BROADER_UNIVERSE_SIZE,
        }
    report["broader_universe"] = bu_report

    # cohort_a ⊆ broader-universe invariance.
    bu_intersection = set(inputs.broader_universe_per_regime[PHASE2C_15_REGIMES[0]].keys())
    for regime in PHASE2C_15_REGIMES:
        bu_intersection &= set(inputs.broader_universe_per_regime[regime].keys())
    cohort_in_bu = cohort_hashes.issubset(bu_intersection)
    report["cohort_a_subset_of_broader_universe_intersection"] = {
        "all_cohort_in_broader_intersection": cohort_in_bu,
        "broader_intersection_size": len(bu_intersection),
        "cohort_a_minus_intersection_count": len(cohort_hashes - bu_intersection),
    }

    # Parquet invariants (if loaded).
    if inputs.parquet_sha256:
        report["parquet"] = {
            "sha256": inputs.parquet_sha256,
            "sha256_ok": inputs.parquet_sha256 == EXPECTED_PARQUET_SHA256,
            "total_bars": int(len(inputs.btc_parquet)),
        }

    # All-green summary.
    all_ok = (
        report["cohort_a"]["size_ok"]
        and report["cohort_a"]["stratum_a_calendar_effect_size"] == 22
        and report["cohort_a"]["stratum_b_non_calendar_size"] == 17
        and not report["cohort_a"]["missing_columns"]
        and all(d["row_count_ok"] for d in forward_report.values())
        and all(d["has_holdout_sharpe"] for d in forward_report.values())
        and cross_invariance
        and cohort_in_forward
        and all(d["count_ok"] for d in bu_report.values())
        and cohort_in_bu
        and (
            (not inputs.parquet_sha256) or report["parquet"]["sha256_ok"]
        )
    )
    report["all_green"] = all_ok
    return report


def execute_indicators(inputs: SealedInputs, logger: logging.Logger) -> dict[str, Any]:
    """Fire §2.a-§2.f indicator construction in sealed enumeration order."""
    results: dict[str, Any] = {}

    logger.info("§2.a signal decay — firing Wilcoxon paired Δ (α=0.05 one-sided less)")
    results["signal_decay"] = compute_signal_decay(
        inputs.cohort_a, inputs.forward_per_cost_bps[7]
    )
    logger.info(
        f"  §2.a detected={results['signal_decay']['detected']} "
        f"p={results['signal_decay']['p_value']}"
    )

    logger.info("§2.b cost drag — firing per-candidate Spearman ρ + cohort Wilcoxon")
    results["cost_drag"] = compute_cost_drag(
        inputs.cohort_a, inputs.forward_per_cost_bps
    )
    logger.info(
        f"  §2.b detected={results['cost_drag']['detected']} "
        f"p={results['cost_drag']['p_value']}"
    )

    logger.info("§2.c cohort weakness — firing 75th/90th percentile-rank AND-conditions")
    results["cohort_weakness"] = compute_cohort_weakness(
        inputs.cohort_a, inputs.broader_universe_per_regime
    )
    logger.info(
        f"  §2.c detected={results['cohort_weakness']['detected']} "
        f"C1={results['cohort_weakness'].get('condition_1_median_lt_075')} "
        f"C2={results['cohort_weakness'].get('condition_2_p75_lt_090')}"
    )

    logger.info(
        "§2.d AND-gate overfit — firing canonical-fresh ≡ pre-computed-audit "
        "gate, then TOST + Approach A Jaccard"
    )
    results["andgate_overfit"] = compute_andgate_overfit(
        inputs.cohort_a, inputs.broader_universe_per_regime
    )
    logger.info(
        f"  §2.d detected={results['andgate_overfit']['detected']} "
        f"suspended={results['andgate_overfit'].get('execution_suspended')}"
    )

    logger.info("§2.e success-metric mismatch — firing Wilcoxon per stratum (Bonferroni α=0.025)")
    results["success_metric_mismatch"] = compute_success_metric_mismatch(
        inputs.cohort_a,
        inputs.forward_per_cost_bps[15],
        inputs.forward_per_cost_bps[7],
    )
    logger.info(
        f"  §2.e detected={results['success_metric_mismatch']['detected']}"
    )

    logger.info("§2.f regime change — firing quantile band on 17 reference blocks vs forward block")
    results["regime_change"] = compute_regime_change(inputs.btc_parquet)
    logger.info(
        f"  §2.f detected={results['regime_change']['detected']} "
        f"suspended={results['regime_change'].get('execution_suspended')}"
    )

    return results


def extract_detections_and_states(
    mode_results: dict[str, Any],
) -> tuple[dict[str, bool | None], list[str], list[str]]:
    """Extract canonical (detected | not-detected | NaN | suspended) state per mode."""
    detections: dict[str, bool | None] = {}
    nan_modes: list[str] = []
    suspended_modes: list[str] = []
    for mode_key, r in mode_results.items():
        if r.get("execution_suspended"):
            suspended_modes.append(mode_key)
            detections[mode_key] = None
            continue
        d = r.get("detected")
        if d is None:
            nan_modes.append(mode_key)
            detections[mode_key] = None
        else:
            detections[mode_key] = bool(d)
    return detections, nan_modes, suspended_modes


def _json_safe(obj: Any) -> Any:
    """Recursive conversion to JSON-serializable form."""
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, np.ndarray):
        return [_json_safe(v) for v in obj.tolist()]
    return obj


def write_outputs(
    output_dir: Path,
    mode_results: dict[str, Any],
    multi_mode: dict[str, Any],
    ambiguity: dict[str, Any],
    schema_report: dict[str, Any],
    logger: logging.Logger,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    indicator_path = output_dir / "indicator_outputs.json"
    multi_mode_path = output_dir / "multi_mode_labels.json"
    ambiguity_path = output_dir / "ambiguity_disposition.json"
    summary_path = output_dir / "execution_summary.md"

    payload_indicator = {
        "schema_version": 1,
        "generated_at_utc": _now_iso_utc(),
        "sealed_subspec_commit": "49ae7e3",
        "session": "phase_5_diagnostic_execution_session_1",
        "schema_verification": schema_report,
        "mode_results": mode_results,
    }
    indicator_path.write_text(json.dumps(_json_safe(payload_indicator), indent=2))

    multi_mode_payload = {
        "schema_version": 1,
        "generated_at_utc": _now_iso_utc(),
        "sealed_subspec_commit": "49ae7e3",
        "register": "§3.1 multi-mode coexistence rule-tree labels",
        "multi_mode_labels": multi_mode,
    }
    multi_mode_path.write_text(json.dumps(_json_safe(multi_mode_payload), indent=2))

    ambiguity_payload = {
        "schema_version": 1,
        "generated_at_utc": _now_iso_utc(),
        "sealed_subspec_commit": "49ae7e3",
        "register": "§3.2 diagnostic ambiguity disposition",
        "case_a_evaluation": ambiguity,
    }
    ambiguity_path.write_text(json.dumps(_json_safe(ambiguity_payload), indent=2))

    summary_path.write_text(render_summary(mode_results, multi_mode, ambiguity))

    logger.info(f"wrote {indicator_path}")
    logger.info(f"wrote {multi_mode_path}")
    logger.info(f"wrote {ambiguity_path}")
    logger.info(f"wrote {summary_path}")


def render_summary(
    mode_results: dict[str, Any],
    multi_mode: dict[str, Any],
    ambiguity: dict[str, Any],
) -> str:
    """Render human-readable session-1 execution summary in markdown."""
    lines: list[str] = []
    lines.append("# Phase 5 Diagnostic Execution Session-1 — Summary")
    lines.append("")
    lines.append(f"Generated: `{_now_iso_utc()}`")
    lines.append("")
    lines.append("Anchored to sealed sub-spec at `docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md` (sub-spec drafting cycle SEAL at `49ae7e3`).")
    lines.append("")
    lines.append("## §2.a-§2.f Per-mode binary outcomes")
    lines.append("")
    lines.append("| Mode | Detected | Key statistic |")
    lines.append("|---|---|---|")
    for mode_key, label in (
        ("signal_decay", "§2.a signal decay"),
        ("cost_drag", "§2.b cost drag"),
        ("cohort_weakness", "§2.c cohort weakness"),
        ("andgate_overfit", "§2.d AND-gate overfit"),
        ("success_metric_mismatch", "§2.e success-metric mismatch"),
        ("regime_change", "§2.f regime change"),
    ):
        r = mode_results[mode_key]
        if r.get("execution_suspended"):
            detected_str = f"SUSPENDED ({r.get('suspension_cause')})"
            stat_str = ""
        else:
            detected_str = "✓ detected" if r["detected"] else "not detected"
            if mode_key == "signal_decay":
                stat_str = f"Wilcoxon p={r['p_value']:.4g} n={r['n_effective']}"
            elif mode_key == "cost_drag":
                stat_str = f"Wilcoxon p={r['p_value']:.4g} on ρ_i across [7,13,15,17]bps"
            elif mode_key == "cohort_weakness":
                stat_str = (
                    f"rank_median={r['primary_oos']['rank_median']:.3f} "
                    f"rank_p75={r['primary_oos']['rank_p75']:.3f}"
                )
            elif mode_key == "andgate_overfit":
                stat_str = (
                    f"TOST p={r['tost_p_value']} obs={r['obs']} "
                    f"exp={r['exp']:.3f} ε={r['epsilon']:.3f}"
                )
            elif mode_key == "success_metric_mismatch":
                p_a = r["primary_15bps"]["per_stratum"]["stratum_a_calendar_effect"]["p_value"]
                p_b = r["primary_15bps"]["per_stratum"]["stratum_b_non_calendar"]["p_value"]
                stat_str = f"Wilcoxon p_A={p_a:.4g} p_B={p_b:.4g} Bonferroni α=0.025"
            elif mode_key == "regime_change":
                stat_str = (
                    f"forward_T={r['forward_T']:.5f} "
                    f"band=[{r['quantile_band']['lower_q025']:.5f}, "
                    f"{r['quantile_band']['upper_q975']:.5f}]"
                )
            else:
                stat_str = ""
        lines.append(f"| {label} | {detected_str} | {stat_str} |")
    lines.append("")
    lines.append("## §3.1 Multi-mode composite labels")
    lines.append("")
    if multi_mode.get("execution_suspended"):
        lines.append(f"**Execution suspended**: {multi_mode.get('suspension_cause')}")
    elif multi_mode["emits_substantive"]:
        firing = ", ".join(multi_mode["firing_modes"]) or "(none)"
        lines.append(f"Firing modes: `{firing}`")
        lines.append("")
        for mode_key, label in multi_mode["per_mode_labels"].items():
            lines.append(f"- **{mode_key}**: {label}")
    else:
        lines.append("§3.1 silent — 0 modes detected at canonical binary register; §3.2 handles per XOR complementarity")
    lines.append("")
    lines.append("## §3.2 Diagnostic ambiguity disposition")
    lines.append("")
    if ambiguity.get("execution_suspended"):
        lines.append(f"**Execution suspended**: {ambiguity.get('suspension_cause')}")
    elif ambiguity.get("silent_state"):
        firing = ", ".join(ambiguity.get("firing_modes", [])) or "(none)"
        lines.append(f"§3.2 silent — §3.1 fired on firing_modes=`{firing}` per sealed XOR complementarity property")
    else:
        lines.append(f"**Label**: `{ambiguity['label']}`")
        tt = ambiguity.get("terminal_trigger") or {}
        lines.append(f"**Terminal trigger**: `{json.dumps(_json_safe(tt))}`")
    lines.append("")
    lines.append("## Phase 4 verdict invariance")
    lines.append("")
    lines.append(
        "§2.a-§2.f outputs above operate at sealed register-class-distinct registers per sealed §2.x prose; "
        "none of the per-mode results modify the Phase 4 closeout verdict at 15bps (no forward persistence "
        "detected at PLAN §1.5 success criterion). The Phase 4 verdict is sealed at PLAN §1.5 framework register "
        "per scoping §4.6 sealed-content invariance, anchored at `docs/closeout/PHASE4_RESULTS.md` commit `e8f62f1` "
        "+ tag `phase4-forward-test-v1`."
    )
    lines.append("")
    lines.append("## Sealed §4.1 hard scope binding")
    lines.append("")
    lines.append(
        "Sealed §4.1 hard scope binding (verbatim at sub-spec §8 ADV-N4 quote in "
        "`docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md` sealed at commit `49ae7e3`)."
    )
    lines.append("")
    lines.append("Downstream consumers (§4a successor-class mapping / §4b framing-resolution-pressure / §5 admissibility flags / §6 attribution narrative) are deferred to subsequent session scope at Charlie register-event boundary per pre-fire plan (a) pacing-not-pre-committed.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 5 diagnostic execution orchestrator — fires §2.a-§2.f + "
            "§3.1 + §3.2 per sealed sub-spec."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate sealed inputs + execute §2-§3 procedures with stdout "
            "report only; write no artifacts."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/phase5_diagnostic/execution_session_1_v1"),
        help="Directory to write indicator_outputs.json + multi_mode_labels.json + ambiguity_disposition.json + execution_summary.md",
    )
    parser.add_argument(
        "--skip-parquet",
        action="store_true",
        help="Skip parquet load + §2.f execution (for partial dry-run only).",
    )
    args = parser.parse_args(argv)

    if args.skip_parquet and not args.dry_run:
        parser.error("--skip-parquet requires --dry-run")

    logger = _setup_logger()
    logger.info("Phase 5 diagnostic execution session-1 start")
    logger.info(f"dry_run={args.dry_run} output_dir={args.output_dir}")

    logger.info("Loading sealed §1 inputs")
    try:
        inputs = load_all_sealed_inputs(skip_parquet=args.skip_parquet)
    except Exception as exc:
        logger.error(f"sealed input load failed: {type(exc).__name__}: {exc}")
        return 2
    logger.info("Sealed §1 inputs loaded")

    logger.info("Verifying sealed §1 schema + count invariants")
    schema_report = verify_schema_and_counts(inputs, logger)
    if not schema_report["all_green"]:
        logger.error("Schema/count verification FAILED:")
        logger.error(json.dumps(schema_report, indent=2, default=str))
        return 3
    logger.info("Schema/count verification CLEAN — all sealed §1 invariants pass")

    logger.info("Firing §2.a-§2.f indicator construction")
    mode_results = execute_indicators(inputs, logger)

    detections, nan_modes, suspended_modes = extract_detections_and_states(mode_results)
    logger.info(
        f"Per-mode detection state: firing={sorted(k for k,v in detections.items() if v is True)} "
        f"not-detected={sorted(k for k,v in detections.items() if v is False)} "
        f"nan_modes={nan_modes} suspended_modes={suspended_modes}"
    )

    logger.info("Assembling §3.1 multi-mode composite labels")
    multi_mode = assemble_multi_mode_labels(detections, nan_modes=nan_modes, suspended_modes=suspended_modes)

    logger.info("Evaluating §3.2 Case A condition")
    ambiguity = evaluate_case_a(detections, nan_modes=nan_modes, suspended_modes=suspended_modes)

    if args.dry_run:
        logger.info("DRY-RUN: skipping artifact write; reporting to stdout only")
        report = {
            "schema_verification": schema_report,
            "detections": detections,
            "nan_modes": nan_modes,
            "suspended_modes": suspended_modes,
            "multi_mode_summary": {
                "emits_substantive": multi_mode.get("emits_substantive"),
                "firing_modes": multi_mode.get("firing_modes"),
                "per_mode_labels": multi_mode.get("per_mode_labels"),
                "execution_suspended": multi_mode.get("execution_suspended"),
            },
            "ambiguity_summary": {
                "label": ambiguity.get("label"),
                "terminal_trigger": ambiguity.get("terminal_trigger"),
                "silent_state": ambiguity.get("silent_state"),
                "execution_suspended": ambiguity.get("execution_suspended"),
            },
        }
        print(json.dumps(_json_safe(report), indent=2))
        logger.info("DRY-RUN complete")
        return 0

    logger.info(f"Writing outputs to {args.output_dir}")
    try:
        write_outputs(args.output_dir, mode_results, multi_mode, ambiguity, schema_report, logger)
    except OSError as exc:
        logger.error(f"artifact write failed: {type(exc).__name__}: {exc}")
        return 4
    logger.info("Phase 5 diagnostic execution session-1 complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
