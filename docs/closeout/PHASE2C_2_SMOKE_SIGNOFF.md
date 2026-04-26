# PHASE2C_2_SMOKE_SIGNOFF

## 1. Scope

This signoff covers Phase 2C **smoke acceptance only** for the β
(Stage 2c live Sonnet) follow-up. It does not close full Phase 2C; it
does not prove strategy alpha quality; it does not authorize live
trading. The single decision under this signoff is whether the
post-D8.4 pipeline state — exercised end-to-end against the live
Anthropic Sonnet API — is safe to scale from a controlled smoke batch
to a real Phase 2C mining batch with budget caps. Alpha quality,
methodology revisions, and live readiness are explicitly out of scope.

This is the second smoke acceptance event for Phase 2C; α (Stage 2c
dry-run / stub backend) is signed off separately at
`docs/closeout/PHASE2C_1_SMOKE_SIGNOFF.md` (verdict
`PARTIAL_PASS_BY_DESIGN`).

## 2. Evidence Artifact

- **Notebook path:** `docs/test_notebooks/PHASE2C_1_smoke_acceptance.ipynb`
  (re-executed in-place against the β artifact; same canonical notebook
  used for α with `SMOKE_ARTIFACT_PATH` set to the β batch directory —
  see §5 notes for convention shift from α discovery)
- **Smoke artifact path inspected:** `raw_payloads/batch_1595af57-fc42-433b-9d5a-442b1f529a16/`
- **Smoke batch invocation:** `python -m agents.proposer.stage2c_batch`
  (no `--dry-run`; live SonnetProposerBackend)
- **Smoke run HEAD (acceptance template SHA):** `79a0d33` (α signoff
  commit; same HEAD used to launch β so static guardrails and bucket-3
  protections are verified at the exact post-α state)
- **Notebook executed at HEAD:** `79a0d33` (no notebook code changes
  applied between α and β — only the `SMOKE_ARTIFACT_PATH` config
  literal updated to point at the β batch; gate logic identical to
  α-fixed state)
- **Date / time (UTC):** 2026-04-26 (β batch produced 2026-04-26T03:47-03:49Z;
  acceptance notebook executed immediately after)
- **Backend mode:** `dry_run = False` (live SonnetProposerBackend; real
  API spend against $100 monthly cap)

## 3. Preconditions

- α (Stage 2c dry-run / stub backend) signed off at HEAD `79a0d33` with
  verdict `PARTIAL_PASS_BY_DESIGN` (G4 + G8 PARTIAL_BY_DESIGN under
  stub-backend limitations; full G8 coverage required β).
- D8.4 methodology refinement sub-arc fully closed (sealed at `767d0e5`).
- Bucket 3 high-severity data write hazard fixed
  (`bulk_download.py` canonical-overwrite refusal default + `--force`
  override path with archive + atomic-promote, sealed at `1f27fe4`).
- Issue 6 theme-rotation operational boundary documented across
  `agents/proposer/stage2c_batch.py`, `agents/proposer/stage2d_batch.py`,
  `CLAUDE.md`, and `agents/themes.py` (sealed at `613da3f`).
- Operational theme rotation is the 5-theme rotation
  (`THEME_CYCLE_LEN = 5`); `multi_factor_combination` is canonical but
  excluded from operational rotation pending separate validation.
- `ANTHROPIC_API_KEY` provisioned in `.env` (loaded at runtime by
  `agents.proposer.stage2c_batch._load_dotenv` before SonnetProposerBackend
  instantiates the Anthropic client; pre-flight verified key length=108).
- The signoff process itself does not perform any canonical-data
  mutation; it inspects the notebook output produced by the
  separately-executed β smoke batch.

## 4. Acceptance Gates

