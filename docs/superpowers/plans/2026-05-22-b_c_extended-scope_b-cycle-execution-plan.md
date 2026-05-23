# B-C-extended Scope-B cycle execution plan — v5

**Status:** **RATIFIED 2026-05-22 per Charlie register "Inline-fix Codex Fv5-1 + Fv5-2 → Charlie direct ratify v5"** (cross-leg-convergent APPROVE at v5 PFR + 2 Codex LOW inline-fixed); local scratch (untracked)
**Plan version:** v5 RATIFIED (replaces v4; v4 PFR adjudication = ADOPT 10; v5 PFR cross-leg-convergent APPROVE + 2 inline-fix LOW)
**Drafted:** 2026-05-22
**Ratified:** 2026-05-22

---

## §0 Cycle metadata

**Cycle ID:** B-C-extended (engine-layer artifact-preservation structural refactor)
**Path:** Path 3 — Scope-B
**Entry register-event boundary:** 2026-05-22
**Charlie register text:** "convergent disambiguations + Path 3 Codex authorized"
**v5 register text:** "(α''') Fire v5 drafting with all v4 ADOPT findings applied; dispatch v5 PFR (Codex's recommendation; rigor over cycle-cost)"

**Locked state (carried forward):**
- Substantive direction: Scope-B
- V3 Scope-B branch wording: locked
- Disambiguations (a)/(b)/(c): locked

**Orchestrator self-correction register (cumulative within B-C-extended planning arc — 3 confirmed instances):**

