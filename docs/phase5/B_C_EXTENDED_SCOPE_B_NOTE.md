# B-C-extended Scope-B Structural Artifact-Preservation Refactor Cycle SEAL Note

**Cycle**: B-C-extended Scope-B structural artifact-preservation refactor (Scope-B from V3 branch; engineering infrastructure cycle; NOT a methodology lock cycle)

**V_SEAL status**: **SEALED at register-event boundary 2026-05-25** per Charlie register "(α') Inline fix + ratify"

**Path framing (locked at prior register-event boundaries)**:
- **Scope-B** (Charlie pre-authorization 2026-05-23): structural artifact-preservation refactor scope; driven by R6.1 §34 data-accessibility pre-verification gap (per-bar return series + per-candidate γ3/γ4 moments NOT preserved at engine→writer boundary; precondition for any DSR-family empirical evaluation)
- **R3.1d sequencing 1→3→4** (carry-forward from prior cycles): all task SEAL ratify events follow R3.1d-locked sequencing
- **B-C-narrow data-recovery successor cycle** (binding condition at R6.1 V_SEAL §10): engine re-run reproducing phase4_forward_2026_15bps_v1 with per-bar return series preservation + per-candidate γ3/γ4 moments + registry linkage; B-C-extended Scope-B is the infrastructure precondition for B-C-narrow
- **Post-V_SEAL Tier 6 evaluation application** (R6.1 Path α invariant): R6.1 V_SEAL methodology lock + B-C-extended Scope-B infrastructure + B-C-narrow data-recovery jointly precondition the Tier 6 evaluation application; the application is itself a separate Charlie register-event under Path α

**HARD CONSTRAINT compliance anchors**:
- CLAUDE.md `❌ NEVER allow trades during the warmup period` + `❌ NEVER compute metrics (Sharpe, drawdown, etc.) including the warmup period` (Execution Integrity)
- CLAUDE.md `❌ NEVER use global aggregations` + `❌ NEVER use future-touching operations in factors` (Factor & Vectorization Integrity)
- CLAUDE.md `❌ NEVER commit code that doesn't pass existing tests` (Code Quality; cycle preserves zero-regression discipline)
- CLAUDE.md `❌ NEVER omit `cost_anchor_id` from `experiment_registry.runs` entries on new Phase B / Tier 5 / Tier 6 runs once schema migration lands` at `:272` (Conservative-Anchor Gate Integrity; cycle delivers the schema migration this references)

**Discipline anchors**:
- **B2 standing rule LOCKED 2026-05-19** (Codex cross-model + Advisor opus 2-leg default; cumulative empirical reaffirmation extended through this cycle at 9+ cycle cumulative scale per [`feedback_reviewer_routing_subagent_default.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md))
- **3-layer safety architecture** (Advisor self-discount + Codex cross-model + orchestrator Mode A independent verification); all 3 layers operational across cycle with Layer 3 load-bearing at T1.6 multiple instances
- **Mode A independent re-verification** (orchestrator grep/Read source on every Advisor specific-claim before adoption); applied at every PFR + SEAL-eve adjudication boundary
- **Anti-pre-emption discipline** (only Charlie register authorizes operational fires; reviewer convergence advisory only); 20+ Charlie register-events during T1.6 cycle alone per T1.6 sub-plan §10 task SEAL chain
- **Authorization-routing hard rule** (Charlie register sole authorization source per [`feedback_authorization_routing.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md))
- **Rule 2 SEAL-eve adversarial OPERATIONALLY REQUIRED** (post-PFR-convergent-APPROVE; vindicated at 2-cycle scale during this cycle — T1.5 SEAL-eve v1+v2 caught HIGH at implementation gate; T1.6 sub-plan SEAL-eve Round 1 caught Codex F1 MEDIUM at sub-plan gate)

---

## §0 Cycle metadata + Charlie register chain

**Cycle entry**: B-C-extended Scope-B cycle authorized by Charlie register 2026-05-22 (cycle-entry boundary per anti-pre-emption discipline); plan drafting commenced same day. Parent plan at [`docs/superpowers/plans/2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md`](../superpowers/plans/2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md) v5 RATIFIED 2026-05-22.

**Plan iteration arc**: v1 → v2 → v3 → v4 → v5 (5 plan iterations; 4 PFR-rule-Y reviewer rounds; ratified at v5 with 2 inline LOW fixes per Codex Fv5-1 + Fv5-2).

**Implementation order LOCKED at plan v5 §9**: T1.2 → T1.3 → T1.1 → T1.4 → T1.5 → T1.6 (schema design first, then registry API extension, then artifact writer, then backward-compat verification, then test suite, then documentation + consumer enumeration).

**Charlie register chain through cycle SEAL** (selected primary register-events; full chain at parent plan §11 + T1.6 sub-plan §10). **Date convention**: dates below are Charlie register-event boundary dates in **UTC** per CLAUDE.md "All times are UTC. No exceptions." When register-events are bundled into a single commit, commit-timestamp UTC date may differ from individual register-event UTC dates (e.g., bundled commit `12dffde` landed 2026-05-23 UTC but bundled T1.2/T1.3 register-events fired 2026-05-22 UTC + T1.1 register-event fired 2026-05-23 UTC).

| # | Date | Register text | Decision class |
|---|---|---|---|
| 1 | 2026-05-22 | "Inline-fix Codex Fv5-1 + Fv5-2 → Charlie direct ratify v5" | Parent plan v5 RATIFY |
| 2 | 2026-05-22 | "(A1) Lock Option (i) with Codex's domain-fence-via-per-domain-tuple-split refinement" | T1.2 Sub-decision A: 3 per-domain ACCEPTED tuples + 3 helpers + CONTRACT BOUNDARY architecture |
| 3 | 2026-05-22 | "(B-lock-Codex) Lock Codex package: (B1-c) hybrid + (B2-b) + (B3-b) BCExtendedSchemaValidationError subclass" | T1.2 Sub-decisions B1/B2/B3: hybrid validation order + Optional parent_run_id + new exception class |
| 4 | 2026-05-22 | "Lock convergent package above" (T1.3-A-ii + T1.3-B + T1.3-C HYBRID + T1.3-D-i) | T1.3 Sub-decisions: SQL ALTER TABLE migration + canonicalize_execution_config_path() + LineageContext primary mechanism + frozen dataclass with kw_only |
| 5 | 2026-05-22 | "(T1.2-SEAL-charlie-ratify)" + "(T1.3-SEAL-charlie-ratify) Charlie direct T1.3 SEAL ratify register" | T1.2 + T1.3 SEAL ratify (bundled at commit `12dffde`) |
| 6 | 2026-05-23 | "charlie-direct-SEAL-ratify authorized" | T1.1 SEAL ratify (cross-leg convergent APPROVE at v9 with Codex explicit "cycle-final APPROVE; no v10 finding predicted") |
| 7 | 2026-05-24 | T1.4 sub-plan v_final ratify + T1.4 SEAL ratify + T1.4 post-SEAL LOW cleanup register chain (multi-register; see T1.4 sub-plan §10) | T1.4 SEAL bundle: `ba982da` + `b647860` + `5a44ec6` + `56fe413` |
| 8 | 2026-05-24 | T1.5 sub-plan v3.2 v_final ratify + T1.5 SEAL ratify register chain (multi-register; see T1.5 sub-plan §10) | T1.5 SEAL bundle: `79fa4dc` + `9d9a40d` |
| 9 | 2026-05-24 | "Authorize sub-plan v_seal ratify" | T1.6 sub-plan v7 v_final RATIFY at commit `b6da611` |
| 10 | 2026-05-25 | T1.6 SEAL ratify register (post-Path-A strict-iterate + FINAL ROUND framing convergence) | T1.6 SEAL at commit `ec647dc` (pushed origin/main) |
| 11 | 2026-05-25 | "path 1 authorized" (this cycle SEAL bundle drafting register-event boundary) | B-C-extended cycle SEAL bundle drafting authorized |

