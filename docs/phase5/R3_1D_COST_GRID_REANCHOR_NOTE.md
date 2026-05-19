# R3_1D_COST_GRID_REANCHOR_NOTE.md

**Canonical artifact for Phase B Pre-Sequence Roadmap V3 register-event R3.1d (Template B Bucket-1 investigation note; structural analog to PHASE5_1_COST_MODEL_INVESTIGATION_NOTE, PHASE5_2_VENUE_RECONCILIATION_NOTE, PHASE5_A_CLARIFICATION_NOTE, R1_2_IS_OOS_RANK_CORRELATION_NOTE, R3_1A_VENUE_INFRASTRUCTURE_NOTE, R4_1_PHASE_B_VENUE_COMMITMENT_NOTE).**

**Status:** V_SEAL (sealed at register-event boundary 2026-05-19 per Charlie register "接受 6 个 V3.5 patches + 接受最终 V_SEAL register text + Fire V_SEAL register"). Sub-decision locks (SD1-SD9 + 7 mechanical patches P1-P7) landed at "ratify all" 2026-05-18. V1 → V2 applied 9 ADOPT patches; V2 → V3 applied 3 ADOPT patches per Codex V2 BLOCKING fix (path-based mapping replaces non-injective fee_model_label); V3 → V_SEAL applied 6 V3.5 patches (V3.5-PD BLOCKING removes fabricated BH-FDR + R1.2 §6 cross-reference traced to propagated Advisor hallucination, replaces with FWER-only language; V3.5-PE broadens Tier 6 instrument language; V3.5-PF advisor agent anti-push framing (audit-trail; out-of-repo); V3.5-PG adds CLAUDE.md HARD CONSTRAINT reference in V_SEAL register; V3.5-PH SD9 item 4 "deferred"→"eligible" + architecture-conditional qualifier; V3.5-PI advisor agent + memory file → audit trail not staged per METHODOLOGY_NOTES §32). Final V_SEAL register text locked per Charlie ratify; SD9 Tier 5 gate = Option A (holdout_sharpe > 0 strict at 15 bps/side); Tier 6 gate REQUIRED multiplicity correction (FWER-class) at R6.1.

---

**Trigger:** R4.1 SEAL (2026-05-18; commit `3ff085e` SEAL artifacts + `7a63516` Phase Marker advance) formally committed Branch.A (SPOT execution) per Phase 5.2 §6.4 corrected semantics, elevating R3.1a working-assumption status to formal venue commitment. R4.1 §6 + R3.1a §12 Errata appendix explicitly named R3.1d cost-grid re-anchor as eligible-not-named for separate Charlie register-event per X8. Charlie session-close lock 2026-05-18 named R3.1d as next register-event. Cycle entry register "1 → 3 → 4 with conservative-anchor synthesis approved, R3.1d fire authorized" fires R3.1d under formal Branch.A SPOT context.

**Scope binding (Charlie-locked pre-draft):**

| # | Locked content | Source register |
|---|---|---|
| 1 | Sequencing 1 → 3 → 4 (R3.1d → Tier 2 → Tier 5/6) | "approved 1→3→4" 2026-05-18 |
| 2 | Anchor framework = conservative anchor at upper end of realistic range (NOT preserve-7bps; NOT midpoint estimate; NOT non-anchor grid-only) | "conservative-anchor synthesis approved" 2026-05-18 |
| 3 | R3.1b/c deferred until Phase 4 paper-trading infrastructure deploys; non-foreclosed | Prior adjudication 2026-05-18 |
| 4 | Tier 5/6 gated behind R3.1d + Tier 2 SEAL | Prior adjudication 2026-05-18 |
| 5 | Cycle entry = R3.1d cost-grid re-anchor (Bucket-1 investigation) | "R3.1d fire authorized" 2026-05-18 |
| 6 | SD1-SD9 + 7 mechanical patches P1-P7 (per §1 lock table) | "ratify all" 2026-05-18 |

**Charlie register chain (R3.1d cycle through V_SEAL):**

| # | Charlie register | Decision |
|---|---|---|
| 1 | "1 → 3 → 4 with conservative-anchor synthesis approved, R3.1d fire authorized" | Cycle entry — framework + sequencing locked |
| 2 | "dispatch 2-leg reviewer round to gather thoughts, then we adjudicate and decide" | Sub-decision Round 1 reviewer dispatch (2-leg subagent: codex:codex-rescue + quant-research-advisor parallel; BL-Y-refined blind-lean Phase 1) |
| 3 | "PFR cross-validation round dispatch" | Sub-decision PFR cross-validation dispatch (2-leg subagent parallel) |
| 4 | "ratify all" | SD1-SD9 + 7 patches P1-P7 locked |
| 5 | "fire V1 draft, then dispatch reviewer round, i will review it while reviewer work in parallel" | V1 draft fire + V1 reviewer dispatch authorize |
| 6 | "cancel and kill, then rerun blind lean for codex and advisor review freshly. so we can verify the hallucination issue." | V1 round Codex stall recovery + fresh re-dispatch for hallucination diagnostic |
| 7 | "Apply V2 patches + 进入 V2 reviewer round + Memory codification investigation" | V1 adjudication ratify + V2 patch application + V2 reviewer dispatch + memory codification fire |
| 8 | "接受 V3-PA path-based mapping + V3-PB + V3-PC + PFR rule-Y trigger + Apply V3 patches + PFR dispatch" | V2 adjudication ratify + V3 patch application + V3 PFR dispatch authorize |
| 9 | "Apply V2 patches" through "PFR dispatch" + "dispatch to reviewer round for final review before fire seal" + "i mannually changed quant-research-advisor.md model to opus" | V3 PFR ratify + final pre-SEAL reviewer round + agent model manual upgrade |
| 10 | "接受 6 个 V3.5 patches + 接受最终 V_SEAL register text + Fire V_SEAL register" | V_SEAL register fire — SD9 criterion lock (Option A at Tier 5; FWER multiplicity REQUIRED at Tier 6 R6.1) + atomic SEAL bundle commit |

**§0 scope-bleed trip-wire status:** clean. Cycle work bounded to conservative cost-anchor commitment + companion artifact specifications + SD9 deferred criterion options menu + attrition sensitivity analysis from existing Phase 4 holdout artifacts (no new backtests). NO new engine runs. NO API spend. NO new data acquired. NO numeric change to `config/execution.yaml` (sidecar pattern per SD2-D). R3.1b/c remains eligible-not-named pending Phase 4 paper-trading infrastructure deployment.

---

## §1 Locked sub-decisions (sub-decision register sealed 2026-05-18 at "ratify all")

| SD | Locked option | Substance | Mechanical patches applied |
|---|---|---|---|
| SD1 | A | 15 bps/side (30 bps round trip) committed as conservative anchor | — supplementary sensitivity reporting at 13 bps and 17 bps bands |
| SD2 | D | Sidecar config pattern (NOT modify main `config/execution.yaml`) | P1: alias config `config/execution_phaseb_spot_15bps.yaml` (copied YAML with distinct Phase B header, same `cost_model` body as `execution_phase4_15bps.yaml`, separate SHA256). P2: anchor id `spot_realistic_15bps_v1` as new schema column `cost_anchor_id TEXT` in `experiment_registry.runs` table. |
| SD3 | D | Tiered Pillar 1 policy (archival grandfathered + new Tier 5 conservative-anchor gate as HARD CONSTRAINT) | P3: HARD CONSTRAINT wording in CLAUDE.md = placeholder ("criterion per SD9 V_SEAL lock") until SD9 locked. |
| SD4 | A | Bundle R4.1 hygiene patches into R3.1d SEAL atomically | P4: 2-sentence editorial provenance note in §5.4 explaining why bundling here. |
| SD5 | B | Separate register-event for R2.1 audit-criterion pre-commit (Tier 2 sub-task; NOT bundled into R3.1d) | — |
| SD6 | A | Explicit R3.1b/c non-foreclosure with Phase 4 paper-trading trigger condition (§8) | — |
| SD7 | A | Bucket-1 Template B at `docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md` (THIS file) | — |
| SD8 | A | 2-leg subagent default (codex:codex-rescue + quant-research-advisor) for V1 + subsequent rounds | — |
| SD9 | NEW | HARD invariant locked NOW ("no Tier 5 promotion without conservative-anchor pass"); exact criterion deferred to V_SEAL register lock | P5: V1 surfaces SD9 criterion options as explicit numbered menu (§7) with attrition data embedded (anti-rubber-stamp guard); V_SEAL adjudicates pre-framed options. |
| — | + V1 attrition table | Attrition-rate sensitivity from existing Phase 4 forward-window holdout artifacts (no new backtests) | P6: label "Phase 4 forward-holdout attrition" (not "Tier 5 expected survival"; representativeness caveat). P7: N + 95% Clopper-Pearson binomial CI per band + explicit post-hoc selection pre-commitment + 1-2 paragraph analysis cap. |

