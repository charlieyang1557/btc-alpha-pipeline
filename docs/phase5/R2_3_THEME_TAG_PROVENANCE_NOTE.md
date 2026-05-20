# R2.3 Theme Tag Provenance Verification — V_SEAL

**Cycle class:** Phase B Pre-Sequence Roadmap V3 Tier 2 R2.3 substantive cycle — Phase A V4 SEAL OBSERVATION 10 theme-tag provenance verification (Bucket-1 Template B per β3 hybrid lock; structural analog to R2.0 / R2.1 / R3.1d / R4.1 cycle pattern; sister cycle to R2.1 under R2.0 SD-B B2 Tier 2 SEAL prereq pair).

**Authorization chain:** Charlie register "R2.3 substantive cycle authorized" 2026-05-20 (cycle entry); Round-1 sub-decision menu lock "SD-α α2 + SD-β β3 + SD-γ γ1 + SD-δ δ1 ratify" 2026-05-20 (post-2-leg reviewer round CONVERGED on α2/γ1/δ1 + DIVERGED narrow on β with Codex β3 / Advisor β1; orchestrator pushback lean β3 ratified by Charlie).

**Version:** V_SEAL (sealed at register-event boundary 2026-05-20)

---

## §0 Cycle metadata

| Field | Value |
|---|---|
| Cycle name | R2.3 Theme Tag Provenance Verification |
| Cycle class | Substantive cycle (NOT pre-commit; NOT errata; NOT implementation arc) |
| Template | Bucket-1 Template B (R2.0 / R2.1 / R3.1d / R4.1 precedent) |
| Cycle entry | 2026-05-20 |
| Authorization source | Charlie register "R2.3 substantive cycle authorized" |
| Sister cycle | R2.1 Stratum B DSL audit (`docs/phase5/R2_1_STRATUM_B_DSL_AUDIT_NOTE.md`); paired under R2.0 SD-B B2 |
| Tier 2 SEAL gate completion status | R2.1 ✓ + R2.3 ✓ (this cycle) = Tier 2 SEAL **COMPLETE** at this V_SEAL register-event boundary per R2.0 SD-B B2 lock |
| Locked sub-decisions | α2 (4-dimensional with dim (d) INDETERMINATE-DSL-UNAVAILABLE) + β3 (hybrid: standalone artifact + Phase A §11 Errata cross-reference) + γ1 (explicit §34 first-empirical-test section) + δ1 (population-wide INDETERMINATE-DSL-UNAVAILABLE per Sub-1 η1-C extension) |
| Notable first | **FIRST cycle since METHODOLOGY_NOTES §34 codification** (commits `39f0727` + `60b60a0` 2026-05-20); §34 application pre-commit yielded load-bearing finding before lock (raw_payloads gap at 0/5 cohort_a source batches) |
| Anti-rescue binding | V3-P1 (R2.0:137) preserved; no same-cycle threshold mutation; no post-observation criterion adjustment |
| Anti-pre-emption binding | R5.1 cohort-framing decisions eligible-not-named at separate Charlie register-event |
| Cycle scope | Local static code analysis + cohort-reference inspection + accessibility audit; NO new data acquired; NO API spend; NO engine runs |

---

## §1 Sub-decision register chain summary

| # | Sub-decision | Locked option | Source register |
|---|---|---|---|
| α | Audit dimensions | **α2** = 4-dimensional ((a) authorship + (b) timing + (c) audit trail + (d) cross-artifact consistency) with dim (d) classified INDETERMINATE-DSL-UNAVAILABLE per Sub-1 η1-C extension; 2-leg CONVERGED MEDIUM | Round-1 sub-decision menu ratify |
| β | V_SEAL artifact class | **β3** = hybrid (standalone Bucket-1 Template B canonical artifact at this file path + Phase A §11 Errata cross-reference append pointing to this artifact); 2-leg DIVERGED narrow (Advisor β1 / Codex β3); orchestrator pushback lean β3 per navigation-value argument | Round-1 ratify (Codex + orchestrator pushback ratified by Charlie) |
| γ | §34 empirical codification framing | **γ1** = explicit "§34 first-empirical-test" section in V_SEAL artifact, tight scope ~30-50 lines per Advisor scoping discipline; documents §34 application + lessons + cross-cycle empirical evidence; 2-leg CONVERGED HIGH (Advisor explicit own-finding-anchoring discount declared) | Round-1 ratify |
| δ | Anti-rescue + INDETERMINATE-DSL-UNAVAILABLE framing | **δ1** = population-wide INDETERMINATE-DSL-UNAVAILABLE classification for all 39 candidates' dim (d) per Sub-1 η1-C extension; compact verdict, not 39-row repetition; 2-leg CONVERGED MEDIUM (contingent on α2) | Round-1 ratify |

---

## §2 Phase A V4 OBSERVATION 10 binary framing + R2.3 three-layer reshape

### §2.1 Phase A V4 OBSERVATION 10 (verbatim source)

Per `docs/phase5/PHASE5_A_CLARIFICATION_NOTE.md` lines 297-299:

> **OBSERVATION 10: Theme tag provenance is unverified in this cycle (eligible-not-named).**
>
> The `theme` column derives Stratum A vs B per Phase 5.1 §4.2-§4.3. Whether themes were assigned by AI-proposer at hypothesis generation OR post-hoc by reviewers is not verified in this cycle. Theme-level patterns (Codex A.2 C3) are exploratory, not strong family-boundary evidence. This caveat binds any theme-based framing in OBSERVATIONS 4 + 7.

Binary framing: (a) AI-proposer-at-hypothesis-generation OR (b) post-hoc-by-reviewers.

### §2.2 R2.3 three-layer reshape (per Codex Round-1 SF3 finding)

The OBS 10 binary framing is incomplete. The verified theme-assignment mechanism is a **three-layer** characterization:

- **Layer 1 (timing):** Themes are assigned at GENERATION TIME — at BatchContext construction, BEFORE the Proposer LLM is called. This is closer to OBS 10's (a) than (b).
- **Layer 2 (authorship):** BUT theme assignment is performed by ROTATION LOGIC in the Proposer batch driver (`agents/proposer/stage2c_batch.py`), NOT by the Proposer LLM itself. The Proposer LLM does not choose the theme.
- **Layer 3 (constraint):** The Proposer LLM receives the assigned theme as a prompt directive (`theme (rotating): {theme}` at `agents/proposer/prompt_builder.py:227`) and is constrained to generate a hypothesis WITHIN that theme. The LLM operates under theme constraint, not under theme choice.

**Substantive consequence for Phase A OBS 4 + OBS 7 + theme-based framing:** Themes are pre-registered family labels (legitimate family-boundary signals per generation-time-assignment) BUT the cleavage was pre-committed by ROTATION LOGIC rather than by content-aware classification by the Proposer LLM. Theme-level patterns reflect (i) the rotation logic's coverage choices + (ii) per-theme Proposer interpretation quality + (iii) downstream evaluation outcomes — NOT a content-aware family clustering.

### §2.3 Phase A OBS 10 resolution status

Per the three-layer reshape: OBS 10's binary framing **resolves to NOT-(b)** (NOT post-hoc-by-reviewers; no orchestrator post-Proposer theme reassignment; no theme column in experiments.db `runs` registry) with the structural caveat that (a) is also imprecise — the closer-truth is (a') generation-time + rotation-logic + LLM-constrained-not-chosen. Theme-level patterns ARE legitimate family-boundary evidence for the pre-registered pre-commitment class, but NOT for content-aware family clustering. Phase A OBSERVATIONS 4 + 7 + 10 caveat binding can be RELAXED for pre-registered family interpretation + PRESERVED for content-aware family interpretation.

---

## §3 Audit dim (a) — Authorship

### §3.1 Code locus identification (per §34 Step 3 source-artifact mapping)

Theme assignment authorship code locus, verified via grep + Read across repo:

| Source artifact | Role | Citation |
|---|---|---|
| `agents/themes.py:22-29` | CONTRACT BOUNDARY single source of truth for `THEMES` tuple | [VERIFIED via Read 2026-05-20] |
| `agents/themes.py:17-20` | `THEME_CYCLE_LEN = 5`: Stage 2c/2d operational rotation uses first 5 themes only | [VERIFIED via Read] |
| `agents/proposer/stage2c_batch.py:200-213` | `_theme_for_position(k, theme_override)` function: returns `theme_override` if set + valid, else `THEMES[(k - 1) % THEME_CYCLE_LEN]` rotation | [VERIFIED via Read] |
| `agents/proposer/stage2c_batch.py:213` | **Canonical rotation formula:** `return THEMES[(k - 1) % THEME_CYCLE_LEN]` | [VERIFIED via Read] |
| `agents/proposer/stage2c_batch.py:674` | `BatchContext` construction: `theme_slot=(k - 1) % THEME_CYCLE_LEN` | [VERIFIED via Read] |
| `agents/proposer/prompt_builder.py:104-107` | `_theme_for_slot(slot)`: resolves slot integer → theme name string via `THEMES[slot % len(THEMES)]` | [VERIFIED via Read] |
| `agents/proposer/prompt_builder.py:196-205` | PHASE2C_12 Q9 mechanism: `theme_override` (when set) wins over `theme_slot` rotation; smoke batch operationalization | [VERIFIED via Read] |
| `agents/proposer/prompt_builder.py:227` | Theme directive injected into Proposer LLM prompt: `f"  - theme (rotating): {theme}"` | [VERIFIED via Read] |
| `agents/orchestrator/` (directory grep) | `grep -rn "theme" agents/orchestrator/` returns EMPTY — orchestrator package has NO theme handling code | [VERIFIED via grep] |
| `backtest/experiments.db runs` table schema | NO `theme` column — themes are NOT stored in the experiment registry | [VERIFIED via `PRAGMA table_info(runs)` grep -ci theme = 0] |

### §3.2 Locus precision correction (per Codex Round-1 SF1)

