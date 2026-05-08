# PHASE2C_15 Implementation Arc Step 3 — PHASE2C_12 Comparison Artifact Reconstruction Results

**Status:** SEAL pending — Q-S135 SEAL bundle authorization required at Charlie register per `feedback_authorization_routing.md` hard rule.

**Cycle scope:** Path 1 per Q-S131 (A) Charlie register authorization — PHASE2C_12 comparison artifact reconstruction at canonical location `data/phase2c_evaluation_gate/comparison_phase2c_12_v1/` per Step 2 sub-spec [`PHASE2C_15_STEP2_PLAN.md`](PHASE2C_15_STEP2_PLAN.md) §3.1 5-step procedure; HARD STOP byte-level verification on (i) headline 8/197 anchor (PHASE2C_12_RESULTS.md:111) AND (ii) per-regime breakdown (28, 82, 65, 43) anchor (PHASE2C_12_RESULTS.md §3.1). Local artifact reconstruction; no API spend; no new model/evaluation fire; no irreversible empirical PHASE2C_15 state.

---

## §1 Procedure execution summary

Steps 1-4 of §3.1 executed sequentially; Step 5 = this deliverable + SEAL bundle pending Q-S135 authorization.

**Step 1 — Unfiltered tier presence verified (4/4 dirs at canonical paths):**

| Regime | Path | State |
|---|---|---|
| bear_2022 | `data/phase2c_evaluation_gate/phase2c_12_audit_v1/` | present (audit confirmed) |
| validation_2024 | `data/phase2c_evaluation_gate/phase2c_12_audit_2024_v1/` | present |
| eval_2020 | `data/phase2c_evaluation_gate/phase2c_12_eval_2020_v1/` | present |
| eval_2021 | `data/phase2c_evaluation_gate/phase2c_12_eval_2021_v1/` | present |

**Step 2 — Filtered tier dirs generated via `scripts/filter_evaluation_gate.py` × 4 invocations** (threshold pinned at module-level `MIN_TOTAL_TRADES = 20`; per-candidate JSONs byte-identical to primary; aggregate recomputed):

| Regime | primary_total | included | excluded |
|---|---|---|---|
| bear_2022 (audit_v1) | 197 | 117 | 80 |
| validation_2024 (audit_2024_v1) | 197 | 113 | 84 |
| eval_2020 (eval_2020_v1) | 197 | 110 | 87 |
| eval_2021 (eval_2021_v1) | 197 | 117 | 80 |

All 4 regimes show `primary_total = 197` (consistent with Anchor 1 n_candidates).

**Step 3 — `scripts/compare_multi_regime.py` invoked over 4 unfiltered + 4 filtered tier dirs**:

```
python -m scripts.compare_multi_regime \
  --regime-input v2.regime_holdout=data/phase2c_evaluation_gate/phase2c_12_audit_v1 \
  --regime-input v2.validation=data/phase2c_evaluation_gate/phase2c_12_audit_2024_v1 \
  --regime-input evaluation_regimes.eval_2020_v1=data/phase2c_evaluation_gate/phase2c_12_eval_2020_v1 \
  --regime-input evaluation_regimes.eval_2021_v1=data/phase2c_evaluation_gate/phase2c_12_eval_2021_v1 \
  --filtered-input v2.regime_holdout=data/phase2c_evaluation_gate/phase2c_12_audit_v1_filtered \
  --filtered-input v2.validation=data/phase2c_evaluation_gate/phase2c_12_audit_2024_v1_filtered \
  --filtered-input evaluation_regimes.eval_2020_v1=data/phase2c_evaluation_gate/phase2c_12_eval_2020_v1_filtered \
  --filtered-input evaluation_regimes.eval_2021_v1=data/phase2c_evaluation_gate/phase2c_12_eval_2021_v1_filtered \
  --output-dir data/phase2c_evaluation_gate/comparison_phase2c_12_v1
```

Output: `n_candidates=197 cohort_a_unfiltered=8 cohort_a_filtered=6 cohort_c_unfiltered=88`.

**Step 4 — HARD STOP verification fired** (results in §2).

---

## §2 HARD STOP verification result — ALL CLEAR at byte-level register-precision

**Anchor 1 (headline 8/197) — VERIFIED:**

| Field | Reconstructed value | PHASE2C_12_RESULTS.md:111 anchor | Match |
|---|---|---|---|
| `cohort_a_cardinality_unfiltered` | **8** | 8 | ✓ |
| `totals.n_candidates` | **197** | 197 | ✓ |

Verbatim cite from [`docs/closeout/PHASE2C_12_RESULTS.md:111`](../closeout/PHASE2C_12_RESULTS.md): *"**8 of 197 candidates passed all 4 regimes** = 4.06% AND-gate rate."*

**Anchor 2 (per-regime breakdown 28/82/65/43) — VERIFIED:**

| Regime | Reconstructed pass count | PHASE2C_12_RESULTS.md §3.1 anchor | Match |
|---|---|---|---|
| bear_2022 | **28** | 28 | ✓ |
| validation_2024 | **82** | 82 | ✓ |
| eval_2020_v1 | **65** | 65 | ✓ |
| eval_2021_v1 | **43** | 43 | ✓ |

