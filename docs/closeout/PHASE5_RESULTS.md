# PHASE 5 — Diagnostic Attribution Cycle Results

**Status:** DRAFT (sealed pending reviewer routing + final Charlie register authorization at SEAL author register) · Authoring date: 2026-05-15 · Tag candidate: `phase5-diagnostic-execution-v1` (conditional on reviewer convergence + final Charlie register authorization; tag fire is a separate fire from SEAL commits)

**Cycle scope:** Phase 5 diagnostic-attribution procedure executed per pre-registered sealed sub-spec at [`docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md`](../phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md) (sub-spec drafting cycle SEAL at `49ae7e3`), consuming sealed inputs frozen at Phase 5 cycle entry per scoping §4.1 hard scope binding. Diagnostic execution session-1 (sealed at `ad35915`) computed §2.a–§2.f indicator outputs and assembled §3.1/§3.2 multi-mode labels; diagnostic execution session-2 (sealed at `d7dfbf1`) emitted §4a successor-cycle-class mapping, §4b framing-resolution-pressure assessment, §5 substantive-vs-operational admissibility flags, and §6 initial narrative draft (structural-template traversal). This deliverable is the attribution report per scoping §3 deliverable scope at Phase 5 SEAL register-event boundary.

## §1 Phase 5 result

Per scoping §1 cycle scope language ("attribution cycle to determine what Phase 4's null result means"), the Phase 5 attribution finding is:

> Phase 5 diagnostic procedure detected a single firing failure mode at canonical execution — **§2.b cost drag** with Wilcoxon signed-rank `p = 1.82e-12` on per-candidate cost-Sharpe Spearman correlations across {7, 13, 15, 17} bps — and §4a sealed output records a single eligible successor-cycle-class assignment (cost-model investigation eligible, gross-vs-realistic decomposition). Both substantive and operational terminal-conclusion admissibility criteria evaluated `admissible=False` at canonical execution per sealed §5 D2.1 + D2.2 mechanical routing. Framing-question resolution disposition: DEFERRED under framing question (4) indeterminate. No paradigm-exhaustion terminal-conclusion is invoked at this register.

§1 is the single-sentence synthesis distillation of §8.1 + §8.2 + §8.3 narrations under reading-order convention inherited from Phase 4 closeout (verdict-first-then-rationale). §1 is **not** an independent fourth SEAL author register fire — the three reserved narration authorities at sealed §5 (x) + §6 (vii)(c) + §4b (vii) remain exhaustive.

## §2 Diagnostic procedure summary

Restate per sealed sub-spec; not re-derived at this register. Phase 5 diagnostic procedure comprises six per-mode indicator computations (sub-spec §2.a–§2.f) operationalizing the failure-mode taxonomy at scoping §2.1; multi-mode coexistence rules at sub-spec §3.1; diagnostic ambiguity handling at sub-spec §3.2; successor-cycle-class mapping at sub-spec §4a; framing-resolution-pressure assessment at sub-spec §4b; and substantive-vs-operational admissibility flagging at sub-spec §5. All thresholds frozen at sub-spec SEAL register-event boundary per §2.2 operationalization-freeze lock; no modification at Phase 5 closeout register.

## §3 Per-mode indicator results

Source: session-1 sealed output `data/phase5_diagnostic/execution_session_1_v1/indicator_outputs.json` (sealed at `ad35915`); restated below.

| Mode | Binary detection | Headline statistic | Test / cutoff |
|---|---|---|---|
| §2.a signal decay | not detected | Wilcoxon `p = 0.2558`, n_eff = 39 | one-sided Wilcoxon signed-rank on (forward_Sharpe − training_Sharpe) at 7bps; α = 0.05 |
| §2.b cost drag | **detected** | Wilcoxon `p = 1.82e-12`, n_eff = 39 | one-sided Wilcoxon signed-rank on per-candidate Spearman ρ across {7, 13, 15, 17} bps; α = 0.05 |
| §2.c cohort weakness | not detected | `primary_oos.rank_median = 0.874`, `primary_oos.rank_p75 = 0.960` | AND-gated 75th/90th percentile-rank cutoffs (0.75 / 0.90) |
| §2.d AND-gate overfit | not detected | TOST `p = 1.0`; observed intersection = 39 vs expected = 4.90 (ε = 4.42) | TOST α = 0.05 Binomial-exact ε = 2σ; intersection_count_N = 993 |
| §2.e success-metric mismatch | not detected | per-stratum Wilcoxon `p_A = 0.3051` (calendar_effect), `p_B = 0.9338` (non-calendar) | per-stratum Wilcoxon Bonferroni-adjusted α = 0.025/stratum at 15bps PLAN-§1.5-alignment register |
| §2.f regime change | not detected | forward_T = 0.00533; reference band [0.00393, 0.01120] | non-parametric symmetric 95% quantile band on forward-block T-statistic vs reference distribution |

