# Path B Verdict-Run Build — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the Path B harness's verdict-run build gaps (H2/H3 DSL builders, a Path-B holdout producer + integrity-gated moments loader, an end-to-end orchestrator) plus 2 LOCK-conformance fixes, so the harness is *run-ready* — without touching the forward_2026/validation/test verdict data (the RUN is the gated §6 step).

**Architecture:** Reuse the existing engine + DSL compiler + tier6 integrity gate. The 3 hypotheses compile through the *current* DSL (no schema change). Path B produces its OWN holdout artifacts in the dead-18 *layout* via `write_per_bar_artifact`, then loads them through the existing `load_candidate_moments` (sha256 + moment-recompute gate reused). The orchestrator composes the existing gauntlet/DSR/taxonomy modules; its engine calls are unit-tested with mocks so the build never touches verdict data.

**Tech Stack:** Python 3.11, pydantic v2 DSL, Backtrader engine, pytest. Governing pre-registration: [verdict-run build pre-registration](../specs/2026-05-30-pathb-verdict-run-build-preregistration-design.md) + [Step −1 LOCK](../specs/2026-05-30-pathb-step-minus-1-preregistration-lock.md) (FROZEN).

**Pre-registration discipline (READ FIRST):** This plan is committed BEFORE any build edit or data-touch. All builder/sizing/exit/moments code conforms to the frozen LOCK + the registered decisions (design §0/§4). Do NOT peek at any Step-0/gauntlet result and then refine a builder/sizing/exit — that is reverse-fitting and voids the cycle. The forward_2026 RUN is NOT a task in this plan.

**Build-pinned realizations flagged for the B2 review (unlocked by the LOCK):**
- **H2/H3 exit predicates** are pinned as **time-stop (`max_hold_bars`) exits** — per-leg signal-reversal exits are not cleanly expressible as OR-of-AND exit groups in the DSL. Pinned: H2 `max_hold_bars=24`, H3 `max_hold_bars=48`. (H1 keeps its LOCK time-stop=3 + reversion exit.)
- **H2/H3 sizing ladder edges** = single-factor `cdf_realized_vol_720` ternary `<0.5→1.0`, `≥0.5→0.5` (design §4①).

---

## File structure

| File | Responsibility | Action |
|---|---|---|
| `backtest/pathb_eval_gauntlet.py` | H1/H2/H3 DSL builders (was: H1 only) | Modify |
| `backtest/pathb_perleg_mechanism.py` | per-leg mechanism sanity (F5 regime-split fix) | Modify |
| `backtest/pathb_holdout_producer.py` | run a candidate on a window → dead-18-layout artifacts | Create |
| `backtest/pathb_moments.py` | load Path B moments via `load_candidate_moments` (integrity gate reuse) | Create |
| `backtest/pathb_orchestrator.py` | compose gauntlet → moments → DSR-FWER → perleg → evidence → escalation | Create |
| `scripts/pathb_run_verdict.py` | CLI for the gated RUN (built + smoke-tested with mocks; NOT executed here) | Create |
| `tests/test_pathb_dsl_builders.py` | H1/H2/H3 builder + compile tests | Create |
| `tests/test_pathb_perleg_mechanism.py` | F5 regime-split tests (extend existing if present) | Create/Modify |
| `tests/test_pathb_holdout_producer.py` | producer artifact-layout tests (mock engine) | Create |
| `tests/test_pathb_moments.py` | moments loader integrity tests | Create |
| `tests/test_pathb_orchestrator.py` | orchestrator composition tests (mock engine) | Create |

---

## Task 1 — H1 DSL → LOCK conformance (F6)

**Files:**
- Modify: `backtest/pathb_eval_gauntlet.py` (`build_hypothesis_dsl`, ~L52-84)
- Test: `tests/test_pathb_dsl_builders.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathb_dsl_builders.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_pathb_dsl_builders.py::test_h1_conforms_to_lock -v`
Expected: FAIL (`build_h1_dsl` not defined / `max_hold_bars==24`).

- [ ] **Step 3: Rename `build_hypothesis_dsl` → `build_h1_dsl` and fix to the LOCK**

In `backtest/pathb_eval_gauntlet.py`, rename the function and change the entry group + `max_hold_bars`:

```python
THETA_PUSH = -0.6
THETA_RANGE = 1.0  # LOCK: range_over_atr > 1.0 (meaningful displacement)
H1_MAX_HOLD = 3    # LOCK: max_hold_bars = 3


def build_h1_dsl() -> StrategyDSL:
    """H1 intrabar_push_fade, conforming to the Step -1 LOCK.

    Long when a large one-sided DOWN-push occurs at meaningful displacement
    (intrabar_push < -0.6 AND range_over_atr > 1.0); exit on reversion or
    after max_hold_bars=3. Vol-regime ternary sizing on cdf_realized_vol_720.
    """
    entry = ConditionGroup(conditions=[
        Condition(factor="intrabar_push", op="<", value=THETA_PUSH),
        Condition(factor="range_over_atr", op=">", value=THETA_RANGE),
    ])
    exit_grp = ConditionGroup(conditions=[
        Condition(factor="intrabar_push", op=">", value=0.0)
    ])
    sizing = SizingSpec(
        factor="cdf_realized_vol_720",
        bands=[SizingBand(lower=0.3, upper=0.8, size=1.0)],
        default_size=0.5,
    )
    return StrategyDSL(
        name="pathb_h1",
        description="Path B H1: fade a large-displacement one-sided down-push (mean-reversion), vol-regime ternary sizing.",
        entry=[entry],
        exit=[exit_grp],
        position_sizing=sizing,
        max_hold_bars=H1_MAX_HOLD,
    )
```