**Orchestrator-adjudication-error instances during cycle (3 instances; covered at §11)**: 3 confirmed instances during the planning arc per parent plan v5 §8 (Risk disclosure → Process risks subsection) short markers (v1 "5.5", v3 "fisher=True 2.5", v4 "12 fields"). No additional instances documented during T1.x SEAL cycles (T1.6 cycle Mode A Layer-3 verifications maintained 0 verified hallucinations across 18+ reviewer dispatches per T1.6 sub-plan §11 addendum). The R6.1-A first-orchestrator-adjudication-error pattern documented at R6.1 V_SEAL artifact §9.1 (referenced from CLAUDE.md Phase Marker §9) is a SEPARATE cycle (R6.1 Tier 6 Promotion Class) — not a B-C-extended instance.

---

## §1 Substantive scope

**Driver**: METHODOLOGY_NOTES §34 standing rule ("Data-accessibility pre-verification for pre-commit audit-criterion locks") applied at R6.1 V_SEAL §8 data-accessibility pre-verification application table produced lock-choice (c) 4-of-7 INDETERMINATE classification documented at R6.1 V_SEAL §11.4 residual-risk closure (SD-A-α BLdP closed-form + N\*-ε scalar + SD-B-α + SD-F Path 1 cascade). All 4 INDETERMINATEs trace to a single common cause — per-bar return series and per-candidate γ3/γ4 moments are NOT preserved at the engine→writer artifact boundary, making any DSR-family analytical computation INDETERMINATE-on-data-unavailability at R6.1 V_SEAL register-event time. B-C-extended Scope-B is the structural infrastructure precondition.

**Scope-B substantive scope (locked at plan v5 §1)**:
1. Per-bar return series preservation at engine→artifact-writer boundary (T1.1)
2. Per-candidate γ3/γ4 moment computation + storage (T1.1 + T1.5)
3. New schema version `b_c_extended_v1` with distinct validation branch (T1.2)
4. Registry linkage from `runs` table to per-bar artifact paths + content hashes + `cost_anchor_id` (T1.3)
5. Backward compatibility verification for legacy artifacts (T1.4)
6. Fixture + smoke + registry-integrity test suite (T1.5)
7. Documentation + consumer enumeration (T1.6)

**Out-of-scope (anti-pre-emption preservation)**:
- B-C-narrow data-recovery successor cycle (engine re-run reproducing phase4_forward_2026_15bps_v1 with preserved per-bar artifacts + γ3/γ4 moments + registry linkage; eligible-not-named at §12)
- Tier 6 evaluation application (R6.1 V_SEAL methodology applied to candidate cohort using recovered data; eligible-not-named at §12)
- R5.2 framework family reopening (eligible-not-named at §12 per R5.2 §2.3 + R6.1 Path X)
- Any per-strategy capital commitment or paper trading deployment

---

## §2 Contract locks 2.0.1-2.0.6 execution outcomes

Contracts locked at parent plan v5 §2.0; sealed across T1.x implementation tasks.

| Contract | Lock summary | SEAL site | Sealed implementation |
|---|---|---|---|
| **2.0.1** Moment estimator convention | γ4 raw kurtosis via `scipy.stats.kurtosis(..., fisher=False, bias=True, nan_policy='omit')`; 5 PROHIBITED alternatives explicitly enumerated (pandas `.kurt()` default; pandas `.kurt() + 3`; scipy default `fisher=True/bias=True`; scipy `fisher=True/bias=False`; scipy `fisher=False/bias=False`); see §6 for sealed test method names + Δ values | T1.5 (`9d9a40d`) | `tests/test_t1_5_fixture_moments.py` 9 methods with 5 PROHIBITED lockout via independent test methods preserving per-library failure attribution |
| **2.0.2** Schema version string + distinct validation branch | `b_c_extended_v1` schema version + `BCExtendedSchemaValidationError(ValueError)` exception subclass (LSP preserves existing `except ValueError` consumers) + B1-c hybrid validation order (fail-fast structural; collect-all per-field) | T1.2 (`12dffde`) | `backtest/artifact_schema.py:50` `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` per-domain tuple + `backtest/artifact_schema.py:556` `BCExtendedSchemaValidationError` + `:667` `check_b_c_extended_semantics_or_raise`; legacy backward-compat union `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` at `wf_lineage.py:129` (frozen alias for pre-domain-split consumers) |
| **2.0.3** Linkage aliasing | `LineageContext` carries triple linkage (run_id ↔ registry runs.run_id; hypothesis_hash; source_batch_id ↔ registry runs.batch_id) | T1.3 (`12dffde`) | `backtest/artifact_schema.py:206` LineageContext dataclass (14 fields = 13 Contract 2.0.5 header excluding artifact_schema_version per D2-b + T_obs required-adjacent 15th field) |
| **2.0.4** `cost_anchor_id` mapping | 6-row path → cost_anchor_id mapping at `backtest/artifact_schema.py:76` `COST_ANCHOR_ID_MAPPING`; `canonicalize_execution_config_path()` at `:96` with commonpath-based containment + case-sensitive exact match + repo-relative POSIX | T1.3 (`12dffde`) | Live DB migration fired at T1.3 SEAL (`cost_anchor_id` column added to `experiments.db`); `experiment_registry.py:121` `MIGRATION_COLUMNS` |
| **2.0.5** Artifact path policy + 14-field schema + per-bar linkage validation | 14 header fields + T_obs as required-adjacent 15th field (per-bar-content-shape attribute outside header table) + file-exists + path-confinement + SHA256-recompute + T_obs-alignment validation discipline | T1.1 + T1.5 + T1.6 (`12dffde` + `9d9a40d` + `ec647dc`) | `backtest/artifact_schema.py:206` LineageContext + `:307-309` T_obs declaration (comment + field) + `:815-827` T_obs validation block (presence + type + positivity); `docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md` §1.5b T_obs documentation |
| **2.0.6** Validation matrix | Per-domain validation: WF/EVALUATION (existing); B-C-EXTENDED (new); per-domain tuple split blocks cross-domain leakage at constant level | T1.2 (`12dffde`) | 3 per-domain tuples: `wf_lineage.py:111` `ACCEPTED_EVALUATION_SCHEMA_VERSIONS` + `:119` `ACCEPTED_WF_SCHEMA_VERSIONS` + `artifact_schema.py:50` `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS`; 1 legacy alias `wf_lineage.py:129` `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` (backward-compat union); 3 per-domain helpers: `wf_lineage.py:262` `check_wf_semantics_or_raise` + `:352` `check_evaluation_semantics_or_raise` + `artifact_schema.py:667` `check_b_c_extended_semantics_or_raise` (CONTRACT BOUNDARY per heavy-private-impl extraction) |

