# BTC Alpha Pipeline — Phase 2 Blueprint (v2)

**Version:** v2 (supersedes v1)
**Status:** Ready for D1 kickoff after final review pass
**Change log vs v1:** 23 amendments integrated from two rounds of ChatGPT + Gemini
review plus two author-added items. See "v1 → v2 Change Log" at end of document.

---

## Phase 2 Target

Build an AI-assisted hypothesis generation loop on top of the validated Phase 1
pipeline. The AI is the hypothesis source, but the research discipline is
enforced by plain Python infrastructure. Phase 2 is successful if it generates
and rigorously filters 200 hypotheses per batch without letting any of them
cheat on validation or test data, and produces an auditable shortlist that a
human reviews before any strategy advances toward paper trading.

**What "done" looks like for Phase 2A (infrastructure):**
A factor library with 14 core factors, a strategy DSL that compiles to
Backtrader, a deterministic hypothesis hash for deduplication, and a regime
holdout (2022) wired into the engine and registry. Zero LLM calls at this
stage.

**What "done" looks like for Phase 2B (AI loop):**
A single command runs a batch of 200 hypotheses end-to-end: Proposer generates
DSL → Critic vetoes weak ones → survivors run walk-forward on train → survivors
run regime holdout → survivors logged with batch-level DSR threshold → human-
reviewable leaderboard and auto-generated batch report. Entire batch stays
under $20. Zero test-set contamination.

---

## Phase 2A vs Phase 2B

Phase 2 is split to enforce discipline: AI cannot be introduced before the
scaffolding that prevents it from cheating exists.

**Phase 2A — AI-Free Infrastructure**
- D1: Factor library + registry + feature_version governance
- D2: Strategy DSL schema + Backtrader compiler
- D3: Hypothesis hash + dedup
- D4: Regime holdout integration (2022, fixed)
- D5: Baselines in DSL (sign-off gate)

**Phase 2B — AI Loop**
- D6: Proposer agent
- D7: Critic agent (approve/reject only)
- D8: Orchestrator with hard budget enforcement + lifecycle tracking
- D9: Batch DSR + leaderboard + auto-generated batch report

Do NOT start Phase 2B until Phase 2A is fully signed off. Do NOT make a single
Claude API call until 2A is green.

---

## Phase 2A Sign-Off Criteria

All 7 conditions must pass before Phase 2A is considered complete:

1. ✅ Core factor registry complete (14 total), each with docstring
   specifying inputs, computation, warmup period, output dtype, and null policy
2. ✅ Every factor has a unit test covering: warmup correctness, at least one
   known-value assertion against raw OHLCV, and NaN policy compliance
3. ✅ DSL schema validates: can round-trip a known strategy (e.g. SMA crossover)
   through DSL → compiler → Backtrader → engine with metrics matching the
   hand-written version (trade_count exact, Sharpe/return/drawdown within 1e-4)
4. ✅ Hypothesis hash is deterministic: same DSL → same hash; trivially
   equivalent DSL (reordered conditions, whitespace, operand order on
   commutative ops, float formatting variants) produces same hash
5. ✅ Regime holdout (2022-01-01 to 2022-12-31) is plumbed as an orchestrator-
   internal engine call (no general-purpose CLI); registry has new fields
   distinguishing train / holdout / validation / test runs
6. ✅ All 4 existing baseline strategies are reimplemented in DSL and pass
   identical metrics (within documented tolerance) to their hand-written
   versions. If any baseline cannot be expressed in DSL without special-case
   compiler hacks, the DSL schema MUST be revised — compiler special cases are
   a blueprint violation.
7. ✅ No existing tests break. Full test suite green (335+ existing + 2A
   additions)

## Phase 2B Sign-Off Criteria

All 9 conditions must pass before Phase 2B is considered complete:

1. ✅ Proposer emits valid DSL that validates against schema 100% of the time
   after up to 3 retries; hard failures logged as `proposer_invalid_dsl`
2. ✅ Critic outputs structured verdict (approve/reject) with mandatory
   economic_rationale_score, overfitting_risk_score, and reasoning fields
3. ✅ Orchestrator enforces $20 per-batch cap as a hard pre-call stop
4. ✅ Monthly cap of $100 enforced via persistent SQLite ledger that spans
   sessions and is crash-safe (pre-flight pending rows)
5. ✅ Deduplication works end-to-end: duplicates within a batch are collapsed
   and counted as `duplicate` in lifecycle tracking
6. ✅ Prompt contamination test passes: automated check asserts that
   validation, test, and regime-holdout data never appear in any Proposer or
   Critic prompt
7. ✅ Every hypothesis gets a lifecycle state; sum of lifecycle state counts
   equals `hypotheses_attempted`
8. ✅ End-to-end dry run on ~20 hypotheses (mocked API) completes without
   errors, produces leaderboard, applies batch-level DSR threshold, and emits
   a batch report markdown
9. ✅ At least one full 200-hypothesis live batch runs within budget with
   expected characteristics: most hypotheses fail DSR, survivors fewer than
   5, no silent lookahead bias detected in survivor audit

---

## Tech Stack (Phase 2 Additions)

| Component | Choice | Rationale |
|-----------|--------|-----------|
| LLM (Proposer) | Claude Sonnet (claude-sonnet-4-20250514) | Strategy reasoning |
| LLM (Critic) | Claude Sonnet (claude-sonnet-4-20250514) | Critic work requires deep reasoning for economic rationale + overfit detection. Haiku is too shallow for this. Budget supports Sonnet for both. |
| LLM (Haiku) | RESERVED for Phase 2.5 semantic dedup | Not used in initial Phase 2 |
| API client | `anthropic` Python SDK | Approved in CLAUDE.md for Phase 2+ |
| DSL validation | `pydantic` v2 (~= 2.0) | Structured LLM output validation |
| Hash | `hashlib` (stdlib) | SHA256 of canonical DSL JSON |
| Orchestration | Plain Python + asyncio for parallel API calls | No framework |

**New library approval request:** `pydantic` v2. Limited to DSL schema
validation and Anthropic SDK's structured output features. Not a framework
dependency.

---

## Deliverable Order — Phase 2A (5 items)

### D1 — Factor Library (`factors/`)

Create `factors/registry.py` with a `FactorRegistry` class. Each factor
implemented in `factors/<category>.py` and decorated with `@register_factor`.

**Core factors (required for D1 sign-off, 14 total):**

| Category | File | Factor Name |
|----------|------|-------------|
| Returns | `factors/returns.py` | `return_1h`, `return_24h`, `return_168h` |
| Moving averages | `factors/moving_averages.py` | `sma_20`, `sma_50`, `ema_12`, `ema_26` |
| Volatility | `factors/volatility.py` | `realized_vol_24h`, `atr_14` |
| Momentum | `factors/momentum.py` | `rsi_14`, `macd_hist` |
| Volume | `factors/volume.py` | `volume_zscore_24h` |
| Structural | `factors/structural.py` | `hour_of_day`, `day_of_week` |

