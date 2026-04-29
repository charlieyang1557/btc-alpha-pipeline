# CLAUDE.md — BTC Alpha Pipeline

## What This Project Is

A single-person quantitative research system for BTC algorithmic trading strategies.
Built in phases: data infrastructure → backtesting → AI-assisted strategy mining → paper trading → live.

**Current status:** Phase 2A in progress — building AI-free infrastructure (factor
library, DSL compiler, hypothesis hash, regime holdout integration) in preparation
for AI-assisted strategy mining in Phase 2B.

**Completed phases:**
- Phase 0: Data infrastructure (validated BTC 1h data from 2020-01 onward)
- Phase 1A: Single-run Backtrader engine with 7bps effective cost model
- Phase 1B: Walk-forward orchestration + 4 baseline strategies + heuristic DSR

## Tech Stack

- **Python 3.11+** with dependencies pinned in `pyproject.toml`
- **Parquet** for all time-series market data (research layer)
- **SQLite** for experiment registry, paper trading state, and spend ledger (operational layer)
- **CCXT** for exchange API access (incremental data updates, future live trading)
- **Binance Vision** for bulk historical data download
- **Backtrader 1.9.78+** for event-driven backtesting
- **scipy** for statistical computations (Sharpe ratio, etc.)
- **matplotlib** for equity curve visualization (optional, debugging only)
- **pydantic v2** for DSL schema validation (Phase 2+)
- **Claude API via `anthropic` SDK** — Sonnet for both Proposer and Critic in Phase 2.
  Haiku is NOT used in Phase 2 (reserved for potential Phase 2.5 semantic dedup)

## Project Structure

```
btc-alpha-pipeline/
├── config/              # Execution conventions, date splits, schemas (IMMUTABLE by agents)
├── data/
│   ├── raw/             # Canonical current OHLCV parquet (archive/ holds snapshots)
│   ├── raw/archive/     # Pre-reconcile snapshots for reproducibility
│   ├── features/        # Precomputed factor parquet (Phase 2)
│   ├── quality/         # Auto-generated validation reports
│   ├── results/         # Per-run trade CSVs
│   ├── compiled_strategies/  # DSL compilation manifests (Phase 2)
│   └── batches/         # Batch leaderboards + auto-generated reports (Phase 2)
├── ingestion/           # Download, update, reconcile, validate scripts
├── backtest/            # Engine, metrics, experiment registry, trade audit
│   ├── bt_parquet_feed.py      # Parquet → Backtrader data adapter
│   ├── execution_model.py      # Reads execution.yaml, configures Cerebro
│   ├── slippage.py             # SlippageModel (effective 7bps for Phase 1-2)
│   ├── engine.py               # Single-run + walk-forward + regime holdout
│   ├── metrics.py              # Sharpe, drawdown, trade stats
│   ├── trade_audit.py          # Manual trade verification helper
│   ├── experiment_registry.py  # SQLite experiment tracking
│   ├── evaluate_dsr.py         # Heuristic multiple-testing screen + batch DSR
│   ├── batch_report.py         # Auto-generated batch reports (Phase 2)
│   └── experiments.db          # Auto-populated by engine
├── strategies/
│   ├── template.py             # Base strategy class
│   ├── baseline/               # Hand-written baselines (Phase 1)
│   ├── dsl.py                  # DSL pydantic schema (Phase 2)
│   ├── dsl_compiler.py         # DSL → Backtrader strategy class (Phase 2)
│   └── dsl_baselines/          # Baselines re-expressed in DSL (Phase 2A gate)
├── factors/             # Feature computation (Phase 2)
│   ├── registry.py             # FactorRegistry + feature_version governance
│   ├── build_features.py       # Full-dataset factor parquet builder
│   ├── returns.py
│   ├── moving_averages.py
│   ├── volatility.py
│   ├── momentum.py
│   ├── volume.py
│   └── structural.py
├── agents/              # AI hypothesis + strategy generation (Phase 2B)
│   ├── hypothesis_hash.py      # Canonical DSL hash + dedup (Phase 2A D3)
│   ├── proposer/               # Phase 2B D6 — Proposer agent (stub + Sonnet)
│   │   ├── interface.py        # ProposerBackend Protocol + I/O schemas
│   │   ├── stub_backend.py     # Deterministic stub backend (Stage 1)
│   │   ├── sonnet_backend.py   # Live Sonnet backend (Stage 2a+)
│   │   ├── prompt_builder.py   # Prompt construction + leakage audit helpers
│   │   └── stage2a_smoke.py    # Single-hypothesis smoke run script
│   ├── orchestrator/           # Phase 2B D8 — main batch loop
│   │   ├── ingest.py           # ProposerOutput → lifecycle state assignment
│   │   └── budget_ledger.py    # Crash-safe pre-charge SQLite ledger
│   ├── critic/                 # Phase 2B D7 — Critic module (rule gate + LLM)
│   │   ├── __init__.py         # Public API: CriticResult, run_critic, BatchContext
│   │   ├── result.py           # Frozen CriticResult dataclass + serialization
│   │   ├── batch_context.py    # BatchContext dataclass + theme constants
│   │   ├── d7a_feature_extraction.py  # DSL feature extraction primitives
│   │   ├── d7a_rules.py        # Deterministic D7a scoring rules (4 axes)
│   │   ├── d7b_backend.py      # Abstract D7bBackend protocol
│   │   ├── d7b_stub.py         # StubD7bBackend (all scores 0.5)
│   │   ├── d7b_live.py         # LiveSonnetD7bBackend (Stage 2a+, own Anthropic client)
│   │   ├── d7b_prompt.py       # D7b prompt template + leakage audit
│   │   ├── d7b_parser.py       # D7b response parser + forbidden-language scan
│   │   ├── replay.py           # Replay reconstruction from Stage 2d artifacts
│   │   └── orchestrator.py     # run_critic() orchestrator + reliability fuse
│   └── spend_ledger.db         # SQLite file owned by orchestrator/budget_ledger.py
├── risk/                # Position sizing and capital allocation (Phase 3+)
├── paper_trading/       # Simulated live execution (Phase 4)
├── tests/               # Automated test suite
└── live/                # Real money execution (Phase 5+)
```

