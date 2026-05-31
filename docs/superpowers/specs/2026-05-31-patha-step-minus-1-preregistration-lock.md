# Path A — Step −1 Pre-Registration LOCK (Funding-Rate Axis)

**Date:** 2026-05-31 (UTC)
**Status:** **LOCKED** at a Charlie register-event 2026-05-31. This file is committed **BEFORE** any funding data is ingested or peeked, any factor build, and any evaluation — its commit-order is the anti-hindsight evidence (METHODOLOGY_NOTES §3.3: pre-register expectations before running; commit-order so post-hoc rationalization is impossible). Only the Binance Vision file *listing* was verified (funding history starts 2020-01); no funding *values* have been observed.

**Authority:** Charlie register (plain-text, 2026-05-31): "register, 实施计划走2 leg review" — registering the a-priori values presented in chat (Q1 funding-only, Q2 N\*=3, Q3 forward_2026 gate, Q4 scope-only + full ingestion design, Q5 all long/flat).

**Binding rule:** **No post-hoc additions.** Adding any variant after any funding peek / Step-0 / run result is seen **voids N\*** and invalidates the cycle's falsification integrity. The values below are frozen for the duration of the Path A cycle.

**Governing spec:** [2026-05-31-path-a-funding-scoping-design.md](2026-05-31-path-a-funding-scoping-design.md) (v1, B2-reviewed). **Plan:** [../plans/2026-05-31-patha-funding-mine.md](../plans/2026-05-31-patha-funding-mine.md) (to be written by `writing-plans`, 2-leg-reviewed).

---

## Pre-registration 1 — Hypotheses + variant grid → N\*

**N\* = 3** (minimal grid: 3 hypotheses × 1 pre-registered variant each; **no parameter sweep**). This is the full considered inferential family; N\* counts it in full. All **long/flat**, ternary `{0, 0.5, 1.0}` sizing on `cdf_realized_vol_720`. Funding factors are computed on the **8h settlement series** (causal rolling over settlement units) and carried forward onto 1h bars by a backward as-of join (discrete-settlement carry, NOT interpolation; `funding_interval_hours` read per-row, never hardcoded). Funding gates the long ON/OFF or the entry trigger; it never scales position size.

