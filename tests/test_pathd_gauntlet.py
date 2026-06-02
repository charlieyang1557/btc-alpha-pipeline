# tests/test_pathd_gauntlet.py
"""Path D OI-axis hypothesis DSL builder tests (Phase D, Tasks C1-C3).

build_h1_dsl / build_h2_dsl / build_h3_dsl construct the LOCKed N*=3 OI
H-grid DSLs using the REAL DSL/compiler API:
  - Condition(value=...) for factor-vs-scalar and factor-vs-factor (NOT threshold);
  - OR-groups = a list of ConditionGroup;
  - compile via compile_dsl_to_strategy(dsl, write_manifest=False) (NOT compile_strategy);
  - referenced_factors(dsl) is a module-level helper (NOT dsl.referenced_factors()).

All parameter values are frozen by the Path D Step -1 pre-registration LOCK.
H1 is SIMPLER than Path C H1: NO sign conjunct, NO price-trend conjunct, NO
De Morgan, NO time-stop (inherits Amendment-A1).
H3 uses STRICT < on oi_pct_rank_2160 (exact partition with H1's >= theta tail).
H3 entry has NO extra price-return conjunct beyond the decay cross (graft fix).
"""

from __future__ import annotations

from backtest.pathd_eval_gauntlet import (
    build_all_hypotheses,
    build_h1_dsl,
    build_h2_dsl,
    build_h3_dsl,
    referenced_factors,
)
from strategies.dsl import SizingSpec
from strategies.dsl_compiler import compile_dsl_to_strategy


# ---------------------------------------------------------------------------
# Helper: extract the set of factor names referenced in ONLY the entry conditions
# (excludes sizing factor; use referenced_factors() for the full set including sizing).
# ---------------------------------------------------------------------------

def _entry_condition_factors(dsl) -> set[str]:
    """Factor names appearing in entry conditions only (LHS + factor-vs-factor RHS)."""
    names: set[str] = set()
    for group in dsl.entry:
        for cond in group.conditions:
            names.add(cond.factor)
            if isinstance(cond.value, str):
                names.add(cond.value)
    return names


# ---------------------------------------------------------------------------
# Task C1: H1 oi_extreme_fade (single entry group, no sign, no price-trend, no time-stop)
# ---------------------------------------------------------------------------


def test_h1_dsl_matches_lock_and_compiles():
    dsl = build_h1_dsl()
    assert dsl.position_sizing != "full_equity"  # ternary SizingSpec
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)  # REAL compiler API; must not raise
    assert cls is not None
    # H1: single entry group (no De Morgan — simpler than Path C), single exit group.
    assert len(dsl.entry) == 1
    assert len(dsl.exit) == 1


def test_h1_no_time_stop():
    # H1 has NO time-stop — exit ONLY via the tail-gate (inherits Amendment-A1).
    dsl = build_h1_dsl()
    assert getattr(dsl, "max_hold_bars", None) in (None, 0)


def test_h1_entry_condition_factors_exact():
    # H1 entry references ONLY oi_pct_rank_2160 (pure level-tail overlay).
    dsl = build_h1_dsl()
    assert _entry_condition_factors(dsl) == {"oi_pct_rank_2160"}


def test_h1_sizing_factor_in_referenced_factors():
    dsl = build_h1_dsl()
    assert "cdf_realized_vol_720" in referenced_factors(dsl)


def test_h1_entry_is_single_lt_group():
    dsl = build_h1_dsl()
    triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    assert ("oi_pct_rank_2160", "<", 0.90) in triples


def test_h1_exit_is_single_ge_group():
    dsl = build_h1_dsl()
    triples = {(c.factor, c.op, c.value) for c in dsl.exit[0].conditions}
    assert ("oi_pct_rank_2160", ">=", 0.90) in triples
    # No oi_sign, no decay cross in the exit (simpler than Path C H1).
    exit_factors = {c.factor for c in dsl.exit[0].conditions}
    assert exit_factors == {"oi_pct_rank_2160"}


def test_h1_sizing_is_vol_cdf_ternary():
    dsl = build_h1_dsl()
    s = dsl.position_sizing
    assert isinstance(s, SizingSpec)
    assert s.factor == "cdf_realized_vol_720"
    # band [0.3, 0.8) -> 1.0, else default 0.5
    assert len(s.bands) == 1
    band = s.bands[0]
    assert (band.lower, band.upper, band.size) == (0.3, 0.8, 1.0)
    assert s.default_size == 0.5


