# tests/test_pathc_gauntlet.py
"""Path C basis hypothesis DSL builder tests (Phase C, Tasks C1-C3).

build_h1_dsl / build_h2_dsl / build_h3_dsl construct the LOCKed N*=3 basis
H-grid DSLs using the REAL DSL/compiler API:
  - Condition(value=...) for factor-vs-scalar and factor-vs-factor (NOT threshold);
  - OR-groups = a list of ConditionGroup;
  - compile via compile_dsl_to_strategy(dsl, write_manifest=False) (NOT compile_strategy);
  - referenced_factors(dsl) is a module-level helper (NOT dsl.referenced_factors()).

All parameter values are frozen by the Path C Step -1 pre-registration LOCK
(docs/superpowers/specs/2026-05-31-pathc-step-minus-1-preregistration-lock.md).
H1 has NO time-stop (inherits Path A Amendment-A1 by design).
H3 uses STRICT < on basis_pct_rank_2160 (exact partition with H1's >= theta tail).
"""

from __future__ import annotations

from backtest.pathc_eval_gauntlet import (
    build_all_hypotheses,
    build_h1_dsl,
    build_h2_dsl,
    build_h3_dsl,
    referenced_factors,
)
from strategies.dsl import SizingSpec
from strategies.dsl_compiler import compile_dsl_to_strategy


# ---------------------------------------------------------------------------
# Task C1: H1 basis_extreme_fade (De Morgan complement, no time-stop)
# ---------------------------------------------------------------------------


def test_h1_dsl_matches_lock_and_compiles():
    dsl = build_h1_dsl()
    assert dsl.position_sizing != "full_equity"  # ternary SizingSpec
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)  # REAL compiler API; must not raise
    assert cls is not None
    # H1 is long on the COMPLEMENT of the extreme tail (De Morgan: 2 OR entry-groups);
    # exit = the tail-gate group; NO time-stop (inherits Path A Amendment-A1 by design).
    facs = referenced_factors(dsl)  # helper walks dsl.entry / dsl.exit / dsl.position_sizing
    assert {"basis_pct_rank_2160", "basis_sign"} <= facs
    assert len(dsl.entry) == 2  # the two De Morgan OR-groups


def test_h1_no_time_stop():
    # H1 has NO time-stop — exit ONLY via the tail-gate (inherits Amendment-A1).
    dsl = build_h1_dsl()
    assert getattr(dsl, "max_hold_bars", None) in (None, 0)


def test_h1_entry_is_de_morgan_complement():
    dsl = build_h1_dsl()
    groups = [
        {(c.factor, c.op, c.value) for c in g.conditions} for g in dsl.entry
    ]
    # De Morgan of NOT(rank >= 0.90 AND sign > 0) = (rank < 0.90) OR (sign <= 0).
    assert {("basis_pct_rank_2160", "<", 0.90)} in groups
    assert {("basis_sign", "<=", 0.0)} in groups


def test_h1_exit_is_the_tail_gate():
    dsl = build_h1_dsl()
    # Single tail-gate exit group: (rank >= 0.90 AND sign > 0).
    assert len(dsl.exit) == 1
    triples = {(c.factor, c.op, c.value) for c in dsl.exit[0].conditions}
    assert ("basis_pct_rank_2160", ">=", 0.90) in triples
    assert ("basis_sign", ">", 0.0) in triples


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
# Task C2: H2 basis_regime_gate (max_hold 24)
# ---------------------------------------------------------------------------


def test_h2_dsl_matches_lock_and_compiles():
    dsl = build_h2_dsl()
    assert dsl.position_sizing != "full_equity"
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)
    assert cls is not None
    facs = referenced_factors(dsl)
    assert {
        "basis_ewm_240_pctrank_2160",
        "decay_linear_close_48",
        "decay_linear_close_168",
    } <= facs


def test_h2_permissive_entry_and_max_hold():
    dsl = build_h2_dsl()
    # PERMISSIVE long: regime pctrank < 0.80 AND decay_48 > decay_168 (price-trend confirm).
    assert len(dsl.entry) == 1
    triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    assert ("basis_ewm_240_pctrank_2160", "<", 0.80) in triples
    assert ("decay_linear_close_48", ">", "decay_linear_close_168") in triples
    # LOCK: max_hold_bars = 24.
    assert dsl.max_hold_bars == 24


def test_h2_de_risk_exit_present():
    dsl = build_h2_dsl()
    # Exit on de-risk regime (pctrank >= 0.80) / trend roll-over.
    exit_triples = set()
    for g in dsl.exit:
        exit_triples |= {(c.factor, c.op, c.value) for c in g.conditions}
    assert ("basis_ewm_240_pctrank_2160", ">=", 0.80) in exit_triples
    assert ("decay_linear_close_48", "<=", "decay_linear_close_168") in exit_triples


def test_h2_sizing_is_vol_cdf_ternary():
    dsl = build_h2_dsl()
    s = dsl.position_sizing
    assert isinstance(s, SizingSpec)
    assert s.factor == "cdf_realized_vol_720"
    assert (s.bands[0].lower, s.bands[0].upper, s.bands[0].size) == (0.3, 0.8, 1.0)
    assert s.default_size == 0.5


