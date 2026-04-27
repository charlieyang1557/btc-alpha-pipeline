# Corrected Walk-Forward Engine Sign-Off

**Sign-off date:** 2026-04-26
**Status:** PASS / CLOSED
**Branch:** `origin/claude/setup-structure-validators-JNqoI`
**Final pushed commit:** `0fc58e2`
**Corrected-engine tag:** `wf-corrected-v1` (target `3d24fcb`; engine-fix anchor `eb1c87f`)

---

## §1 Status

The walk-forward test-boundary semantics correction project arc is complete and shipped on origin. The corrected engine is the canonical engine for all future walk-forward research. Pre-correction artifacts are quarantined and prohibited from downstream consumption per Section RS.

This sign-off closes the corrected-engine work scope. The next major work cycle (Phase 2 technique implementation: DSR, PBO, CPCV, MDS) builds directly on the artifacts and discipline established here.

---

## §2 What was fixed

The pre-correction `run_walk_forward()` in `backtest/engine.py` carried train-period equity into reported test-period metrics. This contaminated walk-forward Sharpe, return, drawdown, and trade aggregates by mixing pre-test broker state into the test-period accounting. Empirically, 82.1% of pre-correction walk-forward windows had non-trivial carry-in PnL contamination, and the median window had 92% of reported PnL coming from train-period accumulation.

The corrected semantic implements Q2 option (iii) from the design spec: at the test-window boundary, the strategy's broker state is reset and a new Backtrader run is initiated against the test data only. Test-period metrics are computed exclusively from test-period equity and trades, with no leakage from the train period. The full bug analysis, design rationale, and consumption rules are in [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md).

---

## §3 Trust chain (commit-by-commit)

The corrected-engine work landed across the following commits, in dependency order:

| Commit | Subject | Role |
|---|---|---|
| `0f785fc` | docs(brainstorm): WF test-boundary semantics design spec | Spec |
| `bd513e5` | docs(brainstorm): WF spec amendments per dual-reviewer pass | Spec amend |
| `3acb6d7` | docs(plan): WF test-boundary semantics implementation plan | Plan |
| `85fb593` | docs(plan): WF semantics plan amendments per dual-reviewer pass | Plan amend |
| `2678444` | docs(decisions): canonical WF test-boundary semantics decision | Task 1 |
| `19e9e0f` | docs(decisions): WF boundary semantics test classification table | Task 2 |
| `bf2be4a` | test: WF boundary regression test fixtures (T1-T9 infrastructure) | Task 3 |
| `bfbd3e5` | test: WF + regime_holdout boundary semantics regression tests T1-T10 | Task 4 |
| `eb1c87f` | fix(engine): WF gated wrapper implements Q2 (iii) | **Task 5 (engine fix)** |
| `876302c` | test: T1/T2 use TrainOnlyStrategy (absolute-timestamp fixture) | Task 5 fixture |
| `5f53ee5` | feat(scripts): Task 7.6 — corrected-engine lineage guard + stale-artifact quarantine | Task 7.6 base |
| `ebfbbe1` | feat(backtest): Task 7.6 expansion — shared wf_lineage module + consumer-side helper | Task 7.6 expansion |
| `3d24fcb` | fix(lineage): anchor corrected-engine guard to repo root | Task 7.6 CWD fix; tag target |
| `0e368a8` | docs(backlog): Task 10a — corrected-engine dependency on PBO/DSR/CPCV/MDS entries | Task 10a |
| `a22051e` | refactor(phase2c): WF metric renaming wf_* → wf_test_period_* | Task 10b |
| `e93bffd` | feat(phase1b): canonical corrected v2 WF engine-sanity baselines | Task 8a |
| `9d1c722` | docs(closeout): Phase 1B WF corrected baseline supplement (Task 8b) | Task 8b |
| `1946dd6` | docs(phase2c): Phase 2C Phase 1 erratum under corrected WF semantics | Task 9 |
| `0fc58e2` | fix(phase2c-erratum): Codex Task 11 review-response — quartile recomputation + audit-artifact reference | Task 11 |

(Several intermediate plan-amendment commits omitted for brevity; full chain available via `git log eb1c87f..0fc58e2`.)

---

## §4 Verification surfaces

The corrected engine has four independent verification surfaces, each with durable on-disk artifacts:

**Regression test suite** (committed under `tests/`):
- `tests/test_walk_forward_boundary_semantics.py` — 9 tests covering boundary semantics T1-T9
- `tests/test_regime_holdout.py` — includes T10 boundary regression alongside pre-existing regime holdout tests (35 tests total)
- `tests/test_wf_lineage_guard.py` — 9 tests covering producer guard, CWD anchor, consumer helper
- `tests/test_phase1b_corrected_runner.py` — 3 tests covering Phase 1B runner lineage wiring, metadata stamping, force-overwrite refusal