Indicator construction per sub-spec §2.a–§2.f sealed procedures + §2.2 operationalization-freeze; no judgment-rule modification at this register. Descriptive supplements per sub-spec are not re-enumerated here; available at session-1 sealed outputs for downstream consumers.

## §4 Multi-mode interpretation per §3.1 + §3.2

Source: session-1 sealed outputs `multi_mode_labels.json` + `ambiguity_disposition.json` (sealed at `ad35915`).

- **§3.1 multi-mode label set** — `firing_modes: ['cost_drag']`; `not_detected_modes: ['andgate_overfit', 'cohort_weakness', 'regime_change', 'signal_decay', 'success_metric_mismatch']`; `nan_modes: []`; `per_mode_labels.cost_drag: "cost-drag reading"`. Partition table contains a single row at `mode=cost_drag, categorical_label=cost-drag reading`; Line 1 (§2.f regime-change qualifier) does not fire; Line 2 (§2.d → §2.c gate-validity overlay) does not fire; tier bilateral overlay not applicable at single-mode firing.
- **§3.2 diagnostic ambiguity disposition** — `silent_state: true`, `reason_silent: "≥1 §2.x at canonical detected register; §3.1 emits labels per its register-class; §3.2 emits no substantive output per XOR complementarity sealed property"`, `firing_modes: ['cost_drag']`. §3.2 silent at this execution per sub-spec §3.1↔§3.2 XOR complementarity sealed property.

## §5 Successor-cycle class assignment per §4a

Source: session-2 sealed output `successor_class_outputs.json` (sealed at `d7dfbf1`).

- `input_pattern: single_mode`; `assignments` cardinality = 1.
- Single assignment: `class: "cost-model investigation"`, `disposition: "eligible"`, `qualifier: null`, `verbatim_label: "cost-model investigation eligible (gross-vs-realistic decomposition)"`, `source_modes: ['cost_drag']`. Per sub-spec §4a single-mode lookup composition (no §2.f Line 1 qualifier; no §2.d→§2.c elevation; no de-duplication required at single-assignment input).

## §6 Framing-question resolution-pressure assessment per §4b

Source: session-2 sealed output `framing_pressure_outputs.json` (sealed at `d7dfbf1`).

- `pressure_label_set` cardinality = 1 (β union-of-labels per active finding contribution; single firing finding → single pressure object).
- Single pressure object: `pressure_label: "deferred"`, `pivot_direction_dependency: "none"`, `propagation_state: "active"`, `context_qualifiers: []`, `finding_source: "§2.b"`. Basis verbatim from scoping §2.4: *"framing question can stay deferred under (4) indeterminate; empirically-conditioned continuation defensible under any framing"*.

Per sub-spec §4b (vii) "procedure ≠ resolution" discipline, this §4b output is the procedural pressure assessment register-class output, not the framing-question resolution itself. Resolution authority is at Phase 5 SEAL author register (engaged at §8.2 below).

## §7 Substantive-vs-operational admissibility flags per §5

Source: session-2 sealed output `admissibility_flags.json` (sealed at `d7dfbf1`).

- **Substantive availability slot**: `admissible: false`, `basis: "criteria not satisfied at canonical execution"`, `propagation_state: "active"`.
- **Operational availability slot**: `admissible: false`, `basis: "criteria not satisfied at canonical execution"`, `propagation_state: "active"`.

Mechanical routing provenance (machine-readable forensic citation per sub-spec session-2 SEAL schema additions):
- `substantive_evaluated_case: "D2.1_case_a_canonical_5_condition_check"`; `substantive_case_a_canonical_check_passed: false`.
- `operational_evaluated_case: "D2.2_CASE_1_residual_ambiguity_check"`; `operational_case_1_silent_or_terminal_false: true`; `operational_distinct_assignment_count: 1`; `operational_case_1_threshold: 2`.

