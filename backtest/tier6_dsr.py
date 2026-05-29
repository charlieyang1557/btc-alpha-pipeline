"""Tier 6 Deflated Sharpe Ratio evaluation application (post-R6.1-V_SEAL).

Applies the R6.1-locked BLdP-2014 closed-form DSR methodology + §12 Errata (a1)
to the B-C-narrow-recovered phase4_forward_2026_15bps_v1 cohort. See design spec
docs/superpowers/specs/2026-05-29-tier6-dsr-evaluation-application-design.md.

NOT the heuristic screen in evaluate_dsr.py (sqrt(2 ln N)); that module is
untouched. This is the production closed-form DSR per CLAUDE.md HARD CONSTRAINT
"DSR-family preferred" for the Tier 6 promotion class.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, norm, skew

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOLDOUT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1"

ALPHA = 0.05
N_STAR = 18
EULER_GAMMA = 0.5772156649015329
ANNUALIZATION_BARS_PER_YEAR = 8760  # hourly bars/year; cross-check only

# R5.1 §188 R2.1-EXCLUDED identifiers (pre-registered; not Monday-named).
R21_EXCLUDED = frozenset({"35dcfcfbee4cfafc", "38a1bb228f103c26"})


def is_monday_pattern(name: str) -> bool:
    """Name-substring Monday-pattern predicate (DSL content unavailable).

    Args:
        name: Candidate strategy name.

    Returns:
        True if the lowercased name contains the substring ``monday``.
    """
    return "monday" in str(name).lower()


def derive_cohort(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Partition cohort_a into (locked-18, companion-21).

    locked-18 = 39 - 19 Monday-pattern (name ~ /monday/i) - 2 R2.1-EXCLUDED.

    Args:
        df: The holdout_results.csv DataFrame (39 rows; cols include
            ``hypothesis_hash``, ``name``, ``theme``).

    Returns:
        ``(locked, companion)`` lists of ``hypothesis_hash`` strings.

    Raises:
        ValueError: If the partition is not exactly 18/21 (drift in the
            Monday predicate or R21_EXCLUDED set).
    """
    monday = df["name"].map(is_monday_pattern)
    r21 = df["hypothesis_hash"].isin(R21_EXCLUDED)
    locked = df.loc[~monday & ~r21, "hypothesis_hash"].tolist()
    companion = df.loc[monday | r21, "hypothesis_hash"].tolist()
    if len(locked) != 18 or len(companion) != 21:
        raise ValueError(
            f"cohort partition drift: locked={len(locked)} companion={len(companion)} "
            f"(expected 18/21); check Monday predicate + R21_EXCLUDED"
        )
    return locked, companion


# --------------------------------------------------------------------------
# Task 2: per-candidate moment loader + consume-and-verify
# --------------------------------------------------------------------------
MOMENT_RECOMPUTE_EPS = 1e-6


@dataclass(frozen=True)
class CandidateMoments:
    """Per-candidate moments consumed from holdout artifacts.

    ``gamma4`` is RAW kurtosis (3.0 = Gaussian), matching the engine-stored
    convention and the Mertens ``(gamma4-1)/4`` term. ``sr_per_bar`` is the
    per-bar Sharpe ``mean(r)/std(r, ddof=0)`` over the finite return series.
    ``T`` is the count of finite per-bar returns (total bars, incl. zeros).
    """

    hypothesis_hash: str
    name: str
    theme: str
    sr_per_bar: float
    gamma3: float
    gamma4: float  # RAW kurtosis (3 = Gaussian)
    T: int
    trades: int | None


