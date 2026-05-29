"""Tier 6 Deflated Sharpe Ratio evaluation application (post-R6.1-V_SEAL).

Applies the R6.1-locked BLdP-2014 closed-form DSR methodology + §12 Errata (a1)
to the B-C-narrow-recovered phase4_forward_2026_15bps_v1 cohort. See design spec
docs/superpowers/specs/2026-05-29-tier6-dsr-evaluation-application-design.md.

NOT the heuristic screen in evaluate_dsr.py (sqrt(2 ln N)); that module is
untouched. This is the production closed-form DSR per CLAUDE.md HARD CONSTRAINT
"DSR-family preferred" for the Tier 6 promotion class.
"""
from __future__ import annotations

import csv
import hashlib
import json
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


# --------------------------------------------------------------------------
# Task 5: robustness flags (g4-high / provisional / r21-indeterminate)
# --------------------------------------------------------------------------
G4_HIGH = 50.0
PROVISIONAL_DSR_MARGIN = 0.5

# R6.1 §8.1 R2.1-INDETERMINATE identifiers. CONTRACT BOUNDARY: this is a
# DIFFERENT set from R21_EXCLUDED (R5.1 §188; companion-partition cohort
# exclusions). These two hashes are heavy-overlap candidates whose R2.1
# disposition is indeterminate; they are annotated, never partition-excluded.
R21_INDETERMINATE = frozenset({"7abff29fc2f117a1", "2433a38b2f9a7211"})


def annotate_flags(res: dict) -> dict:
    """Annotate an ``evaluate_candidate`` result dict with robustness flags.

    Adds three boolean flags WITHOUT mutating the input dict:

    - ``g4_high_flag``: ``gamma4 >= G4_HIGH`` (RAW kurtosis well above the
      Gaussian 3.0; flags heavy-tailed candidates whose closed-form asymptotic
      is least trustworthy).
    - ``r21_indeterminate_flag``: ``hypothesis_hash in R21_INDETERMINATE``
      (R6.1 §8.1; DIFFERENT from ``R21_EXCLUDED``).
    - ``provisional_flag``: an authoritative (Form B) pass whose
      ``dsr_statistic_B`` margin is in ``[0, PROVISIONAL_DSR_MARGIN)`` — a
      narrow pass labelled provisional pending SD-E-γ serial-correlation
      handling. A failing row (``pass_B`` False) is never provisional.

    Args:
        res: An ``evaluate_candidate`` (and optionally pre-flagged) result dict.
            Must contain ``gamma4``, ``hypothesis_hash``, ``pass_B`` and
            ``dsr_statistic_B``.

    Returns:
        A NEW dict (shallow copy of ``res``) with the three flags added.
    """
    res = dict(res)
    res["g4_high_flag"] = bool(res["gamma4"] >= G4_HIGH)
    res["r21_indeterminate_flag"] = res["hypothesis_hash"] in R21_INDETERMINATE
    res["provisional_flag"] = bool(
        res["pass_B"] and 0 <= res["dsr_statistic_B"] < PROVISIONAL_DSR_MARGIN
    )
    return res


