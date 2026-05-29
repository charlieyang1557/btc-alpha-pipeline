# Tier 6 DSR Evaluation Application — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compute per-candidate Bailey–López de Prado closed-form Deflated Sharpe Ratio for the R6.1-locked 18-candidate cohort, apply the locked pass rule, and emit an authoritative promotion list + quarantined companion + MC validation, per the approved design spec `docs/superpowers/specs/2026-05-29-tier6-dsr-evaluation-application-design.md`.

**Architecture:** A new pure-analytical module `backtest/tier6_dsr.py` consuming the B-C-narrow-recovered per-bar return series + stored moments at `data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1/`. No engine changes; `evaluate_dsr.py` (the heuristic screen) is untouched. TDD throughout; the computation FIRE (running on the real cohort to produce the promotion artifacts) is a separately Charlie-gated step (Task 11), not auto-run during implementation.

**Tech Stack:** Python 3.11, numpy, pandas, scipy.stats (`norm`), pytest. Reuses `backtest.wf_lineage.check_evaluation_semantics_or_raise`.

---

## Locked constants & conventions (verified 2026-05-29 against recovered data)

- `N_STAR = 18` (ρ̄=0 / (a1) lock); `ALPHA = 0.05`; `EULER_GAMMA = 0.5772156649015329`.
- Kurtosis `γ₄` is **RAW** (3 = Gaussian); skew `γ₃` is **population** (`scipy` `bias=True`). Stored engine values reproduce `scipy.stats.kurtosis(fisher=False, bias=True)` / `scipy.stats.skew(bias=True)` exactly.
- `T` = count of finite per-bar returns (= stored `T_obs`, ~2358–2503). **Total finite bars, never active/non-zero, never the sealed "≈6000".**
- `SR_per_bar = mean(r)/std(r, ddof=0)` over the finite per-bar `return` series (population std, consistent with the population moments; pop-vs-sample differ <1e-4 at T~2500). `holdout_sharpe` (CSV) ≈ `SR_per_bar · √8760` (annualization cross-check only).
- Expected-max ratios at N\*=18: **Form A `√(2·ln N*)` = 2.4043** (companion); **Form B Euler–Mascheroni = 1.8539** (authoritative). `z(0.95) = 1.6449`.
- **SR\*** (benchmark, per candidate): `SR* = √(1/(T−1)) · ER` (null variance; γ₃/γ₄ vanish at SR=0; candidate-specific only via T).
- **Deflated z**: `(SR̂ − SR*)·√(T−1) / √(1 − γ₃·SR̂ + ((γ₄−1)/4)·SR̂²)` = `(SR̂·√(T−1) − ER) / √Mertens(SR̂)`.
- **DSR statistic** = `deflated_z − z(1−α)`; **PSR(SR\*)** = `Φ(deflated_z)`. **Pass ⇔ DSR statistic ≥ 0 ⇔ PSR ≥ 1−α=0.95 ⇔ deflated_z ≥ 1.6449** (locked R6.1 §3.1; one-sided; no Bonferroni layering).

## File structure

- Create: `backtest/tier6_dsr.py` — all functions below + CLI.
- Create: `tests/test_tier6_dsr.py` — full test suite.
- Create (at FIRE, Task 11): `data/phase2c_evaluation_gate/tier6_dsr_v1/{tier6_dsr_results.csv, tier6_dsr_companion.csv, tier6_promotion_list.json, tier6_mc_validation.json}`.
- SEAL bundle (Task 12, gated): `docs/phase5/R6_1_TIER_6_EVALUATION_APPLICATION_NOTE.md`; R6.1 NOTE `§12.5` errata; `CLAUDE.md` Phase Marker + `docs/phase_marker_history.md`.

---

## Task 1: Cohort derivation (pure)

**Files:** Create `backtest/tier6_dsr.py`; Test `tests/test_tier6_dsr.py`

- [ ] **Step 1: Write the failing test**

```python
import pandas as pd
from backtest import tier6_dsr as t6

def _cohort_df():
    base = t6.HOLDOUT_DIR / "holdout_results.csv"
    return pd.read_csv(base)

def test_derive_cohort_partitions_39_into_18_and_21():
    df = _cohort_df()
    assert len(df) == 39
    locked, companion = t6.derive_cohort(df)
    assert len(locked) == 18
    assert len(companion) == 21
    assert set(locked).isdisjoint(set(companion))
    assert set(locked) | set(companion) == set(df["hypothesis_hash"])

def test_locked_cohort_theme_composition():
    df = _cohort_df()
    locked, _ = t6.derive_cohort(df)
    sub = df[df["hypothesis_hash"].isin(locked)]
    comp = sub["theme"].value_counts().to_dict()
    assert comp == {"volume_divergence": 6, "momentum": 6,
                    "calendar_effect": 3, "mean_reversion": 2, "volatility_regime": 1}

def test_r21_excluded_are_not_monday_and_in_companion():
    df = _cohort_df()
    locked, companion = t6.derive_cohort(df)
    for h in ("35dcfcfbee4cfafc", "38a1bb228f103c26"):
        assert h in companion
        assert h not in locked
```

- [ ] **Step 2: Run to verify it fails** — `python -m pytest tests/test_tier6_dsr.py -k cohort -q` → FAIL (module/attrs not defined).

- [ ] **Step 3: Implement**