# ---------------------------------------------------------------------------
# Task C3: H3 basis_momentum_continuation (max_hold 48, STRICT < partition)
# ---------------------------------------------------------------------------


def test_h3_dsl_matches_lock_and_compiles():
    dsl = build_h3_dsl()
    assert dsl.position_sizing != "full_equity"
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)
    assert cls is not None
    facs = referenced_factors(dsl)
    assert {
        "basis_ewm_480",
        "basis_pct_rank_2160",
        "decay_linear_close_48",
        "decay_linear_close_168",
    } <= facs


def test_h3_entry_uses_strict_lt_on_pct_rank():
    # B2 exact-partition requirement: H3 entry uses STRICT < on basis_pct_rank_2160
    # (partitions with H1's >= theta flat-tail).
    dsl = build_h3_dsl()
    assert len(dsl.entry) == 1
    rank_cond = next(
        c for c in dsl.entry[0].conditions if c.factor == "basis_pct_rank_2160"
    )
    assert rank_cond.op == "<", (
        f"H3 entry basis_pct_rank_2160 must use STRICT '<' (exact partition with H1 >= theta); "
        f"got op={rank_cond.op!r}"
    )


def test_h3_entry_and_max_hold():
    dsl = build_h3_dsl()
    assert len(dsl.entry) == 1
    triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    # long when basis_ewm_480 > 0 AND pct_rank < 0.90 (strict, excludes H1's tail)
    # AND price-trend confirm.
    assert ("basis_ewm_480", ">", 0.0) in triples
    assert ("basis_pct_rank_2160", "<", 0.90) in triples
    assert ("decay_linear_close_48", ">", "decay_linear_close_168") in triples
    # LOCK: max_hold_bars = 48.
    assert dsl.max_hold_bars == 48


def test_h3_exit_groups():
    dsl = build_h3_dsl()
    # Exit OR-groups: basis_ewm_480 <= 0 / trend roll-over / pct_rank >= 0.90.
    exit_triples = set()
    for g in dsl.exit:
        exit_triples |= {(c.factor, c.op, c.value) for c in g.conditions}
    assert ("basis_ewm_480", "<=", 0.0) in exit_triples
    assert ("decay_linear_close_48", "<=", "decay_linear_close_168") in exit_triples
    assert ("basis_pct_rank_2160", ">=", 0.90) in exit_triples


def test_h3_exit_includes_pct_rank_ge_theta():
    # Explicit assertion: exit includes basis_pct_rank_2160 >= theta (LOCK).
    dsl = build_h3_dsl(theta=0.90)
    exit_triples = set()
    for g in dsl.exit:
        exit_triples |= {(c.factor, c.op, c.value) for c in g.conditions}
    assert ("basis_pct_rank_2160", ">=", 0.90) in exit_triples


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
    # H3 uses strict < on pct_rank vs H1's >= in the flat-tail gate.
    # Exact partition: H1's flat-gate fires at >= theta; H3 eligible at < theta.
    h1, h3 = build_h1_dsl(), build_h3_dsl()
    h3_entry = {(c.factor, c.op, c.value) for c in h3.entry[0].conditions}
    assert ("basis_pct_rank_2160", "<", 0.90) in h3_entry
    h1_exit = {(c.factor, c.op, c.value) for c in h1.exit[0].conditions}
    assert ("basis_pct_rank_2160", ">=", 0.90) in h1_exit


# ---------------------------------------------------------------------------
# build_all_hypotheses
# ---------------------------------------------------------------------------


def test_build_all_hypotheses_is_n_star_3():
    h = build_all_hypotheses()
    assert set(h) == {"H1", "H2", "H3"}
    names = {d.name for d in h.values()}
    assert names == {"pathc_h1", "pathc_h2", "pathc_h3"}


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
    assert ("basis_pct_rank_2160", ">=", 0.90) in triples


def test_h3_theta_default_is_0_90():
    dsl = build_h3_dsl()
    triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    assert ("basis_pct_rank_2160", "<", 0.90) in triples


def test_h1_theta_param_respected():
    # Fallback theta=0.85 must thread through entry and exit.
    dsl = build_h1_dsl(theta=0.85)
    entry_groups = [
        {(c.factor, c.op, c.value) for c in g.conditions} for g in dsl.entry
    ]
    assert {("basis_pct_rank_2160", "<", 0.85)} in entry_groups
    exit_triples = {(c.factor, c.op, c.value) for c in dsl.exit[0].conditions}
    assert ("basis_pct_rank_2160", ">=", 0.85) in exit_triples


def test_h3_theta_param_respected():
    # Fallback theta=0.85: entry strict < 0.85; exit >= 0.85.
    dsl = build_h3_dsl(theta=0.85)
    entry_triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    assert ("basis_pct_rank_2160", "<", 0.85) in entry_triples
    exit_triples = set()
    for g in dsl.exit:
        exit_triples |= {(c.factor, c.op, c.value) for c in g.conditions}
    assert ("basis_pct_rank_2160", ">=", 0.85) in exit_triples