# --------------------------------------------------------------------------
# Task 6: Monte-Carlo expected-max validation (seeded, NON-AUTHORITATIVE)
# --------------------------------------------------------------------------
def mc_expected_max_ratio(
    n_star: int = N_STAR, n_sims: int = 100_000, seed: int = 20260529
) -> dict:
    """Monte-Carlo expected max of ``n_star`` i.i.d. standard normals.

    Bounds the Form A / Form B closed-form approximation error at the moderate
    ``N*=18`` regime by simulating ``n_sims`` draws of ``max`` of ``n_star``
    standard normals and taking the sample mean (the expected-max ratio in
    normalized ``SR*/sqrt(Var)`` units). NON-AUTHORITATIVE validation companion
    — never a capital gate; the authoritative ratio is the Form B closed form.

    The RNG is ``numpy.random.default_rng(seed)``, so the result is fully
    reproducible for a fixed ``(n_star, n_sims, seed)``.

    Args:
        n_star: Effective number of independent trials (default ``N_STAR=18``).
        n_sims: Number of Monte-Carlo simulations (default 100_000).
        seed: RNG seed for reproducibility (default 20260529).

    Returns:
        A dict with ``empirical_ratio`` (sample mean of max-of-n_star normals),
        ``form_a_ratio`` / ``form_b_ratio`` (the closed forms), the signed
        errors ``form_a_minus_empirical`` / ``form_b_minus_empirical``, plus the
        echoed ``n_star`` / ``n_sims`` / ``seed``.

    Raises:
        ValueError: If ``n_sims <= 0`` (no draws → empty-array mean is nan).
            ``evaluate_cohort`` already calls this only ``if n_sims`` (so
            ``n_sims=0`` skips MC entirely); this guard is defensive for direct
            callers.
    """
    if n_sims <= 0:
        raise ValueError(f"n_sims must be positive; got {n_sims}")
    rng = np.random.default_rng(seed)
    maxes = rng.standard_normal((n_sims, n_star)).max(axis=1)
    emp = float(maxes.mean())
    fa = expected_max_ratio_form_a(n_star)
    fb = expected_max_ratio_form_b(n_star)
    return {
        "n_star": n_star,
        "n_sims": n_sims,
        "seed": seed,
        "empirical_ratio": emp,
        "form_a_ratio": fa,
        "form_b_ratio": fb,
        "form_a_minus_empirical": fa - emp,
        "form_b_minus_empirical": fb - emp,
    }


# --------------------------------------------------------------------------
# Task 7: cohort evaluator + artifact emitters
# --------------------------------------------------------------------------
DEFAULT_OUT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1"

# A5/A9 reconciliation: these MUST match the actual keys emitted by
# evaluate_candidate + annotate_flags + the A3 degenerate-flag wrapper —
# i.e. er_B/er_A (uppercase), var_sr_null (NOT var_null), psr_B/dsr_statistic_B
# (NOT a bare ambiguous DSR_B). CSV emission uses extrasaction="ignore" so
# row-only fields (non_authoritative, monday_flag) are dropped from the
# authoritative CSV unless added as `extra` columns. MED-1: failure_reason is
# now a persisted column (empty string on normal rows, populated on degenerate
# rows) so a flagged-fail's diagnostic survives into the written CSV.
_RESULT_FIELDS = [
    "hypothesis_hash", "name", "theme", "T", "sr_per_bar",
    "gamma3", "gamma4", "trades", "var_sr_null",
    "er_B", "sr_star_B", "deflated_z_B", "psr_B", "dsr_statistic_B", "pass_B",
    "er_A", "sr_star_A", "deflated_z_A", "psr_A", "dsr_statistic_A", "pass_A",
    "g4_high_flag", "provisional_flag", "r21_indeterminate_flag",
    "mertens_degenerate_flag", "failure_reason",
]


def _read_cohort_csv() -> pd.DataFrame:
    """Read the cohort ``holdout_results.csv`` (39 rows).

    DESIGN INVARIANT: a single seam for the cohort CSV read so the next-chunk
    ``wf_lineage`` evaluation-semantics consumption guard (Task 8) can be
    inserted right after this read, and so tests can monkeypatch the read.

    Returns:
        The holdout results DataFrame.
    """
    return pd.read_csv(HOLDOUT_DIR / "holdout_results.csv")