Update the import line to include `SizingBand`. Update `compile_hypothesis()` (~L109) to call `build_h1_dsl()`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_pathb_dsl_builders.py -v`
Expected: PASS (both H1 tests).

- [ ] **Step 5: Update any references to the old name**

Run: `rg "build_hypothesis_dsl" backtest/ scripts/ tests/`
For each hit, update to `build_h1_dsl`. Re-run the affected test files.

- [ ] **Step 6: Stage (do NOT commit — Option A controller-checkpoint gate)**

```bash
git add backtest/pathb_eval_gauntlet.py tests/test_pathb_dsl_builders.py
```

---

## Task 2 — H2 DSL builder (B1)

**Files:**
- Modify: `backtest/pathb_eval_gauntlet.py`
- Test: `tests/test_pathb_dsl_builders.py`

- [ ] **Step 1: Write the failing test**

```python
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
    from strategies.dsl_compiler import compile_dsl_to_strategy
    compile_dsl_to_strategy(build_h2_dsl(), write_manifest=False)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_pathb_dsl_builders.py::test_h2_regime_switch_structure -v`
Expected: FAIL (`build_h2_dsl` not defined).

- [ ] **Step 3: Implement `build_h2_dsl`**

```python
THETA_Z_LOW = -1.0
THETA_Z_HIGH = 1.0
VOL_REGIME_SPLIT = 0.5  # cdf_realized_vol_720 median split
H2_MAX_HOLD = 24        # build-pinned time-stop (per-leg signal exit not DSL-expressible)


def build_h2_dsl() -> StrategyDSL:
    """H2 vol_regime_switch: LOW-vol mean-revert OR HIGH-vol trend, long/flat.

    Entry (OR of two regime legs):
      LOW : cdf_realized_vol_720 < 0.5 AND zscore_48 < -1.0  (oversold-in-calm)
      HIGH: cdf_realized_vol_720 >= 0.5 AND zscore_48 > +1.0 (breakout-in-stress)
    Exit: time-stop max_hold_bars=24 (per-leg signal-reversal exit is not
    cleanly expressible as OR-of-AND exit groups; build-pinned, B2-reviewed).
    Sizing: single-factor cdf_realized_vol_720 inverse-vol ternary (Decision 1).
    """
    low = ConditionGroup(conditions=[
        Condition(factor="cdf_realized_vol_720", op="<", value=VOL_REGIME_SPLIT),
        Condition(factor="zscore_48", op="<", value=THETA_Z_LOW),
    ])
    high = ConditionGroup(conditions=[
        Condition(factor="cdf_realized_vol_720", op=">=", value=VOL_REGIME_SPLIT),
        Condition(factor="zscore_48", op=">", value=THETA_Z_HIGH),
    ])
    # Exit on REGIME FLIP (the switch is the edge) + time-stop. A single global
    # exit condition cannot serve both opposite-signed entry legs (a zscore exit
    # true for the LOW leg is also true at HIGH entry, closing it same-bar). The
    # regime-flip cross is leg-symmetric: a LOW-leg long (cdf<0.5) closes when
    # cdf crosses ABOVE 0.5; a HIGH-leg long (cdf>=0.5) closes when cdf crosses
    # BELOW 0.5. max_hold_bars=24 is the backstop.
    exit_up = ConditionGroup(conditions=[
        Condition(factor="cdf_realized_vol_720", op="crosses_above", value=VOL_REGIME_SPLIT)
    ])
    exit_down = ConditionGroup(conditions=[
        Condition(factor="cdf_realized_vol_720", op="crosses_below", value=VOL_REGIME_SPLIT)
    ])
    sizing = SizingSpec(
        factor="cdf_realized_vol_720",
        bands=[SizingBand(lower=0.0, upper=VOL_REGIME_SPLIT, size=1.0)],
        default_size=0.5,
    )
    return StrategyDSL(
        name="pathb_h2",
        description="Path B H2: vol-regime switch (low-vol revert / high-vol trend), long/flat, single-factor inverse-vol sizing.",
        entry=[low, high],
        exit=[exit_up, exit_down],
        position_sizing=sizing,
        max_hold_bars=H2_MAX_HOLD,
    )
```

> **B2 NOTE (build-pinned, review me):** H2 exit = regime-flip cross (leg-symmetric) + `max_hold_bars=24`. This is a coarse exit (a LOW-leg mean-revert ideally exits when `zscore_48` recovers, not only when vol regime flips), but it is unambiguous and avoids the same-bar-close bug a single zscore exit creates for the HIGH leg. Reviewers: confirm acceptable for a first pre-registered pass, or propose a cleaner per-leg exit. Sizing/exit affect holdout magnitude only — not the falsified mechanism (the switch).

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_pathb_dsl_builders.py -k h2 -v`
Expected: PASS.

- [ ] **Step 5: Stage**

```bash
git add backtest/pathb_eval_gauntlet.py tests/test_pathb_dsl_builders.py
```

---

## Task 3 — H3 DSL builder (B2)

**Files:**
- Modify: `backtest/pathb_eval_gauntlet.py`
- Test: `tests/test_pathb_dsl_builders.py`

- [ ] **Step 1: Write the failing test**