def _sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file's bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_candidate_moments(hypothesis_hash: str, df: pd.DataFrame) -> CandidateMoments:
    """Load per-candidate moments with consume-and-verify integrity gates.

    Pipeline:
    1. A8 artifact-integrity gate: verify the CSV-stored
       ``returns_per_bar_sha256`` against the on-disk parquet's actual
       SHA-256 BEFORE any recompute. Raises on mismatch.
    2. Independently recompute ``T``, ``gamma3`` (population skew,
       ``bias=True``), ``gamma4`` (RAW kurtosis, ``fisher=False, bias=True``)
       and ``SR_per_bar`` (``mean/std(ddof=0)``) from the parquet ``return``
       column over its finite entries.
    3. Consume the stored ``T_obs/gamma3/gamma4`` and verify each against the
       recompute (raise on >EPS mismatch; T_obs is exact-integer).

    Args:
        hypothesis_hash: Candidate identifier (row key in ``df``).
        df: The holdout_results.csv DataFrame.

    Returns:
        A frozen :class:`CandidateMoments`.

    Raises:
        ValueError: If ``hypothesis_hash`` is absent from ``df``, on sha256
            integrity mismatch, or stored-vs-recompute moment mismatch beyond
            ``MOMENT_RECOMPUTE_EPS``.
    """
    matches = df.loc[df["hypothesis_hash"] == hypothesis_hash]
    if matches.empty:
        raise ValueError(f"hypothesis_hash {hypothesis_hash!r} not found in cohort DataFrame")
    row = matches.iloc[0]
    pq = HOLDOUT_DIR / hypothesis_hash / "returns_per_bar.parquet"

    # A8: artifact-integrity gate BEFORE recompute.
    stored_sha = str(row["returns_per_bar_sha256"])
    actual_sha = _sha256_file(pq)
    if stored_sha != actual_sha:
        raise ValueError(
            f"sha256 integrity mismatch for {hypothesis_hash}: "
            f"stored={stored_sha} on_disk={actual_sha} (path={pq})"
        )

    r = pd.read_parquet(pq)["return"]
    rf = r[np.isfinite(r)]
    T = int(len(rf))
    g3 = float(skew(rf, bias=True))
    g4 = float(kurtosis(rf, fisher=False, bias=True))  # RAW (3 = Gaussian)
    sr = float(rf.mean() / rf.std(ddof=0))

    for label, stored, recomputed in (
        ("T_obs", int(row["T_obs"]), T),
        ("gamma3", float(row["gamma3"]), g3),
        ("gamma4", float(row["gamma4"]), g4),
    ):
        tol = 0 if label == "T_obs" else MOMENT_RECOMPUTE_EPS
        if abs(stored - recomputed) > tol:
            raise ValueError(
                f"moment mismatch for {hypothesis_hash} {label}: "
                f"stored={stored} recomputed={recomputed}"
            )

    trades = row.get("holdout_total_trades")
    trades = None if pd.isna(trades) else int(trades)
    return CandidateMoments(
        hypothesis_hash, str(row["name"]), str(row["theme"]),
        sr, g3, g4, T, trades,
    )


# --------------------------------------------------------------------------
# Task 3: expected-max ratios (Form A companion / Form B authoritative)
# --------------------------------------------------------------------------
def expected_max_ratio_form_a(n_star: int) -> float:
    """Form A asymptotic expected-max ratio (COMPANION; non-authoritative).

    ``sqrt(2 * ln N*)`` — the project's interim heuristic screen
    (CLAUDE.md "interim screen only"). Retained for first-fire transparency;
    NOT the capital-adjacent gate.

    Args:
        n_star: Effective number of independent trials (must be > 1).

    Returns:
        The normalized expected-max-of-N* ratio.

    Raises:
        ValueError: If ``n_star <= 1`` (log/degenerate).
    """
    if n_star <= 1:
        raise ValueError("Form A expected-max requires N* > 1")
    return math.sqrt(2.0 * math.log(n_star))


def expected_max_ratio_form_b(n_star: int) -> float:
    """Form B Euler-Mascheroni closed-form expected-max ratio (AUTHORITATIVE).

    BLdP 2014 / SD-A-alpha lock:
    ``(1-g)*Phi^-1(1 - 1/N*) + g*Phi^-1(1 - 1/(N*e))``, g = Euler-Mascheroni.
    This is the SD-A-alpha-locked instrument and the authoritative capital gate.

    Args:
        n_star: Effective number of independent trials (must be > 1).

    Returns:
        The normalized expected-max-of-N* ratio.

    Raises:
        ValueError: If ``n_star <= 1`` (``Phi^-1(0) = -inf``).
    """
    if n_star <= 1:
        raise ValueError("Form B closed-form requires N* > 1 (Phi^-1(0) = -inf)")
    g = EULER_GAMMA
    return float(
        (1.0 - g) * norm.ppf(1.0 - 1.0 / n_star)
        + g * norm.ppf(1.0 - 1.0 / (n_star * math.e))
    )


