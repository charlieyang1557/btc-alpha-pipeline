# B-C-narrow Phase 1 — Pre-Implementation Gates Sub-Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to execute this sub-plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Sub-plan scope:** Phase 1 of B-C-narrow data-recovery cycle ONLY — **BLOCKING pre-implementation verification gates** at the current `origin/main` HEAD post Phase 0 SEAL. NO engine code edits. NO producer code edits. NO test scaffolding. NO data writes outside the verification artifacts themselves. Pure observation + classification + symlink integrity check + acknowledgment of pre-satisfied Phase 0 gate.

**Sub-plan motivation:** Plan v3.5-Phase0 (sealed at commit `9e7c42b`; implementation at `ebc0d26` + `fd1b7ea` + `8f64712` + `bedc9b4` + `f112599` per Charlie register PV3-SPLIT-BY-PHASE) completed Phase 0 engine extension with 13/13 GREEN. Per spec §4.1 (`docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md` at `d6c7fc0`), Phase 2 producer TDD requires 4 BLOCKING gates to pass FIRST. This sub-plan executes those 4 gates as discrete verification tasks (T5-T8 per spec §5 Phase 1 enumeration), enabling Charlie register-event #N+1 (Phase 1 ratify → Phase 2 drafting authorization) per anti-pre-emption discipline.

**Tech Stack:** Python 3.11+, pytest (for G3.5 acknowledgment only), git (G1 audit), `find` + `wc` (G3 inventory).

**Cycle context:** R6.1 V_SEAL §10 binding precondition (`d6c7fc0` spec doc; B-C-narrow cycle entry Charlie register N1 2026-05-26). Phase 0 (engine extension) SEALED at task level 2026-05-27 per Charlie register SEAL-TASK-LEVEL (no Phase Marker advance per anti-pre-emption — arc-level closeout reserved for full B-C-narrow cycle SEAL after Phase 4). This sub-plan is Phase 1; Phase 2/3/4 sub-plans drafted SEPARATELY per Charlie register chain.

---

## File Structure (Phase 1 scope only)

| File | Action | Scope |
|---|---|---|
| `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-1-pre-impl-gates-plan.md` | CREATE | this plan |
| `docs/superpowers/phase-1-gate-results/g1-engine-diff-audit.md` | CREATE at T5 | G1 commit classification table + adjudication rationale |
| `docs/superpowers/phase-1-gate-results/g2-dsl-backward-compat-sample.json` | CREATE at T6 | G2 per-candidate validation results (≥39 samples) |
| `docs/superpowers/phase-1-gate-results/g3-raw-payloads-inventory.md` | CREATE at T7 | G3 symlink inventory + resolution check |
| `docs/superpowers/phase-1-gate-results/phase-1-ratify-summary.md` | CREATE at T9 | comprehensive Phase 1 ratify packet for Charlie register-event |

**No code files modified.** No engine.py / tests/ / scripts/ / config/ changes. All deliverables are evidence artifacts under `docs/superpowers/phase-1-gate-results/`.

---

## Pre-Phase-1 Charlie register-event boundary (HISTORICAL — Phase 0 SEAL fulfilled)

Phase 0 task-level SEAL acknowledged 2026-05-27 per Charlie register `SEAL-TASK-LEVEL` (no Phase Marker advance). Phase 0 evidence chain (now on origin/main):

| Commit | Role |
|---|---|
| `9e7c42b` | Plan v3.5-Phase0 SEALED (post PFR R4 convergent APPROVE-WITH-FINDINGS; all 4 R4 findings closed inline) |
| `ebc0d26` | T1 RED-phase tests (13 new methods + shared fixtures + 2 stub edits) |
| `fd1b7ea` | pc9 BASELINE 2191 → 2204 amend (B-C-narrow Phase 0 cohort addition; T1-amend per Charlie AMEND-PC9-INLINE-A) |
| `8f64712` | T2 RegimeHoldoutResult dataclass +equity_curve field + call-site update |
| `bedc9b4` | T3 run_regime_holdout signature +4 LC-b kwargs |
| `f112599` | T4 body LC-b construction (preflight + atomic write-then-registry + 2 helpers + 3 imports; subagent dispatch per Charlie EXEC-SUBAGENT-TASK-4) |

Phase 0 final state: 13/13 PASS on TestBCNarrowPhase0EngineExtension; full suite 2328 passed / 0 failed / 2 xfailed.