## §8 SEAL author register narration

The three narration authorities reserved at sealed §5 (x) + §6 (vii)(c) + §4b (vii) — terminal-conclusion invocation, framing-question resolution, and admissibility-flag interpretive narration — are engaged at this Phase 5 closeout SEAL author register and discharged in §8.1, §8.2, §8.3 below. §1 above is the synthesis distillation of these three narrations under reading-order convention, not a fourth independent fire.

### §8.1 Terminal-conclusion invocation decision

**Substantive availability F1**: per sealed admissibility output, `substantive.admissible = False` with mechanical routing provenance `substantive_evaluated_case = D2.1_case_a_canonical_5_condition_check` and `substantive_case_a_canonical_check_passed = False`. The substantive admission criterion at sealed sub-spec §5 D2.1 α HARD LOCK is a biconditional between substantive admissibility and §3.2 canonical Case A state, where canonical Case A state is itself defined by a 5-bullet condition conjunction per sealed §5 D2.1 (label / triggered / canonical_0_mode / suspended_modes / nan_modes); per provenance field the 5-condition canonical check evaluated `False` at canonical execution. No substantive admit at this register.

**Operational availability F1**: per sealed admissibility output, `operational.admissible = False` with mechanical routing provenance `operational_evaluated_case = D2.2_CASE_1_residual_ambiguity_check`, `operational_case_1_silent_or_terminal_false = True`, `operational_distinct_assignment_count = 1`, `operational_case_1_threshold = 2`. The operational admission criterion at sealed sub-spec §5 D2.2 1-CASE α LOCK requires (a) §3.2 Case A terminal_trigger False (or silent state per XOR complementarity) AND (b) §4a output ≥ 2 distinct successor-cycle-class assignments AND (c) those ≥ 2 assignments NOT resolved by §4a-internal precedence. Per provenance the (a) condition holds (silent_or_terminal_false = True) but the (b) ≥ 2 distinct condition fails (`distinct_assignment_count = 1 < threshold = 2`). No operational admit at this register.

**Verdict**: Neither substantive nor operational paradigm-exhaustion terminal-conclusion is invoked at Phase 5 closeout. Per sealed §5 (x) anti-circularity authority, the SEAL author register retains full authority over terminal-conclusion invocation at full-context register, including the authority to decline invocation, defer terminal-conclusion to later cycle, continue exploratory investigation, or route toward additional clarification cycles. The chosen disposition at this register is: **no terminal-conclusion invocation**, consistent with the empty admissible set at canonical execution and absent any sealed co-fire pathway authorizing invocation outside the admissible set. This is a structural finding (criteria mechanically unmet via documented routing), not a strength-of-evidence judgment — §2.b cost_drag fires with very strong statistical evidence as recorded at §3 above.

### §8.2 Framing-question resolution disposition

**Resolution disposition: DEFERRED under framing question (4) indeterminate.**

Per session-2 §4b pressure output `pressure_label = deferred` with basis quoted verbatim from scoping §2.4: *"framing question can stay deferred under (4) indeterminate; empirically-conditioned continuation defensible under any framing"*. The empirical signal pattern at canonical execution (single-mode §2.b firing; no §2.c / §2.d / §2.f findings; no terminal-conclusion finding) maps in scoping §2.4 to the (a)/(b) bucket under which the framing question can remain deferred under (4) indeterminate. At Phase 5 SEAL author register, the framing-question resolution disposition is **DEFERRED under (4) indeterminate**. Per sub-spec §4b (vii) "procedure ≠ resolution" discipline, "deferred under (4) indeterminate" is itself a resolution-class disposition (the SEAL register chose deferment at the current evidence base, on sealed §2.4 authority), not a procedural punt; the framing-question authority is discharged at this register-event boundary.

### §8.3 Admissibility-flag interpretive narration

