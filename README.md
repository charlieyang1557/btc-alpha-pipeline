# BTC Alpha Pipeline

A quantitative research pipeline for discovering, testing, and validating BTC trading
strategies.

This repo is an active pre-MVP research system. The emphasis is not on shipping a
trading bot as quickly as possible, but on building the data, backtesting, evaluation,
and research-discipline infrastructure needed to avoid common quant mistakes like
look-ahead bias, data leakage, and backtest overfitting.

## Current Status

The project has completed the foundational data, backtesting, mining, evaluation,
forward-persistence, and diagnostic-attribution phases. Active work is methodology
consolidation (Path 3) before the next substantive research cycle.

Completed:

- Validated BTC/USDT hourly OHLCV ingestion from Binance Vision and CCXT
- Parquet-based market data storage with schema and quality checks
- Backtrader-based single-run and walk-forward backtesting infrastructure
  (corrected walk-forward engine sealed at `wf-corrected-v1`)
- Experiment registry for run tracking and reproducibility
- Baseline strategies and manual trade-audit workflows
- Factor library, strategy DSL, hypothesis hashing, regime holdout integration
- AI-assisted hypothesis mining: Proposer + Critic + budgeted orchestrator,
  with deterministic stub + live Sonnet backends (Phase 2B D6/D7)
- Evaluation-gate cycle (Phase 2C): single- and multi-regime evaluation,
  multiple-testing and Sharpe deflation screens, methodology consolidation,
  breadth-expansion fire, main-fire cohort (PHASE2C_3 through PHASE2C_15)
- Forward-persistence test (Phase 4): pre-registered binomial test on the
  PHASE2C_15 cohort over a 2026-01-01 forward window at 15bps.
  **Result: no forward persistence detected at the pre-registered success
  criterion.** Sealed at tag `phase4-forward-test-v1`.
- Diagnostic attribution (Phase 5): six pre-registered per-mode indicators
  applied to the Phase 4 null result. **Result: single firing failure mode —
  §2.b cost drag (Wilcoxon `p = 1.82e-12`).** Successor-cycle class:
  cost-model investigation (gross-vs-realistic decomposition) eligible.
  Sealed at tag `phase5-diagnostic-execution-v1`.

In progress:

- Path 3 methodology consolidation cycle: filtering ≥40 accumulated discipline
  observations from the Phase 5 arc and prior cycles into the canonical
  methodology corpus. Scoping and sub-spec drafting cycles SEALED;
  execute cycle eligible-not-named.

Parked (complete but not merged):

- Phase 2.5 — combined factor bandit + semantic dedup. Implementation,
  cross-track e2e, and arc-level closeout sealed on a side branch; awaiting
  batch cadence resumption before merging. See [docs/parked/PARKED_BRANCHES.md](docs/parked/PARKED_BRANCHES.md).

Not yet:

- Cost-model investigation cycle (eligible successor to Phase 5)
- Production live trading
- Capital allocation automation
- Public performance claims
- A polished demo UI

## Why This Exists

Most trading-system projects fail quietly because the backtest is too permissive:
signals accidentally see future data, execution assumptions are too generous, or
hundreds of variants are mined until one looks good by chance.

BTC Alpha Pipeline is built around the opposite bias: make the research process
auditable before treating any strategy as promising.

Core design principles:

- Signals are computed on bar N and execute on bar N+1 open.
- All timestamps are UTC.
- Costs are explicitly modeled.
- Train, validation, holdout, and test boundaries are treated as research constraints.
- Strategy candidates are tracked through reproducible hashes and registry records.
- Batch-level results are evaluated with multiple-testing controls.

## Architecture

