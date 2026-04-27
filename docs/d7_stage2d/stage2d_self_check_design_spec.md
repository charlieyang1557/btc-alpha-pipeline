# Stage 2d Self-Check Design Spec (Consolidated v3 + v4 + v5 + Errata)

**Target implementation:** `scripts/stage2d_self_check.py`

**Scope-lock anchor:** `docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md` Lock 12, plus
§11.1 required-section headers and §11.1.a authoring-convention amendment.

**Expectations-file anchor (DRAFT SHA at spec write):**
`98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5`
(`docs/d7_stage2d/stage2d_expectations.DRAFT.md`, 948 lines)

**Spec revision lineage:** v1 → v2 (blocker, rebuilt) → v3 (ratified body) → v4 (precision deltas, ratified) → v5 (precision deltas, ratified) → this consolidated document. Errata resolved against v5 are noted in the §Errata section at the end.

**Ratification status:** Task 3a v5 APPROVED by ChatGPT and Claude reviewer; Task 3b authorized. This document is the single source of truth for Task 3b implementation.

---

## §1 — Purpose

Pre-fire structural integrity check for
`docs/d7_stage2d/stage2d_expectations.md` (or
`stage2d_expectations.DRAFT.md` pre-rename). Enforces Lock 12's 17
canonical gates plus 11 format/consistency gates (**28 counted gates
total** — FMT-02 and FMT-02b are distinct gates per Option X; FMT-10
removed). Zero semantic judgment; only structural / format /
cross-reference validation. Runs in <5 s; stdlib only.

## §2 — Invocation

```bash
python scripts/stage2d_self_check.py [--strict]
```

- No positional args. All paths derived from
  `Path(__file__).resolve().parents[1]` (repo root).
- `--strict`: promotes counted-gate `WARN` → `FAIL`. Default lenient.
- Exit codes:
  - `0` — all counted gates pass (counted `WARN` permitted in lenient).
  - `1` — any counted gate `FAIL`.
  - `2` — harness error (file missing, JSON parse error, `L12-01`
    hard-fail cascade).
- `PATH-01` / `PATH-02` are **harness-level warnings** reported inline,
  **excluded from the counted-gate tally**, and do not drive exit code.
- `SKIP` counts (upstream-dependent gates that could not run) → stderr;
  `PASS` / `FAIL` / counted-`WARN` lines → stdout.

`--output-json` is **not in Task 3b scope**; deferred to Task 3c per
pre-flight ratification.

## §3 — Path Policy

```python
REPO_ROOT            = Path(__file__).resolve().parents[1]
EXPECTATIONS_MD      = REPO_ROOT / "docs/d7_stage2d/stage2d_expectations.md"
EXPECTATIONS_DRAFT   = REPO_ROOT / "docs/d7_stage2d/stage2d_expectations.DRAFT.md"
SCOPE_LOCK           = REPO_ROOT / "docs/d7_stage2d/D7_STAGE2D_SCOPE_LOCK_v2.md"
LABEL_UNIVERSE       = REPO_ROOT / "docs/d7_stage2d/label_universe_analysis.json"
REPLAY_CANDS         = REPO_ROOT / "docs/d7_stage2d/replay_candidates.json"
DEEP_DIVE_CANDS      = REPO_ROOT / "docs/d7_stage2d/deep_dive_candidates.json"
TEST_RETEST          = REPO_ROOT / "docs/d7_stage2d/test_retest_baselines.json"
```

**Pre-rename fallback:**
- `EXPECTATIONS_MD` present → use it. No warning.
- `EXPECTATIONS_MD` absent, `EXPECTATIONS_DRAFT` present → `WARN[PATH-01]
  operating on DRAFT (pre-rename)`, use DRAFT for all subsequent checks.
- Both present → `WARN[PATH-02] both .md and .DRAFT.md present; using
  .md`.
- Neither present → harness error; emit to stderr, exit 2.

## §4 — Hard-Coded Constants (Lock-Cited)

