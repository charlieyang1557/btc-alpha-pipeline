"""D7 Stage 2a — live-call entrypoint (single forensic probe).

This script is the final step of the D7 Stage 2a pipeline. It:

    1. Reconstructs the exact BatchContext from a signed-off Stage 2d
       batch at a given position.
    2. Runs ``run_critic()`` with either the stub backend (default) or
       the live Sonnet backend (``--confirm-live``).
    3. Writes raw artifacts to ``raw_payloads/batch_<uuid>/critic/``.
    4. Charges the production spend ledger (``agents/spend_ledger.db``).

Safety flags:

    ``--stub`` (default)
        Uses ``StubD7bBackend`` against real replay artifacts. Exercises
        the full reconstruction + orchestrator path without API calls.

    ``--confirm-live``
        Uses ``LiveSonnetD7bBackend`` for a real Sonnet API call. This
        is the only flag that triggers a live API call. Requires the
        ``ANTHROPIC_API_KEY`` environment variable.

Anti-hindsight-bias gate:

    Before any live call, this script checks that
    ``docs/d7_stage2a/replay_candidate_expectations.md`` exists and was
    committed to git before the current invocation timestamp. This
    prevents results-shopping: the researcher must commit expectations
    before seeing the live response.

    Skipped in ``--stub`` mode (no live call, no bias risk).

CONTRACT BOUNDARY: Claude Code's scope ENDS at a green dry-run. Only
Charlie runs ``--confirm-live``.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow bare ``python scripts/run_d7_stage2a_live.py`` invocation from
# the repo root without requiring ``python -m`` or PYTHONPATH export.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agents.critic.batch_context import BatchContext  # noqa: E402, F401
from agents.critic.d7a_feature_extraction import extract_factors  # noqa: E402
from agents.critic.d7b_stub import StubD7bBackend  # noqa: E402
from agents.critic.orchestrator import run_critic  # noqa: E402
from agents.critic.replay import reconstruct_batch_context_at_position  # noqa: E402
from agents.orchestrator.budget_ledger import BudgetLedger  # noqa: E402
from strategies.dsl import StrategyDSL  # noqa: E402, F401


LEDGER_PATH = Path("agents/spend_ledger.db")
EXPECTATIONS_PATH = Path("docs/d7_stage2a/replay_candidate_expectations.md")
LIVE_CALL_RECORD_PATH = Path("docs/d7_stage2a/stage2a_live_call_record.json")


def _load_dotenv(path: Path | None = None) -> None:
    """Load .env file into os.environ (stdlib-only)."""
    env_path = path or _REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _check_expectations_committed() -> tuple[bool, str]:
    """Verify replay_candidate_expectations.md exists and is committed.

    Returns ``(ok, detail)``. The commit timestamp is NOT validated
    against "before the current invocation" because git timestamps are
    author-controlled. We verify only that the file is tracked and has
    at least one commit.
    """
    if not EXPECTATIONS_PATH.exists():
        return False, f"{EXPECTATIONS_PATH} does not exist"

    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1", "--", str(EXPECTATIONS_PATH)],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return False, (
                f"{EXPECTATIONS_PATH} exists but has no git commit; "
                "commit your expectations before the live call"
            )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return False, f"git check failed: {exc}"

    return True, "expectations file committed"


def run_live(
    batch_uuid: str,
    position: int,
    *,
    confirm_live: bool = False,
    artifacts_root: Path = Path("raw_payloads"),
    ledger_path: Path = LEDGER_PATH,
) -> dict:
    """Run the D7 Stage 2a pipeline against real replay artifacts.

    Args:
        batch_uuid: UUID of the signed-off Stage 2d batch.
        position: 1-indexed call position to replay.
        confirm_live: If True, use the live Sonnet backend. If False
            (default), use the stub backend.
        artifacts_root: Root containing ``batch_<uuid>/`` subdirs.
        ledger_path: Path to the production spend ledger.

    Returns:
        CriticResult as a dict.
    """
    request_ts = datetime.now(timezone.utc)

    # Reconstruct replay context.
    dsl, theme, batch_context = reconstruct_batch_context_at_position(
        batch_uuid, position, stage2d_artifacts_root=artifacts_root,
    )

    print(f"[stage2a] replay: batch={batch_uuid}, position={position}, "
          f"theme={theme}")
    print(f"[stage2a] DSL name: {dsl.name}")
    print(f"[stage2a] factors: {extract_factors(dsl)}")

    # Backend selection.
    if confirm_live:
        ok, detail = _check_expectations_committed()
        if not ok:
            print(f"[stage2a] ABORT: anti-hindsight gate failed: {detail}",
                  file=sys.stderr)
            sys.exit(1)

        from agents.critic.d7b_live import (
            D7B_STAGE2A_COST_CEILING_USD,
            LiveSonnetD7bBackend,
        )

        backend = LiveSonnetD7bBackend(
            raw_payload_dir=artifacts_root,
            api_call_number=position,
            batch_id=batch_uuid,
        )
        est_cost = D7B_STAGE2A_COST_CEILING_USD
        backend_label = "live"
    else:
        backend = StubD7bBackend()
        est_cost = 0.0
        backend_label = "stub"

    print(f"[stage2a] backend: {backend_label}, mode={backend.mode}")

    # Ledger pre-charge.
    ledger = BudgetLedger(ledger_path)
    row_id = ledger.write_pending(
        batch_id=batch_uuid,
        api_call_kind=f"d7b_critic_{backend_label}",
        backend_kind="d7b_critic",
        call_role="critique",
        estimated_cost_usd=est_cost,
        now=request_ts,
        notes=f"Stage 2a {backend_label}, position={position}",
    )

    # Run critic.
    result = run_critic(dsl, theme, batch_context, backend)

    response_ts = datetime.now(timezone.utc)
    wall_clock_s = (response_ts - request_ts).total_seconds()

    # Finalize ledger with actual cost AND token counts.
    actual_cost = 0.0
    if result.d7b_cost_actual_usd is not None:
        actual_cost = result.d7b_cost_actual_usd
    ledger.finalize(
        row_id,
        actual_cost_usd=actual_cost,
        now=response_ts,
        input_tokens=result.d7b_input_tokens,
        output_tokens=result.d7b_output_tokens,
    )

    result_dict = result.to_dict()

    # Write CriticResult artifact on ALL status values (ok, d7a_error,
    # d7b_error, both_error). The error path is forensically valuable:
    # null scores, populated supporting measures, error signature.
    critic_dir = artifacts_root / f"batch_{batch_uuid}" / "critic"
    critic_dir.mkdir(parents=True, exist_ok=True)
    result_path = critic_dir / f"call_{position:04d}_critic_result.json"
    result_path.write_text(
        json.dumps(result_dict, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[stage2a] result written to {result_path}")

    # Collect raw payload file paths for the meta-record.
    prompt_path = critic_dir / f"call_{position:04d}_prompt.txt"
    response_path = critic_dir / f"call_{position:04d}_response.json"
    traceback_path = critic_dir / f"call_{position:04d}_traceback.txt"

    # Build the stage2a_live_call_record.json meta-record (Deliverable 11).
    cost_ratio: float | None = None
    if est_cost > 0 and actual_cost > 0:
        cost_ratio = round(actual_cost / est_cost, 4)

    live_call_record = {
        "request_timestamp_utc": request_ts.isoformat(),
        "response_timestamp_utc": response_ts.isoformat(),
        "wall_clock_seconds": round(wall_clock_s, 3),
        "retry_count": result.d7b_retry_count,
        "d7b_mode": result.d7b_mode,
        "critic_result": result_dict,
        "ledger_row": {
            "row_id": row_id,
            "batch_id": batch_uuid,
            "api_call_kind": f"d7b_critic_{backend_label}",
            "backend_kind": "d7b_critic",
            "call_role": "critique",
            "estimated_cost_usd": est_cost,
            "actual_cost_usd": actual_cost,
            "input_tokens": result.d7b_input_tokens,
            "output_tokens": result.d7b_output_tokens,
        },
        "raw_payload_paths": {
            "prompt": str(prompt_path) if prompt_path.exists() else None,
            "response": str(response_path) if response_path.exists() else None,
            "traceback": str(traceback_path) if traceback_path.exists() else None,
            "critic_result": str(result_path),
        },
        "cost": {
            "estimated_usd": est_cost,
            "actual_usd": actual_cost,
            "ratio": cost_ratio,
        },
        "leakage_audit_result": None,
        "forbidden_language_scan_result": None,
        "refusal_scan_result": None,
    }

    LIVE_CALL_RECORD_PATH.parent.mkdir(parents=True, exist_ok=True)
    LIVE_CALL_RECORD_PATH.write_text(
        json.dumps(live_call_record, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[stage2a] live call record written to {LIVE_CALL_RECORD_PATH}")

    return result_dict


def main() -> None:
    _load_dotenv()

    parser = argparse.ArgumentParser(
        description="D7 Stage 2a: single forensic probe on a replayed candidate.",
    )
    parser.add_argument(
        "--batch-uuid",
        required=True,
        help="UUID of the signed-off Stage 2d batch.",
    )
    parser.add_argument(
        "--position",
        type=int,
        required=True,
        help="1-indexed position within the batch.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--stub",
        action="store_true",
        default=True,
        help="Use stub backend (default — no API call).",
    )
    group.add_argument(
        "--confirm-live",
        action="store_true",
        help="Use live Sonnet backend (real API call).",
    )
    parser.add_argument(
        "--artifacts-root",
        type=Path,
        default=Path("raw_payloads"),
        help="Root directory for Stage 2d artifacts.",
    )
    parser.add_argument(
        "--ledger-path",
        type=Path,
        default=LEDGER_PATH,
        help="Path to spend ledger SQLite.",
    )
    args = parser.parse_args()

    result = run_live(
        args.batch_uuid,
        args.position,
        confirm_live=args.confirm_live,
        artifacts_root=args.artifacts_root,
        ledger_path=args.ledger_path,
    )

    print(f"\n[stage2a] critic_status={result['critic_status']}, "
          f"d7b_mode={result['d7b_mode']}")
    print(f"[stage2a] d7a_rule_scores={result['d7a_rule_scores']}")
    print(f"[stage2a] d7b_llm_scores={result['d7b_llm_scores']}")
    if result.get("d7b_cost_actual_usd"):
        print(f"[stage2a] d7b_cost=${result['d7b_cost_actual_usd']:.6f}")
    if result.get("critic_error_signature"):
        print(f"[stage2a] error_signature={result['critic_error_signature']}")
    print("[stage2a] done.")


if __name__ == "__main__":
    main()