## Document Conflict Priority

If any two documents in this project contradict each other, resolve by this hierarchy (highest priority first):

1. **`config/execution.yaml`** — execution semantics and fee assumptions
2. **`config/environments.yaml`** — date splits and research discipline (now at `v2` with regime holdout)
3. **`config/schemas.yaml`** — column definitions and validation rules
4. **`CLAUDE.md`** (this file) — hard constraints and prohibitions
5. **`data_dictionary.md`** — human-readable schema reference
6. **`PHASE2_BLUEPRINT.md`** (v2) — Phase 2 implementation plan (current phase)
7. **`PHASE1_BLUEPRINT.md`** — Phase 1 reference (completed)
8. **`PHASE0_BLUEPRINT.md`** — Phase 0 reference (completed)

Structured config files are the machine-readable source of truth. This file governs behavior and prohibitions but does not outrank the actual config values. If you encounter a conflict, follow the higher-priority document and flag the inconsistency in a code comment.

## Execution Convention (CRITICAL — READ BEFORE WRITING ANY STRATEGY CODE)

All backtests in this project follow these rules without exception:

1. **Signal timing:** Signals are computed using data available at bar N's close.
2. **Execution timing:** Orders execute at bar N+1's open price. NEVER at bar N's close.
3. **No same-bar execution:** A strategy CANNOT observe a bar's close and execute at that same bar's close. This is look-ahead bias.
4. **Cost model (Phase 1-2):** Effective cost = **7bps per side** (14bps round trip). This is a simplification of 4bps taker fee + 3bps slippage. Do NOT treat this as a realistic execution simulator — it is an effective cost model for baseline validation. The `fee_model` registry field must be `"effective_7bps_per_side"`. Upgrading to a volatility-scaled slippage model is deferred to Phase 3.
5. **Stop/limit orders within a bar:** If both stop-loss and take-profit would trigger within the same OHLCV bar, assume the adverse one triggers first (conservative).
6. **Zero-volume fill deferral:** If the designated fill bar has `volume == 0`, defer execution to the next bar with `volume > 0`, using that bar's open price. If deferral exceeds 24 bars (24 hours), cancel the order entirely.
7. **All times are UTC.** No exceptions. No implicit local timezone conversions.

These rules are defined in `config/execution.yaml` and enforced by `backtest/execution_model.py`.

## Backtrader-Specific Rules

### Cerebro Configuration (MUST be set for every backtest run)
- `cerebro.broker.set_coc(False)` — disable cheat-on-close
- `cerebro.broker.set_coo(False)` — disable cheat-on-open
- `cerebro.broker.setcommission(commission=0.0007)` — 7bps per side effective cost
- `cerebro.broker.setcash(10000)` — default starting capital

### Common Pitfalls (Claude Code MUST avoid these)
- `self.data.close[0]` is the CURRENT bar's close — NOT the next bar's
- `self.buy()` submits a market order that fills at the NEXT bar's open — this is correct behavior, do not try to "fix" it
- `self.data.datetime.datetime(0)` returns a **naive** datetime — always convert to UTC when comparing with our data
- Backtrader's `PandasData` feed expects the DataFrame index to be datetime — set index before passing
- If `fromdate`/`todate` are timezone-naive, Backtrader may misalign with our UTC data — always use timezone-aware datetime objects
- Backtrader indicators (SMA, etc.) are **bar-based, not time-based** — a 24-period SMA averages the last 24 rows regardless of time gaps between them. This is acceptable (31 gaps in 55K bars is negligible) but must be documented.

### Warmup Handling
- Each strategy declares `WARMUP_BARS` (number of bars before signals are valid)
- The engine loads data from `start_date` but only begins recording metrics after warmup
- **No trades are allowed during the warmup period**
- Strategies must only emit signals inside Backtrader's `next()` method, NEVER in `prenext()`
- `prenext()` runs while indicators are still warming up — it must remain empty or contain only logging
- The first eligible signal bar is the first bar where `next()` is called
- The first eligible fill is the bar after that signal
- Metrics (Sharpe, drawdown, etc.) are computed ONLY on the post-warmup period
- If a strategy attempts to trade during warmup, the engine must block it
- **Phase 2 DSL compiler**: `WARMUP_BARS` is auto-set to `registry.max_warmup(factors_used)` — see D2 in `PHASE2_BLUEPRINT.md`

## Timestamp & Timezone Rules