| Hyp | Family | Locked parameters |
|---|---|---|
| **H1** `funding_extreme_fade` | crowded-long reversal (long-biased de-risk overlay) | **flat** when `funding_pct_rank_270 ≥ 0.90` AND `funding_sign > 0`; **long** otherwise (the complement). `max_hold_bars = 72`. Sizing: vol-CDF ternary on `cdf_realized_vol_720` — `1.0` in band `[0.3, 0.8]`, else `0.5`; `0` when flat. |
| **H2** `funding_sign_regime_switch` | regime-gate on a price-trend book (state-class) | regime axis = causal rolling-270 percentile of `funding_ewm_30` (`adjust=False`). **DE-RISK (flat)** when that percentile `≥ 0.80`; **PERMISSIVE** otherwise → **long** when `decay_linear_close_48 > decay_linear_close_168`. Exit: enter de-risk regime / trend roll-over (`48 < 168`) / `max_hold_bars = 24`. Same vol-CDF ternary sizing. |
| **H3** `funding_momentum_continuation` | moderate-persistence trend confirm (state-class) | **long** when `funding_ewm_60 > 0` (`adjust=False`) AND `funding_pct_rank_270 ≤ 0.90` (excludes H1's tail → non-overlapping populations) AND `decay_linear_close_48 > decay_linear_close_168`. Exit: `funding_ewm_60 ≤ 0` / trend roll-over / `funding_pct_rank_270 > 0.90` / `max_hold_bars = 48`. Same vol-CDF ternary sizing. |

**Locked factor windows (a-priori, no train tuning):** `funding_pct_rank_270` = rolling 270 settlements (≈90 days) causal percentile of the settled funding rate; `funding_ewm_30` / `funding_ewm_60` = causal EWM spans of 30 / 60 settlements (`adjust=False`); `funding_sign` = sign of the carried settled rate. Price-trend confirm reuses Path B's `decay_linear_close_48 > decay_linear_close_168`. Sizing reuses Path B's `cdf_realized_vol_720` band.

## Pre-registration 2 — Gate (locked, never revisited post-result)

- Cost anchor: `spot_realistic_15bps_v1` — 15 bps/side (`config/execution_phaseb_spot_15bps.yaml`). **Not relaxed.**
- Tier-5 entry: `holdout_sharpe > 0` (strict) at 15 bps on the **forward_2026** single-run holdout artifact (`check_evaluation_semantics_or_raise`, `evaluation_semantics = 'single_run_holdout_v1'`).
- Tier-6 multiplicity: DSR-FWER, **Form B authoritative**, at **N\* = 3** (`backtest/tier6_dsr.py`, `Z_PASS = 1.644853626951472` frozen; reused for Path A's own new cohort; sealed `tier6_dsr_v1` byte-untouched — sha256 re-verified before AND after).
- 2025 test touched once only for a `b_positive` confirmation.

## Pre-registration 3 — Process-delta (set before any result)

- **Cost-aware objective:** any ranking among the pre-registered variants is by Sharpe **net of 15 bps/side**; floors applied **before** ranking.
- **Hypothesis-class floors (eligibility, on the TRAIN window):**
  - **H1 (long-biased overlay):** ≥ **200 defensive flat-exit episodes** (funding-signal firings) over train — NOT long-bar occupancy.
  - **H2 / H3 (state-class):** `zero_fraction < 0.50` **AND** ≥ **200** trades over train.
  - **Deployment-readiness target** (separate from eligibility): ≥ **1000** trades.
- **Sizing:** single-factor vol-CDF ternary `{0, 0.5, 1.0}` (funding gates, never scales size).
- **Causal funding carry-forward:** funding features computed on the 8h settlement series; bar N at close `c` receives the most recent settlement with `calc_time ≤ c`; dedicated causality guard (delete/reverse/shuffle future settlements → bit-identical).
- **Fenced funding-marginal-contribution diagnostic (diagnostic-only, NOT in N\*, NOT promotion-affecting):** funding-gated strategy vs the identical price-trend / always-long baseline WITHOUT the funding gate, on the same bars — so any A-result attributes to funding's marginal contribution, not Path B's already-dead decay-MA leg (H2/H3) or buy-and-hold (H1).

## Pre-registration 4 — Kill-criterion taxonomy + A-escalation (advisory; Charlie registers the fire)

- **mechanism-refuted** — no leg's conditional forward-return sign matches its hypothesized direction (H1 reversal-DOWN; H2 permissive-mean > de-risk-mean AND permissive-mean > 0; H3 continuation-UP). Earned negative.
- **process-refuted-for-this-grid** — ≥1 leg mechanism-sane, but **no variant clears Tier-5 `holdout_sharpe > 0`** at 15 bps on forward_2026. Earned negative.
- **b-positive** — ≥1 variant clears Tier-5 `holdout_sharpe > 0` (even if it fails DSR-FWER at N\*); weak if no DSR pass (needs 2025 OOS), stronger if a DSR `pass_B`. NOT an earned negative.
- **Mechanism-sanity (train-only):** conditional forward-return sign test (Pre-reg 1 directions) at **24h AND 72h** horizons. **strong-sane** = hypothesized sign at *both* horizons; **weak-sane (floor)** = sign at *either*. Both signs are pre-registered and reported separately; a verdict resting on weak-sane-only legs is flagged in the advisory bundle (so a single-horizon noise flip cannot silently manufacture mechanism-sanity).
- **Objective-A / next-axis escalation (advisory):** any "a real edge exists" determination is gated by DSR-**significance** (`pass_B` / PSR ≥ 0.95), **not** a point-estimate. **The binding taxonomy verdict and the actual escalation are a Charlie register-event** at the earned-negative gate — never an automated fire.

---

## What this lock authorizes next

- **The implementation plan** (`superpowers:writing-plans`, 2-leg-reviewed per Charlie register) may now be written: ingestion → funding-feature pipeline → factors + DSL hypotheses + `patha_*` harness reuse → run.
- **Ingestion / build / run each remain a separate downstream Charlie register-event** — this lock authorizes none of them; it freezes the pre-registration only.
- **Per-task commits await Charlie authorization** (only Charlie-register authorizes operational fires).
- The next crypto-native axes (open interest, perp-spot basis, liquidations), short legs, and continuous/funding-scaled sizing remain conditional, separately-registered successors — **not scoped here** (anti-pre-emption).
