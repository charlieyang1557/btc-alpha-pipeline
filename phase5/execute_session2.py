"""Phase 5 diagnostic execution orchestrator — Session-2 scope.

Session-2 cycle scope (per Charlie-register ratified pre-fire plan with patches
1+2+3 at 2026-05-15): consume sealed session-1 outputs and execute §4a
successor-class mapping + §4b framing-resolution-pressure assessment + §5
substantive-vs-operational admissibility flagging + initial §6 narrative draft.

Sealed sub-spec at docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md (sub-spec drafting
cycle SEAL at commit 49ae7e3). Session-1 SEAL at commit ad35915 reads
data/phase5_diagnostic/execution_session_1_v1/ as canonical input register.

Per Patch 1 + V12 anchor: §6 narrative draft is strict structural-template
traversal output only — no terminal-conclusion invocation, no framing-question
(1)/(2)/(3)/(4) resolution, no admissibility-flag interpretive narration.

Usage:
    python -m phase5.execute_session2 --dry-run
    python -m phase5.execute_session2 \
        --session-1-dir data/phase5_diagnostic/execution_session_1_v1 \
        --output-dir data/phase5_diagnostic/execution_session_2_v1
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from phase5.admissibility import flag_admissibility
from phase5.framing_pressure import assess_framing_pressure
from phase5.narrative_draft import draft_narrative
from phase5.successor_class import map_successor_classes

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SESSION_1_DIR = REPO_ROOT / "data" / "phase5_diagnostic" / "execution_session_1_v1"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "phase5_diagnostic" / "execution_session_2_v1"

SEALED_SUBSPEC_COMMIT = "49ae7e3"
SEALED_SESSION_1_COMMIT = "ad35915"


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("phase5.execute_session2")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)sZ [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    handler.formatter.converter = time.gmtime  # type: ignore[assignment]
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def load_session_1_artifacts(session_1_dir: Path) -> dict[str, Any]:
    """Load session-1 sealed output artifacts at canonical register."""
    indicator_path = session_1_dir / "indicator_outputs.json"
    multi_path = session_1_dir / "multi_mode_labels.json"
    ambiguity_path = session_1_dir / "ambiguity_disposition.json"
    for p in (indicator_path, multi_path, ambiguity_path):
        if not p.exists():
            raise FileNotFoundError(
                f"sealed session-1 artifact not found at {p} "
                f"(expected at sealed canonical register; "
                f"session-1 SEAL at commit {SEALED_SESSION_1_COMMIT})"
            )
    with indicator_path.open("r") as fh:
        indicator_outputs = json.load(fh)
    with multi_path.open("r") as fh:
        multi_envelope = json.load(fh)
    with ambiguity_path.open("r") as fh:
        ambiguity_envelope = json.load(fh)
    return {
        "indicator_outputs": indicator_outputs,
        "multi_mode_envelope": multi_envelope,
        "ambiguity_envelope": ambiguity_envelope,
    }


def derive_detections(multi_mode_result: dict[str, Any]) -> dict[str, bool]:
    """Reconstruct per-mode detection dict from §3.1 multi_mode_result."""
    detections: dict[str, bool] = {}
    for m in multi_mode_result.get("firing_modes", []):
        detections[m] = True
    for m in multi_mode_result.get("not_detected_modes", []):
        detections[m] = False
    return detections


def run_session2(
    session_1_dir: Path,
    output_dir: Path,
    dry_run: bool,
    logger: logging.Logger,
) -> dict[str, Any]:
    """Execute §4a → §4b → §5 → §6 pipeline from session-1 sealed outputs."""
    logger.info(f"loading session-1 sealed artifacts from {session_1_dir}")
    artifacts = load_session_1_artifacts(session_1_dir)
    indicator_outputs = artifacts["indicator_outputs"]
    multi_envelope = artifacts["multi_mode_envelope"]
    ambiguity_envelope = artifacts["ambiguity_envelope"]

    # Verify session-1 sealed_subspec_commit matches current across ALL three envelopes
    # per Codex adversarial review HIGH-1 fix (indicator_outputs was previously unchecked
    # and could ship stale narrative if mismatched).
    for name, env in [
        ("indicator_outputs", indicator_outputs),
        ("multi_mode_labels", multi_envelope),
        ("ambiguity_disposition", ambiguity_envelope),
    ]:
        sealed_commit = env.get("sealed_subspec_commit")
        if sealed_commit != SEALED_SUBSPEC_COMMIT:
            raise ValueError(
                f"session-1 {name} sealed_subspec_commit mismatch: "
                f"expected {SEALED_SUBSPEC_COMMIT}, got {sealed_commit}"
            )

    multi_mode_result = multi_envelope["multi_mode_labels"]
    case_a_result = ambiguity_envelope["case_a_evaluation"]
    detections = derive_detections(multi_mode_result)

    # Cross-check per-mode detected flag in indicator_outputs against §3.1 firing/not-detected
    # sets per Codex adversarial review HIGH-1 fix.
    indicator_mode_results = indicator_outputs.get("mode_results", {})
    expected_firing = set(multi_mode_result.get("firing_modes", []))
    expected_not_detected = set(multi_mode_result.get("not_detected_modes", []))
    for mode_key, mr in indicator_mode_results.items():
        if not isinstance(mr, dict) or "detected" not in mr:
            continue
        ind_detected = mr.get("detected")
        if ind_detected is True and mode_key not in expected_firing:
            raise ValueError(
                f"indicator_outputs mode_results[{mode_key}].detected=True but "
                f"§3.1 firing_modes={sorted(expected_firing)} does not include it"
            )
        if ind_detected is False and mode_key not in expected_not_detected:
            raise ValueError(
                f"indicator_outputs mode_results[{mode_key}].detected=False but "
                f"§3.1 not_detected_modes={sorted(expected_not_detected)} does not include it"
            )

    logger.info(
        f"reconstructed detections: firing={sorted([m for m,d in detections.items() if d])}, "
        f"not_detected={sorted([m for m,d in detections.items() if not d])}"
    )

    # §4a successor-class mapping.
    logger.info("running §4a successor-class mapping")
    successor_class_result = map_successor_classes(multi_mode_result, case_a_result)
    logger.info(
        f"§4a output: input_pattern={successor_class_result.get('input_pattern')}; "
        f"assignments={len(successor_class_result.get('assignments', []))}"
    )

    # §4b framing-pressure assessment.
    logger.info("running §4b framing-pressure assessment")
    framing_pressure_result = assess_framing_pressure(
        multi_mode_result, case_a_result, successor_class_result
    )
    logger.info(
        f"§4b output: pressure_label_set={len(framing_pressure_result.get('pressure_label_set', []))}"
    )

    # §5 admissibility flagging.
    logger.info("running §5 admissibility flagging")
    admissibility_result = flag_admissibility(
        multi_mode_result, case_a_result, successor_class_result, framing_pressure_result
    )
    logger.info(
        f"§5 output: substantive={admissibility_result['substantive']['admissible']}; "
        f"operational={admissibility_result['operational']['admissible']}"
    )

    # §6 initial narrative draft (structural-template traversal).
    logger.info("running §6 initial narrative draft (structural-template traversal)")
    narrative_result = draft_narrative(
        detections=detections,
        indicator_outputs=indicator_outputs,
        multi_mode_result=multi_mode_result,
        case_a_result=case_a_result,
        successor_class_result=successor_class_result,
        framing_pressure_result=framing_pressure_result,
        admissibility_result=admissibility_result,
    )
    audit = narrative_result["anti_pre_emption_audit"]
    if audit["forbidden_pattern_matches"]:
        raise ValueError(
            f"V12 anchor failure: §6 narrative draft contains forbidden decisional "
            f"language: {audit['forbidden_pattern_matches']}"
        )
    logger.info(
        f"§6 anti-pre-emption audit clean: "
        f"no_terminal_conclusion_invocation={audit['no_terminal_conclusion_invocation']}, "
        f"no_framing_question_resolution={audit['no_framing_question_resolution']}, "
        f"no_admissibility_flag_interpretive_narration={audit['no_admissibility_flag_interpretive_narration']}"
    )

    if dry_run:
        logger.info("dry-run mode — no artifacts written")
        return {
            "dry_run": True,
            "successor_class_result": successor_class_result,
            "framing_pressure_result": framing_pressure_result,
            "admissibility_result": admissibility_result,
            "narrative_result": narrative_result,
        }

    # Write output artifacts at canonical register.
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = _now_iso_utc()
    envelope_meta = {
        "schema_version": 1,
        "generated_at_utc": generated_at,
        "sealed_subspec_commit": SEALED_SUBSPEC_COMMIT,
        "sealed_session_1_commit": SEALED_SESSION_1_COMMIT,
        "session": "phase_5_diagnostic_execution_session_2",
    }

    sc_path = output_dir / "successor_class_outputs.json"
    fp_path = output_dir / "framing_pressure_outputs.json"
    adm_path = output_dir / "admissibility_flags.json"
    nd_path = output_dir / "narrative_draft.md"
    es_path = output_dir / "execution_summary.md"

    with sc_path.open("w") as fh:
        json.dump({**envelope_meta, "successor_class": successor_class_result}, fh, indent=2)
    with fp_path.open("w") as fh:
        json.dump({**envelope_meta, "framing_pressure": framing_pressure_result}, fh, indent=2)
    with adm_path.open("w") as fh:
        json.dump({**envelope_meta, "admissibility": admissibility_result}, fh, indent=2)
    with nd_path.open("w") as fh:
        fh.write(narrative_result["narrative_markdown"])

    summary = _render_execution_summary(
        generated_at=generated_at,
        successor_class_result=successor_class_result,
        framing_pressure_result=framing_pressure_result,
        admissibility_result=admissibility_result,
        narrative_result=narrative_result,
    )
    with es_path.open("w") as fh:
        fh.write(summary)
    logger.info(f"wrote 5 artifacts to {output_dir}")

    return {
        "dry_run": False,
        "output_dir": str(output_dir),
        "artifacts": {
            "successor_class_outputs": str(sc_path),
            "framing_pressure_outputs": str(fp_path),
            "admissibility_flags": str(adm_path),
            "narrative_draft": str(nd_path),
            "execution_summary": str(es_path),
        },
    }


def _render_execution_summary(
    generated_at: str,
    successor_class_result: dict[str, Any],
    framing_pressure_result: dict[str, Any],
    admissibility_result: dict[str, Any],
    narrative_result: dict[str, Any],
) -> str:
    """Render session-2 execution summary markdown.

    Mirrors session-1 execution_summary.md layout: per-§ output disclosure
    + V12 audit summary + Phase 4 verdict invariance + anti-pre-emption
    discipline reaffirmation. Strict structural enumeration only — no
    closeout narrative interpretation per Patch 1 + V12 anchor.
    """
    sub = admissibility_result["substantive"]
    op = admissibility_result["operational"]
    audit = narrative_result["anti_pre_emption_audit"]
    lines = [
        "# Phase 5 Diagnostic Execution Session-2 — Summary",
        "",
        f"Generated: `{generated_at}`",
        "",
        f"Anchored to sealed sub-spec at `docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md` "
        f"(sub-spec drafting cycle SEAL at `{SEALED_SUBSPEC_COMMIT}`); consumes "
        f"sealed session-1 outputs at `data/phase5_diagnostic/execution_session_1_v1/` "
        f"(session-1 SEAL at `{SEALED_SESSION_1_COMMIT}`).",
        "",
        "## §4a successor-cycle-class mapping",
        "",
        f"- input_pattern: `{successor_class_result.get('input_pattern')}`",
        f"- assignment count: {len(successor_class_result.get('assignments', []))}",
    ]
    for a in successor_class_result.get("assignments", []):
        lines.append(
            f"  - class: `{a['class']}` ({a['disposition']}); "
            f"source_modes: {a.get('source_modes', [])}"
        )
    lines += [
        "",
        "## §4b framing-resolution-pressure assessment",
        "",
        f"- pressure_label_set size: {len(framing_pressure_result.get('pressure_label_set', []))}",
    ]
    for o in framing_pressure_result.get("pressure_label_set", []):
        lines.append(
            f"  - finding_source: `{o.get('finding_source')}`; "
            f"pressure_label: `{o.get('pressure_label')}`; "
            f"propagation_state: `{o.get('propagation_state')}`"
        )
    lines += [
        "",
        "## §5 substantive-vs-operational admissibility flags",
        "",
        f"- substantive: `admissible={sub['admissible']}`; "
        f"propagation_state=`{sub['propagation_state']}`; basis=\"{sub['basis']}\"",
        f"- operational: `admissible={op['admissible']}`; "
        f"propagation_state=`{op['propagation_state']}`; basis=\"{op['basis']}\"",
        "",
        "## §6 initial narrative draft (structural-template traversal)",
        "",
        "- See `narrative_draft.md` for full structural-template traversal output.",
        f"- V12 anchor anti-pre-emption audit: "
        f"no_terminal_conclusion_invocation={audit['no_terminal_conclusion_invocation']}, "
        f"no_framing_question_resolution={audit['no_framing_question_resolution']}, "
        f"no_admissibility_flag_interpretive_narration={audit['no_admissibility_flag_interpretive_narration']}.",
        f"- Forbidden pattern matches: {len(audit['forbidden_pattern_matches'])} (clean).",
        "",
        "## Phase 4 verdict invariance",
        "",
        "Session-2 §4a/§4b/§5/§6 outputs operate at sealed register-class-distinct "
        "registers per sealed §4a/§4b/§5/§6 prose; none of these outputs modify the "
        "Phase 4 closeout verdict at 15bps (no forward persistence detected at PLAN "
        "§1.5 success criterion). The Phase 4 verdict is sealed at PLAN §1.5 framework "
        "register per scoping §4.6 sealed-content invariance, anchored at "
        "`docs/closeout/PHASE4_RESULTS.md` commit `e8f62f1` + tag `phase4-forward-test-v1`.",
        "",
        "## Anti-pre-emption discipline",
        "",
        "Per Patch 1 + V12 anchor: §6 narrative draft is strict structural-template "
        "traversal output only. Terminal-conclusion invocation decision, framing-question "
        "(1)/(2)/(3)/(4) resolution decision, and admissibility-flag interpretive "
        "narration are reserved for Phase 5 SEAL author register at arc-level closeout "
        "SEAL per sealed §6 (vii)(c) inheritance — NOT session-2 scope.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 5 diagnostic execution orchestrator (session-2 scope: §4a + "
            "§4b + §5 + §6 initial narrative draft)."
        )
    )
    parser.add_argument(
        "--session-1-dir",
        type=Path,
        default=DEFAULT_SESSION_1_DIR,
        help="Path to sealed session-1 output directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Path to write session-2 output artifacts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate + execute pipeline with stdout-only report; write no artifacts.",
    )
    args = parser.parse_args()
    logger = _setup_logger()
    logger.info(f"phase5.execute_session2 start (dry_run={args.dry_run})")
    try:
        result = run_session2(args.session_1_dir, args.output_dir, args.dry_run, logger)
    except Exception as exc:
        logger.error(f"session-2 execution failed: {exc}")
        return 1
    logger.info(f"phase5.execute_session2 complete (dry_run={result.get('dry_run')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