Plan v3-Phase1 drafting authorized 2026-05-27 per Charlie register `PLAN-V3-PHASE-1-DRAFTING` (separate register-event from B per anti-pre-emption).

---

# Phase 1 — BLOCKING pre-impl gates (Tasks 5-9)

## Task 5: G1 Engine-diff audit

**Spec reference:** §4.1 G1 — classify 3 commits at `git log --oneline d0b8101..506285b -- backtest/` as semantics-affecting vs additive-only.

**Pass criteria:** All 3 commits classified additive-only → V4 ε=1e-6 expected achievable at §4.2 post-impl gate. Any semantics-affecting → Charlie register adjudication (widen ε with rationale; reject Q2; or accept drift).

**The 3 commits (verified at plan drafting time):**

| Commit | Subject (first line) |
|---|---|
| `ec647dc` | feat(b-c-extended/t1.6): fire T1.6 documentation + consumer enumeration SEAL |
| `12dffde` | feat(b-c-extended/t1.1): fire T1.1 artifact writer SEAL — revalidate_for_write() centralized 14-field tamper closure |
| `44840a3` | docs(phase5): fire R3.1d cost-grid re-anchor V_SEAL — conservative anchor 15 bps/side |

- [ ] **Step 5.1: Inspect each commit's backtest/ diff for numerical-path impact**

For each of the 3 commits, run:

```bash
git show --stat <commit> -- backtest/
git show <commit> -- backtest/engine.py | head -200
```

Focus on whether the diff touches: `single_run`, `run_backtest`, `run_regime_holdout`, `_evaluate_regime_holdout_pass`, slippage/cost computation, equity_curve series construction, or any function in the V4 reproducibility chain. Classify each commit as:

- **ADDITIVE-ONLY**: introduces new code paths (new functions, new optional kwargs with backward-compat defaults, new test/contract files) without modifying existing numerical pipelines. Verified by: existing tests still GREEN at the commit, no signature changes to V4-chain functions, no slippage/fee/order-execution semantics changes.
- **SEMANTICS-AFFECTING**: modifies code path of `single_run` / `run_regime_holdout` / numerical compute (slippage, fees, Sharpe denominator, NaN handling, etc.). Any such commit triggers Charlie register adjudication.

- [ ] **Step 5.2: Write classification artifact**

Write `docs/superpowers/phase-1-gate-results/g1-engine-diff-audit.md` with table:

```markdown
| Commit | Subject | Files touched in backtest/ | Numerical-path impact | Classification | Rationale |
|---|---|---|---|---|---|
| ec647dc | T1.6 SEAL ... | <list> | <none / single_run / ...> | ADDITIVE-ONLY or SEMANTICS-AFFECTING | <citation evidence> |
| 12dffde | T1.1 SEAL ... | <list> | ... | ... | ... |
| 44840a3 | R3.1d V_SEAL ... | <list> | ... | ... | ... |
```

Include per-commit cited line-range evidence (e.g., "ec647dc: `backtest/wf_lineage.py` lines 70-95 — adds CORRECTED_WF_ENGINE_COMMIT constant + ENGINE_CORRECTED_LINEAGE_TAG; constants-only addition, no numerical path touched").

- [ ] **Step 5.3: G1 pass/fail determination**

If ALL 3 commits classified ADDITIVE-ONLY → G1 PASS. Proceed to Task 6.

If ANY commit classified SEMANTICS-AFFECTING → G1 FAIL → STOP and surface to Charlie. Adjudication paths per spec §4.1:
  1. Widen ε with documented rationale + evidence;
  2. Reject Q2 lock + escalate Q2 re-litigation;
  3. Accept drift + update INDETERMINATE classification.

NO automatic widening of ε without Charlie register.

---

## Task 6: G2 StrategyDSL backward-compat sample

**Spec reference:** §4.1 G2 — sample N ≥ 39 attempt responses from recovered `raw_payloads/`; `StrategyDSL.model_validate(json.loads(...))` succeeds at current Pydantic schema (HEAD = `f112599`).

**Pass criteria:** 100% sample pass. Any failure → Charlie register adjudication (identify schema-drift commit; fix or rollback).

**Sample selection:** the 39 cohort_a candidates per spec §1 (the cohort targeted by post-V_SEAL Tier 6 evaluation). Producer recovers these from raw_payloads at `tests/conftest.py:_load_dsl_from_response` precedent (already validated in Phase 0 fixture `dsl_bollinger_zscore_reversion`).

