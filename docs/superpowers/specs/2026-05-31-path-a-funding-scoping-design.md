# Path A — Funding-Rate Axis Mechanism-First Mine (Alpha-Source Rethink, Cycle 2) — Design Spec

**Date:** 2026-05-31 (UTC)
**Version:** v1 (design approved in-chat by Charlie 2026-05-31; pending written-spec review gate + 2-leg B2 before the Step −1 LOCK register).
**Status:** DRAFT — design body approved wholesale in chat. NOT yet authorized for the Step −1 LOCK register, for any ingestion/build/run, or for any commit beyond this spec doc itself.
**Cycle class:** Bounded, pre-committed, **one-cycle** falsification test of the funding-rate information axis — the conditional successor to Path B, now **escalation-WARRANTED** (Path B earned-negative, 2026-05-31) and opened as a **fresh, separately-registered scoping cycle** (anti-pre-emption).
**Predecessor:** Path B mechanism-first OHLCV re-mine — VERDICT `process_refuted_for_this_grid` (earned negative): H1/H2/H3 net Sharpe −8.42 / −2.65 / −2.61 on forward_2026; 0/3 Tier-5; 0 DSR pass; A-escalation warranted under the §9 significance amendment (0/39 dead candidates lift at `pass_B`). Spec [`2026-05-30-pathb-mechanism-first-rethink-design.md`](2026-05-30-pathb-mechanism-first-rethink-design.md); LOCK [`2026-05-30-pathb-step-minus-1-preregistration-lock.md`](2026-05-30-pathb-step-minus-1-preregistration-lock.md); verdict artifact `data/phase2c_evaluation_gate/pathb_verdict_v1/pathb_verdict_advisory.json`.
**Cost anchor:** `spot_realistic_15bps_v1` — 15 bps/side, 30 bps round trip (`config/execution_phaseb_spot_15bps.yaml`). HARD CONSTRAINT; not relaxed anywhere in this cycle.

---

## 0.1 Registered decisions (provenance)

Each was surfaced as plain-text options + intuitive Chinese and explicitly registered by Charlie 2026-05-31 (reviewer/research convergence was advisory only):

