# PHASE2C_11 Step 3 — Schema draft (Markdown prose; pre-codification)

**Status:** working draft for dual-reviewer prose pass (ChatGPT structural + Claude advisor substantive). Codex skip per locked routing (Codex first-fires at Step 3 implementation register per [§8.2](PHASE2C_11_PLAN.md), not at schema register).

**Scope:** prose-level field definitions for the three frozen dataclasses introduced at Step 3 — `SimplifiedDSRResult`, `PerCandidateDisposition`, `SensitivityRow`. NO Python code at this register; implementation turn codifies prose into Python after schema seals.

**Lockpoint anchors:** [PHASE2C_11_PLAN.md](PHASE2C_11_PLAN.md) v3.1 (commit `c021c60`) §4.3 + §4.5 + §5.4 + §3.6 + §6 + §2.5 + Step 2 deliverable §5.3 dual-gate forward-flag.

**Authorization chain:** Charlie-register `approved with Synthesized Step 3 sequence` authorizing 7-item adjudication + advisor refinements 1-4 layered on top. Reviewer-suggestion adjudication discipline per [memory `feedback_reviewer_suggestion_adjudication.md`](../..).

---

## 0. Pre-fire register check

This document is **prose schema**, NOT a result computation. Per [§7.3](PHASE2C_11_PLAN.md) hard rule: "Steps 2-5 MUST NOT fire before sub-spec seals at register-precision register." Sub-spec sealed at v3.1 commit `c021c60`. Schema-draft register fires before any `compute_simplified_dsr()` invocation; §3 lockpoints + §4 specification untouched at this register.

**§20 v2 Trigger 1 closure timeline (sharpened per P-L7):**

```
schema seal              → still pre-result (open)
TDD-RED test seal        → still pre-result (open; tests don't fire formula)
implementation code seal → still pre-result (open; code exists, doesn't run)
live computation turn    → CLOSES at compute_simplified_dsr(canonical inputs) invocation
```

Trigger 1 boundary closes **at the canonical formula computation turn (post-implementation, post-test-GREEN)**, not at schema seal nor at TDD-RED turn nor at implementation seal. Until live computation turn fires, §0.4 path remains available for any §3 lockpoint defects surfaced + §20 v2 documented exception path remains available for pre-result structural infeasibility. After live computation fires, §20 closes for this PHASE2C_11 arc per locked discipline; any new §3 lockpoint issue routes strict §0.4 (inconclusive disposition + successor cycle re-pre-registration).

No §3 lockpoint defect is anticipated at schema register — schema is type-level descriptive; canonical formula register fires at implementation turn, not here.

---

## 1. `SimplifiedDSRResult` (frozen dataclass)

**Intent:** canonical Step 3 output; consumed by Step 4 deliverable authoring at canonical phrasing register per [§6.7](PHASE2C_11_PLAN.md). Reproducibility lockpoint: same `SimplifiedDSRInputs` + same `n_trials` → byte-identical `SimplifiedDSRResult` (except for floating-point formatting across platforms; tests use tolerance `1e-9` for floats).

**Fields:**

