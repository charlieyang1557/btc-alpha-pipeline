# Phase 5 Diagnostic Sub-Spec

> **Status:** WORKING DRAFT (session-2; §0 + §1 authoring)
> **Cycle:** Phase 5 sub-spec drafting cycle (Path 1 per scoping decision §6 successor cycle eligible-not-named slot)
> **Meta-plan:** [`docs/superpowers/plans/2026-05-09-phase5-diagnostic-subspec.md`](../superpowers/plans/2026-05-09-phase5-diagnostic-subspec.md) (sealed at `0e305bc`)
> **Spec source:** [`PHASE5_SCOPING_DECISION.md`](PHASE5_SCOPING_DECISION.md) (sealed at `697c26b` 2026-05-10T01:29:10Z)

---

## §0 — Scope + structure

This sub-spec operationalizes the Phase 5 diagnostic-attribution procedure pre-registered at [`PHASE5_SCOPING_DECISION.md`](PHASE5_SCOPING_DECISION.md) §2.1–§2.5. Its purpose is to lock — before any diagnostic execution fires — the indicator-extraction procedures, cutoffs, multi-mode coexistence rules, ambiguity-handling rules, successor-cycle-class mapping, framing-question resolution-pressure assessment procedure, terminal-conclusion criteria, and attribution-report structure that Phase 5 will operate under.

Scope is constrained by scoping decision §2.2 operationalization-freeze: thresholds must be frozen before any diagnostic execution can fire. This sub-spec does NOT execute the diagnostic; this sub-spec does NOT resolve framing-question (1)/(2)/(3)/(4); this sub-spec is the procedural lockpoint upstream of the diagnostic fire.

Section-by-section:

- **§1 Locked inputs** — existing sealed artifacts the diagnostic consumes; derived-vs-new-data boundary per scoping §4.1.
- **§2 Per-mode operationalization (§2.a–§2.f)** — indicator extraction + cutoffs per failure mode in scoping §2.1 taxonomy. Load-bearing.
- **§3 Multi-mode rules + diagnostic ambiguity** — §3.1 coexistence (multiple modes positively detected) + §3.2 ambiguity (procedure fails to reliably separate).
- **§4a Successor-cycle-class mapping** — operationalization of scoping §2.3 mapping.
- **§4b Framing-question resolution-pressure assessment procedure** — operationalization of scoping §2.4. Procedure ≠ resolution; resolution happens at Phase 5 SEAL based on diagnostic findings.
- **§5 Terminal-conclusion criteria** — operationalization of scoping §2.5; preserves substantive-availability + operational-availability distinction per scoping §2.5 / Mod-pass-2 F1 disambiguation.
- **§6 Attribution report deliverable structure** — Phase 5 closeout deliverable framework; substantively depends on §5.
- **§7 Verification + reviewer disposition** — V# verification chain to be fired at sub-spec SEAL pre-fire boundary; reviewer pass routing at sub-spec SEAL.
- **§8 Cross-references** — anchored references to sealed corpus.

---

## §1 — Locked inputs

Phase 5 diagnostic procedure consumes only sealed artifacts at Phase 5 cycle entry. Source set is frozen; acquisition of new empirical data is prohibited per scoping §4.1.

**Sealed inputs binding the diagnostic procedure:**

- **Phase 4 null result anchor** — closeout deliverable at [`docs/closeout/PHASE4_RESULTS.md`](../closeout/PHASE4_RESULTS.md) sealed at `e8f62f1`; tag `phase4-forward-test-v1` at seal commit; finding content + per-stratum statistics consumed by §2 / §6 from this sealed source.
- **Candidate-cohort reference** — `data/phase4_scoping/cohort_a_candidate_reference.csv` sealed at `11b39f2`; 39 candidates from PHASE2C_15 `cohort_a` with Phase 4 analysis partition per PHASE4_PLAN §1.3 (calendar_effect n=22, non-calendar n=17).
- **Engine + WF lineage anchor** — engine commit `eb1c87f` (corrected walk-forward implementation); lineage chain anchor at tag `wf-corrected-v1` (commit `3d24fcb`; anchors engine fix `eb1c87f` + lineage guard `5f53ee5`).
- **Phase 4 forward-test artifacts** — `data/phase2c_evaluation_gate/phase4_forward_2026_{07,13,15,17}bps_v1/` cost-sweep + `data/phase2c_evaluation_gate/phase4_smoke_15bps_v0/` smoke; parquet anchor `db4ce1d2a2e5e7b556975837260f7aaa29ee4fd5ddc603690d1bc57912aa7035` invariant across artifacts; forward window `[2026-01-01T00:00:00Z, 2026-04-16T07:00:00Z]`; 2528 forward bars.
- **PHASE2C_15 main-fire artifacts** — sealed per-regime evaluation-gate artifacts at `data/phase2c_evaluation_gate/phase2c_15_main_fire_{bear_2022,audit_2024,eval_2020,eval_2021}_v1[_filtered]/` + walk-forward at `data/phase2c_walkforward/batch_phase2c_15_main_fire_combined_corrected/`.
- **Sealed prior-cycle corpus** — closeout MDs (PHASE2C_10/11/12/13/15) + PHASE2C_14 sub-spec MDs at `docs/phase2c/PHASE2C_14_{PLAN,SCOPING_DECISION}.md` + METHODOLOGY_NOTES.md sealed sections + CLAUDE.md Phase Marker entries through Phase 5 entry SEAL. Treated as read-only within the Phase 5 diagnostic cycle per scoping §4.6.

**Derived-vs-new-data boundary** (per scoping §4.1; §8 will anchor the verbatim source quote):

- **ALLOWED**: derived statistics + diagnostic computations from sealed artifacts (re-aggregations, alternative metric profiles on existing per-candidate trade data, statistical decomposition of existing forward Sharpe distributions, regime-conditioning of existing cohort indicators, etc.).
- **NOT ALLOWED**: additional BTC OHLCV history beyond what is already on disk, additional candidate generation, additional regime data, additional Critic/Proposer API calls, new methodology codification.

**Scope binding:** All downstream sections (§2–§6) shall consume only the inputs declared in this section; classification of "derived" vs "new" per the boundary above is binding throughout.