```python
FRESH_7_POOL        = {3, 43, 68, 128, 173, 188, 198}
# Lock 6.4 — hard-coded, no JSON derivation permitted.
# Validated by L12-13 (§6.4 structured-claim literal-set + threshold=2
# check), not by FMT-11 cross-check. FMT-04 is E3 OR-bucket syntax,
# unrelated.

FRESH_9_POOL        = {122, 127, 128, 129, 132, 172, 178, 182, 187}
# Lock 4.3 — fresh eligible pool (universe_a \\ stage2c_20).

TIER_1_POSITIONS    = {17, 73, 74, 97, 138}
# Lock 12 Gate 7 — exact position set for the three-run test-retest tier.

STAGE2C_POSITIONS   = {17, 22, 27, 32, 62, 72, 73, 74, 77, 83,
                       97, 102, 107, 112, 117, 138, 143, 147, 152, 162}
# The 20 Stage 2c replay positions; upstream frozen.

POSITION_116_SKIP   = 116
# Lock 1.5 — deterministic skipped source; no D7b call issued.

RSI_ABSENT_THRESHOLD = 2
# Lock 6.4 — fresh-7 RSI-absent structured claim: ≥ 2/7 with SVR < 0.5.

E3_OR_BUCKET_POSITIONS = {72, 74, 83, 138}
# §E3 defects note v2.1 — the only positions permitted OR-buckets in E3
# under Path A adjudication.

E3_OR_BUCKET_PAIRS = {("MODERATE-HIGH", "HIGH"), ("LOW", "MODERATE-LOW")}
# §E3 defects note v2.1 — the only sealed adjacent-bucket disjunctions.

SECTION_64_HEADER_RE = r'^## §6\.4 — Fresh-7 RSI-Absent vol_regime Structured Claim$'
# L12-14 allowlist scope boundary — matches exact §6.4 section header on
# disk.
```

All constants are cross-checked against JSON fixtures via FMT-11 (three
sets only — `FRESH_9_POOL`, `TIER_1_POSITIONS`, `STAGE2C_POSITIONS`;
`FRESH_7_POOL` explicitly excluded from cross-check per Lock 6.4).

## §5 — Gate Catalog (28 counted)

### Lock 12 gates (17, verbatim names per scope lock lines 803-831)

| ID | Definition | Severity |
|----|------------|----------|
| L12-01 | Expectations file exists / UTF-8 valid. | FAIL |
| L12-02 | Required canonical headers present; count report: `N required + M permitted + E extras`. Required = 10 per Lock 11.1; permitted additional = 2 (§6.5, §6.6) per §11.1.a; prefix convention matches regex `§\d+\.\d+\s*—\s*` or `§E\d+\s*—\s*` per §11.1.a; dual-literal `Frozen Pre-Registration Anchors` ≡ `Anti-Hindsight Anchor`. | FAIL on missing canonical; WARN on unexpected extras |
| L12-03 | `label_universe_analysis.json` referenced with SHA256 hex string in expectations file. | FAIL |
| L12-04 | `replay_candidates.json`: 200 entries / 199 replay-eligible / pos 116 `is_skipped_source=true`. | FAIL |
| L12-05 | `deep_dive_candidates.json`: exactly 20 entries / no pos 116 / no Stage 2c-20 overlap. | FAIL |
| L12-06 | `test_retest_baselines.json`: exactly 20 baselines / positions ⊆ `STAGE2C_POSITIONS` / all 20 scores populated (plausibility, alignment, svr, reasoning_length, source_record_sha256). | FAIL |
| L12-07 | Tier 1 grid exactly 5 rows / positions `{17,73,74,97,138}`. | FAIL |
| L12-08 | Tier 2 grid exactly 15 rows / matching baselines (positions parsed from §E3 Tier 2 subsection). | FAIL |
| L12-09 | Deep-dive section exactly 20 per-candidate blocks / all in `deep_dive_candidates.json` position set. | FAIL |
| L12-10 | ≥ 3 of 9 fresh eligible-pool positions (`FRESH_9_POOL`) present in deep-dive 20. | FAIL |
| L12-11 | Axis-specific TBD-A1, TBD-A2 resolved to numeric values (not placeholders). | FAIL |
| L12-12 | SVR distribution TBD-DIST resolved to numeric form. | FAIL |
| L12-13 | RSI-absent vol_regime claim references `FRESH_7_POOL` literal set + numeric threshold `2`. | FAIL |
| L12-14 | No sub-group hypothesis language in §E4 deep-dive prose (per-field scan, §6.4 allowlist boundary per `SECTION_64_HEADER_RE`). See §8. | FAIL |
| L12-15 | Aggregate-claim threshold expressions single-line in §6.1, §6.2, §6.3, §6.4, §E3. Patterns: regex hits for `[≥≤<>]\s*\d+(/\d+)?(\.\d+)?` and `SVR\s*[≥≤<>]\s*\d+\.\d+`. §E4 DSL expressions in backtick-fenced content excluded. | FAIL |
| L12-16 | §Position 116 Treatment section references `call_116_live_call_record.json`. | FAIL |
| L12-17 | Universe A / Universe B references cite `label_universe_analysis.json`; no hardcoded count drift (cross-check universe_a_size=29, universe_b_size=199 consistent with JSON). | FAIL |