- **ALL timestamps in code, data, logs, and configs are UTC.**
- Parquet columns: use timezone-aware `datetime64[ms, UTC]`.
- SQLite columns: store as ISO 8601 strings with `Z` suffix (e.g., `2024-01-15T08:00:00Z`).
- Column naming convention: all time columns end in `_utc` (e.g., `open_time_utc`, `ingested_at_utc`, `created_at_utc`).
- Python code: always use `datetime.now(timezone.utc)`, NEVER `datetime.now()` or `datetime.utcnow()`.
- Pandas: when reading timestamps, always pass `utc=True` or explicitly localize with `.dt.tz_localize('UTC')`.
- **NEVER mix timezone-aware and timezone-naive datetimes.** This will silently corrupt data joins and backtest alignment.
- **Phase 2 budget**: "month" is strictly a **UTC calendar month** for monthly cap purposes. A new month begins at `YYYY-MM-01T00:00:00Z`. NEVER use a rolling 30-day window for budget accounting.

## Data Rules

- `data/raw/btcusdt_1h.parquet` is the **canonical current dataset**. It is overwritten by `reconcile.py` after each update.
- Before overwriting, `reconcile.py` MUST archive the previous version to `data/raw/archive/btcusdt_1h_YYYYMMDDTHHMMSSZ.parquet`.
- Raw data is NEVER modified by any process other than `reconcile.py`. Strategies, agents, and analysis scripts read only.
- `open_time_utc` is the primary key for all OHLCV data. It must be unique and sorted ascending.
- Zero-volume bars are flagged in validation reports but NOT auto-removed. They may indicate exchange downtime or data-quality issues.
- Missing bars (gaps) are flagged but NOT auto-interpolated. Forward-filling is PROHIBITED.
- All data files include `source` ("binance_vision", "ccxt_binance", or "ccxt_binanceus") and `ingested_at_utc` columns.

## Factor Parquet Rules (Phase 2)

- `data/features/btcusdt_1h_features.parquet` is the canonical factor dataset.
- `build_features.py` computes factors over the **full available OHLCV range**. Never build for a subset; subsetting happens at the consumption layer (engine `fromdate`/`todate`).
- The parquet's pyarrow metadata stores `feature_version` and `built_at_utc`.
- `feature_version` = SHA256 of canonical registry metadata, including per-factor: name, category, warmup_bars, inputs, output_dtype, and SHA256 of compute function source (via `inspect.getsource`).
- On any downstream read, if stored `feature_version` ≠ live `compute_feature_version(registry)`, the parquet MUST be force-rebuilt. No silent "use stale data" fallback.
- Registered factor compute functions MUST be top-level named callables. Lambdas, nested functions, and dynamically-generated callables are prohibited (breaks `inspect.getsource` stability).

## Experiment Tracking

- Every backtest run MUST be logged in `backtest/experiments.db` (SQLite).
- Required fields per run: `run_id`, `run_type`, `parent_run_id`, `strategy_name`, `git_commit`, `config_hash`, `split_version`, `data_snapshot_date`, `train_start`, `train_end`, `effective_start`, `warmup_bars`, `validation_start`, `validation_end`, `test_start`, `test_end`, `initial_capital`, `final_capital`, core metrics, `fee_model`.
- **Phase 2 additional fields**: `batch_id`, `hypothesis_hash`, `regime_holdout_passed`, `lifecycle_state`, `feature_version`.
- `run_type` must be one of: `"single_run"`, `"walk_forward_window"`, `"walk_forward_summary"`, `"regime_holdout"`, `"batch_summary"`
- `fee_model` for Phase 1-2: `"effective_7bps_per_side"` — do NOT use labels that imply separate fee/slippage modeling
- `split_version` for Phase 2: `"v2"` (train = 2020-2021 + 2023; holdout = 2022; validation = 2024; test = 2025)
- The experiment registry is the system of record for all research results.

## Date Split Rules

- Train/validation/test date boundaries are defined in `config/environments.yaml`.
- These boundaries are IMMUTABLE during a research phase.
- Strategies may ONLY be trained/optimized on data within the training window.
- Validation data is for hyperparameter selection and early stopping only.
- Test data is touched ONCE for final evaluation. If you peek and iterate, it becomes validation data.
- **Phase 2 regime holdout (2022)**: an additional in-train stress test. Agents never see its results. Only hypotheses that pass `regime_holdout_passed` advance to validation. See D4 in `PHASE2_BLUEPRINT.md` for the 4-condition passing criteria.

## Phase 2 DSL Rules

- All AI-generated strategies are expressed in a pydantic-validated DSL (`strategies/dsl.py`) and compiled to Backtrader via `strategies/dsl_compiler.py`. Raw Backtrader code from agents is not accepted in Phase 2.
- **DSL complexity budget (schema-enforced):** entry/exit groups ≤ 3, conditions per group ≤ 4, `max_hold_bars` ≤ 720, `name` ≤ 64 chars, `description` ≤ 300 chars.
- **Comparison operator semantics:** `crosses_above` / `crosses_below` MUST compile to `bt.indicators.CrossOver` or an explicit two-bar form `(a[0] > b[0]) AND (a[-1] <= b[-1])`. A naive single-bar comparison is a compiler bug.
- **NaN in comparisons:** NaN on either side of a comparison evaluates to `False`. Never `True`.
- **Factor-vs-scalar and factor-vs-factor are separate compiler code paths** with independent unit tests for each operator.
- **Compilation manifest:** each compiled strategy writes `data/compiled_strategies/<hypothesis_hash>.json` with canonical DSL, compiler git SHA, factor list snapshot, and feature_version. Drift in any of these fields raises `ManifestDriftError`.

