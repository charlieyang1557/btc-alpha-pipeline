"""Estimand-deployability minimal-confirmation (P1-P4) — read-only analysis.

Implements the spec docs/superpowers/specs/2026-06-02-estimand-deployability-
confirmation-design.md. Confirms (or refutes, B-iii-style) that a directional /
Brier evaluation gate is NOT worth building: its heavy-tail power advantage
concentrates in the non-deployable skew-divorced zone (P1); the deployable-band
net benefit AFTER the 2N* multiplicity of a second gate is far below the 10pp
tripwire (P2/P3); and the runs-test / serial-dependence angle is a confirmation-
layer category error (P4). Verdict: DON'T-BUILD, or SURPRISE_RECONSIDER.

# CONTRACT BOUNDARY (mirrors eval_layer_scoping.py): IMPORT-PRIMITIVES-ONLY.
# Reuses eval_layer_scoping.{unit_var_density_at_zero, FORWARD_T, FORWARD_PPY,
# _phi}. NEVER calls evaluate_cohort() or writes any sealed directory; writes only
# its own non-sealed data/eval_gate_power_study/estimand_deploy_confirm_v1.json.
# Pure-analytical + tiny synthetic; no data, no engine, no holdout, no peek.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats

from backtest.eval_layer_scoping import (
    FORWARD_PPY,
    FORWARD_T,
    _phi,
    unit_var_density_at_zero,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "data/eval_gate_power_study"
RESULTS_PATH = RESULTS_DIR / "estimand_deploy_confirm_v1.json"

DEPLOY_BAND = (1.0, 1.5)  # the build-relevant net-Sharpe tier (PRIMARY)
TRIPWIRE_PP = 10.0  # min absolute net-of-2N* power lift to be BUILD-worthy
N_STAR_ARMS = (3, 18, 39)  # the project's realistic multiplicity values
GAMMA4_ARMS = (11.30944, 30.0, 60.0, 100.0)  # BTC anchor + heavier raw-hourly

# Wide, dense OUT-OF-GRID box for the false-negative foreclosure (§42.2): every
# dial cranked toward the BUILD outcome, most settings absurd / non-deployable.
OOG_SHARPE = tuple(round(0.05 + 0.05 * i, 2) for i in range(40))  # 0.05 .. 2.00
OOG_GAMMA4 = (4.0, 8.0, 11.30944, 20.0, 30.0, 60.0, 100.0, 200.0, 300.0, 600.0, 1000.0)
OOG_NSTAR = (1, 2, 3, 5, 10, 18, 39, 100, 500)


# --------------------------------------------------------------------------
# P1 — skew-divorce: directional gate fires at net-Sharpe <= 0 (non-deployable).
# --------------------------------------------------------------------------
def skew_divorce_case(a: float, drift: float) -> dict:
    """A unit-variance skew-normal (shape a), shifted by `drift` (= the per-bar
    Sharpe, since sd=1). Returns the hit-rate P(up), the Sharpe, and whether the
    directional gate fires while the candidate is non-deployable (Sharpe<=0)."""
    sn = stats.skewnorm(a)
    m, v = float(sn.mean()), float(sn.var())
    sd = math.sqrt(v)
    g3 = float(sn.stats(moments="s"))
    g4 = float(sn.stats(moments="k")) + 3.0  # excess -> raw kurtosis
    # Y = drift + Z, Z=(X-m)/sd standardized; P(Y>0) = P(X > m - drift*sd).
    p_up = float(sn.sf(m - drift * sd))
    sharpe = drift
    sign_z = 2.0 * (p_up - 0.5) * math.sqrt(FORWARD_T)
    return {
        "a": a,
        "gamma3": g3,
        "gamma4": g4,
        "sharpe": sharpe,
        "p_up": p_up,
        "sign_z": sign_z,
        "directional_fires_but_not_deployable": bool(sign_z > 2.0 and sharpe <= 0.0),
    }


def p1_skew_divorce_summary() -> dict:
    """Over a grid of negative skew at net-Sharpe<=0, the directional hit-rate
    reaches high values (the gate fires) -> the directional advantage overlaps the
    NON-deployable zone (the skew-divorce mechanism)."""
    best = 0.5
    for a in (-2.0, -5.0, -10.0, -20.0):
        for drift in (-0.05, -0.02, 0.0):
            c = skew_divorce_case(a, drift)
            if c["sharpe"] <= 0.0:
                best = max(best, c["p_up"])
    return {
        "max_p_up_at_nonpositive_sharpe": best,
        "concentrates_in_nondeployable_zone": best > 0.55,
    }


# --------------------------------------------------------------------------
# P2 + P3 — net benefit of adding a directional gate, AFTER 2N* multiplicity.
# --------------------------------------------------------------------------
def multiplicity_z(n_tests: int, fwer: float = 0.05) -> float:
    """One-sided Bonferroni z-threshold for `n_tests` hypotheses at FWER."""
    return float(stats.norm.ppf(1.0 - fwer / n_tests))


def _power(z_thr: float, ncp: float) -> float:
    return 1.0 - _phi(z_thr - ncp)


def _ncp_sharpe(sharpe_ann: float, T: int = FORWARD_T, ppy: int = FORWARD_PPY) -> float:
    delta = sharpe_ann / math.sqrt(ppy)
    return delta * math.sqrt(T - 1)  # ~kurtosis-independent at a modest per-bar SR


def _ncp_sign(sharpe_ann: float, gamma4: float, T: int = FORWARD_T,
              ppy: int = FORWARD_PPY) -> float:
    delta = sharpe_ann / math.sqrt(ppy)
    return 2.0 * unit_var_density_at_zero(gamma4) * delta * math.sqrt(T)


def net_benefit_after_multiplicity(sharpe_ann: float, gamma4: float,
                                   n_star: int) -> float:
    """Net detection benefit of ADDING a standalone directional gate to the
    Sharpe-DSR gate, FWER-preserved by doubling the family to 2N*:

        detection(Sharpe OR directional, at 2N*) - detection(Sharpe alone, at N*).

    The OR assumes independence (GENEROUS to the BUILD case — real Sharpe/sign
    gates positively correlate, giving LESS combined power). Returns the benefit
    in [-1, 1] (negative = adding the gate is net-harmful)."""
    z1 = multiplicity_z(n_star)
    z2 = multiplicity_z(2 * n_star)
    ncp_s = _ncp_sharpe(sharpe_ann)
    ncp_d = _ncp_sign(sharpe_ann, gamma4)
    sharpe_alone = _power(z1, ncp_s)
    p_s2 = _power(z2, ncp_s)
    p_d2 = _power(z2, ncp_d)
    combined = 1.0 - (1.0 - p_s2) * (1.0 - p_d2)
    return combined - sharpe_alone


def p2_net_benefit_after_multiplicity() -> dict:
    """Max net benefit over the deployable band x realistic gamma4 x N*; confirm
    it is far below the 10pp tripwire (the directional gate adds no build-worthy
    deployable detection once the 2N* multiplicity is paid)."""
    best = -1.0
    best_at: dict | None = None
    for s in (DEPLOY_BAND[0], 1.25, DEPLOY_BAND[1]):
        for g4 in GAMMA4_ARMS:
            for ns in N_STAR_ARMS:
                nb = net_benefit_after_multiplicity(s, g4, ns)
                if nb > best:
                    best, best_at = nb, {"sharpe_ann": s, "gamma4": g4, "n_star": ns}
    return {
        "max_net_benefit_pp": best * 100.0,
        "max_net_benefit_at": best_at,
        "tripwire_pp": TRIPWIRE_PP,
        "below_tripwire": (best * 100.0) < TRIPWIRE_PP,
    }


def p3_multiplicity_cost() -> dict:
    """The z-threshold inflation a SECOND gate imposes by doubling N* -> 2N*."""
    z18, z36 = multiplicity_z(18), multiplicity_z(36)
    return {
        "z_n18": z18,
        "z_2n18": z36,
        "z_increase_n18": z36 - z18,
        "doubling_inflates_bar": z36 > z18,
    }


def out_of_grid_search() -> dict:
    """False-negative foreclosure (§42.2): the GLOBAL max net benefit over a wide,
    dense out-of-grid box (every dial cranked toward BUILD; most settings absurd /
    non-deployable) is still below the 10pp tripwire -> the registered deployable
    grid hides no surprise region. (NOTE: net benefit is NOT globally monotone —
    e.g. it decreases in Sharpe at high N*, low gamma4 — so this rests on the dense
    global maximum, not a monotonicity argument.)"""
    gmax = -1.0
    at: dict | None = None
    for s in OOG_SHARPE:
        for g4 in OOG_GAMMA4:
            for ns in OOG_NSTAR:
                nb = net_benefit_after_multiplicity(s, g4, ns)
                if nb > gmax:
                    gmax, at = nb, {"sharpe_ann": s, "gamma4": g4, "n_star": ns}
    return {
        "global_max_net_benefit_pp": gmax * 100.0,
        "global_max_at": at,
        "n_cells": len(OOG_SHARPE) * len(OOG_GAMMA4) * len(OOG_NSTAR),
        "tripwire_pp": TRIPWIRE_PP,
        "below_tripwire": (gmax * 100.0) < TRIPWIRE_PP,
    }


# --------------------------------------------------------------------------
# P4 — runs-test / serial-dependence is a confirmation-layer category error.
# --------------------------------------------------------------------------
def p4_runs_test_inert(rho: float = 0.32, seed: int = 7, n: int = 20000) -> dict:
    """An AR(1) raw-return series is ~Sharpe-blind and iid-sign-blind, but a
    momentum strategy on it has POSITIVE P&L Sharpe -> the serial-dependence edge
    shows up in STRATEGY P&L (which the Sharpe-DSR gate scores). So a runs-test is
    a signal-DISCOVERY tool (the alpha-generation layer), not a confirmation-gate
    estimand that catches deployable edges the Sharpe gate misses."""
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(n)
    r = np.zeros(n)
    for i in range(1, n):
        r[i] = rho * r[i - 1] + e[i]
    raw_sharpe = float(r.mean() / r.std())
    pos = np.sign(r[:-1])
    pnl = pos * r[1:]
    mom_sharpe = float(pnl.mean() / pnl.std())
    return {
        "rho": rho,
        "raw_return_sharpe": raw_sharpe,
        "momentum_pnl_sharpe": mom_sharpe,
        "serial_edge_shows_in_pnl_sharpe": mom_sharpe > 0.1,
    }


# --------------------------------------------------------------------------
# Aggregate + verdict.
# --------------------------------------------------------------------------
def run_confirmation() -> dict:
    """Run P1-P4 and apply the §3 verdict map."""
    p1 = skew_divorce_case(-10.0, -0.02)
    p1s = p1_skew_divorce_summary()
    p2 = p2_net_benefit_after_multiplicity()
    p3 = p3_multiplicity_cost()
    oog = out_of_grid_search()
    p4 = p4_runs_test_inert()
    # DON'T-BUILD iff skew-divorce real (P1) AND net benefit < tripwire (P2/P3)
    # AND runs-test inert at confirmation (P4). Else SURPRISE -> reconsider.
    dont_build = (
        p1["directional_fires_but_not_deployable"]
        and p1s["concentrates_in_nondeployable_zone"]
        and p2["below_tripwire"]
        and p4["serial_edge_shows_in_pnl_sharpe"]
    )
    return {
        "P1": {**p1, **p1s},
        "P2": p2,
        "P3": p3,
        "P2_out_of_grid": oog,
        "P4": p4,
        "verdict": "DONT_BUILD" if dont_build else "SURPRISE_RECONSIDER",
    }


def main() -> int:
    """Run the confirmation and write the NON-sealed results file."""
    results = {
        "schema": "eval_gate_power_study/estimand_deploy_confirm_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "spec": "docs/superpowers/specs/2026-06-02-estimand-deployability-confirmation-design.md",
        "confirmation": run_confirmation(),
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    print(f"wrote {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
