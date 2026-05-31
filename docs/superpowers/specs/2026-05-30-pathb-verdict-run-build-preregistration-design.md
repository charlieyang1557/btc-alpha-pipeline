# Path B — Verdict-Run Build Pre-Registration — Design Spec

**Date:** 2026-05-30 (UTC)
**Status:** DRAFT — pending Charlie review-gate register. NOT yet authorized for implementation or commit.
**Commit-order role:** This doc is committed **BEFORE** any build edit or data-touch in the verdict-run cycle. Its commit-order is the anti-hindsight evidence (mirrors the Step −1 LOCK; METHODOLOGY_NOTES §3.3). Anything it under-specifies must be pinned here before results are seen.
**Cycle class:** Build-then-run continuation of the bounded one-cycle Path B falsification test. Closes the harness's verdict-run build gaps + 2 LOCK-conformance fixes, then runs the gauntlet to produce the (advisory) earned-negative-or-B-positive evidence.
**Predecessor:** Path B harness arc (Sections A–E, committed on `pathb-mechanism-first-rethink`, 8 ahead of `main`).
**Governing docs (higher priority on conflict):** [Step −1 LOCK](2026-05-30-pathb-step-minus-1-preregistration-lock.md) (H1/H2/H3 params, N\*=3, gate, floors, taxonomy — FROZEN) · [Design spec v2.1](2026-05-30-pathb-mechanism-first-rethink-design.md) (§3/§6/§8/§9).
**Cost anchor:** `spot_realistic_15bps_v1` — 15 bps/side (`config/execution_phaseb_spot_15bps.yaml`); `tier6_dsr.py:706-712` allowlists it and `execution_phase4_15bps.yaml` as functionally-identical 15bps anchors. HARD CONSTRAINT; not relaxed.

---

## 0. Registered decisions (provenance)

Surfaced as plain-text options + intuitive Chinese; 2-leg B2 (Codex cross-model + quant-research-advisor) reviewed; every load-bearing claim re-verified against the repo. **Charlie-registered 2026-05-30** (reviewer convergence advisory only):

| # | Decision | Registered outcome |
|---|---|---|
| ① | H2 **and H3** sizing realization (LOCK names 2-factor sizing; `SizingSpec` node is single-factor) | **Single-factor approximation on `cdf_realized_vol_720`** (drop the `\|zscore_48\|` / trend-strength second factor). Reject node-extension as methodology-over-engineering. Falsification-invariant (kills are sizing-blind). **F3 temper recorded** (§4). |
| ② | Tier-5 gate slice + `CandidateMoments` source | **`forward_2026` window** (2026-01-01T00:00:00Z → 2026-04-16T07:00:00Z, 2528 bars, 15bps) — Path B runs its OWN candidates through the SAME OOS slice where the dead-18 scored 0/18; moments come from these per-bar returns. 2024 = prior stress look; **2025 reserved** for B-positive OOS confirmation. |
| ③ | Path B moments integrity | **Mirror the dead-18 gate**: sha256 the per-bar returns + independent moment recompute self-check; match conventions exactly. |
| F5 | per-leg mechanism regime split | **Reconcile** `pathb_perleg_mechanism.py` to split on the traded gate `cdf_realized_vol_720 < 0.5` (NOT `realized_vol_24h` global median) — the H2 per-leg KILL is an earned-negative verdict input, not a diagnostic. |
| F6 | H1 LOCK-conformance | **Fix** `build_hypothesis_dsl`: `max_hold_bars` 24→**3**; add the `range_over_atr > 1.0` entry conjunct. |

---

## 1. Frame

The Path B harness (A–E) is built but **cannot run the pre-registered verdict as-is**: only H1 is buildable as a DSL (and it drifts from the LOCK), Path B's `CandidateMoments` are consumed but never constructed, there is no end-to-end orchestrator, and the H2 mechanism-sanity regime split disagrees with the traded gate. This cycle closes those gaps + the 2 fixes, **conforming strictly to the frozen Step −1 LOCK**, then runs the gauntlet. The output is **advisory evidence**; the binding earned-negative read and any Path-A escalation remain a separate Charlie register-event (spec §9; the taxonomy/escalation modules are advisory-only by construction).

---

## 2. Determined scope (no decision needed — verified)

- **No DSL schema change.** All three hypotheses are expressible in the current DSL: factor-vs-factor is supported ([dsl.py:95-153](../../../strategies/dsl.py)) for H3's `decay_linear_close_48 > decay_linear_close_168`; OR-connected `ConditionGroup`s (≤3) encode H2's regime switch.
- **No factor/operator build.** All 8 needed factors are registered (`intrabar_push`, `range_over_atr`, `cdf_realized_vol_720`, `decay_linear_close_48/168`, `zscore_48`, `realized_vol_24h`, `atr_14`).
- **`CandidateMoments` contract is fixed** by the dataclass ([tier6_dsr.py:94-111](../../../backtest/tier6_dsr.py)): `(hypothesis_hash, name, theme, sr_per_bar, gamma3, gamma4, T, trades)`.