```python
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
    from strategies.dsl_compiler import compile_dsl_to_strategy
    compile_dsl_to_strategy(build_h3_dsl(), write_manifest=False)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_pathb_dsl_builders.py::test_h3_decay_trend_structure -v`
Expected: FAIL (`build_h3_dsl` not defined).

- [ ] **Step 3: Implement `build_h3_dsl`**

```python
DECAY_FAST = "decay_linear_close_48"
DECAY_SLOW = "decay_linear_close_168"
VOL_TOP_TAIL_GATE = 0.9  # LOCK: realized vol below its cdf_realized_vol_720 top-decile
H3_MAX_HOLD = 48         # build-pinned time-stop (trend held longer than H2)


def build_h3_dsl() -> StrategyDSL:
    """H3 decay_trend_persistence: long while fast decay-MA leads slow, ex top-vol.

    Entry: decay_linear_close_48 > decay_linear_close_168 (factor-vs-factor)
           AND cdf_realized_vol_720 <= 0.9 (not in the vol top-decile).
    Exit: trend break (fast <= slow) or time-stop max_hold_bars=48.
    Sizing: single-factor cdf_realized_vol_720 ternary (Decision 1).
    """
    entry = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op=">", value=DECAY_SLOW),
        Condition(factor="cdf_realized_vol_720", op="<=", value=VOL_TOP_TAIL_GATE),
    ])
    exit_grp = ConditionGroup(conditions=[
        Condition(factor=DECAY_FAST, op="<=", value=DECAY_SLOW)
    ])
    sizing = SizingSpec(
        factor="cdf_realized_vol_720",
        bands=[SizingBand(lower=0.0, upper=0.5, size=1.0)],
        default_size=0.5,
    )
    return StrategyDSL(
        name="pathb_h3",
        description="Path B H3: decay-MA trend persistence (fast leads slow), ex vol top-decile, single-factor sizing.",
        entry=[entry],
        exit=[exit_grp],
        position_sizing=sizing,
        max_hold_bars=H3_MAX_HOLD,
    )
```

- [ ] **Step 4: Add the registry helper + test**

```python
# In backtest/pathb_eval_gauntlet.py
def build_all_hypotheses() -> dict[str, StrategyDSL]:
    """The full N*=3 pre-registered grid (one variant each)."""
    return {"H1": build_h1_dsl(), "H2": build_h2_dsl(), "H3": build_h3_dsl()}
```

```python
# test
def test_build_all_hypotheses_is_n_star_3():
    from backtest.pathb_eval_gauntlet import build_all_hypotheses
    h = build_all_hypotheses()
    assert set(h) == {"H1", "H2", "H3"}
    names = {d.name for d in h.values()}
    assert names == {"pathb_h1", "pathb_h2", "pathb_h3"}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_pathb_dsl_builders.py -v`
Expected: PASS (all builder tests).

- [ ] **Step 6: Stage**

```bash
git add backtest/pathb_eval_gauntlet.py tests/test_pathb_dsl_builders.py
```

---

## Task 4 — F5: per-leg regime-split reconciliation

**Files:**
- Modify: `backtest/pathb_perleg_mechanism.py` (`compute_per_leg_mechanism`, ~L75-78)
- Test: `tests/test_pathb_perleg_mechanism.py`

**Why:** the H2 per-leg KILL is an earned-negative verdict input. The sanity table must split the regime on the *traded* gate `cdf_realized_vol_720 < 0.5`, not `realized_vol_24h` global median.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathb_perleg_mechanism.py
import numpy as np
import pandas as pd
from backtest.pathb_perleg_mechanism import compute_per_leg_mechanism


def test_regime_split_uses_cdf_factor_not_global_median():
    # Construct a frame where realized_vol_24h global-median split and
    # cdf_realized_vol_720<0.5 split disagree, and assert the LOW/HIGH
    # populations follow the cdf gate.
    n = 200
    df = pd.DataFrame({
        "zscore_48": np.linspace(-3, 3, n),
        "realized_vol_24h": np.linspace(0.01, 0.05, n),
        "cdf_realized_vol_720": np.r_[np.full(120, 0.2), np.full(80, 0.8)],
        "intrabar_push": np.zeros(n),
        "decay_linear_close_48": np.ones(n),
        "decay_linear_close_168": np.zeros(n),
        "fwd_ret": np.zeros(n),
    })
    out = compute_per_leg_mechanism(df)
    # LOW population = rows with cdf<0.5 (first 120) AND zscore<-1
    expected_low = int(((df["cdf_realized_vol_720"] < 0.5) & (df["zscore_48"] < -1.0)).sum())
    assert out["h2_low_leg_population"] == expected_low
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_pathb_perleg_mechanism.py::test_regime_split_uses_cdf_factor_not_global_median -v`
Expected: FAIL (current code splits on `realized_vol_24h.median()`).

- [ ] **Step 3: Reconcile the regime split**

In `compute_per_leg_mechanism`, replace the global-median split:

```python
    # Regime split on the TRADED gate cdf_realized_vol_720 < 0.5 (F5: the
    # per-leg KILL is an earned-negative verdict input, so the sanity table
    # must partition the regime exactly as the backtested DSL does — NOT by
    # realized_vol_24h global median).
    low_regime = df["cdf_realized_vol_720"] < 0.5
    high_regime = df["cdf_realized_vol_720"] >= 0.5
    low_mask = low_regime & (df["zscore_48"] < THETA_Z_LOW)
    high_mask = high_regime & (df["zscore_48"] > THETA_Z_HIGH)
