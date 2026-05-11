# External Repos Survey + Backtrader Successor Evaluation + vectorbt Spike A

**Date:** 2026-05-11
**Status:** WORKING DRAFT — discussion artifact, NOT canonical TECHNIQUE_BACKLOG content
**Purpose:** Consolidate (a) survey of 10 external repos for current/future-use opportunities, (b) Backtrader successor evaluation, (c) build-own engine 5-path analysis, (d) Spike A empirical findings on vectorbt ↔ Backtrader byte-equivalence. Designed to be reviewed by Charlie + cross-routed to ChatGPT/advisor before any entries are promoted to `strategies/TECHNIQUE_BACKLOG.md`.

**Integration plan:** Section H lists candidate TECHNIQUE_BACKLOG entries with proposed phase anchors. After Charlie review, approved entries get lifted into TECHNIQUE_BACKLOG.md with the doc's standard discipline (phase anchor + rationale + pushback considered + source).

**Scope binding:** This document operates at **analysis register** per [METHODOLOGY_NOTES §29](../discipline/METHODOLOGY_NOTES.md) (framework architectural refactor evaluation at analysis register only). No implementation is authorized by this document. Any actual engine work requires separate Charlie register authorization.

---

## Section A — Scope context (why this survey)

**Original scope:** Single-asset BTC algorithmic quant research pipeline.

**Expanded scope (per 2026-05-11 discussion):** BTC + stocks + options + multi-agent AI teams. This expansion materially changes the relevance of every repo in the survey:
- Repos that were "interesting but irrelevant" (OpenBB equity data, Lean options, TradingAgents multi-analyst) become **first-class infrastructure candidates** for Phase 4 (stocks) / Phase 5 (options) / multi-agent expansion.
- Repos that overlapped Phase 2C (qlib factor DSL, TradingAgents persona debate) become **immediate borrowing candidates** for current Critic/Proposer work.

**Backlog discipline preserved:** TECHNIQUE_BACKLOG.md's rule "Nothing gets added without a specific phase / deliverable anchor" applies. This doc proposes candidate entries with anchors; promotion is gated by Charlie register.

---

## Section B — 10-Repo Analysis (one-paragraph + structured per repo)

For each repo: **Maturity** / **🟢 Now / 🟡 Future / 🔴 Skip** / **Top 2-4 TECHNIQUE_BACKLOG candidate entries (draft)**.

### B.1 OpenBB — github.com/OpenBB-finance/OpenBB

**One-line 中文直觉:** 一个把各家金融数据 API 打包成统一接口的"数据水管中转站",顺便挂了 MCP server 给 AI agent 用——它不是量化研究框架,是数据接入层。

**Maturity:** 67.4k⭐ / very active / latest release 2026-04-25 / AGPLv3 (viral copyleft — research-only OK, blocks future SaaS).

**🟢 Now (Phase 2C/3 BTC):** Nothing substantive. Our CCXT + Binance Vision pipeline already self-sufficient. MCP server pattern is reference-only.

**🟡 Future (Phase 4 stocks / Phase 5 options / AI teams):**
- `extensions/equity` + `extensions/derivatives` provider connectors — Phase 4/5 anchor; consolidates FMP/Polygon/Yahoo/CBOE under one API surface
- `extensions/economy` (FRED/IMF/OECD) — Phase 4 macro regime conditioning
- Fama-French factor data extension — Phase 4+ canonical multi-factor benchmark
- `agents-for-openbb` companion repo — Phase 2.5+ multi-agent expansion reference

**🔴 Skip:** Not a backtest engine; `quantitative` ext is descriptive stats only (no DSR/PBO); `technical` ext overlaps our factors registry; workspace/Desktop UI overkill for single-person; AGPL contagion blocks future commercialization.

**Candidate TECHNIQUE_BACKLOG entries:**
1. **OpenBB equity + derivatives provider layer (read-only adoption)** — Phase 4-5 — Use `obb.equity.price.historical()` + `obb.derivatives.options.chains()` when scope leaves BTC-only. Pushback: AGPLv3 contagion — confirm research-only use stays clear of derivative-work boundary; could stay direct-on-vendor (Polygon SDK etc.) if license proves blocking.
2. **Fama-French factor data extension** — Phase 4+ — Pull FF 3/5-factor returns as reference benchmark when expanding factor library beyond price/volume. Pushback: 20 lines of pandas directly from Ken French's site may be sufficient; OpenBB wrapper is marginal convenience.

---

### B.2 ai-hedge-fund — github.com/virattt/ai-hedge-fund

**One-line 中文直觉:** 19 个"投资名人 + 分析师"AI 角色各自打分,组合经理汇总信号给股票交易建议(教育玩具,不真下单)。

**Maturity:** 58.5k⭐ / Python+TS / last release 2026-05-09 / explicitly "educational proof-of-concept, does not make trades."

**🟢 Now (Phase 2C/3):**
- **Persona-conditioned Critic ensemble** — drop-in idea for D7b: add 2-3 frozen-prompt persona Critics (Taleb tail-risk, Graham margin-of-safety) running parallel, AND-gate their verdicts. Each persona is independent `D7bBackend` implementation, plugs into existing `agents/critic/orchestrator.py`.
- **Per-agent confidence/signal schema** — structured `{signal, confidence: 0-100}` per persona; cleaner than current D7b free-form scores
- **Persona-as-prompt-template separation** — file-level addressable prompts (codifies "frozen prompt per role" discipline)

**🟡 Future:**
- **LangGraph workflow orchestration** — canonical multi-agent DAG pattern for Phase 4+
- **Portfolio Manager + Risk Manager as separate agents** — Phase 3 paper-trade design pattern
- **Stocks ticker-list + fundamentals patterns** — Phase 5 stocks scope

**🔴 Skip:** Persona pantheon itself is aesthetic-heavy, light on rigor; backtest layer has no WF/DSR/CV; we're substantially more rigorous on evaluation gates.

**Candidate TECHNIQUE_BACKLOG entries:**
1. **Persona-conditioned Critic ensemble (multi-Critic AND-gate)** — Phase 2C+ D7b extension or Phase 2D successor cycle — Add 2-3 persona-style Critics (Taleb / Graham / Druckenmiller) running parallel with AND-gate consensus. Pushback: cost scales linearly per Sonnet call; personas may overfit to investing folklore not BTC-microstructure-applicable; AND-gate may over-filter under PHASE2C_15's 4% hit rate baseline. Mitigate via smoke fire at small N.
2. **Portfolio Manager / signal-aggregation layer separation** — Phase 3 paper trading — Codify "aggregator" module above Proposer/Critic that handles overlap + sizing + risk-gate. Pushback: premature abstraction for single-strategy current state; but Phase 4+ multi-asset will force it.
3. **LangGraph as orchestration backbone (eval-only, defer adoption)** — Phase 4 entry scoping — Evaluate (not adopt) LangGraph when agent count grows beyond Proposer/Critic dyad. Pushback: new dependency not in approved list; abstraction overhead; our crash-safe ledger already covers checkpointing.

---

### B.3 TradingAgents — github.com/tauricresearch/tradingagents

**One-line 中文直觉:** 一个把华尔街研究部全员搬进 LangGraph 的多角色 LLM 团队——分析师 → 多空辩论 → 交易员 → 风控,通过结构化辩论给出单日交易决策。

**Maturity:** 73.4k⭐ / Python / v0.2.4 2026-04-25 / AAAI 2025 paper (Xiao et al. 2025, arXiv:2412.20138) / active research framework, NOT production-grade trading discipline.

**🟢 Now (Phase 2C/3):**
- **Bull/Bear researcher debate with `max_debate_rounds`** — D7b LLM Critic enhancement: replace single-shot rubric with bounded 2-3 round bull/bear debate over candidate DSL. New D7b backend, doesn't touch D7a contract.
- **Reflection-memory injection** — distill prior-batch survivors into 1-sentence reflections (composition-only, no raw metrics) into next Proposer prompt. Aligns with CLAUDE.md hard constraint.
- **`deep_think_llm` vs `quick_think_llm` split** — Sonnet for Proposer/Critic, Haiku for DSL-validity pre-check + duplicate-hypothesis hashing (pre-Critic structural filters, NOT Critic itself — boundary intact per CLAUDE.md).

**🟡 Future:**
- **Four-analyst decomposition (Fundamentals/Sentiment/News/Technical)** — Phase 4 stocks anchor
- **Portfolio Manager / Risk Manager final approval gate** — Phase 3+ capital allocation
- **Decision-log realized-return reflection loop** — Phase 4 paper-trading instrumentation

