"""Monte-Carlo gate-power validation for the Evaluation-Gate Power Study.

Empirically validates the analytical confirmation-power claim in
``backtest/eval_power.py`` (+ ``docs/phase5/EVAL_GATE_POWER_STUDY.md``): that the
live DSR-FWER gate's 80%-power minimum-detectable Sharpe (MDE) is ~4.63 (N*=1) /
~6.22 (N*=3) annualized hourly, i.e. it CANNOT confirm a modest ~1-1.5 Sharpe
edge. It measures the gate's ACTUAL detection (pass) rate as a function of a
KNOWN true Sharpe by simulating series through the LIVE ``tier6_dsr`` gate.

# CONTRACT BOUNDARY (mirrors eval_power.py, B2-advisor): IMPORT-PRIMITIVES-ONLY.
# Imports Z_PASS, sr_star, deflated_z from backtest.tier6_dsr. The stationary
# bootstrap is reimplemented as _stationary_bootstrap_from_source (generalizing
# tier6_bootstrap.stationary_bootstrap_indices to source_len != output_len —
# we resample a length-T window from the FULL ~55k-bar series; the primitive
# couples output-length and modulus so it cannot. Pinned equivalent to the
# primitive by test). It MUST NEVER call
# evaluate_cohort() / _read_cohort_csv() / emit_artifacts() /
# run_cohort_suitability() / bootstrap_sharpe_se() — the first group defaults to
# WRITING the sealed tier6_dsr_v1/ or tier6_serialcorr_robustness_v1/ dirs, and
# bootstrap_sharpe_se() raises on >0.1% degenerate replicates. The only write
# this module performs is to its own non-sealed
# data/eval_gate_power_study/mc_power_v1.json, and only from __main__.

## The DGP (advisor-corrected — BLOCKING fix)
The as-designed recipe ("demean per-sim, then add mean = sr_true * per-sim
realized sigma") made sr_hat ~= sr_true DETERMINISTIC (sd(sr_hat) ~ 2e-17 vs the
correct 1/sqrt(T-1)), collapsing the power curve into a falsely-confirmatory step
function. FIX (verified to recover ~80% at the MDE): inject at the POPULATION
level and let the sample mean fluctuate —

    y = sr_true_pb * sigma_pop + base_draw(T)

where base_draw is NOT per-sim-demeaned and sigma_pop is FIXED (1.0 for the iid
arm; the real series' global sigma for the bootstrap arm). The gate then sees
sr_hat = mean(y)/std(y) carrying its full ~1/sqrt(T-1) sampling spread around the
injected sr_true_pb. test_eval_power_mc pins sd(sr_hat) ~= 1/sqrt(T-1) so the
fatal recipe can never silently return.

## Two arms (report SEPARATELY)
Arm 1 (iid Gaussian) = closed-form SELF-CONSISTENCY / no-code-bug check. The
gate's Mertens variance assumes iid, so this is near-tautological as a power
claim; it confirms the closed-form inversion + the gate code agree.
Arm 2 (stationary block-bootstrap of REAL BTC 1h log-returns) = the LOAD-BEARING
real-data power test (the iid-Mertens gate does NOT assume real fat tails +
vol-clustering). Bootstrap SOURCE = the FULL canonical return distribution, NOT
any train/val/test/holdout split: this samples the return DISTRIBUTION, it does
not evaluate a strategy on a designated split (no peeking, no governance touch).

## Scope + residual (disclosed)
Validates the gate's POWER (the confirmation wall), NOT edge existence. The MC
injects a STATIONARY constant Sharpe; a real NON-STATIONARY edge of the same
nominal Sharpe would be detected NO MORE often, so the measured detection rate is
an UPPER BOUND on power = a LOWER BOUND on the confirmation wall.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# CONTRACT BOUNDARY (see module docstring): primitives ONLY.
from backtest.tier6_dsr import Z_PASS, deflated_z, sr_star
from backtest import eval_power

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_RETURNS_PATH = PROJECT_ROOT / "data/raw/btcusdt_1h.parquet"
RESULTS_DIR = PROJECT_ROOT / "data/eval_gate_power_study"
RESULTS_PATH = RESULTS_DIR / "mc_power_v1.json"

# Observed-moment anchor (Path D H1) — the moments the analytical headline uses.
OBS_G3, OBS_G4 = 0.14036, 11.30944
DEFAULT_M = 5000
DEFAULT_BLOCK_LEN = 24  # stationary-bootstrap expected block (hours); ~1 day
DEFAULT_SEED = 20260602


def _moments(y: np.ndarray) -> tuple[float, float, float]:
    """Realized per-bar (sr_hat, gamma3, gamma4_raw) via method-of-moments.

    Matches the gate's expectation: sr_hat = mean/sigma (ddof=0); gamma4 RAW
    (3 = Gaussian), as tier6_dsr.mertens_variance expects.
    """
    yc = y - y.mean()
    m2 = float(np.mean(yc * yc))
    sigma = math.sqrt(m2)
    sr_hat = float(y.mean()) / sigma
    g3 = float(np.mean(yc**3)) / sigma**3
    g4 = float(np.mean(yc**4)) / sigma**4
    return sr_hat, g3, g4


def _sr_star_for(n_star: int, T: int) -> float:
    """sr_star for the gate. N*=1 = a single pre-registered hypothesis: no
    expected-max-of-N deflation, so sr_star = 0 (mirrors eval_power)."""
    return 0.0 if n_star == 1 else sr_star(n_star, T, "B")


def inject_iid_gaussian(
    T: int, sr_true_pb: float, rng: np.random.Generator, sigma_pop: float = 1.0
) -> np.ndarray:
    """Arm 1: iid Gaussian base, population-level Sharpe injection.

    y = sr_true_pb * sigma_pop + N(0, sigma_pop^2). The sample mean fluctuates,
    so sr_hat carries its full 1/sqrt(T-1) sampling spread (the BLOCKING fix).
    """
    base = rng.standard_normal(T) * sigma_pop
    return sr_true_pb * sigma_pop + base


def _stationary_bootstrap_from_source(
    out_len: int, source_len: int, expected_block_len: float, rng: np.random.Generator
) -> np.ndarray:
    """Politis-Romano stationary-bootstrap: ``out_len`` indices over a source of
    length ``source_len``.

    Generalizes ``tier6_bootstrap.stationary_bootstrap_indices`` (which couples
    output length and modulus, so it can only resample a length-N series into
    length-N) to ``source_len != out_len`` — needed because we resample a
    length-T window from the FULL ~55k-bar return series. With
    ``source_len == out_len`` and the same RNG it is byte-identical to the
    primitive (pinned by test). Modulus is ``source_len`` (circular wrap over the
    full distribution).
    """
    p = 1.0 / expected_block_len
    idx = np.empty(out_len, dtype=np.int64)
    idx[0] = int(rng.integers(0, source_len))
    u = rng.random(out_len - 1)
    fresh = rng.integers(0, source_len, size=out_len - 1)
    for i in range(1, out_len):
        idx[i] = fresh[i - 1] if u[i - 1] < p else (idx[i - 1] + 1) % source_len
    return idx


def inject_bootstrap(
    source0: np.ndarray,
    sigma_src: float,
    T: int,
    sr_true_pb: float,
    rng: np.random.Generator,
    block_len: int = DEFAULT_BLOCK_LEN,
) -> np.ndarray:
    """Arm 2: stationary block-bootstrap of REAL (globally-demeaned) returns,
    population-level Sharpe injection.

    source0 is the canonical FULL return series demeaned ONCE by its global mean
    (a constant); a length-T stationary-bootstrap resample over the FULL series
    preserves real fat tails + autocorrelation with a ~0 mean, and we add a FIXED
    mu = sr_true_pb * sigma_src (NOT re-tied per resample). sr_hat then fluctuates
    around sr_true_pb. (B2-fix: must resample the FULL ~55k-bar distribution, not
    only the first T bars — the latter biased the sample to the 2020 COVID-crash
    window, inflating std/kurtosis and halving the recovered Sharpe.)
    """
    idx = _stationary_bootstrap_from_source(T, source0.shape[0], block_len, rng)
    base = source0[idx]
    return sr_true_pb * sigma_src + base


def detection_rate(
    inject_fn, sr_star_val: float, T: int, M: int, rng: np.random.Generator
) -> dict:
    """Empirical gate detection (pass) rate over M sims for one cell.

    inject_fn(rng) -> a length-T series. Each sim: realized (sr_hat, g3, g4) ->
    live deflated_z(sr_hat, sr_star_val, g3, g4, T) -> pass iff >= Z_PASS.
    Degenerate sims (deflated_z raises on a non-positive Mertens term) are
    counted and excluded from the rate denominator.
    """
    passes = 0
    degen = 0
    sr_hats = np.empty(M)
    g3s = np.empty(M)
    g4s = np.empty(M)
    for i in range(M):
        y = inject_fn(rng)
        sr_hat, g3, g4 = _moments(y)
        sr_hats[i] = sr_hat
        g3s[i] = g3
        g4s[i] = g4
        try:
            z = deflated_z(sr_hat, sr_star_val, g3, g4, T)
        except ValueError:
            degen += 1
            continue
        if z >= Z_PASS:
            passes += 1
    n_eval = M - degen
    return {
        "detection_rate": (passes / n_eval) if n_eval else float("nan"),
        "passes": passes,
        "n_eval": n_eval,
        "degenerate": degen,
        "sr_hat_mean": float(sr_hats.mean()),
        "sr_hat_sd": float(sr_hats.std(ddof=1)),
        "g3_mean": float(g3s.mean()),
        "g4_mean": float(g4s.mean()),
    }


@dataclass(frozen=True)
class Cell:
    arm: str
    T: int
    ppy: int
    n_star: int


def _load_real_returns0() -> tuple[np.ndarray, float]:
    """Load the canonical BTC 1h log-returns, demeaned ONCE by the global mean.

    SOURCE = the full canonical return distribution (all bars), NOT a designated
    split — this samples the return distribution, it does not evaluate on a split.
    """
    import pandas as pd

    df = pd.read_parquet(RAW_RETURNS_PATH, columns=["close"])
    r = np.log(df["close"].to_numpy())
    r = np.diff(r)
    r = r[np.isfinite(r)]
    sigma_src = float(r.std(ddof=0))
    return r - r.mean(), sigma_src


def _sharpe_targets(n_star: int, T: int, ppy: int) -> list[tuple[str, float]]:
    """Annualized true-Sharpe targets for a cell, incl. the EXACT just-sig +
    MDE for this (N*, T) at observed moments (advisor: don't assume 3.0 hits
    just-sig)."""
    ss = _sr_star_for(n_star, T)
    just_sig_ann = eval_power.annualize(
        eval_power.just_significant_per_bar(ss, T, OBS_G3, OBS_G4), ppy
    )
    mde_ann = eval_power.annualize(
        eval_power.mde_per_bar(ss, T, OBS_G3, OBS_G4), ppy
    )
    return [
        ("zero", 0.0),
        ("modest_1.0", 1.0),
        ("deployable_1.5", 1.5),
        ("strong_3.0", 3.0),
        ("just_significant", just_sig_ann),
        ("analytical_MDE", mde_ann),
    ]


def run_validation(m: int = DEFAULT_M, seed: int = DEFAULT_SEED) -> dict:
    """Full MC sweep: arms x cells x sharpe-targets -> detection rates."""
    rng = np.random.default_rng(seed)
    source0, sigma_src = _load_real_returns0()
    cells = [
        Cell("iid_gaussian", 2527, 8760, 1),
        Cell("iid_gaussian", 2527, 8760, 3),
        Cell("iid_gaussian", 105, 365, 1),
        Cell("iid_gaussian", 105, 365, 3),
        Cell("real_bootstrap", 2527, 8760, 1),
        Cell("real_bootstrap", 2527, 8760, 3),
        Cell("real_bootstrap", 105, 365, 1),
        Cell("real_bootstrap", 105, 365, 3),
    ]
    rows: list[dict] = []
    for c in cells:
        ss = _sr_star_for(c.n_star, c.T)
        for label, sr_ann in _sharpe_targets(c.n_star, c.T, c.ppy):
            sr_pb = sr_ann / math.sqrt(c.ppy)
            if c.arm == "iid_gaussian":
                inject = lambda r, _pb=sr_pb, _T=c.T: inject_iid_gaussian(_T, _pb, r)
            else:
                inject = lambda r, _pb=sr_pb, _T=c.T: inject_bootstrap(
                    source0, sigma_src, _T, _pb, r
                )
            res = detection_rate(inject, ss, c.T, m, rng)
            rows.append({
                "arm": c.arm,
                "T": c.T,
                "ppy": c.ppy,
                "n_star": c.n_star,
                "sr_true_label": label,
                "sr_true_ann": sr_ann,
                **res,
            })
    return {
        "schema": "eval_gate_power_study/mc_power_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "validates": "docs/phase5/EVAL_GATE_POWER_STUDY.md analytical MDE",
        "params": {
            "M": m,
            "seed": seed,
            "block_len_hours": DEFAULT_BLOCK_LEN,
            "Z_PASS": Z_PASS,
            "obs_moments": {"gamma3": OBS_G3, "gamma4": OBS_G4},
        },
        "criteria": (
            "detection@0~=5%; detection@just_sig~=50%; detection@MDE~=80% (PASS "
            "[77,83]%); detection@1.5<<50% (the wall). Arm1=self-consistency, "
            "Arm2=real-data power (load-bearing). Stationary-edge UPPER BOUND."
        ),
        "rows": rows,
    }


def main() -> int:
    results = run_validation()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    print(f"wrote {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