# ---------------------------------------------------------------------------
# Task C2: H2 oi_regime_gate (permissive + de-risk exits, max_hold 24)
# ---------------------------------------------------------------------------


def test_h2_dsl_matches_lock_and_compiles():
    dsl = build_h2_dsl()
    assert dsl.position_sizing != "full_equity"
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)
    assert cls is not None
    facs = referenced_factors(dsl)
    assert {
        "oi_velocity_ewm_240_pctrank_2160",
        "decay_linear_close_48",
        "decay_linear_close_168",
    } <= facs


def test_h2_permissive_entry_uses_oi_velocity_pctrank():
    dsl = build_h2_dsl()
    # PERMISSIVE long: oi_velocity_ewm_240_pctrank_2160 < 0.80 AND decay_48 > decay_168.
    assert len(dsl.entry) == 1
    triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    assert ("oi_velocity_ewm_240_pctrank_2160", "<", 0.80) in triples
    assert ("decay_linear_close_48", ">", "decay_linear_close_168") in triples


def test_h2_max_hold_is_24():
    dsl = build_h2_dsl()
    assert dsl.max_hold_bars == 24


def test_h2_de_risk_exit_present():
    dsl = build_h2_dsl()
    # Exit on de-risk regime (pctrank >= 0.80) / trend roll-over.
    exit_triples = set()
    for g in dsl.exit:
        exit_triples |= {(c.factor, c.op, c.value) for c in g.conditions}
    assert ("oi_velocity_ewm_240_pctrank_2160", ">=", 0.80) in exit_triples
    assert ("decay_linear_close_48", "<=", "decay_linear_close_168") in exit_triples


def test_h2_sizing_is_vol_cdf_ternary():
    dsl = build_h2_dsl()
    s = dsl.position_sizing
    assert isinstance(s, SizingSpec)
    assert s.factor == "cdf_realized_vol_720"
    assert (s.bands[0].lower, s.bands[0].upper, s.bands[0].size) == (0.3, 0.8, 1.0)
    assert s.default_size == 0.5


# ---------------------------------------------------------------------------
# Task C3: H3 oi_momentum_continuation (max_hold 48, STRICT < partition, graft fix)
# ---------------------------------------------------------------------------


def test_h3_dsl_matches_lock_and_compiles():
    dsl = build_h3_dsl()
    assert dsl.position_sizing != "full_equity"
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)
    assert cls is not None
    facs = referenced_factors(dsl)
    assert {
        "oi_velocity_ewm_240",
        "oi_pct_rank_2160",
        "decay_linear_close_48",
        "decay_linear_close_168",
    } <= facs


def test_h3_entry_condition_factors_exact():
    # H3 entry references EXACTLY these 4 factors (and NOTHING else —
    # the graft fix: no extra price-return conjunct beyond the decay cross).
    dsl = build_h3_dsl()
    assert _entry_condition_factors(dsl) == {
        "oi_velocity_ewm_240",
        "oi_pct_rank_2160",
        "decay_linear_close_48",
        "decay_linear_close_168",
    }


def test_h3_entry_uses_strict_lt_on_pct_rank():
    # B2 exact-partition requirement: H3 entry uses STRICT < on oi_pct_rank_2160
    # (partitions with H1's >= theta flat-tail).
    dsl = build_h3_dsl()
    assert len(dsl.entry) == 1
    rank_cond = next(
        c for c in dsl.entry[0].conditions if c.factor == "oi_pct_rank_2160"
    )
    assert rank_cond.op == "<", (
        f"H3 entry oi_pct_rank_2160 must use STRICT '<' (exact partition with H1 >= theta); "
        f"got op={rank_cond.op!r}"
    )


def test_h3_entry_and_max_hold():
    dsl = build_h3_dsl()
    assert len(dsl.entry) == 1
    triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    # long when oi_velocity_ewm_240 > 0 AND pct_rank < 0.90 (strict) AND price-trend.
    assert ("oi_velocity_ewm_240", ">", 0.0) in triples
    assert ("oi_pct_rank_2160", "<", 0.90) in triples
    assert ("decay_linear_close_48", ">", "decay_linear_close_168") in triples
    # LOCK: max_hold_bars = 48.
    assert dsl.max_hold_bars == 48


