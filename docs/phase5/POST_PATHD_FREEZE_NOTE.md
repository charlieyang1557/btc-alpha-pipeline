# Post-Path-D Strategic Freeze — sealed closeout note

- **Date:** 2026-06-02 UTC
- **Decision:** **FREEZE (accept-the-negative)** — Charlie-registered binding read, `p` low.
- **Scope:** closes the **post-Path-D strategic-fork arc**. This is the *decision record*; the supporting study is [`docs/phase5/EVAL_GATE_POWER_STUDY.md`](EVAL_GATE_POWER_STUDY.md).
- **Status:** sealed. Analytical study + Monte-Carlo empirical validation both 2-leg-B2'd SOUND. Branch `eval-gate-power-study`.

## The decision

The single-asset directional BTC research frame, under its committed evaluation discipline, is **frozen** on an earned negative. The decision is **not** "crypto has no alpha" and **not** "the project failed" — it is a precisely-scoped epistemic conclusion: **this frame, as disciplined, can neither generate nor confirm a realistic edge, and the honest, EV-rational move is to stop spending cycles on it while preserving optionality.**

## The two binding constraints (the genuine finding)

1. **Alpha-source constraint — earned across four axes.** Four pre-registered, mechanism-first single-asset cycles each returned `process_refuted_for_this_grid`: Path B (OHLCV), Path A (funding), Path C (basis ≈ funding), Path D (open interest — the *first genuinely-independent* axis). forward_2026 net Sharpes −2.5 to −8.4; 0/3 Tier-5, 0/3 DSR each. No confirmable edge was generated.
2. **Confirmation-power constraint — the new finding, analytically *and* empirically grounded.** The evaluation gate (immutable touch-once splits, FWER multiplicity, ~105-day clean OOS) has an 80%-power minimum-detectable Sharpe of **~4.63 (N\*=1) to ~6.22 (N\*=3)** annualized — far above the ~1–1.5 band of a deployable edge. The Monte-Carlo validation *measured* this on the live gate: a genuinely-existing ~1.5-Sharpe edge clears the gate only **~20% (N\*=1) / ~5% (N\*=3)** of the time, on **both** synthetic and real-BTC return structure. The gate can **refute** (it killed four cycles at large effect sizes) but **cannot *reliably* confirm** a modest edge (it is severely under-powered there, not literally blind). Even the single arm that reaches BUILD-viability (`daily_3yr · N\*=1`, MDE 1.44) is *doubly* out of reach: governance-blocked (it would spend the 2024 validation + 2025 test windows) **and** requires abandoning multiplicity.

The standing thesis ([[alpha-source-is-the-binding-constraint-not-data-methodology]]) is thereby revised: there are **two** binding constraints, not one — even *with* an edge, this frame could not confirm it.

## Precise scoping (what this freeze does and does NOT claim)

- **Does NOT claim "no edge exists."** The four negatives falsify *large* edges along four *long/flat* axes; the gate is *severely under-powered* for *modest* edges — the Monte-Carlo measures only ≈20% (N\*=1) / ≈5% (N\*=3) detection of a real 1.5-Sharpe edge (under-powered, **not** literally blind — the category error the freeze explicitly avoids). The conclusion is bounded to **"under the achievable OOS designs and the long/flat single-asset frame tested."**
- **Untested, NOT exhausted (recorded open):** short legs (every cohort was long/flat); continuous (non-binary) position sizing; on-chain / flow data (a genuinely-independent signal axis); cross-sectional multi-asset rank (the literature's strongest edge, structurally inexpressible in a single-asset engine). Liquidations were excluded on an *earned* basis (mechanically spanned by Paths B+D + the 2021-04-27 Binance throttle corrupting the only independent residual — see the 1b stop documented in the arc).
- **The holdout is preserved UNSPENT.** 2024 (validation) and 2025 (test) were *not* spent to manufacture a BUILD-viable gate. They remain the option value any *fundamentally different* future frame would require.

## Non-foreclosing posture — deferred-open paths (not killed)

The freeze is a *stop on this frame*, not a permanent foreclosure. The following remain explicitly open for a future fresh register, **none requiring the holdout to be spent now**:

1. **Let `forward_2026` accrue fresh, clean OOS** — the MDE falls monotonically with T; in ~2–3 more calendar years a daily book over the genuinely-fresh forward tape reaches BUILD-viable power *without touching 2024/2025*. The cost is patience, not held-out data.
2. **A pre-registered Bayesian / continuous-evidence evaluation layer** that pools across cycles and degrades gracefully under low power (sidesteps the single-shot NHST MDE artifact). Caveat: switching evaluation frameworks after four negatives carries garden-of-forking-paths risk and needs hard pre-registration.
3. **The structurally-different frames** — short-enabled / continuous-sizing single-asset; cross-sectional multi-asset rank; on-chain flow — each a separate Charlie register with its own scoping.

## Evidentiary base

- Four verdict artifacts: `data/phase2c_evaluation_gate/path{b,a,c,d}_verdict_v1/`.
- Gate-power study: [`docs/phase5/EVAL_GATE_POWER_STUDY.md`](EVAL_GATE_POWER_STUDY.md), `backtest/eval_power.py`, `data/eval_gate_power_study/results_v1.json`.
- Monte-Carlo empirical validation: `backtest/eval_power_mc.py`, `data/eval_gate_power_study/mc_power_v1.json`.

## Review provenance

- Binding read: two **adversarial** advisor legs (steelman continue-redesign vs steelman accept-the-negative) adjudicated; Charlie registered FREEZE, `p` low. Both legs converged on: do not spend 2024/2025; a non-destructive fresh-OOS path exists; the heavy cross-sectional build is weak on the numbers; the decision hinges on `p`.
- Gate-power study + MC validation: each 2-leg-B2'd (Codex + advisor) SOUND; the MC design review caught a fatal DGP bug *pre-run*; a second (bootstrap source-window) bug was caught by diagnostic; both fixed + regression-guarded.

## Methodology lessons (codified in METHODOLOGY_NOTES)

Confirmation-power as a *second binding constraint*; "refutation-powered ≠ confirmation-powered"; the option-value of an unspent touch-once holdout dominating marginal gate-sensitivity; empirically validate an analytical power projection before sealing a strategic conclusion on it; the value of a design-review gate (it caught a fatal bug before any run).