All 6 Contract locks executed against substantive sealed code; no Contract was deferred or partially closed.

---

## §3 Engineering deliverables (T1.1-T1.6) — SEAL outcomes

| Task | SEAL commit | Iteration count | Adversarial rounds | Test delta | Substantive content |
|---|---|---|---|---|---|
| **T1.2** Schema design | `12dffde` (bundle) | 2 PFR | 2 | +69 tests | `backtest/wf_lineage.py` 3 ACCEPTED tuples + 2 helpers + CONTRACT BOUNDARY documentation; `backtest/artifact_schema.py` 3rd helper + per-domain tuple split + LineageContext-precursor + canonicalize_execution_config_path() |
| **T1.3** Registry + API extension | `12dffde` (bundle) | 3 PFR | 3 | +66 tests | `backtest/engine.py` +191 lines (LineageContext threading at 4 entry points with asymmetric architecture: opt-in kwarg at `run_backtest` + `run_regime_holdout`; scalar `execution_config_path` retained at `run_walk_forward` + evaluation-gate driver per T1.1 slice-aware-boundary discipline; consumption converges at `_write_to_registry` — see §9 for detail); `backtest/artifact_schema.py` LineageContext canonical site (14 fields, frozen dataclass, kw_only); FIX-H2 cost-config/registry alignment + FIX-B1-extension parent_run_id defensive + FIX-M2-extension Path('') guard |
| **T1.1** Artifact writer + slice-aware emission | `12dffde` (bundle) | 9 PFR | 9 | +143 tests (sys_fix) +80 tests (artifact_writer) | `backtest/engine.py` `compute_per_bar_returns` + `compute_moments` + `write_per_bar_artifact` + 4 write-boundary mirrors + DESIGN INVARIANT marker at engine.py:1133-1148; `backtest/artifact_schema.py` SYS4 LATE_FILL `__post_init__` invariant + SYS5 `LineageContext.revalidate_for_write()` centralized 14-field tamper closure (structural pattern-breaker over 5-asymmetry-class enumeration; cycle-final convergent APPROVE at v9 with Codex explicit "no v10 finding predicted") |
| **T1.4** Backward compatibility verification | `ba982da` + `b647860` + `5a44ec6` + `56fe413` | 6 sub-plan + 4 implementation | 5 sub-plan PFR + 4 implementation PFR-rule-Y + 2 SEAL-eve | +106 tests (7 test classes; full suite 2297 PASS = baseline 2191 + 106 per T1.4 SEAL commit `5a44ec6` body) | `tests/test_t1_4_backward_compat.py` 4-tuple structure + B3.1/B3.2 LC-positive entry-point flow + B3.3 hermetic + B3.4 smart-mock fidelity; 6th asymmetry class B3.1/B3.2 LC-positive entry-point bypass caught at v3 SEAL-eve via Codex cross-model leg (Advisor framed Codex MEDIUM as "bounded scope; not actionable" — Rule 3 reaffirmed) |
| **T1.5** Fixture/smoke/registry-integrity test suite | `79fa4dc` + `9d9a40d` | 5 sub-plan + 2 v_impl_polish | 1 sub-plan PFR + 3 PFR-rule-Y + 1 Implementation PFR + 2 SEAL-eve | +20 tests | 3 NEW test files: `test_t1_5_fixture_moments.py` (9 methods); `test_t1_5_smoke_end_to_end.py` (4 methods + 176-bar 2023-08 OHLCV window + N=2 SMA hand-written candidates); `test_t1_5_registry_integrity.py` (7 methods + triple-resolution + 5 failure-cases + 1 case-mismatch APFS edge + 2 xfail DS8 PENDING) |
| **T1.6** Documentation + consumer enumeration | `b6da611` + `ec647dc` | 7 sub-plan + 6 v_impl_polish | 14 reviewer rounds (4 sub-plan PFR-rule-Y + 2 sub-plan SEAL-eve + 1 Implementation PFR + 1 T1.6 SEAL-eve Round 2 + 6 PFR rounds post-v_impl_polish through FINAL ROUND); plus 6 v_impl_polish fix iterations (distinct from reviewer rounds) | (no test-collection delta; doc-only cycle; `tests/test_t1_1_sys_fix.py` + `tests/test_t1_3_registry_api.py` modified per `ec647dc` for comment/docstring updates only — collection count stable at 2317) | 3 NEW `docs/decisions/`: `B_C_EXTENDED_V1_SCHEMA_SPEC.md` (750 lines; M1 (a)-(d) canonical); `SCHEMA_VERSION_EXTENSION_PROTOCOL.md` (382 lines; γ Hybrid (f) per DS2); `B_C_EXTENDED_V1_CONSUMER_ENUMERATION.md` (684 lines; γ Hybrid (g) consumer enumeration HANDLES=181/NO-OP=31/NEEDS-EXTENSION=0); `data_dictionary.md` Section 2.x + NEW Section 4 (14 header + T_obs + per-bar parquet); `backtest/wf_lineage.py` extension protocol docstring updates |

---

## §4 Validation results

