# Path C — Step −1 Pre-Registration LOCK (Perp-Spot Basis Axis)

**Date:** 2026-05-31 (UTC)
**Status:** **DRAFT — pending Charlie register.** This file is to be committed **BEFORE** any basis data is ingested or peeked, any factor build, and any evaluation — its commit-order is the anti-hindsight evidence (METHODOLOGY_NOTES §3.3: pre-register expectations before running; commit-order so post-hoc rationalization is impossible). Only the Binance Vision file *listing* + 2020-01 schema have been verified (mark/index/premiumIndex kline history starts 2020-01, §13 of the spec); **no basis *values* in the forward_2026 gate window have been observed.**

**Authority:** Charlie register (to be recorded on the register-event) — registering the a-priori values below (Q1 basis-only, Q2 (b) strict-parallel + §37.3 denser-delta resolved to Option A, reframe option-1-then-OI, N\*=3, forward_2026 gate, all long/flat; round-1 B2 Findings 1–8 + round-2 2-leg B2 — Codex 2e/2f/2d + advisor F1–F6 — all folded).

**Binding rule:** **No post-hoc additions.** Adding any variant after any basis peek / Step-0 / run result is seen **voids N\*** and invalidates the cycle's falsification integrity. The values below are frozen for the duration of the Path C cycle.

**Governing spec:** [2026-05-31-path-c-basis-scoping-design.md](2026-05-31-path-c-basis-scoping-design.md) (v1, two-round 2-leg B2 — advisor SOUND-WITH-CAVEATS + Codex anchors-confirmed; all findings folded; commits `1af19f5` + `4801ba2`). **Plan:** `../plans/2026-05-31-pathc-basis-mine.md` (to be written by `writing-plans`, 2-leg-reviewed).

---

## Pre-registration 1 — Hypotheses + variant grid → N\*

**N\* = 3** (minimal grid: 3 hypotheses × 1 pre-registered variant each; **no parameter sweep**). This is the full considered inferential family; N\* counts it in full. All **long/flat**, ternary `{0, 0.5, 1.0}` sizing on `cdf_realized_vol_720`. Basis factors are computed on the **native 1h `basis_rel` series** (causal rolling over 1h bars — **NO cross-cadence carry**; basis is native-1h, the §37.2 simplification). Basis gates the long ON/OFF or the entry trigger; it never scales position size.

**Basis series (locked):** `basis_rel[t] = (markPrice_close[t] − spot_close[t]) / spot_close[t]` — perp mark price (Binance USDⓂ `markPriceKlines` 1h) over the canonical Binance spot BTCUSDT 1h close (`data/raw/btcusdt_1h.parquet`), joined on `open_time_utc` (same grid, no carry). Less-clamped than `premiumIndex` (B2 Finding 8: markPrice is itself a smoothed Binance construct — "less dampening," not strictly un-clamped; characterized at ingestion against the `premiumIndex` / `(mark−index)` cross-check within a pinned numeric tolerance).

