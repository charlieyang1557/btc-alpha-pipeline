# G1 — Engine-diff audit (B-C-narrow Phase 1)

**Verified at:** 2026-05-27T16:12:06Z
**HEAD commit:** b8d6523 (plan v3-Phase1 v3 SEAL; code-state equivalent to f112599 — no code changes between)
**Plan reference:** `docs/superpowers/plans/2026-05-27-b-c-narrow-phase-1-pre-impl-gates-plan.md` §"Task 5"
**Spec reference:** `docs/superpowers/specs/2026-05-26-b-c-narrow-data-recovery-design.md` §4.1 G1

## Methodology

Per plan §"Task 5" Step 5.1 (PFR R1 F2 fix v2 — full-file diff, NOT `| head -200` truncation):

1. Step A — `git show --stat <commit> -- backtest/` to enumerate files touched in `backtest/`.
2. Step B — `git show <commit> -- backtest/` full-file diff (with `/tmp/g1-12dffde.diff` for offline inspection of the 2345-line 12dffde diff).
3. Step C — `rg -nC2` symbol grep over numerical-path identifiers per plan line 127 (PFR R2 LOW-3/NEW-1 fix v3 extended symbol list including `compute_all_metrics` + `compute_moments`):
   `run_backtest | run_regime_holdout | single_run | _evaluate_regime_holdout_pass | slippage | fee_model | cost_model | sharpe_ratio | max_drawdown | equity_curve | _save_trade_csv | compute_per_bar_returns | compute_all_metrics | compute_moments`
4. Step D — signature regex `^\s*def (run_backtest|run_regime_holdout|single_run|_evaluate_regime_holdout_pass)` to detect signature changes.

## 4-category framework (per plan line 101 PFR R1 F4 fix v2)

| Category | Definition | Triggers V4 ε adjudication? |
|---|---|---|
| **NUMERICAL-PATH** | Modifies `single_run` / `run_backtest` / `run_regime_holdout` / `_evaluate_regime_holdout_pass` / slippage / fees / Sharpe denominator / NaN handling / equity_curve computation in a way that changes outputs for the legacy call pattern | YES |
| **REGISTRY/LINEAGE-ONLY** | Modifies `_write_to_registry` / artifact write paths / lineage-context plumbing / experiment registry schema, WITHOUT changing the numerical inputs/outputs of the backtest engine | NO |
| **API/OPTIONAL-ADDITIVE** | Adds new optional kwargs with backward-compat defaults / new helper functions / new module-level constants; legacy callers see no behavior change | NO |
| **DOC/TEST-ONLY** | Doc files, test files, comments, doc-string changes; no production engine path touched | NO |

## Spec-original-range commits (`d0b8101..506285b -- backtest/`)

| Commit | Subject | Files touched in backtest/ (count) | Symbol grep hits (Step C summary) | Classification | Rationale (with cited line-range evidence) |
|---|---|---|---|---|---|
| `ec647dc` | feat(b-c-extended/t1.6): fire T1.6 documentation + consumer enumeration SEAL | 3 files (`artifact_schema.py` +39/-17; `engine.py` +1/-1; `wf_lineage.py` +21/-3) — only `backtest/engine.py` matters for symbol grep | 1 hit: comment-only edit at `backtest/engine.py:1141` — `# FIX-T1.1-SYS5-REVALIDATE: revalidate ALL 14 dataclass fields (13 Contract 2.0.5 + T_obs)` (prior version `revalidate ALL 14 Contract 2.0.5 fields`). Signature regex (Step D): NO hits — no function signature changed. | **DOC/TEST-ONLY** | The single `engine.py` line is `+/-` of a comment (both pre and post start with `#`). Diff verified at full-file scope: `1 insertion(+), 1 deletion(-)` total, with the changed line being a doc-comment string only. `artifact_schema.py` and `wf_lineage.py` changes are documentation/comment polish per the T1.6 SEAL "M1 (a)-(d) + γ Hybrid (e)-(g)" deliverables (per commit message). No code path numerical behavior changed. |
| `12dffde` | feat(b-c-extended/t1.1): fire T1.1 artifact writer SEAL — revalidate_for_write() centralized 14-field tamper closure | 4 files (`artifact_schema.py` +1069/0 NEW; `engine.py` +845/-19; `experiment_registry.py` +31/0; `wf_lineage.py` +109/0 NEW) | MANY hits all within additive zones: (a) `run_backtest` signature gains NEW kwarg `lineage_context: "Any | None" = None` (default None preserves backward compat); (b) `run_regime_holdout` signature gains NEW kwargs (per plan §"Pre-Phase-1 Charlie register-event boundary" line 41 `bedc9b4` Phase 0 commit; in this commit `12dffde` only the `run_backtest` lineage_context kwarg was added pre-Phase 0); (c) NEW top-level helpers `compute_per_bar_returns()`, `compute_moments()`, `write_per_bar_artifact()` at engine.py post-line-1170 (new module-level functions, no callers within legacy paths); (d) FIX-H2 within `run_backtest` body: `_effective_exec_config_path = execution_config_path` (bit-exact init); override `if _effective_exec_config_path is None and lineage_context is not None` — gated by lc-not-None; (e) FIX-H2 within `run_regime_holdout` body: `_rh_effective_exec_path = execution_config_path` (bit-exact init); override `if _rh_effective_exec_path is None and lineage_context is not None`; (f) `_write_to_registry` body extensions for 14-field tamper closure + cost_anchor_id population. Signature regex (Step D): zero DELETIONS of any of the 4 core function signatures — all changes are additive kwargs with `= None` defaults. Zero DELETED lines containing core numerical symbols (`sharpe_ratio | max_drawdown | equity_curve | slippage | fee_model`). | **API/OPTIONAL-ADDITIVE** for the LC-b path; **BIT-EXACT-PRESERVING** for the legacy path | Legacy V4 reproducibility surface (the original `phase4_forward_2026_15bps_v1` fire) called `run_backtest(execution_config_path=<phase4_yaml>, ...)` with scalar `execution_config_path` set and NO `lineage_context` kwarg (the kwarg did not exist at fire time). At HEAD `b8d6523`/`f112599`, the same call pattern produces identical behavior because: (1) `_effective_exec_config_path = execution_config_path` (bit-exact initial assignment at engine.py post-12dffde lines 712+); (2) the LC-derivation branch is gated by `lineage_context is not None` which is False for legacy callers; (3) the inner `run_backtest()` call inside `run_regime_holdout` passes `_rh_effective_exec_path` which equals the scalar `execution_config_path` for legacy callers. The NEW helpers (`compute_per_bar_returns` / `compute_moments` / `write_per_bar_artifact`) have ZERO callers in the legacy V4 fire path — they are invoked only via the new LC-b artifact-writer path activated when both `lineage_context is not None` and `artifact_dir is not None`. `_write_to_registry` extensions for `cost_anchor_id` population are REGISTRY/LINEAGE-ONLY (forensic metadata; not consumed in any numerical compute path). |
| `44840a3` | docs(phase5): fire R3.1d cost-grid re-anchor V_SEAL — conservative anchor 15 bps/side | 1 file (`experiment_registry.py` +9/0) | Zero symbol grep hits within `backtest/` (the only changes are `cost_anchor_id TEXT` column addition to `CREATE_TABLE_SQL` + appending one entry to `MIGRATION_COLUMNS`). Signature regex (Step D): zero hits. | **REGISTRY/LINEAGE-ONLY** | SQLite schema migration adds `cost_anchor_id TEXT` column for forensic discrimination of Phase B/Tier 5/6 runs. Column is metadata-only — not consumed by any numerical compute function. `MIGRATION_COLUMNS` append is idempotent ALTER via existing migration loop (per commit message). Zero impact on legacy V4 numerical surface. |