- [ ] **Step 6.1: Write sampling + validation script**

Create `docs/superpowers/phase-1-gate-results/g2-validate.py` (ephemeral; commit alongside results then can delete OR keep as audit trail):

```python
"""G2 StrategyDSL backward-compat validation.

Loads 39 cohort_a candidate DSL JSONs from raw_payloads/ and runs
StrategyDSL.model_validate() at the current Pydantic schema (HEAD f112599).
Writes results to g2-dsl-backward-compat-sample.json.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from strategies.dsl import StrategyDSL
from scripts.run_phase2c_evaluation_gate import _strip_markdown_fence


def load_cohort_a_attempts(combined_dir: Path) -> list[tuple[str, Path]]:
    """Enumerate cohort_a attempt response files from combined synthetic dir.

    Returns list of (hypothesis_hash, response_path) pairs for the 39
    cohort_a candidates per spec §1.
    """
    # TODO at implementation: list cohort_a attempts. Strategy: read the
    # source_stage2d_summary_*.json symlinks in combined_dir to identify
    # cohort_a hypothesis_hashes (16-char per agents/hypothesis_hash.py:154),
    # then resolve each to its attempt_NNNN_response.txt path. Implementation
    # subagent should grep + parse the summary JSONs at execution time.
    raise NotImplementedError(
        "Implementation subagent: enumerate via source_stage2d_summary_*.json "
        "+ resolve to attempt response paths. See _load_dsl_from_response at "
        "scripts/run_phase2c_evaluation_gate.py for the pattern."
    )


def validate_one(response_path: Path) -> dict:
    """Validate a single attempt response → StrategyDSL.

    Returns: {"path": str, "hypothesis_hash": str, "pass": bool, "error": str | None}.
    """
    raw = response_path.read_text(encoding="utf-8")
    payload_text = _strip_markdown_fence(raw)
    try:
        payload = json.loads(payload_text)
        StrategyDSL.model_validate(payload)
        return {"path": str(response_path), "pass": True, "error": None}
    except Exception as e:
        return {"path": str(response_path), "pass": False, "error": f"{type(e).__name__}: {e}"}


def main() -> int:
    combined = REPO_ROOT / "raw_payloads" / "batch_phase2c_15_main_fire_combined"
    attempts = load_cohort_a_attempts(combined)
    if len(attempts) < 39:
        print(f"FAIL: cohort_a sample size {len(attempts)} < 39 minimum", file=sys.stderr)
        return 2

    results = [validate_one(p) for _, p in attempts]
    n_pass = sum(1 for r in results if r["pass"])
    n_fail = len(results) - n_pass

    output_path = REPO_ROOT / "docs" / "superpowers" / "phase-1-gate-results" / "g2-dsl-backward-compat-sample.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({
        "n_total": len(results),
        "n_pass": n_pass,
        "n_fail": n_fail,
        "pass_rate": n_pass / len(results) if results else 0.0,
        "head_commit": "f112599",
        "per_attempt": results,
    }, indent=2))

    if n_fail > 0:
        print(f"G2 FAIL: {n_fail}/{len(results)} attempts failed validation", file=sys.stderr)
        return 1

    print(f"G2 PASS: {n_pass}/{len(results)} attempts validate cleanly at HEAD f112599")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6.2: Run validation script**

```bash
cd /Users/yutianyang/Documents/GitHub/btc-alpha-pipeline
python docs/superpowers/phase-1-gate-results/g2-validate.py
```

Expected: exit code 0 + `g2-dsl-backward-compat-sample.json` written with `n_fail == 0` and `pass_rate == 1.0`.

- [ ] **Step 6.3: G2 pass/fail determination**

If `n_fail == 0` → G2 PASS. Proceed to Task 7.

If `n_fail > 0` → G2 FAIL → STOP. Surface failing per-attempt entries to Charlie. Adjudication paths:
  1. Identify the schema-drift commit (likely in pydantic schema or DSL validator history; `git log strategies/dsl.py` post the original recovery commit may show the drift point);
  2. Fix the schema or rollback the drift commit;
  3. Or accept partial validation + flag in §8 NOTE.

---

## Task 7: G3 Raw_payloads inventory

**Spec reference:** §4.1 G3 — 5 cohort_a sub-batch dirs + combined synthetic dir; combined dir has 993 attempt symlinks + 5 source_stage2d_summary_*.json symlinks (998 total); all symlinks resolve.

**Pass criteria:** Inventory matches; all symlinks resolve. Failure → re-run rsync from cold-storage.

- [ ] **Step 7.1: Count symlinks in combined dir**

```bash
cd /Users/yutianyang/Documents/GitHub/btc-alpha-pipeline
find raw_payloads/batch_phase2c_15_main_fire_combined -type l | wc -l
```

Expected: exactly `998`. If different, surface delta + sub-counts:

```bash
find raw_payloads/batch_phase2c_15_main_fire_combined -type l -name "attempt_*" | wc -l   # expected 993
find raw_payloads/batch_phase2c_15_main_fire_combined -type l -name "source_stage2d_summary_*.json" | wc -l   # expected 5
```

- [ ] **Step 7.2: Verify all symlinks resolve (no broken)**

```bash
find raw_payloads/batch_phase2c_15_main_fire_combined -type l ! -exec test -e {} \; -print | head -20
```

Expected: empty output (no broken symlinks). Any path printed → broken symlink → G3 FAIL → re-run rsync from cold-storage (per spec §4.1 G3 + cold-storage registry at `docs/operations/MAC_MINI_DATA_REFERENCE.md`).

- [ ] **Step 7.3: Write inventory artifact**

Write `docs/superpowers/phase-1-gate-results/g3-raw-payloads-inventory.md`:

```markdown
# G3 Raw_payloads inventory result

