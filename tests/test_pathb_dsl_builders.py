# tests/test_pathb_dsl_builders.py
"""H1/H2/H3 DSL builder + compile tests (Tasks 1-3 of verdict-run build plan)."""
from __future__ import annotations

from backtest.pathb_eval_gauntlet import build_h1_dsl
from strategies.dsl_compiler import compile_dsl_to_strategy


def test_h1_conforms_to_lock():
    dsl = build_h1_dsl()
    # LOCK: max_hold_bars=3; entry = intrabar_push < -0.6 AND range_over_atr > 1.0
    assert dsl.max_hold_bars == 3
    entry_group = dsl.entry[0]
    triples = {(c.factor, c.op, c.value) for c in entry_group.conditions}
    assert ("intrabar_push", "<", -0.6) in triples
    assert ("range_over_atr", ">", 1.0) in triples
    # sizing unchanged: cdf_realized_vol_720 band [0.3,0.8]->1.0 else 0.5
    assert dsl.position_sizing.factor == "cdf_realized_vol_720"


def test_h1_compiles():
    compile_dsl_to_strategy(build_h1_dsl(), write_manifest=False)


# ---- Task 2: H2 ----

from backtest.pathb_eval_gauntlet import build_h2_dsl


def test_h2_regime_switch_structure():
    dsl = build_h2_dsl()
    # Two OR-connected groups: LOW (cdf<0.5 AND z<-1) ; HIGH (cdf>=0.5 AND z>+1)
    assert len(dsl.entry) == 2
    groups = [
        {(c.factor, c.op, c.value) for c in g.conditions} for g in dsl.entry
    ]
    low = {("cdf_realized_vol_720", "<", 0.5), ("zscore_48", "<", -1.0)}
    high = {("cdf_realized_vol_720", ">=", 0.5), ("zscore_48", ">", 1.0)}
    assert low in groups and high in groups
    assert dsl.position_sizing.factor == "cdf_realized_vol_720"  # single-factor (Decision 1)
    assert dsl.max_hold_bars == 24  # build-pinned time-stop exit


def test_h2_compiles():
    compile_dsl_to_strategy(build_h2_dsl(), write_manifest=False)


# ---- Task 3: H3 ----

from backtest.pathb_eval_gauntlet import build_h3_dsl


def test_h3_decay_trend_structure():
    dsl = build_h3_dsl()
    g = dsl.entry[0]
    triples = {(c.factor, c.op, c.value) for c in g.conditions}
    # factor-vs-factor: decay_linear_close_48 > decay_linear_close_168
    assert ("decay_linear_close_48", ">", "decay_linear_close_168") in triples
    # vol-CDF top-tail gate: cdf_realized_vol_720 <= 0.9
    assert ("cdf_realized_vol_720", "<=", 0.9) in triples
    assert dsl.position_sizing.factor == "cdf_realized_vol_720"
    assert dsl.max_hold_bars == 48


def test_h3_compiles():
    compile_dsl_to_strategy(build_h3_dsl(), write_manifest=False)


# ---- Task 3 step 4: build_all_hypotheses ----

def test_build_all_hypotheses_is_n_star_3():
    from backtest.pathb_eval_gauntlet import build_all_hypotheses
    h = build_all_hypotheses()
    assert set(h) == {"H1", "H2", "H3"}
    names = {d.name for d in h.values()}
    assert names == {"pathb_h1", "pathb_h2", "pathb_h3"}
