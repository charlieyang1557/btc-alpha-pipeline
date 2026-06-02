# Path D — Open Interest Axis Mechanism-First Mine (Alpha-Source Rethink, Cycle 4) — Design Spec

**Date:** 2026-06-01 (UTC)
**Version:** v1 (reconciliation 2-leg-B2'd — Codex *SOUND-WITH-CAVEATS* + advisor *ADOPT-WITH-CHANGES*; **written-spec 2-leg-B2'd 2026-06-01 — Codex *APPROVE-WITH-CHANGES* + advisor *COMMIT-WITH-CHANGES*, all findings folded**: H2 nested regime factor `oi_velocity_ewm_240_pctrank_2160` pinned, §38.3-guard scoped for the D1-only cycle, contamination-correlation window default added, §1 contracts-not-notional wording. All six registered decisions approved in-chat by Charlie 2026-06-01).
**Status:** Written-spec 2-leg-B2 complete (both legs approve-with-changes; all folded); Charlie-authorized to commit this spec doc. NOT yet authorized for the Step −1 LOCK register, for any ingestion/build/run, or for anything beyond this spec doc itself.
**Cycle class:** Bounded, pre-committed, **one-cycle** falsification test of the **open-interest (OI)** positioning axis — the genuinely **INDEPENDENT** crypto-native member (a *positioning/participation* signal, NOT a price-derived signal and NOT the funding/basis premium that Path A/C tested). The Charlie-**authorized** escalation successor to Path C (basis earned-negative, 2026-06-01), opened as a **fresh, separately-registered scoping cycle** (anti-pre-emption WITHIN the authorization: *authorized-to-scope ≠ mechanisms/N\*/hypotheses pre-decided*).
**Predecessors (all `process_refuted_for_this_grid`, earned-negative):**
- Path B mechanism-first OHLCV re-mine — H1/H2/H3 net Sharpe −8.42 / −2.65 / −2.61 on forward_2026; 0/3 Tier-5; 0 DSR pass. Verdict `data/phase2c_evaluation_gate/pathb_verdict_v1/`.
- Path A funding-rate axis mine — H1 −1.77 / H2 −2.98 / H3 −1.62; 0/3 Tier-5; H1 train-refuted, H2/H3 strong-sane. Spec [`2026-05-31-path-a-funding-scoping-design.md`](2026-05-31-path-a-funding-scoping-design.md); verdict `…/patha_verdict_v1/`.
- Path C perp-spot basis axis mine — H1 `basis_extreme_fade` −0.87 / H2 `basis_regime_gate` −2.83 / H3 `basis_momentum_continuation` 0.0 (degenerate, 0 trades); 0/3 Tier-5; dual-orthogonalization H2 VACUOUS, H1/H3 `basis_adds_signal` = artifacts. Spec [`2026-05-31-path-c-basis-scoping-design.md`](2026-05-31-path-c-basis-scoping-design.md); LOCK [`2026-05-31-pathc-step-minus-1-preregistration-lock.md`](2026-05-31-pathc-step-minus-1-preregistration-lock.md); verdict `…/pathc_verdict_v1/`.

The alpha-source-binding hypothesis is now **thrice-earned on *correlated* axes**: OHLCV (Path B), funding (Path A), and the funding/basis premium at 1h (Path C — basis ≈ funding by construction). **OI is the first genuinely *independent* axis tested.**

**Cost anchor:** `spot_realistic_15bps_v1` — 15 bps/side, 30 bps round trip (`config/execution_phaseb_spot_15bps.yaml`). HARD CONSTRAINT; not relaxed anywhere in this cycle.

---

## 0.1 Registered decisions (provenance)

Each surfaced as plain-text options + intuitive Chinese and explicitly registered by Charlie 2026-06-01 (reviewer/research convergence was advisory only):

| Decision | Registered outcome |
|---|---|
| Escalation authorization | **OI is AUTHORIZED (warranted→authorized) as the next axis** (Charlie 2026-06-01), as a *fresh* scoping cycle replicating Path C's gate sequence. Authorized-to-scope ≠ pre-decided mechanisms. |
| Q1 — data family | **Open interest only** (single crypto-native family this cycle; the genuinely-independent member, NOT combined with funding/basis — the "OI + premium multi-signal" composite was rejected as a one-family-discipline violation). |
| Q1b — directionality (OI is directionless) | **Refined Option A.** Direction is 100% the inherited price-trend cross; OI **never originates a sign**. OI enters as exactly **one removable boolean gate** `oi_ok`, AND-composed with the price-long. OI's "best directional shot" is bought at the *mechanism of `oi_ok`* (velocity firewall + the H3 new-flow graft, §3), NOT at the sign level — preserving clean D1 attribution. (See §3; the reconciliation was produced by an adversarial design workflow + 2-leg B2.) |
| Reconciliation A1 — D2 diagnostic | **DROP D2 entirely; D1-only orthogonalization.** Path C's D2 (vs-funding) was a *derived-from redundancy* test (basis ≈ funding); for an *independent* axis there is no derived-from relation, so the motivation evaporates. D1 (vs-momentum) already carries the attribution; minimal-latitude argues against retrofitting an idle socket. The `basis_marginal_d2` / `redundancy_read` machinery is **NOT** repurposed for Path D. |
| Reconciliation B2 — firewall residual | **Disclose + a small FENCED reported-correlation diagnostic.** State the vol/liquidation-cascade contamination plainly (the velocity firewall reduces *level/momentum* endogeneity but leaves *vol/liquidation* endogeneity that D1 cannot catch), AND pre-register a fenced, measured-&-reported-only correlation set (`oi_velocity` vs `{return_1h, abs(return_1h), realized_vol_24h, cdf_realized_vol_720}`) — never a control, never promotion-affecting — to quantify the disclosure at verdict time. |
| Q2 — structural frame | **(b) Strict Path-A/C parallel + the §37.3 denser-trading delta, AS FEASIBLY APPLIED** — reuse the entire frame, swapping only data family (OI) + 3 mechanisms + baselines. **NOT "clear the floors by construction"** (Path C B2 Finding 1, inherited): the inherited price-trend AND-confirm binds occupancy; band design cannot clear the `zero_fraction` floor. Heightened under-power this cycle (the 2020-09 OI-start shorter train, §1/§12) → H2/H3 (and possibly all three) pre-registered as expected-INDETERMINATE. |
| Q4 — N\* | **N\* = 3** (three OI mechanisms, one pre-registered variant each, no parameter sweep). |
| Q5 — Tier-5 gate window | **forward_2026** (2528 bars), 15 bps spot anchor (strict `holdout_sharpe > 0`) — the same OOS slice Path B/A/C and the dead-18 were gated on (apples-to-apples across all four cycles). |
| Q6 — sizing / shorts | **All three long/flat** (no shorts); single-factor vol-CDF ternary sizing on `cdf_realized_vol_720`. OI never sets position size. |
| Mechanical proposals | All §3 mechanics (OI series choice, velocity-firewall, factor windows, `θ_oi_hi` rule, H2 band edges, max-holds) are **PROPOSED here, frozen at Step −1 LOCK** with Charlie's per-parameter register (anti-pre-emption tone, advisor flag). |
| Successor direction-note | **Direction-noted only, none scoped/authorized:** liquidations, cross-sectional/multi-asset rank structure, short legs, OI-scaled sizing. Each a separate future conditional register (anti-pre-emption, §10). The post-Path-D strategic fork (cross-sectional pivot vs equities/options) is recorded in project memory and deferred to a dedicated future session. |

