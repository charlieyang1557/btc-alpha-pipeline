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

### Conservative-Anchor Gate Integrity (Phase B Tier 5/6 per R3.1d V_SEAL 2026-05-19)
- ❌ NEVER promote a candidate strategy to Phase B Tier 5 evaluation without `holdout_sharpe > 0` strict pass at `spot_realistic_15bps_v1` anchor (via `config/execution_phaseb_spot_15bps.yaml`; 15 bps/side = 30 bps round trip)
- ❌ NEVER promote a candidate strategy to Phase B Tier 6 (R6.1 promotion class) without FWER-style multiplicity correction pass — eligible instruments: Deflated Sharpe Ratio per Bailey-López de Prado 2014 (preferred); Romano-Wolf stepdown; Westfall-Young permutation FWER; heuristic DSR `sqrt(2*ln(N))` acceptable interim screen only (supersession to production-grade required before final capital commitment)
- ❌ NEVER use Benjamini-Hochberg FDR (BH-FDR) at Tier 6 — controls FDR (expected proportion of false discoveries) not FWER (probability of any false discovery); per-strategy capital commitment under this project's serial individual-allocation architecture (no cross-strategy portfolio diversification at deployment) requires FWER framework
- ❌ NEVER use Phase 1-2 `effective_7bps_per_side` results as Tier 5/6 promotion basis under formal Branch.A SPOT commitment (per R4.1 SEAL + R3.1d V_SEAL tiered Pillar 1 policy SD3-D)
- ❌ NEVER modify `config/execution_phaseb_spot_15bps.yaml` without explicit human approval (parallel rule to `config/execution.yaml` Data Integrity)
- ❌ NEVER omit `cost_anchor_id` from `experiment_registry.runs` entries on new Phase B / Tier 5 / Tier 6 runs once schema migration lands (per R3.1d §5.2; mapping table path-keyed at `execution_config_path` → `cost_anchor_id`)
- ❌ NEVER lock Tier 6 multiplicity instrument variant + threshold + N value at R3.1d V_SEAL; these are pre-committed for R6.1 V_SEAL based on cohort properties at R6.1 fire time

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

