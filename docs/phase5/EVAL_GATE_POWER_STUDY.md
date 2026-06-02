# Evaluation-Gate Power Study — results memo

- **Date:** 2026-06-02 UTC
- **Spec:** [`docs/superpowers/specs/2026-06-02-evaluation-gate-power-study-design.md`](../superpowers/specs/2026-06-02-evaluation-gate-power-study-design.md) (§5 interpretation rule Charlie-ratified, frozen pre-run)
- **Module / tests / data:** [`backtest/eval_power.py`](../../backtest/eval_power.py) · [`tests/test_eval_power.py`](../../tests/test_eval_power.py) (29 passed) · `data/eval_gate_power_study/results_v1.json`
- **Status:** analytical result + **Monte-Carlo empirical validation** ([`backtest/eval_power_mc.py`](../../backtest/eval_power_mc.py), `data/eval_gate_power_study/mc_power_v1.json`), **both** 2-leg-B2'd (Codex + advisor) **SOUND**. **Binding read: Charlie registered FREEZE (accept-the-negative), `p` low, 2026-06-02** — the §5 classification is *mechanical*; the strategic FREEZE is the PI's.
- **Provenance discipline:** purely analytical / read-only. No data, no backtest, no signal, no split change, no peek; sealed `tier6_dsr_v1/` SHA-256 byte-untouched throughout; no `evaluate_cohort()` call (import-primitives-only, `CONTRACT BOUNDARY` in the module).

## The question

> Can the project's evaluation frame **confirm** a modest (~1–1.5 ann Sharpe) edge at 80% power under any **achievable** design (data-feasible AND within the immutable splits), or is the gate itself a confirmation bottleneck — a candidate **second binding constraint** alongside the alpha source?

## Verdict (mechanical, per the pre-registered §5 rule)

**CONFIRMATION-LIMITED on both halves, under all achievable designs.** No achievable single-instrument or cross-sectional design clears the 80%-power MDE down to the BUILD line (≤ 1.5 ann Sharpe); every achievable arm sits at the confirmation-limited bin (≥ 3.0).

## Method (recap — full detail in the spec / module)

The DSR-FWER pass test (`backtest/tier6_dsr.py`: `sr_star` + the Mertens-deflated `deflated_z ≥ Z_PASS=1.6449`) is inverted to the **80%-power minimum-detectable Sharpe (MDE)**, solved as a **fixed point** in the Mertens denominator (heavy-tail-aware): `MDE_per_bar = sr_star + (Z_PASS + 0.8416)·σ_denom(MDE)/√(T−1)`, annualized `× √(periods_per_year)`. Swept over OOS design × rebalance frequency × N\* × return moments × cost. The **significance bar** (≈50% power, e.g. hourly 4.65) is distinct from and below the **80%-power MDE** (e.g. hourly 6.22); **§5 compares the MDE**. Half B adds the fundamental-law IR ceiling `IR_ann ≈ IC·√(N_eff·independent_bets)` with the equicorrelation `N_eff = N/(1+(N−1)ρ)` primary.

## Half A — single-instrument gate (achievable arms, observed moments)

| Arm | MDE (ann, 80% power) | §5 bin |
|---|---|---|
| `hourly_105d` · N\*=1 (no-multiplicity floor) | **4.63** | confirmation-limited |
| `hourly_105d` · N\*=3 | 6.22 | confirmation-limited |
| `hourly_105d` · N\*=18 | 8.10 | confirmation-limited |
| `daily_105d` · N\*=1 | 4.97 | confirmation-limited |
| `daily_105d` · N\*=3 | 6.87 | confirmation-limited |
| `daily_105d` · N\*=18 | 9.25 | confirmation-limited |

The two cleanly-achievable OOS designs are `hourly_105d` (the current `forward_2026` gate) and `daily_105d` (a daily book over the same ~105-day window). **The softest achievable MDE is 4.63** — the most-favorable case (single pre-registered hypothesis, no multiplicity) — still **3.1× the BUILD line and 1.5× the confirmation-limited line.**

