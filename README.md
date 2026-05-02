# BTC Alpha Pipeline

A quantitative research pipeline for discovering, testing, and validating BTC trading
strategies.

This repo is an active pre-MVP research system. The emphasis is not on shipping a
trading bot as quickly as possible, but on building the data, backtesting, evaluation,
and research-discipline infrastructure needed to avoid common quant mistakes like
look-ahead bias, data leakage, and backtest overfitting.

## Current Status

The project has completed the foundational data and backtesting phases and is now
focused on Phase 2C evaluation discipline.

Completed:

- Validated BTC/USDT hourly OHLCV ingestion from Binance Vision and CCXT
- Parquet-based market data storage with schema and quality checks
- Backtrader-based single-run and walk-forward backtesting infrastructure
- Experiment registry for run tracking
- Baseline strategies and manual trade-audit workflows
- Factor library, strategy DSL, hypothesis hashing, and AI-assisted mining scaffolding

In progress:

- Regime-aware holdout evaluation
- Multiple-testing and Sharpe deflation screens
- Cleaner evidence gates for separating possible signal from overfit artifacts
- Documentation of research methodology and phase-by-phase decisions

Not yet:

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

- Phase 0: data infrastructure
- Phase 1A: single-run backtest validation
- Phase 1B: walk-forward orchestration and baseline evaluation
- Phase 2A: factor library, strategy DSL, hypothesis hash, regime holdout plumbing
- Phase 2B: AI-assisted hypothesis generation, critic filtering, budgeted orchestration
- Phase 2C: evaluation gates, corrected walk-forward lineage, overfitting controls
- Future: paper trading, risk layer, live execution

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

- [CLAUDE.md](CLAUDE.md): project operating rules and current phase marker
- [data_dictionary.md](data_dictionary.md): data schemas and column definitions
- [Phase 0 Blueprint](blueprint/PHASE0_BLUEPRINT.md): data infrastructure plan
- [Phase 1 Blueprint](blueprint/PHASE1_BLUEPRINT.md): backtesting plan
- [Phase 2 Blueprint](blueprint/PHASE2_BLUEPRINT.md): AI-assisted research design
- [Methodology Notes](docs/discipline/METHODOLOGY_NOTES.md): research discipline notes

## Disclaimer

This is research software, not financial advice. Nothing in this repository should be
interpreted as a recommendation to trade BTC or any other asset.