```

Update the docstring's required-columns line (drop `volume_zscore_24h`; require `cdf_realized_vol_720`). Remove the now-unused `vol_med` line.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_pathb_perleg_mechanism.py -v`
Expected: PASS.

- [ ] **Step 5: Update any existing perleg tests that fed `realized_vol_24h`-only frames**

Run: `rg "compute_per_leg_mechanism" tests/`
For each existing test, ensure the input frame has a `cdf_realized_vol_720` column; fix as needed. Re-run.

- [ ] **Step 6: Stage**

```bash
git add backtest/pathb_perleg_mechanism.py tests/test_pathb_perleg_mechanism.py
```

---

## Task 5 — Path B holdout producer (B4, part 1)

**Files:**
- Create: `backtest/pathb_holdout_producer.py`
- Test: `tests/test_pathb_holdout_producer.py`

**Responsibility:** run ONE compiled candidate on a date window at the 15bps anchor and emit dead-18-layout artifacts (`<hash>/returns_per_bar.parquet`, `<hash>/holdout_summary.json`, and a cohort `holdout_results.csv` row) into a Path B namespace — so the existing `load_candidate_moments` can later consume them with its integrity gate. The engine call is injected (default `run_backtest`) so tests mock it and the build never touches verdict data.

- [ ] **Step 1: Write the failing test (engine mocked — no data touch)**

```python
# tests/test_pathb_holdout_producer.py
import json
from datetime import datetime, timezone
import pandas as pd
from backtest.pathb_holdout_producer import produce_candidate_holdout


def _fake_result(run_id="r1"):
    idx = pd.date_range("2026-01-01", periods=50, freq="h", tz="UTC")
    eq = pd.Series(10_000.0 * (1 + 0.0001) ** range(50), index=idx)
    class R:  # minimal BacktestResult stand-in
        pass
    r = R(); r.run_id = run_id; r.equity_curve = eq
    r.metrics = {"sharpe_ratio": 0.5, "total_trades": 12, "max_drawdown": 0.1, "total_return": 0.05}
    r.start_date = idx[0].to_pydatetime(); r.end_date = idx[-1].to_pydatetime()
    return r


def test_producer_writes_dead18_layout(tmp_path):
    dsl_hash = "abc123"
    out = produce_candidate_holdout(
        hypothesis_hash=dsl_hash,
        name="pathb_h1",
        theme="pathb",
        strategy_cls=object,  # unused — engine is mocked
        window=(datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 4, 16, 7, tzinfo=timezone.utc)),
        cohort_dir=tmp_path,
        execution_config_path="config/execution_phaseb_spot_15bps.yaml",
        _run_backtest=lambda **kw: _fake_result(),
    )
    cand_dir = tmp_path / dsl_hash
    assert (cand_dir / "returns_per_bar.parquet").exists()
    summary = json.loads((cand_dir / "holdout_summary.json").read_text())
    assert summary["evaluation_semantics"] == "single_run_holdout_v1"
    assert out["holdout_sharpe"] == 0.5
    assert out["row"]["hypothesis_hash"] == dsl_hash
    assert "returns_per_bar_sha256" in out["row"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_pathb_holdout_producer.py -v`
Expected: FAIL (module not found).

- [ ] **Step 3: Implement the producer**

