# tests/test_patha_gauntlet.py
"""Path A funding hypothesis DSL builder tests (Phase C, Tasks C1-C3).

build_h1_dsl / build_h2_dsl / build_h3_dsl construct the LOCKed N*=3 funding
H-grid DSLs using the REAL DSL/compiler API:
  - Condition(value=...) for factor-vs-scalar and factor-vs-factor (NOT threshold);
  - OR-groups = a list of ConditionGroup;
  - compile via compile_dsl_to_strategy(dsl, write_manifest=False) (NOT compile_strategy);
  - referenced_factors(dsl) is a module-level helper (NOT dsl.referenced_factors()).

All parameter values are frozen by the Path A Step -1 pre-registration LOCK
(docs/superpowers/specs/2026-05-31-patha-step-minus-1-preregistration-lock.md),
including Amendment A1 (H1 has NO time-stop — exit only via the tail-gate).
"""

from __future__ import annotations

from backtest.patha_eval_gauntlet import (
    build_all_hypotheses,
    build_h1_dsl,
    build_h2_dsl,
    build_h3_dsl,
    referenced_factors,
)
from strategies.dsl import SizingSpec
from strategies.dsl_compiler import compile_dsl_to_strategy


# ---------------------------------------------------------------------------
# Task C1: H1 funding_extreme_fade
# ---------------------------------------------------------------------------


def test_h1_dsl_matches_lock_and_compiles():
    dsl = build_h1_dsl()
    assert dsl.position_sizing != "full_equity"  # ternary SizingSpec
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)  # REAL compiler API; must not raise
    assert cls is not None
    # H1 is long on the COMPLEMENT of the extreme tail (De Morgan: 2 OR entry-groups);
    # exit = the tail-gate group; NO time-stop (LOCK Amendment A1).
    facs = referenced_factors(dsl)  # helper walks dsl.entry / dsl.exit / dsl.position_sizing
    assert {"funding_pct_rank_270", "funding_sign"} <= facs
    assert len(dsl.entry) == 2  # the two De Morgan OR-groups


def test_h1_no_time_stop_amendment_a1():
    # Amendment A1: H1 has NO time-stop — exit ONLY via the tail-gate.
    dsl = build_h1_dsl()
    assert dsl.max_hold_bars is None


def test_h1_entry_is_de_morgan_complement():
    dsl = build_h1_dsl()
    groups = [
        {(c.factor, c.op, c.value) for c in g.conditions} for g in dsl.entry
    ]
    # De Morgan of NOT(rank >= 0.90 AND sign > 0) = (rank < 0.90) OR (sign <= 0).
    assert {("funding_pct_rank_270", "<", 0.90)} in groups
    assert {("funding_sign", "<=", 0.0)} in groups


def test_h1_exit_is_the_tail_gate():
    dsl = build_h1_dsl()
    # Single tail-gate exit group: (rank >= 0.90 AND sign > 0).
    assert len(dsl.exit) == 1
    triples = {(c.factor, c.op, c.value) for c in dsl.exit[0].conditions}
    assert ("funding_pct_rank_270", ">=", 0.90) in triples
    assert ("funding_sign", ">", 0.0) in triples


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
# Task C2: funding_ewm_30_pctrank_270 factor + H2 funding_sign_regime_switch
# ---------------------------------------------------------------------------


def test_h2_dsl_matches_lock_and_compiles():
    dsl = build_h2_dsl()
    assert dsl.position_sizing != "full_equity"
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)
    assert cls is not None
    facs = referenced_factors(dsl)
    assert {
        "funding_ewm_30_pctrank_270",
        "decay_linear_close_48",
        "decay_linear_close_168",
    } <= facs


def test_h2_permissive_entry_and_max_hold():
    dsl = build_h2_dsl()
    # PERMISSIVE long: ewm-pctrank < 0.80 AND decay_48 > decay_168 (price-trend confirm).
    assert len(dsl.entry) == 1
    triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    assert ("funding_ewm_30_pctrank_270", "<", 0.80) in triples
    assert ("decay_linear_close_48", ">", "decay_linear_close_168") in triples
    # LOCK: max_hold_bars = 24.
    assert dsl.max_hold_bars == 24


