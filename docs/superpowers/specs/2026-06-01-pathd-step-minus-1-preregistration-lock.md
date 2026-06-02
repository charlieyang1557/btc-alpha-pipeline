# Path D — Step −1 Pre-Registration LOCK (Open-Interest Axis)

**Date:** 2026-06-01 (UTC)
**Status:** **Charlie-registered (2026-06-01).** This file is committed **BEFORE** any OI data is ingested or peeked, any factor build, and any evaluation — its commit-order is the anti-hindsight evidence (METHODOLOGY_NOTES §3.3: pre-register expectations before running; commit-order so post-hoc rationalization is impossible). **No OI data — neither values NOR the Binance Vision file listing/schema — has been observed this cycle.** The `2020-09` OI history start is an **in-repo prior** (Path C spec §1, line 36), to be re-verified at register-A; it is NOT a value peek.

**Authority:** Charlie register 2026-06-01 — registering the a-priori values below (escalation AUTHORIZED → fresh scoping cycle; Q1 OI-only; refined-Option-A directionality; A1 drop D2 → D1-only; B2 disclose + fenced contamination-correlation set; Q2 (b) strict-parallel NOT clear-floors; N\*=3; forward_2026 gate; all long/flat). The reconciliation + the written spec were each 2-leg-B2'd (Codex *SOUND-WITH-CAVEATS* / *APPROVE-WITH-CHANGES* + advisor *ADOPT/COMMIT-WITH-CHANGES*); all findings folded.

**Binding rule:** **No post-hoc additions.** Adding any variant after any OI peek / Step-0 / run result is seen **voids N\*** and invalidates the cycle's falsification integrity. The values below are frozen for the duration of the Path D cycle.

