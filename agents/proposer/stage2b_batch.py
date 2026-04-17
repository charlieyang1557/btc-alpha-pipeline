"""D6 Stage 2b — 5-hypothesis sequential live observation batch.

Executes five sequential live Sonnet calls through the full pipeline,
observing theme rotation, approved-examples accumulation, and prompt
shape evolution under live API conditions.

Hard constraints enforced:
    - batch_size = 5
    - budget cap = $3 (via BudgetLedger.can_afford)
    - prompt caching DISABLED
    - sequential ordering: call k+1 only after call k fully completes
      (API response → payload write → classify → ingest → ledger
      finalize → approved_so_far update)
    - leakage audit MUST pass before each call
    - approved_examples cap = 3 (most recent first, pending_backtest only)
    - all Stage 1 contracts preserved

Usage:
    python -m agents.proposer.stage2b_batch [--dry-run]

``--dry-run`` uses the stub backend instead of Sonnet.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agents.orchestrator.budget_ledger import BudgetLedger
from agents.orchestrator.ingest import (
    PENDING_BACKTEST,
    BatchIngestState,
    assert_lifecycle_invariant_at_batch_close,
    ingest_output,
)
from agents.proposer.interface import (
    BatchContext,
    ProposerOutput,
    ValidCandidate,
)
from agents.proposer.prompt_builder import (
    audit_prompt_for_leakage,
    build_prompt,
)
from agents.proposer.sonnet_backend import (
    SonnetProposerBackend,
    compute_cost_usd,
)
from agents.proposer.stub_backend import (
    StubProposerBackend,
    _strip_markdown_fence,
)
from agents.themes import THEMES
from factors.registry import FactorRegistry, get_registry


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

STAGE2B_BATCH_SIZE = 5
STAGE2B_BATCH_CAP_USD = 3.0
STAGE2B_MONTHLY_CAP_USD = 100.0
APPROVED_EXAMPLES_CAP = 3
CHARS_PER_TOKEN = 2.9
EST_OUTPUT_TOKENS = 500
RAW_PAYLOAD_DIR = Path("raw_payloads")
LEDGER_PATH = Path("agents/spend_ledger.db")

ALLOWED_OPERATORS = (
    "<", "<=", ">", ">=", "==", "crosses_above", "crosses_below",
)

THEME_FACTORS: dict[str, frozenset[str]] = {
    "momentum": frozenset({
        "return_1h", "return_24h", "return_168h", "rsi_14", "macd_hist",
    }),
    "mean_reversion": frozenset({
        "zscore_48", "bb_upper_24_2", "sma_20", "sma_50", "close",
    }),
    "volatility_regime": frozenset({
        "atr_14", "realized_vol_24h", "bb_upper_24_2",
    }),
    "volume_divergence": frozenset({"volume_zscore_24h"}),
    "calendar_effect": frozenset({"day_of_week", "hour_of_day"}),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


def _estimate_input_tokens(prompt_text: str) -> int:
    """Estimate input tokens from prompt character count.

    Calibrated to Stage 2a observation: 2892 chars → 995 tokens (~2.9
    chars/token). Uses ceiling division for conservative upper bound.
    """
    return max(math.ceil(len(prompt_text) / CHARS_PER_TOKEN), 500)


def _extract_factors(dsl: object) -> set[str]:
    """Extract all factor names referenced in a StrategyDSL."""
    factors: set[str] = set()
    for group in list(dsl.entry) + list(dsl.exit):  # type: ignore[union-attr]
        for cond in group.conditions:
            factors.add(cond.factor)
            if isinstance(cond.value, str):
                factors.add(cond.value)
    return factors


def _classify_theme_adherence(dsl: object, theme: str) -> str:
    """Classify theme adherence: Yes (all factors in theme list),
    Partial (some overlap), No (zero overlap)."""
    theme_factors = THEME_FACTORS.get(theme, frozenset())
    if not theme_factors:
        return "N/A"
    used = _extract_factors(dsl)
    overlap = used & theme_factors
    if not overlap:
        return "No"
    if used <= theme_factors:
        return "Yes"
    return "Partial"


def _classify_cardinality(raw_text: str) -> str:
    """Classify response cardinality after fence stripping."""
    stripped = _strip_markdown_fence(raw_text)
    if not stripped.strip():
        return "zero_objects"
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        if "{" in raw_text or "[" in raw_text:
            return "prose_plus_object"
        return "zero_objects"
    if isinstance(parsed, dict):
        return "single_object"
    if isinstance(parsed, list):
        return f"json_array_{len(parsed)}"
    return "single_object"


def _classify_error(
    lifecycle_state: str, parse_error: str | None,
) -> dict[str, str]:
    """Classify error for the report."""
    if lifecycle_state == PENDING_BACKTEST:
        return {"error_category": "none", "error_signature": "valid"}
    if lifecycle_state == "duplicate":
        return {"error_category": "duplicate_condition",
                "error_signature": "duplicate_hash"}
    if lifecycle_state == "rejected_complexity":
        return {"error_category": "complexity_rejection",
                "error_signature": "over_complex"}
    if lifecycle_state == "backend_empty_output":
        return {"error_category": "backend_empty",
                "error_signature": "empty_response"}
    if parse_error is None:
        return {"error_category": "other", "error_signature": "unknown"}
    pe = parse_error.lower()
    if "json_decode_error" in pe:
        return {"error_category": "json_parse",
                "error_signature": "malformed_json"}
    if any(w in pe for w in ("unknown factor", "not a registered factor")):
        return {"error_category": "frozen_registry_violation",
                "error_signature": "unknown_factor"}
    if "operator" in pe or "op" in pe:
        return {"error_category": "grammar_violation",
                "error_signature": "invalid_operator"}
    if "nan" in pe or "finite" in pe:
        return {"error_category": "non_finite_threshold",
                "error_signature": "non_finite_value"}
    return {
        "error_category": "schema_field_mismatch",
        "error_signature": parse_error[:80].replace(" ", "_").lower(),
        "parse_error_prefix": parse_error[:200],
    }


# ---------------------------------------------------------------------------
# Main batch loop
# ---------------------------------------------------------------------------


def run_stage2b(
    *,
    dry_run: bool = False,
    _backend: object | None = None,
    _ledger_path: Path | None = None,
    _payload_dir: Path | None = None,
) -> dict:
    """Execute the Stage 2b observation batch. Returns a summary dict.

    Parameters prefixed with ``_`` are test injection points; production
    callers should leave them at None.
    """
    _load_dotenv()
    registry = get_registry()
    batch_id = str(uuid.uuid4())
    payload_dir = _payload_dir or RAW_PAYLOAD_DIR
    ledger_path = _ledger_path or LEDGER_PATH

    print(f"[Stage 2b] batch_id={batch_id}")
    print(f"[Stage 2b] dry_run={dry_run}")
    print(f"[Stage 2b] timestamp={datetime.now(timezone.utc).isoformat()}")

    # --- Pre-flight: clear stale pending entries ---
    ledger = BudgetLedger(ledger_path)
    pending = ledger.pending_entries()
    if pending:
        print(f"[Stage 2b] pre-flight: marking {len(pending)} stale "
              f"pending entries as crashed")
        for entry in pending:
            ledger.mark_crashed(
                entry.id,
                now=datetime.now(timezone.utc),
                notes="Stage 2b pre-flight: clearing stale entry "
                      f"from batch {entry.batch_id}",
            )

    # --- Select backend ---
    if _backend is not None:
        backend = _backend
        print("[Stage 2b] backend: injected (test)")
    elif dry_run:
        backend = StubProposerBackend(registry=registry, cost_per_call_usd=0.0)
        print("[Stage 2b] backend: stub (dry-run)")
    else:
        backend = SonnetProposerBackend(
            registry=registry,
            max_retries=3,
            backoff_base_seconds=1.0,
            raw_payload_dir=payload_dir,
        )
        print("[Stage 2b] backend: sonnet (live)")

    # --- Sequential batch loop ---
    state = BatchIngestState(batch_id=batch_id)
    approved_so_far: list[str] = []
    approved_logic_notes: list[str] = []
    call_summaries: list[dict] = []
    factor_usage: dict[str, int] = {}
    truncated_at: int | None = None

    for k in range(1, STAGE2B_BATCH_SIZE + 1):
        theme = THEMES[(k - 1) % len(THEMES)]
        print(f"\n[Stage 2b] --- Call {k}/{STAGE2B_BATCH_SIZE} "
              f"(theme={theme}) ---")

        # D2: build approved_examples (last up-to-3, most recent first)
        examples_for_prompt = tuple(reversed(approved_so_far[-APPROVED_EXAMPLES_CAP:]))
        n_examples = len(examples_for_prompt)

        # Sync backend's approved_examples (Sonnet only)
        if isinstance(backend, SonnetProposerBackend):
            backend.approved_examples = examples_for_prompt

        # Build BatchContext
        now = datetime.now(timezone.utc)
        ctx = BatchContext(
            batch_id=batch_id,
            position=k,
            batch_size=STAGE2B_BATCH_SIZE,
            allowed_factors=tuple(registry.list_names()),
            allowed_operators=ALLOWED_OPERATORS,
            theme_slot=k - 1,
            budget_remaining={
                "batch_usd": ledger.batch_remaining_usd(
                    batch_id, batch_cap_usd=STAGE2B_BATCH_CAP_USD),
                "monthly_usd": ledger.monthly_remaining_usd(
                    now=now, monthly_cap_usd=STAGE2B_MONTHLY_CAP_USD),
            },
        )

        # Build prompt for leakage audit + cost estimation
        prompt = build_prompt(
            ctx, registry=registry, approved_examples=examples_for_prompt,
        )
        leakage_findings = audit_prompt_for_leakage(prompt)
        if leakage_findings:
            print(f"[Stage 2b] ABORT: leakage audit at call {k}: "
                  f"{leakage_findings}")
            sys.exit(1)
        print(f"[Stage 2b] leakage audit: CLEAN")

        # D4: dynamic input-token estimation from actual prompt
        prompt_text = prompt.all_text()
        est_input_tokens = _estimate_input_tokens(prompt_text)
        est_cost = compute_cost_usd(est_input_tokens, EST_OUTPUT_TOKENS)

        # Budget check (pre-call)
        if not ledger.can_afford(
            batch_id=batch_id,
            estimated_cost_usd=est_cost,
            now=now,
            batch_cap_usd=STAGE2B_BATCH_CAP_USD,
            monthly_cap_usd=STAGE2B_MONTHLY_CAP_USD,
        ):
            print(f"[Stage 2b] TRUNCATED at call {k}: cannot afford "
                  f"${est_cost:.6f} (batch spent: "
                  f"${ledger.batch_spent_usd(batch_id):.6f})")
            truncated_at = k
            for j in range(k, STAGE2B_BATCH_SIZE + 1):
                call_summaries.append({
                    "position": j,
                    "theme": THEMES[(j - 1) % len(THEMES)],
                    "truncated_by_cap": True,
                    "lifecycle_state": None,
                    "hypothesis_hash": None,
                    "input_tokens": None,
                    "output_tokens": None,
                    "estimated_cost_usd": None,
                    "actual_cost_usd": None,
                    "approved_examples_count_in_prompt_before_call": None,
                    "theme_adherence": "N/A",
                    "cardinality": "N/A",
                    "retry_count": 0,
                    "error_info": None,
                })
            break

        # Pre-charge ledger
        ledger_row_id = ledger.write_pending(
            batch_id=batch_id,
            api_call_kind="proposer",
            estimated_cost_usd=est_cost,
            now=now,
        )
        print(f"[Stage 2b] pre-charge: ${est_cost:.6f} "
              f"(row {ledger_row_id})")

        # API call
        try:
            output = backend.generate(ctx)
        except Exception as exc:
            ledger.mark_crashed(
                ledger_row_id,
                now=datetime.now(timezone.utc),
                notes=f"generate() raised: {exc}",
            )
            print(f"[Stage 2b] CRASH at call {k}: {exc}")
            raise

        # Finalize ledger with actual cost
        actual_cost = output.cost_actual_usd
        ledger.finalize(
            ledger_row_id,
            actual_cost_usd=actual_cost,
            now=datetime.now(timezone.utc),
        )
        print(f"[Stage 2b] actual_cost: ${actual_cost:.6f} "
              f"(est: ${est_cost:.6f}, "
              f"delta: ${actual_cost - est_cost:.6f})")

        # Ingest into lifecycle
        records = ingest_output(state, output)
        rec = records[0] if records else None
        lifecycle_state = rec.lifecycle_state if rec else "backend_empty_output"
        hypothesis_hash = rec.hypothesis_hash if rec else None
        print(f"[Stage 2b] lifecycle: {lifecycle_state} "
              f"hash={hypothesis_hash}")

        # D2: accumulate approved_so_far (pending_backtest only)
        if lifecycle_state == PENDING_BACKTEST:
            cand = output.candidates[0] if output.candidates else None
            if isinstance(cand, ValidCandidate):
                canonical_json = cand.dsl.model_dump_json()
                approved_so_far.append(canonical_json)
                approved_logic_notes.append(cand.dsl.description)
                # Track factor usage
                for f in _extract_factors(cand.dsl):
                    factor_usage[f] = factor_usage.get(f, 0) + 1
                print(f"[Stage 2b] approved_so_far: {len(approved_so_far)} "
                      f"(added '{cand.dsl.name}')")

        # Extract telemetry
        telemetry = output.telemetry
        input_tokens = telemetry.get("input_tokens")
        output_tokens = telemetry.get("output_tokens")

        # Cardinality: read raw response from disk if available
        cardinality = "n/a"
        prompt_file = (payload_dir / f"batch_{batch_id}"
                       / f"attempt_{k:04d}_prompt.txt")
        response_file = (payload_dir / f"batch_{batch_id}"
                         / f"attempt_{k:04d}_response.txt")
        if response_file.exists():
            raw_text = response_file.read_text(encoding="utf-8")
            cardinality = _classify_cardinality(raw_text)

        # Retry count: count retry files
        batch_dir = payload_dir / f"batch_{batch_id}"
        retry_count = 0
        if batch_dir.exists():
            retry_count = len(list(
                batch_dir.glob(f"attempt_{k:04d}_retry_*_response.txt")
            ))

        # Theme adherence
        theme_adherence = "N/A"
        if lifecycle_state == PENDING_BACKTEST and isinstance(
            output.candidates[0] if output.candidates else None,
            ValidCandidate,
        ):
            theme_adherence = _classify_theme_adherence(
                output.candidates[0].dsl, theme)

        # Error classification
        error_info = None
        if lifecycle_state != PENDING_BACKTEST:
            parse_error = rec.parse_error if rec else None
            error_info = _classify_error(lifecycle_state, parse_error)
            if parse_error:
                error_info["parse_error_prefix"] = parse_error[:200]

        call_summaries.append({
            "position": k,
            "theme": theme,
            "truncated_by_cap": False,
            "lifecycle_state": lifecycle_state,
            "hypothesis_hash": hypothesis_hash,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": est_cost,
            "actual_cost_usd": actual_cost,
            "approved_examples_count_in_prompt_before_call": n_examples,
            "approved_example_logic_notes": (
                list(reversed(approved_logic_notes[-APPROVED_EXAMPLES_CAP:]))
                if n_examples > 0 else []
            ),
            "theme_adherence": theme_adherence,
            "cardinality": cardinality,
            "retry_count": retry_count,
            "error_info": error_info,
            "prompt_file": str(prompt_file),
            "response_file": str(response_file),
            "prompt_file_exists": prompt_file.exists(),
            "response_file_exists": response_file.exists(),
        })

        print(f"[Stage 2b] tokens: in={input_tokens} out={output_tokens}")
        print(f"[Stage 2b] cardinality: {cardinality}")
        print(f"[Stage 2b] theme_adherence: {theme_adherence}")

    # --- Batch close ---
    print(f"\n[Stage 2b] --- Batch close ---")
    assert_lifecycle_invariant_at_batch_close(state)
    print("[Stage 2b] lifecycle invariant: OK")

    # Aggregate telemetry
    attempted_calls = [c for c in call_summaries if not c["truncated_by_cap"]]
    truncated_calls = [c for c in call_summaries if c["truncated_by_cap"]]
    total_est = sum(c["estimated_cost_usd"] for c in attempted_calls
                    if c["estimated_cost_usd"] is not None)
    total_actual = sum(c["actual_cost_usd"] for c in attempted_calls
                       if c["actual_cost_usd"] is not None)
    monthly_spend = ledger.monthly_spent_usd(now=datetime.now(timezone.utc))

    # Lifecycle distribution
    lifecycle_dist = dict(state.lifecycle_counts)

    # Cardinality distribution
    cardinality_dist: dict[str, int] = {}
    for c in attempted_calls:
        card = c.get("cardinality", "n/a")
        cardinality_dist[card] = cardinality_dist.get(card, 0) + 1

    # Theme adherence distribution
    adherence_dist: dict[str, int] = {}
    for c in call_summaries:
        adh = c.get("theme_adherence", "N/A")
        adherence_dist[adh] = adherence_dist.get(adh, 0) + 1

    # Error breakdown
    error_breakdown = []
    for c in attempted_calls:
        if c.get("error_info"):
            error_breakdown.append(c["error_info"])

    # Build summary
    summary = {
        "batch_id": batch_id,
        "dry_run": dry_run,
        "batch_size": STAGE2B_BATCH_SIZE,
        "batch_cap_usd": STAGE2B_BATCH_CAP_USD,
        "hypotheses_attempted": state.hypotheses_attempted,
        "unissued_slots": len(truncated_calls),
        "truncated": truncated_at is not None,
        "truncated_at_call": truncated_at,
        "lifecycle_counts": lifecycle_dist,
        "lifecycle_invariant_ok": True,
        "total_estimated_cost_usd": total_est,
        "total_actual_cost_usd": total_actual,
        "cost_ratio": (total_est / total_actual if total_actual > 0
                       else float("inf")),
        "cumulative_monthly_spend_usd": monthly_spend,
        "factor_usage": factor_usage,
        "cardinality_distribution": cardinality_dist,
        "theme_adherence_distribution": adherence_dist,
        "error_breakdown": error_breakdown,
        "approved_examples_trace": [
            {
                "call_k": c["position"],
                "count_in_prompt": c.get(
                    "approved_examples_count_in_prompt_before_call"),
                "logic_notes": c.get("approved_example_logic_notes", []),
            }
            for c in call_summaries
        ],
        "calls": call_summaries,
    }

    # Write summary JSON
    summary_dir = payload_dir / f"batch_{batch_id}"
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = summary_dir / "stage2b_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"[Stage 2b] summary written: {summary_path}")

    # Console report
    print(f"\n[Stage 2b] SUMMARY:")
    print(f"  batch_id: {batch_id}")
    print(f"  hypotheses_attempted: {state.hypotheses_attempted}")
    print(f"  unissued_slots: {len(truncated_calls)}")
    print(f"  lifecycle: {lifecycle_dist}")
    print(f"  total_est_cost: ${total_est:.6f}")
    print(f"  total_actual_cost: ${total_actual:.6f}")
    if total_actual > 0:
        print(f"  cost_ratio (est/actual): {total_est / total_actual:.2f}x")
    else:
        print("  cost_ratio (est/actual): n/a (zero actual)")
    print(f"  monthly_spend: ${monthly_spend:.6f}")
    print(f"  truncated: {truncated_at is not None}")

    for c in call_summaries:
        trunc = " [TRUNCATED]" if c["truncated_by_cap"] else ""
        print(f"  call {c['position']}: {c['lifecycle_state']} "
              f"hash={c['hypothesis_hash']} "
              f"in={c['input_tokens']} out={c['output_tokens']} "
              f"est=${c.get('estimated_cost_usd', 0) or 0:.6f} "
              f"act=${c.get('actual_cost_usd', 0) or 0:.6f} "
              f"examples={c.get('approved_examples_count_in_prompt_before_call', 0)} "
              f"theme_adh={c['theme_adherence']} "
              f"card={c['cardinality']}{trunc}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="D6 Stage 2b — 5-hypothesis sequential Sonnet batch"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use stub backend instead of live Sonnet",
    )
    args = parser.parse_args()
    run_stage2b(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