```python
# backtest/pathb_holdout_producer.py
"""Path B holdout producer: run one candidate on a window -> dead-18-layout
artifacts (returns_per_bar.parquet + holdout_summary.json + a results.csv row),
so the existing tier6 load_candidate_moments integrity gate can consume them.

Writes ONLY into a Path B namespace; never the sealed cohort dirs. The engine
call is injected (default backtest.engine.run_backtest) for test isolation.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from backtest.engine import run_backtest, write_per_bar_artifact
from backtest.wf_lineage import EVALUATION_SEMANTICS_TAG

# Lineage constants the evaluation guard requires (mirror run_phase2c_evaluation_gate).
_ENGINE_COMMIT = "eb1c87f"  # CORRECTED_WF_ENGINE_COMMIT (verify against wf_lineage at impl time)
_ENGINE_LINEAGE = "wf-corrected-v1"


def _eval_lineage_metadata(current_git_sha: str) -> dict[str, Any]:
    return {
        "evaluation_semantics": EVALUATION_SEMANTICS_TAG,  # "single_run_holdout_v1"
        "engine_commit": _ENGINE_COMMIT,
        "engine_corrected_lineage": _ENGINE_LINEAGE,
        "lineage_check": "passed",
        "current_git_sha": current_git_sha,
        "artifact_schema_version": "phase2c_8_1",
        "regime_key": "evaluation_regimes.forward_2026",
        "regime_label": "forward_2026",
    }


def produce_candidate_holdout(
    *,
    hypothesis_hash: str,
    name: str,
    theme: str,
    strategy_cls: type,
    window: tuple[datetime, datetime],
    cohort_dir: Path,
    execution_config_path: str,
    current_git_sha: str = "PATHB_BUILD",
    _run_backtest: Callable[..., Any] = run_backtest,
    _write_per_bar: Callable[..., Any] = write_per_bar_artifact,
) -> dict[str, Any]:
    """Run one candidate on ``window`` and emit dead-18-layout artifacts.

    Returns a dict with ``holdout_sharpe`` and ``row`` (the holdout_results.csv
    row: hypothesis_hash, name, theme, T_obs, gamma3, gamma4,
    returns_per_bar_sha256, holdout_total_trades).
    """
    start, end = window
    cand_dir = Path(cohort_dir) / hypothesis_hash
    cand_dir.mkdir(parents=True, exist_ok=True)

    result = _run_backtest(
        strategy_cls=strategy_cls,
        start_date=start,
        end_date=end,
        execution_config_path=Path(execution_config_path),
        write_registry=False,
    )
    per_bar = _write_per_bar(
        equity_curve=result.equity_curve,
        artifact_dir=cand_dir,
        run_id=result.run_id,
    )

    summary = {
        "hypothesis_hash": hypothesis_hash,
        "name": name,
        "theme": theme,
        "run_id": result.run_id,
        "execution_config_path": execution_config_path,
        "forward_window_metadata": {
            "forward_window_start_utc": start.isoformat(),
            "forward_window_end_utc": end.isoformat(),
            "forward_bar_count": int(per_bar["T_obs"]),
        },
        **_eval_lineage_metadata(current_git_sha),
    }
    (cand_dir / "holdout_summary.json").write_text(__import__("json").dumps(summary, indent=1))

    # Codex-3d guard: write_per_bar_artifact returns gamma3/gamma4 = None for a
    # degenerate (flat / zero-variance) equity curve; load_candidate_moments
    # does float(row["gamma3"]) -> TypeError on None. Fail fast here so a
    # degenerate candidate surfaces as an explicit error, not a loader crash.
    if per_bar["gamma3"] is None or per_bar["gamma4"] is None:
        raise ValueError(
            f"candidate {hypothesis_hash}: degenerate per-bar returns "
            f"(gamma3/gamma4 is None; T_obs={per_bar['T_obs']}) — flat or "
            f"zero-variance equity; cannot build CandidateMoments."
        )

    row = {
        "hypothesis_hash": hypothesis_hash,
        "name": name,
        "theme": theme,
        "T_obs": int(per_bar["T_obs"]),
        "gamma3": per_bar["gamma3"],
        "gamma4": per_bar["gamma4"],
        "returns_per_bar_sha256": per_bar["returns_per_bar_sha256"],
        "holdout_total_trades": int(result.metrics.get("total_trades", 0)),
        "holdout_sharpe": float(result.metrics["sharpe_ratio"]),
    }
    return {"holdout_sharpe": float(result.metrics["sharpe_ratio"]), "row": row}
```

> **IMPL NOTE:** verify `_ENGINE_COMMIT`/`_ENGINE_LINEAGE`/`artifact_schema_version` against `backtest/wf_lineage.py` constants and a real dead-18 `holdout_summary.json` at implementation time; `check_evaluation_semantics_or_raise` must accept this summary (Task 7 asserts it).

- [ ] **Step 3b: Add the degenerate-equity (None gamma) guard test**

```python
def test_producer_raises_on_degenerate_equity(tmp_path):
    import pytest
    idx = pd.date_range("2026-01-01", periods=50, freq="h", tz="UTC")
    flat = pd.Series(10_000.0, index=idx)  # zero-variance -> gamma None
    class R: pass
    r = R(); r.run_id = "r"; r.equity_curve = flat
    r.metrics = {"sharpe_ratio": 0.0, "total_trades": 0}
    r.start_date = idx[0].to_pydatetime(); r.end_date = idx[-1].to_pydatetime()
    with pytest.raises(ValueError, match="degenerate per-bar returns"):
        produce_candidate_holdout(
            hypothesis_hash="deg", name="pathb_h1", theme="pathb",
            strategy_cls=object,
            window=(r.start_date, r.end_date), cohort_dir=tmp_path,
            execution_config_path="config/execution_phaseb_spot_15bps.yaml",
            _run_backtest=lambda **kw: r,
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_pathb_holdout_producer.py -v`
Expected: PASS (layout + degenerate-guard).

- [ ] **Step 5: Stage**

```bash
git add backtest/pathb_holdout_producer.py tests/test_pathb_holdout_producer.py
```

---

## Task 6 — Path B moments loader via integrity-gate reuse (B4, part 2 + Decision ③)

**Files:**
- Create: `backtest/pathb_moments.py`
- Test: `tests/test_pathb_moments.py`

**Responsibility:** assemble the cohort `holdout_results.csv` from producer rows and load each candidate's `CandidateMoments` through the EXISTING `load_candidate_moments` — reusing its sha256 + moment-recompute integrity gate (Decision ③). No bespoke moment math.

- [ ] **Step 1: Write the failing test (build a tiny real artifact, then load + tamper)**

