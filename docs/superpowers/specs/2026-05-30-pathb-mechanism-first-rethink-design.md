# Path B — Mechanism-First OHLCV Re-Mine (Alpha-Source Rethink, Cycle 1) — Design Spec

**Date:** 2026-05-30 (UTC)
**Version:** v2 (B2-review-adopted; all 13 adjudicated changes incorporated — see §0.2)
**Status:** DRAFT — pending Charlie review-gate register. NOT yet authorized for implementation or commit.
**Cycle class:** Bounded, pre-committed, one-cycle falsification test (the "alpha-source rethink" registered in direction by Charlie 2026-05-30).
**Predecessor:** A-1 SD-E-γ stationary-bootstrap suitability cycle SEAL (`docs/phase5/A1_SERIALCORR_BOOTSTRAP_SUITABILITY_NOTE.md`); Tier 6 DSR evaluation 0/18 (`docs/phase5/R6_1_TIER_6_EVALUATION_APPLICATION_NOTE.md`).
**Cost anchor:** `spot_realistic_15bps_v1` — 15 bps/side, 30 bps round trip (`config/execution_phaseb_spot_15bps.yaml`). HARD CONSTRAINT; not relaxed anywhere in this cycle.

---

## 0.1 Registered decisions (provenance)

Each was surfaced as plain-text options + intuitive Chinese and explicitly registered by Charlie (reviewer convergence was advisory only):

| Decision | Registered outcome |
|---|---|
| D1 — central bet | **Path B** as the bounded active cycle; **Path A** (new crypto-native data) as a *conditional, separately-registered successor* (objective trigger pre-committed, scope unlocked — anti-pre-emption). |
| D2 — hypotheses | Core 3: **H1** `intrabar_push_fade`, **H2** `vol_regime_switch`, **H3** `decay_trend_persistence`. |
| D3 — leakage guard regime | Confirmed (G1–G4 below), sequenced as **Step 1 — before any new operator is used**. |
| Fork A — pre-B diagnostic | **YES** — Codex's cheap diagnostic is **Step 0** (advisory-only). |
| Fork B — directionality | **Long/flat only** this cycle (no short legs; short deferred). |
| B2 changelog | **All 13 adjudicated changes adopted** (registered 2026-05-30). |

## 0.2 B2-review changelog (v1 → v2)

Two B2 legs (Codex adversarial + quant-research-advisor) reviewed v1; both ENDORSE-WITH-CHANGES. Every cited code claim was grep-verified TRUE. Adopted changes:

- **[C1] Holdout-artifact pinning** — v1 conflated three artifacts under "holdout_sharpe". Correct guard mapping (per `wf_lineage.py:19-20`): **train walk-forward** → `check_wf_semantics_or_raise` (`corrected_test_boundary_v1`); the **single-run evaluations — 2022 regime-holdout, the forward single-regime holdout, and 2024 validation** → `check_evaluation_semantics_or_raise` (`single_run_holdout_v1`; the regime-holdout gate is a single-run evaluation, like PHASE2C_6). v2 §4/§6/§9 pin each; Path B produces its **own** evaluation artifacts. *(v2.1 errata: an earlier v2 draft mis-pinned the 2022 regime-holdout to `check_wf_semantics_or_raise`; corrected here after the plan-B2 integration trace.)*
- **[C2] Narrowed earned-negative** + taxonomy (§1, §9).
- **[C3] N\* plumbing** is real implementation work; sealed `tier6_dsr_v1` byte-untouched (§8).
- **[C4] Pre-registration is a register-event BEFORE Step 0**; Step 0 advisory-only (§6, §7).
- **[C5] `cdf_realized_vol_720` causal construction pre-committed** (§3, §5).
- **[C6] Ternary sizing = pure compiler closure** + no-positive-index tests + sizer override semantics (§4, §5, §11).
- **[C7] Hypothesis-class floors** (event vs state) replace the universal occupancy floor (§9).
- **[C8] H2 kill split into per-leg sign kills** (§3).
- **[C9] Small-N\* asymmetry** surfaced; B-positive tempered + 2025 OOS confirmation (§8, §9).
- **[C10] Honesty fixes**: floor "pre-committed not derived"; diversity = "2 families + a switch meta-bet"; `prompt_builder:233` is caller-discipline + leakage-test, not code-enforced; G1 necessary-not-sufficient, G2 authoritative; freeze **all considered** variants ex-ante (§3, §5, §6, §7, §9, §12).
- **[C11] Fence holdout-reuse**: comparative-baseline kills are diagnostic-only or counted in N\* (§3, §9).
- **[C12] H1 grid scrutiny** at the §7 lock (§3, §7).
- **[C13] Train-only mechanism sanity table** before backtests (§6).