**🔴 Skip:** Single-day decision flow incompatible with our WF + DSR discipline; LangGraph rewrite of orchestrator not incremental gain (our crash-safe ledger already covers checkpointing); Alpha Vantage / StockTwits / Reddit data sources irrelevant.

**Candidate TECHNIQUE_BACKLOG entries:**
1. **Bull/Bear debate D7b Critic backend variant** — Phase 2C+ Critic methodology consolidation cycle — Replace single-shot D7b rubric with bounded 2-3 round bull/bear debate over candidate DSL. Pushback: 2-3× cost per critique; locked D7b prompt is a contract boundary per CLAUDE.md — needs new Stage decision. Suitable as Phase 2.5 or Phase 3 experiment, NOT current PHASE2C_15.
2. **Reflection-memory injection for Proposer context** — Phase 2C+ Proposer prompt evolution — Distill survivors into 1-2-sentence composition-only reflections; next Proposer batch receives prior reflections as bounded context. Pushback: anti-anchoring already flagged in PHASE2C_14 sub-spec §2.1; pre-register information-leakage audit checklist before adoption.
3. **Quick-think / deep-think LLM role split** — Phase 3 (cost-scaling cycle) — Designate cheap-and-fast checks (DSL validity, near-duplicate hash, manifest sanity) to Haiku; Sonnet for Proposer + Critic LLM-rubric. Pushback: CLAUDE.md hard constraint Haiku-NOT-for-Critic preserved (proposed roles are pre-Critic structural filters); still needs explicit Stage decision.
4. **Portfolio Manager approval gate as risk-limit enforcement seam** — Phase 3+ multi-strategy capital allocation — Introduce "Portfolio Manager" layer between strategy outputs and order placement. Pushback: premature for single-strategy current state.

---

### B.4 freqtrade — github.com/freqtrade/freqtrade

**One-line 中文直觉:** 加密界的"自动交易瑞士军刀"——数据下载、回测、Hyperopt、ML、干跑、实盘、Telegram/WebUI 一条龙,但学术统计严谨性弱。

**Maturity:** 50.1k⭐ / Python / 月度 release 2026-04-30 / 7+ years production dry-run + live experience.

**🟢 Now (Phase 2C/3):**
- **12 loss function reference implementations** (SharpeHyperOptLoss, SortinoHyperOptLoss, CalmarHyperOptLoss, MultiMetricHyperOptLoss, ProfitDrawDownHyperOptLoss…) — Phase 2C+ leaderboard multi-metric ranking
- **Optuna search-space abstraction** (`IntParameter`, `DecimalParameter`) — Phase 3+ DSL candidate hyperparam tuning
- **Bar-internal event ordering** (Exit → Stoploss → ROI → Trailing stop, low-before-high) — comparison reference for our `execution.yaml` "adverse first" rule

**🟡 Future:**
- **Dry-run architecture** — Phase 3 paper trading direct blueprint (same strategy class dry/live switch, SQLite trade state, ccxt real-time feed); fork or mimic to save 2-3 weeks
- **Exchange abstraction layer** — Phase 3.5+ live: Binance/Kraken/OKX/Bybit + futures wrapper
- **FreqAI auto-retrain pipeline** — Phase 4+ ML signal expansion (PCA + outlier removal + retraining cadence)
- **MultiMetricHyperOptLoss + Calmar/Sortino formula bank** — Phase 3 risk gates

**🔴 Skip:**
- Whole framework replacement of Backtrader — not worth migration cost
- **Hyperopt as strategy generation** — no walk-forward / CV / DSR / PBO; conflicts with our anti-p-hacking discipline
- **Default zero-slippage assumption** — fills at requested price within candle high/low; backtest fidelity strictly worse than our 7bps; do NOT downgrade our standard
- **ROI exit uses candle high** — optimistic; conflicts with our "adverse first" conservative rule
- FreqAI as Proposer replacement — paradigm mismatch (supervised learning ≠ LLM hypothesis generation)

**Candidate TECHNIQUE_BACKLOG entries:**
1. **Multi-metric leaderboard composite (Sortino + Calmar + MaxDD + ProfitDD)** — Phase 3 risk gates / leaderboard multi-dim — Upgrade `min(train_sharpe, holdout_sharpe)` ranking to composite multi-metric loss; reference freqtrade's 12 loss function formulas. Pushback: composite ranking interacts with DSR multiple-testing — multi-metric should run AFTER DSR as tiebreak, never modify N semantics; anti-p-hacking requires metric choice pre-registered at sub-spec, no ad-hoc weight tuning.
2. **Dry-run paper trading harness architecture blueprint** — Phase 3 paper trade — Fork or mimic freqtrade's dry-run loop (same strategy code, SQLite persistence, ccxt feed, default exchange fees, kill-switch). Pushback: their fill-at-requested-price is optimistic — inject our 7bps slippage explicitly in our adaptation; verify reconnect/timeout logic.
3. **FreqAI-style rolling retrain framework reference** — Phase 4+ ML signals — Reference FreqAI's auto-retrain cadence + train/test split + PCA + outlier removal pipeline. Pushback: their train/test split is not equivalent to our environments.yaml v2 four-way split (train/holdout/validation/test); must preserve our regime-holdout + test-touched-once discipline.

---

### B.5 qlib — github.com/microsoft/qlib

**One-line 中文直觉:** 微软开源的"端到端 AI 量化投资平台",自带因子表达式 DSL + 缓存 + 模型动物园 + 回测 + RL,但主战场是 A 股/美股,不是 BTC。

**Maturity:** 42.5k⭐ / Microsoft / MIT license / v0.9.7 Aug 2025 / 2,065+ commits / RD-Agent (LLM-based autonomous factor mining) directly relevant.

**🟢 Now (Phase 2C/3):**
- **`Ref(factor, k)` lag operator as first-class DSL primitive** — our DSL has no lag operator; can't express "yesterday's RSI vs today's RSI" without pre-baking lagged factors
- **Three-tier expression cache (Mem/Expression/Dataset)** — disk-based timestamp-aware invalidation; could replace our full-rebuild-on-`feature_version`-mismatch with incremental tail-only recompute after CCXT update
- **`learn_processors` vs `infer_processors` split** with `fit_start_time`/`fit_end_time` — explicit fit-window decoupling from data-load window; aligns with our Section RS attestation-domain discipline at data-handler layer

**🟡 Future:**
- **RD-Agent (LLM-based autonomous factor mining) read-comparison** — Phase 4 entry scoping — external multi-agent quant precedent at production scale
- **Alpha158 / Alpha360 factor sets** — Phase 4 stocks — 158/360-factor curated banks (US + China); scaffold for factor library expansion
- **RL framework (TWAP / PPO / OPDS)** — Phase 4+ learned execution; Phase 5+ Greeks-aware execution
- **`qrun` YAML workflow + rolling prediction** — multi-asset orchestration template
- **Model Zoo (25+ models incl. Transformer/TabNet/GBDT)** — Phase 4+ when DSL graduates to learned signals