**Verified at:** <ISO timestamp UTC>
**HEAD commit:** f112599

## Combined dir symlink counts

| Subset | Expected | Actual | Match |
|---|---|---|---|
| `attempt_*` symlinks | 993 | <N> | ✅ / ❌ |
| `source_stage2d_summary_*.json` symlinks | 5 | <N> | ✅ / ❌ |
| **TOTAL** | **998** | **<N>** | ✅ / ❌ |

## Symlink resolution

`find ... -type l ! -exec test -e {} \;` output: <empty / list of broken paths>

## 5 cohort_a sub-batch dirs

| Batch UUID | Source stage 2d summary | Attempt count |
|---|---|---|
| <UUID 1> | source_stage2d_summary_*.json | <count> |
| ... | ... | ... |

## Verdict

G3 = **PASS** / **FAIL**
```

- [ ] **Step 7.4: G3 pass/fail determination**

If all 3 sub-checks pass → G3 PASS. Proceed to Task 8.

If any sub-check fails → G3 FAIL → STOP. Re-run rsync from cold-storage per `docs/operations/MAC_MINI_DATA_REFERENCE.md` SSH alias `mac-mini-cold-storage`. Charlie register required to authorize re-rsync.

---

## Task 8: G3.5 RegimeHoldoutResult.equity_curve smoke acknowledgment

**Spec reference:** §4.1 G3.5 — `RegimeHoldoutResult` dataclass includes `equity_curve: pd.Series` field; smoke test passes.

**Pass criteria:** Engine extension complete + tested in isolation. **ALREADY SATISFIED** at Phase 0 commits `8f64712` (dataclass +field) + `f112599` (body populates equity_curve from BacktestResult).

- [ ] **Step 8.1: Re-run Phase 0 smoke evidence**

The smoke test = `test_regime_holdout_result_dataclass_exact_field_set` + `test_run_regime_holdout_returns_result_with_equity_curve_populated`:

```bash
cd /Users/yutianyang/Documents/GitHub/btc-alpha-pipeline
python -m pytest tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension::test_regime_holdout_result_dataclass_exact_field_set tests/test_t1_1_artifact_writer.py::TestBCNarrowPhase0EngineExtension::test_run_regime_holdout_returns_result_with_equity_curve_populated -v
```

Expected: 2 PASS (already GREEN per Phase 0 SEAL).

- [ ] **Step 8.2: Acknowledge pre-satisfied status**

No new artifact needed — G3.5 is acknowledged as pre-satisfied by Phase 0 SEAL evidence chain. Include this in Task 9 ratify summary.

---

## Task 9: Phase 1 ratify packet

- [ ] **Step 9.1: Write comprehensive ratify summary**

Write `docs/superpowers/phase-1-gate-results/phase-1-ratify-summary.md`:

```markdown
# B-C-narrow Phase 1 ratify packet

