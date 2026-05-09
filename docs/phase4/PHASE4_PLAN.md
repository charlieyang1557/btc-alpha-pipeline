# PHASE4_PLAN: parameter lock

**Status:** SEALED at sub-spec drafting cycle SEAL register-event boundary.

**Cycle scope:** parameter specification for the Phase 4 forward-test of PHASE2C_15 cohort_a candidates. Locks coordinates for the persistence test; does not authorize the implementation arc. Z-tier minimal-governance-surface discipline binding per scoping cycle entry. Anti-momentum-binding preserved: cycle SEAL does not imply implementation arc authorization.

## §1 Parameter values

### §1.1 Forward-test window date D (smallest item)

- **D = 2026-01-01 00:00 UTC.**
- Two registers must hold: Register A (D > proposer training cutoff) AND Register B (D > test-window end). Register B binds; Register A satisfied by construction.
- Proposer = `claude-sonnet-4-5` per [`agents/proposer/sonnet_backend.py:59`](../../agents/proposer/sonnet_backend.py#L59); training cutoff per Anthropic published model card (verify exact date at fire-time, but well before mid-2025).
- Test window per `config/environments.yaml` v2: `test = 2025`. D = first day post-test = 2026-01-01.

Justification: brief §2 item 2 entry-time binding constraint sealed at scoping cycle entry; not relitigated. Co-existing constraints; more restrictive binds.

### §1.2 Forward-test window methodology

- **Single-contiguous window [2026-01-01, T_end].** T_end = canonical parquet latest at fire-time.
- Current window at this PLAN: [2026-01-01, 2026-04-16 07:00 UTC] ≈ 3.5 months / ~2,500 1h bars.
- Pre-fire data refresh permitted via `ingestion.incremental_update` (extends T_end forward); post-fire refresh prohibited (locks T_end at fire register-event boundary).
- Methodology lock is final at this PLAN: pre-fire data refresh extends T_end but does NOT unlock methodology re-adjudication (e.g., an extended window does not authorize switching to walk-forward at fire-time).
- Walk-forward NOT used: per Lookup 2 calendar_effect candidates have median 14.5 trades across 4 regimes; multi-segment WF would over-fragment thin trade counts and destabilize per-segment Sharpe.

Justification: function of §1.1 D and post-D parquet availability. Single-contiguous gives statistical power; refresh policy locks data integrity asymmetrically (extend allowed pre-fire; freeze at fire).

### §1.3 Candidate evaluation universe + theme decomposition (Item 1 + observation #6 coupled)

- **Sub-path: (c.1) all 39 unfiltered candidates with calendar-explicit 2-strata reporting.**
- Stratum A (calendar): 22 calendar_effect candidates.
- Stratum B (non-calendar): 17 candidates (volume_divergence n=7, momentum n=6, mean_reversion n=2, volatility_regime n=2).
- Each stratum tested independently per §1.5; both outcomes reported as register-class-distinct persistence claims.
- (c.3) filtered 24 retained as descriptive supplementary slice (NOT primary): filter functions as theme de-concentrator (13/15 = 86.7% of filter exclusions are calendar per Lookup 1) — conflates trade-count with theme.
- (c.2) top-N excluded: selection-on-noise risk per ChatGPT + advisor convergence. (c.4) excluded: collapses to (c.3) at filtered register; only meaningful at unfiltered (37/39) where (c.1) already covers 39. Full-(c.5) excluded: structurally underpowered at thin themes (mean_reversion = vol_regime = 2 each).
- Positive justification for (c.1) base + 2-strata (vs the alternatives): preserves the original cohort_a unit of analysis (39 candidates as fired, no post-hoc subsetting); 2-strata reporting protects against post-fire theme-imbalance framing drift without conditioning on trade-count-correlated subsetting (which the (c.3) filter would do).

Justification: brief §4 substantive implications + observation #6 binding. Calendar-explicit decomposition pre-registers theme-imbalance handling, protects against post-fire framing drift on the AND-gate ~4% rate claim, and respects the ~10× theme-rate asymmetry (calendar 22/200 = 11% vs thin themes ~1%) that FFH p=0.42 omnibus did not test. Calendar/non-calendar is the substantive cleavage; theme-by-theme is too fragmented at this N.

### §1.4 Cost model

Structure: per-side cost = taker_fee + slippage_bps. Position size: constant nominal $1000 USD per trade (~0.002% of typical BTC 1h Binance spot volume of ~$50M+; impact dynamics negligible at this scale).

- **Taker fee: 10 bps per side** (Binance VIP 0 spot taker, no BNB discount; conservative retail profile; verify at fire-time against Binance published fee schedule).
- **Slippage: 5 bps per side fixed** (no L2 order book modeling at MVD scope).
- **Per-side base case: 15 bps; round-trip: 30 bps.**
- **Sensitivity: per-side {13 bps, 17 bps}** (slippage ±2 bps).
- **Dual-reporting:** Phase 4 reports both research-time 7 bps per side (PHASE2C_15-comparability) AND realistic 15 bps per side (forward answer). Success criterion §1.5 evaluated at realistic-cost basis only.

Justification: research-time 7 bps per side substantively below realistic floor (Binance VIP 0 taker = 10 bps alone). Population→strategy register transition per PHASE2C_15 closeout requires realistic costs to ground deployable-alpha-class claims. Sensitivity range bounds slippage uncertainty without L2 modeling. Dual-reporting preserves comparability without conflating registers.

### §1.5 Success criterion (hardest item)

Per stratum (Stratum A n=22, Stratum B n=17):

- H_0: fraction of candidates with positive forward Sharpe (net of realistic costs per §1.4) equals 0.5.
- H_a: fraction > 0.5.
- Test: one-sided binomial per stratum at **Bonferroni-adjusted nominal α=0.025/stratum** (family-wise α=0.05 controlled).
- **Phase 4 success iff at least one stratum rejects H_0** evaluated at §1.4 base-case cost (15 bps per side). Sensitivity values {13, 17} bps are auxiliary, not part of the success criterion.
- Strict thresholds (smallest k with achieved per-stratum α ≤ 0.025; verified via `scipy.stats.binom.sf`):
  - **Stratum A: ≥17/22** (achieved α=0.0085; pass rate 77.3%)
  - **Stratum B: ≥13/17** (achieved α=0.0245; pass rate 76.5%)
  - Achieved family-wise α ≈ 0.033 (conservative under nominal 0.05 due to binomial discreteness).

Interpretation guard (purely restrictive on framing of outcomes):
- If the disjunction is satisfied by **Stratum A only**: the Phase 4 claim is "calendar-effect candidates show forward persistence; non-calendar candidates do not."
- If by **Stratum B only**: the converse — "non-calendar candidates show forward persistence; calendar-effect candidates do not."
- If by **both**: the claim is two independent stratum-level persistence results, NOT a strengthened cohort-level claim.

Auxiliary descriptive (NOT pre-committed as criterion): per-candidate forward-Sharpe distribution; per-stratum pass count at research-time 7 bps and realistic 15 bps; per-stratum pass count at sensitivity {13, 17} bps.

The 7 bps research-time number is descriptive only for triangulating against PHASE2C_15 WF Sharpes; under no framing does it constitute a Phase 4 success measure.

Honest power disclosure: at moderate true effect (p≈0.7), per-stratum power is **31% (Stratum A) and 39% (Stratum B)**; at substantial true effect (p≈0.8), power is 73% (A) and 76% (B). Phase 4 has adequate power for substantial effects but limited power for moderate ones at this N — this is a substantive trade-off, not a hidden disclaimer.

Justification: coin-flip rejection answers the strong epistemic claim Phase 4 can support (population-level edge vs random-direction); absolute Sharpe thresholds are NOT pre-registered because no analogous external baseline exists (PHASE2C_15 had PHASE2C_12 baseline; Phase 4 has none). The stricter Bonferroni-adjusted thresholds are accepted as the cost of preserving observation #6 theme-decomposition pre-registration as load-bearing success-criterion structure (not descriptive afterthought) while honestly controlling family-wise Type I error. The power profile is the right kind of conservatism for a falsifiable persistence test.

## §2 Cycle-scope binding

PHASE2C_15 closeout §3.4 violation-index 4-pattern register continues to bind throughout Phase 4. Sealed corpus invariance preserved: METHODOLOGY_NOTES §31 PHASE2C_8.1→15 arc lessons + PHASE2C_15 closeout artifacts not modified by Phase 4.

§31 P6 default-not-gated discipline carries: descriptive lookups against committed data (Binance fee schedule queries, parquet probes, reference-artifact reads) run unconditionally as cycle-internal data work. Authorization gates apply to API spend / commits / pushes / methodology pre-commitment / scope expansion only.

## §3 Discipline anchors

- Anti-pre-naming preserved: implementation arc Step structure + closeout deliverable scope + tag wording NOT pre-committed at this PLAN.
- Anti-momentum-binding strict reading: SEAL of this PLAN does NOT authorize implementation arc; Charlie register authorization required at fresh boundary post-SEAL.
- Per-fix reviewer adjudication binds (no bulk-accept) per [`feedback_reviewer_suggestion_adjudication.md`](../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md).
- Reviewer routing: ChatGPT + Claude advisor single-pass at PLAN-class deliverable. Codex skipped at PLAN scope unless `cost_model.py` or equivalent implementation surfaces in cycle, in which case Codex on that artifact only.
- Length budget: this PLAN targets ≤ 130 lines (advisor structural objection at cycle entry; weight-by-depth honored).

## §4 Anchors

- HEAD at WORKING DRAFT register: `11b39f2`
- Brief: `/tmp/PHASE4_SUBSPEC_CYCLE_ENTRY_BRIEF.md` (provenance only; not canonical artifact)
- Reference artifact: `data/phase4_scoping/cohort_a_candidate_reference.csv` (39 × 19; committed at `11b39f2`)
- PHASE2C_15 main fire SEAL: tag `phase2c-15-main-fire-v1` at commit `734570c`
- Engine lineage: `eb1c87f` (`wf-corrected-v1`)
- Test window register source: `config/environments.yaml` v2 schema (`test = 2025`)
- Cost model upstream context: CLAUDE.md "Execution Convention" §4 (research-time 7 bps per side); PHASE2C_15 closeout §4 (population→strategy transition framing)