**🔴 Skip:** No crypto / no 1h native; point-in-time .bin format would be strict downgrade for our parquet; A-share-specific factor neutralization; Backtrader replacement (Qlib's backtest is cross-sectional portfolio not event-driven single-asset).

**Candidate TECHNIQUE_BACKLOG entries:**
1. **Lag operator `Ref()` as first-class DSL primitive** — Phase 2C / DSL schema revision sub-spec drafting cycle — Add `Ref(factor, k)` to DSL so agents can express "yesterday's RSI vs today's RSI" without pre-baked lag factors. Pushback: risk of agents emitting nonsense lags; mitigate via DSL complexity budget (max k ≤ warmup constraint already enforced).
2. **Timestamp-aware expression cache for incremental factor builds** — Phase 2C+ operational hardening — Layer per-expression disk cache keyed by (source hash, last-bar-utc); only recompute on tail after CCXT incremental. Pushback: adds invalidation surface (known footgun class — see our `feature_version` discipline); defer until incremental rebuild time becomes empirical bottleneck.
3. **RD-Agent prompt/orchestrator patterns reference read** — Phase 4 entry scoping (or methodology consolidation cycle) — Time-boxed (≤4h) study of RD-Agent code as comparative reference for our Proposer/Critic/budget-ledger design. NOT adopt the system — read the patterns. Pushback: RD-Agent itself early-stage; may not be stronger reference than what we've built.
4. **`learn_processors` / `infer_processors` split pattern** — Phase 4 stocks — Adopt Qlib's processor split with explicit fit-window decoupling. Pushback: premature for current single-asset; capture now as reference so we don't reinvent.

---

### B.6 TradingAgents-CN — github.com/hsliuping/TradingAgents-CN

**One-line 中文直觉:** 上游 tradingagents 的中文增强 fork——主要价值不在 agent 创新,而在「A 股数据 + 国产 LLM 适配 + FastAPI/Vue 产品化外壳」。对纯 BTC quant 来说大部分功能不相关。

**Maturity:** 26.2k⭐ / Python+Vue+TS / v1.0.1 2026-04-14 / 活跃但许可证混合(核心 Apache 2.0,`app/`+`frontend/` 是 proprietary 需商业授权).

**Delta vs upstream tradingagents:** `llm_adapters/` (Qwen/DeepSeek/GLM/Tongyi/Doubao + AiHubMix), A股数据源 fallback chain, FastAPI 后端 + MongoDB/Redis + Vue 3 前端, 智能新闻分析模块 (零技术细节), 用户认证 + RBAC, 上游 indicator bug 修复.

**🟢 Now:** 几乎没有——A股数据对我们不相关。

**🟡 Future:**
- **Multi-provider LLM adapter pattern** — Phase 4+ 月度 spend > $100 时,DeepSeek/Qwen 成本 ~1/10-1/20 Sonnet,可作 Critic 或 sub-analyst 廉价路由(但 repo **没 cost benchmark**,需自验)
- **多级缓存模式 (MongoDB/Redis/file)** — Phase 4+ 多资产时(我们 parquet 已足够,直到 paper trade live)
- **WebSocket + SSE 实时通知** — Phase 4 paper trade 监控

**🔴 Skip:** A股数据源、FastAPI+Vue 整 stack、用户认证、新闻分析模块零细节、`app/`+`frontend/` proprietary。核心 agent 逻辑仍来自上游 tradingagents,不如直接读上游。

**Candidate TECHNIQUE_BACKLOG entries:**
1. **Multi-provider LLM adapter pattern (DeepSeek/Qwen cost-down fallback)** — Phase 4+ when monthly spend approaches $100 cap consistently — Abstract `LLMBackend` protocol with cost-aware routing; Sonnet primary, DeepSeek/Qwen for retry/cheap-path. Pushback: CLAUDE.md library policy requires explicit approval; cost savings unverified (no benchmarks in repo); language mismatch risk on English DSL prompts.

---

### B.7 Kronos — github.com/shiyu-coder/Kronos

**One-line 中文直觉:** 一个针对 OHLCV K 线的预训练 **decoder-only Transformer** 基础模型(金融版 GPT)——输入历史 K 线 + 未来时间戳,自回归生成未来 N 根 K 线的 open/high/low/close/volume(可采样多条路径做概率预测)。

**Maturity:** 23.9k⭐ / Python / MIT license / AAAI 2026 paper (arXiv 2508.02739) / 4 pretrained sizes on HuggingFace (mini 4.1M / small 24.7M / base 102.3M / large 499.2M) / pretrained on 12B K-line records from 45 exchanges including BTC/USDT.

**Model:** Two-stage — quantizer tokenizes OHLCV → hierarchical discrete tokens → autoregressive Transformer. Output: forecasted OHLCV df indexed by future timestamps; supports `sample_count > 1` for probabilistic forecasts.

**🟢 Now (Phase 2C+ factor library extension):**
- **Zero-shot K-line forecast as factor family**: `kronos_pred_ret_24h`, `kronos_path_dispersion`, `kronos_directional_prob`, `kronos_pred_hi_lo_range` registered in `factors/` — plugs directly into existing DSL pipeline

**🟡 Future:**
- **Cross-asset zero-shot generalization** — Phase 4 stocks expansion: 45-exchange pretraining should generalize without retraining
- **Fine-tuning pipeline (Qlib-integrated)** — Phase 3+ when GPU budget available; BTC-specialized forecaster as higher-tier signal
- **Synthetic K-line generation (paper claims 22% gen-fidelity)** — Phase 3+ stress-test scenarios; complement to stationary bootstrap
- **Implied-vol surface analog for options (Phase 5)** — path-dispersion at multiple horizons = empirical forward-vol term structure

**🔴 Skip:** No reported Sharpe / OOS trading metrics in paper or README (only RankIC + MAE + gen-fidelity — NOT risk-adjusted returns); repo explicitly says "not a production-ready quantitative trading system"; not a substitute for canonical DSR / PBO.

**🚨 CRITICAL CAVEAT:** Foundation model trained through 2025 on 45 exchanges. **Pretraining data almost certainly overlaps our 2020-2025 train/val/test/holdout splits.** Cannot be used as a "model" on dates inside its pretraining cutoff without contaminating splits. Must verify Kronos pretraining cutoff predates 2020-01 OR restrict use to post-cutoff forward dates only. If cutoff is 2024+, factor unusable on 2020-2024 splits → effectively forces Phase 3+ paper-trade scope, NOT Phase 2C backtest scope. This is **CLAUDE.md hard constraint level risk** (execution integrity).

**Candidate TECHNIQUE_BACKLOG entries:**
1. **Kronos zero-shot K-line forecast as factor family** — Phase 2C+ factor library extension OR Phase 3+ paper trade — Register 3-5 Kronos-derived factors via `factors/` registry; inference at bar N close, factor stored for bar N+1 consumption. **Pushback CRITICAL: pretraining cutoff leakage** — must verify Kronos cutoff predates 2020-01 OR restrict to post-cutoff forward dates. If cutoff ≥2024, factor unusable on historical splits → defer to Phase 3 paper-trade forward scope. Also: inference cost at Kronos-large × thousands of bars non-trivial; use Kronos-small for batch builds.
2. **Kronos path-sampling as forward-volatility proxy** — Phase 3 paper trade + statistical machinery prep — Use `sample_count=N` Monte-Carlo paths as forward-looking scenario sets for position sizing. Pushback: complements (does NOT replace) canonical stationary bootstrap; same pretraining-cutoff leakage caveat as above; cumulative path divergence over 24+ bars may be unrealistic (model misspecification).
3. **Fine-tuned Kronos-BTC as Phase 4+ tier-1 signal** — Phase 4 (stocks expansion) or later — Fine-tune Kronos-base/large on canonical BTC parquet + selected equity panels. Pushback: adds GPU dependency + non-DSL signal layer (breaks Phase 2's DSL-only discipline); should only happen post-Phase-2 with explicit scope-decision authorization.

---

### B.8 backtrader — github.com/mementum/backtrader (we already use)

**One-line 中文直觉:** 老牌 Python 回测框架,事件驱动 + 多资产 + 活跃券商对接,但作者从 **2023-04-19 起 0 commits**——21.5k stars 但实质上是冻结的成熟库,我们在用一个"骨架仍坚固但不再修缮"的房子。

**Maturity:** ⚠️ **CRITICAL — effectively unmaintained.** Last code commit `b853d7c` "Version 1.9.78.123" on **2023-04-19** (~3 years stale). 59 PRs unmerged, Python 3.12+ not officially verified. Community continues via forums + forks (backtrader2 = ALSO dead at 2021-08).

**🟢 Now (features we have but underuse):**
- **Analyzers framework** (SharpeRatio_A, DrawDown, TradeAnalyzer, SQN, VWR, PyFolio) — replace hand-rolled metrics in `backtest/metrics.py`
- **OCO + bracket orders** (`buy_bracket`, `sell_bracket`) — DSL `exit` blocks could compile to bracket primitives, eliminating "adverse first within same bar" approximation
- **Sizers** (PercentSizer, AllInSizerInt, FixedReverser) — Phase 3 position sizing
- **`bt.observers.*`** (Broker/Trades/BuySell/DrawDown) — trade debugging
- **`bt.TimeFrame` resampling + replay** — 1h → 4h / 1d in-engine
- **Trading calendars** (`bt.tradingcal.PandasMarketCalendars`) — irrelevant for 24/7 BTC but mandatory Phase 4 stocks

**🟡 Future:**
- **Multi-data Cerebro** (multiple `adddata()` feeds) — Phase 4 stocks portfolio backtests
- **`bt.feeds.RollOver`** — Phase 5 futures contract-roll
- **Live brokers: IB / Oanda / VisualChart** — Phase 3 paper trade
  - **CAVEAT**: IB store uses deprecated `ibpy`; modern IB API requires community fork (`ib_insync` / `ib_async`)
- **CCXT live data feed** — community `bt-ccxt-store` fork is ALSO stale; Phase 3 risk

**🔴 Known issues:**
- **Maintenance freeze (2023-04 last commit)** — Phase 3+ live trading cannot rely on upstream fixes
- **Bar-based indicators, not time-based** (already documented in CLAUDE.md)
- **No native options pricing / Greeks** — Phase 5 needs external layer (`py_vollib`, `mibian`) bolted on
- **No proper portfolio rebalancing primitives** — multi-asset works at feed level but rebalancing must be hand-written
- **Naive datetime issue** (already documented)
- **Python 3.12+ not officially verified** — may hit `collections.abc` / `imp` removals on upgrade

**Candidate TECHNIQUE_BACKLOG entries:**
1. **Adopt Backtrader Analyzers for canonical metric reporting** — Phase 2D / Phase 3 prep — Replace hand-rolled Sharpe/DD in `backtest/metrics.py` with `bt.analyzers.SharpeRatio_A` + `DrawDown` + `TradeAnalyzer`, gated by warmup-aware slicing. Pushback: annualization constant disagreement risk (252 vs 365 vs 8760 bars/yr); lock annualization explicitly in adapter + regression test against existing sealed runs.
2. **Successor-framework evaluation track (maintenance hedge)** — Phase 3 entry scoping (NOT pre-committed) — Evaluate `nautilus_trader`, `vectorbt`/`vectorbtpro`, `Lean` for live-trading viability. Pushback: successor switch is CLAUDE.md-shaking (DSL compiler / execution_model / slippage / engine all touch Backtrader); scope as evaluation-only first.
3. **Bracket-order lowering for DSL `exit` groups** — Phase 2D / Phase 3 prep — Compile DSL `exit` blocks (stop + take-profit) into `buy_bracket`/`sell_bracket` instead of independent stop+limit; engine handles OCO atomically. Pushback: Backtrader's bracket sim ≠ live IB bracket exactly; keep "adverse first" rule as fallback for DSL exits that can't express as bracket; parity test on PHASE2C survivor cohort.

---

### B.9 FinGPT — github.com/AI4Finance-Foundation/FinGPT

**One-line 中文直觉:** 一个把开源 LLM(Llama2/3、ChatGLM2、InternLM)用 LoRA 在金融指令数据集上微调的"轻量适配器集合"——主打股票情绪分析和单周方向预测,不是独立预训练模型。

**Maturity:** 20k⭐ / Python / v1.0.0 2026-04-08 / MIT license + "not financial advice" disclaimer. LoRA adapters published on HuggingFace; download counts mostly 9-48 (forecaster 439 max) — academic citations > production adoption.

**Model variants:** Sentiment LoRA (Llama2-13B / InternLM-20B / ChatGLM2-6B), Forecaster LoRA (Llama2-7B; DOW30 + SZ50 one-week direction), Multi-task LoRA (Llama2-7B / Llama3-8B), RAG variant for sentiment.

**🟢 Now:** Essentially none — no crypto-trained variants; equity-news training distribution (FPB/FiQA/TFNS) severely out-of-distribution for BTC.

**🟡 Future:**
- **fingpt-sentiment LoRA** — Phase 4 (stocks expansion) — Equity-news sentiment factor in registry; training distribution matches
- **fingpt-forecaster_dow30** — Phase 5+ AI teams — *Benchmark to beat*, not a component; design reference for analyst agents
- **Instruction-dataset format** — Phase 5+ contingent — Template if we ever build BTC sentiment dataset to fine-tune local model
- **FinNLP sibling repo** — Phase 4+ news ingestion plumbing more useful than FinGPT itself

**🔴 Skip:** No crypto coverage; DSL/strategy generation overlap with our Proposer absent (no overlap); forecaster's one-week direction too coarse for our 1h-bar WF; self-hosting 13B + LoRA operationally heavier than calling Sonnet at our scale; low download counts.

**Candidate TECHNIQUE_BACKLOG entries:**
1. **FinGPT sentiment LoRA as Phase 4 equity-news factor** — Phase 4 (stocks expansion) — Use `fingpt-sentiment_llama2-13b_lora` or `fingpt-mt_llama3-8b_lora` over equity news as sentiment factor in registry. Pushback: self-hosting infra debt; could just route through Sonnet with caching; only worth it at high news-volume.
2. **FinGPT-Forecaster as prior-art benchmark for Phase 5 analyst agents** — Phase 5+ AI teams — Study prompt template (headlines + financials → developments / concerns / direction) as design reference. Pushback: not benchmarked rigorously in public docs; design-pattern value only.
3. **FinNLP sibling repo for news ingestion plumbing** — Phase 4 (stocks / news flow) — Evaluate FinNLP's RSS/scrapers/normalized schemas as starting point. Pushback: quality of FinNLP scrapers unverified; needs separate audit pass; could be stale.

---

### B.10 Lean — github.com/QuantConnect/Lean

**One-line 中文直觉:** Lean 是机构级开源回测+实盘引擎,支持股票/期权/期货/外汇/加密"全资产",但核心是 C#,Python 通过 PythonNet 桥接(性能与调试折衷:能写策略但底层不在 Python,堆栈跨语言不直观)。

**Maturity:** 18.9k⭐ / C# 94.1% + Python 5.7% / Apache 2.0 / actively maintained by QuantConnect Inc.

**🟢 Now:** Essentially none — Phase 2C deep in Backtrader + DSL compiler + corrected-WF engine; switching cost vastly exceeds remaining BTC-only marginal benefit.

**🟡 Future (this is the big section):**
- **Multi-asset universe + portfolio modeling** — Phase 4 stocks — Native equity + futures + options + forex + crypto same algorithm
- **Options chain + Greeks native support** — Phase 5 options must-have — delta/gamma/theta/vega + IV surface as first-class citizens
- **Paper trading + live brokerage integration** — Phase 3 paper trade — IB / Tradier / Alpaca / Coinbase / Binance / Kraken / Bitfinex pre-integrated
- **Walk-forward + parameter optimization** — Built-in genetic/grid optimizer, cluster-parallelizable
- **Event-driven + data-agnostic feed** — Phase 4 third-party stock/options data
- **AI team collaboration** — Apache 2.0 + modular + large community examples

**🔴 Friction we'd pay:**
- **C# core → Python via PythonNet bridge** — cross-CLR/CPython debug stacks unfriendly; deep custom indicators/execution_model forces reading C# source
- **Migration cost 4-8 weeks** — `dsl_compiler.py` + `execution_model.py` + `bt_parquet_feed.py` + `walk_forward.py` + `experiment_registry.py` all rewrite + N+1/7bps/24-bar in Lean fee model + tests
- **Functional duplication** — Our simplified DSR + corrected-WF lineage + RS guards exist; Lean's statistics module doesn't align exactly; migration loses PHASE2C_11 attestation domain
- **Data layer duplication** — Our parquet vs Lean's binary scheme; dual-maintain or converter
- **Local Docker dependence** — LEAN CLI pushes Docker workflow; ops surface expansion

**Candidate TECHNIQUE_BACKLOG entries:**
1. **Lean as Phase 5 options engine (NOT Backtrader replacement)** — Phase 5 (options expansion) — Keep Backtrader for BTC + Phase 4 stocks; Phase 5 options goes Lean; cross-engine DSL hash + experiment_registry unified registration. Pushback: dual-engine = 2 execution-semantic maintenance; but Backtrader-on-options structurally impossible — dual-engine is forced not nice-to-have.
2. **Lean brokerage-abstraction interface as Phase 3 paper trade blueprint** — Phase 3 (paper trading) — Don't introduce Lean dependency; study `IBrokerage` interface design + order lifecycle state machine as `paper_trading/` API reference. Pushback: "read Apache 2.0 source then write" boundary fuzzy; answer: study public interface design only, no code copy.
3. **Lean LEAN CLI optimizer evaluation (NOT pre-committed adoption)** — Phase 4 (stocks expansion) — Evaluate whether Lean's optimizer (genetic/grid + cluster-parallel) beats hand-rolled walk_forward.py for multi-asset. Pushback: migration = abandoning corrected-WF lineage + attestation domain; evaluate only when Phase 4 actual bottleneck demands.

---

## Section C — Backtrader Successor Deep Evaluation

**Trigger:** Per Section B.8, Backtrader effectively unmaintained since 2023-04-19. Phase 3+ live trading + Phase 4 multi-asset + Phase 5 options all expose successor-needed pressure. METHODOLOGY_NOTES §29 binds: framework refactor evaluation at analysis register only; this section IS that analysis register output.

### C.1 Candidate evaluation table

| Candidate | Maintenance | License | N+1 invariant | Multi-asset | Options+Greeks | Live broker | Batch perf | Migration cost | **Adjudication** |
|---|---|---|---|---|---|---|---|---|---|
| **nautilus_trader** | ✅ Active (bi-weekly) | LGPL-3.0 | ⚠️ Half-compatible (OHLC 4-point decompose) | ✅ | ⚠️ Greeks unclear | ✅ IB/Binance/Coinbase | ⚠️ Event-driven + GIL | **8-14 weeks** | 🟡 **Strong Phase 3+ paper→live candidate; not now** |
| **vectorbt (free)** | ✅ Active | Apache + **Commons Clause** | ❌ **User-discipline `.fshift(1)`** | ✅ | ❌ | ❌ | 🟢 **100-1000× Backtrader** | **6-10 weeks** | 🟢 **NOT replace — use as parallel pre-filter / BTC engine base** (see Section E) |
| **vectorbtpro** | ✅ Active paid | Commercial | (same + partial mitigation) | ✅ | ❌ | ❌ | 🟢 | 同上 + paid | 🟡 Pro's purged CV is Phase 3 re-evaluation point |
| **zipline-reloaded** | ⚠️ Stefan Jansen + dependabot | Apache 2.0 | ✅ Default | ❌ (Equity+Future hard-coded) | ❌ | ❌ | ❌ Slow | 6-10 weeks | 🔴 **SKIP** — no 1h freq, no options, no crypto |
| **Backtesting.py** | ✅ Active | **AGPL-3.0** | ✅ Default | ❌ **Single-asset by design** | ❌ | ❌ | ❌ | 4-6 weeks + impossible | 🔴 **SKIP** — toy, structurally blocks Phase 4/5 |
| **backtrader2 fork** | ❌ **2021-08 last commit** | GPL-3.0 | (same upstream) | (same) | ❌ | (same) | (same) | 0 | 🔴 **DEAD** — more stale than upstream |
| **Lean** | ✅ Active | Apache 2.0 | ⚠️ C# semantic re-express | ✅ | ✅ **唯一开源 options first-class** | ✅ IB/Alpaca/Coinbase | ⚠️ | 8-12 weeks total | 🟡 **Phase 5 options-only engine; dual with Backtrader** |

### C.2 Recommended strategy: Stratified, not unified

**No single successor.** The honest synthesis is layered + dual-engine, not "one ring to rule them all":

```
Phase 2C 现在:
  Backtrader (truth layer, 7bps, N+1)                  ← 不动,继续做 SEALED 评估

可加(Phase 2C 后期 / Phase 3 prep):
  vectorbt (parallel pre-filter / BTC engine candidate) ← Section D-E 路径
  Backtrader (truth layer)                              ← 双引擎并跑,逐 SEALED revalidate

Phase 3+ 实盘:
  nautilus_trader (paper→live) — 6-8h spike POC 先验证   ← C.1 评估候选

Phase 5 期权:
  Lean (options + Greeks engine)                        ← 跨引擎 DSL hash + experiment_registry
  Backtrader / BTC engine (BTC + stocks)
```

---

## Section D — Build-Own Engine: 5-Path Analysis

After surveying successors, Charlie raised the question: build our own engine, possibly forking vectorbt as base?

### D.1 Five paths enumerated

| Path | Scope | Engineering (single-dev focused) | Phase 2C SEALED risk | Leverage |
|---|---|---|---|---|
| **A. Full fork + 魔改 vectorbt** | Take whole vectorbt codebase, modify | **8-16 weeks** | High (revalidate all SEALED) | Inherits vectorbt speed + we own discipline layer |
| **B. From-scratch vectorized engine** | No fork, just inspired-by | **12-24 weeks** | High | Clean license, no Commons Clause |
| **C. Thin discipline wrapper around vectorbt** | `disciplined_pf_from_signals()` + auto-shift + 7bps + WF lineage + 24-bar defer | **1.5-2.5 weeks** (revised post-Spike A) | Low | vectorbt speed + N+1 footgun closed at boundary |
| **D. MVP DSL-only engine** | Pure function `evaluate_dsl(dsl, ohlcv) → trades+metrics`, numpy/numba, hard-codes our 6 operators + 7bps + N+1 + 24-bar | **4-6 weeks** | Medium (dual-engine validation) | Tight fit to actual use case; ~3-6k lines |
| **E. No build, vectorbt pre-filter only** | Status quo + vectorbt as parallel scanner | **2-3 weeks** | Zero | Speed for pre-filter, truth stays Backtrader |

### D.2 vectorbt core abstraction block analysis (per Charlie's question)

| Block | Severity | Solvable | Resolution |
|---|---|---|---|
| **N+1 default unsafe** | 🟡 Medium | ✅ **Yes** | `from_signals(close=close, entries=entries.shift(1), exits=exits.shift(1), price=open, fees=0.0007)` — vectorbt accepts `price=` parameter; **core abstraction does NOT block** |
| **Custom slippage + 24-bar defer** | 🟡 Medium | ✅ **Yes** | (a) preprocess entries/exits to mask zero-volume bars (~30 lines numpy); or (b) `from_order_func` numba callback (vectorbt's explicit escape hatch). **Empirically validated in Spike A.3b.** |
| **WF lineage + attestation** | 🟢 Low | ✅ **Yes** | Wrapper boundary `check_wf_semantics_or_raise()` — orthogonal to engine |
| **Multi-asset cross-sectional portfolio rebalance** (stocks) | 🟡 Medium | ⚠️ **Half-solvable** | `from_orders` provides primitive; rebalance abstraction needs rewrite layer (Phase 4 stocks engine extends BTC engine) |
| **Options chain + Greeks + multi-leg** | 🔴 High | ❌ **No** | vectorbt assumes single price series; no strike/expiry/payoff concepts. **Phase 5 must use separate engine** (Lean OR custom). |

**Key correction from earlier nervous analysis:** "vectorbt's N+1 is a design philosophy conflict" was overstated. The precise statement is: **vectorbt's default API is unsafe, but it exposes explicit extension points (`price=`, `from_order_func`) for us to re-impose N+1 invariant at wrapper boundary.** Confirmed by Spike A (Section G).

### D.3 Charlie's "三个引擎" refinement (2+1, not 1+1+1)

Charlie's intuition: split by asset class instead of one general engine.

**Precise version:**
- **BTC engine + Stocks engine** share vectorbt base (fork). BTC engine = thin wrapper; Stocks engine = + rebalance layer.
- **Options engine** must be independent. vectorbt does NOT support options. Options engine = Lean OR custom from-scratch (8-16 weeks).

**Shared discipline library:** Same N+1 / 7bps / WF lineage / DSR / experiment_registry shared across all engines via `discipline/` library (LLVM IR + backend pattern; PyTorch CPU/CUDA/MPS pattern).

```
discipline/
├── wf_lineage.py          ← existing
├── n1_invariant.py        ← NEW (all engine entry points must call)
├── zero_volume_defer.py   ← NEW (24-bar preprocessing)
├── dsr.py                 ← existing
├── experiment_registry.py ← existing
└── attestation_domain.py  ← existing (Section RS)
```

### D.4 Phased build plan (revised post-Spike A)

| Phase | Deliverable | Engineering (focused) | Triggers |
|---|---|---|---|
| **Phase 2C late / Phase 3 prep** | shared discipline library + BTC engine (fork vectorbt + wrapper) | **5-8 weeks** | §29 evaluation + Phase 3 entry scoping authorization |
| **Phase 4 launch** | Stocks engine (fork BTC engine + rebalance abstraction) | **4-6 weeks** additional | Phase 4 scoping authorization |
| **Phase 5 launch** | Options engine (Lean adoption OR custom from-scratch) | **8-16 weeks** | Phase 5 scoping authorization |

**vs all-in-one upfront:** 18-30 weeks total all-at-once is strongly NOT recommended.

### D.5 Charlie's confirmed direction

**BTC engine = vectorbt fork + Backtrader dual-engine.** Progressive replacement, not big-bang. Backtrader stays as reference oracle for at least 1-2 batch cycles of validation. **Stocks + Options retain multi-option (Lean / custom / vectorbt-extended) — not locked.**

**Commons Clause = not a problem (Charlie self-use only, no commercial redistribution).**

---

## Section E — vectorbt-as-BTC-engine: License + Fork Considerations

**License:** vectorbt is Apache-2.0 + **Commons Clause**. Commons Clause restricts *commercial redistribution* of the library itself; **using vectorbt in a research/private pipeline is fully permitted**. Per Charlie 2026-05-11: "Commons Clause 无所谓,我完全自用,不会拿出来卖."

**Fork strategy (vs pure-wrapper):**

| Dimension | Wrapper call (no fork) | Fork + discipline layer |
|---|---|---|
| Engineering (BTC engine immediate) | 2-3 weeks | 3-5 weeks (fork init overhead) |
| Upstream vectorbt bug | Wait for upstream | Patch ourselves |
| Upstream version bumps | Track + may break wrapper | We decide when to merge |
| Progressive replacement of core kernel | Cannot (no source) | Can — strategic option |
| Maintenance burden | Low (upstream-dependent) | Medium (we own everything) |

**Recommendation: fork is the right move post-Charlie's "Commons Clause OK"** — same near-term cost, strategic option preserved for long-term.

**Known immediate fork patch:** vectorbt 0.26.2 + plotly ≥ 5.20 = incompatible (`heatmapgl` removed). Pin `plotly < 5.20` OR upstream-patch the `_settings.py` template. Captured here so it's not rediscovered later.

---

## Section F — Spike A Empirical Findings (the load-bearing new data)

**Spike A** = 2-4 hour hands-on verification of build-own engine theoretical claims. Authorized 2026-05-11, executed same session.

### F.1 Hypothesis under test

> vectorbt's `Portfolio.from_signals(close=close, entries=entries.shift(1), exits=exits.shift(1), price=open, fees=0.0007)` produces a trade list byte-equivalent to Backtrader's `set_coc(False) + set_coo(False) + default-fill-on-next-open` under the same strategy signals on the same OHLCV data.

### F.2 Methodology

3-way comparison across:
1. **Manual numpy oracle** — explicit per-bar loop, verifiable by hand
2. **Backtrader** — current project engine, `set_coc(False) + set_coo(False) + setcommission(0.0007) + PercentSizer(99%)`
3. **vectorbt** — `from_signals` with the formula under test

**Data:** `data/raw/btcusdt_1h.parquet`, multiple windows.
**Throwaway venv at `/tmp/vectorbt_spike/`.** No project codebase modified.

### F.3 Five tests + results

| Test | Strategy | Trade count match | Price byte diff | Notes |
|---|---|---|---|---|
| **A.1** | SMA crossover (fast=20, slow=50) | 30 / 30 / 30 ✅ | **0.0000000000** | 3-way byte-equivalent; per-trade gross return max diff = **5.68e-7** (float precision noise) |
| **A.2.1** | Momentum (PctChange(24) > 0.02 / < 0) | 36 / 36 ✅ | **0.0000000000** | Threshold operators (`>` / `<`) perfect |
| **A.2.2** | Mean reversion (z-score, entry z<-2, exit z>0) | **23 + 1 trade** ⚠️ | **0.0000000000** (first 23) | End-of-window convention difference — see F.4 |
| **A.3** | SMA crossover at 2023-03-15 to 2023-04-15 (contains zero-vol bar) | 10 / 10 ✅ | **0.0000000000** | No signal hit the zero-vol bar; preprocessing was no-op |
| **A.3b** | Synthetic forced entry at 2023-03-24 11:00 (signal→fill at zero-vol 12:00) | 1 / 1 ✅ | **0.0000000000** | **AlphaBroker deferred to 14:00 + preprocessing deferred to 14:00, byte-identical** — 24-bar deferral preprocessing approach validated |

### F.4 The 23-vs-24 mean_reversion mismatch — fully diagnosed

**Cause:** End-of-window convention difference, NOT an engine semantic bug.

- 2024-04-01 05:00 BUY signal fires in both Backtrader and vectorbt (z=-2.5646; identical signal recognition)
- Both engines enter at 2024-04-01 06:00 open @ $69167.47
- **Backtrader:** leaves position open at end of data (does NOT include in closed-trades list)
- **vectorbt:** auto-closes at last bar's close @ 23:00 (forces closed-trade with exit_price=$69649.80)

**Both are "correct" — just different conventions.** Backtrader's: "trades are only what the strategy closed." vectorbt's: "every entry must have a settled exit, even if synthetic."

**Implication for wrapper:** explicit `end_of_window_policy: Literal["leave_open", "force_close"]` parameter. Setting `force_close=False` masks `exits.iloc[-1] = False` and vectorbt won't auto-close. Or use `close_on_end=False` in `from_signals` directly.

### F.5 Confirmed empirical claims (write into BTC engine spec)

1. ✅ **`entries.shift(1) + price=open + fees=0.0007` reproduces Backtrader N+1 fill within float precision**
2. ✅ **24-bar zero-volume deferral CAN be implemented as preprocessing** — byte-equivalent to project's AlphaBroker
3. ✅ **CrossOver / `>` / `<` / composite z-score operators all byte-equivalent**
4. ⚠️ **End-of-window handling requires explicit wrapper-level policy**

### F.6 NOT yet tested (deliberately deferred — future spike candidates)

- Walk-forward multi-window stitching (corrected-WF lineage discipline across windows)
- AND/OR composite conditions (`(rsi<30) & (volume>volume.rolling(20).mean())`)
- Short trades (long-only currently; future expansion)
- Multi-asset cross-sectional (Phase 4 stocks engine)
- Full PHASE2C SEALED candidate regression on Backtrader-vs-vectorbt (Spike C scope, 3-4 weeks)

### F.7 Revised wrapper API draft (post-empirical)

```python
def disciplined_pf_from_signals(
    entries: pd.Series,
    exits: pd.Series,
    ohlcv: pd.DataFrame,
    fees: float = 0.0007,
    init_cash: float = 10000.0,
    end_of_window_policy: Literal["leave_open", "force_close"] = "leave_open",
    max_defer_bars: int = 24,
) -> vbt.Portfolio:
    _assert_no_lookahead(entries, exits, ohlcv)              # static check
    entries_shifted = entries.shift(1).fillna(False).astype(bool)
    exits_shifted   = exits.shift(1).fillna(False).astype(bool)
    entries_shifted = defer_to_next_valid_bar(entries_shifted, ohlcv["volume"], max_defer_bars)
    exits_shifted   = defer_to_next_valid_bar(exits_shifted,   ohlcv["volume"], max_defer_bars)
    if end_of_window_policy == "leave_open":
        exits_shifted.iloc[-1] = False
    pf = vbt.Portfolio.from_signals(
        close=ohlcv["close"], entries=entries_shifted, exits=exits_shifted,
        price=ohlcv["open"], fees=fees, init_cash=init_cash, freq="1H",
        close_on_end=(end_of_window_policy == "force_close"),
    )
    check_wf_semantics_or_raise(pf)
    return pf
```

**Engineering estimate revised: 1.5-2 focused weeks** for wrapper (down from 2-3 weeks pre-spike) — unknowns reduced by empirical validation.

### F.8 Spike artifacts (kept at /tmp for this session; can be promoted if Charlie wants)

- `/tmp/vectorbt_spike/spike_compare.py` — A.1 (SMA crossover 3-way)
- `/tmp/vectorbt_spike/spike_sizing_diagnostic.py` — A.1 per-trade return + sizing analysis
- `/tmp/vectorbt_spike/spike_a2_operators.py` — A.2 momentum + mean_reversion
- `/tmp/vectorbt_spike/spike_a2b_mean_rev_diagnostic.py` — A.2b end-of-window finding
- `/tmp/vectorbt_spike/spike_a3_zero_volume.py` — A.3 zero-vol no-op case
- `/tmp/vectorbt_spike/spike_a3b_forced_defer.py` — A.3b forced zero-vol defer

---

## Section G — TECHNIQUE_BACKLOG Candidate Shortlist (recommended for promotion)

After cross-repo synthesis + spike empirical filtering, the following candidates score highest for **near-term TECHNIQUE_BACKLOG.md promotion** with proper phase anchors. Promotion requires Charlie register approval; this is recommendation, not authorization.

### G.1 Strong recommend (Phase 2C+ / Phase 3 prep)

1. **`disciplined_pf_from_signals()` BTC engine wrapper** (NEW entry — proposed) — Phase 3 prep — Build vectorbt-fork-based BTC engine via the wrapper API in F.7; double-engine with Backtrader for 1-2 batch cycles for validation, then Backtrader retires to reference oracle. **Spike A empirically validates** the core formula. Pushback: §29 evaluation register only at this register; implementation requires separate Phase 3 entry scoping cycle authorization; PHASE2C SEALED revalidation cost is real.
   *Source: this discussion + Spike A 2026-05-11.*

2. **Lag operator `Ref()` as first-class DSL primitive** (from qlib survey) — Phase 2C / DSL schema revision sub-spec — Add `Ref(factor, k)` to DSL. Zero data-pipeline cost, expands hypothesis space. Pushback: nonsense-lag risk mitigated by existing DSL complexity budget.
   *Source: qlib Alpha158/Alpha360 DSL.*

3. **Bull/Bear debate D7b Critic backend variant** (from TradingAgents survey) — Phase 2C+ Critic methodology consolidation — Bounded 2-3 round bull/bear debate over candidate DSL; new D7b backend, doesn't touch D7a contract. Pushback: 2-3× cost; locked D7b prompt is contract boundary per CLAUDE.md.
   *Source: TradingAgents paper (Xiao et al. 2025).*

4. **Persona-conditioned Critic ensemble** (from ai-hedge-fund survey) — Phase 2C+ D7b extension or Phase 2D — 2-3 persona-style Critics (Taleb / Graham / Druckenmiller) running parallel with AND-gate. Pushback: cost scales linearly; personas may overfit to investing folklore not BTC-microstructure-applicable; over-filter risk under 4% hit rate baseline.
   *Source: ai-hedge-fund.*

5. **Reflection-memory injection for Proposer** (from TradingAgents survey) — Phase 2C+ Proposer prompt evolution — 1-sentence composition-only survivor reflections injected into next Proposer prompt. Pushback: anti-anchoring already flagged in PHASE2C_14 sub-spec §2.1.
   *Source: TradingAgents trading_memory pattern.*

### G.2 Phase 3 paper-trade gate

6. **Multi-metric leaderboard composite (Sortino + Calmar + MaxDD-rel)** (from freqtrade survey) — Phase 3 risk gates — Upgrade `min(train_sharpe, holdout_sharpe)` to composite. Pushback: must run AFTER DSR as tiebreak; metric choice must be pre-registered at sub-spec.
   *Source: freqtrade HyperOptLoss bank.*

7. **Dry-run paper trading harness architecture** (from freqtrade survey) — Phase 3 paper trade — Fork/mimic freqtrade dry-run loop. Pushback: inject our 7bps explicitly; verify reconnect logic.
   *Source: freqtrade dry-run.*

8. **nautilus_trader Phase 3+ paper→live POC** (from successor evaluation) — Phase 3 entry scoping — 6-8h spike POC for paper trade adapter. Pushback: 8-14 week full migration cost too high before Phase 3 actual demand.
   *Source: Backtrader successor eval Section C.*

### G.3 Phase 4 multi-asset / Phase 5 options

9. **OpenBB equity + derivatives provider layer adoption** (from OpenBB survey) — Phase 4-5 — Use `obb.equity` + `obb.derivatives` to consolidate data vendors. Pushback: AGPL contagion if commercializing.
   *Source: OpenBB extensions.*

10. **Lean as Phase 5 options engine (NOT Backtrader replacement)** (from successor + Lean survey) — Phase 5 — Dual-engine; cross-engine DSL hash + experiment_registry unification. Pushback: dual maintenance burden but options on Backtrader structurally impossible.
    *Source: Lean equity-options key concepts.*

11. **Qlib RD-Agent reference read** (from qlib survey) — Phase 4 entry scoping — Time-boxed (≤4h) study as comparative reference. Pushback: RD-Agent itself early-stage.
    *Source: Microsoft RD-Agent.*

### G.4 Conditional / risk-flagged

12. **Kronos zero-shot K-line forecast as factor family** (from Kronos survey) — Phase 2C+ OR Phase 3+ depending on pretraining cutoff — Register Kronos-derived factors. **CRITICAL pushback: pretraining data cutoff almost certainly contaminates 2020-2025 splits.** Verify Kronos cutoff predates 2020-01 OR restrict to post-cutoff forward use only.
    *Source: Kronos AAAI 2026 paper (arXiv 2508.02739).*

13. **Successor framework evaluation track** (from successor eval) — Phase 3 entry scoping (NOT pre-committed) — Evaluate nautilus / vectorbt / Lean before live trading. Already implicit in (8) but worth standalone backlog entry.
    *Source: Backtrader maintenance freeze 2023-04.*

### G.5 Explicit REJECTED (record so we don't re-litigate)

- **backtrader2 community fork** — DEAD since 2021-08; do not use as Backtrader fork basis
- **zipline-reloaded** — three structural mismatches (no 1h, no options, no crypto) for our scope
- **Backtesting.py** — single-asset toy by design; AGPL viral; structurally blocks Phase 4-5
- **freqtrade Hyperopt as strategy generation** — no walk-forward / DSR / PBO; conflicts with our anti-p-hacking discipline
- **Whole TradingAgents / TradingAgents-CN framework adoption** — research-grade single-day decision flow, no statistical-significance machinery
- **FinGPT as Proposer/Critic replacement** — paradigm mismatch + equity-only training distribution + heavier infra than Sonnet at our scale

---

## Section H — Open Questions / Next-Step Options

### H.1 Immediate decisions for Charlie

1. **Which candidates from Section G to promote to TECHNIQUE_BACKLOG.md?** Default: route this doc to ChatGPT + Claude advisor for cross-review, integrate convergent picks. Charlie register authorizes final promotion.
2. **What to do with spike artifacts at `/tmp/vectorbt_spike/`?** Options: (a) leave (auto-cleaned on reboot), (b) promote to `docs/discussion/spike_artifacts/2026-05-11_vectorbt/`, (c) keep as reference until next spike work.
3. **§29 BTC engine analysis register output:** does this doc satisfy "framework refactor evaluation at analysis register"? If yes, future Phase 3 entry scoping can cite this as input. If no, what's missing?

### H.2 Spike work that would tighten analysis (NOT now, future cycles)

- **Spike B**: PHASE2C_12 197-candidate batch vectorbt vs Backtrader rank correlation (1-2 weeks; validates "pre-filter mode" claim)
- **Spike C**: Full PHASE2C SEALED arc byte-equivalent on vectorbt (3-4 weeks; provides hard evidence for §29 implementation authorization)
- **Spike D**: Walk-forward multi-window vectorbt validation (corrected-WF lineage on new engine)
- **Spike E**: AND/OR composite + short trades + multi-asset (broadens operator coverage)

### H.3 Methodology consolidation candidates surfaced this session (not codified now)

- **External-repo survey discipline** — the "ten-repo parallel subagent + per-repo structured analysis + cross-synthesis + spike validation" workflow worked well; potential §A3 (or wherever new methodology entries go) candidate at next consolidation cycle
- **Analysis-register-discipline empirical escape hatch** — Spike A demonstrated that **time-boxed hands-on validation IS the right exit from analysis register**, not "stay in analysis forever." This is consistent with §29 intent but worth codifying as concrete pattern.

---

## Section I — Closing notes

**This document is the working draft.** Promotion to TECHNIQUE_BACKLOG.md, formal §29 evaluation, or any implementation work requires:
1. Charlie register approval for specific entries (G.1-G.4)
2. Per-fix adjudication discipline preserved (no bulk-accept)
3. ChatGPT / Claude advisor cross-routing per `feedback_decision_options_plaintext.md`
4. Anti-momentum-binding strict reading: SEAL of this discussion does NOT authorize successor cycle or implementation

**Cumulative session record (for context preservation):**
- 10 parallel subagent surveys → structured per-repo analysis
- 4 parallel subagent successor evaluations → Backtrader 3-year-stale finding
- 5-path build-own analysis → rev 1 strategy (3-engine split, 2+1 precise)
- Spike A empirical validation → byte-equivalent N+1 + 24-bar deferral confirmed
- Wrapper API draft revised from theoretical (2-3w) to empirical (1.5-2w)

**End of working draft v1 — Section J appended below (Cross-Review Outcomes 2026-05-11).**

---

## Section J — Cross-Review Outcomes (2026-05-11, same session)

This survey was routed by Charlie for cross-review by ChatGPT and Claude advisor. Both replies were received same session, adjudicated, and the load-bearing items executed. This section records the adjudication trail.

### J.1 Two-reviewer divergence pattern

The two reviewers operated at **different registers**, and that explains most of their divergence:

- **ChatGPT** operated at **content-quality register** — assessing each candidate on epistemic merit, methodology fit, anti-rationalization safety.
- **Claude advisor** operated at **canonical-artifact-compliance register** — assessing whether each candidate respects TECHNIQUE_BACKLOG.md's stated scope clause + phase numbering + redundancy with existing entries.

Both registers are valid; **Claude advisor's register was load-bearing for THIS adjudication** because the question on the table was "what enters TECHNIQUE_BACKLOG.md," and that's a register-classification question, not a content-quality question.

### J.2 Three Claude-advisor structural claims — verified true against canonical

| Claim | Verification | Result |
|---|---|---|
| TECHNIQUE_BACKLOG.md Scope clause excludes infrastructure decisions | Line 5: *"Techniques only. Does not track infrastructure decisions, deliverable sign-offs, or blueprint content"* | ✅ TRUE |
| §1 phase numbering rejects stocks as scope at Phase 6+ | Lines 36-40: *"Phase 4 — Multi-crypto spot (BTC / ETH / SOL / etc.) ... Phase 6+ — Stocks (currently REJECTED as scope)"* | ✅ TRUE |
| §2.6.2 already includes `delay` operator, making proposed Ref() redundant | Line 188: *"Operators include: ... delta, decay_linear, ... delay, signedpower, sign, abs, log"* | ✅ TRUE |

This changed the adjudication basis. My own Section A "expanded scope" framing (assuming BTC + stocks + options authorized) was wrong — Charlie's verbal scope expansion is a register-class-distinct event from canonical artifact change; assuming the former entailed the latter is a precondition-skip pattern.

### J.3 Per-candidate adjudication outcome

| # | Candidate | ChatGPT verdict | Claude advisor verdict | **Final adjudicated outcome** |
|---|---|---|---|---|
| G.1.1 | `disciplined_pf_from_signals()` wrapper | ADD (DEFER) | REJECT (§29) | **REJECT for backlog** — infrastructure register; goes to §29 analysis register / future ENGINE_DECISION register |
| G.1.2 | `Ref()` lag operator | ADD | REJECT (redundant with §2.6.2 `delay`) | **REJECT** — already covered by §2.6.2 |
| G.1.3 | Bull/Bear debate D7b backend | ADD (experimental) | REJECT (agent architecture) | **REJECT for backlog** — D7b sub-spec scope; *underlying adversarial-composition principle NOT yet PRINCIPLE-ONLY codified* (see J.4 below) |
| G.1.4 | Persona-conditioned Critic | ADD | REJECT (architecture + roleplay risk) | **REJECT** — both registers agree |
| G.1.5 | Reflection-memory injection | Defer | REJECT (PHASE2C_14 sub-spec scope) | **REJECT for backlog** — already in PHASE2C_14 sub-spec §2.1 anti-anchoring discipline |
| G.2.6 | Multi-metric leaderboard composite | ADD (lexicographic) | REJECT (reporting convention) | **DEFER to Phase 3 evaluation-gate sub-spec drafting cycle** (see J.4 self-PUSHBACK) |
| G.2.7 | Dry-run paper trade harness | Later | REJECT (infra) | **REJECT for backlog** — Phase 3 deliverable scope |
| G.2.8 | nautilus_trader paper→live POC | ADD (conditional) | REJECT (§29) | **REJECT for backlog** — §29 register |
| G.3.9 | OpenBB equity + derivatives | Later | REJECT (scope mismatch + infra) | **REJECT for backlog** — stocks scope not authorized; infra register |
| G.3.10 | Lean as Phase 5 options engine | REJECT | REJECT (§29) | **REJECT for backlog** — §29 register |
| G.3.11 | Qlib RD-Agent reference read | (no flag) | REJECT ("Cool idea, someday") | **REJECT** — backlog explicit rule |
| **G.4.12** | **Kronos zero-shot factor family** | DO NOT ADD YET | **ADD as §6 OPEN QUESTIONS conditional** | ✅ **ADDED to TECHNIQUE_BACKLOG.md §6.2** with Claude advisor's additional pretraining-transferability pushback |
| G.4.13 | Successor framework evaluation track | REJECT | REJECT (§29) | **REJECT for backlog** — §29 register |

**Net result:** 1 of 13 candidates entered canonical TECHNIQUE_BACKLOG.md (§6.2 Kronos). The other 12 are register-classified to their proper homes (§29 / sub-spec scope / already-covered / deferred-pending-scope-reopen).

### J.4 Self-PUSHBACK on my own prior adjudication

Two corrections to my mid-session adjudication. The CONCLUSIONS for these two items did not change, but the RATIONALE / placement was wrong.

**G.1.3 Bull/Bear debate Critic rationale — corrected.** I claimed "§3.7 + §3.10 PRINCIPLE-ONLY 覆盖" the adversarial-debate principle. On verification:
- **§3.7 Independent weak-signal composition (Naive Bayes pattern)** is **independent** signals + multiplicative aggregation under independence. The math is joint posterior under independence assumption.
- **§3.10 Low pairwise correlation among shared-primitive alphas** is correlation, not adversarial mechanism.

Bull/Bear debate is *adversarial / minimax / argumentation-theoretic*, which is a different mathematical structure than Naive-Bayes independence. **The principle is NOT yet PRINCIPLE-ONLY codified**. The REJECT-for-current-backlog conclusion stays (debate backend is D7b sub-spec scope), but adversarial-composition is a legitimate future PRINCIPLE-ONLY candidate, separate cycle to evaluate.

**G.2.6 Multi-metric leaderboard — placement corrected.** My PARTIAL adjudication proposed appending as a sub-bullet under §2.2.3 DSR entry. On second look, lexicographic-vs-weighted is a *Phase 3 evaluation gate* design question (which metrics to rank by), orthogonal to DSR (which deflates single Sharpe under multiple-testing). Cleaner placement: **defer to Phase 3 evaluation gate sub-spec drafting cycle**, citing ChatGPT's "lexicographic + sparse + no weighted-optimization" refinement as input. No backlog entry; no §2.2.3 sub-bullet.

### J.5 Scope-binding meta-issue resolution — Path α

Both reviewers converged on **Path α**: do NOT silently expand stocks/equity into canonical scope.

- **Path γ rejected** — verbal scope expansion ≠ canonical artifact change. Treating it as such opens a "one-sentence overrides sealed entries" precedent more costly than any single scope expansion.
- **Path β deferred** — formal §5.4 reopen cycle is the structurally correct trigger, but should fire when there's an actual Phase 4 entry demand, not now. Phase 5 attribution is in progress.

**Operative consequence:** all "Phase 4 stocks" anchors in this survey are unauthorized until §5.4 is formally reopened. Phase 4 = multi-crypto only (BTC / ETH / SOL etc.) per canonical §1. Phase 5 derivatives (crypto options, perps) scope is already approved and uncontested.

### J.6 Carry-forward observations (NOT codified this session)

Per Phase 5 attribution scope binding §4.1 ("no new methodology codification") and METHODOLOGY_NOTES §20.6 Strong-tier promotion bar criteria (≥10 instances + ≥3 cycles), these are observations only:

- **Verbal scope statement ≠ canonical change.** Treating verbal expansion as working assumption without cross-checking canonical artifact is a precondition-skip pattern (cf. METHODOLOGY_NOTES §5). Single instance this session; candidate §5 case-study augmentation at future methodology consolidation cycle.
- **"Convergent picks" ≠ valid merge criterion.** Reviewer convergence is heuristic; argument quality is the standard. Single instance this session; observation-only.
- **Two-reviewer register-divergence pattern.** ChatGPT operating at content-quality register vs Claude advisor operating at canonical-compliance register both produce useful but non-overlapping findings. Cross-cycle accumulation observation candidate.

### J.7 Codex routing — Path 1 (SKIP) per memory

Claude advisor recommended firing Codex for adjudication precision review. Memory [`feedback_codex_review_scope.md`](.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md) explicitly excludes Codex from scoping/deliberation docs (this adjudication is deliberation, not substantive code/closeout). Charlie register Path 1 authorization preserves the memory discipline. If "adjudication precision" routing is desired in future, the memory should be updated first (not break the rule one-off).

### J.8 Executed this session

1. ✅ **TECHNIQUE_BACKLOG.md §6.2 Kronos** added as OPEN QUESTIONS conditional entry with cutoff + transferability preconditions
2. ✅ **Last updated** date bumped to 2026-05-11
3. ✅ **Spike A artifacts** preserved at `docs/discussion/spike_artifacts/2026-05-11_vectorbt/` (6 scripts + README.md)
4. ✅ **This Section J** appended

### J.9 Deferred to future session(s)

- Adjudication on **Path β formal §5.4 reopen** when Phase 4 entry demand materializes (NOT this session)
- **METHODOLOGY_NOTES §5 case study** (verbal-scope-statement precondition-skip pattern) at future methodology consolidation cycle, if cross-cycle instance count accumulates
- **Adversarial-composition PRINCIPLE-ONLY candidate** (G.1.3 rationale correction) at future principle-codification cycle
- **G.2.6 multi-metric lexicographic ranking** at Phase 3 evaluation gate sub-spec drafting cycle
- **Spike B / C / D / E** (197-candidate batch / full SEALED arc regression / multi-window WF / AND-OR + short + multi-asset) if BTC engine path is authorized at future §29 evaluation register

**End of working draft v2 — 2026-05-11.**