```python
"""Tier 6 Deflated Sharpe Ratio evaluation application (post-R6.1-V_SEAL).

Applies the R6.1-locked BLdP-2014 closed-form DSR methodology + §12 Errata (a1)
to the B-C-narrow-recovered phase4_forward_2026_15bps_v1 cohort. See design spec
docs/superpowers/specs/2026-05-29-tier6-dsr-evaluation-application-design.md.

NOT the heuristic screen in evaluate_dsr.py (sqrt(2 ln N)); that module is
untouched. This is the production closed-form DSR per CLAUDE.md HARD CONSTRAINT
line 268 'DSR-family preferred'.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOLDOUT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1"

ALPHA = 0.05
N_STAR = 18
EULER_GAMMA = 0.5772156649015329
ANNUALIZATION_BARS_PER_YEAR = 8760  # hourly bars/year; cross-check only

# R5.1 §188 R2.1-EXCLUDED identifiers (pre-registered; not Monday-named).
R21_EXCLUDED = frozenset({"35dcfcfbee4cfafc", "38a1bb228f103c26"})


def is_monday_pattern(name: str) -> bool:
    """Name-substring Monday-pattern predicate (DSL content unavailable)."""
    return "monday" in str(name).lower()


def derive_cohort(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Partition cohort_a into (locked-18, companion-21).

    locked-18 = 39 - 19 Monday-pattern (name ~ /monday/i) - 2 R2.1-EXCLUDED.
    Returns hypothesis_hash lists. Raises if the partition is not 18/21.
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
```

- [ ] **Step 4: Run to verify it passes** — `python -m pytest tests/test_tier6_dsr.py -k cohort -q` → PASS.

- [ ] **Step 5: Commit** — `git add backtest/tier6_dsr.py tests/test_tier6_dsr.py && git commit -m "feat(tier6): cohort derivation 39->18/21 (Tier 6 DSR eval app Task 1)"`

---

## Task 2: Moment loader + consume-with-verify

**Files:** Modify `backtest/tier6_dsr.py`; Test `tests/test_tier6_dsr.py`

- [ ] **Step 1: Write the failing test**

```python
import json
import numpy as np
from scipy.stats import skew, kurtosis

def test_load_moments_matches_recompute_and_raw_kurtosis():
    df = _cohort_df()
    h = "7abff29fc2f117a1"  # ema_crossover_momentum_acceleration
    cm = t6.load_candidate_moments(h, df)
    # recompute from parquet
    r = pd.read_parquet(t6.HOLDOUT_DIR / h / "returns_per_bar.parquet")["return"]
    rf = r[np.isfinite(r)]
    assert cm.T == len(rf)
    assert abs(cm.gamma3 - float(skew(rf, bias=True))) < t6.MOMENT_RECOMPUTE_EPS
    # RAW kurtosis (3=normal), NOT excess
    assert abs(cm.gamma4 - float(kurtosis(rf, fisher=False, bias=True))) < t6.MOMENT_RECOMPUTE_EPS
    assert abs(cm.gamma4 - float(kurtosis(rf, fisher=True, bias=True))) > 1.0  # != excess
    assert abs(cm.sr_per_bar - rf.mean() / rf.std(ddof=0)) < 1e-12

def test_load_moments_raises_on_stored_recompute_mismatch(monkeypatch, tmp_path):
    # if stored gamma deviates from recompute beyond EPS, raise (forensic guard)
    df = _cohort_df()
    h = "7abff29fc2f117a1"
    bad = df.copy()
    bad.loc[bad.hypothesis_hash == h, "gamma4"] = 999.0
    import pytest
    with pytest.raises(ValueError, match="moment mismatch"):
        t6.load_candidate_moments(h, bad)
```

- [ ] **Step 2: Run to verify it fails** — `python -m pytest tests/test_tier6_dsr.py -k moments -q` → FAIL.

- [ ] **Step 3: Implement** (append to `backtest/tier6_dsr.py`)

```python
MOMENT_RECOMPUTE_EPS = 1e-6


@dataclass(frozen=True)
class CandidateMoments:
    hypothesis_hash: str
    name: str
    theme: str
    sr_per_bar: float
    gamma3: float
    gamma4: float  # RAW kurtosis (3 = Gaussian)
    T: int
    trades: int | None


def load_candidate_moments(hypothesis_hash: str, df: pd.DataFrame) -> CandidateMoments:
    """Load per-candidate moments; consume stored gamma3/gamma4/T_obs and
    verify them against an independent recompute from returns_per_bar.parquet
    (raises on >EPS mismatch). SR_per_bar is computed from the parquet."""
    from scipy.stats import skew, kurtosis

    row = df.loc[df["hypothesis_hash"] == hypothesis_hash].iloc[0]
    pq = HOLDOUT_DIR / hypothesis_hash / "returns_per_bar.parquet"
    r = pd.read_parquet(pq)["return"]
    rf = r[np.isfinite(r)]
    T = int(len(rf))
    g3 = float(skew(rf, bias=True))
    g4 = float(kurtosis(rf, fisher=False, bias=True))  # RAW
    sr = float(rf.mean() / rf.std(ddof=0))

    for label, stored, recomputed in (
        ("T_obs", int(row["T_obs"]), T),
        ("gamma3", float(row["gamma3"]), g3),
        ("gamma4", float(row["gamma4"]), g4),
    ):
        if abs(stored - recomputed) > (0 if label == "T_obs" else MOMENT_RECOMPUTE_EPS):
            raise ValueError(
                f"moment mismatch for {hypothesis_hash} {label}: "
                f"stored={stored} recomputed={recomputed}"
            )
    trades = row.get("holdout_total_trades")
    trades = None if pd.isna(trades) else int(trades)
    return CandidateMoments(hypothesis_hash, str(row["name"]), str(row["theme"]),
                            sr, g3, g4, T, trades)
```

- [ ] **Step 4: Run to verify it passes** — `python -m pytest tests/test_tier6_dsr.py -k moments -q` → PASS.