| Field | Type | Intent | Source / lockpoint |
|---|---|---|---|
| `per_candidate` | `tuple[PerCandidateDisposition, ...]` | per-eligible-candidate disposition records; one entry per Step 2 eligible candidate | [§4.3 Step 4](PHASE2C_11_PLAN.md); count = `n_eligible` (= 154 at canonical fire) |
| `population_disposition` | `Literal["signal_evidence", "artifact_evidence", "inconclusive"]` | population-level disposition from `c_max` candidate per [§4.3 Step 5](PHASE2C_11_PLAN.md) | §3.6 conservative AND-gate at canonical formula register |
| `population_argmax_hash` | `str` (16-char DSL truncated hash) | hypothesis_hash of the candidate yielding `SR_max` (= argmax over eligible subset) | tie-break policy: deterministic at first-occurrence of max; documented in docstring |
| `n_trials` | `int` | trial count param fed to function (must equal 198 per §3.2 dual-gate forward-flag) | [§3.2 lockpoint](PHASE2C_11_PLAN.md) + Step 2 §5.3 |
| `n_eligible` | `int` | size of eligible subset processed (= `len(per_candidate)`) | [§4.4(1)/(2)/(3)](PHASE2C_11_PLAN.md) post-filter count |
| `n_raw` | `int` | full raw population (= `inputs.n_raw`); should equal `n_trials` | dual-gate per Step 2 §5.3 forward-flag |
| `bonferroni_threshold` | `float` | `sqrt(2*ln(n_trials))` per [§4.3 Step 1](PHASE2C_11_PLAN.md); ≈ 3.2522 at N=198 | canonical formula lockpoint |
| `expected_max_sharpe_null` | `float` | `E[max SR \| null]` per [§4.3 Step 2](PHASE2C_11_PLAN.md) Gumbel approximation | canonical formula lockpoint |
| `sharpe_var_used` | `float` | `Var(SR)` consumed at canonical formula (= `inputs.sharpe_var`); recorded for audit-trail | matches `SimplifiedDSRInputs.sharpe_var`; cross-validation register |
| `sensitivity_table` | `tuple[SensitivityRow, ...]` | sensitivity probe rows at N_eff ∈ {198, 80, 40, 5}; primary register reads N_eff=198 row only | [§5.4](PHASE2C_11_PLAN.md) descriptive sensitivity probe |
| `bonferroni_cross_check` | `Mapping[str, bool \| float]` | `{"sr_max": float, "bonferroni_threshold": float, "bonferroni_pass": bool, "dsr_style_pass": bool, "criteria_agree": bool}` | [§6.6](PHASE2C_11_PLAN.md) Bonferroni-vs-DSR-style cross-check disposition |
| `excluded_candidates_summary` | `tuple[tuple[str, int], ...]` sorted by reason key (P-T2 lock; ChatGPT lock + advisor concede) | count of excluded candidates by reason class; structurally immutable, hashable, JSON-serializes natively as nested arrays, sort-by-key deterministic across Python dict-order versions | reason keys synchronized with Step 2 `CandidateExclusion.reason` enum: `{low_trade_count, zero_trades, missing_sharpe, missing_trades}`; expected counts at canonical fire sum to 44 |
| `degenerate_state` | `Literal["none", "n_eligible_zero", "var_zero"] \| None` | edge-case routing per [§4.4(4)](PHASE2C_11_PLAN.md) + [§1.5](PHASE2C_11_PLAN.md) dual-handling: `n_eligible_zero` (Step 2 NaN-state) / `var_zero` (`Var(SR) == 0`); `None` when normal path | when non-`None`, `population_disposition` MUST be `"inconclusive"` |
| `rs_guard_call_count` | `int` | audit-trail count of `check_evaluation_semantics_or_raise()` invocations at function entry | per advisor refinement (b) + P-T1 lock; expected value at canonical fire = `n_eligible` (= 154 at canonical fire). See joint-coverage docstring lockpoint below. |

**P-L3 lockpoint:** `n_trials_lockpoint_verified: bool` field DELETED per advisor anti-pattern correction. Dual-gate verification (`n_trials == EXPECTED_N_RAW` AND `inputs.n_raw == EXPECTED_N_RAW`) is enforced at function entry by raising `ValueError` on failure — invariant-as-state is anti-pattern; result dataclass existence implies invariant held. Test surface (`TestComputeSimplifiedDSRDualGateNRawCheck`) asserts `pytest.raises(ValueError)` on failure path, NOT field-value comparison.

**Wording lockpoint per advisor refinement (c.iii):**

The dataclass docstring MUST include the verbatim wording: *"Primary disposition uses N_eff=198 per §3.2 lockpoint; sensitivity rows in `sensitivity_table` use N_eff ∈ {80, 40, 5} per §5.4 descriptive sensitivity probe; primary lockpoint NOT mutated by sensitivity computation."*

**P-T1 joint-coverage docstring lockpoint (load-bearing per advisor L2):**

The `rs_guard_call_count` field docstring MUST include verbatim: *"expected value at canonical fire = `n_eligible`; full 198-coverage of audit_v1 paths is achieved jointly via Step 2 RS-2 (n_raw=198) + Step 3 RS-3 (n_eligible=154); excluded candidate paths visited at Step 2 only, not re-visited at Step 3 because excluded candidates are not consumed at canonical formula register. Future-caller forward-pointer: if a future Step 3 caller bypasses Step 2 loader (e.g., constructs `SimplifiedDSRInputs` directly via fixture), the n_eligible RS-3 fire alone does NOT cover excluded candidates' paths — those callers MUST handle audit_v1 access patterns separately."*

**P-T3 reproducibility wording lockpoint:**