---

## 1. Motivation & frame

**Binding constraint = the alpha source / hypothesis-space, NOT data volume or statistical methodology** (reviewer-convergent, Charlie-registered; memory `alpha-source-is-the-binding-constraint-not-data-methodology`). Evidence: Tier 6 DSR sealed **0/18 promoted** at 15bps, best candidate ~**1.89 z-units short**; A-1 found the survivors **sparse / low-trade-frequency** (zero_fraction 0.64–0.99); the funnel was **993 → 39 → 18** so N\*=18 is *lenient*.

**Why Path B first (the central bet).** The 0/18 result is a *source-or-process* statement that cannot by itself discriminate. The sparse survivors are *predicted by verified process defects*: the selection objective is **not cost-aware** (`agents/critic/d7a_rules.py`), sizing is **all-in-or-flat** (`dsl.py:244`), there is **no min-trade-count filter**, and the DSL is **comparison-only** (`dsl.py:53`). Path B holds the **data fixed** and varies **only the process**:
- **B-negative** → the process explanation is *refuted for this grid*, and the A escalation is *earned as the next-cheapest untried axis* — handed a validated process. (See §9 for the precise, narrowed claim: B-negative does **not** prove OHLCV is exhausted.)
- **B-positive** → edge existed and the process was destroying it; A becomes optional upside — **re-evaluated by Charlie, not auto-demoted** (and a small-N\* B-positive is weak evidence; §8).

There is no B outcome we regret running first, and B is the cheapest path (no ingestion; reuses the DSL+backtest stack).

---

## 2. Scope

**In scope:** (1) pre-B diagnostic re-score (Step 0, advisory-only); (2) a leakage guard-rail layer (Step 1); (3) one new DSL operator (`decay_linear`) + 5 factors + a ternary sizing node (Step 2), each fully tested; (4) three pre-registered mechanism-first hypotheses (Steps 3–4); (5) cost-aware evaluation + hypothesis-class floors + DSR-FWER at a pre-committed, re-locked N\* (Steps 4–5).

