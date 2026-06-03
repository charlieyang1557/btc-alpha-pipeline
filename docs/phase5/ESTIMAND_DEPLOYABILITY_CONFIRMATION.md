# Estimand-Deployability Confirmation — results memo (minimal-confirmation run)

- **Date:** 2026-06-02 UTC
- **Spec:** [`docs/superpowers/specs/2026-06-02-estimand-deployability-confirmation-design.md`](../superpowers/specs/2026-06-02-estimand-deployability-confirmation-design.md) (decision rule revised per the design-point 2-leg; pre-registered before compute).
- **Module / tests / data:** [`backtest/eval_estimand_deploy.py`](../../backtest/eval_estimand_deploy.py) · [`tests/test_eval_estimand_deploy.py`](../../tests/test_eval_estimand_deploy.py) (7 passed) · `data/eval_gate_power_study/estimand_deploy_confirm_v1.json`.
- **Status:** analysis complete; verdict below. Result 2-leg B2 pending; binding read is the PI's.
- **Provenance discipline:** purely analytical / read-only. No real strategy run, no engine, no data, no holdout, no peek; sealed `tier6_dsr_v1/` SHA-256 byte-unchanged; no `evaluate_cohort()` (AST-checked).

## The question (spec §1)

> Does a directional / sign / proper-scoring evaluation estimand's heavy-tail statistical-power advantage over the Sharpe-DSR gate translate into confirming a **DEPLOYABLE** BTC edge (net-of-15bps Sharpe in the ~1.0–1.5 band, non-adverse skew) — or is it confined to the non-deployable skew-divorced zone and eaten by the multiplicity cost of a second gate?

## Verdict (per the pre-registered §3 rule): **DON'T-BUILD**

The B-iii M6 lead is closed as an **earned negative**: a directional/Brier evaluation gate is **not worth building**. All four pillars confirmed; no surprise (unlike B-iii, which flipped — the *run* preserved that chance and it did not fire here).

## The four pillars (all read-only, hand-verified)

- **P1 — Skew-divorce (confirmed).** A unit-variance skew-normal (γ3=−0.96) shifted to **Sharpe = −0.02** has hit-rate **P(up)=0.566** → a sign test fires at **z=6.6** while the Sharpe gate correctly does not. Over the negative-skew grid the directional hit-rate reaches high values *at net-Sharpe ≤ 0*, so the directional gate's "extra" firing **concentrates in the non-deployable zone**. The model uses the explicit standardized median (F(0)), not a kurtosis-only proxy (the design-point fix).
- **P2 — Deployable-band net benefit ≪ tripwire (confirmed).** The net detection benefit of *adding* a standalone directional gate (FWER-preserved at 2N\*) over the Sharpe gate alone, maximized over the **entire** deployable grid (Sharpe ∈ {1.0,1.25,1.5} × γ4 ∈ {11.3,30,60,100} × N\* ∈ {3,18,39}), is **+2.08pp** — at the *most generous* corner (1.5 Sharpe, γ4=100, N\*=3, independence-assumed OR). That is **≪ the 10pp tripwire** (which is ~9× any achievable gain). The directional advantage is real but trivially small where it is deployable.
- **P3 — Multiplicity inflates the bar (confirmed).** A second gate doubles the test family N\*→2N\*; the one-sided Bonferroni z rises **2.773 → 2.991 (+0.218)** at N\*=18 — a power cost already netted into P2 (and P2 is still positive only because the independence-OR is generous).
- **P4 — Runs-test is a confirmation-layer category error (confirmed).** An AR(1) raw-return series (ρ=0.32) is ~Sharpe-blind (raw per-bar Sharpe −0.009) and iid-sign-blind, **but a momentum strategy on it has P&L Sharpe +0.265** → the serial-dependence edge *already* shows in STRATEGY P&L, which the Sharpe-DSR gate scores. A runs-test is therefore a *signal-discovery* tool (the alpha-generation layer Paths B/A/C/D already mined), not a confirmation-gate estimand that catches deployable edges the Sharpe gate misses.

## Decision-rule application (spec §3)

DON'T-BUILD ⟺ directional advantage in the non-deployable zone (P1 ✓) **AND** deployable-band gain after 2N\* < 10pp (P2 ✓: 2.08pp) **AND** runs-test confirmation-layer-inert (P4 ✓). All three hold → **DON'T-BUILD**. The surprise branch (a deployable region with ≥10pp net gain) did **not** fire.

## What this closes / non-foreclosing

- **Closes:** the B-iii **M6 lead** (change-the-estimand) as a path to a deployable confirmation gain — earned negative. Combined with B-iii's M1/M2/M3/M4/M5 results, the **continuous-evidence / Bayesian / alternative-estimand evaluation-layer family is now exhausted as a build-now confirmation-power lever.**
- **Does NOT close:** the directional/sign estimand remains a legitimate *honesty-reporting* annotation (it just isn't a deployable-confirmation gate); the freeze's *other* deferred-open paths (fresh-OOS accrual = the literal time lever; structurally-different frames — short legs, continuous sizing, on-chain, cross-sectional rank) are **untouched**. The 2024/2025 holdout stays **UNSPENT**.
- The empirical version (run a directional gate on real candidates) is moot — the analytical result shows no deployable region to chase.

## Review provenance

- Design point: 2-leg B2 (Codex + advisor) reshaped the study to this minimal confirmation (skew-divorce + multiplicity reproduced; deployment-definition inverted to band-primary; complementary→standalone-2N\*; runs-test reframed via F1).
- Analysis: 7 tests green; P1 (z=6.6), P3 (+0.218), P4 (P&L Sharpe 0.265) reproduce the design-point previews; P2 (2.08pp max) computed over the full deployable grid. Result 2-leg B2 pending.

## Assumptions / limits (disclosed)

- **Over-correction guard:** the DON'T-BUILD follows the advisor's three CONDITIONAL leans across B-iii; the minimal *run* (not accept-without-run) was the guard — the four pillars are computed, and the verdict map left the surprise branch genuinely reachable; it did not fire.
- P2's combined detection uses an **independence-OR** (generous to BUILD; real Sharpe/sign gates positively correlate → even less benefit) — so 2.08pp is an *upper bound* on the directional gate's net benefit.
- The skew-normal is a model family; the skew-divorce mechanism (median-above-mean under negative skew) is family-robust.
- **P4 was the softest pillar** at design-point (advisor-inferred the gate scores strategy P&L); the AR(1) illustration confirms a serial edge manifests in P&L Sharpe — consistent with the gate's `holdout_sharpe` being a strategy-P&L Sharpe.
