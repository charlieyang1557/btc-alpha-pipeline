# D7 Stage 2c Scope Lock Document

**Branch:** `claude/setup-structure-validators-JNqoI`
**Tip at scope lock:** `0c86993`
**Phase:** Phase 2B D7 Stage 2c (N=20 live D7b batch probe)
**Cumulative Phase 2B spend to date:** ~$2.62 ($30 cap, 8.7% utilized)

---

## 0. Purpose of this document

This document locks the 10 scope decisions for D7 Stage 2c against the **real selection data** produced by commit `594957c` and locked as a committed artifact at `b71ffd1`. Unlike an abstract scope proposal, every decision here is anchored to concrete numbers from `docs/d7_stage2c/replay_candidates.json`.

This document is the input to adversarial review (ChatGPT + Gemini). After review and any amendments, it becomes the input to the Stage 2c launch prompt draft, which in turn drives Claude Code's fire-script extension patch.

**What this document locks:** the 10 scope decisions + 1 addendum (test-retest handling).

**What this document does NOT lock:** fire script implementation details, expectations file content (Charlie-authored), or sign-off verdict criteria beyond what's stated in Lock 10.

---

## 1. Pre-fire state (committed artifacts)

The following commits establish the pre-fire anchor for Stage 2c. All are on `origin/claude/setup-structure-validators-JNqoI`:

| Commit | Content | Timestamp |
|---|---|---|
| `b71ffd1` | Locked Stage 2c selection JSON at `docs/d7_stage2c/replay_candidates.json` | 2026-04-18T15:01:20Z (selection_timestamp_utc) |
| `9c59510` | Stage 2c selection test fixtures (8) + test file (42 new tests) | — |
| `594957c` | Stage 2c selector extension code (`STAGE2C_*` constants + 869 lines) | — |
| `bf8a6f4` | Stage 2c selection acceptance notebook (PASS verdict) | — |
| `0c86993` | .gitignore update (Rhistory) | — |

**Known state of selection JSON:**
- `stage_label: d7_stage2c`, `record_version: 1.0`
- `selection_tier: 0`, `selection_warnings: []`
- 20 candidates at positions `[17, 22, 27, 32, 62, 72, 73, 74, 77, 83, 97, 102, 107, 112, 117, 138, 143, 147, 152, 162]`
- `theme_counts_in_selected: {mean_reversion: 15, volatility_regime: 4, volume_divergence: 1}`
- `label_counts_in_selected: {agreement_expected: 8, divergence_expected: 3, neutral: 9}`
- `stage2b_overlap_count: 5`, positions `[17, 73, 74, 97, 138]`
- `pool_size_total: 200`, `pool_size_passing_per_candidate_criteria: 29`

**Acceptance:** verdict PASS per the committed acceptance notebook. 8/8 acceptance gates satisfied. 42 Stage 2c selection tests green; 1146 full-suite tests green.

---

## 2. The 10 locks

### Lock 1 — N=20, same batch, from locked selection

Stage 2c fires 20 sequential D7b calls, one per candidate in `docs/d7_stage2c/replay_candidates.json`, in the firing order encoded there (position ascending). The batch reference is `5cf76668-47d1-48d7-bd90-db06d31982ed` — identical to Stage 2a and Stage 2b, no re-batching.

**Rationale:** Stage 2c exists to characterize D7b behavior at probe-size N=20, leveraging the signed-off Stage 2d batch. Generating a new batch would introduce confounding variables (different proposer seed, different factor distributions) that would preclude clean replication of the Stage 2b N=5 finding.

**Anchor:** selection JSON at `b71ffd1`; candidates read at fire-script startup once, identity verified by SHA-256.

**Runtime integrity requirement:** the Stage 2c fire script MUST record `selection_json_sha256` at startup and refuse to run if the hash of the on-disk `docs/d7_stage2c/replay_candidates.json` differs from the hash recorded in this scope-lock document at the time the scope was frozen. If the selection file is regenerated (e.g., re-running `select_replay_candidate.py --n=20`), this scope lock is invalidated and must be re-adjudicated. The SHA-256 of the committed selection artifact is the binding anchor, not the semantic selection outcome.

---

### Lock 2 — Constraints as implemented, not as originally framed

