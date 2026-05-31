"""GATED RUN entry point for the Path A funding verdict (PHASE D — Charlie register).

Wires the real engine-backed stages into backtest.patha_orchestrator.run_patha_verdict
on the forward_2026 window at the 15bps spot anchor and writes the ADVISORY evidence
bundle to data/phase2c_evaluation_gate/patha_verdict_v1/.

PHASE-D GATE (CRITICAL): executing the real forward_2026 RUN is a SEPARATE Charlie
register-event (Phase D), gated downstream of the C4-C7 build. ``main()`` therefore
REFUSES to run unless ``PHASE_D_AUTHORIZED`` is flipped True by an explicit
Charlie-registered Phase-D authorization. The C4-C7 scope is building this
orchestrator + its unit tests (mocked engine) — NOT executing the verdict run. Do
NOT flip the flag without the Phase-D register.

SCOPE (when Phase D fires): the RUN executes the forward_2026 Tier-5 single-run per
hypothesis (the binding falsification gate) + the train-only tiered per-leg
mechanism sanity + DSR-FWER at N*=3 + the C7 hypothesis-class floors + the fenced
C6 funding-marginal diagnostic. There is NO Step-0 (Path A is a fresh funding
cohort, not a re-score of the dead-18).

Pre-registration discipline: every builder/sizing/exit/threshold is hardcoded
(frozen LOCK). Nothing here is fitted to a result. Sealed tier6_dsr_v1/ sha256 is
verified UNCHANGED before AND after the run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from backtest.patha_train_sanity import in_train_window, load_train_windows

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATHA_VERDICT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/patha_verdict_v1"
FEATURES_PATH = PROJECT_ROOT / "data/features/btcusdt_1h_features.parquet"
FORWARD_WINDOW = (
    datetime(2026, 1, 1, 0, tzinfo=timezone.utc),
    datetime(2026, 4, 16, 7, tzinfo=timezone.utc),
)
ANCHOR = "config/execution_phaseb_spot_15bps.yaml"

# Mechanism-sanity horizons (LOCK Pre-registration 4: 24h AND 72h).
FWD_HORIZON_24H = 24
FWD_HORIZON_72H = 72

# PHASE-D GATE: the forward_2026 RUN is a separate Charlie register-event. This
# flag stays False until that register fires; main() refuses to run while False.
PHASE_D_AUTHORIZED = False

# Sealed dirs that must NEVER be written (inode-identity guard).
SEALED_DIRS = [
    PROJECT_ROOT / "data/phase2c_evaluation_gate/tier6_dsr_v1",
    PROJECT_ROOT / "data/phase2c_evaluation_gate/phase4_forward_2026_15bps_v1",
]
# The 4 sealed tier6_dsr_v1 artifacts whose sha256 must be invariant across the run.
_SEALED_TIER6_FILES = [
    SEALED_DIRS[0] / "tier6_dsr_companion.csv",
    SEALED_DIRS[0] / "tier6_dsr_results.csv",
    SEALED_DIRS[0] / "tier6_mc_validation.json",
    SEALED_DIRS[0] / "tier6_promotion_list.json",
]


def assert_not_sealed(out_dir: Path) -> None:
    """Raise if out_dir is (inode-identical to) or a CHILD of any sealed artifact dir.

    Three-layer check: os.path.samefile inode identity (both must exist) + resolved
    path string equality (catches a not-yet-created namespace) + a child-path guard
    (a write into a sub-path UNDER a sealed dir is refused; the sha256 check is the
    backstop). The child check uses the os.sep boundary so a sibling sharing only the
    sealed dir's name PREFIX is not falsely refused.

    Raises:
        ValueError: If ``out_dir`` resolves to / is inode-identical to / is a child of
            a SEALED_DIR.
    """
    out = Path(out_dir)
    for sealed in SEALED_DIRS:
        if sealed.exists() and out.exists():
            try:
                if os.path.samefile(out, sealed):
                    raise ValueError(f"refusing to write sealed dir {sealed}")
            except OSError:
                pass
        if str(out.resolve()) == str(sealed.resolve()):
            raise ValueError(f"refusing to write sealed dir {sealed}")
        # Child-path guard (defense-in-depth): refuse a write into a CHILD of a
        # sealed dir. The os.sep suffix makes this a path-boundary check, so a
        # sibling like ".../tier6_dsr_v1_sibling" is NOT falsely refused.
        if str(out.resolve()).startswith(str(sealed.resolve()) + os.sep):
            raise ValueError(f"refusing to write a child of sealed dir {sealed}")


def _sealed_fingerprint() -> dict[str, str]:
    """Return {filename: sha256} for the 4 sealed tier6_dsr_v1 artifacts."""
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in _SEALED_TIER6_FILES}


def _git_sha() -> str:
    """Return the current git HEAD sha (short), or 'UNKNOWN'."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=str(PROJECT_ROOT)
        ).decode().strip()
    except Exception:
        return "UNKNOWN"


