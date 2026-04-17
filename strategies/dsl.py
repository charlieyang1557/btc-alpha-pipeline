"""Strategy DSL — pydantic v2 schema (Phase 2A, D2).

Validates one hypothesis before it ever reaches the compiler. Rejection
happens at schema-parse time for:

- Complexity budget violations (entry/exit groups > 3, conditions per
  group > 4, ``max_hold_bars`` > 720, ``name`` > 64 chars,
  ``description`` > 300 chars).
- Unknown factor names (LHS or RHS), resolved against the live
  :class:`factors.registry.FactorRegistry`.
- Position sizing other than ``"full_equity"`` (Phase 2 restriction).

The compiler (``strategies/dsl_compiler.py``) is a pure code-path dispatcher;
it trusts that whatever DSL it receives has already passed this schema.

Registry injection:
    By default all validators resolve factor names against
    :func:`factors.registry.get_registry`. To validate against a non-global
    registry (unit tests, dry-run orchestration), pass
    ``context={"registry": my_registry}`` to
    :meth:`StrategyDSL.model_validate`.

Canonicalization:
    :func:`canonicalize_dsl` returns a deterministic JSON string used for
    hashing (D2 manifest, D3 hypothesis_hash) and for wire transport to
    the compiler. ``sort_keys=True`` + compact separators remove whitespace
    variance. Key ordering is deterministic because the DSL's model_dump
    output is ordered by declaration.
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic import ValidationInfo

from factors.registry import FactorRegistry, get_registry

# ---------------------------------------------------------------------------
# Allowed operator set — single source of truth for both schema and compiler.
# ---------------------------------------------------------------------------

_CONTINUOUS_OPS = ("<", "<=", ">", ">=", "==")
_CROSS_OPS = ("crosses_above", "crosses_below")
ALL_OPS = _CONTINUOUS_OPS + _CROSS_OPS

# Pydantic's Literal needs a fixed tuple literal; we re-declare here to
# keep the schema importable even if ALL_OPS is extended in the future.
OpLiteral = Literal[
    "<", "<=", ">", ">=", "==", "crosses_above", "crosses_below"
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _registry_from_info(info: ValidationInfo) -> FactorRegistry:
    """Pull a registry out of validation context, falling back to global."""
    ctx = info.context or {}
    reg = ctx.get("registry")
    if reg is None:
        reg = get_registry()
    if not isinstance(reg, FactorRegistry):
        raise TypeError(
            f"validation context 'registry' must be FactorRegistry, "
            f"got {type(reg).__name__}"
        )
    return reg


# ---------------------------------------------------------------------------
# Condition
# ---------------------------------------------------------------------------


class Condition(BaseModel):
    """One atomic predicate: ``<factor> <op> <value>``.

    ``factor`` must be a registered factor name. ``value`` is either a
    numeric scalar (factor-vs-scalar) or the name of another registered
    factor (factor-vs-factor). No other string values are permitted — a
    string that does not match a registered factor is rejected at
    validation time, not silently reinterpreted.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    factor: str
    op: OpLiteral
    value: float | str

    @field_validator("factor")
    @classmethod
    def _validate_factor(cls, v: str, info: ValidationInfo) -> str:
        if not v:
            raise ValueError("factor must be a non-empty string")
        reg = _registry_from_info(info)
        known = set(reg.list_names())
        if v not in known:
            raise ValueError(
                f"unknown factor {v!r}; registered factors: {sorted(known)}"
            )
        return v

    @field_validator("value", mode="before")
    @classmethod
    def _reject_bool_before_coercion(cls, v):
        # Pydantic coerces ``True``/``False`` to ``1.0``/``0.0`` for a
        # ``float | str`` annotation before our post-validation runs, so
        # the bool rejection must happen BEFORE coercion.
        if isinstance(v, bool):
            raise ValueError("value must be float or str, not bool")
        return v

    @field_validator("value")
    @classmethod
    def _validate_value(
        cls, v: float | str, info: ValidationInfo
    ) -> float | str:
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            if not v:
                raise ValueError("value string must be non-empty")
            reg = _registry_from_info(info)
            known = set(reg.list_names())
            if v not in known:
                raise ValueError(
                    f"value {v!r} is not a registered factor name; "
                    f"registered factors: {sorted(known)}. "
                    f"Use a float for factor-vs-scalar comparisons."
                )
            return v
        raise ValueError(
            f"value must be float or registered factor name (str); "
            f"got {type(v).__name__}"
        )


# ---------------------------------------------------------------------------
# ConditionGroup
# ---------------------------------------------------------------------------


class ConditionGroup(BaseModel):
    """AND-connected group of conditions (1..4 items).

    Multiple ``ConditionGroup`` objects in an entry/exit list are
    OR-connected; within a group, all conditions must be true.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    conditions: list[Condition] = Field(min_length=1, max_length=4)


# ---------------------------------------------------------------------------
# StrategyDSL
# ---------------------------------------------------------------------------


class StrategyDSL(BaseModel):
    """Top-level DSL node.

    Fields:
        name: Short unique label (1..64 chars).
        description: One-sentence human-readable rationale (1..300 chars).
        entry: 1..3 OR-connected ConditionGroup objects for entry.
        exit: 1..3 OR-connected ConditionGroup objects for exit.
        position_sizing: Phase 2 restricts this to ``"full_equity"``.
        max_hold_bars: Optional hard cap on holding time in bars
            (1..720 ≈ 30 days of 1h bars). ``None`` means "no cap".

    The model is ``frozen=True`` so a validated instance cannot be mutated
    into something that would pass the compiler but violate the budget.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=1, max_length=300)
    entry: list[ConditionGroup] = Field(min_length=1, max_length=3)
    exit: list[ConditionGroup] = Field(min_length=1, max_length=3)
    position_sizing: Literal["full_equity"]
    max_hold_bars: int | None = Field(default=None, ge=1, le=720)


# ---------------------------------------------------------------------------
# Canonicalization + hashing
# ---------------------------------------------------------------------------


def canonicalize_dsl(dsl: StrategyDSL) -> str:
    """Deterministic JSON serialization of a validated DSL.

    Uses ``sort_keys=True`` and compact separators so the output is
    byte-stable across Python runs on the same machine. The returned
    string is safe to feed into :func:`hashlib.sha256` for manifest keys
    and (later) D3's hypothesis_hash.
    """
    return json.dumps(
        dsl.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )


def compute_dsl_hash(dsl: StrategyDSL) -> str:
    """SHA256 hex digest of :func:`canonicalize_dsl`.

    D2 uses this as the compilation-manifest filename key. D3 may build
    a richer ``hypothesis_hash`` on top (e.g. composing with a DSL
    schema version) without invalidating D2's usage — the manifest
    records the canonical DSL directly, so drift detection does not
    depend on a specific hashing scheme.
    """
    return hashlib.sha256(canonicalize_dsl(dsl).encode("utf-8")).hexdigest()


__all__ = [
    "ALL_OPS",
    "Condition",
    "ConditionGroup",
    "StrategyDSL",
    "OpLiteral",
    "canonicalize_dsl",
    "compute_dsl_hash",
]