def test_h3_exit_groups():
    dsl = build_h3_dsl()
    # Exit OR-groups: oi_velocity_ewm_240 <= 0 / trend roll-over / pct_rank >= 0.90.
    exit_triples = set()
    for g in dsl.exit:
        exit_triples |= {(c.factor, c.op, c.value) for c in g.conditions}
    assert ("oi_velocity_ewm_240", "<=", 0.0) in exit_triples
    assert ("decay_linear_close_48", "<=", "decay_linear_close_168") in exit_triples
    assert ("oi_pct_rank_2160", ">=", 0.90) in exit_triples


def test_h3_exit_includes_pct_rank_ge_theta():
    # Explicit assertion: exit includes oi_pct_rank_2160 >= theta (LOCK).
    dsl = build_h3_dsl(theta=0.90)
    exit_triples = set()
    for g in dsl.exit:
        exit_triples |= {(c.factor, c.op, c.value) for c in g.conditions}
    assert ("oi_pct_rank_2160", ">=", 0.90) in exit_triples


def test_h3_sizing_factor_in_referenced_factors():
    dsl = build_h3_dsl()
    assert "cdf_realized_vol_720" in referenced_factors(dsl)


def test_h3_sizing_is_vol_cdf_ternary():
    dsl = build_h3_dsl()
    s = dsl.position_sizing
    assert isinstance(s, SizingSpec)
    assert s.factor == "cdf_realized_vol_720"
    assert (s.bands[0].lower, s.bands[0].upper, s.bands[0].size) == (0.3, 0.8, 1.0)
    assert s.default_size == 0.5


# ---------------------------------------------------------------------------
# H1 / H3 exact-partition complementarity
# ---------------------------------------------------------------------------


def test_h1_h3_exact_partition_at_theta():
    # H3 uses strict < on oi_pct_rank vs H1's >= in the flat-tail gate.
    # Exact partition: H1's flat-gate fires at >= theta; H3 eligible at < theta.
    h1, h3 = build_h1_dsl(), build_h3_dsl()
    h3_entry = {(c.factor, c.op, c.value) for c in h3.entry[0].conditions}
    assert ("oi_pct_rank_2160", "<", 0.90) in h3_entry
    h1_exit = {(c.factor, c.op, c.value) for c in h1.exit[0].conditions}
    assert ("oi_pct_rank_2160", ">=", 0.90) in h1_exit


# ---------------------------------------------------------------------------
# build_all_hypotheses
# ---------------------------------------------------------------------------


def test_build_all_hypotheses_is_n_star_3():
    h = build_all_hypotheses()
    assert set(h) == {"H1", "H2", "H3"}
    names = {d.name for d in h.values()}
    assert names == {"pathd_h1", "pathd_h2", "pathd_h3"}


def test_referenced_factors_includes_sizing_factor():
    # referenced_factors must walk position_sizing too (the sizing factor).
    for build in (build_h1_dsl, build_h2_dsl, build_h3_dsl):
        assert "cdf_realized_vol_720" in referenced_factors(build())


# ---------------------------------------------------------------------------
# Theta parameter plumbing (H1 and H3 accept theta kwarg, default 0.90)
# ---------------------------------------------------------------------------


def test_h1_theta_default_is_0_90():
    dsl = build_h1_dsl()
    triples = {(c.factor, c.op, c.value) for c in dsl.exit[0].conditions}
    assert ("oi_pct_rank_2160", ">=", 0.90) in triples


def test_h3_theta_default_is_0_90():
    dsl = build_h3_dsl()
    triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    assert ("oi_pct_rank_2160", "<", 0.90) in triples


def test_h1_theta_param_respected():
    # Fallback theta=0.85 must thread through entry and exit.
    dsl = build_h1_dsl(theta=0.85)
    entry_triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    assert ("oi_pct_rank_2160", "<", 0.85) in entry_triples
    exit_triples = {(c.factor, c.op, c.value) for c in dsl.exit[0].conditions}
    assert ("oi_pct_rank_2160", ">=", 0.85) in exit_triples


def test_h3_theta_param_respected():
    # Fallback theta=0.85: entry strict < 0.85; exit >= 0.85.
    dsl = build_h3_dsl(theta=0.85)
    entry_triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    assert ("oi_pct_rank_2160", "<", 0.85) in entry_triples
    exit_triples = set()
    for g in dsl.exit:
        exit_triples |= {(c.factor, c.op, c.value) for c in g.conditions}
    assert ("oi_pct_rank_2160", ">=", 0.85) in exit_triples