def build_train_frame(
    windows: list[tuple[pd.Timestamp, pd.Timestamp]],
    features_path: Path = FEATURES_PATH,
) -> pd.DataFrame:
    """Load the factor parquet, restrict to TRAIN windows, attach 24h + 72h fwd rets.

    ``fwd_ret_24h`` / ``fwd_ret_72h`` are the cumulative realized returns over the
    next 24 / 72 bars (TRAIN-ONLY diagnostic targets for the tiered mechanism-sanity
    sign test — NOT registered factors, NOT tradeable signals). The forward windows
    are computed WITHIN each contiguous train segment, so no train bar's forward
    target reaches across a segment edge into the held-out 2022 / 2024 validation.

    Args:
        windows: Train windows from patha_train_sanity.load_train_windows.
        features_path: Path to the funding-factor parquet.

    Returns:
        A train-only frame with the H1/H2/H3 funding factors + fwd_ret_24h/72h.
    """
    df = pd.read_parquet(features_path).sort_values("open_time_utc").reset_index(drop=True)
    mask = df["open_time_utc"].apply(lambda t: in_train_window(pd.Timestamp(t), windows))
    train = df.loc[mask].copy()
    seg = (train.index.to_series().diff() != 1).cumsum()  # new segment at each index gap

    def _fwd_cum(group: pd.Series, horizon: int) -> pd.Series:
        # cumulative return over the next `horizon` bars, computed within-segment:
        # prod(1+r[i+1..i+horizon]) - 1; the last `horizon` bars get NaN (dropped).
        # use simple shifted rolling product on (1+r) over a forward window.
        fwd = (1.0 + group).shift(-1).rolling(window=horizon, min_periods=horizon).apply(
            lambda w: w.prod(), raw=True
        )
        # rolling is backward-looking; shift it forward so row i sees i+1..i+horizon.
        return fwd.shift(-(horizon - 1)) - 1.0

    train["fwd_ret_24h"] = train.groupby(seg)["return_1h"].transform(
        lambda g: _fwd_cum(g, FWD_HORIZON_24H)
    )
    train["fwd_ret_72h"] = train.groupby(seg)["return_1h"].transform(
        lambda g: _fwd_cum(g, FWD_HORIZON_72H)
    )
    train = train.dropna(subset=["fwd_ret_24h", "fwd_ret_72h"]).reset_index(drop=True)
    return train


