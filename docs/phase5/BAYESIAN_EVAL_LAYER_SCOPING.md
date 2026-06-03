# Continuous-Evidence / Bayesian Evaluation-Layer Scoping — results memo

- **Date:** 2026-06-02 UTC
- **Spec:** [`docs/superpowers/specs/2026-06-02-bayesian-eval-layer-scoping-design.md`](../superpowers/specs/2026-06-02-bayesian-eval-layer-scoping-design.md) (§5 decision rule Charlie-ratified, frozen pre-analysis).
- **Module / tests / data:** [`backtest/eval_layer_scoping.py`](../../backtest/eval_layer_scoping.py) · [`tests/test_eval_layer_scoping.py`](../../tests/test_eval_layer_scoping.py) (18 passed) · `data/eval_gate_power_study/eval_layer_scoping_v1.json`.
- **Status:** analysis complete; headline verdict below. **The verdict was CORRECTED from DON'T-BUILD to CONDITIONAL during the result 2-leg B2** (Codex caught a verdict-critical bug in SV6 — see "Correction provenance"). Result-B2 of the correction pending; the binding go/no-go read is the PI's.
- **Provenance discipline:** purely analytical / read-only. No data spent, no holdout touched, no strategy run on held data, no peek; the 12 cohort Sharpes are read from the sealed Path verdict artifacts; sealed `tier6_dsr_v1/` SHA-256 byte-unchanged throughout; no `evaluate_cohort()` call (AST-checked).

## The question (spec §1)

> Can a continuous-evidence / Bayesian evaluation layer **legitimately improve the deploy decision** for a modest (~1–1.5 ann Sharpe) BTC edge — raise confirmation power, or improve the decision under low power — **WITHOUT spending the 2024/2025 holdout and without a garden-of-forking-paths inflation** — by enough to justify building it?

## Headline verdict (per the §5 map): **CONDITIONAL-BUILD** — go pending a named estimand study

Most of the design space is closed: M1 (sizing) and M3 (cross-cycle pooling) are killed; M2/M4/M5 add only honesty or time, not fixed-`T` power. **But M6 — change the estimand from Sharpe to a directional / sign / proper-scoring statistic — plausibly *does* raise confirmation power at BTC's heavy tails** (the sign test's efficiency is at near-parity at the strategy-moment kurtosis γ4≈11.3 [ARE 0.994] and *overtakes* the Sharpe test at the higher kurtosis of raw hourly returns; crossover γ4≈11.84, and the Student-t used is the *conservative* heavy-tail family). The catch that keeps it CONDITIONAL rather than BUILD: a directional power gain confirms a **median/directional shift**, which is **not** the same as a deployable **Sharpe** edge (a high hit-rate with negative skew has a *negative* Sharpe — "picking up pennies"). Whether the power gain translates into confirming a *deployable* edge needs a quantification beyond this scoping's inline budget → **§5 CONDITIONAL branch (i): name the study as the next register.**

## Per-mechanism classification (Axis-1 × Axis-2 + per-mechanism clause)

| Mechanism | SV result | Axis-1 (power) | Axis-2 (decision-value) | Clause | Contribution |
|---|---|---|---|---|---|
| **M1** posterior→sizing | `f*`=2.5, P(SR≤0)=**21%** | `no-power-gain` | `negative`→`modest` (capital-danger) | — | kill |
| **M2** Bayesian sequential | seq detect **0.001** ≪ fixed **0.205** | `only-via-time` | `modest` | — | not BUILD/COND |
| **M3** pool across cycles | posterior **−0.26 / −1.60** ≪ deploy line | `backfires` | `none`/`negative` | — | kill |
| **M4** skeptical-prior report | posterior < y always (only tightens) | `no-power-gain` | `modest` (honesty) | pass | not BUILD/COND |
| **M5** always-valid / e-value | e=**1.38** vs 20 needed; ~**2.66 yr** to threshold | `only-via-time` | `modest` (nothing to monitor now) | pass | not BUILD/COND |
| **M6** change-the-estimand | sign-test ARE **crosses 1 at γ4≈11.84**; strategy anchor γ4≈11.3 → **near-parity (0.994)**, ≥1.10 by γ4=60 (raw hourly ≫ crossover) | **`raises-power-legitimately` (plausibly)** | conditional | pass | **→ CONDITIONAL** (deployment-relevance pending) |
| **M7** within-batch EB | shrink 0.224; `in_scope_now=False` | conditional / out-of-scope | conditional | — | out-of-scope (not a kill) |