Hard constraints (inherited unchanged from N=5, scaled where needed):
- All 20 candidates pass the 7 per-candidate criteria
- `factor_count_range = STAGE2B_N_FACTORS_RANGE = (3, 7)` — reused verbatim, no Stage 2c-specific range
- ≥3 distinct themes (empirically bounded; pool has exactly 3)
- ≥5 per position bucket (early/mid/late)
- ≥4 `agreement_expected` candidates (promoted to hard after review)
- Unique `hypothesis_hash` across the 20

Soft constraints (tier ladder, fixed-order relaxation):
- **Tier 0** (achieved): ≥2 `divergence_expected` AND at least 2 selected `divergence_expected` candidates come from distinct themes
- **Tier 1 Sub-case A:** ≥2 `divergence_expected`, all from a single theme
- **Tier 1 Sub-case B:** exactly 1 `divergence_expected`
- **Tier 2:** 0 `divergence_expected`, agreement floor still enforced

**Observed outcome:** Tier 0 achieved cleanly. 3 divergence candidates spanning 3 themes (mean_reversion, volatility_regime, volume_divergence). Agreement count = 8 (floor = 4). No warnings.

**Rationale:** Empirical pool composition supports Tier 0 with non-trivial margin on agreement (8 vs 4 floor) but tight margin on divergence (3 vs 2 minimum). The cross-theme span was possible only because the three rare non-mean_reversion divergence candidates (73, 74) happened to satisfy the structural distance threshold (`max_overlap <= 2`).

**Stage 2b overlap handling (clarifying statement):** Stage 2b overlap is **permitted but not explicitly optimized for**. The 5-position overlap `[17, 73, 74, 97, 138]` arises from the locked Stage 2c selection algorithm operating on the full eligible pool under unchanged per-candidate criteria and unchanged label rubric. It is not the result of a selection step that deliberately includes or excludes Stage 2b positions. The overlap provides test-retest evidence (see Lock 10a) but is not the selection objective.

---

### Lock 3 — Firing order = position ascending, locked pre-live

Firing order matches the `firing_order` field in the selection JSON, which is `[1..20]` corresponding to position-ascending list order `[17, 22, 27, 32, 62, 72, 73, 74, 77, 83, 97, 102, 107, 112, 117, 138, 143, 147, 152, 162]`.

**Rationale:** position-ascending order preserves Stage 2b's discipline, exposes monotonic context-size scaling (earlier candidates have fewer priors, later candidates more), and eliminates any runtime optimization that could be mistaken for hindsight selection.

**No runtime reordering permitted** under any circumstance, per Stage 2b lock pattern.

---

### Lock 4 — 5-second inter-call spacing

Sleep 5 seconds between calls (no sleep after call 20). Total idle time: 19 × 5 = 95 seconds.

**Rationale:** matches Stage 2b. Well below Anthropic tier-1 rate limit bands. Adds observability gap between consecutive calls without meaningfully extending wall-clock. Stage 2b's 73-second wall-clock extrapolates to ~5 minutes for Stage 2c (20 calls × ~10s each + 95s idle).

**Does NOT test rate limiting.** Rate limit characterization is deferred to Stage 2d (N=200) and is not a Stage 2c deliverable.

---

### Lock 5 — Cost caps: $0.50 total, $0.05 per-call

- `STAGE2C_TOTAL_COST_CAP_USD = 0.50`
- `STAGE2C_PER_CALL_COST_CEILING_USD = 0.05` (unchanged from Stage 2b)

**Rationale and empirical backing:**

Stage 2b fired 5 calls at $0.076725 total ($0.015345 per call average, max $0.018765 at position 138). Extrapolating to 20 calls with position-linear cost scaling through position 162:

| Estimate method | Projected Stage 2c cost |
|---|---|
| Simple linear: 20 × 0.0187 | $0.374 |
| Position-weighted (avg position higher at Stage 2c) | $0.45 |
| Worst case all at per-call ceiling | $1.00 (exceeds cap, would abort) |

The $0.50 cap preserves a ~1.1× safety margin over the position-weighted estimate. If actual spend exceeds $0.50, the probe aborts on rule (e) with partial-completion artifact preserved.

Per-call ceiling stays at $0.05 (unchanged) because Stage 2b's highest call was $0.018765 — 38% of ceiling. No evidence supports tightening.

---

### Lock 6 — Abort rules (5-rule taxonomy, same structure as Stage 2b)

Fire sequence aborts on first match:

1. **(a) Consecutive API-level errors:** 2 consecutive calls with `critic_status == "d7b_error"` AND `d7b_error_category == "api_level"` AND `actual_cost_usd == 0`
2. **(b) Cumulative d7b_error rate > 40% at K ≥ 3:** (error_count / completed_calls) > 0.40 after at least 3 calls
3. **(c) Content-level errors ≥ 4 after K ≥ 8:** `content_level_error_count >= 4` once at least 8 calls have completed. Threshold scaled from Stage 2b's absolute `>= 3 of K >= 3` (which was 60% at N=5); at N=20 the same absolute threshold would be 15%, which is not "systemic." The revised threshold targets ~20% error rate and requires meaningful sample size (K ≥ 8) before firing. Early clustering (e.g., 4 errors in first 8 calls) still triggers abort.
4. **(d) Per-call cost exceeded:** any single call `actual_cost_usd > $0.05`
5. **(e) Cumulative cost exceeded:** cumulative `actual_cost_usd > $0.50`

Classification source of truth is the **persisted per-call record**, not ad-hoc batch-loop re-classification. Same discipline as Stage 2b's HG pattern.

Abort is controlled termination; partial aggregate record is still written with `sequence_aborted: true`, `abort_reason: "<enum>"`, `abort_at_call_index: <K>`, `completed_call_count: <K>`.

---

### Lock 7 — Per-candidate expectations file with 20 subsections

Charlie authors `docs/d7_stage2c/stage2c_expectations.md` before fire. File must contain:

- `## Anti-Hindsight Anchor` header
- `## Aggregate Expectations Across All 20 Calls` header
- `## Per-Candidate Expectations` header
- **20 candidate subsection headers**, each EXACTLY matching the selection JSON:
    - `### Candidate 1 — Position 17, mean_reversion, divergence_expected`
    - `### Candidate 2 — Position 22, mean_reversion, neutral`
    - `### Candidate 3 — Position 27, mean_reversion, agreement_expected`
    - `### Candidate 4 — Position 32, mean_reversion, neutral`
    - `### Candidate 5 — Position 62, mean_reversion, neutral`
    - `### Candidate 6 — Position 72, mean_reversion, neutral`
    - `### Candidate 7 — Position 73, volatility_regime, divergence_expected`
    - `### Candidate 8 — Position 74, volume_divergence, divergence_expected`
    - `### Candidate 9 — Position 77, mean_reversion, neutral`
    - `### Candidate 10 — Position 83, volatility_regime, neutral`
    - `### Candidate 11 — Position 97, mean_reversion, agreement_expected`
    - `### Candidate 12 — Position 102, mean_reversion, agreement_expected`
    - `### Candidate 13 — Position 107, mean_reversion, agreement_expected`
    - `### Candidate 14 — Position 112, mean_reversion, agreement_expected`
    - `### Candidate 15 — Position 117, mean_reversion, neutral`
    - `### Candidate 16 — Position 138, volatility_regime, neutral`
    - `### Candidate 17 — Position 143, volatility_regime, neutral`
    - `### Candidate 18 — Position 147, mean_reversion, agreement_expected`
    - `### Candidate 19 — Position 152, mean_reversion, agreement_expected`
    - `### Candidate 20 — Position 162, mean_reversion, agreement_expected`

