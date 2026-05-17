# Phase 5.1 Cost-Model Investigation Note — Bucket-1 Cycle Plan

> **For execution discipline:** This is a Charlie-register-gated **Bucket-1-style investigation** plan, NOT a multi-cycle scoping → sub-spec → execute → closeout arc. Each task is gated by Charlie register at register-event boundaries per `feedback_authorization_routing.md` hard rule. **The pre-declared interpretation rules gate (Task 4) is the load-bearing discipline boundary**: analytical pass MUST NOT begin until Charlie ratifies Tasks 1-3 outputs. Plan invariant once ratified; refinements require fresh Charlie register.

**Goal:** Produce a single Bucket-1-style investigation note that decomposes Phase 4's null result by cost assumption, using sealed Phase 4 cost-run artifacts at 7/13/15/17 bps on the 39 cohort_a candidates, with pre-declared interpretation rules set before any analytical pass.

**Architecture:** Single-deliverable investigation note at `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md`. Pre-declared interpretation rules + cost regime rationale ratified BEFORE analytical pass to prevent post-hoc threshold fitting (ChatGPT anti-alpha-rescue nuance). Q1 scope-shape: (a) sealed-artifact gross-vs-realistic decomposition only; (b) extended real-cost-discovery deferred to separate register-event conditional on (a)'s findings.

**Tech Stack:** Read-only consumption of sealed Phase 4 artifacts at `data/phase2c_evaluation_gate/phase4_forward_2026_{07,13,15,17}bps_v1/`; pandas for CSV analytics; matplotlib optional for visualization. No code modification expected. No new batch fires. No engine touches.

---

## §0 — Cycle metadata

### §0.1 — Cycle anchor

Phase 5.1 cost-model investigation cycle entry register-event fired at 2026-05-17. Predecessor Phase 5 SEALED at `54ba912` (diagnostic execution arc-level closeout) + `4b9e2dc` (Phase Marker advance) + tag `phase5-diagnostic-execution-v1`. Per sealed Phase 5 §4a `successor_class_outputs.json`: single eligible assignment = `"cost-model investigation eligible (gross-vs-realistic decomposition)"`. Disposition: `eligible`, NOT `authorized` — cycle shape is Charlie's adjudication.

### §0.2 — Authorization register

| Register | Text | Gate | Scope |
|---|---|---|---|
| Phase 5.1 cycle entry | "authorize on convergence" | Charlie register at 2026-05-17 (this cycle) | Authorizes 4-leg convergent recommendation: Template B Bucket-1 investigation note + Q1 (a) first + (b) conditional + disciplines + Codex eligible-not-automatic at pre-SEAL + bundle independent |
| Sequencing choice | "Option α" | Charlie register at 2026-05-17 (this cycle) | writing-plans skill invocation for lightweight Bucket-1 plan; analytical pass gated by Charlie ratify of Tasks 1-3 |
| Codex routing timing | "agree with your lean" | Charlie register at 2026-05-17 (this cycle) | Codex routing eligibility re-evaluated at pre-SEAL after analytical pass, not at draft surface |
| Plan ratify | implicit per "β-2 authorized" + 3/3 spot-check PASS | Charlie register at 2026-05-17 | Plan as-amended ratified after 9 edits (6 mechanical refinements + 3 Round 6 gap-close completing Round 4-5 ADOPTED Pushback 3 scope) |
| Step 1.1 fire | "Authorized for step 1.1" | Charlie register at 2026-05-17 | Single-step authorization fired; Step 1.1 PASS (4 CSV paths verified, n=39 confirmed) |
| Cadence β | "Cadence β authorized" | Charlie register at 2026-05-17 | Steps 1.2-1.6 fire in sequence; stop at Task 1.7 mini-gate |
| Task 1.7 mini-gate ratify | "Option 2 authorized" | Charlie register at 2026-05-17 | Input survey ratified; §4.4 disclosure note added to investigation note (Step 1.5 empty grep = documented audit-trail per execution.yaml inheritance); Task 2 grounding discipline binding (PHASE4_PLAN + execution.yaml canonical, not PHASE2C_15_PLAN) |
| Audit-trail micro-fix (canonicalize plan) | "Option A authorized" | Charlie register at 2026-05-17 | Plan moved from /tmp/ ephemeral to docs/phase5/PHASE5_1_INVESTIGATION_PLAN.md git-tracked location per ChatGPT path recommendation; commit framing audit-trail-durability; Task 2 fire requires separate fresh register |
| Pre-declared rules gate (Task 4) | PENDING | After Tasks 2-3 | Required before Task 5 (analytical pass) fire; Task 4 scope narrowed to Tasks 2-3 by Task 1.7 split |
| Pre-SEAL Codex routing decision | PENDING | After Task 7 | Required before Task 9 (Codex fire decision) |
| SEAL register | PENDING | After Task 8 + 9 | Required for final commit + Phase Marker advance |

### §0.3 — ChatGPT precision rule scope at Phase 5.1

This cycle is authorized to:
- Decompose Phase 4 null result using sealed cost-run artifacts at 7/13/15/17 bps
- Pre-declare interpretation rules + cost regime enumeration BEFORE analytical pass
- Apply rules mechanically to decomposition output
- Surface successor routing observation matrix (paths eligible-not-named per §10 sub-§§ codified)
- Produce single investigation note deliverable