1. **v1 PUSHBACK on Codex F2 "5.5" claim** (caught at v2): wrong-scope verification (N=100,000 vs Codex's intended fixture-N=6). Codex was empirically correct.
2. **v3 application of Codex F5 introduced scipy fisher=True numerical misattribution** (caught at v3 PFR by BOTH legs independently): wrote "2.5" while actual scipy `kurtosis(fisher=True, bias=True)` (default) = 0.0.
3. **v4 T1.2 line 165 "(12 total fields)" while Contract 2.0.5 enumerates 14** (caught at v4 PFR by BOTH legs independently): orchestrator-layer arithmetic drift — added `parent_run_id` + `returns_per_bar_path` + `returns_per_bar_sha256` to Contract 2.0.5 but did not update T1.2 reference count from v3's 11 → v4's 14.

**Cumulative pattern observation:** 3 instances across 4 iterations (75% recurrence rate at orchestrator-layer numerical claims absent cross-leg verification). Pattern is empirically structural. Cross-model leg LOAD-BEARING at every plan iteration boundary. **§35-adjacent codification candidate strengthened:** "Numerical claim verification at every plan iteration boundary, not just at first introduction."

**v5 process discipline (extended):**
- ALL numerical claims empirically re-verified via Python before writing
- ALL field counts cross-referenced against Contract 2.0.5 enumeration (target: 14)
- R3.1d §5.2 6-row mapping fully inlined (not delegated)
- Path canonicalization rule explicit
- `None` normalization scoping disambiguated (interpretation b: opt-in=False default-resolves)

---

## §1 Substantive scope (locked from V3 Scope-B branch)

> **B-C-extended cycle entry — Scope-B locked.**
>
> **Scope:** engine-layer artifact-preservation refactor for future Phase B / Tier 5 / Tier 6 single-run holdout and evaluation-gate runs.
>
> **Engineering scope:** preserve post-warmup per-bar portfolio return series + T_obs + γ3 (sample skew) + γ4 (raw standardized kurtosis mu4/sigma⁴, NOT excess; Gaussian limit = 3) + registry linkage fields per Contract 2.0.3-2.0.4. Schema discipline per Contract 2.0.2 + Contract 2.0.5.
>
> **Validation = fixture/smoke/canary/integrity suite** (NOT historical reproduction): see §3.
>
> **Path α invariant binding:** canonical 18-cohort artifact production deferred to B-C-narrow at separate Charlie register-event. B-C-extended SEAL produces NO promotion-relevant numerical output.

---

## §2.0 Contract locks before code

### Contract 2.0.1: Moment estimator convention

- **γ3 (sample skew):** `mean((r - rbar)^3) / mean((r - rbar)^2)^(3/2)`; population formula (NOT bias-corrected)
- **γ4 (raw standardized kurtosis):** `mean((r - rbar)^4) / mean((r - rbar)^2)^2`; population formula (NOT bias-corrected, NOT excess)
- **Gaussian limit:** γ3 = 0, γ4 = 3
- **Environment precondition:** scipy ≥ 1.9 required for `nan_policy` keyword; fixture test fails closed if precondition not met
- **LOCKED implementation:**
  - γ4 via `scipy.stats.kurtosis(returns_array, fisher=False, bias=True, nan_policy='omit')`
  - γ3 via `scipy.stats.skew(returns_array, bias=True, nan_policy='omit')`
- **PROHIBITED implementations (empirically verified divergent values at fixture vector `[-1, 1, 0, 0, 0, 0]`, N=6):**
  - pandas `.kurt()` (default; Fisher excess bias-corrected) = 2.5 (excess, NOT raw)
  - pandas `.kurt() + 3` = 5.5 (raw bias-corrected, NOT raw population)
  - scipy `kurtosis(fisher=True, bias=True)` = 0.0 (excess uncorrected; default scipy)
  - scipy `kurtosis(fisher=True, bias=False)` = 2.5 (excess bias-corrected)
  - scipy `kurtosis(fisher=False, bias=False)` = 5.5 (raw bias-corrected)
- **Downstream consumer note:** BLdP DSR consumption layer applies excess conversion (γ4 - 3) if formula expects excess

### Contract 2.0.2: Schema version string + distinct validation branch

- **New value:** `b_c_extended_v1`
- **Extension pattern:** add to `ARTIFACT_SCHEMA_VERSION_*` enum + `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` tuple at `backtest/wf_lineage.py:61-126`
- **Distinct validation branch:** adding to tuple alone is insufficient. A distinct consumer-side validation branch must enforce ALL Contract 2.0.5 header fields + per-bar artifact linkage + `cost_anchor_id` mapping integrity. Tuple membership = acceptance gate; per-version validation branch = field-discipline gate. Both required.
- **Backward compatibility:** `phase2c_7_1` consumers continue to validate without modification
- **Helper placement** (NAMED sub-decision per §10): third helper `check_b_c_extended_semantics_or_raise` vs extension of existing helpers vs new module `backtest/artifact_schema.py`; final lock at T1.2 implementation

### Contract 2.0.3: Linkage aliasing

- **Artifact field:** `source_batch_id` (matches existing producer convention)
- **Registry column:** `runs.batch_id` (matches existing schema)
- **Validation:** alias mapping documented at schema spec; consumer code rejects mismatched aliases at write-time
- **Triple linkage:** `hypothesis_hash + batch_id + run_id` resolvable in `experiments.db` runs table
- **`run_id` field name:** lock artifact field name to `run_id` (aliases registry `runs.run_id`); avoid `engine_run_id`

### Contract 2.0.4: cost_anchor_id mapping (extended per Codex v4 Fv4-1 HIGH + cross-leg-convergent v4 Fv4-2/F-v4-2 MEDIUM)

- **Field:** `cost_anchor_id` in registry `runs` table (column exists at `experiment_registry.py:86,139`)
- **Population mechanism:** resolved from canonicalized `execution_config_path` via path-keyed mapping table at R3.1d §5.2

- **Path canonicalization rule (per Codex v4 Fv4-1 HIGH + v5 Fv5-1 LOW inline-fix for safe containment):** before mapping lookup, T1.3 engine MUST canonicalize the path using `commonpath`-based containment (NOT naive string-prefix; prefix-based comparison falsely admits paths like `/repo_rootX/file` to `/repo_root` containment):

  ```python
  repo_root_real = os.path.realpath(repo_root)
  candidate_real = os.path.realpath(os.path.abspath(path))
  # Containment check: commonpath returns repo_root_real iff candidate is genuinely under it
  if os.path.commonpath([repo_root_real, candidate_real]) != repo_root_real:
      raise FailClosedError(...)  # path outside repo root
  # Repo-relative POSIX key for mapping lookup:
  key = os.path.relpath(candidate_real, repo_root_real).replace(os.sep, "/")
  ```

- **Case-sensitivity policy (per v5 Fv5-1 LOW inline-fix):** on case-insensitive filesystems (macOS HFS+/APFS default), exact-case match is required at mapping lookup (do NOT apply `os.path.normcase`); case-only mismatches (e.g., `config/Execution.yaml`) FAIL CLOSED via mapping miss. This is intentional — mapping table keys are case-sensitive lowercase by convention.
- **Paths NOT under repo root:** fail closed with structured error per Contract 2.0.4 (only truly outside paths fail; legitimate in-repo paths regardless of caller's path-form succeed)

- **Initial mapping table — FULL 6-row inline enumeration per R3.1d §5.2 (per cross-leg-convergent F-v4-2/Fv4-2 MEDIUM):**

| canonicalized `execution_config_path` | `cost_anchor_id` | Role (paraphrased from R3.1d §5.2 — see source for verbatim text) |
|---|---|---|
| `config/execution.yaml` | `legacy_perp_inspired_7bps_v0` | default; legacy Phase 1-2 runs |
| `config/execution_phase4_07bps.yaml` | `phase4_forward_07bps_v1` | Phase 4 cost-grid 07bps (supplementary sensitivity) |
| `config/execution_phase4_13bps.yaml` | `phase4_forward_13bps_v1` | Phase 4 cost-grid 13bps (supplementary sensitivity) |
| `config/execution_phase4_15bps.yaml` | `phase4_forward_15bps_v1` | Phase 4 forward-holdout primary basis (per PHASE4_PLAN §1.5) |
| `config/execution_phase4_17bps.yaml` | `phase4_forward_17bps_v1` | Phase 4 cost-grid 17bps (supplementary sensitivity) |
| `config/execution_phaseb_spot_15bps.yaml` | `spot_realistic_15bps_v1` | Phase B Tier 5/6 conservative-anchor gate (R3.1d SEAL output) |

**Authoritative source:** Path→`cost_anchor_id` pairs (columns 1+2) are byte-equivalent against R3.1d §5.2 verbatim (verified at v5 PFR by both legs). Role descriptions (column 3) are paraphrased; for verbatim role text consult `docs/phase5/R3_1D_COST_GRID_REANCHOR_NOTE.md` §5.2 lines 286-293.

Do NOT extend mapping at this cycle; future anchors require fresh Charlie register per R3.1d §5.2 discipline.

- **Default normalization (per Codex v3 Fv3-2 HIGH; clarified per Advisor v4 F-v4-6 LOW):** 
  - **Interpretation (b) LOCKED:** when lineage context object is None OR `execution_config_path` is None at engine entry, normalize to `config/execution.yaml` and resolve to `legacy_perp_inspired_7bps_v0`. This preserves backward compat for all callers (legacy Phase 1-2 backtests + new callers not threading lineage context).
  - Callers explicitly threading lineage context with non-None `execution_config_path` use canonicalized lookup per mapping table.

- **Critical disambiguation:** `cost_anchor_id` values come ONLY from R3.1d §5.2 path mapping (canonicalized), NOT YAML `cost_model.name` field

- **Fail-closed clause:** if canonicalized `execution_config_path` is set to a value not in mapping table AND not the legacy default OR path is outside repo root, T1.3 engine MUST raise (fail closed); do NOT silently fall back to `cost_model.name`

- **Error message content (per Advisor v3 A3 LOW; precedent at `wf_lineage.py:147-156`):** raised error MUST include (i) the canonicalized un-mapped path; (ii) full known mapping table contents (6 rows); (iii) explicit guidance: "Update R3.1d §5.2 mapping for new anchor or contact human approval before extending mapping"

- **Engine modification:** `_write_to_registry()` populates `cost_anchor_id` for new Phase B / Tier 5 / Tier 6 runs per CLAUDE.md HARD CONSTRAINT line 272

### Contract 2.0.5: Artifact path policy + per-bar linkage validation discipline (extended per Codex v4 Fv4-4 MEDIUM + Advisor v4 F-v4-7 LOW)

- **New artifacts under:** `data/phase2c_evaluation_gate/<run_id_or_batch_dir>/<hypothesis_hash>/` directory pattern
- **Per-bar return series file:** path + format locked at T1.2 implementation (working assumption: `returns_per_bar.parquet`)
- **Moment summary location:** lock at T1.2 (extend `holdout_summary.json` vs new `moment_summary.json`)

- **Header fields per artifact — 14 total fields (count locked; cross-referenced against enumeration below):**

| # | Field | Type | Description |
|---|---|---|---|
| 1 | `artifact_schema_version` | string | LOCKED to `b_c_extended_v1` for new artifacts |
| 2 | `run_id` | string | aliases registry `runs.run_id` per Contract 2.0.3 |
| 3 | `hypothesis_hash` | string | per Contract 2.0.3 triple linkage |
| 4 | `source_batch_id` | string | aliases registry `runs.batch_id` per Contract 2.0.3 |
| 5 | `parent_run_id` | Optional[string] | per Codex v3 Fv3-1; required by current `_write_to_registry()`; None valid for single-run callers without parent (per Advisor v4 F-v4-5) |
| 6 | `regime_key` | string | per existing schema convention |
| 7 | `engine_commit` | string | git SHA at engine-commit level |
| 8 | `current_git_sha` | string | git SHA at full-repo level |
| 9 | `execution_config_path` | string | repo-relative POSIX path per Contract 2.0.4 canonicalization |
| 10 | `execution_config_sha256` | string | content-addressable hash; required per Advisor v1 F11 |
| 11 | `parquet_data_sha256` | string | content-addressable hash for source data |
| 12 | `cost_anchor_id` | string | resolved per Contract 2.0.4 mapping |
| 13 | `returns_per_bar_path` | string | relative to artifact's containing directory `<run_id_or_batch_dir>/<hypothesis_hash>/` (per Advisor v4 F-v4-7) |
| 14 | `returns_per_bar_sha256` | string | content-addressable hash for per-bar artifact integrity |

- **Per-bar artifact validation discipline (per Codex v4 Fv4-4 MEDIUM; matching `parquet_data_sha256` precedent):**
  - **File-exists check:** consumer MUST verify `returns_per_bar_path` resolves to existing file before reading; fail closed on absence
  - **Path confinement:** consumer MUST verify resolved path is under artifact's containing directory (no `../` escapes); fail closed on confinement violation
  - **SHA256 recomputation on read:** consumer MUST recompute SHA256 of read file content; compare against stored `returns_per_bar_sha256`; fail closed on mismatch
  - **T_obs alignment check:** consumer MUST verify `T_obs` (count of finite per-bar returns) matches actual finite-row count in per-bar series; fail closed on mismatch

### Contract 2.0.6: Validation matrix

**4 test classes:**

**(a) Fixture test — comprehensive adversarial value specification:**

Input: explicit vector `[-1, 1, 0, 0, 0, 0]` (N=6); all numerical values empirically verified at v5 drafting:

- **PASS criterion:** scipy `kurtosis(fisher=False, bias=True, nan_policy='omit')` produces `3.000000` (within 1e-12 of raw analytical mu4/sigma⁴)
- **FAIL assertions (ALL must confirm-fail the 1e-12 tolerance band around 3.0; deterministic separation ≥ 0.5):**
  - pandas `.kurt()` (default) = `2.500000` ≠ 3.0
  - pandas `.kurt() + 3` = `5.500000` ≠ 3.0
  - scipy `kurtosis(fisher=True, bias=True)` (default scipy) = `0.000000` ≠ 3.0
  - scipy `kurtosis(fisher=True, bias=False)` = `2.500000` ≠ 3.0
  - scipy `kurtosis(fisher=False, bias=False)` = `5.500000` ≠ 3.0
- γ4 passing band MUST EXCLUDE 0.0 (excess-kurtosis convention check)
- Test seed: deterministic; vector explicit (no random generator)
- scipy version precondition check: fail closed if scipy < 1.9

**(b) Smoke test:** 1-3 synthetic minimal candidates via canonical `data/raw/btcusdt_1h.parquet` OR fully synthetic OHLCV (lock at T1.5 implementation)

**(c) Canary test (extended per Codex v4 Fv4-5 LOW):** legacy `phase2c_7_1` artifacts + new per-bar-aware consumer code; hash-before-after byte identity protection covers:
  - Aggregate `holdout_results.csv` (mandatory)
  - **Aggregate `holdout_summary.json` (MANDATORY, not "if exists")** — Phase 4 15bps directory specifically has this file [VERIFIED via filesystem inspection]
  - ALL N per-candidate `holdout_summary.json` files where N = candidate count at gate dir root (currently N=39 at `phase4_forward_2026_15bps_v1/`; per Advisor v4 F-v4-3 LOW, T1.4 implementation verifies N matches expected at canary test execution)

**(d) Registry integrity test:** triple resolution + 5 failure cases:
  - Duplicate `run_id`: fail closed
  - Missing `hypothesis_hash`: fail closed
  - Missing `batch_id`: fail closed
  - Mismatched `cost_anchor_id` vs canonicalized `execution_config_path` mapping: fail closed
  - Un-mapped canonicalized `execution_config_path` (non-None, non-default): fail closed
  - Plus happy path: `None` → `config/execution.yaml` → `legacy_perp_inspired_7bps_v0` normalization

**Pass criterion:** 4/4 classes pass; no relaxation without fresh Charlie register-event.

---

## §2 Engineering deliverables (Tier 1 task decomposition; execution order)

**Execution order:** T1.2 → T1.3 → T1.1 → T1.4 → T1.5 → T1.6

### T1.2 Schema design

**Scope:** Implement Contract 2.0.2 + 2.0.5 — versioned schema spec + distinct validation branch + per-bar linkage validation discipline.

**Deliverables:**
- New schema version `b_c_extended_v1` added to `backtest/wf_lineage.py` enum + tuple
- **Distinct validation branch** enforcing **14 Contract 2.0.5 header fields** (count cross-referenced against Contract 2.0.5 enumeration; do NOT hardcode count separately from enumeration)
- Per-bar artifact validation discipline per Contract 2.0.5 (file-exists + path-confinement + SHA256-recompute + T_obs-alignment)
- Versioned schema discipline: required-field validation at write-time + fail-closed consumer validation at read-time + deterministic row/key ordering
- Backward compatibility preserved
- Documentation: schema spec at schema declaration boundary

**Touchpoints:**
- `backtest/wf_lineage.py` — schema enum + tuple + new per-version validation branch
- New module `backtest/artifact_schema.py` OR extended `backtest/wf_lineage.py` (NAMED sub-decision per §10)

### T1.3 Registry + API extension

**Scope:** Implement Contract 2.0.3 + 2.0.4 — registry triple linkage + cost_anchor_id population + canonicalization + API plumbing.

**Deliverables:**
- Extend `run_backtest()` API with explicit artifact/lineage context object containing all 14 Contract 2.0.5 fields. Context object opt-in: default disabled (preserves backward compat); when None or absent, Contract 2.0.4 default normalization applies (interpretation b LOCKED).
- **`_write_to_registry()` signature extension** (per Advisor v3 A1 MEDIUM): add `execution_config_path` parameter; without this, fail-closed clause cannot be implemented
- **Path canonicalization implementation** (per Codex v4 Fv4-1 HIGH): `os.path.realpath()` + repo-root relative POSIX conversion + mapping lookup; paths outside repo root fail closed
- **`execution_config_path = None` normalization (interpretation b LOCKED)**: None → `config/execution.yaml` → `legacy_perp_inspired_7bps_v0`
- **`parent_run_id` Optional[str] semantics under opt-in=True** (per Advisor v4 F-v4-5 LOW): None valid for single-run callers without parent linkage; required-or-None policy locked at T1.3 implementation
- **Lineage context propagation surface (4 entry points):**
  1. `run_backtest()` API (primary)
  2. `run_regime_holdout()` at `backtest/engine.py:1464` (current implementation threads `parent_run_id`; extend with full lineage context)
  3. `run_walk_forward()` at `backtest/engine.py:829, 982-1022` (inner `run_backtest()` opt-in=False at engine.py:986; outer wrapper handles slice-aware writer)
  4. Evaluation-gate driver `scripts/run_phase2c_evaluation_gate.py`
- `_write_to_registry()` populates `cost_anchor_id` via canonicalized Contract 2.0.4 mapping; fails closed on un-mapped paths with structured error message
- Triple linkage: every preserved per-bar artifact emits records resolvable to `(hypothesis_hash, batch_id, run_id)` in `experiments.db`
- Migration approach: append-only + idempotent + backward-compatible per `experiment_registry.py:99-103` convention; rollback via backup/restore-based
- **Registry migration as named sub-decision** requiring fresh Charlie register-event if SQL `ALTER TABLE ... ADD COLUMN` migration is needed

**Failure mode handling:**
- Duplicate `run_id`: fail closed
- Missing `hypothesis_hash` or `batch_id`: fail closed
- Mismatched `cost_anchor_id` vs canonicalized `execution_config_path`: fail closed
- Un-mapped canonicalized `execution_config_path` (non-None, non-default): fail closed with structured error
- Path outside repo root: fail closed with structured error

### T1.1 Engine artifact writer + slice-aware emission

**Scope:** Implement Contract 2.0.1 + 2.0.5 + 2.0.6 — engine modification.

**Deliverables:**
- Extend `EquityCurveCollector` analyzer at `backtest/engine.py:265-300` for per-bar portfolio return series capture
- Add return-series persistence at write-time; write `returns_per_bar.parquet` + populate `returns_per_bar_path` + `returns_per_bar_sha256` per Contract 2.0.5
- Compute γ3 + γ4 + T_obs per Contract 2.0.1 (scipy `kurtosis(fisher=False, bias=True, nan_policy='omit')` + `skew(bias=True, nan_policy='omit')`)
- **Slice-aware emission:** canonical writer signature accepts explicit `equity_curve=ec_test` + `trades=trades_test` parameters; MUST NOT infer from `BacktestResult.equity_curve`
- **Walk-forward integration discipline:** `run_walk_forward()` inner `run_backtest()` call at `engine.py:986` MUST be invoked with opt-in=False; WF outer wrapper is only legitimate WF writer
- Emit artifacts at structured artifact path per Contract 2.0.5

**Implementation discipline:**
- γ3/γ4/T_obs computed on post-warmup finite per-bar returns (NaN/inf excluded from T_obs count)
- Backtrader determinism preservation
- γ4 fixture-test-driven verification via explicit vector

### T1.4 Backward compatibility verification

**Scope:** Implement Contract 2.0.6 canary test class with extended scope.

**Deliverables:**
- **Test case (i):** legacy `phase4_forward_2026_15bps_v1/<hash>/holdout_summary.json` files validate under existing `wf_lineage.check_evaluation_semantics_or_raise()` without modification
- **Test case (ii):** new per-bar-aware consumer code rejects-or-degrades-gracefully on absence of per-bar series for legacy schema
- **Hash-before-after verification (extended scope):**
  - Aggregate `holdout_results.csv` byte-identical before/after (MANDATORY)
  - **Aggregate `holdout_summary.json` byte-identical before/after (MANDATORY for Phase 4 15bps; NOT conditional per Codex v4 Fv4-5 LOW)**
  - ALL N per-candidate `holdout_summary.json` files byte-identical before/after (N=39 currently; verify N matches expected at test execution per Advisor v4 F-v4-3 LOW)
- Validation call coverage: `check_evaluation_semantics_or_raise()` on aggregate + all per-candidate artifacts

### T1.5 Fixture/smoke/canary/integrity test suite

**Scope:** Implement Contract 2.0.6 validation matrix.

**Deliverables:**

**(a) Fixture test:** deterministic vector `[-1, 1, 0, 0, 0, 0]`
- Input: explicit hard-coded vector
- Expected: scipy `kurtosis(fisher=False, bias=True, nan_policy='omit')` produces `3.000000` ± 1e-12
- All 5 alternative implementations MUST FAIL 1e-12 tolerance around 3.0 (specific values from Contract 2.0.6 (a))
- γ4 passing band MUST EXCLUDE 0.0
- scipy version precondition: fail closed if scipy < 1.9
- Deterministic seed; explicit vector

**(b) Smoke test:** 1-3 synthetic candidates

**(c) Canary test:** as T1.4 specification (aggregate CSV + aggregate JSON mandatory + N per-candidate)

**(d) Registry integrity test:** triple resolution + 5 failure cases + 1 None-normalization happy path

### T1.6 Documentation + consumer enumeration

**Scope:** Document Contract 2.0.1-2.0.5 + consumer enumeration.

**Deliverables:**
- Schema spec
- γ3/γ4 raw-standardized convention notes at schema declaration boundary
- Registry linkage spec including R3.1d §5.2 6-row mapping table + canonicalization rule
- Migration notes if applicable
- `data_dictionary.md` updates
- wf_lineage.py extension pattern documentation
- Consumer enumeration: grep all consumers of `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` + `schema_version` references; verify each handles `b_c_extended_v1` OR document explicit no-op behavior

---

## §3 Validation approach + success criteria (restored numbered structure per Advisor v4 F-v4-4 LOW)

**Validation = Contract 2.0.6 4-class suite** (specifications detailed at §2.0.6).

**Success criteria for cycle SEAL (8 mandatory items):**

1. All 4 test classes (fixture/smoke/canary/integrity) pass — 4/4 mandatory
2. Backward compatibility verified — hash-before-after byte identity on aggregate CSV + aggregate JSON + ALL N legacy per-candidate JSONs
3. Schema spec documented at schema declaration boundary per Contract 2.0.1-2.0.5
4. γ4 raw-standardized convention documented + fixture-test-verified with explicit vector + 5 alternative implementations confirmed-failing
5. `b_c_extended_v1` distinct validation branch implemented + tested
6. Engineering deliverables T1.1-T1.6 complete with Contract 2.0 lock adherence
7. Lineage context propagation verified through all 4 entry points (`run_backtest` / `run_regime_holdout` / `run_walk_forward` / evaluation-gate driver)
8. Consumer enumeration complete; all consumers handle `b_c_extended_v1` or have documented no-op behavior

**Failure handling:** if any test class fails or schema discipline violation discovered, cycle does NOT SEAL until resolved. No tolerance relaxation without fresh Charlie register-event.

---

## §4 Explicit exclusions

NOT in scope:
- Canonical 18-cohort artifact production (deferred to B-C-narrow)
- Historical reproduction of `phase4_forward_2026_15bps_v1`
- DSR / PSR / N* / ρ̄ computation under any framing
- Threshold evaluation; promotion-list; Tier 6 application; Tier 5 SEAL; capital implication
- Retroactive backfill; cost-model parameter changes (all 6 R3.1d §5.2 mapped configs unmodified)
- Registry schema additions beyond Contract 2.0.4 cost_anchor_id population + Contract 2.0.3 triple linkage
- Methodology codification (§35 + R6.1-A/B/C separate eligible-not-named)

---

## §5 Anti-pre-emption preservation

Non-exhaustive successor classes remain eligible-not-named at separate Charlie register-event boundaries:

- B-C-narrow data-recovery (method/timing/fire-boundary remain separate decisions)
- Post-V_SEAL Tier 6 evaluation application
- §35 codification candidate (strengthened by 3 cross-cycle orchestrator-error instances)
- R6.1-A + R6.1-B + R6.1-C codification cycle
- **Orchestrator-adjudication-error pattern cross-cycle codification (3 confirmed instances within B-C-extended planning arc):** v1 "5.5" PUSHBACK + v3 "fisher=True 2.5" misattribution + v4 "12 total fields" count drift; all caught by cross-model leg; pattern empirically structural at ~75% per-iteration rate
- BL-Y-refined Phase 1 effectiveness extension codification
- Codex cross-model leg LOAD-BEARING precedent codification
- Advisor miss-pattern empirical data codification
- RW/WY framework family reopening cycle
- N* / SD-A-ε / SD-E-γ estimator refinements (post-data-recovery)
- R2.2 Monday-pattern; R3.1b/c cost measurement; FLIP-TRIGGERED mechanism investigation
- P2a DSL recovery; IS-OOS supplementary; Bonferroni re-evaluation
- Phase 4 paper-trading deployment
- Memory codification on R5.2 + R6.1 + B-C-extended planning-arc empirical contributions
- Other Charlie-specified

---

## §6 Reviewer round plan

### v5 PFR-rule-Y reviewer round (THIS ROUND; in parallel dispatch with v5 drafting)

**Routing:** 2-leg per B2 standing rule
**Legs:** Codex + quant-research-advisor parallel
**Iteration count:** v1 → v2 → v3 → v4 → v5 = 5 plan iterations; 4 PFR rounds total
**PFR-rule-Y eligibility:** FIRES — v4 adjudication introduced substantive NEW content (Contract 2.0.4 path canonicalization rule + 6-row inline mapping + Contract 2.0.5 14-field tabular enumeration with per-bar validation discipline + interpretation (b) LOCKED + restored §3 numbered structure)

**Review tasks:**
1. Own-finding-anchoring acknowledgment + verify v4 findings correctly applied in v5
2. Adversarial review of v5 substantive changes (path canonicalization rule + 6-row enumeration + Contract 2.0.5 tabular fields + per-bar validation discipline)
3. **Numerical/factual claim verification:** independently re-execute kurtosis fixture values; verify Contract 2.0.5 field count = 14; verify R3.1d §5.2 6-row inlined mapping matches authoritative source
4. Newly-introduced issues check (5th iteration; orchestrator pattern recurrence ~75% rate suggests still possible)
5. Anti-pre-emption check
6. **APPROVE-FOR-PLAN-RATIFY** recommendation OR further v6 iteration; if APPROVE, recommend whether to skip PFR or do final PFR-rule-Y as confirmation

### Convergence + escalation

- Per-finding adjudication per `feedback_reviewer_suggestion_adjudication.md`
- Plan iteration at 5; Advisor F9 escalation framework has fired (2-3 rounds typical); Charlie's "(α''') Codex rigor over cycle-cost" register chose continued iteration over Advisor's Path δ-revisited inline-fix
- If v6 required → cycle-pattern reassessment IS warranted (see §8 process risks)

---

## §7 SEAL artifact structure (preliminary)

**Path:** `docs/phase5/B_C_EXTENDED_SCOPE_B_NOTE.md`
**Estimated size:** 350-550 lines (extended from v4 estimate per Contract 2.0.4 + 2.0.5 expanded specification)

**Required sections:**
- §0 Cycle metadata + Charlie register chain (extended with 5 plan iterations + 3 orchestrator-error instances)
- §1 Substantive scope
- §2 Contract locks (2.0.1-2.0.6) execution outcomes
- §3 Engineering deliverables (T1.1-T1.6)
- §4 Validation results
- §5 Schema spec documentation
- §6 γ4 convention specification with fixture vector verification
- §7 Backward compatibility verification
- §8 cost_anchor_id mapping + canonicalization + registry linkage verification
- §9 Lineage context propagation verification (4 entry points)
- §10 Consumer enumeration results
- §11 Orchestrator-adjudication-error pattern recurrence summary (3 instances; eligible-not-named for separate codification)
- §12 Eligible-not-named successors NOT bound
- §13 V_SEAL closure

---

## §8 Risk disclosure

### Engineering risks

- **Moment estimator full convention risk:** library defaults all matter; Contract 2.0.1 + 2.0.6 + T1.5 (a) lock comprehensive specification with empirical adversarial assertions
- **`cost_anchor_id` mapping + canonicalization correctness:** Contract 2.0.4 covers full 6-row mapping + path canonicalization rule + None normalization scoping + fail-closed with structured error
- **`b_c_extended_v1` validation branch gap risk:** distinct branch required beyond tuple membership
- **Lineage context propagation surface:** 4 entry points; missing `parent_run_id` fixed at v4; Optional[str] semantics clarified at v5
- **Per-bar artifact linkage + validation discipline:** Contract 2.0.5 14-field schema + file-exists + path-confinement + SHA256-recompute + T_obs-alignment per parquet_data_sha256 precedent
- **Registry schema migration risk:** SQLite one-way idempotent; backup/restore-based rollback
- **Backtrader determinism risk:** version drift unverified; structural refactor preserves determinism
- **Legacy artifact backward compatibility risk:** canary covers aggregate CSV + aggregate JSON (mandatory) + ALL N per-candidate
- **Walk-forward slice-aware emission risk:** explicit writer signature mitigates
- **Consumer migration risk:** new schema version requires T1.6 consumer enumeration

### Process risks (extended per cumulative arc observations)

- **Orchestrator-adjudication-error pattern recurrence:** 3 confirmed instances within planning arc (v1 "5.5", v3 "fisher=True 2.5", v4 "12 fields"). Pattern empirically structural at ~75% per-iteration rate absent cross-leg verification. Cross-model leg LOAD-BEARING at every plan iteration boundary. v5 process discipline (empirical pre-verification + cross-referenced field counts + inlined mapping table) attempts to break the pattern; v5 PFR will verify success or 4th-instance failure.
- **Reviewer round iteration scope at plan stage:** 5 iterations + 4 PFR rounds. Advisor F9 escalation framework: 2-3 rounds typical; v5 is beyond. Charlie register chose continued iteration over Path δ-revisited inline-fix.
- **PFR-rule-Y eligibility scoping:** applied at each round; cross-model leg structurally required.

---

## §9 Honest uncertainty

- **Touchpoint precision:** preliminary list across `backtest/engine.py` + `metrics.py` + `experiment_registry.py` + `wf_lineage.py` + `scripts/run_phase2c_evaluation_gate.py` + new test files; final lock at implementation
- **Registry schema migration necessity:** unverified at plan level; lock at T1.3 implementation; fresh Charlie register if SQL migration required
- **Smoke test data source:** canonical OHLCV vs fully synthetic; lock at T1.5
- **Cycle duration:** rough multi-day estimate; no binding timing per R6.1 §11 "no timing bound" precedent
- **Implementation order:** T1.2 → T1.3 → T1.1 → T1.4 → T1.5 → T1.6 LOCKED
- **Fixture vector verification:** explicit `[-1, 1, 0, 0, 0, 0]` empirically verified at v4 + v5 drafting; 5 alternative implementations specified with empirical values
- **Plan iteration count:** v1 → v2 → v3 → v4 → v5 = 5 iterations. Cycle-pattern observation: v4 had zero BLOCKING + 1 HIGH (path canonicalization) + 2 cross-leg-convergent MEDIUM + 5 LOW. v5 attempts substantive saturation. If v5 PFR returns zero NEW BLOCKING, plan ratify defensible.

---

## §10 Anti-pre-emption explicit reminder + named sub-decisions

This plan v5 is **advisory and pre-ratify**. No engineering work begins until:
1. v5 PFR-rule-Y reviewer round completes
2. Per-finding adjudication applied
3. Possible v6 iteration for new content
4. Convergent APPROVE-FOR-PLAN-RATIFY reached
5. **Charlie plan ratify register fires**

### Named load-bearing sub-decisions requiring fresh Charlie register-event if not in v_final plan:

- Schema version string (currently `b_c_extended_v1`)
- ~~`b_c_extended_v1` validation branch semantics~~ **RESOLVED 2026-05-22 per Charlie register "(B-lock-Codex) Lock Codex package: (B1-c) hybrid + (B2-b) + (B3-b) BCExtendedSchemaValidationError subclass":** B1-c hybrid validation order (fail-fast on structural failures: schema_version mismatch, missing required fields, path-confinement violations; collect-all on per-field deterministic failures within successful structural pass); B2-b Optional field semantics for `parent_run_id` (None valid + missing-key FAIL CLOSED + empty-string FAIL CLOSED); B3-b new exception class `BCExtendedSchemaValidationError(ValueError)` (LSP preserves existing `except ValueError` consumers; carries structured failure list as exception payload per B1-c hybrid pairing). Validation check order MUST be structural-first: schema_version → top-level discriminator fields → per-domain required fields → optional-field presence checks (per Advisor B1×B2 ordering hazard mitigation).
- ~~Validation-branch helper placement~~ **RESOLVED 2026-05-22 per Charlie register "(A1) Lock Option (i) with Codex's domain-fence-via-per-domain-tuple-split refinement":** third helper `check_b_c_extended_semantics_or_raise` added to `backtest/wf_lineage.py` alongside existing 2 helpers + `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` split into 3 per-domain tuples (`ACCEPTED_EVALUATION_SCHEMA_VERSIONS` / `ACCEPTED_WF_SCHEMA_VERSIONS` / `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS`); each helper accepts only its domain's tuple (constant-level domain fence; per Codex v2-A Sub-decision A cross-leg convergent recommendation); heavy-private-implementation extraction to `backtest/artifact_schema.py` DEFERRED to T1.2 implementation discretion (if Contract 2.0.5 validation needs DataFrame/parquet/registry-heavy logic, extract to private impl module behind wf_lineage.py public shim; if pure dict/path/hash logic, stay fully in wf_lineage.py).
- ~~Lineage context propagation surface (4 entry points)~~ **RESOLVED 2026-05-22 per Charlie register "Lock convergent package above" (T1.3-D-i):** `@dataclass(frozen=True, kw_only=True) class LineageContext` with 14 Contract 2.0.5 fields; `__post_init__` validates B2-b parent_run_id + canonicalizes execution_config_path + resolves cost_anchor_id via mapping; field-count assertion test catches drift. Threading through 4 entry points: `run_backtest()` (already has `execution_config_path` per Phase 4 [VERIFIED engine.py:330-340]) + `run_regime_holdout()` (already has [VERIFIED engine.py:1464-1484]) + `run_walk_forward()` (parameter to be ADDED per T1.3 additional lock [VERIFIED engine.py:829-839 currently missing]) + evaluation-gate driver. Codex `kw_only=True` refinement adopted; avoid mutable defaults; `field(default_factory)` only when needed.
- ~~`parent_run_id` Optional[str] required-or-None policy~~ **RESOLVED 2026-05-22 per Charlie register "Lock convergent package above" (T1.3-C HYBRID):** preserve existing `_write_to_registry(parent_run_id: str | None = None)` scalar default-None kwarg for backward compat (103 test call sites + 19 script call sites at risk per cross-leg verification); ADD `LineageContext` as primary mechanism for NEW Phase B / Tier 5 / Tier 6 public callers (T1.3-D-i); conflict-check at write boundary — if both scalar AND context passed with disagreement, FAIL CLOSED.
- γ4 fixture tolerance (currently 1e-12)
- ~~Registry migration approach (application-layer indexing vs SQL `ALTER TABLE`)~~ **RESOLVED 2026-05-22 per Charlie register "Lock convergent package above" (T1.3-A-ii):** SQL `ALTER TABLE` migration via existing `MIGRATION_COLUMNS` pattern at `experiment_registry.py:113-140` (entry for `cost_anchor_id` already present at line 139); empirical verification confirmed `cost_anchor_id` column MISSING from live `experiments.db` (`.schema runs` query) while source declares it — migration never ran on existing DB. Lazy-trigger via existing `create_table()` call at `_write_to_registry:628` (already invoked); no NEW migration code required; idempotent append-only convention preserved.
- ~~Path canonicalization implementation details (currently `os.path.realpath()` + repo-root relative POSIX; specific edge cases may need T1.3 implementation refinement)~~ **RESOLVED 2026-05-22 per Charlie register "Lock convergent package above" (T1.3-B):** pure function `canonicalize_execution_config_path(path: Path | str, *, repo_root: Path | None = None) -> str` added to `backtest/artifact_schema.py` (co-located with `COST_ANCHOR_ID_MAPPING` for atomic-maintenance SSOT); repo root resolution via `Path(__file__).resolve().parent.parent` per existing `experiment_registry.py:45` `PROJECT_ROOT` precedent; resolve relative paths against repo root BEFORE `realpath` (per Codex Fv5-1 + Codex v1 N1 catch — `os.path.abspath(relative_path)` anchors to CWD which is bug-prone); `commonpath`-based containment + POSIX repo-relative + case-sensitive exact match locked at plan v5 Contract 2.0.4 preserved.
- Per-bar artifact path format (currently `returns_per_bar.parquet` working assumption)
- Moment summary file location (extend `holdout_summary.json` vs new file)
- Smoke test data source (canonical OHLCV vs fully synthetic)
- Library-specific kurtosis value verification discipline (per cross-cycle 3-instance pattern recurrence; T1.5 implementation MUST empirically re-verify all alternative library values)

Each named sub-decision requires explicit Charlie register at decision-point if not pre-committed in v_final plan.

**Default posture:** non-execution awaiting Charlie register at each register-event boundary.

---

**End of plan v5. RATIFIED 2026-05-22 per Charlie register "Inline-fix Codex Fv5-1 + Fv5-2 → Charlie direct ratify v5".**

---

## §11 Task SEAL chain (post-ratify execution log)

- **T1.2 SEALED 2026-05-22** per Charlie register (cross-leg convergent APPROVE post-fix-iteration + post-extraction): `backtest/wf_lineage.py` (545 lines) + new `backtest/artifact_schema.py` (535 lines) + `tests/test_b_c_extended_schema.py` (1568 lines, 69 tests); per-domain tuple split + LineageContext-precursor + canonicalize function; all v1+v2 PFR findings adjudicated; 1838 tests pass + 99% coverage
- **T1.3 SEALED 2026-05-22** per Charlie register "(T1.3-SEAL-charlie-ratify) Charlie direct T1.3 SEAL ratify register" (cross-leg convergent APPROVE post-second-fix-iteration): `backtest/engine.py` (2158 lines; +191 from baseline) + `backtest/artifact_schema.py` (790 lines; LineageContext + canonicalize + FIX-M2 guard) + `tests/test_t1_3_registry_api.py` (2113 lines, 66 tests); FIX-H2 cost-config/registry alignment + FIX-B1-extension parent_run_id defensive + FIX-M2-extension Path('') guard; live DB migration fired (`cost_anchor_id` column added); all 3 PFR rounds adjudicated (v1 BLOCKING duck-typing + execution_config_path silent precedence → first fix; v2 BLOCKING cost-config divergence → second fix; v3 CONVERGENT APPROVE); 1904 tests pass + 84% combined coverage; 8 cumulative cross-model leg LOAD-BEARING instances within B-C-extended arc validated
- **T1.1 SEALED 2026-05-23** per Charlie register "charlie-direct-SEAL-ratify authorized" (cross-leg convergent APPROVE on `LineageContext.revalidate_for_write()` centralized structural pattern-breaker): `backtest/engine.py` (2743 lines; +585 from T1.3-SEAL baseline; `compute_per_bar_returns` + `compute_moments` + `write_per_bar_artifact` + 4 write-boundary defense-in-depth mirrors + `lineage_context.revalidate_for_write()` call at :1149 + DESIGN INVARIANT marker at :1133 replacing prior CONTRACT GAP) + `backtest/artifact_schema.py` (1069 lines; +279 from T1.3-SEAL baseline; SYS4-LATE-FILL `__post_init__` closed-set pair invariant + SYS5-REVALIDATE centralized 14-field tamper closure method) + `backtest/experiment_registry.py` (537 lines; T1.3 schema migration retained) + new `tests/test_t1_1_artifact_writer.py` (1826 lines, 80 tests) + new `tests/test_t1_1_sys_fix.py` (2946 lines, 143 tests covering SYS-fix-1 through SYS5 truth tables) + `tests/test_t1_3_registry_api.py` (2151 lines; +38 lines for SYS5 message updates on 2 pre-existing parent_run_id tamper tests); 9-iteration arc with 9 PFR rounds (v1 BLOCKING T_obs finite-return + WF fence → v2 BLOCKING registry persistence gap + atomicity → v3 F-systematic BLOCKING 3 third-level asymmetries → v4 SYS2 BLOCKING OR-vs-AND pair-completeness + mutated T_obs bypass → v5 SYS3-narrow BLOCKING `(None, "")` third-state → v6 CONVERGENT APPROVE on SYS4-hybrid synthesis + Mode A refuted Advisor `regime_key` broader-redesign claim → v7 CONVERGENT APPROVE on SYS4-hybrid implementation → v8 final-round-adversarial BLOCKING 5th asymmetry class STRICT field tamper via `object.__setattr__` bypassing frozen-dataclass guard + registry nullable TEXT silently accepting → v9 CONVERGENT APPROVE on `revalidate_for_write()` centralized structural pattern-breaker, Codex explicit "cycle-final APPROVE; no v10 finding predicted"); 2191 tests pass + zero regression; cumulative cross-model leg LOAD-BEARING extended to 14+ instances (6 within T1.1 arc + 8 cumulative pre-T1.1) within B-C-extended cycle validated; §35-adjacent observation evidence base now 2-cycle empirical (SYS4 producer-side LATE_FILL invariant + SYS5 `LineageContext.revalidate_for_write()` centralization is structural pattern-breaker over case-by-case enumeration) per Advisor v9 reaffirmation — codification deferred to B-C-extended cycle SEAL boundary per Charlie register option (c) anti-pre-emption preserved; 4 mirror sites at engine.py:1138-1148 (cost_anchor_id) / :1159-1170 (parent_run_id) / :1267-1282 (T_obs SYS3-B2) / :1320-1342 (LATE_FILL SYS3-B1) RETAINED as belt-and-suspenders per project defense-in-depth doctrine; Advisor v9 informational findings (F1 cosmetic T_obs error message + F2 LOW insert_run public + F3 LOW DESIGN INVARIANT marker + F4 INFO test coverage + F5 LOW t1_3 line updates) all non-blocking and folded into T1.6 documentation phase scope per cycle-SEAL deferral; F1 cosmetic eligible for T1.6 polish

**Plan ratify status:** v5 plan with 2 inline LOW fixes (Codex Fv5-1 commonpath-based containment + case-sensitivity policy at Contract 2.0.4; Codex Fv5-2 R3.1d §5.2 mapping table column 3 paraphrase labeling) is the final ratified plan version. No further reviewer rounds needed. Advance to T1.x implementation cycle entry per execution order T1.2 → T1.3 → T1.1 → T1.4 → T1.5 → T1.6 requires SEPARATE Charlie register-event boundary per anti-pre-emption discipline.