### Format gates (11; FMT-xx)

| ID | Definition | Severity |
|----|------------|----------|
| FMT-01 | Per-candidate §E4 block count = 20. | FAIL |
| FMT-02 | Each §E4 block contains the **numbered + ordered + bolded** 6-label skeleton verbatim: `1. **Structural assessment.**` → `6. **Core judgment.**` in sequence. Order AND numeric prefix enforced. See §6. | FAIL |
| FMT-02b | `7. **UA metadata.**` prefix + label present iff position ∈ `FRESH_9_POOL`; absent iff position ∉ `FRESH_9_POOL`. | FAIL |
| FMT-03 | SVR bucket labels match rubric (LOW / MODERATE-LOW / MEDIUM / MODERATE-HIGH / HIGH). Scope = §E3 grid rows + §E4 field 4 (`SVR expectation.`) only; §6.1-6.4 numeric thresholds excluded. | FAIL |
| FMT-04 | OR-bucket syntax scope = §E3 only, positions `E3_OR_BUCKET_POSITIONS` only, pairs `E3_OR_BUCKET_PAIRS` only; §E4 single-bucket required (no OR anywhere in §E4). Separator ` or ` (lowercase). | FAIL |
| FMT-05 | Subsection header `### Known Pre-Fire §E3 Defects (Path A documented)` present under §E3. Body contains literal substrings `Issue B`, `Issue D`, `Path A`, and an audit-trail date (`2026-04-19` or `2026-04` prefix). | FAIL |
| FMT-06 | `## Remaining Candidates (Schema-Level Only)` header present verbatim. | FAIL |
| FMT-07 | `## Position 116 Treatment — brief reference to Lock 1.5` header present verbatim. | FAIL |
| FMT-08 | §Position 116 Treatment section contains all 11 Lock 1.5 schema field-name strings (name-presence only, not value-verbatim). See §7. | FAIL |
| FMT-09 | `**three distinct counters**` bolding present in taxonomy-isolation paragraph of §Position 116 Treatment. | FAIL |
| FMT-11 | Cross-consistency (three sets only): (i) `FRESH_9_POOL` == `{p ∈ label_universe_analysis.json.fresh_eligible_pool_positions}`; (ii) `TIER_1_POSITIONS` == set of position numbers parsed from §E3 `### Tier 1 — Three-run candidates (n=5)` grid rows; (iii) `STAGE2C_POSITIONS` == `{b.position for b in test_retest_baselines.baselines}`. `FRESH_7_POOL` intentionally excluded per Lock 6.4. | FAIL |

**Violation-reporting shapes:**

- `FMT-02`: `block pos=NNN label_index=<N> expected="<X>" found="<Y|MISSING>"`.
- `FMT-02b`: `block pos=NNN expected=<PRESENT|ABSENT> actual=<PRESENT|ABSENT> (fresh-9 membership=<bool>)`.
- `FMT-11`: `set=<FRESH_9|TIER_1|STAGE2C> hardcoded=<{...}> derived=<{...}> diff=<sym-diff>`.
- `L12-14`: `block pos=NNN field="<field-label>" phrase="<matched>" section="<enclosing ## header>"`.

**FMT-10 does not exist.** The ID was reserved for a scope-lock SHA
anchor gate in v1; dropped per ChatGPT v2 ruling as ill-conceived and
orthogonal to Stage 2d concerns.

## §6 — Sealed §E4 Field Labels (FMT-02 target set) — DISK-VERIFIED

Verified by Python extract across all 20 §E4 entries in DRAFT SHA
`98b87a70...`. On-disk sealed format (verbatim, Position 1 sample):

```
1. **Structural assessment.** ...
2. **Plausibility expectation.** ...
3. **Alignment expectation.** ...
4. **SVR expectation.** ...
5. **Reconciliation expectation.** ...
6. **Core judgment.** ...
7. **UA metadata.** `universe_a_label`: `<value>`.   (fresh-9 only)
```

**Shared 6-label skeleton** (all 20 §E4 blocks must contain verbatim, in
strict sequence with numeric prefixes):

1. `**Structural assessment.**`
2. `**Plausibility expectation.**`
3. `**Alignment expectation.**`
4. `**SVR expectation.**`
5. `**Reconciliation expectation.**`
6. `**Core judgment.**`

