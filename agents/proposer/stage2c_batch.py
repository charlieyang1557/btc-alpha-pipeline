"""D6 Stage 2c — 20-hypothesis sequential live observation batch.

Scales Stage 2b 4x (N=20) to produce the first statistically interpretable
parse-rate and lifecycle distribution. Each of the 5 themes (momentum,
mean_reversion, volatility_regime, volume_divergence, calendar_effect)
gets exactly 4 calls via interleaved-cyclic rotation
(``theme_slot = (k - 1) % 5``).

Hard constraints enforced:
    - batch_size = 20
    - budget cap = $6 (via BudgetLedger.can_afford)
    - prompt caching DISABLED
    - sequential ordering: call k+1 only after call k fully completes
      (API response → payload write → classify → ingest → ledger
      finalize → approved_so_far update)
    - leakage audit MUST pass before each call
    - approved_examples cap = 3 (most recent first, pending_backtest only)
    - all Stage 1/2a/2b contracts preserved

Catastrophic stop conditions (evaluated post-finalize for each call):
    - Early parse-rate stop: valid/issued < 0.5 for k ≥ 5
    - Per-theme single-mode failure: theme has 4 issued calls all with
      identical (error_category, error_signature)
    - Cardinality violation count > 2
    - Cumulative Stage-2 monthly spend > $30

CONTRACT BOUNDARY: THEME_HINTS below is used ONLY for post-hoc telemetry
(overlap counts, dominant factors). It MUST NOT be referenced in prompt
construction, candidate validation, lifecycle classification, ingest
rules, or any acceptance logic.

Usage:
    python -m agents.proposer.stage2c_batch [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agents.orchestrator.budget_ledger import BudgetLedger
from agents.orchestrator.ingest import (
    BACKEND_EMPTY_OUTPUT,
    DUPLICATE,
    INVALID_DSL,
    PENDING_BACKTEST,
    REJECTED_COMPLEXITY,
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
from factors.registry import get_registry


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

STAGE_LABEL = "D6_STAGE2C"
MODEL_NAME = "claude-sonnet-4-5"
PROMPT_CACHING_ENABLED = False
STAGE2C_BATCH_SIZE = 20
STAGE2C_BATCH_CAP_USD = 6.0
STAGE2C_MONTHLY_CAP_USD = 100.0
STAGE2C_CUMULATIVE_CAP_USD = 30.0  # catastrophic stop threshold
APPROVED_EXAMPLES_CAP = 3
THEME_ROTATION_MODE = "interleaved_cyclic"
THEME_CYCLE_LEN = 5  # first 5 THEMES; multi_factor_combination excluded
CHARS_PER_TOKEN = 2.9
EST_OUTPUT_TOKENS = 500
PARSE_RATE_THRESHOLD = 0.5
PARSE_RATE_MIN_K = 5
CARDINALITY_VIOLATION_STOP = 2  # stop if count EXCEEDS this
NARROW_FACTOR_VOCAB_THRESHOLD = 5  # first 10 calls
RSI14_COLLAPSE_THRESHOLD = 8  # first 10 calls
RAW_PAYLOAD_DIR = Path("raw_payloads")
LEDGER_PATH = Path("agents/spend_ledger.db")

ALLOWED_OPERATORS = (
    "<", "<=", ">", ">=", "==", "crosses_above", "crosses_below",
)

# CONTRACT BOUNDARY: post-hoc telemetry only. Never touched by prompt
# builder, ingest, or validation. Mirror of the mapping in the Stage 2c
# launch prompt (Deliverable 5 §Theme-to-factor hint mapping).
THEME_HINTS: dict[str, frozenset[str]] = {
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

DEFAULT_MOMENTUM_FACTORS: frozenset[str] = frozenset({
    "rsi_14", "return_1h", "return_24h", "macd_hist",
})

# Derived literal for reporting clarity (lifecycle_state is source of truth).
VALID_STATUS_VALID = "valid"
VALID_STATUS_INVALID_SCHEMA = "invalid_schema"
VALID_STATUS_INVALID_DUPLICATE = "invalid_duplicate"
VALID_STATUS_BACKEND_EMPTY = "backend_empty"
VALID_STATUS_TRUNCATED = "truncated_by_cap"


def _git_commit_short() -> str:
    """Return short git HEAD hash, or ``"unknown"`` if unavailable."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True, timeout=5,
        )
        return out.stdout.strip() or "unknown"
    except (subprocess.CalledProcessError, FileNotFoundError,
            subprocess.TimeoutExpired):
        return "unknown"


def _theme_for_position(k: int) -> str:
    """Interleaved cyclic theme rotation: theme_slot = (k - 1) % 5."""
    return THEMES[(k - 1) % THEME_CYCLE_LEN]


# ---------------------------------------------------------------------------
# Helpers (reused from Stage 2b; duplicated here so Stage 2c owns its surface)
# ---------------------------------------------------------------------------


