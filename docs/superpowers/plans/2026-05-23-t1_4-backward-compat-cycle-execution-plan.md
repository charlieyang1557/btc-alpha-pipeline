# T1.4 Backward-Compatibility Verification Cycle Execution Plan (v6 — RATIFIED 2026-05-23)

**Status:** v6 RATIFIED 2026-05-23 per Charlie register "ratify" + §2.2 (i) git-plumbing LOCK. All §8.1 named sub-decisions resolved (empirical locks at HEAD applied). Next register-event boundary: T1.4 implementation start.
**Cycle entry:** R3a-bounded; Charlie register β authorized 2026-05-23 ("Plan-v5-§2.4 + handoff item-4 3 sub-bullets")
**Iteration:** v1 → v2 → v3 → v4 → v5 → v6 (revision logs at §11 v1→v2→v3; §12 v3→v4; §13 v4→v5; §14 v5→v6)
**v6 trigger:** Charlie register 2026-05-23 "Path A (apply 3 mechanical fixes inline; skip v6 PFR re-review per PFR-rule-Y SKIP criterion + both-legs no-v6-finding-predicted cycle-final convergence)"
**Ratify register:** Charlie 2026-05-23 "ratify" + §2.2 lock register "(i) git-plumbing"
**Parent plan:** [`docs/superpowers/plans/2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md`](2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md) v5 RATIFIED
**Parent cycle precedents:** T1.2 SEAL + T1.3 SEAL + T1.1 SEAL bundled at commit `12dffde` (pushed origin/main 2026-05-23); pre-T1.x parent `7c8f4a7` (R6.1 V_SEAL)
**Default posture:** non-execution awaiting Charlie register at each register-event boundary

---

## §1 Cycle scope statement + β-scope register provenance

T1.4 is the backward-compatibility verification task within the B-C-extended Scope-B structural artifact-preservation refactor cycle. It does NOT implement new artifact-writer behavior (T1.1 SEALED), new schema (T1.2 SEALED), or new registry/API (T1.3 SEALED). T1.4's sole purpose is to **verify that the T1.1/T1.2/T1.3 SEALED changes preserve backward compatibility on existing legacy artifacts + signatures + flows**.

### §1.1 β-scope decomposition (Charlie register β 2026-05-23)

**β-scope = plan v5 §2.4 5 deliverables UNION handoff item-4 3 backward-compat sub-bullets** within R3a-bounded register. Scope expansion beyond β requires fresh Charlie register-event.

**Deliverable A — plan v5 §2.4 (5 items):**

| A# | Deliverable | Source spec |
|---|---|---|
| A1 | Test case (i): legacy `phase4_forward_2026_15bps_v1/<hash>/holdout_summary.json` validates under existing `wf_lineage.check_evaluation_semantics_or_raise()` without modification | plan v5 §2.4 line 274 |
| A2 | Test case (ii): NEW `check_b_c_extended_semantics_or_raise()` validator's domain-fence correctly rejects legacy artifact (per Charlie A2-α LOCKED 2026-05-23; structural Phase 1 fail-fast with `ValueError` per Charlie F1 ADOPT 2026-05-23; see §2.3) | plan v5 §2.4 line 275 |
| A3 | Aggregate `holdout_results.csv` byte-identical before/after T1.x SEAL (MANDATORY) | plan v5 §2.4 line 277 + Codex v4 Fv4-5 LOW |
| A4 | Aggregate `holdout_summary.json` byte-identical before/after T1.x SEAL (MANDATORY; NOT conditional) | plan v5 §2.4 line 278 + Codex v4 Fv4-5 LOW |
| A5 | ALL N per-candidate `holdout_summary.json` byte-identical before/after (N empirically verified = 39 at sub-plan drafting; verify N matches at test execution per Advisor v4 F-v4-3 LOW) | plan v5 §2.4 line 279 + Advisor v4 F-v4-3 LOW |

**Deliverable B — handoff item-4 (3 sub-bullets):**