```python
# tests/test_pathb_moments.py
import numpy as np, pandas as pd, hashlib
from pathlib import Path
from backtest.pathb_moments import build_cohort_csv, load_pathb_moments


def _write_candidate(cohort: Path, h: str):
    cand = cohort / h; cand.mkdir(parents=True)
    r = pd.Series(np.r_[np.nan, np.random.default_rng(0).normal(0, 0.01, 199)])
    pd.DataFrame({"return": r}).to_parquet(cand / "returns_per_bar.parquet")
    sha = hashlib.sha256((cand / "returns_per_bar.parquet").read_bytes()).hexdigest()
    rf = r[np.isfinite(r)]
    from scipy.stats import skew, kurtosis
    (cand / "holdout_summary.json").write_text(__import__("json").dumps({
        "evaluation_semantics": "single_run_holdout_v1", "engine_commit": "eb1c87f",
        "engine_corrected_lineage": "wf-corrected-v1", "lineage_check": "passed",
        "current_git_sha": "x", "artifact_schema_version": "phase2c_8_1",
        "regime_key": "evaluation_regimes.forward_2026", "regime_label": "forward_2026"}))
    return {"hypothesis_hash": h, "name": "pathb_h1", "theme": "pathb",
            "T_obs": int(len(rf)), "gamma3": float(skew(rf, bias=True)),
            "gamma4": float(kurtosis(rf, fisher=False, bias=True)),
            "returns_per_bar_sha256": sha, "holdout_total_trades": 10}


def test_load_pathb_moments_roundtrip(tmp_path):
    rows = [_write_candidate(tmp_path, "h1aaa")]
    df = build_cohort_csv(rows, tmp_path)
    cms = load_pathb_moments(["h1aaa"], df, tmp_path)
    assert len(cms) == 1 and cms[0].T > 0


def test_integrity_gate_fires_on_tamper(tmp_path):
    import pytest
    rows = [_write_candidate(tmp_path, "h1bbb")]
    df = build_cohort_csv(rows, tmp_path)
    # tamper the parquet after the sha was recorded
    (tmp_path / "h1bbb" / "returns_per_bar.parquet").write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="sha256 integrity mismatch"):
        load_pathb_moments(["h1bbb"], df, tmp_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_pathb_moments.py -v`
Expected: FAIL (module not found).

- [ ] **Step 3: Implement the loader (reuses `load_candidate_moments`)**

```python
# backtest/pathb_moments.py
"""Path B moments: assemble the cohort CSV from producer rows, then load each
CandidateMoments through the EXISTING tier6 integrity gate (Decision 3).

We do NOT recompute moments here — load_candidate_moments performs the sha256
verification + the independent gamma3/gamma4/T recompute, so Path B's moments
meet exactly the same integrity bar as the dead-18 cohort they are DSR-compared
against. Path B owns its OWN namespace; this never reads the sealed cohort.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from backtest.tier6_dsr import CandidateMoments, load_candidate_moments


def build_cohort_csv(rows: list[dict], cohort_dir: Path) -> pd.DataFrame:
    """Assemble + persist the Path B holdout_results.csv from producer rows."""
    df = pd.DataFrame(rows)
    (Path(cohort_dir) / "holdout_results.csv").write_text(df.to_csv(index=False))
    return df


def load_pathb_moments(
    hashes: list[str], df: pd.DataFrame, cohort_dir: Path
) -> list[CandidateMoments]:
    """Load each candidate's moments via the integrity-gated tier6 loader."""
    return [load_candidate_moments(h, df, holdout_dir=Path(cohort_dir)) for h in hashes]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_pathb_moments.py -v`
Expected: PASS (roundtrip + integrity-gate-fires).

- [ ] **Step 5: Stage**

```bash
git add backtest/pathb_moments.py tests/test_pathb_moments.py
```

---

## Task 7 — Pinned approximation-tempers field + orchestrator composition (B5)

**Files:**
- Modify: `backtest/pathb_earned_negative.py` (add the pinned `approximation_tempers` field)
- Create: `backtest/pathb_orchestrator.py`
- Test: `tests/test_pathb_earned_negative.py` (extend), `tests/test_pathb_orchestrator.py`

**Responsibility:** (a) carry the *pre-registered, build-pinned* approximation tempers into the canonical advisory bundle (not prose only — advisor Points 2/5, METHODOLOGY_NOTES §6); (b) compose the verdict pipeline as a pure function over injected stage callables, unit-testable with mocks (no data touch).

- [ ] **Step 0a: Write the failing temper-field test**

```python
# tests/test_pathb_earned_negative.py (extend)
from backtest.pathb_earned_negative import assemble_evidence, APPROXIMATION_TEMPERS


def test_assemble_evidence_carries_pinned_tempers():
    out = assemble_evidence(
        per_leg={"h1_sane": True}, n_tier5_pass=0, n_dsr_pass=0,
        step0_promotion_side_effect=False,
    )
    # the pinned, data-independent build approximations must be in the bundle
    assert out["approximation_tempers"] == list(APPROXIMATION_TEMPERS)
    assert any("sizing" in t for t in out["approximation_tempers"])
    assert any("exit" in t for t in out["approximation_tempers"])
```

- [ ] **Step 0b: Run test to verify it fails**

Run: `python -m pytest tests/test_pathb_earned_negative.py::test_assemble_evidence_carries_pinned_tempers -v`
Expected: FAIL (`APPROXIMATION_TEMPERS` not defined / key absent).

- [ ] **Step 0c: Add the pinned tempers to `pathb_earned_negative.py`**

```python
# Pinned BEFORE any data-touch (these describe build-pinned approximations of
# the Step -1 LOCK, not results). Surfaced in the advisory bundle so Charlie's
# §9 earned-negative read sees every conclusiveness temper in ONE place rather
# than buried in spec prose (advisor Points 2/5; METHODOLOGY_NOTES §6).
APPROXIMATION_TEMPERS = (
    # Decision 1: LOCK named a 2-factor sizing; realized single-factor cdf ladder.
    "sizing_single_factor_cdf_vs_locked_2factor",
    # H2 exit: regime-flip cross only (+ time-stop); the spec §5.2 natural
    # OR-exit's zscore-reverts leg was approximated away; 15bps cdf-0.5
    # boundary-whipsaw is a known downward pressure on H2 holdout_sharpe.
    "h2_exit_regime_flip_only_vs_natural_or_zscore_reverts",
)
```

