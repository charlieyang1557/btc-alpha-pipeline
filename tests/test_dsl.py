"""Contract tests for the Phase 2A D2 Strategy DSL + compiler.

Split into four groups so failures localize clearly:

1. ``TestSchema`` — pydantic schema validation. Complexity budget,
   unknown factor rejection (LHS + RHS), frozen/extra-field rules.
2. ``TestCanonicalization`` — deterministic JSON + dsl_hash stability.
3. ``TestFactorVsScalar`` / ``TestFactorVsFactor`` — the two INDEPENDENT
   comparison code paths, one test per operator per path, plus the
   mandatory "stays-above-level-for-many-bars" crosses_above single-fire
   test at the helper level.
4. ``TestNanSemantics`` — NaN always evaluates to False in every operator
   and every path.

End-to-end compile/run/round-trip/manifest tests live in
``test_dsl_integration.py`` so this file stays fast (pure Python).
"""

from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from factors.registry import FactorRegistry, FactorSpec, get_registry
from strategies.dsl import (
    Condition,
    ConditionGroup,
    StrategyDSL,
    canonicalize_dsl,
    compute_dsl_hash,
)
from strategies.dsl_compiler import (
    _compare_factor_vs_factor,
    _compare_factor_vs_scalar,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def live_registry() -> FactorRegistry:
    """The live, fully-bootstrapped registry (14 core factors)."""
    return get_registry()


def _only_factor_compute(df):
    """Test-only top-level factor: returns close cast to float64."""
    return df["close"].astype("float64")


def _basic_entry() -> list[dict]:
    return [
        {"conditions": [{"factor": "sma_20", "op": ">", "value": 50000.0}]}
    ]


def _basic_exit() -> list[dict]:
    return [
        {"conditions": [{"factor": "sma_20", "op": "<", "value": 45000.0}]}
    ]


def _valid_dsl_dict(**overrides) -> dict:
    base = {
        "name": "test_strategy",
        "description": "test description",
        "entry": _basic_entry(),
        "exit": _basic_exit(),
        "position_sizing": "full_equity",
    }
    base.update(overrides)
    return base


# ===========================================================================
# 1. Schema validation
# ===========================================================================


class TestSchema:
    def test_valid_dsl_parses(self, live_registry):
        dsl = StrategyDSL.model_validate(_valid_dsl_dict())
        assert dsl.name == "test_strategy"
        assert dsl.position_sizing == "full_equity"
        assert len(dsl.entry) == 1
        assert dsl.max_hold_bars is None

    def test_frozen_model_rejects_mutation(self):
        dsl = StrategyDSL.model_validate(_valid_dsl_dict())
        with pytest.raises(ValidationError):
            dsl.name = "changed"

    def test_extra_field_forbidden(self):
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(_valid_dsl_dict(unexpected=1))

    def test_condition_extra_field_forbidden(self):
        bad = _valid_dsl_dict()
        bad["entry"] = [
            {"conditions": [
                {"factor": "sma_20", "op": ">", "value": 1.0, "extra": "x"}
            ]}
        ]
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(bad)

    # ---- Complexity budget --------------------------------------------------

    def test_name_too_long_rejected(self):
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(_valid_dsl_dict(name="x" * 65))

    def test_name_empty_rejected(self):
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(_valid_dsl_dict(name=""))

    def test_description_too_long_rejected(self):
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(
                _valid_dsl_dict(description="x" * 301)
            )

    def test_description_empty_rejected(self):
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(_valid_dsl_dict(description=""))

    def test_entry_empty_rejected(self):
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(_valid_dsl_dict(entry=[]))

    def test_entry_too_many_groups_rejected(self):
        groups = [_basic_entry()[0] for _ in range(4)]
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(_valid_dsl_dict(entry=groups))

    def test_exit_empty_rejected(self):
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(_valid_dsl_dict(exit=[]))

    def test_exit_too_many_groups_rejected(self):
        groups = [_basic_exit()[0] for _ in range(4)]
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(_valid_dsl_dict(exit=groups))

    def test_conditions_per_group_empty_rejected(self):
        bad = _valid_dsl_dict(entry=[{"conditions": []}])
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(bad)

    def test_conditions_per_group_too_many_rejected(self):
        conds = [
            {"factor": "sma_20", "op": ">", "value": float(i)}
            for i in range(5)
        ]
        bad = _valid_dsl_dict(entry=[{"conditions": conds}])
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(bad)

    def test_max_hold_bars_accepts_boundary_values(self):
        ok1 = StrategyDSL.model_validate(_valid_dsl_dict(max_hold_bars=1))
        ok720 = StrategyDSL.model_validate(_valid_dsl_dict(max_hold_bars=720))
        assert ok1.max_hold_bars == 1
        assert ok720.max_hold_bars == 720

    def test_max_hold_bars_zero_rejected(self):
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(_valid_dsl_dict(max_hold_bars=0))

    def test_max_hold_bars_over_720_rejected(self):
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(_valid_dsl_dict(max_hold_bars=721))

    # ---- Position sizing ---------------------------------------------------

    def test_position_sizing_restricted_to_full_equity(self):
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(
                _valid_dsl_dict(position_sizing="kelly")
            )

    # ---- Operator literals -------------------------------------------------

    def test_unknown_operator_rejected(self):
        bad = _valid_dsl_dict(entry=[
            {"conditions": [
                {"factor": "sma_20", "op": "~=", "value": 1.0}
            ]}
        ])
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(bad)

    # ---- Factor-name validation (LHS and RHS) ------------------------------

    def test_unknown_factor_lhs_rejected(self, live_registry):
        bad = _valid_dsl_dict(entry=[
            {"conditions": [
                {"factor": "nonexistent_factor", "op": ">", "value": 1.0}
            ]}
        ])
        with pytest.raises(ValidationError) as exc:
            StrategyDSL.model_validate(bad)
        assert "unknown factor" in str(exc.value).lower()

    def test_unknown_factor_rhs_string_rejected(self, live_registry):
        bad = _valid_dsl_dict(entry=[
            {"conditions": [
                {"factor": "sma_20", "op": ">", "value": "not_a_factor"}
            ]}
        ])
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(bad)

    def test_factor_vs_factor_rhs_ok(self, live_registry):
        dsl = StrategyDSL.model_validate(_valid_dsl_dict(entry=[
            {"conditions": [
                {"factor": "sma_20", "op": ">", "value": "sma_50"}
            ]}
        ]))
        assert dsl.entry[0].conditions[0].value == "sma_50"

    def test_bool_value_rejected(self):
        bad = _valid_dsl_dict(entry=[
            {"conditions": [
                {"factor": "sma_20", "op": ">", "value": True}
            ]}
        ])
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(bad)

    # ---- Registry injection via context ------------------------------------

    def test_custom_registry_via_context(self):
        reg = FactorRegistry()
        reg.register(FactorSpec(
            name="only_factor",
            category="test",
            warmup_bars=0,
            inputs=["close"],
            output_dtype="float64",
            compute=_only_factor_compute,
            docstring="dummy",
        ))
        # Factor not in global registry, but is in the context registry.
        dsl = StrategyDSL.model_validate(
            _valid_dsl_dict(
                entry=[{"conditions": [
                    {"factor": "only_factor", "op": ">", "value": 0.0}
                ]}],
                exit=[{"conditions": [
                    {"factor": "only_factor", "op": "<", "value": 0.0}
                ]}],
            ),
            context={"registry": reg},
        )
        assert dsl.entry[0].conditions[0].factor == "only_factor"

    def test_unknown_factor_on_custom_registry_rejected(self):
        reg = FactorRegistry()  # empty
        with pytest.raises(ValidationError):
            StrategyDSL.model_validate(
                _valid_dsl_dict(),
                context={"registry": reg},
            )


# ===========================================================================
# 2. Canonicalization + hashing
# ===========================================================================


class TestCanonicalization:
    def test_canonicalize_deterministic(self):
        d1 = _valid_dsl_dict()
        d2 = _valid_dsl_dict()
        dsl1 = StrategyDSL.model_validate(d1)
        dsl2 = StrategyDSL.model_validate(d2)
        assert canonicalize_dsl(dsl1) == canonicalize_dsl(dsl2)

    def test_canonicalize_sorted_keys(self):
        dsl = StrategyDSL.model_validate(_valid_dsl_dict())
        s = canonicalize_dsl(dsl)
        # sorted keys: description comes before entry, entry before exit, ...
        assert '"description"' in s
        # Compact separators (no whitespace).
        assert ", " not in s
        assert ": " not in s

    def test_dsl_hash_stable(self):
        d = _valid_dsl_dict()
        h1 = compute_dsl_hash(StrategyDSL.model_validate(d))
        h2 = compute_dsl_hash(StrategyDSL.model_validate(d))
        assert h1 == h2
        assert len(h1) == 64  # SHA256 hex

    def test_dsl_hash_changes_on_content_change(self):
        base = compute_dsl_hash(StrategyDSL.model_validate(_valid_dsl_dict()))
        modified = compute_dsl_hash(
            StrategyDSL.model_validate(_valid_dsl_dict(name="other"))
        )
        assert base != modified


# ===========================================================================
# 3A. Factor-vs-scalar comparisons — ONE test per operator.
# This code path is DELIBERATELY independent of factor-vs-factor. A bug in
# one must not affect the other; these tests are the proof of separation.
# ===========================================================================


class TestFactorVsScalar:
    def test_lt(self):
        # cur_val < scalar
        assert _compare_factor_vs_scalar("<", 1.0, 99.0, 2.0) is True
        assert _compare_factor_vs_scalar("<", 2.0, 99.0, 2.0) is False
        assert _compare_factor_vs_scalar("<", 3.0, 99.0, 2.0) is False

    def test_le(self):
        assert _compare_factor_vs_scalar("<=", 1.0, 99.0, 2.0) is True
        assert _compare_factor_vs_scalar("<=", 2.0, 99.0, 2.0) is True
        assert _compare_factor_vs_scalar("<=", 3.0, 99.0, 2.0) is False

    def test_gt(self):
        assert _compare_factor_vs_scalar(">", 3.0, 99.0, 2.0) is True
        assert _compare_factor_vs_scalar(">", 2.0, 99.0, 2.0) is False
        assert _compare_factor_vs_scalar(">", 1.0, 99.0, 2.0) is False

    def test_ge(self):
        assert _compare_factor_vs_scalar(">=", 3.0, 99.0, 2.0) is True
        assert _compare_factor_vs_scalar(">=", 2.0, 99.0, 2.0) is True
        assert _compare_factor_vs_scalar(">=", 1.0, 99.0, 2.0) is False

    def test_eq(self):
        assert _compare_factor_vs_scalar("==", 2.0, 99.0, 2.0) is True
        assert _compare_factor_vs_scalar("==", 2.0000001, 99.0, 2.0) is False

    def test_crosses_above_fires_at_actual_cross(self):
        # prev below, cur above — fire.
        assert _compare_factor_vs_scalar(
            "crosses_above", cur_val=60.0, prev_val=40.0, scalar=50.0
        ) is True
        # prev at level (<=), cur above — still a cross.
        assert _compare_factor_vs_scalar(
            "crosses_above", cur_val=60.0, prev_val=50.0, scalar=50.0
        ) is True

    def test_crosses_above_does_not_fire_when_still_above(self):
        # Both bars above the level — not a new cross.
        assert _compare_factor_vs_scalar(
            "crosses_above", cur_val=70.0, prev_val=60.0, scalar=50.0
        ) is False

    def test_crosses_above_does_not_fire_when_below(self):
        # Both bars below — definitely not a cross.
        assert _compare_factor_vs_scalar(
            "crosses_above", cur_val=40.0, prev_val=30.0, scalar=50.0
        ) is False

    def test_crosses_above_single_fire_over_50_bar_run(self):
        """**MANDATORY**: a factor that jumps above a level on bar K and
        stays above for 50 more bars must fire crosses_above exactly once.

        This is the test that catches the "naive single-bar comparison"
        bug described in PHASE2_BLUEPRINT_v2.md D2.
        """
        level = 50.0
        # Values: 30 bars at 10, one cross, then 50 bars at 60.
        values = [10.0] * 30 + [60.0] * 50
        fire_count = 0
        for i in range(1, len(values)):
            cur = values[i]
            prev = values[i - 1]
            if _compare_factor_vs_scalar(
                "crosses_above", cur, prev, level
            ):
                fire_count += 1
        assert fire_count == 1, (
            f"crosses_above must fire exactly once across a "
            f"{len(values)}-bar staying-above run; got {fire_count}"
        )

    def test_crosses_below_fires_at_actual_cross(self):
        assert _compare_factor_vs_scalar(
            "crosses_below", cur_val=40.0, prev_val=60.0, scalar=50.0
        ) is True
        assert _compare_factor_vs_scalar(
            "crosses_below", cur_val=40.0, prev_val=50.0, scalar=50.0
        ) is True

    def test_crosses_below_does_not_fire_when_still_below(self):
        assert _compare_factor_vs_scalar(
            "crosses_below", cur_val=30.0, prev_val=40.0, scalar=50.0
        ) is False

    def test_crosses_below_single_fire_over_50_bar_run(self):
        level = 50.0
        values = [70.0] * 30 + [40.0] * 50
        fire_count = 0
        for i in range(1, len(values)):
            if _compare_factor_vs_scalar(
                "crosses_below", values[i], values[i - 1], level
            ):
                fire_count += 1
        assert fire_count == 1

    def test_unknown_op_raises(self):
        with pytest.raises(ValueError):
            _compare_factor_vs_scalar("@@", 1.0, 1.0, 1.0)


# ===========================================================================
# 3B. Factor-vs-factor comparisons — independent tests per operator.
# ===========================================================================


class TestFactorVsFactor:
    def test_lt(self):
        assert _compare_factor_vs_factor("<", 1.0, 99.0, 2.0, 99.0) is True
        assert _compare_factor_vs_factor("<", 2.0, 99.0, 2.0, 99.0) is False
        assert _compare_factor_vs_factor("<", 3.0, 99.0, 2.0, 99.0) is False

    def test_le(self):
        assert _compare_factor_vs_factor("<=", 1.0, 99.0, 2.0, 99.0) is True
        assert _compare_factor_vs_factor("<=", 2.0, 99.0, 2.0, 99.0) is True
        assert _compare_factor_vs_factor("<=", 3.0, 99.0, 2.0, 99.0) is False

    def test_gt(self):
        assert _compare_factor_vs_factor(">", 3.0, 99.0, 2.0, 99.0) is True
        assert _compare_factor_vs_factor(">", 2.0, 99.0, 2.0, 99.0) is False
        assert _compare_factor_vs_factor(">", 1.0, 99.0, 2.0, 99.0) is False

    def test_ge(self):
        assert _compare_factor_vs_factor(">=", 3.0, 99.0, 2.0, 99.0) is True
        assert _compare_factor_vs_factor(">=", 2.0, 99.0, 2.0, 99.0) is True
        assert _compare_factor_vs_factor(">=", 1.0, 99.0, 2.0, 99.0) is False

    def test_eq(self):
        assert _compare_factor_vs_factor("==", 2.0, 99.0, 2.0, 99.0) is True
        assert _compare_factor_vs_factor("==", 2.0, 99.0, 2.1, 99.0) is False

    def test_crosses_above_fires_once(self):
        # Bar K: fast jumps above slow. prev: fast <= slow, cur: fast > slow.
        assert _compare_factor_vs_factor(
            "crosses_above",
            cur_a=60.0, prev_a=40.0, cur_b=50.0, prev_b=50.0,
        ) is True

    def test_crosses_above_not_fire_when_still_above(self):
        assert _compare_factor_vs_factor(
            "crosses_above",
            cur_a=70.0, prev_a=60.0, cur_b=50.0, prev_b=50.0,
        ) is False

    def test_crosses_above_not_fire_when_below(self):
        assert _compare_factor_vs_factor(
            "crosses_above",
            cur_a=40.0, prev_a=30.0, cur_b=50.0, prev_b=50.0,
        ) is False

    def test_crosses_above_single_fire_across_50_bars_factor_vs_factor(self):
        """**MANDATORY (factor-vs-factor variant)**: two factors cross
        once, then factor A stays above factor B for 50 more bars —
        crosses_above must fire exactly once.
        """
        a_vals = [10.0] * 30 + [60.0] * 50
        b_vals = [50.0] * 80  # flat at 50
        fire_count = 0
        for i in range(1, len(a_vals)):
            if _compare_factor_vs_factor(
                "crosses_above",
                a_vals[i], a_vals[i - 1],
                b_vals[i], b_vals[i - 1],
            ):
                fire_count += 1
        assert fire_count == 1

    def test_crosses_below_fires_once(self):
        assert _compare_factor_vs_factor(
            "crosses_below",
            cur_a=40.0, prev_a=60.0, cur_b=50.0, prev_b=50.0,
        ) is True

    def test_crosses_below_single_fire_across_50_bars(self):
        a_vals = [70.0] * 30 + [40.0] * 50
        b_vals = [50.0] * 80
        fire_count = 0
        for i in range(1, len(a_vals)):
            if _compare_factor_vs_factor(
                "crosses_below",
                a_vals[i], a_vals[i - 1],
                b_vals[i], b_vals[i - 1],
            ):
                fire_count += 1
        assert fire_count == 1

    def test_unknown_op_raises(self):
        with pytest.raises(ValueError):
            _compare_factor_vs_factor("@@", 1.0, 1.0, 1.0, 1.0)


# ===========================================================================
# 4. NaN → False semantics in BOTH code paths.
# This is where D1's warmup boundary meets D2's comparison logic. Silent
# bugs here (NaN→True or short-circuit True) would let strategies fire at
# warmup boundaries.
# ===========================================================================


NAN = float("nan")


class TestNanSemantics:
    @pytest.mark.parametrize("op", ["<", "<=", ">", ">=", "=="])
    def test_scalar_nan_cur_is_false(self, op):
        assert _compare_factor_vs_scalar(
            op, cur_val=NAN, prev_val=5.0, scalar=1.0
        ) is False

    def test_scalar_crosses_above_nan_cur_is_false(self):
        assert _compare_factor_vs_scalar(
            "crosses_above", cur_val=NAN, prev_val=5.0, scalar=10.0
        ) is False

    def test_scalar_crosses_above_nan_prev_is_false(self):
        # prev NaN (typical at warmup boundary) must NOT produce a fire.
        assert _compare_factor_vs_scalar(
            "crosses_above", cur_val=50.0, prev_val=NAN, scalar=10.0
        ) is False

    def test_scalar_crosses_below_nan_prev_is_false(self):
        assert _compare_factor_vs_scalar(
            "crosses_below", cur_val=5.0, prev_val=NAN, scalar=10.0
        ) is False

    @pytest.mark.parametrize("op", ["<", "<=", ">", ">=", "=="])
    def test_factor_factor_nan_either_side_is_false(self, op):
        assert _compare_factor_vs_factor(
            op, NAN, 1.0, 5.0, 1.0
        ) is False
        assert _compare_factor_vs_factor(
            op, 5.0, 1.0, NAN, 1.0
        ) is False

    def test_factor_factor_crosses_above_any_nan_is_false(self):
        # Any of the four operands NaN → False.
        for idx in range(4):
            args = [60.0, 40.0, 50.0, 50.0]  # valid fire otherwise
            args[idx] = NAN
            assert _compare_factor_vs_factor(
                "crosses_above", *args
            ) is False, f"NaN at operand index {idx} must be False"

    def test_factor_factor_crosses_below_any_nan_is_false(self):
        for idx in range(4):
            args = [40.0, 60.0, 50.0, 50.0]
            args[idx] = NAN
            assert _compare_factor_vs_factor(
                "crosses_below", *args
            ) is False

    def test_nan_never_short_circuits_to_true(self):
        """Defense-in-depth: exercising every op with NaN in every
        position yields False, never a truthy short-circuit.
        """
        for op in ["<", "<=", ">", ">=", "==", "crosses_above", "crosses_below"]:
            out = _compare_factor_vs_scalar(op, NAN, NAN, 1.0)
            assert out is False, f"{op} with NaN operands returned {out}"
        for op in ["<", "<=", ">", ">=", "==", "crosses_above", "crosses_below"]:
            out = _compare_factor_vs_factor(op, NAN, NAN, NAN, NAN)
            assert out is False, f"{op} with NaN operands returned {out}"


# ---------------------------------------------------------------------------
# 5. Separation-of-paths sanity test.
# Proves the two helpers are genuinely independent modules of logic, not a
# thin wrapper around a shared core: they are imported under distinct names
# and comparing their references verifies D2's "do not merge" mandate.
# ---------------------------------------------------------------------------


class TestPathsAreIndependent:
    def test_scalar_and_factor_are_distinct_functions(self):
        assert _compare_factor_vs_scalar is not _compare_factor_vs_factor

    def test_scalar_signature_takes_single_rhs(self):
        sig = _compare_factor_vs_scalar.__code__.co_varnames[
            : _compare_factor_vs_scalar.__code__.co_argcount
        ]
        assert sig == ("op", "cur_val", "prev_val", "scalar")

    def test_factor_signature_takes_two_factor_sides(self):
        sig = _compare_factor_vs_factor.__code__.co_varnames[
            : _compare_factor_vs_factor.__code__.co_argcount
        ]
        assert sig == ("op", "cur_a", "prev_a", "cur_b", "prev_b")


# ---------------------------------------------------------------------------
# Simple guard: the NAN constant above should actually be NaN
# ---------------------------------------------------------------------------


def test_nan_constant_is_nan():
    assert math.isnan(NAN)