- [ ] **Step 5: Commit** — `git commit -am "feat(tier6): moment loader with consume-and-verify + raw-kurtosis convention (Task 2)"`

---

## Task 3: Expected-max ratios (Form A + Form B) + monotonicity + degenerate guard

**Files:** Modify `backtest/tier6_dsr.py`; Test `tests/test_tier6_dsr.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest

def test_expected_max_ratios_at_18():
    assert abs(t6.expected_max_ratio_form_a(18) - 2.4043) < 1e-3
    assert abs(t6.expected_max_ratio_form_b(18) - 1.8539) < 1e-3

def test_expected_max_ratios_monotonic_increasing():
    for f in (t6.expected_max_ratio_form_a, t6.expected_max_ratio_form_b):
        vals = [f(n) for n in (2, 5, 10, 18, 30)]
        assert all(b > a for a, b in zip(vals, vals[1:]))

def test_form_b_degenerate_guard():
    with pytest.raises(ValueError):
        t6.expected_max_ratio_form_b(1)
    with pytest.raises(ValueError):
        t6.expected_max_ratio_form_a(1)
```

- [ ] **Step 2: Run to verify it fails** — `python -m pytest tests/test_tier6_dsr.py -k expected_max -q` → FAIL.

- [ ] **Step 3: Implement**

```python
def expected_max_ratio_form_a(n_star: int) -> float:
    """Form A asymptotic (interim heuristic; CLAUDE.md 268): sqrt(2 ln N*).
    COMPANION ONLY — non-authoritative."""
    if n_star <= 1:
        raise ValueError("Form A expected-max requires N* > 1")
    return math.sqrt(2.0 * math.log(n_star))


def expected_max_ratio_form_b(n_star: int) -> float:
    """Form B Euler-Mascheroni closed-form (BLdP 2014; SD-A-alpha lock):
    (1-g)*Phi^-1(1-1/N*) + g*Phi^-1(1-1/(N* e)). AUTHORITATIVE."""
    if n_star <= 1:
        raise ValueError("Form B closed-form requires N* > 1 (Phi^-1(0) = -inf)")
    g = EULER_GAMMA
    return float((1 - g) * norm.ppf(1 - 1.0 / n_star)
                 + g * norm.ppf(1 - 1.0 / (n_star * math.e)))
```

- [ ] **Step 4: Run to verify it passes** — `python -m pytest tests/test_tier6_dsr.py -k expected_max -q` → PASS.

- [ ] **Step 5: Commit** — `git commit -am "feat(tier6): Form A/B expected-max ratios + monotonicity + degenerate guard (Task 3)"`

---

## Task 4: Mertens variance + SR\* + deflated-z + DSR/PSR + pass rule

**Files:** Modify `backtest/tier6_dsr.py`; Test `tests/test_tier6_dsr.py`

- [ ] **Step 1: Write the failing test**

```python
def test_mertens_variance_reduces_to_null_at_sr_zero():
    # at SR=0 the skew/kurt terms vanish -> 1/(T-1)
    assert abs(t6.mertens_variance(0.0, 5.0, 80.0, 2491) - 1.0 / 2490) < 1e-15

# ⚠️ SUPERSEDED by PFR amendment A4 — first assertion is buggy (term=0.75 > 0 does NOT raise).
# Use the corrected test_mertens_variance_guard from the PFR Adjudication section:
def test_mertens_variance_non_negative_guard():
    with pytest.raises(ValueError):
        t6.mertens_variance(1.0, 0.0, 0.0, 100)  # BUG: term = 0.75 > 0, no raise
    # construct a denominator <= 0 -> raise
    with pytest.raises(ValueError):
        t6.mertens_variance(2.0, 5.0, 1.0, 100)  # 1 - 10 + 0 = -9 < 0

def test_sr_star_null_scaling():
    er = t6.expected_max_ratio_form_b(18)
    assert abs(t6.sr_star(18, 2491, "B") - math.sqrt(1.0 / 2490) * er) < 1e-12

def test_dsr_statistic_pass_rule_equivalence():
    # construct a candidate whose deflated_z is just above/below z(0.95)
    # pass <=> dsr_statistic >= 0 <=> psr >= 0.95
    res_pass = t6.evaluate_candidate(_synthetic_cm(sr=0.05, g3=0.0, g4=3.0, T=2491), n_star=18)
    res_fail = t6.evaluate_candidate(_synthetic_cm(sr=0.02, g3=0.0, g4=3.0, T=2491), n_star=18)
    for res in (res_pass, res_fail):
        assert (res["dsr_statistic_B"] >= 0) == (res["psr_B"] >= 0.95)
        assert (res["dsr_statistic_B"] >= 0) == res["pass_B"]
    assert res_pass["pass_B"] is True
    assert res_fail["pass_B"] is False

def _synthetic_cm(sr, g3, g4, T):
    return t6.CandidateMoments("synthetic", "synthetic", "test", sr, g3, g4, T, None)
```

> ⚠️ **SUPERSEDED by PFR amendment A1** — the `sr=0.05` pass case is WRONG (deflated_z=0.64 < 1.6449 → `pass_B` False; that arithmetic used the *weak* rule). Use the corrected `test_dsr_statistic_pass_rule_strong_not_weak` (sr_pass=0.08 / sr_fail=0.045) from the PFR Adjudication section.

- [ ] **Step 2: Run to verify it fails** — `python -m pytest tests/test_tier6_dsr.py -k "mertens or sr_star or pass_rule" -q` → FAIL.

- [ ] **Step 3: Implement**