In `assemble_evidence`, add `"approximation_tempers": list(APPROXIMATION_TEMPERS)` to the returned dict. Update the docstring to note a B-negative (esp. process-refuted) under these approximations is marginally less conclusive (F3 temper, now covering sizing AND the H2 exit).

- [ ] **Step 0d: Run test to verify it passes; fix the existing assemble_evidence tests**

Run: `python -m pytest tests/test_pathb_earned_negative.py -v`
Expected: PASS (new test + existing tests, which may need the new key added to their expected dicts).

- [ ] **Step 1: Write the failing test (all stages mocked)**

```python
# tests/test_pathb_orchestrator.py
from backtest.pathb_orchestrator import run_pathb_verdict


def test_orchestrator_composes_advisory_pipeline():
    # 3 candidates; 1 clears Tier-5 -> B_POSITIVE; escalation NOT warranted.
    fake_holdout = {
        "H1": {"holdout_sharpe": 0.3}, "H2": {"holdout_sharpe": -0.1}, "H3": {"holdout_sharpe": -0.2},
    }
    out = run_pathb_verdict(
        hypotheses={"H1": object(), "H2": object(), "H3": object()},
        run_gauntlet=lambda key, dsl: fake_holdout[key],
        build_moments=lambda holdouts: [],            # no DSR pass in this scenario
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"h1_sane": True, "h2_low_leg_sane": True,
                          "h2_high_leg_sane": False, "h3_sane": True},
        step0_lifted_any=False,
    )
    assert out["taxonomy"]["advisory_taxonomy"] == "b_positive"
    assert out["escalation"]["a_escalation_warranted"] is False
    assert out["n_tier5_pass"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_pathb_orchestrator.py -v`
Expected: FAIL (module not found).

- [ ] **Step 3: Implement the composition**

```python
# backtest/pathb_orchestrator.py
"""Path B verdict orchestrator (ADVISORY).

Pure composition over injected stage callables: per-candidate gauntlet ->
holdout_sharpe; build integrity-gated moments; DSR-FWER at N*=3; train-only
per-leg mechanism sanity; earned-negative taxonomy; A-escalation advisory.
The binding earned-negative read + A-escalation remain a Charlie register.
"""
from __future__ import annotations

from typing import Any, Callable

from backtest.pathb_dsr_fwer import run_dsr_fwer, PATHB_N_STAR
from backtest.pathb_earned_negative import assemble_evidence
from backtest.pathb_escalation import a_escalation_advisory


def run_pathb_verdict(
    *,
    hypotheses: dict[str, Any],
    run_gauntlet: Callable[[str, Any], dict],
    build_moments: Callable[[dict], list],
    run_dsr: Callable[[list], dict] = run_dsr_fwer,
    per_leg: Callable[[], dict],
    step0_lifted_any: bool,
) -> dict[str, Any]:
    """Compose the advisory verdict pipeline. Returns the evidence bundle."""
    holdouts = {key: run_gauntlet(key, dsl) for key, dsl in hypotheses.items()}
    n_tier5_pass = sum(1 for h in holdouts.values() if h["holdout_sharpe"] > 0)

    cms = build_moments(holdouts)
    dsr = run_dsr(cms) if cms else {"survivors": [], "rows": [], "n_star": PATHB_N_STAR}
    n_dsr_pass = len(dsr["survivors"])

    sanity = per_leg()
    taxonomy = assemble_evidence(
        per_leg=sanity,
        n_tier5_pass=n_tier5_pass,
        n_dsr_pass=n_dsr_pass,
        step0_promotion_side_effect=False,
    )
    escalation = a_escalation_advisory(
        taxonomy["advisory_taxonomy"], step0_lifted_any=step0_lifted_any
    )
    return {
        "holdouts": holdouts,
        "n_tier5_pass": n_tier5_pass,
        "n_dsr_pass": n_dsr_pass,
        "dsr": dsr,
        "per_leg": sanity,
        "taxonomy": taxonomy,
        "escalation": escalation,
    }
```

- [ ] **Step 4: Add a second scenario test (process-refuted → escalation warranted)**

```python
def test_orchestrator_process_refuted_warrants_escalation():
    out = run_pathb_verdict(
        hypotheses={"H1": object()},
        run_gauntlet=lambda key, dsl: {"holdout_sharpe": -0.4},
        build_moments=lambda h: [],
        run_dsr=lambda cms: {"survivors": [], "rows": [], "n_star": 3},
        per_leg=lambda: {"h1_sane": True, "h2_low_leg_sane": False,
                          "h2_high_leg_sane": False, "h3_sane": False},
        step0_lifted_any=False,
    )
    assert out["taxonomy"]["advisory_taxonomy"] == "process_refuted_for_this_grid"
    assert out["escalation"]["a_escalation_warranted"] is True
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_pathb_orchestrator.py -v`
Expected: PASS (both scenarios).

- [ ] **Step 6: Stage**

```bash
git add backtest/pathb_orchestrator.py tests/test_pathb_orchestrator.py
```

---

## Task 8 — Run CLI + sealed-invariant guard (built + mock-smoked; RUN is gated)

**Files:**
- Create: `scripts/pathb_run_verdict.py`
- Test: `tests/test_pathb_orchestrator.py` (add a CLI smoke with mocked stages)

**Responsibility:** the CLI that wires the REAL engine-backed stages into `run_pathb_verdict` and writes the advisory evidence to a Path B namespace. It is built + smoke-tested with mocks here; **executing it on forward_2026 is the gated §6 RUN, NOT a task in this plan.**

