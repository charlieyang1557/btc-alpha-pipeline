# Estimand-Deployability Confirmation — design spec (minimal-confirmation run)

- **Date:** 2026-06-02 UTC
- **Register context:** the B-iii eval-layer scoping cycle (sealed `ef37233a`) reached **CONDITIONAL-BUILD** with M6 (change the estimand from Sharpe to a directional/sign/Brier statistic) as the live lead, gated on a deployment-relevance question. Charlie registered the recommended **estimand-deployability study**; a 2-leg design-point review (Codex + advisor) converged that the verdict is **near-foreseeable DON'T-BUILD** and is reachable *cheaply* via four determinate analytical pillars — so Charlie registered a **minimal-confirmation run** (not a full grid-sweep).
- **Status:** DESIGN / pre-registration (anti-hindsight lock — committed BEFORE any compute). Decision rule revised per the 2-leg review; the run, then a result 2-leg-B2, then Charlie's binding read.
- **Purpose:** confirm (or refute, B-iii-style) that a directional/Brier evaluation gate is **NOT worth building** — i.e. its heavy-tail power advantage does not translate into confirming a *deployable* edge. Allowed to surprise (a deployable region with a real net gain → CONDITIONAL/BUILD).
- **Boundary (Charlie-ratified "A"):** pure-analytical + read-only code-inspection. NO real strategy run, NO engine execution, NO data, NO holdout spend, NO peek. Closed-form + tiny synthetic checks reusing `backtest/eval_layer_scoping.py` primitives; sealed `tier6_dsr_v1/` SHA-256 verified byte-unchanged.

## 1. The question

> Does a directional / sign / proper-scoring evaluation estimand's heavy-tail statistical-power advantage over the Sharpe-DSR gate translate into confirming a **DEPLOYABLE** BTC edge (net-of-15bps annualized Sharpe in the ~1.0–1.5 band, non-adverse skew) — or is the advantage confined to the non-deployable, skew-divorced zone and eaten by the multiplicity cost of a second gate?

## 2. The four pillars (each confirmed by a minimal read-only computation)

- **P1 — Skew-divorce (the core).** A negatively-skewed return distribution has median > mean, so P(up) (hit-rate) can be high even at net-Sharpe ≤ 0. Confirm: over a (per-bar Sharpe δ, skew γ3, kurtosis γ4) grid, the region where a directional gate fires (P(up) materially > 0.5) but net-Sharpe ≤ 0 is large, and the directional advantage over the Sharpe gate **concentrates in the non-deployable zone**. *Design-point preview (Codex): skew-normal γ3=−0.96, Sharpe −0.02, P(up)=0.566 → sign-test z=6.6 fires while the Sharpe gate correctly does not.*
- **P2 — Tiny deployable-region gain.** At the deployable region (realistic BTC γ4≈11.3, δ for a ~1.0–1.5 Sharpe), the sign-test ARE is ≈0.994 (near-parity) → the absolute directional power lift over Sharpe is **~1 percentage point** near the ~20% floor — far below the ≥10pp tripwire.
- **P3 — Multiplicity eats the gain.** A standalone directional gate *added* to the Sharpe-DSR gate doubles the test family N\*→2N\* (a candidate advanceable by either gate). Confirm the z-threshold increase + the power cost (*Codex preview: N\*=18 Bonferroni z 2.773→2.991, +0.218; an 80%-powered gate drops to ~73%*) **exceeds** the P2 deployable-region gain → net-negative.
- **P4 — Runs-test / serial-dependence is a confirmation-layer category error.** The gate scores *strategy P&L*, not raw returns; a serial-dependence edge, once captured by a strategy, already manifests in its P&L Sharpe (*advisor preview: AR(1) ρ=0.32 raw series is Sharpe-blind, but a momentum strategy on it has P&L Sharpe +0.26*). So a runs-test is a *signal-discovery* tool (the alpha-generation layer Paths B/A/C/D already mined), NOT a confirmation-gate estimand that catches deployable edges the Sharpe gate misses. Confirm by reasoning + a small illustration.

## 3. Pre-registered decision rule (revised per the 2-leg review — anti-hindsight lock)