| Gate | Description | Expected | Result | Notes |
|---|---|---|---|---|
| G1 | Environment / git state captured | HEAD SHA + dirty-tree status + Python version recorded in notebook output | **PASS** | HEAD `79a0d33`; 5 dirty entries (M `.DS_Store`, M `docs/test_notebooks/PHASE2C_1_smoke_acceptance.ipynb` from re-execution outputs, ?? `.claude/`, ?? `docs/d7_stage2c/D7_STAGE2C_PATCH_REPORT.md`, ?? `docs/d7_stage2c/stage2c_candidate_worksheet.md`); 4 non-known-unrelated entries surface as warning, not failure (informational; notebook re-execution is expected to dirty its own file). |
| G2 | Static guardrails pass | No regressions in import paths, theme constants, or CLAUDE.md spec references | **PASS** | All 10 sub-checks pass (THEMES len=6, multi_factor_combination at index 5, stage2c+2d THEME_CYCLE_LEN=5, no PHASE2_BLUEPRINT_v2 residuals in code, all 4 bulk_download protections). Identical to α G2. |
| G3 | Smoke artifacts discoverable | Smoke batch output directory exists and contains expected files | **PASS** | `raw_payloads/batch_1595af57-fc42-433b-9d5a-442b1f529a16/stage2c_summary.json` discovered via explicit `SMOKE_ARTIFACT_PATH` (no warning since path was configured, not discovered). |
| G4 | Lifecycle counts reconcile | `sum(terminal_lifecycle_counts) == hypotheses_attempted` (per CLAUDE.md invariant, checked at batch close) | **PASS (flipped from α PARTIAL_BY_DESIGN)** | hypotheses_attempted=20; terminal lifecycle sum=20 (`pending_backtest`:20); `lifecycle_invariant_ok=True`. No EARLY_STOP truncation (parse_rate=1.000 ≫ 0.5 threshold; live Sonnet 100% valid). record_count=20 = attempted=20 — no `truncated_by_cap` filtering needed under live backend. **G4 flipped from α PARTIAL_BY_DESIGN to clean PASS as predicted by Claude+ChatGPT pre-execution analysis.** |
| G5 | Theme rotation matches 5-theme operational boundary | Theme distribution shows only the 5 operational themes (no `multi_factor_combination` calls) | **PASS** | All 5 operational themes assigned 4× each across 20 issued calls (momentum=4, mean_reversion=4, volatility_regime=4, volume_divergence=4, calendar_effect=4); `multi_factor_combination` calls = 0. Issue 6 operational boundary empirically confirmed at full Stage 2c batch_size=20. |
| G6 | Cost under configured smoke cap | Actual smoke batch cost ≤ configured smoke cap (well under $20/batch limit) | **PASS** | total_actual_cost_usd = $0.200538 ≤ $1.00 notebook cap (and ≪ $6.00 stage2c per-batch hard cap). Within Claude+ChatGPT pre-execution estimate range $0.18-0.90 (actual landed near low end; see §5 cost-estimate observations). |
| G7 | No unexplained infrastructure errors | No unhandled exceptions, no abort attempts beyond expected retry pattern | **PASS (flipped from α PARTIAL_BY_DESIGN)** | No abort_* artifacts in batch directory. Zero failure records (failure_record_count=0; all 20 calls returned valid Sonnet output, parsed cleanly, lifecycle=pending_backtest). **G7 stub-mode detection branch did NOT fire** under β (`is_stub_run = summary.get('dry_run', False) = False`); live error-metadata path was exercised by absence-of-failures (no records required error_category/signature because no failures occurred). G7 flipped from α PARTIAL_BY_DESIGN to clean PASS as predicted. |
| G8 | Output artifacts complete for configured smoke scope | All expected per-call prompts / responses / critic results present; no truncated artifacts | **PASS (flipped from α PARTIAL_BY_DESIGN)** | summary JSON present + 20 `attempt_*_prompt.txt` + 20 `attempt_*_response.txt` files = 41 artifacts total. SonnetProposerBackend writes per-call forensic files to `raw_payload_dir` (per `agents/proposer/sonnet_backend.py` design); StubProposerBackend at α does not. **G8 flipped from α PARTIAL_BY_DESIGN to clean PASS as predicted by Claude+ChatGPT pre-execution analysis — this was the primary objective of running β.** |
| G9 | No canonical data write path touched | No writes to `data/raw/btcusdt_1h.parquet`; no `bulk_download.py` invocation; smoke batch operated read-only on canonical data | **PASS** | `data/raw/btcusdt_1h.parquet` mtime = `Apr 16 01:14:15 2026` (size=3389174 bytes); identical pre-β and post-β; no canonical data touched. |
| G10 | Final verdict generated by notebook | Notebook prints explicit PASS / PARTIAL PASS / FAIL with per-gate breakdown | **PASS** | Verdict generated: PASS with single non-blocking working-tree dirty-entries warning; full per-gate JSON breakdown in cell 24 output. |

## 5. Notebook Result Summary

- **Notebook verdict:** **PASS** (10 of 10 gates pass; no FAIL, no
  PARTIAL_BY_DESIGN under live backend; single non-blocking warning
  about working-tree dirty entries)
