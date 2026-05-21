# R5_2_PHASE_B_SELECTION_INFLATION_HANDLING_NOTE.md

**Canonical artifact for Phase B Pre-Sequence Roadmap V3 register-event R5.2 (Tier 5 substantive cycle; structural analog to R2.1, R2.3, R3.1d, R4.1, R5.1 SEAL cycles per Bucket-1 Template B).**

**Status:** **V_SEAL SEALED at register-event boundary 2026-05-21 per Charlie register #13 "fire V_SEAL register".** V1 DRAFT authored post Charlie register #9 sub-decision lock; V1 reviewer round (Task 7) returned CONVERGENT BLOCK-LOCK (Codex 6 + Advisor 8 = 14 unique findings; 11 ADOPTed v1→V2 patches P40-P50). V2 DRAFT authored post Charlie register #10; V2 PFR returned CONVERGENT BLOCK-LOCK (Codex 1 BL + Advisor 2 HIGH + 3 MED + 3 LOW = 8 findings; root cause = patch-incomplete-landing pattern at V1→V2 transition; 4 ADOPTed V2→V3 patches P51-P54 + 4 DEFER). V3 DRAFT authored post Charlie register #11; V3 PFR returned CONVERGENT outcome (Codex 1 MED + Advisor BLOCK-LOCK 1 BL + 1 LOW; R5.2-G third-instance patch-incomplete-landing at §8.2); 2 V3-internal fixes applied. V3-confirmation PFR (per Charlie register #12) returned CONVERGENT APPROVE-V_FOR_V_SEAL on both legs with 0 findings. V_SEAL fire register #13 fired 2026-05-21; SEAL bundle commit per Option 1A 17th empirical trigger.

---

## §0 Cycle Metadata

**Cycle type:** Tier 5 substantive cycle per R3.1d sequencing 1→3→4 (R3.1d ✓ → Tier 2 SEAL ✓ → R5.1 ✓ → R5.2 → R6.1). R5.2 = Phase B Selection-Inflation Handling. Structural analog to R2.1, R2.3, R3.1d, R4.1, R5.1 (Bucket-1 Template B substantive cycle).

**Cycle boundary:** R5.2 register-event from R5.1 V_SEAL (commits `eec9b1c` + `536e5bd` 2026-05-20). Cycle entry authorized by Charlie at register 2026-05-20 ("authorized on the Critical-path priority" + clarification "A" = R5.2-only).

**Charlie register chain (R5.2 cycle entry through Task 4 sub-decision lock fire):**

| # | Date | Charlie register text | Decision class |
|---|---|---|---|
| 1 | 2026-05-20 | "authorized on the Critical-path priority" + "A" | Cycle entry register (R5.2-only confirmation; R6.1 remains gated eligible-not-named) |
| 2 | 2026-05-20 | "ratify plan, fire Task 1" | Cycle plan ratify + Round-1 sub-decision menu drafting fire |
| 3 | 2026-05-20 | "Authorize Task 2 reviewer dispatch on this v1 menu" | Task 2 reviewer dispatch authorization (v1 menu → Round-1 reviewer round) |
| 4 | 2026-05-20 | "Authorize all 17 ADOPTs + draft v2 menu + fire PFR-Round-1 on v2" | 17 v1→v2 patches + v2 draft + PFR-Round-1 fire |
| 5 | 2026-05-20 | "Authorize all 10 patches P18-P27 with reviewer-recommended path for each substantive decision (P22 remove Bonferroni + P25 remove SD-A-γ + P26 remove SD-B-δ) + fire PFR-Round-2 on v3" | 10 v2→v3 patches + v3 draft + PFR-Round-2 fire + 3 substantive removals authorized |
| 6 | 2026-05-20 | "Authorize v4 patches + fire PFR-Round-3 on v4" | 8 v3→v4 patches + v4 draft + PFR-Round-3 fire |
| 7 | 2026-05-20 | "Apply 3 mechanical v5 patches (P37+P38+P39) inline + skip PFR-Round-4 + proceed to Task 4 Charlie sub-decision lock" | 3 v4→v5 mechanical patches + v5 draft + skip PFR-Round-4 + Task 4 sub-decision lock proceed |
| 8 | 2026-05-20 | "i am thinking SD-A-β + SD-B-α + SD-C-γ + SD-D-α, but shot a blind lean to reviewers first to see what they think" | Blind-lean Phase 1 reviewer round dispatch + Charlie initial lean disclosure to orchestrator (NOT to reviewers per BL-Y-refined Phase 1 discipline) |
| 9 | 2026-05-20 | "Switch to reviewers' converged lean SD-A-α + SD-B-α + SD-C-β + SD-D-α" | Sub-decision lock register fire (Task 4): SD-A-α + SD-B-α + SD-C-β + SD-D-α |

R5.2 V_SEAL register-event will fire at separate Charlie register following V1 reviewer round (Task 7) + adjudication + any conditional V2/V3 + PFR-rule-Y rounds + V_SEAL closure section finalization. NOT pre-named here per anti-pre-emption.