**Reviewer reliability data at V2 patch application (cumulative across R3.1d cycle through V1 fresh redispatch):** **0/3 Codex hallucinations** across 3 dispatches (sub-decision Round 1 + sub-decision PFR + V1 fresh; V1 original killed at stall before output) + **9/12 verified Advisor hallucinations = 75% rate** across 4 dispatches (Round 1: SD4 verification false-claim "no PENDING in R4.1 doc"; PFR: false-claim "line 5 V_SEAL SEALED"; V1 original: §6 numerics 29/8/7/5 fabrication + §7 Option E "multi-period stability" fabrication + Phase 4 dir existence false-claim; V1 fresh redispatch: §6 numerics 22/18/16/14 fabrication + by-theme "trend" theme fabrication + theme pass-rates fabrication + "mean_reversion most cost-sensitive" mischaracterization). All Advisor hallucinations Mode A (file:line/exact-quote/numerical-content errors); PUSHBACK applied via citation verification discipline; ground-truth data independently re-verified. **Mandatory verification mandate in dispatch brief did NOT eliminate hallucinations** — structural pattern, not prompt-fixable. Cumulative Reading 3 pilot stats post-R3.1d V1 fresh redispatch: **~4% Codex stalls + ~2% Codex hallucinations + ~30-40% Advisor hallucinations cumulative across pilot** (this cycle's 75% rate is elevated data point reinforcing prior trend). Memory codification investigation registered as concurrent task per Charlie register row 7.

---

## §2 Conservative anchor commitment

### §2.1 What "conservative anchor" means at R3.1d

Per Charlie session-close framing 2026-05-18 + cycle entry register 2026-05-18, "conservative anchor at upper end of realistic range" excludes three alternative postures:
1. **Preserve 7 bps/side (current `effective_7bps_per_side`)** — under-estimates SPOT-realistic cost; Phase B Tier 5 promotion would inherit research-time cost simplification as deployable gate, violating R4.1 formal SPOT commitment intent
2. **Midpoint estimate (~10-11 bps/side)** — anchors at fee-schedule mid; loses safety margin against slippage uncertainty
3. **Non-anchor cost-grid only** — analysis cycle, not decision cycle; would not unblock Tier 5/6 (Advisor PFR Dissent 3 framing)

Conservative anchor = single committed point estimate at the **upper end of the heuristic realistic range** per Phase 5.2 §6.4 Branch.A definition, with sensitivity reporting at adjacent bands. R3.1d SEALS this anchor as Phase B Tier 5/6 evaluation basis (NOT as a venue-accurate execution simulator — that role remains R3.1b/c empirical measurement, deferred per §8).

### §2.2 Why 15 bps/side (verified dual sealed-source backing)

The conservative anchor commits to **15 bps per side = 30 bps round trip**, derived from two independent sealed-source converging anchors:

**Source 1: Phase 5.2 §6.4 Branch.A definition** (`docs/phase5/PHASE5_2_VENUE_RECONCILIATION_NOTE.md` line 263, verified at draft):
> "Branch.A: IF Charlie's venue commitment register-event resolves to **spot execution** (matching canonical data layer) → realistic cost basis is **fee-schedule-anchored at 10 bps spot taker per §3.1 plus heuristic slippage component per §3.2 (literature-grounded heuristic, NOT empirically verified)**, total ≈ 15 bps per side at upper end of heuristic range."

**Source 2: Phase 4 PLAN §1.4 sealed cost basis** (cited in `PHASE5_2_VENUE_RECONCILIATION_NOTE.md` line 170, verified at draft):
> "Taker fee: 10 bps per side (Binance VIP 0 spot taker, no BNB discount; conservative retail profile; verify at fire-time against Binance published fee schedule). Slippage: 5 bps per side fixed (no L2 order book modeling at MVD scope). Per-side base case: 15 bps; round-trip: 30 bps."

**Source 3: Existing Phase 4 holdout config family** (`config/execution_phase4_{07,13,15,17}bps.yaml` family verified extant): 15 bps/side is already-operationalized as `config/execution_phase4_15bps.yaml` with cost decomposition `taker_fee_bps: 10.0 + slippage_bps: 5.0`. SD2-D sidecar pattern leverages this directly via Phase B alias.

**Sanity check:** Per Phase 5.2 §3.1 cost decomposition table (line 118-119, verified): Binance Spot VIP-0 typical band is 11-15 bps/side; stressed band is 15-20 bps/side. 15 bps lands at the upper edge of "typical" and lower edge of "stressed" — the boundary between routine retail execution and adverse conditions. This is the operationally correct interpretation of "conservative anchor at upper end of realistic range."

### §2.3 Why not the rejected alternatives (13 / 17 / 20 / non-anchor)

- **13 bps/side (26 bps RT)** — middle of typical band; sub-conservative under Phase 5.2 §6.4 Branch.A "upper end" framing; existing `execution_phase4_13bps.yaml` retained for supplementary sensitivity reporting only
- **17 bps/side (34 bps RT)** — stressed-typical boundary; conservative beyond §6.4 anchor; existing `execution_phase4_17bps.yaml` retained for supplementary sensitivity reporting only
- **20 bps/side (40 bps RT)** — stressed upper bound; outside §6.4 "upper end of heuristic" framing; no existing Phase 4 config band; over-conservative relative to retail SPOT reality
- **Non-anchor cost-grid** — explicitly excluded by Charlie's "conservative-anchor synthesis approved" register; analysis without committed anchor does not unblock Tier 5/6 gate criterion

### §2.4 What R3.1d commits at 15 bps/side

The conservative anchor binds the following:
1. **Phase B Tier 5/6 candidate evaluation** runs at 15 bps/side via SD2 sidecar config
2. **HARD CONSTRAINT** (per SD3 + SD9): no Tier 5 promotion without conservative-anchor pass at 15 bps/side
3. **Anchor id `spot_realistic_15bps_v1`** in `experiment_registry.runs.cost_anchor_id` for forensic traceability
4. **Phase 1-2 research record** continues at 7 bps/side under `effective_7bps_per_side` (Pillar 1 tiered policy per SD3-D; §4 below)
5. **R3.1b/c eligible-not-named** (§8) as deferred empirical supersession path

What R3.1d does NOT commit:
- Tier 5 gate pass criterion specifics (deferred to V_SEAL register per SD9; options menu in §7)
- R3.1b/c scope or method (eligible-not-named; non-foreclosed)
- Path 1 / Path 2 / Stratum A D-I classification (eligible-not-named per R4.1 §6 + R3.1a §12.7)

---

## §3 Source verification (line-anchored citations; verified at V1 draft)

### §3.1 Current effective cost model (`config/execution.yaml`)

Verified content at V1 draft time:
- Line 42 (post-E.3 patched): `# Effective SPOT execution cost model (7 bps/side simplification; not venue-accurate; see CLAUDE.md Execution Convention §4)`
- Cost decomposition: `taker_fee_bps: 4.0`, `maker_fee_bps: 2.0`, `slippage_bps: 3.0` (effective 7 bps/side = 14 bps RT)
- `fee_model` registry field value: `effective_7bps_per_side`
- Post-E.3 canonical `config_hash`: `sha256:db2ce75bd41e8513` (3-file scope: execution.yaml + environments.yaml + schemas.yaml; 16-hex truncation per `compute_config_hash()` at `backtest/experiment_registry.py:188`)

### §3.2 Phase 5.2 §3.1 cost decomposition table (`docs/phase5/PHASE5_2_VENUE_RECONCILIATION_NOTE.md:118-119`)

| Venue | Taker fee (VIP-0, no BNB) | Slippage assumption | Per-side total |
|---|---|---|---|
| Binance Spot | 10 bps | 1-3 bps typical / 5-10 bps stressed | **11-15 bps typical / 15-20 bps stressed** |
| Binance Futures USDT-M | ~4-5 bps | (not analyzed) | ~7-10 bps |

15 bps/side = upper edge of "typical" SPOT taker total; lower edge of "stressed" — boundary anchor.

### §3.3 Phase 5.2 §6.4 Branch.A definition (line 263, verified)

Branch.A formal commitment fee anchor = "10 bps spot taker per §3.1 plus heuristic slippage component per §3.2 (literature-grounded heuristic, NOT empirically verified), **total ≈ 15 bps per side at upper end of heuristic range**."

### §3.4 Phase 4 PLAN §1.4 sealed cost basis (cited in PHASE5_2:170)

Quoted: "Taker fee: 10 bps per side ... Slippage: 5 bps per side fixed ... Per-side base case: 15 bps; round-trip: 30 bps."

This is the same numeric basis as Phase 5.2 §6.4 Branch.A, verified at independent doc / independent register-event.

### §3.5 Phase 4 forward-window holdout config family (verified at V1 draft)

Four operationalized cost-band configs at `config/execution_phase4_{07,13,15,17}bps.yaml`. Verified content of `execution_phase4_15bps.yaml`:
- Line 1-3 header comment: "Phase 4 realistic base cost. Per PHASE4_PLAN §1.4 (sealed at 432b2bd): 10bps Binance VIP 0 spot taker + 5bps slippage = 15bps per side. Round-trip: 30bps."
- Lines 5-9: "*** THIS CONFIG IS THE BASIS FOR PHASE 4 §1.5 SUCCESS CRITERION. *** Sensitivity bounds at 13bps (-2 slip) and 17bps (+2 slip) are auxiliary descriptive; success/failure of Phase 4's persistence test is evaluated at this 15bps basis only."
- Line 19: `cost_model.name: "phase4_realistic_base_15bps"`
- Line 21: `taker_fee_bps: 10.0`
- Line 23: `slippage_bps: 5.0`

### §3.6 R3.1a §4.1 historical origin (4 bps inspired by perpetual VIP-0)

Per R3.1a `docs/phase5/R3_1A_VENUE_INFRASTRUCTURE_NOTE.md` §4.1 (verified): "The 4bps taker fee + 3bps slippage decomposition was inspired by the Binance perpetual futures VIP 0 fee schedule (4-5bps taker at retail tier per Binance fee schedule referenced in Phase 5.2 §2 + §3) plus a 3bps slippage estimate." 4 bps was NOT calibrated to SPOT venue — the historical decomposition inherits a futures-context anchor applied to SPOT data.

### §3.7 R1.2 AMBIGUOUS verdict (`docs/phase5/R1_2_IS_OOS_RANK_CORRELATION_NOTE.md`)

Per R1.2 §2 + §6 (verified): "C.4 verdict: AMBIGUOUS (CI straddles 0)." Per R1.2 §7 OBSERVATION 1 (line 272-274, verified): "AMBIGUOUS verdict binds Phase B promotion HARDER per pre-bound rule... Phase B R5.1 candidate-subset commitment cannot claim the robust subset as 'stable' without additional evidence."

R1.2 AMBIGUOUS binds R3.1d sequencing: conservative anchor at 15 bps/side under R1.2-AMBIGUOUS conditions creates stacked validity hurdle for Tier 5 promotion — both cost realism AND IS-OOS rank stability must clear before a candidate proceeds.

### §3.8 R4.1 SEAL formal Branch.A commitment (`docs/phase5/R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md`)

R4.1 SEALED at commit `3ff085e` + Phase Marker advance `7a63516` (verified via `git log --oneline -5`). Formal Branch.A commitment = SPOT execution per Phase 5.2 §6.4 corrected semantics. R3.1a §7.2 inverted trigger logic table row 1 activated → R3.1a §12 Errata appended atomically → `config/execution.yaml` line 42 patched venue-agnostic. Pre-E.3 canonical `config_hash` `sha256:3850424a0ef2d292` → post-E.3 `sha256:db2ce75bd41e8513`.

### §3.9 `experiment_registry.runs` current schema (verified at V1 draft)

`backtest/experiment_registry.py:55` (`CREATE TABLE IF NOT EXISTS runs`) defines the schema. `fee_model TEXT` exists at line 85. No `cost_anchor_id` column exists at V1 draft time. P2 specifies schema migration to add `cost_anchor_id TEXT` column.

---

## §4 Pillar 1 / Pillar 2 trade-off analysis

### §4.1 Pillar 1 (research validity)

Pillar 1 per R3.1a §6.1 / R4.1 §8.1: numeric semantics of sealed Phase 1-5 backtest results. The `effective_7bps_per_side` cost was correctly applied to SPOT OHLCV bars throughout Phase 1-5 per the cost-model semantics that were operative at the time of those runs. Per R3.1a §5.2 (verified at lines 162-168): "No sealed backtest result requires retroactive recomputation. The `effective_7bps_per_side` cost was correctly applied to SPOT OHLCV bars throughout Phase 1-5."

R3.1d preserves Pillar 1 invariance for historical research records. The 7 bps anchor was correct under the simplification framing it was committed under — it is not "wrong"; it is operationally non-deployable under formal Branch.A SPOT context. SD3-D tiered policy makes this explicit:
- Phase 1-2 archival records: `effective_7bps_per_side` (historical record, no recomputation)
- Phase B Tier 5/6 new evaluation: `spot_realistic_15bps_v1` (conservative anchor)

### §4.2 Pillar 2 (forensic byte-identity / `config_hash` chain)

Pillar 2 per R3.1a §6.2 / R4.1 §8.2: byte-identity preservation of `config/execution.yaml` for forensic chain continuity. R4.1 SEAL spent Pillar 2 cost once at E.3 errata (pre-E.3 hash `sha256:3850424a0ef2d292` → post-E.3 `sha256:db2ce75bd41e8513`).

**R3.1d does NOT spend Pillar 2 cost again.** SD2-D sidecar pattern (main `config/execution.yaml` unchanged; conservative anchor lives in `config/execution_phaseb_spot_15bps.yaml` separately) preserves post-E.3 canonical hash `sha256:db2ce75bd41e8513` as canonical for all subsequent Phase 1-2 archival runs.

The new alias config file (`execution_phaseb_spot_15bps.yaml`) has its own separate SHA256 (recorded as `execution_config_sha256` in Tier 5/6 evaluation artifacts per Phase 4 holdout precedent at `holdout_summary.json` schema). This is parallel forensic tracking, not chain continuation — analogous to how Phase 4 holdout already uses 4 separate per-band config SHA256 values.

### §4.3 Why grandfathered + new gate (SD3-D rationale)

Three rejected alternatives:
- **SD3-A (pure grandfathered, no gate)** — too weak; allows strategies that only survive at 7 bps to enter Tier 5; false-promotion risk
- **SD3-C (full retroactive recomputation)** — prohibitive cost; zero methodological benefit; would create batches with shifting metrics depending on observation time; violates Pillar 1 historical-record invariance
- **SD3-B (sensitivity-only subset)** — lacks formal gate structure; subset selection introduces selection-inflation surface

SD3-D (tiered) is the only option that respects Pillar 1 (no retroactive rewriting) AND provides forward gate against false-promotion. Phase 4 holdout infrastructure already supports this — the 7/13/15/17 bps config family is exactly the multi-band evaluation primitive needed.

### §4.4 HARD CONSTRAINT placeholder (P3)

CLAUDE.md HARD CONSTRAINTS section gains new rule:
> ❌ NEVER promote a candidate strategy to Phase B Tier 5/6 evaluation without conservative-anchor pass at `spot_realistic_15bps_v1` (criterion per SD9 V_SEAL lock; see `docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md` §7).

The placeholder ("criterion per SD9 V_SEAL lock") prevents premature wording that conflicts with SD9 outcome. SD9 criterion is locked at V_SEAL register from the numbered options menu in §7 + attrition data in §6. Final CLAUDE.md wording resolves the placeholder at SEAL bundle landing.

---

## §5 Implementation specification (companion artifacts)

All companion artifacts are SPECIFIED in V1 draft; WRITTEN to disk atomically at R3.1d SEAL bundle commit.

### §5.1 NEW: `config/execution_phaseb_spot_15bps.yaml` alias config (per SD2-D + P1; V2-P3 patch applied)

**Type:** New file. Cost-model body and execution semantics identical to `execution_phase4_15bps.yaml`; distinct header explaining Phase B role; distinct `cost_model.name` field; separate SHA256.

**V2-P3 patch applied:** added missing `position.max_leverage: 1.0` field (verified at `execution_phase4_15bps.yaml:31`); tightened "operationally identical" language to specify cost-model + execution semantics scope (not byte-identical, since header + `cost_model.name` differ by design).

**Body structure (cost-model + execution semantics identical to `execution_phase4_15bps.yaml`):**
```yaml
# execution_phaseb_spot_15bps.yaml — Phase B conservative anchor for Tier 5/6 evaluation
# Per R3.1d SEAL (sealed at [SEAL commit pending]): 15 bps/side = 30 bps round trip
# Sourced from Phase 5.2 §6.4 Branch.A "upper end of heuristic range" + Phase 4 PLAN §1.4
# Anchor id: spot_realistic_15bps_v1 (logged in experiment_registry.runs.cost_anchor_id via
# fee_model_label engine mapping — see §5.2 below)
#
# *** THIS CONFIG IS THE CONSERVATIVE-ANCHOR PASS CRITERION BASIS FOR ***
# *** Phase B Tier 5/6 evaluation per CLAUDE.md HARD CONSTRAINT (SD3-D + SD9). ***
#
# Cost-model body + execution semantics identical to config/execution_phase4_15bps.yaml.
# Separate file for forensic clarity: Phase 4 vs Phase B usage context.
# Distinct from phase4_15bps.yaml only via: header comment + cost_model.name field.
# Sealed at: R3.1d SEAL [commit pending]

execution:
  signal_timing: "bar_close"
  fill_timing: "next_bar_open"
  stop_limit_intrabar: "adverse_first"

cost_model:
  name: "phaseb_spot_realistic_15bps"
  maker_fee_bps: 2.0
  taker_fee_bps: 10.0
  default_fee_bps: 10.0
  slippage_bps: 5.0

zero_volume:
  treatment: "flag_only"

position:
  max_position_pct: 1.0
  default_position_pct: 1.0
  max_leverage: 1.0

timezone:
  canonical: "UTC"

timeframe:
  primary: "1h"
```

**Note on alias vs byte-identical:** the cost_model body (taker_fee_bps: 10.0, slippage_bps: 5.0) and execution semantics (signal_timing, fill_timing, stop_limit_intrabar, zero_volume, position) are identical to `execution_phase4_15bps.yaml`. The header comment + `cost_model.name` differ by design (Phase B vs Phase 4 attribution). This produces a distinct SHA256 from `execution_phase4_15bps.yaml` (current SHA256: `bf84cb4aa203b740c161c28d4264e61731c0b7c232d71c383cbdbde1f279b70d` per `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_summary.json` execution_config_sha256 field). The new alias file SHA256 is recorded at SEAL bundle landing.

### §5.2 NEW: `cost_anchor_id TEXT` schema column (per SD2-D + P2; V2-P4 + V2-P5 patches applied)

**Migration target:** `backtest/experiments.db` runs table.

**V2-P4 patch applied:** schema evolution is **code-resident** in `backtest/experiment_registry.py`, not a one-off ALTER. Pattern (verified at lines 54-176): `CREATE_TABLE_SQL` (line 54) defines the schema for fresh DB creation; `MIGRATION_COLUMNS` (line 112) lists columns added post-initial-schema; the migration loop (line 174) applies `ALTER TABLE runs ADD COLUMN {col_name} {col_def}` idempotently from `MIGRATION_COLUMNS` on every connection. R3.1d SEAL bundle modifies **both** `CREATE_TABLE_SQL` (add `cost_anchor_id TEXT` to column list) and `MIGRATION_COLUMNS` (append `("cost_anchor_id", "TEXT")` tuple). Existing migration loop handles idempotent ALTER on existing databases; fresh creation uses updated CREATE_TABLE_SQL. No one-off SQL script needed.

**Migration spec (V2-P4 corrected):**
```python
# backtest/experiment_registry.py modifications at SEAL bundle landing:

# (1) CREATE_TABLE_SQL update — add cost_anchor_id column to fresh schema
# Insert in the column list near the existing `fee_model TEXT` (line 85):
#     fee_model TEXT,
#     cost_anchor_id TEXT,      -- NEW: per R3.1d SEAL
#     ...

# (2) MIGRATION_COLUMNS update — append tuple for idempotent ALTER on existing DBs
# MIGRATION_COLUMNS = [
#     ...existing entries...,
#     ("cost_anchor_id", "TEXT"),    # NEW: per R3.1d SEAL
# ]
```

**V3-PA patch (replaces V2-P5; Codex V2 BLOCKING fix) — engine integration mapping:** `backtest/engine.py` (or `execution_model.py`) reads the active execution config and writes `cost_anchor_id` to registry on run insert. **Map from `execution_config_path`** (the canonical config file path; already recorded in Phase 4 holdout artifacts schema as `execution_config_path` field — verified at `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/holdout_summary.json`). This is path-injective by definition: each config file has a unique path.

**V2-P5 (deprecated) was non-injective:** `fee_model_label` (returned by `ConstantSlippage.fee_model_label` at `backtest/slippage.py:11` as `f"effective_{self.total_bps:g}bps_per_side"`) collapses Phase 4 15bps and Phase B 15bps into the same label `effective_15bps_per_side`; same for legacy 7bps and Phase 4 07bps both producing `effective_7bps_per_side`. The mapping table required distinct anchor ids but `fee_model_label` cannot distinguish them. Codex V2 BLOCKING catch at slippage.py:11 invalidated V2-P5; V3-PA replaces with `execution_config_path` discriminator.

**Canonical anchor id enumeration (locked at R3.1d SEAL; path-based per V3-PA):**

| `execution_config_path` | `cost_anchor_id` value | Origin |
|---|---|---|
| `config/execution.yaml` | `legacy_perp_inspired_7bps_v0` | Phase 1-2 historical research record (`cost_model.name: "constant_pessimistic"`, fee_model_label `effective_7bps_per_side`) |
| `config/execution_phase4_07bps.yaml` | `phase4_forward_07bps_v1` | Phase 4 forward-holdout sensitivity band (-2 slip) |
| `config/execution_phase4_13bps.yaml` | `phase4_forward_13bps_v1` | Phase 4 forward-holdout sensitivity band (-2 slip vs anchor) |
| `config/execution_phase4_15bps.yaml` | `phase4_forward_15bps_v1` | Phase 4 forward-holdout primary basis (per PHASE4_PLAN §1.5) |
| `config/execution_phase4_17bps.yaml` | `phase4_forward_17bps_v1` | Phase 4 forward-holdout sensitivity band (+2 slip) |
| `config/execution_phaseb_spot_15bps.yaml` (NEW alias per §5.1) | `spot_realistic_15bps_v1` | Phase B Tier 5/6 conservative-anchor gate (R3.1d SEAL output) |

**Path injectivity:** each row's left column is a unique file path; mapping is bijective. Codex V2 BLOCKING (non-injective `fee_model_label` discriminator) resolved by switching to path discriminator. **Phase 4 holdout artifacts already use `execution_config_path` as the canonical config identifier** in `holdout_summary.json` (verified field present + populated), so this discriminator class is the existing project precedent — V3-PA aligns with existing schema rather than introducing new convention.

**Historical runs backfill:** existing Phase 1-2 runs at `config/execution.yaml` backfilled as `legacy_perp_inspired_7bps_v0`; existing Phase 4 forward-holdout runs backfilled per their `execution_config_path` field via the path-to-anchor-id mapping table above. Backfill SQL specified in SEAL bundle migration script; applied atomically at SEAL bundle landing.

**Implementation note:** engine code change deferred to SEAL bundle landing; mapping table above is canonical contract. **fee_model_label may still be retained as a complementary registry column** (existing `fee_model TEXT` at `experiment_registry.py:85` already records it) — V3-PA's discriminator is `execution_config_path` for the new `cost_anchor_id` lookup; the existing `fee_model` column is orthogonal historical metadata.

### §5.3 NEW: CLAUDE.md HARD CONSTRAINT addition (per SD3 + P3)

**Insertion location:** CLAUDE.md "HARD CONSTRAINTS" section.

**Wording (V1 draft form — final form resolved at V_SEAL once SD9 criterion locks):**
> **### Conservative-Anchor Gate Integrity (Phase B Tier 5/6)**
> - ❌ NEVER promote a candidate strategy to Phase B Tier 5/6 evaluation without conservative-anchor pass at `spot_realistic_15bps_v1` per `config/execution_phaseb_spot_15bps.yaml` (anchor: 15 bps/side = 30 bps round trip)
> - ❌ NEVER use Phase 1-2 `effective_7bps_per_side` results as Tier 5/6 promotion basis under formal Branch.A SPOT commitment (per R3.1d SEAL + R4.1 SEAL)
> - ❌ NEVER modify `config/execution_phaseb_spot_15bps.yaml` without explicit human approval (parallel rule to `config/execution.yaml` per CLAUDE.md HARD CONSTRAINTS Data Integrity)
> - Conservative-anchor pass criterion: [PLACEHOLDER — locked at SD9 V_SEAL register per `docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md` §7]

The criterion placeholder is filled at V_SEAL adjudication from §7 numbered options menu.

### §5.4 R4.1 hygiene patches (per SD4 + P4)

**Verified hygiene gap at V1 draft time** (re-verified per Advisor PFR F1 PUSHBACK; confirmed real):
- `docs/phase5/R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md` line 5: "Status: V3 REVISED-POST-PFR-RULE-Y (current; pre-V_SEAL) for combined V1 reviewer round + PFR rule-Y round adjudicated; awaiting Charlie V_SEAL register"
- Line 42: "V_SEAL fire + SEAL bundle commit authorize | PENDING (next Charlie register)"
- Line 462: "V_SEAL | PENDING (awaiting Charlie register)"
- Line 498: "End of V3 REVISED-POST-PFR-RULE-Y."

**Patches to apply at R3.1d SEAL bundle landing:**

| Line | Pre-patch | Post-patch |
|---|---|---|
| 5 | "Status: V3 REVISED-POST-PFR-RULE-Y (current; pre-V_SEAL) ... awaiting Charlie V_SEAL register" | "Status: V_SEAL (sealed at `3ff085e` + Phase Marker advance `7a63516` 2026-05-18). R4.1 + R3.1a §12 Errata + `config/execution.yaml` line 42 patch as single atomic SEAL bundle." |
| 42 | "V_SEAL fire + SEAL bundle commit authorize \| PENDING (next Charlie register)" | "V_SEAL fire + SEAL bundle commit authorize \| `3ff085e` + `7a63516` 2026-05-18" |
| 462 | "V_SEAL \| PENDING (awaiting Charlie register) \| ..." | "V_SEAL \| SEALED (`3ff085e` + `7a63516`) \| ..." |
| 498 | "End of V3 REVISED-POST-PFR-RULE-Y." | "End of V_SEAL (sealed `3ff085e` + `7a63516` 2026-05-18)." |

**Editorial provenance note (per P4; V2-P6 trimmed to 2 sentences):**
> R4.1 SEAL artifact (`3ff085e`) committed the cycle-metadata header text in its V3 pre-SEAL state — the SEAL bundle landed the document atomically with the body content but did NOT update the V-anchor status strings to reflect post-SEAL state. The R3.1d cycle bundles these hygiene patches into its own SEAL artifacts per SD4-A; this is an inline-edit class patch (stale-status-string correction), distinct from R3.1a §12's substantive errata-append class.

**V2-P8 patch — inline-edit vs errata-append classification (Advisor A-F3 legitimate methodology finding):**

The R4.1 hygiene patches are classified as **inline-edit class** (stale-status-string corrections to cycle-metadata header), structurally distinct from R3.1a §12 Errata appendix (substantive errata-content append per Phase A `9c00f59` precedent). The two classes have different Pillar 2 implications:

| Class | Example | Sealed-content invariance | Pillar 2 impact |
|---|---|---|---|
| **Errata-append** (R3.1a §12) | NEW §12 appended after sealed §§0-11 | §§0-11 byte-identical preserved | Pillar 2 cost spent once (config_hash change); appendix is forensically additive |
| **Inline-edit hygiene** (R4.1 lines 5/42/462/498, this patch) | Stale status string `"V3 REVISED-POST-PFR-RULE-Y (pre-V_SEAL)"` → `"V_SEAL (sealed at 3ff085e)"` | NOT byte-identical (stale status strings updated to reflect post-SEAL state) | No Pillar 2 cost (no `config_hash` source file modified); forensic chain preserved via post-SEAL commit metadata `7a63516` already in PM/history |

This classification is explicit: inline-edit class is **NOT a violation of sealed-content invariance** — the patched strings were *cycle-metadata header* status strings that were correct at V3 draft time but became misleading post-SEAL. The substantive content of R4.1 §§0-12 remains unchanged. The patches update purely status-reflective metadata to match the post-SEAL state already documented in `git log` + CLAUDE.md Phase Marker + `docs/phase_marker_history.md` row.

**Precedent basis for inline-edit hygiene class:** none directly in the project — this is the first inline-edit hygiene patch class. The classification is established here per Advisor V1 review finding A-F3 + Charlie V2 patch ratification. Future similar hygiene gaps (likely rare; structural cause: V_SEAL register fires SEAL bundle atomically but cycle-metadata header is drafted at V3 stage) will reference R3.1d §5.4 as inline-edit class precedent.

### §5.5 R2.1 audit-criterion pre-commit (separate register-event per SD5-B)

R2.1 (volume_divergence DSL audit) requires pre-commitment of audit criterion before inspection per Codex Round 2 Catch B (CLAUDE.md Phase Marker). SD5-B locks: this pre-commitment happens at a separate Charlie register-event after R3.1d SEAL, before R2.1 cycle entry. R3.1d does NOT bundle R2.1 audit criterion into its sub-decision locks. R2.1 remains eligible-not-named for separate Charlie register-event boundary.

### §5.6 R3.1b/c non-foreclosure language (per SD6-A; §8 below)

See §8 for full conditional-trigger language. R3.1d explicitly preserves R3.1b/c as deferred empirical validation supersession path.

---

## §6 Attrition-rate sensitivity analysis (Phase 4 forward-holdout)

### §6.1 Methodology + representativeness caveat (per P6)

**Source artifacts:** Phase 4 forward-window holdout results at `data/phase2c_evaluation_gate/phase4_forward_2026_{07,13,15,17}bps_v1/holdout_summary.json` + `holdout_results.csv` (verified extant 2026-05-19; 4 directories with both files per band). Source batch_id: `phase2c_15_main_fire_combined`. Forward window: 2026-01-01T00:00:00Z to 2026-04-16T07:00:00Z (2528 bars; parquet_data_sha256 `db4ce1d2a2e5e7b556975837260f7aaa29ee4fd5ddc603690d1bc57912aa7035`).

**Label:** **Phase 4 forward-holdout attrition** (NOT "Tier 5 expected survival"). The PHASE2C_15 cohort_a candidate population (N=39) is a **structural analog**, NOT a representative sample, of the Phase B Tier 5 candidate pool. Phase B Tier 5 candidates may come from different mining cycles (post-R3.1d Phase 2B AI loop iterations) with different Sharpe distributions, theme mixes, and selection histories. This table informs SD9 criterion design but does NOT predict Phase B Tier 5 pass rates.

**Statistical framing:** Clopper-Pearson 95% binomial confidence interval per band. Sample size N=39 is fixed; CIs are wide reflecting that.

**Two-metric framing (V2-P1 patch per Codex V1 BLOCKING C-F1/C-F2):** §6.2/§6.3/§6.4 below report **`holdout_passed` attrition** (existing 4-condition AND gate per Phase 4 PLAN §1.5: `holdout_sharpe ≥ -0.5 AND holdout_max_drawdown ≤ 0.25 AND holdout_total_return ≥ -0.15 AND holdout_total_trades ≥ 5`). §6.7 below reports **strict positive-Sharpe attrition** (`holdout_sharpe > 0` only — the metric Option A in §7 SD9 menu operates on). These are DIFFERENT metrics with different pass counts; both are reported here for SD9 criterion calibration.

### §6.2 `holdout_passed` attrition table (existing 4-condition AND gate)

**Source:** `counts.holdout_passed` field from each band's `holdout_summary.json` (verified 2026-05-19 via `jq -r '.counts.holdout_passed'`).

| Band | k_pass / N | Observed pass rate | 95% CP CI |
|---|---|---|---|
| 07 bps/side | 23/39 | 58.97% | [42.10%, 74.43%] |
| 13 bps/side | 20/39 | 51.28% | [34.78%, 67.58%] |
| **15 bps/side** | **20/39** | **51.28%** | **[34.78%, 67.58%]** |
| 17 bps/side | 20/39 | 51.28% | [34.78%, 67.58%] |

**`holdout_passed` attrition observation:** Pass count drops by 3 candidates (23→20) between 07 bps and 13 bps; **identical 20/39 = 51.28% pass at 13, 15, and 17 bps** (no further attrition above 13 bps under the 4-condition gate). The `holdout_passed` criterion includes `holdout_sharpe ≥ -0.5` (a wide tolerance band), which is why the gate is not strongly cost-sensitive within {13, 15, 17}. 95% CIs overlap heavily between 07 and 15 bands.

### §6.3 By-theme breakdown (`holdout_passed`)

| Theme | 07 bps | 13 bps | 15 bps | 17 bps |
|---|---|---|---|---|
| calendar_effect | 14/22 (64%) | 11/22 (50%) | 11/22 (50%) | 11/22 (50%) |
| momentum | 4/6 (67%) | 4/6 (67%) | 4/6 (67%) | 4/6 (67%) |
| volume_divergence | 4/7 (57%) | 4/7 (57%) | 4/7 (57%) | 4/7 (57%) |
| volatility_regime | 1/2 (50%) | 1/2 (50%) | 1/2 (50%) | 1/2 (50%) |
| mean_reversion | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) |

