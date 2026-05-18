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

- **Current phase:** Phase A clarification cycle (Bucket-1-style investigation note per Template B; structural analog to Phase 5.1 + 5.2 investigation notes; answers Charlie's statistical-significance question on Phase 5.1's 17/22 binomial pass by characterizing structure below the binomial summary) **SEALED** at Phase A SEAL register-event boundary (canonical artifact at [`docs/phase5/PHASE5_A_CLARIFICATION_NOTE.md`](docs/phase5/PHASE5_A_CLARIFICATION_NOTE.md) sealed at Phase A SEAL commit `ab62b2e` + this Phase Marker advance commit; ~10 main §§ (§0 cycle metadata + 4-row Charlie register chain through V4 SEAL + Cadence B 2-cadence structure; §1 scope binding + 7 explicit "NOT resolved" items + V1-DRAFT scope-verification anchor; §2 headline finding "technically significant by pre-registration but methodologically thin" with Bonferroni + single-window caveats; §3 methodology with hypothesis_hash unique-key derivation + §3.4 robust-subset definition standardization; §4 Stratum A cost-sensitivity decomposition with effect-size breakdown + 8-strategy robust subset table + 3-vote-thin fragility analysis; §5 Stratum B failure-mode analysis with theme breakdown + 3-strategy robust subset + continuation-vs-reversal naming hypothesis; §6 10 OBSERVATIONS named anti-pre-naming + eligible-not-named for separate Charlie register-event boundaries; §7 Phase B decision surface inventory (4 axes: venue commitment / candidate-subset / promotion-class / prerequisite) without directional claims; §8 11 reserved decisions per anti-pre-emption invariant; §9 V# anchor chain V1 DRAFT → V2 → V3 → V4 SEAL with detailed adjudication history table; §10 references with sealed artifacts only — external literature names removed per Codex PFR NF2). **Outcome:** Phase 5.1's 17/22 binomial pass at 7bps resolved as **technically significant by pre-registration (p≈0.0085 < Phase-4-declared Bonferroni α=0.025) but methodologically thin** — 3 of 17 positives have Sharpe ≤ 0.1 (specifically 0.0008, 0.0337, 0.0532) with breakeven costs 7.0/8.0/9.2 bps (all at or below canonical 7bps); removing these 3 drops count to 14/22 (fails threshold). Below the binomial: 8 Stratum A robust candidates (Sharpe > 0.5 at all 4 tested costs 7/13/15/17 bps; 7 monday-pattern + 1 weekend-pattern, ALL within calendar_effect theme); 3 Stratum B robust candidates (analogous criterion despite stratum-level binomial failure; spans momentum/volume_divergence/volatility_regime themes); 11-candidate cross-stratum robust subset eligible-not-named for Phase B framing per OBSERVATION 5 selection-inflation guard + Codex A.2 C5 "cannot retrofit Stratum C in this cycle." Stratum A failure boundary characterized as 3-vote-thin (binomial-test artifact obscures structure); Stratum B characterized as bimodal in volume_divergence theme (naming pattern suggests continuation strategies survive, counter-trend strategies fail). Per-strategy Bonferroni framing documented symmetrically with joint composite framing — both mathematically valid, answer different questions; Phase 4 §1.5 pre-registration is canonical. Single-forward-window (~Jan-Apr 2026, ~2900 hourly bars) limitation flagged binding all per-strategy inferences. Trade-count range 1-26 across 11 robust candidates (with 2 strategies at 1-2 trades) flagged as severely limiting individual-strategy inference. NO tag at Phase A SEAL per Bucket-1 investigation note ≠ arc-level closeout per CLAUDE.md Tag policy + Phase 5.1 + Phase 5.2 precedent. **Cycle scope:** Phase A = Bucket-1 single-deliverable investigation cycle (Template B; analytical-only; no engine re-runs; no API spend). Scope strictly bounded to A.1 (cost-sensitivity decomposition on existing artifacts) + A.2 (Stratum B failure-mode analysis); Phase B venue commitment + path selection are out-of-scope and eligible-not-named for separate Charlie register-event boundaries per V4 §7 + §8. **5 Charlie register fires across Phase A cycle through SEAL:** (1) Cycle entry "Phase A clarification cycle authorize"; (2) Cycle structure bundle (cycle shape α + cadence shape B + skip incremental compute + reviewer round at V1) "authorize"; (3) Cadence 1 fire "authorize Cadence 1"; (4) Workflow batch ("A.1 reviewers + adjudication / A.2 reviewers + adjudication / Cadence 2 fire / V1 DRAFT reviewers + V1→V2 + PFR; stop before SEAL") + V1→V2 + V2→V3 PFR fixes; (5) V4 SEAL "SEAL fire". **Adjudication register at SEAL:** 4 reviewer rounds fired (A.1 + A.2 + V1 DRAFT + PFR rule-Y) with 2-leg subagent default each (Codex + quant-research-advisor parallel) = 8 individual dispatches; 0/8 Codex stalls; 0/8 verified advisor hallucinations (Option II citation verification discipline operationally enforced — every reviewer-cited fact grep-verified before adoption; no PUSHBACK fired this cycle). V1→V2 applied 11 ADOPTED fixes (Codex F1 BLOCKING §7 anti-pre-naming rewrite + Codex F2/F3/F4/F5 SUBSTANTIVE numerical corrections + Codex F6 MINOR + Advisor F1/F2 SUBSTANTIVE + Advisor F3/F4 MINOR + Advisor NF1 MINOR). V2→V3 PFR applied 5 ADOPTED fixes (Codex PFR NF1 SUBSTANTIVE §7 "should X" → "Whether X" pattern + Codex PFR §6/§7 contradiction SUBSTANTIVE residual directional language neutralization + Codex PFR §9 count correction + Codex PFR NF2 MINOR external literature removal + Advisor PFR F1 SUBSTANTIVE Bonferroni symmetric framing); 1 DEFERRED (Advisor PFR F2 MINOR "consistent with" with reviewer's self-acknowledged over-engineering risk). **Empirical observations from this cycle on reviewer routing reliability (consistent with Phase 5.2 codification):** Cross-model bilateral diversity validated again — Codex caught §7 BLOCKING directional language + §6 carry-forward directional residue that Advisor did not surface; Advisor caught selection-inflation guard + Bonferroni framing nuance + multi-confound isolation in (ii) hypothesis that Codex did not surface. Zero hallucination instances this cycle (improvement from Phase 5.2's 2/9 rate) — possibly attributable to brief-level disclosure of prior hallucination patterns in dispatch prompts; sample size too small to generalize. Cross-model diversity routine retains positive value per [[feedback_reviewer_routing_subagent_default.md]] B2 pilot sample (cumulative 12+ dispatches across Phase 5.1 + 5.2 + Phase A). **Option 1A atomicity binding empirical 7th trigger:** this Phase Marker advance commit atomically updates `docs/phase_marker_history.md` per Option 1A binding (`feedback_claude_md_freshness.md`); 7th trigger at this advance — cross-cycle robustness now 7-instance validated. **Forward-only carry-forward observations from Phase A SEAL (4 new):** (1) Phase 4 forward window exact date range not currently traced (plausibly ~Jan-Apr 2026 ≈ 2900 hourly bars; CSV rows lack date fields; eligible-not-named per OBSERVATION 8); (2) In-sample (Phase 2C training-window) vs OOS (Phase 4 forward) rank correlation is a gating prerequisite for Phase B promotion decisions, not computed in this cycle (eligible-not-named per OBSERVATION 9); (3) Continuation-vs-reversal naming pattern in volume_divergence theme suggests structural signal-direction split (DSL inspection would confirm/refute; eligible-not-named per OBSERVATION 7); (4) Monday-pattern concentration in robust-8 (7/8) is curve-fit-suspect; no in-repo literature support; external literature reportedly mixed but not invoked as project-internal grounding per Codex A.1 [UNVERIFIED in repo] discipline. **Active next action:** Phase A cycle SEAL bundle pushed at this register-event; Phase B venue commitment register-event eligible-not-named per V3 §6.3 (Phase 5.2 carry-forward; Branch.A/B/C/D from Phase 5.2 §6.4 still unfired); Phase B candidate-subset axis eligible-not-named (22-candidate Stratum A vs 8-candidate robust subset vs 11-candidate cross-stratum); Phase B promotion-class axis eligible-not-named (Path 1 paper trading / Path 2 real-cost-discovery / Path 3 Stratum B reconsideration / Path 1' refined / pause); prerequisite register-events eligible (forward window date verification / in-sample OOS rank correlation / DSL inspection); Phase 2.5 bandit-dedup activation still parked per [`PARKED_BRANCHES.md`](docs/parked/PARKED_BRANCHES.md); pre-existing noise cleanup eligible (.DS_Store + docs/d7_stage2c/*); project pause / strategic-absorption eligible; other Charlie-specified — all eligible at separate Charlie register-event boundary per anti-pre-emption + §10 sub-§ codified discipline. Push timing at this commit: **2 commits at this Phase A SEAL bundle** (Phase A SEAL artifact commit + this Phase Marker advance commit with atomic history file update); NO tag per Bucket-1 investigation note ≠ arc-level closeout per Tag policy + Phase 5.1 + 5.2 precedent. _Phase 5.2 entry detail (full verbatim) preserved at [`docs/phase_marker_history.md`](docs/phase_marker_history.md) per sealed-content invariance + Phase Marker compactness discipline._

**Sealed phase history**: full historical detail at [docs/phase_marker_history.md](docs/phase_marker_history.md). Compact summary of 5 most recent prior register-events:

| Phase / Arc | Seal commit | Closeout / canonical artifact | Tag |
|---|---|---|---|
| Phase A clarification cycle SEAL | `ab62b2e` (+ Phase Marker advance — this commit) | [`docs/phase5/PHASE5_A_CLARIFICATION_NOTE.md`](docs/phase5/PHASE5_A_CLARIFICATION_NOTE.md) | — |
| Phase 5.2 §2.1-reconciliation-lite cycle SEAL | `4a9aa3c` (+ Phase Marker advance `3369e4f`) | [`docs/phase5/PHASE5_2_VENUE_RECONCILIATION_NOTE.md`](docs/phase5/PHASE5_2_VENUE_RECONCILIATION_NOTE.md) | — |
| Phase 5.1 cost-model investigation cycle SEAL | `8251067` (+ Phase Marker advance `ea13015`) | [`docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md`](docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md) | — |
| Path 3 methodology consolidation execute cycle Pass 2 SEAL | `0b7cb69` (+ Phase Marker advance `ae62fc3`) | [`docs/path3/PATH3_EXECUTE_PASS2_CODIFICATION.md`](docs/path3/PATH3_EXECUTE_PASS2_CODIFICATION.md) | — |
| Path 3 methodology consolidation execute cycle Pass 1 SEAL | `244378c` (+ Phase Marker advance `14a77c0`) | [`docs/path3/PATH3_EXECUTE_PASS1_DECISIONS.md`](docs/path3/PATH3_EXECUTE_PASS1_DECISIONS.md) | — |

- **Active blueprint:** `blueprint/PHASE2_BLUEPRINT.md` (v2; **freshness note** added at top per Option B at commit `3a554fb` documenting D9 + post-D9 evaluation framework supersession by PHASE2C_3-9 arc series; CLAUDE.md Phase Marker remains operational source of truth)
- **Current batch_id:** `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` (Phase 2C Phase 1 walk-forward; corrected-engine re-run in `_corrected/` directory is canonical; same batch consumed by PHASE2C_6 single-regime evaluation runs at `data/phase2c_evaluation_gate/{smoke,primary,audit}_v1/`, by PHASE2C_7.1 multi-regime evaluation runs at `data/phase2c_evaluation_gate/{audit_2024_v1, audit_2024_v1_filtered, comparison_2022_vs_2024_v1}/`, and by PHASE2C_8.1 extended multi-regime evaluation runs at `data/phase2c_evaluation_gate/{eval_2020_v1, eval_2020_v1_filtered, eval_2021_v1, eval_2021_v1_filtered, audit_v1_filtered, comparison_2022_2024_2020_2021_v1}/`)
- **Current UTC-month spend (May 2026):** ~$19.66 (10 batches, all status `completed`; covers PHASE2C_15 cohort_a AND-gate fires + Phase 4 forward persistence test cost-runs at 7/13/15/17 bps + earlier Phase 2C iteration / smoke batches; per `agents/spend_ledger.db` `ledger` table, queried 2026-05-17; last API call 2026-05-09; Phase 5 + Phase 5.1 work to date is local-only with no API spend)
- **Hard rule for any future WF-consuming work:** must consume corrected artifacts only and call `backtest.wf_lineage.check_wf_semantics_or_raise()` before computing derived metrics from walk-forward summaries. For single-run holdout artifacts (PHASE2C_6 attestation domain `single_run_holdout_v1`), use the companion guard `backtest.wf_lineage.check_evaluation_semantics_or_raise()`. See [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md) Section RS for the corrected-engine consumption discipline that governs both attestation domains.

## Project-discipline notes

Standing project-discipline principles (apply across all work cycles, not bound to a phase) are codified at [`docs/discipline/METHODOLOGY_NOTES.md`](docs/discipline/METHODOLOGY_NOTES.md). Seven principles currently in force: §1 empirical verification for factual claims, §2 meta-claim verification discipline, §3 regime-aware calibration bands, §4 scale-step discipline for empirical evaluations, §5 precondition verification for structural and organizational principles, §6 commit messages are not canonical result layers, §7 asymmetric confidence reporting on multi-sample claims. §8 is the synthesis "How to apply these principles" section. The §4-§7 additions were codified during the PHASE2C_6 evaluation gate arc (commit `536f737`). Future cycles append new lessons as additional sections.

## Parked branches

Branches containing completed-but-not-yet-merged work are registered at [`docs/parked/PARKED_BRANCHES.md`](docs/parked/PARKED_BRANCHES.md), with activation trigger conditions and pre-merge verification checklist per parked branch. Currently parked: `phase2.5/bandit-dedup` (factor bandit Track A + semantic dedup Track B; combined Option-1 Path-3-style cycle authorized 2026-05-16; awaiting batch cadence resumption per Concern 1 isolation strategy).
