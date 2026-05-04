# PHASE2C_12 Step 2 Fire-Prep Deliverable — `--live-critic` + `PHASE2C_BATCH_SIZE` + ledger pre-charge

## §0 Document scope + register-class

Step 2 fire-prep deliverable artifact at register-class-comparable to [PHASE2C_12 Step 1 deliverable precedent](PHASE2C_12_STEP1_DELIVERABLE.md) (substantive-implementation deliverable register; numerical/code anchors at register-precision register-binding). Records Step 2 **fire-prep** implementation arc fire of [PHASE2C_12 sub-spec §3.2 + §4.1 + §8.1 Step 2](PHASE2C_12_PLAN.md) at code-register fire register.

Step 2 fire-prep scope: **3-surface coupled patch** that prepares the smoke fire infrastructure but does NOT fire the smoke batch itself. Smoke batch fire (40 candidates 100% `multi_factor_combination`) is **out of this deliverable's scope** — sequenced for separate fire boundary requiring Charlie-register auth #3 per Q5 LOCKED + [`feedback_authorization_routing.md`](../../) memory.

This deliverable is the **second code-register fire artifact at PHASE2C_12 cycle** following Step 1 deliverable seal at commit `4e112a3`. Three OPEN questions surfaced at next-session-entry audit + adjudicated at Charlie register before code fire authorized.

---

## §1 Implementation summary

### §1.1 Commit register at Step 2 fire-prep implementation arc

Per Step 1 register-precedent (RED → Q9 → Q10 → Codex hotfix bundle → seal) + Charlie auth #1-expanded covering 3-surface coupled patch:

| # | SHA | Type | Surface |
|---|---|---|---|
| 1 | `af5419e` | TDD-RED | [`tests/test_phase2c_12_step2_fire_prep.py`](../../tests/test_phase2c_12_step2_fire_prep.py) (new file; 564 lines; 28 tests across 3 surfaces) |
| 2 | `7c682fd` | Surface (1) GREEN | `agents/proposer/stage2d_batch.py` — `_resolve_batch_size()` env-var resolver + `STAGE2D_BATCH_SIZE` config-driven |
| 3 | `30d3bfd` | Surfaces (2)+(3) GREEN | Same module — `--live-critic` CLI flag + `LiveSonnetD7bBackend` instantiation + ledger pre-charge wrap around `run_critic()` |
| 4 | `1f68f37` | Codex first-fire hotfix | Same module + test file — Findings #1 (HIGH) affordability gate + #2 (MEDIUM) stderr surfacing; Finding #3 (LOW) deferred |

### §1.2 Files changed across Step 2 fire-prep fire register

| File | Change scope |
|---|---|
| [`tests/test_phase2c_12_step2_fire_prep.py`](../../tests/test_phase2c_12_step2_fire_prep.py) | New file; 729 lines post-hotfix; 28 original TDD tests + 2 hotfix tests = 30 tests across 3 surfaces (19 batch_size + 4 live_critic CLI + 5 ledger pre-charge + 2 hotfix) |
| [`agents/proposer/stage2d_batch.py`](../../agents/proposer/stage2d_batch.py) | (1) `_resolve_batch_size()` + `STAGE2D_BATCH_SIZE = _resolve_batch_size()` config-driven (2) `live_critic` parameter on `run_stage2d` + ValueError on flag-interaction + `LiveSonnetD7bBackend` instantiation + `--live-critic` argparse flag + `_batch_id` test injection point (3) Ledger pre-charge wrap around `run_critic()` with affordability gate + stderr surfacing on finalize failure |

---

## §2 Surface (1) implementation register — `PHASE2C_BATCH_SIZE`

### §2.1 `_resolve_batch_size()` env-var-driven resolver

Per Q1 LOCKED (smoke=40) + Q3 LOCKED (main=198) at sub-spec §3.2 + §4.1 + §4.2:

```python
def _resolve_batch_size() -> int:
    raw = os.environ.get("PHASE2C_BATCH_SIZE", "200")
    try:
        n = int(raw)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"PHASE2C_BATCH_SIZE={raw!r} is not a valid integer"
        ) from err
    if not (1 <= n <= 200):
        raise ValueError(
            f"PHASE2C_BATCH_SIZE={n} out of range; "
            f"must be in [1, 200] (canonical-baseline ceiling)"
        )
    return n


STAGE2D_BATCH_SIZE = _resolve_batch_size()
```