def test_h2_de_risk_exit_present():
    dsl = build_h2_dsl()
    # Exit on de-risk regime (ewm-pctrank >= 0.80) / trend roll-over.
    exit_triples = set()
    for g in dsl.exit:
        exit_triples |= {(c.factor, c.op, c.value) for c in g.conditions}
    assert ("funding_ewm_30_pctrank_270", ">=", 0.80) in exit_triples
    assert ("decay_linear_close_48", "<=", "decay_linear_close_168") in exit_triples


def test_h2_sizing_is_vol_cdf_ternary():
    dsl = build_h2_dsl()
    s = dsl.position_sizing
    assert isinstance(s, SizingSpec)
    assert s.factor == "cdf_realized_vol_720"
    assert (s.bands[0].lower, s.bands[0].upper, s.bands[0].size) == (0.3, 0.8, 1.0)
    assert s.default_size == 0.5


# ---------------------------------------------------------------------------
# Task C3: H3 funding_momentum_continuation
# ---------------------------------------------------------------------------


def test_h3_dsl_matches_lock_and_compiles():
    dsl = build_h3_dsl()
    assert dsl.position_sizing != "full_equity"
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)
    assert cls is not None
    facs = referenced_factors(dsl)
    assert {
        "funding_ewm_60",
        "funding_pct_rank_270",
        "decay_linear_close_48",
        "decay_linear_close_168",
    } <= facs


def test_h3_entry_and_max_hold():
    dsl = build_h3_dsl()
    assert len(dsl.entry) == 1
    triples = {(c.factor, c.op, c.value) for c in dsl.entry[0].conditions}
    # long when ewm_60 > 0 AND pct_rank <= 0.90 (excludes H1's tail) AND trend confirm.
    assert ("funding_ewm_60", ">", 0.0) in triples
    assert ("funding_pct_rank_270", "<=", 0.90) in triples
    assert ("decay_linear_close_48", ">", "decay_linear_close_168") in triples
    # LOCK: max_hold_bars = 48.
    assert dsl.max_hold_bars == 48


def test_h3_exit_groups():
    dsl = build_h3_dsl()
    # Exit OR-groups: ewm_60 <= 0 / trend roll-over / pct_rank > 0.90.
    exit_triples = set()
    for g in dsl.exit:
        exit_triples |= {(c.factor, c.op, c.value) for c in g.conditions}
    assert ("funding_ewm_60", "<=", 0.0) in exit_triples
    assert ("decay_linear_close_48", "<=", "decay_linear_close_168") in exit_triples
    assert ("funding_pct_rank_270", ">", 0.90) in exit_triples


def test_h1_h3_tail_complementarity():
    # H1/H3 are near-complementary on the funding tail: H3 uses pct_rank <= 0.90
    # (entry) vs H1's tail-gate >= 0.90 (flat). They overlap only at exactly
    # 0.90 (measure-zero on a continuous percentile); LOCK <=/>= kept as-is.
    h1, h3 = build_h1_dsl(), build_h3_dsl()
    h3_entry = {(c.factor, c.op, c.value) for c in h3.entry[0].conditions}
    assert ("funding_pct_rank_270", "<=", 0.90) in h3_entry
    h1_exit = {(c.factor, c.op, c.value) for c in h1.exit[0].conditions}
    assert ("funding_pct_rank_270", ">=", 0.90) in h1_exit


def test_h3_sizing_is_vol_cdf_ternary():
    dsl = build_h3_dsl()
    s = dsl.position_sizing
    assert isinstance(s, SizingSpec)
    assert s.factor == "cdf_realized_vol_720"
    assert (s.bands[0].lower, s.bands[0].upper, s.bands[0].size) == (0.3, 0.8, 1.0)
    assert s.default_size == 0.5


# ---------------------------------------------------------------------------
# build_all_hypotheses
# ---------------------------------------------------------------------------


def test_build_all_hypotheses_is_n_star_3():
    h = build_all_hypotheses()
    assert set(h) == {"H1", "H2", "H3"}
    names = {d.name for d in h.values()}
    assert names == {"patha_h1", "patha_h2", "patha_h3"}


def test_referenced_factors_includes_sizing_factor():
    # referenced_factors must walk position_sizing too (the sizing factor).
    for build in (build_h1_dsl, build_h2_dsl, build_h3_dsl):
        assert "cdf_realized_vol_720" in referenced_factors(build())