**The sharpened finding.** The *only* arm anywhere in the 40+ cell grid that reaches **BUILD-viable** is `daily_3yr · N\*=1` (MDE **1.44**) — and it is **doubly out of reach**: it is **governance-blocked** (a 3-yr daily OOS spans the 2024 validation + 2025 test windows, violating the immutable touch-once discipline) **and** it requires committing to a **single pre-registered hypothesis** (N\*=1). BUILD-viability under this frame requires *both* spending the held-out test set *and* abandoning multiplicity — neither alone suffices.

## Half B — cross-sectional gate (IR ceiling)

The best achievable cross-sectional net IR over the pre-registered grid (IC∈[0.02,0.05], N∈[15,25], ρ∈[0.7,0.9], ρ_rank∈[0.5,0.9], turnover∈[0.3,0.7], daily rebalance):

- **Primary** (equicorrelation `N_eff`, which collapses N=25,ρ=0.7 → `N_eff≈1.40` — the book is ≈ one bet): best net IR ≈ **0.25**.
- **Soft-form sensitivity** (generous `N_eff=(1−ρ)N+ρ`): best net IR ≈ **1.39**.
- Achievable gate MDE benchmark (softest achievable, `hourly_105d` observed): **6.22**.

**Best achievable cross-sectional net IR (0.25 primary / 1.39 generous) ≪ 6.22 → does not clear.** The cross-sectional fork is confirmation-limited on the achievable gate, even under the generous N_eff.

## Robustness / what does NOT move the verdict

