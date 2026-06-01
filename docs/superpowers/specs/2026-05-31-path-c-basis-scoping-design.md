# Path C — Perp-Spot Basis Axis Mechanism-First Mine (Alpha-Source Rethink, Cycle 3) — Design Spec

**Date:** 2026-05-31 (UTC)
**Version:** v1 (design approved in-chat by Charlie 2026-05-31; pending written-spec review gate + 2-leg B2 before the Step −1 LOCK register).
**Status:** DRAFT — design body approved wholesale in chat. NOT yet authorized for the Step −1 LOCK register, for any ingestion/build/run, or for any commit beyond this spec doc itself.
**Cycle class:** Bounded, pre-committed, **one-cycle** falsification test of the perp-spot **basis** information axis — honestly reframed (§1) as a **higher-frequency robustness/generalization re-test of the funding/basis premium signal** (a near-collinear member of the broader positioning-premium family; NOT the whole family — §1), not a fresh independent axis. The conditional successor to Path A (funding earned-negative, 2026-05-31), opened as a **fresh, separately-registered scoping cycle** (anti-pre-emption).
**Predecessors:**
- Path B mechanism-first OHLCV re-mine — VERDICT `process_refuted_for_this_grid` (earned negative): H1/H2/H3 net Sharpe −8.42 / −2.65 / −2.61 on forward_2026; 0/3 Tier-5; 0 DSR pass. Spec `2026-05-30-pathb-mechanism-first-rethink-design.md`; verdict `data/phase2c_evaluation_gate/pathb_verdict_v1/pathb_verdict_advisory.json`.
- Path A funding-rate axis mine — VERDICT `process_refuted_for_this_grid` (earned negative): H1 `funding_extreme_fade` −1.77 / H2 `funding_sign_regime_switch` −2.98 / H3 `funding_momentum_continuation` −1.62 on forward_2026; 0/3 Tier-5; 0/3 DSR pass_B; H1 mechanism **refuted** in train (extreme funding → *positive* fwd return), H2/H3 strong-sane → process-refuted. Spec [`2026-05-31-path-a-funding-scoping-design.md`](2026-05-31-path-a-funding-scoping-design.md); LOCK [`2026-05-31-patha-step-minus-1-preregistration-lock.md`](2026-05-31-patha-step-minus-1-preregistration-lock.md); verdict `data/phase2c_evaluation_gate/patha_verdict_v1/patha_verdict_advisory.json`.
**Cost anchor:** `spot_realistic_15bps_v1` — 15 bps/side, 30 bps round trip (`config/execution_phaseb_spot_15bps.yaml`). HARD CONSTRAINT; not relaxed anywhere in this cycle.

---

## 0.1 Registered decisions (provenance)

Each was surfaced as plain-text options + intuitive Chinese and explicitly registered by Charlie 2026-05-31 (reviewer/research convergence was advisory only):

| Decision | Registered outcome |
|---|---|
| Q1 — data family | **Perp-spot basis only** (single crypto-native family this cycle; chosen over OI and a funding short-leg extension). |
| Q2 — structural frame | **(b) Strict Path-A parallel + the §37.3 denser-trading delta** — reuse the entire Path A frame, swapping only data family + 3 mechanisms + no-axis baselines, and deliberately design the basis mechanisms to clear the train floors by construction *(as originally registered; later refined to Option A by B2 Finding 1, below — band-widening cannot clear the state-class `zero_fraction` floor)*. |
| Honest-reframe checkpoint | After the grounding passes revealed **basis ≈ funding by construction**, Charlie registered **"先 1 再 2"** — proceed with basis now (option 1, reframed as a funding-family high-frequency robustness/generalization re-test), then **OI** as the successor cycle (option 2). Charlie's stated rationale: *"1 如果是 correlated 或者 confounded,统计上来说确实就是会再测一遍多半还是负面"* — the redundancy is understood and accepted; a confirming negative that generalizes the funding negative is the expected and valuable outcome. |
| OI successor | **Direction-noted only.** OI is recorded as the next conditional register; it is NOT scoped, pre-named in build terms, or authorized by this cycle (anti-pre-emption, §10). |
| N\* | **N\* = 3** (three basis mechanisms, one pre-registered variant each, no parameter sweep). |
| Tier-5 gate window | **forward_2026** — the same OOS slice the dead-18 scored 0/18 and Path B/Path A H1/H2/H3 were gated on (apples-to-apples across all three cycles). |
| Sizing / shorts | **All three long/flat** (no shorts); single-factor vol-CDF ternary sizing. |
| Mechanical defaults | Accepted as proposed (basis factors / percentile threshold / 24h+72h sanity horizon / reuse Path B price-confirm factor / single-factor vol-CDF sizing / inherit §9 escalation + reuse harness / the dual-orthogonalization diagnostic, §9 Finding D). |
| B2 Finding 1 resolution (denser-trading-delta feasibility) | **Option A — honest down-scope** (registered by Charlie 2026-05-31, post-advisor-B2). Verified: band-widening does NOT clear the state-class `zero_fraction` floor — the inherited price-trend AND-confirm is the binding constraint (Path A H2/H3 were 0.62/0.67 at a wide-open 0.80 band). So **H2/H3 are pre-registered as expected-INDETERMINATE on `zero_fraction`**; the (b) delta's real benefit is the no-carry simplification + an H1 flat-exit-episode boost (verified-not-assumed) + a deterministic `θ_basis_hi` fallback. Verdict robustness rests on mechanism-sanity + §9 Finding D + the §37.3 "negative holds independent of floor" logic. |

---

## 1. Motivation & frame

