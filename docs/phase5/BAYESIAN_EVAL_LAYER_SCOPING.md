# Continuous-Evidence / Bayesian Evaluation-Layer Scoping — results memo

- **Date:** 2026-06-02 UTC
- **Spec:** [`docs/superpowers/specs/2026-06-02-bayesian-eval-layer-scoping-design.md`](../superpowers/specs/2026-06-02-bayesian-eval-layer-scoping-design.md) (§5 decision rule Charlie-ratified, frozen pre-analysis).
- **Module / tests / data:** [`backtest/eval_layer_scoping.py`](../../backtest/eval_layer_scoping.py) · [`tests/test_eval_layer_scoping.py`](../../tests/test_eval_layer_scoping.py) (18 passed) · `data/eval_gate_power_study/eval_layer_scoping_v1.json`.
- **Status:** analysis complete; headline verdict below. Result 2-leg B2 (Codex + advisor) pending; the binding go/no-go read is the PI's.
- **Provenance discipline:** purely analytical / read-only. No data spent, no holdout touched, no strategy run on held data, no peek; the 12 cohort Sharpes are read from the sealed Path verdict artifacts; sealed `tier6_dsr_v1/` SHA-256 byte-unchanged throughout; no `evaluate_cohort()` call (AST-checked).

## The question (spec §1)

> Can a continuous-evidence / Bayesian evaluation layer **legitimately improve the deploy decision** for a modest (~1–1.5 ann Sharpe) BTC edge — raise confirmation power, or improve the decision under low power — **WITHOUT spending the 2024/2025 holdout and without a garden-of-forking-paths inflation** — by enough to justify building it?

## Headline verdict (per the §5 map): **DON'T-BUILD (now)** — precisely scoped, non-foreclosing

No mechanism raises fixed-`T` confirmation power; the only legitimate power lever is **time**, which — with the frame frozen and no live candidate to monitor — changes no current action. So a continuous-evidence/Bayesian layer built **now** would be rigor-theater on a frozen frame. This is **not** "the idea is wrong": two ingredients (M5 always-valid monitoring, M4 honest skeptical-posterior reporting) are recommended for any **future re-entry** cycle's evaluation design — just not a standalone build today.

The verdict-critical lead (M6, change-the-estimand) was **measured and refuted**: a directional/hit-rate estimand is *less* powerful than Sharpe at the deployable regime, not more.

## Per-mechanism classification (Axis-1 × Axis-2 + per-mechanism clause)

| Mechanism | SV result | Axis-1 (power) | Axis-2 (decision-value) | Clause | Contribution |
|---|---|---|---|---|---|
| **M1** posterior→sizing | `f*`=2.5, P(SR≤0)=**21%** | `no-power-gain` | `negative`→`modest` (capital-danger) | — | kill |
| **M2** Bayesian sequential | seq detect **0.0008** ≪ fixed **0.205** | `only-via-time` | `modest` (early-kill real; posterior peeking invalid w/o M5; nothing to monitor now) | — | → DON'T-BUILD |
| **M3** pool across cycles | posterior **−0.26 / −1.60** ≪ deploy line | `backfires` | `none`/`negative` | — | kill |
| **M4** skeptical-prior report | posterior < y always (only tightens) | `no-power-gain` | `modest` (honesty: separates under-power from no-edge) | pass | → DON'T-BUILD |
| **M5** always-valid / e-value | e=**1.38** vs 20 needed; ~**2.66 yr** to threshold | `only-via-time` | **`modest` now (HINGE — see below)** | pass | → DON'T-BUILD (CONDITIONAL if Axis-2=`high`) |
| **M6** change-the-estimand | power_sign **0.158** < power_sharpe **0.201**; ARE=**0.637** | `no-power-gain` (mild loss) | — | — | **BUILD unreachable** |
| **M7** within-batch EB | shrink 0.224; `in_scope_now=False` | conditional / out-of-scope | conditional | — | out-of-scope (not a kill) |

**Verdict-map application:** BUILD requires ≥1 `raises-power-legitimately` (clause-passing) — **none** (M6 refuted). CONDITIONAL branch (ii) requires `only-via-time AND Axis-2=high` — M2/M5 are `only-via-time` but Axis-2=`modest` (see hinge). Every mechanism is `no-power-gain`/`backfires`/`only-via-time-modest`/out-of-scope, none reaches Axis-2=`high` → **DON'T-BUILD**.

## The SV1–SV7 numbers

