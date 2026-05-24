# T1.5 Fixture / Smoke / Registry-integrity test suite — sub-plan v3.2 **RATIFIED v_final 2026-05-24** (Charlie R7a register; sub-plan LOCKED per §8.1 anti-pre-emption)

**Cycle:** T1.5 of B-C-extended Scope-B structural artifact-preservation refactor cycle
**Parent plan v5 (RATIFIED):** [`docs/superpowers/plans/2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md`](2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md)
**Execution order within parent:** T1.2 → T1.3 → T1.1 → T1.4 → **T1.5** → T1.6
**Prior task SEAL commits:** T1.2 + T1.3 + T1.1 bundle at `12dffde` (2026-05-23); T1.4 SEAL at `5a44ec6` (2026-05-23); T1.4 sub-plan v7 amendment at `b647860`; T1.4 v4 PFR LOW cleanup at `56fe413`
**Scope-class:** Path B narrow (deliverables (a) Fixture + (b) Smoke + (d) Registry integrity; deliverable (c) Canary DEFERRED per T1.4 SEAL coverage at [`tests/test_t1_4_backward_compat.py`](../../../tests/test_t1_4_backward_compat.py))
**Drafting modality:** γ Hybrid — orchestrator skeleton (§1, §2.4, §2.5, §3-§11) + `quant-research-advisor` subagent per-deliverable detail-fill (§2.1, §2.2, §2.3); integrated 2026-05-23 with orchestrator Mode A spot-verification PASS on 5 kurtosis empirical values + load-bearing file:line citations (per §2.5)

**Charlie register chain (2026-05-23):**
- T1.5 cycle ENTRY: AUTHORIZED
- Scope-class Path B: REGISTERED (a + b + d; c DEFERRED)
- Sub-plan v1 drafting fire: AUTHORIZED
- Subagent ratify for per-deliverable detail-fill: `quant-research-advisor` RATIFIED
- DS2 (smoke-test data-source lock): **RATIFIED 2026-05-24 — Option (i) canonical OHLCV slice** + Codex F-NEW off-by-one bar-count fix ADOPTed + Q5 gap (a) explicit acknowledgment ADOPTed + heavy-tail empirical archived (per "Option (i) + 同意must-ADOPT" Charlie register 2026-05-24)
- Q1 reading: **implicit (α) per DS2 = (i) entailment** ("same Smoke does both pipeline-通 + production-data validation" partially; heavy-tail axis exercised; NaN/zero-volume/gap-window axes deferred to §8.2 DS-NEW (e) successor cycle); explicit Charlie confirmation surfaceable on demand
- 2-leg BL-Y Phase 1 blind-lean DS2 reviewer round COMPLETED 2026-05-24 — Codex (Option i) + Advisor opus instance #2 (Option ii) DIVERGED on DS2 + Q1 reading; CONVERGED on Q5 gap (a) + Codex F-NEW off-by-one bar-count fix

---

## §1 Cycle scope statement + Path B scope register provenance

### §1.1 Path B scope decomposition (Charlie register Path B 2026-05-23)

Path B narrow scope ratified at Charlie register-event 2026-05-23 per [post-T1.4-SEAL handoff](/tmp/post_t1_4_seal_handoff_2026-05-23.md). Three deliverables IN SCOPE; one DEFERRED:

| T1.5 # | Deliverable | Status under Path B | Cross-reference |
|---|---|---|---|
| (a) | **Fixture test** | IN SCOPE — §2.1 | Contract 2.0.1 + 2.0.6 (a) |
| (b) | **Smoke test** | IN SCOPE — §2.2; **DS2 RATIFIED Option (i) canonical OHLCV slice 2026-05-24** | Contract 2.0.5 + 2.0.6 (b) |
| (c) | **Canary test** | DEFERRED — T1.4 SEAL implementation explicitly covers canary class; T1.5 sub-plan references [`tests/test_t1_4_backward_compat.py`](../../../tests/test_t1_4_backward_compat.py) with explicit non-duplication note (§4) | Contract 2.0.6 (c) — already verified at T1.4 SEAL |
| (d) | **Registry integrity test** | IN SCOPE — §2.3 | Contract 2.0.3 + 2.0.4 + 2.0.6 (d) |

### §1.2 Validation coverage scope

T1.5 implements **3 of 4** Contract 2.0.6 test classes (Path B subset). Aggregate Path B coverage target: validate (i) moment estimator correctness against 5 alternative implementations + (ii) end-to-end pipeline integrity for 1-3 synthetic candidates + (iii) registry triple-resolution with 5 fail-closed cases + 1 happy-path None-normalization.

(c) Canary class verification responsibility is fully discharged at T1.4 SEAL per Charlie register Path B 2026-05-23; T1.5 does NOT re-implement aggregate-CSV + aggregate-JSON + N-per-candidate byte-identity protection. Re-implementation would be wasteful duplication AND would risk introducing skew between two canary-class test surfaces.

### §1.3 Aggregate cycle outputs

- 3 test classes (one per Path B deliverable) at structured test file paths (per §2 detail)
- Expected cumulative test count: ~25-35 individual test methods across 3 classes (per subagent §2 draft sketch — locked at implementation)
- Full suite delta target: zero regression on T1.4 baseline of 2297 tests; T1.5 adds tests within Path B scope only
- All tests deterministic (explicit seeds; no random generator state)
- All tests hermetically isolated (DEFAULT_DB_PATH monkeypatch + tempdir per test method per T1.4 SEAL B3.4 pattern)

---

## §2 Engineering deliverables (per-deliverable test design)

### §2.1 (a) Fixture test design

#### 2.1.1 Scope

§2.1 verifies Contract 2.0.1 moment-estimator implementation correctness via the Contract 2.0.6 (a) fixture-test class. The test surface is intentionally narrow: prove the LOCKED scipy invocation deterministically returns γ4 = 3.000000 (raw standardized kurtosis, Gaussian-limit-equal) and γ3 = 0.000000 at the explicit fixture vector `[-1, 1, 0, 0, 0, 0]`, AND prove that all 5 enumerated PROHIBITED alternative implementations deterministically diverge from γ4 = 3.000000 by ≥ 0.5 (sufficient empirical separation to lock out silent library-default swaps). Out-of-scope: writer-boundary integration (§2.2 scope), `LineageContext.revalidate_for_write()` invariant (T1.1 SEAL coverage at [`tests/test_t1_1_sys_fix.py:2583`](../../../tests/test_t1_1_sys_fix.py) `TestSys5RevalidateForWriteDirectStrictFields`), and per-bar artifact SHA256 integrity (T1.2 scope already shipped at `check_b_c_extended_semantics_or_raise()`).

This test exists because of one specific historical risk: **the 3-instance orchestrator-adjudication-error pattern within the B-C-extended planning arc** (parent plan v5 §0 ll.23-29) included two numerical misattributions on these exact library defaults (v1 "5.5" wrong-scope; v3 "fisher=True 2.5" misattribution). The fixture test is the empirical receipt that the LOCKED implementation matches the spec at one specific input where all 6 plausible library invocations produce 6 different floats.

#### 2.1.2 Test inputs

**Vector:** `numpy.array([-1.0, 1.0, 0.0, 0.0, 0.0, 0.0])`, dtype `float64`, N=6. Hard-coded module-level constant; no random generator.

**Why this vector:** symmetric around mean=0 (so γ3 = 0 cleanly without bias-correction noise); finite N=6 produces strong empirical separation between bias-corrected and population formulas (e.g., scipy fisher=False bias=True = 3.0 vs scipy fisher=False bias=False = 5.5; a Δ of 2.5 — well beyond any tolerance band); contains zero-value bars (mirrors the legitimate flat-period structure in BTC OHLCV per CLAUDE.md "Known Data Characteristics" §3 zero-volume bars). Exactly the same vector enumerated at parent plan v5 Contract 2.0.6 (a) ll.173-185 — DO NOT alter at T1.5; alteration invalidates the 5 pre-computed PROHIBITED values.

**Seed discipline:** none required (vector is deterministic). Test MUST NOT call `np.random.seed()` or any RNG. If a future test author introduces RNG-driven sampling at this layer, they have left the fixture-test paradigm and entered smoke-test territory (route to §2.2).

#### 2.1.3 PASS assertions

Two assertions, both at `1e-12` absolute tolerance per parent plan v5 Contract 2.0.6 (a) line 175:

1. **γ4 PASS** [VERIFIED via Bash empirical at scipy 1.10.0, 2026-05-23 + orchestrator independent re-verification 2026-05-23]:
   ```python
   from scipy.stats import kurtosis
   import numpy as np
   _FIXTURE_VECTOR = np.array([-1.0, 1.0, 0.0, 0.0, 0.0, 0.0])
   result = kurtosis(_FIXTURE_VECTOR, fisher=False, bias=True, nan_policy='omit')
   assert abs(result - 3.0) < 1e-12, f"γ4 PASS failed: expected 3.0 ± 1e-12, got {result!r}"
   ```
   Empirical: `3.0` exactly at scipy 1.10.0 [VERIFIED].

2. **γ3 PASS** [VERIFIED via Bash empirical at scipy 1.10.0, 2026-05-23 + orchestrator independent re-verification 2026-05-23]:
   ```python
   from scipy.stats import skew
   result = skew(_FIXTURE_VECTOR, bias=True, nan_policy='omit')
   assert abs(result - 0.0) < 1e-12, f"γ3 PASS failed: expected 0.0 ± 1e-12, got {result!r}"
   ```
   Empirical: `0.0` exactly. (Symmetric vector → population skew = 0 trivially.)

**γ4 passing-band exclusion of 0.0** (Contract 2.0.6 (a) line 182):
   ```python
   assert abs(result - 0.0) > 0.5, (
       "γ4 PASS band must EXCLUDE 0.0 — 0.0 is the scipy fisher=True bias=True "
       "(default scipy) excess-kurtosis convention value for this vector. "
       "If the test accepts 0.0, the production γ4 implementation has silently "
       "drifted to the excess-kurtosis convention and the BLdP DSR consumer "
       "will compute (γ4 - 3) - 3 = -6 in place of the intended (γ4 - 3) = 0."
   )
   ```
This is a **separate method** from the PASS assertion above (not bundled). Two reasons: (i) per-method assertion attribution on failure surfaces the exact contract violated; (ii) future test author who relaxes the tolerance band can't silently swallow the 0.0-vs-3.0 confusion.

#### 2.1.4 FAIL assertions for 5 alternative implementations

Each of the 5 PROHIBITED implementations gets **its own independent test method** (do NOT bundle into a parametrize over the 5 — see §2.1.7 rationale). Each method computes the prohibited value at runtime and confirm-fails the PASS band:

[All 5 values empirically re-verified at scipy 1.10.0 + pandas 2.2.3 + HEAD `56fe413`, 2026-05-23 via Bash — orchestrator independent re-verification confirms subagent's empirical claims:]

| # | Test method name | Implementation | Empirical value | Δ from 3.0 |
|---|---|---|---|---|
| 1 | `test_fail_pandas_kurt_default` | `pd.Series(v).kurt()` | `2.5` [VERIFIED] | -0.5 |
| 2 | `test_fail_pandas_kurt_plus_3` | `pd.Series(v).kurt() + 3` | `5.5` [VERIFIED] | +2.5 |
| 3 | `test_fail_scipy_fisher_true_bias_true` | `scipy.stats.kurtosis(v, fisher=True, bias=True)` (scipy default) | `0.0` [VERIFIED] | -3.0 |
| 4 | `test_fail_scipy_fisher_true_bias_false` | `scipy.stats.kurtosis(v, fisher=True, bias=False)` | `2.5` [VERIFIED] | -0.5 |
| 5 | `test_fail_scipy_fisher_false_bias_false` | `scipy.stats.kurtosis(v, fisher=False, bias=False)` | `5.5` [VERIFIED] | +2.5 |

Each method's assertion shape:
```python
def test_fail_pandas_kurt_default(self) -> None:
    import pandas as pd
    prohibited = pd.Series(_FIXTURE_VECTOR).kurt()
    # Confirm-fail: deterministic separation from 3.0 by ≥ 0.5
    assert abs(prohibited - 3.0) >= 0.5, (
        f"FAIL-1 (pandas .kurt() default): expected divergence from 3.0 by ≥ 0.5, "
        f"got prohibited={prohibited!r}, |Δ|={abs(prohibited - 3.0)!r}. "
        f"If this assertion passes (i.e., pandas matches scipy fisher=False bias=True), "
        f"the library defaults have converged and this lockout test is no longer needed — "
        f"raise to Charlie register for Contract 2.0.1 spec update."
    )
    # Plus PASS-band negative: this implementation MUST NOT produce 3.0 ± 1e-12
    assert abs(prohibited - 3.0) > 1e-12, (
        f"FAIL-1 produced 3.0 ± 1e-12 — this is the LOCKED PASS value; "
        f"production has silently swapped implementations. Investigate."
    )
```

**Δ ≥ 0.5 lower bound rationale:** the smallest Δ across the 5 prohibited implementations is 0.5 (pandas `.kurt()` default = 2.5; scipy fisher=True bias=False = 2.5). 0.5 is the empirical "tightest" separation that ALL 5 satisfy AND that exceeds any plausible floating-point drift band. Tightening to ≥ 1e-12 would be wrong because some prohibited implementations may legitimately approach the PASS value asymptotically as N grows (e.g., bias-corrected → population at large N); fixture-N=6 gives strong empirical separation, but the contract is about identity-at-this-N, not asymptotic divergence.

**Independent test methods (not parametrize):** if one library upgrade changes pandas `.kurt()` default to match scipy fisher=False bias=True, the failure should fire as "FAIL-1" specifically, not as a generic "one of 5 alternative implementations no longer diverges." Independent test methods preserve failure attribution. Reviewer-leg precedent at [`tests/test_t1_4_backward_compat.py:223`](../../../tests/test_t1_4_backward_compat.py) `TestT1_4_A2_DomainFenceRejection` uses the same one-method-per-keyword-class pattern.

#### 2.1.5 scipy version precondition

Per Contract 2.0.1 line 61: "scipy ≥ 1.9 required for `nan_policy` keyword; fixture test fails closed if precondition not met."

**Implementation:**
```python
def test_scipy_version_precondition(self) -> None:
    """Gate: fail closed if scipy < 1.9 (nan_policy keyword unavailable).

    Empirical at sub-plan drafting: scipy 1.10.0 [VERIFIED].
    If scipy < 1.9, the entire fixture suite is invalid (PASS implementation
    cannot be invoked). Raise a clear error rather than letting per-test
    TypeError obscure the version mismatch.
    """
    import scipy
    from packaging.version import Version  # stdlib alternative: tuple-compare scipy.__version__.split('.')
    assert Version(scipy.__version__) >= Version("1.9"), (
        f"scipy {scipy.__version__} < 1.9: nan_policy keyword unavailable; "
        f"Contract 2.0.1 LOCKED implementation cannot run. "
        f"Upgrade scipy to ≥ 1.9 before invoking T1.5 fixture suite."
    )
```

**Suite-gate discipline:** add `pytestmark = pytest.mark.skipif(scipy.__version__ < "1.9", reason="...")` at module level OR run the precondition test FIRST (alphabetical ordering via `test_AAA_scipy_version_precondition` naming) so suite fails before per-PASS/FAIL methods produce confusing errors. Recommend the latter (explicit per-test method visible in pytest output) over the former (silently skipped, hard to detect in CI).

#### 2.1.6 γ3 (skew) coverage

**Surface judgment:** Contract 2.0.1 LOCKS γ3 via `scipy.stats.skew(returns_array, bias=True, nan_policy='omit')` (line 64). The fixture vector `[-1, 1, 0, 0, 0, 0]` is symmetric around mean=0, so γ3 = 0 trivially regardless of bias-correction convention — meaning the fixture-vector does NOT provide empirical separation between alternative skew implementations the way it does for kurtosis.

**Recommendation:** include γ3 PASS verification at the LOCKED implementation (§2.1.3 covers this) BUT do NOT enumerate PROHIBITED skew alternatives at this vector. They will all compute 0.0 trivially and the test would be tautological. **Defer γ3 PROHIBITED enumeration to a separate fixture vector** that is asymmetric (e.g., `[-2, -1, 0, 1, 1, 3]` or similar) — but this is **out-of-scope for T1.5 Path B narrow** (deliverable (a) per parent plan v5 §2.5 lock).

**If γ3 PROHIBITED enumeration is judged necessary:** flag as eligible-not-named for a future cycle (§2.1.8 sealing condition: "fixture test verifies γ4 lockout per Contract 2.0.6 (a); γ3 lockout deferred to separate Charlie register if/when needed"). The empirical-divergence risk for γ3 is materially lower than γ4 because the production DSR pathway is more sensitive to γ4 mis-attribution (excess vs raw confusion impacts BLdP DSR formula at γ4 - 3 term) than to γ3 bias-correction choice.

**For T1.5 v1:** ship γ3 PASS only; explicitly document γ3 PROHIBITED enumeration as a §2.1.8 exclusion. **DS5 named sub-decision at §8.2** — Charlie register at sub-plan PFR if DEFER recommendation is contested.

#### 2.1.7 Implementation discipline

**Test file:** `tests/test_t1_5_fixture_moments.py`

**Test class:** `TestT1_5_FixtureMomentImplementation`

**Method naming convention:**
- `test_AAA_scipy_version_precondition` — alphabetical sorting forces precondition gate first
- `test_pass_locked_gamma4_implementation` — LOCKED γ4
- `test_pass_locked_gamma3_implementation` — LOCKED γ3
- `test_pass_gamma4_band_excludes_excess_kurtosis_zero` — band exclusion of 0.0
- `test_fail_pandas_kurt_default` — FAIL-1
- `test_fail_pandas_kurt_plus_3` — FAIL-2
- `test_fail_scipy_fisher_true_bias_true` — FAIL-3 (scipy default)
- `test_fail_scipy_fisher_true_bias_false` — FAIL-4
- `test_fail_scipy_fisher_false_bias_false` — FAIL-5

Mirrors T1.4 conventions at [`tests/test_t1_4_backward_compat.py`](../../../tests/test_t1_4_backward_compat.py) per-class naming style.

**Module-level constants:**
```python
_FIXTURE_VECTOR = np.array([-1.0, 1.0, 0.0, 0.0, 0.0, 0.0])
_PASS_GAMMA4_EXPECTED = 3.0
_PASS_GAMMA3_EXPECTED = 0.0
_PASS_TOLERANCE_ABS = 1e-12
_FAIL_MIN_SEPARATION = 0.5
```

**DO NOT parametrize the 5 FAIL assertions** (rationale at §2.1.4): independent methods preserve failure attribution; per-test docstring carries the historical / library context. Parametrize discipline is appropriate at A1/A5 in T1.4 (39 per-candidate dirs is data-driven enumeration where every instance is structurally identical); the 5 prohibited implementations are NOT structurally identical (different libraries, different parameter spaces).

**Assertion idiom:** use `pytest.approx` ONLY for the PASS band (`assert result == pytest.approx(3.0, abs=1e-12)`); use plain `abs(x - y)` for FAIL separation bands (clearer failure messages on prohibited values).

#### 2.1.8 Explicit exclusions

T1.5 (a) Fixture test does NOT cover:

1. **Writer-boundary integration** — the assertion is about scipy/pandas invocation correctness at a fixed vector, NOT about engine.py producer code calling the right function. §2.2 Smoke test covers producer-side moment computation at end-to-end pipeline.
2. **`LineageContext.revalidate_for_write()` invariant** — already shipped at T1.1 SEAL [`tests/test_t1_1_sys_fix.py:2583`](../../../tests/test_t1_1_sys_fix.py). T1.5 (a) does NOT re-verify SYS5; cross-reference only.
3. **Per-bar artifact validation** (file-exists, SHA256-recompute, path-confinement, T_obs-alignment) — Contract 2.0.5 (a) lines 161-166 shipped at T1.2 `check_b_c_extended_semantics_or_raise()`. T1.5 (a) does NOT re-verify these; §2.2 covers end-to-end.
4. **γ3 PROHIBITED enumeration** at this vector (§2.1.6 rationale; eligible-not-named for separate register-event; DS5 at §8.2).
5. **Registry insertion of γ3/γ4/T_obs** — §2.3 scope.
6. **Backward-compat verification on legacy artifacts** — T1.4 SEAL coverage [`tests/test_t1_4_backward_compat.py`](../../../tests/test_t1_4_backward_compat.py).
7. **Cross-library asymptotic divergence checks** at varying N — out of fixture scope (varying N is closer to smoke / property-based testing; fixture is about identity at one fixed input).

#### 2.1.9 Cycle-pattern observations

**Library-version-empirical-revalidation discipline.** The 5 PROHIBITED values are empirically verified at scipy 1.10.0 + pandas 2.2.3 + HEAD `56fe413` (2026-05-23). The B-C-extended planning-arc 3-instance orchestrator-error pattern (parent plan v5 §0 ll.23-29) included two instances where library defaults were misattributed in spec documents. **Recommendation: at every scipy or pandas major-version upgrade (1.x → 2.x), re-run the empirical verification command** (`python3 -c "..."` in §2.1.4 prep) **and confirm the 5 values remain at the expected separations.** If any value drifts, the FAIL test method for that library will fire — that is the correct signal, but the lock-step orchestrator discipline is: confirm the drift is expected (library convention change) vs unexpected (test bug), then either update the spec (Charlie register) or fix the call site.

**Verify-once + lock vs revisit-per-upgrade split.** The PASS implementation (`scipy.stats.kurtosis(fisher=False, bias=True, nan_policy='omit')`) has stable semantics across scipy ≥ 1.9 and is verify-once at first ship; the LOCK is durable. The 5 PROHIBITED values are revisit-per-major-upgrade because library defaults occasionally change (e.g., pandas `.kurt()` historically went through bias-correction-default flip-flops; scipy fisher default changed in early 0.x versions). Document this asymmetry in the test module docstring so future cycle-author understands the maintenance contract.

**Cross-leg verification load-bearing precedent.** Parent plan v5 §0 cumulative pattern (3 orchestrator-error instances at ~75% per-iteration rate absent cross-leg verification) suggests Codex independent re-execution of the empirical values at PFR rounds is structurally required — NOT optional — for any T1.5 (a) PFR round. Pre-emptive verification at this draft (§2.1.3 + §2.1.4 [VERIFIED] tokens + orchestrator §2.5 independent re-verification) reduces but does not eliminate PFR-leg verification need.

**Anti-saturation observation.** §2.1 design includes 4 PASS/band/precondition tests + 5 FAIL tests = 9 test methods for one fixture vector. This is dense but each method has independent failure-attribution value (per §2.1.4 / §2.1.7 rationale). Resist consolidation pressure at T1.5 PFR rounds; consolidation collapses 5 library lockouts into 1 generic assertion that loses post-failure debugging signal.

---

### §2.2 (b) Smoke test design — DS2 RATIFIED Option (i) canonical OHLCV slice 2026-05-24

#### 2.2.1 Scope

§2.2 verifies that the **end-to-end pipeline** — engine entry point → moment computation → artifact writer → schema validator → registry triple-linkage insertion — produces conformant artifacts for 1-3 synthetic minimal candidates per parent plan v5 §2.5 T1.5 (b) lock. The test surface deliberately stays **integration-level**, NOT unit-level: §2.1 covers moment-formula correctness (unit), §2.3 covers registry-edge-case fail-closed branches (unit-ish), §2.2 verifies the connective tissue works on a realistic-shape input.

**Pass = artifact emitted at correct path + all 14 Contract 2.0.5 header fields present + `returns_per_bar.parquet` exists with verified SHA256 + T_obs matches finite-row count + γ3/γ4 computed within Gaussian-limit-adjacent bands + triple linkage `(hypothesis_hash, batch_id, run_id)` resolvable in registry.**

Out-of-scope (cross-reference): per-fixture moment value verification (§2.1); per-failure-case registry coverage (§2.3); backward compat verification (T1.4 SEAL [`tests/test_t1_4_backward_compat.py`](../../../tests/test_t1_4_backward_compat.py)); slice-aware writer signature verification (already covered at T1.1 SEAL by 4 mirror-site engine.py tests).

#### 2.2.2 Data-source: Option (i) canonical OHLCV slice LOCKED 2026-05-24 (rejected enumeration preserved at §2.2.2-historical)

**DS2 RATIFIED 2026-05-24:** Charlie registered **Option (i) canonical OHLCV slice** ("Option (i) + 同意must-ADOPT" register). Locked specification at §2.2.2-locked below; rejected enumeration ((ii) + (iii)) preserved at §2.2.2-historical per §2.2.9 discipline.

**Codex F-NEW ADOPTed 2026-05-24:** subagent v1 §2.2.2 bar-count claim of "175 hourly bars from 2023-08-01T00:00:00Z to 2023-08-08T07:00:00Z" is off-by-one — empirically verified **176 bars** actually present in canonical parquet at that window (orchestrator independent re-execution at HEAD `56fe413` 2026-05-24 per Codex F-NEW catch at 2-leg BL-Y reviewer round). Locked endpoint resolution: keep `2023-08-08T07:00:00Z` inclusive endpoint → **176 hourly bars** (corrected from 175). All consumers below reflect 176-bar count.

### §2.2.2-locked: Option (i) canonical OHLCV slice (LOCKED 2026-05-24)

---

**Option (i): Canonical OHLCV slice**

Source: `data/raw/btcusdt_1h.parquet` (canonical dataset; do NOT modify, per CLAUDE.md HARD CONSTRAINT "Data Integrity").

Slice: **176 hourly bars** from `2023-08-01T00:00:00Z` through `2023-08-08T07:00:00Z` inclusive both endpoints (7.33 days). Orchestrator independent re-execution at HEAD `56fe413` 2026-05-24 confirmed: 176 bars actually present + 0 zero-volume bars + 0 NaN closes in slice. (Subagent v1 claim of "175 hourly bars" was off-by-one per Codex F-NEW catch at 2-leg reviewer round; ADOPTed 2026-05-24.) 2023 chosen because:
- Post-2022 regime-holdout window (no leakage into regime-holdout integrity)
- Pre-2024 validation window (no leakage into split discipline per `config/environments.yaml`)
- No known data gaps in 2024+ per CLAUDE.md "Known Data Characteristics" §3
- 2020-2023 contain the 31 known missing hours + 3 zero-volume bars; 2023-08 window selected to avoid these structural anomalies (require verification at DS2 register: grep `data/quality/` validation reports for 2023-08 anomaly absence)

**Downstream consequences if Option (i) locks:**
- Real-data return distribution preserves heavy-tail BTC structure; γ3/γ4 PASS band must accommodate empirical (probably γ4 in `[5, 20]` range for hourly returns over 176 bars under log-return basis `np.log(close).diff()`; pct_change basis `close.pct_change()` yields slightly different empirical γ4 by ~0.05-0.20 per v4 PFR-rule-Y Advisor DEFECT-3 empirical 2026-05-24; γ3 may be non-zero); see §2.2.4 calibration discussion
- scipy precondition gate fires at module level (§2.1.5 pattern)
- Warmup boundary handling: smoke strategy MUST have `warmup_bars ≤ 50` (leaves ≥ 125 post-warmup bars for T_obs); engine MUST exclude warmup bars from γ3/γ4/T_obs per CLAUDE.md HARD CONSTRAINT "NEVER compute metrics including the warmup period"
- Parquet I/O: read once from canonical path via existing `bt_parquet_feed` adapter; write to tempdir per §2.2.7 isolation
- Fixture-window-stability over reproducibility: pick window-start by date (`pd.Timestamp('2023-08-01T00:00:00Z')`), NOT by row-index (row-index drifts as new incremental data appends to canonical parquet)

**Risk:** if Binance Vision re-curates 2023 historical data (extremely rare but documented at parent plan v5 §8 "Backtrader determinism risk" precedent), bytes change → test fixture drifts. Mitigate via dataset-snapshot SHA256 assertion in test setUp (compare current canonical parquet SHA256 against locked fixture-time SHA256; fail closed if mismatch).

---

### §2.2.2-historical: rejected options enumeration (preserved per §2.2.9 discipline)

The following options were enumerated at v1 drafting and considered by Charlie at DS2 register-event 2026-05-24. Charlie ratified Option (i) above; Options (ii) and (iii) are preserved here as historical record per §2.2.9 discipline for future audit / cycle-pattern reference.

**Option (ii): Fully synthetic OHLCV**

Source: deterministic generator function exposed at `tests/conftest.py` or test-local helper:

```python
def _make_synthetic_ohlcv(
    *, n_bars: int = 176, seed: int = 1557, start: datetime = datetime(2023, 8, 1, tzinfo=timezone.utc)
) -> pd.DataFrame:
    """Generate deterministic synthetic OHLCV for smoke testing.

    Returns:
        DataFrame with [open_time_utc, open, high, low, close, volume, source, ingested_at_utc]
        columns matching canonical parquet schema. Deterministic via fixed seed.
    """
    rng = np.random.default_rng(seed)
    log_returns = rng.normal(loc=0.0, scale=0.01, size=n_bars)  # ~1% hourly vol
    close = 25000.0 * np.exp(np.cumsum(log_returns))
    # ... construct OHLC from close + intra-bar synthetic high/low ...
```

**Downstream consequences if Option (ii) locks:**
- Maximum reproducibility (same seed → same bytes forever; no canonical-data-drift risk)
- Loses real BTC heavy-tail structure (synthetic Gaussian returns will produce γ4 close to 3.0 — Gaussian limit — which is the LOCKED PASS value at §2.1.3 BUT happens to coincide with the production γ4 of a true Gaussian process; this is a feature not a bug for smoke purposes BUT means smoke does not exercise the heavy-tail-handling code path that production hits)
- γ3/γ4 PASS band can be tight: synthetic Gaussian over N=176 should produce γ4 ∈ [2.3, 3.7] with high probability (empirical N=176 sampling distribution from Gaussian; orchestrator independent re-verification at seed=1557 N=176 2026-05-24: γ4 = 3.61); test can assert `2.0 < γ4 < 4.5` defensively
- T_obs alignment trivial (no NaN injection unless explicit; warmup behavior tested by including known warmup bars in the synthetic series)
- Parquet I/O: write synthetic to tempdir, read via `bt_parquet_feed`; full write+read roundtrip exercised
- Generator function signature surface is a sub-decision: should it accept `regime_archetype` parameter to inject bear / bull / sideways shapes? If yes, that opens a Pandora's box of synthetic-regime-design decisions; if no, smoke covers exactly one regime shape (Gaussian) which is narrow

**Risk:** smoke passes on synthetic but production code path hits a heavy-tail edge case that smoke doesn't exercise. Cross-cycle precedent: T1.4 B3.4 smart-mock fidelity gap — Codex caught a row-shape invariant violation that the smart-mock did not exercise (per parent plan v5 §0 v2 PFR observations adjacent). Synthetic data has the SAME risk class as smart-mock at registry layer.

---

**Option (iii): Hybrid (real prices + synthetic perturbation)**

NOT RECOMMENDED. Parent plan v5 §9 framing is binary (canonical OHLCV vs fully synthetic). Hybrid combines weaknesses of both — loses bit-reproducibility of (ii) AND loses canonical-data-snapshot guarantee of (i) — while gaining nothing concrete. **Flag as out-of-scope at DS2 register-event;** if Charlie sees a use case, separate register required.

---

#### 2.2.3 Synthetic candidate design

"1-3 minimal candidates" per parent plan v5 §2.5. **Recommendation: N=2** — provides triple-linkage uniqueness coverage (two candidates with same batch_id → different hypothesis_hash → different run_id, exercising the 3-axis primary-key resolution at §2.5 below) while remaining minimal.

Per candidate, the smoke test constructs:

```python
@dataclass
class _SmokeCandidate:
    strategy_id: str            # e.g., "smoke_sma_5_20" / "smoke_sma_10_30"
    hypothesis_hash: str        # canonical DSL hash; pre-computed at fixture-time
    dsl_fragment: dict          # minimal DSL with one factor + threshold + side
    params: dict                # strategy params
    expected_artifact_path: Path  # data/phase2c_evaluation_gate/<run_id>/<hypothesis_hash>/
```

**Recommended candidates (placeholder; align with DS2 source-choice):**
1. SMA crossover (fast_period=5, slow_period=20): hand-derived expected trade count at 176-bar pre-warmup window (post-warmup ≈ 156 bars after `SMACrossover.WARMUP_BARS = slow_period = 20` per `strategies/baseline/sma_crossover.py:51`); γ3/γ4 from post-warmup return series
2. SMA crossover (fast_period=10, slow_period=30): different warmup boundary, different trade count (post-warmup ≈ 146 bars after `SMACrossover.WARMUP_BARS = slow_period = 30` per `strategies/baseline/sma_crossover.py:51`)

**CONTRACT GAP — warmup convention divergence (per v3.1 PFR-rule-Y v4 Advisor DEFECT-1 disclosure 2026-05-24 + v5 PFR-rule-Y Advisor DEFECT-MICRO-3 taxonomy re-adjudication 2026-05-24; severity MEDIUM; tag re-classified from DESIGN INVARIANT to CONTRACT GAP per CLAUDE.md L297-300 strict-reading where trigger-condition framing dominates):** §2.2.3 candidates LOCK to hand-written `strategies.baseline.sma_crossover.SMACrossover` per implementation choice at L338 below (`WARMUP_BARS = slow_period` per L51).

**Trigger condition (CONTRACT GAP semantic per CLAUDE.md L297-300):** if T1.6 or future cycle refactors smoke candidates to DSL-compiled crossover (`strategies/dsl_compiler.py` warmup convention uses `factors.registry.max_warmup(factors_used)` per L642+ which uses `period - 1` registry convention per `factors/moving_averages.py:83/93`), post-warmup count would shift by 1 bar (SMA(5/20) → 157 not 156; SMA(10/30) → 147 not 146) → §2.2.4 PASS band recalibration required + new test fixture or assertion mechanism to enforce the locked convention. 1-bar drift risk for any DSL refactor; fresh Charlie register-event required to authorize such refactor + concomitant §2.2.4 PASS band recalibration.

Both share the canonical Phase 1B baseline DSL shape (per `strategies/dsl_baselines/`) — no novel DSL feature exercise (that's T1.6 + T1.5 (a) territory).

**Strategy class:** reuse existing `strategies.baseline.sma_crossover.SMACrossover` per the precedent at T1.4 B3.1 LC-positive substantive verification (uses SMACrossover at [`tests/test_t1_4_backward_compat.py:898`](../../../tests/test_t1_4_backward_compat.py)+) — proven smoke-test-friendly and well-understood expected behavior.

**Engine entry point:** `run_backtest(lineage_context=<canonical LineageContext>, ...)` per the chain-propagation verified at T1.4 B3.1 v4 SEAL-eve. Do NOT bypass to direct `_write_to_registry(...)` call — that's `§2.3` registry-integrity scope and would miss the engine→writer chain coverage.

#### 2.2.4 PASS criteria

For each of N synthetic candidates:

**Artifact emission:**
1. File exists at `data/phase2c_evaluation_gate/<run_id_or_batch_dir>/<hypothesis_hash>/` (artifact dir per Contract 2.0.5 line 138); use tempdir override per §2.2.7 isolation
2. Per-bar return series file `returns_per_bar.parquet` exists in the same dir (Contract 2.0.5 line 139 working assumption locked at T1.2 — verify lock not changed at T1.5 fixture-time via grep against T1.2 SEAL impl)
3. Moment-summary JSON exists at the location locked at T1.2 (extend `holdout_summary.json` vs new `moment_summary.json` per parent plan v5 line 140 — verify lock via grep at T1.5 fixture-time)

**Header field completeness (14 Contract 2.0.5 fields):**

```python
expected_header_fields = [
    "artifact_schema_version",  # field 1 → "b_c_extended_v1"
    "run_id",                   # field 2
    "hypothesis_hash",          # field 3
    "source_batch_id",          # field 4
    "parent_run_id",            # field 5 → Optional[str]; can be None for smoke candidate
    "regime_key",               # field 6
    "engine_commit",            # field 7
    "current_git_sha",          # field 8
    "execution_config_path",    # field 9 → canonicalized POSIX
    "execution_config_sha256",  # field 10
    "parquet_data_sha256",      # field 11
    "cost_anchor_id",           # field 12 → mapping-resolved
    "returns_per_bar_path",     # field 13 → relative to artifact's containing dir
    "returns_per_bar_sha256",   # field 14
]
# 14 fields total — assert len(expected_header_fields) == 14 as anti-drift guard
```

**Per-bar artifact integrity (Contract 2.0.5 lines 161-166):**
- File-exists: `Path(artifact_dir / header["returns_per_bar_path"]).is_file()` → True
- Path-confinement: resolved path is `commonpath`-contained in artifact dir (no `../` escape; assert via `os.path.commonpath` per T1.3-B canonicalization precedent at [`backtest/artifact_schema.py`](../../../backtest/artifact_schema.py) `canonicalize_execution_config_path()`)
- SHA256-recompute: open parquet bytes, `hashlib.sha256(content).hexdigest() == header["returns_per_bar_sha256"]`
- T_obs alignment: read parquet → count finite-row returns → equal `header["T_obs"]`

Most of these are already exercised by `check_b_c_extended_semantics_or_raise()` at T1.2 SEAL ([`backtest/artifact_schema.py`](../../../backtest/artifact_schema.py)); the smoke test should INVOKE that validator on the emitted artifact and assert it does NOT raise. Avoid duplicating the validator logic in smoke test code — that creates a second source of truth that can drift.

**γ3/γ4 PASS bands (calibration over 1-3 candidates is intrinsically loose):**

Surface judgment: with N=1-3 candidates × 176 pre-warmup bars → ~146-156 post-warmup bars (depending on candidate warmup_bars; SMA (fast_period=5, slow_period=20) → 156 post-warmup; SMA (fast_period=10, slow_period=30) → 146 post-warmup) at hourly resolution from real BTC (Option i) OR synthetic Gaussian (Option ii), expected γ4 distributions are:
- Real BTC hourly 2023-08 (Option i, ~heavy-tail empirical at γ4 ≈ 13.73 on full 176-bar window per orchestrator Mode A re-verification 2026-05-24 under log-return basis `np.log(close).diff()` producing N=175 returns; pct_change basis `close.pct_change()` yields γ4 ≈ 13.89 per v4 PFR-rule-Y Advisor DEFECT-3 empirical 2026-05-24): γ4 ∈ `[3, 25]` plausible on post-warmup subset; LOWER bound assertion `γ4 ≥ 2.0` (excludes pathologically platykurtic implementations); UPPER bound assertion `γ4 ≤ 50` (excludes runaway-tail bugs)
- Synthetic Gaussian (Option ii): γ4 ∈ `[2.3, 3.7]` with high probability over N=176 (empirical at seed=1557 N=176: γ4 = 3.61 per orchestrator re-verification 2026-05-24); assertion `γ4 ∈ [2.0, 4.5]` defensive
- γ3 (skew) under both options: `|γ3| ≤ 5.0` defensive (real BTC may show modest skew; synthetic Gaussian centered on 0)

**Calibration over 1-3 candidates is LOOSE — recommend `assert isfinite(γ4) AND γ4 > 0` as the durable assertion**, with the band ranges above as defensive-only (catches runaway computational bug, not statistical regression). The smoke test is structurally-not-statistically calibrated; tight γ4 band assertions belong at §2.1 fixture vector, not §2.2 smoke.

#### 2.2.5 Triple linkage end-to-end check

After artifact emission, query `experiments.db.runs`:

```python
import sqlite3
conn = sqlite3.connect(str(tmp_db_path))
conn.row_factory = sqlite3.Row
row = conn.execute(
    "SELECT * FROM runs WHERE hypothesis_hash = ? AND batch_id = ? AND run_id = ?",
    (candidate.hypothesis_hash, candidate.source_batch_id, candidate.run_id),
).fetchone()
assert row is not None, (
    f"Triple linkage resolution failed for candidate {candidate.strategy_id!r}: "
    f"(hypothesis_hash={candidate.hypothesis_hash!r}, batch_id={candidate.source_batch_id!r}, "
    f"run_id={candidate.run_id!r}) not in runs table."
)
```

**End-to-end-vs-unit split:** §2.2 only verifies that one happy-path triple-linkage query returns one row. The 5 failure modes (duplicate run_id, missing hypothesis_hash, missing batch_id, mismatched cost_anchor_id, un-mapped execution_config_path) are §2.3 scope and use direct `_write_to_registry()` calls rather than end-to-end engine invocation. Do NOT duplicate failure-mode coverage at §2.2.

#### 2.2.6 cost_anchor_id end-to-end check

Contract 2.0.4 canonicalization must fire through the engine entry point + reach the registry insert. Assertion per candidate:

```python
assert row["cost_anchor_id"] == expected_cost_anchor, (
    f"cost_anchor_id end-to-end mismatch: candidate {candidate.strategy_id!r} "
    f"with execution_config_path={candidate.execution_config_path!r} "
    f"expected cost_anchor_id={expected_cost_anchor!r}, got {row['cost_anchor_id']!r}"
)
```

For smoke, recommend `execution_config_path = "config/execution.yaml"` → `cost_anchor_id = "legacy_perp_inspired_7bps_v0"` (default mapping; lowest novelty). DO NOT use `config/execution_phaseb_spot_15bps.yaml` at smoke — that's the formal Phase B Tier 5/6 anchor and using it in a smoke test creates conceptual confusion about whether smoke artifacts have promotion-relevance. (They don't, but the cost_anchor_id label leaks naming-namespace into smoke output.)

Integrates with §2.2.4 PASS criteria via field 12 of Contract 2.0.5 verification.

#### 2.2.7 Implementation discipline

**Test file:** `tests/test_t1_5_smoke_end_to_end.py`

**Test class:** `TestT1_5_SmokeEndToEndPipeline`

**Hermetic isolation (CRITICAL per T1.4 B3.4 precedent at [`tests/test_t1_4_backward_compat.py:813`](../../../tests/test_t1_4_backward_compat.py)+):**

Two mechanisms required:

1. **Tempdir for artifact output:** use pytest `tmp_path` fixture; pass via engine entry-point's artifact-dir parameter (lock the parameter name at DS2 register-event — depends on T1.1 SEAL writer signature).
2. **DEFAULT_DB_PATH monkeypatch for registry:** per Codex F1 v3 PFR ADOPT at T1.4 B3.4 ([`backtest/experiment_registry.py:46`](../../../backtest/experiment_registry.py) `DEFAULT_DB_PATH`; resolved at call-time in `get_connection(None)` at line 187):

```python
def test_smoke_one_candidate(self, tmp_path, monkeypatch):
    from backtest.experiment_registry import create_table
    import backtest.experiment_registry as registry_mod

    tmp_db = tmp_path / "smoke.db"
    # Initialize schema
    conn = sqlite3.connect(str(tmp_db))
    create_table(conn)
    conn.close()

    # Monkeypatch DEFAULT_DB_PATH BEFORE any code that calls get_connection(None)
    monkeypatch.setattr(registry_mod, "DEFAULT_DB_PATH", tmp_db)

    # ... engine invocation ...
```

**Pollution prevention:** if smoke test writes ANY artifact under `data/phase2c_evaluation_gate/` (not under tempdir), that's a test bug — pytest worker concurrency + future test runs would interfere. Add an explicit assertion at test teardown:

```python
def teardown_method(self):
    # Verify no smoke artifacts leaked into canonical phase2c_evaluation_gate namespace
    canonical_gate_dir = _REPO_ROOT / "data" / "phase2c_evaluation_gate"
    for child in canonical_gate_dir.iterdir():
        assert not child.name.startswith("smoke_"), (
            f"Smoke test polluted canonical namespace: {child}. "
            f"All smoke artifacts must write to tempdir."
        )
```

**Parametrize discipline:** if N=2 candidates, do NOT parametrize the whole smoke flow over candidates (each parametrize instance runs engine end-to-end → 2x cost). Instead, run engine once over both candidates within one test method + assert per-candidate via loop, OR use shared `setup_class` to amortize engine setup. For T1.5 v1 implementation, recommend single-test-method-with-loop pattern (clearest failure attribution; engine cost is dominated by data loading, not by candidate count).

#### 2.2.8 Explicit exclusions

T1.5 (b) Smoke test does NOT cover:

1. Per-fixture moment value verification at canonical vector (§2.1 scope; smoke uses bands not equalities)
2. Per-failure-case registry coverage (§2.3 scope; smoke only happy-path)
3. Backward compat verification on legacy artifacts (T1.4 SEAL [`tests/test_t1_4_backward_compat.py`](../../../tests/test_t1_4_backward_compat.py))
4. Slice-aware writer signature verification (T1.1 SEAL `engine.py:1133-1148` DESIGN INVARIANT marker + 4 mirror sites)
5. Walk-forward integration (Contract 2.0.5 + T1.3 opt-out per γ-1 verified at T1.4 B3.3 — smoke uses `run_backtest()` single-run path only)
6. Regime-holdout integrity (Phase 2A scope; smoke artifact does NOT exercise regime-holdout gate)
7. **Per-bar artifact validator logic itself** — smoke INVOKES `check_b_c_extended_semantics_or_raise()` but does not re-implement or unit-test it (T1.2 SEAL scope)
8. **Production-data smoke** (running smoke against `phase4_forward_2026_15bps_v1` candidates) — out of T1.5 Path B narrow; would duplicate T1.4 A1+A6 coverage from the other direction

#### 2.2.9 DS2 register-event gating (RESOLVED 2026-05-24)

**Current state:** DS2 RATIFIED Option (i) per Charlie register "Option (i) + 同意must-ADOPT" 2026-05-24. v2 sub-plan reflects locked Option (i) specification at §2.2.2-locked above; rejected enumeration ((ii) + (iii)) preserved at §2.2.2-historical below.

**Historical record (pre-ratify framing; preserved for audit):** prior to Charlie DS2 register-event, v1 reviewer dispatches were gated on this HARD CONSTRAINT; v1 PFR rounds were authorized to proceed on the DS2 PLACEHOLDER provided the following conditions were met:

1. §2.2.2 enumeration (3 options + downstream consequences) is complete and unbiased
2. Per-option PASS criteria implications are surfaced (γ3/γ4 band tightness; SHA256 fixture-time pin)
3. Hybrid is explicitly out-of-scope (no Charlie register required to reject)
4. §2.2.10 cross-cycle recommendation framing (T1.4 B3.4 smart-mock precedent) is included

**Discharged actions post-Charlie-DS2-register (2026-05-24):** v1 → v2 integration replaced §2.2.2 enumeration with locked Option (i) section + preserved (ii)/(iii) enumeration as historical record at §2.2.2-historical per discipline above. Subsequent v2 → v3 + v3 → v3.1 fixes applied via PFR-rule-Y v2/v4 cycles per Charlie register chain.

#### 2.2.10 Cycle-pattern observations

**Synthetic-vs-real-data trade-off recommendation framing.** The T1.4 B3.4 smart-mock fidelity gap (Codex caught a row-shape invariant violation at the smart-mock layer; verified in parent plan v5 §0 cumulative-arc observation context) is direct empirical precedent that synthetic / mock data structurally underexercises production code paths. Apply to DS2 decision:

- **If Charlie picks Option (i) canonical OHLCV:** smoke exercises real heavy-tail distribution; risk shifts to canonical-data-drift (mitigated via SHA256 snapshot assertion at test setUp); higher fidelity, more brittleness
- **If Charlie picks Option (ii) fully synthetic:** smoke exercises only Gaussian-shaped returns; risk shifts to smart-mock-class fidelity gap; lower brittleness, lower fidelity
- **If Charlie picks Option (iii) hybrid:** worst of both (NOT recommended; flag at register)

**Recommendation framing (no lock — preserve trade-off for Charlie):** the T1.4 B3.4 precedent does NOT cleanly favor one direction. Smart-mock fidelity gap argued for "use real data shapes;" but real-data tests have caused more cross-cycle nondeterminism brittleness than smart-mock tests. The decision is a values trade-off (fidelity-vs-determinism), not a verdict.

**Subagent structural lean (DISCOUNTED per Mode A risk):** Option (i) canonical OHLCV slice with SHA256-snapshot setUp assertion — aligned with parent plan v5 §9 "Smoke test data source: canonical OHLCV vs fully synthetic; lock at T1.5" framing where canonical is named first; aligned with T1.4 SEAL's preference for real-data hash-verification over smart-mock substitutes. BUT discount this lean ~85% per Advisor Mode A track record on data-source decisions; route to Charlie register with neutral enumeration.

**Cycle-pattern: smoke-test scope creep risk.** Future cycles may pressure to extend smoke from "1-3 minimal candidates" to "all 39 phase4 candidates" — that's NOT smoke, that's canary or backward-compat (T1.4 SEAL). Hold the line at T1.5 SEAL boundary: 1-3 candidates per parent plan v5 §2.5; scope expansion requires separate Charlie register.

**Codex `[VERIFIED]` token convention reminder.** Parent T1.4 §9 codified that Codex `[VERIFIED]` tokens are reliable evidence within tokenized scope (0 hallucinations within tokenized verification claims across recent arc); Advisor `[VERIFIED]` tokens are NOT reliable evidence. At §2.2 PFR rounds, expect Codex independent re-execution of any DS2-option file:line claim; orchestrator should pre-verify [VERIFIED] tokens on data-source claims (paths, dataset properties, gap-window-absence) to reduce PFR iteration cost.

---

### §2.3 (d) Registry integrity test design

#### 2.3.1 Scope

§2.3 verifies registry triple-linkage resolution + 5 failure-mode fail-closed branches + 1 happy-path None-normalization per parent plan v5 Contract 2.0.6 (d). Test surface is **unit-level at the `_write_to_registry()` boundary** — exercises the SQL insert + Contract 2.0.4 canonicalization + mapping-lookup logic directly on a hermetic temp `experiments.db`, NOT via engine entry point (that's §2.2 scope).

The 5 failure cases are non-overlapping fail-closed branches; each tests one specific defensive path. Plus the happy-path None-normalization verifies Contract 2.0.4 interpretation (b) at the canonical entry shape (no LineageContext, no explicit `execution_config_path` → resolves to legacy default).

Out-of-scope (cross-reference): end-to-end engine→registry flow (§2.2 scope); per-bar artifact SHA256 verification (T1.2 scope at `check_b_c_extended_semantics_or_raise()`); regime-holdout-passed semantics (T1.3 + Phase 2A scope); LineageContext `revalidate_for_write()` field-tamper coverage (T1.1 SEAL at [`tests/test_t1_1_sys_fix.py:2583`](../../../tests/test_t1_1_sys_fix.py) `TestSys5RevalidateForWriteDirectStrictFields`).

#### 2.3.2 Triple-resolution happy-path

Insert one row with full lineage context populated; query by `(hypothesis_hash, batch_id, run_id)`; assert exactly one row returned; verify each of 14 Contract 2.0.5 header fields persisted correctly.

```python
def test_triple_resolution_happy_path(self, tmp_path, monkeypatch):
    from backtest.engine import _write_to_registry
    from backtest.artifact_schema import LineageContext
    import backtest.experiment_registry as registry_mod
    from backtest.experiment_registry import create_table

    tmp_db = tmp_path / "triple.db"
    conn = sqlite3.connect(str(tmp_db))
    create_table(conn)
    conn.close()
    monkeypatch.setattr(registry_mod, "DEFAULT_DB_PATH", tmp_db)

    lc = LineageContext(
        run_id="triple-run-id",
        hypothesis_hash="triple-hash",
        source_batch_id="triple-batch",
        regime_key="v2.regime_holdout",
        engine_commit="abc123",
        current_git_sha="def456",
        execution_config_path="config/execution_phaseb_spot_15bps.yaml",
        execution_config_sha256="sha256:exec",
        parquet_data_sha256="sha256:parquet",
        returns_per_bar_path="returns_per_bar.parquet",
        returns_per_bar_sha256="sha256:rpb",
        T_obs=100,
        parent_run_id=None,
    )
    args = _make_minimal_write_args(run_id="triple-run-id")
    args["db_path"] = tmp_db
    args["lineage_context"] = lc
    args["hypothesis_hash"] = "triple-hash"
    args["batch_id"] = "triple-batch"

    _write_to_registry(**args)

    # Triple-linkage query: WHERE hypothesis_hash = ? AND batch_id = ? AND run_id = ?
    conn = sqlite3.connect(str(tmp_db))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM runs WHERE hypothesis_hash = ? AND batch_id = ? AND run_id = ?",
        ("triple-hash", "triple-batch", "triple-run-id"),
    ).fetchall()
    conn.close()

    assert len(rows) == 1, f"Triple-linkage query must return exactly 1 row, got {len(rows)}"
    row = rows[0]

    # Field-by-field verification of 9 new T1.x columns (Contract 2.0.5 + T1.3 alignment)
    assert row["cost_anchor_id"] == "spot_realistic_15bps_v1"  # mapping-resolved per LC
    assert row["regime_key"] == "v2.regime_holdout"
    assert row["current_git_sha"] == "def456"
    assert row["execution_config_path"] == "config/execution_phaseb_spot_15bps.yaml"
    assert row["execution_config_sha256"] == "sha256:exec"
    assert row["parquet_data_sha256"] == "sha256:parquet"
    assert row["returns_per_bar_path"] == "returns_per_bar.parquet"
    assert row["returns_per_bar_sha256"] == "sha256:rpb"
    assert row["T_obs"] == 100
    # ... plus existing Phase 1A/2A fields (strategy_name, metrics, etc.)
```

**Use existing `_make_minimal_write_args()` helper** mirroring T1.4 pattern at [`tests/test_t1_4_backward_compat.py:131`](../../../tests/test_t1_4_backward_compat.py) — reuse the proven minimal-args dict + add LineageContext via `args["lineage_context"] = lc`.

#### 2.3.3 Failure case 1: Duplicate `run_id`

Per [`backtest/experiment_registry.py:56`](../../../backtest/experiment_registry.py) `run_id TEXT PRIMARY KEY` — SQLite enforces uniqueness; second insert with same `run_id` fires `sqlite3.IntegrityError` ("UNIQUE constraint failed: runs.run_id") from the INSERT statement.

```python
def test_failure_1_duplicate_run_id(self, tmp_path, monkeypatch):
    # ... setup tmp_db + monkeypatch as above ...

    args = _make_minimal_write_args(run_id="dup-run-id")
    args["db_path"] = tmp_db

    # First insert: succeeds
    _write_to_registry(**args)

    # Second insert with same run_id: must fail closed
    args2 = _make_minimal_write_args(run_id="dup-run-id")  # same run_id
    args2["db_path"] = tmp_db

    with pytest.raises((sqlite3.IntegrityError, ValueError)) as exc_info:
        _write_to_registry(**args2)

    # Error message must identify the duplicated run_id for forensic clarity
    assert "dup-run-id" in str(exc_info.value) or "UNIQUE" in str(exc_info.value), (
        f"Duplicate run_id failure must surface run_id value or UNIQUE constraint in message; "
        f"got: {exc_info.value!r}"
    )
```

**Exception class judgment:** raw `sqlite3.IntegrityError` would propagate unless `_write_to_registry()` wraps it. Test accepts `(sqlite3.IntegrityError, ValueError)` tuple — preserve flexibility for T1.x implementation choices. Recommend test asserts the tuple per Codex F1 v2 PFR exception-class precedent at T1.4 A2.

**Error message content assertion:** assert run_id value OR "UNIQUE" present (don't lock specific wording — wording is engine internal; the contract is "operator can diagnose which row collided"). Tighter assertions are §2.3.13 belt-and-suspenders eligibility, not v1 requirement.

#### 2.3.4 Failure case 2: Missing `hypothesis_hash`

Per CLAUDE.md "Experiment Tracking" `hypothesis_hash` is a required field for Phase 2+ runs. **Surface judgment: current [`backtest/experiment_registry.py:91`](../../../backtest/experiment_registry.py) declares `hypothesis_hash TEXT` without `NOT NULL` constraint** — SQLite allows NULL insertion silently. The fail-closed behavior must be enforced at the engine `_write_to_registry()` layer, NOT at the SQL constraint layer.

```python
def test_failure_2_missing_hypothesis_hash(self, tmp_path, monkeypatch):
    # ... setup ...

    args = _make_minimal_write_args(run_id="missing-hh-run-id")
    args["db_path"] = tmp_db
    args["hypothesis_hash"] = None  # missing
    args["batch_id"] = "some-batch"  # present

    with pytest.raises(ValueError) as exc_info:
        _write_to_registry(**args)

    msg = str(exc_info.value)
    assert "hypothesis_hash" in msg, (
        f"Missing hypothesis_hash failure must identify the field name; got: {msg!r}"
    )
    # NOT raised as silent NULL insertion — defensive verification
    conn = sqlite3.connect(str(tmp_db))
    rows = conn.execute("SELECT * FROM runs WHERE run_id = ?", ("missing-hh-run-id",)).fetchall()
    conn.close()
    assert len(rows) == 0, (
        f"Failure case 2 must NOT silently insert NULL hypothesis_hash row; "
        f"got {len(rows)} rows with run_id='missing-hh-run-id'"
    )
```

**Surface gap [UNVERIFIED]:** subagent did NOT independently verify that `_write_to_registry()` currently rejects `hypothesis_hash=None`. The current engine code shows hypothesis_hash conflict-checks against LineageContext but does not show a None-rejection at the scalar pathway. **This test may CURRENTLY FAIL on T1.4 SEAL HEAD** — if so, that is a GAP in T1.3 implementation that T1.5 surfaces; route to Charlie register for engineering fix (NOT T1.5 in-scope corrective). Flag at PFR rounds; verify via Codex independent grep before locking the test's expected behavior. **DS8 named sub-decision at §8.2.**

**Alternative spec interpretation:** if Phase 1-2 hand-written baselines legitimately use `hypothesis_hash=None` (per CLAUDE.md "DSL canonical hash (NULL for hand-written" pattern), then `hypothesis_hash=None` is NOT a fail-closed condition for `single_run` run_type — it's only a fail-closed for `walk_forward_window` / `batch_summary` / Phase 2+ DSL runs. In that case, restructure §2.3.4 to test "`hypothesis_hash=None` AND `run_type='batch_summary'` → fails closed" rather than universal rejection.

**Recommend: defer this nuance to Charlie register at sub-plan PFR.** Two interpretations:
1. Strict: hypothesis_hash required for ALL inserts (breaks Phase 1A baselines)
2. Conditional: hypothesis_hash required for Phase 2+ DSL-derived inserts (preserves Phase 1A backward compat)

Either is defensible; pre-commit at sub-plan v_next ratify. **DS8 named sub-decision at §8.2.**

#### 2.3.5 Failure case 3: Missing `batch_id`

Per Contract 2.0.3: `source_batch_id` (artifact field) aliases registry `runs.batch_id`. Same SQL-constraint gap as §2.3.4 — `batch_id TEXT` at [`backtest/experiment_registry.py:90`](../../../backtest/experiment_registry.py) declared without NOT NULL.

```python
def test_failure_3_missing_batch_id(self, tmp_path, monkeypatch):
    # ... setup ...

    args = _make_minimal_write_args(run_id="missing-bid-run-id")
    args["db_path"] = tmp_db
    args["hypothesis_hash"] = "some-hash"
    args["batch_id"] = None  # missing

    with pytest.raises(ValueError) as exc_info:
        _write_to_registry(**args)

    msg = str(exc_info.value)
    # Per Contract 2.0.3: error must surface BOTH the canonical registry column name
    # AND the artifact alias name (operator diagnostic)
    assert ("batch_id" in msg) or ("source_batch_id" in msg), (
        f"Missing batch_id failure must identify field name (batch_id or source_batch_id alias); "
        f"got: {msg!r}"
    )
```

**Same caveat as §2.3.4:** Phase 1A single-run baselines may legitimately have `batch_id=None` (not part of a Phase 2 batch). The fail-closed scope is conditional, not universal. Defer to Charlie register at PFR. **DS8 named sub-decision at §8.2.**

**Alias resolution discipline verification:** assert error message surfaces EITHER the registry column name (`batch_id`) OR the Contract 2.0.3 artifact alias (`source_batch_id`) — proves the alias mapping is documented at the failure boundary (not buried elsewhere). This is a tighter assertion than just "fail closed" and exercises the Contract 2.0.3 aliasing intent.

#### 2.3.6 Failure case 4: Mismatched `cost_anchor_id` vs canonicalized `execution_config_path`

This is THE Contract 2.0.4 integrity check. The current LineageContext `__post_init__` at [`backtest/artifact_schema.py`](../../../backtest/artifact_schema.py) `__post_init__` (line 300+) **resolves cost_anchor_id from execution_config_path at construction time** — meaning a user cannot directly construct an LC with mismatched values (the construction overwrites cost_anchor_id via `object.__setattr__`).

**Surface judgment:** the mismatch case is therefore reachable only via:
1. Post-construction tampering via `object.__setattr__(lc, "cost_anchor_id", "wrong_value")` — covered by T1.1 SEAL `revalidate_for_write()` at [`backtest/artifact_schema.py`](../../../backtest/artifact_schema.py) `revalidate_for_write()`; already tested at [`tests/test_t1_1_sys_fix.py:2583`](../../../tests/test_t1_1_sys_fix.py) `TestSys5RevalidateForWriteDirectStrictFields`
2. Direct `_write_to_registry()` call with scalar `execution_config_path` + scalar `cost_anchor_id` disagreement — but the current engine code shows the scalar pathway derives `cost_anchor_id` from canonicalized path, not from a separate scalar; user can't pass conflicting cost_anchor_id

**Recommendation:** §2.3.6 may be testing a defensive path that is already structurally closed by Contract 2.0.4 design. Two paths forward:

1. **Specification-driven test (recommended for T1.5 v1):** test the spec at the LineageContext layer — `object.__setattr__(lc, "cost_anchor_id", "wrong_value"); _write_to_registry(lineage_context=lc, ...)` MUST raise via `revalidate_for_write()` invariant. This duplicates T1.1 SEAL coverage but exercises the engine-registry pathway specifically. Mark as cross-reference to T1.1 SEAL.

2. **Scalar-pathway test:** verify that direct scalar `cost_anchor_id` argument to `_write_to_registry()` is REJECTED (the function should not accept a scalar cost_anchor_id at all — it's always derived). If the function silently ignores a scalar cost_anchor_id keyword, that is a SURFACE GAP requiring engineering register.

**[UNVERIFIED]** whether `_write_to_registry()` accepts a scalar `cost_anchor_id` keyword argument at all; recommend Codex grep at PFR. If it does NOT, §2.3.6 path 2 is moot and only path 1 makes sense. **DS10 named sub-decision at §8.2.**

```python
def test_failure_4_cost_anchor_id_tamper_via_setattr(self, tmp_path, monkeypatch):
    """Per Contract 2.0.4 integrity + T1.1 SYS5 revalidate_for_write invariant.

    Mismatch is structurally unreachable via normal LC construction; this test
    exercises the post-construction tamper path closed by SYS5.
    Cross-reference: tests/test_t1_1_sys_fix.py:2583 TestSys5RevalidateForWriteDirectStrictFields.
    """
    # ... setup ...

    lc = LineageContext(
        run_id="mismatch-run-id",
        # ... 12 other valid fields ...
        execution_config_path="config/execution.yaml",  # → legacy_perp_inspired_7bps_v0
        # ... LATE_FILL fields deferred ...
    )
    # Post-construction tamper (intentional bypass of frozen guard)
    object.__setattr__(lc, "cost_anchor_id", "spot_realistic_15bps_v1")  # WRONG

    args = _make_minimal_write_args(run_id="mismatch-run-id")
    args["db_path"] = tmp_db
    args["lineage_context"] = lc

    with pytest.raises(ValueError) as exc_info:
        _write_to_registry(**args)

    msg = str(exc_info.value)
    assert "cost_anchor_id" in msg, f"Mismatch must surface cost_anchor_id field; got: {msg!r}"
    # Either revalidate_for_write tag OR explicit Contract 2.0.4 reference acceptable
    assert ("revalidate_for_write" in msg) or ("Contract 2.0.4" in msg) or ("does not match" in msg), (
        f"Mismatch failure must surface invariant violation context; got: {msg!r}"
    )
```

#### 2.3.7 Failure case 5: Un-mapped canonicalized `execution_config_path`

Already covered at T1.4 B2.c [`tests/test_t1_4_backward_compat.py:712`](../../../tests/test_t1_4_backward_compat.py)+ for the scalar-path entry. §2.3.7 should cover the **LineageContext-path** entry which fails at LC construction time (before reaching `_write_to_registry()`):

```python
def test_failure_5_unmapped_path_via_lineage_context_construction(self, tmp_path, monkeypatch):
    """Per Contract 2.0.4 fail-closed clause via LC __post_init__ path.

    Cross-reference: tests/test_t1_4_backward_compat.py:712 (scalar-path B2.c).
    This test covers the LC-construction-time fail-closed (raises at __post_init__,
    not at _write_to_registry).
    """
    from backtest.artifact_schema import LineageContext, COST_ANCHOR_ID_MAPPING

    unmapped_path = "config/execution_phase4_unknown.yaml"

    with pytest.raises(ValueError) as exc_info:
        LineageContext(
            run_id="unmapped-run-id",
            hypothesis_hash="h", source_batch_id="b", regime_key="v2.regime_holdout",
            engine_commit="e", current_git_sha="g",
            execution_config_path=unmapped_path,
            execution_config_sha256="s1", parquet_data_sha256="s2",
            returns_per_bar_path="", returns_per_bar_sha256="",
            T_obs=10, parent_run_id=None,
        )

    msg = str(exc_info.value)
    # Per Contract 2.0.4 error message content per LC __post_init__ at
    # backtest/artifact_schema.py:434-447
    assert unmapped_path in msg or "unknown.yaml" in msg
    # FULL mapping enumeration per Codex F3 v2 PFR tightening precedent at T1.4 B2.c
    for path_key, anchor_id in COST_ANCHOR_ID_MAPPING.items():
        assert path_key in msg, f"Mapping entry {path_key!r} missing from error; got: {msg!r}"
        assert anchor_id in msg, f"Mapping entry {anchor_id!r} missing from error; got: {msg!r}"
    # Guidance text
    assert ("R3.1d" in msg) or ("Update" in msg) or ("human approval" in msg)
```

**Cross-reference discipline:** T1.4 B2.c covers the scalar-path; T1.5 §2.3.7 covers the LC-construction-path. Two paths reach the same fail-closed contract; both should be tested independently. The scalar-path fails at `_write_to_registry()`; the LC-path fails at LineageContext `__post_init__`. Both raise ValueError with similar message content per Contract 2.0.4 fail-closed clause.

#### 2.3.8 Happy-path: None-normalization

Per Contract 2.0.4 interpretation (b) LOCKED [parent plan v5 line 125]: `lineage_context=None` OR `execution_config_path=None` → normalize to `config/execution.yaml` → resolve to `legacy_perp_inspired_7bps_v0`.

Already covered at T1.4 B2.a [`tests/test_t1_4_backward_compat.py:660`](../../../tests/test_t1_4_backward_compat.py)+. §2.3.8 may DUPLICATE T1.4 B2.a coverage or differentiate.

**Subagent recommendation: drop §2.3.8 happy-path from T1.5 scope (covered by T1.4 B2.a); replace with explicit cross-reference + scope exclusion at §2.3.12.** Per T1.4 B2.a [`tests/test_t1_4_backward_compat.py:679`](../../../tests/test_t1_4_backward_compat.py)+ asserts `execution_config_path IS NULL` under B2.a — meaning normalization populates `cost_anchor_id` but leaves `execution_config_path` column NULL. The 5 failure-mode coverage in §2.3.3-§2.3.7 is the substantive T1.5 (d) deliverable; happy-path None-normalization is T1.4 coverage.

**DS9 named sub-decision at §8.2** — Charlie register at sub-plan PFR if DROP recommendation is contested (alternative: differentiate §2.3.8 from T1.4 B2.a by extending assertion scope).

#### 2.3.9 Hermetic isolation discipline

Per T1.4 SEAL B3.4 precedent at [`tests/test_t1_4_backward_compat.py:813`](../../../tests/test_t1_4_backward_compat.py)+:

**Required mechanisms:**

1. **Temp `experiments.db` per test method** (not shared via class fixture) — each test method gets its own `tmp_path` and creates its own DB. Sharing creates ordering-dependent failures.
2. **DEFAULT_DB_PATH monkeypatch** — per Codex F1 ADOPT at T1.4 ([`backtest/experiment_registry.py:46`](../../../backtest/experiment_registry.py) `DEFAULT_DB_PATH` resolved at call-time in `get_connection(None)` at line 187):
   ```python
   monkeypatch.setattr(registry_mod, "DEFAULT_DB_PATH", tmp_db)
   ```
3. **Schema initialization per test:** call `create_table(conn)` after opening tmp_db connection; per [`backtest/experiment_registry.py:193`](../../../backtest/experiment_registry.py) `create_table` is idempotent + applies migration columns; ensures full 14-Contract-2.0.5 schema available
4. **No cross-test pollution:** verify via teardown assertion that no canonical paths were written (defensive; pollution would indicate `db_path` parameter not respected somewhere in engine code)

**Anti-pattern (do NOT do):**
```python
# WRONG: shared class-level DB
class TestT1_5_RegistryIntegrity:
    @classmethod
    def setup_class(cls):
        cls.db_path = ...  # shared across tests → ordering-dependent failures
```

**Mirror T1.4 B2 helper pattern:**
```python
def _make_db(self, tmp_path: Path, name: str = "test.db") -> Path:
    from backtest.experiment_registry import create_table
    db_path = tmp_path / name
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    create_table(conn)
    conn.close()
    return db_path
```

Direct copy of [`tests/test_t1_4_backward_compat.py:650`](../../../tests/test_t1_4_backward_compat.py)+ `TestT1_4_B2_LegacyDefaultNormalization._make_db` — preserves proven pattern.

#### 2.3.10 Path canonicalization edge cases

Contract 2.0.4 path canonicalization edge cases — surface judgment on T1.5 §2.3 scope:

**Edge case A: path outside repo root.** Covered at T1.4 B2.d [`tests/test_t1_4_backward_compat.py:761`](../../../tests/test_t1_4_backward_compat.py)+. DO NOT duplicate at T1.5 §2.3. Cross-reference.

**Edge case B: case-insensitive filesystem + exact-case mismatch.** Contract 2.0.4 line 106 LOCKED `config/Execution.yaml` (capital E) FAILS CLOSED via mapping miss on macOS HFS+/APFS. T1.4 does NOT cover this case. **Subagent recommendation: §2.3.10 covers this at LineageContext-construction path:**

```python
def test_canonicalization_case_only_mismatch_fails_closed_on_case_insensitive_fs(
    self, tmp_path, monkeypatch
):
    """Per Contract 2.0.4 line 106 case-sensitivity policy LOCK.

    On case-insensitive filesystems (macOS HFS+/APFS default), exact-case match
    required at mapping lookup. 'config/Execution.yaml' (capital E) FAILS CLOSED
    via mapping miss — intentional per plan v5 Fv5-1 LOW inline-fix.
    """
    from backtest.artifact_schema import LineageContext

    # Skip if running on case-sensitive FS (Linux ext4 default) — the case-mismatch
    # would resolve to a non-existent file rather than via case-folding
    import platform
    if platform.system() == "Linux":
        pytest.skip("Test specific to case-insensitive filesystems (macOS default)")

    case_mismatch_path = "config/Execution.yaml"  # capital E

    with pytest.raises(ValueError) as exc_info:
        LineageContext(
            # ... canonical fields ...
            execution_config_path=case_mismatch_path,
            # ...
        )

    msg = str(exc_info.value)
    # Per Contract 2.0.4 fail-closed clause: full mapping enumerated; guidance text
    assert "Execution.yaml" in msg or "execution_config_path" in msg
```

**Surface judgment [UNVERIFIED]:** subagent did NOT independently verify that `realpath()` on macOS HFS+ preserves the input case (vs case-folding to the on-disk canonical case). If realpath case-folds, the test as written would NOT raise (canonicalize would resolve `config/Execution.yaml` to `config/execution.yaml` and mapping lookup would succeed). Verify at PFR via Codex independent test execution on macOS. **DS6 named sub-decision at §8.2.**

**Edge case C: relative path with `../` traversal.** E.g., `execution_config_path = "config/../config/execution.yaml"` — canonicalize via realpath resolves to `config/execution.yaml`; mapping succeeds. This is NORMAL behavior, not a fail-closed branch. Skip from §2.3 scope unless verifying that the canonicalized form (without `..`) is what's persisted to the DB row — which is a property of canonicalize_execution_config_path() unit-tested at T1.3 SEAL coverage; defer.

**Surface judgment on §2.3 vs §2.1-adjacent scope:** Edge case A (outside-repo) lives at registry-integrity (T1.4 B2.d already); Edge case B (case-only mismatch) is path-canonicalization unit territory more than registry-integrity; Edge case C (relative with `..`) is canonicalize unit territory.

**Subagent recommendation:** §2.3.10 covers Edge case B only (it's the gap T1.4 leaves); Edge cases A + C explicitly excluded with cross-references. If Charlie wants comprehensive path-canonicalization coverage, route to a separate test module `tests/test_t1_5_path_canonicalization.py` outside §2.3 scope. **DS6 named sub-decision at §8.2.**

#### 2.3.11 Implementation discipline

**Test file:** `tests/test_t1_5_registry_integrity.py`

**Test class:** `TestT1_5_RegistryIntegrity` — covers happy-path triple resolution + 5 failure cases + §2.3.10 case-mismatch edge

**Method naming convention:**
- `test_triple_resolution_happy_path`
- `test_failure_1_duplicate_run_id`
- `test_failure_2_missing_hypothesis_hash`
- `test_failure_3_missing_batch_id`
- `test_failure_4_cost_anchor_id_tamper_via_setattr`
- `test_failure_5_unmapped_path_via_lineage_context_construction`
- `test_canonicalization_case_only_mismatch_fails_closed_on_case_insensitive_fs`

Mirrors T1.4 numbered-failure-case naming at [`tests/test_t1_4_backward_compat.py:712`](../../../tests/test_t1_4_backward_compat.py)-798.

**Parametrize discipline:** do NOT parametrize the 5 failure cases over one test method. Per the T1.4 B2 precedent + §2.3.3-§2.3.7 above, each failure case is structurally distinct (different field, different error message keywords, different invariant); independent methods preserve failure attribution. The smoke test §2.2 may parametrize over 1-3 candidates (structurally identical); §2.3 failure cases cannot.

**Error-message-content assertions:**
- Assert specific guidance text presence (e.g., "R3.1d", "Update", "human approval") per Codex F3 v2 PFR tightening precedent at T1.4 B2.c
- Do NOT just `pytest.raises(ValueError)` — that's necessary-but-insufficient (a ValueError raised from wrong line for wrong reason would pass)
- For mapping fail-closed: assert FULL mapping enumeration present (per Codex F1 v3 PFR convergent + T1.4 B2.c precedent at [`tests/test_t1_4_backward_compat.py:737`](../../../tests/test_t1_4_backward_compat.py)-754) — verifies error message contains all 6 entries per Contract 2.0.4 fail-closed-clause discipline

**Hermetic isolation per §2.3.9.**

#### 2.3.12 Explicit exclusions

T1.5 (d) Registry integrity test does NOT cover:

1. **End-to-end engine→registry flow** — §2.2 Smoke scope (smoke goes through engine entry point; §2.3 tests `_write_to_registry()` directly)
2. **Per-bar artifact SHA256 verification at consumer-side** — T1.2 SEAL scope at `check_b_c_extended_semantics_or_raise()`
3. **Regime-holdout-passed semantics** — T1.3 + Phase 2A scope
4. **LineageContext post-construction field-tamper across ALL 14 fields** — T1.1 SEAL coverage at [`tests/test_t1_1_sys_fix.py:2583`](../../../tests/test_t1_1_sys_fix.py) `TestSys5RevalidateForWriteDirectStrictFields`. §2.3.6 references one specific tamper (cost_anchor_id) to verify the engine-registry pathway; does NOT re-cover all 14 fields
5. **B2.a/b/c/d 4-scenario default-normalization** — T1.4 B2 SEAL coverage at [`tests/test_t1_4_backward_compat.py:640`](../../../tests/test_t1_4_backward_compat.py)-798 (§2.3.8 dropped per subagent recommendation per DS9; happy-path None-normalization is T1.4 coverage)
6. **Outside-repo path fail-closed** — T1.4 B2.d coverage
7. **Relative-path `..` canonicalization** — T1.3 canonicalize_execution_config_path unit test scope
8. **Walk-forward / evaluation-gate driver opt-out registry behavior** — T1.4 B3.3/B3.4 γ-1 SEAL coverage
9. **DB migration idempotency** — T1.4 SEAL `TestT1_4_DBMigrationIdempotency` covers 3 scenarios; T1.5 does NOT re-cover

#### 2.3.13 Cycle-pattern observations

**Hermetic isolation gap surfacing late.** T1.4 cumulative empirical (parent plan v5 §0 v2 PFR + Codex F1 v3 PFR ADOPT) showed hermetic isolation gaps via `DEFAULT_DB_PATH` resolution timing — `get_connection(None)` resolves global at call-time, requiring monkeypatch BEFORE any engine code that triggers DB resolution. §2.3 inherits this lesson directly: monkeypatch BEFORE `_write_to_registry()` invocation in every test method, NOT after import. Recommend test review at PFR explicitly verifies monkeypatch ordering.

**Row-shape invariant catches at smart-mock layer.** T1.4 B3.4 precedent (Codex caught smart-mock row-shape violation that Advisor missed) directly applies to §2.3 if any test method uses smart-mock for `_write_to_registry()` (e.g., to inject duplicate-run_id without actually calling SQLite). **Recommend §2.3 implementation AVOID smart-mocks entirely** — use real SQLite tempdir per §2.3.9. Smart-mocks at registry layer have empirical structural-fidelity-gap risk.

**Belt-and-suspenders defense-in-depth (where applicable).** Per [`feedback_invariant_level_vs_enumeration.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_invariant_level_vs_enumeration.md) cycle-pattern observation codified at B-C-extended T1.1 9-iteration arc: "centralized invariant-level closure at producer layer + retain consumer-side mirrors as defense-in-depth." §2.3 is the consumer-side mirror layer; T1.1 SYS5 `revalidate_for_write()` is the producer-side invariant. Both should test the same contracts (cost_anchor_id consistency, field non-emptiness) from different entry points. Recommend §2.3 explicitly cross-references T1.1 SEAL at each method docstring where the underlying invariant is shared.

**Engineering-gap surfacing risk.** §2.3.4 + §2.3.5 + §2.3.6 each carry [UNVERIFIED] flags about current engine behavior (whether engine fail-closes on None hypothesis_hash, None batch_id, scalar cost_anchor_id-vs-execution_config_path disagreement). Surfacing these tests at T1.5 may EXPOSE engineering gaps in T1.3 SEAL — that is the structurally correct behavior of a registry-integrity test suite, but creates a routing decision: gap → fresh Charlie register-event for T1.3 corrective (NOT T1.5 in-scope fix). Mirror T1.4 §3.2 failure handling discipline: "Any new defect surfacing in T1.1/T1.3 territory during T1.4 execution → classify as defect; raise to Charlie; require fresh register-event (NOT in-T1.4 corrective fix)." Apply same policy to T1.5.

**Codex independent verification expected at PFR.** Per parent T1.4 §9 codification: Codex `[VERIFIED]` tokens are reliable within tokenized scope (0 hallucinations within tokenized claims across recent arc). Multiple [UNVERIFIED] flags in §2.3.4-§2.3.8 above are explicit invitations for Codex independent grep at PFR rounds; orchestrator should pre-grep the engine `_write_to_registry()` failure paths to reduce PFR iteration count. Recommended pre-PFR verification commands:
- `grep -n "hypothesis_hash" backtest/engine.py | grep -i "raise\|none\|fail"`
- `grep -n "batch_id" backtest/engine.py | grep -i "raise\|none\|fail"`
- `grep -n "cost_anchor_id" backtest/engine.py | grep -i "raise\|disagree\|conflict"`

**Test count budget.** §2.3 design: 1 happy-path + 5 failure cases + 1 case-mismatch edge = 7 test methods (8 if §2.3.8 retained; 6 if §2.3.10 dropped). Compact, attribute-clean, cross-references T1.4 + T1.1 SEAL coverage. Resist scope expansion pressure at PFR (e.g., "add T1.3 SEAL signature backward-compat coverage" — that's T1.4 B1 coverage). Hold the §2.3 boundary at registry-integrity unit-level + 5 fail-closed branches per parent plan v5 Contract 2.0.6 (d).

---

### §2.4 Module integration into existing test suite

**Scope:** wire 3 new test files into existing pytest collection + verify they appear in `python -m pytest --collect-only` output + verify they execute under `python -m pytest -q tests/test_t1_5_*.py` invocation pattern.

**Integration discipline:**
- New test files at `tests/test_t1_5_*.py` follow existing convention (test_t1_1_sys_fix.py + test_t1_4_backward_compat.py patterns)
- No changes to `pyproject.toml` test configuration
- No `conftest.py` shared-fixture introduction unless explicitly registered as substantive sub-decision (§8 named sub-decision)
- Full suite invocation: `python -m pytest -q` MUST report success with delta count of new T1.5 tests added to baseline 2297

**Baseline verification:**
- Pre-T1.5-implementation: `pytest --collect-only -q | tail -1` reports 2297 tests
- Post-T1.5-implementation: same command reports `2297 + N` where N = T1.5 test method count
- Zero regression: all 2297 existing tests PASS after T1.5 additions

---

### §2.5 Subagent §2 detail-fill provenance + Mode A spot-verification + carry-forward risk disclosure

#### 2.5.1 Provenance

§2.1, §2.2, §2.3 content drafted by `quant-research-advisor` (opus) subagent dispatched in background 2026-05-23 per γ Hybrid drafting modality (Charlie register: "ratify use quant-research-advisor, authorized" 2026-05-23). Subagent brief gated content scope to §2.1+§2.2+§2.3 ONLY (skeleton §1+§3-§11 reserved for orchestrator authorship); subagent ran with Read/Grep/Glob/Bash tools and pre-verified empirical claims via independent shell execution + file:line citation pre-check.

#### 2.5.2 Orchestrator Mode A spot-verification PASS (2026-05-23)

Per [`feedback_reviewer_routing_subagent_default.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md) 3-layer safety architecture Layer 3 (orchestrator independent re-verification on every Advisor specific-claim before adoption) — orchestrator independently verified load-bearing subagent claims at integration time:

| Claim | Verification method | Outcome |
|---|---|---|
| 5 prohibited kurtosis values (§2.1.4) at scipy 1.10.0 + pandas 2.2.3 | Independent `python3 -c "..."` execution at HEAD `56fe413` | **ALL 5 EXACTLY MATCH** subagent claims (2.5, 5.5, 0.0, 2.5, 5.5) |
| `TestSys5RevalidateForWriteDirectStrictFields` at tests/test_t1_1_sys_fix.py:2583 | Independent `grep` | ✓ exists at line 2583 |
| `TestT1_4_A2_DomainFenceRejection` at tests/test_t1_4_backward_compat.py:223 | Independent `grep` | ✓ exists at line 223 |
| `TestT1_4_B2_LegacyDefaultNormalization` at tests/test_t1_4_backward_compat.py:640 | Independent `grep` | ✓ exists at line 640 |
| `_make_minimal_write_args` at tests/test_t1_4_backward_compat.py:131 | Independent `grep` | ✓ exists at line 131 |
| `_make_db` at tests/test_t1_4_backward_compat.py:650 (B2) + 816 (B3) | Independent `grep` | ✓ both exist |
| `DEFAULT_DB_PATH` at backtest/experiment_registry.py:46 | Independent `grep` | ✓ exists |
| `run_id TEXT PRIMARY KEY` at backtest/experiment_registry.py:56 | Independent `grep` | ✓ exists |
| `batch_id TEXT` at backtest/experiment_registry.py:90 | Independent `grep` | ✓ exists |
| `hypothesis_hash TEXT` at backtest/experiment_registry.py:91 | Independent `grep` | ✓ exists |
| `get_connection` at backtest/experiment_registry.py:178 | Independent `grep` | ✓ exists (line 178 def; line 187 is `path = db_path or DEFAULT_DB_PATH` resolution line cited by subagent for call-time semantics — both citations valid) |
| `create_table` at backtest/experiment_registry.py:193 | Independent `grep` | ✓ exists |
| `COST_ANCHOR_ID_MAPPING` at backtest/artifact_schema.py:71 | Independent `grep` | ✓ exists |
| `LineageContext` at backtest/artifact_schema.py:201 | Independent `grep` | ✓ exists |
| `__post_init__` at backtest/artifact_schema.py:300 | Independent `grep` | ✓ exists (subagent's "434-447" cite refers to within-method mapping-lookup block — valid range citation) |

**Mode A verification verdict:** zero load-bearing hallucinations in subagent's drafted content. `[VERIFIED via Bash empirical]` tokens used by subagent on the 5 kurtosis values are reliable evidence within tokenized scope (orchestrator independent re-execution PASS). Cross-cycle precedent: this is consistent with opus pilot 0/13+ hallucination rate at post-/agents-fix regime per [`feedback_reviewer_routing_subagent_default.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md) cumulative record.

#### 2.5.3 Subagent-surfaced [UNVERIFIED] items (carry forward to PFR Codex verification)

Subagent explicitly flagged 6 [UNVERIFIED] items for Codex PFR independent verification (per Mode A discipline: surface gaps rather than fabricate). These ARE preserved as such in §2.1-§2.3 content; reviewer dispatches MUST verify before adoption-into-implementation:

1. **§2.3.4** — current `_write_to_registry()` behavior on `hypothesis_hash=None` scalar (rejects vs silently inserts NULL); blocks DS8 register decision
2. **§2.3.5** — current `_write_to_registry()` behavior on `batch_id=None` scalar (rejects vs silently inserts NULL); blocks DS8 register decision
3. **§2.3.6** — whether `_write_to_registry()` accepts a scalar `cost_anchor_id` keyword argument at all; blocks DS10 register decision
4. **§2.3.8** — whether T1.4 B2.a's `execution_config_path IS NULL` assertion under None-normalization is current behavior; blocks DS9 register decision
5. **§2.3.10** — whether `realpath()` on macOS HFS+ preserves input case vs case-folds; blocks DS6 register decision (Edge B case-mismatch test executability)
6. **§2.2.2 Option (i)** — verification that 2023-08-01 to 2023-08-08 window in canonical parquet has zero gap-window and zero zero-volume-bar anomalies; blocks DS2 register decision (Option (i) feasibility)

#### 2.5.4 Subagent self-discount disclosures (carry-forward)

Subagent applied own-anchoring discipline + Mode A self-flag discipline per dispatch brief. Surfaced explicit lean-discounts:

- **§2.2.10 structural lean toward Option (i)** (canonical OHLCV) — subagent self-discounted ~85% per Advisor Mode A track record on data-source decisions; orchestrator preserves discount + routes to Charlie DS2 register with neutral enumeration (no lean injection at integration)
- **§2.3.4/§2.3.5 hypothesis_hash/batch_id rejection scope** — subagent surfaced 2 alternative interpretations (strict vs conditional); did NOT pre-commit; routes to DS8 register
- **§2.3.6 cost_anchor_id mismatch test path** — subagent surfaced 2 alternative paths (LC tamper vs scalar); did NOT pre-commit; routes to DS10 register
- **§2.3.8 happy-path drop recommendation** — subagent recommends DROP based on T1.4 B2.a coverage; routes to DS9 register if contested
- **§2.3.10 Edge B inclusion** — subagent recommends INCLUDE conditional on macOS realpath behavior; routes to DS6 register

#### 2.5.5 Risk disclosure (subagent-authored; preserved verbatim)

The following risk disclosure is subagent-authored at the end of its draft and preserved verbatim per Mode A transparency discipline:

> **Advisor biases applicable to this output:**
> - Mode A hallucination tendency on citation-dense tasks (~85% per-dispatch rate per R3.1d cycle empirical; this draft contains many `engine.py:line` and `artifact_schema.py:line` citations + scipy/pandas empirical values — non-trivial Mode A surface).
> - Own-anchoring tendency at implementation-review iteration class per [`feedback_advisor_own_anchoring_implementation_review.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_advisor_own_anchoring_implementation_review.md) — this draft IS implementation-design-class (one step earlier than implementation-review but adjacent); apply discount accordingly at PFR rounds.
> - Directional instability on data-source recommendations (§2.2.10 lean toward Option (i) discounted ~85%).
>
> **Mitigations applied in this draft:**
> - All 5 PROHIBITED kurtosis values empirically re-verified via Bash at scipy 1.10.0 / pandas at HEAD `12dffde`, 2026-05-23 → `[VERIFIED via Bash empirical]` tokens
> - File:line citations cross-referenced via Read tool to current HEAD content (artifact_schema.py, experiment_registry.py, test_t1_4_backward_compat.py, wf_lineage.py)
> - Multiple [UNVERIFIED] flags surfaced explicitly at §2.3.4 / §2.3.5 / §2.3.6 / §2.3.10 inviting Codex independent verification at PFR
> - Cross-references to T1.4 SEAL + T1.1 SEAL coverage to avoid scope duplication
> - DS2 PLACEHOLDER discipline strictly preserved at §2.2 — no data-source lock; enumeration is unbiased per Charlie register
>
> **Chain-trust limits:**
> - Subagent did NOT execute `pytest` against draft test methods — sketch-level only; Codex will independently verify test executability at PFR
> - Subagent did NOT independently verify §2.3.4 / §2.3.5 / §2.3.6 engine current behavior; flagged inline as [UNVERIFIED]
> - Subagent did NOT verify scipy 1.10.0 fixture-vector empirical values cross-platform (only macOS local); reviewer should confirm on CI Linux
> - DS2 decision is Charlie-register-gated; v1 PFR may surface that one of the 3 options is technically infeasible (e.g., canonical OHLCV path resolution under test isolation) — orchestrator should pre-verify Option (i) feasibility before DS2 register-event fire
>
> **Verification gaps:**
> - §2.3.8 happy-path None-normalization recommendation to drop assumes T1.4 B2.a coverage is sufficient — orchestrator + Codex should independently confirm at PFR
> - §2.2.2 Option (i) requires `data/quality/` validation report grep for 2023-08 gap-window-absence to confirm fixture-window stability — not performed at this draft
> - Test count for §2.1 (9 methods), §2.2 (1-3 methods per candidate × N), §2.3 (7 methods) are draft estimates; actual count locks at T1.5 implementation
>
> **Default posture:** non-execution. Awaiting Charlie DS2 register-event before T1.5 v_next reviewer dispatches fire. Sub-plan integration owned by orchestrator. No `[APPROVE]` / `[BLOCK]` verdict implied — drafter dispatch only.

---

## §3 Validation approach + success criteria

### §3.1 Pass criteria

Cycle SEAL conditional on the following mandatory items:

1. **Path B deliverable 3-of-3 PASS:** §2.1 fixture test + §2.2 smoke test + §2.3 registry integrity test all PASS at cycle SEAL
2. **Zero regression on T1.4 baseline:** full suite (`python -m pytest -q`) reports `2297 + N` tests with zero failures (N = T1.5 test method count, locked at implementation; subagent draft estimate ~17-25 across 3 classes)
3. **DS2 register-event resolved:** Charlie register-event for smoke-test data-source lock (option i/ii/iii per §2.2.2) lands BEFORE reviewer dispatches fire; sub-plan v_next reflects lock
4. **2-leg PFR convergent APPROVE:** Codex codex-rescue + Advisor opus (separate instance from §2 drafter — see §6.4 cross-leg discipline) both APPROVE at v_final PFR round
5. **SEAL-eve adversarial round APPROVE:** explicit "assume hidden bugs and find them" framing per T1.4 v3 SEAL-eve discipline; OPERATIONALLY REQUIRED post v_final PFR convergent APPROVE (5-instance T1.4 cycle empirical — see [`feedback_advisor_own_anchoring_implementation_review.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_advisor_own_anchoring_implementation_review.md))
6. **Mode A independent re-verification:** orchestrator independently grep/Read source for every Advisor specific-claim before adoption per cumulative cycle empirical
7. **All ADOPTed fixes integrated:** per-fix adjudication discipline per [`feedback_reviewer_suggestion_adjudication.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_suggestion_adjudication.md); no bulk-accept
8. **§1 scope statement + §4 explicit exclusions reaffirmed at SEAL gate:** Path B scope preserved; no scope drift to (c) Canary or to T1.6 documentation territory
9. **§10 task SEAL chain populated:** all PFR + SEAL-eve + ratify register-events recorded post-fact
10. **Charlie register-event for SEAL ratify:** SEAL ratify fire AUTHORIZED at separate register-event (NOT pre-authorized; T1.5 cycle entry pre-auth covers ENTRY only per anti-pre-emption)

### §3.2 Failure handling

- **v_n PFR finds BLOCKING/HIGH:** drop v_n; iterate v_n+1 with ADOPTed fixes; re-dispatch 2-leg PFR
- **v_n PFR convergent APPROVE but Codex SEAL-eve catches BLOCKING:** drop v_n; iterate v_n+1; re-dispatch SEAL-eve (per T1.4 v3 empirical — DO NOT skip SEAL-eve)
- **Mode A hallucination from Advisor:** PUSHBACK on hallucinated finding; do NOT adopt fix for non-existent defect
- **DS2 register-event delayed:** sub-plan v1 reviewer dispatches HOLD until DS2 register; orchestrator does not auto-fire
- **Full suite regression detected:** STOP cycle; root-cause regression before SEAL; do NOT mask via xfail/skip
- **Engineering gap surfaced in §2.3.4/§2.3.5/§2.3.6 [UNVERIFIED] items:** classify as defect; raise to Charlie; require fresh register-event for T1.3 corrective (NOT T1.5 in-scope fix) per parent plan v5 §3.2 failure handling discipline

---

## §4 Explicit exclusions (anti-pre-emption discipline)

The following are OUT OF SCOPE for T1.5 Path B per Charlie register-event 2026-05-23:

| # | Excluded scope | Reason | Cross-reference |
|---|---|---|---|
| 1 | (c) Canary class (aggregate CSV + aggregate JSON + N per-candidate byte-identity) | DEFERRED per Charlie register Path B 2026-05-23; T1.4 SEAL implementation covers fully | [`tests/test_t1_4_backward_compat.py`](../../../tests/test_t1_4_backward_compat.py) — TestT1_4_A1_A6 + TestT1_4_A2 + TestT1_4_A3_A4_A5 classes |
| 2 | T1.6 documentation deliverables (schema spec write-up + consumer enumeration + `data_dictionary.md` updates) | T1.6 cycle ENTRY pre-authorized; sub-plan drafting + implementation in next cycle | Parent plan v5 §2.6 |
| 3 | Engine modification tests (per-bar return series capture + `EquityCurveCollector` extension) | T1.1 SEAL scope (`12dffde`) | Parent plan v5 §2.3 |
| 4 | Schema validator tests (versioned schema spec + distinct validation branch + per-bar artifact discipline) | T1.2 SEAL scope (bundled in `12dffde`) | Parent plan v5 §2.1 + Contract 2.0.2 + 2.0.5 |
| 5 | Registry API tests beyond triple-linkage + 5 failure cases + happy-path None-normalization | T1.3 SEAL scope (bundled in `12dffde`) + Contract 2.0.6 (d) scope boundary | Parent plan v5 §2.2 |
| 6 | Backward-compatibility verification (B1 AST-based call-site classifier + B2 default-normalization + B3 legitimate flows γ-1 opt-out) | T1.4 SEAL scope (`5a44ec6`) | T1.4 sub-plan v7 + [`tests/test_t1_4_backward_compat.py`](../../../tests/test_t1_4_backward_compat.py) |
| 7 | Performance / benchmark tests for T1.x deliverables | Out of cycle scope; performance regression not in §3.1 pass criteria | — |
| 8 | Coverage instrumentation changes | Out of cycle scope; existing coverage tooling untouched | — |
| 9 | DSL compiler unit tests | T1.x deliverables consume DSL but don't modify it; DSL compiler test surface is separate concern | `strategies/dsl_compiler.py` |
| 10 | Pre-existing failing tests (if any surface during T1.5 work) | Out of T1.5 scope; flag as separate finding for separate Charlie register-event | — |
| 11 | γ3 PROHIBITED enumeration at the fixture vector | §2.1.6 surface judgment + tautological at symmetric vector; eligible-not-named for separate register if asymmetric-vector future cycle | DS5 at §8.2 |
| 12 | All-14-fields LineageContext post-construction field-tamper coverage | T1.1 SEAL `TestSys5RevalidateForWriteDirectStrictFields` scope; §2.3.6 references one tamper only | T1.1 SEAL |
| 13 | Production-data anomaly handling (NaN bars / zero-volume bars / gap-window axes) at engine→writer chain on real-data shape | Path B narrow scope; DS2 = Option (i) August-2023 window deliberately avoids known anomalies (orchestrator empirical 2026-05-24: 0 zero-volume / 0 NaN / 0 gaps in 176-bar window); heavy-tail axis IS exercised (γ4 ≈ 13.73 per Codex empirical re-verified 2026-05-24) but discrete-anomaly axes are NOT; eligible-not-named successor cycle per §8.2 DS-NEW (e) | Codex 2-leg PFR Q4b + heavy-tail empirical 2026-05-24 + orchestrator Mode A re-verification |

**Anti-pre-emption preserve:** none of the above exclusions are eligible to be re-included via reviewer adjudication or PFR finding adoption. Scope expansion requires fresh Charlie register-event boundary.

---

## §5 Risks + dependencies

### §5.1 Dependencies

- **Plan v5 Contract 2.0.1-2.0.6 LOCKED at parent ratify (2026-05-22)** — all 6 contracts are reference-only for T1.5 test design; no contract revision in T1.5 scope
- **T1.1 + T1.2 + T1.3 + T1.4 SEAL artifacts available** — T1.5 tests consume `backtest/artifact_schema.py` + `backtest/wf_lineage.py` + `backtest/experiment_registry.py` + `backtest/engine.py` modifications at `12dffde` / `5a44ec6` / `56fe413` HEAD state
- **scipy ≥ 1.9 in test environment** — Contract 2.0.1 LOCKED implementation requires `nan_policy` keyword; fixture test gate fails closed if precondition not met (§2.1.5 scope; orchestrator verified scipy 1.10.0 + pandas 2.2.3 present 2026-05-23)
- **DEFAULT_DB_PATH monkeypatch convention** — T1.4 SEAL B3.4 establishes hermetic isolation pattern; T1.5 §2.3 reuses (§2.3.9 scope)
- **DS2 register-event** — sub-plan v1 reviewer dispatches gated on Charlie DS2 register before fire; reviewer dispatch hold expected

### §5.2 Risks

**Engineering risks:**
- **DS2 unresolved at sub-plan v1 surface time** → reviewer dispatches blocked until Charlie register-event lands; mitigated by §8 named sub-decision discipline + explicit hold protocol
- **scipy version drift in test environment** → silent skip of fixture test would mask regression; mitigated by §2.1.5 fail-closed precondition gate (proactive fail at test entry, not silent skip)
- **Synthetic OHLCV generator design (if DS2 = (ii))** → generator interface lock becomes substantive sub-decision (§8 named DS3); if surfaces during implementation, requires Charlie register before commit
- **Registry IntegrityError vs ValueError wrapping inconsistency** → §2.3 failure cases assert specific exception class; if T1.3 implementation wraps differently, T1.5 tests may need adjustment OR raise as T1.3 reconsider (NOT T1.5 scope expansion)
- **Hermetic test isolation pollution** → DEFAULT_DB_PATH monkeypatch must apply at every §2.3 test method; class-scoped fixture risk (if shared, isolation breaks); mitigated by §2.3.9 explicit method-scoped fixture discipline
- **Path canonicalization edge case scope creep at §2.3.10** → DS6 named sub-decision
- **Subagent-surfaced [UNVERIFIED] items at §2.3.4/§2.3.5/§2.3.6/§2.3.8/§2.3.10/§2.2.2** → 6 verification gaps; Codex PFR independent verification required; engineering-gap surfacing risk per §3.2 failure handling

**Process risks:**
- **Advisor own-anchoring at implementation-review iteration class** — 5-instance T1.4 cycle empirical (codified at [`feedback_advisor_own_anchoring_implementation_review.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_advisor_own_anchoring_implementation_review.md)); applies at every PFR round + SEAL-eve; MAXIMUM anti-anchoring discipline + Codex cross-model leg LOAD-BEARING
- **`quant-research-advisor` is both §2 drafter (this cycle) AND one reviewer leg candidate** → authorship-anchoring risk at v_n review of §2 content drafted by same subagent; mitigated by (i) Codex cross-model leg as no-authorship-anchor primary catch layer per B2 standing rule LOCKED 2026-05-19 + (ii) orchestrator Layer 3 independent verification (Mode A discipline; §2.5.2 spot-check applied) + (iii) §6.4 cross-leg discipline (separate Advisor instance for reviewer leg)
- **SEAL-eve adversarial OPERATIONALLY REQUIRED** — cannot skip after PFR convergent APPROVE per T1.4 v3→v4 empirical (6 substantive defects caught at v3 SEAL-eve)
- **Cross-model leg dispatch dependency** — Codex codex-rescue has historic stall rate ~4-8% per dispatch (cumulative through R3.1d); helper script + stale-dead classification per [`feedback_reviewer_routing_subagent_default.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md)
- **Sub-plan v_n iteration count uncertainty** — T1.4 sub-plan was 6 iterations + 1 amendment (v1→v7); T1.5 Path B narrow scope may converge faster (~3-4 iterations expected) but no a-priori lock

---

## §6 Reviewer dispatch plan

### §6.1 Sub-plan v_n PFR-rule-Y rounds (post-Charlie-sub-plan-fire)

**v1 PFR round (next; gated on DS2 register-event):**
- **Leg 1: Codex (codex-rescue)** — cross-model adversarial scan; structural defect class catches + canonical-artifact verification; expected verification load on subagent-surfaced [UNVERIFIED] items (6 from §2.5.3)
- **Leg 2: Advisor (`quant-research-advisor` SEPARATE instance from §2 drafter per cross-leg discipline)** — senior-quant + senior-AI-engineer prose-substance + methodology judgment + spec compliance verification
- **Dispatch in parallel** via single message multi-Agent call per [`feedback_parallel_subagent_dispatch.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_parallel_subagent_dispatch.md)
- **Codex auto-notification routine** per `~/.claude/scripts/codex-wait-and-fetch.sh` helper script + nonce-bearing sentinel discipline

**v_n+1 → cycle-final convergence:**
- Per-fix adjudication per D-5 P1 discipline; no bulk-accept
- PFR-rule-Y scoped post-fix re-review on new-content fixes (per [`feedback_reviewer_routing_subagent_default.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md))
- Expected iteration count: 3-4 PFR rounds typical at implementation-review class (per T1.4 cycle empirical)

### §6.2 Sub-plan SEAL-eve adversarial round

- **OPERATIONALLY REQUIRED** post v_final PFR convergent APPROVE (per T1.4 v3 SEAL-eve empirical — 6 substantive defects caught after convergent APPROVE)
- 2-leg dispatch with explicit "assume hidden bugs and find them" framing
- If SEAL-eve catches BLOCKING/HIGH: drop v_final; iterate; re-dispatch SEAL-eve (DO NOT skip)
- Advisor "no v_n+1 finding predicted" outputs are SIGNAL not authoritative — dispatch Codex anyway per [`feedback_advisor_own_anchoring_implementation_review.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_advisor_own_anchoring_implementation_review.md) Rule 1

### §6.3 Implementation review rounds (post-sub-plan-ratify; separate from §6.1-§6.2)

After sub-plan v_final ratify + Charlie register for implementation fire:
- v_n implementation work fires (orchestrator-direct OR subagent-dispatch; modality decided at implementation fire register-event)
- v_n implementation review rounds (analog of §6.1 but on implementation code, not sub-plan)
- v_n+1 → cycle-final convergence
- SEAL-eve adversarial on implementation code (analog of §6.2)
- T1.5 SEAL ratify (Charlie register-event)

### §6.4 Cross-leg discipline

- **§2.1+§2.2+§2.3 drafter** = `quant-research-advisor` instance #1 (background dispatch 2026-05-23; agentId `a0cc21961fcff600c` completed)
- **v_n PFR Advisor leg** = `quant-research-advisor` instance #2 (separate dispatch; no shared state with instance #1)
- **v_n PFR Codex leg** = `codex-rescue` (cross-model; no authorship anchor)
- **Why separate Advisor instances:** mitigates authorship-anchoring risk at review of §2 content drafted by same persona; cross-instance dispatch ≈ no-authorship-anchor proxy though same model class

---

## §7 SEAL gate criteria

T1.5 SEAL fires when ALL §3.1 pass criteria items 1-10 met AND:

1. **All 3 §2.X test classes implemented** at indicated test file paths
2. **Full suite reports `2297 + N` tests with zero failures** (N locked at implementation)
3. **DS2 register-event resolved** + reflected in sub-plan v_final + implementation
4. **§10 task SEAL chain fully populated** with all PFR + SEAL-eve + Charlie register-event timestamps + commit refs
5. **§4 explicit exclusions reaffirmed at SEAL gate** — no scope drift to (c) Canary or T1.6 territory
6. **Charlie register-event for SEAL ratify fires** (NOT pre-authorized; explicit register required)
7. **All [UNVERIFIED] items resolved** — either Codex PFR verification PASSED, OR engineering gap routed to fresh Charlie register-event for T1.3 corrective

T1.5 SEAL artifact: commit message format analog of T1.4 SEAL (`feat(b-c-extended/t1.5): fire T1.5 fixture/smoke/registry-integrity test suite SEAL — ...`); commit bundles implementation + sub-plan v_final + §10 task SEAL chain update.

T1.5 SEAL is task-level within B-C-extended cycle; Phase Marker advance fires at B-C-extended cycle SEAL boundary (after T1.6 SEAL), NOT at T1.5 SEAL per [`feedback_claude_md_freshness.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_claude_md_freshness.md) discipline.

---

## §8 Anti-pre-emption explicit reminder + named sub-decisions

### §8.1 Anti-pre-emption preserve

T1.5 cycle ENTRY + Path B scope-class + sub-plan v1 drafting fire + subagent ratify are AUTHORIZED at Charlie register 2026-05-23. The following downstream gates each require **separate Charlie register-event boundaries**; reviewer convergence is advisory only per [`feedback_authorization_routing.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_authorization_routing.md):

1. **DS2 register-event** — smoke-test data-source lock (i / ii / iii) before reviewer dispatches fire
2. **Sub-plan v1 reviewer dispatch fire** — 2-leg Codex + Advisor dispatch
3. **Each sub-plan PFR fix-adjudication iteration** — per-fix ADOPT/PUSHBACK/DEFER
4. **Sub-plan v_final ratify** — Charlie register for ratify; locks sub-plan
5. **Implementation work fire** — Charlie register for implementation modality + dispatch
6. **Each implementation PFR fix-adjudication iteration** — per-fix
7. **SEAL-eve adversarial dispatch fire**
8. **T1.5 SEAL ratify fire** — Charlie register; commits SEAL bundle
9. **T1.6 cycle ENTRY** (pre-authorized but T1.6 sub-plan drafting + reviewer + SEAL all need fresh register)
10. **B-C-extended cycle SEAL bundle** (pre-authorized but scope drafting + Phase Marker advance + §35 codification need fresh register)

### §8.2 Named load-bearing sub-decisions

Sub-decisions surfaced at v1 drafting (orchestrator skeleton + subagent §2 detail-fill) that require Charlie register-event if not resolved within v_final plan (i.e., before sub-plan ratify):

| # | Sub-decision | Resolution timing | Default if unregistered | Risk if pre-empted |
|---|---|---|---|---|
| **DS2** | Smoke-test data-source lock: (i) canonical OHLCV slice / (ii) fully synthetic OHLCV / (iii) hybrid | Before sub-plan v1 reviewer dispatches fire (HARD GATE) | sub-plan v1 reviewer dispatches DO NOT FIRE | reviewer dispatches on placeholder content + likely re-do post-DS2 lock; wasted review cycle |
| DS3 | Synthetic OHLCV generator interface (if DS2 = ii) | At sub-plan v_n drafting if DS2 = ii, before implementation fire if DS2 ≠ ii | locked to deterministic-seed + Gaussian-baseline return distribution per §2.2 placeholder | implementation interface drift; downstream test brittleness |
| DS4 | Registry test isolation mechanism: DEFAULT_DB_PATH monkeypatch + tempdir OR alternate | At §2.3 drafting time | DEFAULT_DB_PATH monkeypatch per T1.4 SEAL B3.4 precedent | implementation hermetic-isolation gap; cross-test pollution |
| DS5 | γ3 (skew) coverage in fixture test: PASS-only (subagent recommendation) vs PASS+PROHIBITED-enumeration at asymmetric vector | At §2.1 PFR adjudication if DEFER recommendation is contested | PASS-only per §2.1.6 subagent recommendation (PROHIBITED enumeration deferred to separate register-event) | partial moment estimator coverage; γ3 alternative-implementation lockout untested |
| DS6 | Path canonicalization edge case scope at §2.3.10: Edge B include only (subagent recommendation) vs Edge A+B+C comprehensive | At §2.3 PFR adjudication; Codex verify macOS realpath behavior first | Edge B include only per §2.3.10 subagent recommendation (A covered at T1.4 B2.d; C deferred to T1.3 canonicalize unit) | edge case coverage gap; production deployment risk |
| DS7 | Test file naming + organization (`tests/test_t1_5_*.py` pattern) | At §2.X drafting time | follow T1.4 SEAL pattern (`test_t1_5_<deliverable>.py`) | inconsistent test discovery + collection pattern |
| **DS8** | §2.3.4/§2.3.5 hypothesis_hash/batch_id rejection scope: strict (ALL inserts) vs conditional (Phase 2+ DSL-derived only) | At §2.3 PFR adjudication after Codex verifies current engine behavior on None inputs | NOT pre-committed; surface 2 interpretations for Charlie register | engineering gap surfacing risk; T1.3 corrective routing decision |
| **DS9** | §2.3.8 happy-path None-normalization scope: DROP (subagent recommendation; T1.4 B2.a coverage) vs DIFFERENTIATE | At §2.3 PFR adjudication | DROP per §2.3.8 subagent recommendation (T1.4 B2.a sufficient) | scope duplication; testing-redundancy creep |
| **DS10** | §2.3.6 cost_anchor_id mismatch test path: LC-tamper path 1 (subagent recommendation) vs scalar-pathway path 2 | At §2.3 PFR adjudication after Codex verifies scalar `cost_anchor_id` keyword acceptance | path 1 per §2.3.6 subagent recommendation (cross-reference to T1.1 SEAL SYS5 coverage) | scalar-pathway coverage gap; ambiguous test contract |
| **DS-NEW (e)** | Successor cycle "production-data anomaly engine→writer smoke" — covers NaN bars / zero-volume bars / gap-window axes that DS2 = Option (i) August-2023 window does NOT exercise (heavy-tail axis already covered at Option (i) per Codex empirical 13.73 vs 3.61 synth orchestrator re-verified 2026-05-24) | Eligible-not-named per anti-pre-emption; requires fresh Charlie register-event to fire; scope-class bounded at entry register | NOT pre-committed at T1.5 SEAL; CHARLIE-REGISTER-GATED per anti-pre-emption | Per Q5 gap (a) acknowledgment ADOPTed from CONVERGED 2-leg PFR 2026-05-24 |
| **DS-NEW (f)** | Successor cycle "T1.5-followup smoke artifact-writer + schema-validator chain coverage" — covers production engine→writer (`write_per_bar_artifact()`) → validator (`check_b_c_extended_semantics_or_raise()`) chain that DS2 = Option (i) Smoke does NOT exercise (deferred-state LATE_FILL bypasses writer phase at engine.py:1353; §2.2.4 PASS criteria "artifact emitted at correct path + INVOKE check_b_c_extended_semantics_or_raise" remaining structural coverage gap per SEAL-eve v2 Codex + Advisor #8 CONVERGED HIGH 2026-05-24) | Eligible-not-named per anti-pre-emption; requires fresh Charlie register-event to fire; scope-class bounded at entry register | NOT pre-committed at T1.5 SEAL; CHARLIE-REGISTER-GATED per anti-pre-emption | Per Path C hybrid invariant-level closure framework per `feedback_invariant_level_vs_enumeration.md` cycle empirical 2026-05-24; HIGH-1 partial-closure at v_impl_polish v1 (moment-chain helper covered; writer-validator chain deferred); HIGH-2 closure tight at v_impl_polish v2 (9/9 T1.x columns) |

DS8/DS9/DS10 are SURFACED BY SUBAGENT at §2 detail-fill drafting; orchestrator preserves without lean injection. Charlie register at sub-plan PFR adjudication after Codex independent verification of [UNVERIFIED] items.

---

## §9 Cycle-pattern observations (carry-forward from T1.4 cumulative + T1.1 9-iteration arc)

### §9.1 T1.4 cycle empirical (5-instance Advisor own-anchoring pattern at implementation-review iteration class)

Codified at [`feedback_advisor_own_anchoring_implementation_review.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_advisor_own_anchoring_implementation_review.md). Operational implications for T1.5:

- **Rule 1: Advisor APPROVE at implementation-review iteration class is SIGNAL not authoritative.** Apply at v_n PFR rounds + SEAL-eve.
- **Rule 2: Codex SEAL-eve adversarial OPERATIONALLY REQUIRED post PFR convergent APPROVE.** Apply at T1.5 SEAL gate.
- **Rule 3: Codex catches BLOCKING/HIGH at implementation-review → adjudication discount on Advisor's contemporaneous APPROVE/LOW-only.** Cumulative T1.4 record: 5/5 prior cycle positions had Codex substantive catch vs Advisor under-weight.
- **Rule 4: Apply MAXIMUM anti-anchoring discipline at Advisor brief.** Even MAXIMUM doesn't fully resolve pattern (T1.4 v4 SEAL-eve empirically demonstrated); still operationally LOAD-BEARING reducer.

### §9.2 T1.1 9-iteration arc empirical (producer-consumer asymmetry recurrence pattern)

Codified at [`feedback_invariant_level_vs_enumeration.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_invariant_level_vs_enumeration.md). Operational implications for T1.5:

- If T1.5 PFR iterations show recurrence pattern at the same defect class (e.g., 3+ iterations all closing BLOCKING at moment-estimator-band class), surface as candidate for invariant-level closure at producer layer (Contract 2.0.1 + 2.0.6 (a) producer = §2.1 test design itself, not the test implementation)
- Retain consumer-side mirrors as belt-and-suspenders + document with `DESIGN INVARIANT` marker per CLAUDE.md Contract Markers discipline
- Pattern signature most likely at §2.1 (5 alternative library values) and §2.3 (5 failure cases) — both have enumeration territory

### §9.3 Cross-model leg LOAD-BEARING (B2 standing rule LOCKED 2026-05-19)

5-cycle cumulative empirical (R2.0 + R3.1d + §34 + R2.3 + B2-housekeeping; reaffirmed at T1.1 + T1.4 within-arc 6+5 instances). Operational implications for T1.5:

- Codex catches Advisor would miss at every cycle position: ALWAYS dispatch 2-leg for SEAL-class artifact review rounds
- Advisor's `[VERIFIED]` tokens are NOT reliable evidence (Mode A structural failure); independent re-verification by orchestrator REQUIRED
- Codex's `[VERIFIED]` tokens ARE reliable evidence within tokenized verification scope (cumulative ~0% hallucination within tokens; 1/18 cite hallucination outside token discipline at §34 PFR-NEW-F2 single instance)

### §9.4 3-layer safety architecture (codified post-B2 R1 cycle 2026-05-20)

| Layer | Mechanism | Failure mode caught | T1.5 application |
|---|---|---|---|
| 1 | Advisor own-finding-anchoring discount self-declaration | Self-aware but insufficient | Applied at every Advisor brief; subagent §2.5.4 self-discounts demonstrated |
| 2 | Codex cross-model leg (no authorship anchor) | Adversarial reading absent in Advisor | Dispatch at every PFR + SEAL-eve |
| 3 | Orchestrator independent verification (final reading independent of both reviewer legs) | Cross-model leg framing gaps OR Advisor anchoring on general framing without grep-verified counter-evidence | Apply Mode A independent re-verification per [`feedback_reviewer_routing_subagent_default.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md); §2.5.2 spot-check applied at integration time |

All 3 layers LOAD-BEARING for T1.5 SEAL-class artifact discipline.

### §9.5 Library-version-empirical-revalidation discipline (cross-cycle 3-instance pattern from T1.1+T1.2+T1.4)

§2.1.4 5 alternative library values must be empirically re-verified at every library upgrade (scipy version drift in particular). Discipline: pinned scipy version in test environment + explicit revalidation step in test method docstring + `DESIGN INVARIANT` marker at test class header.

### §9.6 §35 codification adjacency (B-C-extended cycle SEAL deferred)

T1.5 work surfaces empirical material for METHODOLOGY_NOTES §35 codification candidate ("Data-preservation requirements for analytical methodology must be specified at the artifact-design boundary, not discovered at the consumption boundary") per R6.1 V_SEAL post-event. T1.5 sub-plan does NOT pre-codify §35; codification fires at B-C-extended cycle SEAL boundary per Charlie register anti-pre-emption preserve.

### §9.7 γ Hybrid drafting modality empirical (NEW observation — T1.5 v1 drafting)

First cycle within B-C-extended arc to use γ Hybrid drafting (orchestrator skeleton + subagent §2 detail-fill). Observation at v1 integration time:

- Subagent (`quant-research-advisor` opus, dispatch agentId `a0cc21961fcff600c`) returned ~600-line §2.1+§2.2+§2.3 content in 488s (~8 min)
- 6 explicit [UNVERIFIED] flags surfaced (correctly invites Codex PFR independent verification per Mode A discipline)
- Orchestrator Mode A spot-verification PASS on 15 load-bearing claims (zero hallucinations within tokenized [VERIFIED] scope)
- 3 NEW named sub-decisions surfaced (DS8/DS9/DS10) extending §8.2 from 7 to 10 entries
- Authorship-anchoring risk surfaced explicitly + routed to §6.4 cross-leg discipline (separate Advisor instance for reviewer leg)

**Cycle-pattern observation candidate:** γ Hybrid drafting modality may produce higher-density sub-decision surface than orchestrator-direct drafting (subagent's senior-quant lens surfaced 3 sub-decisions orchestrator skeleton missed). If observed across 2-3 future cycles, codify as standing observation for sub-plan drafting modality choice.

---

## §10 Task SEAL chain (post-ratify execution log; populated as cycle progresses)

(Populated at each register-event boundary)

| Stage | Status | Charlie register | Commit | Reviewer dispatch | Notes |
|---|---|---|---|---|---|
| T1.5 cycle ENTRY | AUTHORIZED 2026-05-23 | "T1.5 + T1.6 + B-C-extended cycle SEAL... authorized" | — | — | pre-auth scope: ENTRY only |
| Scope-class Path B register | REGISTERED 2026-05-23 | "Path B" | — | — | narrow scope: a + b + d |
| Sub-plan v1 drafting fire | AUTHORIZED 2026-05-23 | "authorized" | — | — | γ Hybrid modality |
| Subagent ratify | RATIFIED 2026-05-23 | "use quant-research-advisor" | — | — | per-deliverable detail-fill |
| Subagent §2 dispatch complete | COMPLETED 2026-05-23 | — | — | agentId `a0cc21961fcff600c` (488s wallclock) | §2.1+§2.2+§2.3 returned; 6 [UNVERIFIED] flags + 3 NEW DS surfaced |
| Orchestrator §2 integration | COMPLETED 2026-05-23 | — | — | Mode A spot-check PASS on 15 load-bearing claims | this commit (sub-plan v1 INTEGRATED) |
| DS2 register-event | **RATIFIED 2026-05-24** | "Option (i) + 同意must-ADOPT" 2026-05-24 | — | — | Option (i) canonical OHLCV slice; off-by-one fix ADOPTed; gap (a) acknowledgment ADOPTed; heavy-tail empirical archived |
| Sub-plan v1 PFR 2-leg dispatch (BL-Y Phase 1 blind-lean) | **COMPLETED 2026-05-24** | — | — | Codex (cross-model) + Advisor opus instance #2 | DIVERGED on DS2 + Q1 reading; CONVERGED on Q5 gap (a) + Codex F-NEW off-by-one catch ADOPTed |
| Sub-plan v1 → v2 integration | **COMPLETED 2026-05-24** | — | this commit | — | applies DS2 ratify + must-ADOPT items |
| Sub-plan v2 next-action register | RATIFIED 2026-05-24 | "G1 跑 PFR-rule-Y v2 评审" 2026-05-24 | — | — | Charlie G1 register on PFR-rule-Y v2 fire (conservative protection) |
| Sub-plan v2 PFR-rule-Y 2-leg dispatch | COMPLETED 2026-05-24 | — | — | Codex (cross-model) + Advisor opus instance #3 | DIVERGED on severity (Codex BLOCK; Advisor APPROVE-WITH-FINDINGS LOW); ADOPT Codex per Rule 3 + memory feedback_advisor_own_anchoring_implementation_review.md 6th cross-cycle instance |
| Sub-plan v2 → v3 integration (V3-F1/F2/F3/F4 fixes) | COMPLETED 2026-05-24 | "R1 ADOPT 上述 4 类修复" + "R2b PFR-rule-Y v4" 2026-05-24 | this commit | — | 11 surgical Edits applied; per Codex F-NEW substance + orchestrator Mode A re-verification upgrade |
| Sub-plan v3 PFR-rule-Y v4 dispatch (per Charlie R2b conservative) | COMPLETED 2026-05-24 | — | — | Codex (cross-model) + Advisor opus instance #4 | CONVERGED on APPROVE-WITH-FINDINGS; COMPLEMENTARY 5 findings (Codex LOW-1/LOW-2 + Advisor DEFECT-1 HIGH→MEDIUM + DEFECT-2 LOW + DEFECT-3 MEDIUM); Advisor instance #4 explicitly applied MAXIMUM anti-anchoring + counter to 6-instance pattern |
| Sub-plan v3 → v3.1 integration (5 findings ADOPTed) | COMPLETED 2026-05-24 | "ADOPT Orchestrator recommend + Fire v5 PFR-rule-Y → v_final ratify after" 2026-05-24 | this commit | — | 10 surgical Edits applied; per-fix adjudication per memory feedback_reviewer_suggestion_adjudication.md |
| Sub-plan v3.1 PFR-rule-Y v5 dispatch (per Charlie R5b conservative) | COMPLETED 2026-05-24 | — | — | Codex (cross-model) + Advisor opus instance #5 | CONVERGED on APPROVE-WITH-FINDINGS; 4 LOW micro-findings (1 CONVERGED L334 cross-ref drift + 1 Codex-unique Candidate-2 symmetry + 1 Advisor-unique §2.2.4 shorthand + 1 Advisor-unique DESIGN INVARIANT→CONTRACT GAP taxonomy); Advisor instance #5 MAX anti-anchoring applied + calibration accurate (no over-correction) |
| Sub-plan v3.1 → v3.2 integration (4 micro-findings ADOPTed) | COMPLETED 2026-05-24 | "R6a" 2026-05-24 | this commit | — | 5 surgical Edits applied; per-fix adjudication per memory feedback_reviewer_suggestion_adjudication.md; DESIGN INVARIANT → CONTRACT GAP re-tag with explicit trigger-condition framing per CLAUDE.md L297-300 |
| Sub-plan v3.2 v_final ratify | **RATIFIED 2026-05-24** | "R7a" 2026-05-24 | this commit (v_final ratify Edits) | — | v3.2 LOCKED as v_final sub-plan; no further sub-plan revisions without fresh Charlie register-event per §8.1; cycle convergence achieved at LOW micro-finding floor at v5 PFR-rule-Y; skip v6 PFR-rule-Y per R6a validated |
| Implementation work fire register | PENDING | — | — | — | Charlie register on (a) implementation modality choice (orchestrator-direct / subagent-dispatch / γ Hybrid) + (b) implementation work fire authorization per §6.3 + §8.1 gate 5 |
| Implementation work execution | PENDING | — | — | — | 3 test files per §2.1/§2.2/§2.3 file path locks: `tests/test_t1_5_fixture_moments.py` + `tests/test_t1_5_smoke_end_to_end.py` + `tests/test_t1_5_registry_integrity.py` |
| Implementation PFR rounds | PENDING | — | — | — | per §6.3; 2-leg dispatch analog of sub-plan PFR but on test code |
| Implementation SEAL-eve adversarial round | PENDING | — | — | — | OPERATIONALLY REQUIRED per §6.2 + memory `feedback_advisor_own_anchoring_implementation_review.md` Rule 2 + T1.4 v3 empirical (CANNOT SKIP after PFR convergent APPROVE) |
| T1.5 SEAL ratify | **RATIFIED 2026-05-24** | "SEAL-ratify-bundle 授权 ratify + commit + push" 2026-05-24 | this SEAL bundle commit | — | per Path C hybrid 2026-05-24 SEAL-eve v2 convergent assessment + v_impl_polish v2 inline fixes + DS-NEW (f) HIGH-1 successor cycle eligible-not-named per anti-pre-emption invariant-level closure |
| T1.5 SEAL commit + push | **COMPLETED 2026-05-24** | per SEAL-ratify-bundle Charlie register | this commit (5 files staged: sub-plan + T1.4 baseline + 3 NEW T1.5 test files; pre-existing scratch NOT staged) | — | SEAL bundle pushed to origin/main per Charlie SEAL-ratify-bundle 2026-05-24 |
| Sub-plan v_n PFR rounds | PENDING | — | — | — | per §6.1 |
| Sub-plan SEAL-eve adversarial | PENDING | — | — | — | per §6.2 |
| Sub-plan v_final ratify | PENDING | — | — | — | Charlie register |
| Implementation work fire | PENDING | — | — | — | Charlie register |
| Implementation PFR rounds | PENDING | — | — | — | per §6.3 |
| Implementation SEAL-eve adversarial | PENDING | — | — | — | per §6.3 |
| T1.5 SEAL ratify | PENDING | — | — | — | Charlie register |

---

## §11 Revision log

(Populated as v_n → v_n+1 revisions accumulate; each revision = consolidated entry with PFR finding adoptions + fix scope summary + reviewer round metadata)

### v1 (2026-05-23 sub-plan drafting fire + integration)

- **Drafting modality:** γ Hybrid (orchestrator skeleton + `quant-research-advisor` subagent §2 detail-fill in parallel)
- **Sections populated by orchestrator:** §1, §2.4, §2.5, §3-§11 (cycle metadata + scope + module integration + subagent provenance + pass criteria + exclusions + risks + reviewer plan + SEAL gate + anti-pre-emption + cycle-pattern observations + task SEAL chain + revision log)
- **Sections populated by subagent (INTEGRATED):** §2.1, §2.2, §2.3 — `quant-research-advisor` opus dispatch agentId `a0cc21961fcff600c` returned ~600 lines in 488s wallclock
- **Orchestrator Mode A spot-verification PASS (2026-05-23):** 5 prohibited kurtosis values + 10 file:line citations independently verified (§2.5.2 table); zero hallucinations within tokenized [VERIFIED] scope
- **New named sub-decisions surfaced by subagent (DS8/DS9/DS10):** extends §8.2 from 7 to 10 entries; awaiting Charlie register at sub-plan PFR adjudication
- **Subagent [UNVERIFIED] items (6 flagged):** §2.3.4 / §2.3.5 / §2.3.6 / §2.3.8 / §2.3.10 / §2.2.2 Option (i) feasibility; carry forward to Codex PFR independent verification per §2.5.3
- **Status:** integrated v1; reviewer dispatches gated on DS2 register-event + Charlie sub-plan reviewer dispatch fire authorization
- **Next action:** Charlie DS2 register-event (smoke-test data-source lock i/ii/iii) before 2-leg reviewer dispatch fire authorization

### v2 (2026-05-24 DS2 ratify + 2-leg PFR adoption)

- **DS2 register**: Charlie ratified **Option (i) canonical OHLCV slice** 2026-05-24 ("Option (i) + 同意must-ADOPT")
- **Q1 reading**: implicit (α) per DS2 = (i) entailment; explicit Charlie confirmation surfaceable on demand
- **2-leg BL-Y Phase 1 blind-lean reviewer round COMPLETED 2026-05-24**: Codex (cross-model adversarial; agentId tracked internally) + Advisor opus instance #2 (senior-quant + research-methodology lens; cross-leg discipline per §6.4; agentId tracked internally); DIVERGED on DS2 (Codex → i; Advisor → ii) + Q1 reading (Codex → α; Advisor → β); CONVERGED on Q5 gap (a)
- **Codex F-NEW ADOPTed**: §2.2.2 off-by-one bar-count fix (175 → 176 hourly bars; orchestrator independent re-execution at HEAD `56fe413` 2026-05-24 confirmed 176 bars actually present + 0 zero-volume + 0 NaN closes in slice)
- **Q5 gap (a) ADOPTed**: §4 row 13 new exclusion for "production-data anomaly handling (NaN/zero-volume/gap-window axes) at engine→writer chain on real-data shape"; §8.2 DS-NEW (e) successor cycle eligible-not-named per anti-pre-emption
- **Heavy-tail empirical archived (methodology basis disclosed per v3.1 v4-PFR-rule-Y Advisor DEFECT-3 ADOPTed)**: log-return basis (`np.log(close).diff()` over N=175 returns from 176 bars) — Codex independent measurement γ4 ≈ 13.67 / synthetic 3.59 at seed=1557; orchestrator Mode A re-verified γ4 = 13.73 / synthetic = 3.61 at HEAD `56fe413` 2026-05-24; v4 PFR-rule-Y Advisor instance #4 independent measurement at pct_change basis (`close.pct_change()` over N=175 returns) γ4 ≈ 13.89; orchestrator independent re-verification both bases at HEAD `56fe413` confirmed (log-return γ4 = 13.7264; pct_change γ4 = 13.8900); confirms Option (i) materially exercises heavy-tail axis (3.8× divergence over synthetic Gaussian under either basis) — closes 1 of 4 production-shape axes; remaining 3 axes (NaN bars + zero-volume bars + gap-window axes) deferred to DS-NEW (e) successor cycle per V3-F4 reconciliation 2026-05-24
- **Advisor instance #2 [VERIFIED] Mode A spot-check PASS**: parent plan v5 line 186 verbatim + parent plan v5 §8 line 429 Backtrader determinism risk + T1.4 B3.4 smart-mock characterization all VERIFY clean; consistent with cumulative post-/agents-fix opus 0/13+ track record
- **BL-Y Phase 3 lean injection fired** on DIVERGENCE per [`feedback_reviewer_routing_subagent_default.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_reviewer_routing_subagent_default.md): orchestrator lean trajectory disclosed (pre-2-leg lean Option ii → post-Codex-empirical Option i lean medium-low confidence); Charlie register resolved DS2 divergence per authorization-routing discipline
- **Status**: v2 integrated; awaiting Charlie register for next gate (v2 PFR-rule-Y re-review on new-content fixes — §4 row 13 + §8.2 DS-NEW (e) are NEW content beyond literal reviewer adoption — OR v_final ratify per anti-pre-emption discipline)
- **Next action**: Charlie register on next gate decision (PFR-rule-Y v2 re-review OR v_final ratify)

### v3 (2026-05-24 V3-F1/F2/F3/F4 fixes per Charlie R1 ADOPT + R2b conservative)

- **Charlie R1 ADOPT**: all 4 V3 fix categories authorized 2026-05-24 ("ADOPT 上述 4 类修复(V3-F1/F2/F3/F4) 是")
- **Charlie R2b conservative**: PFR-rule-Y v4 round to fire after v3 fixes before v_final ratify
- **Charlie R3 implicit Option A**: silent acceptance of orchestrator lean (§11 axes count "1 of 4; 3 remaining")
- **Charlie R4 deferred**: memory update on 6-instance Advisor own-anchoring reaffirmation deferred to T1.5 SEAL or cycle SEAL boundary per anti-pre-emption
- **V3-F1 BLOCKING propagation (5 sites; line numbers approximate per pre-edit layout — shift with subsequent edits per v3.1 Codex LOW-2 annotation)**: L262 + L278 + L295 + L327 + L377-379 stale "175" → "176" + warmup-aware reframing at L377-379 (SMA(5/20) → 156 post-warmup; SMA(10/30) → 146 post-warmup); orchestrator Mode A upgrade beyond Codex catch scope (Codex flagged 1-2 sites; orchestrator grep upgraded to 5 sites)
- **V3-F2 MEDIUM PLACEHOLDER stale (4 sites; line numbers approximate per pre-edit layout — shift with subsequent edits per v3.1 Codex LOW-2 annotation)**: L30 (§1.1 table) + L231 (§2.2 header) + L241 (§2.2.2 subsection) + L481 (§2.2.9 conditional) "PLACEHOLDER / do NOT lock" → "DS2 RATIFIED Option (i) 2026-05-24" / "RESOLVED 2026-05-24"; orchestrator Mode A upgrade beyond Codex catch scope (Codex flagged 1 site; orchestrator grep upgraded to 4 sites)
- **V3-F3 LOW anchor drift**: §2.2.2-historical heading added between Option (i) downstream content and Option (ii) historical-record preserved content (Codex F-NEW-3 catch)
- **V3-F4 MEDIUM axes count reconcile**: §11 v2 entry "1 of 5 production-shape axes; remaining 4 axes" → "1 of 4 production-shape axes; remaining 3 axes (NaN bars + zero-volume bars + gap-window axes)"; resolves §11-vs-§8.2 DS-NEW (e) count mismatch per V3-F4
- **6-instance Advisor own-anchoring cross-cycle empirical**: T1.5 v2 PFR-rule-Y is 6th instance of pattern codified at [`feedback_advisor_own_anchoring_implementation_review.md`](file:///Users/yutianyang/.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_advisor_own_anchoring_implementation_review.md) (5 T1.4 instances + 1 T1.5 v2 PFR-rule-Y); standing rule reaffirmation deferred to T1.5 SEAL boundary per Charlie register-implicit
- **Status**: v3 integrated; awaiting Charlie register for v4 PFR-rule-Y 2-leg dispatch fire per R2b conservative protection
- **Next action**: Charlie register on v4 PFR-rule-Y 2-leg dispatch fire authorization

### v3.1 (2026-05-24 V4-PFR-rule-Y 5 findings ADOPTed per Charlie R1' + R5b)

- **v4 PFR-rule-Y 2-leg outcome (2026-05-24)**: Codex (cross-model) APPROVE-WITH-FINDINGS (2 LOW: §2.2.9 wording confusion + §11 line-drift labels) + Advisor opus instance #4 APPROVE-WITH-FINDINGS (3 defects: DEFECT-1 HIGH→MEDIUM warmup convention divergence disclosure gap + DEFECT-2 LOW SMA notation ambiguity + DEFECT-3 MEDIUM γ4 basis disclosure); CONVERGED on APPROVE; COMPLEMENTARY findings (non-overlapping); per BL-Y memory definition CONVERGENT counts as not-divergent → orchestrator does NOT inject DS-level lean; per-fix adjudication discipline applies
- **Advisor instance #4 MAXIMUM anti-anchoring discipline applied**: deliberately surfaced DEFECT-1 at HIGH (not LOW) to counter prior instance #3's under-weighing tendency at v2 PFR-rule-Y; orchestrator adjudicated DEFECT-1 severity DOWN to MEDIUM (HIGH was over-correction by 1 notch; §2.2.3 explicit lock to hand-written SMACrossover makes current arithmetic correct; future-cycle drift risk is real but bounded by §2.2.3 explicit lock)
- **Charlie R1' ADOPT all 5 orchestrator recommendations 2026-05-24** ("Per-fix ADOPT Orchestrator recommend"): per-fix adjudication discipline preserved (no bulk-accept); 5 mechanical inline fixes applied
- **Charlie R5b conservative 2026-05-24** ("Fire v5 PFR-rule-Y → v_final ratify after"): another PFR-rule-Y round before v_final ratify per defense-in-depth pattern; consistent with R2b conservative precedent
- **Charlie R4' deferred**: memory update on 6-instance + Codex 2-LOW-only at v4 PFR-rule-Y empirical reaffirmation deferred to T1.5 SEAL or cycle SEAL boundary per anti-pre-emption
- **Codex LOW-1 §2.2.9 wording (ADOPTed)**: separated "Current state" (RESOLVED) from "Historical record" (pre-ratify framing) from "Discharged actions post-ratify"; clean 3-block structure replaces prior mixed historical/future wording
- **Codex LOW-2 §11 line drift (PUSHBACK + annotation)**: line numbers in v3 entry V3-F1/F2 descriptions annotated as "approximate per pre-edit layout — shift with subsequent edits" rather than re-numbering; structurally cleaner since line numbers will continue to drift with future Edits
- **Advisor DEFECT-1 warmup convention DESIGN INVARIANT (HIGH→MEDIUM ADOPTed)**: §2.2.3 candidates updated with explicit warmup convention reference (`SMACrossover.WARMUP_BARS = slow_period` per L51) + DESIGN INVARIANT marker disclosing 1-bar drift risk if T1.6 refactors to DSL-compiled crossover; fresh Charlie register-event required for any DSL refactor + PASS band recalibration
- **Advisor DEFECT-2 SMA notation (ADOPTed)**: §2.2.3 candidates updated from "SMA(5/20)" to "(fast_period=5, slow_period=20)" notation; eliminates fast/slow ambiguity
- **Advisor DEFECT-3 γ4 basis disclosure (ADOPTed at 3 sites)**: L262 + L381-383 + §11 v2 entry updated with explicit "log-return basis (`np.log(close).diff()` over N=175 returns from 176 bars)" disclosure for γ4 ≈ 13.73 claim + cross-reference to pct_change basis γ4 ≈ 13.89 alternative; orchestrator independent re-verification both bases at HEAD `56fe413` confirmed (log_return γ4 = 13.7264; pct_change γ4 = 13.8900)
- **Mode A spot-check both legs PASS at v4 PFR-rule-Y**: Codex empirical claims (5-site V3-F1 verification + 4-site V3-F2 verification + γ4 ≈ 13.89 measurement) + Advisor instance #4 empirical claims (SMACrossover L51 + factors L83/L93 + DSL compiler L642+ + γ4 reconciliation) all VERIFY clean via orchestrator independent re-execution at HEAD `56fe413` 2026-05-24
- **6+1-instance Advisor own-anchoring cross-cycle empirical reaffirmation**: T1.5 v4 PFR-rule-Y is 7th observation of pattern (v2 PFR-rule-Y was 6th; v4 PFR-rule-Y instance #4 explicit counter-discipline application IS the 7th data point — Advisor surfaced HIGH at DEFECT-1 to counter prior LOW-only pattern; whether this counter-discipline application worked is itself data); standing rule reaffirmation deferred to T1.5 SEAL boundary per Charlie R4' implicit
- **Status**: v3.1 integrated; awaiting Charlie register for v5 PFR-rule-Y 2-leg dispatch fire per R5b conservative protection
- **Next action**: Charlie register on v5 PFR-rule-Y 2-leg dispatch fire authorization

### v3.2 (2026-05-24 V5-PFR-rule-Y 4 LOW micro-findings ADOPTed per Charlie R6a)

- **v5 PFR-rule-Y 2-leg outcome (2026-05-24)**: Codex (cross-model) APPROVE-WITH-FINDINGS (2 LOW: L334 cross-ref drift + Candidate-2 symmetry break) + Advisor opus instance #5 APPROVE-WITH-FINDINGS (3 LOW: DEFECT-MICRO-1 L334 cross-ref drift CONVERGED + DEFECT-MICRO-2 §2.2.4 L383 shorthand inconsistency + DEFECT-MICRO-3 DESIGN INVARIANT vs CONTRACT GAP taxonomy partial-fit); CONVERGED on APPROVE; COMPLEMENTARY 4 LOW findings (1 CONVERGED + 1 Codex-unique + 2 Advisor-unique); no BLOCKING/HIGH/MEDIUM
- **Advisor instance #5 MAX anti-anchoring discipline empirically calibrated**: caught real defects (1 CONVERGED + 2 unique) AND did NOT over-correct on severity (all LOW; no HIGH-stretched). Compared to instance #3 (under-weighed at v2 PFR-rule-Y; Codex BLOCK ADOPTed per Rule 3) + instance #4 (HIGH-stretched DEFECT-1 at v4 PFR-rule-Y; orchestrator down-adjudicated to MEDIUM), instance #5's calibration looks empirically more accurate — MAX-discipline + explicit cumulative-pattern framing in brief works partially
- **Charlie R6a ADOPT all 4 + skip v6 PFR-rule-Y 2026-05-24** ("R6a 我推荐"): per-fix adjudication discipline preserved; 5 mechanical Edits applied; v6 PFR-rule-Y skipped per "mechanical literal application of CONVERGED/COMPLEMENTARY reviewer findings" PFR-rule-Y skip criterion
- **Fix 1 (CONVERGED) + Fix 4 (Advisor-unique) combined ADOPTed via single Edit at §2.2.3 DESIGN INVARIANT block**: L334 cross-ref "L336 below" → "L338 below" + DESIGN INVARIANT tag re-classified to CONTRACT GAP per CLAUDE.md L297-300 strict-reading (trigger-condition framing dominates) + explicit "Trigger condition" heading added per CLAUDE.md Contract Markers discipline ("CONTRACT GAP = a test or mechanism that should exist but doesn't yet, with a trigger condition that will require adding it")
- **Fix 2 (Codex-unique) ADOPTed at §2.2.3 Candidate 2**: added `SMACrossover.` class prefix + repeated `strategies/baseline/sma_crossover.py:51` file:line cite to Candidate 2 line; symmetry with Candidate 1 restored
- **Fix 3 (Advisor-unique) ADOPTed at §2.2.4 L383**: shorthand "SMA(5/20)" + "SMA(10/30)" → explicit "SMA (fast_period=5, slow_period=20)" + "SMA (fast_period=10, slow_period=30)"; surface consistency with §2.2.3 explicit-keyword form restored
- **Mode A spot-check both legs PASS at v5 PFR-rule-Y**: all 4 LOW micro-findings VERIFY clean via orchestrator independent grep/Read at HEAD `56fe413` 2026-05-24
- **6+1+1-instance Advisor own-anchoring cross-cycle empirical update**: T1.5 v5 PFR-rule-Y is 8th observation (5 T1.4 instances + T1.5 v2 PFR-rule-Y + T1.5 v4 PFR-rule-Y + T1.5 v5 PFR-rule-Y); calibration trajectory: instance #3 under-weighed → instance #4 over-corrected (HIGH-stretch) → instance #5 calibrated accurately (all LOW; no over/under-correction). Standing rule reaffirmation deferred to T1.5 SEAL boundary per Charlie R4' implicit; cycle pattern observation evolved from "Advisor under-weighs at implementation-review" to "Advisor calibration trajectory under MAX-discipline framing: under-weigh → over-correct → accurate (3-instance progression at T1.5)"
- **Status**: v3.2 integrated; cycle saturation point reached at T1.5 sub-plan level (1 substantive PFR + 3 PFR-rule-Y rounds; 6 reviewer dispatches; ~30 cumulative findings tracked); awaiting Charlie register for v_final ratify per R6a (v6 PFR-rule-Y skipped per R6a)
- **Next action**: Charlie register on v_final ratify decision (sub-plan ratify Charlie register-event)

### v_final ratify (2026-05-24 Charlie R7a register — v3.2 RATIFIED as locked sub-plan)

- **Charlie R7a register 2026-05-24** ("R7a"): v3.2 RATIFIED as v_final locked sub-plan
- **Sub-plan ratify status**: LOCKED — no further sub-plan revisions without fresh Charlie register-event boundary per §8.1 anti-pre-emption
- **Cycle final statistics**: 5 versions (v1 → v2 → v3 → v3.1 → v3.2 = v_final) + 4 reviewer rounds (1 v1 PFR + 3 PFR-rule-Y) + 8 reviewer dispatches + ~17 findings tracked + RESOLVED + cycle convergence achieved at LOW micro-finding floor at v5 PFR-rule-Y
- **CONVERGED outcomes locked at v_final**: DS2 = Option (i) canonical OHLCV slice (176 hourly bars from 2023-08-01T00:00Z to 2023-08-08T07:00Z; log-return basis for γ4 ≈ 13.73 empirical) + 4 V3-F categories (off-by-one fix + PLACEHOLDER → RATIFIED + anchor heading + axes count reconcile) + 5 v4-PFR-rule-Y findings (Codex 2 LOW + Advisor 3 DEFECT) + 4 v5-PFR-rule-Y LOW micro-findings (1 CONVERGED L334 cross-ref + 1 Codex-unique Candidate-2 symmetry + 1 Advisor-unique §2.2.4 shorthand + 1 Advisor-unique CONTRACT GAP taxonomy re-tag)
- **Cross-cycle empirical contributions** (memory update candidates per Charlie R4' deferred to T1.5 SEAL or B-C-extended cycle SEAL boundary):
  1. **8-instance Advisor own-anchoring cross-cycle pattern** (5 T1.4 + 3 T1.5 PFR-rule-Y; calibration trajectory under-weigh → over-correct → calibrated under MAX-discipline framing) — extends `feedback_advisor_own_anchoring_implementation_review.md` empirical foundation
  2. **γ Hybrid drafting modality empirically validated** as effective for sub-plan substantial drafting + surfaces additional named sub-decisions (3 NEW DS surfaced beyond skeleton)
  3. **Codex BLOCK adoption per Rule 3 empirically validated** when Advisor under-weighs at implementation-review iteration class (v2 PFR-rule-Y instance #3)
  4. **Mode A independent re-verification (3-layer safety architecture Layer 3)** caught propagation drift beyond reviewer scope at v2 PFR-rule-Y → v3 integration scope upgrade (Codex flagged 1-2 sites; orchestrator grep upgraded to 5 sites for V3-F1 + 1 → 4 sites for V3-F2)
  5. **PFR-rule-Y v5 cycle saturation observation**: convergence achieved at LOW micro-finding floor; R6a "skip v6 mechanical literal application" criterion empirically validated as appropriate
- **Status**: v_final RATIFIED + sub-plan LOCKED; awaiting Charlie register for next gate per §6.3 (implementation work fire register)
- **Next action**: Charlie register-event on implementation work fire authorization (separate register per §8.1 gates 4 → 5)

### v_impl_polish_v2 (2026-05-24 SEAL-eve v2 BLOCK adoption per Path C hybrid)

- **SEAL-eve v1 2-leg outcome 2026-05-24**: Codex BLOCK (2 HIGH structural coverage gaps) + Advisor #7 APPROVE-WITH-FINDINGS (3 LOW + 2 MEDIUM); ADOPT Codex BLOCK per Rule 3 → v_impl_polish v1 ADOPTed 6 fixes
- **SEAL-eve v2 2-leg outcome 2026-05-24** (re-fire per Charlie SE1 conservative): Codex BLOCK (2 CONVERGED HIGH partial-closure + Codex-unique HIGH F real parquet hash + MEDIUM B/E + LOW C) + Advisor opus instance #8 APPROVE-WITH-FINDINGS (2 CONVERGED HIGH partial-closure + LOW dead-code); ADOPT Codex BLOCK per Rule 3 + producer-consumer asymmetry recurrence pattern detected per `feedback_invariant_level_vs_enumeration.md` framework
- **Charlie Path C hybrid register 2026-05-24** ("Path C — Hybrid"): apply easy v_impl_polish v2 inline fixes (HIGH-2 closure tight + HIGH-F real parquet hash + MEDIUM B/E + LOW C/dead-code); defer HARD HIGH-1 (smoke artifact-writer + schema-validator chain coverage) to §8.2 DS-NEW (f) successor cycle per anti-pre-emption invariant-level closure
- **v_impl_polish v2 inline fixes applied**:
  - HIGH-2 closure tight (CONVERGED): added 3 deferred-state T1.x column assertions (`T_obs == 10` + `returns_per_bar_path == ""` + `returns_per_bar_sha256 == ""`) at `test_triple_resolution_happy_path` → 9-of-9 T1.x columns asserted per §2.3.2 spec
  - HIGH-F real parquet hash (Codex-unique): smoke `_make_smoke_lineage_context` defaults to real DS2 OHLCV bytes SHA256 (computed via `_compute_ds2_window_ohlcv_sha256()`); registry test uses deterministic real hash via `hashlib.sha256(b"triple-test-parquet-bytes").hexdigest()`; closes producer-consumer placeholder-vs-real asymmetry
  - MEDIUM B pollution guard recursive (Codex-unique): changed `iterdir() + is_file()` to `rglob("*") + is_file()` for recursive snapshot; catches subdirectory writes
  - MEDIUM E CONTRACT GAP marker (Codex-unique): added formal CONTRACT GAP marker text near T_obs=10 placeholder in `_make_smoke_lineage_context` docstring per CLAUDE.md L297-300; trigger condition + closure mechanism + cross-reference to DS-NEW (f)
  - LOW C OHLCV docs update (Codex-unique): module docstring "close-price bytes" → "5-col OHLCV (open + high + low + close + volume) bytes" with explicit engine-consumption justification
  - LOW dead-code removal (Advisor-unique): removed `hasattr(result, "equity_curve")` + `get_equity_curve()` fallback at smoke L451-453 (BacktestResult @dataclass guarantees field per engine.py:635-649)
- **HIGH-1 DEFERRED via §8.2 DS-NEW (f) per Path C invariant-level closure**: smoke artifact-writer + schema-validator chain coverage (production `write_per_bar_artifact()` + `check_b_c_extended_semantics_or_raise()` invocation) NOT exercised at T1.5 SEAL due to deferred-state LATE_FILL bypass; explicit-deferral-with-successor-cycle-naming per anti-pre-emption discipline (matches DS-NEW (e) production-data-anomaly pattern); §8.2 DS-NEW (f) eligible-not-named successor cycle "T1.5-followup smoke artifact-writer + schema-validator chain coverage"
- **Cycle saturation observation**: 7 adversarial cycles + 16+ reviewer dispatches across T1.5; producer-consumer asymmetry recurrence pattern empirically observed (SEAL-eve v1 caught HIGH → v_impl_polish v1 partial closure → SEAL-eve v2 caught next-narrowest at writer-validator boundary + parquet hash placeholder + 3 deferred-state fields); Path C invariant-level closure via explicit-deferral-with-successor-cycle-naming is structurally cleaner than continued enumeration per T1.1 9-iteration arc framework
- **12+1-instance Advisor own-anchoring cross-cycle pattern at SEAL-eve v2 boundary**: instance #8 dispatched with MAXIMUM anti-anchoring + acknowledged cumulative pattern; calibrated accurately on substantive findings but slight tendency to soften severity (APPROVE-WITH-FINDINGS vs Codex BLOCK at CONVERGED HIGH) — pattern persists with attenuated magnitude
- **Skip re-SEAL-eve v3 per Path C saturation observation**: cycle empirical justifies; continued enumeration would spawn next-narrowest asymmetry without invariant closure
- **Status**: v_impl_polish v2 integrated; full suite zero-regression verified (2317 collected; 2315 PASS + 2 xfail + 0 FAIL); awaiting Charlie register for T1.5 SEAL ratify
- **Next action**: Charlie register on T1.5 SEAL ratify + SEAL bundle commit + push

### v_seal (2026-05-24 T1.5 SEAL ratify + commit + push per Charlie SEAL-ratify-bundle)

- **Charlie SEAL-ratify-bundle register 2026-05-24** ("SEAL-ratify-bundle 授权 ratify + commit + push"): single register covers (a) T1.5 SEAL ratify decision + (b) SEAL bundle commit fire + (c) git push to origin/main per v_final R7a + commit-bundle pattern + T1.4 SEAL `5a44ec6` precedent
- **T1.5 SEAL bundle scope**: 5 files staged (sub-plan v3.2 RATIFIED + v_impl_polish v1 + v_impl_polish_v2 + v_seal record + §8.2 DS-NEW (e) + (f) + §11 task SEAL chain + T1.4 B1 baseline maintenance per Charlie B1 register 2026-05-24 + 3 NEW T1.5 test files); pre-existing scratch NOT staged (backtest/engine.py,cover + coverage.json + R5.1/R5.2/R6.1 plan docs scratch — pre-T1.5 untracked work)
- **T1.5 SEAL final state**: 20 T1.5 tests (18 PASS + 2 xfail DS8 PENDING per anti-pre-emption); full suite 2317 collected zero-regression preserved (2315 PASS + 2 xfail + 0 FAIL) per CLAUDE.md HARD CONSTRAINT pc7 + §3.1 PASS criteria item 2; 2 eligible-not-named successor cycles registered at §8.2 (DS-NEW (e) production-data-anomaly + DS-NEW (f) artifact-writer + schema-validator chain coverage) per anti-pre-emption discipline
- **T1.5 cycle final empirical**: 7 adversarial cycles (1 sub-plan PFR + 3 PFR-rule-Y + 1 Implementation PFR + 2 SEAL-eve) + 16+ reviewer dispatches across 8 Advisor instances + Codex cross-model leg per cross-leg discipline §6.4 + B2 standing rule LOCKED 2026-05-19; producer-consumer asymmetry recurrence pattern empirically observed at SEAL-eve v1 → v_impl_polish v1 → SEAL-eve v2 → v_impl_polish v2 → Path C invariant-level closure (next-narrowest asymmetry at writer-validator boundary deferred to DS-NEW (f) successor cycle per `feedback_invariant_level_vs_enumeration.md` cycle empirical 2026-05-24 analog of T1.1 9-iteration arc)
- **T1.5 SEAL cumulative empirical contributions to memory** (codification deferred to B-C-extended cycle SEAL boundary per Charlie R4'): 12+ instance Advisor own-anchoring cross-cycle pattern reaffirmation (`feedback_advisor_own_anchoring_implementation_review.md`) + SEAL-eve adversarial discipline empirically LOAD-BEARING (Rule 2 v1 + v2 both caught HIGH that PFR convergent APPROVE missed) + γ Hybrid drafting modality validated at sub-plan drafting + M1 orchestrator-direct validated at implementation work + CONTRACT GAP marker discipline applied 2x at sub-plan §2.2.3 + v_impl_polish_v2 T_obs=10 placeholder + Path C hybrid invariant-level closure framework empirically validated (`feedback_invariant_level_vs_enumeration.md` extension)
- **Status**: T1.5 SEAL committed + pushed to origin/main; sub-plan v3.2 + v_seal LOCKED per §8.1 anti-pre-emption
- **Next action**: Charlie register on T1.6 cycle ENTRY per anti-pre-emption (pre-authorized at sub-plan ratify but each downstream gate within T1.6 requires fresh register) per execution order T1.2 → T1.3 → T1.1 → T1.4 → T1.5 → T1.6 → B-C-extended cycle SEAL