### Phase 0 commits (506285b..f112599) — PRE-CLASSIFIED by SEAL evidence

Per plan §"Task 5" PFR R1 H1 fix v2: between spec-original-range upper bound `506285b` and current HEAD `f112599` (code-equivalent to `b8d6523`), 3 Phase 0 commits touched `backtest/engine.py`. Per Phase 0 SEAL evidence chain + the 13/13 GREEN test suite + the single-gate `lcb_active = artifact_dir is not None` pattern, these commits are PRE-CLASSIFIED:

| Commit | Subject | Pre-classification | Evidence |
|---|---|---|---|
| `8f64712` | T2 RegimeHoldoutResult.equity_curve field | **API/OPTIONAL-ADDITIVE** | New dataclass field + call-site update; legacy callers always receive populated equity_curve (no opt-out, but semantically the field is new metadata, not a numerical-input). |
| `bedc9b4` | T3 run_regime_holdout signature +4 LC-b kwargs | **API/OPTIONAL-ADDITIVE** | All 4 kwargs default None for backward-compat; cost_anchor_id INTENTIONALLY omitted (derived in LC __post_init__). |
| `f112599` | T4 body LC-b construction + preflight + 2 helpers | **API/OPTIONAL-ADDITIVE for LC-b path; legacy path unchanged** | Single-gate `lcb_active = artifact_dir is not None`; with `artifact_dir=None`, body is bit-exact pre-Phase-0 (run_backtest → _write_to_registry with no LC); with `artifact_dir != None`, NEW LC-b path activated (preflight + LC construction + atomic write). 13/13 PASS in TestBCNarrowPhase0EngineExtension validates both paths. |

Phase 0 SEAL evidence chain: `ebc0d26` (T1 RED tests) → `fd1b7ea` (pc9 BASELINE amend) → `8f64712` (T2) → `bedc9b4` (T3) → `f112599` (T4). Full-suite zero-regression: 2328 passed / 0 failed / 2 xfailed at HEAD `f112599`. Pre-classification authority: Phase 0 task-level SEAL register-event (Charlie register `SEAL-TASK-LEVEL` 2026-05-27).

## G1 verdict

ALL 3 spec-original-range commits classified NON-NUMERICAL-PATH:
- `ec647dc`: DOC/TEST-ONLY
- `12dffde`: API/OPTIONAL-ADDITIVE (LC-b path) + BIT-EXACT-PRESERVING (legacy path)
- `44840a3`: REGISTRY/LINEAGE-ONLY

Phase 0 commits also non-numerical (API/OPTIONAL-ADDITIVE per SEAL evidence).

**G1 = PASS** → V4 ε=1e-6 expected achievable at §4.2 post-impl gate. Proceed to Task 6.