---

## 1. Motivation & frame

**Binding constraint = the alpha source / hypothesis-space** (reviewer-convergent, Charlie-registered; memory `alpha-source-is-the-binding-constraint-not-data-methodology`). Path B held the **data** fixed (OHLCV) and varied **only the process** → earned negative. Path A varied the **data axis** (+ funding) → earned negative. Path C varied to **basis** (≈ funding by construction) → earned negative, tightening the localization to *"the funding/basis premium adds no rescue at either its 8h or 1h frequency."* Path D tests the **first genuinely independent member** of the broader positioning family.

**Why OI is the right Cycle-4 axis — and what makes it structurally different.** Path B (OHLCV), Path A (funding), and Path C (basis) all tested **price-derived or funding-equivalent** signals. **Open interest is structurally different: a *positioning/participation* signal** — the total contracts outstanding (notional value stored only as a cross-check), i.e. "how much leverage is currently in the market" — **not a price-derived premium.** A clean negative here is the **most informative** single result in the series so far: it would graduate the binding-constraint thesis from "thrice-earned on *correlated* axes" to **"earned across an *independent* axis."**

**The load-bearing structural fact: OI is *directionless*.** Funding and basis are **signed** premium signals (positive = leveraged longs paying / perp premium = the long side is crowded), so they can lean a directional book by themselves. **OI is an unsigned magnitude** — it tells you *how many* contracts are open, not *which side* is crowded. Consequently an OI mechanism cannot originate a long/flat direction; it can only (a) **gate** an already-directional price-trend book, or (b) be **paired with price**. This cycle takes the disciplined path: **OI is exclusively a removable gate `oi_ok` on the inherited price-trend long/flat book** (§3); direction is 100% the price cross. The "directional shot" is granted only through *which OI quantity* gates and *how* (the velocity firewall + the H3 new-flow graft), all pre-registered — never through OI inventing a sign.

**Calibrated prior (registered 2026-06-01):**
- **D-negative (most likely)** → the OI positioning axis adds no directional rescue to a single-asset long/flat price-trend book under this process/grid → extends the localization from the *premium* family (funding/basis) to the **independent positioning member**. **Calibration:** this is still **NOT** "the whole positioning family fails" — OI is *one* independent member; **liquidations, cross-sectional/multi-asset rank structure, short legs, and OI-scaled sizing remain untried, not falsified.** A family-level claim would require those too.
- **D-positive (low prior)** → an OI gate carries directional rescue the price book lacks → a genuine, small-N\* finding requiring 2025 OOS confirmation **and** surviving the D1 attribution + the fenced contamination-correlation disclosure (§9) before any promotion. Even then, it would **not** be cleanly attributable to OI-information vs a vol/liquidation filter at the diagnostic level (§9, §12).

**Honest prior (do not oversell — §12).** The literature's *strong* OI/positioning evidence is **cross-sectional** (Chi et al. JFM 2023: basis/positioning factors predict *cross-sectional* differences), which a single-asset directional long/flat engine **cannot express** — the same gap that capped funding and basis. The single-asset *time-series* OI→price directional signal is weakly evidenced (folklore-grade taxonomy, no peer-reviewed single-asset directional result), **momentum-endogenous** (OI is partly caused by recent price moves), and additionally confounded by **vol/liquidation cascades** (§12). A clean earned-negative is the **most likely and most informative** outcome (failing an *easier* small-N\*=3 bar is *more* conclusive — the §8 small-N\* asymmetry, inherited). The acknowledged cost of the minimal-latitude design: if OI's *only* real edge is a **predictive directional divergence that leads price**, this design cannot capture it — every adversarial reviewer agreed that is the correct trade for clean interpretation. **There is no Path-D outcome we regret running.**

---

## 2. Scope

**In scope (this cycle = scoping artifacts ONLY):** (1) this design spec; (2) the Step −1 pre-registration LOCK (§7); (3) the implementation plan (`superpowers:writing-plans`). **This cycle touches no OI data and writes no harness code.**

**In scope of the design pinned here (executed at downstream registers):** (a) an OI ingestion pipeline (Binance Vision bulk `metrics`; CCXT incremental for the recent window) producing a new raw parquet + schema; (b) an OI-feature pipeline (OI factors on a causally-downsampled 1h OI series); (c) three pre-registered OI mechanism-first hypotheses (H1/H2/H3, §3); (d) cost-aware evaluation + hypothesis-class floors + DSR-FWER at N\*=3; (e) the **single-orthogonalization (D1) marginal diagnostic + the fenced contamination-correlation set** (§9); (f) reuse of the Path C/A verdict harness (`pathc_* → pathd_*`).