**Date:** <ISO UTC>
**HEAD commit:** f112599
**Plan version:** v3-Phase1 (sealed at <plan-commit-hash>)

## Gate results

| Gate | Spec ref | Result | Evidence |
|---|---|---|---|
| G1 — Engine-diff audit | §4.1 | PASS / FAIL | g1-engine-diff-audit.md |
| G2 — StrategyDSL backward-compat | §4.1 | PASS / FAIL | g2-dsl-backward-compat-sample.json |
| G3 — Raw_payloads inventory | §4.1 | PASS / FAIL | g3-raw-payloads-inventory.md |
| G3.5 — Engine extension smoke | §4.1 | PASS (pre-satisfied) | Phase 0 commits 8f64712 + f112599 |

## Overall verdict

ALL gates PASS → Phase 2 producer-TDD sub-plan drafting authorized at separate Charlie register-event.

ANY gate FAIL → adjudication required per spec §4.1 per-gate failure paths.

## Next register-event (#N+1)

- Phase 1 ratify acknowledgment
- (If all PASS) Phase 2 sub-plan drafting authorization
- (If any FAIL) per-gate adjudication
```

- [ ] **Step 9.2: Commit Phase 1 evidence**

```bash
git add docs/superpowers/phase-1-gate-results/
git commit -m "evidence(b-c-narrow/phase-1): G1+G2+G3+G3.5 gate results (Phase 1 ratify packet)

Per Plan v3-Phase1 Tasks 5-9 + spec §4.1 BLOCKING pre-impl gates.

Gates: G1 engine-diff audit (3 commits classified), G2 DSL backward-compat
(N=<count> sample), G3 raw_payloads inventory (998 symlinks), G3.5 engine
extension smoke (pre-satisfied by Phase 0 SEAL).

Verdict: <ALL PASS / details>. Phase 1 ratify gate met; awaiting Charlie
register-event #N+1 for Phase 2 sub-plan drafting authorization."
```

Do NOT push (orchestrator handles).

- [ ] **Step 9.3: Charlie register-event #N+1**

**STOP HERE.** Surface to Charlie:
- 4 gate verdicts (PASS/FAIL per gate)
- Phase 1 ratify packet content
- Evidence artifact paths
- Push decision option
- Phase 2 drafting authorization option (separate register-event from ratify; anti-pre-emption discipline)

Do NOT auto-fire Phase 2 drafting; that requires Charlie register-event #N+2.

---

## DEFER items (Phase 1 scope only)

**Phase-1-internal:** NONE. All 4 gates (G1/G2/G3/G3.5) executed in this sub-plan.

**Phase 2+ blockers DEFERRED** to respective sub-plans per spec §5 enumeration:
- **Phase 2** (T9-T11 producer TDD): R9 architectural call-order flaw fix, `_finalize_batch_registry` create_table addition, `_parse_args` → `_build_argparser` rename, `_CSV_FIELDS` extension, archive idempotency guard, T1.4 baseline maintenance update. Drafting requires Charlie register-event #N+2 after Phase 1 ratify.
- **Phase 3** (T12-T14b fire): 39-candidate cohort_a re-run with `parquet_data_sha256` populated + per-bar artifacts + γ3/γ4 moments + V4 reproducibility gate (ε=1e-6). Drafting requires Charlie register-event #N+3 after Phase 2 SEAL.
- **Phase 4** (T15-T16 SEAL): B-C-narrow data-recovery cycle SEAL artifact + Phase Marker advance (arc-level closeout). Drafting requires Charlie register-event #N+4 after Phase 3 SEAL.

Each sub-plan requires separate Charlie register-event for drafting authorization per anti-pre-emption discipline.

---

## Execution Handoff

Plan v3-Phase1 v1 saved to `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-1-pre-impl-gates-plan.md`.

After Plan v3-Phase1 B2 2-leg PFR returns APPROVE (or APPROVE-WITH-FINDINGS at LOW-only floor) → use **superpowers:subagent-driven-development** per Charlie register PV3-SPLIT-BY-PHASE: dispatch fresh subagent per task with two-stage review OR orchestrator-manual execution per Charlie register-event-by-register-event.

After Phase 1 SEALED (Task 9 ratify) → request Charlie register-event for Plan v3-Phase2 sub-plan drafting authorization (separate fire — anti-pre-emption discipline preserved).