These tests run on every CI invocation and continuously verify the corrected engine's properties.

**Lineage metadata stamping** (per-artifact, runtime-verified):
Every `walk_forward_summary.json` produced by the corrected engine carries `wf_semantics='corrected_test_boundary_v1'`, `corrected_wf_semantics_commit='eb1c87f'`, `current_git_sha`, and `lineage_check='passed'`. The lineage helper at [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) provides both producer-side enforcement (`enforce_corrected_engine_lineage()`) and consumer-side validation (`check_wf_semantics_or_raise()`).

**Codex adversarial reviews** (three rounds, all PASS-class verdicts):
- Task 7.5 — engine wrapper review: TRUSTED across all six attack surfaces
- Task 7.6 — lineage helper review: TRUSTED with one MEDIUM finding (CWD anchor) fixed at `3d24fcb`
- Task 11 — Phase 2C erratum + corrected artifacts: needs-attention with 3 MEDIUM findings; review-response fix at `0fc58e2`; focused re-review verdict: PASS

**Round-trip artifact validation**:
All 5 Phase 1B summaries and the Phase 2C corrected summary pass `check_wf_semantics_or_raise()` round-trip validation when re-loaded from disk.

---

## §5 Artifact policy

### Canonical artifacts (consume these)

- `data/phase1b_corrected/phase1b_corrected_v1/` — Phase 1B canonical baselines (4 per-baseline + 1 aggregate summary)
- `data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/` — Phase 2C corrected re-run artifacts (CSV, summary JSON, delta report)

### Quarantined artifacts (must not be consumed)

- `data/quarantine/pre_correction_wf/` — all pre-correction Phase 2C walk-forward artifacts

### Hard rule (Section RS)

No downstream consumer (DSR, PBO, CPCV, MDS, strategy-shortlist tooling) may consume a walk-forward artifact unless **all three** conditions hold:

1. The producing commit is descended from `eb1c87f` (or carries the `wf-corrected-v1` tag's lineage)
2. The summary contains `wf_semantics='corrected_test_boundary_v1'`
3. The consumer calls `backtest.wf_lineage.check_wf_semantics_or_raise()` on the loaded summary before computing any derived metrics

The expected enforcement pattern: load `walk_forward_summary.json` → call `check_wf_semantics_or_raise()` → only then load or join the corresponding CSV. Validating the summary while consuming an adjacent stale CSV defeats the contract.

The Phase 2 technique backlog entries at `strategies/TECHNIQUE_BACKLOG.md` (PBO §2.2.2, DSR §2.2.3, CPCV §2.2.4, MDS §2.4.1) all cross-reference this enforcement helper per Task 10a.

---

## §6 Errata and supplements published

This work scope produced two corrected-engine closeout artifacts:

- **Phase 1B corrected baseline supplement:** [`docs/closeout/PHASE1B_WF_CORRECTED_BASELINE_SUPPLEMENT.md`](PHASE1B_WF_CORRECTED_BASELINE_SUPPLEMENT.md) — supplement to the original Phase 1 sign-off, publishing the canonical corrected v2 walk-forward engine-sanity baselines (Task 8b)

- **Phase 2C Phase 1 erratum:** [`docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`](PHASE2C_5_PHASE1_RESULTS_ERRATUM.md) — erratum to the original Phase 2C Phase 1 closeout, with corrected numerical findings (binary criterion 48/198 → 44/198) and one epistemic correction ("FALSIFIED" RSI wording amended to "null result, not supported") (Task 9 + Task 11)

Both original closeouts (`PHASE1_SIGNOFF.md`, `PHASE2C_5_PHASE1_RESULTS.md`) are preserved unmodified for historical reproducibility per the project's "sealed closeouts retain original numbers, errata point forward" discipline.

---

## §7 Final conclusion

The corrected walk-forward engine is trusted for all future walk-forward research, subject to Section RS consumption rules. The `wf-corrected-v1` tag (commit `3d24fcb`) is the canonical anchor for any new artifact requiring lineage validation.

Phase 2C Phase 1's acceptance verdict survives correction (44/198 still strongly clears the ≥10 binary criterion at 4.4x). Phase 1B's four hand-written baselines pass author-stated calibration bands under corrected engine-sanity scope. No work prior to this arc requires re-adjudication beyond the published erratum and supplement.

---

## §8 Deferred non-blocking followups

Three project-discipline notes surfaced during this work and should land in `strategies/TECHNIQUE_BACKLOG.md` or a project-discipline document at the start of the next major work cycle:

1. **Empirical verification for factual claims (generalized).** Any specific quantitative or referential claim — in dispatch text, prose, table cells, code references, file paths, JSON structure — must be empirically verified against canonical data before commit. Eight instances of this defect class were caught across Task 9 + Task 11 work, including in fix prose itself. Generalizes the Task 8b methodology lesson from "calibration bands" to all artifact-level claims.

2. **Meta-claim verification discipline.** Confidence-sounding meta-claims about process state ("we've verified X," "the framing is pinned," "re-dispatch is low-value") need the same empirical-verification discipline as artifact-level claims. Plausible reasoning at the meta layer can fail in the same way as plausible reasoning at the artifact layer.

3. **Regime-aware calibration-band methodology.** Calibration bands for strategy expected behavior must consult per-strategy author-stated expected ranges (when documented in strategy docstrings) rather than generic batch-wide bands. The Task 8a calibration-band defect (a generic `[-2.0, 0.5]` band that empirically did not match any baseline's design intent) motivates this principle.

These are non-blocking — the corrected-engine work shipped without them codified — but worth landing before the next major closeout cycle so the discipline is durable.

One additional deferred item is documented elsewhere: **FP9** in [`data/phase1b_corrected/phase1b_corrected_v1/BASELINE_NUMBERS.md`](../../data/phase1b_corrected/phase1b_corrected_v1/BASELINE_NUMBERS.md) §FP9 flags that future canonical multi-regime baselines (validation 2024, test 2025 single-run evaluations) are needed before any DSR/PBO/CPCV/MDS technique can consume Phase 1B canonical baselines as multi-regime anchors. Not blocking on this sign-off; blocks the first downstream technique implementation that requires Phase 1B canonical baselines as input.

---

## §9 References

### Decision and design documents

- [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md) — canonical decision document with Section RS hard prohibition
- [`docs/decisions/wf_test_boundary_semantics_test_classification.md`](../decisions/wf_test_boundary_semantics_test_classification.md) — test classification table
- [`docs/superpowers/specs/2026-04-26-wf-test-boundary-semantics-design.md`](../superpowers/specs/2026-04-26-wf-test-boundary-semantics-design.md) — design spec
- [`docs/superpowers/plans/2026-04-26-wf-test-boundary-semantics-plan.md`](../superpowers/plans/2026-04-26-wf-test-boundary-semantics-plan.md) — implementation plan

### Code modules

- [`backtest/engine.py`](../../backtest/engine.py) — `run_walk_forward()` with corrected test-boundary semantic
- [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) — producer-side and consumer-side lineage enforcement helpers
- [`scripts/run_phase2c_batch_walkforward.py`](../../scripts/run_phase2c_batch_walkforward.py) — Phase 2C corrected runner
- [`scripts/run_phase1b_corrected.py`](../../scripts/run_phase1b_corrected.py) — Phase 1B corrected runner

### Test files

- [`tests/test_walk_forward_boundary_semantics.py`](../../tests/test_walk_forward_boundary_semantics.py) — T1-T9 boundary regression tests
- [`tests/test_regime_holdout.py`](../../tests/test_regime_holdout.py) — includes T10 boundary regression
- [`tests/test_wf_lineage_guard.py`](../../tests/test_wf_lineage_guard.py) — lineage guard tests
- [`tests/test_phase1b_corrected_runner.py`](../../tests/test_phase1b_corrected_runner.py) — Phase 1B runner smoke tests

### Closeout artifacts

- [`docs/closeout/PHASE1B_WF_CORRECTED_BASELINE_SUPPLEMENT.md`](PHASE1B_WF_CORRECTED_BASELINE_SUPPLEMENT.md)
- [`docs/closeout/PHASE2C_5_PHASE1_RESULTS_ERRATUM.md`](PHASE2C_5_PHASE1_RESULTS_ERRATUM.md)
- [`data/phase1b_corrected/phase1b_corrected_v1/BASELINE_NUMBERS.md`](../../data/phase1b_corrected/phase1b_corrected_v1/BASELINE_NUMBERS.md)
- [`data/phase1b_corrected/phase1b_corrected_v1/SMA_CROSSOVER_AUDIT_NOTE.md`](../../data/phase1b_corrected/phase1b_corrected_v1/SMA_CROSSOVER_AUDIT_NOTE.md)
- [`data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/PHASE2C_CORRECTED_DELTA_REPORT.md`](../../data/phase2c_walkforward/batch_b6fcbf86-4d57-4d1f-ae41-1778296b1ae9_corrected/PHASE2C_CORRECTED_DELTA_REPORT.md)

### Backlog cross-references

- [`strategies/TECHNIQUE_BACKLOG.md`](../../strategies/TECHNIQUE_BACKLOG.md) — PBO §2.2.2, DSR §2.2.3, CPCV §2.2.4, MDS §2.4.1 (per Task 10a, commit `0e368a8`)