```python
def mertens_variance(sr: float, gamma3: float, gamma4: float, T: int) -> float:
    """Mertens 2002 asymptotic Sharpe-estimator variance numerator term / (T-1).
    Var(SR) = (1 - g3*SR + ((g4-1)/4)*SR^2)/(T-1). gamma4 RAW. Raises if the
    variance term is non-positive (degenerate / asymptotic breakdown)."""
    term = 1.0 - gamma3 * sr + ((gamma4 - 1.0) / 4.0) * sr * sr
    if term <= 0.0:
        raise ValueError(f"non-positive Mertens variance term {term:.4f} "
                         f"(sr={sr}, g3={gamma3}, g4={gamma4}): asymptotic breakdown")
    return term / (T - 1)


def sr_star(n_star: int, T: int, form: str) -> float:
    """Expected-max Sharpe benchmark = sqrt(null var 1/(T-1)) * expected-max ratio."""
    er = expected_max_ratio_form_b(n_star) if form == "B" else expected_max_ratio_form_a(n_star)
    return math.sqrt(1.0 / (T - 1)) * er


def deflated_z(sr: float, sr_star_val: float, gamma3: float, gamma4: float, T: int) -> float:
    """(SR_hat - SR*) * sqrt(T-1) / sqrt(Mertens(SR_hat))."""
    denom = math.sqrt(mertens_variance(sr, gamma3, gamma4, T) * (T - 1))
    return (sr - sr_star_val) * math.sqrt(T - 1) / denom


Z_PASS = float(norm.ppf(1 - ALPHA))  # 1.6449


def evaluate_candidate(cm: "CandidateMoments", n_star: int = N_STAR) -> dict:
    """Compute Form B (authoritative) + Form A (companion) DSR statistics + pass."""
    out = {"hypothesis_hash": cm.hypothesis_hash, "name": cm.name, "theme": cm.theme,
           "T": cm.T, "sr_per_bar": cm.sr_per_bar, "gamma3": cm.gamma3,
           "gamma4": cm.gamma4, "trades": cm.trades,
           "var_null": 1.0 / (cm.T - 1)}
    for form in ("B", "A"):
        ssz = sr_star(n_star, cm.T, form)
        z = deflated_z(cm.sr_per_bar, ssz, cm.gamma3, cm.gamma4, cm.T)
        out[f"sr_star_{form}"] = ssz
        out[f"deflated_z_{form}"] = z
        out[f"psr_{form}"] = float(norm.cdf(z))
        out[f"dsr_statistic_{form}"] = z - Z_PASS
        out[f"pass_{form}"] = bool(z >= Z_PASS)
    return out
```

- [ ] **Step 4: Run to verify it passes** (calibrate synthetic boundary values if needed) — `python -m pytest tests/test_tier6_dsr.py -k "mertens or sr_star or pass_rule" -q` → PASS.

- [ ] **Step 5: Commit** — `git commit -am "feat(tier6): Mertens var + SR* + deflated-z + DSR/PSR pass rule (Task 4)"`

---

## Task 5: Robustness flags (g4-high, provisional margin)

**Files:** Modify `backtest/tier6_dsr.py`; Test `tests/test_tier6_dsr.py`

> Threshold values below are the plan defaults; they are re-confirmed at the B2 plan reviewer round (design spec §10.5). `G4_HIGH = 50.0` (raw kurtosis; well above Gaussian 3, flags the heavy-tailed candidates whose closed-form asymptotic is least trustworthy). `PROVISIONAL_DSR_MARGIN = 0.5` (a pass with `dsr_statistic_B` below this small z-margin is labelled provisional pending SD-E-γ serial-correlation handling).

- [ ] **Step 1: Write the failing test**

```python
def test_robustness_flags():
    hi = t6.evaluate_candidate(_synthetic_cm(sr=0.06, g3=5.0, g4=200.0, T=2491))
    hi = t6.annotate_flags(hi)
    assert hi["g4_high_flag"] is True
    lo = t6.evaluate_candidate(_synthetic_cm(sr=0.05, g3=0.0, g4=3.0, T=2491))
    lo = t6.annotate_flags(lo)
    assert lo["g4_high_flag"] is False
    # provisional: a pass with small dsr_statistic margin
    assert "provisional_flag" in lo

def test_r21_indeterminate_flag():
    res = t6.annotate_flags(t6.evaluate_candidate(
        _synthetic_cm(sr=0.05, g3=0.0, g4=3.0, T=2491)._replace_hash("38a1bb228f103c26")))
    assert res["r21_indeterminate_flag"] is True
```

(Use a small helper `_replace_hash` or construct `CandidateMoments` directly with the R2.1 hash — adjust in Step 3 to match the dataclass; `CandidateMoments` is frozen so build a new instance.)

- [ ] **Step 2: Run to verify it fails** — `python -m pytest tests/test_tier6_dsr.py -k "robustness or indeterminate" -q` → FAIL.

- [ ] **Step 3: Implement**

```python
G4_HIGH = 50.0
PROVISIONAL_DSR_MARGIN = 0.5
R21_INDETERMINATE = frozenset({"7abff29fc2f117a1", "2433a38b2f9a7211"})  # R6.1 §8.1


def annotate_flags(res: dict) -> dict:
    res = dict(res)
    res["g4_high_flag"] = bool(res["gamma4"] >= G4_HIGH)
    res["r21_indeterminate_flag"] = res["hypothesis_hash"] in R21_INDETERMINATE
    # provisional: an authoritative (Form B) pass with a small DSR-statistic margin
    res["provisional_flag"] = bool(
        res["pass_B"] and 0 <= res["dsr_statistic_B"] < PROVISIONAL_DSR_MARGIN
    )
    return res
```

- [ ] **Step 4: Run to verify it passes** — `python -m pytest tests/test_tier6_dsr.py -k "robustness or indeterminate" -q` → PASS.

