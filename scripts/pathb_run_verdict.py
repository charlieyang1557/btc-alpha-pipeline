"""Gated RUN entry point for the Path B verdict (Charlie register-event only).

Wires the real engine-backed stages into backtest.pathb_orchestrator.run_pathb_verdict
on the forward_2026 window at the 15bps spot anchor and writes the ADVISORY evidence
bundle to data/phase2c_evaluation_gate/pathb_verdict_v1/. Executing this is a Charlie
register-event (design §6); the binding earned-negative read + any A-escalation remain
Charlie's at the §9 gate.

SCOPE (pinned, B2-reviewed): the RUN executes the forward_2026 Tier-5 single-run per
hypothesis (the binding falsification gate — the SAME OOS slice the dead-18 scored 0/18)
+ the train-only per-leg mechanism sanity + the read-only Step-0 diagnostic + DSR-FWER
at N*=3. The train-WF / 2022-regime-holdout / 2024-validation stages are NOT run as
gating stages: the §9 taxonomy keys ONLY on (a) train-only mechanism sanity and (b)
Tier-5 holdout_sharpe>0; the intermediate stages are methodological narrative, not
taxonomy inputs, and running them changes no binding read.

Pre-registration discipline: every builder/sizing/exit/threshold is hardcoded (frozen
LOCK + registered decisions); nothing here is fitted to a result. Sealed tier6_dsr_v1/
sha256 is verified UNCHANGED before AND after the run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATHB_VERDICT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/pathb_verdict_v1"
FEATURES_PATH = PROJECT_ROOT / "data/features/btcusdt_1h_features.parquet"
FORWARD_WINDOW = (
    datetime(2026, 1, 1, 0, tzinfo=timezone.utc),
    datetime(2026, 4, 16, 7, tzinfo=timezone.utc),
)
ANCHOR = "config/execution_phaseb_spot_15bps.yaml"

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
    """Raise if out_dir is (inode-identical to) any sealed artifact dir.

    Two-layer check:
      1. os.path.samefile — inode identity (both paths must exist).
      2. resolved-path string equality — catches the case where one side
         does not exist yet (e.g., new namespace before first write).

    Args:
        out_dir: The proposed output directory path.

    Raises:
        ValueError: If ``out_dir`` resolves to or is inode-identical to any
            entry in ``SEALED_DIRS``.
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