## Phase 2 Agent & Budget Rules

- **Budget caps (hard-enforced in code):** $20 per batch, $100 per UTC calendar month. Enforcement happens PRE-call (before each API invocation), not post-call.
- **Spend ledger uses pre-flight charge pattern:** write `status="pending"` row with upper-bound cost estimate BEFORE the API call; update to `status="completed"` with actual cost after. Pending rows count as spent. Crashed batches are not resumed.
- **Hypothesis lifecycle states** (8 terminal, 1 transient):
  - Terminal: `proposer_invalid_dsl`, `duplicate`, `critic_rejected`, `train_failed`, `holdout_failed`, `dsr_failed`, `shortlisted`, `budget_exhausted`
  - Transient: `pending_dsr` (orchestrator-time; resolved by D9 at batch close)
- **Invariant:** `sum(terminal_lifecycle_counts) == hypotheses_attempted`. Checked at batch close ONLY, never mid-batch.
- **`hypotheses_attempted` counting rule:** increments immediately after each Proposer call returns, regardless of validity, duplication, or Critic outcome. Unissued slots (budget exhausted before proposing) are tracked separately in `batch_summary.unissued_slots`.
- **Theme rotation:** `theme = THEMES[(k - 1) % len(THEMES)]` where k is 1-indexed batch position and THEMES is the canonical 6-theme list defined in D6.
- **Theme rotation operational boundary (Stage 2c/2d):** Current Stage 2c/2d operational rotation uses the first 5 canonical themes (`THEME_CYCLE_LEN = 5` in `agents/proposer/stage2c_batch.py` and `stage2d_batch.py`). `multi_factor_combination` remains part of the canonical theme list but is not included in the current operational rotation until separately validated. **The exclusion is operational practice, not canonical specification; canonical anchors (`THEMES` tuple in `agents/themes.py`, `expectations.md`, `blueprint/PHASE2_BLUEPRINT.md`) retain the 6-theme list.** Resolves Issue 6 of D8.4 methodology refinement (sub-arc sealed at commit `767d0e5`) as documentation-completeness + methodology-acceptance per Issue 6 candidate-resolution-layer enumeration. Option to flip to 6 themes preserved for future decision when there's a specific Phase 2C reason to want multi-factor combination strategies; flip would require small 6th-theme-only smoke batch to verify candidate quality first.
- **Train-summary aggregation for disjoint train windows (v2):** `train_sharpe` = mean of per-window Sharpes; `train_return` = mean of per-window returns; `train_max_dd` = max of per-window drawdowns; `train_total_trades` = sum. NEVER stitch disjoint train-window equity curves into a continuous series.
- **Leaderboard ranking:** after filtering to `lifecycle_state == "shortlisted"`, rank by `min(train_sharpe, holdout_sharpe)` descending. Ties broken by `train_return` descending.
- **DSR N:** always `hypotheses_attempted` from the `batch_summary` row. NEVER use `hypotheses_approved` or survivor count.
- **D9 finalization authority:** `shortlisted` and `dsr_failed` terminal states are written ONLY by D9's `finalize_batch()`. The orchestrator writes `pending_dsr` and stops.

## Raw payload audit artifact retention (permanent)

`raw_payloads/` directories referenced by signed-off Stage 2 acceptance
notebooks are audit artifacts and must not be deleted or bulk-cleaned
without explicit human approval. Currently protected batches:

- Stage 2a signed-off:              raw_payloads/batch_03d62937-dbe8-46f2-a91b-50fa5696b14e/
- Stage 2a post-patch re-smoke:     raw_payloads/batch_74a52dae-7a2e-4555-b773-c95f2211ad9f/
- Stage 2b signed-off:              raw_payloads/batch_cd2f32ba-1984-4461-8216-1a9ac4ca2c17/
- Stage 2c signed-off:              raw_payloads/batch_e07f34a2-b532-4f35-a9f3-af97a5a96f1f/

New acceptance batches are added here as they sign off. Claude Code
must not include these paths in any cleanup operation.

---

## HARD CONSTRAINTS — THINGS CLAUDE CODE MUST NEVER DO

These are non-negotiable rules. Violating any of these invalidates research results.

### Data Integrity
- ❌ NEVER modify `config/environments.yaml` (date splits are immutable)
- ❌ NEVER modify `config/execution.yaml` without explicit human approval
- ❌ NEVER write to `data/raw/btcusdt_1h.parquet` from any script other than `reconcile.py`
- ❌ NEVER forward-fill missing bars or interpolate prices
- ❌ NEVER silently drop or filter rows from raw data
- ❌ NEVER auto-remove zero-volume bars (flag only)

### Execution Integrity
- ❌ NEVER assume same-bar execution (signal on close, execute on same close)
- ❌ NEVER hardcode transaction costs in strategy code — read from execution.yaml
- ❌ NEVER write strategies that access future data (no `shift(-1)` on price data for signals)
- ❌ NEVER use test-set performance to modify strategy parameters
- ❌ NEVER set `cheat_on_close=True` or `cheat_on_open=True` in Backtrader Cerebro
- ❌ NEVER fill orders on zero-volume bars — defer to next valid bar
- ❌ NEVER allow trades during the warmup period
- ❌ NEVER compute metrics (Sharpe, drawdown, etc.) including the warmup period
- ❌ NEVER use Backtrader's naive datetimes without converting to UTC for comparisons