**Deferred to Phase 2.1 (do NOT implement in D1):**
`sma_200`, `bbwidth_20_2`, `vwap_deviation_24h`, `bars_since_new_high_168h`,
`volume_ratio_24h_168h`, `macd_signal`. Add only after Phase 2B demonstrates
factor starvation in batch results (dedup rate > 30% or mode collapse observed).

**Registry API:**

```python
@dataclass
class FactorSpec:
    name: str                      # e.g. "rsi_14"
    category: str                  # e.g. "momentum"
    warmup_bars: int               # declared, not inferred
    inputs: list[str]              # e.g. ["close"]
    output_dtype: str              # "float64"
    compute: Callable              # (DataFrame) -> Series
    docstring: str                 # mandatory
    null_policy: Literal["nan_before_warmup_only"]  # only allowed value in D1

class FactorRegistry:
    def register(self, spec: FactorSpec) -> None: ...
    def get(self, name: str) -> FactorSpec: ...
    def list_names(self) -> list[str]: ...
    def max_warmup(self, names: list[str]) -> int: ...
    def compute_all(self, df, names: list[str]) -> DataFrame: ...
    def menu_for_prompt(self) -> str: ...  # formatted string for Proposer
    def canonical_metadata(self) -> dict:   # used for feature_version hash
        """Returns dict: {factor_name: {name, category, warmup_bars, inputs,
           output_dtype, compute_source_sha256}} sorted by name."""
```

**Hard constraints:**
- Every factor function takes a single `DataFrame` (full OHLCV) and returns a
  `Series` aligned to the same index