**Out of scope (non-goals):**
- ❌ Funding/basis composites or any multi-axis signal (one-family discipline — OI may combine only with the engine's own *price* series, never with another crypto-native axis).
- ❌ A **D2 (vs prior-axis) diagnostic** — DROPPED (decision A1); the `redundancy_read` / `basis_marginal_d2` machinery is not repurposed.
- ❌ Liquidations, cross-sectional / multi-asset rank structure (the registered direction-noted successors — separate future registers; the cross-sectional pivot is the post-Path-D strategic fork, deferred).
- ❌ Short legs (long/flat only; deferred).
- ❌ OI-scaled / 2-factor position sizing (single-factor vol-CDF sizing only; deferred).
- ❌ Any change to the promotion-gate math or the 15 bps anchor; the only sanctioned gate action is reusing the N\*=3 DSR-FWER plumbing for Path D's own new cohort. Sealed `tier6_dsr_v1` stays byte-identical.
- ❌ Any ingestion/build/run execution this cycle.

---

## 3. The three pre-registered hypotheses

All **long/flat**, ternary `{0, 0.5, 1.0}` sizing on `cdf_realized_vol_720` (reused). **Direction is 100% the inherited price-trend cross** `decay_linear_close_48 > decay_linear_close_168` (reused from Path B); **OI never originates a sign and never sets size.** OI enters as exactly **one removable boolean `oi_ok`, AND-composed** with the price-long (`long iff price_long AND oi_ok, else flat`), so the D1 baseline (`oi_ok ≡ True`) is a structurally clean single-factor subtraction (the cleanest D1 substrate in the series). Parameters are fixed a priori from mechanism + literature, **proposed here and frozen at Step −1, with no train tuning and no post-hoc sweep.**

**OI series (PROPOSED, frozen at LOCK — a load-bearing firewall choice):** the primary OI series is **`sum_open_interest` (base/coin-denominated contracts), NOT `sum_open_interest_value` (USDT notional).** Rationale: notional = contracts × price, so `Δlog(notional) = Δlog(contracts) + price_return` — a **notional velocity mechanically embeds the price return and would DEFEAT the velocity firewall.** Contract-denominated OI's log-change is the position flow without the price-return term injected. (This is the single most firewall-critical pre-registration; flagged for explicit Charlie register.)

**Cadence (PROPOSED; verified at register-A, §5):** OI's native Binance-Vision cadence (≈5-min per the `metrics` tree) is **causally downsampled to the 1h grid** (bar-close OI = the last OI observation at/before the 1h bar close — no future read), and OI factors are computed **on the 1h OI series in 1h-bar units**. Computing on the consumption grid avoids the §37.2 cross-cadence-warmup conversion bug (the funding 8h→1h hazard); it discards intra-hour OI, which is acceptable for a daily-horizon positioning signal.

**Proposed OI factors (frozen at LOCK):**
- `oi_pct_rank_2160` — causal rolling **2160-bar** (≈90d) percentile of the OI **level**.
- `oi_velocity_ewm_240` — causal **span-240** (≈10d) EWM (`adjust=False`) of the OI **log-change** (`oi_log_change[t] = log(OI[t]) − log(OI[t−1])`) = the *flow of new positioning* (the anti-endogeneity firewall quantity).
- `oi_sign` — sign of `oi_log_change` (inflow vs outflow).
- `oi_velocity_ewm_240_pctrank_2160` — causal rolling-**2160**-bar percentile of `oi_velocity_ewm_240` (**H2's regime axis**; the nested percentile-of-velocity-EWM, mirroring Path C's `basis_ewm_240_pctrank_2160`; the outer 2160-percentile `min_periods` dominates the inner 240-EWM warmup). *(4 OI factors total.)*
- Reuses Path B's `decay_linear_close_48/168` (price-trend confirm) and `cdf_realized_vol_720` (sizing). A `log_change`/`.diff()` factor primitive may be net-new (build-register concern).

The triad mirrors Path A/C on identical archetypes (extremity-reversal / regime-gate / persistence-continuation) so the OI result is directly comparable. **Firewall asymmetry (pre-registered, advisor calibration):** H1 is **level-based → the UN-firewalled, weakest, most momentum-contaminated leg** (OI *level* is near-cointegrated with cumulative price drift); H2/H3 are **velocity-based → firewalled.** Under Path D the weakest-leg label therefore **flips from Path C's H3 to H1**.

### H1 — `oi_extreme_fade` (crowded-positioning reversal; long-biased de-risk overlay; UN-FIREWALLED weakest leg)
- **Mechanism:** an extreme-high OI *level* proxies crowded, over-leveraged positioning whose forced-liquidation fragility skews forward returns negative (de-lever / cascade). We fade the crowded book *defensively* (long/flat: go flat, do not short).
- **STRUCTURE NOTE (inherited from Path A/C H1):** a long-biased de-risk OVERLAY, long on the complement of the rare extreme-OI tail, flat only during extremity. Forward Sharpe is partly buy-and-hold-dominated; the edge claim ("do OI-driven defensive flat-exits add Sharpe over always-long?") is read via the §9 D1 diagnostic, NOT raw Sharpe. The floor keys on the **count of defensive flat-exit episodes** on train (§9).
- **OI factor(s):** `oi_pct_rank_2160` (level percentile). *(No `oi_sign` conjunct — OI is directionless; "extreme high OI level" alone defines the crowded tail, unlike Path C's signed `basis_sign > 0`.)*
- **`oi_ok` (the gate):** `oi_ok = NOT(oi_pct_rank_2160 ≥ θ_oi_hi)`. **Signal:** long iff `price_long AND oi_pct_rank_2160 < θ_oi_hi`; **flat** when `oi_pct_rank_2160 ≥ θ_oi_hi` (extreme-high OI). **NO time-stop** (inherits Path A Amendment A1 / Path C by design: a near-always-long overlay must not carry a churn-inducing `max_hold`).
- **Sizing:** vol-regime ternary on `cdf_realized_vol_720`.
- **Directional hypothesis (pre-registered sign):** extreme-high-OI-level bars have conditional forward return **< 0**.
- **Kill (pre-registered):** train-only — partition bars by `oi_pct_rank_2160 ≥ θ_oi_hi`; if the conditional mean forward return over the sanity horizon (§9) is **not negative**, the reversal mechanism is refuted (we do NOT flip to "buy high OI").
- **Honest weakness (pre-registered):** H1 is the **un-firewalled level leg** — OI level is near-cointegrated with cumulative price drift, so H1 carries the momentum-in-disguise risk the velocity firewall removes from H2/H3. H1's D1 is expected to be the **least attributable** of the three; a non-inert H1 D1 is most likely an artifact (the Path A/C H1 replay). Refutation/low-attribution is the expected, informative result.

### H2 — `oi_regime_gate` (positioning-regime gate on a price-trend book; state-class; VELOCITY-firewalled)
- **Mechanism:** the rate of new positioning (OI velocity) is a *regime* state variable — rapid OI inflation marks aggressive crowding/fragility. It GATES a directional price-trend book: permit price-trend longs in the normal/low-inflow regime, de-risk to flat in the fast-inflow (crowded) regime. **Velocity, not level, is the firewall** (level is momentum-cointegrated; velocity is the least-contaminated "fresh leverage entering" proxy). Tested purely as conditional separation of forward returns by OI-velocity regime; makes no carry/accrual claim.
- **OI factor(s):** `oi_velocity_ewm_240`, regime band defined via its own causal rolling-2160 percentile (robust to level drift).
- **Signal (two OR-connected regime groups):** PERMISSIVE — `oi_velocity_ewm_240` causal-2160-percentile `< 0.80` AND price-trend confirm (`decay_48 > decay_168`) → long. DE-RISK — percentile `≥ 0.80` (fastest-inflow / crowding regime) → **flat**, regardless of price trend.
- **Exit:** enter de-risk regime, OR price-trend roll-over (`48 ≤ 168`), OR `max_hold_bars = 24`.
- **Sizing:** long/flat ternary on `cdf_realized_vol_720`.
- **Directional hypothesis (pre-registered sign):** conditional mean forward return of price-trend-longs is **higher** in the permissive regime than the de-risk regime, AND positive in the permissive regime.
- **Kill (pre-registered):** train-only — conditional mean forward return for price-trend-long bars **split by OI-velocity regime**; SANE iff `(permissive mean) > (de-risk mean)` AND `permissive mean > 0`. REFUTED if the OI split adds no separation (gate inert → OI contributes nothing beyond price).
- **Floor / occupancy (B2 Finding 6, inherited):** `Min de-risk-cell occupancy ≥ 10% of evaluated train bars` (the 0.80 band gives ~20% by construction) so the conditional-separation kill stays powered. **H2 pre-registered as expected-INDETERMINATE on `zero_fraction`** (the price-trend AND-confirm binds occupancy; Path C Finding 1 carry). Band edge locked a priori as a causal percentile, never tuned to Sharpe.

### H3 — `oi_momentum_continuation` (new-flow trend confirm; state-class; most endogenous; VELOCITY-firewalled + the graft)
- **Mechanism:** fresh positioning *inflow* (positive OI velocity) alongside an established uptrend reflects ongoing leveraged demand that can sustain the trend → rising OI short of the reversal extreme confirms continuation. **Named "new-FLOW continuation," NOT "new-longs"** — OI velocity is **sign-agnostic about who enters** (OI rises on new shorts too); the directionality is 100% the inherited price cross, and OI velocity only types the confirm (B2 / advisor refinement).
- **OI factor(s):** `oi_velocity_ewm_240` (the flow/persistence proxy) + `oi_pct_rank_2160` (UPPER guard excluding H1's reversal-extreme tail).
- **`oi_ok` (the gate, the graft):** `oi_ok = (oi_velocity_ewm_240 > 0 AND oi_pct_rank_2160 < θ_oi_hi)`. **Signal:** long iff `price_long AND oi_velocity_ewm_240 > 0 AND oi_pct_rank_2160 < θ_oi_hi`; flat otherwise. **The graft fix (load-bearing):** the gate embeds **NO price-return conjunct** beyond the inherited decay cross — the only price leg is the D1 baseline itself — so H3's D1 marginal stays attributable to OI rather than to a smuggled second momentum filter. The strict `<` against H1's `≥ θ_oi_hi` makes H1/H3 an **exact partition** of the pct-rank axis (boundary bar `= θ` belongs to H1's tail only; Path C Codex 2e inherited).
- **Exit:** `oi_velocity_ewm_240 ≤ 0` (flow fades) OR price-trend roll-over OR `oi_pct_rank_2160 ≥ θ_oi_hi` (crosses into the reversal tail) OR `max_hold_bars = 48`.
- **Sizing:** long/flat ternary on `cdf_realized_vol_720`.
- **Directional hypothesis (pre-registered sign):** positive-OI-velocity + (not-extreme level) + uptrend bars have conditional forward return **> 0** (continuation).
- **Kill (pre-registered):** train-only — partition bars by `oi_velocity_ewm_240 > 0 AND oi_pct_rank_2160 < θ_oi_hi AND price-trend-up`; SANE iff conditional mean forward return over the sanity horizon is **positive**; REFUTED if non-positive.
- **Floor / endogeneity (pre-registered):** `zero_fraction` floor NOT clearable by band design (price-trend AND-confirm binds); **H3 pre-registered as expected-INDETERMINATE on `zero_fraction`.** H3 is the **most momentum-endogenous** of the velocity legs; the **thin-sample-SANE clause (§9)** applies with force — an under-powered-but-SANE H3 on the 2020-09-shortened train is reported *consistent-with-undetected-momentum/vol-leakage*, NOT as OI-mechanism evidence.

---

## 4. Build surface

- **New ingestion (1):** an OI ingestion pipeline (§5) — Binance Vision bulk `futures/um/.../metrics/BTCUSDT/` + CCXT incremental (recent window only) → new raw parquet `data/raw/btcusdt_oi_1h.parquet` (the causally-downsampled 1h OI) + new `config/schemas.yaml` `oi` block + validators. Reuses the funding/markprice ingestion code pattern (`ingestion/funding_*.py`, `ingestion/markprice_*.py`) — and, per §38.2, **mirrors the most defensive existing parser (header-autodetect):** Binance Vision `metrics` CSVs carry a header row.
- **New OI-feature pipeline (1):** OI factors computed on the **1h `sum_open_interest` series** (causal rolling, 1h-bar units) — the OI is downsampled to 1h at ingestion, so factors compute on the consumption grid (no cross-cadence carry, §37.2). Whether this extends `factors/build_features.py` or a parallel builder is a plan-stage decision; the design intent is fixed here. **`factors/build_features.py` must add an `oi` route** (it currently routes only `ohlcv`/`funding`/`basis` — Codex Q6).
- **New registered OI factors (4):** `oi_pct_rank_2160`, `oi_velocity_ewm_240`, `oi_velocity_ewm_240_pctrank_2160` (H2's nested regime axis — mirrors Path C's `basis_ewm_240_pctrank_2160`), `oi_sign`. Top-level named functions; rolling/causal only; pass the inherited G1–G4 leakage guards. The `factors/registry.py` `input_source` validation set (currently `{"ohlcv","funding","basis"}`, a `str` field — NOT a `Literal`) must be **widened to include `"oi"`, with the same-PR contract-widen test** (precedent: `tests/test_basis_build_routing.py`).
- **Hypotheses (3):** H1/H2/H3 in the DSL (factor-vs-scalar + factor-vs-factor + OR-groups + ternary sizing node — all already in the DSL from Path A/B/C; **no new DSL schema** expected; confirm at plan stage).
- **Harness reuse (1):** `pathc_* → pathd_*` verdict harness (holdout producer, `pathd_moments` [note: the file is `pathc_moments.py`, NOT `pathc_candidate_moments.py` — Codex], DSR-FWER N\*=3, earned-negative taxonomy, marginal diagnostic, orchestrator). Reuse, do not rebuild.
- **Diagnostic (D1-only + fenced contamination-correlations):** keep the inherited **D1 (vs-momentum)** leg (`*_marginal_d1`); **REMOVE the D2 path** for Path D (decision A1) — `basis_marginal_d2` / `redundancy_read` are not wired. **Add the fenced contamination-correlation diagnostic** (decision B2): compute & report Pearson/Spearman of `oi_velocity_ewm_240` vs `{return_1h, abs(return_1h), realized_vol_24h, cdf_realized_vol_720}` over the evaluated bars; fenced (`promotion_affecting=False, in_n_star=False`); measured-and-reported-only.
- **Process (0 new):** the cost-aware objective + hypothesis-class floors are inherited unchanged.

---

## 5. OI-data ingestion design + leakage/alignment guards (pinned; executed at a downstream register)

**Source (NOT yet independently probed this cycle — the #1 register-A verification item; §13).**
- **Bulk history:** Binance Vision `futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-YYYY-MM-DD.zip` (daily partitions; ≈5-min cadence; columns `create_time, symbol, sum_open_interest, sum_open_interest_value, …`). **History start UNVERIFIED this cycle; the in-repo prior (Path C spec §1, line 36) states OI starts 2020-09** (an 8-month gap vs the 2020-01 OHLCV/funding/basis start). **Register-A re-verifies the start, the CSV schema (header present), and quantifies the train-window shrinkage** (2020-09 lops ~8 months off the 2020-21+2023 train window — a real power handicap; §12).
- **Incremental / forward (incl. 2026):** CCXT `fetch_open_interest_history` — **but Binance's OI-history endpoint returns only ~30 days**, so CCXT is a recent-window top-up only; **Binance Vision bulk is the sole path to full 2020→2026 history.** This is a material difference from funding/basis (both had clean CCXT backfill).
- Per §38.1/§38.2: **treat the first authorized OI ingestion run as the format/availability validation gate** (expect a real-data integration bug — header drift, missing-day partitions, unit ambiguity); the header-autodetect parser is the guard.

**OI series + derivation (pre-registered — see §3).** Primary signal = **`sum_open_interest` (contracts), causally downsampled to the 1h grid** (bar-close = last 5-min OI at/before the 1h close). **NOT `sum_open_interest_value`** (notional velocity embeds the price return → defeats the firewall). `oi_log_change`, `oi_velocity_ewm_240`, `oi_pct_rank_2160`, `oi_sign` computed on the 1h OI series.

**New raw parquet + schema.** `data/raw/btcusdt_oi_1h.parquet`; new `config/schemas.yaml` `oi` block. Columns: `open_time_utc` (UTC tz-aware `datetime64[ms, UTC]`, **unique sorted PK**), `sum_open_interest` (float64, contracts), `sum_open_interest_value` (float64, USDT — stored for the cross-check/diagnostic, NOT the signal), `source` (`binance_vision` / `ccxt_binance`), `ingested_at_utc`. Reconcile archives-before-overwrite into `data/raw/archive/`. No forward-fill; gaps flagged not interpolated.

**Causal alignment (OI-specific leakage surface — DESIGN INVARIANT).**
- The downsample is **strictly causal**: the 1h bar at close-time `t` uses only the OI observation(s) at timestamps `≤ t`. Orders fill at N+1 open (project execution convention).
- OI factors computed on the 1h OI series with rolling windows in **1h-bar units** (causal: bar T uses only OI at bars ≤ T). The §37.2 warmup-unit hazard is avoided by computing on the 1h consumption grid (no source-cadence conversion); the LOCK still states warmup in 1h-bar units explicitly.
- A dedicated causality guard (mirroring Path A/C G2) asserts each OI factor at bar N is bit-identical when bars after N are deleted/reversed/shuffled.
- **Cross-stream join integrity (Path C B2 advisor Finding 6, inherited):** assert the downsampled OI 1h grid and the spot OHLCV 1h grid share identical `open_time_utc` coverage over the join window — OR an explicit inner-join with a logged dropped-bar count; a one-bar misalignment must **RAISE**, never silently pair `OI@t` with `price@t±1`.
- The inherited Path B leakage guards (G1 AST-scanner, G2 future-bar-invariance sentinel, G3 per-operator known-value + ternary causality, G4 registry-sync) apply unchanged to the new OI factors.

**Known data characteristics to document before train (not auto-cleaned).** The 2020-09 start (shorter train, §12); the FTX-era break (Nov 2022); any metrics-partition gaps; the ±ms timestamp jitter (reuse the funding/markprice validator tolerance on exact spacing). Flagged in the validation report, never interpolated.

---

## 6. Cycle sequence (this cycle = Step −1 design artifacts; Steps 0+ are downstream registers)

- **THIS CYCLE (scoping):** this design spec → **Step −1 pre-registration LOCK** (§7; a Charlie register-event, committed BEFORE any OI data is ingested or peeked — the anti-hindsight commit-order) → implementation plan (`superpowers:writing-plans`).
- **Downstream register A — ingestion.** Build the OI ingestion + OI-feature pipeline (§5); ingest + validate the OI parquet; **re-verify the 2020-09 start + CSV schema + cadence.** First data touch — only after the Step −1 LOCK freezes the hypotheses.
- **Downstream register B — build.** `pathd_*` factors + DSL hypotheses + harness reuse + D1-only diagnostic + fenced contamination-correlation set; TDD + 2-leg B2 (Codex on the grounded implementation + code-reviewer/advisor on LOCK/spec conformance, per §37.4).
- **Downstream register C — run.** Train-only mechanism-sanity table → walk-forward train (the **immutable** 2020-2021 + 2023 split, `check_wf_semantics_or_raise` — the split boundaries do NOT change; OI factors are simply NaN/un-warmed before ~2020-09 + warmup, so the OI-*informed* train is effectively shorter: the §12 handicap, not a split change) → forward_2026 Tier-5 single-run holdout (`check_evaluation_semantics_or_raise`, `holdout_sharpe > 0` at 15 bps) → DSR-FWER N\*=3 → D1 diagnostic + contamination-correlation disclosure → earned-negative taxonomy → D-result advisory → Charlie's binding read. 2025 touched once only for a `c_positive` confirmation. **A pre-fire PFR** (§38.4: trace the end-to-end gated entrypoint, not just modules) precedes the authorized run.

Each downstream register is a **separate Charlie register-event**; this cycle authorizes none of them.

---

## 7. The pre-registrations (to be LOCKED at Step −1, before any OI peek)

The Step −1 LOCK doc (`2026-06-01-pathd-step-minus-1-preregistration-lock.md`, written + committed as its own register-event) will freeze:

1. **Hypotheses + variant grid → N\*.** The exact 3 OI hypotheses (§3) and their single pre-registered variants. **N\* = 3** = the full considered inferential family. Adding any variant after a Step-0/run peek **voids N\***. Includes the exact a-priori values: the **OI series choice** (`sum_open_interest` contracts, NOT notional — the firewall-critical pre-reg); the **1h causal downsample**; `oi_pct_rank_2160` window; `oi_velocity_ewm_240` span; the nested `oi_velocity_ewm_240_pctrank_2160` (H2 regime axis); `θ_oi_hi` as a **deterministic rule** (`:= 0.90; → 0.85 if train H1 flat-exit episodes < 200`; not a judgment call; shared by H1/H3 for the exact partition); the H2 regime-band edge (`≥ 0.80` de-risk percentile + a pinned **min de-risk-cell occupancy ≥ 10%**); `max_hold` (`H2 = 24`, `H3 = 48`; **H1 has NO time-stop** — Amendment A1).
2. **Gate pre-commit.** 15 bps anchor + DSR-FWER (Form B authoritative) at N\*=3 + Tier-5 `holdout_sharpe > 0` (strict) on **forward_2026**. Locked, never revisited post-result.
3. **Process-delta pre-spec.** Cost-aware (net-of-15bps) objective; hypothesis-class floors (**H1 event-class ≥ 200 defensive-flat-exit episodes on train** — verified-not-assumed, H1-INDETERMINATE-on-floor contingency pre-registered; **H2/H3 state-class `zero_fraction < 0.50` AND ≥ 200 trades on train** — `zero_fraction` floor NOT clearable by band design → **H2/H3 pre-registered expected-INDETERMINATE**, verdict robust via §9 + §37.3 **only when the forward Sharpe is a measured loss**; deployment-readiness target ≥ 1000 trades); single-factor vol-CDF ternary sizing; the causal 1h OI downsample (§5).
4. **Diagnostic pre-spec (§9):** **D1 (vs-momentum) only** — fenced, diagnostic-only, not in N\* (D2 DROPPED, A1); the **fenced contamination-correlation set** (B2) — series, window, fence flags; the **near-zero-D1-is-modal** read (an inert `oi_ok` → `d1_marginal ≈ 0` by construction → "OI gate inert," NOT an edge); the §38.3 *fenced-label-read-against-the-gate* discipline ONLY (the `redundancy_read` vacuous-*agreement* machinery is dropped with D2 — it presupposes a D2).
5. **Kill-criterion taxonomy + escalation** (§9), inheriting the §9-amended significance prong + the **thin-sample-SANE clause** + the **under-determined carve-out** (`UNDER_DETERMINED_TRADE_THRESHOLD`).

---

## 8. Multiplicity, the gate, and the small-N\* asymmetry (inherited)

The N\*=3 DSR-FWER plumbing (`backtest/tier6_dsr.py` + the `path*_dsr_fwer.py` reuse, Form B authoritative, `Z_PASS = 1.644853626951472` frozen) is **reused** for Path D's own new cohort; the sealed `tier6_dsr_v1` artifacts stay **byte-untouched** (re-verify sha256 before AND after).

**Small-N\* asymmetry (inherited).** N\*=3 ≪ the sealed 18, so the bar (`sr_star`) is *lower*. A **D-negative is MORE conclusive** (a variant failed even an *easier* bar); a **D-positive is LESS conclusive** (cleared an easier bar) → a D-positive requires **2025 OOS confirmation** AND must survive the §9 D1 attribution + the contamination-correlation disclosure before any promotion. N\* prices only the post-hoc family of the 3 pre-registered variants.

---

## 9. Pre-registration values + earned-negative taxonomy (drafted; confirmed at Step −1)

- **Hypothesis-class floors (honest power disclosure).** *H1 (long-biased overlay):* floor keys on the **count of defensive flat-exit episodes** on train (NOT long-bar occupancy); ≥ 200 episodes — verified-not-assumed; H1-INDETERMINATE-on-floor contingency pre-registered (and, as the un-firewalled leg, a possible H1-D1-low-attribution forward read). *State-class (H2/H3):* `zero_fraction < 0.50` AND ≥ 200 trades on train — `zero_fraction` floor **NOT clearable by band design** (price-trend AND-confirm binds), so **H2/H3 pre-registered expected-INDETERMINATE**. Deployment-readiness target ≥ 1000 trades. **Floors checked on the TRAIN window**; the taxonomy keys on mechanism-sanity + Tier-5 `holdout_sharpe > 0` + §9 D1 — and **the earned-negative holds independent of floor eligibility (§37.3):** an under-floor leg with measured forward loss is a *substantive* negative, not a *vacuous* eligibility exclusion. **Heightened-under-power note (Q2 / §12):** the 2020-09-shortened train + the inherited AND-confirm could push **all three legs INDETERMINATE**, resting the verdict on §37.3's substantive-measured-loss path with thinner samples than Path C — pre-disclosed, not discovered post-hoc.
- **Thin-sample-SANE clause + under-determined carve-out (pre-registered).** §37.3's substantive-negative path is available **only when the forward Sharpe is a measured loss.** If an expected-INDETERMINATE leg instead returns a **thin-sample near-zero/positive** forward Sharpe (floor-ineligible AND `< UNDER_DETERMINED_TRADE_THRESHOLD` forward trades), it is reported **genuinely under-determined** — NOT folded into the earned-negative, surfaced to Charlie's binding read as a power gap. **OI-specific addition:** an under-powered-but-SANE H3 (the most-endogenous leg) on the short OI train is reported **consistent-with-undetected-momentum/vol-leakage, NOT as OI-mechanism evidence.**
- **Cost-aware objective.** Ranking among pre-registered variants by Sharpe net of 15 bps/side; floors applied before ranking; N\* = full grid → no post-hoc cherry-picking.
- **Mechanism-sanity horizon (inherited).** Train-only conditional-return sign tests (§3) at **24h AND 72h**, **sane iff EITHER**; both horizon signs pre-registered + reported separately; **strong-sane** = hypothesized sign at both, **weak-sane (floor)** = one. A verdict resting on weak-sane-only legs is flagged.
- **Earned-negative taxonomy (inherited).**
  1. **mechanism-refuted** — no leg's conditional forward-return sign matches its hypothesized direction.
  2. **process-refuted-for-this-grid** — ≥1 leg mechanism-sane, but no variant clears Tier-5 `holdout_sharpe > 0` at 15 bps on forward_2026.
  3. **NOT "OI exhausted."** A D-negative localizes failure away from *{OI + cost-aware + trade-frequency + ternary long/flat sizing + these 3 mechanisms}* — it does **not** exonerate the OI information set (short legs, OI-scaled sizing, cross-sectional/multi-asset structure remain *untried, not falsified*). **It extends the localization to the independent positioning member** — but is **NOT family-level** (liquidations + cross-sectional structure untried; §1 calibration).
- **d-positive** — ≥1 variant clears Tier-5 `holdout_sharpe > 0` (even if it fails DSR-FWER at N\*) → weak (small-N\*, §8) requiring 2025 OOS + surviving the §9 D1 + contamination disclosure; Charlie re-evaluates (no auto-trigger).
- **Finding D — single-orthogonalization (D1) + the contamination-correlation disclosure (fenced; diagnostic-only).**
  - **(D1) vs momentum** — the OI-gated strategy vs the identical price-trend / always-long baseline WITHOUT the OI gate, Sharpe-difference on the same bars (does the OI gate add over pure momentum?). **D1 attributes, it does NOT license:** it removes the *shared* momentum LEVEL but NOT momentum/vol re-entering through the gate's bar-*selection*. **A near-zero D1 is the *modal* expectation** on this independent axis (inert `oi_ok` → `d1_marginal ≈ 0` by construction) → read as "OI gate inert," NOT an edge. The promotion locus is **Tier-5 + DSR `pass_B`**, never D1 standalone. **§38.3 scope (D1-only, advisor B2):** with D2 dropped there is no agreement-conjunction to evaluate, so the `redundancy_read` / `d2_agrees` / `d1_noninert` truth-table machinery has NO role in Path D; the cycle inherits ONLY the §38.3 *fenced-label-read-against-the-gate* + *inert-D1-is-modal* discipline — not the vacuous-*agreement* guard (which presupposes a D2).
  - **(Contamination-correlation set, NEW, fenced — B2)** — report `corr(oi_velocity_ewm_240, {return_1h, abs(return_1h), realized_vol_24h, cdf_realized_vol_720})` over the evaluated bars (**proposed default, frozen at LOCK:** Pearson AND Spearman; computed on the forward_2026 post-warmup bars AND the train bars, reported separately; on each hypothesis's signal-active bars; NaN-dropped). Purpose: **quantify the disclosed residual** (a non-inert D1 on OI-velocity is consistent with a vol/liquidation-cascade filter that neither D1 nor any price control catches — §12). **Measured-and-reported-only; never a control; never promotion-affecting; not in N\*.** It informs Charlie's binding read; it does not gate.
  - **D2 (vs prior axis) is DROPPED** (decision A1) — no derived-from relation exists for an independent axis; the `redundancy_read` machinery is not wired.
- **Escalation prong (inherited §9 amendment).** Any "a real edge exists" determination is gated by DSR-**significance** (`pass_B` / PSR ≥ 0.95), **not** a point-estimate. The binding taxonomy verdict and any next-axis escalation are a **Charlie register-event** — never an automated fire.

---

## 10. Anti-pre-emption

- This cycle scopes **OI only** (Q1). **Liquidations, cross-sectional/multi-asset rank structure, short legs, and OI-scaled sizing are direction-noted successors** — recorded as next conditional registers, **not scoped, not pre-named in build terms, not authorized here.** The post-Path-D strategic fork (cross-sectional crypto pivot vs equities/options) is recorded in project memory and **deferred to a dedicated future session.**
- All §3 mechanics are **PROPOSED, frozen at Step −1 LOCK** with Charlie's per-parameter register — the design spec proposes; the LOCK (a separate register) freezes; reviewer convergence is advisory.
- No methodology successor (Romano-Wolf / Westfall-Young / SD-E-γ) is pre-named; all remain deferred per the binding-constraint thesis.
- Only Charlie-register authorizes fires (ingestion, build, run, commits beyond this spec).

---

## 11. Test plan (executed at the downstream build register; pinned here)

- **Ingestion:** Binance Vision `metrics` CSV parse with **header-autodetect** (§38.2 — the metrics files carry a header); ms-epoch → UTC; UTC PK uniqueness + sort; archive-before-overwrite; validator extension for the `oi` schema; the **causal 1h downsample** correctness (bar-close = last OI ≤ close; no future read); the **`sum_open_interest`-not-notional** assertion; the ≈5-min cadence + 2020-09-start + CSV-schema re-verification; gap/jitter flagging.
- **OI factors:** each new factor — null policy, declared warmup (1h-bar units), causality, known-value; rolling/causal AST scan (G1); future-bar-invariance sentinel (G2); the `log_change` primitive (if net-new) gets its own known-value + causality test.
- **1h alignment:** the downsample causality guard (delete/reverse/shuffle future 5-min obs → bit-identical 1h value); cross-stream join integrity (OI 1h grid vs spot OHLCV 1h grid — identical coverage OR explicit inner-join with logged drop count; one-bar misalignment RAISES).
- **Hypotheses:** each compiled-through-engine; `set_coc/coo(False)`; signal at N close fills at N+1 open; long/flat ternary sizing emits the `{0,0.5,1.0}` ladder; H1/H3 **exact-partition** assertion (H1 `≥ θ_oi_hi` / H3 `< θ_oi_hi` → disjoint at the boundary); H1 **no-time-stop** assertion.
- **Verdict harness (`pathd_*`):** forward_2026 single-run holdout producer; CandidateMoments constructor + integrity gate (+ the Path C `0d06c22d` degenerate/flat-equity handling, inherited — a 0-trade leg is a Tier-5 non-pass, excluded from DSR, recorded); DSR-FWER N\*=3 (reuse, `pass_B` keyed on `holdout_sharpe`); earned-negative taxonomy with the tiered 24h+72h sanity horizon + thin-sample-SANE clause; orchestrator end-to-end; the **§37.1 function-boundary authorization gate** (`PHASE_D_AUTHORIZED` + injected `_run_backtest`; `run_verdict(_run_backtest=None)` raises while unauthorized) **re-verified to survive the `pathc_*→pathd_*` rename**; **sealed `tier6_dsr_v1` sha256 4/4 unchanged before AND after.**
- **Diagnostic (fenced, §9):** D1 (vs momentum) computed + reported; asserted diagnostic-only (not promotion-affecting, not in N\*); the **D2 path asserted ABSENT** — `basis_marginal_d2` / `redundancy_read` / `d2_agrees` / `d1_noninert` asserted **unwired** in the Path D verdict path (A1 regression guard); the **contamination-correlation set** computed + reported + asserted fenced.
- Full suite green before each register/seal boundary (current baseline **pc9 3014**, full suite per the Path C SEAL).

---

## 12. Risks & open questions

- **The directional OI edge is weakly evidenced AND directionless (headline risk).** The *strong* OI/positioning edge is cross-sectional (Chi et al. JFM 2023), which a single-asset directional engine cannot express; and OI cannot originate a sign, so it can only gate a price book. A clean earned-negative is the most likely outcome (§1). Do not oversell.
- **The vol/liquidation-cascade residual (the advisor's single biggest concern — pre-disclosed, B2).** The velocity firewall reduces *level/momentum* endogeneity but leaves *vol/liquidation* endogeneity: a long-squeeze cascade dumps OI and price **together**, so an `oi_velocity > 0` gate systematically *excludes violent down-bars* → it can be a **realized-vol/tail filter wearing an OI mask**, which **D1 (a momentum control) cannot catch.** A non-inert D1 on OI-velocity is therefore consistent with a vol filter and does **not** by itself license an OI-edge claim. **Containment (no added DoF):** the fenced contamination-correlation set (§9) quantifies it; the promotion gate (Tier-5 + DSR) is the real licensing; the clean-negative prior absorbs it. We deliberately do **not** add a vol-control diagnostic (scope/DoF discipline).
- **OI velocity is sign-agnostic.** OI rises on new shorts as well as new longs; the "new-flow" naming (H3) does not claim "new longs." Directionality is 100% the inherited price cross.
- **Momentum endogeneity (H1 most exposed).** OI level is near-cointegrated with cumulative price drift → the un-firewalled level leg (H1) is the most momentum-contaminated; H3 (velocity continuation) is the most endogenous velocity leg. D1 + the thin-sample-SANE clause are the guards.
- **The 2020-09 data handicap (heightened under-power).** OI history starts ~8 months later than OHLCV/funding/basis (in-repo prior, §13; re-verified at register-A). The shorter train + the inherited AND-confirm could push all three legs INDETERMINATE → the verdict may rest on §37.3's substantive-measured-loss path with thin samples. Pre-disclosed (§9).
- **Data-availability is the #1 register-A unknown.** OI history start, the `metrics` CSV schema, the cadence, and the contracts-vs-notional unit must all be empirically re-verified; CCXT gives only ~30 days so Binance Vision bulk is the sole backfill path. Per §38.1 the first ingestion run is the validation gate.
- **No-peek discipline.** The pre-registration is theory-driven only. No 2026 OI observation may touch the design — that would be a forward_2026 peek voiding the cycle.
- **Citation verification (open; §1 discipline).** The cross-sectional-positioning framing (Chi et al. JFM 2023) is carried verbatim-verified from the Path C LOCK; any OI-specific literature claim is re-verified at the B2 before the LOCK. The single-asset *directional* OI taxonomy is treated as folklore-grade (no load-bearing citation).
- **Open (review-gate / Step −1 lock):** the exact OI series (`sum_open_interest`), downsample rule, `oi_pct_rank` window, `oi_velocity` span, `θ_oi_hi` rule, H2 band edge, `max_hold` values, and the contamination-correlation series/window — all locked a priori at Step −1, no train tuning, Charlie per-parameter register.

---

## 13. Verified anchors (this cycle)

- **OI data source — NOT yet independently probed this cycle (honest gap; the #1 register-A item).** The realistic source is Binance Vision `futures/um/daily/metrics/BTCUSDT/` (≈5-min cadence, header CSV). **History start is the in-repo prior `2020-09`** (Path C spec [§1, line 36](2026-05-31-path-c-basis-scoping-design.md): *"OI … starts 2020-09, an 8-month gap worsening the §37.3 under-power problem"*) — **re-verified at register-A**, not asserted here. CCXT `fetch_open_interest_history` ≈ 30-day window only → bulk Vision is the sole full-history path. Per §38.1/§38.2 the first ingestion run is the format/availability validation gate.
- **Local spot anchor (verified, Path C):** `data/raw/btcusdt_1h.parquet` 55,105 rows, 2020-01-01 → 2026-04-16, `datetime64[ms, UTC]` — the price series the OI gate rides on.
- **Reconciliation 2-leg B2 (2026-06-01):** Codex *SOUND-WITH-CAVEATS* (verified D1 is an equity-Sharpe-difference; `redundancy_read` is a 2-input pinned table; `input_source` is a `str` validation set; `pathc_moments.py` is the moments file); advisor *ADOPT-WITH-CHANGES* (D2-not-a-relabel → drop; firewall residual disclose; H1-weakest flip; near-zero-D1-modal; tone reframe; cite 2020-09). All changes folded into this spec. Both legs grounded; both load-bearing claims independently re-verified by the orchestrator.
- **Path C verdict + LOCK + harness (grep-verified):** `data/phase2c_evaluation_gate/pathc_verdict_v1/`; `backtest/pathc_{marginal_diagnostic,eval_gauntlet,moments,dsr_fwer,earned_negative,escalation,holdout_producer,orchestrator,perleg_mechanism,train_sanity}.py`; `scripts/pathc_run_verdict.py`; `factors/{basis,basis_derive,registry,build_features}.py`; `ingestion/{funding_*,markprice_*}.py` — all reusable templates.
- **Literature (carried verbatim-verified from the Path C LOCK):** strong basis/positioning edge is **cross-sectional** (Chi et al. JFM 2023, DOI 10.1002/fut.22425) — not single-asset directional; short-horizon. Crypto carry / leveraged-long demand (Schmeling/Schrimpf/Todorov, BIS WP 1087). The single-asset *directional* OI taxonomy (price×OI 4-state folklore) is **not** treated as a load-bearing citation.
- **Discipline:** `config/execution_phaseb_spot_15bps.yaml` (15 bps); `config/environments.yaml` forward_2026; `backtest/tier6_dsr.py` Form B + `Z_PASS`; `backtest/wf_lineage.py` `check_evaluation_semantics_or_raise` (`single_run_holdout_v1`); CLAUDE.md HARD CONSTRAINTS + Conservative-Anchor Gate Integrity; METHODOLOGY_NOTES §36 + §37 + §38.

---

## 14. Terminal state

On written-spec review-gate approval + (per scope discipline) the 2-leg B2 already completed on the reconciliation: write + commit the Step −1 pre-registration LOCK (`2026-06-01-pathd-step-minus-1-preregistration-lock.md`) as its own Charlie register-event, then invoke `superpowers:writing-plans` to turn this spec into a step-by-step implementation plan (ingestion → build → run). Ingestion / build / run each remain a separate downstream Charlie register; this cycle authorizes none of them.
