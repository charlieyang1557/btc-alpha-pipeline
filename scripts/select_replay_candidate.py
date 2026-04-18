"""D7 Stage 2a — replay candidate selection from a signed-off Stage 2d batch.

Scans a Stage 2d summary and selects the first call that passes all seven
selection criteria for use as the forensic replay target. If no candidate
passes, prints a diagnostic breakdown and exits non-zero.

Selection criteria (all must hold):
    1. lifecycle_state == "pending_backtest"
    2. theme != "momentum"
    3. 3 <= len(factors_used) <= 5
    4. At least one crosses_above or crosses_below operator in the DSL
    5. rsi_14 is not the sole factor
    6. position in [10, 190]
    7. thin_theme_momentum_bleed flag would NOT fire on this call
       (routed through ``agents.critic.d7a_feature_extraction.
       is_thin_theme_momentum_bleed`` — the same predicate used by
       ``d7a_rules.compute_rule_flags``, so selection and flag evaluation
       cannot drift).

NOTE on criterion 7: this is a probe-QUALITY filter, not a probe-VALIDITY
filter. The goal is to pick a replay candidate whose critique is
informative on its own semantic merits rather than dominated by a
known-to-fire D7a flag. Relaxing this criterion (e.g., to admit
flagged candidates for the explicit purpose of auditing the flag's
behavior in the live critic) is a deliberate research decision that
MUST be documented in the acceptance notebook and in
``docs/d7_stage2a/replay_candidate_expectations.md`` before re-running
selection.

Determinism: scan order is ``sorted(calls, key=(position, hypothesis_hash))``
so two invocations of this script against the same ``stage2d_summary.json``
return the same candidate even if the summary's native ordering changes
across serialization layers.

The script reads signed-off artifacts only. It never generates new DSLs,
never mutates on-disk state, and never imports anthropic.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# Allow bare ``python scripts/select_replay_candidate.py`` invocation
# from the repo root without requiring ``python -m`` or PYTHONPATH export.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agents.critic.d7a_feature_extraction import (  # noqa: E402
    is_thin_theme_momentum_bleed,
)


# -----------------------------------------------------------------------
# Selection criteria
# -----------------------------------------------------------------------

MIN_POSITION = 10
MAX_POSITION = 190
MIN_FACTORS = 3
MAX_FACTORS = 5


def _has_cross_operator(response_text: str) -> bool:
    """Check whether the raw response contains a cross operator.

    Parses the JSON DSL from the response and looks for
    ``crosses_above`` or ``crosses_below`` in any condition's
    ``operator`` field. Falls back to a plain substring search if
    JSON parsing fails (defensive).
    """
    try:
        payload = json.loads(response_text)
        if isinstance(payload, dict):
            return _scan_conditions_for_cross(payload)
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return "crosses_above" in response_text or "crosses_below" in response_text


def _scan_conditions_for_cross(dsl: dict) -> bool:
    """Walk entry/exit groups looking for cross operators."""
    for block_key in ("entry", "exit"):
        block = dsl.get(block_key)
        if not isinstance(block, list):
            continue
        for group in block:
            if not isinstance(group, dict):
                continue
            conditions = group.get("conditions", [])
            if not isinstance(conditions, list):
                continue
            for cond in conditions:
                op = cond.get("op") or cond.get("operator", "")
                if op in ("crosses_above", "crosses_below"):
                    return True
    return False


def _call_would_trigger_thin_theme_momentum_bleed(call: dict) -> bool:
    """Check whether this call would trigger the D7a ``thin_theme_momentum_bleed`` flag.

    Adapts a Stage 2d per-call summary record to the canonical predicate
    in ``agents.critic.d7a_feature_extraction.is_thin_theme_momentum_bleed``.
    The per-call record exposes ``default_momentum_factors_used`` as a
    list of distinct factor names; its length is the exact input the
    predicate expects.
    """
    theme = call.get("theme", "")
    momentum_used = call.get("default_momentum_factors_used") or []
    return is_thin_theme_momentum_bleed(theme, len(momentum_used))


def passes_selection(
    call: dict,
    *,
    batch_dir: Path,
    batch_uuid: str,
) -> tuple[bool, str]:
    """Check all seven criteria. Returns (pass, reason)."""
    pos = call.get("position")

    if call.get("lifecycle_state") != "pending_backtest":
        return False, "lifecycle_state != pending_backtest"

    if call.get("theme") == "momentum":
        return False, "theme == momentum"

    factors = call.get("factors_used") or []
    if not (MIN_FACTORS <= len(factors) <= MAX_FACTORS):
        return False, f"n_factors={len(factors)} outside [{MIN_FACTORS},{MAX_FACTORS}]"

    if factors == ["rsi_14"]:
        return False, "rsi_14 is sole factor"

    if pos is None or not (MIN_POSITION <= pos <= MAX_POSITION):
        return False, f"position={pos} outside [{MIN_POSITION},{MAX_POSITION}]"

    if _call_would_trigger_thin_theme_momentum_bleed(call):
        return False, "thin_theme_momentum_bleed would fire"

    response_path = _find_response_path(batch_dir, pos)
    if response_path is None:
        return False, f"response file not found for position {pos}"

    try:
        response_text = response_path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"cannot read response: {exc}"

    if not _has_cross_operator(response_text):
        return False, "no crosses_above/crosses_below operator"

    return True, "all criteria met"


def _find_response_path(batch_dir: Path, position: int) -> Path | None:
    """Locate the response file for a position, handling retries."""
    primary = batch_dir / f"attempt_{position:04d}_response.txt"
    if primary.exists():
        return primary
    retries = sorted(
        batch_dir.glob(f"attempt_{position:04d}_retry_*_response.txt")
    )
    if retries:
        return retries[-1]
    return None


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------


def select_candidate(
    batch_uuid: str,
    *,
    artifacts_root: Path = Path("raw_payloads"),
    summary_name: str = "stage2d_summary.json",
) -> dict | None:
    """Return the first call record passing all criteria, or None."""
    batch_dir = artifacts_root / f"batch_{batch_uuid}"
    summary_path = batch_dir / summary_name

    if not summary_path.exists():
        print(
            f"[select] summary not found: {summary_path}\n"
            f"[select] batch {batch_uuid} may not exist in {artifacts_root}/",
            file=sys.stderr,
        )
        return None

    with summary_path.open(encoding="utf-8") as fh:
        summary = json.load(fh)

    calls: list[dict] = summary.get("calls", [])
    if not calls:
        print("[select] summary has no calls", file=sys.stderr)
        return None

    # Deterministic scan order: position ascending, then hypothesis_hash
    # lexicographic as a stable tiebreak. This pins the selection to a
    # reproducible candidate even if the upstream summary's native
    # ordering shifts across serialization or aggregation layers.
    calls = sorted(
        calls,
        key=lambda c: (
            c.get("position", float("inf")),
            c.get("hypothesis_hash", ""),
        ),
    )

    rejection_reasons: dict[str, int] = {}
    for call in calls:
        ok, reason = passes_selection(
            call, batch_dir=batch_dir, batch_uuid=batch_uuid,
        )
        if ok:
            return call
        rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

    print(
        f"[select] no candidate passed all criteria "
        f"({len(calls)} calls examined):",
        file=sys.stderr,
    )
    for reason, count in sorted(
        rejection_reasons.items(), key=lambda x: -x[1]
    ):
        print(f"  {count:4d}  {reason}", file=sys.stderr)
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Select a D7 Stage 2a replay candidate from a Stage 2d batch.",
    )
    parser.add_argument(
        "batch_uuid",
        help="UUID of the signed-off Stage 2d batch",
    )
    parser.add_argument(
        "--artifacts-root",
        type=Path,
        default=Path("raw_payloads"),
        help="Root directory containing batch_<uuid>/ subdirs",
    )
    parser.add_argument(
        "--summary-name",
        default="stage2d_summary.json",
        help="Filename of the summary JSON within the batch dir",
    )
    args = parser.parse_args()

    result = select_candidate(
        args.batch_uuid,
        artifacts_root=args.artifacts_root,
        summary_name=args.summary_name,
    )
    if result is None:
        sys.exit(1)

    print(json.dumps(result, indent=2))
    print(
        f"\n[select] recommended: position={result['position']}, "
        f"theme={result['theme']}, "
        f"n_factors={len(result.get('factors_used', []))}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