**Binding constraint = the alpha source / hypothesis-space** (reviewer-convergent, Charlie-registered; memory `alpha-source-is-the-binding-constraint-not-data-methodology`). Path B held the **data** fixed (OHLCV) and varied **only the process** → earned negative. Path A then held the **process** fixed and varied **only the data axis** (OHLCV → OHLCV + funding) → earned negative. Both negatives localize failure away from their respective grids without exonerating the information set in general. Path C continues the falsification series on the next-cheapest, cleanest crypto-native axis.

**Why basis is the right Cycle-3 axis — AND its honest reframe.** Perp-spot basis (the perpetual-futures premium over spot) is the cheapest, cleanest 1h-native signal still untested: free Binance-Vision bulk history from **2020-01** (matching the OHLCV/funding start exactly), UTC-native, and — critically — **the same 1h cadence as OHLCV, so no cross-cadence carry is needed** (the §37.2 funding 8h→1h warmup-conversion complexity disappears). It was registered over OI (which starts 2020-09, an 8-month gap worsening the §37.3 under-power problem) and over a funding short-leg extension (whose Path A pre-registration trigger was not met — H1's train mechanism was refuted, not "passed-sanity-but-merely-defensive").

**The load-bearing honesty correction (grounding pass, §13).** Funding is **literally computed from a time-average of the premium index**, and perp-spot basis *is* that premium index (or its less-clamped mark-minus-spot equivalent). So **basis is near-redundant with funding by construction** — the continuous, higher-frequency version of the signal Path A just earned a clean negative on. Path C is therefore **not** a fresh, independent axis; it is a **higher-frequency robustness re-test of the funding/basis premium signal** (a near-collinear member of the broader positioning-premium family — see the calibration bullet below). This reframe is registered (Charlie 2026-05-31) and is the calibrated prior for the cycle:
- **C-negative (most likely)** → the funding/basis *premium* signal adds no directional rescue at *either* its 8h (funding) or 1h (basis) sampling frequency under this process/grid → tightens the Path A localization from *"funding adds no rescue"* to *"the funding/basis premium signal adds no rescue at either sampling frequency"* — a tighter, robustness-confirming statement, at the cheapest available data cost. **(Calibration, B2 Finding 5):** this is NOT yet "the whole positioning-premium family fails" — funding and basis are two *near-collinear* members (basis ≈ funding by construction), not the family; the genuinely-independent member (open interest, the noted successor) must also be tested before any family-level claim. The §9 Finding D D2 leg is what licenses even the cross-frequency claim (and only jointly with a non-inert D1).
- **C-positive (low prior)** → higher-frequency basis carries directional edge the 8h funding could not → a genuine, small-N\* finding requiring 2025 OOS confirmation AND surviving the dual-orthogonalization diagnostic (§9 Finding D) before any promotion.

**Honest prior (do not oversell — §12).** The literature is clear that the *strong* basis edge is **cross-sectional/carry** (Chi et al. JFM 2023: basis is the strongest *cross-sectional* predictor), which a single-asset directional long/flat engine **cannot express** — exactly the gap that capped funding. The single-asset *time-series* basis→price signal is weak, short-horizon (8–72h), endogenous to momentum, and post-ETF-compressed. A clean earned-negative is the **most likely and most informative** outcome (failing an *easier* small-N\*=3 bar is *more* conclusive — the §8 small-N\* asymmetry, inherited). There is no Path-C outcome we regret running.

---

## 2. Scope

**In scope (this cycle = scoping artifacts ONLY):** (1) this design spec; (2) the Step −1 pre-registration LOCK (§7); (3) the implementation plan (`superpowers:writing-plans`). **This cycle touches no basis data and writes no harness code.**

**In scope of the design pinned here (executed at downstream registers):** (a) a basis ingestion pipeline (Binance Vision bulk `markPriceKlines` + `indexPriceKlines`, CCXT incremental) producing a new raw parquet + schema; (b) a basis-feature pipeline (3 basis factors on the 1h series — no cross-cadence carry); (c) three pre-registered basis mechanism-first hypotheses (H1/H2/H3, §3); (d) cost-aware evaluation + hypothesis-class floors + DSR-FWER at N\*=3; (e) the **dual-orthogonalization** marginal diagnostic (§9 Finding D); (f) reuse of the Path A verdict harness (`patha_* → pathc_*`).

**Out of scope (non-goals):**
- ❌ Open interest (the registered direction-noted *successor* cycle — separate future register), liquidations, cross-sectional/multi-asset structure.
- ❌ Short legs (long/flat only; deferred to a separate register).
- ❌ Basis-scaled / 2-factor position sizing (single-factor vol-CDF sizing only; deferred).
- ❌ Delta-neutral basis-carry harvest (long-spot/short-perp) — not expressible in the single-asset directional engine and explicitly **not** a Path C mechanism (§12 guard).
- ❌ Any change to the promotion-gate math or the 15 bps anchor; the only sanctioned gate action is reusing the Path A/B N\*=3 DSR-FWER plumbing for Path C's own new cohort. Sealed `tier6_dsr_v1` artifacts stay byte-identical.
- ❌ Any ingestion/build/run execution this cycle.

---

## 3. The three pre-registered hypotheses

All **long/flat**, ternary `{0, 0.5, 1.0}` sizing on `cdf_realized_vol_720` (the Path-B single-factor vol-CDF sizing, reused). Basis factors are evaluated on the **1h series directly** (no carry — basis is native-1h). Basis never sets position *size*; it sets the long ON/OFF *gate* or the entry trigger. Parameters are fixed a priori from the mechanism and the basis/funding literature, locked at Step −1, with **no train tuning and no post-hoc sweep**.

Diversity mirrors Path A's triad on identical archetypes (extremity-reversal / regime-gate / moderate-persistence-continuation) so the basis-axis result is directly comparable to the funding-axis result. Each hypothesis names its **funding twin** (the Path A leg it re-tests at higher frequency) to keep the redundancy explicit (§1).

### H1 — `basis_extreme_fade` (crowded-premium reversal; long-biased de-risk overlay)
- **Mechanism:** an extreme-high (rich) basis proxies crowded, over-leveraged long positioning whose forced-liquidation fragility skews forward returns negative (long-squeeze / de-lever). We fade the crowded long *defensively* (long/flat: go flat, do not short).
- **STRUCTURE NOTE (inherited from Path A H1):** H1 is a long-biased de-risk OVERLAY, not a sparse event strategy. Under long/flat, H1 is **long on the complement** of the rare extreme-basis tail and goes **flat** only during rare positive-premium extremity. Its forward Sharpe is **partly buy-and-hold-dominated**; its edge claim is precisely "do the basis-driven defensive flat-exits add Sharpe over an always-long baseline?" — read via the §9 dual-orthogonalization diagnostic, NOT raw Sharpe. The eligibility floor keys on the **count of defensive flat-exit episodes** on train (§9), not long-bar occupancy.
- **Basis factor(s):** `basis_pct_rank` (causal rolling percentile of `basis_rel` over a pre-registered window) + `basis_sign`.
- **Signal:** **flat** when `basis_pct_rank ≥ θ_basis_hi` (pre-registered ~0.90) AND `basis_sign > 0` (positive-premium crowded-long side only); **long** otherwise (the complement). Time exit `max_hold_bars = H1_hold` (pre-registered).
- **Sizing:** vol-regime ternary on `cdf_realized_vol_720`.
- **Directional hypothesis (pre-registered sign):** extreme-high-basis bars have conditional forward return **< 0**.
- **Kill (pre-registered):** train-only — partition bars by `basis_pct_rank ≥ θ_basis_hi AND basis_sign > 0`; if the conditional mean forward return over the sanity horizon (§9) is **not negative**, the reversal mechanism is refuted (we do NOT flip to "buy high basis").
- **Denser-trading design (§37.3 delta b; B2 Finding 3 — verified-not-assumed):** basis is **1h-continuous** (vs funding's 8h-settled carry), so the top-(1−θ) tail is sampled every bar — this is *expected* to raise the count of distinct defensive-flat-exit *episodes* above Path A's 150/200, but episode count is bounded by signal *transitions* into the tail (not tail-bar occupancy), so it is **verified at train, not assumed**; an **H1-INDETERMINATE-on-floor contingency is pre-registered** (mirroring Path A's honest H1 pre-disclosure). `θ_basis_hi` is locked at Step −1 as a **deterministic a-priori rule** — `θ_basis_hi := 0.90; if train flat-exit episodes < 200, θ_basis_hi := 0.85` (a fixed fallback, NOT a judgment call) — targeting eligibility/power only, orthogonal to forward Sharpe, **never tuned toward Sharpe**.
- **Funding twin (honest prior):** Path A H1 `funding_extreme_fade` was **REFUTED in train** (extreme funding → *positive* fwd return, opposite the reversal sign). Because basis ≈ funding, **H1 basis most likely refutes the same way.** Pre-registered sign remains the reversal hypothesis (negative); refutation is the expected, informative result.

### H2 — `basis_regime_gate` (regime-gate on a price-trend book; state-class)
- **Mechanism:** the carried basis level is a *positioning* state variable summarizing which side is crowded; it GATES a directional price-trend book — permit price-trend longs in the non-crowded/favorable basis regime, de-risk to flat in the crowded/stressed regime. Basis is the gate; the price-trend confirm is the directional leg. Tested purely as **conditional separation of forward returns by basis regime** (§3 kill); makes NO basis-accrual/carry claim.
- **Basis factor(s):** `basis_sign` + `basis_ewm` (causal EWM of `basis_rel`, pre-registered span; regime band defined via its own causal percentile to be robust to post-ETF level drift).
- **Signal (two OR-connected regime groups):** PERMISSIVE (long-enabled) — `basis_ewm` in the favorable band AND price-trend confirm (`decay_linear_close_48 > decay_linear_close_168`, reused from Path B) → long. DE-RISK — `basis_ewm` in the crowded/stressed band → **flat**, regardless of price trend.
- **Exit:** switch to flat on entering the de-risk regime, OR price-trend roll-over (`48 < 168`), OR `max_hold_bars = H2_hold`.
- **Sizing:** long/flat ternary on `cdf_realized_vol_720`.
- **Directional hypothesis (pre-registered sign):** conditional mean forward return of price-trend-longs is **higher** in the permissive regime than the de-risk regime, AND positive in the permissive regime.
- **Kill (pre-registered):** train-only — conditional mean forward return for price-trend-long bars **split by basis regime**; SANE iff `(permissive mean) > (de-risk mean)` AND `permissive mean > 0`. REFUTED if the basis split adds no separation (gate inert → basis contributes nothing beyond OHLCV).
- **Denser-trading design (§37.3 delta b) — HONEST LIMIT (B2 Finding 1, verified):** widening the basis regime band does **NOT** clear the `zero_fraction < 0.50` floor. Path A H2's permissive band was already wide (bottom 80% → ~0.20 zero_fraction from the band alone), yet its actual train `zero_fraction` was **0.62** — because the binding constraint is the **price-trend AND-confirm** (`decay_48 > decay_168` fires <50% of bars), which Path C H2 inherits verbatim. The basis band is therefore kept at the **Path-A-analog (~0.80 de-risk percentile)** — NOT widened to chase the floor — and a **minimum de-risk-cell occupancy is pre-registered** (B2 Finding 6) so the conditional-separation kill stays powered (a near-empty de-risk cell would make the kill noise-dominated). **H2 is pre-registered as expected-INDETERMINATE on the `zero_fraction` floor**; its verdict rests on mechanism-sanity + §9 Finding D + the §37.3 "negative holds independent of floor" logic. Band edges locked a priori as causal percentiles, never tuned to Sharpe.
- **Funding twin:** Path A H2 `funding_sign_regime_switch` (strong-sane in train). Highest momentum-contamination risk after H3.

### H3 — `basis_momentum_continuation` (moderate-persistence trend confirm; state-class)
- **Mechanism:** persistent *moderate* positive basis reflects ongoing capital-efficient leveraged-long demand that can sustain an established uptrend, so rising/steady basis short of the reversal extreme confirms trend continuation.
- **Basis factor(s):** `basis_ewm` (causal EWM, pre-registered span — persistence proxy) + `basis_pct_rank` (the UPPER guard excluding the reversal-extreme tail).
- **Signal:** **long** when `basis_ewm > 0` (persistent positive premium) AND `basis_pct_rank ≤ θ_basis_hi` (NOT in H1's reversal tail — the explicit exclusion preventing H1/H3 collision) AND price-trend confirm (`decay_linear_close_48 > decay_linear_close_168`); flat otherwise.
- **Exit:** `basis_ewm ≤ 0` (demand fades) OR price-trend roll-over OR `basis_pct_rank` crossing into the reversal tail (`> θ_basis_hi`) OR `max_hold_bars = H3_hold`.
- **Sizing:** long/flat ternary on `cdf_realized_vol_720`.
- **Directional hypothesis (pre-registered sign):** moderate-persistent-positive-basis + uptrend bars have conditional forward return **> 0** (continuation).
- **Kill (pre-registered):** train-only — partition bars by `basis_ewm > 0 AND basis_pct_rank ≤ θ_basis_hi AND price-trend-up`; SANE iff conditional mean forward return over the sanity horizon is **positive**; REFUTED if non-positive.
- **Denser-trading design (§37.3 delta b) — HONEST LIMIT (B2 Finding 1):** like H2, H3 inherits the price-trend AND-confirm, so the `zero_fraction < 0.50` floor is **NOT** clearable by basis-band design (Path A H3 was 0.67). `basis_ewm > 0` being common only widens the eligible set; the price-trend AND-confirm still binds long-bar occupancy. **H3 is pre-registered as expected-INDETERMINATE on the `zero_fraction` floor**; verdict rests on mechanism-sanity + §9 Finding D + the §37.3 independent-of-floor logic.
- **Funding twin:** Path A H3 `funding_momentum_continuation` (strong-sane but +0.38 funding-marginal on a still-losing book → "price-trend wearing a funding mask"). **Weakest leg; highest momentum-contamination risk** (literature Q6) — its conditional-separation kill + the §9 Finding D orthogonalization are the critical discriminators.

---

## 4. Build surface

- **New ingestion (1):** a basis ingestion pipeline (§5) — Binance Vision bulk `markPriceKlines` (1h) + `indexPriceKlines` (1h, for the consistency cross-check) + CCXT incremental → new raw parquet `data/raw/btcusdt_markprice_1h.parquet` + new `config/schemas.yaml` `markprice`/`basis` block + validators. Reuses the funding-ingestion code pattern (`ingestion/funding_bulk_download.py` / `funding_incremental_update.py` / `funding_reconcile.py`).
- **New basis-feature pipeline (1):** basis factors computed on the **1h `basis_rel` series directly** (causal rolling) — **no cross-cadence carry** (basis is native-1h; this is the §37.2 simplification). Whether this extends `factors/build_features.py` or a parallel builder is a plan-stage decision; the design intent (compute-on-1h-basis-series, no carry) is fixed here.
- **New registered basis factors (3):** `basis_pct_rank` (causal rolling percentile), `basis_ewm` (causal EWM, `adjust=False`), `basis_sign`. Top-level named functions; rolling/causal only; must pass the inherited G1–G4 leakage guards. Reuses Path B's `decay_linear_close_48/168` (price-trend confirm) and `cdf_realized_vol_720` (sizing) — both already registered.
- **Hypotheses (3):** H1/H2/H3 in the DSL (factor-vs-scalar + factor-vs-factor + OR-groups + ternary sizing node — all already in the DSL from Path A/B; **no new DSL schema** expected; confirm at plan stage).
- **Harness reuse (1):** `patha_* → pathc_*` verdict harness (holdout producer, moments, DSR-FWER N\*=3, earned-negative taxonomy, marginal diagnostic, orchestrator). Reuse, do not rebuild.
- **Dual-orthogonalization diagnostic (extend `patha_marginal_diagnostic.py`):** add the **vs-funding** leg (§9 Finding D) alongside the inherited vs-momentum leg. The funding-gated H1/H2/H3 strategies + funding factors + funding data are already on `main` (Path A) and are reused as the comparison baseline.
- **Process (0 new):** the cost-aware objective + hypothesis-class floors are inherited unchanged from Path A/B.

---

## 5. Basis-data ingestion design + leakage/alignment guards (pinned; executed at a downstream register)

**Source (verified by direct Binance Vision S3 probe, 2026-05-31, §13).**
- History: Binance Vision bulk `futures/um/monthly/markPriceKlines/BTCUSDT/1h/` and `.../indexPriceKlines/BTCUSDT/1h/` — both confirmed start **2020-01** (first `open_time = 1577836800000` = 2020-01-01T00:00:00Z), 1h cadence (Δ = 3,600,000 ms), standard 12-col headerless kline CSV. `premiumIndexKlines/BTCUSDT/1h/` likewise from 2020-01 (used only as a consistency cross-check, §B). Same download→checksum→parse pattern as the OHLCV bulk ingest.
- Incremental / forward (incl. 2026): CCXT mark-price / index-price endpoints or raw Binance futures kline endpoints. Daily Vision partitions are the gap-filler for the current partial month.

**Basis derivation (pre-registered).** Primary signal series:
- `basis_rel[t] = (markPrice_close[t] − spot_close[t]) / spot_close[t]`, where `spot_close` = the existing canonical Binance **spot** BTCUSDT 1h close (`data/raw/btcusdt_1h.parquet`, verified 2020-01-01 → 2026-04-16, aligned). This is the perp fair-value premium over the spot we actually trade at 15 bps — continuous and **less-clamped than `premiumIndex`** (B2 Finding 8: markPrice is itself a smoothed Binance construct, so this is "less Binance dampening," **not strictly un-clamped** — characterized at the ingestion register against the cross-check). It avoids `premiumIndex`'s explicit clamping/dampening, which would reintroduce a `zero_fraction` sparsity analogous to Path A funding.
- Cross-check (NOT a signal, not a DoF): Binance `premiumIndex_close` and `(markPrice_close − indexPrice_close)/indexPrice_close` should track `basis_rel` *approximately* (B2 Finding 8 — note the anchor wedge: `basis_rel` uses single-venue Binance spot in the denominator, the cross-check uses the multi-venue `indexPrice`). A **numeric tolerance** (pinned at the ingestion register, §11) bounds the acceptable wedge so a real ingestion bug is not masked, nor a benign index-vs-spot wedge mistaken for a failure; used to validate ingestion only.
- `markPrice` is a smoothed fair value (not last-trade) — appropriate for a basis/premium signal; documented as such.

**New raw parquet + schema.** `data/raw/btcusdt_markprice_1h.parquet`; new `config/schemas.yaml` `markprice` block. Columns: `open_time_utc` (UTC tz-aware `datetime64[ms, UTC]`, **unique sorted PK**), `mark_open/high/low/close`, `index_close` (for cross-check), `source` (`binance_vision` / `ccxt_binance`), `ingested_at_utc`. Reconcile archives-before-overwrite into `data/raw/archive/` (mirrors the OHLCV rule). No forward-fill of missing bars; gaps flagged not interpolated.

**Causal alignment (basis-specific leakage surface — DESIGN INVARIANT).**
- Basis is **native 1h** — `basis_rel[t]` joins `markPrice@t` to `spot_close@t` on `open_time_utc` (same grid, **no carry**). Each 1h bar at close-time uses only data available at that close; orders fill at N+1 open (project execution convention).
- Basis factors (`basis_pct_rank`, `basis_ewm`, `basis_sign`) are computed on the 1h `basis_rel` series with rolling windows in **1h bar units** (causal: bar T uses only `basis_rel` at bars ≤ T).
- A dedicated causality guard (mirroring Path A's G2 sentinel) asserts the basis factor at bar N is bit-identical when bars after N are deleted/reversed/shuffled.
- The inherited Path B leakage guards (G1 AST-scanner, G2 future-bar-invariance sentinel, G3 per-operator known-value + ternary causality, G4 registry-sync) are on `main` and apply unchanged to the new basis factors.

**Known data characteristics to document before train (not auto-cleaned).** The FTX-era break (Nov 2022); the post-spot-ETF basis compression (Jan 2024, the §12 decay temper); any kline gaps. The funding ingest found Binance `calc_time` ±ms jitter producing false gaps — the same `open_time` validator tolerance (on exact 3,600,000 ms spacing) is reused. Flagged in the validation report, never interpolated.

---

## 6. Cycle sequence (this cycle = Step −1 design artifacts; Steps 0+ are downstream registers)

- **THIS CYCLE (scoping):** this design spec → **Step −1 pre-registration LOCK** (§7; a Charlie register-event, committed BEFORE any basis data is ingested or peeked — the anti-hindsight commit-order) → implementation plan (`superpowers:writing-plans`).
- **Downstream register A — ingestion.** Build the basis ingestion + basis-feature pipeline (§5); ingest + validate the basis parquet. **First data touch — only after the Step −1 LOCK freezes the hypotheses.**
- **Downstream register B — build.** `pathc_*` factors + DSL hypotheses + harness reuse + dual-orthogonalization extension, TDD + B2 (Codex on the grounded implementation + code-reviewer/advisor on LOCK/spec conformance).
- **Downstream register C — run.** Train-only mechanism-sanity table → walk-forward train (2020-21+2023, `check_wf_semantics_or_raise`) → forward_2026 Tier-5 single-run holdout (`check_evaluation_semantics_or_raise`, `holdout_sharpe > 0` at 15 bps) → DSR-FWER N\*=3 → dual-orthogonalization diagnostic → earned-negative taxonomy → C-result advisory → Charlie's binding read. 2025 touched once only for a `c_positive` confirmation.

Each downstream register is a **separate Charlie register-event**; this cycle authorizes none of them.

---

## 7. The pre-registrations (to be LOCKED at Step −1, before any basis peek)

The Step −1 LOCK doc (`2026-05-31-pathc-step-minus-1-preregistration-lock.md`, written + committed as its own register-event) will freeze:

1. **Hypotheses + variant grid → N\*.** The exact 3 basis hypotheses (§3) and their single pre-registered variants. **N\* = 3** = the full considered inferential family. Adding any variant after a Step-0/run peek **voids N\***. Includes the exact a-priori values: `θ_basis_hi` as a **deterministic rule** (`:= 0.90; → 0.85 if train H1 flat-exit episodes < 200`, §3 H1; not a judgment call), the `basis_pct_rank` window, the `basis_ewm` spans (H2/H3), the H2 regime-band edges (Path-A-analog ~0.80 de-risk percentile + a pinned **minimum de-risk-cell occupancy**, B2 Findings 1/6), `H1_hold`/`H2_hold`/`H3_hold`, and the `basis_rel` derivation (mark−spot, less-clamped-than-premiumIndex).
2. **Gate pre-commit.** 15 bps anchor + DSR-FWER (Form B authoritative) at N\*=3 + Tier-5 `holdout_sharpe > 0` (strict) on **forward_2026**. Locked, never revisited post-result.
3. **Process-delta pre-spec.** Cost-aware (net-of-15bps) objective; hypothesis-class floors (**H1 event-class ≥200 defensive-flat-exit episodes on train** — verified-not-assumed, H1-INDETERMINATE-on-floor contingency pre-registered; **H2/H3 state-class `zero_fraction < 0.50` AND ≥200 trades on train** — `zero_fraction` floor **NOT clearable by basis-band design** per B2 Finding 1, so H2/H3 **pre-registered as expected-INDETERMINATE on `zero_fraction`**, verdict robust via §9 + §37.3; deployment-readiness target ≥1000 trades); single-factor vol-CDF ternary sizing; the native-1h causal basis derivation (§5); the §37.3 denser-trading design intent (as feasibly applied — Option A).
4. **Dual-orthogonalization diagnostic pre-spec** (§9 Finding D) — fenced, diagnostic-only, not in N\*.
5. **Kill-criterion taxonomy + escalation** (§9), inheriting the §9-amended significance prong.

---

## 8. Multiplicity, the gate, and the small-N\* asymmetry (inherited)

The Path A/B N\*=3 DSR-FWER plumbing (`backtest/tier6_dsr.py` + `backtest/patha_dsr_fwer.py`, Form B authoritative, `Z_PASS = 1.644853626951472` frozen) is **reused** for Path C's own new cohort; the sealed `tier6_dsr_v1` artifacts stay **byte-untouched** (re-verify sha256 before AND after, per the sealed-artifact invariant).

**Small-N\* asymmetry (inherited).** N\*=3 is much smaller than the sealed 18, so the bar (`sr_star`) is *lower*. A **C-negative is MORE conclusive** (a variant failed even an *easier* bar); a **C-positive is LESS conclusive** (cleared an easier bar) → a C-positive requires **2025 OOS confirmation** AND must survive the §9 Finding D dual-orthogonalization before any promotion. N\* prices only the post-hoc family of the 3 pre-registered variants.

---

## 9. Pre-registration values + earned-negative taxonomy (drafted; confirmed at Step −1)

- **Hypothesis-class floors (B2 Finding 1 — honest power disclosure).** *H1 (long-biased overlay):* floor keys on the **count of defensive flat-exit episodes** on train (NOT long-bar occupancy); ≥200 episodes — basis's 1h cadence is *expected* to raise the episode count above Path A's 150, but episodes are **transition-bound, not tail-bar-bound**, so this is **verified at train, not assumed**; an H1-INDETERMINATE-on-floor contingency is pre-registered. *State-class (H2/H3):* `zero_fraction < 0.50` AND ≥200 trades on train — the `zero_fraction` floor is **NOT clearable by basis-band design** (the inherited price-trend AND-confirm binds long-bar occupancy; Path A H2/H3 were 0.62/0.67 at a wide-open band), so **H2/H3 are pre-registered as expected-INDETERMINATE on `zero_fraction`**. Deployment-readiness target ≥1000 trades. **Floors checked on the TRAIN window**; the taxonomy keys on mechanism-sanity + Tier-5 `holdout_sharpe > 0` + §9 Finding D — and **the earned-negative holds independent of floor eligibility (§37.3):** an under-floor leg with measured forward loss is a *substantive* negative (measured loss), not a *vacuous* eligibility exclusion — the verdict is named to disclose which.
- **Cost-aware objective.** Ranking among pre-registered variants by Sharpe net of 15 bps/side; floors applied before ranking. N\* = full grid → no post-hoc cherry-picking.
- **Mechanism-sanity horizon (inherited from Path A, Charlie-kept).** The train-only conditional-return sign tests (§3) are evaluated at **24h AND 72h** horizons, **sane iff EITHER**. Both horizon signs are **pre-registered and reported separately**; a leg with the hypothesized sign at **both** horizons is **strong-sane**, at **only one** is **weak-sane (floor)**. A verdict resting on weak-sane-only legs is flagged in the advisory bundle.
- **Earned-negative taxonomy (inherited).**
  1. **mechanism-refuted** — no leg's conditional forward-return sign matches its hypothesized direction (H1 reversal-DOWN; H2 permissive>de-risk & permissive>0; H3 continuation-UP).
  2. **process-refuted-for-this-grid** — ≥1 leg mechanism-sane, but no variant clears Tier-5 `holdout_sharpe > 0` at 15 bps on forward_2026.
  3. **NOT "basis exhausted."** A C-negative localizes failure away from *{basis + cost-aware + trade-frequency + ternary long/flat sizing + these 3 mechanisms}* — it does **not** exonerate the basis information set (short legs, basis-scaled sizing, cross-structure remain *untried, not falsified*). Symmetric to the OHLCV/funding-not-exonerated caveats. **AND it generalizes the Path A funding negative** (§1): a C-negative + the §9-Finding-D redundancy confirmation tightens the **cross-frequency** localization (the funding/basis premium fails at both its 8h and 1h frequencies) — **NOT yet family-level** (OI, the genuinely-independent member, is required first; §1 calibration, B2 Finding 5).
- **c-positive** — ≥1 variant clears Tier-5 `holdout_sharpe > 0` (even if it fails DSR-FWER at N\*) → weak (small-N\*, §8) requiring 2025 OOS confirmation AND surviving Finding D; Charlie re-evaluates (no auto-trigger, no auto-demote).
- **Finding D — dual-orthogonalization marginal diagnostic (fenced, diagnostic-only; the key new element).** Because basis ≈ funding ≈ momentum, a raw negative/positive Sharpe cannot be attributed to *basis*. A pre-registered comparison computes, on the same bars:
  - **(D1) vs momentum** — the basis-gated strategy vs the identical price-trend / always-long baseline WITHOUT the basis gate (does basis add over pure momentum?). [Path A's funding-marginal, inherited.]
  - **(D2) vs funding (NEW)** — the basis-gated strategy vs the *funding-gated* Path A strategy on the same bars (does higher-frequency basis add anything over the 8h funding it is derived from?). **Inference rule (B2 Finding 2 — pinned to avoid a vacuous-agreement trap):** redundancy is confirmed ONLY by the **conjunction** `basis-gated ≈ funding-gated` (D2) **AND** each gate **non-inert** (its D1 marginal materially ≠ 0). Mutual agreement under *jointly-inert* D1 — both gates contribute nothing, both books merely track the dead price leg / buy-and-hold — is **vacuous** and does NOT license the redundancy/generalization read. When confirmed, this tightens the §1 cross-frequency localization rigorously rather than rhetorically — operationalizing the registered "correlated/confounded → re-test" rationale.
  - **Diagnostic-only, NOT promotion-affecting, NOT counted in N\*** (mirrors the Path A/B fenced-diagnostic discipline — e.g. Path A's funding-marginal). **D1 and D2 each emit a separate fenced record per hypothesis** (`promotion_affecting=False, in_n_star=False`). Without D, taxonomy point (3)'s localization does **not** hold for the basis legs, whose failure would otherwise be confounded with the dead price leg / buy-and-hold / the funding twin.
- **Escalation prong (inherited §9 amendment).** Any "a real edge exists" determination is gated by DSR-**significance** (`pass_B` / PSR ≥ 0.95), **not** a point-estimate. The binding taxonomy verdict and any next-axis escalation are a **Charlie register-event** — never an automated fire.

---

## 10. Anti-pre-emption

- This cycle scopes **basis only** (Q1). **Open interest is the registered direction-noted *successor*** ("先 1 再 2") — recorded as the next conditional register, **not scoped, not pre-named in build terms, not authorized here.** Liquidations, short legs, and basis-scaled sizing are each a separate, future, conditional register — direction noted, none scoped here.
- A short-leg variant is **not** registered (Path A's short-leg trigger was not met; not carried forward as pre-authorized).
- No methodology successor (Romano-Wolf / Westfall-Young / SD-E-γ) is pre-named; all remain deferred per the binding-constraint thesis.
- Reviewer / research convergence is advisory; only Charlie-register authorizes fires (ingestion, build, run, commits beyond this spec).

---

## 11. Test plan (executed at the downstream build register; pinned here)

- **Ingestion:** mark/index kline bulk parse (Binance Vision CSV schema, headerless 12-col, ms epoch → UTC); UTC PK uniqueness + sort; archive-before-overwrite; validator extension for the `markprice` schema; the `basis_rel` derivation correctness + the `premiumIndex`/`(mark−index)` consistency cross-check **within a pinned numeric tolerance** (§5, B2 Finding 8); gap/break flagging (FTX Nov-2022, post-ETF Jan-2024); ±ms-jitter false-gap tolerance reused from funding.
- **Basis factors:** each new factor — null policy, declared warmup, causality, known-value; rolling/causal AST scan (G1); future-bar-invariance sentinel (G2).
- **Native-1h alignment:** `basis_rel` join (markPrice@t to spot_close@t on `open_time_utc`, no carry); dedicated causality guard (delete/reverse/shuffle future bars → bit-identical); no-future-bar-read assertion.
- **Hypotheses:** each compiled-through-engine; `set_coc/coo(False)`; signal at N close fills at N+1 open; long/flat ternary sizing emits the `{0,0.5,1.0}` ladder; H1/H3 non-overlapping-population assertion (`pct_rank` tail exclusivity).
- **Verdict harness (`pathc_*`):** forward_2026 single-run holdout producer; CandidateMoments constructor + integrity gate; DSR-FWER N\*=3 (reuse, `pass_B` keyed on `holdout_sharpe`); earned-negative taxonomy with the tiered 24h+72h sanity horizon; orchestrator end-to-end; the **§37.1 function-boundary authorization gate** (real engine reachable only via gated `main()` + injected `_run_backtest` dependency; `run_verdict(_run_backtest=None)` raises while unauthorized) **re-verified to survive the `patha_*→pathc_*` rename**; **sealed `tier6_dsr_v1` sha256 4/4 unchanged before AND after.**
- **Dual-orthogonalization diagnostic (fenced, §9 Finding D):** D1 (vs momentum) + D2 (vs funding) computed + reported on identical bars; asserted **diagnostic-only** (not promotion-affecting, not in N\*); D2 reuses the Path A funding-gated strategies on `main`.
- Full suite green before each register/seal boundary (current baseline **2895 passed / 9 skipped / 2 xfailed; pc9 2780**).

---

## 12. Risks & open questions

- **The directional basis edge is weakly evidenced AND near-redundant with funding (headline risk).** The *strong* basis edge is cross-sectional/carry (Chi et al. JFM 2023), not single-asset directional; and basis is the higher-frequency twin of the funding signal Path A already falsified. A clean earned-negative is the most likely outcome (§1). Do not oversell.
- **Delta-neutral-carry framing trap (DESIGN GUARD).** No mechanism may be justified by basis-carry economics. H1/H2/H3 are directional spot-price bets that *use* basis as a state variable; none collects the spread.
- **Basis-axis-specific compression temper (carried from Path A's post-ETF temper, sharpened).** The spot-ETF launch (Jan 2024) brought arbitrage capital that compresses and stabilizes the basis — train-window (2020-21+2023) basis effects likely **overstate** forward_2026 magnitudes more than for funding. Percentile/EWM-normalized inputs (`basis_pct_rank`, causal-percentile regime band) partially immunize; pre-registered as an expected headwind.
- **Momentum endogeneity (the most dangerous failure mode).** Basis is *caused by* recent price moves (longs pile in → premium rises), so a naive basis-long risks being a lagged-momentum strategy wearing a basis mask. §9 Finding D's vs-momentum leg (D1) is the guard; H3 is most at risk.
- **Funding redundancy (the reframe's core).** Basis is not independent evidence; §9 Finding D's vs-funding leg (D2) measures the marginal information of higher frequency over the 8h funding. A near-zero D2 is the *expected, confirming* result, not a failure of the cycle.
- **No-peek discipline.** The pre-registration is theory-driven only. No 2026 basis observation may touch the design — that would be a forward_2026 peek voiding the cycle.
- **Citation verification (open; §1 discipline).** Chi et al. JFM 2023 and He et al. metadata are moderate-confidence (flagged by the grounding pass); empirically re-verified at the B2 before the LOCK, as Path A re-verified its funding citations.
- **Open (review-gate / Step −1 lock):** the exact `basis_pct_rank` window + `basis_ewm` spans + `θ_basis_hi` percentile + H2 regime-band percentile edges + `H_hold` values + the final `basis_rel` derivation — all locked a priori at Step −1, no train tuning. The price-confirm factor is **committed** to Path B's reused decay-MA cross to minimize DoF.

---

## 13. Verified anchors (this cycle)

- **Binance Vision S3 probe (2026-05-31, metadata-only, no forward_2026 value peek):** `futures/um/monthly/{markPriceKlines,premiumIndexKlines,indexPriceKlines}/BTCUSDT/1h/` all start **2020-01** (first `open_time = 1577836800000` = 2020-01-01T00:00:00Z), 1h cadence (Δ=3,600,000 ms), 76 monthly partitions through ~2026-04, standard 12-col headerless kline CSV. Daily partitions exist (earliest ~2019-12-23) as the partial-current-month gap-filler. Local spot `data/raw/btcusdt_1h.parquet` verified 55,105 rows, 2020-01-01 → 2026-04-16, `datetime64[ms, UTC]` — aligned start for the mark−spot derivation.
- **Basis derivation recommendation (grounding pass):** `basis_rel = (markPrice_close − spot_close)/spot_close` (less-clamped than `premiumIndex`, denser) primary; `premiumIndex` + `(mark−index)` consistency cross-checks; ms-epoch → UTC; headerless 12-col positional schema; reuse funding ingest pattern + ±ms-jitter validator.
- **Literature (grounding pass; signs LOW-confidence, caveats load-bearing):** strong basis edge is cross-sectional/carry (Chi et al. JFM 2023), not single-asset directional; basis near-redundant with funding by construction; momentum-endogenous; short horizon (8–72h); post-ETF compressed. Suggested signs: H1 fade-extreme (LOW-MOD), H2 regime-gate (LOW), H3 continuation (LOW/SPECULATIVE). References to re-verify (carrying Path A's §13 identifiers for consistency, B2 Finding 7): Chi et al. JFM 2023; Schmeling/Schrimpf/Todorov BIS WP 1087 "Crypto Carry"; He/Manela/Ross/von Wachter arXiv 2212.06888 (delta-neutral carry — OUT OF SCOPE); Liu/Tsyvinski RFS 2021; Liu/Tsyvinski/Wu JF 2022; Makarov/Schoar JFE 2020. **All literature identifiers AND the load-bearing "strong basis edge is cross-sectional, not single-asset directional" claim (Chi et al.) are web-verified before the Step −1 LOCK (§1 / METHODOLOGY_NOTES §1 discipline); no LOCK text asserts a citation as fact until verified, and the §12 "most likely earned-negative" confidence is softened if the cross-sectional framing cannot be confirmed.**
- **Path A verdict:** `data/phase2c_evaluation_gate/patha_verdict_v1/patha_verdict_advisory.json` — funding H1/H2/H3 −1.77/−2.98/−1.62; 0/3 Tier-5; H1 train-refuted, H2/H3 strong-sane; `process_refuted_for_this_grid`.
- **Reusable harness (grep-verified on `main`):** `backtest/patha_{dsr_fwer,earned_negative,escalation,eval_gauntlet,holdout_producer,marginal_diagnostic,moments,orchestrator,perleg_mechanism,train_sanity}.py`; `scripts/patha_run_verdict.py`; funding infra `factors/funding{,_align}.py`, `ingestion/funding_{bulk_download,incremental_update,reconcile}.py`. `data/raw/btcusdt_funding_8h.parquet` present (for §9 Finding D's D2 leg).
- **Discipline:** `config/execution_phaseb_spot_15bps.yaml` (15 bps); `config/environments.yaml` forward_2026; `backtest/tier6_dsr.py` Form B + `Z_PASS`; `backtest/wf_lineage.py` `check_evaluation_semantics_or_raise` (`single_run_holdout_v1`); CLAUDE.md HARD CONSTRAINTS; METHODOLOGY_NOTES §36 + §37 (cross-cadence warmup; gate-at-function-boundary; under-floor verdict naming; B2 routing).

---

## 14. Terminal state

On written-spec review-gate approval + 2-leg B2: write + commit the Step −1 pre-registration LOCK (`2026-05-31-pathc-step-minus-1-preregistration-lock.md`) as its own Charlie register-event, then invoke `superpowers:writing-plans` to turn this spec into a step-by-step implementation plan (ingestion → build → run). Ingestion / build / run each remain a separate downstream Charlie register; this cycle authorizes none of them.
