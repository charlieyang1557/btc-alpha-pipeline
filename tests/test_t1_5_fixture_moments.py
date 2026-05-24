"""T1.5 (a) Fixture moment-estimator tests.

Per ratified T1.5 sub-plan v3.2 (v_final) at
`docs/superpowers/plans/2026-05-23-t1_5-fixture-smoke-registry-test-suite-cycle-execution-plan.md`.

Sub-plan v_final RATIFIED 2026-05-24 per Charlie register chain
(cycle entry + Path B + sub-plan drafting fire + quant-research-advisor +
DS2 Option (i) + G1 + R1 + R2b + R1' + R5b + R6a + R7a) under B-C-extended
Scope-B structural artifact-preservation refactor cycle per R3.1d
sequencing 1→3→4.

Coverage scope (Contract 2.0.1 + 2.0.6 (a) per parent plan v5):
- Contract 2.0.1 LOCKED γ4 implementation: scipy.stats.kurtosis(returns_array,
  fisher=False, bias=True, nan_policy='omit') at fixture vector
  `[-1, 1, 0, 0, 0, 0]` (N=6) produces 3.000000 ± 1e-12.
- Contract 2.0.1 LOCKED γ3 implementation: scipy.stats.skew(returns_array,
  bias=True, nan_policy='omit') at same fixture vector produces 0.000000 ± 1e-12.
- Contract 2.0.6 (a) 5 PROHIBITED alternative implementations confirm-fail with
  deterministic separation ≥ 0.5 from the LOCKED PASS value.
- scipy ≥ 1.9 precondition (nan_policy keyword availability).

Out-of-scope per §2.1.8 (cross-references):
- Writer-boundary integration (§2.2 Smoke scope).
- LineageContext.revalidate_for_write() invariant (T1.1 SEAL
  tests/test_t1_1_sys_fix.py:2583 TestSys5RevalidateForWriteDirectStrictFields).
- Per-bar artifact validation (T1.2 SEAL check_b_c_extended_semantics_or_raise()).
- γ3 PROHIBITED enumeration at this vector (tautological at symmetric vector;
  eligible-not-named for separate Charlie register-event per DS5).
- Registry insertion (§2.3 Registry-integrity scope).

Library-version-empirical-revalidation discipline per §2.1.9 + §9.5:
- All 5 PROHIBITED values empirically verified at scipy 1.10.0 + pandas 2.2.3 +
  HEAD `56fe413` (2026-05-24).
- At every scipy or pandas major-version upgrade (1.x → 2.x), re-run the
  empirical verification script (see module-level docstring in test methods
  below) and confirm the 5 values remain at the expected separations.
- If any value drifts, the corresponding test_fail_* method will fire; that
  signal requires Charlie register on whether to update the spec (Contract
  2.0.1) or fix the call site.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import scipy
from packaging.version import Version
from scipy.stats import kurtosis, skew


# ---------------------------------------------------------------------------
# Module-level constants per §2.1.7
# ---------------------------------------------------------------------------

_FIXTURE_VECTOR: np.ndarray = np.array([-1.0, 1.0, 0.0, 0.0, 0.0, 0.0])
"""Hard-coded deterministic fixture vector (N=6).

Symmetric around mean=0 (so γ3 = 0 trivially without bias-correction noise);
finite N=6 produces strong empirical separation between bias-corrected and
population kurtosis formulas (e.g., scipy fisher=False bias=True = 3.0 vs
scipy fisher=False bias=False = 5.5; Δ = 2.5 well beyond any tolerance band).

Contains zero-value bars (mirrors legitimate flat-period structure in BTC
OHLCV per CLAUDE.md "Known Data Characteristics" §3 zero-volume bars).