This cycle MUST NOT:
- Modify sealed Phase 4/5 corpus or sealed Phase 5 §4a output
- Run new batch fires (no API spend on new generation)
- Activate `phase2.5/bandit-dedup` parked branch
- Continue Path 3 methodology consolidation cycles
- Pre-commit to refire (refire eligible only conditional on this cycle's resolution per ChatGPT refinement)
- Post-hoc adjust interpretation rules after seeing analytical output (anti-alpha-rescue discipline)
- Extend to real-cost-discovery in this cycle (deferred to separate register-event per Q1 (b))
- Bundle CLAUDE.md spend freshness fix into this deliverable scope
- Re-narrate Phase 5 three discharged narration authorities

### §0.4 — Discipline anchors operating throughout

1. **Pre-declared interpretation rules invariance** (load-bearing per ChatGPT anti-alpha-rescue nuance): rules set + Charlie-ratified BEFORE analytical pass; rules applied mechanically thereafter; no post-hoc rule modification without explicit errata register-event
2. **Anti-momentum-binding** per `feedback_authorization_routing.md` + METHODOLOGY_NOTES §10 sub-§ codified at Pass 2: each gate fire requires fresh Charlie register; this plan ratification does NOT pre-authorize subsequent gates
3. **Anti-pre-naming preservation** per METHODOLOGY_NOTES §10 sub-§: successor paths surfaced as observations, NOT recommendations or pre-bound commitments
4. **Eligible-not-named successor cycle framing** per METHODOLOGY_NOTES §10 sub-§: enumerate without ordering / recommendation / pre-characterization
5. **Sealed-content invariance**: sealed Phase 4/5 artifacts read-only; sealed METHODOLOGY_NOTES §1-§33 invariant; sealed Path 3 corpus invariant; CLAUDE.md Phase Marker prior entries invariant
6. **Per-fix adjudication** per `feedback_reviewer_suggestion_adjudication.md`: at reviewer routing (Task 8), no bulk-accept; reasoned per-finding ADOPT/PUSHBACK
7. **SEAL bundle composition** per METHODOLOGY_NOTES §32 codified at Pass 2: investigation note SEAL bundle = note commit + (optional) Phase Marker advance commit + atomic history file update
8. **Pre-fire micro-check pattern** per METHODOLOGY_NOTES §33 codified at Pass 2: V# anchor verification chain fires at pre-SEAL register-event boundary (Task 9)
9. **Option 1A atomicity** per `feedback_claude_md_freshness.md`: if Phase Marker advance fires, atomically include `CLAUDE.md` + `docs/phase_marker_history.md`; 5th empirical trigger forecast if SEAL produces Phase Marker advance

---

## §1 — Cycle parameters

### §1.1 — Q-disposition

| Q | Disposition | Source |
|---|---|---|
| Q1 Scope shape | (a) sealed-artifact gross-vs-realistic decomposition only; (b) extended real-cost-discovery deferred to separate register-event conditional on (a)'s findings | Charlie register "authorize on convergence" 2026-05-17 |
| Q2 Cycle shape | Template B Bucket-1-style investigation note (single-deliverable; not multi-arc scoping/sub-spec/execute) | Charlie register 4-leg convergent |
| Q3 Reviewer routing | 2-leg default (ChatGPT structural-overlay + Claude advisor full-prose-access); Codex eligible-not-automatic at pre-SEAL trigger per substantive empirical methodology touch | Charlie register + `feedback_codex_review_scope.md` register-class re-evaluation |
| Q4 Pre-declared rules discipline | Rules ratified BEFORE analytical pass; mechanically applied thereafter; anti-alpha-rescue nuance from ChatGPT load-bearing | Charlie register + ChatGPT pushback adoption |
| Q5 Scope discipline | Sealed Phase 4 cost-run artifacts only; no new generation; no engine modification | Charlie register + cycle scope |
| Q6 Successor routing framing | Observation matrix only; eligible-not-named successor paths per §10 sub-§§; no pre-authorization | METHODOLOGY_NOTES §10 sub-§§ codified at Pass 2 |

### §1.2 — Bundle disposition

CLAUDE.md spend freshness fix (May $19.66 vs displayed April $8.65) is **independent**, NOT bundled into this investigation note deliverable. Eligible at:
- Phase Marker advance commit IF this cycle SEAL produces one (ride-along)
- OR separate micro-register-event (independent fire)
- OR defer

Decision deferred to Task 9 (pre-SEAL register-event boundary).

---

## §2 — Investigation note structure (target deliverable)

Target file: `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md`

Section outline (~400-700 lines forecast):

- **§0 Cycle metadata + authorization** — anchor commits, Charlie register chain, ChatGPT precision rule scope
- **§1 Scope text** — Q1 (a) sealed-artifact only; (b) extended deferred to separate register-event
- **§2 Cost regime enumeration with rationale** — bounded regimes + sealed-project rationale for each + external grounding declaration (where applicable)
- **§3 Pre-declared interpretation rules** — applied mechanically at §5; structure: trigger condition → interpretation outcome → successor observation
- **§4 Sealed input survey** — Phase 4 cost-run artifact paths + schemas + n=39 confirmed + stratum split A=22 / B=17
- **§5 Analytical pass: per-candidate cost-regime sensitivity decomposition** — at 7/13/15/17 bps; stratified by stratum
- **§6 Pre-declared rule application** — mechanical mapping from §5 results to §3 interpretation outcomes
- **§7 Successor routing observation matrix** — eligible-not-named paths conditional on §6 outcomes; no pre-authorization
- **§8 V# anchor chain verification** — per Task 9 pre-SEAL micro-check
- **§9 Reserved decisions** — per anti-pre-emption invariant

---

## §3 — Task sequence

### Task 1: Sealed input survey

**Files:**
- Read-only: `data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/holdout_results.csv`
- Read-only: `data/phase2c_evaluation_gate/phase4_forward_2026_13bps_v1/holdout_results.csv`
- Read-only: `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv`
- Read-only: `data/phase2c_evaluation_gate/phase4_forward_2026_17bps_v1/holdout_results.csv`
- Read-only: `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_summary.json` (cross-check schema)
- Read-only: `data/phase4_scoping/cohort_a_candidate_reference.csv` (stratum reference)
- Read-only: `docs/phase2c/PHASE2C_15_PLAN.md` + `docs/phase4/PHASE4_PLAN.md` (cost-basis selection rationale)

- [ ] **Step 1.1: Verify all 4 cost-run CSV paths exist and have 39 rows each**

```bash
for cost in 07 13 15 17; do
  echo "=== ${cost}bps ==="
  wc -l data/phase2c_evaluation_gate/phase4_forward_2026_${cost}bps_v1/holdout_results.csv
done
```

Expected: 4 files exist, each with 40 lines (39 rows + 1 header).

- [ ] **Step 1.2: Inspect CSV schema (column names + dtypes) on one file**

```bash
head -1 data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv
```

Expected: column header revealing structure (likely includes candidate_id, sharpe_ratio, total_return, total_trades, plus other metrics).

- [ ] **Step 1.3: Verify cohort_a stratum reference CSV exists + matches n=22 A / n=17 B**

```bash
wc -l data/phase4_scoping/cohort_a_candidate_reference.csv
head -1 data/phase4_scoping/cohort_a_candidate_reference.csv
```

Expected: 40 lines (39 + header); column header reveals stratum labels.

- [ ] **Step 1.4: Read PHASE4_PLAN cost-basis selection rationale (search for "15bps" + "cost" + "realistic")**

```bash
grep -n -i "15bps\|cost basis\|realistic" docs/phase4/PHASE4_PLAN.md | head -30
```

Expected: rationale for why 7/13/15/17 bps grid was selected; specifically why 15bps was the "realistic" success-criterion basis.

- [ ] **Step 1.5: Read PHASE2C_15 cost selection rationale (search same terms)**

```bash
grep -n -i "7bps\|effective cost\|cost model" docs/phase2c/PHASE2C_15_PLAN.md | head -30
```

Expected: rationale for 7bps "effective cost/side" used in research-time backtests.

- [ ] **Step 1.6: Output sealed input survey summary to investigation note draft §4**

Write `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` skeleton with §0 (anchor + authorization chain) + §4 (sealed input survey results). No analytical content yet.

**Expected output**: skeleton file with §0 + §4 populated; rest of sections placeholder-marked as `[pending Task N]`.

- [ ] **Step 1.7: Pre-Tasks-2-3 GATE — Charlie ratify input survey output (mini-gate)**

Per Round 4-5 ADOPTED Pushback 3 (Task 4 ratify bundle too big; split input-survey ratify from rules-design ratify). This mini-gate narrows Task 4 scope from "Tasks 1-3" to "Tasks 2-3" by ratifying input survey separately here. The mini-gate lets Task 2-3 design respond to input-survey reveal before being authored, rather than being designed in parallel and then bundled-ratified at Task 4.

Substep:

Plain-text summary in chat:
- §4 sealed input survey contents: 4 CSV paths verified at expected locations; schemas inspected; n=39 confirmed; stratum reference A=22/B=17 confirmed; cost-basis rationale grep summary (key findings from PHASE4_PLAN + PHASE2C_15_PLAN)

Surface for Charlie register confirmation that input survey is clean. If Charlie surfaces specific input-survey concerns (e.g., unexpected CSV schema reveal that affects Task 2-3 design, or cost-basis rationale grep surfacing rationale that changes regime enumeration), apply per per-fix adjudication and re-surface; if ratified, proceed to Task 2.

**HARD GATE — do NOT proceed to Task 2 without Charlie ratify.** Anti-momentum-binding strict reading: Charlie register required at Task 1.7 mini-gate. Plan ratify in §0.2 does NOT pre-authorize this gate. Steps 1.1-1.6 completion does NOT pre-authorize Task 2 start.

**Expected output**: Charlie register at Task 1.7 mini-gate; ratify text recorded in §0.2 register chain table. Task 2 fire awaits separate Charlie register.

---

### Task 2: Cost regime enumeration with rationale

**Files:**
- Modify: `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (§2 added)

- [ ] **Step 2.1: Enumerate bounded candidate cost regimes**

The 4 cost-run grid (7/13/15/17 bps) is the empirical evidence base. Pre-declare 3-4 cost regime BUCKETS that map cost values to project-relevant rationale (NOT to "results we want to see"):

| Regime | Cost range | Rationale source |
|---|---|---|
| **Research-time** (R) | 7 bps | Sealed CLAUDE.md execution.yaml `effective_7bps_per_side` (4bps Binance taker fee + 3bps slippage); used throughout Phase 1-2 backtests including PHASE2C_15 |
| **Realistic-conservative** (RC) | 13-15 bps | Sealed PHASE4_PLAN §1.4-§1.5 selected 15bps as "realistic" basis with ±2bps sensitivity at 13/17; rationale from Task 1.4 grep |
| **Stress** (S) | 17 bps | Sealed PHASE4_PLAN sensitivity upper band (15+2) |

If Task 1 grep reveals additional rationale (e.g., explicit Binance VIP-tier fee schedule reference), document it in §2.

- [ ] **Step 2.2: Declare what each regime represents in execution reality terms**

For each regime, write 1-2 sentences in the investigation note §2 specifying:
- What execution conditions justify this cost (size, liquidity, hour-of-day, maker/taker mix)
- What the project's evidence for the regime is (sealed source or "untested assumption")
- What this regime does NOT capture (boundary conditions)

- [ ] **Step 2.3: Declare external-grounding need explicitly**

Per Q1 (a) scope binding, this cycle does NOT do external real-cost-discovery. In §2, write explicit text:

> External grounding for "true realistic cost on Binance BTC/USDT spot at this trade frequency" is NOT done in this investigation cycle per Q1 scope-shape (a). All cost regime ranges and rationale are derived from sealed project artifacts. Extended real-cost-discovery (external Binance fee schedule reference, order book replay, paper trading calibration, exchange microstructure analysis) is eligible-not-named at separate Charlie register-event per Q1 (b), conditional on this cycle's findings revealing it as needed.

**Expected output**: §2 populated with 3-4 regime buckets + rationale + external-grounding declaration.

---

### Task 3: Pre-declared interpretation rules

**Files:**
- Modify: `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (§3 added)

This is the load-bearing discipline content per ChatGPT anti-alpha-rescue nuance. Rules MUST be written BEFORE Task 5 analytical pass. Charlie ratification at Task 4 gate is the discipline boundary.

- [ ] **Step 3.1: Pre-declare metric-of-interest**

Specify what metric is computed for interpretation:
- Per-candidate: net Sharpe at each cost regime
- Per-stratum aggregate: count of candidates with `net_sharpe > 0` at each cost regime; binomial test result vs PHASE4_PLAN §1.5 threshold

Reference: PHASE4_PLAN §1.5 used `binomial test on positive-forward-Sharpe count` per stratum at 15bps as success criterion (Stratum A ≥17/22; Stratum B ≥13/17).

- [ ] **Step 3.2: Pre-declare per-stratum disposition framework with D-IV-first sequencing**

Write in §3 verbatim (no later modification). Each of Stratum A and Stratum B is classified INDEPENDENTLY using a two-step process; per-stratum dispositions then aggregate to joint pattern at Step 3.3.

**Step A (D-IV sanity check, applied FIRST per stratum):**

Is the binomial-test positive-count sequence at this stratum across [7, 13, 15, 17] bps **weakly monotonic non-increasing** (`count[i+1] ≤ count[i]` for all i; ties allowed)?

- NO → **D-IV (non-categorical)**: methodology / sample-size issue on this stratum. STOP per-stratum classification at Step A.
- YES → proceed to Step B.

**Step B (binary classification, only if Step A passes):**

With monotonicity verified, classify by binary (meets-at-7bps, meets-at-15bps) per Phase 4 §1.5 binomial threshold (Stratum A ≥17/22, Stratum B ≥13/17):

- meets at 7 AND meets at 15 → **D-III (persistent alpha)**: alpha persists at realistic 15bps cost on this stratum
- meets at 7 AND fails at 15 → **D-I (cost-conservatism)**: salvageable on this stratum at research-time 7bps cost; cost-conservatism is the proximate cause of Phase 4 null on this stratum
- fails at 7 (which under monotonicity implies fails at 13, 15, 17) → **D-II (cost not the cause)**: cost is NOT the dominant failure mode on this stratum (lowest tested cost still produces null)

Genuinely MECE per stratum under D-IV-first sequencing.

- [ ] **Step 3.3: Pre-declare aggregate successor matrix (joint patterns → eligible-not-named paths)**

Write in §3 verbatim. The investigation's overall disposition is the JOINT pattern across both strata. Per METHODOLOGY_NOTES §10 sub-§§ codified at Path 3 Pass 2, all successor paths surfaced as eligible-not-named — NOT recommendations, ordering, or pre-characterizations:

| Joint (A, B) | Eligible-not-named successor paths |
|---|---|
| (D-III, D-III) | Persistent alpha on full cohort. Paper trading on full 39-candidate cohort at realistic 15bps cost is eligible. Extended real-cost-discovery to confirm realistic cost is eligible. |
| (D-III, D-I), (D-III, D-II), (D-I, D-II) — **mixed disposition** | Paper trading on stronger-disposition stratum subset is eligible. Extended real-cost-discovery on the cost-conservatism hypothesis is eligible. Strategic reconsideration on weaker-disposition stratum is eligible. |
| (D-I, D-I) | Both strata salvageable at research-time cost. Paper trading at research-time cost basis on full cohort is eligible. Extended real-cost-discovery to confirm realistic cost is eligible. |
| (D-II, D-II) | Cost not the cause anywhere. Strategy / asset / timeframe reconsideration is eligible. Bandit-dedup activation is structurally relevant ONLY conditional on separate Charlie register for batch cadence resumption intent per [`PARKED_BRANCHES.md`](../parked/PARKED_BRANCHES.md) — joint pattern firing does NOT automatically constitute batch cadence resumption intent. Paradigm-exhaustion is eligible-not-named. |
| Any D-IV | Methodology refinement at separate register-event eligible BEFORE further interpretation on the D-IV stratum. Investigation note's overall successor routing is deferred for the D-IV stratum until methodology is refined. |

- [ ] **Step 3.4: Pre-declare what would VIOLATE the interpretation discipline (HARD STOP triggers)**

Write in §3 verbatim:

> The following would constitute post-hoc threshold fitting (anti-alpha-rescue violation):
> - Adjusting cost regime ranges in §2 after seeing §5 analytical results to make a more favorable disposition fire
> - Adding new dispositions or matrix rows in §3 after §5 results to capture a borderline result
> - Modifying the metric-of-interest in §3.1 after §5 to use a different threshold that produces a more favorable disposition
> - Re-running the analytical pass at additional non-pre-declared cost values to find a more favorable result
> - Relaxing the D-IV monotonicity requirement after §5 to push a non-monotonic stratum into D-I/D-II/D-III
> - Re-framing successor paths in §7 to inject ordering / recommendation / pre-characterization after §6 fires
>
> If any of these are tempted after §5, the correct action is HARD STOP + errata register-event at separate Charlie register-event boundary, not silent modification.

- [ ] **Step 3.5: Pre-declare illustrative classification examples (for Task 6 mechanical-application reference)**

Write in §3 verbatim. The following table illustrates how the per-stratum disposition framework applies to hypothetical count sequences. **These are illustrative classification examples, NOT formal correctness validation tests** — they exist to make Task 6 mechanical application auditable, not to validate the rules themselves.

| Hypothetical count sequence at [7, 13, 15, 17] bps | Stratum (threshold differs) | Step A: monotonic? | Step B: meets / fails | D-classification | Notes |
|---|---|---|---|---|---|
| [17, 12, 11, 10] | A (threshold ≥17/22) | yes (17≥12≥11≥10) | meets-7 (17=17) AND fails-15 (11<17) | **D-I** | matches observed Phase 4 §3 Stratum A pattern |
| [9, 8, 7, 5] | B (threshold ≥13/17) | yes | fails-7 (9<13) | **D-II** | matches observed Phase 4 §3 Stratum B pattern |
| [17, 15, 13, 17] | A | NO (13 < 17 at last step violates non-increasing) | n/a (Step A fails) | **D-IV** | non-monotonic; Task 6 mechanical application halts at Step A |
| [22, 22, 22, 22] | A | yes (flat counts as weak non-increasing) | meets-7 (22≥17) AND meets-15 (22≥17) | **D-III** | hypothetical strong cohort; ties at boundary acceptable |
| [17, 17, 17, 17] | A | yes (flat) | meets-7 AND meets-15 | **D-III** | hypothetical alpha at threshold edge; ties acceptable |

These examples illustrate the mechanical application of Steps A + B. Task 6 fire applies the same logic to actual §5 results.

**Expected output**: §3 populated with per-stratum disposition framework (D-IV-first sequencing + D-I/II/III/IV definitions) + joint successor matrix + violation declaration + illustrative classification examples table. Section locked at Charlie ratify in Task 4.

---

### Task 4: Pre-analytical-pass GATE — Charlie ratify Tasks 2-3

Note: Task 4 scope narrowed from "Tasks 1-3" to "Tasks 2-3" per Round 4-5 ADOPTED Pushback 3 — §4 sealed input survey ratified separately at Task 1.7 mini-gate. Task 4 here ratifies Task 2 cost regime enumeration + Task 3 pre-declared interpretation rules only.

**Files:**
- Read: `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` §0 + §2 + §3

- [ ] **Step 4.1: Surface Tasks 2-3 output to Charlie for ratify**

Plain-text summary in chat:
- §2 cost regime enumeration: 3-4 regime buckets with sealed rationale per regime + external-grounding declaration
- §3 pre-declared interpretation rules: per-stratum disposition framework (D-IV-first sequencing + D-I/II/III/IV definitions) + joint successor matrix (5 rows) + violation declaration + illustrative classification examples table

Surface for Charlie register confirmation that §2 + §3 are accepted as ratified-before-analytical-pass. If Charlie surfaces refinements, apply per per-fix adjudication and re-surface; if ratified, proceed to Task 5.

- [ ] **Step 4.2: HARD GATE — do NOT proceed to Task 5 without Charlie ratify**

Anti-momentum-binding strict reading: Charlie register required at Task 4 gate. Plan ratify in §0.2 above does NOT pre-authorize this gate. Task 1.7 mini-gate ratify does NOT pre-authorize Task 4 gate either — separate register events.

**Expected output**: Charlie register at Task 4 gate; ratify text recorded in §0.2 register chain table.

---

### Task 5: Analytical pass — per-candidate cost-regime sensitivity decomposition

**Files:**
- Modify: `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (§5 added)
- Read-only: 4 cost-run CSVs + cohort_a stratum reference

- [ ] **Step 5.1: Load 4 cost-run CSVs into pandas DataFrames**

Inline Python (executed via Bash heredoc):

```python
import pandas as pd
from pathlib import Path

base = Path("data/phase2c_evaluation_gate")
costs = [7, 13, 15, 17]
dfs = {
    c: pd.read_csv(base / f"phase4_forward_2026_{c:02d}bps_v1" / "holdout_results.csv")
    for c in costs
}

# Verify shape consistency
for c, df in dfs.items():
    print(f"{c}bps: shape={df.shape}, columns={list(df.columns)[:8]}")
```

Expected: 4 DataFrames, each (39, K) with shared schema.

- [ ] **Step 5.2: Join cohort_a stratum reference to identify Stratum A vs B per candidate**

```python
stratum_ref = pd.read_csv("data/phase4_scoping/cohort_a_candidate_reference.csv")
print(f"stratum_ref columns: {list(stratum_ref.columns)}")
print(stratum_ref.head())

# Identify the stratum column name (likely "stratum" or "stratum_label")
# Join to each cost-run DataFrame
```

Expected: stratum column identified; A=22 / B=17 split confirmed.

- [ ] **Step 5.3: Compute per-stratum positive-Sharpe count at each cost regime**

```python
# For each cost regime, compute per-stratum count of candidates with sharpe > 0
results = []
for cost, df in dfs.items():
    merged = df.merge(stratum_ref, on="candidate_id")  # adjust on= per actual schema
    for stratum in ["A", "B"]:
        subset = merged[merged["stratum"] == stratum]  # adjust column name per actual
        positive = (subset["sharpe_ratio"] > 0).sum()
        total = len(subset)
        results.append({"cost_bps": cost, "stratum": stratum, "positive": positive, "total": total})

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))
```

Expected output (illustrative; actual values from Phase 4 results §3):
- 7bps: A 17/22, B 9/17
- 13bps: A 12/22, B 8/17
- 15bps: A 11/22, B 7/17
- 17bps: A 10/22, B 5/17

(Phase 4 §3 already reports these; this step verifies reproduction from sealed CSVs.)

- [ ] **Step 5.4: Compute binomial test p-value per (cost, stratum) cell**

```python
from scipy.stats import binomtest