**Governing spec:** [2026-06-01-path-d-oi-scoping-design.md](2026-06-01-path-d-oi-scoping-design.md) (v1, written-spec 2-leg-B2'd; all findings folded; commit `76a0cd7a`). **Plan:** `../plans/2026-06-01-pathd-oi-mine.md` (to be written by `writing-plans`, 2-leg-reviewed).

---

## Pre-registration 1 — Hypotheses + variant grid → N\*

**N\* = 3** (minimal grid: 3 hypotheses × 1 pre-registered variant each; **no parameter sweep**). This is the full considered inferential family; N\* counts it in full. All **long/flat**, ternary `{0, 0.5, 1.0}` sizing on `cdf_realized_vol_720`. **Direction is 100% the inherited price-trend cross** `decay_linear_close_48 > decay_linear_close_168`; **OI never originates a sign and never scales size** — it enters as exactly one removable boolean gate `oi_ok`, AND-composed with the price-long (`long iff price_long AND oi_ok, else flat`).

**OI series (locked — the firewall-critical choice):** the primary OI series is **`sum_open_interest` (base/coin-denominated contracts), NOT `sum_open_interest_value` (USDT notional).** Rationale: notional = contracts × price, so `Δlog(notional) = Δlog(contracts) + price_return` — a notional-velocity gate would mechanically embed the price return and DEFEAT the velocity firewall. **Cadence (locked):** OI's native Binance-Vision cadence is **causally downsampled to the 1h grid** (bar-close OI = the last OI observation at/before the 1h bar close — no future read); OI factors are computed **on the 1h OI series in 1h-bar units** (the §37.2 cross-cadence-warmup hazard is avoided by computing on the consumption grid). *(The series name→unit mapping, the native cadence, and the 2020-09 start are register-A empirical re-verification items, §5/§13 of the spec; the LOCK freezes the DESIGN choice — `sum_open_interest`, contracts, causal 1h downsample — not an observed value.)*

| Hyp | Family | Locked parameters |
|---|---|---|
| **H1** `oi_extreme_fade` | crowded-positioning reversal (long-biased de-risk overlay; **UN-FIREWALLED weakest leg**) | **flat** when `oi_pct_rank_2160 ≥ θ_oi_hi`; **long** otherwise (the complement). **NO `oi_sign` conjunct** — OI is directionless, so the extreme-high level tail alone defines "crowded" (unlike Path C's signed `basis_sign > 0`). **NO time-stop** — exit to flat only via the tail-gate, re-enter long when the tail clears (inherits Path A's Amendment-A1 by design; Note A). Sizing: vol-CDF ternary on `cdf_realized_vol_720` — `1.0` in band `[0.3, 0.8)`, else `0.5`; `0` when flat. |
| **H2** `oi_regime_gate` | positioning-regime gate on a price-trend book (state-class; VELOCITY-firewalled) | regime axis = `oi_velocity_ewm_240_pctrank_2160` (causal rolling-2160 percentile of the OI-velocity EWM). **DE-RISK (flat)** when that percentile `≥ 0.80` (fastest-inflow / crowding regime); **PERMISSIVE** otherwise → **long** when `decay_linear_close_48 > decay_linear_close_168`. Exit: enter de-risk regime / trend roll-over (`48 ≤ 168`) / `max_hold_bars = 24`. Same vol-CDF ternary sizing. **Min de-risk-cell occupancy ≥ 10% of evaluated train bars** (the 0.80 band gives ~20% by construction — keeps the conditional-separation kill powered). |
| **H3** `oi_momentum_continuation` | new-FLOW trend confirm (state-class; most endogenous; VELOCITY-firewalled + the graft) | **long** when `oi_velocity_ewm_240 > 0` (fresh positioning inflow) AND `oi_pct_rank_2160 < θ_oi_hi` (strictly excludes H1's tail → **exact partition at the pct-rank boundary** vs H1's `≥ θ_oi_hi`, boundary bar `= θ` belongs to H1 only) AND `decay_linear_close_48 > decay_linear_close_168`. **The graft fix:** NO price-return conjunct beyond the inherited decay cross (the only price leg = the D1 baseline), so H3's D1 marginal stays attributable to OI. Exit: `oi_velocity_ewm_240 ≤ 0` / trend roll-over / `oi_pct_rank_2160 ≥ θ_oi_hi` / `max_hold_bars = 48`. Same vol-CDF ternary sizing. **Named "new-FLOW," NOT "new-longs"** — OI velocity is sign-agnostic about who enters; the directionality is 100% the inherited price cross. |

**`θ_oi_hi` (deterministic a-priori rule — NOT a judgment call):** `θ_oi_hi := 0.90`; **if** the train count of H1 defensive-flat-exit episodes `< 200`, **then** `θ_oi_hi := 0.85` (a fixed fallback targeting eligibility/power only, orthogonal to forward Sharpe — **never tuned toward Sharpe**). Evaluated once on train; whichever value results is frozen for H1 and H3 jointly (they share the tail boundary as an **exact partition** — H1 fires at `≥ θ_oi_hi`, H3 eligible at `< θ_oi_hi`). **Floor evaluation order:** the H1 ≥200-episode floor is evaluated at the **frozen** θ (if the fallback fired, episodes are recounted at 0.85 and the floor judged there — the strategy and its eligibility floor always share one θ).

**Locked factor windows (a-priori, calendar-time parity with Path A/C; no train tuning) — 4 OI factors:**
- `oi_pct_rank_2160` = causal rolling **2160-bar** (≈90 days) percentile of the OI **level** (`sum_open_interest`).
- `oi_velocity_ewm_240` = causal EWM (`adjust=False`) span **240** bars (≈10d) of `oi_log_change[t] = log(OI[t]) − log(OI[t−1])` (the flow-of-new-positioning firewall quantity).
- `oi_velocity_ewm_240_pctrank_2160` = causal rolling **2160-bar** percentile of `oi_velocity_ewm_240` (**H2's regime axis**; the nested percentile-of-velocity-EWM, mirroring Path C's `basis_ewm_240_pctrank_2160`).
- `oi_sign` = sign of `oi_log_change`.
- Price-trend confirm reuses Path B's `decay_linear_close_48 > decay_linear_close_168`. Sizing reuses Path B's `cdf_realized_vol_720` band (half-open `[0.3, 0.8)`, inherited convention).
- **Warmup:** the 2160-bar percentile factors (`oi_pct_rank_2160` and the nested `oi_velocity_ewm_240_pctrank_2160`) need 2160 bars; the nested percentile's `min_periods = 2160` dominates the inner 240-EWM warmup. All in **1h-bar units** — no `input_period_bars` conversion (OI is downsampled to the 1h grid at ingestion). No trade may fire during warmup.

## Pre-registration 2 — Gate (locked, never revisited post-result)

- Cost anchor: `spot_realistic_15bps_v1` — 15 bps/side (`config/execution_phaseb_spot_15bps.yaml`). **Not relaxed.**
- Tier-5 entry: `holdout_sharpe > 0` (strict) at 15 bps on the **forward_2026** single-run holdout artifact (`check_evaluation_semantics_or_raise`, `evaluation_semantics = 'single_run_holdout_v1'`).
- Tier-6 multiplicity: DSR-FWER, **Form B authoritative**, at **N\* = 3** (`backtest/tier6_dsr.py`, `Z_PASS = 1.644853626951472` frozen; reused for Path D's own new cohort; **sealed `tier6_dsr_v1` byte-untouched — sha256 re-verified before AND after**).
- 2025 test touched once only for a `c_positive` confirmation.

## Pre-registration 3 — Process-delta (set before any result)

- **Cost-aware objective:** any ranking among the pre-registered variants is by Sharpe **net of 15 bps/side**; floors applied **before** ranking.
- **Hypothesis-class floors (eligibility, on the TRAIN window) — with honest power disclosure:**
  - **H1 (long-biased overlay):** ≥ **200 defensive flat-exit episodes** over train (NOT long-bar occupancy); episodes are **transition-bound**, so **verified at train, not assumed**; an **H1-INDETERMINATE-on-floor contingency is pre-registered**. As the **un-firewalled level leg**, H1's D1 is expected to be the least attributable; a non-inert H1 D1 is most likely an artifact (the Path A/C H1 replay).
  - **H2 / H3 (state-class):** `zero_fraction < 0.50` **AND** ≥ **200** trades over train. The `zero_fraction` floor is **NOT clearable by band design** — the inherited price-trend AND-confirm binds long-bar occupancy. **H2/H3 are pre-registered as expected-INDETERMINATE on `zero_fraction`.**
  - **Heightened under-power (Q2):** the **2020-09 OI start** lops ~8 months off the OI-informed train (the immutable 2020-2021+2023 split is unchanged; OI factors are NaN/un-warmed before ~2020-09 + warmup), so **all three legs could be INDETERMINATE** — the verdict may rest on the §37.3 substantive-measured-loss path with thinner samples than Path C. Pre-disclosed.
  - **Deployment-readiness target** (separate from eligibility): ≥ **1000** trades.
  - **Independent-of-floor verdict robustness (§37.3):** an under-floor leg with measured forward loss is a *substantive* negative (measured loss), not a *vacuous* eligibility exclusion. §37.3's substantive-negative path is available **only when the forward Sharpe is a measured loss**; if an expected-INDETERMINATE leg instead returns a **thin-sample near-zero/positive** forward Sharpe (floor-ineligible AND `< UNDER_DETERMINED_TRADE_THRESHOLD` forward trades), it is reported **genuinely under-determined** — NOT folded into the earned-negative, surfaced to Charlie's binding read as a power gap. **OI-specific (thin-sample-SANE):** an under-powered-but-SANE H3 (the most-endogenous leg) on the short OI train is reported **consistent-with-undetected-momentum/vol-leakage, NOT as OI-mechanism evidence.**
- **Sizing:** single-factor vol-CDF ternary `{0, 0.5, 1.0}` (OI gates, never scales size).
- **Causal OI derivation (contracts, 1h downsample):** primary series `sum_open_interest` (contracts, NOT notional); causal 1h downsample (bar-close = last OI ≤ close); dedicated causality guard (delete/reverse/shuffle future obs → bit-identical 1h value); no-future-bar-read assertion; cross-stream join integrity (OI 1h grid vs spot OHLCV 1h grid — identical coverage OR explicit inner-join with logged drop count; one-bar misalignment RAISES). Inherited G1–G4 leakage guards apply to the new OI factors.
- **Orthogonalization diagnostic (fenced — diagnostic-only, NOT in N\*, NOT promotion-affecting): D1 ONLY (D2 DROPPED, decision A1).**
  - **D1 (vs momentum):** OI-gated strategy vs the identical price-trend / always-long baseline WITHOUT the OI gate (Sharpe-difference on the same bars). **D1 attributes, it does NOT license** (it removes the shared momentum LEVEL, not momentum/vol re-entering through the gate's bar-selection). **A near-zero D1 is the modal expectation** (inert `oi_ok` → `d1_marginal ≈ 0` by construction) → read as "OI gate inert," NOT an edge. Promotion locus = Tier-5 + DSR `pass_B`, never D1 standalone.
  - **§38.3 scope (D1-only):** with D2 dropped there is no agreement-conjunction; the `redundancy_read` / `d2_agrees` / `d1_noninert` truth-table machinery has **NO role** and is **asserted unwired** in the Path D verdict path. Path D inherits ONLY the §38.3 *fenced-label-read-against-the-gate* + *inert-D1-is-modal* discipline.
  - **Fenced contamination-correlation set (NEW — decision B2):** report `corr(oi_velocity_ewm_240, {return_1h, abs(return_1h), realized_vol_24h, cdf_realized_vol_720})` — **Pearson AND Spearman; on the forward_2026 post-warmup bars AND the train bars, reported separately; on each hypothesis's signal-active bars; NaN-dropped.** Purpose: quantify the disclosed vol/liquidation-cascade residual (a non-inert D1 on OI-velocity is consistent with a vol/tail filter that D1 cannot catch — §12 of the spec). **Measured-and-reported-only; never a control; never promotion-affecting; not in N\*.** No vol-control diagnostic is added (scope/DoF discipline).
- **Pre-registered diagnostic/taxonomy tolerances (labeling-only, pre-data, anti-hindsight — registered HERE in the LOCK, before any OI touch, preempting a later ratification):**
  - `D1_NONINERT_THRESHOLD = 0.10` (Sharpe) — `|d1_marginal_sharpe| > 0.10` ⇒ the OI gate is "non-inert"; the inert-D1-modal read is the correctly-humble outcome, not a failure. Labeling only — never promotion.
  - `UNDER_DETERMINED_TRADE_THRESHOLD = 10` — a floor-INELIGIBLE leg with `< 10` forward trades AND `holdout_sharpe ≥ 0` is tagged **under-determined** (power gap) and NOT folded into the earned-negative. Directionally conservative (can only PREVENT over-claiming a negative).
  - **NO `D2_AGREES_TOLERANCE`** — D2 is dropped (A1); there is no agreement band to set.

## Pre-registration 4 — Kill-criterion taxonomy + D-escalation (advisory; Charlie registers the fire)

- **mechanism-refuted** — no leg's conditional forward-return sign matches its hypothesized direction (H1 reversal-DOWN; H2 permissive-mean > de-risk-mean AND permissive-mean > 0; H3 continuation-UP). Earned negative.
- **process-refuted-for-this-grid** — ≥1 leg mechanism-sane, but **no variant clears Tier-5 `holdout_sharpe > 0`** at 15 bps on forward_2026. Earned negative.
- **d-positive** — ≥1 variant clears Tier-5 `holdout_sharpe > 0` (even if it fails DSR-FWER at N\*); weak if no DSR pass (needs 2025 OOS confirmation AND must survive the §9 D1 attribution + the fenced contamination-correlation disclosure), stronger if a DSR `pass_B`. NOT an earned negative. Even a d-positive is **not** cleanly attributable to OI-information vs a vol/liquidation filter at the diagnostic level (§12).
- **Mechanism-sanity (train-only):** conditional forward-return sign test (Pre-reg 1 directions) at **24h AND 72h** horizons. **strong-sane** = hypothesized sign at *both*; **weak-sane (floor)** = sign at *either*. Both signs pre-registered + reported separately; a verdict resting on weak-sane-only legs is flagged.
- **Localization on a D-negative (calibrated):** a D-negative extends the localization to the **independent positioning member** — *"OI adds no directional rescue to a single-asset long/flat price-trend book under this grid."* It is **NOT family-level**: OI is one independent member; **liquidations, cross-sectional/multi-asset rank structure, short legs, and OI-scaled sizing remain untried, not falsified.** OI-not-exonerated-in-general. The *strong* OI/positioning edge is cross-sectional (Chi et al. JFM 2023), which the single-asset directional engine cannot express.
- **Next-axis escalation (advisory):** any "a real edge exists" determination is gated by DSR-**significance** (`pass_B` / PSR ≥ 0.95), **not** a point-estimate. **The binding taxonomy verdict and the actual escalation are a Charlie register-event** at the earned-negative gate — never an automated fire.

---

## Verified citations (carried verbatim-verified from the Path C LOCK, per spec §1 / METHODOLOGY_NOTES §1)

- **Chi, Hao, Hu & Ran — "An empirical investigation on risk factors in cryptocurrency futures"** — Journal of Futures Markets 2023, 43(8):1161–1180, DOI 10.1002/fut.22425. The basis/positioning edge that is statistically strong is **cross-sectional** (predicting cross-sectional differences in crypto-futures returns), short-horizon; this is the load-bearing "strong edge is cross-sectional, NOT single-asset directional" anchor for the §1 honest prior. (Re-verify any OI-specific extension at the build-register B2.)
- **Schmeling, Schrimpf & Todorov — "Crypto Carry"** — BIS Working Paper No 1087 (2023). Crypto carry driven by leveraged-long demand + limits to arbitrage → supports the positioning interpretation + the ETF-compression temper.
- **He, Manela, Ross & von Wachter — "Fundamentals of Perpetual Futures"** — arXiv:2212.06888. The no-arbitrage implied edge is delta-neutral carry — **OUT OF SCOPE** for a single-asset directional engine.
- **NOT load-bearing:** the single-asset *directional* OI price×OI 4-state sign taxonomy is folklore-grade (no peer-reviewed single-asset time-series result); the cycle does not rest on it (it survives only as H3's typed `oi_velocity > 0` confirm).
- **UNVERIFIED this cycle (the #1 register-A item):** OI history start (in-repo prior `2020-09`), the Binance Vision `metrics` CSV schema/header, the native cadence, and the `sum_open_interest`=contracts vs `sum_open_interest_value`=notional unit mapping. CCXT `fetch_open_interest_history` ≈ 30-day window only → bulk Vision is the sole full-history path. Per §38.1/§38.2 the first ingestion run is the format/availability validation gate (header-autodetect parser).

---

## What this lock authorizes next

- **The implementation plan** (`superpowers:writing-plans`, 2-leg-reviewed) may now be written: ingestion → OI-feature pipeline → factors + DSL hypotheses + `pathd_*` harness reuse + D1-only diagnostic + fenced contamination-correlation set → run.
- **Ingestion / build / run each remain a separate downstream Charlie register-event** — this lock authorizes none of them; it freezes the pre-registration only.
- **Per-task commits await Charlie authorization** (only Charlie-register authorizes operational fires).
- **Liquidations, cross-sectional/multi-asset rank structure, short legs, and OI-scaled sizing** remain conditional, separately-registered successors — **not scoped here** (anti-pre-emption). The post-Path-D strategic fork (cross-sectional pivot vs equities/options) is deferred to a dedicated future session.

---

## Note A — H1 inherits Path A's Amendment-A1 no-time-stop correction (by design, not a new amendment)

Path A's LOCK originally mis-applied a `max_hold` to its H1, then removed it (Amendment A1) on the pre-data recognition that a near-always-long de-risk overlay (long on the complement of the rare extreme tail) suffers ~non-mechanistic churn drag from a time-stop that confounds attribution. Path C's H1 adopted the corrected design from the outset; Path D's H1 is the same archetype and does likewise: **no time-stop, exit only via the tail-gate.** This is not a Path D amendment — it is the inherited, already-corrected baseline. H2/H3 retain `max_hold` 24/48 (appropriate backstops for their condition-based exits).