- [ ] **Step 1: Write the failing smoke test (stages mocked; assert namespace + sealed-guard)**

```python
def test_cli_smoke_writes_namespace_and_guards_sealed(tmp_path, monkeypatch):
    import scripts.pathb_run_verdict as cli
    # assert the sealed-dir guard rejects a sealed out-dir
    import pytest
    with pytest.raises(ValueError, match="sealed"):
        cli.assert_not_sealed(cli.SEALED_DIRS[0])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_pathb_orchestrator.py::test_cli_smoke_writes_namespace_and_guards_sealed -v`
Expected: FAIL (module/func not found).

- [ ] **Step 3: Implement the CLI skeleton + sealed-dir guard**

```python
# scripts/pathb_run_verdict.py
"""Gated RUN entry point for the Path B verdict (NOT auto-run by the build).

Wires real engine-backed stages into backtest.pathb_orchestrator.run_pathb_verdict
on the forward_2026 window at the 15bps spot anchor, writes advisory evidence to
data/phase2c_evaluation_gate/pathb_verdict_v1/. Executing this is a Charlie
register-event (design §6); the build only constructs + smoke-tests it.
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATHB_VERDICT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/pathb_verdict_v1"
FORWARD_WINDOW = (
    datetime(2026, 1, 1, 0, tzinfo=timezone.utc),
    datetime(2026, 4, 16, 7, tzinfo=timezone.utc),
)
ANCHOR = "config/execution_phaseb_spot_15bps.yaml"

# Sealed dirs that must NEVER be written (inode-identity guard).
SEALED_DIRS = [
    PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1",
    PROJECT_ROOT / "data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1",
]


def assert_not_sealed(out_dir: Path) -> None:
    """Raise if out_dir is (inode-identical to) any sealed artifact dir."""
    out = Path(out_dir)
    for sealed in SEALED_DIRS:
        if sealed.exists() and out.exists() and os.path.samefile(out, sealed):
            raise ValueError(f"refusing to write sealed dir {sealed}")
        if str(out.resolve()) == str(sealed.resolve()):
            raise ValueError(f"refusing to write sealed dir {sealed}")


def main() -> int:  # pragma: no cover - the gated RUN
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(PATHB_VERDICT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir)
    assert_not_sealed(out)
    raise SystemExit(
        "Path B verdict RUN is a Charlie register-event (design §6); "
        "this CLI is wired but not auto-executed by the build."
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
```

> **IMPL NOTE:** the real-stage wiring (`run_gauntlet` → compile + `run_walk_forward`/`run_regime_holdout`/`run_backtest` per stage; `build_moments` → Task 5 producer + Task 6 loader; `per_leg` → Task 4 on a train frame; `step0_lifted_any` → `scripts/pathb_step0_diagnostic.py`) is filled into `main()` BEFORE the gated RUN — but the build leaves `main()` raising the gate notice so no data is touched here.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_pathb_orchestrator.py -k cli_smoke -v`
Expected: PASS.

- [ ] **Step 5: Full suite + sealed-invariant re-verify**

Run: `python -m pytest -q` (expect prior baseline + the new tests; no failures)
Run: `shasum -a 256 data/phase2c_evaluation_gate/tier6_dsr_v1/*.csv data/phase2c_evaluation_gate/tier6_dsr_v1/*.json`
Expected: the 4 baseline sha256 unchanged (companion `0a7d98…`, results `8eecc6…`, mc `49646c…`, promotion `1803eb…`).

- [ ] **Step 6: Stage**

```bash
git add scripts/pathb_run_verdict.py tests/test_pathb_orchestrator.py
```

---

## Task 9 — Build-boundary B2 + run-readiness checkpoint

- [ ] **Step 1:** Full suite green (`python -m pytest -q`); record the new pass count vs the 2582 pc9 baseline.
- [ ] **Step 2:** Re-verify the sealed `tier6_dsr_v1/` sha256 (4/4 baseline-match) and that `phase4_forward_2026_15bps_v1/` is untouched.
- [ ] **Step 3:** Dispatch the **2-leg build-boundary B2** (Codex `codex:codex-rescue` + `quant-research-advisor`) on the implemented build; adjudicate findings (verify citations; push back on hallucinations).
- [ ] **Step 4:** Controller stages all tasks; **Charlie authorizes the build commit(s)** (Option A gate).
- [ ] **Step 5:** STOP. The forward_2026 verdict RUN is the **separate, Charlie-registered §6 step** — do NOT execute it as part of this plan.

---

## Self-review (run before B2)

- **Spec coverage:** B1→T2, B2→T3, B3/F6→T1, B4→T5+T6, B5→T7+T8, F5→T4; Decision ①→T2/T3 sizing; ②→T5 window/anchor; ③→T6 integrity reuse; pre-registration discipline→header. Run sequence §6 → T8/T9 (gated). ✔
- **Placeholders:** none — every code step shows code; IMPL NOTEs flag values to verify against real files at implementation time (not blanks).
- **Type consistency:** `build_h1_dsl/h2/h3` + `build_all_hypotheses`; `produce_candidate_holdout` returns `{holdout_sharpe,row}`; `build_cohort_csv`/`load_pathb_moments`; `run_pathb_verdict` consumes `assemble_evidence`/`a_escalation_advisory`/`run_dsr_fwer` (verified against the existing module signatures). ✔
