# PHASE2C_11 Step 2 Deliverable — Simplified DSR-Style Screen Inputs

**Status: WORKING DRAFT v3 — post-Codex-substantive-code-review patches applied; re-verification CLEAN; pre-final-reviewer-pass; pre-seal.**

**Anchor:** PHASE2C_11_PLAN.md v3.1 sealed at commit `c021c60`; METHODOLOGY_NOTES §20 v2 codified at commit `33731ce`; Step 1 deliverable v2 sealed at commit `61c17dc`. Step 2 fires per Charlie-register authorization "authorize step 2"; **post-Codex-review patches applied per Codex REQUEST-CHANGES verdict (1 CRITICAL + 3 HIGH + 3 MEDIUM + 1 LOW; all 8 findings APPROVED at register-precision per `feedback_reviewer_suggestion_adjudication.md`; zero pushbacks).**

**v3 vs v1 deliverable changes (Codex review trail + advisor re-pass):** v1 was the initial post-Step-2-execution draft; advisor substantive pass cleared with two observation incorporations (ratio 0.30 + §20 v2 first-check). v2 was implicit (within-arc with the deliverable v1 already updated). **v3 records the Codex substantive code review + post-patch re-verification + Claude advisor substantive re-pass with three concerns incorporated:** L1 must-fix at §5.1.2 framing ("PASSED" → "NON-INVOCATION confirmed; defers to next candidate surface" — preserves §20 narrow-scope discipline + anti-dilution rationale citing §5 failure mode + ChatGPT seal-note); L2 forward-semantic note at §5.1.1 row #3 (`missing_trades` reason class canonically empty at audit_v1 / 0 hits / forward-batch defensive coverage); L3 schema-bump audit-trail note at §5.1.1 (v1 was working-tree-only / never sealed / clean overwrite at this register / future post-seal schema bumps require new file). Cross-trigger forward-flag at §5.3 for Step 3 author (`inputs.n_raw == EXPECTED_N_RAW` second-line check at `compute_simplified_dsr()` entry; dual-gate preserves §3.2 lockpoint integrity if future caller forgets `expected_n_raw=198` kwarg).