### Factor & Vectorization Integrity (Phase 2)
- ❌ NEVER use global aggregations (`.mean()`, `.std()` on full series) in factor compute functions — use `.rolling(N)` or `.ewm(span=N, adjust=False)` only
- ❌ NEVER use future-touching operations in factors: `shift(-k)`, `bfill`, `fillna(method='bfill')`, unbounded `expanding()` without a minimum constraint that excludes future bars
- ❌ NEVER register a factor as a lambda, nested function, or dynamically-generated callable — top-level named functions only
- ❌ NEVER build factor parquet for a subset of dates — always full dataset; subsetting is a consumption-layer concern
- ❌ NEVER read a factor parquet whose stored `feature_version` mismatches the live registry hash — force rebuild instead
- ❌ NEVER modify a docstring and expect `feature_version` to change — docstrings are excluded from the hash

### DSL Compiler Integrity (Phase 2)
- ❌ NEVER translate `crosses_above` / `crosses_below` as a naive single-bar comparison; must use `bt.indicators.CrossOver` or explicit two-bar form
- ❌ NEVER merge factor-vs-scalar and factor-vs-factor into a single code path — they are separate with independent tests
- ❌ NEVER let NaN in a comparison evaluate to `True` or short-circuit; NaN is always `False`
- ❌ NEVER add a compiler special case for a specific baseline; if DSL cannot express a baseline, revise the DSL schema instead
- ❌ NEVER silently regenerate a compilation manifest on drift; drift raises and requires explicit human-acknowledged regeneration
- ❌ NEVER allow a DSL to compile to a strategy that uses negative shifts or intrabar reads of close

### AI Agent & Prompt Integrity (Phase 2)
- ❌ NEVER include validation (2024), test (2025), or regime-holdout (2022) metrics/data in any prompt context sent to an LLM, even after the fact
- ❌ NEVER include raw per-hypothesis numeric results (Sharpe, return, drawdown) in Proposer context — only aggregate stats and DSL-only examples
- ❌ NEVER use Haiku for Critic in Phase 2 — Critic requires Sonnet-level reasoning
- ❌ NEVER bypass the Critic — all approved hypotheses must pass through it
- ❌ NEVER let `overfitting_risk_score >= 4` produce an `approve` verdict — force reject in orchestrator code
- ❌ NEVER implement a Critic `refine` verdict in Phase 2 (v2 removed it; reconsider for Phase 2.5 if needed)

### Budget & Lifecycle Integrity (Phase 2)
- ❌ NEVER modify `agents/spend_ledger.db` from any script other than the orchestrator
- ❌ NEVER interpret "month" as a rolling 30-day window — strictly UTC calendar month
- ❌ NEVER perform a budget check AFTER an API call (must be pre-call)
- ❌ NEVER resume a batch that was marked `crashed` in the ledger
- ❌ NEVER use `hypotheses_approved` as N for DSR — always `hypotheses_attempted` from batch_summary
- ❌ NEVER assign `shortlisted` lifecycle state outside D9's `finalize_batch()`; orchestrator writes `pending_dsr` and stops
- ❌ NEVER check the lifecycle invariant mid-batch; it only holds at batch close
- ❌ NEVER stitch disjoint train-window equity curves into a single continuous series for metric computation

### Regime Holdout Integrity (Phase 2)
- ❌ NEVER expose a general-purpose CLI for regime holdout execution — orchestrator-internal only
- ❌ NEVER let the Proposer or Critic see regime holdout results in any form
- ❌ NEVER include 2022 bars in any walk-forward training window
- ❌ NEVER mark `regime_holdout_passed = True` unless ALL four criteria are met: `sharpe >= -0.5 AND max_dd <= 0.25 AND total_return >= -0.15 AND total_trades >= 5`

### Critic Integrity (Phase 2 D7)
- ❌ NEVER let `run_critic()` raise an exception — all failures are captured in `critic_status` codes
- ❌ NEVER modify D7a rule score formulas without updating the edge behavior table in `test_d7a_rules.py`
- ❌ NEVER let D7a rule scores fall outside `[0.0, 1.0]` or use more than 4 decimal places
- ❌ NEVER return `d7a_rule_scores = {k: 0.0}` when the score is unknown — use `None` for unknown, `0.0` for measured-as-bad
- ❌ NEVER enforce the reliability fuse in Stage 1 — `CRITIC_RELIABILITY_FUSE_ENFORCED` must remain `False` until Stage 2
- ❌ NEVER add critic_result to per-call records when `with_critic=False` — output must be byte-identical to pre-D7 behavior
- ❌ NEVER let the critic influence `approved_examples` window — critic annotates only, never filters
- ❌ NEVER enable prompt caching for D7b calls — this is a CONTRACT BOUNDARY (locked at Stage 2a)
- ❌ NEVER retry D7b content-level errors (malformed JSON, schema violation, refusal) — zero retries; these are forensic signals
- ❌ NEVER let D7b live backend share the D6 Proposer's `anthropic.Anthropic()` client — separate client is a CONTRACT BOUNDARY
- ❌ NEVER modify D7b prompt template wording without a new locked decision — frozen within a Stage 2 run
- ❌ NEVER omit `backend_kind` or `call_role` from `write_pending()` — both are required with no defaults
- ❌ NEVER co-mingle dry-run artifacts with production `raw_payloads/` — use `dryrun_payloads/` with physical isolation

