# TECHNIQUE_BACKLOG.md

**Purpose:** Living roadmap of statistical / mathematical techniques evaluated for the BTC Alpha Pipeline. Every entry here has been through the 5-part evaluation (methodology / context fit / placement / pushback / actionable-now) and assigned to a phase. This document is updated when new articles / ideas / concepts are discussed.

**Scope:** Techniques only. Does not track infrastructure decisions, deliverable sign-offs, or blueprint content — those live in `CLAUDE.md` and phase sign-off notes.

**Maintained by:** Claude (advisor role) with Charlie's approval. New entries are inserted only after explicit discussion and scope fit.

**Last updated:** 2026-04-22 (added entries from Article on dual-factor mining + Articles on minimum information entropy + Kakushadze 2015 "101 Formulaic Alphas")

---

## 0. How to read this document

Each entry has:

- **Name** — canonical name of technique / model / concept
- **One-line description** — what it actually does
- **Fit verdict** — `APPLICABLE` / `PRINCIPLE-ONLY` / `DEFER` / `REJECTED`
- **Target phase / deliverable** — where it enters the project, if applicable
- **Rationale** — why this placement, what it unblocks, what pushback was considered
- **Source** — article / paper / conversation that surfaced it

Entries graduate from `DEFER` → `APPLICABLE` as phases advance. `REJECTED` entries stay for historical record so we don't re-litigate.

**Rule:** Nothing gets added here without a specific phase / deliverable anchor. "Cool idea, someday" is not an entry — if we can't say where it goes, it's not on the list.

---

## 1. Current phase context

**As of 2026-04-20:** Phase 2B D7 Stage 2d in progress (AI critic production-scale live fire, N=199 replay). D8 (Orchestrator / research loop) not yet started. Post-Phase-2B work includes eventual pivot to multi-crypto (Phase 4-ish) and derivatives (Phase 5-ish) per strategic roadmap discussion on 2026-04-20.

Phases referenced in this document use the following numbering (strategic roadmap, not code):

- **Phase 2B** — AI agent alpha discovery, single-asset BTC spot
- **Phase 3** — Paper trade / live small-capital deployment, single-asset BTC spot
- **Phase 4** — Multi-crypto spot (BTC / ETH / SOL / etc.)
- **Phase 5** — Crypto derivatives (Deribit options, Binance perps)
- **Phase 6+** — Stocks (currently REJECTED as scope)

---

## 2. APPLICABLE — queued for insertion

### 2.1 Phase 2B (current) — small, non-scope-creeping insertions

These are cheap adds that fit the current Stage 2d / D8 timeframe without expanding scope.

#### 2.1.1 `bootstrap_sharpe_ci()` stub in `metrics.py`
- **Fit:** PRINCIPLE-ONLY placeholder; full implementation deferred to Phase 3 gate
- **What:** Empty function signature + docstring only. Implementation later.
- **Why now:** Avoids schema refactor later when stationary bootstrap becomes mandatory for live-deployment gate
- **Pushback considered:** Charlie's scope discipline would normally kill this. Justified only because signature-only cost is near-zero and future insertion requires touching the same module
- **Source:** 2026-04-20 discussion on martingale / concentration inequalities

#### 2.1.2 `residual_mds_pvalue` nullable column in experiment registry
- **Fit:** APPLICABLE, field only; enforcement deferred
- **What:** One nullable column in the registry schema. Backfilled post-hoc when MDS test is implemented.
- **Why now:** Same rationale as 2.1.1 — schema touch now avoids migration later. Also serves as the "incremental information test" field discussed for ensemble gating
- **Pushback considered:** Could be deferred to Phase 3 and added then. Accepted risk is minor.
- **Source:** 2026-04-20 discussion on OpenAlphas article (orthogonalization screening) + martingale discussion

### 2.2 Phase 3 (paper trading / live small capital) — pre-deployment validation gate

These are the validation gates that must exist before any capital is risked. They are NOT premature for Phase 2B because Phase 2B is discovery; they are mandatory for Phase 3 because Phase 3 is deployment.

#### 2.2.1 Stationary Bootstrap (Politis-Romano 1994) for Sharpe CI
- **Fit:** APPLICABLE
- **What:** Block bootstrap variant that randomizes block length; gives valid CI for time-series statistics with unknown serial correlation structure
- **Why Phase 3:** Point-estimate Sharpe lies about precision. iid bootstrap understates variance because returns have serial correlation. Stationary bootstrap is the standard fix. Required before any live deployment decision.
- **Pushback considered:** Block bootstrap (fixed length) also works; stationary variant is preferred for robustness to block-length choice
- **Source:** 2026-04-20 martingale discussion (as real-answer to "what should we use instead of Doob's inequality")

#### 2.2.2 PBO (Probability of Backtest Overfitting) — Bailey & López de Prado 2014
- **Fit:** APPLICABLE
- **What:** Quantifies probability that best-in-sample strategy underperforms median out-of-sample via combinatorial symmetric cross-validation
- **Why Phase 3:** D7 critic filters individual hypotheses; PBO measures population-level overfitting across the batch that Phase 2B produces. Complementary to DSR, not redundant — DSR corrects single-strategy Sharpe for multiple testing, PBO tests whether the ranking itself is reliable
- **Pushback considered:** Requires multiple strategies with same CV structure — naturally satisfied by Phase 2B output
- **Corrected-engine dependency (Section RS):** PBO consumes walk-forward outputs and is therefore subject to the WF test-boundary semantics correction. The implementation MUST:
  - Operate only on WF artifacts produced by an engine descended from tag `wf-corrected-v1` (head commit `3d24fcb`, anchored on engine fix `eb1c87f`).
  - Call `check_wf_semantics_or_raise(summary, artifact_path=...)` from `backtest/wf_lineage.py` on every WF summary before computing PBO.
  - Refuse any artifact lacking `wf_semantics: corrected_test_boundary_v1` (those live quarantined under `data/quarantine/pre_correction_wf/`).
  - See `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md` Section RS for the canonical hard prohibition.