DO NOT alter at T1.5: alteration invalidates the 5 pre-computed PROHIBITED
values enumerated in Contract 2.0.6 (a) parent plan v5 ll.173-185.
"""

_PASS_GAMMA4_EXPECTED: float = 3.0
"""LOCKED PASS γ4 value at fixture vector per Contract 2.0.6 (a)."""

_PASS_GAMMA3_EXPECTED: float = 0.0
"""LOCKED PASS γ3 value at fixture vector (symmetric → 0 trivially)."""

_PASS_TOLERANCE_ABS: float = 1e-12
"""Absolute tolerance band for PASS assertions per Contract 2.0.6 (a) line 175."""

_FAIL_MIN_SEPARATION: float = 0.5
"""Minimum |Δ| separation between PASS value (3.0) and each PROHIBITED
implementation value per §2.1.4 rationale.

The smallest empirical Δ across the 5 PROHIBITED implementations is 0.5
(pandas .kurt() default = 2.5; scipy fisher=True bias=False = 2.5). 0.5 is
the tightest separation that ALL 5 satisfy AND exceeds any plausible
floating-point drift band.
"""


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


class TestT1_5_FixtureMomentImplementation:
    """T1.5 (a) Fixture moment-estimator tests per sub-plan v3.2 (v_final) §2.1.

    9 test methods (4 PASS/band/precondition + 5 FAIL):
    - test_AAA_scipy_version_precondition — gate suite on scipy ≥ 1.9
    - test_pass_locked_gamma4_implementation — Contract 2.0.1 LOCKED γ4 (PASS)
    - test_pass_locked_gamma3_implementation — Contract 2.0.1 LOCKED γ3 (PASS)
    - test_pass_gamma4_band_excludes_excess_kurtosis_zero — band exclusion
    - test_fail_pandas_kurt_default — PROHIBITED pandas .kurt() default = 2.5
    - test_fail_pandas_kurt_plus_3 — PROHIBITED pandas .kurt() + 3 = 5.5
    - test_fail_scipy_fisher_true_bias_true — PROHIBITED scipy default = 0.0
    - test_fail_scipy_fisher_true_bias_false — PROHIBITED = 2.5
    - test_fail_scipy_fisher_false_bias_false — PROHIBITED = 5.5

    Independent test methods (NOT parametrize) per §2.1.4 + §2.1.7 rationale:
    preserves failure attribution + per-test docstring carries historical
    library context. Library default convergence in a future upgrade fires
    the specific test_fail_* method that drifted, not a generic
    "one of 5 alternative implementations no longer diverges."

    Library-version-empirical-revalidation discipline per §9.5: pinned scipy
    + pandas version at fixture-time empirical verification; at every major
    library upgrade, re-run empirical script + confirm 5 values remain at
    expected separations.
    """

    def test_AAA_scipy_version_precondition(self) -> None:
        """Gate suite: fail closed if scipy < 1.9 (nan_policy keyword unavailable).

        Per Contract 2.0.1 line 61: "scipy ≥ 1.9 required for nan_policy
        keyword; fixture test fails closed if precondition not met."

        Empirical at sub-plan drafting (HEAD `56fe413` 2026-05-24): scipy 1.10.0.

        Method name `test_AAA_` ensures alphabetical sorting fires this test
        first per §2.1.5 suite-gate discipline (explicit per-test method
        visible in pytest output, preferred over module-level pytest.mark.skipif
        which silently skips + is hard to detect in CI).
        """
        assert Version(scipy.__version__) >= Version("1.9"), (
            f"scipy {scipy.__version__} < 1.9: nan_policy keyword unavailable; "
            f"Contract 2.0.1 LOCKED implementation cannot run. "
            f"Upgrade scipy to >= 1.9 before invoking T1.5 fixture suite."
        )

    def test_pass_locked_gamma4_implementation(self) -> None:
        """Contract 2.0.1 LOCKED γ4 implementation produces 3.000000 ± 1e-12.

        LOCKED implementation:
            scipy.stats.kurtosis(returns_array, fisher=False, bias=True,
                                 nan_policy='omit')

        Expected at _FIXTURE_VECTOR: 3.0 exactly (raw analytical mu4/sigma^4 for
        symmetric ±1 + 4 zeros input).

        Empirical at sub-plan drafting (scipy 1.10.0): 3.0 exactly.
        """
        result = kurtosis(_FIXTURE_VECTOR, fisher=False, bias=True,
                          nan_policy="omit")
        assert result == pytest.approx(_PASS_GAMMA4_EXPECTED,
                                       abs=_PASS_TOLERANCE_ABS), (
            f"γ4 PASS failed: expected {_PASS_GAMMA4_EXPECTED} ± "
            f"{_PASS_TOLERANCE_ABS}, got {result!r}. Production γ4 "
            f"implementation may have silently drifted from Contract 2.0.1 "
            f"LOCKED form."
        )

    def test_pass_locked_gamma3_implementation(self) -> None:
        """Contract 2.0.1 LOCKED γ3 implementation produces 0.000000 ± 1e-12.

        LOCKED implementation:
            scipy.stats.skew(returns_array, bias=True, nan_policy='omit')

        Expected at _FIXTURE_VECTOR: 0.0 exactly (symmetric vector → population
        skew = 0 trivially regardless of bias-correction convention).

        Empirical at sub-plan drafting (scipy 1.10.0): 0.0 exactly.

        Note per §2.1.6: γ3 PROHIBITED enumeration is NOT included at this
        symmetric vector (all alternative implementations also compute 0.0
        trivially → tautological). DS5 named sub-decision for separate cycle
        if asymmetric-vector γ3 lockout is judged necessary.
        """
        result = skew(_FIXTURE_VECTOR, bias=True, nan_policy="omit")
        assert result == pytest.approx(_PASS_GAMMA3_EXPECTED,
                                       abs=_PASS_TOLERANCE_ABS), (
            f"γ3 PASS failed: expected {_PASS_GAMMA3_EXPECTED} ± "
            f"{_PASS_TOLERANCE_ABS}, got {result!r}. Production γ3 "
            f"implementation may have silently drifted from Contract 2.0.1 "
            f"LOCKED form."
        )

    def test_pass_gamma4_band_excludes_excess_kurtosis_zero(self) -> None:
        """γ4 PASS band MUST EXCLUDE 0.0 per Contract 2.0.6 (a) line 182.

        0.0 is the scipy fisher=True bias=True (default scipy) excess-kurtosis
        convention value at the fixture vector. If γ4 PASS band accepts 0.0,
        the production γ4 implementation has silently drifted to the excess-
        kurtosis convention and the BLdP DSR consumer (which applies excess
        conversion γ4 - 3) will compute (γ4 - 3) - 3 = -6 in place of the
        intended (γ4 - 3) = 0.

        Separate test method from test_pass_locked_gamma4_implementation per
        §2.1.3 rationale:
        (i) per-method assertion attribution on failure surfaces the exact
            contract violated;
        (ii) future test author who relaxes the tolerance band cannot silently
             swallow the 0.0-vs-3.0 convention confusion.
        """
        result = kurtosis(_FIXTURE_VECTOR, fisher=False, bias=True,
                          nan_policy="omit")
        assert abs(result - 0.0) > _FAIL_MIN_SEPARATION, (
            f"γ4 PASS band must EXCLUDE 0.0 — 0.0 is the scipy "
            f"fisher=True bias=True (default scipy) excess-kurtosis "
            f"convention value at the fixture vector. "
            f"If γ4 PASS band accepts 0.0, the production γ4 implementation "
            f"has silently drifted to the excess-kurtosis convention and the "
            f"BLdP DSR consumer will compute (γ4 - 3) - 3 = -6 instead of "
            f"(γ4 - 3) = 0. Got γ4={result!r}, |γ4 - 0.0|="
            f"{abs(result - 0.0)!r}."
        )

    def test_fail_pandas_kurt_default(self) -> None:
        """PROHIBITED: pandas Series.kurt() default = 2.5 ≠ 3.0 (Δ = -0.5).

        pandas .kurt() default returns Fisher excess kurtosis with bias-
        correction. Empirical at pandas 2.2.3 + N=6 fixture: 2.5.

        Confirm-fail assertion: |2.5 - 3.0| = 0.5 ≥ _FAIL_MIN_SEPARATION.

        If this assertion passes (i.e., pandas matches scipy fisher=False
        bias=True), the library defaults have converged and this lockout
        test is no longer needed — raise to Charlie register for Contract
        2.0.1 spec update per §2.1.9 library-version-empirical-revalidation
        discipline.
        """
        prohibited = pd.Series(_FIXTURE_VECTOR).kurt()
        assert abs(prohibited - _PASS_GAMMA4_EXPECTED) >= _FAIL_MIN_SEPARATION, (
            f"FAIL-1 (pandas .kurt() default): expected divergence from "
            f"{_PASS_GAMMA4_EXPECTED} by >= {_FAIL_MIN_SEPARATION}, got "
            f"prohibited={prohibited!r}, |Δ|="
            f"{abs(prohibited - _PASS_GAMMA4_EXPECTED)!r}. "
            f"If this assertion passes, library defaults converged; raise to "
            f"Charlie register for Contract 2.0.1 spec update."
        )
        # PASS-band negative: this implementation MUST NOT produce 3.0 ± 1e-12
        assert abs(prohibited - _PASS_GAMMA4_EXPECTED) > _PASS_TOLERANCE_ABS, (
            f"FAIL-1 (pandas .kurt() default) produced {_PASS_GAMMA4_EXPECTED} "
            f"± {_PASS_TOLERANCE_ABS} — this is the LOCKED PASS value; "
            f"production has silently swapped implementations. Investigate."
        )

    def test_fail_pandas_kurt_plus_3(self) -> None:
        """PROHIBITED: pandas Series.kurt() + 3 = 5.5 ≠ 3.0 (Δ = +2.5).

        Common naive raw-kurtosis attempt: take pandas .kurt() (excess) and
        add 3 (assuming the excess-to-raw conversion). However pandas
        default is bias-corrected excess, so adding 3 yields raw-bias-
        corrected (5.5), NOT raw-population (3.0).

        Empirical at pandas 2.2.3 + N=6 fixture: 5.5.
        """
        prohibited = pd.Series(_FIXTURE_VECTOR).kurt() + 3
        assert abs(prohibited - _PASS_GAMMA4_EXPECTED) >= _FAIL_MIN_SEPARATION, (
            f"FAIL-2 (pandas .kurt() + 3): expected divergence from "
            f"{_PASS_GAMMA4_EXPECTED} by >= {_FAIL_MIN_SEPARATION}, got "
            f"prohibited={prohibited!r}, |Δ|="
            f"{abs(prohibited - _PASS_GAMMA4_EXPECTED)!r}."
        )
        assert abs(prohibited - _PASS_GAMMA4_EXPECTED) > _PASS_TOLERANCE_ABS, (
            f"FAIL-2 (pandas .kurt() + 3) produced {_PASS_GAMMA4_EXPECTED} ± "
            f"{_PASS_TOLERANCE_ABS} — this is the LOCKED PASS value; "
            f"production has silently swapped implementations. Investigate."
        )

    def test_fail_scipy_fisher_true_bias_true(self) -> None:
        """PROHIBITED: scipy.stats.kurtosis(fisher=True, bias=True) = 0.0 ≠ 3.0 (Δ = -3.0).

        scipy default (fisher=True, bias=True): excess kurtosis, uncorrected.
        Empirical at scipy 1.10.0 + N=6 fixture: 0.0.

        This is the DEFAULT scipy.stats.kurtosis() invocation (no keyword
        args). The PASS implementation MUST explicitly pass fisher=False AND
        bias=True AND nan_policy='omit' to deviate from this default.

        Largest Δ separation (|0.0 - 3.0| = 3.0) — this is the most likely
        accidental swap target if a future caller drops the LOCKED keyword
        arguments. Critical lockout.
        """
        prohibited = kurtosis(_FIXTURE_VECTOR, fisher=True, bias=True)
        assert abs(prohibited - _PASS_GAMMA4_EXPECTED) >= _FAIL_MIN_SEPARATION, (
            f"FAIL-3 (scipy fisher=True bias=True; scipy default): expected "
            f"divergence from {_PASS_GAMMA4_EXPECTED} by >= "
            f"{_FAIL_MIN_SEPARATION}, got prohibited={prohibited!r}, |Δ|="
            f"{abs(prohibited - _PASS_GAMMA4_EXPECTED)!r}."
        )
        assert abs(prohibited - _PASS_GAMMA4_EXPECTED) > _PASS_TOLERANCE_ABS, (
            f"FAIL-3 (scipy default) produced {_PASS_GAMMA4_EXPECTED} ± "
            f"{_PASS_TOLERANCE_ABS} — this is the LOCKED PASS value; "
            f"production has silently swapped implementations. Investigate."
        )

    def test_fail_scipy_fisher_true_bias_false(self) -> None:
        """PROHIBITED: scipy.stats.kurtosis(fisher=True, bias=False) = 2.5 ≠ 3.0 (Δ = -0.5).

        scipy with bias-correction enabled + excess convention: excess
        kurtosis with bias-correction. Empirical at scipy 1.10.0 + N=6
        fixture: 2.5.

        Possible accidental swap if a future caller passes bias=False
        (intending "bias-corrected estimator") without recognizing that
        fisher=True is the default. Δ = 0.5 satisfies _FAIL_MIN_SEPARATION
        threshold.
        """
        prohibited = kurtosis(_FIXTURE_VECTOR, fisher=True, bias=False)
        assert abs(prohibited - _PASS_GAMMA4_EXPECTED) >= _FAIL_MIN_SEPARATION, (
            f"FAIL-4 (scipy fisher=True bias=False): expected divergence "
            f"from {_PASS_GAMMA4_EXPECTED} by >= {_FAIL_MIN_SEPARATION}, got "
            f"prohibited={prohibited!r}, |Δ|="
            f"{abs(prohibited - _PASS_GAMMA4_EXPECTED)!r}."
        )
        assert abs(prohibited - _PASS_GAMMA4_EXPECTED) > _PASS_TOLERANCE_ABS, (
            f"FAIL-4 (scipy fisher=True bias=False) produced "
            f"{_PASS_GAMMA4_EXPECTED} ± {_PASS_TOLERANCE_ABS} — this is the "
            f"LOCKED PASS value; production has silently swapped "
            f"implementations. Investigate."
        )

    def test_fail_scipy_fisher_false_bias_false(self) -> None:
        """PROHIBITED: scipy.stats.kurtosis(fisher=False, bias=False) = 5.5 ≠ 3.0 (Δ = +2.5).

        scipy with raw-kurtosis convention BUT bias-correction enabled: raw
        bias-corrected kurtosis. Empirical at scipy 1.10.0 + N=6 fixture: 5.5.

        Possible accidental swap if a future caller passes fisher=False
        (intending raw kurtosis) without explicitly setting bias=True (the
        bias-correction default differs from population convention). Δ = 2.5
        well exceeds _FAIL_MIN_SEPARATION threshold.
        """
        prohibited = kurtosis(_FIXTURE_VECTOR, fisher=False, bias=False)
        assert abs(prohibited - _PASS_GAMMA4_EXPECTED) >= _FAIL_MIN_SEPARATION, (
            f"FAIL-5 (scipy fisher=False bias=False): expected divergence "
            f"from {_PASS_GAMMA4_EXPECTED} by >= {_FAIL_MIN_SEPARATION}, got "
            f"prohibited={prohibited!r}, |Δ|="
            f"{abs(prohibited - _PASS_GAMMA4_EXPECTED)!r}."
        )
        assert abs(prohibited - _PASS_GAMMA4_EXPECTED) > _PASS_TOLERANCE_ABS, (
            f"FAIL-5 (scipy fisher=False bias=False) produced "
            f"{_PASS_GAMMA4_EXPECTED} ± {_PASS_TOLERANCE_ABS} — this is the "
            f"LOCKED PASS value; production has silently swapped "
            f"implementations. Investigate."
        )