# --------------------------------------------------------------------------
# Task 4: Mertens variance + SR* + deflated-z + DSR/PSR + pass rule
# --------------------------------------------------------------------------
Z_PASS = float(norm.ppf(1.0 - ALPHA))  # one-sided z(0.95) = 1.6449


def mertens_variance(sr: float, gamma3: float, gamma4: float, T: int) -> float:
    """Mertens 2002 asymptotic Sharpe-estimator variance ``Var(SR)``.

    ``Var(SR) = (1 - g3*SR + ((g4-1)/4)*SR^2) / (T-1)``. ``gamma4`` is RAW
    kurtosis (3 = Gaussian). At ``SR = 0`` the skew/kurtosis terms vanish and
    this reduces to the null variance ``1/(T-1)``.

    Args:
        sr: Sharpe estimate (per-bar units).
        gamma3: Population skew.
        gamma4: RAW kurtosis (3 = Gaussian).
        T: Count of finite per-bar returns.

    Returns:
        The Mertens variance (a positive float).

    Raises:
        ValueError: If ``T <= 1`` (degenerate; the ``T-1`` denominator is
            zero/negative), if ``sr`` is non-finite (a flat zero-variance
            return series yields ``sr = 0/0 = nan``, which the ``term <= 0``
            guard below does NOT catch since ``nan <= 0`` is ``False``), or if
            the numerator term is non-positive (asymptotic breakdown under
            extreme moments). This is the math contract of this pure unit; the
            cohort evaluator wraps it.
    """
    if T <= 1:
        raise ValueError(f"T must be >= 2 for Mertens variance; got T={T}")
    if not math.isfinite(sr):
        raise ValueError(f"non-finite sr={sr} passed to mertens_variance")
    term = 1.0 - gamma3 * sr + ((gamma4 - 1.0) / 4.0) * sr * sr
    if term <= 0.0:
        raise ValueError(
            f"non-positive Mertens variance term {term:.4f} "
            f"(sr={sr}, g3={gamma3}, g4={gamma4}): asymptotic breakdown"
        )
    return term / (T - 1)


def sr_star(n_star: int, T: int, form: str) -> float:
    """Expected-max Sharpe benchmark ``SR* = sqrt(1/(T-1)) * ER``.

    The null variance is ``1/(T-1)`` (Gaussian null: skew/kurtosis vanish at
    SR=0). ``ER`` is the expected-max ratio: Form B (authoritative) or Form A
    (companion).

    Args:
        n_star: Effective number of independent trials.
        T: Count of finite per-bar returns.
        form: ``"B"`` (authoritative) or ``"A"`` (companion).

    Returns:
        The expected-max Sharpe benchmark ``SR*``.

    Raises:
        ValueError: If ``T <= 1`` (the ``1/(T-1)`` null variance is
            degenerate), or if ``form`` is neither ``"B"`` nor ``"A"`` (a typo
            must NOT silently fall back to the lenient companion Form A).
    """
    if T <= 1:
        raise ValueError(f"T must be >= 2 for Mertens variance; got T={T}")
    if form == "B":
        er = expected_max_ratio_form_b(n_star)
    elif form == "A":
        er = expected_max_ratio_form_a(n_star)
    else:
        raise ValueError(f"unknown form {form!r}: expected 'B' or 'A'")
    return math.sqrt(1.0 / (T - 1)) * er