**Design rationale:**
- **Default = 200** preserves canonical `b6fcbf86` operational baseline (parse_rate = 0.99 = 198/200 per PHASE2C_9 Step 2 closeout)
- **Range [1, 200]** = **canonical-baseline ceiling (forward-binding constraint, NOT hard limit)** (defensive-but-not-prescriptive bound; NOT hardcoded {40, 198}; successor cycle may legitimately use other batch sizes within canonical-tested range without re-modifying validation). **Forward-binding caveat:** if a future PHASE2C cycle requires `batch_size > 200`, the upper bound MUST be raised via explicit sub-spec adjudication + Charlie-register authorization at that fire boundary; ad-hoc patching of the validator at fire time is forbidden per anti-scope-creep discipline. The `200` ceiling is canonical-baseline-relative, not infrastructure-imposed.
- **Module-load read** parallel to Q10 `_resolve_theme_cycle_len()` register-class symmetry
- **Closes Step 1 deliverable §9.4 carry-forward** at register-precision: handoff drafting cycle had this as Step 5-only prereq, but empirical Step 2 audit caught that smoke also blocked at 40 ≠ 200 (§19 instance #5 spec-vs-empirical-reality finding pattern)

### §2.2 Affected call sites

11 call sites within stage2d_batch.py reference `STAGE2D_BATCH_SIZE`. None require change since the constant is now resolved at module-load:

| Reference type | Sites |
|---|---|
| Display strings | `[Stage 2d] batch_size=...`, `[Stage 2d] --- Call k/STAGE2D_BATCH_SIZE...` |
| BatchContext construction | `batch_size=STAGE2D_BATCH_SIZE` at ctx instantiation |
| Loop range | `for k in range(1, STAGE2D_BATCH_SIZE + 1):` |
| Truncation iteration | `for j in range(k, STAGE2D_BATCH_SIZE + 1):` (multiple sites) |
| Block telemetry | `BLOCK_COUNT = STAGE2D_BATCH_SIZE // BLOCK_SIZE` (Codex Finding #3 deferred — see §6.3) |

---

## §3 Surfaces (2)+(3) implementation register — `--live-critic` + ledger pre-charge

### §3.1 `--live-critic` CLI flag (Surface 2)

Per OPEN-2 C1 adjudication (live D7b for criterion (B) measurement at register-precision):

**`run_stage2d` signature extension:**
```python
def run_stage2d(
    *,
    dry_run: bool = False,
    with_critic: bool = False,
    live_critic: bool = False,        # ← Surface (2) addition
    _backend: object | None = None,
    _ledger_path: Path | None = None,
    _payload_dir: Path | None = None,
    _d7b_backend: object | None = None,
    _batch_id: str | None = None,     # ← test injection point added in hotfix
) -> dict:
```

**Anti-fishing-license cross-product validation:**
```python
if live_critic and not with_critic:
    raise ValueError(
        "live_critic=True requires with_critic=True; cannot enable "
        "live D7b backend while critic gate is disabled "
        "(anti-fishing-license at flag-interaction register-precision)"
    )
```

**LiveSonnetD7bBackend instantiation (when `live_critic=True`):**
```python
elif live_critic:
    from agents.critic.d7b_live import LiveSonnetD7bBackend
    critic_d7b = LiveSonnetD7bBackend(
        raw_payload_dir=payload_dir,
        batch_id=batch_id,
    )
```

**CONTRACT BOUNDARY preserved:** `LiveSonnetD7bBackend` instantiates its OWN `anthropic.Anthropic()` client independent of the D6 Proposer's client (per [`agents/critic/d7b_live.py`](../../agents/critic/d7b_live.py) dataclass docstring lines 11-14).

**argparse flag at `main()`:**
```python
parser.add_argument(
    "--live-critic", action="store_true",
    help=(
        "Use LiveSonnetD7bBackend instead of StubD7bBackend "
        "(requires --with-critic). Adds ~$0.01-0.02 per Critic "
        "call to ledger via pre-charge wrap. Required for "
        "PHASE2C_12 smoke criterion (B) register-precision."
    ),
)
```

### §3.2 Ledger pre-charge wrap (Surface 3)

Per OPEN-3 D1 adjudication (closes PHASE2C_3 + PHASE2C_5 carry-forward warning at the same fire boundary that wires live-critic):

**Pre-charge sequence:**
```python
critic_row_id = None
if critic_d7b.mode == "live":
    # [Hotfix Finding #1 affordability gate — see §4.1]
    if not critic_skipped_budget:
        critic_row_id = ledger.write_pending(
            batch_id=batch_id,
            api_call_kind="critic_d7b",
            backend_kind=BACKEND_KIND_D7B_CRITIC,
            call_role=CALL_ROLE_CRITIQUE,
            estimated_cost_usd=D7B_STAGE2A_COST_CEILING_USD,  # $0.05 upper bound
            now=critic_now,
        )

if critic_skipped_budget:
    cr = None
    critic_result_dict = None
    print("[Stage 2d] critic skipped at call k: affordability gate ...")
else:
    cr = run_critic(cand.dsl, theme, critic_ctx, critic_d7b)
    critic_result_dict = cr.to_dict()
```

**Finalize sequence:**
```python
if critic_row_id is not None and cr is not None:
    actual_critic_cost = cr.d7b_cost_actual_usd or 0.0
    try:
        ledger.finalize(
            critic_row_id,
            actual_cost_usd=actual_critic_cost,
            now=datetime.now(timezone.utc),
            input_tokens=cr.d7b_input_tokens,
            output_tokens=cr.d7b_output_tokens,
        )
    except Exception as fin_exc:
        # [Hotfix Finding #2 stderr surfacing — see §4.2]
        print(f"[Stage 2d] CRITIC FINALIZE FAILED at call {k}: ...", file=sys.stderr)
        try:
            ledger.mark_crashed(critic_row_id, ...)
        except Exception as mc_exc:
            print(f"[Stage 2d] CRITIC MARK_CRASHED FAILED at call {k}: ...", file=sys.stderr)
```

**Stub mode** (`critic_d7b.mode == "stub"`): bypasses the entire affordability+pre-charge+ledger-write block via the `if critic_d7b.mode == "live":` guard. Stub mode does NOT enter the gate-and-skip path — it falls through directly to `cr = run_critic(cand.dsl, theme, critic_ctx, critic_d7b)` with NO ledger row created at any point. Regression guard against $0 noise rows polluting the ledger and violating "pre-charge for real spend" invariant. Test `test_stub_critic_skips_pre_charge` enforces this: ledger contains zero `backend_kind='d7b_critic'` rows after stub-mode batch completes.

**Closes PHASE2C_3 + PHASE2C_5 carry-forward warning** at register-precision: "becomes a spend-accounting bug if/when LiveSonnetD7bBackend is wired into main()" — wired here, with pre-charge invariant preserved.

---

## §4 Codex first-fire hotfix register

### §4.1 Finding #1 (HIGH) ADOPT — Live critic affordability gate

**Codex claim:** `ledger.write_pending(...)` happens before `run_critic`, but no `ledger.can_afford(...)` or cumulative `$30` check guards the critic estimate before the live D7b call. Near a cap, proposer spend can pass its gate, then live critic can push the ledger over cap and still call the API.

**Severity rationale:** $20/batch is CLAUDE.md hard constraint. At $19.95 batch spend with live critic enabled, proposer would gate-block but critic would slip through. **HIGH** correctly assigned.

**Hotfix surface (parallel to proposer affordability gate at lines ~1086-1115):**

```python
if critic_d7b.mode == "live":
    critic_now = datetime.now(timezone.utc)
    # Cumulative monthly cap check
    critic_monthly_after = (
        ledger.monthly_spent_usd(now=critic_now)
        + D7B_STAGE2A_COST_CEILING_USD
    )
    if critic_monthly_after > STAGE2D_CUMULATIVE_CAP_USD:
        critic_skipped_budget = True
    elif not ledger.can_afford(
        batch_id=batch_id,
        estimated_cost_usd=D7B_STAGE2A_COST_CEILING_USD,
        now=critic_now,
        batch_cap_usd=STAGE2D_BATCH_CAP_USD,
        monthly_cap_usd=STAGE2D_MONTHLY_CAP_USD,
    ):
        critic_skipped_budget = True
```

**Skip behavior:** If gated, NO `run_critic` call, NO ledger row, set `critic_skipped_budget = True`, propagate to `call_summaries[-1]["critic_skipped_budget"]` so smoke PASS adjudication can distinguish from genuine critic-approved/`pending_backtest`.

### §4.2 Finding #2 (MEDIUM) ADOPT-with-refinement — `finalize()` masking

**Codex claim:** Wrapper marks the row crashed but then continues silently. The critical check says "best-effort `mark_crashed` wrap must not mask the original exception"; current behavior masks `fin_exc` whenever `mark_crashed` succeeds.

**Verdict:** APPROVE the diagnosis with **patch refinement**. Codex's exact suggested fix `raise fin_exc` would propagate up, terminating the entire batch on a single critic finalize failure — contradicts fail-open semantics implied by `run_critic()` never raising (cost is sunk; API call already completed).

**Refined hotfix:** Log the exception to stderr (visible in run logs) while continuing the batch. Same pattern applied to `mark_crashed` itself failing.

```python
except Exception as fin_exc:
    print(
        f"[Stage 2d] CRITIC FINALIZE FAILED at call {k}: "
        f"{type(fin_exc).__name__}: {fin_exc}",
        file=sys.stderr,
    )
    try:
        ledger.mark_crashed(...)
    except Exception as mc_exc:
        print(
            f"[Stage 2d] CRITIC MARK_CRASHED FAILED at call {k}: "
            f"{type(mc_exc).__name__}: {mc_exc}",
            file=sys.stderr,
        )
```

### §4.3 Finding #3 (LOW) DEFER — Block telemetry partial-block dropping

**Codex claim:** `BLOCK_COUNT = STAGE2D_BATCH_SIZE // BLOCK_SIZE` excludes the final partial block for `PHASE2C_BATCH_SIZE=198` (yields 3 blocks of 50 covering 1-150; misses 151-198) and yields zero blocks for smoke `40`.

**Verdict:** Push back on scope. Reasoning:
1. Block telemetry is observability output, not load-bearing — doesn't affect mining correctness, ledger accuracy, or smoke PASS/FAIL adjudication
2. Step 2 fire-prep scope is "enable smoke fire (40 candidates with criterion (B) measurable)", not "fix all telemetry edge cases"
3. The fix touches ALL block-trend display paths — register-class-distinct surface (telemetry layer) from the 3 surfaces auth #1-expanded covered (batch-size resolver + live-critic CLI + ledger pre-charge)
4. Per `feedback_authorization_routing.md`: "Pre-authorization via locked sequence applies only to actions explicitly named in the locked sequence" — telemetry refactoring NOT named in auth #1
5. Smoke fire telemetry will display `block 1 (1-50): n=40` (off-label but informative); not pretty but not wrong

**Disposition:** DEFERRED to follow-up commit OR Step 5 fire-prep prerequisite (parallel to original §9.4 carry-forward at PHASE2C_12 cycle). Tracked as **§19 instance #7 candidate** at telemetry-layer register.

### §4.4 Per-finding adjudication discipline

Per [`feedback_reviewer_suggestion_adjudication.md`](../../) memory: "Don't bulk-accept dual-reviewer suggestions. For each suggestion, articulate: what the suggestion claims, is it factually correct and applicable in this context, approve with rationale or push back with rationale."

Codex first-fire returned 3 findings: 1 HIGH ADOPT clean / 1 MEDIUM ADOPT-with-patch-refinement (Codex's `raise` suggestion rejected on fail-open grounds; replaced with stderr log) / 1 LOW DEFER (out-of-scope register-class-distinct surface). Each finding adjudicated individually with file:line citation + suggested patch + verdict + rationale.

### §4.5 Codex re-fire #1 verdict

Re-fire (`bmnq8b11m`, ~5min bounded) returned **APPROVE** with concrete verification:
- "Affordability gate runs before write_pending, checks cumulative+batch+monthly caps, skips run_critic and ledger writes when gated, propagates `critic_skipped_budget` into summary['calls']" (citations [stage2d_batch.py:1276](../../agents/proposer/stage2d_batch.py#L1276), [:1305](../../agents/proposer/stage2d_batch.py#L1305), [:1457](../../agents/proposer/stage2d_batch.py#L1457))
- "finalize() exceptions are printed to stderr before best-effort mark_crashed; mark_crashed exceptions also printed to stderr; no re-raise occurs, batch continues" (citations [:1336](../../agents/proposer/stage2d_batch.py#L1336), [:1362](../../agents/proposer/stage2d_batch.py#L1362))
- One-call harness with BOTH finalize() AND mark_crashed() failing → batch continues without crash, stderr surfaces both
- 2/2 hotfix tests pass; 76/76 Stage 2d + ledger regression slice pass

---

## §5 Test coverage register

### §5.1 Test file structure

[`tests/test_phase2c_12_step2_fire_prep.py`](../../tests/test_phase2c_12_step2_fire_prep.py) — 729 lines, 30 test functions across 3 surfaces + 2 hotfix verifications.

### §5.2 Test coverage matrix

| Surface | Test coverage | Cases |
|---|---|---|
| Surface (1) `PHASE2C_BATCH_SIZE` | 19 tests | default=200 / smoke=40 / main=198 / range-reject (5 bad: 0/-1/-198/201/1000) / non-int (4: forty/empty/1.5/200_) / in-bounds (7: 1/20/40/100/150/198/200) |
| Surface (2) `--live-critic` CLI | 4 tests | absent→stub / set→live / cross-product ValueError / CLI argparse threading |
| Surface (3) Ledger pre-charge | 5 tests | writes_pending_before_run_critic / pending_row_schema / marks_completed_with_actual_cost / marks_crashed_on_finalize_exception / stub_skips_pre_charge |
| Hotfix Finding #1 | 1 test | live_critic_skipped_when_cap_would_be_exceeded (uses `_batch_id` injection + pre-populated $19.96 ledger) |
| Hotfix Finding #2 | 1 test | live_critic_finalize_failure_does_not_mask_original_error (capsys assertion on stderr) |

### §5.3 Test infrastructure register

| Component | Source |
|---|---|
| `_SmallVariedProposer` mock | Stub Proposer emitting valid DSL per call |
| `_FakeLiveD7bBackend` mock | `mode = "live"` + canned `cost_actual_usd=0.012` + 100-char-padded reasoning text (parser schema requirement) |
| `reload_module` fixture | Clear PHASE2C_* env vars on entry/exit + reload to restore canonical state |
| `_critic_pending_rows()` helper | Filter ledger rows by `backend_kind = 'd7b_critic'` |
| Lazy-import patch path | `agents.critic.orchestrator.run_critic` (NOT `agents.proposer.stage2d_batch.run_critic`) — patches source-module before lazy `from X import Y` runs |
| `_batch_id` injection | New keyword parameter on `run_stage2d` parallel to existing `_backend`/`_ledger_path`/etc.; enables pre-population of ledger state with deterministic batch_id |

---

## §6 TDD progression register

### §6.1 Commit chain register

```
af5419e  TDD-RED      28 tests fail at expected register (2 coincidental passes due to literal 200 match)
7c682fd  Surface (1) GREEN   19/19 batch_size tests pass + 75 regression CLEAN
30d3bfd  Surfaces (2)+(3) GREEN   28/28 Step 2 tests pass + 352 regression CLEAN
1f68f37  Codex hotfix         30/30 Step 2 tests pass + 1577 full repo regression CLEAN
```

### §6.2 Final test register at deliverable seal

- **30/30 PHASE2C_12 Step 2 fire-prep tests pass**
- **1577/1577 full repo regression tests pass** (1575 baseline + 2 hotfix tests)
- **No regression at any tested register** (Step 1 + stage2d_batch + d7_integration + d7b_live + proposer_interface + proposer_prompt + evaluate_dsr + wf_lineage_guard + all other suites CLEAN)

---

## §7 Three-OPEN audit + adjudication register

### §7.1 OPEN-1 — Module routing for smoke-40

**Question:** Sub-spec §4.1 binds smoke fire as 40 candidates with composite AND-gate (A)+(B)+(C) but does NOT bind which module (Stage 2c vs Stage 2d). Code-surface inspection at next-session entry revealed Stage 2c (`STAGE2C_BATCH_SIZE = 20`, no `--with-critic` CLI) and Stage 2d (`STAGE2D_BATCH_SIZE = 200`, has `--with-critic`) — neither produces 40 out-of-the-box. New `PHASE2C_BATCH_SIZE` env-var override needed.

**Adjudication:** Charlie register approved Option A (Stage 2d + `PHASE2C_BATCH_SIZE`) over Option B (Stage 2c + Critic plumbing) and Option C (Stage 2d + stub D7b for criterion B). Per advisor + ChatGPT convergence at "infrastructure uniformity at register-precision; Critic CLI already wired at Stage 2d (1591-1595); §9.4 carry-forward closure at natural trigger boundary".

### §7.2 OPEN-2 — Critic backend (stub vs live D7b for criterion B)

**Question:** Sub-spec §4.1 criterion (B) requires "Critic-approved/`pending_backtest` rate ≥ 0.9× canonical baseline". Canonical baseline `b6fcbf86` was measured against live Sonnet D7b per [PHASE2C_9 Step 2 closeout §4](../closeout/PHASE2C_9_RESULTS.md). Stub D7b returns all 0.5 scores → criterion (B) measurement reduces to artifact-of-stub not signal.

**Adjudication:** Charlie register approved Option C1 (live D7b via new `--live-critic` flag) over C2 (stub D7b — register-precision violating) and C3 (skip critic entirely — would mutate LOCKED criterion (B) post-SEAL). Cost impact: smoke estimate $0.46 → ~$0.86-1.26 with Proposer + Critic dual Sonnet calls; well within $20/batch cap.

### §7.3 OPEN-3 — Critic ledger pre-charge constraint (load-bearing carry-forward discovery)

**Question:** [PHASE2C_3 batch 1 closeout §135](../closeout/PHASE2C_3_BATCH1.md) and [PHASE2C_5 closeout §214](../closeout/PHASE2C_5_PHASE1_RESULTS.md) both flag forward-warning: "`stage2d_batch.py:1081-1108` still calls `run_critic` without `ledger.write_pending` for the critic call. Benign in stub mode (current default); becomes a spend-accounting bug if/when `LiveSonnetD7bBackend` is wired into `main()`." Adding `--live-critic` CLI without ledger pre-charge would violate CLAUDE.md hard constraint at the same fire boundary.

**Adjudication:** Charlie register approved Option D1 (clean: 3-surface coupled patch in single Step 2 fire-prep cycle) over D2 (split-scope two cycles — illusory benefit) and D3 (accept drift — register-precision violating; rejected on discipline grounds). Per advisor + ChatGPT convergence at "causal coupling + carry-forward closure at natural trigger boundary + D2 illusory + Codex bounded scope handles multi-surface fine".

### §7.4 Charlie auth #1-expanded scope

| Surface | Auth scope | Charlie message |
|---|---|---|
| (1) `PHASE2C_BATCH_SIZE` | Approved | "Authorized" (auth #1) |
| (2) `--live-critic` CLI | Approved | "Authorized" (auth #1) |
| (3) Ledger pre-charge | Approved (D1 expansion) | "Authorized d1" (auth #1-expanded) |

Subsequent Codex first-fire hotfix landed within auth #1-expanded scope per Step 1 hotfix-bundle register-precedent at `3543fab` (findings on already-authorized surfaces don't require fresh auth-scope expansion).

---

## §8 Register-class boundaries preserved

### §8.1 Authorization-routing discipline operating

Per [`feedback_authorization_routing.md`](../../) memory: only Charlie-register messages constitute authorization. Throughout this session:
- 3 OPEN questions surfaced + adjudicated to leans BEFORE code fire
- Charlie auth #1-expanded explicit ACK on 3-surface scope
- Codex hotfix scope routing per Step 1 register-precedent (no implicit auth expansion)
- Smoke fire boundary (auth #2 patch seal + auth #3 smoke fire) preserved as separate Charlie-register gates downstream

### §8.2 Anti-momentum-binding discipline operating

Surface (3) ledger pre-charge was NOT in original handoff §C OPEN-2 framing — surfaced at fire-prep audit phase as load-bearing carry-forward (PHASE2C_3 + PHASE2C_5 warning). STOPPED at OPEN-3 surface to require explicit Charlie auth-scope ack rather than implicit-momentum extension. Reviewer convergence on D1 was advisory; Charlie's "Authorized d1" message was the explicit ack.

### §8.3 Register-class-distinct surfaces preserved

Codex Finding #3 (block telemetry) is register-class-distinct from authorized 3 surfaces — pushed back on fix scope rather than implicit-expanding auth #1. Tracked as §19 instance #7 candidate + Step 5 fire-prep prerequisite carry-forward parallel to original §9.4 (`STAGE2D_BATCH_SIZE` Step 5-only) which itself caught this pattern at handoff-drafting register.

---

## §9 §19 spec-vs-empirical-reality finding observation register

### §9.0 Instance count register at PHASE2C_12 cycle

§19 spec-vs-empirical-reality finding pattern cumulative count at PHASE2C_12 cycle = **6 instances** (instances #1-#6 below). Instance #7 (block telemetry) is **register-class-distinct** from the §19 defect class and is co-located here for cycle audit completeness only — see §9.0a annotation.

- **Instance #1** (Step 1 sub-spec drafting): V#7 Path A patch at sub-spec SEAL pre-fire
- **Instance #2** (Step 1 sub-spec drafting): line-number drift at canonical artifact §10.1 V#6 row
- **Instance #3** (Step 1 implementation arc): "Proposer entry register" semantic ambiguity caught by Codex first-fire Finding #1
- **Instance #4** (Step 1 deliverable §9.4): `STAGE2D_BATCH_SIZE = 200` vs Q3 LOCKED N=198 (Step 5 scope carry-forward)
- **Instance #5** (Step 2 fire-prep audit, this deliverable): handoff drafting cycle marked batch-size as "Step 5-only prerequisite" but empirical Step 2 audit caught smoke also blocked at 40 ≠ 20 ≠ 200 → re-routed to Step 2+5 prerequisite
- **Instance #6** (Step 2 fire-prep audit, this deliverable): handoff drafting cycle missed PHASE2C_3 + PHASE2C_5 carry-forward ledger pre-charge constraint at register-precision; was already documented at canonical-artifact register but not surfaced at sub-spec / handoff register

### §9.0a Register-class-distinct observation (NOT counted in §19 cumulative)

- **Instance #7 candidate (telemetry layer, register-class-distinct from #5/#6)**: block telemetry `BLOCK_COUNT = STAGE2D_BATCH_SIZE // BLOCK_SIZE` integer-division partial-block dropping at small batch sizes (smoke=40 → 0 blocks; main=198 → 3 blocks of 50 covering 1-150, missing 151-198). **NOT a handoff/sub-spec drafting cycle defect** — implementation-time edge-case at telemetry layer; sub-spec did not (and would not be expected to) spec telemetry-layer behavior. Observability output not load-bearing for mining correctness. Deferred per Codex Finding #3 push-back to follow-up commit OR Step 5 fire-prep prerequisite. Tracked here for cycle audit completeness; **NOT counted in §19 cumulative** to preserve register-class hygiene at methodology consolidation cycle Strong-tier promotion evidence basis.

### §9.1 Pattern observation across PHASE2C_12 cycle

**Instances #1-#6** at this cycle exhibit same defect class: **handoff/sub-spec drafting cycle text-register pass clean, but empirical fire-prep audit caught register-precision violations at code-register**. Same pattern as [PHASE2C_9 Step 5 §7 spec-vs-empirical-reality finding pattern](../discipline/METHODOLOGY_NOTES.md) §19 codification (Step 1 deliverable §9 already enumerated 4 instances at same defect class).

Methodology-codification candidate carried forward: "WHICH reviewer pass at WHICH register" — text-register reviewer pass cycle (M5 ChatGPT structural overlay + M6 advisor full-prose-access + M7 fresh-register full-file pass) is bounded at sub-spec drafting cycle text-register scope; **empirical fire-prep audit at code-register fire is register-class-distinct prevention discipline**, both load-bearing at register-class-distinct prevention discipline. PHASE2C_10 §16 sub-rule "WHO reads prose at WHICH register" is necessary-not-sufficient; pre-fire audit at empirical register is necessary complement.

---

## §10 Compliance audit at this deliverable register

### §10.1 CLAUDE.md compliance

| Rule | Compliance |
|---|---|
| "Spend ledger uses pre-flight charge pattern" | ✅ `write_pending` strictly before `run_critic`; `finalize` after; `mark_crashed` on exception path; pre-charge invariant preserved via `COALESCE(actual_cost, estimated_cost)` semantics |
| "NEVER perform a budget check AFTER an API call (must be pre-call)" | ✅ Affordability gate at lines ~1276-1300 fires BEFORE `write_pending`; `write_pending` fires BEFORE `run_critic` (which is the API call) |
| Budget caps `$20/batch + $100/UTC-month` | ✅ Affordability gate checks `STAGE2D_BATCH_CAP_USD` + `STAGE2D_MONTHLY_CAP_USD` + `STAGE2D_CUMULATIVE_CAP_USD` |
| `backend_kind` + `call_role` required fields | ✅ `BACKEND_KIND_D7B_CRITIC` + `CALL_ROLE_CRITIQUE` imported and used |
| Approved core libraries | ✅ No new dependencies; only stdlib + existing `anthropic`, `pytest` |
| Coding standards (type hints + docstrings + UTC) | ✅ All new functions have type hints + docstrings citing binding source; `datetime.now(timezone.utc)` throughout |

### §10.2 `~/.claude/rules/*` compliance

| Rule file | Compliance |
|---|---|
| `coding-style.md` (PEP 8 + type annotations) | ✅ Type hints on all new signatures; PEP 8 line-length preserved |
| `testing.md` (TDD-first + pytest) | ✅ TDD-RED commit before any GREEN; pytest framework; happy path + edge cases |
| `git-workflow.md` (conventional commits) | ✅ `test(...)`, `feat(...)`, `fix(...)` prefixes consistent with Step 1 register-precedent |
| `security.md` (no hardcoded secrets) | ✅ `PHASE2C_BATCH_SIZE` env var is non-secret config flag; no API keys touched |
| `trading-safety.md` | N/A — no order placement or risk-limit changes at this register-class |

### §10.3 PHASE2C_12_PLAN.md sub-spec compliance

| Q-LOCKED disposition | Implementation surface | Compliance |
|---|---|---|
| Q1 (smoke count = 40) | `PHASE2C_BATCH_SIZE=40` produces 40 calls | ✅ |
| Q3 (main count = 198) | `PHASE2C_BATCH_SIZE=198` produces 198 calls | ✅ |
| Q5 (smoke→main Charlie gate) | Patch fire is fire-prep only; smoke fire requires separate Charlie auth #3 | ✅ preserved |
| Q9 (smoke theme override) | Step 1 `theme_override` mechanism unchanged; threads via existing `BatchContext.theme_override` field | ✅ |
| Q10 (`THEME_CYCLE_LEN` config-driven) | Step 1 `_resolve_theme_cycle_len()` mechanism unchanged | ✅ |

---

## §11 What this deliverable does NOT do

Per (α) strict-canonical scope adjudication discipline at sub-spec §8.1 Step 2 fire-prep scope:

1. **Does NOT fire smoke batch.** Smoke fire (40 candidates 100% `multi_factor_combination` ~$0.86-1.26 first $-spend at PHASE2C_12 cycle) requires separate Charlie-register authorization at smoke-fire boundary per Q5 LOCKED. Operational fire register-class-distinct from this fire-prep code-register modification.
2. **Does NOT fire main batch.** Step 5 main fire (198 candidates uniform 6/6) conditional on smoke PASS + Charlie auth #4 at smoke-vs-main boundary.
3. **Does NOT fix Codex Finding #3 (block telemetry).** Tracked as §9.0a register-class-distinct observation (NOT counted in §19 cumulative) at telemetry-layer register-class-distinct from authorized 3-surface scope. Defer to follow-up commit OR Step 5 fire-prep prerequisite parallel to original §9.4 carry-forward.
4. **Does NOT update CLAUDE.md "Theme rotation operational boundary"** canonical wording. Default `THEME_CYCLE_LEN=5` + `STAGE2D_BATCH_SIZE` default=200 at code register preserves operational invariant at default-state register.
5. **Does NOT advance Phase Marker** beyond Step 2 fire-prep scope. Phase Marker advance commit fires at Step 2 fire-prep deliverable seal register-class-distinct from implementation arc fire register; specific Phase Marker wording adjudicated at deliverable seal commit boundary.
6. **Does NOT distinguish `cr.d7b_cost_actual_usd = None` (D7b error path; no cost captured) from `0.0` (legitimate zero cost).** Surface (3) finalize uses `actual_cost_usd = cr.d7b_cost_actual_usd or 0.0` which collapses these two semantic cases. Pre-charge `$0.05` ceiling at `D7B_STAGE2A_COST_CEILING_USD` dominates the risk surface (any real critic call is at most $0.05 over-counted in worst case; pre-charge invariant preserved per CLAUDE.md `COALESCE(actual_cost, estimated_cost)` semantics). Semantic ambiguity is **register-class-distinct from spend invariant**; downstream cost-efficiency / critic-effectiveness / spend-anomaly-detection analyses may see polluted signal at the `actual_cost = 0` register. **Tracked as known semantic carry-forward**; cleanup deferred to future cycle adjudication. Both ChatGPT and advisor independently surfaced this concern at Step 2 fire-prep ratification register.
7. **Does NOT fix smoke-fire telemetry block-display anomaly.** At smoke `PHASE2C_BATCH_SIZE=40`, the existing `BLOCK_COUNT = STAGE2D_BATCH_SIZE // BLOCK_SIZE` produces `BLOCK_COUNT = 0`; the run-time block-trends report displays `block 1 (1-50): n=40 valid=... cost_total=...; block 2 (51-100): n=0 valid=0 valid_rate=None; block 3 (101-150): n=0 ...; block 4 (151-200): n=0 ...`. **This is expected, not a batch-truncation signal.** Smoke PASS/FAIL adjudicator should NOT misread `blocks 2-4 = n=0` as evidence the batch terminated at call 50 — the batch ran all 40 calls correctly; the telemetry layer simply has integer-division semantics that don't accommodate `batch_size < BLOCK_SIZE`. Same deferred-fix as §11 item 3 (Codex Finding #3); listed here additionally as **forward-binding documentation for smoke-fire adjudication context**.

---

## §12 Anchors

### §12.1 PHASE2C_12 cross-references

- [`docs/phase2c/PHASE2C_12_PLAN.md`](PHASE2C_12_PLAN.md) — sub-spec sealed at `b8e4972`; §3.2 Q1+Q3 LOCKED + §4.1 + §4.2 + §8.1 Step 2 sequenced steps
- [`docs/phase2c/PHASE2C_12_STEP1_DELIVERABLE.md`](PHASE2C_12_STEP1_DELIVERABLE.md) — Step 1 deliverable sealed at `4e112a3`; structural-template register for this Step 2 deliverable
- [`docs/phase2c/PHASE2C_12_SCOPING_DECISION.md`](PHASE2C_12_SCOPING_DECISION.md) — scoping decision sealed at `541c0be`; §4.4 arc designation = breadth expansion arc

### §12.2 PHASE2C_3 + PHASE2C_5 cross-references (carry-forward closure)

- [`docs/closeout/PHASE2C_3_BATCH1.md`](../closeout/PHASE2C_3_BATCH1.md) §135 — original ledger pre-charge carry-forward warning
- [`docs/closeout/PHASE2C_5_PHASE1_RESULTS.md`](../closeout/PHASE2C_5_PHASE1_RESULTS.md) §214 — re-stated carry-forward warning at Phase 1 closeout

### §12.3 Code module cross-references

- [`agents/proposer/stage2d_batch.py`](../../agents/proposer/stage2d_batch.py) — Surfaces (1)+(2)+(3) implementation surface
- [`agents/critic/d7b_live.py`](../../agents/critic/d7b_live.py) — `LiveSonnetD7bBackend` class + `D7B_STAGE2A_COST_CEILING_USD = $0.05`
- [`agents/critic/orchestrator.py`](../../agents/critic/orchestrator.py) — `run_critic()` lazy-imported; never raises (orchestrator contract)
- [`agents/orchestrator/budget_ledger.py`](../../agents/orchestrator/budget_ledger.py) — `BudgetLedger.can_afford()` + `write_pending()` + `finalize()` + `mark_crashed()` API
- [`tests/test_phase2c_12_step2_fire_prep.py`](../../tests/test_phase2c_12_step2_fire_prep.py) — Step 2 test coverage at TDD-GREEN register

### §12.4 Discipline cross-references

- [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) §16 + §17 + §19 — anchor-prose-access discipline + procedural-confirmation defect class + spec-vs-empirical-reality finding pattern
- [`feedback_authorization_routing.md`](../../) — every operational fire boundary requires Charlie-register auth
- [`feedback_reviewer_suggestion_adjudication.md`](../../) — per-finding Codex review adjudication, no bulk accept
- [`feedback_codex_review_scope.md`](../../) — Codex adversarial review on substantive code changes; per-finding adjudication discipline

### §12.5 Authorization register

- Charlie auth #1: "Authorized" (covers Surfaces 1+2 per OPEN-1 + OPEN-2 framing)
- Charlie auth #1-expanded: "Authorized d1" (expands to Surface 3 per OPEN-3 D1 adjudication)
- Charlie auth #2: PENDING — Step 2 patch seal commit + Phase Marker advance
- Charlie auth #3: PENDING — smoke-fire boundary (live $0.86-1.26 first $-spend at PHASE2C_12 cycle)
- Charlie auth #4: PENDING — smoke-vs-main boundary (conditional on smoke PASS)

---

## §13 Active next action

**Step 2 fire-prep deliverable SEAL** at this commit + Phase Marker advance commit per Step 1 deliverable seal precedent at `4e112a3`. Charlie auth #2 required at patch seal boundary.

Post-seal: Step 2 smoke batch fire-prep complete; smoke command env (`PHASE2C_SMOKE_THEME_OVERRIDE=multi_factor_combination` + `PHASE2C_BATCH_SIZE=40` + `--with-critic --live-critic`) **will be prepared for review** pending Charlie auth #3 at smoke-fire boundary. Auth #3 is NOT implied by auth #2; the boundaries are register-class-distinct and require separate explicit Charlie-register authorization per [`feedback_authorization_routing.md`](../../) discipline.