**Test suite outcome at cycle final** (post-T1.6 SEAL, baseline locked at T1.5 SEAL `9d9a40d`):
- **2317 tests collected** (Mode A verified via `python -m pytest tests/ --collect-only` at cycle SEAL drafting time)
- **2315 PASS + 2 xfail + 0 FAIL** at T1.5 SEAL baseline per CLAUDE.md HARD CONSTRAINT `❌ NEVER commit code that doesn't pass existing tests` (at `CLAUDE.md:278`)
- **2 xfail = T1.5 DS8 PENDING** (strict-vs-conditional rejection scope per anti-pre-emption + T1.5 sub-plan §3.2 failure handling; both `strict=True` per T1.5 sub-plan §3.1 PASS criteria item 2 ("pc7" is T1.5 sub-plan internal numbering, not a CLAUDE.md label))
- **Zero-regression preserved** across all T1.x SEAL boundaries (per CLAUDE.md HARD CONSTRAINT `❌ NEVER commit code that doesn't pass existing tests` at `:278` enforced at each T1.x SEAL ratify gate)

**Coverage at registry happy-path** (T1.5 HIGH-2 closure): tight 9/9 T1.x columns covered at registry happy-path (`returns_per_bar_path` + `returns_per_bar_sha256` + `T_obs` + `regime_key` + `current_git_sha` + `execution_config_path` + `execution_config_sha256` + `parquet_data_sha256` + `cost_anchor_id`).