for row in results_df.itertuples():
    test = binomtest(row.positive, row.total, p=0.5, alternative="greater")
    print(f"cost={row.cost_bps}bps stratum={row.stratum}: {row.positive}/{row.total}, p={test.pvalue:.4f}")
```

Expected: p-values per cell; verifies Phase 4 §3 binomial-test results at 15bps (p_A=0.5841, p_B=0.8338) and produces analogous values at 7/13/17 bps.

- [ ] **Step 5.5: Document analytical pass output in investigation note §5**

Write a summary table (cost × stratum × {count, total, binomial p}) into `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` §5. NO interpretation in §5 — pure observation.

**Expected output**: §5 populated with summary table; raw Python output captured for reproducibility.

---

### Task 6: Pre-declared rule application

**Files:**
- Modify: `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (§6 added)

- [ ] **Step 6.1: Per-stratum disposition classification with D-IV-first sequencing**

For EACH of Stratum A and Stratum B independently, apply §3.2 Step A then Step B against §5 results:

For Stratum A:
- Step A: is the count sequence at [7, 13, 15, 17] bps for Stratum A weakly monotonic non-increasing (`count[i+1] ≤ count[i]` for all i)? YES → proceed to Step B. NO → **D-IV (Stratum A)**, halt classification on A.
- Step B (if Step A passes): apply (meets-at-7bps, meets-at-15bps) per Phase 4 §1.5 threshold (Stratum A ≥17/22):
  - meets at 7 AND meets at 15 → **D-III (Stratum A)**
  - meets at 7 AND fails at 15 → **D-I (Stratum A)**
  - fails at 7 → **D-II (Stratum A)**