- [ ] **Step 5: Commit** — `git commit -am "feat(tier6): robustness flags g4-high/provisional/r21-indeterminate (Task 5)"`

---

## Task 6: MC expected-max validation (seeded, non-authoritative)

**Files:** Modify `backtest/tier6_dsr.py`; Test `tests/test_tier6_dsr.py`

- [ ] **Step 1: Write the failing test**

```python
def test_mc_expected_max_brackets_form_a_and_b():
    out = t6.mc_expected_max_ratio(n_star=18, n_sims=20000, seed=12345)
    # the empirical expected-max-of-18 standard normals is ~1.82-2.0; both
    # closed forms should be in a sane neighborhood, Form B closer for Gaussian
    assert 1.5 < out["empirical_ratio"] < 2.3
    assert out["form_a_ratio"] == pytest.approx(2.4043, abs=1e-3)
    assert out["form_b_ratio"] == pytest.approx(1.8539, abs=1e-3)
    assert "form_a_minus_empirical" in out and "form_b_minus_empirical" in out

def test_mc_is_seed_deterministic():
    a = t6.mc_expected_max_ratio(18, n_sims=5000, seed=7)
    b = t6.mc_expected_max_ratio(18, n_sims=5000, seed=7)
    assert a["empirical_ratio"] == b["empirical_ratio"]
```

- [ ] **Step 2: Run to verify it fails** — `python -m pytest tests/test_tier6_dsr.py -k mc -q` → FAIL.

- [ ] **Step 3: Implement**

```python
def mc_expected_max_ratio(n_star: int = N_STAR, n_sims: int = 100_000,
                          seed: int = 20260529) -> dict:
    """Monte-Carlo expected max of N* i.i.d. standard normals (normalized
    SR*/sqrt(Var) units); bounds Form A/B closed-form approximation error at
    the moderate N*=18 regime. NON-AUTHORITATIVE validation companion."""
    rng = np.random.default_rng(seed)
    maxes = rng.standard_normal((n_sims, n_star)).max(axis=1)
    emp = float(maxes.mean())
    fa = expected_max_ratio_form_a(n_star)
    fb = expected_max_ratio_form_b(n_star)
    return {"n_star": n_star, "n_sims": n_sims, "seed": seed,
            "empirical_ratio": emp, "form_a_ratio": fa, "form_b_ratio": fb,
            "form_a_minus_empirical": fa - emp, "form_b_minus_empirical": fb - emp}
```

- [ ] **Step 4: Run to verify it passes** — `python -m pytest tests/test_tier6_dsr.py -k mc -q` → PASS.

- [ ] **Step 5: Commit** — `git commit -am "feat(tier6): seeded MC expected-max validation companion (Task 6)"`

---

## Task 7: Cohort evaluator + artifact emitters

**Files:** Modify `backtest/tier6_dsr.py`; Test `tests/test_tier6_dsr.py`

- [ ] **Step 1: Write the failing test**

```python
def test_evaluate_cohort_structure(tmp_path):
    out = t6.evaluate_cohort(out_dir=tmp_path, n_sims=2000)
    assert len(out["authoritative"]) == 18
    assert len(out["companion"]) == 21
    # promotion list is a subset of the authoritative-18 that pass Form B
    promoted = {r["hypothesis_hash"] for r in out["promotion_list"]}
    auth_pass = {r["hypothesis_hash"] for r in out["authoritative"] if r["pass_B"]}
    assert promoted == auth_pass
    # companion rows carry the same fields but are flagged non-authoritative
    assert all(r["non_authoritative"] is True for r in out["companion"])
    # artifacts written
    for fn in ("tier6_dsr_results.csv", "tier6_dsr_companion.csv",
               "tier6_promotion_list.json", "tier6_mc_validation.json"):
        assert (tmp_path / fn).exists()

def test_companion_never_in_authoritative():
    out = t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    auth = {r["hypothesis_hash"] for r in out["authoritative"]}
    comp = {r["hypothesis_hash"] for r in out["companion"]}
    assert auth.isdisjoint(comp)
    assert len(auth) == 18 and len(comp) == 21
```

- [ ] **Step 2: Run to verify it fails** — `python -m pytest tests/test_tier6_dsr.py -k "evaluate_cohort or companion_never" -q` → FAIL.

- [ ] **Step 3: Implement**

```python
import csv
import json

DEFAULT_OUT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1"
_RESULT_FIELDS = ["hypothesis_hash", "name", "theme", "T", "sr_per_bar",
                  "gamma3", "gamma4", "trades", "var_null",
                  "sr_star_B", "deflated_z_B", "psr_B", "dsr_statistic_B", "pass_B",
                  "sr_star_A", "deflated_z_A", "psr_A", "dsr_statistic_A", "pass_A",
                  "g4_high_flag", "provisional_flag", "r21_indeterminate_flag"]


def _write_csv(path: Path, rows: list[dict], extra: list[str] = ()) -> None:
    fields = _RESULT_FIELDS + list(extra)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def evaluate_cohort(out_dir: Path | None = DEFAULT_OUT_DIR, n_sims: int = 100_000,
                    write: bool = True) -> dict:
    """Evaluate the locked-18 (authoritative) + companion-21 (quarantined)."""
    df = pd.read_csv(HOLDOUT_DIR / "holdout_results.csv")
    locked, companion = derive_cohort(df)

    authoritative = [annotate_flags(evaluate_candidate(load_candidate_moments(h, df)))
                     for h in locked]
    companion_rows = []
    for h in companion:
        row = annotate_flags(evaluate_candidate(load_candidate_moments(h, df)))
        row["non_authoritative"] = True
        row["monday_flag"] = is_monday_pattern(row["name"])
        companion_rows.append(row)

    promotion_list = [r for r in authoritative if r["pass_B"]]
    mc = mc_expected_max_ratio(N_STAR, n_sims=n_sims) if n_sims else {}

    out = {"authoritative": authoritative, "companion": companion_rows,
           "promotion_list": promotion_list, "mc_validation": mc,
           "n_star": N_STAR, "alpha": ALPHA,
           "authoritative_form": "B", "companion_form": "B"}

    if write and out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        _write_csv(out_dir / "tier6_dsr_results.csv", authoritative)
        _write_csv(out_dir / "tier6_dsr_companion.csv", companion_rows,
                   extra=["non_authoritative", "monday_flag"])
        (out_dir / "tier6_promotion_list.json").write_text(json.dumps(
            {"n_star": N_STAR, "alpha": ALPHA, "form": "B",
             "promoted": [r["hypothesis_hash"] for r in promotion_list],
             "count": len(promotion_list)}, indent=2))
        (out_dir / "tier6_mc_validation.json").write_text(json.dumps(mc, indent=2))
    return out
```