- **Passed gates:** G1, G2, G3, G4, G5, G6, G7, G8, G9, G10
- **Failed gates:** *(none)*
- **Warnings:** (1) Working tree has 5 dirty entries — one is the
  notebook itself which the in-place re-execution updated (expected),
  others are α-era known-unrelated items (.DS_Store, .claude/,
  docs/d7_stage2c/*) — informational, not regression.
- **Inspected artifact path:** `raw_payloads/batch_1595af57-fc42-433b-9d5a-442b1f529a16/`
- **Cost (actual / cap):** $0.200538 / $1.00 notebook cap (well under
  $6.00 stage2c per-batch hard cap and $100 monthly cap; monthly spend
  after β = $6.351408 cumulative)
- **Calls issued / batch_size:** 20 / 20 (no EARLY_STOP under live
  backend; parse_rate=1.000)
- **Theme distribution (issued calls):** momentum=4, mean_reversion=4,
  volatility_regime=4, volume_divergence=4, calendar_effect=4,
  multi_factor_combination=0
- **Lifecycle terminal counts (issued):** pending_backtest=20; sum=20 ✓
  matches hypotheses_attempted=20
- **Cardinality:** all 20 calls `single_object`; 0 cardinality violations
- **Main failure modes, if any:** *(none — no infrastructure failures,
  no parse failures, no validation failures, no API errors observed)*

**Notebook code state at β execution:**

The notebook was executed against β after α-era gate-logic fixes
(G2 acceptance-doc exclusion, G4 truncated-entry filtering, G6
`total_actual_cost_usd` direct lookup, G7 stub-mode detection) were
already in place from α commit `79a0d33`. Only the `SMOKE_ARTIFACT_PATH`
config literal was updated; gate logic is identical to α-fixed state.
Three of the four α-era fixes (G4 truncated-entry, G6 `cost_ratio`-inf
exclusion, G7 stub-mode branch) did not fire under β because β did not
exhibit the conditions they were guarding (no truncation, non-zero
actual cost, `dry_run=False`); they remain in place to keep the same
notebook reusable for future stub-mode runs.

**Convention shift from α (`SMOKE_ARTIFACT_PATH` explicit vs discovery):**

α was executed with `SMOKE_ARTIFACT_PATH = ''` (notebook discovered the
most-recent batch under `raw_payloads/`). β was executed with
`SMOKE_ARTIFACT_PATH = 'raw_payloads/batch_1595af57-...'` set explicitly
in the config cell so the executed notebook is unambiguously bound to
the β artifact in committed state (no reliance on "most recent" being
β at any future re-execution time). This makes the committed notebook
self-documenting as β-evidence rather than α-or-β-or-future-evidence.
The trade-off is that the canonical notebook is now β-specific in
committed state; future smoke runs (e.g., PHASE2C_3) should either
reset `SMOKE_ARTIFACT_PATH = ''` for discovery or update it to the new
batch path.

**Cost-estimate observation (per Claude's pre-β framing):**

Actual cost $0.200538 lands at the low end of the Claude+ChatGPT
pre-execution estimate range $0.18-0.90 (closer to the lower bound
than the midpoint $0.54). This is not anomalous — Sonnet output
length appears to be well-controlled by the prompt template (per-call
output_tokens range 270-333, mean ~298). The pre-charge estimator
(`agents/proposer/stage2c_batch.py` cost-estimation logic) is
conservative: `total_estimated_cost_usd = $0.264393` vs
`total_actual_cost_usd = $0.200538` gives `cost_ratio (est/actual) =
1.32x`. This is documented forward-pointer information for any future
cost-estimate calibration work; not a finding requiring immediate
action.

## 6. Decision

**PASS** — β (Stage 2c live Sonnet smoke) validates the live Anthropic
API path end-to-end. All 10 acceptance gates pass cleanly; the three
gates that carried PARTIAL_BY_DESIGN under α (G4 lifecycle, G7 failure
review, G8 artifact completeness) all flipped to clean PASS under β as
predicted. No new regressions surfaced.

**Rationale:** Post-D8.4 pipeline runs cleanly end-to-end under live
Sonnet backend. Orchestration, theme rotation (5-theme operational
boundary empirically confirmed at full batch_size=20), lifecycle
invariant (20→20 reconcile), parse-rate (100% — no EARLY_STOP),
cost-tracking, per-call forensic-file writing, and canonical-write-path
non-touching all behave correctly. The single non-blocking warning
(working-tree dirty entries) is informational and includes the notebook
itself (expected from re-execution).

**What β PASS validates:**
- Live Sonnet API path runs cleanly end-to-end (20/20 calls returned
  valid output, parsed cleanly, all advanced to `pending_backtest`)
- Per-call forensic artifacts are written to `raw_payload_dir` by
  SonnetProposerBackend (40 prompt + response files for 20 calls)
- Cost tracking is accurate against real spend (actual $0.200538;
  estimator conservative at 1.32x)
- Orchestration handles real Sonnet output (cardinality enforcement,
  hash-based dedup, theme rotation, leakage audit all operate against
  non-deterministic backend)

**What β PASS does NOT validate:**
- Strategy alpha quality or candidate research value (Phase 2C research
  question, not acceptance question)
- Behavior at full Stage 2d scale (200-call batch, not Stage 2c's 20
  — different parse-rate distribution risk, different cost trajectory,
  different cardinality-violation accumulation rate)
- Regression-free behavior over time (β is a single point-in-time
  validation; future Sonnet API changes, prompt changes, or factor
  registry changes could regress without re-running smoke)
- Live trading readiness (zero overlap with paper-trading or
  live-execution code paths)

**Status meaning:** Both α (Stage 2c dry-run / stub backend) and β
(Stage 2c live Sonnet smoke) are now signed off. Pipeline is safe to
scale to a real Phase 2C mining batch with normal budget caps. Whether
to actually scale, and at what batch_size, remains a separate
research-direction decision (not an infrastructure-validation decision).

Decision rules:
- **PASS:** smoke infrastructure is safe to scale to a real Phase 2C
  mining batch with budget caps.
- **PARTIAL PASS / PARTIAL_PASS_BY_DESIGN:** smoke mostly worked;
  either a small correction is needed or non-blocking limitations are
  documented as expected.
- **FAIL:** do not scale until the blocking issue is fixed; rerun
  smoke acceptance after fix.
- **NOT_RUN / DRAFT_PENDING_NOTEBOOK_RESULTS:** signoff template;
  no decision yet.

## 7. Next Action

Currently **PASS** for β (Stage 2c live Sonnet smoke). Both α and β
acceptance events are signed off. Next decision is research-direction,
not infrastructure-validation:

1. **First real Phase 2C mining batch decision** — separate decision,
   not authorized by this signoff. Open research questions before
   scaling include: target batch_size (20 / 50 / 100 / 200 — Stage 2c
   vs Stage 2d), whether to run with `--with-critic` (D7 LLM critic
   gate enabled), expected cost trajectory at chosen scale, and what
   minimum candidate-quality outcome would justify the spend.
2. **If first real batch is approved:** invoke
   `python -m agents.proposer.stage2c_batch` (or stage2d for 200-call
   batch) with normal budget caps; this acceptance does not need to be
   re-run for the first real batch unless infrastructure or prompt
   changes happen between β and the real batch.
3. **If new D7 critic stage or methodology changes happen first:** a
   new smoke acceptance event (`PHASE2C_3_SMOKE_SIGNOFF.md`) should be
   created before the first real batch.

## 8. Non-Claims

This signoff explicitly does **not** claim or authorize any of the
following:

- Does not prove strategy profitability or alpha quality.
- Does not validate live trading readiness.
- Does not change the operational theme rotation from 5 to 6 themes.
- Does not modify any D8.4 sub-arc conclusion or recommendation.
- Does not authorize any canonical data overwrite path
  (`bulk_download.py --force` remains a manual operator override gate).
- Does not authorize the first real Phase 2C mining batch (separate
  research-direction decision; this signoff only validates that
  infrastructure is safe to scale, not that scaling is the right next
  research move).
- Does not validate Stage 2d (200-call) batch behavior — β was Stage 2c
  (20-call); Stage 2d has different scale-dependent risk surface.
- Does not validate `--with-critic` (D7 LLM critic) execution path —
  β ran without critic; critic-enabled batches are a separate
  infrastructure validation event.
- Does not constitute Phase 2C closeout.

## 9. Final Status

```
Status: PASS (β / Stage 2c live Sonnet smoke)
Evidence notebook: docs/test_notebooks/PHASE2C_1_smoke_acceptance.ipynb
Smoke artifact: raw_payloads/batch_1595af57-fc42-433b-9d5a-442b1f529a16/
Smoke run HEAD: 79a0d33
Cost: $0.200538 (live Sonnet; under $1.00 notebook cap; under $6.00 stage2c
                 batch cap; cumulative monthly spend = $6.351408 / $100 cap)
Verdict: PASS (10/10 gates pass; G4 + G7 + G8 flipped from α
               PARTIAL_BY_DESIGN to clean PASS as predicted)
Next required action: NONE for infrastructure validation. First real Phase 2C
                     mining batch decision is research-direction-scoped and
                     out of this signoff.
```
