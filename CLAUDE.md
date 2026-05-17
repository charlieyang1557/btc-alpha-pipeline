# CLAUDE.md — BTC Alpha Pipeline


## Quick navigation

- Project info: §What This Project Is / §Tech Stack / §Project Structure
- Hard rules: §HARD CONSTRAINTS / §Execution Convention
- Current state: §Phase Marker (current phase only)
- Extended references:
  - Sealed phase history: [docs/phase_marker_history.md](docs/phase_marker_history.md)
  - Phase-specific execution rules (Backtrader, Factor parquet, Phase 2 DSL/Agent/Budget, Raw payload, Library policy): [docs/rules/phase_execution_rules.md](docs/rules/phase_execution_rules.md)
  - Methodology discipline: [docs/discipline/METHODOLOGY_NOTES.md](docs/discipline/METHODOLOGY_NOTES.md)

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

## Phase-specific execution rules

Phase-specific execution rules (Backtrader-specific configuration, Factor parquet rules, Phase 2 DSL/Agent/Budget rules, Raw payload audit retention, Library policy) are at [docs/rules/phase_execution_rules.md](docs/rules/phase_execution_rules.md). Canonical HARD CONSTRAINTS section below remains authoritative.

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

- **Current phase:** Path 3 methodology consolidation execute cycle Pass 1 (per-candidate judgment register) **SEALED** at Pass 1 SEAL register-event boundary (canonical artifact at [`docs/path3/PATH3_EXECUTE_PASS1_DECISIONS.md`](docs/path3/PATH3_EXECUTE_PASS1_DECISIONS.md) sealed at this Path 3 execute Pass 1 SEAL commit `244378c` + this Phase Marker advance commit; 431 lines / 8 main §§ (§0 cycle metadata + Gate registration chain through session 1-3 V# verification + ChatGPT precision rule scope at Pass 1 + §1 cycle parameters Q1-Q6 inherited from cycle plan + §2 per-candidate disposition table 43 candidates × 9-field canonical schema §2.1-§2.6 with in-cycle refinements paragraph + §3 high-confidence ADOPT subset summary 25 candidates with §3.1 eligibility roster + §3.2 Pass 2 work forecast per-class fire count with tier distribution column + §3.3 R3-alt outcome-monitoring self-check + §4 lower-confidence ADOPT → DEFER subset 9 candidates + §5 PUSHBACK subset 7 candidates with §5.1 asymmetry clarification intro + §6 V# anchor chain V1-V14 verified CLEAN at Gate 5 re-fire post-Gate-4-errata + §7 reserved decisions per anti-pre-emption invariant + §8 Pass 1 outcome summary). **Outcome distribution:** ADOPT high-confidence 25 (58%; Medium tier 6 first-cycle-use + §31-style light append 18 + cross-reference disposition 1 §6 extension) + DEFER 9 (21%; Path 3.x escalation) + PUSHBACK 7 (16%; reasoned rejection with sharpened symmetry reasoning per Gate 4 E3) + ROUTE-ONLY 2 (5%; Class D out-of-Path-3-codification-scope) = 43 total; NO tag at Pass 1 SEAL per cycle-internal SEAL precedent (cycle-internal SEAL, not arc-level — matches Phase 5 sub-spec + Path 3 scoping/sub-spec cross-cycle precedent). **Cycle scope:** Path 3 execute cycle = methodology consolidation cycle execute phase (per-candidate decision register at Pass 1 this SEAL; codification text fire register at Pass 2 pending separate Charlie register-event boundary at Gate 8 per plan §9.8 anti-momentum-binding mandatory separation). Pass 1 deliverable per ChatGPT precision rule §4.4: per-candidate ADOPT/DEFER/PUSHBACK disposition + tier (Weak / Medium / §31-style; Strong EXCLUDED per sub-spec §3.1) + target-§ within candidate-class eligibility + register-class (in-repo / out-of-repo per plan §9.10 R8 discipline lock) + confidence flag (high / lower per plan §3.3 3-AND-conjunction criteria) — final codification text reserved for Pass 2. **(a'') 2-batch × (a') per batch pacing:** Batch 1 = Pass 1 judgment register this SEAL (session 1-1 draft 393 lines via writing-plans skill cycle plan @ `/tmp/path3_execute_cycle_plan_2026-05-16.md` 626 lines + session 1-2 reviewer routing 3 rounds + session 1-3 V# verification + Gate 4-errata V5 reassignment + Gate 5 V# re-fire 14/14 CLEAN + Gate 6 SEAL fire); Batch 2 = Pass 2 codification register pending separate Charlie register at Gate 8 Pass 2 entry boundary. **8 Charlie register fires across Pass 1 cycle through SEAL:** Gate 1 cycle entry "path1 authorized" + Gate 1.5 Q-disposition "authorized on convergence" (Q1-Q6 3-leg convergent composite) + Gate 2 plan ratification "Approve with refinement by both reviewer" (8 refinements ADOPTED R1+R2+R3+R3-alt+R5+R8+Obs1+Obs4 incl. §9.10 in-repo vs out-of-repo discipline lock + §3.2 9-field schema) + Gate 3 reviewer routing "Do we have convergence? authorize if converged" (conditional convergence-test; 3-leg convergent on routing scope refinement met → 2-leg routing per Q3 (a); Codex SKIP per sub-spec §4.6) + Gate 4 edit application "Path β ratified" (Path β chosen over Path α via 3-round routing convergence on ChatGPT hidden-criterion-4 avoidance argument: Path α would implicitly codify unstated 'reviewer convergence' criterion via adjudication precedent; Path β preserves explicit-criteria primacy per sub-spec §3.2 D1.b strict reading; 5 Medium tier promotions C16/C17/C40/C41/C42 + E2-E6 + E1c reclassification + E1e C40 target-§; E6 cycle plan §10.3 deferred to separate plan-errata register-event per Gate 5 strict scope reading) + Gate 4-errata "authorize on convergence" (3-leg convergent Path α-1 V5 reassignment: C24 → METHODOLOGY_NOTES §6 commit-messages canonical-result-layer extension cross-ref; C12 → METHODOLOGY_NOTES new §33 Medium tier 6th promotion; ChatGPT + Claude advisor + Leg-C convergent on advisor-friendly leans) + Gate 5 V# verification "Authorize gate 5 — V# verification fire on Pass 1 SEAL doc only" (initial fire caught V5 FAIL on C24+C12 per sub-spec §2.3 Class C eligibility list does not include §31-style light append; HARD STOP SEAL fire per plan §5.1 binding; re-fire post-Gate-4-errata edits V# 14/14 CLEAN) + Gate 6 SEAL fire "approve on convergence" (Pass 1 SEAL bundle: commit 1 `244378c` Pass 1 SEAL doc seal + commit 2 this Phase Marker advance with Option 1A atomicity to history file 3rd empirical trigger + push + NO tag). Gate 4-errata is errata register-event distinct from Gate 4 main fire per chain-trust register boundary discipline; Gate 5 V# re-fire part of Gate 4-errata authorized bundle. **Adjudication register at SEAL:** Charlie register chain 8 fires across cycle ("path1 authorized" → "authorized on convergence" Q-disposition → "Approve with refinement by both reviewer" → "Do we have convergence? authorize if converged" → "Path β ratified" → "authorize on convergence" Gate-4-errata → "Authorize gate 5" → "approve on convergence" Gate 6); reviewer cycles cumulative = ChatGPT structural-overlay (Leg-C; 3 rounds with 9 L# findings + Round-3 hidden-criterion-4 methodological argument decisive in Path β + V5 catch ratification + Gate 4-errata reassignment lean) + Claude advisor full-prose-access (Leg-D; 3 rounds with 14 F# findings + 2 self-PUSHBACK instances on C40 disposition + V5 catch ratification + C12 Medium tier subdivision lean); Codex SKIPPED per [`feedback_codex_review_scope.md`](.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md) process/spec deliverable register-class hard rule; python-reviewer SKIPPED (no code at Pass 1); per-fix adjudication operated throughout per [`feedback_reviewer_suggestion_adjudication.md`](.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) (no bulk-accept). **Sub-spec §4.5 atomicity binding empirical 3rd trigger:** this Phase Marker advance commit atomically updates `docs/phase_marker_history.md` with 1 new summary-table row (Path 3 execute Pass 1 SEAL current advance row) + 1 verbatim prior-phase block (Path 3 sub-spec drafting cycle SEALED demoted at this advance); commit 2 `git diff --stat` shows BOTH `CLAUDE.md` AND `docs/phase_marker_history.md` per Option 1A binding ([`feedback_claude_md_freshness.md`](.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md)); 1st empirical trigger at `578df13` (Path 3 scoping SEAL), 2nd at `0835805` (Path 3 sub-spec drafting SEAL), 3rd at this advance — Option 1A binding cross-cycle robustness now 3-instance validated; 4th forecast at Pass 2 SEAL Phase Marker advance. **9 forward-only carry-forward observation categories accumulated** (out-of-Q5-scope per strict reading; logged in conversation history; eligible at separate Charlie register-event boundary): 5 from prior cycle (a' three-session pacing cross-register-class validation 2 instances + advisor-vs-Leg-C lean-reversal symmetric pattern 6 instances + Gate 7 handoff prompt write codification candidate + reviewer mid-flight self-revision pattern + cross-leg convergence as Gate 4 priority signal + reviewer-proposed-edit-introduces-new-problem sub-pattern) + 2 added at Gate 2 (#6 out-of-repo memory file audit register pattern at SEAL fires + #7 per-candidate disposition table 9-field canonical schema as methodology consolidation cycle artifact register) + 1 added at §6 V4 note initial Pass 1 SEAL draft (#8 first-codification-cycle tier-class distribution pattern — register-class-coherence vs strict-tier-criteria-application tension; reframed post-Gate-4 per F8) + 1 added at Gate 4-errata V5 catch (#9 sub-spec §2.3 Class C eligibility list completeness gap — §31-style light append not listed at Class C despite §3.4 "most classes are eligible" framing; sub-spec errata register-event candidate at future Charlie register-event boundary). **Path β outcome — first cycle to use Medium tier:** 6 candidates promoted (C12 V# anchor verification chain @ new §33 + C16 SEAL bundle composition @ new §32 + C17 tag policy @ §32 sub-§ + C40 anti-momentum-binding @ §10 sub-§ + C41 anti-pre-naming @ §10 sub-§ + cross-ref to memory rule + C42 eligible-not-named successor framing @ §10 sub-§) — sub-spec §3.2 Medium tier framework first operational validation; ChatGPT 'hidden criterion 4' avoidance argument decisive in Path β. Pass 2 fire scope forecast = 25 fires across target-§ types {new §32 + new §33 + §10 sub-§§ + §6 extension + §31 light append cluster}; §32-§33 SEAL-discipline cluster forming + §10 authorization-preservation cluster forming. **Active next action:** Gate 7 Pass 1 SEAL handoff write authorized at this SEAL register-event (Charlie register precedent "a authorized" at Gate 7 of prior cycle); Pass 2 entry register-event boundary separate Charlie register required at Gate 8 per plan §9.8 anti-momentum-binding mandatory separation (Pass 1 SEAL does NOT pre-authorize Pass 2 entry); other successor paths (Path 3.x continuation if DEFER subset substantive / Phase 5.1+ cost-model investigation eligible per sealed Phase 5 §4a NOT pre-committed / pre-existing noise cleanup / pct_change() deprecation patch / forward-only carry-forward codification register-event for 9 accumulated categories / sub-spec errata register-event for Class C eligibility gap / E6 cycle plan §10.3 plan-errata register-event / pause / other Charlie-specified) eligible at separate Charlie register-event boundary. Three Phase 5 narration authorities at `4b9e2dc` remain discharged — Path 3 execute cycle Pass 1 does NOT re-narrate (C14 ADOPT high-confidence at §31-style light append enumerates discharge pattern without re-narrating specific narrations). Push timing at this commit: 2 commits at this Path 3 execute Pass 1 SEAL bundle (Pass 1 SEAL doc seal commit `244378c` + this Phase Marker advance commit with atomic history file update; pushed together; NO tag per cycle-internal SEAL precedent).

**Sealed phase history**: full historical detail at [docs/phase_marker_history.md](docs/phase_marker_history.md). Compact summary of 5 most recent prior register-events:

| Phase / Arc | Seal commit | Closeout / canonical artifact | Tag |
|---|---|---|---|
| Path 3 methodology consolidation sub-spec drafting cycle SEAL | `a5cb4a0` (+ Phase Marker advance `0835805`) | [`docs/path3/PATH3_METHODOLOGY_CONSOLIDATION_SUBSPEC.md`](docs/path3/PATH3_METHODOLOGY_CONSOLIDATION_SUBSPEC.md) | — |
| Path 3 methodology consolidation scoping cycle SEAL | `6750274` (+ Phase Marker advance `578df13`) | [`docs/path3/PATH3_METHODOLOGY_CONSOLIDATION_SCOPING_DECISION.md`](docs/path3/PATH3_METHODOLOGY_CONSOLIDATION_SCOPING_DECISION.md) | — |
| Phase 5 diagnostic execution arc-level closeout SEAL | `54ba912` (+ Phase Marker advance `4b9e2dc`) | [`docs/closeout/PHASE5_RESULTS.md`](docs/closeout/PHASE5_RESULTS.md) | `phase5-diagnostic-execution-v1` |
| Phase 5 sub-spec drafting cycle SEAL | `49ae7e3` (+ Phase Marker advance `cd82582`) | [`docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md`](docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md) | — |
| Phase 5 entry scoping cycle SEAL | `697c26b` | [`docs/phase5/PHASE5_SCOPING_DECISION.md`](docs/phase5/PHASE5_SCOPING_DECISION.md) | — |

- **Active blueprint:** `blueprint/PHASE2_BLUEPRINT.md` (v2; **freshness note** added at top per Option B at commit `3a554fb` documenting D9 + post-D9 evaluation framework supersession by PHASE2C_3-9 arc series; CLAUDE.md Phase Marker remains operational source of truth)
- **Current batch_id:** `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` (Phase 2C Phase 1 walk-forward; corrected-engine re-run in `_corrected/` directory is canonical; same batch consumed by PHASE2C_6 single-regime evaluation runs at `data/phase2c_evaluation_gate/{smoke,primary,audit}_v1/`, by PHASE2C_7.1 multi-regime evaluation runs at `data/phase2c_evaluation_gate/{audit_2024_v1, audit_2024_v1_filtered, comparison_2022_vs_2024_v1}/`, and by PHASE2C_8.1 extended multi-regime evaluation runs at `data/phase2c_evaluation_gate/{eval_2020_v1, eval_2020_v1_filtered, eval_2021_v1, eval_2021_v1_filtered, audit_v1_filtered, comparison_2022_2024_2020_2021_v1}/`)
- **Current UTC-month spend (April 2026):** ~$8.65 (D7 Stage 2d $5.89 + Phase 2C Batch-1 $2.30 + smoke and dry-run batches; per `agents/spend_ledger.db` `ledger` table, queried 2026-04-26; PHASE2C_6 + PHASE2C_7.1 + PHASE2C_8.1 evaluation work incurred no API spend — local backtest evaluation only)
- **Hard rule for any future WF-consuming work:** must consume corrected artifacts only and call `backtest.wf_lineage.check_wf_semantics_or_raise()` before computing derived metrics from walk-forward summaries. For single-run holdout artifacts (PHASE2C_6 attestation domain `single_run_holdout_v1`), use the companion guard `backtest.wf_lineage.check_evaluation_semantics_or_raise()`. See [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md) Section RS for the corrected-engine consumption discipline that governs both attestation domains.

## Project-discipline notes

Standing project-discipline principles (apply across all work cycles, not bound to a phase) are codified at [`docs/discipline/METHODOLOGY_NOTES.md`](docs/discipline/METHODOLOGY_NOTES.md). Seven principles currently in force: §1 empirical verification for factual claims, §2 meta-claim verification discipline, §3 regime-aware calibration bands, §4 scale-step discipline for empirical evaluations, §5 precondition verification for structural and organizational principles, §6 commit messages are not canonical result layers, §7 asymmetric confidence reporting on multi-sample claims. §8 is the synthesis "How to apply these principles" section. The §4-§7 additions were codified during the PHASE2C_6 evaluation gate arc (commit `536f737`). Future cycles append new lessons as additional sections.

## Parked branches

Branches containing completed-but-not-yet-merged work are registered at [`docs/parked/PARKED_BRANCHES.md`](docs/parked/PARKED_BRANCHES.md), with activation trigger conditions and pre-merge verification checklist per parked branch. Currently parked: `phase2.5/bandit-dedup` (factor bandit Track A + semantic dedup Track B; combined Option-1 Path-3-style cycle authorized 2026-05-16; awaiting batch cadence resumption per Concern 1 isolation strategy).
