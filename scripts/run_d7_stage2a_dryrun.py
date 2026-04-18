"""D7 Stage 2a — dry-run entrypoint (physical isolation).

Exercises the full D7 Stage 2a pipeline through the stub D7b backend
without making any live API calls. Uses physical isolation:

    - ``dryrun_batch_<uuid>/`` — separate directory for all raw payload
      artifacts (prompt, response, traceback). Never co-mingles with
      production ``raw_payloads/batch_<uuid>/`` trees.
    - ``ledger_dryrun.db`` — separate SQLite ledger. Never touches the
      production ``agents/spend_ledger.db``.

This script can be run unconditionally; it imports ``anthropic`` at module
level only via ``d7b_live`` (which defines the exception taxonomy), but
the stub backend never calls the API.

Usage::

    python -m scripts.run_d7_stage2a_dryrun \\
        --batch-uuid 5cf76668-... --position 102

If the specified batch/position does not exist in ``raw_payloads/``, the
script synthesizes a minimal replay context so the dry-run still
exercises the full wiring path.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agents.critic.batch_context import (
    DEFAULT_MOMENTUM_FACTORS,
    THEME_ANCHOR_FACTORS,
    THEME_HINTS,
    BatchContext,
)
from agents.critic.d7b_stub import StubD7bBackend
from agents.critic.orchestrator import run_critic
from agents.orchestrator.budget_ledger import BudgetLedger


# -----------------------------------------------------------------------
# Synthetic fallback (when real artifacts are absent)
# -----------------------------------------------------------------------

_SYNTHETIC_DSL_DICT = {
    "name": "dryrun_momentum_vol_cross",
    "description": (
        "Dry-run synthetic strategy for Stage 2a wiring validation. "
        "Enters on RSI crossing above SMA with a volatility filter."
    ),
    "entry": [
        {
            "conditions": [
                {
                    "factor": "rsi_14",
                    "op": "crosses_above",
                    "value": 30.0,
                },
                {
                    "factor": "atr_14",
                    "op": ">",
                    "value": 0.03,
                },
                {
                    "factor": "sma_50",
                    "op": ">",
                    "value": "sma_20",
                },
            ],
        },
    ],
    "exit": [
        {
            "conditions": [
                {
                    "factor": "rsi_14",
                    "op": "crosses_below",
                    "value": 70.0,
                },
            ],
        },
    ],
    "position_sizing": "full_equity",
    "max_hold_bars": 168,
}


def _build_synthetic_context(
    position: int,
    theme: str = "volatility",
) -> tuple[object, str, BatchContext]:
    """Build a synthetic (dsl, theme, batch_context) triple for dry-run."""
    from strategies.dsl import StrategyDSL

    dsl = StrategyDSL(**_SYNTHETIC_DSL_DICT)
    ctx = BatchContext(
        prior_factor_sets=(
            ("atr_14", "rsi_14", "sma_20", "sma_50"),
            ("atr_14", "return_24h"),
        ),
        prior_hashes=("abcd1234", "efgh5678"),
        batch_position=position,
        theme_hints=THEME_HINTS,
        default_momentum_factors=DEFAULT_MOMENTUM_FACTORS,
        theme_anchor_factors=THEME_ANCHOR_FACTORS,
    )
    return dsl, theme, ctx


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------


def run_dryrun(
    batch_uuid: str,
    position: int,
    *,
    artifacts_root: Path = Path("raw_payloads"),
    dryrun_root: Path = Path("dryrun_payloads"),
    ledger_path: Path | None = None,
) -> dict:
    """Run the full D7 Stage 2a pipeline through the stub backend.

    Returns the CriticResult as a dict.
    """
    if ledger_path is None:
        ledger_path = dryrun_root / "ledger_dryrun.db"

    dryrun_batch_dir = dryrun_root / f"dryrun_batch_{batch_uuid}"
    dryrun_batch_dir.mkdir(parents=True, exist_ok=True)

    # Attempt real replay; fall back to synthetic.
    try:
        from agents.critic.replay import reconstruct_batch_context_at_position
        dsl, theme, batch_context = reconstruct_batch_context_at_position(
            batch_uuid, position, stage2d_artifacts_root=artifacts_root,
        )
        source = "replay"
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"[dryrun] real artifacts unavailable ({exc}); "
            "using synthetic context",
            file=sys.stderr,
        )
        dsl, theme, batch_context = _build_synthetic_context(position)
        source = "synthetic"

    # Ledger: pre-charge and finalize (stub cost = $0.00).
    ledger = BudgetLedger(ledger_path)
    now = datetime.now(timezone.utc)
    row_id = ledger.write_pending(
        batch_id=batch_uuid,
        api_call_kind="d7b_critic_dryrun",
        backend_kind="d7b_critic",
        call_role="critique",
        estimated_cost_usd=0.0,
        now=now,
        notes=f"Stage 2a dry-run, source={source}",
    )

    # Run critic through the stub backend.
    backend = StubD7bBackend()
    result = run_critic(dsl, theme, batch_context, backend)

    # Finalize ledger with actual cost (0 for stub).
    ledger.finalize(
        row_id,
        actual_cost_usd=result.critic_timing_ms.get("d7b_ms", 0) * 0,
        now=datetime.now(timezone.utc),
    )

    result_dict = result.to_dict()

    # Write result artifact.
    result_path = dryrun_batch_dir / f"dryrun_critic_result_{position:04d}.json"
    result_path.write_text(
        json.dumps(result_dict, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Write summary.
    summary = {
        "batch_uuid": batch_uuid,
        "position": position,
        "source": source,
        "theme": theme,
        "critic_status": result.critic_status,
        "d7b_mode": result.d7b_mode,
        "result_path": str(result_path),
        "ledger_path": str(ledger_path),
        "ledger_row_id": row_id,
    }
    summary_path = dryrun_batch_dir / "dryrun_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return result_dict


def main() -> None:
    parser = argparse.ArgumentParser(
        description="D7 Stage 2a dry-run: stub backend, physically isolated.",
    )
    parser.add_argument(
        "--batch-uuid",
        default=str(uuid.uuid4()),
        help="Batch UUID to use (default: fresh UUID).",
    )
    parser.add_argument(
        "--position",
        type=int,
        default=102,
        help="Replay position within the batch (default: 102).",
    )
    parser.add_argument(
        "--artifacts-root",
        type=Path,
        default=Path("raw_payloads"),
        help="Root directory for Stage 2d artifacts.",
    )
    parser.add_argument(
        "--dryrun-root",
        type=Path,
        default=Path("dryrun_payloads"),
        help="Root directory for dry-run artifacts (physically isolated).",
    )
    args = parser.parse_args()

    print(f"[dryrun] batch={args.batch_uuid}, position={args.position}")
    result = run_dryrun(
        args.batch_uuid,
        args.position,
        artifacts_root=args.artifacts_root,
        dryrun_root=args.dryrun_root,
    )

    print(f"[dryrun] critic_status={result['critic_status']}, "
          f"d7b_mode={result['d7b_mode']}")
    print(f"[dryrun] d7a_rule_scores={result['d7a_rule_scores']}")
    print(f"[dryrun] d7b_llm_scores={result['d7b_llm_scores']}")
    print("[dryrun] dry-run complete.")


if __name__ == "__main__":
    main()
