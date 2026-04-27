# Phase 2C — Phase 6: Evaluation Gate (Regime Holdout AND-Gate)

**Plan date:** 2026-04-26
**Branch:** `claude/phase2c-evaluation-gate`
**Base commit:** `8796efc` (corrected-engine arc merged into main)
**Predecessor:** [`docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`](../closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md) (corrected Phase 2C Phase 1 walk-forward results, 44/198 binary winners)
**Successor (forward-pointer):** PHASE2C_7+ — DSR / full lifecycle / D9 finalization (scoped after this deliverable's results inform what comes next)

---

## §1 Scope and rationale

### What this deliverable is

This plan scopes the **first** deliverable of Option A from the Phase 2C Phase 1 closeout's three-options decision point: the regime holdout AND-gate evaluation, applied to Phase 2C corrected candidates with a minimal lifecycle state schema for recording outcomes.

The deliverable answers a single concrete question: **of the 44 corrected Phase 2C binary winners (`wf_test_period_sharpe > 0.5`), how many also pass the 2022 regime holdout AND-gate?**

**Note on existing infrastructure:** the regime holdout gate logic, feed-loading semantic, and run-orchestration are already implemented in `backtest/engine.py` from Phase 2A D4 work, with three reusable entry points:

- `run_regime_holdout()` (engine.py:1365) — top-level wrapper that orchestrates the full holdout evaluation against the canonical 2022 window
- `_evaluate_regime_holdout_pass()` (engine.py:1277-1316) — the four-condition AND-gate evaluator with verified inclusive boundary semantics
- `_load_regime_holdout_config()` (engine.py:1251) — canonical loader for `config/environments.yaml`'s passing criteria

PHASE2C_6 reuses these existing functions rather than reimplementing. The deliverable's net-new work is: (a) the producer script that applies the existing gate to corrected Phase 2C candidates, (b) the artifact schema with the new `evaluation_semantics` lineage tag, (c) the new consumer-side helper `check_evaluation_semantics_or_raise()` for downstream validation, (d) the lifecycle state recording for the three new states, and (e) the closeout document and audit-vs-primary comparison. The gate's pass/fail logic, feed-loading semantic, and run orchestration are canonical and not re-derived here.

This narrowing of net-new scope reduces the implementation risk profile relative to "build the gate from scratch" — the risk is mostly wiring (reuse correctness, artifact schema correctness, lineage stamping correctness) rather than gate-logic correctness.

The 2022 holdout is the v2 split's regime stress test (config-pinned in `config/environments.yaml`). It exposes candidates to a bear-market regime distinct from the 2020-2021 train + 2021 test sub-windows that produced the corrected Phase 2C Phase 1 results. Candidates that survive both the corrected walk-forward AND the 2022 holdout have empirical evidence of robustness across two distinct regimes; candidates that pass walk-forward but fail 2022 are exposed as regime-specific.

### What this deliverable is NOT

- **Not DSR / multiple-testing correction.** That's PHASE2C_7+ scope. This deliverable answers only the regime-survival question, not the statistical-significance question.
- **Not full lifecycle state machine.** Only the three states needed to record holdout outcomes (`pending_holdout`, `holdout_passed`, `holdout_failed`) plus the prior states already established in Phase 2C (`shortlisted` for the 44 corrected binary winners, `wf_below_threshold` for the 154 corrected non-winners). Full state-machine work is PHASE2C_8+ scope.
- **Not paper trading or live execution.** Both deferred to PHASE2C_9+ scope, blocked on PHASE2C_7+ DSR-style validation.
- **Not proposer methodology iteration.** Option C from the closeout decision point is deferred; this deliverable does not change candidate generation.
- **Not changes to the corrected WF engine.** Engine is canonical via tag `wf-corrected-v1`; any change requires a separate decision and its own arc.

### Why narrow scope

Per the project-discipline methodology notes ([`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)) and the established Phase 2B D7 stage-by-stage discipline pattern: each deliverable should be scoped narrowly enough that its results inform the next scope, rather than precommitting to a multi-deliverable arc upfront. The regime holdout result is informationally dense — it changes the scope-relevance of every subsequent piece. A 30-survivor outcome implies a different next-step than a 5-survivor outcome.

---

## §2 Input universe

### Primary universe (44 corrected binary winners)

The 44 candidates that pass `wf_test_period_sharpe > 0.5` per [`data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/walk_forward_results.csv`](../../data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/walk_forward_results.csv). Identification by `hypothesis_hash`. Source DSL retrievable from the corresponding compilation manifest at `data/compiled_strategies/<hypothesis_hash>.json` (per Phase 2C Batch-1 closeout, `docs/closeout/PHASE2C_3_BATCH1.md`).

This is the cohort the deliverable's load-bearing claim is about ("how many corrected winners survive 2022?").

### Audit universe (all 198 corrected candidates)

The full 198-candidate corrected batch is the audit cohort. Running 2022 holdout on the full 198 (not just the 44 winners) gives a comparison baseline that answers a secondary question: **does the regime holdout differentiate winners from non-winners, or does it filter at a similar rate across both groups?**

If the 2022 holdout pass rate is dramatically higher among the 44 winners than among the 154 non-winners, that's evidence the corrected Phase 2C Phase 1 binary criterion has selection power — the candidates that looked best in 2021 sub-windows also tend to survive 2022. If the pass rate is similar across groups, that's evidence the binary criterion is selecting on noise rather than signal.

The audit universe is informational, not gating. Decisions about which candidates to advance to PHASE2C_7+ DSR scope are made on the primary universe.

### Out of universe

- The 4 candidates that flipped binary-criterion status (per erratum §3 and §4: `ca5b4c3a`, `9e6ad910`, `938e135c`, `e135fc0d`). They are part of the audit universe (198) but not the primary universe (44).
- Pre-correction artifacts. Section RS hard prohibition applies.

---

## §3 The regime holdout AND-gate

### Gate definition (config-pinned)

Per `config/environments.yaml` (v2 split) and the canonical implementation in [`backtest.engine._evaluate_regime_holdout_pass`](../../backtest/engine.py) (lines 1277-1316), the regime holdout AND-gate requires **all four** of (inclusive boundaries; verified against existing implementation):

1. `sharpe_ratio >= -0.5` — Sharpe must be at least -0.5 on 2022 holdout (allows for losses but not catastrophic ones)
2. `max_drawdown <= 0.25` — drawdown at most 25%
3. `total_return >= -0.15` — total return loss at most 15%
4. `total_trades >= 5` — minimum activity for the gate to be meaningful (prevents zero-trade or near-zero-trade candidates from passing trivially)

A candidate passes the gate iff all four conditions hold simultaneously. Failing any one of the four fails the gate. NaN on any metric collapses to False (NaN comparisons in Python return False, the conservative behavior).

**Reuse over reimplementation:** the existing `_evaluate_regime_holdout_pass()` function in `backtest/engine.py` already implements the gate with the correct inclusive semantics. PHASE2C_6's script reuses this function rather than reimplementing the gate logic. Likewise, `_load_regime_holdout_config()` (line 1251) loads the canonical passing criteria from `config/environments.yaml`.

**Contract-gap awareness:** an in-code `CONTRACT GAP` comment (line 1302-1310) notes that the passing-criteria thresholds are calibrated for the current D4 feed-loading semantics (first WARMUP_BARS of 2022 are not signal-eligible, effective holdout sample ~8700 bars for WARMUP_BARS ≈ 50). If a later phase modifies the holdout feed loader to prepend pre-window history, these thresholds — especially `min_total_trades=5` — would need re-validation. PHASE2C_6 inherits the existing semantics and does not modify the feed loader.

### Holdout window

`2022-01-01` through `2022-12-31` UTC, the year reserved for this purpose by `config/environments.yaml`. The strategy is evaluated on this window using the existing `run_regime_holdout()` wrapper in `backtest/engine.py` (which itself calls `run_backtest` in single-run mode against 2022). Single-run-mode rationale: the regime holdout's purpose is to test survival on unseen data without further adaptation; walk-forward within 2022 would defeat this purpose by allowing in-regime adaptation. The strategy operates on 2022 with whatever parameters it has from prior compilation; no parameter retuning happens during holdout evaluation.

### Feed-loading semantic (inherited from Phase 2A D4 DESIGN INVARIANT)

The existing infrastructure pins the feed-loading semantic via the DESIGN INVARIANT block at `backtest/engine.py:1319-` (immediately following `_evaluate_regime_holdout_pass`):

- `ParquetFeed.from_parquet(fromdate=2022-01-01, todate=2022-12-31)` filters the parquet to bars **strictly inside that window** — the feed contains ONLY 2022 bars, no pre-window history is prepended
- The first `WARMUP_BARS` bars of 2022 are consumed for indicator warmup and are NOT signal-eligible
- Metrics (Sharpe, drawdown, etc.) are computed from the first post-warmup bar onward
- Effective evaluation sample is ~8700 bars for `WARMUP_BARS ≈ 50` (not the full 8760 bars of the year)

This is the **strict-isolation framing** — no information from outside the holdout window leaks in. PHASE2C_6 inherits this semantic; the alternative "realistic deployment" framing (prepending pre-2022 history for warmup) is the in-code `CONTRACT GAP` future-trigger condition, NOT something PHASE2C_6 changes. If a future phase decides to change feed-loading, the passing-criteria thresholds (especially `min_total_trades=5`) would need re-validation per the contract gap; PHASE2C_6 has no such modification.

### Lineage discipline

The corrected-engine project arc's `wf_semantics='corrected_test_boundary_v1'` tag is specifically about walk-forward boundary semantics. Single-run holdout artifacts do not have walk-forward semantics and therefore should not claim the WF tag — doing so would dilute the precision of the corrected-engine attestation. PHASE2C_6 introduces a separate metadata schema for single-run holdout artifacts:

- The holdout evaluation script must call `backtest.wf_lineage.enforce_corrected_engine_lineage()` at startup (producer-side guard) — this verifies the producing commit is descended from `eb1c87f` and stamps `current_git_sha`. The lineage helper is reused; the metadata stamping pattern differs.
- The output summary JSON carries `evaluation_semantics='single_run_holdout_v1'` (new tag specific to this artifact type), plus the lineage fields `engine_commit='eb1c87f'`, `engine_corrected_lineage='wf-corrected-v1'`, `current_git_sha=<HEAD at run time>`, and `lineage_check='passed'`.
- The output summary does NOT carry `wf_semantics` or `corrected_wf_semantics_commit` fields (those are walk-forward-specific; misapplying them to single-run artifacts is a contract violation).
- A new consumer-side helper `check_evaluation_semantics_or_raise()` is added to `backtest/wf_lineage.py` (alongside the existing `check_wf_semantics_or_raise()` rather than in a new module — kept near the WF helper for code locality, but with strict semantic separation). The helper validates the loaded artifact summary dict has all of:
  - `evaluation_semantics == "single_run_holdout_v1"` (rejects other tag values, including the WF tag — single-run holdout artifacts must not be confused with walk-forward artifacts)
  - `engine_commit == "eb1c87f"` (corrected-engine fix anchor)
  - `engine_corrected_lineage == "wf-corrected-v1"` (tag attestation)
  - `lineage_check == "passed"` (round-trip self-check)
  - `current_git_sha` is present (HEAD at run time, for forensic traceability)
  
  Any field missing or mismatched raises `ValueError` with a specific message identifying the failure. Any consumer reading the holdout summary calls this helper before computing derived metrics.
- The walk-forward consumer helper `check_wf_semantics_or_raise()` would correctly REJECT a single-run holdout artifact because it lacks the WF tag — this is the desired behavior, not a bug.

This preserves the precision of the WF tag (it attests specifically to corrected walk-forward semantics) while giving holdout artifacts their own well-defined attestation. Future single-run evaluations (e.g., validation 2024, test 2025 per Phase 1B FP9) can reuse the `evaluation_semantics='single_run_holdout_v1'` tag if they share the same semantic scope, or define their own (`single_run_validation_v1`, `single_run_test_v1`).

### What the holdout is NOT

- **Not walk-forward.** The 2022 holdout is a single 12-month evaluation against the same strategy that produced the corrected Phase 2C Phase 1 walk-forward result. No quarterly sub-windows, no train/test boundary inside 2022.
- **Not multi-regime.** This is one regime (2022). The "multi-regime evaluation" the project ultimately wants requires combining 2022 holdout with eventual 2024 validation and 2025 test results (per Phase 1B FP9 forward-pointer).
- **Not deployment-ready validation.** Passing the 2022 holdout is necessary but not sufficient for any deployment decision; PHASE2C_7+ DSR-style screens come next.

---

## §4 Minimal lifecycle state schema

### States introduced by this deliverable

| State | Entry condition | Exit condition |
|---|---|---|
| `pending_holdout` | Candidate is in the audit universe (198 corrected candidates); has not yet been evaluated on 2022 holdout | Holdout evaluation completes (transitions to `holdout_passed` or `holdout_failed`) |
| `holdout_passed` | Holdout evaluation completes AND all four AND-gate conditions hold | Terminal for this deliverable; eligible for PHASE2C_7+ DSR scope |
| `holdout_failed` | Holdout evaluation completes AND any of the four AND-gate conditions fails | Terminal for this deliverable; not eligible for PHASE2C_7+ scope |

### States already established (referenced, not introduced)

Per Phase 2C orchestrator and the corrected Phase 2C Phase 1 work:
- `shortlisted` — corrected `wf_test_period_sharpe > 0.5` (the 44 corrected winners)
- `wf_below_threshold` — corrected `wf_test_period_sharpe ≤ 0.5` (the 154 corrected non-winners; this is a new descriptor for clarity within this deliverable, equivalent to the existing terminal-non-shortlisted state)

### State persistence

Lifecycle state is recorded in a per-candidate record alongside the holdout summary. Schema TBD during implementation but constrained to: record per-candidate `hypothesis_hash`, prior state (`shortlisted` or `wf_below_threshold`), holdout state (`pending_holdout` → `holdout_passed` / `holdout_failed`), the four AND-gate metrics (Sharpe, max drawdown, total return, total trades), pass/fail per criterion, overall AND-gate verdict, and full lineage metadata.

### Forward-pointer

PHASE2C_8+ will scope the full lifecycle state machine: states for DSR significance, validation 2024, test 2025, paper-trading entry/exit, capital allocation. This deliverable's three states are the minimum needed to record holdout outcomes cleanly; full state-machine semantics are explicit deferred work.

---

## §5 Artifact paths

### Inputs (read-only)

- Corrected Phase 2C CSV: `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/walk_forward_results.csv`
- Corrected Phase 2C summary: `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/walk_forward_summary.json`
- Per-candidate compilation manifests: `data/compiled_strategies/<hypothesis_hash>.json`
- Configuration: `config/environments.yaml` (v2 split, regime holdout criteria)
- Engine: `backtest/engine.py` `run_backtest` single-run mode
- Lineage helper: `backtest/wf_lineage.py`

### Outputs (created by this deliverable)

Output directory: `data/phase2c_evaluation_gate/<batch_id>/` where `<batch_id>` is a new UUID generated at run time.

Per-candidate artifacts:
- `data/phase2c_evaluation_gate/<batch_id>/<hypothesis_hash>/holdout_summary.json` — single-run summary with full lineage metadata (per §3 schema), the four gate metrics, pass/fail per criterion, AND-gate verdict
- `data/phase2c_evaluation_gate/<batch_id>/<hypothesis_hash>/holdout_trades.csv` — **OPTIONAL.** Per-trade audit detail. Only emitted if the underlying engine exposes a stable trade-log path for this run; this is verified during script implementation. The canonical deliverable does NOT depend on this file existing — it is a forensic-detail artifact. Consumers must not assume its presence.

Aggregate artifacts:
- `data/phase2c_evaluation_gate/<batch_id>/holdout_results.csv` — one row per candidate with hypothesis_hash, prior state, holdout state, four metric values, four pass/fail flags, AND-gate verdict
- `data/phase2c_evaluation_gate/<batch_id>/holdout_summary.json` — batch-level aggregate (count of holdout_passed in primary universe, count in audit universe, by-theme breakdown, full lineage metadata)
- `docs/closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md` — closeout document with primary findings (count of survivors among 44 winners), audit findings (count among 198 candidates), per-theme breakdown, and forward-pointer to PHASE2C_7 scoping

### Producer script

New script: `scripts/run_phase2c_evaluation_gate.py`. Anchored on the lineage guard. CLI flags:

- `--universe primary|audit` — `primary` evaluates only the 44 corrected winners; `audit` evaluates all 198 corrected candidates (which includes the 44, so primary-vs-non-primary breakdown is computable from a single audit run)
- `--candidate <hash>` — evaluate one specific candidate by hypothesis_hash; for debugging or forensic analysis only, not the primary execution path
- `--dry-run` — verify lineage guard, candidate-loading, and metadata stamping without running backtests
- `--force` — overwrite existing artifacts in the output directory (default: refuse to overwrite, per Phase 2C runner convention)

The flags are mutually exclusive at the universe level: exactly one of `--universe` or `--candidate` is required per invocation. Generalizes the script template established by `scripts/run_phase1b_corrected.py` to the holdout-evaluation case, with the addition of single-run-mode evaluation and the `evaluation_semantics` metadata tag.

---

## §6 Pass/fail criteria for this deliverable

### Deliverable success criteria

This deliverable is signed off when:

1. `scripts/run_phase2c_evaluation_gate.py` exists, passes lineage guard, and produces the artifacts listed in §5
2. The 44-candidate primary universe has been evaluated; per-candidate AND-gate verdicts and the count of survivors are recorded in canonical artifacts
3. The 198-candidate audit universe has been evaluated; the audit-vs-primary comparison has been computed
4. `docs/closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md` is written with the load-bearing findings
5. CLAUDE.md Phase Marker is updated to reflect PHASE2C_6 closure (per the freshness discipline noted in CLAUDE.md itself)
6. Codex adversarial review of the deliverable returns PASS, OR returns PASS_WITH_CAVEATS and all caveats have been addressed via review-response commits per the Task 11 precedent (PASS_WITH_CAVEATS is not a soft sign-off — caveats need to be resolved before close)

### What "results inform PHASE2C_7+ scope" means

The results determine the framing of PHASE2C_7+ scoping, not the existence of it. The specific shape of PHASE2C_7+ scope depends on the survival distribution observed:

- **A meaningful survivor population** (i.e., enough candidates that downstream statistical screens like DSR have reasonable input cardinality) likely supports PHASE2C_7 scoping DSR-lite or full DSR against that population. Concrete threshold for "enough" is itself a project-direction decision informed by the actual sample's characteristics, not pre-committed here.
- **A small or zero survivor population** likely warrants a project-direction discussion before scoping continues. Possible directions include methodology iteration (Option C from the original closeout decision point) on candidate generation, deeper diagnostic on what failed (regime-specific factors, prompt structure, evaluation methodology), or revisiting whether the corrected Phase 2C Phase 1 binary criterion is the right gate for downstream consumption at all.

These framings deliberately avoid pre-committing to specific candidate-count thresholds (e.g., "10+ → DSR, 1-9 → methodology, 0 → diagnostic") because such thresholds would be ungrounded calibration bands per `METHODOLOGY_NOTES.md` §3. The actual thresholds depend on the survival distribution shape, the per-theme breakdown, the relationship between primary and audit pass rates, and project-direction context that doesn't exist until PHASE2C_6 results are in hand. PHASE2C_7 scoping captures that grounded reasoning.

The scoping doc PHASE2C_7 will be drafted after PHASE2C_6 results are in hand, not before.

---

## §7 Out of scope (explicit)

- DSR / deflated Sharpe / multiple-testing correction (PHASE2C_7+)
- Full lifecycle state machine beyond the three states named in §4 (PHASE2C_8+)
- Paper trading harness on any candidate (PHASE2C_9+ at earliest, blocked on DSR results)
- Live trading or capital allocation (Phase 3+ work)
- Proposer methodology iteration / momentum-theme prompt revisions (Option C from original closeout decision point; deferred)
- Validation 2024 single-run evaluation (Phase 1B FP9, blocked on DSR/methodology decisions)
- Test 2025 single-run evaluation (Phase 1B FP9, touch-once discipline, blocked on validation 2024 outcome)
- Any change to the corrected WF engine (canonical via tag `wf-corrected-v1`)
- Any change to the v2 split or `config/environments.yaml`

---

## §8 Risks and mitigations

### Risk 1: Holdout result is dominated by chance because n=44 is small

A 44-candidate primary universe with a 4-criteria AND-gate is statistically modest. Survival rates in either direction (very high or very low) could be partly noise.

**Mitigation:** the audit universe (198 candidates) provides a comparison baseline. If the survival rate is similar in both universes, it suggests the regime holdout is filtering at a fixed rate independent of the corrected walk-forward selection. If the 44-survivor rate is meaningfully higher, that's evidence of selection power.

This mitigation does not eliminate the small-sample concern — it bounds it.

### Risk 2: The 2022 regime is itself an unrepresentative sample

2022 was a specific bear-market year for BTC; survival on 2022 doesn't generalize to "robust across all bear markets." The Phase 1B FP9 forward-pointer notes this: full multi-regime evaluation requires 2022 + 2024 + 2025 combined.

**Mitigation:** PHASE2C_6 explicitly does not claim "regime-survivors are robust across all regimes." The framing throughout this scope is "survives 2022 specifically." Forward-pointers to PHASE2C_7+ keep the multi-regime claim deferred to when validation 2024 + test 2025 evaluations land.

### Risk 3: Methodology bug in the holdout script

The corrected-engine project arc demonstrated multiple instances of methodology bugs (calibration bands, fixture defects, factual claims). The holdout script could have similar defects.

**Mitigation:** the project-discipline methodology notes ([`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)) §1 and §3 apply directly. Specifically: empirical verification of all factual claims in the closeout document; calibration bands (if any are introduced — e.g., "expected survival rate") consult per-strategy or per-batch historical context rather than generic intuition. The Codex adversarial review (§6 success criterion 6) is the final external check.

### Risk 4: Lineage discipline violation

If the holdout script bypasses `enforce_corrected_engine_lineage()`, or if the new `check_evaluation_semantics_or_raise()` consumer-side helper isn't wired into downstream consumers, the entire deliverable could be invalidated.

**Mitigation:** the lineage guard is wired in at script startup and at every artifact-load point. Tests cover both producer-side stamping and consumer-side validation (analogous to `tests/test_phase1b_corrected_runner.py` and `tests/test_wf_lineage_guard.py`). Codex review (§6.6) verifies.

### Risk 5: Audit-vs-primary interpretation ambiguity

The §2 audit universe (198 candidates) is included to provide a comparison baseline against the primary universe (44 winners). The natural framing is "if the 2022 holdout pass rate is dramatically higher among the 44 winners than among the 154 non-winners, that's evidence the corrected Phase 2C Phase 1 binary criterion has selection power." However, an alternative interpretation exists: similar pass rates across the two universes could mean either "binary criterion lacks selection power" OR "the 2022 regime is sufficiently extreme that even good candidates struggle equally with bad candidates" (regime-specificity argument). Without independent evidence of what 2022's natural pass rate looks like for arbitrary BTC strategies, distinguishing these two interpretations is difficult.

**Mitigation:** the closeout document (`PHASE2C_6_EVALUATION_GATE_RESULTS.md`) reports both pass rates neutrally and discusses multiple interpretations rather than committing to one as the load-bearing finding. Per `METHODOLOGY_NOTES.md` §1's framing principles ("this batch shows X, not the binary criterion has property Y"), the closeout uses within-batch language. PHASE2C_7+ scoping incorporates this interpretive ambiguity rather than pretending it's already resolved.

---

## §9 Implementation plan

### Step 1: Spec finalization (this document, plus dual-reviewer adjudication)
After this scoping doc lands, surface for ChatGPT + Claude adjudication. Apply approved refinements before proceeding. Estimated: 30-60 minutes of adjudication and folding.

### Step 2: Script implementation
Build `scripts/run_phase2c_evaluation_gate.py` following the template established by `scripts/run_phase1b_corrected.py`:
- Lineage guard called at startup (`enforce_corrected_engine_lineage()`)
- CLI flags per §5: `--universe primary|audit | --candidate <hash> | --dry-run | --force`
- Reads corrected Phase 2C CSV to identify candidates by `hypothesis_hash`; loads DSL from `data/compiled_strategies/<hypothesis_hash>.json` (verified to exist, 198 manifests with `canonical_dsl` field)
- Reuses existing `run_regime_holdout()` wrapper, `_evaluate_regime_holdout_pass()`, and `_load_regime_holdout_config()` from `backtest/engine.py` rather than reimplementing
- For each candidate: compile DSL from manifest's `canonical_dsl` field to strategy, call `run_regime_holdout()` (which orchestrates feed loading + run_backtest + gate evaluation per the inherited DESIGN INVARIANT semantic), capture gate metrics + AND-gate verdict, write per-candidate artifact with `evaluation_semantics='single_run_holdout_v1'` metadata schema (per §3), append to aggregate CSV
- Aggregate summary written at end with batch-level metadata + lineage stamping (also using `evaluation_semantics='single_run_holdout_v1'` schema)

Adds new consumer-side helper `check_evaluation_semantics_or_raise()` to `backtest/wf_lineage.py` for downstream consumption of single-run holdout artifacts.

Estimated: 1-2 days for the script with tests.

### Step 3: Tests
Smoke tests analogous to `tests/test_phase1b_corrected_runner.py`: lineage guard wired, metadata stamping (new `evaluation_semantics` schema) correct, force-overwrite refusal. Plus one test per AND-gate criterion to verify the four conditions are checked correctly via the reused `_evaluate_regime_holdout_pass()` (passes when all four hold; fails when any one is below threshold; NaN collapses to False). Plus tests for the new `check_evaluation_semantics_or_raise()` helper analogous to the WF helper tests in `tests/test_wf_lineage_guard.py`.

Estimated: 0.5 day.

### Step 4: Smoke run on 3-5 candidates
Per project-discipline pattern (smoke before scale): invoke script on a small subset (3-5 candidates from the 44 primary universe) to verify source loading, compilation, lineage stamping, gate evaluation, and metadata schema correctness end-to-end. **Record measured per-candidate runtime during the smoke run.** This establishes the empirical basis for the audit-universe scale-up.

Estimated: 0.5 day (most time is verification, not compute).

### Step 5: Run primary universe
Invoke script on the 44 corrected winners. Empirically verify outputs (lineage metadata stamps correctly, per-candidate artifacts written, aggregate summary computes correctly).

Estimated: TBD after Step 4 smoke run records actual per-candidate runtime. Do not extrapolate from intuition.

### Step 6: Run audit universe
Invoke script on the full 198 candidates (which includes the 44 from Step 5; primary-vs-audit breakdown is computed from a single audit run rather than two separate runs). Verify outputs.

Estimated: TBD after Step 4 smoke run records actual per-candidate runtime.

### Step 7: Closeout document
Write `docs/closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md` with empirically-verified findings. Apply project-discipline methodology notes §1 to all factual claims (no specific quantitative or referential claim without empirical query). Apply Risk 5's neutral-reporting framing to the audit-vs-primary comparison.

Estimated: 1 day with dual-reviewer adjudication.

### Step 8: Codex adversarial review
External review of script + closeout. Address findings before push (PASS_WITH_CAVEATS requires caveats addressed per §6.6).

Estimated: 0.5-1 day.

### Step 9: CLAUDE.md update + push + merge
Update CLAUDE.md Phase Marker per the freshness discipline (per `feedback_claude_md_freshness.md` saved memory). Push working branch, merge to main, push main.

Estimated: 0.5 day.

**Total estimated effort: ~4-7 days** for the full PHASE2C_6 arc, with execution-time uncertainty resolved by Step 4 smoke run.

---

## §10 References

- Predecessor closeout: [`docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`](../closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md)
- Original Phase 2C closeout (preserved): [`docs/closeout/PHASE2C_5_PHASE1_RESULTS.md`](../closeout/PHASE2C_5_PHASE1_RESULTS.md)
- Corrected-engine arc sign-off: [`docs/closeout/CORRECTED_WF_ENGINE_SIGNOFF.md`](../closeout/CORRECTED_WF_ENGINE_SIGNOFF.md)
- Phase 1B canonical baselines: [`data/phase1b_corrected/phase1b_corrected_v1/BASELINE_NUMBERS.md`](../../data/phase1b_corrected/phase1b_corrected_v1/BASELINE_NUMBERS.md)
- Phase 1B FP9 forward-pointer: [`data/phase1b_corrected/phase1b_corrected_v1/BASELINE_NUMBERS.md`](../../data/phase1b_corrected/phase1b_corrected_v1/BASELINE_NUMBERS.md) §FP9
- Decision document (engine semantics): [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md)
- Project-discipline methodology notes: [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md)
- Lineage guard module: [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py)
- Phase 1B corrected runner template: [`scripts/run_phase1b_corrected.py`](../../scripts/run_phase1b_corrected.py)
- Phase 2C runner: [`scripts/run_phase2c_batch_walkforward.py`](../../scripts/run_phase2c_batch_walkforward.py)
- Configuration: [`config/environments.yaml`](../../config/environments.yaml) (v2 split, regime holdout criteria)
- Technique backlog (PBO/DSR/CPCV/MDS dependency lines per Task 10a): [`strategies/TECHNIQUE_BACKLOG.md`](../../strategies/TECHNIQUE_BACKLOG.md)