The Phase 5 diagnostic arc executed the pre-registered procedure mechanically and identified a single firing mode (§2.b cost_drag) with very strong statistical evidence (Wilcoxon signed-rank `p = 1.82e-12` across {7, 13, 15, 17} bps cost-sweep). Session-2 sealed §4a output contains one hybrid assignment (`class = cost-model investigation`, `disposition = eligible`, verbatim_label `cost-model investigation eligible (gross-vs-realistic decomposition)`), conforming to scoping §6 eligible-not-named binding + scoping §4.2 anti-pre-naming binding — successor cycle entry, scope, and timing are NOT predecided at this closeout register; successor cycle entry register-event boundary requires explicit Charlie register authorization per `feedback_authorization_routing.md` hard rule. Neither substantive nor operational admissibility F1 criterion is satisfied at canonical execution per §8.1.

The closeout posture summarized at substantive narrative determination register per sealed §6 (vii)(c) authority: diagnostic procedure executed per pre-registration → signal localized to cost-register single-mode (§2.b cost drag, Wilcoxon `p = 1.82e-12`) → successor-cycle-class assignment recorded at sealed-eligible register without successor cycle entry pre-commitment → framing-question resolution disposition: DEFERRED under (4) indeterminate → no paradigm-exhaustion terminal-conclusion invoked at this register. This narration is not a rescue attempt of Phase 4, not pre-commitment to successor cycle entry, and not a re-litigation of Phase 4 verdict.

## §9 Phase 4 verdict invariance

Phase 5 closeout outputs at §1–§8 above operate at sealed register-class-distinct registers per sealed sub-spec §2.x / §3.x / §4a / §4b / §5 / §6 Phase 4 verdict invariance statements. None of §1–§8 modifies the Phase 4 closeout verdict at 15bps. The Phase 4 verdict is sealed at PHASE4_PLAN §1.5 framework register per scoping §4.6 sealed-content invariance, anchored at [`docs/closeout/PHASE4_RESULTS.md`](PHASE4_RESULTS.md) commit `e8f62f1` + tag `phase4-forward-test-v1`. Phase 5 closeout integration of session-1 + session-2 sealed outputs into terminal-conclusion / framing-resolution / admissibility-flag narration does not retroactively rewrite Phase 4 verdict.

## §10 Locked anchors

- Sealed sub-spec: [`docs/phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md`](../phase5/PHASE5_DIAGNOSTIC_SUBSPEC.md) at commit `49ae7e3`; 1460 lines; sealed across sub-spec drafting cycle sessions 2–16 SEAL register-event boundaries; session-11 + session-15 errata at `aba694b` + `ecb2a70`.
- Sealed scoping decision: [`docs/phase5/PHASE5_SCOPING_DECISION.md`](../phase5/PHASE5_SCOPING_DECISION.md) at commit `697c26b`; entry scoping cycle SEAL.
- Sealed session-1 outputs: `data/phase5_diagnostic/execution_session_1_v1/{indicator_outputs.json, multi_mode_labels.json, ambiguity_disposition.json, execution_summary.md}` at commit `ad35915` (session-1 SEAL).
- Sealed session-2 outputs: `data/phase5_diagnostic/execution_session_2_v1/{successor_class_outputs.json, framing_pressure_outputs.json, admissibility_flags.json, narrative_draft.md, execution_summary.md}` at commit `d7dfbf1` (session-2 SEAL).
- Sealed Phase 4 closeout: [`docs/closeout/PHASE4_RESULTS.md`](PHASE4_RESULTS.md) at commit `e8f62f1` + tag `phase4-forward-test-v1`.
- Sealed engine lineage: engine commit `eb1c87f` (corrected walk-forward); tag `wf-corrected-v1` at commit `3d24fcb`.
- Phase 4 forward-test parquet sha256 anchor (cross-artifact-invariant across the 4 cost-sweep fires): `db4ce1d2a2e5e7b556975837260f7aaa29ee4fd5ddc603690d1bc57912aa7035`; forward window `[2026-01-01T00:00:00Z, 2026-04-16T07:00:00Z]`; 2528 forward bars.

## §11 Run artifacts