- **Source:** 2026-04-20 martingale discussion

#### 2.2.3 Deflated Sharpe Ratio — post-hoc evaluation (already partly built)
- **Fit:** APPLICABLE (partially built in Phase 1B as `evaluate_dsr.py`)
- **What:** Corrects Sharpe for multiple-testing inflation using number of trials and trial-Sharpe variance
- **Why Phase 3:** Phase 2B D6 produces 200 hypotheses per batch; D8 research loop will produce thousands. DSR is the standard deflation.
- **Status:** Heuristic `sqrt(2*ln(N))` screen exists in Phase 1B. Full DSR is already scoped as post-hoc script.
- **Corrected-engine dependency (Section RS):** DSR consumes walk-forward Sharpe values directly. The implementation MUST:
  - Operate only on WF artifacts produced by an engine descended from tag `wf-corrected-v1` (head commit `3d24fcb`, anchored on engine fix `eb1c87f`).
  - Call `check_wf_semantics_or_raise(summary, artifact_path=...)` from `backtest/wf_lineage.py` on every WF summary before computing DSR.
  - Refuse any artifact lacking `wf_semantics: corrected_test_boundary_v1` (those live quarantined under `data/quarantine/pre_correction_wf/`).
  - The existing Phase 1B heuristic `sqrt(2*ln(N))` screen in `evaluate_dsr.py` MUST be updated to call the consumer-side helper before its first use against corrected artifacts.
  - See `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md` Section RS for the canonical hard prohibition.
- **Source:** Original Phase 1B design; re-confirmed in 2026-04-20 discussion

#### 2.2.4 Combinatorial Purged K-Fold CV (AFML Ch. 7, López de Prado)
- **Fit:** APPLICABLE
- **What:** Purges training observations whose labels overlap the test set, applies embargo to prevent leakage, uses combinatorial splits to generate multiple test paths
- **Why Phase 3:** Any strategy with lookback-window features that touches the test fold has leakage under standard K-fold. Purging + embargo is the gold standard. Essential once AI-agent-generated strategies include ML-style feature engineering.
- **Pushback considered:** Walk-forward (already built) is simpler but gives fewer OOS paths. Both have a place; CPCV is more statistical-power-efficient for comparing strategies, walk-forward is more honest about deployment sequence.
- **Corrected-engine dependency (Section RS):** When CPCV's per-fold metrics are compared against the existing walk-forward results (e.g., to check CPCV vs WF agreement, or to use WF metrics as a within-fold reference), the WF side of that comparison MUST come from the corrected engine. The implementation MUST:
  - Operate only on WF artifacts produced by an engine descended from tag `wf-corrected-v1` (head commit `3d24fcb`, anchored on engine fix `eb1c87f`).
  - Call `check_wf_semantics_or_raise(summary, artifact_path=...)` from `backtest/wf_lineage.py` on every WF summary it ingests for cross-comparison.
  - Refuse any artifact lacking `wf_semantics: corrected_test_boundary_v1` (those live quarantined under `data/quarantine/pre_correction_wf/`).
  - CPCV's own per-fold WF-style metrics (when CPCV runs the corrected `run_walk_forward` internally per fold) inherit the corrected semantic by construction; CPCV's implementation must not call the engine via any pre-correction code path.
  - See `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md` Section RS for the canonical hard prohibition.
- **Source:** 2026-04-20 martingale discussion + earlier Phase 1B planning

### 2.3 Phase 3 — risk and sizing layer (before any real capital)

#### 2.3.1 POT / GEV (Peaks-Over-Threshold / Generalized Extreme Value) tail modeling
- **Fit:** APPLICABLE
- **What:** Extreme Value Theory — models the tail of a distribution parametrically (GPD for POT; GEV for block maxima) instead of assuming Gaussian
- **Why Phase 3:** Gaussian VaR catastrophically underestimates crypto tail risk. LUNA, FTX, COVID crash are all 10+ sigma events under Gaussian. POT-based VaR / ES is the correct framework.
- **Pushback considered:** Historical VaR is a cheap alternative but throws away parametric structure. POT uses the Gaussian-violated tail explicitly.
- **Source:** 2026-04-20 classical models discussion

#### 2.3.2 Fractional Kelly sizing
- **Fit:** APPLICABLE
- **What:** Position sizing at 0.25–0.5× full Kelly rather than full Kelly; caps drawdown sensitivity to edge-estimate error
- **Why Phase 3:** Full Kelly blows up when edge is overestimated. Fractional Kelly is the industry-standard hedge against estimation error in edge.
- **Pushback considered:** Kelly at all requires a probabilistic edge estimate — if strategy doesn't output one, use volatility-targeting instead
- **Source:** 2026-04-20 classical models discussion

### 2.4 Phase 3 / 2B late — Martingale concept as statistical tool

