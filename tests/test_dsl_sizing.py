import json

import pytest
from pydantic import ValidationError

from strategies.dsl import (
    Condition,
    ConditionGroup,
    SizingSpec,
    StrategyDSL,
    canonicalize_dsl,
    compute_dsl_hash,
)


def _entry():
    return [ConditionGroup(conditions=[Condition(factor="rsi_14", op="<", value=30.0)])]


def _exit():
    return [ConditionGroup(conditions=[Condition(factor="rsi_14", op=">", value=70.0)])]


def test_sizing_spec_full_equity_literal_still_valid():
    dsl = StrategyDSL(
        name="fe",
        description="full equity sizing keeps working",
        entry=_entry(),
        exit=_exit(),
        position_sizing="full_equity",
    )
    assert dsl.position_sizing == "full_equity"


def test_sizing_spec_valid_bands():
    spec = SizingSpec(
        factor="intrabar_push",
        bands=[
            {"lower": -1.0, "upper": 0.0, "size": 0.25},
            {"lower": 0.0, "upper": 1.0, "size": 0.75},
        ],
        default_size=0.5,
    )
    dsl = StrategyDSL(
        name="ternary",
        description="ternary sizing ladder over intrabar_push",
        entry=_entry(),
        exit=_exit(),
        position_sizing=spec,
    )
    assert isinstance(dsl.position_sizing, SizingSpec)
    assert dsl.position_sizing.factor == "intrabar_push"
    assert len(dsl.position_sizing.bands) == 2


def test_sizing_spec_unknown_factor_rejected():
    with pytest.raises(ValidationError, match="unknown sizing factor"):
        SizingSpec(
            factor="not_a_factor",
            bands=[{"lower": 0.0, "upper": 1.0, "size": 0.5}],
            default_size=0.5,
        )


def test_sizing_spec_band_size_above_one_rejected():
    with pytest.raises(ValidationError):
        SizingSpec(
            factor="intrabar_push",
            bands=[{"lower": 0.0, "upper": 1.0, "size": 1.5}],
            default_size=0.5,
        )


def test_sizing_spec_default_size_negative_rejected():
    with pytest.raises(ValidationError):
        SizingSpec(
            factor="intrabar_push",
            bands=[{"lower": 0.0, "upper": 1.0, "size": 0.5}],
            default_size=-0.1,
        )


def test_sizing_spec_requires_at_least_one_band():
    with pytest.raises(ValidationError):
        SizingSpec(factor="intrabar_push", bands=[], default_size=0.5)


def test_sizing_spec_extra_field_forbidden():
    with pytest.raises(ValidationError):
        SizingSpec(
            factor="intrabar_push",
            bands=[{"lower": 0.0, "upper": 1.0, "size": 0.5}],
            default_size=0.5,
            leverage=2.0,
        )


def test_sizing_band_lower_ge_upper_rejected():
    with pytest.raises(ValidationError, match="must be <"):
        SizingSpec(
            factor="intrabar_push",
            bands=[{"lower": 1.0, "upper": 1.0, "size": 0.5}],
            default_size=0.5,
        )


# ---------------------------------------------------------------------------
# Task 14 — D2 canonicalize_dsl recurses through SizingSpec (green-on-arrival)
# ---------------------------------------------------------------------------


def _sizing_dsl():
    return StrategyDSL(
        name="ternary",
        description="ternary sizing ladder for canonicalization",
        entry=_entry(),
        exit=_exit(),
        position_sizing=SizingSpec(
            factor="intrabar_push",
            bands=[
                {"lower": -1.0, "upper": 0.0, "size": 0.25},
                {"lower": 0.0, "upper": 1.0, "size": 0.75},
            ],
            default_size=0.5,
        ),
    )


def test_canonicalize_dsl_recurses_into_sizing_spec():
    s = canonicalize_dsl(_sizing_dsl())
    payload = json.loads(s)
    ps = payload["position_sizing"]
    # SizingSpec serialized as a nested object, not dropped or stringified.
    assert isinstance(ps, dict)
    assert ps["factor"] == "intrabar_push"
    assert ps["default_size"] == 0.5
    assert [b["size"] for b in ps["bands"]] == [0.25, 0.75]


def test_canonicalize_dsl_byte_stable_for_sizing():
    a = canonicalize_dsl(_sizing_dsl())
    b = canonicalize_dsl(_sizing_dsl())
    assert a == b  # deterministic across two builds
    # full_equity DSL must NOT serialize the same as a SizingSpec DSL.
    fe = StrategyDSL(
        name="ternary",
        description="ternary sizing ladder for canonicalization",
        entry=_entry(),
        exit=_exit(),
        position_sizing="full_equity",
    )
    assert canonicalize_dsl(fe) != a
    assert compute_dsl_hash(fe) != compute_dsl_hash(_sizing_dsl())