def run_verdict(
    out_dir: Path = PATHA_VERDICT_DIR,
    *,
    features_path: Path = FEATURES_PATH,
    _run_backtest: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Execute the Path A verdict RUN and return the ADVISORY evidence bundle.

    Injectable deps (``_run_backtest`` / ``features_path``) make this unit-testable
    with mocks; production (Phase D) passes the real engine. Building + unit-testing
    this is the C4-C7 scope; main() gates the actual Phase-D run.

    DEFENSE-IN-DEPTH (2-leg-review HIGH): ``run_verdict`` is a public function that
    could be called directly (bypassing the ``main()`` Phase-D gate). The REAL
    engine (``backtest.engine.run_backtest``) — which writes per-bar artifacts and
    runs the forward_2026 backtest — is NEVER wired internally here. ``run_verdict``
    REQUIRES an injected ``_run_backtest`` callable: unit tests inject a MOCK, and the
    ONLY place the real engine is wired is behind the ``PHASE_D_AUTHORIZED`` assertion
    in ``main()``. Calling ``run_verdict()`` with ``_run_backtest=None`` while Phase D
    is unauthorized raises rather than reaching the real engine.

    Raises:
        RuntimeError: If ``_run_backtest`` is None and Phase D is not authorized —
            the real-engine path must be reached only through the gated ``main()``.
        ValueError: On a sealed-dir write attempt or a sealed-artifact sha256 change
            across the run.
    """
    # DEFENSE-IN-DEPTH: refuse the real-engine path unless an engine is injected.
    # The real engine is wired only by main() behind PHASE_D_AUTHORIZED; a direct
    # run_verdict() call with no injected engine must NOT reach backtest.engine.
    if _run_backtest is None and not PHASE_D_AUTHORIZED:
        raise RuntimeError(
            "patha_run_verdict.run_verdict: REFUSING — the REAL forward_2026 engine "
            "is Phase-D gated and reachable only via the authorized main() gate. "
            "Pass an injected _run_backtest (a MOCK) for unit testing, or fire the "
            "Phase-D Charlie register (flip PHASE_D_AUTHORIZED) before a real run. "
            "Do NOT bypass the gate by calling run_verdict() directly."
        )

    from backtest.patha_eval_gauntlet import build_all_hypotheses
    from backtest.patha_holdout_producer import produce_candidate_holdout
    from backtest.patha_moments import build_cohort_csv, load_patha_moments
    from backtest.patha_orchestrator import run_patha_verdict
    from backtest.patha_perleg_mechanism import compute_per_leg_tiers
    from scripts.pathb_cost_equivalence import assert_cost_equivalence
    from strategies.dsl import compute_dsl_hash
    from strategies.dsl_compiler import compile_dsl_to_strategy

    # When Phase D IS authorized and no mock was injected, main() is responsible for
    # wiring the real engine; resolve it here only on that authorized path.
    if _run_backtest is not None:
        run_backtest_fn = _run_backtest
    else:
        from backtest.engine import run_backtest  # reached only under PHASE_D_AUTHORIZED
        run_backtest_fn = run_backtest

    out_dir = Path(out_dir)
    assert_not_sealed(out_dir)
    cohort_dir = out_dir / "cohort"
    assert_not_sealed(cohort_dir)  # defense-in-depth at the producer write-site

    # --- Preflight guards (before any consume) ---
    cost = assert_cost_equivalence()              # phase4 == 15bps spot anchor
    sealed_before = _sealed_fingerprint()         # sealed-artifact invariant (before)
    git_sha = _git_sha()

    # --- Train-only tiered per-leg mechanism sanity (mechanism-refuted input) ---
    train = build_train_frame(load_train_windows(), features_path=features_path)
    per_leg_result = compute_per_leg_tiers(train)

    # --- Real engine-backed gauntlet stages (forward_2026 Tier-5 per hypothesis) ---
    hypotheses = build_all_hypotheses()

    def real_run_gauntlet(key: str, dsl) -> dict:
        h = compute_dsl_hash(dsl)
        strat = compile_dsl_to_strategy(dsl, write_manifest=False)
        res = produce_candidate_holdout(
            hypothesis_hash=h, name=dsl.name, theme="patha",
            strategy_cls=strat, window=FORWARD_WINDOW, cohort_dir=cohort_dir,
            execution_config_path=ANCHOR, current_git_sha=git_sha,
            _run_backtest=run_backtest_fn,
        )
        return {"holdout_sharpe": res["holdout_sharpe"], "row": res["row"], "hypothesis_hash": h}

    def real_build_moments(holdouts: dict) -> list:
        rows = [h["row"] for h in holdouts.values()]
        df = build_cohort_csv(rows, cohort_dir)
        return load_patha_moments([r["hypothesis_hash"] for r in rows], df, cohort_dir)

    bundle = run_patha_verdict(
        hypotheses=hypotheses,
        run_gauntlet=real_run_gauntlet,
        build_moments=real_build_moments,
        per_leg=lambda: per_leg_result,
        # floors (C7) + funding_marginal (C6) are computed from the forward_2026 run
        # position/equity series at Phase-D fire-time; the build wiring leaves them
        # None (the orchestrator records None until Phase D fills them).
        #
        # CONTRACT GAP: Phase D MUST compute TRAIN-window eligibility floors before
        # scoring and pass them in here (NOT None) — else under-floor candidates
        # mis-score as Tier-5 pass/fail instead of INDETERMINATE (LOCK Pre-registration
        # 3, "floors applied before ranking"). The TRAIN-window floors are: H1 =
        # count_flat_exit_episodes(H1_train_position) >= 200; H2/H3 = zero_fraction <
        # 0.50 AND >= 200 trades over TRAIN (backtest.patha_orchestrator.{h1_floor,
        # h2h3_floor}). The real train-floor computation (running each compiled
        # strategy over the TRAIN window to extract its position/trade series) is
        # Phase-D-gated and is NOT wired now; this marker records the obligation.
        floors=None,
        # CONTRACT GAP: Phase D must compute the fenced funding-marginal diagnostic
        # on the forward bars (the funding-gated equity vs the IDENTICAL no-funding
        # baseline equity, per backtest.patha_marginal_diagnostic.funding_marginal)
        # and pass it into the evidence bundle here (NOT None). It is fenced
        # diagnostic-only (promotion_affecting=False, in_n_star=False) and never feeds
        # N* or promotion; it rides along so a B-result attributes to funding's
        # marginal contribution. Not wired now — Phase-D-gated.
        funding_marginal=None,
    )

    # --- Sealed-artifact invariant (after); HARD guard ---
    sealed_after = _sealed_fingerprint()
    if sealed_after != sealed_before:
        raise ValueError(
            f"SEALED ARTIFACT CHANGED during the run: before={sealed_before} "
            f"after={sealed_after}; the run must NEVER mutate tier6_dsr_v1/."
        )

    bundle["meta"] = {
        "git_sha": git_sha,
        "forward_window": [FORWARD_WINDOW[0].isoformat(), FORWARD_WINDOW[1].isoformat()],
        "anchor": ANCHOR,
        "cost_equivalence": cost,
        "sealed_sha256_invariant": sealed_after,
        "scope_note": (
            "Path A funding verdict: forward_2026 Tier-5 gate + train-only tiered "
            "mechanism sanity (24h+72h) + DSR-FWER(N*=3); NO Step-0 (fresh funding "
            "cohort). C6 funding-marginal + C7 floors filled at Phase-D fire-time."
        ),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "patha_verdict_advisory.json").write_text(
        json.dumps(bundle, indent=2, default=str)
    )
    return bundle


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="GATED Path A funding verdict RUN (Phase-D Charlie register-event ONLY)."
    )
    ap.add_argument("--out-dir", default=str(PATHA_VERDICT_DIR))
    args = ap.parse_args(argv)

    if not PHASE_D_AUTHORIZED:
        print(
            "patha_run_verdict: REFUSING — the forward_2026 RUN is Phase-D gated and "
            "NOT authorized. The C4-C7 scope is building + unit-testing this harness "
            "(mocked engine); executing the real verdict run is a SEPARATE Charlie "
            "register-event (Phase D). Do NOT flip PHASE_D_AUTHORIZED without that "
            "register. Aborting.",
            file=sys.stderr,
        )
        return 2

    # Real-engine path: authorized ONLY here, behind the PHASE_D_AUTHORIZED gate
    # above. run_verdict(_run_backtest=None) resolves the real engine internally and
    # re-asserts the gate (defense-in-depth) before any real run / artifact write.
    assert PHASE_D_AUTHORIZED, "unreachable: gate checked above"
    bundle = run_verdict(Path(args.out_dir))
    tax = bundle["taxonomy"]
    esc = bundle["escalation"]
    print(json.dumps({
        "advisory_taxonomy": tax["advisory_taxonomy"],
        "is_earned_negative": tax["is_earned_negative"],
        "b_positive_strength": tax.get("b_positive_strength"),
        "verdict_rests_on_weak_sane_only": tax.get("verdict_rests_on_weak_sane_only"),
        "n_tier5_pass": bundle["n_tier5_pass"],
        "n_dsr_pass": bundle["n_dsr_pass"],
        "approximation_tempers": tax["approximation_tempers"],
        "a_escalation_warranted": esc["a_escalation_warranted"],
        "escalation_reason": esc["reason"],
        "authority": "charlie_register_at_earned_negative_gate",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