**7th conditional label** (FMT-02b): `7. **UA metadata.**` present iff
position ∈ `FRESH_9_POOL`. On-disk verification: 9 fresh-9 positions
have it, 11 non-fresh-9 positions do not. Content shape on disk is a
single structured JSON-style line (`` `universe_a_label`:
`neutral`. ``); no prose surface.

FMT-02 enforces the full sealed pattern: `<N>. **<label>.**` with
numeric prefix + period + space + bolded label + period, in sequence
1–6 across each §E4 block.

## §7 — Position 116 Schema Field-Name Strings (FMT-08 target set)

Name-presence check only (not value-verbatim). All 11 strings must
appear as substrings in the §Position 116 Treatment section:

```
"call_index"
"position"
"critic_status"
"d7b_call_attempted"
"d7b_error_category"
"source_lifecycle_state"
"source_valid_status"
"actual_cost_usd"
"input_tokens"
"output_tokens"
"skip_reason"
```

Authority: Lock 1.5 — deterministic skipped-source schema.

## §8 — L12-14 Embedded Sub-Group-Hypothesis Detector

Self-contained. Stage 2c detector gather (Task 3a v3 evidence round)
confirmed no runtime sub-group-hypothesis scanner exists in code;
`D7B_FORBIDDEN_TERMS` in `agents/critic/d7b_prompt.py` scans D7b LLM
output for decision/verdict language (accept/reject/etc.) and is
orthogonal in scope. L12-14 must therefore provide its own detector.

**Scope:** §E4 per-candidate blocks only. Per-field scan.

**Excluded field:** `Reconciliation expectation.` — legitimate
cohort-referencing surface (Stage 2c label semantics, Universe A/B,
§6.4 membership, TBD-A1/A2 aggregate feeds).

**Scanned fields (5):**
- `Structural assessment.`
- `Plausibility expectation.`
- `Alignment expectation.`
- `SVR expectation.`
- `Core judgment.`

**Field 7 `UA metadata.` not scanned** — contains only structured
JSON-style literal (`` `universe_a_label`: `<value>`. ``); no prose
surface.

**Denylist** (case-insensitive, word-boundary enforced):

```
"subgroup", "sub-group", "cluster of candidates", "class of candidates",
"candidates of this type", "tend to land", "typically land",
"usually land", "as a group", "in this group",
"members of this group", "candidates like these",
"bimodal", "monotonic subgroup"
```

**Allowlist scope (strict):** applied only when the parser is inside
the §6.4 section boundary — i.e., between a `## ` header matching
`SECTION_64_HEADER_RE` and the next `## ` header. The allowlist does
NOT apply inside §E4 per-candidate blocks (§E4 is a separate
`## ` section).

**Allowlist exact phrases (within §6.4 boundary only):**

- `"at least 2 of 7 fresh-7 candidates"`
- `"fresh-7 RSI-absent vol_regime"`
- `"RSI absent and vol_regime"`

Outside §6.4 boundary, denylist hits always FAIL regardless of
surrounding tokens. A sentence in §E4 prose containing `"vol_regime"`
or `"RSI absent"` does NOT bypass the denylist — those tokens are
discussion-legitimate elsewhere but the allowlist is scope-gated.

## §9 — Gate Dependency Graph (SKIP Cascade)

```
L12-01 (file I/O)
  ├── L12-02 ─────────── FMT-05, FMT-06, FMT-07
  ├── L12-03, L12-17
  ├── L12-04 ─────────── FMT-11
  ├── L12-05 ─────────── L12-09, L12-10, FMT-01, FMT-02, FMT-02b,
  │                      FMT-03, FMT-04, L12-14, FMT-11
  ├── L12-06 ─────────── L12-07, L12-08, FMT-11
  ├── L12-11, L12-12, L12-13, L12-15
  └── L12-16 ─────────── FMT-07, FMT-08, FMT-09
```

**SKIP logic:**
- `L12-01 FAIL` → emit `exit 2` immediately (harness error). All
  subsequent gates are unreached.
- A JSON-loading gate (`L12-04` / `L12-05` / `L12-06`) `FAIL` on
  file-presence or parse → downstream dependent gates `SKIP` with
  reason `"upstream <id> failed"`. `SKIP` lines go to stderr; not
  counted as `FAIL`.
- Counted-gate `FAIL` that does not break downstream inputs → downstream
  gates still run normally.

## §10 — Output Format (Reference Example)

