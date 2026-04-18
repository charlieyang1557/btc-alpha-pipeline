"""D7 replay reconstruction (D7 Stage 2a).

Rebuilds the exact BatchContext that existed when a target candidate
was proposed in a signed-off Stage 2d batch. Used by the Stage 2a
live-call probe to feed a replayed candidate back through
``run_critic()`` without re-running D6.

DESIGN INVARIANT: ``prior_factor_sets`` is computed by iterating over
calls 1..position-1 and extracting factor sets from pending_backtest
candidates only. Empty factor sets are excluded (matches Stage 1
empty-factor-set semantics and Stage 2d
``valid_with_empty_factor_set_count`` exclusion).

CONTRACT BOUNDARY: This module reads signed-off batch artifacts only.
It never re-runs the D6 Proposer, never generates new DSLs, and never
mutates on-disk state.
"""

from __future__ import annotations

import json
from pathlib import Path

from agents.critic.batch_context import (
    DEFAULT_MOMENTUM_FACTORS,
    THEME_ANCHOR_FACTORS,
    THEME_HINTS,
    BatchContext,
)
from agents.proposer.stub_backend import classify_raw_json
from factors.registry import FactorRegistry, get_registry
from strategies.dsl import StrategyDSL


def _load_stage2d_summary(
    batch_uuid: str, stage2d_artifacts_root: Path,
) -> dict:
    summary_path = (
        stage2d_artifacts_root / f"batch_{batch_uuid}" / "stage2d_summary.json"
    )
    if not summary_path.exists():
        raise FileNotFoundError(
            f"stage2d_summary not found: {summary_path}. "
            "This script reads signed-off batch artifacts only — "
            "provide a batch_uuid that was produced by D6."
        )
    with summary_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_response_text(
    batch_uuid: str, position: int, stage2d_artifacts_root: Path,
) -> str:
    """Load the raw response text for a specific call.

    Handles both ``attempt_<NNNN>_response.txt`` (no retry) and
    ``attempt_<NNNN>_retry_<K>_response.txt`` (last retry wins).
    """
    base = stage2d_artifacts_root / f"batch_{batch_uuid}"
    primary = base / f"attempt_{position:04d}_response.txt"
    if primary.exists():
        return primary.read_text(encoding="utf-8")
    # Fall back to retries: pick the highest retry index.
    retries = sorted(
        base.glob(f"attempt_{position:04d}_retry_*_response.txt")
    )
    if retries:
        return retries[-1].read_text(encoding="utf-8")
    raise FileNotFoundError(
        f"no response payload for call {position:04d} under {base}/"
    )


def _factor_set_from_call_record(call: dict) -> tuple[str, ...] | None:
    """Extract a sorted tuple of factors from a per-call record.

    Returns ``None`` for calls that did not produce a pending_backtest
    candidate or whose factor set is empty.
    """
    if call.get("lifecycle_state") != "pending_backtest":
        return None
    factors = call.get("factors_used") or []
    if not factors:
        return None
    return tuple(sorted(set(factors)))


def reconstruct_prior_factor_sets(
    calls: list[dict], up_to_position_exclusive: int,
) -> tuple[tuple[str, ...], ...]:
    """Build ``prior_factor_sets`` from a Stage 2d summary's call list.

    ``calls`` is the full ordered list of per-call records. Only records
    with ``lifecycle_state == 'pending_backtest'`` at position <
    ``up_to_position_exclusive`` contribute. Empty factor sets are
    excluded. Each set appears at most once, in first-seen order.
    """
    seen: set[tuple[str, ...]] = set()
    out: list[tuple[str, ...]] = []
    for call in calls:
        pos = call.get("position")
        if pos is None or pos >= up_to_position_exclusive:
            continue
        fs = _factor_set_from_call_record(call)
        if fs is None:
            continue
        if fs in seen:
            continue
        seen.add(fs)
        out.append(fs)
    return tuple(out)


def reconstruct_prior_hashes(
    calls: list[dict], up_to_position_exclusive: int,
) -> tuple[str, ...]:
    """Collect pending_backtest hypothesis_hashes prior to the target position."""
    out: list[str] = []
    for call in calls:
        pos = call.get("position")
        if pos is None or pos >= up_to_position_exclusive:
            continue
        if call.get("lifecycle_state") != "pending_backtest":
            continue
        h = call.get("hypothesis_hash")
        if h:
            out.append(h)
    return tuple(out)


def reconstruct_batch_context_at_position(
    batch_uuid: str,
    position: int,
    *,
    stage2d_artifacts_root: Path = Path("raw_payloads"),
    registry: FactorRegistry | None = None,
) -> tuple[StrategyDSL, str, BatchContext]:
    """Rebuild (dsl, theme, batch_context) for a signed-off Stage 2d call.

    Args:
        batch_uuid: UUID of the signed-off Stage 2d batch.
        position: 1-indexed position of the target call.
        stage2d_artifacts_root: Root containing ``batch_<uuid>/`` subdirs.
        registry: Factor registry for DSL re-validation. Defaults to the
            live global registry.

    Returns:
        ``(dsl, theme, batch_context)`` ready to feed into ``run_critic``.

    Raises:
        FileNotFoundError: artifacts missing.
        ValueError: target call is not pending_backtest or raw response
            no longer classifies as a valid candidate.
    """
    summary = _load_stage2d_summary(batch_uuid, stage2d_artifacts_root)
    calls: list[dict] = summary.get("calls", [])

    target = None
    for call in calls:
        if call.get("position") == position:
            target = call
            break
    if target is None:
        raise ValueError(
            f"position {position} not found in batch {batch_uuid}"
        )
    if target.get("lifecycle_state") != "pending_backtest":
        raise ValueError(
            f"position {position} is not pending_backtest "
            f"(got {target.get('lifecycle_state')!r}); cannot replay"
        )

    theme = target.get("theme")
    if not isinstance(theme, str):
        raise ValueError(
            f"position {position} has no theme; summary may be corrupt"
        )

    raw_response = _load_response_text(
        batch_uuid, position, stage2d_artifacts_root,
    )
    reg = registry or get_registry()
    candidate = classify_raw_json(raw_response, registry=reg)
    # Avoid importing ValidCandidate at module top to keep dependency
    # surface minimal; check duck-typed 'dsl' attribute.
    if not hasattr(candidate, "dsl"):
        raise ValueError(
            f"position {position} raw response no longer classifies as "
            f"valid DSL under the current registry"
        )

    prior_fs = reconstruct_prior_factor_sets(calls, position)
    prior_hashes = reconstruct_prior_hashes(calls, position)

    ctx = BatchContext(
        prior_factor_sets=prior_fs,
        prior_hashes=prior_hashes,
        batch_position=position,
        theme_hints=THEME_HINTS,
        default_momentum_factors=DEFAULT_MOMENTUM_FACTORS,
        theme_anchor_factors=THEME_ANCHOR_FACTORS,
    )
    return candidate.dsl, theme, ctx


__all__ = [
    "reconstruct_batch_context_at_position",
    "reconstruct_prior_factor_sets",
    "reconstruct_prior_hashes",
]