### Code Quality
- ❌ NEVER generate a factor/indicator function without a docstring specifying: inputs, computation method, warmup period, output schema, and null policy
- ❌ NEVER skip validation steps when ingesting or updating data
- ❌ NEVER commit code that doesn't pass existing tests

### Library Policy
**Approved core libraries (Phase 0-1):** pandas, numpy, pyarrow, ccxt, requests, pyyaml, backtrader, scipy, matplotlib, and Python stdlib modules (sqlite3, pathlib, argparse, logging, hashlib, datetime, json, zipfile, io, uuid, typing, inspect).

**Approved Phase 2 additions:** `anthropic` (Claude API), `pydantic ~= 2.0` (DSL schema validation).

Any library not listed above requires explicit human approval before use. Standard typing/testing utilities (e.g., `dataclasses`, `typing_extensions`, `pytest`) are allowed without approval.

---

## Coding Standards

- All scripts have `if __name__ == "__main__"` with argparse
- All scripts support `--dry-run` where applicable
- All scripts log to stdout with ISO 8601 UTC timestamps
- All functions have type hints and docstrings
- All data-modifying operations are logged (what changed, row counts before/after)
- Non-zero exit code on any validation failure
- Use `pathlib.Path` for all file paths, never string concatenation
- Config loading: use a shared utility that reads YAML once and passes as dict

## Contract Markers

Three grep-discoverable comment markers document contract obligations in code:

- `CONTRACT GAP` — a test or mechanism that should exist but doesn't yet,
  with a trigger condition that will require adding it (e.g., "widening
  this Literal requires adding test_X in the same PR"). Use
  `rg "CONTRACT GAP"` to list all pending gaps.
- `CONTRACT BOUNDARY` — a deliberate separation between two mechanisms
  that look mergeable but must stay separate (e.g., D2 manifest
  canonicalization vs D3 dedup canonicalization). Mutual cross-references
  required.
- `DESIGN INVARIANT` — a non-obvious design decision that future readers
  might mistake for a bug (e.g., cross operators delay first-firable bar
  by 1). Explain the rationale at the site.

When introducing a contract obligation that can't be closed immediately,
tag it with one of these markers rather than a TODO or a checklist entry
in a separate document. Markers at the code site are self-maintaining;
external checklists are not.

Use these markers **sparingly**, for true contract obligations and
design boundaries — not for routine implementation notes. If the marker
points at something that will be fixed in the next PR, it's a regular
TODO, not a contract marker. Contract markers exist for obligations
whose trigger condition is **external to the current PR's scope**
(e.g., "when Literal X is widened", "when parallel execution is
added", "when a later phase begins"). Prefer placing the marker at the
exact code site where the invariant or future-trigger condition matters,
not at a distant wrapper or caller.

## Running the Pipeline

```bash
# Phase 0: Data management
python -m ingestion.bulk_download --pair BTCUSDT --interval 1h --start 2020-01
python -m ingestion.validators --file data/raw/btcusdt_1h.parquet --report data/quality/
python -m ingestion.incremental_update --pair BTCUSDT --interval 1h
python -m ingestion.reconcile --existing data/raw/btcusdt_1h.parquet --new data/raw/btcusdt_1h_update.parquet

# Phase 1A: Single-run backtesting
python -m backtest.engine --strategy sma_crossover --start 2024-01-01 --end 2024-12-31
python -m backtest.trade_audit --run-id <UUID> --trade-index 0 1 2
python -m backtest.experiment_registry --action list
python -m backtest.experiment_registry --action stats

# Phase 1B: Walk-forward
python -m backtest.engine --strategy sma_crossover --mode walk-forward
python -m backtest.evaluate_dsr --split-version v1

# Phase 2A: Factor library + DSL infrastructure
python -m factors.build_features --pair BTCUSDT --interval 1h
python -m factors.build_features --force-rebuild
# (DSL compiler + hypothesis hash + regime holdout have no user-facing CLI;
#  they are exercised via engine and test suite)

# Phase 2B: AI loop
python -m agents.orchestrator --batch-size 200 --max-usd 20
python -m agents.orchestrator --dry-run --batch-size 5         # mocked API end-to-end
python -m agents.orchestrator --status                          # monthly spend + recent batches
python -m backtest.evaluate_dsr --batch-id <UUID>               # finalize pending_dsr, emit leaderboard + report
```

## Known Data Characteristics

The canonical dataset (`data/raw/btcusdt_1h.parquet`) has these stable, verified properties:
- Dataset begins at **2020-01-01 00:00 UTC** and is extended via incremental CCXT updates
- **31 known missing hours** across 15 gap windows, all in 2020-2023 (historical exchange outages, verified stable across rebuilds)
- **3 known zero-volume bars** (2020-12-21, 2021-02-11, 2023-03-24) — all adjacent to gaps, all have O=H=L=C (frozen price)
- In currently validated snapshots, no gaps or zero-volume bars have been observed from 2024 onward
- All timestamps are UTC-aware and hour-aligned
- Exact row counts and source coverage boundaries change with each incremental update — check validation reports in `data/quality/` for current snapshot details

## Phase Marker (update as work progresses)

**Discipline rule:** this section must be updated in the same arc that ships any phase/stage sign-off, major closeout, or live batch fire. Stale Phase Marker misleads future work.

- **Current phase:** Phase 2C PHASE2C_9 implementation arc Step 1 active — Q-9.B mining-process retrospective (light-touch). Q-9.B substantive theme ratified at PHASE2C_9 scoping cycle adjudication via dual-reviewer convergence (ChatGPT three operational conditions + Claude advisor three carry-forward considerations) on light-touch retrospective alone with cycle-boundary semantics preserving post-Q-9.B successor scoping cycle as separate deliberation register. Spec sealed at commit `8aa1c66` ([`docs/phase2c/PHASE2C_9_PLAN.md`](docs/phase2c/PHASE2C_9_PLAN.md); 1190 lines / 48 sections). Active next action: Step 1 mining-process source review per spec §5.1 — code review of Phase 2B Proposer/Critic/theme-rotation source against canonical batch `b6fcbf86-...` raw_payloads + compiled-strategy manifests; deliverable is `docs/closeout/PHASE2C_9_RESULTS.md` §3 working draft (mechanism descriptions at file:line citation register). Per spec §3 hard scope boundaries: NO new generation, NO new evaluation, NO 198-candidate full re-analysis, NO mining-process redesign, NO statistical-significance machinery, NO calibration variation, NO Phase 3 progression scoping, NO config or code modifications, NO 2025 test split touch.
- **Completed:**
  - Phase 0, Phase 1A, Phase 1B (with corrected v2 WF baseline supplement at [`docs/closeout/PHASE1B_WF_CORRECTED_BASELINE_SUPPLEMENT.md`](docs/closeout/PHASE1B_WF_CORRECTED_BASELINE_SUPPLEMENT.md))
  - Phase 2A (D1-D5 all signed off, [`docs/closeout/PHASE2A_SIGNOFF.md`](docs/closeout/PHASE2A_SIGNOFF.md))
  - Phase 2B D6 Stage 1 (stub plumbing); D6 Stage 2 lessons learned ([`docs/closeout/PHASE2B_D6_STAGE2_LESSONS_LEARNED.md`](docs/closeout/PHASE2B_D6_STAGE2_LESSONS_LEARNED.md))
  - Phase 2B D7 Stage 1 / 2a / 2b / 2c / 2d (D7 Stage 2d signed off 2026-04-23 at [`docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md`](docs/closeout/PHASE2B_D7_STAGE2D_SIGNOFF.md))
  - Phase 2C Smoke α (Stage 2c dry-run, [`docs/closeout/PHASE2C_1_SMOKE_SIGNOFF.md`](docs/closeout/PHASE2C_1_SMOKE_SIGNOFF.md)) + β (live Sonnet, [`docs/closeout/PHASE2C_2_SMOKE_SIGNOFF.md`](docs/closeout/PHASE2C_2_SMOKE_SIGNOFF.md))
  - Phase 2C Batch 1 fire ([`docs/closeout/PHASE2C_3_BATCH1.md`](docs/closeout/PHASE2C_3_BATCH1.md))
  - Phase 2C Phase 1 walk-forward closeout ([`docs/closeout/PHASE2C_5_PHASE1_RESULTS.md`](docs/closeout/PHASE2C_5_PHASE1_RESULTS.md)) + corrected-engine erratum ([`docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`](docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md))
  - Corrected WF Engine Project Arc (engine fix at `eb1c87f`, lineage discipline at [`backtest/wf_lineage.py`](backtest/wf_lineage.py), tag `wf-corrected-v1`, sign-off at [`docs/closeout/CORRECTED_WF_ENGINE_SIGNOFF.md`](docs/closeout/CORRECTED_WF_ENGINE_SIGNOFF.md))
  - PHASE2C_6 Evaluation Gate Arc (single-regime 2022 holdout evaluation across 198 corrected-engine candidates; closeout at [`docs/closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md`](docs/closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md); plan at [`docs/phase2c/PHASE2C_6_EVALUATION_GATE_PLAN.md`](docs/phase2c/PHASE2C_6_EVALUATION_GATE_PLAN.md); Codex review-response at PHASE2C_6.7 commit; new consumer guard `check_evaluation_semantics_or_raise()` for single-run holdout attestation domain in [`backtest/wf_lineage.py`](backtest/wf_lineage.py))
  - PHASE2C_7.1 Multi-Regime Evaluation Gate Arc (Path B per PHASE2C_7.0 scoping; same 198 candidates evaluated against `validation_2024` and compared candidate-aligned to PHASE2C_6's 2022 evaluation; closeout at [`docs/closeout/PHASE2C_7_1_RESULTS.md`](docs/closeout/PHASE2C_7_1_RESULTS.md); artifacts at `data/phase2c_evaluation_gate/{audit_2024_v1, audit_2024_v1_filtered, comparison_2022_vs_2024_v1}/`; Codex review-response at PHASE2C_7.1.7 commit; closeout schema discriminator `artifact_schema_version="phase2c_7_1"`; tag `phase2c-7-1-multi-regime-v1`)
  - PHASE2C_8.0 Scoping Decision (Q-B1 selection over Q-B2/Q-B3.a/Q-B3.b/Q-B4; scoping document at [`docs/phase2c/PHASE2C_8_SCOPING_DECISION.md`](docs/phase2c/PHASE2C_8_SCOPING_DECISION.md) committed at `f223316`; established the n=4 baseline composition + Option A engine-version invariance + in-sample caveat (Concern A) framework that PHASE2C_8.1 implementation operates within)
  - PHASE2C_8.1 Multi-Regime Evaluation Gate Arc (extended; n=4 evaluation against bear_2022 + validation_2024 + eval_2020_v1 + eval_2021_v1; spec at [`docs/phase2c/PHASE2C_8_1_PLAN.md`](docs/phase2c/PHASE2C_8_1_PLAN.md) committed at `1e85d1d`; implementation arc commits `1e85d1d..8086adf` (10 commits); closeout at [`docs/closeout/PHASE2C_8_1_RESULTS.md`](docs/closeout/PHASE2C_8_1_RESULTS.md); novel artifact paths `data/phase2c_evaluation_gate/{eval_2020_v1, eval_2020_v1_filtered, eval_2021_v1, eval_2021_v1_filtered, audit_v1_filtered, comparison_2022_2024_2020_2021_v1}/`; novel schema discriminator `artifact_schema_version="phase2c_8_1"` for train-overlap regimes; verification chain at three independent layers including permanent in-repo recompute gate at `tests/test_phase2c_8_1_independent_recompute.py`; tag `phase2c-8-1-multi-regime-extended-v1`)
  - PHASE2C_9.0 Scoping Decision (Q-9.B selection over Q-9.A/Q-9.C/Q-9.D after dual-reviewer convergence + sequential-hybrid framing collapse to Q-9.B light-touch alone; scoping document at [`docs/phase2c/PHASE2C_9_SCOPING_DECISION.md`](docs/phase2c/PHASE2C_9_SCOPING_DECISION.md) committed at `3e0c99d`; established the cycle-boundary-semantics framework that PHASE2C_9 implementation operates within — PHASE2C_9 = Q-9.B alone, post-Q-9.B successor scoping cycle deferred to post-findings deliberation)
  - PHASE2C_9 Q-9.B Spec (mining-process retrospective at light-touch depth; spec at [`docs/phase2c/PHASE2C_9_PLAN.md`](docs/phase2c/PHASE2C_9_PLAN.md) committed at `8aa1c66`; D1-D6 pre-pinned decisions; 6-step sequential gating; pre-registered exit conditions Case A.1-A.4 / B.1-B.3 / C.1-C.3 with operational evidence criteria; cycle-boundary preservation language audit per Claude advisor's three carry-forward considerations; ChatGPT-caught PHASE2C_10 pre-naming blocker resolved at second-pass dual-reviewer with 23 substantive replacements + 1 forbidden-language illustration retained at §7.2)
- **Active blueprint:** `blueprint/PHASE2_BLUEPRINT.md` (v2)
- **Current batch_id:** `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` (Phase 2C Phase 1 walk-forward; corrected-engine re-run in `_corrected/` directory is canonical; same batch consumed by PHASE2C_6 single-regime evaluation runs at `data/phase2c_evaluation_gate/{smoke,primary,audit}_v1/`, by PHASE2C_7.1 multi-regime evaluation runs at `data/phase2c_evaluation_gate/{audit_2024_v1, audit_2024_v1_filtered, comparison_2022_vs_2024_v1}/`, and by PHASE2C_8.1 extended multi-regime evaluation runs at `data/phase2c_evaluation_gate/{eval_2020_v1, eval_2020_v1_filtered, eval_2021_v1, eval_2021_v1_filtered, audit_v1_filtered, comparison_2022_2024_2020_2021_v1}/`)
- **Current UTC-month spend (April 2026):** ~$8.65 (D7 Stage 2d $5.89 + Phase 2C Batch-1 $2.30 + smoke and dry-run batches; per `agents/spend_ledger.db` `ledger` table, queried 2026-04-26; PHASE2C_6 + PHASE2C_7.1 + PHASE2C_8.1 evaluation work incurred no API spend — local backtest evaluation only)
- **Hard rule for any future WF-consuming work:** must consume corrected artifacts only and call `backtest.wf_lineage.check_wf_semantics_or_raise()` before computing derived metrics from walk-forward summaries. For single-run holdout artifacts (PHASE2C_6 attestation domain `single_run_holdout_v1`), use the companion guard `backtest.wf_lineage.check_evaluation_semantics_or_raise()`. See [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md) Section RS for the corrected-engine consumption discipline that governs both attestation domains.

## Project-discipline notes

Standing project-discipline principles (apply across all work cycles, not bound to a phase) are codified at [`docs/discipline/METHODOLOGY_NOTES.md`](docs/discipline/METHODOLOGY_NOTES.md). Seven principles currently in force: §1 empirical verification for factual claims, §2 meta-claim verification discipline, §3 regime-aware calibration bands, §4 scale-step discipline for empirical evaluations, §5 precondition verification for structural and organizational principles, §6 commit messages are not canonical result layers, §7 asymmetric confidence reporting on multi-sample claims. §8 is the synthesis "How to apply these principles" section. The §4-§7 additions were codified during the PHASE2C_6 evaluation gate arc (commit `536f737`). Future cycles append new lessons as additional sections.