For Stratum B: same procedure with Stratum B threshold (≥13/17).

Cross-reference §3.5 illustrative classification examples table to verify mechanical application matches expected pattern.

- [ ] **Step 6.2: Document per-stratum dispositions + joint pattern**

Write in §6: per-stratum disposition table + joint pattern identification + matrix row from §3.3 that applies to this joint pattern.

Structure:

| Stratum | Step A monotonic? | Step B meets-at-7 / meets-at-15 | D-classification |
|---|---|---|---|
| A | YES / NO | (filled from §5) | D-I / D-II / D-III / D-IV |
| B | YES / NO | (filled from §5) | D-I / D-II / D-III / D-IV |

Joint pattern: (D-X for A, D-Y for B). Matrix row applied per §3.3.

- [ ] **Step 6.3: Surface eligible-not-named successor paths verbatim from §3.3 matrix row**

Per §3.3 matrix row corresponding to observed joint pattern, surface the eligible-not-named successor paths VERBATIM. No re-framing, no ordering injection, no recommendation language per §3.4 violation declaration #6.

- [ ] **Step 6.4: HARD STOP if interpretation discipline violation tempted**

If §5 results suggest a per-stratum disposition that doesn't quite fit any §3.2 Step A or Step B trigger, OR if it's tempting to refine §3 language to make a better fit, OR if §3.3 matrix doesn't have a row covering the observed joint pattern, HARD STOP per §3.4 violation declaration. Surface to Charlie for errata register-event decision.

