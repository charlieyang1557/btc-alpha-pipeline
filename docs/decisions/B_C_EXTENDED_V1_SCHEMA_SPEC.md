# B-C-extended v1 schema spec (Contracts 2.0.1-2.0.5)

> **Canonical specification** for the `b_c_extended_v1` artifact attestation
> domain. Authoritative on:
>
> - **Contract 2.0.1** — γ3/γ4 moment estimator convention (§2)
> - **Contract 2.0.2** — schema version + per-domain tuple architecture (§1)
> - **Contract 2.0.3** — triple linkage `hypothesis_hash + batch_id + run_id` (§3)
> - **Contract 2.0.4** — `cost_anchor_id` mapping + path canonicalization (§3)
> - **Contract 2.0.5** — 14 header fields + per-bar artifact validation discipline (§1)
>
> Companion docs (existing attestation domains): [WF_TEST_BOUNDARY_SEMANTICS.md](./WF_TEST_BOUNDARY_SEMANTICS.md)
> (walk-forward + evaluation domains) + [wf_test_boundary_semantics_test_classification.md](./wf_test_boundary_semantics_test_classification.md)
> (test surface companion). Extension protocol for future schema versions: see
> companion doc `SCHEMA_VERSION_EXTENSION_PROTOCOL.md` (T1.6 §2.6 deliverable
> `(f)`).

---

## §0 Status + provenance

- **Status:** SEALED at B-C-extended Scope-B refactor cycle (R3.1d sequencing
  1→3→4 per parent plan v5)
- **Schema version:** `b_c_extended_v1` (Contract 2.0.2 LOCK)
- **Attestation domain:** per-bar return series preservation artifacts
  (distinct from evaluation + walk-forward domains; see
  [WF_TEST_BOUNDARY_SEMANTICS.md](./WF_TEST_BOUNDARY_SEMANTICS.md))
- **Sealed Contract source:**
  [`docs/superpowers/plans/2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md`](../superpowers/plans/2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md)
  §2.0.1-§2.0.6 (parent plan v5 RATIFIED)
- **SEAL bundle commits:**

  | Task | Scope | Commit |
  |---|---|---|
  | T1.2 | Schema validator (`b_c_extended_v1` + per-domain tuple split + 3 helpers + CONTRACT BOUNDARY) | `12dffde` (2026-05-22) |
  | T1.3 | Registry API + LineageContext threading + `MIGRATION_COLUMNS` extension | `12dffde` (2026-05-22) |
  | T1.1 | Engine artifact writer + slice-aware emission (9-iteration arc; SYS5 producer-side `revalidate_for_write()`) | `12dffde` (2026-05-23) |
  | T1.4 | Backward-compatibility verification + `_T1X_NEW_COLUMNS` test mirror | `5a44ec6` (2026-05-23) + cleanup `56fe413` |
  | T1.5 | Fixture/smoke/registry-integrity test suite (20 tests) | `9d9a40d` (2026-05-24) |
  | T1.6 | Documentation + consumer enumeration (this doc + companion `SCHEMA_VERSION_EXTENSION_PROTOCOL.md` + `data_dictionary.md` updates + consumer enumeration table) | this commit |

- **Document scope (per T1.6 DS1 lock 2026-05-24):** single canonical doc
  covering §1 schema spec (a) + §2 γ3/γ4 convention (b) + §3 registry linkage (c)
  + §4 migration notes (d). Override condition: if any single Contract section
  exceeds ~300 lines empirically, split that one Contract to a companion doc per
  existing UPPER_CASE + lower_case convention.

---

## §1 Schema spec (Contract 2.0.2 + 2.0.5)

### §1.1 Schema version identifier

