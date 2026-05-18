# PHASE5_2_VENUE_RECONCILIATION_NOTE.md

**Canonical artifact for Phase 5.2 §2.1-reconciliation-lite Bucket-1 investigation cycle (Template B; structural analog to PHASE5_1_COST_MODEL_INVESTIGATION_NOTE)**

**Status:** V4 SEAL (Cadence 2 deliverable seal + closeout register-event boundary; SEAL-only authorization per [`feedback_authorization_routing.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md) — venue commitment + branch decision are separate future Charlie register-events; not bundled into this SEAL).

---

## §0 Cycle Metadata

**Cycle type:** Bucket-1 single-deliverable investigation note (Template B; NOT multi-arc scoping → sub-spec → execute → closeout structure).

**Cycle boundary:** Phase 5.2 §2.1-reconciliation-lite cycle.

**Trigger:** Phase 5.1 §2.1 forward-only carry-forward observation (cross-source composition: 4bps `config/execution.yaml` futures-fee-schedule label vs 10bps `PHASE4_PLAN.md §1.4` spot-taker assumption) elevated to active register-event per cycle-entry Charlie register.

**Sequencing position:** Option B sequencing per Phase 5.1 §3.3 reviewer round — §2.1-reconciliation-lite (this cycle) → formal branch register-event at closeout → [Path 1 W4-scoped OR full Path 2 mandatory] → Path 3.

**Scope binding (sealed-only / bounded-desk-research):**
- Cycle scope = single-deliverable investigation note resolving §2.1 cross-source composition observation
- 5 pre-specified sub-tasks (per §0 metadata at cycle entry):
  1. External Binance public fee schedule lookup (Spot taker/maker + Futures + BNB discount + VIP-0 baseline)
  2. 4bps source tracing (`config/execution.yaml` futures-fee-schedule label provenance + spot applicability)
  3. 10bps source tracing (`PHASE4_PLAN.md §1.4` spot-taker assumption derivation)
  4. Microstructure literature for BTC/USDT spot taker slippage bounded literature-based estimate
  5. Reconciliation analysis + branch-criterion proposal (this section)
- NO L2 replay, NO API spend (research-class), NO batch runs, NO new infrastructure, NO sealed-corpus modification, NO simulation beyond bounded desk-research literature

**§0 scope-bleed trip-wire status (Cadence 1 close):** clean. None of the 5 literal triggers fired during Cadence 1 grounding. Material observation surfaced (venue-mismatch as the proposed substantive resolution of §2.1, pending V3 SEAL) is in-scope per Phase 5.1 §7.2 carry-forward framing.

**Cadence structure (Phase 5.2):**
- Cadence 1: sub-tasks 1+2+3+4 (grounding, executed in parallel) — completed
- Cadence 1→2 informal checkpoint: registered as hybrid per modify(b)-with-scope-discipline (advisor + Codex divergence resolved via §10 sub-§§ anti-pre-naming binding)
- Cadence 2: sub-task 5 (synthesis + branch-criterion proposal) — this section
- Reviewer round: 2-leg subagent default at deliverable seal (Codex + quant-research-advisor); BL-Y-refined applies (canonical artifact); PFR-rule-Y at closeout-class
- Closeout: formal branch register-event at Charlie register on sealed Cadence 2 deliverable

**Anti-pre-naming binding (preserved throughout):** this note resolves §2.1's cross-source observation and proposes branch-criterion STRUCTURE. It does NOT adjudicate Path 1 W4 reinterpretation, Path 2 marginal value, Stratum A D-I label re-interpretation, OR execution-venue policy. Each of those is named as eligible-not-named observation for separate Charlie register-event boundary.

**Charlie register chain (Phase 5.2 cycle through V4 SEAL):**

| # | Decision | Register surface |
|---|----------|------------------|
| 1 | §3.3 sequencing (Option B authorized) | "authorized Reviewer convergent verdict + your lean" |
| 2 | Cycle shape (α / Bucket-1) | "authorized as 4 way convergence" |
| 3 | Cadence shape (B / 2-cadence) | "Authorized" |
| 4 | Cadence 1 fire | "iii authorized" |
| 5 | Cadence 1→2 checkpoint (hybrid modify(b)-with-scope-discipline; Cadence 2 fire bundled → V1 DRAFT written) | "agree with your lean, authorized" |
| 6 | V1 DRAFT reviewer round dispatch | "dispatch" |
| 7 | V1→V2 adjudication (7 ADOPT + 1 PUSHBACK on Advisor F1 hallucination) | "confirm 7+1" |
| 8 | PFR-scoped re-review dispatch | implicit per "adopt-all-with-PFR" |
| 9 | V2→V3 PFR adjudication (2 ADOPT Codex NF1+NF2 + 1 PUSHBACK on Advisor PFR NF1 hallucination) | "adopt Codex" |
| 10 | Memory codification (Option II citation verification discipline) | "Option II codify" |
| 11 | V4 SEAL (standalone Bucket-1 closeout; venue commitment + branch decision NOT bundled) | "SEAL-only" |

---

## §1 Scope and Objective

**§1.1 Question this cycle resolves:**

Phase 5.1 §2.1 surfaced a cross-source composition observation: `config/execution.yaml`'s 4bps taker fee (under "Binance perpetual futures, VIP 0" label) and `PHASE4_PLAN.md §1.4`'s 10bps spot taker assumption are unreconciled. The Phase 5.1 cycle deferred this observation per Q1(a) sealed-only scope binding. The §2.1-reconciliation-lite cycle's load-bearing question is:

> **Are the 4bps and 10bps cost numbers contradictory, or are they internally consistent within their respective execution-venue contexts?**

**§1.2 What this cycle does NOT resolve:**

- Execution-venue policy decision (whether project commits to spot, futures, or both)
- Path 1 W4-scoped paper trading interpretive basis (re-evaluation of "salvageable-at-research-time-7bps" framing)
- Path 2 full L2 replay marginal-value re-evaluation
- Stratum A D-I label re-interpretation under venue-clarified cost basis
- `config/execution.yaml` venue-label vs data-layer reconciliation (sealed-corpus modification)
- Sealed-corpus errata for PHASE5_1_COST_MODEL_INVESTIGATION_NOTE

Each of the above is named as eligible-not-named observation for separate Charlie register-event boundary at §5 below. Per §10 sub-§§ anti-pre-naming binding, this note does not pre-name how those questions should be resolved.

**§1.3 Scope verification anchor (V1 DRAFT):**

This deliverable does not modify any sealed artifact. All factual claims in §2-§5 derive from:
- `config/execution.yaml` (sealed; read-only)
- `docs/phase4/PHASE4_PLAN.md` (sealed; read-only)
- `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (sealed; read-only)
- External public sources (Binance fee schedule + academic microstructure literature) — declared transparently in §4

---

## §2 Headline Finding: Venue-Mismatch (NOT 4-vs-10 contradiction)

The §2.1 cross-source observation is resolved as follows:

**Both numbers are externally accurate for their stated venues, but they apply to DIFFERENT execution venues:**

| Source | Numerical claim | Venue label | External verification |
|--------|----------------|-------------|----------------------|
| `config/execution.yaml:42-53` | taker_fee_bps: 4.0 (+ slippage 3.0 = 7bps/side total) | "Binance perpetual futures, VIP 0" | Internal label is consistent with USDⓈ-M perpetual futures venue. Current externally-published Binance USDⓈ-M VIP-0 futures taker is ~5 bps (0.0500%) per https://www.binance.com/en/fee/schedule; ~3.75 bps with BNB 25% discount. The 4 bps sealed project value falls between current published rates and may reflect a historical schedule, partial BNB discount, referral-tier adjustment, or estimation — exact provenance NOT traced in this cycle (eligible-not-named for separate register-event; see §5 OBSERVATION 5). NOT a sealed-corpus errata trigger by itself. |
| `PHASE4_PLAN.md §1.4:43-50` | 10 bps taker + 5 bps slippage = 15 bps/side base | "Binance VIP 0 spot taker, no BNB discount" | Confirmed: Binance Spot VIP-0 taker = 0.100% = 10 bps per side (per https://www.binance.com/en/fee/schedule official schedule, accessed 2026-05-17) |

**The discrepancy is a venue-attribution mismatch:**

- The canonical project data layer is **BTC/USDT 1h SPOT** (Binance Vision spot history per CLAUDE.md "What This Project Is" + `data/raw/btcusdt_1h.parquet`).
- Phase 0-1's cost model in `config/execution.yaml` labels its 4bps taker as "Binance perpetual futures, VIP 0" — i.e., the cost-model label belongs to futures execution venue.
- Phase 4's cost model in `PHASE4_PLAN.md §1.4` labels its 10bps taker as "Binance VIP 0 spot taker" — i.e., the cost-model label belongs to spot execution venue.
- Both labels are externally accurate for their respective venues.
- **Phase 0-1 applied a futures-context cost label to spot-context data.** Phase 4 used a spot-context cost label on the same spot-context data.

**Substantive characterization:** the §2.1 observation is NOT "two contradictory numbers within a single venue context." It is a **venue-attribution mismatch across project phases applied to a consistent (spot) data layer.**

This resolves the §2.1 reconciliation question: the two numbers do not contradict each other in any deep sense; they describe two different things. The substantive question that surfaces in their place is "which venue's cost model is appropriate for the project's research goals" — a question explicitly out of scope for this cycle (§1.2; §5 OBSERVATION 4).

---

## §3 Cost-Regime Reconciliation (Sub-Question of §2)

**§3.1 Per-venue cost decomposition (verified at Cadence 1):**

| Venue | Taker fee (VIP-0, no BNB) | Taker fee (VIP-0, with BNB 25% disc) | Slippage assumption | Per-side total |
|-------|---------------------------|--------------------------------------|---------------------|----------------|
| Binance Spot | 10 bps | 7.5 bps | 1-3 bps typical / 5-10 bps stressed (Cadence 1 §sub-task 4) | 11-15 bps typical / 15-20 bps stressed |
| Binance Futures USDT-M | ~4-5 bps | ~3-4 bps (with BNB) | (project literature does not separately analyze) | ~7-10 bps (futures slippage may differ; not analyzed in this cycle) |

**§3.2 Slippage estimate for BTC/USDT spot at Phase 4 PLAN position size ($1,000 nominal):**

Per Cadence 1 sub-task 4 literature review (bounded desk-research, no L2 replay; **specific numerical bounds are literature-grounded heuristics, NOT empirically verified against L2 order book reconstruction or transaction-tick data**):
- BTC/USDT spot bid-ask spread on Binance: typically ≤0.01% (≤1 bps) in normal liquidity conditions — source: general microstructure descriptions in CoinAPI order book documentation; not a specific paper measurement
- $100k retail order: ~5 bps slippage cited in retail trading guides (Bitget Academy) for liquid-market conditions — heuristic, not source-anchored to a specific empirical study
- $1k retail order (Phase 4 PLAN size): falls in deep-book / tight-spread region; **literature-bounded heuristic estimate 1-3 bps typical** (extrapolated from the smaller order-size scaling implied by the $100k benchmark + tight-spread regime; NOT directly measured at this size)
- Stressed/high-volatility regime: **bounded ceiling 5-10 bps as conservative inference** drawn from volatility transmission literature (Aoyagi & Hattori arxiv:2107.00298 general framing) — NOT a specific bound from any cited paper
- Phase 4 PLAN's fixed 5 bps slippage assumption: comparison framing only (sits at upper end of typical heuristic range); not a source-anchored claim about correctness

**Methodology disclosure**: per METHODOLOGY_NOTES §1 (empirical verification for factual claims), the slippage numbers above are explicitly labeled as desk-research heuristics rather than empirically verified bounds. A precise empirical bounding would require L2 order book replay or transaction-tick analysis, both of which are explicitly out of scope per §0 trip-wire. These heuristics suffice for §2.1 reconciliation framing but should NOT be cited as precise bounds in downstream registers.

**§3.3 Reconciliation summary:**

Phase 0-1's 7 bps research-time per-side cost = correct internal arithmetic for a futures-context VIP-0 taker (4bps) + plausible futures-slippage (3bps). Phase 4's 15 bps per-side cost = correct internal arithmetic for a spot-context VIP-0 taker (10bps) + literature-conservative slippage (5bps). Neither computation is numerically wrong; they apply to different venues.

The "research-time 7 bps" label, as used in Phase 4 PLAN §1.4 dual-reporting ("research-time 7 bps per side substantively below realistic floor"), inherits Phase 0-1's futures-context value but presents it as a comparator within a spot-context analysis. This is descriptive of project history (Phase 0-1 cost model was futures-labeled), not a statement about deployable cost in spot venue.

---

## §4 Sub-Task Verifications (Cadence 1 Grounding Citations)

**§4.1 Sub-task 1: External Binance fee schedule**

- Primary source: https://www.binance.com/en/fee/schedule (official, accessed 2026-05-17)
- Findings: Spot VIP-0 taker/maker = 0.100% (10 bps); BNB 25% discount → 0.075% (7.5 bps); VIP-1 threshold = ≥$1M 30-day volume + ≥5 BNB
- Secondary cross-references (futures rates): TradersUnion + Bitget Academy + CoinPath — Binance perpetual futures USDT-M VIP-0 taker ≈ 4-5 bps; maker ≈ 2 bps
- Status: **VIP/BNB-baseline-bounded.** Cycle scope did not require expansion to tier-tree (VIP-2+ rates not analyzed; not necessary for §2.1 reconciliation).

**§4.2 Sub-task 2: 4bps source tracing**

- Source: `config/execution.yaml:42-53`
- Verbatim relevant block (read at Cadence 1):
  ```yaml
  # Fee structure (Binance perpetual futures, VIP 0)
  maker_fee_bps: 2.0
  taker_fee_bps: 4.0
  default_fee_bps: 4.0
  slippage_bps: 3.0
  ```
- Label is unambiguous: "Binance perpetual futures, VIP 0"
- File-level metadata: "Last reviewed: 2026-04-15"
- **External rate comparison (NOT exact match):** Current externally-published Binance USDⓈ-M VIP-0 futures taker is ~5 bps (0.0500% per official schedule at https://www.binance.com/en/fee/schedule); ~3.75 bps with BNB 25% discount. The sealed 4 bps project value falls between these and may reflect a historical schedule, partial BNB discount, referral-tier adjustment, or estimation. Exact provenance of the 4 bps choice is NOT traced in this cycle.
- Cross-venue applicability: the config file does not explicitly state whether this cost model is intended for spot or futures execution at runtime; the venue label in the comment suggests futures but the project's canonical data is spot
- Status: **traced-cleanly with material observation** (venue label belongs to futures; project data is spot — see §2). 4 bps numerical value provenance is eligible-not-named for separate register-event per §5 OBSERVATION 5.

**§4.3 Sub-task 3: 10bps source tracing**

- Source: `docs/phase4/PHASE4_PLAN.md §1.4:42-50`
- Verbatim relevant block (read at Cadence 1):
  > "Taker fee: 10 bps per side (Binance VIP 0 spot taker, no BNB discount; conservative retail profile; verify at fire-time against Binance published fee schedule). Slippage: 5 bps per side fixed (no L2 order book modeling at MVD scope). Per-side base case: 15 bps; round-trip: 30 bps."
- Justification cited in §1.4: "research-time 7 bps per side substantively below realistic floor (Binance VIP 0 taker = 10 bps alone). Population→strategy register transition per PHASE2C_15 closeout requires realistic costs to ground deployable-alpha-class claims."
- Numerical agreement: 10 bps matches Binance Spot VIP-0 taker (verified §4.1)
- Status: **traced-cleanly**

**§4.4 Sub-task 4: BTC/USDT spot taker slippage literature**

- Primary references:
  - https://www.coinapi.io/blog/binance-order-book-snapshots-explained — Binance BTC/USDT order book spread observations
  - https://www.bitget.com/academy/btc-usdt-trading — retail-size slippage estimates
  - https://arxiv.org/pdf/2107.00298 — "The Role of Binance in Bitcoin Volatility Transmission"
  - https://www.tandfonline.com/doi/full/10.1080/1350486X.2022.2080083 — Fragmentation, Price Formation and Cross-Impact in Bitcoin Markets
- **Heuristic bounds (NOT empirically verified)**: 1-3 bps typical / 5-10 bps stressed for $1k retail BTC/USDT spot taker orders — both bounds are literature-grounded heuristics drawn from general microstructure descriptions, NOT direct measurements from a specific empirical study. See §3.2 methodology disclosure.
- Phase 4 PLAN's 5 bps fixed slippage assumption: comparison framing only (sits at upper end of heuristic typical range); not a source-anchored claim about correctness
- Status: **bounded-heuristic-estimate-obtained** (downgraded from bounded-estimate label per Codex F3 MAJOR adjudication); no simulation / L2 / API / batch / sealed-corpus modification required. Empirical bounding (e.g., L2 replay) would require separate register-event per §0 trip-wire.

---

## §5 Implications (Observations, NOT Adjudicated Conclusions)

The following observations are **named** per anti-pre-naming binding from §10 sub-§§. They are **NOT adjudicated** in this cycle. Each is eligible-not-named for separate Charlie register-event boundary.

**OBSERVATION 1: Path 1 W4-scoped paper trading interpretive basis (eligible-not-named)**

The Phase 5.1 §6 classification of Stratum A as D-I ("salvageable-under-research-time-cost-assumption-as-defined") and the §7.1 Path 1 framing as "paper trading on Stratum A at research-time 7bps cost basis, W4-constrained" both inherit the "research-time 7 bps" basis from `config/execution.yaml`'s futures-labeled cost model (per §2 + §4.2 of this note). The interpretive question — whether "salvageable at 7 bps" retains operational meaning given that 7 bps applies to a futures-context cost model rather than the spot-context data layer — is eligible for re-examination at a separate Charlie register-event boundary, NOT adjudicated in this note.

**OBSERVATION 2: Path 2 full L2 replay marginal-value (eligible-not-named)**

Path 2 (per Phase 5.1 §7.1 + §3.3 brainstorming handoff) was framed as "extended real-cost-discovery via external Binance fee schedule reference + L2 order book replay + paper trading cost calibration + microstructure analysis," with associated one-time L2 historical data acquisition cost estimated at $50-500+ (Tardis.dev or equivalent). Cadence 1 of this cycle obtained: (a) external Binance public fee schedule (§4.1), (b) bounded microstructure literature slippage estimate (§4.4), (c) cross-source venue reconciliation (§2-§3). The marginal-value question — what L2 replay would add beyond what is now in hand from desk-research grounding — is eligible for re-examination at a separate Charlie register-event boundary, NOT adjudicated in this note.

**OBSERVATION 3: Stratum A D-I label re-interpretation under venue-clarified cost basis (eligible-not-named)**

Phase 5.1 §6.1 classified Stratum A as D-I via the binary criterion "meets-7=17/22 AND fails-15=11/22" at the §3.2 Step B threshold. The 7 bps threshold inherits the venue-mismatched cost-model assumption per OBSERVATION 1. Re-interpretation under explicit venue framing (spot 15 bps, futures ~7 bps) is eligible for separate Charlie register-event boundary, NOT adjudicated in this note.

**OBSERVATION 4: Execution-venue policy / project-level venue definition (eligible-not-named)**

The execution-venue commitment question — spot (matches canonical data layer), futures (matches `config/execution.yaml` venue label), both, or deferred — is the load-bearing project-architectural decision that surfaces from the §2.1 reconciliation. Affects every Phase 0+ backtest and every Path 1/2/3 successor formulation. Out of scope for §2.1-reconciliation-lite per §1.2; eligible-not-named for separate Charlie register-event boundary; NOT adjudicated in this note.

**OBSERVATION 5: `config/execution.yaml` venue-label vs data-layer mismatch as sealed-corpus errata candidate (eligible-not-named)**

The `config/execution.yaml` cost-model section carries a venue label ("Binance perpetual futures, VIP 0") that does not match the canonical data layer (Binance Vision spot history). Whether this constitutes sealed-corpus errata requiring formal correction at a separate register-event, OR is correctly understood as a historical artifact of Phase 0-1's cost-model design intent (futures-context cost model used as conservative proxy on spot data), is eligible for separate Charlie register-event boundary, NOT adjudicated in this note. Per CLAUDE.md HARD CONSTRAINTS, `config/execution.yaml` modification requires explicit human approval — this is preserved.

**OBSERVATION 6: Phase 5.1 §7.2 carry-forward resolution status (eligible-not-named)**

This note **proposes resolution** of the §2.1 cross-source composition observation per Phase 5.1 §7.2 #1 carry-forward (pending V3 SEAL) — the observation is now characterized (as venue-mismatch, not contradiction) and the operational/architectural implications are named per OBSERVATIONS 1-5 above. Upon V3 SEAL, this note formalizes the proposed resolution; until SEAL, the resolution remains draft-state. Whether Phase 5.1's §7.2 forward-only carry-forward should be marked "resolved" at sealed corpus (post this note's SEAL), OR retained for ongoing reference, is eligible for separate Charlie register-event boundary. Per CLAUDE.md HARD CONSTRAINTS preservation of sealed-corpus invariance, no modification to PHASE5_1_COST_MODEL_INVESTIGATION_NOTE is performed in this cycle.

---

## §6 Branch-Criterion Proposal (Structure, NOT Answer)

The Phase 5.1 §3.3 sequencing decision authorized §2.1-lite → formal branch register-event at closeout → [Path 1 W4-scoped OR full Path 2 mandatory] → Path 3. The original branch criterion phrasing was "7-15bps band → Path 1; >15bps → full Path 2."

**§6.1 Branch criterion structural decomposition:**

Cadence 1 grounding + §2 venue-mismatch finding reframes the branch criterion from a single-axis cost-magnitude question into a **conditional decomposition on venue commitment** (OBSERVATION 4):

```
IF project commits to spot execution (matching canonical data layer):
  realistic cost basis = ~15 bps per side (10 bps spot taker + 5 bps slippage; §3.3)
  THEN branch decision: realistic cost is bounded by Cadence 1 desk research
    Path 2 full marginal value question (OBSERVATION 2) → resolution
    Path 1 W4 interpretive basis question (OBSERVATION 1) → resolution under spot-venue framing
    Stratum A D-I re-interpretation question (OBSERVATION 3) → resolution under spot-venue framing

IF project commits to futures execution (matching config/execution.yaml venue label):
  realistic cost basis = ~7-10 bps per side (4-5 bps futures taker + slippage TBD via separate analysis)
  spot-data appropriateness as futures-backtesting proxy = open question (eligible-not-named)
  THEN branch decision: cost basis approximately matches Phase 0-1 research-time
    Path 1 W4 interpretive basis question (OBSERVATION 1) → potentially resolved as "salvageable claim retains operational meaning"
    Path 2 full marginal value question (OBSERVATION 2) → may require different scope (futures L2 replay, not spot)

IF project considers both venues (or defers venue commitment):
  branch decision requires sub-axis: per-venue cost basis + per-venue strategy applicability
  Path 1/2/3 each need per-venue formulation
```

**§6.2 What this proposal does NOT name:**

- Which conditional branch should fire (depends on OBSERVATION 4 venue policy register-event)
- What specific cost threshold should operationalize "Path 1 viable" vs "Path 2 mandatory" within each conditional
- Whether the venue commitment register-event should precede or co-occur with the branch register-event

**§6.3 Recommended sequencing at closeout register-event:**

At Phase 5.2 closeout, Charlie's branch register-event has two structural sub-decisions to make (in dependency order):

1. **Venue commitment register-event** (corresponds to OBSERVATION 4): decide whether the project commits to spot execution / futures execution / both / defers commitment
2. **Branch register-event** (downstream of #1): given the venue commitment from #1, decide which §3.3 path to fire — Path 1 W4-scoped (and what W4 means under the venue-clarified basis), full Path 2 (and at what scope), Path 3, or some combination

These may be the same register-event or separate. This note does not pre-name the sequencing.

**§6.4 Branch register-event resolution paths (named per anti-pre-naming + eligible-not-named):**

- **Branch.A**: IF Charlie's venue commitment register-event resolves to **spot execution** (matching canonical data layer) → realistic cost basis is **fee-schedule-anchored at 10 bps spot taker per §3.1 plus heuristic slippage component per §3.2 (literature-grounded heuristic, NOT empirically verified)**, total ≈ 15 bps per side at upper end of heuristic range. Within Branch.A, Charlie determines (each separately eligible-not-named):
  - Whether Path 1 paper trading proceeds at spot-realistic basis, at the venue-corrected research-time basis, or is rescoped or invalidated
  - Whether Path 2 marginal value warrants L2 replay infrastructure given desk-research bounds in hand
  - Whether Stratum A D-I classification is preserved, re-interpreted, or invalidated under spot-venue framing
- **Branch.B**: IF Charlie's venue commitment register-event resolves to **futures execution** (matching `config/execution.yaml` venue label) → realistic cost basis is **fee-schedule-anchored at ~5 bps current published Binance USDⓈ-M VIP-0 futures taker per §3.1, with futures slippage component unresolved/TBD (no futures-specific slippage literature was reviewed in this cycle; see §2 table caveat on 4 bps sealed value vs current published rate)**. Within Branch.B, Charlie determines (each separately eligible-not-named):
  - Whether the spot-data layer is appropriate as a futures-execution proxy (separate sub-question)
  - Whether Path 1 W4 framing is preserved, re-scoped, or invalidated under futures-venue framing
  - Whether Path 2 scope requires re-formulation (e.g., futures-context L2 replay)
  - Whether Stratum A D-I classification is preserved, re-interpreted, or invalidated under futures-venue framing
- **Branch.C**: IF Charlie's venue commitment register-event resolves to **both venues** OR **defers commitment** → Charlie determines per-venue formulations for Path 1/2/3 successor paths; per-venue cost basis applies separately (~15 bps spot, ~5-10 bps futures); per-venue Stratum classification may differ
- **Branch.D**: IF Charlie specifies **an alternative venue commitment framing** not covered by A/B/C → Charlie determines the alternative structure (e.g., non-Binance venue, mixed execution layer, deferred-to-future-cycle, etc.)

Each Branch.X is eligible-not-named; this note proposes the STRUCTURE for adjudication, not the answer. **No directional claim** is made about which Path 1/2/3 outcomes are "likely" within any branch — each sub-decision within each branch is independently Charlie-determined at the venue commitment register-event or downstream register-events.

---

## §7 V# Anchor Chain (Phase 5.2)

| V# | State | Description |
|----|-------|-------------|
| V1 | ARCHIVED | DRAFT (pre-reviewer-round) |
| V2 | ARCHIVED | Post-reviewer-round revised draft (7 ADOPT + 1 PUSHBACK adjudication applied: Codex F1 BLOCKING §6.4 rewrite, F2/F3 MAJOR hedging, F4 MINOR "resolves" softening, Advisor F2 line-range correction, F3 subsumed, F4 partial-ADOPT OBSERVATION 4 tightening; Advisor F1 PUSHBACK on hallucinated phrase). |
| V3 | ARCHIVED | Post-PFR-scoped re-review (2 ADOPT + 1 PUSHBACK PFR adjudication applied: Codex NF1 MAJOR §6.4 "empirically anchored" → "fee-schedule-anchored plus heuristic slippage" softening, Codex NF2 MINOR §9 line-range correction 42-49 → 42-53; Advisor PFR NF1 PUSHBACK on hallucinated "Kyle (1985) / AMH literature" citation). |
| **V4** | **SEAL** | **Canonical sealed artifact (Cadence 2 deliverable seal + closeout register-event boundary; venue commitment + branch decision are SEPARATE future Charlie register-events per SEAL-only authorization).** |

V# anchor chain for Phase 5.2 is intentionally lighter than Phase 5.1 (V1-V14) reflecting Bucket-1 single-deliverable + narrower scope.

**Advisor F1 PUSHBACK rationale (recorded for audit-trail):** Advisor F1 cited a specific phrase ("The 3bps slippage component in the research-time model plausibly underestimates...") at §5 OBSERVATION 2 as anti-pre-naming language drift. Direct V1 DRAFT verification confirmed the cited phrase does NOT appear anywhere in V1 DRAFT — Advisor's finding was mis-grounded against a hallucinated sentence. Underlying anti-pre-naming concern in §5 was independently checked against actual V1 DRAFT OBSERVATIONS 1-5 and found clean (all use "eligible for re-examination ... NOT adjudicated" framing); the genuine anti-pre-naming violation in §6.4 was caught separately by Codex F1 BLOCKING and is addressed in V2. Per [`feedback_reviewer_suggestion_adjudication.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md) "don't bulk-accept; reason through each," PUSHBACK on Advisor F1 is appropriate; not applying a fix for a non-existent defect.

---

## §8 Reserved Decisions (Anti-Pre-Emption)

Per §10 sub-§§ anti-pre-emption invariant — no decision pre-named in this cycle. Reserved decisions for separate Charlie register-event boundary:

1. Whether Path 1 W4 interpretive basis (OBSERVATION 1) is preserved, re-scoped, or invalidated under venue-clarified framing
2. Whether Path 2 full L2 replay (OBSERVATION 2) retains marginal value, is re-scoped, or is deferred
3. Whether Stratum A D-I label (OBSERVATION 3) is re-interpreted, retained, or invalidated
4. Execution-venue policy decision (OBSERVATION 4) — spot / futures / both / defer
5. `config/execution.yaml` venue-label correction (OBSERVATION 5) — errata register-event or historical-artifact-acknowledgment
6. Phase 5.1 §7.2 carry-forward marking (OBSERVATION 6) — resolved / retained / both
7. Sequencing of venue-commitment register-event vs branch register-event (§6.3) — co-occur / sequential / deferred
8. Phase 5.2 closeout SEAL timing and Phase Marker update (deferred to closeout register-event)
9. Phase 5.2 successor cycle entry framing (Path 1 / Path 2 / Path 3 / combinations) — deferred per §6.4 Branch.X resolution
10. Other Charlie-specified reserved decisions

---

## §9 References

**Sealed project artifacts (read-only at this cycle):**
- `config/execution.yaml` (lines 42-53 cited; HARD CONSTRAINTS protect from modification without explicit human approval)
- `docs/phase4/PHASE4_PLAN.md` §1.4 (cited; sealed at sub-spec drafting cycle SEAL register-event boundary)
- `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` §2 + §2.1 + §6 + §7 + §9 (cited; sealed at Phase 5.1 SEAL register-event boundary)
- `CLAUDE.md` Phase Marker section + §10 sub-§§ codified discipline (referenced)

**External public sources (declared per V12-analog scope-verification anchor):**
- https://www.binance.com/en/fee/schedule (Binance official fee schedule; accessed 2026-05-17)
- https://tradersunion.com/brokers/crypto/view/binance/fees/ (TradersUnion Binance fees summary)
- https://bc-binance.com/en/posts/binance-fee-rates/ (CoinPath Binance fee rates)
- https://www.binance.us/fees (Binance.US fee schedule reference)
- https://www.bitget.com/academy/btc-usdt-trading (Bitget Academy BTC/USDT trading guide)
- https://www.coinapi.io/blog/binance-order-book-snapshots-explained (CoinAPI Binance order book snapshots)
- https://arxiv.org/pdf/2107.00298 (Aoyagi & Hattori, "The Role of Binance in Bitcoin Volatility Transmission")
- https://www.tandfonline.com/doi/full/10.1080/1350486X.2022.2080083 ("Fragmentation, Price Formation and Cross-Impact in Bitcoin Markets")

**End of V4 SEAL.** Phase 5.2 §2.1-reconciliation-lite Bucket-1 investigation cycle SEALED at this register-event boundary. Cycle resolved §2.1 cross-source composition observation as **venue-mismatch (NOT 4-vs-10 contradiction)** — both numbers externally accurate within their respective venues (4bps = Binance perpetual futures VIP-0 taker per `config/execution.yaml`; 10bps = Binance spot VIP-0 taker per `PHASE4_PLAN.md §1.4`); canonical project data layer is BTC/USDT 1h SPOT; Phase 0-1 cost model applied futures-context fee labels to spot-context data. Six OBSERVATIONS (§5) named anti-pre-naming + eligible-not-named for separate Charlie register-event boundaries; four Branch.A/B/C/D structures (§6) proposed without pre-naming answers. Memory codification (Option II citation verification discipline) applied at register #10. **NO git tag at SEAL** per CLAUDE.md "Bucket-1 investigation note ≠ arc-level closeout" Tag policy + Phase 5.1 precedent. Phase Marker + atomic `docs/phase_marker_history.md` update follow at SEAL bundle.

**Reviewer routing empirical observations from this cycle** (codified to memory at register #10): 2/9 advisor (`quant-research-advisor`) hallucination rate (V1 round F1 + PFR round NF1, both verified via grep); 2/9 Codex stall rate (across earlier session cycles, none in this cycle's 4 Codex dispatches — 6 consecutive normal Codex runs through SEAL). Cross-model diversity routine retains positive value with citation verification discipline operationally enforced per [[feedback_reviewer_suggestion_adjudication]] "Citation verification discipline" section.