def _degenerate_fail_row(
    hypothesis_hash: str, cm: CandidateMoments | None, exc: Exception
) -> dict:
    """Build a flagged auto-fail row for a candidate whose evaluation raised.

    A3 (mertens-degenerate auto-fail-flag): a degenerate candidate (non-positive
    Mertens variance term, or any ``ValueError`` from ``evaluate_candidate``)
    must NEVER crash the cohort run. We emit a flagged-fail row instead.

    Args:
        hypothesis_hash: The candidate identifier.
        cm: The loaded moments if available (for identifying fields), else None.
        exc: The captured exception (its ``str`` becomes ``failure_reason``).

    Returns:
        A result dict with ``pass_B = pass_A = False``,
        ``mertens_degenerate_flag = True``, ``failure_reason`` and any available
        identifying fields, plus the other flags set to safe defaults.
    """
    row: dict = {
        "hypothesis_hash": hypothesis_hash,
        "name": cm.name if cm is not None else None,
        "theme": cm.theme if cm is not None else None,
        "T": cm.T if cm is not None else None,
        "sr_per_bar": cm.sr_per_bar if cm is not None else None,
        "gamma3": cm.gamma3 if cm is not None else None,
        "gamma4": cm.gamma4 if cm is not None else None,
        "trades": cm.trades if cm is not None else None,
        "pass_B": False,
        "pass_A": False,
        "mertens_degenerate_flag": True,
        "failure_reason": str(exc),
        "g4_high_flag": False,
        "provisional_flag": False,
        "r21_indeterminate_flag": hypothesis_hash in R21_INDETERMINATE,
    }
    return row


def _evaluate_one(hypothesis_hash: str, df: pd.DataFrame, n_star: int = N_STAR) -> dict:
    """Load → evaluate → annotate one candidate, with the A3 degenerate guard.

    DESIGN INVARIANT (HIGH-1): ``load_candidate_moments`` is called OUTSIDE the
    try/except so its DATA-INTEGRITY ValueErrors (missing hash, SHA-256
    mismatch, stored-vs-recompute moment mismatch) PROPAGATE and crash
    ``evaluate_cohort`` with a clear message. These are not Mertens math
    degeneracy; absorbing them as ``mertens_degenerate_flag=True`` would
    silently mask artifact corruption at a capital-adjacent fire. ONLY
    ``evaluate_candidate``'s Mertens-degeneracy ValueError (non-positive
    variance term, etc.) is caught → ``_degenerate_fail_row`` so one degenerate
    candidate produces a flagged-fail row and the batch continues. The hard
    ``ValueError`` RAISE stays inside the pure ``mertens_variance`` unit.

    Args:
        hypothesis_hash: The candidate identifier.
        df: The cohort DataFrame.
        n_star: Effective number of independent trials.

    Returns:
        An annotated result dict; ``mertens_degenerate_flag`` is False for a
        clean candidate and True for a (Mertens-)degenerate flagged-fail one.

    Raises:
        ValueError: Propagated from ``load_candidate_moments`` on any
            data-integrity failure (NOT caught here).
    """
    # Module-level lookup (not the imported name) so monkeypatching
    # tier6_dsr.load_candidate_moments is honored by the cohort evaluator.
    # Data-integrity ValueError propagates (crash) — see DESIGN INVARIANT above.
    cm = load_candidate_moments(hypothesis_hash, df)
    try:
        row = annotate_flags(evaluate_candidate(cm, n_star=n_star))
        row["mertens_degenerate_flag"] = False
        row["failure_reason"] = ""  # MED-1: consistent column on normal rows
        return row
    except ValueError as exc:
        # ONLY Mertens math degeneracy is caught here.
        return _degenerate_fail_row(hypothesis_hash, cm, exc)