| B# | Deliverable | Source spec |
|---|---|---|
| B1 | Confirm no production callers depend on pre-T1.1 `_write_to_registry()` signature (AST-based call-site classifier across SCOPED dirs only — `backtest/`, `tests/`, `scripts/` — with explicit `.claude/`, `.git/`, venv exclusions; classify every `keyword(arg=None, value=...)` as `**kwargs` expansion needing manual review; lock empirical 4-tuple at sub-plan ratify; see §2.4) | handoff item-4 sub-bullet 1 |
| B2 | Verify `run_data` backward-compat for runs WITHOUT `LineageContext` — 4 scenarios per Contract 2.0.4 fail-closed clause (B2.a default normalization → 8 NULL + cost_anchor_id resolved; B2.b explicit mapped path → 8 NULL + cost_anchor_id resolved; B2.c un-mapped in-repo path → fail-closed mapping-lookup; B2.d outside-repo path → fail-closed path-containment; see §2.5) | handoff item-4 sub-bullet 2 |
| B3 | Verify SYS5 `LineageContext.revalidate_for_write()` at [`backtest/artifact_schema.py:449`](../../backtest/artifact_schema.py#L449) does NOT block legitimate flows across all 4 entry points (run_backtest + run_regime_holdout — LC-positive scenarios; run_walk_forward + evaluation-gate driver — γ-1 opt-out-verification scenarios per Charlie γ-1 LOCKED 2026-05-23; see §2.6) | handoff item-4 sub-bullet 3 |

### §1.2 Validation call coverage (A6, implicit in plan v5 §2.4 line 280)

`check_evaluation_semantics_or_raise()` invoked on aggregate `holdout_summary.json` + all 39 per-candidate `holdout_summary.json` files (40 total invocations). Pass criterion: zero raises on legacy artifacts.

---

## §2 Engineering deliverables (task decomposition; execution order)

### §2.1 New test module

**New file:** `tests/test_t1_4_backward_compat.py`

**Module structure (7 test classes):**
- `TestT1_4_A1_A6_LegacyEvaluationValidation` — A1 + A6 (40 `check_evaluation_semantics_or_raise()` invocations)
- `TestT1_4_A2_DomainFenceRejection` — A2 per A2-α LOCKED + F1 ValueError ADOPT
- `TestT1_4_A3_A4_A5_HashByteIdentity` — A3 + A4 + A5 (41 hash comparisons)
- `TestT1_4_B1_SignatureBackwardCompat` — B1 (AST-based call-site classifier; scoped)
- `TestT1_4_B2_LegacyDefaultNormalization` — B2.a + B2.b + B2.c + B2.d (4 scenarios per Contract 2.0.4)
- `TestT1_4_B3_LegitimateFlowsAndOptOutSemantic` — B3.1 + B3.2 (LC-positive) + B3.3 + B3.4 (γ-1 opt-out-verification)
- `TestT1_4_DBMigrationIdempotency` — additional risk-mitigation per F10 (see §2.7)

### §2.2 Hash-fixture approach (NAMED sub-decision; precondition empirically verified)

**Approach (NAMED sub-decision; lock at sub-plan ratify):** Hash-before/after verification requires "before" hashes. Three approaches:

| Approach | Description | Tradeoff |
|---|---|---|
| **(i) Pre-snapshot via git-plumbing** | Use `git show 7c8f4a7:<path>` (= `12dffde^`; empirically verified at v3 drafting) to extract pre-T1.x file content + SHA256-compute "before" hashes at test runtime | Authoritative; ties hash provenance to git; reproducible. Requires git plumbing in tests |
| **(ii) Empirical re-run** | Re-run the Phase 4 pipeline pre-T1.x to regenerate baseline artifacts + hash | Expensive; risk of nondeterminism between runs |
| **(iii) Inline-asserted hashes** | Hard-code expected SHA256 hashes in test fixtures (computed once at sub-plan ratify time from current on-disk files at commit `12dffde` post-T1.x); precondition guarantees pre-T1.x = current-on-disk | Cheapest at test runtime; locks hashes at ratify-time |

**Precondition empirically verified at v2/v3 drafting (2026-05-23):**

```
$ git diff 7c8f4a7..12dffde --stat -- data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/
(empty — no files changed)
```

Verified: legacy phase4 artifacts are byte-identical between pre-T1.x parent (`7c8f4a7`) and T1.x SEAL (`12dffde`). T1.x bundle did NOT mutate phase4 artifacts. **Approach (iii) is therefore equivalent to approach (i)** modulo hash-computation cost.

**~~Pre-commit decision required~~ RESOLVED 2026-05-23 per Charlie ratify register §2.2 lock: (i) git-plumbing LOCKED.** Test implementation will use `subprocess.run(["git", "show", "7c8f4a7:<path>"], capture_output=True, check=True)` at test runtime + SHA256-compute "before" hashes; compare against current on-disk SHA256 for byte-identity verification. Git availability assumed (CI invariant). Provenance ties hashes to git commit `7c8f4a7` (pre-T1.x parent of `12dffde`).

### §2.3 A2-α LOCKED specification (Charlie A2-α 2026-05-23 + F1 ValueError ADOPT 2026-05-23)

**Behavior under A2-α + F1 LOCKED:**
- Test invokes `check_b_c_extended_semantics_or_raise()` (T1.2-sealed; defined at [`backtest/artifact_schema.py:654`](../../backtest/artifact_schema.py#L654); re-exported via [`backtest/wf_lineage.py:544`](../../backtest/wf_lineage.py#L544) for consumer backward-compat) on legacy artifact
- Legacy artifact: any per-candidate `holdout_summary.json` from `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/<hash>/` (39 candidates available; verify `artifact_schema_version` value present + not in `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` at fixture-load time; empirically one such value is `"phase2c_7_1"` per Codex F1 evidence)
- **Expected exception type: `ValueError`** (NOT `BCExtendedSchemaValidationError`; per Codex F1 v2 PFR catch — domain-fence is Phase 1 structural fail-fast which raises plain `ValueError` at [`backtest/artifact_schema.py:740`](../../backtest/artifact_schema.py#L740); `BCExtendedSchemaValidationError` is the subclass for Phase 2 accumulated per-field errors at [`backtest/artifact_schema.py:850`](../../backtest/artifact_schema.py#L850); subclass relationship per plan v5 §10 B3-b preserves LSP for `except ValueError` consumers but A2's specific assertion is the parent class)
- Failure semantic: structural-first per T1.2 B1-c hybrid validation order — `artifact_schema_version` domain-fence check fires first before per-field validation

**Pre-committed message-content keywords (per Codex F3 explicit message-spec recommendation + Advisor F-NEW-3 keyword precision; tautology-safe per Advisor F11):**

| Keyword class | Required substring | Rationale |
|---|---|---|
| Discriminator field name | `artifact_schema_version` | Names the field that failed domain-fence (corrected from v2 `schema_version` per Advisor F-NEW-3 + Codex F1 evidence at artifact_schema.py:738-746) |
| Schema-version value enumeration | `b_c_extended_v1` | The actual accepted-set value present in error message via `accepted_str` enumeration; literal `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` NOT present in message per Codex F1 / Advisor F-NEW-3 empirical evidence |
| Schema-version actual value | Actual artifact's `artifact_schema_version` value (e.g., `phase2c_7_1` for current legacy artifacts; verify at fixture-load time) | Tells caller which value was rejected (via `!r` interpolation at artifact_schema.py:741) |

**Tautology guard:** keyword classes pre-committed at sub-plan ratify against the spec (not derived from current implementation). Test asserts implementation conforms to spec — if implementation changes message, test catches divergence.

**A2-α excludes (in-scope only domain-fence behavior, NOT per-bar content validation):**
- Per-bar artifact validation (file-exists + path-confinement + SHA256-recompute + T_obs-alignment) is in `check_b_c_extended_semantics_or_raise()` scope per Contract 2.0.5 but is NOT exercised by A2 — domain-fence Phase 1 fail-fast fires first; legacy artifact lacks per-bar fields entirely
- T1.5 fixture/smoke/canary suite covers per-bar content validation paths (deferred per execution order)

### §2.4 B1 AST-based call-site classifier (revised per Codex F2 v2 PFR)

**Classifier specification:**

**Phase 1 — scoped enumeration (per Codex F2 worktree-contamination catch):**
```bash
# SCOPED to canonical source dirs only — excludes .claude/, .git/, venvs, etc.
grep -rn "_write_to_registry" \
    --include="*.py" --include="*.sh" \
    backtest/ tests/ scripts/
```

Explicit excluded paths:
- `.claude/` (worktrees + hooks + agents)
- `.git/`
- `venv/`, `.venv/`, `__pycache__/`, `.pytest_cache/`
- `docs/` (documentation refs are not code call sites)
- `data/` (data refs are not call sites)

**Phase 2 — AST-based classification (per Python `ast` module):**
```python
# For each enumerated .py file:
#   parse via ast.parse(); walk Call nodes; for each Call where
#   func.attr == "_write_to_registry" or func.id == "_write_to_registry":
#
#   For each keyword arg in call.keywords:
#     if keyword.arg is not None:
#       # Named kwarg: record kwarg_names_set
#     else:
#       # keyword.arg is None means **kwargs unpacking syntax (per Python ast)
#       # ALWAYS classify as dynamic_count += 1; require manual review
#       # (static inference of helper-returned dict is NOT attempted per
#       # Codex F2 — even when traceable, fragile across refactor)
#
#   For positional args: record positional_arg_count
#
# Output per file: list of (line, positional_count, named_kwargs_set, has_dynamic_kwargs)
```

**Phase 3 — separate counts:**
```
prod_count = sum from backtest/*.py
test_count = sum from tests/*.py
scripts_count = sum from scripts/*.py + scripts/*.sh (currently 0 per empirical)
dynamic_count = sum across all files of has_dynamic_kwargs=True calls
```

**Pass criterion (revised per Codex F2):** at sub-plan ratify, lock 4-tuple `(prod_count, test_count, scripts_count, dynamic_count)` to empirically-observed values. Test asserts (a) classifier produces same 4-tuple at execution time; (b) all named-kwarg call sites use scalar `parent_run_id` kwarg + do NOT pass `lineage_context` (legacy path; T1.3-C HYBRID preservation) OR pass `LineageContext` instance (new path); (c) zero call sites rely on positional argument order in a way broken by T1.3-C HYBRID extension; (d) **every dynamic_count call requires explicit orchestrator adjudication entry at sub-plan ratify** — if dynamic_count > 0, each instance is manually classified as backward-compat-safe OR requires escalation (per F2 senior-engineer concern: "manual review" insufficient without explicit Charlie adjudication entry).

**Scope-bounding clarification (per Advisor F4 v3 PFR ADOPT):** the dynamic_count adjudication entry is **locked at T1.4 sub-plan ratify only** (one-time empirical lock at T1.4 cycle boundary). Future post-T1.4-SEAL engineering that introduces new `**kwargs` callers to `_write_to_registry()` is governed by §35 codification (eligible-not-named per anti-pre-emption); the T1.4 ratify-time dynamic_count adjudication does NOT create a permanent gating mechanism for future engineering.

**Failure mode handling:** if any caller has unmigrated positional dependency that breaks, classify as defect requiring T1.3 corrective register-event (NOT T1.4 in-scope fix).

**Empirical baseline at v3 drafting (2026-05-23) — SCOPED grep:** 55 total `_write_to_registry(` text occurrences across 6 files: `tests/test_t1_1_sys_fix.py:24` + `tests/test_t1_3_registry_api.py:20` + `tests/test_t1_1_artifact_writer.py:2` + `backtest/engine.py:5` + `backtest/artifact_schema.py:3` + `backtest/experiment_registry.py:1`. AST Phase 2 + Phase 3 classification at ratify-time may yield different 4-tuple per dynamic-kwargs identification. (Worktree-contaminated count if `.claude/worktrees/` included would be substantially higher per Codex F2; scoped grep avoids this contamination.)

### §2.5 B2 default-normalization coverage (revised per Codex F2/F3 + Advisor F5/F6)

**4 scenarios cover Contract 2.0.4 happy paths + BOTH fail-closed branches:**

**B2.a — default normalization happy path** (`lineage_context=None` AND `execution_config_path=None`):
- Invoke `_write_to_registry(lineage_context=None, parent_run_id="<uuid>", execution_config_path=None, ...other-required-args...)` on temp SQLite DB
- Verify resulting row at `experiments.db.runs`:
  - `cost_anchor_id` = `"legacy_perp_inspired_7bps_v0"` (Contract 2.0.4 interpretation (b) LOCKED)
  - 8 columns NULL: `returns_per_bar_path`, `returns_per_bar_sha256`, `T_obs`, `regime_key`, `current_git_sha`, `execution_config_path`, `execution_config_sha256`, `parquet_data_sha256`
- Cross-reference: existing sealed test `test_legacy_caller_no_lineage_context_succeeds` at [`tests/test_t1_3_registry_api.py:508`](../../tests/test_t1_3_registry_api.py#L508) asserts same behavior; B2.a is T1.4 backward-compat re-verification

**B2.b — explicit mapped path happy path** (`lineage_context=None` AND `execution_config_path` set to mapped path):
- Invoke with `execution_config_path="config/execution_phaseb_spot_15bps.yaml"` (or another path in `COST_ANCHOR_ID_MAPPING`)
- Verify `cost_anchor_id` resolves to mapped anchor (e.g., `spot_realistic_15bps_v1`)
- Other 8 columns NULL (same as B2.a)
- Confirms canonicalization + mapping lookup runs correctly without LC

**B2.c — un-mapped in-repo path fail-closed (Contract 2.0.4 mapping-lookup branch):**
- Invoke with `execution_config_path="config/unknown.yaml"` (path INSIDE repo root but NOT in `COST_ANCHOR_ID_MAPPING`)
- Verify raises `ValueError` from [`backtest/engine.py:1201`](../../backtest/engine.py#L1201) with structured message containing:
  - Canonicalized un-mapped path string
  - Full mapping enumeration (`COST_ANCHOR_ID_MAPPING.items()`)
  - Explicit guidance text ("Update R3.1d §5.2 mapping" or "contact human approval")

**B2.d — outside-repo path fail-closed (Contract 2.0.4 path-containment branch; NEW per Codex F3):**
- Invoke with `execution_config_path="/tmp/outside_repo_config.yaml"` (or absolute path outside repo root)
- Verify raises `ValueError` from [`backtest/artifact_schema.py:183-188`](../../backtest/artifact_schema.py#L183) (path-containment check via `commonpath`; reached BEFORE mapping lookup at engine.py:1191 per Codex F3 evidence)
- Expected message containing:
  - Original path string (via `!r` interpolation)
  - Repo root real path
  - Text "outside repo root" or "path-containment violation"
  - Text "Contract 2.0.4 fail-closed clause"

**9 new T1.x columns enumerated by name (per Advisor F4 + Codex F2):**

| # | Column | Era / source | MIGRATION_COLUMNS line | Behavior under B2.a |
|---|---|---|---|---|
| 1 | `cost_anchor_id` | Phase B / R3.1d (T1.3) | [`experiment_registry.py:147`](../../backtest/experiment_registry.py#L147) | populates `legacy_perp_inspired_7bps_v0` |
| 2 | `returns_per_bar_path` | B-C-extended T1.1 FIX-B1 | [`experiment_registry.py:155`](../../backtest/experiment_registry.py#L155) | NULL |
| 3 | `returns_per_bar_sha256` | B-C-extended T1.1 FIX-B1 | [`experiment_registry.py:156`](../../backtest/experiment_registry.py#L156) | NULL |
| 4 | `T_obs` | B-C-extended T1.1 FIX-B1 | [`experiment_registry.py:157`](../../backtest/experiment_registry.py#L157) | NULL |
| 5 | `regime_key` | B-C-extended SYS-fix-1 B3/B4 | [`experiment_registry.py:166`](../../backtest/experiment_registry.py#L166) | NULL |
| 6 | `current_git_sha` | B-C-extended SYS-fix-1 B3/B4 | [`experiment_registry.py:167`](../../backtest/experiment_registry.py#L167) | NULL |
| 7 | `execution_config_path` | B-C-extended SYS-fix-1 B3/B4 | [`experiment_registry.py:168`](../../backtest/experiment_registry.py#L168) | NULL |
| 8 | `execution_config_sha256` | B-C-extended SYS-fix-1 B3/B4 | [`experiment_registry.py:169`](../../backtest/experiment_registry.py#L169) | NULL |
| 9 | `parquet_data_sha256` | B-C-extended SYS-fix-1 B3/B4 | [`experiment_registry.py:170`](../../backtest/experiment_registry.py#L170) | NULL |

**Sub-plan ratify gate:** verify column enumeration at HEAD against current `MIGRATION_COLUMNS` (avoid hardcode drift).

### §2.6 B3 legitimate flows + γ-1 opt-out-verification (Charlie γ-1 LOCKED 2026-05-23 + Codex F4 BLOCKING fix)

**Codex F4 + Advisor F-NEW-1 surfaced** that 2 of 4 entry points planned for B3 LC threading are structurally impossible at HEAD: `run_walk_forward()` has NO `lineage_context` param (engine.py:1617-1628; inner `run_backtest()` call HARDCODED `lineage_context=None` at engine.py:1797 per T1.3-D opt-out comment at engine.py:1784-1787); evaluation-gate driver `_evaluate_one_candidate()` calls `run_regime_holdout()` WITHOUT `lineage_context` arg (scripts/run_phase2c_evaluation_gate.py:480-518).

**Charlie γ-1 LOCK 2026-05-23**: rewrite B3.3 + B3.4 to verify the **OPT-OUT semantic** itself — i.e., test that walk_forward + evaluation-gate flows DO NOT populate the 9 T1.x columns (backward-compat preserved by virtue of LC propagation being structurally absent at these entry points).

**4 scenarios across 4 entry points (2 LC-positive + 2 γ-1 opt-out-verification):**

| # | Entry point | Scenario type | Test specification |
|---|---|---|---|
| B3.1 | `run_backtest()` (primary) | LC-positive | Construct canonical `LineageContext(...)`; thread via `run_backtest(lineage_context=lc, ...)`; verify `_write_to_registry()` returns without raise; persisted row has 9 new columns populated from LC |
| B3.2 | [`run_regime_holdout()` at engine.py:2270](../../backtest/engine.py#L2270) (regime holdout entry; `lineage_context` kwarg at engine.py:2290 per T1.3-D) | LC-positive | Construct canonical LC; thread via `run_regime_holdout(..., lineage_context=lc)`; regime holdout completes; persisted row has 9 new columns populated from LC |
| B3.3 | [`run_walk_forward()` at engine.py:1617](../../backtest/engine.py#L1617) (no LC param; T1.3-D opt-out per inner-call comment at engine.py:1784-1787) | γ-1 opt-out-verification | Invoke `run_walk_forward(strategy_cls, ..., db_path=tmp_db, execution_config_path=path, ...)` without LC threading (no API supports it); verify outer-wrapper-emitted registry rows (`run_type="walk_forward_window"` or `"walk_forward_summary"`) have 9 T1.x columns in state matching Contract 2.0.4 default normalization (cost_anchor_id resolved via execution_config_path; other 8 NULL); empirically verify NO LC-derived metadata leaked into persisted rows |
| B3.4 | Evaluation-gate driver `_evaluate_one_candidate()` at [`scripts/run_phase2c_evaluation_gate.py:480-518`](../../scripts/run_phase2c_evaluation_gate.py#L480) (no LC threaded to underlying `run_regime_holdout()`; per Codex F1 v3 PFR also has no `db_path` parameter) | γ-1 opt-out-verification | **Test isolation mechanism (per Codex F1 v3 PFR ADOPT):** monkeypatch `backtest.experiment_registry.DEFAULT_DB_PATH` to `tmp_db` for the duration of the test invocation (preferred per Codex F1 fix option 2; verified at v4 PFR Axis 1 by Codex: `get_connection(None)` resolves DEFAULT_DB_PATH global at call-time at experiment_registry.py:187); ALTERNATE acceptable mechanism is module-level patch of `scripts.run_phase2c_evaluation_gate.run_regime_holdout` with a `db_path=tmp_db`-injecting shim (test-write-time discretion within these 2 named options per §8.1). Invoke `_evaluate_one_candidate(candidate, head_sha, source_batch_id, run_id, output_dir, regime_key, execution_config_path=path)` without LC threading. **Happy-path gate (per Codex F1):** assert `summary["lifecycle_state"] != "holdout_error"` BEFORE querying registry rows (function catches all exceptions into `holdout_error` per [`scripts/run_phase2c_evaluation_gate.py:525-534`](../../scripts/run_phase2c_evaluation_gate.py#L525) `except Exception:` boundary at line 525; row query without happy-path gate would fail silently). **Row query mechanism (per Codex F1):** query rows by unique `parent_run_id=f"phase2c_eval_gate_{run_id}"` (per evaluation-gate driver convention at [`scripts/run_phase2c_evaluation_gate.py:515`](../../scripts/run_phase2c_evaluation_gate.py#L515)) — not by run_id alone. Verify resulting rows have 9 T1.x columns in state matching Contract 2.0.4 default normalization (cost_anchor_id resolved; other 8 NULL); empirically verify driver behavior matches non-LC-threading expectation. |

**γ-1 pass criterion:** B3.3 + B3.4 demonstrate that the T1.3-D opt-out for walk_forward + evaluation-gate driver does NOT break Contract 2.0.4 backward-compat semantic — walk-forward + evaluation-gate writes still produce well-formed registry rows with the 9 T1.x columns either populated correctly (cost_anchor_id via execution_config_path) or NULL (the 8 LC-derived columns).

**γ-1 test-class limitation acknowledgment (per Advisor F1 v3 PFR ADOPT-LIGHT 2026-05-23):** the B3.3 + B3.4 verification design tests that the opt-out semantic produces Contract-2.0.4-compliant default-normalization output; it does NOT positively assert the source-of-output is the intended structural opt-out (e.g., test would also pass if a future regression silently degraded LC-threading to opt-out behavior). This residual test-class limitation is flagged at §5.2 R8 as eligible-not-named for γ-4 corrective register or future hardening cycle; v4 does NOT add positive AST/grep assertions (per Codex non-convergence on Advisor F1 + Advisor self-discount disclosure; overengineering risk).

**γ-4 escalation eligibility (NOT fired at v3):** if Charlie decides to register T1.3 plan-vs-impl divergence corrective at a future register-event, the corrective scope is separate from T1.4 sub-plan. v3 proceeds with γ-1 as committed; γ-4 escalation is eligible-not-named per anti-pre-emption.

**SYS5 line citation (corrected per Codex F5-v1):** `revalidate_for_write()` adversarial coverage exists at [`tests/test_t1_1_sys_fix.py:2571`](../../tests/test_t1_1_sys_fix.py#L2571) (SYS5 marker comment) + [`tests/test_t1_1_sys_fix.py:2583`](../../tests/test_t1_1_sys_fix.py#L2583) (`TestSys5RevalidateForWriteDirectStrictFields` class). **B3 in T1.4 does NOT re-cover SYS5 adversarial scenarios** (avoid duplication).

### §2.7 DB migration idempotency test (per Advisor F10)

**New test class `TestT1_4_DBMigrationIdempotency`** covers regression class on existing user databases:

- Scenario 1: invoke `create_table()` twice in sequence on same `experiments.db`; verify idempotency (no schema modification on 2nd call; no exception)
- Scenario 2: simulate pre-T1.3 DB state (drop `cost_anchor_id` + 8 T1.1 columns); invoke `create_table()`; verify migration adds missing columns; verify existing rows preserved with NULL on new columns
- Scenario 3: simulate partial-migration state (some new columns present, others missing); invoke `create_table()`; verify remaining columns added; existing rows + columns unchanged

**Migration code reference:** [`backtest/experiment_registry.py:106-110`](../../backtest/experiment_registry.py#L106) documents "one-way and idempotent" intent; T1.4 empirically verifies this contract.

### §2.8 Module integration into existing test suite

**Integration:** new test module added to default pytest discovery path; no changes to existing test modules; full suite count expected to grow from baseline (lock at sub-plan ratify per Advisor F8) to baseline + (T1.4 test count); zero pre-T1.4 regression.

---

## §3 Validation approach + success criteria

### §3.1 Pass criteria (9 mandatory items; revised v4 — Mode A re-verification moved to §7 only per Advisor F3 v3 PFR ADOPT)

1. All 7 test classes in `tests/test_t1_4_backward_compat.py` pass — 7/7 mandatory
2. A1 + A6 → 40 `check_evaluation_semantics_or_raise()` invocations on legacy phase4 artifacts: zero raises
3. A2 → `check_b_c_extended_semantics_or_raise()` on legacy artifact: raises `ValueError` (per F1 ADOPT) with all 3 pre-committed message-keyword classes present (per §2.3)
4. A3 + A4 + A5 → 41 byte-identity hash comparisons: 41/41 PASS
5. B1 → AST-based call-site classifier produces 4-tuple `(prod_count, test_count, scripts_count, dynamic_count)` matching empirical lock at ratify-time; zero positional-dependency breakage; every dynamic_count instance explicitly adjudicated at ratify-gate per §2.4
6. B2 → B2.a + B2.b + B2.c + B2.d all pass per §2.5 (4 scenarios cover both fail-closed branches)
7. B3 → B3.1 + B3.2 LC-positive scenarios pass + B3.3 + B3.4 γ-1 opt-out-verification scenarios pass per §2.6
8. DB migration idempotency → 3 scenarios pass per §2.7
9. Full pytest suite: baseline + T1.4-count pass; zero pre-T1.4 regression (baseline empirically locked at ratify-time via `pytest --collect-only` per Advisor F8)

### §3.2 Failure handling

- Any test class failure → cycle does NOT SEAL until resolved
- Any new defect surfacing in T1.1/T1.3 territory during T1.4 execution → classify as defect; raise to Charlie; require fresh register-event (NOT in-T1.4 corrective fix)
- No tolerance relaxation without fresh Charlie register-event

---

## §4 Explicit exclusions (anti-pre-emption discipline)

NOT in scope at T1.4:

- T1.5 fixture/smoke/canary suite (deferred per execution order)
- T1.6 documentation + consumer enumeration grep (deferred per execution order)
- Hypothesis library dependency decision (scoped to T1.5 per plan v5 §10 + handoff)
- F1-Advisor-v1 cosmetic T_obs error message (eligible to fold into T1.6 documentation per handoff)
- §35 codification (deferred to B-C-extended cycle SEAL boundary per handoff)
- **Removal of T1.1's 4 retained mirror sites (per convergent F2 v3 PFR — Codex F2 + Advisor F2 ADOPT 2026-05-23):** The in-source comment block at [`engine.py:1146-1148`](../../backtest/engine.py#L1146) is a **durable doctrine marker** documenting defense-in-depth intent (text: "4 existing mirror sites below (cost_anchor_id at :1148, parent_run_id at :1168, T_obs at :1281, LATE_FILL at :1332) remain as belt-and-suspenders per project defense-in-depth doctrine"). The comment-block-cited line numbers (`:1148/:1168/:1281/:1332`) are the literal references in the source comment but may be slightly stale w.r.t. HEAD post-T1.1-SEAL refactoring; the **actual current check sites empirically verified at v4 drafting (2026-05-23) are at approximately `:1158` (cost_anchor_id FIX-B1 defensive at `expected_anchor = COST_ANCHOR_ID_MAPPING.get(lc_exec_path)`) / `~:1186` (parent_run_id area) / `:1284` (T_obs SYS3-B2 area) / `:1342` (LATE_FILL SYS3-B1 asymmetric pair check)**. The comment-block-vs-current divergence is itself out-of-scope for T1.4 (would require modifying engine.py comment block; eligible for T1.6 documentation cycle per existing exclusion). RETAINED per v9 SEAL ratify discipline; defense-in-depth doctrine.
- T1.1 SYS5 adversarial coverage (already shipped at [`tests/test_t1_1_sys_fix.py:2583`](../../tests/test_t1_1_sys_fix.py#L2583) `TestSys5RevalidateForWriteDirectStrictFields`; do not duplicate)
- Cross-cohort verification (per Advisor F14 v1 hardening): explicit exclusion of `phase4_forward_2026_07bps_v1` + `phase4_forward_2026_13bps_v1` + `phase4_forward_2026_17bps_v1` cost-grid cohorts; β-scope LOCKED to 15bps cohort per plan v5 §2.4 line 279
- Per-bar artifact content validation paths within `check_b_c_extended_semantics_or_raise()` (out of A2-α LOCK scope per §2.3; T1.5 covers)
- Production per-bar consumer code creation (out of T1.4 β-scope; A2-α LOCK avoids this by using existing T1.2-sealed validator)
- T1.3 plan-vs-impl divergence corrective (γ-4 eligible-not-named per anti-pre-emption; v3 proceeds with γ-1 only; future Charlie register-event required to fire γ-4 corrective if substantively warranted)

---

## §5 Risks + dependencies

### §5.1 Dependencies

- T1.1 + T1.2 + T1.3 SEALED at commit `12dffde` (pushed); T1.4 consumes their interfaces
- Legacy phase4 artifacts at `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` (39 candidate subdirs + aggregate) intact + unmutated since pre-T1.x parent `7c8f4a7` (precondition empirically verified at v2/v3 drafting per §2.2)
- pytest discovery + scipy + existing wf_lineage helper modules + Python `ast` stdlib module

### §5.2 Risks (revised v3)

| # | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R1 | Hash-fixture approach (i) requires git plumbing in tests; brittleness risk | LOW | Use `subprocess.run(["git", "show", "7c8f4a7:<path>"], capture_output=True)` with documented error fallback; git availability assumed (CI invariant) |
| R2 | Legacy artifacts mutate between v3 ratify and test execution | LOW | Ratify gate empirically re-verifies `git diff 7c8f4a7..HEAD --stat -- data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/` is empty |
| R3 | B1 grep surfaces positional-dependency breakage in some caller | LOW | Classify as T1.3 corrective defect (NOT T1.4 fix); escalate via Charlie register |
| R4 | A2-α message-keyword spec drifts if `check_b_c_extended_semantics_or_raise()` implementation message changes | LOW | Pre-commit message-keyword classes at sub-plan ratify; test catches drift as backward-compat regression (appropriate) |
| R5 | Producer-consumer asymmetry recurrence pattern reappears at T1.4 reviewer round | LOW | T1.1 SYS5 invariant covers 14 fields at producer; T1.4 is verification not new invariant; cross-model leg + Mode A discipline still load-bearing |
| R6 | DB migration idempotency assumption fails in production | LOW | §2.7 covers 3 idempotency scenarios; catches regression at test time |
| R7 (revised per Codex F2 v2 PFR) | B1 AST classifier misses unusual call shapes | LOW | Phase 2 specification: ALL `keyword(arg=None)` → `dynamic_count` (no static inference); §3.1 pc 5 requires explicit orchestrator adjudication per dynamic instance at ratify-gate |
| R8 (revised v4 per Advisor F1 v3 PFR ADOPT-LIGHT; pointer corrected v5 per Codex F2 v4 PFR) | T1.3 plan-vs-impl divergence at walk_forward + evaluation-gate driver creates blind spot for future LC-threading consumers; **AND γ-1 test-class limitation (B3.3+B3.4 verify Contract-2.0.4-compliant default-normalization output but do NOT positively assert source-of-output is intended opt-out; would pass under silent regression to opt-out)** | LOW | γ-1 verifies opt-out doesn't break backward-compat NOW; future γ-4 corrective register eligible-not-named per anti-pre-emption; **explicit risk-flag preserved here at §5.2 R8 + cross-referenced at §12 v4-2 + §13 v5-5 (revision logs) for cycle-SEAL discoverability** (corrected from v4 stale §10 pointer per Codex F2 v4 PFR — §10 is Task SEAL chain placeholder, not risk-flag location); Advisor F1 v3 PFR proposed positive AST/grep assertions to close γ-1 test-class gap, NOT ADOPTed at v4 per Codex non-convergence + Advisor self-discount (overengineering risk); γ-1 hardening eligible at future cycle |

---

## §6 Reviewer dispatch plan

### §6.1 Sub-plan PFR-rule-Y re-review (historical: v1-v5 PFR rounds completed; v6 SKIPPED per Path A)

**Historical PFR-rule-Y discipline (v1-v5 rounds completed):** 5 iterations of 2-leg parallel dispatch (Codex via `Agent(codex:codex-rescue)` + Claude advisor via `Agent(quant-research-advisor)`) per B2 standing rule LOCKED 2026-05-19. Cross-model leg + own-finding-anchoring discount + orchestrator Mode A re-verification all 3 layers operational across cycle. Final convergence at v5 PFR: both legs returned only LOW mechanical findings + explicit "no v6 finding predicted" per T1.1 v9 cycle-final precedent.

**v6 PFR-rule-Y SKIPPED per Charlie Path A register 2026-05-23:** all 3 v6 fixes are mechanical literal substitutions (§8 preamble version-tag staleness + §6.1 eligibility paragraph staleness + §13 v2→v3 row severity-count correction); per [`feedback_reviewer_routing_subagent_default.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md) PFR-rule-Y SKIP criterion ("All adjudication outcomes were mechanical literal application of reviewer-stated fixes"), v6 PFR re-review is SKIP-eligible; Charlie Path A elected SKIP over Path B continued-rigor per cycle-final convergence already confirmed at v5 PFR.

**Codex auto-notification routine (per Codex F5 v2 PFR fix; preserved for any future PFR rounds):**
- After `Agent(codex:codex-rescue)` returns, call `node "${PLUGIN_PATH}/scripts/codex-companion.mjs" status` (no args) to extract canonical JOB_ID
- Pass canonical JOB_ID (format `(task|review)-[a-z0-9]+-[a-z0-9]+`) to `~/.claude/scripts/codex-wait-and-fetch.sh <JOB_ID> [<timeout_seconds>]`
- See routing memory at `/Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md` lines 48-60 for JOB_ID extraction protocol

**PFR-rule-Y SKIP-eligibility analysis at v6 (per Charlie Path A register; corrected from v5 stale paragraph per convergent F2-Advisor + F1-Codex v5 PFR):** All 3 v6 fixes are mechanical literal application of v5 PFR reviewer-stated fixes (cf. §14 v5→v6 revision log). Per PFR-rule-Y SKIP criterion, v6 re-review SKIP-eligible. Path A elected SKIP per cycle-final convergence already confirmed at v5 PFR (both legs "no v6 finding predicted"); Path B (continued rigor) would have applied if substantive new content existed.

### §6.2 Implementation reviewer rounds (post-ratify)

2-leg dispatch on each PFR round per implementation arc. Final-round adversarial SEAL-eve review with explicit "assume hidden bugs" framing per v8 empirical discipline.

---

## §7 SEAL gate criteria

T1.4 SEAL ratify requires:
1. All §3.1 9 pass criteria met
2. 2-leg convergent APPROVE on final implementation iteration
3. Final-round adversarial SEAL-eve review returns no NEW BLOCKING
4. Mode A independent re-verification on every Advisor specific factual claim (orchestrator grep/Read source before adoption)
5. Charlie register-event boundary: "T1.4 SEAL ratify authorized" — distinct from cycle entry + plan ratify + implementation completion registers
6. Bundle commit at T1.4 SEAL contains all touched artifacts; commit message documents 9/9 pass criteria

---

## §8 Anti-pre-emption explicit reminder + named sub-decisions

This sub-plan v6 is **advisory and pre-ratify**. Cycle-final convergence achieved through 5 PFR-rule-Y iterations (v1→v5; cf. §11+§12+§13+§14 revision logs). No engineering work begins until:
1. ~~v5 PFR-rule-Y reviewer round completes~~ COMPLETED 2026-05-23 (both legs APPROVE-FOR-SUB-PLAN-RATIFY + "no v6 finding predicted")
2. ~~Per-finding adjudication applied~~ COMPLETED — 3 mechanical fixes applied at v6 per Charlie Path A register
3. ~~Possible v6 iteration for new substantive content~~ N/A — only mechanical residuals; v6 PFR SKIPPED per Charlie Path A (PFR-rule-Y SKIP criterion + cycle-final convergence)
4. ~~Convergent APPROVE-FOR-SUB-PLAN-RATIFY reached~~ REACHED at v5 PFR (both legs)
5. **Charlie sub-plan ratify register fires** ← NEXT REGISTER-EVENT BOUNDARY

### §8.1 Named load-bearing sub-decisions (ALL RESOLVED 2026-05-23 at ratify)

- ~~**§2.2 hash-fixture approach:** (i) git-plumbing vs (iii) inline-asserted~~ **RESOLVED 2026-05-23 Charlie register "(i) git-plumbing":** (i) git-plumbing LOCKED — `subprocess.run(["git", "show", "7c8f4a7:<path>"])` at test runtime + SHA256-compute "before" hashes; provenance ties hashes to git commit `7c8f4a7` (pre-T1.x parent); brittleness LOW vs (iii); runtime cost negligible (single subprocess per fixture)
- ~~§2.3 consumer degradation behavior~~ **RESOLVED 2026-05-23 Charlie register "A2-α" + "F1 exception class ADOPT":** A2-α LOCKED with strict-validator domain-fence test raising `ValueError` (per F1; not subclass on structural failure); 3 pre-committed message-keyword classes (corrected per F-NEW-3); A2 excludes per-bar content validation paths
- ~~§2.6 B3 scope: 4 entry points all LC-threading~~ **RESOLVED 2026-05-23 Charlie register "γ-1":** B3.3 + B3.4 rewritten as γ-1 opt-out-verification (verify T1.3-D opt-out preserves Contract 2.0.4 backward-compat); B3.1 + B3.2 remain LC-positive; γ-4 T1.3 plan-vs-impl corrective eligible-not-named per anti-pre-emption
- ~~**§2.4 B1 4-tuple empirical lock**~~ **RESOLVED 2026-05-23 at ratify (empirical lock at HEAD `12dffde`):** `(prod_count=9, test_count=46, scripts_count=0, dynamic_count=17)`. **Dynamic_count adjudication (per §2.4 pass criterion (d)):** all 17 dynamic_count instances classified backward-compat-safe via single-pattern-class adjudication — all are in `tests/test_t1_3_registry_api.py` using uniform `_make_minimal_write_args() → dict + optional mutation + _write_to_registry(**args)` pattern; helper returns named kwargs (positional binding NOT relied on); mutations add named keys (not positional args); `**` expansion as named kwargs preserves T1.3-C HYBRID extension semantics. Single adjudication entry covers all 17 instances. Per-file dynamic counts: test_t1_3_registry_api.py:520 + :562 + :601 + :650 + :675 + :916 + :933 + :954 + :1020 + :1108 + :1141 + :1173 + :1334 + :1354 + :2070 + :2089 + :2109 = 17 instances. (Line :1440 `def fake_write_to_registry(**kwargs):` is a stub def for monkeypatch, NOT a `_write_to_registry(**)` call — excluded from dynamic_count.)
- ~~**§2.5 9-column enumeration**~~ **RESOLVED 2026-05-23 at ratify (empirical verify against MIGRATION_COLUMNS at HEAD `12dffde`):** all 9 columns verified present + ordered: `cost_anchor_id` (line 147) + `returns_per_bar_path` (155) + `returns_per_bar_sha256` (156) + `T_obs` (157) + `regime_key` (166) + `current_git_sha` (167) + `execution_config_path` (168) + `execution_config_sha256` (169) + `parquet_data_sha256` (170). §2.5 table column enumeration matches MIGRATION_COLUMNS at HEAD; no drift.
- ~~**§3.1 pass criterion 9 baseline test count**~~ **RESOLVED 2026-05-23 at ratify (empirical `pytest --collect-only` at HEAD `12dffde`):** **2191 tests collected** (matches v1 Codex empirical verification + CLAUDE.md Phase Marker T1.1 SEAL boundary). T1.4 implementation expected to grow this to 2191 + (T1.4 test count); zero pre-T1.4 regression per §3.1 pc 9.
- ~~**§2.6 B3.4 test isolation mechanism**~~ **RESOLVED at v3 PFR per Codex F1 fix spec:** `DEFAULT_DB_PATH` monkeypatch (preferred) OR `run_regime_holdout` wrapper (alternate); test-write-time discretion within these 2 named options. (No additional Charlie register required at ratify — locked at v3 via 2-named-options spec.)

**ALL §8.1 sub-decisions RESOLVED.** T1.4 sub-plan v6 is fully ratified; T1.4 implementation cycle entry is the next register-event boundary.

### §8.2 Anti-pre-emption preserve

- T1.5 + T1.6 + B-C-extended cycle SEAL + §35 codification + 4 mirror site removal + cost-grid cohorts + γ-4 T1.3 corrective — all EXPLICITLY EXCLUDED at §4
- T1.4 scope expansion beyond β-scope requires fresh Charlie register-event
- Implementation start + 2-leg dispatch + PFR rounds + SEAL ratify — each requires separate Charlie register-event boundary

---

## §9 Cycle-pattern observations (carry-forward from T1.1 SEAL + v2 PFR empirical addition)

Reviewers should be alert for (but not assume) the producer-consumer asymmetry recurrence pattern at T1.4. T1.1 SYS5 `revalidate_for_write()` centralizes 14-field validation at producer; T1.4 is verification-only (not new invariant). Pattern recurrence would manifest at consumer-side asymmetries; if observed across ≥3 review iterations, escalate to invariant-level closure per [`feedback_invariant_level_vs_enumeration.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_invariant_level_vs_enumeration.md).

Mode A discipline: Advisor's `[VERIFIED]` tokens are NOT reliable evidence; orchestrator independent re-verification REQUIRED before adoption.

Codex's `[VERIFIED]` tokens ARE reliable evidence within tokenized scope (0 hallucinations within tokenized verification claims across R3.1d + R2.0 + R2.1 + §34 + R2.3 + B2 + R6.1 + T1.x arc through v2 PFR).

**v2 PFR own-finding-anchoring discount empirical validation (codified at v3):** Advisor authored 15 of 17 v1 fixes; v2 PFR applied explicit own-finding-anchoring discount discipline; caught 1 HIGH defect (F-NEW-1 B3.3 structurally impossible) at her own fix territory (v1 F9 rewrite of B3 scenarios). Codex came in fresh on v2 (no v1 fix authorship); caught 2 BLOCKING (F1 exception class + F4 extended F-NEW-1 to B3.4) + 2 HIGH (F2 AST classifier still incomplete + F3 outside-repo) that Advisor missed via residual anchoring. **3-layer safety architecture (Advisor own-anchoring discount + Codex cross-model leg + orchestrator Mode A re-verification) all 3 load-bearing at v2 PFR.** B2 standing rule LOCKED 2026-05-19 + own-finding-anchoring discount discipline both validated empirically.

**v1 → v2 → v3 orchestrator Mode A lesson (codified at v3):** v1 introduced 2 BLOCKING + 1 logic-error defects caught by 2-leg reviewer round. v2 introduced 0 BLOCKING + 1 HIGH structural defect at B3.3 (own-finding-anchoring trap on Advisor's v1 F9 rewrite) + 1 BLOCKING exception-class misread at A2-α LOCK + 1 HIGH AST-classifier-still-incomplete + 1 HIGH outside-repo-missed + 4 line-ref/keyword precision defects. **Orchestrator Mode A discipline gap at v2 drafting:** misread plan v5 §10 B3-b "BCExtendedSchemaValidationError(ValueError) subclass" as "always-subclass" instead of "structural-Phase-1-fails-with-ValueError + collect-all-Phase-2-fails-with-subclass" per B1-c hybrid order. v3 drafting independently re-verifies every cross-reference to plan v5 §10 RESOLVED locks via independent grep/Read; cross-references plan v5 + T1.2 SEALED impl together to catch divergence.

---

## §10 Task SEAL chain (post-ratify execution log; populated at SEAL boundary)

**(populated post-ratify)**

---

## §11 v1 → v2 → v3 revision log (historical: v1→v2 + v2→v3 iterations; LIVE current-state at §12 + §13)

**v2 PFR-rule-Y reviewer round outcome (2026-05-23):**
- Advisor leg: 6 findings (0 BLOCKING + 1 HIGH + 3 MEDIUM + 2 LOW; explicit own-anchoring discount applied)
- Codex leg: 5 findings (2 BLOCKING + 2 HIGH + 0 MEDIUM + 1 LOW; fresh adversarial; load-bearing F1 exception class + F4 extension catches)
- Mode A re-verification: all specific claims VERIFIED TRUE
- Convergent: B3 entry-points impossible (Advisor F-NEW-1 HIGH + Codex F4 BLOCKING extension); line-ref corrections (Advisor F-NEW-2 + Codex F4 sub-claim)
- Advisor unique: F-NEW-3 keyword precision; F-NEW-4 wf_lineage.py:541 line ref; F-NEW-5 mirror site comment-line refs; F-NEW-6 ratify-time count
- Codex unique: F1 exception class (Advisor own-anchoring blind spot); F2 AST classifier still incomplete (Advisor own-anchoring on v1 F3 fix); F3 outside-repo missing (Advisor missed); F5 JOB_ID extraction missing
- Charlie register 2026-05-23: γ-1 + F1 ADOPT + v3 drafting authorized

**v2 → v3 fix mapping (11 ADOPTed adjudications):**

| Fix # | Source finding(s) | v3 location | Change class |
|---|---|---|---|
| v3-1 | Codex F1 v2 BLOCKING (A2 exception class wrong) | §1.1 A2 + §2.3 + §3.1 pc 3 + §8.1 | Change A2-α LOCK spec: ValueError (not BCExtendedSchemaValidationError); keyword class table revised: `artifact_schema_version` (not `schema_version`) + `b_c_extended_v1` only (drop disjunction) |
| v3-2 | Codex F4 v2 BLOCKING + Advisor F-NEW-1 v2 HIGH (B3.3 + B3.4 impossible at HEAD; γ-1 LOCK) | §1.1 B3 + §2.6 + §8.1 | B3.3 + B3.4 rewritten as γ-1 opt-out-verification; B3.1 + B3.2 remain LC-positive; γ-1 pass criterion specified |
| v3-3 | Codex F2 v2 HIGH (AST classifier still incomplete: **args + worktree contamination) | §2.4 + §3.1 pc 5 + §5.2 R7 | Phase 1 scoped grep (backtest/tests/scripts only; exclude .claude/, .git/, venvs); Phase 2 ALL keyword(arg=None) → dynamic_count; explicit Charlie adjudication at ratify-gate for dynamic_count > 0 |
| v3-4 | Codex F3 v2 HIGH (B2 missing outside-repo fail-closed) | §1.1 B2 + §2.5 + §3.1 pc 6 | NEW B2.d scenario covers outside-repo path-containment fail-closed branch |
| v3-5 | Advisor F-NEW-2 v2 MEDIUM + Codex F4 sub-claim (run_regime_holdout line ref :1464 → :2270) | §2.6 B3.2 | Citation corrected to engine.py:2270 (def) + :2290 (LC kwarg) |
| v3-6 | Advisor F-NEW-3 v2 MEDIUM (A2-α keyword precision) | §2.3 (closed alongside v3-1) | Keyword class 1 corrected to `artifact_schema_version`; class 2 narrowed to `b_c_extended_v1` only |
| v3-7 | Advisor F-NEW-4 v2 MEDIUM (wf_lineage.py:541 wrong) | §2.3 | Citation corrected: artifact_schema.py:654 (def) + wf_lineage.py:544 (re-export import line) |
| v3-8 | Advisor F-NEW-5 v2 LOW (§4 mirror site line refs are comment lines) | §4 | Per Advisor option (b): cite in-source comment-block at engine.py:1146-1148 which itself documents actual check lines (~:1158/~:1186/:1284/:1342); comment-block markers are durable refs |
| v3-9 | Advisor F-NEW-6 v2 LOW ("55 total" verify at ratify) | §2.4 last paragraph | Already addressed via §8.1 ratify-time empirical lock; v3 explicitly notes SCOPED grep yields 55 (vs worktree-contaminated higher number per Codex F2) |
| v3-10 | Codex F5 v2 LOW (JOB_ID extraction missing in §6.1) | §6.1 | Added explicit JOB_ID extraction step + canonical format spec + memory cross-ref with absolute path |
| v3-11 | v2 PFR cycle-pattern empirical (own-anchoring discount + 3-layer safety + orchestrator Mode A gap on plan v5 §10 read) | §9 | Codified empirical lesson at §9 for cycle-SEAL discoverability |

**v3 also corrects (orchestrator Mode A discipline at v3 drafting time):**
- §4 explicit acknowledgment that the 4 mirror site line refs (cited :1148/:1168/:1281/:1332 at v2) are comment-block markers per Advisor F-NEW-5 evidence; actual check lines documented adjacent for reader navigation
- §3.1 pc 10 added: Mode A independent re-verification as explicit SEAL-gate orchestrator discipline criterion per Advisor v2 senior-quant observation (which flagged that "Mode A discipline" mixed test-pass + process criteria)
- §5.2 R8 NEW: T1.3 plan-vs-impl divergence at walk_forward + evaluation-gate as risk flag for cycle-SEAL discoverability; γ-4 corrective eligible-not-named per anti-pre-emption

**v3 does NOT change (per anti-pre-emption / scope-class preserve):**
- β-scope register (Charlie register β unchanged)
- §4 exclusions substance (T1.5/T1.6/§35/4-mirror-removal — preserved; cost-grid + γ-4 corrective added)
- SEAL gate criteria substance (v2→v3 historical record: criterion count revised to 10 with Mode A discipline as pc 10; substance unchanged at v3; SUPERSEDED at v4: see §12 v4-4 which reduced to 9 pass criteria per Advisor F3 v3 PFR)
- §2.7 DB migration idempotency (Advisor F10 fix unchanged at v3)
- §2.2 hash-fixture approach (still NAMED sub-decision; precondition empirically verified at both v2 + v3)

---

## §12 v3 → v4 revision log

**v3 PFR-rule-Y reviewer round outcome (2026-05-23):**
- Advisor leg: 4 findings (0 BLOCKING + 0 HIGH + 1 MEDIUM + 3 LOW; explicit own-anchoring discount applied; authored 6 of 11 v3 fixes)
- Codex leg: 2 findings (0 BLOCKING + 1 HIGH + 0 MEDIUM + 1 LOW; fresh adversarial; non-convergent on Advisor F1 + load-bearing F1 catch on B3.4 isolation)
- Mode A re-verification: all specific claims VERIFIED TRUE
- Convergent: F2 mirror site comment block (both legs LOW)
- NON-convergent: Advisor F1 γ-1 trivial-pass under-spec (Codex didn't flag — informs Advisor own-anchoring artifact assessment); Codex F1 B3.4 isolation (Advisor missed via own-anchoring on her γ-1 rewrite)
- Convergence trajectory: v1 (21 findings, 4 BLOCKING) → v2 (11 findings, 4 BLOCKING) → v3 (6 findings, 0 BLOCKING + 1 HIGH) — clearly trending toward ratify-ready
- Charlie register 2026-05-23: Path B (v4 draft + dispatch PFR-rule-Y re-review) + Advisor F1 ADOPT-LIGHT

**v3 → v4 fix mapping (5 ADOPTed adjudications):**

| Fix # | Source finding | v4 location | Change class |
|---|---|---|---|
| v4-1 | Codex F1 v3 HIGH (B3.4 test isolation missing) | §1.1 B3 + §2.6 B3.4 + §8.1 | Add isolation mechanism spec: `DEFAULT_DB_PATH` monkeypatch (preferred) OR `run_regime_holdout` wrapper (alternate); `summary["lifecycle_state"] != "holdout_error"` happy-path gate; unique `parent_run_id=f"phase2c_eval_gate_{run_id}"` row query |
| v4-2 | Advisor F1 v3 MEDIUM ADOPT-LIGHT (γ-1 trivial-pass under-spec) | §2.6 γ-1 limitation acknowledgment + §5.2 R8 risk-flag revision | Brief acknowledgment of test-class limitation (B3.3+B3.4 verify Contract 2.0.4 default-normalization output but don't positively assert source-of-output); residual risk flagged at §5.2 R8; NO positive AST/grep assertions added (per Codex non-convergence + Advisor self-discount disclosure; overengineering risk) |
| v4-3 | Convergent F2 v3 LOW (Codex + Advisor; mirror site comment block divergence) | §4 mirror-site exclusion + §11 v3-8 (carried at v4 via §12) | Rewording: comment block at engine.py:1146-1148 is durable doctrine marker citing literal `:1148/:1168/:1281/:1332` (may be stale w.r.t. HEAD); actual current check sites empirically verified at v4 drafting: `:1158/~:1186/:1284/:1342`; comment-block-vs-current divergence out-of-scope (T1.6 eligible) |
| v4-4 | Advisor F3 v3 LOW (§3.1 pc 10 vs §7 cr 4 Mode A duplication) | §3.1 (10 → 9 pass criteria) | Remove §3.1 pc 10 (Mode A discipline); preserved at §7 SEAL gate criterion 4 only; renumber to 9 mandatory pass criteria (test-pass vs SEAL-gate process discipline correctly separated) |
| v4-5 | Advisor F4 v3 LOW (§2.4 dynamic_count scope-bounding sentence) | §2.4 Phase 3 pass criterion (d) | Add scope-bounding sentence: "dynamic_count adjudication entry locked at T1.4 ratify only; future post-T1.4-SEAL engineering governed by §35 codification eligible-not-named per anti-pre-emption" |

**v4 does NOT change (per anti-pre-emption / scope-class preserve):**
- β-scope register (Charlie register β unchanged through 4 iterations)
- §4 exclusions substance (T1.5/T1.6/§35/4-mirror-removal/cost-grid/γ-4 corrective preserved)
- §2.7 DB migration idempotency
- §2.2 hash-fixture approach (still NAMED sub-decision; precondition empirically verified at v2/v3/v4)
- §2.3 A2-α LOCK + F1 ValueError fix (closed at v3-1; preserved at v4)
- §2.5 B2.a/b/c/d 4 scenarios + 9-column enumeration table (preserved at v4)
- §2.6 B3.1 + B3.2 LC-positive scenarios + γ-1 B3.3 framework (only B3.4 substantive isolation-mechanism added)

**v4 cross-model leg empirical observation (codified):** v3 PFR demonstrated NON-convergence cost-effectiveness — Advisor F1 (γ-1 trivial-pass) was caught only by Advisor via own-anchoring discount + Codex F1 (B3.4 isolation) was caught only by Codex via fresh-perspective on whole-test-design-not-just-spec-wording territory. **Two distinct anti-anchoring mechanisms (own-finding discount + cross-model fresh-eye) provided non-overlapping defect surfacing.** Both load-bearing at this PFR; neither sufficient alone for this iteration class.

---

## §13 v4 → v5 revision log

**v4 PFR-rule-Y reviewer round outcome (2026-05-23):**
- Advisor leg: 3 findings (0 BLOCKING + 0 HIGH + 0 MEDIUM + 3 LOW; APPROVE-FOR-SUB-PLAN-RATIFY conditional on F1 mechanical fix; own-anchoring discount applied — authored 4 of 5 v4 fixes; cumulative ~26-29/33-38 across cycle)
- Codex leg: 3 findings (0 BLOCKING + 0 HIGH + 0 MEDIUM + 3 LOW; Axis 1 PASS on v4-1 B3.4 isolation + v4-3 mirror-site + §12 row-count; "no structural or methodology gaps" + "HIGH confidence ratify-ready after F1-F3 mechanical fixes")
- Mode A re-verification: all specific claims VERIFIED TRUE
- Convergent: F1 §7 stale "10 pass criteria" references (both legs LOW; mechanical)
- Non-convergent unique: Advisor F2 line-ref off-by-1 in §2.6 B3.4 + Advisor F3 §11 header temporally stale + Codex F2 R8 §10 pointer wrong + Codex F3 §6.1 reviewer-dispatch wording stale (4 unique LOW from each leg + 1 convergent LOW + 1 sub-claim = 6 mechanical fixes total)
- Charlie register 2026-05-23: Path B (apply 6 mechanical fixes + dispatch v5 PFR-rule-Y re-review)

**v4 → v5 fix mapping (6 ADOPTed mechanical adjudications; all LOW; all mechanical literal application of reviewer-stated fixes):**

| Fix # | Source finding | v5 location | Type |
|---|---|---|---|
| v5-1 | Convergent F1 v4 LOW (both legs; §7 stale "10 pass criteria" cross-refs after v4-4 §3.1 renumbering) | §7 cr 1 + cr 6 | Update "10 pass criteria" → "9 pass criteria"; "10/10" → "9/9" |
| v5-2 | Advisor F1 sub-claim v4 LOW (§11 line 426 stale "substance unchanged" bullet at v4) | §11 v3 stale bullet | Annotate: "(v2→v3 historical record: criterion count revised to 10... SUPERSEDED at v4: see §12 v4-4 which reduced to 9)" |
| v5-3 | Advisor F2 v4 LOW (scripts/run_phase2c_evaluation_gate.py line refs off-by-1: :514→:515 parent_run_id; :524→:525 except boundary) | §2.6 B3.4 | Correct line citations to :515 (parent_run_id) and :525-534 (except Exception:) |
| v5-4 | Advisor F3 v4 LOW (§11 header temporally stale at v4) | §11 header | Annotate: "(historical: v1→v2 + v2→v3 iterations; LIVE current-state at §12 + §13)" |
| v5-5 | Codex F2 v4 LOW (§5.2 R8 §10 pointer wrong; §10 is Task SEAL chain placeholder not risk-flag location) | §5.2 R8 | Replace "explicit risk-flag in §10 below" with "explicit risk-flag preserved here at §5.2 R8 + cross-referenced at §12 v4-2 + §13 v5-5 for cycle-SEAL discoverability" |
| v5-6 | Codex F3 v4 LOW (§6.1 reviewer-dispatch wording stale; says "this v3" + "v3 substance + 11-fix completeness" + only v2→v3 log) | §6.1 | Update to "this v5" + "v5 substance + 6-mechanical-fix completeness + ratify-readiness final check"; brief reviewers on §12 + §13 with §11 as prior-trace context |

**v5 does NOT change (per anti-pre-emption / scope-class preserve):**
- β-scope register (Charlie register β unchanged through 5 iterations)
- §4 exclusions substance (T1.5/T1.6/§35/4-mirror-removal/cost-grid/γ-4 corrective preserved)
- §2.2 hash-fixture approach (still NAMED sub-decision; precondition empirically verified at v2/v3/v4/v5)
- §2.3 A2-α LOCK + F1 ValueError fix (preserved)
- §2.5 B2.a/b/c/d 4 scenarios + 9-column enumeration table (preserved)
- §2.6 B3.1 + B3.2 LC-positive scenarios + γ-1 B3.3 framework (only B3.4 substantive isolation-mechanism updates from v4)
- §2.7 DB migration idempotency
- §2.4 B1 AST classifier (Phase 1 scoped + Phase 2 `keyword(arg=None)` + Phase 3 4-tuple + §35 scope-bounding all preserved)

**v5 PFR-rule-Y SKIP-eligibility analysis (per [`feedback_reviewer_routing_subagent_default.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md) PFR-rule-Y skip criterion):**

> "Skip post-fix re-review when: All adjudication outcomes were mechanical literal application of reviewer-stated fixes; Only deletions / mechanical fixes; Bucket-1 / lightweight cycles where reviewer round itself was the diligence (not a closeout); TBD placeholders to be filled at later mechanical step"

All 6 v5 fixes are mechanical literal application of reviewer-stated fixes:
- v5-1: literal "10" → "9" numerical substitution (both legs F1)
- v5-2: literal annotation addition (Advisor F1 sub-claim)
- v5-3: literal line number correction (Advisor F2)
- v5-4: literal header annotation (Advisor F3)
- v5-5: literal pointer correction (Codex F2)
- v5-6: literal wording correction (Codex F3)

**Per PFR-rule-Y SKIP criterion, v5 PFR re-review would technically be eligible to skip.** However, Charlie Path B register explicitly authorized "dispatch v5 PFR-rule-Y re-review" — rigor-prioritized path elected over skip-eligible mechanical-fix shortcut. v5 PFR re-review proceeds per Path B authorization for cycle-final convergent-check rigor (not per PFR-rule-Y mandatory).

**v5 cycle convergence trajectory observation:**

| Iteration | Total findings | BLOCKING | HIGH | MEDIUM | LOW | Severity profile |
|---|---|---|---|---|---|---|
| v1 → v2 | 21 | 4 | 5 | 4 | 8 | substantive defects |
| v2 → v3 (corrected v6 per convergent F3-Advisor + F2-Codex v5 PFR) | 11 | 2 | 3 | 3 | 3 | substantive defects (per-leg sum: Advisor 0+1+3+2=6 + Codex 2+2+0+1=5 = 11) |
| v3 → v4 | 6 | 0 | 1 | 1 | 4 | mostly precision |
| v4 → v5 | 6 | 0 | 0 | 0 | 6 | all mechanical |
| v5 → v6 | 3 | 0 | 0 | 0 | 3 | all mechanical; cycle-final |

Convergence trajectory: BLOCKING 4 → 2 → 0 → 0 → 0 trending zero; HIGH 5 → 3 → 1 → 0 → 0 trending zero; total findings 21 → 11 → 6 → 6 → 3 (clear saturation). v5 PFR returned both-legs APPROVE-FOR-SUB-PLAN-RATIFY with explicit "no v6 finding predicted"; v6 PFR SKIPPED per Charlie Path A + PFR-rule-Y SKIP criterion. Cycle-final convergence empirically reached (analogous to T1.1 v9 cycle-final precedent).

---

**End of T1.4 sub-plan v5 (historical — last PFR-iteration version).** v5 PFR-rule-Y reviewer round completed 2026-05-23; outcome at §14 v5→v6 revision log below.

---

## §14 v5 → v6 revision log (CYCLE-FINAL)

**v5 PFR-rule-Y reviewer round outcome (2026-05-23 — cycle-final convergent-check round per Charlie Path B register at v4→v5):**
- Advisor leg: 3 findings (0 BLOCKING + 0 HIGH + 0 MEDIUM + 3 LOW; APPROVE-FOR-SUB-PLAN-RATIFY conditional on F1+F2+F3 mechanical fixes; own-anchoring discount applied — authored 3 of 6 v5 fixes; cumulative ~28/38 ~74% across 5 iterations)
- Codex leg: 2 findings (0 BLOCKING + 0 HIGH + 0 MEDIUM + 2 LOW; "no v6 finding predicted: both items are direct textual consistency fixes, and the convergence signal remains cycle-final rather than substantively open"; HIGH confidence ratify-ready)
- Mode A re-verification: all specific claims VERIFIED TRUE (orchestrator independent grep/Read on every Advisor + Codex specific claim)
- Convergent findings: F2-Advisor + F1-Codex (§6.1 PFR-rule-Y eligibility paragraph still has v3 rationale; v5-6 fix updated only first half of §6.1, missed trailing eligibility paragraph); F3-Advisor + F2-Codex (§13 v2→v3 trajectory row severity counts wrong: written 4/3/0/4, actual per-leg sums 2/3/3/3)
- Non-convergent unique: F1-Advisor (§8 anti-pre-emption preamble "sub-plan v4" + "v4 PFR-rule-Y" stale; analog of v5-6 pattern at parallel-section site Advisor caught via fresh-eye systematic scan; Codex did not surface)
- Both legs explicit: "no v6 finding predicted" + cycle-final convergence empirically reached
- Charlie register 2026-05-23: Path A (apply 3 mechanical fixes inline; skip v6 PFR re-review per PFR-rule-Y SKIP criterion + both-legs cycle-final convergence confirmation)

**v5 → v6 fix mapping (3 ADOPTed mechanical adjudications; all LOW; all mechanical literal application of reviewer-stated fixes):**

| Fix # | Source finding | v6 location | Type |
|---|---|---|---|
| v6-1 | Advisor F1 v5 LOW (§8 anti-pre-emption preamble version-tag staleness) | §8 preamble | Update "sub-plan v4" → "sub-plan v6" + "v4 PFR-rule-Y" → "v5 PFR-rule-Y reviewer round completed"; revise to reflect cycle-final state with strikethrough on completed steps + arrow on next register-event boundary |
| v6-2 | Convergent F2-Advisor + F1-Codex v5 LOW (§6.1 PFR-rule-Y eligibility paragraph stale v3 rationale; trailing-paragraph staleness within v5-6 section but half not edited) | §6.1 | Replace v3 rationale "v3 has substantial new content beyond mechanical literal application — F1 ValueError correction + γ-1 B3.3+B3.4 opt-out-verification rewrite..." with v6 cycle-final SKIP-eligibility analysis per Path A + cross-ref to §14 |
| v6-3 | Convergent F3-Advisor + F2-Codex v5 LOW (§13 v2→v3 trajectory row severity counts mismatch §11 leg-counts: written 4/3/0/4, actual per-leg sums 2/3/3/3) | §13 trajectory table | Correct v2→v3 row from 4/3/0/4 to 2/3/3/3 per-leg sum (Advisor v2 = 0+1+3+2 + Codex v2 = 2+2+0+1 = 11 total); add explanatory note "(corrected v6 per convergent F3-Advisor + F2-Codex v5 PFR)"; correct trajectory narrative paragraph to reflect actual numbers (BLOCKING 4→2→0→0→0 not 4→4→0→0; total 21→11→6→6→3) |

**v6 also corrects (in §6.1 and §8 preamble):**
- §6.1 historical PFR-rule-Y discipline summary added: documents 5-iteration v1-v5 cycle completion + 3-layer safety architecture all operational + cross-model leg + own-finding-anchoring discount + orchestrator Mode A re-verification
- §8 preamble: strikethrough on completed steps (v5 PFR completed, adjudication applied, v6 PFR skipped, convergent APPROVE reached); arrow on next register-event boundary (Charlie sub-plan ratify register fires)

**v6 does NOT change (per anti-pre-emption / scope-class preserve):**
- β-scope register (Charlie register β unchanged through 6 iterations)
- §4 exclusions substance
- §2.2 hash-fixture approach (still NAMED sub-decision; lock at ratify)
- §2.3 A2-α LOCK + F1 ValueError fix (preserved from v3)
- §2.4 B1 AST classifier (preserved from v3)
- §2.5 B2.a/b/c/d 4 scenarios + 9-column enumeration table (preserved from v3)
- §2.6 B3.1-B3.4 4 scenarios with γ-1 LOCK + B3.4 isolation mechanism (preserved from v4)
- §2.7 DB migration idempotency
- §3.1 9 mandatory pass criteria (preserved from v4)
- SEAL gate criteria substance

**v6 PFR-rule-Y SKIPPED per Charlie Path A register:** all 3 v6 fixes are mechanical literal substitutions of v5 PFR reviewer-stated fixes. Per [`feedback_reviewer_routing_subagent_default.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md) PFR-rule-Y SKIP criterion ("All adjudication outcomes were mechanical literal application of reviewer-stated fixes; Only deletions / mechanical fixes"), v6 re-review SKIP-eligible. Charlie Path A elected SKIP over Path B continued-rigor per cycle-final convergence already empirically confirmed at v5 PFR (both legs "no v6 finding predicted"). v6 is **CYCLE-FINAL RATIFY-READY**.

**v6 cycle-final cumulative observations (codified):**

5 PFR-rule-Y iterations completed (v1-v5):
- v1 PFR: 21 findings (4 BLOCKING + 5 HIGH + 4 MEDIUM + 8 LOW) — original sub-plan substantive review
- v2 PFR: 11 findings (2 BLOCKING + 3 HIGH + 3 MEDIUM + 3 LOW) — orchestrator Mode A discipline gap + plan v5 §10 cross-reference misreads caught
- v3 PFR: 6 findings (0 BLOCKING + 1 HIGH + 1 MEDIUM + 4 LOW) — Codex F1 BLOCKING B3.4 isolation caught Advisor own-anchoring blind spot
- v4 PFR: 6 findings (0 BLOCKING + 0 HIGH + 0 MEDIUM + 6 LOW) — both legs APPROVE-FOR-SUB-PLAN-RATIFY conditional on mechanical fixes
- v5 PFR: 3 findings (0 BLOCKING + 0 HIGH + 0 MEDIUM + 3 LOW) — both legs "no v6 finding predicted" cycle-final convergence

Cumulative reviewer dispatch count: 10 (2 legs × 5 iterations). Cumulative reviewer findings: 47 across 5 iterations (after dedup); 33 ADOPTed fixes (17 v1→v2 + 11 v2→v3 + 5 v3→v4 + 6 v4→v5 + 3 v5→v6); cumulative reviewer-discovered defects in this sub-plan arc = 47 surfaced + 33 adjudicated ADOPT.

3-layer safety architecture empirical reaffirmation across cycle:
- Layer 1 (Advisor own-anchoring discount): caught F-NEW-1 v2 PFR (B3.3 impossible) at her own v1 F9 rewrite territory; applied explicitly at every PFR round
- Layer 2 (Codex cross-model fresh-eye): caught F1 BLOCKING exception class + F1 BLOCKING B3.4 isolation + multiple HIGH at every iteration; load-bearing per B2 standing rule LOCKED 2026-05-19
- Layer 3 (Orchestrator Mode A re-verification): caught cf41b6a fabricated SHA at v1 drafting + multiple line-ref drifts at v3+v5 drafting; independent grep/Read on every reviewer specific claim

All 3 layers load-bearing throughout cycle; B2 standing rule + own-anchoring discount + Mode A discipline all empirically validated at iteration scale (5 rounds) within single sub-plan arc.

T1.4 sub-plan v6 CYCLE-FINAL RATIFY-READY: pending Charlie sub-plan ratify register.

---

**End of T1.4 sub-plan v6 (CYCLE-FINAL).** Awaiting Charlie sub-plan ratify register.