- **Deployment definition (revised — band primary):** "deployable" = net-of-15bps annualized Sharpe in the **~1.0–1.5 band** (the build-relevant tier; **primary**); net-Sharpe > 0 is a **feasibility partition only** (it is too loose to be the build line — admits skew-divorced near-zero edges).
- **Minimum power-improvement (revised — tripwire, net of multiplicity):** **≥ 10 percentage points ABSOLUTE** detection lift over Sharpe-DSR, **measured AFTER the 2N\* multiplicity penalty**, **within the deployable band**, at matched T/FWER. This is a **DON'T-BUILD tripwire** (≈9× any achievable gain), not a calibrated target. Absolute-pp is the metric (relative-pp is operationally misleading near the floor).
- **Composition (revised — drop "complementary"):** the directional gate is evaluated as a **standalone, multiplicity-corrected (2N\*)** gate (the only honest composition; an OR-gate re-admits skew-divorced junk, an AND-gate cannot raise power).
- **Verdict map (frozen pre-compute):**
  - **DON'T-BUILD** ⟺ the directional advantage concentrates in the non-deployable zone (P1) **AND/OR** the deployable-band gain after 2N\* is < 10pp (P2+P3) **AND** the runs-test is confirmation-layer-inert (P4). (The expected outcome.)
  - **CONDITIONAL/BUILD (surprise)** ⟺ a deployable-band region exists where a directional estimand beats Sharpe-DSR by ≥ 10pp **after** 2N\*, AND is DSL-expressible, AND passes the two-prong anti-motivated clause. (Held genuinely open — B-iii's run flipped DON'T-BUILD→CONDITIONAL; this run may surprise symmetrically.)

## 4. Model fixes folded (2-leg review — required for a sound run)

- **Model F(0) / median-offset EXPLICITLY under skew** — not just kurtosis via f(0). P(up)−0.5 = (0.5 − F(0)) + f(0)·δ + …; the skew term (0.5 − F(0)) is the load-bearing skew-divorce driver. Use a skew-t / skew-normal family with the standardized median computed, not assumed 0. (Without this the model conflates hit-rate-from-drift with hit-rate-from-skew — the very mechanism.)
- **Drop Brier from the estimand set** — a deterministic long/flat DSL signal produces no calibrated probabilities; a constant p>0.5 scores well under skew while losing money. Brier is not naturally expressible for the project's gate; the sign/directional test is the representative directional estimand.
- **Observation unit:** the estimand is over **per-bar strategy P&L sign** (the gate's unit); disclose that sparse zero-P&L bars (long/flat books) make the effective N the nonzero-P&L count (consistent with the project's sparse-returns finding) — strengthens, not weakens, the DON'T-BUILD (smaller effective N → smaller directional gain).

## 5. Deliverable

A small read-only module (proposed: sibling `backtest/eval_estimand_deploy.py`, importing `eval_layer_scoping` primitives — keep the sealed B-iii module unextended) confirming P1–P4 + a memo (proposed: `docs/phase5/ESTIMAND_DEPLOYABILITY_CONFIRMATION.md`) reaching the §3 verdict. Import-primitives-only; never calls `evaluate_cohort()`; writes only its own non-sealed JSON.

## 6. What this is NOT

Not a full grid-sweep study (the 2-leg review found the verdict near-determinate). Not a real strategy run, engine execution, data ingestion, or holdout touch. Not a build of a directional gate (a further separate register if the surprise branch fires). No modification of any sealed artifact or `config/`.

## 7. Risks & assumptions (disclosed)

- **Over-correction risk (advisor self-flagged):** the DON'T-BUILD lean follows three CONDITIONAL leans by the advisor across B-iii; the minimal *run* (vs accept-without-run) is precisely the guard — it preserves the chance of a P1–P4 surprise. The four pillars are computed, not assumed.
- **P4 is the softest pillar** (advisor-inferred from greps that the gate scores strategy P&L; reasoning-confirmed but not a full production-path read). The run includes a small confirmation; if P4 fails to confirm, the runs-test re-opens as a candidate (would shift toward the surprise branch).
- The skew-t/skew-normal is a model family; the qualitative skew-divorce result is robust across negatively-skewed families (the mechanism is median-above-mean, not family-specific).

## 8. Review plan

1. Spec self-review. **(next)**
2. Run P1–P4 (TDD; tests anchored to the design-point previews: skew-divorce z=6.6, ARE 0.994, 2N\* z-increase).
3. **Result 2-leg B2** (Codex recompute + advisor methodology, stress-test P4 + the surprise branch).
4. Charlie's binding read. The build (surprise branch) is a separate register (anti-pre-emption).