**Attrition under `holdout_passed` is concentrated in calendar_effect** (3 of 22 calendar candidates fail at 13+ bps that passed at 07 bps); momentum / volume_divergence / volatility_regime / mean_reversion subsets are unchanged across cost bands.

### §6.4 Universe partition (`holdout_passed`)

| Universe | 07 bps | 13 bps | 15 bps | 17 bps |
|---|---|---|---|---|
| audit_only (24 total) | 18/24 (75%) | 16/24 (67%) | 16/24 (67%) | 16/24 (67%) |
| primary (15 total) | 5/15 (33%) | 4/15 (27%) | 4/15 (27%) | 4/15 (27%) |

audit_only and primary partitions both show 1-2 candidate attrition concentrated at the 7→13 boundary.

### §6.5 Post-hoc selection pre-commitment (per P7)

**The attrition table is INFORMATIONAL ONLY.** SD1 = 15 bps/side anchor is locked; this table does NOT reopen the SD1 decision. The table's purpose is **SD9 criterion calibration** (informing the V_SEAL lock on the numbered options menu in §7), NOT cost-anchor re-deliberation. If the table shows attrition rates that differ from prior expectation, the response is to refine the SD9 criterion (which is its purpose), NOT to back-solve from a desired pass rate to a preferred cost assumption. R3.1d V_SEAL register binds SD1 = 15 bps/side regardless of attrition data; the data informs HOW the gate criterion is structured at 15 bps, not WHERE the anchor sits.

