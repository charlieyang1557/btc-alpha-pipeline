"""D6 Stage 2a — single-hypothesis smoke run.

Executes one live Sonnet call end-to-end through the full pipeline:
prompt build → leakage audit → pre-charge ledger → API call → raw
payload log → classify → ingest → finalize ledger → invariant check.

Hard constraints enforced:
    - batch_size = 1 (exactly one hypothesis)
    - budget cap = $1 (via BudgetLedger.can_afford)
    - prompt caching DISABLED
    - leakage audit MUST pass before the call is sent
    - all Stage 1 constraints preserved (frozen factor registry,
      frozen DSL grammar, accounting rules)

Usage:
    python -m agents.proposer.stage2a_smoke [--dry-run]

``--dry-run`` uses the stub backend instead of Sonnet.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _load_dotenv(path: Path | None = None) -> None:
    """Load .env file into os.environ (stdlib-only, no python-dotenv)."""
    env_path = path or Path(__file__).resolve().parents[2] / ".env"
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

from agents.orchestrator.budget_ledger import BudgetLedger
from agents.orchestrator.ingest import (
    BatchIngestState,
    assert_lifecycle_invariant_at_batch_close,
    ingest_output,
)
from agents.proposer.interface import BatchContext
from agents.proposer.prompt_builder import audit_prompt_for_leakage, build_prompt
from agents.proposer.sonnet_backend import (
    SonnetProposerBackend,
    estimate_cost_usd,
)
from agents.proposer.stub_backend import StubProposerBackend
from agents.themes import THEMES
from factors.registry import get_registry


STAGE2A_BATCH_CAP_USD = 1.0
STAGE2A_MONTHLY_CAP_USD = 100.0
RAW_PAYLOAD_DIR = Path("raw_payloads")
LEDGER_PATH = Path("agents/spend_ledger.db")


def run_stage2a(*, dry_run: bool = False) -> dict:
    """Execute the Stage 2a smoke run. Returns a summary dict."""
    _load_dotenv()
    registry = get_registry()
    batch_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    print(f"[Stage 2a] batch_id={batch_id}")
    print(f"[Stage 2a] dry_run={dry_run}")
    print(f"[Stage 2a] timestamp={now.isoformat()}")

    # --- Build prompt and run leakage audit BEFORE anything else ---
    ctx = BatchContext(
        batch_id=batch_id,
        position=1,
        batch_size=1,
        allowed_factors=tuple(registry.list_names()),
        allowed_operators=(
            "<", "<=", ">", ">=", "==", "crosses_above", "crosses_below",
        ),
        theme_slot=0,
        budget_remaining={
            "batch_usd": STAGE2A_BATCH_CAP_USD,
            "monthly_usd": STAGE2A_MONTHLY_CAP_USD,
        },
    )

    prompt = build_prompt(ctx, registry=registry)
    leakage_findings = audit_prompt_for_leakage(prompt)
    if leakage_findings:
        print(f"[Stage 2a] ABORT: leakage audit failed: {leakage_findings}")
        sys.exit(1)
    print("[Stage 2a] leakage audit: CLEAN")

    # --- Budget pre-charge ---
    ledger = BudgetLedger(LEDGER_PATH)
    est_cost = estimate_cost_usd(estimated_input_tokens=4000, max_output_tokens=2000)

    if not ledger.can_afford(
        batch_id=batch_id,
        estimated_cost_usd=est_cost,
        now=now,
        batch_cap_usd=STAGE2A_BATCH_CAP_USD,
        monthly_cap_usd=STAGE2A_MONTHLY_CAP_USD,
    ):
        print(
            f"[Stage 2a] ABORT: cannot afford estimated ${est_cost:.4f} "
            f"(batch spent: ${ledger.batch_spent_usd(batch_id):.4f}, "
            f"monthly: ${ledger.monthly_spent_usd(now=now):.4f})"
        )
        sys.exit(1)

    ledger_row_id = ledger.write_pending(
        batch_id=batch_id,
        api_call_kind="proposer",
        estimated_cost_usd=est_cost,
        now=now,
    )
    print(f"[Stage 2a] pre-charge: ${est_cost:.6f} (ledger row {ledger_row_id})")

    # --- Select backend ---
    if dry_run:
        backend = StubProposerBackend(registry=registry, cost_per_call_usd=0.0)
        print("[Stage 2a] backend: stub (dry-run)")
    else:
        backend = SonnetProposerBackend(
            registry=registry,
            max_retries=3,
            backoff_base_seconds=1.0,
            raw_payload_dir=RAW_PAYLOAD_DIR,
        )
        print("[Stage 2a] backend: sonnet (live)")

    # --- Call backend ---
    try:
        output = backend.generate(ctx)
    except Exception as exc:
        ledger.mark_crashed(ledger_row_id, now=datetime.now(timezone.utc),
                            notes=f"generate() raised: {exc}")
        print(f"[Stage 2a] CRASH: {exc}")
        raise

    # --- Finalize ledger ---
    actual_cost = output.cost_actual_usd
    ledger.finalize(ledger_row_id, actual_cost_usd=actual_cost,
                    now=datetime.now(timezone.utc))
    print(f"[Stage 2a] actual_cost: ${actual_cost:.6f}")
    print(f"[Stage 2a] estimated_cost: ${est_cost:.6f}")
    print(f"[Stage 2a] cost delta: ${actual_cost - est_cost:.6f}")

    # --- Ingest into lifecycle ---
    state = BatchIngestState(batch_id=batch_id)
    records = ingest_output(state, output)

    print(f"[Stage 2a] hypotheses_attempted: {state.hypotheses_attempted}")
    print(f"[Stage 2a] lifecycle_counts: {dict(state.lifecycle_counts)}")
    for rec in records:
        print(
            f"[Stage 2a] record: position={rec.position} "
            f"state={rec.lifecycle_state} hash={rec.hypothesis_hash}"
        )

    # --- Batch-close invariant ---
    assert_lifecycle_invariant_at_batch_close(state)
    print("[Stage 2a] lifecycle invariant: OK")

    # --- Token telemetry ---
    telemetry = output.telemetry
    input_tokens = telemetry.get("input_tokens", "n/a")
    output_tokens = telemetry.get("output_tokens", "n/a")
    print(f"[Stage 2a] input_tokens: {input_tokens}")
    print(f"[Stage 2a] output_tokens: {output_tokens}")

    # --- Payload file check ---
    if not dry_run:
        batch_dir = RAW_PAYLOAD_DIR / f"batch_{batch_id}"
        prompt_file = batch_dir / "attempt_0001_prompt.txt"
        response_file = batch_dir / "attempt_0001_response.txt"
        print(f"[Stage 2a] prompt file exists: {prompt_file.exists()}")
        print(f"[Stage 2a] response file exists: {response_file.exists()}")

    # --- Cumulative spend ---
    total_monthly = ledger.monthly_spent_usd(now=datetime.now(timezone.utc))
    print(f"[Stage 2a] cumulative monthly spend: ${total_monthly:.6f}")

    summary = {
        "batch_id": batch_id,
        "dry_run": dry_run,
        "leakage_audit": "clean",
        "estimated_cost_usd": est_cost,
        "actual_cost_usd": actual_cost,
        "cost_delta_usd": actual_cost - est_cost,
        "hypotheses_attempted": state.hypotheses_attempted,
        "lifecycle_counts": dict(state.lifecycle_counts),
        "lifecycle_state": records[0].lifecycle_state if records else None,
        "hypothesis_hash": records[0].hypothesis_hash if records else None,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "invariant_ok": True,
        "cumulative_monthly_spend_usd": total_monthly,
    }
    print(f"\n[Stage 2a] SUMMARY: {json.dumps(summary, indent=2)}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="D6 Stage 2a — single-hypothesis Sonnet smoke run"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use stub backend instead of live Sonnet",
    )
    args = parser.parse_args()
    run_stage2a(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
