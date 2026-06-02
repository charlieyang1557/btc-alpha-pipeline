# Evaluation-Gate Power Study — design spec

- **Date:** 2026-06-02 UTC
- **Register context:** dedicated post-Path-D session. After four single-asset earned-negatives (Paths B/A/C/D), a feasibility spike on the cross-sectional fork returned `favors_shorts_cycle_first / DEFER the fork`. The 2-leg adjudication surfaced the session's key insight: **the `forward_2026` evaluation gate is refutation-powered, not confirmation-powered.** Charlie registered **(β)**: a cheap, purely-analytical gate-redesign / power-calculation precursor — scope **A + B** — *before* any shorts or fork cycle.
- **Status:** DESIGN — pre-registration of interpretation rule pending Charlie ratify. **2-leg B2 complete (Codex + advisor, 2026-06-02): SHIP-WITH-CHANGES; all nine findings adjudicated and folded into this revision.**
- **Discipline:** fresh register-event. Analytical-only. Anti-pre-emption — scoping this does not pre-decide the gate redesign, shorts, or the fork.

## 1. The question this answers

> Can this project's evaluation frame **confirm** a modest (~1–1.5 annualized Sharpe) edge at adequate statistical power under any **achievable** design — or is the gate itself a fundamental confirmation bottleneck (a candidate **second binding constraint** alongside the alpha source)?

The four prior cycles produced net Sharpes of −2.5 to −8.4 — 2-to-8σ effects that the 105-day `forward_2026` gate detected trivially. But a *modest positive* edge sits inside that gate's noise floor. That asymmetry is a property of the **gate** (window length × cost × multiplicity), not of any particular signal — so it applies equally to a future shorts cycle and to the deferred fork. This study measures it before we spend 3–6 build cycles that may be foreordained to return INDETERMINATE-on-confirmation.

## 2. Hard framing — what keeps this cheap and clean

- **Purely analytical / read-only.** Computes statistical *properties* — the DSR-FWER bar and the minimum detectable Sharpe (MDE) at 80% power — as closed-form functions of (OOS length `T`, rebalance frequency, `N*`, per-bar return moments, cost-driven turnover). Reuses [`backtest/tier6_dsr.py`](../../../backtest/tier6_dsr.py)'s exact `sr_star` + `deflated_z` primitives; adds only a power/MDE layer on top.
- **No new data, no new signal, no backtest, no funding model.** Return-moment inputs (autocorrelation → effective independent observations; skew/kurtosis) are *estimated from existing BTC data and the sealed Path artifacts*, not freshly generated. Cross-sectional inputs (IC, N, correlation, turnover) are *parameterized ranges*, pre-registered below.
- **Respects the immutable splits.** Does **not** modify `config/environments.yaml`; does **not** run any strategy on held data; does **not** peek at any held-out performance. It computes *hypothetical* power under alternative evaluation designs and *separately* enumerates which of those designs are even achievable within the immutable touch-once / no-peek discipline. **Any actual gate redesign that this study motivates is a separate downstream register** with its own governance.
- **Sealed-artifact safety.** Read-only against `tier6_dsr_v1/` and the Path verdict artifacts; recompute, never rewrite. The study writes only to its own new module + memo (see §6 for the hard import-only boundary).

## 3. Scope (Charlie-registered: A + B)

- **Half A — single-instrument gate.** Under what `T` / frequency can the *existing single-asset* evaluation gate confirm a modest edge? Directly answers the KILL-vs-BUILD-feasibility question and "is a shorts edge even confirmable here."
- **Half B — cross-sectional gate.** What `T` / frequency / `N` / IC would a *cross-sectional* book need to be confirmation-powered? Directly informs whether the **deferred fork** could ever work under a redesigned gate (the eventual BUILD target). Reuses Half A's MDE machinery; adds the fundamental-law IR-ceiling layer (already sketched in the feasibility spike).

## 4. Method