### §6.6 Interpretation (~1 paragraph cap per P7)

The empirical attrition cliff at the 7→13 bps boundary (3 of 39 candidates lost under `holdout_passed`; remaining 20 stable across 13/15/17) suggests the 4-condition `holdout_passed` gate is not strongly cost-discriminating within the conservative range, because its Sharpe-component tolerance band (`>= -0.5`) is wide. The strict-positive-Sharpe metric in §6.7 below shows more cost-sensitivity (monotone decline 26→20→18→15) and is the operationally relevant metric for SD9 Option A. The 95% CIs are wide (N=39); we cannot rule out "no real population-level pass-rate difference between 07 and 15 bps" under either metric. The attrition concentrated in calendar_effect under `holdout_passed` suggests trade-cost sensitivity is theme-asymmetric. SD9 criterion design should use the strict-Sharpe metric (§6.7) as the calibration basis when Option A is the chosen criterion class.

### §6.7 NEW: Strict positive-Sharpe attrition table (V2-P1 patch — SD9 Option A calibration basis)

**Source:** `holdout_sharpe > 0` count per band from each `holdout_results.csv` (verified 2026-05-19 via `awk -F',' 'NR>1 && $8 > 0'`).

**Why this table is needed (V2-P1 BLOCKING fix per Codex C-F1/C-F2):** SD9 Option A in §7 operates on `holdout_sharpe > 0`, NOT on `holdout_passed`. These are semantically different gates: `holdout_passed` is a 4-condition AND gate including `holdout_sharpe >= -0.5` (wide tolerance); `holdout_sharpe > 0` is a strict-positivity gate (zero tolerance band). The two produce different pass-set membership: at 15bps, 18 strategies have `holdout_sharpe > 0` strict, while 20 strategies have `holdout_passed = 1` — meaning 5 strategies pass `holdout_passed` despite `holdout_sharpe <= 0` (slack via other 3 conditions), and 3 strategies have `holdout_sharpe > 0` but fail `holdout_passed` (slack-fail via drawdown/return/trade-count). This table is the operationally relevant calibration basis for SD9 Option A.