```text
btc-alpha-pipeline/
|-- ingestion/        # Binance Vision and CCXT data ingestion
|-- config/           # Execution conventions, schemas, and environment splits
|-- data/             # Parquet market data, features, results, and reports
|-- backtest/         # Backtesting engine, metrics, registry, audit tools
|-- factors/          # Feature and factor computation
|-- strategies/       # Baseline strategies and DSL strategy definitions
|-- agents/           # AI proposer, critic, orchestrator, and budget ledger
|-- docs/             # Phase plans, closeouts, methodology notes, decisions
|-- risk/             # Future position sizing and allocation layer
|-- paper_trading/    # Future simulated-live execution layer
`-- live/             # Future live execution layer
```

## Tech Stack

- Python 3.11+
- pandas, NumPy, PyArrow
- Backtrader
- SQLite
- CCXT
- Pydantic
- pytest
- Anthropic SDK for the AI-assisted hypothesis workflow

## Project Phases

- **Phase 0** — data infrastructure (sealed)
- **Phase 1A** — single-run backtest validation (sealed)
- **Phase 1B** — walk-forward orchestration and baseline evaluation (sealed)
- **Phase 2A** — factor library, strategy DSL, hypothesis hash, regime holdout plumbing (sealed)
- **Phase 2B** — AI-assisted hypothesis generation, critic filtering, budgeted orchestration (sealed through D7 Stage 2d)
- **Phase 2C** — evaluation gates, corrected walk-forward lineage, multi-regime
  evaluation, multiple-testing and Sharpe-deflation screens, methodology
  consolidation, breadth-expansion, main-fire cohort (sub-phases 1-15 sealed)
- **Phase 2.5** — factor bandit + semantic dedup (parked on side branch)
- **Phase 4** — forward-persistence test (sealed; null result at 15bps)
- **Phase 5** — diagnostic attribution cycle (sealed; cost-drag identified)
- **Path 3** — methodology consolidation cycle (scoping + sub-spec sealed; execute eligible)
- **Future** — cost-model investigation, paper trading, risk layer, live execution

## Getting Started

Install the base package and development tools:

```bash
pip install -e ".[dev]"
```

Install Phase 1 and Phase 2 extras when working on backtesting or AI-mining code:

```bash
pip install -e ".[dev,phase1,phase2]"
```

Run the test suite:

```bash
pytest
```

Build feature data after market data is available:

```bash
python -m factors.build_features --pair BTCUSDT --interval 1h
```

## Key Docs

Project rules and operating context:

- [CLAUDE.md](CLAUDE.md) — project operating rules and current phase marker
- [data_dictionary.md](data_dictionary.md) — data schemas and column definitions
- [Methodology Notes](docs/discipline/METHODOLOGY_NOTES.md) — research discipline principles
- [Phase Marker History](docs/phase_marker_history.md) — sealed phase history
- [Parked Branches](docs/parked/PARKED_BRANCHES.md) — completed work awaiting merge

Phase blueprints:

- [Phase 0 Blueprint](blueprint/PHASE0_BLUEPRINT.md) — data infrastructure plan
- [Phase 1 Blueprint](blueprint/PHASE1_BLUEPRINT.md) — backtesting plan
- [Phase 2 Blueprint](blueprint/PHASE2_BLUEPRINT.md) — AI-assisted research design

Recent sealed closeouts and decisions:

- [Phase 2C-15 Results](docs/closeout/PHASE2C_15_RESULTS.md) — main-fire cohort
- [Phase 4 Results](docs/closeout/PHASE4_RESULTS.md) — forward-persistence test
- [Phase 5 Scoping Decision](docs/phase5/PHASE5_SCOPING_DECISION.md)
- [Phase 5 Diagnostic Sub-spec](docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md)
- [Phase 5 Results](docs/closeout/PHASE5_RESULTS.md) — diagnostic attribution
- [Path 3 Scoping Decision](docs/path3/PATH3_METHODOLOGY_CONSOLIDATION_SCOPING_DECISION.md)
- [Path 3 Sub-spec](docs/path3/PATH3_METHODOLOGY_CONSOLIDATION_SUBSPEC.md)
- [WF Test Boundary Semantics](docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md) — corrected-engine consumption discipline

## Disclaimer

This is research software, not financial advice. Nothing in this repository should be
interpreted as a recommendation to trade BTC or any other asset.