def _load_dotenv(path: Path | None = None) -> None:
    """Load .env file into os.environ (stdlib-only)."""
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
    """Dynamic input-token estimate from assembled prompt string."""
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


def _is_cardinality_violation(cardinality: str) -> bool:
    """True iff cardinality is a structural repeat (not single_object)."""
    if cardinality == "single_object":
        return False
    if cardinality == "n/a":
        return False
    # json_array_N, prose_plus_object, zero_objects → violation
    return True


def _valid_status_from_lifecycle(
    lifecycle_state: str | None, *, truncated: bool
) -> str:
    """Derive the reporting-layer ``valid_status`` literal."""
    if truncated:
        return VALID_STATUS_TRUNCATED
    if lifecycle_state == PENDING_BACKTEST:
        return VALID_STATUS_VALID
    if lifecycle_state in (INVALID_DSL, REJECTED_COMPLEXITY):
        return VALID_STATUS_INVALID_SCHEMA
    if lifecycle_state == DUPLICATE:
        return VALID_STATUS_INVALID_DUPLICATE
    if lifecycle_state == BACKEND_EMPTY_OUTPUT:
        return VALID_STATUS_BACKEND_EMPTY
    # Unknown lifecycle — treat as schema failure defensively.
    return VALID_STATUS_INVALID_SCHEMA


def _classify_error(
    lifecycle_state: str, parse_error: str | None,
) -> dict[str, str | None]:
    """Map (lifecycle_state, parse_error) to (error_category, error_signature).

    Returns a dict with keys ``error_category`` and ``error_signature``.
    Values are ``None`` when the call is valid (pending_backtest).
    """
    if lifecycle_state == PENDING_BACKTEST:
        return {"error_category": None, "error_signature": None}
    if lifecycle_state == DUPLICATE:
        return {"error_category": "duplicate_condition",
                "error_signature": "duplicate_hash"}
    if lifecycle_state == REJECTED_COMPLEXITY:
        return {"error_category": "complexity_rejection",
                "error_signature": "over_complex"}
    if lifecycle_state == BACKEND_EMPTY_OUTPUT:
        return {"error_category": "backend_empty",
                "error_signature": "empty_response"}
    if parse_error is None:
        return {"error_category": "other", "error_signature": "unknown"}
    pe = parse_error.lower()
    if "json_decode_error" in pe or "expecting value" in pe:
        return {"error_category": "json_parse",
                "error_signature": "malformed_json"}
    if any(w in pe for w in ("unknown factor", "not a registered factor")):
        return {"error_category": "frozen_registry_violation",
                "error_signature": "unknown_factor"}
    if "operator" in pe:
        return {"error_category": "grammar_violation",
                "error_signature": "invalid_operator"}
    if "nan" in pe or "finite" in pe or "infinite" in pe:
        return {"error_category": "non_finite_threshold",
                "error_signature": "non_finite_value"}
    # Default bucket: schema field mismatch. Take a short signature from the
    # first line of the parse error so Sonnet's observed synonyms
    # (e.g., "missing_name_field") become visible in aggregates.
    first_line = parse_error.splitlines()[0] if parse_error else ""
    signature = first_line[:80].replace(" ", "_").lower() or "schema_error"
    return {
        "error_category": "schema_field_mismatch",
        "error_signature": signature,
    }


def _extract_name_from_dsl_json(dsl_json: str) -> str:
    """Pull the ``name`` field out of a normalized DSL JSON string.

    Reporting-only. Returns ``"<unknown>"`` if the JSON is malformed or
    the field is missing (should never happen for approved DSLs, but we
    never crash the reporter).
    """
    try:
        parsed = json.loads(dsl_json)
    except (TypeError, json.JSONDecodeError):
        return "<unknown>"
    if not isinstance(parsed, dict):
        return "<unknown>"
    name = parsed.get("name")
    return name if isinstance(name, str) else "<unknown>"


def _extract_description_from_dsl_json(dsl_json: str) -> str:
    """Pull the ``description`` field out of a normalized DSL JSON string.

    Mechanical extraction ONLY. Per the Stage 2c launch prompt: do NOT
    summarize, rephrase, paraphrase, or interpret this text.
    """
    try:
        parsed = json.loads(dsl_json)
    except (TypeError, json.JSONDecodeError):
        return ""
    if not isinstance(parsed, dict):
        return ""
    desc = parsed.get("description", "")
    return desc if isinstance(desc, str) else ""