**Expected output**: §6 populated with per-stratum disposition table + joint pattern + verbatim matrix row application; OR HARD STOP triggered if violation tempted.

---

### Task 7: Successor routing observation matrix

**Files:**
- Modify: `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (§7 added)

- [ ] **Step 7.1: Write successor routing observation matrix per fired bucket**

Per §3 each bucket specifies "successor observation" — eligible-not-named paths. Per §10 sub-§§ codified at Pass 2 (anti-momentum-binding + anti-pre-naming preservation + eligible-not-named successor framing), §7 surfaces paths as OBSERVATIONS, NOT recommendations or pre-authorization.

Write in §7: bullet list of eligible-not-named successor paths conditional on which bucket fired, with explicit anti-pre-naming framing.

Example structure (if Bucket III fires):
> Eligible-not-named successor paths conditional on Bucket III firing:
> - Extended real-cost-discovery per Q1 (b) (external Binance fee schedule reference, order book replay, paper trading calibration)
> - Methodology refinement of decomposition approach (more cost regimes, larger sample size via PHASE2C_15 re-cohort, etc.)
> - Pause / strategic-absorption register-event
> - Other Charlie-specified
>
> Each requires fresh Charlie register at separate register-event boundary per `feedback_authorization_routing.md` hard rule. This §7 surfaces eligibility, NOT recommendation.

- [ ] **Step 7.2: Surface forward-only carry-forward observations (if any)**

If during Tasks 1-6 any cycle-internal observations surfaced that are out-of-scope for this cycle but worth logging for future register-event consideration, enumerate them in §7 as forward-only log entries per METHODOLOGY_NOTES §31 #1 + Path 3 sub-spec §4.1 in-scope-refinement vs out-of-scope distinction.

**Expected output**: §7 populated with eligible-not-named successor matrix + forward-only carry-forward list.

---

### Task 8: Investigation note draft assembly + pre-SEAL Codex routing decision

**Files:**
- Modify: `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (final assembly)