#### 2.4.1 Martingale Difference Sequence (MDS) test on strategy residuals
- **Fit:** APPLICABLE (as null hypothesis test, not as pricing construct)
- **What:** Escanciano-Velasco (2006), Hong (1999) spectral test. Tests whether a series is a martingale difference sequence — i.e., whether conditional mean given past information is zero.
- **Why:** Rigorous test of "has this signal exhausted the predictability in the residual?" Stronger than R² or Sharpe — directly tests the martingale property that defines absence of predictable structure.
- **Placement:** Phase 2B late (as D8 diagnostic) or Phase 3 (as ensemble-inclusion gate). Field `residual_mds_pvalue` is stubbed in registry per 2.1.2.
- **Corrected-engine dependency (Section RS):** MDS operates on strategy residuals derived from walk-forward equity curves and trade ledgers. The WF source must be corrected. The implementation MUST:
  - Operate only on WF artifacts produced by an engine descended from tag `wf-corrected-v1` (head commit `3d24fcb`, anchored on engine fix `eb1c87f`).
  - Call `check_wf_semantics_or_raise(summary, artifact_path=...)` from `backtest/wf_lineage.py` on every WF summary before computing residuals.
  - Refuse any artifact lacking `wf_semantics: corrected_test_boundary_v1` (those live quarantined under `data/quarantine/pre_correction_wf/`).
  - Residuals computed against pre-correction equity curves are statistically meaningless (the equity curve is contaminated by train-period PnL); MDS p-values from such residuals must not be computed or reported.
  - See `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md` Section RS for the canonical hard prohibition.
- **Source:** 2026-04-20 martingale discussion

### 2.5 Phase 2B late / Phase 3 — Volatility modeling

#### 2.5.1 GARCH family (GARCH / EGARCH / GJR-GARCH)
- **Fit:** APPLICABLE
- **What:** Conditional heteroscedasticity models. EGARCH / GJR-GARCH capture the leverage effect (negative shocks increase vol more than positive shocks — strongly present in crypto).
- **Why Phase 2B late / Phase 3:** BTC volatility clustering is textbook. Vol forecasts feed directly into position sizing, stop placement, regime gating. Not useful as alpha source alone, but essential for risk layer.
- **Pushback considered:** HAR-RV is arguably better for crypto because RV is directly observable. GARCH stays on the list because it's robust, cheap, and well-understood; HAR-RV (2.5.2) is the preferred primary.
- **Source:** 2026-04-20 classical models discussion

#### 2.5.2 HAR-RV (Corsi 2009, Heterogeneous Autoregressive Realized Volatility)
- **Fit:** APPLICABLE — HIGH PRIORITY for vol modeling
- **What:** Linear regression of realized vol on daily, weekly, and monthly lagged realized vol. Captures long-memory structure in vol without GARCH's iterative estimation.
- **Why Phase 2B late / Phase 3:** Crypto match is excellent — 1h realized vol has clear multi-scale persistence. Simple to implement (OLS), forecasts well, integrates cleanly into regime-dependent position sizing.
- **Pushback considered:** Requires RV which requires intraday data. You have 1h bars since 2020 — fine.
- **Source:** 2026-04-20 classical models discussion

#### 2.5.3 Regime detection (HMM or Bayesian online change-point)
- **Fit:** APPLICABLE
- **What:** HMM assigns each bar to a latent regime; online change-point detects regime shifts as they happen.
- **Why Phase 2B late / Phase 3:** BTC bull / bear / consolidation regimes are real and strategies perform differently across them. Regime-conditional metrics give more honest evaluation than pooled.
- **Pushback considered:** HMM is often overfitted to past data with unstable regime labels. Bayesian online CP (e.g., Adams-MacKay 2007) is more honest about "did the regime just change" question.
- **Placement:** HMM as post-hoc diagnostic in Phase 2B; online CP as deployment tool in Phase 3
- **Source:** 2026-04-20 classical models discussion + earlier discussions