- **Current phase:** R3.1d cost-grid re-anchor cycle (R3.1d = Phase B Pre-Sequence Roadmap V3 Tier 3 cost-grid re-anchor Bucket-1 investigation note per Template B; structural analog to Phase 5.1 + 5.2 + Phase A + R1.2 + R3.1a + R4.1 SEAL cycles; fired by Charlie 2026-05-18 as register-event "1 → 3 → 4 with conservative-anchor synthesis approved, R3.1d fire authorized") **SEALED** at R3.1d V_SEAL register-event boundary (canonical R3.1d artifact at [`docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md`](docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md) sealed at R3.1d V_SEAL bundle commit `44840a3` + this Phase Marker advance commit; R3.1d = 620+ lines / 12 main §§ + cycle metadata header + §12 companion artifact appendix). **Locked sub-decisions (Charlie register chain through V_SEAL 2026-05-19):** SD1 = Option A 15 bps/side (30 bps RT) conservative anchor per Phase 5.2 §6.4 Branch.A "upper end of heuristic range" + Phase 4 PLAN §1.4 dual-source backing; SD2-D sidecar config pattern (NEW `config/execution_phaseb_spot_15bps.yaml` alias; main `execution.yaml` unchanged → preserves post-E.3 config_hash `sha256:db2ce75bd41e8513`; new `cost_anchor_id TEXT` schema column in `experiment_registry.runs` for path-based forensic discrimination per V3-PA replaces non-injective V2-P5 `fee_model_label` mapping); SD3-D tiered Pillar 1 policy (Phase 1-2 archival grandfathered at 7bps; new Tier 5/6 work at 15bps conservative anchor; new CLAUDE.md HARD CONSTRAINT "Conservative-Anchor Gate Integrity"); SD4-A bundle R4.1 hygiene patches (inline-edit class per R3.1d §5.4 precedent; stale-status strings on lines 5/42/462/498 of R4.1 doc updated to post-SEAL state); SD5-B separate register-event for R2.1 audit-criterion pre-commit; SD6-A explicit R3.1b/c non-foreclosure with Phase 4 paper-trading deployment trigger; SD7-A Bucket-1 Template B; SD8-A 2-leg subagent default; SD9 V_SEAL lock — **Tier 5 gate = Option A (`holdout_sharpe > 0` strict at 15 bps/side; effect on PHASE2C_15 cohort_a = 18/39 = 46.15% per V3 §6.7 strict-Sharpe table with verified scipy CIs)** + **Tier 6 gate (R6.1 promotion class) PRE-COMMITTED FWER-style multiplicity correction REQUIRED** — project-architecture rationale: serial individual-strategy capital commitment, no cross-strategy diversification at deployment → FWER framework. Eligible Tier 6 instruments: DSR per Bailey-López de Prado 2014 (preferred); Romano-Wolf stepdown; Westfall-Young permutation FWER; heuristic DSR `sqrt(2*ln(N))` acceptable interim screen only. **BH-FDR NOT eligible** (FDR vs FWER framework distinction — V3.5-PD correction removed earlier V2-P9 fabricated BH-FDR eligibility caught by Codex final pre-SEAL grep on R1.2; R1.2 doc contains ZERO hits for DSR/BH-FDR/FDR/Bonferroni/multiplicity terms — propagated Advisor V1 hallucination). N specification per CLAUDE.md HARD CONSTRAINT (`hypotheses_attempted` not `hypotheses_approved`). Instrument variant + threshold + N value locked at R6.1 V_SEAL. R6.1 cycle REQUIRED for Tier 6 promotion (not eligible-not-named). DSR advisory annotation at Tier 5 = eligible at R5.1 implementation cycle. **Cycle scope:** R3.1d V_SEAL = governance commitment (Tier 5 cost gate + Tier 6 multiplicity gate pre-commit) + new config file + schema migration + CLAUDE.md HARD CONSTRAINT addition + R4.1 hygiene patches. NO numeric change to existing Phase 1-2 backtest results (Pillar 1 archival preserved; new work at 15bps anchor). NO API spend (cycle = local-only). NO new data acquired. **10 Charlie register fires across R3.1d cycle through V_SEAL:** (1) cycle entry "1→3→4 with conservative-anchor synthesis approved, R3.1d fire authorized"; (2) sub-decision Round 1 reviewer dispatch; (3) PFR cross-validation dispatch; (4) "ratify all" SD1-SD9 + P1-P7 lock; (5) "fire V1 draft + dispatch reviewer round"; (6) V1 round Codex stall recovery "cancel and kill, then rerun blind lean for codex and advisor review freshly. so we can verify the hallucination issue"; (7) "Apply V2 patches + 进入 V2 reviewer round + Memory codification investigation"; (8) V2 → V3 ratify + PFR rule-Y dispatch; (9) "dispatch to reviewer round for a final review before fire seal" + manual advisor agent model upgrade sonnet→opus; (10) "接受 6 个 V3.5 patches + 接受最终 V_SEAL register text + Fire V_SEAL register". **Adjudication register at V_SEAL:** 8 reviewer dispatches (sub-decision Round 1 + PFR + V1 original killed-at-stall + V1 fresh redispatch + V2 + V3 PFR + final pre-SEAL × 2 legs each = ~14 effective dispatches with stall recovery). **Codex reliability empirically excellent this cycle:** 0/5 completed-dispatch hallucinations + 1 stall (recovered cancel+kill at V1 original); caught V2 BLOCKING (slippage.py:11 fee_model_label injectivity defect) + propagated Advisor hallucination at final pre-SEAL gate (R1.2 §6 BH-FDR fabrication via grep). **Advisor reliability degraded this cycle:** 15+ verified hallucinations across 7 dispatches (~85% per-dispatch rate; vs cumulative baseline ~22%); Mode A structural (file:line/exact-quote/numerical-content + wholesale document fabrication at V3 PFR); mandatory `[VERIFIED via grep]` token in dispatch briefs did NOT eliminate failures (V1 fresh redispatch diagnostic confirmed Mode A is structural not prompt-fixable); model upgrade sonnet→opus at decision-point round 6 yielded substantially improved performance (honest uncertainty disclosure + judgment-quality methodology output). **B2 standing rule LOCKED 2026-05-19** per `feedback_reviewer_routing_subagent_default.md` Reading 3 pilot CLOSED — Codex cross-model leg is load-bearing for SEAL-class canonical artifacts. **Mode A task-class severity refinement codified** (V3.5-PI): Advisor hallucinations severity scales with citation-density of task class — CRITICAL for artifact verification (~85% rate, content unusable); MANAGEABLE for substantive methodology judgment (~1 per dispatch, content recoverable). Operational refinement: skip Advisor for citation-dense artifact verification; keep for substantive judgment. **Option 1A atomicity binding empirical 11th trigger:** this Phase Marker advance commit atomically updates `docs/phase_marker_history.md` per Option 1A binding (`feedback_claude_md_freshness.md`); 11th trigger — cross-cycle robustness now 11-instance validated. **Forward-only carry-forward observations from R3.1d V_SEAL (4 new):** (1) Mode A task-class severity refinement codified; (2) Propagated-hallucination text in V2-P9 caught by Codex final pre-SEAL grep — demonstrates cross-model leg is structurally required for SEAL-class artifacts; (3) Advisor opus upgrade yielded substantial decision-point quality improvement (anti-self-serving discipline + honest uncertainty + Romano-Wolf/Westfall-Young surfaced as alternative FWER instruments); (4) R1.2 §6 contains NO multiplicity-correction prose despite Advisor V1 hallucination citing it — this was a propagated fabrication, not an R1.2 errata trigger. **Active next action:** R3.1d SEAL bundle pushed (2 commits: SEAL artifacts commit `44840a3` + this Phase Marker advance commit `<TBD>` with atomic history file update); R3.1b/c eligible-not-named when Phase 4 paper-trading infrastructure deploys; Phase B Pre-Sequence Roadmap V3 Tier 2 conditional prereqs (R2.1 / R2.2 / R2.3) + R5.1 candidate-subset under SPOT venue + R5.2 selection-inflation handling + R6.1 promotion class (REQUIRED per SD9 lock; instrument + threshold + N at R6.1 V_SEAL) + Tier-0 pause + Phase 2.5 bandit-dedup (parked) + pre-existing noise cleanup (.DS_Store + docs/d7_stage2c/* 13+ session carry-forward) + memory codification follow-up + advisor opus model effects pilot (extended observation) + other Charlie-specified — all eligible at separate Charlie register-event boundary per anti-pre-emption + Phase 5.1/5.2/Phase A/R1.2/R3.1a/R4.1 SEAL precedent. NO tag per Bucket-1 investigation note ≠ arc-level closeout. _R4.1 + R3.1a E.3 errata cycle entry detail (full verbatim) preserved at [`docs/phase_marker_history.md`](docs/phase_marker_history.md) per sealed-content invariance + Phase Marker compactness discipline._

**Sealed phase history**: full historical detail at [docs/phase_marker_history.md](docs/phase_marker_history.md). Compact summary of 5 most recent prior register-events:

| Phase / Arc | Seal commit | Closeout / canonical artifact | Tag |
|---|---|---|---|
| R3.1d cost-grid re-anchor cycle SEAL | `44840a3` (+ Phase Marker advance — this commit) | [`docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md`](docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md) + [`config/execution_phaseb_spot_15bps.yaml`](config/execution_phaseb_spot_15bps.yaml) + R4.1 hygiene patches + CLAUDE.md HARD CONSTRAINT (Conservative-Anchor Gate Integrity) + schema migration (`cost_anchor_id TEXT`) | — |
| R4.1 + R3.1a E.3 errata cycle SEAL | `3ff085e` (+ Phase Marker advance `7a63516`) | [`docs/phase5/R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md`](docs/phase5/R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md) + [`docs/phase5/R3_1A_VENUE_INFRASTRUCTURE_NOTE.md`](docs/phase5/R3_1A_VENUE_INFRASTRUCTURE_NOTE.md) §12 Errata + `config/execution.yaml` line 42 patch | — |
| R3.1a venue-infrastructure formalization cycle SEAL | `16099b8` (+ Phase Marker advance `46615cf`) | [`docs/phase5/R3_1A_VENUE_INFRASTRUCTURE_NOTE.md`](docs/phase5/R3_1A_VENUE_INFRASTRUCTURE_NOTE.md) | — |
| R1.2 IS-OOS rank correlation cycle SEAL | `de158e8` (+ Phase Marker advance `5b7fd7e`) | [`docs/phase5/R1_2_IS_OOS_RANK_CORRELATION_NOTE.md`](docs/phase5/R1_2_IS_OOS_RANK_CORRELATION_NOTE.md) | — |
| Phase A clarification cycle SEAL | `ab62b2e` (+ Phase Marker advance `850b9fe`) | [`docs/phase5/PHASE5_A_CLARIFICATION_NOTE.md`](docs/phase5/PHASE5_A_CLARIFICATION_NOTE.md) | — |

- **Active blueprint:** `blueprint/PHASE2_BLUEPRINT.md` (v2; **freshness note** added at top per Option B at commit `3a554fb` documenting D9 + post-D9 evaluation framework supersession by PHASE2C_3-9 arc series; CLAUDE.md Phase Marker remains operational source of truth)
- **Current batch_id:** `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` (Phase 2C Phase 1 walk-forward; corrected-engine re-run in `_corrected/` directory is canonical; same batch consumed by PHASE2C_6 single-regime evaluation runs at `data/phase2c_evaluation_gate/{smoke,primary,audit}_v1/`, by PHASE2C_7.1 multi-regime evaluation runs at `data/phase2c_evaluation_gate/{audit_2024_v1, audit_2024_v1_filtered, comparison_2022_vs_2024_v1}/`, and by PHASE2C_8.1 extended multi-regime evaluation runs at `data/phase2c_evaluation_gate/{eval_2020_v1, eval_2020_v1_filtered, eval_2021_v1, eval_2021_v1_filtered, audit_v1_filtered, comparison_2022_2024_2020_2021_v1}/`)
- **Current UTC-month spend (May 2026):** ~$19.66 (10 batches, all status `completed`; covers PHASE2C_15 cohort_a AND-gate fires + Phase 4 forward persistence test cost-runs at 7/13/15/17 bps + earlier Phase 2C iteration / smoke batches; per `agents/spend_ledger.db` `ledger` table, queried 2026-05-17; last API call 2026-05-09; Phase 5 + Phase 5.1 work to date is local-only with no API spend)
- **Hard rule for any future WF-consuming work:** must consume corrected artifacts only and call `backtest.wf_lineage.check_wf_semantics_or_raise()` before computing derived metrics from walk-forward summaries. For single-run holdout artifacts (PHASE2C_6 attestation domain `single_run_holdout_v1`), use the companion guard `backtest.wf_lineage.check_evaluation_semantics_or_raise()`. See [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md) Section RS for the corrected-engine consumption discipline that governs both attestation domains.

## Project-discipline notes

Standing project-discipline principles (apply across all work cycles, not bound to a phase) are codified at [`docs/discipline/METHODOLOGY_NOTES.md`](docs/discipline/METHODOLOGY_NOTES.md). Seven principles currently in force: §1 empirical verification for factual claims, §2 meta-claim verification discipline, §3 regime-aware calibration bands, §4 scale-step discipline for empirical evaluations, §5 precondition verification for structural and organizational principles, §6 commit messages are not canonical result layers, §7 asymmetric confidence reporting on multi-sample claims. §8 is the synthesis "How to apply these principles" section. The §4-§7 additions were codified during the PHASE2C_6 evaluation gate arc (commit `536f737`). Future cycles append new lessons as additional sections.

## Parked branches

Branches containing completed-but-not-yet-merged work are registered at [`docs/parked/PARKED_BRANCHES.md`](docs/parked/PARKED_BRANCHES.md), with activation trigger conditions and pre-merge verification checklist per parked branch. Currently parked: `phase2.5/bandit-dedup` (factor bandit Track A + semantic dedup Track B; combined Option-1 Path-3-style cycle authorized 2026-05-16; awaiting batch cadence resumption per Concern 1 isolation strategy).