- Every factor declares its warmup explicitly — no "infer from parameters"
- No factor uses `shift(-1)` or any negative shift that looks into future
- Factors are pure functions: no side effects, no state, no I/O
- **NaN policy**: factor outputs MAY be NaN only before their declared warmup
  period. After warmup, NaN is a build failure (raise, don't silently continue)
- **Causal-only computation (CRITICAL)**: Every value at index `T` must depend
  ONLY on data at indices `<= T`. Vectorization cannot be used as an escape
  hatch for lookahead.

  **Allowed**: `df['x'].rolling(N).mean()`, `df['x'].rolling(N).std()`,
  `df['x'].ewm(span=N, adjust=False).mean()`, `df['x'].shift(+k)` (positive
  shift only), `df['x'].diff(N)` (backward diff), any operation where output
  at `T` is determined by `df.iloc[:T+1]`.

  **PROHIBITED**: `df['x'].mean()` (global), `df['x'].std()` (global),
  `df['x'].expanding().mean()` with no minimum constraint that excludes future
  bars, `df['x'].shift(-k)` (any negative shift), `df['x'].fillna(method='bfill')`
  (backfill), any full-series statistic used as a per-row normalizer, any
  operation that mixes data from `df.iloc[>T]` into `df.iloc[T]`.

  This is a blueprint-level hard rule, NOT a code review suggestion. The
  conversion from Phase 1's event-driven `next()` paradigm to Phase 2's
  vectorized pre-computed parquet removes Backtrader's implicit protection
  against lookahead. A single `.mean()` or `.std()` call on a full series
  silently poisons every downstream backtest and cannot be detected by
  performance metrics (it inflates everything uniformly).

- **Full-dataset parquet coverage**: `build_features.py` ALWAYS computes
  factors over the full available OHLCV range (e.g., 2020-01-01 to present).
  Never build features for a subset (train-only, validation-only, etc.).
  Subsetting happens at the consumption layer (engine via `fromdate`/`todate`),
  never at the production layer. This guarantees that all downstream
  consumers see factor values computed identically, without boundary artifacts
  from restart warmup.

**feature_version governance (strict):**

```python
def compute_feature_version(registry: FactorRegistry) -> str:
    """
    feature_version = SHA256 of a canonical JSON serialization of
    registry.canonical_metadata(), which includes for each factor:
      - name, category, warmup_bars, inputs, output_dtype
      - SHA256 of the compute function's source code (via inspect.getsource)
    Sorted deterministically by factor name.
    """
```

**Factor callable form requirement:**
Registered factor compute functions MUST be top-level named callables defined
in source files (e.g., `def compute_rsi_14(df): ...` at module scope).
Lambdas, nested functions, decorators that wrap the callable at registration
time, and dynamically-generated callables are PROHIBITED. This is required
because `inspect.getsource` behavior on non-top-level callables is not stable
across Python versions and would make `feature_version` non-deterministic.

**File: `factors/build_features.py`**

CLI that computes all factors for the canonical dataset and saves to
`data/features/btcusdt_1h_features.parquet`. The parquet's pyarrow metadata
must include `feature_version` and `built_at_utc`.

**Force-rebuild rule:** On any downstream read, if the parquet's stored
`feature_version` does not match the live `compute_feature_version(registry)`,
the parquet MUST be rebuilt from scratch before any consumer reads it. No
silent "use stale data" fallback.

```bash
python -m factors.build_features --pair BTCUSDT --interval 1h
python -m factors.build_features --force-rebuild
```

**Tests (`tests/test_factors.py`):**
- Registry registration works, duplicate names rejected
- Registry rejects lambdas and nested functions at registration time
- Each of the 14 factors computes without error on a 200-bar synthetic sample
- Each factor produces correct values at a hand-picked index (e.g. `sma_20` at
  row 20 equals `close.iloc[0:20].mean()`)
- `max_warmup([...])` returns correct maximum across inputs
- `build_features.py` produces parquet with expected columns, no nulls after
  warmup period (null policy compliance)
- Factor values identical across two independent builds (determinism)
- `feature_version` changes when a compute function is modified (even trivially)
- `feature_version` unchanged when only a docstring is modified (not included
  in metadata hash)
- Stale parquet (with old `feature_version` in metadata) triggers force-rebuild
  on next read
- **Causal lookahead test (CRITICAL)**: For each factor, split a 1000-bar
  synthetic series at index 500. Compute the factor on the full series, and
  separately on `df.iloc[:501]`. Assert that the factor value at every index
  `<= 500` is identical between the two computations (within float tolerance).
  Any factor using a global `.mean()`, `.std()`, or any non-causal operation
  will fail this test because adding future data (indices 501-999) changes
  earlier values. This is a forensic test designed to catch vectorization
  leaks that produce no visible symptom in normal operation.
- **Full-dataset parquet coverage test**: `build_features.py` invoked with
  the canonical dataset produces a parquet whose first and last index match
  the OHLCV source exactly. No command-line flag should be able to restrict
  the output to a subset of the date range.

---

### D2 — Strategy DSL + Compiler

**File: `strategies/dsl.py`** — Pydantic schema.
**File: `strategies/dsl_compiler.py`** — DSL → Backtrader strategy class.

**DSL schema (pydantic v2):**

```python
class Condition(BaseModel):
    factor: str                              # must be in FactorRegistry
    op: Literal["<", "<=", ">", ">=", "==", "crosses_above", "crosses_below"]
    value: float | str                       # float scalar, or registered factor name

    @field_validator("value")
    @classmethod
    def validate_value(cls, v, info):
        """If str, must match a registered factor name exactly.
           No other string values permitted."""
        ...

    @field_validator("factor")
    @classmethod
    def validate_factor(cls, v):
        """Must be a registered factor name."""
        ...


class ConditionGroup(BaseModel):
    """AND-connected group of conditions. Multiple groups are OR-connected."""
    conditions: list[Condition] = Field(min_length=1, max_length=4)


class StrategyDSL(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=1, max_length=300)  # one-sentence rationale
    entry: list[ConditionGroup] = Field(min_length=1, max_length=3)
    exit: list[ConditionGroup] = Field(min_length=1, max_length=3)
    position_sizing: Literal["full_equity"]                 # Phase 2: only this
    max_hold_bars: int | None = Field(default=None, ge=1, le=720)  # max 30 days

    # Phase 2 restrictions (enforced by validator)
    # - long/flat only, single position, no stops/targets
```

**DSL complexity budget (enforced at schema level):**
- entry groups: ≤ 3 (OR branches)
- exit groups: ≤ 3
- conditions per group: ≤ 4 (AND terms)
- `max_hold_bars`: ≤ 720 (30 days of 1h bars)
- `name`: ≤ 64 chars
- `description`: ≤ 300 chars

Violations reject the DSL. This is deliberate — most real strategies fit in
this budget, and it prevents the agent from generating over-parameterized
monsters that pass validation but represent logic bombs.

**Compiler behavior (must be documented and unit-tested separately per case):**

The compiler MUST dispatch comparisons by operand type explicitly.
`factor-vs-scalar` and `factor-vs-factor` are separate code paths and are
unit-tested independently.

| Operator | factor-vs-scalar | factor-vs-factor |
|----------|------------------|------------------|
| `<`, `<=`, `>`, `>=`, `==` | Continuous comparison on current bar | Continuous comparison on current bar |
| `crosses_above` | MUST use `bt.indicators.CrossOver(factor, scalar_line)` OR explicit two-bar form: `(factor[0] > scalar) AND (factor[-1] <= scalar)` | MUST use `bt.indicators.CrossOver(factor_a, factor_b)` OR explicit two-bar form |
| `crosses_below` | Same pattern, inverted | Same pattern, inverted |

A naive single-bar comparison for `crosses_above` / `crosses_below` is a
**compiler bug** and is rejected by a dedicated unit test that fakes a series
staying above a level for many bars and asserts `crosses_above` fires exactly
once.

**NaN handling in compiler:**
If either side of a comparison is NaN on the current bar, the condition
evaluates to `False`. Never `True`, never short-circuit. This is a common
source of silent bugs when warmup boundaries interact with `crosses_above`.

**Compilation manifest (research reproducibility):**
Every compiled strategy writes a manifest to
`data/compiled_strategies/<hypothesis_hash>.json` containing:
- Original DSL
- Compiler version (git commit SHA of dsl_compiler.py)
- Registered factor list snapshot (names + warmup_bars)
- `feature_version` used
- Pseudo-code rendering of the compiled strategy for human audit

This is written once per unique hypothesis_hash. If the file already exists,
the compiler reads-and-compares.

**Manifest drift definition (explicit):**
Drift is defined as a mismatch in ANY of the following fields between the
stored manifest and the current compilation context:
- Canonical DSL (the `canonicalize_dsl(dsl)` output)
- Compiler version (git SHA of `dsl_compiler.py`)
- Registered factor list snapshot (factor names and warmup_bars)
- `feature_version`

A drift raises `ManifestDriftError` and halts compilation. Resolution requires
explicit manifest regeneration (delete and recompile) with human
acknowledgment in the git log. A compiler that silently regenerates on drift
is a blueprint violation.

**Compiler API:**

```python
def compile_dsl_to_strategy(
    dsl: StrategyDSL,
    registry: FactorRegistry,
) -> type[BaseStrategy]:
    """
    Returns a dynamically-generated Backtrader strategy class that:
    - Reads pre-computed factors from the feature parquet
    - Evaluates entry conditions per bar (AND within group, OR across groups)
    - Emits buy/sell signals through the existing engine unchanged
    - Sets WARMUP_BARS = registry.max_warmup(factors_used)
    - STRATEGY_NAME is the DSL `name` field
    - Is compatible with run_backtest() and run_walk_forward() as-is
    """
```

**Hard constraints:**
- Compiler must NOT modify the existing engine, registry, or metrics code
- DSL validation must reject: unknown factor names, forward-looking operators,
  nested DSL, empty condition groups, non-long position sizing, complexity
  budget violations

**Tests (`tests/test_dsl.py`):**
- Invalid DSL rejected with clear error for each violation class
- Valid DSL compiles to a working strategy class
- `crosses_above` scalar test: series stays above level 50 bars → exactly 1 fire
- `crosses_above` factor-vs-factor test: two factors cross → correct fire count
- NaN test: NaN in factor during warmup does not fire spurious signals
- Round-trip test: hand-written SMA crossover → DSL version → compile → run on
  2024 H1 → `total_trades` exact match, Sharpe/return/max_dd within 1e-4
- `WARMUP_BARS` equals `max_warmup` across referenced factors
- Compilation manifest written, re-compile with same hash is consistent
- factor-vs-scalar and factor-vs-factor code paths have independent tests for
  `<`, `>`, `crosses_above`, `crosses_below`

---

### D3 — Hypothesis Hash + Dedup (`agents/hypothesis_hash.py`)

Build deduplication infrastructure before the first API call.

**Canonical form rules:**
1. Factor names sorted alphabetically within each `ConditionGroup.conditions`
2. Condition groups sorted lexicographically within `entry` and `exit`
3. All floats formatted as `f"{value:.6f}"` strings before JSON serialization
   (NOT `round()`, NOT `Decimal`, NOT `repr()` — this format is deterministic
   across Python versions at 6 decimal places for all IEEE 754 doubles we care
   about)
4. Strategy `name` and `description` excluded from hash (cosmetic)
5. `max_hold_bars` included in hash
6. Hash = SHA256 of canonical JSON, first 16 hex chars

```python
def hash_dsl(dsl: StrategyDSL) -> str: ...
def canonicalize_dsl(dsl: StrategyDSL) -> dict: ...  # for inspection/debugging
def are_equivalent(dsl_a: StrategyDSL, dsl_b: StrategyDSL) -> bool: ...
```

**Tests (`tests/test_hypothesis_hash.py`):**
- Same DSL → same hash
- Reordering conditions within AND group → same hash
- Reordering condition groups within entry/exit → same hash
- Changing `name` or `description` → same hash
- Changing factor, threshold, or operator → different hash
- Float representation: `0.10`, `0.100000`, `0.1` → same hash
- Float edge: `0.1 + 0.2` (= 0.30000000000000004) and `0.3` → same hash (both
  format to `"0.300000"`)
- Two genuinely different strategies → different hashes
- Hash is stable across Python runs (no randomized dict ordering)
- **`test_logical_equivalence_same_hash`** (explicit anti-regression): DSL A =
  `(sma_20 > sma_50) AND (rsi_14 < 30)` and DSL B = `(rsi_14 < 30) AND
  (sma_20 > sma_50)` produce the same hash. Documents the commutative-AND
  dedup attack surface that canonical sorting closes.
- **`test_commutative_or_same_hash`**: DSL with entry groups
  `[group_A, group_B]` and DSL with entry groups `[group_B, group_A]` produce
  the same hash.

---

### D4 — Regime Holdout Integration

Add a fixed 2022 bear-market holdout that the AI will never see.

**Changes to `config/environments.yaml`:**

```yaml
splits:
  v2:  # bumped from v1 for Phase 2
    train_windows:
      - [2020-01-01, 2021-12-31]
      - [2023-01-01, 2023-12-31]
    regime_holdout:
      start: 2022-01-01
      end: 2022-12-31
      label: "bear_2022"
      passing_criteria:
        min_sharpe: -0.5              # allow loss, but not crash
        max_drawdown: 0.25            # single DD ≤ 25%
        min_total_return: -0.15       # full year loss ≤ 15%
        min_total_trades: 5           # must actually trade
    validation:
      start: 2024-01-01
      end: 2024-12-31
    test:
      start: 2025-01-01
      end: 2025-12-31
```

**Rationale for holdout criteria:** 2022 was a near-pure BTC bear market
(~-65% drawdown on buy-and-hold). A long-only strategy is not expected to
generate positive Sharpe — it is expected to **not crash**. Requiring
`Sharpe > 0` is too strict and would reward survivorship by lucky trades.
Requiring `total_trades >= 5` prevents a "stayed flat the whole year" strategy
from passing by absence rather than robustness. These four conditions are AND.

**Changes to `backtest/experiment_registry.py`:**

Add columns:
- `run_type`: extended to include `"regime_holdout"` and `"batch_summary"`
- `batch_id`: TEXT, groups hypotheses from the same Phase 2B batch
- `hypothesis_hash`: TEXT, links to DSL canonical hash
- `split_version`: already exists, bump to `"v2"` for Phase 2 runs
- `regime_holdout_passed`: BOOLEAN — all four criteria met
- `lifecycle_state`: TEXT (see D8)
- `feature_version`: TEXT (from D1)

**Changes to `backtest/engine.py`:**

Add an internal function `run_regime_holdout(dsl, batch_id, parent_run_id)`
that calls `run_backtest()` with `fromdate=2022-01-01, todate=2022-12-31`.
The Backtrader feed loads the full dataset (warmup before Jan 1 2022 is served
naturally by the feed); metrics compute only over the fromdate-todate window.
Writes a row with `run_type="regime_holdout"`, `parent_run_id` linking to the
train walk-forward summary, and `regime_holdout_passed` computed per the
four criteria.

**Hard constraint:** No `--mode regime-holdout` CLI exposed. Regime holdout
is orchestrator-internal only. This is deliberate — holdout must not become
a tool people casually invoke for ad-hoc analysis, because each invocation
is an observation of the held-out data.

**Train window representation in walk-forward:**

The v2 `train_windows` is a list of two disjoint ranges (2020-2021, 2023).
Walk-forward generates windows from each range independently; 2022 bars are
never included in any train window. The Backtrader feed is loaded with
`fromdate` and `todate` set per window; warmup is served from bars preceding
`fromdate` within the loaded feed (Phase 1A mechanism, unchanged).

**Train-summary aggregation semantics (authoritative for v2):**

For v2 splits with multiple disjoint train windows, the `train_sharpe`,
`train_return`, `train_max_dd`, and other `train_*` summary metrics referred
to throughout D6-D9 are aggregate statistics across all walk-forward windows
generated from the `train_windows` list, computed as follows:

- `train_sharpe` = arithmetic mean of per-window Sharpe ratios
- `train_return` = arithmetic mean of per-window total returns
- `train_max_dd` = maximum (worst) of per-window max drawdowns
- `train_total_trades` = sum of per-window trade counts
- `train_win_rate` = trade-weighted mean of per-window win rates

**Hard rule:** Per-window equity curves are NEVER stitched together across
disjoint train windows to form a single continuous series. The 2020-2021
and 2023 windows are independent observations, and a synthetic stitched
equity curve would be meaningless (implying a continuous investment that
was actually interrupted by the 2022 holdout).

Per-window metrics remain stored in the registry as individual
`walk_forward_window` rows. Summary metrics are derived from the set of
window summaries, stored in the `walk_forward_summary` row.

**Tests (`tests/test_regime_holdout.py`):**
- Walk-forward windows generated from v2 split contain zero 2022 bars
- `run_regime_holdout()` produces a registry row with correct `run_type` and
  `parent_run_id`
- Passing criteria evaluation: synthetic cases with Sharpe=-0.6 fails; Sharpe=0
  with DD=30% fails; Sharpe=-0.3, DD=20%, return=-10%, trades=10 passes
- `regime_holdout_passed` is True iff all four criteria met
- Integration test: DSL-compiled SMA crossover runs on v2 train windows + 2022
  holdout; two walk-forward summary rows (one per range) + one holdout row;
  linkage via parent_run_id is correct

---

### D5 — Baselines in DSL (sign-off gate)

Reimplement all 4 existing baselines in DSL. This is the Phase 2A sign-off
gate — if DSL can't express these, the DSL is wrong, not the compiler.

Files:
- `strategies/dsl_baselines/sma_crossover.json`
- `strategies/dsl_baselines/momentum.json`
- `strategies/dsl_baselines/volatility_breakout.json`
- `strategies/dsl_baselines/mean_reversion.json`

**Tests (`tests/test_dsl_baselines.py`):**
- Each DSL JSON loads, validates, compiles, runs on 2024 H1
- `total_trades` exactly matches hand-written version
- Sharpe, total_return, max_drawdown within 1e-4 relative tolerance of
  hand-written version

**Failure mode policy:**
If a baseline cannot be represented in DSL without special-case compiler
hacks, the required action is **DSL schema revision**, NOT a compiler
special case. Compiler special cases for specific baselines are a blueprint
violation and will block 2A sign-off. If schema revision is needed, pause
2A, update D2 and D3, and re-verify D4 and D5.

---

## Deliverable Order — Phase 2B (4 items)

### D6 — Proposer Agent (`agents/proposer.py`)

LLM call that generates hypothesis DSL given a strictly-bounded context.

**Prompt structure (allow-listed fields only):**

```
SYSTEM:
You are a quantitative researcher proposing BTC trading hypotheses.
Respond ONLY with valid JSON matching the schema.
Your strategy must:
  - Reference only factors from the menu below
  - Include a one-sentence economic rationale (why would this work?)
  - Use long/flat positions only
  - Respect complexity budget (entry/exit ≤ 3 groups, ≤ 4 conditions each)

Available factors:
{factor_menu}   # from FactorRegistry.menu_for_prompt()

USER:
Batch context:
  - batch_id: {batch_id}, position: {k}/{N}
  - theme (rotating): {theme}

Recent batch signal (compact, no raw metrics):
  - dedup rate so far: {dedup_rate}
  - top 5 most-used factors: {top_factors}
  - critic rejections in last 50: {rejection_count}
  - up to 3 example approved hypotheses (DSL only, no metrics):
    {approved_examples}

Propose hypothesis #{k}.
```

**Proposer context hard caps (enforced in code):**
- Max 3 prior approved-example DSLs, DSL only, NO metrics
- NO raw Sharpe, return, drawdown, or any per-hypothesis numeric result
- Total Proposer user prompt ≤ 2000 tokens (excluding factor menu)
- Factor menu is a separate constant; not re-transmitted per call if API
  supports prompt caching

**Rotating themes** (to prevent mode collapse):
`THEMES = ["momentum", "mean_reversion", "volatility_regime",
"volume_divergence", "calendar_effect", "multi_factor_combination"]`

**Theme assignment rule (authoritative):**
```python
theme = THEMES[(k - 1) % len(THEMES)]
```
where `k` is the 1-indexed hypothesis position within the batch. For a
200-hypothesis batch, each theme receives ~33 hypotheses, deterministic
across batches for direct comparison.

**Prompt contamination rules (hard, testable):**
- Proposer NEVER sees validation (2024), test (2025), or regime holdout
  (2022) metrics, even after the fact
- Proposer NEVER sees raw price data
- Proposer NEVER sees raw train metrics either — only aggregate stats and
  example DSLs

**Tests (`tests/test_proposer.py`):**
- Mocked API returns valid JSON → parses to StrategyDSL
- Mocked API returns invalid JSON → retry triggered, max 3 retries
- Mocked API returns 3 invalid → failure logged with lifecycle state
  `proposer_invalid_dsl`, loop continues
- Prompt-construction test: assert no numeric Sharpe/return/DD appears in any
  constructed prompt, across 100 random states
- Prompt-construction test: assert factor_menu only references registered
  factors, validation/test/holdout data never present
- Token budget test: constructed prompt stays under 2000 tokens for all
  supported batch states

---

### D7 — Critic Agent (`agents/critic.py`)

Second LLM call that vetoes weak proposals before backtest compute.

**Critic output schema (structured, Sonnet):**

```python
class CriticVerdict(BaseModel):
    verdict: Literal["approve", "reject"]  # NO "refine" in v2
    economic_rationale_score: int = Field(ge=0, le=5)
    overfitting_risk_score: int = Field(ge=0, le=5)
    reasoning: str = Field(min_length=20, max_length=500)
```

**Verdict logic:**
- `approve`: proceeds to backtest
- `reject`: dropped, logged with reasoning
- Auto-reject override: if `overfitting_risk_score >= 4`, verdict is forced to
  `reject` regardless of what the Critic said

**Why approve/reject only (no refine):**
Refinement was in v1. Removed because it creates ambiguity in hypothesis
identity — a refined DSL re-hashes to a new hash, re-runs dedup, re-costs,
and complicates `hypotheses_attempted` accounting. Phase 2's thesis is
discipline over cleverness. If refinement value shows up in Phase 2B
observation, it can be added in Phase 2.5 as a second Proposer turn (not as
Critic self-modification).

**Critic context rules:**
- Critic sees ONLY the current hypothesis DSL + the factor menu
- Critic NEVER sees prior results, raw prices, or evaluation metrics
- Critic cannot modify factor names or introduce new factors

**Tests (`tests/test_critic.py`):**
- Mocked "approve" → hypothesis advances, lifecycle state progresses
- Mocked "reject" → logged with reasoning, lifecycle state `critic_rejected`
- High overfitting_risk_score (4 or 5) forces reject even with "approve"
  verdict field
- Critic prompt does not contain any metrics or prior results (tested
  across 100 random hypotheses)

---

### D8 — Orchestrator + Budget + Lifecycle (`agents/orchestrator.py`)

The main loop. Plain Python. Owns budget and lifecycle. Not an "agent" —
logic.

**Hypothesis lifecycle states (new in v2):**

Every hypothesis is assigned exactly one **terminal** lifecycle state by the
time the batch closes:

Terminal states (8):
- `proposer_invalid_dsl` — 3 retries exhausted
- `duplicate` — hash already seen in this batch
- `critic_rejected` — Critic voted reject or overfit_score forced reject
- `train_failed` — train walk-forward did not meet `min_train_sharpe`
- `holdout_failed` — train passed but regime holdout passing criteria not met
- `dsr_failed` — holdout passed but batch DSR threshold not met
- `shortlisted` — passed all gates, flagged for human review
- `budget_exhausted` — placeholder state used for unissued slots (see below)

Transient orchestration state (1):
- `pending_dsr` — hypothesis has passed all orchestrator-time gates (propose,
  dedup, critic, train, holdout) and is awaiting batch-close DSR
  adjudication. This is NOT a terminal state. It exists only while the batch
  is open and must be resolved to either `shortlisted` or `dsr_failed` by D9
  at batch close.

**Lifecycle invariant (checked at batch close only, never mid-batch):**

```
sum(count(state) for state in TERMINAL_STATES) == hypotheses_attempted
```

Mid-batch the invariant is transiently violated (some hypotheses are in
`pending_dsr`). The invariant check fires as part of D9's `finalize_batch()`,
after all `pending_dsr` hypotheses have been resolved. A mid-batch invariant
check is a blueprint violation.

**Unissued slots handling:**

If `hypotheses_attempted < batch_size` due to budget exhaustion, the
remaining slots are NOT counted as `hypotheses_attempted` and do NOT receive
lifecycle states. They are tracked separately in the `batch_summary` row as
`unissued_slots = batch_size - hypotheses_attempted`. The `budget_exhausted`
terminal state is reserved for a narrower case (see orchestrator pseudocode).

**`hypotheses_attempted` counting rule (hard):**

> `hypotheses_attempted` increments immediately after each Proposer call
> returns, regardless of validity, duplication, or Critic outcome. It does
> NOT include unissued hypotheses that were never proposed because the batch
> stopped early (budget exhausted). Those are recorded separately as
> `unissued_slots` in the batch_summary row.

**Orchestrator pseudocode:**

```python
def run_batch(batch_size=200, max_usd=20.0, theme_rotation=True):
    batch_id = uuid()
    seen_hashes = set()
    hypotheses_attempted = 0
    spent_local = 0.0
    lifecycle_counts = defaultdict(int)

    while hypotheses_attempted < batch_size:
        # Pre-flight budget check (BEFORE api call)
        if spent_local >= max_usd:
            close_batch(batch_id, reason="batch_cap")
            break
        if get_monthly_spend() + spent_local >= MONTHLY_CAP:
            close_batch(batch_id, reason="monthly_cap")
            break

        # 1. Propose (counts regardless of outcome)
        estimated_cost = estimate_proposer_cost(context)
        ledger_pending_row = ledger.write_pending(estimated_cost)
        try:
            dsl_or_error, actual_cost = propose(context)
        except Exception as e:
            ledger.finalize(ledger_pending_row, status="crashed", cost=0)
            raise
        ledger.finalize(ledger_pending_row, status="completed", cost=actual_cost)
        spent_local += actual_cost
        hypotheses_attempted += 1

        if isinstance(dsl_or_error, ProposerError):
            log_lifecycle(batch_id, None, "proposer_invalid_dsl")
            lifecycle_counts["proposer_invalid_dsl"] += 1
            continue

        dsl = dsl_or_error

        # 2. Dedup
        h = hash_dsl(dsl)
        if h in seen_hashes:
            log_lifecycle(batch_id, h, "duplicate")
            lifecycle_counts["duplicate"] += 1
            continue
        seen_hashes.add(h)

        # 3. Critique (pre-flight charge pattern same as above)
        verdict, cost = critique_with_ledger(dsl)
        spent_local += cost
        if verdict.verdict != "approve":
            log_lifecycle(batch_id, h, "critic_rejected")
            lifecycle_counts["critic_rejected"] += 1
            continue

        # 4. Train walk-forward (no LLM cost)
        wf = run_walk_forward_on_train(dsl, batch_id, h)
        if wf.mean_sharpe < MIN_TRAIN_SHARPE:
            log_lifecycle(batch_id, h, "train_failed")
            lifecycle_counts["train_failed"] += 1
            continue

        # 5. Regime holdout (no LLM cost, orchestrator-internal only)
        holdout = run_regime_holdout(dsl, batch_id, wf.run_id)
        if not holdout.regime_holdout_passed:
            log_lifecycle(batch_id, h, "holdout_failed")
            lifecycle_counts["holdout_failed"] += 1
            continue

        # Pre-shortlist (final state assigned by D9 after batch close)
        log_lifecycle(batch_id, h, "pending_dsr")  # transient

    # 6. Batch close: compute DSR, finalize shortlist vs dsr_failed
    finalize_batch(batch_id, hypotheses_attempted, lifecycle_counts,
                   spent_local)
```

**Budget ledger — pre-flight charge (crash-safe):**

SQLite table `agents/spend_ledger.db` with schema:

```sql
CREATE TABLE ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT,
    api_call_kind TEXT,  -- "proposer" | "critic"
    status TEXT,  -- "pending" | "completed" | "crashed"
    estimated_cost REAL,  -- upper bound, set on pending
    actual_cost REAL,  -- set on completion
    created_at_utc TEXT,
    completed_at_utc TEXT
);
```

**Crash-safe rules:**
- BEFORE each API call: write a `status="pending"` row with upper-bound cost
  (prompt token count × max output tokens × unit price)
- AFTER API returns: UPDATE the row to `status="completed", actual_cost=...`
- If orchestrator restarts: any `status="pending"` rows are treated as
  **spent** (conservative), and the batch containing them is marked
  `crashed`; no resumption of crashed batches
- Monthly spend query: `SELECT SUM(COALESCE(actual_cost, estimated_cost))
  FROM ledger WHERE ... AND status IN ('pending', 'completed')` (pending
  counts as spent in all budget checks)

**Monthly cap persistence:**
`MONTHLY_CAP = 100.0`. Query totals from ledger filtered by
`created_at_utc >= start_of_month_utc`.

**Month boundary definition (authoritative):**

"Month" is strictly a **UTC calendar month**, NOT a rolling 30-day window.
A new month begins at `YYYY-MM-01T00:00:00Z` (the first instant of the first
calendar day, in UTC). Budget available on `YYYY-MM-01T00:00:01Z` is the
full `MONTHLY_CAP` regardless of prior spending.

Implementation:
```python
def start_of_month_utc(now: datetime) -> datetime:
    return datetime(now.year, now.month, 1, tzinfo=timezone.utc)
```

Rationale: calendar-month semantics matches human budget intuition and is
predictable. Rolling-30-day is an anti-pattern here — it creates non-
obvious "blackout windows" after a large batch and makes monthly budget
reporting opaque.

**CLI:**

```bash
python -m agents.orchestrator --batch-size 200 --max-usd 20 --theme momentum
python -m agents.orchestrator --dry-run --batch-size 5  # mocked API, full pipeline
python -m agents.orchestrator --status  # show current monthly spend, recent batches
```

**Tests (`tests/test_orchestrator.py`):**
- Dry-run mode with mocked API completes full pipeline on 5 hypotheses
- Budget cap hit mid-batch → clean shutdown, `budget_exhausted` lifecycle used
  for unissued slots? NO — unissued slots go to `batch_summary.unissued_slots`
  column, not the lifecycle table
- Monthly cap persists across sessions (write ledger, restart, verify query)
- Pre-flight pending row pattern: kill process between pending-write and
  completion-update, restart, verify pending row counted as spent
- Duplicate hypothesis handling: same hash proposed twice → second is
  `duplicate` state
- Sum of lifecycle state counts == hypotheses_attempted
- Prompt contamination test: inspect every Proposer and Critic prompt for 100
  simulated hypotheses, assert no prohibited data present

---

### D9 — Batch DSR + Leaderboard + Report

**Extend `backtest/evaluate_dsr.py` and add `backtest/batch_report.py`.**

**DSR command:**

```bash
python -m backtest.evaluate_dsr --batch-id <uuid> --min-train-sharpe 0.5
```

**Logic:**
- Queries registry for the `batch_summary` row; N = `hypotheses_attempted`
  (NOT `hypotheses_approved`, NOT `survivors`)
- Threshold = `sqrt(2 * ln(N))` — heuristic approximating the expected
  maximum Sharpe under the null hypothesis of i.i.d. N(0,1) draws (NOT full
  Bailey-Lopez de Prado DSR; this is documented as approximate)
- For each hypothesis that reached `pending_dsr` lifecycle state:
  - If `train_sharpe >= threshold` AND `regime_holdout_passed == True`:
    finalize lifecycle state to `shortlisted`
  - Else: finalize to `dsr_failed`

**D9 finalization authority (hard rule):**

D9 (`evaluate_dsr.py` / `finalize_batch()`) is the ONLY stage permitted to
transition hypotheses from `pending_dsr` to a terminal state (`shortlisted`
or `dsr_failed`). No earlier stage — including Proposer, Critic, walk-forward,
or regime holdout — may assign `shortlisted`. The orchestrator writes
`pending_dsr` and stops; D9 writes the terminal state at batch close.

**Batch-close statistics principle:**

All statistics that depend on finalized lifecycle distributions or DSR-
adjusted shortlist status are computed ONLY at batch close, never mid-batch.
This includes:
- `sum(terminal_lifecycle_counts) == hypotheses_attempted` invariant
- DSR threshold `sqrt(2 * ln(N))`
- Shortlist count and ranking
- Batch report anomaly flags that depend on terminal states (dedup rate,
  Critic approve rate, factor usage concentration, etc.)

Mid-batch dashboards (if ever added) must clearly distinguish "transient
pending_dsr count" from terminal state counts.

**Leaderboard ranking rule (written into blueprint as authoritative):**

> After filtering to `lifecycle_state == "shortlisted"` AND
> `regime_holdout_passed == True` AND DSR threshold passed, candidates are
> ranked by `min(train_sharpe, holdout_sharpe)` descending. Ties broken by
> `train_return` descending.

Rationale: `min(train, holdout)` rewards strategies that are robust across
both windows, not lucky in one. This replaces the v1 sign-product ranking
which was sign consistency only, not a true rank function.

**Leaderboard CSV columns (`data/batches/<batch_id>_leaderboard.csv`):**
```
rank, hypothesis_hash, strategy_name, description,
train_sharpe, train_return, train_max_dd,
holdout_sharpe, holdout_return, holdout_max_dd, holdout_total_trades,
min_score, lifecycle_state, requires_human_review,
entry_conditions, exit_conditions
```

**Batch report (`data/batches/<batch_id>_report.md`, auto-generated):**

Contains:
- Batch metadata: batch_id, started_at, closed_at, split_version,
  feature_version, total budget spent, batch cap, monthly cap remaining
- Lifecycle state distribution (counts + percentages)
- Factor usage frequency (top 10, across all proposed hypotheses)
- Dedup rate
- Rotating theme distribution
- Critic verdict statistics (approve rate, mean overfitting_risk_score, mean
  economic_rationale_score)
- DSR threshold computed for this N
- Shortlist with one-line description of each survivor
- Budget breakdown (Proposer vs Critic cost)
- Anomaly flags: dedup rate > 30%, Critic approve rate > 50%, any single
  factor used > 40% of the time, Proposer invalid DSL rate > 10%

**Why the report is a D9 deliverable, not a later nicety:**
Without it, postmortem requires manual SQLite queries. With it, prompt
iteration has a feedback signal (high dedup → Proposer prompt too narrow;
high Critic approve rate → Critic too lenient; etc.).

**Tests (`tests/test_batch_dsr.py`, `tests/test_batch_report.py`):**
- Synthetic batch of 200 noise Sharpes: DSR correctly identifies expected
  false-positive rate
- Batch with genuine Sharpe=3 outlier among 200 noise: outlier survives
- N-cheating test: manually compute DSR using approved count only, assert
  result differs (documents the anti-pattern)
- Leaderboard ranking: synthetic candidates, verify `min(train, holdout)`
  ordering
- Report generation: mock batch data, verify all required sections present
- Anomaly flags fire correctly on constructed edge cases

---

## Updated Document Conflict Priority

1. `config/execution.yaml`
2. `config/environments.yaml` (now v2, adds regime_holdout with passing criteria)
3. `config/schemas.yaml`
4. `CLAUDE.md` (needs Phase 2 update — see below)
5. `data_dictionary.md`
6. `PHASE2_BLUEPRINT.md` v2 (this file)
7. `PHASE1_BLUEPRINT.md` (reference only)
8. `PHASE0_BLUEPRINT.md` (reference only)

---

## CLAUDE.md Updates Required (before D1)

Add new hard constraints:
- ❌ NEVER include validation, test, or regime-holdout metrics/data in any
  prompt context sent to an LLM
- ❌ NEVER use `hypotheses_approved` as N for DSR — must use
  `hypotheses_attempted` from the batch_summary row
- ❌ NEVER modify `agents/spend_ledger.db` from any script other than the
  orchestrator
- ❌ NEVER bypass the Critic — all approved hypotheses go through it
- ❌ NEVER allow a DSL to compile to a strategy that uses negative shifts or
  intrabar reads of close
- ❌ NEVER let the Proposer see regime holdout results, even after the fact
- ❌ NEVER translate `crosses_above` / `crosses_below` as a naive single-bar
  comparison; must use `bt.indicators.CrossOver` or explicit two-bar form
- ❌ NEVER add a compiler special case for a specific baseline; if DSL cannot
  express a baseline, revise the DSL
- ❌ NEVER approve a Phase 2 library outside `pydantic` v2 and `anthropic`
  without explicit human approval
- ❌ NEVER expose a general-purpose CLI for regime holdout execution — it is
  orchestrator-internal only
- ❌ NEVER use Haiku for Critic in Phase 2 — Critic requires Sonnet-level
  reasoning for economic rationale and overfit detection
- ❌ NEVER use global aggregations (`.mean()`, `.std()`) or future-touching
  operations (`.shift(-k)`, `bfill`, unbounded `expanding()`) in factor
  compute functions — vectorization is not an escape hatch for lookahead
- ❌ NEVER stitch disjoint train-window equity curves into a single
  continuous series for metric computation — aggregation is mean/sum across
  window summaries, not concatenated bars
- ❌ NEVER register a factor as a lambda, nested function, or dynamically-
  generated callable — top-level named functions only
- ❌ NEVER assign `shortlisted` outside D9 (`finalize_batch()`); the
  orchestrator writes `pending_dsr` and stops
- ❌ NEVER check the lifecycle invariant mid-batch; it only holds at batch
  close
- ❌ NEVER interpret "month" as a rolling 30-day window for budget purposes;
  month is strictly UTC calendar month

Add new phase markers and tracking:
- Phase 2A in progress / Phase 2B in progress / Phase 2 complete
- Current batch_id (if running)
- Current monthly spend (queried from ledger)

---

## Scope Fences (Explicitly NOT in Phase 2)

- ❌ Short positions (Phase 3+)
- ❌ Stop-loss / take-profit (Phase 3+)
- ❌ Multi-asset strategies (Phase 5+)
- ❌ Feature engineering via LLM (DSL references pre-computed factors only)
- ❌ Reinforcement learning, gradient-based optimization
- ❌ Real-time streaming features (Phase 4+)
- ❌ Full Bailey-Lopez de Prado DSR (heuristic remains sufficient)
- ❌ Automated paper trading based on Phase 2 winners (Phase 4)
- ❌ More than 14 factors in initial registry (scope creep; add in Phase 2.1)
- ❌ Agent self-improvement loops, memory, or fine-tuning
- ❌ Critic refinement verdict (removed from v2; consider for Phase 2.5)
- ❌ Semantic deduplication via LLM (Haiku reserved for Phase 2.5 if factor
  enumeration dedup proves insufficient)

---

## Critical Risks & Mitigations

1. **Agent generates lookahead-biased DSL.**
   Mitigation: DSL validator rejects negative shifts; compiler only allows
   factors from registry (audited); `crosses_above` uses CrossOver or
   explicit two-bar form; NaN-to-False rule.

2. **Agent silently memorizes 2024 patterns via prompt contamination.**
   Mitigation: allow-listed prompt fields; integration test asserts only
   train-window summary data in prompts; prompt-construction tests run on
   100 random batch states.

3. **Budget spirals on crash mid-batch.**
   Mitigation: pre-flight charge pattern; pending rows count as spent;
   no resumption of crashed batches.

4. **N-cheating on DSR.**
   Mitigation: `batch_summary.hypotheses_attempted` is authoritative; DSR
   code reads from that field; N-cheating test documents the anti-pattern;
   lifecycle state invariant `sum(counts) == hypotheses_attempted` enforced.

5. **Mode collapse — agent proposes 200 variants of same strategy.**
   Mitigation: dedup via hash; rotating themes; batch report flags dedup
   rate > 30%; if triggered, pause for prompt revision.

6. **Regime holdout leaks back via prompt context.**
   Mitigation: holdout runs in a separate `run_type` bucket; prompt
   builders have unit-tested allowlist of queryable run_types; negative
   test asserts holdout run_type never appears in any constructed prompt.

7. **Stale factor parquet silently used after factor bug fix.**
   Mitigation: feature_version hashed from compute function source;
   parquet metadata stores feature_version; consumers verify match and
   force-rebuild on mismatch; no "use stale data" fallback.

8. **Holdout pass criteria gamed by lucky no-trade strategies.**
   Mitigation: `min_total_trades >= 5` required in addition to Sharpe and
   drawdown conditions.

9. **DSL compiler drift unauditable after the fact.**
   Mitigation: compilation manifest written per hypothesis_hash, including
   compiler git SHA; re-compile with same hash detects drift.

10. **Complexity monster: agent submits 50-condition DSL that passes JSON
    validation but is obvious overfit.**
    Mitigation: DSL complexity budget enforced at pydantic schema level
    (entry/exit ≤ 3 groups, ≤ 4 conditions each).

11. **Vectorization lookahead leak: factor computation uses global
    `.mean()` / `.std()` or expanding window, silently poisoning every
    downstream backtest.**
    Mitigation: D1 Hard Constraint prohibits non-causal operations;
    forensic "future bar invariance" unit test asserts factor values at
    index `T` are identical whether computed on `df[:T+1]` or on full
    dataset. Applied to every factor.

12. **Lifecycle invariant checked mid-batch, failing falsely due to
    transient `pending_dsr` entries.**
    Mitigation: invariant explicitly defined over terminal states only;
    checked exclusively at batch close after D9 finalization; blueprint
    rule prohibits mid-batch invariant assertions.

13. **Disjoint train-window metrics misinterpreted as continuous equity
    curve.**
    Mitigation: v2 authoritative aggregation rule is mean/sum across window
    summaries; no stitched continuous series; per-window rows remain
    available for inspection.

---

## Implementation Notes for Claude Code

**Sequential deliverable discipline** (same as Phase 1):

Phase 2A:
1. D1 Factor Library — ship and sign off, no dependencies
2. D2 DSL + Compiler — depends on D1
3. D3 Hypothesis Hash — depends on D2
4. D4 Regime Holdout — depends on registry schema changes
5. D5 Baselines in DSL — SIGN-OFF GATE for 2A

Phase 2B (only after 2A signed off):
6. D6 Proposer — depends on all of 2A
7. D7 Critic — depends on D6
8. D8 Orchestrator — depends on D6, D7
9. D9 Batch DSR + Report — depends on D8 completing a batch

Do not combine deliverables into a single prompt. Every deliverable ships with:
- Docstrings on all public functions
- `if __name__ == "__main__"` with argparse where applicable
- `--dry-run` support for anything that calls the API
- Unit tests matching the spec above
- Notebook acceptance test demonstrating end-to-end correctness before sign-off

---

## v1 → v2 Change Log

**From first-round review (13 items):**
1. Critic `refine` verdict removed (approve/reject only)
2. `hypotheses_attempted` counting rule explicitly defined
3. Leaderboard ranking: `min(train, holdout)` desc (not sign product)
4. Regime holdout: orchestrator-internal only, no general CLI
5. `feature_version` defined as SHA256 of canonical metadata + compute source
6. `crosses_above/below` must use CrossOver or explicit two-bar form
7. Spend ledger uses pre-flight charge pattern
8. Factor library: 14 core (was 20)
9. Proposer context: allow-listed fields only
10. DSL `value` str validator (must be registered factor name)
11. Crossing operators: both factor-vs-scalar and factor-vs-factor supported
12. Metric tolerance: 1e-4 (was 1e-6); total_trades exact
13. Regime holdout via independent `run_backtest` call (not equity slicing)

**From second-round review (6 items from ChatGPT, 2 from Gemini):**
14. DSL complexity budget enforced at schema level
15. Factor NaN policy: NaN only before warmup; post-warmup NaN is build failure
16. Compiler dispatches by operand type (factor-vs-scalar vs factor-vs-factor
    in separate code paths with independent tests)
17. Proposer context token budget: ≤ 2000 tokens, ≤ 3 examples, no raw metrics
18. Hypothesis lifecycle states formalized (8 terminal states)
19. Leaderboard ranking rule in authoritative blueprint text (not review reply)
20. Proposer and Critic both use Sonnet (Haiku reserved for Phase 2.5)
21. Regime holdout passing criteria quantified (4 AND conditions)

**Author additions (2 items):**
22. Compilation manifest per hypothesis_hash for research reproducibility
23. Batch report as D9 deliverable (not post-hoc nicety)

**Precision corrections:**
- DSR threshold described as "expected max Sharpe under null" not as DSR
- Float canonicalization via `f"{:.6f}"` format, not `round()` or `Decimal`
- Warmup auto-alignment called out in D2 Hard Constraints (was buried in
  method signature in v1)

**Final precision pass (10 additional items):**

*Author-identified during self-review:*
24. `pending_dsr` formally separated from terminal states; transient
    orchestration state
25. Lifecycle invariant `sum(terminal_counts) == hypotheses_attempted`
    enforced at batch close only, not mid-batch
26. Monthly budget boundary defined as UTC calendar month (not rolling 30-day)
27. Theme rotation algorithm fixed as `themes[(k-1) % len(themes)]` 1-indexed
    round-robin

*ChatGPT third-round additions:*
28. Train-window aggregation semantics for disjoint windows (mean/sum of
    per-window summaries; NO equity-curve stitching)
29. Factor compute functions must be top-level named callables (no lambdas
    or nested functions, for `inspect.getsource` stability)
30. Compilation manifest drift defined explicitly (4 fields: canonical DSL,
    compiler SHA, factor list snapshot, feature_version); drift raises
31. D9 is sole finalization authority for `pending_dsr → shortlisted/dsr_failed`

*Gemini third-round additions:*
32. D1 Hard Constraint: factors must be **causal-only**; prohibited list of
    vectorization escape hatches (`.mean()`, `.std()`, `shift(-k)`, `bfill`,
    unbounded `expanding()`). Forensic "future bar invariance" test added.
33. D3 test renamed/added: `test_logical_equivalence_same_hash` with explicit
    SMA+RSI reorder example, documenting the commutative-AND dedup attack
    surface that canonical sorting closes.

*Author-identified during Gemini review (related to item 32):*
34. `build_features.py` must compute over FULL dataset; subsetting happens
    at consumption layer (engine `fromdate`/`todate`), never at production
    layer. No CLI flag may restrict output date range.
