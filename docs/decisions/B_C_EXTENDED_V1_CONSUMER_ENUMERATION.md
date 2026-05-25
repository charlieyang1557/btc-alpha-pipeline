# B-C-extended v1 consumer enumeration

> Per-consumer disposition table for all consumers of the per-domain tuple
> architecture sealed at T1.2 (`12dffde`) + `b_c_extended_v1` schema version
> + `ARTIFACT_SCHEMA_VERSION_*` constants across the codebase.
>
> Companion doc:
> [B_C_EXTENDED_V1_SCHEMA_SPEC.md](./B_C_EXTENDED_V1_SCHEMA_SPEC.md) (full
> schema spec; this doc operates against §1 of that spec).
>
> Per T1.6 sub-plan §2.7 deliverable `(g)`; γ Hybrid Phase 1 skeleton
> (orchestrator pre-populates file:line + reference-type heuristic + tuple
> class; Phase 2 subagent fills Disposition + Cross-reference per
> surrounding-code read).

---

## §0 Status + provenance

- **Status:** Phase 1 skeleton complete + Phase 2 subagent fill COMPLETE
  (per sub-plan §2.7.3; opus general-purpose subagent classified 212 rows
  via ±20-line context read against each cited consumer file:line; Mode A
  spot-verification PASS on subagent disposition reasoning).
  Disposition summary at §3.15: HANDLES=181 / NO-OP=31 / NEEDS-EXTENSION=0.
- **Sub-plan source:** §2.7 of T1.6 sub-plan v_final (RATIFIED at `b6da611`
  2026-05-24)
- **Audit anchor:** 4-tuple architecture per T1.2 Sub-decision A lock (sealed
  at `12dffde`) — see [SCHEMA_VERSION_EXTENSION_PROTOCOL.md](./SCHEMA_VERSION_EXTENSION_PROTOCOL.md)
  for the extension protocol governing future schema additions

### §0.1 KNOWN ISSUE: `wf_lineage.py` cite line numbers in §3.x may be stale or chain-shifted

**Status:** RESOLVED at v_impl_polish (this commit) via atomic Python single-pass
remap on §3.2 cites; current cites point at correct sealed-code positions per
authoritative `rg` re-grep on current `backtest/wf_lineage.py`.

**Corrected root-cause analysis (post-Codex #N7 F3 + orchestrator Mode A
re-verification):** Phase 1 skeleton was generated from an `rg` grep on
`backtest/wf_lineage.py` AFTER orchestrator made two in-cycle edits to that
file (Canonical documentation pointer block +12 lines at module docstring +
stale function-docstring fix +3 lines at L386-392). Therefore the Phase 1
cites in the skeleton were CORRECT current sealed-code positions (e.g., `:111`
for ACCEPTED_EVALUATION_SCHEMA_VERSIONS declaration matched current code).

The drift damage was introduced by ORCHESTRATOR'S OWN bulk-fix attempts which
incorrectly assumed cites were pre-edit and applied `+12` shifts. Sequential
sed rules chain-collided (e.g., `:99 → :111` then `:111 → :123` cascaded
inappropriately). A subsequent Python recovery script also assumed pre-edit
and doubled damage on some cites. Both passes were premised on the FALSE
diagnostic that the Phase 1 grep was pre-edit.

Codex #N7 F3 (MEDIUM) partially caught this (identified specific drift
instances); orchestrator Mode A re-verification post-Codex-return then
revealed the mechanism was sed/Python over-shifting CORRECT cites, not
pre-edit drift in the original skeleton.