```
stage2d_self_check v5 | target=docs/d7_stage2d/stage2d_expectations.DRAFT.md
─────────────────────────────────────────────────────────────────────
WARN PATH-01  operating on DRAFT (pre-rename)   [harness-level; not counted]
PASS L12-01   file exists, UTF-8 valid
PASS L12-02   all 10 required canonical headers present; 2 permitted additional (§6.5, §6.6); 0 unexpected extras
PASS L12-05   deep_dive_candidates.json: 20 entries, no pos 116, no Stage 2c overlap
FAIL L12-14   1 violation: pos=128 field="Alignment expectation." phrase="tend to land" section="## §E4 — ..."
PASS FMT-02   20/20 blocks contain numbered+ordered 6-label skeleton
PASS FMT-02b  UA metadata: 9 present (fresh-9), 11 absent (non-fresh-9)
PASS FMT-05   §E3 defects subsection present with Issue B, Issue D, Path A, audit trail
PASS FMT-11   3/3 cross-consistency sets match (FRESH_9, TIER_1, STAGE2C)
...
─────────────────────────────────────────────────────────────────────
SUMMARY (28 counted gates): 27 PASS, 0 WARN, 1 FAIL, 0 SKIP | 1 harness WARN | runtime=1.87s
EXIT 1
```

**Tally arithmetic:** PASS + counted-WARN + FAIL + SKIP = 28. PATH-01 /
PATH-02 are harness WARNs, surfaced inline but excluded from the tally.
Exit code driven solely by counted-gate outcomes: any FAIL → 1; else 0
(counted-WARN permitted in lenient mode).

## §11 — Known Non-Goals

- No semantic judgment on prose content quality.
- No Stage 2c 20-call cohort re-validation (Stage 2c sign-off is
  upstream trust anchor).
- No scope-lock SHA pinning (FMT-10 dropped).
- No budget-ledger / API-key / spend-ledger validation (orchestrator's
  job).
- No JSON-fixture regeneration (read-only).
- No `--output-json` flag in Task 3b (deferred to Task 3c).

## §12 — Runtime Envelope

< 5 s expected. Sequential reads, single-pass regex scans, ~2 MB total
file I/O. No parallelism. Stdlib only: `re`, `json`, `hashlib`,
`pathlib`, `sys`, `argparse`, `dataclasses`.

---

## §Errata (against v5 delta)

**Erratum E1 — gate count** (v5 §10 output example and §1 text
understated).

- v5 stated "27 counted gates" throughout.
- Correct value under Option X (FMT-02 + FMT-02b as distinct gates):
  **28 counted gates**.
- Breakdown: 17 Lock 12 gates (L12-01..17) + 11 format gates (FMT-01,
  FMT-02, FMT-02b, FMT-03, FMT-04, FMT-05, FMT-06, FMT-07, FMT-08,
  FMT-09, FMT-11). FMT-10 does not exist.
- Integration-test expectation against current DRAFT SHA
  `98b87a702cc80df2d993d51857d4142f93f2ab8be66438bd2937c5dd374010a5`:
  **27 PASS + 0 counted-WARN + 0 FAIL + 0 SKIP + 1 harness WARN
  (PATH-01)**, assuming DRAFT passes all gates.
- Resolution: this document bakes 28 into §1, §5 header, §10 example,
  and all downstream arithmetic. No v6 delta emitted; consolidated
  document is the canonical source-of-truth.

**Erratum E2** — no additional erratum pending.

---

## §Revision History

| Revision | Status | Notable |
|----------|--------|---------|
| v1       | Superseded | Initial draft. |
| v2       | Blocker | §6 field labels fabricated; rebuilt v3 against disk. |
| v3       | Ratified body | Disk-verified §6; Stage 2c detector gather documented; 6 structural fixes. |
| v4       | Ratified delta | L12-02 header count; FMT-05 retargeted to E3 defects subsection; §8 cleaned; L12-14 allowlist regex-boundary; FMT-11 derivation explicit; FMT-02 numbered+ordered; FMT-02b prefix enforcement; L12-15 scope specification; FRESH_7 exclusion from FMT-11. |
| v5       | Ratified delta | PATH-01/02 reclassified as harness-level WARNs (not counted); output tally reconciled; FRESH_7 comment corrected to cite L12-13 not FMT-04. |
| (this)   | Consolidated | v3 body + v4 + v5 deltas folded inline; Erratum E1 gate-count correction (27 → 28) applied throughout. |

---

## §Post-Write Verification Protocol

After writing this file to disk, reviewer must:
1. Record byte count, line count, SHA256.
2. Re-read post-write to confirm content intact.
3. Post verification in chat before drafting Task 3b.1 scaffold.