The `per_candidate` field docstring MUST include verbatim: *"Ordering is **stable** with respect to `SimplifiedDSRInputs.eligible_candidates`; reordering inputs does NOT change `population_disposition` (argmax is order-independent) but DOES change `per_candidate` field iteration order. Two distinct invariants: (i) population_disposition reproducible across input shuffling; (ii) per_candidate iteration tracks input order."*

**P-CG-PUSHBACK:** ChatGPT's proposed `population_argmax_position: int | None` field NOT added. Rejected per 4 reasoning lines: (i) DRY — position derivable from `per_candidate` list iteration via `next(i for i, p in enumerate(result.per_candidate) if p.hypothesis_hash == result.population_argmax_hash)`; (ii) ordering-coupling — position becomes stale if `per_candidate` ordering changes downstream; (iii) test-register sufficient — `TestComputeSimplifiedDSRPopulationDisposition` already asserts `population_argmax_hash` matches the candidate yielding `SR_max`; position-based audit redundant; (iv) future schema evolution risk — hash is absolute identifier, position is relative; relative identifier introduces "position relative to which list?" ambiguity if Step 4 adds second-order argmax (e.g., per-sensitivity-row argmax). Hash-only locked.

---

## 2. `PerCandidateDisposition` (frozen dataclass)

**Intent:** per-candidate canonical-formula-register record at [§4.3 Steps 3-4](PHASE2C_11_PLAN.md). One instance per eligible candidate.

**Fields:**

| Field | Type | Intent | Source / lockpoint |
|---|---|---|---|
| `hypothesis_hash` | `str` (16-char DSL truncated hash) | candidate identifier; matches `CandidateInput.hypothesis_hash` | identifier propagated from Step 2 dataclass |
| `sharpe_ratio` | `float` | `SR_c` consumed unchanged from `CandidateInput.sharpe_ratio` | [§3.3 lockpoint](PHASE2C_11_PLAN.md): canonical scalar from audit_v1 holdout_summary.json |
| `total_trades` | `int` | `T_c` consumed unchanged from `CandidateInput.total_trades` | [§4.3 Step 3](PHASE2C_11_PLAN.md) SE formula input |
| `standard_error` | `float` | `SE(SR_c) = sqrt(1 / (T_c - 1))` per [§4.3 Step 3](PHASE2C_11_PLAN.md) | canonical formula register; assumes IID returns under null |
| `z_score` | `float` | `(SR_c - E[max SR \| null]) / SE(SR_c)` per [§4.3 Step 3](PHASE2C_11_PLAN.md) | canonical formula register |
| `p_value` | `float` | `1 - Φ(z_c)` per [§4.3 Step 3](PHASE2C_11_PLAN.md); computed via `scipy.stats.norm.sf(z_score)` for numerical stability | canonical formula register; bounded `[0.0, 1.0]` |
| `bonferroni_pass` | `bool` | `SR_c > bonferroni_threshold` per [§4.3 Step 4](PHASE2C_11_PLAN.md); strict greater-than | §3.6 conservative AND-gate component |
| `dsr_style_pass` | `bool` | `p_value < 0.05` per [§4.3 Step 4](PHASE2C_11_PLAN.md); strict less-than | §3.6 conservative AND-gate component |
| `disposition` | `Literal["signal_evidence", "artifact_evidence", "inconclusive"]` | per-candidate disposition per [§4.3 Step 4](PHASE2C_11_PLAN.md) | §3.6 4-region AND-gate routing |
| `audit_v1_artifact_path` | `str` | path propagated from `CandidateInput.audit_v1_artifact_path` for traceability | RS-3 audit-trail |

**§3.6 AND-gate routing reference (per §4.3 Step 4 verbatim):**

```
if Bonferroni_pass AND DSR_style_pass: signal_evidence
elif (NOT Bonferroni_pass) AND (NOT DSR_style_pass) AND (p_c >= 0.5): artifact_evidence
else: inconclusive
```

**P-L1 5-region correction (load-bearing canonical-formula-register fix per advisor L1):** the routing pseudocode evaluates 4 boolean dimensions (`Bonferroni_pass × DSR_style_pass`) plus the `p_c ≥ 0.5` sub-condition for artifact qualification, producing **5 distinct §3.6 disposition regions** (NOT 4). Inconclusive splits into 3 sub-regions, each with structurally distinct criteria-disagreement direction:

1. **Region 1 — signal_evidence:** `Bonferroni_pass AND DSR_style_pass`
2. **Region 2 — artifact_evidence:** `(NOT Bonferroni_pass) AND (NOT DSR_style_pass) AND (p_c ≥ 0.5)`
3. **Region 3 — inconclusive (criteria-disagree-Bonferroni-only):** `Bonferroni_pass AND (NOT DSR_style_pass)` — Bonferroni passes but DSR-style p ≥ 0.05
4. **Region 4 — inconclusive (criteria-disagree-DSR-only):** `(NOT Bonferroni_pass) AND DSR_style_pass` — DSR-style p < 0.05 but Bonferroni does not pass
5. **Region 5 — inconclusive (intermediate-p):** `(NOT Bonferroni_pass) AND (NOT DSR_style_pass) AND (p_c < 0.5)` — both criteria fail signal, but p < 0.5 also fails artifact qualification

Note: dispositions are 3-valued (`signal_evidence`, `artifact_evidence`, `inconclusive`); the AND-gate routes 5 regions to 3 dispositions. Region 4 (DSR-style pass but no Bonferroni) was missed in the initial 4-region enumeration; advisor substantive prose-access pass caught the wording-vs-spec drift before schema seal.

`TestComputeSimplifiedDSRBoundaryDispositions` (advisor refinement (f) + P-L1) MUST exercise all **5 regions** explicitly via 5 synthetic candidate constructions, asserting §3.6 AND-gate routes each to the correct disposition Literal value.

---

## 3. `SensitivityRow` (frozen dataclass)

**Intent:** one row per N_eff value at the [§5.4](PHASE2C_11_PLAN.md) sensitivity table. Descriptive register only; primary disposition reads N_eff=198 row only.

**Fields:**

| Field | Type | Intent | Source / lockpoint |
|---|---|---|---|
| `n_eff` | `int` | effective N for this sensitivity probe; one of {198, 80, 40, 5} | [§5.4](PHASE2C_11_PLAN.md) |
| `bonferroni_threshold` | `float` | `sqrt(2*ln(n_eff))` | per-row formula re-evaluation at this N_eff |
| `expected_max_sharpe_null` | `float` | E[max SR \| null] re-evaluated at this `n_eff` (`sharpe_var` held constant) | per-row formula re-evaluation |
| `argmax_p_value` | `float` | `p_max` recomputed for the argmax candidate at this n_eff | per-row formula re-evaluation; NOT a separate argmax search (argmax candidate is fixed across rows) |
| `argmax_disposition_descriptive` | `Literal["signal_evidence", "artifact_evidence", "inconclusive"]` | disposition the argmax candidate WOULD receive at this n_eff per §3.6 AND-gate; **descriptive only** | NOT primary; primary register reads N_eff=198 row only |
| `register_label` | `Literal["primary", "sensitivity"]` | primary at n_eff=198; sensitivity at n_eff ∈ {80, 40, 5} | [§5.4](PHASE2C_11_PLAN.md) lockpoint |

**Wording lockpoint per advisor refinement (c.iii) at sensitivity table register:**

The dataclass docstring + Step 3 deliverable when describing this table MUST include verbatim wording: *"Primary disposition uses N_eff=198 per §3.2 lockpoint; sensitivity rows at N_eff ∈ {80, 40, 5} are §5.4 descriptive sensitivity probe; sensitivity rows do NOT mutate primary lockpoint."*

Sensitivity narrative interpretation (e.g., "sensitivity rows show pattern X") is **deferred to Step 4 deliverable register** per advisor refinement (c.ii); Step 3 emits raw sensitivity values + register labels only.

---

## 4. Disposition `Literal` enum value list (canonical at this register)

The three valid `disposition` values across `PerCandidateDisposition.disposition`, `SimplifiedDSRResult.population_disposition`, and `SensitivityRow.argmax_disposition_descriptive`:

- `"signal_evidence"` — §3.6 conservative AND-gate signal pass
- `"artifact_evidence"` — §3.6 conservative AND-gate artifact pass
- `"inconclusive"` — any disposition not meeting strict signal-AND-gate or artifact-AND-gate

Implementation turn codifies as `typing.Literal["signal_evidence", "artifact_evidence", "inconclusive"]`. Test surface uses the literal string values for comparison.

**Cross-section consistency:** all three dataclasses use the identical Literal type alias; implementation turn defines `DispositionLiteral` once and reuses across the three dataclasses.

---

## 5. Exclusion-reason enum synchronization with Step 2