**Out of scope (non-goals):**
- ❌ Broad DSL search / AI proposer-critic batch generation (mechanism-first + narrow; broadening re-inflates the unpriced-funnel leak).
- ❌ Cross-sectional operators (`rank`/`indneutralize`/`scale`) and any multi-asset universe (deferred; `TECHNIQUE_BACKLOG.md` §4.1.8/§4.1.9).
- ❌ Crypto-native derivatives data (funding/OI/liquidations/basis) — that is **Path A** (separately-registered conditional successor; candidate #9 `funding_epoch_fade` self-flagged infeasible on spot and *seeds* A).
- ❌ Short legs (Fork B: long/flat only).
- ❌ Any change to the promotion gate math or the 15bps anchor; the only sanctioned gate action is re-locking N\* per cohort (§8). Sealed `tier6_dsr_v1` artifacts stay byte-identical.

---

## 3. The three pre-registered hypotheses

All **long/flat**, continuously-active, ternary `{0, 0.5, 1.0}` sizing. Parameters fixed from the mechanism (§3.8 criterion 2). **Diversity is honestly "two edge-families (revert / trend) + a regime-switch meta-bet,"** not three independent bets (H1+H2-low are both short-horizon revert; H2-high+H3 are both trend) — adequate to localize an OHLCV ceiling (revert and trend are what price-only TA can express) without over-claiming. Each hypothesis's *promotion-affecting* signal is its net-of-cost performance; its mechanism-sanity comparisons (e.g. "decay beats SMA") are **diagnostic-only, not promotion-affecting** unless enumerated into the N\* grid (§9, C11).

### H1 — `intrabar_push_fade` (microstructure mean-reversion; event-class)
- **Mechanism:** a 1h bar closing near its extreme (`|intrabar_push|` large) reflects one-sided, largely uninformed taker flow; the liquidity provider who absorbs it is paid by partial reversion over 1–3 bars. Edge exists only at meaningful displacement (push large **and** range > 1 ATR).
- **Signal:** factors `intrabar_push = (close-open)/((high-low)+1e-9)`, `range_over_atr = (high-low)/atr_14`. Long when `intrabar_push < θ_push AND range_over_atr > θ_range`; long/flat (an up-push opens nothing). Time exit `max_hold_bars = H1_hold`.
- **Sizing:** vol-regime ternary on `cdf_realized_vol_720` (full in a mid band, half outside).
- **Pre-registered grid / N\* (C12):** H1 has four thresholds (`θ_push, θ_range, H1_hold`, vol band) with **no external derivation** — they are the most closet-fit-exposed in the slate. Any enumerated alternatives (e.g. `θ_push ∈ {−0.5,−0.6,−0.7}`) MUST be counted in N\* at the §7 lock; if a single value is asserted, it is locked with no post-hoc sweep.
- **Floor (event-class, C7):** eligibility by **trade-count / min-events** (not occupancy — an event strategy with `max_hold=3` is legitimately flat most of the time). Long/flat halves the directional event count (down-pushes only); the count must still clear the event floor or the hypothesis is reported sparse.
- **Kill (pre-registered):** if `sign(mean forward-H1_hold return | push<θ_push)` is *continuation* (same sign as the push), not reversion, on the in-train artifact (§4) → overreaction mechanism refuted. We do **not** flip to momentum.

### H2 — `vol_regime_switch` (regime-conditional; state-class)
- **Mechanism:** low-vol → maker-dominated chop → overshoots revert; high-vol → leverage cascades → returns trend (leverage-effect prior). The *switch* is the edge.
- **Signal:** regime gate `cdf_realized_vol_720` median split (≈50/50 occupancy → continuously active). Core `zscore_48`. LOW: long when `zscore_48 < −1.0`. HIGH (sign flip): long when `zscore_48 > +1.0`. Long/flat (each regime's short side is flat).
- **Sizing:** inverse-vol target × `|zscore_48|` strength step → ternary ladder (cost-aware: high-vol trades smaller).
- **Floor (state-class):** occupancy-based (`zero_fraction` low) — appropriate for a near-continuous state strategy.
- **Kill (pre-registered, per-leg — C8, split from v1's AND):** **(a)** if the LOW-vol leg's conditional forward return is not positive (revert refuted) → LOW leg dead; **(b)** if the HIGH-vol leg's conditional forward return is not positive in the trend direction (leverage-effect sign violated) → HIGH leg dead; **(c)** if a regime-blind single sign backtests ≥ the switch → the switch adds no value (refuted). Each fires independently; a wrong-signed HIGH leg can no longer survive on a correct LOW leg.

### H3 — `decay_trend_persistence` (trend; state-class)
- **Mechanism:** short-horizon trend persistence (under-reaction); `decay_linear` cuts the SMA's phase lag ~in half so the trend state turns continuously, not at rare crossings.
- **Signal:** operator `decay_linear`; factors `decay_linear_close_48`, `decay_linear_close_168`. Long while `decay_linear_close_48 > decay_linear_close_168 AND realized_vol_24h` below its `cdf_realized_vol_720` top-tail gate; flat otherwise.
- **Sizing:** 3-state ladder by `cdf_realized_vol_720` band × trend-strength agreement.
- **Floor (state-class):** occupancy + a trade-count floor (a trend strategy that collapses to near-zero trades has failed the anti-sparseness purpose).
- **Kill (pre-registered):** KILL if the trend leg has no net edge **while** an equal-weight SMA-cross baseline does not do worse (decay gave no advantage — *diagnostic comparison, fenced per C11/§9*); OR trade count collapses below the floor; OR removing the vol-CDF gate does not degrade Sharpe (*diagnostic, fenced*).

---

## 4. Build surface

- **New DSL operator (1):** `decay_linear(x, d)` — linearly-weighted trailing MA (strictly backward).
- **New registered factors (5):** `intrabar_push`, `range_over_atr`, `cdf_realized_vol_720` (shared H2+H3), `decay_linear_close_48`, `decay_linear_close_168`. Reuses existing `zscore_48`, `realized_vol_24h`, `atr_14`, returns.
- **New DSL capability (1):** ternary/conditional position-sizing node — relax `position_sizing: Literal["full_equity"]` (`dsl.py:244`) to a discrete `{0, 0.5, 1.0}` ladder. **Heaviest item.** The `CONTRACT GAP` at `dsl.py:233-244` requires a discriminator + per-variant compiler tests + `position_sizing` staying in D3's canonical hash. **Implementation (C6):** the size is emitted as a **pure compiler closure** reading only `cur_row`/`prev_row` (never a positive `self.data` index); it **overrides** the global `PercentSizer` (`execution_model.py:143`) with an explicit per-order size (override semantics pinned, not composed, so the `{0,0.5,1.0}` ladder is unambiguous).
- **Process (2):** cost-aware evaluation objective (net-of-15bps Sharpe); hypothesis-class trade/occupancy floors.

---

## 5. Leakage guard-rail regime (Step 1 — lands before any new operator is used)

Charlie-registered as existential. Existing defense is strong (causality via `tests/test_factors.py:449`; timing via `execution_model.py:133-134`), but future-touching ops are caught **only behaviorally**. This layer closes the gap **before** new operators exist:

- **G1 — AST source-scanner at registration** (extend `_assert_top_level_callable`, `registry.py:97`): reject `.shift(<0)`, `.bfill`/`backfill`, `rolling(center=True)`, bare `.expanding()`, and global `.mean()/.std()/.sum()/.rank()` on a full Series. **Necessary-not-sufficient (C10):** it catches pandas-method leaks; non-pandas numpy/list future reads can slip → **G2 is the authoritative behavioral guard.**
- **G2 — shuffle-future / time-reversal sentinel** (parametrized over `registry.list_names()`): a factor's value at bar N must be bit-identical when bars >N are deleted, reversed, **and** shuffled.
- **G3 — per-operator known-value tests + ternary-sizing causality test:** each new operator gets a known-value test; the ternary closure is asserted (static + runtime) to read only `cur_row`/`prev_row`, never a positive `self.data` index.
- **G4 — registry-derived invariance coverage:** auto-derive the future-bar-invariance list from `registry.list_names()` + a sync meta-test.

**Highest-leakage-risk factor — `cdf_realized_vol_720` (C5, shared by H2+H3, so one leak contaminates two of three hypotheses).** Pre-committed causal construction: a **named top-level helper** (not a `lambda`-in-`apply`, which would trip `_assert_top_level_callable`) computing, at bar N, the rank of `realized_vol_24h[N]` within the strictly-backward window `[N−719, N]` — no centering, no full-series `.rank()`. This factor gets a dedicated G2 sentinel test before H2/H3 are evaluated.

Path-A-only guards (`merge_asof(backward)` + publication-lag + provenance-stamping into `feature_version`) are **deferred** — not built this cycle.

---

## 6. Cycle sequence

- **Step −1 — Pre-registration register-event (C4).** The four pre-registrations (§7) are locked at their **own Charlie register-event** BEFORE any diagnostic or build, so nothing downstream can reverse-fit them.
- **Step 0 — pre-B diagnostic (advisory-only, C4/C11).** Re-score the existing 993/39/18 artifacts under the *already-locked* cost-aware objective + floors. **Read-only; cannot promote, revive, or re-rank any dead candidate** — output feeds only the §9 A-escalation trigger's second prong. Consumes corrected artifacts only; calls the correct `wf_lineage` guard (§ below).
- **Step 1 — guard-rails (G1–G4).** Land + green before any new operator/factor.
- **Step 2 — operator + factors + ternary node.** Implement `decay_linear`, the 5 factors (incl. the `cdf_realized_vol_720` causal helper), the ternary node; each TDD with G1–G3. Rebuild factor parquet (full dataset; `feature_version` bumps).
- **Step 3 — compile hypotheses + train-only mechanism sanity table (C13).** Express H1/H2/H3 in the DSL; produce a cheap train-only table (raw forward-return signs, event counts, expected occupancy) — **no validation/test touch** — to catch a dead mechanism before spending full backtests.
- **Step 4 — evaluate, with artifacts/guards pinned per step (C1).** Walk-forward on train (2020-2021+2023, `check_wf_semantics_or_raise`, `wf_semantics='corrected_test_boundary_v1'`) → **2022 regime-holdout** (4-condition in-train stress test; **single-run evaluation artifact**, `check_evaluation_semantics_or_raise`, `evaluation_semantics='single_run_holdout_v1'`) → **2024 validation** (single-run, `check_evaluation_semantics_or_raise`) → Tier-5 entry (`holdout_sharpe > 0` at 15bps, single-run holdout artifact, `check_evaluation_semantics_or_raise`). **Path B produces its OWN new artifacts** — the sealed `phase4_forward_2026_15bps_v1/holdout_results.csv` belongs to the dead 18 and is not reused. **2025 test is touched once, only if a candidate reaches it** (and is required for a B-positive confirmation, §8). The exact window→gate mapping is pinned in the implementation plan against `config/environments.yaml` + `backtest/wf_lineage.py`.
- **Step 5 — multiplicity + earned-negative read.** DSR-FWER at the re-locked N\* (§8); apply the §9 taxonomy.

The 18-strategy dead cohort is **frozen + watchlisted** and quarantined from any generation context. Note (C10): `agents/proposer/prompt_builder.py:233` `approved_examples` is **not code-enforced redaction** — its docstring (`:121`) states it does NOT redact; quarantine rests on caller discipline + the leakage-audit test. This cycle does not use the proposer loop, so the channel is unused; the discipline is recorded so a later step cannot reintroduce the 18.

---

## 7. The four pre-registrations (locked at Step −1, before Step 0)

1. **Hypotheses + variant grid → N\*.** The exact 3 hypotheses and their **full enumerated parameter-variant grid**. N\* = the size of the *full inferential family considered*, **not** just the variants run (C10) — if any variant is added after seeing Step-0/Step-4 results, N\* is invalid and the cycle's integrity is void. This is the load-bearing integrity condition, not a footnote.
2. **Gate pre-commit.** 15bps anchor + DSR-FWER (Form B authoritative) + the Tier-5 `holdout_sharpe > 0` entry condition. Locked, never revisited post-result. No gate relaxation.
3. **Process-delta pre-spec.** The cost-aware objective; the hypothesis-class floor values (event vs state, §9); the ternary ladder — all set before any result.
4. **Kill-criterion taxonomy** (§9).

---

## 8. Multiplicity, the gate, and the small-N\* asymmetry

The DSR evaluator (`backtest/tier6_dsr.py`) is **source-agnostic** at the candidate level — `evaluate_candidate(cm, n_star=...)` (`:362`) consumes per-bar moments + `n_star`. **But re-locking N\* is real implementation work, not a free parameter (C3):** `evaluate_cohort()` hardcodes `N_STAR` (`:877/891/906`), `_evaluate_one` defaults to it (`:624`), the CLI has no `--n-star`, and tests pin `==18` (`test_tier6_dsr.py:71,411,512,546`). Path B must add `n_star` plumbing (cohort fn + CLI + MC + degenerate rows + CSV/promotion JSON + new tests) for its **own new cohort**, leaving the sealed `tier6_dsr_v1` artifacts **byte-untouched**.

**Small-N\* asymmetry (C9).** Path B's N\* (≈3–9) is much smaller than the sealed 18, so `sr_star` (the bar) is *lower* (`expected_max_ratio_form_b` grows with N\*). Consequence:
- a **B-negative is MORE conclusive** (a variant failed even an *easier* bar), and
- a **B-positive is LESS conclusive** (it cleared an easier bar than the dead cohort faced) → a B-positive requires **2025 out-of-sample confirmation** before A is re-evaluated; "B-positive → edge existed" (§1) is tempered accordingly.

Inherited limitation (not worsened if we stay narrow): N\* prices only the post-AND-gate family, not any upstream search funnel; mechanism-first narrowness keeps this gap *smaller* than the dead broad search. The 15bps anchor and `DSR ≥ 0` threshold are immutable.

---

## 9. Pre-registration values + earned-negative taxonomy (drafted; confirmed at Step −1)

Principled-direction defaults, grounded where stated and **pre-committed (not derived) where not** (C10):

- **Hypothesis-class floors (C7).** *Event-class (H1):* a min trade-count / min-event floor (occupancy is inappropriate — an event strategy is legitimately flat between events). *State-class (H2, H3):* an occupancy floor (`zero_fraction` low) + a trade-count floor. The specific numbers (e.g. event floor ~N_events; `zero_fraction < 0.50`; ≥200 trades) are **direction-grounded in the dead-cohort pathology (0.64–0.99) and §3.8, but the exact values are pre-committed choices locked at Step −1, not derived** — honest labeling per C10. Deployment-readiness target (separate from eligibility): ~1000+ trades (§3.8 criterion 5).
- **Cost-aware objective.** Any ranking among pre-registered variants is by Sharpe **net of 15bps/side**, floors applied before ranking. (Grid is pre-registered + N\* = full grid → no post-hoc cherry-picking. Open: whether a turnover-aware tie-break is needed beyond net-of-cost Sharpe — §12.)
- **N\* value** = `|full considered variant grid|` (Step −1 lock; expected ~3–9).
- **Earned-negative taxonomy (C2).** Three distinct outcomes, not one label:
  1. **mechanism-refuted** — a hypothesis's own kill condition (§3) fires (its economic story is wrong on BTC 1h).
  2. **process-refuted-for-this-grid** — every variant fails Tier-5 `holdout_sharpe > 0` at 15bps on the pinned artifact, i.e. the cost-aware + min-trade + ternary-sizing process did not rescue *these mechanisms* on OHLCV.
  3. **NOT "OHLCV exhausted."** A B-negative localizes failure away from *{cost-awareness + trade-frequency + ternary sizing + these 3 mechanisms}* and **earns A as the next-cheapest untried axis** — it does **not** exonerate the OHLCV information set, because short legs, continuous sizing, and cross-sectional structure remain *untried, not falsified*.
- **B-positive** = ≥1 variant clears Tier-5 `holdout_sharpe > 0` (even if it later fails DSR-FWER at N\*) → **weak** evidence (small-N\*, §8) requiring 2025 OOS confirmation; Charlie re-evaluates A (no auto-trigger, no auto-demote).
- **Objective A-escalation trigger.** Escalate to Path A iff **(i)** B is a *process-refuted-for-this-grid* negative **and** **(ii)** the Step-0 diagnostic showed the cost-aware re-score lifted **no** existing-cohort candidate's net excess Sharpe above 0. No subjective trigger.
- **Holdout-reuse fence (C11).** Per-hypothesis comparative-baseline kills (H2 "switch beats regime-blind"; H3 "decay beats SMA", "vol-gate is load-bearing") are extra looks at the holdout → either enumerated into the N\* grid OR marked **diagnostic-only, not promotion-affecting**. Default: diagnostic-only. Step 0 is likewise advisory-only and cannot promote/revive a dead candidate.

---

## 10. Anti-pre-emption

- Path A is registered **in direction only**; its data family, ingestion, hypotheses, and N\* are not scoped here — own register-event at A's boundary, informed by B.
- Candidate #9 `funding_epoch_fade` *seeds* A (unobservable on spot) but is not named/locked as A's content.
- The multi-asset cross-sectional 101 rebuild is deferred (`TECHNIQUE_BACKLOG.md` §4.1.9); no methodology successor (Romano-Wolf / Westfall-Young) is pre-named.
- Reviewer convergence is advisory; only Charlie-register authorizes fires.

---

## 11. Test plan

- **Guards:** G1 AST-scanner (each banned construct rejected, each allowed accepted); G2 shuffle/reverse/delete sentinel over the registry (incl. a dedicated `cdf_realized_vol_720` sentinel); G3 per-operator known-value + ternary-causality (static no-positive-index lint + runtime closure test); G4 registry/EXPECTED_FACTORS sync meta-test.
- **`decay_linear`:** known-weight output; warmup; causality.
- **Factors:** each new factor — null policy, declared warmup, causality, known-value; the `cdf_realized_vol_720` top-level-helper construction explicitly tested.
- **Ternary node:** schema discriminator; compiler emits the ladder with fills at N+1 open (no positive-index read); **override** of `PercentSizer` produces the exact `{0,0.5,1.0}` size; D3 canonical-hash includes `position_sizing`; manifest-drift raises.
- **N\* plumbing:** `evaluate_cohort`/CLI/MC/CSV/JSON accept and echo a non-18 `n_star`; sealed `tier6_dsr_v1` regression unchanged.
- **Integration:** each hypothesis compiled-through-engine; `set_coc/coo(False)`; signal at N close fills at N+1 open; per-step `wf_lineage` guard invoked with the correct semantics tag.
- **Step 0:** WF/evaluation-lineage guard called; re-score deterministic; asserts no promotion side-effect.
- Full suite green before each register/seal boundary (baseline 2484 passed / 2 xfailed).

---

## 12. Risks & open questions

- **All three economic stories are plausible but UNTESTED** — the point of Path B is to falsify them; the Step-0 diagnostic + backtest are the truth source. Do not oversell.
- **Diversity is "2 families + a switch meta-bet,"** not 3 independent (C10) — a uniform 0/N is informative about the revert/trend OHLCV ceiling, not about OHLCV in general (§9).
- **Equity-alpha decay / crowding** (H1/H3 descend from 2010-2013 equity alphas; crowded crypto trades) — BTC-specific stories + regime-holdout are load-bearing.
- **Regime dependence** — each can bleed in its opposite regime; 2022 regime-holdout is the honest stress test.
- **Ternary sizing + `cdf_realized_vol_720`** are the build/leakage risk concentrators — G3 + the §5 causal-helper pre-commit are mandatory.
- **Ternary node expressiveness (settle in the plan):** discrete ladder only vs discrete × continuous vol-scalar (H2's inverse-vol target wants the latter) — default discrete-only, approximate H2 with more discrete states unless materially distorting.
- **Open (review-gate / Step −1 lock):** exact floor values, N\* value, the H1 grid enumeration, and whether the cost-aware objective needs an explicit turnover penalty.

---

## 13. Verified anchors (grep-confirmed this cycle)

- `strategies/dsl.py:53` ops (comparison + cross only); `:244` `Literal["full_equity"]`; `:233` CONTRACT GAP.
- `agents/critic/d7a_rules.py` — 4 axes all DSL-structural (no cost/trade-count term).
- `backtest/tier6_dsr.py:39` `N_STAR=18`; `:362` `evaluate_candidate(n_star=...)` source-agnostic; `:877/891/906` `evaluate_cohort` hardcodes `N_STAR`; `:167` `check_evaluation_semantics_or_raise`.
- `backtest/wf_lineage.py:72` `WF_SEMANTICS_TAG='corrected_test_boundary_v1'`; `:79` `EVALUATION_SEMANTICS_TAG='single_run_holdout_v1'`; `:141` 2022 `regime_holdout` `bear_2022`.
- `backtest/evaluate_dsr.py:524` `holdout_sharpe → (holdout_metrics, sharpe_ratio)`.
- `factors/registry.py` — `feature_version` hashes compute source + metadata, NOT upstream data; `:97` `_assert_top_level_callable` (G1 target + lambda-in-apply trip point); `:216` post-warmup-NaN raise.
- `tests/test_factors.py:160/172/449/459` — `EXPECTED_FACTORS` hardcoded, pinned to registry; forensic future-bar-invariance. `tests/test_tier6_dsr.py:71,411,512,546` — N_STAR==18 locks.
- `backtest/execution_model.py:133-134` `cheat_on_close/open=False`; `:143` global `PercentSizer`.
- `agents/proposer/prompt_builder.py:233` approved-examples channel; `:121` "does NOT redact" (caller-discipline, not code-enforced).
- `strategies/TECHNIQUE_BACKLOG.md` §2.6.2/§2.6.3, §3.8 (`:251-261`), §3.9, §4.1.9.

---

## 14. Terminal state

On review-gate approval: invoke `superpowers:writing-plans` to turn this spec into a step-by-step implementation plan (Step −1 → Step 5), then TDD implement → B2 → Rule-2 SEAL-eve → SEAL.
