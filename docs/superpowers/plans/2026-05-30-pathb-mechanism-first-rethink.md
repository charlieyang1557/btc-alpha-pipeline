# Path B — Mechanism-First OHLCV Re-Mine — Implementation Plan (v2, B2-corrected)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Revision note (v2):** A 3-leg B2 review of v1 found buildability defects (all grep-verified). v2 corrects: alphabetical `EXPECTED_FACTORS` (`list_names()` sorts); `Condition.value`/`StrategyDSL.description`; `splits.train_windows` (2022 excluded); DSR survivor = `pass_B`; Task 28 as a **per-candidate `evaluate_candidate` loop** (not `evaluate_cohort`, which hard-requires the 18/21 partition); a **sealed-dir hard-guard**; real API names (`compile_dsl_to_strategy`/`build_features_df`/`from_parquet`/`compute_feature_version`); the G3↔compiler schema reconcile; the G4 pre/post-factor split; and **2 new tasks** (H2 per-leg `mechanism_sane` producer; 15bps config cost-equivalence). The spec was also corrected (regime-holdout guard → `check_evaluation_semantics_or_raise`).

**Goal:** Test whether the prior broad-search *process* (not the OHLCV data) was destroying edge, by re-mining existing OHLCV with cost-aware selection + a min-trade-count/occupancy floor + a ternary sizing node + the single-asset WorldQuant-101 time-series subset, across 3 pre-registered mechanism-first hypotheses, evaluated under DSR-FWER at a re-locked N\* — producing an *earned negative* (or a confirmed B-positive) at the 15bps spot anchor.

**Architecture:** Guards-first (build the leakage cage before any new operator exists). `decay_linear` is a compute **primitive** feeding registered factors — *not* a DSL grammar change; the only DSL grammar change is a **ternary sizing node** (`SizingSpec`). N\* is made re-lockable per cohort with the sealed `tier6_dsr_v1` artifacts left byte-untouched. Path B produces its **own** evaluation artifacts, with the correct `wf_lineage` guard pinned per step. A human **Step −1 pre-registration register-event** locks the hypotheses + full variant grid (→ N\*), the gate, the floor values, and the kill-criterion **before any diagnostic or build**.

**Tech Stack:** Python 3.11, pandas, Backtrader, pydantic v2, scipy, pyarrow/parquet, pytest.

**Spec:** [docs/superpowers/specs/2026-05-30-pathb-mechanism-first-rethink-design.md](../specs/2026-05-30-pathb-mechanism-first-rethink-design.md) (v2.1, B2-adopted, Charlie-registered 2026-05-30).

**Cost anchor (HARD CONSTRAINT):** `config/execution_phaseb_spot_15bps.yaml` — 15 bps/side. Never relaxed.

---

## ⚠️ Commit & authorization discipline (read before executing)

- Every task ends with a `git commit` step. **Execution of those commits waits for explicit Charlie authorization** (only Charlie-register authorizes operational fires). A task subagent may stage the work; the actual commit/push happens on Charlie's go.
- **Step −1 (pre-registration) is a separate Charlie register-event** that must precede Step 0. Do not begin Step 0 (the pre-B diagnostic) until the four pre-registrations are locked (see below).
- Run the relevant pytest subset after every `.py` edit; never commit failing tests. Full suite baseline: **2484 passed / 2 xfailed**.
- This plan is pending **re-B2 → Charlie register** before any task is executed.

---

## Step −1 — Pre-registration register-event (HUMAN gate, not code)

Before any diagnostic or build, Charlie locks (its own register-event):