**v_impl_polish fix applied:** atomic Python single-pass remap (script at
`/tmp/fix_consumer_enum_p3p4.py`) using the original Phase 1 grep dump at
`/tmp/t1_6_phase1_g_grep.txt` as authoritative source (verified to contain
current sealed-code lines via independent re-grep). 37 unique line citations
in §3.2 restored to correct current positions. Also fixed §6 stale cite
`wf_lineage.py:114-116` → `:126-128` (Codex #N7 F3 secondary finding).

**Reliability claim:** all §3.x `file:line` columns now reflect current sealed
code. Dispositions were always correct (opus subagent read CURRENT code
±20 lines from each position at write-time). NEEDS-EXTENSION=0 conclusion
unchanged.

**Cycle empirical contributions (§35 codification candidates for B-C-extended
cycle SEAL boundary; tracking only):**

1. **Atomic single-pass remap discipline:** cite-shift corrections after
   upstream-code edits MUST use atomic single-pass mapping (Python/awk
   with single substitution dictionary), not sequential sed rules which
   chain-collide when OLD values of one rule match NEW values of another.
2. **Mode A discipline applies to root-cause diagnoses, not just symptom
   claims:** the original §0.1 framing claimed "Phase 1 grep was pre-edit"
   as a fact without grep-verifying that the cited lines actually pointed
   at pre-edit positions in current sealed code. A "this is why X is broken"
   statement is itself a factual claim subject to Mode A independent
   verification before adoption.
3. **Bulk-fix tooling matters at propagation chain:** Layer 3 orchestrator
   independent verification per
   [`memory/feedback_reviewer_routing_subagent_default.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md)
   3-layer safety architecture extends to ORCHESTRATOR'S OWN MITIGATION
   ACTIONS, not just to reviewer-leg outputs. Subagent (f) caught the cite
   drift correctly via Mode A grep at write-time; orchestrator's attempted
   sed/Python recovery without atomic single-pass introduced new damage.
   Forward discipline: any bulk-fix tooling for cite/cross-reference issues
   must be Mode A grep-verified PER OPERATION (not just per cite-found).

### §0.2 SCOPE NARROWING: 6-pattern audit excludes producer-side B-C-extended-API imports

Per Codex #N7 F5 (MEDIUM) caught at Implementation PFR 2026-05-25 — the §3.x
enumeration uses 6 grep patterns (T1-T4 + C + L per §1.1) targeting
**`schema_version`-discriminator consumers** (per-domain tuple membership +
`ARTIFACT_SCHEMA_VERSION_*` constants + `b_c_extended_v1` literal). The
audit **does NOT cover** B-C-extended API consumers that import producer-side
symbols without discriminating on `schema_version`:

| Consumer file | Out-of-scope reason | Imports |
|---|---|---|
| [`backtest/engine.py:971-975`](../../backtest/engine.py#L971-L975) | Producer-side writer; imports B-C-extended API but does not `schema_version`-discriminate | `LineageContext`, `canonicalize_execution_config_path`, `COST_ANCHOR_ID_MAPPING` |
| [`tests/test_t1_3_registry_api.py:112`](../../tests/test_t1_3_registry_api.py#L112) | T1.3 SEAL test surface; tests `canonicalize_execution_config_path` helper directly | `canonicalize_execution_config_path` |
| [`tests/test_t1_3_registry_api.py:240`](../../tests/test_t1_3_registry_api.py#L240) | T1.3 SEAL test surface; tests `LineageContext` 14-field-count contract directly | `LineageContext` |
| [`tests/test_t1_5_smoke_end_to_end.py:200`](../../tests/test_t1_5_smoke_end_to_end.py#L200) | T1.5 SEAL test surface; uses `LineageContext` as producer fixture | `LineageContext` |
| [`tests/test_t1_5_registry_integrity.py:215`](../../tests/test_t1_5_registry_integrity.py#L215) | T1.5 SEAL test surface; uses `LineageContext` + `_write_to_registry` for registry round-trip | `LineageContext` + `_write_to_registry` |

**Rationale for scope narrowing (per sub-plan §2.7.2 pattern selection):**
the 6-pattern audit specifically targets consumer code that needs to make
disposition decisions about `b_c_extended_v1` artifacts (HANDLES via
domain-appropriate helper vs NO-OP vs NEEDS-EXTENSION). Producer-side
B-C-extended API imports (LineageContext + canonicalize_execution_config_path
+ COST_ANCHOR_ID_MAPPING) are USERS of the producer infrastructure, not
discriminators of artifact schema version — they don't need to handle
`b_c_extended_v1` differently from other schema versions because they
CONSTRUCT the artifact in the first place. Adding them to the disposition
table would conflate two distinct concerns (producer vs consumer).

**No remediation required:** the 5 callsites above are intentional users of
the B-C-extended producer-side API; the consumer enumeration scope is
correctly bounded. NEEDS-EXTENSION conclusion unchanged (=0 across the
discriminator-consumer scope).

---

## §1 Audit methodology

### §1.1 Six grep patterns

| # | Pattern | Tuple/symbol class | Purpose |
|---|---------|-------------------|---------|
| T1 | `rg "ACCEPTED_EVALUATION_SCHEMA_VERSIONS"` | per-domain tuple | evaluation-domain consumers |
| T2 | `rg "ACCEPTED_WF_SCHEMA_VERSIONS"` | per-domain tuple | WF-domain consumers |
| T3 | `rg "ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS"` | per-domain tuple | B-C-extended-domain consumers (canonical at [`backtest/artifact_schema.py:45-47`](../../backtest/artifact_schema.py#L45-L47); re-exported via shim at [`backtest/wf_lineage.py:556`](../../backtest/wf_lineage.py#L556)) |
| T4 | `rg "ACCEPTED_ARTIFACT_SCHEMA_VERSIONS"` | legacy alias | backward-compat consumers (audit trigger per CONTRACT GAP at [`backtest/wf_lineage.py:126-128`](../../backtest/wf_lineage.py#L126-L128) — should migrate to per-domain tuple matching attestation domain) |
| C  | `rg "ARTIFACT_SCHEMA_VERSION_[A-Z0-9_]+"` | schema version constants | producer + test surfaces |
| L  | `rg "b_c_extended_v1"` | literal string-value | direct literal references (typically tests + docstrings + error messages) |

**Out of scope for this skeleton (deferred to Phase 2 surface):** `rg
"schema_version"` field-only references (~212+ hits across tests; mostly
test fixtures + dict-key accesses; Phase 2 subagent assesses whether any
need disposition).

### §1.2 Six directories audited

`backtest/` + `agents/` + `strategies/` + `factors/` + `scripts/` +
`tests/` (per sub-plan §2.7.2 item 2; `scripts/` added per v1 PFR Advisor
F5 — contains evaluation-gate driver
[`scripts/run_phase2c_evaluation_gate.py`](../../scripts/run_phase2c_evaluation_gate.py)
per parent plan v5 line 239).

### §1.3 Reference-type classification (Phase 1 best-guess heuristic; Phase 2 refines)

| Reference type | Heuristic source |
|---|---|
| `declaration` | Hit lives at the canonical declaration site (`backtest/wf_lineage.py` constants section or `backtest/artifact_schema.py` constants section) |
| `helper_internal` | Hit lives within a `check_*_semantics_or_raise()` body or related helper code |
| `docstring` | Hit appears inside a docstring (triple-quoted) or module-level comment |
| `import` | Hit is part of an `import` / `from ... import` statement |
| `function_call` | Hit is part of a function-call expression (producer/consumer code path) |
| `test_fixture` | Hit appears in a pytest fixture definition |
| `test_assertion` | Hit appears in an `assert ...` statement or pytest comparison |
| `test_dict_key` | Hit appears as a dict-key in a test setup (e.g., `{"artifact_schema_version": ...}`) |
| `comment_reference` | Hit appears in inline comment text |

Phase 2 subagent verifies the heuristic per ±20-line context read and
classifies disposition (HANDLES / NO-OP / NEEDS-EXTENSION) + adds
cross-reference column.

---

## §2 File-level summary

### §2.1 Hits per file × pattern class

Total: **212 hits** across **14 files** (6 patterns; excludes
`schema_version` field-only references — Phase 2 surface).

| File | T1 (EVAL) | T2 (WF) | T3 (B_C_EXT) | T4 (LEGACY) | C (CONST) | L (LITERAL) | Total | Class |
|------|-----------|---------|--------------|-------------|-----------|-------------|-------|-------|
| `backtest/wf_lineage.py` | 5 | 8 | 3 | 5 | 15 | 4 | **40** | production (declaration + helpers + shim) |
| `backtest/artifact_schema.py` | 0 | 0 | 5 | 0 | 3 | 7 | **15** | production (canonical implementation) |
| `scripts/run_phase2c_evaluation_gate.py` | 0 | 0 | 0 | 1 | 1 | 0 | **2** | production (evaluation-gate driver) |
| `scripts/compare_multi_regime.py` | 0 | 0 | 0 | 0 | 2 | 0 | **2** | production (comparison driver) |
| `tests/test_b_c_extended_schema.py` | 12 | 12 | 6 | 0 | 13 | 30 | **73** | test (T1.2 schema test suite) |
| `tests/test_wf_lineage_guard.py` | 0 | 6 | 0 | 5 | 15 | 7 | **33** | test (T1.2 wf_lineage test suite) |
| `tests/test_t1_4_backward_compat.py` | 0 | 0 | 4 | 0 | 0 | 7 | **11** | test (T1.4 backward-compat) |
| `tests/test_phase2c_evaluation_gate_runner.py` | 0 | 0 | 0 | 0 | 11 | 0 | **11** | test (evaluation-gate runner) |
| `tests/test_compare_multi_regime.py` | 0 | 0 | 0 | 0 | 8 | 0 | **8** | test (multi-regime comparison) |
| `tests/test_t1_1_sys_fix.py` | 0 | 0 | 0 | 0 | 3 | 1 | **4** | test (T1.1 SYS-fix-1 + SYS5 invariant) |
| `tests/test_filter_evaluation_gate.py` | 0 | 0 | 0 | 0 | 4 | 0 | **4** | test (evaluation-gate filter) |
| `tests/test_compare_2022_vs_2024.py` | 0 | 0 | 0 | 0 | 4 | 0 | **4** | test (multi-regime variant) |
| `tests/test_t1_1_artifact_writer.py` | 0 | 0 | 0 | 0 | 0 | 3 | **3** | test (T1.1 writer chain) |
| `tests/test_phase4_regime_config.py` | 0 | 0 | 0 | 0 | 2 | 0 | **2** | test (Phase 4 regime config) |
| **Total** | **17** | **26** | **18** | **11** | **81** | **59** | **212** | — |

### §2.2 Non-consumer directories (asserted via grep zero-hit)

The following 3 directories returned **0 hits** across all 6 patterns:

- `agents/` — 0 hits (B-C-extended attestation is not part of D6/D7/D8
  agent loop scope; Phase 2 = AI loop; pre-T1.x)
- `strategies/` — 0 hits (strategy code is DSL/Backtrader-level; does not
  read schema version)
- `factors/` — 0 hits (factor library is Phase 2A; pre-T1.x; reads OHLCV
  parquet only)

**Phase 2 verification:** subagent should confirm zero-hit via independent
`rg` re-run on each pattern × dir before locking; if any new hits
surface (e.g., new agent loop code added between Phase 1 + Phase 2),
classify accordingly.

---

## §3 Per-hit disposition table skeleton

> **PHASE 1 SKELETON:** file:line + tuple class populated; reference_type
> from §1.3 heuristic.
>
> **PHASE 2 SUBAGENT FILL:** subagent reads ±20-line context per hit and
> populates the Disposition + Cross-reference columns. Per sub-plan §2.7.3:
> classify as HANDLES (handles `b_c_extended_v1` correctly via
> domain-appropriate helper) / NO-OP (explicit no-op behavior with
> rationale) / NEEDS-EXTENSION (requires code change). For NEEDS-EXTENSION
> rows: **firmly deferred to successor cycle eligible-not-named per
> anti-pre-emption + v1 PFR Codex F2 — NO in-cycle scope expansion**.

### §3.1 `backtest/artifact_schema.py` (canonical implementation; 15 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:1`](../../backtest/artifact_schema.py#L1) | L | docstring (module) | HANDLES — module-level docstring declaring canonical implementation home for `b_c_extended_v1` validation | [SCHEMA_SPEC §1.1 declaration site](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |
| [`:42`](../../backtest/artifact_schema.py#L42) | C, L | declaration (canonical constant `ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 = "b_c_extended_v1"`) | HANDLES — canonical declaration site per T1.2 SEAL `12dffde` | [SCHEMA_SPEC §1.1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |
| [`:45`](../../backtest/artifact_schema.py#L45) | T3 | declaration (B-C-extended per-domain tuple opens) | HANDLES — canonical per-domain tuple declaration (CONTRACT BOUNDARY anchor row 3) | [SCHEMA_SPEC §1.2 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:46`](../../backtest/artifact_schema.py#L46) | C | declaration (tuple body — sole entry `ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1`) | HANDLES — sole-entry tuple body locks domain to b_c_extended_v1 only | [SCHEMA_SPEC §1.3 CONTRACT BOUNDARY](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:214`](../../backtest/artifact_schema.py#L214) | C | docstring (LineageContext D2-b asymmetry — refers to module-level constant `ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1` to be stamped onto future artifact JSON headers per B-C-narrow successor cycle binding) | HANDLES — documents D2-b provenance asymmetry (LineageContext does NOT carry the constant; future writer will stamp it post-B-C-narrow; T1.6 = infrastructure-only) | [SCHEMA_SPEC §1.5 producer-chain status](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.5-14-header-field-enumeration-contract-2.0.5) |
| [`:575`](../../backtest/artifact_schema.py#L575) | L | comment_reference (12-required-string-fields per Contract 2.0.5 comment block) | HANDLES — documentation of consumption-time required-string field count | [SCHEMA_SPEC §1.5b T_obs](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.5b-t_obs-required-adjacent-15th-field-per-sub-plan-seal-eve-round-1-codex-f1-medium) |
| [`:659`](../../backtest/artifact_schema.py#L659) | L | docstring (`check_b_c_extended_semantics_or_raise` body — B1-c hybrid validation order) | HANDLES — helper docstring describing Phase 1 fail-fast + Phase 2 collect-all discipline | [SCHEMA_SPEC §1.4 helper](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:664`](../../backtest/artifact_schema.py#L664) | T3 | docstring (helper — Phase 1 reject on `not in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS`) | HANDLES — documents Phase 1 structural reject path | [SCHEMA_SPEC §1.4](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:690`](../../backtest/artifact_schema.py#L690) | L | docstring CONTRACT GAP (regime_key validation deferred) | HANDLES — explicit CONTRACT GAP marker with trigger condition for successor cycle | [`backtest/artifact_schema.py:684-690` CONTRACT GAP](../../backtest/artifact_schema.py#L684-L690) |
| [`:735`](../../backtest/artifact_schema.py#L735) | T3 | helper_internal (Phase 1 missing-schema_version error message — formats `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS!r`) | HANDLES — error message lists accepted set; fail-closed on missing | [SCHEMA_SPEC §1.4 inner branch](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:738`](../../backtest/artifact_schema.py#L738) | T3 | helper_internal (Phase 1 domain-membership check `if schema_version not in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS:`) | HANDLES — load-bearing domain-fence check enforcing CONTRACT BOUNDARY at consumer side | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:739`](../../backtest/artifact_schema.py#L739) | T3 | helper_internal (formats `repr(v) for v in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` into error string) | HANDLES — emits accepted set in error message for caller diagnostics | [SCHEMA_SPEC §1.4](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:762`](../../backtest/artifact_schema.py#L762) | L | helper_internal (Phase 2 per-field missing-key error: "required for b_c_extended_v1") | HANDLES — Phase 2 collect-all per-field error message identifies schema domain | [SCHEMA_SPEC §1.6 4-step protocol](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.6-per-bar-artifact-validation-discipline-4-step-protocol-contract-2.0.5) |
| [`:804`](../../backtest/artifact_schema.py#L804) | L | helper_internal (Phase 2 T_obs missing-key error: "required for b_c_extended_v1") | HANDLES — Phase 2 T_obs missing-key error per SEAL-eve Round 1 Codex F1 MEDIUM closure | [SCHEMA_SPEC §1.5b T_obs validation](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.5b-t_obs-required-adjacent-15th-field-per-sub-plan-seal-eve-round-1-codex-f1-medium) |

**Note (§3.1 row-count reconciliation):** §2.1 table cites 15 hits for this
file (5 T3 + 3 C + 7 L). Phase 1 skeleton enumerated 14 distinct file:line
anchors; line :42 carries both C and L pattern classes (counted twice in the
§2.1 totals), accounting for the 15 vs 14 delta. All 15 pattern-class
occurrences are HANDLES-classified.

### §3.2 `backtest/wf_lineage.py` (per-domain tuple declarations + helpers + shim; 40 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:34`](../../backtest/wf_lineage.py#L34) | C, L | docstring (module — B-C-extended Scope-B additions block) | HANDLES — module-level docstring documents T1.2 additions + constant name | [SCHEMA_SPEC §1.1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |
| [`:35`](../../backtest/wf_lineage.py#L35) | T1 | docstring (module — per-domain tuple split announcement) | HANDLES — documents `ACCEPTED_EVALUATION_SCHEMA_VERSIONS` as part of split | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:36`](../../backtest/wf_lineage.py#L36) | T2, T3 | docstring (module — per-domain tuple split continuation) | HANDLES — documents `ACCEPTED_WF_SCHEMA_VERSIONS` + `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` | [SCHEMA_SPEC §1.2 rows 2+3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:47`](../../backtest/wf_lineage.py#L47) | T1 | docstring (sealed module CONTRACT BOUNDARY declaration) | HANDLES — load-bearing CONTRACT BOUNDARY: `ACCEPTED_EVALUATION_SCHEMA_VERSIONS` MUST NOT include `b_c_extended_v1` | [SCHEMA_SPEC §1.3 sealed docstring quotation](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:48`](../../backtest/wf_lineage.py#L48) | T2 | docstring (sealed module CONTRACT BOUNDARY declaration) | HANDLES — CONTRACT BOUNDARY: `ACCEPTED_WF_SCHEMA_VERSIONS` MUST NOT include `b_c_extended_v1` | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:49`](../../backtest/wf_lineage.py#L49) | T3, L | docstring (sealed module CONTRACT BOUNDARY declaration) | HANDLES — CONTRACT BOUNDARY: `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` MUST NOT include `phase2c_7_1` or `phase2c_8_1` | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:55`](../../backtest/wf_lineage.py#L55) | L | docstring (canonical documentation cross-reference to SCHEMA_SPEC) | HANDLES — points consumer readers to canonical documentation | [B_C_EXTENDED_V1_SCHEMA_SPEC.md](./B_C_EXTENDED_V1_SCHEMA_SPEC.md) |
| [`:93`](../../backtest/wf_lineage.py#L93) | C | declaration (`ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1 = "phase2c_7_1"`) | HANDLES — evaluation/WF-domain constant declaration (not B-C-extended; sibling domain) | [SCHEMA_SPEC §1.2 rows 1+2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:103`](../../backtest/wf_lineage.py#L103) | C | declaration (`ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1 = "phase2c_8_1"`) | HANDLES — evaluation/WF-domain constant declaration (sibling domain) | [SCHEMA_SPEC §1.2 rows 1+2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:111`](../../backtest/wf_lineage.py#L111) | T1 | declaration (tuple body: `ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | HANDLES — evaluation-domain tuple body entry 1 | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:112`](../../backtest/wf_lineage.py#L112) | C | declaration (tuple body: `ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1`) | HANDLES — evaluation-domain tuple body entry 2 | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:113`](../../backtest/wf_lineage.py#L113) | C | declaration (tuple body close) | HANDLES — closes evaluation tuple body | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:119`](../../backtest/wf_lineage.py#L119) | T2 | declaration (`ACCEPTED_WF_SCHEMA_VERSIONS: tuple[str, ...] = (`) | HANDLES — WF-domain tuple declaration | [SCHEMA_SPEC §1.2 row 2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:120`](../../backtest/wf_lineage.py#L120) | C | declaration (WF tuple body: `ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | HANDLES — WF-domain tuple body entry 1 | [SCHEMA_SPEC §1.2 row 2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:121`](../../backtest/wf_lineage.py#L121) | C | declaration (WF tuple body: `ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1`) | HANDLES — WF-domain tuple body entry 2 | [SCHEMA_SPEC §1.2 row 2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:124`](../../backtest/wf_lineage.py#L124) | T4 | comment_reference (legacy alias context block opens, "Backward-compat union" framing) | HANDLES — sealed comment introducing legacy alias rationale | [SCHEMA_SPEC §1.2 row 4 + §1.7](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.7-backward-compatibility-statement) |
| [`:126`](../../backtest/wf_lineage.py#L126) | T4 | comment_reference (CONTRACT GAP — consumer-migration trigger documentation) | HANDLES — CONTRACT GAP marker establishing consumer-audit trigger that this enumeration doc satisfies | [`backtest/wf_lineage.py:126-128` CONTRACT GAP authority](../../backtest/wf_lineage.py#L126-L128) |
| [`:128`](../../backtest/wf_lineage.py#L128) | T4 | comment_reference (CONTRACT GAP — audit command `rg "ACCEPTED_ARTIFACT_SCHEMA_VERSIONS"`) | HANDLES — sealed `rg` audit command literal; this doc IS the audit response | [`backtest/wf_lineage.py:126-128`](../../backtest/wf_lineage.py#L126-L128) |
| [`:129`](../../backtest/wf_lineage.py#L129) | T4 | declaration (`ACCEPTED_ARTIFACT_SCHEMA_VERSIONS: tuple[str, ...] = (`) | HANDLES — legacy alias tuple declaration (backward-compat) | [SCHEMA_SPEC §1.2 row 4](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:130`](../../backtest/wf_lineage.py#L130) | C | declaration (legacy alias body: `ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | HANDLES — legacy alias body entry 1; does NOT include `b_c_extended_v1` per CONTRACT BOUNDARY | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:131`](../../backtest/wf_lineage.py#L131) | C | declaration (legacy alias body: `ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1`) | HANDLES — legacy alias body entry 2; does NOT include `b_c_extended_v1` per CONTRACT BOUNDARY | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:166`](../../backtest/wf_lineage.py#L166) | T4 | comment_reference (PHASE2C_8.1 producer-mapping doc — refers to consumer-side `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS`) | HANDLES — documents producer-stamping vs consumer-acceptance asymmetry | [SCHEMA_SPEC §1.7](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.7-backward-compatibility-statement) |
| [`:173`](../../backtest/wf_lineage.py#L173) | C | declaration (`REGIME_KEY_TO_SCHEMA_VERSION_MAPPING` value: `ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | HANDLES — evaluation-domain producer mapping (b_c_extended_v1 NOT a producer mapping value here; correct per CONTRACT BOUNDARY) | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:174`](../../backtest/wf_lineage.py#L174) | C | declaration (`REGIME_KEY_TO_SCHEMA_VERSION_MAPPING` value: `ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | HANDLES — same as :173 | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:175`](../../backtest/wf_lineage.py#L175) | C | declaration (`REGIME_KEY_TO_SCHEMA_VERSION_MAPPING` value: `ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1`) | HANDLES — evaluation-domain producer mapping; CONTRACT BOUNDARY preserved | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:176`](../../backtest/wf_lineage.py#L176) | C | declaration (same as :175) | HANDLES — same as :175 | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:177`](../../backtest/wf_lineage.py#L177) | C | declaration (`REGIME_KEY_TO_SCHEMA_VERSION_MAPPING` value: `ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1` for `forward_2026`) | HANDLES — Phase 4 forward regime mapping; preserves CONTRACT BOUNDARY | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:276`](../../backtest/wf_lineage.py#L276) | T2 | docstring (`check_wf_semantics_or_raise` FIX-B2 docstring: "rejects any value not in `ACCEPTED_WF_SCHEMA_VERSIONS`") | HANDLES — documents WF-domain helper's domain-fence reject path | [SCHEMA_SPEC §1.4 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:302`](../../backtest/wf_lineage.py#L302) | T2 | docstring (continued — Raises clause references `ACCEPTED_WF_SCHEMA_VERSIONS`) | HANDLES — error-contract documentation | [SCHEMA_SPEC §1.4 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:330`](../../backtest/wf_lineage.py#L330) | T2 | comment_reference (FIX-B2 inner-branch intro comment) | HANDLES — documents domain-fence enforcement step at WF helper inner branch | [SCHEMA_SPEC §1.4 row 1 inner branch :322-337](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:336`](../../backtest/wf_lineage.py#L336) | T2 | helper_internal (load-bearing check: `if schema_version not in ACCEPTED_WF_SCHEMA_VERSIONS`) | HANDLES — load-bearing CONTRACT BOUNDARY enforcement: rejects `b_c_extended_v1` from WF helper | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:338`](../../backtest/wf_lineage.py#L338) | T2 | helper_internal (error string format: `ACCEPTED_WF_SCHEMA_VERSIONS`) | HANDLES — emits accepted set in error message | [SCHEMA_SPEC §1.4 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:344`](../../backtest/wf_lineage.py#L344) | L | helper_internal (error message text: "`b_c_extended_v1` artifacts must use `check_b_c_extended_semantics_or_raise`") | HANDLES — error message routes caller to correct domain helper | [SCHEMA_SPEC §1.8 domain selection](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.8-producer--consumer-responsibility-split) |
| [`:493`](../../backtest/wf_lineage.py#L493) | T1 | helper_internal (load-bearing check: `if schema_version not in ACCEPTED_EVALUATION_SCHEMA_VERSIONS`) | HANDLES — load-bearing CONTRACT BOUNDARY enforcement: rejects `b_c_extended_v1` from evaluation helper | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:495`](../../backtest/wf_lineage.py#L495) | T1 | helper_internal (error string format: `ACCEPTED_EVALUATION_SCHEMA_VERSIONS`) | HANDLES — emits accepted set in error message | [SCHEMA_SPEC §1.4 row 2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:555`](../../backtest/wf_lineage.py#L555) | C | import (re-export shim: `ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1` from `backtest.artifact_schema`) | HANDLES — public-surface shim re-export per C1-extract-pre-SEAL register 2026-05-22 | [SCHEMA_SPEC §1.1 re-export shim](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |
| [`:556`](../../backtest/wf_lineage.py#L556) | T3 | import (re-export shim: `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` from `backtest.artifact_schema`) | HANDLES — public-surface shim re-export | [SCHEMA_SPEC §1.1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |

**Note (§3.2 row-count reconciliation):** §2.1 cites 40 hits (5 T1 + 8 T2 + 3
T3 + 5 T4 + 15 C + 4 L). Phase 1 skeleton enumerated 37 distinct file:line
anchors; remaining 3 hits arise from multi-class rows (`:34` C+L, `:36` T2+T3,
`:49` T3+L). All 40 occurrences are HANDLES-classified.

### §3.3 `scripts/run_phase2c_evaluation_gate.py` (production driver; 2 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:94`](../../scripts/run_phase2c_evaluation_gate.py#L94) | C | import (`from backtest.wf_lineage import ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | HANDLES — evaluation-domain producer imports the phase2c_7_1 constant; uses evaluation-domain helpers `check_evaluation_semantics_or_raise` (imported at :100) for validation; b_c_extended_v1 is structurally excluded from this driver's domain | [SCHEMA_SPEC §1.2 row 1 + §1.8 domain selection](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.8-producer--consumer-responsibility-split) |
| [`:391`](../../scripts/run_phase2c_evaluation_gate.py#L391) | T4 | comment_reference (descriptive text inside `_lineage_metadata` docstring/comment block; mentions `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` semantically — no import or use) — **Phase 1 first-pass flag VERIFIED:** actual stamping at :402 uses `regime_key_to_schema_version()` (per-regime helper) returning `phase2c_7_1` or `phase2c_8_1`; legacy alias is NOT imported into this module (grep-verified; only `ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1` at :94 imports a schema-version symbol) | HANDLES — comment-only reference to legacy alias as descriptive shorthand; the per-regime mapping `REGIME_KEY_TO_SCHEMA_VERSION_MAPPING` is the actual consumer surface (sibling evaluation domain); no migration required because no legacy-alias *import* exists in this file | [SCHEMA_SPEC §1.7 backward compat](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.7-backward-compatibility-statement) + [`backtest/wf_lineage.py:126-128` CONTRACT GAP](../../backtest/wf_lineage.py#L126-L128) (does not apply: comment-only, no per-version branching on alias) |

### §3.4 `scripts/compare_multi_regime.py` (production driver; 2 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:62`](../../scripts/compare_multi_regime.py#L62) | C | import (`from backtest.wf_lineage import ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1`) | NO-OP — evaluation-domain comparison driver; reads only evaluation-domain artifacts (phase2c_7_1/phase2c_8_1) via `REGIME_KEY_TO_SCHEMA_VERSION_MAPPING` (imported same block); b_c_extended_v1 silently excluded — the mapping dict has no `b_c_extended_v1`-valued entries and `_resolve_regime_metadata()` raises ValueError on unknown regime_key | [SCHEMA_SPEC §1.7 backward compat](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.7-backward-compatibility-statement) — pre-split evaluation-domain consumer continues to work unmodified |
| [`:93`](../../scripts/compare_multi_regime.py#L93) | C | function_call (`schema_version == ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1` — derives `in_sample_caveat`) | NO-OP — `schema_version` here comes from `REGIME_KEY_TO_SCHEMA_VERSION_MAPPING.get(regime_key)` (line 86), which only returns phase2c_7_1 or phase2c_8_1 (never b_c_extended_v1); the equality check is purely an evaluation-domain caveat derivation; b_c_extended_v1 cannot enter this code path by construction | [SCHEMA_SPEC §1.3 CONTRACT BOUNDARY](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) — domain fence at producer mapping prevents cross-domain leak |

### §3.5 `tests/test_b_c_extended_schema.py` (T1.2 test suite; 73 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:75`](../../tests/test_b_c_extended_schema.py#L75) | L | docstring (`_valid_summary` helper docstring "Build a complete valid b_c_extended_v1 summary dict") | HANDLES — test fixture builder docstring identifies LOCKED schema version it constructs | [SCHEMA_SPEC §1.5 14 header fields](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.5-14-header-field-enumeration-contract-2.0.5) |
| [`:83`](../../tests/test_b_c_extended_schema.py#L83) | L | test_fixture (dict-value literal: `"artifact_schema_version": "b_c_extended_v1"`) | HANDLES — fixture data assigns LOCKED schema version on synthetic happy-path artifact | [SCHEMA_SPEC §1.1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |
| [`:109`](../../tests/test_b_c_extended_schema.py#L109) | C, L | test_assertion (`assert ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 == "b_c_extended_v1"`) | HANDLES — pin test on constant identity | [SCHEMA_SPEC §1.1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |
| [`:110`](../../tests/test_b_c_extended_schema.py#L110) | C | test_import (`from backtest.wf_lineage import ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1`) | HANDLES — import from shim re-export verifying public surface | [SCHEMA_SPEC §1.1 re-export shim](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |
| [`:111`](../../tests/test_b_c_extended_schema.py#L111) | C, L | test_assertion (string-literal pin on constant value) | HANDLES — pin test asserting LOCKED literal | [SCHEMA_SPEC §1.1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |
| [`:114`](../../tests/test_b_c_extended_schema.py#L114) | T3 | test_assertion (`isinstance(ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS, tuple)`) | HANDLES — type pin on B-C-extended tuple | [SCHEMA_SPEC §1.2 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:115`](../../tests/test_b_c_extended_schema.py#L115) | T3 | test_import | HANDLES — import test for B-C-extended tuple | [SCHEMA_SPEC §1.2 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:116`](../../tests/test_b_c_extended_schema.py#L116) | T3 | test_assertion (re-asserts isinstance tuple) | HANDLES — pin tuple type | [SCHEMA_SPEC §1.2 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:118`](../../tests/test_b_c_extended_schema.py#L118) | L | docstring (`test_b_c_extended_v1_in_accepted_b_c_extended_tuple` docstring) | HANDLES — test docstring identifies LOCKED relationship | [SCHEMA_SPEC §1.2 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:119`](../../tests/test_b_c_extended_schema.py#L119) | T3, L | test_import (paired symbols) | HANDLES — import test | [SCHEMA_SPEC §1.2 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:121`](../../tests/test_b_c_extended_schema.py#L121) | T3 | test_import (second symbol of paired import) | HANDLES — import test | [SCHEMA_SPEC §1.2 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:122`](../../tests/test_b_c_extended_schema.py#L122) | C | test_import (paired constant) | HANDLES — import test | [SCHEMA_SPEC §1.1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |
| [`:124`](../../tests/test_b_c_extended_schema.py#L124) | T3, C | test_assertion (`assert ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS`) | HANDLES — pin test verifying constant is in per-domain tuple | [SCHEMA_SPEC §1.2 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:127-156`](../../tests/test_b_c_extended_schema.py#L127-L156) | T1 (×10), T2 (×6), C (×3), L (×4) | test_assertion block (CONTRACT BOUNDARY enforcement tests — `assert ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 not in ACCEPTED_EVALUATION_SCHEMA_VERSIONS` + `... not in ACCEPTED_WF_SCHEMA_VERSIONS`) | HANDLES (block, uniform) — load-bearing CONTRACT BOUNDARY pin tests + happy-path domain membership pins; would FAIL if any cross-domain tuple pollution introduced | [SCHEMA_SPEC §1.3 CONTRACT BOUNDARY](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:159`](../../tests/test_b_c_extended_schema.py#L159) | T2, L | docstring + test_assertion (WF domain-fence excludes b_c_extended_v1) | HANDLES — CONTRACT BOUNDARY pin (WF) | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:162`](../../tests/test_b_c_extended_schema.py#L162) | L | docstring (mentions b_c_extended_v1 in test description) | HANDLES — test docstring identifies CONTRACT BOUNDARY assertion target | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:165`](../../tests/test_b_c_extended_schema.py#L165) | T2 | test_import (`ACCEPTED_WF_SCHEMA_VERSIONS`) | HANDLES — import test | [SCHEMA_SPEC §1.2 row 2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:166`](../../tests/test_b_c_extended_schema.py#L166) | C | test_import (`ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1` paired) | HANDLES — import test | [SCHEMA_SPEC §1.1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |
| [`:168`](../../tests/test_b_c_extended_schema.py#L168) | T2, C | test_assertion (`assert ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 not in ACCEPTED_WF_SCHEMA_VERSIONS`) | HANDLES — CONTRACT BOUNDARY pin (WF) | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:777-828`](../../tests/test_b_c_extended_schema.py#L777-L828) | L (×11) | test_fixture + test_assertion block (happy-path + per-field validation tests; all reference `"b_c_extended_v1"` literal in synthetic summary dicts) | HANDLES (block, uniform) — exercises `check_b_c_extended_semantics_or_raise()` against valid + invalid `b_c_extended_v1` artifacts | [SCHEMA_SPEC §1.4 row 3 + §1.6 4-step protocol](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.6-per-bar-artifact-validation-discipline-4-step-protocol-contract-2.0.5) |
| [`:786`](../../tests/test_b_c_extended_schema.py#L786) | T1 | test_assertion (within :777-828 block — paired domain-fence assertion) | HANDLES — within validation block; CONTRACT BOUNDARY check | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:803`](../../tests/test_b_c_extended_schema.py#L803) | T1 | test_assertion (within :777-828 block — paired domain-fence assertion) | HANDLES — within validation block; CONTRACT BOUNDARY check | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:1243-1334`](../../tests/test_b_c_extended_schema.py#L1243-L1334) | T2 (×6), L (×9) | test_fixture + test_assertion block (cross-domain rejection tests — feeds `b_c_extended_v1` summary to WF helper, asserts ValueError; feeds phase2c_7_1/phase2c_8_1 summary to B-C-extended helper, asserts ValueError) | HANDLES (block, uniform) — load-bearing CONTRACT BOUNDARY runtime enforcement tests at all 3 helpers | [SCHEMA_SPEC §1.3 + §1.4](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |

**Block-level reasoning (§3.5):** test_b_c_extended_schema.py is the T1.2 SEAL
test suite sealed at `12dffde`. The 3 block rows (:127-156, :777-828,
:1243-1334) test CONTRACT BOUNDARY enforcement at both constant-level (the
tuples themselves) and helper-level (cross-domain rejection at runtime). All
block rows uniformly HANDLES — they are LOAD-BEARING tests that would fail
closed if any cross-domain tuple pollution or helper acceptance drift
occurred. All 73 hits across this file classify as HANDLES.

### §3.6 `tests/test_wf_lineage_guard.py` (T1.2 wf_lineage test suite; 33 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:326`](../../tests/test_wf_lineage_guard.py#L326) | C | test_import (`ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | HANDLES — evaluation-domain test_import; no b_c_extended_v1 interaction here | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:342`](../../tests/test_wf_lineage_guard.py#L342) | C | test_fixture (assigns `artifact_schema_version: ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | HANDLES — evaluation-domain test fixture | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:473`](../../tests/test_wf_lineage_guard.py#L473) | T4 | comment_reference (docstring mentioning `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` semantics in defensive-reject context) | HANDLES — legacy alias appears in test docstring describing defensive reject; no actual import | [SCHEMA_SPEC §1.7](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.7-backward-compatibility-statement) |
| [`:519`](../../tests/test_wf_lineage_guard.py#L519) | C | test_import (`ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1`) | HANDLES — evaluation-domain test_import | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:520`](../../tests/test_wf_lineage_guard.py#L520) | T4 | test_import (`ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` legacy alias) | HANDLES — legacy alias test_import; preserves backward-compat surface per §1.7 | [SCHEMA_SPEC §1.2 row 4 + §1.7](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.7-backward-compatibility-statement) |
| [`:535`](../../tests/test_wf_lineage_guard.py#L535) | C | test_fixture (`artifact_schema_version: ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1`) | HANDLES — evaluation-domain test fixture | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:542`](../../tests/test_wf_lineage_guard.py#L542) | T4 | docstring (test_accepted_schema_versions_tuple_contains_both_arcs) | HANDLES — test docstring for legacy alias contract | [SCHEMA_SPEC §1.2 row 4](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:549`](../../tests/test_wf_lineage_guard.py#L549) | T4, C | test_assertion (`assert ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1 in ACCEPTED_ARTIFACT_SCHEMA_VERSIONS`) | HANDLES — pin test on legacy alias contents | [SCHEMA_SPEC §1.2 row 4](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:550`](../../tests/test_wf_lineage_guard.py#L550) | T4, C | test_assertion (`assert ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1 in ACCEPTED_ARTIFACT_SCHEMA_VERSIONS`) | HANDLES — pin test on legacy alias contents | [SCHEMA_SPEC §1.2 row 4](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:551`](../../tests/test_wf_lineage_guard.py#L551) | C | test_assertion (`assert ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1 == "phase2c_8_1"`) | HANDLES — pin test on phase2c_8_1 literal | [SCHEMA_SPEC §1.2 row 4](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:689`](../../tests/test_wf_lineage_guard.py#L689) | C | test_assertion (REGIME_KEY_TO_SCHEMA_VERSION_MAPPING value pin) | HANDLES — evaluation-domain producer mapping pin | [SCHEMA_SPEC §1.2 rows 1+2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:693`](../../tests/test_wf_lineage_guard.py#L693) | C | test_assertion (REGIME_KEY_TO_SCHEMA_VERSION_MAPPING value pin) | HANDLES — same | [SCHEMA_SPEC §1.2 rows 1+2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:703`](../../tests/test_wf_lineage_guard.py#L703) | C | test_assertion (REGIME_KEY_TO_SCHEMA_VERSION_MAPPING value pin) | HANDLES — same | [SCHEMA_SPEC §1.2 rows 1+2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:709`](../../tests/test_wf_lineage_guard.py#L709) | C | test_assertion (REGIME_KEY_TO_SCHEMA_VERSION_MAPPING value pin) | HANDLES — same | [SCHEMA_SPEC §1.2 rows 1+2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:717`](../../tests/test_wf_lineage_guard.py#L717) | C | test_assertion (regime_key_to_schema_version helper pin) | HANDLES — producer-helper pin test | [SCHEMA_SPEC §1.2 rows 1+2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:721`](../../tests/test_wf_lineage_guard.py#L721) | C | test_assertion (regime_key_to_schema_version helper pin) | HANDLES — same | [SCHEMA_SPEC §1.2 rows 1+2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:729`](../../tests/test_wf_lineage_guard.py#L729) | C | test_assertion (regime_key_to_schema_version helper pin) | HANDLES — same | [SCHEMA_SPEC §1.2 rows 1+2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:733`](../../tests/test_wf_lineage_guard.py#L733) | C | test_assertion (regime_key_to_schema_version helper pin) | HANDLES — same | [SCHEMA_SPEC §1.2 rows 1+2](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:760`](../../tests/test_wf_lineage_guard.py#L760) | T2 | comment_reference (test section header for FIX-B2 WF domain fence — `ACCEPTED_WF_SCHEMA_VERSIONS`) | HANDLES — section divider documenting WF domain-fence test region | [SCHEMA_SPEC §1.3 + §1.4 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:762`](../../tests/test_wf_lineage_guard.py#L762) | T2 | comment_reference (FIX-B2 description) | HANDLES — comment documenting WF domain-fence requirement | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:763`](../../tests/test_wf_lineage_guard.py#L763) | L | comment_reference (FIX-B2 description: "must reject b_c_extended_v1 and accept only its own domain's tuple") | HANDLES — documents FIX-B2 CONTRACT BOUNDARY enforcement requirement | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:766`](../../tests/test_wf_lineage_guard.py#L766) | L | docstring (`test_wf_helper_rejects_b_c_extended_v1_when_wf_fields_also_present` test docstring) | HANDLES — docstring identifies CONTRACT BOUNDARY enforcement target | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:767`](../../tests/test_wf_lineage_guard.py#L767) | L | docstring (continuation; "check_wf_semantics_or_raise must reject b_c_extended_v1") | HANDLES — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:769`](../../tests/test_wf_lineage_guard.py#L769) | T2 | docstring (mentions `ACCEPTED_WF_SCHEMA_VERSIONS`) | HANDLES — docstring describes expected post-fix behavior | [SCHEMA_SPEC §1.4 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:770`](../../tests/test_wf_lineage_guard.py#L770) | L | docstring (continuation; b_c_extended_v1) | HANDLES — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:772`](../../tests/test_wf_lineage_guard.py#L772) | L | docstring (continuation; "artifact_schema_version='b_c_extended_v1' must be rejected") | HANDLES — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:783`](../../tests/test_wf_lineage_guard.py#L783) | L | test_fixture (`"artifact_schema_version": "b_c_extended_v1"` in summary dict to be rejected) | HANDLES — synthetic b_c_extended_v1 input fed to WF helper to verify reject | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:788`](../../tests/test_wf_lineage_guard.py#L788) | L | test_assertion (`assert "b_c_extended_v1" in msg or "artifact_schema_version" in msg`) | HANDLES — load-bearing assertion that the WF helper's rejection error message contains the rejected schema version literal | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:795`](../../tests/test_wf_lineage_guard.py#L795) | T2 | docstring (regression guard mentions `ACCEPTED_WF_SCHEMA_VERSIONS`) | HANDLES — regression test docstring | [SCHEMA_SPEC §1.4 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:813`](../../tests/test_wf_lineage_guard.py#L813) | T2 | docstring (regression guard mentions `ACCEPTED_WF_SCHEMA_VERSIONS`) | HANDLES — same | [SCHEMA_SPEC §1.4 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |
| [`:850`](../../tests/test_wf_lineage_guard.py#L850) | T2 | docstring (defensive-reject test mentions `ACCEPTED_WF_SCHEMA_VERSIONS`) | HANDLES — defensive-reject test docstring | [SCHEMA_SPEC §1.4 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) |

**Note (§3.6):** All 33 hits classify as HANDLES. The FIX-B2 test block
(:760-790) is load-bearing CONTRACT BOUNDARY runtime enforcement — verifies
WF helper rejects `b_c_extended_v1` when synthesized in a summary dict.
Legacy alias test_imports (e.g., :520) preserve backward-compat surface
without expanding the consumer surface.

### §3.7 `tests/test_t1_4_backward_compat.py` (T1.4 backward-compat suite; 11 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:18`](../../tests/test_t1_4_backward_compat.py#L18) | L | docstring (module — A2-α LOCK keyword class table includes `b_c_extended_v1`) | HANDLES — module docstring documents A2-α LOCK 3-keyword-class discipline; b_c_extended_v1 is pre-committed keyword for error-message regression discipline | [SCHEMA_SPEC §1.3 + §1.4 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.4-three-distinct-validation-branch-helpers) + T1.4 SEAL commit `5a44ec6` |
| [`:228`](../../tests/test_t1_4_backward_compat.py#L228) | L | docstring (`TestT1_4_A2_DomainFenceRejection` class docstring; "checks `check_b_c_extended_semantics_or_raise` rejects legacy artifact with ValueError") | HANDLES — A2-α LOCK domain-fence test class documentation | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:237`](../../tests/test_t1_4_backward_compat.py#L237) | T3 | test_import (`from backtest.artifact_schema import ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS`) | HANDLES — imports per-domain tuple to verify precondition that legacy artifact does NOT have b_c_extended_v1 schema | [SCHEMA_SPEC §1.2 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:238`](../../tests/test_t1_4_backward_compat.py#L238) | T3 | test_assertion (`assert summary["artifact_schema_version"] not in ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS`) | HANDLES — precondition assertion: legacy artifact schema version is NOT b_c_extended_v1 | [SCHEMA_SPEC §1.2 row 3 + §1.7](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.7-backward-compatibility-statement) |
| [`:239`](../../tests/test_t1_4_backward_compat.py#L239) | T3 | test_assertion (continuation — error message format string references `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS={...}`) | HANDLES — same precondition emit context | [SCHEMA_SPEC §1.2 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:242`](../../tests/test_t1_4_backward_compat.py#L242) | T3 | test_assertion (continuation — `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS={ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS}` in error string) | HANDLES — same | [SCHEMA_SPEC §1.2 row 3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:243`](../../tests/test_t1_4_backward_compat.py#L243) | L | test_assertion (continuation — "A2 test requires legacy-domain artifact (not b_c_extended_v1)") | HANDLES — error message text identifies the precondition class | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:284`](../../tests/test_t1_4_backward_compat.py#L284) | L | docstring (`test_message_contains_b_c_extended_v1_keyword` test docstring) | HANDLES — A2-α LOCK keyword class 2 test docstring | [SCHEMA_SPEC §1.3 + A2-α LOCK at T1.4 SEAL `5a44ec6`](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:285`](../../tests/test_t1_4_backward_compat.py#L285) | L | docstring (continuation — A2-α LOCK keyword class 2 description) | HANDLES — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:296`](../../tests/test_t1_4_backward_compat.py#L296) | L | test_assertion (`assert "b_c_extended_v1" in str(exc_info.value)`) | HANDLES — load-bearing A2-α LOCK keyword class 2 assertion; verifies error message contains accepted-value keyword | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:297`](../../tests/test_t1_4_backward_compat.py#L297) | L | test_assertion (continuation — error string format `f"Keyword class 2 ('b_c_extended_v1') missing..."`) | HANDLES — error message context for A2-α LOCK | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |

**Note (§3.7):** All 11 hits classify as HANDLES. The TestT1_4_A2_DomainFenceRejection
class is the T1.4 SEAL load-bearing test asserting B-C-extended helper
rejects legacy (phase2c_*) artifacts via plain ValueError with 3
pre-committed keyword classes including the b_c_extended_v1 literal.

### §3.8 `tests/test_phase2c_evaluation_gate_runner.py` (evaluation-gate runner test; 11 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:33`](../../tests/test_phase2c_evaluation_gate_runner.py#L33) | C | test_import (`ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | NO-OP — evaluation-domain runner test; imports phase2c_7_1 constant for evaluation-domain producer-stamping verification; b_c_extended_v1 structurally not in this domain | [SCHEMA_SPEC §1.2 row 1 + §1.8](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.8-producer--consumer-responsibility-split) |
| [`:34`](../../tests/test_phase2c_evaluation_gate_runner.py#L34) | C | test_import (`ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1`) | NO-OP — same; phase2c_8_1 constant for evaluation domain | [SCHEMA_SPEC §1.2 row 1 + §1.8](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.8-producer--consumer-responsibility-split) |
| [`:452`](../../tests/test_phase2c_evaluation_gate_runner.py#L452) | C | test_assertion (`meta["artifact_schema_version"] == (ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1)`) | NO-OP — pins runner `_lineage_metadata` to stamp evaluation-domain discriminator (phase2c_7_1) for v2.regime_holdout regime; b_c_extended_v1 not in producer-mapping | [SCHEMA_SPEC §1.3 producer mapping](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:472`](../../tests/test_phase2c_evaluation_gate_runner.py#L472) | C | test_assertion (same pattern for v2.validation regime) | NO-OP — same; evaluation-domain producer pinning | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:496`](../../tests/test_phase2c_evaluation_gate_runner.py#L496) | C | test_assertion (eval_2020_v1 → phase2c_8_1) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:516`](../../tests/test_phase2c_evaluation_gate_runner.py#L516) | C | test_assertion (eval_2021_v1 → phase2c_8_1) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:538`](../../tests/test_phase2c_evaluation_gate_runner.py#L538) | C | test_assertion (mixed-discriminator independence test — phase2c_7_1) | NO-OP — same; evaluation-domain | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:541`](../../tests/test_phase2c_evaluation_gate_runner.py#L541) | C | test_assertion (mixed-discriminator continuation — phase2c_8_1) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:581`](../../tests/test_phase2c_evaluation_gate_runner.py#L581) | C | test_assertion (per-candidate stamping pin) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:635`](../../tests/test_phase2c_evaluation_gate_runner.py#L635) | C | test_assertion (validation regime per-candidate pin) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:688`](../../tests/test_phase2c_evaluation_gate_runner.py#L688) | C | test_assertion (aggregate artifact stamps phase2c_7_1) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |

**Note (§3.8):** All 11 hits classify as NO-OP. This is the evaluation-gate
runner test suite for `scripts/run_phase2c_evaluation_gate.py`. All hits
exercise the evaluation-domain producer-stamping path
(`regime_key_to_schema_version()` returns phase2c_7_1 or phase2c_8_1 per
domain mapping). The b_c_extended_v1 schema version is structurally not in
this evaluation-domain producer's mapping, so it cannot be stamped here per
CONTRACT BOUNDARY. NO-OP framing chosen over HANDLES because the consumer is
on the sibling-domain (evaluation) producer path — b_c_extended_v1 simply
does not cross this surface; the test would PASS unchanged if b_c_extended_v1
were added to the producer mapping for an unrelated reason because the
existing assertions are pin-tests on phase2c_7_1/phase2c_8_1 values only.

### §3.9 `tests/test_compare_multi_regime.py` (8 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:38`](../../tests/test_compare_multi_regime.py#L38) | C | test_import (`ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | NO-OP — comparison-driver test for evaluation-domain artifacts; phase2c_7_1 constant for sibling-domain pin tests | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:39`](../../tests/test_compare_multi_regime.py#L39) | C | test_import (`ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1`) | NO-OP — same | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:94`](../../tests/test_compare_multi_regime.py#L94) | C | test_assertion (`meta["schema_version"] == ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | NO-OP — evaluation-domain regime-metadata resolution pin (v2.regime_holdout → phase2c_7_1); b_c_extended_v1 not in mapping | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:100`](../../tests/test_compare_multi_regime.py#L100) | C | test_assertion (v2.validation → phase2c_7_1) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:108`](../../tests/test_compare_multi_regime.py#L108) | C | test_assertion (eval_2020_v1 → phase2c_8_1) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:116`](../../tests/test_compare_multi_regime.py#L116) | C | test_assertion (eval_2021_v1 → phase2c_8_1) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:449`](../../tests/test_compare_multi_regime.py#L449) | C | test_assertion (compare-row-construction pin) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:450`](../../tests/test_compare_multi_regime.py#L450) | C | test_assertion (compare-row-construction pin) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |

**Note (§3.9):** All 8 hits classify as NO-OP for the same reason as §3.8 —
sibling evaluation-domain test surface; b_c_extended_v1 is not in the
producer mapping consumed by `scripts/compare_multi_regime.py`.

### §3.10 `tests/test_t1_1_sys_fix.py` (T1.1 SYS-fix-1 + SYS5 invariant test; 4 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:1375`](../../tests/test_t1_1_sys_fix.py#L1375) | C | docstring (`test_artifact_schema_version_constant_still_exported` test docstring) | HANDLES — pin test asserting D2-b provenance asymmetry: `ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1` constant remains exported separately from `LineageContext` fields | [SCHEMA_SPEC §1.1 + §1.5 producer-side](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.5-14-header-field-enumeration-contract-2.0.5) |
| [`:1376`](../../tests/test_t1_1_sys_fix.py#L1376) | C | test_import (`from backtest.artifact_schema import ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1`) | HANDLES — verifies canonical-module export of constant | [SCHEMA_SPEC §1.1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |
| [`:1378`](../../tests/test_t1_1_sys_fix.py#L1378) | C, L | test_assertion (`assert ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 == "b_c_extended_v1"`) | HANDLES — pin test on LOCKED constant value | [SCHEMA_SPEC §1.1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.1-schema-version-identifier) |

**Note (§3.10 row-count reconciliation):** §2.1 cites 4 hits (3 C + 1 L).
Phase 1 skeleton enumerated 3 distinct file:line anchors; the 4th hit comes
from line :1378 carrying both C and L pattern classes. All 4 hits classify
as HANDLES.

### §3.11 `tests/test_filter_evaluation_gate.py` (4 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:32`](../../tests/test_filter_evaluation_gate.py#L32) | C | test_import (`ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | NO-OP — evaluation-domain filter test; phase2c_7_1 for sibling-domain pin tests; b_c_extended_v1 structurally not in this domain | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:81`](../../tests/test_filter_evaluation_gate.py#L81) | C | test_fixture (`"artifact_schema_version": ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | NO-OP — evaluation-domain test fixture | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:184`](../../tests/test_filter_evaluation_gate.py#L184) | C | test_fixture (evaluation-domain artifact_schema_version assignment) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:372`](../../tests/test_filter_evaluation_gate.py#L372) | C | test_fixture (evaluation-domain artifact_schema_version assignment) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |

**Note (§3.11):** All 4 hits classify as NO-OP — evaluation-domain filter
script test surface; b_c_extended_v1 not in scope.

### §3.12 `tests/test_compare_2022_vs_2024.py` (4 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:43`](../../tests/test_compare_2022_vs_2024.py#L43) | C | test_import (`ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | NO-OP — multi-regime comparison test variant for sibling evaluation domain; b_c_extended_v1 not in scope | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:179`](../../tests/test_compare_2022_vs_2024.py#L179) | C | test_fixture (evaluation-domain artifact_schema_version assignment) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:189`](../../tests/test_compare_2022_vs_2024.py#L189) | C | test_fixture (same) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |
| [`:378`](../../tests/test_compare_2022_vs_2024.py#L378) | C | test_fixture / test_assertion (same) | NO-OP — same | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |

**Note (§3.12):** All 4 hits classify as NO-OP for the same reason as §3.11.

### §3.13 `tests/test_t1_1_artifact_writer.py` (T1.1 writer chain test; 3 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:931`](../../tests/test_t1_1_artifact_writer.py#L931) | L | comment_reference ("Build the summary dict matching b_c_extended_v1 schema") | HANDLES — inline comment identifying schema target | [SCHEMA_SPEC §1.5 14 header fields](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.5-14-header-field-enumeration-contract-2.0.5) |
| [`:933`](../../tests/test_t1_1_artifact_writer.py#L933) | L | test_fixture (`"artifact_schema_version": "b_c_extended_v1"`) | HANDLES — end-to-end producer chain validator test (writer → summary → `check_b_c_extended_semantics_or_raise`) | [SCHEMA_SPEC §1.4 row 3 + §1.6 4-step protocol](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.6-per-bar-artifact-validation-discipline-4-step-protocol-contract-2.0.5) |
| [`:1127`](../../tests/test_t1_1_artifact_writer.py#L1127) | L | test_fixture (`"artifact_schema_version": "b_c_extended_v1"` in second test) | HANDLES — second producer-chain test path; LineageContext + writer + validator integration | [SCHEMA_SPEC §1.8 producer + consumer](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.8-producer--consumer-responsibility-split) |

**Note (§3.13):** All 3 hits classify as HANDLES — T1.1 producer-chain
end-to-end tests verifying writer + LineageContext + `check_b_c_extended_semantics_or_raise`
integration on the LOCKED schema version.

### §3.14 `tests/test_phase4_regime_config.py` (Phase 4 regime config; 2 hits)

| file:line | Pattern class | Reference type (verified) | Disposition | Cross-reference |
|---|---|---|---|---|
| [`:19`](../../tests/test_phase4_regime_config.py#L19) | C | test_import (`ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | NO-OP — Phase 4 forward-regime config test for evaluation-domain producer mapping (forward_2026 → phase2c_7_1); b_c_extended_v1 not in scope | [SCHEMA_SPEC §1.2 row 1](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.2-per-domain-tuple-architecture-t1.2-sub-decision-a-lock-sealed-at-12dffde) |
| [`:78`](../../tests/test_phase4_regime_config.py#L78) | C | test_assertion (`assert schema == ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`) | NO-OP — pin test on forward_2026 regime → phase2c_7_1 mapping (fully-out-of-sample register parallel to bear_2022 + validation_2024); evaluation-domain | [SCHEMA_SPEC §1.3](./B_C_EXTENDED_V1_SCHEMA_SPEC.md#§1.3-contract-boundary-no-cross-domain-tuple-pollution) |

**Note (§3.14):** All 2 hits classify as NO-OP — Phase 4 evaluation-domain
forward-regime configuration test; b_c_extended_v1 not in this evaluation
domain's producer mapping.

### §3.15 Phase 2 disposition summary (§2.7.2 item 6)

Per sub-plan §2.7.3 Phase 3 obligation: orchestrator computes per-class
totals after Phase 2 subagent classification completes.

**Per-file totals (matching §2.1 row order; 212-hit denominator):**

| File | T1 | T2 | T3 | T4 | C | L | Total | HANDLES | NO-OP | NEEDS-EXTENSION |
|------|----|----|----|----|---|---|-------|---------|-------|------------------|
| `backtest/wf_lineage.py` | 5 | 8 | 3 | 5 | 15 | 4 | **40** | 40 | 0 | 0 |
| `backtest/artifact_schema.py` | 0 | 0 | 5 | 0 | 3 | 7 | **15** | 15 | 0 | 0 |
| `scripts/run_phase2c_evaluation_gate.py` | 0 | 0 | 0 | 1 | 1 | 0 | **2** | 2 | 0 | 0 |
| `scripts/compare_multi_regime.py` | 0 | 0 | 0 | 0 | 2 | 0 | **2** | 0 | 2 | 0 |
| `tests/test_b_c_extended_schema.py` | 12 | 12 | 6 | 0 | 13 | 30 | **73** | 73 | 0 | 0 |
| `tests/test_wf_lineage_guard.py` | 0 | 6 | 0 | 5 | 15 | 7 | **33** | 33 | 0 | 0 |
| `tests/test_t1_4_backward_compat.py` | 0 | 0 | 4 | 0 | 0 | 7 | **11** | 11 | 0 | 0 |
| `tests/test_phase2c_evaluation_gate_runner.py` | 0 | 0 | 0 | 0 | 11 | 0 | **11** | 0 | 11 | 0 |
| `tests/test_compare_multi_regime.py` | 0 | 0 | 0 | 0 | 8 | 0 | **8** | 0 | 8 | 0 |
| `tests/test_t1_1_sys_fix.py` | 0 | 0 | 0 | 0 | 3 | 1 | **4** | 4 | 0 | 0 |
| `tests/test_filter_evaluation_gate.py` | 0 | 0 | 0 | 0 | 4 | 0 | **4** | 0 | 4 | 0 |
| `tests/test_compare_2022_vs_2024.py` | 0 | 0 | 0 | 0 | 4 | 0 | **4** | 0 | 4 | 0 |
| `tests/test_t1_1_artifact_writer.py` | 0 | 0 | 0 | 0 | 0 | 3 | **3** | 3 | 0 | 0 |
| `tests/test_phase4_regime_config.py` | 0 | 0 | 0 | 0 | 2 | 0 | **2** | 0 | 2 | 0 |
| **Total** | **17** | **26** | **18** | **11** | **81** | **59** | **212** | **181** | **31** | **0** |

**Aggregate disposition counts (per sub-plan §2.7.3):**

- **Total N rows audited: 212** (across 14 files)
- **HANDLES: 181** (~85.4%)
- **NO-OP: 31** (~14.6%)
- **NEEDS-EXTENSION: 0** (0.0%)

**Per-disposition breakdown:**

- **HANDLES (181)** — splits as:
  - Production code declarations + helpers + shim (`backtest/wf_lineage.py`
    40 + `backtest/artifact_schema.py` 15 + `scripts/run_phase2c_evaluation_gate.py`
    2 = 57 production-code hits handled via per-domain helper
    `check_b_c_extended_semantics_or_raise()` or via canonical declaration /
    sealed CONTRACT BOUNDARY enforcement)
  - T1.2 SEAL test suite (`tests/test_b_c_extended_schema.py` 73 +
    `tests/test_wf_lineage_guard.py` 33 = 106 test-assertion hits verifying
    CONTRACT BOUNDARY enforcement at both constant-level and helper-level)
  - T1.4 SEAL backward-compat suite (`tests/test_t1_4_backward_compat.py` 11
    test-assertion hits verifying A2-α LOCK domain-fence rejection with 3
    pre-committed keyword classes)
  - T1.1 producer-chain integration (`tests/test_t1_1_artifact_writer.py` 3 +
    `tests/test_t1_1_sys_fix.py` 4 = 7 end-to-end producer/validator pin tests)

- **NO-OP (31)** — splits as:
  - Sibling evaluation-domain test surfaces (`tests/test_phase2c_evaluation_gate_runner.py`
    11 + `tests/test_compare_multi_regime.py` 8 +
    `tests/test_filter_evaluation_gate.py` 4 +
    `tests/test_compare_2022_vs_2024.py` 4 +
    `tests/test_phase4_regime_config.py` 2 = 29 test hits on the
    evaluation-domain producer mapping `REGIME_KEY_TO_SCHEMA_VERSION_MAPPING`
    which structurally cannot return `b_c_extended_v1`)
  - Sibling evaluation-domain comparison driver (`scripts/compare_multi_regime.py`
    2 production hits; same reason — uses evaluation-domain mapping)
  - **Rationale:** all 31 NO-OP hits are on the sibling evaluation
    attestation domain (phase2c_7_1 / phase2c_8_1). The B-C-extended schema
    (`b_c_extended_v1`) is structurally not in the evaluation-domain
    producer mapping (`REGIME_KEY_TO_SCHEMA_VERSION_MAPPING` at
    `backtest/wf_lineage.py:172-178`) by CONTRACT BOUNDARY (§1.3 of the
    schema spec); b_c_extended_v1 cannot enter these code paths.

- **NEEDS-EXTENSION (0)** — zero rows require code changes to handle
  `b_c_extended_v1`. The CONTRACT BOUNDARY architecture sealed at T1.2
  (`12dffde`) + the T1.1/T1.4/T1.5 test suite cohort + the new B-C-extended
  per-domain helper `check_b_c_extended_semantics_or_raise()` (canonical at
  `backtest/artifact_schema.py:654` + shim re-export at
  `backtest/wf_lineage.py:559`) collectively provide load-bearing producer
  and consumer coverage. The legacy alias `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS`
  preserves backward-compat for pre-split consumers without requiring
  migration. The Phase 1 first-pass flag at
  `scripts/run_phase2c_evaluation_gate.py:391` was VERIFIED as a
  comment-only reference (no import or per-version branching on the legacy
  alias), so the CONTRACT GAP migration trigger at
  `backtest/wf_lineage.py:126-128` is not triggered by this consumer.

**Mode A confidence flags:** all 212 row classifications are defensible from
the ±20-line context read against the cited consumer file:line. No rows
flagged as low-confidence at Phase 2 close.

**Per anti-pre-emption discipline (§4 + v1 PFR Codex F2):** zero
NEEDS-EXTENSION rows means no successor cycle eligible-not-named is
registered for §2.7 deliverable `(g)` at this T1.6 sub-cycle close. Any
future schema-version extension that surfaces new consumer-audit obligations
follows the SCHEMA_VERSION_EXTENSION_PROTOCOL.md §2.7 consumer-audit
obligation per CONTRACT GAP at `backtest/wf_lineage.py:126-128`.

---

## §4 NEEDS-EXTENSION row handling (anti-pre-emption discipline)

Per sub-plan §2.7.3 + v1 PFR Codex F2 anti-pre-emption fix:

- Any row Phase 2 classifies as **NEEDS-EXTENSION** must be documented as
  "deferred to successor cycle eligible-not-named per anti-pre-emption."
- Specify exact change required + cross-reference to relevant Contract.
- **NO in-cycle scope expansion path offered.** If NEEDS-EXTENSION work
  is required, fresh Charlie register-event for separate successor cycle
  is required.
- T1.6 sub-plan does NOT pre-offer Path A → Path A+ in-cycle expansion.

**Phase 1 first-pass flag (Phase 2 VERIFIED):**
- [`scripts/run_phase2c_evaluation_gate.py:391`](../../scripts/run_phase2c_evaluation_gate.py#L391)
  was flagged by Phase 1 as candidate legacy-alias consumer.
  **Phase 2 verdict: HANDLES (NO migration required).** Mode A grep
  re-verification confirms `:391` is a comment-only reference within the
  `_lineage_metadata()` docstring/comment block; the file does NOT
  import `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` (the only schema-version
  symbol imported at `:94` is `ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1`); the
  actual stamping at `:402` derives the discriminator via
  `regime_key_to_schema_version()` (per-regime helper returning
  phase2c_7_1 or phase2c_8_1 per `REGIME_KEY_TO_SCHEMA_VERSION_MAPPING`).
  The CONTRACT GAP migration trigger at
  [`backtest/wf_lineage.py:126-128`](../../backtest/wf_lineage.py#L126-L128)
  applies to "consumers that import the legacy alias AND perform per-version
  branching"; neither condition holds at `:391`. No NEEDS-EXTENSION action
  required.

---

## §5 Phase 2 subagent dispatch brief skeleton (orchestrator pre-draft)

When Charlie authorizes Phase 2 subagent dispatch for §2.7 per anti-pre-emption,
the brief should include:

1. **Subagent type:** `general-purpose` (DS3 lean per v1 PFR Advisor F6;
   NOT `quant-research-advisor` to avoid category violation + §6.4
   cross-leg overlap)
2. **Input:** this skeleton doc + sealed implementation files +
   B_C_EXTENDED_V1_SCHEMA_SPEC.md + SCHEMA_VERSION_EXTENSION_PROTOCOL.md
3. **Per-hit task:** read ±20-line context around each cited file:line;
   classify Disposition (HANDLES / NO-OP / NEEDS-EXTENSION) + Cross-reference
4. **NEEDS-EXTENSION discipline:** firmly defer to successor cycle
   eligible-not-named per anti-pre-emption; NO in-cycle scope expansion
5. **Mode A spot-verification (orchestrator post-return):** 5-10 representative
   rows independently verified by orchestrator Read on cited consumer

---

## §6 Cross-references

- [B_C_EXTENDED_V1_SCHEMA_SPEC.md](./B_C_EXTENDED_V1_SCHEMA_SPEC.md) —
  full schema spec; §1.2 per-domain tuple architecture is the audit anchor
- [SCHEMA_VERSION_EXTENSION_PROTOCOL.md](./SCHEMA_VERSION_EXTENSION_PROTOCOL.md) —
  extension protocol governing future schema additions; §2.7 consumer
  audit obligation per CONTRACT GAP at `wf_lineage.py:126-128`
- [WF_TEST_BOUNDARY_SEMANTICS.md](./WF_TEST_BOUNDARY_SEMANTICS.md) — WF +
  evaluation domain semantics (pre-extension architecture)
- [`docs/superpowers/plans/2026-05-24-t1_6-documentation-consumer-enumeration-cycle-execution-plan.md`](../superpowers/plans/2026-05-24-t1_6-documentation-consumer-enumeration-cycle-execution-plan.md)
  §2.7 — sub-plan source

**Sealed CONTRACT GAP authorities (forward triggers):**

- [`backtest/wf_lineage.py:117-118`](../../backtest/wf_lineage.py#L117-L118)
  — WF-specific schema version extension trigger
- [`backtest/wf_lineage.py:126-128`](../../backtest/wf_lineage.py#L126-L128)
  — consumer audit trigger (this doc's audit charter)
- [`backtest/wf_lineage.py:281`](../../backtest/wf_lineage.py#L281) —
  regime_key validation gap (out-of-scope for §2.7)
- [`backtest/artifact_schema.py:684`](../../backtest/artifact_schema.py#L684),
  [`:692`](../../backtest/artifact_schema.py#L692),
  [`:972`](../../backtest/artifact_schema.py#L972) — canonical-site GAPs
  (per v2 PFR Advisor F3 fix-substantive-leak)