- [ ] **Step 8.1: Final assembly check — all sections §0-§7 populated**

Read full note; verify:
- §0 anchor + authorization chain complete with verbatim Charlie register text
- §1 scope text complete
- §2 cost regime enumeration with rationale complete
- §3 pre-declared interpretation rules complete (LOCKED at Task 4 ratify)
- §4 sealed input survey complete
- §5 analytical pass output complete
- §6 mechanical bucket fire complete
- §7 successor routing observation matrix complete
- §8 V# anchor chain — placeholder for Task 9 pre-SEAL fire
- §9 reserved decisions — populate from Task 7 carry-forwards

- [ ] **Step 8.2: Pre-SEAL Codex routing decision**

Per Charlie register confirmation (Codex eligible-not-automatic at pre-SEAL): decide whether to fire Codex adversarial review on the substantive empirical content of the note before SEAL.

Decision criteria:
- Substantive empirical methodology touch? YES (cost-model decomposition + statistical interpretation rules)
- Risk of LLM-prior-correlation artifact? Real (3-leg LLM + my reversal velocity demonstrated in this thread)
- Codex SKIP register-class binding (process/spec deliverable)? Investigation note is borderline — substantive empirical analytics but Bucket-1 lightweight cadence ≠ multi-cycle spec

Surface to Charlie for register decision: FIRE Codex / SKIP Codex. Default lean per Charlie register convergence: eligible-not-automatic means surface decision for Charlie, do not auto-fire.

**Expected output**: Charlie register decision on Codex routing; if FIRE, proceed to Task 8.3; if SKIP, jump to Task 9.