- **Session-1 source**: `phase5/labels.py` (§3.1 multi-mode rule tree + §3.2 ambiguity disposition); `phase5/indicators/*.py` (§2.a–§2.f indicator constructors); `phase5/execute_session1.py` (orchestrator). All sealed at `ad35915`.
- **Session-2 source**: `phase5/successor_class.py` (§4a mapping); `phase5/framing_pressure.py` (§4b assessment); `phase5/admissibility.py` (§5 admissibility flags); `phase5/narrative_draft.py` (§6 structural-template traversal); `phase5/execute_session2.py` (orchestrator). All sealed at `d7dfbf1`.
- **Smoke tests**: 76 Phase 5 own tests at `tests/test_phase5_{labels,successor_class,framing_pressure,admissibility,narrative_draft,execute_session2}.py` pass clean (16 session-1 + 60 session-2; verified at session-2 SEAL `d7dfbf1` and re-verified post-pandas-2.2.3-upgrade at Phase 5 closeout authoring register-event).
- **Broader test baseline** (with `tests/test_phase2c_8_1_independent_recompute.py` + `tests/test_run_d7_stage2d_batch.py` ignores per session-15/16 SEAL baseline): 1720 pass / 0 fail under pandas 2.2.3 at Phase 5 closeout authoring register-event.

## §12 Carry-forwards (forward-only log; finalized at successor methodology consolidation cycle)

§12 is a forward-only log register-class. Items below are recorded without entering Path 3 methodology consolidation register-class authority; consolidation cycle entry register-event boundary requires fresh Charlie register authorization per `feedback_authorization_routing.md` hard rule.

1. **`ingestion/validators.py:391` `pct_change()` `fill_method=None` explicit-mode patch candidate** (pandas 2.x default `fill_method='pad'` deprecation; future-removal warning; non-blocking at current release). Surfaced at Phase 5 closeout-precursor Path 2 pandas remediation register-event. Independent code-hygiene register-event candidate or Path 3 sub-item.
2. **`bqplot 0.12.36 ↔ pandas 2.x` dependency conflict in user-env** (jupyter visualization package not in `pyproject.toml`; not imported by Phase 5 / Phase 2C / Phase 4 code paths). Surfaced at Path 2 install. User-env vs project-env separation pattern candidate.
3. **`mechanical_routing_provenance` schema fields binding from session-2 SEAL onward** (`substantive_evaluated_case`, `substantive_case_a_canonical_check_passed`, `operational_evaluated_case`, `operational_case_1_silent_or_terminal_false`, `operational_distinct_assignment_count`, `operational_case_1_threshold`). Machine-readable forensic provenance schema evolution log; downstream consumers (this closeout §7 / §8.1) cite directly per METHODOLOGY_NOTES §1 V7 grep-able citation discipline.
4. **Session-2 reviewer routing experiences**: post-Leg-A re-route threshold standing practice ("no re-trigger if changes are own-recommended + non-substantive"); cross-leg complementary pattern 2nd observed instance at substantive code/work register-class (1st at session-17 sub-spec session-1 SEAL); 4-state `binary_detection_status` discipline (Codex HIGH-2) carry-forward at sealed §6.a representational requirement.
5. **Path 2 SEAL discipline pattern** (env hygiene as independent register-event before arc-level closeout SEAL): empirical precedent at Phase 5 closeout-precursor sequencing (Path 2 → Path 1 → Path 3). Adoptable for future arc-level register-fires where env-drift is asymmetric risk to substantive register fire.

## §13 Anti-pre-naming preserved

Phase 5.1+ successor cycle scope, successor-class invocation, specific successor pathway, timing, and scope are NOT pre-committed at this Phase 5 closeout SEAL register-event boundary per scoping §4.2 anti-pre-naming + scoping §6 eligible-not-named binding + sealed sub-spec §5 (ix) successor-cycle-entry non-pre-emption. The §4a-recorded eligible-class assignment (cost-model investigation eligible) at §5 above does not constitute a successor cycle entry pre-commitment; successor cycle entry register-event boundary requires explicit Charlie register authorization at fresh register-event boundary per `feedback_authorization_routing.md` hard rule.

Phase 5 SEAL author register at this closeout discharges the three reserved narration authorities (terminal-conclusion invocation, framing-question resolution, admissibility-flag interpretive narration) within sealed-evidence-grounding discipline; substantive narrative determination per sealed §6 (vii)(c) authority is exercised at §8.3 above. Methodology consolidation cycle scope is reserved at separate Charlie register-event boundary per Path 3 boundary discipline; methodology codification authority is NOT engaged at this Phase 5 closeout register-event boundary.

---

**End of PHASE 5 DIAGNOSTIC RESULTS (DRAFT; sealed pending reviewer routing + final Charlie register authorization at SEAL author register).**