- [ ] **Step 4: Run to verify it passes** — `python -m pytest tests/test_tier6_dsr.py -k "evaluate_cohort or companion_never" -q` → PASS.

- [ ] **Step 5: Commit** — `git commit -am "feat(tier6): cohort evaluator + artifact emitters (Task 7)"`

---

## Task 8: CLI + evaluation-semantics consumption guard

**Files:** Modify `backtest/tier6_dsr.py`; Test `tests/test_tier6_dsr.py`

- [ ] **Step 1: Write the failing test**

```python
def test_lineage_guard_invoked(monkeypatch):
    called = {}
    def fake_guard(*a, **k): called["hit"] = True
    monkeypatch.setattr(t6, "check_evaluation_semantics_or_raise", fake_guard)
    t6.evaluate_cohort(out_dir=None, n_sims=0, write=False)
    assert called.get("hit") is True

def test_cli_dry_run_writes_nothing(tmp_path, capsys):
    rc = t6.main(["--dry-run", "--out-dir", str(tmp_path)])
    assert rc == 0
    assert not any(tmp_path.iterdir())
```

- [ ] **Step 2: Run to verify it fails** — `python -m pytest tests/test_tier6_dsr.py -k "lineage or cli" -q` → FAIL.

- [ ] **Step 3: Implement** (add guard call into `evaluate_cohort` after reading df; add `main`)

