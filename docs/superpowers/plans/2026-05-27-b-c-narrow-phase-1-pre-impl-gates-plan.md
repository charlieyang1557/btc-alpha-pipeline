# B-C-narrow Phase 1 — Pre-Implementation Gates Sub-Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to execute this sub-plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Sub-plan scope:** Phase 1 of B-C-narrow data-recovery cycle ONLY — **BLOCKING pre-implementation verification gates** at the current `origin/main` HEAD post Phase 0 SEAL. NO engine code edits. NO producer code edits. NO test scaffolding. NO data writes outside the verification artifacts themselves. Pure observation + classification + symlink integrity check + acknowledgment of pre-satisfied Phase 0 gate.

**Sub-plan motivation:** Plan v3.5-Phase0 (sealed at commit `9e7c42b`; implementation at `ebc0d26` + `fd1b7ea` + `8f64712` + `bedc9b4` + `f112599` per Charlie register PV3-SPLIT-BY-PHASE) completed Phase 0 engine extension with 13/13 GREEN. Per spec §4.1 (`docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md` at `d6c7fc0`), Phase 2 producer TDD requires 4 BLOCKING gates to pass FIRST. This sub-plan executes those 4 gates as discrete verification tasks (T5-T8 per spec §5 Phase 1 enumeration), enabling Charlie register-event #N+1 (Phase 1 ratify ONLY; Phase 2 sub-plan drafting authorization is a SEPARATE register-event #N+2 per anti-pre-emption discipline — see PFR R1 F3 fix v2).

**Tech Stack:** Python 3.11+, pytest (for G3.5 acknowledgment only), git (G1 audit), `find` + `wc` (G3 inventory).

**Cycle context:** R6.1 V_SEAL §10 binding precondition (`d6c7fc0` spec doc; B-C-narrow cycle entry Charlie register N1 2026-05-26). Phase 0 (engine extension) SEALED at task level 2026-05-27 per Charlie register SEAL-TASK-LEVEL (no Phase Marker advance per anti-pre-emption — arc-level closeout reserved for full B-C-narrow cycle SEAL after Phase 4). This sub-plan is Phase 1; Phase 2/3/4 sub-plans drafted SEPARATELY per Charlie register chain.

---

## File Structure (Phase 1 scope only)

| File | Action | Scope |
|---|---|---|
| `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-1-pre-impl-gates-plan.md` | CREATE | this plan |
| `docs/superpowers/phase-1-gate-results/g1-engine-diff-audit.md` | CREATE at T5 | G1 commit classification table + adjudication rationale |
| `docs/superpowers/phase-1-gate-results/g2-validate.py` | CREATE at T6 | G2 ephemeral validation script (PFR R2 LOW-4 fix v3 — was omitted in v2 File Structure) |
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

## Phase 1 execution preconditions (PFR R1 v2 additions)

Before any T5-T8 execution, verify:

- [ ] **Precondition 1: Clean working tree (PFR R1 LOW NEW-2 fix v2 + PFR R2 HIGH-2/NEW-2 fix v3)**

V4 reproducibility claims reference HEAD `f112599`. If any code module touched by a Phase 1 gate has unstaged modifications mid-execution, the gates execute against modified files but report results as-of `f112599` — silent breach. Verify clean state:

```bash
git status --porcelain backtest/ tests/ config/ scripts/ strategies/ factors/
```

PFR R2 HIGH-2 fix v3 scope extensions: g2-validate.py imports from `scripts/run_phase2c_evaluation_gate` (`_strip_markdown_fence`) + `strategies/dsl` (`StrategyDSL`) + optionally `strategies/dsl_compiler` (`compile_dsl_to_strategy`) which in turn uses `factors/registry` (`FactorRegistry`). Unstaged modifications in any of these would silently affect Phase 1 gate results while claims reference HEAD `f112599`.

Expected: empty output. Any output → STOP and surface to Charlie (uncommitted changes must be either committed or stashed before Phase 1 gates run).