- [ ] **Step 8.3: (Conditional on Charlie FIRE Codex) Codex adversarial review**

If Charlie register fires Codex routing at Task 8.2:
- Use codex:codex-rescue agent with adversarial review prompt focused on: (a) §3 pre-declared rule logical consistency, (b) §6 mechanical application correctness, (c) §7 anti-pre-naming compliance
- Surface findings to Charlie for per-fix adjudication per `feedback_reviewer_suggestion_adjudication.md` (no bulk-accept)
- Apply ADOPTed findings; record DEFER/PUSHBACK reasons

**Expected output**: (if FIRE) Codex findings + per-fix adjudication outcome; (if SKIP) proceed directly to Task 9.

---

### Task 9: Pre-SEAL V# anchor verification chain + SEAL register

**Files:**
- Modify: `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (§8 populated)
- Conditional: `CLAUDE.md` Phase Marker section (if bundled per Task 9.3 decision)
- Conditional: `docs/phase_marker_history.md` (Option 1A atomicity if Phase Marker advance fires)

Per METHODOLOGY_NOTES §33 codified at Pass 2: V# anchor verification chain fires at pre-SEAL register-event boundary.

- [ ] **Step 9.1: Fire V# anchor chain (pre-defined at this plan §4 below)**

Run each V# anchor; record CLEAN / FAIL per anchor in §8 of investigation note.

HARD STOP if any V# FAIL; resolution requires errata register-event at separate Charlie register-event boundary before re-fire.

- [ ] **Step 9.2: Reviewer routing — surface draft to ChatGPT + Claude advisor**

Per Q3 2-leg default: surface draft note to ChatGPT structural-overlay + Claude advisor full-prose-access. Receive findings; apply per-fix adjudication per `feedback_reviewer_suggestion_adjudication.md`.

This step may take 1-2 reviewer rounds; each round requires Charlie register for fire authorization (anti-momentum-binding strict reading).

- [ ] **Step 9.3: Bundle decision — CLAUDE.md spend freshness fix**

Per Charlie register convergence + ChatGPT explicit bundling caveat: if Task 9 produces a Phase Marker advance commit (likely for substantive Bucket-1 deliverable SEAL), CLAUDE.md spend freshness fix may ride that natural Phase Marker touch. If NO Phase Marker advance fires this cycle SEAL, spend fix is independent register-event OR deferred.

Surface to Charlie for register decision: BUNDLE spend fix into Phase Marker advance / SEPARATE register-event / DEFER. 

- [ ] **Step 9.4: SEAL register fire**

Charlie register required for SEAL fire. SEAL bundle per METHODOLOGY_NOTES §32 codified at Pass 2:
1. Investigation note commit (substantive deliverable)
2. (Conditional) Phase Marker advance commit with atomic `CLAUDE.md` + `docs/phase_marker_history.md` per Option 1A (5th empirical trigger forecast if fires)
3. Push
4. NO tag (Bucket-1 investigation note ≠ arc-level closeout; default per §32 sub-§ tag policy)

**Expected output**: SEAL bundle committed + pushed; Phase Marker history updated (if Phase Marker advance fires); investigation note SEALED.

---

### Task 10: Post-SEAL handoff write

**Files:**
- Create: `/tmp/phase5_1_cost_model_investigation_seal_handoff_2026-05-XX.md`

- [ ] **Step 10.1: Charlie register at Gate handoff write**

Per Path 3 + Phase 5 precedent: post-SEAL handoff write requires Charlie register at separate gate.

- [ ] **Step 10.2: Write handoff prompt for next session entry**

Mirror Path 3 Pass 2 SEAL handoff structure:
- Part 1: What this session accomplished
- Part 2: State at session close (working tree + sealed corpus + memory state + framework state + forward-only carry-forward observations)
- Part 3: Next session planning (entry posture + eligible-not-named successor paths + atomicity invariant status + authorization-routing reminder)
- Part 4: Verbatim handoff prompt for next session entry

Surface to Charlie for review; finalize per Charlie register.

**Expected output**: handoff prompt at `/tmp/...`; ready for next session entry.

---

## §4 — V# anchor chain (preliminary; finalized at Task 9 fire)

Per METHODOLOGY_NOTES §33: V# anchor chain fires at pre-SEAL register-event boundary. Anchor set is cycle-local; may be refined at Task 9 pre-fire if Tasks 1-8 surface novel scopes.

- **V1 — Pre-declared rules invariance.** §3 interpretation rules text byte-identical to Task 4 Charlie-ratified state; no post-hoc modification. If modified after Task 4 ratify, requires errata register-event citation.

- **V2 — Cost regime rationale grounding.** §2 cost regimes each cite sealed source (CLAUDE.md execution.yaml / PHASE4_PLAN / PHASE2C_15_PLAN) OR explicit "untested assumption" flag; no fabricated rationale.

- **V3 — Stratification consistency.** §5 stratum split A=22 / B=17 matches sealed `cohort_a_candidate_reference.csv`; no leakage.

- **V4 — Interpretation discipline.** §6 mechanical application uses §3 rules verbatim; trigger conditions evaluated against §5 evidence mechanically; no post-hoc rationalization; if HARD STOP triggered at Task 6.3, errata register-event citation present.

- **V5 — Successor routing framing.** §7 surfaces eligible-not-named paths only; no ordering / recommendation / pre-characterization; honors §10 sub-§§ codified at Pass 2.

- **V6 — Discipline guard adherence.** No new batch fires; no bandit-dedup activation; no Path 3 continuation; CLAUDE.md spend fix not bundled into deliverable scope; refire pre-commitment absent.

- **V7 — Sealed corpus invariance.** No modification of sealed Phase 4 cost-run artifacts; no modification of sealed Phase 5 §4a output; no modification of sealed METHODOLOGY_NOTES §1-§33; no modification of sealed Path 3 corpus; no modification of CLAUDE.md Phase Marker prior entries.

- **V8 — Cross-reference integrity.** References to sealed Phase 4 / Phase 5 / METHODOLOGY_NOTES §§ / memory files accurate at register-precision; no fabricated section numbers; no stale tag references.

- **V9 — Charlie register citation accuracy.** "authorize on convergence" + "Option α" + "agree with your lean" + Task 4 ratify + Task 8.2 Codex decision + Task 9.3 bundle decision + Task 9.4 SEAL register all cited verbatim at §0.2 register chain table.

- **V10 — Anti-pre-emption invariant.** §7 + §9 reserved decisions enumerate eligible-not-named paths; no pre-authorization for any successor cycle entry; Q1 (b) extended real-cost-discovery explicitly reserved for separate register-event.

- **V11 — Atomicity binding.** If Phase Marker advance commit fires at Task 9.4, `git diff --cached --stat HEAD` at pre-commit shows BOTH `CLAUDE.md` AND `docs/phase_marker_history.md` staged per Option 1A; 5th empirical trigger forecast.

- **V12 — Q1 scope binding.** Investigation cycle stays within Q1 (a) sealed-artifact-only scope; Q1 (b) extended real-cost-discovery NOT executed this cycle; if Task 5-6 surface need for external grounding, deferred to separate register-event per Q1 (b) discipline.

- **V13 — Pre-declared rules timing.** §3 written + Charlie-ratified BEFORE §5 analytical pass; gap not bridged by mid-cycle rule modification.

- **V14 — §5 pure observation discipline.** Investigation note §5 contains analytical pass output only (numbers, tables, descriptive observation); interpretation language (e.g., "this suggests...", "this implies...", "this means...") absent from §5; all interpretation lives in §6 mechanical rule application; reviewer at Task 9.2 verifies this discipline at register-precision via scan of §5 text for interpretation-flavored language.

V# verification chain fires sequentially at Task 9.1 pre-SEAL register; HARD STOP on any V# FAIL.

---

## §5 — Reserved decisions (per anti-pre-emption invariant)

Reserved at Phase 5.1 SEAL register-event boundary; eligible at separate Charlie register-event boundary:

- **Q1 (b) extended real-cost-discovery cycle entry** — conditional on this cycle's findings revealing need; cycle shape (scoping vs Bucket-1 vs other) at Charlie register
- **Phase 6+ paper trading / live small-size test cycle entry** — conditional on Bucket I firing; cycle shape at Charlie register
- **Phase 2.5 bandit-dedup activation** — eligible-not-named only AND conditional on TWO INDEPENDENT triggers per `PARKED_BRANCHES.md` activation trigger discipline: (i) §3.3 joint pattern (D-II, D-II) firing (cost not the cause anywhere; exploration economics reconsideration structurally relevant); AND (ii) separate Charlie register-event for batch cadence resumption intent. Joint pattern firing alone does NOT automatically constitute batch cadence resumption intent — both triggers required at separate register-events.
- **Path 3.x methodology consolidation continuation** — eligible if cost-model investigation surfaces methodology candidates worth Path 3-style consolidation
- **Path 3 arc-level closeout cycle entry** — Framing C reserved at Path 3 Pass 2 Gate 12; still available
- **CLAUDE.md spend freshness fix** — if not bundled at Task 9.3, eligible at separate micro-register-event
- **Pre-existing noise cleanup** (`.DS_Store` + `docs/d7_stage2c/*`) — independent register-event still eligible
- **Project pause / strategic-absorption register-event** — eligible at any boundary
- **Other Charlie-specified** — eligible

Three Phase 5 narration authorities at `4b9e2dc` remain discharged — Phase 5.1 cycle does NOT re-narrate (per inherited discipline).

---

## §6 — Self-review checklist (pre-fire)

Per writing-plans skill self-review discipline:

**1. Spec coverage:** Charlie register 6-item authorization scope covered? ✓
- (1) Phase 5.1 cost-model investigation direction — Tasks 1-7
- (2) Template B Bucket-1 shape — single-deliverable structure §2 + Tasks
- (3) Q1 (a) sealed-artifact first + (b) conditional — §1.1 Q1 + §0.3 MUST NOT + Task 2.3 + V12
- (4) Pre-declared interpretation discipline — Tasks 3 + 4 + §3 violation declaration + V1 + V13
- (5) Discipline guards (no refire / no bandit / no Path 3 / Codex eligible-not-auto / etc.) — §0.3 + §0.4 + V6
- (6) Bundle independent — Task 9.3 + §0.4 #9 + V6

**2. Placeholder scan:** searched for "TBD" / "TODO" / "fill in later" / "appropriate" / "similar to Task N" — none found in task content. Task content includes specific commands, file paths, expected outputs.

**3. Type consistency:** file paths consistent across tasks (`docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` referenced same in all tasks; `data/phase2c_evaluation_gate/phase4_forward_2026_{XX}bps_v1/holdout_results.csv` consistent). Column names referenced as "adjust per actual schema" where Task 1 will reveal — appropriate hedge given sealed-artifact reading is the first task.

**Self-review result:** plan covers Charlie register scope + no placeholders + types consistent.

---

## §7 — Execution model

Per Charlie register Option α: this plan is invoked via `superpowers:writing-plans`. Execution model is **Inline Execution via superpowers:executing-plans** — NOT subagent-driven, because:
- Bucket-1 cycle is small enough for single-session inline execution
- Charlie register gates at Task 4 + Task 8.2 + Task 9.3 + Task 9.4 + Task 10.1 are critical checkpoints requiring live Charlie engagement, not subagent dispatch
- Per `feedback_authorization_routing.md` strict reading: each gate fire requires fresh Charlie register at the actual session boundary, not subagent-reported convergence

---

**End of Phase 5.1 cost-model investigation cycle plan. STOP before Task 1 fire per (a) plan ratification discipline; Charlie register required at plan ratify gate before any task execution.**