**Cycle empirical totals (reviewer dispatches)**:
- T1.2 + T1.3 + T1.1 cumulative: 14+ cross-leg LOAD-BEARING instances within bundle (6 within T1.1 9-iteration arc + 8 cumulative pre-T1.1)
- T1.4 cycle: ~22+ reviewer dispatches across 5 sub-plan PFR (10 leg-dispatches) + 4 implementation PFR-rule-Y (8 leg-dispatches) + 2 SEAL-eve (4 leg-dispatches)
- T1.5 cycle: 16+ reviewer dispatches across 8 Advisor opus instances
- T1.6 cycle: ~32+ reviewer dispatches across 13 Advisor opus instances (#N1-#N12 enumerated at T1.6 sub-plan §10 task SEAL chain through Round 5 PENDING + #N13 added at T1.6 SEAL commit `ec647dc` per FINAL ROUND BOTH APPROVE-with-LOW convergence) — 4 sub-plan PFR-rule-Y + 2 sub-plan SEAL-eve + Implementation PFR + T1.6 SEAL-eve Round 2 + 6 PFR rounds post-v_impl_polish through FINAL ROUND convergence
- **Cumulative cycle total: ~90+ reviewer dispatches** (across all T1.x sub-cycles + implementation + SEAL-eve rounds; floor estimate per per-task subtotals — T1.2 + T1.3 + T1.1 bundle adding ~28 dispatches + T1.4 ~22+ + T1.5 16+ + T1.6 ~32+)

**Mode A verifications**: applied at every PFR + SEAL-eve adjudication boundary; 0 verified Advisor hallucinations across cycle's 18+ Advisor opus dispatches post-/agents-fix opus regime; 0 Codex hallucinations across cycle dispatches (Codex `[VERIFIED]` tokens reliable evidence per cumulative R3.1d + R2.0 + R2.1 + §34 + R2.3 + R5.1 + R5.2 + R6.1 + B-C-extended cycle empirical).

---

## §5 Schema spec documentation (T1.6 (a)-(d) M1 deliverables)

**Canonical document**: [`docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md`](../decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md) (750 lines; sealed at T1.6 SEAL `ec647dc`).

**Architecture documented** (per T1.2 Sub-decision A lock + T1.6 §2.1 v6 SEAL-eve restructure):
- **3 per-domain tuples + 1 legacy alias**: 3 per-domain tuples are `ACCEPTED_EVALUATION_SCHEMA_VERSIONS` at `wf_lineage.py:111` + `ACCEPTED_WF_SCHEMA_VERSIONS` at `:119` + `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` at `artifact_schema.py:50` (the B_C_EXTENDED tuple is co-located with the rest of the heavy-private-impl in `artifact_schema.py` per CONTRACT BOUNDARY; available via re-export shim at `wf_lineage.py:554-563`). 1 legacy alias `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` at `wf_lineage.py:129` is a frozen backward-compat union for pre-domain-split consumers; new code uses the per-domain tuples directly.
- **3-helper architecture**: `check_wf_semantics_or_raise` at `wf_lineage.py:262` + `check_evaluation_semantics_or_raise` at `:352` + `check_b_c_extended_semantics_or_raise` at `artifact_schema.py:667`. Public shim re-export of the B_C_EXTENDED helper via `wf_lineage.py:554-563`.
- **CONTRACT BOUNDARY**: heavy-private-implementation co-located with `COST_ANCHOR_ID_MAPPING` + `canonicalize_execution_config_path` + `LineageContext` in `artifact_schema.py` for atomic-maintenance SSOT.

**T_obs as 15th required-adjacent field** (per Schema spec §1.5b; sealed at T1.6 sub-plan SEAL-eve Round 1 Codex F1 MEDIUM ADOPT): T_obs is a per-bar-artifact-content-shape attribute (positive integer count of finite per-bar return observations), required at consumption-time but documented OUTSIDE the Contract 2.0.5 14-field header table because the 14-field table is header metadata while T_obs is content-shape metadata. Sealed declaration at `artifact_schema.py:307-309` (comment "T_obs is not in the 14-field header table but is required for artifact validation" + `T_obs: int` field annotation) + validation block at `:815-827` (presence check + type check + positivity branch). Registry linkage at `experiment_registry.py:121` MIGRATION_COLUMNS (entry within 9 T1.x columns).

---

## §6 γ4 convention specification with fixture vector verification

**Locked convention** (Contract 2.0.1 SEAL at T1.5 `9d9a40d`): `scipy.stats.kurtosis(returns, fisher=False, bias=True, nan_policy='omit')` returns γ4 raw (population) kurtosis.

**Two distinct sealed γ4 values at T1.5** (separate calibration purposes):

1. **Pedagogical fixture vector** `[-1, 1, 0, 0, 0, 0]` — γ4 = **3.0 exactly** (`± 1e-12` tolerance) sealed at `tests/test_t1_5_fixture_moments.py:70` (`_PASS_GAMMA4_EXPECTED: float = 3.0`). Used in moment-estimator unit tests to lock the Contract 2.0.1 LOCKED implementation against 5 PROHIBITED alternatives with `_FAIL_MIN_SEPARATION: float = 0.5` (the tightest empirical Δ across the 5 PROHIBITED implementations).
2. **DS2 canonical OHLCV smoke slice** — 176 hourly bars from 2023-08-01T00:00Z to 2023-08-08T07:00Z; log-return-basis γ4 ≈ **13.73** (sealed at T1.5 sub-plan DS2 Option (i) lock per Charlie register 2026-05-24, commit message body of `79fa4dc`). Used in end-to-end smoke calibration `tests/test_t1_5_smoke_end_to_end.py`.

**5 PROHIBITED alternatives explicitly enumerated** (against the pedagogical fixture vector γ4 = 3.0 baseline; T1.5 `test_t1_5_fixture_moments.py` 5 independent test methods preserving per-library failure attribution; sealed values listed in class docstring at `:95-119` with 5-method summary at `:103-107`; per-method docstrings + assertion targets at `:217-345`):
1. `test_fail_pandas_kurt_default` — pandas `pd.Series.kurt()` default = **2.5** (Δ = −0.5)
2. `test_fail_pandas_kurt_plus_3` — pandas `pd.Series.kurt() + 3` = **5.5** (Δ = +2.5)
3. `test_fail_scipy_fisher_true_bias_true` — scipy default `fisher=True, bias=True` = **0.0** (Δ = −3.0; Fisher excess kurtosis)
4. `test_fail_scipy_fisher_true_bias_false` — scipy `fisher=True, bias=False` = **2.5** (Δ = −0.5)
5. `test_fail_scipy_fisher_false_bias_false` — scipy `fisher=False, bias=False` = **5.5** (Δ = +2.5)

Each PROHIBITED variant has an independent test method with assertion that the variant value differs from the locked γ4 by ≥ `_FAIL_MIN_SEPARATION` (0.5); failure of any single variant assertion does NOT mask others (per-library failure attribution preserved by independent-test discipline).

---

## §7 Backward compatibility verification (T1.4 outcome)

**Sealed at**: T1.4 SEAL bundle `ba982da` (sub-plan v_final) + `b647860` (sub-plan amend v6→v7) + `5a44ec6` (T1.4 SEAL ratify) + `56fe413` (post-SEAL LOW cleanup).

**Verification scope** (T1.4 sub-plan v_final §2): 4-tuple structure covering canary tests for:
- **B1**: Aggregate CSV legacy artifacts continue to read + validate under legacy validation path (NO `b_c_extended_v1` discrimination forced on legacy artifacts)
- **B2**: Aggregate JSON legacy artifacts continue to read + validate under legacy validation path
- **B3**: ALL N per-candidate legacy artifacts continue to read + validate under legacy validation path (3 sub-tests at B3.1/B3.2 LC-positive entry-point flow + B3.3 hermetic isolation + B3.4 smart-mock fidelity)
- **B6**: artifact_dir per-task discipline

**6th asymmetry class caught at v3 SEAL-eve** (Codex DIVERGED MEDIUM that Advisor framed as "bounded scope; not actionable"; Rule 3 reaffirmed): B3.1/B3.2 LC-positive entry-point bypass. Test substituted a writer-boundary simulation that passes lower-layer validation while the actual entry-point flow chain was broken; smart-mock fidelity gap (no `db_path` enforcement on default mock). Cycle iterations through v4 implementation post-fix.

**v_impl_polish iteration count**: 4 iterations + 2 SEAL-eve rounds = 6 adversarial rounds at T1.4 implementation phase (cumulative T1.4 cycle: 5 sub-plan PFR + 6 implementation/SEAL-eve = 11+ reviewer rounds at T1.4 boundary).

**Layer 2 cross-model leg load-bearing**: 5/5 implementation-review iteration positions at T1.4 cycle had Codex substantive catch that Advisor missed or downgraded; the 6th asymmetry class catch at v3 SEAL-eve specifically would have shipped under Advisor-only review.

---

## §8 cost_anchor_id mapping + canonicalization + registry linkage verification

**Sealed at**: T1.3 SEAL bundle `12dffde` (canonical mapping site + canonicalize function + LineageContext threading); T1.5 SEAL bundle `9d9a40d` (registry-integrity test suite).

**6-row `COST_ANCHOR_ID_MAPPING`** at `backtest/artifact_schema.py:76`:
- Maps canonicalized repo-relative POSIX execution config paths → `cost_anchor_id` strings (per CLAUDE.md HARD CONSTRAINT Conservative-Anchor Gate Integrity at line 272)
- Co-located with `canonicalize_execution_config_path()` (at `:96`) + `LineageContext` (at `:206`) per CONTRACT BOUNDARY SSOT discipline (all three live in `artifact_schema.py` for atomic-maintenance)

**`canonicalize_execution_config_path(path: Path | str, *, repo_root: Path | None = None) -> str`** at `artifact_schema.py:96-198`:
- Repo root resolution via `Path(__file__).resolve().parent.parent` per `experiment_registry.py:45` `PROJECT_ROOT` precedent
- Resolves relative paths against repo root BEFORE `os.path.realpath` (per Codex Fv5-1 + Codex v1 N1 catch — `os.path.abspath(relative_path)` anchors to CWD which is bug-prone)
- `commonpath`-based containment + POSIX repo-relative + case-sensitive exact match (per plan v5 Contract 2.0.4 inline-fix Fv5-1)

**Live DB migration fired at T1.3 SEAL**: `cost_anchor_id` column was MISSING from live `experiments.db` (`.schema runs` query at T1.3 verification) while source declared it in `MIGRATION_COLUMNS` at `experiment_registry.py:121` (entry for `cost_anchor_id` at line 147 within the per-row schema list). Lazy-trigger via existing `create_table()` function at `experiment_registry.py:193` (invoked from `_write_to_registry` at `engine.py:839` via internal registry-write paths) fired the SQL `ALTER TABLE` migration on first registry write; no NEW migration code required; idempotent append-only convention preserved.

**Triple-resolution registry-integrity test suite** at T1.5 `test_t1_5_registry_integrity.py` (7 methods):
- 5 failure cases at lines 331/387/449/481/552: `test_failure_1_duplicate_run_id` + `test_failure_2_missing_hypothesis_hash` + `test_failure_3_missing_batch_id` + `test_failure_4_cost_anchor_id_tamper_via_setattr` + `test_failure_5_unmapped_path_via_lineage_context_construction`
- 1 case-mismatch macOS APFS edge case (case-insensitive APFS filesystem can return non-canonical path casing; `canonicalize_execution_config_path` requires case-sensitive exact match to defeat APFS-induced cost_anchor_id resolution divergence)
- 2 xfail DS8 PENDING (strict-vs-conditional rejection scope per anti-pre-emption + sub-plan §3.2 failure handling; both `strict=True`)

---

## §9 Lineage context propagation verification (4 entry points)

**Sealed at**: T1.3 SEAL bundle `12dffde` (LineageContext canonical + threading through entry points); T1.1 SEAL bundle `12dffde` (SYS4 + SYS5 invariant-level closure).

**`LineageContext` canonical site**: `backtest/artifact_schema.py:206` (frozen dataclass + kw_only=True). **14 dataclass fields = 13 Contract 2.0.5 header fields (excluding `artifact_schema_version` per D2-b accepted design asymmetry) + T_obs (required-adjacent 15th field outside header table per Schema spec §1.5b)**. Verified by `len(dataclasses.fields(LineageContext)) == 14` invariant test.

**Public shim re-export via `backtest/wf_lineage.py:554-563`**: `LineageContext` + `canonicalize_execution_config_path` + `check_b_c_extended_semantics_or_raise` + per-domain `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` tuple all re-exported per CONTRACT BOUNDARY heavy-private-impl architecture (heavy logic in `artifact_schema.py`; public API surface via `wf_lineage.py`).

**4 entry-point threading verification** (Mode A verified at cycle SEAL drafting time post-T1.6 SEAL; threading model diverged from parent plan v5 T1.3-D-i anticipated lock at T1.1 implementation per slice-aware-boundary discipline):

The threading is asymmetric across the 4 entry points — 2 entry points accept `LineageContext` as opt-in kwarg; 2 entry points retain `execution_config_path` scalar; consumption converges at `_write_to_registry()`:

1. **`run_backtest()` at `backtest/engine.py:657`** — accepts `lineage_context: "Any | None" = None` kwarg at `:667` (T1.3 + T1.1 expansion); LineageContext is opt-in for new Phase B / Tier 5 / Tier 6 callers; legacy callers retain `execution_config_path` scalar at `:666` (already had per Phase 4)
2. **`run_regime_holdout()` at `backtest/engine.py:2270`** — accepts `lineage_context: "Any | None" = None` kwarg at `:2290` (T1.3 + T1.1 expansion); same opt-in semantics; orchestrator-internal only per CLAUDE.md no-CLI rule
3. **`run_walk_forward()` at `backtest/engine.py:1617`** — does NOT accept `lineage_context` kwarg; retains `execution_config_path: Path | None = None` scalar (deliberate — T1.1 slice-aware-boundary discipline; inner `run_backtest()` call at `:1788` explicitly passes `lineage_context=None` to opt out, consistent with [`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`](../decisions/WF_TEST_BOUNDARY_SEMANTICS.md) Decision Section RS: "No position, no equity, no decision/accounting state from train carries into test")
4. **Evaluation-gate driver `scripts/run_phase2c_evaluation_gate.py`** — does NOT use `LineageContext`; retains `execution_config_path: Path | None = None` scalar at `:487`; passes scalar to engine functions at `:517` (current B-C-extended cycle ships infrastructure-only; LineageContext-to-evaluation-gate threading deferred to B-C-narrow successor cycle per Path α invariant)

**Consumption boundary**: `_write_to_registry()` at `backtest/engine.py:839` accepts `lineage_context: "Any | None" = None` kwarg at `:863` and propagates the LineageContext fields into registry rows. **T1.3-C HYBRID-style scalar-vs-LC conflict-check pattern at write boundary applied across 5 field dimensions, all FAIL CLOSED on disagreement**: parent_run_id (`:1040` T1.3-C) + run_id (`:1061` SYS-fix-1 B2 + FIX-T1.1-SYS2-H2) + hypothesis_hash (`:1084` SYS-fix-1 B2 + FIX-T1.1-SYS2-H2) + batch_id (`:1105`) + execution_config_path (`:1125` FIX-H1 T1.3-C-parallel).

**T1.1 9-iteration arc + SYS4/SYS5 invariant-level closure** (cycle-final convergent APPROVE at v9 with Codex explicit "cycle-final APPROVE; no v10 finding predicted"):

**5 asymmetry classes empirically discovered** (per parent plan §11 canonical T1.1 SEAL entry; iteration markers v1-v9 do NOT one-to-one map to asymmetry classes — v3/v4/v5 are progressive refinements within the same class; v8 is the 5th class proper):
- Class 1 (v1): T_obs finite-return + WF domain fence
- Class 2 (v2): Registry persistence gap + atomicity
- Class 3 (v3 F-systematic): 3 third-level asymmetries — engine_commit OVERRIDE + T_obs=None bypass + B6 artifact_dir skip
- Class 4 (v4 SYS2 + v5 SYS3-narrow as progressive refinements): OR-vs-AND pair-completeness + mutated T_obs write-boundary, then `(None, "")` third-state at LATE_FILL pair
- Class 5 (v8 final-round adversarial): direct STRICT field tamper via `object.__setattr__` bypassing frozen-dataclass guard + registry nullable TEXT silently accepting

**Iteration arc through closure**:
- v6-v7 (SYS4-hybrid): closed LATE_FILL pair via `__post_init__` invariant on ONE field group; produced first convergent APPROVE; **pattern continued at v8** with different field group at SAME producer-consumer boundary class (Class 5)
- v9 (SYS5): **centralized `LineageContext.revalidate_for_write()` at `artifact_schema.py:462-553`** covering ALL 14 Contract 2.0.5 fields; called from `backtest/engine.py:1149`; DESIGN INVARIANT marker replacing prior CONTRACT GAP at `engine.py:1133-1148`; **all 5 classes structurally closed at producer layer — cycle-final convergent APPROVE**

**§35-adjacent observation evidence base** (2-cycle empirical foundation; codification deferred to §35 codification cycle component per anti-pre-emption — see §12): producer-side invariant-level closure (`revalidate_for_write()`) is structural pattern-breaker over case-by-case enumeration of named cases (which spawned next-narrowest asymmetry at each iteration). 4 write-boundary mirror sites following the DESIGN INVARIANT marker at `engine.py:1133-1148` (covering cost_anchor_id + parent_run_id + T_obs SYS3-B2 + LATE_FILL SYS3-B1 field classes) RETAINED as belt-and-suspenders per project defense-in-depth doctrine. Cycle-pattern observation captured at [`feedback_invariant_level_vs_enumeration.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_invariant_level_vs_enumeration.md).

---

## §10 Consumer enumeration results (T1.6 (g))

**Canonical document**: [`docs/decisions/B_C_EXTENDED_V1_CONSUMER_ENUMERATION.md`](../decisions/B_C_EXTENDED_V1_CONSUMER_ENUMERATION.md) (684 lines; sealed at T1.6 SEAL `ec647dc`).

**Enumeration outcome (212 total rows; classified via γ Hybrid orchestrator-skeleton + general-purpose opus subagent dispatch per Charlie register 2026-05-24)**:

| Classification | Count | Definition |
|---|---|---|
| **HANDLES** | **181** | Consumer site already correctly handles `b_c_extended_v1` artifacts via existing dispatcher logic OR by being domain-fenced to WF/EVALUATION-only via `ACCEPTED_*_SCHEMA_VERSIONS` per-domain tuple |
| **NO-OP** | **31** | Consumer site does not interact with `b_c_extended_v1` artifacts (orthogonal domain; e.g. cost-model utility helpers; legacy artifact readers not touching B-C-extended schema) |
| **NEEDS-EXTENSION** | **0** | Consumer site WOULD require extension to handle `b_c_extended_v1` artifacts at production time (zero rows flagged at consumer-enumeration phase — anti-pre-emption preserved per T1.6 (g) §2.7.4 PASS criterion 6 "NEEDS-EXTENSION rows firmly DEFERRED to successor cycle") |

**0 Mode A flags on γ Hybrid opus subagent dispatch** (T1.6 §10 task SEAL chain entry): subagent (opus model per Charlie register; general-purpose subagent_type) returned 212 classifications with 0 unverified specific-claims; orchestrator independent verification on classification methodology + sample row spot-checks confirmed 0 hallucinations.

**Successor-cycle eligibility from consumer enumeration**: 0 successor cycles flagged at consumer-enumeration phase per anti-pre-emption (NEEDS-EXTENSION count = 0). Any future NEEDS-EXTENSION emergence at B-C-narrow successor cycle (or later cycles) will trigger separate Charlie register-event boundary; not pre-bound at this cycle SEAL.

---

## §11 Orchestrator-adjudication-error pattern recurrence summary

**Pattern** (per parent plan §8 (Risk disclosure → Process risks subsection)): orchestrator misadjudicates a reviewer finding when the finding is substantively correct + actionable. Empirically structural at ~75% per-iteration rate absent cross-leg verification.

**3 confirmed instances within B-C-extended cycle planning arc** (per parent plan §8 short-marker enumeration; substantive content per planning arc deliberation history at parent plan v1-v5 PFR rounds — not re-narrated here per anti-pre-emption + canonical artifact precision):

| # | Marker | Cycle phase | Caught by |
|---|---|---|---|
| 1 | v1 "5.5" | Planning arc (v1 → v2 PFR adjudication boundary) | v2 PFR Mode A Layer-3 cross-leg verification |
| 2 | v3 "fisher=True 2.5" | Planning arc (v3 → v4 PFR adjudication boundary) | v4 PFR Mode A Layer-3 cross-leg verification |
| 3 | v4 "12 fields" | Planning arc (v4 → v5 PFR adjudication boundary) | v5 PFR Mode A Layer-3 cross-leg verification |

Per parent plan §8: v5 process discipline (empirical pre-verification + cross-referenced field counts + inlined mapping table) attempted to break the pattern; v5 PFR returned 0 BLOCKING confirming the discipline was effective at the planning-arc gate. Codification of the finding-class is eligible-not-named at a separate successor cycle per §12 (NOT bound at this cycle SEAL). The v_impl_polish-iteration analog finding-class (recursive own-finding-anchoring at patch review during the T1.6 SEAL cycle) is a distinct pattern class codified separately at §12 §35 codification candidate #4.

---

## §12 Eligible-not-named successors NOT bound

**Anti-pre-emption preservation**: each item below is eligible-not-named at separate Charlie register-event boundary per anti-pre-emption discipline. No item is bound or scheduled at this cycle SEAL ratify.

**Bundle component successor cycles** (B-C-extended cycle SEAL bundle has 5 separate register-event components per Charlie pre-authorization 2026-05-23):
- **§35 codification cycle component** — METHODOLOGY_NOTES.md addition codifying 7+ §35 candidates queued from this cycle (candidate names enumerated below). Reviewer round + adjudication discipline per B2 standing rule LOCKED 2026-05-19 SEAL-class artifact scope.
- **Memory codification batch component** — `~/.claude/projects/.../memory/` files codifying T1.6 SEAL cycle empirical (batch (b) outstanding + new T1.6 SEAL cycle items).
- **Phase Marker advance component** — CLAUDE.md Phase Marker update + atomic `docs/phase_marker_history.md` update per [`feedback_claude_md_freshness.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md) Option 1A binding (18th cumulative trigger empirical).
- **3 LOW residual cleanup component** — 3 mechanical line-cite-shift corrections (L1 + L2 + L3) carried forward from T1.6 PFR Round 6 FINAL ROUND; substantive content of each correction is deferred to the cleanup register-event.

**§35 codification candidates** (NAME-only enumeration per Charlie register Q2 NAME-only authorization; content of each codification deferred to §35 codification cycle component):
1. Atomic single-pass remap discipline
2. Mode A applies to root-cause diagnoses
3. Bulk-fix tooling Layer 3 propagation
4. Recursive own-finding-anchoring at v_impl_polish patches
5. Historical-ledger preservation vs all-current discipline
6. Multi-site Edit operations must be grep-verified post-Edit
7. FINAL ROUND framing operationalizes cycle saturation criterion
8. T_obs header-field-table framing inheritance gap (per T1.6 sub-plan §9.8 + parent plan v5 §2.0.5 inheritance chain)
9. Data-preservation as pre-commit audit criterion at artifact-design boundary, not consumption boundary (per R6.1 V_SEAL §10.2 originating + this cycle's substantive driver)
10. Anti-recurrence requires invariant-level constraints, not enumeration of named cases (per T1.1 9-iteration arc + T1.5 SEAL-eve cycle; T1.6 sub-plan §9.8 line 812)
11. Heavy-private-impl extraction must be accompanied by canonical-site CONTRACT GAP enumeration; do NOT default to wf_lineage.py GAPs alone after extraction (per v2 PFR Advisor F3 fix-substantive-leak empirical; T1.6 sub-plan §9.8 line 815)

**Memory codification batch items** (NAME-only enumeration; content deferred to memory batch component):
- γ Hybrid + M1 N=4 task-class subdivision empirical
- Upstream propagation chain pattern at 4-instance scale
- Edit-call modality leak pattern at spelled-out variants
- T_obs header-field-table framing inheritance gap
- Cycle saturation criterion sub-rule extension
- Recursive own-finding-anchoring at v_impl_polish (6-iteration empirical)

**External successor cycles eligible-not-named at separate Charlie register-event boundary**:
- **B-C-narrow data-recovery successor cycle** (binding condition at R6.1 V_SEAL §10): engine re-run reproducing `phase4_forward_2026_15bps_v1` with per-bar return series preservation + per-candidate γ3/γ4 moments + registry linkage; bounded scope per binding condition; no timing estimate per R6.1 V_SEAL B-Timing
- **Post-V_SEAL Tier 6 evaluation application** (R6.1 Path α invariant): R6.1 methodology applied to candidate cohort using B-C-narrow recovered data
- **R6.1-A/B/C codification cycle** (per R6.1 V_SEAL §10.2): finding-class memory codification for orchestrator-adjudication-error pattern + BL-Y Phase 1 fresh-dispatch leak pattern + path-lock-incomplete-document-propagation pattern
- **R5.2 framework family reopening cycle** (per R5.2 §2.3 + R6.1 Path X register #1d): eligible to reopen R5.2 SD-A-α framework family lock at separate Charlie register-event
- **DS-NEW (e)** production-data-anomaly engine→writer smoke (per T1.5 sub-plan §8.2)
- **DS-NEW (f)** T1.5-followup smoke artifact-writer + schema-validator chain coverage (per T1.5 §8.2 — HIGH-1 partial-closure successor scope)
- **DS-NEW (NEEDS-EXTENSION)** per T1.6 sub-plan §8.2 (eligible if future consumer-enumeration phases flag NEEDS-EXTENSION rows; currently 0 per §10)
- **R2.2 Monday-pattern mechanism investigation** + **P2a DSL recovery** + **R3.1b/c** + **supplementary IS-OOS analytical cycle per R5.1 §1.5 Path 1+** + **Phase 4 paper-trading deployment** + **mechanism investigation for FLIP-TRIGGERED candidates** + **Bonferroni eligibility re-evaluation** + **advisor /agents-UI refresh** + **Tier-0 pause** + **Phase 2.5 bandit-dedup (parked)** + **pre-existing noise cleanup** + **advisor opus model effects pilot extended observation** + **project pause / strategic-absorption** + other Charlie-specifiable — all eligible at separate Charlie register-event boundary per anti-pre-emption + R6.1 V_SEAL successor frame.

---

## §13 V_SEAL closure section — PENDING at register-event boundary

### §13.1 V_SEAL register-event boundary verbatim

**Charlie register**: "(α') Inline fix + ratify" 2026-05-25 — authorized cycle SEAL ratify after v6 SEAL-eve Round 3 returned APPROVE-WITH-FINDINGS at LOW-only floor from both reviewer legs (Codex + Advisor). 4 LOW fixes (2 CONVERGED + 2 UNIQUE) applied inline at v7 per Path α' before SEAL ratify commit. Cycle SEAL ratify is component 1 of 5 in the B-C-extended cycle SEAL bundle (components 2-5 = §35 codification + memory codification batch + Phase Marker advance + 3 LOW residual cleanup; each separate Charlie register-event per anti-pre-emption).

### §13.2 Charlie register chain summary

**11 primary register-events through cycle SEAL** (per §0 register chain table); ~90+ reviewer dispatches cumulative across all T1.x sub-cycles + implementation + SEAL-eve rounds (per §4 subtotal arithmetic ~28 + ~22 + 16 + ~32 = ~98 floor).

**Charlie register chain summary cross-reference**: full chain at parent plan v5 §11 (T1.2 + T1.3 + T1.1 SEALs) + T1.4 sub-plan §10 (T1.4 cycle ledger) + T1.5 sub-plan §10 (T1.5 cycle ledger) + T1.6 sub-plan §10 ledger through #N12 PENDING at sub-plan-ratify-time + T1.6 SEAL commit `ec647dc` message body for #N13 PFR Round 6 FINAL convergence + §11 addendum at sub-plan EOF.

### §13.3 Locked engineering specification (cycle SEAL substantive content)

**Authoritative substantive content of B-C-extended Scope-B cycle SEAL**:
- Contract locks 2.0.1-2.0.6 (§2 above)
- Engineering deliverables T1.1-T1.6 (§3 above)
- Validation results (§4 above)
- Schema spec documentation (§5 above; canonical at `docs/decisions/B_C_EXTENDED_V1_SCHEMA_SPEC.md`)
- γ4 convention specification (§6 above; canonical at T1.5 `test_t1_5_fixture_moments.py`)
- Backward compatibility verification (§7 above; canonical at T1.4 SEAL `5a44ec6` + `tests/test_t1_4_backward_compat.py`)
- cost_anchor_id mapping + canonicalization + registry linkage (§8 above; canonical at `backtest/artifact_schema.py:76` + `:96` + `experiment_registry.py:121`)
- Lineage context propagation (§9 above; canonical at `backtest/artifact_schema.py:206` + `backtest/wf_lineage.py:554-563` shim re-export)
- Consumer enumeration (§10 above; canonical at `docs/decisions/B_C_EXTENDED_V1_CONSUMER_ENUMERATION.md`)

### §13.4 Cycle SEAL bundle commit + downstream component register-event dependencies

This cycle SEAL artifact is component 1 of 5 in the B-C-extended cycle SEAL bundle (per Charlie pre-authorization 2026-05-23). Components 2-5 (§35 codification + memory codification batch + Phase Marker advance + 3 LOW cleanup) each require separate Charlie register-event per anti-pre-emption — they are NOT shipped at this cycle SEAL ratify commit.

**Atomic commit binding** (`feedback_claude_md_freshness.md` Option 1A): the Phase Marker advance component (when ratified at separate register-event) must atomically stage both `CLAUDE.md` AND `docs/phase_marker_history.md` per Option 1A binding (18th cumulative empirical trigger).

### §13.5 Artifact signature

**Path**: `docs/phase5/B_C_EXTENDED_SCOPE_B_NOTE.md`
**Cycle**: B-C-extended Scope-B structural artifact-preservation refactor
**Total lines**: 362 (within parent plan v5 §7 350-550 target band)
**Sealed by**: Charlie register "(α') Inline fix + ratify" 2026-05-25
**Cycle entry**: 2026-05-22 (parent plan v5 RATIFY register-event)
**Cycle SEAL ratify**: 2026-05-25
**Adversarial round count**: 7 reviewer rounds = 4 PFR-rule-Y (v1+v2+v3+v6) + 3 SEAL-eve (v4 Advisor + v5 Codex + v6 2-leg Round 3)
**Cumulative reviewer dispatches**: ~90+ floor across cycle
**ADOPT fix count**: ~40 across all rounds
**Cycle saturation reached**: v6 SEAL-eve Round 3 returned APPROVE-WITH-FINDINGS at LOW-only floor from both legs
**Rule 2 SEAL-eve VINDICATED at 4-cycle scale**: T1.5 v1+v2 HIGH + T1.6 sub-plan Round 1 MEDIUM + v4 SEAL-eve MEDIUM + v5 SEAL-eve MEDIUM

---

**End of SEAL artifact.**