The `agents/themes.py` module docstring (lines 3-11) states "The orchestrator owns theme assignment (`theme = THEMES[(k - 1) % len(THEMES)]` per CLAUDE.md)." This is **prose-shorthand**; the actual rotation code lives in the Proposer batch driver `agents/proposer/stage2c_batch.py:213`, NOT in the `agents/orchestrator/` Python package. The `agents/orchestrator/ingest.py` module (which validates + hashes + deduplicates + assigns lifecycle state per `agents/orchestrator/ingest.py:1-7,200-275`) does NOT touch theme assignment.

**Substantive answer to OBS 10 unchanged:** programmatic rotation at generation time, not Proposer-LLM-chosen, not post-hoc-reviewer-assigned. **Locus precision:** the rotation site is the Proposer batch driver, not the orchestrator package. The `agents/themes.py` docstring's prose-shorthand can be improved at a future register-event-boundary clean-up cycle (eligible-not-named per §9).

### §3.3 Authorship verdict

**dim (a) PASS:** theme assignment authorship is fully accessible via code analysis on this execution environment. Authorship locus = Proposer batch driver `agents/proposer/stage2c_batch.py:200-213,674` + helper `agents/proposer/prompt_builder.py:104-107`. NO post-Proposer reassignment. NO orchestrator-level theme handling. NO registry-level theme persistence.

---

## §4 Audit dim (b) — Timing

### §4.1 Generation-time evidence

Theme assignment timing relative to Proposer LLM invocation, verified via code-flow analysis:

1. **Step 1 (pre-LLM):** `stage2c_batch.py:674` constructs `BatchContext(...theme_slot=(k - 1) % THEME_CYCLE_LEN, theme_override=smoke_theme_override, ...)`. Theme_slot is computed deterministically from batch position `k` BEFORE any Proposer LLM call.

2. **Step 2 (pre-LLM):** `prompt_builder.py:202-205` resolves the final theme: if `context.theme_override is not None` → use it; else `theme = _theme_for_slot(context.theme_slot)` (which dereferences `THEMES[slot % len(THEMES)]`).

3. **Step 3 (pre-LLM):** `prompt_builder.py:227` injects the resolved theme into the user prompt as `f"  - theme (rotating): {theme}"`. The Proposer LLM receives the theme as a directive in the prompt body.

4. **Step 4 (LLM call):** The Proposer LLM (`agents/proposer/sonnet_backend.py`) is invoked with the prompt that already contains the theme directive. The LLM generates the DSL hypothesis content WITHIN the theme constraint.

5. **Step 5 (post-LLM):** `agents/orchestrator/ingest.py:200-275` validates + hashes + lifecycle-state-assigns the LLM output. **No theme reassignment occurs here; orchestrator ingest is theme-agnostic** (grep on `agents/orchestrator/` returns no theme references). The theme value is tracked by the Proposer batch driver's `call_summaries` record at `agents/proposer/stage2c_batch.py:800-873` outside the orchestrator ingest path, propagating downstream to leaderboard + forward-window CSVs as metadata.

### §4.2 Timing verdict

**dim (b) PASS:** timing is fully accessible via code-flow inspection. Theme assignment happens at **generation time** (specifically: at BatchContext construction, Step 1; before the Proposer LLM is called, Step 4). Theme remains immutable through orchestrator ingest (Step 5). NO post-Proposer or post-execution theme mutation.

---

## §5 Audit dim (c) — Audit trail

### §5.1 Audit-trail source documents

The theme assignment audit trail is documented across the following sealed + canonical artifacts:

| Document | Audit-trail content | Citation |
|---|---|---|
| `agents/themes.py:3-11` (docstring) | CONTRACT BOUNDARY declaration: single source of truth for THEMES; D6 indexes; orchestrator (prose-shorthand for batch driver per §3.2) owns assignment; rotation formula stated | [VERIFIED via Read 2026-05-20] |
| `agents/themes.py:17-20` (comment) | THEME_CYCLE_LEN = 5 rationale: Stage 2c/2d operational rotation uses first 5 themes; `multi_factor_combination` canonical but excluded from current operational rotation pending separate validation; reference to "CLAUDE.md Theme rotation operational boundary" | [VERIFIED via Read] |
| `agents/proposer/prompt_builder.py:196-201` (comment block) | PHASE2C_12 Q9 smoke fire register binding: theme_override semantics; reference to `docs/phase2c/PHASE2C_12_PLAN.md §3.3 Q9 LOCKED + §4.1` | [VERIFIED via Read] |
| `agents/proposer/stage2c_batch.py:200-205` (docstring) | `_theme_for_position()` anti-fishing-license boundary: theme_override MUST be in canonical THEMES tuple or ValueError; binding source = `docs/phase2c/PHASE2C_12_PLAN.md §3.3 Q9 LOCKED` | [VERIFIED via Read] |
| `docs/phase4/PHASE4_PLAN.md §1.3` (lines 28-38) | Theme decomposition pre-registration at Phase 4 design time: 22 calendar_effect (Stratum A) + 17 non-calendar = 7 volume_divergence + 6 momentum + 2 mean_reversion + 2 volatility_regime (Stratum B); "calendar/non-calendar is the substantive cleavage; theme-by-theme is too fragmented at this N"; calendar-explicit decomposition pre-registers theme-imbalance handling | [VERIFIED via Read] |
| `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md §4.2-§4.3` (lines 233-267) | Phase 5.1 input survey theme reference: `theme` column derives stratum (calendar_effect → A; else → B) per Phase 4 §1.3 sealed stratification; not an explicit stratum column | [VERIFIED via Read] |