**Step 2 canonical reason classes** (current state at [`backtest/evaluate_dsr.py`](../../backtest/evaluate_dsr.py); string literals):
- `"low_trade_count"` (§4.4(1); 0 < T_c < MIN_TRADES_FOR_PRIMARY)
- `"zero_trades"` (§4.4(2); T_c == 0)
- `"missing_sharpe"` (§4.4(3); sharpe_ratio missing/null/non-finite)
- `"missing_trades"` (companion to §4.4(3); total_trades missing/non-finite/non-integral)

**P-T4 lockpoint (Charlie-register approved Path I; both reviewers converged):**

`excluded_candidates_summary` keys MUST match this set verbatim. **Path I LOCKED:** Step 3 documents the expected key set via docstring reference to Step 2 `CandidateExclusion.reason`; runtime construction uses string literals matching Step 2. Step 2 dataclass NOT mutated — Path II (cross-Step retrofit upgrading Step 2 string-literal `reason` to `typing.Literal`/`StrEnum`) explicitly REJECTED at Step 3 register per advisor cross-Step-retrofit risk argument: would touch sealed Step 2 commit + tests + `_step2_inputs.json` schema v2 surface; out of Step 3 scope.

**ChatGPT defensive provision:** Step 3 implementation MAY introduce a local Step 3-internal type alias `ExclusionReasonLiteral = Literal["low_trade_count", "zero_trades", "missing_sharpe", "missing_trades"]` if Codex first-fire flags string-literal weakness at canonical formula register. The alias is Step 3-internal — does NOT modify Step 2 `CandidateExclusion.reason: str` field; Step 2 sealed dataclass surface preserved. If Codex does NOT flag, defensive provision NOT required and module surface stays minimal per YAGNI.

---

## 6. Cross-reference register for canonical lockpoints

Schema-draft register-precision verification — every dataclass field above traces back to a §-lockpoint:

| Field | Plan §-lockpoint | Verified |
|---|---|---|
| `bonferroni_threshold` | §4.3 Step 1 + §3.5 + §3.6 | ✓ |
| `expected_max_sharpe_null` | §4.3 Step 2 (Gumbel approximation; canonical) | ✓ |
| `standard_error` | §4.3 Step 3 (SE = sqrt(1/(T_c - 1)); IID under null) | ✓ |
| `z_score` | §4.3 Step 3 | ✓ |
| `p_value` | §4.3 Step 3 (1 - Φ(z_c)) | ✓ |
| `bonferroni_pass` | §4.3 Step 4 | ✓ |
| `dsr_style_pass` | §4.3 Step 4 | ✓ |
| `disposition` Literal (3 values; AND-gate routes 5 regions to 3 dispositions) | §4.3 Step 4 + §3.6 + §6.1 + §6.6 | ✓ |
| `population_disposition` | §4.3 Step 5 | ✓ |
| `population_argmax_hash` | §4.3 Step 5 (`c_max = argmax(SR_observed)`) | ✓ |
| `sensitivity_table` rows | §5.4 + §3.2 (primary at n_eff=198) | ✓ |
| `bonferroni_cross_check` | §6.6 | ✓ |
| `excluded_candidates_summary` | §4.4(1)/(2)/(3) + Step 2 `CandidateExclusion` | ✓ |
| `degenerate_state` | §4.4(4) + §1.5 dual-handling | ✓ |
| `rs_guard_call_count` | §2.5 + §4.5 RS-3 lockpoint + advisor refinement (b) + P-T1 joint-coverage docstring | ✓ |

**P-L3 lockpoint:** `n_trials_lockpoint_verified` row REMOVED per anti-pattern correction (invariant-as-state); function entry `raise ValueError` enforces dual-gate; audit-trail covered by commit history + test coverage.

---

## 7. TBD register — all schema-register TBDs LOCKED at this draft register

Per Charlie-register adjudication at schema-review turn (8 patches + advisor pushback + advisor concede approved):

| ID | Item | Locked decision | Patch ID |
|---|---|---|---|
| T1 | `rs_guard_call_count` expected at canonical fire | `n_eligible` (= 154); joint-coverage docstring required | P-T1 |
| T2 | `excluded_candidates_summary` type | `tuple[tuple[str, int], ...]` sorted by reason key | P-T2 |
| T3 | `per_candidate` ordering | input order; reproducibility wording lockpoint | P-T3 |
| T4 | Step 2 `CandidateExclusion.reason` upgrade (Path II) | REJECTED (Path I locked); ChatGPT local `ExclusionReasonLiteral` defensive provision available if Codex flags | P-T4 |