| Band | `holdout_sharpe > 0` count / N | Observed strict-positive rate | 95% CP CI |
|---|---|---|---|
| 07 bps/side | 26/39 | 66.67% | [49.78%, 80.91%] |
| 13 bps/side | 20/39 | 51.28% | [34.78%, 67.58%] |
| **15 bps/side** | **18/39** | **46.15%** | **[30.09%, 62.82%]** |
| 17 bps/side | 15/39 | 38.46% | [23.36%, 55.38%] |

**Strict-Sharpe attrition observation:** Pass count decreases monotonically across all 4 bands (26→20→18→15), confirming the strict-Sharpe metric IS cost-sensitive across the conservative range (unlike `holdout_passed` which plateaus at 20 from 13bps onward). The attrition rate is approximately 3 candidates per 4bps cost increment. At the locked SD1 = 15 bps/side anchor, 18/39 = 46.15% of PHASE2C_15 cohort_a strategies satisfy `holdout_sharpe > 0` strict.

**Cross-metric divergence:** at 15bps:
- 18 strategies pass `holdout_sharpe > 0` strict (§6.7)
- 20 strategies pass `holdout_passed` 4-condition gate (§6.2)
- Set-intersection NOT equal to either set: 5 strategies pass `holdout_passed` but fail `holdout_sharpe > 0`; 3 strategies pass `holdout_sharpe > 0` but fail `holdout_passed`
- Set-union: 23 strategies pass at least one criterion at 15bps

SD9 V_SEAL adjudication selects which metric class (or composite) becomes the canonical Tier 5/6 conservative-anchor gate per §7 options menu.

---

## §7 SD9 — Tier 5 gate pass criterion (numbered options menu; locked at V_SEAL)

**Locked HARD invariant at sub-decision lock 2026-05-18:** no Tier 5 promotion without conservative-anchor pass at `spot_realistic_15bps_v1`.

**Pass criterion options for V_SEAL register lock** (anti-rubber-stamp per P5; V_SEAL adjudicates from this numbered menu):