- [ ] **Precondition 2: Writable execution environment (PFR R1 LOW F6 fix v2)**

PFR R1 LOW F6 observed: read-only review environments (e.g., Codex sandbox) may fail G3.5 smoke tests with `FileNotFoundError: No usable temporary directory found`. Phase 1 execution requires a writable environment (the agent must be able to create + write to pytest's `tmp_path` fixtures). Verify:

```bash
python -c "import tempfile; f = tempfile.NamedTemporaryFile(); print(f'writable: {f.name}'); f.close()"
```

Expected: prints a temp file path successfully. Failure → environment issue, NOT a real test failure; surface to Charlie for environment remediation.

---

## Task 5: G1 Engine-diff audit

**Spec reference:** §4.1 G1 — classify commits at `git log --oneline d0b8101..506285b -- backtest/` (spec-original range) as NUMERICAL-PATH vs REGISTRY/LINEAGE-ONLY vs API/OPTIONAL-ADDITIVE vs DOC/TEST-ONLY.

**Pass criteria:** Zero commits classified NUMERICAL-PATH → V4 ε=1e-6 expected achievable at §4.2 post-impl gate. Any NUMERICAL-PATH commit → Charlie register adjudication (widen ε with rationale; reject Q2; or accept drift).

**The 3 commits in spec-original range (verified at plan drafting time):**

| Commit | Subject (first line) |
|---|---|
| `ec647dc` | feat(b-c-extended/t1.6): fire T1.6 documentation + consumer enumeration SEAL |
| `12dffde` | feat(b-c-extended/t1.1): fire T1.1 artifact writer SEAL — revalidate_for_write() centralized 14-field tamper closure |
| `44840a3` | docs(phase5): fire R3.1d cost-grid re-anchor V_SEAL — conservative anchor 15 bps/side |

**Phase 0 commits between `506285b` and HEAD `f112599` (Phase 0 SEAL chain — PRE-CLASSIFIED ADDITIVE-FOR-LEGACY-NUMERICAL-PATH per PFR R1 H1 fix v2):**

Per Advisor R1 H1: Plan v1 inherited spec's commit range `d0b8101..506285b` verbatim but current HEAD is `f112599`. Between `506285b` and `f112599` there are 3 additional `backtest/engine.py`-touching commits from Phase 0 itself (`8f64712` + `bedc9b4` + `f112599`). Phase 0 SEAL evidence chain (commit chain at plan §"Pre-Phase-1 Charlie register-event boundary (HISTORICAL)") + the 13/13 GREEN test suite at `f112599` + the single-gate `lcb_active = artifact_dir is not None` (legacy path `artifact_dir=None` is bit-exact preserved pre-Phase-0) jointly establish that these 3 commits are **API/OPTIONAL-ADDITIVE** for the LC-b path (new functionality gated by new kwargs) and **ADDITIVE-FOR-LEGACY-NUMERICAL-PATH** for the legacy path (the path used by the original `phase4_forward_2026_15bps_v1` fire). The V4 reproducibility surface — bit-exact replay of the original fire — uses the legacy path; the LC-b path is new behavior, not a replacement of the V4 surface.

This is the Advisor R1 H1 option-(b) framing: explicit acknowledgment via Phase 0 SEAL evidence rather than expanding G1 commit-range to `d0b8101..HEAD`. Phase 0 commits are NOT re-audited here; their additive-by-design status is locked by the Phase 0 task-level SEAL register-event.

**Classification framework (PFR R1 F4 fix v2 — adopt Codex 4-category framework over plan v1's binary):**

| Category | Definition | Triggers V4 ε adjudication? |
|---|---|---|
| **NUMERICAL-PATH** | Modifies `single_run` / `run_backtest` / `run_regime_holdout` / `_evaluate_regime_holdout_pass` / slippage / fees / Sharpe denominator / NaN handling / equity_curve computation in a way that changes outputs for the legacy call pattern | YES |
| **REGISTRY/LINEAGE-ONLY** | Modifies `_write_to_registry` / artifact write paths / lineage-context plumbing / experiment registry schema, WITHOUT changing the numerical inputs/outputs of the backtest engine | NO |
| **API/OPTIONAL-ADDITIVE** | Adds new optional kwargs with backward-compat defaults / new helper functions / new module-level constants; legacy callers see no behavior change | NO |
| **DOC/TEST-ONLY** | Doc files, test files, comments, doc-string changes; no production engine path touched | NO |

- [ ] **Step 5.1: Full-file diff audit + targeted symbol grep per commit**

PFR R1 F2 fix v2 — replace v1's `git show ... | head -200` (truncation could miss critical hunks; `12dffde` diff is 1061 lines, and `run_regime_holdout` hunks are in the 1440-1585 range). v2 uses full-file diff + targeted `rg` over numerical-path symbols:

For each of the 3 commits (`ec647dc`, `12dffde`, `44840a3`):

```bash
# Step A: enumerate files touched in backtest/
git show --stat <commit> -- backtest/

# Step B: full-file diff (NO head truncation) — pipe to less or paginate
git show <commit> -- backtest/ | less    # OR write to file for offline inspection
git show <commit> -- backtest/ > /tmp/g1-<commit>.diff

# Step C: targeted symbol grep over numerical-path identifiers
# PFR R2 LOW-3 / NEW-1 fix v3: extended symbol list with compute_all_metrics
# (metrics aggregator at engine.py:758) + compute_moments (γ3/γ4 introduced
# in 12dffde; sibling of compute_per_bar_returns).
git show <commit> -- backtest/ | rg -nC2 \
    'run_backtest|run_regime_holdout|single_run|_evaluate_regime_holdout_pass|slippage|fee_model|cost_model|sharpe_ratio|max_drawdown|equity_curve|_save_trade_csv|compute_per_bar_returns|compute_all_metrics|compute_moments'

# Step D: schema-only delta — verify no V4-chain function signature changes
git show <commit> -- backtest/ | rg '^\s*def (run_backtest|run_regime_holdout|single_run|_evaluate_regime_holdout_pass)'
```

For each hit in Step C: classify the hunk's semantic effect (e.g., is the `run_backtest` reference a new caller path, or an in-place modification of the function body?). Use the 4-category framework above.

- [ ] **Step 5.2: Write classification artifact**

Write `docs/superpowers/phase-1-gate-results/g1-engine-diff-audit.md` with table:

```markdown
| Commit | Subject | Files touched in backtest/ (count) | Symbol grep hits (Step C summary) | Classification | Rationale (with cited line-range evidence) |
|---|---|---|---|---|---|
| ec647dc | T1.6 SEAL ... | <N files> | <hit summary> | NUMERICAL-PATH / REGISTRY/LINEAGE-ONLY / API/OPTIONAL-ADDITIVE / DOC/TEST-ONLY | <citation evidence with line ranges> |
| 12dffde | T1.1 SEAL ... | <N files> | <hit summary> | <one of 4 categories> | <citation evidence> |
| 44840a3 | R3.1d V_SEAL ... | <N files> | <hit summary> | <one of 4 categories> | <citation evidence> |
```

Include per-commit cited line-range evidence (e.g., "12dffde: `backtest/engine.py:1440-1585` — `_write_to_registry` body extension for 14-field tamper closure; FIX-H2 at `_rh_effective_exec_path` derivation is API/OPTIONAL-ADDITIVE for the lineage_context-passing callers (Phase 0 LC-b path), NOT NUMERICAL-PATH because legacy callers passing scalar `execution_config_path` see unchanged behavior").

Append Phase 0 commits pre-classification rationale (PFR R1 H1 fix v2):

```markdown
### Phase 0 commits (506285b..f112599) — PRE-CLASSIFIED by SEAL evidence

| Commit | Subject | Pre-classification | Evidence |
|---|---|---|---|
| 8f64712 | T2 RegimeHoldoutResult.equity_curve field | API/OPTIONAL-ADDITIVE | New dataclass field + call-site update; legacy callers always receive populated equity_curve (no opt-out, but semantically the field is new metadata, not a numerical-input). |
| bedc9b4 | T3 run_regime_holdout signature +4 LC-b kwargs | API/OPTIONAL-ADDITIVE | All 4 kwargs default None for backward-compat; cost_anchor_id INTENTIONALLY omitted (derived in LC __post_init__). |
| f112599 | T4 body LC-b construction + preflight + 2 helpers | API/OPTIONAL-ADDITIVE for LC-b path; legacy path unchanged | Single-gate `lcb_active = artifact_dir is not None`; with `artifact_dir=None`, body is bit-exact pre-Phase-0 (run_backtest → _write_to_registry with no LC); with `artifact_dir != None`, NEW LC-b path activated (preflight + LC construction + atomic write). 13/13 PASS in TestBCNarrowPhase0EngineExtension validates both paths. |
```

- [ ] **Step 5.3: G1 pass/fail determination**

If ALL 3 spec-range commits classified NON-NUMERICAL-PATH (any of REGISTRY/LINEAGE-ONLY, API/OPTIONAL-ADDITIVE, DOC/TEST-ONLY) → G1 PASS. Proceed to Task 6.

If ANY commit classified NUMERICAL-PATH → G1 FAIL → STOP and surface to Charlie. Adjudication paths per spec §4.1:
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

Create `docs/superpowers/phase-1-gate-results/g2-validate.py` (commit alongside results as audit trail).

PFR R1 BLOCKING F1 fix (v2): concrete cohort_a enumeration replacing v1's NotImplementedError stub. The enumeration logic:
1. Read `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv`; extract `hypothesis_hash` column; ASSERT exactly 39 unique hashes (cohort_a universe per spec §1; verified empirically — CSV has 40 lines = 39 candidates + header).
2. Parse all 5 `source_stage2d_summary_*.json` files in `raw_payloads/batch_phase2c_15_main_fire_combined/` (NOT symlink targets — read directly via the symlinks; they resolve to the source batch dirs). Each summary's `calls` list has `hypothesis_hash` + `position` per entry; total ~993 calls indexed across 5 batches.
3. Build a single `hash → (batch_id, position)` index from all 5 summaries.
4. For each of the 39 cohort_a hashes, look up `(batch_id, position)` and resolve to attempt path: `raw_payloads/batch_<batch_id>/attempt_<position:04d>_response.txt` (the batch-specific authoritative path — NOT via combined dir's symlink, which uses a different naming scheme).
5. Assert all 39 paths exist; STOP-and-surface if any missing.
6. Validate each via `StrategyDSL.model_validate(json.loads(_strip_markdown_fence(raw)))`; emit per-attempt result.

```python
"""G2 StrategyDSL backward-compat validation (Phase 1 v2 per PFR R1 F1 fix).

Reads 39 cohort_a candidate hashes from holdout_results.csv → maps each via
source_stage2d_summary_*.json to its batch-specific attempt response file →
runs StrategyDSL.model_validate() at the current Pydantic schema (HEAD f112599).
Writes results to g2-dsl-backward-compat-sample.json.

All stdout logging includes ISO 8601 UTC timestamps per CLAUDE.md Coding Standards.
"""
from __future__ import annotations
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from strategies.dsl import StrategyDSL  # noqa: E402
from scripts.run_phase2c_evaluation_gate import _strip_markdown_fence  # noqa: E402


def _ts() -> str:
    """ISO 8601 UTC timestamp prefix for log lines.

    PFR R1 LOW L2 fix v2: this helper applies CLAUDE.md Coding Standards
    "All scripts log to stdout with ISO 8601 UTC timestamps" requirement.
    Used in all print() calls below.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_cohort_a_hashes() -> list[str]:
    """Read holdout_results.csv and return the 39 cohort_a hypothesis_hashes
    in CSV row order.

    PFR R1 F1 fix: cohort selection is anchored to the CSV (authoritative
    cohort_a universe per spec §1 + verified empirically: CSV has 40 lines =
    39 candidates + header).
    """
    csv_path = REPO_ROOT / "data" / "phase2c_evaluation_gate" / "phase4_forward_2026_15bps_v1" / "holdout_results.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"G2 BLOCKING: cohort_a CSV missing at {csv_path}. "
            f"Required for cohort_a enumeration per spec §1."
        )
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        if "hypothesis_hash" not in (reader.fieldnames or []):
            raise ValueError(
                f"G2 BLOCKING: holdout_results.csv missing hypothesis_hash column. "
                f"Fields: {reader.fieldnames}"
            )
        hashes = [row["hypothesis_hash"] for row in reader]
    unique = set(hashes)
    if len(unique) != 39:
        raise ValueError(
            f"G2 BLOCKING: cohort_a universe expected 39 unique hashes; "
            f"got {len(unique)} unique from {len(hashes)} rows. "
            f"Spec §1 lock requires exactly 39."
        )
    return hashes


def build_hash_to_call_index() -> dict[str, tuple[str, int]]:
    """Parse all 5 source_stage2d_summary_*.json files and build a single
    hash → (batch_id, position) index.

    PFR R1 F1 fix: this is the authoritative hash→attempt resolution layer.
    Combined-dir attempt_NNNN_response.txt symlinks use a DIFFERENT (renumbered)
    naming scheme; we resolve via batch-specific paths instead.
    """
    combined_dir = REPO_ROOT / "raw_payloads" / "batch_phase2c_15_main_fire_combined"
    summary_paths = sorted(combined_dir.glob("source_stage2d_summary_*.json"))
    if len(summary_paths) != 5:
        raise FileNotFoundError(
            f"G2 BLOCKING: expected 5 source_stage2d_summary_*.json files; "
            f"got {len(summary_paths)} at {combined_dir}."
        )
    index: dict[str, tuple[str, int]] = {}
    for s in summary_paths:
        data = json.loads(s.read_text())
        batch_id = data["batch_id"]
        for call in data.get("calls", []):
            h = call.get("hypothesis_hash")
            if h is not None:
                index[h] = (batch_id, call["position"])
    return index


def resolve_attempt_path(hsh: str, index: dict[str, tuple[str, int]]) -> Path:
    """Resolve a cohort_a hash to its batch-specific attempt response path."""
    if hsh not in index:
        raise KeyError(
            f"G2 BLOCKING: hash {hsh!r} not found in stage2d call index "
            f"(spans {len(index)} entries across 5 batches). "
            f"Possible cause: cohort_a hash absent from the issued+parsed "
            f"call set, or summary JSON has been mutated."
        )
    batch_id, position = index[hsh]
    return REPO_ROOT / "raw_payloads" / f"batch_{batch_id}" / f"attempt_{position:04d}_response.txt"


def validate_one(hsh: str, response_path: Path) -> dict:
    """Validate a single attempt response → StrategyDSL.

    Returns: {"hypothesis_hash": str, "path": str, "pass": bool, "error": str | None}.
    """
    if not response_path.exists():
        return {
            "hypothesis_hash": hsh,
            "path": str(response_path),
            "pass": False,
            "error": f"FileNotFoundError: attempt path does not exist",
        }
    raw = response_path.read_text(encoding="utf-8")
    payload_text = _strip_markdown_fence(raw)
    try:
        payload = json.loads(payload_text)
        StrategyDSL.model_validate(payload)
        return {
            "hypothesis_hash": hsh,
            "path": str(response_path),
            "pass": True,
            "error": None,
        }
    except Exception as e:
        return {
            "hypothesis_hash": hsh,
            "path": str(response_path),
            "pass": False,
            "error": f"{type(e).__name__}: {e}",
        }


def main() -> int:
    print(f"{_ts()} G2 cohort_a backward-compat validation starting")
    cohort_hashes = load_cohort_a_hashes()
    print(f"{_ts()} cohort_a universe: {len(cohort_hashes)} hashes (expected 39)")
    if len(cohort_hashes) != 39:
        print(f"{_ts()} FAIL: cohort_a size {len(cohort_hashes)} != 39", file=sys.stderr)
        return 2
    index = build_hash_to_call_index()
    print(f"{_ts()} stage2d call index built: {len(index)} entries across 5 batches")
    missing = [h for h in cohort_hashes if h not in index]
    if missing:
        print(
            f"{_ts()} FAIL: {len(missing)} cohort_a hashes not found in call index: "
            f"{missing[:5]}...",
            file=sys.stderr,
        )
        return 2

    results = [validate_one(h, resolve_attempt_path(h, index)) for h in cohort_hashes]
    n_pass = sum(1 for r in results if r["pass"])
    n_fail = len(results) - n_pass

    output_path = REPO_ROOT / "docs" / "superpowers" / "phase-1-gate-results" / "g2-dsl-backward-compat-sample.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({
        "validated_at_utc": _ts(),
        "head_commit": "f112599",  # IMPLEMENTATION SUBAGENT: replace with `git rev-parse --short HEAD` value at execution time
        "cohort": "cohort_a (phase4_forward_2026_15bps_v1)",
        "cohort_source_csv": "data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv",
        "n_total": len(results),
        "n_pass": n_pass,
        "n_fail": n_fail,
        "pass_rate": n_pass / len(results) if results else 0.0,
        "per_attempt": results,
    }, indent=2))

    if n_fail > 0:
        print(
            f"{_ts()} G2 FAIL: {n_fail}/{len(results)} attempts failed validation. "
            f"See {output_path} for per-attempt details.",
            file=sys.stderr,
        )
        return 1

    print(f"{_ts()} G2 PASS: {n_pass}/{len(results)} attempts validate cleanly at HEAD f112599")
    print(f"{_ts()} Results written to {output_path}")
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

If `n_fail == 0` → G2 PASS. Proceed to Step 6.4 (optional spot-check) then Task 7.

If `n_fail > 0` → G2 FAIL → STOP. Surface failing per-attempt entries to Charlie. Adjudication paths:
  1. Identify the schema-drift commit (likely in pydantic schema or DSL validator history; `git log strategies/dsl.py` post the original recovery commit may show the drift point);
  2. Fix the schema or rollback the drift commit;
  3. Or accept partial validation + flag in §8 NOTE.

- [ ] **Step 6.4: OPTIONAL compile-only spot-check (PFR R1 MEDIUM M3 fix v2)**

PFR R1 MEDIUM M3 fix v2: pydantic `model_validate` catches structural schema drift but NOT semantic drift (e.g., factor names that no longer exist in `FactorRegistry`, condition operators that have changed semantics, position_sizing forms removed). G2 PASS at Step 6.3 does NOT guarantee Phase 3 fire reproducibility on cohort_a if factor-registry drift occurred between original fire (May 2026 batch) and current HEAD.

This optional step extends coverage by spot-checking 3 cohort_a candidates through DSL → BacktraderStrategy compilation (NO backtest run; compile-only):

```python
# Append to g2-validate.py OR run as separate g2-compile-spot.py at execution time
# PFR R2 HIGH-1 fix v3: function name is `compile_dsl_to_strategy` (not `compile_dsl`);
# pass `write_manifest=False` to respect Phase 1's NO-data-writes scope (default is
# True which writes data/compiled_strategies/<dsl_hash>.json per dsl_compiler.py:762-765).
from strategies.dsl_compiler import compile_dsl_to_strategy  # noqa: E402

def spot_check_compile(hsh: str, response_path: Path) -> dict:
    """Compile DSL → Backtrader strategy class (no backtest run; NO manifest write).
    Surfaces semantic drift that schema validation misses."""
    raw = response_path.read_text(encoding="utf-8")
    payload = json.loads(_strip_markdown_fence(raw))
    dsl = StrategyDSL.model_validate(payload)
    try:
        # write_manifest=False per Phase 1 NO-data-writes scope (PFR R2 HIGH-1 fix v3).
        compile_dsl_to_strategy(dsl, write_manifest=False)
        return {"hypothesis_hash": hsh, "compile_pass": True, "error": None}
    except Exception as e:
        return {"hypothesis_hash": hsh, "compile_pass": False, "error": f"{type(e).__name__}: {e}"}
```

Spot-check 3 candidates: the first, middle (~20th), and last from `cohort_hashes`. Surface compile failures separately from G2 schema results (compile failures are OUT OF SCOPE for G2 strict pass criteria per spec §4.1 lock; they are diagnostic-only at Phase 1, flagged for Phase 3 fire-time discovery).

This step is OPTIONAL — DEFER-acceptable per spec §4.1 lock. Run it during Phase 1 execution if cohort_a has any commit-history concern over factor registry; skip if cohort_a originates from a recent batch with no schema-drift potential.

- [ ] **Step 6.5: G2 verdict + optional compile spot-check report**

Write summary to `docs/superpowers/phase-1-gate-results/g2-dsl-backward-compat-sample.json` (already done by Step 6.2 script). If Step 6.4 ran, append a `compile_spot_check` section with per-spot-checked-candidate results.

G2 PASS gate at this point even if compile spot-check surfaces failures (per spec §4.1 lock). Compile failures are flagged in Task 9 ratify packet as Phase 3 fire-time concerns.

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

- [ ] **Step 7.2b: Verify symlinks point under repo root (PFR R1 LOW F5 fix v2)**

PFR R1 LOW F5 fix v2: `test -e` passes for symlinks targeting any reachable path, including OFF-REPO paths (e.g., a contaminated rsync could point to a different repo's batch files). Add target-confinement check:

```bash
python3 -c "
import os
from pathlib import Path
REPO_ROOT = Path('/Users/yutianyang/Documents/GitHub/btc-alpha-pipeline').resolve()
combined = REPO_ROOT / 'raw_payloads' / 'batch_phase2c_15_main_fire_combined'
off_repo = []
absolute_text = 0
for link in combined.glob('**/*'):
    if not link.is_symlink():
        continue
    raw_target = os.readlink(link)
    if Path(raw_target).is_absolute():
        absolute_text += 1
    resolved = link.resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        off_repo.append((str(link), str(resolved)))
print(f'total absolute-text symlinks: {absolute_text}')
print(f'off-repo resolved symlinks: {len(off_repo)}')
for link, target in off_repo[:5]:
    print(f'  {link} -> {target}')
"
```

Expected: `total absolute-text symlinks: 0` AND `off-repo resolved symlinks: 0`. Any off-repo target → STOP and surface to Charlie for cold-storage re-rsync adjudication (the off-repo path may be a legitimate cold-storage mount or contamination; Charlie register required).

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

ALL gates PASS → Phase 1 ratify gate met. Phase 2 producer-TDD sub-plan drafting is a SEPARATE register-event (#N+2) per anti-pre-emption discipline; do NOT bundle into #N+1.

ANY gate FAIL → adjudication required per spec §4.1 per-gate failure paths.

## Next register-event (#N+1) — Phase 1 ratify ONLY

PFR R1 F3 fix v2: register-event #N+1 is Phase 1 ratify acknowledgment ONLY. The Phase 2 drafting authorization is a SEPARATE register-event #N+2 (described in §"DEFER items" below). Do NOT auto-bundle.

- Phase 1 ratify acknowledgment (and per-gate adjudication if any FAIL)
- Push decision for Phase 1 evidence artifacts

Phase 2 sub-plan drafting authorization is NOT a sub-option of #N+1; it requires its own register-event #N+2 (see §"DEFER items" below).
```

- [ ] **Step 9.2: Commit Phase 1 evidence**

```bash
git add docs/superpowers/phase-1-gate-results/
git commit -m "evidence(b-c-narrow/phase-1): G1+G2+G3+G3.5 gate results (Phase 1 ratify packet)

Per Plan v3-Phase1 Tasks 5-9 + spec §4.1 BLOCKING pre-impl gates.

Gates: G1 engine-diff audit (3 commits classified per 4-category framework),
G2 DSL backward-compat (N=39 cohort_a universe; PFR R1 L4 fix v2 — specific count
locked, no placeholder), G3 raw_payloads inventory (998 symlinks; PFR R1 F5 fix v2
adds target-confinement check), G3.5 engine extension smoke (pre-satisfied by Phase 0 SEAL).

Verdict: <ALL PASS / details>. Phase 1 ratify gate met; awaiting Charlie
register-event #N+1 for Phase 1 ratify acknowledgment ONLY. Phase 2 sub-plan
drafting is a SEPARATE register-event #N+2 per anti-pre-emption discipline."
```

Do NOT push (orchestrator handles).

- [ ] **Step 9.3: Charlie register-event #N+1 (Phase 1 ratify ONLY)**

**STOP HERE.** Surface to Charlie:
- 4 gate verdicts (PASS/FAIL per gate)
- Phase 1 ratify packet content
- Evidence artifact paths
- Push decision option for evidence commit

**Do NOT surface Phase 2 drafting authorization as a sub-option of #N+1.** Per PFR R1 F3 fix v2 + anti-pre-emption discipline, Phase 2 drafting requires its own register-event #N+2 — fire that as a SEPARATE Charlie message after #N+1 is resolved.

---

## DEFER items (Phase 1 scope only)

**Phase-1-internal:** NONE. All 4 gates (G1/G2/G3/G3.5) executed in this sub-plan.

**Citation-cleanup eligible-for-separate-register (PFR R1 LOW F7 v2):** Codex R1 surfaced a stale citation in the Phase 0 SEALED test file `tests/test_t1_1_artifact_writer.py`:
- Test comment at lines 1952 + 1970 cites UTC localization at `backtest/engine.py:514-518` — current actual is `backtest/engine.py:546-564` (with `tz_localize("UTC")` at `:559`).
- Fix is comment-only (3-line change in test docstring), but it modifies a Phase 0 SEALED artifact.
- Per anti-pre-emption discipline, this fix is NOT in Phase 1 scope. Eligible for a separate Charlie register-event (e.g., "PHASE-0-CITATION-CLEANUP" or folded into a future SEAL bundle as polish). Not blocking for Phase 1 ratify.

**Phase 2+ blockers DEFERRED** to respective sub-plans per spec §5 enumeration:
- **Phase 2** (T9-T11 producer TDD): R9 architectural call-order flaw fix, `_finalize_batch_registry` create_table addition, `_parse_args` → `_build_argparser` rename, `_CSV_FIELDS` extension, archive idempotency guard, T1.4 baseline maintenance update. Drafting requires Charlie register-event #N+2 after Phase 1 ratify.
- **Phase 3** (T12-T14b fire): 39-candidate cohort_a re-run with `parquet_data_sha256` populated + per-bar artifacts + γ3/γ4 moments + V4 reproducibility gate (ε=1e-6). Drafting requires Charlie register-event #N+3 after Phase 2 SEAL.
- **Phase 4** (T15-T16 SEAL): B-C-narrow data-recovery cycle SEAL artifact + Phase Marker advance (arc-level closeout). Drafting requires Charlie register-event #N+4 after Phase 3 SEAL.

Each sub-plan requires separate Charlie register-event for drafting authorization per anti-pre-emption discipline.

---

## Execution Handoff

Plan v3-Phase1 v3 saved to `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-1-pre-impl-gates-plan.md` (PFR R2 LOW-5 fix v3 — version label updated from v1 stale text).

After Plan v3-Phase1 B2 2-leg PFR returns APPROVE (or APPROVE-WITH-FINDINGS at LOW-only floor) → use **superpowers:subagent-driven-development** per Charlie register PV3-SPLIT-BY-PHASE: dispatch fresh subagent per task with two-stage review OR orchestrator-manual execution per Charlie register-event-by-register-event.

After Phase 1 SEALED (Task 9 ratify) → request Charlie register-event for Plan v3-Phase2 sub-plan drafting authorization (separate fire — anti-pre-emption discipline preserved).