def deflated_z(sr: float, sr_star_val: float, gamma3: float, gamma4: float, T: int) -> float:
    """Deflated z-statistic ``(SR_hat - SR*) * sqrt(T-1) / sqrt(Mertens(SR_hat))``.

    DESIGN INVARIANT (A10): the denominator ``sqrt(mertens_variance(...)*(T-1))``
    equals ``sqrt(term)`` exactly, because ``mertens_variance = term/(T-1)`` so
    the ``(T-1)`` factors cancel: ``mertens*(T-1) = term``. We deliberately keep
    the ``*(T-1)`` form (rather than recomputing ``term`` inline) so the single
    source of truth for the variance term is ``mertens_variance`` — both the
    benchmark scaling and the estimator SE flow through it, and its
    non-positive guard fires once. ``test_deflated_z_denominator_equals_sqrt_term``
    pins this cancellation.

    Args:
        sr: Sharpe estimate (per-bar units).
        sr_star_val: The expected-max benchmark ``SR*`` for this candidate.
        gamma3: Population skew.
        gamma4: RAW kurtosis (3 = Gaussian).
        T: Count of finite per-bar returns.

    Returns:
        The deflated z-statistic.

    Raises:
        ValueError: Propagated from ``mertens_variance`` on a non-positive term.
    """
    denom = math.sqrt(mertens_variance(sr, gamma3, gamma4, T) * (T - 1))
    return (sr - sr_star_val) * math.sqrt(T - 1) / denom


def evaluate_candidate(cm: CandidateMoments, n_star: int = N_STAR) -> dict:
    """Compute Form B (authoritative) + Form A (companion) DSR statistics + pass.

    Pass rule (R6.1 §3.1 locked, one-sided, no Bonferroni layering):
    ``pass <=> deflated_z >= z(1-alpha)=1.6449 <=> PSR(SR*) >= 0.95
    <=> dsr_statistic >= 0`` where ``dsr_statistic = deflated_z - z(0.95)`` and
    ``PSR(SR*) = Phi(deflated_z)``.

    Args:
        cm: The candidate's moments.
        n_star: Effective number of independent trials (default ``N_STAR=18``).

    Returns:
        A dict with both forms' ``er_{B,A}``, ``sr_star_{B,A}``,
        ``deflated_z_{B,A}``, ``psr_{B,A}``, ``dsr_statistic_{B,A}``,
        ``pass_{B,A}`` plus context fields.

    Raises:
        ValueError: If ``cm.T <= 1`` (degenerate; surfaces the same guard as
            ``mertens_variance`` / ``sr_star`` rather than letting the
            ``var_sr_null = 1/(T-1)`` context field raise a bare
            ``ZeroDivisionError``), if ``cm.sr_per_bar`` is non-finite, or
            propagated from ``mertens_variance`` on a non-positive term.
    """
    if cm.T <= 1:
        raise ValueError(f"T must be >= 2 for Mertens variance; got T={cm.T}")
    out: dict = {
        "hypothesis_hash": cm.hypothesis_hash,
        "name": cm.name,
        "theme": cm.theme,
        "T": cm.T,
        "sr_per_bar": cm.sr_per_bar,
        "gamma3": cm.gamma3,
        "gamma4": cm.gamma4,
        "trades": cm.trades,
        "var_sr_null": 1.0 / (cm.T - 1),  # A9: Var(SR_null) = 1/(T-1)
        "n_star": n_star,
        "z_pass": Z_PASS,
    }
    for form in ("B", "A"):
        er = expected_max_ratio_form_b(n_star) if form == "B" else expected_max_ratio_form_a(n_star)
        ssz = sr_star(n_star, cm.T, form)
        z = deflated_z(cm.sr_per_bar, ssz, cm.gamma3, cm.gamma4, cm.T)
        out[f"er_{form}"] = er
        out[f"sr_star_{form}"] = ssz
        out[f"deflated_z_{form}"] = z
        # psr_{form} = Phi(deflated_z) = the BLdP DSR in probability form
        # (pass at >= 1-alpha); dsr_statistic_{form} = deflated_z - z(1-alpha),
        # the "DSR >= 0" recentered form per R6.1 §3.1. Naming intentionally
        # matches R6.1 §3.1 / spec §5.4 — do NOT rename.
        out[f"psr_{form}"] = float(norm.cdf(z))
        out[f"dsr_statistic_{form}"] = z - Z_PASS
        out[f"pass_{form}"] = bool(z >= Z_PASS)
    return out