### Option A — Strict Sharpe-positive (recommended pass threshold: SHR > 0 at 15 bps)
- Criterion: `holdout_sharpe > 0` at 15 bps/side over evaluation window
- Phase 4 holdout precedent: the existing `holdout_passed` criterion uses `holdout_sharpe >= -0.5` (wide tolerance), distinct from strict positive Sharpe
- **Effect on PHASE2C_15 cohort_a: 18/39 = 46.15% pass at 15 bps strict** (per **§6.7 strict-Sharpe table**, NOT §6.2 which reports the 4-condition `holdout_passed` gate at 20/39)
- Risk: bare-positive Sharpe leaves no margin for forward-period regime shift; may pass strategies near zero alpha. Annualized Sharpe SE over 2528-bar window is wide (Advisor V1 review noted O(1) SE limitation) — strict-positive at point estimate is not statistical-significance threshold

### Option B — Positive Sharpe + non-dominated by buy-and-hold at equivalent risk
- Criterion: `holdout_sharpe > 0` AND `holdout_sharpe > buy_and_hold_sharpe_at_equivalent_position_size`
- Effect on PHASE2C_15 cohort_a: subset of Option A pass-set (likely smaller; **requires BTC HODL Sharpe over forward window 2026-01-01 to 2026-04-16 to be pre-computed** — Advisor V1 SC1 dependency flag)
- Risk: more conservative; may eliminate weak-alpha strategies that still contribute to portfolio diversification
- Benefit: directly addresses the empty-cupboard risk of passing strategies that under-perform passive holding
- **V_SEAL precondition:** if Option B selected, BTC HODL benchmark Sharpe over forward window must be computed and embedded in SEAL bundle artifacts before promotion gate operationalizes

### Option C — Sharpe > X threshold (X TBD; e.g., 0.5)
- Criterion: `holdout_sharpe > X` at 15 bps/side
- Effect: depends on X; tighter threshold = fewer candidates
- Risk: X choice itself becomes a hyperparameter requiring justification; risk of post-hoc tuning to desired pass rate

### Option D — Composite (positive Sharpe + max_drawdown bounded)
- Criterion: `holdout_sharpe > 0` AND `holdout_max_drawdown < Y` (Y TBD; e.g., 0.15)
- Effect: tighter than Option A; bounds tail risk
- Risk: Y choice becomes hyperparameter; max_drawdown over 2528-bar window is sample-thin

### Option E — Other / Charlie-specified

### Option F — FWER-style multiplicity-corrected gate (V2-P9 patch per CLAUDE.md DSR HARD CONSTRAINT + R1.2 OBS 1; V3.5-PD revised)
- Criterion: `holdout_sharpe > 0` AND production-grade FWER-controlling multiplicity correction passes
- **Eligible instruments (FWER-class):**
  - **Deflated Sharpe Ratio per Bailey-Lopez de Prado 2014** (preferred — adjusts Sharpe variance for cross-strategy correlation, skewness, kurtosis, autocorrelation; production-grade target for capital-commitment decisions)
  - **Romano-Wolf stepdown** (eligible — recovers power under correlated test statistics; production-grade)
  - **Westfall-Young permutation FWER** (eligible — assumption-free via bootstrap of return series; production-grade)
  - Heuristic DSR `sqrt(2*ln(N))` (current `backtest/evaluate_dsr.py` per file caveat: "approximate screen... NOT production-grade DSR. If production-grade DSR is needed, it will be a dedicated effort with proper statistical review") — **acceptable interim screen only**; supersession to production-grade required before capital commitment
- **BH-FDR NOT eligible:** Benjamini-Hochberg controls False Discovery Rate (expected proportion of false rejections among rejections) NOT Family-Wise Error Rate (probability of any false rejection). Per-strategy capital commitment under this project's serial individual-allocation architecture (no cross-strategy portfolio diversification at deployment) requires FWER. V3.5-PD correction: earlier V2-P9 text incorrectly listed BH-FDR as eligible via a fabricated "R1.2 §6 'DSR or BH-FDR pass at appropriate α'" cross-reference; Codex final pre-SEAL grep (2026-05-19) verified R1.2 §6 contains NO such prose (R1.2 §6 = "Per-Candidate Detail + Pattern Surfacing" tables; zero hits for DSR/BH-FDR/FDR/Bonferroni/multiplicity across entire R1.2 doc). See OBS 8 for propagated-hallucination provenance.
- **N specification per CLAUDE.md HARD CONSTRAINT:** "NEVER use `hypotheses_approved` as N for DSR — always `hypotheses_attempted` from batch_summary". Note: `batch_summary` SQLite table does not yet exist in `backtest/experiments.db` (verified 2026-05-19); canonical N retrievable from Phase 2C batch JSON lifecycle artifacts (`agents/proposer/stage{2a,2b,2c}_batch.py` outputs). `batch_summary` SQLite table build is eligible-not-named within R6.1 scope.
- **Methodological basis:** N=39 candidate cohort emerged from larger mining pool (`hypotheses_attempted` ≫ 39); selection inflation under multiple-testing requires FWER correction per R1.2 OBS 1 ("AMBIGUOUS verdict binds Phase B promotion HARDER per pre-bound rule").
- **Effect on PHASE2C_15 cohort_a:** heuristic DSR with N≥100 → expected 0-2 passers from current 18 strict-Sharpe-positive (empty-cupboard risk under heuristic instrument). Production DSR (BLdP) may be more permissive given correlation/skew/kurtosis adjustment; Romano-Wolf stepdown more permissive under correlated test statistics; Westfall-Young permutation captures actual joint distribution.
- **V_SEAL precondition:** Option F is the LOCKED Tier 6 gate framework (per SD9 V_SEAL register). Instrument variant + threshold + N value locked at R6.1 V_SEAL based on cohort properties at R6.1 fire time — NOT pre-locked at R3.1d V_SEAL per Framing 1 staging.

**V_SEAL register adjudicates from this menu after Charlie reviews V2 + attrition data (§6 + §6.7 strict-Sharpe) + V2 reviewer round findings.** Default posture at V2: no lean injection on SD9 criterion choice (BL-Y-refined blind-lean Phase 1 reserved for V2 reviewer round on SD9 specifically).

---

## §8 R3.1b/c explicit non-foreclosure (per SD6-A)

R3.1d's conservative 15 bps/side anchor is a **governance anchor at upper end of heuristic range**, NOT empirical execution truth. Slippage component (5 bps) is literature-grounded heuristic per Phase 5.2 §3.2 (verified at PHASE5_2:123-128), NOT L2-replay-verified or live-fill-measured.

**R3.1b/c eligible-not-named** for separate Charlie register-event boundary with the following trigger condition:

> When Phase 4 paper trading infrastructure deploys (= first crossover from research → operational capital under SPOT venue per CLAUDE.md Phase Marker framing), R3.1b/c becomes eligible-not-named for separate Charlie register. R3.1b/c scope = empirical small-lot venue-conditional cost measurement on real SPOT fills, producing a measured cost distribution that supersedes R3.1d's heuristic anchor.

**Non-foreclosure invariants:**
1. R3.1d 15 bps/side anchor does NOT pre-judge R3.1b/c output
2. R3.1b/c measured cost may be lower OR higher than 15 bps; R3.1d does not assume direction
3. When R3.1b/c fires + completes, its output supersedes R3.1d at a separate Charlie register-event boundary (new conservative anchor lock or volatility-scaled framework or other)
4. R3.1d's `spot_realistic_15bps_v1` anchor id will be archived with a successor anchor id (e.g., `spot_measured_Xbps_v1`) introduced for R3.1b/c-anchored evaluation

**This non-foreclosure prevents R3.1d from becoming an accidental permanent ceiling** — the conservative governance anchor explicitly acknowledges it is a current-state approximation with a defined empirical supersession path, not a foreclosed final cost model.

---

## §9 OBSERVATIONS (anti-pre-naming; eligible-not-named for separate registers unless explicitly Charlie-named)

**OBSERVATION 1 (R3.1d governance anchor ≠ R3.1b/c empirical truth):** R3.1d's 15 bps/side anchor is a heuristic governance commitment, not measured fill cost. Phase 4 paper-trading deployment + R3.1b/c measurement supersede this when fired (per §8). No R3.1d output forecloses R3.1b/c scope.

**OBSERVATION 2 (Attrition cliff at 7→13 boundary in PHASE2C_15 cohort_a):** Per §6 attrition data, the relevant pass-rate drop occurs at the 7→13 bps transition (3/39 = 7.7% absolute drop); 13/15/17 bps bands show identical pass count in this cohort. This is a structural finding for the existing cohort; Phase B Tier 5 candidate pool may show different attrition geometry.

**OBSERVATION 3 (Calendar-effect theme asymmetric cost sensitivity):** Per §6.3, calendar_effect strategies show 3-candidate attrition between 07 and 13 bps; momentum/volume_divergence/volatility_regime themes show zero attrition across all cost bands in this cohort. This suggests cost-sensitivity is theme-asymmetric; SD9 criterion design should weight this if calendar-effect candidates dominate Phase B Tier 5 input.

**OBSERVATION 4 (R1.2 AMBIGUOUS verdict + conservative anchor = stacked Tier 5 hurdle):** Per R1.2 OBS 1 (verified at R1_2:272-274), AMBIGUOUS verdict binds R5.1 candidate-subset commitment harder. Combined with R3.1d 15 bps gate, Tier 5 promotion now requires both cost-realism survival AND IS-OOS rank stability evidence. This is the explicit research-velocity-vs-rigor calibration locked at R3.1d.

