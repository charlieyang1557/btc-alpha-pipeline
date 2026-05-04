"""D6 Stage 2d — 200-hypothesis sequential live production-shape batch.

Final sub-stage of Stage 2 and the last gate before D7 Critic work.
Proves contract-stable 200-call execution, freezes per-theme statistics
at N=40, characterizes long-horizon mode-collapse signals, and provides
production cost/time profile for D8 orchestrator planning.

By default each of the 5 themes (momentum, mean_reversion,
volatility_regime, volume_divergence, calendar_effect) gets exactly 40
calls via interleaved-cyclic rotation
(``theme_slot = (k - 1) % THEME_CYCLE_LEN``; default
``THEME_CYCLE_LEN=5``).

PHASE2C_12 Q10 LOCKED: ``THEME_CYCLE_LEN`` is config-driven via the
``PHASE2C_THEME_CYCLE_LEN`` env var at module-load register; setting
``PHASE2C_THEME_CYCLE_LEN=6`` enables 6-theme rotation including
``multi_factor_combination``.

PHASE2C_12 Q9 LOCKED: setting ``PHASE2C_SMOKE_THEME_OVERRIDE`` to a
canonical theme name (typically ``multi_factor_combination``) locks
every prompt-LLM-visible theme to that override regardless of rotation
position.

Hard constraints enforced:
    - batch_size = 200
    - budget cap = $20 (via BudgetLedger.can_afford)
    - prompt caching DISABLED
    - model = claude-sonnet-4-5
    - sequential ordering: call k+1 only after call k fully completes
      (API response → payload write → classify → ingest → ledger
      finalize → approved_so_far update)
    - leakage audit MUST pass before each call
    - approved_examples cap = 3 (most recent first, pending_backtest only)
    - all Stage 1/2a/2b/2c contracts preserved

Catastrophic stop conditions (two-tier parse-rate gate):
    - Tier 1 (k=5): valid/issued < 0.50
    - Tier 2 (k=20): valid/issued <= 0.75
    - Per-theme single-mode failure: ≥36/40 same (error_category, error_signature)
    - Cardinality violation count > 10
    - Cumulative Stage-2 monthly spend > $30

New in 2d:
    - Crash-preserving incremental summary checkpointing (atomic write)
    - Factor-set saturation aggregates
    - 50-call block trend tracking
    - Interim snapshots at k=50,100,150,200

CONTRACT BOUNDARY: THEME_HINTS below is used ONLY for post-hoc telemetry
(overlap counts, dominant factors). It MUST NOT be referenced in prompt
construction, candidate validation, lifecycle classification, ingest
rules, or any acceptance logic.

D7 Critic integration (optional, via ``--with-critic``):
    When enabled, ``run_critic()`` is called after step 6 (approved_examples
    update) for every ``pending_backtest`` candidate. CriticResult is attached
    to the per-call record. D7 does NOT influence approved_examples selection
    (D6 behavior is byte-identical with or without critic).

Usage:
    python -m agents.proposer.stage2d_batch [--dry-run] [--with-critic]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

from agents.orchestrator.budget_ledger import (
    BACKEND_KIND_D7B_CRITIC,
    BudgetLedger,
    CALL_ROLE_CRITIQUE,
)
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

STAGE_LABEL = "D6_STAGE2D"
MODEL_NAME = "claude-sonnet-4-5"
PROMPT_CACHING_ENABLED = False


# PHASE2C_12 Step 2 fire-prep (Q1/Q3 LOCKED): STAGE2D_BATCH_SIZE is
# config-driven via PHASE2C_BATCH_SIZE env var at module-load register,
# parallel to Q10 PHASE2C_THEME_CYCLE_LEN mechanism. Default = 200
# preserves canonical b6fcbf86 operational baseline (parse_rate = 0.99 =
# 198/200 per PHASE2C_9 Step 2 closeout). PHASE2C_12 smoke fire sets
# PHASE2C_BATCH_SIZE=40 (per Q1 LOCKED at PHASE2C_12_PLAN.md §4.1);
# PHASE2C_12 main fire sets PHASE2C_BATCH_SIZE=198 (per Q3 LOCKED at
# §4.2). Closes Step 1 deliverable §9.4 carry-forward at register-precision.
#
# Range validation: bounded at [1, 200] = canonical-baseline ceiling
# (defensive-but-not-prescriptive; NOT hardcoded {40, 198}; successor
# cycle may legitimately use other batch sizes within the canonical-tested
# range without re-modifying validation).
def _resolve_batch_size() -> int:
    raw = os.environ.get("PHASE2C_BATCH_SIZE", "200")
    try:
        n = int(raw)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"PHASE2C_BATCH_SIZE={raw!r} is not a valid integer"
        ) from err
    if not (1 <= n <= 200):
        raise ValueError(
            f"PHASE2C_BATCH_SIZE={n} out of range; "
            f"must be in [1, 200] (canonical-baseline ceiling)"
        )
    return n


STAGE2D_BATCH_SIZE = _resolve_batch_size()
STAGE2D_BATCH_CAP_USD = 20.0
STAGE2D_MONTHLY_CAP_USD = 100.0
STAGE2D_CUMULATIVE_CAP_USD = 30.0
APPROVED_EXAMPLES_CAP = 3
THEME_ROTATION_MODE = "interleaved_cyclic"
# Q10 LOCKED (PHASE2C_12_PLAN.md §3.3 + §4.2): THEME_CYCLE_LEN is
# config-driven via PHASE2C_THEME_CYCLE_LEN env var at module-load
# register; default = 5 preserves canonical Stage 2c/2d operational
# rotation invariant (multi_factor_combination excluded). PHASE2C_12
# main batch fire sets PHASE2C_THEME_CYCLE_LEN=6 explicitly at fire
# boundary to enable 6-theme rotation including multi_factor_combination
# (33 candidates × 6 themes = 198 clean integer distribution per Q6).
# Persistence decision register: post-PHASE2C_12 successor scoping cycle
# adjudication; default stays 5 at code register until explicitly
# adjudicated otherwise. See CLAUDE.md "Theme rotation operational
# boundary (Stage 2c/2d)" for canonical rationale.
#
# Range validation (Codex Finding #3 ADOPT): module-load fail-fast
# bound at 1 <= THEME_CYCLE_LEN <= len(THEMES). Anti-pre-naming
# preserved via defensive-but-not-prescriptive bound (NOT hardcoded
# {5, 6}); successor cycle may legitimately use other cardinalities
# without re-modifying validation.
def _resolve_theme_cycle_len() -> int:
    raw = os.environ.get("PHASE2C_THEME_CYCLE_LEN", "5")
    try:
        n = int(raw)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"PHASE2C_THEME_CYCLE_LEN={raw!r} is not a valid integer"
        ) from err
    if not (1 <= n <= len(THEMES)):
        raise ValueError(
            f"PHASE2C_THEME_CYCLE_LEN={n} out of range; "
            f"must be in [1, {len(THEMES)}] (len(THEMES)={len(THEMES)})"
        )
    return n


THEME_CYCLE_LEN = _resolve_theme_cycle_len()
CHARS_PER_TOKEN = 2.9
EST_OUTPUT_TOKENS = 500
RAW_PAYLOAD_DIR = Path("raw_payloads")
LEDGER_PATH = Path("agents/spend_ledger.db")

# Two-tier parse-rate gate
TIER1_K = 5
TIER1_THRESHOLD = 0.50
TIER2_K = 20
TIER2_THRESHOLD = 0.75

# Per-theme single-mode failure (90% concentration across 40 calls)
THEME_CALLS_TOTAL = 40
SINGLE_MODE_THRESHOLD = 36

# Cardinality violation hard stop
CARDINALITY_VIOLATION_STOP = 10

# Anomaly thresholds (observation only, NOT stop conditions)
FACTOR_SET_RATIO_ANOMALY = 0.50
OUTPUT_TOKENS_ANOMALY = 500
RSI14_ANOMALY_RATIO = 0.80
REPEATED_FACTOR_SET_ANOMALY = 10

# Block trend configuration
BLOCK_SIZE = 50
BLOCK_COUNT = STAGE2D_BATCH_SIZE // BLOCK_SIZE

# Interim snapshot positions
SNAPSHOT_POSITIONS = (50, 100, 150, 200)

ALLOWED_OPERATORS = (
    "<", "<=", ">", ">=", "==", "crosses_above", "crosses_below",
)

# CONTRACT BOUNDARY: post-hoc telemetry only.
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

VALID_STATUS_VALID = "valid"
VALID_STATUS_INVALID_SCHEMA = "invalid_schema"
VALID_STATUS_INVALID_DUPLICATE = "invalid_duplicate"
VALID_STATUS_BACKEND_EMPTY = "backend_empty"
VALID_STATUS_TRUNCATED = "truncated_by_cap"


# ---------------------------------------------------------------------------
# Basic helpers (carried from 2c)
# ---------------------------------------------------------------------------


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


def _theme_for_position(
    k: int, theme_override: str | None = None,
) -> str:
    """Interleaved cyclic theme rotation: theme_slot = (k - 1) % THEME_CYCLE_LEN.

    When ``theme_override`` is provided (smoke-fire register at PHASE2C_12
    Q9 LOCKED operationalization), returns it directly and bypasses the
    canonical rotation. ``theme_override`` MUST be a member of
    :data:`agents.themes.THEMES` or a ``ValueError`` is raised
    (anti-fishing-license boundary at theme-content register-precision).

    Binding source: ``docs/phase2c/PHASE2C_12_PLAN.md`` §3.3 Q9 LOCKED.
    """
    if theme_override is not None:
        if theme_override not in THEMES:
            raise ValueError(
                f"theme_override={theme_override!r} not in canonical "
                f"THEMES tuple {THEMES}"
            )
        return theme_override
    return THEMES[(k - 1) % THEME_CYCLE_LEN]


def _resolve_smoke_theme_override() -> str | None:
    """Read ``PHASE2C_SMOKE_THEME_OVERRIDE`` env var once at batch entry.

    Distinguishes three states (Codex Finding #2 PARTIAL ADOPT
    refinement):

    - env var **unset** → returns ``None`` (R3 canonical-rotation
      fall-through preserved)
    - env var **set to empty/whitespace string** → raises
      ``ValueError`` (signals user intent to override but value missing;
      anti-fishing-license at malformed-config register)
    - env var **set to a non-empty string** → returns the value verbatim
      (validation against :data:`THEMES` is deferred to
      :func:`_theme_for_position`)

    Binding source: ``docs/phase2c/PHASE2C_12_PLAN.md`` §3.3 Q9 LOCKED
    + Charlie-register R2 binding (env-var read at caller register, not
    inside ``_theme_for_position``) + Codex Finding #2 PARTIAL ADOPT.
    """
    raw = os.environ.get("PHASE2C_SMOKE_THEME_OVERRIDE")
    if raw is None:
        return None
    if not raw.strip():
        raise ValueError(
            "PHASE2C_SMOKE_THEME_OVERRIDE is set to an empty/whitespace "
            "string. Unset the variable to fall through to canonical "
            "rotation, or set it to a canonical theme name from "
            f"{THEMES} to activate the smoke override."
        )
    return raw


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
    if cardinality == "single_object":
        return False
    if cardinality == "n/a":
        return False
    return True


def _valid_status_from_lifecycle(
    lifecycle_state: str | None, *, truncated: bool,
) -> str:
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
    return VALID_STATUS_INVALID_SCHEMA


def _classify_error(
    lifecycle_state: str, parse_error: str | None,
) -> dict[str, str | None]:
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
    first_line = parse_error.splitlines()[0] if parse_error else ""
    signature = first_line[:80].replace(" ", "_").lower() or "schema_error"
    return {"error_category": "schema_field_mismatch",
            "error_signature": signature}


def _build_per_call_telemetry(
    dsl: object | None, theme: str,
) -> dict[str, object]:
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


# ---------------------------------------------------------------------------
# Per-theme aggregation (same as 2c)
# ---------------------------------------------------------------------------


def _aggregate_per_theme(
    calls: list[dict], theme: str,
) -> dict[str, object]:
    theme_calls = [
        c for c in calls
        if c.get("theme") == theme and not c.get("truncated_by_cap")
    ]
    n_calls = len(theme_calls)
    if n_calls == 0:
        return {
            "theme": theme, "n_calls": 0, "valid_count": 0,
            "lifecycle_mix": {},
            "avg_overlap_count": None, "avg_overlap_ratio": None,
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
    factor_counts: dict[str, int] = {}
    for c in valid_calls:
        for f in c.get("factors_used", []):
            factor_counts[f] = factor_counts.get(f, 0) + 1
    sorted_factors = sorted(
        factor_counts.items(), key=lambda kv: (-kv[1], kv[0])
    )
    dominant_top3 = [f for f, _ in sorted_factors[:3]]
    return {
        "theme": theme, "n_calls": n_calls, "valid_count": valid_count,
        "lifecycle_mix": lifecycle_mix,
        "avg_overlap_count": avg_overlap_count,
        "avg_overlap_ratio": avg_overlap_ratio,
        "avg_out_of_theme_factors": avg_out_of_theme,
        "contains_rsi14_count": contains_rsi14_count,
        "contains_momentum_default_count": contains_momentum_default_count,
        "dominant_factors_top3": dominant_top3,
    }


# ---------------------------------------------------------------------------
# Per-theme single-mode failure check (2d: 36/40 threshold)
# ---------------------------------------------------------------------------


def _check_single_mode_failure(
    calls: list[dict], theme: str,
) -> tuple[bool, str | None, str | None]:
    """Check whether a theme shows single-mode failure across its 40 calls.

    Triggered iff the theme has exactly THEME_CALLS_TOTAL (40)
    non-truncated calls AND ≥ SINGLE_MODE_THRESHOLD (36) share identical
    (error_category, error_signature) AND all those are invalid.
    """
    theme_calls = [
        c for c in calls
        if c.get("theme") == theme and not c.get("truncated_by_cap")
    ]
    if len(theme_calls) < THEME_CALLS_TOTAL:
        return False, None, None
    invalid_calls = [
        c for c in theme_calls
        if c.get("lifecycle_state") != PENDING_BACKTEST
    ]
    if len(invalid_calls) < SINGLE_MODE_THRESHOLD:
        return False, None, None
    sig_counter: Counter[tuple[str | None, str | None]] = Counter()
    for c in invalid_calls:
        err = c.get("error_info") or {}
        sig_counter[(err.get("error_category"), err.get("error_signature"))] += 1
    (top_key, top_count), = sig_counter.most_common(1)
    if top_count >= SINGLE_MODE_THRESHOLD:
        cat, sig = top_key
        if cat is None or sig is None:
            return False, None, None
        return True, cat, sig
    return False, None, None


# ---------------------------------------------------------------------------
# NEW in 2d: Factor-set saturation aggregates
# ---------------------------------------------------------------------------


def _compute_factor_set_saturation(
    calls: list[dict],
) -> dict[str, object]:
    """Compute factor-set saturation metrics from attempted calls."""
    valid_calls = [
        c for c in calls
        if c.get("lifecycle_state") == PENDING_BACKTEST
        and not c.get("truncated_by_cap")
    ]
    total_valid = len(valid_calls)
    hashes = [c.get("hypothesis_hash") for c in valid_calls if c.get("hypothesis_hash")]
    distinct_hash_count = len(set(hashes))

    empty_fs_calls = [
        c["position"] for c in valid_calls
        if not c.get("factors_used")
    ]
    non_empty_valid = [
        c for c in valid_calls if c.get("factors_used")
    ]
    factor_sets: list[tuple[str, ...]] = []
    for c in non_empty_valid:
        factor_sets.append(tuple(sorted(c.get("factors_used", []))))
    distinct_fs_count = len(set(factor_sets))
    denom = total_valid - len(empty_fs_calls)
    unique_fs_ratio = (
        round(distinct_fs_count / denom, 4) if denom > 0 else None
    )

    fs_counter: Counter[tuple[str, ...]] = Counter(factor_sets)
    repeated: list[dict] = []
    for fs, count in fs_counter.most_common():
        if count < 2:
            break
        matching = [
            c for c in non_empty_valid
            if tuple(sorted(c.get("factors_used", []))) == fs
        ]
        h_set = {c.get("hypothesis_hash") for c in matching}
        positions = [c["position"] for c in matching]
        themes_used = [c["theme"] for c in matching]
        repeated.append({
            "factor_set": list(fs),
            "occurrence_count": count,
            "distinct_hashes_within_factor_set": len(h_set),
            "occurring_at_calls": positions,
            "themes_used_in": themes_used,
        })
    repeated.sort(key=lambda r: (-r["occurrence_count"], r["occurring_at_calls"][0]))

    return {
        "total_valid_count": total_valid,
        "distinct_hash_count": distinct_hash_count,
        "valid_with_empty_factor_set_count": len(empty_fs_calls),
        "valid_with_empty_factor_set_calls": empty_fs_calls,
        "distinct_factor_set_count": distinct_fs_count,
        "unique_factor_set_ratio": unique_fs_ratio,
        "repeated_factor_sets": repeated,
    }


# ---------------------------------------------------------------------------
# NEW in 2d: 50-call block trends
# ---------------------------------------------------------------------------


def _compute_block_trends(
    calls: list[dict],
) -> list[dict]:
    """Compute per-block (50 calls each) trend metrics."""
    blocks: list[dict] = []
    for b in range(BLOCK_COUNT):
        start = b * BLOCK_SIZE
        end = start + BLOCK_SIZE
        block_calls = [
            c for c in calls[start:end]
            if not c.get("truncated_by_cap")
        ]
        if not block_calls:
            blocks.append({
                "block": b + 1,
                "range": f"{start + 1}-{end}",
                "complete": False,
                "call_count": 0,
                "input_tokens_mean": None,
                "input_tokens_median": None,
                "input_tokens_max": None,
                "output_tokens_mean": None,
                "output_tokens_median": None,
                "output_tokens_max": None,
                "actual_cost_mean": None,
                "actual_cost_total": 0.0,
                "valid_count": 0,
                "valid_rate": None,
                "distinct_factor_set_count_within_block": 0,
            })
            continue

        complete = len(block_calls) == BLOCK_SIZE
        in_toks = [c["input_tokens"] for c in block_calls
                    if c.get("input_tokens") is not None]
        out_toks = [c["output_tokens"] for c in block_calls
                    if c.get("output_tokens") is not None]
        costs = [c["actual_cost_usd"] for c in block_calls
                 if c.get("actual_cost_usd") is not None]
        valid_in_block = [
            c for c in block_calls
            if c.get("lifecycle_state") == PENDING_BACKTEST
        ]
        fs_in_block = set()
        for c in valid_in_block:
            fu = c.get("factors_used")
            if fu:
                fs_in_block.add(tuple(sorted(fu)))

        blocks.append({
            "block": b + 1,
            "range": f"{start + 1}-{end}",
            "complete": complete,
            "call_count": len(block_calls),
            "input_tokens_mean": (
                round(sum(in_toks) / len(in_toks), 1) if in_toks else None
            ),
            "input_tokens_median": (
                round(median(in_toks), 1) if in_toks else None
            ),
            "input_tokens_max": max(in_toks) if in_toks else None,
            "output_tokens_mean": (
                round(sum(out_toks) / len(out_toks), 1) if out_toks else None
            ),
            "output_tokens_median": (
                round(median(out_toks), 1) if out_toks else None
            ),
            "output_tokens_max": max(out_toks) if out_toks else None,
            "actual_cost_mean": (
                round(sum(costs) / len(costs), 6) if costs else None
            ),
            "actual_cost_total": round(sum(costs), 6) if costs else 0.0,
            "valid_count": len(valid_in_block),
            "valid_rate": round(
                len(valid_in_block) / len(block_calls), 4
            ) if block_calls else None,
            "distinct_factor_set_count_within_block": len(fs_in_block),
        })
    return blocks


# ---------------------------------------------------------------------------
# NEW in 2d: Interim snapshots
# ---------------------------------------------------------------------------


def _compute_interim_snapshot(
    calls: list[dict], at_call: int,
    prev_snapshot_call: int,
) -> dict[str, object]:
    """Compute a cumulative interim snapshot at the given call position."""
    cum_calls = [
        c for c in calls[:at_call]
        if not c.get("truncated_by_cap")
    ]
    valid = [c for c in cum_calls
             if c.get("lifecycle_state") == PENDING_BACKTEST]
    hashes = {c.get("hypothesis_hash") for c in valid
              if c.get("hypothesis_hash")}
    non_empty_valid = [c for c in valid if c.get("factors_used")]
    fs = {tuple(sorted(c.get("factors_used", []))) for c in non_empty_valid}
    denom = len(valid) - (len(valid) - len(non_empty_valid))
    ratio = round(len(fs) / denom, 4) if denom > 0 else None

    costs = [c.get("actual_cost_usd", 0) for c in cum_calls
             if c.get("actual_cost_usd") is not None]

    since_last = [
        c for c in calls[prev_snapshot_call:at_call]
        if not c.get("truncated_by_cap")
    ]
    in_since = [c["input_tokens"] for c in since_last
                if c.get("input_tokens") is not None]
    out_since = [c["output_tokens"] for c in since_last
                 if c.get("output_tokens") is not None]

    lifecycle_mix: dict[str, int] = {}
    for c in cum_calls:
        ls = c.get("lifecycle_state") or "unknown"
        lifecycle_mix[ls] = lifecycle_mix.get(ls, 0) + 1

    return {
        "at_call": at_call,
        "cumulative_valid_count": len(valid),
        "cumulative_distinct_hash_count": len(hashes),
        "cumulative_distinct_factor_set_count": len(fs),
        "cumulative_unique_factor_set_ratio": ratio,
        "cumulative_actual_cost_usd": round(sum(costs), 6),
        "cumulative_lifecycle_mix": lifecycle_mix,
        "avg_input_tokens_since_last_snapshot": (
            round(sum(in_since) / len(in_since), 1) if in_since else None
        ),
        "avg_output_tokens_since_last_snapshot": (
            round(sum(out_since) / len(out_since), 1) if out_since else None
        ),
    }


# ---------------------------------------------------------------------------
# Atomic write helper
# ---------------------------------------------------------------------------


def _atomic_write_json(path: Path, data: dict) -> None:
    """Write JSON atomically: write to .tmp then os.replace."""
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(
        json.dumps(data, indent=2, default=str),
        encoding="utf-8",
    )
    os.replace(str(tmp_path), str(path))


# ---------------------------------------------------------------------------
# Anomaly log builder
# ---------------------------------------------------------------------------


def _build_anomaly_log(
    calls: list[dict],
    saturation: dict,
    block_trends: list[dict],
    interim_snapshots: list[dict],
) -> list[dict]:
    """Build anomaly flags for the batch (observation only, NOT stops)."""
    flags: list[dict] = []

    # Factor-set ratio drop at any interim snapshot
    for snap in interim_snapshots:
        ratio = snap.get("cumulative_unique_factor_set_ratio")
        if ratio is not None and ratio < FACTOR_SET_RATIO_ANOMALY:
            flags.append({
                "kind": "factor_set_ratio_below_threshold",
                "scope": f"interim_snapshot_at_call_{snap['at_call']}",
                "ratio": ratio,
                "threshold": FACTOR_SET_RATIO_ANOMALY,
            })

    # Output tokens mean exceeds 500 in any block
    for bt in block_trends:
        mean_out = bt.get("output_tokens_mean")
        if mean_out is not None and mean_out > OUTPUT_TOKENS_ANOMALY:
            flags.append({
                "kind": "output_tokens_high",
                "scope": f"block_{bt['block']}",
                "output_tokens_mean": mean_out,
                "threshold": OUTPUT_TOKENS_ANOMALY,
            })

    # rsi_14 in ≥80% of first 50 valid calls
    attempted = [c for c in calls if not c.get("truncated_by_cap")]
    first50_valid = [
        c for c in attempted[:50]
        if c.get("lifecycle_state") == PENDING_BACKTEST
    ]
    if first50_valid:
        rsi_count = sum(
            1 for c in first50_valid
            if "rsi_14" in c.get("factors_used", [])
        )
        if rsi_count / len(first50_valid) >= RSI14_ANOMALY_RATIO:
            flags.append({
                "kind": "rsi_14_dominance",
                "scope": "first_50_valid_calls",
                "count": rsi_count,
                "total": len(first50_valid),
                "ratio": round(rsi_count / len(first50_valid), 4),
                "threshold": RSI14_ANOMALY_RATIO,
            })

    # Repeated factor set ≥ 10 occurrences
    for rfs in saturation.get("repeated_factor_sets", []):
        if rfs["occurrence_count"] >= REPEATED_FACTOR_SET_ANOMALY:
            flags.append({
                "kind": "repeated_factor_set_high",
                "factor_set": rfs["factor_set"],
                "occurrence_count": rfs["occurrence_count"],
                "distinct_hashes": rfs["distinct_hashes_within_factor_set"],
                "threshold": REPEATED_FACTOR_SET_ANOMALY,
            })

    # Empty factor sets in valid calls
    empty_calls = saturation.get("valid_with_empty_factor_set_calls", [])
    if empty_calls:
        flags.append({
            "kind": "empty_factor_set_in_valid",
            "calls": empty_calls,
            "count": len(empty_calls),
        })

    # Hash duplication (distinct_hash_count < total_valid_count)
    total_valid = saturation.get("total_valid_count", 0)
    distinct_h = saturation.get("distinct_hash_count", 0)
    if distinct_h < total_valid:
        valid_calls = [
            c for c in calls
            if c.get("lifecycle_state") == PENDING_BACKTEST
            and not c.get("truncated_by_cap")
        ]
        hash_to_calls: dict[str, list[int]] = {}
        for c in valid_calls:
            h = c.get("hypothesis_hash")
            if h:
                hash_to_calls.setdefault(h, []).append(c["position"])
        dup_hashes = {
            h: pos for h, pos in hash_to_calls.items() if len(pos) > 1
        }
        flags.append({
            "kind": "hash_duplication",
            "total_valid": total_valid,
            "distinct_hashes": distinct_h,
            "duplicate_hashes": dup_hashes,
        })

    return flags


# ---------------------------------------------------------------------------
# Main batch loop
# ---------------------------------------------------------------------------


def run_stage2d(
    *,
    dry_run: bool = False,
    with_critic: bool = False,
    live_critic: bool = False,
    _backend: object | None = None,
    _ledger_path: Path | None = None,
    _payload_dir: Path | None = None,
    _d7b_backend: object | None = None,
) -> dict:
    """Execute the Stage 2d 200-hypothesis observation batch.

    Args:
        dry_run: Use stub Proposer backend (no API calls).
        with_critic: Enable D7 Critic (rule-based + D7b).
        live_critic: When ``with_critic=True``, instantiate
            ``LiveSonnetD7bBackend`` instead of ``StubD7bBackend``.
            Mutually exclusive with ``with_critic=False`` (raises
            ``ValueError`` for the cross-product). PHASE2C_12 Q-OPEN-2
            LOCKED = live D7b for criterion (B) measurement
            register-precision.

    Returns a summary dict. Parameters prefixed with ``_`` are test
    injection points; production callers should leave them at None.
    """
    if live_critic and not with_critic:
        raise ValueError(
            "live_critic=True requires with_critic=True; cannot enable "
            "live D7b backend while critic gate is disabled "
            "(anti-fishing-license at flag-interaction register-precision)"
        )
    _load_dotenv()
    smoke_theme_override = _resolve_smoke_theme_override()
    registry = get_registry()
    batch_id = str(uuid.uuid4())
    payload_dir = _payload_dir or RAW_PAYLOAD_DIR
    ledger_path = _ledger_path or LEDGER_PATH
    run_timestamp_utc = datetime.now(timezone.utc).isoformat()
    batch_start_time = time.monotonic()
    git_commit = _git_commit_short()

    print(f"[Stage 2d] batch_id={batch_id}")
    print(f"[Stage 2d] dry_run={dry_run}")
    print(f"[Stage 2d] timestamp={run_timestamp_utc}")
    print(f"[Stage 2d] batch_size={STAGE2D_BATCH_SIZE} "
          f"cap=${STAGE2D_BATCH_CAP_USD}")
    print(f"[Stage 2d] theme_rotation={THEME_ROTATION_MODE} "
          f"cycle_len={THEME_CYCLE_LEN}")
    if smoke_theme_override is not None:
        print(f"[Stage 2d] smoke_theme_override={smoke_theme_override!r} "
              f"(PHASE2C_12 Q9 fire register)")

    # --- Pre-flight: clear stale pending entries ---
    ledger = BudgetLedger(ledger_path)
    pending = ledger.pending_entries()
    if pending:
        print(f"[Stage 2d] pre-flight: marking {len(pending)} stale "
              f"pending entries as crashed")
        for entry in pending:
            ledger.mark_crashed(
                entry.id,
                now=datetime.now(timezone.utc),
                notes="Stage 2d pre-flight: clearing stale entry "
                      f"from batch {entry.batch_id}",
            )

    # --- Select backend ---
    if _backend is not None:
        backend = _backend
        print("[Stage 2d] backend: injected (test)")
    elif dry_run:
        backend = StubProposerBackend(registry=registry, cost_per_call_usd=0.0)
        print("[Stage 2d] backend: stub (dry-run)")
    else:
        backend = SonnetProposerBackend(
            registry=registry,
            max_retries=3,
            backoff_base_seconds=1.0,
            raw_payload_dir=payload_dir,
        )
        print("[Stage 2d] backend: sonnet (live)")

    # --- Critic setup (optional) ---
    critic_d7b = None
    if with_critic:
        from agents.critic.batch_context import (
            DEFAULT_MOMENTUM_FACTORS,
            THEME_ANCHOR_FACTORS,
            THEME_HINTS as CRITIC_THEME_HINTS,
            BatchContext as CriticBatchContext,
        )
        from agents.critic.d7a_feature_extraction import (
            extract_factors as critic_extract_factors,
            factor_set_tuple as critic_factor_set_tuple,
        )
        from agents.critic.d7b_stub import StubD7bBackend as StubD7bCriticBackend
        from agents.critic.orchestrator import (
            compute_reliability_stats,
            run_critic,
        )
        if _d7b_backend is not None:
            critic_d7b = _d7b_backend
        elif live_critic:
            # PHASE2C_12 Step 2 fire-prep Surface (2): live D7b for
            # criterion (B) measurement at register-precision against
            # canonical b6fcbf86 baseline. CONTRACT BOUNDARY:
            # LiveSonnetD7bBackend instantiates its OWN anthropic client
            # independent of the D6 Proposer client (per d7b_live.py
            # dataclass docstring).
            from agents.critic.d7b_live import LiveSonnetD7bBackend
            critic_d7b = LiveSonnetD7bBackend(
                raw_payload_dir=payload_dir,
                batch_id=batch_id,
            )
        else:
            critic_d7b = StubD7bCriticBackend()
        print(f"[Stage 2d] critic: enabled (d7b_mode={critic_d7b.mode})")
    else:
        print("[Stage 2d] critic: disabled")

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
    batch_status = "in_progress"
    # Critic state (only used when with_critic=True)
    critic_prior_factor_sets: list[tuple[str, ...]] = []
    critic_prior_hashes: list[str] = []
    critic_ok_count = 0
    critic_d7a_error_count = 0
    critic_d7b_error_count = 0
    critic_both_error_count = 0

    summary_dir = payload_dir / f"batch_{batch_id}"
    summary_dir.mkdir(parents=True, exist_ok=True)
    partial_path = summary_dir / "stage2d_summary_partial.json"

    def _truncated_call(j: int) -> dict:
        return {
            "position": j,
            "theme": _theme_for_position(j, theme_override=smoke_theme_override),
            "truncated_by_cap": True,
            "lifecycle_state": None, "valid_status": VALID_STATUS_TRUNCATED,
            "hypothesis_hash": None,
            "input_tokens": None, "output_tokens": None,
            "estimated_cost_usd": None, "actual_cost_usd": None,
            "approved_examples_count_in_prompt_before_call": None,
            "approved_example_names_before_call": [],
            "approved_example_logic_notes": [],
            "cardinality": "n/a", "retry_count": 0, "error_info": None,
            "factors_used": [], "overlap_count": 0,
            "overlap_ratio": None, "out_of_theme_factor_count": 0,
            "contains_default_momentum_factor": False,
            "default_momentum_factors_used": [],
        }

    # Helper to build the partial config block (reused in checkpoints).
    def _config_block(status: str) -> dict:
        elapsed = time.monotonic() - batch_start_time
        return {
            "stage_label": STAGE_LABEL,
            "model_name": MODEL_NAME,
            "prompt_caching_enabled": PROMPT_CACHING_ENABLED,
            "batch_size": STAGE2D_BATCH_SIZE,
            "batch_cap_usd": STAGE2D_BATCH_CAP_USD,
            "theme_rotation_mode": THEME_ROTATION_MODE,
            "approved_examples_cap": APPROVED_EXAMPLES_CAP,
            "parse_rate_gate_k5_threshold": TIER1_THRESHOLD,
            "parse_rate_gate_k20_threshold": TIER2_THRESHOLD,
            "git_commit": git_commit,
            "run_timestamp_utc": run_timestamp_utc,
            "batch_duration_seconds": round(elapsed, 2),
            "batch_status": status,
        }

    # --- Sequential call loop ---
    for k in range(1, STAGE2D_BATCH_SIZE + 1):
        theme = _theme_for_position(k, theme_override=smoke_theme_override)
        if k <= 5 or k % 50 == 0 or k == STAGE2D_BATCH_SIZE:
            print(f"\n[Stage 2d] --- Call {k}/{STAGE2D_BATCH_SIZE} "
                  f"(theme={theme}) ---")
        elif k % 10 == 0:
            print(f"[Stage 2d] call {k}/{STAGE2D_BATCH_SIZE} "
                  f"(theme={theme})")

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

        if isinstance(backend, SonnetProposerBackend):
            backend.approved_examples = examples_for_prompt

        now = datetime.now(timezone.utc)
        ctx = BatchContext(
            batch_id=batch_id,
            position=k,
            batch_size=STAGE2D_BATCH_SIZE,
            allowed_factors=tuple(registry.list_names()),
            allowed_operators=ALLOWED_OPERATORS,
            theme_slot=(k - 1) % THEME_CYCLE_LEN,
            theme_override=smoke_theme_override,
            budget_remaining={
                "batch_usd": ledger.batch_remaining_usd(
                    batch_id, batch_cap_usd=STAGE2D_BATCH_CAP_USD),
                "monthly_usd": ledger.monthly_remaining_usd(
                    now=now, monthly_cap_usd=STAGE2D_MONTHLY_CAP_USD),
            },
        )

        prompt = build_prompt(
            ctx, registry=registry, approved_examples=examples_for_prompt,
        )
        leakage_findings = audit_prompt_for_leakage(prompt)
        if leakage_findings:
            print(f"[Stage 2d] ABORT: leakage audit at call {k}: "
                  f"{leakage_findings}")
            sys.exit(1)

        prompt_text = prompt.all_text()
        est_input_tokens = _estimate_input_tokens(prompt_text)
        est_cost = compute_cost_usd(est_input_tokens, EST_OUTPUT_TOKENS)

        # Cumulative Stage-2 monthly-spend catastrophic stop (pre-call).
        current_monthly = ledger.monthly_spent_usd(now=now)
        if current_monthly + est_cost > STAGE2D_CUMULATIVE_CAP_USD:
            early_stop_reason = "cumulative_stage2_spend_exceeded"
            early_stop_detail = {
                "at_call": k,
                "current_monthly_usd": current_monthly,
                "next_call_estimate_usd": est_cost,
                "cumulative_cap_usd": STAGE2D_CUMULATIVE_CAP_USD,
            }
            print(f"[Stage 2d] EARLY STOP: cumulative spend "
                  f"${current_monthly:.4f} + est ${est_cost:.4f} "
                  f"> cap ${STAGE2D_CUMULATIVE_CAP_USD}")
            truncated_at = k
            for j in range(k, STAGE2D_BATCH_SIZE + 1):
                call_summaries.append(_truncated_call(j))
            break

        if not ledger.can_afford(
            batch_id=batch_id,
            estimated_cost_usd=est_cost,
            now=now,
            batch_cap_usd=STAGE2D_BATCH_CAP_USD,
            monthly_cap_usd=STAGE2D_MONTHLY_CAP_USD,
        ):
            print(f"[Stage 2d] TRUNCATED at call {k}: cannot afford "
                  f"${est_cost:.6f}")
            truncated_at = k
            for j in range(k, STAGE2D_BATCH_SIZE + 1):
                call_summaries.append(_truncated_call(j))
            break

        ledger_row_id = ledger.write_pending(
            batch_id=batch_id,
            api_call_kind="proposer",
            backend_kind="d6_proposer",
            call_role="propose",
            estimated_cost_usd=est_cost,
            now=now,
        )

        try:
            output = backend.generate(ctx)
        except Exception as exc:
            ledger.mark_crashed(
                ledger_row_id,
                now=datetime.now(timezone.utc),
                notes=f"generate() raised: {exc}",
            )
            batch_status = f"crashed_at_call_{k}"
            early_stop_reason = "infrastructure_crash"
            early_stop_detail = {"at_call": k, "error": str(exc)}
            _atomic_write_json(partial_path, {
                "config": _config_block(batch_status),
                "batch_id": batch_id,
                "batch_status": batch_status,
                "crash_reason": str(exc),
                "last_completed_call": k - 1,
                "elapsed_seconds_so_far": round(
                    time.monotonic() - batch_start_time, 2),
                "calls": call_summaries,
            })
            raise

        actual_cost = output.cost_actual_usd
        ledger.finalize(
            ledger_row_id,
            actual_cost_usd=actual_cost,
            now=datetime.now(timezone.utc),
        )

        records = ingest_output(state, output)
        rec = records[0] if records else None
        lifecycle_state = (
            rec.lifecycle_state if rec else BACKEND_EMPTY_OUTPUT
        )
        hypothesis_hash = rec.hypothesis_hash if rec else None

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

        # --- D7 Critic (optional, after step 6) ---
        critic_result_dict = None
        if with_critic and lifecycle_state == PENDING_BACKTEST and isinstance(
            cand, ValidCandidate
        ):
            critic_ctx = CriticBatchContext(
                prior_factor_sets=tuple(critic_prior_factor_sets),
                prior_hashes=tuple(critic_prior_hashes),
                batch_position=k,
                theme_hints=CRITIC_THEME_HINTS,
                default_momentum_factors=DEFAULT_MOMENTUM_FACTORS,
                theme_anchor_factors=THEME_ANCHOR_FACTORS,
            )

            # PHASE2C_12 Step 2 fire-prep Surface (3): pre-charge ledger
            # for live D7b critic call BEFORE run_critic. Closes
            # PHASE2C_3 + PHASE2C_5 carry-forward warning at register-
            # precision. Stub mode (cost = $0) skips pre-charge to avoid
            # $0 noise rows polluting the ledger. Per CLAUDE.md:
            # "NEVER perform a budget check AFTER an API call (must be
            # pre-call)". Per orchestrator contract, run_critic() never
            # raises — all D7b errors are captured in critic_status
            # codes — so finalize ALWAYS runs in the happy path; the
            # try/finally guards finalize() exceptions only (which are
            # infrastructural, not API-level).
            from agents.critic.d7b_live import (
                D7B_STAGE2A_COST_CEILING_USD,
            )
            critic_row_id = None
            if critic_d7b.mode == "live":
                critic_row_id = ledger.write_pending(
                    batch_id=batch_id,
                    api_call_kind="critic_d7b",
                    backend_kind=BACKEND_KIND_D7B_CRITIC,
                    call_role=CALL_ROLE_CRITIQUE,
                    estimated_cost_usd=D7B_STAGE2A_COST_CEILING_USD,
                    now=datetime.now(timezone.utc),
                )

            cr = run_critic(cand.dsl, theme, critic_ctx, critic_d7b)
            critic_result_dict = cr.to_dict()

            if critic_row_id is not None:
                # cr.d7b_cost_actual_usd is None when D7b never ran
                # (e.g., d7a_error short-circuit). Finalize at $0 in
                # that case — pre-charge represented the upper bound;
                # if no API call, actual = 0 is correct.
                actual_critic_cost = cr.d7b_cost_actual_usd or 0.0
                try:
                    ledger.finalize(
                        critic_row_id,
                        actual_cost_usd=actual_critic_cost,
                        now=datetime.now(timezone.utc),
                        input_tokens=cr.d7b_input_tokens,
                        output_tokens=cr.d7b_output_tokens,
                    )
                except Exception as fin_exc:
                    # Best-effort mark_crashed; pre-charge invariant
                    # preserved (crashed rows still count as spent at
                    # estimated_cost upper bound).
                    try:
                        ledger.mark_crashed(
                            critic_row_id,
                            now=datetime.now(timezone.utc),
                            notes=(
                                f"critic finalize raised: "
                                f"{type(fin_exc).__name__}: {fin_exc}"
                            ),
                        )
                    except Exception:
                        # mark_crashed itself failed; do not mask
                        # the original infrastructural problem
                        pass

            if cr.critic_status == "ok":
                critic_ok_count += 1
            elif cr.critic_status == "d7a_error":
                critic_d7a_error_count += 1
            elif cr.critic_status == "d7b_error":
                critic_d7b_error_count += 1
            elif cr.critic_status == "both_error":
                critic_both_error_count += 1
            # Update prior state for next critic call
            fs_tuple = critic_factor_set_tuple(cand.dsl)
            if fs_tuple:
                critic_prior_factor_sets.append(fs_tuple)
            if hypothesis_hash:
                critic_prior_hashes.append(hypothesis_hash)

        telemetry = output.telemetry
        input_tokens = telemetry.get("input_tokens")
        output_tokens = telemetry.get("output_tokens")

        cardinality = "n/a"
        response_file = (summary_dir / f"attempt_{k:04d}_response.txt")
        if response_file.exists():
            raw_text = response_file.read_text(encoding="utf-8")
            cardinality = _classify_cardinality(raw_text)
        if _is_cardinality_violation(cardinality):
            cardinality_violation_count += 1

        batch_dir = payload_dir / f"batch_{batch_id}"
        retry_count = 0
        if batch_dir.exists():
            retry_count = len(list(
                batch_dir.glob(f"attempt_{k:04d}_retry_*_response.txt")
            ))

        dsl_for_tel = cand.dsl if (
            lifecycle_state == PENDING_BACKTEST and isinstance(
                cand, ValidCandidate)
        ) else None
        per_call_tel = _build_per_call_telemetry(dsl_for_tel, theme)

        parse_error = rec.parse_error if rec else None
        error_info = _classify_error(lifecycle_state, parse_error)
        if parse_error:
            error_info = dict(error_info)
            error_info["parse_error_prefix"] = parse_error[:200]
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
        })
        if with_critic:
            call_summaries[-1]["critic_result"] = critic_result_dict

        if k <= 5 or k % 50 == 0 or k == STAGE2D_BATCH_SIZE:
            print(f"[Stage 2d] k={k} lifecycle={lifecycle_state} "
                  f"hash={hypothesis_hash} "
                  f"in={input_tokens} out={output_tokens} "
                  f"act=${actual_cost:.6f} card={cardinality}")

        # --- Incremental partial summary checkpoint (atomic) ---
        partial_data = {
            "config": _config_block("in_progress"),
            "batch_id": batch_id,
            "batch_status": "in_progress",
            "last_completed_call": k,
            "elapsed_seconds_so_far": round(
                time.monotonic() - batch_start_time, 2),
            "calls": call_summaries,
            "partial_per_theme": [
                _aggregate_per_theme(call_summaries, t)
                for t in list(THEMES)[:THEME_CYCLE_LEN]
            ],
        }
        _atomic_write_json(partial_path, partial_data)

        # --- Catastrophic stop checks (post-finalize) ---

        # Tier 1 — k=5 parse-rate gate (valid/issued < 0.50)
        issued_so_far = [c for c in call_summaries
                         if not c.get("truncated_by_cap")]
        if k == TIER1_K and early_stop_reason is None:
            valid_so_far = sum(
                1 for c in issued_so_far
                if c.get("lifecycle_state") == PENDING_BACKTEST
            )
            rate = valid_so_far / len(issued_so_far) if issued_so_far else 0
            if rate < TIER1_THRESHOLD:
                early_stop_reason = "tier1_parse_rate_below_threshold"
                early_stop_detail = {
                    "at_call": k, "issued": len(issued_so_far),
                    "valid": valid_so_far, "parse_rate": rate,
                    "threshold": TIER1_THRESHOLD,
                }
                print(f"[Stage 2d] EARLY STOP tier-1: "
                      f"parse_rate={rate:.3f} < {TIER1_THRESHOLD}")

        # Tier 2 — k=20 parse-rate gate (valid/issued <= 0.75)
        if k == TIER2_K and early_stop_reason is None:
            valid_so_far = sum(
                1 for c in issued_so_far
                if c.get("lifecycle_state") == PENDING_BACKTEST
            )
            rate = valid_so_far / len(issued_so_far) if issued_so_far else 0
            if rate <= TIER2_THRESHOLD:
                early_stop_reason = "tier2_parse_rate_at_or_below_threshold"
                early_stop_detail = {
                    "at_call": k, "issued": len(issued_so_far),
                    "valid": valid_so_far, "parse_rate": rate,
                    "threshold": TIER2_THRESHOLD,
                }
                print(f"[Stage 2d] EARLY STOP tier-2: "
                      f"parse_rate={rate:.3f} <= {TIER2_THRESHOLD}")

        # Cardinality violation stop (count > 10)
        if (early_stop_reason is None
                and cardinality_violation_count > CARDINALITY_VIOLATION_STOP):
            early_stop_reason = "cardinality_violation_count_exceeded"
            early_stop_detail = {
                "at_call": k,
                "violation_count": cardinality_violation_count,
                "threshold": CARDINALITY_VIOLATION_STOP,
            }
            print(f"[Stage 2d] EARLY STOP: cardinality violations "
                  f"{cardinality_violation_count} > "
                  f"{CARDINALITY_VIOLATION_STOP}")

        # Per-theme single-mode failure (only after a theme has 40 calls)
        if early_stop_reason is None:
            for t in list(THEMES)[:THEME_CYCLE_LEN]:
                triggered, cat, sig = _check_single_mode_failure(
                    call_summaries, t,
                )
                if triggered:
                    early_stop_reason = "per_theme_single_mode_failure"
                    early_stop_detail = {
                        "at_call": k, "theme": t,
                        "error_category": cat, "error_signature": sig,
                    }
                    print(f"[Stage 2d] EARLY STOP: theme '{t}' "
                          f"single-mode failure ({cat}/{sig})")
                    break

        # If any stop fired, mark remaining slots and break.
        if early_stop_reason is not None:
            batch_status = f"crashed_at_call_{k}"
            truncated_at = k + 1 if k < STAGE2D_BATCH_SIZE else None
            for j in range(k + 1, STAGE2D_BATCH_SIZE + 1):
                call_summaries.append(_truncated_call(j))
            _atomic_write_json(partial_path, {
                "config": _config_block(batch_status),
                "batch_id": batch_id,
                "batch_status": batch_status,
                "crash_reason": early_stop_reason,
                "last_completed_call": k,
                "elapsed_seconds_so_far": round(
                    time.monotonic() - batch_start_time, 2),
                "calls": call_summaries,
            })
            break

    # --- Batch close ---
    print(f"\n[Stage 2d] --- Batch close ---")
    assert_lifecycle_invariant_at_batch_close(state)
    print("[Stage 2d] lifecycle invariant: OK")

    if early_stop_reason is None:
        batch_status = "completed"

    batch_duration = round(time.monotonic() - batch_start_time, 2)
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
    lifecycle_dist = dict(state.lifecycle_counts)

    cardinality_dist: dict[str, int] = {}
    for c in attempted_calls:
        card = c.get("cardinality", "n/a")
        cardinality_dist[card] = cardinality_dist.get(card, 0) + 1

    error_breakdown = [
        c["error_info"] for c in attempted_calls if c.get("error_info")
    ]

    per_theme_rows = [
        _aggregate_per_theme(call_summaries, t)
        for t in list(THEMES)[:THEME_CYCLE_LEN]
    ]

    valid_attempted = sum(
        1 for c in attempted_calls
        if c.get("lifecycle_state") == PENDING_BACKTEST
    )
    parse_rate = (
        valid_attempted / len(attempted_calls) if attempted_calls else None
    )

    # Factor-set saturation
    saturation = _compute_factor_set_saturation(call_summaries)

    # Block trends
    block_trends = _compute_block_trends(call_summaries)

    # Interim snapshots
    interim_snapshots: list[dict] = []
    prev = 0
    for snap_k in SNAPSHOT_POSITIONS:
        if snap_k <= len(attempted_calls):
            interim_snapshots.append(
                _compute_interim_snapshot(call_summaries, snap_k, prev)
            )
            prev = snap_k

    # Anomaly log
    anomaly_flags = _build_anomaly_log(
        call_summaries, saturation, block_trends, interim_snapshots,
    )

    # --- Build summary JSON ---
    config = _config_block(batch_status)
    summary = {
        "config": config,
        "batch_id": batch_id,
        "dry_run": dry_run,
        "batch_status": batch_status,
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
        "batch_duration_seconds": batch_duration,
        "factor_usage": factor_usage,
        "error_breakdown": error_breakdown,
        "per_theme": per_theme_rows,
        # Factor-set saturation (top-level)
        "total_valid_count": saturation["total_valid_count"],
        "distinct_hash_count": saturation["distinct_hash_count"],
        "valid_with_empty_factor_set_count":
            saturation["valid_with_empty_factor_set_count"],
        "valid_with_empty_factor_set_calls":
            saturation["valid_with_empty_factor_set_calls"],
        "distinct_factor_set_count": saturation["distinct_factor_set_count"],
        "unique_factor_set_ratio": saturation["unique_factor_set_ratio"],
        "repeated_factor_sets": saturation["repeated_factor_sets"],
        # Block trends + interim snapshots
        "block_trends": block_trends,
        "interim_snapshots": interim_snapshots,
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

    # Critic summary fields (only present when critic is enabled)
    if with_critic:
        summary["critic_enabled"] = True
        summary["d7b_mode"] = critic_d7b.mode
        summary["critic_reliability"] = compute_reliability_stats(
            critic_ok_count,
            critic_d7a_error_count,
            critic_d7b_error_count,
            critic_both_error_count,
        )

    summary_path = summary_dir / "stage2d_summary.json"
    _atomic_write_json(summary_path, summary)
    print(f"[Stage 2d] summary written: {summary_path}")

    # Also update partial to "completed"
    _atomic_write_json(partial_path, {
        "config": _config_block(batch_status),
        "batch_id": batch_id,
        "batch_status": batch_status,
        "last_completed_call": len(attempted_calls),
        "elapsed_seconds_so_far": batch_duration,
        "calls": call_summaries,
    })

    # --- Console report ---
    print(f"\n[Stage 2d] SUMMARY:")
    print(f"  batch_id: {batch_id}")
    print(f"  batch_status: {batch_status}")
    print(f"  git_commit: {git_commit}")
    print(f"  duration: {batch_duration:.1f}s")
    print(f"  hypotheses_attempted: {state.hypotheses_attempted}")
    print(f"  unissued_slots: {len(truncated_calls)}")
    print(f"  lifecycle: {lifecycle_dist}")
    if parse_rate is not None:
        print(f"  parse_rate: {parse_rate:.4f}")
    print(f"  cardinality_dist: {cardinality_dist}")
    print(f"  cardinality_violations: {cardinality_violation_count}")
    print(f"  total_est_cost: ${total_est:.6f}")
    print(f"  total_actual_cost: ${total_actual:.6f}")
    if total_actual > 0:
        print(f"  cost_ratio (est/actual): {total_est / total_actual:.2f}x")
    print(f"  monthly_spend: ${monthly_spend:.6f}")
    print(f"  truncated: {truncated_at is not None}")
    if early_stop_reason:
        print(f"  EARLY STOP: {early_stop_reason}")

    print("\n[Stage 2d] per-theme:")
    for row in per_theme_rows:
        print(f"  {row['theme']}: n={row['n_calls']} "
              f"valid={row['valid_count']} "
              f"avg_overlap={row['avg_overlap_count']} "
              f"top3={row['dominant_factors_top3']}")

    print(f"\n[Stage 2d] factor-set saturation:")
    print(f"  total_valid: {saturation['total_valid_count']}")
    print(f"  distinct_hashes: {saturation['distinct_hash_count']}")
    print(f"  distinct_factor_sets: {saturation['distinct_factor_set_count']}")
    print(f"  unique_fs_ratio: {saturation['unique_factor_set_ratio']}")
    print(f"  repeated_sets: {len(saturation['repeated_factor_sets'])}")

    print("\n[Stage 2d] block trends:")
    for bt in block_trends:
        print(f"  block {bt['block']} ({bt['range']}): "
              f"n={bt['call_count']} valid={bt['valid_count']} "
              f"valid_rate={bt['valid_rate']} "
              f"cost_total=${bt['actual_cost_total']:.4f} "
              f"distinct_fs={bt['distinct_factor_set_count_within_block']}")

    if interim_snapshots:
        print("\n[Stage 2d] interim snapshots:")
        for snap in interim_snapshots:
            print(f"  @{snap['at_call']}: valid={snap['cumulative_valid_count']} "
                  f"hashes={snap['cumulative_distinct_hash_count']} "
                  f"fs_ratio={snap['cumulative_unique_factor_set_ratio']} "
                  f"cost=${snap['cumulative_actual_cost_usd']:.4f}")

    if anomaly_flags:
        print("\n[Stage 2d] anomaly_flags:")
        for af in anomaly_flags:
            print(f"  {af['kind']}: {af}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="D6 Stage 2d — 200-hypothesis sequential Sonnet batch"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use stub backend instead of live Sonnet",
    )
    parser.add_argument(
        "--with-critic",
        action="store_true",
        help="Enable D7 Critic (rule-based + stub D7b in Stage 1)",
    )
    parser.add_argument(
        "--live-critic",
        action="store_true",
        help=(
            "Use LiveSonnetD7bBackend instead of StubD7bBackend "
            "(requires --with-critic). Adds ~$0.01-0.02 per Critic "
            "call to ledger via pre-charge wrap. Required for "
            "PHASE2C_12 smoke criterion (B) register-precision."
        ),
    )
    args = parser.parse_args()
    run_stage2d(
        dry_run=args.dry_run,
        with_critic=args.with_critic,
        live_critic=args.live_critic,
    )


if __name__ == "__main__":
    main()