def _write_csv(path: Path, rows: list[dict], extra: tuple[str, ...] = ()) -> None:
    """Write ``rows`` to ``path`` as CSV using the reconciled ``_RESULT_FIELDS``.

    Uses ``extrasaction="ignore"`` so row-only fields not in the header
    (e.g. ``non_authoritative`` / ``monday_flag`` on the authoritative CSV,
    when not passed via ``extra``) are silently dropped. ``failure_reason`` is
    part of ``_RESULT_FIELDS`` and is always emitted (empty string on normal
    rows; ``restval=""`` covers any row missing the key).

    Args:
        path: Output CSV path.
        rows: Result dicts to write.
        extra: Additional column names appended after ``_RESULT_FIELDS``.
    """
    fields = _RESULT_FIELDS + list(extra)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", restval="")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def evaluate_cohort(
    out_dir: Path | None = DEFAULT_OUT_DIR,
    n_sims: int = 100_000,
    write: bool = True,
) -> dict:
    """Evaluate the locked-18 (authoritative) + companion-21 (quarantined) cohort.

    Reads the cohort ``holdout_results.csv``, derives the 18/21 partition, and
    for each candidate loads its moments, computes the Form B (authoritative) +
    Form A (companion) DSR statistics, and annotates robustness flags. The A3
    degenerate guard ensures a single degenerate candidate cannot abort the
    batch. Companion rows additionally carry ``non_authoritative=True`` and
    ``monday_flag``; authoritative rows carry ``non_authoritative=False``.

    Args:
        out_dir: Output directory for artifacts (default ``DEFAULT_OUT_DIR``).
            Ignored when ``write`` is False or ``out_dir`` is None.
        n_sims: Monte-Carlo simulation count; ``0`` skips MC validation
            (``mc_validation`` becomes ``{}``).
        write: When True (and ``out_dir`` is not None), write the 4 artifacts.

    Returns:
        A dict with ``authoritative`` (18 rows), ``companion`` (21 rows),
        ``promotion_list`` (authoritative rows with ``pass_B is True``),
        ``degenerate_count`` (count of authoritative+companion rows with
        ``mertens_degenerate_flag is True``), ``mc_validation``, ``n_star``,
        ``alpha``, ``authoritative_form="B"`` and ``companion_form="B"``.
    """
    # DESIGN INVARIANT: the wf_lineage evaluation-semantics consumption guard
    # (Task 8, next chunk) is inserted immediately after this read, before any
    # downstream consumption of the cohort artifacts.
    df = _read_cohort_csv()
    locked, companion = derive_cohort(df)

    authoritative: list[dict] = []
    for h in locked:
        row = _evaluate_one(h, df)
        row["non_authoritative"] = False
        authoritative.append(row)

    companion_rows: list[dict] = []
    for h in companion:
        row = _evaluate_one(h, df)
        row["non_authoritative"] = True
        # Resolve the name for monday_flag from the cohort frame (the row's
        # `name` may be None on a degenerate auto-fail).
        name = str(df.loc[df["hypothesis_hash"] == h, "name"].iloc[0])
        row["monday_flag"] = is_monday_pattern(name)
        companion_rows.append(row)

    promotion_list = [r for r in authoritative if r["pass_B"] is True]
    mc = mc_expected_max_ratio(N_STAR, n_sims=n_sims) if n_sims else {}

    # MED-2: count Mertens-degenerate flagged-fail rows across both partitions.
    degenerate_count = sum(
        1 for r in (*authoritative, *companion_rows)
        if r.get("mertens_degenerate_flag") is True
    )

    out = {
        "authoritative": authoritative,
        "companion": companion_rows,
        "promotion_list": promotion_list,
        "degenerate_count": degenerate_count,
        "mc_validation": mc,
        "n_star": N_STAR,
        "alpha": ALPHA,
        "authoritative_form": "B",
        "companion_form": "B",
    }

    if write and out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        _write_csv(out_dir / "tier6_dsr_results.csv", authoritative)
        _write_csv(
            out_dir / "tier6_dsr_companion.csv", companion_rows,
            extra=("non_authoritative", "monday_flag"),
        )
        (out_dir / "tier6_promotion_list.json").write_text(json.dumps(
            {
                "n_star": N_STAR,
                "alpha": ALPHA,
                "form": "B",
                "promoted": [r["hypothesis_hash"] for r in promotion_list],
                "count": len(promotion_list),
            },
            indent=2,
        ))
        (out_dir / "tier6_mc_validation.json").write_text(json.dumps(mc, indent=2))
    return out