def _build_per_call_telemetry(
    dsl: object | None, theme: str,
) -> dict[str, object]:
    """Compute the Stage-2c expanded telemetry fields for one call.

    For invalid calls (``dsl is None``):
        factors_used=[], overlap_count=0, overlap_ratio=None,
        out_of_theme_factor_count=0,
        contains_default_momentum_factor=False,
        default_momentum_factors_used=[]
    """
    if dsl is None:
        return {
            "factors_used": [],
            "overlap_count": 0,
            "overlap_ratio": None,
            "out_of_theme_factor_count": 0,
            "contains_default_momentum_factor": False,
            "default_momentum_factors_used": [],
        }
    factors = _extract_factors(dsl)
    factors_sorted = sorted(factors)
    theme_hints = THEME_HINTS.get(theme, frozenset())
    overlap = factors & theme_hints
    overlap_count = len(overlap)
    total = len(factors_sorted)
    overlap_ratio = (overlap_count / total) if total > 0 else None
    out_of_theme = total - overlap_count
    default_hits = sorted(factors & DEFAULT_MOMENTUM_FACTORS)
    return {
        "factors_used": factors_sorted,
        "overlap_count": overlap_count,
        "overlap_ratio": overlap_ratio,
        "out_of_theme_factor_count": out_of_theme,
        "contains_default_momentum_factor": bool(default_hits),
        "default_momentum_factors_used": default_hits,
    }


def _aggregate_per_theme(
    calls: list[dict], theme: str,
) -> dict[str, object]:
    """Compute the per-theme aggregate row for one theme."""
    theme_calls = [
        c for c in calls
        if c.get("theme") == theme and not c.get("truncated_by_cap")
    ]
    n_calls = len(theme_calls)
    if n_calls == 0:
        return {
            "theme": theme,
            "n_calls": 0,
            "valid_count": 0,
            "lifecycle_mix": {},
            "avg_overlap_count": None,
            "avg_overlap_ratio": None,
            "avg_out_of_theme_factors": None,
            "contains_rsi14_count": 0,
            "contains_momentum_default_count": 0,
            "dominant_factors_top3": [],
        }

    valid_calls = [
        c for c in theme_calls if c.get("lifecycle_state") == PENDING_BACKTEST
    ]
    valid_count = len(valid_calls)

    lifecycle_mix: dict[str, int] = {}
    for c in theme_calls:
        ls = c.get("lifecycle_state") or "unknown"
        lifecycle_mix[ls] = lifecycle_mix.get(ls, 0) + 1

    # Averages over VALID calls only (overlap metrics are undefined for
    # invalid DSLs which have factors_used=[]).
    if valid_count > 0:
        avg_overlap_count = sum(
            c.get("overlap_count", 0) for c in valid_calls
        ) / valid_count
        ratios = [
            c["overlap_ratio"] for c in valid_calls
            if c.get("overlap_ratio") is not None
        ]
        avg_overlap_ratio = (sum(ratios) / len(ratios)) if ratios else None
        avg_out_of_theme = sum(
            c.get("out_of_theme_factor_count", 0) for c in valid_calls
        ) / valid_count
    else:
        avg_overlap_count = None
        avg_overlap_ratio = None
        avg_out_of_theme = None

    contains_rsi14_count = sum(
        1 for c in valid_calls if "rsi_14" in c.get("factors_used", [])
    )
    contains_momentum_default_count = sum(
        1 for c in valid_calls if c.get("contains_default_momentum_factor")
    )

    # Dominant factors top 3 (descending by count, tie-break ascending name).
    factor_counts: dict[str, int] = {}
    for c in valid_calls:
        for f in c.get("factors_used", []):
            factor_counts[f] = factor_counts.get(f, 0) + 1
    sorted_factors = sorted(
        factor_counts.items(), key=lambda kv: (-kv[1], kv[0])
    )
    dominant_top3 = [f for f, _ in sorted_factors[:3]]

    return {
        "theme": theme,
        "n_calls": n_calls,
        "valid_count": valid_count,
        "lifecycle_mix": lifecycle_mix,
        "avg_overlap_count": avg_overlap_count,
        "avg_overlap_ratio": avg_overlap_ratio,
        "avg_out_of_theme_factors": avg_out_of_theme,
        "contains_rsi14_count": contains_rsi14_count,
        "contains_momentum_default_count": contains_momentum_default_count,
        "dominant_factors_top3": dominant_top3,
    }


def _check_single_mode_failure(
    calls: list[dict], theme: str,
) -> tuple[bool, str | None, str | None]:
    """Check whether a theme shows single-mode failure across its 4 calls.

    Returns (triggered, error_category, error_signature). Triggered iff
    the theme has exactly 4 NON-truncated calls AND all 4 are invalid
    (lifecycle != pending_backtest) AND share identical error_category
    AND identical error_signature.
    """
    theme_calls = [
        c for c in calls
        if c.get("theme") == theme and not c.get("truncated_by_cap")
    ]
    if len(theme_calls) < 4:
        return False, None, None
    # All 4 must be invalid.
    if any(c.get("lifecycle_state") == PENDING_BACKTEST for c in theme_calls):
        return False, None, None
    sigs = set()
    cats = set()
    for c in theme_calls:
        err = c.get("error_info") or {}
        cats.add(err.get("error_category"))
        sigs.add(err.get("error_signature"))
    if len(cats) == 1 and len(sigs) == 1:
        (cat,) = cats
        (sig,) = sigs
        if cat is None or sig is None:
            return False, None, None
        return True, cat, sig
    return False, None, None