No outstanding TBDs at schema register. All schema-level decisions sealed; downstream open items (Codex first-fire patches at Step 3 implementation, e.g., potential `ExclusionReasonLiteral` introduction) operate at implementation register, not schema register.

---

## 8. Schema-review turn routing

Per [§8.1](PHASE2C_11_PLAN.md) reviewer architecture + Charlie-register lock at adjudication turn:
- **ChatGPT structural pass:** field count completeness; lockpoint cross-references; type consistency across the three dataclasses; Literal value consistency; TBD register completeness; Path I lock verification at §5.
- **Claude advisor substantive prose-access pass:** wording precision at lockpoint docstrings (especially the §3.2 + §5.4 wording lockpoints at `SimplifiedDSRResult` + `SensitivityRow`); §3.6 5-region AND-gate routing precision (P-L1 correction verification); advisor-refinement (a)-(d) incorporation verification; anchoring-bias audit at field intent docstrings (no result-narrative seeding).
- **Codex skip:** schema register; Codex first-fires at Step 3 implementation turn per [§8.2](PHASE2C_11_PLAN.md) routing.

Both reviewers must independently authorize before TDD-RED turn fires.

---

## 9. Anti-pattern audit at schema register

Per [METHODOLOGY_NOTES.md §16](../discipline/METHODOLOGY_NOTES.md) anchor-prose-access discipline + §17 procedural-confirmation defect class + §18 §7 carry-forward density + §19 spec-vs-empirical-reality finding pattern + §20 v2 Trigger 1 closes-at-Step-3-fire:

- **§16 anchor-prose-access:** schema authored against §4.3 + §4.5 + §5.4 + §3.6 + §6 + §2.5 verbatim cross-reference at row-wise lockpoint table (Section 6); not authored from memory.
- **§17 procedural-confirmation:** schema is prose-only at this register; no implementation fires; reviewer pass focuses on schema correctness, not procedural step recursion.
- **§18 §7 carry-forward:** schema does NOT introduce new carry-forward observations at this register; if schema-review surfaces concerns at canonical-formula register, those route to §0.4 (NOT §20 — Trigger 1 closes at Step 3 fire which has not yet fired but is the immediate next compute boundary).
- **§19 spec-vs-empirical-reality (P-L1-β instance logging):** schema-draft register surfaced a §19 instance at advisor substantive prose-access pass — initial schema enumerated 4 §3.6 disposition regions; advisor caught wording-vs-spec drift (Region 4: NOT-Bonferroni AND DSR-style pass missed; "0.05 ≤ p < 0.5" wording lumped Region 4 with Region 5). Corrected at P-L1 patch to 5 regions. Defect class: schema-vs-spec wording drift at canonical-formula-register caught by reviewer prose-access pass before schema seal. **Instance number TBD: schema-register §19 instance 1 vs cumulative §19 count at PHASE2C_11 (which would advance from 8 → 9)** — schema-register catch register-class characterization (deliverable-register vs schema-register; same cumulative pool vs separate) deferred to future methodology consolidation cycle for adjudication; placeholder logged here for cross-cycle traceability.
- **§20 v2 Trigger 1:** still pre-result at this register; §0.4 + §20 paths both available. Trigger 1 closes at live computation turn per §0 timeline (NOT at schema seal nor TDD-RED nor implementation seal). After live computation fires, §20 closes for this PHASE2C_11 arc per locked discipline.
- **§6.2 forbidden phrases:** schema has no result narrative; forbidden-phrases discipline applies at Step 4 deliverable, not here. But anti-anchoring discipline applies: schema field intent docstrings MUST NOT seed result interpretation (e.g., field intent must NOT say "field captures the artifact-like nature of the population"). Schema reviewed at this register: clean — no field intent docstring contains result-direction language.

---

## 10. End of schema draft (post-patch register)

Schema-draft turn output complete with 9 patches applied per Charlie-register authorization (P-L1-α + P-L1-β + P-T1 + P-T2 + P-T3 + P-T4 + P-L3 + P-L7 + P-CG-PUSHBACK + P-§7). All TBDs locked; no outstanding schema-register adjudications. Standing by for **final dual-reviewer pass on patched draft** (ChatGPT structural pass + advisor final substantive pass) per stale-state risk mitigation discipline (§20 v2 precedent). After dual-reviewer convergence on patched draft + Charlie-register schema-seal authorization, TDD-RED turn fires (13 failing test classes per locked routing; boundary disposition class covers 5 regions explicitly per P-L1).