Reconstructed values derived by counting `holdout_<regime>_passed == True` rows per regime in `comparison_matrix.csv` (197 rows total).

**Internal cross-check (sanity):**

`pass_count_distribution.unfiltered = {0: 88, 1: 41, 2: 35, 3: 25, 4: 8}` → sum = 197 ✓ (matches n_candidates); cohort `4-regimes-passed` = 8 ✓ (matches `cohort_a_cardinality_unfiltered`).

All HARD STOP checks clear at byte-level: headline count (8), denominator (197), and per-regime breakdown (28, 82, 65, 43) all match. No drift detected. Per Step 2 sub-spec §3.1 step 4: "Both must pass for verification clear" — both anchors passed; verification clear.

---

## §3 Canonical artifact reference

**Path:** `data/phase2c_evaluation_gate/comparison_phase2c_12_v1/`

**Contents:**
- `comparison_summary.json` (5,175 bytes; `comparison_schema_version = comparison_schema_v2`; `produced_at_utc = 2026-05-08T06:14:34Z`)
- `comparison_matrix.csv` (46,219 bytes; 197 rows + header; per-candidate per-regime pass/fail + sharpe + filter_state + total_trades)

**Filtered tier dirs persisted at canonical paths:**
- `data/phase2c_evaluation_gate/phase2c_12_audit_v1_filtered/` (117 included candidates)
- `data/phase2c_evaluation_gate/phase2c_12_audit_2024_v1_filtered/` (113)
- `data/phase2c_evaluation_gate/phase2c_12_eval_2020_v1_filtered/` (110)
- `data/phase2c_evaluation_gate/phase2c_12_eval_2021_v1_filtered/` (117)

**Retroactive-authority clarification** (per Step 2 sub-spec §3.1 C6): the reconstructed PHASE2C_12 comparison artifact is reference-only and does not retroactively alter PHASE2C_12 canonical closeout claims. [`PHASE2C_12_RESULTS.md`](../closeout/PHASE2C_12_RESULTS.md) remains the canonical authority on PHASE2C_12 results; the reconstructed artifact serves byte-level reproducibility of PHASE2C_15 PLAN §1.4 comparison input.

---

## §4 Forward-binding observation

PHASE2C_15 PLAN §1.4 Fisher exact comparison input is now byte-level reproducible from canonical artifact at `comparison_phase2c_12_v1/` rather than prose-only citation to PHASE2C_12_RESULTS.md. The compare_multi_regime.py + filter_evaluation_gate.py pipeline is deterministic over fixed inputs; PHASE2C_15 fire's `(success_count, valid_N)` computed via the same pipeline against the same convention will be byte-level comparable to PHASE2C_12 baseline `(8, 197)` at register-precision.

This closes the apples-to-apples register-precision question for PLAN §1.4 Fisher exact comparison. Combined with V-1 critic-mode forensic (state-α confirmed at Step 2 register; PHASE2C_15 fires WITHOUT critic mode) + V-2 engine lineage compliance ((V-2-clean) at PHASE2C_15-relevant scope at Step 2 register) + Path 1 byte-level reproducibility (HARD STOP all clear at this register), the three substantive forensic prerequisites for PHASE2C_15 fire are resolved at register-precision.

Implementation arc Step 4+ entry adjudication boundary is register-class-distinct from this Path 1 closure register; Charlie register adjudicates Step 4 framing at fresh register-event boundary post-Q-S135 SEAL per anti-pre-naming option (ii) preservation.

---

## §5 Anchors

- **Step 2 sub-spec §3.1 procedure spec:** [`docs/phase2c/PHASE2C_15_STEP2_PLAN.md`](PHASE2C_15_STEP2_PLAN.md) sealed at `e1aba42`
- **PLAN §1.4 Fisher exact specification:** [`docs/phase2c/PHASE2C_15_PLAN.md`](PHASE2C_15_PLAN.md) sealed at `df08fa5`
- **PHASE2C_12 closeout anchors (HARD STOP cite source):** [`docs/closeout/PHASE2C_12_RESULTS.md`](../closeout/PHASE2C_12_RESULTS.md) line 111 + §3.1 lines 104-107; sealed at `1989c85` + tag `phase2c-12-breadth-expansion-v1`
- **Authorization register:** Q-S131 (A) Path 1 entry + Q-S132 (A) sequential cadence + Q-S133 (A) 2-reviewer routing + Q-S134 (A) Step 5 deliverable authoring (4 Charlie register authorization boundaries cumulative at Path 1 cycle internal)
- **Reviewer pass cycle** (closed at convergence; APPROVE WITH MINOR PATCHES at both registers; 3 patches landed C2/C4/C5 + 1 PUSHBACK C3 at register-precision + 4 NO ACTION): ChatGPT structural overlay + Claude advisor full-prose-access; Codex SKIP per [`feedback_codex_review_scope.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_codex_review_scope.md) (forensic verification deliverable register-class)

---

**End of Step 3 deliverable WORKING DRAFT.** SEAL bundle pending Q-S135 Charlie register authorization (deliverable seal commit + Phase Marker advance commit + bundled push; NO tag per Step deliverable SEAL precedent at PHASE2C_13 Step 1-11 + PHASE2C_12 Step 1-2).