| Decision | Registered outcome |
|---|---|
| Q1 — data family | **Funding-rate only** (single new crypto-native family; the literal Path B seed `funding_epoch_fade`). |
| Q2 — N\* | **N\* = 3** (three funding mechanisms, one pre-registered variant each, no parameter sweep). |
| Q3 — Tier-5 gate window | **forward_2026** — the *same* OOS slice the dead-18 scored 0/18 and Path B's H1/H2/H3 were gated on (apples-to-apples). 2025 reserved as the positive-confirmation window per the inherited taxonomy. |
| Q4 — cycle boundary | **Scope-only**, with the **full funding-ingestion design pinned in this spec** but **zero data touched** this cycle. Ingestion / build / run are each their own downstream Charlie register. |
| Q5 — sizing / shorts | **All three long/flat** (no short legs); mirrors Path B's no-short discipline. A short-leg H1 variant is deferred to a *separate* register, only if H1 long/flat passes train sanity but fails forward as merely-defensive. |
| Mechanical pre-reg defaults | Accepted as proposed (funding factors / percentile threshold / 24h+72h sanity horizon / reuse Path B price-confirm factor / single-factor vol-CDF sizing / inherit §9 escalation + reuse harness). The one deliberate deviation from strict Path B parity — the **24h + 72h** mechanism-sanity horizon (vs Path B's uniform 24-bar) — was explicitly kept by Charlie. |

---

## 1. Motivation & frame

**Binding constraint = the alpha source / hypothesis-space** (reviewer-convergent, Charlie-registered; memory `alpha-source-is-the-binding-constraint-not-data-methodology`). Path B held the **data** fixed (OHLCV) and varied **only the process** (cost-aware objective + min-trade floors + ternary sizing + 3 mechanism-first hypotheses) → earned negative. That localizes failure away from *{cost-awareness + trade-frequency + ternary sizing + these 3 OHLCV mechanisms}* and **earns A as the next-cheapest untried axis** — but does **not** exonerate OHLCV in general.

**Why funding-rate is the right A axis.** It is the cheapest, cleanest crypto-native information the spot-OHLCV set cannot express: free Binance-Vision bulk history from **2020-01** (matching the OHLCV start exactly), UTC-native, and it directly cashes the registered Path B seed (`funding_epoch_fade`). Path A now holds the **process** fixed (the Path-B-validated cost-aware + floor + ternary discipline) and varies **only the data axis** (OHLCV → OHLCV + funding):
- **A-negative** → the funding axis, under this process and these 3 mechanisms, did not rescue edge either → the binding-constraint thesis is *further* earned, and the next conditional axis (basis / OI / short legs / continuous sizing) is what a *future, separate* register would weigh.
- **A-positive** → funding adds directional edge OHLCV-process-only lacked → a genuine, if small-N\*, finding requiring 2025 OOS confirmation before any promotion.

**Honest prior (do not oversell — §12).** The literature is clear that the *directional* funding→price edge is **weak**: tail-concentrated, day-to-week horizon, decaying post-spot-ETF (Jan 2024), and partly momentum-in-disguise; the *strong* funding edge (Sharpe ~1.8–3.5, He et al.) is **delta-neutral carry**, which a single-asset directional engine **cannot express** and which is **out of scope**. A clean earned-negative is therefore the **most likely and most informative** outcome — failing an *easier* small-N\* bar (N\*=3) is *more* conclusive (the §8 small-N\* asymmetry, inherited from Path B). There is no A outcome we regret running.

---

## 2. Scope

**In scope (this cycle = scoping artifacts ONLY):** (1) this design spec; (2) the Step −1 pre-registration LOCK (§7); (3) the implementation plan (`superpowers:writing-plans`). **This cycle touches no funding data and writes no harness code.**

**In scope of the design pinned here (executed at downstream registers):** (a) a funding-rate ingestion pipeline (Binance Vision bulk + CCXT incremental) producing a new raw parquet + schema; (b) a funding-feature pipeline (3 funding factors computed on the 8h settlement series, causally carried onto 1h bars); (c) three pre-registered funding mechanism-first hypotheses (H1/H2/H3, §3); (d) cost-aware evaluation + hypothesis-class floors + DSR-FWER at N\*=3; (e) reuse of the Path B verdict harness (`pathb_* → patha_*`).

**Out of scope (non-goals):**
- ❌ Open interest, perp-spot basis, liquidations (other crypto-native families — funding-only this cycle, Q1; each a separate future register).
- ❌ Short legs (Q5: long/flat only; short-H1 deferred to a separate register).
- ❌ 2-factor / funding-scaled position sizing (single-factor vol-CDF sizing only; mirrors Path B; deferred).
- ❌ Cross-sectional / multi-asset structure (deferred).
- ❌ Delta-neutral funding-carry harvest (long-spot/short-perp) — not expressible in the single-asset directional engine and explicitly **not** a Path A mechanism (§12 guard).
- ❌ Any change to the promotion-gate math or the 15 bps anchor; the only sanctioned gate action is reusing the Path B N\*=3 DSR-FWER plumbing for Path A's own new cohort. Sealed `tier6_dsr_v1` artifacts stay byte-identical.
- ❌ Any ingestion/build/run execution this cycle (Q4).

---

## 3. The three pre-registered hypotheses

All **long/flat**, ternary `{0, 0.5, 1.0}` sizing on `cdf_realized_vol_720` (the Path-B single-factor vol-CDF sizing, reused). Funding factors are evaluated **only at 8h settlement prints** and **carried forward** onto 1h bars (discrete-settlement carry — NOT interpolation; §5). Funding never sets position *size* (single-factor sizing); it sets the long ON/OFF *gate* or the entry trigger. Parameters are fixed a priori from the mechanism and the funding-trading literature, locked at Step −1, with **no train tuning and no post-hoc sweep**.

Diversity is honest: the three span funding's three documented, mutually-distinct directional readings (extremity-reversal / regime-gate / moderate-persistence-continuation), encoding the documented **sign-flip** between moderate funding (continuation, H3) and extreme funding (reversal, H1) — H1 and H3 fire on **non-overlapping** funding populations by construction. They deliberately mirror the Path B H1-fade / H2-regime / H3-trend triad so the funding-axis result is directly comparable to the OHLCV-axis result on identical archetypes.

### H1 — `funding_extreme_fade` (crowded-long reversal; long-biased de-risk overlay)
- **Mechanism:** an extreme positive 8h funding rate proxies crowded, over-leveraged long positioning whose forced-liquidation fragility skews forward returns negative (long-squeeze / crash). We fade the crowded long *defensively* (long/flat: go flat, do not short).
- **STRUCTURE NOTE (B2 Finding 1) — H1 is a long-biased de-risk OVERLAY, not a sparse event strategy.** Under long/flat (Q5), H1 is **long on the complement** of the rare extreme-funding tail (≈90%+ of bars) and goes **flat** only during the rare positive-funding extremity. Its *funding signal* (the defensive flat-exit) fires rarely; its *exposure* is near-always-long. Consequence: H1's forward Sharpe is **partly buy-and-hold-dominated**, and its edge claim is precisely "do the funding-driven defensive flat-exits add Sharpe over an always-long baseline?" — an overlay test. This is **asymmetric with Path B's H1** (`intrabar_push_fade`, a genuinely sparse event-class strategy, long-on-events). Funding's marginal contribution here must be read via the §9 funding-marginal-contribution diagnostic, NOT the raw Sharpe. The eligibility floor for H1 therefore keys on the **count of defensive flat-exit episodes** (the funding-signal firings on train), not on long-bar occupancy (§9).
- **Funding factor(s):** `funding_pct_rank` (causal rolling percentile of the settled funding rate over a pre-registered settlement-window) + `funding_sign`.
- **Signal:** **flat** when `funding_pct_rank ≥ θ_fund_hi` (pre-registered ~0.90) AND `funding_sign > 0` (positive-funding crowded-long side only — respects the documented positive-side asymmetry); **long** otherwise (the complement). Time exit `max_hold_bars = H1_hold` (pre-registered, mirroring the slow day-to-week reversal horizon).
- **Sizing:** vol-regime ternary on `cdf_realized_vol_720`.
- **Directional hypothesis (pre-registered sign):** extreme-positive-funding bars have conditional forward return **< 0**.
- **Kill (pre-registered):** train-only — partition bars by `funding_pct_rank ≥ θ_fund_hi AND funding_sign > 0`; if the conditional mean forward return over the sanity horizon (§9) is **not negative**, the reversal mechanism is refuted (we do NOT flip to "buy high funding"). *(Mirror of `pathb_perleg` sign test; sane sign is NEGATIVE here.)*
- **Path B analog:** H1 `intrabar_push_fade` — swaps microstructure down-push for funding-extremity as the over-extension proxy; same fade archetype, same vol-CDF ternary sizing, same short `max_hold`.

### H2 — `funding_sign_regime_switch` (regime-gate on a price-trend book; state-class)
- **Mechanism (B2 Finding 3 — positioning framing, zero carry-think):** the carried funding sign/level is a *positioning* state variable summarizing which side is crowded; it is used purely to GATE a directional price-trend book — permit price-trend longs in the non-crowded/favorable funding regime, de-risk to flat in the crowded/stressed regime (avoiding the over-crowded side into a cascade). Funding is the gate; the price-trend confirm is the directional leg (resolving the "funding is not a clean 1h trigger" constraint). The mechanism is tested purely as **conditional separation of forward returns by funding regime** (§3 kill); it makes NO funding-accrual / carry claim.
- **Funding factor(s):** `funding_sign` + `funding_ewm` (causal EWM of the settled rate, pre-registered span; defines the regime band via its own causal percentile to be robust to post-ETF level drift).
- **Signal (two OR-connected regime groups, mirroring Path B H2's two-group structure):** PERMISSIVE (long-enabled) — `funding_ewm` in the favorable band AND price-trend confirm (`decay_linear_close_48 > decay_linear_close_168`, reused from Path B) → long. DE-RISK — `funding_ewm` in the crowded/stressed band → **flat**, regardless of price trend.
- **Exit:** switch to flat on entering the de-risk regime, OR price-trend roll-over (`48 < 168`), OR `max_hold_bars = H2_hold` (≈ Path B H2's 24-bar).
- **Sizing:** long/flat ternary on `cdf_realized_vol_720`.
- **Directional hypothesis (pre-registered sign):** conditional mean forward return of price-trend-longs is **higher** in the permissive regime than the de-risk regime, AND positive in the permissive regime.
- **Kill (pre-registered):** train-only — compute conditional mean forward return for price-trend-long bars **split by funding regime**; SANE iff `(permissive mean) > (de-risk mean)` AND `permissive mean > 0`. REFUTED if the funding split adds no separation (gate inert → funding contributes nothing beyond OHLCV).
- **Path B analog:** H2 `vol_regime_switch` — swaps the vol-CDF regime axis for a funding-sign/level regime axis; same two-OR-group structure, same single-factor vol-CDF ternary sizing, same ≈24-bar time-stop.

### H3 — `funding_momentum_continuation` (moderate-persistence trend confirm; state-class)
- **Mechanism:** persistent *moderate* positive funding reflects ongoing capital-efficient leveraged long demand that can sustain an established uptrend for weeks, so rising/steady funding short of the reversal extreme confirms trend continuation.
- **Funding factor(s):** `funding_ewm` (causal EWM, pre-registered span — the persistence proxy) + `funding_pct_rank` (the UPPER guard excluding the reversal-extreme tail).
- **Signal:** **long** when `funding_ewm > 0` (persistent positive leverage demand) AND `funding_pct_rank ≤ θ_fund_hi` (NOT in H1's reversal tail — the explicit exclusion preventing H1/H3 collision) AND price-trend confirm (`decay_linear_close_48 > decay_linear_close_168`); flat otherwise.
- **Exit:** `funding_ewm ≤ 0` (demand fades) OR price-trend roll-over OR `funding_pct_rank` crossing into the reversal tail (`> θ_fund_hi`) OR `max_hold_bars = H3_hold` (≈ Path B H3's longer hold).
- **Sizing:** long/flat ternary on `cdf_realized_vol_720`.
- **Directional hypothesis (pre-registered sign):** moderate-persistent-positive-funding + uptrend bars have conditional forward return **> 0** (continuation).
- **Kill (pre-registered):** train-only — partition bars by `funding_ewm > 0 AND funding_pct_rank ≤ θ_fund_hi AND price-trend-up`; SANE iff conditional mean forward return over the sanity horizon is **positive**; REFUTED if non-positive (moderate persistent funding does not precede continuation → the continuation channel is refuted).
- **Path B analog:** H3 `decay_trend_persistence` — swaps the decay-MA cross for `funding_ewm > 0` as the persistence/leverage-demand confirm on top of a price trend; same continuation archetype, same vol-CDF ternary sizing, same longest `max_hold`.

---

## 4. Build surface

- **New ingestion (1):** a funding-rate ingestion pipeline (§5) — Binance Vision bulk + CCXT incremental → new raw parquet `data/raw/btcusdt_funding_8h.parquet` + new `config/schemas.yaml` `funding` block + validators.
- **New funding-feature pipeline (1):** funding factors computed on the **native 8h settlement series** (causal rolling over settlement units), then carried forward onto the 1h bar grid via a backward as-of join (§5). Whether this lives in a parallel funding-feature builder or an extension of `factors/build_features.py` is a **plan-stage** decision; the design intent (compute-on-8h-series → causal-carry-onto-1h) is fixed here.
- **New registered funding factors (3):** `funding_pct_rank` (causal rolling percentile), `funding_ewm` (causal EWM, `adjust=False`), `funding_sign`. Top-level named functions; rolling/causal only; must pass the inherited G1–G4 leakage guards (on `main` from Path B). Reuses Path B's `decay_linear_close_48/168` (price-trend confirm) and `cdf_realized_vol_720` (sizing) — both already registered.
- **Hypotheses (3):** H1/H2/H3 expressed in the DSL (factor-vs-scalar + factor-vs-factor + OR-groups + the ternary sizing node — all already in the DSL from Path B; **no new DSL schema** expected; confirm at plan stage).
- **Harness reuse (1):** `pathb_* → patha_*` verdict harness (holdout producer, moments, DSR-FWER N\*=3, earned-negative taxonomy, orchestrator). Reuse, do not rebuild.
- **Process (0 new):** the cost-aware objective + hypothesis-class floors are inherited unchanged from Path B.

---

## 5. Funding-data ingestion design + leakage/alignment guards (pinned; executed at a downstream register)

**Source (verified by direct Binance Vision S3 probe, 2026-05-31).**
- History: Binance Vision bulk `futures/um/monthly/fundingRate/BTCUSDT/` — confirmed starts **2020-01** (first row `calc_time = 1577836800000` = 2020-01-01T00:00:00Z), columns `calc_time` (ms epoch), `funding_interval_hours`, `last_funding_rate`. Same download→checksum→parse pattern as the existing OHLCV bulk ingest (`ingestion/bulk_download.py`).
- Incremental / forward (incl. 2026): CCXT `fetchFundingRateHistory(symbol='BTC/USDT:USDT')` or raw `GET /fapi/v1/fundingRate` (both return the same settled rate).

**New raw parquet + schema.** `data/raw/btcusdt_funding_8h.parquet`; new `config/schemas.yaml` `funding` block. Columns: `open_time_utc` (= settlement time, UTC tz-aware `datetime64[ms, UTC]`, **unique sorted PK**), `funding_rate` (= `last_funding_rate`, the settled realized rate), `funding_interval_hours`, `source` (`binance_vision` / `ccxt_binance`), `ingested_at_utc`. Reconcile archives-before-overwrite into `data/raw/archive/` (mirrors the OHLCV rule); a new `SOURCE_PRIORITY`/venue rule for the funding source. No forward-fill of *missing settlements*; gaps flagged not interpolated.

**Causal alignment (the funding-specific leakage surface — DESIGN INVARIANT).**
- Funding factors (`funding_pct_rank`, `funding_ewm`, `funding_sign`) are computed on the **8h settlement series** with rolling windows in **settlement units** (causal: bar T uses only settlements with `calc_time ≤ T`).
- The funding-feature values are then carried onto the 1h OHLCV bar grid via a **backward as-of join**: each 1h bar at close-time `c` receives the funding-feature values of the **most recent settlement with `calc_time ≤ c`**. This is a discrete-settlement carry-forward, explicitly allowed (it is not price interpolation and it never reads a future settlement). It honors the project execution convention (signal at bar N close uses only data available at N's close; orders fill at N+1 open).
- `funding_interval_hours` is read per row (do **not** hardcode 8h — Binance has variable intervals on some symbols/periods; BTCUSDT was 8h over the historical window but this is verified per-row, not assumed).
- A dedicated causality guard (mirroring Path B's G2 sentinel) asserts the carried funding feature at bar N is bit-identical when settlements after N are deleted/reversed/shuffled.

**Known data characteristics to document before train (not auto-cleaned).** The FTX-era break (Nov 2022); the post-spot-ETF funding-level drift (Jan 2024, the §12 decay temper); any settlement gaps. These are flagged in the validation report, never interpolated.

The inherited Path B leakage guards (G1 AST-scanner, G2 future-bar-invariance sentinel, G3 per-operator known-value + ternary causality, G4 registry-sync) are on `main` and apply unchanged to the new funding factors. Path-A adds only the funding **carry-forward** causality guard above.

---

## 6. Cycle sequence (this cycle = Step −1 design artifacts; Steps 0+ are downstream registers)

- **THIS CYCLE (scoping):** this design spec → **Step −1 pre-registration LOCK** (§7; a Charlie register-event, committed BEFORE any funding data is ingested or peeked — the anti-hindsight commit-order) → implementation plan (`superpowers:writing-plans`).
- **Downstream register A — ingestion.** Build the funding ingestion + funding-feature pipeline (§5); ingest + validate the funding parquet. **First data touch — only after the Step −1 LOCK freezes the hypotheses.**
- **Downstream register B — build.** `patha_*` factors + DSL hypotheses + harness reuse, TDD + B2 (Codex on the grounded implementation + advisor on LOCK/spec conformance).
- **Downstream register C — run.** Train-only mechanism-sanity table → walk-forward train (2020-21+2023, `check_wf_semantics_or_raise`) → forward_2026 Tier-5 single-run holdout (`check_evaluation_semantics_or_raise`, `holdout_sharpe > 0` at 15 bps) → DSR-FWER N\*=3 → earned-negative taxonomy → A-result advisory → Charlie's binding read. 2025 touched once only for a `b_positive` confirmation.

Each downstream register is a **separate Charlie register-event**; this cycle authorizes none of them.

---

## 7. The pre-registrations (to be LOCKED at Step −1, before any funding peek)

The Step −1 LOCK doc (`2026-05-31-patha-step-minus-1-preregistration-lock.md`, written + committed as its own register-event) will freeze:

1. **Hypotheses + variant grid → N\*.** The exact 3 funding hypotheses (§3) and their single pre-registered variants. **N\* = 3** = the full considered inferential family. Adding any variant after a Step-0/run peek **voids N\*** and the cycle's integrity. Includes the exact a-priori values: `θ_fund_hi` (≈0.90 percentile), the `funding_pct_rank` window, the `funding_ewm` spans (H2/H3), the H2 regime-band edges (as causal percentiles), `H1_hold`/`H2_hold`/`H3_hold`.
2. **Gate pre-commit.** 15 bps anchor + DSR-FWER (Form B authoritative) at N\*=3 + Tier-5 `holdout_sharpe > 0` (strict) on **forward_2026**. Locked, never revisited post-result.
3. **Process-delta pre-spec.** Cost-aware (net-of-15bps) objective; hypothesis-class floors (**H1 event-class ≥200 entry events on train**; **H2/H3 state-class `zero_fraction < 0.50` AND ≥200 trades on train**; deployment-readiness target ≥1000 trades); single-factor vol-CDF ternary sizing; the causal funding carry-forward rule (§5).
4. **Kill-criterion taxonomy + escalation** (§9), inheriting the §9-amended significance prong.

---

## 8. Multiplicity, the gate, and the small-N\* asymmetry (inherited)

The Path B N\*=3 DSR-FWER plumbing (`backtest/tier6_dsr.py` + `backtest/pathb_dsr_fwer.py`, Form B authoritative, `Z_PASS = 1.644853626951472` frozen, `expected_max_ratio_form_b(3)`) is **reused** for Path A's own new cohort; the sealed `tier6_dsr_v1` artifacts stay **byte-untouched** (re-verify sha256 before AND after, per the sealed-artifact invariant; `tier6_bootstrap.py` embeds a fingerprint that aborts on change).

**Small-N\* asymmetry (inherited from Path B §8).** N\*=3 is much smaller than the sealed 18, so the bar (`sr_star`) is *lower*. Consequence: an **A-negative is MORE conclusive** (a variant failed even an *easier* bar — exactly the §8 argument that made Path B's negative more conclusive than a positive would have been), and an **A-positive is LESS conclusive** (cleared an easier bar) → an A-positive requires **2025 OOS confirmation** before any promotion. N\* prices only the post-hoc family of the 3 pre-registered variants, not an upstream search funnel — mechanism-first narrowness keeps this gap minimal.

---

## 9. Pre-registration values + earned-negative taxonomy (drafted; confirmed at Step −1)

- **Hypothesis-class floors.** *H1 (long-biased overlay, B2 Finding 1):* the floor keys on the **count of defensive flat-exit episodes** (funding-signal firings) on train — NOT long-bar occupancy (H1 is near-always-long, so an occupancy floor would pass trivially and measure nothing); ≥200 such episodes on train. *State-class (H2/H3):* `zero_fraction < 0.50` AND ≥200 trades on train. Deployment-readiness target ≥1000 trades. **Floors are checked on the TRAIN window** (where leakage-guard is tightest); forward_2026 trade counts are reported but the taxonomy keys on mechanism-sanity + Tier-5 `holdout_sharpe > 0` (this is a carried Path B caveat — §12).
- **Cost-aware objective.** Ranking among pre-registered variants by Sharpe net of 15 bps/side; floors applied before ranking. N\* = full grid → no post-hoc cherry-picking.
- **Mechanism-sanity horizon (DELIBERATE deviation from Path B, Charlie-kept; tiered per B2 Finding 2).** The train-only conditional-return sign tests (§3) are evaluated at **24h AND 72h** horizons, **sane iff EITHER** — because funding effects are documented at day-to-week horizons and Path B's uniform 24-bar horizon would risk a horizon-mismatch false-refute on the funding legs. (Path B used a uniform horizon; this is the one parity break, recorded as such.) **To keep the leniency auditable (B2 Finding 2):** both horizon signs are **pre-registered and reported separately**; a leg with the hypothesized sign at **both** horizons is **strong-sane**, a leg sane at **only one** is **weak-sane (floor)**. The earned-negative taxonomy records which tier each leg achieved, so a single-horizon (possibly noise) sign flip cannot *silently* manufacture mechanism-sanity and push `mechanism_refuted` → the weaker `process_refuted` (the escalation trigger). The "either" floor is retained (Charlie-kept), but a verdict resting on weak-sane-only legs is flagged as such in the advisory bundle.
- **Earned-negative taxonomy (inherited).** Three distinct outcomes:
  1. **mechanism-refuted** — no leg's conditional forward-return sign matches its hypothesized direction (H1 reversal-DOWN; H2 permissive>de-risk & permissive>0; H3 continuation-UP).
  2. **process-refuted-for-this-grid** — ≥1 leg mechanism-sane, but no variant clears Tier-5 `holdout_sharpe > 0` at 15 bps on forward_2026.
  3. **NOT "funding exhausted."** An A-negative localizes failure away from *{funding + cost-aware + trade-frequency + ternary long/flat sizing + these 3 mechanisms}* — it does **not** exonerate the funding information set (short legs, continuous/funding-scaled sizing, basis/OI cross-structure remain *untried, not falsified*). Symmetric to Path B's OHLCV-not-exonerated caveat.
- **b-positive** — ≥1 variant clears Tier-5 `holdout_sharpe > 0` (even if it fails DSR-FWER at N\*) → weak (small-N\*, §8) requiring 2025 OOS confirmation; Charlie re-evaluates (no auto-trigger, no auto-demote).
- **Funding-marginal-contribution diagnostic (fenced, diagnostic-only — NEW per B2 Finding 4).** H2/H3 pair funding with Path B's *already-refuted* decay-MA price-trend leg (Path B H3 `decay_trend_persistence` = −2.61 on forward_2026), and H1 is a long-biased overlay on a near-always-long base. So a raw negative Sharpe cannot by itself be attributed to *funding*. A pre-registered comparison — the funding-gated strategy **vs the identical price-trend / always-long baseline WITHOUT the funding gate**, on the same bars — is computed and reported, so any A-result is attributable to funding's marginal contribution (gate adds / subtracts) rather than the known-dead price leg (H2/H3) or buy-and-hold (H1). This is **diagnostic-only, NOT promotion-affecting, NOT counted in N\*** (mirrors Path B's C11 holdout-reuse fence). Without it, §9 taxonomy point (3)'s "localizes failure away from {funding + ...}" does **not** hold for H2/H3, whose failure would already be localized to the dead price leg.
- **Escalation prong (inherited §9 amendment).** Any "a real edge exists" determination is gated by DSR-**significance** (`pass_B` / PSR ≥ 0.95), **not** a point-estimate (`excess > 0`). The binding taxonomy verdict and any next-axis escalation are a **Charlie register-event** — never an automated fire.

---

## 10. Anti-pre-emption

- This cycle scopes **funding-rate only** (Q1). Open interest, perp-spot basis, liquidations, short legs, and continuous/funding-scaled sizing are each a **separate, future, conditional register** — direction noted, none scoped or pre-named here.
- A short-leg H1 variant is registered *in direction only* (Q5) — built only if H1 long/flat passes train sanity but fails forward as merely-defensive, and only at its own register.
- No methodology successor (Romano-Wolf / Westfall-Young / SD-E-γ) is pre-named; all remain deferred per the binding-constraint thesis.
- Reviewer / research convergence is advisory; only Charlie-register authorizes fires (ingestion, build, run, commits beyond this spec).

---

## 11. Test plan (executed at the downstream build register; pinned here)

- **Ingestion:** funding bulk parse (Binance Vision CSV schema); UTC PK uniqueness + sort; `funding_interval_hours` read per-row; archive-before-overwrite; validator extension for the `funding` schema; gap/break flagging (FTX Nov-2022, post-ETF Jan-2024).
- **Funding factors:** each new factor — null policy, declared warmup, causality, known-value; rolling/causal AST scan (G1); future-bar-invariance sentinel (G2).
- **Carry-forward alignment:** backward as-of join correctness (bar N gets the latest settlement ≤ N close); dedicated causality guard (delete/reverse/shuffle future settlements → bit-identical); no-future-settlement-read assertion.
- **Hypotheses:** each compiled-through-engine; `set_coc/coo(False)`; signal at N close fills at N+1 open; long/flat ternary sizing emits the `{0,0.5,1.0}` ladder; H1/H3 non-overlapping-population assertion (`pct_rank` tail exclusivity).
- **Verdict harness (`patha_*`):** forward_2026 single-run holdout producer; CandidateMoments constructor + integrity gate; DSR-FWER N\*=3 (reuse, `pass_B` keyed on `holdout_sharpe`); earned-negative taxonomy with the tiered 24h+72h sanity horizon (strong-sane / weak-sane per leg, §9); orchestrator end-to-end; **sealed `tier6_dsr_v1` sha256 4/4 unchanged before AND after.**
- **Funding-marginal diagnostic (fenced, §9 Finding 4):** funding-gated strategy vs the no-funding price-trend/always-long baseline on identical bars — computed + reported, asserted **diagnostic-only** (not promotion-affecting, not in N\*).
- Full suite green before each register/seal boundary (current baseline 2718 passed / 8 skipped / 2 xfailed; pc9 2602).

---

## 12. Risks & open questions

- **The directional funding edge is weakly evidenced (headline risk).** Tail-concentrated, day-to-week horizon, partly momentum-in-disguise; the strong funding edge is delta-neutral carry (out of scope). A clean earned-negative is the most likely outcome. Do not oversell any mechanism.
- **Delta-neutral-carry framing trap (DESIGN GUARD).** No mechanism may be justified by funding-accrual economics (8h funding ~1 bp typical, 5–20 bps extreme — below the 30 bps round trip). H1/H2/H3 are directional spot-price bets that *use* funding as a state variable; none collects the spread. H1 is most at risk of accidental carry-think and must be justified only by the price move.
- **Funding-axis-specific decay temper (NEW caveat, beyond Path B's 4).** The spot-ETF launch (Jan 2024) cut carry materially as arbitrage capital entered — train-window (2020-21+2023) funding effects likely **overstate** forward_2026 magnitudes. This is a structural reason train-sanity can pass while forward_2026 fails, and is funding-specific (worse than the OHLCV case).
- **Carried Path B caveats (all still apply).** (1) single-factor (vol-CDF) sizing — funding never scales size, only gates; funding-scaled sizing untried. (2) regime-flip-only-exit / whipsaw — H2 can whipsaw if `funding_ewm` oscillates around its band; time-stops mitigate. (3) sanity-horizon — *partially addressed* here via 24h+72h (tiered per §9). (4) floors-on-train-not-forward — H1's *defensive flat-exit events* are tail-rare (so its event floor is the binding eligibility risk; B2 Finding 1 corrected the earlier mis-statement that H1 "fires only in the tail" — H1 is near-always-LONG, the funding *signal* is what's tail-rare). H1's forward Sharpe is partly buy-and-hold-dominated, so its result must be read via the §9 funding-marginal diagnostic, not the raw Sharpe; few defensive-exit episodes in the 105-day forward window mean a near-certain low-attribution / INDETERMINATE H1 (the §8 small-N pattern). (5) funding-not-exonerated (symmetric to OHLCV-not-exonerated).
- **Multicollinearity.** Funding is endogenous to recent returns/momentum; H2/H3 pair funding with a price-trend confirm, so the price leg can carry the edge while funding adds DoF. The conditional-separation sanity kills (§3) are designed to catch exactly this (gate-inert → refuted), but the temper remains.
- **Weakest mechanism: H3 (continuation)** — its only quantitative anchor (He et al. R²>50%) says funding is largely a momentum *reflection*, so H3 risks being a price-trend strategy wearing a funding mask; its conditional-separation kill is the critical discriminator and is the most likely to fire refuted.
- **No-peek discipline.** The pre-registration is theory-driven only. No 2026 funding observation (e.g. a news headline about early-2026 negative funding) may touch the design — that would be a forward_2026 peek voiding the cycle.
- **Open (review-gate / Step −1 lock):** the exact `funding_pct_rank` window + `funding_ewm` spans + `θ_fund_hi` percentile + H2 regime-band percentile edges + `H_hold` values — all locked a priori at Step −1, no train tuning. The price-confirm factor is **committed** to Path B's reused decay-MA cross (`decay_linear_close_48 > decay_linear_close_168`, §3) to minimize DoF and keep the funding-vs-OHLCV marginal-contribution test clean.

---

## 13. Verified anchors (this cycle)

- Binance Vision S3 probe (2026-05-31): `futures/um/monthly/fundingRate/BTCUSDT/` starts 2020-01 (cols `calc_time`/`funding_interval_hours`/`last_funding_rate`; ~94 rows Jan-2020 = 3/day, interval 8h). **INDEPENDENTLY RE-VERIFIED at B2 (2026-05-31) via direct S3 listing: 76 monthly funding files, earliest `BTCUSDT-fundingRate-2020-01.zip`, through ~2026-04 — confirms the load-bearing 2020-01 start matching the OHLCV start.** No `liquidationSnapshot` type in Vision; OI `metrics` starts 2020-09; `premiumIndexKlines`+`markPriceKlines` 1h start 2020-01.
- Path B verdict: `data/phase2c_evaluation_gate/pathb_verdict_v1/pathb_verdict_advisory.json` — H1/H2/H3 net Sharpe −8.42/−2.65/−2.61; `survivors: []`; `process_refuted_for_this_grid`; `approximation_tempers` 3-item.
- Repo infra (grep-verified): `ingestion/bulk_download.py`, `ingestion/incremental_update.py`, `ingestion/reconcile.py` (archive `:63-87`), `ingestion/validators.py`, `config/schemas.yaml` OHLCV block, `factors/registry.py` (G1 `:97`, feature_version `:377-463`), `factors/build_features.py`, `backtest/bt_parquet_feed.py`. No funding/OI/basis/liquidation ingestion currently exists.
- Discipline: `config/execution_phaseb_spot_15bps.yaml` (15 bps); `config/environments.yaml` forward_2026 `[2026-01-01, T_end]`; `backtest/tier6_dsr.py` Form B + `Z_PASS`; `backtest/wf_lineage.py` `check_evaluation_semantics_or_raise` (`single_run_holdout_v1`); CLAUDE.md HARD CONSTRAINTS (Data Integrity, Conservative-Anchor Gate Tier 5/6, DSR-FWER not BH-FDR); METHODOLOGY_NOTES §36 (significance-not-point-estimate; amendment discipline; realistic fixtures).
- Funding-trading literature (research-agent citations, to be independently re-verified at the B2 before the LOCK; flagged where uncertain): Schmeling/Schrimpf/Todorov BIS WP 1087 "Crypto Carry" (high carry forecasts crashes; ETF DiD cut carry ~36%); He/Manela/Ross/von Wachter arXiv 2212.06888 (delta-neutral carry Sharpe ~1.8–3.5 — OUT OF SCOPE; momentum R²>50%); Liu/Tsyvinski RFS 2021 (TS momentum + attention); Chi et al. JFM 2023 (basis strongest cross-sectional predictor). Practitioner directional claims (win-rate figures) are UNVERIFIED marketing — not load-bearing.

---

## 14. Terminal state

On written-spec review-gate approval + 2-leg B2: write + commit the Step −1 pre-registration LOCK (`2026-05-31-patha-step-minus-1-preregistration-lock.md`) as its own Charlie register-event, then invoke `superpowers:writing-plans` to turn this spec into a step-by-step implementation plan (ingestion → build → run). Ingestion / build / run each remain a separate downstream Charlie register; this cycle authorizes none of them.