### 4.1 DSR bar (reuse, do not re-derive)
Reuse `tier6_dsr.py`: `sr_star` (the BLdP-2014 expected-max-of-`N*` noise hurdle) and the pass condition `deflated_z = (sr_hat − sr_star)·sqrt(T−1)/σ_denom ≥ z_pass`, with the project's locked `z_pass = 1.6449` (one-sided 95%) and `σ_denom = sqrt(1 − γ3·sr_hat + ((γ4−1)/4)·sr_hat²)` (Mertens). Independently confirmed this session (and re-confirmed by both B2 legs against code + artifact): at the current gate (`sr_star_B = 0.016968`, `T = 2527`, hourly), the pass bar is ≈ **4.65 annualized Sharpe gross**, robust to heavy tails (Gaussian 4.653 / γ4=11.3 → 4.650).

**Significance bar vs power MDE (do not conflate).** This ≈4.65 is the *just-significant* DSR bar (≈50% power at the boundary — the Sharpe a book must *exceed* to be declared significant). The §5 decision thresholds compare against the **80%-power MDE** (§4.2), which is strictly higher: at this same hourly gate ≈ **6.22 annualized**. Both ≫ 3.0, so the hourly gate is confirmation-limited either way — but **§5 always compares against the MDE, never against the 4.65 bar.**

### 4.2 Power / MDE formula (the new layer)
Under a true per-bar Sharpe `sr_true`, `sr_hat ≈ Normal(sr_true, σ_denom²/(T−1))`. Power = P(reject | sr_true) = `1 − Φ(z_pass − (sr_true − sr_star)·sqrt(T−1)/σ_denom)`. Setting power = 0.80 (`z_0.80 = 0.8416`):

> **MDE_per_bar = sr_star + (z_pass + 0.8416)·σ_denom / sqrt(T−1)**, annualized by `× sqrt(periods_per_year)`.

(The `sr_star` term is the noise-max hurdle; the `(z_pass + 0.8416)` term is the significance-plus-power increment that scales as `1/sqrt(T)` — the lever a longer OOS pulls down.)

**Denominator evaluation — solve as a FIXED POINT (B2-mandated).** `σ_denom` depends on the very `sr` being solved for, so the MDE is an *implicit* equation and MUST be solved iteratively: `mde ← sr_star + (z_pass + 0.8416)·sqrt(mertens_variance(γ3, γ4, mde)) / sqrt(T−1)` to convergence, using the *empirical* γ3/γ4. The `σ_denom ≈ 1` shortcut is acceptable **only** at the hourly gate (per-bar Sharpe ~0.066, kurtosis term negligible); at the lower-frequency **daily arms the per-bar Sharpe is 3–4× larger and the heavy-tail correction is material — +15% to +37% at γ4≈60** — so the fixed-point heavy-tail MDE is the **load-bearing** number there, not a footnote. (Both B2 legs flagged the constant-σ shortcut; the advisor quantified the daily-arm understatement, Codex specified the fixed-point solver.)