#### 2.5.4 CDF / percentile-of-own-history factor
- **Fit:** APPLICABLE
- **What:** A factor that records, for the current bar, the empirical-CDF percentile of a chosen quantity (return, realized vol, volume, range expansion, etc.) within its own historical distribution. "Where does today's move sit in this asset's own history?" Typical use: gating (only act when percentile is in a specified band) or as a soft feature in an ensemble.
- **Why now:** Legitimate transformation. It encodes "anomaly relative to self" without leaning on cross-sectional comparison (which you don't have until Phase 4). Adds genuine structural information that lookback-window factors don't capture.
- **Placement:** Factor registry expansion. Eligible to enter the D6 grammar once specified with explicit window length, distribution-construction method (rolling empirical vs expanding bootstrap vs parametric fit), and warmup.
- **Pushback considered:** Distribution-construction choice matters a lot — rolling empirical CDF (e.g., trailing 90 days) is honest; bootstrap-with-replacement loses serial structure; parametric fit (Gaussian / Student-t) imposes assumptions BTC violates. Pick rolling empirical unless you have reason not to. Also: avoid retrospective "sweet spot" parameter discovery (e.g., the article's `0.7 < CDF < 0.9` claim) — any band must be specified from theory or pre-registered before backtest.
- **Source:** 2026-04-22 minimum information entropy articles (extracted as the one transferable factor; full framework rejected — see §5.6)

### 2.6 Phase 2B late / D8 — meta-analysis on D6 hypothesis output

#### 2.6.1 Parameter-clustering meta-analysis across top-N D6 hypotheses
- **Fit:** APPLICABLE
- **What:** After D7 critic filtering and walk-forward evaluation of a D6 batch, analyze the parameter distribution across the top-N surviving hypotheses (e.g., top 20 by Sharpe, top 50 by return). If shared parameter values cluster across multiple top performers (e.g., 80% of top-20 use a holding period in 30–60 minutes, or 70% use the same threshold range), those clustered values are robustness-supported in a way single-best-Sharpe ranking does not capture.
- **Why now:** D6 produces 200 hypotheses per batch; D8 will produce thousands. Single-best-Sharpe ranking is fragile (the best is often the luckiest of the noise distribution). Parameter clustering across the top tail is a cheap robustness diagnostic that uses the full population D6 already generates. Doesn't require new infrastructure — runs on existing batch artifacts.
- **Placement:** D8 orchestrator design as a post-batch meta-analysis report. Could also surface clustered-parameter regions back to D6 as a future prompt-conditioning signal, but that's downstream.
- **Pushback considered:** Risk is mistaking clustering for robustness when it's just D6 prompt bias (e.g., the proposer keeps proposing similar values because the prompt anchors it). Mitigate by checking whether clustered values are also clustered in the D6 output *before* D7+walk-forward filtering; if cluster only appears post-filter, that's signal; if it's already in raw D6 output, the prompt is doing the work.
- **Source:** 2026-04-22 dual-factor mining article (this is the one extractable insight; full framework largely subsumed by your existing pipeline — see §3.8)

#### 2.6.2 WorldQuant 101 Alphas — time-series operator vocabulary expansion
- **Fit:** APPLICABLE — HIGH PRIORITY for D6 grammar evolution
- **What:** Systematically incorporate the time-series operator vocabulary used in Kakushadze (2015) "101 Formulaic Alphas" into the factor registry / DSL. Operators include: `ts_min`, `ts_max`, `ts_argmax`, `ts_argmin`, `ts_rank`, `delta`, `decay_linear`, `correlation` (time-series), `covariance` (time-series), `stddev`, `sum`, `product`, `delay`, `signedpower`, `sign`, `abs`, `log`. These are well-tested primitives from a real production alpha library covering ~20 years of WorldQuant research.
- **Why now (after Stage 2d sign-off):** Your current DSL operator set is bounded by what was needed for Phase 1 baselines plus what Phase 2A factor expansion required. The WorldQuant operator vocabulary is a known-good superset that gives D6 proposer richer expressive power without hardcoding any specific alpha. The proposer can recombine these primitives in novel ways while inheriting the structural soundness of an established vocabulary.
- **Placement:** D6 grammar expansion at the factor registry / DSL compiler layer. Each operator added must follow your existing D1 governance — docstring, warmup, output dtype, null policy, causality tests. Operators are added one or two at a time with full test coverage, not bulk-imported.
- **Pushback considered:** (a) Expansion may push proposer toward more complex compositions of familiar patterns rather than genuine novelty — mitigate by running a small-scale (N=20-50) before/after experiment comparing novelty distribution under expanded vs current vocabulary before production rollout. (b) Some operators like `decay_linear` and `signedpower` introduce non-linearity that may interact with your causality tests and warmup conventions in non-obvious ways — handle by per-operator validation. (c) `correlation`/`covariance` here are time-series, not cross-sectional (different from the `rank` operator in §4.1.9) — naming discipline matters.
- **Source:** Kakushadze, Z. (2015) "101 Formulaic Alphas," arXiv:1601.00991 (2026-04-22 discussion)

#### 2.6.3 Single-asset-compatible WorldQuant 101 alpha subset
- **Fit:** APPLICABLE — moderate priority
- **What:** From the 101 alphas in Kakushadze (2015), filter the subset (~15-25) that does not depend on cross-sectional `rank()`, `indneutralize()`, `scale()`, or market-cap data. These are the alphas that operate purely on single-asset OHLCV / VWAP / returns and transfer directly to single-asset BTC. Examples include Alpha#101 (`(close - open) / ((high - low) + .001)`), Alpha#12 (`sign(delta(volume, 1)) * (-1 * delta(close, 1))`), Alpha#41 (`((high * low)^0.5) - vwap`), and others identified by manual reading.
- **Why now:** Three uses. (a) Expand baseline strategy collection beyond Phase 1's four — gives D7 critic and walk-forward more reference points. (b) Serve as prior-knowledge corpus for D7 critic — when proposer outputs structurally resemble a known WorldQuant alpha pattern, that's relevant context for `structural_variant_risk` scoring. (c) Seed candidate pool for eventual D8 ensemble layer.
- **Placement:** Strategy registry expansion (baselines folder) + D7 critic prior-knowledge corpus. Not a D6 input — these are evaluated as fixed strategies, not generated by proposer.
- **Pushback considered:** (a) These alphas are 2010-2013-era equity alphas; equity alpha decay over 13 years is well-documented, and crypto market structure is fundamentally different from US equities. Do not assume any specific alpha will be profitable on BTC — they are reference patterns, not deployable strategies. (b) Reading exercise must be done carefully — some alphas appear single-asset compatible but use `rank` deep inside a composition, which makes them cross-sectional regardless of the outer structure.
- **Source:** Same paper as 2.6.2

---

## 3. PRINCIPLE-ONLY — internalize but don't implement

These are concepts that inform design but don't become modules. They appear in documentation, review checklists, and reviewer judgment — not in code.

### 3.1 Orthogonalization / incremental-information screening
- **From:** OpenAlphas article on Alpha factor library reduction (2026-04-19 discussion)
- **Principle:** Before adding a new signal to an ensemble, regress its prediction against the residuals of existing signals. If the new signal has no incremental predictive power after orthogonalization, it's redundant.
- **Where it shows up:** D8 ensemble-gating design (future); `residual_mds_pvalue` field in registry (2.1.2)
- **Why not a module:** Full Fama-MacBeth requires cross-sectional structure you don't have until Phase 4. The principle applies immediately; the technique waits.

### 3.2 Risk premium vs. genuine alpha distinction
- **From:** Chinese quant article on "why not Codex for quant" (2026-04-20 discussion)
- **Principle:** Claimed excess return is often uncompensated tail risk in disguise (short vol structures, crash-sensitive longs). A high Sharpe before the tail event tells you nothing.
- **Where it shows up:** D8 ensemble acceptance criteria; Phase 3 deployment gate; Phase 5 variance risk premium decisions
- **Why not a module:** This is reviewer judgment, not a computation. But it must be live in every strategy acceptance conversation.

### 3.3 Falsifiability and anti-hindsight commit ordering
- **From:** Your own Phase 2B D7 sign-off discipline
- **Principle:** Pre-register expectations before running; commit-order evidence so post-hoc rationalization is impossible; treat failed predictions as scientific wins.
- **Where it shows up:** Already embedded in Phase 2B D7 Stages 2a–2d. Must carry into D8 and Phase 3.
- **Why here:** Listed explicitly so it's not lost when D7 sign-off docs age out of active reference.

### 3.4 Martingale property as null hypothesis
- **From:** 2026-04-20 Doob / Kolmogorov discussion
- **Principle:** Alpha discovery is the search for violations of martingale property under P-measure. Classical option-pricing uses martingales in Q-measure as a construct; for spot directional trading, martingale is the null, not the tool.
- **Where it shows up:** MDS test (2.4.1); framing of "what counts as edge" in D8 design
- **Why not a module:** The concept informs design philosophy; the statistical test derived from it (MDS) is the module.

### 3.5 Doob decomposition
- **From:** 2026-04-20 Doob / Kolmogorov discussion
- **Principle:** Any submartingale decomposes as martingale + predictable increasing process. The predictable part is the drift / alpha. Gives mathematical precision to "what is edge."
- **Where it shows up:** Conceptual grounding for how D8 evaluates strategies as drift-extractors
- **Why not a module:** Pure conceptual grounding.

### 3.6 Strategy paradigm progression is not linear
- **From:** 2026-04-22 "four-stage roadmap" article discussion
- **Principle:** Indicators / factors / mathematical models / AI agents are coexisting tools, not evolutionary stages. Renaissance and Two Sigma operate across all of them simultaneously. Project decisions should be driven by "which tool fits the current scope" rather than "I should now graduate to the next stage." Resist articles that frame quant evolution as a personal hero's journey from naive to sophisticated — that framing is post-hoc rationalization, not roadmap.
- **Where it shows up:** Whenever an outside article implies "you should now move to X paradigm" — evaluate the technique on its merit for current scope, not on its position in someone else's narrative arc.
- **Why not a module:** Meta-principle for evaluating future content.

### 3.7 Independent weak-signal composition (Naive Bayes pattern)
- **From:** 2026-04-22 minimum information entropy articles
- **Principle:** Multiple weakly-predictive but **independent** features combine multiplicatively in Bayes — the joint posterior can be high-confidence even when each individual signal is weak. This is the legitimate mathematical core of "multi-dim composition" frameworks.
- **Critical caveat — independence is binding:** If features are correlated (which is almost always the case among quant signals), the multiplicative combination overstates joint confidence. Verify independence empirically (correlation matrix on raw signal series) before relying on multiplicative aggregation. In particular, signals derived from price / volume of the same asset are rarely independent.
- **Where it shows up:** D7 critic's multi-axis scoring (`structural_variant_risk`, `semantic_plausibility`, `semantic_theme_alignment`) operationalizes this differently — via independent LLM-judged dimensions rather than statistical signals. D8 ensemble logic should explicitly check pairwise correlation before combining signal sources multiplicatively.
- **Why not a module:** Principle, not technique. The technique is the correlation check before any multiplicative aggregation.

### 3.8 Five-criteria anti-overfitting checklist (Phase 3 deployment-readiness gate)
- **From:** 2026-04-22 dual-factor mining article
- **Principle:** Before any strategy is approved for live capital deployment, it must satisfy: (1) strong explainability — has a coherent economic / behavioral story, not a black-box pattern; (2) fixed specificity — uses pre-specified parameter values, not optimization-derived; (3) low-dimensional composition — built from ~5–6 core features, not dozens; (4) long-term robustness — performance stable across multi-year subsamples (weeks / months / quarters / years); (5) large sample — sufficient trades for statistical claims (~1000+ minimum, ideally more).
- **Where it shows up:** Phase 3 deployment-readiness checklist. Most criteria are already enforced upstream by current pipeline: D7 critic scores explainability (1); DSL fixed values not gradient-optimized (2); factor-count range 3–7 enforces low-dim (3); walk-forward enforces robustness (4). Sample-size criterion (5) is the one that needs explicit gate at Phase 3.
- **Pushback considered:** Criterion (4) "10-year robustness" is unattainable for crypto (~6 years of clean data exists at all). Adapt to "all available subsamples consistent" rather than fixed 10-year requirement.
- **Why not a module:** Checklist of things already partly enforced; explicit consolidation as Phase 3 deployment gate.

### 3.9 Vol-scaling regularity for alpha returns (R ~ σ^0.76)
- **From:** Kakushadze (2015) "101 Formulaic Alphas," Section 3.1 (cross-sectional regression of ln(R) over ln(σ))
- **Principle:** Across a population of 101 real production alphas, return scales sub-linearly with volatility according to R ~ σ^0.76. This is a robust empirical regularity confirmed by an earlier study on 4,000 alphas (Kakushadze & Tulchinsky 2015) — same exponent, different population. The intuition: higher-volatility alphas earn more in absolute terms but with diminishing efficiency per unit of risk.
- **Where it shows up:** Sanity check prior for D8 strategy evaluation and Phase 3 deployment review. If your generated strategies' (R, σ) pairs follow this scaling, that's normal alpha-population behavior; if a strategy claims much higher R for its σ (above the regression line), it is suspicious — either genuinely exceptional or a measurement artifact / lookback. If much lower R for its σ, it's likely capturing risk premium without efficiency.
- **Why not a module:** Conceptual prior, not a formal gate. Not enough data points in any single batch for tight statistical fit; the regularity is meaningful in aggregate across populations.

### 3.10 Low pairwise correlation among shared-primitive alphas — empirical justification for ensembling
- **From:** Kakushadze (2015) "101 Formulaic Alphas," Section 3 (mean pairwise correlation 15.9%, median 14.3%)
- **Principle:** 101 alphas all built from the same OHLCV / VWAP / returns primitives nonetheless show low average pairwise correlation (15.9% mean). Diversification benefits exist even when the universe of input data is shared, as long as the operator compositions differ structurally. This is the empirical foundation for why "combine many alphas into a mega-alpha" works in practice.
- **Where it shows up:** D8 ensemble layer design priors. Justifies investing in ensembling infrastructure even when all candidates share the same underlying data sources. Also informs D7 critic's `structural_variant_risk` axis — structural diversity is a genuine alpha source independent of input diversity.
- **Pushback considered:** This is equity, not crypto, and 2010-2013 not 2026. Crypto pairwise correlations among shared-primitive alphas may differ — but the principle that structural variation produces decorrelation independent of input variation is general. Re-measure on your own D6 batch output as soon as you have enough strategies generated to compute meaningful pairwise correlations.
- **Why not a module:** Empirical regularity used as design prior. Becomes an actual measurement on your data once D8 ensemble layer is being designed.

---

## 4. DEFER — valid techniques, wrong phase

These are real techniques that WILL be useful — but not now, and adding them now is scope creep.

### 4.1 Phase 4 (multi-crypto spot) queue

#### 4.1.1 Fama-MacBeth two-pass regression
- **What:** Cross-sectional factor pricing test. Run cross-sectional regression at each time t, then test the time-series of λ_k for significance.
- **Why defer:** Requires cross-section. Single-asset BTC has no cross-section. Becomes genuinely applicable only with BTC / ETH / SOL / ... basket.
- **Source:** OpenAlphas article (2026-04-19) + follow-up (2026-04-20)

#### 4.1.2 Cointegration (Engle-Granger, Johansen)
- **What:** Tests whether linear combinations of non-stationary series are stationary. Foundation for pairs trading.
- **Why defer:** No pair until you have multiple crypto.
- **Source:** 2026-04-20 classical models discussion

#### 4.1.3 Ornstein-Uhlenbeck process
- **What:** Mean-reverting SDE. Models cointegrated spreads.
- **Why defer:** Useful when you have spreads. Single BTC has no spread.
- **Source:** 2026-04-20 classical models discussion

#### 4.1.4 Ledoit-Wolf covariance shrinkage
- **What:** Shrinks sample covariance toward a structured target matrix; reduces estimation error at cost of small bias.
- **Why defer:** The shrinkage problem only bites when K (# of assets / signals) approaches T (# of observations). Single-asset doesn't have this problem. Becomes essential at multi-crypto scale with many signals.
- **Source:** OpenAlphas article (2026-04-19)

#### 4.1.5 Hansen's SPA test (Superior Predictive Ability)
- **What:** More powerful alternative to White's Reality Check for multiple-testing correction across strategies.
- **Why defer:** Overkill for current D7 critic gate. Becomes relevant when multi-asset strategy space expands combinatorially.
- **Source:** 2026-04-20 martingale discussion

#### 4.1.6 Kalman Filter for dynamic hedge ratio
- **What:** Recursive estimator for time-varying parameters in linear-Gaussian systems.
- **Why defer:** Single-asset use (adaptive MA length, etc.) is moderate value. Sweet spot is dynamic hedge ratio in pairs / basket trading.
- **Source:** 2026-04-20 classical models discussion

#### 4.1.7 Hawkes processes (cross-asset liquidation cascade modeling)
- **What:** Self-exciting point processes. Event intensity depends on history of previous events.
- **Why defer:** Crypto liquidation cascades are a natural application (one forced sell triggers margin calls triggers more forced sells). Requires cross-asset liquidation data to be genuinely useful.
- **Source:** 2026-04-20 classical models discussion

#### 4.1.8 Cross-sectional relative-strength factors
- **What:** Rank-within-basket transformations of strength signals — volume expansion rank, volatility-lift rank, activity-increase rank, return rank — across the multi-asset universe at each time t. Replaces "absolute strength is high" with "this asset is the highest-strength member of the basket right now."
- **Why defer:** Requires a basket. With single-asset BTC, "rank within basket" is degenerate (always rank 1 of 1). Becomes a primary class of factors at Phase 4 multi-crypto.
- **Why it's a real edge when applicable:** Absolute strength is dominated by market-wide moves (when everything pumps, everything looks strong); cross-sectional rank isolates idiosyncratic strength, which is closer to the actual alpha signal. This is the legitimate insight inside the entropy article's "断层第一" (breakout-rank-first) idea — it survives the framework rejection because the principle transfers.
- **Source:** 2026-04-22 minimum information entropy articles (extracted as a Phase 4 factor class; full framework rejected — see §5.6)

#### 4.1.9 Cross-sectional subset of WorldQuant 101 alphas (rank / indneutralize / cap-based)
- **What:** The majority of Kakushadze (2015) 101 alphas — those using `rank()` (cross-sectional rank across stocks at time t), `indneutralize()` (industry neutralization), `scale()` (cross-sectional rescaling), or `cap` (market capitalization). Estimated ~75-85 of the 101 fall into this bucket. These alphas are structurally cross-sectional and degenerate on a single asset (where rank = 1 of 1 always).
- **Why defer:** Requires multi-asset basket. At Phase 4 with BTC/ETH/SOL/etc., these become directly applicable — `rank` becomes meaningful, `cap` becomes available (crypto market cap is a standard data point), and basket-level normalization makes sense.
- **Sub-decision at Phase 4:** Industry neutralization (`indneutralize`) does not transfer cleanly to crypto. Crypto doesn't have a well-defined sector taxonomy comparable to GICS. Either (a) drop indneutralize alphas entirely, (b) use crypto category proxies (L1 / L2 / DeFi / meme / stablecoin) with explicit caveats about how arbitrary the categorization is, or (c) substitute basket-mean neutralization. Decision deferred to Phase 4 design.
- **Source:** Kakushadze (2015) "101 Formulaic Alphas" — see §2.6.2 / §2.6.3 for the time-series-compatible portion handled at Phase 2B

### 4.2 Phase 5 (crypto derivatives) queue

#### 4.2.1 Black-Scholes / Heston / SABR
- **What:** Option pricing models. BS assumes GBM; Heston adds stochastic vol; SABR adds skew.
- **Why defer:** You don't trade options yet. When you pivot to Deribit, these become primary tools.
- **Source:** 2026-04-20 classical models discussion

#### 4.2.2 Greeks / IV surface / volatility risk premium
- **What:** Standard options analytics; VRP strategies short IV when IV > RV systematically.
- **Why defer:** Same reason as 4.2.1. VRP is one of the most legitimate alpha sources in crypto (empirically strong), but requires options infrastructure.
- **Source:** 2026-04-20 classical models discussion

#### 4.2.3 Funding rate arbitrage (perpetuals)
- **What:** Perp funding rates create systematic arb when funding is extreme (basis trade with perps).
- **Why defer:** Requires perp infrastructure + proper hedging. Lower-hanging fruit than options but still Phase 5.
- **Source:** 2026-04-20 classical models discussion

#### 4.2.4 Itô integral / stochastic calculus as direct tool
- **What:** Continuous-time SDE framework.
- **Why defer:** Euler-Maruyama discretization occasionally useful in simulation. Otherwise the framework becomes practical only once you're handling derivatives where the SDE is the pricing model.
- **Source:** 2026-04-20 classical models discussion

### 4.3 Conditional on AUM / scale

#### 4.3.1 Almgren-Chriss optimal execution
- **What:** Optimal trade scheduling to minimize variance + expected cost under market impact.
- **Why defer:** Individual-scale AUM has negligible market impact on BTC. Becomes relevant only if trading size forces slicing.
- **Source:** 2026-04-20 classical models discussion

#### 4.3.2 Kyle's lambda / market microstructure
- **What:** Price-impact coefficient; microstructure analysis of informed vs. uninformed flow.
- **Why defer:** Same as 4.3.1 — individual-scale doesn't face this.
- **Source:** 2026-04-20 classical models discussion

### 4.4 Concentration inequalities — theoretically useful, empirically superseded

#### 4.4.1 Azuma-Hoeffding, Bernstein inequality
- **What:** Concentration bounds for martingale differences / bounded random variables.
- **Why defer / principle-only:** Azuma gives looser bounds than block bootstrap for Sharpe CI; Bernstein is tighter than Hoeffding for rare events but still looser than empirical tail estimation. Theoretically clean but empirically not the best tool.
- **Placement:** Note as principle — concentration bounds are how to think about tail probabilities formally, but stationary bootstrap + POT do the actual work.
- **Source:** 2026-04-20 martingale discussion

---

## 5. REJECTED — evaluated and declined

These are techniques that were considered and found unfit for this project's scope / scenario.

### 5.1 Doob's maximal inequality / Kolmogorov's inequality for price-range bounds
- **Why rejected:** Martingale property holds under Q-measure (risk-neutral), which is a pricing construct. Real-world BTC trading operates under P-measure, where alpha is precisely the search for non-martingale drift. Using martingale inequalities to bound a process you're trying to exploit as non-martingale is conceptually inverted. Additionally, Doob's bound is too loose for practical position-sizing decisions — bootstrap + EVT give much tighter empirical bounds.
- **Note:** The concept of martingale property survives as null hypothesis (see 3.4 and 2.4.1).
- **Source:** 2026-04-20 martingale discussion

### 5.2 Geometric Brownian Motion as BTC model
- **Why rejected:** BTC violates every GBM assumption — heavy tails, vol clustering, jumps, regime dependence. Using GBM directly as a model misrepresents the asset.
- **Note:** GBM survives as (a) null distribution for synthetic-data tests, (b) pedagogical baseline. Not as a real model.
- **Source:** 2026-04-20 classical models discussion

### 5.3 Option-pricing-style range estimation for spot directional trading
- **Why rejected:** Lookback / barrier option pricing uses running-max bounds because the payoff depends on the extremum. Spot directional P&L does not have that structure — you care about entry / exit prices, not the running max over the holding period.
- **Source:** 2026-04-20 martingale discussion

### 5.4 US equity trading as scale target
- **Why rejected:** Market is the most crowded in the world. Individual-scale against Citadel / Jane Street / Renaissance / HRT has structurally no edge. Crypto's 24/7 / no-T+1 / global access / retail composition gives individual quants a genuine structural advantage — abandoning that for US equities is a strictly negative trade.
- **Exception:** Revisit only with a specific, defensible thesis for why you'd have edge in a specific equity niche (e.g., small-cap crypto-correlated equities, specific event-driven setup). "Diversification" is not a thesis.
- **Source:** 2026-04-20 scaling strategy discussion

### 5.5 IC_IR maximization framework for weight optimization
- **Why rejected:** The framework assumes cross-sectional IC (rank correlation across assets). Single-asset time series has no cross-section; "IC" for single-asset degenerates to time-series correlation, which has different statistical properties and is not what Grinold-Kahn's framework is designed for. The math looks applicable but doesn't transfer.
- **Note:** Becomes applicable in Phase 4 after multi-crypto pivot.
- **Source:** OpenAlphas article (2026-04-19)

### 5.6 Six-dim independent-voting scalping framework (entropy article instantiation)
- **Why rejected as a framework:** Four binding problems. (a) Timeframe mismatch — the framework runs on 1-minute bars with strict no-overnight rules; you trade 1-hour bars on a 24/7 asset where "overnight" doesn't exist. (b) Independence assumption is empirically violated — volume expansion, volatility lift, base strength, and breakout signals all derive from the same price/volume series and are highly correlated; the multiplicative joint-probability math (which is the core mathematical claim) collapses without independence. This is precisely the redundancy problem the OpenAlphas article warned about, which the entropy article walks straight into. (c) "Prior gene layer" (only trade instruments that historically trended in a chosen direction) is selecting on the dependent variable — textbook survivorship bias. (d) Cross-instrument scanning requires a multi-asset basket you don't have until Phase 4.
- **Additional concern — post-hoc parameter discovery:** The article's `0.7 < CDF < 0.9` "sweet spot" claim is a free parameter chosen retrospectively without OOS validation. Any adoption of the CDF idea must avoid this trap (see 2.5.4 pushback section).
- **Note — extracted elements survive elsewhere:** CDF-of-own-history factor → §2.5.4 APPLICABLE. Multi-dim weak-signal composition principle → §3.7 PRINCIPLE-ONLY (with explicit independence-check requirement). Cross-sectional rank-strength → §4.1.8 DEFER to Phase 4. The framework as a packaged system is rejected; the components that make sense in your context are placed individually.
- **Source:** 2026-04-22 minimum information entropy articles (parts 1-3)

---

## 6. OPEN QUESTIONS — unresolved evaluations

Items discussed but not yet placed. These are either waiting for context or genuinely uncertain.

### 6.1 Information-theoretic measures — pending future article(s)
- **Status:** Flagged 2026-04-22. The minimum-entropy articles (parts 1-3) used "information entropy" as rhetoric, not as actual entropy computation. Several legitimate information-theoretic techniques exist for quant — Shannon entropy of return distribution as regime feature, mutual information for non-linear dependence detection, maximum-entropy distributions for tail modeling under constraints, transfer entropy as non-linear Granger-causality alternative.
- **Why open:** Charlie indicated more entropy-related articles are coming. Evaluation deferred until specific concrete techniques surface. If future article presents one of the four directions above with concrete implementation, it will graduate to APPLICABLE / DEFER / PRINCIPLE-ONLY based on phase fit. If future articles continue using "entropy" as loose rhetoric, will be folded into existing rejection (§5.6) without re-litigating.

---

## 7. Foundational reading — before certain phase transitions

- **Before D6 grammar expansion (post-Stage-2d):** Kakushadze, Z. (2015) "101 Formulaic Alphas," arXiv:1601.00991 — operator vocabulary reference + single-asset alpha subset reading exercise (see §2.6.2, §2.6.3, §4.1.9)
- **Before Phase 3 start:** López de Prado, *Advances in Financial Machine Learning*, Chs. 5–7 (purged CV, MDA, PBO)
- **Before Phase 2B late vol modeling:** Corsi (2009), *A Simple Approximate Long-Memory Model of Realized Volatility*
- **Before Phase 4 cross-sectional work:** Fama & MacBeth (1973); Ledoit & Wolf (2003, 2004) shrinkage papers; revisit Kakushadze (2015) for cross-sectional alpha subset (§4.1.9)
- **Before Phase 5 options work:** Hull, *Options, Futures, and Other Derivatives*; Gatheral, *The Volatility Surface*

---

## 8. Update protocol

When a new article / idea / concept is discussed:

1. Advisor evaluates using 5-part format (methodology / context fit / placement / pushback / actionable-now)
2. If it has a concrete phase / deliverable anchor → add as entry to appropriate section (2 / 3 / 4)
3. If it doesn't → either REJECTED (5) with explicit reasoning, or OPEN QUESTIONS (6) if genuinely ambiguous
4. Update `Last updated` date at top
5. Conflicts with existing entries are resolved by amendment, not silent overwrite — keep the old entry's rationale for history

Do NOT add entries that lack phase/deliverable placement. "Interesting, we should think about this" is not a valid entry state. If it can't be placed, it's not ready.