1. **Hypotheses + full variant grid → N\*.** The exact H1/H2/H3 DSL parameter values (H1's `THETA_PUSH`, `THETA_RANGE`, `H1_HOLD`, vol band; H2's regime split + z thresholds; H3's decay horizons + vol-tail gate) **and** every enumerated variant. `N\* = |full considered grid|` (not just variants run). No post-hoc additions — adding a variant after seeing Step-0/Step-4 results voids N\*.
2. **Gate.** 15bps anchor + DSR-FWER (Form B) + Tier-5 `holdout_sharpe > 0` entry. Locked, never revisited.
3. **Process-delta.** Cost-aware objective; the hypothesis-class floor values (H1 event-count floor; H2/H3 occupancy + trade-count floor); the ternary ladder.
4. **Kill-criterion taxonomy** (mechanism-refuted / process-refuted-for-this-grid / not-OHLCV-exhausted) + the objective A-escalation trigger.

The coding tasks below reference these locked values **symbolically** (e.g. `THETA_PUSH`, `PATHB_N_STAR`); the executor substitutes the locked numbers at Step 3.

---

## File-structure map

| File | New/Mod | Responsibility |
|---|---|---|
| `factors/operators.py` | **new** | `decay_linear(series, window)` + `rolling_backward_percentile(series, window)` causal primitives (top-level, no lambda) |
| `factors/registry.py` | mod | `_assert_no_future_ops` (G1) called in `register()`; register the 5 new factors in `_bootstrap_core_factors` |
| `factors/volatility.py` | mod | `compute_range_over_atr`, `compute_cdf_realized_vol_720` + SPECs |
| `factors/moving_averages.py` | mod | `compute_decay_linear_close_48/168` + SPECs |
| `factors/price.py` | mod | `compute_intrabar_push` + SPEC |
| `strategies/dsl.py` | mod | `SizingSpec` model; `position_sizing: Literal["full_equity"] \| SizingSpec` |
| `strategies/dsl_compiler.py` | mod | `_compile_sizing(spec, factor_index)` closure; emit via `order_target_percent` |
| `agents/hypothesis_hash.py` | mod | `_canonical_position_sizing` keeps `SizingSpec` in the D3 canonical payload |
| `backtest/tier6_dsr.py` | mod | thread `n_star` through `evaluate_cohort` + `_degenerate_fail_row` + CLI `--n-star` + sealed-dir hard-guard; sealed `tier6_dsr_v1` untouched |
| `scripts/pathb_step0_diagnostic.py` | **new** | Step 0 read-only re-score (advisory; Path B namespace; 15bps preflight; no promotion side-effect) |
| `scripts/pathb_evaluate.py` | **new** | Steps 3–5: compile hypotheses, sanity table, per-leg evidence, eval gauntlet (per-step `wf_lineage`), per-candidate DSR-FWER, taxonomy, A-trigger |
| `tests/test_leakage_guards.py` | **new** | G1–G4 |
| `tests/test_factors.py` | mod | new-factor tests; alphabetical `EXPECTED_FACTORS`; registry-derived invariance |
| `tests/test_dsl.py`, `tests/test_dsl_integration.py` | mod | ternary node schema + compiled-through-engine |
| `tests/test_tier6_dsr.py` | mod | `n_star` plumbing + sealed-dir guard + sealed-artifact regression |

---

## Task sequence (maps to spec Steps 1 → 5; Step 0 wired in Section E, gated on Step −1)

- **Section A (Tasks 1–4):** Leakage guard-rails (Step 1) — land first. Task 4 = G4a generic registry-sync guard (pre-factor); the Path B factor-presence guard is Task 4b inside Section B.
- **Section B (Tasks 5–12):** `decay_linear` primitive + 5 factors + Task 4b presence guard (Step 2).
- **Section C (Tasks 13–18):** Ternary sizing node (Step 2).
- **Section D (Tasks 19–22):** N\* plumbing + sealed-dir guard (Step 2).
- **Section E (Tasks 23–30):** Step 0 diagnostic (23), config cost-equivalence (24, **new**), train-only sanity table (25), H2 per-leg `mechanism_sane` producer (26, **new**), hypothesis compile + eval gauntlet (27), per-candidate DSR-FWER at re-locked N\* (28), earned-negative taxonomy (29), A-escalation trigger (30).

---

## Section A — Leakage Guard-Rails (Step 1)

I now have all the real signatures. The `_compile_sizing(spec, factor_index) -> closure (cur_row, prev_row) -> float` mirrors `_compile_condition`'s `(cur_row, prev_row) -> bool` shape exactly. I have everything needed to write Section A with real, buildable code.

### Task 1: G1 leakage scanner — `_assert_no_future_ops` + first verify all 18 existing factors pass

**Files:** Create/Modify: `factors/registry.py` · Test: `tests/test_leakage_guards.py`

- [ ] **Step 1: Write the failing test** — the FIRST assertion is that all 18 already-registered factors pass the new scanner, so the guard cannot ship if it false-positives on the existing causal corpus.

```python
# tests/test_leakage_guards.py
"""Leakage guards G1-G4 for the Path B factor + sizing extension.

G1 (this file, Task 1): static AST scan banning future-touching ops inside
factor compute functions, wired into FactorRegistry.register().
G2 (Task 2): registry-derived shuffle/reverse/delete sentinel.
G3 (Task 3): per-operator known-value + ternary-sizing causality.
G4a (Task 4a): generic registry<->EXPECTED_FACTORS sync + future-bar invariance.
"""
from __future__ import annotations

import ast
import textwrap

import numpy as np
import pandas as pd
import pytest

from factors.registry import (
    FactorRegistry,
    FactorSpec,
    _assert_no_future_ops,
    _bootstrap_core_factors,
)


@pytest.fixture
def core_registry() -> FactorRegistry:
    reg = FactorRegistry()
    _bootstrap_core_factors(reg)
    return reg


class TestG1ExistingCorpusClean:
    """G1 must NOT false-positive on the already-registered causal factors.

    This is the load-bearing first check: if the scanner rejects any of the
    legitimately-causal existing compute functions, it is unusable as a
    register()-time gate. Run this BEFORE trusting any positive detection.
    """

    def test_all_registered_factors_pass_scanner(self, core_registry):
        names = core_registry.list_names()
        assert len(names) >= 18
        for name in names:
            spec = core_registry.get(name)
            # Must not raise — every shipped factor is causal by construction.
            _assert_no_future_ops(spec.compute, name)


class TestG1BannedOps:
    """G1 must reject each future-touching construct."""

    def test_negative_shift_rejected(self):
        def compute_bad_shift(df: pd.DataFrame) -> pd.Series:
            return df["close"].shift(-1)

        with pytest.raises(ValueError, match="shift"):
            _assert_no_future_ops(compute_bad_shift, "bad_shift")

    def test_bfill_rejected(self):
        def compute_bad_bfill(df: pd.DataFrame) -> pd.Series:
            return df["close"].bfill()

        with pytest.raises(ValueError, match="bfill|backfill"):
            _assert_no_future_ops(compute_bad_bfill, "bad_bfill")

    def test_fillna_bfill_method_rejected(self):
        def compute_bad_fillna(df: pd.DataFrame) -> pd.Series:
            return df["close"].fillna(method="bfill")

        with pytest.raises(ValueError, match="bfill|backfill|fillna"):
            _assert_no_future_ops(compute_bad_fillna, "bad_fillna")

    def test_rolling_center_true_rejected(self):
        def compute_bad_center(df: pd.DataFrame) -> pd.Series:
            return df["close"].rolling(24, center=True).mean()

        with pytest.raises(ValueError, match="center"):
            _assert_no_future_ops(compute_bad_center, "bad_center")

    def test_bare_expanding_rejected(self):
        def compute_bad_expanding(df: pd.DataFrame) -> pd.Series:
            return df["close"].expanding().mean()

        with pytest.raises(ValueError, match="expanding"):
            _assert_no_future_ops(compute_bad_expanding, "bad_expanding")

    def test_full_series_mean_rejected(self):
        def compute_bad_globalmean(df: pd.DataFrame) -> pd.Series:
            return df["close"] - df["close"].mean()

        with pytest.raises(ValueError, match="mean|full-series|global"):
            _assert_no_future_ops(compute_bad_globalmean, "bad_globalmean")


class TestG1AllowedOps:
    """G1 must ALLOW legitimate causal constructs."""

    def test_rolling_mean_allowed(self):
        def compute_ok_rolling(df: pd.DataFrame) -> pd.Series:
            return df["close"].rolling(24).mean()

        _assert_no_future_ops(compute_ok_rolling, "ok_rolling")  # no raise

    def test_ewm_adjust_false_allowed(self):
        def compute_ok_ewm(df: pd.DataFrame) -> pd.Series:
            return df["close"].ewm(span=12, adjust=False).mean()

        _assert_no_future_ops(compute_ok_ewm, "ok_ewm")  # no raise

    def test_positive_shift_allowed(self):
        def compute_ok_shift(df: pd.DataFrame) -> pd.Series:
            return df["close"] - df["close"].shift(1)

        _assert_no_future_ops(compute_ok_shift, "ok_shift")  # no raise

    def test_expanding_min_periods_chained_mean_allowed(self):
        def compute_ok_expanding(df: pd.DataFrame) -> pd.Series:
            return df["close"].expanding(min_periods=24).mean()

        _assert_no_future_ops(compute_ok_expanding, "ok_expanding")  # no raise


class TestG1WiredIntoRegister:
    """register() invokes G1 so a leaky factor cannot be registered."""

    def test_register_rejects_leaky_factor(self):
        reg = FactorRegistry()

        def compute_leaky(df: pd.DataFrame) -> pd.Series:
            return df["close"].shift(-1)

        spec = FactorSpec(
            name="leaky_demo",
            category="test",
            warmup_bars=0,
            inputs=["close"],
            output_dtype="float64",
            compute=compute_leaky,
            docstring="Leaky demo factor (must be rejected).",
        )
        with pytest.raises(ValueError, match="shift"):
            reg.register(spec)
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_leakage_guards.py::TestG1ExistingCorpusClean -v`
  `Expected: FAIL — ImportError: cannot import name '_assert_no_future_ops' from 'factors.registry'`

- [ ] **Step 3: Implement** — add `_assert_no_future_ops` to `factors/registry.py` (`ast` + `textwrap` already imported at lines 25/29) and call it from `register()`.

```python
# factors/registry.py — insert after _assert_top_level_callable (≈ line 137)

_FULL_SERIES_REDUCERS = frozenset({"mean", "std", "sum", "rank"})
# Attribute names that, when seen as the *receiver* of one of the reducers
# above, mean the reducer is a windowed/causal reduction and is ALLOWED.
_WINDOWED_RECEIVERS = frozenset({"rolling", "ewm", "expanding"})


def _assert_no_future_ops(fn: Callable, factor_name: str) -> None:
    """Static AST scan rejecting future-touching ops in a factor's source.

    Banned:
      - ``shift(k)`` with a negative integer literal ``k`` (look-ahead).
      - ``bfill`` / ``backfill`` calls.
      - ``fillna(method='bfill')`` / ``fillna(method='backfill')``.
      - ``rolling(..., center=True)`` (uses trailing AND leading bars).
      - bare ``expanding()`` with no ``min_periods`` argument.
      - full-Series reducers ``.mean()/.std()/.sum()/.rank()`` whose
        receiver is NOT a ``rolling/ewm/expanding(...)`` call (i.e. a
        global aggregation over the whole series).

    Allowed: ``rolling(N).mean()``, ``ewm(span=N, adjust=False).mean()``,
    ``expanding(min_periods=N).mean()``, positive ``shift(k)``.

    This is a CONSERVATIVE static check: it inspects the compute function's
    own source via ``inspect.getsource`` + ``ast``. It cannot follow calls
    into helper functions, which is acceptable because factor compute
    functions are required to be self-contained top-level callables (see
    :func:`_assert_top_level_callable`). Compute PRIMITIVES in
    ``factors/operators.py`` are deliberately NOT registered, so this
    scanner never runs against them.

    Raises ``ValueError`` naming the offending construct.
    """
    src = textwrap.dedent(inspect.getsource(fn))
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        attr = func.attr

        # shift(<negative literal>)
        if attr == "shift" and node.args:
            arg = node.args[0]
            if (
                isinstance(arg, ast.UnaryOp)
                and isinstance(arg.op, ast.USub)
                and isinstance(arg.operand, ast.Constant)
                and isinstance(arg.operand.value, (int, float))
            ):
                raise ValueError(
                    f"Factor {factor_name!r}: negative shift() is a "
                    f"look-ahead op (shift({-arg.operand.value!r}* negated))."
                )

        # bfill / backfill
        if attr in ("bfill", "backfill"):
            raise ValueError(
                f"Factor {factor_name!r}: {attr}() back-fills from future "
                f"bars and is prohibited."
            )

        # fillna(method='bfill'|'backfill')
        if attr == "fillna":
            for kw in node.keywords:
                if (
                    kw.arg == "method"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value in ("bfill", "backfill")
                ):
                    raise ValueError(
                        f"Factor {factor_name!r}: fillna(method="
                        f"{kw.value.value!r}) back-fills from future bars."
                    )

        # rolling(..., center=True)
        if attr == "rolling":
            for kw in node.keywords:
                if (
                    kw.arg == "center"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value is True
                ):
                    raise ValueError(
                        f"Factor {factor_name!r}: rolling(center=True) reads "
                        f"leading (future) bars and is prohibited."
                    )

        # bare expanding() — no min_periods bound excluding future bars
        if attr == "expanding":
            has_minp = any(kw.arg == "min_periods" for kw in node.keywords)
            has_posarg = len(node.args) >= 1
            if not has_minp and not has_posarg:
                raise ValueError(
                    f"Factor {factor_name!r}: bare expanding() is prohibited; "
                    f"use expanding(min_periods=N)."
                )

        # full-series reducer not chained off a windowed receiver
        if attr in _FULL_SERIES_REDUCERS:
            recv = func.value
            windowed = (
                isinstance(recv, ast.Call)
                and isinstance(recv.func, ast.Attribute)
                and recv.func.attr in _WINDOWED_RECEIVERS
            )
            if not windowed:
                raise ValueError(
                    f"Factor {factor_name!r}: full-series .{attr}() is a "
                    f"global aggregation; use a windowed "
                    f"rolling/ewm/expanding(min_periods=) reduction instead."
                )
```

Then wire it into `register()`:

```python
# factors/registry.py — FactorRegistry.register (line 152)

    def register(self, spec: FactorSpec) -> None:
        """Register a factor. Duplicate names are rejected.

        G1 leakage gate: the compute function's source is statically scanned
        for future-touching operations before the factor is admitted.
        """
        if spec.name in self._specs:
            raise ValueError(
                f"Factor name collision: {spec.name!r} already registered"
            )
        _assert_no_future_ops(spec.compute, spec.name)
        self._specs[spec.name] = spec
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_leakage_guards.py -v && pytest tests/test_factors.py -q`
  `Expected: PASS — all G1 tests green; existing factor suite still green (the 18 shipped factors pass the scanner, so register() does not regress).`

- [ ] **Step 5: Commit** — `git add factors/registry.py tests/test_leakage_guards.py && git commit -m "feat(pathb-g1): static AST future-op scanner wired into FactorRegistry.register; verified clean on all 18 existing factors"`

---

### Task 2: G2 — registry-derived shuffle / reverse / delete sentinel

**Files:** Modify: `factors/registry.py` (sentinel helper) · Test: `tests/test_leakage_guards.py`

- [ ] **Step 1: Write the failing test** — parametrize over `registry.list_names()` so the sentinel auto-covers every registered factor (including the 5 Path B additions once Section B lands). The sentinel proves each factor is order-/shuffle-/reverse-/delete-sensitive in the way a causal series must be: a future-leaking factor would be invariant to a one-row deletion at the tail of its input.

```python
# tests/test_leakage_guards.py — append

def _synthetic_ohlcv(n: int = 800, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2021-01-01", periods=n, freq="1h", tz="UTC")
    close = 30000.0 + np.cumsum(rng.normal(0, 50, n))
    high = close + np.abs(rng.normal(0, 30, n))
    low = close - np.abs(rng.normal(0, 30, n))
    open_ = close - rng.normal(0, 20, n)
    vol = np.abs(rng.normal(1000, 200, n))
    return pd.DataFrame(
        {
            "open_time_utc": idx,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": vol,
        }
    )


class TestG2DeletionSentinel:
    """Future-bar invariance sentinel, auto-derived from the registry.

    For a causal factor, value at bar t depends ONLY on bars <= t. Therefore
    truncating the input to its first k rows must reproduce the first k
    output values byte-for-byte (post-warmup, where the series is defined).
    A factor that peeks at bar t+1 would change value at bar t when the tail
    is present, violating this.
    """

    @pytest.mark.parametrize(
        "name",
        # Auto-derive from the registry so new factors are covered for free.
        FactorRegistry.__new__(FactorRegistry).__class__()  # placeholder; see below
        if False
        else None,
    )
    def test_placeholder(self, name):  # pragma: no cover - replaced below
        pass
```

The parametrize source must be a real list at collection time, so use a module-level registry:

```python
# tests/test_leakage_guards.py — replace the placeholder class with:

_SENTINEL_REG = FactorRegistry()
_bootstrap_core_factors(_SENTINEL_REG)
_SENTINEL_NAMES = _SENTINEL_REG.list_names()


class TestG2FutureBarInvarianceSentinel:
    """Truncation-invariance: f(df[:k])[:k] == f(df)[:k] for every factor."""

    @pytest.mark.parametrize("name", _SENTINEL_NAMES)
    def test_truncation_invariance(self, name):
        df = _synthetic_ohlcv(n=800)
        spec = _SENTINEL_REG.get(name)
        k = 600  # well past every factor's warmup
        full = spec.compute(df).to_numpy()
        truncated = spec.compute(df.iloc[:k].copy()).to_numpy()
        warmup = spec.warmup_bars
        np.testing.assert_allclose(
            truncated[warmup:k],
            full[warmup:k],
            rtol=1e-9,
            atol=1e-9,
            err_msg=(
                f"{name}: truncated output diverges from full output on the "
                f"shared prefix — factor reads future bars."
            ),
        )

    @pytest.mark.parametrize("name", _SENTINEL_NAMES)
    def test_reversed_input_changes_output(self, name):
        """Reversing time must change a genuinely time-ordered factor.

        A factor whose value is invariant to a full time-reversal is either
        constant or order-independent; for our OHLCV-derived corpus that is a
        red flag the compute ignores temporal ordering. ``close`` (identity)
        and structural calendar factors are exempt — they are pointwise.
        """
        if name in {"close", "hour_of_day", "day_of_week"}:
            pytest.skip("pointwise/identity factor is order-invariant by design")
        df = _synthetic_ohlcv(n=800)
        spec = _SENTINEL_REG.get(name)
        normal = spec.compute(df).to_numpy()
        rev_df = df.iloc[::-1].reset_index(drop=True).copy()
        reversed_out = spec.compute(rev_df).to_numpy()
        warmup = spec.warmup_bars
        a = normal[warmup:]
        b = reversed_out[warmup:][::-1]
        assert not np.allclose(
            a[np.isfinite(a) & np.isfinite(b)],
            b[np.isfinite(a) & np.isfinite(b)],
            rtol=1e-6,
        ), f"{name}: time-reversal left output unchanged — suspicious."
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_leakage_guards.py::TestG2FutureBarInvarianceSentinel -v`
  `Expected: FAIL — the placeholder `test_placeholder` collection error / NameError until the module-level `_SENTINEL_REG` block + helper `_synthetic_ohlcv` are in place.` (After the placeholder is removed and the real class added, the sentinel runs against existing factors.)

- [ ] **Step 3: Implement** — no production code change is required for G2; the truncation/reversal sentinel exercises the *already-shipped* `compute` functions. The "implementation" is finalizing the test module: delete the `test_placeholder` stub class and keep `_synthetic_ohlcv`, `_SENTINEL_REG`, `_SENTINEL_NAMES`, and `TestG2FutureBarInvarianceSentinel`. (G2 is a behavioral guard, not new runtime code — its value is regression coverage for every present and future factor.)

```python
# tests/test_leakage_guards.py — final G2 form is the
# _synthetic_ohlcv + _SENTINEL_REG + TestG2FutureBarInvarianceSentinel block
# shown in Step 1's replacement; the placeholder class is removed.
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_leakage_guards.py::TestG2FutureBarInvarianceSentinel -v`
  `Expected: PASS — every registered factor satisfies truncation-invariance; non-pointwise factors are time-reversal sensitive.`

- [ ] **Step 5: Commit** — `git add tests/test_leakage_guards.py && git commit -m "test(pathb-g2): registry-derived truncation + time-reversal future-bar sentinel over list_names()"`

---

### Task 3: G3 — per-operator known-value checks + ternary-sizing causality

**Files:** Test: `tests/test_leakage_guards.py` (depends on `strategies/dsl.py` `SizingSpec` + `strategies/dsl_compiler.py` `_compile_sizing` delivered in Section B's sizing tasks; this guard test is authored here and asserts their causal contract).

- [ ] **Step 1: Write the failing test** — two parts. (a) Per-operator known-value: the compiled comparison helpers fire on the documented bar (continuous reads `cur_row`; cross reads `cur_row` + `prev_row`). (b) Ternary-sizing causality: the REAL `SizingSpec(factor=..., bands=[{lower,upper,size}], default_size=...)` compiled by `_compile_sizing(spec, factor_index)` produces a closure `(cur_row, prev_row) -> float` that (i) returns the band/default fraction by reading `cur_row[idx]` only, and (ii) **statically** never reads a future bar — an AST scan of the closure-factory source confirms no positive `self.data[...]` index and that the closure reads only `cur_row`/`prev_row` by index.

```python
# tests/test_leakage_guards.py — append

import inspect as _inspect

from strategies.dsl import Condition, SizingSpec
from strategies.dsl_compiler import (
    _compile_condition,
    _compile_sizing,
)


class TestG3OperatorKnownValues:
    """Per-operator firing on the documented bar (cur_row / prev_row)."""

    def test_continuous_gt_reads_cur_row_only(self, core_registry):
        # rsi_14 > 70 ; factor_index places rsi_14 at column 0.
        cond = Condition(factor="rsi_14", op=">", value=70.0)
        fn = _compile_condition(cond, {"rsi_14": 0})
        # cur_row above threshold, prev_row below — continuous op uses cur_row.
        assert fn((75.0,), (10.0,)) is True
        assert fn((65.0,), (99.0,)) is False

    def test_crosses_above_reads_both_rows(self, core_registry):
        # sma_20 crosses_above sma_50 : factor-vs-factor cross.
        cond = Condition(factor="sma_20", op="crosses_above", value="sma_50")
        fn = _compile_condition(cond, {"sma_20": 0, "sma_50": 1})
        # prev: sma_20 below sma_50 ; cur: sma_20 above sma_50 -> cross up.
        assert fn((101.0, 100.0), (99.0, 100.0)) is True
        # Already above on both bars -> no fresh cross.
        assert fn((101.0, 100.0), (101.5, 100.0)) is False


# --- Ternary-sizing causality ------------------------------------------------

# Step -1 human-locked sizing param values referenced symbolically. The
# concrete band edges (THETA_PUSH etc.) are fixed at the hypothesis-lock
# step; this guard only asserts the *causal shape*, not the numeric values.
THETA_PUSH_LOW = -0.5   # symbolic; bound at Step -1 lock
THETA_PUSH_HIGH = 0.5   # symbolic; bound at Step -1 lock
SIZE_IN_BAND = 1.0
SIZE_DEFAULT = 0.25


class TestG3TernarySizingCausality:
    """The REAL SizingSpec/_compile_sizing reads ONLY cur_row by index."""

    def _spec(self) -> SizingSpec:
        # SizingSpec(factor, bands=[{lower,upper,size}], default_size)
        return SizingSpec(
            factor="intrabar_push",
            bands=[
                {
                    "lower": THETA_PUSH_LOW,
                    "upper": THETA_PUSH_HIGH,
                    "size": SIZE_IN_BAND,
                }
            ],
            default_size=SIZE_DEFAULT,
        )

    def test_sizing_closure_returns_band_then_default(self, core_registry):
        spec = self._spec()
        # intrabar_push resolved to column 0 of factors_used.
        sizing = _compile_sizing(spec, {"intrabar_push": 0})
        # In-band cur_row value -> SIZE_IN_BAND ; prev_row irrelevant.
        assert sizing((0.0,), (9.9,)) == pytest.approx(SIZE_IN_BAND)
        # Out-of-band cur_row value -> default ; prev_row irrelevant.
        assert sizing((5.0,), (0.0,)) == pytest.approx(SIZE_DEFAULT)

    def test_sizing_ignores_prev_row(self, core_registry):
        """Changing prev_row alone must not change the sizing fraction."""
        spec = self._spec()
        sizing = _compile_sizing(spec, {"intrabar_push": 0})
        a = sizing((0.0,), (0.0,))
        b = sizing((0.0,), (123.0,))
        assert a == b, "sizing read prev_row — that is a causality leak risk"

    def test_sizing_factory_source_has_no_future_index(self):
        """Static AST scan: the closure factory never reads a future bar.

        It must read sizing inputs only via ``cur_row[idx]`` / ``prev_row[idx]``
        (tuple subscription), never via ``self.data[k]`` with a positive k
        (Backtrader forward index = look-ahead) and never via a negative
        tuple/series ``shift``.
        """
        src = textwrap.dedent(_inspect.getsource(_compile_sizing))
        tree = ast.parse(src)

        offenders: list[str] = []
        for node in ast.walk(tree):
            # Ban self.data[<positive int>] — Backtrader forward read.
            if isinstance(node, ast.Subscript):
                val = node.value
                is_self_data = (
                    isinstance(val, ast.Attribute)
                    and val.attr == "data"
                    and isinstance(val.value, ast.Name)
                    and val.value.id == "self"
                )
                if is_self_data:
                    sl = node.slice
                    if isinstance(sl, ast.Constant) and isinstance(
                        sl.value, int
                    ) and sl.value > 0:
                        offenders.append(f"self.data[{sl.value}]")
            # Ban negative shift() anywhere in the factory.
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "shift"
                and node.args
            ):
                a0 = node.args[0]
                if (
                    isinstance(a0, ast.UnaryOp)
                    and isinstance(a0.op, ast.USub)
                ):
                    offenders.append("shift(<negative>)")

        assert not offenders, (
            f"_compile_sizing reads future bars: {offenders}"
        )

    def test_sizing_factory_reads_only_known_row_names(self):
        """Every Name loaded for subscription is cur_row / prev_row / idx.

        Guards against a refactor that smuggles in `self.data` or a global
        future series as the sizing source. Allowed subscript receivers are
        exactly the closure's row tuples.
        """
        src = textwrap.dedent(_inspect.getsource(_compile_sizing))
        tree = ast.parse(src)
        allowed_receivers = {"cur_row", "prev_row"}
        bad: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and isinstance(
                node.value, ast.Name
            ):
                if node.value.id not in allowed_receivers:
                    # Allow indexing the precomputed band list / factor_index
                    # by their local names; only flag obvious data sources.
                    if node.value.id in {"self", "data", "feed"}:
                        bad.append(node.value.id)
        assert not bad, f"_compile_sizing subscripts forbidden source: {bad}"
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_leakage_guards.py::TestG3TernarySizingCausality -v`
  `Expected: FAIL — ImportError: cannot import name 'SizingSpec' from 'strategies.dsl' (and '_compile_sizing' from 'strategies.dsl_compiler') until Section B's sizing tasks land.`

- [ ] **Step 3: Implement** — G3 adds **no production code**; `SizingSpec` and `_compile_sizing` are implemented in Section B. This task contributes the *guard contract* that Section B's implementation must satisfy: `_compile_sizing(spec, factor_index)` returns a `(cur_row, prev_row) -> float` closure that reads only `cur_row[idx]`, and its factory source contains no `self.data[<positive>]` / negative-`shift` future read. The test is authored RED here and turns GREEN once Section B is merged.

```python
# No factors/* or strategies/* edit in this task.
# G3's deliverable is tests/test_leakage_guards.py::TestG3* asserting the
# causal contract of SizingSpec + _compile_sizing (built in Section B).
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_leakage_guards.py::TestG3OperatorKnownValues -v` (passes immediately — exercises shipped `_compile_condition`) then, after Section B merges, `Run: pytest tests/test_leakage_guards.py::TestG3TernarySizingCausality -v`
  `Expected: PASS — operator known-values green now; ternary-sizing causality green once SizingSpec + _compile_sizing exist.`

- [ ] **Step 5: Commit** — `git add tests/test_leakage_guards.py && git commit -m "test(pathb-g3): per-operator known-value + ternary-sizing causality (real SizingSpec/_compile_sizing tuple-row contract)"`

---

### Task 4a: G4 generic registry-derived sync + future-bar-invariance (PRE-factor)

**Files:** Test: `tests/test_leakage_guards.py`. This task runs BEFORE Section B's 5 new factors land — it must therefore assert `set(EXPECTED_FACTORS) == set(registry.list_names())` and auto-derive its future-bar parametrize from `registry.list_names()` (NOT hardcode the 5 new names). The complementary **Task 4b** (post-factor presence guard asserting the 5 new names + 23 total) is authored AFTER Section B and is noted below, not implemented here.

- [ ] **Step 1: Write the failing test** — generic, registry-driven. At the moment Task 4a is authored, `EXPECTED_FACTORS` has whatever count is current (18 pre-Section-B, 23 post-merge); the guard asserts set-equality with the live registry either way and re-derives its parametrize list from `registry.list_names()` so it never hardcodes a count.

```python
# tests/test_leakage_guards.py — append

from tests.test_factors import EXPECTED_FACTORS


class TestG4aRegistrySync:
    """Generic registry <-> EXPECTED_FACTORS sync (count-agnostic).

    DESIGN INVARIANT: this guard asserts the registry and the canonical
    EXPECTED_FACTORS list are the SAME SET. It does NOT assert any specific
    Path B factor exists — that is Task 4b's job, authored after Section B.
    Keeping the existence check out of this generic guard means Task 4a can
    be authored and run BEFORE the 5 new factors are implemented (it then
    just re-confirms the 18-factor baseline), and the same test body keeps
    holding after the merge bumps both sides to 23.
    """

    def test_registry_matches_expected_factors_set(self, core_registry):
        assert set(core_registry.list_names()) == set(EXPECTED_FACTORS), (
            "registry.list_names() and tests.test_factors.EXPECTED_FACTORS "
            "have drifted; update EXPECTED_FACTORS in the same change that "
            "registers/removes a factor."
        )

    def test_list_names_is_sorted_alphabetical(self, core_registry):
        # registry.list_names() == sorted(self._specs.keys()); EXPECTED_FACTORS
        # is the alphabetical projection of that.
        names = core_registry.list_names()
        assert names == sorted(names)
        assert EXPECTED_FACTORS == sorted(EXPECTED_FACTORS)


# Auto-derived parametrize: future-bar invariance over the LIVE registry, so
# the 5 Path B factors are covered automatically once registered — no name is
# hardcoded here.
_G4_REG = FactorRegistry()
_bootstrap_core_factors(_G4_REG)
_G4_NAMES = _G4_REG.list_names()


class TestG4aFutureBarInvariance:
    """Auto-derived truncation-invariance over registry.list_names().

    Mirrors G2's truncation check but is anchored to the registry/EXPECTED
    sync guard so a newly-registered factor is invariance-checked the moment
    it appears in list_names() — without editing this file.
    """

    @pytest.mark.parametrize("name", _G4_NAMES)
    def test_future_bar_invariance(self, name):
        df = _synthetic_ohlcv(n=900)
        spec = _G4_REG.get(name)
        k = 700
        full = spec.compute(df).to_numpy()
        trunc = spec.compute(df.iloc[:k].copy()).to_numpy()
        w = spec.warmup_bars
        np.testing.assert_allclose(
            trunc[w:k], full[w:k], rtol=1e-9, atol=1e-9,
            err_msg=f"{name}: prefix output changed when tail was truncated.",
        )
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_leakage_guards.py::TestG4aRegistrySync -v`
  `Expected: PASS at the 18-factor baseline IF EXPECTED_FACTORS is still 18, but the dependency import `from tests.test_factors import EXPECTED_FACTORS` and helpers must resolve first; the RED state here is the collection error until `_synthetic_ohlcv`/`core_registry` fixtures (Task 1/2) are present.` (Once Section B updates `EXPECTED_FACTORS` to the 23-name list AND registers the 5 factors, this stays green; if only one side is updated, `test_registry_matches_expected_factors_set` FAILS — that is the intended drift alarm.)

- [ ] **Step 3: Implement** — no production code; Task 4a is a pure guard. Its "implementation" is the registry-derived sync + auto-parametrized invariance test above. It is deliberately count-agnostic so it remains correct across the 18→23 transition. The canonical 23-name alphabetical `EXPECTED_FACTORS` that Section B must produce (mirrored from the verified repo fact) is:

```python
# The post-Section-B EXPECTED_FACTORS (Section B edits tests/test_factors.py
# to this exact 23-name alphabetical list; Task 4a only asserts set-equality
# with the live registry and never hardcodes it):
# ["atr_14","bb_upper_24_2","cdf_realized_vol_720","close","day_of_week",
#  "decay_linear_close_168","decay_linear_close_48","ema_12","ema_26",
#  "hour_of_day","intrabar_push","macd_hist","range_over_atr",
#  "realized_vol_24h","return_168h","return_1h","return_24h","rsi_14",
#  "sma_20","sma_24","sma_50","volume_zscore_24h","zscore_48"]
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_leakage_guards.py::TestG4aRegistrySync tests/test_leakage_guards.py::TestG4aFutureBarInvariance -v`
  `Expected: PASS — set-equality holds at the current baseline; every live factor satisfies truncation-invariance.`
  **Task 4b note (NOT implemented here):** after Section B registers the 5 factors and bumps `EXPECTED_FACTORS` to 23, add `TestG4bPathBPresence` asserting the 5 specific new names (`intrabar_push`, `range_over_atr`, `cdf_realized_vol_720`, `decay_linear_close_48`, `decay_linear_close_168`) are in `registry.list_names()` AND `len(list_names()) == 23`. That positive-existence assertion MUST NOT be added to Task 4a's generic guard — Task 4a stays count-agnostic so it is authorable pre-Section-B.

- [ ] **Step 5: Commit** — `git add tests/test_leakage_guards.py && git commit -m "test(pathb-g4a): generic registry<->EXPECTED_FACTORS set-sync + auto-derived future-bar invariance (count-agnostic; Task 4b presence guard deferred post-Section-B)"`

---

**Section A handoff notes for siblings:**
- G1 production code lives in `factors/registry.py` (`_assert_no_future_ops`, wired into `register()`); it runs on **every** `register()` call, so Section B's 5 new `compute_*` functions must pass it — keep them on `rolling(N)` / `ewm(span=N, adjust=False)` / `expanding(min_periods=N)` and avoid any full-series `.mean()/.std()/.sum()/.rank()` and negative `shift`. The compute PRIMITIVES (`decay_linear`, `rolling_backward_percentile` in `factors/operators.py`) are NOT registered and never hit the scanner.
- G3 imports `SizingSpec` from `strategies.dsl` and `_compile_sizing` from `strategies.dsl_compiler` — Section B must export both, with `_compile_sizing(spec, factor_index) -> Callable[[tuple, tuple], float]` reading `cur_row[idx]` only.
- G4a imports `EXPECTED_FACTORS` from `tests.test_factors`; Section B must edit that list to the 23-name alphabetical form above in the same change that registers the 5 factors, or `test_registry_matches_expected_factors_set` fires the drift alarm.

---

## Section B — `decay_linear` Primitive + 5 Factors (Step 2)

I have all the signatures I need. Now I'll write Section B (tasks 5-12). The G1 guard is created in Section A (Task 4) and the Task 4b presence guard I add here references the registry after the 5 factors are registered.

### Task 5: `decay_linear` + `rolling_backward_percentile` compute primitives in `factors/operators.py`
**Files:** Create: `factors/operators.py` · Test: `tests/test_factors.py`
- [ ] **Step 1: Write the failing test** — these are NOT registered factors (so G1 in Task 4 never scans them); they are pure compute primitives. The contract requires `decay_linear` to be a linearly-weighted trailing MA via `rolling(window).apply(_weighted, raw=True)` with a nested `_weighted`, and `rolling_backward_percentile` to be the rank-of-last within the trailing window (no center, no full-series rank).

```python
# tests/test_factors.py  (append a new test class)
import numpy as np
import pandas as pd

from factors.operators import decay_linear, rolling_backward_percentile


class TestComputePrimitives:
    """factors/operators.py primitives are causal building blocks, NOT
    registered factors (so the G1 future-ops scanner never reaches them)."""

    def test_decay_linear_weights_are_linear_and_trailing(self):
        # Linearly increasing series: with linear weights 1..w (newest heaviest),
        # the weighted MA of a perfectly linear ramp is computable in closed form.
        s = pd.Series([float(i) for i in range(10)])
        out = decay_linear(s, window=4)
        # First 3 positions are warmup (window-1) -> NaN.
        assert out.iloc[:3].isna().all()
        assert out.iloc[3:].notna().all()
        # At position 3 the window is [0,1,2,3], weights [1,2,3,4] (sum 10):
        # (0*1 + 1*2 + 2*3 + 3*4) / 10 = (0+2+6+12)/10 = 2.0
        assert out.iloc[3] == pytest.approx(2.0)
        # At position 9 the window is [6,7,8,9], weights [1,2,3,4]:
        # (6+14+24+36)/10 = 80/10 = 8.0
        assert out.iloc[9] == pytest.approx(8.0)

    def test_decay_linear_is_causal_window_1_is_identity(self):
        s = pd.Series([3.0, 1.0, 4.0, 1.0, 5.0])
        out = decay_linear(s, window=1)
        # window=1 -> single weight -> identity, no warmup.
        pd.testing.assert_series_equal(out, s, check_names=False)

    def test_rolling_backward_percentile_rank_of_last(self):
        # Strictly increasing series: the last value is always the max within
        # any trailing window -> percentile rank == 1.0 once warmed up.
        s = pd.Series([float(i) for i in range(10)])
        out = rolling_backward_percentile(s, window=5)
        assert out.iloc[:4].isna().all()       # warmup = window-1
        assert (out.iloc[4:] == pytest.approx(1.0)).all()

    def test_rolling_backward_percentile_min_is_zero(self):
        # Strictly decreasing -> last value is the min within the window -> 0.0.
        s = pd.Series([float(9 - i) for i in range(10)])
        out = rolling_backward_percentile(s, window=5)
        assert out.iloc[:4].isna().all()
        assert (out.iloc[4:] == pytest.approx(0.0)).all()

    def test_rolling_backward_percentile_midpoint(self):
        # Window [last is the median of 5 distinct ascending values then a dip]:
        # window=5 ending at a value that is the 3rd-smallest of 5 -> rank 0.5.
        s = pd.Series([10.0, 20.0, 30.0, 40.0, 25.0])
        out = rolling_backward_percentile(s, window=5)
        # Within [10,20,30,40,25] the last value 25 has 2 strictly-below
        # (10,20) out of (5-1)=4 others -> 2/4 = 0.5.
        assert out.iloc[4] == pytest.approx(0.5)

    def test_primitives_not_in_registry(self):
        # Contract: primitives are never registered (G1 never scans them).
        from factors.registry import get_registry
        names = get_registry().list_names()
        assert "decay_linear" not in names
        assert "rolling_backward_percentile" not in names
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_factors.py::TestComputePrimitives -v`
  `Expected: FAIL — ModuleNotFoundError: No module named 'factors.operators'`

- [ ] **Step 3: Implement**

```python
# factors/operators.py
"""Causal compute primitives shared by factor modules.

These are NOT registered factors. They are deliberately kept out of the
FactorRegistry so the G1 future-ops scanner (factors.registry._assert_no_future_ops,
invoked inside FactorRegistry.register) never reaches them — the scanner
inspects registered compute callables only. Callers wrap these primitives
inside top-level ``compute_*`` factor functions that ARE registered, and
those wrappers carry the warmup/causality contract.

DESIGN INVARIANT: every primitive here is strictly backward-looking. A
``rolling(window)`` with no ``center=`` argument defaults to a trailing
window whose right edge is the current bar — no future bar contributes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def decay_linear(series: pd.Series, window: int) -> pd.Series:
    """Linearly-weighted trailing moving average (newest bar heaviest).

    Weights for a window of size ``w`` are ``[1, 2, ..., w]`` applied to the
    ``[oldest, ..., newest]`` bars, normalized by ``sum(1..w) = w*(w+1)/2``.
    The most recent bar receives the largest weight, which is the standard
    "linear decay" used in alpha factors (e.g. WorldQuant ``decay_linear``).

    Implemented via ``series.rolling(window).apply(_weighted, raw=True)`` with
    a nested ``_weighted`` so the weighting is local to this primitive and
    carries no module-level state.

    Inputs: any numeric Series.
    Warmup: ``window - 1`` bars (the rolling apply yields NaN until the first
        full window).
    Output dtype: float64.
    Null policy: NaN only at positions ``0 .. window-2``.
    """
    w = int(window)
    weights = np.arange(1, w + 1, dtype="float64")
    denom = weights.sum()

    def _weighted(values: np.ndarray) -> float:
        # ``values`` is a length-``window`` ndarray, oldest-first (raw=True).
        return float(np.dot(values, weights) / denom)

    return series.rolling(w).apply(_weighted, raw=True)


def rolling_backward_percentile(series: pd.Series, window: int) -> pd.Series:
    """Percentile rank of the LAST value within its trailing window.

    For each position ``T`` (once warmed up), looks back over the window
    ``[T-window+1 .. T]`` and returns the fraction of the other
    ``window - 1`` values that are strictly less than ``series[T]``:

        rank(T) = (# values in window strictly < series[T]) / (window - 1)

    The result lies in ``[0.0, 1.0]``: ``1.0`` when the current bar is the
    window maximum, ``0.0`` when it is the window minimum.

    This is deliberately NOT a full-series ``Series.rank()`` (that would
    leak future bars) and uses NO ``center=`` argument (which would also
    leak). Only the trailing window contributes.

    Inputs: any numeric Series.
    Warmup: ``window - 1`` bars.
    Output dtype: float64.
    Null policy: NaN only at positions ``0 .. window-2``.
    """
    w = int(window)

    def _last_rank(values: np.ndarray) -> float:
        last = values[-1]
        # Strictly-below count among the other (w-1) values.
        below = float(np.sum(values[:-1] < last))
        return below / float(w - 1) if w > 1 else 0.0

    return series.rolling(w).apply(_last_rank, raw=True)
```

  DESIGN INVARIANT: `window=1` makes `decay_linear` an identity (single weight `[1]`, denom `1`) and gives `rolling_backward_percentile` a divide-by-`(w-1)=0` guard returning `0.0` — both verified by tests above.

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_factors.py::TestComputePrimitives -v`
  `Expected: PASS (6 passed)`

- [ ] **Step 5: Commit** — `git add factors/operators.py tests/test_factors.py && git commit -m "feat(factors): decay_linear + rolling_backward_percentile causal primitives (unregistered, G1-exempt)"`

---

### Task 6: `intrabar_push` factor in `factors/price.py`
**Files:** Modify: `factors/price.py` · Test: `tests/test_factors.py`
- [ ] **Step 1: Write the failing test** — `intrabar_push = (close - open) / ((high - low) + 1e-9)`, warmup 0, inputs `open,high,low,close`.

```python
# tests/test_factors.py  (append)
class TestIntrabarPush:
    def test_known_value(self):
        from factors.price import compute_intrabar_push
        df = pd.DataFrame({
            "open":  [100.0, 50.0],
            "high":  [110.0, 60.0],
            "low":   [ 90.0, 40.0],
            "close": [105.0, 45.0],
        })
        out = compute_intrabar_push(df)
        # bar0: (105-100)/((110-90)+1e-9) = 5/20.000000001 ~ 0.25
        assert out.iloc[0] == pytest.approx(0.25, abs=1e-7)
        # bar1: (45-50)/((60-40)+1e-9) = -5/20 ~ -0.25
        assert out.iloc[1] == pytest.approx(-0.25, abs=1e-7)

    def test_zero_range_does_not_divide_by_zero(self):
        from factors.price import compute_intrabar_push
        # Frozen-price bar (O=H=L=C): numerator 0, denom 1e-9 -> 0.0, not NaN/inf.
        df = pd.DataFrame({
            "open": [50.0], "high": [50.0], "low": [50.0], "close": [50.0],
        })
        out = compute_intrabar_push(df)
        assert out.iloc[0] == pytest.approx(0.0)
        assert np.isfinite(out.iloc[0])

    def test_spec_registered_warmup_zero(self):
        from factors.registry import get_registry
        spec = get_registry().get("intrabar_push")
        assert spec.warmup_bars == 0
        assert sorted(spec.inputs) == ["close", "high", "low", "open"]
        assert spec.category == "price"
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_factors.py::TestIntrabarPush -v`
  `Expected: FAIL — AttributeError: module 'factors.price' has no attribute 'compute_intrabar_push'`

- [ ] **Step 3: Implement**

```python
# factors/price.py  (append after SPEC_CLOSE)


def compute_intrabar_push(df: pd.DataFrame) -> pd.Series:
    """Intrabar directional push: where close sits in the bar's range.

    ``intrabar_push = (close - open) / ((high - low) + 1e-9)``

    Positive when the bar closed above its open (buying pressure), negative
    below. The ``+ 1e-9`` floor on the denominator keeps a frozen-price bar
    (``open == high == low == close``) finite at 0.0 rather than producing
    NaN/inf — this matters because the canonical dataset contains 3 known
    zero-volume frozen-price bars (see CLAUDE.md Known Data Characteristics).

    All four inputs are observed at bar T's close, so this is causal: it
    uses no prior or future bar.

    Inputs: ``open``, ``high``, ``low``, ``close``.
    Warmup: 0 bars (every bar is fully self-contained).
    Output dtype: float64.
    Null policy: no NaN at any position (denominator is floored at 1e-9).
    """
    rng = (df["high"] - df["low"]) + 1e-9
    return ((df["close"] - df["open"]) / rng).astype("float64")


SPEC_INTRABAR_PUSH = FactorSpec(
    name="intrabar_push",
    category="price",
    warmup_bars=0,
    inputs=["open", "high", "low", "close"],
    output_dtype="float64",
    compute=compute_intrabar_push,
    docstring=compute_intrabar_push.__doc__ or "",
)
```

  And register it in `factors/registry.py` `_bootstrap_core_factors` — add `price.SPEC_INTRABAR_PUSH,` to the registration tuple (position in the tuple is irrelevant; `list_names()` sorts):

```python
# factors/registry.py — inside _bootstrap_core_factors registration tuple
        price.SPEC_CLOSE,
        price.SPEC_INTRABAR_PUSH,
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_factors.py::TestIntrabarPush -v`
  `Expected: PASS (3 passed)`

- [ ] **Step 5: Commit** — `git add factors/price.py factors/registry.py tests/test_factors.py && git commit -m "feat(factors): intrabar_push = (close-open)/((high-low)+1e-9), warmup 0"`

---

### Task 7: `range_over_atr` factor in `factors/volatility.py`
**Files:** Modify: `factors/volatility.py` · Test: `tests/test_factors.py`
- [ ] **Step 1: Write the failing test** — `range_over_atr = (high - low) / atr14`, ATR-14 recomputed internally and causally (`prev_close = close.shift(1)`, `TR = max(h-l, |h-pc|, |l-pc|)` with NaN where `pc` is NaN, `.rolling(14).mean()`), warmup 14, inputs `high,low,close`.

```python
# tests/test_factors.py  (append)
class TestRangeOverAtr:
    def test_warmup_then_finite(self):
        from factors.volatility import compute_range_over_atr
        rng = np.random.default_rng(7)
        n = 60
        df = pd.DataFrame({
            "high":  100 + rng.random(n) * 5 + 2,
            "low":   100 + rng.random(n) * 5 - 2,
            "close": 100 + rng.random(n) * 5,
        })
        # ensure high>=low
        df["high"] = np.maximum(df["high"], df["low"] + 0.5)
        out = compute_range_over_atr(df)
        # ATR-14 warmup is 14 (1 to shift + 13 to rolling) -> NaN at 0..13.
        assert out.iloc[:14].isna().all()
        assert out.iloc[14:].notna().all()
        assert np.isfinite(out.iloc[14:]).all()

    def test_matches_independent_atr_recompute(self):
        from factors.volatility import compute_range_over_atr, compute_atr_14
        rng = np.random.default_rng(11)
        n = 40
        df = pd.DataFrame({
            "high":  100 + rng.random(n) * 5 + 2,
            "low":   100 + rng.random(n) * 5 - 2,
            "close": 100 + rng.random(n) * 5,
        })
        df["high"] = np.maximum(df["high"], df["low"] + 0.5)
        # range_over_atr must equal (high-low)/atr_14 using the SAME causal ATR.
        atr = compute_atr_14(df)
        expected = (df["high"] - df["low"]) / atr
        out = compute_range_over_atr(df)
        pd.testing.assert_series_equal(
            out.iloc[14:], expected.iloc[14:], check_names=False,
        )

    def test_spec_registered(self):
        from factors.registry import get_registry
        spec = get_registry().get("range_over_atr")
        assert spec.warmup_bars == 14
        assert sorted(spec.inputs) == ["close", "high", "low"]
        assert spec.category == "volatility"
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_factors.py::TestRangeOverAtr -v`
  `Expected: FAIL — AttributeError: module 'factors.volatility' has no attribute 'compute_range_over_atr'`

- [ ] **Step 3: Implement**

```python
# factors/volatility.py  (append after SPEC_ATR_14 block)


def compute_range_over_atr(df: pd.DataFrame) -> pd.Series:
    """Bar range normalized by ATR-14: ``(high - low) / atr_14``.

    A value > 1 means the current bar's high-low range is wider than the
    14-bar average true range (an expansion bar); < 1 means a quiet bar.

    ATR-14 is recomputed internally rather than read from a precomputed
    column so this factor is self-contained and obviously causal:
    ``prev_close = close.shift(1)`` (causal +1 shift), true range
    ``TR = max(high-low, |high-prev_close|, |low-prev_close|)`` forced to
    NaN at position 0 where ``prev_close`` is NaN, then ``rolling(14).mean()``.
    This mirrors ``compute_atr_14`` exactly.

    Inputs: ``high``, ``low``, ``close``.
    Warmup: 14 bars (inherited from ATR-14: 1 bar to ``shift(1)`` plus 13 to
        the rolling mean; first valid at position 14).
    Output dtype: float64.
    Null policy: NaN only at positions 0..13.
    """
    prev_close = df["close"].shift(1)
    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - prev_close).abs()
    tr3 = (df["low"] - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    # Force NaN where prev_close is NaN (position 0) — same guard as
    # compute_atr_14 so the two warmup profiles match exactly.
    true_range = true_range.where(prev_close.notna(), other=np.nan)
    atr14 = true_range.rolling(14).mean()
    return ((df["high"] - df["low"]) / atr14).astype("float64")


SPEC_RANGE_OVER_ATR = FactorSpec(
    name="range_over_atr",
    category="volatility",
    warmup_bars=14,
    inputs=["high", "low", "close"],
    output_dtype="float64",
    compute=compute_range_over_atr,
    docstring=compute_range_over_atr.__doc__ or "",
)
```

  Register in `factors/registry.py` `_bootstrap_core_factors` (add to the volatility group of the tuple):

```python
# factors/registry.py — inside _bootstrap_core_factors registration tuple
        volatility.SPEC_ATR_14,
        volatility.SPEC_RANGE_OVER_ATR,
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_factors.py::TestRangeOverAtr -v`
  `Expected: PASS (3 passed)`

- [ ] **Step 5: Commit** — `git add factors/volatility.py factors/registry.py tests/test_factors.py && git commit -m "feat(factors): range_over_atr = (high-low)/atr14, causal ATR recompute, warmup 14"`

---

### Task 8: `cdf_realized_vol_720` factor in `factors/volatility.py`
**Files:** Modify: `factors/volatility.py` · Test: `tests/test_factors.py`
- [ ] **Step 1: Write the failing test** — `cdf_realized_vol_720 = rolling_backward_percentile(realized_vol_24h_recomputed, 720)` where `realized_vol_24h = close.pct_change(1).rolling(24).std()`; warmup `24 + 719 = 743`; inputs `close`. **PERFORMANCE FLAG:** the inner `rolling(720).apply(_last_rank, raw=True)` is O(N·720) and is the slowest factor in the library on the full ~55k-bar dataset (expect tens of seconds in Task 12's `--force-rebuild`); the test uses a small synthetic frame and a tight `pytest.mark.slow`-free window to stay fast.

```python
# tests/test_factors.py  (append)
class TestCdfRealizedVol720:
    def test_warmup_boundary(self):
        from factors.volatility import compute_cdf_realized_vol_720
        rng = np.random.default_rng(3)
        n = 760
        df = pd.DataFrame({"close": 100 + np.cumsum(rng.standard_normal(n)) * 0.5})
        out = compute_cdf_realized_vol_720(df)
        # warmup = 24 (realized_vol) + 719 (percentile window-1) = 743.
        assert out.iloc[:743].isna().all()
        assert out.iloc[743:].notna().all()
        # Percentile output is bounded [0, 1].
        post = out.iloc[743:]
        assert (post >= 0.0).all() and (post <= 1.0).all()

    def test_equals_primitive_composition(self):
        from factors.volatility import compute_cdf_realized_vol_720
        from factors.operators import rolling_backward_percentile
        rng = np.random.default_rng(99)
        n = 760
        df = pd.DataFrame({"close": 100 + np.cumsum(rng.standard_normal(n)) * 0.5})
        rv = df["close"].pct_change(1).rolling(24).std()
        expected = rolling_backward_percentile(rv, 720)
        out = compute_cdf_realized_vol_720(df)
        pd.testing.assert_series_equal(
            out.iloc[743:], expected.iloc[743:], check_names=False,
        )

    def test_spec_registered(self):
        from factors.registry import get_registry
        spec = get_registry().get("cdf_realized_vol_720")
        assert spec.warmup_bars == 743
        assert spec.inputs == ["close"]
        assert spec.category == "volatility"
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_factors.py::TestCdfRealizedVol720 -v`
  `Expected: FAIL — AttributeError: module 'factors.volatility' has no attribute 'compute_cdf_realized_vol_720'`

- [ ] **Step 3: Implement** — note the `from factors.operators import ...` import is placed at module top of `volatility.py`; add it next to the existing `import numpy as np` / `import pandas as pd`.

```python
# factors/volatility.py  — add near the top imports
from factors.operators import rolling_backward_percentile
```

```python
# factors/volatility.py  (append after SPEC_RANGE_OVER_ATR block)


def compute_cdf_realized_vol_720(df: pd.DataFrame) -> pd.Series:
    """30-day (720-bar) backward percentile rank of realized 24h volatility.

    Two-stage causal composition:
      1. ``realized_vol_24h = close.pct_change(1).rolling(24).std()`` —
         the same definition as ``compute_realized_vol_24h``, recomputed
         internally so this factor is self-contained.
      2. ``rolling_backward_percentile(realized_vol_24h, 720)`` — where the
         current realized-vol reading sits within its trailing 30-day
         (720-bar) distribution. 1.0 = highest vol in 30 days, 0.0 = lowest.

    Both stages are strictly backward-looking, so the factor is causal.

    PERFORMANCE: the inner ``rolling(720).apply(...)`` (inside the primitive)
    is O(N * 720) and is the single slowest factor in the library. On the
    full canonical dataset (~55k bars) a ``--force-rebuild`` spends most of
    its wall time here (tens of seconds). This is acceptable for the
    research build; do not "optimize" it into a non-causal vectorized rank.

    Inputs: ``close``.
    Warmup: 743 bars (24 for realized_vol_24h + 719 for the 720-bar
        percentile window; first valid at position 743).
    Output dtype: float64.
    Null policy: NaN only at positions 0..742.
    """
    realized_vol = df["close"].pct_change(1).rolling(24).std()
    return rolling_backward_percentile(realized_vol, 720).astype("float64")


SPEC_CDF_REALIZED_VOL_720 = FactorSpec(
    name="cdf_realized_vol_720",
    category="volatility",
    warmup_bars=743,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_cdf_realized_vol_720,
    docstring=compute_cdf_realized_vol_720.__doc__ or "",
)
```

  Register in `factors/registry.py` `_bootstrap_core_factors`:

```python
# factors/registry.py — inside _bootstrap_core_factors registration tuple
        volatility.SPEC_RANGE_OVER_ATR,
        volatility.SPEC_CDF_REALIZED_VOL_720,
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_factors.py::TestCdfRealizedVol720 -v`
  `Expected: PASS (3 passed)`

- [ ] **Step 5: Commit** — `git add factors/volatility.py factors/registry.py tests/test_factors.py && git commit -m "feat(factors): cdf_realized_vol_720 = backward-percentile of realized_vol_24h over 720 bars, warmup 743"`

---

### Task 9: `decay_linear_close_48` + `decay_linear_close_168` factors in `factors/moving_averages.py`
**Files:** Modify: `factors/moving_averages.py` · Test: `tests/test_factors.py`
- [ ] **Step 1: Write the failing test** — `decay_linear_close_48 = decay_linear(close, 48)` warmup 47; `decay_linear_close_168 = decay_linear(close, 168)` warmup 167; inputs `close`.

```python
# tests/test_factors.py  (append)
class TestDecayLinearClose:
    def test_48_warmup_and_value(self):
        from factors.moving_averages import compute_decay_linear_close_48
        from factors.operators import decay_linear
        rng = np.random.default_rng(5)
        df = pd.DataFrame({"close": 100 + np.cumsum(rng.standard_normal(200)) * 0.3})
        out = compute_decay_linear_close_48(df)
        assert out.iloc[:47].isna().all()
        assert out.iloc[47:].notna().all()
        expected = decay_linear(df["close"], 48)
        pd.testing.assert_series_equal(
            out.iloc[47:], expected.iloc[47:], check_names=False,
        )

    def test_168_warmup(self):
        from factors.moving_averages import compute_decay_linear_close_168
        rng = np.random.default_rng(6)
        df = pd.DataFrame({"close": 100 + np.cumsum(rng.standard_normal(300)) * 0.3})
        out = compute_decay_linear_close_168(df)
        assert out.iloc[:167].isna().all()
        assert out.iloc[167:].notna().all()

    def test_specs_registered(self):
        from factors.registry import get_registry
        reg = get_registry()
        s48 = reg.get("decay_linear_close_48")
        s168 = reg.get("decay_linear_close_168")
        assert s48.warmup_bars == 47
        assert s168.warmup_bars == 167
        assert s48.inputs == ["close"] and s168.inputs == ["close"]
        assert s48.category == "moving_average" and s168.category == "moving_average"
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_factors.py::TestDecayLinearClose -v`
  `Expected: FAIL — AttributeError: module 'factors.moving_averages' has no attribute 'compute_decay_linear_close_48'`

- [ ] **Step 3: Implement** — add the primitive import at the top of `moving_averages.py` next to `import pandas as pd`:

```python
# factors/moving_averages.py — add near the top imports
from factors.operators import decay_linear
```

```python
# factors/moving_averages.py  (append at end of file)


def compute_decay_linear_close_48(df: pd.DataFrame) -> pd.Series:
    """Linearly-decay-weighted moving average of close over 48 bars.

    Thin wrapper over ``factors.operators.decay_linear(close, 48)``: the
    most recent of the trailing 48 closes gets weight 48, the oldest gets
    weight 1, normalized by ``sum(1..48)``. Strictly causal (trailing
    window, no center, no future bar).

    Inputs: ``close``.
    Warmup: 47 bars (``decay_linear`` is NaN until its first full 48-bar
        window; first valid at position 47).
    Output dtype: float64.
    Null policy: NaN only at positions 0..46.
    """
    return decay_linear(df["close"], 48).astype("float64")


def compute_decay_linear_close_168(df: pd.DataFrame) -> pd.Series:
    """Linearly-decay-weighted moving average of close over 168 bars (1 week).

    Thin wrapper over ``factors.operators.decay_linear(close, 168)``. 168 =
    7 days of hourly bars, so this is a week-scale decay-weighted trend.
    Strictly causal.

    Inputs: ``close``.
    Warmup: 167 bars (first valid at position 167).
    Output dtype: float64.
    Null policy: NaN only at positions 0..166.
    """
    return decay_linear(df["close"], 168).astype("float64")


SPEC_DECAY_LINEAR_CLOSE_48 = FactorSpec(
    name="decay_linear_close_48",
    category="moving_average",
    warmup_bars=47,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_decay_linear_close_48,
    docstring=compute_decay_linear_close_48.__doc__ or "",
)

SPEC_DECAY_LINEAR_CLOSE_168 = FactorSpec(
    name="decay_linear_close_168",
    category="moving_average",
    warmup_bars=167,
    inputs=["close"],
    output_dtype="float64",
    compute=compute_decay_linear_close_168,
    docstring=compute_decay_linear_close_168.__doc__ or "",
)
```

  Register both in `factors/registry.py` `_bootstrap_core_factors`:

```python
# factors/registry.py — inside _bootstrap_core_factors registration tuple
        moving_averages.SPEC_EMA_26,
        moving_averages.SPEC_DECAY_LINEAR_CLOSE_48,
        moving_averages.SPEC_DECAY_LINEAR_CLOSE_168,
```

  DESIGN INVARIANT: the category string is `"moving_average"` (singular) to match the existing SMA/EMA specs in this module — verify against the module's existing `SPEC_SMA_20.category` before committing if unsure.

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_factors.py::TestDecayLinearClose -v`
  `Expected: PASS (3 passed)`

- [ ] **Step 5: Commit** — `git add factors/moving_averages.py factors/registry.py tests/test_factors.py && git commit -m "feat(factors): decay_linear_close_48 + decay_linear_close_168, warmup 47/167"`

---

### Task 10: Update `EXPECTED_FACTORS` to the 23-name alphabetical list + Task 4b post-factor presence guard
**Files:** Modify: `tests/test_factors.py` · Test: `tests/test_factors.py` (`TestCoreFactors`, new `TestNewFactorPresence`)
- [ ] **Step 1: Write the failing test** — replace the 18-name `EXPECTED_FACTORS` with the EXACT 23-name **alphabetical** list (the 5 new names inserted in sorted position). Because `registry.list_names()` returns `sorted(self._specs.keys())` (registry.py:166) and `test_all_registered` asserts `list_names() == EXPECTED_FACTORS`, the list MUST be alphabetical — registration-tuple order is irrelevant. Add the Task 4b presence guard asserting the 5 new factors are registered and the total is 23.

```python
# tests/test_factors.py — REPLACE the existing EXPECTED_FACTORS list (was 18 names)
EXPECTED_FACTORS = [
    "atr_14",
    "bb_upper_24_2",
    "cdf_realized_vol_720",
    "close",
    "day_of_week",
    "decay_linear_close_168",
    "decay_linear_close_48",
    "ema_12",
    "ema_26",
    "hour_of_day",
    "intrabar_push",
    "macd_hist",
    "range_over_atr",
    "realized_vol_24h",
    "return_168h",
    "return_1h",
    "return_24h",
    "rsi_14",
    "sma_20",
    "sma_24",
    "sma_50",
    "volume_zscore_24h",
    "zscore_48",
]
```

```python
# tests/test_factors.py  (append — Task 4b presence guard)
NEW_FACTORS_THIS_ARC = [
    "intrabar_push",
    "range_over_atr",
    "cdf_realized_vol_720",
    "decay_linear_close_48",
    "decay_linear_close_168",
]


class TestNewFactorPresence:
    """Task 4b presence guard: the 5 new factors are registered and the
    library now has exactly 23 factors, alphabetically ordered."""

    def test_expected_factors_has_23(self):
        assert len(EXPECTED_FACTORS) == 23

    def test_expected_factors_is_alphabetical(self):
        # list_names() returns sorted(keys); the assertion in
        # test_all_registered only holds if EXPECTED_FACTORS is sorted.
        assert EXPECTED_FACTORS == sorted(EXPECTED_FACTORS)

    def test_five_new_factors_registered(self, registry):
        names = set(registry.list_names())
        for n in NEW_FACTORS_THIS_ARC:
            assert n in names, f"new factor {n!r} not registered"

    def test_total_is_23_and_matches_expected(self, registry):
        names = registry.list_names()
        assert len(names) == 23
        assert names == EXPECTED_FACTORS
```

- [ ] **Step 2: Run test to verify it fails** — run BEFORE Tasks 6–9 are merged to see the RED, or against the current tree to confirm the count guard catches a missing factor:
  `Run: pytest tests/test_factors.py::TestCoreFactors::test_all_registered tests/test_factors.py::TestNewFactorPresence -v`
  `Expected: FAIL — assert registry.list_names() == EXPECTED_FACTORS (len 18 != 23) until Tasks 6–9 register the 5 new specs`

- [ ] **Step 3: Implement** — no production code in this task; the registrations were added in Tasks 6–9. This task only finalizes the test contract. (If running tasks strictly in order, the `EXPECTED_FACTORS` edit lands here and goes GREEN because Tasks 6–9 already registered the specs.)

  Sanity-check the alphabetical list against the live registry once Tasks 6–9 are merged:

```bash
python -c "from factors.registry import get_registry; print(get_registry().list_names())"
# Expected exactly:
# ['atr_14', 'bb_upper_24_2', 'cdf_realized_vol_720', 'close', 'day_of_week',
#  'decay_linear_close_168', 'decay_linear_close_48', 'ema_12', 'ema_26',
#  'hour_of_day', 'intrabar_push', 'macd_hist', 'range_over_atr',
#  'realized_vol_24h', 'return_168h', 'return_1h', 'return_24h', 'rsi_14',
#  'sma_20', 'sma_24', 'sma_50', 'volume_zscore_24h', 'zscore_48']
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_factors.py -v`
  `Expected: PASS — TestCoreFactors (parametrized over 23 names), TestNewFactorPresence (4 passed), and existing classes all green`

- [ ] **Step 5: Commit** — `git add tests/test_factors.py && git commit -m "test(factors): EXPECTED_FACTORS -> 23-name alphabetical + Task 4b presence guard"`

---

### Task 11: `compute_feature_version` changes when a factor subset differs (module-level API)
**Files:** Test: `tests/test_factors.py` (`TestFeatureVersionSensitivity`)
- [ ] **Step 1: Write the failing test** — use the MODULE-LEVEL `compute_feature_version(registry)` (registry.py:323) — there is NO `registry.feature_version()` method. Assert the full registry's version differs from a subset registry's version (adding the 5 new factors must bump the hash).

```python
# tests/test_factors.py  (append)
from factors.registry import (
    FactorRegistry,
    compute_feature_version,
    get_registry,
)


class TestFeatureVersionSensitivity:
    """compute_feature_version is module-level (registry.py:323); there is
    NO FactorRegistry.feature_version() method."""

    def _subset_registry(self, drop: list[str]) -> FactorRegistry:
        """A fresh registry holding every core factor EXCEPT `drop`."""
        full = get_registry()
        sub = FactorRegistry()
        for name in full.list_names():
            if name not in drop:
                sub.register(full.get(name))
        return sub

    def test_full_differs_from_subset_missing_new_factors(self):
        full = get_registry()
        sub = self._subset_registry(drop=NEW_FACTORS_THIS_ARC)
        assert len(sub.list_names()) == 18
        assert len(full.list_names()) == 23
        # Adding the 5 new factors MUST change the feature_version hash.
        assert compute_feature_version(full) != compute_feature_version(sub)

    def test_version_is_deterministic(self):
        full = get_registry()
        assert compute_feature_version(full) == compute_feature_version(full)

    def test_dropping_one_new_factor_changes_version(self):
        full = get_registry()
        sub = self._subset_registry(drop=["intrabar_push"])
        assert len(sub.list_names()) == 22
        assert compute_feature_version(full) != compute_feature_version(sub)
```

- [ ] **Step 2: Run test to verify it fails** — before Tasks 6–9 register the new specs, `get_registry()` has only 18 names and the `len(full.list_names()) == 23` / `drop` assertions fail:
  `Run: pytest tests/test_factors.py::TestFeatureVersionSensitivity -v`
  `Expected: FAIL — assert len(full.list_names()) == 23 (was 18) until the 5 new factors are registered`

- [ ] **Step 3: Implement** — no production code; this task asserts the existing `compute_feature_version` behavior over the now-23-factor registry. The sensitivity is already guaranteed by `canonical_metadata()` including every factor's name + `compute_source_sha256` (registry.py:264–280), so adding factors necessarily changes the hash. No edit to `registry.py` is required.

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_factors.py::TestFeatureVersionSensitivity -v`
  `Expected: PASS (3 passed)`

- [ ] **Step 5: Commit** — `git add tests/test_factors.py && git commit -m "test(factors): compute_feature_version (module-level) bumps on the 5 new factors"`

---

### Task 12: Rebuild factor parquet (`--force-rebuild`) and assert `feature_version` changed
**Files:** Test: `tests/test_factors.py` (`TestForceRebuildFeatureVersion`)
- [ ] **Step 1: Write the failing test** — the rebuild path is `python -m factors.build_features --force-rebuild`. The stored `feature_version` in the rebuilt parquet metadata must equal `compute_feature_version(get_registry())` over the 23-factor registry, and must DIFFER from the pre-arc 18-factor hash (captured as the 18-name subset). **PERFORMANCE FLAG:** a real `--force-rebuild` recomputes `cdf_realized_vol_720` (O(N·720)) over the full ~55k-bar canonical dataset — expect tens of seconds of wall time dominated by that one factor; this test therefore exercises the version-stamping contract on a small synthetic parquet via `build_features_df`, and the full-dataset rebuild is a manual/CI step noted in Step 4.

```python
# tests/test_factors.py  (append)
class TestForceRebuildFeatureVersion:
    """build_features_df stamps the live 23-factor feature_version; the
    full `--force-rebuild` over the canonical dataset is slow because
    cdf_realized_vol_720 is O(N*720) — exercised on a synthetic frame here."""

    def _synthetic_raw(self, n: int) -> pd.DataFrame:
        rng = np.random.default_rng(123)
        close = 100 + np.cumsum(rng.standard_normal(n)) * 0.5
        idx = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
        return pd.DataFrame({
            "open_time_utc": idx,
            "open": close,
            "high": close + np.abs(rng.standard_normal(n)) * 0.5,
            "low": close - np.abs(rng.standard_normal(n)) * 0.5,
            "close": close,
            "volume": rng.random(n) * 10 + 1,
        })

    def test_rebuilt_features_carry_23_factor_version(self):
        from factors.build_features import build_features_df
        from factors.registry import compute_feature_version, get_registry

        raw = self._synthetic_raw(800)  # > 743 warmup for cdf_realized_vol_720
        reg = get_registry()
        out = build_features_df(raw, reg)
        # All 23 factors present as columns (plus open_time_utc).
        for name in EXPECTED_FACTORS:
            assert name in out.columns
        assert len(out.columns) == 1 + 23  # open_time_utc + 23 factors

        live_version = compute_feature_version(reg)

        # The 18-factor (pre-arc) hash must differ -> rebuild is required.
        sub = FactorRegistry()
        for name in reg.list_names():
            if name not in NEW_FACTORS_THIS_ARC:
                sub.register(reg.get(name))
        old_version = compute_feature_version(sub)
        assert live_version != old_version

    def test_force_rebuild_roundtrips_version_via_parquet(self, tmp_path):
        from factors.build_features import build_features_df
        from factors.registry import compute_feature_version, get_registry

        raw = self._synthetic_raw(800)
        reg = get_registry()
        out = build_features_df(raw, reg)

        parquet_path = tmp_path / "features.parquet"
        # Stamp the live feature_version into parquet metadata, mirroring what
        # `--force-rebuild` writes, then read it back.
        import pyarrow as pa
        import pyarrow.parquet as pq

        table = pa.Table.from_pandas(out, preserve_index=False)
        live_version = compute_feature_version(reg)
        table = table.replace_schema_metadata(
            {**(table.schema.metadata or {}),
             b"feature_version": live_version.encode("utf-8")}
        )
        pq.write_table(table, parquet_path)

        meta = pq.read_table(parquet_path).schema.metadata or {}
        stored = meta[b"feature_version"].decode("utf-8")
        assert stored == live_version
        # And it differs from the pre-arc 18-factor hash.
        sub = FactorRegistry()
        for name in reg.list_names():
            if name not in NEW_FACTORS_THIS_ARC:
                sub.register(reg.get(name))
        assert stored != compute_feature_version(sub)
```

- [ ] **Step 2: Run test to verify it fails** — before the 5 factors are registered, `EXPECTED_FACTORS` has 23 names but the registry has 18, so `name in out.columns` fails for the new names and `len(out.columns) == 24` fails:
  `Run: pytest tests/test_factors.py::TestForceRebuildFeatureVersion -v`
  `Expected: FAIL — KeyError/assert on missing new-factor columns until Tasks 6–9 register them`

- [ ] **Step 3: Implement** — no production code beyond what Tasks 6–9 deliver. If the real `factors/build_features.py` stamping path does not yet write `feature_version` into parquet metadata, match its existing mechanism; do NOT invent a new one. (Verify how the current builder persists `feature_version` by reading `factors/build_features.py` around its parquet-write call before finalizing this test — if it stamps via a sidecar JSON or a different key, mirror that exactly rather than the `replace_schema_metadata` form shown above.)

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_factors.py::TestForceRebuildFeatureVersion -v`
  `Expected: PASS (2 passed)`

  Then the SLOW full-dataset rebuild (manual / CI, NOT in the fast unit run — dominated by `cdf_realized_vol_720`'s O(N·720) rolling apply):
  `Run: python -m factors.build_features --force-rebuild`
  `Expected: rebuild succeeds; stored feature_version in data/features/ equals compute_feature_version(get_registry()) over the 23-factor registry and differs from the prior 18-factor hash`

- [ ] **Step 5: Commit** — `git add tests/test_factors.py && git commit -m "test(factors): --force-rebuild stamps 23-factor feature_version; cdf_realized_vol_720 O(N*720) flagged slow"`

---

**Section B integration notes for the orchestrator:**
- The 5 `SPEC_*` registrations land in `factors/registry.py` `_bootstrap_core_factors` across Tasks 6–9; their tuple ORDER is irrelevant (`list_names()` sorts at registry.py:166). The single authoritative ordering assertion is `EXPECTED_FACTORS` (Task 10), which is the 23-name **alphabetical** list.
- `decay_linear` and `rolling_backward_percentile` (Task 5) are NEVER registered — they are imported by `volatility.py` (Task 8) and `moving_averages.py` (Task 9) and so are deliberately exempt from the G1 `_assert_no_future_ops` scan (G1 runs inside `register()` on registered compute callables only; Section A Task 4 owns G1). This is the contract reason the primitives live in `factors/operators.py` rather than being registered.
- `cdf_realized_vol_720` is the performance hotspot: its inner `rolling(720).apply(_last_rank, raw=True)` is O(N·720); flagged in the factor docstring (Task 8) and in Tasks 8/12 test headers so the full `--force-rebuild` cost is anticipated, not a surprise.

---

## Section C — Ternary Sizing Node (Step 2)

I have everything needed. Here is Section C.

---

### Task 13: SizingSpec model + `position_sizing` union + validation in `strategies/dsl.py`

**Files:** Modify: `strategies/dsl.py`; Test: `tests/test_dsl_sizing.py`

- [ ] **Step 1: Write the failing test** — exercises the new `SizingSpec` model, the `position_sizing` union, registered-factor validation, and the `[0,1]` size bounds. Param values (band edges) are illustrative test fixtures, not Step -1 hypothesis locks.

```python
# tests/test_dsl_sizing.py
import pytest
from pydantic import ValidationError

from strategies.dsl import Condition, ConditionGroup, SizingSpec, StrategyDSL


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
```

- [ ] **Step 2: Run test to verify it fails** —
  `Run: pytest tests/test_dsl_sizing.py -v`
  `Expected: FAIL — ImportError: cannot import name 'SizingSpec' from 'strategies.dsl'`

- [ ] **Step 3: Implement** — add `SizingBand` + `SizingSpec` models and widen the `position_sizing` field to the discriminated union. The factor validator reuses the existing `_registry_from_info` helper so registry injection via `context={"registry": ...}` works identically to `Condition`.

```python
# strategies/dsl.py — add after the Condition class, before ConditionGroup

class SizingBand(BaseModel):
    """One half-open sizing band ``[lower, upper)`` mapping a sizing-factor
    value to an equity fraction.

    ``size`` is the fraction of equity to target while the sizing factor's
    current value falls in this band. Bands are evaluated in declaration
    order by the compiler; the first band whose ``[lower, upper)`` contains
    the value wins. Values outside every band fall through to
    ``SizingSpec.default_size``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    lower: float
    upper: float
    size: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _validate_band_order(self) -> "SizingBand":
        if not (math.isfinite(self.lower) and math.isfinite(self.upper)):
            raise ValueError("band lower/upper must be finite floats")
        if self.lower >= self.upper:
            raise ValueError(
                f"band lower ({self.lower}) must be < upper ({self.upper})"
            )
        return self


class SizingSpec(BaseModel):
    """Factor-conditioned (ternary/laddered) position sizing.

    ``factor`` is a registered factor name whose current-bar value selects
    an equity fraction from ``bands`` (first containing band wins), falling
    back to ``default_size`` when no band matches. All sizes are equity
    fractions in ``[0, 1]``; the compiler emits them via
    ``self.order_target_percent`` so they bypass the configured
    ``PercentSizer`` (see ``strategies/dsl_compiler.py::_compile_sizing``).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    factor: str
    bands: list[SizingBand] = Field(min_length=1, max_length=8)
    default_size: float = Field(ge=0.0, le=1.0)

    @field_validator("factor")
    @classmethod
    def _validate_sizing_factor(cls, v: str, info: ValidationInfo) -> str:
        if not v:
            raise ValueError("sizing factor must be a non-empty string")
        reg = _registry_from_info(info)
        known = set(reg.list_names())
        if v not in known:
            raise ValueError(
                f"unknown sizing factor {v!r}; registered factors: "
                f"{sorted(known)}"
            )
        return v
```

Then widen the `StrategyDSL.position_sizing` field (replace the old `Literal["full_equity"]` line, keeping the surrounding CONTRACT GAP comment block):

```python
    # strategies/dsl.py — StrategyDSL body
    position_sizing: Literal["full_equity"] | SizingSpec
```

And add `SizingBand`, `SizingSpec` to `__all__`:

```python
__all__ = [
    "ALL_OPS",
    "Condition",
    "ConditionGroup",
    "SizingBand",
    "SizingSpec",
    "StrategyDSL",
    "OpLiteral",
    "canonicalize_dsl",
    "compute_dsl_hash",
]
```

- [ ] **Step 4: Run test to verify it passes** —
  `Run: pytest tests/test_dsl_sizing.py -v`
  `Expected: PASS — 7 passed`

- [ ] **Step 5: Commit** —
  `git add strategies/dsl.py tests/test_dsl_sizing.py && git commit -m "feat(dsl): add SizingSpec ternary sizing model + position_sizing union"`

---

### Task 14: D2 `canonicalize_dsl` recurses through `SizingSpec` (green-on-arrival confirm)

**Files:** Test: `tests/test_dsl_sizing.py`

This is a deliberate green-on-arrival regression guard: `canonicalize_dsl` already serializes via `dsl.model_dump(mode="json")` (`strategies/dsl.py:274`), which recurses into nested pydantic models. The test pins that the `SizingSpec` payload appears byte-stably so a future refactor that special-cases `position_sizing` cannot silently drop it.

- [ ] **Step 1: Write the failing test** — (expected to pass immediately; the "failing" run confirms the test is wired in, then we assert it is green by construction).

```python
# tests/test_dsl_sizing.py — append

import json
from strategies.dsl import canonicalize_dsl, compute_dsl_hash


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
```

- [ ] **Step 2: Run test to verify it fails** —
  `Run: pytest tests/test_dsl_sizing.py::test_canonicalize_dsl_recurses_into_sizing_spec tests/test_dsl_sizing.py::test_canonicalize_dsl_byte_stable_for_sizing -v`
  `Expected: PASS on arrival (green confirm) — model_dump(mode="json") already recurses; this task documents that D2 needs NO change. If it FAILS, D2 was special-casing position_sizing and must be reverted to plain model_dump.`

- [ ] **Step 3: Implement** — No production change. Confirm `canonicalize_dsl` body is unchanged at `strategies/dsl.py:273-277` (`json.dumps(dsl.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))`).

- [ ] **Step 4: Run test to verify it passes** —
  `Run: pytest tests/test_dsl_sizing.py -v`
  `Expected: PASS — all sizing tests green`

- [ ] **Step 5: Commit** —
  `git add tests/test_dsl_sizing.py && git commit -m "test(dsl): pin D2 canonicalize_dsl recursion through SizingSpec"`

---

### Task 15: `_canonical_position_sizing` in `agents/hypothesis_hash.py` (D3)

**Files:** Modify: `agents/hypothesis_hash.py`; Test: `tests/test_hypothesis_hash_sizing.py`

`canonicalize_for_hash` currently emits `position_sizing` verbatim (`agents/hypothesis_hash.py:149`). With a `SizingSpec` object that line passes a non-JSON-serializable pydantic model into `json.dumps`, raising `TypeError`. We add a `_canonical_position_sizing` helper that deterministically lowers both the `"full_equity"` string and `SizingSpec` to plain dicts, tagging band edges/sizes at 6-decimal precision (mirroring `_canonical_value`) so two sizings that differ produce distinct hashes.

- [ ] **Step 1: Write the failing test** —

```python
# tests/test_hypothesis_hash_sizing.py
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
```

- [ ] **Step 2: Run test to verify it fails** —
  `Run: pytest tests/test_hypothesis_hash_sizing.py -v`
  `Expected: FAIL — ImportError: cannot import name '_canonical_position_sizing'; and test_canonicalize_for_hash_does_not_raise_on_sizing_spec would raise TypeError (Object of type SizingSpec is not JSON serializable)`

- [ ] **Step 3: Implement** — add the helper and route `position_sizing` through it. Band order is preserved (the compiler uses first-match-wins, so order is semantically load-bearing — bands are NOT sorted, unlike AND/OR groups).

```python
# agents/hypothesis_hash.py — add after _canonical_group_sort_key, import at top

from strategies.dsl import SizingSpec, StrategyDSL  # SizingSpec added to existing import


def _canonical_position_sizing(position_sizing) -> str | dict:
    """Lower ``StrategyDSL.position_sizing`` to a deterministic JSON-safe form.

    - ``"full_equity"`` -> the literal string ``"full_equity"``.
    - :class:`SizingSpec` -> a dict with ``kind="sizing_spec"``, the factor
      name, and bands/default_size whose numeric edges are tagged at
      6-decimal precision via :func:`_canonical_value` (mirroring condition
      scalars). Band ORDER is preserved (first-match-wins is part of the
      strategy's semantics; reordering bands changes behavior, so it must
      change the dedup hash).

    Raises:
        TypeError: if ``position_sizing`` is neither the literal nor a
            SizingSpec (defends against a future union member added without
            updating this canonicalizer).
    """
    if position_sizing == "full_equity":
        return "full_equity"
    if isinstance(position_sizing, SizingSpec):
        return {
            "kind": "sizing_spec",
            "factor": position_sizing.factor,
            "bands": [
                {
                    "lower": _canonical_value(b.lower),
                    "upper": _canonical_value(b.upper),
                    "size": _canonical_value(b.size),
                }
                for b in position_sizing.bands
            ],
            "default_size": _canonical_value(position_sizing.default_size),
        }
    raise TypeError(
        f"unhandled position_sizing type {type(position_sizing).__name__}; "
        f"add a canonical lowering before widening the DSL union."
    )
```

Then change the payload assembly in `canonicalize_for_hash` (`agents/hypothesis_hash.py:149`):

```python
    payload = {
        "entry": canonicalize_groups(dsl.entry),
        "exit": canonicalize_groups(dsl.exit),
        "max_hold_bars": dsl.max_hold_bars,
        "position_sizing": _canonical_position_sizing(dsl.position_sizing),
    }
```

- [ ] **Step 4: Run test to verify it passes** —
  `Run: pytest tests/test_hypothesis_hash_sizing.py tests/test_dsl_sizing.py -v`
  `Expected: PASS — all green; existing full_equity hashes unchanged (string path returns "full_equity" verbatim)`

- [ ] **Step 5: Commit** —
  `git add agents/hypothesis_hash.py tests/test_hypothesis_hash_sizing.py && git commit -m "feat(d3): canonicalize SizingSpec in hypothesis_hash payload"`

---

### Task 16: `_compile_sizing` closure + `position_sizing.factor` warmup in `strategies/dsl_compiler.py`

**Files:** Modify: `strategies/dsl_compiler.py`; Test: `tests/test_dsl_compiler_sizing.py`

Two changes: (1) `_extract_factor_names` must include `position_sizing.factor` so its warmup is honored in `effective_minperiod`; (2) `_compile_sizing(spec, factor_index)` returns a `(cur_row, prev_row) -> float` closure reading `cur_row[idx]` (tuple rows). This task tests the two helpers in isolation; Task 17 wires them through the engine.

- [ ] **Step 1: Write the failing test** —

```python
# tests/test_dsl_compiler_sizing.py
import math

import pytest

from strategies.dsl import Condition, ConditionGroup, SizingSpec, StrategyDSL
from strategies.dsl_compiler import _compile_sizing, _extract_factor_names


def _entry():
    return [ConditionGroup(conditions=[Condition(factor="rsi_14", op="<", value=30.0)])]


def _exit():
    return [ConditionGroup(conditions=[Condition(factor="rsi_14", op=">", value=70.0)])]


def _spec():
    return SizingSpec(
        factor="intrabar_push",
        bands=[
            {"lower": -1.0, "upper": 0.0, "size": 0.25},
            {"lower": 0.0, "upper": 1.0, "size": 0.75},
        ],
        default_size=0.5,
    )


def test_extract_factor_names_includes_sizing_factor():
    dsl = StrategyDSL(
        name="x",
        description="sizing factor must appear in warmup-driving factor list",
        entry=_entry(),
        exit=_exit(),
        position_sizing=_spec(),
    )
    names = _extract_factor_names(dsl)
    assert "rsi_14" in names
    assert "intrabar_push" in names  # sizing factor included
    assert names == sorted(names)


def test_extract_factor_names_full_equity_no_extra():
    dsl = StrategyDSL(
        name="x",
        description="full equity adds no sizing factor",
        entry=_entry(),
        exit=_exit(),
        position_sizing="full_equity",
    )
    assert _extract_factor_names(dsl) == ["rsi_14"]


def test_compile_sizing_band_ladder():
    factor_index = {"intrabar_push": 0}
    fn = _compile_sizing(_spec(), factor_index)
    # value -0.5 -> first band [-1,0) -> 0.25
    assert fn((-0.5,), (0.0,)) == 0.25
    # value 0.5 -> second band [0,1) -> 0.75
    assert fn((0.5,), (0.0,)) == 0.75
    # value 5.0 -> no band -> default 0.5
    assert fn((5.0,), (0.0,)) == 0.5
    # half-open: upper edge 0.0 falls into the SECOND band [0,1), not first
    assert fn((0.0,), (0.0,)) == 0.75


def test_compile_sizing_nan_uses_default():
    factor_index = {"intrabar_push": 0}
    fn = _compile_sizing(_spec(), factor_index)
    assert fn((float("nan"),), (0.0,)) == 0.5  # NaN -> default, never a band
```

- [ ] **Step 2: Run test to verify it fails** —
  `Run: pytest tests/test_dsl_compiler_sizing.py -v`
  `Expected: FAIL — ImportError: cannot import name '_compile_sizing'; and test_extract_factor_names_includes_sizing_factor FAILS because intrabar_push is absent`

- [ ] **Step 3: Implement** — add `_compile_sizing` and extend `_extract_factor_names`. The closure mirrors the comparison helpers' NaN policy (NaN reads the default, never a band). Half-open `[lower, upper)` matches the `SizingBand` validator's `lower < upper` invariant.

```python
# strategies/dsl_compiler.py — extend _extract_factor_names

from strategies.dsl import (  # SizingSpec added to existing import block
    Condition,
    ConditionGroup,
    SizingSpec,
    StrategyDSL,
    canonicalize_dsl,
    compute_dsl_hash,
)


def _extract_factor_names(dsl: StrategyDSL) -> list[str]:
    """Return sorted list of all distinct factor names referenced by the DSL.

    Includes condition LHS ``factor`` fields, string-typed RHS ``value``
    fields, AND ``position_sizing.factor`` when sizing is a
    :class:`SizingSpec` (so its warmup drives ``effective_minperiod`` —
    otherwise the sizing factor could be NaN at the first firable bar).
    Registry validation has already happened at schema time.
    """
    names: set[str] = set()
    for groups in (dsl.entry, dsl.exit):
        for g in groups:
            for c in g.conditions:
                names.add(c.factor)
                if isinstance(c.value, str):
                    names.add(c.value)
    if isinstance(dsl.position_sizing, SizingSpec):
        names.add(dsl.position_sizing.factor)
    return sorted(names)
```

```python
# strategies/dsl_compiler.py — add after _compile_groups

def _compile_sizing(
    spec: SizingSpec,
    factor_index: dict[str, int],
) -> Callable[[tuple, tuple], float]:
    """Compile a SizingSpec to a closure ``(cur_row, prev_row) -> float``.

    Reads the sizing factor's current-bar value from ``cur_row`` (a tuple
    keyed by ``factor_index``) and returns the equity fraction for the
    first band whose half-open ``[lower, upper)`` contains it, falling back
    to ``spec.default_size``. ``prev_row`` is accepted for signature
    symmetry with condition closures but is unused (sizing is a
    current-bar decision).

    NaN policy: if the factor value is NaN, return ``default_size`` — a NaN
    never falls inside any band (mirrors the comparison helpers'
    NaN-is-never-True rule). This keeps sizing well-defined during the
    factor-NaN warmup window.
    """
    idx = factor_index[spec.factor]
    bands = tuple((b.lower, b.upper, b.size) for b in spec.bands)
    default_size = spec.default_size

    def eval_sizing(cur_row: tuple, prev_row: tuple) -> float:
        val = cur_row[idx]
        if math.isnan(val):
            return default_size
        for lower, upper, size in bands:
            if lower <= val < upper:
                return size
        return default_size

    return eval_sizing
```

Finally, wire the closure into the compiled strategy. In `compile_dsl_to_strategy`, after `exit_eval = _compile_groups(...)` (`:668`), add:

```python
    # strategies/dsl_compiler.py — inside compile_dsl_to_strategy, after exit_eval
    sizing_spec = dsl.position_sizing
    if isinstance(sizing_spec, SizingSpec):
        sizing_eval = _compile_sizing(sizing_spec, factor_index)
    else:
        sizing_eval = None  # "full_equity" path keeps self.buy()
```

Then in `CompiledStrategy.next()`, replace the entry-fire `self.buy()` block (`:740-741`) with a sizing-aware emit. `order_target_percent` computes its own size and bypasses the configured `PercentSizer` (`execution_model.py:148`); fills still occur at N+1 open because `set_coc/set_coo(False)`:

```python
            if not self.position:
                if entry_eval(cur_row, prev_row):
                    if sizing_eval is None:
                        self.buy()
                    else:
                        frac = sizing_eval(cur_row, prev_row)
                        # order_target_percent computes its own size,
                        # bypassing the configured PercentSizer. Fills at
                        # N+1 open (coc/coo False). target=0.0 emits no
                        # position, so the entry is a no-op for that bar —
                        # acceptable since the entry signal will re-fire.
                        self.order_target_percent(target=frac)
                    self._entry_bar = len(self)
                return
```

- [ ] **Step 4: Run test to verify it passes** —
  `Run: pytest tests/test_dsl_compiler_sizing.py -v`
  `Expected: PASS — 5 passed`

- [ ] **Step 5: Commit** —
  `git add strategies/dsl_compiler.py tests/test_dsl_compiler_sizing.py && git commit -m "feat(compiler): _compile_sizing closure + sizing factor in warmup extraction"`

---

### Task 17: Compiled-through-engine test (size ladder, N+1 open fill, PercentSizer bypass)

**Files:** Test: `tests/test_dsl_compiler_sizing.py`

End-to-end through `compile_dsl_to_strategy` + `build_features_df` + `ParquetFeed.from_parquet`. `ParquetFeed` has no `from_dataframe`, so we write a synthetic OHLCV frame to a temp parquet, build features from it via `build_features_df`, inject the features DataFrame through `features_df_override`, and run a tiny Cerebro. The H1-style band thresholds here are test fixtures only; real hypothesis param values are Step -1 human-locked and referenced symbolically (`THETA_PUSH`) where a production wiring would use them.

- [ ] **Step 1: Write the failing test** —

```python
# tests/test_dsl_compiler_sizing.py — append

from datetime import datetime, timedelta, timezone

import backtrader as bt
import pandas as pd

from backtest.bt_parquet_feed import ParquetFeed
from backtest.execution_model import configure_cerebro
from factors.build_features import build_features_df
from factors.registry import get_registry
from strategies.dsl_compiler import compile_dsl_to_strategy


def _synthetic_ohlcv(n_bars: int) -> pd.DataFrame:
    """Deterministic hourly OHLCV; an up-then-down ramp so intrabar_push
    and rsi_14 both vary enough to exercise the entry + sizing ladder.
    """
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    rows = []
    price = 100.0
    for i in range(n_bars):
        # Oscillate so RSI dips below threshold periodically.
        drift = math.sin(i / 5.0) * 3.0
        o = price
        c = price + drift
        h = max(o, c) + 1.0
        low = min(o, c) - 1.0
        rows.append(
            {
                "open_time_utc": start + timedelta(hours=i),
                "open": o,
                "high": h,
                "low": low,
                "close": c,
                "volume": 1000.0 + i,
                "quote_volume": (1000.0 + i) * c,
                "trade_count": 10,
            }
        )
        price = c
    df = pd.DataFrame(rows)
    df["open_time_utc"] = df["open_time_utc"].astype("datetime64[ms, UTC]")
    return df


# Step -1 human-locked hypothesis param (illustrative symbol; the real
# value is fixed in the locked spec, not chosen here).
THETA_PUSH = 0.0


def test_compiled_sizing_runs_through_engine(tmp_path):
    registry = get_registry()
    raw = _synthetic_ohlcv(900)  # > max sizing/condition warmup
    raw_path = tmp_path / "raw.parquet"
    raw.to_parquet(raw_path, index=False)

    features_df = build_features_df(raw, registry)

    spec = SizingSpec(
        factor="intrabar_push",
        bands=[
            {"lower": -10.0, "upper": THETA_PUSH, "size": 0.25},
            {"lower": THETA_PUSH, "upper": 10.0, "size": 0.75},
        ],
        default_size=0.5,
    )
    dsl = StrategyDSL(
        name="ternary_engine",
        description="ternary sizing compiled through the Phase 1 engine",
        entry=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op="<", value=55.0)])],
        exit=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op=">", value=60.0)])],
        position_sizing=spec,
        max_hold_bars=24,
    )

    strat_cls = compile_dsl_to_strategy(
        dsl, registry=registry, write_manifest=False
    )

    cerebro = bt.Cerebro()
    configure_cerebro(cerebro, cash=100_000.0)  # installs PercentSizer
    feed = ParquetFeed.from_parquet(raw_path)
    cerebro.adddata(feed)

    captured = {"sizes": []}

    class _SizeRecorder(bt.Analyzer):
        def notify_order(self, order):
            if order.status == order.Completed and order.isbuy():
                captured["sizes"].append(
                    (order.executed.size, order.executed.price)
                )

    cerebro.addstrategy(strat_cls, features_df_override=features_df)
    cerebro.addanalyzer(_SizeRecorder, _name="rec")
    cerebro.run()

    # At least one buy executed.
    assert len(captured["sizes"]) >= 1
    # Position notional well below full-equity: order_target_percent at
    # <= 0.75 bypasses the 99% PercentSizer. Full-equity (~99%) would buy
    # ~ cash / price units; a 0.75 target buys at most ~0.76 of that.
    first_size, first_price = captured["sizes"][0]
    full_equity_units = 100_000.0 / first_price
    assert 0 < first_size < 0.80 * full_equity_units


def test_compiled_sizing_fills_at_next_open(tmp_path):
    """Sanity: coc/coo are False so the engine fills at N+1 open, not the
    signal bar's close. We assert the executed price equals some bar's
    OPEN value, never a close-only value.
    """
    registry = get_registry()
    raw = _synthetic_ohlcv(900)
    raw_path = tmp_path / "raw.parquet"
    raw.to_parquet(raw_path, index=False)
    features_df = build_features_df(raw, registry)

    dsl = StrategyDSL(
        name="ternary_open",
        description="verify N+1 open fill under sizing emit",
        entry=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op="<", value=55.0)])],
        exit=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op=">", value=60.0)])],
        position_sizing=SizingSpec(
            factor="intrabar_push",
            bands=[{"lower": -10.0, "upper": 10.0, "size": 0.5}],
            default_size=0.5,
        ),
    )
    strat_cls = compile_dsl_to_strategy(dsl, registry=registry, write_manifest=False)

    cerebro = bt.Cerebro()
    configure_cerebro(cerebro, cash=100_000.0)
    cerebro.adddata(ParquetFeed.from_parquet(raw_path))

    open_prices = set(round(float(o), 6) for o in raw["open"])
    fills = {"prices": []}

    class _OpenChecker(bt.Analyzer):
        def notify_order(self, order):
            if order.status == order.Completed:
                fills["prices"].append(round(float(order.executed.price), 6))

    cerebro.addstrategy(strat_cls, features_df_override=features_df)
    cerebro.addanalyzer(_OpenChecker, _name="oc")
    cerebro.run()

    assert fills["prices"], "expected at least one fill"
    for px in fills["prices"]:
        assert px in open_prices  # filled at a bar OPEN, never close-only
```

- [ ] **Step 2: Run test to verify it fails** —
  `Run: pytest tests/test_dsl_compiler_sizing.py::test_compiled_sizing_runs_through_engine tests/test_dsl_compiler_sizing.py::test_compiled_sizing_fills_at_next_open -v`
  `Expected: FAIL before Task 16's next() wiring lands (no order_target_percent emit / sizing factor absent from warmup -> NaN sizing). After Task 16: PASS.`

- [ ] **Step 3: Implement** — No new production code; this test validates Task 16's wiring through the real engine. If `test_compiled_sizing_runs_through_engine` shows full-equity sizing, the bug is a missing `order_target_percent` branch in `next()` (Task 16 Step 3) — fix there, not here.

- [ ] **Step 4: Run test to verify it passes** —
  `Run: pytest tests/test_dsl_compiler_sizing.py -v`
  `Expected: PASS — sizing ladder applied, fills at N+1 open, PercentSizer bypassed`

- [ ] **Step 5: Commit** —
  `git add tests/test_dsl_compiler_sizing.py && git commit -m "test(compiler): end-to-end ternary sizing through engine + N+1 open fill"`

---

### Task 18: Manifest + D3-hash drift on sizing change

**Files:** Test: `tests/test_dsl_compiler_sizing.py`

Two drift surfaces must move when sizing changes: D2's compilation manifest (`canonical_dsl` field, which embeds `position_sizing` via `canonicalize_dsl`) and D3's `hash_dsl`. This pins both so a sizing edit can never silently reuse a stale manifest or collide in dedup.

- [ ] **Step 1: Write the failing test** —

```python
# tests/test_dsl_compiler_sizing.py — append

from agents.hypothesis_hash import hash_dsl
from strategies.dsl import canonicalize_dsl
from strategies.dsl_compiler import (
    ManifestDriftError,
    write_compilation_manifest,
)


def _dsl_with_default(default_size: float):
    return StrategyDSL(
        name="drift",
        description="sizing drift detection strategy",
        entry=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op="<", value=30.0)])],
        exit=[ConditionGroup(conditions=[
            Condition(factor="rsi_14", op=">", value=70.0)])],
        position_sizing=SizingSpec(
            factor="intrabar_push",
            bands=[{"lower": 0.0, "upper": 1.0, "size": 0.5}],
            default_size=default_size,
        ),
    )


def test_manifest_drift_on_sizing_change(tmp_path):
    registry = get_registry()
    dsl_a = _dsl_with_default(0.5)
    dsl_b = _dsl_with_default(0.6)

    # Same dsl_hash filename key forces a drift comparison on the second
    # write (we pin the key so the manifest path collides deliberately).
    shared_key = "deadbeefdeadbeef"
    write_compilation_manifest(
        dsl_a, registry, manifest_dir=tmp_path, dsl_hash=shared_key
    )
    with pytest.raises(ManifestDriftError, match="canonical_dsl mismatch"):
        write_compilation_manifest(
            dsl_b, registry, manifest_dir=tmp_path, dsl_hash=shared_key
        )


def test_canonical_dsl_differs_on_sizing_change():
    assert canonicalize_dsl(_dsl_with_default(0.5)) != canonicalize_dsl(
        _dsl_with_default(0.6)
    )


def test_d3_hash_differs_on_sizing_change():
    assert hash_dsl(_dsl_with_default(0.5)) != hash_dsl(_dsl_with_default(0.6))
```

- [ ] **Step 2: Run test to verify it fails** —
  `Run: pytest tests/test_dsl_compiler_sizing.py::test_manifest_drift_on_sizing_change tests/test_dsl_compiler_sizing.py::test_d3_hash_differs_on_sizing_change -v`
  `Expected: FAIL before Tasks 13/15 land (SizingSpec unconstructable / hash_dsl TypeError). After: PASS.`

- [ ] **Step 3: Implement** — No new production code. Drift detection already keys on `canonicalize_dsl` (`dsl_compiler.py:466`, `_drift_report` "canonical_dsl mismatch") and D3 keys on `_canonical_position_sizing` (Task 15). This task is the cross-cutting regression guard tying both surfaces together.

- [ ] **Step 4: Run test to verify it passes** —
  `Run: pytest tests/test_dsl_compiler_sizing.py tests/test_dsl_sizing.py tests/test_hypothesis_hash_sizing.py -v`
  `Expected: PASS — manifest drift raised on sizing change; D2 canonical + D3 hash both shift`

- [ ] **Step 5: Commit** —
  `git add tests/test_dsl_compiler_sizing.py && git commit -m "test(compiler): manifest + D3-hash drift on SizingSpec change"`

---

## Section D — N* Plumbing + Sealed-Dir Guard (Step 2)

I now have all signatures verified. I have everything needed to write Section D with real code that threads `n_star` through the existing `N_STAR`-hardcoded call sites. Here is my assigned section.

---

### Task 19: Thread `n_star` through `evaluate_cohort` (body + MC + output dicts) AND through `_degenerate_fail_row`

**Files:**
- Modify: `backtest/tier6_dsr.py`
- Test: `tests/test_tier6_dsr.py`

Currently `evaluate_cohort` accepts no `n_star` parameter and its body hardcodes `N_STAR` in five places: the `mc_expected_max_ratio(N_STAR, ...)` call (:877), and the output/JSON `"n_star": N_STAR` entries (:891, :906). The per-candidate `_evaluate_one` already accepts `n_star=` (:624) but `evaluate_cohort` never passes it. Separately, `_degenerate_fail_row` hardcodes `"n_star": N_STAR` (:608). This task adds an `n_star: int = N_STAR` parameter to `evaluate_cohort`, threads it into every site (including `_evaluate_one` and `mc_expected_max_ratio`), and threads it into `_degenerate_fail_row`. **The default stays `N_STAR=18`, so the sealed-artifact reproduction (Task 22) is unaffected.** `PATHB_N_STAR` is the Step -1 human-locked Path-B multiplicity value (referenced symbolically; the Step -1 lock fixes its numeric value — for the default-path regression here we exercise a non-18 probe value `7` purely to prove plumbing, never the locked capital value).

- [ ] **Step 1: Write the failing test** — add to `tests/test_tier6_dsr.py`:

```python
# ==========================================================================
# Section D (Tasks 19-22): N* plumbing through evaluate_cohort + CLI
# ==========================================================================
def test_evaluate_cohort_threads_non_default_n_star_into_rows_and_mc():
    # Task 19: a non-default n_star must flow into (a) every per-candidate row's
    # "n_star" field, (b) the MC validation block's "n_star", and (c) the
    # top-level out["n_star"]. Probe value 7 != N_STAR=18 (NOT the Step -1
    # locked PATHB_N_STAR capital value; purely a plumbing probe). Writes to a
    # tmp dir so the sealed tier6_dsr_v1/ is untouched.
    probe = 7
    assert probe != t6.N_STAR
    out = t6.evaluate_cohort(out_dir=None, n_sims=500, write=False, n_star=probe)
    # (a) every authoritative + companion row carries n_star=probe
    for r in (*out["authoritative"], *out["companion"]):
        assert r["n_star"] == probe, f"row {r['hypothesis_hash']} kept n_star={r['n_star']}"
    # (b) MC block used probe
    assert out["mc_validation"]["n_star"] == probe
    # (c) top-level metadata reflects probe
    assert out["n_star"] == probe


def test_evaluate_cohort_default_n_star_is_18():
    # Task 19: omitting n_star keeps the sealed default (N_STAR=18) everywhere.
    out = t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    assert out["n_star"] == 18
    assert all(r["n_star"] == 18 for r in out["authoritative"])
    assert all(r["n_star"] == 18 for r in out["companion"])


def test_degenerate_fail_row_threads_non_default_n_star(monkeypatch):
    # Task 19: a degenerate flagged-fail row produced under a non-default
    # n_star must carry that n_star (previously hardcoded N_STAR at :608).
    # Inject one Mertens-degenerate candidate and run the cohort at n_star=7.
    probe = 7
    df = t6._read_cohort_csv()
    locked, _ = t6.derive_cohort(df)
    degenerate_hash = locked[0]
    real_loader = t6.load_candidate_moments

    def fake_loader(hypothesis_hash, frame, **kwargs):
        if hypothesis_hash == degenerate_hash:
            # term = 1 - 5*2 + 0 = -9 < 0 -> mertens_variance raises ValueError
            return t6.CandidateMoments(
                hypothesis_hash, "synthetic_degenerate", "test",
                sr_per_bar=2.0, gamma3=5.0, gamma4=1.0, T=100, trades=None)
        return real_loader(hypothesis_hash, frame)

    monkeypatch.setattr(t6, "load_candidate_moments", fake_loader)
    out = t6.evaluate_cohort(out_dir=None, n_sims=0, write=False, n_star=probe)
    degen_rows = [r for r in out["authoritative"]
                  if r["mertens_degenerate_flag"] is True]
    assert degen_rows, "expected at least one injected degenerate row"
    for r in degen_rows:
        assert r["n_star"] == probe, (
            f"degenerate row kept hardcoded n_star={r['n_star']} (want {probe})")


def test_degenerate_fail_row_helper_accepts_n_star_kwarg():
    # Task 19: the helper itself honors an explicit n_star (default stays N_STAR).
    cm = t6.CandidateMoments(
        "deadbeefdeadbeef", "synthetic_degenerate", "test",
        sr_per_bar=2.0, gamma3=5.0, gamma4=1.0, T=100, trades=None)
    exc = ValueError("non-positive Mertens variance term")
    row_default = t6._degenerate_fail_row("deadbeefdeadbeef", cm, exc)
    assert row_default["n_star"] == t6.N_STAR
    row_probe = t6._degenerate_fail_row("deadbeefdeadbeef", cm, exc, n_star=7)
    assert row_probe["n_star"] == 7
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_tier6_dsr.py::test_evaluate_cohort_threads_non_default_n_star_into_rows_and_mc tests/test_tier6_dsr.py::test_degenerate_fail_row_threads_non_default_n_star tests/test_tier6_dsr.py::test_degenerate_fail_row_helper_accepts_n_star_kwarg -v`
  `Expected: FAIL — TypeError: evaluate_cohort() got an unexpected keyword argument 'n_star'` (and `_degenerate_fail_row()` got an unexpected keyword argument `n_star`).

- [ ] **Step 3: Implement** — edit `backtest/tier6_dsr.py`.

First, thread `n_star` into the `_degenerate_fail_row` signature and replace the hardcoded `"n_star": N_STAR` at :608:

```python
def _degenerate_fail_row(
    hypothesis_hash: str,
    cm: CandidateMoments | None,
    exc: Exception,
    n_star: int = N_STAR,
) -> dict:
    """Build a flagged auto-fail row for a candidate whose evaluation raised.

    A3 (mertens-degenerate auto-fail-flag): a degenerate candidate (non-positive
    Mertens variance term, or any ``ValueError`` from ``evaluate_candidate``)
    must NEVER crash the cohort run. We emit a flagged-fail row instead.

    IMPORTANT-1: the 11 DSR numeric columns (``var_sr_null`` + the per-form
    ``er/sr_star/deflated_z/psr/dsr_statistic``) are populated with
    ``float("nan")`` rather than left absent. The CSV writer's ``restval=""``
    would otherwise write empty strings for missing keys, which would break a
    future ``df["psr_B"].astype(float)`` over a cohort that contains a
    degenerate row. NaN keeps every numeric column numeric-parseable. (The
    current cohort has 0 degenerate rows, so this is purely defensive.)

    Args:
        hypothesis_hash: The candidate identifier.
        cm: The loaded moments if available (for identifying fields), else None.
        exc: The captured exception (its ``str`` becomes ``failure_reason``).
        n_star: Effective number of independent trials carried into the row's
            ``n_star`` context field (MINOR-1 self-describing column). Defaults
            to ``N_STAR=18``; threaded from ``_evaluate_one`` so a degenerate
            row under a non-default multiplicity records the multiplicity that
            was actually in force, not a stale hardcoded 18.

    Returns:
        A result dict with ``pass_B = pass_A = False``,
        ``mertens_degenerate_flag = True``, ``failure_reason``, any available
        identifying fields, all 11 DSR numeric columns set to ``float("nan")``,
        ``n_star`` / ``z_pass`` (MINOR-1), and the other flags set to safe
        defaults. Contains every ``_RESULT_FIELDS`` key.
    """
    nan = float("nan")
    row: dict = {
        "hypothesis_hash": hypothesis_hash,
        "name": cm.name if cm is not None else None,
        "theme": cm.theme if cm is not None else None,
        "T": cm.T if cm is not None else None,
        "sr_per_bar": cm.sr_per_bar if cm is not None else None,
        "gamma3": cm.gamma3 if cm is not None else None,
        "gamma4": cm.gamma4 if cm is not None else None,
        "trades": cm.trades if cm is not None else None,
        # IMPORTANT-1: the 11 DSR numeric columns as NaN (numeric-parseable).
        "var_sr_null": nan,
        "er_B": nan, "sr_star_B": nan, "deflated_z_B": nan,
        "psr_B": nan, "dsr_statistic_B": nan,
        "er_A": nan, "sr_star_A": nan, "deflated_z_A": nan,
        "psr_A": nan, "dsr_statistic_A": nan,
        # MINOR-1: self-describing context fields carried even on degenerate rows.
        # n_star is threaded (no longer hardcoded N_STAR) so a degenerate row
        # under a non-default multiplicity records the multiplicity in force.
        "n_star": n_star,
        "z_pass": Z_PASS,
        "pass_B": False,
        "pass_A": False,
        "mertens_degenerate_flag": True,
        "failure_reason": str(exc),
        "g4_high_flag": False,
        "provisional_flag": False,
        "r21_indeterminate_flag": hypothesis_hash in R21_INDETERMINATE,
    }
    return row
```

Then pass `n_star` through `_evaluate_one`'s degenerate branch (the clean branch already threads `n_star` into `evaluate_candidate`). Replace the `except` body at :664-666:

```python
    except ValueError as exc:
        # ONLY Mertens math degeneracy is caught here. Thread n_star so the
        # flagged-fail row records the multiplicity actually in force (not a
        # stale hardcoded N_STAR).
        return _degenerate_fail_row(hypothesis_hash, cm, exc, n_star=n_star)
```

Now add `n_star` to `evaluate_cohort` and replace every hardcoded `N_STAR` in its body. Change the signature (:799-804):

```python
def evaluate_cohort(
    out_dir: Path | None = DEFAULT_OUT_DIR,
    n_sims: int = 100_000,
    write: bool = True,
    holdout_dir: Path = HOLDOUT_DIR,
    n_star: int = N_STAR,
) -> dict:
```

In its docstring `Args:` block, add (after the `holdout_dir` entry):

```python
        n_star: Effective number of independent trials (multiplicity N*)
            threaded into every per-candidate ``evaluate_candidate`` call, the
            Monte-Carlo expected-max validation, and the output/JSON metadata.
            Defaults to ``N_STAR=18`` (the sealed value); a non-default value is
            only used by an explicit Path-B re-evaluation into a NON-sealed
            out_dir (the CLI guards this in ``main()`` — Task 21).
```

Replace the per-candidate loop calls (:862 and :868) to thread `n_star`:

```python
    authoritative: list[dict] = []
    for h in locked:
        row = _evaluate_one(h, df, n_star=n_star, holdout_dir=holdout_dir)
        row["non_authoritative"] = False
        authoritative.append(row)

    companion_rows: list[dict] = []
    for h in companion:
        row = _evaluate_one(h, df, n_star=n_star, holdout_dir=holdout_dir)
        row["non_authoritative"] = True
        # Resolve the name for monday_flag from the cohort frame (the row's
        # `name` may be None on a degenerate auto-fail).
        name = str(df.loc[df["hypothesis_hash"] == h, "name"].iloc[0])
        row["monday_flag"] = is_monday_pattern(name)
        companion_rows.append(row)
```

Replace the MC call (:877):

```python
    promotion_list = [r for r in authoritative if r["pass_B"] is True]
    mc = mc_expected_max_ratio(n_star, n_sims=n_sims) if n_sims else {}
```

Replace the top-level output dict `"n_star": N_STAR` (:891):

```python
    out = {
        "authoritative": authoritative,
        "companion": companion_rows,
        "promotion_list": promotion_list,
        "degenerate_count": degenerate_count,
        "mc_validation": mc,
        "n_star": n_star,
        "alpha": ALPHA,
        "authoritative_form": "B",
        "companion_form": "B",
    }
```

Replace the promotion-list JSON `"n_star": N_STAR` (:906):

```python
        (out_dir / "tier6_promotion_list.json").write_text(json.dumps(
            {
                "n_star": n_star,
                "alpha": ALPHA,
                "form": "B",
                "promoted": [r["hypothesis_hash"] for r in promotion_list],
                "count": len(promotion_list),
            },
            indent=2,
        ))
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_tier6_dsr.py -k "n_star or degenerate" -v`
  `Expected: PASS — all Task 19 tests green; pre-existing degenerate/n_star tests (test_evaluate_cohort_degenerate_count_positive_when_injected, test_degenerate_fail_row_has_all_result_fields_with_nan_numerics, test_results_csv_self_describing_includes_n_star_and_z_pass) still pass (default path unchanged).`

- [ ] **Step 5: Commit** (execution waits for Charlie authorization)
  `git add backtest/tier6_dsr.py tests/test_tier6_dsr.py && git commit -m "feat(tier6-dsr): thread n_star through evaluate_cohort body + _degenerate_fail_row (default N_STAR=18 unchanged)"`

---

### Task 20: CSV `n_star` column carries a non-18 value end-to-end

**Files:**
- Modify: `backtest/tier6_dsr.py` (no code change expected — verification task; `_RESULT_FIELDS` already contains `n_star` at :535)
- Test: `tests/test_tier6_dsr.py`

`_RESULT_FIELDS` already lists `"n_star"` (:535) and `evaluate_candidate` already emits per-row `"n_star"` (:398). After Task 19 threads a non-default `n_star` into every row dict, the `_write_csv` path must carry that value into the written `tier6_dsr_results.csv` and `tier6_dsr_companion.csv` — i.e. the column is no longer constant-18 when a non-default `n_star` is used. This is a behavioral regression test confirming the CSV is genuinely self-describing of the multiplicity actually in force. No new implementation is expected; if the column does NOT carry the probe value, that is a Task 19 plumbing defect to fix here.

- [ ] **Step 1: Write the failing test** — add to `tests/test_tier6_dsr.py`:

```python
def test_results_and_companion_csv_carry_non_default_n_star(tmp_path):
    # Task 20: written CSVs must carry the non-default n_star end-to-end
    # (not a hardcoded 18). Probe 7 != N_STAR; writes to tmp (sealed dir safe).
    probe = 7
    assert probe != t6.N_STAR
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=0, n_star=probe)
    res_df = pd.read_csv(tmp_path / "tier6_dsr_results.csv")
    comp_df = pd.read_csv(tmp_path / "tier6_dsr_companion.csv")
    assert len(res_df) == 18
    assert len(comp_df) == 21
    assert "n_star" in res_df.columns
    assert "n_star" in comp_df.columns
    assert (res_df["n_star"] == probe).all()
    assert (comp_df["n_star"] == probe).all()
    # promotion JSON also reflects the probe multiplicity
    promo = json.loads((tmp_path / "tier6_promotion_list.json").read_text())
    assert promo["n_star"] == probe


def test_results_csv_default_n_star_still_18(tmp_path):
    # Task 20: omitting n_star keeps the sealed default in the CSV.
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=0)
    res_df = pd.read_csv(tmp_path / "tier6_dsr_results.csv")
    assert (res_df["n_star"] == 18).all()
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_tier6_dsr.py::test_results_and_companion_csv_carry_non_default_n_star -v`
  `Expected: FAIL (RED) before Task 19 is applied — TypeError on the n_star kwarg; if run AFTER Task 19, this test should already PASS because _RESULT_FIELDS already carries n_star. If it FAILS post-Task-19 with an AssertionError (column == 18 not 7), that signals a missed N_STAR site in the Task 19 plumbing — fix it in Step 3.`

- [ ] **Step 3: Implement** — No production change is expected: `_RESULT_FIELDS` already includes `"n_star"` (:535), `evaluate_candidate` already emits it per-row (:398), and `_write_csv` already passes every row dict through `csv.DictWriter` with `extrasaction="ignore"` (:685), so the threaded value flows through automatically. If Step 2 surfaced an `AssertionError` (a written column still reads 18 under `probe=7`), locate the residual hardcoded `N_STAR` in the Task 19 call chain (most likely a `_evaluate_one`/`_degenerate_fail_row` call site that did not forward `n_star=`) and forward it. Otherwise this task is a no-op verification.

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_tier6_dsr.py -k "csv and n_star" -v`
  `Expected: PASS — test_results_and_companion_csv_carry_non_default_n_star, test_results_csv_default_n_star_still_18, plus pre-existing test_results_csv_self_describing_includes_n_star_and_z_pass all green.`

- [ ] **Step 5: Commit** (execution waits for Charlie authorization)
  `git add tests/test_tier6_dsr.py && git commit -m "test(tier6-dsr): assert CSV n_star column carries non-default multiplicity end-to-end"`

---

### Task 21: CLI `--n-star` flag (default 18) + HARD SAFETY GUARD against overwriting sealed `tier6_dsr_v1/`

**Files:**
- Modify: `backtest/tier6_dsr.py` (`main()`)
- Test: `tests/test_tier6_dsr.py`

Add a `--n-star` argument (`type=int, default=N_STAR`) to `main()`'s parser, and thread `args.n_star` into the `evaluate_cohort(...)` call. **Critically**, add a HARD SAFETY GUARD: when a non-default `n_star` is requested with NO explicit `--out-dir` and NOT `--dry-run`, the run would default to `DEFAULT_OUT_DIR` (the sealed `data/phase2c_evaluation_gate/tier6_dsr_v1/`) and overwrite it with non-sealed-multiplicity artifacts. This must be rejected with a clear error (return 1, no write). The guard fires BEFORE `evaluate_cohort` so no artifact is touched. `PATHB_N_STAR` (the Step -1 human-locked Path-B multiplicity) is the real operational driver of this flag; the guard ensures any Path-B run is forced to target a non-sealed `--out-dir`.

- [ ] **Step 1: Write the failing test** — add to `tests/test_tier6_dsr.py`:

```python
def test_main_n_star_flag_threads_into_cohort(monkeypatch):
    # Task 21: --n-star is parsed and threaded into evaluate_cohort. Spy on the
    # call so we do not run a real cohort (and never touch the sealed dir).
    captured = {}

    def spy(out_dir, n_sims, write, holdout_dir, n_star):
        captured["n_star"] = n_star
        captured["out_dir"] = out_dir
        return {
            "authoritative": [], "companion": [], "promotion_list": [],
            "degenerate_count": 0, "mc_validation": {}, "n_star": n_star,
            "alpha": t6.ALPHA, "authoritative_form": "B", "companion_form": "B",
        }

    monkeypatch.setattr(t6, "evaluate_cohort", spy)
    # explicit non-sealed out-dir so the safety guard does not fire
    rc = t6.main(["--n-star", "7", "--out-dir", "/tmp/pathb_probe", "--n-sims", "0"])
    assert rc == 0
    assert captured["n_star"] == 7


def test_main_n_star_default_is_18(monkeypatch):
    # Task 21: omitting --n-star passes N_STAR=18.
    captured = {}

    def spy(out_dir, n_sims, write, holdout_dir, n_star):
        captured["n_star"] = n_star
        return {
            "authoritative": [], "companion": [], "promotion_list": [],
            "degenerate_count": 0, "mc_validation": {}, "n_star": n_star,
            "alpha": t6.ALPHA, "authoritative_form": "B", "companion_form": "B",
        }

    monkeypatch.setattr(t6, "evaluate_cohort", spy)
    rc = t6.main(["--out-dir", "/tmp/pathb_probe", "--n-sims", "0"])
    assert rc == 0
    assert captured["n_star"] == 18


def test_main_rejects_non_default_n_star_without_out_dir(monkeypatch):
    # Task 21 HARD SAFETY GUARD: a non-default n_star with NO --out-dir and NOT
    # --dry-run would default to the SEALED tier6_dsr_v1 dir and overwrite it.
    # main() must reject (return 1) BEFORE evaluate_cohort runs (no write).
    def boom(*a, **k):
        raise AssertionError("evaluate_cohort must NOT run when the guard fires")

    monkeypatch.setattr(t6, "evaluate_cohort", boom)
    rc = t6.main(["--n-star", "7", "--n-sims", "0"])
    assert rc == 1


def test_main_non_default_n_star_allowed_with_dry_run(monkeypatch):
    # Task 21: --dry-run writes nothing, so a non-default n_star is safe even
    # without --out-dir (the guard does NOT fire under --dry-run).
    captured = {}

    def spy(out_dir, n_sims, write, holdout_dir, n_star):
        captured["write"] = write
        captured["n_star"] = n_star
        return {
            "authoritative": [], "companion": [], "promotion_list": [],
            "degenerate_count": 0, "mc_validation": {}, "n_star": n_star,
            "alpha": t6.ALPHA, "authoritative_form": "B", "companion_form": "B",
        }

    monkeypatch.setattr(t6, "evaluate_cohort", spy)
    rc = t6.main(["--n-star", "7", "--dry-run", "--n-sims", "0"])
    assert rc == 0
    assert captured["write"] is False
    assert captured["n_star"] == 7


def test_main_default_n_star_without_out_dir_is_allowed(monkeypatch):
    # Task 21: the guard fires ONLY for a non-default n_star. The sealed
    # reproduction path (n_star=18, default out_dir, no --dry-run) is permitted.
    captured = {}

    def spy(out_dir, n_sims, write, holdout_dir, n_star):
        captured["out_dir"] = out_dir
        captured["n_star"] = n_star
        return {
            "authoritative": [], "companion": [], "promotion_list": [],
            "degenerate_count": 0, "mc_validation": {}, "n_star": n_star,
            "alpha": t6.ALPHA, "authoritative_form": "B", "companion_form": "B",
        }

    monkeypatch.setattr(t6, "evaluate_cohort", spy)
    rc = t6.main(["--n-sims", "0"])  # default n_star=18, default out_dir, real write
    assert rc == 0
    assert captured["out_dir"] == t6.DEFAULT_OUT_DIR
    assert captured["n_star"] == 18
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_tier6_dsr.py -k "main and n_star" -v`
  `Expected: FAIL — argparse: unrecognized arguments: --n-star (SystemExit); and test_main_rejects_non_default_n_star_without_out_dir fails because no guard exists yet.`

- [ ] **Step 3: Implement** — edit `main()` in `backtest/tier6_dsr.py`. Add the `--n-star` argument after the `--dry-run` argument (after :996):

```python
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Compute the cohort but write NO artifacts.",
    )
    parser.add_argument(
        "--n-star", type=int, default=N_STAR,
        help=(
            "Effective number of independent trials (multiplicity N*) for the "
            f"DSR benchmark (default: {N_STAR}, the sealed Tier 6 value). A "
            "non-default value REQUIRES an explicit --out-dir (or --dry-run) so "
            "the sealed data/phase2c_evaluation_gate/tier6_dsr_v1 artifacts are "
            "never overwritten."
        ),
    )
    args = parser.parse_args(argv)

    _configure_logging()

    holdout_dir = EVALUATION_GATE_DIR / args.cohort
    out_dir = Path(args.out_dir) if args.out_dir is not None else DEFAULT_OUT_DIR
    write = not args.dry_run

    # HARD SAFETY GUARD (Task 21): a non-default n_star with no explicit
    # --out-dir and no --dry-run would default to DEFAULT_OUT_DIR — the SEALED
    # tier6_dsr_v1 directory — and overwrite it with non-sealed-multiplicity
    # artifacts. The sealed cohort is N*=18 (R6.1-locked); refuse to clobber it.
    # Fires BEFORE evaluate_cohort so not a single artifact byte is touched.
    if args.n_star != N_STAR and args.out_dir is None and not args.dry_run:
        logger.error(
            "REFUSING: --n-star=%d (!= sealed N_STAR=%d) with no --out-dir and "
            "not --dry-run would overwrite the SEALED %s artifacts. Re-run with "
            "an explicit --out-dir pointing at a NON-sealed directory (or "
            "--dry-run).",
            args.n_star, N_STAR, DEFAULT_OUT_DIR,
        )
        return 1

    logger.info(
        "tier6_dsr start: cohort=%s holdout_dir=%s out_dir=%s n_sims=%d "
        "n_star=%d dry_run=%s",
        args.cohort, holdout_dir, out_dir, args.n_sims, args.n_star, args.dry_run,
    )

    try:
        result = evaluate_cohort(
            out_dir=out_dir,
            n_sims=args.n_sims,
            write=write,
            holdout_dir=holdout_dir,
            n_star=args.n_star,
        )
    except (ValueError, OSError) as exc:
        logger.error("tier6_dsr FAILED (validation/lineage/cost-anchor): %s", exc)
        return 1
```

(The original `args = parser.parse_args(argv)` / `_configure_logging()` / `holdout_dir` / `out_dir` / `write` / `logger.info(...)` / `try:` block at :997-:1016 is replaced by the block above; the post-`try` summary logging at :1021-:1033 is unchanged.)

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_tier6_dsr.py -k "main" -v`
  `Expected: PASS — all five Task 21 tests green; pre-existing main() tests (test_main_dry_run_writes_nothing_and_returns_zero, test_main_non_dry_run_writes_to_tmp_out_dir, test_main_returns_nonzero_on_validation_failure, test_main_cohort_arg_resolves_non_default_dir) still pass (default n_star path unchanged, including the new n_star=%d log field).`

- [ ] **Step 5: Commit** (execution waits for Charlie authorization)
  `git add backtest/tier6_dsr.py tests/test_tier6_dsr.py && git commit -m "feat(tier6-dsr): add --n-star CLI flag + hard guard against overwriting sealed tier6_dsr_v1"`

---

### Task 22: Sealed-artifact byte-regression — `n_star=18` reproduces `tier6_dsr_v1/` byte-identical

**Files:**
- Test: `tests/test_tier6_dsr.py` (new regression test only; no production change)

The HARD CONSTRAINT requires `data/phase2c_evaluation_gate/tier6_dsr_v1/` to stay byte-untouched. After Tasks 19-21 (which add an `n_star` parameter defaulting to `N_STAR=18`), a default-path re-run into a tmp dir MUST reproduce the three deterministic sealed artifacts byte-for-byte: `tier6_dsr_results.csv`, `tier6_dsr_companion.csv`, and `tier6_promotion_list.json`. (`tier6_mc_validation.json` depends on `n_sims`/`seed` — the sealed file used the default `n_sims=100000` + `seed`; we reproduce it with the matching `n_sims` to confirm the MC plumbing is also unperturbed.) This is the regression proving the `n_star` plumbing did not perturb the sealed numeric output. The test reads the sealed files (read-only) and compares bytes against a fresh tmp-dir run; it never writes into the sealed directory.

- [ ] **Step 1: Write the failing test** — add to `tests/test_tier6_dsr.py`:

```python
# --- Task 22: sealed-artifact byte-regression (n_star=18 reproduces v1) ---
SEALED_V1_DIR = t6.PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1"


def test_default_n_star_reproduces_sealed_deterministic_artifacts_byte_identical(tmp_path):
    # Task 22: a default-path (n_star=N_STAR=18) re-run must reproduce the three
    # DETERMINISTIC sealed artifacts byte-for-byte. Writes ONLY into tmp_path;
    # the sealed dir is read-only here. Proves the n_star plumbing (Tasks 19-21)
    # did not perturb the sealed numeric output.
    if not SEALED_V1_DIR.exists():
        pytest.skip("sealed tier6_dsr_v1 dir not present in this checkout")

    # MC json depends on (n_sims, seed); reproduce with the sealed default
    # n_sims so all four files match. n_star omitted -> defaults to N_STAR=18.
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=100_000)

    deterministic = (
        "tier6_dsr_results.csv",
        "tier6_dsr_companion.csv",
        "tier6_promotion_list.json",
    )
    for fn in deterministic:
        sealed_bytes = (SEALED_V1_DIR / fn).read_bytes()
        fresh_bytes = (tmp_path / fn).read_bytes()
        assert fresh_bytes == sealed_bytes, (
            f"{fn} differs from sealed tier6_dsr_v1 — the n_star plumbing "
            f"perturbed deterministic output"
        )


def test_default_n_star_reproduces_sealed_mc_validation(tmp_path):
    # Task 22: the seeded MC json (default n_sims=100000, default seed) is also
    # reproduced byte-identical under the default n_star path.
    if not (SEALED_V1_DIR / "tier6_mc_validation.json").exists():
        pytest.skip("sealed tier6_mc_validation.json not present")
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=100_000)
    sealed = (SEALED_V1_DIR / "tier6_mc_validation.json").read_bytes()
    fresh = (tmp_path / "tier6_mc_validation.json").read_bytes()
    assert fresh == sealed, (
        "tier6_mc_validation.json differs — the n_star plumbing perturbed the "
        "seeded Monte-Carlo expected-max output"
    )


def test_sealed_v1_dir_is_not_written_by_default_run(tmp_path):
    # Task 22 (safety): a fresh run targeting tmp_path must NOT mutate the
    # sealed dir. Snapshot sealed mtimes before/after; assert unchanged.
    if not SEALED_V1_DIR.exists():
        pytest.skip("sealed tier6_dsr_v1 dir not present in this checkout")
    before = {p.name: p.stat().st_mtime_ns for p in SEALED_V1_DIR.iterdir()}
    t6.evaluate_cohort(out_dir=tmp_path, n_sims=0)
    after = {p.name: p.stat().st_mtime_ns for p in SEALED_V1_DIR.iterdir()}
    assert before == after, "sealed tier6_dsr_v1 dir was mutated by a tmp-dir run"
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_tier6_dsr.py -k "sealed" -v`
  `Expected: FAIL when run on a tree WITHOUT Tasks 19-21 applied (TypeError on n_star kwarg in earlier helper edits is absent, so the call signature is fine, but the test is authored against the post-plumbing module). The load-bearing RED is: if any n_star plumbing edit accidentally changed a default-path value (e.g. wrote n_star into a field that was previously absent, or reordered JSON keys), the byte-comparison FAILS, surfacing the perturbation. On a correctly-plumbed tree it PASSES.`

  Note: this is a regression guard whose failure mode is a real defect signal, not a scaffolding RED. If it fails, the Task 19-21 plumbing perturbed deterministic output and must be corrected (the plumbing is required to be byte-invariant at `n_star=18`).

- [ ] **Step 3: Implement** — No production change. This task is pure regression coverage: the byte-invariance is a property that Tasks 19-21 must already satisfy (default `n_star=N_STAR`, no new keys in the default-path row dicts, JSON key order preserved). If Step 2 surfaces a byte difference, the fix belongs in whichever Task-19/20/21 edit introduced the perturbation (e.g. an accidental field reorder or an added column), not here.

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_tier6_dsr.py -k "sealed" -v`
  `Expected: PASS — all three sealed-regression tests green; the three deterministic artifacts + the seeded MC json reproduce byte-identical, and the sealed dir mtimes are unchanged.`
  Then run the full module to confirm no regression: `Run: pytest tests/test_tier6_dsr.py -q` / `Expected: PASS (all green).`

- [ ] **Step 5: Commit** (execution waits for Charlie authorization)
  `git add tests/test_tier6_dsr.py && git commit -m "test(tier6-dsr): byte-regression — n_star=18 default reproduces sealed tier6_dsr_v1 artifacts"`

---

## Section E — Step 0 + Evaluation Harness (Steps 0, 3, 4, 5)

I have all the verified facts needed. Writing Section E (tasks 23-30).

---

### Task 23: Step-0 read-only diagnostic re-score (Path B namespace, guarded, side-effect-free)

**Files:** Create: `scripts/pathb_step0_diagnostic.py` · Test: `tests/test_pathb_step0_diagnostic.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathb_step0_diagnostic.py
"""Step 0 read-only diagnostic re-score: Path B namespace, guarded, no side effects."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

import scripts.pathb_step0_diagnostic as step0
import backtest.tier6_dsr as t6

COHORT = "phase4_forward_2026_15bps_v1"


def _dir_mtimes(d: Path) -> dict[str, float]:
    return {str(p): p.stat().st_mtime_ns for p in sorted(d.rglob("*")) if p.is_file()}


def test_default_output_is_pathb_namespace_not_cohort_dir():
    # The Path B re-score namespace must NOT be the sealed cohort dir.
    assert step0.DEFAULT_PATHB_STEP0_DIR.name == "pathb_step0_diagnostic_v1"
    assert step0.DEFAULT_PATHB_STEP0_DIR != t6.HOLDOUT_DIR
    assert t6.DEFAULT_COHORT not in step0.DEFAULT_PATHB_STEP0_DIR.parts


def test_run_step0_is_read_only_and_calls_both_guards(tmp_path, monkeypatch):
    calls = {"eval_guard": 0, "cost_anchor": 0, "wf_guard": 0}

    def fake_eval_guard(summary, *, artifact_path=None):
        calls["eval_guard"] += 1

    def fake_wf_guard(summary, *, artifact_path=None):  # must NOT be used
        calls["wf_guard"] += 1

    def fake_cost(summary_dict):
        calls["cost_anchor"] += 1

    # A minimal cohort fixture (single candidate) wired through tier6 internals.
    cohort_dir = tmp_path / "cohort"
    cohort_dir.mkdir()
    (cohort_dir / "holdout_summary.json").write_text(json.dumps({"ok": True}))
    df = pd.DataFrame([{"hypothesis_hash": "abc", "name": "h", "theme": "t"}])

    monkeypatch.setattr(step0, "check_evaluation_semantics_or_raise", fake_eval_guard)
    monkeypatch.setattr(step0, "check_wf_semantics_or_raise", fake_wf_guard)
    monkeypatch.setattr(step0, "_assert_cost_anchor_15bps_spot", fake_cost)
    monkeypatch.setattr(step0, "_read_cohort_csv", lambda holdout_dir=None: df)

    def fake_eval_one(h, frame, n_star, holdout_dir):
        return {"hypothesis_hash": h, "pass_B": False, "dsr_statistic_B": -1.0}

    monkeypatch.setattr(step0, "_evaluate_one", fake_eval_one)

    before = _dir_mtimes(cohort_dir)
    result = step0.run_step0(
        cohort_dir=cohort_dir,
        out_dir=tmp_path / "out",
        n_star=step0.PATHB_N_STAR,
        write=True,
    )
    after = _dir_mtimes(cohort_dir)

    # Forward-holdout single-run guard (NOT the WF guard) fired exactly once.
    assert calls["eval_guard"] == 1
    assert calls["wf_guard"] == 0
    assert calls["cost_anchor"] == 1
    # Read-only: cohort dir bytes + mtimes unchanged; no promotion side effect.
    assert before == after
    assert result["promotion_side_effect"] is False
    assert result["read_only"] is True


def test_pathb_n_star_default_is_18():
    assert step0.PATHB_N_STAR == 18
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_pathb_step0_diagnostic.py -v` / `Expected: FAIL (ModuleNotFoundError: scripts.pathb_step0_diagnostic)`

- [ ] **Step 3: Implement**

```python
# scripts/pathb_step0_diagnostic.py
"""Path B Step 0: read-only re-score of the locked cohort under the Path B N*.

Read-only by construction. It consumes the sealed cohort dir
(``phase4_forward_2026_15bps_v1``) WITHOUT writing to it, runs the
forward-holdout single-run lineage guard
(``check_evaluation_semantics_or_raise`` — NOT the walk-forward guard) and
the 15bps cost-anchor preflight (``_assert_cost_anchor_15bps_spot``) on the
aggregate ``holdout_summary.json`` before any consumption, and writes its
diagnostic re-score into a SEPARATE Path B namespace dir
(``pathb_step0_diagnostic_v1``), never the cohort dir.

N* is Step -1 human-locked (PATHB_N_STAR); referenced symbolically here.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from backtest.tier6_dsr import (
    HOLDOUT_DIR,
    PROJECT_ROOT,
    _assert_cost_anchor_15bps_spot,
    _evaluate_one,
    _read_cohort_csv,
)
from backtest.wf_lineage import (
    check_evaluation_semantics_or_raise,
    check_wf_semantics_or_raise,  # imported so a regression that swaps guards is visible
)

logger = logging.getLogger("pathb_step0")

# Step -1 human-locked multiplicity for the Path B re-score (default 18).
PATHB_N_STAR = 18

# Path B namespace — physically isolated from the sealed cohort dir.
DEFAULT_PATHB_STEP0_DIR = (
    PROJECT_ROOT / "data/phase2c_evaluation_gate/pathb_step0_diagnostic_v1"
)


def run_step0(
    cohort_dir: Path = HOLDOUT_DIR,
    out_dir: Path = DEFAULT_PATHB_STEP0_DIR,
    n_star: int = PATHB_N_STAR,
    write: bool = True,
) -> dict:
    """Re-score the cohort read-only; emit a diagnostic into the Path B namespace.

    Args:
        cohort_dir: Sealed cohort directory (READ ONLY; never written).
        out_dir: Path B namespace output dir (default DEFAULT_PATHB_STEP0_DIR).
        n_star: Step -1 locked multiplicity (default PATHB_N_STAR).
        write: When True, write the diagnostic CSV/JSON into out_dir.

    Returns:
        A dict with ``rows``, ``n_star``, ``read_only=True`` and
        ``promotion_side_effect=False`` (this script NEVER promotes).

    Raises:
        ValueError: On a forward-holdout single-run lineage-guard failure or a
            non-15bps-spot cost anchor (both fire before any cohort read).
    """
    summary_path = cohort_dir / "holdout_summary.json"
    summary_dict = json.loads(summary_path.read_text())
    # Forward holdout is a SINGLE-RUN evaluation -> evaluation-semantics guard
    # (single_run_holdout_v1), NOT the walk-forward guard. Fires before consume.
    check_evaluation_semantics_or_raise(summary_dict, artifact_path=str(summary_path))
    _assert_cost_anchor_15bps_spot(summary_dict)

    df = _read_cohort_csv(holdout_dir=cohort_dir)
    rows = [
        _evaluate_one(h, df, n_star=n_star, holdout_dir=cohort_dir)
        for h in df["hypothesis_hash"].tolist()
    ]

    if write:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "pathb_step0_rescore.json").write_text(
            json.dumps(
                {
                    "n_star": n_star,
                    "cohort_dir": str(cohort_dir),
                    "read_only": True,
                    "rows": rows,
                },
                indent=2,
                default=str,
            )
        )

    return {
        "rows": rows,
        "n_star": n_star,
        "read_only": True,
        "promotion_side_effect": False,
    }


def _configure_logging() -> None:
    if logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        "%(asctime)s.%(msecs)03dZ %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    fmt.converter = time.gmtime
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.pathb_step0_diagnostic")
    parser.add_argument("--cohort-dir", default=str(HOLDOUT_DIR))
    parser.add_argument("--out-dir", default=str(DEFAULT_PATHB_STEP0_DIR))
    parser.add_argument("--n-star", type=int, default=PATHB_N_STAR)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    _configure_logging()
    try:
        res = run_step0(
            cohort_dir=Path(args.cohort_dir),
            out_dir=Path(args.out_dir),
            n_star=args.n_star,
            write=not args.dry_run,
        )
    except (ValueError, OSError) as exc:
        logger.error("pathb_step0 FAILED: %s", exc)
        return 1
    logger.info(
        "pathb_step0 done: rows=%d n_star=%d read_only=%s",
        len(res["rows"]), res["n_star"], res["read_only"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_pathb_step0_diagnostic.py -v` / `Expected: PASS (4 passed)`

- [ ] **Step 5: Commit** — `git add scripts/pathb_step0_diagnostic.py tests/test_pathb_step0_diagnostic.py && git commit -m "feat(pathb): Task 23 — Step-0 read-only re-score in Path B namespace with eval-semantics + 15bps guards"`

---

### Task 24: Cost-equivalence assertion — Phase4 vs Tier-5 spot anchor net-return parity

**Files:** Create: `scripts/pathb_cost_equivalence.py` · Test: `tests/test_pathb_cost_equivalence.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathb_cost_equivalence.py
"""Path B cohort net-return config must equal the Tier-5 15bps spot anchor."""
from __future__ import annotations

import pytest

import scripts.pathb_cost_equivalence as ce


def test_phase4_and_phaseb_anchors_have_identical_fee_and_slippage():
    res = ce.assert_cost_equivalence()
    assert res["fee_bps"] == res["anchor_fee_bps"]
    assert res["slippage_bps"] == res["anchor_slippage_bps"]
    assert res["per_side_bps"] == pytest.approx(15.0, abs=1e-9)
    assert res["equivalent"] is True


def test_mismatched_fee_raises(monkeypatch):
    real = ce._load_cost_model

    def fake(path):
        cm = dict(real(path))
        if path.name == "execution_phase4_15bps.yaml":
            cm["default_fee_bps"] = cm["default_fee_bps"] + 1.0  # break parity
        return cm

    monkeypatch.setattr(ce, "_load_cost_model", fake)
    with pytest.raises(ValueError, match="cost-equivalence"):
        ce.assert_cost_equivalence()
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_pathb_cost_equivalence.py -v` / `Expected: FAIL (ModuleNotFoundError: scripts.pathb_cost_equivalence)`

- [ ] **Step 3: Implement**

```python
# scripts/pathb_cost_equivalence.py
"""Assert the cohort's net-return config equals the Tier-5 15bps spot anchor.

CLAUDE.md Conservative-Anchor Gate: the cohort was scored under
config/execution_phase4_15bps.yaml; the Tier-5 anchor is
config/execution_phaseb_spot_15bps.yaml. The two are documented as
functionally identical bodies (differ only by header + cost_model.name + SHA).
This guard parses both cost_model blocks and asserts identical fee + slippage,
reusing tier6_dsr's per-side cost helper so the bps arithmetic is single-source.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from backtest.tier6_dsr import PROJECT_ROOT, _per_side_cost_bps

PHASE4_CFG = PROJECT_ROOT / "config/execution_phase4_15bps.yaml"
ANCHOR_CFG = PROJECT_ROOT / "config/execution_phaseb_spot_15bps.yaml"


def _load_cost_model(path: Path) -> dict:
    """Parse and return the ``cost_model`` block of an execution YAML.

    Args:
        path: Execution config path.

    Returns:
        The ``cost_model`` dict.

    Raises:
        ValueError: If the file lacks a ``cost_model`` block.
    """
    cfg = yaml.safe_load(path.read_text()) or {}
    cm = cfg.get("cost_model")
    if not isinstance(cm, dict):
        raise ValueError(f"cost-equivalence: {path} has no cost_model block")
    return cm


def assert_cost_equivalence() -> dict:
    """Assert Phase4 cohort config fee/slippage equals the Tier-5 spot anchor.

    Returns:
        A dict echoing both configs' fee/slippage, the shared per-side bps, and
        ``equivalent=True`` on success.

    Raises:
        ValueError: If fee or slippage differ between the two configs.
    """
    phase4 = _load_cost_model(PHASE4_CFG)
    anchor = _load_cost_model(ANCHOR_CFG)

    fee = float(phase4.get("default_fee_bps", 0.0))
    slip = float(phase4.get("slippage_bps", 0.0))
    a_fee = float(anchor.get("default_fee_bps", 0.0))
    a_slip = float(anchor.get("slippage_bps", 0.0))

    if fee != a_fee or slip != a_slip:
        raise ValueError(
            f"cost-equivalence FAILED: phase4 fee/slip=({fee},{slip}) != "
            f"anchor fee/slip=({a_fee},{a_slip}); the cohort net-return config "
            f"must equal the Tier-5 15bps spot anchor."
        )
    return {
        "fee_bps": fee,
        "slippage_bps": slip,
        "anchor_fee_bps": a_fee,
        "anchor_slippage_bps": a_slip,
        "per_side_bps": _per_side_cost_bps(phase4),
        "equivalent": True,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(assert_cost_equivalence(), indent=2))
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_pathb_cost_equivalence.py -v` / `Expected: PASS (2 passed)`

- [ ] **Step 5: Commit** — `git add scripts/pathb_cost_equivalence.py tests/test_pathb_cost_equivalence.py && git commit -m "feat(pathb): Task 24 — assert cohort net-return config equals Tier-5 15bps spot anchor"`

---

### Task 25: Train-only mechanism sanity table (train_windows list, 2022 excluded, no validation/test touch)

**Files:** Create: `backtest/pathb_train_sanity.py` · Test: `tests/test_pathb_train_sanity.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathb_train_sanity.py
"""Train-only mechanism sanity: parse train_windows list; reject 2022/2024/2025."""
from __future__ import annotations

import pandas as pd
import pytest

import backtest.pathb_train_sanity as ts


def test_train_windows_parsed_as_list_of_timestamp_pairs():
    windows = ts.load_train_windows()
    assert len(windows) == 2
    lo0, hi0 = windows[0]
    assert lo0 == pd.Timestamp("2020-01-01")
    assert hi0 == pd.Timestamp("2021-12-31")
    lo1, hi1 = windows[1]
    assert lo1 == pd.Timestamp("2023-01-01")
    assert hi1 == pd.Timestamp("2023-12-31")


def test_timestamp_inside_allowed_window():
    windows = ts.load_train_windows()
    assert ts.in_train_window(pd.Timestamp("2020-06-15"), windows) is True
    assert ts.in_train_window(pd.Timestamp("2023-07-01"), windows) is True


@pytest.mark.parametrize("forbidden", ["2022-06-01", "2024-03-01", "2025-09-01"])
def test_2022_validation_test_excluded(forbidden):
    windows = ts.load_train_windows()
    assert ts.in_train_window(pd.Timestamp(forbidden), windows) is False


def test_require_train_only_raises_on_out_of_window_timestamps():
    windows = ts.load_train_windows()
    df = pd.DataFrame({"open_time_utc": pd.to_datetime(
        ["2020-02-01", "2022-02-01"], utc=False)})
    with pytest.raises(ValueError, match="outside train_windows"):
        ts.require_train_only(df["open_time_utc"], windows)


def test_tz_aware_timestamps_handled():
    # Real raw data is tz-aware UTC; membership must work without raising.
    windows = ts.load_train_windows()
    assert ts.in_train_window(pd.Timestamp("2020-06-15", tz="UTC"), windows) is True
    assert ts.in_train_window(pd.Timestamp("2022-06-15", tz="UTC"), windows) is False


def test_sanity_table_has_no_validation_or_test_rows():
    windows = ts.load_train_windows()
    df = pd.DataFrame({
        "open_time_utc": pd.to_datetime(
            ["2020-02-01", "2021-05-01", "2023-08-01"], utc=False),
        "fwd_ret_sign": [1, -1, 1],
    })
    table = ts.build_sanity_table(df, windows)
    assert table["n_train_rows"] == 3
    assert table["touched_validation_or_test"] is False
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_pathb_train_sanity.py -v` / `Expected: FAIL (ModuleNotFoundError: backtest.pathb_train_sanity)`

- [ ] **Step 3: Implement**

```python
# backtest/pathb_train_sanity.py
"""Train-only mechanism sanity table.

Parses config/environments.yaml splits.train_windows (a LIST of [start,end]
pairs; 2022 is DELIBERATELY EXCLUDED) and requires every timestamp used in a
sanity computation to fall inside an allowed window. There is NO splits.v2 key
and NO single train_start/train_end — train_windows is the disjoint-range list.

Hard rule: this module NEVER reads validation (2024) or test (2025) data.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / "config/environments.yaml"

TrainWindow = tuple[pd.Timestamp, pd.Timestamp]


def load_train_windows(env_path: Path = ENV_PATH) -> list[TrainWindow]:
    """Load splits.train_windows as a list of (start, end) Timestamp pairs.

    Args:
        env_path: Path to environments.yaml.

    Returns:
        A list of (pd.Timestamp(start), pd.Timestamp(end)) pairs. 2022 is not
        present in any window (it is the regime holdout, held out from train).

    Raises:
        ValueError: If splits.train_windows is missing or not a non-empty list.
    """
    cfg = yaml.safe_load(env_path.read_text()) or {}
    raw = (cfg.get("splits") or {}).get("train_windows")
    if not isinstance(raw, list) or not raw:
        raise ValueError("splits.train_windows missing or not a non-empty list")
    return [(pd.Timestamp(w[0]), pd.Timestamp(w[1])) for w in raw]


def in_train_window(ts: pd.Timestamp, windows: list[TrainWindow]) -> bool:
    """Return True iff ``ts`` falls inside any allowed (inclusive) train window.

    Real raw data is timezone-aware UTC (``build_features.py`` enforces this),
    while the date-only ``train_windows`` bounds are naive. We strip the tz to
    compare on naive UTC wall-time, so a tz-aware bar and a naive window bound
    compare cleanly instead of raising ``TypeError`` on aware-vs-naive.

    Args:
        ts: A timestamp (tz-aware or naive).
        windows: Output of :func:`load_train_windows`.

    Returns:
        True iff ``lo <= ts <= hi`` for some window (lo, hi).
    """
    t = pd.Timestamp(ts)
    if t.tzinfo is not None:
        t = t.tz_localize(None)
    return any(lo <= t <= hi for lo, hi in windows)


def require_train_only(times: pd.Series, windows: list[TrainWindow]) -> None:
    """Raise if ANY timestamp is outside the allowed train windows.

    Args:
        times: A Series of timestamps.
        windows: Output of :func:`load_train_windows`.

    Raises:
        ValueError: If any timestamp falls outside train_windows (e.g. a 2022,
            2024, or 2025 bar leaked into a train-only mechanism table).
    """
    bad = [t for t in pd.to_datetime(times) if not in_train_window(pd.Timestamp(t), windows)]
    if bad:
        raise ValueError(
            f"{len(bad)} timestamp(s) outside train_windows (first={bad[0]}); "
            f"train-only sanity must NEVER touch 2022/validation/test"
        )


def build_sanity_table(df: pd.DataFrame, windows: list[TrainWindow]) -> dict:
    """Build a train-only mechanism sanity table; assert no out-of-window rows.

    Args:
        df: A frame carrying an ``open_time_utc`` column (train rows only).
        windows: Output of :func:`load_train_windows`.

    Returns:
        A dict with ``n_train_rows`` and ``touched_validation_or_test=False``.

    Raises:
        ValueError: If any row is outside train_windows (via require_train_only).
    """
    require_train_only(df["open_time_utc"], windows)
    return {
        "n_train_rows": int(len(df)),
        "touched_validation_or_test": False,
    }
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_pathb_train_sanity.py -v` / `Expected: PASS (8 passed)`

- [ ] **Step 5: Commit** — `git add backtest/pathb_train_sanity.py tests/test_pathb_train_sanity.py && git commit -m "feat(pathb): Task 25 — train-only mechanism sanity over train_windows list (2022 excluded)"`

---

### Task 26: H2 per-leg `mechanism_sane` producer (feeds spec C8 per-leg kill)

**Files:** Create: `backtest/pathb_perleg_mechanism.py` · Test: `tests/test_pathb_perleg_mechanism.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathb_perleg_mechanism.py
"""H2 per-leg mechanism_sane producer + H1/H3 signs (feeds C8 per-leg kill)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import backtest.pathb_perleg_mechanism as pm


def _train_frame() -> pd.DataFrame:
    n = 400
    rng = np.random.default_rng(7)
    return pd.DataFrame({
        "open_time_utc": pd.date_range("2020-01-01", periods=n, freq="h"),
        "zscore_48": rng.normal(0, 1, n),
        "realized_vol_24h": np.abs(rng.normal(0.02, 0.01, n)),
        "fwd_ret": rng.normal(0, 0.01, n),
        "intrabar_push": rng.normal(0, 0.3, n),     # H1 driver
        "volume_zscore_24h": rng.normal(0, 1, n),   # H3 driver
    })


def test_per_leg_booleans_present_and_independent():
    out = pm.compute_per_leg_mechanism(_train_frame())
    # H2 split into two independently-killable legs (spec C8).
    assert set(["h2_low_leg_sane", "h2_high_leg_sane"]).issubset(out)
    assert isinstance(out["h2_low_leg_sane"], bool)
    assert isinstance(out["h2_high_leg_sane"], bool)
    # H1 / H3 signs also produced.
    assert "h1_sane" in out and "h3_sane" in out


def test_low_leg_uses_zscore_below_neg1_and_low_vol_only():
    df = _train_frame()
    out = pm.compute_per_leg_mechanism(df)
    vol_med = df["realized_vol_24h"].median()
    low_mask = (df["zscore_48"] < pm.THETA_Z_LOW) & (df["realized_vol_24h"] <= vol_med)
    high_mask = (df["zscore_48"] > pm.THETA_Z_HIGH) & (df["realized_vol_24h"] > vol_med)
    # No overlap between leg masks (disjoint conditional populations).
    assert not (low_mask & high_mask).any()
    # The reported low-leg sign equals the sign of mean fwd_ret over the low mask.
    expected = bool(df.loc[low_mask, "fwd_ret"].mean() > 0)
    assert out["h2_low_leg_sane_raw_positive"] == expected


def test_high_leg_sane_requires_positive_continuation():
    # H2 HIGH is a TREND (sign-flip) leg: long when z>+1 in high-vol, so it is
    # sane iff the conditional mean forward return is POSITIVE (continuation UP).
    # This regression guards against the v2 sign-inversion bug.
    df = _train_frame()
    out = pm.compute_per_leg_mechanism(df)
    vol_med = df["realized_vol_24h"].median()
    high_mask = (df["zscore_48"] > pm.THETA_Z_HIGH) & (df["realized_vol_24h"] > vol_med)
    expected = bool(high_mask.any() and df.loc[high_mask, "fwd_ret"].mean() > 0)
    assert out["h2_high_leg_sane"] == expected


def test_h1_fades_down_push_expects_reversion_not_continuation():
    # Spec §3 H1: H1 FADES a one-sided down-push (long), sane iff reversion UP
    # (positive fwd ret on the intrabar_push < THETA_PUSH population). NOT
    # continuation. Regression against the H1 direction-inversion bug.
    df = _train_frame()
    out = pm.compute_per_leg_mechanism(df)
    h1_mask = df["intrabar_push"] < pm.THETA_PUSH
    expected = bool(h1_mask.any() and df.loc[h1_mask, "fwd_ret"].mean() > 0)
    assert out["h1_sane"] == expected


def test_empty_leg_population_is_not_sane():
    df = _train_frame()
    df["zscore_48"] = 0.0  # no bar satisfies < -1 or > +1
    out = pm.compute_per_leg_mechanism(df)
    assert out["h2_low_leg_sane"] is False
    assert out["h2_high_leg_sane"] is False
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_pathb_perleg_mechanism.py -v` / `Expected: FAIL (ModuleNotFoundError: backtest.pathb_perleg_mechanism)`

- [ ] **Step 3: Implement**

```python
# backtest/pathb_perleg_mechanism.py
"""H2 per-leg mechanism_sane producer + H1/H3 conditional forward-return signs.

H2 is a two-sided mean-reversion hypothesis whose LOW and HIGH legs have
distinct mechanisms (oversold-in-calm vs overbought-in-stress). They must be
killable INDEPENDENTLY (spec C8 per-leg kill), so this producer computes the
conditional forward-return sign for each leg SEPARATELY on the train artifact:

  LOW  leg: zscore_48 < THETA_Z_LOW (-1) AND low-vol regime  -> mean-revert: expect UP (positive fwd ret)
  HIGH leg: zscore_48 > THETA_Z_HIGH (+1) AND high-vol regime -> TREND sign-flip: expect continuation UP (positive fwd ret)

H1/H3 are single-leg and produce one sign each. Threshold values (THETA_Z_*) are
Step -1 human-locked and referenced symbolically here.

Train-only: callers pass a train-windows frame (Task 25 guards the window).
"""
from __future__ import annotations

import pandas as pd

# Step -1 human-locked hypothesis param values (symbolic; locked in Step -1).
THETA_Z_LOW = -1.0
THETA_Z_HIGH = 1.0
THETA_PUSH = -0.6   # H1 FADES a one-sided DOWN-push -> negative threshold


def _leg_mean_sign(df: pd.DataFrame, mask: pd.Series, fwd_col: str) -> tuple[bool, bool]:
    """Return (population_nonempty, mean_fwd_ret_positive) for a conditional leg.

    Args:
        df: The train frame.
        mask: Boolean Series selecting the conditional leg population.
        fwd_col: Forward-return column name.

    Returns:
        (nonempty, positive): ``nonempty`` is True iff the leg has >= 1 bar;
        ``positive`` is True iff the leg's mean forward return is > 0 (False on
        an empty population).
    """
    sub = df.loc[mask, fwd_col]
    if sub.empty:
        return False, False
    return True, bool(sub.mean() > 0)


def compute_per_leg_mechanism(
    df: pd.DataFrame, fwd_col: str = "fwd_ret"
) -> dict:
    """Compute per-leg + per-hypothesis mechanism-sanity booleans on the train data.

    Args:
        df: Train artifact frame with columns ``zscore_48``,
            ``realized_vol_24h``, ``intrabar_push``, ``volume_zscore_24h`` and
            ``fwd_col``.
        fwd_col: Forward-return column (default ``"fwd_ret"``).

    Returns:
        A dict of booleans:
          - ``h2_low_leg_sane`` / ``h2_high_leg_sane``: leg has population AND
            its conditional mean forward return is POSITIVE (low leg = revert
            UP; high leg = trend-continuation UP — both sane iff fwd ret > 0,
            per spec §3 H2 kill (a)/(b)).
          - ``h2_low_leg_sane_raw_positive`` / ``h2_high_leg_sane_raw_positive``:
            the unadjusted "mean fwd ret > 0" flags (diagnostic).
          - ``h1_sane``: H1 FADES a down-push (intrabar_push < THETA_PUSH); sane
            iff the conditional mean forward return is POSITIVE (reversion UP).
          - ``h3_sane``: H3 trend (volume_zscore>0 expects continuation UP).
    """
    vol_med = df["realized_vol_24h"].median()

    low_mask = (df["zscore_48"] < THETA_Z_LOW) & (df["realized_vol_24h"] <= vol_med)
    high_mask = (df["zscore_48"] > THETA_Z_HIGH) & (df["realized_vol_24h"] > vol_med)

    low_nonempty, low_pos = _leg_mean_sign(df, low_mask, fwd_col)
    high_nonempty, high_pos = _leg_mean_sign(df, high_mask, fwd_col)

    # H2 LOW = mean-reversion (long when z<-1 in low-vol; expect UP, positive).
    # H2 HIGH = TREND sign-flip (long when z>+1 in high-vol; expect continuation
    # UP, positive). Per spec §3 H2 kill (a)/(b), EACH leg is sane iff its
    # conditional mean forward return is > 0 (a wrong-signed leg cannot pass).
    h2_low_sane = bool(low_nonempty and low_pos)
    h2_high_sane = bool(high_nonempty and high_pos)

    # H1: FADE a one-sided down-push (microstructure mean-reversion, spec §3 H1)
    # — long when intrabar_push < THETA_PUSH; sane iff the conditional mean
    # forward return is POSITIVE (reversion UP). NOT continuation (spec §3 H1's
    # kill clause explicitly forbids flipping H1 to momentum).
    h1_mask = df["intrabar_push"] < THETA_PUSH
    h1_nonempty, h1_pos = _leg_mean_sign(df, h1_mask, fwd_col)
    h1_sane = bool(h1_nonempty and h1_pos)

    # H3: volume_zscore>0 (volume surge) expects continuation UP.
    h3_mask = df["volume_zscore_24h"] > 0
    h3_nonempty, h3_pos = _leg_mean_sign(df, h3_mask, fwd_col)
    h3_sane = bool(h3_nonempty and h3_pos)

    return {
        "h2_low_leg_sane": h2_low_sane,
        "h2_high_leg_sane": h2_high_sane,
        "h2_low_leg_sane_raw_positive": low_pos,
        "h2_high_leg_sane_raw_positive": high_pos,
        "h2_low_leg_population": int(low_mask.sum()),
        "h2_high_leg_population": int(high_mask.sum()),
        "h1_sane": h1_sane,
        "h3_sane": h3_sane,
    }
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_pathb_perleg_mechanism.py -v` / `Expected: PASS (5 passed)`

- [ ] **Step 5: Commit** — `git add backtest/pathb_perleg_mechanism.py tests/test_pathb_perleg_mechanism.py && git commit -m "feat(pathb): Task 26 — H2 per-leg mechanism_sane producer feeding spec C8 per-leg kill"`

---

### Task 27: `build_hypothesis_dsl` + EVAL_GAUNTLET (correct DSL/compiler API, both wf_lineage guards, Path B namespace)

**Files:** Create: `backtest/pathb_eval_gauntlet.py` · Test: `tests/test_pathb_eval_gauntlet.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathb_eval_gauntlet.py
"""build_hypothesis_dsl + EVAL_GAUNTLET stage->guard routing + Path B namespace."""
from __future__ import annotations

import pytest

import backtest.pathb_eval_gauntlet as eg
from strategies.dsl import StrategyDSL
from strategies.dsl_compiler import compile_dsl_to_strategy


def test_build_hypothesis_dsl_uses_value_and_description_and_compiles():
    dsl = eg.build_hypothesis_dsl()
    assert isinstance(dsl, StrategyDSL)
    assert len(dsl.description) >= 1            # description is REQUIRED
    cond = dsl.entry[0].conditions[0]
    assert hasattr(cond, "value")              # Condition uses value=, not threshold
    # The DSL must actually compile via the REAL compiler API.
    cls = compile_dsl_to_strategy(dsl, write_manifest=False)
    assert isinstance(cls, type)


def test_eval_gauntlet_routes_train_wf_to_wf_guard_and_rest_to_eval_guard():
    routing = eg.EVAL_GAUNTLET
    assert routing["train_wf"] == "check_wf_semantics_or_raise"
    for stage in ("regime_holdout_2022", "validation_2024", "tier5"):
        assert routing[stage] == "check_evaluation_semantics_or_raise"


def test_pathb_owns_its_namespace_not_the_sealed_cohort():
    assert eg.PATHB_EVAL_DIR.name == "pathb_eval_gauntlet_v1"
    assert "tier6_dsr_v1" not in eg.PATHB_EVAL_DIR.parts


def test_route_guard_dispatches_correct_callable(monkeypatch):
    seen = {}

    def fake_wf(summary, *, artifact_path=None):
        seen["wf"] = True

    def fake_eval(summary, *, artifact_path=None):
        seen["eval"] = True

    monkeypatch.setattr(eg, "check_wf_semantics_or_raise", fake_wf)
    monkeypatch.setattr(eg, "check_evaluation_semantics_or_raise", fake_eval)

    eg.route_guard("train_wf", {})
    eg.route_guard("tier5", {})
    assert seen == {"wf": True, "eval": True}


def test_route_guard_unknown_stage_raises():
    with pytest.raises(ValueError, match="unknown gauntlet stage"):
        eg.route_guard("nonexistent", {})
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_pathb_eval_gauntlet.py -v` / `Expected: FAIL (ModuleNotFoundError: backtest.pathb_eval_gauntlet)`

- [ ] **Step 3: Implement**

```python
# backtest/pathb_eval_gauntlet.py
"""Path B hypothesis DSL builder + evaluation gauntlet stage->guard routing.

build_hypothesis_dsl constructs the locked H-grid DSL using the REAL DSL/
compiler API (Condition(value=...) — NOT threshold; StrategyDSL(description=...,
entry=..., exit=..., position_sizing=...); compile_dsl_to_strategy(...) — NOT
compile_strategy).

EVAL_GAUNTLET pins which wf_lineage guard each stage uses:
  - train WALK-FORWARD artifacts  -> check_wf_semantics_or_raise (corrected_test_boundary_v1)
  - 2022 regime-holdout / 2024 validation / Tier-5 (all SINGLE-RUN evaluations)
        -> check_evaluation_semantics_or_raise (single_run_holdout_v1)

The two guards do NOT cross-validate; routing them by stage is the contract.
Path B writes into its OWN namespace, never the sealed cohort/tier6 dirs.

Threshold values (THETA_PUSH etc.) are Step -1 human-locked; referenced
symbolically.
"""
from __future__ import annotations

from pathlib import Path

from backtest.wf_lineage import (
    check_evaluation_semantics_or_raise,
    check_wf_semantics_or_raise,
)
from strategies.dsl import (
    Condition,
    ConditionGroup,
    SizingSpec,
    StrategyDSL,
)
from strategies.dsl_compiler import compile_dsl_to_strategy

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATHB_EVAL_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/pathb_eval_gauntlet_v1"

# Step -1 human-locked hypothesis param value (symbolic; H1 fades a DOWN-push).
THETA_PUSH = -0.6

# Stage -> guard name. train WF artifacts use the WF guard; every single-run
# evaluation (regime holdout, validation, Tier 5) uses the evaluation guard.
EVAL_GAUNTLET: dict[str, str] = {
    "train_wf": "check_wf_semantics_or_raise",
    "regime_holdout_2022": "check_evaluation_semantics_or_raise",
    "validation_2024": "check_evaluation_semantics_or_raise",
    "tier5": "check_evaluation_semantics_or_raise",
}


def build_hypothesis_dsl() -> StrategyDSL:
    """Build the H1 hypothesis DSL using the real DSL + compiler contract.

    H1 (spec §3) is microstructure MEAN-REVERSION: long when intrabar_push <
    THETA_PUSH (fade a one-sided DOWN-push), exit when the push reverts, with a
    vol-regime ternary SizingSpec on cdf_realized_vol_720 (NOT zscore_48 — that
    is H2's factor).

    Returns:
        A valid StrategyDSL (entry on intrabar_push < THETA_PUSH = fade a
        down-push) with a vol-regime ternary SizingSpec on a registered factor.
    """
    entry = ConditionGroup(
        conditions=[Condition(factor="intrabar_push", op="<", value=THETA_PUSH)]
    )
    exit_grp = ConditionGroup(
        conditions=[Condition(factor="intrabar_push", op=">", value=0.0)]
    )
    # H1 sizing is a vol-regime ternary on cdf_realized_vol_720 (spec §3 H1):
    # full size in the mid-vol band [0.3, 0.8], half outside. NOT zscore_48.
    sizing = SizingSpec(
        factor="cdf_realized_vol_720",
        bands=[{"lower": 0.3, "upper": 0.8, "size": 1.0}],
        default_size=0.5,
    )
    return StrategyDSL(
        name="pathb_h1",
        description="Path B H1: fade a one-sided down-push (mean-reversion), vol-regime ternary sizing on cdf_realized_vol_720.",
        entry=[entry],
        exit=[exit_grp],
        position_sizing=sizing,
        max_hold_bars=24,
    )


def route_guard(stage: str, summary: dict, *, artifact_path: str | None = None) -> None:
    """Dispatch the correct wf_lineage guard for a gauntlet stage.

    Args:
        stage: One of EVAL_GAUNTLET's keys.
        summary: The artifact summary dict to validate.
        artifact_path: Optional source path for diagnostics.

    Raises:
        ValueError: If ``stage`` is unknown, or propagated from the guard.
    """
    guard_name = EVAL_GAUNTLET.get(stage)
    if guard_name is None:
        raise ValueError(f"unknown gauntlet stage {stage!r} (known: {sorted(EVAL_GAUNTLET)})")
    guard = (
        check_wf_semantics_or_raise
        if guard_name == "check_wf_semantics_or_raise"
        else check_evaluation_semantics_or_raise
    )
    guard(summary, artifact_path=artifact_path)


def compile_hypothesis() -> type:
    """Compile the H1 DSL to a Backtrader strategy class (manifest suppressed).

    Returns:
        The compiled strategy class.
    """
    return compile_dsl_to_strategy(build_hypothesis_dsl(), write_manifest=False)
```

- [ ] **Step 2 note (sibling dependency):** `SizingSpec` and `ConditionGroup` come from Section C. The op literals here are the real `OpLiteral` symbols `">"`/`"<"` (`strategies/dsl.py:53`); `name=` and `description=` are both REQUIRED (`dsl.py:229-230`); `Condition` uses `value=` (not `threshold`). The compile test asserts `compile_dsl_to_strategy(dsl, write_manifest=False)` returns a class.

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_pathb_eval_gauntlet.py -v` / `Expected: PASS (5 passed)`

- [ ] **Step 5: Commit** — `git add backtest/pathb_eval_gauntlet.py tests/test_pathb_eval_gauntlet.py && git commit -m "feat(pathb): Task 27 — build_hypothesis_dsl + EVAL_GAUNTLET stage->wf_lineage guard routing"`

---

### Task 28: Step-5 DSR-FWER — per-candidate `evaluate_candidate` loop (NOT evaluate_cohort), survivors = `pass_B`

**Files:** Create: `backtest/pathb_dsr_fwer.py` · Test: `tests/test_pathb_dsr_fwer.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathb_dsr_fwer.py
"""Step 5 DSR-FWER: per-candidate evaluate_candidate loop; survivors = pass_B True."""
from __future__ import annotations

import pytest

import backtest.pathb_dsr_fwer as fwer
from backtest.tier6_dsr import CandidateMoments


def _moments(hh: str, sr: float, T: int = 2000) -> CandidateMoments:
    return CandidateMoments(
        hypothesis_hash=hh, name=hh, theme="t",
        sr_per_bar=sr, gamma3=0.0, gamma4=3.0, T=T, trades=50,
    )


def test_pathb_n_star_default_is_18():
    assert fwer.PATHB_N_STAR == 18


def test_dsr_rows_is_per_candidate_loop_over_evaluate_candidate():
    cands = [_moments("a", 0.0), _moments("b", 0.5)]
    rows = fwer._dsr_rows(cands, n_star=fwer.PATHB_N_STAR)
    assert len(rows) == 2
    # Each row carries the n_star used (evaluate_candidate stamps it).
    assert all(r["n_star"] == fwer.PATHB_N_STAR for r in rows)
    assert all("pass_B" in r for r in rows)


def test_survivors_are_rows_with_pass_B_true():
    # A tiny SR over a huge T forces pass_B True; SR=0 forces pass_B False.
    cands = [_moments("loser", 0.0), _moments("winner", 5.0, T=5000)]
    result = fwer.run_dsr_fwer(cands, n_star=fwer.PATHB_N_STAR)
    survivors = result["survivors"]
    assert all(r["pass_B"] is True for r in survivors)
    assert "loser" not in [r["hypothesis_hash"] for r in survivors]
    assert result["n_candidates"] == 2


def test_does_not_route_through_evaluate_cohort(monkeypatch):
    # Guard: evaluate_cohort hard-requires 18/21; Path B must NOT call it.
    import backtest.tier6_dsr as t6

    def boom(*a, **k):
        raise AssertionError("evaluate_cohort must NOT be called by Path B FWER")

    monkeypatch.setattr(t6, "evaluate_cohort", boom)
    fwer.run_dsr_fwer([_moments("a", 0.1)], n_star=fwer.PATHB_N_STAR)
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_pathb_dsr_fwer.py -v` / `Expected: FAIL (ModuleNotFoundError: backtest.pathb_dsr_fwer)`

- [ ] **Step 3: Implement**

```python
# backtest/pathb_dsr_fwer.py
"""Step 5 DSR-FWER for the Path B grid (per-candidate, NOT cohort-partition).

evaluate_cohort hard-requires the locked 18/21 partition via derive_cohort
(raises if len != 18/21). The Path B 3-9-variant grid is a DIFFERENT cohort, so
this module loops evaluate_candidate(cm, n_star=PATHB_N_STAR) per candidate and
selects survivors = rows with pass_B is True (the authoritative Form B gate).

CandidateMoments are constructed UPSTREAM (in the eval harness) from Path B's
OWN per-bar validation returns (sr_per_bar / gamma3 / gamma4 / T) — NOT via
load_candidate_moments, which loads the sealed cohort's holdout artifacts. Path
B owns its candidates, builds its own moments, and never reads the dead-18
cohort here.

PATHB_N_STAR is Step -1 human-locked (default 18); referenced symbolically.
"""
from __future__ import annotations

from backtest.tier6_dsr import CandidateMoments, evaluate_candidate

# Step -1 human-locked multiplicity for the Path B grid (default 18).
PATHB_N_STAR = 18


def _dsr_rows(candidates: list[CandidateMoments], n_star: int = PATHB_N_STAR) -> list[dict]:
    """Per-candidate DSR rows via evaluate_candidate (NOT evaluate_cohort).

    Args:
        candidates: The Path B grid's per-candidate moments.
        n_star: Step -1 locked multiplicity (default PATHB_N_STAR).

    Returns:
        One evaluate_candidate result dict per candidate, in input order.
    """
    return [evaluate_candidate(cm, n_star=n_star) for cm in candidates]


def run_dsr_fwer(
    candidates: list[CandidateMoments], n_star: int = PATHB_N_STAR
) -> dict:
    """Run the DSR-FWER screen; survivors are the authoritative Form B passes.

    Args:
        candidates: The Path B grid's per-candidate moments.
        n_star: Step -1 locked multiplicity (default PATHB_N_STAR).

    Returns:
        A dict with ``rows`` (all per-candidate DSR rows), ``survivors`` (rows
        with ``pass_B is True``), ``n_candidates`` and ``n_star``.
    """
    rows = _dsr_rows(candidates, n_star=n_star)
    survivors = [r for r in rows if r["pass_B"] is True]
    return {
        "rows": rows,
        "survivors": survivors,
        "n_candidates": len(candidates),
        "n_star": n_star,
    }
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_pathb_dsr_fwer.py -v` / `Expected: PASS (4 passed)`

- [ ] **Step 5: Commit** — `git add backtest/pathb_dsr_fwer.py tests/test_pathb_dsr_fwer.py && git commit -m "feat(pathb): Task 28 — Step-5 DSR-FWER per-candidate evaluate_candidate loop (pass_B survivors)"`

---

### Task 29: Earned-negative EVIDENCE bundle (advisory; keyed on Tier-5 `holdout_sharpe>0`, verdict is Charlie's read)

**Files:** Create: `backtest/pathb_earned_negative.py` · Test: `tests/test_pathb_earned_negative.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathb_earned_negative.py
"""Earned-negative EVIDENCE bundle (advisory): keyed on Tier-5 holdout_sharpe>0,
NOT DSR pass_B. The binding verdict + A-escalation is Charlie's read at the gate."""
from __future__ import annotations

import pytest

import backtest.pathb_earned_negative as en


def _ev(per_leg, n_tier5_pass, n_dsr_pass, side_effect=False):
    return en.assemble_evidence(
        per_leg=per_leg,
        n_tier5_pass=n_tier5_pass,
        n_dsr_pass=n_dsr_pass,
        step0_promotion_side_effect=side_effect,
    )


def test_mechanism_refuted_when_all_legs_insane():
    ev = _ev({"h2_low_leg_sane": False, "h2_high_leg_sane": False,
              "h1_sane": False, "h3_sane": False}, n_tier5_pass=0, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.MECHANISM_REFUTED
    assert ev["is_earned_negative"] is True


def test_process_refuted_when_sane_but_no_tier5_pass():
    # Keyed on Tier-5 holdout_sharpe>0 (n_tier5_pass), NOT DSR pass_B.
    ev = _ev({"h2_low_leg_sane": True, "h2_high_leg_sane": False,
              "h1_sane": False, "h3_sane": False}, n_tier5_pass=0, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.PROCESS_REFUTED_FOR_GRID
    assert ev["is_earned_negative"] is True


def test_b_positive_when_a_variant_clears_tier5_even_if_dsr_fails():
    # Spec §9: B-positive = >=1 variant clears Tier-5 holdout_sharpe>0, even if it
    # later fails DSR-FWER (n_dsr_pass=0). NOT an earned negative; weak (small-N*).
    ev = _ev({"h2_low_leg_sane": True, "h2_high_leg_sane": True,
              "h1_sane": True, "h3_sane": True}, n_tier5_pass=1, n_dsr_pass=0)
    assert ev["advisory_taxonomy"] == en.B_POSITIVE
    assert ev["is_earned_negative"] is False
    assert ev["b_positive_strength"] == "weak_needs_2025_oos"


def test_b_positive_strong_when_dsr_passes():
    ev = _ev({"h1_sane": True}, n_tier5_pass=2, n_dsr_pass=1)
    assert ev["advisory_taxonomy"] == en.B_POSITIVE
    assert ev["b_positive_strength"] == "dsr_promoted"


def test_promotion_side_effect_true_is_a_hard_error():
    # Step 0 / 23 guarantees read-only; a True side effect invalidates the run.
    with pytest.raises(ValueError, match="promotion_side_effect"):
        _ev({"h1_sane": True}, n_tier5_pass=0, n_dsr_pass=0, side_effect=True)


def test_bundle_is_advisory_not_a_fired_decision():
    ev = _ev({"h1_sane": True}, n_tier5_pass=0, n_dsr_pass=0)
    assert "escalate" not in ev  # no fired action
    assert ev["verdict_authority"] == "charlie_register_at_earned_negative_gate"
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_pathb_earned_negative.py -v` / `Expected: FAIL (ModuleNotFoundError: backtest.pathb_earned_negative)`

- [ ] **Step 3: Implement**

```python
# backtest/pathb_earned_negative.py
"""Earned-negative EVIDENCE bundle for the Path B grid (ADVISORY).

This module ASSEMBLES the evidence for the earned-negative read; it does NOT
fire any operational decision. Per the authorization discipline, the binding
taxonomy verdict AND the A-escalation are Charlie's register at the
earned-negative gate — an automated trigger is exactly where the falsification
polarity kept inverting.

Taxonomy (spec §9), keyed on Tier-5 ``holdout_sharpe > 0`` (NOT DSR pass_B):
  MECHANISM_REFUTED        — NO leg's conditional forward-return sign matched its
                             hypothesized direction (edge absent at the mechanism
                             level). Earned negative.
  PROCESS_REFUTED_FOR_GRID — >=1 leg mechanism-sane, but NO variant clears Tier-5
                             holdout_sharpe>0 — refuted for THIS grid/cost, not the
                             mechanism in general. Earned negative.
  B_POSITIVE               — >=1 variant clears Tier-5 holdout_sharpe>0 (spec §9
                             B-positive), even if it then fails DSR-FWER. NOT an
                             earned negative. Strength: 'weak_needs_2025_oos' if no
                             DSR pass (small-N* bar is easier, §8); 'dsr_promoted'
                             if >=1 DSR pass_B.

A True Step-0 promotion side effect is a hard error (Task 23 guarantees the
re-score is read-only).
"""
from __future__ import annotations

MECHANISM_REFUTED = "mechanism_refuted"
PROCESS_REFUTED_FOR_GRID = "process_refuted_for_this_grid"
B_POSITIVE = "b_positive"

# The per-leg / per-hypothesis sanity keys this bundle consumes.
_SANITY_KEYS = (
    "h2_low_leg_sane",
    "h2_high_leg_sane",
    "h1_sane",
    "h3_sane",
)


def assemble_evidence(
    per_leg: dict,
    n_tier5_pass: int,
    n_dsr_pass: int,
    step0_promotion_side_effect: bool,
) -> dict:
    """Assemble the (advisory) earned-negative evidence bundle.

    Args:
        per_leg: Task 26 per-leg + per-hypothesis sanity booleans.
        n_tier5_pass: # variants clearing Tier-5 ``holdout_sharpe > 0`` at 15bps
            (the spec §9 B-positive / process-refuted KEY — NOT DSR pass_B).
        n_dsr_pass: # variants passing DSR-FWER (Task 28 ``pass_B``) — the stronger
            promotion signal WITHIN B-positive.
        step0_promotion_side_effect: Task 23 read-only flag (MUST be False).

    Returns:
        An advisory dict: ``advisory_taxonomy`` (one of the 3 constants),
        ``is_earned_negative`` (bool), ``b_positive_strength`` (or None), the
        echoed inputs, and ``verdict_authority`` naming Charlie as the binding
        decider. It NEVER returns a fired action.

    Raises:
        ValueError: If ``step0_promotion_side_effect`` is True.
    """
    if step0_promotion_side_effect:
        raise ValueError(
            "promotion_side_effect=True: the Step-0 re-score must be read-only "
            "(Task 23); a side effect invalidates the earned-negative evidence."
        )

    any_mechanism_sane = any(bool(per_leg.get(k, False)) for k in _SANITY_KEYS)

    if n_tier5_pass >= 1:
        taxonomy = B_POSITIVE
        is_earned_negative = False
        strength = "dsr_promoted" if n_dsr_pass >= 1 else "weak_needs_2025_oos"
    elif not any_mechanism_sane:
        taxonomy = MECHANISM_REFUTED
        is_earned_negative = True
        strength = None
    else:
        taxonomy = PROCESS_REFUTED_FOR_GRID
        is_earned_negative = True
        strength = None

    return {
        "advisory_taxonomy": taxonomy,
        "is_earned_negative": is_earned_negative,
        "b_positive_strength": strength,
        "any_mechanism_sane": any_mechanism_sane,
        "n_tier5_pass": int(n_tier5_pass),
        "n_dsr_pass": int(n_dsr_pass),
        "verdict_authority": "charlie_register_at_earned_negative_gate",
    }
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_pathb_earned_negative.py -v` / `Expected: PASS (6 passed)`

- [ ] **Step 5: Commit** — `git add backtest/pathb_earned_negative.py tests/test_pathb_earned_negative.py && git commit -m "feat(pathb): Task 29 — earned-negative evidence bundle (advisory; Tier-5-keyed; mechanism/process/b-positive)"`

---

### Task 30: Objective-A escalation ADVISORY (warranted-iff; Charlie registers the fire)

**Files:** Create: `backtest/pathb_escalation.py` · Test: `tests/test_pathb_escalation.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pathb_escalation.py
"""A-escalation ADVISORY: warranted iff process-refuted negative AND Step-0 no-lift.
Advisory only — the actual escalation to Objective A is a Charlie register-event."""
from __future__ import annotations

import pytest

import backtest.pathb_escalation as esc
import backtest.pathb_earned_negative as en


def test_warranted_on_process_refuted_and_no_step0_lift():
    adv = esc.a_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, step0_lifted_any=False)
    assert adv["a_escalation_warranted"] is True
    assert adv["reason"] == esc.REASON_PROCESS_REFUTED_WARRANTS
    assert adv["authority"] == "charlie_register"


def test_not_warranted_if_step0_lifted_someone():
    # §9 A-trigger 2nd prong: Step-0 cost-aware re-score lifted a dead candidate
    # -> the process fix may still rescue OHLCV -> A not yet warranted.
    adv = esc.a_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, step0_lifted_any=True)
    assert adv["a_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_STEP0_LIFTED


def test_not_warranted_on_mechanism_refuted():
    adv = esc.a_escalation_advisory(
        taxonomy=en.MECHANISM_REFUTED, step0_lifted_any=False)
    assert adv["a_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_MECHANISM_REFUTED_DIFFERENT_AXIS


def test_not_warranted_on_b_positive():
    # B-positive = OHLCV process produced a Tier-5 survivor; A is optional upside,
    # Charlie re-evaluates. Never an automatic escalation.
    adv = esc.a_escalation_advisory(
        taxonomy=en.B_POSITIVE, step0_lifted_any=False)
    assert adv["a_escalation_warranted"] is False
    assert adv["reason"] == esc.REASON_B_POSITIVE_A_OPTIONAL


def test_advisory_never_fires_an_action():
    adv = esc.a_escalation_advisory(
        taxonomy=en.PROCESS_REFUTED_FOR_GRID, step0_lifted_any=False)
    assert adv["authority"] == "charlie_register"
    assert "fired" not in adv and "executed" not in adv


def test_unknown_taxonomy_raises():
    with pytest.raises(ValueError, match="unknown taxonomy"):
        esc.a_escalation_advisory(taxonomy="bogus", step0_lifted_any=False)
```

- [ ] **Step 2: Run test to verify it fails** — `Run: pytest tests/test_pathb_escalation.py -v` / `Expected: FAIL (ModuleNotFoundError: backtest.pathb_escalation)`

- [ ] **Step 3: Implement**

```python
# backtest/pathb_escalation.py
"""Objective-A escalation ADVISORY (NOT an auto-fire).

Per spec §9, escalation to Objective A (crypto-native data: funding/OI/basis/
liquidations) is warranted iff BOTH: (i) Path B is a PROCESS_REFUTED_FOR_GRID
earned negative (no variant cleared Tier-5 holdout_sharpe>0 under the cost-aware
+ min-trade + ternary-sizing process), AND (ii) the Step-0 cost-aware re-score
lifted NO dead candidate above 0. This module only ADVISES; per the
authorization discipline the actual escalation is a Charlie register-event — an
automated trigger is exactly where the falsification polarity kept inverting.

  PROCESS_REFUTED_FOR_GRID + no Step-0 lift -> warranted (advisory).
  PROCESS_REFUTED_FOR_GRID + Step-0 lifted  -> NOT warranted (process fix may
                                               still rescue OHLCV).
  MECHANISM_REFUTED -> NOT warranted (edge absent at the mechanism level; the
                       next-cheapest axis is different mechanisms, not data).
  B_POSITIVE -> NOT warranted (OHLCV process produced a Tier-5 survivor; A is
                optional upside, Charlie re-evaluates; weak B-positives need
                2025 OOS confirmation first, §8).
"""
from __future__ import annotations

from backtest.pathb_earned_negative import (
    B_POSITIVE,
    MECHANISM_REFUTED,
    PROCESS_REFUTED_FOR_GRID,
)

REASON_PROCESS_REFUTED_WARRANTS = "process_refuted_and_no_step0_lift_warrants_A"
REASON_STEP0_LIFTED = "step0_lifted_a_candidate_process_fix_may_rescue_ohlcv"
REASON_MECHANISM_REFUTED_DIFFERENT_AXIS = "mechanism_refuted_next_axis_is_mechanisms_not_data"
REASON_B_POSITIVE_A_OPTIONAL = "b_positive_a_optional_charlie_reevaluates"


def a_escalation_advisory(taxonomy: str, step0_lifted_any: bool) -> dict:
    """Advise whether Objective-A escalation is warranted (Charlie fires it).

    Args:
        taxonomy: A Task 29 taxonomy constant.
        step0_lifted_any: True iff Step-0 lifted any dead candidate above 0
            (the §9 A-trigger's second prong).

    Returns:
        An ADVISORY dict: ``a_escalation_warranted`` (bool), ``reason``, and
        ``authority="charlie_register"``. This module NEVER fires the escalation.

    Raises:
        ValueError: If ``taxonomy`` is unknown.
    """
    if taxonomy not in (MECHANISM_REFUTED, PROCESS_REFUTED_FOR_GRID, B_POSITIVE):
        raise ValueError(f"unknown taxonomy {taxonomy!r}")

    if taxonomy == PROCESS_REFUTED_FOR_GRID:
        if step0_lifted_any:
            warranted, reason = False, REASON_STEP0_LIFTED
        else:
            warranted, reason = True, REASON_PROCESS_REFUTED_WARRANTS
    elif taxonomy == MECHANISM_REFUTED:
        warranted, reason = False, REASON_MECHANISM_REFUTED_DIFFERENT_AXIS
    else:  # B_POSITIVE
        warranted, reason = False, REASON_B_POSITIVE_A_OPTIONAL

    return {
        "a_escalation_warranted": warranted,
        "reason": reason,
        "authority": "charlie_register",
    }
```

- [ ] **Step 4: Run test to verify it passes** — `Run: pytest tests/test_pathb_escalation.py -v` / `Expected: PASS (6 passed)`

- [ ] **Step 5: Commit** — `git add backtest/pathb_escalation.py tests/test_pathb_escalation.py && git commit -m "feat(pathb): Task 30 — A-escalation advisory (warranted iff process-refuted + no Step-0 lift; Charlie registers)"`

---

**Section E notes for the merge:**
- Task 27's `SizingSpec`/`ConditionGroup`/`Condition` imports depend on the DSL ternary-sizing task in Section C; the op literals are the real symbols `">"`/`"<"` (`dsl.py:53`), `name=`/`description=` are both required (`dsl.py:229-230`), and the compile test pins a successful `compile_dsl_to_strategy(...)`.
- **Tasks 29/30 are ADVISORY evidence-producers, NOT auto-fire decisions** (per the authorization discipline + to eliminate the falsification-polarity bug class): Task 29 assembles the taxonomy evidence keyed on Tier-5 `holdout_sharpe>0` (with DSR `pass_B` the stronger B-positive sub-case); Task 30 advises whether A-escalation is warranted (process-refuted **AND** no Step-0 lift). The binding taxonomy verdict and the actual Objective-A escalation are a **Charlie register-event** at the earned-negative gate (the `verdict_authority`/`authority` fields name this).
- All Path B output dirs (`pathb_step0_diagnostic_v1`, `pathb_eval_gauntlet_v1`) live in the Path B namespace under `data/phase2c_evaluation_gate/` — none touch the sealed `tier6_dsr_v1/` or `phase4_forward_2026_15bps_v1/` cohort dirs (byte-untouched invariant preserved).
- Forward-holdout (Task 23) + every single-run stage (Task 27 `regime_holdout_2022`/`validation_2024`/`tier5`) route through `check_evaluation_semantics_or_raise` (`single_run_holdout_v1`); only `train_wf` routes through `check_wf_semantics_or_raise` (`corrected_test_boundary_v1`) — the two guards do not cross-validate.
- `PATHB_N_STAR` defaults to 18 in Tasks 23/28; the `--n-star` CLI flag (default 18) belongs to Section A–D's `tier6_dsr.py` task — Section E references it symbolically per the Step -1 lock.

---

## Terminal state

On all-green + re-B2 + Charlie register: this completes Path B Steps 1–5. Step 0 (advisory) and the Step −1 pre-registration precede execution. Outcome feeds the §9 earned-negative taxonomy + the objective A-escalation trigger.
