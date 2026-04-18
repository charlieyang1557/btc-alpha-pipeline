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
from agents.critic.d7b_stub import StubD7bBackend  # noqa: E402
from agents.critic.orchestrator import run_critic  # noqa: E402
from agents.critic.replay import reconstruct_batch_context_at_position  # noqa: E402
from agents.orchestrator.budget_ledger import BudgetLedger  # noqa: E402
from strategies.dsl import StrategyDSL  # noqa: E402, F401


LEDGER_PATH = Path("agents/spend_ledger.db")
EXPECTATIONS_PATH = Path("docs/d7_stage2a/replay_candidate_expectations.md")


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
    # Reconstruct replay context.
    dsl, theme, batch_context = reconstruct_batch_context_at_position(
        batch_uuid, position, stage2d_artifacts_root=artifacts_root,
    )

    print(f"[stage2a] replay: batch={batch_uuid}, position={position}, "
          f"theme={theme}")
    print(f"[stage2a] DSL name: {dsl.name}")
    print(f"[stage2a] factors: {sorted(dsl.factors_used())}")

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
            compute_cost_usd,
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
    now = datetime.now(timezone.utc)
    row_id = ledger.write_pending(
        batch_id=batch_uuid,
        api_call_kind=f"d7b_critic_{backend_label}",
        backend_kind="d7b_critic",
        call_role="critique",
        estimated_cost_usd=est_cost,
        now=now,
        notes=f"Stage 2a {backend_label}, position={position}",
    )

    # Run critic.
    result = run_critic(dsl, theme, batch_context, backend)

    # Finalize ledger.
    actual_cost = 0.0
    if result.d7b_cost_actual_usd is not None:
        actual_cost = result.d7b_cost_actual_usd
    ledger.finalize(
        row_id,
        actual_cost_usd=actual_cost,
        now=datetime.now(timezone.utc),
    )

    result_dict = result.to_dict()

    # Write result artifact alongside the raw payloads.
    if confirm_live:
        critic_dir = artifacts_root / f"batch_{batch_uuid}" / "critic"
        critic_dir.mkdir(parents=True, exist_ok=True)
        result_path = critic_dir / f"call_{position:04d}_critic_result.json"
        result_path.write_text(
            json.dumps(result_dict, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"[stage2a] result written to {result_path}")

    return result_dict


def main() -> None:
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
