import pytest

from agents.hypothesis_hash import (
    _canonical_position_sizing,
    canonicalize_for_hash,
    hash_dsl,
)
from strategies.dsl import Condition, ConditionGroup, SizingSpec, StrategyDSL


def _entry():
    return [ConditionGroup(conditions=[Condition(factor="rsi_14", op="<", value=30.0)])]


def _exit():
    return [ConditionGroup(conditions=[Condition(factor="rsi_14", op=">", value=70.0)])]


def _dsl(position_sizing):
    return StrategyDSL(
        name="x",
        description="hash-sizing test strategy",
        entry=_entry(),
        exit=_exit(),
        position_sizing=position_sizing,
    )


def _spec(default_size=0.5):
    return SizingSpec(
        factor="intrabar_push",
        bands=[
            {"lower": -1.0, "upper": 0.0, "size": 0.25},
            {"lower": 0.0, "upper": 1.0, "size": 0.75},
        ],
        default_size=default_size,
    )


def test_canonical_position_sizing_full_equity():
    assert _canonical_position_sizing("full_equity") == "full_equity"


def test_canonical_position_sizing_spec_is_json_safe_dict():
    out = _canonical_position_sizing(_spec())
    assert out["kind"] == "sizing_spec"
    assert out["factor"] == "intrabar_push"
    # 6-decimal tagged, band order preserved (NOT sorted — bands are ordered).
    assert out["default_size"] == "num:0.500000"
    assert out["bands"][0] == {
        "lower": "num:-1.000000",
        "upper": "num:0.000000",
        "size": "num:0.250000",
    }


def test_canonicalize_for_hash_does_not_raise_on_sizing_spec():
    # Before the fix this raised TypeError on json.dumps of a pydantic model.
    s = canonicalize_for_hash(_dsl(_spec()))
    assert "sizing_spec" in s


def test_hash_changes_when_sizing_changes():
    h_full = hash_dsl(_dsl("full_equity"))
    h_spec = hash_dsl(_dsl(_spec()))
    assert h_full != h_spec

    h_a = hash_dsl(_dsl(_spec(default_size=0.5)))
    h_b = hash_dsl(_dsl(_spec(default_size=0.6)))
    assert h_a != h_b  # different default_size -> different dedup key


def test_hash_stable_for_identical_sizing():
    assert hash_dsl(_dsl(_spec())) == hash_dsl(_dsl(_spec()))


def test_hash_differs_for_swapped_band_order():
    bands_ab = [
        {"lower": -1.0, "upper": 0.0, "size": 0.25},
        {"lower": 0.0, "upper": 1.0, "size": 0.75},
    ]
    bands_ba = [
        {"lower": 0.0, "upper": 1.0, "size": 0.75},
        {"lower": -1.0, "upper": 0.0, "size": 0.25},
    ]
    spec_ab = SizingSpec(factor="intrabar_push", bands=bands_ab, default_size=0.5)
    spec_ba = SizingSpec(factor="intrabar_push", bands=bands_ba, default_size=0.5)
    assert hash_dsl(_dsl(spec_ab)) != hash_dsl(_dsl(spec_ba))
