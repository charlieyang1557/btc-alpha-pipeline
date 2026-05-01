# PHASE2C_11 Scoping Decision — Post-methodology-consolidation successor path

**Status: WORKING DRAFT — pre-seal; anchor-prose-access discipline fires at this scoping-cycle seal register before seal.**

**Anchor:** `4c7d9d2` on origin/main; tag `phase2c-10-methodology-consolidation-v1` pushed.
PHASE2C_10 methodology consolidation arc sealed (METHODOLOGY_NOTES.md §16-§19 + §3.5/§3.6 fold-ins at §16 ### Failure-mode signal; sign-off MD at `ff3e4ca`).

**Naming clarification (anti-pre-naming option ii):** This document's
filename uses `PHASE2C_11` for sequential filename uniqueness only. The
arc designation that this scoping decision selects is NOT pre-committed
in the doc body until the scoping decision itself seals (per anti-pre-
naming discipline carried forward from PHASE2C_9 + PHASE2C_10). Throughout
this document, "the selected arc" or "the successor arc" refers to whatever
arc the §4 selection lands on; no arc-designation pre-commitment.

---

## §0 Document scope and structure

### §0.1 Scope

This document is the post-PHASE2C_10 successor scoping cycle's
adjudication deliverable. It enumerates the deliberation surface
remaining from PHASE2C_10 scoping decision §2 path register (paths
(a) / (b) / (c) / (g) — Phase 2 continuation paths; path (f) — Phase 3
trajectory held), evaluates each path against locked scoping inputs
(uncertainty-resolution register at Phase 2C results; one dominant
uncertainty class only; bounded cycle budget), and selects the
successor arc.

### §0.2 Structure

- §1 Locked scoping inputs (empirical state + decision goal + hard constraints)
- §2 Path enumeration ((a)/(b)/(c)/(g) + (f) held)
- §3 Per-path evaluation against locked Goal + constraints (six-question framework per path)
- §4 Selection adjudication and arc designation
- §5 Scoping-cycle guardrails
- §6 Carry-forward to sub-spec drafting cycle (if applicable)
- §7 Verification chain and dual-reviewer disposition
- §8 Cross-references

### §0.3 Discipline anchors operating at this scoping cycle

- **Anchor-prose-access discipline (METHODOLOGY_NOTES §16).** Fires at this scoping-cycle seal register. Paste relevant prose excerpts; reviewers run substantive pass against actual prose; THEN commit.
- **Anti-momentum-binding discipline.** Reviewer-lean inputs (e.g., ChatGPT's path (b) lean expressed at PHASE2C_10 session close) are scoping-cycle inputs not selection. §3 per-path evaluation produces selection independently.
- **Anti-pre-naming discipline.** Arc designation NOT pre-committed in doc body until §4.4 selection-adjudication seal.
- **Empirical verification (METHODOLOGY_NOTES §1).** Path register sourced from PHASE2C_10 scoping decision §2 (paths a-g) verified at canonical artifact register at this scoping cycle entry.
- **Procedural-confirmation defect class (METHODOLOGY_NOTES §17).** Working draft fires at structural authoring register; substantive prose-pass + dual-reviewer adjudication operate on draft prior to seal commit.

---

## §1 Locked scoping inputs

### §1.1 Engagement mode

**Reviewer-input-assisted authoring with Charlie-register authorization.**
ChatGPT's scoping-doc skeleton + per-path evaluation criteria were
accepted as structural input at session entry; the scoping decision
itself is authored and adjudicated at Charlie-register after per-path
evaluation. This preserves the self-first/receiving-cycle substantive
overlay discipline (METHODOLOGY_NOTES §16 ### Failure-mode signal
§3.6 fold-in) by treating reviewer input as input, not selection.

### §1.2 Current empirical state

PHASE2C arc series produced the following load-bearing empirical record:

- **PHASE2C_6 single-regime evaluation gate (bear_2022 holdout):** 198 corrected-engine candidates evaluated; closeout at `docs/closeout/PHASE2C_6_EVALUATION_GATE_RESULTS.md`.
- **PHASE2C_7.1 multi-regime evaluation gate (bear_2022 + validation_2024):** candidate-aligned comparison; closeout at `docs/closeout/PHASE2C_7_1_RESULTS.md`.
- **PHASE2C_8.1 extended multi-regime evaluation gate (n=4 regimes: bear_2022 + validation_2024 + eval_2020_v1 + eval_2021_v1):** closeout at `docs/closeout/PHASE2C_8_1_RESULTS.md`.
- **PHASE2C_9 mining-process retrospective (light-touch depth):** Case C determination with sub-registers C.1 + C.2 + C.3; closeout at `docs/closeout/PHASE2C_9_RESULTS.md` §8.0-§8.4.
- **PHASE2C_10 methodology consolidation:** METHODOLOGY_NOTES.md §16-§19 sealed; sign-off at `docs/closeout/PHASE2C_10_METHODOLOGY_CONSOLIDATION_SIGNOFF.md`.

**Dominant unresolved uncertainty class at this scoping cycle entry:**
PHASE2C_9 light-touch retrospective produced ambiguous evidence at
sub-registers C.1 (single-trade-margin filter exclusion mechanism at
bear_2022) + C.2 (permissive AND-gate at -10.2% eval_2021_v1 acceptance)
+ C.3 (theme alignment at D7a whole-DSL register). Case C means: the
candidates that survived the evaluation gate may represent real signal
OR may represent selection artifacts; PHASE2C_9 light-touch evidence
register cannot disambiguate.

The substantive register shift since PHASE2C arc series began: discovery
register (find candidates that survive gates) → resolution register
(disambiguate signal-vs-artifact at empirical or methodological
precision before any operational commitment).

### §1.3 Decision goal

**Select one next path that best attacks the dominant uncertainty before
any Phase 3 / live-readiness move.**

The selection is NOT "which path is most interesting" or "which path
has the strongest reviewer lean". The selection is "which uncertainty
class is most decision-blocking; which path most directly attacks that
class".

### §1.4 Hard constraints

Constraint enumeration (5 items):

1. **No Phase 3 authorization unless path (f) explicitly wins.** Phase 3 trajectory held at PHASE2C_10 closeout; selection of (f) requires explicit adjudication that current uncertainty is acceptable for Phase 3 progression, not implicit progression.
2. **No path pre-naming before §4 selection.** Anti-pre-naming discipline carried forward from PHASE2C_9 + PHASE2C_10.
3. **One dominant uncertainty class only.** Composite arcs (e.g., (a)+(b) parallel; (b)+(c) sequential) explicitly out of scope. Per-path evaluation surfaces dominant class; selection lands on single path.
4. **Scope must be executable within bounded cycle budget.** Cycle-scope budget at "medium" register (multi-arc commitment at order-of-PHASE2C_8.1-or-PHASE2C_9 scale; not unbounded). Per-path MVD register surfaces what fits.
5. **Selection adjudication independent of input lean.** Per anti-momentum-binding discipline: ChatGPT scoping-cycle-input lean toward (b) at PHASE2C_10 session close is registered as input not selection; §3 per-path evaluation produces selection at register satisfaction.

---

## §2 Path enumeration

Per PHASE2C_10 scoping decision §2 path register: paths (a) Structured
re-examination / (b) Statistical-significance machinery (Q-9.A) / (c)
Calibration-variation (Q-9.C) / (f) Phase 3 trajectory / (g) Breadth
expansion. Paths (d) "other paths" + (e) methodology consolidation
register exhausted at PHASE2C_10 selection.

This scoping cycle's deliberation surface:

### §2.1 Path (a) — Structured re-examination at depth greater than light-touch

PHASE2C_9 light-touch retrospective surfaced Case C ambiguity but
could not disambiguate. Path (a) attacks: deeper structured
re-examination of the mining-process mechanism that produced the
candidates. Specifically:

- Ingest-layer mechanism reconstruction (Q-9-01 tracked fix at PHASE2C_9 §8.3): close the ingest-layer mechanism reconstruction at depth greater than PHASE2C_9 §3 light-touch register
- A.4 deliberate-staged-tightening-vs-defect adjudication (PHASE2C_9 §6 lone-survivor walkthrough's exclusion mechanism at single-trade-margin filter)
- Ingest-pipeline mechanism specificity at lone-survivor register (A.4-vs-B.3 register adjudication)

**Dominant uncertainty attacked:** mechanism / pipeline interpretation
may be wrong. Specifically: are the candidates we observe surviving
the gates surviving via the mining-process mechanism we *think* is
operating, or via mechanism artifacts we haven't reconstructed?

### §2.2 Path (b) — Statistical-significance machinery (Q-9.A register)

Path (b) attacks: test whether the survival rate observed at
PHASE2C_6/7.1/8.1 evaluation gates is distinguishable from
null/noise distributions. Specifically:

- B.2 cohort_a_filtered = 0 noise-floor null-distribution test (PHASE2C_9 §8.2)
- B.3 one-of-N tail-event-vs-systematic-pattern null-distribution test
- DSR (deflated Sharpe ratio) machinery: account for selection bias when
  evaluating Sharpe ratios at multiple-testing register
- PBO (probability of backtest overfitting) machinery: test whether
  in-sample optimization produces out-of-sample collapse
- CPCV (combinatorial purged cross-validation) machinery: test whether
  the train/test split's specific boundary produces selection artifact

**Dominant uncertainty attacked:** signal may be selection artifact /
noise-floor artifact. Specifically: among the candidates we observe
surviving, are they distinguishable from candidates that would survive
random selection of mining-process outputs?

### §2.3 Path (c) — Calibration-variation (Q-9.C register)

Path (c) attacks: test whether the candidates that survived the
canonical AND-gate calibration would also survive at adjacent
calibration choices, or whether survival is artifact of specific
threshold choices. Specifically:

- A.4 canonical AND-gate calibration variation (vary single-trade-margin
  filter threshold; observe survival rate)
- Lone-survivor permissive AND-gate-acceptance-of--10.2%-return
  calibration variation (vary the per-regime accept threshold; observe
  whether lone survivor survives at tighter threshold or whether
  adjacent candidates surface)
- AND-gate parameter grid sweep at evaluation register

**Dominant uncertainty attacked:** result may depend on brittle gate
thresholds. Specifically: are the candidates we observe surviving
robust across calibration choices, or artifact of specific threshold
selections?

### §2.4 Path (g) — Breadth expansion

Path (g) attacks: test whether current candidate population is
representative of mining-process output, or whether expanded search
produces additional candidates with similar properties (or
disjoint candidates that change the distribution). Specifically:

- Additional mining batches at expanded theme rotation (current
  operational rotation = 5/6 themes per CLAUDE.md operational
  boundary; expand to 6/6)
- Factor library expansion (additional factor categories; vocabulary
  expansion)
- Additional mining-batch count beyond Phase 2C Phase 1 batch_id
  `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`

**Dominant uncertainty attacked:** current search may be too narrow.
Specifically: is the candidate population we evaluated artifact of
specific search-space restrictions, or representative of broader
mining-process behavior?

### §2.5 Path (f) — Phase 3 trajectory

Held per §1.4 constraint 1. Path (f) selection requires explicit
adjudication that current Case C ambiguity + PHASE2C_9 §8.4 mandatory
methodology candidate carry-forward register is acceptable for Phase 3
progression. NOT default progression; explicit adjudication only.

**Dominant uncertainty attacked:** none directly — path (f) operates
at different register-class. Phase 3 progression accepts current
uncertainty as non-blocking and moves toward portfolio-level / live-
trading readiness.

### §2.6 Composite paths

Composite arcs combining multiple paths (e.g., (a) + (b) parallel; (b)
+ (c) sequential; (a) + (c) bundled) are theoretically possible but
explicitly out of scope at §1.4 constraint 3. Single-path arcs only at
this cycle's adjudication; composite consideration deferred to
post-PHASE2C_11 successor scoping cycle.

---

## §3 Per-path evaluation

Evaluation register: each path scored against ChatGPT's six-question
framework:

1. **What uncertainty does this path attack?**
2. **What evidence says this uncertainty is load-bearing?**
3. **What would this path prove or falsify?**
4. **What would remain unresolved after this path?**
5. **Why should this path outrank the others now?**
6. **What is the minimum viable deliverable?**

### §3.1 Path (a) — Structured re-examination at depth greater than light-touch

1. **Uncertainty attacked:** mechanism / pipeline interpretation may
   be wrong. The mining-process behavior we *think* produced the
   candidates may not be the mining-process behavior that *actually*
   produced them.

2. **Evidence load-bearing:** PHASE2C_9 §6 lone-survivor walkthrough
   surfaced ingest-layer mechanism reconstruction as Q-9-01 tracked
   fix at §8.3 register. Case C sub-registers C.1 + C.2 specifically
   document mechanism-related ambiguities that light-touch retrospective
   could not resolve. The mechanism question is decision-blocking IF
   the pipeline behavior is fundamentally different from our model of
   it; statistical significance + calibration variation + breadth
   expansion are all moot if the pipeline mechanism is broken.

3. **Proves / falsifies:** whether mining-process mechanism reconstruction
   at depth-greater-than-light-touch surfaces (i) defects that explain
   observed candidates as artifacts, OR (ii) confirms PHASE2C_9 §3
   light-touch reconstruction at depth, leaving signal-vs-artifact
   question for path (b).

4. **Remains unresolved:** signal-vs-noise null distribution question
   (path b's domain); calibration robustness (path c's domain); search-
   space coverage (path g's domain). Path (a) closes mechanism question
   only.

5. **Why outrank others:** if pipeline mechanism is broken, (b)/(c)/(g)
   are downstream of broken pipeline → moot. Path (a) is upstream of
   the others at logical-register. However: PHASE2C_9 §3 already did
   substantive light-touch reconstruction (1139 lines / 212 file:line
   citations across 9 in-scope source files); the "light-touch" qualifier
   signals depth-relative-to-feasible-deeper-register, not absolute
   shallowness. PHASE2C_9 §3 surfaced Case C ambiguity without surfacing
   major mechanism defects at light-touch register; whether deeper
   reconstruction would surface defects PHASE2C_9 §3 missed is genuinely
   unresolved at this scoping cycle. The "upstream of (b)/(c)/(g)"
   argument has weight; the "diminishing returns at deeper register"
   argument has bounded strength (PHASE2C_9 §3 was light-touch by design;
   absence of surface defects at light-touch register does not entail
   absence of defects at deeper register).

6. **MVD:** ingest-layer mechanism reconstruction at depth-greater-than-
   light-touch + A.4 deliberate-staged-tightening-vs-defect adjudication
   register-precision close + lone-survivor mechanism specificity register
   adjudication. Estimated scope: order-of-PHASE2C_9 scale at deeper
   register (~4-6 weeks; multi-arc commitment).

### §3.2 Path (b) — Statistical-significance machinery (Q-9.A register)

1. **Uncertainty attacked:** signal may be selection artifact / noise-
   floor artifact. Among candidates that survived gates, are they
   distinguishable from candidates that would survive random selection
   from mining-process output distribution?

2. **Evidence load-bearing:** PHASE2C_9 §8.2 forward-pointer register
   explicitly named B.2 cohort_a_filtered = 0 + B.3 one-of-N tail-event
   sub-paths as load-bearing. The "is this signal real" question is the
   load-bearing question for any operational commitment downstream;
   without statistical-significance disambiguation, no defensible
   Phase 3 progression. DSR/PBO/CPCV machinery is the candidate tool
   set for this register-class question at multiple-testing context.

3. **Proves / falsifies:** whether observed survival rate at PHASE2C_8.1
   evaluation gates is distinguishable from null/noise distributions.
   - If statistically significant: signal-real-vs-artifact question
     resolves toward signal-real; remaining uncertainty is mechanism
     (path a register) and calibration robustness (path c register).
   - If not statistically significant: signal-vs-artifact resolves
     toward artifact; mechanism / calibration / breadth become
     downstream-of-non-result.

4. **Remains unresolved:** mechanism question (path a's domain) — even
   significant statistics don't prove the mechanism we think operates is
   the mechanism that produces signal; calibration robustness (path c's
   domain); search-space coverage (path g's domain).

5. **Why outrank others:** statistical significance at multiple-testing
   register is the load-bearing question for any commitment downstream.
   Mechanism reconstruction (path a) is diagnostic-register; calibration
   variation (path c) is robustness-register; breadth expansion (path
   g) is coverage-register. Statistical significance is the
   *existence-register* question — does the signal exist at all,
   distinguishable from noise. Without resolving existence-register,
   diagnostic / robustness / coverage are all premature.

6. **MVD:** DSR or PBO machinery implementation at scope sufficient
   for PHASE2C_8.1 candidate set (n=198). DSR alone is bounded; PBO
   adds combinatorial structure. CPCV adds purged cross-validation
   register — likely beyond MVD scope. Estimated scope: medium-arc
   commitment (multi-arc; bounded; ~3-5 weeks at PBO scope or ~2-3
   weeks at DSR-only scope).

### §3.3 Path (c) — Calibration-variation (Q-9.C register)

1. **Uncertainty attacked:** result may depend on brittle gate
   thresholds. Are observed survivors robust across calibration
   choices, or artifact of specific threshold selections?

2. **Evidence load-bearing:** PHASE2C_9 §8.2 forward-pointer register
   named A.4 canonical AND-gate calibration variation + permissive
   AND-gate-acceptance-of--10.2%-return at lone-survivor register.
   Calibration brittleness is real concern — Case C sub-register C.2
   specifically documents permissive accept-of-loss as ambiguous.
   However: brittleness is *secondary* to existence — if signal doesn't
   exist (path b's domain), brittleness is moot; if signal exists but
   only at narrow calibration band, that's a real but downstream concern.

3. **Proves / falsifies:** whether candidates survive calibration grid
   sweep or whether survival is concentrated at specific threshold
   choices.
   - If robust across grid: calibration brittleness resolves toward
     non-issue; remaining uncertainty is existence (path b) + mechanism
     (path a).
   - If concentrated at narrow band: calibration brittleness is real;
     candidates are likely artifacts of specific threshold selection;
     existence question gets complicated.

4. **Remains unresolved:** existence question (path b's domain) — even
   robust calibration doesn't prove signal-vs-noise; mechanism (path
   a's domain); coverage (path g's domain).

5. **Why outrank others:** calibration brittleness as dominant
   uncertainty class implies threshold-dependent fragility is the
   load-bearing decision-blocker. This is plausible but not strongly
   supported — the load-bearing concern at PHASE2C_9 closeout register
   was Case C ambiguity at signal-vs-artifact register, not threshold
   brittleness specifically. Path (c) addresses an important but
   secondary concern.

6. **MVD:** AND-gate parameter grid sweep at evaluation register
   (single-trade-margin filter threshold + permissive accept threshold;
   2-3 axes at 5-10 grid points each); re-run evaluation against
   existing PHASE2C_8.1 candidate set; observe survival distribution
   across grid. Estimated scope: medium-arc commitment at order-of-
   PHASE2C_8.1 evaluation register (~2-4 weeks).

### §3.4 Path (g) — Breadth expansion

1. **Uncertainty attacked:** current search may be too narrow.
   Specifically: is the candidate population we evaluated artifact of
   specific search-space restrictions (5/6 theme rotation, factor
   library scope, mining-batch count), or representative of broader
   mining-process behavior?

2. **Evidence load-bearing:** narrow-search-space concern is plausible
   at theme-rotation register (5/6 operational rotation per CLAUDE.md
   operational boundary). However: PHASE2C_9 §3 reconstructed mining
   process at substantive depth across the canonical mining batch;
   search-narrowness was not surfaced as Case C-relevant ambiguity
   at PHASE2C_9 register. Load-bearing concern at this scoping cycle
   is signal-vs-artifact at observed candidates (paths a/b/c register),
   not whether broader search produces additional candidates.

3. **Proves / falsifies:** whether expanded mining produces (i)
   additional candidates with similar gate-survival properties (signal-
   register support), OR (ii) disjoint candidates that change candidate
   distribution (hard to interpret), OR (iii) similar gate-survival
   properties at broader search (consistent with current findings).

4. **Remains unresolved:** existence (path b's domain) — more
   candidates surviving doesn't prove statistical significance against
   null; mechanism (path a's domain); calibration (path c's domain).
   Path (g) doesn't directly address signal-vs-artifact disambiguation.

5. **Why outrank others:** path (g) operates at *coverage register* —
   different register-class than (a) mechanism / (b) existence / (c)
   robustness. If coverage is dominant uncertainty class, path (g)
   wins. However: at PHASE2C_9 closeout, the dominant uncertainty was
   signal-vs-artifact at observed candidates (Case C), not whether
   additional candidates exist beyond the observed set. Path (g)'s
   register-class doesn't match the dominant uncertainty class
   identified at §1.2.

   **Substantive observation at advisor register:** path (g) is the only
   path that doesn't directly address signal-vs-artifact disambiguation.
   Paths (a)/(b)/(c) attack the existing candidates' interpretation;
   path (g) expands the candidate set without resolving the existing
   set's ambiguity. If selected, path (g) defers signal-vs-artifact
   resolution to downstream cycle while expanding candidate population.

6. **MVD:** additional mining batches at expanded theme rotation
   (6/6 themes including multi_factor_combination; or factor library
   expansion at 1-2 new factor categories). Estimated scope: API spend
   register at ~$20-40 per batch; small-arc commitment (~1-2 weeks)
   if just expanded theme rotation; medium-arc if factor library
   expansion (~3-4 weeks).

---

## §4 Selection adjudication and arc designation

### §4.1 Dominant uncertainty finding

Per §3 per-path evaluation: the dominant uncertainty class at this
scoping cycle is **signal-vs-artifact existence at observed candidates**.
This is path (b)'s domain.

Supporting reasoning at register-precision:

- Case C at PHASE2C_9 closeout determined that observed candidates
  may represent real signal OR may represent selection artifacts; the
  light-touch retrospective register cannot disambiguate.
- The downstream-of-existence questions (mechanism / calibration /
  coverage) are diagnostic / robustness / coverage register-classes
  respectively. Existence is the *upstream* register that the others
  depend on.
- Without resolving existence, no defensible commitment to mechanism
  refinement (path a), calibration robustness (path c), or coverage
  expansion (path g). Existence is the load-bearing decision-blocker.

### §4.2 Selected path

**Selection: path (b) — statistical-significance machinery (Q-9.A
register).**

The successor arc implements DSR (deflated Sharpe ratio) machinery
as MVD; expansion to PBO (probability of backtest overfitting)
considered at sub-spec drafting cycle if scope permits. CPCV
(combinatorial purged cross-validation) explicitly out of MVD scope;
deferred to post-PHASE2C_11 successor cycle if PBO results warrant.

**Pre-registration discipline at sub-spec drafting cycle (anti-p-hacking
guardrail):** the sub-spec must define the candidate population, trial
count, return metric, Sharpe estimation method, and null/deflation
assumptions before any result is computed. Pre-registration locks at
sub-spec drafting cycle; post-results parameter adjustment is forbidden
at register-precision register.

### §4.3 Rejected alternatives

Per §3 per-path evaluation against §1.3 decision goal:

- **Path (a) rejected at this cycle.** Mechanism question is real but
  downstream of existence in adjudication ordering. PHASE2C_9 §3
  light-touch reconstruction surfaced Case C without surfacing major
  mechanism defects at light-touch register; whether deeper mechanism
  reconstruction would surface defects is genuinely unresolved at this
  scoping cycle (per §3.1 bounded-strength framing). Path (a) selection
  would be defensible if mechanism question were judged dominant over
  existence question; at this scoping cycle, the dominant uncertainty
  class identified at §4.1 is existence at observed candidates, not
  mechanism. Defer to post-PHASE2C_11 scoping cycle if path (b) results
  warrant deeper mechanism investigation OR if path (b) results suggest
  mechanism artifacts as load-bearing explanation for path (b) outcomes.

- **Path (c) rejected at this cycle.** Calibration brittleness is
  secondary to existence. If signal doesn't exist (path b resolves
  toward artifact), calibration is moot. If signal exists, calibration
  robustness is real but downstream concern. Defer to post-PHASE2C_11
  scoping cycle.

- **Path (g) rejected at this cycle.** Breadth expansion at coverage
  register doesn't address dominant uncertainty class (existence at
  observed candidates). Adding candidates without resolving existing
  candidate ambiguity defers signal-vs-artifact disambiguation to
  downstream cycle while expanding candidate population. Defer to
  post-PHASE2C_11 scoping cycle.

- **Path (f) rejected at this cycle.** Phase 3 progression requires
  current uncertainty be non-blocking; Case C at PHASE2C_9 + path (b)
  unresolved at this scoping cycle entry means existence remains
  blocking. Path (f) is not authorizable until existence resolves
  (either toward signal-real via path b OR toward artifact, in which
  case Phase 3 trajectory is foreclosed for the current survivor set
  unless a later cycle identifies a different validated candidate basis).

### §4.4 Arc designation

Per anti-pre-naming option (ii): arc designation assigned at this
selection-adjudication seal. Filename `PHASE2C_11_SCOPING_DECISION.md`
selected sequential numbering at scoping doc draft fire; arc designation
that this scoping decision selects:

**PHASE2C_11 = statistical-significance machinery arc (Q-9.A register;
DSR machinery as MVD; PBO at sub-spec drafting cycle if scope permits;
CPCV deferred to post-PHASE2C_11).**

Arc designation committed at scoping decision seal, NOT before. Doc
body above (§§0-§3) and §1 locked inputs preserve "the selected arc" /
"the successor arc" framing per anti-pre-naming discipline; only at
§4.4 (this section, post-§4.1-§4.3 evaluation seal) does the arc
designation commit.

### §4.5 Adjudication transparency note

ChatGPT's lean toward path (b) at PHASE2C_10 session close is registered
as scoping-cycle input not selection. Per anti-momentum-binding
discipline: §3 per-path evaluation against locked decision goal +
constraints produced path (b) as the path attacking the dominant
uncertainty class (existence at observed candidates) *independently of
reviewer lean*. The lean is consistent with selection at this scoping
cycle; the selection is grounded in §3 substantive evaluation.

Counter-evaluation operational at §3: paths (a)/(c)/(g) each evaluated
at register satisfaction with explicit "why outrank others" + "what
remains unresolved" analysis. Selection emerges from comparison register
across paths; not lean-anchored authoring.

---

## §5 Scoping-cycle guardrails

Per ChatGPT scoping-doc skeleton + Charlie's locked guardrails at this
scoping cycle:

1. **Do not convert interesting results into deployment confidence.** Path (b) MVD's outcome is *binary at register-class*: either signal is statistically distinguishable from null, or it is not. "Almost significant" or "borderline interesting" is NOT deployment-warrant; explicit thresholding at sub-spec drafting cycle.

2. **Do not let path (b) win by default just because it sounds rigorous.** At §3 per-path evaluation, (b) was evaluated against rejection criteria explicitly; rejection of (a)/(c)/(g) grounded in dominant-uncertainty-class reasoning, not (b)'s superficial rigor. Sub-spec drafting cycle preserves this discipline at MVD register-precision.

3. **Do not let path (g) become "more mining because more data feels safer."** Coverage expansion without existence resolution defers decision; recognized at §3.4 + §4.3 explicitly.

4. **Do not authorize Phase 3 unless current ambiguity is explicitly accepted.** Phase 3 trajectory held at §1.4 constraint 1 + §4.3 path (f) rejection. Selection of (f) requires explicit adjudication of current uncertainty acceptability; not implicit progression.

5. **§3 per-path evaluation register-precision over reviewer-lean inheritance.** Per anti-momentum-binding discipline; observed at §4.5 transparency note.

---

## §6 Carry-forward to sub-spec drafting cycle

### §6.1 Scope register

PHASE2C_11 sub-spec drafting cycle (next operational deliverable
post-this-scoping-doc-seal) operates against:

- **MVD register:** DSR machinery implementation at scope sufficient for
  PHASE2C_8.1 candidate set (n=198). Specific DSR formulation
  (Bailey-López de Prado canonical; alternative formulations) adjudicated
  at sub-spec drafting cycle.
- **Stretch register:** PBO machinery if MVD scope permits.
- **Out-of-MVD scope:** CPCV; deferred to post-PHASE2C_11 if PBO results warrant.

### §6.2 Pre-registered framing decisions for sub-spec drafting cycle

- **Statistical thresholds pre-registered at sub-spec drafting cycle, NOT post-results.** Per guardrail 1 + anti-p-hacking discipline; null distribution + significance thresholds locked before observing results.
- **Multiple-testing correction explicit:** DSR's deflation factor accounts for selection bias at multiple-testing register; sub-spec drafting cycle locks deflation parameters (number of trials, in-sample optimization variance) at register satisfaction.
- **Candidate set scope:** PHASE2C_8.1 n=198 is canonical input; whether additional candidate sets (e.g., audit-only partition treatments) get separate DSR treatment adjudicated at sub-spec drafting cycle.

### §6.3 Methodology candidate carry-forward register

PHASE2C_10 closeout deferred items at sign-off MD §8 register carry
forward to PHASE2C_11 cycle:

1. §16 substantive Trigger context update — 10 candidate instances cumulative across §17+§18+§19+§3.5/§3.6+closeout sign-off cycles (#6-#15) requires register-class characterization at successor cycle scoping consideration
2. Activity K — CLAUDE.md project-discipline notes staleness fix (§1-§7 → §1-§19) — tracked at §16 ### Failure-mode signal §3.5 fold-in; either successor cycle scoping consideration OR separate one-line CLAUDE.md project-discipline notes refresh outside PHASE2C_11's implementation register

These carry forward as deferred items; not in PHASE2C_11 implementation
scope unless explicitly folded in at sub-spec drafting cycle.

---

## §7 Verification chain and dual-reviewer disposition

### §7.1 Verification anchor chain

- PHASE2C_10 sealed: `4c7d9d2` on origin/main; tag `phase2c-10-methodology-consolidation-v1`
- PHASE2C_10 scoping decision §2 path register: deliberation surface enumeration source for §2 paths (a)/(b)/(c)/(f)/(g)
- PHASE2C_9 §8.2 forward-pointer register: original sub-path enumeration for paths (a)/(b)/(c) at PHASE2C_9 closeout
- PHASE2C_9 §8.4 methodology-codification candidates: register source for §6.3 deferred items carry-forward
- METHODOLOGY_NOTES.md current state: §1-§19 (verified at PHASE2C_10 closeout); §16 ### Failure-mode signal extended at §3.5/§3.6 fold-ins
- ChatGPT scoping-doc skeleton offered at PHASE2C_10 session close; advisor lean-A converged on accepting at session entry

### §7.2 Dual-reviewer disposition

Anchor-prose-access discipline (METHODOLOGY_NOTES §16) fires at this
scoping doc's seal register; dual-reviewer pass:

- ChatGPT first-pass at substantive register (prose excerpts surfaced)
- Claude advisor substantive prose-access pass (full prose access; not summary)
- Codex routing: skipped per scoping-doc register (lighter-touch on scoping-cycle deliverables per PHASE2C_10 §3.5/§3.6 cycle precedent; Codex fires on substantive code/work only per feedback-codex-review-scope memory)
- Both reviewers authorize commit; patches surfaced applied; THEN seal

Status at this draft register: pre-seal; dual-reviewer pass next operational step.

### §7.3 Pre-fire audit pattern observation

Pre-fire-audit-pattern at session-close-of-prior-session (METHODOLOGY_NOTES
§16 ### Failure-mode signal §3.5 fold-in) does NOT apply at this scoping
cycle's fire register. The pattern operates at session-close →
next-session-fire boundary; this scoping cycle's draft fired in-session
post-PHASE2C_11-entry-trigger. Observation-only register; not
operationalized this cycle.

---

## §8 Cross-references

### §8.1 PHASE2C_10 cross-references

- [PHASE2C_10_SCOPING_DECISION.md](PHASE2C_10_SCOPING_DECISION.md) — §2 path register source (paths a-g enumerated); structural reference for this scoping doc's §2 + §4 organization
- [PHASE2C_10_PLAN.md](PHASE2C_10_PLAN.md) — PHASE2C_10 sub-spec; precedent for sub-spec drafting cycle structure at PHASE2C_11 implementation
- [docs/closeout/PHASE2C_10_METHODOLOGY_CONSOLIDATION_SIGNOFF.md](../closeout/PHASE2C_10_METHODOLOGY_CONSOLIDATION_SIGNOFF.md) — PHASE2C_10 closeout sign-off; deferred items source for §6.3

### §8.2 PHASE2C_9 cross-references

- [docs/closeout/PHASE2C_9_RESULTS.md](../closeout/PHASE2C_9_RESULTS.md) — PHASE2C_9 closeout final; §8.0-§8.4 source for current empirical state at §1.2 + Case C sub-register evidence + Q-9.A register source for path (b) MVD framing

### §8.3 METHODOLOGY_NOTES cross-references

- [docs/discipline/METHODOLOGY_NOTES.md](../discipline/METHODOLOGY_NOTES.md) — §1-§19 current state; §16 anchor-prose-access discipline source; §17 procedural-confirmation defect class source; §16 ### Failure-mode signal §3.5/§3.6 fold-ins source for engagement-mode + pre-fire audit pattern observations at this scoping cycle

### §8.4 CLAUDE.md cross-references

- CLAUDE.md Phase Marker — current state at PHASE2C_10 SEALED post-Step-2-closeout-cycle; Phase Marker reconciliation update fires at PHASE2C_11 implementation arc per discipline rule "Phase Marker must be updated in same arc that ships any phase/stage sign-off, major closeout, or live batch fire"

---

**End of working draft.** Anchor-prose-access discipline dual-reviewer pass at this scoping-cycle seal register next operational step.