### §5.2 Audit-trail completeness

The audit trail is **complete in code + plan documentation** for the theme assignment mechanism. Theme rotation is documented at the contract-boundary level (`agents/themes.py` docstring), at the batch-driver level (`stage2c_batch.py:200-213` docstring), at the prompt-construction level (`prompt_builder.py:196-205` comment block), and at the pre-registration level (`PHASE4_PLAN.md §1.3` + `PHASE5_1 §4.2-§4.3`). PHASE2C_12 Q9 LOCKED is the load-bearing binding for the theme_override mechanism.

### §5.3 Audit trail verdict

**dim (c) PASS:** audit trail is fully accessible across sealed artifacts. NO undocumented theme assignment behavior surfaced. The audit trail supports the three-layer characterization (§2.2): generation-time + rotation-logic + LLM-constrained.

---

## §6 Audit dim (d) — Cross-artifact consistency (INDETERMINATE-DSL-UNAVAILABLE per δ1)

### §6.1 Population scope

dim (d) cross-artifact consistency operates on the 39 Phase 4 cohort_a candidates per `data/phase4_scoping/cohort_a_candidate_reference.csv` (39 rows; sourced from 5 unique source batches).

### §6.2 Source-data accessibility (per §34 Step 4 verification)

| Source batch | Cohort_a candidate count | Local accessibility in `raw_payloads/` |
|---|---|---|
| `355a8f9f-2a1f-435d-a1a8-c365b92e185b` | 6 | ✗ ABSENT |
| `4f894318-eb69-48b5-95ef-e22abe3ecdd1` | 12 | ✗ ABSENT |
| `71d42a07-d88f-431a-a653-601010cf1921` | 5 | ✗ ABSENT |
| `91ad68ed-6470-45a7-8735-171c39ff25c3` | 7 | ✗ ABSENT |
| `a12c2a65-4314-4dde-be6e-968a0c70ee6e` | 9 | ✗ ABSENT |
| **Total** | **39** | **0/5 source batches accessible** |

This is the **identical pattern** to R2.1 DSL persistence gap finding (R2.1 §5 + §8.1; 5 PHASE2C_15 source batches absent locally) — the cohort_a source batches are gitignored-as-regenerable or pruned-from-local-state, and the Proposer-time raw_payloads JSON files are not available on this execution environment for filesystem-level cross-artifact consistency checks.

### §6.3 INDETERMINATE-DSL-UNAVAILABLE classification (per δ1 lock)

Per Sub-1 η1-C verdict-vocabulary extension (locked at R2.1 V_SEAL `docs/phase5/R2_1_STRATUM_B_DSL_AUDIT_NOTE.md §6.1` + §1 sub-decision register), all 39 cohort_a candidates' dim (d) cross-artifact consistency is classified **INDETERMINATE-DSL-UNAVAILABLE** as a population-wide verdict.