Fire script validates these 20 headers by exact string match against the selection JSON (analog to Stage 2b's HG4b gate).

**Commit ordering gate:** expectations commit timestamp must be strictly greater than selection commit (`b71ffd1` at 2026-04-18T15:01:20Z) AND strictly less than fire wall-clock timestamp. `git commit --amend` after initial expectations commit is forbidden.

---

### Lock 8 — Mechanical labels + reconciliation rubric unchanged

Labels inherited verbatim from Stage 2b:
- `agreement_expected := factor_set_prior_occurrences > 0`
- `divergence_expected := factor_set_prior_occurrences == 0 AND max_overlap <= 2`
- `neutral := otherwise`

Reconciliation rubric unchanged at per-candidate level:
- Pre-registered `divergence_expected` ⟹ `structural_variant_risk < 0.5` is "consistent"
- Pre-registered `agreement_expected` ⟹ `structural_variant_risk >= 0.5` is "consistent"
- Pre-registered `neutral` ⟹ no per-candidate directional prediction; per-candidate reconciliation is N/A

**Aggregate-level prediction for neutral group (required):** Stage 2c has 9 neutral-labeled candidates (vs Stage 2b's 1). The expectations file MUST include a falsifiable **aggregate-level prediction** for this group, committed before fire. Example acceptable prediction forms:

> "For the 9 neutral-labeled candidates collectively, I predict `structural_variant_risk` group mean < 0.5 AND group variance > the agreement-expected group variance."

> "I predict neutral candidates will bifurcate: candidates with `max_overlap <= 4` score LOW, candidates with `max_overlap >= 5` score HIGH. Cutoff expected around overlap=4.5."

> "I predict no significant aggregate pattern in the neutral group — their scores will span the full [0, 1] range without clear central tendency."

The prediction must be:
- Aggregate-level (about the group, not per-candidate)
- Falsifiable (specific enough that Stage 2c results can confirm or contradict)
- Committed before fire (via the expectations file)

Without this, observing "neutral candidates scored LOW" post-fire would be post-hoc storytelling. Pre-registration of the group-level prediction transforms the N=9 neutral group into the primary novel-replication evidence for Stage 2b's finding (see empirical framing section 3.2).

**Critical rationale (do not relax):** Stage 2c's primary purpose is to test whether the Stage 2b N=5 finding (3/3 divergence candidates contradicted by Sonnet's HIGH structural_variant_risk scoring) replicates at N=20. Any change to the label rubric or reconciliation threshold would confound the replication test. This is a **replication-first stage**, not a repair stage.

---

### Lock 9 — Aggregate record schema inherited from Stage 2b

Produce `docs/d7_stage2c/stage2c_batch_record.json` with the same schema as Stage 2b's `stage2b_batch_record.json`, with the following substitutions:

- `stage_label: "d7_stage2c"` (not `d7_stage2b`)
- `record_version: "1.0"`
- Path field values reference `docs/d7_stage2c/` paths
- Per-call record count = 20 (not 5)
- Sequence fields (e.g. `reasoning_lengths_in_call_order`) have 20 entries
- `selection_json_sha256`, `expectations_file_sha256`, `d7b_prompt_template_sha256` captured at startup as before
- Per-call records preserve the 4 Stage 2b extension fields (`prior_factor_sets_count`, `theme_hint_factor_count`, `prompt_chars`, `prompt_sha256`)

**Immutability via `write_completed_at`** — set last, atomic write via `os.replace()`, no overwrite of existing file. Same discipline as Stage 2b.

No schema novelty. All plumbing inherits.

---

### Lock 10 — Green-light criteria for Stage 2d

Stage 2c passes and unblocks Stage 2d iff all four conditions hold:

**(a) Cost:** `total_actual_cost_usd <= total_estimated_cost_usd`. Hard-fail if actual > estimated (positive budget surprise). Under-consumption (actual/estimated < 0.2) is a calibration signal worth noting but NOT a hard fail.

**(b) Reasoning length:** all 20 completed calls have `reasoning_length in [100, 1500]`. At most 1 cap-hit at 1500 is acceptable (preserves Stage 2b tolerance); 2+ cap hits blocks Stage 2d as evidence of a recurring parser contract issue.

**(c) Replication pattern OR explicit ambiguity source:** the Stage 2c sign-off must either:
- Describe an observed pattern in D7a/D7b reconciliation across labeled candidates (with separate sub-patterns for agreement_expected, divergence_expected, neutral), OR
- Explicitly state "N=20 insufficient to establish pattern" AND identify the dominant source of ambiguity. The ambiguity source must be one of:
    1. Test-retest variance (overlap candidates show Stage 2b ↔ Stage 2c disagreement, indicating Sonnet judgment noise dominates signal)
    2. Theme imbalance (75% mean_reversion in the probe precludes cross-theme generalization)
    3. Overlap confounding (divergence-axis evidence is test-retest-only; no novel divergence replication possible at this pool)
    4. Label sparsity (insufficient candidates in a given label group to establish central tendency)

Post-hoc storytelling without one of these two framings is NOT acceptable. An "unclear" verdict that does not name a specific dominant ambiguity source fails criterion (c). Same discipline as Stage 2b criterion (c), tightened for the higher epistemic bar at N=20.

**(d) No recurring error class:** at most 2 `d7b_error` events of any kind across 20 calls. 3+ indicates a systemic issue (parser, prompt framing, API reliability) requiring investigation before Stage 2d's N=200 scale.

---

### Lock 10a — Test-retest reconciliation for Stage 2b overlap

5 of the 20 Stage 2c candidates are Stage 2b carryovers: positions 17, 73, 74, 97, 138. Stage 2c sign-off must include a **test-retest table** comparing Stage 2b and Stage 2c scores for these 5 candidates:

| Position | Label | Stage 2b plaus / align / svr | Stage 2c plaus / align / svr | Per-axis agreement (±0.1) | Full-vector agreement |
|---|---|---|---|---|---|
| 17 | divergence_expected | 0.75 / 0.85 / 0.85 | (TBD) | (TBD) | (TBD) |
| 73 | divergence_expected | 0.75 / 0.85 / 0.85 | (TBD) | (TBD) | (TBD) |
| 74 | divergence_expected | 0.75 / 0.85 / 0.65 | (TBD) | (TBD) | (TBD) |
| 97 | agreement_expected | 0.75 / 0.90 / 0.95 | (TBD) | (TBD) | (TBD) |
| 138 | neutral | 0.75 / 0.90 / 0.15 | (TBD) | (TBD) | (TBD) |

**Summary statistics (both required):**

1. **Per-axis agreement-rate:** fraction of axes (out of 3 × 5 = 15) that produce Stage 2b vs Stage 2c scores within ±0.1. Captures axis-level stability.

2. **Full-vector agreement count:** number of candidates (out of 5) for which ALL 3 axes agree within ±0.1 simultaneously. Captures candidate-level stability. A candidate with plaus agree, align agree, svr disagree counts as 0 here but contributes 2/3 to per-axis rate. Both views matter.

**This is supplementary evidence, NOT a hard-fail criterion.** Test-retest high agreement strengthens Stage 2c conclusions; low agreement indicates Sonnet temperature-1.0 variance at the stability-of-judgment level and should be recorded as a Stage 2c finding worth carrying forward to Stage 2d design.

**Inference scope (boundary clarification):** test-retest agreement on the 5 overlap candidates bounds inference to those specific candidates. Agreement on overlap candidates does NOT imply low noise on the 15 non-overlap candidates. Stage 2c's sign-off must not generalize test-retest agreement from the overlap set to the full probe. If the Stage 2d design needs a broader noise estimate, that is a Stage 2d scope question, not a Stage 2c inference.

**Framing discipline:** The 3 divergence candidates in Stage 2c ARE all Stage 2b overlap (17, 73, 74). Stage 2c does NOT independently test whether new divergence candidates replicate the Stage 2b finding — because the eligible pool has no new divergence candidates. The sign-off must acknowledge this: the "divergence axis" result at Stage 2c is test-retest only.

---

## 3. Empirical framing addendum (sign-off must address)

Three observations from the locked selection that affect how Stage 2c results must be interpreted:

### 3.1 Theme distribution is 75% mean_reversion

`theme_counts: {mean_reversion: 15, volatility_regime: 4, volume_divergence: 1}`

This reflects D6 proposer's empirical distribution at the non-momentum / pending_backtest / factor-count-in-range / cross-operator / no-thin-theme-bleed intersection. It is NOT a selection defect.

**Consequence for sign-off:** D7b behavior characterized at Stage 2c is dominated by mean_reversion strategy observations. Non-mean_reversion themes (volatility_regime: N=4, volume_divergence: N=1) provide small-N observations. Findings framed as "D7b behaves thus-and-so" must be qualified as "primarily on mean_reversion; tentatively on volatility_regime; single-observation on volume_divergence."

### 3.2 The 9 neutral candidates are the primary novel-replication axis

Label distribution: agreement (8), divergence (3), neutral (9).

The 3 divergence candidates (17, 73, 74) are all Stage 2b overlap — their Stage 2c scores are test-retest, not independent replication.

The 8 agreement candidates (27, 97, 102, 107, 112, 147, 152, 162) include 1 Stage 2b overlap (97); 7 are new. Stage 2c agreement evidence is N=7 fresh + N=1 test-retest.

**The 9 neutral candidates are the richest source of novel Stage 2b finding replication evidence.** Stage 2b had 1 neutral case (position 138) with `structural_variant_risk = 0.15` (LOW). If Stage 2c's 9 neutral candidates consistently score LOW, this supports the hypothesis that `neutral` is the label that predicts Sonnet's "this looks structurally novel" judgment more reliably than `divergence_expected`.

**Sign-off framing:** do not treat divergence as "the" replication axis. Report findings by label separately. The neutral axis at N=9 is the strongest evidence base for either confirming or refuting Stage 2b's insight that D7a/D7b measure orthogonal things.

### 3.3 Bucket distribution is lopsided

Position bucket counts in the selection: `early: 5, mid: 10, late: 5`.

The mid bucket is overweight. Early and late buckets are at the hard floor. Position span 17 → 162 exceeds Stage 2b's 17 → 138.

**Consequence for cost and telemetry:** input tokens will scale with position. Position 162 will generate ~5500 input tokens (extrapolated from Stage 2b's 4475 at position 138). Late-bucket calls contribute disproportionately to total cost. Expected per-call cost distribution will show a heavy right tail.

---

## 4. Out-of-scope for this scope lock

Explicitly deferred to the Stage 2c launch prompt (subsequent document):

- Exact hard-fail gate list for the fire script (Stage 2b had 23; Stage 2c will likely have 23-25 with N=20 adaptations)
- Fire script argument names, stdout format, per-call logging detail
- Stub mode behavior specifics
- Expectations file structural validator details beyond Lock 7
- Raw payload archival rules (Stage 2a `call_0073` already archived during Stage 2b fire; Stage 2b `call_0017`, `call_0073`, `call_0074`, `call_0097`, `call_0138` need archival for Stage 2c — handled in launch prompt)
- Test coverage requirements for the fire script extension patch

Explicitly deferred to the Stage 2c sign-off document (post-fire):

- Interpretation of the test-retest results
- Per-label pattern description or "insufficient signal" determination
- Stage 2d design implications based on observed patterns

---

## 5. Review history

This document went through adversarial review by ChatGPT and Gemini. Eight amendments integrated in v2. Reviewer-flagged issues resolved as follows:

| Amendment | Source | Resolution |
|---|---|---|
| 1. Lock 6(c) scaling | ChatGPT + Gemini (independent) | `content-level >= 3 at K >= 3` → `content-level >= 4 after K >= 8` |
| 2. Lock 10(c) ambiguity source required | ChatGPT + Gemini | "unclear at N=20" must identify one of 4 named ambiguity sources |
| 3. Lock 8 neutral-group prediction required | Gemini | Falsifiable aggregate-level prediction for neutral group in expectations file |
| 4. Lock 10a full-vector agreement | ChatGPT + Gemini | Added as secondary summary statistic |
| 5. Lock 2 overlap language | ChatGPT + Gemini | "Permitted but not explicitly optimized for" clarifying statement |
| 6. Lock 1 SHA-256 runtime verification | ChatGPT + Gemini | Runtime integrity requirement made explicit |
| 7. Lock 2 divergence theme-span phrasing | ChatGPT | "at least 2 selected divergence candidates come from distinct themes" |
| 8. Lock 10a inference scope | Advisor self-review | Test-retest agreement bounded to overlap candidates only |

Locks 1, 3, 4, 8 remain replication-discipline locks inherited from Stage 2b and cannot be revisited without aborting the replication claim. Reviewers did not push back on these.

**Not changed:** Lock 8's per-candidate reconciliation rubric for divergence_expected and agreement_expected (threshold 0.5, direction unchanged). This is the core replication mechanism.

---

## 6. Next steps

1. ✅ Scope lock v2 integrated — this document
2. Draft Stage 2c launch prompt (target 600-800 lines; inherits heavily from Stage 2b's 888-line doc)
3. Adversarial review of launch prompt (ChatGPT + Gemini)
4. Launch prompt amendments applied
5. Send to Claude Code for fire-script extension patch
6. Charlie authors `docs/d7_stage2c/stage2c_expectations.md` with 20 per-candidate subsections AND the required aggregate-level neutral-group prediction (Lock 8)
7. Commit expectations file — anchor timestamp recorded
8. Fire live via `--confirm-live` flag
9. Paste artifacts to advisor for adjudication against hard-fail gates + green-light criteria
10. Sign-off document drafted (mirrors Stage 2b sign-off structure, adds test-retest table with both summary statistics)

---

## 7. Cost and turnaround

- This document: $0 API
- Launch prompt drafting: $0 API (next turn)
- Launch prompt reviewer cycle: $0 API
- Fire-script extension patch: $0 API
- **Stage 2c live fire: ~$0.30-0.45 projected (hard cap $0.50)**
- Total Stage 2c spend: ~$0.30-0.45

Cumulative Phase 2B post-Stage-2c: ~$2.95-3.10 / $30.00 = ~10% utilization.

Expected Stage 2c fire wall-clock: ~5 minutes.
Expected Stage 2c design-to-fire timeline: 2-4 hours given smooth reviewer cycles.

---

**End of D7 Stage 2c Scope Lock document (v2, post-review).**

Ready for Stage 2c launch prompt drafting.