The build is therefore **5 items + 2 fixes** — wiring, not new primitives.

---

## 3. Build surface

**B1 — H2 DSL builder.** Two OR-connected `ConditionGroup`s: LOW = `cdf_realized_vol_720 < 0.5 AND zscore_48 < -1.0`; HIGH = `cdf_realized_vol_720 >= 0.5 AND zscore_48 > +1.0`. Long/flat. Exit on regime-appropriate reversion / time. Sizing: single-factor ternary on `cdf_realized_vol_720` (Decision ①). 1 candidate.

**B2 — H3 DSL builder.** One group: `decay_linear_close_48 > decay_linear_close_168 AND cdf_realized_vol_720 <= 0.9`. Long/flat. Sizing: single-factor ternary on `cdf_realized_vol_720` (Decision ①). 1 candidate.

**B3 — H1 LOCK reconciliation (F6).** Entry group → `intrabar_push < -0.6 AND range_over_atr > 1.0`; `max_hold_bars = 3`; sizing unchanged (`cdf_realized_vol_720` band [0.3,0.8]→1.0, else 0.5). 1 candidate.

**B4 — `CandidateMoments` constructor + integrity gate (Decision ②③).** From Path B's own `forward_2026` per-bar returns: `sr_per_bar = mean/std(ddof=0)`, `gamma3 = skew(bias=True)`, `gamma4 = kurtosis(fisher=False, bias=True)` RAW, `T = #finite`, `trades`. Integrity self-check: sha256 the per-bar returns parquet + recompute-vs-store assertion (the `load_candidate_moments` discipline, [tier6_dsr.py:123-207](../../../backtest/tier6_dsr.py)), so Path B's moments meet the same integrity bar as the dead-18 they are DSR-compared against.

**B5 — orchestrator.** Compose, per candidate: compile DSL → `EVAL_GAUNTLET` (train WF → 2022 regime-holdout → 2024 validation stress → **Tier-5 gate on `forward_2026`**, each routed to its `wf_lineage` guard) → `holdout_sharpe` + per-bar returns → `CandidateMoments`. Then across the 3: `run_dsr_fwer(n_star=3)` → per-leg mechanism sanity (train-only) → `assemble_evidence` (taxonomy, advisory) → `a_escalation_advisory` (advisory). Step-0 read-only diagnostic runs first (separate, advisory-only).

**F5 fix — regime-split reconciliation.** `pathb_perleg_mechanism.py` regime split → `cdf_realized_vol_720 < 0.5` (the traded gate), matching the H2 DSL. Update tests + docstrings.

---

## 4. Registered realization decisions (precise)

- **① Sizing.** H2 and H3 sizing = single-factor `cdf_realized_vol_720` ternary, inverse-vol direction. **Pinned default ladder (committed here, before any data-touch):** `cdf_realized_vol_720 < 0.5 → size 1.0` (full in the lower-vol half), `≥ 0.5 → size 0.5` (half in the upper-vol half); `0` when flat. The LOCK's literal 2-factor sizing (`× |zscore_48|` for H2; `× trend-strength` for H3) is **approximated to single-factor**, justified by spec §12's "default discrete-only, approximate" + the single-factor `SizingSpec` node. The mechanism being falsified (regime-switched / decay-trend *entry*) is unchanged; kills are sign-of-forward-return tests, sizing-blind. Adds no variant → **N\* stays 3.**
  - **F3 temper (recorded for the earned-negative read; covers sizing AND exit — advisor Points 2/5):** a B-negative (especially *process-refuted*) is *marginally less conclusive* than under the literal LOCK, for two pinned reasons: (a) the single-factor sizing approximated away the locked strength-weighting (no strength-weighted variant was run); (b) H2's exit is a regime-flip cross only (+ time-stop), which approximates away the §5.2 "natural OR-exit" `zscore`-reverts leg, and the `cdf_realized_vol_720`-0.5 boundary cross carries a 15bps whipsaw that pressures H2 `holdout_sharpe` (the taxonomy key) downward. Both are honest small-N\*-style caveats (§8 family), not a void. **These tempers are wired as a pinned `approximation_tempers` field in `assemble_evidence`'s advisory bundle** (not prose only — METHODOLOGY_NOTES §6), pinned before any data-touch.
