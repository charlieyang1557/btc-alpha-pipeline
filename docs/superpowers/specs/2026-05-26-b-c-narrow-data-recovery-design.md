# B-C-narrow data-recovery cycle — design spec

**Cycle name**: B-C-narrow data-recovery successor cycle
**Driver**: R6.1 V_SEAL §10 binding precondition
**Drafted**: 2026-05-26
**Status**: design ratified (§1-§10 + Approach D' with engine extension);post-PFR R2 amend integrating Codex 2 HIGH + 4 MEDIUM + advisor D1/N1/D2/D3 inline + post-PFR R3 advisor APPROVE-WITH-FINDINGS 4 polish fixes (NEW-D1 + NEW-D2 + NEW-D3 + NEW-D4). Spec doc pre-implementation; 4 DEFER items remain for plan v1 (see spec-bottom enumeration).
**Cycle entry register**: Charlie 2026-05-26 (N1)
**Repo HEAD evolution during spec authorship** (informational): spec drafting started against `53090a0` (docs-only `MAC_MINI_DATA_REFERENCE.md` commit); spec v1 committed at `b3057fa` (docs-only this spec); spec v2 amended at `309384c` integrating PFR R2 fixes; spec v3 amended after PFR R3 polish fixes (this state) — substantive engine state remains at `506285b` throughout (Q2=E1 unchanged).
**English-only body** per R5.1 + R5.2 + R2.3 + R6.1 + B-C-extended + R6.1 §2.2 narrow patch SEAL artifact precedent

---

## §1 — Cycle scope + driver

**Driver** (per `docs/phase5/R6_1_TIER_6_PROMOTION_CLASS_NOTE.md` §10 line 366): the `phase4_forward_2026_15bps_v1` cohort_a 39-candidate artifact at `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` was produced without per-bar return series preservation, per-candidate γ3/γ4 moment storage, or registry linkage. R6.1 V_SEAL §8 dimensions classified 4-of-7 INDETERMINATE-on-data-unavailability as a result. R6.1 V_SEAL §10 names B-C-narrow as the data-recovery successor cycle that unblocks Tier 6 evaluation application via methodology + (a1) prescription on the recovered cohort.

**Scope** (bounded per R6.1 V_SEAL §10 binding condition):

1. Run the engine on the 39 cohort_a candidates against the forward_2026 window using current HEAD engine code (engine state = `506285b`; repo HEAD = `53090a0` is a docs-only addition).
2. Preserve per-bar return series at `returns_per_bar.parquet` per candidate via T1.x-sealed writers (`write_per_bar_artifact`).
3. Compute γ3 (skew) / γ4 (raw kurtosis) / T_obs per candidate via T1.x-sealed helper (`compute_moments`); **T_obs persists in registry row + per-candidate JSON; γ3/γ4 persist in per-candidate JSON only (recomputable from parquet)** per §3.6 below.
4. Link per-candidate artifact files to registry rows via `returns_per_bar_path` / `returns_per_bar_sha256` / `T_obs` columns (sealed at experiment_registry MIGRATION_COLUMNS).
5. Write a parent `batch_summary` registry row at `run_id=phase4_forward_2026_15bps_v1_b_c_narrow` to provide cohort-level metadata projection.
6. Archive the original artifact under `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` (original `engine_commit=eb1c87f` constant + `current_git_sha=d0b8101`) before overwriting the canonical path.

**Out-of-scope** (separate successor cycles per anti-pre-emption discipline):

- Tier 6 evaluation application (DSR computation + threshold check + promotion list) is gated by this cycle SEAL; separate Charlie register-event.
- R2.1 / R2.3 / R5.1 / R5.2 INDETERMINATE-DSL-UNAVAILABLE re-verification cycles are NAMED successors; see §9.
- Engine-layer structural refactor beyond the minimum extension needed for Approach D'; see §3 for what is in-scope at the engine boundary.

**Dual resolution of R6.1 §8 INDETERMINATE dimensions** (bonus per R-AUDIT-FIRST 2026-05-26):

- R6.1 §8 dim (a) DSL availability — empirically resolved by recovery of 5 cohort_a source batches + combined synthetic dir from cold-storage (per `docs/operations/MAC_MINI_DATA_REFERENCE.md`); verified by `_load_dsl_from_response('phase2c_15_main_fire_combined', 873)` returning a valid `StrategyDSL`.
- R6.1 §8 dim (b) per-bar return + γ3/γ4 — resolved by THIS cycle through Approach D' producer wiring + engine extension.

**Path α invariant preserved**: data recovery and producer-wiring at this cycle; no per-candidate statistical computation (DSR / threshold) at this layer. Computation is the separate Tier 6 application successor.

---

## §2 — Locked scope decisions (Q1-Q6 with verification corrections)

| Q | Decision | Verified detail |
|---|---|---|
| Q1 | **C2** | 39 cohort_a candidates from `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv` (40 lines including header); matches original artifact superset of R6.1 V_SEAL 18-cohort |
| Q2 | **E1** | **Engine code state at commit `506285b`** (R6.1 §2.2 narrow patch SEAL). **Repo HEAD = `53090a0`** (`docs(operations): add cold-storage data registry`) is docs-only; `506285b..HEAD` contains zero `backtest/` / `scripts/` / `tests/` / `config/` changes. T1.1-T1.6 sealed per-bar preservation infrastructure + Contract 2.0.5 schema + LineageContext invariant + experiment_registry MIGRATION_COLUMNS are at `506285b` |
| Q3 | **A3** | Archive original `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` → `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` (parent `archive/` dir created if absent; archive name uses `d0b8101` = original `current_git_sha`, distinct from `engine_commit=eb1c87f` constant). **Output path mechanism**: producer at scripts:908 builds `run_dir = output_root / run_id`;with `--run-id phase4_forward_2026_15bps_v1_b_c_narrow` producer writes to **sibling dir** `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/`. After V4 PASS at T14, **T14b explicit relocation step** moves sibling → canonical `phase4_forward_2026_15bps_v1/`. Registry `run_id` stays `phase4_forward_2026_15bps_v1_b_c_narrow` (distinct from original's `phase4_forward_2026_15bps_v1` to avoid PK collision). Archive idempotency: refuse if target archive dir already exists (per §3.7 ADOPT) |
| Q4 | **R1** | 39 child rows + 1 batch_summary parent row at `run_id=phase4_forward_2026_15bps_v1_b_c_narrow`. **Child run_id scheme intent**: deterministic `{parent_run_id}_{hypothesis_hash}` (e.g. `phase4_forward_2026_15bps_v1_b_c_narrow_8a2a8f73f71a835e`) to avoid `insert_run` primary-key collisions on re-run. **Plan-v1 implementation NOTE**: current `run_backtest` mints internal UUID for `result.run_id`; `run_regime_holdout` uses `result.run_id` for registry write. Deterministic child run_id requires Phase 0 to add an explicit deterministic-run-id input mechanism to `run_regime_holdout` (NEW kwarg, e.g., `run_id_override: str | None = None`); plan v1 specifies. Parent row idempotency guard: refuse if parent row already exists (default REFUSE) |
| Q5 | **V4** | Strict ε=1e-6 abs-diff numerical match on `sharpe_ratio` / `max_drawdown` / `total_return` + exact match on `total_trades` (int) / `holdout_passed` (bool) / 4 `gate_pass_per_criterion` subfields. PRE-FIRE engine-diff audit: 3 commits in `git log d0b8101..506285b -- backtest/` (`ec647dc` + `12dffde` + `44840a3`); classify each as semantics-affecting or additive-only. Cost-anchor for this cycle = `phase4_forward_15bps_v1` (per CLAUDE.md HARD CONSTRAINT lines 268-269 — Tier 5/6 promotion under separate successor uses `spot_realistic_15bps_v1` anchor) |
| Q6 | **D1** | Full NOTE doc at `docs/phase5/B_C_NARROW_DATA_RECOVERY_NOTE.md` (~400-600 lines) at SEAL time |

**Engine-commit identity disambiguation** (per Codex Verification #5 + advisor F2.1):

| Identifier | Value | Meaning |
|---|---|---|
| `engine_commit` (artifact field) | `eb1c87f` (constant from `backtest/wf_lineage.py:71` `CORRECTED_WF_ENGINE_COMMIT`) | Identity of the corrected-WF engine semantics anchor; does NOT change between artifact fires unless the corrected-WF gating constant is bumped |
| `current_git_sha` (artifact field; original) | `d0b8101` | Fire-time HEAD when original artifact was produced |
| `current_git_sha` (artifact field; new B-C-narrow) | `506285b` | Engine code state for this cycle (per Q2 above; repo HEAD `53090a0` adds no engine changes) |
| V4 reproducibility check anchor | `engine_commit=eb1c87f` constant unchanged across original + new artifact; `current_git_sha` advances per Q2 | Numerical reproducibility is governed by engine semantics (`eb1c87f` anchor unchanged) + Python/numpy/scipy patch versions (acknowledged ε bound) |

**Cost-anchor lock**:

- B-C-narrow uses **`phase4_forward_15bps_v1`** cost anchor via `config/execution_phase4_15bps.yaml` (matches the original artifact for V4 reproducibility).
- Formal Tier 5/6 promotion would use `spot_realistic_15bps_v1` via `config/execution_phaseb_spot_15bps.yaml` (per HARD CONSTRAINT line 268-269) — but Tier 6 application is a SEPARATE successor cycle (§9); B-C-narrow is methodology-anchor-independent data recovery.
- Spec doc + NOTE doc must NOT conflate the two anchors.

---

## §3 — Architecture: Approach D' (producer edit + minimum engine extension)

**Approach D'** revises Charlie's initial Approach D ratify per cross-model B2 dispatch CONVERGENT finding that:

1. `RegimeHoldoutResult` dataclass at `backtest/engine.py:2044-2063` lacks an `equity_curve` field. The producer cannot access the per-bar series via the dataclass that `run_regime_holdout` returns.
2. `run_regime_holdout` calls `_write_to_registry` at `backtest/engine.py:2476-2500` **before** returning. Per-candidate artifact metadata (`returns_per_bar_path` / `returns_per_bar_sha256` / `T_obs`) cannot be backfilled into the registry row after return.

Both findings are BLOCKING for the literal "edit producer only" reading of Approach D. The minimum scope expansion to make Approach D' implementable is:

### §3.1 Phase 0 — Engine extension (minimum, bounded)

**3.1.1 Extend `RegimeHoldoutResult` dataclass** at `backtest/engine.py:2044-2063`:

Add field: `equity_curve: pd.Series` populated from the underlying `BacktestResult.equity_curve` (which already exists at `backtest/engine.py:642`). Preserve all existing fields verbatim.

**3.1.2 Modify `run_regime_holdout` internal sequence** at `backtest/engine.py` around lines 2476-2500:

Re-order so that per-bar artifact write + γ3/γ4 computation occur **before** `_write_to_registry`:

1. Run backtest → produce `BacktestResult` (existing).
2. Compute per-bar returns via `compute_per_bar_returns(equity_curve)` (existing helper at engine.py:331).
3. Call `write_per_bar_artifact(equity_curve, candidate_dir, run_id)` (existing helper at engine.py:443) → returns a **dict** with keys `returns_per_bar_path` / `returns_per_bar_sha256` / `T_obs` / `gamma3` / `gamma4` (per engine.py:469-475 docstring; dict not tuple).
4. Call `_write_to_registry` (existing at engine.py:839) with `returns_per_bar_path` / `returns_per_bar_sha256` / `T_obs` populated.
5. Construct `RegimeHoldoutResult` including `equity_curve` field; return.

**3.1.3 Scope guard**: NO new engine CLI mode (the rejected Approach B). NO new public API. NO refactor of unrelated engine code. Two files touched: `backtest/engine.py` (RegimeHoldoutResult dataclass extension + `run_regime_holdout` internal sequencing). Tests gated per §6.

**3.1.4 NOTE — _write_to_registry + run_regime_holdout call-site consistency**: `engine.py` has **4 call sites** of `_write_to_registry` at lines 771 (`run_backtest`), 1841 (walk-forward window), 1896 (walk-forward summary), 2476 (`run_regime_holdout`). Phase 0 (per T2b + T2c) adds `run_id_override: str | None = None` + `artifact_dir: Path | None = None` kwargs to `run_regime_holdout` (default `None` preserves backward compat for existing callers — only B-C-narrow producer + new tests pass these kwargs). The `_write_to_registry` signature stays unchanged at the 4 call sites; only the ORDERING of artifact-write-vs-registry-write changes within `run_regime_holdout` itself. Pre-T4 zero-regression test verifies all 4 call sites' existing tests pass unchanged + new behavior tests pass at the modified `run_regime_holdout` site.

### §3.2 Phase 1 — Producer edits at `scripts/run_phase2c_evaluation_gate.py`

**3.2.1 `_evaluate_one_candidate` at line 480**:

- Thread `LineageContext` (instead of scalar `execution_config_path: Path | None`) — **but see §3.4 plan-v1 construction-pattern NOTE** for chicken-and-egg resolution: today's engine does NOT internally construct LineageContext (verified via grep — only error message reference at engine.py:1003). Plan v1 specifies whether engine-internal or producer-side construction.
- Capture `equity_curve` from the extended `RegimeHoldoutResult` (Phase 0 deliverable) if producer needs it for downstream consumers (most logic is in engine already).
- Compute γ3/γ4/T_obs via `compute_moments(compute_per_bar_returns(equity_curve))` if producer needs them at JSON-merge layer (engine has already done this for artifact + registry; producer-side compute is redundant unless schema needs both layers — see §3.3). **Note**: `compute_moments` takes a **returns array** (not equity_curve) per engine.py:365 signature; must compose with `compute_per_bar_returns` first.
- Merge γ3/γ4/T_obs into the `summary` dict; per-candidate JSON is written **inline at `scripts/run_phase2c_evaluation_gate.py:550-556`** (NOT by `_write_aggregate_summary`); merge must happen before that inline write.

**3.2.2 Per-candidate JSON + EDIT `_write_aggregate_summary`** at producer:

- **Per-candidate `holdout_summary.json` write**: written inline at `scripts/run_phase2c_evaluation_gate.py:550-556` (NOT by `_write_aggregate_summary`). EDIT the inline write to include γ3/γ4/T_obs/returns_per_bar_path/returns_per_bar_sha256 fields in the per-candidate summary dict.
- **Top-level cohort `holdout_summary.json` write**: handled by EXISTING `_write_aggregate_summary` function at `scripts/run_phase2c_evaluation_gate.py:706` (call site at line 1053). EDIT to stamp cohort-level fields (`forward_window_metadata`, `audit_only_*`, `by_theme`, `lineage_check`, `engine_commit`, `current_git_sha`).

**3.2.3 NEW `_finalize_batch_registry()` function in producer**:

Location: `scripts/run_phase2c_evaluation_gate.py` (new top-level function near existing aggregate writers). Responsibilities:

- After all 39 candidates evaluated, write the parent `batch_summary` registry row at `run_id=phase4_forward_2026_15bps_v1_b_c_narrow` with cohort-level metadata.
- Cohort-level fields at parent row: `git_commit` (=`506285b`), `current_git_sha` (=`506285b`), `engine_commit` (=`eb1c87f`), `execution_config_path` + `execution_config_sha256`, `parquet_data_sha256`, `regime_key`, `cost_anchor_id` (=`phase4_forward_15bps_v1`), `batch_id` (=`phase4_forward_2026_15bps_v1_b_c_narrow`), `created_at_utc`, `effective_start` (= forward_window_start_utc), `initial_capital`, `fee_model`, `strategy_name="cohort_summary"`, `strategy_source="b_c_narrow_recovery"`.
- Per-candidate fields at parent row: NULL by design (`sharpe_ratio` / `max_drawdown` / `total_return` / `total_trades` / `hypothesis_hash` / `returns_per_bar_path` / `returns_per_bar_sha256` / `T_obs` etc.).
- Registry writes for the 39 child rows + 1 parent row use sequential `insert_run()` calls (single-transaction wrap NOT feasible per §7 R9 — `insert_run()` commits internally at experiment_registry.py:315). On partial-write failure: compensating-cleanup discipline applies — refuse-if-any-child-row-exists-from-prior-attempt OR `DELETE WHERE parent_run_id = '...'` + re-fire from clean state. Plan v1 locks the specific compensating-cleanup mechanism.

**3.2.4 NEW archive step**:

Location: `scripts/run_phase2c_evaluation_gate.py` (new function before `_evaluate_one_candidate` loop). Responsibilities:

- Check that `data/phase2c_evaluation_gate/archive/` exists (create if absent).
- Check that target archive dir `archive/phase4_forward_2026_15bps_v1_d0b8101/` does NOT exist. If present → refuse with explicit error (rerun-clean-into-empty-dir discipline per §7 R6).
- Move (`shutil.move`) original `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` → archive target.
- Verify post-move: source dir empty/absent, archive target populated with original artifact tree.

**3.2.5 `_CSV_FIELDS` extension** at producer line 581-595:

Locked-now decision: `holdout_results.csv` (39 rows + 1 header) is the per-candidate aggregate CSV. `_CSV_FIELDS` extensions for B-C-narrow:

- ADD `gamma3` (float | None) — γ3 from per-candidate summary
- ADD `gamma4` (float | None) — γ4 from per-candidate summary
- ADD `T_obs` (int) — T_obs from per-candidate summary
- ADD `returns_per_bar_path` (str) — relative path to per-candidate parquet
- ADD `returns_per_bar_sha256` (str) — SHA256 of parquet

(`engine_commit` / `current_git_sha` etc. remain cohort-level and live in top-level `holdout_summary.json`, not in `holdout_results.csv` to avoid 39× duplication.)

### §3.3 Schema-domain routing decision (REFRAMED per PFR H1)

Existing `_evaluate_one_candidate` at `scripts/run_phase2c_evaluation_gate.py:557-562` validates per-candidate `holdout_summary.json` through `check_evaluation_semantics_or_raise` (evaluation-domain validator; def at `wf_lineage.py:352`). B-C-extended Contract 2.0.5 schema uses `check_b_c_extended_semantics_or_raise` (artifact_schema.py:667) which validates a **dict/header** (e.g., LineageContext-projected dict at registry-write boundary), NOT a parquet file directly.

**Important factual correction (verified 2026-05-26 via grep)**:

- `write_per_bar_artifact` writes parquet with **only 3 data columns** (`timestamp`, `portfolio_value`, `return`) per engine.py:498-510. **No `artifact_schema_version` field embedded in parquet.** Integrity via SHA256 + file existence only.
- `check_b_c_extended_semantics_or_raise(summary: dict, ...)` per artifact_schema.py:667 takes a **dict input** named `summary` and validates required string fields + `T_obs > 0` + `artifact_schema_version` ∈ ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS. It validates **DICTS** not parquet files.

**LOCKED DECISION**:

- **Per-candidate `holdout_summary.json`**: evaluation domain (`artifact_schema_version: phase2c_7_1`) with **additive fields** for γ3/γ4/T_obs/returns_per_bar_path/returns_per_bar_sha256. Validated by `check_evaluation_semantics_or_raise` (def at wf_lineage.py:352). No `b_c_extended_v1` schema-version stamp here.
- **LineageContext object** (in-memory dataclass at artifact_schema.py:206-218): b_c_extended domain (`b_c_extended_v1`). **Stamped into registry row via T1.1 SYS5 `revalidate_for_write()` invariant at engine.py:1149** (Mode-A-verified;NOT `check_b_c_extended_semantics_or_raise`). `check_b_c_extended_semantics_or_raise(summary: dict, ...)` at artifact_schema.py:667 validates **dict-input** at consumer-side schema-version boundary (where a dict matching the b_c_extended_v1 schema is read back for verification);it is NOT called at registry-write boundary in the current write flow.
- **`returns_per_bar.parquet`**: **data-only file** (3 columns: timestamp/portfolio_value/return); **no schema_version header embedded**. Integrity via SHA256 (stored in JSON + registry) + file existence. NOT validated by either domain validator (not a dict input).
- **Validator routing**: `check_evaluation_semantics_or_raise` for per-candidate JSON (unchanged from current); `check_b_c_extended_semantics_or_raise` for LineageContext-dict at registry-write boundary (per `revalidate_for_write` invariant). **No cross-domain validation.** Schema domains apply to the **validation function call layer**, not to physical file format.
- Plan-v1 NOTE: if future consumers require a sidecar JSON header alongside parquet (b_c_extended_v1 stamped), that is a separate addition outside current Approach D' scope.

### §3.4 LineageContext construction sequence (chicken-and-egg — DEFERRED to plan v1 NOTE)

Per `backtest/artifact_schema.py:206-218` LineageContext has 14 strict fields requiring valid `run_id` + positive `T_obs` at construction. **Chicken-and-egg gap (verified 2026-05-26 via grep)**: today's engine does **NOT internally construct LineageContext** (only error-message reference at engine.py:1003;all current constructions are in `tests/`). Producer cannot pre-construct LineageContext before `run_regime_holdout` because T_obs is engine-computed AFTER backtest runs.

**LOCKED at design layer**: Phase 0 must add LineageContext construction logic. **Specific pattern DEFERRED to plan v1 (highest-priority architecture decision for Phase 0)** — 3 candidate patterns to adjudicate in plan v1:

- (a) **Engine-internal construction**: engine constructs LC after backtest + write_per_bar_artifact, before `_write_to_registry`. NEW pattern not in current call sites; cleanest for atomicity.
- (b) **Engine-internal with producer-passed scalars**: engine constructs LC internally using engine-computed T_obs + producer-passed metadata scalars (run_id, parent_run_id, source_batch_id, regime_key, execution_config_path); producer does NOT pre-construct LC.
- (c) **Two-phase call**: producer calls engine without LC, captures returned T_obs from extended RegimeHoldoutResult, constructs LC, then re-issues registry write — but breaks atomicity (R9 implications).

Plan v1 selects + locks; intermediate (a) or (b) preferred for atomicity.

Source of each field (mapping table — to be elaborated in plan v1):

| LineageContext field | Source |
|---|---|
| `run_id` | Engine input (= candidate-level deterministic `{parent_run_id}_{hypothesis_hash}`) |
| `parent_run_id` | Engine input (= `phase4_forward_2026_15bps_v1_b_c_narrow`) |
| `batch_id` | Producer config (= `phase2c_15_main_fire_combined` source-batch-id passed in, plus parent_run_id for grouping) |
| `T_obs` | Computed after `compute_per_bar_returns(equity_curve)` |
| `engine_commit` | `CORRECTED_WF_ENGINE_COMMIT` constant (= `eb1c87f`) |
| `current_git_sha` | Engine reads `git rev-parse HEAD` (= `506285b`) |
| ... (others) | per artifact_schema.py:206-218 detailed list |

### §3.5 Approach D' rejection of alternatives (re-confirm)

- **Approach A (NEW file in backtest/)**: rejected per advisor SI-1 + Codex Section 1 (duplicate parallel path)
- **Approach B (engine `--mode=cohort_holdout_recovery`)**: rejected per advisor + Codex (overweight; permanent engine CLI for hypothetical future cycles; violates anti-pre-emption)
- **Approach C (shell loop)**: rejected per advisor + Codex (atomic registry insert lost; TDD difficulty)

### §3.6 γ3/γ4 persistence policy

**LOCKED DECISION**:

- γ3/γ4 **persist in per-candidate `holdout_summary.json` only** (NOT in registry rows); they are recomputable from the per-bar parquet via G5 round-trip gate. Rationale: JSON is the source-of-truth artifact for per-candidate moments.
- T_obs **persists in BOTH per-candidate JSON AND registry rows** (per existing MIGRATION_COLUMNS at experiment_registry.py:155-157 which includes `T_obs INTEGER`). Registry projection enables cohort-level SQL queries on T_obs without re-reading 39 JSON files.
- For low-T_obs candidates (T_obs < 2;engine.py:414-415) AND zero-variance candidates (engine.py:424-425, FIX-T1.1-M2 where `np.var(finite_arr) == 0.0`): γ3 / γ4 = `None` per `compute_moments` existing semantics. Cohort-level aggregation (e.g., `mean(γ3)`) must SKIP None values from BOTH cases; no propagate-as-NaN.
- Plan v1 specifies the exact NaN-handling cohort-aggregation contract.

### §3.7 Atomic write semantics for `returns_per_bar.parquet`

- T1.1 sealed `write_per_bar_artifact` at engine.py:443 already uses write-to-temp + rename (per CONTRACT 2.0.5 line 584 `temp_filename = f"returns_per_bar.parquet.tmp.{uuid.uuid4().hex[:8]}"` — verified).
- No new atomic-write logic needed at Approach D' scope; existing T1.x infrastructure guarantees atomicity.

### §3.8 Out-of-scope at engine boundary

- Engine internal-write disable / no-registry mode: NOT in scope (would expand engine surface beyond Phase 0 minimum).
- Refactor of `_write_to_registry` call sites: NOT in scope (sealed T1.x invariant `_B1_LOCKED_4TUPLE` semantics preserved).
- Walk-forward path changes: NOT in scope.

---

## §4 — Verification chain

### §4.1 Pre-implementation BLOCKING gates

| Gate | Check | Pass criteria |
|---|---|---|
| **G1 — Engine-diff audit** | `git log --oneline d0b8101..506285b -- backtest/` returns **3 commits** (`ec647dc` + `12dffde` + `44840a3`); classify each as semantics-affecting vs additive-only; verify each does not change `single_run` / `run_regime_holdout` numerical path | All 3 commits classified additive-only → V4 ε=1e-6 expected achievable. Any semantics-affecting → Charlie register adjudication (widen ε with rationale; reject Q2; or accept drift) |
| **G2 — StrategyDSL backward-compat** | Sample N ≥ 39 attempt responses (covering all 5 sub-batches) from recovered raw_payloads;`StrategyDSL.model_validate(json.loads(...))` succeeds at current `506285b` Pydantic schema | 100% sample pass. Any failure → Charlie register adjudication (identify schema-drift commit; fix or rollback) |
| **G3 — Raw_payloads inventory** | 5 cohort_a sub-batch dirs + combined synthetic dir at `raw_payloads/`; combined dir has **993 attempt symlinks + 5 source_stage2d_summary_*.json symlinks (998 total)**; all symlinks resolve to existing files (`find raw_payloads/batch_phase2c_15_main_fire_combined -type l \| wc -l = 998`) | Inventory matches; all symlinks resolve. Failure → re-run rsync from cold-storage |
| **G3.5 — RegimeHoldoutResult.equity_curve exposure** | After Phase 0 engine extension lands, `RegimeHoldoutResult` dataclass includes `equity_curve: pd.Series` field; smoke test passes | Engine extension complete + tested in isolation before producer edits |

### §4.2 Post-implementation V4 reproducibility gate (BLOCKING for SEAL)

For each of 39 candidates, compare new vs archived original:

- `sharpe_ratio` / `max_drawdown` / `total_return`: `abs(new - old) < 1e-6`
- `total_trades`: `new == old` (exact integer match)
- `holdout_passed`: `new == old` (exact bool match)
- `gate_pass_per_criterion` 4 subfields: each exact match

**V4 drift stop-condition**:

- Any 1 candidate × any 1 metric breach → SEAL **BLOCKED** until Charlie register adjudication.
- Adjudication paths: (a) classify drift source as environmental (numpy/scipy patch versions) → widen ε with documented rationale + evidence (e.g., `pip freeze` snapshot diff between original + new run + scipy/numpy release notes) → proceed; (b) classify drift as semantic engine change → escalate to Q2 re-litigation; (c) accept drift + **update §8 INDETERMINATE re-classification in THIS cycle's NOTE doc §8 only** (R6.1 §8 sealed per Architecture B; no in-place edit of R6.1 SEAL).
- NO automatic widening of ε without Charlie register.

### §4.3 New-content correctness gates

| Gate | Check | Pass criteria |
|---|---|---|
| **G4 — Per-bar parquet integrity** | (a) row count = T_obs from summary; (b) SHA256 of file = `returns_per_bar_sha256` in summary + registry; (c) data is not all-NaN (degenerate write); (d) **`timestamp` column UTC-aware** (parquet writes `timestamp` as a column not as the index per engine.py:498-510) | All 4 sub-checks pass per candidate |
| **G5 — γ3/γ4 round-trip** | Load parquet → `compute_moments(returns_array)` → compare to stored summary values. Tolerance: bit-exact for T_obs match; abs diff < 1e-10 for γ3/γ4 (float64 round-trip determinism) | All 39 candidates pass round-trip |
| **G6 — Registry parent-child integrity** | 1 batch_summary parent row at `phase4_forward_2026_15bps_v1_b_c_narrow` + 39 child rows (each `run_type=regime_holdout` per existing engine-internal write semantics); each child's `parent_run_id` = parent; cohort-level metadata at parent (NULL at children); per-candidate metadata at children | Schema query passes: `SELECT COUNT(*) FROM runs WHERE parent_run_id='phase4_forward_2026_15bps_v1_b_c_narrow' AND run_type='regime_holdout' = 39`;parent row exists with `run_type='batch_summary'` |
| **G7 — Archive idempotency** | Pre-run: `archive/phase4_forward_2026_15bps_v1_d0b8101/` **does NOT exist** (strict refuse-if-exists per §3.2.4; no auto-handle empty dir; manual cleanup required if archive target preexists from aborted attempt). Post-run: archive contains original artifact tree; source canonical path repopulated with new B-C-narrow output | Strict refuse-if-exists semantics; rerun-clean-into-empty-dir requires manual cleanup of partial state |

---

## §5 — Implementation outline (T1-T16)

Phases interlocked with Charlie register-event boundaries; ~5-15 register events expected (5-8 minimum + 1-2 v_impl_polish iterations per Rule 2 SEAL-eve empirical + 1-2 V4 audit adjudications if drift found).

### Phase 0 — Engine extension (NEW per Approach D')

- **T1** Write FAILING tests for engine return path + schema-domain routing:
  - `test_regime_holdout_result_exposes_equity_curve()` — RED before T2
  - `test_regime_holdout_result_dataclass_fields_complete()` — verify 12-field shape (11 existing + equity_curve)
- **T2** Edit `backtest/engine.py:2044-2063` `RegimeHoldoutResult` dataclass: add `equity_curve: pd.Series` field.
- **T2b** Edit `backtest/engine.py` `run_regime_holdout` signature (around line 2287): add **deterministic-run-id input mechanism** (new kwarg `run_id_override: str | None = None`) so producer can pass `phase4_forward_2026_15bps_v1_b_c_narrow_<hash>` (per §2 Q4 + §3.4 plan-v1 NOTE). Also add `artifact_dir` kwarg threading for per-bar parquet write target (engine currently mints per-run dir;new kwarg enables producer-controlled dir for cohort wiring).
- **T2c** Plan-v1-locked LineageContext construction pattern (per §3.4 deferred decision): implement chosen pattern (a/b/c from §3.4) at `run_regime_holdout` body before `_write_to_registry`. Plan v1 specifies which pattern + lock; if Phase 0 implementation reveals pattern is infeasible → Charlie register-event for re-litigation.
- **T3** Edit `backtest/engine.py` `run_regime_holdout` (around 2476-2500): re-order so per-bar artifact write happens BEFORE `_write_to_registry`. Verify `_write_to_registry` gets populated `returns_per_bar_path` / `returns_per_bar_sha256` / `T_obs`. Use LineageContext (constructed per T2c) for stamping registry row fields atomically.
- **T4** Run T1 tests → GREEN. Run full test suite → zero regression (per CLAUDE.md HARD CONSTRAINT pc7). Update existing test stubs that construct `RegimeHoldoutResult(...)` at `tests/test_phase2c_evaluation_gate_runner.py:83` + `tests/test_t1_4_backward_compat.py:1384` to include `equity_curve=` arg. Update T1.4 baseline maintenance per impact (see §6.4).
- **Charlie register-event #N** — Phase 0 ratify before Phase 1.

### Phase 1 — Pre-implementation gates (BLOCKING)

- **T5** Run G1 engine-diff audit: classify 3 commits (`ec647dc` + `12dffde` + `44840a3`) as additive-only vs semantics-affecting.
- **T6** Run G2 StrategyDSL backward-compat sample (N ≥ 39).
- **T7** Run G3 raw_payloads inventory check (993 + 5 = 998 symlinks; all resolve).
- **T8** Run G3.5 engine extension smoke (RegimeHoldoutResult.equity_curve exposed; smoke test passes).
- **Charlie register-event #N+1** — Phase 1 results surfaced; ratify before Phase 2.

### Phase 2 — Producer edits (TDD)

- **T9** Write FAILING tests for producer edits (per §6 enumeration); RED.
- **T10** Edit `scripts/run_phase2c_evaluation_gate.py`:
  - `_evaluate_one_candidate` at :480 — LineageContext threading + γ3/γ4 merge **into inline per-candidate JSON write at scripts:550-556** (NOT into `_write_aggregate_summary`); verify engine has already done write_per_bar_artifact + registry stamping in Phase 0
  - EDIT `_write_aggregate_summary` at :706 — **cohort-level fields only** (forward_window_metadata + audit_only_* + by_theme + lineage_check + engine_commit + current_git_sha); per-candidate γ3/γ4 are at inline JSON write per above
  - NEW `_finalize_batch_registry()` — writes **ONLY the 1 parent batch_summary row** at `run_id=phase4_forward_2026_15bps_v1_b_c_narrow` (per §3.2.3); the 39 child rows are written per-candidate inside engine's `run_regime_holdout` `_write_to_registry` call (Phase 0 sequencing per §3.1.2). On parent-row partial-write failure: compensating-cleanup per §7 R9 (refuse-if-exists OR `DELETE WHERE parent_run_id = '...'` + re-fire)
  - NEW archive step — idempotent move with refuse-if-exists guard
  - `_CSV_FIELDS` extension at :581-595 — add γ3 / γ4 / T_obs / returns_per_bar_path / returns_per_bar_sha256
- **T11** Run T9 tests → GREEN. Full test suite zero regression. Update T1.4 baseline maintenance per **Phase 0 (T2-T4 engine edits) + Phase 2 (T9-T10 producer edits)** cumulative impact (see §6.4); Phase 1 is BLOCKING gates only (T5-T8), no code edits → no T1.4 impact.
- **Charlie register-event #N+2** — Phase 2 implementation ratify before Phase 3.

### Phase 3 — Fire (data recovery execution)

- **T12** Archive original: `mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1 data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` (guarded by G7 idempotency).
- **T13** Run producer:
  ```
  python -m scripts.run_phase2c_evaluation_gate \
    --candidate-hashes <39 csv from archive/phase4_forward_2026_15bps_v1_d0b8101/holdout_results.csv> \
    --source-batch-id phase2c_15_main_fire_combined \
    --regime-key evaluation_regimes.forward_2026 \
    --execution-config config/execution_phase4_15bps.yaml \
    --run-id phase4_forward_2026_15bps_v1_b_c_narrow \
    --output-root data/phase2c_evaluation_gate/
  ```
  **Producer write target locked**: `--run-id phase4_forward_2026_15bps_v1_b_c_narrow` + producer's `run_dir = output_root / run_id` (scripts:908) → producer writes to **sibling dir** `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow/`. Distinct from canonical path during Phase 3 fire; T14b relocates after V4 PASS.
- **T14** Run V4 reproducibility gate (G4-G7) on sibling dir vs archived original at `archive/phase4_forward_2026_15bps_v1_d0b8101/`:
  - Compare per-candidate metrics at ε=1e-6
  - Verify per-bar parquet integrity
  - Verify γ3/γ4 round-trip
  - Verify registry parent-child integrity
- **T14b** **NEW — Canonical-path relocation** (only if T14 V4 PASS; per §2 Q3 = A3 "overwrite canonical path with new B-C-narrow output"):
  - `mv data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1_b_c_narrow data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1`
  - Registry rows already reference `run_id=phase4_forward_2026_15bps_v1_b_c_narrow` (parent + 39 children); path-content fields in JSON (`returns_per_bar_path` etc.) remain relative;canonical path is the directory name only
  - Verify canonical path now repopulated; sibling dir gone
  - Downstream consumers reading `phase4_forward_2026_15bps_v1/` see new B-C-narrow content;original lineage preserved at `archive/phase4_forward_2026_15bps_v1_d0b8101/`
- **Charlie register-event #N+3** — Phase 3 results ratify before SEAL.

### Phase 4 — SEAL

- **T15** Write `docs/phase5/B_C_NARROW_DATA_RECOVERY_NOTE.md` (D1; ~400-600 lines) covering all §1-§10 content + V4 audit results.
- **T16** SEAL bundle:
  - B2 standing rule 2-leg reviewer dispatch (Codex + advisor) on NOTE doc + code edits
  - Adopt findings + Rule 2 SEAL-eve adversarial dispatch (mandatory per cumulative 26+ instance empirical)
  - Atomic commit: NOTE doc + producer code edits + engine extension + tests + T1.4 baseline maintenance + Phase Marker + history.md + new data artifact files (gitignored but referenced in commit message)
- **Charlie register-event #N+4** — SEAL bundle fire authorization.

---

## §6 — Tests (TDD; write tests first per CLAUDE.md)

### §6.1 Test file impact

| Action | Path | Purpose |
|---|---|---|
| EXTEND | `tests/test_phase2c_evaluation_gate_runner.py` | ~12 new test methods for producer-side edits |
| EXTEND | `tests/test_t1_1_artifact_writer.py` | NEW tests for engine-level Phase 0 changes (RegimeHoldoutResult.equity_curve, run_regime_holdout sequencing) |
| NEW | `tests/test_b_c_narrow_recovery.py` | E2E smoke with N=2 cohort_a candidates against recovered raw_payloads |
| NEW | `tests/test_b_c_narrow_v4_reproducibility.py` | V4 ε=1e-6 + γ3/γ4 round-trip snapshot tests |
| EXTEND | `tests/test_t1_4_backward_compat.py` | Baseline maintenance: `_B1_LOCKED_4TUPLE` update + dynamic-pattern allowlist extension |

### §6.2 Engine-level test additions (Phase 0)

- `test_regime_holdout_result_exposes_equity_curve_field()`
- `test_regime_holdout_result_dataclass_field_count_12()`
- `test_run_regime_holdout_writes_artifact_before_registry()` — verify call ordering
- `test_run_regime_holdout_registry_row_includes_returns_per_bar_path()` — verify atomicity of registry + artifact metadata

### §6.3 Producer-level test additions (Phase 2)

- `test_evaluate_one_candidate_uses_equity_curve_from_extended_result()`
- `test_evaluate_one_candidate_merges_moments_into_summary()`
- `test_evaluate_one_candidate_summary_includes_returns_per_bar_path_sha()`
- `test_finalize_batch_registry_writes_parent_row_only()` — verify `_finalize_batch_registry()` writes ONLY the 1 parent batch_summary row;the 39 child rows are written per-candidate inside engine's `run_regime_holdout` `_write_to_registry` call (sequence verified at Phase 0 G3.5)
- `test_finalize_batch_registry_parent_cohort_metadata_complete()`
- `test_finalize_batch_registry_child_run_id_deterministic_scheme()`
- `test_finalize_batch_registry_parent_idempotency_refuses_duplicate()`
- `test_finalize_batch_registry_compensating_cleanup_on_partial_failure()` — verify partial-cohort writes can be cleaned (DELETE WHERE parent_run_id = ...) for re-fire from clean state per §7 R9 compensating-cleanup discipline (NOT single-transaction;`insert_run()` commits internally per experiment_registry.py:315)
- `test_archive_step_creates_archive_dir_if_absent()`
- `test_archive_step_refuses_existing_archive_target()`
- `test_csv_fields_extension_includes_new_columns()`
- `test_schema_domain_routing_evaluation_for_summary_b_c_extended_for_parquet()`

### §6.4 V4 reproducibility tests

`tests/test_b_c_narrow_v4_reproducibility.py`:

- `test_v4_per_candidate_metric_diff_within_epsilon()` — snapshot fixture vs new artifact for N=2 sampled candidates
- `test_v4_total_trades_exact_match()` — integer + bool exact
- `test_v4_drift_stop_condition_blocks_seal_on_breach()` — inject ε breach → assert SEAL gate raises
- `test_g4_per_bar_parquet_row_count_matches_t_obs()` — G4 direct gate coverage: load parquet → row count = T_obs from summary + **`timestamp` column UTC-aware** (parquet writes `timestamp` as a column not as the index per engine.py:498-510;assertion on column dtype timestamp tz-aware UTC) + non-degenerate (not all-NaN)
- `test_g5_gamma_round_trip_from_parquet_within_epsilon()` — G5 direct gate coverage: load parquet → `compute_moments(compute_per_bar_returns)` recompute = stored γ3/γ4 within abs diff < 1e-10

Fixture: `tests/fixtures/b_c_narrow_archived_baseline.json` captured from `archive/phase4_forward_2026_15bps_v1_d0b8101/` for N=2 sample candidates (specific keys only: sharpe, max_dd, total_return, total_trades, holdout_passed, gate_pass_per_criterion fields). Specific-keys-only comparison avoids full-dict drift on schema-version-bump.

### §6.5 T1.4 baseline maintenance update (`_B1_LOCKED_4TUPLE`)

Current state (verified `tests/test_t1_4_backward_compat.py:83-88`): `(prod_count: 4, test_count: 49, scripts_count: 0, dynamic_count: 23)`.

§6.2 (engine tests) + §6.3 (producer tests) + §6.4 (V4 reproducibility tests) enumerate **4 + 12 + 5 = 21 new test methods** (revised post-PFR with G4/G5 additions).

Estimated post-cycle state (plan v1 to confirm via dry-run grep):

- `test_count`: 49 → **count NEW `_write_to_registry()` call sites in the 21 new test methods** (NOT 21 directly — only counts tests that invoke _write_to_registry; many new tests are about producer logic / parquet integrity / moment round-trip and may not call _write_to_registry). Estimate +5 to +12 call sites depending on which tests touch the registry. Plan v1 computes exact via grep.
- `dynamic_count`: 23 → estimate +3 to +6 (depends on `_write_to_registry(**args)` patterns in new tests; T1.4 single-pattern adjudication discipline forbids ad-hoc allowlist expansion — new test files may need refactor to avoid dynamic pattern OR explicit allowlist addition with rationale per T1.5/T1.6 precedent)
- `prod_count`: 4 → unchanged (no new production `_write_to_registry` call sites; existing engine call at line 2476 is sequence-changed not added; lines 771/1841/1896/2476 all preserved)
- `scripts_count`: 0 → unchanged

**Existing test stubs requiring update post-Phase-0 dataclass extension**:

- `tests/test_phase2c_evaluation_gate_runner.py:83` — `RegimeHoldoutResult(...)` constructor needs `equity_curve=` arg
- `tests/test_t1_4_backward_compat.py:1384` — same

These stub updates are part of Phase 0 test deliverable, not separate from T1.4 baseline maintenance.

If new test files require allowlist additions to the dynamic-pattern allowlist (per T1.4 §6.4 discipline), the allowlist extension must be documented inline with adjudication rationale (per T1.5/T1.6 precedent — single-pattern adjudication discipline).

### §6.6 Fixture strategy

- **Stub backend pattern**: `source_batch_id="stub-source"` (string-value pattern at existing `tests/test_phase2c_evaluation_gate_runner.py:174`, `:219`, etc.) for fast unit tests not requiring real engine execution.
- **Sampled real-engine E2E**: N=2 cohort_a candidates (e.g., `18d92ce5d0b40cc7` + `8a2a8f73f71a835e`) — uses recovered raw_payloads + recovered combined synthetic dir; verifies producer + engine end-to-end.
- **Frozen snapshot fixture**: `tests/fixtures/b_c_narrow_archived_baseline.json` captured from archived original for V4 comparison.

### §6.7 Test execution requirement

Existing 2317-test suite (per CLAUDE.md HARD CONSTRAINT pc7) plus new tests from §6.2-§6.4 (**~21 new methods** per §6.5 enumeration: 4 engine + 12 producer + 5 V4) — total at impl-time will be approximately 2338; binding is "zero regression vs current HEAD test count + cycle delta", not a frozen integer.

---

## §7 — Risk disclosure (R1-R11 after B2 dispatch ADOPT)

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| **R1** | V4 engine-diff audit (G1) surfaces semantic drift across 3 `backtest/` commits (`ec647dc` + `12dffde` + `44840a3`) | HIGH (cycle-blocking) | G1 pre-implementation gate; per Codex preliminary classification all 3 likely additive (T1.1 + T1.6 + lineage commit) but plan v1 must classify formally per Codex Verification #5. If semantic-affecting found → Charlie register adjudication per V4 drift stop-condition (§4.2). Mitigation option of "checkout d0b8101 + cherry-pick" is **NOT eligible** at current Q2=E1 lock (would require Q2 re-litigation) |
| **R2** | StrategyDSL backward-compat (G2) fails on recovered responses | HIGH (cycle-blocking) | G2 pre-implementation gate; N ≥ 39 sample;identify schema-drift commit if failure;Charlie register adjudication |
| **R3** | Cold-storage offline during cycle execution | MEDIUM | Mitigated by completed rsync 2026-05-26;recovered raw_payloads now resident in local repo;ongoing dependency documented in `docs/operations/MAC_MINI_DATA_REFERENCE.md` |
| **R4** | Registry write conflict — superseded by Approach D' Phase 0 engine extension (write_per_bar_artifact moved inside run_regime_holdout before _write_to_registry) | RESOLVED | Resolution baked into Phase 0 §3.1 architecture |
| **R5** | Per-candidate failure handling (DSL load fail / engine error) | MEDIUM | Existing producer pattern at `scripts/run_phase2c_evaluation_gate.py:525-528` catches per-candidate exceptions → `lifecycle_state='holdout_error'` + continue. Original artifact had 39/39 successful; expect same for re-run. Any `holdout_error` in re-run → SEAL blocked pending Charlie adjudication |
| **R6** | Resume vs restart-from-zero discipline | LOW | 39 × ~0.25s = ~10s total wall-clock → restart-from-zero is operationally trivial. Archive step with refuse-if-exists guard enforces rerun-clean-into-empty-dir |
| **R7** | Cycle empirically reaffirms §35.9 + §35.10 + potential §35.X codification candidate (positive) | INFO | §35.A candidate "DSL preservation must outlive producer-batch lifecycle" + §35.B candidate "Off-repo data reference registry as standing operational discipline" — both NAMED placeholders per §9 anti-pre-emption (NOT pre-bound to specific §35 subsection numbers) |
| **R8** | SEAL-eve adversarial gate surfaces new MEDIUM/LOW finding requiring 1-2 v_impl_polish iterations | LOW (expected) | Per Rule 2 + cumulative 26+ instance empirical at B-C-extended + R6.1 §2.2 narrow patch cycles. Plan v1 budgets for expected polish iterations (not as emergency) |
| **R9** | Registry transactional integrity — partial-write of 39 children + 1 parent on crash mid-write | HIGH | **Single-transaction wrap NOT feasible**: `insert_run()` commits internally at `experiment_registry.py:315`; engine child writes happen one candidate at a time per current sequence. **Mitigation = compensating cleanup with partial-idempotency**: if any child row INSERT fails mid-cohort (e.g., primary-key conflict on partial-rerun), the cycle SHOULD (a) refuse start if any child row exists from prior aborted attempt (parent guard) OR (b) DELETE all rows tagged with this `parent_run_id` then re-fire from clean state. Deterministic child run_id scheme `{parent_run_id}_{hypothesis_hash}` enables identification of partial-write rows. Plan v1 locks specific compensating-cleanup mechanism |
| **R10** | Archive idempotency — silent overwrite vs refuse vs auto-renumber | HIGH | Locked semantics: **refuse if archive target exists** (per §3.2.4 + §4.3 G7). No silent overwrite. No auto-rename. Cycle re-run after partial archive requires manual cleanup |
| **R11** | Approach D' Phase 0 engine extension introduces own bugs / breaks unrelated engine code paths | MEDIUM | Tests gated per §6.2 (engine-level test additions BEFORE producer edits per TDD). Phase 0 scope **strictly bounded**: only RegimeHoldoutResult.equity_curve field + run_regime_holdout internal sequencing. NO new engine mode. NO refactor of unrelated engine. Full test suite zero-regression required post-Phase-0 |

---

## §8 — Cross-cycle data-availability acknowledgement

### §8.1 Empirical finding 2026-05-26

The 5 PHASE2C_15 cohort_a source batches (`355a8f9f` / `4f894318` / `71d42a07` / `91ad68ed` / `a12c2a65`) + combined synthetic dir (993 attempt symlinks + 5 source_stage2d_summary symlinks = 998 total) were preserved on cold-storage; rsync recovery completed 2026-05-26 at commit `0bf9b3f` (security-amended to `53090a0`). The recovery was previously assumed lost; cold-storage single-point preservation was the actual state.

Operational reference at `docs/operations/MAC_MINI_DATA_REFERENCE.md` registers the cold-storage location via SSH alias `mac-mini-cold-storage` (committed text contains no IP / username / absolute path).

### §8.2 Cross-cycle INDETERMINATE re-evaluability

Distinction between two recoverability classes:

**Class A — raw_payloads-recoverable** (5 cohort_a source batches recovered 2026-05-26):

| SEAL artifact | Section | INDETERMINATE classification | Recoverable? |
|---|---|---|---|
| `R2_1_STRATUM_B_DSL_AUDIT_NOTE.md` | §5 | 0/4 D3-hash matches | ✓ Yes (re-run D3-hash matching) |
| `R2_3_THEME_TAG_PROVENANCE_NOTE.md` | sub-claims | theme_override / post-rotation-filtering not verifiable | ✓ Yes |
| `R5_1_PHASE_B_CANDIDATE_SUBSET_COMMITMENT_NOTE.md` | §3 dim (d) | 37 candidates DSL-UNAVAILABLE | ✓ Yes (re-verify dim (d)) |
| `R5_2_PHASE_B_SELECTION_INFLATION_HANDLING_NOTE.md` | §3.X | R5.1 carry-forward | ✓ Yes |
| `R6_1_TIER_6_PROMOTION_CLASS_NOTE.md` | §8 (a) DSL | DSL availability | ✓ Yes — empirically resolved this cycle |

**Class B — different gap class** (NOT raw_payloads-driven):

| SEAL artifact | Section | INDETERMINATE | Recoverable? |
|---|---|---|---|
| `R6_1_TIER_6_PROMOTION_CLASS_NOTE.md` | §8 (b) per-bar returns + γ3/γ4 | Engine→writer artifact preservation gap | ⚠️ Resolved by THIS cycle (Approach D' producer wiring + Phase 0 engine extension) |
| `B_C_EXTENDED_SCOPE_B_NOTE.md` | (driver for R6.1) | Engine-layer infrastructure gap | ✗ NOT raw_payloads-driven; resolved by T1.x sealed infrastructure (already done) + producer-wiring (THIS cycle) |

### §8.3 Sealed-content invariance discipline (Architecture B precedent)

Per Architecture B precedent (R6.1 §2.2 narrow patch errata SEAL `506285b`) + R3.1a §12 + R2.3 β3 hybrid: **R2.1 / R2.3 / R5.1 / R5.2 / R6.1 SEAL artifacts MUST NOT be modified in place**. The INDETERMINATE classifications were correct at their SEAL register-event time. The new empirical finding flows through:

(a) This NOTE doc §8 cross-cycle acknowledgement (single-source-of-truth in `docs/operations/MAC_MINI_DATA_REFERENCE.md` audit table; this section is a cross-reference)
(b) Future §9 NAMED successor cycles' errata supplements

No retroactive edit of sealed text.

### §8.4 Methodology reaffirmation

This cycle empirically validates 3 standing rules:

- **METHODOLOGY_NOTES §34** (Data-accessibility pre-verification): pre-commit audit-criterion lock at R6.1 V_SEAL §8 correctly anticipated B-C-narrow as data-recovery successor
- **METHODOLOGY_NOTES §35.9** (Data-preservation as pre-commit audit criterion at artifact-design boundary): this cycle is the first consumption of T1.x sealed infrastructure post §35.9 codification
- **METHODOLOGY_NOTES §35.10** (Anti-recurrence via invariant-level constraints): Approach D' closes the §35.9 invariant gap at producer-class boundary (via Phase 0 engine extension at the smallest possible scope) — case-by-case enumeration of cohort recovery scripts (rejected Approach A) would have repeated the asymmetry

---

## §9 — Eligible-not-named successor cycles (anti-pre-emption preserved)

Each entry is NAMED eligibility class only; **not in this cycle scope**; each requires separate Charlie register-event before fire.

### §9.1 Tier 6 evaluation gated chain

- **Post-V_SEAL Tier 6 evaluation application** (R6.1 Path α invariant): per-candidate DSR computation + threshold check + promotion list under (a1) prescription using B-C-narrow recovered data;separate Charlie register;gated by THIS cycle SEAL

### §9.2 R-AUDIT-FIRST NEW NAMED successors

- **R2.1-DSL-re-verification cycle** — re-run 4 R2.1 target D3-hash matching against recovered raw_payloads
- **R2.3-theme-tag-re-verification cycle** — re-verify theme_override + post-rotation-filtering claims
- **R5.1-dim-(d)-re-verification cycle** — re-verify dim (d) per 37 candidate against recovered DSLs
- **R5.2-DSL-re-verification-carry-forward cycle** — extension of R5.1 outcome to R5.2 carry-forward entries

### §9.3 Methodology / codification successors

- **§35.A codification candidate** (NEW per Mac mini finding): "DSL preservation must outlive producer-batch lifecycle"; specific subsection number NOT pre-bound at this cycle (per anti-pre-emption)
- **§35.B codification candidate** (NEW per cold-storage registry establishment): "Off-repo data reference registry as standing operational discipline"; specific subsection number NOT pre-bound
- **SD-E-γ stationary bootstrap variance overlay upgrade** (Politis-Romano 1994; within-candidate serial-correlation per R6.1 §12.4 axis-governance map; eligible at post-Tier-6-application)
- **Form A asymptotic vs Form B closed-form framing tension resolution** (deferred to post-V_SEAL Tier 6 evaluation application register-event per Path α invariant)
- **R6.1-A/B/C codification cycle** per Charlie register #5 R6.1 V_SEAL (carryover from prior cycle handoff)
- **R5.2 cycle empirical memory codification** (R5.2-A through R5.2-G; 7 findings;carryover)
- **B-C-extended cycle SEAL bundle component 3** (memory codification batch;carryover)

### §9.4 Conditional

- **Conditional RW/WY framework family reopen at successor-cycle boundary** (advisory-trigger candidates per R6.1 §12.6 E6; NO automatic fire; NO pre-locked numeric thresholds)

### §9.5 Other Charlie-specifiable

R2.2 Monday-pattern mechanism investigation + P2a DSL recovery + R3.1b/c + supplementary IS-OOS analytical cycle per R5.1 §1.5 Path 1+ + Phase 4 paper-trading deployment + mechanism investigation for FLIP-TRIGGERED candidates + Bonferroni eligibility re-evaluation + advisor /agents-UI refresh + Tier-0 pause + Phase 2.5 bandit-dedup (parked) + pre-existing noise cleanup + advisor opus model effects pilot extended observation + project pause / strategic-absorption + other Charlie-specifiable.

---

## §10 — SEAL bundle composition + cycle discipline

### §10.1 Atomic commit components

Per prior cycle SEAL precedent (R5.1 + R5.2 + R6.1 + B-C-extended + R6.1 §2.2 narrow patch):

| Component | Path | Action |
|---|---|---|
| NOTE doc | `docs/phase5/B_C_NARROW_DATA_RECOVERY_NOTE.md` | NEW (~400-600 lines; English-only body per prior SEAL precedent) |
| Engine extension (Phase 0) | `backtest/engine.py` | MODIFY at lines 2044-2063 (RegimeHoldoutResult dataclass) + lines 2476-2500 (run_regime_holdout sequencing) |
| Producer edits | `scripts/run_phase2c_evaluation_gate.py` | MODIFY at lines 480 (`_evaluate_one_candidate`), 581-595 (`_CSV_FIELDS`), 706 (`_write_aggregate_summary`), 844 (overwrite protection;reused) + NEW `_finalize_batch_registry()` + NEW archive step |
| Engine tests | `tests/test_t1_1_artifact_writer.py` | EXTEND (Phase 0 engine extension tests) |
| Producer tests | `tests/test_phase2c_evaluation_gate_runner.py` | EXTEND (producer edits tests) |
| New test files | `tests/test_b_c_narrow_recovery.py` + `tests/test_b_c_narrow_v4_reproducibility.py` | NEW |
| T1.4 baseline maintenance | `tests/test_t1_4_backward_compat.py` | MODIFY (`_B1_LOCKED_4TUPLE` update + allowlist extension if needed) |
| Phase Marker | `CLAUDE.md` Phase Marker section | MODIFY (per `feedback_claude_md_freshness.md` discipline) |
| Phase Marker history | `docs/phase_marker_history.md` | MODIFY (Option 1A atomic atomic update; 20+ cumulative trigger) |
| Snapshot fixture | `tests/fixtures/b_c_narrow_archived_baseline.json` | NEW (captured pre-archive per §6.4 specific-keys-only) |
| Data layer (gitignored;NOT in commit) | `data/phase2c_evaluation_gate/archive/phase4_forward_2026_15bps_v1_d0b8101/` (archived original) + `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` (new B-C-narrow output) + registry mutations in `backtest/experiments.db` | Filesystem artifacts produced by Phase 3 fire; NOT in SEAL commit (gitignored); documented in NOTE doc + commit message |

### §10.2 Charlie register chain expected

Per empirical precedent (T1.1 = 9 iterations; T1.6 = 7 versions + 4 PFR rounds; B-C-extended SEAL = 7 versions + 4 PFR + 3 SEAL-eve = ~14 register events): **5-15 register events depending on V4 audit outcome + SEAL-eve iteration count**.

Expected boundaries (~5 minimum):
1. ✓ Cycle entry (today 2026-05-26) — N1 authorized
2. ✓ Design ratify (today) — Q1-Q6 + Approach D' + §1-§10 + B2 dispatch adoption
3. Spec doc commit ratify (next)
4. Plan v1 drafting fire + ratify
5. Phase 0 engine extension ratify
6. Phase 1 pre-implementation gates results ratify
7. Phase 2 producer edits ratify
8. Phase 3 fire ratify (T13 + T14 V4 results)
9. SEAL bundle fire authorization

Plus expected iteration boundaries (1-2 per phase per Rule 2 empirical):
- V4 audit adjudication if drift found (R1)
- SEAL-eve adversarial round findings (R8)
- Possible v_impl_polish iteration(s)

### §10.3 Reviewer discipline

- **B2 standing rule LOCKED 2026-05-19**: 2-leg dispatch (Codex cross-model + advisor opus) at every reviewer round:
  - Plan v_n PFR rounds (≥ 1 per version)
  - NOTE doc v_n PFR rounds
  - Pre-implementation gates result review (G1 + G2 + G3 + G3.5)
  - Post-implementation code review
  - SEAL-eve adversarial dispatch (mandatory per Rule 2 + cumulative 26+ instance empirical)
- **Rule 2 SEAL-eve OPERATIONALLY REQUIRED**: 5-cycle VINDICATED at B-C-extended SEAL; 6-cycle VINDICATED at R6.1 §2.2 narrow patch SEAL; **this cycle expected to surface at least 1 MEDIUM/LOW finding at SEAL-eve**
- **Mode A independent re-verification** at every PFR + SEAL-eve adjudication boundary
- **3-layer safety architecture** all 3 layers operational (Advisor self-discount + Codex cross-model + orchestrator Mode A)

### §10.4 Sealed-content invariance discipline

- R2.1 / R2.3 / R5.1 / R5.2 / R6.1 SEAL artifacts **NOT modified in place** (Architecture B precedent)
- Archived original `archive/phase4_forward_2026_15bps_v1_d0b8101/` **permanently preserved**; no deletion
- Empirical finding "cold-storage preserves data" flows through (a) §8 cross-cycle acknowledgement (b) NAMED successor cycles errata supplements

### §10.5 Pre-implementation prerequisites

- ✓ R6.1 §2.2 narrow patch SEAL `506285b` complete (2026-05-25)
- ✓ MAC_MINI_DATA_REFERENCE.md commit `53090a0` complete (2026-05-26;security-abstracted)
- ✓ raw_payloads recovery via rsync 2026-05-26 (5 sub-batches + combined synthetic dir = 998 symlinks)
- ⚠️ **Push to origin/main decision PENDING**: `506285b` + `53090a0` ahead 2 of `origin/main`. Recommendation: push BEFORE Phase 0 (so reviewer dispatches in Phase 2-4 diff against pushed state, not local-only). Separate Charlie register-event.

### §10.6 SEAL prerequisites checklist (at SEAL bundle fire)

- [ ] Spec doc reviewed + committed (this doc, after Charlie ratify)
- [ ] Plan v1 ratified per Charlie register-event
- [ ] Phase 0 engine extension: tests GREEN + zero regression
- [ ] Phase 1 G1/G2/G3/G3.5 all pass + Charlie ratify
- [ ] Phase 2 producer edits: tests GREEN + zero regression + T1.4 baseline maintenance updated
- [ ] Phase 3 V4 reproducibility: ε=1e-6 + γ3/γ4 round-trip + registry parent-child + archive idempotency all pass
- [ ] NOTE doc B2 2-leg reviewer + ADOPT findings
- [ ] Rule 2 SEAL-eve adversarial dispatch + findings adopted (if any)
- [ ] Phase Marker + history.md update prepared atomic
- [ ] Charlie register-event authorization for SEAL bundle fire

### §10.7 English-only spec body convention

Per R5.1 + R5.2 + R2.3 + R6.1 + B-C-extended + R6.1 §2.2 narrow patch SEAL artifact precedent: NOTE doc body **English-only** (no bilingual). Chinese intuitive explanations are reserved for orchestrator→Charlie surfacing in chat, NOT in committed artifact text. This spec doc follows the same convention (English-only body).

---

## Spec doc maintenance

This spec is the design artifact for B-C-narrow cycle pre-implementation. After cycle SEAL, the canonical artifact is `docs/phase5/B_C_NARROW_DATA_RECOVERY_NOTE.md`. This spec may be:

- Updated in place during plan v1 drafting if findings revise design
- Referenced by plan v1 + NOTE doc as the design provenance
- Preserved as historical record at cycle SEAL (not deleted)

DEFER items (per PFR R1 + R2 + R3 B2 dispatch adjudication 2026-05-26) flagged for plan v1:

1. Codex R1 Section 4 #1 "Write failing tests first" micro-ordering — plan v1 to specify exact RED/GREEN sequencing within Phase 0 + Phase 2 TDD
2. IP6 `scripts/run_phase2c_evaluation_gate.py` 1076-line size discipline (past CLAUDE.md "200-400 typical, 800 max" guideline) — refactor NOT in cycle scope; plan v1 may surface as future tech-debt item
3. **R9 compensating-cleanup specific mechanism choice** (per §7 R9 + §3.2.3 revised wording): plan v1 locks one of (a) refuse-if-any-child-exists-from-prior-attempt + manual cleanup OR (b) `DELETE WHERE parent_run_id = ...` + re-fire from clean state
4. **§3.4 LineageContext construction pattern choice** from a/b/c menu: (a) engine-internal after backtest + write_per_bar_artifact OR (b) engine-internal with producer-passed scalars OR (c) two-phase call. Plan v1 locks specific pattern as Phase 0 T2c deliverable