### 4.3 Half A sweep (single-instrument)
Grid: `{OOS design}` × `{rebalance frequency}` × `{N*}` × `{cost/turnover}`.
- **OOS designs / `T`:** current 105-day hourly (`T≈2527`); 1-yr / 2-yr / 3-yr **daily** (`T≈365 / 730 / 1095` at `periods_per_year = 365`, matching the project's `HOURS_PER_YEAR=8760` ⇒ 365 days/yr convention — *not* the equity 252/504 convention); plus an intermediate "moderate-turnover" point (~6–12h hold) per the advisor's note that the frequency frontier is continuous, not binary hourly-vs-daily.
- **Frequency** sets both the per-bar unit (annualization factor) and the cost drag.
- **`N*`:** {3 (minimal-grid, the prior cycles), 18 (the dead-cohort value)} — bracket the multiplicity penalty.
- **Cost/turnover:** map holding period → one-way turnover → drag at 15bps/side; report MDE in **net** terms (the gross edge required so the net clears the bar at 80% power). Turnover parameterized; sensitivity reported.
- **Moments (γ3, γ4):** estimated from existing BTC return data and the Path artifacts' moment fields; sensitivity across the observed range (γ4 ≈ 3–60, γ3 from negative to zero). **Negative skew raises the MDE** (the Mertens term is `1 − γ3·sr + …`, so γ3 < 0 increases σ_denom); the sweep reports the γ3 < 0 case, not only the favorable γ3 = 0.

### 4.4 Half B (cross-sectional)
- **IR ceiling (fundamental law):** `IR_ann ≈ IC · sqrt(BR)`, breadth `BR = N_eff · independent_bets_per_year`. Net `IR_ann = gross IR_ann − cross-sectional cost drag` (rank-book turnover × 15bps).
- **Effective-N (pre-registered, B2-pinned):** PRIMARY = equicorrelation haircut `N_eff = N / (1 + (N−1)·ρ)` (the conservative standard form; at ρ=0.8, N=20 → `N_eff ≈ 1.23`, i.e. the book is ≈ one bet); SENSITIVITY = soft form `N_eff = (1−ρ)·N + ρ` (→ ≈ 4.8). Report both; the verdict uses the primary.
- **Breadth (pre-registered, B2-pinned):** `independent_bets_per_year = rebalances_per_year · (1 − ρ_rank)`, tied to each arm's rebalance cadence, with cross-sectional rank-autocorrelation `ρ_rank ∈ [0.5, 0.9]` as the pre-registered sensitivity band. A slow/sticky rank refreshes far fewer independent bets than its nominal cadence — the single biggest IR lever (gross IR spans ≈ 0.3–2.4 across this band), so it is pinned rather than left free.
- **Verdict map:** is achievable net `IR_ann` ≥ `MDE_ann(T, frequency, N*)` (from §4.2) for any **achievable** (data-feasible **and** immutable-split-feasible) design?

### 4.5 Immutable-split feasibility check
Enumerate which longer/daily OOS windows are constructible from existing data **without** violating the immutable splits or the touch-once/no-peek discipline (current: train 2020-21+2023, holdout 2022, validation 2024, test 2025, `forward_2026`). Flag the discipline cost of each candidate OOS (e.g., a multi-year daily OOS spanning 2024–2026 reuses windows with prior designated roles → a real governance question, **surfaced not resolved** here). The achievable-design filter is applied **per arm, before** the §5 threshold call: an arm that lands in or near the BUILD band but requires reusing designated windows (e.g., daily-3yr spanning 2024 validation + 2025 test) is reported as *"BUILD-viable only under an unresolved-governance design,"* with the feasibility asterisk attached — never silently as plain BUILD/INDET.

## 5. Pre-registered interpretation rule (set BEFORE computing — anti-hindsight)

Though the computation is formula-based, the *decision thresholds* and *parameter ranges* are fixed here, before any number is produced. **These are the items requiring Charlie ratify before lock.**

- **Decision thresholds (annualized, net, compared against the 80%-power MDE of §4.2 — NOT the 4.65 significance bar — under an *achievable* design):**
  - **MDE ≤ 1.5** → the gate **can** confirm a modest edge → BUILD is viable; proceed to a confirmatory cycle (shorts or fork) under the redesigned gate.
  - **MDE ≥ 3.0** → the single-instrument frame is **fundamentally confirmation-limited** → a strategic finding (more consequential than which signal to try next); the gate, not the alpha source, is the binding constraint for *confirmation*.
  - **1.5 < MDE < 3.0** → INDETERMINATE band; report the curve and the achievable-design frontier; defer the call to Charlie.
- **Parameter ranges (pre-committed):** IC ∈ [0.02, 0.05]; nominal N ∈ [15, 25] (data-feasible from ~2021); ρ ∈ [0.7, 0.9]; **`N_eff` = equicorrelation `N/(1+(N−1)ρ)` (primary)**, soft form as sensitivity; **`ρ_rank` ∈ [0.5, 0.9]** (breadth haircut); one-way turnover ∈ [0.3, 0.7] per rebalance; γ4 ∈ [3, 60]; **γ3 from negative to zero**; `z_pass = 1.6449`, `z_power = 0.8416`.
- **Rationale for the thresholds:** ~1.5 is a *good but realistic* documented crypto-factor net Sharpe; ~3 exceeds what any realistic single-factor book delivers net, so a gate requiring it cannot confirm *any* realistic edge. Pre-registering them *before* computing is genuine anti-hindsight discipline — not against overfitting (the computation is formula-based), but against **post-hoc threshold selection** (choosing the line to match the computed MDE after seeing it). The thresholds remain Charlie's to ratify or adjust.

## 6. Deliverable

- A small, reproducible analytical module (proposed: `backtest/eval_power.py`) reusing `tier6_dsr.py` **pure primitives only** (`sr_star`, `mertens_variance`, `deflated_z`) + a results memo (proposed: `docs/phase5/EVAL_GATE_POWER_STUDY.md`). **Hard boundary (B2, Codex):** the module MUST NOT call `evaluate_cohort()` (which defaults `write=True` / `out_dir=DEFAULT_OUT_DIR` and would write the sealed `tier6_dsr_v1/` directory); a `CONTRACT BOUNDARY` marker in `eval_power.py` documents the import-primitives-only rule.
- **Headline verdict** in the memo: the (fixed-point, heavy-tail) MDE curve over the sweep, the achievable-design frontier, and the pre-registered-threshold call (BUILD-viable / confirmation-limited / INDETERMINATE) for **both** Half A and Half B.
- A one-line decision mapping to the next register-event (see §7).

## 7. Decision → next register mapping

- **A says BUILD-viable** (some achievable single-instrument design clears MDE ≤ 1.5): a shorts (or other single-asset) confirmatory cycle becomes worth running *under that redesigned gate* → next register = the gate-redesign (governance for the immutable splits) + the confirmatory cycle.
- **B says fork confirmation-viable** (achievable cross-sectional design clears the bar): the fork-deferral is partly lifted → the fork re-enters as a *candidate* register under the redesigned gate.
- **Both confirmation-limited (under the achievable OOS designs studied):** the single-instrument evaluation frame cannot confirm a realistic edge *at any achievable OOS length/frequency* → a project-level strategic conclusion (the gate, not the alpha source, is the binding constraint for confirmation); reframes the whole program (e.g., accept-the-negative, or a fundamentally different evaluation/instrument design). **Scope caveat:** a much longer daily OOS (5–10yr) would mechanically pull the MDE under 1.5, but is not achievable under the immutable splits — so the binding statement is "confirmation-limited *under achievable designs*," not in the abstract.
- **On-chain flow** remains last regardless.

## 8. What this study is NOT

Not a gate redesign (only measures what redesign *would* buy). Not a backtest. Not a signal cycle. Not a data-ingestion or funding-model build. Not a modification of `config/environments.yaml` or any sealed artifact. No peeking at held-out performance. No call to `evaluate_cohort()` or any writer into the sealed directory.

## 9. Risks & assumptions (disclosed)

- IC range, turnover, `N_eff`/ρ, and `ρ_rank`/breadth are *assumptions*, not measured in-repo (no multi-asset panel exists). The study reports sensitivity across the pre-registered ranges rather than a point estimate; Half B's verdict is a *ceiling* analysis, not a measured edge.
- The power MDE (§4.2) is solved as a **fixed point** in the Mertens denominator. The "heavy tails move the bar < 0.1%" result from this session applies to the *hourly significance bar* only; at the **daily arms** the heavy-tail correction is **material (+15% to +37%)** and is the load-bearing number — the study reports the heavy-tail-adjusted (fixed-point) MDE as primary there, with the Gaussian as a reference. Negative skew raises the MDE further.
- The immutable-split feasibility check surfaces a governance question (reusing designated windows for a longer OOS) it does **not** resolve; resolving it is the downstream register's job.
- The ~1.5 / ~3 thresholds are judgment lines; pre-registering them here is the anti-hindsight safeguard, but they are Charlie's to ratify or adjust.

## 10. Review plan

1. Spec self-review (placeholder / consistency / scope / ambiguity). **Done.**
2. **2-leg B2 (Codex + advisor): COMPLETE 2026-06-02 — SHIP-WITH-CHANGES; nine findings folded in (fixed-point MDE; daily-T 365/730/1095; significance-vs-MDE framing; Half-B `N_eff`+breadth pinned; per-arm feasibility filter; §5 rationale wording; §7 achievable-design qualifier; import-only safety boundary; negative-skew note).** No CRITICAL/BLOCK; numbers cross-corroborated against `tier6_dsr.py` + the Path D artifact.
3. Charlie reviews this revised spec; ratifies (or adjusts) the §5 pre-registered interpretation rule.
4. On ratify: implement the analytical module + memo (TDD on the fixed-point power/MDE solver against hand-computed cases), then run, then a result-2-leg-B2, then Charlie's binding read.