def _sealed_fingerprint() -> dict[str, str]:
    """Return {filename: sha256} for the 4 sealed tier6_dsr_v1 artifacts."""
    fp = {}
    for p in _SEALED_TIER6_FILES:
        fp[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return fp


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
    """Load the factor parquet, restrict to TRAIN windows, attach a fwd_ret.

    ``fwd_ret`` is the next-bar realized return (return_1h shifted -1) — a
    TRAIN-ONLY diagnostic target for the per-leg mechanism-sanity sign test
    (NOT a registered factor, NOT a tradeable signal). The ≤1-bar boundary
    look-ahead at a train-segment edge is immaterial to a conditional-mean sign
    over thousands of bars and never leaves the train window for the backtest.

    Args:
        windows: Train windows from pathb_train_sanity.load_train_windows.
        features_path: Path to the factor parquet.

    Returns:
        A train-only frame with the H1/H2/H3 factors + ``fwd_ret``.
    """
    from backtest.pathb_train_sanity import in_train_window

    df = pd.read_parquet(features_path).sort_values("open_time_utc").reset_index(drop=True)
    # Mask to TRAIN rows first, THEN compute fwd_ret WITHIN each contiguous train
    # segment, so no train bar's forward target reaches across a segment edge into
    # the held-out 2022 / the 2024 validation that follows (Codex MED). The last
    # bar of each segment gets NaN (dropped) — zero boundary leak into held data.
    mask = df["open_time_utc"].apply(lambda t: in_train_window(pd.Timestamp(t), windows))
    train = df.loc[mask].copy()
    seg = (train.index.to_series().diff() != 1).cumsum()  # new segment at each index gap
    train["fwd_ret"] = train.groupby(seg)["return_1h"].shift(-1)
    train = train.dropna(subset=["fwd_ret"]).reset_index(drop=True)
    return train


def _step0_lifted_any(step0_rows: list[dict]) -> bool:
    """Did the Step-0 re-score lift any dead candidate's excess Sharpe above 0?

    The §9 A-escalation second prong. 'Lifted above 0' = the candidate's
    deflated z-stat (SR_hat − SR*) is positive (it beat its multiplicity bar
    in excess), or it passes DSR-FWER (pass_B). Read defensively against
    whichever keys evaluate_candidate emits.

    Args:
        step0_rows: Rows from scripts.pathb_step0_diagnostic.run_step0.

    Returns:
        True iff any candidate's excess Sharpe was lifted above 0.
    """
    for r in step0_rows:
        if r.get("pass_B") is True:
            return True
        # evaluate_candidate emits FORM-SUFFIXED keys (deflated_z_B / pass_B);
        # Form B is authoritative. deflated_z_B > 0 means SR_hat > SR* — the
        # candidate's excess Sharpe was lifted above 0 under the N*=3 re-score.
        v = r.get("deflated_z_B")
        if isinstance(v, (int, float)) and v > 0:
            return True
    return False


def run_verdict(
    out_dir: Path = PATHB_VERDICT_DIR,
    *,
    features_path: Path = FEATURES_PATH,
    _run_backtest: Callable[..., Any] | None = None,
    _run_step0: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Execute the Path B verdict RUN and return the ADVISORY evidence bundle.

    Injectable deps (``_run_backtest`` / ``_run_step0`` / ``features_path``) make
    this unit-testable with mocks; production passes the real engine + Step-0.

    Raises:
        ValueError: On a sealed-dir write attempt, cost-anchor mismatch, or a
            sealed-artifact sha256 change across the run.
    """
    from backtest.engine import run_backtest
    from backtest.pathb_eval_gauntlet import build_all_hypotheses
    from backtest.pathb_holdout_producer import produce_candidate_holdout
    from backtest.pathb_moments import build_cohort_csv, load_pathb_moments
    from backtest.pathb_orchestrator import run_pathb_verdict
    from backtest.pathb_perleg_mechanism import compute_per_leg_mechanism
    from backtest.pathb_train_sanity import load_train_windows
    from scripts.pathb_cost_equivalence import assert_cost_equivalence
    from scripts.pathb_step0_diagnostic import run_step0
    from strategies.dsl import compute_dsl_hash
    from strategies.dsl_compiler import compile_dsl_to_strategy

    run_backtest_fn = _run_backtest or run_backtest
    run_step0_fn = _run_step0 or run_step0

    out_dir = Path(out_dir)
    assert_not_sealed(out_dir)
    cohort_dir = out_dir / "cohort"
    assert_not_sealed(cohort_dir)  # defense-in-depth at the producer write-site

    # --- Preflight guards (before any consume) ---
    cost = assert_cost_equivalence()              # phase4 == 15bps spot anchor
    sealed_before = _sealed_fingerprint()         # sealed-artifact invariant (before)
    git_sha = _git_sha()

    # --- Step 0: read-only re-score of the dead cohort (escalation prong 2) ---
    step0 = run_step0_fn()
    step0_lift = _step0_lifted_any(step0["rows"])

    # --- Train-only per-leg mechanism sanity (mechanism-refuted input) ---
    train = build_train_frame(load_train_windows(), features_path=features_path)
    per_leg_result = compute_per_leg_mechanism(train)

    # --- Real engine-backed gauntlet stages (forward_2026 Tier-5 per hypothesis) ---
    hypotheses = build_all_hypotheses()

    def real_run_gauntlet(key: str, dsl) -> dict:
        h = compute_dsl_hash(dsl)
        strat = compile_dsl_to_strategy(dsl, write_manifest=False)
        res = produce_candidate_holdout(
            hypothesis_hash=h, name=dsl.name, theme="pathb",
            strategy_cls=strat, window=FORWARD_WINDOW, cohort_dir=cohort_dir,
            execution_config_path=ANCHOR, current_git_sha=git_sha,
            _run_backtest=run_backtest_fn,
        )
        return {"holdout_sharpe": res["holdout_sharpe"], "row": res["row"], "hypothesis_hash": h}

    def real_build_moments(holdouts: dict) -> list:
        rows = [h["row"] for h in holdouts.values()]
        df = build_cohort_csv(rows, cohort_dir)
        return load_pathb_moments([r["hypothesis_hash"] for r in rows], df, cohort_dir)

    bundle = run_pathb_verdict(
        hypotheses=hypotheses,
        run_gauntlet=real_run_gauntlet,
        build_moments=real_build_moments,
        per_leg=lambda: per_leg_result,
        step0_lifted_any=step0_lift,
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
        "step0_lifted_any": step0_lift,
        "step0_rows": step0["rows"],
        "sealed_sha256_invariant": sealed_after,
        "scope_note": "forward_2026 Tier-5 gate + train-only mechanism sanity + Step-0 + DSR-FWER(N*=3); intermediate gauntlet stages not gating (taxonomy keys on Tier-5 + mechanism only).",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pathb_verdict_advisory.json").write_text(
        json.dumps(bundle, indent=2, default=str)
    )
    return bundle


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Gated Path B verdict RUN (Charlie register-event only)."
    )
    ap.add_argument("--out-dir", default=str(PATHB_VERDICT_DIR))
    args = ap.parse_args(argv)
    bundle = run_verdict(Path(args.out_dir))
    tax = bundle["taxonomy"]
    esc = bundle["escalation"]
    print(json.dumps({
        "advisory_taxonomy": tax["advisory_taxonomy"],
        "is_earned_negative": tax["is_earned_negative"],
        "b_positive_strength": tax.get("b_positive_strength"),
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
