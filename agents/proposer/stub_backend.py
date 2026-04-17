"""D6 Stage 1 — deterministic stub Proposer backend.

Produces the seven acceptance categories enumerated in the D6 Stage 1
brief, one per ``generate`` call, cycling through a fixed sequence:

    1. ``valid``                 — parses, validates, compiles clean
    2. ``invalid_json``          — malformed JSON (unclosed brace)
    3. ``duplicate_of_valid``    — hashes identically to ``valid``
    4. ``over_complex``          — exceeds D2 complexity budget
                                   (4 entry groups, budget is 3)
    5. ``factor_out_of_registry``— references a factor outside
                                   ``allowed_factors``
    6. ``grammar_violation``     — uses an operator outside
                                   ``allowed_operators`` (``between``)
    7. ``non_finite_threshold``  — scalar value is NaN

The stub is purely deterministic: the same scenario name always yields
byte-identical raw JSON. This is what makes duplicate detection
testable — ``valid`` and ``duplicate_of_valid`` deliberately return the
same JSON so their D3 hashes collide.

DESIGN INVARIANT: the stub emits raw JSON strings and then routes them
through the SAME ``classify_candidate`` pipeline a Sonnet backend would
use (implemented in this module). Stage 1 proves the classification and
lifecycle mapping on stub output; Stage 2 reuses the same pipeline on
Sonnet output unchanged. If a future refactor hoists classification
into the orchestrator, both backends must still call the same shared
helper — the stub must not get its own classification fast-path.

CONTRACT BOUNDARY: this module does NOT import ``anthropic``. Stub and
Sonnet backends both implement
:class:`~agents.proposer.interface.ProposerBackend`; the orchestrator
depends only on the Protocol. The stub backend must remain usable
without any Anthropic credentials or network access.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable

from pydantic import ValidationError

from agents.proposer.interface import (
    BatchContext,
    DSLCandidate,
    InvalidCandidate,
    ProposerOutput,
    ValidCandidate,
)
from factors.registry import FactorRegistry, get_registry
from strategies.dsl import StrategyDSL


# ---------------------------------------------------------------------------
# Raw-JSON fixtures (stable, byte-identical across runs)
# ---------------------------------------------------------------------------

_VALID_DSL_JSON = json.dumps(
    {
        "name": "stub_momentum_long",
        "description": "Stub: enter on 24h return > 2%, exit on 24h return < 0%.",
        "entry": [
            {"conditions": [{"factor": "return_24h", "op": ">", "value": 0.02}]}
        ],
        "exit": [
            {"conditions": [{"factor": "return_24h", "op": "<", "value": 0.0}]}
        ],
        "position_sizing": "full_equity",
        "max_hold_bars": None,
    },
    sort_keys=True,
    separators=(",", ":"),
)

_OVER_COMPLEX_DSL_JSON = json.dumps(
    {
        "name": "stub_over_complex",
        "description": "Stub: exceeds entry group budget (4 groups, budget is 3).",
        "entry": [
            {"conditions": [{"factor": "return_24h", "op": ">", "value": 0.01}]},
            {"conditions": [{"factor": "return_24h", "op": ">", "value": 0.02}]},
            {"conditions": [{"factor": "return_24h", "op": ">", "value": 0.03}]},
            {"conditions": [{"factor": "return_24h", "op": ">", "value": 0.04}]},
        ],
        "exit": [
            {"conditions": [{"factor": "return_24h", "op": "<", "value": 0.0}]}
        ],
        "position_sizing": "full_equity",
        "max_hold_bars": None,
    },
    sort_keys=True,
    separators=(",", ":"),
)

_FACTOR_OUT_OF_REGISTRY_DSL_JSON = json.dumps(
    {
        "name": "stub_factor_oor",
        "description": "Stub: references an unregistered factor.",
        "entry": [
            {"conditions": [
                {"factor": "nonexistent_factor_42", "op": ">", "value": 0.5}
            ]}
        ],
        "exit": [
            {"conditions": [{"factor": "return_24h", "op": "<", "value": 0.0}]}
        ],
        "position_sizing": "full_equity",
        "max_hold_bars": None,
    },
    sort_keys=True,
    separators=(",", ":"),
)

_GRAMMAR_VIOLATION_DSL_JSON = json.dumps(
    {
        "name": "stub_grammar_viol",
        "description": "Stub: uses a disallowed operator (between).",
        "entry": [
            {"conditions": [
                {"factor": "return_24h", "op": "between", "value": 0.02}
            ]}
        ],
        "exit": [
            {"conditions": [{"factor": "return_24h", "op": "<", "value": 0.0}]}
        ],
        "position_sizing": "full_equity",
        "max_hold_bars": None,
    },
    sort_keys=True,
    separators=(",", ":"),
)

_NON_FINITE_DSL_JSON = (
    '{"name":"stub_non_finite",'
    '"description":"Stub: NaN scalar threshold.",'
    '"entry":[{"conditions":[{"factor":"return_24h","op":">","value":NaN}]}],'
    '"exit":[{"conditions":[{"factor":"return_24h","op":"<","value":0.0}]}],'
    '"position_sizing":"full_equity","max_hold_bars":null}'
)

# Intentionally malformed: unclosed brace + trailing comma.
_INVALID_JSON_STRING = (
    '{"name":"stub_bad_json",'
    '"description":"Stub: unclosed brace and trailing comma.",'
    '"entry":[{"conditions":[{"factor":"return_24h","op":">","value":0.02,}]}'
)


_SCENARIO_TO_RAW: dict[str, str] = {
    "valid": _VALID_DSL_JSON,
    "invalid_json": _INVALID_JSON_STRING,
    "duplicate_of_valid": _VALID_DSL_JSON,
    "over_complex": _OVER_COMPLEX_DSL_JSON,
    "factor_out_of_registry": _FACTOR_OUT_OF_REGISTRY_DSL_JSON,
    "grammar_violation": _GRAMMAR_VIOLATION_DSL_JSON,
    "non_finite_threshold": _NON_FINITE_DSL_JSON,
}

# The default acceptance sequence: one of each category, in a stable
# order. ``hypotheses_attempted == 7`` for this full cycle.
DEFAULT_SCENARIO_SEQUENCE: tuple[str, ...] = (
    "valid",
    "invalid_json",
    "duplicate_of_valid",
    "over_complex",
    "factor_out_of_registry",
    "grammar_violation",
    "non_finite_threshold",
)


# ---------------------------------------------------------------------------
# Shared classifier (used by stub; will be reused by Sonnet backend in Stage 2)
# ---------------------------------------------------------------------------


def classify_raw_json(
    raw_json: str,
    registry: FactorRegistry | None = None,
    *,
    error_kind_hint: str | None = None,
    provenance: dict | None = None,
) -> DSLCandidate:
    """Parse + validate a raw Proposer output string.

    Returns a :class:`ValidCandidate` if the string parses as JSON AND
    validates against :class:`~strategies.dsl.StrategyDSL`; otherwise a
    :class:`InvalidCandidate` carrying ``raw_json`` and a
    ``parse_error`` string.

    ``error_kind_hint`` is optional audit telemetry; the orchestrator's
    lifecycle-state assignment does NOT rely on it (see
    ``agents/orchestrator/ingest.py``).
    """
    prov = dict(provenance or {})
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return InvalidCandidate(
            raw_json=raw_json,
            parse_error=f"json_decode_error: {exc}",
            error_kind=error_kind_hint,
            provenance=prov,
        )
    reg = registry or get_registry()
    try:
        dsl = StrategyDSL.model_validate(payload, context={"registry": reg})
    except ValidationError as exc:
        # Use Pydantic's compact string form; full structured errors are
        # available via ``exc.errors()`` for downstream classification.
        return InvalidCandidate(
            raw_json=raw_json,
            parse_error=str(exc),
            error_kind=error_kind_hint,
            provenance={**prov, "validation_errors": exc.errors()},
        )
    return ValidCandidate(dsl=dsl, provenance=prov)


# ---------------------------------------------------------------------------
# Stub backend
# ---------------------------------------------------------------------------


@dataclass
class StubProposerBackend:
    """Deterministic Proposer backend for D6 Stage 1.

    Cycles through ``scenario_sequence`` one scenario per
    :meth:`generate` call, keyed by ``context.position``. The sequence
    wraps around for batches longer than its length.

    Two calls with the same ``scenario`` always return byte-identical
    raw JSON; this is what makes duplicate-detection testable.

    Args:
        scenario_sequence: Ordered list of scenario names to emit. Each
            name must be a key in :data:`_SCENARIO_TO_RAW`. Defaults to
            :data:`DEFAULT_SCENARIO_SEQUENCE`.
        registry: Optional :class:`~factors.registry.FactorRegistry` used
            during candidate classification. Defaults to the global
            registry.
        cost_per_call_usd: Simulated pre-charge cost per ``generate``
            call. Stage 1 stub calls cost $0 in reality, but the
            orchestrator's budget ledger exercises the pre-charge
            pattern as if each call cost the Sonnet token rate.
    """

    scenario_sequence: tuple[str, ...] = DEFAULT_SCENARIO_SEQUENCE
    registry: FactorRegistry | None = None
    cost_per_call_usd: float = 0.0

    def __post_init__(self) -> None:
        unknown = [s for s in self.scenario_sequence if s not in _SCENARIO_TO_RAW]
        if unknown:
            raise ValueError(
                f"StubProposerBackend: unknown scenarios {unknown!r}; "
                f"valid: {sorted(_SCENARIO_TO_RAW)}"
            )

    def generate(self, context: BatchContext) -> ProposerOutput:
        scenario = self.scenario_sequence[
            (context.position - 1) % len(self.scenario_sequence)
        ]
        raw_json = _SCENARIO_TO_RAW[scenario]
        provenance = {
            "backend": "stub",
            "scenario": scenario,
            "position": context.position,
            "batch_id": context.batch_id,
        }
        candidate = classify_raw_json(
            raw_json,
            registry=self.registry,
            error_kind_hint=scenario,
            provenance=provenance,
        )
        return ProposerOutput(
            candidates=(candidate,),
            cost_estimate_usd=self.cost_per_call_usd,
            cost_actual_usd=self.cost_per_call_usd,
            backend_name="stub",
            telemetry={"scenario": scenario},
        )


__all__ = [
    "DEFAULT_SCENARIO_SEQUENCE",
    "StubProposerBackend",
    "classify_raw_json",
]