```python
from backtest.wf_lineage import check_evaluation_semantics_or_raise

# ⚠️ SUPERSEDED by PFR amendment A2 — the guard takes a summary DICT, not a Path.
# Load holdout_summary.json and call check_evaluation_semantics_or_raise(summary_dict,
# artifact_path=str(path)) BEFORE consuming CSV/parquet. See PFR Adjudication A2.

import argparse
import logging
import sys

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Tier 6 closed-form DSR evaluation application")
    p.add_argument("--cohort", default="phase4_forward_2026_15bps_v1")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--n-sims", type=int, default=100_000)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)sZ %(levelname)s %(message)s")
    out = evaluate_cohort(out_dir=None if args.dry_run else Path(args.out_dir),
                          n_sims=args.n_sims, write=not args.dry_run)
    logger.info("Tier6 DSR: %d/18 authoritative passers (Form B); %d companion rows",
                len(out["promotion_list"]), len(out["companion"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

> Note: the guard's exact signature must match `backtest.wf_lineage.check_evaluation_semantics_or_raise`; inspect it at Step 3 and pass the artifact path/attestation-domain it expects (`single_run_holdout_v1` per CLAUDE.md). Adjust the call + test accordingly.

- [ ] **Step 4: Run to verify it passes** — `python -m pytest tests/test_tier6_dsr.py -k "lineage or cli" -q` → PASS.

- [ ] **Step 5: Commit** — `git commit -am "feat(tier6): CLI + evaluation-semantics consumption guard (Task 8)"`

---

## Task 9: Full-suite zero-regression gate

- [ ] **Step 1: Run the full suite** — `python -m pytest -q`
  Expected: prior baseline (2372 passed, 2 xfailed) + the new `tests/test_tier6_dsr.py` items, 0 failed.
- [ ] **Step 2: If any pre-existing test regressed, STOP** and triage (per CLAUDE.md "NEVER commit code that doesn't pass existing tests"). The new module is additive (no imports into existing modules), so regressions are not expected.
- [ ] **Step 3: Commit** (if any lint/import fixups) — `git commit -am "test(tier6): full-suite zero-regression gate green (Task 9)"`

---

## Task 10: B2 PFR on plan + implementation (reviewer gate — BEFORE fire)

- [ ] Dispatch B2 dual-leg review (Codex `codex:codex-rescue` + `quant-research-advisor`) on the implemented module + tests + this plan, focused on: (a) the §5.3 pass-rule interpretation (`PSR ≥ 0.95` vs `SR̂ ≥ SR*`), (b) the SR\* null-variance construction, (c) the Mertens non-positive-variance guard behavior under extreme γ₄, (d) the total-bars T convention, (e) any look-ahead / consumption-guard gap.
- [ ] Adjudicate findings per reviewer-suggestion-adjudication discipline (grep-verify citations; PUSHBACK on hallucinations); apply ADOPT patches via additional TDD cycles.
- [ ] **Charlie ratify** the reviewed implementation before the fire.

---

## Task 11: FIRE — run the evaluation on the real cohort (Charlie-gated)

> Operational fire; requires explicit Charlie register (authorization-routing hard rule). Does NOT run automatically during implementation.

- [ ] **Step 1:** `python -m backtest.tier6_dsr --cohort phase4_forward_2026_15bps_v1`
- [ ] **Step 2:** Inspect the 4 artifacts; record the authoritative Form B promotion count + the Form A companion count + MC bounds + flagged candidates.
- [ ] **Step 3: Commit the artifacts** — `git add data/phase2c_evaluation_gate/tier6_dsr_v1 && git commit -m "data(tier6): Tier 6 DSR evaluation application results"`
- [ ] **Step 4:** Fire PushNotification + Discord ping (per ping convention) with the headline result.

---

## Task 12: SEAL bundle (Charlie-gated; after Rule-2 SEAL-eve)

> Requires Rule-2 SEAL-eve adversarial round + Charlie register.

- [ ] Draft `docs/phase5/R6_1_TIER_6_EVALUATION_APPLICATION_NOTE.md` — results + D1/D2 locks + N1–N6 dispositions + the **N5 selection-inflation residual-risk disclosure** + the day-of-week-calendar + R2.1-INDETERMINATE disclosure flags.
- [ ] Append R6.1 NOTE **§12.5 errata** (T_obs ≈6000→~2500 + 2025-holdout→forward_2026 prose correction; application-input correction, lock unchanged).
- [ ] Rule-2 SEAL-eve adversarial round (Codex + advisor); adjudicate.
- [ ] Atomic SEAL bundle (Option 1A): NOTE + R6.1 §12.5 errata + CLAUDE.md Phase Marker advance + `docs/phase_marker_history.md` + (fold in the design spec + this plan). Pre-push secret grep gate.
- [ ] Arc tag candidate at SEAL.

---

## Self-review (writing-plans checklist)

- **Spec coverage:** §1 scope → Tasks 1–8/11; D1 (Form B auth + Form A companion) → Tasks 3,4,7; D2 (18 + 21 quarantine) → Tasks 1,7; N1 real T_obs → Tasks 2, 12 errata; N2 total-bars → Task 2; N3 variance objects → Task 4; N4 flags → Task 5; N5 disclosure → Task 12; N6 MC → Task 6; pass-rule pin → Task 4; cohort flags → Tasks 5,12. All covered.
- **Placeholder scan:** threshold values (G4_HIGH, PROVISIONAL_DSR_MARGIN) are concrete defaults flagged for reviewer reconfirmation (design §10.5), not blanks. The guard-signature + synthetic-boundary notes are explicit "inspect-and-match" instructions with the expected values stated. No "TBD"/"handle edge cases" placeholders.
- **Type consistency:** `CandidateMoments` fields, `evaluate_candidate` output keys (`pass_B`, `dsr_statistic_B`, `psr_B`, `sr_star_B`, etc.), `derive_cohort` return shape, and `_RESULT_FIELDS` are consistent across Tasks 1–8.

---

## PFR Adjudication (B2 dual-leg, 2026-05-29) — BINDING amendments

> Workflow `w1w0w3rph`: advisor APPROVE-WITH-FINDINGS + Codex NO-GO-until-patches. **Pass rule (`PSR ≥ 0.95`) independently CONFIRMED correct by BOTH legs** (R6.1 §3.1 line 115; the weak `SR̂ ≥ SR*` rule is the old heuristic-screen at `evaluate_dsr.py:296`, NOT production). All citations Layer-3-verified by orchestrator. None re-litigate the Charlie-locked D1/D2/N1–N6. The amendments below **supersede** the affected steps and are binding on the executor.

**A1 (advisor HIGH-1 — supersedes Task 4 `test_dsr_statistic_pass_rule_equivalence`):** the original `sr=0.05` pass case is WRONG (deflated_z=0.64 < 1.6449 → `pass_B` False; my line-322 arithmetic silently used the weak rule). Corrected test:

```python
def test_dsr_statistic_pass_rule_strong_not_weak():
    # sr_pass: clean STRONG pass (deflated_z ~ 2.13 >= 1.6449)
    rp = t6.evaluate_candidate(_synthetic_cm(sr=0.08, g3=0.0, g4=3.0, T=2491))
    assert rp["pass_B"] is True
    assert (rp["dsr_statistic_B"] >= 0) == (rp["psr_B"] >= 0.95) == rp["pass_B"]
    # sr_fail: SR_hat > SR* (weak rule WOULD pass) but deflated_z ~ 0.39 < 1.6449 (strong FAILS)
    rf = t6.evaluate_candidate(_synthetic_cm(sr=0.045, g3=0.0, g4=3.0, T=2491))
    assert rf["sr_per_bar"] > rf["sr_star_B"]      # weak rule would pass
    assert rf["pass_B"] is False                    # strong rule fails -> pins strong != weak
    assert rf["psr_B"] < 0.95
```
(Executor: re-derive the deflated_z at GREEN to confirm 0.08→pass / 0.045→fail at the locked formula; adjust the synthetic SR only if the boundary shifts, never the assertion logic.)

**A2 (advisor HIGH-2 + Codex BLOCKING — supersedes Task 8 guard call + test):** `check_evaluation_semantics_or_raise(summary: dict, *, artifact_path=...)` takes a **dict**, not a Path. Corrected: load the summaries and call the guard **before** consuming CSV/parquet.

```python
import json
def _load_summary(path):  # path -> dict
    return json.loads(Path(path).read_text())

