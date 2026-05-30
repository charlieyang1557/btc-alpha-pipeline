# Path B — Step −1 Pre-Registration LOCK

**Date:** 2026-05-30 (UTC)
**Status:** **LOCKED** at a Charlie register-event 2026-05-30. This file is committed **BEFORE** any Step-0 diagnostic, any factor/operator build, and any evaluation — its commit-order is the anti-hindsight evidence (METHODOLOGY_NOTES §3.3: pre-register expectations before running; commit-order so post-hoc rationalization is impossible).

**Authority:** Charlie register (plain-text, 2026-05-30): "照上面的默认值 register,N\* = 3(最小网格)".

**Binding rule:** **No post-hoc additions.** Adding any variant after Step-0 or Step-4 results are seen **voids N\*** and invalidates the cycle's falsification integrity. The values below are frozen for the duration of the Path B cycle.

**Governing spec:** [2026-05-30-pathb-mechanism-first-rethink-design.md](2026-05-30-pathb-mechanism-first-rethink-design.md) (v2.1, §7 four pre-registrations). **Plan:** [../plans/2026-05-30-pathb-mechanism-first-rethink.md](../plans/2026-05-30-pathb-mechanism-first-rethink.md) (v2, 30 tasks).

---

## Pre-registration 1 — Hypotheses + variant grid → N\*

**N\* = 3** (minimal grid: 3 hypotheses × 1 pre-registered variant each; **no parameter sweep**). This is the full considered inferential family; N\* counts it in full.

| Hyp | Family | Locked parameters |
|---|---|---|
| **H1** `intrabar_push_fade` | microstructure mean-reversion (event-class) | `θ_push = −0.6` (fade a one-sided DOWN-push: long when `intrabar_push < −0.6`), `θ_range = 1.0` ATR (require `range_over_atr > 1.0`), `max_hold_bars = 3`; vol-regime ternary sizing on `cdf_realized_vol_720`: full size in band `[0.3, 0.8]`, else `0.5`. |
| **H2** `vol_regime_switch` | regime-conditional revert/trend (state-class) | regime gate `cdf_realized_vol_720` median split (`0.5`); LOW (`cdf<0.5`): long when `zscore_48 < −1.0`; HIGH (`cdf≥0.5`, sign flip / trend): long when `zscore_48 > +1.0`; sizing inverse-vol clipped `[0.25, 1.0]` × `|zscore_48|` strength step. Long/flat. |
| **H3** `decay_trend_persistence` | trend (state-class) | `decay_linear_close_48` vs `decay_linear_close_168`; long while `48 > 168` AND `realized_vol_24h` below its `cdf_realized_vol_720` top-decile gate (`cdf ≤ 0.9`); 3-state `{0, 0.5, 1.0}` ladder by vol-CDF band × trend-strength agreement. |

## Pre-registration 2 — Gate (locked, never revisited post-result)

- Cost anchor: `spot_realistic_15bps_v1` — 15 bps/side (`config/execution_phaseb_spot_15bps.yaml`). **Not relaxed.**
- Tier-5 entry: `holdout_sharpe > 0` (strict) at 15 bps.
- Tier-6 multiplicity: DSR-FWER, **Form B authoritative**, at **N\* = 3** (`backtest/tier6_dsr.py`, re-locked per cohort; sealed `tier6_dsr_v1` byte-untouched).

## Pre-registration 3 — Process-delta (set before any result)

- **Cost-aware objective:** any ranking among the pre-registered variants is by Sharpe **net of 15 bps/side**; floors applied **before** ranking.
- **Hypothesis-class floors (eligibility):**
  - **H1 (event-class):** ≥ **200** entry events over the train window.
  - **H2 / H3 (state-class):** `zero_fraction < 0.50` **AND** ≥ **200** trades over the train window.
  - **Deployment-readiness target** (separate from eligibility): ≥ **1000** trades (`TECHNIQUE_BACKLOG.md` §3.8 criterion 5).
- **Ternary sizing ladder:** discrete `{0, 0.5, 1.0}` (default), per hypothesis above.

## Pre-registration 4 — Kill-criterion taxonomy + A-escalation (advisory; Charlie registers the fire)

- **mechanism-refuted** — no leg's conditional forward-return sign matches its hypothesized direction (H1 fade→reversion-UP; H2 LOW revert-UP / HIGH trend-UP; H3 trend-UP). Earned negative.
- **process-refuted-for-this-grid** — ≥1 leg mechanism-sane, but **no variant clears Tier-5 `holdout_sharpe > 0`**. Earned negative.
- **b-positive** — ≥1 variant clears Tier-5 `holdout_sharpe > 0` (even if it fails DSR-FWER at N\*); weak if no DSR pass (needs 2025 OOS), stronger if a DSR `pass_B`. NOT an earned negative.
- **Objective-A escalation (advisory):** warranted iff **(i)** process-refuted-for-this-grid **AND** **(ii)** the Step-0 diagnostic lifted no dead candidate above 0. **The binding taxonomy verdict and the actual A-escalation are a Charlie register-event** at the earned-negative gate — never an automated fire.

---

## What this lock authorizes next

- **Step 0** (advisory-only pre-B diagnostic) and **Steps 1–5** (build + evaluate) may now proceed, subagent-driven.
- **Per-task commits await Charlie authorization** (only Charlie-register authorizes operational fires).
- Path A remains a conditional, separately-registered successor — **not scoped here** (anti-pre-emption).