**Locked sub-decision summary (per Charlie register #9):**

| Sub-decision | Locked option | Substantive scope |
|---|---|---|
| **SD-A** | **α (DSR-family)** | R5.2 framework family lock = Deflated Sharpe Ratio per Bailey-López de Prado 2014 + Sharpe-haircut family. R6.1 instrument variant choice space within DSR-family (illustrative subset; NOT exhaustive): production-grade BLdP closed-form analytical (incorporates skew/kurt correction per BLdP 2014 "non-normality" framework), Monte Carlo refinement, block-bootstrap variants for serial-correlation variance estimation. R6.1 V_SEAL locks specific variant + threshold + N value based on cohort properties at fire time per R3.1d V_SEAL SD9 + CLAUDE.md HARD CONSTRAINT line 273. |
| **SD-B** | **α (Single-α flat)** | R5.2 α allocation framework = equal per-candidate budget across R5.2 scope cohort. R5.1 SD-C-α theme-axis stratification carry-forward documented as cohort metadata (descriptive layer) but NOT operationalized as stratified α allocation at R5.2. R6.1 retains full freedom to allocate α heterogeneously at instrument-variant lock layer per cohort properties at R6.1 fire time. |
| **SD-C** | **β (Minimal-handoff + waiver branch)** | R5.2 → R6.1 handoff = framework family lock + α allocation framework + cohort identifiers + R5.1 carry-forward classification metadata. NO per-candidate adjusted statistics computed at R5.2. R6.1 computes per-candidate statistics + selection-inflation severity + instrument variant + threshold + N value at R6.1 V_SEAL. §34 conditional binding NOT triggered. |
| **SD-D** | **α (All-18 V_SEAL-locked cohort scope)** | R5.2 SCOPE = all 18 V_SEAL-locked candidates per R5.1 V_SEAL §2.1 (39 cohort_a − 2 R2.1-EXCLUDED − 19 Monday-pattern at Path B). R6.1 receives scoped cohort metadata + independently determines statistical N / effective-N under its locked instrument at R6.1 V_SEAL. NO N value pre-binding at R5.2 layer. |

**Reviewer routing routine (this cycle):**

- 2-leg subagent default per B2 standing rule LOCKED 2026-05-19 (cross-model leg structurally LOAD-BEARING for SEAL-class artifacts; 12-cycle precedent confirmed)
- **4 reviewer rounds total + 1 blind-lean Phase 1 round** across cycle deliberation:
  - **Round-1** (Task 2 v1 reviewer round on menu v1): Codex BLOCK-LOCK (4 BL + 2 HIGH + 2 MED + 1 LOW = 9 findings) + Advisor APPROVE-WITH-FINDINGS (4 MED + 4 LOW = 8 findings) — DIVERGENT verdict adjudicated as BLOCK-LOCK; 17 ADOPTed v1→v2 patches
  - **PFR-Round-1** (on v2 menu): Codex BLOCK-LOCK (3 BL + 1 HIGH + 1 MED = 5 findings) + Advisor BLOCK-LOCK (1 BL + 2 HIGH + 3 MED + 2 LOW = 8 findings) — CONVERGENT BLOCK-LOCK; 10 ADOPTed v2→v3 patches; Advisor first MULTI-INSTANCE own-finding-anchoring revision cluster (3 simultaneous revisions: A-3 REVISED + A-4 implementation-revised + A-8 calibrated)
  - **PFR-Round-2** (on v3 menu): Codex APPROVE-WITH-FINDINGS (0 BL + 2 MED + 3 LOW = 5 findings) + Advisor APPROVE-WITH-FINDINGS (0 BL + 1 HIGH + 1 MED + 4 LOW + 4 N/A = 10 items) — CONVERGENT APPROVE-WITH-FINDINGS; monotonic BLOCKING decline achieved (4 → 4 → 0); 8 ADOPTed v3→v4 patches; Advisor first F7 P27 RESOLUTION revision (overcorrection-cascade catch)
  - **PFR-Round-3** (on v4 menu): Codex APPROVE-WITH-FINDINGS (1 LOW) + Advisor APPROVE-V_FOR_CHARLIE_LOCK (7 LOW) — CONVERGENT lock-ready; 3 ADOPTed v4→v5 mechanical patches; Advisor first FULLY-CLEAN bi-directional cycle (0 revisions on all 4 F1-F8 patch reviews)
  - **Blind-lean Phase 1 round** (BL-Y-refined; at Task 4 sub-decision lock decision class): Codex independent lean SD-A-α + SD-B-α + SD-C-β + SD-D-α; Advisor independent lean SD-A-α + SD-B-α + SD-C-β + SD-D DEFER (or α if forced) — CONVERGENT on SD-A + SD-B + SD-C; partial divergence on SD-D (Codex add α / Advisor DEFER, both compatible with α-if-added). Charlie initial lean SD-A-β + SD-B-α + SD-C-γ + SD-D-α; per Phase 3 disclosed without orchestrator-lean injection; Charlie register #9 switched to reviewers' converged lean.

- **Cumulative reviewer reliability across R5.2 cycle (through V1 reviewer round; V2 PFR round in-flight at V2 patch application):**
  - Codex 0/6 verified hallucinations per leg within cycle across 4 menu-stage reviewer rounds (Round-1 + PFR-Round-1/2/3) + 1 blind-lean Phase 1 round + 1 V1 reviewer round = 6 Codex dispatches per leg (12 total dual-leg dispatches across rounds; lifetime ~1/52 ≈ 1.9%)
  - Advisor opus 0/6 verified hallucinations per leg within cycle = 6 Advisor dispatches per leg; cumulative through R5.2 cycle close (estimated 48+ dispatches under post-/agents-fix opus regime; 0 verified hallucinations — Mode A re-evaluation outcome (a) further empirically validated at extended N)

- **3-layer safety architecture** all 3 layers operational across all 5 rounds:
  - **Layer 1 (Advisor self-discount):** empirically validated at PFR-Round-1 3 simultaneous bi-directional revisions + PFR-Round-2 RESOLUTION revision + PFR-Round-3 FULLY-CLEAN bi-directional cycle (sample-size N=4 cycle touch-points)
  - **Layer 2 (Codex cross-model adversarial leg):** empirically validated at Round-1 BLOCKING catches (Codex flagged 4 BLOCKING Advisor missed) + PFR-Round-1 + PFR-Round-2 + PFR-Round-3 convergent findings
  - **Layer 3 (Orchestrator independent verification):** empirically validated across all rounds; 0/65+ adopted findings hallucinated under independent grep/Read verification

**§0 scope-bleed trip-wire status:** clean. Cycle work bounded to R5.2 sub-decision menu + 4 SD locks (SD-A through SD-D) + canonical artifact authorship + V1 reviewer round (Task 7) + any conditional V2/V3 patches + PFR-rule-Y rounds + V_SEAL fire register text. No analytical computation. No engine runs. No API spend. R6.1 instrument variant + threshold + N value + multiplicity correction specifics + Bonferroni eligibility + R2.2 / P2a / supplementary IS-OOS cycle specifics / Phase 4 paper-trading deployment infrastructure / mechanism investigation for FLIP-TRIGGERED candidates / memory codification of R5.2 empirical contributions all remain eligible-not-named per anti-pre-emption invariant.

---

## §1 Sub-Decision Register Chain (Detailed)

### §1.1 SD-A: Selection-Inflation Correction Methodology Framework Family

**Locked option:** SD-A-α (DSR-family) per Charlie register 2026-05-20 (#9).

**Scope:** R5.2 framework family lock = Deflated Sharpe Ratio per Bailey-López de Prado 2014 framework. Each candidate's observed holdout Sharpe is deflated via a Sharpe-specific bias-correction that accounts for the maximum-over-N candidates structure (Sharpe-haircut family). R6.1 instrument variant lock at R6.1 V_SEAL.

**Framework Citation:** Bailey & López de Prado (2014) "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality" — preferred eligible instrument per CLAUDE.md HARD CONSTRAINT line 268.

**Framework correctness assumptions:** approximate normality of returns (or higher-moment correction for skew + kurtosis); effective number of independent trials N* accounts for serial correlation; haircut deflation accounts for max-over-N candidates selection bias.

**R6.1 instrument variant choice space within DSR-family (illustrative subset; NOT exhaustive):**
- **Production-grade BLdP 2014 closed-form analytical:** incorporates skew + kurtosis correction per BLdP paper's "Correcting for ... Non-Normality" framework; analytical formula in terms of variance of estimated Sharpe + higher moments + effective N*
- **Monte Carlo refinement:** simulation-based DSR estimation; better small-N coverage
- **Block-bootstrap / stationary-bootstrap variants:** for variance-of-Sharpe estimation under serial correlation in hourly BTC returns

R6.1 V_SEAL retains authority over specific variant choice + formulation mapping per CLAUDE.md HARD CONSTRAINT line 273; this enumeration is illustrative-subset disclosure, NOT pre-binding of R6.1 instrument-variant choice space. Heuristic DSR `sqrt(2*ln(N))` acceptable INTERIM screen only per HARD CONSTRAINT line 268 (supersession to production-grade required before final capital commitment).

**Anti-pre-emption preservation:** R5.2 framework family lock only; instrument variant + per-candidate threshold + sample-size N value all locked at R6.1 V_SEAL per CLAUDE.md HARD CONSTRAINT line 273 + R3.1d V_SEAL SD9 (line 478 + line 555).

**Rationale for SD-A-α lock (per Charlie register #9 + reviewers' converged blind-lean reasoning):**

1. **Methodology fit for max-over-N Sharpe selection bias:** DSR is purpose-built for the R5.2 problem (correcting selection bias on observed Sharpe statistics when candidates are selected from a larger universe). Direct semantic match — cohort_a 39 → 18 V_SEAL-lock is a max-over-N selection event over Sharpe statistics.

2. **HARD CONSTRAINT preferred status:** CLAUDE.md line 268 explicitly names DSR as "(preferred)" in eligible instruments list — R5.2 lock aligns with project HARD CONSTRAINT preference signal.

3. **Small-N (N=18) favors analytical over resampling-based instruments:** Romano-Wolf bootstrap power-deficient at small N + dependence; Westfall-Young permutation requires subset pivotality with block-bootstrap variants under serial correlation in hourly BTC returns. DSR analytical closed-form sidesteps small-N resampling power constraints.

4. **Cohort dependence structure favors analytical DSR:** calendar_effect candidates share trading-window factor; momentum candidates share trend factors; volume_divergence candidates share volume-spike factors. Positive correlation within stratum reduces effective independent trials. DSR handles this via N* effective independent trials adjustment; FWER-resampling instruments require bootstrap-based joint null estimation that is power-deficient at N=18 + dependence.

5. **Cross-cycle precedent:** R3.1d V_SEAL SD9 V3.5-PE explicitly names DSR as "preferred" in eligible-instruments list; R5.2 lock aligns with the preference signal at sealed cross-cycle anchor.

### §1.2 SD-B: Family-Wise α Allocation Framework

**Locked option:** SD-B-α (Single-α flat) per Charlie register 2026-05-20 (#9).

**Scope:** Total α budget distributed equally across all candidates in R5.2 scope cohort. Per-candidate α = α_total / N where N = R5.2 scope cohort cardinality. Specific α_total value + split mechanism locked at R6.1 V_SEAL per R3.1d V_SEAL SD9 + CLAUDE.md HARD CONSTRAINT line 273.

**R5.1 SD-C-α theme-axis carry-forward treatment:** IGNORED at R5.2 SD-B layer. Theme-axis stratification per R5.1 SD-C-α (Stratum A=22 calendar_effect / Stratum B=15 non-calendar at framing-stage 37; Stratum A=3 / Stratum B=15 at V_SEAL-locked 18) is documented as cohort metadata (descriptive layer) but NOT operationalized as stratified α allocation at R5.2. R5.1 SD-C carry-forward propagates as cohort metadata for R6.1 input; R6.1 retains freedom to apply stratification at instrument-variant layer if desired.

**R6.1 weighted-α allocation eligibility preservation:** Per v5 §2 SD-B-δ REMOVED block P36 disclosure carry-forward: weighted-α allocation remains eligible as R6.1 instrument variant choice within SD-B-α (flat at R5.2; weighted at R6.1) framework. R5.2 SD-B-α lock is R5.2 menu scoping NOT foreclosure of weighted-allocation methodology at R6.1.

**R2.3 §8.2 caveat alignment:** ALIGNED. Single-α flat does not USE theme-axis as decision dimension; R2.3 §8.2 caveat (theme tags = prompt-rotation provenance labels per `agents/proposer/stage2c_batch.py:213` formula, NOT validated content-aware classifications) is moot under flat allocation framework.

**Rationale for SD-B-α lock (per Charlie register #9 + reviewers' converged blind-lean reasoning):**

1. **Stratum A n=3 makes per-stratum FWER statistically fragile:** at V_SEAL-locked 18, Stratum A = 3 non-Monday calendar_effect candidates (1 PASS + 2 FAIL at Phase 4 baseline 15bps preview). 3-candidate stratum cannot support a stratum-scoped FWER inference with meaningful power.

2. **R5.1 SD-C-α carry-forward does NOT mechanically demand SD-B stratification at R5.2:** R5.1 used theme-axis for descriptive cohort breakdown + framing-stage 22/15 distribution; that does not translate into a stratified α allocation framework at R5.2.

3. **R2.3 §8.2 caveat is a direct argument against using theme tags as methodologically load-bearing decision dimension at R5.2:** theme tags are provenance labels, not validated classifications.

4. **R6.1 weighted-α freedom preserved via P36 disclosure:** SD-B-α lock at R5.2 does NOT foreclose stratification or weighted-allocation at R6.1 instrument-variant layer.

5. **Conservative-default principle:** Single-α flat is the conservative default for a 4-axis lock at framework-cycle layer; stratification can be added at R6.1 if cohort survival + properties at R6.1 fire time warrant.

### §1.3 SD-C: R5.2 → R6.1 Handoff Interface

**Locked option:** SD-C-β (Minimal-handoff + waiver branch) per Charlie register 2026-05-20 (#9).

**Scope:** R5.2 V_SEAL artifact contents = SD-A framework family lock (DSR-family) + SD-B α allocation framework lock (Single-α flat) + cohort identifiers (18 V_SEAL-locked candidates) + R5.1 carry-forward classification metadata (INDETERMINATE-DSL-UNAVAILABLE per R5.1 SD-B-α + R2.1 INDETERMINATE-overall flags for 2 of 18). NO per-candidate adjusted statistics computed at R5.2.

**Waiver branch (SD-A-δ not applicable at this lock):** under current SD-A-α lock, standard branch applies (framework family + α framework + cohort + metadata). Waiver branch text in §3 SD-C-β v5 menu remains documented for cross-cycle reference but is unused at R5.2 V_SEAL.

**R6.1 inheritance:** R6.1 receives framework lock (DSR-family) + α framework (Single-α flat) + cohort metadata (18 cohort identifiers + carry-forward classifications). R6.1 computes per-candidate adjusted statistics (DSR statistics under chosen DSR variant) + selection-inflation severity estimate + chooses instrument variant + threshold + N value at R6.1 V_SEAL.

**Anti-pre-emption preservation:** MAXIMUM. R6.1 instrument variant choice space within DSR-family is fully preserved (R5.2 does not compute DSR statistics that would constrain R6.1 variant choice). R6.1 instrument variant + threshold + N lock per R3.1d V_SEAL SD9 + CLAUDE.md HARD CONSTRAINT line 273.

**§34 conditional binding:** NOT triggered under SD-C-β. Data accessibility verification for holdout return series + variance/skew/kurt computation deferred to R6.1 V_SEAL pre-commit checklist. R5.2 V_SEAL lock fires without §34 binding (consistent with §6 application table at v5 §6 row "Methodology framework family lock: framework lock has no data requirement").

**Rationale for SD-C-β lock (per Charlie register #9 + reviewers' converged blind-lean reasoning):**

1. **Max R6.1 freedom:** R5.2 = methodology + framework cycle; R6.1 = computation + instrument variant cycle. Cleanest separation of concerns per R3.1d V_SEAL SD9 staging discipline.

2. **No §34 conditional binding triggered:** data accessibility verification deferred to R6.1 V_SEAL pre-commit; R5.2 V_SEAL lock not delayed by data accessibility verification requirements.

3. **Avoids inadvertent R6.1 instrument variant constraint:** SD-C-α (full-handoff) requires R5.2 to compute statistics under specific DSR variant choice, which constrains R6.1 variant choice space within DSR-family. SD-C-γ (parameterized-handoff) carries parameter functions that may inadvertently bind specific instrument formulation.

4. **0/5 raw_payloads accessible per PHASE2C_15 (INDETERMINATE-DSL-UNAVAILABLE classification carry-forward):** under SD-C-α, R5.2 §34 binding would require holdout return time-series accessibility verification; under SD-C-β this is deferred to R6.1.

### §1.4 SD-D: Source-Cohort Scope (candidate ratified)

**Locked option:** SD-D-α (All-18 V_SEAL-locked cohort scope) per Charlie register 2026-05-20 (#9).

**Scope:** R5.2 methodology framework (DSR-family per SD-A-α) + α allocation framework (Single-α flat per SD-B-α) applies to all 18 V_SEAL-locked candidates per R5.1 V_SEAL §2.1 enumeration (39 cohort_a − 2 R2.1-EXCLUDED dim (c) FLIP-TRIGGERED at framing − 19 Monday-pattern at V_SEAL boundary via Path B = 18). NO downstream conditioning on Tier 5 conservative-anchor gate evaluation outcome at R5.2 V_SEAL.

**R6.1 inheritance:** R6.1 receives the scoped cohort metadata (18 cohort identifiers + carry-forward classifications) as input. R6.1 INDEPENDENTLY determines statistical N / effective-N under its locked DSR variant at R6.1 V_SEAL. R5.2 does NOT pre-specify any N value or effective-N adjustment per P20 v3 fix + CLAUDE.md HARD CONSTRAINT line 273.

**Rationale for SD-D-α lock (per Charlie register #9):**

1. **Consistent with R5.1 V_SEAL committal:** cohort N=18 is the R5.1 V_SEAL-locked cohort; R5.2 methodology applies uniformly to this committed cohort.

2. **Avoids timing complication of SD-D-β (survivors-only):** SD-D-β would require Tier 5 conservative-anchor gate evaluation to fire BEFORE R5.2 V_SEAL or defer R5.2 cohort scope to downstream gate evaluation. SD-D-α keeps R5.2 V_SEAL lock independent of downstream gate timing.

3. **Avoids R5.2 substantive cost increase of SD-D-γ (parallel scopes):** R5.2 V_SEAL artifact carries one methodology application (to all 18) not two.

4. **R6.1 freedom on N value preserved:** R5.2 specifies SCOPE (18 candidates) not N value; R6.1 independently determines the statistical N, effective-N, and any R6.1-layer cohort scoping based on cohort properties at R6.1 fire time per CLAUDE.md HARD CONSTRAINT line 273 + R3.1d V_SEAL SD9.

### §1.5 Cross-SD Lock Coherence

| Pair | Compatibility (per v5 §4 matrix) | Verdict |
|---|---|---|
| SD-A-α × SD-C-β | ✓ fully compatible (matrix row 1: "α / β / γ compatible") | OK |
| SD-A × SD-B | ✓ independent (§4 last paragraph) | OK |
| SD-B × SD-C | ✓ independent (§4 last paragraph) | OK |
| SD-D-α × SD-A/B/C | ✓ scope choice; no compatibility constraint with framework + allocation + handoff dimensions | OK |

No cross-SD compatibility violations at the locked combination. §34 conditional binding NOT triggered (SD-C-β). HARD CONSTRAINT compliance verified (DSR is preferred eligible instrument per line 268; R6.1 instrument variant + threshold + N value lock per line 273 preserved).

---

## §2 R5.2 Methodology Framework Family Specification (SD-A-α DSR-family)

### §2.1 Framework Family Definition

R5.2 locks the **DSR-family** as the R5.2-layer selection-inflation correction methodology framework family. The framework family consists of Sharpe-haircut instruments that deflate observed Sharpe statistics to account for max-over-N candidates selection bias.

**R6.1 V_SEAL instrument variant choice space within DSR-family (illustrative subset; NOT exhaustive; per P46 v1→V2 ADOPT 2026-05-20 + P51 V2→V3 incomplete-landing fix):**

- **Production-grade BLdP 2014 closed-form analytical:** incorporates skew + kurtosis correction per BLdP paper's "Correcting for ... Non-Normality" framework natively (formula `PSR = Z((SR - SR*)√(T-1) / √(1 - γ₃·SR + (γ₄-1)/4·SR²))` with skew γ₃ + kurtosis γ₄ + effective independent trials N* + variance of estimated Sharpe). Cheap (millisecond per candidate).
- **Monte Carlo refinement:** simulation-based DSR estimation; better small-N coverage; higher compute cost.
- **Block-bootstrap / stationary-bootstrap variants:** for variance-of-Sharpe estimation under serial correlation in hourly BTC returns.

R6.1 V_SEAL retains authority over specific variant choice + formulation mapping per CLAUDE.md HARD CONSTRAINT line 273; this enumeration is illustrative-subset disclosure, NOT pre-binding of R6.1 instrument-variant choice space. Heuristic DSR `sqrt(2*ln(N))` acceptable INTERIM screen ONLY per HARD CONSTRAINT line 268 (supersession to production-grade required before final capital commitment).

### §2.2 Anti-Pre-Emption Preservation at SD-A-α Lock

R5.2 SD-A-α lock binds the **framework family** (DSR-family) but NOT the **specific instrument variant** + **threshold** + **N value**. Per CLAUDE.md HARD CONSTRAINT line 273 ("NEVER lock Tier 6 multiplicity instrument variant + threshold + N value at R3.1d V_SEAL"), R6.1 retains lock authority over:

- Specific DSR variant choice (illustrative subset per §2.1; R6.1 retains specific variant + formulation mapping authority per CLAUDE.md HARD CONSTRAINT line 273)
- Per-candidate effective threshold
- Sample-size N value (R6.1 independently determines statistical N + effective-N adjustment per cohort properties at R6.1 fire time)
- α budget value
- Dependence-structure handling within DSR variance estimation

### §2.3 Cross-Framework Eligibility-Not-Named Disclosures

Per anti-pre-emption discipline, the following remain eligible-not-named at separate Charlie register-event boundaries:

- **FWER-resampling-family instrument variants (Romano-Wolf stepdown, Westfall-Young permutation, etc.):** listed as eligible-instrument candidates per CLAUDE.md HARD CONSTRAINT line 268, but R5.2 SD-A-α framework family lock binds the R5.2 methodology family to DSR-family. **Inclusion of FWER-resampling-family instruments at R6.1 layer requires explicit separate Charlie register-event to reopen / broaden R5.2 SD-A framework family lock**; NOT eligible via implicit R6.1 instrument-variant choice while SD-A-α is locked at R5.2. R6.1 instrument-variant choice space within current SD-A-α lock is bounded to DSR-family variants (per §2.1). FWER-resampling-family eligibility at future cycle methodology framework re-evaluation register-event is preserved.

- **Bonferroni eligibility:** NOT eligible at R5.2 per Charlie register #5 P22 removal path 2026-05-20; eligible-not-named at separate Charlie register-event boundary per anti-pre-emption (per CLAUDE.md HARD CONSTRAINT line 268 + R3.1d V3.5-PE language).

- **Hybrid DSR + FWER-resampling framework:** REMOVED at v3 per P25 Charlie register-recommended path; restitution candidate noted (eligible for re-introduction at separate Charlie register-event if methodologically valid distinct-bias-source narrative emerges for 2-layer architecture per Advisor PFR-Round-2 F5 substantive caveat).

- **Cycle-scope waiver (SD-A-δ):** considered at v5 menu but not adopted at R5.2 V_SEAL; eligible-not-named for future cycles.

### §2.4 HARD CONSTRAINT Compliance Verification

CLAUDE.md HARD CONSTRAINT compliance verified:
- **Line 268** (eligible instruments): ✓ DSR is "(preferred)" in eligible instruments list
- **Line 269** (BH-FDR exclusion): ✓ R5.2 framework does NOT use BH-FDR (FDR-family explicitly excluded per architecture rationale)
- **Line 273** (R6.1 timing): ✓ R5.2 locks framework family ONLY; R6.1 V_SEAL retains lock authority over instrument variant + threshold + N value

### §2.5 R5.1 §1.5 Path 1+ Eligibility Preservation

Per R5.1 V_SEAL §1.5 Path 1+ explicit eligibility bullet, supplementary IS-OOS analytical cycle(s) per R1.2 §7 OBS 6 (Pearson on raw Sharpe; bootstrap IS-OOS rank correlation CI; window-shifted rank correlation) eligible at separate Charlie register-event boundary for any SD-A option (locked or future). SD-A-α lock at R5.2 does NOT foreclose supplementary IS-OOS analytical cycle eligibility.

---

## §3 R5.2 α Allocation Framework Specification (SD-B-α Single-α Flat)

### §3.1 Framework Definition

R5.2 locks **Single-α flat** as the R5.2-layer α budget allocation framework. Total α budget = α_total (specific value locked at R6.1 V_SEAL). Per-candidate α = α_total / N where N = R5.2 scope cohort cardinality.

Equal distribution across all candidates in R5.2 scope; no stratification at R5.2 layer.

### §3.2 R6.1 Allocation Implementation Freedom

Per v5 §2 SD-B-δ REMOVED block P36 disclosure carry-forward:

> Weighted-α allocation remains eligible as an R6.1 instrument variant choice within either SD-B-α (flat at R5.2; weighted at R6.1) or SD-B-β (per-stratum at R5.2; weighted within stratum at R6.1) framework. The SD-B-δ removal is **R5.2 menu scoping**, NOT foreclosure of weighted-allocation methodology at downstream R6.1 instrument-variant lock. R6.1 retains full freedom to allocate α heterogeneously per cohort properties at R6.1 fire time.

R6.1 instrument-variant lock space within SD-B-α framework includes:
- Strict flat per-candidate α = α_total / N (default at framework lock)
- Stratification at R6.1 layer (per-stratum split / per-theme split / hierarchical) if R6.1 instrument variant supports it
- Weighted-by-criticality with prior-determined criteria (DSL structural complexity / hash position / theme assignment per pre-PHASE2C_15 priors per v5 P36 disclosure)
- Other α allocation structures eligible-not-named at R6.1 V_SEAL

### §3.3 R5.1 SD-C-α Theme-Axis Carry-Forward Documentation

R5.1 SD-C-α theme-axis stratification is propagated as cohort metadata for R6.1 input (descriptive layer) but NOT operationalized as R5.2 α allocation:

**V_SEAL-18 cohort stratum + theme distribution (carry-forward from R5.1 V_SEAL §2.1 + Phase 4 baseline preview):**

| Stratum | Theme(s) | N at V_SEAL-18 | Phase 4 baseline 15bps strict positive |
|---|---|---|---|
| **Stratum A** | calendar_effect (non-Monday) | **3** | 1/3 (33%) |
| **Stratum B** | non-calendar | **15** | 6/15 (40%) |
| ↳ momentum | | 6 | 2/6 (33%) |
| ↳ volume_divergence | | 6 | 4/6 (67%) |
| ↳ mean_reversion | | 2 | 0/2 (0%) |
| ↳ volatility_regime | | 1 | 0/1 (0%) |
| **TOTAL** | | **18** | **7/18 (38.9%)** |

**Full 18-candidate cohort manifest (per P42 Codex V1 reviewer round C-#3 ADOPT 2026-05-20; SD-C-β minimal-handoff content per §4.1 item 4):**

| # | Hash | Name | Stratum | Theme | Phase 4 baseline 15bps Sharpe | Classification flags |
|---|---|---|---|---|---|---|
| 1 | `22864f01a49e3452` | weekend_volatility_compression_breakout | A (calendar_effect) | calendar_effect | +0.7185 (PASS) | INDETERMINATE-DSL-UNAVAILABLE |
| 2 | `2cc19d1b5e2c9024` | weekday_momentum_friday_fade | A (calendar_effect) | calendar_effect | −1.4237 (FAIL) | INDETERMINATE-DSL-UNAVAILABLE |
| 3 | `b10f4563366481b3` | friday_close_weekend_positioning | A (calendar_effect) | calendar_effect | −3.5093 (FAIL) | INDETERMINATE-DSL-UNAVAILABLE |
| 4 | `7240602b60cd7271` | triple_ema_momentum_surge | B (non-calendar) | momentum | −3.3000 (FAIL) | INDETERMINATE-DSL-UNAVAILABLE |
| 5 | `53e1b5030aefe836` | triple_ema_momentum_convergence | B (non-calendar) | momentum | −3.5383 (FAIL) | INDETERMINATE-DSL-UNAVAILABLE |
| 6 | `4a3c8e2fe04d72c1` | momentum_exhaustion_rsi_macd_reversal | B (non-calendar) | momentum | −0.0204 (FAIL) | INDETERMINATE-DSL-UNAVAILABLE |
| 7 | `8def2951c72f0961` | momentum_continuation_crossover_196 | B (non-calendar) | momentum | +0.0696 (PASS) | INDETERMINATE-DSL-UNAVAILABLE |
| 8 | `b24ca51d477c2e96` | macd_rsi_momentum_alignment | B (non-calendar) | momentum | −0.1788 (FAIL) | INDETERMINATE-DSL-UNAVAILABLE |
| 9 | `7abff29fc2f117a1` | ema_crossover_momentum_acceleration | B (non-calendar) | momentum | +3.0614 (PASS) | INDETERMINATE-DSL-UNAVAILABLE + R2.1 INDETERMINATE-overall |
| 10 | `aa8c55c16db41ea7` | volume_surge_momentum_confirmation | B (non-calendar) | volume_divergence | +0.0698 (PASS) | INDETERMINATE-DSL-UNAVAILABLE |
| 11 | `3ebec90d7be309ab` | volume_surge_low_momentum_divergence | B (non-calendar) | volume_divergence | +0.3519 (PASS) | INDETERMINATE-DSL-UNAVAILABLE |
| 12 | `2433a38b2f9a7211` | volume_surge_breakout_divergence | B (non-calendar) | volume_divergence | +1.1064 (PASS) | INDETERMINATE-DSL-UNAVAILABLE + R2.1 INDETERMINATE-overall |
| 13 | `cfd24b8b72d6e429` | volume_divergence_surge_entry | B (non-calendar) | volume_divergence | +0.1982 (PASS) | INDETERMINATE-DSL-UNAVAILABLE |
| 14 | `54ae22768a3f78e9` | volume_divergence_reversal | B (non-calendar) | volume_divergence | −1.7046 (FAIL) | INDETERMINATE-DSL-UNAVAILABLE |
| 15 | `5fcf29ab42c5f8b6` | volume_divergence_momentum_fade | B (non-calendar) | volume_divergence | −2.5399 (FAIL) | INDETERMINATE-DSL-UNAVAILABLE |
| 16 | `18d92ce5d0b40cc7` | bollinger_zscore_reversion | B (non-calendar) | mean_reversion | −1.4910 (FAIL) | INDETERMINATE-DSL-UNAVAILABLE |
| 17 | `9c90efe879157a5c` | bollinger_extreme_zscore_reversal | B (non-calendar) | mean_reversion | −2.7501 (FAIL) | INDETERMINATE-DSL-UNAVAILABLE |
| 18 | `dc7d6de5e71772ae` | low_volatility_breakout_198 | B (non-calendar) | volatility_regime | −1.1518 (FAIL) | INDETERMINATE-DSL-UNAVAILABLE |

**Verification:** Manifest independently grep/awk-verified against `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv` at V2 patch application time. 18 candidates total (3 Stratum A + 15 Stratum B); 7 PASS + 11 FAIL at Phase 4 baseline 15bps (preview only; Tier 5 re-run authoritative). All 18 carry INDETERMINATE-DSL-UNAVAILABLE per R5.1 SD-B-α. 2 of 18 carry additional R2.1 INDETERMINATE-overall (rows 9 + 12).

### §3.4 R2.3 §8.2 Caveat Propagation

Per R2.3 V_SEAL §8.2 caveat (carry-forward from R5.1 V_SEAL §1.3):

Theme tags in cohort_a are **PROMPT-ROTATION PROVENANCE LABELS** — assigned at BatchContext construction via formula `THEMES[(k-1) % THEME_CYCLE_LEN]` at `agents/proposer/stage2c_batch.py:213` BEFORE Proposer LLM call. They are **NOT validated content-aware classifications**.

Under SD-B-α Single-α flat allocation, this caveat does NOT bite the R5.2 layer (theme-axis not used as decision dimension). R6.1 instrument-variant choice using theme stratification would propagate the caveat for explicit disclosure.

### §3.5 Anti-Pre-Emption Preservation at SD-B-α Lock

R5.2 SD-B-α locks allocation framework structure (flat) only. Specific α_total value + R6.1-layer stratification (if any) + weighting (if any) + threshold all locked at R6.1 V_SEAL.

---

## §4 R5.2 → R6.1 Handoff Interface Specification (SD-C-β Minimal-handoff)

### §4.1 R5.2 V_SEAL Artifact Contents (Handoff to R6.1)

R5.2 V_SEAL artifact contents (per SD-C-β minimal-handoff lock):

1. **SD-A framework family lock:** DSR-family (per §2)
2. **SD-B α allocation framework lock:** Single-α flat (per §3)
3. **SD-D cohort scope lock:** All-18 V_SEAL-locked cohort (per §5)
4. **Cohort identifiers:** 18 hypothesis_hash + name + stratum + theme + classification flags per full 18-candidate manifest at §3.3
5. **R5.1 carry-forward classification metadata:**
   - Universal INDETERMINATE-DSL-UNAVAILABLE per R5.1 SD-B-α (all 18 candidates)
   - 2 of 18 additional R2.1 INDETERMINATE-overall flag (`7abff29fc2f117a1` ema_crossover_momentum_acceleration + `2433a38b2f9a7211` volume_surge_breakout_divergence)
6. **R5.1 §1.5 Path 1+ explicit eligibility bullet:** preserved at R5.2 V_SEAL
7. **R2.3 §8.2 theme-axis provenance caveat:** propagated for R6.1 disclosure
8. **Cross-SD compatibility matrix:** propagated per v5 §4
9. **§34 application status at R5.2 V_SEAL:** trivial pass (no per-candidate statistics computed at R5.2 under SD-C-β; §34 application is eligible-for at R6.1 instrument variant lock per R6.1 cycle authority; see §6 application table)

### §4.2 NO Per-Candidate Adjusted Statistics Computed at R5.2

Under SD-C-β minimal-handoff lock, R5.2 V_SEAL artifact does **NOT** compute:
- Per-candidate DSR statistics under any DSR variant
- Per-candidate selection-inflation severity estimates
- Per-candidate effective threshold values

These are R6.1 V_SEAL responsibility. R6.1 computes per-candidate adjusted statistics using its chosen DSR variant under the SD-A-α framework family lock.

### §4.3 R6.1 Inheritance + Lock Authority

R6.1 receives R5.2 V_SEAL artifact contents (per §4.1) as input. R6.1 V_SEAL locks:

- **Specific DSR instrument variant** (within DSR-family per §2.1): illustrative subset enumerated at §2.1 + heuristic interim screen; R6.1 retains specific variant + formulation mapping authority per HARD CONSTRAINT line 273
- **Per-candidate effective threshold** under chosen DSR variant
- **Sample-size N value** (R6.1 independently determines per cohort properties at R6.1 fire time; effective-N adjustment for serial correlation in variance estimation locked at R6.1 V_SEAL)
- **α_total value** (specific α budget; 0.05 / 0.01 / other per R6.1 cohort properties at fire time)
- **Dependence-structure handling** within DSR variance estimation (serial correlation adjustment, etc.)
- **R6.1 allocation implementation** (flat per §3.1 default OR R6.1-layer stratification/weighted-allocation OR other per §3.2 freedom)
- **Cohort scope at R6.1** (R6.1 independently determines any R6.1-layer sub-scoping; SD-D-α R5.2 scope is handoff metadata not pre-binding on R6.1 statistical cohort)

### §4.4 §34 Conditional Binding Status

§34 conditional binding **NOT triggered** at R5.2 V_SEAL under SD-C-β lock. Per v5 §6 §34 application table:

| Audit dimension | §34 verdict |
|---|---|
| Per-candidate adjusted statistics (would be triggered if SD-C-α) | **Not applicable** (SD-C-β does not compute statistics at R5.2) |

R5.2 V_SEAL fire proceeds without §34 conditional binding. §34 application at R6.1 layer is eligible-for at R6.1 V_SEAL pre-commit checklist (data accessibility verification for holdout return series + variance/skew/kurt computation under chosen DSR variant); R6.1 cycle authority determines §34 application structure at R6.1 V_SEAL.

### §4.5 Anti-Pre-Emption Preservation at SD-C-β Lock

R5.2 SD-C-β handoff contents are framework + framework + scope + metadata + carry-forward classifications. No per-candidate statistics constrain R6.1 instrument variant choice. R6.1 instrument variant + threshold + N value + α budget all locked at R6.1 V_SEAL per CLAUDE.md HARD CONSTRAINT line 273.

---

## §5 R5.2 Source-Cohort Scope Specification (SD-D-α All-18 V_SEAL-locked)

### §5.1 Scope Definition

R5.2 methodology framework (DSR-family per SD-A-α) + α allocation framework (Single-α flat per SD-B-α) applies to the V_SEAL-locked cohort of **18 candidates** per R5.1 V_SEAL §2.1 enumeration:

**Derivation chain (independently verified at PFR rounds against `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv`):**

| Step | Operation | Cohort N |
|---|---|---|
| 1 | Cohort_a (PHASE2C_15 AND-gate fire from batch_id `b6fcbf86-4d57-4d1f-ae41-1778296b1ae9` corrected-engine artifacts) | 39 |
| 2 | − 2 R2.1-EXCLUDED dim (c) FLIP-TRIGGERED at framing stage (per R2.1 V_SEAL `dac3c3c` SD-A A1 action menu): `38a1bb228f103c26` volatility_compression_breakout_ema_cross + `35dcfcfbee4cfafc` volume_divergence_momentum_174 | 37 (framing) |
| 3 | − 19 Monday-pattern candidates at V_SEAL boundary via Path B (R5.1 V_SEAL Charlie register #10 "Path B authorized") | **18 (V_SEAL-locked)** |

### §5.2 R6.1 N / Effective-N Independence

Per P20 v3 fix + CLAUDE.md HARD CONSTRAINT line 273, R5.2 V_SEAL SCOPE lock at all-18 does **NOT** pre-specify R6.1 N value or effective-N adjustment. R6.1 V_SEAL independently determines:

- **Statistical N:** R6.1 independently determines per cohort properties at R6.1 fire time. R5.2 SD-D-α specifies SCOPE (18 candidates as input) NOT N value. R6.1 may use cohort cardinality directly OR sub-scope to Tier 5 conservative-anchor gate survivors (Phase 4 baseline preview = 7/18; Tier 5 re-run authoritative) at instrument-variant layer per CLAUDE.md HARD CONSTRAINT line 273
- **Effective-N (N*) adjustment for serial correlation:** R6.1 instrument-variant locks N* under chosen DSR variant variance-estimation methodology
- **Cohort sub-scoping:** R6.1 may apply additional filtering at instrument-variant layer (e.g., DSR statistic threshold pre-filter)

### §5.3 Tier 5 Conservative-Anchor Gate Independence

R5.2 V_SEAL fires independently of Tier 5 conservative-anchor gate evaluation outcome. Tier 5 evaluation at `spot_realistic_15bps_v1` anchor (`config/execution_phaseb_spot_15bps.yaml`; 15 bps/side; 30 bps round trip per R3.1d V_SEAL SD9 + R4.1 SEAL formal Branch.A commitment) fires at separate Charlie register-event boundary post-R5.2 V_SEAL (timing TBD; not pre-named here per anti-pre-emption).

### §5.4 Carry-Forward Classifications (All 18 Candidates)

**Universal classification:** All 18 candidates carry dim (d) INDETERMINATE-DSL-UNAVAILABLE per R5.1 SD-B-α (R2.1 + R2.3 δ1 population-wide application; §34 Step 5 lock-choice (c) standing discipline applied; 2nd cross-cycle §34 re-use at R5.1; carries to R5.2 as inherited classification metadata).

**Source of INDETERMINATE-DSL-UNAVAILABLE classification:** 0/5 raw_payloads accessible for PHASE2C_15 cohort_a source batches (missing from `raw_payloads/` directory at session entry 2026-05-20; R5.1 §1.2 + R2.1 + R2.3 documentation).

**Additional classifications for 2 of 18 candidates** (carry-forward from R5.1 V_SEAL §1.1):

| Hash | Name | Theme | R2.1 verdict | Phase 4 baseline 15bps |
|---|---|---|---|---|
| `7abff29fc2f117a1` | ema_crossover_momentum_acceleration | momentum | INDETERMINATE-overall (dim a+d INDETERMINATE; dim b+c PASS) | PASS (+3.06) |
| `2433a38b2f9a7211` | volume_surge_breakout_divergence | volume_divergence | INDETERMINATE-overall (dim a+d INDETERMINATE; dim b+c PASS) | PASS (+1.11) |

Carry-forward classifications (universal INDETERMINATE-DSL-UNAVAILABLE + 2-of-18 INDETERMINATE-overall) are R5.2 V_SEAL artifact handoff contents per §4.1; R6.1 V_SEAL artifact treatment of these classifications per R6.1 cycle authority (R5.2 does NOT pre-bind R6.1 V_SEAL artifact structure per anti-pre-emption + CLAUDE.md HARD CONSTRAINT line 273).

### §5.5 P2a DSL Recovery Cycle Eligibility (carry-forward)

Per R5.1 V_SEAL §1.2 carry-forward: P2a DSL recovery cycle (~$3-8 API spend per Sub-2 β eligible-not-named binding) remains eligible at separate Charlie register-event boundary. If P2a fires post-R5.2 V_SEAL and produces differential dim (d) outcomes (some candidates PASS, others FAIL, others remain INDETERMINATE), R5.2 cohort framing may be revisited at fresh Charlie register-event with potential SD-B / SD-D re-evaluation per anti-pre-emption.

---

## §6 §34 Pre-Commit Checklist Application

**Cross-cycle precedent:** R2.1 V_SEAL `dac3c3c` (first §34 codification trigger) + R2.3 V_SEAL `fc577d9` (first cross-cycle re-use) + R5.1 V_SEAL `eec9b1c` (second cross-cycle re-use; INDETERMINATE-DSL-UNAVAILABLE classification per §34 Step 5 lock-choice (c)).

**R5.2 §34 application:**

| Audit dimension | Data accessibility status | §34 verdict |
|---|---|---|
| Cohort identifiers (18 candidates) | ✓ Verified at `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_results.csv` + `data/phase4_scoping/cohort_a_candidate_reference.csv` | Pass |
| R5.1 carry-forward INDETERMINATE-DSL-UNAVAILABLE classification | Inherited from R5.1 V_SEAL §1.2 (no re-verification needed at R5.2 layer) | Pass via inheritance |
| Theme-axis stratification at V_SEAL-18 | ✓ Computed via theme column in holdout_results.csv | Pass |
| Phase 4 baseline preview at SPOT 15bps | ✓ Read holdout_results.csv | Pass (preview only; Tier 5 re-run authoritative) |
| SD-A methodology framework family lock | Abstract framework; no data accessibility dependency at R5.2 lock | Pass (framework lock has no data requirement) |
| SD-B α allocation framework lock | Abstract framework; no data accessibility dependency at R5.2 lock | Pass (framework lock has no data requirement) |
| SD-C-β handoff interface (no per-candidate statistics computed at R5.2) | No data accessibility verification required | Pass (no §34 conditional binding triggered) |
| SD-D-α all-18 cohort scope lock | Cohort identifiers verified per row 1 | Pass |

**Verdict:** §34 application at R5.2 V_SEAL is **trivial pass** under locked SD-A-α + SD-B-α + SD-C-β + SD-D-α combination. NO §34 conditional binding triggered at R5.2 lock. §34 application is eligible-for at R6.1 V_SEAL pre-commit checklist per R6.1 cycle authority (data accessibility verification for holdout return series + variance/skew/kurt computation under chosen DSR variant).

**Cross-cycle precedent summary:**

| Cycle | §34 application status | Decision class |
|---|---|---|
| R2.1 V_SEAL `dac3c3c` | First §34 codification trigger | Sub-1 η1-C extension authorized |
| R2.3 V_SEAL `fc577d9` | First cross-cycle re-use | INDETERMINATE-DSL-UNAVAILABLE classification (δ1 population-wide application) |
| R5.1 V_SEAL `eec9b1c` | Second cross-cycle re-use | INDETERMINATE-DSL-UNAVAILABLE per §34 Step 5 lock-choice (c) for all 18 candidates |
| **R5.2 V_SEAL (this cycle)** | **Trivial pass (framework + scope locks; no data-dependent commitments at R5.2 layer)** | **Inherited from R5.1; no new §34 application at R5.2; §34 application is eligible-for at R6.1 V_SEAL per R6.1 cycle authority** |

---

## §7 Finding-Class Observations (Eligible-Not-Named per Anti-Pre-Emption)

R5.2 cycle empirical contributions (forward-only observation; eligible-not-named at separate Charlie register-event boundary for memory codification at `feedback_reviewer_routing_subagent_default.md` extension OR `feedback_*.md` new file creation):

### §7.1 R5.2-A: First MULTI-INSTANCE own-finding-anchoring revision cluster in single PFR round (PFR-Round-1)

Advisor PFR-Round-1 produced **3 simultaneous revisions of distinct prior findings** under explicit bi-directional counter-reminder discipline — heterogeneous revision class (down-calibration + implementation-revision + refinement-calibration), not strictly bi-directional in canonical sense (Advisor revising same finding in opposite directions across rounds). Cluster characterization per P47 v1→V2 patch ADOPT 2026-05-20:
- **A-3 REVISED:** "R3.1d §11 citation imprecise" original finding was structurally OVERCALIBRATED — §11 V_SEAL row at line 555 DOES contain SD9 lock text; original "per R3.1d §11" cite was factually defensible. Bi-directional re-examination revised A-3 from precision-defect classification.
- **A-4 implementation-revised:** "SD-A × SD-C coupling unacknowledged" original finding was substantively correct; v2 P13 matrix implementation overstated restriction. Implementation direction REVISED at PFR-Round-1.
- **A-8 calibrated:** "Q6 tier ranking framework" original recommendation "δ > β > α > γ" strict order lacked rigorous α vs β motivation. Calibrated to partial order "δ > {α, β} > γ" (equivalence-class within family-lock tier).

**First-of-kind:** This is the first cross-cycle MULTI-INSTANCE revision-cluster pattern (3 simultaneous revisions of distinct findings in single PFR round) under explicit bi-directional counter-reminder discipline. Heterogeneous revision class (down-cal A-3 + impl-revision A-4 + refinement-cal A-8); NOT strictly bi-directional in canonical sense (Advisor revising same finding in opposite directions across rounds). Validates bi-directional discipline effectiveness at extended N when explicit reminder is applied per dispatch brief.

### §7.2 R5.2-B: First overcorrection-cascade catch via bi-directional discipline (PFR-Round-2)

Advisor PFR-Round-2 produced **F7 RESOLUTION REVISION** under bi-directional discipline — identifying that P27 v2→v3 mechanical fix overcorrected by stripping diacritic from LITERAL CLAUDE.md quote. Pattern:

> Advisor v1 A-3 (overcalibration) → Charlie ADOPT → v2 P12 fix → v3 P27 overcorrection (line 273 + diacritic stripped from literal quote) → Advisor PFR-Round-2 A-#1 + Codex PFR-Round-2 #4 (independent convergence on caught overcorrection)

**First-of-kind:** This is the first empirical instance of own-finding-anchoring producing a Mode-A-class mechanical-overcorrection cascade that requires PFR-round adversarial catch under bi-directional discipline. Analog to R3.1d V3 BH-FDR fabrication cascade (caught by Codex final-gate grep) but produced via own-finding-anchoring chain rather than fresh hallucination. Bi-directional discipline + cross-model leg both load-bearing for cascade catch.

### §7.3 R5.2-C: First FULLY-CLEAN bi-directional cycle (PFR-Round-3)

Advisor PFR-Round-3 produced **0 own-finding-anchoring revisions** under explicit bi-directional counter-reminder discipline — all 4 prior PFR-Round-2 findings (A-#1 + A-#3 + A-#7 + A-#10) REAFFIRMED clean on bi-directional re-examination (specific finding-by-finding reaffirmation documented in PFR-Round-3 dispatch artifact; not re-litigated here per P50 v1→V2 patch ADOPT 2026-05-20).

**First-of-kind:** This is the first empirical FULLY-CLEAN bi-directional cycle in cross-cycle precedent. Pattern validation: as menu converges to V_FOR_CHARLIE_LOCK, bi-directional revision frequency converges to 0. Bi-directional discipline asymptotic behavior empirically established at extended N within R5.2 cycle.

### §7.4 R5.2-D: 4-round monotonic BLOCKING decline trajectory pattern

R5.2 cycle trajectory: Round-1 (Codex 4 BL + Advisor 0 BL — DIVERGENT BLOCK-LOCK adjudicated) → PFR-Round-1 (Codex 3 BL + Advisor 1 BL — CONVERGENT BLOCK-LOCK) → PFR-Round-2 (Codex 0 BL + Advisor 0 BL — CONVERGENT APPROVE-WITH-FINDINGS; monotonic BLOCKING decline achieved) → PFR-Round-3 (Codex 0 BL + Advisor 0 BL — CONVERGENT APPROVE-WITH-FINDINGS / APPROVE-V_FOR_CHARLIE_LOCK).

**Pattern observation:** R5.2 achieved monotonic BLOCKING decline + reviewer convergence in 4 rounds (vs R5.1's 6 rounds for analogous cycle structure). Shorter convergence due to cleaner v1 menu structure + structural removal path (P22 + P25 + P26) at PFR-Round-1 → PFR-Round-2 transition eliminating high-complexity options.

### §7.5 R5.2-E: BL-Y-refined Phase 1 blind-lean discipline at Task 4 decision class

Charlie register #8 invoked BL-Y-refined Phase 1 blind-lean discipline at Task 4 sub-decision lock decision class with Charlie initial lean disclosed to orchestrator (SD-A-β + SD-B-α + SD-C-γ + SD-D-α) but NOT injected in reviewer dispatch briefs. Reviewers produced independent leans:
- Codex: SD-A-α + SD-B-α + SD-C-β + SD-D-α
- Advisor: SD-A-α + SD-B-α + SD-C-β + SD-D DEFER (or α if forced)

Mechanical Phase 2: CONVERGENT on SD-A + SD-B + SD-C; partial divergence on SD-D. Both reviewers diverged from Charlie's initial lean on SD-A (α vs β) + SD-C (β vs γ). Charlie register #9 switched to reviewers' converged lean.

**Pattern observation:** BL-Y-refined Phase 1 blind-lean discipline at substantive decision class (sub-decision lock register) produced reviewer convergence that Charlie subsequently adopted. Demonstrates empirical value of blind-lean discipline preventing reviewer anchoring on Charlie's lean + producing independent assessment that can revise Charlie's initial direction.

### §7.6 Eligible-Not-Named for Memory Codification

The above R5.2-A through R5.2-E pattern observations are forward-only finding-class candidates eligible for memory codification at separate Charlie register-event boundary per anti-pre-emption. R5.2 cycle does NOT codify these patterns; codification is separate Charlie-register-class register-event at `feedback_reviewer_routing_subagent_default.md` extension OR new `feedback_*.md` file creation.

**Combined cumulative own-finding-anchoring data through R5.2 V_SEAL:**

| Source | Instances | Status |
|---|---|---|
| R2.0 V_SEAL V2-P6 | 1 | Codex-caught (1st cross-cycle instance) |
| R3.1d V_SEAL V2 | 1 | Codex-caught (2nd) |
| R3.1d V_SEAL §32 forward-attribution | 1 | Codex-caught (3rd) |
| R2.3 V_SEAL V-state contradiction | 1 | Codex-caught (4th) |
| B2 housekeeping R1 | 1 | Orchestrator-caught (5th; first Layer-3 instance) |
| R5.1 SD-A-ε v2-PFR | 1 | Advisor-self-caught under explicit reminder (6th; first Layer-1 self-catch) |
| R5.1 H2 PFR-Round-3 | 1 | Advisor-self-caught with 5 H2-AF defects + BLOCK-LOCK (7th) |
| R5.1 PFR-Round-4 bi-directional | 1 | Advisor-bi-directional under counter-reminder (8th; first bi-directional) |
| **R5.2 PFR-Round-1 MULTI-INSTANCE cluster (R5.2-A)** | **3 simultaneous** | **Advisor-bi-directional under counter-reminder (first MULTI-INSTANCE revision-cluster in single PFR round)** |
| **R5.2 PFR-Round-2 F7 RESOLUTION revision (R5.2-B)** | **1** | **Advisor-bi-directional; first OVERCORRECTION-CASCADE catch** |
| **R5.2 PFR-Round-3 FULLY-CLEAN cycle (R5.2-C)** | **0 revisions** | **First FULLY-CLEAN bi-directional cycle empirical pattern** |

Total cumulative empirical own-finding-anchoring instances (through R5.2 V_SEAL): **12 instances** = 8 prior + 4 R5.2 revision instances (3 PFR-Round-1 + 1 PFR-Round-2). R5.2-C is a 0-revision clean-cycle observation, NOT an additional anchoring instance (per P47 v1→V2 patch ADOPT 2026-05-20 — clean-cycle pattern is a methodological-trajectory observation, not a revision instance).

---

## §8 R5.2 → R6.1 Cycle Handoff Contents (Detailed)

### §8.1 R5.2 V_SEAL Artifact Contents Inherited by R6.1

Per §4.1 SD-C-β minimal-handoff lock:

1. **SD-A framework family lock** (DSR-family per §2)
2. **SD-B α allocation framework lock** (Single-α flat per §3)
3. **SD-D source-cohort scope lock** (All-18 V_SEAL-locked per §5)
4. **Cohort identifiers** (18 hypothesis_hash + name + stratum + theme + classification flags per full 18-candidate manifest at §3.3)
5. **R5.1 carry-forward classifications** (INDETERMINATE-DSL-UNAVAILABLE universal + 2 INDETERMINATE-overall)
6. **R5.1 §1.5 Path 1+ explicit eligibility bullet** (supplementary IS-OOS analytical cycle preservation)
7. **R2.3 §8.2 theme-axis provenance caveat** (for R6.1 disclosure if theme stratification applied)
8. **Cross-SD compatibility matrix** (per v5 §4)
9. **§34 application status at R5.2 V_SEAL** (trivial pass; R6.1 §34 application is eligible-for at instrument variant lock per R6.1 cycle authority)

### §8.2 R6.1 Lock Authority

R6.1 V_SEAL locks (per R3.1d V_SEAL SD9 + CLAUDE.md HARD CONSTRAINT line 273):

- Specific DSR instrument variant (illustrative subset per §2.1; R6.1 retains specific variant + formulation mapping authority per CLAUDE.md HARD CONSTRAINT line 273)
- Per-candidate effective threshold
- Statistical N value + effective-N adjustment for serial correlation
- α_total value + R6.1-layer allocation implementation (flat default OR stratification OR weighted)
- Cohort scope at R6.1 (R6.1 independently determines R6.1-layer cohort treatment; SD-D-α R5.2 scope is handoff metadata; any R6.1 sub-scoping per cohort properties at R6.1 fire time)
- §34 application at R6.1 pre-commit (data accessibility verification for holdout return series + variance/skew/kurt under chosen DSR variant)

### §8.3 Anti-Pre-Emption Eligibility-Not-Named Items (preserved for R6.1 + downstream cycles)

- **Bonferroni eligibility:** NOT eligible at R5.2 per Charlie register #5 P22 removal; eligible-not-named at separate Charlie register-event for R6.1 cycle entry OR future methodology re-evaluation per anti-pre-emption (per CLAUDE.md HARD CONSTRAINT line 268 + R3.1d V3.5-PE "OR equivalent" language)
- **FWER-resampling-family (RW + WY)** eligibility-not-named: inclusion at R6.1 layer requires explicit separate Charlie register-event to reopen / broaden R5.2 SD-A framework family lock (NOT eligible via implicit R6.1 instrument-variant choice while SD-A-α DSR-family lock is in force at R5.2)
- **Hybrid DSR + FWER-resampling** restitution candidate per v3 P25 REMOVED block (eligible at separate Charlie register-event if methodologically valid distinct-bias-source narrative emerges)
- **SD-A-δ (Cycle-scope waiver)** restitution candidate for future cycles
- **Supplementary IS-OOS analytical cycle per R5.1 §1.5 Path 1+** at any SD-A option (Pearson on raw Sharpe; bootstrap IS-OOS rank correlation CI; window-shifted rank correlation per R1.2 §7 OBS 6)
- **P2a DSL recovery cycle** (~$3-8 API spend) eligible-not-named per Sub-2 β binding from R2.1 SEAL
- **R2.2 Monday-pattern mechanism investigation** eligible-not-named at separate Charlie register-event per R5.1 V_SEAL §1.4 + Path B post-V_SEAL fire

---

## §9 Eligible-Not-Named Successors (Anti-Pre-Emption Preservation)

R5.2 cycle scope strictly bounds the following NON-RESOLUTIONS (eligible-not-named for separate Charlie register-event boundary per anti-pre-emption + R-series SEAL precedent codified discipline):

**Critical-path priority (UNLOCKED at R5.2 V_SEAL per R3.1d sequencing 1→3→4):**

1. **R6.1 Tier 6 promotion class** — gated behind R5.2 V_SEAL; pending Charlie V_SEAL fire register. R6.1 remains eligible-not-named at separate Charlie register-event boundary. FWER multiplicity correction REQUIRED per R3.1d V_SEAL SD9 + CLAUDE.md HARD CONSTRAINT line 268; instrument variant + threshold + N value lock at R6.1 V_SEAL based on cohort properties at fire time. R5.2 V_SEAL (when sealed) hands off framework family (DSR) + α allocation framework (Single-α flat) + cohort metadata (all-18); R6.1 selects instrument variant + computes statistics + locks numerics.

**Eligible-not-named carry-forward:**

2. **R2.2 Monday-pattern mechanism investigation** — eligible-not-named per R5.1 V_SEAL §1.4 + Path B post-fire framing; eligible at separate Charlie register-event boundary
3. **P2a DSL recovery cycle** (~$3-8 API spend per Sub-2 β eligible-not-named)
4. **Mechanism investigation for FLIP-TRIGGERED candidates** — per R2.1 SD-A A1 dim (c) action menu + V3-P1 anti-rescue binding (2 R2.1-EXCLUDED candidates)
5. **Supplementary IS-OOS analytical cycle per Path 1+ explicit eligibility bullet** — Pearson on raw Sharpe; bootstrap IS-OOS rank correlation CI; window-shifted rank correlation per R1.2 §7 OBS 6
6. **Bonferroni eligibility re-evaluation** — eligible-not-named at separate Charlie register-event boundary
7. **Hybrid DSR + FWER-resampling framework restitution** — per v3 P25 REMOVED block; eligible if methodologically valid distinct-bias-source narrative emerges
8. **SD-B-γ (Hierarchical FWER) restitution** — per v2 P11 REMOVED at v2 A-2 finding
9. **SD-B-δ (Weighted-by-criticality) restitution** — per v3 P26 REMOVED at v3 reviewer-recommended path
10. **SD-A-δ (Cycle-scope waiver) for future cycles** — at v5 documented but not adopted at R5.2 V_SEAL
11. **Memory codification on R5.2 cycle empirical contributions** — R5.2-A (first MULTI-INSTANCE revision-cluster) + R5.2-B (first OVERCORRECTION-CASCADE catch) + R5.2-C (first FULLY-CLEAN bi-directional cycle) + R5.2-D (4-round monotonic BLOCKING decline at menu stage) + R5.2-E (BL-Y-refined Phase 1 effectiveness at substantive decision class) + R5.2-F (patch-incomplete-landing pattern at V1→V2 canonical artifact transition caught by V2 PFR cross-model + bi-directional discipline) + **R5.2-G (patch-incomplete-landing pattern third-instance recurrence at V2→V3 follow-through; conservative-path V3-confirmation PFR per Charlie register #12 effective as anti-pattern circuit-breaker preventing fourth-instance recurrence to V_SEAL)** eligible for memory codification at `feedback_reviewer_routing_subagent_default.md` extension OR new `feedback_*.md` file creation
12. **R3.1b/c** empirical small-lot venue-conditional cost measurement (eligible when Phase 4 paper-trading deploys per R3.1d §8)
13. **Phase 4 paper-trading deployment infrastructure** — eligible at separate Charlie register-event boundary
14. **`agents/themes.py:11` docstring prose-shorthand precision patch** per R2.3 §3.2 (eligible-not-named lightweight cleanup)
15. **Deferred Codex HIGH resolution** (stub-mode `RAW_PAYLOAD_ROOT` + Stage 2b symmetry; eligible per B2 housekeeping cycle 2026-05-20)
16. **Phase 2.5 bandit-dedup activation** (parked per `docs/parked/PARKED_BRANCHES.md`)
17. **Tier-0 pause / strategic-absorption** (defensible after 13 SEAL cycles in current arc post-R5.2)
18. **Advisor opus extended observation pilot** (R5.2 cycle adds N=10 advisor dispatches all with 0 hallucinations; cumulative ~46+ post-/agents-fix dispatches)
19. **Project pause / strategic-absorption** register-event
20. **Other Charlie-specified**

All eligible at separate Charlie register-event boundary per anti-pre-emption + R-series SEAL precedent codified discipline.

---

## §10 V_SEAL Closure Section (Finalized — V_SEAL register-event boundary text pending Charlie register fire)

**Status:** R5.2 V_SEAL closure section finalized post Charlie register #12 "Fire one more brief V3-confirmation PFR 2-leg, if clean then Proceed to V_SEAL closure section finalization" + V3-confirmation PFR CONVERGENT APPROVE-V_FOR_V_SEAL outcome (0 findings; 2 V3-internal fixes verified clean). V_SEAL register-event boundary text pending Charlie register #13 V_SEAL fire authorization.

**Charlie register chain summary (full chain from cycle entry through V_SEAL fire pending):**

| # | Date | Charlie register text | Decision class |
|---|---|---|---|
| 1 | 2026-05-20 | "authorized on the Critical-path priority" + "A" | Cycle entry (R5.2-only) |
| 2 | 2026-05-20 | "ratify plan, fire Task 1" | Plan ratify + Task 1 menu drafting fire |
| 3 | 2026-05-20 | "Authorize Task 2 reviewer dispatch on this v1 menu" | Task 2 v1 reviewer round dispatch |
| 4 | 2026-05-20 | "Authorize all 17 ADOPTs + draft v2 menu + fire PFR-Round-1 on v2" | v1→v2 17 patches + PFR-Round-1 fire |
| 5 | 2026-05-20 | "Authorize all 10 patches P18-P27 with reviewer-recommended path for each substantive decision (P22 remove Bonferroni + P25 remove SD-A-γ + P26 remove SD-B-δ) + fire PFR-Round-2 on v3" | v2→v3 10 patches + 3 removals + PFR-Round-2 fire |
| 6 | 2026-05-20 | "Authorize v4 patches + fire PFR-Round-3 on v4" | v3→v4 8 patches + PFR-Round-3 fire |
| 7 | 2026-05-20 | "Apply 3 mechanical v5 patches (P37+P38+P39) inline + skip PFR-Round-4 + proceed to Task 4 Charlie sub-decision lock" | v4→v5 3 patches + skip PFR-Round-4 + Task 4 proceed |
| 8 | 2026-05-20 | "i am thinking SD-A-β + SD-B-α + SD-C-γ + SD-D-α, but shot a blind lean to reviewers first to see what they think" | Blind-lean Phase 1 dispatch + Charlie initial lean disclosure |
| 9 | 2026-05-20 | "Switch to reviewers' converged lean SD-A-α + SD-B-α + SD-C-β + SD-D-α" | Sub-decision lock fire (Task 4) |
| 10 | 2026-05-20 | "Authorize all 11 v1→V2 patches (P40-P50) + draft V2 + fire V2 PFR reviewer round (PFR-rule-Y triggered per substantive patches)" | v1→V2 11 canonical patches + V2 PFR fire |
| 11 | 2026-05-20 | "Authorize 3 required V3 patches (P51 + P52 + P53) + §10 V1→V2 placeholder fix (mechanical) + V3 PFR + proceed to V_SEAL closure section finalization" | V2→V3 4 canonical patches + V3 PFR fire |
| 12 | 2026-05-21 | "Fire one more brief V3-confirmation PFR 2-leg, if clean then Proceed to V_SEAL closure section finalization" | V3-confirmation PFR fire + V_SEAL closure finalization on clean outcome |
| 13 | 2026-05-21 | "fire V_SEAL register" | V_SEAL fire register-event boundary fires; SEAL bundle commit (canonical artifact + Phase Marker advance + history.md atomic update per Option 1A 17th empirical trigger) |

**V_SEAL register-event boundary text:** Charlie register 2026-05-21 "fire V_SEAL register" authorizes R5.2 V_SEAL bundle commit. R5.2 Phase B Selection-Inflation Handling cycle SEALED at this register-event boundary. Locked sub-decisions per §0 register #9 (SD-A-α + SD-B-α + SD-C-β + SD-D-α) propagated to V_SEAL artifact body §1-§5; R6.1 instrument variant + threshold + N value lock per CLAUDE.md HARD CONSTRAINT line 273 preserved + R5.1 §1.5 Path 1+ supplementary IS-OOS analytical cycle eligibility preserved + Bonferroni eligibility-not-named at separate Charlie register-event boundary + R6.1 cycle authorization gated behind this V_SEAL fire + R6.1 inheritance per §4 + §8 handoff specification.

**Locked sub-decisions (V_SEAL canonical):**

- **SD-A-α** DSR-family methodology framework family lock (Bailey-López de Prado 2014; Sharpe-haircut framework family)
- **SD-B-α** Single-α flat α allocation framework lock
- **SD-C-β** Minimal-handoff R5.2 → R6.1 handoff interface lock
- **SD-D-α** All-18 V_SEAL-locked cohort scope lock

**Cumulative cycle metrics (V_SEAL-ready state at V3-confirmation PFR completion):**

- **Reviewer rounds:** 9 substantive rounds × 2-leg subagent default = **18 total dispatches** (9 per leg). Breakdown:
  - 4 menu-stage reviewer rounds (Round-1 + PFR-Round-1/2/3) = 8 dispatches
  - 1 Blind-lean Phase 1 round at Task 4 sub-decision lock = 2 dispatches
  - 1 V1 reviewer round (Task 7 canonical artifact) = 2 dispatches
  - 1 V2 PFR round = 2 dispatches
  - 1 V3 PFR round = 2 dispatches
  - 1 V3-confirmation PFR round (per Charlie register #12) = 2 dispatches
- **Monotonic BLOCKING decline trajectory:** Round-1 4 BL → PFR-Round-1 4 BL → PFR-Round-2 0 BL → PFR-Round-3 0 BL (CONVERGED at PFR-Round-2 at menu stage); V1 reviewer round 1 BL → V2 PFR 1 BL → V3 PFR 1 BL → V3-confirmation PFR 0 BL (CONVERGED at V3-confirmation at canonical artifact stage)
- **Cumulative patches across cycle:** 38 menu-stage patches (v1→v2 17 + v2→v3 10 + v3→v4 8 + v4→v5 3) + 15 canonical artifact patches (v1→V2 11 [P40-P50] + V2→V3 4 [P51-P54]) + 3 V3-internal fixes (2 P51 follow-through at §2.2/§8.2 + 1 V3 PFR §8.2 line 518 fix + 1 V3 PFR F7 tally correction) = **56 cumulative patches**
- **0 verified Codex hallucinations within cycle** through 9 Codex dispatches (lifetime ~1/57 ≈ 1.8%)
- **0 verified Advisor opus hallucinations within cycle** through 9 Advisor dispatches (cumulative through R5.2 close: 50+ post-/agents-fix dispatches; 0 verified hallucinations — Mode A re-evaluation outcome (a) further validated at extended N)
- **4 R5.2 own-finding-anchoring REVISION instances** (3 PFR-Round-1 simultaneous revisions + 1 PFR-Round-2 RESOLUTION revision; PFR-Round-3/V2-PFR/V3-PFR/V3-confirmation-PFR all REAFFIRMATIONS not revisions) = **total 12 cumulative cross-cycle empirical own-finding-anchoring instances** under explicit bi-directional discipline (8 prior + 4 R5.2)
- **4 patch-incomplete-landing pattern instances** caught by reviewer rounds within cycle (R5.2-G empirical class):
  1. V1→V2: P45 R6.1 imperative (V1: 5 sites named; V2: 2 fixed; V3: 3 remaining)
  2. V1→V2: P46 §2.1 5-variant (V1: site named; V2: missed; V3: §2.1 rewritten + 2 follow-through at §2.2/§8.2)
  3. V1→V2: P47 DUAL-BI-DIRECTIONAL (V1: 4 sites named; V2: only §7.1 heading; V3: 4 sites propagated)
  4. V2→V3: P51 follow-through at §8.2 line 518 (V3 brief: site named; V3 application: missed; V3 PFR: caught; V3-internal: fixed)
- **3-layer safety architecture:** Layer 1 (Advisor self-discount) + Layer 2 (Codex cross-model) + Layer 3 (Orchestrator independent verification) all operational across all 9 rounds; cross-model leg LOAD-BEARING at V1 reviewer + V2 PFR + V3 PFR + V3-confirmation PFR

**Artifact signature:** R5.2 Phase B Selection-Inflation Handling V_SEAL canonical artifact sealed at register-event boundary 2026-05-21 per Charlie register #13 "fire V_SEAL register". Approximately 680 lines / 11 main §§ + V_SEAL closure §10 + V-anchor chain §11. SEAL bundle: this artifact + CLAUDE.md Phase Marker advance + docs/phase_marker_history.md atomic update per Option 1A 17th empirical trigger.

---

## §11 V-anchor Chain / Provenance Trail

### V1 → V2 → V3 → V4 → V5 menu evolution (v5 menu §9 provenance trail; this artifact V1 inherits)

[See `/tmp/r5_2_round1_sd_menu_draft_v5.md` §9 v1→v2 + v2→v3 + v3→v4 + v4→v5 provenance subsections for detailed patch trail of 38 patches across 5 menu versions]

### V1 → V2 canonical artifact patches (11 ADOPTed from V1 reviewer round Task 7 CONVERGENT BLOCK-LOCK 2026-05-20)

| Patch | Source | V1 issue | V2 application |
|---|---|---|---|
| **P40** | Codex V1 reviewer #1 (BLOCKING) + Advisor V1 reviewer A-#1 (HIGH) | §9 "now satisfied at R5.2 cycle close" + §10 cumulative metrics framing pre-empts V_SEAL fire boundary while V1 DRAFT pre-reviewer-round | §9: "gated behind R5.2 V_SEAL; pending Charlie V_SEAL fire register"; §0 status banner updated to V2 DRAFT |
| **P41** | Codex V1 reviewer #2 (HIGH) | 6 instances of "likely = 18" / "likely inherited" pre-characterizations for R6.1 N at §1.4 + §2.2 + §4.3 + §5.2 + §5.4 + §8.2 | All instances replaced with neutral "R6.1 independently determines the statistical N, effective-N, and any R6.1-layer cohort scoping based on cohort properties at R6.1 fire time" |
| **P42** | Codex V1 reviewer #3 (HIGH) | SD-C-β handoff claims "18 hypothesis_hash + theme assignments (per §3.3 table)" but §3.3 only had 3 Stratum A enumerated; no full 18-candidate manifest | Added full 18-row cohort manifest at §3.3 with hash + name + stratum + theme + Phase 4 baseline Sharpe + classification flags; §4.1 + §8.1 references updated |
| **P43** | Codex V1 reviewer #4 (MEDIUM) | §2.3 + §8.3 FWER-resampling eligibility "alongside DSR variants" at R6.1 without separate Charlie register — loophole around DSR-family lock | Tightened §2.3 + §8.3 to require explicit separate Charlie register-event to reopen / broaden R5.2 SD-A framework family lock; R6.1 NOT eligible to add FWER-resampling via implicit instrument-variant choice while SD-A-α in force |
| **P44** | Codex V1 reviewer #5 (MEDIUM) | "Codex 0/10 + Advisor 0/10" dispatch math wrong (5 rounds × 2 legs = 10 total; 5 per leg through Task 4) | Updated to "Codex 0/6 + Advisor 0/6 per leg through V1 reviewer round = 12 total dispatches across 6 rounds (4 menu-stage + 1 blind-lean + 1 V1 review); lifetime ~1/52 ≈ 1.9%" |
| **P45** | Advisor V1 reviewer A-#2 (MEDIUM) | §5.4 "R6.1 must propagate ... classifications" + §8.1 item 9 "R6.1 will need application" — imperative pre-binds R6.1 V_SEAL artifact structure from R5.2 layer | Softened §5.4 to "Carry-forward classifications are R5.2 V_SEAL artifact handoff contents per §4.1; R6.1 V_SEAL artifact treatment per R6.1 cycle authority"; §8.1 item 9 softened to "is eligible-for at R6.1 instrument variant lock per R6.1 cycle authority" |
| **P46** | Advisor V1 reviewer A-#3 (MEDIUM) | §2.1 enumeration of 5 DSR variants overstates distinctness (variance-stabilized + higher-moment-corrected NOT distinct from BLdP closed-form which incorporates non-normality correction per paper) | Re-enumerated §2.1 to illustrative-subset (3 items): BLdP closed-form analytical (incorporates skew/kurt), Monte Carlo refinement, block-bootstrap variants for serial-correlation variance; framing explicitly "illustrative subset; NOT exhaustive; R6.1 retains specific variant ↔ formulation mapping authority" |
| **P47** | Advisor V1 reviewer A-#4 (LOW) + Codex V1 reviewer #6 (LOW) | §7.1 "DUAL-BI-DIRECTIONAL" naming inflates revision-class (actual = heterogeneous: down-cal A-3 + impl-revision A-4 + refinement-cal A-8) + §7.6 + §10 12-instance tally conflates R5.2-C 0-revision observation with anchoring instance | §7.1 renamed to "First MULTI-INSTANCE own-finding-anchoring revision cluster in single PFR round"; §7.6 + §10 12-instance tally clarified: "12 instances = 8 prior + 4 R5.2 revision instances (3 PFR-Round-1 + 1 PFR-Round-2). R5.2-C is 0-revision clean-cycle observation NOT additional instance" |
| **P48** | Advisor V1 reviewer A-#7 (LOW) | §0 scope-bleed trip-wire status doesn't include V1 reviewer round + V2/V3 patches as in-scope | Appended "+ V1 reviewer round (Task 7) + any conditional V2/V3 patches + PFR-rule-Y rounds + V_SEAL fire register text" to §0 trip-wire status |
| **P49** | Advisor V1 reviewer A-#8 (LOW) | §4.1 (8 items) vs §8.1 (9 items) inconsistency — §8.1 added §34 status row not in §4.1 | §4.1 item 9 added: "§34 application status at R5.2 V_SEAL: trivial pass (no per-candidate statistics computed at R5.2 under SD-C-β; see §6 application table)" |
| **P50** | Advisor V1 reviewer A-#6 (LOW) | §7.3 R5.2-C "REAFFIRMED clean" sub-claim not independently verifiable from current session artifacts | Added caveat "(specific finding-by-finding reaffirmation documented in PFR-Round-3 dispatch artifact; not re-litigated here)" to §7.3 R5.2-C |

### V2 → V3 canonical artifact patches (4 ADOPTed from V2 PFR CONVERGENT BLOCK-LOCK 2026-05-20)

| Patch | Source | V2 issue | V3 application |
|---|---|---|---|
| **P51** | Codex V2 PFR #1 (BLOCKING) + Advisor V2 PFR #1 (HIGH) | P46 incomplete landing: §2.1 retained V1 5-variant enumeration (variance-stabilized + higher-moment-corrected NOT distinct from BLdP closed-form per BLdP 2014 paper structure); only §1.1 had been rewritten to 3-item illustrative subset | Rewrote §2.1 to match §1.1 3-item illustrative subset (BLdP closed-form analytical w/ skew/kurt + Monte Carlo refinement + block-bootstrap variants); explicit BLdP formula `PSR = Z((SR - SR*)√(T-1) / √(1 - γ₃·SR + (γ₄-1)/4·SR²))` reference added to demonstrate native non-normality correction |
| **P52** | Advisor V2 PFR #2 (HIGH) | P45 incomplete landing: §4.4 + §6 verdict + §6 cross-cycle table retained "R6.1 will need / will be required / will apply" imperative pre-binding language; only §5.4 + §8.1 item 9 softened | Softened all 3 remaining sites: §4.4 "R6.1 V_SEAL will need" → "§34 application at R6.1 layer is eligible-for at R6.1 V_SEAL pre-commit checklist per R6.1 cycle authority"; §6 verdict "will be required" → "is eligible-for"; §6 cross-cycle table "R6.1 V_SEAL will apply §34" → "§34 application is eligible-for at R6.1 V_SEAL per R6.1 cycle authority" |
| **P53** | Advisor V2 PFR #3 (MEDIUM) | P47 incomplete landing: "DUAL-BI-DIRECTIONAL" terminology persisted at §0 line 45 + §7.1 body + §7.6 table + §9 line 562; only §7.1 heading had been renamed to "MULTI-INSTANCE" | Replaced all 4 remaining sites with "MULTI-INSTANCE revision-cluster" framing consistently |
| **P54** | Advisor V2 PFR #6 (LOW) | §10 V_SEAL Closure placeholder header read "V1 DRAFT placeholder structure" — stale at V2/V3 | Updated to "placeholder structure (version-neutral; finalized at V_SEAL fire register with full cycle metrics including V2 PFR round + V3 PFR round + V_SEAL fire register dispatches)" |
| (DEFER) | Advisor V2 PFR #4 MEDIUM | §10 dispatch math (10 → 12) + lifetime hallucination percentage (1/50 → 1/52) | DEFER to V_SEAL fire register §10 finalization (full cycle metrics including V2 PFR + V3 PFR + V_SEAL fire dispatches) |
| (DEFER) | Advisor V2 PFR #5 MEDIUM | §1.5 cross-SD compatibility matrix references /tmp/ working file (not SEAL-class self-contained) | DEFER as eligible-not-named cleanup OR V_SEAL fire register §1.5 optional enhancement |
| (DEFER) | Advisor V2 PFR #7 LOW | §4.4 single-row table vs §6 9-row table framing tension | DEFER as eligible-not-named polish |
| (DEFER) | Advisor V2 PFR #8 LOW | §10 38 cumulative menu-stage patches doesn't include 11 canonical v1→V2 patches | DEFER to V_SEAL fire register §10 finalization |

### V-anchor chain (canonical artifact versions)

| Version | Status | Description |
|---|---|---|
| V1 | ARCHIVED | Initial canonical artifact draft post Charlie register #9 sub-decision lock (SD-A-α + SD-B-α + SD-C-β + SD-D-α). Structure: 11 main §§ + V_SEAL closure placeholder + V-anchor chain. V1 reviewer round returned CONVERGENT BLOCK-LOCK (Codex 6 + Advisor 8 = 14 findings; 11 ADOPTed for v1→V2 patches P40-P50). |
| V2 | ARCHIVED | Post-V1-reviewer-round 11 ADOPTed patches applied (P40-P50). V2 PFR returned CONVERGENT BLOCK-LOCK (Codex 1 BL + Advisor 2 HIGH + 3 MED + 3 LOW; root cause = patch-incomplete-landing pattern at V1→V2 transition; 4 ADOPTed V2→V3 patches P51-P54; 4 DEFER to V_SEAL fire OR eligible-not-named cleanup). |
| V3 | ARCHIVED | Post-V2-PFR 4 ADOPTed patches applied (P51 §2.1 + P52 R6.1 imperatives + P53 MULTI-INSTANCE terminology + P54 §10 placeholder version). V3 PFR returned CONVERGENT outcome (Codex 1 MED at §8.2 line 518 + Advisor BLOCK-LOCK 1 BL + 1 LOW; same root issue = R5.2-G third-instance patch-incomplete-landing). 2 V3-internal fixes applied (§8.2 line 518 + §0/§11 V2 ARCHIVED row tally correction). V3-confirmation PFR (per Charlie register #12 conservative-path) returned CONVERGENT APPROVE-V_FOR_V_SEAL on both legs with 0 findings. |
| **V_SEAL** | **SEALED 2026-05-21** | Canonical sealed artifact at register-event boundary per Charlie register #13 "fire V_SEAL register" 2026-05-21. V_SEAL closure §10 finalized with full Charlie register chain #1-#13 + cumulative cycle metrics + locked sub-decisions canonical statement + artifact signature. SEAL bundle commit = this artifact + CLAUDE.md Phase Marker advance + docs/phase_marker_history.md atomic update per Option 1A binding 17th empirical trigger. |

---

**End of V_SEAL (sealed 2026-05-21).** R5.2 Phase B Selection-Inflation Handling V_SEAL canonical artifact sealed at register-event boundary per Charlie register #13. SEAL bundle commit fired. R6.1 Tier 6 promotion class eligible-not-named per anti-pre-emption + R3.1d sequencing 1→3→4 (R3.1d ✓ → Tier 2 SEAL ✓ → R5.1 ✓ → R5.2 ✓ → R6.1). All eligible-not-named successors at §9 await separate Charlie register-event boundary per `feedback_authorization_routing.md` hard rule + anti-pre-emption discipline.