# in evaluate_cohort, BEFORE pd.read_csv(...):
top = HOLDOUT_DIR / "holdout_summary.json"
check_evaluation_semantics_or_raise(_load_summary(top), artifact_path=str(top))
# and per-candidate as each is consumed (Task 2 load path):
#   sp = HOLDOUT_DIR / hypothesis_hash / "holdout_summary.json"
#   check_evaluation_semantics_or_raise(_load_summary(sp), artifact_path=str(sp))
```
Tests: replace the monkeypatched `test_lineage_guard_invoked` with a **real (non-monkeypatched)** call against the recovered top-level summary (asserts it passes — tags `evaluation_semantics="single_run_holdout_v1"`, `lineage_check="passed"` are present) + a test asserting the guard is called before any parquet read (call-order/arg-shape).

**A3 (advisor MEDIUM + Codex HIGH — amends Tasks 4 + 7):** keep the hard `ValueError` RAISE inside the pure `mertens_variance()` unit (math contract), but the **cohort evaluator must NOT crash the batch**. In `evaluate_candidate`, wrap the per-form computation: on `ValueError` from a non-positive Mertens term, set `pass_B=pass_A=False`, emit `mertens_degenerate_flag=True`, record `failure_reason`, and continue. Add a test that a degenerate candidate yields a flagged non-pass (not an exception). (Verified the guard never fires on this cohort — term ∈ [0.699, 1.114] — so this is robustness for future cohorts.)

**A4 (Codex HIGH — supersedes Task 4 `test_mertens_variance_non_negative_guard`):** the original first assertion is buggy (`mertens_variance(1.0,0.0,0.0,100)` → term=0.75 > 0, does NOT raise). Corrected:

```python
def test_mertens_variance_guard():
    assert t6.mertens_variance(1.0, 0.0, 0.0, 100) > 0      # term=0.75, positive, no raise
    with pytest.raises(ValueError):
        t6.mertens_variance(2.0, 5.0, 1.0, 100)             # term = 1-10+0 = -9 < 0 -> raise
```

**A5 (Codex MEDIUM — amends Tasks 4/7 + reconciles spec §5.4):** add `er_b` and `er_a` (the expected-max ratios) to `evaluate_candidate` output + `_RESULT_FIELDS`. Report the headline DSR explicitly as `psr_B` (the probability ∈[0,1]) **and** `dsr_statistic_B` (= deflated_z − z(0.95), the "DSR ≥ 0" form); do NOT emit a bare `DSR_B` column whose scale is ambiguous. Update spec §5.4 field list to match (`er_b, er_a, psr_B, dsr_statistic_B, …`).

**A6 (Codex MEDIUM — amends Task 8 CLI):** `--cohort` must be honored: derive `HOLDOUT_DIR` from the argument (`PROJECT_ROOT/"data/phase2c_evaluation_gate"/args.cohort`) instead of the module constant, and add a test that a non-default `--cohort` resolves a different dir (or is rejected if unknown).

**A7 (Codex LOW):** UTC logging — use a formatter with `logging.Formatter(..., )` + `converter = time.gmtime` (or emit `datetime.now(timezone.utc).isoformat()`), not local `%(asctime)s` with a literal `Z`.

**A8 (Codex LOW):** verify `returns_per_bar_sha256` (from the CSV) against the on-disk parquet `sha256` in `load_candidate_moments` **before** recompute; raise on mismatch (artifact-integrity gate).

**A9 (advisor LOW):** rename emitted `var_null` → `var_sr_null` (it is `Var(SR_null)=1/(T−1)`, distinct from the per-candidate Mertens denominator); update `_RESULT_FIELDS` + spec §5.4.

**A10 (advisor LOW + Codex):** add a `DESIGN INVARIANT` comment at `deflated_z` documenting the `√(mertens·(T−1)) = √term` cancellation, + a unit test asserting `denom == sqrt(term)`.

**A11 (advisor LOW):** MC test — additionally assert `abs(form_b_minus_empirical) < abs(form_a_minus_empirical)` (encodes that Form B is the better Gaussian-extreme-value approximation at N\*=18).

**A12 (advisor OTHER + HARD CONSTRAINT 270-271 — NEW preflight in Task 8/11):** add a cost-anchor provenance preflight: assert the cohort's `execution_config_path` cost-model body is the 15bps/side spot anchor (orchestrator verified `execution_phase4_15bps.yaml` body is functionally identical to `execution_phaseb_spot_15bps.yaml` — both 15bps spot, differ only in header + `cost_model.name` + SHA by design). The NOTE (Task 12) discloses that the cohort ran under the `phase4_realistic_base_15bps` path-label (not the `phaseb_spot_realistic_15bps` label) but at the identical 15bps spot cost basis — satisfying HARD CONSTRAINT 270 (not 7bps), with the path-label distinction noted for forensic clarity.

**A13 (advisor OTHER — amends Task 12 errata wording):** the R6.1 §12.5 errata must also state the window is **2026-01-01 → 2026-04-16 (~3.5 months, forward_2026)**, not a full-year 2025 holdout (the prose error is on BOTH magnitude ~2500-not-6000 AND window-label).

**A14 (both legs — Task 12 NOTE disclosures, binding):** (a) frame the (verified-preview) **0/18 outcome** as a structurally-informative conservative-first-fire zero-capital result (§11.4), NOT a pipeline failure; (b) the **N5 selection-inflation** disclosure is load-bearing given 0/18 — explicitly forbid any future cycle relaxing N\* or the pass rule to manufacture passers (threshold-shopping against the D1 anti-revisitation binding); (c) flag that the top-Sharpe candidate `7abff29fc2f117a1` (ema_crossover_momentum_acceleration) is BOTH the highest performer AND R2.1-INDETERMINATE-flagged; (d) disclose the ~85–93% zero-return fraction as context for the small per-bar SR magnitudes. **Task 10 post-fix re-verify:** confirm NO weak-rule (`PSR≥0.5` / `z≥0` / `SR̂≥SR*`) semantics leaked anywhere into the strong-rule implementation or the NOTE prose (the 2 HIGH findings were that exact error class recurring).
