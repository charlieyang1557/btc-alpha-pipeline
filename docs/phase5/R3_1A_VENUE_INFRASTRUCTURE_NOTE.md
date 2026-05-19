# R3_1A_VENUE_INFRASTRUCTURE_NOTE.md

**Canonical artifact for Phase B Pre-Sequence Roadmap V3 register-event R3.1a (Template B Bucket-1 investigation note; structural analog to PHASE5_1_COST_MODEL_INVESTIGATION_NOTE, PHASE5_2_VENUE_RECONCILIATION_NOTE, PHASE5_A_CLARIFICATION_NOTE, and R1_2_IS_OOS_RANK_CORRELATION_NOTE).**

**Status:** V4 SEAL (canonical sealed artifact at register-event boundary; SEAL fire authorized by Charlie 2026-05-18 register chain #5 "V_SEAL fire authorized"). Cycle scope = single coherent Bucket-1 question per Template B: "how to formally document the `config/execution.yaml` line 42 venue-label discrepancy under Branch.A working assumption per corrected Phase 5.2 §6.4 semantics?" NO git tag at SEAL per CLAUDE.md "Bucket-1 investigation note ≠ arc-level closeout" Tag policy + Phase 5.1 + Phase 5.2 + Phase A + R1.2 precedent.

---

## §0 Cycle Metadata

**Cycle type:** Template B Bucket-1 single-deliverable methodology note (cycle shape α). Cadence shape A (1-cadence: pre-bound option choice + artifact generation per locked rules; no analytical computation in this cycle).

**Cycle boundary:** R3.1a register-event from Phase B Pre-Sequence Roadmap V3 Tier 3. Cycle entry authorized by Charlie at register 2026-05-18 ("Fire R3.1a").

**Trigger:** Phase 5.2 §2.1-reconciliation-lite cycle surfaced a venue-label discrepancy: `config/execution.yaml` line 42 declares "Binance perpetual futures, VIP 0" as the documentary source of the maker/taker fee decomposition, while canonical data `data/raw/btcusdt_1h.parquet` is BTC/USDT 1h SPOT. R3.1a fires the venue-infrastructure formalization to resolve this label-vs-data discrepancy as administrative documentation under Branch.A working assumption.

**Scope binding (pre-bound under Charlie register lock; sealed before draft):**

| Sub-decision | Locked answer | Charlie register |
|---|---|---|
| A | **Branch.A working assumption** per Phase 5.2 §6.4 corrected semantics = SPOT execution (matching canonical data layer is the working operational prior within Phase B planning horizon; no active venue switch under consideration) | "Lock Branch.B prior (A) ... Branch.A working assumption E.2" 2026-05-18 |
| B | Bucket-1 investigation note class (no git tag at SEAL) | Default ratified at same register |
| C | Artifact location `docs/phase5/R3_1A_VENUE_INFRASTRUCTURE_NOTE.md` | Default ratified at same register |

**Derived option choice:** **E.2 = methodology note only; no `config/execution.yaml` modification; preserves byte-identity of all sealed artifacts.**

**§0 scope-bleed trip-wire status:** clean. Cycle work bounded to authorized scope (venue-label discrepancy resolution as administrative documentation under Branch.A SPOT inertia per corrected §6.4). No analytical computation. No engine runs. No `config/execution.yaml` modification. No code changes. No new data acquired.

**Charlie register chain (R3.1a cycle through V2):**

| # | Decision | Register surface |
|---|----------|------------------|
| 1 | R3.1a cycle entry authorize | "Fire R3.1a" |
| 2 | Cycle structure ratification + lock all three sub-decisions + option choice | "Lock Branch.B prior (A) + scope class (B) + artifact location (C), Branch.A working assumption E.2" |
| 3 | V1 reviewer round dispatch + V1 → V2 adjudication (P1 path: re-affirm E.2 with corrected §6.4 semantics) | "dispatch to reviewers for decision point thoughts" + Round 2 P1 convergence |
| 4 | V2 PFR rule-Y dispatch + V2 → V3 adjudication (3 ADOPT mechanical landings + 1 PUSHBACK on Advisor F2 hallucination) | "PFR rule round" |
| 5 | V_SEAL fire + SEAL bundle commit authorize | "V3 patch plan proceed / V_SEAL fire authorized / SEAL bundle commit + Phase Marker advance atomic authorized" |

**Anti-pre-naming binding (preserved throughout):** this note resolves only the venue-label discrepancy as administrative documentation per E.2 option choice under Branch.A working assumption. It does NOT pre-name:
- Eventual R4.1 venue commitment outcome (Branch.A/B/C/D per Phase 5.2 §6.4)
- Whether Branch.A (SPOT execution) will be formally committed at R4.1 (working-assumption status ≠ formal commitment)
- Whether Branch.B (futures execution) may become live at a future R4.1 register-event
- Whether E.2 will be upgraded to E.3 (errata patch to comment) at a future register
- R3.1b/c empirical cost measurement scope or method
- R3.1d post-venue cost-grid re-anchor scope or method
- Any Phase 1-2 cost-model semantics (those are locked by CLAUDE.md Execution Convention §4 `effective_7bps_per_side` rule and CLAUDE.md HARD CONSTRAINTS on `execution.yaml` modification approval + hardcoded-cost prohibition)

---

## §1 Scope and Objective

**§1.1 Question this cycle resolves:**

How should the project formally document the discrepancy between `config/execution.yaml` line 42 (which attributes the fee decomposition to "Binance perpetual futures, VIP 0") and the canonical data source `data/raw/btcusdt_1h.parquet` (which is BTC/USDT 1h SPOT), given that under Phase 5.2 §6.4 corrected semantics, Branch.A (SPOT execution matching canonical data layer) is the working operational prior?

Per Charlie register lock 2026-05-18 + V1 → V2 P1-path adjudication, the answer is **Option E.2: methodology note only, no execution.yaml modification, sealed-content invariance maximized**, with explicit acknowledgment of the surface tension between Branch.A SPOT working assumption and futures-attribution comment (see §5.5).

**§1.2 What this cycle does NOT resolve:**

Per anti-pre-naming binding (§0):

1. R4.1 Phase B venue commitment (Branch.A/B/C/D per Phase 5.2 §6.4) is NOT decided in this cycle. Branch.A working assumption is locked as the **operational prior within R3.1a's E.2 derivation scope**; this is not equivalent to Charlie committing to Branch.A at R4.1.
2. Whether Branch.B may become a live consideration at a future R4.1 register-event is NOT decided.
3. R3.1b/c empirical small-lot venue-conditional cost measurement is NOT performed in this cycle.
4. R3.1d post-venue-commitment cost-grid re-anchor is NOT performed in this cycle.
5. Phase 1-2 cost-model semantics are NOT re-evaluated. The `effective_7bps_per_side` simplification remains in force per CLAUDE.md Execution Convention §4.
6. Phase 5.1 cost-model investigation findings are NOT re-opened.
7. Phase 5.2 venue reconciliation findings are NOT re-opened. R3.1a builds on the §2 mismatch identification + §6.4 Branch structures without re-evaluating them.

---

## §2 Headline Finding (Discrepancy Stated Precisely)

**§2.1 Discrepancy:**

`config/execution.yaml` line 42 reads:

```
# Fee structure (Binance perpetual futures, VIP 0)
```

This is a **YAML comment**, not a structured key-value field. The line attributes the fee decomposition (lines 43-44: `maker_fee_bps: 2.0`, `taker_fee_bps: 4.0`; lines 49, 53: `default_fee_bps: 4.0`, `slippage_bps: 3.0`) to the Binance perpetual futures VIP 0 fee schedule.

The canonical data source for all Phase 0-5 backtests is `data/raw/btcusdt_1h.parquet`, which is **BTC/USDT 1h SPOT** ingested from Binance Vision + CCXT (sources documented in CLAUDE.md "Tech Stack"). All Phase 0-5 sealed research was conducted on SPOT data; no Phase 0-5 work has been performed against Binance perpetual futures data.

**§2.2 Nature of the discrepancy:**

The discrepancy is between the **documentary attribution** of the fee-model decomposition (Binance perpetual futures VIP 0) and the **actual data regime** of all sealed backtests (Binance SPOT). The numeric fee values themselves (4bps taker, 3bps slippage, 7bps effective per side, 14bps round trip) are deliberately treated by CLAUDE.md Execution Convention §4 as `effective_7bps_per_side` — a simplification for baseline validation, NOT a venue-accurate execution simulation.

**§2.3 What the discrepancy is and is not:**

| Dimension | Status |
|---|---|
| Documentary attribution mismatch (comment ↔ data regime) | YES — this is the discrepancy |
| Numeric model error | NO — `effective_7bps_per_side` is by CLAUDE.md Execution Convention §4 a simplification, not a venue-accurate calibration |
| Retroactive backtest invalidation | NO — sealed Phase 1-5 results computed correctly under the simplification model |
| Operational risk to Phase B under Branch.A working assumption | NO — no live tooling reads the line-42 comment programmatically (verified at §5.5) |
| Operational risk if Branch.A formally committed at R4.1 | LOW — documentary discrepancy persists but is fully explained by this note; E.3 upgrade eligible at separate register |
| Operational risk if Branch.B formally committed at R4.1 | NONE — comment matches operational venue at that point |

---

## §3 Source Verification (Line-Anchored Citations)

**§3.1 `config/execution.yaml` content (verified 2026-05-18):**

- Line 42: `  # Fee structure (Binance perpetual futures, VIP 0)`
- Line 43: `  maker_fee_bps: 2.0    # 0.02% per side`
- Line 44: `  taker_fee_bps: 4.0    # 0.04% per side`
- Line 49: `  default_fee_bps: 4.0`
- Line 53: `  slippage_bps: 3.0`
- Lines 55-57: documentation that total effective cost per side = `default_fee_bps + slippage_bps = 7 bps`; round trip = 14 bps

**§3.2 CLAUDE.md Execution Convention §4 (cost model semantics):**

CLAUDE.md "Execution Convention" §4: "Cost model (Phase 1-2): Effective cost = **7bps per side** (14bps round trip). This is a simplification of 4bps taker fee + 3bps slippage. Do NOT treat this as a realistic execution simulator — it is an effective cost model for baseline validation. The `fee_model` registry field must be `effective_7bps_per_side`. Upgrading to a volatility-scaled slippage model is deferred to Phase 3."

CLAUDE.md "Experiment Tracking" rule: "`fee_model` for Phase 1-2: `effective_7bps_per_side` — do NOT use labels that imply separate fee/slippage modeling."

**§3.3 Canonical data source (verified 2026-05-18):**

`data/raw/btcusdt_1h.parquet` — BTC/USDT 1h SPOT. Verified `source` column unique values via `pd.read_parquet('data/raw/btcusdt_1h.parquet')['source'].unique()`: `['binance_vision', 'ccxt_binance']`. CLAUDE.md "Tech Stack" lists `ccxt_binanceus` as a potential source but it is not present in the current canonical parquet. All present sources are SPOT venues.

**§3.4 Phase 5.2 §2.1 reference:**

Phase 5.2 §2 ("Headline Finding: Venue-Mismatch") identified the discrepancy. Phase 5.2 §2.1-reconciliation-lite cycle SEAL discharged the immediate-resolution scope but parked the formal venue-infrastructure formalization decision as eligible-not-named for a separate register-event. R3.1a is that successor register-event.

**§3.5 Phase 5.2 §6.4 Branch.A/B/C/D definitions (verified 2026-05-18):**

Phase 5.2 §6.4 ("Branch register-event resolution paths") defines:
- **Branch.A**: IF Charlie's venue commitment register-event resolves to **spot execution** (matching canonical data layer) → realistic cost basis ≈ 15 bps per side (10 bps spot taker + heuristic slippage component)
- **Branch.B**: IF Charlie's venue commitment register-event resolves to **futures execution** (matching `config/execution.yaml` venue label) → realistic cost basis ≈ 5 bps (current Binance USDⓈ-M VIP-0 futures taker; futures slippage TBD)
- **Branch.C**: both venues OR defers commitment
- **Branch.D**: alternative venue framing not covered by A/B/C

These definitions are load-bearing for R3.1a's option-choice derivation (see §5 and §7).

---

## §4 Historical Context

**§4.1 Origin of the fee decomposition (4bps + 3bps):**

The 4bps taker fee + 3bps slippage decomposition was inspired by the Binance perpetual futures VIP 0 fee schedule (4-5bps taker at retail tier per Binance fee schedule referenced in Phase 5.2 §2 + §3) plus a 3bps slippage estimate. This decomposition was adopted at Phase 0/1A as the baseline cost model and documented in `config/execution.yaml` with the line-42 comment attributing the inspiration source.

**§4.2 Why the decomposition was applied to SPOT data:**

Per CLAUDE.md Execution Convention §4, the fee model is treated as `effective_7bps_per_side` — a SIMPLIFICATION not a venue-accurate calibration. The Phase 0-2 research goal is baseline strategy validation under a pessimistic-but-tractable cost assumption, not exact execution simulation. The 7bps effective cost is intentionally close to a realistic Binance perpetual VIP 0 cost profile because that was the documentary inspiration source at Phase 0 inception, but Phase 0-5 data infrastructure was built on SPOT (Binance Vision bulk + CCXT incremental updates from Binance, all SPOT sources per §3.3). The fee-derivation attribution in the line-42 comment persisted unchanged through subsequent phases.

**§4.3 Phase 5.1 cost-model investigation:**

Phase 5.1 cost-model investigation cycle SEAL examined the realism of the `effective_7bps_per_side` simplification across cost-grid bands (7/13/15/17 bps) and documented the D-classification framework for cost-regime confidence (Phase 5.1 §3.2). Phase 5.1 did NOT change the Phase 1-2 cost-model semantics (those remain locked at `effective_7bps_per_side` per CLAUDE.md Execution Convention §4) but established the framework for Phase 3+ upgrade to volatility-scaled slippage and regime-aware calibration bands. Phase 5.1 §7.1 successor paths are referenced here for context; not re-opened.

**§4.4 Phase 5.2 venue reconciliation:**

Phase 5.2 §2 identified the venue-label discrepancy. Phase 5.2 §6.4 enumerated Branch.A/B/C/D venue commitment options for R4.1. R3.1a builds on these findings without re-evaluating them. The R3.1a cycle output (this note) is the Bucket-1 administrative formalization that Phase 5.2 §2.1-reconciliation-lite cycle parked as eligible-not-named.

---

## §5 Methodology Implications

**§5.1 Cost model is venue-agnostic by CLAUDE.md Execution Convention §4 (Phase 1-2):**

Per CLAUDE.md §3.2 cited above: the `effective_7bps_per_side` model is a simplification, not a venue-accurate execution simulator. The label "Binance perpetual futures, VIP 0" in the comment is documentary attribution of the numeric inspiration source. Whether the actual data was SPOT or perpetual does not change the `effective_7bps_per_side` semantics that all Phase 1-2 backtests operated under.

**§5.2 All sealed Phase 1-5 results are valid as computed:**

No sealed backtest result requires retroactive recomputation. The `effective_7bps_per_side` cost was correctly applied to SPOT OHLCV bars throughout Phase 1-5. Per CLAUDE.md "Execution Convention" the cost model is bar-level deterministic and venue-independent at the simplification layer.

**§5.3 What the discrepancy actually misleads:**

A naïve reader of `config/execution.yaml` line 42 might infer:
- That the canonical data is Binance perpetual futures (it is not — verified §3.3)
- That the 4bps taker / 3bps slippage values were calibrated to be venue-accurate for SPOT (they were not — they were inspired by perpetual VIP 0 per §4.1)
- That a different venue (e.g., true SPOT VIP 0 with ~10bps standard taker per Phase 5.2 §3.1) would warrant a different `effective_cost_bps` value (per CLAUDE.md Execution Convention §4, all Phase 1-2 work uses 7bps regardless of operational venue)

This note exists to disambiguate those potential misreads.

**§5.4 What the discrepancy does not affect:**

- Execution timing semantics (signal at bar N close, fill at bar N+1 open; unchanged)
- Zero-volume handling (`flag_only`; unchanged)
- Look-ahead-bias prohibitions (unchanged)
- Walk-forward attestation domains (unchanged)
- IS-OOS rank correlation R1.2 verdict (independent of venue label — IS/OOS Sharpe ratios are computed against the same SPOT data regardless)
- Phase 4 forward-window holdout artifacts (sealed; use a SEPARATE config file `config/execution_phase4_07bps.yaml`; see §8 OBS 4 for details)

**§5.5 Surface tension acknowledgment (under corrected §6.4 semantics):**

Under Phase 5.2 §6.4 corrected semantics, Branch.A = SPOT execution (matches canonical data layer) is the working operational prior within R3.1a's option-choice scope. The `config/execution.yaml` line 42 comment attributes the fee decomposition to Binance perpetual futures VIP 0. These two facts coexist in the project artifact set under E.2 (no execution.yaml modification).

This is a deliberately preserved surface tension, not an oversight. The disposition rationale:

1. **The comment is documentary fee-derivation attribution, not an operational venue claim.** Per CLAUDE.md Execution Convention §4, the `effective_7bps_per_side` model is explicitly a simplification, not a venue-accurate execution simulator. The line-42 comment records where the 4bps + 3bps decomposition was historically derived from (Binance perpetual VIP 0 fee schedule); it does not assert that the operational data layer is perpetual.

2. **Live code reads only structured numeric keys, not the comment.** Verified at:
   - [`backtest/slippage.py:135-136`](../../backtest/slippage.py#L135-L136): `fee_bps=config["cost_model"]["default_fee_bps"]` + `slippage_bps=config["cost_model"]["slippage_bps"]` (structured YAML keys)
   - [`backtest/execution_model.py:137-138`](../../backtest/execution_model.py#L137-L138): `ConstantSlippage.from_config(config)` + `cost_model.apply(cerebro.broker)` (applies the structured config)
   - No code path reads the line-42 comment programmatically. The comment is documentary only.

3. **Sealed-content invariance preserved.** [`backtest/experiment_registry.py:188`](../../backtest/experiment_registry.py#L188) `compute_config_hash()` uses `hasher.update(path.read_bytes())` which includes YAML comments in the hash. E.2 (no execution.yaml modification) preserves `config_hash` byte-identity for all Phase 1-5 walk-forward runs that hashed execution.yaml at compute time. Modifying the comment (E.1 or E.3) would invalidate all those frozen hash values.

4. **Upgrade trigger preserved at R4.1 register-event (see §7.2).** If Charlie's R4.1 venue commitment formally selects Branch.A (SPOT execution), a separate Charlie register may upgrade R3.1a's E.2 outcome to E.3 (errata to align the comment with the formally-committed SPOT venue). If R4.1 selects Branch.B (futures execution), the comment already matches the operational venue and no errata is needed. The upgrade trigger logic is **inverted from the natural reading** because under corrected §6.4 semantics, Branch.A formal commitment is the case where the comment becomes operationally misleading (SPOT venue with futures-attribution comment), not Branch.B.

The surface tension is intentional and explained; the methodology note functions as the authoritative reference for any reader who encounters the apparent inconsistency.

---

## §6 Grandfathering Rationale (Sealed-Content Invariance)

**§6.1 Pillar 1 — Cost-model abstraction (load-bearing research-validity argument):**

The `effective_7bps_per_side` model is by CLAUDE.md Execution Convention §4 a SIMPLIFICATION abstracted from venue-specific fee structure. This is the load-bearing pillar of grandfathering: the cost computation in Phase 1-5 backtests is a single-parameter simplification (`fee_bps + slippage_bps = effective_cost_bps`), explicitly agnostic to whether the underlying venue would have been perpetual or SPOT at live execution. The line-42 comment's perpetual attribution does not propagate into the cost computation because the computation uses the structured numeric keys directly (`default_fee_bps`, `slippage_bps`), not the comment.

Consequence: research validity of Phase 1-5 sealed results is unaffected by the venue-label discrepancy. The 7bps cost was applied correctly to SPOT data; the comment is a documentary derivation note that does not enter the computation.

**§6.2 Pillar 2 — `config_hash` forensic traceability:**

E.2 preserves `config/execution.yaml` byte-identical. This means all historical `config_hash` values logged in `backtest/experiments.db` remain consistent with the file they were computed against:

- [`backtest/experiment_registry.py:188`](../../backtest/experiment_registry.py#L188) `compute_config_hash()` hashes `execution.yaml + environments.yaml + schemas.yaml` via `hasher.update(path.read_bytes())` (byte-level hash including comments)
- All sealed walk-forward result CSVs and run records reference these `config_hash` values
- All sealed Phase 5 investigation notes (Phase 5.1, Phase 5.2, Phase A, R1.2) that reference `config/execution.yaml` continue to reference the exact same byte content

Consequence: forensic auditability of sealed runs is preserved. A future inspector can re-hash `execution.yaml` and match against registry entries with byte-exact reproducibility.

**§6.3 Pillar 1 vs Pillar 2 distinction:**

Pillar 1 (cost-model abstraction) is the load-bearing argument for research validity. Pillar 2 (`config_hash` forensic traceability) is an additional benefit specific to E.2 vs E.1/E.3. Both are real, but they operate at different layers — pillar 1 establishes that the discrepancy is consequence-free for research correctness regardless of which option (E.1/E.2/E.3) is chosen; pillar 2 establishes that E.2 specifically preserves an additional forensic-audit-trail property.

**§6.4 Why E.2 rather than E.1 or E.3 under Branch.A working assumption:**

E.1 (errata patch only) and E.3 (errata + note) both require modification of `config/execution.yaml`, which per CLAUDE.md HARD CONSTRAINT requires explicit human approval. Under Branch.A working assumption (SPOT execution = current data regime per corrected §6.4 semantics, no active venue switch under consideration), no live tooling reads the line-42 comment programmatically (verified at §5.5 pillar 2); the discrepancy is administrative documentation only. E.2 is sufficient and reversible-upgradeable: if Branch.A is ever formally committed at R4.1 (different from working-assumption status), a separate Charlie register can authorize an E.1-style errata commit to the comment at that point.

**§6.5 What grandfathering means here:**

Phase 0-5 work is "grandfathered" in the sense that:
- The fee model attribution in line 42 is retained as the historical record of the documentary inspiration source
- The numeric model (`effective_7bps_per_side`) is retained as the operational semantics per CLAUDE.md Execution Convention §4
- The mismatch between attribution and data regime is documented in this note rather than corrected in the source config

This preserves the historical audit trail: a future reader can see both the original line-42 attribution AND this note explaining its documentary-not-operational nature.

---

## §7 Forward-Treatment Policy

**§7.1 Under Branch.A working assumption (current operational prior per corrected §6.4):**

No operational impact from the discrepancy. The line-42 comment remains as documentary fee-derivation attribution per §5.5 disposition. This note serves as the authoritative reference for understanding the discrepancy. Phase B Tier 3-6 work that operates under Branch.A SPOT inertia inherits sealed-content invariance from `config/execution.yaml`.

**§7.2 Upgrade trigger to E.3 (eligible-not-named successor register; corrected §6.4 trigger logic):**

The upgrade trigger to E.3 is **inverted from the natural reading** under corrected §6.4 semantics:

| R4.1 outcome | Comment status | Errata trigger |
|---|---|---|
| Branch.A (SPOT execution) formally committed at R4.1 | Futures-attribution comment becomes operationally misleading for the formally-committed SPOT venue | **E.3 errata becomes eligible** (separate Charlie register to align comment with operational venue) |
| Branch.B (futures execution) formally committed at R4.1 | Comment matches formally-committed venue | No errata needed; E.2 remains terminal |
| Branch.C (both / defer) formally committed at R4.1 | Mixed disposition; per-venue framing | Charlie determines per-Branch.C resolution |
| Branch.D (alternative framing) at R4.1 | Charlie-specified disposition | Per Branch.D resolution |

At the upgrade-trigger register-event:
- Per CLAUDE.md HARD CONSTRAINT, `config/execution.yaml` modification requires explicit human approval at that register.
- This note remains as the historical record regardless of whether E.3 ever fires; the upgrade would append a §12 Errata section in the style of Phase A V4 SEAL §11 Errata, preserving sealed-content invariance for the current V_SEAL.

**§7.3 What this cycle does NOT pre-name about §7.2:**

R3.1a does not pre-name:
- Whether Branch.A will be formally committed at R4.1 (working-assumption status ≠ formal commitment)
- Whether Branch.B may become live at R4.1
- When the E.3 upgrade trigger would activate (if at all)
- What specific replacement comment wording would be authorized at that point
- Whether the cost-model semantics themselves (independent of the label) would change at R4.1 (that question is in R3.1d's scope, not R3.1a)

These remain eligible-not-named per anti-pre-emption discipline.

---

## §8 OBSERVATIONS (Anti-Pre-Naming Forward-Only)

Per anti-pre-emption invariant codified across Phase 5.1, Phase 5.2, Phase A, and R1.2 SEAL precedent — observations below are surfaced as forward-only carry-forward signals; they do NOT pre-name any future Charlie register outcome.

**OBSERVATION 1 (administrative-vs-operational classification):** The line-42 discrepancy is administrative documentation, not an operational defect, under Branch.A working assumption per §5.5 disposition. Eligible-not-named at any future Branch.A formal commitment at R4.1: re-evaluate whether the administrative classification still holds at that venue-formalization point.

**OBSERVATION 2 (cost-model semantics independence):** The `effective_7bps_per_side` simplification is independent of the line-42 attribution per CLAUDE.md Execution Convention §4. Phase 3+ upgrade to volatility-scaled slippage (per Phase 5.1 successor paths) is a separate question from venue-label resolution.

**OBSERVATION 3 (sealed-content invariance):** E.2 preserves byte-identity of `config/execution.yaml`. All sealed `config_hash` values in `backtest/experiments.db` remain consistent. Verified empirically at [`backtest/experiment_registry.py:188`](../../backtest/experiment_registry.py#L188) (hash computed at write-time via `hasher.update(path.read_bytes())` including comments; no read-time integrity check).

**OBSERVATION 4 (Phase 4 forward-window artifact independence):** Phase 4 forward-window holdout artifacts (sealed at `data/phase2c_evaluation_gate/phase4_forward_2026_*/`) use a SEPARATE execution config FAMILY of per-cost-band files: `config/execution_phase4_{07,13,15,17}bps.yaml` (sample instance: `config/execution_phase4_07bps.yaml`), NOT `config/execution.yaml`. The 4-band cost-grid corresponds to Phase 5.1 §3.2 D-classification framework. The `holdout_summary.json` structure uses `execution_config_path` + `execution_config_sha256` to sha-lock each specific phase-4 config band, and `forward_window_metadata.parquet_data_sha256` to sha-lock the data parquet. E.2's byte-identity preservation of `config/execution.yaml` is therefore orthogonal to Phase 4 holdout artifact integrity (those are integrity-locked against different files per cost-band). The E.2 preservation argument applies specifically to Phase 1-3 walk-forward + Phase 2C experiment_registry entries that hashed `config/execution.yaml`.

**OBSERVATION 5 (Phase B venue-commitment decoupling):** R3.1a (administrative documentation under Branch.A working assumption) and R4.1 (operational venue commitment) are decoupled by E.2. Resolving R3.1a does not pre-commit R4.1 outcome to any specific branch. Per §7.2 inverted trigger logic, the E.3 upgrade is eligible specifically under Branch.A formal commitment at R4.1; Branch.B (futures execution) formal commitment does NOT trigger E.3 (comment matches operational venue at that point); Branch.C / Branch.D per Charlie determination at R4.1 register-event.

**OBSERVATION 6 (R3.1b/c empirical cost cycle is separate):** The numeric cost model question (whether 7bps is realistic for SPOT live execution at small lot sizes) is in R3.1b/c scope, not R3.1a. R3.1a does not pre-name whether R3.1b/c will be fired or what their conclusions will be.

**OBSERVATION 7 (R3.1d post-venue-commitment cost-grid re-anchor):** If R4.1 ever resolves to a venue that requires cost-grid re-anchoring (e.g., Branch.A formal commitment with SPOT-realistic 15bps; Branch.B with futures-realistic 5bps; Branch.D alternative), R3.1d may re-anchor the cost-grid against the committed venue. R3.1a does not pre-name R3.1d's scope or method.

---

## §9 Reserved Decisions (Eligible-Not-Named)

Per anti-pre-emption invariant — no decision pre-named in this cycle. Reserved for separate Charlie register-event boundary:

1. R4.1 Phase B venue commitment (Branch.A/B/C/D per Phase 5.2 §6.4)
2. R3.1b/c empirical small-lot venue-conditional cost measurement scope + method
3. R3.1d post-venue-commitment cost-grid re-anchor scope + method
4. Phase B Tier 2 conditional prereqs (R2.1 / R2.2 / R2.3) — informed by R1.2 SEAL findings; sequencing eligible-not-named
5. R5.1 Phase B candidate-subset commitment (R1.2 AMBIGUOUS verdict binds harder; 3-candidate IS-OOS-consistent sub-cohort framing eligible per R1.2 OBS 5)
6. R5.2 predeclared selection-inflation handling cycle
7. R6.1 Phase B promotion class (minimum-trade-count gate + per-strategy multiplicity pre-bind; pause branch eligible)
8. Tier-0 pause / strategic-absorption per V3 top note
9. Upgrade of R3.1a E.2 outcome to E.3 (only triggers under Branch.A FORMAL commitment at R4.1 per corrected §6.4 semantics; see §7.2)
10. Cost-model semantics upgrade beyond `effective_7bps_per_side` (deferred to Phase 3 per CLAUDE.md Execution Convention §4; Phase 5.1 successor paths apply)
11. Other Charlie-specified reserved decisions

---

## §10 V# Anchor Chain (R3.1a)

| V# | State | Description |
|----|-------|-------------|
| V1 | ARCHIVED | Pre-reviewer-round draft. Sub-decisions A/B/C locked per Charlie register 2026-05-18; option choice E.2 derived from Sub-decision A. Structure mirrored R1.2 / Phase A / Phase 5.1 / Phase 5.2 sealed artifact format. |
| **V2** | **REVISED-POST-V1-REVIEW** | Post-V1-reviewer-round revised draft after 2-leg subagent dispatch (Codex + quant-research-advisor parallel). Round 1 verdict: Codex BLOCK (3 BLOCKING + 1 SUBSTANTIVE + 1 MINOR); Advisor APPROVE-WITH-FINDINGS (4 SUBSTANTIVE/MINOR + 2 HALLUCINATIONS). Reviewer reliability this round: 0/2 stalls; 2/2 verified Advisor hallucinations (Advisor F1 fabricated execution.yaml `fee_mode: taker_fee` + `notes:` field that doesn't exist; Advisor F4 claimed `compute_config_hash` at line 186 when actually line 188) — **PUSHBACK applied on both** per Option II citation verification. Round 2 decision-point round on P1/P2/P3 (re-affirm E.2 with corrected semantics / switch to E.3 / re-frame) converged on P1 with both legs + Advisor's required condition (V2 must explicitly name the surface tension under corrected §6.4 semantics). V1→V2 applied 8 ADOPT patches: (1) Codex F1 BLOCKING — Branch.A/B semantics correction throughout per Phase 5.2 §6.4 actual definitions (Branch.A = SPOT execution; Branch.B = futures execution); (2) Codex F2 BLOCKING — §3.3 parquet sources corrected to actual contents `binance_vision + ccxt_binance` only (CLAUDE.md Tech Stack notes `ccxt_binanceus` is potential but verified absent); (3) Codex F3 BLOCKING — §8 OBS 4 restructured to reflect actual Phase 4 holdout summary structure (separate `execution_phase4_07bps.yaml` config file; `execution_config_path` + `execution_config_sha256` + `forward_window_metadata.parquet_data_sha256` fields; NO `config_hash` in `forward_window_metadata`); (4) Codex F4 SUBSTANTIVE — HARD CONSTRAINT misattribution corrected throughout (`effective_7bps_per_side` rule is in CLAUDE.md Execution Convention §4 / Experiment Tracking; HARD CONSTRAINTS section binds only `execution.yaml` modification approval + hardcoded-cost prohibition); (5) Codex F5 MINOR — symbolic `V_SEAL` placeholder replaced with concrete V2 / (pending) V3 / V_SEAL slots per R1.2 / Phase 5.x precedent; (6) Advisor F3 SUBSTANTIVE — §6 restructured for pillar separation (pillar 1 cost-model abstraction load-bearing for research validity; pillar 2 `config_hash` forensic traceability additional benefit specific to E.2); (7) Advisor F5 MINOR — §7.2 upgrade trigger language expanded to full §6.4-anchored description with **inverted trigger logic table** (Branch.A formal commitment is the case where errata becomes operationally relevant, not Branch.B); (8) **NEW SECTION §5.5** — Surface tension acknowledgment per Advisor's P1 required condition: explicit naming of Branch.A SPOT working assumption coexisting with futures-attribution comment, with disposition rationale (4 items: documentary not operational + live code reads structured keys not comment + sealed-content invariance preserved + upgrade trigger preserved); items (i)-(ii) map to §6.1 Pillar 1 (cost-model abstraction); item (iii) maps to §6.2 Pillar 2 (config_hash forensic traceability); item (iv) maps to §7.2 forward-treatment policy. Cross-model diversity validated: Codex caught Branch semantics reversal + parquet source false claim + holdout summary structure false claim + HARD CONSTRAINT misattribution (4 BLOCKING/SUBSTANTIVE that Advisor missed); Advisor caught grandfathering pillar conflation + surface-tension required-condition (2 SUBSTANTIVE that Codex missed). |
| **V3** | **REVISED-POST-PFR-RULE-Y** | Post-PFR-rule-Y re-review revised draft after 2-leg subagent dispatch (Codex + quant-research-advisor parallel). Round 3 (PFR) verdict: Codex BLOCK (2 fixes: P3-F1 BLOCKING + P7-F1 MINOR); Advisor APPROVE-WITH-MINOR (2 findings: F1 POLISH partial + F2 POLISH HALLUCINATION). Reviewer reliability this round: 0/2 stalls; 1/2 verified Advisor hallucination (Advisor F2 falsely claimed Phase 5.2 does not use §6.4 numbering — verified false at `docs/phase5/PHASE5_2_VENUE_RECONCILIATION_NOTE.md` line 261 `**§6.4 Branch register-event resolution paths**`). **PUSHBACK applied on Advisor F2** per Option II citation verification. V2→V3 applied 3 ADOPT patches: (1) **Codex P3-F1 BLOCKING** — §8 OBS 4 broadened Phase 4 config reference from singular 07bps instance to *bps family (07/13/15/17 bps verified via `ls config/execution_phase4_*bps.yaml`; 4 files exist + matching 4 holdout_summary.json directories at `data/phase2c_evaluation_gate/phase4_forward_2026_*bps_v1/`); (2) **Codex P7-F1 MINOR** — §8 OBS 5 restricted upgrade trigger to Branch.A formal commitment only per §7.2 inverted logic table; Branch.B explicitly excluded from triggering; Branch.C/D per Charlie determination; (3) **Advisor F1 ADOPT-with-modification** — §10 V2 "4 pillars" → "4 items" with explicit cross-mapping (items i-ii → §6.1 Pillar 1; item iii → §6.2 Pillar 2; item iv → §7.2). Cumulative R3.1a cycle reviewer reliability across 3 rounds (V1 round + decision-point Round 2 + V2 PFR): 0/6 Codex stalls + 3/6 verified Advisor hallucinations — cross-model diversity LOAD-BEARING this cycle (Codex caught Branch.A/B semantics reversal + parquet sources + holdout summary structure + HARD CONSTRAINT misattribution + Phase 4 config family + OBS 5 internal inconsistency that Advisor would have missed in single-leg runs). V3 patches all mechanical literal landings of reviewer-stated PFR findings → SKIP further PFR round per `feedback_reviewer_routing_subagent_default.md` routing routine. |
| **V4** | **SEAL** | Canonical sealed artifact at register-event boundary (Charlie SEAL register fire 2026-05-18 "V_SEAL fire authorized + SEAL bundle commit + Phase Marker advance atomic authorized"; V3 patches all mechanical literal landings → SKIP further PFR per routing routine). |

---

## §11 References

**Sealed project artifacts (read-only at this cycle):**
- `docs/phase5/PHASE5_2_VENUE_RECONCILIATION_NOTE.md` (Phase 5.2 V4 SEAL; §2 venue-mismatch finding identified the discrepancy R3.1a formalizes; §6.4 Branch.A/B/C/D structures load-bearing for §3.5 + §7.2 inverted trigger logic)
- `docs/phase5/PHASE5_1_COST_MODEL_INVESTIGATION_NOTE.md` (Phase 5.1 V4 SEAL; §3.2 D-classification + §7.1 successor paths referenced for §4.3 historical context)
- `docs/phase5/PHASE5_A_CLARIFICATION_NOTE.md` (Phase A V4 SEAL + §11 Errata; §11 referenced as precedent for §7.2 upgrade-via-errata-appendix pattern)
- `docs/phase5/R1_2_IS_OOS_RANK_CORRELATION_NOTE.md` (R1.2 V4 SEAL; §10 anchor chain + §11 References format referenced for R3.1a artifact structure)
- `config/execution.yaml` (byte-identical; R3.1a E.2 preserves this)
- `CLAUDE.md` Phase Marker + HARD CONSTRAINTS (`config/execution.yaml` modification approval rule + hardcoded-cost prohibition) + Execution Convention §4 (`effective_7bps_per_side` simplification rule)
- [`backtest/experiment_registry.py:188`](../../backtest/experiment_registry.py#L188) (`compute_config_hash()` definition; referenced for §5.5 pillar 2 + §6.2 sealed-content invariance verification)
- [`backtest/slippage.py:135-136`](../../backtest/slippage.py#L135-L136) (`config["cost_model"]["default_fee_bps"]` + `slippage_bps` reads; referenced for §5.5 pillar 2 live-code verification)
- [`backtest/execution_model.py:137-138`](../../backtest/execution_model.py#L137-L138) (`ConstantSlippage.from_config(config)` + apply; referenced for §5.5 pillar 2 live-code verification)
- `config/execution_phase4_07bps.yaml` (separate Phase 4 execution config; referenced for §8 OBS 4 holdout artifact independence)
- Sample `data/phase2c_evaluation_gate/phase4_forward_2026_07bps_v1/holdout_summary.json` (verified structure: `execution_config_path` + `execution_config_sha256` + `forward_window_metadata.parquet_data_sha256`; referenced for §8 OBS 4)

**No analytical computation in this cycle; no analysis artifact generated.**

**Cross-reviewer adjudication corpus (this cycle):**
- R1.2 SEAL session reviewer routing routine applied (2-leg subagent default per `feedback_reviewer_routing_subagent_default.md`)
- R3.1a V1 DRAFT reviewer round: Codex (BLOCK; 5 findings) + quant-research-advisor (APPROVE-WITH-FINDINGS; 6 findings); per-fix adjudication recorded in transcript + §10 V2 description
- R3.1a P1/P2/P3 decision-point Round 2: Codex (lean P1) + advisor (lean P1 with required condition); CONVERGED on P1
- R3.1a V2 PFR rule-Y round: (PENDING) conditional per new-content magnitude in V2

**External literature posture:** None invoked. All factual claims grounded in sealed in-repo artifacts + direct file inspection.

---

**End of V4 SEAL.** R3.1a Bucket-1 investigation cycle SEALED at this register-event boundary. Cycle resolved Phase 5.2 §2.1-reconciliation-lite parked venue-infrastructure formalization decision as: **Option E.2 (methodology note only; no `config/execution.yaml` modification) under Branch.A working assumption per corrected Phase 5.2 §6.4 semantics**. Surface tension between Branch.A SPOT working assumption and futures-attribution comment is intentionally preserved per §5.5 disposition rationale (4 items mapped to §6.1 Pillar 1 + §6.2 Pillar 2 + §7.2 forward-treatment). Upgrade trigger to E.3 eligible at separate Charlie register IFF R4.1 formally commits Branch.A (SPOT execution) per §7.2 inverted trigger logic; Branch.B formal commitment does NOT trigger (comment matches operational venue at that point); Branch.C/D per Charlie determination. 7 OBSERVATIONS named anti-pre-naming + 11 reserved decisions eligible-not-named for separate Charlie register-event boundaries. Cumulative R3.1a cycle reviewer reliability across 3 rounds: 0/6 Codex stalls + 3/6 verified Advisor hallucinations — cross-model diversity load-bearing this cycle. **NO git tag at SEAL** per CLAUDE.md "Bucket-1 investigation note ≠ arc-level closeout" Tag policy + Phase 5.1 + Phase 5.2 + Phase A + R1.2 precedent. Phase Marker + atomic `docs/phase_marker_history.md` update follow at SEAL bundle commit per Option 1A binding 9th empirical trigger.

---

## §12 Errata (appended post-SEAL per sealed-content invariance discipline)

**Errata E.3 (2026-05-18; R4.1 Phase B formal Branch.A commitment register-event):**

R3.1a V4 SEAL §7.2 inverted trigger logic table named E.3 errata as eligible IFF R4.1 formally commits Branch.A (SPOT execution). Charlie register chain fire 2026-05-18 ("fire, authorized R3.1a E.3 upgrade trigger and Tier 4 R4.1" + sub-decision Round 1 dispatch + PFR cross-validation dispatch + "ratify all") formally commits Branch.A per companion R4.1 SEAL artifact at [`docs/phase5/R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md`](R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md). E.3 errata fires under this register chain per R3.1a §7.2 inverted trigger logic table row 1 (Branch.A formal commitment → comment "becomes operationally misleading" → E.3 errata eligible).

**Post-SEAL append protocol:** §12 is appended via separate post-SEAL commit per Phase A `9c00f59` precedent (`git log --oneline -- docs/phase5/PHASE5_A_CLARIFICATION_NOTE.md` shows `ab62b2e` Phase A SEAL fire + `9c00f59` post-SEAL §11 errata append, 21 insertions). R3.1a V4 SEAL §§0-11 remain **byte-identical** post-E.3; only §12 is appended. Sealed-content invariance preserved.

**§12.1 E.3 patch to `config/execution.yaml` line 42 (locked per SD4 + PFR ratification):**

Old (pre-E.3, sealed in `config/execution.yaml` line 42):
```yaml
  # Fee structure (Binance perpetual futures, VIP 0)
```

New (post-E.3, atomic with SEAL bundle commit):
```yaml
  # Effective SPOT execution cost model (7 bps/side simplification; not venue-accurate; see CLAUDE.md Execution Convention §4)
```

**§12.2 Wording rationale (per Codex Round 1 PUSHBACK + PFR ratification):**

- Removes false "perpetual futures" attribution under Branch.A formal commitment (R4.1 SEAL elevates working-assumption to formal commitment per Phase 5.2 §6.4)
- Avoids false "Spot VIP 0 basis" attribution that calling agent Round 1 SD4 options (a) and (b) would have introduced (per Phase 5.2 §3 fee table: Binance Spot VIP 0 taker ≈ 10bps, not 4bps; the config retains 4bps fee + 3bps slippage = 7bps effective which traces to perp VIP 0 derivation per R3.1a §4.1, not Spot VIP 0)
- "Effective" + "simplification" + "not venue-accurate" framing makes documentary-not-operational claim explicit per CLAUDE.md Execution Convention §4
- "see CLAUDE.md Execution Convention §4" anchors to the authoritative source for the simplification framing (preserves R3.1a §6.1 Pillar 1 invariance)

**§12.3 `config_hash` impact (per X3' technical scope verification):**

`compute_config_hash()` at [`backtest/experiment_registry.py:188`](../../backtest/experiment_registry.py#L188) hashes the byte content of three config files defined at [`backtest/experiment_registry.py:48`](../../backtest/experiment_registry.py#L48) (`CONFIG_FILES`):
- `config/execution.yaml`
- `config/environments.yaml`
- `config/schemas.yaml`

The hash uses `hasher.update(path.read_bytes())` per file and returns `f"sha256:{hasher.hexdigest()[:16]}"` (sha256 prefix + 16 hex chars truncation; 18 chars total returned). Byte content includes YAML comments. Modifying the line-42 comment changes the `execution.yaml` byte content and therefore changes the returned hash for all future runs.

**§12.4 Pre-E.3 + Post-E.3 canonical hash state (per X4' + A4 V3 update):**

- Parent commit at V1 DRAFT time: `46615cf` (recompute at SEAL bundle landing in case of intervening commits)
- **Pre-E.3** `config_hash` (computed on current `execution.yaml` with line 42 = "Binance perpetual futures, VIP 0"; independently verified via Python `hashlib.sha256` reproduction of `compute_config_hash()` 2026-05-18): `sha256:3850424a0ef2d292` — Codex Round 1 LBR + PFR Codex both independently corroborated
- **Post-E.3** `config_hash` (computed on proposed post-patch `execution.yaml` with line 42 = "Effective SPOT execution cost model (7 bps/side simplification; not venue-accurate; see CLAUDE.md Execution Convention §4)"; Codex PFR independent computation via byte-level reproduction): `sha256:db2ce75bd41e8513`
- Both hashes use `hasher.update(path.read_bytes())` per file in `CONFIG_FILES` (3-file scope: `execution.yaml` + `environments.yaml` + `schemas.yaml`); both are 16-hex-char truncations of full SHA-256
- Pre-E.3 byte content of `execution.yaml` is recoverable post-E.3 via `git show <pre-E.3-parent-commit-SHA>:config/execution.yaml` for any auditor who needs to verify historical `config_hash` values

**§12.5 Pillar 1 preservation (per R3.1a §6.1 invariance; per X8):**

Research validity of all sealed Phase 1-5 backtests is **unaffected** by E.3 fire. The `effective_7bps_per_side` cost computation uses structured numeric keys (`default_fee_bps`, `slippage_bps`) per [`backtest/slippage.py:135-136`](../../backtest/slippage.py#L135-L136) + [`backtest/execution_model.py:137-138`](../../backtest/execution_model.py#L137-L138), NOT the line-42 comment. Per R3.1a §6.1 (sealed; preserved):

> The cost computation in Phase 1-5 backtests is a single-parameter simplification (`fee_bps + slippage_bps = effective_cost_bps`), explicitly agnostic to whether the underlying venue would have been perpetual or SPOT at live execution.

E.3 changes only the documentary comment; the numeric keys and computation are byte-identical post-E.3. **No backtest result requires retroactive recomputation.**

**§12.6 Pillar 2 cost (per R3.1a §6.3 classification):**

E.3 invalidates byte-identity between historical `experiments.db` entries (which logged `config_hash` values computed against pre-E.3 byte content) and the post-E.3 `execution.yaml` content. A future inspector re-hashing `execution.yaml` after E.3 will get a different hash than the registry entries. This is the Pillar 2 cost being spent at R4.1 SEAL. Per R3.1a §6.3 (sealed):

> Pillar 2 (`config_hash` forensic traceability) is an additional benefit specific to E.2 vs E.1/E.3. ... pillar 2 establishes that E.2 specifically preserves an additional forensic-audit-trail property.

Under E.3 fire, Pillar 2 is no longer preserved for entries that hashed against pre-E.3 byte content. Reconstruction remains possible via `git show <pre-E.3-commit>:config/execution.yaml` per §12.4. Pillar 1 invariance is not affected.

**§12.7 Historical `experiments.db` entries retain pre-E.3 hash intentionally (per X7):**

All Phase 1-5 walk-forward and Phase 2C experiment_registry entries that logged `config_hash` retain their **pre-E.3 hash value** (`sha256:3850424a0ef2d292` for entries logged against the pre-E.3 byte content with current `environments.yaml` + `schemas.yaml`) in the SQLite database. These entries are **NOT** retroactively updated to post-E.3 hash values. **This is intentional and expected post-E.3.** A future reader encountering hash mismatches between registry entries and current `execution.yaml` content should understand this as documented expected state, not a data-integrity failure.

**§12.7.1 No read-time `config_hash` recomputation guard (per V1 reviewer round Advisor LBR1; verified):**

`compute_config_hash()` is called at write-time only. Verified via two grep commands:

Narrow grep `grep -n "compute_config_hash" backtest/experiment_registry.py` returns exactly 2 lines:
- Line 188: `def compute_config_hash() -> str:` (function definition)
- Line 265: `run_data.setdefault("config_hash", compute_config_hash())` — **sole call site**, inside `insert_run()` insert/create path

Broader grep `grep -n "config_hash" backtest/experiment_registry.py` returns 4 lines (above 2 plus):
- Line 62: `config_hash TEXT,` (schema declaration only)
- Line 243: docstring mention only

No read-time integrity guard exists in `experiment_registry.py`. Post-E.3, historical `experiments.db` entries are queried without automated mismatch warnings. Behavior is consistent with §12.7 intentional-retention framing.

**§12.8 Phase 4 forward-window artifact independence carve-out (per X5; per R3.1a §8 OBS 4):**

Phase 4 forward-window holdout artifacts (sealed at `data/phase2c_evaluation_gate/phase4_forward_2026_*bps_v1/`) use a SEPARATE execution config FAMILY: `config/execution_phase4_{07,13,15,17}bps.yaml` (4 files for 4 cost bands per Phase 5.1 §3.2 D-classification framework). Phase 4 holdout artifacts integrity-lock against these specific per-band files via `execution_config_path` + `execution_config_sha256` fields, NOT against `config/execution.yaml`. **E.3 does NOT affect Phase 4 forward-window holdout artifact integrity.** Phase 4 `execution_config_sha256` values remain byte-identical to their per-band config files post-E.3.

**§12.9 Numeric semantics + R3.1d non-resolution explicit (per X8):**

E.3 is **comment-level documentary alignment only**. It does NOT:
- Change any numeric value in the `cost_model` block of `execution.yaml` (`default_fee_bps`, `slippage_bps`, `maker_fee_bps`, `taker_fee_bps`, derived `effective_cost_bps` all byte-identical post-E.3)
- Imply or resolve R3.1d (post-venue cost-grid re-anchor — remains eligible-not-named for separate Charlie register-event)
- Claim spot fee-schedule accuracy (the replacement comment explicitly frames the 7bps as "not venue-accurate" + "simplification")
- Re-open Phase 1-2 cost-model semantics (locked at `effective_7bps_per_side` per CLAUDE.md Execution Convention §4)
- Re-open Phase 5.1 cost-model investigation findings
- Pre-name any Phase 5.2 §6.4 Branch.A sub-question (Path 1 paper trading basis, Path 2 L2 replay, Stratum A D-I classification — all eligible-not-named per R4.1 SEAL §6 + R4.1 §10)

**Errata scope:** comment-level documentary alignment only. The wording change reflects Branch.A formal commitment (R4.1 SEAL operationalizes SPOT as the venue) without claiming venue-accuracy of the cost model and without resolving R3.1d. All Phase 1-5 factual findings remain unchanged because they were computed on actual SPOT data under venue-agnostic `effective_7bps_per_side` semantics; the line-42 comment is documentary attribution only. Pillar 1 invariance preserved (research validity unaffected); Pillar 2 cost spent (forensic byte-identity traceability degraded post-E.3 fire date; reconstruction via git history remains possible).

**§12.10 SEAL bundle commit scope (per SD6 + X6'):**

R4.1 SEAL bundle commit (atomic) lands:
1. R4.1 SEAL artifact at `docs/phase5/R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md`
2. R3.1a §12 Errata appendix (this content; appended to existing sealed R3.1a artifact post-SEAL per Phase A `9c00f59` precedent)
3. `config/execution.yaml` line 42 patch per §12.1
4. CLAUDE.md Phase Marker advance + `docs/phase_marker_history.md` atomic update (per Option 1A atomicity binding 10th empirical trigger)

Reviewer dispatch on combined R4.1 V1 + §12 Errata V1 + `execution.yaml` diff V1 precedes V_SEAL fire per X6'.

**§12.10.1 Operational discipline for Phase Marker advance (per V1 reviewer round Advisor LBR2):**

CLAUDE.md Phase Marker entry for R4.1 SEAL is drafted **pre-commit** with placeholder `PENDING` for SEAL commit SHA + push-commit SHA (since these are not yet known at draft time). Placeholders are filled at commit-landing time before the atomic SEAL bundle commit fires. Established discipline per R3.1a precedent (commit `46615cf` = R3.1a Phase Marker advance; placeholders filled in commit message at landing).

**§12.11 Cross-reference:**

For full context on R4.1 formal Branch.A commitment, see companion sealed artifact at [`docs/phase5/R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md`](R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md). For R3.1a §§0-11 sealed content (byte-identical post-E.3), see §§0-11 above.

**§12.12 Verification method — code path, NOT parsed-YAML form (per V1 reviewer round Codex LBR):**

Canonical verification of `config_hash` MUST use the [`compute_config_hash()`](../../backtest/experiment_registry.py#L188) code path at [`backtest/experiment_registry.py:188`](../../backtest/experiment_registry.py#L188), which performs `hasher.update(path.read_bytes())` per file in `CONFIG_FILES` (byte-level hash including YAML comments). Verification MUST NOT use a parsed-YAML form (e.g., `yaml.safe_load(path) → json.dumps → sha256`) because parsed-YAML **strips comments** during parsing and would silently report a stable hash even after the line-42 comment is replaced. Any SEAL checklist item or future audit script that uses parsed-YAML form would produce a **false-negative invariance check** post-E.3, masking the expected hash change.

Verified by Codex V1 + PFR round LBRs via independent reproductions. Parsed-YAML form is NON-CANONICAL by definition — different serialization choices (e.g., `yaml.safe_load + json.dumps(sort_keys=True)` vs `yaml.safe_load + json.dumps(sort_keys=False)` vs `yaml.dump` round-trip) produce DIFFERENT non-canonical hash values for the same source file. Empirically Codex PFR computed `aa265c14a4760d80` for one parsed-YAML form; another reproduction yielded a different value. The canonical `compute_config_hash()` byte-level hash is well-defined:
- Pre-E.3: `sha256:3850424a0ef2d292` (current line 42 = "Binance perpetual futures, VIP 0")
- Post-E.3: `sha256:db2ce75bd41e8513` (Codex PFR independent computation via byte-level reproduction of the proposed line-42 patch)

Critical asymmetry: any parsed-YAML form silently produces the SAME hash before and after the comment change (because comments are stripped during parse); the canonical form changes deterministically. SEAL verification correctness requires the code path. Operational tooling must use `compute_config_hash()` at [`backtest/experiment_registry.py:188`](../../backtest/experiment_registry.py#L188), NOT a parsed-YAML round-trip.

---

**End of §12 Errata E.3 appendix.** R3.1a V4 SEAL §§0-11 byte-identical preserved. §12 appended via separate post-SEAL commit per Phase A `9c00f59` precedent. Pillar 1 research validity invariant; Pillar 2 forensic byte-identity cost spent + documented (Pillar 2 transitions from pre-E.3 hash `sha256:3850424a0ef2d292` as forensic anchor to post-E.3 hash as new canonical identifier for subsequent runs). Companion artifact R4.1 SEAL at [`docs/phase5/R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md`](R4_1_PHASE_B_VENUE_COMMITMENT_NOTE.md) formally commits Branch.A; this §12 fires E.3 errata under that formal commitment.