# ---------------------------------------------------------------------------
# Main batch loop
# ---------------------------------------------------------------------------


def run_stage2c(
    *,
    dry_run: bool = False,
    _backend: object | None = None,
    _ledger_path: Path | None = None,
    _payload_dir: Path | None = None,
) -> dict:
    """Execute the Stage 2c 20-hypothesis observation batch.

    Returns a summary dict. Parameters prefixed with ``_`` are test
    injection points; production callers should leave them at None.
    """
    _load_dotenv()
    registry = get_registry()
    batch_id = str(uuid.uuid4())
    payload_dir = _payload_dir or RAW_PAYLOAD_DIR
    ledger_path = _ledger_path or LEDGER_PATH
    run_timestamp_utc = datetime.now(timezone.utc).isoformat()

    print(f"[Stage 2c] batch_id={batch_id}")
    print(f"[Stage 2c] dry_run={dry_run}")
    print(f"[Stage 2c] timestamp={run_timestamp_utc}")
    print(f"[Stage 2c] batch_size={STAGE2C_BATCH_SIZE} "
          f"cap=${STAGE2C_BATCH_CAP_USD}")
    print(f"[Stage 2c] theme_rotation={THEME_ROTATION_MODE} "
          f"cycle_len={THEME_CYCLE_LEN}")

    # --- Pre-flight: clear stale pending entries ---
    ledger = BudgetLedger(ledger_path)
    pending = ledger.pending_entries()
    if pending:
        print(f"[Stage 2c] pre-flight: marking {len(pending)} stale "
              f"pending entries as crashed")
        for entry in pending:
            ledger.mark_crashed(
                entry.id,
                now=datetime.now(timezone.utc),
                notes="Stage 2c pre-flight: clearing stale entry "
                      f"from batch {entry.batch_id}",
            )

    # --- Select backend ---
    if _backend is not None:
        backend = _backend
        print("[Stage 2c] backend: injected (test)")
    elif dry_run:
        backend = StubProposerBackend(registry=registry, cost_per_call_usd=0.0)
        print("[Stage 2c] backend: stub (dry-run)")
    else:
        backend = SonnetProposerBackend(
            registry=registry,
            max_retries=3,
            backoff_base_seconds=1.0,
            raw_payload_dir=payload_dir,
        )
        print("[Stage 2c] backend: sonnet (live)")

    # --- Per-batch running state ---
    state = BatchIngestState(batch_id=batch_id)
    approved_so_far: list[str] = []
    approved_logic_notes: list[str] = []
    approved_names: list[str] = []
    call_summaries: list[dict] = []
    factor_usage: dict[str, int] = {}
    truncated_at: int | None = None
    cardinality_violation_count = 0
    early_stop_reason: str | None = None
    early_stop_detail: dict | None = None
    git_commit = _git_commit_short()

    # --- Sequential call loop ---
    for k in range(1, STAGE2C_BATCH_SIZE + 1):
        theme = _theme_for_position(k)
        print(f"\n[Stage 2c] --- Call {k}/{STAGE2C_BATCH_SIZE} "
              f"(theme={theme}) ---")

        # approved_examples: last up-to-3, most recent first
        examples_for_prompt = tuple(
            reversed(approved_so_far[-APPROVED_EXAMPLES_CAP:])
        )
        names_for_prompt = list(
            reversed(approved_names[-APPROVED_EXAMPLES_CAP:])
        )
        logic_for_prompt = list(
            reversed(approved_logic_notes[-APPROVED_EXAMPLES_CAP:])
        )
        n_examples = len(examples_for_prompt)

        # Sync backend approved_examples (Sonnet only)
        if isinstance(backend, SonnetProposerBackend):
            backend.approved_examples = examples_for_prompt

        # Build BatchContext
        now = datetime.now(timezone.utc)
        ctx = BatchContext(
            batch_id=batch_id,
            position=k,
            batch_size=STAGE2C_BATCH_SIZE,
            allowed_factors=tuple(registry.list_names()),
            allowed_operators=ALLOWED_OPERATORS,
            theme_slot=(k - 1) % THEME_CYCLE_LEN,
            budget_remaining={
                "batch_usd": ledger.batch_remaining_usd(
                    batch_id, batch_cap_usd=STAGE2C_BATCH_CAP_USD),
                "monthly_usd": ledger.monthly_remaining_usd(
                    now=now, monthly_cap_usd=STAGE2C_MONTHLY_CAP_USD),
            },
        )

        # Build prompt (for leakage audit + token estimation)
        prompt = build_prompt(
            ctx, registry=registry, approved_examples=examples_for_prompt,
        )
        leakage_findings = audit_prompt_for_leakage(prompt)
        if leakage_findings:
            print(f"[Stage 2c] ABORT: leakage audit at call {k}: "
                  f"{leakage_findings}")
            sys.exit(1)
        print(f"[Stage 2c] leakage audit: CLEAN")

        # Dynamic input-token estimate
        prompt_text = prompt.all_text()
        est_input_tokens = _estimate_input_tokens(prompt_text)
        est_cost = compute_cost_usd(est_input_tokens, EST_OUTPUT_TOKENS)

        # Cumulative Stage-2 monthly-spend catastrophic stop (pre-call).
        current_monthly = ledger.monthly_spent_usd(now=now)
        if current_monthly + est_cost > STAGE2C_CUMULATIVE_CAP_USD:
            early_stop_reason = "cumulative_stage2_spend_exceeded"
            early_stop_detail = {
                "at_call": k,
                "current_monthly_usd": current_monthly,
                "next_call_estimate_usd": est_cost,
                "cumulative_cap_usd": STAGE2C_CUMULATIVE_CAP_USD,
            }
            print(f"[Stage 2c] EARLY STOP: cumulative Stage-2 spend "
                  f"${current_monthly:.6f} + est ${est_cost:.6f} "
                  f"would exceed cap ${STAGE2C_CUMULATIVE_CAP_USD}")
            truncated_at = k
            for j in range(k, STAGE2C_BATCH_SIZE + 1):
                t_j = _theme_for_position(j)
                call_summaries.append({
                    "position": j, "theme": t_j, "truncated_by_cap": True,
                    "lifecycle_state": None, "hypothesis_hash": None,
                    "input_tokens": None, "output_tokens": None,
                    "estimated_cost_usd": None, "actual_cost_usd": None,
                    "approved_examples_count_in_prompt_before_call": None,
                    "approved_example_names_before_call": [],
                    "approved_example_logic_notes": [],
                    "cardinality": "n/a",
                    "retry_count": 0, "error_info": None,
                    "factors_used": [], "overlap_count": 0,
                    "overlap_ratio": None, "out_of_theme_factor_count": 0,
                    "contains_default_momentum_factor": False,
                    "default_momentum_factors_used": [],
                    "valid_status": VALID_STATUS_TRUNCATED,
                })
            break

        # Budget check (batch + monthly caps)
        if not ledger.can_afford(
            batch_id=batch_id,
            estimated_cost_usd=est_cost,
            now=now,
            batch_cap_usd=STAGE2C_BATCH_CAP_USD,
            monthly_cap_usd=STAGE2C_MONTHLY_CAP_USD,
        ):
            print(f"[Stage 2c] TRUNCATED at call {k}: cannot afford "
                  f"${est_cost:.6f} (batch spent: "
                  f"${ledger.batch_spent_usd(batch_id):.6f})")
            truncated_at = k
            for j in range(k, STAGE2C_BATCH_SIZE + 1):
                t_j = _theme_for_position(j)
                call_summaries.append({
                    "position": j, "theme": t_j, "truncated_by_cap": True,
                    "lifecycle_state": None, "hypothesis_hash": None,
                    "input_tokens": None, "output_tokens": None,
                    "estimated_cost_usd": None, "actual_cost_usd": None,
                    "approved_examples_count_in_prompt_before_call": None,
                    "approved_example_names_before_call": [],
                    "approved_example_logic_notes": [],
                    "cardinality": "n/a",
                    "retry_count": 0, "error_info": None,
                    "factors_used": [], "overlap_count": 0,
                    "overlap_ratio": None, "out_of_theme_factor_count": 0,
                    "contains_default_momentum_factor": False,
                    "default_momentum_factors_used": [],
                    "valid_status": VALID_STATUS_TRUNCATED,
                })
            break

        # Pre-charge ledger
        ledger_row_id = ledger.write_pending(
            batch_id=batch_id,
            api_call_kind="proposer",
            backend_kind="d6_proposer",
            call_role="propose",
            estimated_cost_usd=est_cost,
            now=now,
        )
        print(f"[Stage 2c] pre-charge: ${est_cost:.6f} (row {ledger_row_id})")

        # API call (exceptions are infra-level; surface them)
        try:
            output = backend.generate(ctx)
        except Exception as exc:
            ledger.mark_crashed(
                ledger_row_id,
                now=datetime.now(timezone.utc),
                notes=f"generate() raised: {exc}",
            )
            print(f"[Stage 2c] CRASH at call {k}: {exc}")
            raise

        # Finalize ledger with actual cost
        actual_cost = output.cost_actual_usd
        ledger.finalize(
            ledger_row_id,
            actual_cost_usd=actual_cost,
            now=datetime.now(timezone.utc),
        )
        print(f"[Stage 2c] actual_cost: ${actual_cost:.6f} "
              f"(est: ${est_cost:.6f}, "
              f"delta: ${actual_cost - est_cost:.6f})")

        # Ingest into lifecycle
        records = ingest_output(state, output)
        rec = records[0] if records else None
        lifecycle_state = (
            rec.lifecycle_state if rec else BACKEND_EMPTY_OUTPUT
        )
        hypothesis_hash = rec.hypothesis_hash if rec else None
        print(f"[Stage 2c] lifecycle: {lifecycle_state} "
              f"hash={hypothesis_hash}")

        # Accumulate approved_so_far (pending_backtest only)
        cand = output.candidates[0] if output.candidates else None
        if lifecycle_state == PENDING_BACKTEST and isinstance(
            cand, ValidCandidate
        ):
            canonical_json = cand.dsl.model_dump_json()
            approved_so_far.append(canonical_json)
            approved_logic_notes.append(cand.dsl.description)
            approved_names.append(cand.dsl.name)
            for f in _extract_factors(cand.dsl):
                factor_usage[f] = factor_usage.get(f, 0) + 1
            print(f"[Stage 2c] approved_so_far: {len(approved_so_far)} "
                  f"(added '{cand.dsl.name}')")

        # Backend telemetry
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

        if _is_cardinality_violation(cardinality):
            cardinality_violation_count += 1

        # Retry count (count retry files)
        batch_dir = payload_dir / f"batch_{batch_id}"
        retry_count = 0
        if batch_dir.exists():
            retry_count = len(list(
                batch_dir.glob(f"attempt_{k:04d}_retry_*_response.txt")
            ))

        # Per-call telemetry (overlap, theme, default-momentum)
        dsl_for_tel = cand.dsl if (
            lifecycle_state == PENDING_BACKTEST and isinstance(
                cand, ValidCandidate)
        ) else None
        per_call_tel = _build_per_call_telemetry(dsl_for_tel, theme)

        # Error classification (None for valid)
        parse_error = rec.parse_error if rec else None
        error_info = _classify_error(lifecycle_state, parse_error)
        if parse_error:
            error_info = dict(error_info)
            error_info["parse_error_prefix"] = parse_error[:200]
        # For valid calls, drop the None keys so consumers don't see them.
        if lifecycle_state == PENDING_BACKTEST:
            error_info = None

        valid_status = _valid_status_from_lifecycle(
            lifecycle_state, truncated=False,
        )

        call_summaries.append({
            "position": k,
            "theme": theme,
            "truncated_by_cap": False,
            "lifecycle_state": lifecycle_state,
            "valid_status": valid_status,
            "hypothesis_hash": hypothesis_hash,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": est_cost,
            "actual_cost_usd": actual_cost,
            "approved_examples_count_in_prompt_before_call": n_examples,
            "approved_example_names_before_call": names_for_prompt,
            "approved_example_logic_notes": logic_for_prompt,
            "cardinality": cardinality,
            "retry_count": retry_count,
            "error_info": error_info,
            "factors_used": per_call_tel["factors_used"],
            "overlap_count": per_call_tel["overlap_count"],
            "overlap_ratio": per_call_tel["overlap_ratio"],
            "out_of_theme_factor_count":
                per_call_tel["out_of_theme_factor_count"],
            "contains_default_momentum_factor":
                per_call_tel["contains_default_momentum_factor"],
            "default_momentum_factors_used":
                per_call_tel["default_momentum_factors_used"],
            "prompt_file": str(prompt_file),
            "response_file": str(response_file),
            "prompt_file_exists": prompt_file.exists(),
            "response_file_exists": response_file.exists(),
        })

        print(f"[Stage 2c] tokens: in={input_tokens} out={output_tokens}")
        print(f"[Stage 2c] cardinality: {cardinality} "
              f"violations_so_far={cardinality_violation_count}")
        print(f"[Stage 2c] overlap: {per_call_tel['overlap_count']}/"
              f"{len(per_call_tel['factors_used'])} "
              f"oot={per_call_tel['out_of_theme_factor_count']}")

        # --- Catastrophic stop checks (post-finalize) ---

        # Early parse-rate stop (only evaluated once k >= 5).
        issued_so_far = [c for c in call_summaries
                         if not c.get("truncated_by_cap")]
        if len(issued_so_far) >= PARSE_RATE_MIN_K:
            valid_so_far = sum(
                1 for c in issued_so_far
                if c.get("lifecycle_state") == PENDING_BACKTEST
            )
            parse_rate = valid_so_far / len(issued_so_far)
            if parse_rate < PARSE_RATE_THRESHOLD:
                early_stop_reason = "parse_rate_below_threshold"
                early_stop_detail = {
                    "at_call": k,
                    "issued": len(issued_so_far),
                    "valid": valid_so_far,
                    "parse_rate": parse_rate,
                    "threshold": PARSE_RATE_THRESHOLD,
                }
                print(f"[Stage 2c] EARLY STOP: parse_rate={parse_rate:.3f} "
                      f"< {PARSE_RATE_THRESHOLD} at k={k}")

        # Cardinality violation stop (count > 2).
        if (early_stop_reason is None
                and cardinality_violation_count > CARDINALITY_VIOLATION_STOP):
            early_stop_reason = "cardinality_violation_count_exceeded"
            early_stop_detail = {
                "at_call": k,
                "violation_count": cardinality_violation_count,
                "threshold": CARDINALITY_VIOLATION_STOP,
            }
            print(f"[Stage 2c] EARLY STOP: cardinality violations "
                  f"{cardinality_violation_count} > "
                  f"{CARDINALITY_VIOLATION_STOP} at k={k}")

        # Per-theme single-mode failure (only possible after theme has 4
        # non-truncated calls; fires as soon as the 4th call lands).
        if early_stop_reason is None:
            for t in list(THEMES)[:THEME_CYCLE_LEN]:
                triggered, cat, sig = _check_single_mode_failure(
                    call_summaries, t,
                )
                if triggered:
                    early_stop_reason = "per_theme_single_mode_failure"
                    early_stop_detail = {
                        "at_call": k,
                        "theme": t,
                        "error_category": cat,
                        "error_signature": sig,
                    }
                    print(f"[Stage 2c] EARLY STOP: theme '{t}' shows "
                          f"single-mode failure ({cat}/{sig}) at k={k}")
                    break

        # If any stop fired, mark remaining slots truncated and break.
        if early_stop_reason is not None:
            truncated_at = k + 1 if k < STAGE2C_BATCH_SIZE else None
            for j in range(k + 1, STAGE2C_BATCH_SIZE + 1):
                t_j = _theme_for_position(j)
                call_summaries.append({
                    "position": j, "theme": t_j, "truncated_by_cap": True,
                    "lifecycle_state": None, "hypothesis_hash": None,
                    "input_tokens": None, "output_tokens": None,
                    "estimated_cost_usd": None, "actual_cost_usd": None,
                    "approved_examples_count_in_prompt_before_call": None,
                    "approved_example_names_before_call": [],
                    "approved_example_logic_notes": [],
                    "cardinality": "n/a",
                    "retry_count": 0, "error_info": None,
                    "factors_used": [], "overlap_count": 0,
                    "overlap_ratio": None, "out_of_theme_factor_count": 0,
                    "contains_default_momentum_factor": False,
                    "default_momentum_factors_used": [],
                    "valid_status": VALID_STATUS_TRUNCATED,
                })
            break

    # --- Batch close ---
    print(f"\n[Stage 2c] --- Batch close ---")
    assert_lifecycle_invariant_at_batch_close(state)
    print("[Stage 2c] lifecycle invariant: OK")

    attempted_calls = [c for c in call_summaries if not c["truncated_by_cap"]]
    truncated_calls = [c for c in call_summaries if c["truncated_by_cap"]]
    total_est = sum(
        c["estimated_cost_usd"] for c in attempted_calls
        if c["estimated_cost_usd"] is not None
    )
    total_actual = sum(
        c["actual_cost_usd"] for c in attempted_calls
        if c["actual_cost_usd"] is not None
    )
    monthly_spend = ledger.monthly_spent_usd(now=datetime.now(timezone.utc))

    # Lifecycle distribution from ingest state (source of truth).
    lifecycle_dist = dict(state.lifecycle_counts)

    # Cardinality distribution across attempted calls.
    cardinality_dist: dict[str, int] = {}
    for c in attempted_calls:
        card = c.get("cardinality", "n/a")
        cardinality_dist[card] = cardinality_dist.get(card, 0) + 1

    # Error breakdown (list of per-call error_info for invalid attempts).
    error_breakdown = [
        c["error_info"] for c in attempted_calls if c.get("error_info")
    ]

    # Per-theme aggregates (all 5 themes, even if 0 calls).
    per_theme_rows = [
        _aggregate_per_theme(call_summaries, t)
        for t in list(THEMES)[:THEME_CYCLE_LEN]
    ]

    # Parse rate across attempted calls (for headline).
    valid_attempted = sum(
        1 for c in attempted_calls
        if c.get("lifecycle_state") == PENDING_BACKTEST
    )
    parse_rate = (
        valid_attempted / len(attempted_calls)
        if attempted_calls else None
    )

    # --- Anomaly log (narrow factor vocab, rsi_14 collapse) ---
    anomaly_flags: list[dict] = []
    first10_valid = [
        c for c in attempted_calls[:10]
        if c.get("lifecycle_state") == PENDING_BACKTEST
    ]
    vocab: set[str] = set()
    for c in first10_valid:
        vocab.update(c.get("factors_used", []))
    if first10_valid and len(vocab) < NARROW_FACTOR_VOCAB_THRESHOLD:
        anomaly_flags.append({
            "kind": "narrow_factor_vocab",
            "scope": "first_10_calls",
            "unique_factors": sorted(vocab),
            "count": len(vocab),
            "threshold": NARROW_FACTOR_VOCAB_THRESHOLD,
        })
    rsi14_first10 = sum(
        1 for c in first10_valid if "rsi_14" in c.get("factors_used", [])
    )
    if rsi14_first10 >= RSI14_COLLAPSE_THRESHOLD:
        anomaly_flags.append({
            "kind": "rsi_14_collapse",
            "scope": "first_10_calls",
            "count": rsi14_first10,
            "threshold": RSI14_COLLAPSE_THRESHOLD,
        })

    # --- Summary JSON ---
    summary = {
        "config": {
            "stage_label": STAGE_LABEL,
            "model_name": MODEL_NAME,
            "prompt_caching_enabled": PROMPT_CACHING_ENABLED,
            "batch_size": STAGE2C_BATCH_SIZE,
            "batch_cap_usd": STAGE2C_BATCH_CAP_USD,
            "cumulative_stage2_cap_usd": STAGE2C_CUMULATIVE_CAP_USD,
            "theme_rotation_mode": THEME_ROTATION_MODE,
            "theme_cycle_len": THEME_CYCLE_LEN,
            "approved_examples_cap": APPROVED_EXAMPLES_CAP,
            "git_commit": git_commit,
            "run_timestamp_utc": run_timestamp_utc,
        },
        "batch_id": batch_id,
        "dry_run": dry_run,
        "hypotheses_attempted": state.hypotheses_attempted,
        "unissued_slots": len(truncated_calls),
        "truncated": truncated_at is not None,
        "truncated_at_call": truncated_at,
        "early_stop_reason": early_stop_reason,
        "early_stop_detail": early_stop_detail,
        "lifecycle_counts": lifecycle_dist,
        "lifecycle_invariant_ok": True,
        "parse_rate": parse_rate,
        "cardinality_distribution": cardinality_dist,
        "cardinality_violation_count": cardinality_violation_count,
        "total_estimated_cost_usd": total_est,
        "total_actual_cost_usd": total_actual,
        "cost_ratio": (total_est / total_actual if total_actual > 0
                       else float("inf")),
        "cumulative_monthly_spend_usd": monthly_spend,
        "factor_usage": factor_usage,
        "error_breakdown": error_breakdown,
        "per_theme": per_theme_rows,
        "anomaly_flags": anomaly_flags,
        "approved_examples_trace": [
            {
                "call_k": c["position"],
                "count_in_prompt": c.get(
                    "approved_examples_count_in_prompt_before_call"),
                "names": c.get("approved_example_names_before_call", []),
                "logic_notes": c.get("approved_example_logic_notes", []),
            }
            for c in call_summaries
        ],
        "calls": call_summaries,
    }

    summary_dir = payload_dir / f"batch_{batch_id}"
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = summary_dir / "stage2c_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"[Stage 2c] summary written: {summary_path}")

    # --- Console report ---
    print(f"\n[Stage 2c] SUMMARY:")
    print(f"  batch_id: {batch_id}")
    print(f"  git_commit: {git_commit}")
    print(f"  hypotheses_attempted: {state.hypotheses_attempted}")
    print(f"  unissued_slots: {len(truncated_calls)}")
    print(f"  lifecycle: {lifecycle_dist}")
    if parse_rate is not None:
        print(f"  parse_rate: {parse_rate:.3f}")
    print(f"  cardinality_dist: {cardinality_dist}")
    print(f"  cardinality_violations: {cardinality_violation_count}")
    print(f"  total_est_cost: ${total_est:.6f}")
    print(f"  total_actual_cost: ${total_actual:.6f}")
    if total_actual > 0:
        print(f"  cost_ratio (est/actual): {total_est / total_actual:.2f}x")
    else:
        print("  cost_ratio (est/actual): n/a (zero actual)")
    print(f"  monthly_spend: ${monthly_spend:.6f}")
    print(f"  truncated: {truncated_at is not None}")
    if early_stop_reason:
        print(f"  EARLY STOP: {early_stop_reason} @ {early_stop_detail}")

    print("\n[Stage 2c] per-theme:")
    for row in per_theme_rows:
        print(f"  {row['theme']}: n={row['n_calls']} "
              f"valid={row['valid_count']} "
              f"avg_overlap={row['avg_overlap_count']} "
              f"avg_oot={row['avg_out_of_theme_factors']} "
              f"rsi14={row['contains_rsi14_count']} "
              f"top3={row['dominant_factors_top3']}")

    if anomaly_flags:
        print("\n[Stage 2c] anomaly_flags:")
        for f in anomaly_flags:
            print(f"  {f}")

    for c in call_summaries:
        trunc = " [TRUNCATED]" if c["truncated_by_cap"] else ""
        print(f"  call {c['position']}: {c.get('lifecycle_state')} "
              f"valid_status={c.get('valid_status')} "
              f"hash={c.get('hypothesis_hash')} "
              f"in={c.get('input_tokens')} out={c.get('output_tokens')} "
              f"est=${c.get('estimated_cost_usd', 0) or 0:.6f} "
              f"act=${c.get('actual_cost_usd', 0) or 0:.6f} "
              f"examples={c.get('approved_examples_count_in_prompt_before_call', 0)} "
              f"overlap={c.get('overlap_count')} "
              f"card={c.get('cardinality')}{trunc}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="D6 Stage 2c — 20-hypothesis sequential Sonnet batch"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use stub backend instead of live Sonnet",
    )
    args = parser.parse_args()
    run_stage2c(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