**Specific sub-claims rendered INDETERMINATE by raw_payloads gap:**
- Per-call Proposer prompt theme directive value (was `theme_slot` or `theme_override` used?)
- Per-call `theme` field in Proposer output JSON (does it match the cohort_a reference theme?)
- `theme_override` per-batch usage attestation (cohort_a distribution 22/7/6/2/2 doesn't match even 5-theme rotation — Codex Round-1 SF2 surfaced this as a possible theme_override or post-rotation-filtering signature; NOT VERIFIABLE without raw_payloads access)

### §6.4 Why dim (d) is NOT load-bearing for OBS 10 binary resolution

Dim (a) authorship via code analysis (§3) is the substantive driver for the OBS 10 binary resolution. The dim (d) cross-artifact consistency check would have surfaced (i) whether the theme assignment mechanism was applied UNIFORMLY across the 39 candidates and (ii) whether `theme_override` was used at PHASE2C_15 source batches — both of which are downstream confirmations of the upstream code-mechanism finding, NOT independent evidence for AI-proposer-vs-post-hoc-reviewer authorship.

Dim (d) is eligible for separate Charlie register-event resolution if (i) Sub-2 β P2a DSL recovery cycle fires for R2.1 reasons (and re-runs would surface theme metadata) or (ii) PHASE2C_15 source batches become locally accessible via separate recovery cycle.

### §6.5 dim (d) verdict

**dim (d) INDETERMINATE-DSL-UNAVAILABLE (population-wide; 39/39 candidates):** raw_payloads gap blocks filesystem-level cross-artifact consistency verification. NOT load-bearing for OBS 10 binary resolution. Eligible-not-named for separate Charlie register-event resolution per anti-pre-emption.

---

## §7 §34 first-empirical-test codification (per γ1 lock)

### §7.1 Application context

R2.3 is the **FIRST cycle since METHODOLOGY_NOTES §34 codification** (commits `39f0727` + `60b60a0` 2026-05-20, sealed within ~12 hours of R2.3 cycle entry). §34 = "Data accessibility pre-verification for pre-commit audit-criterion locks." Application discipline: at R2.3 pre-commit (Round-1 sub-decision menu drafting), §34 Steps 1-5 applied to the proposed audit dimensions before SD-α lock.

### §7.2 §34 application result table

| §34 step | R2.3 application outcome |
|---|---|
| 1. Enumerate dimensions | 4 candidate dimensions: (a) authorship + (b) timing + (c) audit trail + (d) cross-artifact consistency |
| 2. Identify audit population | 39 Phase 4 cohort_a candidates from 5 unique source batches |
| 3. Map (dim × population) → source artifacts | (a)+(b)+(c) → code + sealed plan/spec docs; (d) → `raw_payloads/batch_*/<hash>.json` + `experiments.db` + forward-window CSVs |
| 4. Verify accessibility on canonical execution environment | (a)+(b)+(c) ✓ FULLY ACCESSIBLE; (d) ✗ 0/5 source batches accessible (R2.1 DSL persistence gap pattern recurrence) |
| 5. Risk classification + choice at lock | dim (d) raw_payloads gap surfaced **pre-commit**; choice (c) "lock with INDETERMINATE-on-data-unavailability classification disclosed in pre-commit artifact's residual-risk section" applied via Sub-1 η1-C verdict-vocabulary extension |

### §7.3 What §34 detected (resolution discipline empirical evidence)

§34's pre-commit accessibility check surfaced the raw_payloads gap **BEFORE** Round-1 sub-decision menu lock — not at substantive-cycle execution time (R2.1 pattern). This is the discipline §34 was codified to produce: shift the accessibility-failure detection from substantive-cycle execution time (where it produces INDETERMINATE per-candidate verdicts that block scope-bounded resolution) to pre-commit time (where it shapes audit-dimension choice + verdict-vocabulary at lock).

### §7.4 What §34 resolution discipline produced

Per §34 Step 5, three lock-choices were available given the dim (d) raw_payloads gap: (a) scope-narrow to data-accessible subset (α1 3-dimensional), (b) add a recovery sub-task as separate Charlie register-event prerequisite (P2a class), or (c) lock with INDETERMINATE-on-data-unavailability classification. The Round-1 reviewer round + Charlie register selected (c) via α2 + δ1 — re-using R2.1's Sub-1 η1-C verdict-vocabulary extension as the disciplined disclosure mechanism. This is the **first cross-cycle re-use** of the Sub-1 η1-C extension, which validates the extension's standing-discipline status (not a one-cycle artifact).

### §7.5 Cross-cycle empirical evidence + future implications

R2.3 demonstrates §34's value at first empirical test: (i) §34 detection works at pre-commit (raw_payloads gap surfaced before lock), (ii) §34 resolution-discipline lock-choices integrate with R2.1's verdict-vocabulary extension (INDETERMINATE-DSL-UNAVAILABLE applied at R2.3 dim (d) per δ1), (iii) the cycle's substantive answer (dim (a)+(b)+(c) PASS) is NOT degraded by the dim (d) INDETERMINATE classification — the binary OBS 10 resolution stands on code-level evidence alone.

**Future-applications guidance:** future §34 applications can be documented more lightly once cross-cycle precedent is established. R2.3's explicit "§34 first-empirical-test codification" section establishes the cross-cycle evidence chain. Subsequent cycles applying §34 can reference R2.3 §7 as precedent + document only the application-result table (§7.2) without re-narrating the discipline. Methodology-over-engineering risk is bounded by this scoping discipline.

---

## §8 Surfaced finding-class observations (anti-pre-emption preserved)

These observations are surfaced inline as R2.3 findings without expanding R2.3's scope beyond the OBS 10 binary resolution. Each is eligible-not-named for separate Charlie register-event resolution.

### §8.1 OBSERVATION R2.3-A: Three-layer theme assignment mechanism (per Codex Round-1 SF3)

Phase A V4 OBS 10 binary framing is incomplete; the verified mechanism is three-layer (§2.2). This observation does NOT contest Phase A V4 SEAL's sealed content; it reshapes the binary-question framing as an R2.3 inline finding (analog to R2.1 §2.2 R1.2 name-drift handling per δ1). Phase A V4 SEAL preserved; §11 Errata cross-reference will land per β3 hybrid lock.

### §8.2 OBSERVATION R2.3-B: Theme tags ≠ content-aware classifications (per Codex Round-1 SF1+iv finding)

`agents/proposer/stage2c_batch.py:409-445` (`_build_per_call_telemetry()`) computes telemetry fields `overlap_count`, `overlap_ratio`, `out_of_theme_factor_count`, `contains_default_momentum_factor`, `default_momentum_factors_used` — using a `THEME_HINTS` lookup to map theme name → expected factor frozenset. This telemetry exists precisely because theme tags are PROMPT-ROTATION PROVENANCE LABELS (the LLM is told "this is a calendar_effect theme; propose accordingly") and NOT validated content-aware classifications. A strategy tagged "calendar_effect" may use no calendar-related factors in its DSL; the telemetry quantifies the gap.

**Substantive consequence for Phase A OBS 4 (calendar-pattern concentration of robust-8):** Calendar-concentration in cohort_a (22/39 = 56%) reflects (i) rotation logic's allocation of calendar_effect slots + (ii) per-theme AND-gate pass rates + (iii) Proposer LLM's per-theme generation quality — NOT a content-aware family clustering signal. Phase A OBS 4 interpretive framing should treat calendar concentration as a SELECTION pattern at the AND-gate-passing terminus, not as a GENERATION pattern reflecting independent family-boundary structure.

### §8.3 OBSERVATION R2.3-C: cohort_a theme distribution does not match even 5-theme rotation (per Codex Round-1 SF2)

Cohort_a theme distribution = 22 calendar_effect + 7 volume_divergence + 6 momentum + 2 mean_reversion + 2 volatility_regime (39 total). Even 5-theme rotation across an arbitrary batch size N would produce approximately uniform distribution (N/5 per theme). The observed 22/7/6/2/2 distribution is non-uniform. **Possible explanations** (NOT load-bearing for OBS 10 binary; flagged for future P2a recovery cycle if it fires):
- (i) PHASE2C_15 source batches used `theme_override` for some smoke or targeted iterations (PHASE2C_12 Q9 mechanism)
- (ii) AND-gate passing rate differs substantially by theme — calendar_effect strategies pass at higher rate than thin themes
- (iii) Downstream cohort_a selection filtering compounded with rotation distribution
- (iv) Combination of (i) + (ii) + (iii)

Discrimination between (i)/(ii)/(iii)/(iv) requires raw_payloads + batch metadata access (dim (d) INDETERMINATE-DSL-UNAVAILABLE per δ1). Per anti-pre-emption: any resolution requires separate Charlie register-event.

### §8.4 OBSERVATION R2.3-D: `multi_factor_combination` theme excluded from current operational rotation

Per `agents/themes.py:17-20` comment: Stage 2c/2d operational rotation uses first 5 themes only (THEME_CYCLE_LEN = 5). `multi_factor_combination` is canonical (member of THEMES tuple) but NOT in current operational rotation, pending "separate validation" per CLAUDE.md "Theme rotation operational boundary." Cohort_a contains 0 `multi_factor_combination` candidates (consistent with operational-rotation exclusion). This is a documentation reference for any cycle considering theme-axis cohort framing alongside the §8.2 telemetry caveat; specific successor cycle scoping eligible-not-named per §9 anti-pre-emption.

---

## §9 Eligible-not-named successors + reserved decisions

R2.3 cycle scope strictly bounds the following NON-RESOLUTIONS (eligible-not-named for separate Charlie register-event per anti-pre-emption + R2.0 / R2.1 SEAL precedent codified discipline):

1. **dim (d) recovery sub-cycle** — per §6 INDETERMINATE-DSL-UNAVAILABLE classification; eligible-not-named at separate Charlie register-event. If Sub-2 β P2a DSL recovery cycle fires for R2.1 reasons, dim (d) cross-artifact consistency verification could be folded into the same recovery scope (NOT R2.3 cycle's pre-naming).

2. **`agents/themes.py:11` docstring prose-shorthand precision patch** — per §3.2 locus precision correction; the docstring states "orchestrator owns theme assignment" but actual code locus is `agents/proposer/stage2c_batch.py`. Eligible-not-named clean-up cycle (NOT R2.3 cycle's modification of `agents/themes.py`).

3. **Observation R2.3-B/C/D follow-up cycles** — per §8 finding-class observations; each eligible-not-named for separate Charlie register-event with pre-registered scope.

4. **R5.1 cohort-framing decisions involving theme-axis structure** — gated behind Tier 2 SEAL completion (NOW COMPLETE per R2.0 SD-B B2 lock at R2.1 V_SEAL + R2.3 V_SEAL). R5.1 cycle adjudicates whether cohort framing leverages theme-axis (and if so, how to handle the rotation-vs-content-aware caveat per §2.2 + §8.2).

5. **R5.2 selection-inflation handling involving theme-stratum framing** — gated behind R5.1.

6. **R6.1 Tier 6 promotion class involving theme-axis N treatment** — gated behind R5.1/R5.2; theme-rotation provenance verified at R2.3 may inform R6.1's N treatment choice (per R2.0 SD-C C1 α/β/γ sub-requirements) but R6.1 cycle's design decisions are NOT pre-named here.

7. **R2.2 Monday-pattern mechanism investigation** — per R1.2 OBS 4; eligible-not-named WITH Monday-candidate guard at R5.1 V_SEAL lock per R2.0 SD-B B2.

All eligible at separate Charlie register-event boundary per anti-pre-emption + Phase 5.1/5.2/Phase A/R1.2/R3.1a/R4.1/R3.1d/R2.0/R2.1 SEAL precedent codified discipline.

---

## §10 V-anchor chain + cycle adjudication provenance

### §10.1 V-anchor chain (V_SEAL state)

| Anchor | Description | State | Commit |
|---|---|---|---|
| V1 DRAFT | First-pass canonical artifact | COMPLETE | (in-session 2026-05-20) |
| V1 reviewer round | 2-leg subagent default (Codex + Advisor parallel per B2 LOCKED) on V1 DRAFT | COMPLETE — Codex BLOCK on F1 V-state contradiction (caught Advisor-missed) + Advisor APPROVE-WITH-FINDINGS on F1 `_resolve_theme`→`_theme_for_position` function name drift | (in-session 2026-05-20) |
| V2 | Adjudication patches per V1 reviewer round (5 ADOPT patches: V2-P1 §10.1+§11 V-state alignment + V2-P2 function name find-and-replace mechanical literal + V2-P3 §4.1 step 5 wording precision (theme tracked by batch driver outside ingest) + V2-P5 §8.4 anti-pre-emption soften (drop "load-bearing future R5.1+") + V2-P7 §10.3 reliability data update + 4th own-finding-anchoring instance) | COMPLETE | (this V_SEAL commit) |
| PFR rule-Y | Post-fix re-review on V2 (FIRED per Charlie register 2026-05-20) — Codex F1 BLOCKING resolution + V2-P7 introduce meaningful new content + SEAL-class canonical artifact + §34 cycle precedent | **FIRED — returned BLOCK at first pass** (Codex PFR-NEW-F1 §11 line 311 stale + Advisor PFR-NEW-F1 §10.1 circular pre-claim + Advisor PFR-NEW-F2 §11 same as Codex + Advisor PFR-NEW-F4 §10.3 denominator drift); V3 patches mechanical literal applied (V3-P1 §11 row addition + V3-P2 §10.1 PFR row state correction + V3-P3 §10.3 denominator fix); V3 mini-PFR FIRED + returned APPROVE-V_SEAL convergent (Advisor APPROVE-V_SEAL + Codex APPROVE-WITH-FINDINGS NIT-only) | (this V_SEAL commit) |
| V3 patches + V3 mini-PFR | V3 patches resolving PFR BLOCKINGs (V3-P1 + V3-P2 + V3-P3 mechanical literal); V3 mini-PFR FIRED per Charlie register; 1 NIT V3-NIT-P1 (Codex V3-PFR-NEW-F1 §11 patch ID enumeration symmetry) mechanical literal landed at V_SEAL commit | V3 patches COMPLETE; V3 mini-PFR APPROVE-V_SEAL convergent (Advisor + Codex) | (this V_SEAL commit) |
| V_SEAL | Canonical artifact seal at register-event boundary | **SEALED at register-event boundary 2026-05-20** per Charlie register "V_SEAL fire on V3-NIT-P1 + finalization edits authorized" 2026-05-20 (post Charlie pre-authorization "V_SEAL conditionally pre-authorize on clean PFR Authorized" + post V3 mini-PFR APPROVE-V_SEAL convergent ratification) | (this commit) |

### §10.2 Round-1 sub-decision menu adjudication (already complete)

- Round-1 reviewer round dispatched 2-leg parallel (Codex + Advisor)
- Codex leg: SD-α α2 MEDIUM + SD-β β3 HIGH + SD-γ γ1 HIGH + SD-δ δ1 MEDIUM
- Advisor leg: SD-α α2 MEDIUM + SD-β β1 HIGH + SD-γ γ1 (HIGH own-finding-anchoring discount declared) + SD-δ δ1 MEDIUM
- Classification: SD-α/γ/δ CONVERGED; SD-β DIVERGED narrow (β1 vs β3); orchestrator pushback lean β3 per navigation-value argument
- Charlie register lock: "SD-α α2 + SD-β β3 + SD-γ γ1 + SD-δ δ1 ratify" — β3 ratified, all 4 SDs locked

### §10.3 Cumulative reliability data through R2.3 V_SEAL

Per orchestrator's session observation across R2.3 cycle dispatches (Round-1 sub-decision menu round + V1 reviewer round + PFR round):

- Codex leg completed 3 R2.3 dispatches (Round-1 + V1 + PFR); 0 stalls; 0 hallucinations cycle-internal. Codex caught load-bearing precision drifts at Round-1 (agents/orchestrator vs agents/proposer locus + PHASE4_PLAN.md path + 3-layer reshape framing) + caught V1 F1 BLOCKING V-state contradiction (V_SEAL/SEALED claims in title/version/§11 alongside §10.1 V_SEAL row PENDING) that Advisor missed under γ1/§7 own-finding-anchoring distraction + caught PFR-NEW-F1 BLOCKING §11 line 311 stale text (converged with Advisor PFR-NEW-F2).
- Advisor leg completed 3 R2.3 dispatches (Round-1 + V1 + PFR); 0 stalls; 0 hallucinations cycle-internal. Advisor caught V1 F1 BLOCKING function name drift (`_resolve_theme` → `_theme_for_position` cite drift propagated from orchestrator brief; 2 occurrences in §3.1 + §5.1 tables) + caught PFR-NEW-F1 BLOCKING §10.1 PFR row circular pre-claim + PFR-NEW-F2 BLOCKING §11 (converged with Codex) + PFR-NEW-F4 BLOCKING §10.3 denominator drift (this finding is what this revised paragraph addresses). Explicit HIGH own-finding-anchoring discount declared on γ1/§7 per Sub-3 β' R2.1 co-authorship; discount validated by Codex parallel review (Codex did not push back on §7 framing).
- **4th empirical instance of own-finding-anchoring pattern** at R2.3 V1 round (Codex caught V-state contradiction at §10/§11 that Advisor missed). Cross-cycle precedent: R2.0 V2-P6 anti-rescue leak (Codex) + R3.1d V2-P5 fee_model_label injectivity (Codex) + §34 V1 §32 forward-attribution (Codex) + R2.3 V1 V-state contradiction (Codex). Cross-model leg structurally LOAD-BEARING at SEAL-class canonical artifact discipline empirically validated 4 times.
- Cumulative through R2.3 V_SEAL (math reconstruction: §34 SEAL state Codex 1/15 + Advisor 0/10 per CLAUDE.md Phase Marker; +3 R2.3 dispatches each leg = Codex 1/18, Advisor 0/13): **Codex 1/18 verified cite hallucinations (~5.6%; single hallucination instance at §34 PFR-NEW-F2 apostrophe-missing); Advisor 0/13 verified hallucinations under post-/agents-fix opus regime (~0%)**.
- B2 standing rule LOCKED 2026-05-19 preserved + further empirically validated at R2.3 cycle (both Round-1 + V1 + PFR rounds caught cross-model load-bearing defects).

---

## §11 V_SEAL closure

R2.3 Theme Tag Provenance Verification cycle SEALED at register-event boundary 2026-05-20 per Charlie register chain:

| Register-event | Charlie register text |
|---|---|
| Cycle entry | "R2.3 substantive cycle authorized" (2026-05-20) |
| Round-1 sub-decision menu lock | "SD-α α2 + SD-β β3 + SD-γ γ1 + SD-δ δ1 ratify" (2026-05-20) |
| V2 patch list lock + PFR-rule-Y FIRE + V_SEAL conditional pre-authorization | "V2 ADOPT (V2-P1 + V2-P2 + V2-P3 + V2-P5 + V2-P7) / PFR-rule-Y FIRE / V_SEAL conditionally pre-authorize on clean PFR Authorized" (2026-05-20) |
| V3 patches lock + V3 mini-PFR FIRE (V3-P1 + V3-P2 + V3-P3 mechanical literal; post-PFR BLOCK on V2-P1 incomplete §11 + §10.1 circular pre-claim + §10.3 denominator drift) | "V3 ADOPT + V3 mini-PFR FIRE" (2026-05-20) |
| V_SEAL fire post-V3-mini-PFR clean (+ V3-NIT-P1 §11 patch ID enumeration symmetry mechanical literal) | "V_SEAL fire on V3-NIT-P1 + finalization edits authorized" (2026-05-20) |

**Substantive R2.3 outcome:**
- dim (a) authorship PASS: theme assignment is programmatic at `agents/proposer/stage2c_batch.py:200-213, 674` + `prompt_builder.py:104-107, 196-205, 227`; NOT post-hoc-reviewer-assigned; NOT Proposer-LLM-chosen (LLM constrained, not choosing)
- dim (b) timing PASS: theme assigned at generation time (BatchContext construction, before LLM call); NO post-Proposer or post-execution mutation
- dim (c) audit trail PASS: documented across `agents/themes.py` CONTRACT BOUNDARY docstring + `agents/proposer/` code comments + `PHASE4_PLAN.md §1.3` + `PHASE5_1 §4.2-§4.3`; PHASE2C_12 Q9 LOCKED binds theme_override mechanism
- dim (d) cross-artifact consistency INDETERMINATE-DSL-UNAVAILABLE per Sub-1 η1-C extension: 0/5 cohort_a source batches accessible in `raw_payloads/` (identical R2.1 DSL persistence gap pattern); population-wide verdict for all 39 candidates
- Phase A V4 OBS 10 binary framing RESHAPED to three-layer characterization per §2.2: generation-time + rotation-logic-not-content-aware + LLM-constrained-not-chosen; binary resolves to NOT-(b) with structural caveat on (a); theme-level patterns are pre-registered family labels NOT content-aware family clusterings
- §34 first-empirical-test codified per γ1: §34 detection works at pre-commit; resolution-discipline integrated with R2.1 Sub-1 η1-C extension; first cross-cycle re-use validates standing-discipline status (§7)
- 4 finding-class observations surfaced per §8 (R2.3-A three-layer + R2.3-B telemetry caveat + R2.3-C distribution non-uniformity + R2.3-D multi_factor_combination exclusion); each eligible-not-named for separate Charlie register-event

**Tier 2 SEAL completion:** With R2.3 V_SEAL landing, Tier 2 SEAL = R2.1 ✓ + R2.3 ✓ per R2.0 SD-B B2 lock is **COMPLETE**. R5.1 unlocked at separate Charlie register-event boundary per anti-pre-emption + R2.0 / R2.1 / R2.3 SEAL precedent.

Successor register-events eligible-not-named per §9. **No Charlie-named next register-event at V_SEAL close 2026-05-20.** Default posture: non-execution awaiting Charlie register.

---