**OBSERVATION 5 (Pillar 2 second-spend avoided):** R3.1d's SD2-D sidecar pattern explicitly avoids the second `config_hash` invalidation that SD2-A (numeric modification of execution.yaml) would have spent. Post-E.3 canonical `sha256:db2ce75bd41e8513` remains canonical for all Phase 1-2 archival runs. Cost-anchor change is forensically tracked via separate alias config + new `cost_anchor_id` registry column, not via main config_hash chain mutation.

**OBSERVATION 6 (Cumulative pilot reviewer reliability — R3.1d cycle V2 update; V2-P7 patch applied):** R3.1d cycle reviewer pipeline through V1 fresh redispatch (sub-decision Round 1 + sub-decision PFR + V1 original killed at Codex stall + V1 fresh redispatch): **1 Codex stall** (V1 original, 1h 41m worker-PID-dead pattern; cancel-and-kill recovery applied per Charlie register row 6) + **0/3 Codex hallucinations** (sub-decision Round 1 + PFR + V1 fresh, clean for Codex on 3 completed dispatches) + **9/12 verified Advisor hallucinations = 75% rate** across 4 Advisor dispatches (Round 1 + PFR + V1 original + V1 fresh). Hallucination breakdown: (a) Round 1 SD4 verification false-claim "no PENDING in R4.1 doc"; (b) PFR Item 1 false-claim "line 5 V_SEAL SEALED"; (c) V1 original §6 numerics 29/8/7/5 fabrication + §7 Option E content fabrication + Phase 4 dir existence false-claim (3 in single dispatch); (d) V1 fresh §6 numerics 22/18/16/14 fabrication + by-theme "trend" theme fabrication + theme pass-rate fabrication + theme characterization mischaracterization (4 in single dispatch). **All hallucinations Mode A** (file:line/exact-quote/numerical-content errors). PUSHBACK applied via citation verification discipline; ground-truth re-verified independently. **Critical diagnostic finding (Charlie's V1 fresh redispatch test):** mandatory `[VERIFIED via grep]` token in dispatch brief did NOT eliminate hallucinations; Advisor used the token but the verifications were still fabricated. **Mode A failure is structural, not prompt-fixable.** Cumulative Reading 3 pilot stats post-R3.1d V1 fresh: ~4-8% Codex stall rate (2 stalls / ~25 dispatches) + ~2% Codex hallucinations (1 verified at R4.1) + **~30-40% Advisor hallucinations cumulative** (this cycle's 75% rate is elevated data point reinforcing prior trend across R4.1 + R3.1a). **Memory codification investigation registered as concurrent task per Charlie register row 7 "Memory codification investigation"** — investigation updates `feedback_reviewer_routing_subagent_default.md` + may create new feedback memory documenting Mode A structural failure + B2 standing-rule support; deliverable bundled with R3.1d SEAL.

**OBSERVATION 7 (R3.1d V1 draft scope coherence):** Per Advisor PFR Item 6, V1 draft scope is "coherent and tight" — 15 bps anchor + Pillar 1 tiered policy + R4.1 hygiene patch (bundled) + R3.1b/c non-foreclosure + attrition table (capped) + SD9 numbered options menu. No expansion into new empirical runs or Tier 5 final criterion selection before V1 reviewer round.

**OBSERVATION 8 (Propagated Advisor hallucination caught at final pre-SEAL gate — V3.5-PD correction provenance):** V2-P9 patch added §7 Option F with text claiming "Deflated Sharpe Ratio (DSR) or Benjamini-Hochberg FDR control on holdout p-values are standard" + V_SEAL precondition allowing "BH q < 0.10". Original justification cited Advisor V1 A-F4 finding which itself cited R1.2 §6 prose "DSR or BH-FDR pass at appropriate α". **Codex final pre-SEAL F2 (VERIFY-FAILED via grep 2026-05-19):** R1.2 doc contains ZERO hits for DSR / BH-FDR / FDR / Benjamini / Hochberg / Bonferroni / multiplicity terms; R1.2 §6 is "Per-Candidate Detail + Pattern Surfacing" (per-candidate Sharpe tables, NOT methodology discussion). The "R1.2 §6 lists BH-FDR" claim was fabricated by Advisor V1; I propagated it into V3 §7 Option F at V2-P9; Codex grep at final pre-SEAL gate caught the discrepancy. V3.5-PD removes the fabricated cross-reference entirely + replaces with FWER-only language motivated by CLAUDE.md HARD CONSTRAINT (real) + R1.2 OBS 1 (real "AMBIGUOUS verdict binds Phase B promotion HARDER"). **Charlie's BH-FDR push-back instinct was doubly correct:** (a) methodology framework distinction (FWER vs FDR — different statistical guarantees); (b) authorizing citation didn't exist in source doc. **Cross-model diversity load-bearing again:** Codex grep catch at final pre-SEAL gate prevented propagated-hallucination text from shipping into V_SEAL artifact. Hallucination tally R3.1d cycle: 15+ verified Advisor hallucinations across 7 dispatches (~85% rate; Mode A structural; the 15th retroactively traced via Codex final-gate grep on V3 content originally written based on Advisor V1 A-F4 hallucinated citation).

---

## §10 Reserved decisions / eligible-not-named successors

**R3.1d cycle scope strictly bounds the following NON-RESOLUTIONS** (eligible-not-named for separate Charlie register-event boundary per anti-pre-emption + Phase 5.1/5.2/Phase A/R1.2/R3.1a/R4.1 SEAL precedent codified discipline):

1. **SD9 exact criterion** — locked at V_SEAL register from §7 numbered options menu
2. **R2.1 audit criterion** (volume_divergence DSL audit) — separate register-event after R3.1d SEAL (per SD5-B)
3. **R2.2** (Monday-pattern mechanism investigation) — separate register; informed by R1.2 OBS 4
4. **R2.3** (Phase A V4 SEAL OBSERVATION 10 theme provenance verification) — separate register [MP1 citation-clarity inline patch applied at R2.0 V_SEAL 2026-05-19 per V2-P8 sub-class precedent: citation-label disambiguation, no substantive content change, Pillar 2 invariance preserved]
5. **R3.1b/c** (empirical small-lot cost measurement) — eligible-not-named when Phase 4 paper-trading infrastructure deploys (per §8)
6. **R5.1** (Phase B candidate-subset commitment under SPOT venue) — gated behind R3.1d + Tier 2 SEAL per sequencing 1→3→4
7. **R5.2** (selection-inflation handling cycle) — gated behind R5.1
8. **R6.1** (Phase B promotion class — minimum-trade-count gate + per-strategy multiplicity pre-bind) — gated behind R5.1/R5.2
9. **Tier-0 pause / strategic-absorption** — per V3 top note
10. **3-candidate IS-OOS-consistent sub-cohort framing** (per R1.2 OBSERVATION 5) — eligible-not-named
11. **Broader Stratum B DSL audit** (per R1.2 OBSERVATION 3) — eligible-not-named
12. **Pure-in-sample comparison cycle** (per R1.2 OBSERVATION 7) — eligible-not-named
13. **Memory codification investigation on Advisor hallucination rate elevation** — eligible-not-named
14. **Pre-existing noise cleanup** (`.DS_Store` + `docs/d7_stage2c/*`; 12+ session carry-forward) — eligible-not-named
15. **Phase 2.5 bandit-dedup activation** — parked per `docs/parked/PARKED_BRANCHES.md`
16. **Project pause / strategic-absorption** — eligible-not-named
17. **Other Charlie-specified** — eligible-not-named

All eligible at separate Charlie register-event boundary per anti-pre-emption invariant. R3.1d cycle does NOT pre-name any of these; surfacing them here is forward-only carry-forward, not pre-emptive scope binding.

---

## §11 V-anchor chain

