# PHASE2C_12 Step 1 Deliverable — Q9/Q10 code-surface modifications

## §0 Document scope + register-class

Step 1 deliverable artifact at register-class-comparable to [`PHASE2C_11_STEP3_DELIVERABLE.md`](PHASE2C_11_STEP3_DELIVERABLE.md) precedent (substantive-implementation deliverable register; numerical/code anchors at register-precision register-binding). Records Step 1 implementation arc fire of [PHASE2C_12 sub-spec §3.3 + §4.1 + §4.2 + §8.1 Step 1](PHASE2C_12_PLAN.md) at code-register fire register.

Step 1 scope per sub-spec §8.1: Q9 (smoke theme override at proposer entry) + Q10 (`THEME_CYCLE_LEN` config-driven at engine entry) **only**. Step 2 (smoke batch fire 40 candidates 100% `multi_factor_combination`) is **out of this deliverable's scope** — sequenced for separate session per Charlie-register gate at smoke-fire boundary per Q5 LOCKED + [`feedback_authorization_routing.md`](../../) memory.

This deliverable is the **first code-register fire artifact at PHASE2C_12 cycle**. Sub-spec drafting cycle was text-register only; implementation arc Step 1 = first code commit + first Codex routing fire at PHASE2C_12 cycle per handoff §12.1.

---

## §1 Implementation summary

### §1.1 Commit register at Step 1 implementation arc

Per Q30 LOCKED + Charlie composite authorization (3 register-class-distinct commit boundaries: RED → Q9 → Q10) plus single-bundle Codex hotfix (Commit 4) per advisor + sub-spec author convergence on PHASE2C_11 Step 3 hotfix-3 register-precedent:

| # | SHA | Type | Surface |
|---|---|---|---|
| 1 | `38e012e` | TDD-RED | `tests/test_phase2c_12_theme_rotation.py` (new file; 160 lines; 4 test classes parametrized × 2 modules = 8 test instances) |
| 2 | `d46e24f` | Q9 implementation | `agents/proposer/stage2c_batch.py` + `agents/proposer/stage2d_batch.py` — `_theme_for_position` signature extension + R1 `ValueError` validation + `_resolve_smoke_theme_override()` helper + R2 caller-register threading |
| 3 | `cc4c056` | Q10 implementation | Same modules — `THEME_CYCLE_LEN = int(os.environ.get("PHASE2C_THEME_CYCLE_LEN", "5"))` at module-load register |
| 4 | `3543fab` | Codex first-fire hotfix bundle | `agents/proposer/interface.py` (BatchContext `theme_override` field) + `agents/proposer/prompt_builder.py` (override integration) + stage2c/stage2d (refined helper + `_resolve_theme_cycle_len()` validator + BatchContext threading + docstrings) + tests (+7 functions covering Findings #2 + #3 + #4) |

### §1.2 Files changed across Step 1 fire register

| File | Change scope |
|---|---|
| [`tests/test_phase2c_12_theme_rotation.py`](../../tests/test_phase2c_12_theme_rotation.py) | New file; 338 lines post-hotfix; 4 original test classes (TDD scope) + 7 new test functions (Codex hotfix scope) parametrized over both modules; total 43 test instances post-parametrization |
| [`agents/proposer/interface.py`](../../agents/proposer/interface.py) | (Hotfix Finding #1) Add `theme_override: str \| None = None` field to `BatchContext` frozen dataclass; field docstring explicit at register-class-clean separation from `theme_slot` |
| [`agents/proposer/prompt_builder.py`](../../agents/proposer/prompt_builder.py) | (Hotfix Finding #1) `build_prompt()` reads `context.theme_override`; when set, injects override into prompt-LLM-visible register; falls through to `_theme_for_slot(context.theme_slot)` otherwise |
| [`agents/proposer/stage2c_batch.py`](../../agents/proposer/stage2c_batch.py) | Q9: `_theme_for_position(k, theme_override=None)` + R1 ValueError + `_resolve_smoke_theme_override()` helper (refined post-Hotfix #2) + R2 caller threading at `run_stage2c()` (4 call sites threaded; BatchContext construction also threads `theme_override`). Q10: `_resolve_theme_cycle_len()` validator + module-load `THEME_CYCLE_LEN` (post-Hotfix #3 range bound). Module docstring updated (Hotfix #5) |
| [`agents/proposer/stage2d_batch.py`](../../agents/proposer/stage2d_batch.py) | Same surface for stage2d (2 call sites threaded including `_truncated_call` closure + BatchContext theme_override threading) |

---

## §2 Q9 implementation register

### §2.1 `_theme_for_position` signature extension

Per Q9 LOCKED at sub-spec §3.3 + §4.1 + Charlie R1 refinement:

```python
def _theme_for_position(
    k: int, theme_override: str | None = None,
) -> str:
    if theme_override is not None:
        if theme_override not in THEMES:
            raise ValueError(
                f"theme_override={theme_override!r} not in canonical "
                f"THEMES tuple {THEMES}"
            )
        return theme_override
    return THEMES[(k - 1) % THEME_CYCLE_LEN]
```

| Property | Verification |
|---|---|
| Signature backward-compat | Default `None` preserves existing call-site semantics; existing 67 proposer tests PASS |
| R1 validation enforced | Empty string + case-mismatched string + invalid theme name all raise `ValueError` (test #4 × 2 modules GREEN) |
| Function purity | No module-level mutable state; no env-var read inside function (R2 binding satisfied at function register) |

### §2.2 `_resolve_smoke_theme_override()` helper

Reads `PHASE2C_SMOKE_THEME_OVERRIDE` env var once at batch entry register. Returns the override theme name if set to non-empty string, otherwise `None`. Validation deferred to `_theme_for_position` (R3 fall-through preserves canonical rotation when env unset/empty).

### §2.3 Caller-register threading (R2 binding)

Per ChatGPT R2: env-var read at caller register, NOT inside the function. `run_stage2c()` and `run_stage2d()` resolve once after `_load_dotenv()`:

```python
_load_dotenv()
smoke_theme_override = _resolve_smoke_theme_override()
...
if smoke_theme_override is not None:
    print(f"[Stage 2X] smoke_theme_override={smoke_theme_override!r} "
          f"(PHASE2C_12 Q9 fire register)")
```

Threaded via `theme_override=smoke_theme_override` at all `_theme_for_position(...)` call sites:

| Module | Call sites threaded | Closure capture |
|---|---|---|
| `stage2c_batch.py` | 4 (main loop + 3 truncation/early-stop loops) | None (all sites in same function scope) |
| `stage2d_batch.py` | 2 (main loop + `_truncated_call` nested function) | `_truncated_call` captures `smoke_theme_override` via closure |

---

## §3 Q10 implementation register

### §3.1 `THEME_CYCLE_LEN` env-var-driven module-load read

Per Q10 LOCKED at sub-spec §3.3 + §4.2 + Charlie Q26 (env var) + Q27 (default=5):

```python
# Q10 LOCKED (PHASE2C_12_PLAN.md §3.3 + §4.2): THEME_CYCLE_LEN is
# config-driven via PHASE2C_THEME_CYCLE_LEN env var at module-load
# register; default = 5 preserves canonical Stage 2c/2d operational
# rotation invariant (multi_factor_combination excluded). PHASE2C_12
# main batch fire sets PHASE2C_THEME_CYCLE_LEN=6 explicitly at fire
# boundary to enable 6-theme rotation including multi_factor_combination
# (33 candidates × 6 themes = 198 clean integer distribution per Q6).
# Persistence decision register: post-PHASE2C_12 successor scoping cycle
# adjudication; default stays 5 at code register until explicitly
# adjudicated otherwise. See CLAUDE.md "Theme rotation operational
# boundary (Stage 2c/2d)" for canonical rationale.
THEME_CYCLE_LEN = int(os.environ.get("PHASE2C_THEME_CYCLE_LEN", "5"))
```

| Property | Verification |
|---|---|
| Default = 5 | `os.environ.get("PHASE2C_THEME_CYCLE_LEN", "5")` returns `"5"` if env unset; `int(...)` → 5 |
| `PHASE2C_THEME_CYCLE_LEN=6` enables 6-theme rotation | Test #2 × 2 modules verifies 33 × 6 = 198 distribution |
| Anti-momentum-binding | Default stays 5 at code register; persistence decision deferred to successor scoping cycle per Q10 LOCKED |
| Canonical Stage 2c/2d invariant preserved | Existing `test_stage2c_batch.test_theme_for_position_cycle_len_5` + `test_stage2d_batch.test_theme_for_position_200` PASS unchanged |

---

## §4 Test coverage register

### §4.1 Test file structure

[`tests/test_phase2c_12_theme_rotation.py`](../../tests/test_phase2c_12_theme_rotation.py) — 4 test classes parametrized over `MODULE_PATHS = ["agents.proposer.stage2c_batch", "agents.proposer.stage2d_batch"]` = **8 test instances**.

### §4.2 Test class coverage matrix

| # | Test | Coverage | Verification anchor |
|---|---|---|---|
| 1 | `test_theme_for_position_canonical_5theme_rotation` | R3 fall-through: unset env vars preserve canonical 5-theme rotation; `multi_factor_combination` NOT in default | Q10 default=5 + Stage 2c/2d invariant preservation |
| 2 | `test_theme_for_position_main_6theme_rotation` | Q10 PHASE2C_THEME_CYCLE_LEN=6 enables 6-theme rotation; 33 candidates × 6 themes = 198 clean distribution | Q10 functional + Q6 LOCKED 198 cardinality |
| 3 | `test_theme_for_position_smoke_override` | Q9 theme_override returns override regardless of `k` AND THEME_CYCLE_LEN (cross-product 5+6) | Q9 functional + Q9×Q10 cross-product |
| 4 | `test_theme_for_position_invalid_override_raises` | Q9 R1 validation: invalid override raises `ValueError` (case-sensitive + empty rejected) | Q9 R1 anti-fishing-license boundary |

### §4.3 Test infrastructure register

`reload_module` fixture pattern: `monkeypatch.delenv` both PHASE2C env vars on entry → yield reload-callable → restore canonical state on teardown via final `importlib.reload`. Cross-test contamination prevention at register-precision register-binding.

---

## §5 V#6 deferred verification register fire

Per canonical artifact §10.1 row #6 + handoff §7.5: V#6 DEFERRED at SEAL pre-fire; fires post-implementation-surface-exists at this Step 1 register.

### §5.1 V#6 verification dimensions (3 substantive checks)

| Check | Specification | Verification result |
|---|---|---|
| V#6.1 | Env var name = `PHASE2C_THEME_CYCLE_LEN` | ✅ confirmed at `stage2c_batch.py:104` + `stage2d_batch.py:123` |
| V#6.2 | Default value = `5` | ✅ `int(os.environ.get("PHASE2C_THEME_CYCLE_LEN", "5"))` returns 5 when env unset |
| V#6.3 | Module-load-time read at module-level constant | ✅ functional behavior: unset → 5, env=6 → 6, restore → 5 (3 register-class-distinct empirical checks) |

### §5.2 V#6 register-precision binding

Implementation surface satisfies Q10 LOCKED operationalization at register-precision register: env var name matches Q26 disposition; default value matches Q27 disposition; module-load-time read fires at module-level constant per "engine entry register" semantic in Q10 LOCKED.

V#6 register: **CLEAN at 3-substantive-check register-precision**.

---

## §6 TDD progression register

| State | Test result | Register transition |
|---|---|---|
| Pre-Commit-1 (canonical state) | N/A — test file does not exist | — |
| Post-Commit-1 (TDD-RED) | 6/8 FAIL, 2/8 PASS | Failure register confirms Q9 + Q10 not yet implemented; 2/8 PASS at canonical-5theme regression register (hardcoded `THEME_CYCLE_LEN=5` matches R3 fall-through trivially) |
| Post-Commit-2 (Q9 GREEN) | 6/8 PASS, 2/8 FAIL | Test #1 + #3 + #4 × 2 modules GREEN (Q9 + R1 + R3 functional); test #2 × 2 still FAIL (awaits Q10) |
| Post-Commit-3 (Q10 GREEN) | **8/8 PASS** | Test #2 × 2 modules GREEN (Q10 functional); full suite GREEN at Step 1 implementation register |
| Post-Commit-4 (Codex hotfix bundle GREEN) | **43/43 PASS** | +35 new test instances covering Findings #2 helper refinement (8 new) + Finding #3 range validation (24 parametrized) + Finding #4 prompt integration (3 new); all GREEN at substantive register-precision register |

---

## §7 Regression check register

Existing test suite execution post-Commit-3 at register-precision register:

| Suite | Pre-Step-1 | Post-Step-1 | Delta |
|---|---|---|---|
| `tests/test_evaluate_dsr.py` | 174 PASS | 174 PASS | 0 |
| `tests/test_wf_lineage_guard.py` | (included in 174 baseline) | (included) | 0 |
| `tests/test_stage2c_batch.py` | 67/67 PASS | 67/67 PASS | 0 |
| `tests/test_stage2d_batch.py` | (included in 67) | (included) | 0 |
| `tests/test_phase2c_12_theme_rotation.py` | (did not exist) | 43/43 PASS | +43 |
| `tests/test_proposer_interface.py` + `tests/test_proposer_prompt.py` | (not in narrow baseline) | 45/45 PASS | covered by broader scan |
| **Broader post-hotfix regression scan** | — | **286 existing tests + 43 PHASE2C_12 tests = 329 total PASS** | scope expansion register |

**No regression at existing test suite register**. Step 1 changes preserve canonical Stage 2c/2d operational rotation invariant at empirical state register. The 241-test "narrow baseline" (test_evaluate_dsr + test_wf_lineage_guard + test_stage2c_batch + test_stage2d_batch) was the pre-Step-1 reference scope; the broader 329-total post-hotfix scan adds `test_proposer_interface.py` + `test_proposer_prompt.py` (load-bearing for `BatchContext` field-addition + `build_prompt()` integration check) — all PASS unchanged.

---

## §8 Reviewer-trail register

### §8.1 Codex first-fire at code/spec interface

Per Q31 LOCKED + [`feedback_codex_review_scope.md`](../../) memory + PHASE2C_11 Step 3 register-precedent (8/8 findings cleared at `f2e4087` + hotfix-3 at `1b8132e`): Codex routing fires at code/spec interface register post-GREEN, pre-deliverable-seal.

| Property | Value |
|---|---|
| Codex CLI version | codex-cli 0.125.0 |
| Runtime mode | shared session runtime |
| Authentication | confirmed |
| Fire mode | background-mode + dual-channel ping at completion per [`feedback_long_task_pings.md`](../../) |
| Fire timing | post-Commit-3 GREEN, pre-Step-1-deliverable-seal |
| Findings artifact | [`/tmp/PHASE2C_12_STEP1_CODEX_REVIEW.md`](/tmp/PHASE2C_12_STEP1_CODEX_REVIEW.md) (transient at `/tmp` register; findings table folded into §8.2 below) |

### §8.2 Codex first-fire findings + dispositions

5 findings surfaced; per-finding adjudication per [`feedback_reviewer_suggestion_adjudication.md`](../../) at advisor + sub-spec author convergence; Charlie composite approval on convergence; all 5 ADOPTED (Finding #2 with PARTIAL refinement) at single-bundle hotfix Commit `3543fab`.

| # | Severity | Title | File:line (pre-hotfix) | Finding | Disposition | Patch surface (post-hotfix) |
|---|---|---|---|---|---|---|
| 1 | CRITICAL | Smoke override does not reach the actual proposer prompt theme | [`prompt_builder.py:196`](../../agents/proposer/prompt_builder.py#L196), `:218` + caller sites in stage2c/stage2d | `BatchContext.theme_slot` continued rotating through `_theme_for_slot()` regardless of Q9 override; smoke would NOT be 100% `multi_factor_combination` at LLM register; F7 verification + Component 1 cascade would fail | **ADOPT (α)** — explicit `theme_override` field at BatchContext over (β) theme_slot re-purpose | New field at [`interface.py:82`](../../agents/proposer/interface.py#L82) (frozen-dataclass field, default None); [`prompt_builder.py:196-205`](../../agents/proposer/prompt_builder.py#L196-L205) reads override-first / fall-through; threading at `BatchContext(...)` construction at stage2c/stage2d main-loop entry |
| 2 | HIGH | Empty smoke override env var silently disables Q9 | [`stage2c_batch.py:196-197`](../../agents/proposer/stage2c_batch.py) + stage2d analogues | `_resolve_smoke_theme_override()` returned `None` for both unset and empty/whitespace; R3 authorizes unset fall-through, NOT malformed-empty silent fall-through | **PARTIAL ADOPT** — distinguish unset (None) from set-empty/whitespace (raise ValueError) per sub-spec author refinement | Refined helper at stage2c/stage2d: explicit `is None` check for unset → return None; `not raw.strip()` → raise ValueError; non-empty → return verbatim |
| 3 | MEDIUM | `PHASE2C_THEME_CYCLE_LEN` has no range validation | [`stage2c_batch.py:104`](../../agents/proposer/stage2c_batch.py#L104) + [`stage2d_batch.py:123`](../../agents/proposer/stage2d_batch.py#L123) | Raw `int(...)` accepted zero, negative, > `len(THEMES)`, non-integer; failures landed mid-batch (late) rather than at module-load (early) | **ADOPT (broader bound)** — `1 <= n <= len(THEMES)` over Codex's `{5, 6}` per anti-pre-naming option (ii) carry-forward at validation register | New `_resolve_theme_cycle_len()` helper at stage2c/stage2d module-load: non-integer raises ValueError ("not a valid integer"); out-of-range raises ValueError ("out of range") |
| 4 | MEDIUM | Tests do not cover env helper or caller/prompt threading | [`tests/test_phase2c_12_theme_rotation.py:101,127,130,135,138`](../../tests/test_phase2c_12_theme_rotation.py) | Direct-only `_theme_for_position` tests missed register-class-eligibility-skip at prompt-LLM-visible register that Finding #1 surfaced | **ADOPT** — extends Finding #1 fix at integration register | +7 new test functions: `test_resolve_smoke_theme_override_*` (unset/empty/whitespace/valid × 2 modules); `test_theme_cycle_len_range_validation_*` (parametrized over bad/good values × 2 modules); `test_build_prompt_smoke_override_visible_in_prompt` + 2 companion integration tests at prompt register |
| 5 | LOW | Module docstrings still state fixed 5-theme rotation | `stage2c_batch.py:4,7,970` + `stage2d_batch.py:8,10` | Docstrings/comments implied unconditional `% 5` despite Q10 env-var-driven flexibility | **ADOPT** — stylistic at function-correctness register but substantive at audit-trail register | Module docstrings updated at stage2c/stage2d header (lines 1-19/1-23) to reflect "default 5; configurable to 6 via PHASE2C_THEME_CYCLE_LEN env var" + Q9 smoke override semantics |

**Substantive observation**: Finding #1 closes a §19 spec-vs-empirical-reality finding pattern instance — sub-spec drafting cycle authored Q9 LOCKED at "proposer entry register" without empirical verification of WHICH proposer-entry register controls LLM generation. Codex first-fire at code/spec interface caught at register-precision before Step 1 deliverable seal. Q31 LOCKED prevention discipline working correctly at register-class-distinct from M5/M6/M7 text-register reviewer pass cycle. Carry-forward observation logged at §9.

### §8.3 Per-finding adjudication discipline

Per [`feedback_reviewer_suggestion_adjudication.md`](../../): NO bulk-accept of Codex findings. For each finding:
1. State what Codex claims
2. Verify factual correctness against current code state (empirically verified Finding #1 at [`prompt_builder.py:196,218`](../../agents/proposer/prompt_builder.py#L196-L218))
3. Approve with rationale OR push back with rationale
4. Cite file:line + binding source at substantive register

Two-reviewer convergence on dispositions: sub-spec author + advisor 5/5 (1 ADOPT(α) + 1 PARTIAL ADOPT + 3 ADOPT). Charlie composite approval on convergence ratified the dispositions + single-bundle Commit 4 boundary + Codex re-fire authorization at substantive change-surface expansion register.

### §8.4 Codex re-fire register

Per advisor recommendation + sub-spec author convergence: Codex re-fire authorized at substantive change-surface expansion register (hotfix added BatchContext field + prompt_builder integration + new helper + range-validation + integration tests — all register-class-distinct from original first-fire scope).

| Property | Value |
|---|---|
| Re-fire trigger | Substantive change-surface expansion register-precision |
| Re-fire mode | Background-mode + dual-channel ping at completion per [`feedback_long_task_pings.md`](../../) |
| Re-fire scope | Hotfix patch correctness + 5 finding patch completeness verification + cross-cutting check |
| Re-fire artifact | First attempt (`task-mor5yjou-kuehla`): hung at 24m+ at scope-disambiguation deliberation phase (Codex paused on whether `STAGE2D_BATCH_SIZE=200` vs Q3 LOCKED N=198 belongs in re-fire scope; cancelled per Charlie (β) selection). Second attempt (`task-mp1...` agent `a94b76344ba034415` 4m 0s): completed cleanly with bounded scope prompt + 5-min budget. |
| Re-fire verdict | **APPROVE** — 0 hotfix findings; Step 1 deliverable seal cleared at register-precision register-binding |

### §8.5 Codex first-fire + re-fire cumulative verdict

**Composite verdict: APPROVE for Step 1 deliverable seal.**

| Phase | Findings | Disposition | Cumulative state |
|---|---|---|---|
| First-fire (`task-mor52zdt-6rzczy` at 4m 8s) | 5 findings (1 CRITICAL + 1 HIGH + 2 MEDIUM + 1 LOW) | All 5 ADOPTED at advisor + sub-spec author + Charlie 3-way convergence | Hotfix Commit `3543fab` patched all 5 |
| Re-fire #1 (`task-mor5yjou-kuehla` at 26m+ HUNG) | Partial — captured 3 interim positive observations (build_prompt sole surface; edge cases concrete; pytest GREEN inside Codex sandbox) before stalling at scope-disambiguation deliberation | Cancelled per Charlie (β) selection at hung-process register | Step-5-scope batch-size observation logged as §19 Instance #4 carry-forward at §9.4 |
| Re-fire #2 (scoped, 4m 0s) | **0 hotfix findings** — "Hotfix bundle clean for Step 1 deliverable seal. `theme_override` is defaulted, honored by `build_prompt()`, validated on the stage entry path, and covered by helper/range/prompt integration tests." | **APPROVE** at code/spec interface register-precision | Step 1 deliverable seal authorized at Codex register |

Codex re-fire #2 explicitly stated: "Verdict: APPROVE — Step 1 hotfix patches did not introduce a cited blocking defect within the bounded review scope." Carry-forward observation: `STAGE2D_BATCH_SIZE=200` at `stage2d_batch.py:118` per Step 5 scope (already logged at §9.4 Instance #4).

Per Q31 LOCKED + PHASE2C_11 Step 3 register-precedent (8/8 findings cleared at hotfix-3): Step 1 deliverable seal pre-fire register CLEAN at Codex routing register.

---

## §9 §19 spec-vs-empirical-reality finding observation register

Per [METHODOLOGY_NOTES §19](../discipline/METHODOLOGY_NOTES.md) + handoff §11 carry-forward register: cumulative-count register at next consolidation cycle.

PHASE2C_12 Step 1 implementation arc surfaced **2 §19 instances at register-class-distinct registers**:

### §9.0 Instance count register at PHASE2C_12 cycle

| Instance | Cycle/register | Description |
|---|---|---|
| Instance #1 (sub-spec drafting cycle) | V#7 Path A patch at sub-spec SEAL pre-fire register | PHASE2C_11 §4.4 edge-case filter wording propagated through handoff/sub-spec as "≥20 trades" (PHASE2C_8.1 audit_v1_filtered cohort framing); empirical canonical = `T_c < 5 EXCLUDED` per PHASE2C_11_PLAN §4.4 line 346 verbatim. Caught by SEAL pre-fire 9-empirical-verification fire BEFORE seal. |
| Instance #2 (Step 1 implementation arc) | Line-number drift at canonical artifact §10.1 V#6 row | See §9.2 below |
| Instance #3 (Step 1 Codex first-fire) | Q9 "proposer entry register" semantic ambiguity → prompt-LLM-visible register-class-eligibility-skip at sub-spec drafting cycle | See §9.3 below |
| Instance #4 (Step 1 Codex re-fire — partial output before hang) | `STAGE2D_BATCH_SIZE = 200` hardcoded vs Q3 LOCKED N=198 main batch register-precision mismatch | See §9.4 below |

PHASE2C_12 cumulative §19 instance count at Step 1 deliverable register: **4 instances**. PHASE2C_11 + PHASE2C_12 cumulative across cycles: **14 instances** (PHASE2C_11 = 10 per closeout MD §0.5 + Step 4 closeout entries; PHASE2C_12 = 4 at this register). Carry-forward to next methodology consolidation cycle for §19 cumulative-count register update.

### §9.2 Instance #2 — Line-number drift at canonical artifact §10.1 V#6 row

| Register | Cited (handoff §10.1 + canonical artifact §11.8) | Empirical (post-Q10 commit `cc4c056`) |
|---|---|---|
| `stage2c_batch.py` `THEME_CYCLE_LEN` line | 93 | **104** |
| `stage2d_batch.py` `THEME_CYCLE_LEN` line | 112 | **123** |
| `stage2c_batch.py` `_theme_for_position` line | 156-158 | **156-178** (signature extension at Q9 commit) |
| `stage2d_batch.py` `_theme_for_position` line | 198-200 | **198-220** (signature extension at Q9 commit) |

**Drift cause:** comment block expansion at Q9 commit (docstring extension on `_theme_for_position` + new `_resolve_smoke_theme_override()` helper) + Q10 commit (replacing 7-line trailing comment with 12-line preceding comment block + replacing hardcoded `5` with `int(os.environ.get(...))` literal).

**Defect class:** §19 spec-vs-empirical-reality finding pattern at empirical-line-citation register. Same defect class observed at PHASE2C_11 sub-spec drafting cycle (Instance #1-#4 cumulative per v3.2 §0.5) + Step 1 implementation arc (Instance #5-#7 per v3.1 `c021c60`) + Step 4 closeout (Instance #8-#10 per `7e41058` + `5dba0df`).

**Substantive impact:** non-blocking observation at content register. Functional behavior verified CLEAN at V#6 (§5 above); line-number citations are descriptive metadata, not load-bearing at functional-correctness register. Sub-spec canonical artifact citations remain authoritative at register-class scope; specific line numbers are advisory at audit-trail-precision register.

**Routing:** descriptive register only at this deliverable; carry-forward to next methodology consolidation cycle.

### §9.3 Instance #3 — "Proposer entry register" semantic ambiguity (Codex Finding #1)

**Defect:** Sub-spec drafting cycle authored Q9 LOCKED (PHASE2C_12_PLAN.md §3.3 line 205 + §4.1 line 301) at "proposer entry register" semantic without empirically verifying which proposer-entry register substantively binds at LLM-generation control register. Two register-class-distinct candidates existed:

- **Telemetry register** — `_theme_for_position()` return value flowing into `call_summary` records (what was generated)
- **Prompt-LLM-visible register** — `BatchContext.theme_slot` flowing through `build_prompt()` → `_theme_for_slot()` (what controls generation)

Q9 LOCKED at sub-spec drafting cycle text-register implicitly bound only the telemetry register; the prompt-LLM-visible register binding was substantively load-bearing but register-class-eligibility-skipped.

**Defect class:** §19 spec-vs-empirical-reality finding pattern at sub-spec drafting cycle text-register scope vs implementation arc code-register scope.

**Reviewer-pass register-class-eligibility-skip:** M5 ChatGPT structural overlay + M6 advisor full-prose-access + M7 fresh-register full-file pass at sub-spec drafting cycle text-register all CLEAN; NONE substantively bound at "WHICH proposer-entry register controls LLM-generation" register-precision. Codex first-fire at code/spec interface (Q31 LOCKED prevention discipline) caught at register-precision register-class-distinct from text-register reviewer pass cycle.

**Substantive impact:** if smoke fired without Hotfix Commit 4: smoke batch generates rotating-theme candidates (NOT 100% `multi_factor_combination`); F7 verification fails at empirical register; Component 1 axis selection cascade fails at register-precision; Component 4 Check #4 multi_factor_combination verification fires false-CLEAN at register-precision register-violating. Codex first-fire prevention discipline substantively load-bearing at Q31 register.

**Routing:** descriptive register only at this deliverable; carry-forward to next methodology consolidation cycle as concrete instance of methodology refinement candidate "WHICH reviewer pass at WHICH register" (register-class-distinct from existing METHODOLOGY_NOTES §16 sub-rule "WHO reads prose at WHICH register"). M5/M6/M7 reviewer pass cycle bounded at sub-spec drafting cycle text-register scope; Codex first-fire bounded at implementation arc code-register scope; both load-bearing at register-class-distinct prevention discipline.

### §9.4 Instance #4 — `STAGE2D_BATCH_SIZE = 200` vs Q3 LOCKED N=198 (Step 5 scope carry-forward)

**Defect (observed but Step-1-out-of-scope):** Codex re-fire (first attempt) captured a partial assistant message at `12:17:58.675Z` before stalling: "I also found a broader execution-surface issue around PHASE2C_12's 198-candidate main-batch promise that is not in the prompt-builder patch itself, so I'm verifying whether it belongs in this re-fire scope before writing the report."

The substantive observation: [`stage2d_batch.py:107`](../../agents/proposer/stage2d_batch.py#L107) hardcodes `STAGE2D_BATCH_SIZE = 200`. PHASE2C_12 main batch fire requires N=198 per Q3 LOCKED at sub-spec §3.2. The two values mismatch at register-precision register-binding.

**Defect class:** §19 spec-vs-empirical-reality finding pattern at sub-spec drafting cycle text-register scope vs implementation arc code-register scope (parallel register-class to Instance #3).

**Scope boundary:** **Step 5 (main batch fire) scope, NOT Step 1 (Q9/Q10 code-surface modifications) scope** per sub-spec §8.1 sequencing. Step 1 deliverable register-class-eligibility-bound at theme-rotation surface only; batch-size config mechanism is register-class-distinct surface to be addressed at Step 5 fire-prep register.

**Substantive impact:** if Step 5 main batch fired without addressing the mismatch: stage2d would loop 200 times instead of 198; theme distribution would be 33+33+33+33+33+34 (last theme +1) instead of clean 33×6=198. Cardinality at Component 4 verification check would still satisfy `33 ± 2` per Q11 LOCKED tolerance, but the canonical-baseline-relative comparison register would be off-by-2 at register-precision register-binding.

**Remediation register-class-eligible (Step 5 scope, NOT Step 1):** add `PHASE2C_BATCH_SIZE` env var override or similar config-driven batch-size parameter at Step 5 fire-prep register, parallel to Q10 `PHASE2C_THEME_CYCLE_LEN` mechanism. Pre-Step-5 implementation should adjudicate via separate sub-spec or scope-extension authorization.

**Routing:** descriptive register only at this deliverable; explicitly **carry-forward to Step 5 fire-prep register** at PHASE2C_12 implementation arc continuation. Tracked as Step 5 prerequisite register-class-distinct from Step 1 deliverable seal scope.

---

## §10 Compliance audit at this deliverable register

### §10.1 CLAUDE.md compliance

| Rule | Compliance |
|---|---|
| Theme rotation operational boundary (Stage 2c/2d) | ✅ Default `THEME_CYCLE_LEN=5` preserves canonical 5-theme rotation; 6th theme `multi_factor_combination` flip is config-override-only at PHASE2C_12 fire boundary |
| Approved core libraries | ✅ No new dependencies introduced; only stdlib (`os`, `importlib` for tests) + existing `pytest` |
| Timestamp & timezone rules | N/A — no timestamp surfaces touched |
| Coding standards (type hints + docstrings + UTC) | ✅ `_theme_for_position` + `_resolve_smoke_theme_override` + tests have full type hints + docstrings citing binding source |

### §10.2 `~/.claude/rules/*` compliance

| Rule file | Compliance |
|---|---|
| `coding-style.md` (PEP 8 + type annotations) | ✅ Type hints on all signatures; PEP 8 line-length preserved; immutability of THEMES tuple preserved |
| `testing.md` (TDD-first + pytest) | ✅ TDD-RED commit before any implementation; pytest framework; happy path + edge cases (empty string, case-mismatch, invalid theme name) |
| `git-workflow.md` (conventional commits) | ✅ Commit messages: `test(phase2c-12): TDD-RED`, `feat(phase2c-12): Q9 ...`, `feat(phase2c-12): Q10 ...` |
| `security.md` (no hardcoded secrets) | ✅ No new env vars contain secrets; `PHASE2C_THEME_CYCLE_LEN` + `PHASE2C_SMOKE_THEME_OVERRIDE` are non-secret config flags |
| `trading-safety.md` | N/A — no order placement or risk-limit changes at this register-class |

### §10.3 PHASE2C_12_PLAN.md sub-spec compliance

| Q-LOCKED disposition | Implementation surface | Compliance |
|---|---|---|
| Q9 (smoke theme override at proposer entry) | `_theme_for_position(k, theme_override=None)` + caller threading | ✅ |
| Q10 (THEME_CYCLE_LEN config-driven at engine entry) | `int(os.environ.get("PHASE2C_THEME_CYCLE_LEN", "5"))` at module-load | ✅ |
| Q26 (env var mechanism) | `PHASE2C_THEME_CYCLE_LEN` env var | ✅ |
| Q27 (default = 5) | Default = 5 preserves canonical rotation invariant | ✅ |
| Q28 (function-signature + caller env-var read) | Function param `theme_override=None` + R2 caller threading at `run_stage2c`/`run_stage2d` | ✅ |
| Q29 (4 test classes + 8 instances) | Parametrized over both modules; R3 fall-through assertion explicit | ✅ |
| Q30 (3-commit register-class-distinct boundaries) | RED → Q9 → Q10 commits | ✅ |
| Q31 (Codex pre-deliverable-seal) | Background fire post-GREEN, pre-seal | ✅ |

---

## §11 What this deliverable does NOT do

Per (α) strict-canonical scope adjudication discipline at sub-spec §8.1 Step 1 scope:

1. **Does NOT fire smoke batch.** Step 2 = smoke fire (40 candidates, 100% `multi_factor_combination`); requires separate Charlie-register authorization at smoke-fire boundary per Q5 LOCKED. Smoke fire = first $-spend at PHASE2C_12 cycle (~$0.46 estimate per handoff §12.2); operational fire register-class-distinct from this code-modification register.
2. **Does NOT fire main batch.** Step 5 = main fire (198 candidates, uniform 6/6 rotation); conditional on smoke PASS + Charlie-register authorization at smoke-vs-main boundary.
3. **Does NOT re-purpose `theme_slot` semantics**. Codex first-fire Finding #1 (CRITICAL) revealed that an explicit `theme_override` field at `BatchContext` is load-bearing at the prompt-LLM-visible register (NOT just descriptive telemetry as pre-Codex framing assumed). The (α) implementation surface adopted at Hotfix Commit 4 adds a new `theme_override: str \| None = None` field to `BatchContext` while preserving `theme_slot` as pure rotation-position metadata — register-class-clean separation between telemetry (`theme_slot`) and control (`theme_override`). The (β) alternative (re-purposing `theme_slot` to point to override theme's index) was rejected at sub-spec author + advisor convergence: it collapses two register-classes into one field at register-precision register-violating semantics, and loses rotation-position telemetry under override.
4. **Does NOT update CLAUDE.md "Theme rotation operational boundary"** canonical wording. Default `THEME_CYCLE_LEN=5` at code register preserves operational invariant; CLAUDE.md wording remains accurate at default-state register. Successor scoping cycle adjudicates persistence + canonical-wording revision per Q10 LOCKED.
5. **Does NOT advance Phase Marker** beyond Step 1 scope. Phase Marker advance commit fires at Step 1 deliverable seal register-class-distinct from implementation arc fire register; specific Phase Marker wording adjudicated at deliverable seal commit boundary.

---

## §12 Anchors

### §12.1 PHASE2C_12 cross-references

- [`docs/phase2c/PHASE2C_12_PLAN.md`](PHASE2C_12_PLAN.md) — sub-spec sealed at `b8e4972`; §3.3 Q9 + Q10 LOCKED + §4.1 + §4.2 + §8.1 Step 1 sequenced steps
- [`docs/phase2c/PHASE2C_12_SCOPING_DECISION.md`](PHASE2C_12_SCOPING_DECISION.md) — scoping decision sealed at `541c0be`; §4.4 arc designation = breadth expansion arc

### §12.2 PHASE2C_11 cross-references (register-precedent)

- [`docs/phase2c/PHASE2C_11_STEP3_DELIVERABLE.md`](PHASE2C_11_STEP3_DELIVERABLE.md) — Step 3 deliverable sealed at `6315ec0`; structural-template register for this Step 1 deliverable
- [`docs/closeout/PHASE2C_11_RESULTS.md`](../closeout/PHASE2C_11_RESULTS.md) — closeout MD sealed at `5dba0df`; canonical-basis comparison anchor for PHASE2C_12 §6 evaluation register

### §12.3 Code module cross-references

- [`agents/themes.py`](../../agents/themes.py) — canonical `THEMES` tuple (6 themes; `multi_factor_combination` 6th)
- [`agents/proposer/stage2c_batch.py`](../../agents/proposer/stage2c_batch.py) — Q9 + Q10 implementation surface (stage2c)
- [`agents/proposer/stage2d_batch.py`](../../agents/proposer/stage2d_batch.py) — Q9 + Q10 implementation surface (stage2d)
- [`tests/test_phase2c_12_theme_rotation.py`](../../tests/test_phase2c_12_theme_rotation.py) — Step 1 test coverage at TDD-GREEN register

### §12.4 Discipline cross-references

- [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) §16 + §17 + §19 — anchor-prose-access discipline + procedural-confirmation defect class + spec-vs-empirical-reality finding pattern

### §12.5 Memory cross-references

- [`feedback_authorization_routing.md`](../../) — Charlie-register gate at every operational fire boundary
- [`feedback_reviewer_suggestion_adjudication.md`](../../) — per-finding adjudication discipline at Codex routing register
- [`feedback_codex_review_scope.md`](../../) — Codex routing scope at substantive code/work register
- [`feedback_long_task_pings.md`](../../) — dual-channel ping at SEAL fire boundary
- [`feedback_use_planning_skills_for_complex_tasks.md`](../../) — Step 1 implementation arc as planning-skill instance precedent

---

**End of PHASE2C_12 Step 1 Deliverable v1 — Codex first-fire + re-fire APPROVE; awaiting Charlie-register seal authorization at Step 1 deliverable seal commit + Phase Marker advance + push + dual-channel ping boundary.**