- **SV6 (verdict-critical) — directional estimand REFUTED as a power lever.** For a true 1.5-ann-Sharpe edge over the forward gate: Sharpe-test power **0.2006** (matches the MC ~0.20), directional/sign-test power **0.1582**. The sign test's asymptotic relative efficiency is **0.6366 ≈ 2/π** — the classic sign-vs-t efficiency. The heavy-tail rescue (the one route by which a directional estimand could overtake) needs raw kurtosis **≈ 8892** at the modest hourly per-bar Sharpe (BTC realized γ4 ≈ 11–30); even **daily + γ4=60** gives ARE 0.693 < 1 (no overtake). A directional estimand answers a different question with *less* power here. Cost gate moot (M6 already fails on power; the hit-rate excess is ~0.64%/bar, swamped by 15bps/side).
- **SV3 (M3) — pooling backfires, robust to the modeling choice.** Cohort mean −2.5467; pooling a +1.5 candidate gives posterior **−0.26** (raw observed τ²=4.53) to **−1.60** (de-noised between-group τ²=1.06). Both ≪ the 1.0 deploy line. Borrowed "strength" = evidence of no edge.
- **SV2 (M2) — no free acceleration.** An anytime-valid mixture e-process detects the true 1.5 edge over [0,T] only **0.08%** of the time vs **20.5%** fixed-horizon at T — the anytime-validity penalty; Bayes/e-process adds **no** fixed-`T` power.
- **SV5 (M5) — only-via-time.** The expected log-e over the forward window is 0.32 nats (e ≈ 1.38) vs the ln(20) ≈ 3.0 needed; the e-value crosses its deploy threshold only after **~2.66 more years** of hourly tape.
- **SV1 (M1) — capital-danger.** Full-Kelly `f*`=2.5×, but P(true Sharpe ≤ 0)=**21%** at se_ann=1.86 — sizing-by-evidence on a straddling-zero posterior puts capital on noise.
- **SV4 (M4) — honesty, not power.** A skeptical prior (located at 0 or the cohort mean) only *lowers* the posterior below the data point — it can tighten, never loosen, confirmation.
- **SV7 (M7) — conditional.** Within-batch EB winner's-curse shrinkage (0.224) is legitimate but in-scope only if a *future* candidate batch is registered; the frozen frame has none.

## The hinge: M5's Axis-2 (the one genuine judgment, disclosed)

The verdict turns on whether M5 (always-valid/e-value monitoring) is Axis-2 `high` or `modest`:
- **`modest` (my reasoned call → DON'T-BUILD):** the pinned §5 criterion requires `high` to change *a real action the current frame cannot already take*. With the frame frozen and **no live candidate strategy producing a signal to monitor**, anytime-valid monitoring changes no current action. The reviewers' "pre-register the tracker now, while clean" credibility argument is real but is **already provided by the project's per-cycle pre-registration discipline** — any future re-entry cycle pre-registers its evaluator *before* its run (exactly as every Path cycle did), so the clean window does not require a standalone build now.
- **`high` (the reviewers' design-stage CONDITIONAL lean):** if "pre-register the always-valid tracker now, while there is no candidate to game it" is itself judged a high-value now-only action, M5 → CONDITIONAL ("name a next register: pre-register a thin always-valid evidence-tracker").

I weight the **DON'T-BUILD** reading higher (the pinned criterion + the per-cycle-pre-registration counter), but flag this as the soft judgment the result-B2 should stress-test. Either way the **hard** results stand: M3/M1 killed, M6 refuted, BUILD unreachable.

## Non-foreclosing scope (what this does and does NOT close)

- **Closes:** the deferred-open path (ii) **as a standalone power lever / build-now**. A Bayesian/continuous-evidence layer cannot manufacture confirmation power on the fixed window (no free lunch, now mechanism-by-mechanism confirmed), and pooling the dead cohort actively backfires.
- **Does NOT close:** M5 (always-valid monitoring) + M4 (honest skeptical-posterior reporting) as **recommended ingredients** for any future re-entry cycle's evaluation design; M7 (within-batch EB) as in-scope if a future candidate batch is registered; the freeze's other deferred-open paths (fresh-OOS accrual = the literal `only-via-time` lever; structurally-different frames) — all untouched.
- **The 2024/2025 holdout stays UNSPENT.**

## Decision → next register (spec §7)

DON'T-BUILD: no build or study is recommended now. The non-foreclosing ingredients (M5/M4/M7) attach to a *future* re-entry register, not a standalone one. Per anti-pre-emption, any such cycle is a fresh Charlie register; **this analysis authorizes nothing downstream.**

## Review provenance

- Design spec: 2-leg B2 in two passes (design-point + written-spec), SOUND-WITH-CAVEATS / SHIP-WITH-CHANGES; all findings folded; §5 rule Charlie-ratified.
- Analysis: 18 tests green; every headline number hand-derivable and pinned (SV1 f\*/P(SR≤0); SV3 −0.26/−1.60; SV5 0.32 nats / 2.66 yr; SV6 ARE 2/π / crossover ≈8892; SV2 seq≪fixed). Result 2-leg B2 (Codex recompute + advisor methodology, stress-testing the M5-Axis-2 hinge) pending.

## Assumptions / limits (disclosed)

- **The M5-Axis-2 call is the one soft judgment** (high vs modest); the verdict flips DON'T-BUILD↔CONDITIONAL on it. Disclosed and flagged for the B2 + the PI.
- The SV2 MC uses an iid-Gaussian DGP (the no-free-acceleration property is DGP-independent; the iid arm suffices) and a single mixture-e-process construction (τ matched to the alternative — generous to the sequential test).
- SV6's directional power uses a normal approximation to the binomial (T large) and the sign/Brier family as the directional estimand; an exotic estimand outside this family is not covered, but the 2/π efficiency + the astronomical kurtosis-crossover make a power *gain* implausible at the deployable regime.
- M7's IC/τ are illustrative (no future batch exists); it is a conditional classification, not a measured edge.