| Version | Status | Description |
|---|---|---|
| V1 | ARCHIVED | Initial draft post-Charlie register chain "fire V1 draft, then dispatch reviewer round" 2026-05-18. Structure: 12 main §§ + cycle metadata header + §12 appendix. Sub-decision locks SD1-SD9 + 7 mechanical patches P1-P7 incorporated. Attrition analysis (§6) computed from existing Phase 4 forward-window holdout artifacts. V1 reviewer round (fresh after Codex stall + redispatch per Charlie register row 6) returned 2026-05-19: Codex BLOCK verdict (2 BLOCKING + 2 SUBSTANTIVE + 2 POLISH + 1 LBR; clean 0 hallucinations); Advisor APPROVE-WITH-FINDINGS (4 verified Advisor hallucinations on §6 numerics + by-theme structure + theme characterization; 1 legitimate methodology finding A-F3 Pillar 2 classification; 1 marginal finding A-F4 multiplicity option; rest REJECT on hallucinated basis). Cumulative R3.1d cycle reviewer reliability: 0/3 Codex hallucinations + 9/12 Advisor hallucinations (75% rate; Mode A structural per V1 PFR self-reflection; mandatory verification mandate did NOT eliminate hallucinations — confirmed structural). |
| V2 | ARCHIVED | Post-V1-reviewer-round revised draft per Charlie register "Apply V2 patches + 进入 V2 reviewer round + Memory codification investigation" 2026-05-19. V1 → V2 applied 9 ADOPT patches (P1-P9 per V1 ARCHIVED row description). V2 reviewer round (Codex + Advisor parallel) returned 2026-05-19: Codex BLOCK verdict — 1 BLOCKING (V2-P5 `fee_model_label` non-injective mapping; `slippage.py:11` `f"effective_{self.total_bps:g}bps_per_side"` collapses Phase 4 15bps + Phase B 15bps into same label) + 1 SUBSTANTIVE (V2 footer stale "End of V1 DRAFT") + 1 LBR (§6.7 CI lower bound 30.10% vs scipy 30.09%); 0 hallucinations; all findings source-verified. Advisor INVALID — 10th hallucination claimed "DELIVERABLE NOT FOUND IN FILESYSTEM" but Codex found file cleanly at `docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md`; Mode A file-existence fabrication. V2 reviewer round outcome: Codex caught real BLOCKING that would have shipped under Advisor-only review; **B2 standing rule LOCKED 2026-05-19 per R3.1d cycle empirical** (codified in `feedback_reviewer_routing_subagent_default.md` Reading 3 pilot CLOSED section). |
| V3 | ARCHIVED | Post-V2-reviewer-round revised draft per Charlie register "Apply V3 patches + PFR dispatch" 2026-05-19. V2 → V3 applied 3 ADOPT patches (V3-PA path-based mapping; V3-PB footer; V3-PC CI rounding). V3 PFR round (Codex + Advisor parallel) returned 2026-05-19: Codex APPROVE-WITH-FINDINGS clean (0 hallucinations); Advisor INVALID (wholesale document content fabrication — 14th hallucination this cycle). V3 PFR effectively no-op (Codex meta-finding on brief-side verification recipe only; not artifact change). Final pre-SEAL reviewer round (Codex + Advisor with opus model upgrade per Charlie manual change) returned 2026-05-19: Codex APPROVE-WITH-FINDINGS clean (0 hallucinations, 8 findings; **F2 VERIFY-FAILED caught propagated Advisor hallucination — "R1.2 §6 'DSR or BH-FDR pass at appropriate α'" cross-reference is FABRICATED; grep R1.2 returns 0 hits for DSR/BH-FDR/FDR/Bonferroni/multiplicity terms; R1.2 §6 is actually "Per-Candidate Detail + Pattern Surfacing" tables**); Advisor APPROVE-WITH-FINDINGS with substantially improved performance (opus-driven; honest uncertainty distinguishing factual vs judgment claims; surfaced Romano-Wolf/Westfall-Young as alternative FWER instruments; Q5 self-review with anti-self-serving discipline). |
| **V_SEAL** | **SEALED 2026-05-19** | Canonical sealed artifact at register-event boundary per Charlie register "接受 6 个 V3.5 patches + 接受最终 V_SEAL register text + Fire V_SEAL register" 2026-05-19. V3 → V_SEAL applied 6 V3.5 patches: **V3.5-PD BLOCKING** (Codex final F2) — §7 Option F rewritten removing fabricated BH-FDR + R1.2 §6 cross-reference (provenance: propagated Advisor V1 A-F4 hallucination → my V2-P9 synthesis → V3 §7 Option F text → caught by Codex grep at final pre-SEAL gate); **V3.5-PE SUBSTANTIVE** (Advisor Q2) — Tier 6 instrument language broadened to "production-grade FWER-controlling instrument (DSR per Bailey-Lopez de Prado 2014, OR equivalent like Romano-Wolf stepdown, Westfall-Young permutation FWER)" — no single-technique pre-lock; **V3.5-PF SUBSTANTIVE** (Advisor Q5) — anti-push framing in advisor agent file (out-of-repo audit trail; distinguishes factual-citation abstention from substantive-judgment confidence-qualification); **V3.5-PG SUBSTANTIVE** (Advisor C2) — V_SEAL register references CLAUDE.md HARD CONSTRAINT directly (N = `hypotheses_attempted` not `hypotheses_approved`); **V3.5-PH POLISH** (Advisor C1+Q1) — SD9 item 4 "deferred"→"eligible" + architecture-conditional FWER qualifier (serial individual-strategy commitment; no cross-strategy portfolio diversification at deployment); **V3.5-PI OPERATIONAL** (Codex F6 per METHODOLOGY_NOTES §32) — advisor agent + memory file = V_SEAL audit trail (out-of-repo); Commit A staged files = in-repo artifacts only. **Final SD9 V_SEAL register text (LOCKED 2026-05-19):** (1) Tier 5 gate (R5.1 candidate selection) = Option A: `holdout_sharpe > 0` strict at 15 bps/side. (2) Tier 6 gate (R6.1 promotion class) PRE-COMMITTED: FWER-style multiplicity correction REQUIRED — project-architecture rationale: serial individual-strategy capital commitment; no cross-strategy diversification at deployment → FWER framework (not FDR/BH). Eligible instruments: DSR per BLdP 2014 (preferred); Romano-Wolf stepdown; Westfall-Young permutation FWER; heuristic DSR `sqrt(2*ln(N))` acceptable INTERIM screen only (current `evaluate_dsr.py`; supersession required before capital commitment). BH-FDR NOT eligible (controls FDR not FWER). N specification per CLAUDE.md HARD CONSTRAINT: "NEVER use `hypotheses_approved` as N for DSR — always `hypotheses_attempted` from batch_summary". Threshold + N value + instrument variant locked at R6.1 V_SEAL based on cohort properties. (3) §10 R6.1 cycle REQUIRED for Tier 6 promotion (not optional); instrument variant + threshold + N eligible-not-named WITHIN R6.1 scope. (4) DSR advisory annotation at Tier 5 evaluation = eligible (not obligated) at R5.1 implementation cycle. |

---

## §12 Companion artifact specifications (deferred file-write to SEAL bundle)

**All artifacts below are SPECIFIED in V1 draft; WRITTEN to disk atomically at R3.1d SEAL bundle commit** (analog to R4.1 SEAL bundling R3.1a §12 Errata + `config/execution.yaml` line 42 patch atomically).

| Artifact | File path | Status at V1 | Status at SEAL bundle landing |
|---|---|---|---|
| R3.1d canonical note (THIS document) | `docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md` | EXISTS (V1 DRAFT) | UPDATED to V_SEAL status |
| Phase B alias config | `config/execution_phaseb_spot_15bps.yaml` | SPECIFIED in §5.1 | WRITTEN as new file |
| Schema migration | `experiments.db` runs.cost_anchor_id column | SPECIFIED in §5.2 | APPLIED at SEAL landing |
| CLAUDE.md HARD CONSTRAINT addition | CLAUDE.md HARD CONSTRAINTS section | SPECIFIED in §5.3 | INSERTED at SEAL landing (with SD9 criterion locked) |
| R4.1 hygiene patches | `docs/phase5/R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md` lines 5, 42, 462, 498 | SPECIFIED in §5.4 | APPLIED at SEAL landing |
| CLAUDE.md Phase Marker advance | CLAUDE.md Phase Marker section | TBD at V_SEAL | UPDATED at SEAL landing (atomic with `docs/phase_marker_history.md` per Option 1A 11th trigger) |
| `docs/phase_marker_history.md` atomic update | `docs/phase_marker_history.md` | TBD at V_SEAL | UPDATED at SEAL landing (R4.1 row archived to verbatim entry; R3.1d row added to compact table top) |

**SEAL bundle commit composition (expected 2 commits per R4.1 precedent):**
- Commit A (SEAL artifacts): R3.1d note V_SEAL + new alias config + R4.1 hygiene patches + schema migration script + CLAUDE.md HARD CONSTRAINT insertion
- Commit B (Phase Marker advance + history atomic): CLAUDE.md Phase Marker R3.1d SEALED state + `docs/phase_marker_history.md` atomic update per Option 1A binding (11th empirical trigger)

**NO git tag at SEAL** per CLAUDE.md Tag policy + METHODOLOGY_NOTES.md §32 line 7079 + Phase 5.1/5.2/Phase A/R1.2/R3.1a/R4.1 precedent (Bucket-1 investigation note ≠ arc-level closeout).

---

**End of V_SEAL (sealed 2026-05-19).** R3.1d cost-grid re-anchor V_SEAL canonical artifact with 12 main §§ + cycle metadata header + §12 companion artifact specifications appendix. Cycle through V_SEAL: sub-decision locks SD1-SD9 + 7 mechanical patches P1-P7 (2026-05-18 "ratify all"); V1 → V2 applied 9 patches (V2-P1 through V2-P9); V2 → V3 applied 3 patches (V3-PA path-based mapping; V3-PB footer; V3-PC CI rounding); V3 → V_SEAL applied 6 V3.5 patches (V3.5-PD BLOCKING BH-FDR removal per Codex final F2; V3.5-PE FWER instrument breadth per Advisor Q2; V3.5-PF advisor anti-push framing per Advisor Q5; V3.5-PG CLAUDE.md HARD CONSTRAINT reference per Advisor C2; V3.5-PH SD9 item 4 deferred→eligible + architecture-conditional qualifier per Advisor C1+Q1; V3.5-PI audit trail vs staged scope per Codex F6 + METHODOLOGY_NOTES §32). **SD9 V_SEAL lock (canonical):** Tier 5 = Option A (`holdout_sharpe > 0` strict at 15 bps/side) per cost-realism filter; Tier 6 (R6.1 promotion class) PRE-COMMITTED FWER multiplicity correction REQUIRED (project-architecture: serial individual-strategy capital commitment; no cross-strategy diversification at deployment); BH-FDR NOT eligible (FDR vs FWER framework distinction); instrument + threshold + N variant locked at R6.1 V_SEAL based on cohort properties; R6.1 cycle REQUIRED (not eligible-not-named). Attrition sensitivity analysis from Phase 4 forward-window holdout artifacts (both `holdout_passed` per §6.2 AND strict `holdout_sharpe > 0` per §6.7; informational only; does NOT reopen SD1). R3.1b/c eligible-not-named with Phase 4 paper-trading deployment trigger (§8). 15+ verified Advisor hallucinations across 7 dispatches (~85% rate; Mode A structural; B2 standing rule LOCKED per `feedback_reviewer_routing_subagent_default.md` Reading 3 pilot CLOSED 2026-05-19); Codex cross-model leg load-bearing (caught propagated Advisor hallucination at final pre-SEAL gate via R1.2 grep).