- **String literal:** `b_c_extended_v1`
- **Constant name:** `ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1`
- **Canonical declaration site:** [`backtest/artifact_schema.py:42`](../../backtest/artifact_schema.py#L42)
- **Re-export shim for consumer backward compat:** [`backtest/wf_lineage.py:546-563`](../../backtest/wf_lineage.py#L546-L563)
  (preserves public surface per C1-extract-pre-SEAL Charlie register
  2026-05-22; canonical implementation lives in `backtest.artifact_schema`)

### §1.2 Per-domain tuple architecture (T1.2 Sub-decision A lock; SEALED at `12dffde`)

The schema version validation surface is split across three per-domain tuples
(plus one backward-compat legacy alias). Each tuple binds an attestation domain;
each per-domain tuple has a matching `check_*_semantics_or_raise()` validation
helper.

| # | Tuple | Domain | Declaration site | Contents |
|---|---|---|---|---|
| 1 | `ACCEPTED_EVALUATION_SCHEMA_VERSIONS` | Evaluation (single-run holdout artifacts) | [`backtest/wf_lineage.py:111-114`](../../backtest/wf_lineage.py#L111-L114) | `phase2c_7_1` + `phase2c_8_1` |
| 2 | `ACCEPTED_WF_SCHEMA_VERSIONS` | Walk-forward (WF summary artifacts) | [`backtest/wf_lineage.py:119-122`](../../backtest/wf_lineage.py#L119-L122) | `phase2c_7_1` + `phase2c_8_1` |
| 3 | `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` | B-C-extended (per-bar return series artifacts) | [`backtest/artifact_schema.py:45-47`](../../backtest/artifact_schema.py#L45-L47) | `b_c_extended_v1` |
| 4 | `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` | **Backward-compat legacy alias** | [`backtest/wf_lineage.py:129-132`](../../backtest/wf_lineage.py#L129-L132) | `phase2c_7_1` + `phase2c_8_1` (currently identical to per-domain tuples #1 + #2 since both accept the same legacy versions) |

**Terminology note (per v2 PFR Advisor F7 reframing):** the sealed comment at
[`backtest/wf_lineage.py:124-125`](../../backtest/wf_lineage.py#L124-L125)
reads `# Backward-compat union: existing code that imported
ACCEPTED_ARTIFACT_SCHEMA_VERSIONS continues to work. New code should use the
per-domain tuples above.` The term "union" is a slight misnomer — the tuple
holds the pre-domain-split contents and currently mirrors the per-domain
contents; "legacy alias" is the more precise framing. Both terms refer to the
same constant; the sealed comment is authoritative on intent (preserve
backward-compat for pre-split consumers), the framing here is canonical for
new readers.

### §1.3 CONTRACT BOUNDARY (no cross-domain tuple pollution)

**Sealed module docstring at [`backtest/wf_lineage.py:47-51`](../../backtest/wf_lineage.py#L47-L51):**

```
CONTRACT BOUNDARY: ACCEPTED_EVALUATION_SCHEMA_VERSIONS and
ACCEPTED_WF_SCHEMA_VERSIONS are the existing-domain tuples; they MUST NOT
include b_c_extended_v1. ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS is the
B-C-extended-domain tuple; it MUST NOT include phase2c_7_1 or phase2c_8_1.
Each check_*_semantics_or_raise helper accepts ONLY its own domain's tuple.
```

**Reinforced at declaration site
[`backtest/wf_lineage.py:107-108`](../../backtest/wf_lineage.py#L107-L108):**

```
# CONTRACT BOUNDARY: no tuple may contain another domain's schema version.
# See module-level docstring for CONTRACT BOUNDARY declaration.
```

**Rationale:** the constant-level domain fence prevents cross-domain validation
pollution. Without the BOUNDARY, future code adding a new schema version to the
wrong tuple would silently broaden the accepting set of an unrelated domain's
helper — a class of error that would slip through type checks (all tuples have
the same `tuple[str, ...]` type) but cause semantic-level cross-contamination
(WF helpers accepting B-C-extended artifacts or vice versa).

### §1.4 Three distinct validation branch helpers

Each per-domain tuple has a paired validation helper that accepts ONLY its own
domain's tuple. Validation logic is routed at the consumer call site (consumer
determines the domain and calls the appropriate helper).

| Helper | `def` line | Domain tuple gate | Inner `schema_version` validation branch |
|---|---|---|---|
| `check_wf_semantics_or_raise()` | [`backtest/wf_lineage.py:262`](../../backtest/wf_lineage.py#L262) | `ACCEPTED_WF_SCHEMA_VERSIONS` | [`:334-349`](../../backtest/wf_lineage.py#L334-L349) (executable block; rejects `b_c_extended_v1` and all other non-WF) |
| `check_evaluation_semantics_or_raise()` | [`backtest/wf_lineage.py:352`](../../backtest/wf_lineage.py#L352) | `ACCEPTED_EVALUATION_SCHEMA_VERSIONS` | [`:489-503`](../../backtest/wf_lineage.py#L489-L503) (executable block; rejects `b_c_extended_v1` and all other non-evaluation; comment header at `:486-488` excluded per stated convention) |
| `check_b_c_extended_semantics_or_raise()` | [`backtest/artifact_schema.py:654`](../../backtest/artifact_schema.py#L654) (canonical impl; re-exported via shim at [`backtest/wf_lineage.py:559`](../../backtest/wf_lineage.py#L559)) | `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` | Enforces all 14 Contract 2.0.5 header fields + per-bar linkage validation discipline (§1.6) + T_obs (§1.5b) |

**Inner-branch line ranges (per v2 PFR Advisor F1 correction):** the `def` lines
above point at the function definitions; the inner schema_version validation
branch within each function lives at the cited range and contains only the
executable validation block (the lines preceding each range hold the comment
header, intentionally excluded from the cite).

### §1.5 14 header field enumeration (Contract 2.0.5)

The header fields are enumerated verbatim in
[parent plan v5 §2.0.5 lines 144-159](../superpowers/plans/2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md#L144-L159).
DO NOT duplicate the table; the parent plan is the authoritative source for
the per-field type + Optional-ness + per-row description. Cross-reference
summary (count + identity only):

| # | Field | Type |
|---|---|---|
| 1 | `artifact_schema_version` | string (LOCKED `b_c_extended_v1`) |
| 2 | `run_id` | string |
| 3 | `hypothesis_hash` | string |
| 4 | `source_batch_id` | string |
| 5 | `parent_run_id` | Optional[string] |
| 6 | `regime_key` | string |
| 7 | `engine_commit` | string |
| 8 | `current_git_sha` | string |
| 9 | `execution_config_path` | string |
| 10 | `execution_config_sha256` | string |
| 11 | `parquet_data_sha256` | string |
| 12 | `cost_anchor_id` | string |
| 13 | `returns_per_bar_path` | string |
| 14 | `returns_per_bar_sha256` | string |

**Producer-side field source (infrastructure at T1.6; production producer deferred):** the
`LineageContext` dataclass at
[`backtest/artifact_schema.py:205-311`](../../backtest/artifact_schema.py#L205-L311)
holds **13 header/linkage fields plus T_obs = 14 dataclass fields total** as
frozen attributes (decorator + class def at :205-206; attribute declarations
span :280-311 ending at `parent_run_id` at :311; verified by sealed contract
lock at [`tests/test_t1_3_registry_api.py:236-245`](../../tests/test_t1_3_registry_api.py#L236-L245)
`test_field_count_is_14` asserting `len(dataclasses.fields(LineageContext)) == 14`).
The 14 LineageContext fields comprise 13 of the Contract 2.0.5 header fields
PLUS T_obs (per §1.5b); `artifact_schema_version` (field 1 of Contract 2.0.5) is
explicitly excluded from `LineageContext` per the D2-b design at
[`backtest/artifact_schema.py:220-231`](../../backtest/artifact_schema.py#L220-L231)
— it is a producer-stamped header field, not a lineage-carried attribute.

**Production producer chain status (T1.6 = infrastructure-only; CONTRACT GAP):**
the b_c_extended_v1 schema architecture at T1.6 ships **validator + dataclass +
constants + 9 registry migration columns** — but **no production code currently
emits b_c_extended_v1-stamped artifacts**. As of T1.6, `engine._write_to_registry()`
at [`backtest/engine.py:839+`](../../backtest/engine.py#L839) populates registry
columns from `LineageContext` when provided but does NOT stamp
`artifact_schema_version` onto any JSON header (no JSON header is written by the
T1.6 producer chain). `engine.write_per_bar_artifact()` at
[`backtest/engine.py:443-627`](../../backtest/engine.py#L443-L627) emits ONLY the
per-bar parquet (timestamp + portfolio_value + return columns) with no header
metadata. The only production code currently stamping `artifact_schema_version`
is [`scripts/run_phase2c_evaluation_gate.py:402`](../../scripts/run_phase2c_evaluation_gate.py#L402)
which stamps `phase2c_7_1` / `phase2c_8_1` (sibling evaluation-domain values), NEVER
`b_c_extended_v1`.

**CONTRACT GAP:** future b_c_extended_v1 producer code (per the B-C-narrow
data-recovery successor cycle binding condition per CLAUDE.md Phase Marker)
will need to stamp `artifact_schema_version = "b_c_extended_v1"` onto the
per-bar artifact JSON header alongside the 13 LineageContext-derived header
fields + T_obs. The validator
`check_b_c_extended_semantics_or_raise()` at [`backtest/artifact_schema.py:654`](../../backtest/artifact_schema.py#L654)
is the consumer-side enforcement that future producer code must satisfy. Trigger
condition: B-C-narrow successor cycle authorization for per-bar artifact emission;
producer-stamp obligation lands at that cycle, not T1.6.

**Consumer-side field validation:** `check_b_c_extended_semantics_or_raise()`
at [`backtest/artifact_schema.py:654`](../../backtest/artifact_schema.py#L654)
enforces presence + type + cross-field consistency for all 14 fields + T_obs.

### §1.5b T_obs — required-adjacent 15th field (per sub-plan SEAL-eve Round 1 Codex F1 MEDIUM)

**Why required-adjacent vs in-14-field-table:** Contract 2.0.5 enumerates 14
header metadata fields covering identity + linkage + path + content-hash. T_obs
is a **per-bar-artifact-content-shape attribute** — semantically distinct from
header metadata. It is required for `b_c_extended_v1` validation but is not part
of the 14-field header table.

**Sealed declaration** at [`backtest/artifact_schema.py:307-309`](../../backtest/artifact_schema.py#L307-L309)
(within `LineageContext` dataclass):

```python
# T_obs is not in the 14-field header table but is required for artifact validation;
# included here as field 13-equivalent for moment + T_obs linkage.
T_obs: int
```

**Sealed validation** at [`backtest/artifact_schema.py:815-827`](../../backtest/artifact_schema.py#L815-L827)
(within `check_b_c_extended_semantics_or_raise()` body):

```python
# 2c. T_obs: present, integer, positive.
if "T_obs" not in summary:
    errors.append("T_obs: missing key (required for b_c_extended_v1)")
else:
    t_obs = summary["T_obs"]
    if not isinstance(t_obs, int) or isinstance(t_obs, bool):
        errors.append(
            f"T_obs: expected positive integer, got {type(t_obs).__name__!r}"
        )
    elif t_obs <= 0:
        errors.append(
            f"T_obs: must be positive (> 0), got {t_obs!r}"
        )
```

**Type:** `int` (positive integer). `bool` is explicitly rejected because
`isinstance(True, int)` returns `True` in Python (`bool` is an `int` subclass);
the `or isinstance(t_obs, bool)` clause guards against that conflation.

**Semantic:** count of finite per-bar return observations stored in the
artifact's `returns_per_bar.parquet`. The per-bar artifact validation
discipline (§1.6) requires `T_obs == finite-row-count` of the read parquet
(T_obs-alignment check, step 4).

**Registry linkage:** T_obs is one of 3 T1.1 FIX-B1 per-bar artifact linkage
fields persisted to `runs` via `engine._write_to_registry()` when
`lineage_context` is provided. See §4.2 item 2 (3 T1.1 FIX-B1 fields at
[`backtest/experiment_registry.py:155-157`](../../backtest/experiment_registry.py#L155-L157)).

### §1.6 Per-bar artifact validation discipline (4-step protocol; Contract 2.0.5)

Consumer-side validation of a `b_c_extended_v1` artifact runs four checks
in sequence, all fail-closed:

1. **File-exists check:** consumer MUST verify `returns_per_bar_path` resolves
   to an existing file before reading. Fail closed on absence.
2. **Path confinement:** consumer MUST verify resolved path is under the
   artifact's containing directory `<run_id_or_batch_dir>/<hypothesis_hash>/`
   (no `../` escapes). Fail closed on confinement violation.
3. **SHA256 recomputation on read:** consumer MUST recompute SHA256 of read
   file content and compare against stored `returns_per_bar_sha256`. Fail
   closed on mismatch. (Matches the precedent set by `parquet_data_sha256`
   for source data integrity.)
4. **T_obs alignment check:** consumer MUST verify stored `T_obs` matches the
   actual finite-row count of the per-bar series. Fail closed on mismatch.

**Source:** parent plan v5 §2.0.5 lines 161-165 (verbatim discipline) +
sealed implementation in `check_b_c_extended_semantics_or_raise()` at
[`backtest/artifact_schema.py:654+`](../../backtest/artifact_schema.py#L654).

### §1.7 Backward compatibility statement

- Legacy `phase2c_7_1` + `phase2c_8_1` consumers continue to validate via
  the existing per-domain helpers `check_evaluation_semantics_or_raise()` +
  `check_wf_semantics_or_raise()` without modification.
- `b_c_extended_v1` is **additive** via the new B-C-extended attestation
  domain — new per-domain tuple + new helper at canonical site
  ([`backtest/artifact_schema.py`](../../backtest/artifact_schema.py)) + shim
  re-export ([`backtest/wf_lineage.py:546-563`](../../backtest/wf_lineage.py#L546-L563)).
- The legacy alias `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` ([`backtest/wf_lineage.py:129-132`](../../backtest/wf_lineage.py#L129-L132))
  preserves the import surface for pre-split consumers; it does NOT include
  `b_c_extended_v1` per CONTRACT BOUNDARY (§1.3).
- See `CONTRACT GAP` at [`backtest/wf_lineage.py:126-128`](../../backtest/wf_lineage.py#L126-L128)
  for the consumer-migration trigger: consumers that import the legacy alias
  AND perform per-version branching should migrate to the per-domain tuple
  matching their attestation domain. Audit via `rg "ACCEPTED_ARTIFACT_SCHEMA_VERSIONS"`.

### §1.8 Producer / consumer responsibility split

- **Producer side at T1.6 (infrastructure-only):** the registry writer
  [`engine._write_to_registry()`](../../backtest/engine.py#L839) populates the
  9 new T1.x registry columns from `LineageContext` when provided (see §4 for
  column enumeration). The per-bar writer
  [`engine.write_per_bar_artifact()`](../../backtest/engine.py#L443) emits the
  `returns_per_bar.parquet` file with 3 columns (timestamp + portfolio_value +
  return; no JSON header is written by this writer at T1.6). Producer-side
  invariant enforcement lives in `LineageContext.revalidate_for_write()` at
  [`backtest/artifact_schema.py:449-540`](../../backtest/artifact_schema.py#L449-L540)
  (SYS5 centralized invariant per T1.1 9-iteration arc closure — see
  [`memory/feedback_invariant_level_vs_enumeration.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_invariant_level_vs_enumeration.md)
  cycle empirical).
- **Producer side post-B-C-narrow (CONTRACT GAP):** future b_c_extended_v1
  producer code (per the B-C-narrow data-recovery successor cycle binding
  condition per CLAUDE.md Phase Marker) will emit all 14 header fields + T_obs
  + per-bar parquet AND stamp `artifact_schema_version = "b_c_extended_v1"` onto
  the per-bar artifact JSON header. The validator (consumer side, below) is the
  pre-committed enforcement that future producer code must satisfy. **No T1.6
  production code currently emits b_c_extended_v1-stamped artifacts** —
  see §1.5 production producer chain status note for the verified-current-state
  details.
- **Consumer side** (`check_b_c_extended_semantics_or_raise()` at
  [`backtest/artifact_schema.py:654`](../../backtest/artifact_schema.py#L654)
  via shim re-export): validates all 14 header fields + T_obs + per-bar
  SHA256 + T_obs-alignment on read. Consumer-side validation is fully
  operational at T1.6 (eagerly ready for the future producer chain).
- **Domain selection:** consumer code calls the domain-appropriate helper
  (NOT the legacy alias). Per-domain helper rejects mismatched schema
  versions per CONTRACT BOUNDARY.

---

## §2 γ3/γ4 raw-standardized convention (Contract 2.0.1)

### §2.1 Estimator formulas (population moments; not bias-corrected)

- **γ3 (sample skew):**
  `mean((r - rbar)^3) / mean((r - rbar)^2)^(3/2)`
  Gaussian limit: γ3 = 0
- **γ4 (raw standardized kurtosis; NOT excess):**
  `mean((r - rbar)^4) / mean((r - rbar)^2)^2`
  Gaussian limit: γ4 = 3

Both formulas are **population** estimators (denominator divides by N, not
N-1). γ4 is **raw** kurtosis (Gaussian = 3), NOT **excess** kurtosis
(Gaussian = 0). This is the per-cycle LOCK at Contract 2.0.1.

### §2.2 LOCKED implementations

- **γ4 LOCKED:** `scipy.stats.kurtosis(returns_array, fisher=False, bias=True, nan_policy='omit')`
- **γ3 LOCKED:** `scipy.stats.skew(returns_array, bias=True, nan_policy='omit')`

**Environment precondition:** scipy ≥ 1.9 required for the `nan_policy`
keyword. Fixture test fails closed if precondition is not met. See
[`tests/test_t1_5_fixture_moments.py`](../../tests/test_t1_5_fixture_moments.py)
§2.1.5 for the precondition gate.

### §2.3 5 PROHIBITED alternative implementations

Empirically-verified divergent values at fixture vector `[-1, 1, 0, 0, 0, 0]`
(N=6) per [`tests/test_t1_5_fixture_moments.py`](../../tests/test_t1_5_fixture_moments.py)
(9 test methods; LOCKED scipy + 5 PROHIBITED kurtosis lockout via independent
test methods preserving per-library failure attribution):

| # | Implementation | Value at fixture | Reason |
|---|---|---|---|
| 1 | `pandas.Series.kurt()` (default) | 2.5 | Fisher excess + bias-corrected (NOT raw) |
| 2 | `pandas.Series.kurt() + 3` | 5.5 | raw bias-corrected (NOT raw population) |
| 3 | `scipy.stats.kurtosis(fisher=True, bias=True)` (default scipy) | 0.0 | excess uncorrected (NOT raw) |
| 4 | `scipy.stats.kurtosis(fisher=True, bias=False)` | 2.5 | excess bias-corrected |
| 5 | `scipy.stats.kurtosis(fisher=False, bias=False)` | 5.5 | raw bias-corrected (NOT raw population) |

### §2.4 LOCKED reference value (NOT in PROHIBITED list)

For the same fixture vector `[-1, 1, 0, 0, 0, 0]` (N=6):

`scipy.stats.kurtosis([-1, 1, 0, 0, 0, 0], fisher=False, bias=True, nan_policy='omit')` = **3.0** (raw uncorrected; Gaussian limit; THIS CONVENTION).

This row is the LOCKED reference value; the 5 PROHIBITED alternatives in
§2.3 are explicitly the "what the convention is NOT" set, useful for
disambiguating downstream code that may accidentally import an unlocked
variant.

### §2.5 Downstream consumer note (DSR consumption layer)

The Bailey-López de Prado (BLdP) Deflated Sharpe Ratio at R6.1 Tier 6
promotion class applies an excess conversion (`γ4 - 3`) if the formula
expects excess kurtosis. The raw vs excess conversion happens at the
**consumption layer**, not at the artifact-emission layer. See
[`docs/phase5/R6_1_TIER_6_PROMOTION_CLASS_NOTE.md`](../phase5/R6_1_TIER_6_PROMOTION_CLASS_NOTE.md)
for the authoritative DSR consumption layer specification.

### §2.6 Test surface (empirical receipt)

Authoritative test for the LOCKED convention:
[`tests/test_t1_5_fixture_moments.py`](../../tests/test_t1_5_fixture_moments.py)
(9 test methods including γ3 PASS + 5 PROHIBITED kurtosis lockout +
scipy version precondition gate). T1.5 SEAL artifact at commit `9d9a40d`
is the empirical receipt for the LOCKED convention.

### §2.7 Cycle motivation (orchestrator-adjudication-error pattern)

The fixture test exists in part because the B-C-extended planning arc
itself surfaced 3 instances of orchestrator-adjudication-error on
kurtosis convention questions (v1 "5.5" PUSHBACK + v3 "fisher=True 2.5"
misattribution + v4 "12 total fields" count drift; all caught by
cross-model leg). See parent plan v5 §0 lines 23-29 for the historical
context. The fixture vector + 5 PROHIBITED lockout exist to provide a
runnable, fail-closed receipt for the convention so that future
adjudication errors are caught at test-time, not at downstream
consumption.

---

## §3 Registry linkage spec (Contract 2.0.3 + 2.0.4)

### §3.1 Triple linkage (Contract 2.0.3)

**Three required keys** for unique artifact-to-registry resolution:

- `hypothesis_hash` — canonical DSL hash + dedup key
- `batch_id` — orchestrator batch identifier
- `run_id` — per-run UUID

**Artifact-side ↔ registry-side field aliasing:**

- artifact `source_batch_id` ↔ registry `runs.batch_id`
- artifact `run_id` ↔ registry `runs.run_id`

The alias mapping is applied at write-time; consumer rejects mismatched
aliases at read-time.

**Resolution endpoint:** `experiments.db` `runs` table (SQLite). Canonical
resolution uses a 3-WHERE-clause join on the three required keys:

```sql
SELECT * FROM runs
WHERE hypothesis_hash = :hh
  AND batch_id = :bid
  AND run_id = :rid;
```

### §3.2 5 failure cases (per Contract 2.0.6 (d); T1.5 SEAL authoritative)

The triple-linkage discipline enforces 5 failure modes + 1 happy path. The
authoritative empirical receipt is
[`tests/test_t1_5_registry_integrity.py`](../../tests/test_t1_5_registry_integrity.py)
(7 test methods + 4 failure cases + 1 case-mismatch macOS APFS edge):

| # | Failure case | Disposition |
|---|---|---|
| 1 | Duplicate `run_id` | fail closed |
| 2 | Missing `hypothesis_hash` | fail closed |
| 3 | Missing `batch_id` | fail closed |
| 4 | Mismatched `cost_anchor_id` vs canonicalized `execution_config_path` mapping | fail closed |
| 5 | Un-mapped canonicalized `execution_config_path` (non-None, non-default) | fail closed |
| (happy path) | `None` → `config/execution.yaml` → `legacy_perp_inspired_7bps_v0` normalization | succeeds |

### §3.3 `cost_anchor_id` field location (Contract 2.0.4)

`runs.cost_anchor_id` is declared at two sites in
[`backtest/experiment_registry.py`](../../backtest/experiment_registry.py):

| Site | Line | Purpose |
|---|---|---|
| `CREATE TABLE runs (...)` column declaration | [:86](../../backtest/experiment_registry.py#L86) | `cost_anchor_id TEXT,` — initial-create schema |
| `MIGRATION_COLUMNS` entry | [:147](../../backtest/experiment_registry.py#L147) | `("cost_anchor_id", "TEXT"),` — ALTER TABLE migration for pre-existing databases |

**Correction history:** earlier handoff prompts cited `experiment_registry.py:86,139`;
line 139 is in the `regime_holdout_passed` migration area, NOT
`cost_anchor_id`. The correct migration entry is at **line 147** (Mode A
grep-verified at T1.6 §2.3 v1 PFR adjudication; v1 PFR Advisor F2 correction).

### §3.4 `cost_anchor_id` population mechanism

`cost_anchor_id` is resolved from the canonicalized `execution_config_path`
via a path-keyed mapping table (§3.6). The mapping is path-keyed (not
value-keyed) so that future cost anchors require only a new entry in
the mapping table + addition of a new config file.

### §3.5 Path canonicalization rule (per v1 PFR Codex F5; v2 PFR Advisor F6 range correction)

**Sealed implementation:** `canonicalize_execution_config_path()` at
[`backtest/artifact_schema.py:91-193`](../../backtest/artifact_schema.py#L91-L193)
(T1.3 SEAL bundle `12dffde`; Mode A grep-verified — function spans from
the `def` at line 91 through the `return rel.replace(os.sep, "/")` at
line 193).

**Rule (canonical form):**

1. Relative paths are anchored to `repo_root` BEFORE `realpath` resolution.
2. Absolute paths are used directly (with `realpath` for symlink
   resolution).
3. `commonpath`-based containment check ensures the candidate path is
   genuinely under `repo_root` (defends against `..` escapes).
4. Final form is a **repo-relative POSIX path** (POSIX separators
   regardless of host OS).

Cross-reference: parent plan v5 §2.0.4 enumerates the `commonpath`
invariant as the Contract-level containment requirement.

### §3.5a Case-sensitivity policy (v5 Fv5-1 LOW inline-fix; SEALED)

On case-insensitive filesystems (macOS HFS+/APFS default), an exact-case
match is required at mapping lookup. Case-only mismatches **FAIL CLOSED**
via mapping miss. This is the intended behavior: the mapping table
defines exact path-keys; future cost anchors will have exact-case path
entries; lookup is exact-case to prevent silent acceptance of
case-mismatched paths.

Test surface for the macOS APFS edge case:
[`tests/test_t1_5_registry_integrity.py`](../../tests/test_t1_5_registry_integrity.py)
(1 case-mismatch macOS APFS edge case among the 7 test methods).

### §3.6 6-row `cost_anchor_id` mapping table

Verbatim from parent plan v5 §2.0.4 lines 109-118 (column 1 + column 2
verbatim; column 3 paraphrased role per cross-leg-convergent v5 Fv5-2
LOW). Sealed at
[`backtest/artifact_schema.py:71-77`](../../backtest/artifact_schema.py#L71-L77)
as `COST_ANCHOR_ID_MAPPING: dict[str, str]`. Authoritative source:
[`docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md`](../phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md)
§5.2 lines 286-293.

| `execution_config_path` (path-key) | `cost_anchor_id` (value) | Role |
|---|---|---|
| `config/execution.yaml` | `legacy_perp_inspired_7bps_v0` | default; legacy Phase 1-2 runs |
| `config/execution_phase4_07bps.yaml` | `phase4_forward_07bps_v1` | Phase 4 cost-grid 07bps supplementary sensitivity |
| `config/execution_phase4_13bps.yaml` | `phase4_forward_13bps_v1` | Phase 4 cost-grid 13bps supplementary sensitivity |
| `config/execution_phase4_15bps.yaml` | `phase4_forward_15bps_v1` | Phase 4 forward-holdout primary basis per PHASE4_PLAN §1.5 |
| `config/execution_phase4_17bps.yaml` | `phase4_forward_17bps_v1` | Phase 4 cost-grid 17bps supplementary sensitivity |
| `config/execution_phaseb_spot_15bps.yaml` | `spot_realistic_15bps_v1` | Phase B Tier 5/6 conservative-anchor gate per R3.1d SEAL output |

### §3.7 Default normalization (Codex v3 Fv3-2 HIGH; Advisor v4 F-v4-6 LOW)

When `lineage_context` is `None` OR `execution_config_path` is `None`,
the canonical normalization is:

`None → config/execution.yaml → legacy_perp_inspired_7bps_v0`

This preserves the path-keyed mapping invariant (every persisted row has a
non-NULL `cost_anchor_id`) while accommodating legacy callers without
lineage context.

### §3.8 Fail-closed clause on un-mapped path

An un-mapped path (non-None, non-default) raises with an error message
containing:

1. The canonicalized un-mapped path
2. The full 6-row mapping table (so the error is self-contained)
3. Guidance: "Update R3.1d §5.2 mapping for new anchor or contact human
   approval before extending mapping."

### §3.9 HARD CONSTRAINT cross-reference

Per [`CLAUDE.md`](../../CLAUDE.md) line 272: `cost_anchor_id` is REQUIRED
for new Phase B / Tier 5 / Tier 6 runs once the schema migration lands.
This is part of the Conservative-Anchor Gate Integrity HARD CONSTRAINT
section per R3.1d V_SEAL 2026-05-19.

---

## §4 Migration notes (T1.x columns)

### §4.1 Migration class — ADDITIVE only

The T1.x migration is **ADDITIVE**: new columns are added to the existing
`runs` table; no pre-T1.x columns are removed or renamed. Pre-T1.x rows
remain readable; new columns default to NULL for legacy rows; pre-T1.x
consumers continue to work without modification.

### §4.2 Production source — `MIGRATION_COLUMNS`

The cumulative migration registry is
[`MIGRATION_COLUMNS` at `backtest/experiment_registry.py:121`](../../backtest/experiment_registry.py#L121)
(list start). The T1.x relevant entries span lines 141-170 and divide into
three subgroups by sealed comment delimiters:

1. **`cost_anchor_id` (Contract 2.0.4 + R3.1d Phase B)** at
   [:147](../../backtest/experiment_registry.py#L147) —
   `("cost_anchor_id", "TEXT"),`. Populated from canonicalized
   `execution_config_path` per §3.4.

2. **3 T1.1 FIX-B1 per-bar artifact linkage fields (Contract 2.0.5
   persistence obligation; populated by `engine._write_to_registry()`
   when `lineage_context` is provided)** at
   [:155-157](../../backtest/experiment_registry.py#L155-L157):
   - `("returns_per_bar_path", "TEXT"),` — relative path to per-bar
     returns parquet artifact
   - `("returns_per_bar_sha256", "TEXT"),` — SHA256 hex digest of that
     artifact (integrity)
   - `("T_obs", "INTEGER"),` — count of finite per-bar return observations
     stored in the artifact

3. **5 SYS-fix-1 `LineageContext` persistence fields (B3/B4 2026-05-23;
   populated from `LineageContext` when `lineage_context` is provided)**
   at [:166-170](../../backtest/experiment_registry.py#L166-L170):
   - `("regime_key", "TEXT"),` — regime identity key (e.g.
     `v2.regime_holdout`)
   - `("current_git_sha", "TEXT"),` — full-repo git SHA at run time
   - `("execution_config_path", "TEXT"),` — canonicalized repo-relative
     POSIX path to execution config YAML
   - `("execution_config_sha256", "TEXT"),` — content-addressable hash of
     execution config file
   - `("parquet_data_sha256", "TEXT"),` — content-addressable hash of
     source data parquet

**Total: 9 T1.x columns** (1 cost_anchor_id + 3 T1.1 FIX-B1 + 5 SYS-fix-1).

### §4.3 Test mirror — `_T1X_NEW_COLUMNS`

The test-only mirror is
[`_T1X_NEW_COLUMNS` at `tests/test_t1_4_backward_compat.py:51`](../../tests/test_t1_4_backward_compat.py#L51)
with invariant assertion
[`assert len(_T1X_NEW_COLUMNS) == 9, "§2.5 9 columns count invariant"`](../../tests/test_t1_4_backward_compat.py#L62)
at :62. The mirror has 7 reference sites across **6 distinct test
methods**:

| Site | Line | Containing method |
|---|---|---|
| :700 | reference 1 | distinct method (1 of 6) |
| :727 | reference 2 | distinct method (2 of 6) |
| :1251 | reference 3 | distinct method (3 of 6) |
| :1457 | reference 4 | distinct method (4 of 6) |
| :1607 | reference 5 | `test_pre_t1_3_db_state_migration_adds_columns_preserves_rows` (at :1582) — site 5 + 6 share this method (5 of 6) |
| :1614 | reference 6 | same method (`test_pre_t1_3_db_state_migration_adds_columns_preserves_rows`) — distinct site but same method |
| :1648 | reference 7 | `test_partial_migration_state_adds_remaining_columns` (at :1621; 6 of 6) |

**Correction history (per v1 PFR Codex F3 + Advisor F10):** earlier handoff
prompts referenced `_T1X_NEW_COLUMNS` as if it were a production constant.
It is **test-only**. The production source is `MIGRATION_COLUMNS`
(§4.2); `_T1X_NEW_COLUMNS` is the test mirror of the 9 T1.x columns
that the production migration adds (i.e., the test asserts the migration
adds exactly the 9 expected columns, not more, not fewer).

### §4.4 Schema migration mechanism — `ALTER TABLE ... ADD COLUMN`

When `runs` already exists (from an earlier phase), the migration runner
iterates `MIGRATION_COLUMNS` and applies any missing column via
`ALTER TABLE runs ADD COLUMN ...`. SQLite supports `ADD COLUMN` but not
in-place modification.

- **Iteration site:** the migration logic lives just past
  [`backtest/experiment_registry.py:197`](../../backtest/experiment_registry.py#L197)
  (`for col_name, col_def in MIGRATION_COLUMNS:` loop applies missing
  columns; T1.3 SEAL bundle `12dffde`).
- **Idempotency:** columns that already exist are silently skipped, so
  older Phase 1A rows are preserved untouched and newly-added Phase 2A /
  T1.x columns default to NULL on existing rows.

### §4.5 Backward compatibility

Four-statement set:

1. Pre-T1.x `runs` rows continue to be readable; new columns are NULL
   for legacy rows.
2. Pre-T1.x consumers continue to work (no required-field changes on
   existing columns; new T1.x columns are nullable).
3. New T1.x writers MUST populate all 9 new T1.x columns when
   `lineage_context` is provided.
4. **Backfill discipline:** existing Phase 1-2 runs are backfilled as
   `cost_anchor_id = 'legacy_perp_inspired_7bps_v0'`; Phase 4
   forward-holdout runs are backfilled per `execution_config_path` field
   per R3.1d §5.2 (see also the inline backfill provenance comment at
   [`backtest/experiment_registry.py:142-146`](../../backtest/experiment_registry.py#L142-L146)).

### §4.6 Write-time discipline

`_write_to_registry()` populates all 9 new T1.x columns for new runs
per Contracts 2.0.3 + 2.0.4 + 2.0.5. Legacy callers without
`lineage_context` normalize to `config/execution.yaml` default per
§3.7 (Contract 2.0.4 default normalization).

### §4.7 HARD CONSTRAINT cross-reference

Per [`CLAUDE.md`](../../CLAUDE.md) line 272: `cost_anchor_id` is REQUIRED
for new Phase B / Tier 5 / Tier 6 runs (also referenced from §3.9).

### §4.8 Schema version forward-compatibility (per v2 PFR Codex F2 conditional reframing)

Future schema versions extend the migration pattern **conditionally**:

- **(a)** If the new schema version adds new registry columns, append
  entries to `MIGRATION_COLUMNS` + update the relevant test mirror
  invariants where the new columns are asserted.
- **(b)** If the new schema version adds NO new registry columns (e.g.,
  metadata-only or per-bar-artifact-only changes), `MIGRATION_COLUMNS`
  and `_T1X_NEW_COLUMNS` need no update.

**Do NOT prescribe `_T1X_NEW_COLUMNS` update as the default future-schema
action** (v2 PFR Codex F2 anti-pre-emption). Document migration delta in
the successor's own decision doc + follow CONTRACT BOUNDARY discipline
at extension (different attestation domain → new per-domain tuple + new
helper). See companion doc `SCHEMA_VERSION_EXTENSION_PROTOCOL.md` (T1.6
§2.6 deliverable `(f)`) for the full schema-version extension protocol.

---

## §5 Further reading + cross-references

**Sealed Contract source (parent plan v5):**

- [`docs/superpowers/plans/2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md`](../superpowers/plans/2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md)
  §2.0.1-§2.0.6

**Companion docs (other attestation domains + extension protocol):**

- [WF_TEST_BOUNDARY_SEMANTICS.md](./WF_TEST_BOUNDARY_SEMANTICS.md) —
  WF + evaluation domain (`phase2c_7_1` + `phase2c_8_1`)
- [wf_test_boundary_semantics_test_classification.md](./wf_test_boundary_semantics_test_classification.md) —
  test surface companion for WF + evaluation domain
- `SCHEMA_VERSION_EXTENSION_PROTOCOL.md` (T1.6 §2.6 deliverable; see
  T1.6 sub-plan) — extension protocol for adding new schema versions

**Phase B / Tier 5 / Tier 6 context:**

- [`docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md`](../phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md) —
  authoritative 6-row `cost_anchor_id` mapping (§5.2)
- [`docs/phase5/R6_1_TIER_6_PROMOTION_CLASS_NOTE.md`](../phase5/R6_1_TIER_6_PROMOTION_CLASS_NOTE.md) —
  BLdP DSR consumption layer specification (§2.5 reference)

**HARD CONSTRAINTS:**

- [`CLAUDE.md`](../../CLAUDE.md) Conservative-Anchor Gate Integrity
  section (line ~270+) — `cost_anchor_id` HARD CONSTRAINT

**Sealed implementation:**

- [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) — 3 per-domain
  tuples + 3 helpers + CONTRACT BOUNDARY + legacy alias + shim re-exports
- [`backtest/artifact_schema.py`](../../backtest/artifact_schema.py) —
  `b_c_extended_v1` canonical implementation + `LineageContext` + T_obs
  + `canonicalize_execution_config_path()` +
  `COST_ANCHOR_ID_MAPPING` +
  `check_b_c_extended_semantics_or_raise()` + producer-side
  `revalidate_for_write()`
- [`backtest/experiment_registry.py`](../../backtest/experiment_registry.py) —
  `CREATE TABLE runs` (lines 1-100+) + `MIGRATION_COLUMNS` (lines
  121-170+) + ALTER TABLE migration runner (line 197+)

**Test surface:**

- [`tests/test_t1_4_backward_compat.py`](../../tests/test_t1_4_backward_compat.py) —
  `_T1X_NEW_COLUMNS` test mirror + 6 distinct test methods covering
  backward-compat invariants
- [`tests/test_t1_5_fixture_moments.py`](../../tests/test_t1_5_fixture_moments.py) —
  γ3 + γ4 LOCKED scipy implementation + 5 PROHIBITED kurtosis lockout
- [`tests/test_t1_5_smoke_end_to_end.py`](../../tests/test_t1_5_smoke_end_to_end.py) —
  end-to-end pipeline smoke (176-bar 2023-08 OHLCV; N=2 SMA crossover
  candidates)
- [`tests/test_t1_5_registry_integrity.py`](../../tests/test_t1_5_registry_integrity.py) —
  triple-resolution + 4 failure-cases + 1 case-mismatch macOS APFS edge

**Cycle empirical (memory standing rules):**

- [`memory/feedback_invariant_level_vs_enumeration.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_invariant_level_vs_enumeration.md) —
  T1.1 9-iteration arc producer-consumer asymmetry recurrence + SYS5
  centralized invariant closure pattern
- [`memory/feedback_advisor_own_anchoring_implementation_review.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_advisor_own_anchoring_implementation_review.md) —
  Rule 2 SEAL-eve adversarial discipline (vindicated empirically at T1.5
  + T1.6 sub-plan cycles)