| Hyp | Family | Locked parameters |
|---|---|---|
| **H1** `basis_extreme_fade` | crowded-premium reversal (long-biased de-risk overlay) | **flat** when `basis_pct_rank_2160 ≥ θ_basis_hi` AND `basis_sign > 0`; **long** otherwise (the complement). **NO time-stop** — exit to flat only via the tail-gate, re-enter long when the tail clears (inherits Path A's Amendment-A1 correction by design: H1 is a near-always-long de-risk overlay, so a `max_hold` would impose ~non-mechanistic churn drag; see Note A). Sizing: vol-CDF ternary on `cdf_realized_vol_720` — `1.0` in band `[0.3, 0.8)`, else `0.5`; `0` when flat. |
| **H2** `basis_regime_gate` | regime-gate on a price-trend book (state-class) | regime axis = causal rolling-2160 percentile of `basis_ewm_240`. **DE-RISK (flat)** when that percentile `≥ 0.80`; **PERMISSIVE** otherwise → **long** when `decay_linear_close_48 > decay_linear_close_168`. Exit: enter de-risk regime / trend roll-over (`48 < 168`) / `max_hold_bars = 24`. Same vol-CDF ternary sizing. **Min de-risk-cell occupancy ≥ 10% of evaluated train bars** (B2 Finding 6 — the 0.80 band gives ~20% by construction, comfortably above; keeps the conditional-separation kill powered). |
| **H3** `basis_momentum_continuation` | moderate-persistence trend confirm (state-class) | **long** when `basis_ewm_480 > 0` AND `basis_pct_rank_2160 < θ_basis_hi` (strictly excludes H1's tail → **exact partition at the pct-rank boundary** vs H1's `≥ θ_basis_hi` flat-tail, B2 Codex Finding 2e; H1's flat *also* requires `basis_sign > 0` — a subset of that tail) AND `decay_linear_close_48 > decay_linear_close_168`. Exit: `basis_ewm_480 ≤ 0` / trend roll-over / `basis_pct_rank_2160 ≥ θ_basis_hi` / `max_hold_bars = 48`. Same vol-CDF ternary sizing. |

**`θ_basis_hi` (deterministic a-priori rule — B2 Finding 4, NOT a judgment call):** `θ_basis_hi := 0.90`; **if** the train count of H1 defensive-flat-exit episodes `< 200`, **then** `θ_basis_hi := 0.85` (a fixed fallback targeting eligibility/power only, orthogonal to forward Sharpe — **never tuned toward Sharpe**). The fallback is evaluated once on train; whichever value results is frozen for H1 and H3 jointly (they share the tail boundary as an **exact partition at the pct-rank boundary** — H1 fires at `≥ θ_basis_hi`, H3 eligible at `< θ_basis_hi`; the boundary bar `= θ` belongs to H1's tail only, B2 Codex Finding 2e). **Floor evaluation order (B2 advisor Finding 6):** the H1 ≥200-episode floor is evaluated at the **frozen** θ — i.e. if the fallback fired, episodes are recounted at 0.85 and the floor judged there (the strategy and its eligibility floor always share one θ).

**Locked factor windows (a-priori, calendar-time parity with Path A; no train tuning):**
- `basis_pct_rank_2160` = causal rolling **2160-bar** (≈90 days = Path A's 270 settlements × 8) percentile of `basis_rel`.
- `basis_ewm_240` / `basis_ewm_480` = causal EWM (`adjust=False`) spans of **240** / **480** bars (≈10d / 20d = Path A's 30 / 60 settlements × 8).
- `basis_sign` = sign of `basis_rel`.
- Price-trend confirm reuses Path B's `decay_linear_close_48 > decay_linear_close_168`. Sizing reuses Path B's `cdf_realized_vol_720` band (half-open `[0.3, 0.8)` per the inherited `SizingBand` convention — measure-zero boundary, no behavior change; Path A Clarification C1 inherited).
- **Warmup:** `basis_pct_rank_2160` needs 2160 bars; the H2 regime percentile (rolling-2160 of `basis_ewm_240`) needs 2160 bars — the percentile's `min_periods = 2160` dominates the inner 240-EWM warmup (mirrors Path A's `funding_ewm_30_pctrank_270` nesting, B2 advisor Finding 7). All in **1h-bar units** — no `input_period_bars` conversion (basis is native-1h). No trade may fire during warmup.

## Pre-registration 2 — Gate (locked, never revisited post-result)

- Cost anchor: `spot_realistic_15bps_v1` — 15 bps/side (`config/execution_phaseb_spot_15bps.yaml`). **Not relaxed.**
- Tier-5 entry: `holdout_sharpe > 0` (strict) at 15 bps on the **forward_2026** single-run holdout artifact (`check_evaluation_semantics_or_raise`, `evaluation_semantics = 'single_run_holdout_v1'`).
- Tier-6 multiplicity: DSR-FWER, **Form B authoritative**, at **N\* = 3** (`backtest/tier6_dsr.py`, `Z_PASS = 1.644853626951472` frozen; reused for Path C's own new cohort; sealed `tier6_dsr_v1` byte-untouched — sha256 re-verified before AND after).
- 2025 test touched once only for a `c_positive` confirmation.

## Pre-registration 3 — Process-delta (set before any result)

- **Cost-aware objective:** any ranking among the pre-registered variants is by Sharpe **net of 15 bps/side**; floors applied **before** ranking.
- **Hypothesis-class floors (eligibility, on the TRAIN window) — with honest power disclosure (B2 Finding 1):**
  - **H1 (long-biased overlay):** ≥ **200 defensive flat-exit episodes** over train — NOT long-bar occupancy. Basis's 1h cadence is *expected* to raise the episode count above Path A's 150, but episodes are **transition-bound, not tail-bar-bound**, so this is **verified at train, not assumed**; an **H1-INDETERMINATE-on-floor contingency is pre-registered** (B2 advisor Finding 2: extends to a possible H1-D1-low-attribution *forward* read — Path A H1 fired only 9 forward trades; forward-window attribution power is verified at the run, not assumed).
  - **H2 / H3 (state-class):** `zero_fraction < 0.50` **AND** ≥ **200** trades over train. The `zero_fraction` floor is **NOT clearable by basis-band design** — the inherited price-trend AND-confirm (`decay_48 > decay_168`, fires <50% of bars) binds long-bar occupancy (verified: Path A H2/H3 were `zero_fraction` 0.62/0.67 at a wide-open 0.80 band). **H2/H3 are therefore pre-registered as expected-INDETERMINATE on `zero_fraction`.**
  - **Deployment-readiness target** (separate from eligibility): ≥ **1000** trades.
  - **Independent-of-floor verdict robustness (§37.3):** an under-floor leg with measured forward loss is a *substantive* negative (measured loss), not a *vacuous* eligibility exclusion. The verdict is named to disclose which; H2/H3 INDETERMINATE-on-floor does NOT block an earned negative when the forward loss is measured. **(B2 advisor Finding 3 — the conditional, made explicit because this cohort pre-commits H2/H3 to expected-INDETERMINATE:)** §37.3's substantive-negative path is available **only when the forward Sharpe is a measured loss**; if an expected-INDETERMINATE leg instead returns a **thin-sample near-zero/positive** forward Sharpe (too few trades for a substantive read AND floor-ineligible), it is reported **genuinely under-determined** — neither substantive-negative nor Tier-5-eligible, NOT folded into the earned negative, and surfaced to Charlie's binding read as a power gap (never silently read as a negative).
- **Sizing:** single-factor vol-CDF ternary `{0, 0.5, 1.0}` (basis gates, never scales size).
- **Causal basis derivation (native-1h, no carry):** `basis_rel` joins markPrice@t to spot_close@t on `open_time_utc`; dedicated causality guard (delete/reverse/shuffle future bars → bit-identical); no-future-bar-read assertion. Inherited G1–G4 leakage guards apply to the new basis factors.
- **Dual-orthogonalization diagnostic (fenced — diagnostic-only, NOT in N\*, NOT promotion-affecting; B2 Finding 2):** on the same bars,
  - **D1 (vs momentum):** basis-gated strategy vs the identical price-trend / always-long baseline WITHOUT the basis gate.
  - **D2 (vs funding):** basis-gated strategy vs the *funding-gated* Path A strategy (does higher-frequency basis add over the 8h funding it is derived from?).
  - **Inference rule (pinned, anti-vacuous-agreement):** redundancy is confirmed ONLY by the **conjunction** `basis-gated ≈ funding-gated` (D2) **AND** each gate **non-inert** (its D1 marginal materially ≠ 0). Mutual agreement under jointly-inert D1 is **vacuous** and licenses no redundancy/generalization read. **(D2-disagree branch, B2 advisor Finding 1):** if `basis-gated ≠ funding-gated` with D1 non-inert, higher-frequency basis carries marginal information over the 8h funding — this does NOT auto-promote (still Tier-5 + DSR `pass_B` + 2025 OOS gated) but **blocks** the cross-frequency redundancy read and is surfaced to Charlie's binding read as a genuine (small-N\*) basis-specific signal. D1 and D2 each emit a separate fenced record per hypothesis.

## Pre-registration 4 — Kill-criterion taxonomy + C-escalation (advisory; Charlie registers the fire)

- **mechanism-refuted** — no leg's conditional forward-return sign matches its hypothesized direction (H1 reversal-DOWN; H2 permissive-mean > de-risk-mean AND permissive-mean > 0; H3 continuation-UP). Earned negative.
- **process-refuted-for-this-grid** — ≥1 leg mechanism-sane, but **no variant clears Tier-5 `holdout_sharpe > 0`** at 15 bps on forward_2026. Earned negative.
- **c-positive** — ≥1 variant clears Tier-5 `holdout_sharpe > 0` (even if it fails DSR-FWER at N\*); weak if no DSR pass (needs 2025 OOS confirmation AND must survive the §9 Finding D dual-orthogonalization), stronger if a DSR `pass_B`. NOT an earned negative.
- **Mechanism-sanity (train-only):** conditional forward-return sign test (Pre-reg 1 directions) at **24h AND 72h** horizons. **strong-sane** = hypothesized sign at *both* horizons; **weak-sane (floor)** = sign at *either*. Both signs pre-registered and reported separately; a verdict resting on weak-sane-only legs is flagged in the advisory bundle.
- **Localization on a C-negative (calibrated, B2 Finding 5):** a C-negative + a confirmed D2 redundancy (per the Pre-reg 3 conjunction rule) tightens the Path A localization to *"the funding/basis premium signal adds no directional rescue at either its 8h or 1h sampling frequency under this grid"* — a **cross-frequency**, robustness-confirming statement. It is **NOT yet "the whole positioning-premium family fails"**: funding and basis are two near-collinear members; the genuinely-independent member (open interest — the noted successor) must also be tested before any family-level claim. Basis-not-exonerated-in-general (short legs / basis-scaled sizing / cross-structure untried).
- **Next-axis escalation (advisory):** any "a real edge exists" determination is gated by DSR-**significance** (`pass_B` / PSR ≥ 0.95), **not** a point-estimate. **The binding taxonomy verdict and the actual escalation are a Charlie register-event** at the earned-negative gate — never an automated fire.

---

## Verified citations (web-verified before this LOCK, per spec §1 / METHODOLOGY_NOTES §1; independently re-verified 2026-05-31 via WebSearch)

- **He, Manela, Ross & von Wachter — "Fundamentals of Perpetual Futures"** — arXiv:2212.06888 (v1 2022-12-13; updated through 2024). **VERBATIM-confirmed (re-verified 2026-05-31):** *"long investors periodically pay shorts a funding rate proportional to this difference"* (perpetual − spot), funding payment `κ(Fₛ − Sₛ)ds` → confirms the load-bearing reframe identity **basis ≈ funding by construction**; the no-arbitrage / cash-and-carry implied strategy is the strong (delta-neutral) edge, OUT OF SCOPE for a single-asset directional engine.
- **Chi, Hao, Hu & Ran — "An empirical investigation on risk factors in cryptocurrency futures"** — Journal of Futures Markets 2023, 43(8):1161–1180, DOI 10.1002/fut.22425. **VERBATIM-confirmed (re-verified 2026-05-31):** *"the basis is the strongest signal predicting **cross-sectional** differences in cryptocurrency futures returns"*; momentum not statistically powerful; basis-momentum disappears once basis is accounted for; *"daily factor returns are statistically much stronger than weekly factor returns, while monthly factor returns are nonsignificant"* (short horizon); sample 2017–2021. This is the load-bearing "strong basis edge is **cross-sectional**, not single-asset directional + short-horizon" anchor — directly supports the §12 honest-prior framing.
- **Schmeling, Schrimpf & Todorov — "Crypto Carry"** — BIS Working Paper No 1087 (2023-04-04; also Management Science 2024, DOI 10.1287/mnsc.2024.05069). **VERIFIED:** crypto carry reaches >40% p.a., driven by leveraged-long demand + limits to arbitrage → supports the positioning interpretation + the ETF-compression temper.
- **NOT asserted (not abstract-confirmed; flagged body-level-only, NOT load-bearing):** He et al. "Sharpe ~1.8–3.5 / momentum R²>50%"; Schmeling "high carry forecasts crashes / ETF DiD cut carry ~36%". The Path C prior does **not** rest on these specifics.

---

## What this lock authorizes next

- **The implementation plan** (`superpowers:writing-plans`, 2-leg-reviewed) may now be written: ingestion → basis-feature pipeline → factors + DSL hypotheses + `pathc_*` harness reuse + dual-orthogonalization extension → run.
- **Ingestion / build / run each remain a separate downstream Charlie register-event** — this lock authorizes none of them; it freezes the pre-registration only.
- **Per-task commits await Charlie authorization** (only Charlie-register authorizes operational fires).
- **Open interest** (the registered direction-noted successor — "先 1 再 2"), liquidations, short legs, and basis-scaled sizing remain conditional, separately-registered successors — **not scoped here** (anti-pre-emption).

---

## Note A — H1 inherits Path A's Amendment-A1 no-time-stop correction (by design, not a new amendment)

Path A's LOCK originally mis-applied a `max_hold = 72` to H1, then removed it (Amendment A1) on the pre-data recognition that H1 is a near-always-long de-risk overlay (long on the ~90% complement of the extreme tail), for which a time-stop imposes ~non-mechanistic churn drag (~35 forced round-trips over forward_2026 at 30 bps ≈ 10% artifact drag) that would confound attribution. Path C's H1 is the same archetype, so it adopts the **corrected** design from the outset: **no time-stop**, exit only via the tail-gate. This is not a Path C amendment — it is the inherited, already-corrected baseline. H2/H3 retain `max_hold` 24/48 (appropriate backstops for their condition-based exits).

---

## Ratification Clarification R1 — diagnostic/taxonomy operationalization values (2026-06-01, Charlie-ratified; PRE-RUN / anti-hindsight)

**Status:** Charlie-ratified at the Phase D register ENTRY, **before** the `PHASE_D_AUTHORIZED` fire and before any forward_2026 basis value was computed or observed (the gate remains `False` in the repo; no `pathc_verdict_v1/` artifact exists at ratification time). These values were pre-committed in code during the Phase C build, surfaced at a 2-leg PFR (Codex + advisor), and the advisor confirmed they govern **diagnostic / taxonomy LABELING only — never promotion** (promotion is Tier-5 `holdout_sharpe > 0` + DSR `pass_B`, which these do not touch). Ratifying them now is therefore anti-hindsight-clean (pre-data, direction-orthogonal). They are frozen for the Path C cycle alongside Pre-registrations 1–4.

| Value / choice | Ratified | Role (labeling-only; not promotion) |
|---|---|---|
| `UNDER_DETERMINED_TRADE_THRESHOLD` | **10** | F3 carve-out: a floor-INELIGIBLE leg with `< 10` forward trades AND `holdout_sharpe >= 0` is tagged **under-determined** (power gap) and NOT folded into the earned-negative. Directionally conservative (can only PREVENT over-claiming a negative). |
| `D2_AGREES_TOLERANCE` | **0.10** (Sharpe) | `redundancy_read`: `|d2_marginal_sharpe| <= 0.10` ⇒ basis-gated ≈ funding-gated ("agree"). ~measurement noise on a ~100-trade forward window. |
| `D1_NONINERT_THRESHOLD` | **0.10** (Sharpe) | `redundancy_read`: `|d1_marginal_sharpe| > 0.10` ⇒ the basis gate is "non-inert". A "vacuous" read (agreement under a jointly-inert D1) is a plausible, honest outcome and is the correctly-humble result, not a harness failure. |
| D2 hypothesis correspondence | **same-index** (basis-Hi ↔ funding-Hi) | D2 compares each basis hypothesis to the same-archetype Path A funding hypothesis (H1↔H1 / H2↔H2 / H3↔H3) — the documented funding-twin mapping (§3 / design spec). |
| F3 design | **retain the `=10` trade-count threshold** | (vs "floor-ineligible + sign-of-Sharpe alone") — distinguishes a barely-under-floor decent sample from a genuinely thin one. |

**Clarification R1b — H2 trend-rollover exit operator (PFR Q3, documentation accuracy).** Pre-registration 1's H2 prose writes the trend-rollover exit as "`48 < 168`". The compiled DSL (and the vetted/sealed Path A H2 it mirrors) uses `decay_linear_close_48 <= decay_linear_close_168` — the **exact logical complement** of the H2 entry confirm `decay_linear_close_48 > decay_linear_close_168`. At the measure-zero boundary `48 == 168` the strategy is flat either way (the entry `>` already excludes equality), so the `<=` vs `<` distinction is **behaviorally immaterial**; the prose `<` is loose shorthand for "trend has rolled over" (= `<=`). No code change; the implementation is correct and Path-A-faithful. *(PFR Codex Q1 — EWM factors omit `min_periods` — was reviewed as a benign early-bar calibration matter, not look-ahead, matching Path A; no change.)*

**The gate is unchanged:** `PHASE_D_AUTHORIZED` stays `False`. The actual forward_2026 verdict run remains a separate, explicit Charlie data-touch register-event.