- **Cost convention is irrelevant to the Half-A verdict (mechanically confirmed, both B2 legs):** `classify_mde()` reads only the *net* MDE; the cost block (σ_ret_ann=0.60, ×2 round-trip, worst-case `rebalances=ppy` → an illustrative hourly gross-required ~28) is reported but never feeds the classification. **The 6.22 is the cost-independent noise hurdle; cost only raises the gross-required edge on top.** (Cost *does* enter Half B's net IR, but the verdict there rests on the *best* arm at lowest turnover, which survives.)
- **Heavy tails:** the fixed-point MDE is +21%/+28% above the Gaussian on the daily-1yr γ4=60 arms (spec band confirmed); negative skew raises it further. The achievable-arm verdict holds under Gaussian, observed, γ4=60, and γ3<0 moments.
- **Multiplicity:** bracketed N\*∈{1,3,18}; even N\*=1 (no penalty) leaves every achievable arm confirmation-limited.

## Empirical validation — Monte-Carlo gate-power (the projection, now measured)

The §5 verdict above is an *analytical projection* (a closed-form inversion of the gate's power). Per the PI's caveat (*"需要真实跑才知道"* — a real run is needed to know the concrete result), it was **empirically validated** by measuring the live `tier6_dsr` gate's actual detection (pass) rate vs a *known injected true Sharpe*, via Monte-Carlo ([`backtest/eval_power_mc.py`](../../backtest/eval_power_mc.py); M=5000; advisor-design-approved *after* it caught a fatal DGP bug; result 2-leg-B2 SOUND). Two DGP arms: **Arm 1** iid Gaussian (closed-form self-consistency / no-code-bug check); **Arm 2** stationary block-bootstrap of the *full* real BTC 1h return distribution (the load-bearing real-data test).

| arm | N\* | detect@0 | @just-sig | **@MDE** | **@deployable 1.5** |
|---|---|---|---|---|---|
| iid | 1 | 4.8% | 48.7% | **80.0%** | **19.8%** |
| iid | 3 | 0.5% | 49.9% | **80.9%** | **4.4%** |
| real-BTC | 1 | 5.1% | 50.5% | **79.7%** | **21.3%** |
| real-BTC | 3 | 0.7% | 52.1% | **79.2%** | **5.3%** |

(0 degenerate sims; all four MDE cells inside the pre-registered [77,83]% band.)

- **The wall is now MEASURED, not projected:** a genuinely-existing deployable ~1.5 Sharpe edge clears the live gate only **~20% (N\*=1) / ~5% (N\*=3)** of the time.
- **Not a fat-tail / autocorrelation artifact:** the real-BTC arm matches the iid arm at the MDE (79.2–80.9% on both). The closed-form iid-Mertens MDE holds on real return structure because real *return* autocorrelation is tiny (lag-1 = −0.021); vol-clustering (+0.163 in squared returns) is strong but does not enter the Sharpe-estimator variance (the mean is linear in returns). The bootstrap arm carries heavy tails (realized γ4≈30) **well in excess of** the analytical anchor (γ4=11.3) and still lands at ~80%, so the heavy-tail objection is empirically closed.
- **The measured wall is an UPPER BOUND on power = LOWER BOUND on the true wall**, on two compounding (both conservative) grounds: (a) the MC injects a *stationary* constant Sharpe — a real *non-stationary* edge of the same nominal Sharpe is detected no more often; (b) the MC injects a *dense* return every bar, but the real Path A–D books traded *sparsely* (9–55 trades), so their effective T is far smaller and their wall even higher.
- The N\*=3 null detection (<1%) confirms the DSR multiplicity hurdle makes the gate *strictly more conservative* than a raw 5% test under the null.

**Two bugs were caught + fixed + regression-guarded en route** (the gates working as designed): the advisor's *design* review caught a fatal DGP variance-collapse *pre-run*; a diagnostic then caught a bootstrap source-window bug (sampling only the 2020 COVID window, halving the recovered Sharpe). Both fixed; pinned by the `sd(sr_hat)≈1/√(T−1)`, injected-Sharpe-recovery, and resampler↔primitive equivalence tests.

## Conclusion (mechanical) → for the binding read

Per spec §7, with the "both confirmation-limited" branch realized: **within the splits this project is committed to, no achievable OOS confirms a modest ~1–1.5 Sharpe edge** — the evaluation gate, not only the alpha source, is a binding constraint *for confirmation*. This is now **empirically grounded** (the Monte-Carlo measures a real 1.5-Sharpe edge clearing the live gate only ~20% / ~5% of the time), not merely an analytical projection — and the measured detection is a conservative *upper bound* on the true power. This is bounded by "**under achievable OOS designs**": a 5–10-yr daily OOS would mechanically pull the MDE under 1.5 (the governance-blocked `daily_3yr` 1.44 already shows the trend), but is not achievable under the immutable splits. The standing thesis ([[alpha-source-is-the-binding-constraint-not-data-methodology]]) gains a **second binding constraint**: even *with* an edge, this frame could not confirm it.

The decision this informs (spec §7) — gate-redesign + a confirmatory cycle, vs accept-the-negative, vs a different evaluation/instrument design — is the **PI's binding read and a fresh register**, not decided here.

## Review provenance

- Design spec: 2-leg B2 (Codex + advisor) SHIP-WITH-CHANGES; 9 findings folded pre-run.
- Analytical result: 2-leg B2 (Codex + advisor) — both **SOUND / SOUND-WITH-CAVEATS**, headline numbers reproduced bit-for-bit against the artifact + `tier6_dsr.sr_star`; no CRITICAL. Corrections folded: `daily_1yr` achievability bug → `achievable=False` (it strengthened the verdict); added the `daily_105d` clean-daily arm + the N\*=1 no-multiplicity floor; `sigma_denom`↔`mertens_variance` equivalence pin (caught + fixed my own arg-order error) + NaN-guard parity; Half B re-benchmarked against an achievable MDE.
- MC empirical validation: design **advisor-APPROVE-WITH-CHANGES** (caught a fatal DGP variance-collapse pre-run); result 2-leg B2 (Codex + advisor) — both **SOUND** (Codex all six checks PASS; advisor all criteria PASS, mechanism verified, four independent anchors agree at ~80%). A second bug (bootstrap source-window) caught by diagnostic + fixed; both bugs regression-guarded. Two advisor memo-precision additions folded (heavy-tail-attenuation phrasing; dense-T-vs-sparse-T upper-bound layer).

## Assumptions / limits (disclosed)

- Half B IC/ρ/ρ_rank/turnover are *assumptions* (no multi-asset panel exists); Half B is a **ceiling analysis**, not a measured edge.
- `N*=1` was added post-§5-ratification as a B2-recommended *most-favorable* robustness floor (it can only make BUILD easier; it stays confirmation-limited) — disclosed, flagged for the PI.
- The immutable-split feasibility is *surfaced, not resolved*: any actual gate redesign (e.g. a longer daily OOS) is a separate downstream register with its own no-peek governance.
- "Observed" moments (γ3≈0.14, γ4≈11.3) are the Path D H1 strategy's per-bar moments (a real-strategy anchor); the Gaussian/γ4=60/neg-skew arms bracket the range.