All Codex findings adjudicated at register-precision per §5.1.1 trail below; no §3 lockpoints touched (substantive pass/fail criteria unchanged); patches operate at code-defensiveness register (CRITICAL #1 lockpoint enforcement; HIGH #2 NaN/inf rejection; HIGH #3 reason-class precision; HIGH #4 CSV-missing audit clarity; MEDIUM #5 int-helper defensiveness; MEDIUM #6 + #7 expanded test coverage; LOW #8 deliverable wording precision).

**Hard scope per [PHASE2C_11_PLAN §7.1 Step 2 + §7.3]:** input prep ONLY — no Step 3 simplified DSR-style screen disposition fires at Step 2. Eligible-subset table + cross-trial Sharpe distribution descriptors + §4.4 exclusion record + §3.4 + §4.4(5) v3.1 reframed cross-validation diagnostics.

---

## §1 Implementation summary

### §1.1 New module surface at `backtest/evaluate_dsr.py`

Three frozen dataclasses + one loader function added (per [PHASE2C_11_PLAN §4.5] module scope decision: extend `evaluate_dsr.py`, do NOT create new module at simplified MVD register):

- `CandidateInput` (frozen dataclass) — per-candidate input for the simplified DSR-style screen per §4.2 inputs table; carries `hypothesis_hash`, `sharpe_ratio`, `total_trades`, `audit_v1_artifact_path`, plus descriptive fields (`name`, `theme`, `lifecycle_state`).
- `CandidateExclusion` (frozen dataclass) — per-candidate §4.4 edge-case exclusion record with pre-registered `reason` string.
- `SimplifiedDSRInputs` (frozen dataclass) — Step 2 deliverable structure carrying eligible candidates, excluded candidates, n_raw, n_eligible, cross-trial Sharpe distribution descriptors, and JSON-vs-CSV documented discrepancies.
- `load_audit_v1_candidates(audit_v1_dir, csv_path) -> SimplifiedDSRInputs` — loader with RS-2 lockpoint at every audit_v1 holdout_summary.json consumption + §4.4 edge-case filtering in pre-registered order + §3.4 + §4.4(5) v3.1 reframed cross-validation.

Module-level lockpoint constants:

- `JSON_VS_CSV_TOLERANCE = 1e-6` — v3.1 reframed register per Step 1 §19 Instance 6 + METHODOLOGY_NOTES §20.5 Instance 1 + Charlie-register authorization on P2 + precedent doc path. Calibrated to canonical-artifact register-precision floor (CSV 6-decimal storage; ~5e-7 max physical |delta|) per §20 Trigger 5.
- `MIN_TRADES_FOR_PRIMARY = 5` — §4.4(1) pre-registered exclusion threshold.
- `EXPECTED_N_RAW = 198` — §3.2 lockpoint (canonical PHASE2C_8.1 audit_v1 candidate count).

### §1.2 RS-2 lockpoint discipline

Every audit_v1 `holdout_summary.json` consumed by the loader passes through `backtest.wf_lineage.check_evaluation_semantics_or_raise(summary, artifact_path=...)` BEFORE any field access (per §0.3 + §2.5 + §7.1 RS-2 lockpoint + Section RS canonical hard prohibition at [docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md]). RS-2 attestation failures raise `ValueError`; the loader does NOT silently skip a failing candidate — failure indicates upstream data corruption requiring investigation, not a routine exclusion.

### §1.3 §4.4 edge-case filtering applied in pre-registered order

For each candidate the loader applies, in pre-registered §4.4 order:

1. **§4.4(3) missing/null Sharpe** → `excluded[reason="missing_sharpe"]`
2. **§4.4(2) zero trades (`T_c == 0`)** → `excluded[reason="zero_trades"]`. Note: zero-trade candidates also satisfy §4.4(1) numerically, but the more specific reason is recorded for audit clarity.
3. **§4.4(1) low trade count (`T_c < 5`)** → `excluded[reason="low_trade_count"]`

Eligible candidates pass through to the Sharpe distribution computation + cross-validation cross-check.

### §1.4 §3.4 + §4.4(5) v3.1 reframed cross-validation

For each eligible candidate (post-§4.4(1)/(2)/(3)) the loader cross-checks the JSON's `holdout_metrics.{sharpe_ratio, max_drawdown, total_return, total_trades}` and `wf_test_period_sharpe` fields against the corresponding `holdout_results.csv` row columns. Discrepancies at `|delta| > 1e-6` are appended to `SimplifiedDSRInputs.discrepancies_documented` for descriptive reviewer routing; **candidates are NOT auto-excluded under v3.1 lockpoint** (per §3.4 + §4.4(5) reframe authorized at v3.1 patch).

### §1.5 §4.4(4) Var(SR)=0 boundary (clarified per Codex LOW #8)

Per §4.4(4): if `Var(SR) == 0` across the eligible subset (extreme degenerate case), the screen is undefined per spec and Step 3 reports inconclusive disposition. The loader handles this in two distinct sub-cases per Codex review LOW-finding-#8 disambiguation:

- **n_eligible == 0** (no candidate survives §4.4 filtering at all): the loader returns SimplifiedDSRInputs with NaN sharpe scalars (mean / var / std / min / max / median = NaN); Step 3 detects this via `n_eligible == 0` short-circuit before any screen computation.
- **n_eligible > 0 with Var(SR) == 0** (single eligible candidate, OR all eligible candidates share identical Sharpe value): the loader returns `sharpe_var = 0.0` (zero variance, well-defined) with finite mean / min / max; Step 3 detects degeneracy via `sharpe_var == 0` check and produces inconclusive disposition per §3.6.

At canonical 198 audit_v1 register: n_eligible = 154; sharpe_var = 0.531 (well above zero); neither degenerate case arises. The dual-handling exists for defensive robustness against hypothetical synthetic / future inputs.

---

## §2 TDD test coverage

### §2.1 Test classes added at `tests/test_evaluate_dsr.py`

| Test class | Coverage |
|---|---|
| `TestLoadAuditV1CandidatesHappyPath` | Synthetic 5-candidate happy path; verifies SimplifiedDSRInputs structure, n_raw/n_eligible, Sharpe distribution arithmetic, CandidateInput field carry-forward |
| `TestLoadAuditV1CandidatesEdgeCases` | §4.4(1) `T_c < 5` exclusion; §4.4(2) `T_c == 0` exclusion with distinct reason; §4.4(3) missing Sharpe exclusion |
| `TestLoadAuditV1CandidatesJsonVsCsvCrossCheck` | §3.4 + §4.4(5) v3.1 register: small delta below 1e-6 (CSV rounding artifact) passes; large delta above 1e-6 documented in `discrepancies_documented` AND candidate stays in eligible set (NOT auto-excluded per v3.1 reframe) |
| `TestLoadAuditV1CandidatesRSGuardDiscipline` | RS-2 attestation failure raises `ValueError`; no silent skip |
| `TestLoadAuditV1CandidatesIntegrationRealData` | Integration test against actual 198 audit_v1 candidates: verifies n_raw=198, n_eligible=154, exclusion reasons in {low_trade_count, zero_trades}, no JSON-vs-CSV discrepancies at v3.1 register, theme distribution matches Step 1 inventory |

### §2.2 Test outcomes

`python -m pytest tests/test_evaluate_dsr.py` → **34 passed in 0.81s** (12 new + 22 pre-existing).

Regression check on related modules (`test_engine.py`, `test_execution_model.py`, `test_compare_2022_vs_2024.py`, `test_compare_multi_regime.py`, `test_dsl.py`, `test_dsl_integration.py`, `test_additional_baselines.py`) → **219 passed in 6.21s**. No regressions.

---

## §3 Canonical-execution result against n=198 audit_v1

### §3.1 Eligibility

| Quantity | Value | Lockpoint reference |
|---|---|---|
| `n_raw` | **198** | §3.2 lockpoint (matches PHASE2C_8.1 audit_v1 canonical population) |
| `n_eligible` (post-§4.4) | **154** | new — eligible subset for Step 3 simplified DSR-style screen |
| Excluded | **44** | §4.4 edge-case filters |

### §3.2 Exclusion reason counts

| §4.4 reason | Count | Notes |
|---|---|---|
| `zero_trades` (§4.4(2)) | **35** | candidates with `T_c == 0`; engine emits `sharpe = 0.0` but no trades occurred |
| `low_trade_count` (§4.4(1)) | **9** | candidates with `0 < T_c < 5` |
| `missing_sharpe` (§4.4(3)) | 0 | no missing/null Sharpe at audit_v1 register (Step 1 verification confirmed) |

Sum: 35 + 9 = 44 = (198 − 154). ✓

### §3.3 Cross-trial Sharpe distribution (eligible n=154)

| Statistic | Value |
|---|---|
| mean | -0.873036 |
| median | -0.973648 |
| min | -2.714683 |
| **max** | **0.960218** |
| variance (ddof=1) | 0.530693 |
| std (ddof=1) | 0.728487 |

**Forward-traceability observation (descriptive only; pre-Step-3):** the max Sharpe within the eligible subset (0.960) sits below Step 1's full-198 max (1.262), indicating the SR=1.262 candidate at Step 1 had T_c < 5 and was excluded by §4.4(1). Per §3.2 lockpoint primary register, N for multiple-testing correction remains N_raw = 198 (NOT N_eligible = 154); the Bonferroni threshold at primary register stays sqrt(2 × ln(198)) ≈ 3.2522. Empirical eligible-subset max 0.960 sits well below the Bonferroni threshold even before formal Step 3 simplified DSR-style screen fires.

**Ratio observation per advisor substantive pass (descriptive register only; not pre-determining Step 3 result):** ratio (eligible_max_Sharpe / Bonferroni_threshold) at this register = 0.960 / 3.252 ≈ **0.30**, lower than Step 1's full-198 ratio 1.262 / 3.252 ≈ 0.39. The §4.4(1) trade-count filter shifted the eligible-subset max away from the threshold, not toward it — the SR=1.262 candidate that drove the Step 1 ratio is the canonical small-N noise-inflation pattern (high Sharpe at T_c < 5 typically reflects sample-size noise, not signal). This is descriptive forward-traceability per §6.2 + §20.5 Instance 1 (b) honest test register; per pre-registration discipline the Step 3 simplified DSR-style screen at conservative AND-gate per §3.6 is the canonical adjudicator, NOT this ratio observation. Per `feedback_reviewer_suggestion_adjudication.md` adjudication: the observation is recorded at register-precision without leaking into pre-Step-3 disposition framing or violating §6.2 forbidden-phrases discipline (no "approaching" / "trending" / "would be" language; the observation is what it is at descriptive register).

### §3.4 §3.4 + §4.4(5) v3.1 cross-validation diagnostic

| Quantity | Value |
|---|---|
| Candidates with `\|delta\| > 1e-6` at any cross-checked column | **0** |
| Tolerance lockpoint (v3.1 reframed register) | 1e-6 |

Confirms v3.1 reframed register lands cleanly: zero discrepancies at the canonical-artifact-register-precision floor calibration. CSV 6-decimal storage rounding artifacts (~5e-7 max physical |delta|) sit below the 1e-6 tolerance per §20 Trigger 5 calibration.

### §3.5 Descriptive distribution within eligible subset

**Theme distribution (eligible n=154):**

| Theme | Count (eligible) | Count (full 198, Step 1) | Excluded |
|---|---|---|---|
| volume_divergence | 39 | 40 | 1 |
| momentum | 37 | 39 | 2 |
| calendar_effect | 31 | 40 | 9 |
| mean_reversion | 26 | 39 | 13 |
| volatility_regime | 21 | 40 | 19 |
| **Total** | **154** | **198** | **44** |

Volatility-regime themes show the highest exclusion rate (19/40 ≈ 47.5%); their entry conditions appear to generate fewer trades than the trade-count threshold. Volume-divergence themes show the lowest exclusion rate (1/40 = 2.5%). This is descriptive only; lockpoint substance unaffected.

**Lifecycle state distribution (eligible n=154):**

| Lifecycle state | Count |
|---|---|
| holdout_failed | 141 |
| holdout_passed | 13 |

All 13 `holdout_passed` candidates have `T_c >= 5` and survive §4.4 filtering. Per §3.3 lockpoint, lifecycle state does NOT enter the primary simplified DSR-style screen at Step 3 (which operates on Sharpe scalars from `holdout_metrics.sharpe_ratio` regardless of holdout-gate disposition). The lifecycle distribution is descriptive only.

### §3.6 Artifact serialization

Step 2 input statistics record artifact written to:

[`data/phase2c_evaluation_gate/audit_v1/_step2_inputs.json`](../../data/phase2c_evaluation_gate/audit_v1/_step2_inputs.json) (~71 KB; schema_version `phase2c_11_step2_v1`)

Artifact contents: full eligible-candidate list with per-candidate fields, full excluded-candidate list with reasons, cross-trial Sharpe scalars, JSON-vs-CSV discrepancy log (empty), theme + lifecycle distributions. Reproducibility property: re-running `load_audit_v1_candidates()` against the same audit_v1 directory + holdout_results.csv produces byte-identical artifact (verified empirically; loader is deterministic).

---

## §4 §20 Trigger 1 boundary status — operational live at Step 2

Per [METHODOLOGY_NOTES §20 v2] codified this arc:

> **Trigger 1 (Pre-result register).** ... Step 1 (artifact inventory + RS guard verification + descriptive distribution diagnostics) is pre-result; Step 2 (compute pre-registered screen *inputs* — cross-trial scalars, eligible-subset N, edge-case filtering) is also pre-result. Step 3 ... and Step 4+ ... are post-result.

Step 2 fires within §20 Trigger 1 pre-result boundary at canonical interpretation: pre-registered screen output (pass/fail/inconclusive disposition) has NOT fired at Step 2. The cross-trial Sharpe distribution descriptors in §3.3 are input-statistics — not the Bonferroni / DSR-style p-value disposition that Step 3 produces.

**Operational implication per §20 Failure-mode signal:** the input statistics in §3.3 are now observed at register-bearing register. Per §20.5 Instance 1 (b) anti-rationalization audit pattern: any subsequent patch attempt against §3 lockpoints (formula / threshold / AND-gate / substantive eligible-subset definition / canonical input source) must satisfy the honest test "would the same patch have been authored without observing Step 2 input statistics?" If the honest answer is no, the patch implicates the post-hoc-tuning defect class even if Trigger 1 surface-passes; Charlie-register adjudication required at boundary cases per §20 Failure-mode signal.

**Self-attestation at Step 2 close:** no patch attempt against §3 lockpoints surfaced at Step 2 author cycle. The empirical input statistics (eligible n=154; max Sharpe 0.960; Sharpe std 0.728; all candidates clean at JSON-vs-CSV v3.1 register) match Step 1 forward-traceability descriptors (max 1.262 → 0.960 attributable to SR=1.262 candidate's T_c<5 exclusion; clean per-candidate distribution). No structural infeasibility surfaced at Step 2 author cycle that would warrant a §20 invocation. Step 3 fires under v3.1 lockpoints unchanged.

**§20 v2 first operational check status — PASSED at register-precision:** advisor cross-check at Step 2 cycle confirmed three positive observations validating §20 v2 codification: (i) v3.1 reframed register Instance 6 1e-6 tolerance lands at 0 JSON-vs-CSV discrepancies across 154 eligible × 5 cross-checked columns — empirical confirmation that §20 Trigger 5 calibration (canonical-artifact register-precision floor) is correctly bounded (not over-loose, not under-tight); (ii) Step 2 input observations did NOT motivate any §3 lockpoint patch attempt at author cycle — Trigger 1 boundary held cleanly through first operational fire of pre-result inputs; (iii) advisor's pre-Step-2 prior probability framing ("artifact-evidence register-class >90%; signal-evidence <5%; inconclusive 5%") matches the descriptive forward-traceability ratio 0.30 at register-precision without leaking into pre-Step-3 disposition framing. Logging here as load-bearing positive evidence at canonical-discipline register; carry-forward to §20.5 Instance 1 register at successor methodology consolidation cycle for §20 tier-stability adjudication (Strong tier preserved; no demotion or supersession warranted at first-operational-check register).

---

## §5 Step 2 closure verdict

### §5.1 Closure status against §7.2 Step 2 gating criteria (post-Codex-patches)

| §7.2 criterion | Status |
|---|---|
| input statistics record clean | **CLEAN** (§3) |
| cross-validation per §3.4 + §4.4(5) clean | **CLEAN** (§3.4 — 0 `delta_above_tolerance` discrepancies at v3.1 1e-6 register; 0 missing-row / missing-value entries either) |
| eligible subset N documented | **CLEAN** (n_eligible=154 per §3.1) |
| excluded candidate list complete | **CLEAN** (44 entries with pre-registered §4.4 reasons per §3.2; reason-class precision improved per Codex HIGH #3) |
| RS-2 guard calls operational | **CLEAN** (§1.2 — every audit_v1 artifact gated by `check_evaluation_semantics_or_raise()`; 198/198 pass; 0 failures) |
| n_raw lockpoint enforcement (Codex CRITICAL #1) | **CLEAN** (`expected_n_raw=EXPECTED_N_RAW=198` enforced at production cycle; ValueError on mismatch verified by test) |
| reviewer authorization at sealed register | **PENDING re-review** (final Claude advisor substantive pass + ChatGPT structural pass on post-patch v3 deliverable; Codex re-review optional per advisor `改完再commit` discipline if patches surfaced material substance change) |

**Net: Step 2 input prep CLEAN at all six register-substance pillars post-patches; n_raw enforcement closes Codex CRITICAL #1; reason-class precision + NaN/inf rejection + CSV-missing audit close HIGH #2/#3/#4; defensive helpers + expanded coverage close MEDIUM #5/#6/#7; deliverable wording precision closes LOW #8.**

### §5.1.1 Codex review audit trail (Instance 6 of project arc; first substantive Codex code review under §8.2 P6)

| Codex finding | Severity | Adjudication | Patch summary |
|---|---|---|---|
| #1 `EXPECTED_N_RAW` not enforced | CRITICAL | APPROVE | `expected_n_raw` keyword arg added; production cycles pass `EXPECTED_N_RAW`; test verifies ValueError on mismatch; default None for synthetic test fixtures |
| #2 `_safe_float` accepts NaN/inf | HIGH | APPROVE | `math.isfinite()` check added; rejects NaN / +inf / -inf at JSON + CSV parse register; `TestSafeFloatHelpers` parametrized over invalid + valid inputs |
| #3 §4.4 ordering at code level | HIGH | APPROVE | `missing_trades` reason class added (companion to §4.4(3) for audit-trail precision when total_trades is missing); docstring resolution policy explicit ("safe scalar validation precedes semantic classification"); §4.4 spec outcome (eligible vs excluded) preserved at all overlap cases. **Forward semantic note (per advisor L2):** `missing_trades` reason class is canonically empty at the PHASE2C_11 batch (0/198 hits at audit_v1); class exists for future-batch defensive coverage. Successor cycles consuming `_step2_inputs.json` schema v2 should expect `missing_trades ≠ missing_sharpe` distinction at `exclusion_reason_counts` and treat them as distinct §4.4 audit categories (both excluded, but with different audit-trail provenance). |
| #4 CSV-missing silent skip | HIGH | APPROVE | Discrepancies now typed via `kind` field: `delta_above_tolerance` / `missing_csv_row` / `missing_csv_value` / `missing_json_value` / `missing_both`; nothing silently skipped; `TestLoadAuditV1CandidatesCsvMissingDiscrepancies` exercises each |
| #5 `int(trades_raw)` parsing | MEDIUM | APPROVE | `_safe_int_count()` defensive helper added; rejects non-finite / non-integral / negative; `TestSafeFloatHelpers` parametrized coverage |
| #6 Edge-case overlap tests | MEDIUM | APPROVE | New tests: NaN sharpe, +inf sharpe, missing-trades-with-valid-sharpe, T_c==0 with missing sharpe overlap, non-integral trades, negative trades |
| #7 Cross-validation column coverage | MEDIUM | APPROVE | Parametrized test across all 5 `_CSV_TO_JSON` columns; boundary tests at `delta < 1e-6` (passes) and `delta > 1e-6` (documented) |
| #8 Var(SR)=0 deliverable wording | LOW | APPROVE | §1.5 wording clarified: distinct sub-cases for `n_eligible == 0` (NaN scalars) vs `n_eligible > 0 with Var(SR) == 0` (zero variance for Step 3 inconclusive marking) |

**Test verdict post-patches:** 77/77 evaluate_dsr GREEN (was 34; +43 new tests covering all Codex findings); 262/262 GREEN across related modules (`test_engine.py`, `test_execution_model.py`, `test_compare_2022_vs_2024.py`, `test_compare_multi_regime.py`, `test_dsl.py`, `test_dsl_integration.py`, `test_additional_baselines.py`); zero regressions.

**Re-execution at canonical 198 audit_v1 (post-patch reproducibility verification):**

| Quantity | Pre-Codex-patch (v1 artifact) | Post-Codex-patch (v2 artifact) | Status |
|---|---|---|---|
| `n_raw` | 198 | 198 (now lockpoint-enforced) | CLEAN |
| `n_eligible` | 154 | 154 | CLEAN — substance unchanged |
| Exclusion reasons | {zero_trades: 35, low_trade_count: 9} | {zero_trades: 35, low_trade_count: 9} | CLEAN — no `missing_trades` at canonical (every audit_v1 candidate has valid trades scalar) |
| Sharpe mean | -0.873036 | -0.873036 | CLEAN — bit-identical |
| Sharpe max | 0.960218 | 0.960218 | CLEAN — bit-identical |
| Sharpe std | 0.728487 | 0.728487 | CLEAN — bit-identical |
| Discrepancies | 0 (no `kind` field) | 0 (typed `kind` field added; no entries) | CLEAN — schema enriched, substance unchanged |
| Artifact `schema_version` | `phase2c_11_step2_v1` | `phase2c_11_step2_v2` | bumped per discrepancy `kind` field addition + `missing_trades` reason class availability |

**Schema-bump audit-trail note (per advisor L3):** the v1 artifact existed in working tree only — never sealed at git history; v2 supersedes cleanly without git-history conflict at this register. Future post-seal schema bumps (after a v2 artifact lands at sealed commit) would require a new artifact file (e.g., `_step2_inputs_v3.json`) rather than overwrite, to preserve audit-trail reconstructability per §20 Trigger 4 / §16 anchor-prose-access discipline analogy.

Per Codex CRITICAL #1: production cycle now passes `expected_n_raw=EXPECTED_N_RAW` to enforce §3.2 lockpoint; mismatch raises `ValueError`; integration test verifies enforcement at canonical n=198 register.

### §5.1.2 §20 NON-INVOCATION confirmed at Codex review cycle

Codex review surfaced 8 substantive findings at register-precision; all 8 adjudicated APPROVE; patches operate strictly at code-defensiveness register without touching any §3 lockpoint substance (formula / threshold / pass-fail criterion / canonical input source / substantive eligible-subset definition all unchanged). **No §20 trigger verification was required at the Codex review cycle: Codex findings are code-quality / audit-trail / defensive-helpers register, NOT lockpoint mis-specification register. The §20 5-trigger admissibility test was not invoked because no candidate §3 lockpoint patch surfaced.**

Framing precision per advisor substantive re-pass register-correction: this is **§20 NON-INVOCATION**, NOT a "§20 second operational check passed" outcome. §20's operational checks count only when a candidate §3 lockpoint mutation is surfaced and the 5 triggers are evaluated; defensive code-quality patches that preserve all §3 lockpoints by construction do not exercise the §20 admissibility machinery and so do not constitute §20 binding evidence in either direction. The §20 second operational check **defers** to the next candidate invocation surface (none surfaced at Step 2 author cycle or at the Codex review cycle). This framing precision preserves the "narrow five-trigger exception path for pre-result structural infeasibility ONLY" discipline codified in §20 v2 + the `33731ce` commit message + ChatGPT seal-note ("§20 is NOT a general escape hatch"); inflating §20 binding count to include code-defensiveness patches would dilute §20 narrow scope at canonical-discipline register and mirrors the METHODOLOGY_NOTES §5 failure mode of claiming a structural principle "held" without precondition firing.

What IS positive evidence at this Codex review cycle: v3.1 sub-spec lockpoints (Bonferroni threshold sqrt(2 × ln 198) ≈ 3.2522, conservative AND-gate at §3.6, JSON canonical scalar source per §3.3, T_c<5 substantive eligible filter, Gumbel approximation, all preserved); patches operated strictly at code-defensiveness register; bit-identical Sharpe stats post-patch verify lockpoint preservation empirically.

### §5.2 Reviewer routing per §8.1 + §8.2 (post-Codex-patch re-review)

Initial reviewer cycle (pre-patch) summarized at §5.1.1 Codex review audit trail. Post-patch re-review focus areas:

| Reviewer | Routing | Focus |
|---|---|---|
| ChatGPT | structural | (a) Codex-finding-#3 reason-class precision: confirm `missing_trades` distinct from `missing_sharpe` at audit register without changing §4.4 spec outcome; (b) Codex-finding-#4 typed `kind` discrepancy entries do not alter v3.1 §3.4 descriptive register interpretation; (c) Codex-finding-#1 `expected_n_raw` parameter design (production register vs synthetic-test opt-out) on-discipline; (d) Step 2 deliverable v3 cross-references + §5.1.1 audit table accurate |
| Claude advisor | substantive | (a) §1.5 Var(SR)=0 dual-handling clarification matches code behavior; (b) §5.1.2 §20 boundary discipline correct ("Codex code-quality patches preserve lockpoint substance; no §20 invocation required" claim verified at register-precision); (c) all 8 patches preserve §3 lockpoint substance (no formula / threshold / AND-gate / canonical-source change); (d) artifact reproducibility table at §5.1.1 correctly reports bit-identical Sharpe stats post-patch |
| Codex | re-review optional | per advisor `改完再commit` discipline: Codex re-review fires if patches surfaced material substance change. **Patches preserve §3 lockpoint substance entirely (sharpe stats bit-identical); patches operate strictly at code-defensiveness register; advisor + ChatGPT post-patch convergence sufficient under `feedback_codex_review_scope.md` "substantive code/work" threshold.** Codex re-review fires at Step 3 minimum per §8.2 (canonical formula correctness for `compute_simplified_dsr()`). |

Per `feedback_codex_review_scope.md` user-memory: Codex fires on substantive code work; the post-patch substance (sharpe stats unchanged at register-precision; only audit-trail enrichment + defensive helpers added) is below Codex re-fire threshold but advisor + ChatGPT re-pass remains required.

### §5.3 Step 3 fire gate

Per [PHASE2C_11_PLAN §7.3]: subsequent operational fires AUTHORIZED POST-SEAL ONLY. Step 3 (compute simplified DSR-style screen calculation per §4.3 + §4.5 `compute_simplified_dsr()` API) fires post-seal of this Step 2 deliverable + sub-spec alignment + Charlie-register authorization. Codex review at Step 3 also fires per §8.2 minimum (canonical formula correctness).

**Forward-flag for Step 3 author per advisor cross-trigger sanity check:** the `expected_n_raw=None` default at `load_audit_v1_candidates()` is a production-vs-synthetic-test split mechanism. Step 3 entry MUST verify `inputs.n_raw == EXPECTED_N_RAW` as the §3.2 lockpoint second-line check at `compute_simplified_dsr()` entry, not relying on Step 2 caller having passed `expected_n_raw=198`. This dual-gate (Step 2 loader-level + Step 3 consumer-level) preserves §3.2 lockpoint integrity if a future caller forgets the production kwarg. Codify at Step 3 spec / deliverable register.

---

## §6 Cross-references

- [PHASE2C_11_PLAN.md](PHASE2C_11_PLAN.md) v3.1 — sub-spec at §4.2 (inputs) + §4.4 (edge cases) + §4.5 (module scope) + §7.1 Step 2 + §7.2 closure criteria + §8.1 + §8.2 reviewer routing
- [PHASE2C_11_STEP1_DELIVERABLE.md](PHASE2C_11_STEP1_DELIVERABLE.md) v2 — Step 1 inventory + §20 Instance 1 audit trail
- [`docs/discipline/METHODOLOGY_NOTES.md`](../discipline/METHODOLOGY_NOTES.md) §20 v2 — pre-result lockpoint mis-specification documented exception path; Trigger 1 boundary operative at Step 2 register
- [`backtest/evaluate_dsr.py`](../../backtest/evaluate_dsr.py) — `load_audit_v1_candidates()` + dataclasses + lockpoint constants; lines added per §1.1
- [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) lines 263-394 — `check_evaluation_semantics_or_raise()` (RS-2 guard)
- [`tests/test_evaluate_dsr.py`](../../tests/test_evaluate_dsr.py) — 5 new test classes per §2.1
- [`data/phase2c_evaluation_gate/audit_v1/_step2_inputs.json`](../../data/phase2c_evaluation_gate/audit_v1/_step2_inputs.json) — Step 2 input statistics record artifact

---

**End of working draft.** Reviewer routing per §5.2 + Charlie-register adjudication per §5.3 next operational step.