**Verdict-map application:** BUILD requires a mechanism *definitively* `raises-power-legitimately` (clause-passing). M6 is *plausibly* there but its **legitimacy for confirmation hinges on the deployment-relevance question** (a directional power gain ≠ a confirmed deployable Sharpe edge) — a quantification exceeding the A⁺ inline budget. That is exactly **§5 CONDITIONAL branch (i)** → **CONDITIONAL-BUILD**, naming the study. (M5's `modest`-vs-`high` hinge is now **not load-bearing** — M6 drives the verdict regardless.)

## The SV1–SV7 numbers

- **SV6 (verdict-critical) — directional estimand plausibly RAISES power at BTC's heavy tails (corrected).** The Sharpe-DSR test's power is ~kurtosis-independent at a modest per-bar edge (its Mertens correction is O(sr²)≈0) → power **0.201** at 1.5 ann. The directional/sign test's efficiency vs the mean/Sharpe test is **(2·f(0))²** with f(0) the unit-variance return density at zero: **2/π = 0.637 at Gaussian**, rising **past 1.0 at raw kurtosis ≈ 11.84** (the median beats the mean under heavy tails — the classic robust-statistics result). At the strategy's observed γ4 ≈ 11.31 the directional estimand is at **near-exact parity** (ARE 0.994, power 0.200); at the higher raw kurtosis typical of hourly BTC returns (γ4 ≫ 12) it **overtakes** (ARE 1.08 at γ4=30, 1.10 at γ4=60; sign power 0.212 at γ4=60). **So M6 is not refuted as a power lever.**
  - **The deployment caveat (why CONDITIONAL not BUILD):** the sign/directional test confirms a **median shift** (wins > 50% of bars), which is *not* a deployable **Sharpe** edge. A negative-skew strategy (win small often, lose big rarely) can have a high hit-rate **and** a negative Sharpe; the 15bps cost gate compounds this. So a directional gate's power gain may confirm a non-deployable edge. Resolving whether the gain holds for the **deployment-relevant** quantity (directional accuracy *jointly with* positive net-of-cost risk-adjusted return / non-adverse skew) is the named next-register study.
- **SV3 (M3) — pooling backfires, robust.** Cohort mean −2.5467; posterior −0.26 (raw τ²=4.53) to −1.60 (de-noised τ²=1.06), both ≪ the 1.0 deploy line.
- **SV2 (M2) — no free acceleration.** Anytime-valid mixture e-process detects the true 1.5 edge over [0,T] only ~0.1% vs 20.5% fixed-horizon at T.
- **SV5 (M5) — only-via-time.** e ≈ 1.38 over the window vs ln(20)≈3.0 nats needed; the e-value crosses its threshold only after ~2.66 more years of hourly tape.
- **SV1 (M1) — capital-danger.** `f*`=2.5×, P(true Sharpe ≤ 0)=21% at se_ann=1.86.
- **SV4 (M4) — honesty, not power.** A skeptical prior only *lowers* the posterior below the data point.
- **SV7 (M7) — conditional.** Within-batch EB shrinkage 0.224 is legitimate but in-scope only if a *future* candidate batch is registered.

## Decision → next register (spec §7)

**CONDITIONAL-BUILD → name the study (a fresh Charlie register, NOT executed here):** a directional / Brier / proper-scoring **estimand-power-vs-deployability study**. The study must pre-register: (a) a **minimum *absolute* power-improvement** threshold, not merely "overtakes parity" — the absolute gain is only a few points near the ~20% floor at the strategy anchor (B2 [MED]); (b) the **deployment-relevance** test — does the directional power gain confirm a *deployable* edge (jointly: directional accuracy AND positive net-of-15bps Sharpe / non-adverse skew), or merely a hit-rate that skew can divorce from Sharpe?; (c) **DSL-expressibility** — can the engine even express a directional/Brier gate?; (d) the **runs-test / serial-dependence** estimand (a persistence statistic answers a genuinely different question — the residual M6 channel); (e) re-pass the two-prong anti-motivated clause for the specific estimand. (Context: the Student-t crossover γ4≈11.84 is the *conservative* heavy-tail family; under peaked-body families the directional advantage is larger, so the lead is if anything understated.) **If the study confirms a deployment-relevant power gain → a separate BUILD register (a directional/Brier evaluation gate); if not → DON'T-BUILD earned.** Per anti-pre-emption, this analysis authorizes nothing downstream.

## Non-foreclosing scope

- **Open (the CONDITIONAL path):** M6 (change-the-estimand) — the named study above. This is the live lead.
- **Closed as build-now power levers:** M1 (capital-danger), M3 (backfires). M2/M4/M5 add only time/honesty (recommended as *ingredients* for any future re-entry cycle's evaluation design, not standalone builds). M7 in-scope only with a future candidate batch.
- **The 2024/2025 holdout stays UNSPENT.** The freeze's other deferred-open paths are untouched.

## Correction provenance (the result B2 working as designed)

The first-pass verdict was **DON'T-BUILD**, resting on an SV6 that concluded the directional estimand has *lower* power (ARE always ≈ 2/π; crossover kurtosis ≈ 8892). **The result 2-leg B2 caught this as verdict-flipping:** Codex's independent recompute found the sign-vs-mean ARE crosses 1 at raw kurtosis ≈ **11.8** (ARE 1.10 at γ4=60), not 8892. The bug: the first SV6 modeled the heavy-tail effect on the *Sharpe* side (Mertens σ_denom, ∝ sr² ≈ 0 at a modest edge) but held the *sign test's* density `f(0)` at its **Gaussian** value — missing that the median/sign estimator gains efficiency over the mean under heavy tails. The fix models `f(0)` via a kurtosis-matched Student-t; the author independently re-derived the corrected crossover (≈ 11.84) before adopting Codex's finding. The advisor leg rated SV6 SOUND but *disclosed* it had not verified the ARE against a primary source and named Codex better-positioned — the 2-leg routine caught what one leg missed.

## Review provenance

- Design spec: 2-leg B2 in two passes (design-point + written-spec); §5 rule Charlie-ratified.
- Analysis: 18 tests green; every headline number hand-derivable. **First-pass result B2: Codex `has-BLOCK` (SV6) — verified correct + fixed (verdict DON'T-BUILD → CONDITIONAL); advisor `SOUND-WITH-CAVEATS`.** Result-B2 of the correction pending.

## Assumptions / limits (disclosed)

- **The corrected SV6 uses a Student-t model** for the heavy-tail density `f(0)`; the exact crossover kurtosis is distribution-family-dependent, but the qualitative result (crossover at *realistic* γ4 ~ 10–12, BTC at/above it) is robust across heavy-tailed families (Laplace ARE=2 at γ4=6).
- **The deployment-relevance question (directional power ≠ deployable Sharpe) is the load-bearing reason for CONDITIONAL** and is explicitly deferred to the named study — not resolved here.
- The SV2 MC uses an iid-Gaussian DGP + a single mixture-e construction (τ matched to the alternative — generous to the sequential test).
- M7's IC/τ are illustrative (no future batch exists); a conditional classification, not a measured edge.