- **② Gate.** Tier-5 holdout = Path B's OWN single-run on the `forward_2026` window [2026-01-01T00:00:00Z, 2026-04-16T07:00:00Z], 2528 bars, anchor `config/execution_phaseb_spot_15bps.yaml`. **Reuses the WINDOW (raw 2026 OHLCV), NOT the dead-18 sealed ARTIFACT** (`phase4_forward_2026_15bps_v1/` stays byte-untouched). `holdout_sharpe > 0` is the Tier-5 gate; the per-bar returns build the moments. 2024 validation is an informational stress look (no selection → no leakage; N\*=3, nothing fit). 2025 test stays sealed, touched once only on a B-positive.
- **③ Integrity.** As B4. The conventions (`skew bias=True`; `kurtosis fisher=False,bias=True` RAW; `sr=mean/std ddof=0`; `T=#finite`) MUST match `load_candidate_moments` exactly, else the two cohorts enter the same DSR math under different definitions.

---

## 5. Pre-registration integrity rules

1. **Conform to the frozen LOCK.** The build realizes the Step −1 LOCK; it does NOT alter H-params, the gate, the floors, the taxonomy, or N\*=3. The only sanctioned LOCK-vs-code reconciliations are F6 (H1 back to LOCK) and the registered ① sizing approximation (documented deviation).
2. **Pin-before-data.** Residual realization details the LOCK does not pin — H2/H3 **exit predicates** (natural form: exit when the entry signal turns off, i.e. H2 `zscore_48` reverts past 0 or regime flips; H3 `decay_linear_close_48 ≤ decay_linear_close_168` or the vol-CDF gate exceeded), H2/H3 **`max_hold_bars`**, and any band-edge refinement within the §4① pinned intent — are **fixed in the implementation plan, which is itself committed BEFORE any build edit or data-touch.** The plan's commit-order is therefore also anti-hindsight evidence. Writing or refining builder/sizing/exit/moments code *after* a Step-0 or gauntlet result is seen is reverse-fitting that voids the cycle.
3. **No post-hoc variants.** Adding any hypothesis/variant after results voids N\* (LOCK binding rule).
4. **Sealed-artifact invariant.** Re-verify the 4 `tier6_dsr_v1/` sha256 (and that `phase4_forward_2026_15bps_v1/` is untouched) immediately before AND after the run. The run reads raw 2026 OHLCV; it writes only to a Path B namespace.

---

## 6. Run sequence (after build + B2 green)

1. **Step-0 diagnostic** (read-only, advisory-only): re-score the existing 993/39/18 under the locked cost-aware objective + floors; feeds only the §9 A-escalation second prong. No promotion side-effect (hard error if violated).
2. **Build** B1–B5 + F5 fix, TDD; green suite.
3. **B2 2-leg** (Codex + advisor) on the implementation at the build boundary.
4. **Gauntlet run** per candidate → Tier-5 `holdout_sharpe` on forward_2026 + per-bar returns → `CandidateMoments` (with integrity gate).
5. **DSR-FWER** at N\*=3 (survivors = `pass_B`).
6. **Per-leg mechanism sanity** (train-only, reconciled regime split).
7. **Taxonomy** (`assemble_evidence`, keyed on Tier-5 `holdout_sharpe>0`) + **A-escalation advisory** — both ADVISORY.
8. **Charlie registers** the binding earned-negative read at the §9 gate. A B-positive needs 2025 OOS confirmation before A is re-evaluated.

---

## 7. Test plan

- **B1/B2/B3:** each DSL compiles through the engine; entry/exit fire at N+1 open (`set_coc/coo(False)`); H2 OR-group regime logic + H3 factor-vs-factor verified; H1 conforms to LOCK (max_hold=3, range_over_atr conjunct present).
- **B4:** moment conventions byte-match `load_candidate_moments` on a known series; sha256 + recompute self-check raises on tamper; degenerate (flat/zero-var) handled.
- **B5:** orchestrator wires the 4 stages; each `wf_lineage` guard invoked with the correct semantics tag; Step-0 read-only assertion.
- **F5:** per-leg regime split == `cdf_realized_vol_720 < 0.5`; the H2 LOW/HIGH populations match the traded gate.
- **Sealed invariant:** `tier6_dsr_v1/` 4-file sha256 unchanged; `phase4_forward_2026_15bps_v1/` untouched; full suite green before the build-boundary B2 and before the run.

---

## 8. Anti-pre-emption

Nothing here scopes Path A (data family / N\* / hypotheses unscoped; spec §10, LOCK line 52). Decision ②'s "reserve 2025" is within Path B's own register. The §9 earned-negative gate remains the only door to A, and it is a Charlie register-event.

---

## 9. Terminal state

On review-gate approval: invoke `superpowers:writing-plans` to turn this spec into a step-by-step implementation plan (build B1–B5 + F5, TDD → build-boundary B2 → run), then TDD implement → B2 → Rule-2 SEAL-eve → run → earned-negative gate (Charlie).
